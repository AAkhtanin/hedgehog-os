from __future__ import annotations

from demo.run_canonical_needle_outcome_trace import (
    collect_canonical_needle_outcome_trace,
)
from demo.run_canonical_needle_outcome_trace import run_canonical_needle_outcome_trace


SCENARIOS = {
    "needle_success_mock",
    "needle_timeout",
    "needle_invalid_json",
    "needle_contract_version_mismatch",
    "needle_permission_required",
    "needle_circuit_breaker_open",
    "needle_schema_validation_failed",
    "needle_unknown_exception",
}

FORBIDDEN_TERMS = {
    "raw_user_text",
    "api_key",
    "token",
    "secret",
    "password",
    "private_key",
    "passport_number",
    "card_number",
    "cvv",
    "hidden reasoning",
    "chain of thought",
}


def _rows_by_scenario():
    return {
        row.scenario: row for row in collect_canonical_needle_outcome_trace()
    }


def _assert_no_sensitive_terms_in_value(value):
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key).lower()
            assert key_text not in FORBIDDEN_TERMS
            _assert_no_sensitive_terms_in_value(child)
        return
    if isinstance(value, list):
        for child in value:
            _assert_no_sensitive_terms_in_value(child)
        return
    if isinstance(value, str):
        lowered = value.lower()
        for term in FORBIDDEN_TERMS:
            assert term not in lowered


def test_runner_output_contains_title_and_all_sections():
    output = run_canonical_needle_outcome_trace()

    assert "[CANONICAL NEEDLE OUTCOME TRACE]" in output
    assert "[NEEDLE OUTCOMES]" in output
    assert "[CANONICAL BOUNDARY]" in output
    assert "[POST V&V]" in output
    assert "[GT / ROOT DECISION]" in output
    assert "[DRS / AUDIT ROUTING]" in output
    assert "[SUMMARY]" in output


def test_runner_collects_all_eight_scenarios():
    rows = _rows_by_scenario()

    assert set(rows) == SCENARIOS


def test_every_scenario_crosses_canonical_boundary_and_post_vv():
    for row in collect_canonical_needle_outcome_trace():
        assert row.converted_to_result_proposal is True
        assert row.result_proposal_shape_valid is True
        assert row.post_vv_ran is True
        assert row.source.proposal["result_payload"]["source"] == "needle_runtime"


def test_gt_root_boundary_invariants_are_visible_in_output():
    output = run_canonical_needle_outcome_trace()

    assert "gt_boundary_after_post_vv: true" in output
    assert "gt_runtime_called: true" in output
    assert "gt_decision_mode: gt_validator_runtime" in output
    assert "canonical_gt_runtime_integration: true" in output
    assert "gt_report_present_count: 8" in output
    assert "unsafe_outcomes_not_marked_success: true" in output
    assert "invalid_json_not_success: true" in output
    assert "schema_validation_failed_not_success: true" in output
    assert "unknown_exception_not_success: true" in output
    assert "gt_committed_final_output: false" in output
    assert "needle_created_final_output: false" in output
    assert "executor_owns_needle: false" in output
    assert "direct_user_answers_from_needle: 0" in output
    assert "root_decisions_required: 8" in output
    assert "canonical_needle_outcome_trace_status: PASS" in output


def test_invalid_json_routes_to_quarantine():
    row = _rows_by_scenario()["needle_invalid_json"]

    assert row.source.needle_result.failure_kind == "invalid_json"
    assert row.root_visible_decision == "quarantine"
    assert row.intended_drs_route == "quarantine"
    assert row.source.needle_result.quarantine_required is True
    assert row.gt_report["decision"] != "accept"
    assert row.source.proposal["result_payload"]["task_completed"] is False


def test_schema_validation_failed_routes_to_quarantine():
    row = _rows_by_scenario()["needle_schema_validation_failed"]

    assert row.source.needle_result.failure_kind == "schema_validation_failed"
    assert row.root_visible_decision == "quarantine"
    assert row.intended_drs_route == "quarantine"
    assert row.source.needle_result.quarantine_required is True
    assert row.gt_report["decision"] != "accept"
    assert row.source.proposal["result_payload"]["task_completed"] is False


def test_permission_required_routes_to_needs_user_or_blocked():
    row = _rows_by_scenario()["needle_permission_required"]

    assert row.source.needle_result.failure_kind == "permission_required"
    assert row.root_visible_decision == "needs_user_or_blocked"
    assert row.intended_drs_route == "needs_user_or_blocked_trace"
    assert row.source.needle_result.permission_required is True
    assert row.gt_report["decision"] != "accept"


def test_circuit_breaker_open_routes_to_blocked():
    row = _rows_by_scenario()["needle_circuit_breaker_open"]

    assert row.source.needle_result.failure_kind == "circuit_breaker_open"
    assert row.root_visible_decision == "blocked"
    assert row.intended_drs_route == "blocked_trace"
    assert row.source.needle_result.circuit_breaker_opened is True


def test_timeout_routes_to_degraded_trace():
    row = _rows_by_scenario()["needle_timeout"]

    assert row.source.needle_result.failure_kind == "timeout"
    assert row.root_visible_decision == "degraded_trace"
    assert row.intended_drs_route == "degraded_trace"
    assert row.source.needle_result.status == "degraded"
    assert row.source.proposal["result_payload"]["status"] == "degraded"


def test_success_routes_to_work_candidate():
    row = _rows_by_scenario()["needle_success_mock"]

    assert row.source.needle_result.failure_kind == "none"
    assert row.root_visible_decision == "accept/work_candidate"
    assert row.intended_drs_route == "work_candidate"
    assert row.source.needle_result.status == "completed"
    assert row.gt_report["decision"] == "accept"
    assert row.gt_report.get("winner") == row.source.vv_report["proposal_id"]


def test_unknown_exception_is_contained_and_does_not_raise():
    row = _rows_by_scenario()["needle_unknown_exception"]

    assert row.source.needle_result.failure_kind == "unknown_exception"
    assert row.root_visible_decision == "failed_or_quarantine"
    assert row.intended_drs_route == "quarantine_or_failed_trace"
    assert row.source.needle_result.status == "failed"
    assert row.source.proposal["result_payload"]["root_crash_risk_contained"] is True
    assert row.gt_report["decision"] != "accept"
    assert row.source.proposal["result_payload"]["task_completed"] is False


def test_every_scenario_has_real_gt_report_after_post_vv():
    for row in collect_canonical_needle_outcome_trace():
        assert row.post_vv_ran is True
        assert row.gt_report.get("gt_report_id")
        assert row.gt_report.get("decision") in {"accept", "revise", "no_update"}
        assert "final_output" not in row.gt_report
        assert "answer" not in row.gt_report


def test_output_says_no_real_external_actions_and_no_unhandled_exceptions():
    output = run_canonical_needle_outcome_trace()

    assert "no_real_external_actions: true" in output
    assert "unhandled_exceptions: 0" in output
    assert "note: no real external actions" in output


def test_output_contains_no_sensitive_terms():
    output = run_canonical_needle_outcome_trace().lower()

    for term in FORBIDDEN_TERMS:
        assert term not in output


def test_underlying_payloads_contain_no_sensitive_terms_before_rendering():
    rows = collect_canonical_needle_outcome_trace()

    for row in rows:
        _assert_no_sensitive_terms_in_value(row.source.proposal)
        _assert_no_sensitive_terms_in_value(row.source.proposal["result_payload"])
        _assert_no_sensitive_terms_in_value(row.source.needle_result.result_payload)
        _assert_no_sensitive_terms_in_value(row.gt_report)
