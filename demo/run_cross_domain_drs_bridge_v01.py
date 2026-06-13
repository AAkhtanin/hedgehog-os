from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from demo.run_applied_drs_retrieval_reuse import collect_applied_drs_retrieval_reuse
from demo.run_audit_hash_chain import canonical_hash, collect_audit_hash_chain
from demo.run_conflictcheck import collect_conflictcheck
from demo.run_controlled_fractal_dac_expansion_v01 import (
    collect_controlled_fractal_dac_expansion_v01,
)
from demo.run_dual_fractal_coupling_v01 import collect_dual_fractal_coupling_v01
from demo.run_multi_domain_applied_smoke_v02 import collect_multi_domain_applied_smoke_v02


@dataclass(frozen=True)
class CrossDomainDrsBridgeV01Report:
    source_evidence: dict[str, Any]
    bridge_registry: list[dict[str, Any]]
    traversal_request: dict[str, Any]
    traversal_steps: list[dict[str, Any]]
    bridge_boundary_matrix: list[dict[str, Any]]
    traversal_result: dict[str, Any]
    conflictcheck_result: dict[str, Any]
    gt_advisory: dict[str, Any]
    root_final: dict[str, Any]
    proof_artifact: dict[str, Any]
    audit_entry: dict[str, Any]
    summary: dict[str, Any]


def _bridge(
    bridge_id: str,
    source_cell: str,
    target_cell: str,
    semantic_field: str,
    semantic_value: str,
) -> dict[str, Any]:
    return {
        "bridge_id": bridge_id,
        "source_domain": "certificate_parent_dac",
        "source_record": "APP-77/CERT-310",
        "source_cell": source_cell,
        "target_domain": "travel_parent_dac",
        "target_record": "TRAVEL-900/ITIN-44",
        "target_cell": target_cell,
        "semantic_field": semantic_field,
        "semantic_value": semantic_value,
        "bridge_type": "local_cross_domain_semantic_bridge",
        "bridge_status": "active_local_proof_only",
        "external_drs_pointer_created": False,
        "global_drs_write": False,
        "production_persistence": False,
        "transfers_authority": False,
        "transfers_final": False,
        "transfers_execution": False,
        "root_review_required": True,
    }


def _traversal_step(
    traversal_step_id: str,
    bridge_id: str,
    source_evidence: str,
    target_implication: str,
) -> dict[str, Any]:
    return {
        "traversal_step_id": traversal_step_id,
        "bridge_id": bridge_id,
        "source_evidence": source_evidence,
        "target_implication": target_implication,
        "local_effect": "inform_target_check",
        "marks_target_parent_ready": False,
        "finalizes_target_parent": False,
        "executes_external_action": False,
        "writes_global_drs": False,
        "writes_external_drs": False,
    }


def validate_cross_domain_drs_bridge_v01_report_consistency(
    report: CrossDomainDrsBridgeV01Report,
) -> bool:
    bridges = {row["bridge_id"]: row for row in report.bridge_registry}
    steps = {row["traversal_step_id"]: row for row in report.traversal_steps}
    boundaries = {
        row["bridge_id"]: row for row in report.bridge_boundary_matrix
    }
    expected_bridges = {
        "bridge_certificate_insurance_to_travel_document_v01",
        "bridge_certificate_payment_to_travel_payment_v01",
    }
    expected_steps = {
        "step_insurance_certificate_expired",
        "step_payment_receipt_missing",
    }
    bridge_false_fields = (
        "external_drs_pointer_created",
        "global_drs_write",
        "production_persistence",
        "transfers_authority",
        "transfers_final",
        "transfers_execution",
    )
    step_false_fields = (
        "marks_target_parent_ready",
        "finalizes_target_parent",
        "executes_external_action",
        "writes_global_drs",
        "writes_external_drs",
    )
    boundary_false_fields = (
        "bridge_can_decide",
        "bridge_transfers_authority",
        "bridge_transfers_root",
        "bridge_transfers_final",
        "bridge_transfers_execution",
        "bridge_transfers_drs_write",
        "source_domain_can_finalize_target",
        "target_domain_can_finalize_source",
    )
    root_false_fields = (
        "drs_bridge_decided_target",
        "traversal_finalized_target",
        "bridge_transferred_authority",
        "bridge_transferred_execution",
        "bridge_transferred_drs_write",
        "external_drs_pointer_created",
        "global_drs_write",
        "external_drs_write",
        "production_persistence",
        "completed_external_action_created",
        "travel_request_submitted",
        "booking_created",
        "payment_executed",
        "certificate_request_submitted",
        "protocol_candidate_created",
        "needle_candidate_created",
        "installed_needle_created",
        "gemini_called",
        "network_called",
        "telegram_used",
        "marennya_invoked",
        "up_invoked",
    )
    non_overclaim = report.proof_artifact.get("non_overclaim", {})
    return all(
        (
            set(bridges) == expected_bridges,
            all(
                bridge.get("source_domain") == "certificate_parent_dac"
                and bridge.get("target_domain") == "travel_parent_dac"
                and bridge.get("bridge_type") == "local_cross_domain_semantic_bridge"
                and bridge.get("bridge_status") == "active_local_proof_only"
                and bridge.get("root_review_required") is True
                and all(bridge.get(field) is False for field in bridge_false_fields)
                for bridge in bridges.values()
            ),
            report.traversal_request.get("requested_by") == "Root",
            report.traversal_request.get("root_authorized_traversal") is True,
            report.traversal_request.get("traversal_is_local_proof_only") is True,
            report.traversal_request.get("external_drs_not_implemented") is True,
            report.traversal_request.get("traversal_can_inform") is True,
            all(
                report.traversal_request.get(field) is False
                for field in (
                    "traversal_can_decide",
                    "traversal_can_execute",
                    "traversal_can_finalize",
                )
            ),
            set(steps) == expected_steps,
            all(
                step.get("bridge_id") in bridges
                and step.get("local_effect") == "inform_target_check"
                and all(step.get(field) is False for field in step_false_fields)
                for step in steps.values()
            ),
            set(boundaries) == expected_bridges,
            all(
                boundary.get("bridge_can_inform") is True
                and boundary.get("root_review_required") is True
                and boundary.get("root_final_required") is True
                and all(
                    boundary.get(field) is False for field in boundary_false_fields
                )
                for boundary in boundaries.values()
            ),
            report.traversal_result.get("traversal_status") == "completed_local_proof",
            report.traversal_result.get("bridges_traversed") == 2,
            report.traversal_result.get("traversal_steps_observed") == 2,
            report.traversal_result.get("target_domain_informed") is True,
            report.traversal_result.get("target_domain_decided_by_traversal") is False,
            report.traversal_result.get("target_parent_finalized_by_traversal")
            is False,
            report.traversal_result.get("target_parent_ready_after_traversal") is False,
            report.traversal_result.get("target_parent_result_after_root_review")
            == "not_ready",
            report.traversal_result.get("drs_bridge_is_not_authority") is True,
            report.traversal_result.get("traversal_trace_is_not_truth") is True,
            report.traversal_result.get("root_review_required") is True,
            report.traversal_result.get("root_final_required") is True,
            report.conflictcheck_result.get("conflict_detected") is True,
            report.conflictcheck_result.get("conflictcheck_is_authority") is False,
            report.gt_advisory.get("gt_recommendation") == "target_parent_not_ready",
            report.gt_advisory.get("gt_is_advisory") is True,
            all(
                report.gt_advisory.get(field) is False
                for field in (
                    "gt_can_mark_target_ready",
                    "gt_can_execute_action",
                    "gt_can_grant_bridge_authority",
                    "gt_can_create_external_drs_pointer",
                    "gt_can_install_needle",
                )
            ),
            report.root_final.get("root_result") == "not_ready",
            report.root_final.get("safe_secondary_outcome")
            == "needs_user_travel_update",
            report.root_final.get("root_remains_final_authority") is True,
            report.root_final.get("drs_bridge_traversal_completed") is True,
            report.root_final.get("drs_bridge_informed_target") is True,
            all(report.root_final.get(field) is False for field in root_false_fields),
            non_overclaim.get("cross_domain_drs_traversal_observed") is True,
            non_overclaim.get("local_drs_bridge_proof_only") is True,
            non_overclaim.get("external_drs_implemented") is False,
            non_overclaim.get("external_drs_pointer_protocol_only") is False,
            non_overclaim.get("global_semantic_fabric_claimed") is False,
            non_overclaim.get("production_autonomy_claimed") is False,
            non_overclaim.get("real_connector_used") is False,
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


def collect_cross_domain_drs_bridge_v01() -> CrossDomainDrsBridgeV01Report:
    dual = collect_dual_fractal_coupling_v01()
    controlled = collect_controlled_fractal_dac_expansion_v01()
    multi_domain = collect_multi_domain_applied_smoke_v02()
    reuse = collect_applied_drs_retrieval_reuse()
    conflict = collect_conflictcheck()
    audit = collect_audit_hash_chain()

    source = {
        "dual_fractal_coupling_source_status": dual.summary[
            "dual_fractal_coupling_v01_status"
        ],
        "controlled_fractal_dac_source_status": controlled.summary[
            "controlled_fractal_dac_expansion_v01_status"
        ],
        "multi_domain_source_status": multi_domain.summary[
            "multi_domain_applied_smoke_v02_status"
        ],
        "applied_drs_retrieval_reuse_source_status": reuse.summary[
            "applied_drs_retrieval_reuse_status"
        ],
        "conflictcheck_source_status": conflict.summary["conflictcheck_status"],
        "audit_hash_chain_source_status": audit.summary["audit_hash_chain_status"],
    }
    bridges = [
        _bridge(
            "bridge_certificate_insurance_to_travel_document_v01",
            "certificate_insurance_check",
            "travel_document_check",
            "insurance_certificate",
            "expired",
        ),
        _bridge(
            "bridge_certificate_payment_to_travel_payment_v01",
            "certificate_payment_receipt_check",
            "travel_payment_check",
            "payment_receipt",
            "missing",
        ),
    ]
    traversal_request = {
        "traversal_id": "drs_traversal_certificate_to_travel_TRAVEL900_v01",
        "source_domain": "certificate_parent_dac",
        "target_domain": "travel_parent_dac",
        "traversal_goal": "inform_travel_readiness_checks",
        "requested_by": "Root",
        "root_authorized_traversal": True,
        "traversal_is_local_proof_only": True,
        "external_drs_not_implemented": True,
        "traversal_can_inform": True,
        "traversal_can_decide": False,
        "traversal_can_execute": False,
        "traversal_can_finalize": False,
    }
    steps = [
        _traversal_step(
            "step_insurance_certificate_expired",
            "bridge_certificate_insurance_to_travel_document_v01",
            "insurance_certificate:expired",
            "travel_document_check_blocked",
        ),
        _traversal_step(
            "step_payment_receipt_missing",
            "bridge_certificate_payment_to_travel_payment_v01",
            "payment_receipt:missing",
            "travel_payment_check_blocked",
        ),
    ]
    boundaries = [
        {
            "bridge_id": bridge["bridge_id"],
            "bridge_can_inform": True,
            "bridge_can_decide": False,
            "bridge_transfers_authority": False,
            "bridge_transfers_root": False,
            "bridge_transfers_final": False,
            "bridge_transfers_execution": False,
            "bridge_transfers_drs_write": False,
            "source_domain_can_finalize_target": False,
            "target_domain_can_finalize_source": False,
            "root_review_required": True,
            "root_final_required": True,
        }
        for bridge in bridges
    ]
    traversal_result = {
        "traversal_status": "completed_local_proof",
        "bridges_traversed": 2,
        "traversal_steps_observed": 2,
        "target_domain_informed": True,
        "target_domain_decided_by_traversal": False,
        "target_parent_finalized_by_traversal": False,
        "target_parent_ready_after_traversal": False,
        "target_parent_result_after_root_review": "not_ready",
        "safe_secondary_outcome": "needs_user_travel_update",
        "drs_bridge_is_not_authority": True,
        "traversal_trace_is_not_truth": True,
        "root_review_required": True,
        "root_final_required": True,
    }
    conflict_result = {
        "conflict_id": "conflict_drs_bridge_authority_escalation_attempt",
        "conflict_detected": True,
        "reason": (
            "drs_bridge_traversal_cannot_transfer_authority_or_finalize_target_parent"
        ),
        "conflictcheck_is_authority": False,
        "root_review_required": True,
    }
    gt = {
        "gt_recommendation": "target_parent_not_ready",
        "gt_reason": "traversal_informs_blocked_travel_checks_but_cannot_finalize",
        "gt_is_advisory": True,
        "gt_can_mark_target_ready": False,
        "gt_can_execute_action": False,
        "gt_can_grant_bridge_authority": False,
        "gt_can_create_external_drs_pointer": False,
        "gt_can_install_needle": False,
    }
    root = {
        "root_result": "not_ready",
        "safe_secondary_outcome": "needs_user_travel_update",
        "root_remains_final_authority": True,
        "drs_bridge_traversal_completed": True,
        "drs_bridge_informed_target": True,
        "drs_bridge_decided_target": False,
        "traversal_finalized_target": False,
        "bridge_transferred_authority": False,
        "bridge_transferred_execution": False,
        "bridge_transferred_drs_write": False,
        "external_drs_pointer_created": False,
        "global_drs_write": False,
        "external_drs_write": False,
        "production_persistence": False,
        "completed_external_action_created": False,
        "travel_request_submitted": False,
        "booking_created": False,
        "payment_executed": False,
        "certificate_request_submitted": False,
        "protocol_candidate_created": False,
        "needle_candidate_created": False,
        "installed_needle_created": False,
        "gemini_called": False,
        "network_called": False,
        "telegram_used": False,
        "marennya_invoked": False,
        "up_invoked": False,
    }
    non_overclaim = {
        "cross_domain_drs_traversal_observed": True,
        "local_drs_bridge_proof_only": True,
        "external_drs_implemented": False,
        "external_drs_pointer_protocol_only": False,
        "global_semantic_fabric_claimed": False,
        "production_autonomy_claimed": False,
        "real_connector_used": False,
        "gemini_called": False,
        "network_called": False,
    }
    proof_artifact = {
        "proof_artifact_id": "cross_domain_drs_bridge_v01",
        "source_evidence": source,
        "bridge_registry": bridges,
        "traversal_request": traversal_request,
        "traversal_steps": steps,
        "bridge_boundary_matrix": boundaries,
        "traversal_result": traversal_result,
        "conflictcheck_result": conflict_result,
        "gt_advisory": gt,
        "root_final": root,
        "non_overclaim": non_overclaim,
    }
    audit_entry = {
        "audit_entry_id": "audit_cross_domain_drs_bridge_v01",
        "canonical_payload_hash": canonical_hash(proof_artifact),
        "previous_chain_last_entry_hash": audit.chain_summary["last_entry_hash"],
        "proof_only": True,
        "production_persistence": False,
        "global_drs_write": False,
        "external_drs_write": False,
        "audit_chain_decides_truth": False,
    }
    provisional = CrossDomainDrsBridgeV01Report(
        source,
        bridges,
        traversal_request,
        steps,
        boundaries,
        traversal_result,
        conflict_result,
        gt,
        root,
        proof_artifact,
        audit_entry,
        {},
    )
    source_pass = all(status == "PASS" for status in source.values())
    consistent = validate_cross_domain_drs_bridge_v01_report_consistency(provisional)
    passed = source_pass and consistent
    summary = {
        "cross_domain_drs_bridge_v01_status": "PASS" if passed else "FAIL",
        "bridge_records_observed": len(bridges),
        "traversal_steps_observed": len(steps),
        "source_domain": "certificate_parent_dac",
        "target_domain": "travel_parent_dac",
        "target_domain_informed": True,
        "target_domain_decided_by_traversal": False,
        "target_parent_finalized_by_traversal": False,
        "target_parent_result_after_root_review": "not_ready",
        "safe_secondary_outcome": "needs_user_travel_update",
        "bridge_can_inform": True,
        "bridge_can_decide": False,
        "no_bridge_authority_transfer": True,
        "no_bridge_root_transfer": True,
        "no_bridge_final_transfer": True,
        "no_bridge_execution_transfer": True,
        "no_bridge_drs_write_transfer": True,
        "drs_bridge_is_not_authority": True,
        "traversal_trace_is_not_truth": True,
        "root_review_required": True,
        "root_final_required": True,
        "gt_remains_advisory_until_root": True,
        "conflictcheck_remains_advisory_until_root": True,
        "audit_chain_decides_truth": False,
        "root_remains_final_authority": True,
        "no_real_external_action_executed": True,
        "no_travel_request_submitted": True,
        "no_certificate_request_submitted": True,
        "no_booking_created": True,
        "no_payment_executed": True,
        "no_production_persistence": True,
        "no_global_drs_write": True,
        "no_external_drs_write": True,
        "external_drs_implemented": False,
        "external_drs_pointer_created": False,
        "global_semantic_fabric_claimed": False,
        "protocol_candidate_created": False,
        "needle_candidate_created": False,
        "installed_needle_created": False,
        "real_connector_used": False,
        "gemini_called": False,
        "network_called": False,
        "telegram_used": False,
        "marennya_invoked": False,
        "up_invoked": False,
        "ready_for_cross_domain_drs_bridge_v01_tests": passed,
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


def render_cross_domain_drs_bridge_v01(report: CrossDomainDrsBridgeV01Report) -> str:
    lines = [
        "[CROSS-DOMAIN DRS BRIDGE v0.1]",
        "note: deterministic local DRS bridge traversal proof only",
        "note: traversal informs Root review but transfers no authority or finalization",
    ]
    _section(lines, "[SOURCE EVIDENCE]", report.source_evidence)
    _rows(lines, "[BRIDGE REGISTRY]", report.bridge_registry)
    _section(lines, "[TRAVERSAL REQUEST]", report.traversal_request)
    _rows(lines, "[TRAVERSAL STEPS]", report.traversal_steps)
    _rows(lines, "[BRIDGE BOUNDARY MATRIX]", report.bridge_boundary_matrix)
    _section(lines, "[TRAVERSAL RESULT]", report.traversal_result)
    _section(lines, "[CONFLICTCHECK]", report.conflictcheck_result)
    _section(lines, "[GT ADVISORY]", report.gt_advisory)
    _section(lines, "[ROOT FINAL]", report.root_final)
    _section(lines, "[AUDIT]", report.audit_entry)
    _section(lines, "[SUMMARY]", report.summary)
    return "\n".join(lines).rstrip() + "\n"


def run_cross_domain_drs_bridge_v01() -> str:
    return render_cross_domain_drs_bridge_v01(collect_cross_domain_drs_bridge_v01())


def main() -> int:
    print(run_cross_domain_drs_bridge_v01(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
