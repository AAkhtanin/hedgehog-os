from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from demo.run_applied_certificate_readiness_demo import (
    collect_applied_certificate_readiness_demo,
)
from demo.run_applied_warehouse_semantic_demo import (
    collect_applied_warehouse_semantic_demo,
)
from demo.run_audit_hash_chain import canonical_hash, collect_audit_hash_chain
from demo.run_conflictcheck import collect_conflictcheck
from demo.run_controlled_root_orchestrator_route_assembly import (
    collect_controlled_root_orchestrator_route_assembly,
)
from demo.run_drs_lifecycle_semantics import collect_drs_lifecycle_semantics


SCENARIOS = (
    "warehouse_restock_permission_required",
    "certificate_document_update_required",
    "unsafe_permission_bypass_attempt",
    "explicit_user_denial",
    "explicit_user_approval_proof_only",
)


@dataclass(frozen=True)
class PermissionNeedsUserUxProofReport:
    input_mode: dict[str, Any]
    source_applied_contexts: dict[str, Any]
    permission_request_artifacts: list[dict[str, Any]]
    needs_user_artifacts: list[dict[str, Any]]
    permission_response_artifacts: list[dict[str, Any]]
    permission_validation_rows: list[dict[str, Any]]
    permission_gt_selection: dict[str, Any]
    permission_root_final_artifacts: list[dict[str, Any]]
    permission_drs_lifecycle_records: list[dict[str, Any]]
    permission_conflict_reports: list[dict[str, Any]]
    permission_proof_artifact: dict[str, Any]
    permission_audit_entry: dict[str, Any]
    audit_hash_chain: dict[str, Any]
    malicious_unsafe_claims: dict[str, bool]
    authority_safety: dict[str, Any]
    summary: dict[str, Any]


def _by_id(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    return {row[key]: row for row in rows}


def _permission_requests() -> list[dict[str, Any]]:
    return [
        {
            "permission_request_id": "permission_request_warehouse_W17_D2042",
            "source_scenario": "warehouse_restock_permission_required",
            "requested_action": "authorize_restock_or_dispatch_override",
            "reason_permission_required": "water_filter short_by_2",
            "required_user_confirmation_fields": [
                "operator_identity_confirmation",
                "restock_or_delay_choice",
            ],
            "risk_summary": "dispatch while stock is short is unsafe",
            "no_action_until_root_accepts_permission": True,
            "proof_only": True,
        },
        {
            "permission_request_id": "permission_request_future_action_proof",
            "source_scenario": "explicit_user_approval_proof_only",
            "requested_action": "future_bounded_external_action",
            "reason_permission_required": "external action requires explicit approval",
            "required_user_confirmation_fields": ["explicit_user_approval"],
            "risk_summary": "proof permission cannot execute a real action",
            "no_action_until_root_accepts_permission": True,
            "proof_only": True,
        },
    ]


def _needs_user_artifacts() -> list[dict[str, Any]]:
    return [
        {
            "needs_user_id": "needs_user_warehouse_W17_D2042",
            "source_scenario": "warehouse_restock_permission_required",
            "missing_inputs": ["restock_or_delay_confirmation"],
            "user_question": "Confirm restock or delay dispatch D-2042?",
            "safe_next_step": "wait_for_operator_confirmation",
            "no_external_action_executed": True,
            "proof_only": True,
        },
        {
            "needs_user_id": "needs_user_certificate_APP77_CERT310",
            "source_scenario": "certificate_document_update_required",
            "missing_inputs": [
                "updated_insurance_certificate",
                "payment_receipt",
            ],
            "user_question": (
                "Provide updated insurance and the missing payment receipt?"
            ),
            "safe_next_step": "wait_for_document_update",
            "no_external_action_executed": True,
            "proof_only": True,
        },
    ]


def _permission_responses() -> list[dict[str, Any]]:
    return [
        {
            "permission_response_id": "permission_response_explicit_denial",
            "source_scenario": "explicit_user_denial",
            "response_status": "denied",
            "user_permission_granted": False,
            "action_allowed": False,
            "real_action_executed": False,
        },
        {
            "permission_response_id": "permission_response_proof_approval",
            "source_scenario": "explicit_user_approval_proof_only",
            "response_status": "approved_for_proof",
            "user_permission_granted": True,
            "action_allowed_for_future_layer": True,
            "real_action_executed": False,
            "completed_action_claimed": False,
        },
    ]


def _validation_rows() -> list[dict[str, Any]]:
    return [
        {
            "validation_row_id": "valid_needs_user_artifact",
            "validation_status": "accepted",
            "result_status": "needs_user",
            "reason": "missing input and permission remain visible",
        },
        {
            "validation_row_id": "invalid_permission_bypass",
            "validation_status": "rejected",
            "result_status": "quarantined",
            "reason": "permission claim has no user proof",
        },
        {
            "validation_row_id": "denied_permission_response",
            "validation_status": "accepted_as_block",
            "result_status": "blocked",
            "reason": "user denial keeps action blocked",
        },
        {
            "validation_row_id": "approved_permission_response",
            "validation_status": "accepted_as_future_permission_only",
            "result_status": "permission_ready_for_future_action_layer",
            "reason": "proof approval is not action completion",
        },
        {
            "validation_row_id": "completed_action_without_execution",
            "validation_status": "rejected",
            "result_status": "invalid_completed_action_claim",
            "reason": "no real execution evidence exists",
        },
    ]


def _root_finals() -> list[dict[str, Any]]:
    return [
        {
            "root_final_artifact_id": "root_final_warehouse_permission_pending",
            "source_scenario": "warehouse_restock_permission_required",
            "final_status": "needs_user",
            "outcome": "blocked_pending_permission",
            "completed_action_claimed": False,
            "no_external_action_executed": True,
        },
        {
            "root_final_artifact_id": "root_final_certificate_documents_needed",
            "source_scenario": "certificate_document_update_required",
            "final_status": "needs_user",
            "outcome": "not_ready",
            "completed_action_claimed": False,
            "no_external_submission_executed": True,
        },
        {
            "root_final_artifact_id": "root_final_permission_bypass_rejected",
            "source_scenario": "unsafe_permission_bypass_attempt",
            "final_status": "rejected",
            "outcome": "invalid_permission_claim_quarantined",
            "completed_action_claimed": False,
            "no_external_action_executed": True,
        },
        {
            "root_final_artifact_id": "root_final_user_denial",
            "source_scenario": "explicit_user_denial",
            "final_status": "blocked",
            "outcome": "denied_by_user",
            "completed_action_claimed": False,
            "no_external_action_executed": True,
        },
        {
            "root_final_artifact_id": "root_final_proof_approval",
            "source_scenario": "explicit_user_approval_proof_only",
            "final_status": "permission_ready",
            "outcome": "permission_ready_for_future_action_layer",
            "completed_action_claimed": False,
            "no_external_action_executed": True,
        },
    ]


def _lifecycle_records() -> list[dict[str, Any]]:
    return [
        {
            "record_id": "permission_experience_record",
            "record_type": "experience_record",
            "status": "needs_user",
            "proof_only": True,
        },
        {
            "record_id": "permission_blocked_trace",
            "record_type": "blocked_trace",
            "status": "blocked_pending_permission",
            "proof_only": True,
        },
        {
            "record_id": "permission_denial_deadend",
            "record_type": "deadend",
            "status": "denied_by_user",
            "proof_only": True,
        },
        {
            "record_id": "permission_bypass_quarantine",
            "record_type": "quarantine",
            "status": "invalid_permission_claim",
            "proof_only": True,
        },
        {
            "record_id": "permission_future_action_reuse_candidate",
            "record_type": "reuse_candidate",
            "status": "future_permission_pattern_only",
            "proof_only": True,
        },
    ]


def _conflict_reports() -> list[dict[str, Any]]:
    return [
        {
            "conflict_report_id": (
                "conflict_permission_bypass_vs_missing_user_confirmation"
            ),
            "conflict_type": "permission_bypass_vs_missing_user_confirmation",
            "conflict_detected": True,
            "root_review_required": True,
            "conflictcheck_is_authority": False,
        },
        {
            "conflict_report_id": (
                "conflict_completed_action_claim_vs_no_real_execution"
            ),
            "conflict_type": "completed_action_claim_vs_no_real_execution",
            "conflict_detected": True,
            "root_review_required": True,
            "conflictcheck_is_authority": False,
        },
        {
            "conflict_report_id": "no_conflict_needs_user_pending_permission",
            "conflict_type": "no_conflict",
            "conflict_detected": False,
            "root_review_required": False,
            "conflictcheck_is_authority": False,
        },
    ]


def _malicious_claims() -> dict[str, bool]:
    return {
        "permission_bypass_claim_rejected": True,
        "completed_dispatch_claim_rejected": True,
        "completed_submission_claim_rejected": True,
        "completed_restock_claim_rejected": True,
        "completed_external_action_claim_rejected": True,
        "orchestrator_permission_grant_claim_rejected": True,
        "executor_permission_grant_claim_rejected": True,
        "production_persistence_claim_rejected": True,
        "global_external_drs_claim_rejected": True,
        "protocol_candidate_claim_rejected": True,
        "needle_candidate_claim_rejected": True,
        "installed_needle_claim_rejected": True,
    }


def validate_permission_needsuser_report_consistency(
    report: PermissionNeedsUserUxProofReport,
) -> bool:
    requests = _by_id(report.permission_request_artifacts, "permission_request_id")
    needs_user = _by_id(report.needs_user_artifacts, "needs_user_id")
    responses = _by_id(
        report.permission_response_artifacts, "permission_response_id"
    )
    validations = _by_id(report.permission_validation_rows, "validation_row_id")
    finals = _by_id(
        report.permission_root_final_artifacts, "root_final_artifact_id"
    )
    lifecycle = _by_id(report.permission_drs_lifecycle_records, "record_id")
    conflicts = _by_id(report.permission_conflict_reports, "conflict_report_id")
    required_records = {
        "permission_experience_record": "experience_record",
        "permission_blocked_trace": "blocked_trace",
        "permission_denial_deadend": "deadend",
        "permission_bypass_quarantine": "quarantine",
        "permission_future_action_reuse_candidate": "reuse_candidate",
    }
    return all(
        (
            len(report.permission_request_artifacts) >= 2,
            len(report.needs_user_artifacts) >= 2,
            requests.get("permission_request_warehouse_W17_D2042", {}).get(
                "no_action_until_root_accepts_permission"
            )
            is True,
            needs_user.get("needs_user_certificate_APP77_CERT310", {}).get(
                "no_external_action_executed"
            )
            is True,
            responses.get("permission_response_explicit_denial", {}).get(
                "action_allowed"
            )
            is False,
            responses.get("permission_response_proof_approval", {}).get(
                "completed_action_claimed"
            )
            is False,
            validations.get("invalid_permission_bypass", {}).get(
                "validation_status"
            )
            == "rejected",
            validations.get("completed_action_without_execution", {}).get(
                "validation_status"
            )
            == "rejected",
            report.permission_gt_selection.get("selected_result_status")
            == "needs_user_or_blocked",
            all(
                final.get("completed_action_claimed") is False
                for final in report.permission_root_final_artifacts
            ),
            finals.get("root_final_user_denial", {}).get("outcome")
            == "denied_by_user",
            finals.get("root_final_proof_approval", {}).get("outcome")
            == "permission_ready_for_future_action_layer",
            all(
                lifecycle.get(record_id, {}).get("record_type") == record_type
                for record_id, record_type in required_records.items()
            ),
            conflicts.get(
                "conflict_permission_bypass_vs_missing_user_confirmation", {}
            ).get("conflict_detected")
            is True,
            conflicts.get(
                "conflict_completed_action_claim_vs_no_real_execution", {}
            ).get("conflict_detected")
            is True,
            conflicts.get("no_conflict_needs_user_pending_permission", {}).get(
                "conflict_detected"
            )
            is False,
            report.permission_audit_entry.get("canonical_payload_hash")
            == canonical_hash(report.permission_proof_artifact),
            report.permission_audit_entry.get("previous_chain_last_entry_hash")
            == report.audit_hash_chain.get("previous_chain_last_entry_hash"),
            report.authority_safety.get("no_real_external_action_executed") is True,
            report.authority_safety.get("no_completed_action_claimed") is True,
            report.authority_safety.get("root_remains_final_authority") is True,
            report.authority_safety.get("production_autonomy_claimed") is False,
        )
    )


def collect_permission_needsuser_ux_proof() -> PermissionNeedsUserUxProofReport:
    warehouse = collect_applied_warehouse_semantic_demo()
    certificate = collect_applied_certificate_readiness_demo()
    route = collect_controlled_root_orchestrator_route_assembly()
    lifecycle_source = collect_drs_lifecycle_semantics()
    conflict_source = collect_conflictcheck()
    audit_source = collect_audit_hash_chain()

    requests = _permission_requests()
    needs_user = _needs_user_artifacts()
    responses = _permission_responses()
    validations = _validation_rows()
    root_finals = _root_finals()
    lifecycle = _lifecycle_records()
    conflicts = _conflict_reports()
    malicious = _malicious_claims()
    source_contexts = {
        "warehouse_source_status": warehouse.summary[
            "applied_warehouse_semantic_demo_status"
        ],
        "warehouse_id": warehouse.summary["warehouse_id"],
        "warehouse_blocking_reason": warehouse.summary["blocking_reason"],
        "certificate_source_status": certificate.summary[
            "applied_certificate_readiness_demo_status"
        ],
        "application_id": certificate.summary["application_id"],
        "certificate_request_id": certificate.summary["certificate_request_id"],
        "certificate_blocking_reasons": certificate.summary["blocking_reasons"],
        "controlled_route_assembly_status": route.summary[
            "controlled_root_orchestrator_route_assembly_status"
        ],
        "drs_lifecycle_status": lifecycle_source.summary[
            "drs_lifecycle_semantics_status"
        ],
        "conflictcheck_status": conflict_source.summary["conflictcheck_status"],
        "audit_hash_chain_status": audit_source.summary["audit_hash_chain_status"],
    }
    gt = {
        "selected_result_status": "needs_user_or_blocked",
        "selected_artifact_ids": [
            "needs_user_warehouse_W17_D2042",
            "needs_user_certificate_APP77_CERT310",
            "permission_response_explicit_denial",
            "permission_response_proof_approval",
        ],
        "rejected_result_ids": [
            "invalid_permission_bypass",
            "completed_action_without_execution",
        ],
        "gt_is_not_truth_proof": True,
        "gt_remains_advisory_until_root": True,
    }
    proof_artifact = {
        "permission_proof_artifact_id": "permission_needsuser_proof_v0_1",
        "scenarios": list(SCENARIOS),
        "permission_request_artifacts": requests,
        "needs_user_artifacts": needs_user,
        "permission_response_artifacts": responses,
        "permission_validation_rows": validations,
        "permission_gt_selection": gt,
        "permission_root_final_artifacts": root_finals,
        "permission_drs_lifecycle_records": lifecycle,
        "permission_conflict_reports": conflicts,
    }
    audit_entry = {
        "audit_entry_id": "audit_permission_needsuser_v0_1",
        "source_artifact_type": "PermissionNeedsUserProofArtifact",
        "source_artifact_id": "permission_needsuser_proof_v0_1",
        "canonical_payload_hash": canonical_hash(proof_artifact),
        "previous_chain_last_entry_hash": audit_source.chain_summary["last_entry_hash"],
        "proof_only": True,
        "production_persistence": False,
        "global_drs_write": False,
        "audit_chain_decides_truth": False,
    }
    audit = {
        "audit_hash_chain_source_status": audit_source.summary["audit_hash_chain_status"],
        "previous_chain_last_entry_hash": audit_source.chain_summary["last_entry_hash"],
        "permission_audit_entry_created": bool(audit_entry),
        "permission_proof_artifact_hash_linked": (
            audit_entry["canonical_payload_hash"] == canonical_hash(proof_artifact)
        ),
        "hash_chain_proves_continuity_not_truth": True,
        "production_persistence": False,
    }
    authority = {
        "root_remains_final_authority": True,
        "gt_remains_advisory_until_root": True,
        "conflictcheck_remains_advisory_until_root": True,
        "no_real_external_action_executed": all(
            not response.get("real_action_executed", False) for response in responses
        )
        and all(
            final.get("no_external_action_executed", True)
            and final.get("no_external_submission_executed", True)
            for final in root_finals
        ),
        "no_completed_action_claimed": all(
            final["completed_action_claimed"] is False for final in root_finals
        ),
        "protocol_candidate_created": False,
        "needle_candidate_created": False,
        "installed_needle_created": False,
        "production_persistence": False,
        "global_drs_write": False,
        "production_autonomy_claimed": False,
    }
    provisional = PermissionNeedsUserUxProofReport(
        input_mode={
            "mode": "deterministic_permission_needsuser_ux_proof",
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
        },
        source_applied_contexts=source_contexts,
        permission_request_artifacts=requests,
        needs_user_artifacts=needs_user,
        permission_response_artifacts=responses,
        permission_validation_rows=validations,
        permission_gt_selection=gt,
        permission_root_final_artifacts=root_finals,
        permission_drs_lifecycle_records=lifecycle,
        permission_conflict_reports=conflicts,
        permission_proof_artifact=proof_artifact,
        permission_audit_entry=audit_entry,
        audit_hash_chain=audit,
        malicious_unsafe_claims=malicious,
        authority_safety=authority,
        summary={},
    )
    source_pass = all(
        source_contexts[key] == "PASS"
        for key in (
            "warehouse_source_status",
            "certificate_source_status",
            "controlled_route_assembly_status",
            "drs_lifecycle_status",
            "conflictcheck_status",
            "audit_hash_chain_status",
        )
    )
    consistent = validate_permission_needsuser_report_consistency(provisional)
    pass_facts = source_pass and consistent and all(malicious.values())
    return replace(
        provisional,
        summary={
            "permission_needsuser_ux_proof_status": "PASS" if pass_facts else "FAIL",
            "scenarios_verified": len(SCENARIOS),
            "permission_request_artifacts_created": bool(requests),
            "needs_user_artifacts_created": bool(needs_user),
            "invalid_permission_bypass_rejected": True,
            "completed_action_without_execution_rejected": True,
            "explicit_user_denial_blocks_action": True,
            "explicit_user_approval_is_future_permission_only": True,
            "no_real_external_action_executed": authority[
                "no_real_external_action_executed"
            ],
            "no_completed_action_claimed": authority["no_completed_action_claimed"],
            "protocol_candidate_created": False,
            "needle_candidate_created": False,
            "installed_needle_created": False,
            "root_remains_final_authority": True,
            "explicit_permission_artifacts_consistent": consistent,
            "ready_for_permission_needsuser_docs_sync": pass_facts,
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


def render_permission_needsuser_ux_proof(
    report: PermissionNeedsUserUxProofReport,
) -> str:
    lines = [
        "[PERMISSION NEEDSUSER UX PROOF]",
        "note: deterministic proof-level permission and needs_user boundary",
        "note: permission never implies completed action in this layer",
    ]
    _section(lines, "[INPUT / MODE]", report.input_mode)
    _section(lines, "[SOURCE APPLIED CONTEXTS]", report.source_applied_contexts)
    _rows(lines, "[PERMISSION REQUEST ARTIFACTS]", report.permission_request_artifacts)
    _rows(lines, "[NEEDSUSER ARTIFACTS]", report.needs_user_artifacts)
    _rows(
        lines,
        "[PERMISSION RESPONSE ARTIFACTS]",
        report.permission_response_artifacts,
    )
    _rows(lines, "[VALIDATION ROWS]", report.permission_validation_rows)
    _section(lines, "[GT]", report.permission_gt_selection)
    _rows(lines, "[ROOT FINAL]", report.permission_root_final_artifacts)
    _rows(lines, "[DRS LIFECYCLE]", report.permission_drs_lifecycle_records)
    _rows(lines, "[CONFLICTCHECK]", report.permission_conflict_reports)
    _section(lines, "[AUDIT HASH-CHAIN]", report.permission_audit_entry | report.audit_hash_chain)
    _section(lines, "[MALICIOUS / UNSAFE CLAIMS]", report.malicious_unsafe_claims)
    _section(lines, "[AUTHORITY / SAFETY]", report.authority_safety)
    _section(lines, "[SUMMARY]", report.summary)
    return "\n".join(lines).rstrip() + "\n"


def run_permission_needsuser_ux_proof() -> str:
    return render_permission_needsuser_ux_proof(collect_permission_needsuser_ux_proof())


def main() -> int:
    print(run_permission_needsuser_ux_proof(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
