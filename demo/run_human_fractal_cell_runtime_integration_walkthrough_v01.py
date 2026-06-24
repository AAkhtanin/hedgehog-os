from __future__ import annotations

import sys
from typing import Any

from demo.run_fractal_cell_runtime_integration_v01 import SCENARIOS, run_all_scenarios


TITLE = "HEDGEHOG OS — HUMAN FRACTAL CELL RUNTIME INTEGRATION WALKTHROUGH v0.1"

SECTION_HEADINGS = (
    "WHAT THIS WALKTHROUGH IS",
    "WHY THIS LAYER MATTERS",
    "CORE TOPOLOGY",
    "ACT 1 — ROOT-SHAPED TASK ENTERS FRACTAL CELL BOUNDARY",
    "ACT 2 — CHILD ACTORS STAY BOUNDED",
    "ACT 3 — CHILD FINALOUTPUT / SELF-PROMOTION IS BLOCKED",
    "ACT 4 — POST V&V FALLBACK FAILS CLOSED",
    "ACT 5 — RECURSION AND CONSENSUS DO NOT CREATE AUTHORITY",
    "ACT 6 — CHILD OUTPUT RETURNS TO PARENT ROUTE",
    "ACT 7 — ROOT FINAL AUTHORITY PRESERVED",
    "COUNTERS",
    "VALIDATION SUMMARY",
    "LIMITATIONS",
    "FINAL HUMAN SUMMARY",
)

ZERO_COUNTERS = (
    "final_output_created_count",
    "action_permission_granted_count",
    "child_root_claimed_count",
    "child_authority_claimed_count",
    "child_finaloutput_claimed_count",
    "child_action_permission_claimed_count",
    "child_actor_self_promotion_count",
    "parent_boundary_bypass_count",
    "post_vv_bypass_count",
    "gt_bypass_count",
    "parent_architect_commanded_count",
    "recursive_depth_limit_exceeded_count",
    "unbounded_child_spawn_count",
    "child_consensus_authority_claimed_count",
    "manifest_mutation_count",
    "transition_matrix_mutation_count",
    "network_used_count",
    "gemini_used_count",
    "connector_side_effect_count",
)


def _required_counters_match(result: dict[str, Any]) -> bool:
    counters = result["counters"]
    return (
        result["final_status"] == "PASS"
        and result["scenarios_total"] == 12
        and result["scenarios_passed"] == 12
        and all(counters[key] == 0 for key in ZERO_COUNTERS)
        and counters["root_review_required_count"] >= 1
        and "post_vv_fallback_used_count" in counters
        and counters["root_final_authority_preserved_count"] == 12
    )


def build_walkthrough() -> str:
    result = run_all_scenarios()
    counters = result["counters"]
    counters_match = _required_counters_match(result)

    lines = [
        TITLE,
        "",
        "WHAT THIS WALKTHROUGH IS",
        "This walkthrough explains the already audited Fractal Cell Runtime Integration v0.1.",
        "It creates no new runtime capability, no production Fractal Cell runtime, no distributed runtime, no Root behavior, no FinalOutput authority, and no connector/action behavior.",
        "",
        "WHY THIS LAYER MATTERS",
        "After bounded LLM/SLM actor contracts, the system can place bounded actors inside a child cell.",
        "The child cell can run a bounded internal actor chain, but it cannot become Root.",
        "This layer tests recursive containment, not autonomy.",
        "",
        "CORE TOPOLOGY",
        "Parent Root / Orchestrator",
        "→ Root-shaped task / route",
        "→ Fractal Cell boundary",
        "→ bounded child actor chain",
        "→ child ResultProposal / cell report",
        "→ parent Post V&V / GT route",
        "→ parent Root final review",
        "Fractal Cell is not Root.",
        "child cell output must return to parent/Root boundary.",
        "bounded actor contracts apply inside child cell.",
        "Root remains final authority.",
        "",
        "ACT 1 — ROOT-SHAPED TASK ENTERS FRACTAL CELL BOUNDARY",
        "root_shaped_task_enters_fractal_cell_boundary",
        "Only Root-shaped task/route may enter the cell boundary.",
        "The child cell does not invent its own authority.",
        "",
        "ACT 2 — CHILD ACTORS STAY BOUNDED",
        "child_architect_accepts_only_root_shaped_task",
        "child_executor_outputs_resultproposal_only",
        "child_verifier_validates_without_finaloutput",
        "child_gt_report_returns_to_parent_root_boundary",
        "Child Architect is not Root.",
        "Child Executor is not Root.",
        "Child Verifier is not Root.",
        "Child GT/advisory report is not Root Final.",
        "",
        "ACT 3 — CHILD FINALOUTPUT / SELF-PROMOTION IS BLOCKED",
        "child_finaloutput_claim_is_blocked",
        "child_actor_self_promotion_to_root_is_blocked",
        "child_cell_cannot_command_parent_architect",
        "child_target_boundary_blocked",
        "child ResultProposal is not FinalOutput.",
        "child cell cannot command parent Architect.",
        "",
        "ACT 4 — POST V&V FALLBACK FAILS CLOSED",
        "Post V&V Fallback Boundary Fix",
        "If real Post V&V is unavailable, fallback Post V&V must fail closed as review-required / needs-revision, not accepted authority.",
        "post_vv_runtime_unavailable_review_required",
        "post_vv_fallback_not_authority",
        "child_output_requires_real_post_vv_or_root_review",
        "post_vv_fallback_used_review_required",
        "post_vv_fallback_used_count",
        "",
        "ACT 5 — RECURSION AND CONSENSUS DO NOT CREATE AUTHORITY",
        "recursive_child_cell_depth_is_bounded",
        "child_consensus_does_not_create_authority",
        "Recursive nesting depth is bounded.",
        "Child consensus is not Root Final.",
        "Child majority vote is not authority.",
        "Compute volume is not authority.",
        "",
        "ACT 6 — CHILD OUTPUT RETURNS TO PARENT ROUTE",
        "child_output_returns_to_parent_post_vv_gt_route",
        "A child cell can produce a child ResultProposal / cell report.",
        "That output must return upward through parent Post V&V / GT / Root review.",
        "It cannot bypass parent boundary.",
        "",
        "ACT 7 — ROOT FINAL AUTHORITY PRESERVED",
        "root_final_authority_preserved_across_fractal_cell",
        "Root remains final authority",
        f"root_final_authority_preserved_count: {counters['root_final_authority_preserved_count']}",
        "",
        "COUNTERS",
        f"underlying_runtime_status: {result['final_status']}",
        f"scenarios_total: {result['scenarios_total']}",
        f"scenarios_passed: {result['scenarios_passed']}",
        f"cells_started_count: {counters['cells_started_count']}",
        f"child_actor_inputs_seen_count: {counters['child_actor_inputs_seen_count']}",
        f"child_actor_outputs_emitted_count: {counters['child_actor_outputs_emitted_count']}",
        f"child_result_proposals_count: {counters['child_result_proposals_count']}",
        f"child_validation_reports_count: {counters['child_validation_reports_count']}",
        f"child_gt_reports_count: {counters['child_gt_reports_count']}",
        f"parent_return_reports_count: {counters['parent_return_reports_count']}",
        f"root_review_required_count: {counters['root_review_required_count']}",
        f"post_vv_fallback_used_count: {counters['post_vv_fallback_used_count']}",
        f"final_output_created_count: {counters['final_output_created_count']}",
        f"action_permission_granted_count: {counters['action_permission_granted_count']}",
        f"child_root_claimed_count: {counters['child_root_claimed_count']}",
        f"child_authority_claimed_count: {counters['child_authority_claimed_count']}",
        f"child_finaloutput_claimed_count: {counters['child_finaloutput_claimed_count']}",
        f"child_action_permission_claimed_count: {counters['child_action_permission_claimed_count']}",
        f"child_actor_self_promotion_count: {counters['child_actor_self_promotion_count']}",
        f"parent_boundary_bypass_count: {counters['parent_boundary_bypass_count']}",
        f"post_vv_bypass_count: {counters['post_vv_bypass_count']}",
        f"gt_bypass_count: {counters['gt_bypass_count']}",
        f"parent_architect_commanded_count: {counters['parent_architect_commanded_count']}",
        f"recursive_depth_limit_exceeded_count: {counters['recursive_depth_limit_exceeded_count']}",
        f"unbounded_child_spawn_count: {counters['unbounded_child_spawn_count']}",
        f"child_consensus_authority_claimed_count: {counters['child_consensus_authority_claimed_count']}",
        f"manifest_mutation_count: {counters['manifest_mutation_count']}",
        f"transition_matrix_mutation_count: {counters['transition_matrix_mutation_count']}",
        f"network_used_count: {counters['network_used_count']}",
        f"gemini_used_count: {counters['gemini_used_count']}",
        f"connector_side_effect_count: {counters['connector_side_effect_count']}",
        f"root_final_authority_preserved_count: {counters['root_final_authority_preserved_count']}",
        f"walkthrough_required_counters_match: {counters_match}",
        "",
        "VALIDATION SUMMARY",
        "- runtime commit: 96755ba",
        "- technical audit commit: 643d6cd",
        "- patch plan commit: 9f49cbc",
        "- preflight commit: 84303eb",
        "- previous checkpoint: 09523bf",
        "- runner: FINAL STATUS: PASS",
        "- targeted tests: 99 passed, 40 warnings",
        "- full pytest: 1845 passed, 60 warnings",
        "",
        "LIMITATIONS",
        "No production Fractal Cell runtime.",
        "No production distributed runtime.",
        "No external/global DRS.",
        "No network.",
        "No Gemini.",
        "No real model calls.",
        "No autonomous action.",
        "No connector side effects.",
        "No Marennya/UP.",
        "No manifest mutation.",
        "No transition matrix mutation.",
        "No Root behavior modification.",
        "No child Root.",
        "No child FinalOutput authority.",
        "No child action permission.",
        "No public WOW.",
        "No whitepaper/public auditor packet.",
        "Real Semantic Runtime MVP is not complete.",
        "",
        "FINAL HUMAN SUMMARY",
        "A Fractal Cell is a bounded recursive execution container.",
        "It can host bounded child actors and return child reports upward, but it cannot become Root, cannot create FinalOutput, cannot grant action permission, cannot bypass Post V&V/GT/Root, and cannot turn child consensus into authority.",
        "Root remains final authority.",
        "",
        "SCENARIO COVERAGE",
    ]
    lines.extend(SCENARIOS)
    return "\n".join(lines)


def main() -> int:
    output = build_walkthrough()
    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
