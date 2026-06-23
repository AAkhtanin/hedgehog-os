from __future__ import annotations

from typing import Any

from demo import run_candidate_vector_generator_avf_scoring_v01 as avf_runner
from hedgehog.gt_lgt_advisory_evaluator import (
    GTLGTAdvisoryReport,
    evaluate_candidate_report,
)


TITLE = "HEDGEHOG OS — GT/LGT ADVISORY EVALUATOR v0.1"

SCENARIOS = (
    "avf_ranked_report_becomes_advisory_input_only",
    "gt_accept_signal_requires_root_final_review",
    "gt_degrade_signal_routes_to_review_not_final",
    "gt_reject_signal_blocks_candidate_not_root_final",
    "lgt_absent_or_local_signal_remains_advisory",
    "stale_high_score_candidate_cannot_silent_accept",
    "quarantine_deadend_overrides_high_score_to_review",
    "conflicting_provenance_blocks_advisory_accept",
    "duplicate_spam_cannot_force_gt_lgt_accept",
    "root_final_authority_preserved_across_gt_lgt_advisory",
)

SOURCE_SCENARIOS = {
    "avf_ranked_report_becomes_advisory_input_only": (
        "drs_resolved_candidates_generate_candidate_vectors"
    ),
    "gt_accept_signal_requires_root_final_review": (
        "high_score_candidate_still_requires_gt_lgt_root_review"
    ),
    "gt_degrade_signal_routes_to_review_not_final": (
        "stale_candidate_gets_review_required_penalty"
    ),
    "gt_reject_signal_blocks_candidate_not_root_final": (
        "quarantine_deadend_candidate_blocked_from_top_reuse"
    ),
    "lgt_absent_or_local_signal_remains_advisory": (
        "drs_resolved_candidates_generate_candidate_vectors"
    ),
    "stale_high_score_candidate_cannot_silent_accept": (
        "stale_candidate_gets_review_required_penalty"
    ),
    "quarantine_deadend_overrides_high_score_to_review": (
        "quarantine_deadend_candidate_blocked_from_top_reuse"
    ),
    "conflicting_provenance_blocks_advisory_accept": (
        "conflicting_provenance_penalizes_or_blocks_candidate"
    ),
    "duplicate_spam_cannot_force_gt_lgt_accept": (
        "duplicate_spam_candidates_do_not_win_by_volume"
    ),
    "root_final_authority_preserved_across_gt_lgt_advisory": (
        "root_final_authority_preserved_across_avf_scoring"
    ),
}


def _gt_signal(report: GTLGTAdvisoryReport):
    return next(signal for signal in report.signals if signal.signal_kind == "gt")


def _lgt_signal(report: GTLGTAdvisoryReport):
    return next(signal for signal in report.signals if signal.signal_kind.startswith("lgt_"))


def _base_pass(report: GTLGTAdvisoryReport) -> bool:
    counters = report.counters
    return (
        report.root_review_required
        and report.direct_reuse_allowed_count == 0
        and report.action_permission_granted_count == 0
        and report.final_output_created_count == 0
        and report.root_final_authority_preserved
        and counters["direct_reuse_allowed_count"] == 0
        and counters["action_permission_granted_count"] == 0
        and counters["final_output_created_count"] == 0
        and counters["gt_authority_claimed_count"] == 0
        and counters["lgt_authority_claimed_count"] == 0
        and counters["advisory_truth_claimed_count"] == 0
        and counters["advisory_accept_as_root_final_count"] == 0
        and counters["manifest_mutation_count"] == 0
        and counters["transition_matrix_mutation_count"] == 0
        and counters["network_used_count"] == 0
        and counters["gemini_used_count"] == 0
    )


def _scenario_passed(scenario_id: str, report: GTLGTAdvisoryReport) -> bool:
    gt_signal = _gt_signal(report)
    lgt_signal = _lgt_signal(report)
    reasons = set(report.reason_codes)
    if not _base_pass(report):
        return False
    if scenario_id == "avf_ranked_report_becomes_advisory_input_only":
        return (
            gt_signal.signal_kind == "gt"
            and "gt_signal_advisory_only" in reasons
            and report.candidate_count > 0
        )
    if scenario_id == "gt_accept_signal_requires_root_final_review":
        return gt_signal.advisory_decision == "accept_candidate" and (
            "gt_accept_signal_requires_root_final_review" in reasons
        )
    if scenario_id == "gt_degrade_signal_routes_to_review_not_final":
        return gt_signal.advisory_decision == "degrade_candidate" and (
            "gt_degrade_signal_routes_to_review_not_final" in reasons
        )
    if scenario_id == "gt_reject_signal_blocks_candidate_not_root_final":
        return gt_signal.advisory_decision == "reject_candidate" and (
            "gt_reject_signal_blocks_candidate_not_root_final" in reasons
        )
    if scenario_id == "lgt_absent_or_local_signal_remains_advisory":
        return (
            lgt_signal.signal_kind == "lgt_deferred"
            and lgt_signal.authority_claimed is False
            and "lgt_absent_or_local_signal_remains_advisory" in reasons
        )
    if scenario_id == "stale_high_score_candidate_cannot_silent_accept":
        return gt_signal.advisory_decision != "accept_candidate" and (
            "stale_high_score_candidate_cannot_silent_accept" in reasons
        )
    if scenario_id == "quarantine_deadend_overrides_high_score_to_review":
        return gt_signal.advisory_decision != "accept_candidate" and (
            "quarantine_deadend_overrides_high_score_to_review" in reasons
        )
    if scenario_id == "conflicting_provenance_blocks_advisory_accept":
        return gt_signal.advisory_decision != "accept_candidate" and (
            "conflicting_provenance_blocks_advisory_accept" in reasons
        )
    if scenario_id == "duplicate_spam_cannot_force_gt_lgt_accept":
        return gt_signal.advisory_decision != "accept_candidate" and (
            "duplicate_spam_cannot_force_gt_lgt_accept" in reasons
        )
    if scenario_id == "root_final_authority_preserved_across_gt_lgt_advisory":
        return "root_final_authority_preserved_across_gt_lgt_advisory" in reasons
    raise ValueError(f"unknown scenario: {scenario_id}")


def evaluate_scenario(scenario_id: str) -> dict[str, Any]:
    source = avf_runner.evaluate_scenario(SOURCE_SCENARIOS[scenario_id])
    report = evaluate_candidate_report(
        source["report"],
        report_id=scenario_id,
        lgt_status="deferred",
    )
    return {
        "scenario_id": scenario_id,
        "source_scenario_id": source["scenario_id"],
        "status": "PASS" if _scenario_passed(scenario_id, report) else "FAIL",
        "report": report,
        "candidate_count": report.candidate_count,
        "gt_decision": _gt_signal(report).advisory_decision,
        "lgt_status": _lgt_signal(report).signal_kind,
        "recommended_review_route": report.recommended_review_route,
        "reason_codes": report.reason_codes,
    }


def _empty_counters() -> dict[str, int]:
    return {
        "advisory_inputs_count": 0,
        "gt_signals_emitted_count": 0,
        "lgt_signals_emitted_count": 0,
        "lgt_deferred_count": 0,
        "advisory_reports_created_count": 0,
        "advisory_accept_count": 0,
        "advisory_degrade_count": 0,
        "advisory_reject_count": 0,
        "advisory_needs_review_count": 0,
        "direct_reuse_allowed_count": 0,
        "action_permission_granted_count": 0,
        "final_output_created_count": 0,
        "gt_authority_claimed_count": 0,
        "lgt_authority_claimed_count": 0,
        "advisory_truth_claimed_count": 0,
        "advisory_accept_as_root_final_count": 0,
        "high_score_forced_accept_count": 0,
        "duplicate_spam_forced_accept_count": 0,
        "stale_silent_accept_count": 0,
        "quarantine_deadend_override_count": 0,
        "conflicting_provenance_hidden_count": 0,
        "manifest_mutation_count": 0,
        "transition_matrix_mutation_count": 0,
        "network_used_count": 0,
        "gemini_used_count": 0,
        "root_review_required_count": 0,
        "root_final_authority_preserved_count": 0,
    }


def run_all_scenarios() -> dict[str, Any]:
    scenarios = [evaluate_scenario(scenario_id) for scenario_id in SCENARIOS]
    counters = _empty_counters()
    for scenario in scenarios:
        report = scenario["report"]
        for key, value in report.counters.items():
            if key in counters:
                counters[key] += value
    scenarios_passed = sum(1 for scenario in scenarios if scenario["status"] == "PASS")
    pass_conditions = {
        "scenarios_total_is_10": len(scenarios) == 10,
        "scenarios_passed": scenarios_passed == len(scenarios),
        "direct_reuse_allowed_count_zero": counters["direct_reuse_allowed_count"] == 0,
        "action_permission_granted_count_zero": (
            counters["action_permission_granted_count"] == 0
        ),
        "final_output_created_count_zero": counters["final_output_created_count"] == 0,
        "gt_authority_claimed_count_zero": counters["gt_authority_claimed_count"] == 0,
        "lgt_authority_claimed_count_zero": counters["lgt_authority_claimed_count"] == 0,
        "advisory_truth_claimed_count_zero": (
            counters["advisory_truth_claimed_count"] == 0
        ),
        "advisory_accept_as_root_final_count_zero": (
            counters["advisory_accept_as_root_final_count"] == 0
        ),
        "high_score_forced_accept_count_zero": (
            counters["high_score_forced_accept_count"] == 0
        ),
        "duplicate_spam_forced_accept_count_zero": (
            counters["duplicate_spam_forced_accept_count"] == 0
        ),
        "stale_silent_accept_count_zero": counters["stale_silent_accept_count"] == 0,
        "quarantine_deadend_override_count_zero": (
            counters["quarantine_deadend_override_count"] == 0
        ),
        "conflicting_provenance_hidden_count_zero": (
            counters["conflicting_provenance_hidden_count"] == 0
        ),
        "manifest_mutation_count_zero": counters["manifest_mutation_count"] == 0,
        "transition_matrix_mutation_count_zero": (
            counters["transition_matrix_mutation_count"] == 0
        ),
        "network_used_count_zero": counters["network_used_count"] == 0,
        "gemini_used_count_zero": counters["gemini_used_count"] == 0,
        "root_final_authority_preserved": (
            counters["root_final_authority_preserved_count"] == len(scenarios)
        ),
    }
    return {
        "title": TITLE,
        "scenarios": scenarios,
        "scenarios_total": len(scenarios),
        "scenarios_passed": scenarios_passed,
        "counters": counters,
        "pass_conditions": pass_conditions,
        "final_status": "PASS" if all(pass_conditions.values()) else "FAIL",
    }


def render_report(result: dict[str, Any] | None = None) -> str:
    result = result or run_all_scenarios()
    lines = [
        TITLE,
        "",
        "pipeline:",
        "DRS resolved candidates",
        "→ CandidateVectors",
        "→ AVF scored/ranked reports",
        "→ GT/LGT advisory evaluation",
        "→ Root review/final authority still required",
        "",
        "scenario table:",
        "scenario_id | status | gt_decision | lgt_status | review_route | reasons",
    ]
    for scenario in result["scenarios"]:
        lines.append(
            f"{scenario['scenario_id']} | {scenario['status']} | "
            f"{scenario['gt_decision']} | {scenario['lgt_status']} | "
            f"{scenario['recommended_review_route']} | "
            f"{', '.join(scenario['reason_codes'])}"
        )
    lines.extend(["", "aggregate counters:"])
    lines.append(f"scenarios_total: {result['scenarios_total']}")
    lines.append(f"scenarios_passed: {result['scenarios_passed']}")
    for key in sorted(result["counters"]):
        lines.append(f"{key}: {result['counters'][key]}")
    lines.extend(
        [
            "",
            "authority boundary summary:",
            "GT is advisory",
            "LGT is advisory or deferred",
            "GT/LGT report is not truth",
            "GT/LGT report is not Root Final",
            "GT/LGT advisory accept is not action permission",
            "GT/LGT advisory accept is not direct reuse permission",
            "AVF score is not authority",
            "Candidate vector is not truth",
            "DRS hit is not authority",
            "DRS reuse candidate is not action permission",
            "Root remains final authority",
            "",
            "limitations:",
            "local deterministic advisory evaluator only",
            "no production GT/LGT",
            "no production DRS",
            "no production AVF",
            "no external/global DRS",
            "no network",
            "no Gemini",
            "no embeddings",
            "no LLM semantic matching",
            "no autonomous action",
            "no connector side effects",
            "no manifest mutation",
            "no transition matrix mutation",
            "no RootOrchestrator modification",
            "no FinalOutput creation",
            "Real Semantic Runtime MVP is not complete",
            "",
            f"FINAL STATUS: {result['final_status']}",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    result = run_all_scenarios()
    print(render_report(result))
    return 0 if result["final_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
