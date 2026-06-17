from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass
from typing import Any

from hedgehog.time_model import make_time_envelope


FAILURE_KINDS = {
    "none",
    "timeout",
    "invalid_json",
    "contract_version_mismatch",
    "permission_required",
    "circuit_breaker_open",
    "schema_validation_failed",
    "unknown_exception",
}


@dataclass(frozen=True)
class NeedleCall:
    needle_id: str
    capability: str
    contract_version: str
    required_contract_version: str
    payload: dict[str, Any]
    permission_confirmed: bool
    timeout_ms: int
    scenario: str


@dataclass(frozen=True)
class NeedleExecutionResult:
    needle_id: str
    status: str
    failure_kind: str
    result_payload: dict[str, Any]
    result_proposal_status: str
    quarantine_required: bool
    circuit_breaker_opened: bool
    permission_required: bool
    no_real_external_action: bool
    audit_event: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _audit_event(call: NeedleCall, *, status: str, failure_kind: str) -> dict[str, Any]:
    return {
        "event_type": "needle_runtime_mock_execution",
        "needle_id": call.needle_id,
        "capability": call.capability,
        "scenario": call.scenario,
        "status": status,
        "failure_kind": failure_kind,
        "no_real_external_action": True,
    }


def _result(
    call: NeedleCall,
    *,
    status: str,
    failure_kind: str,
    result_payload: dict[str, Any] | None = None,
    result_proposal_status: str,
    quarantine_required: bool = False,
    circuit_breaker_opened: bool = False,
    permission_required: bool = False,
) -> NeedleExecutionResult:
    if failure_kind not in FAILURE_KINDS:
        failure_kind = "unknown_exception"
    return NeedleExecutionResult(
        needle_id=call.needle_id,
        status=status,
        failure_kind=failure_kind,
        result_payload=result_payload or {},
        result_proposal_status=result_proposal_status,
        quarantine_required=quarantine_required,
        circuit_breaker_opened=circuit_breaker_opened,
        permission_required=permission_required,
        no_real_external_action=True,
        audit_event=_audit_event(call, status=status, failure_kind=failure_kind),
    )


def execute_needle_call(call: NeedleCall) -> NeedleExecutionResult:
    """Simulate bounded needle execution without external side effects."""
    try:
        if call.contract_version != call.required_contract_version:
            return _result(
                call,
                status="blocked",
                failure_kind="contract_version_mismatch",
                result_proposal_status="blocked",
                result_payload={
                    "expected_contract_version": call.required_contract_version,
                    "actual_contract_version": call.contract_version,
                },
            )

        if not call.permission_confirmed:
            return _result(
                call,
                status="blocked",
                failure_kind="permission_required",
                result_proposal_status="blocked",
                permission_required=True,
            )

        if call.scenario == "needle_success_mock":
            return _result(
                call,
                status="completed",
                failure_kind="none",
                result_proposal_status="completed",
                result_payload={
                    "mock_receipt": f"mock:{call.needle_id}:{call.capability}",
                    "echo_keys": sorted(call.payload.keys()),
                },
            )

        if call.scenario == "needle_timeout":
            return _result(
                call,
                status="degraded",
                failure_kind="timeout",
                result_proposal_status="degraded",
                result_payload={"timeout_ms": call.timeout_ms},
            )

        if call.scenario == "needle_invalid_json":
            return _result(
                call,
                status="quarantined",
                failure_kind="invalid_json",
                result_proposal_status="failed",
                quarantine_required=True,
            )

        if call.scenario == "needle_circuit_breaker_open":
            return _result(
                call,
                status="blocked",
                failure_kind="circuit_breaker_open",
                result_proposal_status="blocked",
                circuit_breaker_opened=True,
            )

        if call.scenario == "needle_schema_validation_failed":
            return _result(
                call,
                status="quarantined",
                failure_kind="schema_validation_failed",
                result_proposal_status="failed",
                quarantine_required=True,
            )

        if call.scenario == "needle_unknown_exception":
            raise RuntimeError("simulated needle runtime exception")

        return _result(
            call,
            status="failed",
            failure_kind="unknown_exception",
            result_proposal_status="failed",
            quarantine_required=True,
            result_payload={"unknown_scenario": call.scenario},
        )
    except Exception as exc:
        return _result(
            call,
            status="failed",
            failure_kind="unknown_exception",
            result_proposal_status="failed",
            quarantine_required=True,
            result_payload={"exception_type": type(exc).__name__},
        )


def needle_result_to_result_proposal(
    result: NeedleExecutionResult,
    *,
    request_id: str,
    session_anchor: str = "needle_runtime_failure_integration",
) -> dict[str, Any]:
    proposal_status = result.result_proposal_status
    safe_for_gt = result.status in {"completed", "blocked", "degraded"}
    blocked_reason = None
    requires_human_input = False
    task_completed = proposal_status == "completed"
    risk_severity = "low"

    if proposal_status == "blocked":
        blocked_reason = result.failure_kind
        risk_severity = "medium"
    elif proposal_status == "degraded":
        blocked_reason = result.failure_kind
        risk_severity = "medium"
    elif proposal_status == "failed":
        blocked_reason = result.failure_kind
        risk_severity = "high"
    if result.permission_required:
        requires_human_input = True

    return {
        "proposal_id": f"proposal:{request_id}:{result.needle_id}:{result.failure_kind}",
        "request_id": request_id,
        "producer": {
            "executor_id": "needle_runtime_adapter",
            "needle_id": result.needle_id,
        },
        "vector_id": f"needle_runtime_{result.needle_id}",
        "plan_id": f"plan:{request_id}:needle_runtime_adapter",
        "result_payload": {
            "source": "needle_runtime",
            "needle_id": result.needle_id,
            "status": proposal_status,
            "failure_kind": result.failure_kind,
            "result_payload": dict(result.result_payload),
            "quarantine_required": result.quarantine_required,
            "circuit_breaker_opened": result.circuit_breaker_opened,
            "permission_required": result.permission_required,
            "no_real_external_action": result.no_real_external_action,
            "safe_for_gt": safe_for_gt,
            "root_crash_risk_contained": True,
            "artifact_type": "needle_runtime_result",
            "task_completed": task_completed,
            "requires_human_input": requires_human_input,
            "blocked_reason": blocked_reason,
        },
        "evidence": [
            {
                "kind": "audit",
                "summary": "NeedleRuntime returned a structured mock result with no external action.",
                "ref_id": result.audit_event["event_type"],
            }
        ],
        "cost": {
            "tokens": 0,
            "walltime_ms": 0,
            "toolcalls": 0,
        },
        "risks": [
            {
                "risk_id": f"risk:needle_runtime:{result.failure_kind}",
                "severity": risk_severity,
                "description": f"NeedleRuntime outcome: {result.failure_kind}.",
            }
        ],
        "time_envelope": make_time_envelope(session_anchor),
        "trace_refs": [
            {
                "trace_id": f"trace:{request_id}:needle_runtime",
                "span_id": "needle_runtime_adapter",
                "kind": "needle_runtime",
            }
        ],
    }
