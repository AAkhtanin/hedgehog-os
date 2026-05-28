from __future__ import annotations

from demo.run_needle_failure_integration import collect_needle_failure_integration
from demo.run_needle_failure_integration import run_needle_failure_integration
from hedgehog.needle_runtime import NeedleCall
from hedgehog.needle_runtime import execute_needle_call
from hedgehog.needle_runtime import needle_result_to_result_proposal
from hedgehog.post_vv import validate_result_proposal


FORBIDDEN_TERMS = {
    "raw_user_text",
    "api_key",
    "token",
    "secret",
    "hidden reasoning",
    "chain of thought",
}


def _call(scenario: str, *, permission_confirmed: bool = True) -> NeedleCall:
    return NeedleCall(
        needle_id="test_needle",
        capability="mock_capability",
        contract_version="1.0",
        required_contract_version="1.0",
        payload={"slot": "value"},
        permission_confirmed=permission_confirmed,
        timeout_ms=100,
        scenario=scenario,
    )


def _proposal_for(scenario: str):
    result = execute_needle_call(_call(scenario))
    return needle_result_to_result_proposal(result, request_id=f"test_{scenario}")


def test_adapter_maps_completed_needle_to_completed_proposal():
    proposal = _proposal_for("needle_success_mock")
    payload = proposal["result_payload"]
    vv_report = validate_result_proposal(proposal)

    assert payload["source"] == "needle_runtime"
    assert payload["status"] == "completed"
    assert payload["failure_kind"] == "none"
    assert payload["safe_for_gt"] is True
    assert vv_report["execution_status"] == "completed"


def test_adapter_maps_blocked_needle_to_blocked_proposal():
    result = execute_needle_call(_call("needle_success_mock", permission_confirmed=False))
    proposal = needle_result_to_result_proposal(result, request_id="test_blocked")
    payload = proposal["result_payload"]
    vv_report = validate_result_proposal(proposal)

    assert payload["status"] == "blocked"
    assert payload["failure_kind"] == "permission_required"
    assert payload["permission_required"] is True
    assert payload["safe_for_gt"] is True
    assert vv_report["execution_status"] == "blocked"


def test_adapter_maps_degraded_timeout_to_degraded_proposal():
    proposal = _proposal_for("needle_timeout")
    payload = proposal["result_payload"]
    vv_report = validate_result_proposal(proposal)

    assert payload["status"] == "degraded"
    assert payload["failure_kind"] == "timeout"
    assert payload["safe_for_gt"] is True
    assert vv_report["execution_status"] == "degraded"


def test_adapter_maps_invalid_json_and_schema_failure_to_quarantine_caution():
    for scenario, failure_kind in [
        ("needle_invalid_json", "invalid_json"),
        ("needle_schema_validation_failed", "schema_validation_failed"),
    ]:
        proposal = _proposal_for(scenario)
        payload = proposal["result_payload"]
        vv_report = validate_result_proposal(proposal)

        assert payload["status"] == "failed"
        assert payload["failure_kind"] == failure_kind
        assert payload["quarantine_required"] is True
        assert payload["safe_for_gt"] is False
        assert vv_report["execution_status"] == "failed"


def test_adapter_maps_unknown_exception_without_throwing():
    proposal = _proposal_for("needle_unknown_exception")
    payload = proposal["result_payload"]
    vv_report = validate_result_proposal(proposal)

    assert payload["status"] == "failed"
    assert payload["failure_kind"] == "unknown_exception"
    assert payload["safe_for_gt"] is False
    assert payload["root_crash_risk_contained"] is True
    assert vv_report["execution_status"] == "failed"


def test_demo_collects_all_needle_failure_integration_scenarios():
    rows = collect_needle_failure_integration()
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
    for row in rows:
        assert row.proposal["result_payload"]["source"] == "needle_runtime"
        assert row.proposal["result_payload"]["no_real_external_action"] is True
        assert row.proposal["result_payload"]["root_crash_risk_contained"] is True


def test_demo_output_has_summary_and_no_sensitive_terms():
    output = run_needle_failure_integration()
    lowered = output.lower()

    assert "[NEEDLE FAILURE INTEGRATION]" in output
    assert "demo-level integration adapter, not full Root integration yet" in output
    assert "scenarios: 8" in output
    assert "completed_proposals:" in output
    assert "blocked_proposals:" in output
    assert "degraded_proposals:" in output
    assert "failed_or_quarantined_proposals:" in output
    assert "safe_for_gt_count:" in output
    assert "unsafe_or_caution_for_gt_count:" in output
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
