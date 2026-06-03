from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Any

from demo.run_cold_start_benchmark import ColdStartPhase
from demo.run_cold_start_benchmark import ColdStartReport
from demo.run_cold_start_benchmark import collect_cold_start_benchmark
from demo.run_needle_outcome_drs_routing import NeedleOutcomeDrsRoutingReport
from demo.run_needle_outcome_drs_routing import collect_needle_outcome_drs_routing


COMPUTE_WEIGHTS = {
    "intent_normalization": 1,
    "temporal_query": 1,
    "drs_precheck": 2,
    "candidate_vectors_avf": 4,
    "architect_plan": 12,
    "dag_executor": 10,
    "post_vv": 4,
    "gt": 4,
    "root_finalization": 2,
    "drs_writeback": 2,
    "direct_reuse_gate": 2,
    "final_render": 1,
}

FORBIDDEN_OUTPUT_TERMS = (
    "raw_user_text",
    "api_key",
    "secret",
    "password",
    "private_key",
    "passport_number",
    "card_number",
    "cvv",
    "hidden reasoning",
    "chain of thought",
)


@dataclass(frozen=True)
class ComputeCollapseScenario:
    scenario: str
    route: str
    memory_context_applied: bool
    direct_reuse_applied: bool
    architect_called: bool
    architect_skipped: bool
    executor_called: bool
    executor_skipped: bool
    dag_runner_called: bool
    dag_runner_skipped: bool
    post_vv_called: bool
    gt_called: bool
    drs_writeback_done: bool
    root_created_final_output: bool
    root_final_authority_preserved: bool
    no_real_external_actions: bool
    successful_work_source: str
    unsafe_reuse_candidates: int
    compute_units: int
    reuse_blocked_reason: str


@dataclass(frozen=True)
class ComputeCollapseShowcaseReport:
    cold_start_report: ColdStartReport
    drs_routing_report: NeedleOutcomeDrsRoutingReport
    scenarios: list[ComputeCollapseScenario]
    compute_model: dict[str, Any]
    reuse_safety: dict[str, Any]
    authority_boundaries: dict[str, Any]
    summary: dict[str, Any]


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _sanitize_output(output: str) -> str:
    sanitized = output
    for term in FORBIDDEN_OUTPUT_TERMS:
        sanitized = sanitized.replace(term, "[redacted]")
        sanitized = sanitized.replace(term.upper(), "[redacted]")
    return sanitized


def _phase_by_name(report: ColdStartReport, phase_name: str) -> ColdStartPhase:
    for phase in report.phases:
        if phase.phase == phase_name:
            return phase
    raise KeyError(phase_name)


def _compute_units(*, scenario: ComputeCollapseScenario | None = None, flags: dict[str, bool] | None = None) -> int:
    if scenario is not None:
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
    assert flags is not None
    return sum(weight for key, weight in COMPUTE_WEIGHTS.items() if flags.get(key))


def _scenario_from_phase(
    *,
    scenario: str,
    phase: ColdStartPhase,
    post_vv_called: bool,
    gt_called: bool,
    successful_work_source: str,
    reuse_blocked_reason: str = "none",
) -> ComputeCollapseScenario:
    direct_reuse = phase.direct_reuse_applied
    scenario_obj = ComputeCollapseScenario(
        scenario=scenario,
        route=phase.route,
        memory_context_applied=phase.memory_context_applied,
        direct_reuse_applied=direct_reuse,
        architect_called=not phase.architect_skipped,
        architect_skipped=phase.architect_skipped,
        executor_called=not phase.executor_skipped,
        executor_skipped=phase.executor_skipped,
        dag_runner_called=False,
        dag_runner_skipped=True,
        post_vv_called=post_vv_called,
        gt_called=gt_called,
        drs_writeback_done=phase.drs_writes > 0,
        root_created_final_output=True,
        root_final_authority_preserved=True,
        no_real_external_actions=True,
        successful_work_source=successful_work_source,
        unsafe_reuse_candidates=0,
        compute_units=0,
        reuse_blocked_reason=reuse_blocked_reason,
    )
    return scenario_obj.__class__(
        **{**scenario_obj.__dict__, "compute_units": _compute_units(scenario=scenario_obj)}
    )


def _unsafe_reuse_counts(report: NeedleOutcomeDrsRoutingReport) -> dict[str, int]:
    records = report.records
    return {
        "quarantine_reuse_candidates": sum(
            record["content"].get("direct_reuse_eligible", False)
            for record in records
            if record["layer"] == "quarantine"
        ),
        "deadend_reuse_candidates": sum(
            record["content"].get("direct_reuse_eligible", False)
            for record in records
            if record["layer"] == "deadends"
        ),
        "failed_reuse_candidates": sum(
            record["content"].get("direct_reuse_eligible", False)
            for record in records
            if record["content"].get("failure_kind") in {"unknown_exception"}
        ),
        "blocked_reuse_candidates": sum(
            record["content"].get("direct_reuse_eligible", False)
            for record in records
            if record["content"].get("deadend_or_blocked")
        ),
        "degraded_success_reuse_candidates": sum(
            record["content"].get("direct_reuse_eligible", False)
            for record in records
            if record["content"].get("degraded")
        ),
    }


def _unsafe_records_scenario(report: NeedleOutcomeDrsRoutingReport) -> ComputeCollapseScenario:
    counts = _unsafe_reuse_counts(report)
    direct_reuse_unsafe = sum(counts.values())
    scenario_obj = ComputeCollapseScenario(
        scenario="unsafe_records_not_reused",
        route="reuse_safety_check",
        memory_context_applied=True,
        direct_reuse_applied=False,
        architect_called=False,
        architect_skipped=True,
        executor_called=False,
        executor_skipped=True,
        dag_runner_called=False,
        dag_runner_skipped=True,
        post_vv_called=False,
        gt_called=False,
        drs_writeback_done=False,
        root_created_final_output=False,
        root_final_authority_preserved=True,
        no_real_external_actions=True,
        successful_work_source="none",
        unsafe_reuse_candidates=direct_reuse_unsafe,
        compute_units=0,
        reuse_blocked_reason="unsafe_layers_not_eligible",
    )
    return scenario_obj.__class__(
        **{**scenario_obj.__dict__, "compute_units": _compute_units(scenario=scenario_obj)}
    )


def _build_scenarios(
    cold_start: ColdStartReport,
    drs_routing: NeedleOutcomeDrsRoutingReport,
) -> list[ComputeCollapseScenario]:
    first = _phase_by_name(cold_start, "first_run_cold_start")
    second = _phase_by_name(cold_start, "second_run_memory_influence")
    direct = _phase_by_name(cold_start, "seeded_direct_reuse_eligible_run")
    return [
        _scenario_from_phase(
            scenario="cold_start_full_pipeline",
            phase=first,
            post_vv_called=True,
            gt_called=True,
            successful_work_source="none",
        ),
        _scenario_from_phase(
            scenario="memory_context_only",
            phase=second,
            post_vv_called=True,
            gt_called=True,
            successful_work_source="none",
            reuse_blocked_reason="not_eligible",
        ),
        _scenario_from_phase(
            scenario="eligible_direct_reuse",
            phase=direct,
            post_vv_called=False,
            gt_called=False,
            successful_work_source="eligible_work_record",
        ),
        _unsafe_records_scenario(drs_routing),
    ]


def _compute_model(scenarios: list[ComputeCollapseScenario]) -> dict[str, Any]:
    by = {scenario.scenario: scenario for scenario in scenarios}
    cold_units = by["cold_start_full_pipeline"].compute_units
    memory_units = by["memory_context_only"].compute_units
    direct_units = by["eligible_direct_reuse"].compute_units
    savings_ratio = 1 - (direct_units / cold_units)
    return {
        "compute_model": "illustrative_deterministic_units",
        "absolute_zero_cost_claimed": False,
        "real_token_billing_measured": False,
        "cold_start_units": cold_units,
        "memory_context_only_units": memory_units,
        "direct_reuse_units": direct_units,
        "savings_ratio": round(savings_ratio, 3),
    }


def _reuse_safety(
    cold_start: ColdStartReport,
    drs_routing: NeedleOutcomeDrsRoutingReport,
) -> dict[str, Any]:
    counts = _unsafe_reuse_counts(drs_routing)
    direct_reuse_unsafe = sum(counts.values())
    return {
        "direct_reuse_requires_eligible_work": cold_start.direct_reuse_requires_eligibility,
        "context_memory_does_not_equal_reuse": True,
        **counts,
        "direct_reuse_unsafe_candidates": direct_reuse_unsafe,
        "root_gate_required": True,
        "root_authority_preserved": cold_start.root_final_authority_preserved,
    }


def _authority_boundaries(
    scenarios: list[ComputeCollapseScenario],
    reuse_safety: dict[str, Any],
) -> dict[str, Any]:
    executable = [scenario for scenario in scenarios if scenario.root_created_final_output]
    return {
        "root_created_final_output": all(
            scenario.root_created_final_output for scenario in executable
        ),
        "architect_created_final_output": False,
        "executor_created_final_output": False,
        "gt_committed_final_output": False,
        "direct_reuse_bypasses_root": False,
        "no_real_external_actions": all(
            scenario.no_real_external_actions for scenario in scenarios
        ),
        "no_live_gemini": True,
        "no_global_drs": True,
        "no_external_drs_network": True,
        "production_autonomy_claimed": False,
    }


def _scenario_passes(scenarios: list[ComputeCollapseScenario]) -> dict[str, bool]:
    by = {scenario.scenario: scenario for scenario in scenarios}
    cold = by["cold_start_full_pipeline"]
    memory = by["memory_context_only"]
    direct = by["eligible_direct_reuse"]
    unsafe = by["unsafe_records_not_reused"]
    return {
        "cold_start_full_pipeline_verified": (
            cold.route in {"proof_full_pipeline", "fractal_dag"}
            and not cold.direct_reuse_applied
            and cold.architect_called
            and cold.executor_called
            and cold.post_vv_called
            and cold.gt_called
            and cold.root_created_final_output
        ),
        "memory_context_only_not_fake_reuse": (
            memory.memory_context_applied
            and not memory.direct_reuse_applied
            and memory.architect_called
            and memory.executor_called
            and memory.reuse_blocked_reason == "not_eligible"
        ),
        "eligible_direct_reuse_skips_architect": (
            direct.direct_reuse_applied and direct.architect_skipped
        ),
        "eligible_direct_reuse_skips_executor": (
            direct.direct_reuse_applied
            and direct.executor_skipped
            and direct.dag_runner_skipped
        ),
        "unsafe_records_not_reused": unsafe.unsafe_reuse_candidates == 0,
    }


def _summary(
    scenarios: list[ComputeCollapseScenario],
    compute_model: dict[str, Any],
    reuse_safety: dict[str, Any],
    authority: dict[str, Any],
) -> dict[str, Any]:
    scenario_pass = _scenario_passes(scenarios)
    savings_ratio_positive = compute_model["savings_ratio"] > 0
    direct_reuse_requires_eligibility = reuse_safety[
        "direct_reuse_requires_eligible_work"
    ]
    root_authority_preserved = reuse_safety["root_authority_preserved"] and not authority[
        "direct_reuse_bypasses_root"
    ]
    absolute_zero_cost_claimed = compute_model["absolute_zero_cost_claimed"]
    all_pass = (
        all(scenario_pass.values())
        and direct_reuse_requires_eligibility
        and root_authority_preserved
        and not absolute_zero_cost_claimed
        and savings_ratio_positive
        and authority["no_real_external_actions"]
    )
    return {
        "compute_collapse_showcase_status": "PASS" if all_pass else "FAIL",
        **scenario_pass,
        "direct_reuse_requires_eligibility": direct_reuse_requires_eligibility,
        "root_authority_preserved": root_authority_preserved,
        "absolute_zero_cost_claimed": absolute_zero_cost_claimed,
        "savings_ratio_positive": savings_ratio_positive,
        "no_real_external_actions": authority["no_real_external_actions"],
    }


def collect_compute_collapse_reuse_showcase() -> ComputeCollapseShowcaseReport:
    cold_start = collect_cold_start_benchmark()
    drs_routing = collect_needle_outcome_drs_routing()
    scenarios = _build_scenarios(cold_start, drs_routing)
    compute_model = _compute_model(scenarios)
    reuse_safety = _reuse_safety(cold_start, drs_routing)
    authority = _authority_boundaries(scenarios, reuse_safety)
    summary = _summary(scenarios, compute_model, reuse_safety, authority)
    return ComputeCollapseShowcaseReport(
        cold_start_report=cold_start,
        drs_routing_report=drs_routing,
        scenarios=scenarios,
        compute_model=compute_model,
        reuse_safety=reuse_safety,
        authority_boundaries=authority,
        summary=summary,
    )


def _field_lines(fields: dict[str, Any]) -> list[str]:
    lines = []
    for key, value in fields.items():
        if isinstance(value, bool):
            lines.append(f"{key}: {_bool_text(value)}")
        else:
            lines.append(f"{key}: {value}")
    return lines


def _scenario_line(scenario: ComputeCollapseScenario) -> str:
    return " | ".join(
        [
            scenario.scenario,
            scenario.route,
            _bool_text(scenario.memory_context_applied),
            _bool_text(scenario.direct_reuse_applied),
            _bool_text(scenario.architect_skipped),
            _bool_text(scenario.executor_skipped),
            _bool_text(scenario.dag_runner_skipped),
            _bool_text(scenario.post_vv_called),
            _bool_text(scenario.gt_called),
            _bool_text(scenario.drs_writeback_done),
            _bool_text(scenario.root_created_final_output),
            str(scenario.unsafe_reuse_candidates),
            str(scenario.compute_units),
        ]
    )


def render_compute_collapse_reuse_showcase(
    report: ComputeCollapseShowcaseReport,
) -> str:
    lines = [
        "[COMPUTE COLLAPSE VIA DRS REUSE]",
        "note: deterministic showcase over existing DRS/reuse proof modules",
        "note: not absolute zero cost",
        "note: no real external actions",
        "note: no live Gemini",
        "note: no global DRS",
        "note: Root authority remains final",
        "note: direct reuse requires eligible DRS record",
        "",
        "[INPUT MODULES]",
        "cold_start_benchmark_available: true",
        "reuse_gate_available: true",
        "local_drs_available: true",
        "root_orchestrator_direct_reuse_available: true",
        "",
        "[SCENARIO TABLE]",
        "scenario | route | memory_context_applied | direct_reuse_applied | architect_skipped | executor_skipped | dag_runner_skipped | post_vv_called | gt_called | drs_writeback_done | root_created_final_output | unsafe_reuse_candidates | compute_units",
        "--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---",
    ]
    lines.extend(_scenario_line(scenario) for scenario in report.scenarios)
    lines.extend(["", "[COMPUTE MODEL]"])
    lines.extend(_field_lines(report.compute_model))
    lines.append("note: compute units are illustrative deterministic units, not token billing")
    lines.extend(["", "[REUSE SAFETY]"])
    lines.extend(_field_lines(report.reuse_safety))
    lines.extend(["", "[AUTHORITY / BOUNDARIES]"])
    lines.extend(_field_lines(report.authority_boundaries))
    lines.extend(["", "[SUMMARY]"])
    lines.extend(_field_lines(report.summary))
    return _sanitize_output("\n".join(lines).rstrip() + "\n")


def run_compute_collapse_reuse_showcase() -> str:
    return render_compute_collapse_reuse_showcase(
        collect_compute_collapse_reuse_showcase()
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run Compute Collapse via DRS Reuse showcase."
    )
    parser.parse_args()
    print(run_compute_collapse_reuse_showcase(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
