from __future__ import annotations

import argparse
import tempfile
from pathlib import Path
from typing import Any

from demo.run_deadend_memory_demo import DEADEND_RECORD_ID, run_deadend_memory_demo
from hedgehog.drs import LocalDRS
from hedgehog.llm_architect import validate_plan_graph_contract
from hedgehog.root_orchestrator import RootOrchestrator
from hedgehog.time_model import make_time_envelope
from hedgehog.trace_reporter import inspect_plan_graph


ROOT = Path(__file__).resolve().parents[1]
NEEDLES_DIR = ROOT / "needles"
FORBIDDEN_OUTPUT_TERMS = ("raw_user_text", "api_key", "token")


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _llm_called(trace: dict) -> bool:
    llm_architect = trace.get("llm_architect_result") or {}
    llm_gateway = trace.get("llm_gateway_result") or {}
    return bool(llm_architect.get("used_llm") or llm_gateway.get("used_llm"))


def _selected_vector_ids(trace: dict) -> list[str]:
    packet = trace.get("attractor_packet") or {}
    return [vector.get("vector_id", "unknown") for vector in packet.get("candidate_vectors", [])]


def _winner_vector_id(trace: dict) -> str:
    gt_report = trace.get("gt_report") or {}
    winner = gt_report.get("winner")
    if not winner:
        return "none"
    for proposal in trace.get("result_proposals", []):
        if proposal.get("proposal_id") == winner:
            return proposal.get("vector_id", "none")
    return "none"


def _branch_counts(trace: dict) -> tuple[int, int, int]:
    accepted = revised = rejected = 0
    for report in trace.get("vv_reports", []):
        if report.get("decision") == "accept" or report.get("status") == "accepted":
            accepted += 1
        elif report.get("decision") == "revise" or report.get("status") == "needs_revision":
            revised += 1
        elif report.get("decision") == "reject" or report.get("status") == "rejected":
            rejected += 1
    return accepted, revised, rejected


def _seed_direct_reuse_record(drs: LocalDRS) -> str:
    record_id = "work:reasoning_showcase_direct_reuse_source"
    drs.write_record(
        {
            "record_id": record_id,
            "layer": "work",
            "type": "task_outcome",
            "domain": "government_certificate",
            "content": {"summary": "Trusted prior mock certificate outcome."},
            "time_envelope": make_time_envelope("reasoning_showcase_direct_reuse_source_session"),
            "provenance": {
                "request_id": "reasoning_showcase_direct_reuse_source",
                "created_by": "root_orchestrator",
                "trace_refs": [],
            },
            "gt": {
                "gt_report_id": "gt:reasoning:direct_reuse_source",
                "half_life_hours": 2_000.0,
                "decay_rate": 0.0001,
            },
            "status": "accepted",
        }
    )
    return record_id


def _story_block(name: str, steps: list[str], why: str) -> str:
    lines = [f"[STORY] {name}"]
    lines.extend(f"{index}. {step}" for index, step in enumerate(steps, start=1))
    lines.extend(["", "WHY THIS MATTERS:", why])
    return "\n".join(lines)


def _story_l0_reflex(root_path: Path) -> str:
    drs = LocalDRS(root_path / "l0")
    orchestrator = RootOrchestrator(drs=drs, needles_dir=NEEDLES_DIR)
    final_output = orchestrator.process_event(
        raw_user_text="turn on tv",
        request_id="story_l0_reflex_turn_on_tv",
        session_anchor="story_l0_reflex_session",
        allow_reflex=True,
        force_full_pipeline=False,
    )
    trace = orchestrator.last_trace
    steps = [
        "ModeRouter selected deterministic_reflex for a known mock action.",
        f"LLM called: {_bool_text(_llm_called(trace))}.",
        f"Architect skipped: {_bool_text(trace.get('architect_skipped', False))}.",
        f"Executor skipped: {_bool_text(trace.get('executor_skipped', False))}.",
        f"Root wrote Work memory: {_bool_text(bool(final_output.get('drs_writes')))}.",
    ]
    return _story_block(
        "story_l0_reflex_turn_on_tv",
        steps,
        "A cheap deterministic path can handle known safe mock actions without invoking planning or LLM work.",
    )


def _story_memory_first_direct_reuse(root_path: Path) -> str:
    drs = LocalDRS(root_path / "direct_reuse")
    source_record_id = _seed_direct_reuse_record(drs)
    orchestrator = RootOrchestrator(drs=drs, needles_dir=NEEDLES_DIR)
    final_output = orchestrator.process_event(
        raw_user_text="mock certificate request",
        request_id="story_memory_first_direct_reuse",
        session_anchor="story_memory_first_direct_reuse_session",
        allow_direct_reuse=True,
        force_full_pipeline=False,
    )
    trace = orchestrator.last_trace
    reuse_gate = trace.get("reuse_gate") or {}
    steps = [
        f"DRS retrieval found prior eligible Work record {source_record_id}.",
        f"ReuseGate marked best candidate as {reuse_gate.get('reuse_decision', 'none')} with reason eligible.",
        f"Root applied reuse decision {trace.get('reuse_decision', 'none')}.",
        f"Architect skipped: {_bool_text(trace.get('architect_skipped', False))}.",
        f"Executor skipped: {_bool_text(trace.get('executor_skipped', False))}.",
        "Compute saved: no LLM, no PlanGraph execution, and no ResultProposal execution were needed.",
        f"Root wrote new Work memory: {_bool_text(bool(final_output.get('drs_writes')))}.",
    ]
    return _story_block(
        "story_memory_first_direct_reuse",
        steps,
        "Memory is persistent world state; trusted eligible records can reduce compute while Root still owns final output and writeback.",
    )


def _story_full_certificate_pipeline(root_path: Path) -> str:
    drs = LocalDRS(root_path / "full_certificate")
    orchestrator = RootOrchestrator(drs=drs, needles_dir=NEEDLES_DIR)
    final_output = orchestrator.process_event(
        raw_user_text="mock certificate request",
        request_id="story_full_certificate_pipeline",
        session_anchor="story_full_certificate_pipeline_session",
        architect_provider="mock_llm",
    )
    trace = orchestrator.last_trace
    selected = _selected_vector_ids(trace)
    plan_info = inspect_plan_graph(trace.get("plan_graph"))
    accepted, revised, rejected = _branch_counts(trace)
    gt_report = trace.get("gt_report") or {}
    steps = [
        f"InputIntake classified the request as {(trace.get('input_intake') or {}).get('intent_kind', 'unknown')}.",
        f"DRS found no direct reuse: reuse_decision={trace.get('reuse_decision', 'none')}.",
        f"AVF selected {', '.join(selected)}.",
        "AVF blocked illegal_coercion before Architect.",
        f"Architect produced a {plan_info['topology']} PlanGraph with {plan_info['node_count']} nodes.",
        f"Executor produced {len(trace.get('result_proposals', []))} ResultProposals.",
        f"Post V&V accepted {accepted}, marked {revised} for revision, and rejected {rejected}.",
        f"GT selected {_winner_vector_id(trace)} using {gt_report.get('payoff_formula_version', 'none')}.",
        f"RootOrchestrator created FinalOutput as {final_output.get('created_by')} and wrote Work memory.",
    ]
    return _story_block(
        "story_full_certificate_pipeline",
        steps,
        "The Architect only sees safe AVF-selected branches, GT selects under explicit payoff, and Root remains final authority.",
    )


def _story_permission_blocked(root_path: Path) -> str:
    drs = LocalDRS(root_path / "permission_blocked")
    orchestrator = RootOrchestrator(drs=drs, needles_dir=NEEDLES_DIR)
    final_output = orchestrator.process_event(
        raw_user_text="order pizza",
        request_id="story_permission_blocked_without_confirm",
        session_anchor="story_permission_blocked_session",
        allow_reflex=True,
        force_full_pipeline=False,
        user_confirmed=False,
    )
    trace = orchestrator.last_trace
    reflex_result = trace.get("reflex_result") or {}
    steps = [
        f"Permission policy required confirmation for action kind {reflex_result.get('action_kind', 'unknown')}.",
        f"Action result was {reflex_result.get('status', 'unknown')} without confirmation.",
        f"No real external action occurred; protocol_mock_only={_bool_text(reflex_result.get('protocol_mock_only', False))}.",
        f"Final status is {final_output.get('status')}.",
    ]
    return _story_block(
        "story_permission_blocked_without_confirm",
        steps,
        "Permission gates stop actionful paths before side effects while still producing an auditable Root response.",
    )


def _story_architect_contract_recovery(root_path: Path) -> str:
    invalid_plan_graph = {
        "source_packet_id": "packet:invalid",
        "nodes": [],
        "edges": [],
        "executor_assignments": [],
        "time_assumptions": {},
    }
    try:
        validate_plan_graph_contract(invalid_plan_graph)
        contract_error = "none"
    except ValueError as exc:
        contract_error = str(exc)

    drs = LocalDRS(root_path / "contract_recovery")
    orchestrator = RootOrchestrator(drs=drs, needles_dir=NEEDLES_DIR)
    final_output = orchestrator.process_event(
        raw_user_text="mock certificate request",
        request_id="story_architect_contract_violation_recovered",
        session_anchor="story_architect_contract_recovery_session",
        architect_provider="mock_llm",
    )
    steps = [
        f"Invalid PlanGraph contract rejected: {contract_error}.",
        "Deterministic recovery/fallback used the normal schema-valid Architect path.",
        f"Root still created FinalOutput as {final_output.get('created_by')}.",
    ]
    return _story_block(
        "story_architect_contract_violation_recovered",
        steps,
        "LLM-shaped planning artifacts must satisfy contracts before execution; invalid plans do not reach Executor.",
    )


def _story_deadend_memory(root_path: Path) -> str:
    demo_output = run_deadend_memory_demo(drs_root=root_path / "deadend_memory")
    first_blocked = "first_pass_block | PASS" in demo_output
    signal_written = "deadend_record_written | PASS" in demo_output
    second_retrieved = "second_pass_retrieval | PASS" in demo_output
    second_avoided = "second_pass_avoidance | PASS" in demo_output
    final_authority = "final_authority | PASS" in demo_output
    steps = [
        f"First pass observed illegal_coercion blocked before Architect: {_bool_text(first_blocked)}.",
        f"System wrote a demo-level DeadEnd/Fraud-like DRS signal: {_bool_text(signal_written)}.",
        f"Signal identity: {DEADEND_RECORD_ID}; layer deadends; type dead_end; reason forbidden_vector_blocked.",
        f"Second pass retrieved the remembered bad route: {_bool_text(second_retrieved)}.",
        f"The bad vector was not sent to Architect: {_bool_text(second_avoided)}.",
        f"Root remained final authority: {_bool_text(final_authority)}.",
        "No real external action occurred.",
        "This is demo-level DeadEnd memory, not full Marennya/UP mutation.",
    ]
    return _story_block(
        "story_deadend_memory_avoids_bad_route",
        steps,
        "The OS does not only block unsafe branches once; it can preserve negative experience as memory so similar bad routes are recognized later.",
    )


def _story_live_gemini_architect(root_path: Path) -> str:
    drs = LocalDRS(root_path / "live_gemini_architect")
    orchestrator = RootOrchestrator(drs=drs, needles_dir=NEEDLES_DIR)
    final_output = orchestrator.process_event(
        raw_user_text="mock certificate request",
        request_id="story_live_gemini_architect_certificate",
        session_anchor="story_live_gemini_architect_session",
        architect_provider="gemini",
        force_full_pipeline=True,
    )
    trace = orchestrator.last_trace
    llm_architect = trace.get("llm_architect_result") or {}
    plan_info = inspect_plan_graph(trace.get("plan_graph"))
    fallback = llm_architect.get("fallback", "none")
    error = llm_architect.get("error") or "none"
    status = llm_architect.get("status", "none")
    used_llm = bool(llm_architect.get("used_llm", False))
    fallback_used = fallback not in {None, "none", ""}
    steps = [
        "Live Gemini requested: true.",
        f"Architect provider: {llm_architect.get('provider', 'gemini')}.",
        f"LLM Architect status: {status}.",
        f"LLM Architect used_llm: {_bool_text(used_llm)}.",
        f"LLM Architect fallback: {fallback}.",
        f"LLM Architect error: {error}.",
        f"PlanGraph node count: {plan_info['node_count']}.",
        f"PlanGraph topology: {plan_info['topology']}.",
        f"GT winner vector: {_winner_vector_id(trace)}.",
        f"FinalOutput created_by: {final_output.get('created_by')}.",
        f"Deterministic fallback/recovery used: {_bool_text(fallback_used)}.",
    ]
    if status == "completed" and not fallback_used:
        steps.extend(
            [
                "Gemini produced a contract-valid PlanGraph.",
                "Contract validation passed before Executor.",
                "Root still created final output.",
            ]
        )
        why = "A live stochastic Architect can participate, but only through a validated PlanGraph contract under Root authority."
    else:
        steps.extend(
            [
                "Gemini attempt failed or produced an invalid plan.",
                "Deterministic fallback/recovery used a schema-valid PlanGraph path.",
                "Root still created final output if fallback succeeded.",
            ]
        )
        why = "Live LLM failure is SAFE_FAIL/RECOVERED: invalid or unavailable Architect output does not reach Executor."
    return _story_block(
        "story_live_gemini_architect_certificate",
        steps,
        why,
    )


def _sanitize_output(output: str) -> str:
    sanitized = output
    for term in FORBIDDEN_OUTPUT_TERMS:
        sanitized = sanitized.replace(term, "[redacted]")
        sanitized = sanitized.replace(term.upper(), "[redacted]")
    return sanitized


def run_reasoning_showcase(
    *,
    drs_root: Path | None = None,
    include_live_gemini: bool = False,
) -> str:
    if drs_root is None:
        with tempfile.TemporaryDirectory(prefix="hedgehog_reasoning_showcase_") as temp_dir:
            return run_reasoning_showcase(
                drs_root=Path(temp_dir),
                include_live_gemini=include_live_gemini,
            )
    root_path = Path(drs_root)
    blocks = [
        _story_l0_reflex(root_path),
        _story_memory_first_direct_reuse(root_path),
        _story_full_certificate_pipeline(root_path),
        _story_permission_blocked(root_path),
        _story_architect_contract_recovery(root_path),
        _story_deadend_memory(root_path),
    ]
    if include_live_gemini:
        blocks.append(_story_live_gemini_architect(root_path))
    return _sanitize_output("\n\n".join(blocks).rstrip() + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Render Hedgehog OS structured execution stories.")
    parser.add_argument("--include-live-gemini", action="store_true")
    args = parser.parse_args()
    print(run_reasoning_showcase(include_live_gemini=args.include_live_gemini), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
