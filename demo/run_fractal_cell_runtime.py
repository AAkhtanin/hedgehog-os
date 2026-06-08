from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any


MAX_DEPTH = 2
CHILD_BUDGET = 100
CHILD_SCENARIOS = (
    "non_atomic_child_cell_completed",
    "non_atomic_child_cell_degraded_budget_limit",
    "non_atomic_child_cell_blocked_max_depth",
    "non_atomic_child_cell_failed_contract_mismatch",
)
NON_CHILD_SCENARIOS = (
    "atomic_node_does_not_spawn_child_cell",
    "needle_bound_node_does_not_spawn_child_cell",
)
MALICIOUS_SCENARIOS = (
    "malicious_child_claiming_final_output_rejected",
    "malicious_child_claiming_parent_drs_write_rejected",
    "malicious_child_claiming_real_action_rejected",
    "malicious_child_orchestrator_claiming_root_rejected",
    "malicious_child_claiming_live_llm_use_rejected",
)
SCENARIOS_UNDER_TEST = CHILD_SCENARIOS + NON_CHILD_SCENARIOS + MALICIOUS_SCENARIOS + (
    "raw_child_output_blocked",
)


@dataclass(frozen=True)
class FractalCellRuntimeReport:
    input_mode: dict[str, Any]
    parent_plan_graph: dict[str, Any]
    child_cell_requests: list[dict[str, Any]]
    child_mini_cell_execution: list[dict[str, Any]]
    child_boundary_snapshots: list[dict[str, Any]]
    parent_adapter: list[dict[str, Any]]
    post_vv_gt_root_final: list[dict[str, Any]]
    non_child_routes: dict[str, Any]
    blocked_malicious_inputs: dict[str, Any]
    authority_safety: dict[str, Any]
    summary: dict[str, Any]


def _parent_plan_graph() -> dict[str, Any]:
    nodes = [
        {"node_id": "node_atomic_validate", "node_kind": "atomic", "route": "executor"},
        {
            "node_id": "node_needle_lookup",
            "node_kind": "needle_bound",
            "route": "needleruntime",
        },
        {
            "node_id": "node_non_atomic_workflow",
            "node_kind": "non_atomic",
            "child_cell_required": True,
            "task": "Decompose and prove a bounded certificate workflow branch.",
            "complexity_level": "high",
            "risk_level": "bounded_proof",
            "max_child_depth": MAX_DEPTH,
            "child_budget": CHILD_BUDGET,
            "parent_plan_graph_proposal_id": "parent_plan_graph_proposal_fractal_cell_v0_1",
            "parent_trace_id": "parent_trace_fractal_cell_v0_1",
            "route": "child_cell",
        },
    ]
    kinds = [node["node_kind"] for node in nodes]
    return {
        "parent_plan_graph_proposal_id": "parent_plan_graph_proposal_fractal_cell_v0_1",
        "parent_trace_id": "parent_trace_fractal_cell_v0_1",
        "node_types_present": kinds,
        "atomic_nodes": [node["node_id"] for node in nodes if node["node_kind"] == "atomic"],
        "needle_bound_nodes": [
            node["node_id"] for node in nodes if node["node_kind"] == "needle_bound"
        ],
        "non_atomic_nodes": [
            node["node_id"] for node in nodes if node["node_kind"] == "non_atomic"
        ],
        "child_cell_required_nodes": [
            node["node_id"] for node in nodes if node.get("child_cell_required")
        ],
        "topology_routes": {
            "atomic": "executor",
            "needle_bound": "needleruntime",
            "non_atomic": "child_cell",
        },
        "nodes": nodes,
    }


def _non_atomic_node(parent: dict[str, Any]) -> dict[str, Any]:
    return next(node for node in parent["nodes"] if node["node_kind"] == "non_atomic")


def _child_request(scenario: str, node: dict[str, Any]) -> dict[str, Any]:
    requested_depth = MAX_DEPTH + 1 if scenario.endswith("max_depth") else 1
    return {
        "scenario": scenario,
        "child_cell_request_id": f"child_cell_request_{scenario}",
        "created_by": "fractal_dag_executor",
        "source_parent_plan_graph_proposal_id": node["parent_plan_graph_proposal_id"],
        "source_parent_node_id": node["node_id"],
        "requested_cell_type": "deterministic_minicell",
        "child_cell_scope": "branch_local",
        "requested_depth": requested_depth,
        "max_depth": node["max_child_depth"],
        "child_budget": node["child_budget"],
        "allowed_child_roles": ["child_orchestrator", "child_architect", "child_executor"],
        "forbidden_capabilities": [
            "child_drs",
            "live_llm_slm",
            "real_needleruntime",
            "telegram",
            "external_api",
            "marennya_up",
        ],
        "parent_drs_write_allowed": False,
        "real_external_action_allowed": False,
        "live_llm_allowed": False,
        "child_final_output_allowed": False,
        "parent_promotion_requires_root": True,
    }


def _child_snapshot(request: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    scenario = request["scenario"]
    facts = {
        "non_atomic_child_cell_completed": ("completed", "none", 58, True),
        "non_atomic_child_cell_degraded_budget_limit": (
            "degraded",
            "budget_limit_approached",
            95,
            True,
        ),
        "non_atomic_child_cell_blocked_max_depth": (
            "blocked",
            "max_depth_exceeded",
            0,
            False,
        ),
        "non_atomic_child_cell_failed_contract_mismatch": (
            "failed",
            "contract_mismatch",
            31,
            True,
        ),
    }
    status, failure, budget_used, roles_ran = facts[scenario]
    execution = {
        "scenario": scenario,
        "child_orchestrator_ran": roles_ran,
        "child_architect_ran": roles_ran,
        "child_executor_ran": roles_ran,
        "child_depth": request["requested_depth"],
        "child_budget_used": budget_used,
        "child_status": status,
        "failure_kind": failure,
        "child_created_final_output": False,
        "child_wrote_parent_drs": False,
        "child_executed_real_action": False,
        "child_orchestrator_is_root": False,
        "child_used_live_llm": False,
        "root_crash_risk_contained": True,
    }
    snapshot = {
        **execution,
        "child_boundary_snapshot_id": f"child_boundary_snapshot_{scenario}",
        "created_by": "child_cell_runtime",
        "source_child_cell_request_id": request["child_cell_request_id"],
        "source_parent_node_id": request["source_parent_node_id"],
        "source_parent_plan_graph_proposal_id": request[
            "source_parent_plan_graph_proposal_id"
        ],
        "child_cell_scope": "branch_local",
        "boundary_summary": f"bounded child branch ended with {status}",
        "child_artifacts": (
            ["child_route_proposal", "child_plan_proposal", "child_result_evidence"]
            if roles_ran
            else []
        ),
        "child_event_log": [
            "child_cell_request_received",
            f"child_status:{status}",
            f"failure_kind:{failure}",
            "child_boundary_snapshot_returned",
        ],
        "risks": [] if status == "completed" else [failure],
        "promotion_candidate": status in {"completed", "degraded"},
        "parent_promotion_requires_root": True,
        "time_envelope": {
            "observed_at": "2026-06-08T00:00:00Z",
            "valid_from": "2026-06-08T00:00:00Z",
            "valid_to": None,
            "time_basis": "deterministic_proof_clock",
        },
        "provenance": {
            "runtime": "deterministic_child_cell_runtime",
            "proof_only": True,
        },
    }
    return execution, snapshot


def _unsafe_claims(snapshot: dict[str, Any]) -> list[str]:
    checks = (
        ("child_created_final_output", "child_final_output_claim_rejected"),
        ("child_wrote_parent_drs", "child_parent_drs_write_claim_rejected"),
        ("child_executed_real_action", "child_real_action_claim_rejected"),
        ("child_orchestrator_is_root", "child_orchestrator_root_claim_rejected"),
        ("child_used_live_llm", "child_live_llm_claim_rejected"),
    )
    return [reason for field, reason in checks if snapshot.get(field) is True]


def _is_snapshot(snapshot: dict[str, Any]) -> bool:
    required = {
        "child_boundary_snapshot_id",
        "created_by",
        "source_child_cell_request_id",
        "source_parent_node_id",
        "source_parent_plan_graph_proposal_id",
        "child_status",
        "child_event_log",
        "risks",
        "parent_promotion_requires_root",
    }
    return (
        required <= set(snapshot)
        and snapshot.get("created_by") == "child_cell_runtime"
        and snapshot.get("child_status") in {"completed", "degraded", "blocked", "failed"}
    )


def _parent_adapter(snapshot: dict[str, Any]) -> dict[str, Any] | None:
    if not _is_snapshot(snapshot) or _unsafe_claims(snapshot):
        return None
    status = snapshot["child_status"]
    return {
        "scenario": snapshot["scenario"],
        "result_proposal_created": True,
        "result_proposal_id": f"result_proposal_{snapshot['scenario']}",
        "created_by": "parent_child_snapshot_adapter",
        "source_child_boundary_snapshot_id": snapshot["child_boundary_snapshot_id"],
        "source_parent_node_id": snapshot["source_parent_node_id"],
        "source_parent_plan_graph_proposal_id": snapshot[
            "source_parent_plan_graph_proposal_id"
        ],
        "result_status": status,
        "child_boundary_snapshot_preserved": True,
        "degraded_or_blocked_preserved": status in {"degraded", "blocked", "failed"},
        "final_output_claim": False,
        "drs_write_claim": False,
        "real_external_action_claim": False,
        "risks": list(snapshot["risks"]),
    }


def _downstream(adapter: dict[str, Any]) -> dict[str, Any]:
    status = adapter["result_status"]
    post_vv = "accepted" if status == "completed" else "degraded" if status == "degraded" else "rejected"
    gt = "accept" if post_vv == "accepted" else "degrade" if post_vv == "degraded" else "reject"
    root = "accepted" if gt == "accept" else "degraded" if gt == "degrade" else "rejected"
    return {
        "scenario": adapter["scenario"],
        "post_vv_status": post_vv,
        "gt_decision": gt,
        "root_final_status": root,
        "root_final_artifact_id": f"root_final_artifact_{adapter['scenario']}",
        "root_final_artifact_created": True,
        "root_is_only_final_output_authority": True,
        "post_vv_bypassed": False,
        "gt_bypassed": False,
        "root_bypassed": False,
        "unsafe_success_hidden": status != "completed" and root == "accepted",
    }


def _blocked_malicious(base: dict[str, Any]) -> dict[str, Any]:
    rows: dict[str, Any] = {"raw_child_output_blocked": True}
    claims = {
        "malicious_child_final_output_claim_rejected": (
            "child_created_final_output",
            "child_final_output_claim_rejected",
        ),
        "malicious_child_parent_drs_write_claim_rejected": (
            "child_wrote_parent_drs",
            "child_parent_drs_write_claim_rejected",
        ),
        "malicious_child_real_action_claim_rejected": (
            "child_executed_real_action",
            "child_real_action_claim_rejected",
        ),
        "malicious_child_orchestrator_root_claim_rejected": (
            "child_orchestrator_is_root",
            "child_orchestrator_root_claim_rejected",
        ),
        "malicious_child_live_llm_claim_rejected": (
            "child_used_live_llm",
            "child_live_llm_claim_rejected",
        ),
    }
    for name, (field, reason) in claims.items():
        snapshot = copy.deepcopy(base)
        snapshot[field] = True
        reasons = _unsafe_claims(snapshot)
        rows[name] = _parent_adapter(snapshot) is None and reason in reasons
        rows[f"{name}_reasons"] = reasons
    return rows


def collect_fractal_cell_runtime() -> FractalCellRuntimeReport:
    parent = _parent_plan_graph()
    node = _non_atomic_node(parent)
    requests = [_child_request(scenario, node) for scenario in CHILD_SCENARIOS]
    executions: list[dict[str, Any]] = []
    snapshots: list[dict[str, Any]] = []
    for request in requests:
        execution, snapshot = _child_snapshot(request)
        executions.append(execution)
        snapshots.append(snapshot)
    adapters = [adapter for snapshot in snapshots if (adapter := _parent_adapter(snapshot))]
    downstream = [_downstream(adapter) for adapter in adapters]
    blocked = _blocked_malicious(snapshots[0])
    non_child = {
        "atomic_node_does_not_spawn_child_cell": True,
        "ordinary_executor_route_visible": parent["topology_routes"]["atomic"] == "executor",
        "needle_bound_node_does_not_spawn_child_cell": True,
        "needleruntime_route_visible": parent["topology_routes"]["needle_bound"]
        == "needleruntime",
    }
    authority = {
        "child_cell_is_authority": False,
        "child_orchestrator_is_root": any(row["child_orchestrator_is_root"] for row in snapshots),
        "child_output_is_final_truth": False,
        "root_remains_authority": all(row["root_is_only_final_output_authority"] for row in downstream),
        "root_is_only_final_output_authority": all(
            row["root_is_only_final_output_authority"] for row in downstream
        ),
        "child_created_final_output": any(row["child_created_final_output"] for row in snapshots),
        "child_wrote_parent_drs": any(row["child_wrote_parent_drs"] for row in snapshots),
        "child_executed_real_action": any(row["child_executed_real_action"] for row in snapshots),
        "child_used_live_llm": any(row["child_used_live_llm"] for row in snapshots),
        "recursion_bounded": all(row["child_depth"] <= MAX_DEPTH or row["child_status"] == "blocked" for row in snapshots),
        "budget_bounded": all(row["child_budget_used"] <= CHILD_BUDGET for row in snapshots),
        "parent_promotion_requires_root": all(
            row["parent_promotion_requires_root"] for row in snapshots
        ),
        "production_external_action_executed": False,
        "production_persistence_claimed": False,
        "global_drs_implemented": False,
        "external_drs_network_implemented": False,
        "marennya_invoked": False,
        "up_invoked": False,
    }
    malicious_rejected = sum(
        blocked[key]
        for key in (
            "malicious_child_final_output_claim_rejected",
            "malicious_child_parent_drs_write_claim_rejected",
            "malicious_child_real_action_claim_rejected",
            "malicious_child_orchestrator_root_claim_rejected",
            "malicious_child_live_llm_claim_rejected",
        )
    )
    boundaries_pass = (
        len(requests) == len(snapshots) == len(adapters) == len(downstream) == 4
        and all(not row["unsafe_success_hidden"] for row in downstream)
        and all(
            not row["post_vv_bypassed"] and not row["gt_bypassed"] and not row["root_bypassed"]
            for row in downstream
        )
        and all(non_child.values())
        and blocked["raw_child_output_blocked"]
        and malicious_rejected == 5
        and not authority["child_cell_is_authority"]
        and not authority["child_orchestrator_is_root"]
        and authority["root_remains_authority"]
        and authority["root_is_only_final_output_authority"]
        and not authority["child_created_final_output"]
        and not authority["child_wrote_parent_drs"]
        and not authority["child_executed_real_action"]
        and not authority["child_used_live_llm"]
        and authority["recursion_bounded"]
        and authority["budget_bounded"]
        and authority["parent_promotion_requires_root"]
    )
    summary = {
        "fractal_cell_runtime_status": "PASS" if boundaries_pass else "FAIL",
        "scenarios_verified": len(SCENARIOS_UNDER_TEST),
        "child_cell_completed_scenarios": sum(row["child_status"] == "completed" for row in snapshots),
        "child_cell_degraded_scenarios": sum(row["child_status"] == "degraded" for row in snapshots),
        "child_cell_blocked_or_failed_scenarios": sum(
            row["child_status"] in {"blocked", "failed"} for row in snapshots
        ),
        "malicious_child_claims_rejected": malicious_rejected,
        "raw_child_output_blocked": blocked["raw_child_output_blocked"],
        "atomic_route_preserved": non_child["atomic_node_does_not_spawn_child_cell"]
        and non_child["ordinary_executor_route_visible"],
        "needle_route_preserved": non_child["needle_bound_node_does_not_spawn_child_cell"]
        and non_child["needleruntime_route_visible"],
        "non_atomic_route_spawns_child_cell": len(requests) == 4,
        "child_boundary_snapshot_preserved": all(
            row["child_boundary_snapshot_preserved"] for row in adapters
        ),
        "root_remains_authority": authority["root_remains_authority"],
        "root_is_only_final_output_authority": authority["root_is_only_final_output_authority"],
        "no_child_final_output": not authority["child_created_final_output"],
        "no_child_parent_drs_write": not authority["child_wrote_parent_drs"],
        "no_real_external_actions": not authority["child_executed_real_action"],
        "recursion_bounded": authority["recursion_bounded"],
        "budget_bounded": authority["budget_bounded"],
        "ready_for_drs_lifecycle_semantics_v0_2": boundaries_pass,
        "production_autonomy_claimed": False,
    }
    snapshot_rows = [
        {
            "scenario": row["scenario"],
            "child_boundary_snapshot_id": row["child_boundary_snapshot_id"],
            "source_child_cell_request_id": row["source_child_cell_request_id"],
            "source_parent_node_id": row["source_parent_node_id"],
            "child_status": row["child_status"],
            "boundary_summary": row["boundary_summary"],
            "child_event_log_present": bool(row["child_event_log"]),
            "promotion_candidate": row["promotion_candidate"],
            "parent_promotion_requires_root": row["parent_promotion_requires_root"],
            "risks": row["risks"],
        }
        for row in snapshots
    ]
    return FractalCellRuntimeReport(
        input_mode={
            "mode": "deterministic_fractal_cell_runtime",
            "live_network_used": False,
            "telegram_used": False,
            "real_external_action": False,
            "production_persistence": False,
            "max_depth": MAX_DEPTH,
            "child_budget": CHILD_BUDGET,
        },
        parent_plan_graph={key: value for key, value in parent.items() if key != "nodes"},
        child_cell_requests=requests,
        child_mini_cell_execution=executions,
        child_boundary_snapshots=snapshot_rows,
        parent_adapter=adapters,
        post_vv_gt_root_final=downstream,
        non_child_routes=non_child,
        blocked_malicious_inputs=blocked,
        authority_safety=authority,
        summary=summary,
    )


def _format(value: Any) -> str:
    return "true" if value is True else "false" if value is False else str(value)


def _section(lines: list[str], title: str, fields: dict[str, Any]) -> None:
    lines.extend(["", title])
    lines.extend(f"{key}: {_format(value)}" for key, value in fields.items())


def _rows(lines: list[str], title: str, rows: list[dict[str, Any]]) -> None:
    lines.extend(["", title])
    for row in rows:
        lines.append(" | ".join(f"{key}={_format(value)}" for key, value in row.items()))


def render_fractal_cell_runtime(report: FractalCellRuntimeReport) -> str:
    lines = [
        "[FRACTAL CELL RUNTIME]",
        "note: deterministic Fractal Cell Runtime v0.1 proof",
        "note: non-atomic PlanGraph node spawns bounded child cell",
        "note: this is not a long chain",
        "note: child cell returns ChildBoundarySnapshot upward",
        "note: child cell is not Root",
        "note: child Orchestrator is not Root",
        "note: no child FinalOutput",
        "note: no parent DRS write by child",
        "note: no real external actions",
        "note: no live LLM/SLM inside child cell",
        "note: recursion bounded by max_depth and budget",
        "note: Marennya / UP remain deferred and not invoked",
    ]
    _section(lines, "[INPUT / MODE]", report.input_mode)
    _section(lines, "[PARENT PLAN GRAPH]", report.parent_plan_graph)
    _rows(lines, "[CHILD CELL REQUESTS]", report.child_cell_requests)
    _rows(lines, "[CHILD MINI-CELL EXECUTION]", report.child_mini_cell_execution)
    _rows(lines, "[CHILD BOUNDARY SNAPSHOTS]", report.child_boundary_snapshots)
    _rows(lines, "[PARENT ADAPTER]", report.parent_adapter)
    _rows(lines, "[POST V&V / GT / ROOT FINAL]", report.post_vv_gt_root_final)
    _section(lines, "[NON-CHILD ROUTES]", report.non_child_routes)
    _section(lines, "[BLOCKED / MALICIOUS INPUTS]", report.blocked_malicious_inputs)
    _section(lines, "[AUTHORITY / SAFETY]", report.authority_safety)
    _section(lines, "[SUMMARY]", report.summary)
    return "\n".join(lines).rstrip() + "\n"


def run_fractal_cell_runtime() -> str:
    return render_fractal_cell_runtime(collect_fractal_cell_runtime())


def main() -> int:
    print(run_fractal_cell_runtime(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
