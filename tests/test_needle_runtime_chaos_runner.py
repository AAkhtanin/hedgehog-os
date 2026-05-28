from __future__ import annotations

from demo.run_needle_runtime_chaos import collect_needle_runtime_chaos
from demo.run_needle_runtime_chaos import run_needle_runtime_chaos
from hedgehog.needle_runtime import NeedleCall
from hedgehog.needle_runtime import execute_needle_call


FORBIDDEN_TERMS = {
    "raw_user_text",
    "api_key",
    "token",
    "secret",
    "hidden reasoning",
    "chain of thought",
}


def _call(
    scenario: str,
    *,
    permission_confirmed: bool = True,
    contract_version: str = "1.0",
    required_contract_version: str = "1.0",
) -> NeedleCall:
    return NeedleCall(
        needle_id="test_needle",
        capability="mock_capability",
        contract_version=contract_version,
        required_contract_version=required_contract_version,
        payload={"slot": "value"},
        permission_confirmed=permission_confirmed,
        timeout_ms=100,
        scenario=scenario,
    )


def test_success_scenario_completes():
    result = execute_needle_call(_call("needle_success_mock"))

    assert result.status == "completed"
    assert result.failure_kind == "none"
    assert result.result_proposal_status == "completed"
    assert result.quarantine_required is False
    assert result.no_real_external_action is True


def test_timeout_returns_structured_degraded_result():
    result = execute_needle_call(_call("needle_timeout"))

    assert result.status == "degraded"
    assert result.failure_kind == "timeout"
    assert result.result_proposal_status == "degraded"
    assert result.no_real_external_action is True


def test_invalid_json_quarantines_structurally():
    result = execute_needle_call(_call("needle_invalid_json"))

    assert result.status == "quarantined"
    assert result.failure_kind == "invalid_json"
    assert result.quarantine_required is True
    assert result.result_proposal_status == "failed"


def test_contract_version_mismatch_blocks():
    result = execute_needle_call(
        _call(
            "needle_success_mock",
            contract_version="0.9",
            required_contract_version="1.0",
        )
    )

    assert result.status == "blocked"
    assert result.failure_kind == "contract_version_mismatch"
    assert result.result_proposal_status == "blocked"


def test_missing_permission_blocks_before_execution():
    result = execute_needle_call(
        _call("needle_success_mock", permission_confirmed=False)
    )

    assert result.status == "blocked"
    assert result.failure_kind == "permission_required"
    assert result.permission_required is True
    assert result.result_proposal_status == "blocked"


def test_circuit_breaker_open_blocks():
    result = execute_needle_call(_call("needle_circuit_breaker_open"))

    assert result.status == "blocked"
    assert result.failure_kind == "circuit_breaker_open"
    assert result.circuit_breaker_opened is True
    assert result.result_proposal_status == "blocked"


def test_schema_validation_failure_quarantines():
    result = execute_needle_call(_call("needle_schema_validation_failed"))

    assert result.status == "quarantined"
    assert result.failure_kind == "schema_validation_failed"
    assert result.quarantine_required is True
    assert result.result_proposal_status == "failed"


def test_unknown_exception_does_not_escape():
    result = execute_needle_call(_call("needle_unknown_exception"))

    assert result.status == "failed"
    assert result.failure_kind == "unknown_exception"
    assert result.quarantine_required is True
    assert result.result_proposal_status == "failed"
    assert result.result_payload["exception_type"] == "RuntimeError"


def test_demo_collects_all_scenarios():
    rows = collect_needle_runtime_chaos()
    scenarios = {row.scenario for row in rows}

    assert scenarios == {
        "needle_success_mock",
        "needle_timeout",
        "needle_invalid_json",
        "needle_contract_version_mismatch",
        "needle_permission_required",
        "needle_circuit_breaker_open",
        "needle_schema_validation_failed",
        "needle_unknown_exception",
    }


def test_demo_output_has_summary_and_no_sensitive_terms():
    output = run_needle_runtime_chaos()
    lowered = output.lower()

    assert "[NEEDLE RUNTIME CHAOS]" in output
    assert "unhandled_exceptions: 0" in output
    assert "no_real_external_actions: true" in output
    assert "root_crash_risk_contained: true" in output
    for scenario in [
        "needle_success_mock",
        "needle_timeout",
        "needle_invalid_json",
        "needle_contract_version_mismatch",
        "needle_permission_required",
        "needle_circuit_breaker_open",
        "needle_schema_validation_failed",
        "needle_unknown_exception",
    ]:
        assert scenario in output
    for term in FORBIDDEN_TERMS:
        assert term not in lowered
