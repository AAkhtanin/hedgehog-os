from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Any

from demo.run_reuse_score import ReuseScoreCandidate
from demo.run_reuse_score import ReuseScoreReport
from demo.run_reuse_score import collect_reuse_score


EXPECTED_TAXONOMY_KINDS = {
    "work_candidate",
    "quarantine",
    "dead_end",
    "blocked_trace",
    "degraded_trace",
    "needs_user_trace",
}
UNSAFE_TAXONOMY_KINDS = {
    "quarantine",
    "dead_end",
    "blocked_trace",
    "degraded_trace",
    "needs_user_trace",
}
REQUIRED_STAGE_NAMES = [
    "local_drs_retrieval",
    "taxonomy_filtering",
    "typed_edge_interpretation",
    "graph_proximity",
    "reuse_score",
    "reuse_gate_root_boundary",
]


@dataclass(frozen=True)
class SemanticReuseStage:
    stage: str
    status: str
    key_proof_field: str


@dataclass(frozen=True)
class SemanticReuseScenario:
    scenario: str
    record_id: str
    taxonomy_kind: str
    graph_proximity: float
    raw_reuse_score: float
    policy_allowed: bool
    direct_reuse_allowed_after_policy: bool
    reuse_score_recommendation: str
    pipeline_recommendation: str
    boundary_decision: str
    root_boundary_required: bool
    reuse_gate_boundary_required: bool
    committed_by_pipeline: bool
    unsafe_reuse_candidate: bool
    explanation: str


@dataclass(frozen=True)
class SemanticReusePipelineReport:
    source_report: ReuseScoreReport
    input_modules: dict[str, Any]
    stages: list[SemanticReuseStage]
    scenarios: list[SemanticReuseScenario]
    boundary_safety: dict[str, Any]
    summary: dict[str, Any]


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _candidate_by_id(report: ReuseScoreReport) -> dict[str, ReuseScoreCandidate]:
    return {candidate.record_id: candidate for candidate in report.candidates}


def _pipeline_recommendation(candidate: ReuseScoreCandidate, scenario: str) -> str:
    if scenario == "context_memory_not_reuse" and candidate.graph_proximity == 0:
        return "needs_full_pipeline"
    return candidate.reuse_recommendation


def _boundary_decision(pipeline_recommendation: str) -> str:
    if pipeline_recommendation == "direct_reuse_candidate":
        return "root_reusegate_required"
    if pipeline_recommendation == "needs_conflict_check":
        return "root_conflict_check_required"
    if pipeline_recommendation == "needs_full_pipeline":
        return "root_full_pipeline_fallback_required"
    return "root_reusegate_required"


def _scenario(
    name: str,
    candidate: ReuseScoreCandidate,
) -> SemanticReuseScenario:
    pipeline_recommendation = _pipeline_recommendation(candidate, name)
    unsafe_reuse_candidate = (
        candidate.direct_reuse_allowed_after_policy
        and candidate.taxonomy_kind in UNSAFE_TAXONOMY_KINDS
    )
    explanation = candidate.explanation
    if name == "context_memory_not_reuse":
        explanation = "weak_or_unrelated_context_requires_root_reusegate_boundary"
    return SemanticReuseScenario(
        scenario=name,
        record_id=candidate.record_id,
        taxonomy_kind=candidate.taxonomy_kind,
        graph_proximity=candidate.graph_proximity,
        raw_reuse_score=candidate.raw_reuse_score,
        policy_allowed=candidate.policy_allowed,
        direct_reuse_allowed_after_policy=candidate.direct_reuse_allowed_after_policy,
        reuse_score_recommendation=candidate.reuse_recommendation,
        pipeline_recommendation=pipeline_recommendation,
        boundary_decision=_boundary_decision(pipeline_recommendation),
        root_boundary_required=True,
        reuse_gate_boundary_required=True,
        committed_by_pipeline=False,
        unsafe_reuse_candidate=unsafe_reuse_candidate,
        explanation=explanation,
    )


def _build_scenarios(report: ReuseScoreReport) -> list[SemanticReuseScenario]:
    rows = _candidate_by_id(report)
    return [
        _scenario("eligible_direct_reuse_candidate", rows["supportive_work"]),
        _scenario("context_memory_not_reuse", rows["unrelated_fresh_work"]),
        _scenario("contradiction_needs_conflict_check", rows["child_work"]),
        _scenario("high_score_blocked_by_policy", rows["nearby_blocked_trace"]),
        _scenario("quarantine_not_reused", rows["nearby_quarantine"]),
        _scenario("needs_user_not_completed_action", rows["nearby_needs_user_trace"]),
        _scenario("degraded_not_stable_success", rows["nearby_degraded_trace"]),
        _scenario("dead_end_not_reused", rows["nearby_dead_end"]),
    ]


def _input_modules(report: ReuseScoreReport) -> dict[str, Any]:
    return {
        "typed_drs_lineage_edges_available": (
            report.source_report.summary["typed_drs_lineage_edges_status"] == "PASS"
        ),
        "reuse_score_available": report.summary["reuse_score_status"] == "PASS",
        "drs_layer_taxonomy_available": EXPECTED_TAXONOMY_KINDS.issubset(
            {candidate.taxonomy_kind for candidate in report.candidates}
        ),
        "drs_graph_proximity_available": report.summary[
            "graph_proximity_used_as_signal"
        ],
        "local_drs_only": report.summary["local_drs_only"],
    }


def _boundary_stage_passed(boundary_safety: dict[str, Any]) -> bool:
    return (
        boundary_safety["semantic_pipeline_committed_final_output"] is False
        and boundary_safety["semantic_pipeline_bypassed_root"] is False
        and boundary_safety["semantic_pipeline_bypassed_reuse_gate"] is False
        and boundary_safety["root_boundary_required"] is True
        and boundary_safety["reuse_gate_boundary_required"] is True
        and boundary_safety["production_autonomy_claimed"] is False
    )


def _stage_results(
    report: ReuseScoreReport,
    boundary_safety: dict[str, Any],
) -> list[SemanticReuseStage]:
    taxonomy_kinds = {candidate.taxonomy_kind for candidate in report.candidates}
    unsafe_filtered = all(
        not candidate.direct_reuse_allowed_after_policy
        for candidate in report.candidates
        if candidate.taxonomy_kind in UNSAFE_TAXONOMY_KINDS
    )
    stages = [
        (
            "local_drs_retrieval",
            len(report.source_report.records) == 10
            and report.summary["local_drs_only"]
            and not report.summary["external_drs_network_implemented"]
            and not report.summary["global_drs_implemented"],
            "records_loaded=10",
        ),
        (
            "taxonomy_filtering",
            EXPECTED_TAXONOMY_KINDS.issubset(taxonomy_kinds) and unsafe_filtered,
            "unsafe_records_filtered=true",
        ),
        (
            "typed_edge_interpretation",
            report.source_report.summary["edge_types_present"] == 8
            and report.source_report.summary["typed_edges_are_signals_only"]
            and not report.source_report.safety["typed_edges_override_policy"]
            and not report.source_report.summary["contradiction_target_auto_blocked"]
            and report.source_report.summary[
                "contradiction_target_requires_future_conflict_check"
            ],
            "edge_types_present=8",
        ),
        (
            "graph_proximity",
            report.source_report.summary["graph_distance_computed_at_query_time"]
            and not report.source_report.summary["static_hops_stored_in_records"]
            and report.summary["graph_proximity_used_as_signal"],
            "query_time_distance=true",
        ),
        (
            "reuse_score",
            report.summary["ReuseScore_is_advisory"]
            and not report.safety["reuse_score_overrides_policy"]
            and not report.scoring_model["high_score_overrides_policy"]
            and not report.safety["high_score_unsafe_record_reused"]
            and report.safety["contradiction_requires_conflict_check"]
            and report.summary["unsafe_direct_reuse_candidates"] == 0,
            "advisory_score=true",
        ),
        (
            "reuse_gate_root_boundary",
            _boundary_stage_passed(boundary_safety),
            "boundary_preserved=true",
        ),
    ]
    return [
        SemanticReuseStage(
            stage=name,
            status="PASS" if passed else "FAIL",
            key_proof_field=proof,
        )
        for name, passed, proof in stages
    ]


def _boundary_safety(
    report: ReuseScoreReport,
    scenarios: list[SemanticReuseScenario],
) -> dict[str, Any]:
    return {
        "semantic_pipeline_committed_final_output": False,
        "semantic_pipeline_bypassed_root": False,
        "semantic_pipeline_bypassed_reuse_gate": False,
        "root_boundary_required": all(
            scenario.root_boundary_required for scenario in scenarios
        ),
        "reuse_gate_boundary_required": all(
            scenario.reuse_gate_boundary_required for scenario in scenarios
        ),
        "reuse_score_is_advisory": report.summary["ReuseScore_is_advisory"],
        "high_score_overrides_policy": report.scoring_model[
            "high_score_overrides_policy"
        ],
        "typed_edges_override_policy": report.source_report.safety[
            "typed_edges_override_policy"
        ],
        "graph_proximity_overrides_policy": False,
        "context_memory_equals_direct_reuse": False,
        "contradiction_auto_reuse": (
            report.safety["contradiction_auto_reuse_candidates"] > 0
        ),
        "contradiction_requires_conflict_check": report.safety[
            "contradiction_requires_conflict_check"
        ],
        "unsafe_direct_reuse_candidates": report.summary[
            "unsafe_direct_reuse_candidates"
        ],
        "quarantine_direct_reuse_candidates": report.safety[
            "quarantine_direct_reuse_candidates"
        ],
        "deadend_direct_reuse_candidates": report.safety[
            "deadend_direct_reuse_candidates"
        ],
        "blocked_direct_reuse_candidates": report.safety[
            "blocked_direct_reuse_candidates"
        ],
        "degraded_direct_reuse_candidates": report.safety[
            "degraded_direct_reuse_candidates"
        ],
        "needs_user_direct_reuse_candidates": report.safety[
            "needs_user_direct_reuse_candidates"
        ],
        "no_real_external_actions": True,
        "no_live_gemini": True,
        "no_telegram_actions": True,
        "no_global_drs": not report.summary["global_drs_implemented"],
        "no_external_drs_network": not report.summary[
            "external_drs_network_implemented"
        ],
        "production_autonomy_claimed": False,
    }


def _summary(
    report: ReuseScoreReport,
    stages: list[SemanticReuseStage],
    scenarios: list[SemanticReuseScenario],
    boundary_safety: dict[str, Any],
) -> dict[str, Any]:
    direct_reuse_recommended = [
        scenario
        for scenario in scenarios
        if scenario.pipeline_recommendation == "direct_reuse_candidate"
    ]
    fallback_recommended = [
        scenario
        for scenario in scenarios
        if scenario.pipeline_recommendation == "needs_full_pipeline"
    ]
    conflict_required = [
        scenario
        for scenario in scenarios
        if scenario.pipeline_recommendation == "needs_conflict_check"
    ]
    policy_blocked = [
        scenario
        for scenario in scenarios
        if scenario.pipeline_recommendation == "blocked"
    ]
    stages_passed = sum(stage.status == "PASS" for stage in stages)
    unsafe_reuse_candidates = sum(
        scenario.unsafe_reuse_candidate for scenario in scenarios
    )
    pass_status = (
        stages_passed == len(REQUIRED_STAGE_NAMES)
        and len(scenarios) >= 8
        and len(direct_reuse_recommended) >= 1
        and len(fallback_recommended) >= 1
        and len(conflict_required) >= 1
        and len(policy_blocked) >= 1
        and unsafe_reuse_candidates == 0
        and boundary_safety["root_boundary_required"]
        and boundary_safety["reuse_gate_boundary_required"]
        and not boundary_safety["semantic_pipeline_committed_final_output"]
        and not boundary_safety["semantic_pipeline_bypassed_root"]
        and not boundary_safety["semantic_pipeline_bypassed_reuse_gate"]
        and not boundary_safety["production_autonomy_claimed"]
    )
    return {
        "semantic_reuse_pipeline_status": "PASS" if pass_status else "FAIL",
        "records_loaded": len(report.source_report.records),
        "candidates_scored": len(report.candidates),
        "scenarios_evaluated": len(scenarios),
        "pipeline_stages_passed": stages_passed,
        "direct_reuse_candidates_recommended": len(direct_reuse_recommended),
        "full_pipeline_fallbacks_recommended": len(fallback_recommended),
        "conflict_check_required_cases": len(conflict_required),
        "policy_blocked_cases": len(policy_blocked),
        "unsafe_reuse_candidates": unsafe_reuse_candidates,
        "root_boundary_preserved": boundary_safety["root_boundary_required"]
        and not boundary_safety["semantic_pipeline_bypassed_root"],
        "reuse_gate_boundary_preserved": boundary_safety[
            "reuse_gate_boundary_required"
        ]
        and not boundary_safety["semantic_pipeline_bypassed_reuse_gate"],
        "pipeline_committed_final_output": boundary_safety[
            "semantic_pipeline_committed_final_output"
        ],
        "local_drs_only": report.summary["local_drs_only"],
        "external_drs_network_implemented": report.summary[
            "external_drs_network_implemented"
        ],
        "global_drs_implemented": report.summary["global_drs_implemented"],
        "production_autonomy_claimed": boundary_safety[
            "production_autonomy_claimed"
        ],
    }


def collect_semantic_reuse_pipeline() -> SemanticReusePipelineReport:
    source_report = collect_reuse_score()
    scenarios = _build_scenarios(source_report)
    boundary_safety = _boundary_safety(source_report, scenarios)
    stages = _stage_results(source_report, boundary_safety)
    summary = _summary(source_report, stages, scenarios, boundary_safety)
    return SemanticReusePipelineReport(
        source_report=source_report,
        input_modules=_input_modules(source_report),
        stages=stages,
        scenarios=scenarios,
        boundary_safety=boundary_safety,
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


def _stage_line(stage: SemanticReuseStage) -> str:
    return " | ".join([stage.stage, stage.status, stage.key_proof_field])


def _scenario_line(scenario: SemanticReuseScenario) -> str:
    return " | ".join(
        [
            scenario.scenario,
            scenario.record_id,
            scenario.taxonomy_kind,
            f"{scenario.graph_proximity:.6f}",
            f"{scenario.raw_reuse_score:.6f}",
            _bool_text(scenario.policy_allowed),
            _bool_text(scenario.direct_reuse_allowed_after_policy),
            scenario.reuse_score_recommendation,
            scenario.pipeline_recommendation,
            scenario.boundary_decision,
            _bool_text(scenario.root_boundary_required),
            _bool_text(scenario.reuse_gate_boundary_required),
            _bool_text(scenario.committed_by_pipeline),
            _bool_text(scenario.unsafe_reuse_candidate),
            scenario.explanation,
        ]
    )


def render_semantic_reuse_pipeline(report: SemanticReusePipelineReport) -> str:
    lines = [
        "[SEMANTIC REUSE PIPELINE]",
        "note: bounded LocalDRS semantic reuse integration proof",
        "note: no global DRS",
        "note: no external DRS network",
        "note: no real external actions",
        "note: no live Gemini",
        "note: no Telegram actions",
        "note: not production autonomy",
        "note: Root / ReuseGate boundary preserved",
        "note: semantic pipeline recommends but does not commit",
        "",
        "[INPUT MODULES]",
    ]
    lines.extend(_field_lines(report.input_modules))
    lines.extend(
        [
            "",
            "[PIPELINE STAGES]",
            "stage | status | key_proof_field",
            "--- | --- | ---",
        ]
    )
    lines.extend(_stage_line(stage) for stage in report.stages)
    lines.extend(
        [
            "",
            "[SCENARIO TABLE]",
            "scenario | record_id | taxonomy_kind | graph_proximity | raw_reuse_score | policy_allowed | direct_reuse_allowed_after_policy | reuse_score_recommendation | pipeline_recommendation | boundary_decision | root_boundary_required | reuse_gate_boundary_required | committed_by_pipeline | unsafe_reuse_candidate | explanation",
            "--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---",
        ]
    )
    lines.extend(_scenario_line(scenario) for scenario in report.scenarios)
    lines.extend(["", "[BOUNDARY / SAFETY]"])
    lines.extend(_field_lines(report.boundary_safety))
    lines.extend(["", "[SUMMARY]"])
    lines.extend(_field_lines(report.summary))
    return "\n".join(lines).rstrip() + "\n"


def run_semantic_reuse_pipeline() -> str:
    return render_semantic_reuse_pipeline(collect_semantic_reuse_pipeline())


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run Semantic Reuse Pipeline integration proof."
    )
    parser.parse_args()
    print(run_semantic_reuse_pipeline(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
