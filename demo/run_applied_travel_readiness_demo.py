from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from demo.run_applied_certificate_readiness_demo import (
    collect_applied_certificate_readiness_demo,
)
from demo.run_applied_drs_retrieval_reuse import collect_applied_drs_retrieval_reuse
from demo.run_audit_hash_chain import canonical_hash, collect_audit_hash_chain
from demo.run_conflictcheck import collect_conflictcheck
from demo.run_permission_needsuser_ux_proof import (
    collect_permission_needsuser_ux_proof,
)


@dataclass(frozen=True)
class AppliedTravelReadinessReport:
    source_evidence: dict[str, Any]
    travel_request: dict[str, Any]
    travel_evidence: dict[str, Any]
    travel_condition_matrix: list[dict[str, Any]]
    travel_decomposition_hint: dict[str, Any]
    travel_drs_reuse_candidates: list[dict[str, Any]]
    travel_permission_boundary: dict[str, Any]
    travel_conflict_report: dict[str, Any]
    travel_gt_advisory: dict[str, Any]
    travel_root_final: dict[str, Any]
    travel_proof_artifact: dict[str, Any]
    travel_audit_entry: dict[str, Any]
    summary: dict[str, Any]


def _condition_matrix() -> list[dict[str, Any]]:
    return [
        {"condition_id": "passport_validity", "status": "ready", "blocks_travel": False},
        {
            "condition_id": "insurance_certificate",
            "status": "expired",
            "blocks_travel": True,
        },
        {
            "condition_id": "payment_receipt",
            "status": "missing",
            "blocks_travel": True,
        },
        {
            "condition_id": "hotel_confirmation",
            "status": "present",
            "blocks_travel": False,
        },
        {
            "condition_id": "route_window",
            "status": "uncertain",
            "blocks_travel": True,
        },
        {
            "condition_id": "user_permission",
            "status": "not_confirmed",
            "blocks_travel": True,
        },
    ]


def validate_applied_travel_readiness_report_consistency(
    report: AppliedTravelReadinessReport,
) -> bool:
    conditions = {row["condition_id"]: row for row in report.travel_condition_matrix}
    blockers = [row for row in report.travel_condition_matrix if row["blocks_travel"]]
    root = report.travel_root_final
    decomposition = report.travel_decomposition_hint
    return all(
        (
            len(conditions) == 6,
            len(blockers) == 4,
            conditions.get("passport_validity", {}).get("blocks_travel") is False,
            conditions.get("hotel_confirmation", {}).get("blocks_travel") is False,
            conditions.get("insurance_certificate", {}).get("status") == "expired",
            conditions.get("payment_receipt", {}).get("status") == "missing",
            conditions.get("route_window", {}).get("status") == "uncertain",
            conditions.get("user_permission", {}).get("status") == "not_confirmed",
            all(
                candidate.get("reuse_type") == "bounded_partial_reuse"
                and candidate.get("marks_travel_ready") is False
                and candidate.get("submits_external_action") is False
                and candidate.get("drs_retrieval_is_not_authority") is True
                for candidate in report.travel_drs_reuse_candidates
            ),
            report.travel_permission_boundary.get("permission_required") is True,
            report.travel_permission_boundary.get("permission_is_not_execution")
            is True,
            report.travel_conflict_report.get("conflict_detected") is True,
            report.travel_conflict_report.get("conflictcheck_is_authority") is False,
            report.travel_gt_advisory.get("gt_recommendation") == "not_ready",
            report.travel_gt_advisory.get("gt_is_advisory") is True,
            report.travel_gt_advisory.get("gt_can_mark_ready") is False,
            decomposition.get("decomposition_hint_present") is True,
            decomposition.get("fractal_dac_not_invoked") is True,
            decomposition.get("child_cells_created") is False,
            decomposition.get("child_authority_granted") is False,
            root.get("root_result") == "not_ready",
            root.get("safe_secondary_outcome") == "needs_user_travel_update",
            all(
                root.get(key) is False
                for key in (
                    "ready_certificate_created",
                    "travel_request_submitted",
                    "booking_created",
                    "payment_executed",
                    "external_action_executed",
                    "direct_ready_override",
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
            ),
            report.travel_audit_entry.get("canonical_payload_hash")
            == canonical_hash(report.travel_proof_artifact),
            report.travel_audit_entry.get("audit_chain_decides_truth") is False,
            report.travel_audit_entry.get("proof_only") is True,
            report.travel_audit_entry.get("production_persistence") is False,
            report.travel_audit_entry.get("global_drs_write") is False,
            report.travel_audit_entry.get("external_drs_write") is False,
        )
    )


def collect_applied_travel_readiness_demo() -> AppliedTravelReadinessReport:
    certificate = collect_applied_certificate_readiness_demo()
    permission = collect_permission_needsuser_ux_proof()
    reuse = collect_applied_drs_retrieval_reuse()
    conflict = collect_conflictcheck()
    audit = collect_audit_hash_chain()

    source = {
        "certificate_readiness_source_status": certificate.summary[
            "applied_certificate_readiness_demo_status"
        ],
        "permission_needsuser_source_status": permission.summary[
            "permission_needsuser_ux_proof_status"
        ],
        "applied_drs_retrieval_reuse_source_status": reuse.summary[
            "applied_drs_retrieval_reuse_status"
        ],
        "conflictcheck_source_status": conflict.summary["conflictcheck_status"],
        "audit_hash_chain_source_status": audit.summary["audit_hash_chain_status"],
    }
    request = {
        "travel_request_id": "TRAVEL-900",
        "itinerary_id": "ITIN-44",
        "request_type": "travel_multi_condition_readiness",
        "proof_only": True,
    }
    evidence = {
        "passport_validity": "valid",
        "insurance_certificate": "expired",
        "payment_receipt": "missing",
        "hotel_confirmation": "present",
        "route_window": "uncertain",
        "user_permission": "not_confirmed",
    }
    conditions = _condition_matrix()
    decomposition = {
        "decomposition_hint_present": True,
        "future_bounded_branches": [
            "document_check",
            "payment_check",
            "lodging_check",
            "route_window_check",
            "permission_check",
        ],
        "fractal_dac_not_invoked": True,
        "child_cells_created": False,
        "child_authority_granted": False,
    }
    reuse_candidates = [
        {
            "retrieval_candidate_id": "travel_reuse_certificate_APP77_CERT310",
            "source_record_id": "certificate_reuse_candidate_APP77_CERT310",
            "source_context": "APP-77/CERT-310",
            "reuse_type": "bounded_partial_reuse",
            "suggested_checks": ["insurance_certificate", "payment_receipt"],
            "marks_travel_ready": False,
            "submits_external_action": False,
            "semantic_similarity_is_not_authority": True,
            "reuse_score_is_not_root": True,
            "drs_retrieval_is_not_authority": True,
        },
        {
            "retrieval_candidate_id": "travel_reuse_certificate_APP78_CERT311",
            "source_record_id": "reuse_candidate_certificate_APP78_CERT311",
            "source_context": "APP-78/CERT-311",
            "reuse_type": "bounded_partial_reuse",
            "suggested_checks": ["insurance_certificate", "payment_receipt"],
            "marks_travel_ready": False,
            "submits_external_action": False,
            "semantic_similarity_is_not_authority": True,
            "reuse_score_is_not_root": True,
            "drs_retrieval_is_not_authority": True,
        },
    ]
    permission_boundary = {
        "permission_required": True,
        "user_permission_status": "not_confirmed",
        "permission_is_not_execution": True,
        "proof_only_approval_is_future_action_permission_only": True,
        "completed_action_created": False,
    }
    conflict_report = {
        "conflict_report_id": "conflict_travel_ready_claim_vs_missing_conditions",
        "conflict_detected": True,
        "reason": (
            "ready_claim_contradicts_expired_missing_uncertain_not_confirmed_conditions"
        ),
        "conflictcheck_is_authority": False,
        "root_review_required": True,
    }
    gt = {
        "gt_recommendation": "not_ready",
        "gt_reason": "blocking_conditions_present",
        "gt_is_advisory": True,
        "gt_can_mark_ready": False,
        "gt_can_execute_action": False,
        "gt_can_submit_travel_request": False,
    }
    root = {
        "root_result": "not_ready",
        "safe_secondary_outcome": "needs_user_travel_update",
        "ready_certificate_created": False,
        "travel_request_submitted": False,
        "booking_created": False,
        "payment_executed": False,
        "external_action_executed": False,
        "direct_ready_override": False,
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
        "root_remains_final_authority": True,
    }
    proof_artifact = {
        "travel_proof_artifact_id": "applied_travel_readiness_TRAVEL900_ITIN44",
        "travel_request": request,
        "travel_evidence": evidence,
        "travel_condition_matrix": conditions,
        "travel_decomposition_hint": decomposition,
        "travel_drs_reuse_candidates": reuse_candidates,
        "travel_permission_boundary": permission_boundary,
        "travel_conflict_report": conflict_report,
        "travel_gt_advisory": gt,
        "travel_root_final": root,
    }
    audit_entry = {
        "audit_entry_id": "audit_applied_travel_TRAVEL900_ITIN44",
        "canonical_payload_hash": canonical_hash(proof_artifact),
        "previous_chain_last_entry_hash": audit.chain_summary["last_entry_hash"],
        "proof_only": True,
        "production_persistence": False,
        "global_drs_write": False,
        "external_drs_write": False,
        "audit_chain_decides_truth": False,
    }
    provisional = AppliedTravelReadinessReport(
        source_evidence=source,
        travel_request=request,
        travel_evidence=evidence,
        travel_condition_matrix=conditions,
        travel_decomposition_hint=decomposition,
        travel_drs_reuse_candidates=reuse_candidates,
        travel_permission_boundary=permission_boundary,
        travel_conflict_report=conflict_report,
        travel_gt_advisory=gt,
        travel_root_final=root,
        travel_proof_artifact=proof_artifact,
        travel_audit_entry=audit_entry,
        summary={},
    )
    consistent = validate_applied_travel_readiness_report_consistency(provisional)
    source_pass = all(status == "PASS" for status in source.values())
    passed = source_pass and consistent
    return replace(
        provisional,
        summary={
            "applied_travel_readiness_demo_status": "PASS" if passed else "FAIL",
            "travel_request_id": "TRAVEL-900",
            "itinerary_id": "ITIN-44",
            "root_result": "not_ready",
            "safe_secondary_outcome": "needs_user_travel_update",
            "blocking_conditions_count": 4,
            "all_blocking_conditions_detected": True,
            "bounded_drs_reuse_observed": True,
            "semantic_similarity_is_not_authority": True,
            "reuse_score_is_not_root": True,
            "drs_retrieval_is_not_authority": True,
            "permission_is_not_execution": True,
            "decomposition_hint_present": True,
            "fractal_dac_not_invoked": True,
            "child_cells_created": False,
            "child_authority_granted": False,
            "gt_remains_advisory_until_root": True,
            "conflictcheck_remains_advisory_until_root": True,
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
            "gemini_called": False,
            "network_called": False,
            "telegram_used": False,
            "marennya_invoked": False,
            "up_invoked": False,
            "ready_for_applied_travel_readiness_tests": passed,
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


def render_applied_travel_readiness_demo(report: AppliedTravelReadinessReport) -> str:
    lines = [
        "[APPLIED TRAVEL READINESS DEMO]",
        "note: deterministic local travel multi-condition readiness proof",
        "note: decomposition hint only; Fractal DAC and child cells are not invoked",
    ]
    _section(lines, "[SOURCE EVIDENCE]", report.source_evidence)
    _section(lines, "[TRAVEL REQUEST]", report.travel_request | report.travel_evidence)
    _rows(lines, "[TRAVEL CONDITION MATRIX]", report.travel_condition_matrix)
    _section(lines, "[DECOMPOSITION HINT]", report.travel_decomposition_hint)
    _rows(lines, "[DRS REUSE]", report.travel_drs_reuse_candidates)
    _section(lines, "[PERMISSION BOUNDARY]", report.travel_permission_boundary)
    _section(lines, "[CONFLICTCHECK]", report.travel_conflict_report)
    _section(lines, "[GT ADVISORY]", report.travel_gt_advisory)
    _section(lines, "[ROOT FINAL]", report.travel_root_final)
    _section(lines, "[AUDIT]", report.travel_audit_entry)
    _section(lines, "[SUMMARY]", report.summary)
    return "\n".join(lines).rstrip() + "\n"


def run_applied_travel_readiness_demo() -> str:
    return render_applied_travel_readiness_demo(collect_applied_travel_readiness_demo())


def main() -> int:
    print(run_applied_travel_readiness_demo(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
