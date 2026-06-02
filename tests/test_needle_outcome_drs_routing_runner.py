from __future__ import annotations

from demo.run_needle_outcome_drs_routing import (
    collect_needle_outcome_drs_routing,
)
from demo.run_needle_outcome_drs_routing import run_needle_outcome_drs_routing


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
}


def _rows_by_scenario():
    return {row.scenario: row for row in collect_needle_outcome_drs_routing().rows}


def _assert_no_sensitive_terms(value):
    if isinstance(value, dict):
        for key, child in value.items():
            assert str(key).lower() not in FORBIDDEN_TERMS
            _assert_no_sensitive_terms(child)
        return
    if isinstance(value, list):
        for child in value:
            _assert_no_sensitive_terms(child)
        return
    if isinstance(value, str):
        lowered = value.lower()
        for term in FORBIDDEN_TERMS:
            assert term not in lowered


def test_runner_output_contains_required_sections_and_summary():
    output = run_needle_outcome_drs_routing()

    assert "[NEEDLE OUTCOME DRS ROUTING]" in output
    assert "[INPUT]" in output
    assert "[ROUTING TABLE]" in output
    assert "[DRS RECORDS]" in output
    assert "[REUSE SAFETY]" in output
    assert "[SUMMARY]" in output
    assert "needle_outcome_drs_routing_status: PASS" in output


def test_all_eight_scenarios_are_routed():
    rows = _rows_by_scenario()

    assert set(rows) == SCENARIOS


def test_success_writes_only_successful_work_candidate():
    report = collect_needle_outcome_drs_routing()
    row = {row.scenario: row for row in report.rows}["needle_success_mock"]
    successful_records = [
        record
        for record in report.records
        if record["content"]["successful_work_record"]
    ]

    assert row.persisted_record["layer"] == "work"
    assert row.persisted_record["type"] == "task_outcome"
    assert row.successful_work_record is True
    assert row.direct_reuse_eligible is True
    assert len(successful_records) == 1
    assert successful_records[0]["record_id"] == row.persisted_record["record_id"]


def test_invalid_json_writes_quarantine_not_work():
    row = _rows_by_scenario()["needle_invalid_json"]

    assert row.persisted_record["layer"] == "quarantine"
    assert row.quarantine is True
    assert row.successful_work_record is False
    assert row.direct_reuse_eligible is False


def test_schema_validation_failed_writes_quarantine_not_work():
    row = _rows_by_scenario()["needle_schema_validation_failed"]

    assert row.persisted_record["layer"] == "quarantine"
    assert row.quarantine is True
    assert row.successful_work_record is False
    assert row.direct_reuse_eligible is False


def test_unknown_exception_writes_quarantine_or_failed_trace_not_success():
    row = _rows_by_scenario()["needle_unknown_exception"]

    assert row.persisted_record["layer"] == "quarantine"
    assert row.quarantine is True
    assert row.successful_work_record is False
    assert row.direct_reuse_eligible is False
    assert row.source.source.proposal["result_payload"]["root_crash_risk_contained"] is True


def test_contract_version_mismatch_writes_deadend_blocked_trace():
    row = _rows_by_scenario()["needle_contract_version_mismatch"]

    assert row.persisted_record["layer"] == "deadends"
    assert row.persisted_record["type"] == "dead_end"
    assert row.deadend_or_blocked is True
    assert row.successful_work_record is False
    assert row.direct_reuse_eligible is False


def test_circuit_breaker_open_writes_deadend_blocked_trace():
    row = _rows_by_scenario()["needle_circuit_breaker_open"]

    assert row.persisted_record["layer"] == "deadends"
    assert row.persisted_record["type"] == "dead_end"
    assert row.deadend_or_blocked is True
    assert row.successful_work_record is False
    assert row.direct_reuse_eligible is False


def test_permission_required_writes_needs_user_blocked_trace():
    row = _rows_by_scenario()["needle_permission_required"]

    assert row.persisted_record["layer"] == "deadends"
    assert row.needs_user is True
    assert row.persisted_record["content"]["needle_status"] == "blocked"
    assert row.successful_work_record is False
    assert row.direct_reuse_eligible is False


def test_timeout_writes_degraded_trace_not_successful_work():
    row = _rows_by_scenario()["needle_timeout"]

    assert row.persisted_record["layer"] == "deadends"
    assert row.degraded is True
    assert row.successful_work_record is False
    assert row.direct_reuse_eligible is False


def test_every_persisted_record_has_required_audit_metadata():
    report = collect_needle_outcome_drs_routing()

    assert len(report.records) == 8
    for record in report.records:
        assert record["time_envelope"]
        assert record["provenance"]
        assert record["trace_refs"]
        assert record["provenance"]["trace_refs"]
        assert record["gt"]["gt_report_id"]
        assert record["validation"]["vv_report_id"]
        assert record["content"]["gt_decision"]
        assert record["content"]["sensitive_terms_absent"] is True
        assert record["content"]["no_real_external_action"] is True
        assert record["content"]["local_drs_only"] is True
        assert record["content"]["resolver_boundary"] == "local_only"


def test_no_persisted_record_contains_sensitive_terms():
    report = collect_needle_outcome_drs_routing()

    for record in report.records:
        _assert_no_sensitive_terms(record)


def test_direct_reuse_candidates_exclude_unsafe_layers_and_statuses():
    report = collect_needle_outcome_drs_routing()
    unsafe = [
        record
        for record in report.records
        if record["content"]["direct_reuse_eligible"]
        and (
            record["layer"] != "work"
            or not record["content"]["successful_work_record"]
            or record["content"]["quarantine"]
            or record["content"]["deadend_or_blocked"]
            or record["content"]["degraded"]
            or record["content"]["needle_status"] in {"failed", "blocked", "quarantined"}
        )
    ]

    assert unsafe == []


def test_runner_output_marks_local_only_and_no_global_drs():
    output = run_needle_outcome_drs_routing()

    assert "local_drs_only: true" in output
    assert "external_drs_network_implemented: false" in output
    assert "global_drs_implemented: false" in output
    assert "direct_reuse_unsafe_candidates: 0" in output
    assert "no_real_external_actions: true" in output


def test_audit_trace_count_matches_total_records():
    output = run_needle_outcome_drs_routing()

    assert "total_records_written: 8" in output
    assert "audit_or_trace_records: 8" in output
    assert "audit_trace_embedded_in_records: true" in output
