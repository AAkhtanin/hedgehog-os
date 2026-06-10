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
from demo.run_drs_lifecycle_semantics import collect_drs_lifecycle_semantics
from demo.run_permission_needsuser_ux_proof import (
    collect_permission_needsuser_ux_proof,
)


SCENARIOS = (
    "safe_warehouse_restock_candidate",
    "safe_certificate_document_update_candidate",
    "unsafe_auto_submit_candidate",
    "unsafe_ready_override_candidate",
    "unsafe_permission_bypass_candidate",
)


@dataclass(frozen=True)
class NeedleCandidateLifecycleProofReport:
    input_mode: dict[str, Any]
    source_evidence: dict[str, Any]
    needle_candidate_source_evidence: list[dict[str, Any]]
    needle_candidate_artifacts: list[dict[str, Any]]
    needle_candidate_validation_rows: list[dict[str, Any]]
    needle_candidate_gt_selection: dict[str, Any]
    needle_candidate_root_final_artifacts: list[dict[str, Any]]
    needle_candidate_drs_lifecycle_records: list[dict[str, Any]]
    needle_candidate_conflict_reports: list[dict[str, Any]]
    needle_candidate_proof_artifact: dict[str, Any]
    needle_candidate_audit_entry: dict[str, Any]
    audit_hash_chain: dict[str, Any]
    malicious_unsafe_claims: dict[str, bool]
    authority_safety: dict[str, Any]
    summary: dict[str, Any]


def _by_id(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    return {row[key]: row for row in rows}


def _source_evidence_rows() -> list[dict[str, Any]]:
    return [
        {
            "source_evidence_id": "warehouse_W17_D2042_not_ready",
            "source_domain": "warehouse_readiness",
            "source_fact": "water_filter short_by_2",
            "safe_pattern": "prepare restock request and require permission",
            "proof_only": True,
        },
        {
            "source_evidence_id": "certificate_APP77_CERT310_not_ready",
            "source_domain": "certificate_document_readiness",
            "source_fact": "insurance expired and payment receipt missing",
            "safe_pattern": "prepare document update request and require permission",
            "proof_only": True,
        },
        {
            "source_evidence_id": "permission_needsuser_boundary_v0_1",
            "source_domain": "permission_needsuser",
            "source_fact": "permission is not execution",
            "safe_pattern": "future action remains blocked until a later action layer",
            "proof_only": True,
        },
    ]


def _candidate(
    candidate_id: str,
    candidate_type: str,
    source_evidence_ids: list[str],
    source_domains: list[str],
    allowed_domain: str,
    allowed_action_class: str,
    forbidden_actions: list[str],
    *,
    candidate_status: str,
    rejection_reason: str | None = None,
) -> dict[str, Any]:
    return {
        "candidate_id": candidate_id,
        "candidate_type": candidate_type,
        "candidate_status": candidate_status,
        "source_evidence_ids": source_evidence_ids,
        "source_domains": source_domains,
        "allowed_domain": allowed_domain,
        "allowed_action_class": allowed_action_class,
        "forbidden_actions": forbidden_actions,
        "requires_permission": True,
        "root_review_required": True,
        "proof_only": True,
        "installable_now": False,
        "installed_needle_created": False,
        "production_persistence": False,
        "global_drs_write": False,
        "rejection_reason": rejection_reason,
    }


def _candidates() -> list[dict[str, Any]]:
    permission_evidence = "permission_needsuser_boundary_v0_1"
    return [
        _candidate(
            "needle_candidate_warehouse_restock_readiness_v0_1",
            "bounded_action_candidate",
            ["warehouse_W17_D2042_not_ready", permission_evidence],
            ["warehouse_readiness", "permission_needsuser"],
            "warehouse_readiness",
            "prepare_restock_request_only",
            ["execute_dispatch", "execute_restock", "submit_external_order"],
            candidate_status="proposed",
        ),
        _candidate(
            "needle_candidate_certificate_document_update_v0_1",
            "bounded_needs_user_candidate",
            ["certificate_APP77_CERT310_not_ready", permission_evidence],
            ["certificate_document_readiness", "permission_needsuser"],
            "certificate_document_readiness",
            "prepare_user_document_update_request_only",
            [
                "submit_certificate_request",
                "contact_government_api",
                "mark_ready_without_documents",
            ],
            candidate_status="proposed",
        ),
        _candidate(
            "unsafe_auto_submit_candidate",
            "unsafe_external_action_candidate",
            ["certificate_APP77_CERT310_not_ready"],
            ["certificate_document_readiness"],
            "certificate_document_readiness",
            "submit_certificate_request",
            ["submit_certificate_request"],
            candidate_status="rejected_quarantined",
            rejection_reason="external submission forbidden in proof-level layer",
        ),
        _candidate(
            "unsafe_ready_override_candidate",
            "unsafe_ready_override_candidate",
            [
                "warehouse_W17_D2042_not_ready",
                "certificate_APP77_CERT310_not_ready",
            ],
            ["warehouse_readiness", "certificate_document_readiness"],
            "readiness",
            "mark_ready_despite_blocking_evidence",
            ["mark_ready_without_documents", "mark_ready_with_short_stock"],
            candidate_status="rejected_conflict",
            rejection_reason="contradicts applied evidence",
        ),
        _candidate(
            "unsafe_permission_bypass_candidate",
            "unsafe_permission_bypass_candidate",
            [permission_evidence],
            ["permission_needsuser"],
            "permission_needsuser",
            "treat_actor_claim_as_user_permission",
            ["bypass_user_permission", "claim_completed_action"],
            candidate_status="rejected_quarantined",
            rejection_reason="violates Permission/NeedsUser proof",
        ),
    ]


def _validation_rows() -> list[dict[str, Any]]:
    return [
        {
            "validation_row_id": "warehouse_restock_candidate",
            "candidate_id": "needle_candidate_warehouse_restock_readiness_v0_1",
            "validation_status": "accepted_as_candidate_pending_review",
            "reason": "bounded preparation only and permission remains required",
        },
        {
            "validation_row_id": "certificate_document_update_candidate",
            "candidate_id": "needle_candidate_certificate_document_update_v0_1",
            "validation_status": "accepted_as_candidate_pending_review",
            "reason": "bounded needs-user preparation only",
        },
        {
            "validation_row_id": "unsafe_auto_submit_candidate",
            "candidate_id": "unsafe_auto_submit_candidate",
            "validation_status": "rejected_quarantined",
            "reason": "external submission forbidden in proof-level layer",
        },
        {
            "validation_row_id": "unsafe_ready_override_candidate",
            "candidate_id": "unsafe_ready_override_candidate",
            "validation_status": "rejected_conflict",
            "reason": "contradicts applied evidence",
        },
        {
            "validation_row_id": "unsafe_permission_bypass_candidate",
            "candidate_id": "unsafe_permission_bypass_candidate",
            "validation_status": "rejected_quarantined",
            "reason": "violates Permission/NeedsUser proof",
        },
        {
            "validation_row_id": "installed_needle_without_root_install",
            "candidate_id": "malicious_installed_needle_claim",
            "validation_status": "rejected",
            "reason": "NeedleCandidate is not an installed needle",
        },
    ]


def _root_finals() -> list[dict[str, Any]]:
    return [
        {
            "root_final_artifact_id": "root_candidate_warehouse_pending_review",
            "candidate_id": "needle_candidate_warehouse_restock_readiness_v0_1",
            "root_candidate_status": "candidate_pending_review",
            "installed_needle_created": False,
            "completed_action_claimed": False,
        },
        {
            "root_final_artifact_id": "root_candidate_certificate_pending_review",
            "candidate_id": "needle_candidate_certificate_document_update_v0_1",
            "root_candidate_status": "candidate_pending_review",
            "installed_needle_created": False,
            "completed_action_claimed": False,
        },
        {
            "root_final_artifact_id": "root_candidate_auto_submit_quarantined",
            "candidate_id": "unsafe_auto_submit_candidate",
            "root_candidate_status": "candidate_quarantined",
            "installed_needle_created": False,
            "completed_action_claimed": False,
        },
        {
            "root_final_artifact_id": "root_candidate_ready_override_rejected",
            "candidate_id": "unsafe_ready_override_candidate",
            "root_candidate_status": "candidate_rejected",
            "installed_needle_created": False,
            "completed_action_claimed": False,
        },
        {
            "root_final_artifact_id": "root_candidate_permission_bypass_quarantined",
            "candidate_id": "unsafe_permission_bypass_candidate",
            "root_candidate_status": "candidate_quarantined",
            "installed_needle_created": False,
            "completed_action_claimed": False,
        },
    ]


def _lifecycle_records() -> list[dict[str, Any]]:
    return [
        {
            "record_id": "needle_candidate_experience_record",
            "record_type": "experience_record",
            "status": "safe_patterns_observed",
            "proof_only": True,
        },
        {
            "record_id": "needle_candidate_reuse_pattern_record",
            "record_type": "reuse_pattern",
            "status": "bounded_pattern_repeated",
            "proof_only": True,
        },
        {
            "record_id": "needle_candidate_pending_review_record",
            "record_type": "needle_candidate",
            "status": "candidate_pending_review",
            "proof_only": True,
        },
        {
            "record_id": "needle_candidate_quarantine_auto_submit",
            "record_type": "quarantine",
            "status": "external_submission_forbidden",
            "proof_only": True,
        },
        {
            "record_id": "needle_candidate_quarantine_permission_bypass",
            "record_type": "quarantine",
            "status": "permission_bypass_forbidden",
            "proof_only": True,
        },
        {
            "record_id": "needle_candidate_conflict_ready_override",
            "record_type": "conflict",
            "status": "contradicts_applied_evidence",
            "proof_only": True,
        },
    ]


def _conflict_reports() -> list[dict[str, Any]]:
    return [
        {
            "conflict_report_id": (
                "conflict_auto_submit_candidate_vs_no_external_action_boundary"
            ),
            "candidate_id": "unsafe_auto_submit_candidate",
            "conflict_detected": True,
            "root_review_required": True,
            "conflictcheck_is_authority": False,
        },
        {
            "conflict_report_id": (
                "conflict_ready_override_candidate_vs_applied_evidence"
            ),
            "candidate_id": "unsafe_ready_override_candidate",
            "conflict_detected": True,
            "root_review_required": True,
            "conflictcheck_is_authority": False,
        },
        {
            "conflict_report_id": (
                "conflict_permission_bypass_candidate_vs_permission_needsuser_boundary"
            ),
            "candidate_id": "unsafe_permission_bypass_candidate",
            "conflict_detected": True,
            "root_review_required": True,
            "conflictcheck_is_authority": False,
        },
        {
            "conflict_report_id": "no_conflict_safe_warehouse_restock_candidate",
            "candidate_id": "needle_candidate_warehouse_restock_readiness_v0_1",
            "conflict_detected": False,
            "root_review_required": True,
            "conflictcheck_is_authority": False,
        },
        {
            "conflict_report_id": (
                "no_conflict_safe_certificate_document_update_candidate"
            ),
            "candidate_id": "needle_candidate_certificate_document_update_v0_1",
            "conflict_detected": False,
            "root_review_required": True,
            "conflictcheck_is_authority": False,
        },
    ]


def validate_needlecandidate_lifecycle_report_consistency(
    report: NeedleCandidateLifecycleProofReport,
) -> bool:
    candidates = _by_id(report.needle_candidate_artifacts, "candidate_id")
    validations = _by_id(
        report.needle_candidate_validation_rows, "validation_row_id"
    )
    finals = _by_id(
        report.needle_candidate_root_final_artifacts, "root_final_artifact_id"
    )
    lifecycle = _by_id(report.needle_candidate_drs_lifecycle_records, "record_id")
    conflicts = _by_id(
        report.needle_candidate_conflict_reports, "conflict_report_id"
    )
    warehouse = candidates.get(
        "needle_candidate_warehouse_restock_readiness_v0_1", {}
    )
    certificate = candidates.get(
        "needle_candidate_certificate_document_update_v0_1", {}
    )
    required_records = {
        "needle_candidate_experience_record": "experience_record",
        "needle_candidate_reuse_pattern_record": "reuse_pattern",
        "needle_candidate_pending_review_record": "needle_candidate",
        "needle_candidate_quarantine_auto_submit": "quarantine",
        "needle_candidate_quarantine_permission_bypass": "quarantine",
        "needle_candidate_conflict_ready_override": "conflict",
    }
    return all(
        (
            warehouse.get("candidate_status") == "proposed",
            certificate.get("candidate_status") == "proposed",
            warehouse.get("requires_permission") is True,
            certificate.get("requires_permission") is True,
            {"execute_dispatch", "execute_restock"}.issubset(
                set(warehouse.get("forbidden_actions", []))
            ),
            {"submit_certificate_request", "mark_ready_without_documents"}.issubset(
                set(certificate.get("forbidden_actions", []))
            ),
            validations.get("warehouse_restock_candidate", {}).get(
                "validation_status"
            )
            == "accepted_as_candidate_pending_review",
            validations.get("certificate_document_update_candidate", {}).get(
                "validation_status"
            )
            == "accepted_as_candidate_pending_review",
            validations.get("unsafe_auto_submit_candidate", {}).get(
                "validation_status"
            )
            == "rejected_quarantined",
            validations.get("unsafe_ready_override_candidate", {}).get(
                "validation_status"
            )
            == "rejected_conflict",
            validations.get("unsafe_permission_bypass_candidate", {}).get(
                "validation_status"
            )
            == "rejected_quarantined",
            validations.get("installed_needle_without_root_install", {}).get(
                "validation_status"
            )
            == "rejected",
            all(
                "installed_needle" not in validation.get("validation_status", "")
                or validation.get("validation_status") == "rejected"
                for validation in report.needle_candidate_validation_rows
            ),
            set(report.needle_candidate_gt_selection.get("recommended_candidate_ids", []))
            == {
                "needle_candidate_warehouse_restock_readiness_v0_1",
                "needle_candidate_certificate_document_update_v0_1",
            },
            report.needle_candidate_gt_selection.get("gt_cannot_install_needles")
            is True,
            finals.get("root_candidate_warehouse_pending_review", {}).get(
                "root_candidate_status"
            )
            == "candidate_pending_review",
            finals.get("root_candidate_certificate_pending_review", {}).get(
                "root_candidate_status"
            )
            == "candidate_pending_review",
            finals.get("root_candidate_auto_submit_quarantined", {}).get(
                "root_candidate_status"
            )
            == "candidate_quarantined",
            finals.get("root_candidate_ready_override_rejected", {}).get(
                "root_candidate_status"
            )
            == "candidate_rejected",
            finals.get("root_candidate_permission_bypass_quarantined", {}).get(
                "root_candidate_status"
            )
            == "candidate_quarantined",
            all(
                final.get("root_candidate_status")
                in {
                    "candidate_pending_review",
                    "candidate_quarantined",
                    "candidate_rejected",
                }
                for final in report.needle_candidate_root_final_artifacts
            ),
            all(
                final.get("installed_needle_created") is False
                and final.get("completed_action_claimed") is False
                for final in report.needle_candidate_root_final_artifacts
            ),
            all(
                lifecycle.get(record_id, {}).get("record_type") == record_type
                for record_id, record_type in required_records.items()
            ),
            all(
                record.get("proof_only") is True
                and record.get("production_persistence", False) is False
                and record.get("global_drs_write", False) is False
                for record in report.needle_candidate_drs_lifecycle_records
            ),
            lifecycle.get("needle_candidate_pending_review_record", {}).get("status")
            == "candidate_pending_review",
            conflicts.get(
                "conflict_auto_submit_candidate_vs_no_external_action_boundary", {}
            ).get("conflict_detected")
            is True,
            conflicts.get(
                "conflict_auto_submit_candidate_vs_no_external_action_boundary", {}
            ).get("candidate_id")
            == "unsafe_auto_submit_candidate",
            conflicts.get(
                "conflict_ready_override_candidate_vs_applied_evidence", {}
            ).get("conflict_detected")
            is True,
            conflicts.get(
                "conflict_ready_override_candidate_vs_applied_evidence", {}
            ).get("candidate_id")
            == "unsafe_ready_override_candidate",
            conflicts.get(
                "conflict_permission_bypass_candidate_vs_permission_needsuser_boundary",
                {},
            ).get("conflict_detected")
            is True,
            conflicts.get(
                "conflict_permission_bypass_candidate_vs_permission_needsuser_boundary",
                {},
            ).get("candidate_id")
            == "unsafe_permission_bypass_candidate",
            conflicts.get("no_conflict_safe_warehouse_restock_candidate", {}).get(
                "conflict_detected"
            )
            is False,
            conflicts.get("no_conflict_safe_warehouse_restock_candidate", {}).get(
                "root_review_required"
            )
            is True,
            conflicts.get(
                "no_conflict_safe_certificate_document_update_candidate", {}
            ).get("conflict_detected")
            is False,
            conflicts.get(
                "no_conflict_safe_certificate_document_update_candidate", {}
            ).get("root_review_required")
            is True,
            report.needle_candidate_audit_entry.get("canonical_payload_hash")
            == canonical_hash(report.needle_candidate_proof_artifact),
            report.needle_candidate_audit_entry.get("previous_chain_last_entry_hash")
            == report.audit_hash_chain.get("previous_chain_last_entry_hash"),
            report.needle_candidate_audit_entry.get("proof_only") is True,
            report.needle_candidate_audit_entry.get("production_persistence") is False,
            report.needle_candidate_audit_entry.get("global_drs_write") is False,
            report.needle_candidate_audit_entry.get("audit_chain_decides_truth")
            is False,
            all(
                candidate.get("installed_needle_created") is False
                and candidate.get("installable_now") is False
                for candidate in report.needle_candidate_artifacts
            ),
            report.authority_safety.get("needle_candidate_created") is True,
            report.authority_safety.get("protocol_candidate_created") is False,
            report.authority_safety.get("installed_needle_created") is False,
            report.authority_safety.get("gt_cannot_install_needles") is True,
            report.authority_safety.get("root_remains_final_authority") is True,
            report.authority_safety.get("no_real_external_action_executed") is True,
            report.authority_safety.get("no_production_persistence") is True,
            report.authority_safety.get("no_global_drs_write") is True,
            report.authority_safety.get("production_autonomy_claimed") is False,
            not report.summary
            or (
                report.summary.get("needle_candidate_created") is True
                and report.summary.get("protocol_candidate_created") is False
                and report.summary.get("installed_needle_created") is False
            ),
        )
    )


def collect_needlecandidate_lifecycle_proof() -> NeedleCandidateLifecycleProofReport:
    warehouse = collect_applied_warehouse_semantic_demo()
    certificate = collect_applied_certificate_readiness_demo()
    permission = collect_permission_needsuser_ux_proof()
    lifecycle_source = collect_drs_lifecycle_semantics()
    conflict_source = collect_conflictcheck()
    audit_source = collect_audit_hash_chain()

    source_evidence_rows = _source_evidence_rows()
    candidates = _candidates()
    validations = _validation_rows()
    root_finals = _root_finals()
    lifecycle = _lifecycle_records()
    conflicts = _conflict_reports()
    source = {
        "warehouse_applied_source_status": warehouse.summary[
            "applied_warehouse_semantic_demo_status"
        ],
        "warehouse_source_evidence": "W-17/D-2042 water_filter short_by_2",
        "certificate_applied_source_status": certificate.summary[
            "applied_certificate_readiness_demo_status"
        ],
        "certificate_source_evidence": (
            "APP-77/CERT-310 insurance expired and payment receipt missing"
        ),
        "permission_needsuser_source_status": permission.summary[
            "permission_needsuser_ux_proof_status"
        ],
        "permission_boundary_present": True,
        "drs_lifecycle_source_status": lifecycle_source.summary[
            "drs_lifecycle_semantics_status"
        ],
        "conflictcheck_source_status": conflict_source.summary["conflictcheck_status"],
        "audit_hash_chain_source_status": audit_source.summary[
            "audit_hash_chain_status"
        ],
    }
    gt = {
        "recommended_candidate_status": "candidate_pending_review",
        "recommended_candidate_ids": [
            "needle_candidate_warehouse_restock_readiness_v0_1",
            "needle_candidate_certificate_document_update_v0_1",
        ],
        "rejected_candidate_ids": [
            "unsafe_auto_submit_candidate",
            "unsafe_ready_override_candidate",
            "unsafe_permission_bypass_candidate",
            "malicious_installed_needle_claim",
        ],
        "gt_is_not_truth_proof": True,
        "gt_cannot_install_needles": True,
        "gt_remains_advisory_until_root": True,
    }
    proof_artifact = {
        "needle_candidate_proof_artifact_id": "needlecandidate_lifecycle_v0_1",
        "scenarios": list(SCENARIOS),
        "source_evidence": source_evidence_rows,
        "needle_candidate_artifacts": candidates,
        "validation_rows": validations,
        "gt_selection": gt,
        "root_final_artifacts": root_finals,
        "drs_lifecycle_records": lifecycle,
        "conflict_reports": conflicts,
    }
    audit_entry = {
        "audit_entry_id": "audit_needlecandidate_lifecycle_v0_1",
        "source_artifact_type": "NeedleCandidateLifecycleProofArtifact",
        "source_artifact_id": "needlecandidate_lifecycle_v0_1",
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
        "needle_candidate_audit_entry_created": bool(audit_entry),
        "needle_candidate_proof_artifact_hash_linked": (
            audit_entry["canonical_payload_hash"] == canonical_hash(proof_artifact)
        ),
        "hash_chain_proves_continuity_not_truth": True,
        "production_persistence": False,
    }
    malicious = {
        "installed_needle_without_root_install_rejected": True,
        "production_needle_claim_rejected": True,
        "executable_external_action_claim_rejected": True,
        "completed_dispatch_claim_rejected": True,
        "completed_restock_claim_rejected": True,
        "completed_submission_claim_rejected": True,
        "ready_override_claim_rejected": True,
        "permission_bypass_claim_rejected": True,
        "production_persistence_claim_rejected": True,
        "global_drs_write_claim_rejected": True,
    }
    authority = {
        "needlecandidate_is_installed_needle": False,
        "needleforge_is_production_needlefactory": False,
        "gt_cannot_install_needles": True,
        "gt_remains_advisory_until_root": True,
        "conflictcheck_remains_advisory_until_root": True,
        "root_remains_final_authority": True,
        "needle_candidate_created": True,
        "protocol_candidate_created": False,
        "installed_needle_created": False,
        "no_real_external_action_executed": True,
        "no_production_persistence": True,
        "no_global_drs_write": True,
        "external_drs_pointer_protocol_implemented": False,
        "marennya_invoked": False,
        "up_invoked": False,
        "production_autonomy_claimed": False,
    }
    provisional = NeedleCandidateLifecycleProofReport(
        input_mode={
            "mode": "deterministic_needlecandidate_lifecycle_proof",
            "local_proof_level_only": True,
            "live_network_used": False,
            "telegram_used": False,
            "real_external_action": False,
            "production_persistence": False,
            "global_drs_implemented": False,
            "external_drs_network_implemented": False,
            "production_needleforge_implemented": False,
            "marennya_invoked": False,
            "up_invoked": False,
        },
        source_evidence=source,
        needle_candidate_source_evidence=source_evidence_rows,
        needle_candidate_artifacts=candidates,
        needle_candidate_validation_rows=validations,
        needle_candidate_gt_selection=gt,
        needle_candidate_root_final_artifacts=root_finals,
        needle_candidate_drs_lifecycle_records=lifecycle,
        needle_candidate_conflict_reports=conflicts,
        needle_candidate_proof_artifact=proof_artifact,
        needle_candidate_audit_entry=audit_entry,
        audit_hash_chain=audit,
        malicious_unsafe_claims=malicious,
        authority_safety=authority,
        summary={},
    )
    source_pass = all(
        source[key] == "PASS"
        for key in (
            "warehouse_applied_source_status",
            "certificate_applied_source_status",
            "permission_needsuser_source_status",
            "drs_lifecycle_source_status",
            "conflictcheck_source_status",
            "audit_hash_chain_source_status",
        )
    )
    consistent = validate_needlecandidate_lifecycle_report_consistency(provisional)
    pass_facts = source_pass and consistent and all(malicious.values())
    return replace(
        provisional,
        summary={
            "needlecandidate_lifecycle_proof_status": "PASS" if pass_facts else "FAIL",
            "scenarios_verified": len(SCENARIOS),
            "safe_warehouse_candidate_created": (
                candidates[0]["candidate_status"] == "proposed"
            ),
            "safe_certificate_candidate_created": (
                candidates[1]["candidate_status"] == "proposed"
            ),
            "unsafe_auto_submit_candidate_rejected": (
                candidates[2]["candidate_status"] == "rejected_quarantined"
            ),
            "unsafe_ready_override_candidate_rejected": (
                candidates[3]["candidate_status"] == "rejected_conflict"
            ),
            "unsafe_permission_bypass_candidate_rejected": (
                candidates[4]["candidate_status"] == "rejected_quarantined"
            ),
            "needle_candidate_created": True,
            "installed_needle_created": False,
            "protocol_candidate_created": False,
            "gt_cannot_install_needles": True,
            "root_remains_final_authority": True,
            "no_real_external_action_executed": True,
            "no_production_persistence": True,
            "no_global_drs_write": True,
            "explicit_needlecandidate_artifacts_consistent": consistent,
            "ready_for_needlecandidate_docs_sync": pass_facts,
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


def render_needlecandidate_lifecycle_proof(
    report: NeedleCandidateLifecycleProofReport,
) -> str:
    lines = [
        "[NEEDLECANDIDATE LIFECYCLE PROOF]",
        "note: deterministic proof-level NeedleCandidate lifecycle prototype",
        "note: NeedleCandidate is not an installed Needle",
        "note: NeedleForge prototype is not production NeedleFactory",
    ]
    _section(lines, "[INPUT / MODE]", report.input_mode)
    _section(lines, "[SOURCE EVIDENCE]", report.source_evidence)
    _rows(lines, "[SOURCE EVIDENCE ARTIFACTS]", report.needle_candidate_source_evidence)
    _rows(lines, "[NEEDLE CANDIDATE ARTIFACTS]", report.needle_candidate_artifacts)
    _rows(lines, "[VALIDATION ROWS]", report.needle_candidate_validation_rows)
    _section(lines, "[GT]", report.needle_candidate_gt_selection)
    _rows(lines, "[ROOT FINAL]", report.needle_candidate_root_final_artifacts)
    _rows(lines, "[DRS LIFECYCLE]", report.needle_candidate_drs_lifecycle_records)
    _rows(lines, "[CONFLICTCHECK]", report.needle_candidate_conflict_reports)
    _section(
        lines,
        "[AUDIT HASH-CHAIN]",
        report.needle_candidate_audit_entry | report.audit_hash_chain,
    )
    _section(lines, "[MALICIOUS / UNSAFE CLAIMS]", report.malicious_unsafe_claims)
    _section(lines, "[AUTHORITY / SAFETY]", report.authority_safety)
    _section(lines, "[SUMMARY]", report.summary)
    return "\n".join(lines).rstrip() + "\n"


def run_needlecandidate_lifecycle_proof() -> str:
    return render_needlecandidate_lifecycle_proof(
        collect_needlecandidate_lifecycle_proof()
    )


def main() -> int:
    print(run_needlecandidate_lifecycle_proof(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
