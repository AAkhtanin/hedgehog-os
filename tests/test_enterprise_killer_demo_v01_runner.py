from __future__ import annotations

import pytest

from demo.run_audit_hash_chain import canonical_hash
from demo.run_enterprise_killer_demo_v01 import (
    ADVERSARIAL_ATTEMPT_IDS,
    collect_enterprise_killer_demo_v01,
    render_enterprise_killer_demo_v01,
)


@pytest.fixture(scope="module")
def report():
    return collect_enterprise_killer_demo_v01()


@pytest.fixture(scope="module")
def rendered(report):
    return render_enterprise_killer_demo_v01(report)


def test_rendered_output_contains_required_sections(rendered):
    for section in (
        "[HEADER]",
        "[SOURCE CHECKPOINTS]",
        "[ACT 1 — DIRTY ENTERPRISE REQUEST]",
        "[ACT 2 — AUTHORITY STRESS]",
        "[ACT 3 — COMPUTE COLLAPSE]",
        "[KILLER HUMAN MOMENT]",
        "[ENTERPRISE SCENARIO]",
        "[OBSERVATIONS ARE NOT TRUTH]",
        "[EVIDENCE ACCEPTANCE GATE]",
        "[LLM EXECUTOR NODE DRAFT]",
        "[DRS REUSE SIGNAL]",
        "[DEVELOPER FACADE MANIFEST CANDIDATE]",
        "[TRANSITION MATRIX BLOCKS]",
        "[ENTERPRISE CHAOS / CONFLICTS]",
        "[COMPUTE COLLAPSE ESTIMATE]",
        "[PRODUCTION BOUNDARY]",
        "[ROOT FINAL]",
        "[WHAT HUMAN SEES]",
        "[WHAT THIS PROVES]",
        "[WHAT THIS DOES NOT PROVE]",
        "[SUMMARY]",
    ):
        assert section in rendered


def test_rendered_output_contains_positive_grep_terms(rendered):
    for line in (
        "Enterprise Killer Demo v0.1",
        "enterprise_killer_demo_v01_status: PASS",
        "deterministic_local_assembly_proof_only",
        "assembly of proven layers",
        "source_checkpoint_count: 10",
        "connector_observation_is_truth: false",
        "evidence_candidate_requires_acceptance_gate: true",
        "llm_is_authority: false",
        "drs_reuse_is_authority: false",
        "capability_manifest_is_installed_capability: false",
        "transition_matrix_is_authority: false",
        "transition_matrix_is_production_runtime_authority: false",
        "production_ready_claimed: false",
        "real_external_action_authorized: false",
        "real_external_action_executed: false",
        "root_final_status: not_ready",
        "safe_secondary_outcome: needs_human_review",
        "adversarial_attempts_observed: 18",
        "adversarial_attempts_blocked: 18",
        "naive_synthetic_llm_call_units: 29",
        "naive_context_units: 180",
        "hedgehog_bounded_llm_semantic_nodes: 1",
        "hedgehog_context_units: 32",
        "hedgehog_blocked_authority_attempts: 18",
        "act_count: 3",
        "human_walkthrough_ready: true",
        "real_cost_savings_claimed: false",
        "no_network: true",
        "no_gemini: true",
    ):
        assert line in rendered


def test_act_sections_render_human_story(rendered):
    assert "A company asks whether a vendor shipment can be approved" in rendered
    assert "vendor record says ready" in rendered
    assert "connector observation says certificate exists" in rendered
    assert "DRS reuse says a similar previous case was approved" in rendered
    assert 'LLM draft says "looks ready"' in rendered
    assert "manifest candidate offers read-only vendor observation" in rendered
    assert "compliance certificate is stale/expired" in rendered
    assert "invoice total conflicts with purchase order" in rendered
    assert "payment approval is missing" in rendered


def test_killer_human_moment_is_rendered(rendered):
    assert "The system did not become an autonomous agent." in rendered
    assert "It became a controlled semantic runtime." in rendered
    assert "Система не стала автономным агентом." in rendered
    assert "Она стала управляемой смысловой операционной средой." in rendered


def test_status_and_proof_type(report):
    assert report.summary["enterprise_killer_demo_v01_status"] == "PASS"
    assert report.summary["proof_type"] == "deterministic_local_assembly_proof_only"
    assert report.header["new_authority_layer_created"] is False


def test_closed_source_checkpoint_metadata(report):
    assert report.source_evidence["source_evidence_mode"] == "closed_checkpoint_metadata_only"
    assert report.source_evidence["source_collectors_replayed"] is False
    assert report.source_evidence["source_checkpoint_count"] == 10
    assert report.source_evidence["source_checkpoints_all_closed"] is True
    assert len(report.source_checkpoints) == 10
    assert all(row["checkpoint_status"] == "closed" for row in report.source_checkpoints)


def test_scenario_facts_and_conflicts(report):
    scenario = report.enterprise_scenario
    conflicts = report.enterprise_chaos_conflicts
    assert scenario["enterprise_id"] == "ENT-ACME-42"
    assert scenario["request_id"] == "REQ-KILLER-001"
    assert scenario["domain"] == "enterprise_procurement_readiness"
    assert conflicts["conflict_detected"] is True
    assert set(
        (
            "compliance_certificate_stale",
            "invoice_total_conflicts_with_purchase_order",
            "payment_approval_missing",
        )
    ).issubset(set(conflicts["conflict_reasons"]))


def test_connector_observation_is_not_truth_evidence_or_action(report):
    observation = report.observations_are_not_truth
    assert observation["connector_observation_created"] is True
    assert observation["connector_observation_is_truth"] is False
    assert observation["connector_observation_is_accepted_evidence"] is False
    assert observation["connector_observation_triggers_action"] is False


def test_evidence_candidate_requires_gate(report):
    evidence = report.evidence_acceptance_gate
    assert evidence["evidence_candidate_created"] is True
    assert evidence["evidence_candidate_requires_acceptance_gate"] is True
    assert evidence["accepted_evidence_created"] is False
    assert evidence["accepted_evidence_status"] == (
        "rejected_or_not_accepted_due_to_stale_conflict"
    )
    assert evidence["accepted_evidence_is_truth"] is False
    assert evidence["accepted_evidence_triggers_action"] is False


def test_llm_draft_is_bounded_not_authority_final_action_or_drs_writer(report):
    llm = report.llm_executor_node_draft
    assert llm["bounded_llm_draft_created"] is True
    assert llm["llm_draft_claim"] == "looks ready"
    assert llm["llm_is_authority"] is False
    assert llm["llm_can_finalize"] is False
    assert llm["llm_can_execute_external_action"] is False
    assert llm["llm_can_write_drs_by_itself"] is False
    assert llm["llm_draft_overruled_by_boundaries"] is True


def test_drs_reuse_is_context_only_not_authority(report):
    drs = report.drs_reuse_signal
    assert drs["drs_reuse_candidate_found"] is True
    assert drs["drs_reuse_is_authority"] is False
    assert drs["drs_reuse_applied_as_context_only"] is True
    assert drs["drs_direct_approval_created"] is False
    assert drs["global_drs_write"] is False
    assert drs["external_drs_write"] is False


def test_developer_facade_candidate_is_candidate_only(report):
    manifest = report.developer_facade_manifest_candidate
    assert manifest["capability_manifest_candidate_created"] is True
    assert (
        manifest["capability_manifest_decision"]
        == "facade_validated_manifest_candidate_only"
    )
    assert manifest["capability_manifest_is_installed_capability"] is False
    assert manifest["installed_capabilities_created"] == 0
    assert manifest["installed_needles_created"] == 0
    assert manifest["developer_manifest_is_authority"] is False


def test_transition_matrix_blocks_invalid_external_action(report):
    matrix = report.transition_matrix_blocks
    assert matrix["transition_matrix_required"] is True
    assert matrix["transition_matrix_is_authority"] is False
    assert matrix["transition_matrix_is_production_runtime_authority"] is False
    assert matrix["invalid_transition_attempted"] is True
    assert matrix["invalid_transition_name"] == "accepted_evidence_to_external_action"
    assert matrix["invalid_transition_blocked"] is True
    assert (
        matrix["transition_matrix_blocks_external_action_without_root_and_permission"]
        is True
    )
    assert matrix["transition_matrix_does_not_replace_root"] is True


def test_production_boundary_prevents_overclaim(report):
    boundary = report.production_boundary
    assert boundary["production_boundary_checked"] is True
    assert boundary["production_boundary_design_docs_referenced"] is True
    assert boundary["production_boundary_design_is_implementation"] is False
    assert boundary["production_ready_claimed"] is False
    assert boundary["production_runtime_implemented"] is False
    assert boundary["production_kernel_enforcement_implemented"] is False
    assert boundary["real_api_called"] is False
    assert boundary["real_external_action_authorized"] is False
    assert boundary["real_external_action_executed"] is False


def test_root_final_is_not_ready_and_needs_human_review(report):
    root = report.root_final
    assert root["root_remains_final_authority"] is True
    assert root["root_final_created"] is True
    assert root["root_final_status"] == "not_ready"
    assert set(
        (
            "stale_compliance_certificate",
            "invoice_po_conflict",
            "missing_payment_approval",
            "real_action_not_authorized",
        )
    ).issubset(set(root["root_final_reason"]))
    assert root["safe_secondary_outcome"] == "needs_human_review"


def test_no_external_action_approval_or_payment(report):
    root = report.root_final
    assert root["external_action_executed"] is False
    assert root["vendor_shipment_approved"] is False
    assert root["payment_triggered"] is False
    assert root["production_claim_created"] is False


def test_compute_collapse_uses_estimates_only(report):
    estimate = report.compute_collapse_estimate
    assert estimate["naive_baseline_steps_estimate"] == 44
    assert estimate["hedgehog_routed_steps_estimate"] == 10
    assert estimate["estimated_routed_units_saved"] == 34
    assert estimate["estimated_savings_ratio"] == 0.773
    assert estimate["naive_synthetic_llm_call_units"] == 29
    assert estimate["naive_context_units"] == 180
    assert estimate["naive_collector_replays"] == 4
    assert estimate["naive_validation_passes"] == 6
    assert estimate["naive_action_planning_steps"] == 6
    assert estimate["naive_unbounded_authority_risk_units"] == 18
    assert estimate["hedgehog_bounded_llm_semantic_nodes"] == 1
    assert estimate["hedgehog_context_units"] == 32
    assert estimate["hedgehog_collector_replays"] == 0
    assert estimate["hedgehog_validation_passes"] == 1
    assert estimate["hedgehog_action_planning_steps"] == 0
    assert estimate["hedgehog_unbounded_authority_risk_units"] == 0
    assert estimate["hedgehog_blocked_authority_attempts"] == 18
    assert estimate["proof_level_estimate_only"] is True
    assert estimate["real_cost_savings_claimed"] is False
    assert estimate["real_latency_measured"] is False
    assert estimate["real_billing_measured"] is False
    assert "not real billing" in estimate["human_wording"]


def test_adversarial_attempt_counts(report):
    assert len(report.adversarial_attempts) == 18
    assert report.summary["adversarial_attempts_observed"] == 18
    assert report.summary["adversarial_attempts_blocked"] == 18
    assert all(row["detected"] is True for row in report.adversarial_attempts)
    assert all(row["blocked"] is True for row in report.adversarial_attempts)
    assert all(
        row["final_effect"] in {"blocked", "quarantined_and_blocked"}
        for row in report.adversarial_attempts
    )


def test_all_18_attempt_ids_are_present(report):
    assert [row["attempt_id"] for row in report.adversarial_attempts] == list(
        ADVERSARIAL_ATTEMPT_IDS
    )


def test_quarantined_authority_stress_attempts(report):
    attempts = {row["attempt_id"]: row for row in report.adversarial_attempts}
    for attempt_id in (
        "external_pointer_to_global_drs_write",
        "bridge_traversal_to_provenance_laundering",
        "stale_timeenvelope_to_current",
    ):
        assert attempts[attempt_id]["final_effect"] == "quarantined_and_blocked"


def test_adversarial_attempts_create_no_illegal_effects(report):
    for row in report.adversarial_attempts:
        for field in (
            "authority_transferred",
            "root_bypassed",
            "final_output_created",
            "truth_claim_created",
            "accepted_evidence_created",
            "external_action_executed",
            "global_drs_write",
            "external_drs_write",
            "installed_capability_created",
            "installed_needle_created",
            "production_persistence",
            "network_called",
            "gemini_called",
            "marennya_invoked",
            "up_invoked",
        ):
            assert row[field] is False


def test_all_summary_guardrail_flags_are_safe(report):
    summary = report.summary
    for field in (
        "connector_observation_is_truth",
        "accepted_evidence_is_truth",
        "llm_is_authority",
        "drs_reuse_is_authority",
        "developer_manifest_is_authority",
        "capability_manifest_is_installed_capability",
        "transition_matrix_is_authority",
        "transition_matrix_is_production_runtime_authority",
        "production_boundary_design_is_implementation",
        "production_ready_claimed",
        "real_api_called",
        "real_external_action_authorized",
        "real_external_action_executed",
        "external_action_executed",
        "global_drs_write",
        "external_drs_write",
        "external_global_drs_implemented",
        "production_persistence_implemented",
        "secrets_vault_implemented",
        "live_monitoring_implemented",
        "root_bypassed",
        "vendor_shipment_approved",
        "payment_triggered",
        "real_cost_savings_claimed",
        "real_latency_measured",
        "real_billing_measured",
        "network_called",
        "gemini_called",
        "marennya_invoked",
        "up_invoked",
    ):
        assert summary[field] is False


def test_summary_positive_safety_flags(report):
    summary = report.summary
    assert summary["root_remains_final_authority"] is True
    assert summary["evidence_candidate_requires_acceptance_gate"] is True
    assert summary["hedgehog_blocked_authority_attempts"] == 18
    assert summary["act_count"] == 3
    assert summary["human_walkthrough_ready"] is True
    assert summary["no_network"] is True
    assert summary["no_gemini"] is True
    assert summary["no_real_api"] is True
    assert summary["no_real_external_action"] is True
    assert summary["no_production_persistence"] is True
    assert summary["no_installed_capability"] is True
    assert summary["no_installed_needle"] is True
    assert summary["no_marennya"] is True
    assert summary["no_up"] is True


def test_human_visible_output_is_safe(report):
    human_view = report.what_human_sees
    assert human_view["human_visible_status"] == "not_ready"
    assert human_view["human_visible_next_step"] == "needs_human_review"
    assert human_view["shipment_approval_visible"] is False
    assert human_view["payment_trigger_visible"] is False
    assert human_view["production_claim_visible"] is False


def test_act_report_fields_are_consistent(report):
    assert report.act1_dirty_enterprise_request["root_result"] == "not_ready"
    assert (
        report.act1_dirty_enterprise_request["safe_secondary_outcome"]
        == "needs_human_review"
    )
    assert report.act1_dirty_enterprise_request["no_shipment_approved"] is True
    assert report.act1_dirty_enterprise_request["no_payment_triggered"] is True
    assert report.act1_dirty_enterprise_request["no_external_action_executed"] is True
    assert report.act2_authority_stress["blocked_attempt_count"] == 18
    assert "GT did not become Root" in report.act2_authority_stress["human_summary"]
    assert report.act3_compute_collapse["naive_synthetic_llm_call_units"] == 29
    assert report.act3_compute_collapse["hedgehog_context_units"] == 32


def test_audit_hash_is_continuity_only_not_truth(report):
    assert report.audit_entry["canonical_payload_hash"] == canonical_hash(
        report.proof_artifact
    )
    assert report.audit_entry["audit_hash_chain_records_continuity_only"] is True
    assert report.audit_entry["audit_hash_decides_truth"] is False
