from __future__ import annotations

from demo.run_needle_adversarial_safety_pack_v01 import (
    collect_needle_adversarial_safety_pack_v01,
)


def render_human_needle_adversarial_safety_pack_walkthrough_v01(report) -> str:
    attempts = {row["attempt_id"]: row for row in report.adversarial_attempts}
    conflict = report.conflictcheck_result
    gt = report.gt_advisory
    root = report.root_final
    summary = report.summary

    lines = [
        "HEDGEHOG OS — HUMAN NEEDLE ADVERSARIAL SAFETY PACK WALKTHROUGH v0.1",
        "",
        "1. WHAT THIS DEMO IS",
        "",
        "This is a human-readable walkthrough over the committed Needle adversarial / "
        "safety pack v0.1. It attacks boundaries created by retrieval, DRS bridge "
        "traversal, coupling, child-cell proposals, DAG nodes, GT, and the "
        "NeedleCandidate lifecycle.",
        "",
        "The goal is to prove that these mechanisms cannot become authority, truth, "
        "an installed Needle, a capability, or an external action.",
        "",
        "This is not NeedleFactory, production Needle installation, External DRS, "
        "global semantic fabric, real production RAG retrieval, Gemini, network, "
        "Telegram, Marennya, UP, or production autonomy.",
        "",
        "2. WHY THIS COMES AFTER DRS BRIDGE",
        "",
        "Cross-domain DRS Bridge showed local proof-only traversal across bounded "
        "semantic edges.",
        "",
        "Before External DRS Pointer Protocol, the system must prove that bridge and "
        "retrieval evidence cannot be promoted into authority. Future external "
        "pointers will look like incoming semantic evidence, so safety must be tested "
        "before pointer protocol.",
        "",
        "3. THE EIGHT ADVERSARIAL ATTEMPTS",
        "",
        f"adversary_bridge_to_needle_install tries to use a DRS bridge record to "
        f"install a Needle directly. Outcome: "
        f"{attempts['adversary_bridge_to_needle_install']['final_effect']}.",
        "",
        f"adversary_rag_result_to_truth tries to use RAG-like retrieved evidence as "
        f"truth proof. Outcome: {attempts['adversary_rag_result_to_truth']['final_effect']}.",
        "",
        f"adversary_coupling_edge_to_command tries to treat a coupling edge as a "
        f"command channel between parent DACs. Outcome: "
        f"{attempts['adversary_coupling_edge_to_command']['final_effect']}.",
        "",
        f"adversary_child_cell_to_external_action tries to let a child-cell proposal "
        f"submit a travel or certificate action. Outcome: "
        f"{attempts['adversary_child_cell_to_external_action']['final_effect']}.",
        "",
        f"adversary_dag_node_to_root tries to treat a DAG execution node as Root "
        f"final authority. Outcome: {attempts['adversary_dag_node_to_root']['final_effect']}.",
        "",
        f"adversary_gt_to_installed_needle tries to let GT advice install a Needle or "
        f"grant capability. Outcome: "
        f"{attempts['adversary_gt_to_installed_needle']['final_effect']}.",
        "",
        "adversary_bridge_provenance_laundering tries to launder unsafe evidence "
        f"through bridge traversal. Outcome: "
        f"{attempts['adversary_bridge_provenance_laundering']['final_effect']}.",
        "",
        "adversary_needlecandidate_to_capability tries to promote an existing "
        f"NeedleCandidate directly to installed Needle or capability. Outcome: "
        f"{attempts['adversary_needlecandidate_to_capability']['final_effect']}.",
        "",
        f"{summary['adversarial_attempts_observed']} attempts were observed and "
        f"{summary['adversarial_attempts_blocked']} were blocked. "
        f"{summary['quarantined_attempts_observed']} attempt was quarantined and blocked.",
        "",
        "No external action was executed. No installed Needle was created. No "
        "authority was transferred. No truth was proven.",
        "",
        "4. SAFETY BOUNDARY MATRIX",
        "",
        "DAG node is not Root.",
        "RAG-like retrieval result is not truth.",
        "DRS bridge is not authority.",
        "Traversal trace is not truth.",
        "Bridge traversal is not provenance laundering.",
        "Coupling edge is not command channel.",
        "Child-cell proposal is not parent final.",
        "NeedleCandidate is not installed Needle.",
        "GT is not authority.",
        "Audit hash chain is not truth.",
        "Root review is required for capability.",
        "Root final is required for action.",
        "An explicit installation boundary is required for a Needle.",
        "There is no external action without permission and Root.",
        "",
        "5. CONFLICTCHECK AND GT",
        "",
        f"ConflictCheck detects all {conflict['conflict_count']} escalation attempts. "
        "ConflictCheck is not authority.",
        "",
        f"GT recommends {gt['gt_recommendation']}. GT cannot install a Needle, grant "
        "authority, execute an action, or mark truth.",
        "",
        "6. ROOT FINAL",
        "",
        f"Root result: {root['root_result']}.",
        f"Safe secondary outcome: {root['safe_secondary_outcome']}.",
        "",
        "All adversarial attempts are blocked. There is no illegal authority transfer, "
        "illegal truth promotion, installed Needle, external action, production "
        "persistence, or global/external DRS write.",
        "",
        "There is no Gemini, network, Telegram, Marennya, or UP invocation. Root "
        "remains final authority.",
        "",
        "7. WHAT THIS PROVES",
        "",
        "Semantic retrieval, DRS bridge traversal, coupling edges, DAG nodes, GT "
        "advice, child-cell proposals, and NeedleCandidate references cannot "
        "self-promote into authority, action, or capability.",
        "",
        "Bridge traversal cannot launder provenance. Retrieval is not truth. "
        "NeedleCandidate cannot become installed Needle without an explicit boundary.",
        "",
        "This safety layer is a prerequisite before External DRS Pointer Protocol.",
        "",
        "8. WHAT THIS DOES NOT PROVE",
        "",
        "It does not implement NeedleFactory or install real Needles. It does not "
        "implement External DRS Pointer Protocol, global DRS, public semantic fabric, "
        "or real production RAG.",
        "",
        "It does not prove full adversarial safety for all future external records, "
        "grant production autonomy, or invoke Marennya or UP.",
        "",
        "9. FINAL HUMAN SUMMARY",
        "",
        "Eight escalation attempts were tested.",
        "All were blocked.",
        "Provenance laundering was quarantined and blocked.",
        "Retrieval is not truth.",
        "Bridge traversal is not authority.",
        "NeedleCandidate is not installed Needle.",
        "DAG node is not Root.",
        "GT is not authority.",
        "Root remains sovereign.",
    ]
    return "\n".join(lines).rstrip() + "\n"


def run_human_needle_adversarial_safety_pack_walkthrough_v01() -> str:
    return render_human_needle_adversarial_safety_pack_walkthrough_v01(
        collect_needle_adversarial_safety_pack_v01()
    )


def main() -> int:
    print(run_human_needle_adversarial_safety_pack_walkthrough_v01(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
