from __future__ import annotations

from demo.run_external_evidence_acceptance_gate_v01 import (
    collect_external_evidence_acceptance_gate_v01,
)


def render_human_external_evidence_acceptance_gate_walkthrough_v01(report) -> str:
    source = report.source_evidence
    validations = {row["scenario_id"]: row for row in report.validation_packets}
    decisions = {row["scenario_id"]: row for row in report.acceptance_decisions}
    attempts = {row["attempt_id"]: row for row in report.adversarial_attempts}
    conflict = report.conflictcheck_result
    gt = report.gt_advisory
    root = report.root_final

    lines = [
        "HEDGEHOG OS — HUMAN EXTERNAL EVIDENCE ACCEPTANCE GATE WALKTHROUGH v0.1",
        "",
        "1. WHAT THIS DEMO IS",
        "",
        "This is a human-readable walkthrough over the committed External Evidence "
        "Acceptance Gate v0.1 proof. It is a deterministic local proof-only acceptance "
        "gate.",
        "",
        "There is no External DRS implementation, real connector/API access, network, "
        "Gemini, production persistence, external action, installed Needle, Marennya, "
        "or UP.",
        "",
        "Validation is mock proof-level validation only. It is not real cryptographic "
        "signature validation, a real trust registry, or a real revocation registry.",
        "",
        "2. WHY THIS LAYER MATTERS",
        "",
        "Read-only Enterprise Connector Sandbox proved that connector responses can be "
        "observed but not trusted.",
        "",
        "This layer proves the next boundary: a ConnectorObservation can become an "
        "EvidenceCandidate, and only a Root-reviewed, validation-passing candidate can "
        "become AcceptedEvidence.",
        "",
        "This is one of the key layers required before a clean enterprise success path "
        "can exist in the future Enterprise Killer Demo. It remains local proof-level "
        "infrastructure, not production trust.",
        "",
        "3. SOURCE EVIDENCE MODE",
        "",
        "The prior Read-only Enterprise Connector Sandbox checkpoint is referenced as "
        "closed checkpoint metadata.",
        f"source_evidence_mode={source['source_evidence_mode']}.",
        f"source_collectors_replayed={str(source['source_collectors_replayed']).lower()}.",
        "",
        "This is targeted proof runtime hygiene, not full historical replay. Full "
        "historical replay belongs to explicit audit or super-smoke modes.",
        "",
        "4. ACCEPTANCE FLOW",
        "",
        "ConnectorObservation -> EvidenceCandidate -> ValidationPacket -> RootDecision "
        "-> AcceptedEvidence / RejectedEvidence / QuarantinedEvidence.",
        "",
        "ConnectorObservation is not truth.",
        "ConnectorObservation is not trusted evidence.",
        "EvidenceCandidate is not accepted evidence.",
        "EvidenceCandidate remains candidate_only until Root decision.",
        "ValidationPacket is not Root acceptance or Root final.",
        "GT is advisory.",
        "ConflictCheck is not authority.",
        "AcceptedEvidence is created only by Root decision.",
        "",
        "5. SIX EVIDENCE SCENARIOS",
        "",
        "accepted_bank_payment_evidence:",
        "bank_source reports payment_status observed_paid with MOCK-TXN-001.",
        f"Validation: provenance={validations['accepted_bank_payment_evidence']['provenance_status']}, "
        f"freshness={validations['accepted_bank_payment_evidence']['freshness_status']}, "
        f"signature={validations['accepted_bank_payment_evidence']['signature_status']}, "
        f"trust={validations['accepted_bank_payment_evidence']['trust_registry_status']}, "
        f"revocation={validations['accepted_bank_payment_evidence']['revocation_status']}, "
        f"time_envelope={validations['accepted_bank_payment_evidence']['time_envelope_status']}, "
        f"conflict={validations['accepted_bank_payment_evidence']['conflict_status']}.",
        f"Root decision: {decisions['accepted_bank_payment_evidence']['decision']}. "
        "It creates AcceptedEvidence only; it proves no truth, creates no ready status, "
        "executes no action, and writes no DRS.",
        "",
        "rejected_stale_legal_certificate_evidence:",
        "The legal certificate is expired. Freshness and time envelope are expired, "
        "and conflict is detected.",
        f"Root decision: {decisions['rejected_stale_legal_certificate_evidence']['decision']}. "
        "accepted_evidence_created=false.",
        "",
        "quarantined_unknown_source_evidence:",
        "An unknown source claims payment_receipt present. Provenance, freshness, "
        "trust, revocation, and time envelope are unknown; signature is missing; "
        "conflict is detected.",
        f"Root decision: {decisions['quarantined_unknown_source_evidence']['decision']}.",
        "",
        "rejected_signature_mismatch_evidence:",
        "The claim is otherwise fresh, but signature_status=mismatch.",
        f"Root decision: {decisions['rejected_signature_mismatch_evidence']['decision']}. "
        "real_signature_validated=false.",
        "",
        "rejected_revoked_evidence:",
        "The claim is otherwise clean, but revocation_status=revoked.",
        f"Root decision: {decisions['rejected_revoked_evidence']['decision']}.",
        "",
        "accepted_warehouse_stock_evidence:",
        "The warehouse inventory signal validates cleanly.",
        f"Root decision: {decisions['accepted_warehouse_stock_evidence']['decision']}. "
        "It creates AcceptedEvidence only; readiness_finalized_by_evidence=false and "
        "ready_status_created=false.",
        "",
        "6. ACCEPTED / REJECTED / QUARANTINED COUNTS",
        "",
        f"Evidence candidates created: {root['evidence_candidates_created']}.",
        f"Validation packets created: {root['validation_packets_created']}.",
        f"Accepted evidence created: {root['accepted_evidence_created']}.",
        f"Rejected evidence created: {root['rejected_evidence_created']}.",
        f"Quarantined evidence created: {root['quarantined_evidence_created']}.",
        "",
        "Accepted only: accepted_bank_payment_evidence and "
        "accepted_warehouse_stock_evidence.",
        "Rejected: rejected_stale_legal_certificate_evidence, "
        "rejected_signature_mismatch_evidence, and rejected_revoked_evidence.",
        "Quarantined: quarantined_unknown_source_evidence.",
        "",
        "7. MOCK VALIDATION BOUNDARY",
        "",
        "mock_valid signature is not real cryptographic validation.",
        "mock_known trust registry is not a real trust registry.",
        "not_revoked mock status is not a real revocation registry.",
        "real_signature_validated=false.",
        "real_trust_registry_used=false.",
        "real_revocation_registry_used=false.",
        "",
        "8. BOUNDARY MATRIX",
        "",
        "Connector observation is not truth.",
        "Connector observation is not trusted evidence.",
        "Evidence candidate is not truth.",
        "Evidence candidate is not accepted evidence.",
        "Validation packet is not Root acceptance.",
        "GT is not acceptance authority.",
        "ConflictCheck is not acceptance authority.",
        "Accepted evidence requires Root decision.",
        "Accepted evidence does not execute action.",
        "Accepted evidence does not write DRS by itself.",
        "Accepted evidence does not install Needle.",
        "Mock signature is not real signature.",
        "Mock trust registry is not real trust registry.",
        "Mock revocation check is not real revocation registry.",
        "Root remains final authority.",
        "",
        "9. EIGHT ADVERSARIAL ATTEMPTS",
        "",
        f"adversary_candidate_to_truth: {attempts['adversary_candidate_to_truth']['final_effect']}.",
        f"adversary_validation_packet_to_acceptance: "
        f"{attempts['adversary_validation_packet_to_acceptance']['final_effect']}.",
        f"adversary_gt_to_acceptance: {attempts['adversary_gt_to_acceptance']['final_effect']}.",
        f"adversary_conflictcheck_to_rejection_authority: "
        f"{attempts['adversary_conflictcheck_to_rejection_authority']['final_effect']}.",
        f"adversary_accepted_evidence_to_external_action: "
        f"{attempts['adversary_accepted_evidence_to_external_action']['final_effect']}.",
        f"adversary_accepted_evidence_to_drs_write: "
        f"{attempts['adversary_accepted_evidence_to_drs_write']['final_effect']}.",
        f"adversary_accepted_evidence_to_installed_needle: "
        f"{attempts['adversary_accepted_evidence_to_installed_needle']['final_effect']}.",
        f"adversary_mock_signature_to_real_signature_claim: "
        f"{attempts['adversary_mock_signature_to_real_signature_claim']['final_effect']}.",
        "",
        f"{root['adversarial_attempts_observed']} attempts were observed and "
        f"{root['adversarial_attempts_blocked']} were blocked. There is no truth, ready "
        "status, external action, DRS write, installed Needle, real signature "
        "validation, or production persistence.",
        "",
        "10. CONFLICTCHECK AND GT",
        "",
        f"ConflictCheck detects conflict paths: {conflict['conflict_paths']}. "
        "ConflictCheck is not authority.",
        "",
        f"GT recommends {gt['gt_recommendation']}. GT is advisory. GT cannot accept "
        "evidence, mark truth, execute action, write DRS, or install a Needle.",
        "",
        "11. ROOT FINAL",
        "",
        f"root_result: {root['root_result']}.",
        f"safe_secondary_outcome: {root['safe_secondary_outcome']}.",
        "Accepted evidence created: 2. Rejected: 3. Quarantined: 1.",
        "",
        "truth_proven=false.",
        "ready_status_created=false.",
        "external_action_executed=false.",
        "global_drs_write=false.",
        "external_drs_write=false.",
        "installed_needle_created=false.",
        "real_signature_validated=false.",
        "real_trust_registry_used=false.",
        "real_revocation_registry_used=false.",
        "network_called=false.",
        "gemini_called=false.",
        "production_persistence=false.",
        "root_remains_final_authority=true.",
        "",
        "12. WHAT THIS PROVES",
        "",
        "External observations can be promoted into EvidenceCandidate objects. "
        "Candidates can be locally validated into ValidationPacket objects.",
        "",
        "Only Root can accept, reject, or quarantine. Clean candidates can become "
        "AcceptedEvidence, while failed candidates are rejected or quarantined.",
        "",
        "Accepted evidence remains bounded: it is not truth, action, ready status, DRS "
        "write, or Needle. This is the first honest substrate for a future clean "
        "enterprise success path.",
        "",
        "13. WHAT THIS DOES NOT PROVE",
        "",
        "It does not implement External DRS, real connector/API access, network, "
        "Gemini, real cryptographic signature validation, a real trust registry, or a "
        "real revocation registry.",
        "",
        "It does not create production persistence, ready status, payment/shipment/"
        "legal action, DRS write, installed Needle, or invoke Marennya or UP. Accepted "
        "evidence does not equal truth.",
        "",
        "14. FINAL HUMAN SUMMARY",
        "",
        "Six candidates were created.",
        "Six validation packets were created.",
        "Root accepted two.",
        "Root rejected three.",
        "Root quarantined one.",
        "Eight escalation attempts were blocked.",
        "AcceptedEvidence is not truth.",
        "AcceptedEvidence is not ready.",
        "AcceptedEvidence is not action.",
        "AcceptedEvidence is not DRS write.",
        "AcceptedEvidence is not Needle.",
        "Root remains final authority.",
        "This unlocks the future clean enterprise success path, but not production trust yet.",
    ]
    return "\n".join(lines).rstrip() + "\n"


def run_human_external_evidence_acceptance_gate_walkthrough_v01() -> str:
    return render_human_external_evidence_acceptance_gate_walkthrough_v01(
        collect_external_evidence_acceptance_gate_v01()
    )


def main() -> int:
    print(run_human_external_evidence_acceptance_gate_walkthrough_v01(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
