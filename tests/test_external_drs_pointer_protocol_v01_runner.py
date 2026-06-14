from __future__ import annotations

import pytest

from demo.run_audit_hash_chain import canonical_hash
from demo.run_external_drs_pointer_protocol_v01 import (
    collect_external_drs_pointer_protocol_v01,
    render_external_drs_pointer_protocol_v01,
)


@pytest.fixture(scope="module")
def report():
    return collect_external_drs_pointer_protocol_v01()


def _by_id(rows, key):
    return {row[key]: row for row in rows}


def test_runner_title_and_required_sections_exist(report):
    output = render_external_drs_pointer_protocol_v01(report)
    for heading in (
        "[EXTERNAL DRS POINTER PROTOCOL v0.1]",
        "[SOURCE EVIDENCE]",
        "[POINTER CANDIDATES]",
        "[PROTOCOL BOUNDARY MATRIX]",
        "[ADVERSARIAL ATTEMPTS]",
        "[CONFLICTCHECK]",
        "[GT ADVISORY]",
        "[ROOT FINAL]",
        "[AUDIT]",
        "[SUMMARY]",
    ):
        assert heading in output


def test_source_statuses_pass(report):
    status_fields = {
        key: value
        for key, value in report.source_evidence.items()
        if key.endswith("_source_status")
    }
    assert set(status_fields.values()) == {"PASS"}
    assert report.source_evidence["source_collectors_replayed"] is False
    assert (
        report.source_evidence["source_evidence_mode"]
        == "closed_checkpoint_metadata_only"
    )


def test_exactly_two_pointer_candidates_exist(report):
    assert len(report.pointer_candidates) == 2


def test_pointer_candidates_are_not_accepted_trusted_evidence(report):
    assert all(
        row["pointer_kind"] == "external_drs_pointer_candidate"
        and row["trusted_evidence_created"] is False
        for row in report.pointer_candidates
    )
    assert report.root_final["pointer_candidates_accepted"] == 0


def test_external_pointer_candidate_is_not_external_drs(report):
    assert report.protocol_boundary_matrix["external_pointer_is_not_external_drs"]
    assert all(row["external_drs_implemented"] is False for row in report.pointer_candidates)


def test_no_retrieval_network_or_connector_performed(report):
    assert all(
        row["retrieval_performed"] is False
        and row["remote_source_contacted"] is False
        and row["external_network_called"] is False
        for row in report.pointer_candidates
    )
    assert report.root_final["real_connector_used"] is False


def test_pointer_claim_is_not_truth(report):
    assert report.protocol_boundary_matrix["pointer_claim_is_not_truth"] is True
    assert all(row["truth_proven"] is False for row in report.pointer_candidates)


def test_pointer_status_does_not_finalize(report):
    assert report.protocol_boundary_matrix["pointer_status_does_not_finalize"] is True


def test_pointer_cannot_execute_action(report):
    assert report.protocol_boundary_matrix["pointer_cannot_execute_action"] is True


def test_pointer_cannot_write_global_or_external_drs(report):
    boundary = report.protocol_boundary_matrix
    assert boundary["pointer_cannot_write_global_drs"] is True
    assert boundary["pointer_cannot_write_external_drs"] is True


def test_pointer_cannot_install_needle(report):
    assert report.protocol_boundary_matrix["pointer_cannot_install_needle"] is True


def test_pointer_cannot_bypass_required_boundaries(report):
    boundary = report.protocol_boundary_matrix
    for field in (
        "pointer_cannot_bypass_root",
        "pointer_cannot_bypass_conflictcheck",
        "pointer_cannot_bypass_gt",
        "pointer_cannot_bypass_permission_needsuser",
        "pointer_cannot_bypass_quarantine",
    ):
        assert boundary[field] is True


def test_signature_placeholder_is_not_signature(report):
    assert report.protocol_boundary_matrix["signature_placeholder_is_not_signature"]


def test_trust_placeholder_is_not_trust(report):
    assert report.protocol_boundary_matrix["trust_registry_placeholder_is_not_trust"]


def test_revocation_placeholder_is_not_revocation(report):
    assert report.protocol_boundary_matrix["revocation_placeholder_is_not_revocation"]


def test_exactly_six_adversarial_attempts_exist(report):
    assert len(report.adversarial_attempts) == 6


def test_all_adversarial_attempts_detected_and_blocked(report):
    assert all(
        row["detected"] is True and row["blocked"] is True
        for row in report.adversarial_attempts
    )


def test_untrusted_source_laundering_is_quarantined_and_blocked(report):
    attempts = _by_id(report.adversarial_attempts, "attempt_id")
    laundering = attempts["adversary_untrusted_source_laundering"]
    assert laundering["quarantined"] is True
    assert laundering["blocked"] is True
    assert laundering["final_effect"] == "quarantined_blocked"


def test_no_attempt_creates_trusted_evidence_or_truth(report):
    assert all(
        row["trusted_evidence_created"] is False and row["truth_proven"] is False
        for row in report.adversarial_attempts
    )


def test_no_attempt_executes_writes_installs_or_transfers(report):
    assert all(
        row["external_action_executed"] is False
        and row["global_drs_write"] is False
        and row["external_drs_write"] is False
        and row["installed_needle_created"] is False
        and row["authority_transferred"] is False
        for row in report.adversarial_attempts
    )


def test_conflictcheck_detects_all_attempts_but_is_not_authority(report):
    conflict = report.conflictcheck_result
    assert conflict["conflict_detected"] is True
    assert conflict["conflict_count"] == 6
    assert conflict["conflictcheck_is_authority"] is False


def test_gt_cannot_promote_pointer_or_execute(report):
    gt = report.gt_advisory
    assert gt["gt_is_advisory"] is True
    for field in (
        "gt_can_mark_pointer_trusted",
        "gt_can_mark_truth",
        "gt_can_execute_action",
        "gt_can_write_external_drs",
        "gt_can_install_needle",
    ):
        assert gt[field] is False


def test_root_final_blocks_or_quarantines_pointer_escalation(report):
    root = report.root_final
    assert root["root_result"] == "blocked_or_quarantined"
    assert root["safe_secondary_outcome"] == "needs_external_pointer_protocol_hardening"
    assert root["root_remains_final_authority"] is True


def test_root_accepts_zero_pointer_candidates(report):
    root = report.root_final
    assert root["pointer_candidates_observed"] == 2
    assert root["pointer_candidates_accepted"] == 0


def test_no_external_drs_fabric_internet_or_persistence(report):
    root = report.root_final
    assert root["external_drs_implemented"] is False
    assert root["global_semantic_fabric_claimed"] is False
    assert root["public_internet_of_meaning_claimed"] is False
    assert root["production_persistence"] is False
    assert root["remote_retrieval_performed"] is False


def test_no_external_system_or_deferred_layer_invoked(report):
    root = report.root_final
    for field in (
        "gemini_called",
        "network_called",
        "telegram_used",
        "marennya_invoked",
        "up_invoked",
    ):
        assert root[field] is False


def test_audit_hash_matches_proof_artifact(report):
    assert report.audit_entry["canonical_payload_hash"] == canonical_hash(
        report.proof_artifact
    )
    assert report.audit_entry["audit_chain_decides_truth"] is False


def test_summary_pass_and_ready_for_tests(report):
    summary = report.summary
    assert summary["external_drs_pointer_protocol_v01_status"] == "PASS"
    assert summary["pointer_candidates_observed"] == 2
    assert summary["pointer_candidates_accepted"] == 0
    assert summary["adversarial_attempts_observed"] == 6
    assert summary["adversarial_attempts_blocked"] == 6
    assert summary["quarantined_attempts_observed"] == 1
    assert summary["ready_for_external_drs_pointer_protocol_v01_tests"] is True
