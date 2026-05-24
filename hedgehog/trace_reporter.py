from __future__ import annotations

import json
from typing import Any


SENSITIVE_TERMS = ("raw_user_text", "api_key", "apikey", "token")


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _short(value: Any, limit: int = 240) -> str:
    if value is None:
        return "none"
    line = " ".join(str(value).split())
    for term in SENSITIVE_TERMS:
        line = line.replace(term, "[redacted]")
    if len(line) <= limit:
        return line
    return f"{line[: limit - 3]}..."


def _winner_vector_id(trace: dict, winner_proposal_id: str | None) -> str:
    if not winner_proposal_id:
        return "none"
    for proposal in trace.get("result_proposals", []):
        if proposal.get("proposal_id") == winner_proposal_id:
            return proposal.get("vector_id", "none")
    return "none"


def _best_reuse(trace: dict) -> tuple[str, str]:
    reuse_gate = trace.get("reuse_gate") or {}
    best_id = reuse_gate.get("best_record_id")
    reason = "none"
    for score in reuse_gate.get("candidate_scores", []):
        if score.get("record_id") == best_id:
            reason = score.get("reason", "none")
            break
    return best_id or "none", reason


def _branch_counts(trace: dict) -> tuple[int, int, int, int]:
    accepted = rejected = revise = blocked = 0
    for report in trace.get("vv_reports", []):
        decision = report.get("decision")
        status = report.get("status")
        if decision == "accept" or status == "accepted":
            accepted += 1
        elif decision == "reject" or status == "rejected":
            rejected += 1
        elif decision == "revise" or status == "needs_revision":
            revise += 1
    for proposal in trace.get("result_proposals", []):
        if proposal.get("result_payload", {}).get("blocked_reason"):
            blocked += 1
    return accepted, rejected, revise, blocked


def _avf_lines(trace: dict) -> list[str]:
    packet = trace.get("attractor_packet") or {}
    plan_graph = trace.get("plan_graph") or {}
    selected = [vector.get("vector_id", "unknown") for vector in packet.get("candidate_vectors", [])]
    node_vectors = [node.get("vector_id", "unknown") for node in plan_graph.get("nodes", [])]
    illegal_blocked = "illegal_coercion" not in selected and "illegal_coercion" not in node_vectors
    lines = ["[AVF]"]
    lines.append(f"- selected vector ids: {', '.join(selected) if selected else 'none'}")
    lines.append("- blocked forbidden vectors: illegal_coercion" if illegal_blocked else "- blocked forbidden vectors: none")
    lines.append(f"- illegal_coercion blocked: {_bool_text(illegal_blocked)}")
    return lines


def _architect_lines(trace: dict) -> list[str]:
    llm_result = trace.get("llm_architect_result") or {}
    plan_graph = trace.get("plan_graph") or {}
    lines = ["[ARCHITECT]"]
    lines.append(f"- architect_provider: {llm_result.get('provider', 'deterministic')}")
    if llm_result:
        lines.extend(
            [
                f"- llm_architect status: {llm_result.get('status', 'none')}",
                f"- llm_architect provider: {llm_result.get('provider', 'none')}",
                f"- llm_architect model: {llm_result.get('model', 'none')}",
                f"- llm_architect used_llm: {_bool_text(llm_result.get('used_llm', False))}",
                f"- llm_architect fallback: {llm_result.get('fallback', 'none')}",
                f"- llm_architect error: {_short(llm_result.get('error'))}",
            ]
        )
    lines.append(f"- architect_skipped: {_bool_text(trace.get('architect_skipped', False))}")
    lines.append(f"- PlanGraph node count: {len(plan_graph.get('nodes', []))}")
    return lines


def render_trace_report(trace: dict, final_output: dict | None = None) -> str:
    final = final_output or trace.get("final_output") or {}
    input_intake = trace.get("input_intake") or {}
    gt_report = trace.get("gt_report") or {}
    best_reuse_id, best_reuse_reason = _best_reuse(trace)
    accepted, rejected, revise, blocked = _branch_counts(trace)
    winner_proposal_id = gt_report.get("winner")
    lines = [
        "[ROOT]",
        f"- request_id: {final.get('request_id', 'none')}",
        f"- execution_mode: {trace.get('execution_mode') or trace.get('mode_router', {}).get('execution_mode', 'unknown')}",
        f"- route: {trace.get('route') or trace.get('execution_mode') or trace.get('mode_router', {}).get('execution_mode', 'unknown')}",
        f"- final_status: {final.get('status', 'none')}",
    ]
    if input_intake:
        lines.append(f"- input_intake: {input_intake.get('intent_kind', 'none')} ({input_intake.get('reason', 'none')})")

    lines.extend(
        [
            "",
            "[DRS]",
            f"- retrieved_record_count: {trace.get('retrieved_record_count', 0)}",
            f"- memory_context_applied: {_bool_text(trace.get('memory_context_applied', False))}",
            f"- reuse_decision: {trace.get('reuse_decision', 'none')}",
            f"- reuse_applied: {_bool_text(trace.get('reuse_applied', False))}",
            f"- direct_reuse_applied: {_bool_text(trace.get('direct_reuse_applied', False) or (trace.get('reuse_decision') == 'direct_reuse' and trace.get('reuse_applied')))}",
            f"- best reuse candidate: {best_reuse_id}",
            f"- best reuse reason: {best_reuse_reason}",
            "",
            *_avf_lines(trace),
            "",
            *_architect_lines(trace),
            "",
            "[EXECUTOR]",
            f"- executor_skipped: {_bool_text(trace.get('executor_skipped', False))}",
            f"- ResultProposal count: {len(trace.get('result_proposals', []))}",
            "- count note: categories may overlap",
            f"- completed reports: {accepted}",
            f"- needs_user reports: {revise}",
            f"- blocked proposals: {blocked}",
            "",
            "[POST_VV]",
            f"- accepted count: {accepted}",
            f"- rejected count: {rejected}",
            f"- revision count: {revise}",
            "",
            "[GT]",
            f"- decision: {gt_report.get('decision', 'none')}",
            f"- winner proposal id: {winner_proposal_id or 'none'}",
            f"- winner vector id: {_winner_vector_id(trace, winner_proposal_id)}",
            "",
            "[FINAL]",
            f"- created_by: {final.get('created_by', 'none')}",
            f"- status: {final.get('status', 'none')}",
            f"- drs_writes: {', '.join(final.get('drs_writes', [])) if final.get('drs_writes') else 'none'}",
        ]
    )
    report = "\n".join(lines)
    lowered = report.lower()
    if any(term in lowered for term in SENSITIVE_TERMS):
        safe = report
        for term in SENSITIVE_TERMS:
            safe = safe.replace(term, "[redacted]")
        return safe
    return report
