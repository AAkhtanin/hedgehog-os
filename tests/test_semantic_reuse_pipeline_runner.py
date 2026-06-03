from __future__ import annotations

from demo.run_semantic_reuse_pipeline import REQUIRED_STAGE_NAMES
from demo.run_semantic_reuse_pipeline import _boundary_stage_passed
from demo.run_semantic_reuse_pipeline import collect_semantic_reuse_pipeline
from demo.run_semantic_reuse_pipeline import run_semantic_reuse_pipeline


def _scenario_by_name(report):
    return {scenario.scenario: scenario for scenario in report.scenarios}


def _stage_by_name(report):
    return {stage.stage: stage for stage in report.stages}


def test_runner_output_contains_required_sections():
    output = run_semantic_reuse_pipeline()

    assert "[SEMANTIC REUSE PIPELINE]" in output
    assert "[INPUT MODULES]" in output
    assert "[PIPELINE STAGES]" in output
    assert "[SCENARIO TABLE]" in output
    assert "[BOUNDARY / SAFETY]" in output
    assert "[SUMMARY]" in output
    assert "semantic_reuse_pipeline_status: PASS" in output


def test_reuse_score_report_is_structurally_consumed():
    report = collect_semantic_reuse_pipeline()

    assert report.source_report.summary["reuse_score_status"] == "PASS"
    assert len(report.source_report.candidates) == 10
    assert report.summary["candidates_scored"] == len(report.source_report.candidates)


def test_source_typed_edge_report_is_present():
    report = collect_semantic_reuse_pipeline()

    assert report.source_report.source_report.summary["typed_drs_lineage_edges_status"] == "PASS"
    assert len(report.source_report.source_report.records) == 10
    assert report.input_modules["typed_drs_lineage_edges_available"] is True


def test_all_pipeline_stages_are_present_and_pass():
    report = collect_semantic_reuse_pipeline()
    stages = _stage_by_name(report)

    assert list(stages) == REQUIRED_STAGE_NAMES
    assert all(stage.status == "PASS" for stage in report.stages)
    assert report.summary["pipeline_stages_passed"] == 6


def test_taxonomy_filtering_detects_unsafe_records_without_reusing_them():
    report = collect_semantic_reuse_pipeline()
    stages = _stage_by_name(report)

    assert stages["taxonomy_filtering"].status == "PASS"
    assert "unsafe_records_filtered=true" in stages["taxonomy_filtering"].key_proof_field
    assert report.boundary_safety["unsafe_direct_reuse_candidates"] == 0
    assert report.boundary_safety["quarantine_direct_reuse_candidates"] == 0
    assert report.boundary_safety["deadend_direct_reuse_candidates"] == 0


def test_typed_edge_interpretation_does_not_override_policy():
    report = collect_semantic_reuse_pipeline()

    assert _stage_by_name(report)["typed_edge_interpretation"].status == "PASS"
    assert report.boundary_safety["typed_edges_override_policy"] is False
    assert report.source_report.source_report.summary["edge_types_present"] == 8
    assert report.source_report.source_report.summary["typed_edges_are_signals_only"] is True
    assert (
        report.source_report.source_report.summary[
            "contradiction_target_auto_blocked"
        ]
        is False
    )


def test_graph_proximity_is_query_time_signal_and_not_policy_override():
    report = collect_semantic_reuse_pipeline()

    assert _stage_by_name(report)["graph_proximity"].status == "PASS"
    assert (
        report.source_report.source_report.summary[
            "graph_distance_computed_at_query_time"
        ]
        is True
    )
    assert (
        report.source_report.source_report.summary["static_hops_stored_in_records"]
        is False
    )
    assert report.boundary_safety["graph_proximity_overrides_policy"] is False


def test_reuse_score_is_advisory_and_not_policy_override():
    report = collect_semantic_reuse_pipeline()

    assert _stage_by_name(report)["reuse_score"].status == "PASS"
    assert report.boundary_safety["reuse_score_is_advisory"] is True
    assert report.boundary_safety["high_score_overrides_policy"] is False


def test_eligible_direct_reuse_candidate_is_recommended_not_committed():
    row = _scenario_by_name(collect_semantic_reuse_pipeline())[
        "eligible_direct_reuse_candidate"
    ]

    assert row.taxonomy_kind == "work_candidate"
    assert row.direct_reuse_allowed_after_policy is True
    assert row.pipeline_recommendation == "direct_reuse_candidate"
    assert row.boundary_decision == "root_reusegate_required"
    assert row.committed_by_pipeline is False


def test_context_memory_does_not_equal_direct_reuse():
    row = _scenario_by_name(collect_semantic_reuse_pipeline())[
        "context_memory_not_reuse"
    ]

    assert row.record_id == "unrelated_fresh_work"
    assert row.graph_proximity == 0.0
    assert row.pipeline_recommendation == "needs_full_pipeline"
    assert row.boundary_decision == "root_full_pipeline_fallback_required"
    assert "weak_or_unrelated_context" in row.explanation


def test_contradiction_case_becomes_needs_conflict_check():
    row = _scenario_by_name(collect_semantic_reuse_pipeline())[
        "contradiction_needs_conflict_check"
    ]

    assert row.record_id == "child_work"
    assert row.reuse_score_recommendation == "needs_conflict_check"
    assert row.pipeline_recommendation == "needs_conflict_check"
    assert row.direct_reuse_allowed_after_policy is False


def test_high_score_blocked_trace_remains_blocked():
    row = _scenario_by_name(collect_semantic_reuse_pipeline())[
        "high_score_blocked_by_policy"
    ]

    assert row.record_id == "nearby_blocked_trace"
    assert row.raw_reuse_score > 0.50
    assert row.taxonomy_kind == "blocked_trace"
    assert row.policy_allowed is False
    assert row.direct_reuse_allowed_after_policy is False
    assert row.pipeline_recommendation == "blocked"


def test_quarantine_is_not_reused():
    row = _scenario_by_name(collect_semantic_reuse_pipeline())["quarantine_not_reused"]

    assert row.taxonomy_kind == "quarantine"
    assert row.direct_reuse_allowed_after_policy is False
    assert row.pipeline_recommendation == "quarantine"
    assert row.unsafe_reuse_candidate is False


def test_needs_user_is_not_completed_action():
    row = _scenario_by_name(collect_semantic_reuse_pipeline())[
        "needs_user_not_completed_action"
    ]

    assert row.taxonomy_kind == "needs_user_trace"
    assert row.pipeline_recommendation == "needs_user"
    assert row.direct_reuse_allowed_after_policy is False
    assert row.committed_by_pipeline is False


def test_degraded_is_not_stable_success():
    row = _scenario_by_name(collect_semantic_reuse_pipeline())[
        "degraded_not_stable_success"
    ]

    assert row.taxonomy_kind == "degraded_trace"
    assert row.pipeline_recommendation == "degraded"
    assert row.direct_reuse_allowed_after_policy is False


def test_dead_end_is_not_reused():
    row = _scenario_by_name(collect_semantic_reuse_pipeline())["dead_end_not_reused"]

    assert row.taxonomy_kind == "dead_end"
    assert row.pipeline_recommendation == "dead_end"
    assert row.direct_reuse_allowed_after_policy is False


def test_semantic_pipeline_does_not_commit_final_output():
    report = collect_semantic_reuse_pipeline()

    assert report.boundary_safety["semantic_pipeline_committed_final_output"] is False
    assert report.summary["pipeline_committed_final_output"] is False
    assert all(not scenario.committed_by_pipeline for scenario in report.scenarios)


def test_semantic_pipeline_does_not_bypass_root():
    report = collect_semantic_reuse_pipeline()

    assert report.boundary_safety["semantic_pipeline_bypassed_root"] is False
    assert report.summary["root_boundary_preserved"] is True
    assert all(scenario.root_boundary_required for scenario in report.scenarios)


def test_semantic_pipeline_does_not_bypass_reuse_gate():
    report = collect_semantic_reuse_pipeline()

    assert report.boundary_safety["semantic_pipeline_bypassed_reuse_gate"] is False
    assert report.summary["reuse_gate_boundary_preserved"] is True
    assert all(scenario.reuse_gate_boundary_required for scenario in report.scenarios)


def test_reuse_gate_root_boundary_stage_is_derived_from_boundary_safety():
    report = collect_semantic_reuse_pipeline()
    stage = _stage_by_name(report)["reuse_gate_root_boundary"]

    expected_pass = _boundary_stage_passed(report.boundary_safety)
    assert stage.status == ("PASS" if expected_pass else "FAIL")
    assert expected_pass is True


def test_boundary_stage_would_fail_if_required_boundary_predicate_were_false():
    report = collect_semantic_reuse_pipeline()

    broken = dict(report.boundary_safety)
    broken["semantic_pipeline_bypassed_root"] = True
    assert _boundary_stage_passed(broken) is False

    broken = dict(report.boundary_safety)
    broken["reuse_gate_boundary_required"] = False
    assert _boundary_stage_passed(broken) is False


def test_unsafe_direct_reuse_candidates_are_zero():
    report = collect_semantic_reuse_pipeline()

    assert report.boundary_safety["unsafe_direct_reuse_candidates"] == 0
    assert report.summary["unsafe_reuse_candidates"] == 0


def test_no_real_external_actions_live_gemini_or_telegram():
    report = collect_semantic_reuse_pipeline()
    output = run_semantic_reuse_pipeline()

    assert report.boundary_safety["no_real_external_actions"] is True
    assert report.boundary_safety["no_live_gemini"] is True
    assert report.boundary_safety["no_telegram_actions"] is True
    assert "note: no real external actions" in output
    assert "note: no live Gemini" in output
    assert "note: no Telegram actions" in output


def test_no_global_or_external_drs():
    report = collect_semantic_reuse_pipeline()

    assert report.boundary_safety["no_global_drs"] is True
    assert report.boundary_safety["no_external_drs_network"] is True
    assert report.summary["global_drs_implemented"] is False
    assert report.summary["external_drs_network_implemented"] is False


def test_production_autonomy_is_not_claimed():
    report = collect_semantic_reuse_pipeline()

    assert report.boundary_safety["production_autonomy_claimed"] is False
    assert report.summary["production_autonomy_claimed"] is False


def test_pass_summary_is_derived_from_stage_and_scenario_facts():
    report = collect_semantic_reuse_pipeline()

    stages_pass = all(stage.status == "PASS" for stage in report.stages)
    direct = [
        row for row in report.scenarios if row.pipeline_recommendation == "direct_reuse_candidate"
    ]
    fallback = [
        row for row in report.scenarios if row.pipeline_recommendation == "needs_full_pipeline"
    ]
    conflict = [
        row for row in report.scenarios if row.pipeline_recommendation == "needs_conflict_check"
    ]
    blocked = [row for row in report.scenarios if row.pipeline_recommendation == "blocked"]

    expected_pass = (
        stages_pass
        and len(direct) >= 1
        and len(fallback) >= 1
        and len(conflict) >= 1
        and len(blocked) >= 1
        and report.summary["unsafe_reuse_candidates"] == 0
        and report.summary["root_boundary_preserved"]
        and report.summary["reuse_gate_boundary_preserved"]
        and not report.summary["pipeline_committed_final_output"]
    )
    assert report.summary["semantic_reuse_pipeline_status"] == (
        "PASS" if expected_pass else "FAIL"
    )
