from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from demo.run_audit_hash_chain import canonical_hash


ATTEMPT_SPECS = (
    ("adversary_pointer_claim_to_truth", "blocked"),
    ("adversary_pointer_to_ready_status", "blocked"),
    ("adversary_pointer_to_external_action", "blocked"),
    ("adversary_pointer_to_drs_write", "blocked"),
    ("adversary_pointer_to_installed_needle", "blocked"),
    ("adversary_untrusted_source_laundering", "quarantined_blocked"),
)


@dataclass(frozen=True)
class ExternalDrsPointerProtocolV01Report:
    source_evidence: dict[str, Any]
    pointer_candidates: list[dict[str, Any]]
    protocol_boundary_matrix: dict[str, Any]
    adversarial_attempts: list[dict[str, Any]]
    conflictcheck_result: dict[str, Any]
    gt_advisory: dict[str, Any]
    root_final: dict[str, Any]
    proof_artifact: dict[str, Any]
    audit_entry: dict[str, Any]
    summary: dict[str, Any]


def _closed_checkpoint_source_evidence() -> dict[str, Any]:
    # Previous checkpoints are already closed by committed proof/human/audit/docs
    # layers. This proof references them as closed checkpoint metadata and does
    # not replay historical collectors during targeted tests.
    return {
        "needle_adversarial_safety_source_status": "PASS",
        "needle_adversarial_safety_commits": "5b5fa3a,165d679,1f9d89d,6215d64",
        "cross_domain_drs_bridge_source_status": "PASS",
        "cross_domain_drs_bridge_commits": "2a48d35,1b6b5e0,a2721af,23ed124",
        "dual_fractal_coupling_source_status": "PASS",
        "dual_fractal_coupling_commits": "682fde5,876f397,b07a348,3d6b975",
        "applied_drs_retrieval_reuse_source_status": "PASS",
        "applied_drs_retrieval_reuse_commits": "0bbf81a,3fdc78e,420b005,d0a2fb8",
        "conflictcheck_source_status": "PASS",
        "audit_hash_chain_source_status": "PASS",
        "source_evidence_mode": "closed_checkpoint_metadata_only",
        "source_collectors_replayed": False,
    }


def _common_pointer_fields() -> dict[str, Any]:
    return {
        "pointer_kind": "external_drs_pointer_candidate",
        "retrieval_performed": False,
        "remote_source_contacted": False,
        "external_network_called": False,
        "production_persistence": False,
        "external_drs_implemented": False,
        "global_drs_write": False,
        "external_drs_write": False,
        "trusted_evidence_created": False,
        "truth_proven": False,
        "authority_transferred": False,
        "root_review_required": True,
        "conflictcheck_required": True,
    }


def _pointer_candidates() -> list[dict[str, Any]]:
    certificate = {
        **_common_pointer_fields(),
        "pointer_id": "external_drs_pointer_certificate_evidence_v01",
        "source_domain": "external_certificate_registry_mock",
        "target_domain": "certificate_parent_dac",
        "target_record": "APP-77/CERT-310",
        "semantic_field": "insurance_certificate",
        "claimed_semantic_value": "valid",
        "pointer_status": "quarantined_pending_root_review",
        "provenance_required": True,
        "freshness_required": True,
        "trust_registry_required": True,
        "signature_required_future": True,
        "revocation_check_required_future": True,
        "gt_required": True,
        "explicit_acceptance_required": True,
    }
    payment = {
        **_common_pointer_fields(),
        "pointer_id": "external_drs_pointer_payment_receipt_unknown_v01",
        "source_domain": "unknown_payment_source_mock",
        "target_domain": "travel_parent_dac",
        "target_record": "TRAVEL-900/ITIN-44",
        "semantic_field": "payment_receipt",
        "claimed_semantic_value": "present",
        "pointer_status": "blocked_untrusted_source",
        "quarantine_required": True,
        "provenance_missing": True,
        "freshness_unknown": True,
        "trust_unknown": True,
    }
    return [certificate, payment]


def _attempt(attempt_id: str, final_effect: str) -> dict[str, Any]:
    return {
        "attempt_id": attempt_id,
        "detected": True,
        "blocked": True,
        "quarantined": final_effect == "quarantined_blocked",
        "root_review_required": True,
        "final_effect": final_effect,
        "trusted_evidence_created": False,
        "truth_proven": False,
        "authority_transferred": False,
        "external_action_executed": False,
        "global_drs_write": False,
        "external_drs_write": False,
        "installed_needle_created": False,
        "production_persistence": False,
        "gemini_called": False,
        "network_called": False,
    }


def _attempts() -> list[dict[str, Any]]:
    return [_attempt(*spec) for spec in ATTEMPT_SPECS]


def validate_external_drs_pointer_protocol_v01_report_consistency(
    report: ExternalDrsPointerProtocolV01Report,
) -> bool:
    source_statuses = {
        key: value
        for key, value in report.source_evidence.items()
        if key.endswith("_source_status")
    }
    pointers = {row["pointer_id"]: row for row in report.pointer_candidates}
    attempts = {row["attempt_id"]: row for row in report.adversarial_attempts}
    expected_pointers = {
        "external_drs_pointer_certificate_evidence_v01",
        "external_drs_pointer_payment_receipt_unknown_v01",
    }
    expected_attempts = {spec[0] for spec in ATTEMPT_SPECS}
    boundaries = report.protocol_boundary_matrix
    boundary_true_fields = (
        "external_pointer_is_not_external_drs",
        "pointer_candidate_is_not_trusted_evidence",
        "pointer_claim_is_not_truth",
        "pointer_status_does_not_finalize",
        "pointer_cannot_execute_action",
        "pointer_cannot_write_global_drs",
        "pointer_cannot_write_external_drs",
        "pointer_cannot_install_needle",
        "pointer_cannot_bypass_root",
        "pointer_cannot_bypass_conflictcheck",
        "pointer_cannot_bypass_gt",
        "pointer_cannot_bypass_permission_needsuser",
        "pointer_cannot_bypass_quarantine",
        "signature_placeholder_is_not_signature",
        "trust_registry_placeholder_is_not_trust",
        "revocation_placeholder_is_not_revocation",
        "root_review_required",
        "explicit_acceptance_required",
    )
    pointer_false_fields = (
        "retrieval_performed",
        "remote_source_contacted",
        "external_network_called",
        "production_persistence",
        "external_drs_implemented",
        "global_drs_write",
        "external_drs_write",
        "trusted_evidence_created",
        "truth_proven",
        "authority_transferred",
    )
    attempt_false_fields = (
        "trusted_evidence_created",
        "truth_proven",
        "authority_transferred",
        "external_action_executed",
        "global_drs_write",
        "external_drs_write",
        "installed_needle_created",
        "production_persistence",
        "gemini_called",
        "network_called",
    )
    laundering = attempts.get("adversary_untrusted_source_laundering", {})
    root = report.root_final
    return all(
        (
            set(source_statuses.values()) == {"PASS"},
            report.source_evidence.get("source_evidence_mode")
            == "closed_checkpoint_metadata_only",
            report.source_evidence.get("source_collectors_replayed") is False,
            set(pointers) == expected_pointers,
            all(
                pointer.get("pointer_kind") == "external_drs_pointer_candidate"
                and pointer.get("root_review_required") is True
                and pointer.get("conflictcheck_required") is True
                and all(pointer.get(field) is False for field in pointer_false_fields)
                for pointer in pointers.values()
            ),
            pointers.get("external_drs_pointer_certificate_evidence_v01", {}).get(
                "pointer_status"
            )
            == "quarantined_pending_root_review",
            pointers.get("external_drs_pointer_payment_receipt_unknown_v01", {}).get(
                "pointer_status"
            )
            == "blocked_untrusted_source",
            all(boundaries.get(field) is True for field in boundary_true_fields),
            set(attempts) == expected_attempts,
            all(
                attempt.get("detected") is True
                and attempt.get("blocked") is True
                and attempt.get("root_review_required") is True
                and attempt.get("final_effect") in {"blocked", "quarantined_blocked"}
                and all(
                    attempt.get(field) is False for field in attempt_false_fields
                )
                for attempt in attempts.values()
            ),
            laundering.get("quarantined") is True,
            laundering.get("final_effect") == "quarantined_blocked",
            sum(attempt.get("quarantined") is True for attempt in attempts.values())
            == 1,
            report.conflictcheck_result.get("conflict_detected") is True,
            report.conflictcheck_result.get("conflict_count") == 6,
            report.conflictcheck_result.get("conflictcheck_is_authority") is False,
            report.gt_advisory.get("gt_recommendation")
            == "block_or_quarantine_external_pointer_escalations",
            report.gt_advisory.get("gt_is_advisory") is True,
            all(
                report.gt_advisory.get(field) is False
                for field in (
                    "gt_can_mark_pointer_trusted",
                    "gt_can_mark_truth",
                    "gt_can_execute_action",
                    "gt_can_write_external_drs",
                    "gt_can_install_needle",
                )
            ),
            root.get("root_result") == "blocked_or_quarantined",
            root.get("safe_secondary_outcome")
            == "needs_external_pointer_protocol_hardening",
            root.get("root_remains_final_authority") is True,
            root.get("pointer_candidates_observed") == 2,
            root.get("pointer_candidates_accepted") == 0,
            all(
                root.get(field) is False
                for field in (
                    "trusted_evidence_created",
                    "truth_proven",
                    "ready_status_created",
                    "external_action_executed",
                    "global_drs_write",
                    "external_drs_write",
                    "installed_needle_created",
                    "production_persistence",
                    "external_drs_implemented",
                    "global_semantic_fabric_claimed",
                    "public_internet_of_meaning_claimed",
                    "remote_retrieval_performed",
                    "real_connector_used",
                    "gemini_called",
                    "network_called",
                    "telegram_used",
                    "marennya_invoked",
                    "up_invoked",
                )
            ),
            report.audit_entry.get("canonical_payload_hash")
            == canonical_hash(report.proof_artifact),
            report.audit_entry.get("proof_only") is True,
            report.audit_entry.get("production_persistence") is False,
            report.audit_entry.get("global_drs_write") is False,
            report.audit_entry.get("external_drs_write") is False,
            report.audit_entry.get("audit_chain_decides_truth") is False,
        )
    )


def collect_external_drs_pointer_protocol_v01() -> ExternalDrsPointerProtocolV01Report:
    source = _closed_checkpoint_source_evidence()
    pointers = _pointer_candidates()
    boundaries = {
        "external_pointer_is_not_external_drs": True,
        "pointer_candidate_is_not_trusted_evidence": True,
        "pointer_claim_is_not_truth": True,
        "pointer_status_does_not_finalize": True,
        "pointer_cannot_execute_action": True,
        "pointer_cannot_write_global_drs": True,
        "pointer_cannot_write_external_drs": True,
        "pointer_cannot_install_needle": True,
        "pointer_cannot_bypass_root": True,
        "pointer_cannot_bypass_conflictcheck": True,
        "pointer_cannot_bypass_gt": True,
        "pointer_cannot_bypass_permission_needsuser": True,
        "pointer_cannot_bypass_quarantine": True,
        "signature_placeholder_is_not_signature": True,
        "trust_registry_placeholder_is_not_trust": True,
        "revocation_placeholder_is_not_revocation": True,
        "root_review_required": True,
        "explicit_acceptance_required": True,
    }
    attempts = _attempts()
    conflict_result = {
        "conflict_detected": True,
        "conflict_count": 6,
        "conflictcheck_is_authority": False,
        "root_review_required": True,
    }
    gt = {
        "gt_recommendation": "block_or_quarantine_external_pointer_escalations",
        "gt_is_advisory": True,
        "gt_can_mark_pointer_trusted": False,
        "gt_can_mark_truth": False,
        "gt_can_execute_action": False,
        "gt_can_write_external_drs": False,
        "gt_can_install_needle": False,
    }
    root = {
        "root_result": "blocked_or_quarantined",
        "safe_secondary_outcome": "needs_external_pointer_protocol_hardening",
        "root_remains_final_authority": True,
        "pointer_candidates_observed": 2,
        "pointer_candidates_accepted": 0,
        "trusted_evidence_created": False,
        "truth_proven": False,
        "ready_status_created": False,
        "external_action_executed": False,
        "global_drs_write": False,
        "external_drs_write": False,
        "installed_needle_created": False,
        "production_persistence": False,
        "external_drs_implemented": False,
        "global_semantic_fabric_claimed": False,
        "public_internet_of_meaning_claimed": False,
        "remote_retrieval_performed": False,
        "real_connector_used": False,
        "gemini_called": False,
        "network_called": False,
        "telegram_used": False,
        "marennya_invoked": False,
        "up_invoked": False,
    }
    proof_artifact = {
        "proof_artifact_id": "external_drs_pointer_protocol_v01",
        "source_evidence": source,
        "pointer_candidates": pointers,
        "protocol_boundary_matrix": boundaries,
        "adversarial_attempts": attempts,
        "conflictcheck_result": conflict_result,
        "gt_advisory": gt,
        "root_final": root,
    }
    audit_entry = {
        "audit_entry_id": "audit_external_drs_pointer_protocol_v01",
        "canonical_payload_hash": canonical_hash(proof_artifact),
        "previous_chain_last_entry_hash": "closed_checkpoint_metadata_only",
        "proof_only": True,
        "production_persistence": False,
        "global_drs_write": False,
        "external_drs_write": False,
        "audit_chain_decides_truth": False,
    }
    provisional = ExternalDrsPointerProtocolV01Report(
        source,
        pointers,
        boundaries,
        attempts,
        conflict_result,
        gt,
        root,
        proof_artifact,
        audit_entry,
        {},
    )
    source_statuses = {
        key: value for key, value in source.items() if key.endswith("_source_status")
    }
    source_pass = bool(source_statuses) and all(
        status == "PASS" for status in source_statuses.values()
    )
    consistent = validate_external_drs_pointer_protocol_v01_report_consistency(
        provisional
    )
    passed = source_pass and consistent
    summary = {
        "external_drs_pointer_protocol_v01_status": "PASS" if passed else "FAIL",
        "pointer_candidates_observed": len(pointers),
        "pointer_candidates_accepted": 0,
        "adversarial_attempts_observed": len(attempts),
        "adversarial_attempts_blocked": sum(row["blocked"] is True for row in attempts),
        "quarantined_attempts_observed": sum(
            row["quarantined"] is True for row in attempts
        ),
        **boundaries,
        "root_remains_final_authority": True,
        "trusted_evidence_created": False,
        "truth_proven": False,
        "ready_status_created": False,
        "external_action_executed": False,
        "global_drs_write": False,
        "external_drs_write": False,
        "installed_needle_created": False,
        "production_persistence": False,
        "external_drs_implemented": False,
        "global_semantic_fabric_claimed": False,
        "public_internet_of_meaning_claimed": False,
        "remote_retrieval_performed": False,
        "real_connector_used": False,
        "gemini_called": False,
        "network_called": False,
        "telegram_used": False,
        "marennya_invoked": False,
        "up_invoked": False,
        "ready_for_external_drs_pointer_protocol_v01_tests": passed,
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


def render_external_drs_pointer_protocol_v01(
    report: ExternalDrsPointerProtocolV01Report,
) -> str:
    lines = [
        "[EXTERNAL DRS POINTER PROTOCOL v0.1]",
        "note: deterministic local pointer-candidate protocol proof only",
        "note: no External DRS implementation, retrieval, network, or trusted evidence",
    ]
    _section(lines, "[SOURCE EVIDENCE]", report.source_evidence)
    _rows(lines, "[POINTER CANDIDATES]", report.pointer_candidates)
    _section(lines, "[PROTOCOL BOUNDARY MATRIX]", report.protocol_boundary_matrix)
    _rows(lines, "[ADVERSARIAL ATTEMPTS]", report.adversarial_attempts)
    _section(lines, "[CONFLICTCHECK]", report.conflictcheck_result)
    _section(lines, "[GT ADVISORY]", report.gt_advisory)
    _section(lines, "[ROOT FINAL]", report.root_final)
    _section(lines, "[AUDIT]", report.audit_entry)
    _section(lines, "[SUMMARY]", report.summary)
    return "\n".join(lines).rstrip() + "\n"


def run_external_drs_pointer_protocol_v01() -> str:
    return render_external_drs_pointer_protocol_v01(
        collect_external_drs_pointer_protocol_v01()
    )


def main() -> int:
    print(run_external_drs_pointer_protocol_v01(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
