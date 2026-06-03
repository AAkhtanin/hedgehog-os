from __future__ import annotations

from demo.run_root_semantic_reuse_final_decision_trace import (
    ROOT_FINAL_DECISION_BY_GATE_OUTCOME,
    collect_root_semantic_reuse_final_decision_trace,
    run_root_semantic_reuse_final_decision_trace,
)


def _row_by_scenario(report):
    return {row.scenario: row for row in report.final_decisions}


def test_runner_output_contains_title_and_sections():
    output = run_root_semantic_reuse_final_decision_trace()

    assert "[ROOT SEMANTIC REUSE FINAL DECISION TRACE]" in output
    assert "[INPUT]" in output
    assert "[ROOT FINAL DECISION TABLE]" in output
    assert "[FINAL AUTHORITY CHECKS]" in output
    assert "[SUMMARY]" in output
    assert "root_semantic_reuse_final_decision_trace_status: PASS" in output


def test_gate_trace_is_structurally_consumed():
    report = collect_root_semantic_reuse_final_decision_trace()

    assert report.source_report.summary["root_semantic_reuse_gate_trace_status"] == "PASS"
    assert report.input["root_semantic_reuse_gate_trace_available"] is True
    assert report.input["gate_trace_status"] == "PASS"


def test_eight_gate_rows_are_received():
    report = collect_root_semantic_reuse_final_decision_trace()

    assert report.input["gate_rows_received"] == 8
    assert len(report.final_decisions) == 8


def test_gate_approved_candidate_maps_to_controlled_direct_reuse_trace_accept():
    row = _row_by_scenario(collect_root_semantic_reuse_final_decision_trace())[
        "eligible_direct_reuse_candidate"
    ]

    assert row.gate_outcome == "gate_review_accepts_candidate_for_root_final_decision"
    assert (
        row.root_final_decision
        == "root_final_accepts_controlled_direct_reuse_trace"
    )
    assert row.trace_final_decision_artifact_created is True
    assert row.trace_artifact_created_by == "root_orchestrator"


def test_controlled_direct_reuse_trace_accept_does_not_execute_production_reuse():
    row = _row_by_scenario(collect_root_semantic_reuse_final_decision_trace())[
        "eligible_direct_reuse_candidate"
    ]

    assert row.production_direct_reuse_executed is False
    assert row.production_final_output_created is False
    assert row.production_action_executed is False


def test_trace_final_decision_artifact_is_created_by_root_only():
    report = collect_root_semantic_reuse_final_decision_trace()
    artifacts = [
        row
        for row in report.final_decisions
        if row.trace_final_decision_artifact_created
    ]

    assert len(artifacts) == 1
    assert all(row.trace_artifact_created_by == "root_orchestrator" for row in artifacts)
    assert report.final_authority_checks["trace_artifacts_created_only_by_root"] is True


def test_production_final_output_is_not_created():
    report = collect_root_semantic_reuse_final_decision_trace()

    assert all(
        not row.production_final_output_created for row in report.final_decisions
    )
    assert report.final_authority_checks["production_final_output_created"] is False
    assert report.summary["production_final_output_created"] is False


def test_production_work_record_is_not_written():
    report = collect_root_semantic_reuse_final_decision_trace()

    assert all(
        not row.production_work_record_written for row in report.final_decisions
    )
    assert report.final_authority_checks["production_work_record_written"] is False
    assert report.summary["production_work_record_written"] is False


def test_full_pipeline_fallback_is_preserved():
    row = _row_by_scenario(collect_root_semantic_reuse_final_decision_trace())[
        "context_memory_not_reuse"
    ]

    assert row.gate_outcome == "gate_not_applicable_full_pipeline_fallback"
    assert row.root_final_decision == "root_final_selects_full_pipeline_fallback"
    assert row.full_pipeline_fallback_selected is True
    assert row.production_direct_reuse_executed is False


def test_conflict_check_is_preserved():
    row = _row_by_scenario(collect_root_semantic_reuse_final_decision_trace())[
        "contradiction_needs_conflict_check"
    ]
    report = collect_root_semantic_reuse_final_decision_trace()

    assert row.gate_outcome == "gate_not_applicable_conflict_check_required"
    assert row.root_final_decision == "root_final_requires_conflict_check"
    assert row.conflict_check_required is True
    assert report.final_authority_checks["contradiction_auto_reuse"] is False


def test_policy_block_is_preserved_and_high_score_does_not_override_policy():
    row = _row_by_scenario(collect_root_semantic_reuse_final_decision_trace())[
        "high_score_blocked_by_policy"
    ]
    report = collect_root_semantic_reuse_final_decision_trace()

    assert row.gate_outcome == "gate_not_applicable_policy_blocked"
    assert row.root_final_decision == "root_final_blocks_policy_route"
    assert row.policy_blocked is True
    assert report.final_authority_checks["high_score_overrode_policy"] is False


def test_quarantine_routes_to_quarantine_and_is_not_work_or_reuse():
    row = _row_by_scenario(collect_root_semantic_reuse_final_decision_trace())[
        "quarantine_not_reused"
    ]
    report = collect_root_semantic_reuse_final_decision_trace()

    assert row.root_final_decision == "root_final_routes_to_quarantine"
    assert row.quarantine_route is True
    assert row.production_work_record_written is False
    assert row.production_direct_reuse_executed is False
    assert report.final_authority_checks["quarantine_not_work"] is True


def test_needs_user_is_not_completed_action():
    row = _row_by_scenario(collect_root_semantic_reuse_final_decision_trace())[
        "needs_user_not_completed_action"
    ]
    report = collect_root_semantic_reuse_final_decision_trace()

    assert row.root_final_decision == "root_final_requires_user_input"
    assert row.user_input_required is True
    assert row.production_action_executed is False
    assert report.final_authority_checks["needs_user_not_completed_action"] is True


def test_degraded_is_not_stable_success():
    row = _row_by_scenario(collect_root_semantic_reuse_final_decision_trace())[
        "degraded_not_stable_success"
    ]
    report = collect_root_semantic_reuse_final_decision_trace()

    assert row.root_final_decision == "root_final_marks_degraded_trace"
    assert row.degraded_route is True
    assert row.production_direct_reuse_executed is False
    assert report.final_authority_checks["degraded_not_stable_success"] is True


def test_dead_end_is_not_reused():
    row = _row_by_scenario(collect_root_semantic_reuse_final_decision_trace())[
        "dead_end_not_reused"
    ]
    report = collect_root_semantic_reuse_final_decision_trace()

    assert row.root_final_decision == "root_final_rejects_dead_end"
    assert row.dead_end_rejected is True
    assert row.production_direct_reuse_executed is False
    assert report.final_authority_checks["dead_end_not_reused"] is True


def test_semantic_pipeline_authority_is_not_granted():
    report = collect_root_semantic_reuse_final_decision_trace()

    assert report.final_authority_checks["semantic_pipeline_authority_granted"] is False
    assert report.summary["semantic_pipeline_authority_granted"] is False


def test_reuse_gate_authority_is_not_granted():
    report = collect_root_semantic_reuse_final_decision_trace()

    assert report.final_authority_checks["reuse_gate_authority_granted"] is False
    assert report.summary["reuse_gate_authority_granted"] is False


def test_root_authority_is_preserved():
    report = collect_root_semantic_reuse_final_decision_trace()

    assert report.summary["root_authority_preserved"] is True
    assert report.final_authority_checks["root_received_all_gate_results"] is True
    assert report.final_authority_checks["root_final_boundary_checked_for_all"] is True


def test_unsafe_reuse_candidates_are_zero():
    report = collect_root_semantic_reuse_final_decision_trace()

    assert report.final_authority_checks["unsafe_reuse_candidates"] == 0
    assert report.summary["unsafe_reuse_candidates"] == 0


def test_no_real_external_actions():
    report = collect_root_semantic_reuse_final_decision_trace()

    assert report.final_authority_checks["no_real_external_actions"] is True
    assert report.final_authority_checks["production_action_executed"] is False


def test_no_live_gemini_or_telegram():
    report = collect_root_semantic_reuse_final_decision_trace()
    output = run_root_semantic_reuse_final_decision_trace()

    assert report.final_authority_checks["no_live_gemini"] is True
    assert report.final_authority_checks["no_telegram_actions"] is True
    assert "note: no live Gemini" in output
    assert "note: no Telegram actions" in output


def test_no_global_or_external_drs():
    report = collect_root_semantic_reuse_final_decision_trace()

    assert report.input["global_drs_implemented"] is False
    assert report.input["external_drs_network_implemented"] is False
    assert report.final_authority_checks["no_global_drs"] is True
    assert report.final_authority_checks["no_external_drs_network"] is True


def test_production_autonomy_is_not_claimed():
    report = collect_root_semantic_reuse_final_decision_trace()

    assert report.final_authority_checks["production_autonomy_claimed"] is False
    assert report.summary["production_autonomy_claimed"] is False


def test_pass_summary_is_derived_from_final_decisions_and_authority_checks():
    report = collect_root_semantic_reuse_final_decision_trace()

    derived = all(
        row.root_final_decision
        == ROOT_FINAL_DECISION_BY_GATE_OUTCOME[row.gate_outcome]
        for row in report.final_decisions
    )
    expected_pass = (
        report.source_report.summary["root_semantic_reuse_gate_trace_status"] == "PASS"
        and len(report.final_decisions) == 8
        and derived
        and report.summary["controlled_direct_reuse_trace_accepts"] == 1
        and report.final_authority_checks["gate_trace_consumed"]
        and report.final_authority_checks["root_received_all_gate_results"]
        and report.final_authority_checks["root_final_boundary_checked_for_all"]
        and report.final_authority_checks["trace_artifacts_created_only_by_root"]
        and not report.summary["production_direct_reuse_executed"]
        and not report.summary["production_final_output_created"]
        and not report.summary["production_action_executed"]
        and not report.summary["production_work_record_written"]
        and not report.summary["semantic_pipeline_authority_granted"]
        and not report.summary["reuse_gate_authority_granted"]
        and report.summary["unsafe_reuse_candidates"] == 0
        and report.summary["root_authority_preserved"]
        and report.summary["reuse_gate_boundary_preserved"]
        and not report.summary["production_autonomy_claimed"]
    )
    assert report.summary["root_semantic_reuse_final_decision_trace_status"] == (
        "PASS" if expected_pass else "FAIL"
    )
