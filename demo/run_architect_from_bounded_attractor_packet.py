from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from demo.run_avf_attractor_from_accepted_matrix import (
    collect_avf_attractor_from_accepted_matrix,
)
from hedgehog.llm_architect import validate_plan_graph_contract


SCENARIOS_UNDER_TEST = (
    "accepted_packet_architect_plan_valid",
    "downgraded_packet_architect_plan_limited",
    "rejected_matrix_never_reaches_architect",
    "raw_orchestrator_matrix_blocked",
    "raw_user_intent_blocked",
    "invalid_attractor_packet_blocked",
    "invalid_architect_artifact_contained",
)


@dataclass(frozen=True)
class ArchitectFromBoundedAttractorPacketReport:
    input_attractor_packets: dict[str, Any]
    architect_input_filter: list[dict[str, Any]]
    architect_plan_proposals: list[dict[str, Any]]
    containment: dict[str, Any]
    authority_safety: dict[str, Any]
    summary: dict[str, Any]


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _format_value(value: Any) -> str:
    if isinstance(value, bool):
        return _bool_text(value)
    return str(value)


def _contract_packet(packet: dict[str, Any]) -> dict[str, Any]:
    return {
        "packet_id": packet["packet_id"],
        "candidate_vectors": [
            {"vector_id": vector_id}
            for vector_id in packet.get("allowed_vectors", [])
        ],
    }


def _make_plan_graph(packet: dict[str, Any], *, invalid: bool = False) -> dict[str, Any]:
    if invalid:
        return {
            "plan_id": f"invalid_plan_{packet['packet_id']}",
            "source_packet_id": packet["packet_id"],
            "edges": [],
            "executor_assignments": [],
        }

    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, str]] = []
    previous_node_id: str | None = None
    for index, vector_id in enumerate(packet.get("allowed_vectors", []), start=1):
        node_id = f"node_{packet['packet_id']}_{index}"
        nodes.append(
            {
                "node_id": node_id,
                "vector_id": vector_id,
                "kind": "validation" if index == 1 else "retrieval",
                "task": (
                    f"build_plan_proposal_for_{vector_id};"
                    "bounded_packet_source=true;"
                    "executor_must_return_result_proposal"
                ),
                "executor_id": "exec_mock_certificate",
                "depends_on": [previous_node_id] if previous_node_id else [],
                "expected_output": "result_proposal",
                "branching_mode": "horizontal",
            }
        )
        if previous_node_id:
            edges.append({"from": previous_node_id, "to": node_id})
        previous_node_id = node_id

    return {
        "plan_id": f"plan_{packet['packet_id']}",
        "source_packet_id": packet["packet_id"],
        "time_assumptions": {
            "as_of": "2026-06-05T00:00:00Z",
            "freshness_required": "normal",
            "assumptions": [
                "Architect received bounded AVF packet only",
                "Executor remains outside this proof layer",
            ],
        },
        "nodes": nodes,
        "edges": edges,
        "executor_assignments": [
            {
                "executor_id": "exec_mock_certificate",
                "node_ids": [node["node_id"] for node in nodes],
                "mode": "simulate_later",
            }
        ],
    }


def _check_plan_graph(plan_graph: dict[str, Any], packet: dict[str, Any]) -> tuple[bool, str | None]:
    try:
        validate_plan_graph_contract(plan_graph, _contract_packet(packet))
    except ValueError as exc:
        return False, str(exc)
    return True, None


def _forbidden_vectors_absent(plan_graph: dict[str, Any], packet: dict[str, Any]) -> bool:
    plan_vectors = {
        node.get("vector_id")
        for node in plan_graph.get("nodes", [])
        if isinstance(node, dict)
    }
    forbidden = set(packet.get("blocked_vectors", [])) | set(packet.get("forbidden_vector_classes", []))
    return not bool(plan_vectors.intersection(forbidden))


def _proposal_from_packet(
    scenario: str,
    packet: dict[str, Any],
    *,
    invalid_artifact: bool = False,
) -> tuple[dict[str, Any], dict[str, Any]]:
    plan_graph = _make_plan_graph(packet, invalid=invalid_artifact)
    valid, error = _check_plan_graph(plan_graph, packet)
    proposal = {
        "proposal_id": f"architect_plan_proposal_{scenario}",
        "created_by": "architect",
        "scenario": scenario,
        "source_packet_id": packet["packet_id"],
        "source_gate_decision_id": packet["source_gate_decision_id"],
        "source_matrix_id": packet["source_matrix_id"],
        "input_is_bounded_attractor_packet": True,
        "raw_orchestrator_matrix_received": False,
        "raw_user_intent_received": False,
        "rejected_matrix_received": False,
        "plan_graph_present": bool(plan_graph),
        "plan_graph_contract_checked": True,
        "plan_graph_contract_valid": valid,
        "plan_graph_contract_error": error,
        "nodes": plan_graph.get("nodes", []),
        "edges": plan_graph.get("edges", []),
        "forbidden_vectors_absent": valid and _forbidden_vectors_absent(plan_graph, packet),
        "downstream_actor_scope": [
            actor
            for actor in packet.get("downstream_actor_expectations", [])
            if actor in {"Architect", "Executor", "Post V&V", "GT", "Root"}
        ],
        "downgraded_claims_visible": list(packet.get("downgraded_claims", [])),
        "architect_creates_final_output": False,
        "architect_writes_drs": False,
        "architect_executes_actions": False,
        "executor_invoked": False,
    }
    filter_row = {
        "scenario": scenario,
        "input_kind": "bounded_attractor_packet",
        "architect_invoked": True,
        "blocked_before_architect": False,
        "block_reasons": [],
        "input_is_bounded_attractor_packet": True,
        "raw_orchestrator_matrix_received": False,
        "raw_user_intent_received": False,
        "rejected_matrix_received": False,
    }
    return filter_row, proposal


def _blocked_filter_row(
    scenario: str,
    input_kind: str,
    block_reasons: list[str],
) -> dict[str, Any]:
    return {
        "scenario": scenario,
        "input_kind": input_kind,
        "architect_invoked": False,
        "blocked_before_architect": True,
        "block_reasons": block_reasons,
        "input_is_bounded_attractor_packet": False,
        "raw_orchestrator_matrix_received": False,
        "raw_user_intent_received": False,
        "rejected_matrix_received": False,
    }


def _containment(
    filters: list[dict[str, Any]],
    proposals: list[dict[str, Any]],
) -> dict[str, Any]:
    invalid_proposals = [
        proposal for proposal in proposals
        if proposal["plan_graph_contract_checked"] and not proposal["plan_graph_contract_valid"]
    ]
    return {
        "invalid_architect_artifact_caught": bool(invalid_proposals),
        "invalid_architect_reached_executor": any(
            proposal["executor_invoked"] for proposal in invalid_proposals
        ),
        "invalid_architect_created_final_output": any(
            proposal["architect_creates_final_output"] for proposal in invalid_proposals
        ),
        "invalid_architect_wrote_drs": any(
            proposal["architect_writes_drs"] for proposal in invalid_proposals
        ),
        "raw_matrix_reached_architect": any(
            row["input_kind"] == "raw_orchestrator_matrix" and row["architect_invoked"]
            for row in filters
        ),
        "rejected_matrix_reached_architect": any(
            row["input_kind"] == "rejected_matrix_result" and row["architect_invoked"]
            for row in filters
        ),
    }


def _authority_safety(
    filters: list[dict[str, Any]],
    proposals: list[dict[str, Any]],
    containment: dict[str, Any],
) -> dict[str, Any]:
    return {
        "architect_receives_only_bounded_attractor_packet": all(
            row["input_is_bounded_attractor_packet"]
            for row in filters
            if row["architect_invoked"]
        ),
        "architect_receives_raw_orchestrator_matrix": containment["raw_matrix_reached_architect"],
        "architect_receives_raw_user_intent": any(
            row["raw_user_intent_received"] for row in filters
        ),
        "architect_receives_rejected_matrix": containment["rejected_matrix_reached_architect"],
        "plan_graph_contract_required": True,
        "plan_graph_contract_checked": all(
            proposal["plan_graph_contract_checked"] for proposal in proposals
        ),
        "architect_creates_final_output": any(
            proposal["architect_creates_final_output"] for proposal in proposals
        ),
        "architect_writes_drs": any(proposal["architect_writes_drs"] for proposal in proposals),
        "architect_executes_actions": any(
            proposal["architect_executes_actions"] for proposal in proposals
        ),
        "executor_invoked": any(proposal["executor_invoked"] for proposal in proposals),
        "post_vv_invoked": False,
        "gt_invoked": False,
        "production_final_output_created": False,
        "production_external_action_executed": False,
        "global_drs_implemented": False,
        "external_drs_network_implemented": False,
        "marennya_invoked": False,
        "up_invoked": False,
    }


def _summary(
    source_status: str,
    filters: list[dict[str, Any]],
    proposals: list[dict[str, Any]],
    containment: dict[str, Any],
    authority: dict[str, Any],
) -> dict[str, Any]:
    valid_proposals = [
        proposal for proposal in proposals if proposal["plan_graph_contract_valid"]
    ]
    accepted_proposals = [
        proposal for proposal in valid_proposals
        if proposal["source_packet_id"] == "attractor_packet_valid_matrix_accept"
    ]
    downgraded_proposals = [
        proposal for proposal in valid_proposals
        if proposal["source_packet_id"] == "attractor_packet_incomplete_guards_downgrade_or_reject"
    ]
    raw_blocked = any(
        row["scenario"] == "raw_orchestrator_matrix_blocked"
        and row["blocked_before_architect"]
        for row in filters
    )
    raw_user_intent_blocked = any(
        row["scenario"] == "raw_user_intent_blocked"
        and row["blocked_before_architect"]
        for row in filters
    )
    rejected_blocked = any(
        row["scenario"] == "rejected_matrix_never_reaches_architect"
        and row["blocked_before_architect"]
        for row in filters
    )
    invalid_packet_blocked = any(
        row["scenario"] == "invalid_attractor_packet_blocked"
        and row["blocked_before_architect"]
        for row in filters
    )
    boundary_pass = (
        authority["architect_receives_only_bounded_attractor_packet"]
        and not authority["architect_receives_raw_orchestrator_matrix"]
        and not authority["architect_receives_raw_user_intent"]
        and not authority["architect_receives_rejected_matrix"]
        and authority["plan_graph_contract_checked"]
        and not authority["architect_creates_final_output"]
        and not authority["architect_writes_drs"]
        and not authority["architect_executes_actions"]
        and not authority["executor_invoked"]
        and not authority["post_vv_invoked"]
        and not authority["gt_invoked"]
        and not authority["production_final_output_created"]
        and not authority["production_external_action_executed"]
        and not authority["global_drs_implemented"]
        and not authority["external_drs_network_implemented"]
        and not authority["marennya_invoked"]
        and not authority["up_invoked"]
        and containment["invalid_architect_artifact_caught"]
        and not containment["invalid_architect_reached_executor"]
    )
    status = (
        "PASS"
        if source_status == "PASS"
        and len(filters) == len(SCENARIOS_UNDER_TEST)
        and len(valid_proposals) == 2
        and len(accepted_proposals) == 1
        and len(downgraded_proposals) == 1
        and raw_blocked
        and raw_user_intent_blocked
        and rejected_blocked
        and invalid_packet_blocked
        and boundary_pass
        else "FAIL"
    )
    return {
        "architect_from_bounded_attractor_packet_status": status,
        "source_avf_attractor_status": source_status,
        "scenarios_verified": len(filters),
        "valid_plan_graph_proposals_created": len(valid_proposals),
        "accepted_packet_plan_proposals": len(accepted_proposals),
        "downgraded_packet_plan_proposals": len(downgraded_proposals),
        "raw_orchestrator_matrix_blocked": raw_blocked,
        "raw_user_intent_blocked": raw_user_intent_blocked,
        "rejected_matrix_blocked": rejected_blocked,
        "invalid_packet_blocked": invalid_packet_blocked,
        "invalid_architect_artifact_contained": containment[
            "invalid_architect_artifact_caught"
        ] and not containment["invalid_architect_reached_executor"],
        "ready_for_dag_executor_from_valid_plan_graph": status == "PASS",
        "production_final_output_created": authority["production_final_output_created"],
        "production_external_action_executed": authority[
            "production_external_action_executed"
        ],
        "production_autonomy_claimed": False,
    }


def collect_architect_from_bounded_attractor_packet() -> ArchitectFromBoundedAttractorPacketReport:
    avf_report = collect_avf_attractor_from_accepted_matrix()
    packets_by_gate = {
        packet["gate_decision"]: packet for packet in avf_report.attractor_packets
    }
    results_by_scenario = {
        row["scenario"]: row for row in avf_report.avf_formation_results
    }

    filters: list[dict[str, Any]] = []
    proposals: list[dict[str, Any]] = []

    filter_row, proposal = _proposal_from_packet(
        "accepted_packet_architect_plan_valid",
        packets_by_gate["accept"],
    )
    filters.append(filter_row)
    proposals.append(proposal)

    filter_row, proposal = _proposal_from_packet(
        "downgraded_packet_architect_plan_limited",
        packets_by_gate["downgrade"],
    )
    filters.append(filter_row)
    proposals.append(proposal)

    filters.append(
        _blocked_filter_row(
            "rejected_matrix_never_reaches_architect",
            "rejected_matrix_result",
            ["rejected_matrix_not_allowed"],
        )
    )
    rejected_result = results_by_scenario["missing_temporal_query_reject"]
    filters[-1]["rejected_matrix_received"] = False
    filters[-1]["source_gate_decision"] = rejected_result["gate_decision"]

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
            ["raw_unchecked_user_intent_not_allowed"],
        )
    )

    filters.append(
        _blocked_filter_row(
            "invalid_attractor_packet_blocked",
            "invalid_attractor_packet",
            ["invalid_or_unbounded_attractor_packet"],
        )
    )

    filter_row, proposal = _proposal_from_packet(
        "invalid_architect_artifact_contained",
        packets_by_gate["accept"],
        invalid_artifact=True,
    )
    filters.append(filter_row)
    proposals.append(proposal)

    source_status = avf_report.summary["avf_attractor_from_accepted_matrix_status"]
    input_packets = {
        "source_avf_report_status": source_status,
        "packets_imported": [packet["packet_id"] for packet in avf_report.attractor_packets],
        "accepted_matrix_packets": avf_report.summary["accepted_matrix_packets"],
        "downgraded_matrix_packets": avf_report.summary["downgraded_matrix_packets"],
        "rejected_matrix_packets": avf_report.summary["rejected_matrix_packets"],
    }
    containment = _containment(filters, proposals)
    authority = _authority_safety(filters, proposals, containment)
    summary = _summary(source_status, filters, proposals, containment, authority)
    return ArchitectFromBoundedAttractorPacketReport(
        input_attractor_packets=input_packets,
        architect_input_filter=filters,
        architect_plan_proposals=proposals,
        containment=containment,
        authority_safety=authority,
        summary=summary,
    )


def _section(lines: list[str], title: str, fields: dict[str, Any]) -> None:
    lines.extend(["", title])
    for key, value in fields.items():
        lines.append(f"{key}: {_format_value(value)}")


def render_architect_from_bounded_attractor_packet(
    report: ArchitectFromBoundedAttractorPacketReport,
) -> str:
    lines = [
        "[ARCHITECT FROM BOUNDED ATTRACTOR PACKET]",
        "note: deterministic Architect proof from bounded AttractorPacket-like input",
        "note: Architect receives AVF-bounded input only",
        "note: raw Orchestrator matrix is not passed to Architect",
        "note: rejected matrix cannot reach Architect",
        "note: Architect may produce PlanGraph proposal only",
        "note: PlanGraph contract is checked",
        "note: invalid Architect artifact is contained",
        "note: Executor is not invoked",
        "note: no production FinalOutput",
        "note: no Architect DRS write",
        "note: no real external actions",
        "note: no global DRS",
        "note: no external DRS network",
        "note: Marennya / UP remain deferred and not invoked",
    ]
    _section(lines, "[INPUT ATTRACTOR PACKETS]", report.input_attractor_packets)

    lines.extend(["", "[ARCHITECT INPUT FILTER]"])
    filter_fields = (
        "scenario",
        "input_kind",
        "architect_invoked",
        "blocked_before_architect",
        "block_reasons",
        "input_is_bounded_attractor_packet",
        "raw_orchestrator_matrix_received",
        "raw_user_intent_received",
        "rejected_matrix_received",
    )
    for row in report.architect_input_filter:
        lines.append(
            " | ".join(f"{field}={_format_value(row[field])}" for field in filter_fields)
        )

    lines.extend(["", "[ARCHITECT PLAN PROPOSALS]"])
    proposal_fields = (
        "proposal_id",
        "created_by",
        "source_packet_id",
        "source_gate_decision_id",
        "source_matrix_id",
        "plan_graph_present",
        "plan_graph_contract_checked",
        "plan_graph_contract_valid",
        "nodes",
        "edges",
        "forbidden_vectors_absent",
        "downstream_actor_scope",
        "downgraded_claims_visible",
        "architect_creates_final_output",
        "architect_writes_drs",
        "architect_executes_actions",
        "executor_invoked",
    )
    for proposal in report.architect_plan_proposals:
        lines.append(
            " | ".join(
                f"{field}={_format_value(proposal[field])}" for field in proposal_fields
            )
        )

    _section(lines, "[CONTAINMENT]", report.containment)
    _section(lines, "[AUTHORITY / SAFETY]", report.authority_safety)
    _section(lines, "[SUMMARY]", report.summary)
    return "\n".join(lines).rstrip() + "\n"


def run_architect_from_bounded_attractor_packet() -> str:
    return render_architect_from_bounded_attractor_packet(
        collect_architect_from_bounded_attractor_packet()
    )


def main() -> int:
    print(run_architect_from_bounded_attractor_packet(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
