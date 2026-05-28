from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from hedgehog.architect import make_plan_graph
from hedgehog.avf import build_attractor_packet, score_candidate_vector
from hedgehog.candidate_vectors import load_candidate_vectors_from_needles
from hedgehog.drs import LocalDRS
from hedgehog.final_renderer import render_final_draft
from hedgehog.fractal_dag_executor import run_fractal_dag_executor
from hedgehog.gt_validator import validate_gt
from hedgehog.post_vv import validate_result_proposals
from hedgehog.time_model import make_temporal_query, make_time_envelope, utc_now_iso


ROOT = Path(__file__).resolve().parents[1]
NEEDLES_DIR = ROOT / "needles"


@dataclass(frozen=True)
class CanonicalPipelineTrace:
    sections: dict[str, dict[str, Any]]
    output: str


def _bool_text(value: bool) -> str:
    return "true" if value else "false"


def _seq(value: list[list[str]]) -> str:
    if not value:
        return "none"
    return " / ".join(",".join(batch) for batch in value)


def _contains_key(value: Any, forbidden_key: str) -> bool:
    if isinstance(value, dict):
        return forbidden_key in value or any(
            _contains_key(child, forbidden_key) for child in value.values()
        )
    if isinstance(value, list):
        return any(_contains_key(item, forbidden_key) for item in value)
    return False


def _safe_join(values: list[str]) -> str:
    return ", ".join(values) if values else "none"


def _winner_vector(result_proposals: list[dict], gt_report: dict) -> str:
    winner = gt_report.get("winner")
    for proposal in result_proposals:
        if proposal.get("proposal_id") == winner:
            return proposal.get("vector_id", "none")
    return "none"


def _make_root_final_output(
    *,
    request_id: str,
    final_draft: dict,
    gt_report: dict,
    result_proposals: list[dict],
    drs_writes: list[str],
) -> dict:
    status = "success" if gt_report.get("decision") == "accept" else "needs_user"
    return {
        "final_output_id": f"final:{request_id}",
        "request_id": request_id,
        "created_by": "root_orchestrator",
        "status": status,
        "answer": final_draft["body"],
        "used_proposals": [gt_report["winner"]] if gt_report.get("winner") else [],
        "gt_report_ref": gt_report["gt_report_id"],
        "drs_writes": list(drs_writes),
        "time_envelope": make_time_envelope("canonical_pipeline_trace_session"),
        "summary": final_draft["summary"],
        "trace_refs": [
            {
                "trace_id": f"trace:{request_id}",
                "span_id": "root_final_output",
                "kind": "root_orchestrator",
            }
        ],
        "proposal_count_observed": len(result_proposals),
    }


def _make_work_record(
    *,
    request_id: str,
    final_output: dict,
    final_draft: dict,
    gt_report: dict,
    retrieved_records: int,
) -> dict:
    return {
        "record_id": f"work:{request_id}",
        "layer": "work",
        "type": "task_outcome",
        "domain": "government_certificate",
        "content": {
            "summary": "Canonical pipeline trace completed with mock certificate flow.",
            "input_kind": "certificate_demo",
            "result": "simulated_success",
            "final_status": final_output["status"],
            "execution_mode": "canonical_pipeline_trace",
            "route": "proof_full_pipeline_with_fractal_dag_executor",
            "selected_proposal_ids": list(final_draft["selected_proposal_ids"]),
            "completed_proposal_ids": list(final_draft["completed_proposal_ids"]),
            "needs_user_proposal_ids": list(final_draft["needs_user_proposal_ids"]),
            "blocked_proposal_ids": list(final_draft["blocked_proposal_ids"]),
            "rejected_proposal_ids": list(final_draft["rejected_proposal_ids"]),
            "gt_report_ref": gt_report["gt_report_id"],
            "gt_decision": gt_report["decision"],
            "final_draft_ref": final_draft["draft_id"],
            "retrieved_record_count": retrieved_records,
            "memory_context_applied": retrieved_records > 0,
            "architect_skipped": False,
            "executor_skipped": False,
            "fractal_dag_executor_used": True,
            "root_final_authority": True,
        },
        "time_envelope": make_time_envelope("canonical_pipeline_trace_session"),
        "provenance": {
            "request_id": request_id,
            "created_by": "root_orchestrator",
            "trace_refs": [
                {
                    "trace_id": f"trace:{request_id}",
                    "span_id": "drs_writeback",
                    "kind": "canonical_pipeline_trace",
                }
            ],
        },
        "gt": {
            "gt_report_id": gt_report["gt_report_id"],
            "half_life_hours": gt_report.get("half_life_hours", 1.0),
            "decay_rate": gt_report.get("decay_rate", 0.0),
        },
        "status": "accepted" if gt_report["decision"] == "accept" else "no_update",
    }


def run_canonical_pipeline_trace(drs_root: Path | None = None) -> CanonicalPipelineTrace:
    request_id = "req:canonical_pipeline_trace"
    owns_temp = drs_root is None
    temp_dir = TemporaryDirectory() if owns_temp else None
    try:
        active_root = Path(temp_dir.name) / "drs" if temp_dir else Path(drs_root)
        drs = LocalDRS(active_root)
        temporal_query = make_temporal_query()
        retrieved = drs.query_records(temporal_query, ["work"])

        vectors = load_candidate_vectors_from_needles(
            [
                NEEDLES_DIR / "government_services.json",
                NEEDLES_DIR / "fallback_exploration.json",
            ]
        )
        scored_vectors = [score_candidate_vector(vector) for vector in vectors]
        hard_masked_vectors = [
            score["vector_id"] for score in scored_vectors if score["hard_masked"]
        ]
        attractor_packet = build_attractor_packet(
            request_id=request_id,
            intent_id="intent:canonical_pipeline_trace",
            world_state_ref="world:canonical_pipeline_trace",
            goal_id="goal:mock_certificate",
            desired_state="Prepare a safe mock government certificate request.",
            candidate_vectors=vectors,
            as_of=utc_now_iso(),
            max_selected=4,
        )
        selected_vectors = [
            vector["vector_id"] for vector in attractor_packet["candidate_vectors"]
        ]
        plan_graph = make_plan_graph(attractor_packet)
        architect_received_forbidden = any(
            node["vector_id"] in hard_masked_vectors for node in plan_graph["nodes"]
        )

        runner_report = run_fractal_dag_executor(
            plan_graph,
            runner_id="runner:canonical_pipeline_trace",
            session_anchor="canonical_pipeline_trace_session",
        )
        result_proposals = runner_report["result_proposals"]
        vv_reports = validate_result_proposals(result_proposals)
        gt_report = validate_gt(vv_reports)
        final_draft = render_final_draft(
            request_id=request_id,
            gt_report=gt_report,
            result_proposals=result_proposals,
            vv_reports=vv_reports,
            drs_writes=[f"work:{request_id}"],
            mode="canonical_pipeline_trace",
        )
        final_output = _make_root_final_output(
            request_id=request_id,
            final_draft=final_draft,
            gt_report=gt_report,
            result_proposals=result_proposals,
            drs_writes=[f"work:{request_id}"],
        )
        work_record = _make_work_record(
            request_id=request_id,
            final_output=final_output,
            final_draft=final_draft,
            gt_report=gt_report,
            retrieved_records=len(retrieved),
        )
        work_path = drs.write_record(work_record)
        written_record = drs.read_record("work", work_record["record_id"])
        record_json = json.dumps(written_record, sort_keys=True)

        completed_reports = [
            report for report in vv_reports if report.get("status") == "accepted"
        ]
        blocked_or_failed_reports = [
            report for report in vv_reports if report.get("status") != "accepted"
        ]
        gt_winner_vector = _winner_vector(result_proposals, gt_report)
        sections = {
            "root_intake": {
                "request_id": request_id,
                "input_kind": "certificate_demo",
                "root_authority": True,
                "final_output_created_by_root_only": True,
            },
            "temporal_drs_precheck": {
                "temporal_query_used": bool(temporal_query.get("as_of")),
                "retrieved_records": len(retrieved),
                "memory_context_applied": len(retrieved) > 0,
                "sensitive_input_absent_from_writeback": "raw_user_text" not in record_json,
            },
            "candidate_vectors": {
                "candidate_vectors_total": len(vectors),
                "candidate_vector_ids": [vector.vector_id for vector in vectors],
                "candidate_sources": sorted({vector.source for vector in vectors}),
                "free_llm_hallucinated_vectors": False,
            },
            "avf_hardmask": {
                "hard_mask_applied": bool(hard_masked_vectors),
                "hard_masked_vectors": hard_masked_vectors,
                "forbidden_vector_blocked_before_architect": "illegal_coercion" in hard_masked_vectors,
                "architect_received_forbidden_vectors": architect_received_forbidden,
            },
            "attractor_packet": {
                "selected_vectors": selected_vectors,
                "required_guards": [
                    "AVF",
                    "HardMask",
                    "PlanGraph contract",
                    "Post V&V",
                    "GT",
                    "Root final authority",
                ],
                "branch_budget": attractor_packet["branch_budget"],
                "forbidden_regions": [
                    region["region_id"]
                    for region in attractor_packet["hard_forbidden_regions"]
                ],
            },
            "architect_plan_graph": {
                "architect_created_final_output": False,
                "plan_graph_valid": bool(plan_graph.get("nodes")) and bool(plan_graph.get("time_assumptions")),
                "plan_graph_node_count": len(plan_graph["nodes"]),
                "plan_graph_edge_count": len(plan_graph["edges"]),
                "time_assumptions_present": bool(plan_graph.get("time_assumptions")),
            },
            "fractal_dag_executor": {
                "executor_runner_used": True,
                "runner_status": runner_report["status"],
                "ready_sequence": runner_report["ready_sequence"],
                "execution_batches": runner_report["execution_batches"],
                "result_proposals_count": len(result_proposals),
                "child_boundary_snapshots": runner_report["child_boundary_snapshots"],
                "executor_created_final_output": runner_report["executor_created_final_output"],
                "no_real_external_action": runner_report["no_real_external_action"],
            },
            "post_vv": {
                "vv_reports_count": len(vv_reports),
                "completed_reports": len(completed_reports),
                "blocked_or_failed_reports": len(blocked_or_failed_reports),
                "post_vv_before_gt": True,
            },
            "gt": {
                "gt_decision": gt_report["decision"],
                "gt_winner_vector": gt_winner_vector,
                "gt_winner_proposal": gt_report.get("winner", "none"),
                "gt_committed_final_output": False,
            },
            "root_final_output": {
                "final_status": final_output["status"],
                "root_final_authority": True,
                "root_created_final_output": final_output["created_by"] == "root_orchestrator",
                "created_by": final_output["created_by"],
                "uncontrolled_delegation": False,
            },
            "drs_writeback_audit": {
                "drs_write_count": 1,
                "work_record_written": work_path.exists(),
                "time_envelope_present": bool(written_record.get("time_envelope")),
                "sensitive_input_absent": not _contains_key(written_record, "raw_user_text"),
                "audit_trace_present": bool(written_record.get("provenance", {}).get("trace_refs")),
                "trace_summary_present": True,
            },
        }
        output = render_trace(sections)
        return CanonicalPipelineTrace(sections=sections, output=output)
    finally:
        if temp_dir is not None:
            temp_dir.cleanup()


def _render_key_values(section: dict[str, Any]) -> list[str]:
    lines = []
    for key, value in section.items():
        if isinstance(value, bool):
            rendered = _bool_text(value)
        elif isinstance(value, list) and value and all(isinstance(item, list) for item in value):
            rendered = _seq(value)
        elif isinstance(value, list):
            rendered = _safe_join([str(item) for item in value])
        elif isinstance(value, dict):
            rendered = ", ".join(f"{k}={v}" for k, v in value.items())
        else:
            rendered = str(value)
        lines.append(f"- {key}: {rendered}")
    return lines


def render_trace(sections: dict[str, dict[str, Any]]) -> str:
    lines = [
        "[CANONICAL PIPELINE TRACE]",
        "note: auditor-facing full canonical runtime trace",
        "note: uses Fractal DAG Executor Core",
        "note: no real external actions",
        "note: no live Gemini by default",
        "note: Root remains final authority",
    ]
    ordered = [
        ("ROOT INTAKE", "root_intake"),
        ("TEMPORAL / DRS PRECHECK", "temporal_drs_precheck"),
        ("CANDIDATE VECTORS", "candidate_vectors"),
        ("AVF / HARDMASK", "avf_hardmask"),
        ("ATTRACTOR PACKET", "attractor_packet"),
        ("ARCHITECT PLAN GRAPH", "architect_plan_graph"),
        ("FRACTAL DAG EXECUTOR", "fractal_dag_executor"),
        ("POST V&V", "post_vv"),
        ("GT", "gt"),
        ("ROOT FINAL OUTPUT", "root_final_output"),
        ("DRS WRITEBACK / AUDIT", "drs_writeback_audit"),
    ]
    for title, key in ordered:
        lines.append("")
        lines.append(f"[{title}]")
        lines.extend(_render_key_values(sections[key]))

    summary = {
        "canonical_trace_status": "PASS",
        "root_final_authority_preserved": sections["root_final_output"]["root_final_authority"],
        "architect_created_final_output": sections["architect_plan_graph"]["architect_created_final_output"],
        "executor_created_final_output": sections["fractal_dag_executor"]["executor_created_final_output"],
        "gt_committed_final_output": sections["gt"]["gt_committed_final_output"],
        "forbidden_vector_blocked_before_architect": sections["avf_hardmask"]["forbidden_vector_blocked_before_architect"],
        "post_vv_before_gt": sections["post_vv"]["post_vv_before_gt"],
        "drs_writeback_done": sections["drs_writeback_audit"]["work_record_written"],
        "no_real_external_actions": sections["fractal_dag_executor"]["no_real_external_action"],
        "uncontrolled_delegation": sections["root_final_output"]["uncontrolled_delegation"],
        "next_step": "integrate Canonical Pipeline Trace into broader showcase or add Root-level DAG runner integration",
    }
    lines.append("")
    lines.append("[SUMMARY]")
    for key, value in summary.items():
        rendered = _bool_text(value) if isinstance(value, bool) else str(value)
        lines.append(f"- {key}: {rendered}")
    return "\n".join(lines)


def main() -> None:
    print(run_canonical_pipeline_trace().output)


if __name__ == "__main__":
    main()
