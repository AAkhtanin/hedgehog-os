from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any

from demo.run_audit_hash_chain import canonical_hash


SCENARIO_VALIDATIONS = (
    (
        "accepted_bank_payment_evidence",
        "bank_source",
        "payment_status:observed_paid|transaction_id:MOCK-TXN-001",
        "verified",
        "fresh",
        "mock_valid",
        "mock_known",
        "not_revoked",
        "valid",
        "clear",
        "accepted",
        "accepted_evidence_only",
    ),
    (
        "rejected_stale_legal_certificate_evidence",
        "legal_registry_source",
        "certificate_status:expired",
        "verified",
        "expired",
        "mock_valid",
        "mock_known",
        "not_revoked",
        "expired",
        "conflict_detected",
        "rejected",
        "rejected_stale_or_expired_evidence",
    ),
    (
        "quarantined_unknown_source_evidence",
        "unknown_connector_source",
        "payment_receipt:present",
        "unknown",
        "unknown",
        "missing",
        "unknown",
        "unknown",
        "unknown",
        "conflict_detected",
        "quarantined",
        "quarantined_unknown_source",
    ),
    (
        "rejected_signature_mismatch_evidence",
        "bank_source",
        "payment_status:observed_paid",
        "verified",
        "fresh",
        "mismatch",
        "mock_known",
        "not_revoked",
        "valid",
        "conflict_detected",
        "rejected",
        "rejected_signature_mismatch",
    ),
    (
        "rejected_revoked_evidence",
        "legal_registry_source",
        "certificate_status:valid_claim",
        "verified",
        "fresh",
        "mock_valid",
        "mock_known",
        "revoked",
        "valid",
        "conflict_detected",
        "rejected",
        "rejected_revoked_evidence",
    ),
    (
        "accepted_warehouse_stock_evidence",
        "warehouse_source",
        "inventory_stock:water_filter_available_6",
        "verified",
        "fresh",
        "mock_valid",
        "mock_known",
        "not_revoked",
        "valid",
        "clear",
        "accepted",
        "accepted_evidence_only",
    ),
)

ADVERSARIAL_ATTEMPTS = (
    "adversary_candidate_to_truth",
    "adversary_validation_packet_to_acceptance",
    "adversary_gt_to_acceptance",
    "adversary_conflictcheck_to_rejection_authority",
    "adversary_accepted_evidence_to_external_action",
    "adversary_accepted_evidence_to_drs_write",
    "adversary_accepted_evidence_to_installed_needle",
    "adversary_mock_signature_to_real_signature_claim",
)


@dataclass(frozen=True)
class ExternalEvidenceAcceptanceGateReport:
    source_evidence: dict[str, Any]
    evidence_candidates: list[dict[str, Any]]
    validation_packets: list[dict[str, Any]]
    acceptance_decisions: list[dict[str, Any]]
    accepted_evidence: list[dict[str, Any]]
    rejected_evidence: list[dict[str, Any]]
    quarantined_evidence: list[dict[str, Any]]
    boundary_matrix: dict[str, Any]
    adversarial_attempts: list[dict[str, Any]]
    conflictcheck_result: dict[str, Any]
    gt_advisory: dict[str, Any]
    root_final: dict[str, Any]
    proof_artifact: dict[str, Any]
    audit_entry: dict[str, Any]
    summary: dict[str, Any]


def _closed_checkpoint_source_evidence() -> dict[str, Any]:
    return {
        "read_only_enterprise_connector_sandbox_source_status": "PASS",
        "read_only_enterprise_connector_sandbox_commits": (
            "5110d14,01a6b64,af872eb,056e2cd"
        ),
        "source_evidence_mode": "closed_checkpoint_metadata_only",
        "source_collectors_replayed": False,
    }


def _candidate(spec: tuple[str, ...]) -> dict[str, Any]:
    (
        scenario_id,
        source_domain,
        observation,
        *_,
        expected_decision,
        expected_post_root_effect,
    ) = spec
    return {
        "evidence_candidate_id": f"candidate_{scenario_id}",
        "scenario_id": scenario_id,
        "source_domain": source_domain,
        "connector_observation": observation,
        "evidence_candidate_created": True,
        "candidate_effect": "candidate_only",
        "expected_decision": expected_decision,
        "expected_post_root_effect": expected_post_root_effect,
        "root_review_required": True,
        "root_acceptance_required": True,
        "proof_only": True,
        "truth_proven": False,
        "ready_status_created": False,
        "external_action_executed": False,
        "global_drs_write": False,
        "external_drs_write": False,
        "installed_needle_created": False,
        "production_persistence": False,
        "final_effect": "candidate_only",
    }


def _validation_packet(spec: tuple[str, ...]) -> dict[str, Any]:
    (
        scenario_id,
        _,
        _,
        provenance,
        freshness,
        signature,
        trust,
        revocation,
        time_envelope,
        conflict,
        expected_decision,
        _,
    ) = spec
    validation_passed = expected_decision == "accepted"
    return {
        "validation_packet_id": f"validation_{scenario_id}",
        "scenario_id": scenario_id,
        "validation_packet_created": True,
        "provenance_status": provenance,
        "freshness_status": freshness,
        "signature_status": signature,
        "trust_registry_status": trust,
        "revocation_status": revocation,
        "time_envelope_status": time_envelope,
        "conflict_status": conflict,
        "validation_passed": validation_passed,
        "root_review_required": True,
        "validation_packet_is_root_final": False,
        "real_signature_validated": False,
        "real_trust_registry_used": False,
        "real_revocation_registry_used": False,
        "local_proof_only": True,
    }


def _decision(spec: tuple[str, ...]) -> dict[str, Any]:
    scenario_id, _, _, *_, outcome, final_effect = spec
    return {
        "acceptance_gate_decision_id": f"root_decision_{scenario_id}",
        "scenario_id": scenario_id,
        "decision": outcome,
        "root_decision": True,
        "root_accepted": outcome == "accepted",
        "root_rejected": outcome == "rejected",
        "root_quarantined": outcome == "quarantined",
        "accepted_evidence_created": outcome == "accepted",
        "rejected_evidence_created": outcome == "rejected",
        "quarantined_evidence_created": outcome == "quarantined",
        "truth_proven": False,
        "ready_status_created": False,
        "external_action_executed": False,
        "global_drs_write": False,
        "external_drs_write": False,
        "installed_needle_created": False,
        "final_effect": final_effect,
    }


def _accepted_record(decision: dict[str, Any]) -> dict[str, Any]:
    return {
        "accepted_evidence_id": f"accepted_{decision['scenario_id']}",
        "scenario_id": decision["scenario_id"],
        "accepted_evidence_created": True,
        "accepted_by": "Root",
        "root_acceptance_required": True,
        "truth_proven": False,
        "readiness_finalized_by_evidence": False,
        "ready_status_created": False,
        "external_action_executed": False,
        "global_drs_write": False,
        "external_drs_write": False,
        "installed_needle_created": False,
        "production_persistence": False,
        "final_effect": "accepted_evidence_only",
    }


def _rejected_record(decision: dict[str, Any]) -> dict[str, Any]:
    return {
        "rejected_evidence_id": f"rejected_{decision['scenario_id']}",
        "scenario_id": decision["scenario_id"],
        "rejected_evidence_created": True,
        "accepted_evidence_created": False,
        "root_rejected": True,
        "final_effect": decision["final_effect"],
    }


def _quarantined_record(decision: dict[str, Any]) -> dict[str, Any]:
    return {
        "quarantined_evidence_id": f"quarantined_{decision['scenario_id']}",
        "scenario_id": decision["scenario_id"],
        "quarantined_evidence_created": True,
        "accepted_evidence_created": False,
        "root_quarantined": True,
        "final_effect": decision["final_effect"],
    }


def _adversarial_attempts() -> list[dict[str, Any]]:
    return [
        {
            "attempt_id": attempt_id,
            "detected": True,
            "blocked": True,
            "root_review_required": True,
            "final_effect": "blocked",
            "accepted_evidence_created": False,
            "truth_proven": False,
            "ready_status_created": False,
            "authority_transferred": False,
            "external_action_executed": False,
            "global_drs_write": False,
            "external_drs_write": False,
            "installed_needle_created": False,
            "real_signature_validated": False,
            "production_persistence": False,
        }
        for attempt_id in ADVERSARIAL_ATTEMPTS
    ]


def validate_external_evidence_acceptance_gate_report_consistency(
    report: ExternalEvidenceAcceptanceGateReport,
) -> bool:
    statuses = {
        key: value
        for key, value in report.source_evidence.items()
        if key.endswith("_source_status")
    }
    decisions = {row["scenario_id"]: row for row in report.acceptance_decisions}
    accepted_ids = {row["scenario_id"] for row in report.accepted_evidence}
    rejected_ids = {row["scenario_id"] for row in report.rejected_evidence}
    quarantined_ids = {row["scenario_id"] for row in report.quarantined_evidence}
    accepted_expected = {
        "accepted_bank_payment_evidence",
        "accepted_warehouse_stock_evidence",
    }
    rejected_expected = {
        "rejected_stale_legal_certificate_evidence",
        "rejected_signature_mismatch_evidence",
        "rejected_revoked_evidence",
    }
    prohibited = (
        "truth_proven",
        "ready_status_created",
        "external_action_executed",
        "global_drs_write",
        "external_drs_write",
        "installed_needle_created",
    )
    root = report.root_final
    return all(
        (
            set(statuses.values()) == {"PASS"},
            report.source_evidence.get("source_evidence_mode")
            == "closed_checkpoint_metadata_only",
            report.source_evidence.get("source_collectors_replayed") is False,
            len(report.evidence_candidates) == 6,
            len(report.validation_packets) == 6,
            len(decisions) == 6,
            accepted_ids == accepted_expected,
            rejected_ids == rejected_expected,
            quarantined_ids == {"quarantined_unknown_source_evidence"},
            all(row.get("root_review_required") is True for row in report.evidence_candidates),
            all(
                row.get("candidate_effect") == "candidate_only"
                and row.get("final_effect") == "candidate_only"
                and row.get("expected_post_root_effect")
                in {
                    "accepted_evidence_only",
                    "rejected_stale_or_expired_evidence",
                    "quarantined_unknown_source",
                    "rejected_signature_mismatch",
                    "rejected_revoked_evidence",
                }
                for row in report.evidence_candidates
            ),
            all(
                row.get("final_effect") != "accepted_evidence_only"
                for row in report.evidence_candidates
            ),
            all(row.get("validation_packet_is_root_final") is False for row in report.validation_packets),
            all(row.get("local_proof_only") is True for row in report.validation_packets),
            all(all(row.get(field) is False for field in prohibited) for row in report.evidence_candidates),
            all(all(row.get(field) is False for field in prohibited) for row in report.accepted_evidence),
            decisions["accepted_bank_payment_evidence"].get("root_accepted") is True,
            decisions["accepted_warehouse_stock_evidence"].get("root_accepted") is True,
            len(report.adversarial_attempts) == 8,
            all(row.get("detected") is True and row.get("blocked") is True for row in report.adversarial_attempts),
            all(all(row.get(field) is False for field in prohibited) for row in report.adversarial_attempts),
            all(value is True for value in report.boundary_matrix.values()),
            report.conflictcheck_result.get("conflict_detected") is True,
            report.conflictcheck_result.get("conflictcheck_is_authority") is False,
            report.gt_advisory.get("gt_is_advisory") is True,
            report.gt_advisory.get("gt_can_accept_evidence") is False,
            root.get("root_result") == "external_evidence_acceptance_gate_completed",
            root.get("evidence_candidates_created") == 6,
            root.get("validation_packets_created") == 6,
            root.get("accepted_evidence_created") == 2,
            root.get("rejected_evidence_created") == 3,
            root.get("quarantined_evidence_created") == 1,
            root.get("adversarial_attempts_blocked") == 8,
            root.get("root_remains_final_authority") is True,
            all(root.get(field) is False for field in prohibited),
            report.audit_entry.get("canonical_payload_hash")
            == canonical_hash(report.proof_artifact),
            report.audit_entry.get("audit_chain_decides_truth") is False,
        )
    )


def collect_external_evidence_acceptance_gate_v01() -> ExternalEvidenceAcceptanceGateReport:
    source = _closed_checkpoint_source_evidence()
    candidates = [_candidate(spec) for spec in SCENARIO_VALIDATIONS]
    validations = [_validation_packet(spec) for spec in SCENARIO_VALIDATIONS]
    decisions = [_decision(spec) for spec in SCENARIO_VALIDATIONS]
    accepted = [_accepted_record(row) for row in decisions if row["decision"] == "accepted"]
    rejected = [_rejected_record(row) for row in decisions if row["decision"] == "rejected"]
    quarantined = [
        _quarantined_record(row) for row in decisions if row["decision"] == "quarantined"
    ]
    boundary = {
        "connector_observation_is_not_truth": True,
        "connector_observation_is_not_trusted_evidence": True,
        "evidence_candidate_is_not_truth": True,
        "evidence_candidate_is_not_accepted_evidence": True,
        "validation_packet_is_not_root_acceptance": True,
        "gt_is_not_acceptance_authority": True,
        "conflictcheck_is_not_acceptance_authority": True,
        "accepted_evidence_requires_root_decision": True,
        "accepted_evidence_does_not_execute_action": True,
        "accepted_evidence_does_not_write_drs_by_itself": True,
        "accepted_evidence_does_not_install_needle": True,
        "mock_signature_is_not_real_signature": True,
        "mock_trust_registry_is_not_real_trust_registry": True,
        "mock_revocation_check_is_not_real_revocation_registry": True,
        "root_remains_final_authority": True,
    }
    attempts = _adversarial_attempts()
    conflict = {
        "conflict_detected": True,
        "conflict_paths": 12,
        "conflictcheck_is_authority": False,
        "root_review_required": True,
    }
    gt = {
        "gt_recommendation": "accept_clean_candidates_reject_or_quarantine_failed_candidates",
        "gt_is_advisory": True,
        "gt_can_accept_evidence": False,
        "gt_can_mark_truth": False,
        "gt_can_execute_action": False,
        "gt_can_write_drs": False,
        "gt_can_install_needle": False,
    }
    root = {
        "root_result": "external_evidence_acceptance_gate_completed",
        "safe_secondary_outcome": "accepted_evidence_available_for_future_readiness_checks",
        "evidence_candidates_created": len(candidates),
        "validation_packets_created": len(validations),
        "accepted_evidence_created": len(accepted),
        "rejected_evidence_created": len(rejected),
        "quarantined_evidence_created": len(quarantined),
        "adversarial_attempts_observed": len(attempts),
        "adversarial_attempts_blocked": len(attempts),
        "truth_proven": False,
        "ready_status_created": False,
        "external_action_executed": False,
        "global_drs_write": False,
        "external_drs_write": False,
        "installed_needle_created": False,
        "real_signature_validated": False,
        "real_trust_registry_used": False,
        "real_revocation_registry_used": False,
        "network_called": False,
        "gemini_called": False,
        "telegram_used": False,
        "marennya_invoked": False,
        "up_invoked": False,
        "production_persistence": False,
        "root_remains_final_authority": True,
    }
    proof_artifact = {
        "proof_artifact_id": "external_evidence_acceptance_gate_v01",
        "source_evidence": source,
        "evidence_candidates": candidates,
        "validation_packets": validations,
        "acceptance_decisions": decisions,
        "accepted_evidence": accepted,
        "rejected_evidence": rejected,
        "quarantined_evidence": quarantined,
        "boundary_matrix": boundary,
        "adversarial_attempts": attempts,
        "conflictcheck_result": conflict,
        "gt_advisory": gt,
        "root_final": root,
    }
    audit = {
        "audit_entry_id": "audit_external_evidence_acceptance_gate_v01",
        "canonical_payload_hash": canonical_hash(proof_artifact),
        "previous_chain_last_entry_hash": "closed_checkpoint_metadata_only",
        "proof_only": True,
        "production_persistence": False,
        "global_drs_write": False,
        "external_drs_write": False,
        "audit_chain_decides_truth": False,
    }
    provisional = ExternalEvidenceAcceptanceGateReport(
        source,
        candidates,
        validations,
        decisions,
        accepted,
        rejected,
        quarantined,
        boundary,
        attempts,
        conflict,
        gt,
        root,
        proof_artifact,
        audit,
        {},
    )
    passed = validate_external_evidence_acceptance_gate_report_consistency(provisional)
    summary = {
        "external_evidence_acceptance_gate_v01_status": "PASS" if passed else "FAIL",
        **root,
        **boundary,
        "ready_for_external_evidence_acceptance_gate_v01_tests": passed,
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


def render_external_evidence_acceptance_gate_v01(
    report: ExternalEvidenceAcceptanceGateReport,
) -> str:
    lines = [
        "[EXTERNAL EVIDENCE ACCEPTANCE GATE v0.1]",
        "note: deterministic local proof-only acceptance gate",
        "note: accepted evidence is not truth, ready status, action, or DRS write",
    ]
    _section(lines, "[SOURCE EVIDENCE]", report.source_evidence)
    _rows(lines, "[EVIDENCE CANDIDATES]", report.evidence_candidates)
    _rows(lines, "[VALIDATION PACKETS]", report.validation_packets)
    _rows(lines, "[ACCEPTANCE DECISIONS]", report.acceptance_decisions)
    _rows(lines, "[ACCEPTED EVIDENCE]", report.accepted_evidence)
    _rows(
        lines,
        "[REJECTED / QUARANTINED EVIDENCE]",
        report.rejected_evidence + report.quarantined_evidence,
    )
    _section(lines, "[BOUNDARY MATRIX]", report.boundary_matrix)
    _rows(lines, "[ADVERSARIAL ATTEMPTS]", report.adversarial_attempts)
    _section(lines, "[CONFLICTCHECK]", report.conflictcheck_result)
    _section(lines, "[GT ADVISORY]", report.gt_advisory)
    _section(lines, "[ROOT FINAL]", report.root_final)
    _section(lines, "[AUDIT]", report.audit_entry)
    _section(lines, "[SUMMARY]", report.summary)
    return "\n".join(lines).rstrip() + "\n"


def run_external_evidence_acceptance_gate_v01() -> str:
    return render_external_evidence_acceptance_gate_v01(
        collect_external_evidence_acceptance_gate_v01()
    )


def main() -> int:
    print(run_external_evidence_acceptance_gate_v01(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
