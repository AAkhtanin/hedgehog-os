from __future__ import annotations

from demo.run_controlled_fractal_dac_expansion_v01 import (
    collect_controlled_fractal_dac_expansion_v01,
)


def render_human_controlled_fractal_dac_walkthrough_v01(report) -> str:
    parent = report.parent_request
    decomposition = report.decomposition_plan
    children = {row["child_cell_id"]: row for row in report.child_cell_candidates}
    aggregation = report.aggregation_result
    conflict = report.conflictcheck_result
    gt = report.gt_advisory
    root = report.root_final

    lines = [
        "HEDGEHOG OS — HUMAN CONTROLLED FRACTAL DAC WALKTHROUGH v0.1",
        "",
        "1. WHAT THIS DEMO IS",
        "",
        "This is a human-readable walkthrough over the committed Controlled Fractal "
        "DAC Expansion v0.1 proof. It is the first controlled fractal decomposition "
        "proof, not a new proof layer or capability layer.",
        "",
        "No real child agents are started. The walkthrough performs no external "
        "action, booking, payment, travel submission, Gemini call, network call, "
        "production persistence, or global/external DRS operation. Root remains "
        "final authority.",
        "",
        "2. PARENT REQUEST",
        "",
        f"The parent request is {parent['request_id']} / {parent['itinerary_id']}. "
        f"Its request type is {parent['request_type']}.",
        "",
        "Travel readiness is complex because it depends on multiple conditions. "
        "Root is the parent authority, and a Root final is required.",
        "",
        "3. CONTROLLED DECOMPOSITION",
        "",
        f"The parent request is decomposed into {decomposition['child_cells_planned']} "
        "bounded child-cell candidates:",
        "- document_check",
        "- payment_check",
        "- lodging_check",
        "- route_window_check",
        "- permission_check",
        "",
        '"child_cells_created" means local proof-mode child-cell candidates are '
        "created. They are runtime-local-only structures, not real autonomous or "
        "production agents.",
        "",
        "They have no Root authority, external action authority, DRS write authority, "
        "or final output authority. Decomposition requires Root aggregation.",
        "",
        "4. CHILD CELL LOCAL PROPOSALS",
        "",
        f"document_check sees {children['document_check']['input_evidence']} and "
        f"proposes {children['document_check']['local_proposal']}.",
        f"payment_check sees {children['payment_check']['input_evidence']} and "
        f"proposes {children['payment_check']['local_proposal']}.",
        f"lodging_check sees {children['lodging_check']['input_evidence']} and "
        f"proposes {children['lodging_check']['local_proposal']}.",
        f"route_window_check sees {children['route_window_check']['input_evidence']} "
        f"and proposes {children['route_window_check']['local_proposal']}.",
        f"permission_check sees {children['permission_check']['input_evidence']} and "
        f"proposes {children['permission_check']['local_proposal']}.",
        "",
        f"{aggregation['blocked_child_cells']} child cells are blocked and "
        f"{aggregation['ready_child_cells']} child cell is ready. All proposals are "
        "local only. No proposal is the parent final answer.",
        "",
        "5. AUTHORITY BOUNDARIES",
        "",
        "No child cell has Root authority, sibling authority, final output authority, "
        "external action authority, or DRS write authority.",
        "",
        "No child cell can mark the parent ready, override a sibling, spawn another "
        "child, install a Needle, or create a protocol_candidate or needle_candidate.",
        "",
        "6. ROOT AGGREGATION",
        "",
        f"Root observes {aggregation['child_cells_observed']} child-cell proposals: "
        f"{aggregation['blocked_child_cells']} blocked and "
        f"{aggregation['ready_child_cells']} ready.",
        "",
        f"The aggregate status is {aggregation['aggregate_status']}. The aggregate "
        f"result is {aggregation['aggregate_result']}, with safe secondary outcome "
        f"{aggregation['safe_secondary_outcome']}.",
        "",
        "Child-cell consensus is not Root. Majority vote is not Root. Aggregation is "
        "not final until Root finalizes.",
        "",
        "7. CONFLICTCHECK AND GT",
        "",
        "A parent-ready claim would contradict the blocked child-cell proposals.",
        f"ConflictCheck detects the contradiction: "
        f"{str(conflict['conflict_detected']).lower()}, but it is not authority.",
        "",
        f"GT recommends {gt['gt_recommendation']}. GT cannot mark the parent ready, "
        "execute an action, grant child authority, or install a Needle.",
        "",
        "8. ROOT FINAL",
        "",
        f"Root final result: {root['root_result']}.",
        f"Safe secondary outcome: {root['safe_secondary_outcome']}.",
        "",
        "Child cells exist only as bounded local candidates. They do not have "
        "authority and do not finalize the result.",
        "",
        "There is no direct ready override, travel request submission, booking, "
        "payment, protocol_candidate, needle_candidate, installed Needle, production "
        "persistence, global/external DRS, Gemini, network, Telegram, Marennya, or UP.",
        "",
        "9. WHAT THIS MEANS ARCHITECTURALLY",
        "",
        "This is the first visible controlled fractal expansion. The system can split "
        "a complex request into bounded local cells, and each cell can inspect only "
        "its own scope while the parent Root keeps authority.",
        "",
        "It is the bridge from multi-domain observation toward controlled Fractal "
        "DAC. It is not Dual Fractal Coupling and not production autonomy.",
        "",
        "10. FINAL HUMAN SUMMARY",
        "",
        "A complex travel readiness request is decomposed into 5 bounded child-cell "
        "candidates.",
        "The child cells produce local proposals only.",
        "Four blockers and one ready sub-check are observed.",
        "Children cannot execute, finalize, write DRS, install needles, or override "
        "each other.",
        "Root aggregates and finalizes not_ready / needs_user_travel_update.",
        "This proves controlled fractal expansion without autonomy.",
    ]
    return "\n".join(lines).rstrip() + "\n"


def run_human_controlled_fractal_dac_walkthrough_v01() -> str:
    return render_human_controlled_fractal_dac_walkthrough_v01(
        collect_controlled_fractal_dac_expansion_v01()
    )


def main() -> int:
    print(run_human_controlled_fractal_dac_walkthrough_v01(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
