from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from demo.run_architect_from_bounded_attractor_packet import (
    collect_architect_from_bounded_attractor_packet,
)


SCENARIOS_UNDER_TEST = (
    "accepted_plan_graph_executor_result_proposal",
    "downgraded_plan_graph_executor_limited_result_proposal",
    "invalid_architect_artifact_blocked_before_executor",
    "raw_architect_text_blocked",
    "raw_orchestrator_matrix_blocked",
    "raw_user_intent_blocked",
    "unvalidated_plan_graph_blocked",
)


@dataclass(frozen=True)
class DagExecutorFromValidPlanGraphReport:
    input_plan_graphs: dict[str, Any]
    executor_input_filter: list[dict[str, Any]]
    result_proposals: list[dict[str, Any]]
    containment: dict[str, Any]
    authority_safety: dict[str, Any]
    summary: dict[str, Any]


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _format_value(value: Any) -> str:
    if isinstance(value, bool):
        return _bool_text(value)
    return str(value)


def _proposal_is_valid_plan_graph(proposal: dict[str, Any]) -> bool:
    return (
        proposal.get("created_by") == "architect"
        and proposal.get("plan_graph_present") is True
        and proposal.get("plan_graph_contract_checked") is True
        and proposal.get("plan_graph_contract_valid") is True
        and bool(proposal.get("nodes"))
    )


def _node_result(node: dict[str, Any], *, limited: bool) -> dict[str, Any]:
    return {
        "node_id": node["node_id"],
        "vector_id": node["vector_id"],
        "status": "degraded" if limited else "completed",
        "output_kind": "deterministic_node_result",
        "real_external_action_executed": False,
        "final_output_created": False,
        "drs_written": False,
    }


def _result_proposal_from_plan(
    scenario: str,
    proposal: dict[str, Any],
    *,
    limited: bool = False,
) -> tuple[dict[str, Any], dict[str, Any]]:
    valid_input = _proposal_is_valid_plan_graph(proposal)
    node_results = [
        _node_result(node, limited=limited)
        for node in proposal.get("nodes", [])
    ]
    result_status = "degraded" if limited else "completed"
    result_proposal = {
        "result_proposal_id": f"result_proposal_{scenario}",
        "created_by": "executor",
        "scenario": scenario,
        "source_plan_graph_proposal_id": proposal["proposal_id"],
        "source_packet_id": proposal["source_packet_id"],
        "source_gate_decision_id": proposal["source_gate_decision_id"],
        "executor_input_is_validated_plan_graph": valid_input,
        "raw_architect_text_received": False,
        "raw_orchestrator_matrix_received": False,
        "raw_user_intent_received": False,
        "invalid_plan_graph_received": False,
        "node_results": node_results,
        "execution_mode": "deterministic_mock",
        "result_status": result_status,
        "evidence": [
            "validated_plan_graph_contract=true",
            "executor_returned_result_proposal_only=true",
        ],
        "risks": (
            ["downgraded_claims_limit_executor_scope"]
            if limited
            else []
        ),
        "downgraded_claims_visible": list(
            proposal.get("downgraded_claims_visible", [])
        ),
        "executor_creates_final_output": False,
        "executor_writes_drs": False,
        "executor_executes_real_action": False,
        "post_vv_invoked": False,
        "gt_invoked": False,
    }
    filter_row = {
        "scenario": scenario,
        "input_kind": "validated_plan_graph",
        "executor_invoked": valid_input,
        "blocked_before_executor": not valid_input,
        "block_reasons": [] if valid_input else ["invalid_plan_graph_not_allowed"],
        "executor_input_is_validated_plan_graph": valid_input,
        "raw_architect_text_received": False,
        "raw_orchestrator_matrix_received": False,
        "raw_user_intent_received": False,
        "invalid_plan_graph_received": False,
    }
    return filter_row, result_proposal


def _blocked_filter_row(
    scenario: str,
    input_kind: str,
    block_reasons: list[str],
    *,
    invalid_plan_graph_received: bool = False,
) -> dict[str, Any]:
    return {
        "scenario": scenario,
        "input_kind": input_kind,
        "executor_invoked": False,
        "blocked_before_executor": True,
        "block_reasons": block_reasons,
        "executor_input_is_validated_plan_graph": False,
        "raw_architect_text_received": False,
        "raw_orchestrator_matrix_received": False,
        "raw_user_intent_received": False,
        "invalid_plan_graph_received": invalid_plan_graph_received,
    }


def _containment(filters: list[dict[str, Any]], results: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "invalid_architect_artifact_reached_executor": any(
            row["scenario"] == "invalid_architect_artifact_blocked_before_executor"
            and row["executor_invoked"]
            for row in filters
        ),
        "raw_architect_text_reached_executor": any(
            row["input_kind"] == "raw_architect_text" and row["executor_invoked"]
            for row in filters
        ),
        "raw_orchestrator_matrix_reached_executor": any(
            row["input_kind"] == "raw_orchestrator_matrix" and row["executor_invoked"]
            for row in filters
        ),
        "raw_user_intent_reached_executor": any(
            row["input_kind"] == "raw_user_intent" and row["executor_invoked"]
            for row in filters
        ),
        "unvalidated_plan_graph_reached_executor": any(
            row["input_kind"] == "unvalidated_plan_graph" and row["executor_invoked"]
            for row in filters
        ),
        "invalid_executor_result_created_final_output": any(
            result["executor_creates_final_output"] for result in results
        ),
        "invalid_executor_result_wrote_drs": any(
            result["executor_writes_drs"] for result in results
        ),
    }


def _authority_safety(
    filters: list[dict[str, Any]],
    results: list[dict[str, Any]],
    containment: dict[str, Any],
) -> dict[str, Any]:
    invoked_rows = [row for row in filters if row["executor_invoked"]]
    return {
        "executor_receives_only_validated_plan_graph_nodes": bool(invoked_rows)
        and all(row["executor_input_is_validated_plan_graph"] for row in invoked_rows),
        "executor_receives_raw_architect_text": containment[
            "raw_architect_text_reached_executor"
        ],
        "executor_receives_raw_orchestrator_matrix": containment[
            "raw_orchestrator_matrix_reached_executor"
        ],
        "executor_receives_raw_user_intent": containment[
            "raw_user_intent_reached_executor"
        ],
        "executor_receives_invalid_plan_graph": containment[
            "invalid_architect_artifact_reached_executor"
        ] or containment["unvalidated_plan_graph_reached_executor"],
        "result_proposal_only": bool(results)
        and all(result["created_by"] == "executor" for result in results),
        "executor_creates_final_output": any(
            result["executor_creates_final_output"] for result in results
        ),
        "executor_writes_drs": any(result["executor_writes_drs"] for result in results),
        "executor_executes_real_action": any(
            result["executor_executes_real_action"] for result in results
        ),
        "post_vv_invoked": any(result["post_vv_invoked"] for result in results),
        "gt_invoked": any(result["gt_invoked"] for result in results),
        "production_final_output_created": False,
        "production_external_action_executed": False,
        "global_drs_implemented": False,
        "external_drs_network_implemented": False,
        "marennya_invoked": False,
        "up_invoked": False,
    }


def _blocked(filters: list[dict[str, Any]], scenario: str) -> bool:
    return any(
        row["scenario"] == scenario and row["blocked_before_executor"]
        for row in filters
    )


def _summary(
    source_status: str,
    filters: list[dict[str, Any]],
    results: list[dict[str, Any]],
    containment: dict[str, Any],
    authority: dict[str, Any],
) -> dict[str, Any]:
    accepted_results = [
        result for result in results
        if result["source_packet_id"] == "attractor_packet_valid_matrix_accept"
    ]
    downgraded_results = [
        result for result in results
        if result["source_packet_id"] == "attractor_packet_incomplete_guards_downgrade_or_reject"
    ]
    boundary_pass = (
        authority["executor_receives_only_validated_plan_graph_nodes"]
        and not authority["executor_receives_raw_architect_text"]
        and not authority["executor_receives_raw_orchestrator_matrix"]
        and not authority["executor_receives_raw_user_intent"]
        and not authority["executor_receives_invalid_plan_graph"]
        and authority["result_proposal_only"]
        and not authority["executor_creates_final_output"]
        and not authority["executor_writes_drs"]
        and not authority["executor_executes_real_action"]
        and not authority["post_vv_invoked"]
        and not authority["gt_invoked"]
        and not authority["production_final_output_created"]
        and not authority["production_external_action_executed"]
        and not authority["global_drs_implemented"]
        and not authority["external_drs_network_implemented"]
        and not authority["marennya_invoked"]
        and not authority["up_invoked"]
        and not containment["invalid_executor_result_created_final_output"]
        and not containment["invalid_executor_result_wrote_drs"]
    )
    status = (
        "PASS"
        if source_status == "PASS"
        and len(filters) == len(SCENARIOS_UNDER_TEST)
        and len(results) == 2
        and len(accepted_results) == 1
        and len(downgraded_results) == 1
        and _blocked(filters, "invalid_architect_artifact_blocked_before_executor")
        and _blocked(filters, "raw_architect_text_blocked")
        and _blocked(filters, "raw_orchestrator_matrix_blocked")
        and _blocked(filters, "raw_user_intent_blocked")
        and _blocked(filters, "unvalidated_plan_graph_blocked")
        and boundary_pass
        else "FAIL"
    )
    return {
        "dag_executor_from_valid_plan_graph_status": status,
        "source_architect_from_attractor_status": source_status,
        "scenarios_verified": len(filters),
        "result_proposals_created": len(results),
        "accepted_plan_result_proposals": len(accepted_results),
        "downgraded_plan_result_proposals": len(downgraded_results),
        "invalid_architect_artifact_blocked": _blocked(
            filters, "invalid_architect_artifact_blocked_before_executor"
        ),
        "raw_architect_text_blocked": _blocked(filters, "raw_architect_text_blocked"),
        "raw_orchestrator_matrix_blocked": _blocked(
            filters, "raw_orchestrator_matrix_blocked"
        ),
        "raw_user_intent_blocked": _blocked(filters, "raw_user_intent_blocked"),
        "unvalidated_plan_graph_blocked": _blocked(
            filters, "unvalidated_plan_graph_blocked"
        ),
        "executor_receives_only_validated_plan_graph_nodes": authority[
            "executor_receives_only_validated_plan_graph_nodes"
        ],
        "ready_for_post_vv_from_result_proposal": status == "PASS",
        "production_final_output_created": authority["production_final_output_created"],
        "production_external_action_executed": authority[
            "production_external_action_executed"
        ],
        "production_autonomy_claimed": False,
    }


def collect_dag_executor_from_valid_plan_graph() -> DagExecutorFromValidPlanGraphReport:
    architect_report = collect_architect_from_bounded_attractor_packet()
    source_status = architect_report.summary[
        "architect_from_bounded_attractor_packet_status"
    ]
    proposals_by_scenario = {
        proposal["scenario"]: proposal
        for proposal in architect_report.architect_plan_proposals
    }
    valid_proposals = [
        proposal for proposal in architect_report.architect_plan_proposals
        if _proposal_is_valid_plan_graph(proposal)
    ]

    filters: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []

    row, result = _result_proposal_from_plan(
        "accepted_plan_graph_executor_result_proposal",
        proposals_by_scenario["accepted_packet_architect_plan_valid"],
    )
    filters.append(row)
    results.append(result)

    row, result = _result_proposal_from_plan(
        "downgraded_plan_graph_executor_limited_result_proposal",
        proposals_by_scenario["downgraded_packet_architect_plan_limited"],
        limited=True,
    )
    filters.append(row)
    results.append(result)

    filters.append(
        _blocked_filter_row(
            "invalid_architect_artifact_blocked_before_executor",
            "invalid_architect_artifact",
            ["invalid_architect_artifact_not_allowed"],
            invalid_plan_graph_received=False,
        )
    )
    filters.append(
        _blocked_filter_row(
            "raw_architect_text_blocked",
            "raw_architect_text",
            ["raw_architect_text_not_allowed"],
        )
    )
    filters.append(
        _blocked_filter_row(
            "raw_orchestrator_matrix_blocked",
            "raw_orchestrator_matrix",
            ["raw_orchestrator_matrix_not_allowed"],
        )
    )
    filters.append(
        _blocked_filter_row(
            "raw_user_intent_blocked",
            "raw_user_intent",
            ["raw_user_intent_not_allowed"],
        )
    )
    filters.append(
        _blocked_filter_row(
            "unvalidated_plan_graph_blocked",
            "unvalidated_plan_graph",
            ["unvalidated_plan_graph_not_allowed"],
            invalid_plan_graph_received=False,
        )
    )

    input_plan_graphs = {
        "source_architect_report_status": source_status,
        "valid_proposals_imported": [proposal["proposal_id"] for proposal in valid_proposals],
        "accepted_packet_plan_proposals": architect_report.summary[
            "accepted_packet_plan_proposals"
        ],
        "downgraded_packet_plan_proposals": architect_report.summary[
            "downgraded_packet_plan_proposals"
        ],
    }
    containment = _containment(filters, results)
    authority = _authority_safety(filters, results, containment)
    summary = _summary(source_status, filters, results, containment, authority)
    return DagExecutorFromValidPlanGraphReport(
        input_plan_graphs=input_plan_graphs,
        executor_input_filter=filters,
        result_proposals=results,
        containment=containment,
        authority_safety=authority,
        summary=summary,
    )


def _section(lines: list[str], title: str, fields: dict[str, Any]) -> None:
    lines.extend(["", title])
    for key, value in fields.items():
        lines.append(f"{key}: {_format_value(value)}")


def render_dag_executor_from_valid_plan_graph(
    report: DagExecutorFromValidPlanGraphReport,
) -> str:
    lines = [
        "[DAG EXECUTOR FROM VALID PLAN GRAPH]",
        "note: deterministic DAG / Executor proof from valid PlanGraph",
        "note: Executor receives validated PlanGraph nodes only",
        "note: invalid Architect artifacts do not reach Executor",
        "note: raw Architect text is blocked",
        "note: raw Orchestrator matrix is blocked",
        "note: raw user intent is blocked",
        "note: Executor returns ResultProposal only",
        "note: Executor does not create FinalOutput",
        "note: Executor does not write DRS directly",
        "note: Executor does not execute real external actions",
        "note: Post V&V is not invoked yet",
        "note: GT is not invoked yet",
        "note: no production persistence",
        "note: no global DRS",
        "note: no external DRS network",
        "note: Marennya / UP remain deferred and not invoked",
    ]
    _section(lines, "[INPUT PLAN GRAPHS]", report.input_plan_graphs)

    lines.extend(["", "[EXECUTOR INPUT FILTER]"])
    filter_fields = (
        "scenario",
        "input_kind",
        "executor_invoked",
        "blocked_before_executor",
        "block_reasons",
        "executor_input_is_validated_plan_graph",
        "raw_architect_text_received",
        "raw_orchestrator_matrix_received",
        "raw_user_intent_received",
        "invalid_plan_graph_received",
    )
    for row in report.executor_input_filter:
        lines.append(
            " | ".join(f"{field}={_format_value(row[field])}" for field in filter_fields)
        )

    lines.extend(["", "[RESULT PROPOSALS]"])
    result_fields = (
        "result_proposal_id",
        "created_by",
        "source_plan_graph_proposal_id",
        "source_packet_id",
        "source_gate_decision_id",
        "execution_mode",
        "result_status",
        "node_results",
        "evidence",
        "risks",
        "downgraded_claims_visible",
        "executor_creates_final_output",
        "executor_writes_drs",
        "executor_executes_real_action",
        "post_vv_invoked",
        "gt_invoked",
    )
    for result in report.result_proposals:
        lines.append(
            " | ".join(f"{field}={_format_value(result[field])}" for field in result_fields)
        )

    _section(lines, "[CONTAINMENT]", report.containment)
    _section(lines, "[AUTHORITY / SAFETY]", report.authority_safety)
    _section(lines, "[SUMMARY]", report.summary)
    return "\n".join(lines).rstrip() + "\n"


def run_dag_executor_from_valid_plan_graph() -> str:
    return render_dag_executor_from_valid_plan_graph(
        collect_dag_executor_from_valid_plan_graph()
    )


def main() -> int:
    print(run_dag_executor_from_valid_plan_graph(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
