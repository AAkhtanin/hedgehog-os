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


def _avf_final_viability(proposal: dict) -> float | None:
    result_payload = proposal.get("result_payload")
    if not isinstance(result_payload, dict):
        return None
    avf = result_payload.get("avf")
    if not isinstance(avf, dict):
        return None
    value = avf.get("final_viability")
    if isinstance(value, (int, float)):
        return _clamp_01(float(value))
    return None


def _avf_vector_id(proposal: dict) -> str | None:
    result_payload = proposal.get("result_payload")
    if not isinstance(result_payload, dict):
        return None
    avf = result_payload.get("avf")
    if isinstance(avf, dict) and avf.get("vector_id"):
        return avf["vector_id"]
    return result_payload.get("vector_id")


def _avf_soft_mask(proposal: dict) -> float | None:
    result_payload = proposal.get("result_payload")
    if not isinstance(result_payload, dict):
        return None
    avf = result_payload.get("avf")
    if not isinstance(avf, dict):
        return None
    value = avf.get("soft_mask")
    if isinstance(value, (int, float)):
        return _clamp_01(float(value))
    return None


def _violation(violation_id: str, kind: str, description: str) -> dict:
    return {
        "violation_id": violation_id,
        "kind": kind,
        "description": description,
    }


def _payload_semantics(candidate: dict) -> dict:
    result_payload = candidate.get("result_payload")
    if not isinstance(result_payload, dict):
        return {
            "artifact_type": None,
            "payload_status": None,
            "task_completed": None,
            "requires_human_input": False,
            "blocked_reason": None,
            "needs_user": False,
            "blocked": False,
        }

    payload_status = result_payload.get("status")
    task_completed = result_payload.get("task_completed")
    requires_human_input = result_payload.get("requires_human_input", False) is True
    blocked_reason = result_payload.get("blocked_reason")
    needs_user = requires_human_input or payload_status == "needs_user"
    blocked = bool(blocked_reason) or (
        task_completed is False and payload_status == "needs_user"
    )
    return {
        "artifact_type": result_payload.get("artifact_type"),
        "payload_status": payload_status,
        "task_completed": task_completed,
        "requires_human_input": requires_human_input,
        "blocked_reason": blocked_reason,
        "needs_user": needs_user,
        "blocked": blocked,
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

    semantics = _payload_semantics(candidate)
    if (
        schema_score == 1.0
        and policy_score == 1.0
        and time_score == 1.0
        and semantics["needs_user"]
    ):
        violations.append(
            _violation(
                "vv_human_input_required",
                "consistency",
                "ResultProposal requires human input before completion.",
            )
        )
    if (
        schema_score == 1.0
        and policy_score == 1.0
        and time_score == 1.0
        and semantics["blocked"]
    ):
        violations.append(
            _violation(
                "vv_blocked_before_completion",
                "consistency",
                "ResultProposal is blocked before completion.",
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
    avf_final_viability = _avf_final_viability(candidate)
    avf_soft_mask = _avf_soft_mask(candidate)
    utility = overall_score
    if (
        avf_final_viability is not None
        and avf_soft_mask is not None
        and schema_score == 1.0
        and policy_score == 1.0
        and time_score == 1.0
        and safety_score == 1.0
    ):
        avf_utility = (avf_final_viability * 0.9) + (avf_soft_mask * 0.1)
        utility = (overall_score + avf_utility) / 2

    robustness = (evidence_score + consistency_score + time_score) / 3
    semantic_penalty = 0.0
    if semantics["blocked"]:
        semantic_penalty = 0.4
    elif semantics["needs_user"]:
        semantic_penalty = 0.25
    if semantic_penalty:
        utility = _clamp_01(utility * (1.0 - semantic_penalty))
        robustness = _clamp_01(robustness * (1.0 - semantic_penalty / 2))

    if (
        schema_score == 1.0
        and policy_score == 1.0
        and time_score == 1.0
        and safety_score == 1.0
    ):
        if semantics["needs_user"] or semantics["blocked"]:
            decision = "revise"
        else:
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
        "vector_id": candidate.get("vector_id") or _avf_vector_id(candidate),
        "artifact_type": semantics["artifact_type"],
        "execution_status": semantics["payload_status"] or status,
        "dependency_depth": candidate.get("result_payload", {}).get("dependency_depth", 0),
        "status": status,
        "scores": scores,
        "overall_score": overall_score,
        "decision": decision,
        "checked_at": utc_now_iso(),
        "violations": violations,
        "normalized_features": {
            "utility": utility,
            "robustness": robustness,
            "compute_cost": _compute_cost_score(candidate.get("cost", {})),
            "violations": _clamp_01(1.0 - policy_score + semantic_penalty),
            "transfer": 0.0,
            "novelty_guard": 0.0,
            "avf_final_viability": avf_final_viability,
            "avf_soft_mask": avf_soft_mask,
        },
        "trace_refs": list(candidate.get("trace_refs", [])),
    }
    if "request_id" in candidate:
        report["request_id"] = candidate["request_id"]
    return report


def validate_result_proposals(proposals: list[dict]) -> list[dict]:
    return [validate_result_proposal(proposal) for proposal in proposals]
