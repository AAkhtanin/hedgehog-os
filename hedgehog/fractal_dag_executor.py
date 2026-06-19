from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from hedgehog.time_model import make_time_envelope


@dataclass(frozen=True)
class RunnerReport:
    runner_id: str
    plan_id: str
    status: str
    ready_sequence: list[list[str]]
    execution_batches: list[list[str]]
    result_proposals: list[dict]
    blocked_nodes: list[str]
    cycle_detected: bool
    max_nodes_exceeded: bool
    child_boundary_snapshots: int
    budget_limits_applied: dict
    executor_created_final_output: bool
    no_real_external_action: bool
    unhandled_exceptions: int
    evidence: list[str]

    def to_dict(self) -> dict:
        return {
            "runner_id": self.runner_id,
            "plan_id": self.plan_id,
            "status": self.status,
            "ready_sequence": self.ready_sequence,
            "execution_batches": self.execution_batches,
            "result_proposals": self.result_proposals,
            "blocked_nodes": self.blocked_nodes,
            "cycle_detected": self.cycle_detected,
            "max_nodes_exceeded": self.max_nodes_exceeded,
            "child_boundary_snapshots": self.child_boundary_snapshots,
            "budget_limits_applied": self.budget_limits_applied,
            "executor_created_final_output": self.executor_created_final_output,
            "no_real_external_action": self.no_real_external_action,
            "unhandled_exceptions": self.unhandled_exceptions,
            "evidence": self.evidence,
        }


def _node_id(node: dict) -> str:
    return str(node["node_id"])


def _node_deps(node: dict) -> list[str]:
    deps = node.get("deps", node.get("depends_on", []))
    return [str(dep) for dep in deps]


def _branch_budget(plan_graph: dict) -> dict:
    budget = plan_graph.get("branch_budget") or {}
    return {
        "max_depth": int(budget.get("max_depth", 8)),
        "max_parallelism": max(1, int(budget.get("max_parallelism", 4))),
        "max_nodes": max(1, int(budget.get("max_nodes", 64))),
    }


def _dependency_map(plan_graph: dict) -> tuple[dict[str, set[str]], dict[str, dict], list[str]]:
    nodes = plan_graph.get("nodes") or []
    nodes_by_id = {_node_id(node): node for node in nodes}
    order = [_node_id(node) for node in nodes]
    dependencies = {node_id: set(_node_deps(node)) for node_id, node in nodes_by_id.items()}

    for edge in plan_graph.get("edges") or []:
        from_id = str(edge.get("from", ""))
        to_id = str(edge.get("to", ""))
        if to_id in dependencies and from_id:
            dependencies[to_id].add(from_id)

    return dependencies, nodes_by_id, order


def _has_cycle(dependencies: dict[str, set[str]]) -> bool:
    node_ids = set(dependencies)
    remaining = {node_id: set(deps) for node_id, deps in dependencies.items()}
    completed: set[str] = set()

    while remaining:
        ready = [
            node_id
            for node_id, deps in remaining.items()
            if deps <= completed and deps <= node_ids
        ]
        if not ready:
            return True
        for node_id in ready:
            completed.add(node_id)
            del remaining[node_id]

    return False


def _unknown_dependency_nodes(dependencies: dict[str, set[str]]) -> list[str]:
    known = set(dependencies)
    return sorted(
        node_id for node_id, deps in dependencies.items() if any(dep not in known for dep in deps)
    )


def _atomic_payload(node: dict) -> dict:
    return {
        "status": "completed",
        "atomic": True,
        "node_id": _node_id(node),
        "task_kind": node.get("task_kind", "atomic_task"),
        "vector_id": node.get("vector_id", "unknown_vector"),
        "task_completed": True,
        "executed_domain_action": False,
        "global_commit_claimed": False,
        "payload": node.get("payload", {}),
    }


def _child_boundary_payload(node: dict) -> dict:
    return {
        "status": "boundary_snapshot",
        "atomic": False,
        "node_id": _node_id(node),
        "task_kind": node.get("task_kind", "child_cell"),
        "vector_id": node.get("vector_id", "unknown_vector"),
        "task_completed": False,
        "child_cell_placeholder": True,
        "not_executed_in_v0_1": True,
        "root_does_not_manage_internal_state": True,
        "executed_domain_action": False,
        "global_commit_claimed": False,
        "payload": {
            "boundary_snapshot": node.get("payload", {}),
            "local_authority_only": True,
        },
    }


def _make_result_proposal(
    plan_graph: dict,
    node: dict,
    session_anchor: str,
) -> dict:
    plan_id = str(plan_graph.get("plan_id", "plan:unknown"))
    node_id = _node_id(node)
    atomic = bool(node.get("atomic", True))
    payload = _atomic_payload(node) if atomic else _child_boundary_payload(node)
    proposal = {
        "proposal_id": f"rp:{plan_id}:{node_id}",
        "request_id": str(plan_graph.get("request_id", f"req:{plan_id}")),
        "producer": {
            "executor_id": str(node.get("executor_id", "fractal_dag_executor")),
            "model_id": "fractal_dag_executor_v0_1",
        },
        "vector_id": str(node.get("vector_id", "unknown_vector")),
        "plan_id": plan_id,
        "result_payload": payload,
        "evidence": [
            {
                "kind": "fractal_dag_executor",
                "summary": (
                    "Executed atomic DAG node without external action."
                    if atomic
                    else "Created child-cell boundary snapshot without recursion."
                ),
                "ref_id": node_id,
                "confidence": 1.0,
            }
        ],
        "cost": {
            "tokens": 0,
            "walltime_ms": int(node.get("estimated_cost", 0) or 0),
            "toolcalls": 0,
        },
        "risks": [],
        "time_envelope": make_time_envelope(session_anchor),
        "trace_refs": [
            {
                "trace_id": f"trace:{plan_id}",
                "span_id": node_id,
                "kind": "fractal_dag_executor_node",
            }
        ],
    }
    return proposal


def run_fractal_dag_executor(
    plan_graph: dict[str, Any],
    *,
    runner_id: str = "fractal_dag_runner_v0_1",
    session_anchor: str = "fractal_dag_executor_session",
) -> dict:
    plan_id = str(plan_graph.get("plan_id", "plan:unknown"))
    budget = _branch_budget(plan_graph)
    nodes = plan_graph.get("nodes") or []
    budget_limits_applied = {
        "parallelism_limited": False,
        "max_nodes": budget["max_nodes"],
        "max_parallelism": budget["max_parallelism"],
        "max_depth": budget["max_depth"],
    }

    if len(nodes) > budget["max_nodes"]:
        return RunnerReport(
            runner_id=runner_id,
            plan_id=plan_id,
            status="blocked",
            ready_sequence=[],
            execution_batches=[],
            result_proposals=[],
            blocked_nodes=[_node_id(node) for node in nodes],
            cycle_detected=False,
            max_nodes_exceeded=True,
            child_boundary_snapshots=0,
            budget_limits_applied=budget_limits_applied,
            executor_created_final_output=False,
            no_real_external_action=True,
            unhandled_exceptions=0,
            evidence=["max_nodes_exceeded: execution blocked before any node ran"],
        ).to_dict()

    dependencies, nodes_by_id, order = _dependency_map(plan_graph)
    blocked_unknown = _unknown_dependency_nodes(dependencies)
    cycle_detected = _has_cycle(dependencies)
    if cycle_detected or blocked_unknown:
        reason = "cycle_detected: execution blocked before any node ran"
        if blocked_unknown:
            reason = "unknown_dependency: execution blocked before any node ran"
        return RunnerReport(
            runner_id=runner_id,
            plan_id=plan_id,
            status="blocked",
            ready_sequence=[],
            execution_batches=[],
            result_proposals=[],
            blocked_nodes=blocked_unknown or order,
            cycle_detected=cycle_detected,
            max_nodes_exceeded=False,
            child_boundary_snapshots=0,
            budget_limits_applied=budget_limits_applied,
            executor_created_final_output=False,
            no_real_external_action=True,
            unhandled_exceptions=0,
            evidence=[reason],
        ).to_dict()

    completed: set[str] = set()
    executed: set[str] = set()
    ready_sequence: list[list[str]] = []
    execution_batches: list[list[str]] = []
    result_proposals: list[dict] = []
    child_boundary_snapshots = 0

    while len(completed) < len(order):
        ready = [
            node_id
            for node_id in order
            if node_id not in executed and dependencies[node_id] <= completed
        ]
        if not ready:
            return RunnerReport(
                runner_id=runner_id,
                plan_id=plan_id,
                status="failed",
                ready_sequence=ready_sequence,
                execution_batches=execution_batches,
                result_proposals=result_proposals,
                blocked_nodes=[node_id for node_id in order if node_id not in completed],
                cycle_detected=False,
                max_nodes_exceeded=False,
                child_boundary_snapshots=child_boundary_snapshots,
                budget_limits_applied=budget_limits_applied,
                executor_created_final_output=False,
                no_real_external_action=True,
                unhandled_exceptions=0,
                evidence=["no_ready_nodes: execution stopped without external side effects"],
            ).to_dict()

        ready_sequence.append(list(ready))
        if len(ready) > budget["max_parallelism"]:
            budget_limits_applied["parallelism_limited"] = True
        batch = ready[: budget["max_parallelism"]]
        execution_batches.append(list(batch))

        for node_id in batch:
            node = nodes_by_id[node_id]
            result_proposals.append(
                _make_result_proposal(plan_graph, node, session_anchor)
            )
            if not bool(node.get("atomic", True)):
                child_boundary_snapshots += 1
            executed.add(node_id)
            completed.add(node_id)

    return RunnerReport(
        runner_id=runner_id,
        plan_id=plan_id,
        status="completed",
        ready_sequence=ready_sequence,
        execution_batches=execution_batches,
        result_proposals=result_proposals,
        blocked_nodes=[],
        cycle_detected=False,
        max_nodes_exceeded=False,
        child_boundary_snapshots=child_boundary_snapshots,
        budget_limits_applied=budget_limits_applied,
        executor_created_final_output=False,
        no_real_external_action=True,
        unhandled_exceptions=0,
        evidence=["completed: ready sets computed from local PlanGraph dependencies"],
    ).to_dict()
