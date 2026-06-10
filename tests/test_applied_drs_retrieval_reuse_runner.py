from __future__ import annotations

from copy import deepcopy
from dataclasses import replace

import pytest

from demo.run_applied_drs_retrieval_reuse import (
    collect_applied_drs_retrieval_reuse,
    run_applied_drs_retrieval_reuse,
    validate_applied_drs_retrieval_reuse_report_consistency,
)
from demo.run_audit_hash_chain import canonical_hash


@pytest.fixture(scope="module")
def report():
    return collect_applied_drs_retrieval_reuse()


def _by_id(rows, key):
    return {row[key]: row for row in rows}


def test_runner_title_and_required_sections_exist(report):
    output = run_applied_drs_retrieval_reuse()
    for heading in (
        "[APPLIED DRS RETRIEVAL / REUSE PROOF]",
        "[INPUT / MODE]",
        "[SOURCE EVIDENCE]",
        "[DRS QUERY ARTIFACTS]",
        "[RETRIEVAL CANDIDATES]",
        "[REUSE SCORE ROWS]",
        "[REUSE GATE ROWS]",
        "[WORLDSTATE CHECKS]",
        "[FRESHNESS CHECKS]",
        "[QUARANTINE / DEADEND CHECKS]",
        "[GT]",
        "[ROOT FINAL]",
        "[DRS LIFECYCLE]",
        "[CONFLICTCHECK]",
        "[AUDIT HASH-CHAIN]",
        "[MALICIOUS / UNSAFE REUSE CLAIMS]",
        "[AUTHORITY / SAFETY]",
        "[SUMMARY]",
    ):
        assert heading in output


def test_mode_is_deterministic_local_proof_only(report):
    mode = report.input_mode
    assert mode["mode"] == "deterministic_applied_drs_retrieval_reuse"
    assert mode["local_proof_level_only"] is True
    for key in (
        "live_network_used",
        "telegram_used",
        "real_external_action",
        "production_persistence",
        "global_drs_implemented",
        "external_drs_network_implemented",
        "real_vector_db_used",
        "marennya_invoked",
        "up_invoked",
    ):
        assert mode[key] is False


def test_all_source_proof_statuses_are_pass(report):
    assert set(report.source_evidence.values()) == {"PASS"}


def test_safe_warehouse_and_certificate_reuse_candidates(report):
    candidates = _by_id(report.applied_drs_retrieval_candidates, "retrieval_candidate_id")
    warehouse = candidates["reuse_candidate_warehouse_W18_D2043"]
    certificate = candidates["reuse_candidate_certificate_APP78_CERT311"]
    assert warehouse["source_record_id"] == "warehouse_reuse_candidate_W17_D2042"
    assert warehouse["proposed_reuse_mode"] == "partial_reuse_candidate"
    assert warehouse["worldstate_compatible"] is True
    assert certificate["source_record_id"] == "certificate_reuse_candidate_APP77_CERT310"
    assert certificate["proposed_reuse_mode"] == "needs_user_reuse_candidate"
    assert certificate["permission_boundary_required"] is True
    assert warehouse["direct_reuse_allowed"] is False
    assert certificate["direct_reuse_allowed"] is False


def test_unsafe_retrieval_candidates_are_not_direct_reuse(report):
    candidates = _by_id(report.applied_drs_retrieval_candidates, "retrieval_candidate_id")
    stale = candidates["reuse_candidate_stale_high_similarity"]
    quarantine = candidates["reuse_candidate_quarantined_record"]
    deadend = candidates["reuse_candidate_deadend_branch"]
    wrong = candidates["reuse_candidate_wrong_domain_near_match"]
    permission = candidates["reuse_candidate_permission_trace_as_completed_action"]
    assert stale["semantic_similarity_score"] > 0.9
    assert stale["freshness_status"] == "stale"
    assert quarantine["quarantine_proximity"] is True
    assert deadend["deadend_proximity"] is True
    assert wrong["source_domain"] != wrong["target_domain"]
    assert wrong["worldstate_compatible"] is False
    assert permission["permission_boundary_required"] is True
    assert permission["proposed_reuse_mode"] == "block_reuse"
    assert all(
        candidate["direct_reuse_allowed"] is False
        for candidate in (stale, quarantine, deadend, wrong, permission)
    )


def test_every_candidate_is_root_reviewed_and_never_completes_action(report):
    for candidate in report.applied_drs_retrieval_candidates:
        assert candidate["root_review_required"] is True
        assert candidate["proof_only"] is True
        assert candidate["completed_external_action_claimed"] is False
        assert candidate["production_persistence"] is False
        assert candidate["global_drs_write"] is False


def test_reuse_scores_are_advisory_not_root(report):
    rows = report.applied_reuse_score_rows
    assert len(rows) == 7
    assert all(row["reuse_score_is_advisory"] is True for row in rows)
    assert all(row["reuse_score_decides_root_final"] is False for row in rows)


def test_gate_rows_preserve_required_outcomes(report):
    gates = _by_id(report.applied_reuse_gate_rows, "gate_row_id")
    assert gates["warehouse_similar_request"]["gate_status"] == (
        "accepted_as_partial_reuse_candidate"
    )
    assert gates["certificate_similar_request"]["gate_status"] == (
        "accepted_as_needs_user_reuse_candidate"
    )
    assert gates["stale_high_similarity_record"]["gate_status"] == (
        "downgraded_to_rerun_required"
    )
    assert gates["quarantined_record_attempted_reuse"]["gate_status"] == (
        "blocked_quarantine"
    )
    assert gates["deadend_branch_attempted_reuse"]["gate_status"] == (
        "blocked_or_ask_user"
    )
    assert gates["wrong_domain_near_match"]["gate_status"] == (
        "rejected_domain_mismatch"
    )
    assert gates["permission_trace_reused_as_completed_action_attempt"][
        "gate_status"
    ] == "rejected_conflict"


def test_gt_is_advisory_and_cannot_mark_ready_or_create_candidates(report):
    gt = report.applied_reuse_gt_selection
    assert gt["gt_decides_final_reuse"] is False
    assert gt["gt_is_not_truth_proof"] is True
    assert gt["gt_remains_advisory_until_root"] is True
    assert gt["gt_can_mark_ready"] is False
    assert gt["gt_can_execute_action"] is False
    assert gt["gt_can_create_protocol_candidate"] is False
    assert gt["gt_can_create_needle_candidate"] is False
    assert gt["gt_can_install_needle"] is False


def test_root_final_contains_only_allowed_decisions_and_no_action(report):
    finals = report.applied_reuse_root_final_artifacts
    allowed = {
        "partial_reuse_then_rerun_validation",
        "partial_reuse_then_needs_user",
        "rerun_required",
        "block_reuse_quarantined_record",
        "block_or_ask_user",
        "reject_completed_action_reuse",
    }
    assert {final["root_decision"] for final in finals}.issubset(allowed)
    for final in finals:
        assert final["direct_ready_created"] is False
        assert final["completed_external_action_created"] is False
        assert final["protocol_candidate_created"] is False
        assert final["needle_candidate_created"] is False
        assert final["installed_needle_created"] is False
        assert final["global_drs_write"] is False


def test_drs_lifecycle_records_are_local_proof_only(report):
    records = report.applied_reuse_drs_lifecycle_records
    assert len(records) == 9
    assert all(record["proof_only"] is True for record in records)
    assert all(record["production_persistence"] is False for record in records)
    assert all(record["global_drs_write"] is False for record in records)
    assert all(record["external_drs_write"] is False for record in records)


def test_conflictcheck_has_unsafe_conflicts_and_safe_no_conflicts(report):
    conflicts = _by_id(report.applied_reuse_conflict_reports, "conflict_report_id")
    for conflict_id in (
        "conflict_permission_trace_reused_as_completed_action",
        "conflict_wrong_domain_near_match",
        "conflict_stale_high_similarity_record",
        "conflict_quarantined_record_attempted_reuse",
        "conflict_deadend_branch_attempted_reuse",
    ):
        assert conflicts[conflict_id]["conflict_detected"] is True
    for conflict_id in (
        "no_conflict_warehouse_partial_reuse",
        "no_conflict_certificate_needs_user_reuse",
    ):
        assert conflicts[conflict_id]["conflict_detected"] is False
    assert all(
        conflict["conflictcheck_is_authority"] is False
        for conflict in conflicts.values()
    )


def test_audit_entry_hashes_applied_reuse_artifact(report):
    audit = report.applied_reuse_audit_entry
    assert audit["audit_entry_id"] == "audit_applied_drs_retrieval_reuse_v0_1"
    assert audit["canonical_payload_hash"] == canonical_hash(
        report.applied_reuse_proof_artifact
    )
    assert audit["previous_chain_last_entry_hash"] == (
        report.audit_hash_chain["previous_chain_last_entry_hash"]
    )
    assert audit["proof_only"] is True
    assert audit["production_persistence"] is False
    assert audit["global_drs_write"] is False
    assert audit["audit_chain_decides_truth"] is False


def test_validator_rejects_wrong_audit_hash(report):
    audit = deepcopy(report.applied_reuse_audit_entry)
    audit["canonical_payload_hash"] = "0" * 64
    assert validate_applied_drs_retrieval_reuse_report_consistency(
        replace(report, applied_reuse_audit_entry=audit)
    ) is False


def _corrupt_candidate(report, candidate_id, **changes):
    candidates = deepcopy(report.applied_drs_retrieval_candidates)
    candidate = _by_id(candidates, "retrieval_candidate_id")[candidate_id]
    candidate.update(changes)
    return candidates


def test_validator_rejects_stale_or_quarantine_direct_reuse(report):
    for candidate_id in (
        "reuse_candidate_stale_high_similarity",
        "reuse_candidate_quarantined_record",
    ):
        candidates = _corrupt_candidate(report, candidate_id, direct_reuse_allowed=True)
        assert validate_applied_drs_retrieval_reuse_report_consistency(
            replace(report, applied_drs_retrieval_candidates=candidates)
        ) is False


def test_validator_rejects_deadend_direct_reuse(report):
    candidates = _corrupt_candidate(
        report, "reuse_candidate_deadend_branch", direct_reuse_allowed=True
    )
    assert validate_applied_drs_retrieval_reuse_report_consistency(
        replace(report, applied_drs_retrieval_candidates=candidates)
    ) is False


def test_validator_rejects_wrong_domain_compatible_direct_reuse(report):
    candidates = _corrupt_candidate(
        report,
        "reuse_candidate_wrong_domain_near_match",
        worldstate_compatible=True,
        direct_reuse_allowed=True,
    )
    assert validate_applied_drs_retrieval_reuse_report_consistency(
        replace(report, applied_drs_retrieval_candidates=candidates)
    ) is False


def test_validator_rejects_permission_trace_completed_action_acceptance(report):
    candidates = _corrupt_candidate(
        report,
        "reuse_candidate_permission_trace_as_completed_action",
        proposed_reuse_mode="direct_reuse_candidate",
        direct_reuse_allowed=True,
        completed_external_action_claimed=True,
    )
    assert validate_applied_drs_retrieval_reuse_report_consistency(
        replace(report, applied_drs_retrieval_candidates=candidates)
    ) is False


def test_validator_rejects_root_direct_ready(report):
    finals = deepcopy(report.applied_reuse_root_final_artifacts)
    finals[0]["direct_ready_created"] = True
    assert validate_applied_drs_retrieval_reuse_report_consistency(
        replace(report, applied_reuse_root_final_artifacts=finals)
    ) is False


def test_validator_rejects_candidate_or_install_creation(report):
    for key in ("needle_candidate_created", "installed_needle_created"):
        authority = deepcopy(report.authority_safety)
        authority[key] = True
        assert validate_applied_drs_retrieval_reuse_report_consistency(
            replace(report, authority_safety=authority)
        ) is False


def test_validator_rejects_production_persistence_or_global_drs(report):
    for key in ("no_production_persistence", "no_global_drs_write"):
        authority = deepcopy(report.authority_safety)
        authority[key] = False
        assert validate_applied_drs_retrieval_reuse_report_consistency(
            replace(report, authority_safety=authority)
        ) is False


def test_authority_and_summary_preserve_all_boundaries(report):
    assert all(report.malicious_unsafe_reuse_claims.values())
    authority = report.authority_safety
    assert authority["drs_retrieval_is_authority"] is False
    assert authority["semantic_similarity_is_not_authority"] is True
    assert authority["reuse_score_is_not_root"] is True
    assert authority["root_remains_final_authority"] is True
    assert authority["no_real_external_action_executed"] is True
    summary = report.summary
    assert summary["applied_drs_retrieval_reuse_status"] == "PASS"
    assert summary["scenarios_verified"] == 7
    assert summary["explicit_applied_reuse_artifacts_consistent"] is True
    assert summary["ready_for_applied_drs_retrieval_reuse_docs_sync"] is True
    assert summary["protocol_candidate_created"] is False
    assert summary["needle_candidate_created"] is False
    assert summary["installed_needle_created"] is False
    assert summary["production_autonomy_claimed"] is False
