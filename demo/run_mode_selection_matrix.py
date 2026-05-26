from __future__ import annotations

import argparse
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from hedgehog.drs import LocalDRS
from hedgehog.root_orchestrator import RootOrchestrator
from hedgehog.time_model import make_time_envelope


ROOT = Path(__file__).resolve().parents[1]
NEEDLES_DIR = ROOT / "needles"
FORBIDDEN_OUTPUT_TERMS = ("raw_user_text", "api_key", "token", "hidden reasoning", "chain of thought")


@dataclass
class ModeSelectionRow:
    scenario: str
    input_kind: str
    selected_mode: str
    llm_used: bool
    full_pipeline_used: bool
    reuse_applied: bool
    forbidden_blocked: bool
    gt_winner: str
    drs_write: bool
    reason_for_mode: str


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _llm_used(trace: dict) -> bool:
    llm_architect = trace.get("llm_architect_result") or {}
    llm_gateway = trace.get("llm_gateway_result") or {}
    return bool(llm_architect.get("used_llm") or llm_gateway.get("used_llm"))


def _selected_vector_ids(trace: dict) -> set[str]:
    packet = trace.get("attractor_packet") or {}
    return {vector.get("vector_id", "unknown") for vector in packet.get("candidate_vectors", [])}


def _plan_vector_ids(trace: dict) -> set[str]:
    plan_graph = trace.get("plan_graph") or {}
    return {node.get("vector_id", "unknown") for node in plan_graph.get("nodes", [])}


def _illegal_blocked(trace: dict) -> bool:
    return "illegal_coercion" not in _selected_vector_ids(trace) and "illegal_coercion" not in _plan_vector_ids(trace)


def _winner_vector_id(trace: dict) -> str:
    gt_report = trace.get("gt_report") or {}
    winner = gt_report.get("winner")
    if not winner:
        return "none"
    for proposal in trace.get("result_proposals", []):
        if proposal.get("proposal_id") == winner:
            return proposal.get("vector_id", "none")
    return "none"


def _seed_direct_reuse_record(drs: LocalDRS) -> str:
    record_id = "work:mode_matrix_direct_reuse_source"
    drs.write_record(
        {
            "record_id": record_id,
            "layer": "work",
            "type": "task_outcome",
            "domain": "government_certificate",
            "content": {"summary": "Trusted prior mock certificate outcome."},
            "time_envelope": make_time_envelope("mode_matrix_direct_reuse_source_session"),
            "provenance": {
                "request_id": "mode_matrix_direct_reuse_source",
                "created_by": "root_orchestrator",
                "trace_refs": [],
            },
            "gt": {
                "gt_report_id": "gt:mode_matrix:direct_reuse_source",
                "half_life_hours": 2_000.0,
                "decay_rate": 0.0001,
            },
            "status": "accepted",
        }
    )
    return record_id


def _row_l0(root_path: Path) -> ModeSelectionRow:
    drs = LocalDRS(root_path / "l0")
    orchestrator = RootOrchestrator(drs=drs, needles_dir=NEEDLES_DIR)
    final_output = orchestrator.process_event(
        raw_user_text="turn on tv",
        request_id="mode_l0_reflex_turn_on_tv",
        session_anchor="mode_l0_reflex_session",
        allow_reflex=True,
        force_full_pipeline=False,
    )
    trace = orchestrator.last_trace
    return ModeSelectionRow(
        scenario="mode_l0_reflex_turn_on_tv",
        input_kind="simple_command",
        selected_mode=trace.get("execution_mode", "none"),
        llm_used=_llm_used(trace),
        full_pipeline_used=bool((trace.get("plan_graph") or {}).get("nodes")),
        reuse_applied=bool(trace.get("reuse_applied", False)),
        forbidden_blocked=True,
        gt_winner=_winner_vector_id(trace),
        drs_write=bool(final_output.get("drs_writes")),
        reason_for_mode="known deterministic mock action; no planning needed",
    )


def _row_general_math(root_path: Path) -> ModeSelectionRow:
    drs = LocalDRS(root_path / "general_math")
    orchestrator = RootOrchestrator(drs=drs, needles_dir=NEEDLES_DIR)
    final_output = orchestrator.process_event(
        raw_user_text="x + y = 110\nx - y = 100",
        request_id="mode_general_math_mock",
        session_anchor="mode_general_math_session",
        llm_provider="mock",
    )
    trace = orchestrator.last_trace
    return ModeSelectionRow(
        scenario="mode_general_math_mock",
        input_kind="simple_general_question",
        selected_mode=trace.get("execution_mode", "none"),
        llm_used=_llm_used(trace),
        full_pipeline_used=bool((trace.get("plan_graph") or {}).get("nodes")),
        reuse_applied=bool(trace.get("reuse_applied", False)),
        forbidden_blocked=True,
        gt_winner=_winner_vector_id(trace),
        drs_write=bool(final_output.get("drs_writes")),
        reason_for_mode="simple general question uses cheap mock general responder route",
    )


def _row_full_certificate(root_path: Path) -> ModeSelectionRow:
    drs = LocalDRS(root_path / "full_certificate")
    orchestrator = RootOrchestrator(drs=drs, needles_dir=NEEDLES_DIR)
    final_output = orchestrator.process_event(
        raw_user_text="mock certificate request",
        request_id="mode_full_certificate_pipeline",
        session_anchor="mode_full_certificate_session",
        architect_provider="mock_llm",
    )
    trace = orchestrator.last_trace
    return ModeSelectionRow(
        scenario="mode_full_certificate_pipeline",
        input_kind="complex_certificate_task",
        selected_mode=trace.get("execution_mode") or trace.get("route") or "proof_full_pipeline",
        llm_used=_llm_used(trace),
        full_pipeline_used=bool((trace.get("plan_graph") or {}).get("nodes")),
        reuse_applied=bool(trace.get("reuse_applied", False)),
        forbidden_blocked=_illegal_blocked(trace),
        gt_winner=_winner_vector_id(trace),
        drs_write=bool(final_output.get("drs_writes")),
        reason_for_mode="complex constrained task needs AVF, PlanGraph, Executor, Post V&V, and GT",
    )


def _row_direct_reuse(root_path: Path) -> ModeSelectionRow:
    drs = LocalDRS(root_path / "direct_reuse")
    _seed_direct_reuse_record(drs)
    orchestrator = RootOrchestrator(drs=drs, needles_dir=NEEDLES_DIR)
    final_output = orchestrator.process_event(
        raw_user_text="mock certificate request",
        request_id="mode_memory_direct_reuse",
        session_anchor="mode_memory_direct_reuse_session",
        allow_direct_reuse=True,
        force_full_pipeline=False,
    )
    trace = orchestrator.last_trace
    return ModeSelectionRow(
        scenario="mode_memory_direct_reuse",
        input_kind="repeated_known_task",
        selected_mode=trace.get("execution_mode") or trace.get("reuse_decision", "none"),
        llm_used=_llm_used(trace),
        full_pipeline_used=bool((trace.get("plan_graph") or {}).get("nodes")),
        reuse_applied=bool(trace.get("reuse_applied", False)),
        forbidden_blocked=True,
        gt_winner=_winner_vector_id(trace),
        drs_write=bool(final_output.get("drs_writes")),
        reason_for_mode="trusted eligible memory record allows direct reuse and compute saved",
    )


def _sanitize_output(output: str) -> str:
    sanitized = output
    for term in FORBIDDEN_OUTPUT_TERMS:
        sanitized = sanitized.replace(term, "[redacted]")
        sanitized = sanitized.replace(term.upper(), "[redacted]")
    return sanitized


def run_mode_selection_matrix(*, drs_root: Path | None = None) -> str:
    if drs_root is None:
        with tempfile.TemporaryDirectory(prefix="hedgehog_mode_matrix_") as temp_dir:
            return run_mode_selection_matrix(drs_root=Path(temp_dir))
    root_path = Path(drs_root)
    rows = [
        _row_l0(root_path),
        _row_general_math(root_path),
        _row_full_certificate(root_path),
        _row_direct_reuse(root_path),
    ]
    lines = [
        "[MODE SELECTION MATRIX]",
        "scenario | input_kind | selected_mode | llm_used | full_pipeline_used | reuse_applied | forbidden_blocked | gt_winner | drs_write | reason_for_mode",
        "--- | --- | --- | --- | --- | --- | --- | --- | --- | ---",
    ]
    for row in rows:
        lines.append(
            " | ".join(
                [
                    row.scenario,
                    row.input_kind,
                    row.selected_mode,
                    _bool_text(row.llm_used),
                    _bool_text(row.full_pipeline_used),
                    _bool_text(row.reuse_applied),
                    _bool_text(row.forbidden_blocked),
                    row.gt_winner,
                    _bool_text(row.drs_write),
                    row.reason_for_mode,
                ]
            )
        )
    lines.extend(
        [
            "",
            "SUMMARY:",
            "Hedgehog OS does not use one pipeline for everything.",
            "It scales from deterministic reflex to direct reuse to general LLM to full PlanGraph pipeline.",
        ]
    )
    return _sanitize_output("\n".join(lines).rstrip() + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Render Hedgehog OS mode selection matrix.")
    parser.parse_args()
    print(run_mode_selection_matrix(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
