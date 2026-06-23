from __future__ import annotations

import subprocess
import sys

import demo.run_human_avf_candidate_advisory_evaluator_walkthrough_v01 as walkthrough


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

COUNTERS = (
    "underlying_runtime_status: PASS",
    "scenarios_total: 10",
    "scenarios_passed: 10",
    "advisory_inputs_count: 10",
    "gt_signals_emitted_count: 10",
    "lgt_signals_emitted_count: 10",
    "lgt_deferred_count: 10",
    "advisory_reports_created_count: 10",
    "root_review_required_count: 10",
    "root_final_authority_preserved_count: 10",
    "direct_reuse_allowed_count: 0",
    "action_permission_granted_count: 0",
    "final_output_created_count: 0",
    "gt_authority_claimed_count: 0",
    "lgt_authority_claimed_count: 0",
    "advisory_truth_claimed_count: 0",
    "advisory_accept_as_root_final_count: 0",
    "network_used_count: 0",
    "gemini_used_count: 0",
    "walkthrough_required_counters_match: True",
)


def test_module_imports_and_main_returns_zero() -> None:
    assert walkthrough.main() == 0


def test_command_exits_zero_and_prints_title() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "demo.run_human_avf_candidate_advisory_evaluator_walkthrough_v01",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    assert (
        "HEDGEHOG OS — HUMAN AVF CANDIDATE ADVISORY EVALUATOR WALKTHROUGH v0.1"
        in completed.stdout
    )


def test_output_includes_sections_scenarios_topology_and_counters() -> None:
    output = walkthrough.build_walkthrough()

    for heading in SECTION_HEADINGS:
        assert heading in output
    for scenario in SCENARIOS:
        assert scenario in output
    for counter in COUNTERS:
        assert counter in output

    required_phrases = (
        "TOPOLOGY CLARIFICATION",
        "does not relocate canonical terminal GTValidator",
        "pre-Architect candidate-level advisory review",
        "does not command Architect",
        "LGT is deferred/local placeholder only",
        "AVF Candidate Advisory Evaluator",
        "GT-style advisory signal",
        "Root remains final authority",
        "Real Semantic Runtime MVP is not complete",
    )
    for phrase in required_phrases:
        assert phrase in output


def test_output_does_not_claim_public_or_runtime_completion() -> None:
    output = walkthrough.build_walkthrough()
    forbidden = (
        "production " + "ready",
        "public auditor " + "ready",
        "public launch " + "ready",
        "whitepaper " + "ready",
        "runtime " + "complete",
        "canonical GT moved upstream",
        "GTValidator " + "relocated",
        "Architect commanded by advisory",
        "GT is " + "authority",
        "LGT is " + "authority",
        "GT/LGT report is " + "truth",
        "GT/LGT report is Root " + "Final",
    )

    for marker in forbidden:
        assert marker not in output
