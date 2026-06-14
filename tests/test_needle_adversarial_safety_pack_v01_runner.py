from __future__ import annotations

import pytest

from demo.run_audit_hash_chain import canonical_hash
from demo.run_needle_adversarial_safety_pack_v01 import (
    collect_needle_adversarial_safety_pack_v01,
    render_needle_adversarial_safety_pack_v01,
)


@pytest.fixture(scope="module")
def report():
    return collect_needle_adversarial_safety_pack_v01()


def _by_id(rows, key):
    return {row[key]: row for row in rows}


def test_runner_title_and_required_sections_exist(report):
    output = render_needle_adversarial_safety_pack_v01(report)
    for heading in (
        "[NEEDLE ADVERSARIAL SAFETY PACK v0.1]",
        "[SOURCE EVIDENCE]",
        "[ADVERSARIAL ATTEMPTS]",
        "[SAFETY BOUNDARY MATRIX]",
        "[CONFLICTCHECK]",
        "[GT ADVISORY]",
        "[ROOT FINAL]",
        "[AUDIT]",
        "[SUMMARY]",
    ):
        assert heading in output


def test_all_source_statuses_pass(report):
    assert set(report.source_evidence.values()) == {"PASS"}


def test_exactly_eight_adversarial_attempts_exist(report):
    assert len(report.adversarial_attempts) == 8


def test_all_attempts_are_detected(report):
    assert all(row["detected"] is True for row in report.adversarial_attempts)


def test_all_attempts_are_blocked(report):
    assert all(row["blocked"] is True for row in report.adversarial_attempts)


def test_provenance_laundering_is_quarantined_and_blocked(report):
    attempts = _by_id(report.adversarial_attempts, "attempt_id")
    laundering = attempts["adversary_bridge_provenance_laundering"]
    assert laundering["quarantined"] is True
    assert laundering["blocked"] is True
    assert laundering["final_effect"] == "quarantined_blocked"


def test_no_attempt_executes_external_action(report):
    assert all(
        row["external_action_executed"] is False for row in report.adversarial_attempts
    )


def test_no_attempt_creates_installed_needle(report):
    assert all(
        row["installed_needle_created"] is False
        for row in report.adversarial_attempts
    )


def test_no_attempt_transfers_authority(report):
    assert all(
        row["authority_transferred"] is False for row in report.adversarial_attempts
    )


def test_no_attempt_proves_truth(report):
    assert all(row["truth_proven"] is False for row in report.adversarial_attempts)


def test_no_production_global_or_external_drs_writes(report):
    assert all(
        row["production_persistence"] is False
        and row["global_drs_write"] is False
        and row["external_drs_write"] is False
        for row in report.adversarial_attempts
    )


def test_no_gemini_or_network_calls(report):
    assert all(
        row["gemini_called"] is False and row["network_called"] is False
        for row in report.adversarial_attempts
    )


def test_dag_node_is_not_root(report):
    assert report.safety_boundary_matrix["dag_node_is_not_root"] is True


def test_rag_like_result_is_not_truth(report):
    assert report.safety_boundary_matrix["rag_result_is_not_truth"] is True


def test_drs_bridge_is_not_authority(report):
    assert report.safety_boundary_matrix["drs_bridge_is_not_authority"] is True


def test_traversal_trace_is_not_truth(report):
    assert report.safety_boundary_matrix["traversal_trace_is_not_truth"] is True


def test_bridge_traversal_is_not_provenance_laundering(report):
    assert (
        report.safety_boundary_matrix["bridge_traversal_is_not_provenance_laundering"]
        is True
    )


def test_coupling_edge_is_not_command_channel(report):
    assert (
        report.safety_boundary_matrix["coupling_edge_is_not_command_channel"] is True
    )


def test_child_cell_proposal_is_not_parent_final(report):
    assert (
        report.safety_boundary_matrix["child_cell_proposal_is_not_parent_final"]
        is True
    )


def test_needlecandidate_is_not_installed_needle(report):
    assert (
        report.safety_boundary_matrix["needle_candidate_is_not_installed_needle"]
        is True
    )


def test_gt_is_not_authority(report):
    assert report.safety_boundary_matrix["gt_is_not_authority"] is True


def test_audit_hash_chain_is_not_truth(report):
    assert report.safety_boundary_matrix["audit_hash_chain_is_not_truth"] is True


def test_root_review_required_for_capability(report):
    assert (
        report.safety_boundary_matrix["root_review_required_for_capability"] is True
    )


def test_root_final_required_for_action(report):
    assert report.safety_boundary_matrix["root_final_required_for_action"] is True


def test_explicit_installation_boundary_required_for_needle(report):
    assert (
        report.safety_boundary_matrix[
            "explicit_installation_boundary_required_for_needle"
        ]
        is True
    )


def test_no_external_action_without_permission_and_root(report):
    assert (
        report.safety_boundary_matrix[
            "no_external_action_without_permission_and_root"
        ]
        is True
    )


def test_conflictcheck_detects_all_attempts_but_is_not_authority(report):
    conflict = report.conflictcheck_result
    assert conflict["conflict_detected"] is True
    assert conflict["conflict_count"] == 8
    assert conflict["conflictcheck_is_authority"] is False


def test_gt_cannot_install_grant_execute_or_mark_truth(report):
    gt = report.gt_advisory
    assert gt["gt_is_advisory"] is True
    assert gt["gt_can_install_needle"] is False
    assert gt["gt_can_grant_authority"] is False
    assert gt["gt_can_execute_action"] is False
    assert gt["gt_can_mark_truth"] is False


def test_root_final_blocks_or_quarantines_all_attempts(report):
    root = report.root_final
    assert root["root_result"] == "blocked_or_quarantined"
    assert root["all_adversarial_attempts_blocked"] is True
    assert root["root_remains_final_authority"] is True
    assert root["no_installed_needle_created"] is True
    assert root["no_external_action_executed"] is True


def test_summary_pass_and_ready_for_tests(report):
    assert report.audit_entry["canonical_payload_hash"] == canonical_hash(
        report.proof_artifact
    )
    summary = report.summary
    assert summary["needle_adversarial_safety_pack_v01_status"] == "PASS"
    assert summary["adversarial_attempts_observed"] == 8
    assert summary["adversarial_attempts_blocked"] == 8
    assert summary["quarantined_attempts_observed"] == 1
    assert summary["ready_for_needle_adversarial_safety_pack_v01_tests"] is True
