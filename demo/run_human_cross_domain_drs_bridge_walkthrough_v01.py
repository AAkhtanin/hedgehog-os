from __future__ import annotations

from demo.run_cross_domain_drs_bridge_v01 import collect_cross_domain_drs_bridge_v01


def render_human_cross_domain_drs_bridge_walkthrough_v01(report) -> str:
    bridges = {row["bridge_id"]: row for row in report.bridge_registry}
    request = report.traversal_request
    steps = {row["traversal_step_id"]: row for row in report.traversal_steps}
    result = report.traversal_result
    conflict = report.conflictcheck_result
    gt = report.gt_advisory
    root = report.root_final

    lines = [
        "HEDGEHOG OS — HUMAN CROSS-DOMAIN DRS BRIDGE WALKTHROUGH v0.1",
        "",
        "1. WHAT THIS DEMO IS",
        "",
        "This is a human-readable walkthrough over the committed Cross-domain DRS "
        "Bridge Proof v0.1. The proof observes local proof-only DRS bridge traversal "
        "over already established bounded semantic coupling edges.",
        "",
        "Root authorizes traversal. Traversal informs Root review, but it does not "
        "decide, finalize, execute, or transfer authority.",
        "",
        "This is not External DRS, global DRS, a public semantic fabric, production "
        "persistence, remote retrieval, connector/API access, Gemini, network, "
        "Telegram, Marennya, UP, or live agent execution.",
        "",
        "2. WHY THIS COMES AFTER DUAL COUPLING",
        "",
        "Dual Fractal Coupling established two bounded parent DACs: "
        "certificate_parent_dac and travel_parent_dac.",
        "",
        "It also established bounded semantic coupling edges for "
        "insurance_certificate and payment_receipt.",
        "",
        "DRS Bridge v0.1 does not invent new authority. It locally traverses those "
        "already established bounded semantic edges.",
        "",
        "A coupling edge is the bounded semantic relation. DRS bridge traversal is the "
        "local, reviewed trace over that relation.",
        "",
        "3. SOURCE AND TARGET DOMAINS",
        "",
        f"Source domain: {request['source_domain']} / APP-77 / CERT-310.",
        f"Target domain: {request['target_domain']} / TRAVEL-900 / ITIN-44.",
        "",
        f"After Root review, the target remains "
        f"{result['target_parent_result_after_root_review']}. The safe secondary "
        f"outcome remains {result['safe_secondary_outcome']}.",
        "",
        "4. BRIDGE RECORDS",
        "",
        f"{bridges['bridge_certificate_insurance_to_travel_document_v01']['bridge_id']} "
        "carries insurance_certificate: expired as candidate evidence that informs "
        "travel_document_check.",
        "",
        f"{bridges['bridge_certificate_payment_to_travel_payment_v01']['bridge_id']} "
        "carries payment_receipt: missing as candidate evidence that informs "
        "travel_payment_check.",
        "",
        "Both bridge records are local proof-only records. They create no external DRS "
        "pointer, global DRS write, or production persistence. They transfer no "
        "authority, finalization, or execution. Root review is required.",
        "",
        "5. TRAVERSAL STEPS",
        "",
        f"{steps['step_insurance_certificate_expired']['traversal_step_id']} informs "
        "that travel_document_check is blocked.",
        f"{steps['step_payment_receipt_missing']['traversal_step_id']} informs that "
        "travel_payment_check is blocked.",
        "",
        "Traversal can inform target checks. It cannot mark the target parent ready, "
        "finalize the target parent, execute an external action, or write global or "
        "external DRS.",
        "",
        "6. WHY BRIDGE IS NOT AUTHORITY",
        "",
        "DRS bridge is not authority. Traversal trace is not truth. Shared evidence "
        "can inform but cannot decide. DRS retrieval is not authority. Semantic "
        "similarity is not authority. ReuseScore is not Root.",
        "",
        "Audit hash proves continuity, not truth. Bridge traversal is not provenance "
        "laundering.",
        "",
        "Certificate evidence may inform travel checks, but certificate_parent_dac "
        "does not command travel_parent_dac.",
        "",
        "7. CONFLICTCHECK AND GT",
        "",
        "ConflictCheck detects the authority-escalation attempt: using DRS bridge "
        "traversal to transfer authority or finalize the target parent.",
        f"Conflict detected: {str(conflict['conflict_detected']).lower()}. "
        "ConflictCheck is advisory, not authority.",
        "",
        f"GT recommends {gt['gt_recommendation']}. GT cannot mark the target ready, "
        "execute an action, grant bridge authority, create an external DRS pointer, "
        "or install a Needle.",
        "",
        "8. ROOT FINAL",
        "",
        f"Root result remains {root['root_result']}.",
        f"Safe secondary outcome remains {root['safe_secondary_outcome']}.",
        "",
        f"DRS bridge traversal completed: "
        f"{str(root['drs_bridge_traversal_completed']).lower()}. The bridge informed "
        "the target but did not decide or finalize it.",
        "",
        "No authority, execution, or DRS write transferred. There is no external DRS "
        "pointer, global/external DRS write, production persistence, travel or "
        "certificate submission, booking, payment, protocol_candidate, "
        "needle_candidate, installed Needle, Gemini, network, Telegram, Marennya, or UP.",
        "",
        "9. WHAT THIS PROVES",
        "",
        "Local proof-only DRS bridge traversal can route candidate evidence across "
        "domains. Root can use that traversal as reviewed evidence.",
        "",
        "Cross-domain evidence can inform target checks while the target domain remains "
        "under Root review and Root final. This is a safe bridge between Dual Coupling "
        "and future safety and pointer work.",
        "",
        "10. WHAT THIS DOES NOT PROVE",
        "",
        "External DRS Pointer Protocol is not proven. Global semantic fabric and public "
        "Internet of Meaning are not proven. Remote DRS retrieval is not proven.",
        "",
        "Signatures, trust registry, revocation, production DRS persistence, real "
        "inter-organization memory exchange, and full adversarial external-record "
        "safety are not proven.",
        "",
        "The bridge cannot decide readiness. Marennya and UP are not proven.",
        "",
        "11. FINAL HUMAN SUMMARY",
        "",
        "Dual Coupling established bounded semantic edges.",
        "Cross-domain DRS Bridge v0.1 locally traverses those edges as candidate evidence.",
        "The bridge may inform but cannot decide.",
        "The traversal trace is not truth.",
        "Bridge traversal is not provenance laundering.",
        "Root remains sovereign.",
    ]
    return "\n".join(lines).rstrip() + "\n"


def run_human_cross_domain_drs_bridge_walkthrough_v01() -> str:
    return render_human_cross_domain_drs_bridge_walkthrough_v01(
        collect_cross_domain_drs_bridge_v01()
    )


def main() -> int:
    print(run_human_cross_domain_drs_bridge_walkthrough_v01(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
