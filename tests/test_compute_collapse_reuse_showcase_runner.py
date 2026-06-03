from __future__ import annotations

from demo.run_compute_collapse_reuse_showcase import COMPUTE_WEIGHTS
from demo.run_compute_collapse_reuse_showcase import (
    collect_compute_collapse_reuse_showcase,
)
from demo.run_compute_collapse_reuse_showcase import (
    run_compute_collapse_reuse_showcase,
)


def _by_scenario(report):
    return {scenario.scenario: scenario for scenario in report.scenarios}


def _expected_units(scenario) -> int:
    flags = {
        "intent_normalization": True,
        "temporal_query": True,
        "drs_precheck": True,
        "candidate_vectors_avf": not scenario.direct_reuse_applied
        and scenario.scenario != "unsafe_records_not_reused",
        "architect_plan": scenario.architect_called,
        "dag_executor": scenario.executor_called or scenario.dag_runner_called,
        "post_vv": scenario.post_vv_called,
        "gt": scenario.gt_called,
        "root_finalization": scenario.root_created_final_output,
        "drs_writeback": scenario.drs_writeback_done,
        "direct_reuse_gate": scenario.direct_reuse_applied
        or scenario.scenario in {"memory_context_only", "unsafe_records_not_reused"},
        "final_render": scenario.root_created_final_output,
    }
    return sum(weight for key, weight in COMPUTE_WEIGHTS.items() if flags[key])


def test_compute_collapse_runner_prints_required_sections_and_scenarios() -> None:
    output = run_compute_collapse_reuse_showcase()

    assert "[COMPUTE COLLAPSE VIA DRS REUSE]" in output
    assert "[INPUT MODULES]" in output
    assert "[SCENARIO TABLE]" in output
    assert "[COMPUTE MODEL]" in output
    assert "[REUSE SAFETY]" in output
    assert "[AUTHORITY / BOUNDARIES]" in output
    assert "[SUMMARY]" in output
    assert "cold_start_full_pipeline" in output
    assert "memory_context_only" in output
    assert "eligible_direct_reuse" in output
    assert "unsafe_records_not_reused" in output


def test_input_modules_are_reported_available() -> None:
    output = run_compute_collapse_reuse_showcase()

    assert "cold_start_benchmark_available: true" in output
    assert "reuse_gate_available: true" in output
    assert "local_drs_available: true" in output
    assert "root_orchestrator_direct_reuse_available: true" in output


def test_cold_start_full_pipeline_does_not_apply_direct_reuse() -> None:
    report = collect_compute_collapse_reuse_showcase()
    scenario = _by_scenario(report)["cold_start_full_pipeline"]

    assert scenario.route == "proof_full_pipeline"
    assert scenario.memory_context_applied is False
    assert scenario.direct_reuse_applied is False
    assert scenario.architect_called is True
    assert scenario.architect_skipped is False
    assert scenario.executor_called is True
    assert scenario.executor_skipped is False
    assert scenario.post_vv_called is True
    assert scenario.gt_called is True
    assert scenario.drs_writeback_done is True
    assert scenario.root_created_final_output is True
    assert scenario.root_final_authority_preserved is True
    assert scenario.no_real_external_actions is True


def test_memory_context_only_is_not_fake_reuse() -> None:
    report = collect_compute_collapse_reuse_showcase()
    scenario = _by_scenario(report)["memory_context_only"]

    assert scenario.route == "context_only"
    assert scenario.memory_context_applied is True
    assert scenario.direct_reuse_applied is False
    assert scenario.architect_called is True
    assert scenario.executor_called is True
    assert scenario.reuse_blocked_reason == "not_eligible"
    assert report.reuse_safety["context_memory_does_not_equal_reuse"] is True


def test_eligible_direct_reuse_applies_and_skips_compute() -> None:
    report = collect_compute_collapse_reuse_showcase()
    scenario = _by_scenario(report)["eligible_direct_reuse"]

    assert scenario.route == "direct_reuse"
    assert scenario.memory_context_applied is True
    assert scenario.direct_reuse_applied is True
    assert scenario.architect_called is False
    assert scenario.architect_skipped is True
    assert scenario.executor_called is False
    assert scenario.executor_skipped is True
    assert scenario.dag_runner_called is False
    assert scenario.dag_runner_skipped is True
    assert scenario.successful_work_source == "eligible_work_record"
    assert scenario.root_created_final_output is True
    assert scenario.root_final_authority_preserved is True


def test_unsafe_records_are_not_reused() -> None:
    report = collect_compute_collapse_reuse_showcase()
    scenario = _by_scenario(report)["unsafe_records_not_reused"]
    safety = report.reuse_safety

    assert scenario.unsafe_reuse_candidates == 0
    assert safety["quarantine_reuse_candidates"] == 0
    assert safety["deadend_reuse_candidates"] == 0
    assert safety["failed_reuse_candidates"] == 0
    assert safety["blocked_reuse_candidates"] == 0
    assert safety["degraded_success_reuse_candidates"] == 0
    assert safety["direct_reuse_unsafe_candidates"] == 0
    assert safety["direct_reuse_requires_eligible_work"] is True
    assert safety["root_gate_required"] is True


def test_authority_boundaries_are_preserved() -> None:
    report = collect_compute_collapse_reuse_showcase()
    authority = report.authority_boundaries

    assert authority["root_created_final_output"] is True
    assert authority["architect_created_final_output"] is False
    assert authority["executor_created_final_output"] is False
    assert authority["gt_committed_final_output"] is False
    assert authority["direct_reuse_bypasses_root"] is False
    assert authority["no_real_external_actions"] is True
    assert authority["no_live_gemini"] is True
    assert authority["no_global_drs"] is True
    assert authority["no_external_drs_network"] is True
    assert authority["production_autonomy_claimed"] is False


def test_compute_model_is_illustrative_not_billing_or_zero_cost() -> None:
    report = collect_compute_collapse_reuse_showcase()
    model = report.compute_model

    assert model["compute_model"] == "illustrative_deterministic_units"
    assert model["absolute_zero_cost_claimed"] is False
    assert model["real_token_billing_measured"] is False
    assert model["cold_start_units"] > 0
    assert model["direct_reuse_units"] > 0
    assert model["direct_reuse_units"] < model["cold_start_units"]
    assert model["memory_context_only_units"] >= model["cold_start_units"]


def test_compute_units_are_computed_from_scenario_flags() -> None:
    report = collect_compute_collapse_reuse_showcase()

    for scenario in report.scenarios:
        assert scenario.compute_units == _expected_units(scenario)


def test_savings_ratio_is_positive_and_computed() -> None:
    report = collect_compute_collapse_reuse_showcase()
    model = report.compute_model

    expected = round(1 - (model["direct_reuse_units"] / model["cold_start_units"]), 3)
    assert model["savings_ratio"] == expected
    assert model["savings_ratio"] > 0
    assert report.summary["savings_ratio_positive"] is True


def test_pass_summary_is_derived_from_scenario_predicates() -> None:
    report = collect_compute_collapse_reuse_showcase()
    by = _by_scenario(report)
    cold = by["cold_start_full_pipeline"]
    memory = by["memory_context_only"]
    direct = by["eligible_direct_reuse"]
    unsafe = by["unsafe_records_not_reused"]
    summary = report.summary

    cold_pass = (
        cold.route == "proof_full_pipeline"
        and not cold.direct_reuse_applied
        and cold.architect_called
        and cold.executor_called
        and cold.post_vv_called
        and cold.gt_called
        and cold.root_created_final_output
    )
    memory_pass = (
        memory.memory_context_applied
        and not memory.direct_reuse_applied
        and memory.architect_called
        and memory.executor_called
        and memory.reuse_blocked_reason == "not_eligible"
    )
    direct_architect_pass = direct.direct_reuse_applied and direct.architect_skipped
    direct_executor_pass = (
        direct.direct_reuse_applied and direct.executor_skipped and direct.dag_runner_skipped
    )
    unsafe_pass = unsafe.unsafe_reuse_candidates == 0

    assert summary["cold_start_full_pipeline_verified"] is cold_pass
    assert summary["memory_context_only_not_fake_reuse"] is memory_pass
    assert summary["eligible_direct_reuse_skips_architect"] is direct_architect_pass
    assert summary["eligible_direct_reuse_skips_executor"] is direct_executor_pass
    assert summary["unsafe_records_not_reused"] is unsafe_pass
    assert summary["compute_collapse_showcase_status"] == (
        "PASS"
        if all(
            [
                cold_pass,
                memory_pass,
                direct_architect_pass,
                direct_executor_pass,
                unsafe_pass,
                summary["direct_reuse_requires_eligibility"],
                summary["root_authority_preserved"],
                not summary["absolute_zero_cost_claimed"],
                summary["savings_ratio_positive"],
                summary["no_real_external_actions"],
            ]
        )
        else "FAIL"
    )


def test_output_contains_required_safety_lines() -> None:
    output = run_compute_collapse_reuse_showcase()

    assert "absolute_zero_cost_claimed: false" in output
    assert "real_token_billing_measured: false" in output
    assert "direct_reuse_requires_eligible_work: true" in output
    assert "context_memory_does_not_equal_reuse: true" in output
    assert "direct_reuse_bypasses_root: false" in output
    assert "gt_committed_final_output: false" in output
    assert "no_real_external_actions: true" in output
    assert "no_live_gemini: true" in output
    assert "no_global_drs: true" in output
    assert "no_external_drs_network: true" in output
    assert "compute_collapse_showcase_status: PASS" in output


def test_output_has_no_sensitive_terms() -> None:
    output = run_compute_collapse_reuse_showcase().lower()

    forbidden = {
        "raw_user_text",
        "api_key",
        "secret",
        "password",
        "private_key",
        "passport_number",
        "card_number",
        "cvv",
        "chain of thought",
    }
    for term in forbidden:
        assert term not in output
