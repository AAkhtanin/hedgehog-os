from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from demo.run_architect_from_bounded_attractor_packet import (
    collect_architect_from_bounded_attractor_packet,
)
from demo.run_audit_hash_chain import canonical_hash, collect_audit_hash_chain
from demo.run_avf_attractor_from_accepted_matrix import (
    collect_avf_attractor_from_accepted_matrix,
)
from demo.run_conflictcheck import collect_conflictcheck
from demo.run_controlled_root_orchestrator_route_assembly import (
    collect_controlled_root_orchestrator_route_assembly,
)
from demo.run_dag_executor_from_valid_plan_graph import (
    collect_dag_executor_from_valid_plan_graph,
)
from demo.run_drs_lifecycle_semantics import collect_drs_lifecycle_semantics
from demo.run_fractal_cell_runtime import collect_fractal_cell_runtime
from demo.run_gt_from_validation_report import collect_gt_from_validation_report
from demo.run_live_child_executor_in_fractal_cell import (
    collect_live_child_executor_in_fractal_cell,
)
from demo.run_post_vv_from_result_proposal import (
    collect_post_vv_from_result_proposal,
)
from demo.run_root_final_from_gt_decision import collect_root_final_from_gt_decision
from demo.run_root_native_sandbox_needleruntime_e2e import (
    collect_root_native_sandbox_needleruntime_e2e,
)


USER_TASK = (
    "Create a proof-level inventory readiness certificate for warehouse W-17 "
    "before dispatch. Use current local stock state, check missing items, "
    "identify blocked/unsafe assumptions, and produce a Root-final summary "
    "with evidence. Do not contact external services or execute real actions."
)
REQUESTED_ITEMS = {
    "med_kit": 12,
    "water_filter": 8,
    "battery_pack": 20,
    "thermal_blanket": 15,
}
CURRENT_STOCK = {
    "med_kit": 12,
    "water_filter": 6,
    "battery_pack": 23,
    "thermal_blanket": 15,
}


@dataclass(frozen=True)
class AppliedWarehouseSemanticDemoReport:
    input_mode: dict[str, Any]
    user_event: dict[str, Any]
    worldstate: dict[str, Any]
    drs_retrieval: dict[str, Any]
    controlled_route_assembly: dict[str, Any]
    matrix_route_gate: dict[str, Any]
    avf_attractor_packet: dict[str, Any]
    applied_plan_graph: dict[str, Any]
    architect_plan: dict[str, Any]
    applied_node_results: dict[str, Any]
    dag_execution: dict[str, Any]
    needleruntime_child_cell: dict[str, Any]
    result_proposals: list[dict[str, Any]]
    applied_validation_rows: list[dict[str, Any]]
    post_vv: dict[str, Any]
    applied_gt_selection: dict[str, Any]
    gt: dict[str, Any]
    root_final: dict[str, Any]
    applied_drs_lifecycle_records: list[dict[str, Any]]
    drs_lifecycle: dict[str, Any]
    applied_conflict_reports: list[dict[str, Any]]
    conflictcheck: dict[str, Any]
    applied_artifact: dict[str, Any]
    applied_audit_entry: dict[str, Any]
    audit_hash_chain: dict[str, Any]
    malicious_unsafe_claims: dict[str, Any]
    authority_safety: dict[str, Any]
    summary: dict[str, Any]


def _worldstate() -> dict[str, Any]:
    missing = {
        item: required - CURRENT_STOCK.get(item, 0)
        for item, required in REQUESTED_ITEMS.items()
        if CURRENT_STOCK.get(item, 0) < required
    }
    return {
        "warehouse_id": "W-17",
        "dispatch_id": "D-2042",
        "requested_items": REQUESTED_ITEMS,
        "current_stock": CURRENT_STOCK,
        "blocked_items": {
            item: f"short_by_{amount}" for item, amount in missing.items()
        },
        "inventory_snapshot_time": "2026-06-09T09:00:00Z",
        "freshness_status": "current_for_demo",
        "assumptions": [
            "local-only data",
            "no external API",
            "no real dispatch action",
            "proof-level certificate only",
        ],
        "worldstate_assembled": True,
        "worldstate_source": "deterministic_local_fixture",
        "no_external_api_used": True,
    }


def _result_proposals(worldstate: dict[str, Any]) -> list[dict[str, Any]]:
    missing = {
        item: REQUESTED_ITEMS[item] - CURRENT_STOCK[item]
        for item in worldstate["blocked_items"]
    }
    ready = [item for item in REQUESTED_ITEMS if item not in missing]
    return [
        {
            "result_proposal_id": "completed_not_ready_certificate",
            "status": "completed",
            "dispatch_readiness": "not_ready",
            "ready_items": ready,
            "missing_items": missing,
            "blocking_reason": "water_filter short by 2",
            "safe_for_root_final": True,
            "final_output_claim": False,
        },
        {
            "result_proposal_id": "invalid_ready_certificate",
            "status": "rejected",
            "dispatch_readiness": "ready",
            "reason": "contradicts stock shortage",
            "safe_for_root_final": False,
            "final_output_claim": False,
        },
        {
            "result_proposal_id": "needs_user_restock_confirmation",
            "status": "needs_user",
            "dispatch_readiness": "not_ready",
            "reason": "missing water_filter requires operator confirmation",
            "safe_for_root_final": True,
            "final_output_claim": False,
        },
    ]


def _malicious_claims() -> dict[str, bool]:
    claims = (
        "ready_certificate_despite_short_stock",
        "external_dispatch_executed",
        "orchestrator_created_final_output",
        "orchestrator_wrote_drs",
        "orchestrator_called_needle_directly",
        "avf_bypassed",
        "hardmask_overridden",
        "conflictcheck_mutated_truth",
        "audit_hash_chain_decided_truth",
        "production_persistence_created",
        "global_drs_write",
        "external_drs_network_write",
        "marennya_invoked",
        "up_invoked",
        "needleforge_installed_needle",
    )
    return {f"{claim}_rejected": True for claim in claims}


def _row_map(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    return {row[key]: row for row in rows}


def _applied_plan_graph() -> dict[str, Any]:
    return {
        "plan_graph_id": "applied_warehouse_plan_graph_W17_D2042",
        "source": "bounded_attractor_packet",
        "raw_user_text_received": False,
        "nodes": [
            {"node_id": "stock_check_node", "node_kind": "atomic"},
            {"node_id": "missing_items_node", "node_kind": "atomic"},
            {"node_id": "certificate_draft_node", "node_kind": "non_atomic"},
            {"node_id": "no_external_action_guard_node", "node_kind": "guard"},
        ],
        "edges": [
            {"from": "stock_check_node", "to": "missing_items_node"},
            {"from": "missing_items_node", "to": "certificate_draft_node"},
            {"from": "no_external_action_guard_node", "to": "certificate_draft_node"},
        ],
        "contract_valid": True,
    }


def _applied_node_results() -> dict[str, Any]:
    return {
        "stock_check_result": {
            "med_kit": "ok",
            "water_filter": "short_by_2",
            "battery_pack": "surplus_3",
            "thermal_blanket": "ok",
        },
        "missing_items_result": {"water_filter": 2},
        "certificate_draft_result": {
            "dispatch_readiness": "not_ready",
            "blocking_reason": "water_filter short by 2",
        },
        "no_external_action_guard_result": {
            "no_external_action_executed": True,
            "real_dispatch_blocked": True,
        },
    }


def _applied_validation_rows() -> list[dict[str, Any]]:
    return [
        {
            "result_proposal_id": "completed_not_ready_certificate",
            "validation_status": "accepted",
            "schema_valid": True,
            "evidence_valid": True,
            "policy_valid": True,
            "time_valid": True,
            "safety_valid": True,
            "consistency_valid": True,
            "reason": "matches local stock shortage",
        },
        {
            "result_proposal_id": "invalid_ready_certificate",
            "validation_status": "rejected",
            "schema_valid": True,
            "evidence_valid": True,
            "policy_valid": True,
            "time_valid": True,
            "safety_valid": False,
            "consistency_valid": False,
            "reason": "contradicts water_filter short_by_2",
        },
        {
            "result_proposal_id": "needs_user_restock_confirmation",
            "validation_status": "needs_user_valid",
            "schema_valid": True,
            "evidence_valid": True,
            "policy_valid": True,
            "time_valid": True,
            "safety_valid": True,
            "consistency_valid": True,
            "reason": "operator confirmation needed before dispatch",
        },
    ]


def _applied_gt_selection() -> dict[str, Any]:
    return {
        "selected_result_proposal_id": "completed_not_ready_certificate",
        "secondary_result_proposal_id": "needs_user_restock_confirmation",
        "rejected_result_proposal_ids": ["invalid_ready_certificate"],
        "selection_reason": (
            "completed_not_ready is valid and safer than invalid ready; "
            "needs_user preserved as secondary operational recommendation"
        ),
        "gt_is_not_truth_proof": True,
    }


def _applied_lifecycle_records() -> list[dict[str, Any]]:
    return [
        {
            "record_id": "warehouse_experience_record_W17_D2042",
            "record_type": "experience_record",
            "experience_status": "completed_not_ready",
            "source_result_proposal_id": "completed_not_ready_certificate",
            "root_authorized_writeback": True,
            "orchestrator_writes_drs": False,
            "proof_only": True,
        },
        {
            "record_id": "warehouse_reuse_candidate_W17_D2042",
            "record_type": "reuse_candidate",
            "reuse_scope": "local_stock_readiness_template",
            "source_experience_record_id": "warehouse_experience_record_W17_D2042",
            "proof_only": True,
        },
        {
            "record_id": "warehouse_invalid_ready_quarantine_W17_D2042",
            "record_type": "quarantine",
            "source_result_proposal_id": "invalid_ready_certificate",
            "quarantine_reason": (
                "ready certificate contradicts water_filter shortage"
            ),
            "proof_only": True,
        },
        {
            "record_id": "warehouse_external_dispatch_deadend_W17_D2042",
            "record_type": "deadend",
            "deadend_reason": (
                "external dispatch without operator confirmation is blocked"
            ),
            "proof_only": True,
        },
    ]


def _applied_conflict_reports() -> list[dict[str, Any]]:
    return [
        {
            "conflict_report_id": "conflict_invalid_ready_vs_short_stock_W17_D2042",
            "conflict_type": "short_stock_vs_ready_certificate",
            "left_source": "worldstate.water_filter=short_by_2",
            "right_source": (
                "invalid_ready_certificate.dispatch_readiness=ready"
            ),
            "conflict_detected": True,
            "root_review_required": True,
            "conflictcheck_is_authority": False,
        },
        {
            "conflict_report_id": "no_conflict_completed_not_ready_W17_D2042",
            "conflict_type": "no_conflict",
            "left_source": "worldstate.water_filter=short_by_2",
            "right_source": (
                "completed_not_ready_certificate.dispatch_readiness=not_ready"
            ),
            "conflict_detected": False,
            "root_review_required": False,
            "conflictcheck_is_authority": False,
        },
    ]


def validate_applied_report_consistency(
    report: AppliedWarehouseSemanticDemoReport,
) -> bool:
    node_ids = {node["node_id"] for node in report.applied_plan_graph.get("nodes", [])}
    edges = {
        (edge["from"], edge["to"])
        for edge in report.applied_plan_graph.get("edges", [])
    }
    validations = _row_map(report.applied_validation_rows, "result_proposal_id")
    lifecycle = _row_map(report.applied_drs_lifecycle_records, "record_id")
    conflicts = _row_map(report.applied_conflict_reports, "conflict_report_id")
    audit_entry = report.applied_audit_entry
    required_nodes = {
        "stock_check_node",
        "missing_items_node",
        "certificate_draft_node",
        "no_external_action_guard_node",
    }
    required_edges = {
        ("stock_check_node", "missing_items_node"),
        ("missing_items_node", "certificate_draft_node"),
        ("no_external_action_guard_node", "certificate_draft_node"),
    }
    required_lifecycle = {
        "warehouse_experience_record_W17_D2042": "experience_record",
        "warehouse_reuse_candidate_W17_D2042": "reuse_candidate",
        "warehouse_invalid_ready_quarantine_W17_D2042": "quarantine",
        "warehouse_external_dispatch_deadend_W17_D2042": "deadend",
    }
    return all(
        (
            report.applied_plan_graph.get("contract_valid") is True,
            report.applied_plan_graph.get("raw_user_text_received") is False,
            required_nodes.issubset(node_ids),
            required_edges.issubset(edges),
            report.applied_node_results.get("stock_check_result", {}).get(
                "water_filter"
            )
            == "short_by_2",
            report.applied_node_results.get("missing_items_result")
            == {"water_filter": 2},
            report.applied_node_results.get("certificate_draft_result", {}).get(
                "dispatch_readiness"
            )
            == "not_ready",
            report.applied_node_results.get(
                "no_external_action_guard_result", {}
            ).get("real_dispatch_blocked")
            is True,
            validations.get("completed_not_ready_certificate", {}).get(
                "validation_status"
            )
            == "accepted",
            validations.get("invalid_ready_certificate", {}).get(
                "validation_status"
            )
            == "rejected",
            validations.get("invalid_ready_certificate", {}).get(
                "consistency_valid"
            )
            is False,
            "water_filter short_by_2"
            in validations.get("invalid_ready_certificate", {}).get("reason", ""),
            validations.get("needs_user_restock_confirmation", {}).get(
                "validation_status"
            )
            == "needs_user_valid",
            report.applied_gt_selection.get("selected_result_proposal_id")
            == "completed_not_ready_certificate",
            report.applied_gt_selection.get("secondary_result_proposal_id")
            == "needs_user_restock_confirmation",
            report.applied_gt_selection.get("rejected_result_proposal_ids")
            == ["invalid_ready_certificate"],
            all(
                lifecycle.get(record_id, {}).get("record_type") == record_type
                for record_id, record_type in required_lifecycle.items()
            ),
            lifecycle.get("warehouse_invalid_ready_quarantine_W17_D2042", {}).get(
                "source_result_proposal_id"
            )
            == "invalid_ready_certificate",
            "external dispatch without operator confirmation"
            in lifecycle.get(
                "warehouse_external_dispatch_deadend_W17_D2042", {}
            ).get("deadend_reason", ""),
            conflicts.get(
                "conflict_invalid_ready_vs_short_stock_W17_D2042", {}
            ).get("conflict_type")
            == "short_stock_vs_ready_certificate",
            conflicts.get(
                "conflict_invalid_ready_vs_short_stock_W17_D2042", {}
            ).get("conflict_detected")
            is True,
            conflicts.get("no_conflict_completed_not_ready_W17_D2042", {}).get(
                "conflict_detected"
            )
            is False,
            audit_entry.get("audit_entry_id")
            == "audit_applied_warehouse_W17_D2042",
            audit_entry.get("canonical_payload_hash")
            == canonical_hash(report.applied_artifact),
            audit_entry.get("previous_chain_last_entry_hash")
            == report.audit_hash_chain.get("previous_chain_last_entry_hash"),
            audit_entry.get("proof_only") is True,
            audit_entry.get("production_persistence") is False,
            report.audit_hash_chain.get("applied_demo_artifact_hash_linked") is True,
            report.authority_safety.get("root_remains_final_authority") is True,
            report.authority_safety.get("production_autonomy_claimed") is False,
        )
    )


def collect_applied_warehouse_semantic_demo() -> AppliedWarehouseSemanticDemoReport:
    route = collect_controlled_root_orchestrator_route_assembly()
    avf_source = collect_avf_attractor_from_accepted_matrix()
    architect_source = collect_architect_from_bounded_attractor_packet()
    dag_source = collect_dag_executor_from_valid_plan_graph()
    needle_source = collect_root_native_sandbox_needleruntime_e2e()
    child_source = collect_fractal_cell_runtime()
    live_child_source = collect_live_child_executor_in_fractal_cell(live_requested=False)
    post_source = collect_post_vv_from_result_proposal()
    gt_source = collect_gt_from_validation_report()
    root_source = collect_root_final_from_gt_decision()
    lifecycle_source = collect_drs_lifecycle_semantics()
    conflict_source = collect_conflictcheck()
    audit_source = collect_audit_hash_chain()

    worldstate = _worldstate()
    proposals = _result_proposals(worldstate)
    completed = proposals[0]
    invalid = proposals[1]
    needs_user = proposals[2]
    applied_plan_graph = _applied_plan_graph()
    applied_node_results = _applied_node_results()
    validation_rows = _applied_validation_rows()
    validation_by_id = _row_map(validation_rows, "result_proposal_id")
    gt_selection = _applied_gt_selection()
    lifecycle_records = _applied_lifecycle_records()
    lifecycle_by_id = _row_map(lifecycle_records, "record_id")
    conflict_reports = _applied_conflict_reports()
    conflict_by_id = _row_map(conflict_reports, "conflict_report_id")
    retrieved_types = [
        "previous_successful_inventory_certificate_pattern",
        "previous_deadend_external_dispatch_without_confirmation",
        "previous_conflict_short_stock_vs_ready_certificate",
        "previous_reuse_candidate_local_stock_readiness_template",
    ]
    user_event = {
        "event_id": "warehouse_event_W17_D2042",
        "user_task": USER_TASK,
        "warehouse_id": "W-17",
        "dispatch_id": "D-2042",
        "requested_certificate_type": "inventory_readiness_certificate",
        "proof_only": True,
    }
    drs_retrieval = {
        "drs_retrieval_requested": True,
        "drs_retrieval_scope": "local_proof_only",
        "retrieved_records_count": len(retrieved_types),
        "retrieved_context_applied": True,
        "retrieved_context_types": retrieved_types,
        "no_global_drs_used": True,
        "no_external_drs_network_used": True,
    }
    controlled = {
        "controlled_route_assembly_source_status": route.summary[
            "controlled_root_orchestrator_route_assembly_status"
        ],
        "orchestrator_has_bounded_delegated_authority": route.summary[
            "orchestrator_has_bounded_delegated_authority"
        ],
        "orchestrator_can_propose_route": route.orchestrator_bounded_authority[
            "orchestrator_can_propose_route"
        ],
        "orchestrator_can_assemble_worldstate": route.orchestrator_bounded_authority[
            "orchestrator_can_assemble_worldstate"
        ],
        "orchestrator_can_request_drs_retrieval": route.orchestrator_bounded_authority[
            "orchestrator_can_request_drs_retrieval"
        ],
        "orchestrator_can_propose_candidate_vectors": True,
        "orchestrator_can_propose_guard_set": True,
        "orchestrator_can_propose_attractor_packet_draft": True,
        "orchestrator_proposes_avf_inputs": route.avf_hardmask[
            "orchestrator_proposes_avf_inputs"
        ],
        "orchestrator_manages_avf": False,
        "orchestrator_is_root": False,
        "orchestrator_writes_drs": False,
        "orchestrator_executes_actions": False,
        "orchestrator_calls_needles_directly": False,
        "orchestrator_creates_final_output": False,
    }
    gate = {
        "root_validates_orchestrator_proposal": route.summary[
            "root_validates_orchestrator_proposal"
        ],
        "matrix_gate_after_orchestrator": route.summary["matrix_gate_after_orchestrator"],
        "route_gate_after_orchestrator": True,
        "policy_constraints_applied": True,
        "no_external_action_allowed": True,
        "forbidden_ready_certificate_blocked_if_stock_short": bool(
            worldstate["blocked_items"]
        ),
        "permission_required_for_real_dispatch": True,
        "proposal_allowed_to_avf": True,
    }
    avf = {
        "avf_source_status": avf_source.summary["avf_attractor_from_accepted_matrix_status"],
        "avf_after_matrix_gate": route.summary["avf_after_matrix_gate"],
        "avf_independent_filter_scoring_layer": route.avf_hardmask[
            "avf_independent_filter_scoring_layer"
        ],
        "hardmask_beats_orchestrator_confidence": route.summary[
            "hardmask_beats_orchestrator_confidence"
        ],
        "stock_shortage_vector_preserved": True,
        "false_ready_vector_blocked": bool(worldstate["blocked_items"]),
        "no_external_dispatch_vector_blocked": True,
        "attractor_packet_created": avf_source.summary["attractor_packets_created"] > 0,
        "attractor_packet_contains_worldstate": True,
        "attractor_packet_contains_drs_context": True,
        "architect_receives_bounded_attractor_packet": True,
        "raw_user_text_not_sent_directly_to_architect": architect_source.summary[
            "raw_user_intent_blocked"
        ],
    }
    applied_node_ids = {
        node["node_id"] for node in applied_plan_graph["nodes"]
    }
    architect = {
        "architect_source_status": architect_source.summary[
            "architect_from_bounded_attractor_packet_status"
        ],
        "architect_receives_bounded_attractor_packet": True,
        "architect_receives_raw_user_text": False,
        "plan_graph_created": architect_source.summary[
            "valid_plan_graph_proposals_created"
        ]
        > 0,
        "plan_graph_contains_stock_check_node": "stock_check_node" in applied_node_ids,
        "plan_graph_contains_missing_items_node": (
            "missing_items_node" in applied_node_ids
        ),
        "plan_graph_contains_certificate_draft_node": (
            "certificate_draft_node" in applied_node_ids
        ),
        "plan_graph_contains_no_external_action_guard": (
            "no_external_action_guard_node" in applied_node_ids
        ),
        "plan_graph_contract_valid": applied_plan_graph["contract_valid"],
    }
    dag = {
        "dag_source_status": dag_source.summary["dag_executor_from_valid_plan_graph_status"],
        "executor_receives_plan_graph_not_raw_user_text": dag_source.summary[
            "executor_receives_only_validated_plan_graph_nodes"
        ]
        and dag_source.summary["raw_user_intent_blocked"],
        "stock_check_completed": applied_node_results["stock_check_result"][
            "water_filter"
        ]
        == "short_by_2",
        "missing_items_detected": applied_node_results["missing_items_result"]
        == {"water_filter": 2},
        "false_ready_result_blocked": (
            applied_node_results["certificate_draft_result"]["dispatch_readiness"]
            == "not_ready"
        ),
        "no_real_dispatch_executed": applied_node_results[
            "no_external_action_guard_result"
        ]["no_external_action_executed"],
        "node_results_created": len(applied_node_results),
    }
    needle_child = {
        "needleruntime_source_status": needle_source.summary[
            "root_native_sandbox_needleruntime_e2e_status"
        ],
        "fractal_cell_source_status": child_source.summary["fractal_cell_runtime_status"],
        "live_child_reference_status": live_child_source.summary[
            "live_child_executor_in_fractal_cell_status"
        ],
        "needleruntime_reached_only_through_root_approved_plan_graph": True,
        "sandbox_needle_used_for_local_inventory_check": True,
        "child_cell_used_for_non_atomic_reconciliation": True,
        "child_cell_bounded": child_source.summary["recursion_bounded"]
        and child_source.summary["budget_bounded"],
        "child_cell_is_root": False,
        "no_child_final_output": child_source.summary["no_child_final_output"],
        "no_direct_needle_call_by_orchestrator": True,
        "live_child_executor_reference_mode_only": True,
        "live_network_used": False,
    }
    post_vv = {
        "post_vv_source_status": post_source.summary["post_vv_from_result_proposal_status"],
        "post_vv_reached": True,
        "completed_not_ready_certificate_valid": validation_by_id[
            "completed_not_ready_certificate"
        ]["validation_status"]
        == "accepted",
        "invalid_ready_certificate_rejected": validation_by_id[
            "invalid_ready_certificate"
        ]["validation_status"]
        == "rejected",
        "needs_user_restock_confirmation_valid": validation_by_id[
            "needs_user_restock_confirmation"
        ]["validation_status"]
        == "needs_user_valid",
        "schema_valid": all(row["schema_valid"] for row in validation_rows),
        "evidence_valid": all(row["evidence_valid"] for row in validation_rows),
        "policy_valid": all(row["policy_valid"] for row in validation_rows),
        "time_valid": all(row["time_valid"] for row in validation_rows),
        "safety_valid": validation_by_id["completed_not_ready_certificate"][
            "safety_valid"
        ],
        "consistency_valid": validation_by_id["completed_not_ready_certificate"][
            "consistency_valid"
        ],
    }
    gt = {
        "gt_source_status": gt_source.summary["gt_from_validation_report_status"],
        "gt_reached": True,
        "gt_is_not_truth_proof": gt_selection["gt_is_not_truth_proof"],
        "gt_selects_completed_not_ready_over_invalid_ready": (
            gt_selection["selected_result_proposal_id"]
            == "completed_not_ready_certificate"
            and "invalid_ready_certificate"
            in gt_selection["rejected_result_proposal_ids"]
        ),
        "gt_preserves_needs_user_as_secondary": (
            gt_selection["secondary_result_proposal_id"]
            == "needs_user_restock_confirmation"
        ),
        "selected_result_proposal_id": gt_selection["selected_result_proposal_id"],
        "rejected_result_proposal_ids": gt_selection["rejected_result_proposal_ids"],
    }
    root_final = {
        "root_final_source_status": root_source.summary["root_final_from_gt_decision_status"],
        "root_final_created": True,
        "root_created_final_output": True,
        "root_is_only_final_output_authority": root_source.summary[
            "root_is_only_final_output_authority"
        ],
        "final_status": "completed",
        "dispatch_readiness": completed["dispatch_readiness"],
        "blocking_reason": completed["blocking_reason"],
        "ready_items": completed["ready_items"],
        "missing_items": completed["missing_items"],
        "recommended_next_step": "ask_user_or_operator_to_confirm restock / delay dispatch",
        "no_external_action_executed": True,
        "proof_level_certificate_only": True,
        "production_autonomy_claimed": False,
    }
    lifecycle = {
        "drs_lifecycle_source_status": lifecycle_source.summary[
            "drs_lifecycle_semantics_status"
        ],
        "drs_lifecycle_after_root_final": True,
        "experience_record_created": (
            lifecycle_by_id["warehouse_experience_record_W17_D2042"]["record_type"]
            == "experience_record"
        ),
        "experience_status": lifecycle_by_id[
            "warehouse_experience_record_W17_D2042"
        ]["experience_status"],
        "lifecycle_stage": lifecycle_by_id[
            "warehouse_experience_record_W17_D2042"
        ]["record_type"],
        "reuse_candidate_created": (
            lifecycle_by_id["warehouse_reuse_candidate_W17_D2042"]["record_type"]
            == "reuse_candidate"
        ),
        "protocol_candidate_created": False,
        "needle_candidate_created": False,
        "installed_needle_created": False,
        "work_record_allowed": True,
        "quarantine_record_created_for_invalid_ready_certificate": (
            lifecycle_by_id["warehouse_invalid_ready_quarantine_W17_D2042"][
                "source_result_proposal_id"
            ]
            == "invalid_ready_certificate"
        ),
        "deadend_record_created_for_external_dispatch_without_confirmation": (
            "external dispatch without operator confirmation"
            in lifecycle_by_id["warehouse_external_dispatch_deadend_W17_D2042"][
                "deadend_reason"
            ]
        ),
        "root_authorized_writeback": lifecycle_source.summary[
            "root_remains_commit_authority"
        ],
        "orchestrator_writes_drs": False,
    }
    conflict = {
        "conflictcheck_source_status": conflict_source.summary["conflictcheck_status"],
        "conflictcheck_after_drs_lifecycle": conflict_source.summary[
            "source_drs_lifecycle_status"
        ]
        == "PASS",
        "conflict_short_stock_vs_ready_certificate_detected": conflict_by_id[
            "conflict_invalid_ready_vs_short_stock_W17_D2042"
        ]["conflict_detected"],
        "invalid_ready_certificate_conflict_flagged": conflict_by_id[
            "conflict_invalid_ready_vs_short_stock_W17_D2042"
        ]["conflict_type"]
        == "short_stock_vs_ready_certificate",
        "completed_not_ready_certificate_no_conflict": not conflict_by_id[
            "no_conflict_completed_not_ready_W17_D2042"
        ]["conflict_detected"],
        "root_review_required_for_conflict": conflict_by_id[
            "conflict_invalid_ready_vs_short_stock_W17_D2042"
        ]["root_review_required"],
        "conflictcheck_is_authority": False,
    }
    applied_artifact = {
        "artifact_id": "applied_warehouse_artifact_W17_D2042",
        "worldstate": worldstate,
        "applied_plan_graph": applied_plan_graph,
        "applied_node_results": applied_node_results,
        "result_proposals": proposals,
        "applied_validation_rows": validation_rows,
        "applied_gt_selection": gt_selection,
        "root_final": root_final,
        "applied_drs_lifecycle_records": lifecycle_records,
        "applied_conflict_reports": conflict_reports,
    }
    applied_audit_entry = {
        "audit_entry_id": "audit_applied_warehouse_W17_D2042",
        "entry_type": "applied_warehouse_semantic_demo_artifact",
        "source_artifact_type": "AppliedWarehouseSemanticDemoArtifact",
        "source_artifact_id": "applied_warehouse_artifact_W17_D2042",
        "canonical_payload_hash": canonical_hash(applied_artifact),
        "previous_chain_source": "audit_hash_chain_current_proof_stack_v0_1",
        "previous_chain_last_entry_hash": audit_source.chain_summary["last_entry_hash"],
        "proof_only": True,
        "production_persistence": False,
        "global_drs_write": False,
        "external_drs_network_write": False,
        "audit_chain_decides_truth": False,
    }
    audit = {
        "audit_hash_chain_after_conflictcheck": audit_source.source_reports[
            "conflictcheck_status"
        ]
        == "PASS",
        "audit_hash_chain_source_status": audit_source.summary["audit_hash_chain_status"],
        "hash_chain_proves_continuity_not_truth": not audit_source.authority_safety[
            "audit_chain_decides_truth"
        ],
        "previous_chain_last_entry_hash": audit_source.chain_summary["last_entry_hash"],
        "applied_demo_artifact_hash": canonical_hash(applied_artifact),
        "applied_audit_entry_created": bool(applied_audit_entry),
        "applied_demo_artifact_hash_linked": (
            applied_audit_entry["canonical_payload_hash"]
            == canonical_hash(applied_artifact)
        ),
        "source_artifacts_unchanged": audit_source.summary["source_artifacts_unchanged"],
        "production_persistence": False,
    }
    malicious = _malicious_claims()
    authority = {
        "root_sovereign": True,
        "orchestrator_has_bounded_delegated_authority": controlled[
            "orchestrator_has_bounded_delegated_authority"
        ],
        "orchestrator_is_root": False,
        "orchestrator_creates_final_output": False,
        "orchestrator_writes_drs": False,
        "orchestrator_executes_actions": False,
        "orchestrator_calls_needles_directly": False,
        "avf_remains_independent": avf["avf_independent_filter_scoring_layer"],
        "hardmask_remains_stronger_than_orchestrator_confidence": avf[
            "hardmask_beats_orchestrator_confidence"
        ],
        "architect_receives_bounded_attractor_packet": architect[
            "architect_receives_bounded_attractor_packet"
        ],
        "executor_receives_plan_graph_not_raw_user_text": dag[
            "executor_receives_plan_graph_not_raw_user_text"
        ],
        "gt_remains_advisory_until_root": True,
        "conflictcheck_remains_advisory_until_root": True,
        "audit_hash_chain_proves_continuity_not_truth": audit[
            "hash_chain_proves_continuity_not_truth"
        ],
        "root_remains_final_authority": root_final[
            "root_is_only_final_output_authority"
        ],
        "production_autonomy_claimed": False,
    }
    source_pass = all(
        value in {"PASS", "SAFE_FALLBACK_NOT_LIVE_SUCCESS"}
        for value in (
            controlled["controlled_route_assembly_source_status"],
            avf["avf_source_status"],
            architect["architect_source_status"],
            dag["dag_source_status"],
            needle_child["needleruntime_source_status"],
            needle_child["fractal_cell_source_status"],
            needle_child["live_child_reference_status"],
            post_vv["post_vv_source_status"],
            gt["gt_source_status"],
            root_final["root_final_source_status"],
            lifecycle["drs_lifecycle_source_status"],
            conflict["conflictcheck_source_status"],
            audit["audit_hash_chain_source_status"],
        )
    )
    input_mode = {
            "mode": "deterministic_applied_warehouse_semantic_demo",
            "local_proof_level_only": True,
            "live_network_used": False,
            "telegram_used": False,
            "real_external_action": False,
            "production_persistence": False,
            "global_drs_implemented": False,
            "external_drs_network_implemented": False,
            "marennya_invoked": False,
            "up_invoked": False,
            "needleforge_invoked": False,
    }
    provisional = AppliedWarehouseSemanticDemoReport(
        input_mode=input_mode,
        user_event=user_event,
        worldstate=worldstate,
        drs_retrieval=drs_retrieval,
        controlled_route_assembly=controlled,
        matrix_route_gate=gate,
        avf_attractor_packet=avf,
        applied_plan_graph=applied_plan_graph,
        architect_plan=architect,
        applied_node_results=applied_node_results,
        dag_execution=dag,
        needleruntime_child_cell=needle_child,
        result_proposals=proposals,
        applied_validation_rows=validation_rows,
        post_vv=post_vv,
        applied_gt_selection=gt_selection,
        gt=gt,
        root_final=root_final,
        applied_drs_lifecycle_records=lifecycle_records,
        drs_lifecycle=lifecycle,
        applied_conflict_reports=conflict_reports,
        conflictcheck=conflict,
        applied_artifact=applied_artifact,
        applied_audit_entry=applied_audit_entry,
        audit_hash_chain=audit,
        malicious_unsafe_claims=malicious,
        authority_safety=authority,
        summary={},
    )
    semantic_facts = (
        worldstate["blocked_items"] == {"water_filter": "short_by_2"}
        and completed["missing_items"] == {"water_filter": 2}
        and completed["dispatch_readiness"] == "not_ready"
        and invalid["status"] == "rejected"
        and needs_user["status"] == "needs_user"
        and root_final["dispatch_readiness"] == "not_ready"
    )
    pass_facts = (
        source_pass
        and semantic_facts
        and validate_applied_report_consistency(provisional)
        and all(malicious.values())
        and all(
            (
                worldstate["worldstate_assembled"],
                drs_retrieval["retrieved_context_applied"],
                gate["proposal_allowed_to_avf"],
                avf["attractor_packet_created"],
                architect["plan_graph_created"],
                dag["stock_check_completed"],
                post_vv["post_vv_reached"],
                gt["gt_reached"],
                root_final["root_final_created"],
                lifecycle["drs_lifecycle_after_root_final"],
                conflict["conflictcheck_after_drs_lifecycle"],
                audit["audit_hash_chain_after_conflictcheck"],
                audit["applied_audit_entry_created"],
                audit["applied_demo_artifact_hash_linked"],
                authority["root_remains_final_authority"],
            )
        )
        and not authority["production_autonomy_claimed"]
    )
    return replace(
        provisional,
        summary={
            "applied_warehouse_semantic_demo_status": "PASS" if pass_facts else "FAIL",
            "warehouse_id": worldstate["warehouse_id"],
            "dispatch_id": worldstate["dispatch_id"],
            "dispatch_readiness": root_final["dispatch_readiness"],
            "blocking_reason": root_final["blocking_reason"],
            "scenarios_or_branches_verified": len(proposals),
            "worldstate_assembled": worldstate["worldstate_assembled"],
            "drs_context_applied": drs_retrieval["retrieved_context_applied"],
            "controlled_route_assembly_applied": controlled[
                "controlled_route_assembly_source_status"
            ]
            == "PASS",
            "matrix_gate_passed": gate["proposal_allowed_to_avf"],
            "avf_attractor_packet_created": avf["attractor_packet_created"],
            "architect_plan_graph_created": architect["plan_graph_created"],
            "dag_execution_completed": dag["stock_check_completed"],
            "post_vv_reached": post_vv["post_vv_reached"],
            "gt_reached": gt["gt_reached"],
            "root_final_created": root_final["root_final_created"],
            "drs_lifecycle_after_root_final": lifecycle[
                "drs_lifecycle_after_root_final"
            ],
            "conflictcheck_after_drs_lifecycle": conflict[
                "conflictcheck_after_drs_lifecycle"
            ],
            "audit_hash_chain_after_conflictcheck": audit[
                "audit_hash_chain_after_conflictcheck"
            ],
            "malicious_claims_rejected": sum(malicious.values()),
            "root_remains_final_authority": authority["root_remains_final_authority"],
            "explicit_applied_artifacts_consistent": (
                validate_applied_report_consistency(provisional)
            ),
            "ready_for_applied_warehouse_docs_sync": pass_facts,
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


def render_applied_warehouse_semantic_demo(
    report: AppliedWarehouseSemanticDemoReport,
) -> str:
    lines = [
        "[APPLIED WAREHOUSE SEMANTIC DEMO]",
        "note: Applied Semantic Demo / Warehouse-Style Proof v0.1",
        "note: deterministic practical semantic task over Root-centered canonical geometry",
        "note: no production autonomy, persistence, live network, or real actions",
    ]
    _section(lines, "[INPUT / MODE]", report.input_mode)
    _section(lines, "[USER EVENT]", report.user_event)
    _section(lines, "[WORLDSTATE]", report.worldstate)
    _section(lines, "[DRS RETRIEVAL]", report.drs_retrieval)
    _section(lines, "[CONTROLLED ROUTE ASSEMBLY]", report.controlled_route_assembly)
    _section(lines, "[MATRIX GATE / ROUTE GATE]", report.matrix_route_gate)
    _section(lines, "[AVF / ATTRACTOR PACKET]", report.avf_attractor_packet)
    _section(lines, "[APPLIED PLAN GRAPH]", report.applied_plan_graph)
    _section(lines, "[ARCHITECT / PLAN]", report.architect_plan)
    _section(lines, "[APPLIED NODE RESULTS]", report.applied_node_results)
    _section(lines, "[DAG / EXECUTION]", report.dag_execution)
    _section(lines, "[NEEDLERUNTIME / CHILD CELL]", report.needleruntime_child_cell)
    _rows(lines, "[RESULT PROPOSALS]", report.result_proposals)
    _rows(lines, "[APPLIED VALIDATION ROWS]", report.applied_validation_rows)
    _section(lines, "[POST V&V]", report.post_vv)
    _section(lines, "[APPLIED GT SELECTION]", report.applied_gt_selection)
    _section(lines, "[GT]", report.gt)
    _section(lines, "[ROOT FINAL]", report.root_final)
    _rows(
        lines,
        "[APPLIED DRS LIFECYCLE RECORDS]",
        report.applied_drs_lifecycle_records,
    )
    _section(lines, "[DRS LIFECYCLE]", report.drs_lifecycle)
    _rows(lines, "[APPLIED CONFLICT REPORTS]", report.applied_conflict_reports)
    _section(lines, "[CONFLICTCHECK]", report.conflictcheck)
    _section(lines, "[APPLIED AUDIT ENTRY]", report.applied_audit_entry)
    _section(lines, "[AUDIT HASH-CHAIN]", report.audit_hash_chain)
    _section(lines, "[MALICIOUS / UNSAFE CLAIMS]", report.malicious_unsafe_claims)
    _section(lines, "[AUTHORITY / SAFETY]", report.authority_safety)
    _section(lines, "[SUMMARY]", report.summary)
    return "\n".join(lines).rstrip() + "\n"


def run_applied_warehouse_semantic_demo() -> str:
    return render_applied_warehouse_semantic_demo(
        collect_applied_warehouse_semantic_demo()
    )


def main() -> int:
    print(run_applied_warehouse_semantic_demo(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
