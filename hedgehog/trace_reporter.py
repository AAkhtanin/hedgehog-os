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


def _edge_cycle_validity(node_ids: set[str], edges: list[dict]) -> bool | None:
    adjacency = {node_id: [] for node_id in node_ids}
    for edge in edges:
        if not isinstance(edge, dict) or "from" not in edge or "to" not in edge:
            return None
        source = edge["from"]
        target = edge["to"]
        if source not in node_ids or target not in node_ids:
            return None
        adjacency[source].append(target)

    visited = set()
    active = set()

    def visit(node_id: str) -> bool:
        if node_id in active:
            return False
        if node_id in visited:
            return True
        active.add(node_id)
        for child in adjacency[node_id]:
            if not visit(child):
                return False
        active.remove(node_id)
        visited.add(node_id)
        return True

    return all(visit(node_id) for node_id in node_ids)


def _classify_topology(nodes: list[dict], edges: list[dict], dag_valid: bool | None) -> str:
    if dag_valid is None:
        return "unknown"
    if dag_valid is False:
        return "cyclic_invalid"
    if not nodes:
        return "empty"
    if len(nodes) == 1 and not edges:
        return "single_node"
    if not edges:
        return "horizontal"

    node_ids = {node["node_id"] for node in nodes}
    incoming = {node_id: 0 for node_id in node_ids}
    outgoing = {node_id: 0 for node_id in node_ids}
    for edge in edges:
        outgoing[edge["from"]] += 1
        incoming[edge["to"]] += 1

    roots = [node_id for node_id, count in incoming.items() if count == 0]
    leaves = [node_id for node_id, count in outgoing.items() if count == 0]
    linear = (
        len(edges) == len(nodes) - 1
        and len(roots) == 1
        and len(leaves) == 1
        and all(count <= 1 for count in incoming.values())
        and all(count <= 1 for count in outgoing.values())
    )
    if linear:
        return "vertical"
    return "hybrid"


def inspect_plan_graph(plan_graph: dict | None) -> dict:
    if not plan_graph:
        return {
            "plan_id": "none",
            "source_packet_id": "none",
            "request_id": "none",
            "node_count": 0,
            "edge_count": 0,
            "dag_valid": "unknown",
            "topology": "empty",
            "nodes": [],
            "edges": [],
        }
    if not isinstance(plan_graph, dict):
        return {
            "plan_id": "unknown",
            "source_packet_id": "unknown",
            "request_id": "unknown",
            "node_count": 0,
            "edge_count": 0,
            "dag_valid": "unknown",
            "topology": "unknown",
            "nodes": [],
            "edges": [],
        }

    raw_nodes = plan_graph.get("nodes", [])
    raw_edges = plan_graph.get("edges", [])
    if not isinstance(raw_nodes, list) or not isinstance(raw_edges, list):
        return {
            "plan_id": plan_graph.get("plan_id", "unknown"),
            "source_packet_id": plan_graph.get("source_packet_id", "unknown"),
            "request_id": plan_graph.get("request_id", "unknown"),
            "node_count": 0,
            "edge_count": 0,
            "dag_valid": "unknown",
            "topology": "unknown",
            "nodes": [],
            "edges": [],
        }

    nodes = []
    malformed = False
    node_ids = set()
    for node in raw_nodes:
        if not isinstance(node, dict) or "node_id" not in node:
            malformed = True
            continue
        node_ids.add(node["node_id"])
        nodes.append(
            {
                "node_id": _short(node.get("node_id", "unknown"), 80),
                "vector_id": _short(node.get("vector_id", "unknown"), 80),
                "executor_id": _short(node.get("executor_id", "unknown"), 80),
                "depends_on": [
                    _short(dep, 60)
                    for dep in node.get("depends_on", [])
                    if isinstance(dep, str)
                ],
                "task_short": _short(node.get("task", "unknown"), 100),
            }
        )

    edge_items = []
    for edge in raw_edges:
        if not isinstance(edge, dict) or "from" not in edge or "to" not in edge:
            malformed = True
            continue
        edge_items.append(
            {
                "from": _short(edge["from"], 80),
                "to": _short(edge["to"], 80),
            }
        )

    dag_value = None if malformed else _edge_cycle_validity(node_ids, raw_edges)
    topology = _classify_topology(raw_nodes, raw_edges, dag_value)
    return {
        "plan_id": _short(plan_graph.get("plan_id", "unknown"), 120),
        "source_packet_id": _short(plan_graph.get("source_packet_id", "unknown"), 120),
        "request_id": _short(plan_graph.get("request_id", "unknown"), 120),
        "node_count": len(raw_nodes),
        "edge_count": len(raw_edges),
        "dag_valid": "unknown" if dag_value is None else _bool_text(dag_value),
        "topology": topology,
        "nodes": nodes,
        "edges": edge_items,
    }


def render_plan_graph_section(plan_graph: dict | None) -> list[str]:
    info = inspect_plan_graph(plan_graph)
    lines = [
        "[PLAN_GRAPH]",
        f"- plan_id: {info['plan_id']}",
        f"- source_packet_id: {info['source_packet_id']}",
        f"- request_id: {info['request_id']}",
        f"- node_count: {info['node_count']}",
        f"- edge_count: {info['edge_count']}",
        f"- dag_valid: {info['dag_valid']}",
        f"- topology: {info['topology']}",
        "- nodes:",
    ]
    if info["nodes"]:
        for node in info["nodes"]:
            deps = ", ".join(node["depends_on"]) if node["depends_on"] else "none"
            lines.append(
                "  - "
                f"node_id={node['node_id']} "
                f"vector_id={node['vector_id']} "
                f"executor_id={node['executor_id']} "
                f"depends_on={deps} "
                f"task_short={node['task_short']}"
            )
    else:
        lines.append("  - none")
    lines.append("- edges:")
    if info["edges"]:
        for edge in info["edges"]:
            lines.append(f"  - {edge['from']} -> {edge['to']}")
    else:
        lines.append("  - none")
    return lines


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
            *(
                [*render_plan_graph_section(trace.get("plan_graph")), ""]
                if trace.get("plan_graph")
                else []
            ),
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
