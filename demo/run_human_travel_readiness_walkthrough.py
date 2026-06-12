from __future__ import annotations

from demo.run_applied_travel_readiness_demo import (
    collect_applied_travel_readiness_demo,
)


def render_human_travel_readiness_walkthrough(report) -> str:
    request = report.travel_request
    conditions = {row["condition_id"]: row for row in report.travel_condition_matrix}
    reuse = report.travel_drs_reuse_candidates
    permission = report.travel_permission_boundary
    decomposition = report.travel_decomposition_hint
    conflict = report.travel_conflict_report
    gt = report.travel_gt_advisory
    root = report.travel_root_final
    summary = report.summary

    lines = [
        "HEDGEHOG OS — HUMAN TRAVEL READINESS WALKTHROUGH",
        "",
        "1. WHAT THIS DEMO IS",
        "",
        "This is a human-readable walkthrough over the committed Applied Travel / "
        "Multi-condition Readiness proof. It is not a new proof layer, capability "
        "layer, Fractal DAC implementation, or test suite.",
        "",
        "The walkthrough performs no real external action, booking, payment, "
        "certificate or travel submission, Gemini call, network call, production "
        "persistence, or global/external DRS operation. Root remains final authority.",
        "",
        "2. SCENARIO",
        "",
        f"Request {request['travel_request_id']} asks whether itinerary "
        f"{request['itinerary_id']} is ready.",
        "",
        "This is multi-condition travel readiness, not a single document check. "
        "Documents, payment evidence, lodging, route timing, and permission must be "
        "considered together.",
        "",
        "3. CONDITION CHECK",
        "",
        f"passport_validity is {conditions['passport_validity']['status']} and does "
        "not block travel.",
        f"insurance_certificate is {conditions['insurance_certificate']['status']} "
        "and blocks travel.",
        f"payment_receipt is {conditions['payment_receipt']['status']} and blocks travel.",
        f"hotel_confirmation is {conditions['hotel_confirmation']['status']} and does "
        "not block travel.",
        f"route_window is {conditions['route_window']['status']} and blocks travel.",
        f"user_permission is {conditions['user_permission']['status']} and blocks travel.",
        "",
        f"{summary['blocking_conditions_count']} blocking conditions are detected. "
        "Root cannot mark travel ready while they remain.",
        "",
        "4. DRS REUSE",
        "",
        f"DRS retrieves prior certificate-readiness experience "
        f"{reuse[0]['source_context']} and certificate reuse experience "
        f"{reuse[1]['source_context']}.",
        "",
        "This is bounded_partial_reuse. It helps suggest checks for "
        "insurance_certificate and payment_receipt, but it cannot mark travel ready "
        "or submit anything.",
        "",
        "Semantic similarity is not authority. ReuseScore is not Root. DRS retrieval "
        "is not authority.",
        "",
        "5. PERMISSION / NEEDSUSER",
        "",
        f"User permission is {permission['user_permission_status']}, so permission is "
        "required. Permission is not execution.",
        "",
        "A proof-only approval would be future-action permission only. It would not "
        "create a completed action.",
        "",
        "6. DECOMPOSITION HINT",
        "",
        "Travel readiness is not atomic. It naturally decomposes into future bounded "
        "branches:",
    ]
    lines.extend(f"- {branch}" for branch in decomposition["future_bounded_branches"])
    lines.extend(
        [
            "",
            "In v0.1, Fractal DAC is not invoked. No child cells are created and no "
            "child authority is granted. This is only a bridge toward future Fractal "
            "DAC Expansion.",
            "",
            "7. CONFLICTCHECK AND GT",
            "",
            "A ready claim would contradict expired, missing, uncertain, and "
            "not-confirmed evidence.",
            "",
            f"ConflictCheck detects the contradiction: "
            f"{str(conflict['conflict_detected']).lower()}. It is not final authority.",
            "",
            f"GT recommends {gt['gt_recommendation']} because blocking conditions are "
            "present. GT cannot mark ready, execute an action, or submit the travel request.",
            "",
            "8. ROOT FINAL",
            "",
            f"Root result: {root['root_result']}.",
            f"Safe secondary outcome: {root['safe_secondary_outcome']}.",
            "",
            "No travel request is submitted. No booking is created. No payment is "
            "executed. No external action or direct ready override occurs.",
            "",
            "No protocol_candidate, needle_candidate, or installed Needle is created. "
            "There is no production persistence, global/external DRS, Gemini, network, "
            "Telegram, Marennya, or UP.",
            "",
            "9. FINAL HUMAN SUMMARY",
            "",
            "The system handles a multi-condition travel request.",
            "It can reuse prior document-readiness experience without trusting reuse blindly.",
            "It does not execute anything.",
            "It exposes a future decomposition shape without invoking Fractal DAC.",
            "Root remains final authority.",
            "Result: not_ready, needs_user_travel_update.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def run_human_travel_readiness_walkthrough() -> str:
    return render_human_travel_readiness_walkthrough(
        collect_applied_travel_readiness_demo()
    )


def main() -> int:
    print(run_human_travel_readiness_walkthrough(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
