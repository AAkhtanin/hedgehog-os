from __future__ import annotations

from demo.run_root_native_semantic_reuse_e2e_trace import (
    REQUIRED_STAGE_NAMES,
    collect_root_native_semantic_reuse_e2e_trace,
    run_root_native_semantic_reuse_e2e_trace,
)


def _stage_by_name(report):
    return {stage.stage: stage for stage in report.stages}


def test_runner_output_contains_title_and_sections():
    output = run_root_native_semantic_reuse_e2e_trace()

    assert "[ROOT-NATIVE SEMANTIC REUSE E2E TRACE]" in output
    assert "[INPUT TASK]" in output
    assert "[E2E TRACE STAGES]" in output
    assert "[SELECTED SCENARIO PATH]" in output
    assert "[TRACE FINAL ANSWER ARTIFACT]" in output
    assert "[FALLBACK / SAFETY ROUTES]" in output
    assert "[AUTHORITY / SAFETY]" in output
    assert "[SUMMARY]" in output


def test_authority_stack_audit_is_structurally_consumed():
    report = collect_root_native_semantic_reuse_e2e_trace()

    assert (
        report.source_report.summary["semantic_reuse_authority_stack_audit_status"]
        == "PASS"
    )
    assert report.source_report.summary["modules_verified"] == 8
    assert report.source_report.summary["scenarios_verified"] == 8


def test_all_twelve_e2e_stages_are_present_and_pass():
    report = collect_root_native_semantic_reuse_e2e_trace()

    assert [stage.stage for stage in report.stages] == REQUIRED_STAGE_NAMES
    assert len(report.stages) == 12
    assert all(stage.status == "PASS" for stage in report.stages)


def test_temporal_query_stage_is_present():
    stage = _stage_by_name(collect_root_native_semantic_reuse_e2e_trace())[
        "temporal_query"
    ]

    assert stage.status == "PASS"
    assert "temporal_query_created=true" in stage.key_proof
    assert "temporal_query_required_for_drs_retrieval=true" in stage.key_proof


def test_local_drs_retrieval_stage_is_local_only():
    report = collect_root_native_semantic_reuse_e2e_trace()
    stage = _stage_by_name(report)["local_drs_retrieval"]

    assert stage.status == "PASS"
    assert report.summary["local_drs_only"] is True
    assert report.summary["external_drs_network_implemented"] is False
    assert report.summary["global_drs_implemented"] is False


def test_taxonomy_filtering_is_used_and_unsafe_records_are_not_reusable():
    report = collect_root_native_semantic_reuse_e2e_trace()
    stage = _stage_by_name(report)["taxonomy_filtering"]

    assert stage.status == "PASS"
    assert "taxonomy_used_as_filter=true" in stage.key_proof
    assert report.authority_safety["unsafe_reuse_candidates"] == 0


def test_typed_edges_are_signals_and_do_not_override_policy():
    report = collect_root_native_semantic_reuse_e2e_trace()
    stage = _stage_by_name(report)["typed_edge_interpretation"]

    assert stage.status == "PASS"
    assert "typed_edges_used_as_signals=true" in stage.key_proof
    assert "typed_edges_override_policy=false" in stage.key_proof
    assert report.authority_safety["contradiction_auto_reuse"] is False


def test_graph_proximity_is_signal_and_does_not_override_policy():
    stage = _stage_by_name(collect_root_native_semantic_reuse_e2e_trace())[
        "graph_proximity"
    ]

    assert stage.status == "PASS"
    assert "graph_proximity_used_as_signal=true" in stage.key_proof
    assert "graph_proximity_overrides_policy=false" in stage.key_proof


def test_reuse_score_is_advisory_and_does_not_override_policy():
    report = collect_root_native_semantic_reuse_e2e_trace()
    stage = _stage_by_name(report)["reuse_score"]

    assert stage.status == "PASS"
    assert report.authority_safety["reuse_score_advisory_only"] is True
    assert report.authority_safety["high_score_overrides_policy"] is False


def test_semantic_recommendation_does_not_commit_or_bypass_boundaries():
    report = collect_root_native_semantic_reuse_e2e_trace()
    stage = _stage_by_name(report)["semantic_recommendation"]

    assert stage.status == "PASS"
    assert "recommendation_is_action=false" in stage.key_proof
    assert report.source_report.key_proofs["semantic_pipeline_committed_final_output"] is False
    assert report.source_report.key_proofs["semantic_pipeline_bypassed_root"] is False
    assert report.source_report.key_proofs["semantic_pipeline_bypassed_reuse_gate"] is False


def test_root_decision_is_derived_from_pipeline():
    report = collect_root_native_semantic_reuse_e2e_trace()

    assert report.source_report.key_proofs["root_decisions_derived_from_pipeline"] is True
    assert report.authority_safety["root_decides"] is True


def test_reuse_gate_review_is_derived_from_root_decision():
    report = collect_root_native_semantic_reuse_e2e_trace()

    assert report.source_report.key_proofs["gate_rows_derived_from_root_decisions"] is True
    assert report.authority_safety["reuse_gate_guards"] is True


def test_reuse_gate_review_stage_depends_on_gate_no_final_output_and_no_reuse():
    report = collect_root_native_semantic_reuse_e2e_trace()
    stage = _stage_by_name(report)["reuse_gate_review"]
    gate_checks = report.source_report.root_semantic_reuse_gate_trace.authority_checks
    expected_pass = (
        report.source_report.root_semantic_reuse_gate_trace.summary[
            "root_semantic_reuse_gate_trace_status"
        ]
        == "PASS"
        and report.source_report.key_proofs["gate_rows_derived_from_root_decisions"]
        and report.source_report.key_proofs["gate_reviews_performed"] == 1
        and report.source_report.key_proofs["gate_approvals_for_root_final_decision"]
        == 1
        and report.source_report.key_proofs["reuse_gate_boundary_preserved"]
        and gate_checks["gate_does_not_create_final_output"]
        and gate_checks["gate_does_not_execute_direct_reuse"]
        and not report.source_report.key_proofs["production_direct_reuse_executed"]
    )

    assert stage.status == ("PASS" if expected_pass else "FAIL")
    assert gate_checks["gate_does_not_create_final_output"] is True
    assert gate_checks["gate_does_not_execute_direct_reuse"] is True


def test_root_final_decision_is_derived_from_reuse_gate():
    report = collect_root_native_semantic_reuse_e2e_trace()

    assert report.source_report.key_proofs["final_decisions_derived_from_gate_rows"] is True
    assert report.authority_safety["root_final_trace_decides"] is True


def test_selected_scenario_is_eligible_direct_reuse_candidate():
    report = collect_root_native_semantic_reuse_e2e_trace()

    assert report.selected_path.scenario == "eligible_direct_reuse_candidate"
    assert report.selected_path.record_id == "supportive_work"


def test_selected_scenario_path_has_expected_authority_chain_values():
    path = collect_root_native_semantic_reuse_e2e_trace().selected_path

    assert path.semantic_pipeline_recommendation == "direct_reuse_candidate"
    assert path.root_decision == "root_accepts_direct_reuse_candidate_for_gate_review"
    assert path.reuse_gate_outcome == "gate_review_accepts_candidate_for_root_final_decision"
    assert path.root_final_decision == "root_final_accepts_controlled_direct_reuse_trace"
    assert path.production_execution is False
    assert path.unsafe_reuse is False


def test_trace_final_answer_artifact_is_created():
    artifact = collect_root_native_semantic_reuse_e2e_trace().trace_final_answer_artifact

    assert artifact.artifact_kind == "trace_level_final_answer_artifact"
    assert artifact.based_on_scenario == "eligible_direct_reuse_candidate"


def test_trace_artifact_is_created_only_by_root_orchestrator():
    artifact = collect_root_native_semantic_reuse_e2e_trace().trace_final_answer_artifact

    assert artifact.created_by == "root_orchestrator"


def test_trace_artifact_is_not_production_final_output():
    artifact = collect_root_native_semantic_reuse_e2e_trace().trace_final_answer_artifact

    assert artifact.production_final_output is False


def test_production_direct_reuse_is_false():
    report = collect_root_native_semantic_reuse_e2e_trace()

    assert report.authority_safety["production_direct_reuse_executed"] is False
    assert report.summary["production_direct_reuse_executed"] is False


def test_production_work_writeback_is_false():
    report = collect_root_native_semantic_reuse_e2e_trace()

    assert report.trace_final_answer_artifact.production_work_record_written is False
    assert report.summary["production_work_record_written"] is False


def test_unsafe_reuse_candidates_are_zero():
    report = collect_root_native_semantic_reuse_e2e_trace()

    assert report.authority_safety["unsafe_reuse_candidates"] == 0
    assert report.summary["unsafe_reuse_candidates"] == 0


def test_fallback_and_safety_routes_are_visible():
    report = collect_root_native_semantic_reuse_e2e_trace()

    assert all(report.fallback_routes.values())


def test_no_real_external_actions():
    report = collect_root_native_semantic_reuse_e2e_trace()

    assert report.input_task["real_external_action"] is False
    assert report.authority_safety["no_real_external_actions"] is True
    assert report.authority_safety["production_action_executed"] is False


def test_no_live_gemini_or_telegram():
    report = collect_root_native_semantic_reuse_e2e_trace()
    output = run_root_native_semantic_reuse_e2e_trace()

    assert report.input_task["live_gemini_used"] is False
    assert report.input_task["telegram_used"] is False
    assert report.authority_safety["no_live_gemini"] is True
    assert report.authority_safety["no_telegram_actions"] is True
    assert "note: no live Gemini" in output
    assert "note: no Telegram actions" in output


def test_no_global_or_external_drs():
    report = collect_root_native_semantic_reuse_e2e_trace()

    assert report.summary["global_drs_implemented"] is False
    assert report.summary["external_drs_network_implemented"] is False
    assert report.summary["local_drs_only"] is True


def test_production_autonomy_is_not_claimed():
    report = collect_root_native_semantic_reuse_e2e_trace()

    assert report.authority_safety["production_autonomy_claimed"] is False
    assert report.summary["production_autonomy_claimed"] is False


def test_pass_summary_is_derived_from_stages_path_artifact_and_authority():
    report = collect_root_native_semantic_reuse_e2e_trace()

    expected_pass = (
        report.source_report.summary["semantic_reuse_authority_stack_audit_status"]
        == "PASS"
        and sum(stage.status == "PASS" for stage in report.stages) == 12
        and report.selected_path.scenario == "eligible_direct_reuse_candidate"
        and report.selected_path.semantic_pipeline_recommendation
        == "direct_reuse_candidate"
        and report.selected_path.root_decision
        == "root_accepts_direct_reuse_candidate_for_gate_review"
        and report.selected_path.reuse_gate_outcome
        == "gate_review_accepts_candidate_for_root_final_decision"
        and report.selected_path.root_final_decision
        == "root_final_accepts_controlled_direct_reuse_trace"
        and report.trace_final_answer_artifact.created_by == "root_orchestrator"
        and not report.trace_final_answer_artifact.production_final_output
        and not report.authority_safety["production_direct_reuse_executed"]
        and not report.authority_safety["production_work_record_written"]
        and report.authority_safety["unsafe_reuse_candidates"] == 0
        and report.source_report.summary["authority_chain_complete_in_dry_run"]
        and not report.authority_safety["production_autonomy_claimed"]
    )

    assert report.summary["root_native_semantic_reuse_e2e_trace_status"] == (
        "PASS" if expected_pass else "FAIL"
    )
