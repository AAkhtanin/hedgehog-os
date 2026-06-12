from __future__ import annotations

import pytest

from demo.run_audit_hash_chain import canonical_hash
from demo.run_dual_fractal_coupling_v01 import (
    collect_dual_fractal_coupling_v01,
    render_dual_fractal_coupling_v01,
)


@pytest.fixture(scope="module")
def report():
    return collect_dual_fractal_coupling_v01()


def _by_id(rows, key):
    return {row[key]: row for row in rows}


def test_runner_title_and_required_sections_exist(report):
    output = render_dual_fractal_coupling_v01(report)
    for heading in (
        "[DUAL FRACTAL COUPLING v0.1]",
        "[SOURCE EVIDENCE]",
        "[PARENT DAC MATRIX]",
        "[LOCAL CELL MATRIX]",
        "[COUPLING EDGES]",
        "[COUPLING BOUNDARY MATRIX]",
        "[INTERLOCK OBSERVATION]",
        "[CONFLICTCHECK]",
        "[GT ADVISORY]",
        "[ROOT FINAL MATRIX]",
        "[AUDIT]",
        "[SUMMARY]",
    ):
        assert heading in output


def test_all_source_statuses_pass(report):
    assert set(report.source_evidence.values()) == {"PASS"}


def test_exactly_two_parent_dacs_observed(report):
    assert len(report.parent_dac_matrix) == 2


def test_parent_root_results_remain_not_ready(report):
    assert all(row["root_result"] == "not_ready" for row in report.parent_dac_matrix)


def test_total_local_cells_is_eight(report):
    assert len(report.local_cell_matrix) == 8


def test_expected_certificate_cells_exist(report):
    cells = _by_id(report.local_cell_matrix, "cell_id")
    assert {
        "certificate_insurance_check",
        "certificate_payment_receipt_check",
        "certificate_submission_permission_check",
    } <= set(cells)


def test_expected_travel_cells_exist(report):
    cells = _by_id(report.local_cell_matrix, "cell_id")
    assert {
        "travel_document_check",
        "travel_payment_check",
        "travel_lodging_check",
        "travel_route_window_check",
        "travel_permission_check",
    } <= set(cells)


def test_certificate_cells_are_blocked(report):
    assert all(
        row["local_status"] == "blocked"
        for row in report.local_cell_matrix
        if row["parent_dac_id"] == "certificate_parent_dac"
    )


def test_travel_has_four_blocked_and_one_ready_cell(report):
    travel = [
        row
        for row in report.local_cell_matrix
        if row["parent_dac_id"] == "travel_parent_dac"
    ]
    assert sum(row["local_status"] == "blocked" for row in travel) == 4
    assert sum(row["local_status"] == "ready" for row in travel) == 1


def test_all_local_cells_are_local_only(report):
    assert all(row["local_only"] is True for row in report.local_cell_matrix)


def test_all_local_cells_have_no_root_authority(report):
    assert all(row["root_authority"] is False for row in report.local_cell_matrix)


def test_all_local_cells_have_no_parent_final_authority(report):
    assert all(
        row["parent_final_authority"] is False for row in report.local_cell_matrix
    )


def test_all_local_cells_have_no_cross_parent_authority(report):
    assert all(
        row["cross_parent_authority"] is False for row in report.local_cell_matrix
    )


def test_all_local_cells_have_no_external_action_authority(report):
    assert all(
        row["external_action_authority"] is False for row in report.local_cell_matrix
    )


def test_all_local_cells_have_no_drs_write_authority(report):
    assert all(row["drs_write_authority"] is False for row in report.local_cell_matrix)


def test_no_cell_can_mark_either_parent_ready(report):
    assert all(
        row["can_mark_own_parent_ready"] is False
        and row["can_mark_other_parent_ready"] is False
        for row in report.local_cell_matrix
    )


def test_no_cell_can_override_spawn_install_or_create_candidates(report):
    fields = (
        "can_override_coupled_cell",
        "can_spawn_child",
        "can_install_needle",
        "can_create_protocol_candidate",
        "can_create_needle_candidate",
    )
    assert all(
        all(row[field] is False for field in fields)
        for row in report.local_cell_matrix
    )


def test_exactly_two_coupling_edges_exist(report):
    assert len(report.coupling_edges) == 2


def test_coupling_edges_are_insurance_and_payment(report):
    assert {edge["shared_semantic_field"] for edge in report.coupling_edges} == {
        "insurance_certificate",
        "payment_receipt",
    }


def test_coupling_edges_transfer_no_authority_final_or_execution(report):
    assert all(
        edge["transfers_authority"] is False
        and edge["transfers_final"] is False
        and edge["transfers_execution"] is False
        for edge in report.coupling_edges
    )


def test_shared_evidence_can_inform_but_cannot_decide(report):
    assert all(
        row["shared_evidence_can_inform"] is True
        and row["shared_evidence_can_decide"] is False
        for row in report.coupling_boundary_matrix
    )


def test_coupling_boundaries_block_transfer_and_cross_finalization(report):
    fields = (
        "coupling_transfers_authority",
        "coupling_transfers_root",
        "coupling_transfers_execution",
        "coupling_transfers_drs_write",
        "coupled_cell_can_override_target",
        "source_parent_can_finalize_target_parent",
        "target_parent_can_finalize_source_parent",
    )
    assert all(
        all(row[field] is False for field in fields)
        and row["root_review_required"] is True
        for row in report.coupling_boundary_matrix
    )


def test_interlock_observed_with_two_parents_and_edges(report):
    interlock = report.interlock_observation
    assert interlock["interlock_observed"] is True
    assert interlock["coupled_parents"] == 2
    assert interlock["coupling_edges_observed"] == 2


def test_shared_evidence_reuse_and_drs_are_not_authority(report):
    interlock = report.interlock_observation
    assert interlock["shared_evidence_is_not_authority"] is True
    assert interlock["semantic_similarity_is_not_authority"] is True
    assert interlock["reuse_score_is_not_root"] is True
    assert interlock["drs_retrieval_is_not_authority"] is True


def test_conflictcheck_detects_authority_leak_attempt_but_is_advisory(report):
    conflict = report.conflictcheck_result
    assert conflict["conflict_detected"] is True
    assert conflict["reason"] == (
        "coupling_edge_cannot_transfer_authority_or_parent_finalization"
    )
    assert conflict["conflictcheck_is_authority"] is False


def test_gt_cannot_merge_or_mark_parent_ready(report):
    gt = report.gt_advisory
    assert gt["gt_recommendation"] == "dual_parent_not_ready"
    assert gt["gt_can_merge_parent_authority"] is False
    assert gt["gt_can_mark_certificate_ready"] is False
    assert gt["gt_can_mark_travel_ready"] is False


def test_root_final_matrix_has_two_root_authoritative_finals(report):
    assert len(report.root_final_matrix) == 2
    assert all(
        row["root_result"] == "not_ready"
        and row["root_remains_final_authority"] is True
        for row in report.root_final_matrix
    )


def test_no_coupled_parent_finalizes_the_other(report):
    assert all(
        row["coupled_parent_finalized_this_parent"] is False
        and row["child_cells_finalized_result"] is False
        and row["coupling_edges_transferred_authority"] is False
        for row in report.root_final_matrix
    )


def test_no_external_action_or_submission_booking_payment(report):
    finals = _by_id(report.root_final_matrix, "parent_dac_id")
    assert all(
        row["completed_external_action_created"] is False
        for row in report.root_final_matrix
    )
    assert finals["certificate_parent_dac"]["certificate_request_submitted"] is False
    assert finals["travel_parent_dac"]["travel_request_submitted"] is False
    assert finals["travel_parent_dac"]["booking_created"] is False
    assert finals["travel_parent_dac"]["payment_executed"] is False


def test_no_protocol_candidate_needle_candidate_or_installed_needle(report):
    assert all(
        row["protocol_candidate_created"] is False
        and row["needle_candidate_created"] is False
        and row["installed_needle_created"] is False
        for row in report.root_final_matrix
    )


def test_no_production_global_or_external_drs(report):
    assert all(
        row["production_persistence"] is False
        and row["global_drs_write"] is False
        and row["external_drs_write"] is False
        for row in report.root_final_matrix
    )


def test_no_external_system_or_deferred_layer_invoked(report):
    for field in (
        "gemini_called",
        "network_called",
        "telegram_used",
        "marennya_invoked",
        "up_invoked",
    ):
        assert report.summary[field] is False


def test_non_overclaim_flags_prove_controlled_interlock_only(report):
    summary = report.summary
    assert summary["dual_fractal_coupling_observed"] is True
    assert summary["controlled_interlock_only"] is True
    assert summary["real_child_agents_started"] is False
    assert summary["production_autonomy_claimed"] is False
    assert summary["external_drs_not_implemented"] is True


def test_audit_hash_matches_proof_artifact(report):
    assert report.audit_entry["canonical_payload_hash"] == canonical_hash(
        report.proof_artifact
    )
    assert report.audit_entry["proof_only"] is True
    assert report.audit_entry["audit_chain_decides_truth"] is False


def test_summary_pass_and_ready_for_tests(report):
    summary = report.summary
    assert summary["dual_fractal_coupling_v01_status"] == "PASS"
    assert summary["coupled_parent_dacs"] == 2
    assert summary["total_local_cells"] == 8
    assert summary["all_local_cells_bounded"] is True
    assert summary["root_remains_final_authority"] is True
    assert summary["ready_for_dual_fractal_coupling_v01_tests"] is True
