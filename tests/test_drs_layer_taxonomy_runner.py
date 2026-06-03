from __future__ import annotations

from demo.run_drs_layer_taxonomy import collect_drs_layer_taxonomy
from demo.run_drs_layer_taxonomy import run_drs_layer_taxonomy


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


def _rows_by_scenario():
    return {row.scenario: row for row in collect_drs_layer_taxonomy().rows}


def test_runner_output_contains_required_sections() -> None:
    output = run_drs_layer_taxonomy()

    assert "[DRS LAYER TAXONOMY]" in output
    assert "[INPUT]" in output
    assert "[TAXONOMY TABLE]" in output
    assert "[SAFETY]" in output
    assert "[SUMMARY]" in output
    assert "drs_layer_taxonomy_status: PASS" in output


def test_eight_records_are_classified() -> None:
    report = collect_drs_layer_taxonomy()

    assert len(report.rows) == 8
    assert set(_rows_by_scenario()) == SCENARIOS
    assert report.summary["records_classified"] == 8


def test_success_is_work_candidate_and_only_direct_reuse_candidate() -> None:
    report = collect_drs_layer_taxonomy()
    row = _rows_by_scenario()["needle_success_mock"]
    direct_reuse_rows = [row for row in report.rows if row.direct_reuse_eligible]

    assert row.taxonomy_kind == "work_candidate"
    assert row.routing_class == "successful_work"
    assert row.original_layer == "work"
    assert row.successful_work_record is True
    assert row.direct_reuse_eligible is True
    assert row.reuse_policy == "eligible_work_only"
    assert len(direct_reuse_rows) == 1
    assert direct_reuse_rows[0].scenario == "needle_success_mock"


def test_invalid_json_is_quarantine_not_work() -> None:
    row = _rows_by_scenario()["needle_invalid_json"]

    assert row.taxonomy_kind == "quarantine"
    assert row.routing_class == "invalid_payload"
    assert row.original_layer == "quarantine"
    assert row.work_allowed is False
    assert row.quarantine_allowed is True
    assert row.successful_work_record is False
    assert row.direct_reuse_eligible is False


def test_schema_validation_failed_is_quarantine_not_work() -> None:
    row = _rows_by_scenario()["needle_schema_validation_failed"]

    assert row.taxonomy_kind == "quarantine"
    assert row.routing_class == "schema_failed"
    assert row.original_layer == "quarantine"
    assert row.work_allowed is False
    assert row.quarantine_allowed is True
    assert row.successful_work_record is False
    assert row.direct_reuse_eligible is False


def test_unknown_exception_is_quarantine_or_failed_trace_not_work() -> None:
    row = _rows_by_scenario()["needle_unknown_exception"]

    assert row.taxonomy_kind in {"quarantine", "failed_trace"}
    assert row.routing_class == "unknown_exception"
    assert row.original_layer == "quarantine"
    assert row.work_allowed is False
    assert row.successful_work_record is False
    assert row.direct_reuse_eligible is False


def test_timeout_is_degraded_trace_not_successful_work() -> None:
    row = _rows_by_scenario()["needle_timeout"]

    assert row.taxonomy_kind == "degraded_trace"
    assert row.routing_class == "timeout"
    assert row.degraded is True
    assert row.stable_dead_end is False
    assert row.successful_work_record is False
    assert row.direct_reuse_eligible is False


def test_permission_required_is_needs_user_trace_not_completed_action() -> None:
    row = _rows_by_scenario()["needle_permission_required"]

    assert row.taxonomy_kind == "needs_user_trace"
    assert row.routing_class == "permission_required"
    assert row.needs_user is True
    assert row.stable_dead_end is False
    assert row.successful_work_record is False
    assert row.direct_reuse_eligible is False


def test_contract_version_mismatch_is_deadend_or_blocked_not_success() -> None:
    row = _rows_by_scenario()["needle_contract_version_mismatch"]

    assert row.taxonomy_kind in {"dead_end", "blocked_trace"}
    assert row.routing_class == "contract_boundary"
    assert row.blocked is True
    assert row.successful_work_record is False
    assert row.direct_reuse_eligible is False
    if row.taxonomy_kind == "dead_end":
        assert row.stable_dead_end is True


def test_circuit_breaker_open_is_blocked_or_deadend_not_success() -> None:
    row = _rows_by_scenario()["needle_circuit_breaker_open"]

    assert row.taxonomy_kind in {"blocked_trace", "dead_end"}
    assert row.routing_class == "circuit_breaker"
    assert row.blocked is True
    assert row.successful_work_record is False
    assert row.direct_reuse_eligible is False


def test_safety_counts_prevent_unsafe_direct_reuse() -> None:
    safety = collect_drs_layer_taxonomy().safety

    assert safety["taxonomy_does_not_override_policy"] is True
    assert safety["successful_work_records"] == 1
    assert safety["direct_reuse_candidates"] == 1
    assert safety["unsafe_direct_reuse_candidates"] == 0
    assert safety["quarantine_direct_reuse_candidates"] == 0
    assert safety["deadend_direct_reuse_candidates"] == 0
    assert safety["blocked_direct_reuse_candidates"] == 0
    assert safety["degraded_direct_reuse_candidates"] == 0
    assert safety["needs_user_direct_reuse_candidates"] == 0
    assert safety["degraded_trace_not_successful_work"] is True
    assert safety["needs_user_trace_not_completed_action"] is True
    assert safety["blocked_trace_not_success"] is True
    assert safety["quarantine_not_work"] is True


def test_taxonomy_does_not_override_policy_is_derived_from_rows() -> None:
    report = collect_drs_layer_taxonomy()
    unsafe_taxonomy_kinds = {
        "quarantine",
        "dead_end",
        "blocked_trace",
        "degraded_trace",
        "needs_user_trace",
    }
    direct_reuse_rows = [row for row in report.rows if row.direct_reuse_eligible]
    expected = (
        all(row.successful_work_record for row in direct_reuse_rows)
        and all(row.taxonomy_kind == "work_candidate" for row in direct_reuse_rows)
        and not any(
            row.direct_reuse_eligible and row.taxonomy_kind in unsafe_taxonomy_kinds
            for row in report.rows
        )
    )

    assert report.safety["taxonomy_does_not_override_policy"] is expected


def test_broad_deadends_semantics_clarified_is_derived_from_rows() -> None:
    report = collect_drs_layer_taxonomy()
    rows_by_failure = {row.failure_kind: row for row in report.rows}
    expected = (
        report.summary["degraded_trace_records"] >= 1
        and report.summary["needs_user_trace_records"] >= 1
        and report.summary["dead_end_or_blocked_records"] >= 2
        and rows_by_failure["timeout"].taxonomy_kind == "degraded_trace"
        and rows_by_failure["permission_required"].taxonomy_kind == "needs_user_trace"
    )

    assert report.summary["broad_deadends_semantics_clarified"] is expected


def test_direct_reuse_policy_unchanged_is_derived_from_rows() -> None:
    report = collect_drs_layer_taxonomy()
    direct_reuse_rows = [row for row in report.rows if row.direct_reuse_eligible]
    expected = (
        report.safety["direct_reuse_candidates"] == 1
        and report.safety["unsafe_direct_reuse_candidates"] == 0
        and len(direct_reuse_rows) == 1
        and direct_reuse_rows[0].scenario == "needle_success_mock"
        and direct_reuse_rows[0].taxonomy_kind == "work_candidate"
        and direct_reuse_rows[0].successful_work_record is True
    )

    assert report.summary["direct_reuse_policy_unchanged"] is expected


def test_summary_marks_local_only_no_schema_refactor_and_policy_unchanged() -> None:
    summary = collect_drs_layer_taxonomy().summary

    assert summary["drs_layer_taxonomy_status"] == "PASS"
    assert summary["work_candidates"] == 1
    assert summary["quarantine_records"] == 3
    assert summary["dead_end_or_blocked_records"] >= 2
    assert summary["degraded_trace_records"] >= 1
    assert summary["needs_user_trace_records"] >= 1
    assert summary["broad_deadends_semantics_clarified"] is True
    assert summary["direct_reuse_policy_unchanged"] is True
    assert summary["unsafe_direct_reuse_candidates"] == 0
    assert summary["local_drs_only"] is True
    assert summary["external_drs_network_implemented"] is False
    assert summary["global_drs_implemented"] is False
    assert summary["schema_refactor_performed"] is False


def test_runner_output_contains_required_safety_lines() -> None:
    output = run_drs_layer_taxonomy()

    assert "records_loaded: 8" in output
    assert "taxonomy_does_not_override_policy: true" in output
    assert "direct_reuse_policy_unchanged: true" in output
    assert "unsafe_direct_reuse_candidates: 0" in output
    assert "degraded_trace_not_successful_work: true" in output
    assert "needs_user_trace_not_completed_action: true" in output
    assert "blocked_trace_not_success: true" in output
    assert "quarantine_not_work: true" in output
    assert "external_drs_network_implemented: false" in output
    assert "global_drs_implemented: false" in output
    assert "schema_refactor_performed: false" in output


def test_output_has_no_sensitive_terms() -> None:
    output = run_drs_layer_taxonomy().lower()
    forbidden = {
        "raw_user_text",
        "api_key",
        "token",
        "secret",
        "password",
        "private_key",
        "passport_number",
        "card_number",
        "cvv",
        "chain of thought",
    }
    for term in forbidden:
        assert term not in output
