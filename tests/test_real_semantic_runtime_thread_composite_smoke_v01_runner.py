from __future__ import annotations

import subprocess
import sys

import demo.run_real_semantic_runtime_thread_composite_smoke_v01 as smoke


def test_module_imports_and_main_returns_zero(capsys) -> None:
    assert smoke.TITLE.startswith("HEDGEHOG OS")
    assert smoke.main() == 0
    output = capsys.readouterr().out
    assert smoke.TITLE in output
    assert "FINAL STATUS: PASS" in output


def test_command_execution_exits_zero() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "demo.run_real_semantic_runtime_thread_composite_smoke_v01",
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    assert smoke.TITLE in completed.stdout
    assert "FINAL STATUS: PASS" in completed.stdout


def test_output_includes_invoked_layers_and_scenario_totals() -> None:
    output = smoke.render_report()

    for layer_name in smoke.LAYER_NAMES:
        assert layer_name in output
    required_lines = (
        "drs_scenarios_total: 8",
        "avf_scenarios_total: 9",
        "advisory_scenarios_total: 10",
        "bounded_actor_scenarios_total: 12",
        "fractal_cell_scenarios_total: 12",
        "composite_layers_total: 5",
        "composite_layers_passed: 5",
        "composite_scenarios_total: 51",
        "composite_required_scenarios_present: True",
    )
    for line in required_lines:
        assert line in output


def test_structured_result_contains_all_imported_scenarios() -> None:
    result = smoke.run_composite_smoke()
    layer_scenarios = {
        "drs": smoke.DRS_SCENARIOS,
        "avf": smoke.AVF_SCENARIOS,
        "advisory": smoke.ADVISORY_SCENARIOS,
        "bounded_actor": smoke.ACTOR_SCENARIOS,
        "fractal_cell": smoke.FRACTAL_SCENARIOS,
    }

    assert result["composite_required_scenarios_present"] is True
    assert result["composite_required_counter_keys_present"] is True
    assert result["missing_required_counter_keys"] == {}
    for layer_id, scenario_ids in layer_scenarios.items():
        observed = {
            scenario["scenario_id"] for scenario in result["layers"][layer_id]["scenarios"]
        }
        assert set(scenario_ids) <= observed


def test_missing_required_counter_key_fails_composite_smoke(monkeypatch) -> None:
    results = smoke.collect_layer_results()
    results["drs"]["counters"].pop("direct_reuse_allowed_count")
    monkeypatch.setattr(smoke, "collect_layer_results", lambda: results)

    result = smoke.run_composite_smoke()

    assert result["composite_required_counter_keys_present"] is False
    assert result["missing_required_counter_keys"] == {
        "drs": ("direct_reuse_allowed_count",)
    }
    assert result["pass_conditions"]["required_counter_keys_present"] is False
    assert result["final_status"] == "FAIL"


def test_output_includes_aggregate_zero_counters_and_optional_live_defaults() -> None:
    output = smoke.render_report()

    required_counter_lines = (
        "composite_required_counters_match: True",
        "composite_required_counter_keys_present: True",
        "missing_required_counter_keys: {}",
        "composite_direct_reuse_allowed_count: 0",
        "composite_action_permission_granted_count: 0",
        "composite_final_output_created_by_non_root_count: 0",
        "composite_authority_claimed_by_non_root_count: 0",
        "composite_truth_claimed_by_non_root_count: 0",
        "composite_poisoning_or_spam_authority_claimed_count: 0",
        "composite_high_score_or_advisory_forced_accept_count: 0",
        "composite_silent_or_hidden_safety_failure_count: 0",
        "composite_actor_escalation_or_raw_command_accept_count: 0",
        "composite_root_boundary_bypass_count: 0",
        "composite_parent_boundary_bypass_count: 0",
        "composite_post_vv_bypass_count: 0",
        "composite_gt_bypass_count: 0",
        "composite_child_boundary_violation_count: 0",
        "composite_network_used_count: 0",
        "composite_gemini_used_count: 0",
        "composite_connector_side_effect_count: 0",
        "composite_production_or_external_drs_used_count: 0",
        "composite_manifest_mutation_count: 0",
        "composite_transition_matrix_mutation_count: 0",
        "optional_live_llm_lane_default_enabled: False",
        "optional_live_llm_core_pass_dependency: False",
        "live_llm_authority_claimed_count: 0",
        "live_llm_final_output_created_count: 0",
        "full_e2e_claimed_count: 0",
        "production_readiness_claimed_count: 0",
        "root_final_authority_preserved_across_thread: True",
    )
    for line in required_counter_lines:
        assert line in output


def test_output_includes_authority_boundaries_and_limitations() -> None:
    output = smoke.render_report()

    required_markers = (
        "DRS record is not truth",
        "DRS hit is not authority",
        "Candidate vector is not truth",
        "AVF score is not authority",
        "Top-ranked candidate is not action permission",
        "GT-style advisory signal is not Root Final",
        "LGT is deferred/local placeholder only",
        "actor output is not truth",
        "actor output is not authority",
        "actor output is not action permission",
        "actor output is not FinalOutput",
        "Fractal Cell is not Root",
        "child ResultProposal is not FinalOutput",
        "child cell output must return to parent/Root boundary",
        "Post V&V fallback fails closed",
        "Root remains final authority",
        "This composite smoke is deterministic and machine-checking only.",
        "Real Semantic Runtime MVP is not complete.",
    )
    for marker in required_markers:
        assert marker in output


def test_output_does_not_claim_production_public_or_completion_readiness() -> None:
    output = smoke.render_report()
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
