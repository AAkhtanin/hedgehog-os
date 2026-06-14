from __future__ import annotations

import pytest

from demo.run_audit_hash_chain import canonical_hash
from demo.run_external_evidence_acceptance_gate_v01 import (
    collect_external_evidence_acceptance_gate_v01,
    render_external_evidence_acceptance_gate_v01,
)


@pytest.fixture(scope="module")
def report():
    return collect_external_evidence_acceptance_gate_v01()


def _by_id(rows, key):
    return {row[key]: row for row in rows}


def test_runner_title_and_required_sections(report):
    output = render_external_evidence_acceptance_gate_v01(report)
    for heading in (
        "[EXTERNAL EVIDENCE ACCEPTANCE GATE v0.1]",
        "[SOURCE EVIDENCE]",
        "[EVIDENCE CANDIDATES]",
        "[VALIDATION PACKETS]",
        "[ACCEPTANCE DECISIONS]",
        "[ACCEPTED EVIDENCE]",
        "[REJECTED / QUARANTINED EVIDENCE]",
        "[BOUNDARY MATRIX]",
        "[ADVERSARIAL ATTEMPTS]",
        "[CONFLICTCHECK]",
        "[GT ADVISORY]",
        "[ROOT FINAL]",
        "[AUDIT]",
        "[SUMMARY]",
    ):
        assert heading in output


def test_source_metadata_does_not_replay_collectors(report):
    assert report.source_evidence["read_only_enterprise_connector_sandbox_source_status"] == "PASS"
    assert report.source_evidence["source_evidence_mode"] == "closed_checkpoint_metadata_only"
    assert report.source_evidence["source_collectors_replayed"] is False


def test_required_candidate_validation_and_decision_counts(report):
    assert len(report.evidence_candidates) == 6
    assert len(report.validation_packets) == 6
    assert len(report.acceptance_decisions) == 6


def test_candidates_remain_candidate_only_until_root_decision(report):
    assert all(
        row["candidate_effect"] == "candidate_only"
        and row["final_effect"] == "candidate_only"
        and row["final_effect"] != "accepted_evidence_only"
        for row in report.evidence_candidates
    )
    assert {
        row["expected_post_root_effect"] for row in report.evidence_candidates
    } == {
        "accepted_evidence_only",
        "rejected_stale_or_expired_evidence",
        "quarantined_unknown_source",
        "rejected_signature_mismatch",
        "rejected_revoked_evidence",
    }


def test_only_root_decisions_and_accepted_evidence_carry_accepted_effect(report):
    decision_effects = {
        row["scenario_id"]: row["final_effect"] for row in report.acceptance_decisions
    }
    assert decision_effects["accepted_bank_payment_evidence"] == "accepted_evidence_only"
    assert decision_effects["accepted_warehouse_stock_evidence"] == "accepted_evidence_only"
    assert all(
        row["final_effect"] == "accepted_evidence_only"
        for row in report.accepted_evidence
    )
    assert all(
        row["final_effect"] != "accepted_evidence_only"
        for row in report.rejected_evidence + report.quarantined_evidence
    )


def test_exactly_two_clean_candidates_are_accepted(report):
    assert {row["scenario_id"] for row in report.accepted_evidence} == {
        "accepted_bank_payment_evidence",
        "accepted_warehouse_stock_evidence",
    }


def test_failed_candidates_are_not_accepted(report):
    accepted = {row["scenario_id"] for row in report.accepted_evidence}
    assert accepted.isdisjoint(
        {
            "rejected_stale_legal_certificate_evidence",
            "quarantined_unknown_source_evidence",
            "rejected_signature_mismatch_evidence",
            "rejected_revoked_evidence",
        }
    )
    assert len(report.rejected_evidence) == 3
    assert len(report.quarantined_evidence) == 1


def test_validation_dimensions_and_mock_boundaries(report):
    assert all(
        row["root_review_required"] is True
        and row["validation_packet_is_root_final"] is False
        and row["local_proof_only"] is True
        and row["real_signature_validated"] is False
        and row["real_trust_registry_used"] is False
        and row["real_revocation_registry_used"] is False
        for row in report.validation_packets
    )


def test_root_decisions_create_accept_reject_or_quarantine(report):
    decisions = _by_id(report.acceptance_decisions, "scenario_id")
    assert decisions["accepted_bank_payment_evidence"]["root_accepted"] is True
    assert decisions["accepted_warehouse_stock_evidence"]["root_accepted"] is True
    assert decisions["rejected_stale_legal_certificate_evidence"]["root_rejected"] is True
    assert decisions["quarantined_unknown_source_evidence"]["root_quarantined"] is True


def test_accepted_evidence_is_not_truth_ready_action_write_or_needle(report):
    for row in report.accepted_evidence:
        assert row["truth_proven"] is False
        assert row["readiness_finalized_by_evidence"] is False
        assert row["ready_status_created"] is False
        assert row["external_action_executed"] is False
        assert row["global_drs_write"] is False
        assert row["external_drs_write"] is False
        assert row["installed_needle_created"] is False


def test_all_boundary_invariants_hold(report):
    assert all(value is True for value in report.boundary_matrix.values())


def test_all_eight_adversarial_attempts_are_blocked(report):
    assert len(report.adversarial_attempts) == 8
    assert all(row["detected"] is True and row["blocked"] is True for row in report.adversarial_attempts)


def test_adversarial_attempts_create_no_illegal_effect(report):
    for row in report.adversarial_attempts:
        for field in (
            "accepted_evidence_created",
            "truth_proven",
            "ready_status_created",
            "authority_transferred",
            "external_action_executed",
            "global_drs_write",
            "external_drs_write",
            "installed_needle_created",
            "real_signature_validated",
            "production_persistence",
        ):
            assert row[field] is False


def test_conflictcheck_and_gt_are_not_acceptance_authority(report):
    assert report.conflictcheck_result["conflict_detected"] is True
    assert report.conflictcheck_result["conflictcheck_is_authority"] is False
    assert report.gt_advisory["gt_is_advisory"] is True
    assert report.gt_advisory["gt_can_accept_evidence"] is False


def test_root_final_counts_and_boundaries(report):
    root = report.root_final
    assert root["root_result"] == "external_evidence_acceptance_gate_completed"
    assert root["evidence_candidates_created"] == 6
    assert root["validation_packets_created"] == 6
    assert root["accepted_evidence_created"] == 2
    assert root["rejected_evidence_created"] == 3
    assert root["quarantined_evidence_created"] == 1
    assert root["adversarial_attempts_observed"] == 8
    assert root["adversarial_attempts_blocked"] == 8
    assert root["root_remains_final_authority"] is True


def test_no_external_or_production_system_is_used(report):
    root = report.root_final
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


def test_summary_pass_and_ready(report):
    assert report.summary["external_evidence_acceptance_gate_v01_status"] == "PASS"
    assert report.summary["ready_for_external_evidence_acceptance_gate_v01_tests"] is True
