from __future__ import annotations

import pytest

from demo.run_audit_hash_chain import canonical_hash
from demo.run_enterprise_chaos_pack_v01 import (
    collect_enterprise_chaos_pack_v01,
    render_enterprise_chaos_pack_v01,
)


@pytest.fixture(scope="module")
def report():
    return collect_enterprise_chaos_pack_v01()


def test_renderer_has_required_sections(report):
    output = render_enterprise_chaos_pack_v01(report)
    for section in (
        "[SOURCE CHECKPOINTS]",
        "[ENTERPRISE CHAOS REQUEST]",
        "[CHAOS ATTEMPTS]",
        "[QUARANTINE SUMMARY]",
        "[BOUNDARY MATRIX]",
        "[ROOT FINAL]",
        "[AUDIT]",
        "[SUMMARY]",
    ):
        assert section in output


def test_source_checkpoints_are_closed_pass_metadata(report):
    assert len(report.source_checkpoints) == 4
    assert all(row["checkpoint_status"] == "PASS" for row in report.source_checkpoints)
    assert all(row["closure_status"] == "closed" for row in report.source_checkpoints)
    assert report.source_evidence["source_evidence_mode"] == "closed_checkpoint_metadata_only"
    assert report.source_evidence["source_collectors_replayed"] is False
    assert report.source_evidence["source_collectors_replayed_count"] == 0


def test_exactly_eighteen_attempts_are_detected_and_blocked(report):
    assert len(report.chaos_attempts) == 18
    assert all(row["detected"] is True for row in report.chaos_attempts)
    assert all(row["blocked"] is True for row in report.chaos_attempts)


def test_exactly_four_attempts_are_quarantined_and_blocked(report):
    quarantined = [
        row for row in report.chaos_attempts if row["final_effect"] == "quarantined_and_blocked"
    ]
    assert len(quarantined) == 4
    assert {row["attempt_id"] for row in quarantined} == {
        "bridge_traversal_to_provenance_laundering",
        "external_pointer_to_global_drs_write",
        "time_envelope_stale_to_current",
        "conflicting_sources_to_ready",
    }


def test_attempts_create_no_illegal_effects(report):
    for row in report.chaos_attempts:
        for field in (
            "authority_transferred",
            "root_bypassed",
            "truth_proven",
            "ready_status_created",
            "accepted_evidence_created_without_gate",
            "external_action_executed",
            "global_drs_write",
            "external_drs_write",
            "installed_needle_created",
            "child_autonomy_created",
            "plan_modified_by_llm",
            "root_final_created_by_non_root",
            "production_persistence",
            "network_called",
            "gemini_called",
        ):
            assert row[field] is False


def test_all_boundary_matrix_values_are_true(report):
    assert all(value is True for value in report.boundary_matrix.values())


def test_root_final_blocks_all_escalations(report):
    root = report.root_final
    assert root["root_result"] == "enterprise_chaos_pack_all_escalations_blocked"
    assert root["safe_secondary_outcome"] == "needs_root_supervised_hardening_before_killer_demo"
    assert root["enterprise_chaos_attempts_blocked"] == 18
    assert root["enterprise_ready"] is False
    assert root["truth_proven"] is False
    assert root["external_action_executed"] is False
    assert root["root_remains_final_authority"] is True


def test_no_external_deferred_or_persistent_system_is_used(report):
    root = report.root_final
    for field in (
        "network_called",
        "gemini_called",
        "telegram_used",
        "marennya_invoked",
        "up_invoked",
        "production_persistence",
        "global_drs_write",
        "external_drs_write",
        "external_action_executed",
        "installed_needle_created",
    ):
        assert root[field] is False


def test_audit_hash_matches_canonical_proof_artifact(report):
    assert report.audit_entry["canonical_payload_hash"] == canonical_hash(report.proof_artifact)
    assert report.audit_entry["audit_chain_decides_truth"] is False


def test_summary_counts_and_pass_status(report):
    summary = report.summary
    assert summary["enterprise_chaos_pack_v01_status"] == "PASS"
    assert summary["enterprise_chaos_attempts_observed"] == 18
    assert summary["enterprise_chaos_attempts_detected"] == 18
    assert summary["enterprise_chaos_attempts_blocked"] == 18
    assert summary["quarantined_and_blocked_count"] == 4
    assert summary["source_checkpoints_referenced"] == 4
    assert summary["source_collectors_replayed"] is False
    assert summary["source_collectors_replayed_count"] == 0
    assert summary["root_finals_created"] == 1
    assert summary["external_actions_executed"] == 0
    assert summary["global_drs_writes"] == 0
    assert summary["external_drs_writes"] == 0
    assert summary["installed_needles_created"] == 0
    assert summary["network_calls"] == 0
    assert summary["gemini_calls"] == 0
    assert summary["production_persistence_writes"] == 0
    assert summary["ready_for_enterprise_chaos_pack_v01_tests"] is True
