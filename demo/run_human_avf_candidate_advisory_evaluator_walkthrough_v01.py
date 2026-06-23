from __future__ import annotations

from typing import Any

from demo.run_gt_lgt_advisory_evaluator_v01 import (
    SCENARIOS,
    run_all_scenarios,
)


TITLE = "HEDGEHOG OS — HUMAN AVF CANDIDATE ADVISORY EVALUATOR WALKTHROUGH v0.1"

REQUIRED_COUNTERS = {
    "scenarios_total": 10,
    "scenarios_passed": 10,
    "advisory_inputs_count": 10,
    "gt_signals_emitted_count": 10,
    "lgt_signals_emitted_count": 10,
    "lgt_deferred_count": 10,
    "advisory_reports_created_count": 10,
    "root_review_required_count": 10,
    "root_final_authority_preserved_count": 10,
    "direct_reuse_allowed_count": 0,
    "action_permission_granted_count": 0,
    "final_output_created_count": 0,
    "gt_authority_claimed_count": 0,
    "lgt_authority_claimed_count": 0,
    "advisory_truth_claimed_count": 0,
    "advisory_accept_as_root_final_count": 0,
    "network_used_count": 0,
    "gemini_used_count": 0,
}

SECTION_HEADINGS = (
    "WHAT THIS WALKTHROUGH IS",
    "TOPOLOGY CLARIFICATION",
    "PIPELINE",
    "ACT 1 — AVF RANKED REPORT BECOMES ADVISORY INPUT ONLY",
    "ACT 2 — GT-STYLE ACCEPT STILL REQUIRES ROOT REVIEW",
    "ACT 3 — DEGRADE / REJECT ROUTE TO REVIEW, NOT FINAL",
    "ACT 4 — LGT IS DEFERRED PLACEHOLDER ONLY",
    "ACT 5 — SAFETY PRESSURE OVERRIDES HIGH SCORE",
    "ACT 6 — ROOT FINAL AUTHORITY PRESERVED",
    "COUNTERS",
    "LIMITATIONS",
    "FINAL HUMAN SUMMARY",
)


def _required_counters_match(result: dict[str, Any]) -> bool:
    observed = {
        "scenarios_total": result["scenarios_total"],
        "scenarios_passed": result["scenarios_passed"],
        **result["counters"],
    }
    return all(observed.get(key) == expected for key, expected in REQUIRED_COUNTERS.items())


def build_walkthrough() -> str:
    result = run_all_scenarios()
    counters = result["counters"]
    counters_match = _required_counters_match(result)

    lines = [
        TITLE,
        "",
        "WHAT THIS WALKTHROUGH IS",
        "This walkthrough explains the already audited GT/LGT Advisory Evaluator runtime using the safer human-facing name AVF Candidate Advisory Evaluator.",
        "It creates no new runtime capability, no new GTValidator, no production LGT, no Root behavior, no Architect behavior, and no FinalOutput.",
        "",
        "TOPOLOGY CLARIFICATION",
        "This layer does not relocate canonical terminal GTValidator.",
        "Canonical GTValidator remains after Executor/Post V&V and before Root FinalOutput.",
        "This layer is pre-Architect candidate-level advisory review over AVF-ranked DRS candidates.",
        "It does not command Architect.",
        "It returns advisory signals to Root/Orchestrator route decision.",
        "Architect receives only Root-shaped tasks/routes.",
        "Root remains final authority.",
        "",
        "PIPELINE",
        "AVF-ranked DRS candidates",
        "→ Candidate Advisory Review",
        "→ GT-style advisory signal",
        "→ LGT deferred placeholder",
        "→ Root/Orchestrator route decision",
        "→ Architect receives Root-shaped task",
        "→ canonical GTValidator remains downstream",
        "→ Root remains final authority",
        "The evaluator labels review signals before Architect; it does not issue commands to Architect.",
        "",
        "ACT 1 — AVF RANKED REPORT BECOMES ADVISORY INPUT ONLY",
        "avf_ranked_report_becomes_advisory_input_only",
        "AVF-ranked DRS candidates enter as advisory input only. The report can inform route review, but it is not truth or authority.",
        "",
        "ACT 2 — GT-STYLE ACCEPT STILL REQUIRES ROOT REVIEW",
        "gt_accept_signal_requires_root_final_review",
        "A GT-style advisory accept still returns upward for Root review.",
        f"advisory_accept_as_root_final_count: {counters['advisory_accept_as_root_final_count']}",
        "",
        "ACT 3 — DEGRADE / REJECT ROUTE TO REVIEW, NOT FINAL",
        "gt_degrade_signal_routes_to_review_not_final",
        "gt_reject_signal_blocks_candidate_not_root_final",
        "Degrade and reject are route-review signals, not final user-facing outcomes.",
        f"final_output_created_count: {counters['final_output_created_count']}",
        "",
        "ACT 4 — LGT IS DEFERRED PLACEHOLDER ONLY",
        "lgt_absent_or_local_signal_remains_advisory",
        "LGT is deferred/local placeholder only.",
        f"lgt_deferred_count: {counters['lgt_deferred_count']}",
        f"lgt_authority_claimed_count: {counters['lgt_authority_claimed_count']}",
        "",
        "ACT 5 — SAFETY PRESSURE OVERRIDES HIGH SCORE",
        "stale_high_score_candidate_cannot_silent_accept",
        "quarantine_deadend_overrides_high_score_to_review",
        "conflicting_provenance_blocks_advisory_accept",
        "duplicate_spam_cannot_force_gt_lgt_accept",
        "Stale, quarantine/deadend, conflict, and duplicate-spam pressure block or force review even when AVF rank is high.",
        "",
        "ACT 6 — ROOT FINAL AUTHORITY PRESERVED",
        "root_final_authority_preserved_across_gt_lgt_advisory",
        "Root remains final authority.",
        f"root_final_authority_preserved_count: {counters['root_final_authority_preserved_count']}",
        "",
        "COUNTERS",
        f"underlying_runtime_status: {result['final_status']}",
        f"scenarios_total: {result['scenarios_total']}",
        f"scenarios_passed: {result['scenarios_passed']}",
        f"advisory_inputs_count: {counters['advisory_inputs_count']}",
        f"gt_signals_emitted_count: {counters['gt_signals_emitted_count']}",
        f"lgt_signals_emitted_count: {counters['lgt_signals_emitted_count']}",
        f"lgt_deferred_count: {counters['lgt_deferred_count']}",
        f"advisory_reports_created_count: {counters['advisory_reports_created_count']}",
        f"root_review_required_count: {counters['root_review_required_count']}",
        f"root_final_authority_preserved_count: {counters['root_final_authority_preserved_count']}",
        f"direct_reuse_allowed_count: {counters['direct_reuse_allowed_count']}",
        f"action_permission_granted_count: {counters['action_permission_granted_count']}",
        f"final_output_created_count: {counters['final_output_created_count']}",
        f"gt_authority_claimed_count: {counters['gt_authority_claimed_count']}",
        f"lgt_authority_claimed_count: {counters['lgt_authority_claimed_count']}",
        f"advisory_truth_claimed_count: {counters['advisory_truth_claimed_count']}",
        f"advisory_accept_as_root_final_count: {counters['advisory_accept_as_root_final_count']}",
        f"network_used_count: {counters['network_used_count']}",
        f"gemini_used_count: {counters['gemini_used_count']}",
        f"walkthrough_required_counters_match: {counters_match}",
        "",
        "LIMITATIONS",
        "No production GT/LGT.",
        "No production LGT.",
        "No canonical GTValidator relocation.",
        "No Architect command.",
        "No Root behavior modification.",
        "No FinalOutput authority.",
        "No production DRS/AVF.",
        "No external/global DRS.",
        "No network/Gemini.",
        "No embeddings.",
        "No LLM semantic matching.",
        "No Fractal Cell Runtime integration.",
        "No Marennya/UP.",
        "No manifest mutation.",
        "No transition matrix mutation.",
        "Real Semantic Runtime MVP is not complete.",
        "",
        "FINAL HUMAN SUMMARY",
        "The layer is a small candidate advisory review stage.",
        "It can label AVF-ranked memory candidates as advisory accept/degrade/reject/needs-review, but it cannot decide truth, cannot command Architect, cannot create FinalOutput, and cannot move canonical GTValidator upstream.",
        "Root remains final authority.",
        "",
        "scenario coverage:",
        *SCENARIOS,
    ]
    return "\n".join(lines)


def main() -> int:
    output = build_walkthrough()
    print(output)
    return 0 if "walkthrough_required_counters_match: True" in output else 1


if __name__ == "__main__":
    raise SystemExit(main())
