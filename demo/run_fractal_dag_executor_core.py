from __future__ import annotations

from dataclasses import dataclass

from hedgehog.fractal_dag_executor import run_fractal_dag_executor


@dataclass(frozen=True)
class ScenarioResult:
    name: str
    plan_graph: dict
    report: dict


def _node(
    node_id: str,
    *,
    task_kind: str = "mock_step",
    atomic: bool = True,
    deps: list[str] | None = None,
    vector_id: str = "official_online_request",
    executor_id: str = "mock_executor",
    payload: dict | None = None,
) -> dict:
    return {
        "node_id": node_id,
        "task_kind": task_kind,
        "atomic": atomic,
        "deps": deps or [],
        "vector_id": vector_id,
        "executor_id": executor_id,
        "payload": payload or {"summary": f"mock payload for {node_id}"},
        "estimated_cost": 0,
        "uncertainty": 0.0,
    }


def _plan(
    plan_id: str,
    nodes: list[dict],
    edges: list[dict] | None = None,
    *,
    max_parallelism: int = 4,
    max_nodes: int = 16,
) -> dict:
    return {
        "plan_id": plan_id,
        "request_id": f"req:{plan_id}",
        "nodes": nodes,
        "edges": edges or [],
        "branch_budget": {
            "max_depth": 4,
            "max_parallelism": max_parallelism,
            "max_nodes": max_nodes,
        },
        "time_assumptions": {"clock": "demo_static"},
    }


def build_scenarios() -> list[tuple[str, dict]]:
    return [
        (
            "horizontal_parallel_branches",
            _plan(
                "plan:horizontal",
                [_node("A"), _node("B"), _node("C")],
                max_parallelism=3,
            ),
        ),
        (
            "vertical_chain",
            _plan(
                "plan:vertical",
                [_node("A"), _node("B"), _node("C")],
                [{"from": "A", "to": "B"}, {"from": "B", "to": "C"}],
                max_parallelism=3,
            ),
        ),
        (
            "hybrid_graph",
            _plan(
                "plan:hybrid",
                [_node("A"), _node("B"), _node("C"), _node("D")],
                [
                    {"from": "A", "to": "C"},
                    {"from": "A", "to": "D"},
                    {"from": "B", "to": "D"},
                ],
                max_parallelism=2,
            ),
        ),
        (
            "non_atomic_child_cell_placeholder",
            _plan(
                "plan:child-cell",
                [
                    _node(
                        "A",
                        task_kind="child_fractal_cell",
                        atomic=False,
                        payload={"child_scope": "local_certificate_requirements"},
                    )
                ],
            ),
        ),
        (
            "parallelism_budget_limit",
            _plan(
                "plan:parallelism-limit",
                [_node("A"), _node("B"), _node("C"), _node("D")],
                max_parallelism=2,
            ),
        ),
        (
            "cycle_detected",
            _plan(
                "plan:cycle",
                [_node("A"), _node("B")],
                [{"from": "A", "to": "B"}, {"from": "B", "to": "A"}],
            ),
        ),
        (
            "max_nodes_exceeded",
            _plan(
                "plan:max-nodes",
                [_node("A"), _node("B"), _node("C")],
                max_nodes=2,
            ),
        ),
    ]


def run_scenarios() -> list[ScenarioResult]:
    rows = []
    for name, plan_graph in build_scenarios():
        report = run_fractal_dag_executor(
            plan_graph,
            runner_id=f"runner:{name}",
            session_anchor=f"session:{name}",
        )
        rows.append(ScenarioResult(name=name, plan_graph=plan_graph, report=report))
    return rows


def _bool_text(value: bool) -> str:
    return "true" if value else "false"


def _seq(value: list[list[str]]) -> str:
    if not value:
        return "none"
    return " / ".join(",".join(batch) for batch in value)


def render_report(rows: list[ScenarioResult] | None = None) -> str:
    rows = rows or run_scenarios()
    lines = [
        "[FRACTAL DAG EXECUTOR CORE]",
        "note: canonical executor runner demo",
        "note: ready sets are computed from nodes and edges",
        "note: Executor returns ResultProposal only",
        "note: non-atomic nodes create boundary snapshots, not uncontrolled recursion",
        "note: no real external actions",
        "note: not integrated into RootOrchestrator yet",
        "",
        "scenario | status | nodes | edges | ready_sequence | execution_batches | result_proposals | child_snapshots | cycle_detected | max_nodes_exceeded | executor_created_final_output | no_real_external_action | evidence",
    ]

    for row in rows:
        report = row.report
        lines.append(
            " | ".join(
                [
                    row.name,
                    report["status"],
                    str(len(row.plan_graph["nodes"])),
                    str(len(row.plan_graph["edges"])),
                    _seq(report["ready_sequence"]),
                    _seq(report["execution_batches"]),
                    str(len(report["result_proposals"])),
                    str(report["child_boundary_snapshots"]),
                    _bool_text(report["cycle_detected"]),
                    _bool_text(report["max_nodes_exceeded"]),
                    _bool_text(report["executor_created_final_output"]),
                    _bool_text(report["no_real_external_action"]),
                    "; ".join(report["evidence"]),
                ]
            )
        )

    successful = sum(1 for row in rows if row.report["status"] == "completed")
    blocked = len(rows) - successful
    proposal_total = sum(len(row.report["result_proposals"]) for row in rows)
    snapshots = sum(row.report["child_boundary_snapshots"] for row in rows)
    cycles = sum(1 for row in rows if row.report["cycle_detected"])
    max_nodes = sum(1 for row in rows if row.report["max_nodes_exceeded"])
    limited = sum(
        1
        for row in rows
        if row.report["budget_limits_applied"].get("parallelism_limited") is True
    )
    unhandled = sum(row.report["unhandled_exceptions"] for row in rows)
    executor_final = any(row.report["executor_created_final_output"] for row in rows)
    external_actions = any(not row.report["no_real_external_action"] for row in rows)

    lines.extend(
        [
            "",
            "[SUMMARY]",
            f"- scenarios: {len(rows)}",
            f"- successful_graphs: {successful}",
            f"- blocked_or_failed_graphs: {blocked}",
            f"- result_proposals_total: {proposal_total}",
            f"- child_boundary_snapshots: {snapshots}",
            f"- cycles_detected: {cycles}",
            f"- max_nodes_exceeded: {max_nodes}",
            f"- parallelism_limited_scenarios: {limited}",
            f"- executor_created_final_output: {_bool_text(executor_final)}",
            f"- no_real_external_actions: {_bool_text(not external_actions)}",
            f"- unhandled_exceptions: {unhandled}",
            "- next_step: Canonical Pipeline Trace v0.1 after Executor DAG core",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    print(render_report())


if __name__ == "__main__":
    main()
