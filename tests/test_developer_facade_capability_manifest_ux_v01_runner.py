from __future__ import annotations

import pytest

from demo.run_audit_hash_chain import canonical_hash
from demo.run_developer_facade_capability_manifest_ux_v01 import (
    collect_developer_facade_capability_manifest_ux_v01,
    render_developer_facade_capability_manifest_ux_v01,
)


@pytest.fixture(scope="module")
def report():
    return collect_developer_facade_capability_manifest_ux_v01()


def test_renderer_has_required_sections(report):
    output = render_developer_facade_capability_manifest_ux_v01(report)
    for section in (
        "[HEADER]",
        "[SOURCE CHECKPOINTS]",
        "[DEVELOPER FACADE PURPOSE]",
        "[CAPABILITY MANIFEST CONTRACT]",
        "[MANIFEST CANDIDATES]",
        "[VALIDATED MANIFEST CANDIDATES]",
        "[REJECTED / NEEDS_USER MANIFESTS]",
        "[ADVERSARIAL MANIFEST ATTEMPTS]",
        "[KERNEL TRANSITION MATRIX BOUNDARY]",
        "[PERMISSION / RISK BOUNDARY]",
        "[EXTERNAL OBSERVATION SCHEMA BOUNDARY]",
        "[LLM / DRS / ACTION BOUNDARY]",
        "[ROOT FINAL]",
        "[AUDIT]",
        "[SUMMARY]",
    ):
        assert section in output
    assert "developer_facade_capability_manifest_ux_v01_status: PASS" in output


def test_closed_checkpoint_metadata_only(report):
    source = report.source_evidence
    assert source["source_evidence_mode"] == "closed_checkpoint_metadata_only"
    assert source["source_collectors_replayed"] is False
    assert source["source_collectors_replayed_count"] == 0
    assert source["kernel_enforcement_checkpoint_referenced"] is True
    assert len(report.source_checkpoints) == 8
    assert all(row["checkpoint_status"] == "PASS" for row in report.source_checkpoints)
    assert all(row["closure_status"] == "closed" for row in report.source_checkpoints)


def test_manifest_counts(report):
    summary = report.summary
    assert summary["manifest_candidates_created"] == 6
    assert summary["facade_validated_manifest_candidates"] == 3
    assert summary["rejected_manifest_candidates"] == 2
    assert summary["needs_user_manifest_candidates"] == 1
    assert len(report.manifest_candidates) == 6
    assert len(report.validated_manifest_candidates) == 3
    assert len(report.rejected_needs_user_manifests) == 3


def test_sample_manifest_outcomes(report):
    outcomes = {
        row["manifest_id"]: row["facade_decision"]
        for row in report.manifest_candidates
    }
    assert (
        outcomes["read_only_vendor_connector_manifest"]
        == "facade_validated_manifest_candidate_only"
    )
    assert (
        outcomes["bounded_llm_semantic_executor_manifest"]
        == "facade_validated_manifest_candidate_only"
    )
    assert (
        outcomes["local_drs_reuse_helper_manifest"]
        == "facade_validated_manifest_candidate_only"
    )
    assert outcomes["external_action_connector_manifest"] == "rejected"
    assert outcomes["authority_escalation_manifest"] == "rejected"
    assert outcomes["incomplete_manifest_missing_risk_or_permission"] == "needs_user"


def test_manifest_contract_fields_are_present(report):
    required = set(report.capability_manifest_contract["contract_fields"])
    for row in report.manifest_candidates:
        assert required.issubset(row.keys())


def test_adversarial_attempt_counts_and_blocking(report):
    summary = report.summary
    assert summary["adversarial_attempts_observed"] == 10
    assert summary["adversarial_attempts_blocked"] == 10
    assert len(report.adversarial_manifest_attempts) == 10
    assert all(row["detected"] is True for row in report.adversarial_manifest_attempts)
    assert all(row["blocked"] is True for row in report.adversarial_manifest_attempts)
    assert all(
        row["final_effect"] == "blocked"
        for row in report.adversarial_manifest_attempts
    )


def test_adversarial_attempts_create_no_illegal_effects(report):
    for row in report.adversarial_manifest_attempts:
        for field in (
            "authority_transferred",
            "final_output_created",
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


def test_no_installation_action_or_drs_write_occurs(report):
    summary = report.summary
    assert summary["installed_capabilities_created"] == 0
    assert summary["installed_needles_created"] == 0
    assert summary["external_actions_executed"] == 0
    assert summary["global_drs_write"] is False
    assert summary["external_drs_write"] is False
    assert summary["no_global_drs_write"] is True
    assert summary["no_external_drs_write"] is True


def test_transition_matrix_and_manifest_are_not_authority(report):
    summary = report.summary
    assert summary["transition_matrix_required"] is True
    assert summary["transition_matrix_is_authority"] is False
    assert summary["developer_manifest_is_authority"] is False
    assert summary["capability_manifest_is_installed_capability"] is False
    assert report.kernel_transition_matrix_boundary["root_remains_final_authority"] is True


def test_permission_risk_and_observation_boundaries(report):
    summary = report.summary
    assert summary["risk_class_is_safety_proof"] is False
    assert summary["permission_boundary_is_execution"] is False
    assert summary["external_observation_schema_is_evidence_acceptance"] is False
    assert summary["validated_manifest_is_accepted_evidence"] is False
    assert summary["validated_manifest_is_truth"] is False
    assert summary["validated_manifest_is_final_output"] is False


def test_root_installation_and_authority_boundaries(report):
    summary = report.summary
    assert summary["root_remains_final_authority"] is True
    assert summary["root_commit_required_for_installation"] is True
    assert report.root_final["root_result"] == "developer_facade_capability_manifest_ux_completed"
    assert report.root_final["installed_capabilities_created"] == 0
    assert report.root_final["installed_needles_created"] == 0


def test_llm_and_drs_boundaries(report):
    summary = report.summary
    assert summary["llm_is_bounded_executor_node_capability"] is True
    assert summary["llm_is_authority"] is False
    assert summary["drs_reuse_is_authority"] is False
    assert report.llm_drs_action_boundary["llm_can_finalize"] is False
    assert report.llm_drs_action_boundary["llm_can_write_drs_by_itself"] is False


def test_facade_does_not_bypass_kernel_or_authorize_killer_demo(report):
    summary = report.summary
    assert summary["kernel_enforcement_checkpoint_referenced"] is True
    assert summary["developer_facade_does_not_bypass_transition_matrix"] is True
    assert summary["developer_facade_does_not_authorize_killer_demo"] is True


def test_no_external_or_deferred_system_is_used(report):
    summary = report.summary
    for field in (
        "no_network",
        "no_gemini",
        "no_external_action",
        "no_global_drs_write",
        "no_external_drs_write",
        "no_installed_capability",
        "no_installed_needle",
        "no_production_persistence",
        "no_marennya",
        "no_up",
    ):
        assert summary[field] is True


def test_summary_status_and_readiness(report):
    summary = report.summary
    assert summary["developer_facade_capability_manifest_ux_v01_status"] == "PASS"
    assert summary["proof_type"] == "deterministic_local_proof_only"
    assert summary["production_ui_implemented"] is False
    assert summary["production_capability_registry_implemented"] is False
    assert summary["runtime_rewrite_performed"] is False
    assert summary["schemas_modified"] is False
    assert summary["real_connector_created"] is False
    assert summary["real_api_called"] is False
    assert summary["source_collectors_replayed"] is False
    assert (
        summary["ready_for_developer_facade_capability_manifest_ux_v01_tests"]
        is True
    )


def test_audit_hash_matches_canonical_proof_artifact(report):
    assert report.audit_entry["canonical_payload_hash"] == canonical_hash(
        report.proof_artifact
    )
    assert report.audit_entry["audit_chain_decides_truth"] is False
