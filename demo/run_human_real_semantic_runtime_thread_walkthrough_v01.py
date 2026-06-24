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


TITLE = "HEDGEHOG OS — HUMAN REAL SEMANTIC RUNTIME THREAD WALKTHROUGH v0.1"

SECTION_HEADINGS = (
    "WHAT THIS WALKTHROUGH IS",
    "MAXIMAL BUT NOT FULL E2E",
    "CORE THREAD TOPOLOGY",
    "ACT 1 — ROOT-SHAPED REQUEST ENTERS SEMANTIC MEMORY",
    "ACT 2 — DRS SAFETY PRESSURE STAYS ACTIVE",
    "ACT 3 — CANDIDATE VECTORS AND AVF RANKING",
    "ACT 4 — AVF CANDIDATE ADVISORY REVIEW",
    "ACT 5 — BOUNDED LLM/SLM ACTOR CONTRACTS",
    "ACT 6 — OPTIONAL LIVE LLM EVIDENCE LANE",
    "ACT 7 — FRACTAL CELL BOUNDED CHILD EXECUTION",
    "ACT 8 — POST V&V FALLBACK FAILS CLOSED",
    "ACT 9 — HISTORICAL CANONICAL SPINE EVIDENCE",
    "ACT 10 — SAFETY PACKS STILL MATTER",
    "ACT 11 — CLOSED HISTORICAL LAYER CATALOG",
    "ACT 12 — OPTIONAL LIVE LLM / GEMINI HISTORICAL EVIDENCE",
    "COMBINED COUNTERS",
    "VALIDATION SUMMARY",
    "LIMITATIONS",
    "FINAL HUMAN SUMMARY",
)

HISTORICAL_CANONICAL_SPINE = (
    "Architect from bounded AttractorPacket",
    "DAG Executor from valid PlanGraph",
    "Post V&V from ResultProposal",
    "GT from ValidationReport",
    "Root Final from GTDecision",
    "DRS writeback from Root Final",
)

SAFETY_PACKS = (
    "DRS lineage provenance pressure",
    "long-lived DRS TTL aging",
    "compromised upstream pack",
    "External Evidence Acceptance Gate",
    "read-only connector sandbox",
    "schema contract hardening",
    "artifact/evidence vocabulary",
    "target-boundary guards",
)

HISTORICAL_CLOSED_LAYER_CATALOG = (
    "Controlled Orchestrator matrix gate",
    "AVF attractor formation",
    "Architect from bounded AttractorPacket",
    "DAG Executor from valid PlanGraph",
    "Post V&V from ResultProposal",
    "GT from ValidationReport",
    "Root Final from GTDecision",
    "DRS writeback from Root Final",
    "Root-native canonical trace",
    "Root-native semantic reuse E2E trace",
    "ReuseScore advisory proof",
    "typed DRS lineage edges",
    "DRS layer taxonomy",
    "DRS lineage provenance pressure",
    "long-lived DRS TTL aging",
    "compromised upstream pack",
    "External DRS pointer protocol",
    "cross-domain DRS bridge",
    "Needle adversarial safety",
    "read-only enterprise connector sandbox",
    "External Evidence Acceptance Gate",
    "Bounded LLM Semantic Executor Node",
    "Enterprise Chaos Pack",
    "Compute Collapse Enterprise Bench",
    "Kernel Enforcement Transition Matrix",
    "Developer Facade Capability Manifest UX",
    "Production Boundary Design",
    "Enterprise Killer Demo v0.1",
    "Enterprise Document Killer Demo B v0.1",
    "Schema Contract Alignment Phase 1",
    "Schema Contract Alignment Phase 2",
    "Runtime JSON Schema Validation Hardening",
    "Outgoing VVReport Runtime Validation",
    "EvidenceItem kind Alignment",
    "NeedleRuntime audit evidence shape",
    "Artifact type runtime vocabulary map",
)

OPTIONAL_LIVE_LLM_EVIDENCE_PATHS = (
    "optional live Gemini Architect smoke",
    "optional live Gemini Orchestrator smoke",
    "ordered live Gemini Orchestrator Architect smoke",
    "live dual-Gemini full chain smoke",
)

COMPOSITE_HUMAN_SCENARIO_IDS = (
    "memory_candidate_to_advisory_to_child_cell_review_only",
    "stale_memory_cannot_become_actor_command",
    "compromised_upstream_cannot_poison_avf_advisory",
    "external_evidence_connector_readonly_no_action",
    "schema_valid_artifact_is_not_semantic_truth",
    "bounded_actor_live_llm_text_is_not_authority",
    "child_cell_resultproposal_returns_to_parent_post_vv_gt",
    "historical_spine_root_final_writeback_evidence_only",
    "enterprise_demo_b_is_showcase_not_runtime_authority",
    "target_boundary_guards_block_illegal_transitions",
)


def _counter(result: dict[str, Any], key: str) -> int:
    return int(result.get("counters", {}).get(key, 0))


def _scenario_names(result: dict[str, Any]) -> set[str]:
    return {scenario["scenario_id"] for scenario in result["scenarios"]}


def _all_required_scenarios_present(results: dict[str, dict[str, Any]]) -> bool:
    return (
        set(DRS_SCENARIOS) <= _scenario_names(results["drs"])
        and set(AVF_SCENARIOS) <= _scenario_names(results["avf"])
        and set(ADVISORY_SCENARIOS) <= _scenario_names(results["advisory"])
        and set(ACTOR_SCENARIOS) <= _scenario_names(results["actors"])
        and set(FRACTAL_SCENARIOS) <= _scenario_names(results["fractal"])
    )


def _combined_counters(results: dict[str, dict[str, Any]]) -> dict[str, Any]:
    drs = results["drs"]
    avf = results["avf"]
    advisory = results["advisory"]
    actors = results["actors"]
    fractal = results["fractal"]

    closed_layers = (drs, avf, advisory, actors, fractal)
    closed_layers_status_pass_count = sum(
        1 for result in closed_layers if result["final_status"] == "PASS"
    )
    combined_direct_reuse = (
        _counter(drs, "direct_reuse_allowed_count")
        + _counter(avf, "direct_reuse_allowed_count")
        + _counter(advisory, "direct_reuse_allowed_count")
    )
    combined_action_permission = (
        _counter(drs, "action_permission_granted_count")
        + _counter(avf, "action_permission_granted_count")
        + _counter(advisory, "action_permission_granted_count")
        + _counter(actors, "action_permission_granted_count")
        + _counter(fractal, "action_permission_granted_count")
    )
    combined_final_output_by_non_root = (
        _counter(advisory, "final_output_created_count")
        + _counter(actors, "final_output_created_count")
        + _counter(fractal, "final_output_created_count")
    )
    combined_non_root_authority = (
        _counter(avf, "avf_authority_claimed_count")
        + _counter(avf, "vector_truth_claimed_count")
        + _counter(advisory, "gt_authority_claimed_count")
        + _counter(advisory, "lgt_authority_claimed_count")
        + _counter(advisory, "advisory_truth_claimed_count")
        + _counter(actors, "actor_authority_claimed_count")
        + _counter(actors, "llm_truth_claimed_count")
        + _counter(actors, "slm_truth_claimed_count")
        + _counter(fractal, "child_authority_claimed_count")
        + _counter(fractal, "child_root_claimed_count")
    )
    combined_post_vv_bypass = _counter(actors, "post_vv_bypass_count") + _counter(
        fractal,
        "post_vv_bypass_count",
    )
    combined_gt_bypass = _counter(actors, "gt_bypass_count") + _counter(
        fractal,
        "gt_bypass_count",
    )
    combined_network = (
        _counter(drs, "network_used_count")
        + _counter(avf, "network_used_count")
        + _counter(advisory, "network_used_count")
        + _counter(actors, "network_used_count")
        + _counter(fractal, "network_used_count")
    )
    combined_gemini = (
        _counter(drs, "gemini_used_count")
        + _counter(avf, "gemini_used_count")
        + _counter(advisory, "gemini_used_count")
        + _counter(actors, "gemini_used_count")
        + _counter(fractal, "gemini_used_count")
    )
    root_preserved = (
        _counter(drs, "root_final_authority_preserved_count") == drs["scenarios_total"]
        and _counter(avf, "root_final_authority_preserved_count")
        == avf["scenarios_total"]
        and _counter(advisory, "root_final_authority_preserved_count")
        == advisory["scenarios_total"]
        and _counter(actors, "root_final_authority_preserved_count")
        == actors["scenarios_total"]
        and _counter(fractal, "root_final_authority_preserved_count")
        == fractal["scenarios_total"]
    )

    counters = {
        "closed_layers_invoked_count": len(closed_layers),
        "closed_layers_status_pass_count": closed_layers_status_pass_count,
        "combined_direct_reuse_allowed_count": combined_direct_reuse,
        "combined_action_permission_granted_count": combined_action_permission,
        "combined_final_output_created_by_non_root_count": combined_final_output_by_non_root,
        "combined_authority_claimed_by_non_root_count": combined_non_root_authority,
        "combined_parent_boundary_bypass_count": _counter(
            fractal,
            "parent_boundary_bypass_count",
        ),
        "combined_post_vv_bypass_count": combined_post_vv_bypass,
        "combined_gt_bypass_count": combined_gt_bypass,
        "combined_network_used_count": combined_network,
        "combined_gemini_used_count": combined_gemini,
        "optional_live_llm_lane_default_enabled": False,
        "optional_live_llm_core_pass_dependency": False,
        "root_final_authority_preserved_across_thread": root_preserved,
        "full_e2e_claimed_count": 0,
        "production_readiness_claimed_count": 0,
        "historical_closed_layers_listed_count": len(HISTORICAL_CLOSED_LAYER_CATALOG),
        "optional_live_llm_evidence_paths_listed_count": len(
            OPTIONAL_LIVE_LLM_EVIDENCE_PATHS
        ),
        "live_llm_authority_claimed_count": 0,
        "live_llm_final_output_created_count": 0,
    }
    counters["walkthrough_required_counters_match"] = (
        _all_required_scenarios_present(results)
        and closed_layers_status_pass_count == len(closed_layers)
        and counters["combined_direct_reuse_allowed_count"] == 0
        and counters["combined_action_permission_granted_count"] == 0
        and counters["combined_final_output_created_by_non_root_count"] == 0
        and counters["combined_authority_claimed_by_non_root_count"] == 0
        and counters["combined_parent_boundary_bypass_count"] == 0
        and counters["combined_post_vv_bypass_count"] == 0
        and counters["combined_gt_bypass_count"] == 0
        and counters["combined_network_used_count"] == 0
        and counters["combined_gemini_used_count"] == 0
        and counters["optional_live_llm_lane_default_enabled"] is False
        and counters["optional_live_llm_core_pass_dependency"] is False
        and counters["root_final_authority_preserved_across_thread"] is True
        and counters["full_e2e_claimed_count"] == 0
        and counters["production_readiness_claimed_count"] == 0
        and counters["historical_closed_layers_listed_count"]
        == len(HISTORICAL_CLOSED_LAYER_CATALOG)
        and counters["optional_live_llm_evidence_paths_listed_count"]
        == len(OPTIONAL_LIVE_LLM_EVIDENCE_PATHS)
        and counters["live_llm_authority_claimed_count"] == 0
        and counters["live_llm_final_output_created_count"] == 0
    )
    return counters


def collect_underlying_results() -> dict[str, dict[str, Any]]:
    return {
        "drs": run_drs_scenarios(),
        "avf": run_avf_scenarios(),
        "advisory": run_advisory_scenarios(),
        "actors": run_actor_scenarios(),
        "fractal": run_fractal_scenarios(),
    }


def _scenario_lines(title: str, scenarios: tuple[str, ...]) -> list[str]:
    return [title, *[f"- {scenario_id}" for scenario_id in scenarios]]


def build_walkthrough(results: dict[str, dict[str, Any]] | None = None) -> str:
    results = results or collect_underlying_results()
    combined = _combined_counters(results)
    drs = results["drs"]["counters"]
    avf = results["avf"]["counters"]
    advisory = results["advisory"]["counters"]
    actors = results["actors"]["counters"]
    fractal = results["fractal"]["counters"]

    lines = [
        TITLE,
        "",
        "WHAT THIS WALKTHROUGH IS",
        "This walkthrough stitches already audited / checkpointed runtime-facing layers into one human-readable semantic thread.",
        "It creates no new runtime capability, no new authority layer, no production E2E, no public WOW, no Root behavior, no action permission, and no FinalOutput authority.",
        "Real Semantic Runtime MVP is not complete.",
        "",
        "MAXIMAL BUT NOT FULL E2E",
        "This walkthrough shows the widest safe thread available today.",
        "It is a composite human walkthrough over closed layers and historical evidence.",
        "It is not a single production end-to-end business execution.",
        "It does not claim that one live object traverses every historical proof layer.",
        "",
        "CORE THREAD TOPOLOGY",
        "Root-shaped request",
        "→ semantic memory write/resolve",
        "→ DRS candidates",
        "→ candidate vectors",
        "→ AVF scoring/ranking",
        "→ candidate advisory review",
        "→ bounded LLM/SLM actor contracts",
        "→ bounded Fractal Cell child execution",
        "→ child ResultProposal / cell report",
        "→ parent Post V&V / GT route",
        "→ parent Root final review",
        "→ DRS writeback evidence",
        "Root remains final authority.",
        "",
        "ACT 1 — ROOT-SHAPED REQUEST ENTERS SEMANTIC MEMORY",
        "Real Local DRS Resolver / Writeback evidence shows semantic memory write/resolve under Root review.",
        "DRS record is not truth.",
        "DRS hit is not authority.",
        f"records_written_count: {drs['records_written_count']}",
        f"candidates_returned_count: {drs['candidates_returned_count']}",
        f"direct_reuse_allowed_count: {drs['direct_reuse_allowed_count']}",
        *_scenario_lines("DRS scenarios:", DRS_SCENARIOS),
        "",
        "ACT 2 — DRS SAFETY PRESSURE STAYS ACTIVE",
        "stale_record_forces_root_review",
        "quarantine_proximity_blocks_direct_reuse",
        "changed_worldstate_blocks_old_reuse",
        "conflicting_provenance_blocks_reuse",
        "duplicate_poisoning_pressure_does_not_create_authority",
        f"root_review_required_count: {drs['root_review_required_count']}",
        f"poisoning_pressure_authority_claimed_count: {drs['poisoning_pressure_authority_claimed_count']}",
        f"drs_action_permission_granted_count: {drs['action_permission_granted_count']}",
        "",
        "ACT 3 — CANDIDATE VECTORS AND AVF RANKING",
        "drs_resolved_candidates_generate_candidate_vectors",
        "exact_domain_and_claim_match_scores_higher_but_not_authority",
        "schema_valid_vector_is_not_semantic_truth",
        "Candidate vector is not truth.",
        "AVF score is not authority.",
        "Top-ranked candidate is not action permission.",
        f"candidate_vectors_generated_count: {avf['candidate_vectors_generated_count']}",
        f"avf_scores_computed_count: {avf['avf_scores_computed_count']}",
        f"avf_authority_claimed_count: {avf['avf_authority_claimed_count']}",
        f"vector_truth_claimed_count: {avf['vector_truth_claimed_count']}",
        f"high_score_direct_reuse_granted_count: {avf['high_score_direct_reuse_granted_count']}",
        *_scenario_lines("AVF scenarios:", AVF_SCENARIOS),
        "",
        "ACT 4 — AVF CANDIDATE ADVISORY REVIEW",
        "Human-facing name: AVF Candidate Advisory Evaluator.",
        "This layer does not relocate canonical terminal GTValidator.",
        "This layer is pre-Architect candidate-level advisory review.",
        "It may emit GT-style advisory signals.",
        "It does not command Architect.",
        "LGT is deferred/local placeholder only.",
        "Root remains final authority.",
        *_scenario_lines("Advisory scenarios:", ADVISORY_SCENARIOS),
        f"advisory_scenarios_total: {results['advisory']['scenarios_total']}",
        f"advisory_scenarios_passed: {results['advisory']['scenarios_passed']}",
        f"advisory_final_output_created_count: {advisory['final_output_created_count']}",
        f"gt_authority_claimed_count: {advisory['gt_authority_claimed_count']}",
        f"lgt_authority_claimed_count: {advisory['lgt_authority_claimed_count']}",
        "",
        "ACT 5 — BOUNDED LLM/SLM ACTOR CONTRACTS",
        "Actors may intake, route, propose, execute, verify, or return reports only within bounded role contracts.",
        "LLM/SLM actor output is not truth, not authority, not action permission, and not Root Final.",
        "Root/Orchestrator remains the route authority.",
        "Intake",
        "Orchestrator",
        "Architect",
        "Executor",
        "Verifier",
        "Root boundary",
        "actor output is not authority",
        "actor output is not FinalOutput",
        "actor output returns to Root/Orchestrator boundary",
        *_scenario_lines("Bounded actor scenarios:", ACTOR_SCENARIOS),
        f"actor_scenarios_total: {results['actors']['scenarios_total']}",
        f"actor_scenarios_passed: {results['actors']['scenarios_passed']}",
        f"actor_authority_claimed_count: {actors['actor_authority_claimed_count']}",
        f"actor_final_output_created_count: {actors['final_output_created_count']}",
        "",
        "ACT 6 — OPTIONAL LIVE LLM EVIDENCE LANE",
        "Real LLM/Gemini paths have existed as optional live smoke/evidence paths, but this deterministic walkthrough does not call network/Gemini by default.",
        "Optional live LLM output, if manually enabled in future, is evidence/demo text only and cannot affect PASS, authority, action permission, or FinalOutput.",
        f"optional_live_llm_lane_default_enabled: {combined['optional_live_llm_lane_default_enabled']}",
        f"optional_live_llm_core_pass_dependency: {combined['optional_live_llm_core_pass_dependency']}",
        f"default_network_used_count: {combined['combined_network_used_count']}",
        f"default_gemini_used_count: {combined['combined_gemini_used_count']}",
        "live LLM output is not authority",
        "live LLM output is not Root Final",
        "",
        "ACT 7 — FRACTAL CELL BOUNDED CHILD EXECUTION",
        "Fractal Cell is not Root.",
        "child ResultProposal is not FinalOutput.",
        "child cell output must return to parent/Root boundary.",
        "bounded actor contracts apply inside child cell.",
        "child_target_boundary_blocked",
        "recursive_child_cell_depth_is_bounded",
        "child_consensus_does_not_create_authority",
        *_scenario_lines("Fractal Cell scenarios:", FRACTAL_SCENARIOS),
        f"scenarios_total: {results['fractal']['scenarios_total']}",
        f"scenarios_passed: {results['fractal']['scenarios_passed']}",
        f"post_vv_fallback_used_count: {fractal['post_vv_fallback_used_count']}",
        f"final_output_created_count: {fractal['final_output_created_count']}",
        f"action_permission_granted_count: {fractal['action_permission_granted_count']}",
        f"child_root_claimed_count: {fractal['child_root_claimed_count']}",
        f"child_authority_claimed_count: {fractal['child_authority_claimed_count']}",
        f"parent_boundary_bypass_count: {fractal['parent_boundary_bypass_count']}",
        f"post_vv_bypass_count: {fractal['post_vv_bypass_count']}",
        f"gt_bypass_count: {fractal['gt_bypass_count']}",
        f"root_final_authority_preserved_count: {fractal['root_final_authority_preserved_count']}",
        "",
        "ACT 8 — POST V&V FALLBACK FAILS CLOSED",
        "Post V&V fallback fails closed as review-required / needs-revision.",
        "Fallback Post V&V is shape-compatible only.",
        "It is not accepted authority.",
        "post_vv_runtime_unavailable_review_required",
        "post_vv_fallback_not_authority",
        "child_output_requires_real_post_vv_or_root_review",
        "post_vv_fallback_used_review_required",
        "",
        "ACT 9 — HISTORICAL CANONICAL SPINE EVIDENCE",
        "These are closed historical proof/checkpoint layers, not proof that this walkthrough performs one full production E2E object traversal.",
        *HISTORICAL_CANONICAL_SPINE,
        "",
        "ACT 10 — SAFETY PACKS STILL MATTER",
        "These packs constrain interpretation and safety pressure; they are not action permission.",
        *SAFETY_PACKS,
        "",
        "ACT 11 — CLOSED HISTORICAL LAYER CATALOG",
        "This section is evidence-only unless a public runner is already invoked elsewhere.",
        "It does not imply one live object traverses every layer.",
        *HISTORICAL_CLOSED_LAYER_CATALOG,
        "",
        "ACT 12 — OPTIONAL LIVE LLM / GEMINI HISTORICAL EVIDENCE",
        "These are historical optional live evidence paths, not default PASS dependencies.",
        "This walkthrough does not call network/Gemini by default.",
        "Live LLM/Gemini output is not truth, not authority, not action permission, not Root Final, and not a PASS dependency.",
        *OPTIONAL_LIVE_LLM_EVIDENCE_PATHS,
        f"live_llm_authority_claimed_count: {combined['live_llm_authority_claimed_count']}",
        f"live_llm_final_output_created_count: {combined['live_llm_final_output_created_count']}",
        "",
        "COMPOSITE HUMAN SCENARIO IDS",
        *COMPOSITE_HUMAN_SCENARIO_IDS,
        "",
        "COMBINED COUNTERS",
        f"walkthrough_required_counters_match: {combined['walkthrough_required_counters_match']}",
        f"closed_layers_invoked_count: {combined['closed_layers_invoked_count']}",
        f"closed_layers_status_pass_count: {combined['closed_layers_status_pass_count']}",
        f"combined_direct_reuse_allowed_count: {combined['combined_direct_reuse_allowed_count']}",
        f"combined_action_permission_granted_count: {combined['combined_action_permission_granted_count']}",
        f"combined_final_output_created_by_non_root_count: {combined['combined_final_output_created_by_non_root_count']}",
        f"combined_authority_claimed_by_non_root_count: {combined['combined_authority_claimed_by_non_root_count']}",
        f"combined_parent_boundary_bypass_count: {combined['combined_parent_boundary_bypass_count']}",
        f"combined_post_vv_bypass_count: {combined['combined_post_vv_bypass_count']}",
        f"combined_gt_bypass_count: {combined['combined_gt_bypass_count']}",
        f"combined_network_used_count: {combined['combined_network_used_count']}",
        f"combined_gemini_used_count: {combined['combined_gemini_used_count']}",
        f"optional_live_llm_lane_default_enabled: {combined['optional_live_llm_lane_default_enabled']}",
        f"optional_live_llm_core_pass_dependency: {combined['optional_live_llm_core_pass_dependency']}",
        f"root_final_authority_preserved_across_thread: {combined['root_final_authority_preserved_across_thread']}",
        f"full_e2e_claimed_count: {combined['full_e2e_claimed_count']}",
        f"production_readiness_claimed_count: {combined['production_readiness_claimed_count']}",
        f"historical_closed_layers_listed_count: {combined['historical_closed_layers_listed_count']}",
        f"optional_live_llm_evidence_paths_listed_count: {combined['optional_live_llm_evidence_paths_listed_count']}",
        f"live_llm_authority_claimed_count: {combined['live_llm_authority_claimed_count']}",
        f"live_llm_final_output_created_count: {combined['live_llm_final_output_created_count']}",
        "",
        "VALIDATION SUMMARY",
        "- DRS runtime commit: 2a18df5",
        "- DRS technical audit: 6bb2422",
        "- DRS checkpoint: 4f513d1",
        "- CandidateVector/AVF runtime commit: 1506eea",
        "- CandidateVector/AVF technical audit: cf3da99",
        "- CandidateVector/AVF checkpoint: 762239c",
        "- AVF Candidate Advisory runtime commit: b0ce686",
        "- AVF Candidate Advisory technical audit: 7cbcb77",
        "- AVF Candidate Advisory human walkthrough: 5f7cfe7",
        "- AVF Candidate Advisory human audit: bc80aae",
        "- Bounded LLM/SLM Actors runtime commit: 6802d14",
        "- Bounded LLM/SLM Actors technical audit: dfd43b9",
        "- Bounded LLM/SLM Actors human walkthrough: df45900",
        "- Bounded LLM/SLM Actors human audit: 388749c",
        "- Bounded LLM/SLM Actors checkpoint: 09523bf",
        "- Bounded LLM/SLM Actors targeted tests: 92 passed, 50 warnings",
        "- Bounded LLM/SLM Actors full pytest: 1819 passed, 60 warnings",
        "- Fractal Cell runtime commit: 96755ba",
        "- Fractal Cell technical audit: 643d6cd",
        "- Fractal Cell human walkthrough: b6b53f8",
        "- Fractal Cell human audit: 1f1a196",
        "- Fractal Cell docs checkpoint: bc7ec63",
        "- Fractal Cell full pytest: 1845 passed, 60 warnings",
        "",
        "LIMITATIONS",
        "This walkthrough is explanatory/composite only.",
        "It does not implement production E2E, production Fractal Cell runtime, production distributed runtime, production DRS, production AVF, production GT/LGT, production LGT, external/global DRS, autonomous action, connector side effects, public WOW, whitepaper/public auditor packet, manifest mutation, transition matrix mutation, direct reuse permission, action permission, or FinalOutput authority.",
        "Default run does not use network/Gemini/real model calls.",
        "Real Semantic Runtime MVP is not complete.",
        "",
        "FINAL HUMAN SUMMARY",
        "Hedgehog OS can now show a broad semantic thread: memory can be written and resolved, candidates can be vectorized and ranked, advisory review can route candidates without authority, bounded actors define who may speak, and Fractal Cell can host bounded child execution that returns upward.",
        "But the thread remains bounded: memory is not truth, AVF is not authority, advisory is not Root, live LLM output is not authority, child cell is not Root, child output is not FinalOutput, and Root remains final authority.",
    ]
    return "\n".join(lines)


def main() -> int:
    results = collect_underlying_results()
    combined = _combined_counters(results)
    print(build_walkthrough(results))
    return 0 if combined["walkthrough_required_counters_match"] else 1


if __name__ == "__main__":
    sys.exit(main())
