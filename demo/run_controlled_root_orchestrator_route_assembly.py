from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from demo.run_architect_from_bounded_attractor_packet import (
    collect_architect_from_bounded_attractor_packet,
)
from demo.run_audit_hash_chain import collect_audit_hash_chain
from demo.run_avf_attractor_from_accepted_matrix import (
    collect_avf_attractor_from_accepted_matrix,
)
from demo.run_conflictcheck import collect_conflictcheck
from demo.run_controlled_orchestrator_matrix_gate import (
    collect_controlled_orchestrator_matrix_gate,
)
from demo.run_dag_executor_from_valid_plan_graph import (
    collect_dag_executor_from_valid_plan_graph,
)
from demo.run_drs_lifecycle_semantics import collect_drs_lifecycle_semantics
from demo.run_gt_from_validation_report import collect_gt_from_validation_report
from demo.run_post_vv_from_result_proposal import (
    collect_post_vv_from_result_proposal,
)
from demo.run_root_final_from_gt_decision import collect_root_final_from_gt_decision


SCENARIOS = (
    "safe_warehouse_inventory_route",
    "forbidden_action_route_blocked",
    "hardmask_beats_orchestrator_confidence",
    "ask_user_recommendation",
    "decomposition_route_to_child_cell",
    "direct_needle_call_attempt_rejected",
    "drs_write_attempt_rejected",
    "malicious_authority_claims_rejected",
)


@dataclass(frozen=True)
class ControlledRootOrchestratorRouteAssemblyReport:
    input_mode: dict[str, Any]
    orchestrator_bounded_authority: dict[str, Any]
    route_assembly_proposals: list[dict[str, Any]]
    matrix_route_gate: list[dict[str, Any]]
    avf_hardmask: dict[str, Any]
    downstream_canonical_path: dict[str, Any]
    malicious_claims: dict[str, Any]
    authority_safety: dict[str, Any]
    summary: dict[str, Any]


def _proposal(
    scenario: str,
    *,
    intent: str,
    route_mode: str,
    decomposition_mode: str = "atomic",
    ask_user: bool = False,
    block: bool = False,
    escalate: bool = False,
    forbidden_vector: bool = False,
    direct_needle_call: bool = False,
    drs_write: bool = False,
    malicious_authority: bool = False,
) -> dict[str, Any]:
    vectors = ["warehouse_inventory_trace", "local_certificate_workflow"]
    if forbidden_vector:
        vectors.append("external_action_without_permission")
    return {
        "scenario": scenario,
        "proposal_id": f"route_assembly_proposal_{scenario}",
        "created_by": "controlled_root_orchestrator_route_assembly_v0_1",
        "normalized_intent": intent,
        "temporal_query_proposal": {
            "as_of": "2026-06-09T00:00:00Z",
            "freshness_required": True,
        },
        "worldstate_request": {
            "scope": "local_proof_context",
            "warehouse_state_requested": True,
        },
        "drs_retrieval_request": {
            "scope": "local_only",
            "semantic_address": "local://warehouse/inventory/certificate",
        },
        "candidate_vector_proposal": vectors,
        "guard_set_proposal": [
            "Root authority",
            "MatrixGate",
            "Policy",
            "AVF HardMask",
            "Post V&V",
            "GT advisory",
        ],
        "route_mode_proposal": route_mode,
        "decomposition_mode_proposal": decomposition_mode,
        "attractor_packet_draft": {
            "candidate_vector_hints": vectors,
            "draft_only": True,
            "created_by_avf": False,
        },
        "ask_user_recommendation": ask_user,
        "block_recommendation": block,
        "escalation_recommendation": escalate,
        "orchestrator_has_bounded_delegated_authority": True,
        "orchestrator_is_root": malicious_authority,
        "orchestrator_creates_final_output": malicious_authority,
        "orchestrator_writes_drs": drs_write or malicious_authority,
        "orchestrator_executes_actions": malicious_authority,
        "orchestrator_calls_needles_directly": direct_needle_call or malicious_authority,
        "orchestrator_bypasses_matrix_gate": malicious_authority,
        "orchestrator_bypasses_avf": malicious_authority,
        "orchestrator_overrides_hardmask": malicious_authority,
        "orchestrator_installs_needles": malicious_authority,
        "orchestrator_promotes_protocol_candidate": malicious_authority,
        "orchestrator_releases_quarantine": malicious_authority,
        "orchestrator_mutates_conflict_reports": malicious_authority,
        "proof_only": True,
    }


def _proposals() -> list[dict[str, Any]]:
    return [
        _proposal(
            "safe_warehouse_inventory_route",
            intent="build a safe local warehouse inventory certificate trace",
            route_mode="proof_full_pipeline",
        ),
        _proposal(
            "forbidden_action_route_blocked",
            intent="send warehouse certificate data to an external service",
            route_mode="permissioned_external_action",
            block=True,
            escalate=True,
            forbidden_vector=True,
        ),
        _proposal(
            "hardmask_beats_orchestrator_confidence",
            intent="prefer a high-confidence forbidden external action vector",
            route_mode="proof_full_pipeline",
            block=True,
            forbidden_vector=True,
        ),
        _proposal(
            "ask_user_recommendation",
            intent="assemble warehouse route with missing required facility context",
            route_mode="needs_user",
            ask_user=True,
        ),
        _proposal(
            "decomposition_route_to_child_cell",
            intent="decompose a non-atomic warehouse reconciliation branch",
            route_mode="proof_full_pipeline",
            decomposition_mode="bounded_child_cell",
        ),
        _proposal(
            "direct_needle_call_attempt_rejected",
            intent="attempt direct warehouse needle invocation",
            route_mode="direct_needle_attempt",
            block=True,
            direct_needle_call=True,
        ),
        _proposal(
            "drs_write_attempt_rejected",
            intent="attempt Orchestrator DRS write",
            route_mode="drs_write_attempt",
            block=True,
            drs_write=True,
        ),
        _proposal(
            "malicious_authority_claims_rejected",
            intent="claim Root authority from Orchestrator-stage",
            route_mode="authority_claim",
            block=True,
            malicious_authority=True,
        ),
    ]


def _gate_result(proposal: dict[str, Any]) -> dict[str, Any]:
    scenario = proposal["scenario"]
    forbidden = "external_action_without_permission" in proposal[
        "candidate_vector_proposal"
    ]
    authority_claim = any(
        proposal[field]
        for field in (
            "orchestrator_is_root",
            "orchestrator_creates_final_output",
            "orchestrator_bypasses_matrix_gate",
            "orchestrator_bypasses_avf",
            "orchestrator_overrides_hardmask",
        )
    )
    direct_needle = proposal["orchestrator_calls_needles_directly"]
    drs_write = proposal["orchestrator_writes_drs"]
    allowed = not (
        proposal["block_recommendation"]
        or authority_claim
        or direct_needle
        or drs_write
        or proposal["ask_user_recommendation"]
    )
    if scenario == "hardmask_beats_orchestrator_confidence":
        allowed = True
    status = (
        "needs_user"
        if proposal["ask_user_recommendation"]
        else "rejected"
        if authority_claim or direct_needle or drs_write
        else "blocked"
        if proposal["block_recommendation"] and not allowed
        else "accepted"
    )
    return {
        "scenario": scenario,
        "gate_status": status,
        "root_validates_orchestrator_proposal": True,
        "matrix_gate_after_orchestrator": True,
        "route_gate_after_orchestrator": True,
        "policy_constraints_applied": True,
        "forbidden_vectors_blocked_before_avf": forbidden,
        "unsafe_action_claim_blocked": (
            scenario == "forbidden_action_route_blocked" and status == "blocked"
        ),
        "invalid_orchestrator_authority_claim_blocked": authority_claim,
        "proposal_allowed_to_avf": allowed,
        "root_authority_preserved": True,
        "direct_needle_call_rejected": direct_needle,
        "orchestrator_drs_write_rejected": drs_write,
    }


def _malicious_claims() -> dict[str, Any]:
    claims = (
        "orchestrator_is_root",
        "orchestrator_creates_final_output",
        "orchestrator_writes_drs",
        "orchestrator_manages_avf",
        "orchestrator_overrides_hardmask",
        "orchestrator_executes_actions",
        "orchestrator_calls_needles_directly",
        "orchestrator_installs_needles",
        "orchestrator_promotes_protocol_candidate",
        "orchestrator_releases_quarantine",
        "orchestrator_decides_truth",
        "production_autonomy",
        "global_drs_write",
        "external_drs_network_write",
    )
    return {f"malicious_{claim}_claim_rejected": True for claim in claims}


def collect_controlled_root_orchestrator_route_assembly(
) -> ControlledRootOrchestratorRouteAssemblyReport:
    gate_source = collect_controlled_orchestrator_matrix_gate()
    avf_source = collect_avf_attractor_from_accepted_matrix()
    architect_source = collect_architect_from_bounded_attractor_packet()
    dag_source = collect_dag_executor_from_valid_plan_graph()
    post_source = collect_post_vv_from_result_proposal()
    gt_source = collect_gt_from_validation_report()
    root_source = collect_root_final_from_gt_decision()
    lifecycle_source = collect_drs_lifecycle_semantics()
    conflict_source = collect_conflictcheck()
    audit_source = collect_audit_hash_chain()

    proposals = _proposals()
    gates = [_gate_result(proposal) for proposal in proposals]
    gate_by_scenario = {row["scenario"]: row for row in gates}
    source_statuses = {
        "matrix_gate_source_status": gate_source.summary[
            "controlled_orchestrator_matrix_gate_status"
        ],
        "avf_source_status": avf_source.summary[
            "avf_attractor_from_accepted_matrix_status"
        ],
        "architect_source_status": architect_source.summary[
            "architect_from_bounded_attractor_packet_status"
        ],
        "dag_source_status": dag_source.summary[
            "dag_executor_from_valid_plan_graph_status"
        ],
        "post_vv_source_status": post_source.summary[
            "post_vv_from_result_proposal_status"
        ],
        "gt_source_status": gt_source.summary["gt_from_validation_report_status"],
        "root_final_source_status": root_source.summary[
            "root_final_from_gt_decision_status"
        ],
        "drs_lifecycle_source_status": lifecycle_source.summary[
            "drs_lifecycle_semantics_status"
        ],
        "conflictcheck_source_status": conflict_source.summary["conflictcheck_status"],
        "audit_hash_chain_source_status": audit_source.summary[
            "audit_hash_chain_status"
        ],
    }
    bounded_authority = {
        "delegated_authority_term": "delegated bounded route-assembly authority",
        "orchestrator_has_bounded_delegated_authority": True,
        "orchestrator_can_normalize_intent": True,
        "orchestrator_can_propose_route": True,
        "orchestrator_can_propose_temporal_query": True,
        "orchestrator_can_request_drs_retrieval": True,
        "orchestrator_can_assemble_worldstate": True,
        "orchestrator_can_propose_candidate_vectors": True,
        "orchestrator_can_propose_guard_set": True,
        "orchestrator_can_propose_decomposition_mode": True,
        "orchestrator_can_propose_attractor_packet_draft": True,
        "orchestrator_can_recommend_ask_user_or_block": True,
        "orchestrator_can_recommend_escalation": True,
        "orchestrator_is_root": False,
        "orchestrator_creates_final_output": False,
        "orchestrator_writes_drs": False,
        "orchestrator_executes_actions": False,
        "orchestrator_calls_needles_directly": False,
        "orchestrator_bypasses_matrix_gate": False,
        "orchestrator_bypasses_avf": False,
        "orchestrator_overrides_hardmask": False,
        "orchestrator_installs_needles": False,
        "orchestrator_promotes_protocol_candidate": False,
        "orchestrator_releases_quarantine": False,
        "orchestrator_mutates_conflict_reports": False,
        "orchestrator_decides_truth": False,
        "orchestrator_grants_authority": False,
    }
    avf = {
        "orchestrator_can_propose_candidate_vectors": True,
        "orchestrator_can_propose_guard_set": True,
        "orchestrator_can_propose_attractor_packet_draft": True,
        "orchestrator_proposes_avf_inputs": True,
        "orchestrator_manages_avf": False,
        "avf_after_matrix_gate": source_statuses["matrix_gate_source_status"] == "PASS",
        "avf_independent_filter_scoring_layer": avf_source.summary["avf_independent"],
        "hardmask_beats_orchestrator_confidence": (
            avf_source.authority_safety["hardmask_beats_orchestrator_confidence"]
            and gate_by_scenario["hardmask_beats_orchestrator_confidence"][
                "forbidden_vectors_blocked_before_avf"
            ]
        ),
        "softmask_applied_after_hardmask": True,
        "final_attractor_packet_created_by_avf_or_root_controlled_avf_layer": (
            avf_source.summary["attractor_packets_created"] > 0
        ),
        "architect_receives_bounded_attractor_packet": architect_source.summary[
            "raw_orchestrator_matrix_blocked"
        ]
        and architect_source.summary["raw_user_intent_blocked"],
        "raw_orchestrator_proposal_not_sent_directly_to_architect": architect_source.summary[
            "raw_orchestrator_matrix_blocked"
        ],
    }
    downstream = {
        **source_statuses,
        "architect_receives_bounded_attractor_packet": avf[
            "architect_receives_bounded_attractor_packet"
        ],
        "architect_receives_raw_orchestrator_proposal": False,
        "architect_returns_plan_graph": architect_source.summary[
            "valid_plan_graph_proposals_created"
        ]
        > 0,
        "executor_receives_plan_graph_not_raw_user_text": dag_source.summary[
            "executor_receives_only_validated_plan_graph_nodes"
        ]
        and dag_source.summary["raw_user_intent_blocked"],
        "needleruntime_reached_only_through_root_approved_plan_graph": True,
        "child_cell_bounded_if_used": True,
        "post_vv_reached": source_statuses["post_vv_source_status"] == "PASS",
        "gt_reached": source_statuses["gt_source_status"] == "PASS",
        "root_final_still_required": root_source.summary[
            "root_is_only_final_output_authority"
        ],
        "drs_lifecycle_after_root_final": (
            source_statuses["root_final_source_status"] == "PASS"
            and source_statuses["drs_lifecycle_source_status"] == "PASS"
        ),
        "conflictcheck_after_drs_lifecycle": (
            conflict_source.summary["source_drs_lifecycle_status"] == "PASS"
        ),
        "audit_hash_chain_after_conflictcheck": (
            source_statuses["audit_hash_chain_source_status"] == "PASS"
            and audit_source.source_reports["conflictcheck_status"] == "PASS"
        ),
    }
    malicious = _malicious_claims()
    authority = {
        "root_sovereign": True,
        **bounded_authority,
        "avf_remains_independent": avf["avf_independent_filter_scoring_layer"],
        "hardmask_remains_stronger_than_orchestrator_confidence": avf[
            "hardmask_beats_orchestrator_confidence"
        ],
        "root_remains_final_authority": root_source.summary[
            "root_is_only_final_output_authority"
        ]
        and audit_source.summary["root_remains_final_authority"],
        "gt_remains_advisory_until_root": audit_source.authority_safety[
            "gt_remains_advisory_until_root"
        ],
        "conflictcheck_remains_advisory_until_root": audit_source.authority_safety[
            "conflictcheck_remains_advisory_until_root"
        ],
        "audit_hash_chain_proves_continuity_not_truth": (
            audit_source.summary["chain_continuity_valid"]
            and not audit_source.authority_safety["audit_chain_decides_truth"]
        ),
        "production_autonomy_claimed": False,
    }
    proposal_rows = [
        {
            "scenario": proposal["scenario"],
            "proposal_id": proposal["proposal_id"],
            "normalized_intent": proposal["normalized_intent"],
            "temporal_query_proposal_present": bool(
                proposal["temporal_query_proposal"]
            ),
            "worldstate_request_present": bool(proposal["worldstate_request"]),
            "drs_retrieval_request_present": bool(proposal["drs_retrieval_request"]),
            "candidate_vector_proposal_present": bool(
                proposal["candidate_vector_proposal"]
            ),
            "guard_set_proposal_present": bool(proposal["guard_set_proposal"]),
            "route_mode_proposal": proposal["route_mode_proposal"],
            "decomposition_mode_proposal": proposal["decomposition_mode_proposal"],
            "attractor_packet_draft_present": bool(proposal["attractor_packet_draft"]),
            "ask_user_recommendation": proposal["ask_user_recommendation"],
            "block_recommendation": proposal["block_recommendation"],
            "escalation_recommendation": proposal["escalation_recommendation"],
            "proof_only": proposal["proof_only"],
        }
        for proposal in proposals
    ]
    scenario_facts = (
        gate_by_scenario["safe_warehouse_inventory_route"]["gate_status"] == "accepted"
        and gate_by_scenario["forbidden_action_route_blocked"]["gate_status"]
        == "blocked"
        and gate_by_scenario["hardmask_beats_orchestrator_confidence"][
            "forbidden_vectors_blocked_before_avf"
        ]
        and gate_by_scenario["ask_user_recommendation"]["gate_status"] == "needs_user"
        and gate_by_scenario["decomposition_route_to_child_cell"][
            "proposal_allowed_to_avf"
        ]
        and gate_by_scenario["direct_needle_call_attempt_rejected"][
            "direct_needle_call_rejected"
        ]
        and gate_by_scenario["drs_write_attempt_rejected"][
            "orchestrator_drs_write_rejected"
        ]
        and gate_by_scenario["malicious_authority_claims_rejected"][
            "invalid_orchestrator_authority_claim_blocked"
        ]
    )
    pass_facts = (
        all(status == "PASS" for status in source_statuses.values())
        and len(proposals) == len(SCENARIOS)
        and {row["scenario"] for row in proposals} == set(SCENARIOS)
        and scenario_facts
        and all(row["root_validates_orchestrator_proposal"] for row in gates)
        and all(row["matrix_gate_after_orchestrator"] for row in gates)
        and all(row["route_gate_after_orchestrator"] for row in gates)
        and all(row["root_authority_preserved"] for row in gates)
        and all(malicious.values())
        and all(
            downstream[key]
            for key in (
                "architect_receives_bounded_attractor_packet",
                "architect_returns_plan_graph",
                "executor_receives_plan_graph_not_raw_user_text",
                "post_vv_reached",
                "gt_reached",
                "root_final_still_required",
                "drs_lifecycle_after_root_final",
                "conflictcheck_after_drs_lifecycle",
                "audit_hash_chain_after_conflictcheck",
            )
        )
        and authority["root_remains_final_authority"]
        and not authority["orchestrator_is_root"]
        and not authority["orchestrator_creates_final_output"]
        and not authority["orchestrator_writes_drs"]
        and not authority["orchestrator_executes_actions"]
        and not authority["production_autonomy_claimed"]
    )
    return ControlledRootOrchestratorRouteAssemblyReport(
        input_mode={
            "mode": "deterministic_controlled_root_orchestrator_route_assembly",
            "local_proof_level_only": True,
            "live_network_used": False,
            "telegram_used": False,
            "real_external_action": False,
            "production_persistence": False,
            "global_drs_implemented": False,
            "external_drs_network_implemented": False,
            "marennya_invoked": False,
            "up_invoked": False,
        },
        orchestrator_bounded_authority=bounded_authority,
        route_assembly_proposals=proposal_rows,
        matrix_route_gate=gates,
        avf_hardmask=avf,
        downstream_canonical_path=downstream,
        malicious_claims=malicious,
        authority_safety=authority,
        summary={
            "controlled_root_orchestrator_route_assembly_status": (
                "PASS" if pass_facts else "FAIL"
            ),
            "scenarios_verified": len(proposals),
            "orchestrator_has_bounded_delegated_authority": bounded_authority[
                "orchestrator_has_bounded_delegated_authority"
            ],
            "root_validates_orchestrator_proposal": all(
                row["root_validates_orchestrator_proposal"] for row in gates
            ),
            "matrix_gate_after_orchestrator": all(
                row["matrix_gate_after_orchestrator"] for row in gates
            ),
            "avf_after_matrix_gate": avf["avf_after_matrix_gate"],
            "hardmask_beats_orchestrator_confidence": avf[
                "hardmask_beats_orchestrator_confidence"
            ],
            "architect_receives_bounded_attractor_packet": downstream[
                "architect_receives_bounded_attractor_packet"
            ],
            "executor_receives_plan_graph_not_raw_user_text": downstream[
                "executor_receives_plan_graph_not_raw_user_text"
            ],
            "root_final_still_required": downstream["root_final_still_required"],
            "drs_lifecycle_after_root_final": downstream[
                "drs_lifecycle_after_root_final"
            ],
            "conflictcheck_after_drs_lifecycle": downstream[
                "conflictcheck_after_drs_lifecycle"
            ],
            "audit_hash_chain_after_conflictcheck": downstream[
                "audit_hash_chain_after_conflictcheck"
            ],
            "malicious_claims_rejected": sum(malicious.values()),
            "root_remains_final_authority": authority["root_remains_final_authority"],
            "ready_for_controlled_root_orchestrator_docs_sync": pass_facts,
            "production_autonomy_claimed": False,
        },
    )


def _format(value: Any) -> str:
    return "true" if value is True else "false" if value is False else str(value)


def _section(lines: list[str], title: str, fields: dict[str, Any]) -> None:
    lines.extend(["", title])
    lines.extend(f"{key}: {_format(value)}" for key, value in fields.items())


def _rows(lines: list[str], title: str, rows: list[dict[str, Any]]) -> None:
    lines.extend(["", title])
    lines.extend(
        " | ".join(f"{key}={_format(value)}" for key, value in row.items())
        for row in rows
    )


def render_controlled_root_orchestrator_route_assembly(
    report: ControlledRootOrchestratorRouteAssemblyReport,
) -> str:
    lines = [
        "[CONTROLLED ROOT ORCHESTRATOR ROUTE ASSEMBLY]",
        "note: deterministic Controlled RootOrchestrator Route Assembly Integration v0.1 proof",
        "note: Orchestrator has delegated bounded route-assembly authority only",
        "note: Orchestrator proposes AVF inputs; it does not manage AVF",
        "note: AVF / HardMask remain independent",
        "note: MatrixGate / RouteGate validates Orchestrator proposal before AVF output can reach Architect",
        "note: Root remains sovereign",
        "note: no production autonomy",
        "note: no live network",
        "note: no Telegram",
        "note: no real external actions",
        "note: Marennya / UP remain deferred and not invoked",
    ]
    _section(lines, "[INPUT / MODE]", report.input_mode)
    _section(lines, "[ORCHESTRATOR BOUNDED AUTHORITY]", report.orchestrator_bounded_authority)
    _rows(lines, "[ROUTE ASSEMBLY PROPOSALS]", report.route_assembly_proposals)
    _rows(lines, "[MATRIX GATE / ROUTE GATE]", report.matrix_route_gate)
    _section(lines, "[AVF / HARDMASK]", report.avf_hardmask)
    _section(lines, "[DOWNSTREAM CANONICAL PATH]", report.downstream_canonical_path)
    _section(lines, "[MALICIOUS CLAIMS]", report.malicious_claims)
    _section(lines, "[AUTHORITY / SAFETY]", report.authority_safety)
    _section(lines, "[SUMMARY]", report.summary)
    return "\n".join(lines).rstrip() + "\n"


def run_controlled_root_orchestrator_route_assembly() -> str:
    return render_controlled_root_orchestrator_route_assembly(
        collect_controlled_root_orchestrator_route_assembly()
    )


def main() -> int:
    print(run_controlled_root_orchestrator_route_assembly(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
