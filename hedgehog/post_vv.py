from __future__ import annotations

from copy import deepcopy

from hedgehog.time_model import utc_now_iso


REQUIRED_RESULT_PROPOSAL_FIELDS = {
    "proposal_id",
    "producer",
    "vector_id",
    "plan_id",
    "result_payload",
    "evidence",
    "cost",
    "risks",
    "time_envelope",
    "trace_refs",
}

REQUIRED_TIME_ENVELOPE_FIELDS = {
    "pt_created_at",
    "kt_asof",
    "ct_session_anchor",
    "ttl_seconds",
}

FORBIDDEN_KEYS = {"final_output", "answer", "raw_user_text"}


def _clamp_01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _contains_forbidden_key(value) -> bool:
    if isinstance(value, dict):
        return bool(FORBIDDEN_KEYS & set(value)) or any(
            _contains_forbidden_key(child) for child in value.values()
        )
    if isinstance(value, list):
        return any(_contains_forbidden_key(item) for item in value)
    return False


def _critical_risk_present(proposal: dict) -> bool:
    risks = proposal.get("risks", [])
    if not isinstance(risks, list):
        return True
    return any(isinstance(risk, dict) and risk.get("severity") == "critical" for risk in risks)


def _compute_cost_score(cost: dict) -> float:
    if not isinstance(cost, dict):
        return 1.0
    tokens = float(cost.get("tokens", 0) or 0)
    walltime_ms = float(cost.get("walltime_ms", 0) or 0)
    toolcalls = float(cost.get("toolcalls", 0) or 0)
    normalized_cost = tokens / 10_000 + walltime_ms / 60_000 + toolcalls / 100
    return _clamp_01(normalized_cost)


def _violation(violation_id: str, kind: str, description: str) -> dict:
    return {
        "violation_id": violation_id,
        "kind": kind,
        "description": description,
    }


def validate_result_proposal(proposal: dict) -> dict:
    candidate = deepcopy(proposal)
    violations = []

    schema_score = 1.0 if REQUIRED_RESULT_PROPOSAL_FIELDS <= set(candidate) else 0.0
    if schema_score == 0.0:
        violations.append(
            _violation(
                "vv_schema_missing_required",
                "schema",
                "ResultProposal is missing required fields.",
            )
        )

    evidence_score = 1.0 if isinstance(candidate.get("evidence"), list) and candidate["evidence"] else 0.0
    if evidence_score == 0.0:
        violations.append(
            _violation(
                "vv_evidence_missing",
                "evidence",
                "ResultProposal evidence is missing or empty.",
            )
        )

    policy_score = 0.0 if _contains_forbidden_key(candidate) else 1.0
    if policy_score == 0.0:
        violations.append(
            _violation(
                "vv_policy_forbidden_key",
                "policy",
                "ResultProposal contains a forbidden user-facing or root-only key.",
            )
        )

    time_envelope = candidate.get("time_envelope")
    time_score = (
        1.0
        if isinstance(time_envelope, dict)
        and REQUIRED_TIME_ENVELOPE_FIELDS <= set(time_envelope)
        else 0.0
    )
    if time_score == 0.0:
        violations.append(
            _violation(
                "vv_time_envelope_invalid",
                "time",
                "ResultProposal TimeEnvelope is missing required fields.",
            )
        )

    safety_score = 0.0 if _critical_risk_present(candidate) else 1.0
    if safety_score == 0.0:
        violations.append(
            _violation(
                "vv_safety_critical_risk",
                "safety",
                "ResultProposal contains a critical risk.",
            )
        )

    consistency_score = (
        1.0
        if candidate.get("proposal_id")
        and candidate.get("vector_id")
        and candidate.get("plan_id")
        and isinstance(candidate.get("result_payload"), dict)
        else 0.0
    )
    if consistency_score == 0.0:
        violations.append(
            _violation(
                "vv_consistency_invalid",
                "consistency",
                "ResultProposal identifiers or result_payload are inconsistent.",
            )
        )

    scores = {
        "schema": schema_score,
        "evidence": evidence_score,
        "policy": policy_score,
        "time": time_score,
        "safety": safety_score,
        "consistency": consistency_score,
    }
    overall_score = sum(scores.values()) / len(scores)

    if schema_score == 1.0 and policy_score == 1.0 and time_score == 1.0:
        decision = "accept"
    elif schema_score == 0.0 or policy_score == 0.0:
        decision = "reject"
    else:
        decision = "revise"

    status = {
        "accept": "accepted",
        "reject": "rejected",
        "revise": "needs_revision",
    }[decision]

    report = {
        "vv_report_id": f"vv:{candidate.get('proposal_id', 'missing_proposal')}",
        "proposal_id": candidate.get("proposal_id", "missing_proposal"),
        "status": status,
        "scores": scores,
        "overall_score": overall_score,
        "decision": decision,
        "checked_at": utc_now_iso(),
        "violations": violations,
        "normalized_features": {
            "utility": overall_score,
            "robustness": (evidence_score + consistency_score + time_score) / 3,
            "compute_cost": _compute_cost_score(candidate.get("cost", {})),
            "violations": 1.0 - policy_score,
            "transfer": 0.0,
            "novelty_guard": 0.0,
        },
        "trace_refs": list(candidate.get("trace_refs", [])),
    }
    if "request_id" in candidate:
        report["request_id"] = candidate["request_id"]
    return report


def validate_result_proposals(proposals: list[dict]) -> list[dict]:
    return [validate_result_proposal(proposal) for proposal in proposals]
