from __future__ import annotations

from copy import deepcopy
from dataclasses import replace

import pytest

from demo.run_audit_hash_chain import canonical_hash
from demo.run_drs_adversarial_stress_pack import (
    collect_drs_adversarial_stress_pack,
    run_drs_adversarial_stress_pack,
    validate_drs_adversarial_stress_pack_report_consistency,
)


@pytest.fixture(scope="module")
def report():
    return collect_drs_adversarial_stress_pack()


def _by_id(rows, key):
    return {row[key]: row for row in rows}


def test_runner_title_and_required_sections_exist(report):
    output = run_drs_adversarial_stress_pack()
    for heading in (
        "[DRS ADVERSARIAL STRESS PACK]",
        "[INPUT / MODE]",
        "[SOURCE EVIDENCE]",
        "[ADVERSARIAL INPUTS]",
        "[ADVERSARIAL RETRIEVAL CANDIDATES]",
        "[DETECTION ROWS]",
        "[GATE ROWS]",
        "[GT]",
        "[ROOT FINAL]",
        "[CONFLICTCHECK]",
        "[AUDIT HASH-CHAIN]",
        "[AUTHORITY / SAFETY]",
        "[SUMMARY]",
    ):
        assert heading in output


def test_source_proof_statuses_are_pass(report):
    assert set(report.source_evidence.values()) == {"PASS"}


def test_all_eight_scenarios_exist_and_are_bounded(report):
    assert len(report.drs_adversarial_inputs) == 8
    assert len(report.drs_adversarial_retrieval_candidates) == 8
    assert all(
        candidate["direct_reuse_allowed"] is False
        and candidate["root_review_required"] is True
        for candidate in report.drs_adversarial_retrieval_candidates
    )


def test_gate_outcomes_block_all_attacks(report):
    gates = _by_id(report.drs_adversarial_gate_rows, "gate_row_id")
    expected = {
        "spoofed_high_similarity_score": "rejected_score_spoof",
        "fake_freshness_on_stale_record": "downgraded_to_rerun_required",
        "quarantine_laundering_attempt": "blocked_quarantine_laundering",
        "deadend_laundering_attempt": "blocked_deadend_laundering",
        "permission_laundering_attempt": "rejected_permission_laundering",
        "domain_camouflage_attempt": "rejected_domain_camouflage",
        "fake_audit_hash_attempt": "blocked_bad_audit_hash",
        "root_final_injection_attempt": "rejected_injected_root_final",
    }
    assert {key: row["gate_status"] for key, row in gates.items()} == expected


def test_adversarial_detection_fields_are_explicit(report):
    candidates = _by_id(
        report.drs_adversarial_retrieval_candidates, "adversarial_candidate_id"
    )
    assert candidates["adversarial_candidate_spoofed_high_similarity_score"][
        "claimed_reuse_score"
    ] > candidates["adversarial_candidate_spoofed_high_similarity_score"][
        "independent_reuse_score"
    ]
    assert candidates["adversarial_candidate_fake_freshness_on_stale_record"][
        "independent_freshness"
    ] == "stale"
    assert candidates["adversarial_candidate_quarantine_laundering_attempt"][
        "quarantine_lineage_detected"
    ] is True
    assert candidates["adversarial_candidate_deadend_laundering_attempt"][
        "deadend_lineage_detected"
    ] is True
    assert candidates["adversarial_candidate_permission_laundering_attempt"][
        "permission_laundering_detected"
    ] is True
    assert candidates["adversarial_candidate_domain_camouflage_attempt"][
        "domain_camouflage_detected"
    ] is True
    assert candidates["adversarial_candidate_fake_audit_hash_attempt"][
        "audit_hash_valid"
    ] is False
    assert candidates["adversarial_candidate_root_final_injection_attempt"][
        "injected_root_final_detected"
    ] is True


def test_gt_remains_advisory(report):
    gt = report.drs_adversarial_gt_selection
    assert gt["gt_decides_final_reuse"] is False
    assert gt["gt_remains_advisory_until_root"] is True
    assert gt["gt_can_mark_ready"] is False
    assert gt["gt_can_execute_action"] is False
    assert gt["gt_can_create_protocol_candidate"] is False
    assert gt["gt_can_create_needle_candidate"] is False
    assert gt["gt_can_install_needle"] is False


def test_root_decisions_are_allowed_only(report):
    allowed = {
        "block_reuse_score_spoof",
        "rerun_required",
        "block_reuse_quarantine_laundering",
        "block_reuse_deadend_laundering",
        "reject_permission_laundering",
        "reject_domain_camouflage",
        "block_reuse_bad_audit_hash",
        "reject_injected_root_final",
    }
    assert {
        final["root_decision"] for final in report.drs_adversarial_root_final_artifacts
    } == allowed
    assert all(
        final["direct_ready_created"] is False
        and final["completed_external_action_created"] is False
        and final["protocol_candidate_created"] is False
        and final["needle_candidate_created"] is False
        and final["installed_needle_created"] is False
        for final in report.drs_adversarial_root_final_artifacts
    )


def test_conflicts_cover_every_attack_and_remain_advisory(report):
    assert len(report.drs_adversarial_conflict_reports) == 8
    assert all(
        conflict["conflict_detected"] is True
        and conflict["conflictcheck_is_authority"] is False
        for conflict in report.drs_adversarial_conflict_reports
    )


def test_no_production_global_or_external_writes(report):
    assert all(
        candidate["production_persistence"] is False
        and candidate["global_drs_write"] is False
        and candidate["external_drs_write"] is False
        for candidate in report.drs_adversarial_retrieval_candidates
    )
    authority = report.authority_safety
    assert authority["no_production_persistence"] is True
    assert authority["no_global_drs_write"] is True
    assert authority["no_external_drs_write"] is True


def test_audit_hash_matches_proof_artifact(report):
    audit = report.drs_adversarial_audit_entry
    assert audit["canonical_payload_hash"] == canonical_hash(
        report.drs_adversarial_proof_artifact
    )
    assert audit["audit_chain_decides_truth"] is False


def _corrupt_candidate(report, candidate_id, **changes):
    candidates = deepcopy(report.drs_adversarial_retrieval_candidates)
    _by_id(candidates, "adversarial_candidate_id")[candidate_id].update(changes)
    return candidates


def test_validator_rejects_spoofed_score_direct_reuse(report):
    candidates = _corrupt_candidate(
        report,
        "adversarial_candidate_spoofed_high_similarity_score",
        direct_reuse_allowed=True,
    )
    assert validate_drs_adversarial_stress_pack_report_consistency(
        replace(report, drs_adversarial_retrieval_candidates=candidates)
    ) is False


def test_validator_rejects_fake_audit_hash_acceptance(report):
    candidates = _corrupt_candidate(
        report, "adversarial_candidate_fake_audit_hash_attempt", audit_hash_valid=True
    )
    assert validate_drs_adversarial_stress_pack_report_consistency(
        replace(report, drs_adversarial_retrieval_candidates=candidates)
    ) is False


def test_validator_rejects_injected_root_final_acceptance(report):
    candidates = _corrupt_candidate(
        report,
        "adversarial_candidate_root_final_injection_attempt",
        injected_root_final_detected=False,
    )
    assert validate_drs_adversarial_stress_pack_report_consistency(
        replace(report, drs_adversarial_retrieval_candidates=candidates)
    ) is False


def test_summary_pass_and_boundaries_hold(report):
    summary = report.summary
    assert summary["drs_adversarial_stress_pack_status"] == "PASS"
    assert summary["scenarios_verified"] == 8
    assert summary["explicit_drs_adversarial_artifacts_consistent"] is True
    assert summary["ready_for_drs_adversarial_stress_pack_tests"] is True
    assert summary["drs_retrieval_is_not_authority"] is True
    assert summary["root_remains_final_authority"] is True
    assert summary["protocol_candidate_created"] is False
    assert summary["needle_candidate_created"] is False
    assert summary["installed_needle_created"] is False
    assert summary["production_autonomy_claimed"] is False
