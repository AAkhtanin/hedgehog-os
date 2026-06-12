from __future__ import annotations

import pytest

from demo.run_applied_travel_readiness_demo import (
    collect_applied_travel_readiness_demo,
    render_applied_travel_readiness_demo,
)
from demo.run_audit_hash_chain import canonical_hash


@pytest.fixture(scope="module")
def report():
    return collect_applied_travel_readiness_demo()


def _by_id(rows, key):
    return {row[key]: row for row in rows}


def test_runner_title_and_required_sections_exist(report):
    output = render_applied_travel_readiness_demo(report)
    for heading in (
        "[APPLIED TRAVEL READINESS DEMO]",
        "[SOURCE EVIDENCE]",
        "[TRAVEL REQUEST]",
        "[TRAVEL CONDITION MATRIX]",
        "[DECOMPOSITION HINT]",
        "[DRS REUSE]",
        "[PERMISSION BOUNDARY]",
        "[CONFLICTCHECK]",
        "[GT ADVISORY]",
        "[ROOT FINAL]",
        "[AUDIT]",
        "[SUMMARY]",
    ):
        assert heading in output


def test_all_source_statuses_pass(report):
    assert set(report.source_evidence.values()) == {"PASS"}


def test_travel_request_ids_exist(report):
    assert report.travel_request["travel_request_id"] == "TRAVEL-900"
    assert report.travel_request["itinerary_id"] == "ITIN-44"


def test_condition_matrix_has_six_rows_and_four_blockers(report):
    assert len(report.travel_condition_matrix) == 6
    blockers = [row for row in report.travel_condition_matrix if row["blocks_travel"]]
    assert len(blockers) == 4
    assert {row["condition_id"] for row in blockers} == {
        "insurance_certificate",
        "payment_receipt",
        "route_window",
        "user_permission",
    }


def test_passport_and_hotel_do_not_block(report):
    conditions = _by_id(report.travel_condition_matrix, "condition_id")
    assert conditions["passport_validity"]["blocks_travel"] is False
    assert conditions["hotel_confirmation"]["blocks_travel"] is False


def test_drs_reuse_is_bounded_and_not_authority(report):
    assert len(report.travel_drs_reuse_candidates) == 2
    for candidate in report.travel_drs_reuse_candidates:
        assert candidate["reuse_type"] == "bounded_partial_reuse"
        assert candidate["marks_travel_ready"] is False
        assert candidate["submits_external_action"] is False
        assert candidate["semantic_similarity_is_not_authority"] is True
        assert candidate["reuse_score_is_not_root"] is True
        assert candidate["drs_retrieval_is_not_authority"] is True


def test_permission_is_required_and_not_execution(report):
    boundary = report.travel_permission_boundary
    assert boundary["permission_required"] is True
    assert boundary["user_permission_status"] == "not_confirmed"
    assert boundary["permission_is_not_execution"] is True
    assert boundary["completed_action_created"] is False


def test_decomposition_hint_does_not_invoke_fractal_dac(report):
    hint = report.travel_decomposition_hint
    assert hint["decomposition_hint_present"] is True
    assert len(hint["future_bounded_branches"]) == 5
    assert hint["fractal_dac_not_invoked"] is True
    assert hint["child_cells_created"] is False
    assert hint["child_authority_granted"] is False


def test_conflictcheck_detects_contradiction_but_is_not_authority(report):
    conflict = report.travel_conflict_report
    assert conflict["conflict_detected"] is True
    assert conflict["conflictcheck_is_authority"] is False
    assert conflict["root_review_required"] is True


def test_gt_recommends_not_ready_but_cannot_mark_ready_or_execute(report):
    gt = report.travel_gt_advisory
    assert gt["gt_recommendation"] == "not_ready"
    assert gt["gt_is_advisory"] is True
    assert gt["gt_can_mark_ready"] is False
    assert gt["gt_can_execute_action"] is False
    assert gt["gt_can_submit_travel_request"] is False


def test_root_final_is_not_ready_and_needs_user_update(report):
    root = report.travel_root_final
    assert root["root_result"] == "not_ready"
    assert root["safe_secondary_outcome"] == "needs_user_travel_update"
    assert root["root_remains_final_authority"] is True


def test_no_external_actions_persistence_or_drs_writes(report):
    root = report.travel_root_final
    for key in (
        "travel_request_submitted",
        "booking_created",
        "payment_executed",
        "external_action_executed",
        "direct_ready_override",
        "production_persistence",
        "global_drs_write",
        "external_drs_write",
    ):
        assert root[key] is False


def test_no_candidate_or_installed_needle_created(report):
    root = report.travel_root_final
    assert root["protocol_candidate_created"] is False
    assert root["needle_candidate_created"] is False
    assert root["installed_needle_created"] is False


def test_no_external_system_or_deferred_layer_invoked(report):
    root = report.travel_root_final
    for key in (
        "gemini_called",
        "network_called",
        "telegram_used",
        "marennya_invoked",
        "up_invoked",
    ):
        assert root[key] is False


def test_audit_hash_matches_proof_artifact(report):
    assert report.travel_audit_entry["canonical_payload_hash"] == canonical_hash(
        report.travel_proof_artifact
    )
    assert report.travel_audit_entry["audit_chain_decides_truth"] is False


def test_summary_pass_and_ready_for_tests(report):
    summary = report.summary
    assert summary["applied_travel_readiness_demo_status"] == "PASS"
    assert summary["blocking_conditions_count"] == 4
    assert summary["all_blocking_conditions_detected"] is True
    assert summary["fractal_dac_not_invoked"] is True
    assert summary["root_remains_final_authority"] is True
    assert summary["ready_for_applied_travel_readiness_tests"] is True
