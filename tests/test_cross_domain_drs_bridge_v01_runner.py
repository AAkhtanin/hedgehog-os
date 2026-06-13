from __future__ import annotations

import pytest

from demo.run_audit_hash_chain import canonical_hash
from demo.run_cross_domain_drs_bridge_v01 import (
    collect_cross_domain_drs_bridge_v01,
    render_cross_domain_drs_bridge_v01,
)


@pytest.fixture(scope="module")
def report():
    return collect_cross_domain_drs_bridge_v01()


def _by_id(rows, key):
    return {row[key]: row for row in rows}


def test_runner_title_and_required_sections_exist(report):
    output = render_cross_domain_drs_bridge_v01(report)
    for heading in (
        "[CROSS-DOMAIN DRS BRIDGE v0.1]",
        "[SOURCE EVIDENCE]",
        "[BRIDGE REGISTRY]",
        "[TRAVERSAL REQUEST]",
        "[TRAVERSAL STEPS]",
        "[BRIDGE BOUNDARY MATRIX]",
        "[TRAVERSAL RESULT]",
        "[CONFLICTCHECK]",
        "[GT ADVISORY]",
        "[ROOT FINAL]",
        "[AUDIT]",
        "[SUMMARY]",
    ):
        assert heading in output


def test_all_source_statuses_pass(report):
    assert set(report.source_evidence.values()) == {"PASS"}


def test_exactly_two_bridge_records_observed(report):
    assert len(report.bridge_registry) == 2


def test_bridge_records_map_certificate_evidence_to_travel_checks(report):
    bridges = _by_id(report.bridge_registry, "bridge_id")
    insurance = bridges["bridge_certificate_insurance_to_travel_document_v01"]
    payment = bridges["bridge_certificate_payment_to_travel_payment_v01"]
    assert (insurance["semantic_field"], insurance["semantic_value"]) == (
        "insurance_certificate",
        "expired",
    )
    assert insurance["target_cell"] == "travel_document_check"
    assert (payment["semantic_field"], payment["semantic_value"]) == (
        "payment_receipt",
        "missing",
    )
    assert payment["target_cell"] == "travel_payment_check"


def test_bridge_records_are_local_proof_only_without_external_pointer(report):
    assert all(
        row["bridge_status"] == "active_local_proof_only"
        and row["external_drs_pointer_created"] is False
        for row in report.bridge_registry
    )


def test_bridge_records_transfer_no_authority_final_or_execution(report):
    assert all(
        row["transfers_authority"] is False
        and row["transfers_final"] is False
        and row["transfers_execution"] is False
        for row in report.bridge_registry
    )


def test_traversal_request_is_root_authorized_local_proof(report):
    request = report.traversal_request
    assert request["requested_by"] == "Root"
    assert request["root_authorized_traversal"] is True
    assert request["traversal_is_local_proof_only"] is True


def test_traversal_can_inform_but_not_decide_execute_or_finalize(report):
    request = report.traversal_request
    assert request["traversal_can_inform"] is True
    assert request["traversal_can_decide"] is False
    assert request["traversal_can_execute"] is False
    assert request["traversal_can_finalize"] is False


def test_exactly_two_traversal_steps_exist(report):
    assert len(report.traversal_steps) == 2


def test_steps_inform_target_checks_but_cannot_mark_ready(report):
    assert all(
        row["local_effect"] == "inform_target_check"
        and row["marks_target_parent_ready"] is False
        for row in report.traversal_steps
    )


def test_steps_cannot_finalize_target_parent(report):
    assert all(row["finalizes_target_parent"] is False for row in report.traversal_steps)


def test_steps_cannot_execute_or_write_drs(report):
    assert all(
        row["executes_external_action"] is False
        and row["writes_global_drs"] is False
        and row["writes_external_drs"] is False
        for row in report.traversal_steps
    )


def test_bridge_boundary_can_inform_but_cannot_decide(report):
    assert all(
        row["bridge_can_inform"] is True and row["bridge_can_decide"] is False
        for row in report.bridge_boundary_matrix
    )


def test_bridge_boundary_transfers_no_root_final_execution_or_drs_write(report):
    fields = (
        "bridge_transfers_root",
        "bridge_transfers_final",
        "bridge_transfers_execution",
        "bridge_transfers_drs_write",
    )
    assert all(
        all(row[field] is False for field in fields)
        for row in report.bridge_boundary_matrix
    )


def test_source_and_target_domains_cannot_cross_finalize(report):
    assert all(
        row["source_domain_can_finalize_target"] is False
        and row["target_domain_can_finalize_source"] is False
        for row in report.bridge_boundary_matrix
    )


def test_traversal_result_is_completed_local_proof(report):
    assert report.traversal_result["traversal_status"] == "completed_local_proof"


def test_target_is_informed_but_not_decided_by_traversal(report):
    result = report.traversal_result
    assert result["target_domain_informed"] is True
    assert result["target_domain_decided_by_traversal"] is False
    assert result["target_parent_finalized_by_traversal"] is False


def test_target_result_after_root_review_remains_not_ready(report):
    assert report.traversal_result["target_parent_result_after_root_review"] == (
        "not_ready"
    )


def test_bridge_is_not_authority_and_trace_is_not_truth(report):
    result = report.traversal_result
    assert result["drs_bridge_is_not_authority"] is True
    assert result["traversal_trace_is_not_truth"] is True


def test_conflictcheck_detects_escalation_attempt_but_is_advisory(report):
    conflict = report.conflictcheck_result
    assert conflict["conflict_detected"] is True
    assert conflict["reason"] == (
        "drs_bridge_traversal_cannot_transfer_authority_or_finalize_target_parent"
    )
    assert conflict["conflictcheck_is_authority"] is False


def test_gt_cannot_escalate_bridge_or_execute(report):
    gt = report.gt_advisory
    assert gt["gt_recommendation"] == "target_parent_not_ready"
    for field in (
        "gt_can_mark_target_ready",
        "gt_can_execute_action",
        "gt_can_grant_bridge_authority",
        "gt_can_create_external_drs_pointer",
        "gt_can_install_needle",
    ):
        assert gt[field] is False


def test_root_final_remains_not_ready_with_safe_secondary(report):
    root = report.root_final
    assert root["root_result"] == "not_ready"
    assert root["safe_secondary_outcome"] == "needs_user_travel_update"
    assert root["root_remains_final_authority"] is True


def test_root_says_bridge_informed_but_did_not_decide_or_transfer(report):
    root = report.root_final
    assert root["drs_bridge_informed_target"] is True
    assert root["drs_bridge_decided_target"] is False
    assert root["traversal_finalized_target"] is False
    assert root["bridge_transferred_authority"] is False


def test_no_external_or_global_drs_or_production_persistence(report):
    root = report.root_final
    assert root["external_drs_pointer_created"] is False
    assert root["global_drs_write"] is False
    assert root["external_drs_write"] is False
    assert root["production_persistence"] is False


def test_no_external_action_or_submissions_booking_payment(report):
    root = report.root_final
    for field in (
        "completed_external_action_created",
        "travel_request_submitted",
        "certificate_request_submitted",
        "booking_created",
        "payment_executed",
    ):
        assert root[field] is False


def test_no_protocol_candidate_needle_candidate_or_installed_needle(report):
    root = report.root_final
    assert root["protocol_candidate_created"] is False
    assert root["needle_candidate_created"] is False
    assert root["installed_needle_created"] is False


def test_no_external_system_or_deferred_layer_invoked(report):
    for field in (
        "gemini_called",
        "network_called",
        "telegram_used",
        "marennya_invoked",
        "up_invoked",
    ):
        assert report.summary[field] is False


def test_non_overclaim_flags_prove_local_bridge_only(report):
    summary = report.summary
    assert summary["external_drs_implemented"] is False
    assert summary["global_semantic_fabric_claimed"] is False
    assert summary["real_connector_used"] is False
    non_overclaim = report.proof_artifact["non_overclaim"]
    assert non_overclaim["cross_domain_drs_traversal_observed"] is True
    assert non_overclaim["local_drs_bridge_proof_only"] is True


def test_audit_hash_matches_proof_artifact(report):
    assert report.audit_entry["canonical_payload_hash"] == canonical_hash(
        report.proof_artifact
    )
    assert report.audit_entry["proof_only"] is True
    assert report.audit_entry["audit_chain_decides_truth"] is False


def test_summary_pass_and_ready_for_tests(report):
    summary = report.summary
    assert summary["cross_domain_drs_bridge_v01_status"] == "PASS"
    assert summary["bridge_records_observed"] == 2
    assert summary["traversal_steps_observed"] == 2
    assert summary["root_remains_final_authority"] is True
    assert summary["ready_for_cross_domain_drs_bridge_v01_tests"] is True
