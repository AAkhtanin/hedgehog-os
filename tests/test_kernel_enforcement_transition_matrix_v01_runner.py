from __future__ import annotations

import pytest

from demo.run_audit_hash_chain import canonical_hash
from demo.run_kernel_enforcement_transition_matrix_v01 import (
    collect_kernel_enforcement_transition_matrix_v01,
    render_kernel_enforcement_transition_matrix_v01,
)


@pytest.fixture(scope="module")
def report():
    return collect_kernel_enforcement_transition_matrix_v01()


def test_renderer_has_required_sections(report):
    output = render_kernel_enforcement_transition_matrix_v01(report)
    for section in (
        "[HEADER]",
        "[SOURCE CHECKPOINTS]",
        "[TRANSITION MATRIX PURPOSE]",
        "[ARTIFACT TYPES]",
        "[TRANSITION TARGET TYPES]",
        "[LOCAL TRANSITION TAXONOMY]",
        "[ALLOWED TRANSITIONS]",
        "[BLOCKED TRANSITIONS]",
        "[ROOT COMMIT BOUNDARY]",
        "[AUTHORITY BOUNDARY MATRIX]",
        "[LLM EXECUTOR NODE BOUNDARY]",
        "[DRS / METADATA / AUDIT BOUNDARY]",
        "[COMPUTE COLLAPSE / KILLER DEMO BOUNDARY]",
        "[ROOT FINAL]",
        "[AUDIT]",
        "[SUMMARY]",
    ):
        assert section in output


def test_summary_status_and_counts(report):
    summary = report.summary
    assert summary["kernel_enforcement_transition_matrix_v01_status"] == "PASS"
    assert summary["allowed_transitions_count"] == 10
    assert summary["blocked_transitions_count"] == 35
    assert summary["blocked_transitions_blocked"] == 35
    assert summary["ready_for_kernel_enforcement_transition_matrix_v01_tests"] is True


def test_allowed_transitions_count_and_shape(report):
    assert len(report.allowed_transitions) == 10
    assert all("artifact_type" in row for row in report.allowed_transitions)
    assert all("expected_decision" in row for row in report.allowed_transitions)
    assert any(
        row["transition_id"] == "root_to_root_final_output"
        and row["final_output_created"] is True
        for row in report.allowed_transitions
    )


def test_allowed_transition_terms_are_covered_by_local_taxonomy(report):
    taxonomy = set(report.local_transition_taxonomy)
    assert all(row["artifact_type"] in taxonomy for row in report.allowed_transitions)
    assert all(
        row["attempted_target_or_effect"] in taxonomy
        for row in report.allowed_transitions
    )


def test_blocked_transition_terms_are_covered_by_local_taxonomy(report):
    taxonomy = set(report.local_transition_taxonomy)
    assert all(row["artifact_type"] in taxonomy for row in report.blocked_transitions)
    assert all(
        row["attempted_target_or_effect"] in taxonomy
        for row in report.blocked_transitions
    )


def test_local_drs_writeback_transition_is_explicitly_local(report):
    transition = next(
        row
        for row in report.allowed_transitions
        if row["transition_id"] == "root_final_output_to_drs_writeback"
    )
    assert transition["drs_writeback_scope"] == "local_after_root_final"
    assert transition["local_drs_writeback"] is True
    assert transition["global_drs_write"] is False
    assert transition["external_drs_write"] is False


def test_all_blocked_transitions_are_detected_and_blocked(report):
    assert len(report.blocked_transitions) == 35
    assert all(row["detected"] is True for row in report.blocked_transitions)
    assert all(row["blocked"] is True for row in report.blocked_transitions)
    assert all(row["final_effect"] == "blocked" for row in report.blocked_transitions)


def test_blocked_transitions_create_no_illegal_effects(report):
    for row in report.blocked_transitions:
        for field in (
            "authority_transferred",
            "final_output_created",
            "truth_claim_created",
            "ready_status_created",
            "external_action_executed",
            "global_drs_write",
            "external_drs_write",
            "installed_needle_created",
            "production_persistence",
            "network_called",
            "gemini_called",
            "marennya_invoked",
            "up_invoked",
        ):
            assert row[field] is False


def test_root_commit_boundary_is_preserved(report):
    summary = report.summary
    assert summary["root_only_final_output"] is True
    assert summary["root_commit_required_for_final_output"] is True
    assert report.root_commit_boundary["non_root_final_output_transitions_blocked"] is True


def test_transition_matrix_is_not_authority(report):
    purpose = report.transition_matrix_purpose
    assert purpose["transition_matrix_is_proof_only"] is True
    assert purpose["transition_matrix_is_authority"] is False
    assert purpose["transition_matrix_is_production_runtime_authority"] is False
    assert report.summary["transition_matrix_is_proof_only"] is True
    assert report.summary["transition_matrix_is_authority"] is False
    assert report.summary["transition_matrix_is_production_runtime_authority"] is False


def test_authority_boundary_matrix_values(report):
    summary = report.summary
    assert summary["drs_reuse_is_authority"] is False
    assert summary["closed_checkpoint_metadata_is_authority"] is False
    assert summary["audit_hash_decides_truth"] is False
    assert summary["connector_observation_is_truth"] is False
    assert summary["evidence_candidate_is_accepted_evidence"] is False
    assert summary["accepted_evidence_is_truth"] is False
    assert summary["accepted_evidence_is_action"] is False
    assert summary["semantic_draft_is_final"] is False
    assert summary["resultproposal_is_final"] is False
    assert summary["gt_is_final_authority"] is False


def test_llm_executor_node_is_bounded_not_authority(report):
    summary = report.summary
    assert summary["llm_is_bounded_executor_node_capability"] is True
    assert summary["llm_is_authority"] is False
    assert report.llm_executor_node_boundary["llm_can_write_drs"] is False
    assert report.llm_executor_node_boundary["llm_can_execute_external_action"] is False


def test_compute_collapse_does_not_authorize_killer_demo(report):
    summary = report.summary
    assert summary["compute_collapse_authorizes_killer_demo"] is False
    assert report.compute_collapse_killer_demo_boundary[
        "production_enforcement_implemented"
    ] is False
    assert report.compute_collapse_killer_demo_boundary["runtime_rewrite_performed"] is False


def test_no_external_or_deferred_system_is_used(report):
    summary = report.summary
    for field in (
        "no_network",
        "no_gemini",
        "no_external_action",
        "no_global_drs_write",
        "no_external_drs_write",
        "no_installed_needle",
        "no_production_persistence",
        "no_marennya",
        "no_up",
    ):
        assert summary[field] is True


def test_audit_hash_matches_proof_artifact(report):
    assert report.audit_entry["canonical_payload_hash"] == canonical_hash(
        report.proof_artifact
    )
    assert report.audit_entry["audit_chain_decides_truth"] is False
