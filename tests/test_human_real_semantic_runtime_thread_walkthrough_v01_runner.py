from __future__ import annotations

import subprocess
import sys

import demo.run_human_real_semantic_runtime_thread_walkthrough_v01 as walkthrough


def test_module_imports_and_main_returns_zero(capsys) -> None:
    assert walkthrough.TITLE.startswith("HEDGEHOG OS")
    assert walkthrough.main() == 0
    output = capsys.readouterr().out
    assert walkthrough.TITLE in output
    assert "walkthrough_required_counters_match: True" in output


def test_command_execution_exits_zero() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "demo.run_human_real_semantic_runtime_thread_walkthrough_v01",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    assert walkthrough.TITLE in completed.stdout
    assert "FINAL HUMAN SUMMARY" in completed.stdout


def test_output_includes_required_section_headings() -> None:
    output = walkthrough.build_walkthrough()

    assert walkthrough.TITLE in output
    for heading in walkthrough.SECTION_HEADINGS:
        assert heading in output


def test_output_includes_layer_scenarios_and_actor_roles() -> None:
    output = walkthrough.build_walkthrough()

    for scenario_id in walkthrough.DRS_SCENARIOS:
        assert scenario_id in output
    for scenario_id in walkthrough.AVF_SCENARIOS:
        assert scenario_id in output
    for scenario_id in walkthrough.ADVISORY_SCENARIOS:
        assert scenario_id in output
    for scenario_id in walkthrough.ACTOR_SCENARIOS:
        assert scenario_id in output
    for scenario_id in walkthrough.FRACTAL_SCENARIOS:
        assert scenario_id in output

    for role_name in (
        "Intake",
        "Orchestrator",
        "Architect",
        "Executor",
        "Verifier",
        "Root boundary",
    ):
        assert role_name in output


def test_output_includes_required_boundary_markers() -> None:
    output = walkthrough.build_walkthrough()

    required_markers = (
        "Root-shaped request",
        "semantic memory write/resolve",
        "candidate vectors",
        "AVF scoring/ranking",
        "candidate advisory review",
        "bounded LLM/SLM actor contracts",
        "bounded Fractal Cell child execution",
        "parent Post V&V / GT route",
        "Root remains final authority",
        "DRS record is not truth",
        "DRS hit is not authority",
        "Candidate vector is not truth",
        "AVF score is not authority",
        "Top-ranked candidate is not action permission",
        "does not relocate canonical terminal GTValidator",
        "LGT is deferred/local placeholder only",
        "actor output is not authority",
        "actor output is not FinalOutput",
        "optional_live_llm_lane_default_enabled: False",
        "optional_live_llm_core_pass_dependency: False",
        "live LLM output is not authority",
        "Fractal Cell is not Root",
        "child ResultProposal is not FinalOutput",
        "child_target_boundary_blocked",
        "Post V&V fallback fails closed",
        "post_vv_runtime_unavailable_review_required",
        "post_vv_fallback_not_authority",
        "child_output_requires_real_post_vv_or_root_review",
        "post_vv_fallback_used_review_required",
        "Real Semantic Runtime MVP is not complete",
    )
    for marker in required_markers:
        assert marker in output


def test_output_includes_historical_spine_and_safety_pack_names() -> None:
    output = walkthrough.build_walkthrough()

    for marker in walkthrough.HISTORICAL_CANONICAL_SPINE:
        assert marker in output
    for marker in walkthrough.SAFETY_PACKS:
        assert marker in output
    for marker in walkthrough.HISTORICAL_CLOSED_LAYER_CATALOG:
        assert marker in output
    for marker in walkthrough.OPTIONAL_LIVE_LLM_EVIDENCE_PATHS:
        assert marker in output


def test_output_includes_composite_human_scenario_ids() -> None:
    output = walkthrough.build_walkthrough()

    for scenario_id in walkthrough.COMPOSITE_HUMAN_SCENARIO_IDS:
        assert scenario_id in output


def test_output_includes_combined_counters() -> None:
    output = walkthrough.build_walkthrough()

    required_counter_lines = (
        "walkthrough_required_counters_match: True",
        "closed_layers_invoked_count: 5",
        "closed_layers_status_pass_count: 5",
        "combined_direct_reuse_allowed_count: 0",
        "combined_action_permission_granted_count: 0",
        "combined_final_output_created_by_non_root_count: 0",
        "combined_authority_claimed_by_non_root_count: 0",
        "combined_parent_boundary_bypass_count: 0",
        "combined_post_vv_bypass_count: 0",
        "combined_gt_bypass_count: 0",
        "combined_network_used_count: 0",
        "combined_gemini_used_count: 0",
        "optional_live_llm_lane_default_enabled: False",
        "optional_live_llm_core_pass_dependency: False",
        "root_final_authority_preserved_across_thread: True",
        "full_e2e_claimed_count: 0",
        "production_readiness_claimed_count: 0",
        "historical_closed_layers_listed_count:",
        "optional_live_llm_evidence_paths_listed_count:",
        "live_llm_authority_claimed_count: 0",
        "live_llm_final_output_created_count: 0",
    )
    for line in required_counter_lines:
        assert line in output


def test_output_includes_validation_summary_commits() -> None:
    output = walkthrough.build_walkthrough()

    required_markers = (
        "DRS runtime commit: 2a18df5",
        "DRS technical audit: 6bb2422",
        "DRS checkpoint: 4f513d1",
        "CandidateVector/AVF runtime commit: 1506eea",
        "CandidateVector/AVF technical audit: cf3da99",
        "CandidateVector/AVF checkpoint: 762239c",
        "AVF Candidate Advisory runtime commit: b0ce686",
        "AVF Candidate Advisory technical audit: 7cbcb77",
        "AVF Candidate Advisory human walkthrough: 5f7cfe7",
        "AVF Candidate Advisory human audit: bc80aae",
        "Bounded LLM/SLM Actors runtime commit: 6802d14",
        "Bounded LLM/SLM Actors technical audit: dfd43b9",
        "Bounded LLM/SLM Actors human walkthrough: df45900",
        "Bounded LLM/SLM Actors human audit: 388749c",
        "Bounded LLM/SLM Actors checkpoint: 09523bf",
        "Bounded LLM/SLM Actors targeted tests: 92 passed, 50 warnings",
        "Bounded LLM/SLM Actors full pytest: 1819 passed, 60 warnings",
        "Fractal Cell runtime commit: 96755ba",
        "Fractal Cell technical audit: 643d6cd",
        "Fractal Cell human walkthrough: b6b53f8",
        "Fractal Cell human audit: 1f1a196",
        "Fractal Cell docs checkpoint: bc7ec63",
        "Fractal Cell full pytest: 1845 passed, 60 warnings",
    )
    for marker in required_markers:
        assert marker in output


def test_output_does_not_claim_production_public_or_completion_readiness() -> None:
    output = walkthrough.build_walkthrough()
    forbidden = (
        "production " + "ready",
        "public auditor " + "ready",
        "public " + "ready",
        "production E2E " + "implemented",
        "production Fractal Cell " + "implemented",
        "distributed runtime " + "implemented",
        "production DRS " + "implemented",
        "production AVF " + "implemented",
        "production GT " + "implemented",
        "production LGT " + "implemented",
        "external DRS " + "implemented",
        "global DRS " + "implemented",
        "network used: " + "true",
        "Gemini used: " + "true",
        "real model call " + "required",
        "LLM output is " + "authority",
        "Fractal Cell Runtime " + "implemented",
        "Root behavior " + "modified",
        "FinalOutput " + "created",
        "action permission " + "granted",
        "child cell " + "is Root",
        "child Root " + "implemented",
        "child consensus " + "is authority",
        "Real Semantic Runtime MVP " + "implemented",
        "runtime " + "complete",
        "full E2E " + "complete",
        "public launch " + "ready",
        "whitepaper " + "ready",
        "direct reuse " + "allowed",
        "AVF is " + "authority",
        "candidate vector is " + "truth",
    )

    for marker in forbidden:
        assert marker not in output
