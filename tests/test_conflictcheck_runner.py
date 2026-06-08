from __future__ import annotations

import copy

from demo.run_conflictcheck import (
    CONFLICT_TYPES,
    collect_conflictcheck,
    run_conflictcheck,
)
from demo.run_drs_lifecycle_semantics import collect_drs_lifecycle_semantics


def _report():
    return collect_conflictcheck()


def _reports():
    return {row["conflict_type"]: row for row in _report().conflict_reports}


def _pairs():
    return {row["scenario"]: row for row in _report().conflict_candidate_pairs}


def test_runner_contains_required_sections():
    output = run_conflictcheck()
    for heading in (
        "[CONFLICTCHECK]",
        "[INPUT / MODE]",
        "[SOURCE LIFECYCLE]",
        "[CONFLICT CANDIDATE PAIRS]",
        "[CONFLICT REPORTS]",
        "[MALICIOUS CLAIMS]",
        "[AUTHORITY / SAFETY]",
        "[SUMMARY]",
    ):
        assert heading in output


def test_lifecycle_collector_is_consumed_without_network():
    report = _report()
    source = report.source_lifecycle
    assert source["source_collector"] == "collect_drs_lifecycle_semantics"
    assert source["drs_lifecycle_semantics_status"] == "PASS"
    assert source["lifecycle_records_consumed"] == 13
    assert source["conflict_status_default"] == "not_checked"
    assert source["lifecycle_records_local_only"] is True
    assert source["root_commit_authority_preserved"] is True
    assert report.input_mode["live_network_used"] is False


def test_lifecycle_records_are_consumed_and_unchanged():
    lifecycle = collect_drs_lifecycle_semantics()
    before = copy.deepcopy(lifecycle.lifecycle_records)
    report = _report()
    after = collect_drs_lifecycle_semantics().lifecycle_records
    assert before == after
    assert report.source_lifecycle["lifecycle_records_unchanged"] is True
    assert report.authority_safety["lifecycle_records_unchanged"] is True


def test_all_required_candidate_pairs_and_reports_are_created():
    report = _report()
    assert set(_pairs()) == set(CONFLICT_TYPES)
    assert set(_reports()) == set(CONFLICT_TYPES)
    assert len(report.conflict_candidate_pairs) == 11
    assert len(report.conflict_reports) == 11
    for pair in report.conflict_candidate_pairs:
        assert pair["left_experience_record_id"]
        assert pair["right_experience_record_id"]
        assert pair["shared_resonance_tags"]
        assert pair["comparison_scope"]
        assert pair["conflict_check_reason"]


def test_completed_conflict_families_are_flagged_for_root_review():
    reports = _reports()
    completed = reports["completed_vs_completed_conflict"]
    deadend = reports["completed_vs_deadend_conflict"]
    assert completed["conflict_status"] == "flagged"
    assert completed["severity"] in {"medium", "high"}
    assert completed["root_review_required"] is True
    assert deadend["conflict_status"] == "flagged"
    assert deadend["severity"] == "high"
    assert deadend["reuse_block_recommended"] is True
    assert deadend["root_review_required"] is True


def test_reuse_candidate_vs_quarantine_blocks_reuse_and_requests_review():
    report = _reports()["reuse_candidate_vs_quarantine_conflict"]
    assert report["reuse_block_recommended"] is True
    assert report["quarantine_review_recommended"] is True
    assert report["root_review_required"] is True


def test_promotion_candidate_vs_rejected_evidence_blocks_promotion():
    report = _reports()["promotion_candidate_vs_rejected_evidence"]
    assert report["promotion_block_recommended"] is True
    assert report["gt_review_recommended"] is True
    assert report["root_review_required"] is True


def test_stale_vs_fresh_sets_record_ids_without_invalidating():
    report = _reports()["stale_vs_fresh_conflict"]
    assert report["older_record_id"]
    assert report["newer_record_id"]
    assert report["older_record_id"] != report["newer_record_id"]
    assert report["invalidation_recommended"] is True
    assert report["conflictcheck_invalidates_record"] is False
    assert report["root_review_required"] is True


def test_lower_trust_vs_higher_trust_recommends_gt_without_choosing_winner():
    report = _reports()["lower_trust_vs_higher_trust_conflict"]
    assert report["lower_trust_record_id"]
    assert report["higher_trust_record_id"]
    assert report["lower_trust_record_id"] != report["higher_trust_record_id"]
    assert report["gt_review_recommended"] is True
    assert report["conflictcheck_decides_truth"] is False


def test_action_like_blocked_vs_reuse_blocks_reuse_and_promotion():
    report = _reports()["action_like_blocked_vs_reuse_conflict"]
    assert report["severity"] == "critical"
    assert report["reuse_block_recommended"] is True
    assert report["promotion_block_recommended"] is True
    assert report["root_review_required"] is True


def test_permission_required_vs_action_execution_is_critical_and_no_action_runs():
    report = _reports()["permission_required_vs_action_execution_conflict"]
    assert report["severity"] == "critical"
    assert report["reuse_block_recommended"] is True
    assert report["root_review_required"] is True
    assert report["production_external_action_executed"] is False


def test_protocol_and_needle_candidate_conflicts_block_promotion():
    reports = _reports()
    protocol = reports["protocol_candidate_vs_deadend_conflict"]
    needle = reports["needle_candidate_vs_quarantine_conflict"]
    assert protocol["promotion_block_recommended"] is True
    assert protocol["gt_review_recommended"] is True
    assert protocol["root_review_required"] is True
    assert needle["promotion_block_recommended"] is True
    assert needle["quarantine_review_recommended"] is True
    assert needle["root_review_required"] is True
    lifecycle = collect_drs_lifecycle_semantics()
    assert lifecycle.promotion_ladder["installed_needle_count"] == 0


def test_same_completed_lineage_has_no_conflict_or_review_blocks():
    report = _reports()["no_conflict_same_completed_lineage"]
    assert report["conflict_status"] == "no_conflict"
    assert report["severity"] == "info"
    assert report["root_review_required"] is False
    assert report["reuse_block_recommended"] is False
    assert report["promotion_block_recommended"] is False


def test_flagged_and_needs_review_conflicts_require_root_review():
    for report in _report().conflict_reports:
        if report["conflict_status"] != "no_conflict":
            assert report["root_review_required"] is True


def test_reports_are_flags_only_and_never_mutate_or_decide():
    for report in _report().conflict_reports:
        assert report["created_by"] == "conflictcheck_v0_1"
        assert report["conflictcheck_decides_truth"] is False
        assert report["conflictcheck_mutates_drs"] is False
        assert report["conflictcheck_invalidates_record"] is False
        assert report["conflictcheck_promotes_record"] is False
        assert report["conflictcheck_demotes_record"] is False
        assert report["root_remains_authority"] is True
        assert report["production_persistence"] is False
        assert report["global_drs_write"] is False
        assert report["external_drs_network_write"] is False


def test_malicious_authority_and_mutation_claims_are_rejected():
    malicious = _report().malicious_claims
    assert malicious["malicious_conflictcheck_truth_decision_claim_rejected"] is True
    assert malicious["malicious_conflictcheck_drs_mutation_claim_rejected"] is True
    assert malicious["malicious_conflictcheck_invalidation_claim_rejected"] is True
    assert malicious["malicious_conflictcheck_promotion_claim_rejected"] is True
    assert malicious["malicious_conflictcheck_demotion_claim_rejected"] is True
    assert malicious["conflictcheck_decides_truth"] is False
    assert malicious["conflictcheck_mutates_drs"] is False
    assert malicious["conflictcheck_invalidates_record"] is False
    assert malicious["conflictcheck_promotes_record"] is False
    assert malicious["conflictcheck_demotes_record"] is False


def test_malicious_production_global_and_external_claims_are_rejected():
    malicious = _report().malicious_claims
    assert malicious["malicious_production_persistence_claim_rejected"] is True
    assert malicious["malicious_global_drs_write_claim_rejected"] is True
    assert malicious["malicious_external_drs_network_claim_rejected"] is True
    assert malicious["production_persistence"] is False
    assert malicious["global_drs_write"] is False
    assert malicious["external_drs_network_write"] is False


def test_authority_and_safety_boundaries_hold():
    authority = _report().authority_safety
    assert authority["conflictcheck_is_authority"] is False
    assert authority["conflictcheck_decides_truth"] is False
    assert authority["conflictcheck_mutates_drs"] is False
    assert authority["conflictcheck_invalidates_records"] is False
    assert authority["conflictcheck_promotes_records"] is False
    assert authority["conflictcheck_demotes_records"] is False
    assert authority["drs_remains_storage_index_lifecycle_layer"] is True
    assert authority["root_remains_final_authority"] is True
    assert authority["gt_review_is_advisory_until_root"] is True
    assert authority["production_persistence_claimed"] is False
    assert authority["global_drs_implemented"] is False
    assert authority["external_drs_network_implemented"] is False
    assert authority["production_external_action_executed"] is False
    assert authority["marennya_invoked"] is False
    assert authority["up_invoked"] is False


def test_pass_summary_is_derived_from_reports_rejections_and_authority():
    report = _report()
    summary = report.summary
    derived_pass = (
        summary["source_drs_lifecycle_status"] == "PASS"
        and summary["lifecycle_records_consumed"] == 13
        and summary["candidate_pairs_created"] == len(CONFLICT_TYPES)
        and summary["conflict_reports_created"] == len(CONFLICT_TYPES)
        and set(summary["conflict_types_represented"]) == set(CONFLICT_TYPES)
        and summary["no_conflict_reports"] == 1
        and summary["root_review_required_reports"] == 10
        and summary["malicious_claims_rejected"] == 8
        and summary["conflictcheck_does_not_decide_truth"] is True
        and summary["conflictcheck_does_not_mutate_drs"] is True
        and summary["root_remains_final_authority"] is True
        and report.authority_safety["lifecycle_records_unchanged"] is True
    )
    assert derived_pass is True
    assert summary["conflictcheck_status"] == "PASS"
    assert summary["ready_for_audit_hash_chain_hardening_v0_1"] is True
    assert summary["production_autonomy_claimed"] is False
