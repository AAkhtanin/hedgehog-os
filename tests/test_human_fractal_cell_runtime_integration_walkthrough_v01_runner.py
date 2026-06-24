from __future__ import annotations

import subprocess
import sys

import demo.run_human_fractal_cell_runtime_integration_walkthrough_v01 as walkthrough


def test_module_imports_and_main_returns_zero() -> None:
    assert walkthrough.TITLE.startswith("HEDGEHOG OS")
    assert walkthrough.main() == 0


def test_command_exits_zero() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "demo.run_human_fractal_cell_runtime_integration_walkthrough_v01"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0


def test_output_contains_required_sections_scenarios_and_boundaries() -> None:
    output = walkthrough.build_walkthrough()

    assert walkthrough.TITLE in output
    for heading in walkthrough.SECTION_HEADINGS:
        assert heading in output
    for scenario_id in walkthrough.SCENARIOS:
        assert scenario_id in output

    required_markers = (
        "Post V&V Fallback Boundary Fix",
        "post_vv_runtime_unavailable_review_required",
        "post_vv_fallback_not_authority",
        "child_output_requires_real_post_vv_or_root_review",
        "post_vv_fallback_used_review_required",
        "post_vv_fallback_used_count",
        "child_target_boundary_blocked",
        "Fractal Cell is not Root",
        "child ResultProposal is not FinalOutput",
        "child cell output must return to parent/Root boundary",
        "bounded actor contracts apply inside child cell",
        "Root remains final authority",
        "Real Semantic Runtime MVP is not complete",
    )
    for marker in required_markers:
        assert marker in output


def test_output_contains_required_counters() -> None:
    output = walkthrough.build_walkthrough()

    required_lines = (
        "underlying_runtime_status: PASS",
        "scenarios_total: 12",
        "scenarios_passed: 12",
        "cells_started_count:",
        "child_actor_inputs_seen_count:",
        "child_actor_outputs_emitted_count:",
        "child_result_proposals_count:",
        "child_validation_reports_count:",
        "child_gt_reports_count:",
        "parent_return_reports_count:",
        "root_review_required_count:",
        "post_vv_fallback_used_count:",
        "final_output_created_count: 0",
        "action_permission_granted_count: 0",
        "child_root_claimed_count: 0",
        "child_authority_claimed_count: 0",
        "child_finaloutput_claimed_count: 0",
        "child_action_permission_claimed_count: 0",
        "child_actor_self_promotion_count: 0",
        "parent_boundary_bypass_count: 0",
        "post_vv_bypass_count: 0",
        "gt_bypass_count: 0",
        "parent_architect_commanded_count: 0",
        "recursive_depth_limit_exceeded_count: 0",
        "unbounded_child_spawn_count: 0",
        "child_consensus_authority_claimed_count: 0",
        "manifest_mutation_count: 0",
        "transition_matrix_mutation_count: 0",
        "network_used_count: 0",
        "gemini_used_count: 0",
        "connector_side_effect_count: 0",
        "root_final_authority_preserved_count: 12",
        "walkthrough_required_counters_match: True",
    )
    for line in required_lines:
        assert line in output


def test_output_does_not_claim_production_public_or_complete_readiness() -> None:
    output = walkthrough.build_walkthrough()
    blocked_phrases = (
        "production " + "ready",
        "public auditor " + "ready",
        "production Fractal Cell " + "implemented",
        "distributed runtime " + "implemented",
        "external connector " + "implemented",
        "network used: " + "true",
        "Gemini " + "activated",
        "real model call " + "implemented",
        "Fractal Cell Runtime " + "implemented",
        "Root behavior " + "modified",
        "FinalOutput " + "created",
        "action permission " + "granted",
        "child cell " + "is Root",
        "child Root " + "implemented",
        "child consensus " + "is authority",
        "runtime " + "complete",
        "Real Semantic Runtime MVP " + "implemented",
        "public launch " + "ready",
        "whitepaper " + "ready",
    )

    for phrase in blocked_phrases:
        assert phrase not in output
