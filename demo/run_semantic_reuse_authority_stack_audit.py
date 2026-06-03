from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Any

from demo.run_drs_graph_proximity import DrsGraphProximityReport
from demo.run_drs_graph_proximity import collect_drs_graph_proximity
from demo.run_drs_layer_taxonomy import DrsLayerTaxonomyReport
from demo.run_drs_layer_taxonomy import collect_drs_layer_taxonomy
from demo.run_reuse_score import ReuseScoreReport
from demo.run_reuse_score import collect_reuse_score
from demo.run_root_semantic_reuse_decision_trace import (
    RootSemanticReuseDecisionTraceReport,
)
from demo.run_root_semantic_reuse_decision_trace import (
    collect_root_semantic_reuse_decision_trace,
)
from demo.run_root_semantic_reuse_final_decision_trace import (
    RootSemanticReuseFinalDecisionTraceReport,
)
from demo.run_root_semantic_reuse_final_decision_trace import (
    collect_root_semantic_reuse_final_decision_trace,
)
from demo.run_root_semantic_reuse_gate_trace import RootSemanticReuseGateTraceReport
from demo.run_root_semantic_reuse_gate_trace import (
    collect_root_semantic_reuse_gate_trace,
)
from demo.run_semantic_reuse_pipeline import SemanticReusePipelineReport
from demo.run_semantic_reuse_pipeline import collect_semantic_reuse_pipeline
from demo.run_typed_drs_lineage_edges import TypedDrsLineageReport
from demo.run_typed_drs_lineage_edges import collect_typed_drs_lineage_edges


STACK_FLOW_STAGES = [
    "LocalDRS retrieval / graph proximity",
    "DRS taxonomy",
    "Typed lineage edges",
    "ReuseScore advisory scoring",
    "Semantic reuse pipeline recommendation",
    "Root decision trace",
    "ReuseGate review trace",
    "Root final dry-run decision trace",
]


@dataclass(frozen=True)
class SemanticReuseAuthorityModuleStatus:
    module: str
    available: bool
    status: str


@dataclass(frozen=True)
class SemanticReuseAuthorityFlowStage:
    order: int
    stage: str
    status: str


@dataclass(frozen=True)
class SemanticReuseAuthorityScenario:
    scenario: str
    semantic_pipeline_recommendation: str
    root_decision: str
    reuse_gate_outcome: str
    root_final_decision: str
    production_execution: bool
    unsafe_reuse: bool


@dataclass(frozen=True)
class SemanticReuseAuthorityStackAuditReport:
    drs_graph_proximity: DrsGraphProximityReport
    drs_layer_taxonomy: DrsLayerTaxonomyReport
    typed_drs_lineage_edges: TypedDrsLineageReport
    reuse_score: ReuseScoreReport
    semantic_reuse_pipeline: SemanticReusePipelineReport
    root_semantic_reuse_decision_trace: RootSemanticReuseDecisionTraceReport
    root_semantic_reuse_gate_trace: RootSemanticReuseGateTraceReport
    root_semantic_reuse_final_decision_trace: RootSemanticReuseFinalDecisionTraceReport
    input_modules: list[SemanticReuseAuthorityModuleStatus]
    stack_flow: list[SemanticReuseAuthorityFlowStage]
    key_proofs: dict[str, Any]
    scenario_summary: list[SemanticReuseAuthorityScenario]
    authority_summary: dict[str, Any]
    summary: dict[str, Any]


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _drs_graph_proximity_pass(report: DrsGraphProximityReport) -> bool:
    rows_by_id = {row.record["record_id"]: row for row in report.rows}
    return (
        len(report.records) == 7
        and bool(report.links)
        and all(record.get("time_envelope") for record in report.records)
        and all(record.get("provenance") for record in report.records)
        and rows_by_id["child_work_direct"].final_rank_score
        > rows_by_id["fresh_but_unrelated_work"].final_rank_score
        and not rows_by_id["nearby_quarantine"].direct_reuse_eligible
        and not rows_by_id["nearby_deadend"].direct_reuse_eligible
    )


def _module_statuses(
    graph_report: DrsGraphProximityReport,
    taxonomy_report: DrsLayerTaxonomyReport,
    typed_report: TypedDrsLineageReport,
    reuse_report: ReuseScoreReport,
    pipeline_report: SemanticReusePipelineReport,
    decision_report: RootSemanticReuseDecisionTraceReport,
    gate_report: RootSemanticReuseGateTraceReport,
    final_report: RootSemanticReuseFinalDecisionTraceReport,
) -> list[SemanticReuseAuthorityModuleStatus]:
    return [
        SemanticReuseAuthorityModuleStatus(
            "drs_graph_proximity",
            True,
            "PASS" if _drs_graph_proximity_pass(graph_report) else "FAIL",
        ),
        SemanticReuseAuthorityModuleStatus(
            "drs_layer_taxonomy",
            True,
            taxonomy_report.summary["drs_layer_taxonomy_status"],
        ),
        SemanticReuseAuthorityModuleStatus(
            "typed_drs_lineage_edges",
            True,
            typed_report.summary["typed_drs_lineage_edges_status"],
        ),
        SemanticReuseAuthorityModuleStatus(
            "reuse_score",
            True,
            reuse_report.summary["reuse_score_status"],
        ),
        SemanticReuseAuthorityModuleStatus(
            "semantic_reuse_pipeline",
            True,
            pipeline_report.summary["semantic_reuse_pipeline_status"],
        ),
        SemanticReuseAuthorityModuleStatus(
            "root_semantic_reuse_decision_trace",
            True,
            decision_report.summary["root_semantic_reuse_decision_trace_status"],
        ),
        SemanticReuseAuthorityModuleStatus(
            "root_semantic_reuse_gate_trace",
            True,
            gate_report.summary["root_semantic_reuse_gate_trace_status"],
        ),
        SemanticReuseAuthorityModuleStatus(
            "root_semantic_reuse_final_decision_trace",
            True,
            final_report.summary["root_semantic_reuse_final_decision_trace_status"],
        ),
    ]


def _stack_flow(
    modules: list[SemanticReuseAuthorityModuleStatus],
) -> list[SemanticReuseAuthorityFlowStage]:
    return [
        SemanticReuseAuthorityFlowStage(index, stage, modules[index - 1].status)
        for index, stage in enumerate(STACK_FLOW_STAGES, start=1)
    ]


def _key_proofs(
    reuse_report: ReuseScoreReport,
    pipeline_report: SemanticReusePipelineReport,
    decision_report: RootSemanticReuseDecisionTraceReport,
    gate_report: RootSemanticReuseGateTraceReport,
    final_report: RootSemanticReuseFinalDecisionTraceReport,
) -> dict[str, Any]:
    return {
        "local_drs_only": final_report.summary["local_drs_only"],
        "external_drs_network_implemented": final_report.summary[
            "external_drs_network_implemented"
        ],
        "global_drs_implemented": final_report.summary["global_drs_implemented"],
        "taxonomy_used_as_filter": reuse_report.summary["taxonomy_used_as_filter"],
        "typed_edges_used_as_signals": reuse_report.summary[
            "typed_edges_used_as_signals"
        ],
        "graph_proximity_used_as_signal": reuse_report.summary[
            "graph_proximity_used_as_signal"
        ],
        "reuse_score_is_advisory": reuse_report.summary["ReuseScore_is_advisory"],
        "reuse_score_overrides_policy": reuse_report.safety[
            "reuse_score_overrides_policy"
        ],
        "high_score_overrides_policy": reuse_report.scoring_model[
            "high_score_overrides_policy"
        ],
        "context_memory_equals_direct_reuse": pipeline_report.boundary_safety[
            "context_memory_equals_direct_reuse"
        ],
        "contradiction_auto_reuse": decision_report.boundary_checks[
            "contradiction_auto_reuse"
        ],
        "contradiction_requires_conflict_check": reuse_report.safety[
            "contradiction_requires_conflict_check"
        ],
        "semantic_pipeline_committed_final_output": pipeline_report.boundary_safety[
            "semantic_pipeline_committed_final_output"
        ],
        "semantic_pipeline_bypassed_root": pipeline_report.boundary_safety[
            "semantic_pipeline_bypassed_root"
        ],
        "semantic_pipeline_bypassed_reuse_gate": pipeline_report.boundary_safety[
            "semantic_pipeline_bypassed_reuse_gate"
        ],
        "root_decisions_derived_from_pipeline": decision_report.summary[
            "root_decisions_derived_from_pipeline"
        ],
        "gate_rows_derived_from_root_decisions": gate_report.summary[
            "gate_rows_derived_from_root_decisions"
        ],
        "final_decisions_derived_from_gate_rows": final_report.summary[
            "final_decisions_derived_from_gate_rows"
        ],
        "gate_reviews_performed": gate_report.summary["gate_reviews_performed"],
        "gate_approvals_for_root_final_decision": gate_report.summary[
            "gate_approvals_for_root_final_decision"
        ],
        "controlled_direct_reuse_trace_accepts": final_report.summary[
            "controlled_direct_reuse_trace_accepts"
        ],
        "trace_final_decision_artifacts_created": final_report.final_authority_checks[
            "trace_final_decision_artifacts_created"
        ],
        "trace_artifacts_created_only_by_root": final_report.summary[
            "trace_artifacts_created_only_by_root"
        ],
        "production_direct_reuse_executed": final_report.summary[
            "production_direct_reuse_executed"
        ],
        "production_final_output_created": final_report.summary[
            "production_final_output_created"
        ],
        "production_action_executed": final_report.summary[
            "production_action_executed"
        ],
        "production_work_record_written": final_report.summary[
            "production_work_record_written"
        ],
        "unsafe_reuse_candidates": final_report.summary["unsafe_reuse_candidates"],
        "root_authority_preserved": final_report.summary[
            "root_authority_preserved"
        ],
        "reuse_gate_boundary_preserved": final_report.summary[
            "reuse_gate_boundary_preserved"
        ],
        "semantic_pipeline_authority_granted": final_report.summary[
            "semantic_pipeline_authority_granted"
        ],
        "reuse_gate_authority_granted": final_report.summary[
            "reuse_gate_authority_granted"
        ],
        "production_autonomy_claimed": final_report.summary[
            "production_autonomy_claimed"
        ],
    }


def _scenario_summary(
    pipeline_report: SemanticReusePipelineReport,
    decision_report: RootSemanticReuseDecisionTraceReport,
    gate_report: RootSemanticReuseGateTraceReport,
    final_report: RootSemanticReuseFinalDecisionTraceReport,
) -> list[SemanticReuseAuthorityScenario]:
    pipeline_by_scenario = {
        scenario.scenario: scenario for scenario in pipeline_report.scenarios
    }
    decision_by_scenario = {
        decision.scenario: decision for decision in decision_report.decisions
    }
    gate_by_scenario = {row.scenario: row for row in gate_report.rows}
    final_by_scenario = {
        row.scenario: row for row in final_report.final_decisions
    }
    rows: list[SemanticReuseAuthorityScenario] = []
    for scenario in pipeline_report.scenarios:
        decision = decision_by_scenario[scenario.scenario]
        gate = gate_by_scenario[scenario.scenario]
        final = final_by_scenario[scenario.scenario]
        rows.append(
            SemanticReuseAuthorityScenario(
                scenario=scenario.scenario,
                semantic_pipeline_recommendation=scenario.pipeline_recommendation,
                root_decision=decision.root_decision,
                reuse_gate_outcome=gate.gate_outcome,
                root_final_decision=final.root_final_decision,
                production_execution=(
                    final.production_direct_reuse_executed
                    or final.production_action_executed
                ),
                unsafe_reuse=(
                    scenario.unsafe_reuse_candidate
                    or decision.unsafe_reuse_candidate
                    or gate.unsafe_reuse_candidate
                    or final.unsafe_reuse_candidate
                ),
            )
        )
    return rows


def _authority_summary() -> dict[str, Any]:
    return {
        "semantic_pipeline_role": "recommends_only",
        "reuse_score_role": "advisory_ranking_only",
        "root_decision_role": "maps_recommendations",
        "reuse_gate_role": "reviews_direct_reuse_candidate_only",
        "root_final_role": "creates_trace_level_final_decision_artifact_only",
        "production_execution": False,
        "production_final_output": False,
        "production_work_writeback": False,
    }


def _summary(
    modules: list[SemanticReuseAuthorityModuleStatus],
    flow: list[SemanticReuseAuthorityFlowStage],
    key_proofs: dict[str, Any],
    scenarios: list[SemanticReuseAuthorityScenario],
) -> dict[str, Any]:
    modules_pass = all(module.status == "PASS" for module in modules)
    flow_pass = all(stage.status == "PASS" for stage in flow)
    scenarios_pass = (
        len(scenarios) == 8
        and all(not row.production_execution for row in scenarios)
        and all(not row.unsafe_reuse for row in scenarios)
    )
    key_pass = (
        key_proofs["local_drs_only"]
        and not key_proofs["external_drs_network_implemented"]
        and not key_proofs["global_drs_implemented"]
        and key_proofs["taxonomy_used_as_filter"]
        and key_proofs["typed_edges_used_as_signals"]
        and key_proofs["graph_proximity_used_as_signal"]
        and key_proofs["reuse_score_is_advisory"]
        and not key_proofs["reuse_score_overrides_policy"]
        and not key_proofs["high_score_overrides_policy"]
        and not key_proofs["context_memory_equals_direct_reuse"]
        and not key_proofs["contradiction_auto_reuse"]
        and key_proofs["contradiction_requires_conflict_check"]
        and not key_proofs["semantic_pipeline_committed_final_output"]
        and not key_proofs["semantic_pipeline_bypassed_root"]
        and not key_proofs["semantic_pipeline_bypassed_reuse_gate"]
        and key_proofs["root_decisions_derived_from_pipeline"]
        and key_proofs["gate_rows_derived_from_root_decisions"]
        and key_proofs["final_decisions_derived_from_gate_rows"]
        and key_proofs["gate_reviews_performed"] == 1
        and key_proofs["gate_approvals_for_root_final_decision"] == 1
        and key_proofs["controlled_direct_reuse_trace_accepts"] == 1
        and key_proofs["trace_final_decision_artifacts_created"] == 1
        and key_proofs["trace_artifacts_created_only_by_root"]
        and not key_proofs["production_direct_reuse_executed"]
        and not key_proofs["production_final_output_created"]
        and not key_proofs["production_action_executed"]
        and not key_proofs["production_work_record_written"]
        and key_proofs["unsafe_reuse_candidates"] == 0
        and key_proofs["root_authority_preserved"]
        and key_proofs["reuse_gate_boundary_preserved"]
        and not key_proofs["semantic_pipeline_authority_granted"]
        and not key_proofs["reuse_gate_authority_granted"]
        and not key_proofs["production_autonomy_claimed"]
    )
    pass_status = modules_pass and flow_pass and scenarios_pass and key_pass
    return {
        "semantic_reuse_authority_stack_audit_status": (
            "PASS" if pass_status else "FAIL"
        ),
        "modules_verified": len(modules),
        "scenarios_verified": len(scenarios),
        "authority_chain_complete_in_dry_run": (
            modules_pass
            and flow_pass
            and key_proofs["final_decisions_derived_from_gate_rows"]
            and key_proofs["trace_artifacts_created_only_by_root"]
            and not key_proofs["production_direct_reuse_executed"]
        ),
        "ready_for_root_native_semantic_reuse_e2e_trace": pass_status,
        "local_drs_only": key_proofs["local_drs_only"],
        "external_drs_network_implemented": key_proofs[
            "external_drs_network_implemented"
        ],
        "global_drs_implemented": key_proofs["global_drs_implemented"],
        "production_autonomy_claimed": key_proofs["production_autonomy_claimed"],
    }


def collect_semantic_reuse_authority_stack_audit() -> (
    SemanticReuseAuthorityStackAuditReport
):
    graph_report = collect_drs_graph_proximity()
    taxonomy_report = collect_drs_layer_taxonomy()
    typed_report = collect_typed_drs_lineage_edges()
    reuse_report = collect_reuse_score()
    pipeline_report = collect_semantic_reuse_pipeline()
    decision_report = collect_root_semantic_reuse_decision_trace()
    gate_report = collect_root_semantic_reuse_gate_trace()
    final_report = collect_root_semantic_reuse_final_decision_trace()
    modules = _module_statuses(
        graph_report,
        taxonomy_report,
        typed_report,
        reuse_report,
        pipeline_report,
        decision_report,
        gate_report,
        final_report,
    )
    flow = _stack_flow(modules)
    key_proofs = _key_proofs(
        reuse_report,
        pipeline_report,
        decision_report,
        gate_report,
        final_report,
    )
    scenarios = _scenario_summary(
        pipeline_report,
        decision_report,
        gate_report,
        final_report,
    )
    authority = _authority_summary()
    summary = _summary(modules, flow, key_proofs, scenarios)
    return SemanticReuseAuthorityStackAuditReport(
        drs_graph_proximity=graph_report,
        drs_layer_taxonomy=taxonomy_report,
        typed_drs_lineage_edges=typed_report,
        reuse_score=reuse_report,
        semantic_reuse_pipeline=pipeline_report,
        root_semantic_reuse_decision_trace=decision_report,
        root_semantic_reuse_gate_trace=gate_report,
        root_semantic_reuse_final_decision_trace=final_report,
        input_modules=modules,
        stack_flow=flow,
        key_proofs=key_proofs,
        scenario_summary=scenarios,
        authority_summary=authority,
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


def _module_line(module: SemanticReuseAuthorityModuleStatus) -> str:
    return " | ".join(
        [
            module.module,
            _bool_text(module.available),
            module.status,
        ]
    )


def _flow_line(stage: SemanticReuseAuthorityFlowStage) -> str:
    return f"{stage.order}. {stage.stage}: {stage.status}"


def _scenario_line(row: SemanticReuseAuthorityScenario) -> str:
    return " | ".join(
        [
            row.scenario,
            row.semantic_pipeline_recommendation,
            row.root_decision,
            row.reuse_gate_outcome,
            row.root_final_decision,
            _bool_text(row.production_execution),
            _bool_text(row.unsafe_reuse),
        ]
    )


def render_semantic_reuse_authority_stack_audit(
    report: SemanticReuseAuthorityStackAuditReport,
) -> str:
    lines = [
        "[SEMANTIC REUSE AUTHORITY STACK AUDIT]",
        "note: auditor-facing aggregate proof only",
        "note: no production RootOrchestrator behavior change",
        "note: no production direct reuse execution",
        "note: no production FinalOutput",
        "note: no production Work writeback",
        "note: no real external actions",
        "note: no live Gemini",
        "note: no Telegram actions",
        "note: no global DRS",
        "note: no external DRS network",
        "note: semantic pipeline recommends, Root decides, ReuseGate guards, Root final trace decides",
        "",
        "[INPUT MODULES]",
        "module | available | status",
        "--- | --- | ---",
    ]
    lines.extend(_module_line(module) for module in report.input_modules)
    lines.extend(["", "[STACK FLOW]"])
    lines.extend(_flow_line(stage) for stage in report.stack_flow)
    lines.extend(["", "[KEY PROOFS]"])
    lines.extend(_field_lines(report.key_proofs))
    lines.extend(
        [
            "",
            "[SCENARIO SUMMARY]",
            "scenario | semantic_pipeline_recommendation | root_decision | reuse_gate_outcome | root_final_decision | production_execution | unsafe_reuse",
            "--- | --- | --- | --- | --- | --- | ---",
        ]
    )
    lines.extend(_scenario_line(row) for row in report.scenario_summary)
    lines.extend(["", "[AUTHORITY SUMMARY]"])
    lines.extend(_field_lines(report.authority_summary))
    lines.extend(["", "[SUMMARY]"])
    lines.extend(_field_lines(report.summary))
    return "\n".join(lines).rstrip() + "\n"


def run_semantic_reuse_authority_stack_audit() -> str:
    return render_semantic_reuse_authority_stack_audit(
        collect_semantic_reuse_authority_stack_audit()
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run Semantic Reuse Authority Stack Audit proof."
    )
    parser.parse_args()
    print(run_semantic_reuse_authority_stack_audit(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
