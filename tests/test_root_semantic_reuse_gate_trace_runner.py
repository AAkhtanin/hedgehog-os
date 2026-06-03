from __future__ import annotations

from demo.run_root_semantic_reuse_gate_trace import GATE_OUTCOME_BY_ROOT_DECISION
from demo.run_root_semantic_reuse_gate_trace import (
    collect_root_semantic_reuse_gate_trace,
)
from demo.run_root_semantic_reuse_gate_trace import run_root_semantic_reuse_gate_trace


def _row_by_scenario(report):
    return {row.scenario: row for row in report.rows}


def test_runner_output_contains_title_and_sections():
    output = run_root_semantic_reuse_gate_trace()

    assert "[ROOT SEMANTIC REUSE GATE TRACE]" in output
    assert "[INPUT]" in output
    assert "[REUSEGATE TRACE TABLE]" in output
    assert "[GATE / AUTHORITY CHECKS]" in output
    assert "[SUMMARY]" in output
    assert "root_semantic_reuse_gate_trace_status: PASS" in output


def test_root_decision_trace_is_structurally_consumed():
    report = collect_root_semantic_reuse_gate_trace()

    assert report.source_report.summary["root_semantic_reuse_decision_trace_status"] == "PASS"
    assert report.input["root_semantic_reuse_decision_trace_available"] is True
    assert report.input["decision_trace_status"] == "PASS"


def test_eight_root_decisions_are_received():
    report = collect_root_semantic_reuse_gate_trace()

    assert report.input["decisions_received"] == 8
    assert len(report.rows) == 8


def test_direct_reuse_candidate_goes_to_gate_review():
    row = _row_by_scenario(collect_root_semantic_reuse_gate_trace())[
        "eligible_direct_reuse_candidate"
    ]

    assert row.gate_applicable is True
    assert row.gate_review_performed is True
    assert row.gate_outcome == "gate_review_accepts_candidate_for_root_final_decision"
    assert row.gate_approved_for_root_final_decision is True


def test_gate_review_is_performed_only_for_direct_reuse_candidate():
    report = collect_root_semantic_reuse_gate_trace()

    reviewed = [row for row in report.rows if row.gate_review_performed]
    assert len(reviewed) == 1
    assert reviewed[0].scenario == "eligible_direct_reuse_candidate"
    assert report.authority_checks["gate_review_only_for_direct_reuse_candidate"] is True


def test_gate_approval_returns_to_root_not_production_execution():
    row = _row_by_scenario(collect_root_semantic_reuse_gate_trace())[
        "eligible_direct_reuse_candidate"
    ]

    assert row.gate_approved_for_root_final_decision is True
    assert row.root_final_decision_required is True
    assert row.direct_reuse_executed is False
    assert row.root_created_production_final_output is False


def test_gate_does_not_create_final_output():
    report = collect_root_semantic_reuse_gate_trace()

    assert all(not row.reuse_gate_created_final_output for row in report.rows)
    assert report.authority_checks["gate_does_not_create_final_output"] is True
    assert report.summary["gate_did_not_commit_final_output"] is True


def test_gate_does_not_execute_direct_reuse():
    report = collect_root_semantic_reuse_gate_trace()

    assert all(not row.direct_reuse_executed for row in report.rows)
    assert report.authority_checks["gate_does_not_execute_direct_reuse"] is True
    assert report.summary["gate_did_not_execute_direct_reuse"] is True


def test_full_pipeline_fallback_remains_non_gate_route():
    row = _row_by_scenario(collect_root_semantic_reuse_gate_trace())[
        "context_memory_not_reuse"
    ]

    assert row.gate_applicable is False
    assert row.gate_outcome == "gate_not_applicable_full_pipeline_fallback"
    assert row.full_pipeline_fallback_required is True


def test_conflict_check_remains_non_gate_route():
    row = _row_by_scenario(collect_root_semantic_reuse_gate_trace())[
        "contradiction_needs_conflict_check"
    ]

    assert row.gate_applicable is False
    assert row.gate_outcome == "gate_not_applicable_conflict_check_required"
    assert row.conflict_check_required is True


def test_policy_blocked_remains_blocked_and_high_score_does_not_override_policy():
    row = _row_by_scenario(collect_root_semantic_reuse_gate_trace())[
        "high_score_blocked_by_policy"
    ]
    report = collect_root_semantic_reuse_gate_trace()

    assert row.gate_applicable is False
    assert row.gate_outcome == "gate_not_applicable_policy_blocked"
    assert row.policy_blocked is True
    assert report.authority_checks["high_score_overrode_policy"] is False


def test_quarantine_is_not_reused():
    row = _row_by_scenario(collect_root_semantic_reuse_gate_trace())[
        "quarantine_not_reused"
    ]
    report = collect_root_semantic_reuse_gate_trace()

    assert row.gate_outcome == "gate_not_applicable_quarantine"
    assert row.quarantine_route is True
    assert row.direct_reuse_executed is False
    assert report.authority_checks["quarantine_not_reused"] is True


def test_needs_user_is_not_completed_action():
    row = _row_by_scenario(collect_root_semantic_reuse_gate_trace())[
        "needs_user_not_completed_action"
    ]
    report = collect_root_semantic_reuse_gate_trace()

    assert row.gate_outcome == "gate_not_applicable_needs_user"
    assert row.user_input_required is True
    assert row.production_action_executed is False
    assert report.authority_checks["needs_user_not_completed_action"] is True


def test_degraded_is_not_stable_success():
    row = _row_by_scenario(collect_root_semantic_reuse_gate_trace())[
        "degraded_not_stable_success"
    ]
    report = collect_root_semantic_reuse_gate_trace()

    assert row.gate_outcome == "gate_not_applicable_degraded"
    assert row.degraded_route is True
    assert row.direct_reuse_executed is False
    assert report.authority_checks["degraded_not_stable_success"] is True


def test_dead_end_is_not_reused():
    row = _row_by_scenario(collect_root_semantic_reuse_gate_trace())[
        "dead_end_not_reused"
    ]
    report = collect_root_semantic_reuse_gate_trace()

    assert row.gate_outcome == "gate_not_applicable_dead_end"
    assert row.dead_end_rejected is True
    assert row.direct_reuse_executed is False
    assert report.authority_checks["dead_end_not_reused"] is True


def test_semantic_pipeline_authority_is_not_granted():
    report = collect_root_semantic_reuse_gate_trace()

    assert report.authority_checks["semantic_pipeline_authority_granted"] is False
    assert report.summary["semantic_pipeline_authority_granted"] is False


def test_root_authority_is_preserved():
    report = collect_root_semantic_reuse_gate_trace()

    assert report.summary["root_authority_preserved"] is True
    assert report.summary["root_final_decision_required_for_gate_approval"] is True


def test_reuse_gate_boundary_is_preserved():
    report = collect_root_semantic_reuse_gate_trace()

    assert report.summary["reuse_gate_boundary_preserved"] is True
    assert report.authority_checks["gate_review_performed_for_direct_reuse_candidate"] is True


def test_unsafe_reuse_candidates_are_zero():
    report = collect_root_semantic_reuse_gate_trace()

    assert report.authority_checks["unsafe_reuse_candidates"] == 0
    assert report.summary["unsafe_reuse_candidates"] == 0


def test_no_real_external_actions():
    report = collect_root_semantic_reuse_gate_trace()

    assert report.authority_checks["no_real_external_actions"] is True
    assert report.authority_checks["production_action_executed"] is False


def test_no_live_gemini_or_telegram():
    report = collect_root_semantic_reuse_gate_trace()
    output = run_root_semantic_reuse_gate_trace()

    assert report.authority_checks["no_live_gemini"] is True
    assert report.authority_checks["no_telegram_actions"] is True
    assert "note: no live Gemini" in output
    assert "note: no Telegram actions" in output


def test_no_global_or_external_drs():
    report = collect_root_semantic_reuse_gate_trace()

    assert report.input["global_drs_implemented"] is False
    assert report.input["external_drs_network_implemented"] is False
    assert report.authority_checks["no_global_drs"] is True
    assert report.authority_checks["no_external_drs_network"] is True


def test_production_autonomy_is_not_claimed():
    report = collect_root_semantic_reuse_gate_trace()

    assert report.authority_checks["production_autonomy_claimed"] is False
    assert report.summary["production_autonomy_claimed"] is False


def test_pass_summary_is_derived_from_gate_rows_and_authority_checks():
    report = collect_root_semantic_reuse_gate_trace()

    gate_reviews = [row for row in report.rows if row.gate_review_performed]
    approvals = [row for row in report.rows if row.gate_approved_for_root_final_decision]
    expected_pass = (
        len(report.rows) == 8
        and all(
            row.gate_outcome == GATE_OUTCOME_BY_ROOT_DECISION[row.root_decision]
            for row in report.rows
        )
        and len(gate_reviews) == 1
        and len(approvals) == 1
        and report.summary["non_applicable_gate_routes"] == 7
        and report.authority_checks["gate_does_not_create_final_output"]
        and report.authority_checks["gate_does_not_execute_direct_reuse"]
        and report.summary["unsafe_reuse_candidates"] == 0
        and report.summary["root_authority_preserved"]
        and report.summary["reuse_gate_boundary_preserved"]
        and not report.summary["semantic_pipeline_authority_granted"]
        and not report.summary["production_final_output_created"]
        and not report.summary["production_autonomy_claimed"]
    )
    assert report.summary["root_semantic_reuse_gate_trace_status"] == (
        "PASS" if expected_pass else "FAIL"
    )
