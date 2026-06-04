from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Any

from demo.run_root_native_canonical_trace import RootNativeCanonicalTrace
from demo.run_root_native_canonical_trace import run_trace as collect_canonical_trace
from demo.run_root_native_semantic_reuse_e2e_trace import (
    RootNativeSemanticReuseE2EReport,
)
from demo.run_root_native_semantic_reuse_e2e_trace import (
    collect_root_native_semantic_reuse_e2e_trace,
)


FIRST_RUN_TASK = (
    "Create a safe certificate workflow plan and produce a Root-controlled "
    "trace artifact."
)
SECOND_RUN_TASK = (
    "Reuse the previously accepted certificate workflow if safe; otherwise run "
    "the full pipeline."
)

FIRST_RUN_STAGE_NAMES = [
    "root_intake",
    "orchestrator_boundary",
    "architect_plan_graph",
    "avf_attractor",
    "dag_executor",
    "post_vv",
    "gt",
    "root_final_trace_artifact",
    "drs_writeback_audit",
]


@dataclass(frozen=True)
class FullCanonicalE2EStage:
    stage: str
    status: str
    key_proof: str
    source: str


@dataclass(frozen=True)
class FullCanonicalE2ESelectedPath:
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
class RootNativeFullCanonicalE2EReport:
    first_run_source: RootNativeCanonicalTrace
    second_run_source: RootNativeSemanticReuseE2EReport
    input_tasks: dict[str, Any]
    first_run_stages: list[FullCanonicalE2EStage]
    second_run_stages: list[FullCanonicalE2EStage]
    selected_scenario_path: FullCanonicalE2ESelectedPath
    bridge_between_runs: dict[str, Any]
    final_artifacts: dict[str, Any]
    authority_safety: dict[str, Any]
    summary: dict[str, Any]


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _input_tasks() -> dict[str, Any]:
    return {
        "first_run_task_id": "full_canonical_first_run_001",
        "first_run_input_text": FIRST_RUN_TASK,
        "second_run_task_id": "full_canonical_second_run_001",
        "second_run_input_text": SECOND_RUN_TASK,
        "deterministic_trace": True,
        "live_gemini_used": False,
        "telegram_used": False,
        "real_external_action": False,
    }


def _stage(
    name: str,
    passed: bool,
    key_proof: str,
    source: str = "existing_proof_summary",
) -> FullCanonicalE2EStage:
    return FullCanonicalE2EStage(
        stage=name,
        status="PASS" if passed else "FAIL",
        key_proof=key_proof,
        source=source,
    )


def _first_run_stages(
    canonical: RootNativeCanonicalTrace,
) -> list[FullCanonicalE2EStage]:
    sections = canonical.sections
    root_intake = sections["root_intake"]
    route = sections["root_orchestrator_route_assembly"]
    avf = sections["avf_attractor"]
    architect = sections["architect"]
    dag = sections["dag_runner"]
    post_gt = sections["post_vv_gt"]
    root_final = sections["root_final"]
    drs = sections["drs_writeback_audit"]

    return [
        _stage(
            "root_intake",
            root_intake["root_authority"]
            and root_intake["final_output_created_by_root_only"],
            "root_boundary_entered=true; root_authority_present=true",
        ),
        _stage(
            "orchestrator_boundary",
            route["orchestrator_stage_explicit"]
            and not route["orchestrator_created_final_output"],
            (
                "orchestrator_or_route_boundary_visible=true; "
                "orchestrator_does_not_create_final_output=true"
            ),
        ),
        _stage(
            "architect_plan_graph",
            architect["plan_graph_valid"]
            and architect["architect_returned_plan_graph"]
            and not architect["architect_created_final_output"],
            (
                "architect_or_plan_graph_visible=true; plan_graph_present=true; "
                "architect_does_not_answer_user=true"
            ),
        ),
        _stage(
            "avf_attractor",
            avf["avf_runs_before_architect"]
            and avf["attractor_packet_created"]
            and not avf["architect_received_forbidden_vectors"],
            (
                "avf_or_attractor_visible=true; "
                "attractor_packet_or_vector_selection_present=true; "
                "avf_does_not_build_final_answer=true"
            ),
        ),
        _stage(
            "dag_executor",
            dag["fractal_dag_executor_used"]
            and dag["dag_result_proposals_count"] > 0
            and not dag["executor_created_final_output"],
            (
                "dag_or_executor_path_visible=true; result_proposals_present=true; "
                "executor_does_not_create_final_output=true"
            ),
        ),
        _stage(
            "post_vv",
            post_gt["post_vv_after_dag_executor"]
            and post_gt["vv_reports_count"] > 0,
            "post_vv_present=true; post_vv_before_gt=true",
        ),
        _stage(
            "gt",
            post_gt["gt_after_post_vv"]
            and post_gt["gt_decision"] == "accept"
            and not post_gt["gt_committed_final_output"],
            "gt_present=true; gt_after_post_vv=true; gt_does_not_claim_truth_proof=true",
        ),
        _stage(
            "root_final_trace_artifact",
            root_final["root_created_final_output"]
            and not root_final["uncontrolled_delegation"],
            (
                "root_final_authority_preserved=true; "
                "root_created_trace_artifact=true; "
                "production_external_action_executed=false"
            ),
        ),
        _stage(
            "drs_writeback_audit",
            drs["work_record_written"]
            and drs["time_envelope_present"]
            and drs["provenance_present"]
            and drs["audit_trace_present"]
            and drs["sensitive_input_absent"],
            (
                "local_drs_writeback_or_trace_visible=true; "
                "time_envelope_present=true; provenance_present=true; "
                "audit_visibility_present=true; no_sensitive_payload=true"
            ),
        ),
    ]


def _second_run_stages(
    semantic: RootNativeSemanticReuseE2EReport,
) -> list[FullCanonicalE2EStage]:
    return [
        FullCanonicalE2EStage(
            stage=stage.stage,
            status=stage.status,
            key_proof=stage.key_proof,
            source="collect_root_native_semantic_reuse_e2e_trace",
        )
        for stage in semantic.stages
    ]


def _selected_path(
    semantic: RootNativeSemanticReuseE2EReport,
) -> FullCanonicalE2ESelectedPath:
    path = semantic.selected_path
    return FullCanonicalE2ESelectedPath(
        scenario=path.scenario,
        record_id=path.record_id,
        semantic_pipeline_recommendation=path.semantic_pipeline_recommendation,
        root_decision=path.root_decision,
        reuse_gate_outcome=path.reuse_gate_outcome,
        root_final_decision=path.root_final_decision,
        final_artifact_kind=path.final_artifact_kind,
        production_execution=path.production_execution,
        unsafe_reuse=path.unsafe_reuse,
    )


def _stage_pass_count(stages: list[FullCanonicalE2EStage]) -> int:
    return sum(stage.status == "PASS" for stage in stages)


def _bridge(
    canonical: RootNativeCanonicalTrace,
    semantic: RootNativeSemanticReuseE2EReport,
) -> dict[str, Any]:
    drs = canonical.sections["drs_writeback_audit"]
    semantic_local_drs_stage = next(
        stage for stage in semantic.stages if stage.stage == "local_drs_retrieval"
    )
    return {
        "first_run_created_root_trace_artifact": canonical.sections[
            "root_final"
        ]["root_created_final_output"],
        "first_run_local_drs_writeback_visible": drs["work_record_written"]
        and drs["time_envelope_present"]
        and drs["provenance_present"],
        "first_run_local_work_record_written_in_proof": drs["work_record_written"],
        "second_run_retrieved_local_drs_signal": (
            semantic_local_drs_stage.status == "PASS"
        ),
        "second_run_used_semantic_reuse_stack": semantic.summary[
            "authority_chain_complete_in_dry_run"
        ],
        "reuse_bridge_is_dry_run": True,
        "production_reuse_not_executed": not semantic.summary[
            "production_direct_reuse_executed"
        ],
        "bridge_mode": "deterministic_proof_linkage",
        "production_persistence_claimed": False,
        "production_reuse_claimed": False,
    }


def _final_artifacts(
    semantic: RootNativeSemanticReuseE2EReport,
) -> dict[str, Any]:
    return {
        "first_run_artifact_kind": "root_controlled_trace_artifact",
        "first_run_artifact_created_by": "root_orchestrator",
        "second_run_artifact_kind": semantic.trace_final_answer_artifact.artifact_kind,
        "second_run_artifact_created_by": semantic.trace_final_answer_artifact.created_by,
        "production_final_output_created": False,
        "production_external_action_executed": False,
    }


def _authority_safety(
    canonical: RootNativeCanonicalTrace,
    semantic: RootNativeSemanticReuseE2EReport,
    bridge: dict[str, Any],
) -> dict[str, Any]:
    first_sections = canonical.sections
    semantic_authority = semantic.authority_safety
    return {
        "root_authority_preserved_first_run": first_sections["root_final"][
            "root_created_final_output"
        ]
        and not first_sections["root_final"]["uncontrolled_delegation"],
        "root_authority_preserved_second_run": semantic_authority["root_decides"]
        and semantic_authority["root_final_trace_decides"],
        "reuse_gate_boundary_preserved": semantic_authority[
            "reuse_gate_guards"
        ],
        "semantic_pipeline_recommends_only": semantic_authority[
            "semantic_pipeline_recommends_only"
        ],
        "reuse_score_advisory_only": semantic_authority[
            "reuse_score_advisory_only"
        ],
        "architect_does_not_answer_user": not first_sections["architect"][
            "architect_created_final_output"
        ],
        "executor_does_not_create_final_output": not first_sections[
            "dag_runner"
        ]["executor_created_final_output"],
        "gt_does_not_create_final_output": not first_sections["post_vv_gt"][
            "gt_committed_final_output"
        ],
        "production_direct_reuse_executed": semantic_authority[
            "production_direct_reuse_executed"
        ],
        "production_final_output_created": False,
        "production_work_record_written": False,
        "production_external_action_executed": False,
        "no_real_external_actions": first_sections["dag_runner"][
            "no_real_external_action"
        ]
        and semantic_authority["no_real_external_actions"],
        "no_live_gemini": semantic_authority["no_live_gemini"],
        "no_telegram_actions": semantic_authority["no_telegram_actions"],
        "no_global_drs": semantic_authority["no_global_drs"],
        "no_external_drs_network": semantic_authority["no_external_drs_network"],
        "production_autonomy_claimed": semantic_authority[
            "production_autonomy_claimed"
        ],
        "deterministic_bridge_between_runs": bridge["bridge_mode"]
        == "deterministic_proof_linkage",
    }


def _summary(
    first_run_stages: list[FullCanonicalE2EStage],
    second_run_stages: list[FullCanonicalE2EStage],
    selected_path: FullCanonicalE2ESelectedPath,
    bridge: dict[str, Any],
    artifacts: dict[str, Any],
    authority: dict[str, Any],
    semantic: RootNativeSemanticReuseE2EReport,
) -> dict[str, Any]:
    first_passed = _stage_pass_count(first_run_stages)
    second_passed = _stage_pass_count(second_run_stages)
    pass_status = (
        first_passed == 9
        and second_passed == 12
        and selected_path.scenario == "eligible_direct_reuse_candidate"
        and selected_path.root_final_decision
        == "root_final_accepts_controlled_direct_reuse_trace"
        and artifacts["second_run_artifact_created_by"] == "root_orchestrator"
        and bridge["first_run_created_root_trace_artifact"]
        and bridge["first_run_local_drs_writeback_visible"]
        and bridge["first_run_local_work_record_written_in_proof"]
        and bridge["bridge_mode"] == "deterministic_proof_linkage"
        and not bridge["production_persistence_claimed"]
        and not bridge["production_reuse_claimed"]
        and authority["root_authority_preserved_first_run"]
        and authority["root_authority_preserved_second_run"]
        and authority["reuse_gate_boundary_preserved"]
        and authority["semantic_pipeline_recommends_only"]
        and authority["reuse_score_advisory_only"]
        and authority["architect_does_not_answer_user"]
        and authority["executor_does_not_create_final_output"]
        and authority["gt_does_not_create_final_output"]
        and not authority["production_direct_reuse_executed"]
        and not authority["production_final_output_created"]
        and not authority["production_work_record_written"]
        and not authority["production_external_action_executed"]
        and authority["no_real_external_actions"]
        and authority["no_live_gemini"]
        and authority["no_telegram_actions"]
        and authority["no_global_drs"]
        and authority["no_external_drs_network"]
        and not authority["production_autonomy_claimed"]
    )
    semantic_source_summary = semantic.summary
    return {
        "root_native_full_canonical_e2e_trace_status": (
            "PASS" if pass_status else "FAIL"
        ),
        "first_run_stages_passed": first_passed,
        "second_run_stages_passed": second_passed,
        "first_run_root_authority_preserved": authority[
            "root_authority_preserved_first_run"
        ],
        "second_run_root_authority_preserved": authority[
            "root_authority_preserved_second_run"
        ],
        "semantic_reuse_path_used": selected_path.scenario
        == "eligible_direct_reuse_candidate",
        "deterministic_bridge_between_runs": bridge["bridge_mode"]
        == "deterministic_proof_linkage",
        "production_reuse_claimed": bridge["production_reuse_claimed"],
        "production_direct_reuse_executed": authority[
            "production_direct_reuse_executed"
        ],
        "production_final_output_created": authority[
            "production_final_output_created"
        ],
        "production_external_action_executed": authority[
            "production_external_action_executed"
        ],
        "production_work_record_written": authority["production_work_record_written"],
        "production_persistence_claimed": bridge["production_persistence_claimed"],
        "local_drs_only": semantic_source_summary["local_drs_only"],
        "external_drs_network_implemented": semantic_source_summary[
            "external_drs_network_implemented"
        ],
        "global_drs_implemented": semantic_source_summary[
            "global_drs_implemented"
        ],
        "ready_for_optional_live_gemini_smoke_later": pass_status,
    }


def collect_root_native_full_canonical_e2e_trace() -> (
    RootNativeFullCanonicalE2EReport
):
    first_run_source = collect_canonical_trace()
    second_run_source = collect_root_native_semantic_reuse_e2e_trace()
    first_run_stages = _first_run_stages(first_run_source)
    second_run_stages = _second_run_stages(second_run_source)
    selected_path = _selected_path(second_run_source)
    bridge = _bridge(first_run_source, second_run_source)
    artifacts = _final_artifacts(second_run_source)
    authority = _authority_safety(first_run_source, second_run_source, bridge)
    summary = _summary(
        first_run_stages,
        second_run_stages,
        selected_path,
        bridge,
        artifacts,
        authority,
        second_run_source,
    )
    return RootNativeFullCanonicalE2EReport(
        first_run_source=first_run_source,
        second_run_source=second_run_source,
        input_tasks=_input_tasks(),
        first_run_stages=first_run_stages,
        second_run_stages=second_run_stages,
        selected_scenario_path=selected_path,
        bridge_between_runs=bridge,
        final_artifacts=artifacts,
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


def _dataclass_fields(instance: Any) -> dict[str, Any]:
    return {
        key: getattr(instance, key)
        for key in instance.__dataclass_fields__
    }


def _stage_line(stage: FullCanonicalE2EStage) -> str:
    return f"{stage.stage} | {stage.status} | {stage.key_proof} | {stage.source}"


def render_root_native_full_canonical_e2e_trace(
    report: RootNativeFullCanonicalE2EReport,
) -> str:
    lines = [
        "[ROOT-NATIVE FULL CANONICAL E2E TRACE]",
        "note: deterministic full canonical E2E proof",
        "note: first run uses canonical Root-controlled path",
        "note: second run uses semantic reuse authority path",
        "note: no production RootOrchestrator behavior change",
        "note: no production direct reuse execution",
        "note: no production external action",
        "note: no live Gemini",
        "note: no Telegram actions",
        "note: no global DRS",
        "note: no external DRS network",
        "note: Root remains final authority",
        "note: ReuseGate guards reuse",
        "note: semantic pipeline recommends only",
        "",
        "[INPUT TASKS]",
    ]
    lines.extend(_field_lines(report.input_tasks))
    lines.extend(
        [
            "",
            "[FIRST RUN CANONICAL PATH]",
            "stage | status | key proof | source",
            "--- | --- | --- | ---",
        ]
    )
    lines.extend(_stage_line(stage) for stage in report.first_run_stages)
    lines.extend(
        [
            "",
            "[SECOND RUN SEMANTIC REUSE PATH]",
            "stage | status | key proof | source",
            "--- | --- | --- | ---",
        ]
    )
    lines.extend(_stage_line(stage) for stage in report.second_run_stages)
    lines.extend(["", "[BRIDGE BETWEEN RUNS]"])
    lines.extend(_field_lines(report.bridge_between_runs))
    lines.extend(["", "[FINAL ARTIFACTS]"])
    lines.extend(_field_lines(report.final_artifacts))
    lines.extend(["", "[AUTHORITY / SAFETY]"])
    lines.extend(_field_lines(report.authority_safety))
    lines.extend(["", "[SUMMARY]"])
    lines.extend(_field_lines(report.summary))
    return "\n".join(lines).rstrip() + "\n"


def run_root_native_full_canonical_e2e_trace() -> str:
    return render_root_native_full_canonical_e2e_trace(
        collect_root_native_full_canonical_e2e_trace()
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run Root-native Full Canonical E2E Trace proof."
    )
    parser.parse_args()
    print(run_root_native_full_canonical_e2e_trace(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
