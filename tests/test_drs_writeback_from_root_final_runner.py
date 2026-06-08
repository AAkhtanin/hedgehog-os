from __future__ import annotations

import pytest

from demo.run_drs_writeback_from_root_final import (
    SCENARIOS_UNDER_TEST,
    collect_drs_writeback_from_root_final,
    run_drs_writeback_from_root_final,
)


def _report():
    return collect_drs_writeback_from_root_final()


def _filters():
    return {row["scenario"]: row for row in _report().drs_writeback_input_filter}


def _records():
    return {
        row["root_final_status_seen"]: row
        for row in _report().drs_writeback_audit_records
    }


def test_runner_output_contains_required_sections():
    output = run_drs_writeback_from_root_final()

    for heading in (
        "[DRS WRITEBACK FROM ROOT FINAL]",
        "[INPUT ROOT FINAL ARTIFACTS]",
        "[DRS WRITEBACK INPUT FILTER]",
        "[DRS WRITEBACK AUDIT RECORDS]",
        "[CONTAINMENT]",
        "[AUTHORITY / SAFETY]",
        "[SUMMARY]",
    ):
        assert heading in output


def test_source_root_final_proof_status_is_pass():
    report = _report()

    assert report.input_root_final_artifacts["source_root_final_report_status"] == "PASS"
    assert report.summary["source_root_final_status"] == "PASS"
    assert len(report.input_root_final_artifacts["root_final_artifacts_imported"]) == 3


@pytest.mark.parametrize(
    ("status", "scenario"),
    [
        ("accepted", "accepted_root_final_creates_local_audit_record"),
        ("degraded", "degraded_root_final_creates_degraded_audit_record"),
        ("rejected", "rejected_root_final_creates_rejection_audit_record"),
    ],
)
def test_canonical_root_final_creates_local_audit_record(status, scenario):
    row = _filters()[scenario]
    record = _records()[status]

    assert row["drs_writeback_invoked"] is True
    assert row["input_is_root_final_artifact"] is True
    assert record["created_by"] == "root_orchestrator"
    assert record["root_final_status_seen"] == status
    assert record["writeback_scope"] == "local_audit_only"
    assert record["production_persistence"] is False
    assert record["global_drs_write"] is False
    assert record["external_drs_network_write"] is False
    assert record["real_external_action_executed"] is False
    assert record["time_envelope"]["time_basis"] == "deterministic_proof_clock"
    assert record["provenance"]["proof_only"] is True


def test_degraded_and_rejected_claims_remain_visible():
    records = _records()

    assert records["degraded"]["audit_summary"][
        "degraded_or_rejected_claims_visible"
    ] is True
    assert records["rejected"]["audit_summary"][
        "degraded_or_rejected_claims_visible"
    ] is True


@pytest.mark.parametrize(
    ("scenario", "reason"),
    [
        ("raw_gt_decision_blocked", "raw_gt_decision_not_allowed"),
        ("raw_validation_report_blocked", "raw_validation_report_not_allowed"),
        ("raw_result_proposal_blocked", "raw_result_proposal_not_allowed"),
        (
            "raw_architect_plan_graph_blocked",
            "raw_architect_plan_graph_not_allowed",
        ),
        ("raw_orchestrator_matrix_blocked", "raw_orchestrator_matrix_not_allowed"),
        ("raw_user_intent_blocked", "raw_user_intent_not_allowed"),
        ("real_action_output_blocked", "real_action_output_not_allowed"),
    ],
)
def test_raw_inputs_are_blocked(scenario, reason):
    row = _filters()[scenario]

    assert row["drs_writeback_invoked"] is False
    assert row["blocked_before_writeback"] is True
    assert reason in row["block_reasons"]


def test_malformed_root_final_artifact_is_rejected():
    row = _filters()["malformed_root_final_artifact_rejected"]

    assert row["blocked_before_writeback"] is True
    assert row["input_is_root_final_artifact"] is False
    assert "malformed_root_final_artifact" in row["block_reasons"]


def test_malicious_global_drs_write_claim_is_rejected():
    row = _filters()["malicious_root_final_claiming_global_drs_write_rejected"]

    assert row["blocked_before_writeback"] is True
    assert "global_drs_write_claim_rejected" in row["block_reasons"]
    assert _report().containment["malicious_global_drs_write_claim_passed"] is False


def test_malicious_external_drs_network_write_claim_is_rejected():
    row = _filters()[
        "malicious_root_final_claiming_external_drs_network_write_rejected"
    ]
    report = _report()

    assert row["blocked_before_writeback"] is True
    assert row["drs_writeback_invoked"] is False
    assert "external_drs_network_write_claim_rejected" in row["block_reasons"]
    assert report.containment["malicious_external_drs_network_claim_passed"] is False
    assert report.authority_safety["external_drs_network_implemented"] is False


def test_malicious_production_persistence_claim_is_rejected():
    row = _filters()["malicious_root_final_claiming_production_persistence_rejected"]
    report = _report()

    assert row["blocked_before_writeback"] is True
    assert row["drs_writeback_invoked"] is False
    assert "production_persistence_claim_rejected" in row["block_reasons"]
    assert report.containment["malicious_production_persistence_claim_passed"] is False
    assert report.authority_safety["production_persistence_claimed"] is False


def test_malicious_root_drs_write_claim_is_rejected():
    row = _filters()["malicious_root_final_claiming_root_drs_write_rejected"]

    assert row["blocked_before_writeback"] is True
    assert row["drs_writeback_invoked"] is False
    assert "root_drs_write_claim_rejected" in row["block_reasons"]
    assert _report().containment["malicious_root_drs_write_claim_passed"] is False


def test_malicious_action_claim_is_rejected():
    row = _filters()["malicious_root_final_claiming_action_rejected"]

    assert row["blocked_before_writeback"] is True
    assert "real_action_claim_rejected" in row["block_reasons"]
    assert _report().containment["malicious_action_claim_passed"] is False


def test_drs_writeback_receives_only_root_final_artifact():
    authority = _report().authority_safety

    assert authority["drs_writeback_receives_only_root_final_artifact"] is True
    assert authority["root_authority_preserved"] is True
    assert authority["drs_is_authority"] is False


def test_writeback_is_local_audit_only_without_production_persistence():
    report = _report()

    assert report.authority_safety["writeback_scope_local_audit_only"] is True
    assert report.authority_safety["production_persistence_claimed"] is False
    assert all(
        record["writeback_scope"] == "local_audit_only"
        for record in report.drs_writeback_audit_records
    )


def test_no_global_external_drs_or_real_action():
    report = _report()

    assert report.authority_safety["global_drs_implemented"] is False
    assert report.authority_safety["external_drs_network_implemented"] is False
    assert report.authority_safety["production_external_action_executed"] is False
    assert all(not record["global_drs_write"] for record in report.drs_writeback_audit_records)
    assert all(
        not record["external_drs_network_write"]
        for record in report.drs_writeback_audit_records
    )


def test_marennya_and_up_not_invoked():
    authority = _report().authority_safety

    assert authority["marennya_invoked"] is False
    assert authority["up_invoked"] is False


def test_pass_summary_is_derived_from_source_records_blocks_and_boundaries():
    report = _report()
    summary = report.summary

    derived_pass = (
        summary["source_root_final_status"] == "PASS"
        and summary["scenarios_verified"] == len(SCENARIOS_UNDER_TEST) == 16
        and summary["drs_writeback_records_created"] == 3
        and summary["accepted_writeback_records"] == 1
        and summary["degraded_writeback_records"] == 1
        and summary["rejected_writeback_records"] == 1
        and summary["raw_gt_decision_blocked"] is True
        and summary["raw_validation_report_blocked"] is True
        and summary["raw_result_proposal_blocked"] is True
        and summary["raw_architect_plan_graph_blocked"] is True
        and summary["raw_orchestrator_matrix_blocked"] is True
        and summary["raw_user_intent_blocked"] is True
        and summary["real_action_output_blocked"] is True
        and summary["malformed_root_final_artifact_rejected"] is True
        and summary["malicious_global_drs_write_claim_rejected"] is True
        and summary["malicious_external_drs_network_claim_rejected"] is True
        and summary["malicious_production_persistence_claim_rejected"] is True
        and summary["malicious_root_drs_write_claim_rejected"] is True
        and summary["malicious_action_claim_rejected"] is True
        and summary["drs_writeback_receives_only_root_final_artifact"] is True
        and summary["root_authority_preserved"] is True
        and summary["writeback_scope_local_audit_only"] is True
        and summary["production_persistence_claimed"] is False
        and summary["production_external_action_executed"] is False
    )

    assert derived_pass is True
    assert summary["drs_writeback_from_root_final_status"] == "PASS"
    assert summary["ready_for_full_cycle_with_drs_audit_trace"] is True
    assert summary["production_autonomy_claimed"] is False
