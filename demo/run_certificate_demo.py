from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

from hedgehog.drs import LocalDRS
from hedgehog.root_orchestrator import RootOrchestrator
from hedgehog.time_model import make_time_envelope


ROOT = Path(__file__).resolve().parents[1]
NEEDLES_DIR = ROOT / "needles"


def _bool_text(value: bool) -> str:
    return "true" if value else "false"


def _winner_vector_id(trace: dict) -> tuple[str, str]:
    gt_report = trace.get("gt_report") or {}
    winner_proposal_id = gt_report.get("winner")
    if not winner_proposal_id:
        return "none", "none"

    for proposal in trace["result_proposals"]:
        if proposal["proposal_id"] == winner_proposal_id:
            return winner_proposal_id, proposal["vector_id"]
    return winner_proposal_id, "none"


def _reuse_gate_lines(trace: dict) -> list[str]:
    reuse_gate = trace.get("reuse_gate", {})
    candidate_scores = reuse_gate.get("candidate_scores", [])
    best_record_id = reuse_gate.get("best_record_id")
    best_score = "none"
    best_reason = "none"
    for score in candidate_scores:
        if score.get("record_id") == best_record_id:
            best_score = str(score["reuse_score"])
            best_reason = score["reason"]
            break

    reused_record_ids = trace.get("reused_record_ids") or reuse_gate.get("reused_record_ids", [])
    return [
        f"  reuse_gate decision: {reuse_gate.get('reuse_decision', 'none')}",
        f"  reuse_score_best: {best_score}",
        f"  reuse_candidate_record_id: {best_record_id or 'none'}",
        f"  reuse_gate reason: {best_reason}",
        f"  reused_record_ids: {', '.join(reused_record_ids) if reused_record_ids else 'none'}",
    ]


def _summarize_run(label: str, orchestrator: RootOrchestrator, final_output: dict) -> list[str]:
    trace = orchestrator.last_trace
    attractor_packet = trace.get("attractor_packet")
    plan_graph = trace.get("plan_graph")
    selected_vector_ids = []
    if attractor_packet:
        selected_vector_ids = [
            vector["vector_id"]
            for vector in attractor_packet["candidate_vectors"]
        ]
    plan_nodes = plan_graph["nodes"] if plan_graph else []
    plan_node_vector_ids = [node["vector_id"] for node in plan_nodes]
    accepted_count = sum(
        1 for report in trace["vv_reports"] if report["decision"] == "accept"
    )
    illegal_blocked = (
        "illegal_coercion" not in selected_vector_ids
        and "illegal_coercion" not in plan_node_vector_ids
    )
    winner_proposal_id, winner_vector_id = _winner_vector_id(trace)

    lines = [
        f"{label}:",
        f"  retrieved_record_count: {trace['retrieved_record_count']}",
        f"  memory_context_applied: {_bool_text(trace['memory_context_applied'])}",
        f"  reuse_decision: {trace['reuse_decision']}",
        f"  reuse_applied: {_bool_text(trace['reuse_applied'])}",
        *_reuse_gate_lines(trace),
        f"  architect_skipped: {_bool_text(trace.get('architect_skipped', False))}",
        f"  executor_skipped: {_bool_text(trace.get('executor_skipped', False))}",
        f"  AVF selected vector ids: {', '.join(selected_vector_ids)}",
        f"  illegal_coercion blocked: {_bool_text(illegal_blocked)}",
        f"  PlanGraph node count: {len(plan_nodes)}",
        f"  ResultProposal count: {len(trace['result_proposals'])}",
        f"  Post V&V accepted count: {accepted_count}",
        f"  GT decision: {(trace.get('gt_report') or {}).get('decision', 'none')}",
        f"  GT winner proposal id: {winner_proposal_id}",
        f"  GT winner vector id: {winner_vector_id}",
        f"  FinalOutput created_by: {final_output['created_by']}",
        f"  FinalOutput status: {final_output['status']}",
        f"  DRS writes: {', '.join(final_output['drs_writes'])}",
    ]
    if trace.get("marenna_records") or trace.get("up_records"):
        lines.extend(
            [
                f"  Marennya quarantine records: {', '.join(trace.get('marenna_records', []))}",
                f"  UP quarantine records: {', '.join(trace.get('up_records', []))}",
            ]
        )
    return lines


def _run_once(orchestrator: RootOrchestrator, request_id: str, session_anchor: str) -> dict:
    return orchestrator.process_event(
        raw_user_text="mock certificate request",
        request_id=request_id,
        session_anchor=session_anchor,
    )


def _seed_direct_reuse_record(drs: LocalDRS) -> None:
    drs.write_record(
        {
            "record_id": "work:demo_direct_reuse_source",
            "layer": "work",
            "type": "task_outcome",
            "domain": "government_certificate",
            "content": {
                "summary": "Strong prior mock certificate outcome."
            },
            "time_envelope": make_time_envelope("demo_direct_reuse_source_session"),
            "provenance": {
                "request_id": "demo_direct_reuse_source",
                "created_by": "root_orchestrator",
                "trace_refs": [],
            },
            "gt": {
                "gt_report_id": "gt:demo:direct_reuse_source",
                "half_life_hours": 2_000.0,
                "decay_rate": 0.0001,
            },
            "status": "accepted",
        }
    )


def run_demo(scenario: str, drs_root: Path | None = None) -> str:
    if scenario not in {"cold_start", "reuse", "direct_reuse"}:
        raise ValueError(f"unknown scenario: {scenario}")

    def run_with_root(root_path: Path) -> str:
        drs = LocalDRS(root_path)
        orchestrator = RootOrchestrator(drs=drs, needles_dir=NEEDLES_DIR)
        lines = [f"Scenario: {scenario}"]

        if scenario == "cold_start":
            final_output = _run_once(
                orchestrator,
                request_id="demo_cold_start_001",
                session_anchor="demo_cold_start_session",
            )
            lines.extend(_summarize_run("run", orchestrator, final_output))
        elif scenario == "reuse":
            first_output = _run_once(
                orchestrator,
                request_id="demo_reuse_001",
                session_anchor="demo_reuse_session_001",
            )
            lines.extend(_summarize_run("first_run", orchestrator, first_output))
            second_output = _run_once(
                orchestrator,
                request_id="demo_reuse_002",
                session_anchor="demo_reuse_session_002",
            )
            lines.extend(_summarize_run("second_run", orchestrator, second_output))
            lines.append("  direct reuse implemented: false")
            lines.append("  note: context_only memory use still runs Architect and Executor.")
        else:
            _seed_direct_reuse_record(drs)
            final_output = orchestrator.process_event(
                raw_user_text="mock certificate request",
                request_id="demo_direct_reuse_001",
                session_anchor="demo_direct_reuse_session",
                allow_direct_reuse=True,
            )
            lines.extend(_summarize_run("run", orchestrator, final_output))

        return "\n".join(lines) + "\n"

    if drs_root is not None:
        return run_with_root(Path(drs_root))

    with tempfile.TemporaryDirectory(prefix="hedgehog_demo_drs_") as temp_dir:
        return run_with_root(Path(temp_dir))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Hedgehog OS certificate MVP demo.")
    parser.add_argument(
        "--scenario",
        choices=["cold_start", "reuse", "direct_reuse"],
        required=True,
    )
    args = parser.parse_args(argv)
    print(run_demo(args.scenario), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
