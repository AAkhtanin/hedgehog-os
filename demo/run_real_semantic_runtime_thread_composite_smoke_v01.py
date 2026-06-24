from __future__ import annotations

import sys
from typing import Any

from demo.run_bounded_llm_slm_actors_v01 import (
    SCENARIOS as ACTOR_SCENARIOS,
    run_all_scenarios as run_actor_scenarios,
)
from demo.run_candidate_vector_generator_avf_scoring_v01 import (
    SCENARIOS as AVF_SCENARIOS,
    run_all_scenarios as run_avf_scenarios,
)
from demo.run_fractal_cell_runtime_integration_v01 import (
    SCENARIOS as FRACTAL_SCENARIOS,
    run_all_scenarios as run_fractal_scenarios,
)
from demo.run_gt_lgt_advisory_evaluator_v01 import (
    SCENARIOS as ADVISORY_SCENARIOS,
    run_all_scenarios as run_advisory_scenarios,
)
from demo.run_real_local_drs_resolver_writeback_v01 import (
    SCENARIOS as DRS_SCENARIOS,
    run_all_scenarios as run_drs_scenarios,
)


TITLE = "HEDGEHOG OS — REAL SEMANTIC RUNTIME THREAD COMPOSITE SMOKE v0.1"

LAYER_NAMES = (
    "Real Local DRS Resolver / Writeback",
    "CandidateVectorGenerator + Real AVF Scoring",
    "AVF Candidate Advisory / GT-LGT Advisory",
    "Bounded LLM/SLM Actors",
    "Fractal Cell Runtime Integration",
)

EXPECTED_TOTALS = {
    "drs": 8,
    "avf": 9,
    "advisory": 10,
    "bounded_actor": 12,
    "fractal_cell": 12,
}

REQUIRED_COUNTER_KEYS_BY_LAYER = {
    "drs": (
        "root_final_authority_preserved_count",
        "direct_reuse_allowed_count",
        "action_permission_granted_count",
        "poisoning_pressure_authority_claimed_count",
        "network_used_count",
        "gemini_used_count",
        "production_drs_used_count",
        "external_drs_used_count",
        "manifest_mutation_count",
        "transition_matrix_mutation_count",
    ),
    "avf": (
        "root_final_authority_preserved_count",
        "direct_reuse_allowed_count",
        "action_permission_granted_count",
        "avf_authority_claimed_count",
        "vector_truth_claimed_count",
        "schema_validity_truth_claimed_count",
        "duplicate_spam_authority_claimed_count",
        "high_score_direct_reuse_granted_count",
        "network_used_count",
        "gemini_used_count",
        "manifest_mutation_count",
        "transition_matrix_mutation_count",
    ),
    "advisory": (
        "root_final_authority_preserved_count",
        "direct_reuse_allowed_count",
        "action_permission_granted_count",
        "final_output_created_count",
        "gt_authority_claimed_count",
        "lgt_authority_claimed_count",
        "advisory_truth_claimed_count",
        "high_score_forced_accept_count",
        "duplicate_spam_forced_accept_count",
        "advisory_accept_as_root_final_count",
        "stale_silent_accept_count",
        "quarantine_deadend_override_count",
        "conflicting_provenance_hidden_count",
        "network_used_count",
        "gemini_used_count",
        "manifest_mutation_count",
        "transition_matrix_mutation_count",
    ),
    "bounded_actor": (
        "root_final_authority_preserved_count",
        "action_permission_granted_count",
        "final_output_created_count",
        "actor_authority_claimed_count",
        "model_confidence_authority_claimed_count",
        "llm_truth_claimed_count",
        "slm_truth_claimed_count",
        "prompt_injection_escalation_count",
        "actor_self_promotion_count",
        "raw_advisory_command_accepted_count",
        "raw_drs_memory_instruction_accepted_count",
        "root_boundary_bypass_count",
        "post_vv_bypass_count",
        "gt_bypass_count",
        "network_used_count",
        "gemini_used_count",
        "connector_side_effect_count",
        "manifest_mutation_count",
        "transition_matrix_mutation_count",
    ),
    "fractal_cell": (
        "root_final_authority_preserved_count",
        "action_permission_granted_count",
        "final_output_created_count",
        "child_authority_claimed_count",
        "child_root_claimed_count",
        "parent_boundary_bypass_count",
        "post_vv_bypass_count",
        "gt_bypass_count",
        "child_finaloutput_claimed_count",
        "child_action_permission_claimed_count",
        "child_actor_self_promotion_count",
        "parent_architect_commanded_count",
        "recursive_depth_limit_exceeded_count",
        "unbounded_child_spawn_count",
        "child_consensus_authority_claimed_count",
        "network_used_count",
        "gemini_used_count",
        "connector_side_effect_count",
        "manifest_mutation_count",
        "transition_matrix_mutation_count",
    ),
}


def _counter(result: dict[str, Any], key: str) -> int:
    return int(result.get("counters", {}).get(key, 0))


def _scenario_names(result: dict[str, Any]) -> set[str]:
    return {scenario["scenario_id"] for scenario in result["scenarios"]}


def collect_layer_results() -> dict[str, dict[str, Any]]:
    return {
        "drs": run_drs_scenarios(),
        "avf": run_avf_scenarios(),
        "advisory": run_advisory_scenarios(),
        "bounded_actor": run_actor_scenarios(),
        "fractal_cell": run_fractal_scenarios(),
    }


def _required_scenarios_present(results: dict[str, dict[str, Any]]) -> bool:
    return (
        set(DRS_SCENARIOS) <= _scenario_names(results["drs"])
        and set(AVF_SCENARIOS) <= _scenario_names(results["avf"])
        and set(ADVISORY_SCENARIOS) <= _scenario_names(results["advisory"])
        and set(ACTOR_SCENARIOS) <= _scenario_names(results["bounded_actor"])
        and set(FRACTAL_SCENARIOS) <= _scenario_names(results["fractal_cell"])
    )


def _missing_required_counter_keys(
    results: dict[str, dict[str, Any]],
) -> dict[str, tuple[str, ...]]:
    missing: dict[str, tuple[str, ...]] = {}
    for layer_id, required_keys in REQUIRED_COUNTER_KEYS_BY_LAYER.items():
        observed_keys = set(results.get(layer_id, {}).get("counters", {}))
        missing_keys = tuple(key for key in required_keys if key not in observed_keys)
        if missing_keys:
            missing[layer_id] = missing_keys
    return missing


def _required_counter_keys_present(results: dict[str, dict[str, Any]]) -> bool:
    return not _missing_required_counter_keys(results)


def _root_authority_preserved(results: dict[str, dict[str, Any]]) -> bool:
    return (
        _counter(results["drs"], "root_final_authority_preserved_count")
        == results["drs"]["scenarios_total"]
        and _counter(results["avf"], "root_final_authority_preserved_count")
        == results["avf"]["scenarios_total"]
        and _counter(results["advisory"], "root_final_authority_preserved_count")
        == results["advisory"]["scenarios_total"]
        and _counter(results["bounded_actor"], "root_final_authority_preserved_count")
        == results["bounded_actor"]["scenarios_total"]
        and _counter(results["fractal_cell"], "root_final_authority_preserved_count")
        == results["fractal_cell"]["scenarios_total"]
    )


def _aggregate_counters(results: dict[str, dict[str, Any]]) -> dict[str, Any]:
    drs = results["drs"]
    avf = results["avf"]
    advisory = results["advisory"]
    actor = results["bounded_actor"]
    fractal = results["fractal_cell"]

    counters = {
        "composite_direct_reuse_allowed_count": (
            _counter(drs, "direct_reuse_allowed_count")
            + _counter(avf, "direct_reuse_allowed_count")
            + _counter(advisory, "direct_reuse_allowed_count")
        ),
        "composite_action_permission_granted_count": (
            _counter(drs, "action_permission_granted_count")
            + _counter(avf, "action_permission_granted_count")
            + _counter(advisory, "action_permission_granted_count")
            + _counter(actor, "action_permission_granted_count")
            + _counter(fractal, "action_permission_granted_count")
        ),
        "composite_final_output_created_by_non_root_count": (
            _counter(advisory, "final_output_created_count")
            + _counter(actor, "final_output_created_count")
            + _counter(fractal, "final_output_created_count")
        ),
        "composite_authority_claimed_by_non_root_count": (
            _counter(avf, "avf_authority_claimed_count")
            + _counter(advisory, "gt_authority_claimed_count")
            + _counter(advisory, "lgt_authority_claimed_count")
            + _counter(actor, "actor_authority_claimed_count")
            + _counter(actor, "model_confidence_authority_claimed_count")
            + _counter(fractal, "child_authority_claimed_count")
            + _counter(fractal, "child_root_claimed_count")
        ),
        "composite_truth_claimed_by_non_root_count": (
            _counter(avf, "vector_truth_claimed_count")
            + _counter(avf, "schema_validity_truth_claimed_count")
            + _counter(advisory, "advisory_truth_claimed_count")
            + _counter(actor, "llm_truth_claimed_count")
            + _counter(actor, "slm_truth_claimed_count")
        ),
        "composite_poisoning_or_spam_authority_claimed_count": (
            _counter(drs, "poisoning_pressure_authority_claimed_count")
            + _counter(avf, "duplicate_spam_authority_claimed_count")
        ),
        "composite_high_score_or_advisory_forced_accept_count": (
            _counter(avf, "high_score_direct_reuse_granted_count")
            + _counter(advisory, "high_score_forced_accept_count")
            + _counter(advisory, "duplicate_spam_forced_accept_count")
            + _counter(advisory, "advisory_accept_as_root_final_count")
        ),
        "composite_silent_or_hidden_safety_failure_count": (
            _counter(advisory, "stale_silent_accept_count")
            + _counter(advisory, "quarantine_deadend_override_count")
            + _counter(advisory, "conflicting_provenance_hidden_count")
        ),
        "composite_actor_escalation_or_raw_command_accept_count": (
            _counter(actor, "prompt_injection_escalation_count")
            + _counter(actor, "actor_self_promotion_count")
            + _counter(actor, "raw_advisory_command_accepted_count")
            + _counter(actor, "raw_drs_memory_instruction_accepted_count")
        ),
        "composite_root_boundary_bypass_count": _counter(
            actor,
            "root_boundary_bypass_count",
        )
        + _counter(fractal, "parent_boundary_bypass_count"),
        "composite_parent_boundary_bypass_count": _counter(
            fractal,
            "parent_boundary_bypass_count",
        ),
        "composite_post_vv_bypass_count": _counter(
            actor,
            "post_vv_bypass_count",
        )
        + _counter(fractal, "post_vv_bypass_count"),
        "composite_gt_bypass_count": _counter(actor, "gt_bypass_count")
        + _counter(fractal, "gt_bypass_count"),
        "composite_child_boundary_violation_count": (
            _counter(fractal, "child_finaloutput_claimed_count")
            + _counter(fractal, "child_action_permission_claimed_count")
            + _counter(fractal, "child_actor_self_promotion_count")
            + _counter(fractal, "parent_architect_commanded_count")
            + _counter(fractal, "recursive_depth_limit_exceeded_count")
            + _counter(fractal, "unbounded_child_spawn_count")
            + _counter(fractal, "child_consensus_authority_claimed_count")
        ),
        "composite_network_used_count": (
            _counter(drs, "network_used_count")
            + _counter(avf, "network_used_count")
            + _counter(advisory, "network_used_count")
            + _counter(actor, "network_used_count")
            + _counter(fractal, "network_used_count")
        ),
        "composite_gemini_used_count": (
            _counter(drs, "gemini_used_count")
            + _counter(avf, "gemini_used_count")
            + _counter(advisory, "gemini_used_count")
            + _counter(actor, "gemini_used_count")
            + _counter(fractal, "gemini_used_count")
        ),
        "composite_connector_side_effect_count": _counter(
            actor,
            "connector_side_effect_count",
        )
        + _counter(fractal, "connector_side_effect_count"),
        "composite_production_or_external_drs_used_count": (
            _counter(drs, "production_drs_used_count")
            + _counter(drs, "external_drs_used_count")
        ),
        "composite_manifest_mutation_count": (
            _counter(drs, "manifest_mutation_count")
            + _counter(avf, "manifest_mutation_count")
            + _counter(advisory, "manifest_mutation_count")
            + _counter(actor, "manifest_mutation_count")
            + _counter(fractal, "manifest_mutation_count")
        ),
        "composite_transition_matrix_mutation_count": (
            _counter(drs, "transition_matrix_mutation_count")
            + _counter(avf, "transition_matrix_mutation_count")
            + _counter(advisory, "transition_matrix_mutation_count")
            + _counter(actor, "transition_matrix_mutation_count")
            + _counter(fractal, "transition_matrix_mutation_count")
        ),
        "optional_live_llm_lane_default_enabled": False,
        "optional_live_llm_core_pass_dependency": False,
        "live_llm_authority_claimed_count": 0,
        "live_llm_final_output_created_count": 0,
        "full_e2e_claimed_count": 0,
        "production_readiness_claimed_count": 0,
        "root_final_authority_preserved_across_thread": _root_authority_preserved(
            results
        ),
    }
    zero_keys = (
        "composite_direct_reuse_allowed_count",
        "composite_action_permission_granted_count",
        "composite_final_output_created_by_non_root_count",
        "composite_authority_claimed_by_non_root_count",
        "composite_truth_claimed_by_non_root_count",
        "composite_poisoning_or_spam_authority_claimed_count",
        "composite_high_score_or_advisory_forced_accept_count",
        "composite_silent_or_hidden_safety_failure_count",
        "composite_actor_escalation_or_raw_command_accept_count",
        "composite_root_boundary_bypass_count",
        "composite_parent_boundary_bypass_count",
        "composite_post_vv_bypass_count",
        "composite_gt_bypass_count",
        "composite_child_boundary_violation_count",
        "composite_network_used_count",
        "composite_gemini_used_count",
        "composite_connector_side_effect_count",
        "composite_production_or_external_drs_used_count",
        "composite_manifest_mutation_count",
        "composite_transition_matrix_mutation_count",
        "live_llm_authority_claimed_count",
        "live_llm_final_output_created_count",
        "full_e2e_claimed_count",
        "production_readiness_claimed_count",
    )
    counters["composite_required_counters_match"] = (
        all(counters[key] == 0 for key in zero_keys)
        and counters["optional_live_llm_lane_default_enabled"] is False
        and counters["optional_live_llm_core_pass_dependency"] is False
        and counters["root_final_authority_preserved_across_thread"] is True
    )
    return counters


def run_composite_smoke() -> dict[str, Any]:
    results = collect_layer_results()
    missing_required_counter_keys = _missing_required_counter_keys(results)
    required_counter_keys_present = not missing_required_counter_keys
    counters = _aggregate_counters(results)
    composite_layers_total = len(results)
    composite_layers_passed = sum(
        1 for result in results.values() if result["final_status"] == "PASS"
    )
    scenario_totals = {
        "drs_scenarios_total": results["drs"]["scenarios_total"],
        "avf_scenarios_total": results["avf"]["scenarios_total"],
        "advisory_scenarios_total": results["advisory"]["scenarios_total"],
        "bounded_actor_scenarios_total": results["bounded_actor"]["scenarios_total"],
        "fractal_cell_scenarios_total": results["fractal_cell"]["scenarios_total"],
    }
    composite_scenarios_total = sum(scenario_totals.values())
    required_scenarios_present = _required_scenarios_present(results)
    scenario_totals_match = (
        scenario_totals["drs_scenarios_total"] == EXPECTED_TOTALS["drs"]
        and scenario_totals["avf_scenarios_total"] == EXPECTED_TOTALS["avf"]
        and scenario_totals["advisory_scenarios_total"]
        == EXPECTED_TOTALS["advisory"]
        and scenario_totals["bounded_actor_scenarios_total"]
        == EXPECTED_TOTALS["bounded_actor"]
        and scenario_totals["fractal_cell_scenarios_total"]
        == EXPECTED_TOTALS["fractal_cell"]
    )
    pass_conditions = {
        "layer_statuses_pass": composite_layers_passed == composite_layers_total,
        "scenario_totals_match": scenario_totals_match,
        "composite_scenarios_total_is_51": composite_scenarios_total == 51,
        "required_scenarios_present": required_scenarios_present,
        "required_counter_keys_present": required_counter_keys_present,
        "aggregate_counters_match": counters["composite_required_counters_match"],
    }
    return {
        "title": TITLE,
        "layers": results,
        "layer_names": LAYER_NAMES,
        **scenario_totals,
        "composite_layers_total": composite_layers_total,
        "composite_layers_passed": composite_layers_passed,
        "composite_scenarios_total": composite_scenarios_total,
        "composite_required_scenarios_present": required_scenarios_present,
        "composite_required_counter_keys_present": required_counter_keys_present,
        "missing_required_counter_keys": missing_required_counter_keys,
        "counters": counters,
        "pass_conditions": pass_conditions,
        "final_status": "PASS" if all(pass_conditions.values()) else "FAIL",
    }


def _scenario_lines(label: str, scenario_ids: tuple[str, ...]) -> list[str]:
    return [label, *[f"- {scenario_id}" for scenario_id in scenario_ids]]


def render_report(result: dict[str, Any] | None = None) -> str:
    result = result or run_composite_smoke()
    counters = result["counters"]
    lines = [
        TITLE,
        "",
        "Invoked layers:",
        *[f"- {name}" for name in result["layer_names"]],
        "",
        "Per-layer status:",
        f"drs_final_status: {result['layers']['drs']['final_status']}",
        f"avf_final_status: {result['layers']['avf']['final_status']}",
        f"advisory_final_status: {result['layers']['advisory']['final_status']}",
        f"bounded_actor_final_status: {result['layers']['bounded_actor']['final_status']}",
        f"fractal_cell_final_status: {result['layers']['fractal_cell']['final_status']}",
        "",
        "Scenario totals:",
        f"drs_scenarios_total: {result['drs_scenarios_total']}",
        f"avf_scenarios_total: {result['avf_scenarios_total']}",
        f"advisory_scenarios_total: {result['advisory_scenarios_total']}",
        f"bounded_actor_scenarios_total: {result['bounded_actor_scenarios_total']}",
        f"fractal_cell_scenarios_total: {result['fractal_cell_scenarios_total']}",
        f"composite_layers_total: {result['composite_layers_total']}",
        f"composite_layers_passed: {result['composite_layers_passed']}",
        f"composite_scenarios_total: {result['composite_scenarios_total']}",
        f"composite_required_scenarios_present: {result['composite_required_scenarios_present']}",
        f"composite_required_counter_keys_present: {result['composite_required_counter_keys_present']}",
        f"missing_required_counter_keys: {result['missing_required_counter_keys']}",
        "",
        "Scenario coverage:",
        *_scenario_lines("DRS scenarios:", DRS_SCENARIOS),
        *_scenario_lines("AVF scenarios:", AVF_SCENARIOS),
        *_scenario_lines("Advisory scenarios:", ADVISORY_SCENARIOS),
        *_scenario_lines("Bounded actor scenarios:", ACTOR_SCENARIOS),
        *_scenario_lines("Fractal Cell scenarios:", FRACTAL_SCENARIOS),
        "",
        "Aggregate counters:",
        f"composite_required_counters_match: {counters['composite_required_counters_match']}",
        f"composite_direct_reuse_allowed_count: {counters['composite_direct_reuse_allowed_count']}",
        f"composite_action_permission_granted_count: {counters['composite_action_permission_granted_count']}",
        f"composite_final_output_created_by_non_root_count: {counters['composite_final_output_created_by_non_root_count']}",
        f"composite_authority_claimed_by_non_root_count: {counters['composite_authority_claimed_by_non_root_count']}",
        f"composite_truth_claimed_by_non_root_count: {counters['composite_truth_claimed_by_non_root_count']}",
        f"composite_poisoning_or_spam_authority_claimed_count: {counters['composite_poisoning_or_spam_authority_claimed_count']}",
        f"composite_high_score_or_advisory_forced_accept_count: {counters['composite_high_score_or_advisory_forced_accept_count']}",
        f"composite_silent_or_hidden_safety_failure_count: {counters['composite_silent_or_hidden_safety_failure_count']}",
        f"composite_actor_escalation_or_raw_command_accept_count: {counters['composite_actor_escalation_or_raw_command_accept_count']}",
        f"composite_root_boundary_bypass_count: {counters['composite_root_boundary_bypass_count']}",
        f"composite_parent_boundary_bypass_count: {counters['composite_parent_boundary_bypass_count']}",
        f"composite_post_vv_bypass_count: {counters['composite_post_vv_bypass_count']}",
        f"composite_gt_bypass_count: {counters['composite_gt_bypass_count']}",
        f"composite_child_boundary_violation_count: {counters['composite_child_boundary_violation_count']}",
        f"composite_network_used_count: {counters['composite_network_used_count']}",
        f"composite_gemini_used_count: {counters['composite_gemini_used_count']}",
        f"composite_connector_side_effect_count: {counters['composite_connector_side_effect_count']}",
        f"composite_production_or_external_drs_used_count: {counters['composite_production_or_external_drs_used_count']}",
        f"composite_manifest_mutation_count: {counters['composite_manifest_mutation_count']}",
        f"composite_transition_matrix_mutation_count: {counters['composite_transition_matrix_mutation_count']}",
        f"optional_live_llm_lane_default_enabled: {counters['optional_live_llm_lane_default_enabled']}",
        f"optional_live_llm_core_pass_dependency: {counters['optional_live_llm_core_pass_dependency']}",
        f"live_llm_authority_claimed_count: {counters['live_llm_authority_claimed_count']}",
        f"live_llm_final_output_created_count: {counters['live_llm_final_output_created_count']}",
        f"full_e2e_claimed_count: {counters['full_e2e_claimed_count']}",
        f"production_readiness_claimed_count: {counters['production_readiness_claimed_count']}",
        f"root_final_authority_preserved_across_thread: {counters['root_final_authority_preserved_across_thread']}",
        "",
        "Authority boundary summary:",
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
        "",
        "Optional live LLM lane:",
        "optional_live_llm_lane_default_enabled: False",
        "optional_live_llm_core_pass_dependency: False",
        "",
        "Limitations:",
        "This composite smoke is deterministic and machine-checking only.",
        "It does not implement production E2E, production Fractal Cell runtime, production distributed runtime, production DRS, production AVF, production GT/LGT, production LGT, external/global DRS, autonomous action, connector side effects, public WOW, whitepaper/public auditor packet, manifest mutation, transition matrix mutation, direct reuse permission, action permission, or FinalOutput authority.",
        "Default run does not use network/Gemini/real model calls.",
        "Real Semantic Runtime MVP is not complete.",
        "",
        f"FINAL STATUS: {result['final_status']}",
    ]
    return "\n".join(lines)


def main() -> int:
    result = run_composite_smoke()
    print(render_report(result))
    return 0 if result["final_status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
