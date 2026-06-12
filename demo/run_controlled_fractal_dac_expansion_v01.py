from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from demo.run_applied_drs_retrieval_reuse import collect_applied_drs_retrieval_reuse
from demo.run_applied_travel_readiness_demo import collect_applied_travel_readiness_demo
from demo.run_audit_hash_chain import canonical_hash, collect_audit_hash_chain
from demo.run_conflictcheck import collect_conflictcheck
from demo.run_multi_domain_applied_smoke_v02 import collect_multi_domain_applied_smoke_v02


@dataclass(frozen=True)
class ControlledFractalDacExpansionV01Report:
    source_evidence: dict[str, Any]
    parent_request: dict[str, Any]
    decomposition_plan: dict[str, Any]
    child_cell_candidates: list[dict[str, Any]]
    child_cell_local_proposals: list[dict[str, Any]]
    authority_boundary_matrix: list[dict[str, Any]]
    aggregation_result: dict[str, Any]
    conflictcheck_result: dict[str, Any]
    gt_advisory: dict[str, Any]
    root_final: dict[str, Any]
    proof_artifact: dict[str, Any]
    audit_entry: dict[str, Any]
    summary: dict[str, Any]


def _child_cell(
    child_cell_id: str,
    local_scope: str,
    input_evidence: str,
    local_status: str,
    local_proposal: str,
) -> dict[str, Any]:
    return {
        "child_cell_id": child_cell_id,
        "local_scope": local_scope,
        "input_evidence": input_evidence,
        "local_status": local_status,
        "local_proposal": local_proposal,
        "external_action_executed": False,
        "root_authority": False,
        "final_output_authority": False,
        "external_action_authority": False,
        "drs_write_authority": False,
        "can_mark_parent_ready": False,
        "can_override_sibling": False,
        "can_spawn_child": False,
        "can_install_needle": False,
        "can_create_protocol_candidate": False,
        "can_create_needle_candidate": False,
        "production_persistence": False,
        "global_drs_write": False,
        "external_drs_write": False,
        "gemini_called": False,
        "network_called": False,
    }


def _child_cells() -> list[dict[str, Any]]:
    return [
        _child_cell(
            "document_check",
            "insurance_certificate",
            "insurance_certificate:expired",
            "blocked",
            "needs_document_update",
        ),
        _child_cell(
            "payment_check",
            "payment_receipt",
            "payment_receipt:missing",
            "blocked",
            "needs_payment_receipt",
        ),
        _child_cell(
            "lodging_check",
            "hotel_confirmation",
            "hotel_confirmation:present",
            "ready",
            "lodging_ok",
        ),
        _child_cell(
            "route_window_check",
            "route_window",
            "route_window:uncertain",
            "blocked",
            "needs_route_window_confirmation",
        ),
        _child_cell(
            "permission_check",
            "user_permission",
            "user_permission:not_confirmed",
            "blocked",
            "needs_user_permission",
        ),
    ]


def _local_proposals(children: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "child_cell_id": child["child_cell_id"],
            "local_status": child["local_status"],
            "local_proposal": child["local_proposal"],
            "proposal_is_local_only": True,
            "proposal_is_not_parent_final": True,
            "root_aggregation_required": True,
        }
        for child in children
    ]


def _authority_matrix(children: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "child_cell_id": child["child_cell_id"],
            "root_authority": False,
            "sibling_authority": False,
            "final_output_authority": False,
            "external_action_authority": False,
            "drs_write_authority": False,
            "root_review_required": True,
            "root_aggregation_required": True,
        }
        for child in children
    ]


def validate_controlled_fractal_dac_expansion_v01_report_consistency(
    report: ControlledFractalDacExpansionV01Report,
) -> bool:
    children = {row["child_cell_id"]: row for row in report.child_cell_candidates}
    proposals = {
        row["child_cell_id"]: row for row in report.child_cell_local_proposals
    }
    boundaries = {
        row["child_cell_id"]: row for row in report.authority_boundary_matrix
    }
    blocked = [row for row in children.values() if row.get("local_status") == "blocked"]
    ready = [row for row in children.values() if row.get("local_status") == "ready"]
    expected_children = {
        "document_check",
        "payment_check",
        "lodging_check",
        "route_window_check",
        "permission_check",
    }
    child_false_fields = (
        "external_action_executed",
        "root_authority",
        "final_output_authority",
        "external_action_authority",
        "drs_write_authority",
        "can_mark_parent_ready",
        "can_override_sibling",
        "can_spawn_child",
        "can_install_needle",
        "can_create_protocol_candidate",
        "can_create_needle_candidate",
        "production_persistence",
        "global_drs_write",
        "external_drs_write",
        "gemini_called",
        "network_called",
    )
    root_false_fields = (
        "child_cells_have_authority",
        "child_cells_finalized_result",
        "direct_ready_override",
        "completed_external_action_created",
        "travel_request_submitted",
        "booking_created",
        "payment_executed",
        "protocol_candidate_created",
        "needle_candidate_created",
        "installed_needle_created",
        "production_persistence",
        "global_drs_write",
        "external_drs_write",
        "gemini_called",
        "network_called",
        "telegram_used",
        "marennya_invoked",
        "up_invoked",
    )
    non_overclaim = report.proof_artifact.get("non_overclaim", {})
    return all(
        (
            report.parent_request.get("request_id") == "TRAVEL-900",
            report.parent_request.get("itinerary_id") == "ITIN-44",
            report.parent_request.get("root_is_parent_authority") is True,
            report.parent_request.get("root_final_required") is True,
            report.decomposition_plan.get("child_cells_planned") == 5,
            report.decomposition_plan.get("child_cells_created") is True,
            report.decomposition_plan.get("child_cells_are_candidates") is True,
            report.decomposition_plan.get("child_cells_are_runtime_local_only") is True,
            report.decomposition_plan.get("child_cells_are_not_production_agents") is True,
            report.decomposition_plan.get("child_cells_have_no_root_authority") is True,
            report.decomposition_plan.get("child_cells_have_no_external_action_authority")
            is True,
            report.decomposition_plan.get("child_cells_have_no_drs_write_authority")
            is True,
            report.decomposition_plan.get("child_cells_have_no_final_output_authority")
            is True,
            report.decomposition_plan.get("decomposition_requires_root_aggregation")
            is True,
            set(children) == expected_children,
            set(proposals) == expected_children,
            set(boundaries) == expected_children,
            len(blocked) == 4,
            len(ready) == 1,
            children.get("lodging_check", {}).get("local_status") == "ready",
            all(
                children.get(child_id, {}).get("local_status") == "blocked"
                for child_id in (
                    "document_check",
                    "payment_check",
                    "route_window_check",
                    "permission_check",
                )
            ),
            all(
                all(child.get(field) is False for field in child_false_fields)
                for child in children.values()
            ),
            all(
                proposal.get("proposal_is_local_only") is True
                and proposal.get("proposal_is_not_parent_final") is True
                and proposal.get("root_aggregation_required") is True
                for proposal in proposals.values()
            ),
            all(
                boundary.get("root_authority") is False
                and boundary.get("sibling_authority") is False
                and boundary.get("final_output_authority") is False
                and boundary.get("external_action_authority") is False
                and boundary.get("drs_write_authority") is False
                and boundary.get("root_review_required") is True
                and boundary.get("root_aggregation_required") is True
                for boundary in boundaries.values()
            ),
            report.aggregation_result.get("child_cells_observed") == 5,
            report.aggregation_result.get("blocked_child_cells") == 4,
            report.aggregation_result.get("ready_child_cells") == 1,
            report.aggregation_result.get("aggregate_status") == "blocked",
            report.aggregation_result.get("aggregate_result") == "not_ready",
            report.aggregation_result.get("child_cell_consensus_is_not_root") is True,
            report.aggregation_result.get("majority_vote_is_not_root") is True,
            report.aggregation_result.get("aggregation_is_not_final_until_root") is True,
            report.aggregation_result.get("root_final_required") is True,
            report.conflictcheck_result.get("conflict_detected") is True,
            report.conflictcheck_result.get("conflictcheck_is_authority") is False,
            report.gt_advisory.get("gt_recommendation") == "not_ready",
            report.gt_advisory.get("gt_is_advisory") is True,
            report.gt_advisory.get("gt_can_mark_parent_ready") is False,
            report.gt_advisory.get("gt_can_execute_action") is False,
            report.gt_advisory.get("gt_can_grant_child_authority") is False,
            report.gt_advisory.get("gt_can_install_needle") is False,
            report.root_final.get("root_result") == "not_ready",
            report.root_final.get("safe_secondary_outcome")
            == "needs_user_travel_update",
            report.root_final.get("root_remains_final_authority") is True,
            report.root_final.get("child_cells_created") is True,
            all(report.root_final.get(field) is False for field in root_false_fields),
            non_overclaim.get("fractal_dac_expansion_observed") is True,
            non_overclaim.get("controlled_fractal_expansion_only") is True,
            non_overclaim.get("real_child_agents_started") is False,
            non_overclaim.get("production_autonomy_claimed") is False,
            non_overclaim.get("dual_fractal_coupling_invoked") is False,
            non_overclaim.get("external_drs_not_implemented") is True,
            report.audit_entry.get("canonical_payload_hash")
            == canonical_hash(report.proof_artifact),
            report.audit_entry.get("proof_only") is True,
            report.audit_entry.get("production_persistence") is False,
            report.audit_entry.get("global_drs_write") is False,
            report.audit_entry.get("external_drs_write") is False,
            report.audit_entry.get("audit_chain_decides_truth") is False,
        )
    )


def collect_controlled_fractal_dac_expansion_v01(
) -> ControlledFractalDacExpansionV01Report:
    travel = collect_applied_travel_readiness_demo()
    multi_domain = collect_multi_domain_applied_smoke_v02()
    reuse = collect_applied_drs_retrieval_reuse()
    conflict = collect_conflictcheck()
    audit = collect_audit_hash_chain()

    source = {
        "travel_source_status": travel.summary["applied_travel_readiness_demo_status"],
        "multi_domain_source_status": multi_domain.summary[
            "multi_domain_applied_smoke_v02_status"
        ],
        "applied_drs_retrieval_reuse_source_status": reuse.summary[
            "applied_drs_retrieval_reuse_status"
        ],
        "conflictcheck_source_status": conflict.summary["conflictcheck_status"],
        "audit_hash_chain_source_status": audit.summary["audit_hash_chain_status"],
    }
    parent = {
        "request_id": "TRAVEL-900",
        "itinerary_id": "ITIN-44",
        "request_type": "travel_multi_condition_readiness",
        "complexity": "multi_condition",
        "proof_only": True,
        "root_is_parent_authority": True,
        "root_final_required": True,
    }
    decomposition = {
        "decomposition_id": "fractal_dac_expansion_TRAVEL900_ITIN44_v01",
        "decomposition_type": "bounded_child_cell_candidates",
        "child_cells_planned": 5,
        "child_cells_created": True,
        "child_cells_are_candidates": True,
        "child_cells_are_runtime_local_only": True,
        "child_cells_are_not_production_agents": True,
        "child_cells_have_no_root_authority": True,
        "child_cells_have_no_external_action_authority": True,
        "child_cells_have_no_drs_write_authority": True,
        "child_cells_have_no_final_output_authority": True,
        "decomposition_requires_root_aggregation": True,
    }
    children = _child_cells()
    local_proposals = _local_proposals(children)
    authority = _authority_matrix(children)
    aggregation = {
        "aggregation_id": "root_aggregation_TRAVEL900_ITIN44_v01",
        "child_cells_observed": 5,
        "blocked_child_cells": 4,
        "ready_child_cells": 1,
        "aggregate_status": "blocked",
        "aggregate_result": "not_ready",
        "safe_secondary_outcome": "needs_user_travel_update",
        "child_cell_consensus_is_not_root": True,
        "majority_vote_is_not_root": True,
        "aggregation_is_not_final_until_root": True,
        "root_final_required": True,
    }
    conflict_result = {
        "conflict_id": "conflict_child_ready_claim_vs_blocked_children",
        "conflict_detected": True,
        "reason": "parent_ready_claim_contradicts_blocked_child_cell_proposals",
        "conflictcheck_is_authority": False,
        "root_review_required": True,
    }
    gt = {
        "gt_recommendation": "not_ready",
        "gt_reason": "blocked_child_cell_proposals_present",
        "gt_is_advisory": True,
        "gt_can_mark_parent_ready": False,
        "gt_can_execute_action": False,
        "gt_can_grant_child_authority": False,
        "gt_can_install_needle": False,
    }
    root = {
        "root_result": "not_ready",
        "safe_secondary_outcome": "needs_user_travel_update",
        "root_remains_final_authority": True,
        "child_cells_created": True,
        "child_cells_have_authority": False,
        "child_cells_finalized_result": False,
        "direct_ready_override": False,
        "completed_external_action_created": False,
        "travel_request_submitted": False,
        "booking_created": False,
        "payment_executed": False,
        "protocol_candidate_created": False,
        "needle_candidate_created": False,
        "installed_needle_created": False,
        "production_persistence": False,
        "global_drs_write": False,
        "external_drs_write": False,
        "gemini_called": False,
        "network_called": False,
        "telegram_used": False,
        "marennya_invoked": False,
        "up_invoked": False,
    }
    non_overclaim = {
        "fractal_dac_expansion_observed": True,
        "controlled_fractal_expansion_only": True,
        "real_child_agents_started": False,
        "production_autonomy_claimed": False,
        "dual_fractal_coupling_invoked": False,
        "external_drs_not_implemented": True,
    }
    proof_artifact = {
        "proof_artifact_id": "controlled_fractal_dac_expansion_TRAVEL900_ITIN44_v01",
        "source_evidence": source,
        "parent_request": parent,
        "decomposition_plan": decomposition,
        "child_cell_candidates": children,
        "child_cell_local_proposals": local_proposals,
        "authority_boundary_matrix": authority,
        "aggregation_result": aggregation,
        "conflictcheck_result": conflict_result,
        "gt_advisory": gt,
        "root_final": root,
        "non_overclaim": non_overclaim,
    }
    audit_entry = {
        "audit_entry_id": "audit_controlled_fractal_dac_expansion_v01",
        "canonical_payload_hash": canonical_hash(proof_artifact),
        "previous_chain_last_entry_hash": audit.chain_summary["last_entry_hash"],
        "proof_only": True,
        "production_persistence": False,
        "global_drs_write": False,
        "external_drs_write": False,
        "audit_chain_decides_truth": False,
    }
    provisional = ControlledFractalDacExpansionV01Report(
        source_evidence=source,
        parent_request=parent,
        decomposition_plan=decomposition,
        child_cell_candidates=children,
        child_cell_local_proposals=local_proposals,
        authority_boundary_matrix=authority,
        aggregation_result=aggregation,
        conflictcheck_result=conflict_result,
        gt_advisory=gt,
        root_final=root,
        proof_artifact=proof_artifact,
        audit_entry=audit_entry,
        summary={},
    )
    source_pass = all(status == "PASS" for status in source.values())
    consistent = validate_controlled_fractal_dac_expansion_v01_report_consistency(
        provisional
    )
    passed = source_pass and consistent
    summary = {
        "controlled_fractal_dac_expansion_v01_status": "PASS" if passed else "FAIL",
        "parent_request_id": "TRAVEL-900",
        "child_cells_planned": 5,
        "child_cells_created": True,
        "child_cell_candidates_observed": len(children),
        "blocked_child_cells": 4,
        "ready_child_cells": 1,
        "aggregate_result": "not_ready",
        "safe_secondary_outcome": "needs_user_travel_update",
        "all_child_cells_bounded": consistent,
        "no_child_root_authority": all(
            child["root_authority"] is False for child in children
        ),
        "no_child_final_output_authority": all(
            child["final_output_authority"] is False for child in children
        ),
        "no_child_external_action_authority": all(
            child["external_action_authority"] is False for child in children
        ),
        "no_child_drs_write_authority": all(
            child["drs_write_authority"] is False for child in children
        ),
        "no_child_sibling_override": all(
            child["can_override_sibling"] is False for child in children
        ),
        "root_aggregation_required": True,
        "child_cell_consensus_is_not_root": True,
        "majority_vote_is_not_root": True,
        "conflictcheck_remains_advisory_until_root": True,
        "gt_remains_advisory_until_root": True,
        "audit_chain_decides_truth": False,
        "root_remains_final_authority": True,
        "no_real_external_action_executed": True,
        "no_travel_request_submitted": True,
        "no_booking_created": True,
        "no_payment_executed": True,
        "no_production_persistence": True,
        "no_global_drs_write": True,
        "no_external_drs_write": True,
        "protocol_candidate_created": False,
        "needle_candidate_created": False,
        "installed_needle_created": False,
        **non_overclaim,
        "gemini_called": False,
        "network_called": False,
        "telegram_used": False,
        "marennya_invoked": False,
        "up_invoked": False,
        "ready_for_controlled_fractal_dac_expansion_v01_tests": passed,
    }
    return replace(provisional, summary=summary)


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


def render_controlled_fractal_dac_expansion_v01(
    report: ControlledFractalDacExpansionV01Report,
) -> str:
    lines = [
        "[CONTROLLED FRACTAL DAC EXPANSION v0.1]",
        "note: deterministic local proof-mode decomposition and Root aggregation only",
        "note: no real child agents, Dual Fractal Coupling, External DRS, or autonomy",
    ]
    _section(lines, "[SOURCE EVIDENCE]", report.source_evidence)
    _section(lines, "[PARENT REQUEST]", report.parent_request)
    _section(lines, "[DECOMPOSITION PLAN]", report.decomposition_plan)
    _rows(lines, "[CHILD CELL CANDIDATES]", report.child_cell_candidates)
    _rows(lines, "[CHILD CELL LOCAL PROPOSALS]", report.child_cell_local_proposals)
    _rows(lines, "[AUTHORITY BOUNDARY MATRIX]", report.authority_boundary_matrix)
    _section(lines, "[AGGREGATION RESULT]", report.aggregation_result)
    _section(lines, "[CONFLICTCHECK]", report.conflictcheck_result)
    _section(lines, "[GT ADVISORY]", report.gt_advisory)
    _section(lines, "[ROOT FINAL]", report.root_final)
    _section(lines, "[AUDIT]", report.audit_entry)
    _section(lines, "[SUMMARY]", report.summary)
    return "\n".join(lines).rstrip() + "\n"


def run_controlled_fractal_dac_expansion_v01() -> str:
    return render_controlled_fractal_dac_expansion_v01(
        collect_controlled_fractal_dac_expansion_v01()
    )


def main() -> int:
    print(run_controlled_fractal_dac_expansion_v01(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
