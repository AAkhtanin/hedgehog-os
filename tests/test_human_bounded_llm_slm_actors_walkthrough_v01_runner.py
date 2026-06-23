from __future__ import annotations

import subprocess
import sys

import demo.run_human_bounded_llm_slm_actors_walkthrough_v01 as walkthrough


SECTION_HEADINGS = (
    "WHAT THIS WALKTHROUGH IS",
    "WHY THIS LAYER MATTERS",
    "CORE RULE",
    "ACT 1 — INTAKE MAY NORMALIZE, NOT DECIDE",
    "ACT 2 — ORCHESTRATOR CONSUMES SIGNALS, NOT COMMANDS",
    "ACT 3 — ARCHITECT RECEIVES ONLY ROOT-SHAPED TASKS",
    "ACT 4 — EXECUTOR RECEIVES ONLY BOUNDED PLANGRAPH",
    "ACT 5 — VERIFIER / POST V&V VALIDATES, NOT FINALIZES",
    "ACT 6 — PROMPT INJECTION CANNOT PROMOTE ACTOR TO ROOT",
    "ACT 7 — TARGET BOUNDARY FIX",
    "ACT 8 — CANONICAL CHAIN IS STILL ALLOWED",
    "ACT 9 — ROOT FINAL AUTHORITY PRESERVED",
    "COUNTERS",
    "VALIDATION SUMMARY",
    "LIMITATIONS",
    "FINAL HUMAN SUMMARY",
)

SCENARIOS = (
    "intake_actor_normalizes_intent_without_authority",
    "orchestrator_actor_consumes_advisory_report_as_signal_only",
    "orchestrator_route_proposal_requires_root_boundary",
    "architect_actor_accepts_only_root_shaped_task",
    "architect_actor_outputs_plangraph_proposal_only",
    "executor_actor_accepts_only_bounded_plangraph",
    "executor_actor_outputs_resultproposal_only",
    "verifier_actor_validates_without_finaloutput",
    "prompt_injection_cannot_promote_actor_to_root",
    "actor_role_confusion_is_blocked",
    "model_confidence_does_not_create_authority",
    "root_final_authority_preserved_across_actor_chain",
)

ACTOR_ROLES = (
    "Intake Actor",
    "Orchestrator Actor",
    "Architect Actor",
    "Executor Actor",
    "Verifier/Post V&V",
    "GT boundary",
    "Root return",
)

DANGEROUS_TRANSITIONS = (
    "Architect PlanGraph -> final_output",
    "Architect PlanGraph -> root_return",
    "Executor ResultProposal -> final_output",
    "Executor ResultProposal -> root_return",
    "Verifier VVReport -> final_output",
    "Verifier VVReport -> root_return",
    "GTReport -> final_output",
    "GTReport -> Architect",
)

CANONICAL_CHAIN = (
    "intake -> Root/Orchestrator",
    "Root-shaped route -> Architect",
    "PlanGraph -> Executor",
    "ResultProposal -> Verifier/Post V&V",
    "VVReport -> GT boundary",
    "GTReport -> Root return",
    "Root return -> Root/Orchestrator",
)

COUNTERS = (
    "underlying_runtime_status: PASS",
    "scenarios_total: 12",
    "scenarios_passed: 12",
    "final_output_created_count: 0",
    "action_permission_granted_count: 0",
    "actor_authority_claimed_count: 0",
    "llm_truth_claimed_count: 0",
    "slm_truth_claimed_count: 0",
    "model_confidence_authority_claimed_count: 0",
    "prompt_injection_escalation_count: 0",
    "actor_self_promotion_count: 0",
    "raw_advisory_command_accepted_count: 0",
    "raw_drs_memory_instruction_accepted_count: 0",
    "root_boundary_bypass_count: 0",
    "post_vv_bypass_count: 0",
    "gt_bypass_count: 0",
    "network_used_count: 0",
    "gemini_used_count: 0",
    "connector_side_effect_count: 0",
    "root_final_authority_preserved_count: 12",
    "walkthrough_required_counters_match: True",
)


def test_module_imports_and_main_returns_zero() -> None:
    assert walkthrough.main() == 0


def test_command_exits_zero_and_prints_title() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "demo.run_human_bounded_llm_slm_actors_walkthrough_v01",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    assert (
        "HEDGEHOG OS — HUMAN BOUNDED LLM/SLM ACTORS WALKTHROUGH v0.1"
        in completed.stdout
    )


def test_output_includes_sections_scenarios_roles_boundaries_and_counters() -> None:
    output = walkthrough.build_walkthrough()

    for heading in SECTION_HEADINGS:
        assert heading in output
    for scenario in SCENARIOS:
        assert scenario in output
    for role in ACTOR_ROLES:
        assert role in output
    for transition in DANGEROUS_TRANSITIONS:
        assert transition in output
    for chain_link in CANONICAL_CHAIN:
        assert chain_link in output
    for counter in COUNTERS:
        assert counter in output

    required_phrases = (
        "Target Boundary Fix",
        "ACT 7 — TARGET BOUNDARY FIX",
        "final_output_target_boundary_blocked",
        "Root remains final authority",
        "Real Semantic Runtime MVP is not complete",
        "Fractal Cell Runtime integration depends on these bounded actor contracts.",
        "This layer does NOT create autonomous agents.",
        "This layer does NOT activate LLM/SLM/Gemini/network.",
    )
    for phrase in required_phrases:
        assert phrase in output


def test_output_includes_validation_summary() -> None:
    output = walkthrough.build_walkthrough()
    expected = (
        "runtime commit: 6802d14",
        "technical audit: dfd43b9",
        "targeted tests: 92 passed, 50 warnings",
        "full pytest: 1819 passed, 60 warnings",
        "runner: FINAL STATUS: PASS",
    )
    for marker in expected:
        assert marker in output


def test_output_does_not_claim_public_or_runtime_completion() -> None:
    output = walkthrough.build_walkthrough()
    forbidden = (
        "production " + "ready",
        "public auditor " + "ready",
        "public launch " + "ready",
        "whitepaper " + "ready",
        "runtime " + "complete",
        "Real Semantic Runtime MVP " + "implemented",
        "Gemini " + "activated",
        "network used: " + "true",
        "FinalOutput " + "created",
        "action permission " + "granted",
        "actor is " + "authority",
        "LLM is " + "authority",
        "SLM is " + "authority",
    )

    for marker in forbidden:
        assert marker not in output
