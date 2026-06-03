from __future__ import annotations

from demo.run_root_semantic_reuse_decision_trace import (
    ROOT_DECISION_BY_RECOMMENDATION,
)
from demo.run_root_semantic_reuse_decision_trace import (
    collect_root_semantic_reuse_decision_trace,
)
from demo.run_root_semantic_reuse_decision_trace import (
    run_root_semantic_reuse_decision_trace,
)


def _decision_by_scenario(report):
    return {decision.scenario: decision for decision in report.decisions}


def test_runner_output_contains_title_and_sections():
    output = run_root_semantic_reuse_decision_trace()

    assert "[ROOT SEMANTIC REUSE DECISION TRACE]" in output
    assert "[INPUT]" in output
    assert "[ROOT DECISION TABLE]" in output
    assert "[BOUNDARY CHECKS]" in output
    assert "[SUMMARY]" in output
    assert "root_semantic_reuse_decision_trace_status: PASS" in output


def test_semantic_reuse_pipeline_is_structurally_consumed():
    report = collect_root_semantic_reuse_decision_trace()

    assert report.source_report.summary["semantic_reuse_pipeline_status"] == "PASS"
    assert report.input["semantic_reuse_pipeline_available"] is True
    assert report.input["pipeline_status"] == "PASS"


def test_eight_recommendations_are_received():
    report = collect_root_semantic_reuse_decision_trace()

    assert report.input["scenarios_received"] == 8
    assert len(report.decisions) == 8
    assert report.boundary_checks["root_received_all_recommendations"] is True


def test_eligible_direct_reuse_candidate_maps_to_gate_review():
    row = _decision_by_scenario(collect_root_semantic_reuse_decision_trace())[
        "eligible_direct_reuse_candidate"
    ]

    assert row.pipeline_recommendation == "direct_reuse_candidate"
    assert row.root_decision == "root_accepts_direct_reuse_candidate_for_gate_review"
    assert row.boundary_decision == "root_reusegate_review_required"
    assert row.reuse_gate_required is True
    assert row.semantic_pipeline_committed is False
    assert row.production_action_executed is False


def test_direct_reuse_candidate_still_requires_reuse_gate():
    report = collect_root_semantic_reuse_decision_trace()
    row = _decision_by_scenario(report)["eligible_direct_reuse_candidate"]

    assert row.reuse_gate_required is True
    assert row.reuse_gate_bypassed is False
    assert report.boundary_checks["reuse_gate_required_for_direct_reuse_candidate"] is True


def test_direct_reuse_is_not_executed_in_trace():
    report = collect_root_semantic_reuse_decision_trace()

    assert all(not decision.direct_reuse_executed for decision in report.decisions)
    assert report.boundary_checks["direct_reuse_executed_in_trace"] is False
    assert report.summary["direct_reuse_executed_in_trace"] is False


def test_context_memory_maps_to_full_pipeline_fallback():
    row = _decision_by_scenario(collect_root_semantic_reuse_decision_trace())[
        "context_memory_not_reuse"
    ]

    assert row.pipeline_recommendation == "needs_full_pipeline"
    assert row.root_decision == "root_selects_full_pipeline_fallback"
    assert row.boundary_decision == "root_full_pipeline_fallback_required"
    assert row.fallback_required is True
    assert row.direct_reuse_executed is False


def test_context_memory_does_not_equal_direct_reuse():
    report = collect_root_semantic_reuse_decision_trace()

    assert report.boundary_checks["context_memory_equals_direct_reuse"] is False


def test_contradiction_maps_to_conflict_check():
    row = _decision_by_scenario(collect_root_semantic_reuse_decision_trace())[
        "contradiction_needs_conflict_check"
    ]

    assert row.pipeline_recommendation == "needs_conflict_check"
    assert row.root_decision == "root_requires_conflict_check"
    assert row.boundary_decision == "root_conflict_check_required"
    assert row.conflict_check_required is True
    assert row.direct_reuse_executed is False


def test_contradiction_does_not_auto_reuse():
    report = collect_root_semantic_reuse_decision_trace()

    assert report.boundary_checks["contradiction_auto_reuse"] is False


def test_high_score_blocked_route_maps_to_root_block():
    row = _decision_by_scenario(collect_root_semantic_reuse_decision_trace())[
        "high_score_blocked_by_policy"
    ]

    assert row.pipeline_recommendation == "blocked"
    assert row.root_decision == "root_blocks_policy_blocked_route"
    assert row.boundary_decision == "root_policy_block_boundary"
    assert row.direct_reuse_executed is False


def test_high_score_does_not_override_policy():
    report = collect_root_semantic_reuse_decision_trace()

    assert report.boundary_checks["high_score_overrode_policy"] is False
    assert report.boundary_checks["blocked_route_reused"] is False


def test_quarantine_maps_to_quarantine_route_not_work_or_reuse():
    row = _decision_by_scenario(collect_root_semantic_reuse_decision_trace())[
        "quarantine_not_reused"
    ]
    report = collect_root_semantic_reuse_decision_trace()

    assert row.root_decision == "root_routes_to_quarantine"
    assert row.boundary_decision == "root_quarantine_route_boundary"
    assert row.quarantine_route is True
    assert row.direct_reuse_executed is False
    assert report.boundary_checks["quarantine_reused"] is False


def test_needs_user_maps_to_user_input_not_completed_action():
    row = _decision_by_scenario(collect_root_semantic_reuse_decision_trace())[
        "needs_user_not_completed_action"
    ]
    report = collect_root_semantic_reuse_decision_trace()

    assert row.root_decision == "root_requires_user_input"
    assert row.boundary_decision == "root_user_input_boundary"
    assert row.user_input_required is True
    assert row.production_action_executed is False
    assert report.boundary_checks["needs_user_completed_as_action"] is False


def test_degraded_maps_to_degraded_trace_not_success():
    row = _decision_by_scenario(collect_root_semantic_reuse_decision_trace())[
        "degraded_not_stable_success"
    ]
    report = collect_root_semantic_reuse_decision_trace()

    assert row.root_decision == "root_marks_degraded_trace"
    assert row.boundary_decision == "root_degraded_trace_boundary"
    assert row.degraded_route is True
    assert row.direct_reuse_executed is False
    assert report.boundary_checks["degraded_trace_reused"] is False


def test_dead_end_maps_to_rejection_not_reuse():
    row = _decision_by_scenario(collect_root_semantic_reuse_decision_trace())[
        "dead_end_not_reused"
    ]
    report = collect_root_semantic_reuse_decision_trace()

    assert row.root_decision == "root_rejects_dead_end"
    assert row.boundary_decision == "root_dead_end_rejection_boundary"
    assert row.dead_end_rejected is True
    assert row.direct_reuse_executed is False
    assert report.boundary_checks["dead_end_reused"] is False


def test_semantic_pipeline_does_not_commit_final_output():
    report = collect_root_semantic_reuse_decision_trace()

    assert all(not decision.semantic_pipeline_committed for decision in report.decisions)
    assert report.boundary_checks["semantic_pipeline_committed_final_output"] is False
    assert report.summary["semantic_pipeline_authority_granted"] is False


def test_root_decision_trace_does_not_create_production_final_output():
    report = collect_root_semantic_reuse_decision_trace()

    assert all(not decision.root_created_final_output for decision in report.decisions)
    assert all(
        not decision.production_final_output_created for decision in report.decisions
    )
    assert report.summary["production_final_output_created"] is False


def test_root_boundary_is_preserved():
    report = collect_root_semantic_reuse_decision_trace()

    assert report.boundary_checks["root_received_all_recommendations"] is True
    assert report.boundary_checks["root_boundary_checked_for_all"] is True
    assert report.boundary_checks["semantic_pipeline_bypassed_root"] is False
    assert report.summary["root_boundary_preserved"] is True


def test_reuse_gate_boundary_is_preserved():
    report = collect_root_semantic_reuse_decision_trace()

    assert report.boundary_checks["reuse_gate_bypassed"] is False
    assert report.boundary_checks["semantic_pipeline_bypassed_reuse_gate"] is False
    assert report.summary["reuse_gate_boundary_preserved"] is True


def test_reuse_gate_required_only_for_direct_reuse_candidate_review():
    report = collect_root_semantic_reuse_decision_trace()

    for decision in report.decisions:
        if decision.pipeline_recommendation == "direct_reuse_candidate":
            assert decision.reuse_gate_required is True
            assert decision.boundary_decision == "root_reusegate_review_required"
        else:
            assert decision.reuse_gate_required is False
            assert decision.boundary_decision != "root_reusegate_review_required"


def test_semantic_pipeline_is_not_granted_authority():
    report = collect_root_semantic_reuse_decision_trace()

    assert report.summary["semantic_pipeline_authority_granted"] is False
    assert all(not decision.semantic_pipeline_committed for decision in report.decisions)


def test_unsafe_reuse_candidates_are_zero():
    report = collect_root_semantic_reuse_decision_trace()

    assert report.boundary_checks["unsafe_reuse_candidates"] == 0
    assert report.summary["unsafe_reuse_candidates"] == 0


def test_no_real_external_actions():
    report = collect_root_semantic_reuse_decision_trace()

    assert report.boundary_checks["no_real_external_actions"] is True
    assert report.boundary_checks["production_action_executed"] is False


def test_no_live_gemini_or_telegram():
    report = collect_root_semantic_reuse_decision_trace()
    output = run_root_semantic_reuse_decision_trace()

    assert report.boundary_checks["no_live_gemini"] is True
    assert report.boundary_checks["no_telegram_actions"] is True
    assert "note: no live Gemini" in output
    assert "note: no Telegram actions" in output


def test_no_global_or_external_drs():
    report = collect_root_semantic_reuse_decision_trace()

    assert report.input["global_drs_implemented"] is False
    assert report.input["external_drs_network_implemented"] is False
    assert report.boundary_checks["no_global_drs"] is True
    assert report.boundary_checks["no_external_drs_network"] is True


def test_production_autonomy_is_not_claimed():
    report = collect_root_semantic_reuse_decision_trace()

    assert report.boundary_checks["production_autonomy_claimed"] is False
    assert report.summary["production_autonomy_claimed"] is False


def test_pass_summary_is_derived_from_decisions_and_boundary_facts():
    report = collect_root_semantic_reuse_decision_trace()

    expected_pass = (
        len(report.decisions) == 8
        and all(
            decision.root_decision
            == ROOT_DECISION_BY_RECOMMENDATION[decision.pipeline_recommendation]
            for decision in report.decisions
        )
        and report.summary["direct_reuse_candidates_sent_to_reuse_gate_review"] >= 1
        and report.summary["full_pipeline_fallbacks_selected"] >= 1
        and report.summary["conflict_check_required_cases"] >= 1
        and report.summary["policy_blocked_cases"] >= 1
        and report.summary["quarantine_routes"] >= 1
        and report.summary["needs_user_routes"] >= 1
        and report.summary["degraded_routes"] >= 1
        and report.summary["dead_end_rejections"] >= 1
        and report.summary["root_boundary_preserved"]
        and report.summary["reuse_gate_boundary_preserved"]
        and not report.summary["semantic_pipeline_authority_granted"]
        and not report.summary["direct_reuse_executed_in_trace"]
        and not report.summary["production_final_output_created"]
        and report.summary["unsafe_reuse_candidates"] == 0
    )
    assert report.summary["root_semantic_reuse_decision_trace_status"] == (
        "PASS" if expected_pass else "FAIL"
    )
