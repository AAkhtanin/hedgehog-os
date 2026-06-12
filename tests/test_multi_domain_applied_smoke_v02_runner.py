from __future__ import annotations

import pytest

from demo.run_audit_hash_chain import canonical_hash
from demo.run_multi_domain_applied_smoke_v02 import (
    collect_multi_domain_applied_smoke_v02,
    render_multi_domain_applied_smoke_v02,
)


@pytest.fixture(scope="module")
def report():
    return collect_multi_domain_applied_smoke_v02()


def _by_id(rows, key):
    return {row[key]: row for row in rows}


def test_runner_title_and_required_sections_exist(report):
    output = render_multi_domain_applied_smoke_v02(report)
    for heading in (
        "[MULTI-DOMAIN APPLIED SMOKE v0.2]",
        "[SOURCE EVIDENCE]",
        "[DOMAIN MATRIX]",
        "[CROSS-DOMAIN REUSE]",
        "[DOMAIN ISOLATION]",
        "[CONFLICTCHECK]",
        "[GT ADVISORY]",
        "[ROOT FINAL MATRIX]",
        "[AUDIT]",
        "[SUMMARY]",
    ):
        assert heading in output


def test_all_source_statuses_pass(report):
    assert set(report.source_evidence.values()) == {"PASS"}


def test_exactly_three_domains_observed_and_not_ready(report):
    assert len(report.domain_matrix) == 3
    assert all(row["root_result"] == "not_ready" for row in report.domain_matrix)


def test_each_domain_preserves_its_own_blocker(report):
    domains = _by_id(report.domain_matrix, "domain_id")
    assert domains["warehouse_domain"]["primary_blocker"] == "water_filter_short_by_2"
    assert domains["certificate_domain"]["primary_blocker"] == (
        "insurance_expired_payment_missing"
    )
    assert domains["travel_domain"]["primary_blocker"] == (
        "insurance_expired_payment_missing_route_uncertain_permission_not_confirmed"
    )


def test_certificate_to_travel_reuse_is_bounded_not_ready(report):
    reuse = report.cross_domain_reuse_observations
    assert reuse["certificate_to_travel_document_reuse_observed"] is True
    assert reuse["certificate_to_travel_direct_ready_allowed"] is False
    assert reuse["cross_domain_reuse_requires_root_review"] is True


def test_drs_reuse_and_similarity_are_not_authority(report):
    reuse = report.cross_domain_reuse_observations
    assert reuse["semantic_similarity_is_not_authority"] is True
    assert reuse["reuse_score_is_not_root"] is True
    assert reuse["drs_retrieval_is_not_authority"] is True


def test_all_six_domain_isolation_rows_block_direct_authority(report):
    assert len(report.domain_isolation_matrix) == 6
    assert all(
        row["direct_authority"] is False
        and row["root_review_required"] is True
        and row["child_authority_granted"] is False
        for row in report.domain_isolation_matrix
    )


def test_conflictcheck_detects_cross_domain_ready_contradiction(report):
    conflict = report.conflict_matrix
    assert conflict["conflict_detected"] is True
    assert conflict["conflictcheck_is_authority"] is False
    assert conflict["root_review_required"] is True


def test_gt_cannot_merge_authority_mark_ready_or_execute(report):
    gt = report.gt_advisory
    assert gt["gt_recommendation"] == "multi_domain_not_ready"
    assert gt["gt_is_advisory"] is True
    assert gt["gt_can_merge_domain_authority"] is False
    assert gt["gt_can_mark_any_domain_ready"] is False
    assert gt["gt_can_execute_action"] is False


def test_root_final_matrix_preserves_root_authority(report):
    assert len(report.root_final_matrix) == 3
    assert all(
        row["root_result"] == "not_ready"
        and row["root_remains_final_authority"] is True
        and row["direct_ready_override"] is False
        for row in report.root_final_matrix
    )


def test_no_external_actions_or_persistence(report):
    for row in report.root_final_matrix:
        assert row["completed_external_action_created"] is False
        assert row["production_persistence"] is False
        assert row["global_drs_write"] is False
        assert row["external_drs_write"] is False
    summary = report.summary
    assert summary["no_completed_dispatch"] is True
    assert summary["no_completed_certificate_submission"] is True
    assert summary["no_travel_request_submitted"] is True
    assert summary["no_booking_created"] is True
    assert summary["no_payment_executed"] is True


def test_no_candidate_or_installed_needle_created(report):
    for row in report.root_final_matrix:
        assert row["protocol_candidate_created"] is False
        assert row["needle_candidate_created"] is False
        assert row["installed_needle_created"] is False


def test_fractal_dac_dual_coupling_and_children_not_invoked(report):
    summary = report.summary
    assert summary["fractal_dac_not_invoked"] is True
    assert summary["dual_fractal_coupling_not_invoked"] is True
    assert summary["child_cells_created"] is False
    assert summary["child_authority_granted"] is False


def test_no_external_system_or_deferred_layer_invoked(report):
    summary = report.summary
    for key in (
        "gemini_called",
        "network_called",
        "telegram_used",
        "marennya_invoked",
        "up_invoked",
    ):
        assert summary[key] is False


def test_audit_hash_matches_proof_artifact(report):
    assert report.multi_domain_audit_entry["canonical_payload_hash"] == canonical_hash(
        report.multi_domain_proof_artifact
    )
    assert report.multi_domain_audit_entry["audit_chain_decides_truth"] is False


def test_summary_pass_and_ready_for_tests(report):
    summary = report.summary
    assert summary["multi_domain_applied_smoke_v02_status"] == "PASS"
    assert summary["domains_observed"] == 3
    assert summary["all_domain_specific_blockers_preserved"] is True
    assert summary["domain_isolation_preserved"] is True
    assert summary["root_remains_final_authority"] is True
    assert summary["ready_for_multi_domain_applied_smoke_v02_tests"] is True
