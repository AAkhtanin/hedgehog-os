from __future__ import annotations

from demo.run_multi_domain_applied_smoke_v02 import (
    collect_multi_domain_applied_smoke_v02,
)


def render_human_multi_domain_applied_walkthrough_v02(report) -> str:
    domains = {row["domain_id"]: row for row in report.domain_matrix}
    reuse = report.cross_domain_reuse_observations
    conflict = report.conflict_matrix
    gt = report.gt_advisory
    finals = {row["domain_id"]: row for row in report.root_final_matrix}
    summary = report.summary

    lines = [
        "HEDGEHOG OS — HUMAN MULTI-DOMAIN APPLIED WALKTHROUGH v0.2",
        "",
        "1. WHAT THIS DEMO IS",
        "",
        "This is a human-readable walkthrough over the committed Multi-domain Applied "
        "Smoke v0.2 proof. It observes three applied domains together without creating "
        "a new proof layer, capability layer, Fractal DAC, Dual Fractal Coupling, "
        "External DRS, or test suite.",
        "",
        "It performs no real external action, dispatch, certificate submission, travel "
        "submission, booking, payment, Gemini call, network call, production "
        "persistence, or global/external DRS operation. Root remains final authority.",
        "",
        "2. SCENARIO",
        "",
        "The system observes three applied domains at once:",
        f"- warehouse {domains['warehouse_domain']['scenario_id']}",
        f"- certificate {domains['certificate_domain']['scenario_id']}",
        f"- travel {domains['travel_domain']['scenario_id']}",
        "",
        "This is multi-domain observation, not a merge of authority.",
        "",
        "3. DOMAIN RESULTS",
        "",
        "Warehouse is not_ready because water_filter is short by 2.",
        "Certificate is not_ready because insurance is expired and the payment receipt "
        "is missing.",
        "Travel is not_ready because insurance is expired, the payment receipt is "
        "missing, the route window is uncertain, and user permission is not confirmed.",
        "",
        "All three domains remain not_ready. Each keeps its own blocker, and no external "
        "action is executed.",
        "",
        "4. CROSS-DOMAIN REUSE",
        "",
        "Certificate experience can help travel check document-like conditions. "
        f"certificate_to_travel_document_reuse_observed="
        f"{str(reuse['certificate_to_travel_document_reuse_observed']).lower()}.",
        "",
        "This reuse is bounded. Certificate evidence does not make travel ready. "
        "Semantic similarity is not authority. ReuseScore is not Root. DRS retrieval "
        "is not authority. Cross-domain reuse requires Root review.",
        "",
        "5. DOMAIN ISOLATION",
        "",
        "Warehouse does not authorize certificate or travel.",
        "Certificate does not authorize warehouse or travel.",
        "Travel does not authorize warehouse or certificate.",
        "",
        f"All {len(report.domain_isolation_matrix)} isolation directions deny direct "
        "cross-domain authority. Root review is required, and child authority is not granted.",
        "",
        "6. CONFLICTCHECK AND GT",
        "",
        "A cross-domain ready claim would contradict the domain-specific blockers.",
        f"ConflictCheck detects this: {str(conflict['conflict_detected']).lower()}, but "
        "ConflictCheck is not final authority.",
        "",
        f"GT recommends {gt['gt_recommendation']}. GT cannot merge domain authority, "
        "mark any domain ready, or execute actions.",
        "",
        "7. ROOT FINAL MATRIX",
        "",
        f"Root keeps warehouse separate: {finals['warehouse_domain']['root_result']}.",
        f"Root keeps certificate separate: {finals['certificate_domain']['root_result']} "
        f"/ {finals['certificate_domain']['safe_secondary_outcome']}.",
        f"Root keeps travel separate: {finals['travel_domain']['root_result']} / "
        f"{finals['travel_domain']['safe_secondary_outcome']}.",
        "",
        "There is no direct ready override, completed external action, protocol_candidate, "
        "needle_candidate, installed Needle, production persistence, global/external DRS, "
        "Gemini, network, Telegram, Marennya, or UP.",
        "",
        "8. WHAT THIS IS NOT YET",
        "",
        "This is not Fractal DAC or Dual Fractal Coupling. No child cells exist and no "
        "child authority exists. External DRS is not implemented.",
        "",
        "This smoke is a bridge toward controlled fractal expansion and later coupling.",
        "",
        "9. FINAL HUMAN SUMMARY",
        "",
        f"The system observes {summary['domains_observed']} applied domains together.",
        "It preserves each domain's own blockers and Root final.",
        "It allows bounded certificate-to-travel reuse without letting reuse become authority.",
        "It prevents direct cross-domain authority.",
        "It does not execute anything.",
        "It is a necessary bridge toward Fractal DAC Expansion, but it is not yet Fractal DAC.",
    ]
    return "\n".join(lines).rstrip() + "\n"


def run_human_multi_domain_applied_walkthrough_v02() -> str:
    return render_human_multi_domain_applied_walkthrough_v02(
        collect_multi_domain_applied_smoke_v02()
    )


def main() -> int:
    print(run_human_multi_domain_applied_walkthrough_v02(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
