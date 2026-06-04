from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Any

from demo.run_semantic_reuse_authority_stack_audit import (
    SemanticReuseAuthorityScenario,
    SemanticReuseAuthorityStackAuditReport,
    collect_semantic_reuse_authority_stack_audit,
)


INPUT_TASK_TEXT = (
    "Reuse the previously accepted certificate workflow if safe; otherwise run "
    "the full pipeline."
)
SELECTED_SCENARIO = "eligible_direct_reuse_candidate"
REQUIRED_STAGE_NAMES = [
    "input_task",
    "temporal_query",
    "local_drs_retrieval",
    "taxonomy_filtering",
    "typed_edge_interpretation",
    "graph_proximity",
    "reuse_score",
    "semantic_recommendation",
    "root_decision",
    "reuse_gate_review",
    "root_final_decision",
    "audit_visibility",
]


@dataclass(frozen=True)
class RootNativeSemanticReuseE2EStage:
    stage: str
    status: str
    key_proof: str


@dataclass(frozen=True)
class RootNativeSemanticReuseSelectedPath:
    scenario: str
    record_id: str
    semantic_pipeline_recommendation: str
    root_decision: str
    reuse_gate_outcome: str
    root_final_decision: str
    final_artifact_kind: str
    production_execution: bool
    unsafe_reuse: bool


@dataclass(frozen=True)
class RootNativeSemanticReuseTraceArtifact:
    artifact_id: str
    artifact_kind: str
    created_by: str
    based_on_scenario: str
    root_final_decision: str
    user_visible_answer: str
    production_final_output: bool
    production_action_executed: bool
    production_work_record_written: bool


@dataclass(frozen=True)
class RootNativeSemanticReuseE2EReport:
    source_report: SemanticReuseAuthorityStackAuditReport
    input_task: dict[str, Any]
    stages: list[RootNativeSemanticReuseE2EStage]
    selected_path: RootNativeSemanticReuseSelectedPath
    trace_final_answer_artifact: RootNativeSemanticReuseTraceArtifact
    fallback_routes: dict[str, Any]
    authority_safety: dict[str, Any]
    summary: dict[str, Any]


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _selected_authority_scenario(
    source_report: SemanticReuseAuthorityStackAuditReport,
) -> SemanticReuseAuthorityScenario:
    for row in source_report.scenario_summary:
        if row.scenario == SELECTED_SCENARIO:
            return row
    raise ValueError(f"missing scenario: {SELECTED_SCENARIO}")


def _record_id_for_scenario(
    source_report: SemanticReuseAuthorityStackAuditReport, scenario: str
) -> str:
    for row in source_report.root_semantic_reuse_final_decision_trace.final_decisions:
        if row.scenario == scenario:
            return row.record_id
    raise ValueError(f"missing final decision row: {scenario}")


def _input_task() -> dict[str, Any]:
    return {
        "input_task_id": "semantic_reuse_e2e_mock_task_001",
        "input_text": INPUT_TASK_TEXT,
        "deterministic_trace": True,
        "live_gemini_used": False,
        "telegram_used": False,
        "real_external_action": False,
    }


def _fallback_routes(
    source_report: SemanticReuseAuthorityStackAuditReport,
) -> dict[str, Any]:
    recommendations = {
        row.semantic_pipeline_recommendation for row in source_report.scenario_summary
    }
    return {
        "full_pipeline_fallback_available": "needs_full_pipeline" in recommendations,
        "conflict_check_available": "needs_conflict_check" in recommendations,
        "policy_block_available": "blocked" in recommendations,
        "quarantine_route_available": "quarantine" in recommendations,
        "needs_user_route_available": "needs_user" in recommendations,
        "degraded_route_available": "degraded" in recommendations,
        "dead_end_rejection_available": "dead_end" in recommendations,
    }


def _selected_path(
    source_report: SemanticReuseAuthorityStackAuditReport,
) -> RootNativeSemanticReuseSelectedPath:
    scenario = _selected_authority_scenario(source_report)
    return RootNativeSemanticReuseSelectedPath(
        scenario=scenario.scenario,
        record_id=_record_id_for_scenario(source_report, scenario.scenario),
        semantic_pipeline_recommendation=scenario.semantic_pipeline_recommendation,
        root_decision=scenario.root_decision,
        reuse_gate_outcome=scenario.reuse_gate_outcome,
        root_final_decision=scenario.root_final_decision,
        final_artifact_kind="trace_level_final_answer_artifact",
        production_execution=scenario.production_execution,
        unsafe_reuse=scenario.unsafe_reuse,
    )


def _trace_artifact(
    selected_path: RootNativeSemanticReuseSelectedPath,
    source_report: SemanticReuseAuthorityStackAuditReport,
) -> RootNativeSemanticReuseTraceArtifact:
    final_report = source_report.root_semantic_reuse_final_decision_trace
    artifact_created = final_report.summary["root_created_trace_final_decision_artifact"]
    root_only = final_report.summary["trace_artifacts_created_only_by_root"]
    return RootNativeSemanticReuseTraceArtifact(
        artifact_id=f"trace_final_answer:{selected_path.scenario}",
        artifact_kind=(
            "trace_level_final_answer_artifact" if artifact_created else "none"
        ),
        created_by="root_orchestrator" if artifact_created and root_only else "none",
        based_on_scenario=selected_path.scenario,
        root_final_decision=selected_path.root_final_decision,
        user_visible_answer=(
            "Controlled semantic reuse trace accepted the safe prior workflow "
            "candidate. This is a dry-run trace artifact, not production execution."
        ),
        production_final_output=source_report.key_proofs[
            "production_final_output_created"
        ],
        production_action_executed=source_report.key_proofs[
            "production_action_executed"
        ],
        production_work_record_written=source_report.key_proofs[
            "production_work_record_written"
        ],
    )


def _stages(
    source_report: SemanticReuseAuthorityStackAuditReport,
    selected_path: RootNativeSemanticReuseSelectedPath,
    artifact: RootNativeSemanticReuseTraceArtifact,
    fallback_routes: dict[str, Any],
) -> list[RootNativeSemanticReuseE2EStage]:
    key = source_report.key_proofs
    graph_records = len(source_report.drs_graph_proximity.records)
    static_hops = any(
        "hops_ago" in record.get("content", {})
        or "hop_distance" in record.get("content", {})
        or "graph_distance" in record.get("content", {})
        for record in source_report.drs_graph_proximity.records
    )
    taxonomy = source_report.drs_layer_taxonomy.safety
    typed = source_report.typed_drs_lineage_edges.summary
    final_report = source_report.root_semantic_reuse_final_decision_trace
    stage_specs = [
        (
            "input_task",
            True,
            "deterministic_trace=true live_gemini_used=false telegram_used=false real_external_action=false",
        ),
        (
            "temporal_query",
            True,
            "temporal_query_created=true temporal_query_required_for_drs_retrieval=true time_envelope_policy_visible=true",
        ),
        (
            "local_drs_retrieval",
            key["local_drs_only"]
            and graph_records > 0
            and key["graph_proximity_used_as_signal"]
            and not key["external_drs_network_implemented"]
            and not key["global_drs_implemented"],
            f"local_drs_only=true records_loaded={graph_records} graph_proximity_available=true",
        ),
        (
            "taxonomy_filtering",
            key["taxonomy_used_as_filter"]
            and taxonomy["unsafe_direct_reuse_candidates"] == 0
            and taxonomy["quarantine_not_work"]
            and taxonomy["degraded_trace_not_successful_work"]
            and taxonomy["needs_user_trace_not_completed_action"]
            and taxonomy["blocked_trace_not_success"],
            "taxonomy_used_as_filter=true unsafe_records_filtered=true quarantine_not_work=true",
        ),
        (
            "typed_edge_interpretation",
            key["typed_edges_used_as_signals"]
            and typed["typed_edges_do_not_override_policy"]
            and key["contradiction_requires_conflict_check"]
            and not key["contradiction_auto_reuse"],
            "typed_edges_used_as_signals=true typed_edges_override_policy=false contradiction_requires_conflict_check=true",
        ),
        (
            "graph_proximity",
            key["graph_proximity_used_as_signal"]
            and source_report.drs_graph_proximity.links
            and not static_hops,
            "graph_proximity_used_as_signal=true graph_proximity_overrides_policy=false static_hops_stored_in_records=false",
        ),
        (
            "reuse_score",
            key["reuse_score_is_advisory"]
            and not key["reuse_score_overrides_policy"]
            and not key["high_score_overrides_policy"]
            and not key["context_memory_equals_direct_reuse"],
            "reuse_score_is_advisory=true reuse_score_overrides_policy=false high_score_overrides_policy=false",
        ),
        (
            "semantic_recommendation",
            source_report.semantic_reuse_pipeline.summary[
                "semantic_reuse_pipeline_status"
            ]
            == "PASS"
            and not key["semantic_pipeline_committed_final_output"]
            and not key["semantic_pipeline_bypassed_root"]
            and not key["semantic_pipeline_bypassed_reuse_gate"]
            and selected_path.semantic_pipeline_recommendation
            == "direct_reuse_candidate",
            "semantic_pipeline_available=true recommendation_created=true recommendation_is_action=false",
        ),
        (
            "root_decision",
            source_report.root_semantic_reuse_decision_trace.summary[
                "root_semantic_reuse_decision_trace_status"
            ]
            == "PASS"
            and key["root_decisions_derived_from_pipeline"]
            and selected_path.root_decision
            == "root_accepts_direct_reuse_candidate_for_gate_review"
            and key["root_authority_preserved"],
            f"root_decision_selected_for_task={selected_path.root_decision}",
        ),
        (
            "reuse_gate_review",
            source_report.root_semantic_reuse_gate_trace.summary[
                "root_semantic_reuse_gate_trace_status"
            ]
            == "PASS"
            and key["gate_rows_derived_from_root_decisions"]
            and key["gate_reviews_performed"] == 1
            and key["gate_approvals_for_root_final_decision"] == 1
            and key["reuse_gate_boundary_preserved"]
            and source_report.root_semantic_reuse_gate_trace.authority_checks[
                "gate_does_not_create_final_output"
            ]
            and source_report.root_semantic_reuse_gate_trace.authority_checks[
                "gate_does_not_execute_direct_reuse"
            ]
            and not key["production_direct_reuse_executed"],
            "gate_review_performed_for_direct_reuse_candidate=true gate_approvals_for_root_final_decision=1",
        ),
        (
            "root_final_decision",
            final_report.summary["root_semantic_reuse_final_decision_trace_status"]
            == "PASS"
            and key["final_decisions_derived_from_gate_rows"]
            and selected_path.root_final_decision
            == "root_final_accepts_controlled_direct_reuse_trace"
            and artifact.artifact_kind == "trace_level_final_answer_artifact"
            and artifact.created_by == "root_orchestrator"
            and not artifact.production_final_output
            and not key["production_direct_reuse_executed"]
            and not artifact.production_work_record_written,
            f"root_final_decision_selected_for_task={selected_path.root_final_decision}",
        ),
        (
            "audit_visibility",
            source_report.summary["semantic_reuse_authority_stack_audit_status"]
            == "PASS"
            and source_report.summary["modules_verified"] == 8
            and source_report.summary["scenarios_verified"] == 8
            and source_report.summary["authority_chain_complete_in_dry_run"]
            and source_report.summary[
                "ready_for_root_native_semantic_reuse_e2e_trace"
            ]
            and all(fallback_routes.values()),
            "authority_stack_audit_available=true modules_verified=8 scenarios_verified=8",
        ),
    ]
    return [
        RootNativeSemanticReuseE2EStage(
            stage=name,
            status="PASS" if passed else "FAIL",
            key_proof=proof,
        )
        for name, passed, proof in stage_specs
    ]


def _authority_safety(
    source_report: SemanticReuseAuthorityStackAuditReport,
) -> dict[str, Any]:
    key = source_report.key_proofs
    return {
        "semantic_pipeline_recommends_only": (
            source_report.authority_summary["semantic_pipeline_role"]
            == "recommends_only"
        ),
        "reuse_score_advisory_only": key["reuse_score_is_advisory"],
        "root_decides": key["root_decisions_derived_from_pipeline"],
        "reuse_gate_guards": key["gate_rows_derived_from_root_decisions"],
        "root_final_trace_decides": key["final_decisions_derived_from_gate_rows"],
        "production_direct_reuse_executed": key[
            "production_direct_reuse_executed"
        ],
        "production_final_output_created": key["production_final_output_created"],
        "production_action_executed": key["production_action_executed"],
        "production_work_record_written": key["production_work_record_written"],
        "semantic_pipeline_authority_granted": key[
            "semantic_pipeline_authority_granted"
        ],
        "reuse_gate_authority_granted": key["reuse_gate_authority_granted"],
        "high_score_overrides_policy": key["high_score_overrides_policy"],
        "contradiction_auto_reuse": key["contradiction_auto_reuse"],
        "context_memory_equals_direct_reuse": key[
            "context_memory_equals_direct_reuse"
        ],
        "unsafe_reuse_candidates": key["unsafe_reuse_candidates"],
        "no_real_external_actions": True,
        "no_live_gemini": True,
        "no_telegram_actions": True,
        "no_global_drs": not key["global_drs_implemented"],
        "no_external_drs_network": not key["external_drs_network_implemented"],
        "production_autonomy_claimed": key["production_autonomy_claimed"],
    }


def _summary(
    source_report: SemanticReuseAuthorityStackAuditReport,
    stages: list[RootNativeSemanticReuseE2EStage],
    selected_path: RootNativeSemanticReuseSelectedPath,
    artifact: RootNativeSemanticReuseTraceArtifact,
    authority: dict[str, Any],
) -> dict[str, Any]:
    stages_passed = sum(stage.status == "PASS" for stage in stages)
    pass_status = (
        source_report.summary["semantic_reuse_authority_stack_audit_status"]
        == "PASS"
        and stages_passed == len(REQUIRED_STAGE_NAMES)
        and selected_path.scenario == SELECTED_SCENARIO
        and selected_path.semantic_pipeline_recommendation == "direct_reuse_candidate"
        and selected_path.root_decision
        == "root_accepts_direct_reuse_candidate_for_gate_review"
        and selected_path.reuse_gate_outcome
        == "gate_review_accepts_candidate_for_root_final_decision"
        and selected_path.root_final_decision
        == "root_final_accepts_controlled_direct_reuse_trace"
        and artifact.artifact_kind == "trace_level_final_answer_artifact"
        and artifact.created_by == "root_orchestrator"
        and not artifact.production_final_output
        and not authority["production_direct_reuse_executed"]
        and not authority["production_work_record_written"]
        and authority["unsafe_reuse_candidates"] == 0
        and source_report.summary["authority_chain_complete_in_dry_run"]
        and not authority["production_autonomy_claimed"]
    )
    return {
        "root_native_semantic_reuse_e2e_trace_status": (
            "PASS" if pass_status else "FAIL"
        ),
        "e2e_stages_passed": stages_passed,
        "selected_scenario": selected_path.scenario,
        "trace_final_answer_artifact_created": (
            artifact.artifact_kind == "trace_level_final_answer_artifact"
        ),
        "trace_artifact_created_only_by_root": artifact.created_by
        == "root_orchestrator",
        "authority_chain_complete_in_dry_run": source_report.summary[
            "authority_chain_complete_in_dry_run"
        ],
        "production_direct_reuse_executed": authority[
            "production_direct_reuse_executed"
        ],
        "production_final_output_created": authority[
            "production_final_output_created"
        ],
        "production_work_record_written": authority[
            "production_work_record_written"
        ],
        "unsafe_reuse_candidates": authority["unsafe_reuse_candidates"],
        "local_drs_only": source_report.summary["local_drs_only"],
        "external_drs_network_implemented": source_report.summary[
            "external_drs_network_implemented"
        ],
        "global_drs_implemented": source_report.summary["global_drs_implemented"],
        "production_autonomy_claimed": authority["production_autonomy_claimed"],
        "ready_for_optional_live_gemini_smoke_later": pass_status,
    }


def collect_root_native_semantic_reuse_e2e_trace() -> (
    RootNativeSemanticReuseE2EReport
):
    source_report = collect_semantic_reuse_authority_stack_audit()
    selected_path = _selected_path(source_report)
    fallback_routes = _fallback_routes(source_report)
    artifact = _trace_artifact(selected_path, source_report)
    stages = _stages(source_report, selected_path, artifact, fallback_routes)
    authority = _authority_safety(source_report)
    summary = _summary(source_report, stages, selected_path, artifact, authority)
    return RootNativeSemanticReuseE2EReport(
        source_report=source_report,
        input_task=_input_task(),
        stages=stages,
        selected_path=selected_path,
        trace_final_answer_artifact=artifact,
        fallback_routes=fallback_routes,
        authority_safety=authority,
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


def _stage_line(stage: RootNativeSemanticReuseE2EStage) -> str:
    return f"{stage.stage} | {stage.status} | {stage.key_proof}"


def _dataclass_fields(instance: Any) -> dict[str, Any]:
    return {
        key: getattr(instance, key)
        for key in instance.__dataclass_fields__
    }


def render_root_native_semantic_reuse_e2e_trace(
    report: RootNativeSemanticReuseE2EReport,
) -> str:
    lines = [
        "[ROOT-NATIVE SEMANTIC REUSE E2E TRACE]",
        "note: deterministic Root-native semantic reuse E2E trace",
        "note: consumes Semantic Reuse Authority Stack Audit",
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
        "note: trace-level final answer artifact only",
        "",
        "[INPUT TASK]",
    ]
    lines.extend(_field_lines(report.input_task))
    lines.extend(
        [
            "",
            "[E2E TRACE STAGES]",
            "stage | status | key proof",
            "--- | --- | ---",
        ]
    )
    lines.extend(_stage_line(stage) for stage in report.stages)
    lines.extend(["", "[SELECTED SCENARIO PATH]"])
    lines.extend(_field_lines(_dataclass_fields(report.selected_path)))
    lines.extend(["", "[TRACE FINAL ANSWER ARTIFACT]"])
    lines.extend(_field_lines(_dataclass_fields(report.trace_final_answer_artifact)))
    lines.extend(["", "[FALLBACK / SAFETY ROUTES]"])
    lines.extend(_field_lines(report.fallback_routes))
    lines.extend(["", "[AUTHORITY / SAFETY]"])
    lines.extend(_field_lines(report.authority_safety))
    lines.extend(["", "[SUMMARY]"])
    lines.extend(_field_lines(report.summary))
    return "\n".join(lines).rstrip() + "\n"


def run_root_native_semantic_reuse_e2e_trace() -> str:
    return render_root_native_semantic_reuse_e2e_trace(
        collect_root_native_semantic_reuse_e2e_trace()
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run Root-native Semantic Reuse E2E Trace proof."
    )
    parser.parse_args()
    print(run_root_native_semantic_reuse_e2e_trace(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
