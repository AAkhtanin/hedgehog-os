from __future__ import annotations

import json
import re
from copy import deepcopy
from datetime import datetime, timedelta
from functools import lru_cache
from pathlib import Path

import jsonschema

from hedgehog.time_model import utc_now_iso


ROOT = Path(__file__).resolve().parents[1]
SCHEMAS_DIR = ROOT / "schemas"

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
_CANONICAL_UTC_SECOND_RE_V02 = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\+00:00"
)


def _resolve_post_vv_checked_at_v02(checked_at: str | None) -> str | None:
    if checked_at is None:
        return None
    if (
        type(checked_at) is not str
        or _CANONICAL_UTC_SECOND_RE_V02.fullmatch(checked_at) is None
    ):
        raise ValueError("post_vv_checked_at_invalid")
    try:
        parsed = datetime.fromisoformat(checked_at)
    except ValueError:
        raise ValueError("post_vv_checked_at_invalid") from None
    if (
        parsed.utcoffset() != timedelta(0)
        or parsed.microsecond != 0
        or parsed.isoformat(timespec="seconds") != checked_at
    ):
        raise ValueError("post_vv_checked_at_invalid")
    return checked_at


def _load_schema(name: str) -> dict:
    with (SCHEMAS_DIR / name).open("r", encoding="utf-8") as handle:
        return json.load(handle)


@lru_cache(maxsize=1)
def _result_proposal_validator() -> jsonschema.Draft202012Validator:
    common_schema = _load_schema("common.schema.json")
    time_envelope_schema = _load_schema("time_envelope.schema.json")
    result_proposal_schema = _load_schema("result_proposal.schema.json")
    store = {
        common_schema["$id"]: common_schema,
        "common.schema.json": common_schema,
        "https://hedgehog-os.local/schemas/common.schema.json": common_schema,
        time_envelope_schema["$id"]: time_envelope_schema,
        "time_envelope.schema.json": time_envelope_schema,
        "https://hedgehog-os.local/schemas/time_envelope.schema.json": time_envelope_schema,
        result_proposal_schema["$id"]: result_proposal_schema,
    }
    resolver = jsonschema.RefResolver.from_schema(result_proposal_schema, store=store)
    return jsonschema.Draft202012Validator(
        result_proposal_schema,
        resolver=resolver,
    )


@lru_cache(maxsize=1)
def _vv_report_validator() -> jsonschema.Draft202012Validator:
    common_schema = _load_schema("common.schema.json")
    vv_report_schema = _load_schema("vv_report.schema.json")
    store = {
        common_schema["$id"]: common_schema,
        "common.schema.json": common_schema,
        "https://hedgehog-os.local/schemas/common.schema.json": common_schema,
        vv_report_schema["$id"]: vv_report_schema,
    }
    resolver = jsonschema.RefResolver.from_schema(vv_report_schema, store=store)
    return jsonschema.Draft202012Validator(
        vv_report_schema,
        resolver=resolver,
    )


def _schema_error_location(error: jsonschema.ValidationError) -> str:
    if not error.absolute_path:
        return "$"
    return ".".join(str(part) for part in error.absolute_path)


def _result_proposal_schema_violations(candidate) -> list[dict]:
    validator = _result_proposal_validator()
    errors = sorted(
        validator.iter_errors(candidate),
        key=lambda error: (list(error.absolute_path), error.message),
    )
    return [
        _violation(
            "vv_runtime_schema_validation_failed",
            "schema",
            (
                "ResultProposal runtime schema validation failed at "
                f"{_schema_error_location(error)}: {error.message}"
            ),
        )
        for error in errors
    ]


def _vv_report_schema_violations(report: dict) -> list[dict]:
    validator = _vv_report_validator()
    errors = sorted(
        validator.iter_errors(report),
        key=lambda error: (list(error.absolute_path), error.message),
    )
    return [
        _violation(
            "vv_outgoing_runtime_schema_validation_failed",
            "schema",
            (
                "Outgoing VVReport runtime schema validation failed at "
                f"{_schema_error_location(error)}: {error.message}"
            ),
        )
        for error in errors
    ]


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
    if not isinstance(proposal, dict):
        return True
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
    if not isinstance(candidate, dict):
        return {
            "artifact_type": None,
            "payload_status": None,
            "task_completed": None,
            "requires_human_input": False,
            "blocked_reason": None,
            "needs_user": False,
            "blocked": False,
        }

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


def _safe_id(value, fallback: str) -> str:
    return value if isinstance(value, str) and value else fallback


def _safe_optional_id(value) -> str | None:
    return value if isinstance(value, str) and value else None


def _safe_trace_refs(candidate: dict) -> list[dict]:
    trace_refs = candidate.get("trace_refs") if isinstance(candidate, dict) else []
    return list(trace_refs) if isinstance(trace_refs, list) else []


def _dependency_depth(candidate: dict) -> int:
    result_payload = candidate.get("result_payload") if isinstance(candidate, dict) else None
    if not isinstance(result_payload, dict):
        return 0
    value = result_payload.get("dependency_depth", 0)
    return value if isinstance(value, int) and value >= 0 else 0


def _safe_rejected_vv_report(
    *,
    proposal_id: str,
    trace_refs: list[dict],
    violations: list[dict],
    checked_at: str | None = None,
) -> dict:
    return {
        "vv_report_id": f"vv:{proposal_id}",
        "proposal_id": proposal_id,
        "status": "rejected",
        "scores": {
            "schema": 0.0,
            "evidence": 0.0,
            "policy": 0.0,
            "time": 0.0,
            "safety": 0.0,
            "consistency": 0.0,
        },
        "overall_score": 0.0,
        "decision": "reject",
        "checked_at": checked_at if checked_at is not None else utc_now_iso(),
        "violations": violations,
        "normalized_features": {
            "utility": 0.0,
            "robustness": 0.0,
            "compute_cost": 0.0,
            "violations": 1.0,
            "transfer": 0.0,
            "novelty_guard": 0.0,
            "avf_final_viability": None,
            "avf_soft_mask": None,
        },
        "trace_refs": trace_refs,
    }


def _validate_outgoing_vv_report(
    report: dict,
    candidate: dict,
    *,
    checked_at: str | None = None,
) -> dict:
    violations = _vv_report_schema_violations(report)
    if not violations:
        return report
    proposal_id = _safe_id(
        candidate.get("proposal_id") if isinstance(candidate, dict) else None,
        "missing_proposal",
    )
    return _safe_rejected_vv_report(
        proposal_id=proposal_id,
        trace_refs=_safe_trace_refs(candidate),
        violations=violations,
        checked_at=checked_at,
    )


def _validate_result_proposal_with_resolved_checked_at_v02(
    proposal: dict,
    *,
    checked_at: str | None,
) -> dict:
    candidate = deepcopy(proposal)
    violations = _result_proposal_schema_violations(candidate)

    schema_score = 0.0 if violations else 1.0
    required_fields_present = (
        isinstance(candidate, dict)
        and REQUIRED_RESULT_PROPOSAL_FIELDS <= set(candidate)
    )
    if not required_fields_present:
        violations.append(
            _violation(
                "vv_schema_missing_required",
                "schema",
                "ResultProposal is missing required fields.",
            )
        )

    evidence = candidate.get("evidence") if isinstance(candidate, dict) else None
    evidence_score = 1.0 if isinstance(evidence, list) and evidence else 0.0
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

    time_envelope = candidate.get("time_envelope") if isinstance(candidate, dict) else None
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
        if isinstance(candidate, dict)
        and candidate.get("proposal_id")
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
    avf_final_viability = _avf_final_viability(candidate) if isinstance(candidate, dict) else None
    avf_soft_mask = _avf_soft_mask(candidate) if isinstance(candidate, dict) else None
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
    elif schema_score == 0.0 or policy_score == 0.0 or safety_score == 0.0:
        decision = "reject"
    else:
        decision = "revise"

    status = {
        "accept": "accepted",
        "reject": "rejected",
        "revise": "needs_revision",
    }[decision]

    proposal_id = _safe_id(
        candidate.get("proposal_id") if isinstance(candidate, dict) else None,
        "missing_proposal",
    )
    report = {
        "vv_report_id": f"vv:{proposal_id}",
        "proposal_id": proposal_id,
        "dependency_depth": _dependency_depth(candidate),
        "status": status,
        "scores": scores,
        "overall_score": overall_score,
        "decision": decision,
        "checked_at": checked_at if checked_at is not None else utc_now_iso(),
        "violations": violations,
        "normalized_features": {
            "utility": utility,
            "robustness": robustness,
            "compute_cost": _compute_cost_score(candidate.get("cost", {}) if isinstance(candidate, dict) else {}),
            "violations": _clamp_01(1.0 - policy_score + semantic_penalty),
            "transfer": 0.0,
            "novelty_guard": 0.0,
            "avf_final_viability": avf_final_viability,
            "avf_soft_mask": avf_soft_mask,
        },
        "trace_refs": _safe_trace_refs(candidate),
    }
    vector_id = _safe_optional_id(
        candidate.get("vector_id") if isinstance(candidate, dict) else None
    ) or (
        _safe_optional_id(_avf_vector_id(candidate))
        if isinstance(candidate, dict)
        else None
    )
    if vector_id is not None:
        report["vector_id"] = vector_id
    if isinstance(semantics["artifact_type"], str) and semantics["artifact_type"]:
        report["artifact_type"] = semantics["artifact_type"]
    execution_status = semantics["payload_status"] or status
    if isinstance(execution_status, str) and execution_status:
        report["execution_status"] = execution_status
    if isinstance(candidate, dict) and "request_id" in candidate:
        request_id = _safe_optional_id(candidate["request_id"])
        if request_id is not None:
            report["request_id"] = request_id
    # Final outgoing schema boundary; manual checks above remain in force.
    return _validate_outgoing_vv_report(
        report,
        candidate,
        checked_at=checked_at,
    )


def validate_result_proposal(
    proposal: dict,
    *,
    checked_at: str | None = None,
) -> dict:
    resolved_checked_at = _resolve_post_vv_checked_at_v02(checked_at)
    return _validate_result_proposal_with_resolved_checked_at_v02(
        proposal,
        checked_at=resolved_checked_at,
    )


def validate_result_proposals(
    proposals: list[dict],
    *,
    checked_at: str | None = None,
) -> list[dict]:
    resolved_checked_at = _resolve_post_vv_checked_at_v02(checked_at)
    if resolved_checked_at is None:
        return [validate_result_proposal(proposal) for proposal in proposals]
    return [
        _validate_result_proposal_with_resolved_checked_at_v02(
            proposal,
            checked_at=resolved_checked_at,
        )
        for proposal in proposals
    ]
