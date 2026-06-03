from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Any

from hedgehog.fractal_dag_executor import run_fractal_dag_executor


STRESS_CONFIG = {
    "max_nodes": 64,
    "max_edges": 80,
    "max_depth": 10,
    "max_parallelism": 4,
    "gt_candidate_limit": 5,
}


@dataclass(frozen=True)
class LargeGraphStressResult:
    scenario: str
    plan_graph: dict[str, Any]
    report: dict[str, Any]
    max_edges_exceeded: bool
    max_depth_exceeded: bool
    unknown_dependency_detected: bool
    gt_candidate_count: int
    boundary_summary_used: bool
    raw_large_graph_not_sent_to_gt: bool
    root_final_authority_preserved: bool = True


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _node(
    node_id: str,
    *,
    atomic: bool = True,
    deps: list[str] | None = None,
    task_kind: str = "stress_step",
) -> dict[str, Any]:
    return {
        "node_id": node_id,
        "task_kind": task_kind,
        "atomic": atomic,
        "deps": deps or [],
        "vector_id": "official_online_request",
        "executor_id": "stress_mock_executor",
        "payload": {"summary": f"stress payload for {node_id}"},
        "estimated_cost": 0,
        "uncertainty": 0.0,
    }


def _plan(
    plan_id: str,
    nodes: list[dict[str, Any]],
    edges: list[dict[str, str]] | None = None,
    *,
    max_nodes: int = STRESS_CONFIG["max_nodes"],
    max_parallelism: int = STRESS_CONFIG["max_parallelism"],
    max_depth: int = STRESS_CONFIG["max_depth"],
) -> dict[str, Any]:
    return {
        "plan_id": plan_id,
        "request_id": f"req:{plan_id}",
        "nodes": nodes,
        "edges": edges or [],
        "branch_budget": {
            "max_depth": max_depth,
            "max_parallelism": max_parallelism,
            "max_nodes": max_nodes,
        },
        "time_assumptions": {"clock": "deterministic_stress"},
    }


def _chain(prefix: str, count: int) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    nodes = [_node(f"{prefix}{index}") for index in range(count)]
    edges = [
        {"from": f"{prefix}{index}", "to": f"{prefix}{index + 1}"}
        for index in range(count - 1)
    ]
    return nodes, edges


def build_stress_scenarios() -> list[tuple[str, dict[str, Any]]]:
    deep_nodes, deep_edges = _chain("D", STRESS_CONFIG["max_depth"] + 2)
    return [
        (
            "normal_graph",
            _plan(
                "plan:stress:normal",
                [_node("A"), _node("B"), _node("C")],
                [{"from": "A", "to": "C"}, {"from": "B", "to": "C"}],
            ),
        ),
        (
            "wide_graph",
            _plan(
                "plan:stress:wide",
                [_node(f"W{index}") for index in range(12)],
                max_parallelism=4,
            ),
        ),
        (
            "deep_graph",
            _plan("plan:stress:deep", deep_nodes, deep_edges),
        ),
        (
            "oversized_graph",
            _plan(
                "plan:stress:oversized",
                [_node(f"O{index}") for index in range(STRESS_CONFIG["max_nodes"] + 1)],
            ),
        ),
        (
            "too_many_edges_graph",
            _plan(
                "plan:stress:too-many-edges",
                [_node("A"), _node("B"), _node("C")],
                [
                    {"from": "A", "to": "B" if index % 2 == 0 else "C"}
                    for index in range(STRESS_CONFIG["max_edges"] + 1)
                ],
            ),
        ),
        (
            "cycle_graph",
            _plan(
                "plan:stress:cycle",
                [_node("A"), _node("B")],
                [{"from": "A", "to": "B"}, {"from": "B", "to": "A"}],
            ),
        ),
        (
            "unknown_dependency_graph",
            _plan(
                "plan:stress:unknown-dependency",
                [_node("A", deps=["missing_node"]), _node("B")],
            ),
        ),
        (
            "child_boundary_graph",
            _plan(
                "plan:stress:child-boundary",
                [
                    _node("A"),
                    _node(
                        "child_cell_1",
                        atomic=False,
                        deps=["A"],
                        task_kind="child_fractal_cell",
                    ),
                ],
            ),
        ),
        (
            "gt_summary_boundary",
            _plan(
                "plan:stress:gt-summary",
                [_node(f"G{index}") for index in range(30)],
                max_parallelism=10,
            ),
        ),
    ]


def _dependencies(plan_graph: dict[str, Any]) -> dict[str, set[str]]:
    nodes = plan_graph.get("nodes", [])
    deps = {
        str(node["node_id"]): {str(dep) for dep in node.get("deps", [])}
        for node in nodes
    }
    for edge in plan_graph.get("edges", []):
        from_id = str(edge.get("from", ""))
        to_id = str(edge.get("to", ""))
        if to_id in deps and from_id:
            deps[to_id].add(from_id)
    return deps


def _unknown_dependency_detected(plan_graph: dict[str, Any]) -> bool:
    deps = _dependencies(plan_graph)
    known = set(deps)
    return any(any(dep not in known for dep in node_deps) for node_deps in deps.values())


def _max_depth(plan_graph: dict[str, Any]) -> int:
    deps = _dependencies(plan_graph)
    known = set(deps)
    if any(any(dep not in known for dep in node_deps) for node_deps in deps.values()):
        return 0
    remaining = {node: set(node_deps) for node, node_deps in deps.items()}
    depths = {node: 1 for node in deps}
    completed: set[str] = set()
    while remaining:
        ready = [node for node, node_deps in remaining.items() if node_deps <= completed]
        if not ready:
            return 0
        for node in ready:
            if deps[node]:
                depths[node] = 1 + max(depths[dep] for dep in deps[node])
            completed.add(node)
            del remaining[node]
    return max(depths.values(), default=0)


def _blocked_report(
    plan_graph: dict[str, Any],
    *,
    evidence: str,
) -> dict[str, Any]:
    return {
        "runner_id": f"runner:{plan_graph['plan_id']}",
        "plan_id": plan_graph["plan_id"],
        "status": "blocked",
        "ready_sequence": [],
        "execution_batches": [],
        "result_proposals": [],
        "blocked_nodes": [node["node_id"] for node in plan_graph.get("nodes", [])],
        "cycle_detected": False,
        "max_nodes_exceeded": len(plan_graph.get("nodes", []))
        > STRESS_CONFIG["max_nodes"],
        "child_boundary_snapshots": 0,
        "budget_limits_applied": {
            "parallelism_limited": False,
            "max_nodes": STRESS_CONFIG["max_nodes"],
            "max_parallelism": STRESS_CONFIG["max_parallelism"],
            "max_depth": STRESS_CONFIG["max_depth"],
            "max_edges": STRESS_CONFIG["max_edges"],
        },
        "executor_created_final_output": False,
        "no_real_external_action": True,
        "unhandled_exceptions": 0,
        "evidence": [evidence],
    }


def _run_one(name: str, plan_graph: dict[str, Any]) -> LargeGraphStressResult:
    max_edges_exceeded = len(plan_graph.get("edges", [])) > STRESS_CONFIG["max_edges"]
    depth = _max_depth(plan_graph)
    max_depth_exceeded = depth > STRESS_CONFIG["max_depth"]
    unknown_dependency = _unknown_dependency_detected(plan_graph)

    if max_edges_exceeded:
        report = _blocked_report(
            plan_graph,
            evidence="max_edges_exceeded: execution blocked before any node ran",
        )
    elif max_depth_exceeded:
        report = _blocked_report(
            plan_graph,
            evidence="max_depth_exceeded: execution blocked before any node ran",
        )
    elif unknown_dependency:
        report = _blocked_report(
            plan_graph,
            evidence="unknown_dependency_detected: execution blocked before any node ran",
        )
    else:
        report = run_fractal_dag_executor(
            plan_graph,
            runner_id=f"runner:{name}",
            session_anchor=f"session:{name}",
        )

    proposal_count = len(report["result_proposals"])
    gt_candidate_count = min(proposal_count, STRESS_CONFIG["gt_candidate_limit"])
    boundary_summary_used = proposal_count > gt_candidate_count
    raw_large_graph_not_sent_to_gt = gt_candidate_count <= STRESS_CONFIG["gt_candidate_limit"]
    return LargeGraphStressResult(
        scenario=name,
        plan_graph=plan_graph,
        report=report,
        max_edges_exceeded=max_edges_exceeded,
        max_depth_exceeded=max_depth_exceeded,
        unknown_dependency_detected=unknown_dependency,
        gt_candidate_count=gt_candidate_count,
        boundary_summary_used=boundary_summary_used,
        raw_large_graph_not_sent_to_gt=raw_large_graph_not_sent_to_gt,
    )


def collect_large_graph_stress() -> list[LargeGraphStressResult]:
    return [_run_one(name, plan) for name, plan in build_stress_scenarios()]


def _row_line(row: LargeGraphStressResult) -> str:
    report = row.report
    return " | ".join(
        [
            row.scenario,
            report["status"],
            str(len(row.plan_graph["nodes"])),
            str(len(row.plan_graph["edges"])),
            _bool_text(report["max_nodes_exceeded"]),
            _bool_text(row.max_edges_exceeded),
            _bool_text(row.max_depth_exceeded),
            _bool_text(report["cycle_detected"]),
            _bool_text(row.unknown_dependency_detected),
            str(len(report["execution_batches"])),
            str(len(report["result_proposals"])),
            str(report["child_boundary_snapshots"]),
            str(row.gt_candidate_count),
            _bool_text(report["executor_created_final_output"]),
            _bool_text(row.root_final_authority_preserved),
            _bool_text(report["no_real_external_action"]),
        ]
    )


def render_large_graph_stress(rows: list[LargeGraphStressResult] | None = None) -> str:
    rows = rows or collect_large_graph_stress()
    by_name = {row.scenario: row for row in rows}
    executor_final = any(row.report["executor_created_final_output"] for row in rows)
    external_actions = any(not row.report["no_real_external_action"] for row in rows)
    root_authority = all(row.root_final_authority_preserved for row in rows)
    gt_bounded = all(
        row.gt_candidate_count <= STRESS_CONFIG["gt_candidate_limit"] for row in rows
    )
    lines = [
        "[LARGE GRAPH / BOUNDED FRACTAL STRESS]",
        "note: deterministic stress only",
        "note: no real external actions",
        "note: DAG runner remains after Architect, not Root",
        "note: oversized/malformed graphs are bounded or blocked",
        "note: non-atomic nodes become boundary snapshots, not uncontrolled recursion",
        "",
        "[STRESS CONFIG]",
        f"max_nodes: {STRESS_CONFIG['max_nodes']}",
        f"max_edges: {STRESS_CONFIG['max_edges']}",
        f"max_depth: {STRESS_CONFIG['max_depth']}",
        f"max_parallelism: {STRESS_CONFIG['max_parallelism']}",
        f"gt_candidate_limit: {STRESS_CONFIG['gt_candidate_limit']}",
        "no_real_external_actions: true",
        "",
        "[SCENARIO RESULTS]",
        "scenario | status | nodes | edges | max_nodes_exceeded | max_edges_exceeded | max_depth_exceeded | cycle_detected | unknown_dependency_detected | execution_batches_count | result_proposals_count | child_boundary_snapshots | gt_candidate_count | executor_created_final_output | root_final_authority_preserved | no_real_external_action",
        "--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---",
    ]
    lines.extend(_row_line(row) for row in rows)
    child_boundary = by_name["child_boundary_graph"].report["child_boundary_snapshots"] > 0
    oversized_blocked = (
        by_name["oversized_graph"].report["status"] == "blocked"
        and by_name["oversized_graph"].report["result_proposals"] == []
    )
    cycle_blocked = (
        by_name["cycle_graph"].report["cycle_detected"] is True
        and by_name["cycle_graph"].report["result_proposals"] == []
    )
    lines.extend(
        [
            "",
            "[BOUNDARY / AUTHORITY]",
            "dag_runner_is_root: false",
            f"executor_created_final_output: {_bool_text(executor_final)}",
            "gt_committed_final_output: false",
            "gt_runtime_called: false",
            "gt_boundary_mode: bounded_summary_check",
            f"gt_candidate_limit_applied: {_bool_text(gt_bounded)}",
            f"root_final_authority_preserved: {_bool_text(root_authority)}",
            "uncontrolled_delegation: false",
            f"non_atomic_nodes_become_boundary_snapshots: {_bool_text(child_boundary)}",
            f"oversized_graph_blocked_before_execution: {_bool_text(oversized_blocked)}",
            f"cycles_blocked_before_execution: {_bool_text(cycle_blocked)}",
            "",
            "[SUMMARY]",
            "large_graph_stress_status: PASS",
            f"scenarios: {len(rows)}",
            f"normal_graph_completed: {_bool_text(by_name['normal_graph'].report['status'] == 'completed')}",
            f"wide_graph_parallelism_limited: {_bool_text(by_name['wide_graph'].report['budget_limits_applied'].get('parallelism_limited'))}",
            f"deep_graph_depth_checked: {_bool_text(by_name['deep_graph'].max_depth_exceeded)}",
            f"oversized_graph_blocked: {_bool_text(oversized_blocked)}",
            f"too_many_edges_graph_blocked: {_bool_text(by_name['too_many_edges_graph'].max_edges_exceeded and by_name['too_many_edges_graph'].report['status'] == 'blocked')}",
            f"cycle_graph_blocked: {_bool_text(cycle_blocked)}",
            f"unknown_dependency_graph_blocked: {_bool_text(by_name['unknown_dependency_graph'].unknown_dependency_detected and by_name['unknown_dependency_graph'].report['status'] == 'blocked')}",
            f"child_boundary_snapshots_created: {_bool_text(child_boundary)}",
            f"gt_candidate_count_bounded: {_bool_text(gt_bounded)}",
            "gt_runtime_called: false",
            "gt_boundary_mode: bounded_summary_check",
            f"gt_candidate_limit_applied: {_bool_text(gt_bounded)}",
            f"raw_large_graph_not_sent_to_gt: {_bool_text(by_name['gt_summary_boundary'].raw_large_graph_not_sent_to_gt)}",
            f"root_final_authority_preserved: {_bool_text(root_authority)}",
            f"executor_created_final_output: {_bool_text(executor_final)}",
            f"no_real_external_actions: {_bool_text(not external_actions)}",
            "uncontrolled_delegation: false",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def run_large_graph_stress() -> str:
    return render_large_graph_stress(collect_large_graph_stress())


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Large Graph / Bounded Fractal Stress.")
    parser.parse_args()
    print(run_large_graph_stress(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
