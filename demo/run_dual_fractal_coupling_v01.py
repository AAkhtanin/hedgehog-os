from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from demo.run_applied_certificate_readiness_demo import (
    collect_applied_certificate_readiness_demo,
)
from demo.run_applied_drs_retrieval_reuse import collect_applied_drs_retrieval_reuse
from demo.run_applied_travel_readiness_demo import collect_applied_travel_readiness_demo
from demo.run_audit_hash_chain import canonical_hash, collect_audit_hash_chain
from demo.run_conflictcheck import collect_conflictcheck
from demo.run_controlled_fractal_dac_expansion_v01 import (
    collect_controlled_fractal_dac_expansion_v01,
)
from demo.run_multi_domain_applied_smoke_v02 import collect_multi_domain_applied_smoke_v02


@dataclass(frozen=True)
class DualFractalCouplingV01Report:
    source_evidence: dict[str, Any]
    parent_dac_matrix: list[dict[str, Any]]
    local_cell_matrix: list[dict[str, Any]]
    coupling_edges: list[dict[str, Any]]
    coupling_boundary_matrix: list[dict[str, Any]]
    interlock_observation: dict[str, Any]
    conflictcheck_result: dict[str, Any]
    gt_advisory: dict[str, Any]
    root_final_matrix: list[dict[str, Any]]
    proof_artifact: dict[str, Any]
    audit_entry: dict[str, Any]
    summary: dict[str, Any]


def _local_cell(
    parent_dac_id: str,
    cell_id: str,
    status: str,
    evidence: str,
    proposal: str,
) -> dict[str, Any]:
    return {
        "parent_dac_id": parent_dac_id,
        "cell_id": cell_id,
        "local_status": status,
        "input_evidence": evidence,
        "local_proposal": proposal,
        "local_only": True,
        "root_authority": False,
        "parent_final_authority": False,
        "sibling_authority": False,
        "cross_parent_authority": False,
        "external_action_authority": False,
        "drs_write_authority": False,
        "can_mark_own_parent_ready": False,
        "can_mark_other_parent_ready": False,
        "can_override_coupled_cell": False,
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


def _root_final(parent_dac_id: str, secondary: str) -> dict[str, Any]:
    final = {
        "parent_dac_id": parent_dac_id,
        "root_result": "not_ready",
        "safe_secondary_outcome": secondary,
        "root_remains_final_authority": True,
        "coupled_parent_finalized_this_parent": False,
        "child_cells_finalized_result": False,
        "coupling_edges_transferred_authority": False,
        "completed_external_action_created": False,
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
    if parent_dac_id == "certificate_parent_dac":
        final["certificate_request_submitted"] = False
    else:
        final.update(
            {
                "travel_request_submitted": False,
                "booking_created": False,
                "payment_executed": False,
            }
        )
    return final


def validate_dual_fractal_coupling_v01_report_consistency(
    report: DualFractalCouplingV01Report,
) -> bool:
    parents = {row["parent_dac_id"]: row for row in report.parent_dac_matrix}
    cells = {row["cell_id"]: row for row in report.local_cell_matrix}
    edges = {row["coupling_edge_id"]: row for row in report.coupling_edges}
    boundaries = {
        row["coupling_edge_id"]: row for row in report.coupling_boundary_matrix
    }
    finals = {row["parent_dac_id"]: row for row in report.root_final_matrix}
    expected_cells = {
        "certificate_insurance_check",
        "certificate_payment_receipt_check",
        "certificate_submission_permission_check",
        "travel_document_check",
        "travel_payment_check",
        "travel_lodging_check",
        "travel_route_window_check",
        "travel_permission_check",
    }
    cell_false_fields = (
        "root_authority",
        "parent_final_authority",
        "sibling_authority",
        "cross_parent_authority",
        "external_action_authority",
        "drs_write_authority",
        "can_mark_own_parent_ready",
        "can_mark_other_parent_ready",
        "can_override_coupled_cell",
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
    final_false_fields = (
        "coupled_parent_finalized_this_parent",
        "child_cells_finalized_result",
        "coupling_edges_transferred_authority",
        "completed_external_action_created",
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
            len(parents) == 2,
            all(parent.get("root_result") == "not_ready" for parent in parents.values()),
            parents.get("certificate_parent_dac", {}).get("child_cells_count") == 3,
            parents.get("travel_parent_dac", {}).get("child_cells_count") == 5,
            all(
                parent.get("parent_root_authority") is True
                and parent.get("parent_final_required") is True
                and parent.get("external_action_executed") is False
                for parent in parents.values()
            ),
            set(cells) == expected_cells,
            all(cell.get("local_only") is True for cell in cells.values()),
            all(
                all(cell.get(field) is False for field in cell_false_fields)
                for cell in cells.values()
            ),
            len(edges) == 2,
            all(
                edge.get("coupling_type") == "bounded_semantic_resonance"
                and edge.get("transfers_authority") is False
                and edge.get("transfers_final") is False
                and edge.get("transfers_execution") is False
                and edge.get("requires_root_review") is True
                for edge in edges.values()
            ),
            set(boundaries) == set(edges),
            all(
                boundary.get("semantic_resonance_observed") is True
                and boundary.get("shared_evidence_can_inform") is True
                and boundary.get("shared_evidence_can_decide") is False
                and boundary.get("coupling_transfers_authority") is False
                and boundary.get("coupling_transfers_root") is False
                and boundary.get("coupling_transfers_execution") is False
                and boundary.get("coupling_transfers_drs_write") is False
                and boundary.get("coupled_cell_can_override_target") is False
                and boundary.get("source_parent_can_finalize_target_parent") is False
                and boundary.get("target_parent_can_finalize_source_parent") is False
                and boundary.get("root_review_required") is True
                for boundary in boundaries.values()
            ),
            report.interlock_observation.get("interlock_observed") is True,
            report.interlock_observation.get("coupled_parents") == 2,
            report.interlock_observation.get("coupling_edges_observed") == 2,
            report.interlock_observation.get("shared_evidence_is_not_authority") is True,
            report.interlock_observation.get("root_required_to_resolve_interlock") is True,
            report.conflictcheck_result.get("conflict_detected") is True,
            report.conflictcheck_result.get("conflictcheck_is_authority") is False,
            report.gt_advisory.get("gt_recommendation") == "dual_parent_not_ready",
            report.gt_advisory.get("gt_is_advisory") is True,
            all(
                report.gt_advisory.get(field) is False
                for field in (
                    "gt_can_merge_parent_authority",
                    "gt_can_mark_certificate_ready",
                    "gt_can_mark_travel_ready",
                    "gt_can_execute_action",
                    "gt_can_grant_cross_parent_authority",
                    "gt_can_install_needle",
                )
            ),
            len(finals) == 2,
            all(
                final.get("root_result") == "not_ready"
                and final.get("root_remains_final_authority") is True
                and all(final.get(field) is False for field in final_false_fields)
                for final in finals.values()
            ),
            finals.get("certificate_parent_dac", {}).get(
                "certificate_request_submitted"
            )
            is False,
            all(
                finals.get("travel_parent_dac", {}).get(field) is False
                for field in (
                    "travel_request_submitted",
                    "booking_created",
                    "payment_executed",
                )
            ),
            non_overclaim.get("dual_fractal_coupling_observed") is True,
            non_overclaim.get("controlled_interlock_only") is True,
            non_overclaim.get("real_child_agents_started") is False,
            non_overclaim.get("production_autonomy_claimed") is False,
            non_overclaim.get("external_drs_not_implemented") is True,
            non_overclaim.get("gemini_called") is False,
            non_overclaim.get("network_called") is False,
            report.audit_entry.get("canonical_payload_hash")
            == canonical_hash(report.proof_artifact),
            report.audit_entry.get("proof_only") is True,
            report.audit_entry.get("production_persistence") is False,
            report.audit_entry.get("global_drs_write") is False,
            report.audit_entry.get("external_drs_write") is False,
            report.audit_entry.get("audit_chain_decides_truth") is False,
        )
    )


def collect_dual_fractal_coupling_v01() -> DualFractalCouplingV01Report:
    controlled = collect_controlled_fractal_dac_expansion_v01()
    multi_domain = collect_multi_domain_applied_smoke_v02()
    certificate = collect_applied_certificate_readiness_demo()
    travel = collect_applied_travel_readiness_demo()
    reuse = collect_applied_drs_retrieval_reuse()
    conflict = collect_conflictcheck()
    audit = collect_audit_hash_chain()

    source = {
        "controlled_fractal_dac_source_status": controlled.summary[
            "controlled_fractal_dac_expansion_v01_status"
        ],
        "multi_domain_source_status": multi_domain.summary[
            "multi_domain_applied_smoke_v02_status"
        ],
        "certificate_source_status": certificate.summary[
            "applied_certificate_readiness_demo_status"
        ],
        "travel_source_status": travel.summary["applied_travel_readiness_demo_status"],
        "applied_drs_retrieval_reuse_source_status": reuse.summary[
            "applied_drs_retrieval_reuse_status"
        ],
        "conflictcheck_source_status": conflict.summary["conflictcheck_status"],
        "audit_hash_chain_source_status": audit.summary["audit_hash_chain_status"],
    }
    parents = [
        {
            "parent_dac_id": "certificate_parent_dac",
            "scenario_id": "APP-77/CERT-310",
            "parent_type": "certificate_readiness",
            "root_result": "not_ready",
            "safe_secondary_outcome": "needs_user_document_update",
            "parent_root_authority": True,
            "child_cells_count": 3,
            "parent_final_required": True,
            "external_action_executed": False,
        },
        {
            "parent_dac_id": "travel_parent_dac",
            "scenario_id": "TRAVEL-900/ITIN-44",
            "parent_type": "travel_multi_condition_readiness",
            "root_result": "not_ready",
            "safe_secondary_outcome": "needs_user_travel_update",
            "parent_root_authority": True,
            "child_cells_count": 5,
            "parent_final_required": True,
            "external_action_executed": False,
        },
    ]
    cells = [
        _local_cell(
            "certificate_parent_dac",
            "certificate_insurance_check",
            "blocked",
            "insurance_certificate:expired",
            "needs_document_update",
        ),
        _local_cell(
            "certificate_parent_dac",
            "certificate_payment_receipt_check",
            "blocked",
            "payment_receipt:missing",
            "needs_payment_receipt",
        ),
        _local_cell(
            "certificate_parent_dac",
            "certificate_submission_permission_check",
            "blocked",
            "permission:not_confirmed_or_not_available",
            "needs_user_permission_or_hold",
        ),
        _local_cell(
            "travel_parent_dac",
            "travel_document_check",
            "blocked",
            "insurance_certificate:expired",
            "needs_document_update",
        ),
        _local_cell(
            "travel_parent_dac",
            "travel_payment_check",
            "blocked",
            "payment_receipt:missing",
            "needs_payment_receipt",
        ),
        _local_cell(
            "travel_parent_dac",
            "travel_lodging_check",
            "ready",
            "hotel_confirmation:present",
            "lodging_ok",
        ),
        _local_cell(
            "travel_parent_dac",
            "travel_route_window_check",
            "blocked",
            "route_window:uncertain",
            "needs_route_window_confirmation",
        ),
        _local_cell(
            "travel_parent_dac",
            "travel_permission_check",
            "blocked",
            "user_permission:not_confirmed",
            "needs_user_permission",
        ),
    ]
    edges = [
        {
            "coupling_edge_id": "certificate_insurance_to_travel_document",
            "from_parent": "certificate_parent_dac",
            "from_cell": "certificate_insurance_check",
            "to_parent": "travel_parent_dac",
            "to_cell": "travel_document_check",
            "shared_semantic_field": "insurance_certificate",
            "shared_evidence": "expired",
            "coupling_type": "bounded_semantic_resonance",
            "transfers_authority": False,
            "transfers_final": False,
            "transfers_execution": False,
            "requires_root_review": True,
        },
        {
            "coupling_edge_id": "certificate_payment_to_travel_payment",
            "from_parent": "certificate_parent_dac",
            "from_cell": "certificate_payment_receipt_check",
            "to_parent": "travel_parent_dac",
            "to_cell": "travel_payment_check",
            "shared_semantic_field": "payment_receipt",
            "shared_evidence": "missing",
            "coupling_type": "bounded_semantic_resonance",
            "transfers_authority": False,
            "transfers_final": False,
            "transfers_execution": False,
            "requires_root_review": True,
        },
    ]
    boundaries = [
        {
            "coupling_edge_id": edge["coupling_edge_id"],
            "semantic_resonance_observed": True,
            "shared_evidence_can_inform": True,
            "shared_evidence_can_decide": False,
            "coupling_transfers_authority": False,
            "coupling_transfers_root": False,
            "coupling_transfers_execution": False,
            "coupling_transfers_drs_write": False,
            "coupled_cell_can_override_target": False,
            "source_parent_can_finalize_target_parent": False,
            "target_parent_can_finalize_source_parent": False,
            "root_review_required": True,
        }
        for edge in edges
    ]
    interlock = {
        "interlock_observed": True,
        "coupled_parents": 2,
        "coupling_edges_observed": 2,
        "certificate_to_travel_reuse_observed": True,
        "travel_to_certificate_authority_allowed": False,
        "certificate_to_travel_authority_allowed": False,
        "shared_evidence_is_not_authority": True,
        "semantic_similarity_is_not_authority": True,
        "reuse_score_is_not_root": True,
        "drs_retrieval_is_not_authority": True,
        "root_required_to_resolve_interlock": True,
    }
    conflict_result = {
        "conflict_id": "conflict_dual_fractal_coupling_authority_leak_attempt",
        "conflict_detected": True,
        "reason": "coupling_edge_cannot_transfer_authority_or_parent_finalization",
        "conflictcheck_is_authority": False,
        "root_review_required": True,
    }
    gt = {
        "gt_recommendation": "dual_parent_not_ready",
        "gt_reason": "blocked_cells_in_both_parent_dacs",
        "gt_is_advisory": True,
        "gt_can_merge_parent_authority": False,
        "gt_can_mark_certificate_ready": False,
        "gt_can_mark_travel_ready": False,
        "gt_can_execute_action": False,
        "gt_can_grant_cross_parent_authority": False,
        "gt_can_install_needle": False,
    }
    finals = [
        _root_final("certificate_parent_dac", "needs_user_document_update"),
        _root_final("travel_parent_dac", "needs_user_travel_update"),
    ]
    non_overclaim = {
        "dual_fractal_coupling_observed": True,
        "controlled_interlock_only": True,
        "real_child_agents_started": False,
        "production_autonomy_claimed": False,
        "external_drs_not_implemented": True,
        "gemini_called": False,
        "network_called": False,
    }
    proof_artifact = {
        "proof_artifact_id": "dual_fractal_coupling_v01",
        "source_evidence": source,
        "parent_dac_matrix": parents,
        "local_cell_matrix": cells,
        "coupling_edges": edges,
        "coupling_boundary_matrix": boundaries,
        "interlock_observation": interlock,
        "conflictcheck_result": conflict_result,
        "gt_advisory": gt,
        "root_final_matrix": finals,
        "non_overclaim": non_overclaim,
    }
    audit_entry = {
        "audit_entry_id": "audit_dual_fractal_coupling_v01",
        "canonical_payload_hash": canonical_hash(proof_artifact),
        "previous_chain_last_entry_hash": audit.chain_summary["last_entry_hash"],
        "proof_only": True,
        "production_persistence": False,
        "global_drs_write": False,
        "external_drs_write": False,
        "audit_chain_decides_truth": False,
    }
    provisional = DualFractalCouplingV01Report(
        source,
        parents,
        cells,
        edges,
        boundaries,
        interlock,
        conflict_result,
        gt,
        finals,
        proof_artifact,
        audit_entry,
        {},
    )
    source_pass = all(status == "PASS" for status in source.values())
    consistent = validate_dual_fractal_coupling_v01_report_consistency(provisional)
    passed = source_pass and consistent
    summary = {
        "dual_fractal_coupling_v01_status": "PASS" if passed else "FAIL",
        "coupled_parent_dacs": len(parents),
        "total_local_cells": len(cells),
        "coupling_edges_observed": len(edges),
        "interlock_observed": True,
        "certificate_root_result": "not_ready",
        "travel_root_result": "not_ready",
        "certificate_safe_secondary_outcome": "needs_user_document_update",
        "travel_safe_secondary_outcome": "needs_user_travel_update",
        "shared_evidence_can_inform": True,
        "shared_evidence_can_decide": False,
        "no_cross_parent_authority": True,
        "no_coupling_authority_transfer": True,
        "no_coupling_execution_transfer": True,
        "no_coupling_drs_write_transfer": True,
        "no_coupled_parent_cross_finalization": True,
        "all_local_cells_bounded": consistent,
        "no_child_root_authority": True,
        "no_child_parent_final_authority": True,
        "no_child_cross_parent_authority": True,
        "no_child_external_action_authority": True,
        "no_child_drs_write_authority": True,
        "root_required_to_resolve_interlock": True,
        "gt_remains_advisory_until_root": True,
        "conflictcheck_remains_advisory_until_root": True,
        "audit_chain_decides_truth": False,
        "root_remains_final_authority": True,
        "no_real_external_action_executed": True,
        "no_certificate_request_submitted": True,
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
        "telegram_used": False,
        "marennya_invoked": False,
        "up_invoked": False,
        "ready_for_dual_fractal_coupling_v01_tests": passed,
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


def render_dual_fractal_coupling_v01(report: DualFractalCouplingV01Report) -> str:
    lines = [
        "[DUAL FRACTAL COUPLING v0.1]",
        "note: deterministic local proof-mode semantic interlock only",
        "note: coupling informs but transfers no authority, finalization, or execution",
    ]
    _section(lines, "[SOURCE EVIDENCE]", report.source_evidence)
    _rows(lines, "[PARENT DAC MATRIX]", report.parent_dac_matrix)
    _rows(lines, "[LOCAL CELL MATRIX]", report.local_cell_matrix)
    _rows(lines, "[COUPLING EDGES]", report.coupling_edges)
    _rows(lines, "[COUPLING BOUNDARY MATRIX]", report.coupling_boundary_matrix)
    _section(lines, "[INTERLOCK OBSERVATION]", report.interlock_observation)
    _section(lines, "[CONFLICTCHECK]", report.conflictcheck_result)
    _section(lines, "[GT ADVISORY]", report.gt_advisory)
    _rows(lines, "[ROOT FINAL MATRIX]", report.root_final_matrix)
    _section(lines, "[AUDIT]", report.audit_entry)
    _section(lines, "[SUMMARY]", report.summary)
    return "\n".join(lines).rstrip() + "\n"


def run_dual_fractal_coupling_v01() -> str:
    return render_dual_fractal_coupling_v01(collect_dual_fractal_coupling_v01())


def main() -> int:
    print(run_dual_fractal_coupling_v01(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
