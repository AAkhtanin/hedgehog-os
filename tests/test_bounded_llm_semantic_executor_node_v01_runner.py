from __future__ import annotations

import pytest

from demo.run_audit_hash_chain import canonical_hash
from demo.run_bounded_llm_semantic_executor_node_v01 import (
    collect_bounded_llm_semantic_executor_node_v01,
    render_bounded_llm_semantic_executor_node_v01,
)


@pytest.fixture(scope="module")
def report():
    return collect_bounded_llm_semantic_executor_node_v01()


def test_renderer_sections_exist(report):
    output = render_bounded_llm_semantic_executor_node_v01(report)
    for heading in (
        "[SOURCE EVIDENCE]",
        "[PLAN GRAPH]",
        "[EXECUTOR SEMANTIC NODE INPUT]",
        "[BOUNDED LLM CALL ENVELOPE]",
        "[SEMANTIC DRAFT]",
        "[SEMANTIC DRAFT RESULT PROPOSAL]",
        "[POST V&V]",
        "[GT ADVISORY]",
        "[ROOT FINAL]",
        "[BOUNDARY MATRIX]",
        "[ADVERSARIAL ATTEMPTS]",
        "[AUDIT]",
        "[SUMMARY]",
    ):
        assert heading in output


def test_source_metadata_does_not_replay_collectors(report):
    assert report.source_evidence["external_evidence_acceptance_gate_source_status"] == "PASS"
    assert report.source_evidence["source_evidence_mode"] == "closed_checkpoint_metadata_only"
    assert report.source_evidence["source_collectors_replayed"] is False


def test_plan_graph_has_four_architect_created_nodes(report):
    graph = report.plan_graph
    assert graph["created_by"] == "Architect"
    assert graph["created_before_llm_execution"] is True
    assert len(graph["nodes"]) == 4


def test_exactly_one_llm_semantic_executor_node(report):
    llm_nodes = [
        node
        for node in report.plan_graph["nodes"]
        if node["node_type"] == "llm_semantic_executor_node"
    ]
    assert len(llm_nodes) == 1
    assert llm_nodes[0]["implementation"] == "bounded_mock_llm"


def test_llm_is_executor_node_capability_and_cannot_modify_plan(report):
    envelope = report.bounded_llm_call_envelope
    assert envelope["llm_role"] == "executor_node_capability"
    assert envelope["plan_modification_allowed"] is False
    assert report.plan_graph["llm_created_plan_graph"] is False
    assert report.plan_graph["llm_modified_plan_graph"] is False


def test_bounded_envelope_denies_tools_connectors_actions_and_network(report):
    envelope = report.bounded_llm_call_envelope
    for field in (
        "network_called",
        "gemini_called",
        "tools_allowed",
        "connector_access_allowed",
        "drs_write_allowed",
        "external_action_allowed",
        "root_final_allowed",
        "input_contains_raw_secret",
    ):
        assert envelope[field] is False


def test_semantic_draft_is_bounded_nonfinal_output(report):
    draft = report.semantic_draft
    assert draft["semantic_draft_created"] is True
    assert draft["confidence_label"] == "mock_confidence_only"
    for field in (
        "truth_proven",
        "ready_status_created",
        "external_action_executed",
        "global_drs_write",
        "external_drs_write",
        "installed_needle_created",
        "root_final_created",
        "plan_modified",
    ):
        assert draft[field] is False


def test_result_proposal_requires_post_vv_gt_and_root(report):
    proposal = report.semantic_draft_result_proposal
    assert proposal["proposal_type"] == "semantic_draft_result_proposal"
    assert proposal["safe_for_post_vv"] is True
    assert proposal["requires_post_vv"] is True
    assert proposal["requires_gt"] is True
    assert proposal["requires_root_final"] is True


def test_post_vv_passes_only_without_overclaim(report):
    assert all(value is True for value in report.post_vv_semantic_check.values())


def test_gt_is_advisory_only(report):
    gt = report.gt_semantic_advisory
    assert gt["gt_is_advisory"] is True
    assert gt["gt_recommendation"] == "accept_semantic_draft_as_explanation_candidate"
    assert all(value is False for key, value in gt.items() if key.startswith("gt_can_"))


def test_root_accepts_explanation_candidate_only(report):
    root = report.root_semantic_final
    assert root["root_result"] == "bounded_llm_semantic_executor_node_completed"
    assert root["safe_secondary_outcome"] == "semantic_explanation_candidate_available"
    assert root["semantic_explanation_candidate_created"] is True
    assert root["llm_is_executor_node_capability"] is True
    assert root["root_remains_final_authority"] is True


def test_all_boundary_matrix_values_hold(report):
    assert all(value is True for value in report.boundary_matrix.values())


def test_all_nine_adversarial_attempts_are_blocked(report):
    assert len(report.adversarial_attempts) == 9
    assert all(
        row["detected"] is True
        and row["blocked"] is True
        and row["final_effect"] == "blocked"
        for row in report.adversarial_attempts
    )


def test_adversarial_attempts_create_no_illegal_effect(report):
    for row in report.adversarial_attempts:
        for field in (
            "truth_proven",
            "ready_status_created",
            "external_action_executed",
            "global_drs_write",
            "external_drs_write",
            "installed_needle_created",
            "plan_modified",
            "root_final_created_by_llm",
            "network_called",
            "gemini_called",
            "authority_transferred",
        ):
            assert row[field] is False


def test_no_external_or_deferred_system_is_used(report):
    root = report.root_semantic_final
    for field in (
        "network_called",
        "gemini_called",
        "telegram_used",
        "marennya_invoked",
        "up_invoked",
        "production_persistence",
    ):
        assert root[field] is False


def test_audit_hash_matches_proof_artifact(report):
    assert report.audit_entry["canonical_payload_hash"] == canonical_hash(report.proof_artifact)
    assert report.audit_entry["audit_chain_decides_truth"] is False


def test_summary_counts_and_pass(report):
    summary = report.summary
    assert summary["bounded_llm_semantic_executor_node_v01_status"] == "PASS"
    assert summary["plan_nodes_created"] == 4
    assert summary["llm_semantic_executor_nodes_created"] == 1
    assert summary["bounded_llm_call_envelopes_created"] == 1
    assert summary["semantic_drafts_created"] == 1
    assert summary["semantic_draft_result_proposals_created"] == 1
    assert summary["post_vv_passed"] == 1
    assert summary["adversarial_attempts_observed"] == 9
    assert summary["adversarial_attempts_blocked"] == 9
    assert summary["ready_for_bounded_llm_semantic_executor_node_v01_tests"] is True
