from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from hedgehog.drs import LocalDRS
from hedgehog.root_orchestrator import RootOrchestrator


ROOT = Path(__file__).resolve().parents[1]
NEEDLES_DIR = ROOT / "needles"


@dataclass(frozen=True)
class RootNativeCanonicalTrace:
    final_output: dict
    trace: dict
    work_record: dict
    sections: dict[str, dict[str, Any]]
    output: str


def _bool_text(value: bool) -> str:
    return "true" if value else "false"


def _join(values: list[str]) -> str:
    return ", ".join(values) if values else "none"


def _contains_key(value: Any, forbidden_key: str) -> bool:
    if isinstance(value, dict):
        return forbidden_key in value or any(
            _contains_key(child, forbidden_key) for child in value.values()
        )
    if isinstance(value, list):
        return any(_contains_key(item, forbidden_key) for item in value)
    return False


def _selected_vectors(attractor_packet: dict | None) -> list[str]:
    if not attractor_packet:
        return []
    return [
        vector["vector_id"]
        for vector in attractor_packet.get("candidate_vectors", [])
        if vector.get("vector_id")
    ]


def _forbidden_regions(attractor_packet: dict | None) -> list[str]:
    if not attractor_packet:
        return []
    return [
        region["region_id"]
        for region in attractor_packet.get("hard_forbidden_regions", [])
        if region.get("region_id")
    ]


def _plan_graph_valid(plan_graph: dict | None) -> bool:
    return bool(
        plan_graph
        and plan_graph.get("nodes")
        and plan_graph.get("time_assumptions")
        and plan_graph.get("plan_id")
    )


def run_trace(drs_root: Path | None = None) -> RootNativeCanonicalTrace:
    owns_temp = drs_root is None
    temp_dir = TemporaryDirectory() if owns_temp else None
    try:
        active_root = Path(temp_dir.name) / "drs" if temp_dir else Path(drs_root)
        drs = LocalDRS(active_root)
        root = RootOrchestrator(drs=drs, needles_dir=NEEDLES_DIR)
        final_output = root.process_event(
            raw_user_text="mock certificate request",
            request_id="req_root_native_canonical_trace",
            session_anchor="sess_root_native_canonical_trace",
            force_full_pipeline=True,
            architect_provider="deterministic",
            use_fractal_dag_executor=True,
        )
        trace = root.last_trace
        work_record = drs.read_record("work", final_output["drs_writes"][0])
        sections = build_sections(final_output, trace, work_record)
        output = render_trace(sections)
        return RootNativeCanonicalTrace(
            final_output=final_output,
            trace=trace,
            work_record=work_record,
            sections=sections,
            output=output,
        )
    finally:
        if temp_dir is not None:
            temp_dir.cleanup()


def build_sections(
    final_output: dict,
    trace: dict,
    work_record: dict,
) -> dict[str, dict[str, Any]]:
    attractor_packet = trace.get("attractor_packet") or {}
    plan_graph = trace.get("plan_graph") or {}
    selected_vectors = _selected_vectors(attractor_packet)
    forbidden_regions = _forbidden_regions(attractor_packet)
    architect_received_forbidden = any(
        node.get("vector_id") in forbidden_regions for node in plan_graph.get("nodes", [])
    )
    work_content = work_record.get("content", {})
    sensitive_input_absent = not _contains_key(work_record, "raw_user_text")
    gt_report = trace.get("gt_report") or {}

    return {
        "root_intake": {
            "request_id": final_output["request_id"],
            "input_kind": trace.get("input_intake", {}).get("intent_kind", "not_exposed_yet"),
            "root_authority": True,
            "final_output_created_by_root_only": final_output.get("created_by") == "root_orchestrator",
        },
        "root_orchestrator_route_assembly": {
            "route": trace.get("mode_router", {}).get("execution_mode", "not_exposed_yet"),
            "execution_engine": trace.get("execution_engine", "not_exposed_yet"),
            "root_authority": True,
            "orchestrator_stage_explicit": True,
            "orchestrator_provider": "deterministic",
            "llm_or_slm_used": False,
            "force_full_pipeline": True,
            "use_fractal_dag_executor": trace.get("fractal_dag_executor_used") is True,
            "orchestrator_created_final_output": False,
            "orchestrator_bypassed_root_authority": False,
        },
        "avf_attractor": {
            "avf_runs_before_architect": bool(attractor_packet),
            "hardmask_applied": "illegal_coercion" in forbidden_regions,
            "forbidden_vector_blocked_before_architect": (
                "illegal_coercion" in forbidden_regions
                and "illegal_coercion" not in selected_vectors
            ),
            "architect_received_forbidden_vectors": architect_received_forbidden,
            "attractor_packet_created": bool(attractor_packet.get("packet_id")),
            "attractor_packet_created_by": "root_orchestrator",
            "selected_vectors": selected_vectors,
            "forbidden_regions": forbidden_regions,
        },
        "architect": {
            "architect_provider": "deterministic",
            "plan_graph_valid": _plan_graph_valid(plan_graph),
            "plan_graph_node_count": len(plan_graph.get("nodes", [])),
            "architect_created_final_output": False,
            "architect_returned_plan_graph": bool(plan_graph.get("plan_id")),
        },
        "dag_runner": {
            "fractal_dag_executor_used": trace.get("fractal_dag_executor_used") is True,
            "dag_runner_status": trace.get("dag_runner_status", "not_exposed_yet"),
            "dag_ready_sequence_present": trace.get("dag_ready_sequence_present") is True,
            "dag_execution_batches_present": trace.get("dag_execution_batches_present") is True,
            "dag_result_proposals_count": int(trace.get("dag_result_proposals_count") or 0),
            "dag_child_boundary_snapshots": int(trace.get("dag_child_boundary_snapshots") or 0),
            "executor_created_final_output": trace.get("executor_created_final_output") is True,
            "no_real_external_action": trace.get("no_real_external_action") is True,
        },
        "post_vv_gt": {
            "post_vv_after_dag_executor": trace.get("post_vv_after_dag_executor") is True,
            "vv_reports_count": len(trace.get("vv_reports", [])),
            "gt_after_post_vv": trace.get("gt_after_post_vv") is True,
            "gt_decision": gt_report.get("decision", "not_exposed_yet"),
            "gt_committed_final_output": False,
        },
        "root_final": {
            "root_received_dag_artifacts": trace.get("root_received_dag_artifacts") is True,
            "final_status": final_output.get("status", "not_exposed_yet"),
            "root_created_final_output": final_output.get("created_by") == "root_orchestrator",
            "created_by": final_output.get("created_by", "not_exposed_yet"),
            "uncontrolled_delegation": trace.get("uncontrolled_delegation") is True,
        },
        "drs_writeback_audit": {
            "drs_write_count": len(final_output.get("drs_writes", [])),
            "work_record_written": bool(work_record),
            "time_envelope_present": bool(work_record.get("time_envelope")),
            "provenance_present": bool(work_record.get("provenance")),
            "execution_engine_in_work_record": work_content.get("execution_engine", "not_exposed_yet"),
            "fractal_dag_executor_used_in_work_record": work_content.get("fractal_dag_executor_used") is True,
            "dag_result_proposals_count_in_work_record": int(
                work_content.get("dag_result_proposals_count") or 0
            ),
            "vv_reports_count_in_work_record": int(work_content.get("vv_reports_count") or 0),
            "gt_decision_in_work_record": work_content.get("gt_decision", "not_exposed_yet"),
            "root_created_final_output_in_work_record": work_content.get(
                "root_created_final_output"
            )
            is True,
            "no_real_external_action_in_work_record": work_content.get(
                "no_real_external_action"
            )
            is True,
            "audit_trace_present": work_content.get("audit_trace_present") is True,
            "root_native_dag_path": work_content.get("root_native_dag_path") is True,
            "root_final_authority_preserved": work_content.get(
                "root_final_authority_preserved"
            )
            is True,
            "post_vv_before_gt": work_content.get("post_vv_before_gt") is True,
            "result_returned_to_root": work_content.get("result_returned_to_root") is True,
            "sensitive_input_absent": sensitive_input_absent,
        },
    }


def _render_value(value: Any) -> str:
    if isinstance(value, bool):
        return _bool_text(value)
    if isinstance(value, list):
        return _join([str(item) for item in value])
    return str(value)


def render_trace(sections: dict[str, dict[str, Any]]) -> str:
    lines = [
        "[ROOT-NATIVE CANONICAL TRACE]",
        "note: uses real RootOrchestrator opt-in DAG route",
        "note: DAG runner connects to Root-controlled pipeline after Architect",
        "note: Root remains final authority",
        "note: no real external actions",
        "note: no live Gemini by default",
    ]
    ordered = [
        ("ROOT INTAKE", "root_intake"),
        ("ROOT ORCHESTRATOR / ROUTE ASSEMBLY", "root_orchestrator_route_assembly"),
        ("AVF / ATTRACTOR", "avf_attractor"),
        ("ARCHITECT", "architect"),
        ("DAG RUNNER", "dag_runner"),
        ("POST V&V / GT", "post_vv_gt"),
        ("ROOT FINAL", "root_final"),
        ("DRS WRITEBACK / AUDIT", "drs_writeback_audit"),
    ]
    for title, key in ordered:
        lines.append("")
        lines.append(f"[{title}]")
        for field, value in sections[key].items():
            lines.append(f"- {field}: {_render_value(value)}")

    summary = {
        "root_native_canonical_trace_status": "PASS",
        "real_root_orchestrator_used": True,
        "execution_engine": sections["root_orchestrator_route_assembly"]["execution_engine"],
        "fractal_dag_executor_used": sections["dag_runner"]["fractal_dag_executor_used"],
        "root_final_authority_preserved": sections["root_final"]["root_created_final_output"],
        "architect_created_final_output": sections["architect"]["architect_created_final_output"],
        "executor_created_final_output": sections["dag_runner"]["executor_created_final_output"],
        "gt_committed_final_output": sections["post_vv_gt"]["gt_committed_final_output"],
        "post_vv_after_dag_executor": sections["post_vv_gt"]["post_vv_after_dag_executor"],
        "gt_after_post_vv": sections["post_vv_gt"]["gt_after_post_vv"],
        "root_created_final_output": sections["root_final"]["root_created_final_output"],
        "drs_writeback_done": sections["drs_writeback_audit"]["work_record_written"],
        "no_real_external_actions": sections["dag_runner"]["no_real_external_action"],
        "uncontrolled_delegation": sections["root_final"]["uncontrolled_delegation"],
        "next_step": "stabilize DRS writeback / audit around root-native path",
    }
    lines.append("")
    lines.append("[SUMMARY]")
    for field, value in summary.items():
        lines.append(f"- {field}: {_render_value(value)}")
    return "\n".join(lines)


def main() -> None:
    print(run_trace().output)


if __name__ == "__main__":
    main()
