from __future__ import annotations

import pytest

from demo.run_audit_hash_chain import canonical_hash
from demo.run_controlled_fractal_dac_expansion_v01 import (
    collect_controlled_fractal_dac_expansion_v01,
    render_controlled_fractal_dac_expansion_v01,
)


@pytest.fixture(scope="module")
def report():
    return collect_controlled_fractal_dac_expansion_v01()


def _by_id(rows, key):
    return {row[key]: row for row in rows}


def test_runner_title_and_required_sections_exist(report):
    output = render_controlled_fractal_dac_expansion_v01(report)
    for heading in (
        "[CONTROLLED FRACTAL DAC EXPANSION v0.1]",
        "[SOURCE EVIDENCE]",
        "[PARENT REQUEST]",
        "[DECOMPOSITION PLAN]",
        "[CHILD CELL CANDIDATES]",
        "[CHILD CELL LOCAL PROPOSALS]",
        "[AUTHORITY BOUNDARY MATRIX]",
        "[AGGREGATION RESULT]",
        "[CONFLICTCHECK]",
        "[GT ADVISORY]",
        "[ROOT FINAL]",
        "[AUDIT]",
        "[SUMMARY]",
    ):
        assert heading in output


def test_all_source_statuses_pass(report):
    assert set(report.source_evidence.values()) == {"PASS"}


def test_parent_request_and_root_final_requirement(report):
    parent = report.parent_request
    assert parent["request_id"] == "TRAVEL-900"
    assert parent["itinerary_id"] == "ITIN-44"
    assert parent["root_is_parent_authority"] is True
    assert parent["root_final_required"] is True


def test_decomposition_plan_creates_five_bounded_candidates(report):
    plan = report.decomposition_plan
    assert plan["child_cells_planned"] == 5
    assert plan["child_cells_created"] is True
    assert plan["child_cells_are_candidates"] is True
    assert plan["child_cells_are_runtime_local_only"] is True
    assert plan["child_cells_are_not_production_agents"] is True


def test_all_expected_child_cells_exist(report):
    assert {row["child_cell_id"] for row in report.child_cell_candidates} == {
        "document_check",
        "payment_check",
        "lodging_check",
        "route_window_check",
        "permission_check",
    }


def test_four_expected_child_cells_are_blocked(report):
    children = _by_id(report.child_cell_candidates, "child_cell_id")
    for child_id in (
        "document_check",
        "payment_check",
        "route_window_check",
        "permission_check",
    ):
        assert children[child_id]["local_status"] == "blocked"


def test_lodging_check_is_ready(report):
    children = _by_id(report.child_cell_candidates, "child_cell_id")
    assert children["lodging_check"]["local_status"] == "ready"
    assert children["lodging_check"]["local_proposal"] == "lodging_ok"


def test_every_child_has_no_root_authority(report):
    assert all(row["root_authority"] is False for row in report.child_cell_candidates)


def test_every_child_has_no_final_output_authority(report):
    assert all(
        row["final_output_authority"] is False
        for row in report.child_cell_candidates
    )


def test_every_child_has_no_external_action_authority(report):
    assert all(
        row["external_action_authority"] is False
        for row in report.child_cell_candidates
    )


def test_every_child_has_no_drs_write_authority(report):
    assert all(
        row["drs_write_authority"] is False for row in report.child_cell_candidates
    )


def test_no_child_can_escalate_or_create_candidates(report):
    forbidden_capabilities = (
        "can_mark_parent_ready",
        "can_override_sibling",
        "can_spawn_child",
        "can_install_needle",
        "can_create_protocol_candidate",
        "can_create_needle_candidate",
    )
    assert all(
        all(row[field] is False for field in forbidden_capabilities)
        for row in report.child_cell_candidates
    )


def test_authority_matrix_requires_root_review_and_aggregation(report):
    assert len(report.authority_boundary_matrix) == 5
    assert all(
        row["root_review_required"] is True
        and row["root_aggregation_required"] is True
        and row["sibling_authority"] is False
        for row in report.authority_boundary_matrix
    )


def test_aggregation_counts_and_result(report):
    aggregation = report.aggregation_result
    assert aggregation["child_cells_observed"] == 5
    assert aggregation["blocked_child_cells"] == 4
    assert aggregation["ready_child_cells"] == 1
    assert aggregation["aggregate_result"] == "not_ready"


def test_consensus_and_majority_vote_are_not_root(report):
    aggregation = report.aggregation_result
    assert aggregation["child_cell_consensus_is_not_root"] is True
    assert aggregation["majority_vote_is_not_root"] is True
    assert aggregation["aggregation_is_not_final_until_root"] is True


def test_conflictcheck_detects_parent_ready_contradiction(report):
    conflict = report.conflictcheck_result
    assert conflict["conflict_detected"] is True
    assert conflict["reason"] == (
        "parent_ready_claim_contradicts_blocked_child_cell_proposals"
    )
    assert conflict["conflictcheck_is_authority"] is False


def test_gt_is_advisory_and_cannot_escalate(report):
    gt = report.gt_advisory
    assert gt["gt_recommendation"] == "not_ready"
    assert gt["gt_is_advisory"] is True
    assert gt["gt_can_mark_parent_ready"] is False
    assert gt["gt_can_execute_action"] is False
    assert gt["gt_can_grant_child_authority"] is False
    assert gt["gt_can_install_needle"] is False


def test_root_final_remains_not_ready_with_safe_secondary(report):
    root = report.root_final
    assert root["root_result"] == "not_ready"
    assert root["safe_secondary_outcome"] == "needs_user_travel_update"
    assert root["root_remains_final_authority"] is True


def test_root_final_does_not_grant_child_authority_or_finalization(report):
    root = report.root_final
    assert root["child_cells_created"] is True
    assert root["child_cells_have_authority"] is False
    assert root["child_cells_finalized_result"] is False


def test_no_external_action_travel_submission_booking_or_payment(report):
    root = report.root_final
    for field in (
        "completed_external_action_created",
        "travel_request_submitted",
        "booking_created",
        "payment_executed",
    ):
        assert root[field] is False


def test_no_protocol_candidate_needle_candidate_or_installed_needle(report):
    root = report.root_final
    assert root["protocol_candidate_created"] is False
    assert root["needle_candidate_created"] is False
    assert root["installed_needle_created"] is False


def test_no_production_global_or_external_drs_persistence(report):
    root = report.root_final
    assert root["production_persistence"] is False
    assert root["global_drs_write"] is False
    assert root["external_drs_write"] is False
    assert all(
        row["production_persistence"] is False
        and row["global_drs_write"] is False
        and row["external_drs_write"] is False
        for row in report.child_cell_candidates
    )


def test_no_external_system_or_deferred_layer_invoked(report):
    summary = report.summary
    for field in (
        "gemini_called",
        "network_called",
        "telegram_used",
        "marennya_invoked",
        "up_invoked",
    ):
        assert summary[field] is False


def test_non_overclaim_flags_prove_controlled_expansion_only(report):
    summary = report.summary
    assert summary["fractal_dac_expansion_observed"] is True
    assert summary["controlled_fractal_expansion_only"] is True
    assert summary["real_child_agents_started"] is False
    assert summary["dual_fractal_coupling_invoked"] is False
    assert summary["external_drs_not_implemented"] is True


def test_audit_hash_matches_proof_artifact(report):
    assert report.audit_entry["canonical_payload_hash"] == canonical_hash(
        report.proof_artifact
    )
    assert report.audit_entry["proof_only"] is True
    assert report.audit_entry["audit_chain_decides_truth"] is False


def test_summary_pass_and_ready_for_tests(report):
    summary = report.summary
    assert summary["controlled_fractal_dac_expansion_v01_status"] == "PASS"
    assert summary["child_cell_candidates_observed"] == 5
    assert summary["all_child_cells_bounded"] is True
    assert summary["root_remains_final_authority"] is True
    assert summary["ready_for_controlled_fractal_dac_expansion_v01_tests"] is True
