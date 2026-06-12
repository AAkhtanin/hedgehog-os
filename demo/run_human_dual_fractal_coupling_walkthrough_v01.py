from __future__ import annotations

from demo.run_dual_fractal_coupling_v01 import collect_dual_fractal_coupling_v01


def render_human_dual_fractal_coupling_walkthrough_v01(report) -> str:
    parents = {row["parent_dac_id"]: row for row in report.parent_dac_matrix}
    cells = {row["cell_id"]: row for row in report.local_cell_matrix}
    edges = {row["coupling_edge_id"]: row for row in report.coupling_edges}
    interlock = report.interlock_observation
    conflict = report.conflictcheck_result
    gt = report.gt_advisory
    finals = {row["parent_dac_id"]: row for row in report.root_final_matrix}

    lines = [
        "HEDGEHOG OS — HUMAN DUAL FRACTAL COUPLING WALKTHROUGH v0.1",
        "",
        "1. WHAT THIS DEMO IS",
        "",
        "This is a human-readable walkthrough over the committed Dual Fractal "
        "Coupling / Interlocking DAC Proof v0.1. It observes two bounded parent DACs "
        "together and connects shared semantic evidence through coupling edges.",
        "",
        "Coupling means bounded semantic resonance, not authority transfer. The "
        "walkthrough performs no real external action, certificate submission, travel "
        "submission, booking, payment, Gemini call, network call, production "
        "persistence, or global/external DRS operation. Root remains final authority.",
        "",
        "2. TWO PARENT DACs",
        "",
        f"certificate_parent_dac uses "
        f"{parents['certificate_parent_dac']['scenario_id']}. Its Root result is "
        f"{parents['certificate_parent_dac']['root_result']} / "
        f"{parents['certificate_parent_dac']['safe_secondary_outcome']}.",
        "",
        f"travel_parent_dac uses {parents['travel_parent_dac']['scenario_id']}. Its "
        f"Root result is {parents['travel_parent_dac']['root_result']} / "
        f"{parents['travel_parent_dac']['safe_secondary_outcome']}.",
        "",
        "Each parent DAC keeps its own final. The parent DACs do not merge authority.",
        "",
        "3. LOCAL CELLS",
        "",
        f"certificate_insurance_check sees "
        f"{cells['certificate_insurance_check']['input_evidence']} and is blocked.",
        f"certificate_payment_receipt_check sees "
        f"{cells['certificate_payment_receipt_check']['input_evidence']} and is blocked.",
        f"certificate_submission_permission_check sees "
        f"{cells['certificate_submission_permission_check']['input_evidence']} and is "
        "blocked.",
        "",
        f"travel_document_check sees {cells['travel_document_check']['input_evidence']} "
        "and is blocked.",
        f"travel_payment_check sees {cells['travel_payment_check']['input_evidence']} "
        "and is blocked.",
        f"travel_lodging_check sees {cells['travel_lodging_check']['input_evidence']} "
        "and is ready.",
        f"travel_route_window_check sees "
        f"{cells['travel_route_window_check']['input_evidence']} and is blocked.",
        f"travel_permission_check sees "
        f"{cells['travel_permission_check']['input_evidence']} and is blocked.",
        "",
        f"Total local cells: {len(cells)}. Every local cell is local-only. No local "
        "cell has Root authority, parent-final authority, cross-parent authority, "
        "external action authority, or DRS write authority.",
        "",
        "4. COUPLING EDGES",
        "",
        f"Two bounded semantic coupling edges are observed: "
        f"{edges['certificate_insurance_to_travel_document']['coupling_edge_id']} and "
        f"{edges['certificate_payment_to_travel_payment']['coupling_edge_id']}.",
        "",
        "insurance_certificate expired is shared evidence between the certificate "
        "insurance check and the travel document check.",
        "",
        "payment_receipt missing is shared evidence between the certificate payment "
        "check and the travel payment check.",
        "",
        "The coupling type is bounded semantic resonance. Coupling can inform the "
        "other parent, but it cannot decide for the other parent. It transfers no "
        "authority, finalization, or execution.",
        "",
        "5. WHY COUPLING IS NOT AUTHORITY",
        "",
        "Shared evidence can inform. Shared evidence cannot decide. Semantic "
        "similarity is not authority. ReuseScore is not Root. DRS retrieval is not "
        "authority.",
        "",
        "Certificate cannot finalize travel. Travel cannot finalize certificate. A "
        "coupled cell cannot override the target cell. Root review is required to "
        "resolve the interlock.",
        "",
        "6. CONFLICTCHECK AND GT",
        "",
        "An authority-leak attempt would try to use coupling to transfer authority or "
        "finalize another parent.",
        f"ConflictCheck detects this: {str(conflict['conflict_detected']).lower()}, but "
        "ConflictCheck is not authority.",
        "",
        f"GT recommends {gt['gt_recommendation']}. GT cannot merge parent authority, "
        "mark certificate ready, mark travel ready, execute actions, grant "
        "cross-parent authority, or install a Needle.",
        "",
        "7. ROOT FINAL MATRIX",
        "",
        f"Root keeps certificate final: "
        f"{finals['certificate_parent_dac']['root_result']} / "
        f"{finals['certificate_parent_dac']['safe_secondary_outcome']}.",
        f"Root keeps travel final: {finals['travel_parent_dac']['root_result']} / "
        f"{finals['travel_parent_dac']['safe_secondary_outcome']}.",
        "",
        "No coupled parent finalizes the other parent. Child cells do not finalize the "
        "result. Coupling edges transfer no authority.",
        "",
        "There is no external action, certificate request submission, travel request "
        "submission, booking, payment, protocol_candidate, needle_candidate, installed "
        "Needle, production persistence, global/external DRS, Gemini, network, "
        "Telegram, Marennya, or UP.",
        "",
        "8. WHAT THIS MEANS ARCHITECTURALLY",
        "",
        "This is the first visible interlocking DAC proof. One parent DAC can resonate "
        "with another through shared semantic evidence, and that resonance is useful "
        "but bounded.",
        "",
        "It is the bridge from controlled Fractal DAC Expansion to future cross-domain "
        "DRS traversal. It is not External DRS, production autonomy, or live agent "
        "execution.",
        "",
        "9. FINAL HUMAN SUMMARY",
        "",
        f"Two bounded parent DACs are observed together: "
        f"{interlock['coupled_parents']} parents and "
        f"{interlock['coupling_edges_observed']} semantic edges.",
        "They are coupled through insurance and payment evidence.",
        "The shared evidence can inform but cannot decide.",
        "No authority, finalization, execution, or DRS write crosses the coupling edge.",
        "Root keeps separate finals for certificate and travel.",
        "This proves controlled dual fractal coupling without authority leakage.",
    ]
    return "\n".join(lines).rstrip() + "\n"


def run_human_dual_fractal_coupling_walkthrough_v01() -> str:
    return render_human_dual_fractal_coupling_walkthrough_v01(
        collect_dual_fractal_coupling_v01()
    )


def main() -> int:
    print(run_human_dual_fractal_coupling_walkthrough_v01(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
