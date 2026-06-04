from __future__ import annotations

from demo.run_root_native_full_canonical_e2e_trace import (
    FIRST_RUN_STAGE_NAMES,
    collect_root_native_full_canonical_e2e_trace,
    run_root_native_full_canonical_e2e_trace,
)


def _stage_by_name(stages):
    return {stage.stage: stage for stage in stages}


def test_runner_output_contains_title_and_sections():
    output = run_root_native_full_canonical_e2e_trace()

    assert "[ROOT-NATIVE FULL CANONICAL E2E TRACE]" in output
    assert "[INPUT TASKS]" in output
    assert "[FIRST RUN CANONICAL PATH]" in output
    assert "[SECOND RUN SEMANTIC REUSE PATH]" in output
    assert "[BRIDGE BETWEEN RUNS]" in output
    assert "[FINAL ARTIFACTS]" in output
    assert "[AUTHORITY / SAFETY]" in output
    assert "[SUMMARY]" in output


def test_first_run_canonical_path_has_nine_stages():
    report = collect_root_native_full_canonical_e2e_trace()

    assert [stage.stage for stage in report.first_run_stages] == FIRST_RUN_STAGE_NAMES
    assert len(report.first_run_stages) == 9
    assert all(stage.status == "PASS" for stage in report.first_run_stages)


def test_second_run_semantic_reuse_path_has_twelve_stages():
    report = collect_root_native_full_canonical_e2e_trace()

    assert len(report.second_run_stages) == 12
    assert all(stage.status == "PASS" for stage in report.second_run_stages)
    assert report.second_run_source.summary["root_native_semantic_reuse_e2e_trace_status"] == "PASS"


def test_semantic_e2e_collector_is_structurally_consumed():
    report = collect_root_native_full_canonical_e2e_trace()

    assert report.second_run_source.selected_path.scenario == "eligible_direct_reuse_candidate"
    assert report.second_run_source.summary["e2e_stages_passed"] == 12
    assert all(
        stage.source == "collect_root_native_semantic_reuse_e2e_trace"
        for stage in report.second_run_stages
    )


def test_first_run_root_authority_is_preserved():
    report = collect_root_native_full_canonical_e2e_trace()
    stage = _stage_by_name(report.first_run_stages)["root_intake"]

    assert stage.status == "PASS"
    assert report.authority_safety["root_authority_preserved_first_run"] is True
    assert report.summary["first_run_root_authority_preserved"] is True


def test_first_run_architect_does_not_answer_user():
    report = collect_root_native_full_canonical_e2e_trace()
    stage = _stage_by_name(report.first_run_stages)["architect_plan_graph"]

    assert stage.status == "PASS"
    assert "architect_does_not_answer_user=true" in stage.key_proof
    assert report.authority_safety["architect_does_not_answer_user"] is True


def test_first_run_executor_does_not_create_final_output():
    report = collect_root_native_full_canonical_e2e_trace()
    stage = _stage_by_name(report.first_run_stages)["dag_executor"]

    assert stage.status == "PASS"
    assert "executor_does_not_create_final_output=true" in stage.key_proof
    assert report.authority_safety["executor_does_not_create_final_output"] is True


def test_post_vv_is_before_gt_and_gt_after_post_vv():
    report = collect_root_native_full_canonical_e2e_trace()
    stages = _stage_by_name(report.first_run_stages)

    assert stages["post_vv"].status == "PASS"
    assert "post_vv_before_gt=true" in stages["post_vv"].key_proof
    assert stages["gt"].status == "PASS"
    assert "gt_after_post_vv=true" in stages["gt"].key_proof


def test_first_run_trace_artifact_is_root_created():
    report = collect_root_native_full_canonical_e2e_trace()
    stage = _stage_by_name(report.first_run_stages)["root_final_trace_artifact"]

    assert stage.status == "PASS"
    assert "root_created_trace_artifact=true" in stage.key_proof
    assert report.final_artifacts["first_run_artifact_created_by"] == "root_orchestrator"


def test_first_run_drs_and_audit_visibility_are_present():
    report = collect_root_native_full_canonical_e2e_trace()
    stage = _stage_by_name(report.first_run_stages)["drs_writeback_audit"]

    assert stage.status == "PASS"
    assert "local_drs_writeback_or_trace_visible=true" in stage.key_proof
    assert "time_envelope_present=true" in stage.key_proof
    assert "provenance_present=true" in stage.key_proof
    assert "audit_visibility_present=true" in stage.key_proof
    assert "no_sensitive_payload=true" in stage.key_proof


def test_second_run_selected_scenario_is_eligible_direct_reuse_candidate():
    report = collect_root_native_full_canonical_e2e_trace()

    assert report.selected_scenario_path.scenario == "eligible_direct_reuse_candidate"
    assert report.selected_scenario_path.record_id == "supportive_work"


def test_second_run_reaches_root_final_controlled_direct_reuse_trace():
    path = collect_root_native_full_canonical_e2e_trace().selected_scenario_path

    assert path.semantic_pipeline_recommendation == "direct_reuse_candidate"
    assert path.root_decision == "root_accepts_direct_reuse_candidate_for_gate_review"
    assert path.reuse_gate_outcome == "gate_review_accepts_candidate_for_root_final_decision"
    assert path.root_final_decision == "root_final_accepts_controlled_direct_reuse_trace"


def test_second_run_trace_final_answer_artifact_is_root_created():
    report = collect_root_native_full_canonical_e2e_trace()

    assert report.final_artifacts["second_run_artifact_kind"] == "trace_level_final_answer_artifact"
    assert report.final_artifacts["second_run_artifact_created_by"] == "root_orchestrator"


def test_bridge_is_deterministic_proof_linkage():
    report = collect_root_native_full_canonical_e2e_trace()
    bridge = report.bridge_between_runs

    assert bridge["bridge_mode"] == "deterministic_proof_linkage"
    assert bridge["reuse_bridge_is_dry_run"] is True
    assert bridge["first_run_created_root_trace_artifact"] is True
    assert bridge["first_run_local_drs_writeback_visible"] is True
    assert bridge["first_run_local_work_record_written_in_proof"] is True
    assert bridge["second_run_retrieved_local_drs_signal"] is True
    assert bridge["second_run_used_semantic_reuse_stack"] is True


def test_production_persistence_and_reuse_are_not_claimed():
    report = collect_root_native_full_canonical_e2e_trace()

    assert report.bridge_between_runs["production_persistence_claimed"] is False
    assert report.bridge_between_runs["production_reuse_claimed"] is False
    assert report.summary["production_persistence_claimed"] is False
    assert report.summary["production_reuse_claimed"] is False


def test_no_production_direct_reuse_final_output_or_work_writeback():
    report = collect_root_native_full_canonical_e2e_trace()

    assert report.authority_safety["production_direct_reuse_executed"] is False
    assert report.authority_safety["production_final_output_created"] is False
    assert report.authority_safety["production_work_record_written"] is False
    assert report.summary["production_direct_reuse_executed"] is False
    assert report.summary["production_final_output_created"] is False
    assert report.summary["production_work_record_written"] is False


def test_no_real_external_actions_live_gemini_or_telegram():
    report = collect_root_native_full_canonical_e2e_trace()
    output = run_root_native_full_canonical_e2e_trace()

    assert report.input_tasks["real_external_action"] is False
    assert report.input_tasks["live_gemini_used"] is False
    assert report.input_tasks["telegram_used"] is False
    assert report.authority_safety["no_real_external_actions"] is True
    assert report.authority_safety["no_live_gemini"] is True
    assert report.authority_safety["no_telegram_actions"] is True
    assert "note: no live Gemini" in output
    assert "note: no Telegram actions" in output


def test_no_global_or_external_drs():
    report = collect_root_native_full_canonical_e2e_trace()
    semantic_summary = report.second_run_source.summary

    assert report.authority_safety["no_global_drs"] is True
    assert report.authority_safety["no_external_drs_network"] is True
    assert report.summary["local_drs_only"] == semantic_summary["local_drs_only"]
    assert (
        report.summary["external_drs_network_implemented"]
        == semantic_summary["external_drs_network_implemented"]
    )
    assert (
        report.summary["global_drs_implemented"]
        == semantic_summary["global_drs_implemented"]
    )


def test_semantic_pipeline_recommends_only_and_reuse_score_is_advisory():
    report = collect_root_native_full_canonical_e2e_trace()

    assert report.authority_safety["semantic_pipeline_recommends_only"] is True
    assert report.authority_safety["reuse_score_advisory_only"] is True
    assert report.second_run_source.authority_safety["context_memory_equals_direct_reuse"] is False
    assert report.second_run_source.authority_safety["high_score_overrides_policy"] is False
    assert report.second_run_source.authority_safety["contradiction_auto_reuse"] is False


def test_reuse_gate_boundary_is_preserved():
    report = collect_root_native_full_canonical_e2e_trace()

    assert report.authority_safety["reuse_gate_boundary_preserved"] is True
    assert report.second_run_source.authority_safety["reuse_gate_guards"] is True


def test_pass_summary_is_derived_from_stages_bridge_and_authority():
    report = collect_root_native_full_canonical_e2e_trace()
    expected_pass = (
        sum(stage.status == "PASS" for stage in report.first_run_stages) == 9
        and sum(stage.status == "PASS" for stage in report.second_run_stages) == 12
        and report.selected_scenario_path.scenario == "eligible_direct_reuse_candidate"
        and report.selected_scenario_path.root_final_decision
        == "root_final_accepts_controlled_direct_reuse_trace"
        and report.bridge_between_runs["first_run_created_root_trace_artifact"]
        and report.bridge_between_runs["first_run_local_drs_writeback_visible"]
        and report.bridge_between_runs["first_run_local_work_record_written_in_proof"]
        and report.bridge_between_runs["bridge_mode"] == "deterministic_proof_linkage"
        and not report.bridge_between_runs["production_persistence_claimed"]
        and not report.bridge_between_runs["production_reuse_claimed"]
        and report.authority_safety["root_authority_preserved_first_run"]
        and report.authority_safety["root_authority_preserved_second_run"]
        and report.authority_safety["reuse_gate_boundary_preserved"]
        and report.authority_safety["semantic_pipeline_recommends_only"]
        and report.authority_safety["reuse_score_advisory_only"]
        and report.authority_safety["architect_does_not_answer_user"]
        and report.authority_safety["executor_does_not_create_final_output"]
        and report.authority_safety["gt_does_not_create_final_output"]
        and not report.authority_safety["production_direct_reuse_executed"]
        and not report.authority_safety["production_final_output_created"]
        and not report.authority_safety["production_work_record_written"]
        and not report.authority_safety["production_external_action_executed"]
        and report.authority_safety["no_real_external_actions"]
        and report.authority_safety["no_live_gemini"]
        and report.authority_safety["no_telegram_actions"]
        and report.authority_safety["no_global_drs"]
        and report.authority_safety["no_external_drs_network"]
        and not report.authority_safety["production_autonomy_claimed"]
    )

    assert report.summary["root_native_full_canonical_e2e_trace_status"] == (
        "PASS" if expected_pass else "FAIL"
    )
