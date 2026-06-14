from __future__ import annotations

from demo.run_external_drs_pointer_protocol_v01 import (
    collect_external_drs_pointer_protocol_v01,
)


def render_human_external_drs_pointer_protocol_walkthrough_v01(report) -> str:
    source = report.source_evidence
    pointers = {row["pointer_id"]: row for row in report.pointer_candidates}
    attempts = {row["attempt_id"]: row for row in report.adversarial_attempts}
    conflict = report.conflictcheck_result
    gt = report.gt_advisory
    root = report.root_final
    summary = report.summary

    certificate = pointers["external_drs_pointer_certificate_evidence_v01"]
    payment = pointers["external_drs_pointer_payment_receipt_unknown_v01"]

    lines = [
        "HEDGEHOG OS — HUMAN EXTERNAL DRS POINTER PROTOCOL WALKTHROUGH v0.1",
        "",
        "1. WHAT THIS DEMO IS",
        "",
        "This is a human-readable walkthrough over the committed External DRS Pointer "
        "Protocol v0.1 proof. It introduces local proof-only external pointer "
        "candidates.",
        "",
        "The proof shows that pointer candidates cannot become trusted evidence, "
        "truth, authority, an installed Needle, a DRS write, or an external action.",
        "",
        "This is not External DRS implementation, remote retrieval, connector/API "
        "access, network use, production persistence, or production autonomy.",
        "",
        "2. WHY THIS COMES AFTER NEEDLE SAFETY",
        "",
        "Needle adversarial / safety pack proved that retrieval, bridge traversal, "
        "DAG nodes, GT, and NeedleCandidate references cannot self-promote into "
        "authority, action, truth, or capability.",
        "",
        "External pointer protocol is the next boundary because future external "
        "records will arrive as pointer-like claims. Before real External DRS or "
        "connector work, pointer claims must be quarantined and reviewed, not trusted.",
        "",
        "3. SOURCE EVIDENCE MODE",
        "",
        "This proof references already closed checkpoints as closed-checkpoint "
        "metadata. source_collectors_replayed=false.",
        "",
        "This avoids replaying the entire historical proof chain during targeted "
        "tests. It is not a truth claim and does not hide truth; it separates a "
        "targeted proof from full historical audit replay.",
        "",
        "Full historical replay belongs to explicit audit or super-smoke runs, not "
        "every targeted proof test.",
        "",
        f"Needle adversarial safety source status: "
        f"{source['needle_adversarial_safety_source_status']}.",
        f"Cross-domain DRS Bridge source status: "
        f"{source['cross_domain_drs_bridge_source_status']}.",
        f"Dual Fractal Coupling source status: "
        f"{source['dual_fractal_coupling_source_status']}.",
        f"Applied DRS Retrieval Reuse source status: "
        f"{source['applied_drs_retrieval_reuse_source_status']}.",
        f"ConflictCheck source status: {source['conflictcheck_source_status']}.",
        f"Audit hash-chain source status: {source['audit_hash_chain_source_status']}.",
        "",
        "4. POINTER CANDIDATES",
        "",
        f"{certificate['pointer_id']} is a mock external certificate registry pointer "
        f"candidate. It claims insurance_certificate={certificate['claimed_semantic_value']} "
        f"for {certificate['target_record']}.",
        "",
        f"Its status is {certificate['pointer_status']}. retrieval_performed=false, "
        "trusted_evidence_created=false, and truth_proven=false.",
        "",
        f"{payment['pointer_id']} is an unknown payment source pointer candidate. It "
        f"claims payment_receipt={payment['claimed_semantic_value']} for "
        f"{payment['target_record']}.",
        "",
        f"Its status is {payment['pointer_status']}. Provenance is missing, freshness "
        "is unknown, and trust is unknown. retrieval_performed=false, "
        "trusted_evidence_created=false, and truth_proven=false.",
        "",
        "5. PROTOCOL BOUNDARY MATRIX",
        "",
        "External pointer is not External DRS.",
        "Pointer candidate is not trusted evidence.",
        "Pointer claim is not truth.",
        "Pointer status does not finalize.",
        "Pointer cannot execute action.",
        "Pointer cannot write global DRS.",
        "Pointer cannot write External DRS.",
        "Pointer cannot install Needle.",
        "Pointer cannot bypass Root.",
        "Pointer cannot bypass ConflictCheck.",
        "Pointer cannot bypass GT.",
        "Pointer cannot bypass permission or needs_user.",
        "Pointer cannot bypass quarantine.",
        "Signature placeholder is not signature.",
        "Trust registry placeholder is not trust.",
        "Revocation placeholder is not revocation.",
        "Root review and explicit acceptance are required.",
        "",
        "6. SIX ADVERSARIAL ATTEMPTS",
        "",
        f"adversary_pointer_claim_to_truth tries to treat a pointer claim as truth. "
        f"Outcome: {attempts['adversary_pointer_claim_to_truth']['final_effect']}.",
        "",
        f"adversary_pointer_to_ready_status tries to make certificate or travel ready "
        f"from a pointer claim. Outcome: "
        f"{attempts['adversary_pointer_to_ready_status']['final_effect']}.",
        "",
        f"adversary_pointer_to_external_action tries to submit an external action from "
        f"a pointer. Outcome: "
        f"{attempts['adversary_pointer_to_external_action']['final_effect']}.",
        "",
        f"adversary_pointer_to_drs_write tries to write a pointer into global or "
        f"External DRS as accepted Work. Outcome: "
        f"{attempts['adversary_pointer_to_drs_write']['final_effect']}.",
        "",
        f"adversary_pointer_to_installed_needle tries to install a Needle from a "
        f"pointer. Outcome: "
        f"{attempts['adversary_pointer_to_installed_needle']['final_effect']}.",
        "",
        f"adversary_untrusted_source_laundering tries to launder an unknown payment "
        f"source into trusted evidence. Outcome: "
        f"{attempts['adversary_untrusted_source_laundering']['final_effect']}.",
        "",
        f"{summary['adversarial_attempts_observed']} attempts were observed and "
        f"{summary['adversarial_attempts_blocked']} were blocked. "
        f"{summary['quarantined_attempts_observed']} attempt was quarantined and blocked.",
        "",
        f"{summary['pointer_candidates_accepted']} pointer candidates were accepted. "
        "No trusted evidence or truth was created. No external action, DRS write, or "
        "installed Needle was created.",
        "",
        "7. CONFLICTCHECK AND GT",
        "",
        f"ConflictCheck detects {conflict['conflict_count']} pointer escalation "
        "conflicts. ConflictCheck is not authority.",
        "",
        f"GT recommends {gt['gt_recommendation']}. GT cannot mark a pointer trusted, "
        "mark truth, execute an action, write External DRS, or install a Needle.",
        "",
        "8. ROOT FINAL",
        "",
        f"Root result: {root['root_result']}.",
        f"Safe secondary outcome: {root['safe_secondary_outcome']}.",
        f"Pointer candidates observed: {root['pointer_candidates_observed']}.",
        f"Pointer candidates accepted: {root['pointer_candidates_accepted']}.",
        "",
        "There is no trusted evidence, truth, ready status, external action, "
        "global/external DRS write, installed Needle, or production persistence.",
        "",
        "External DRS is not implemented. There is no global semantic fabric, public "
        "Internet of Meaning, remote retrieval, connector, Gemini, network, Telegram, "
        "Marennya, or UP. Root remains final authority.",
        "",
        "9. WHAT THIS PROVES",
        "",
        "External pointer candidates can be represented safely as local proof-only "
        "objects. Pointer claims cannot become truth or trusted evidence.",
        "",
        "Unknown sources are blocked or quarantined. Signature, trust-registry, and "
        "revocation placeholders are not treated as real signature, trust, or "
        "revocation.",
        "",
        "Root review and explicit acceptance remain required. This prepares the "
        "topology for future External DRS without implementing it.",
        "",
        "10. WHAT THIS DOES NOT PROVE",
        "",
        "It does not implement External DRS, remote retrieval, connector/API access, "
        "production RAG, global semantic fabric, or public Internet of Meaning.",
        "",
        "It does not install Needles, prove full adversarial safety for all future "
        "external records, grant production autonomy, or invoke Marennya or UP.",
        "",
        "11. FINAL HUMAN SUMMARY",
        "",
        "Two pointer candidates were observed.",
        "Zero were accepted.",
        "Six escalation attempts were tested.",
        "All were blocked.",
        "Unknown-source laundering was quarantined and blocked.",
        "External pointer is not External DRS.",
        "Pointer claim is not truth.",
        "Pointer candidate is not trusted evidence.",
        "Root remains sovereign.",
    ]
    return "\n".join(lines).rstrip() + "\n"


def run_human_external_drs_pointer_protocol_walkthrough_v01() -> str:
    return render_human_external_drs_pointer_protocol_walkthrough_v01(
        collect_external_drs_pointer_protocol_v01()
    )


def main() -> int:
    print(run_human_external_drs_pointer_protocol_walkthrough_v01(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
