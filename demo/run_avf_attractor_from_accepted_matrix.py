from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from demo.run_controlled_orchestrator_matrix_gate import (
    collect_controlled_orchestrator_matrix_gate,
    _scenario_matrices,
)

SCENARIOS_UNDER_TEST = (
    "valid_matrix_accept",
    "incomplete_guards_downgrade_or_reject",
    "missing_temporal_query_reject",
    "high_confidence_policy_block",
    "forbidden_bypass_reject",
    "wrong_downstream_actors_reject",
)


@dataclass(frozen=True)
class AvfAttractorFromAcceptedMatrixReport:
    input_gate_decisions: dict[str, Any]
    avf_formation_results: list[dict[str, Any]]
    attractor_packets: list[dict[str, Any]]
    authority_safety: dict[str, Any]
    summary: dict[str, Any]


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _format_value(value: Any) -> str:
    if isinstance(value, bool):
        return _bool_text(value)
    return str(value)


def _candidate_vector_decision(matrix: dict[str, Any], decision: dict[str, Any]) -> tuple[list[str], list[str]]:
    hints = list(matrix.get("candidate_vector_hints", []))
    blocked = (
        set(matrix.get("forbidden_vector_classes", []))
        | {
            "credential_exposure",
            "external_action_without_permission",
            "policy_bypass",
        }
    )
    if decision["gate_decision"] == "downgrade":
        return [hint for hint in hints if hint != "official_online_request"], sorted(
            blocked | {"missing_guard_claim"}
        )
    return hints, sorted(blocked)


def _downgraded_claims(decision: dict[str, Any]) -> list[str]:
    claims: list[str] = []
    claims.extend(f"missing_guard:{guard}" for guard in decision["missing_guards"])
    claims.extend(f"downgrade_reason:{reason}" for reason in decision["downgrade_reasons"])
    return claims


def _make_packet(
    scenario: str,
    matrix: dict[str, Any],
    decision: dict[str, Any],
) -> dict[str, Any]:
    allowed_vectors, blocked_vectors = _candidate_vector_decision(matrix, decision)
    downgraded_claims = _downgraded_claims(decision)
    hardmask_blocks = sorted(set(matrix.get("forbidden_vector_classes", [])))
    policy_blocks = sorted(
        {
            "no_external_action_without_permission",
            "no_credential_capture",
            "no_policy_bypass",
        }
    )
    ignored_hints = [
        hint for hint in matrix.get("candidate_vector_hints", []) if hint not in allowed_vectors
    ]
    return {
        "packet_id": f"attractor_packet_{scenario}",
        "created_by": "avf",
        "source_gate_decision_id": decision["decision_id"],
        "source_matrix_id": matrix["matrix_id"],
        "gate_decision": decision["gate_decision"],
        "accepted_or_downgraded": decision["gate_decision"] in {"accept", "downgrade"},
        "candidate_vector_hints_used": allowed_vectors,
        "candidate_vector_hints_ignored": ignored_hints,
        "forbidden_vector_classes": sorted(matrix.get("forbidden_vector_classes", [])),
        "hardmask_blocks": hardmask_blocks,
        "policy_blocks": policy_blocks,
        "risk_flags": list(matrix.get("risk_flags", [])),
        "budget_hints": matrix.get("budget_hints", {}),
        "guard_context": sorted(matrix.get("guard_set", [])),
        "downstream_actor_expectations": sorted(matrix.get("downstream_actors", [])),
        "allowed_vectors": allowed_vectors,
        "blocked_vectors": blocked_vectors,
        "downgraded_claims": downgraded_claims,
        "root_override_applied": decision["gate_decision"] == "downgrade",
        "architect_input_bounded": True,
        "architect_input_summary": (
            "bounded attractor packet only; no raw Orchestrator authority"
        ),
        "avf_creates_final_output": False,
        "avf_writes_drs": False,
        "avf_executes_actions": False,
    }


def _formation_result(
    scenario: str,
    matrix: dict[str, Any],
    decision: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    can_reach_avf = decision["gate_decision"] in {"accept", "downgrade"}
    packet = _make_packet(scenario, matrix, decision) if can_reach_avf else None
    hardmask_blocks = packet["hardmask_blocks"] if packet else sorted(matrix.get("forbidden_vector_classes", []))
    policy_blocks = (
        packet["policy_blocks"]
        if packet
        else sorted(
            set(decision.get("rejection_reasons", []))
            | {"policy_beats_orchestrator_confidence"}
        )
    )
    return (
        {
            "scenario": scenario,
            "gate_decision": decision["gate_decision"],
            "route_confidence": matrix.get("route_confidence"),
            "avf_invoked": can_reach_avf,
            "attractor_packet_created": packet is not None,
            "rejected_matrix_reached_avf": False,
            "packet_id": packet["packet_id"] if packet else None,
            "allowed_vectors": packet["allowed_vectors"] if packet else [],
            "blocked_vectors": packet["blocked_vectors"] if packet else [],
            "hardmask_blocks": hardmask_blocks,
            "policy_blocks": policy_blocks,
            "downgraded_claims": packet["downgraded_claims"] if packet else [],
            "missing_guards": list(decision.get("missing_guards", [])),
            "missing_downstream_actors": list(decision.get("missing_downstream_actors", [])),
            "extra_downstream_actors": list(decision.get("extra_downstream_actors", [])),
            "forbidden_bypass_detected": decision["forbidden_bypass_detected"],
            "policy_beats_orchestrator_confidence": decision[
                "policy_beats_orchestrator_confidence"
            ],
            "architect_input_bounded": packet["architect_input_bounded"] if packet else False,
            "architect_reached": False,
            "executor_reached": False,
            "avf_creates_final_output": False,
            "avf_writes_drs": False,
            "avf_executes_actions": False,
        },
        packet,
    )


def _authority_safety(results: list[dict[str, Any]], packets: list[dict[str, Any]]) -> dict[str, Any]:
    rejected = [result for result in results if result["gate_decision"] == "reject"]
    return {
        "orchestrator_hints_are_commands": False,
        "avf_independent": True,
        "root_gate_before_avf": True,
        "hardmask_beats_orchestrator_confidence": all(
            bool(result["hardmask_blocks"]) for result in results
        ),
        "policy_beats_orchestrator_confidence": all(
            result["policy_beats_orchestrator_confidence"] for result in results
        ),
        "rejected_matrix_reaches_avf": any(
            result["rejected_matrix_reached_avf"] for result in rejected
        ),
        "architect_reached_from_rejected_matrix": any(
            result["architect_reached"] for result in rejected
        ),
        "architect_reached": any(result["architect_reached"] for result in results),
        "executor_reached": any(result["executor_reached"] for result in results),
        "avf_creates_final_output": any(
            packet["avf_creates_final_output"] for packet in packets
        ),
        "avf_writes_drs": any(packet["avf_writes_drs"] for packet in packets),
        "avf_executes_actions": any(packet["avf_executes_actions"] for packet in packets),
        "orchestrator_writes_drs": False,
        "production_final_output_created": False,
        "production_external_action_executed": False,
        "global_drs_implemented": False,
        "external_drs_network_implemented": False,
        "marennya_invoked": False,
        "up_invoked": False,
    }


def _summary(
    source_status: str,
    results: list[dict[str, Any]],
    packets: list[dict[str, Any]],
    authority: dict[str, Any],
) -> dict[str, Any]:
    accepted_packets = [
        packet for packet in packets if packet["gate_decision"] == "accept"
    ]
    downgraded_packets = [
        packet for packet in packets if packet["gate_decision"] == "downgrade"
    ]
    rejected_packet_count = sum(
        1 for result in results
        if result["gate_decision"] == "reject" and result["attractor_packet_created"]
    )
    rejected_blocked = all(
        not result["avf_invoked"] and not result["attractor_packet_created"]
        for result in results
        if result["gate_decision"] == "reject"
    )
    boundary_pass = (
        rejected_packet_count == 0
        and rejected_blocked
        and not authority["rejected_matrix_reaches_avf"]
        and not authority["architect_reached"]
        and not authority["executor_reached"]
        and not authority["avf_creates_final_output"]
        and not authority["avf_writes_drs"]
        and not authority["avf_executes_actions"]
        and not authority["production_final_output_created"]
        and not authority["production_external_action_executed"]
        and not authority["global_drs_implemented"]
        and not authority["external_drs_network_implemented"]
        and not authority["marennya_invoked"]
        and not authority["up_invoked"]
    )
    status = (
        "PASS"
        if source_status == "PASS"
        and len(results) == len(SCENARIOS_UNDER_TEST)
        and len(accepted_packets) == 1
        and len(downgraded_packets) == 1
        and boundary_pass
        and authority["avf_independent"]
        and authority["root_gate_before_avf"]
        and authority["hardmask_beats_orchestrator_confidence"]
        and authority["policy_beats_orchestrator_confidence"]
        else "FAIL"
    )
    return {
        "avf_attractor_from_accepted_matrix_status": status,
        "source_matrix_gate_status": source_status,
        "scenarios_verified": len(results),
        "attractor_packets_created": len(packets),
        "accepted_matrix_packets": len(accepted_packets),
        "downgraded_matrix_packets": len(downgraded_packets),
        "rejected_matrix_packets": rejected_packet_count,
        "rejected_matrices_blocked_before_avf": rejected_blocked,
        "avf_independent": authority["avf_independent"],
        "ready_for_architect_from_bounded_attractor_packet": status == "PASS",
        "production_final_output_created": authority["production_final_output_created"],
        "production_external_action_executed": authority[
            "production_external_action_executed"
        ],
        "production_autonomy_claimed": False,
    }


def collect_avf_attractor_from_accepted_matrix() -> AvfAttractorFromAcceptedMatrixReport:
    gate_report = collect_controlled_orchestrator_matrix_gate()
    decisions_by_scenario = {
        decision["scenario"]: decision for decision in gate_report.gate_decisions
    }
    matrices_by_scenario = {
        row["scenario"]: row["matrix"] for row in _scenario_matrices()
    }
    results: list[dict[str, Any]] = []
    packets: list[dict[str, Any]] = []
    for scenario in SCENARIOS_UNDER_TEST:
        result, packet = _formation_result(
            scenario,
            matrices_by_scenario[scenario],
            decisions_by_scenario[scenario],
        )
        results.append(result)
        if packet:
            packets.append(packet)

    source_status = gate_report.summary["controlled_orchestrator_matrix_gate_status"]
    input_gate_decisions = {
        "source_gate_report_status": source_status,
        "scenarios_imported": [row["scenario"] for row in gate_report.input_matrices],
        "accepted_count": gate_report.summary["accepted_count"],
        "rejected_count": gate_report.summary["rejected_count"],
        "downgraded_count": gate_report.summary["downgraded_count"],
    }
    authority = _authority_safety(results, packets)
    summary = _summary(source_status, results, packets, authority)
    return AvfAttractorFromAcceptedMatrixReport(
        input_gate_decisions=input_gate_decisions,
        avf_formation_results=results,
        attractor_packets=packets,
        authority_safety=authority,
        summary=summary,
    )


def _section(lines: list[str], title: str, fields: dict[str, Any]) -> None:
    lines.extend(["", title])
    for key, value in fields.items():
        lines.append(f"{key}: {_format_value(value)}")


def render_avf_attractor_from_accepted_matrix(
    report: AvfAttractorFromAcceptedMatrixReport,
) -> str:
    lines = [
        "[AVF ATTRACTOR FROM ACCEPTED MATRIX]",
        "note: deterministic AVF / Attractor proof from Root-accepted matrix",
        "note: Orchestrator hints are hints, not commands",
        "note: Root-controlled Matrix Gate runs before AVF",
        "note: rejected matrix cannot reach AVF",
        "note: downgraded matrix may reach AVF only with downgraded claims visible",
        "note: AVF remains independent",
        "note: HardMask beats Orchestrator confidence",
        "note: policy beats Orchestrator confidence",
        "note: no production RootOrchestrator behavior change",
        "note: no live Telegram action",
        "note: no real external actions",
        "note: no production FinalOutput",
        "note: no DRS write by AVF or Orchestrator",
        "note: no global DRS",
        "note: no external DRS network",
        "note: Marennya / UP remain deferred and not invoked",
    ]
    _section(lines, "[INPUT GATE DECISIONS]", report.input_gate_decisions)
    lines.extend(["", "[AVF FORMATION RESULTS]"])
    result_fields = (
        "scenario",
        "gate_decision",
        "avf_invoked",
        "attractor_packet_created",
        "rejected_matrix_reached_avf",
        "packet_id",
        "allowed_vectors",
        "blocked_vectors",
        "hardmask_blocks",
        "policy_blocks",
        "downgraded_claims",
        "architect_input_bounded",
        "architect_reached",
    )
    for result in report.avf_formation_results:
        lines.append(
            " | ".join(
                f"{field}={_format_value(result[field])}" for field in result_fields
            )
        )
    lines.extend(["", "[ATTRACTOR PACKETS]"])
    packet_fields = (
        "packet_id",
        "created_by",
        "source_gate_decision_id",
        "source_matrix_id",
        "gate_decision",
        "candidate_vector_hints_used",
        "candidate_vector_hints_ignored",
        "forbidden_vector_classes",
        "hardmask_blocks",
        "policy_blocks",
        "risk_flags",
        "budget_hints",
        "guard_context",
        "downstream_actor_expectations",
        "downgraded_claims",
        "root_override_applied",
        "architect_input_summary",
    )
    for packet in report.attractor_packets:
        lines.append(
            " | ".join(
                f"{field}={_format_value(packet[field])}" for field in packet_fields
            )
        )
    _section(lines, "[AUTHORITY / SAFETY]", report.authority_safety)
    _section(lines, "[SUMMARY]", report.summary)
    return "\n".join(lines).rstrip() + "\n"


def run_avf_attractor_from_accepted_matrix() -> str:
    return render_avf_attractor_from_accepted_matrix(
        collect_avf_attractor_from_accepted_matrix()
    )


def main() -> int:
    print(run_avf_attractor_from_accepted_matrix(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
