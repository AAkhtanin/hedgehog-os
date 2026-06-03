from __future__ import annotations

from demo.run_semantic_reuse_authority_stack_audit import (
    STACK_FLOW_STAGES,
    collect_semantic_reuse_authority_stack_audit,
    run_semantic_reuse_authority_stack_audit,
)


EXPECTED_MODULES = {
    "drs_graph_proximity",
    "drs_layer_taxonomy",
    "typed_drs_lineage_edges",
    "reuse_score",
    "semantic_reuse_pipeline",
    "root_semantic_reuse_decision_trace",
    "root_semantic_reuse_gate_trace",
    "root_semantic_reuse_final_decision_trace",
}

EXPECTED_SCENARIOS = {
    "eligible_direct_reuse_candidate",
    "context_memory_not_reuse",
    "contradiction_needs_conflict_check",
    "high_score_blocked_by_policy",
    "quarantine_not_reused",
    "needs_user_not_completed_action",
    "degraded_not_stable_success",
    "dead_end_not_reused",
}


def test_runner_output_contains_title_and_sections():
    output = run_semantic_reuse_authority_stack_audit()

    assert "[SEMANTIC REUSE AUTHORITY STACK AUDIT]" in output
    assert "[INPUT MODULES]" in output
    assert "[STACK FLOW]" in output
    assert "[KEY PROOFS]" in output
    assert "[SCENARIO SUMMARY]" in output
    assert "[AUTHORITY SUMMARY]" in output
    assert "[SUMMARY]" in output
    assert "semantic_reuse_authority_stack_audit_status: PASS" in output


def test_all_eight_modules_are_consumed():
    report = collect_semantic_reuse_authority_stack_audit()

    assert {module.module for module in report.input_modules} == EXPECTED_MODULES
    assert all(module.available for module in report.input_modules)
    assert len(report.input_modules) == 8


def test_all_consumed_modules_have_pass_status():
    report = collect_semantic_reuse_authority_stack_audit()

    assert all(module.status == "PASS" for module in report.input_modules)


def test_stack_flow_contains_all_eight_stages():
    report = collect_semantic_reuse_authority_stack_audit()

    assert [stage.stage for stage in report.stack_flow] == STACK_FLOW_STAGES
    assert all(stage.status == "PASS" for stage in report.stack_flow)


def test_scenario_summary_contains_all_eight_scenarios():
    report = collect_semantic_reuse_authority_stack_audit()

    assert {row.scenario for row in report.scenario_summary} == EXPECTED_SCENARIOS
    assert len(report.scenario_summary) == 8


def test_reuse_score_remains_advisory():
    report = collect_semantic_reuse_authority_stack_audit()

    assert report.key_proofs["reuse_score_is_advisory"] is True
    assert report.authority_summary["reuse_score_role"] == "advisory_ranking_only"


def test_semantic_pipeline_does_not_commit():
    report = collect_semantic_reuse_authority_stack_audit()

    assert report.key_proofs["semantic_pipeline_committed_final_output"] is False
    assert report.authority_summary["semantic_pipeline_role"] == "recommends_only"


def test_root_decision_derives_from_semantic_pipeline():
    report = collect_semantic_reuse_authority_stack_audit()

    assert report.key_proofs["root_decisions_derived_from_pipeline"] is True
    assert report.authority_summary["root_decision_role"] == "maps_recommendations"


def test_reuse_gate_derives_from_root_decision():
    report = collect_semantic_reuse_authority_stack_audit()

    assert report.key_proofs["gate_rows_derived_from_root_decisions"] is True
    assert (
        report.authority_summary["reuse_gate_role"]
        == "reviews_direct_reuse_candidate_only"
    )


def test_root_final_decision_derives_from_reuse_gate():
    report = collect_semantic_reuse_authority_stack_audit()

    assert report.key_proofs["final_decisions_derived_from_gate_rows"] is True
    assert (
        report.authority_summary["root_final_role"]
        == "creates_trace_level_final_decision_artifact_only"
    )


def test_exactly_one_gate_review_is_performed():
    report = collect_semantic_reuse_authority_stack_audit()

    assert report.key_proofs["gate_reviews_performed"] == 1


def test_exactly_one_controlled_direct_reuse_trace_accept_exists():
    report = collect_semantic_reuse_authority_stack_audit()

    assert report.key_proofs["controlled_direct_reuse_trace_accepts"] == 1


def test_trace_final_artifact_is_created_only_by_root():
    report = collect_semantic_reuse_authority_stack_audit()

    assert report.key_proofs["trace_final_decision_artifacts_created"] == 1
    assert report.key_proofs["trace_artifacts_created_only_by_root"] is True


def test_production_direct_reuse_is_false():
    report = collect_semantic_reuse_authority_stack_audit()

    assert report.key_proofs["production_direct_reuse_executed"] is False
    assert report.authority_summary["production_execution"] is False


def test_production_final_output_is_false():
    report = collect_semantic_reuse_authority_stack_audit()

    assert report.key_proofs["production_final_output_created"] is False
    assert report.authority_summary["production_final_output"] is False


def test_production_work_writeback_is_false():
    report = collect_semantic_reuse_authority_stack_audit()

    assert report.key_proofs["production_work_record_written"] is False
    assert report.authority_summary["production_work_writeback"] is False


def test_unsafe_reuse_candidates_are_zero():
    report = collect_semantic_reuse_authority_stack_audit()

    assert report.key_proofs["unsafe_reuse_candidates"] == 0
    assert all(not row.unsafe_reuse for row in report.scenario_summary)


def test_no_live_gemini_no_telegram_no_real_external_actions():
    report = collect_semantic_reuse_authority_stack_audit()
    output = run_semantic_reuse_authority_stack_audit()

    assert report.key_proofs["production_action_executed"] is False
    assert "note: no real external actions" in output
    assert "note: no live Gemini" in output
    assert "note: no Telegram actions" in output


def test_no_global_or_external_drs():
    report = collect_semantic_reuse_authority_stack_audit()

    assert report.summary["global_drs_implemented"] is False
    assert report.summary["external_drs_network_implemented"] is False
    assert report.summary["local_drs_only"] is True


def test_aggregate_pass_is_derived_from_module_and_scenario_facts():
    report = collect_semantic_reuse_authority_stack_audit()

    modules_pass = all(module.status == "PASS" for module in report.input_modules)
    flow_pass = all(stage.status == "PASS" for stage in report.stack_flow)
    scenarios_pass = (
        len(report.scenario_summary) == 8
        and all(not row.production_execution for row in report.scenario_summary)
        and all(not row.unsafe_reuse for row in report.scenario_summary)
    )
    key_pass = (
        report.key_proofs["root_decisions_derived_from_pipeline"]
        and report.key_proofs["gate_rows_derived_from_root_decisions"]
        and report.key_proofs["final_decisions_derived_from_gate_rows"]
        and report.key_proofs["gate_reviews_performed"] == 1
        and report.key_proofs["controlled_direct_reuse_trace_accepts"] == 1
        and report.key_proofs["trace_artifacts_created_only_by_root"]
        and report.key_proofs["unsafe_reuse_candidates"] == 0
        and not report.key_proofs["production_direct_reuse_executed"]
        and not report.key_proofs["production_final_output_created"]
        and not report.key_proofs["production_work_record_written"]
        and not report.key_proofs["semantic_pipeline_authority_granted"]
        and not report.key_proofs["reuse_gate_authority_granted"]
        and not report.key_proofs["production_autonomy_claimed"]
    )
    expected_status = "PASS" if modules_pass and flow_pass and scenarios_pass and key_pass else "FAIL"

    assert report.summary["semantic_reuse_authority_stack_audit_status"] == expected_status
