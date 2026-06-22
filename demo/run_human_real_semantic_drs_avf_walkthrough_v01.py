from __future__ import annotations

from typing import Any

from demo.run_candidate_vector_generator_avf_scoring_v01 import (
    run_all_scenarios as run_avf_scenarios,
)
from demo.run_real_local_drs_resolver_writeback_v01 import (
    run_all_scenarios as run_drs_scenarios,
)


TITLE = "HEDGEHOG OS — HUMAN REAL SEMANTIC DRS → AVF WALKTHROUGH v0.1"

DRS_REQUIRED_COUNTERS = {
    "scenarios_total": 8,
    "scenarios_passed": 8,
    "records_written_count": 9,
    "resolve_queries_count": 7,
    "candidates_returned_count": 8,
    "direct_reuse_allowed_count": 0,
    "root_review_required_count": 8,
    "stale_record_reuse_blocked_count": 1,
    "quarantine_reuse_blocked_count": 1,
    "changed_worldstate_reuse_blocked_count": 1,
    "conflicting_provenance_blocked_count": 1,
    "duplicate_poisoning_records_seen_count": 2,
    "poisoning_pressure_authority_claimed_count": 0,
    "action_permission_granted_count": 0,
    "production_drs_used_count": 0,
    "external_drs_used_count": 0,
    "network_used_count": 0,
    "gemini_used_count": 0,
    "root_final_authority_preserved_count": 8,
}

AVF_REQUIRED_COUNTERS = {
    "scenarios_total": 9,
    "scenarios_passed": 9,
    "direct_reuse_allowed_count": 0,
    "action_permission_granted_count": 0,
    "avf_authority_claimed_count": 0,
    "vector_truth_claimed_count": 0,
    "schema_validity_truth_claimed_count": 0,
    "duplicate_spam_authority_claimed_count": 0,
    "high_score_direct_reuse_granted_count": 0,
    "network_used_count": 0,
    "gemini_used_count": 0,
    "root_final_authority_preserved_count": 9,
}

DRS_SCENARIOS = (
    "write_then_resolve_semantic_record_candidate_only",
    "stale_record_forces_root_review",
    "quarantine_proximity_blocks_direct_reuse",
    "changed_worldstate_blocks_old_reuse",
    "conflicting_provenance_blocks_reuse",
    "duplicate_poisoning_pressure_does_not_create_authority",
    "root_review_required_before_reuse_affects_final_output",
    "writeback_records_root_final_without_action_side_effects",
)

AVF_SCENARIOS = (
    "drs_resolved_candidates_generate_candidate_vectors",
    "exact_domain_and_claim_match_scores_higher_but_not_authority",
    "stale_candidate_gets_review_required_penalty",
    "quarantine_deadend_candidate_blocked_from_top_reuse",
    "conflicting_provenance_penalizes_or_blocks_candidate",
    "duplicate_spam_candidates_do_not_win_by_volume",
    "high_score_candidate_still_requires_gt_lgt_root_review",
    "schema_valid_vector_is_not_semantic_truth",
    "root_final_authority_preserved_across_avf_scoring",
)

SECTION_HEADINGS = (
    "WHAT THIS WALKTHROUGH IS",
    "WHY THIS IS THE FIRST REAL SEMANTIC RUNTIME THREAD",
    "THE PIPELINE",
    "ACT 1 — DRS WRITES MEANING",
    "ACT 2 — DRS RESOLVES MEMORY CANDIDATES",
    "ACT 3 — SAFETY PRESSURE IN DRS",
    "ACT 4 — ROOTFINAL WRITEBACK IS LOCAL MEMORY, NOT ACTION",
    "ACT 5 — CANDIDATE VECTOR GENERATOR BUILDS BOUNDED VECTORS",
    "ACT 6 — AVF SCORES AND RANKS, BUT DOES NOT DECIDE",
    "ACT 7 — AVF SAFETY PRESSURE",
    "ACT 8 — REVIEW BOUNDARY",
    "COMBINED COUNTERS",
    "VALIDATION SUMMARY",
    "LIMITATIONS",
    "FINAL HUMAN SUMMARY",
)


def _scenario_names(result: dict[str, Any]) -> set[str]:
    return {scenario["scenario_id"] for scenario in result["scenarios"]}


def _required_counters_match(
    drs_result: dict[str, Any],
    avf_result: dict[str, Any],
) -> bool:
    drs_observed = {
        "scenarios_total": drs_result["scenarios_total"],
        "scenarios_passed": drs_result["scenarios_passed"],
        **drs_result["counters"],
    }
    avf_observed = {
        "scenarios_total": avf_result["scenarios_total"],
        "scenarios_passed": avf_result["scenarios_passed"],
        **avf_result["counters"],
    }
    drs_ok = all(
        drs_observed.get(key) == expected
        for key, expected in DRS_REQUIRED_COUNTERS.items()
    )
    avf_ok = all(
        avf_observed.get(key) == expected
        for key, expected in AVF_REQUIRED_COUNTERS.items()
    )
    return drs_ok and avf_ok


def _required_scenarios_present(
    drs_result: dict[str, Any],
    avf_result: dict[str, Any],
) -> bool:
    return set(DRS_SCENARIOS) <= _scenario_names(drs_result) and set(AVF_SCENARIOS) <= (
        _scenario_names(avf_result)
    )


def _combined_counter_lines(
    drs_result: dict[str, Any],
    avf_result: dict[str, Any],
) -> list[str]:
    drs = drs_result["counters"]
    avf = avf_result["counters"]
    counters_match = _required_counters_match(drs_result, avf_result)
    combined_direct_reuse = (
        drs["direct_reuse_allowed_count"] + avf["direct_reuse_allowed_count"]
    )
    combined_action_permission = (
        drs["action_permission_granted_count"]
        + avf["action_permission_granted_count"]
    )
    combined_network = drs["network_used_count"] + avf["network_used_count"]
    combined_gemini = drs["gemini_used_count"] + avf["gemini_used_count"]

    return [
        "DRS Resolver counters:",
        f"drs_underlying_runtime_status: {drs_result['final_status']}",
        f"drs_scenarios_total: {drs_result['scenarios_total']}",
        f"drs_scenarios_passed: {drs_result['scenarios_passed']}",
        f"records_written_count: {drs['records_written_count']}",
        f"resolve_queries_count: {drs['resolve_queries_count']}",
        f"candidates_returned_count: {drs['candidates_returned_count']}",
        f"drs_direct_reuse_allowed_count: {drs['direct_reuse_allowed_count']}",
        f"root_review_required_count: {drs['root_review_required_count']}",
        f"stale_record_reuse_blocked_count: {drs['stale_record_reuse_blocked_count']}",
        f"quarantine_reuse_blocked_count: {drs['quarantine_reuse_blocked_count']}",
        f"changed_worldstate_reuse_blocked_count: {drs['changed_worldstate_reuse_blocked_count']}",
        f"conflicting_provenance_blocked_count: {drs['conflicting_provenance_blocked_count']}",
        f"duplicate_poisoning_records_seen_count: {drs['duplicate_poisoning_records_seen_count']}",
        f"poisoning_pressure_authority_claimed_count: {drs['poisoning_pressure_authority_claimed_count']}",
        f"drs_action_permission_granted_count: {drs['action_permission_granted_count']}",
        f"drs_production_drs_used_count: {drs['production_drs_used_count']}",
        f"drs_external_drs_used_count: {drs['external_drs_used_count']}",
        f"drs_network_used_count: {drs['network_used_count']}",
        f"drs_gemini_used_count: {drs['gemini_used_count']}",
        f"drs_root_final_authority_preserved_count: {drs['root_final_authority_preserved_count']}",
        "",
        "AVF counters:",
        f"avf_underlying_runtime_status: {avf_result['final_status']}",
        f"avf_scenarios_total: {avf_result['scenarios_total']}",
        f"avf_scenarios_passed: {avf_result['scenarios_passed']}",
        f"drs_candidates_input_count: {avf['drs_candidates_input_count']}",
        f"candidate_vectors_generated_count: {avf['candidate_vectors_generated_count']}",
        f"avf_scores_computed_count: {avf['avf_scores_computed_count']}",
        f"ranked_candidates_count: {avf['ranked_candidates_count']}",
        f"top_ranked_candidates_count: {avf['top_ranked_candidates_count']}",
        f"avf_direct_reuse_allowed_count: {avf['direct_reuse_allowed_count']}",
        f"avf_action_permission_granted_count: {avf['action_permission_granted_count']}",
        f"avf_authority_claimed_count: {avf['avf_authority_claimed_count']}",
        f"vector_truth_claimed_count: {avf['vector_truth_claimed_count']}",
        f"schema_validity_truth_claimed_count: {avf['schema_validity_truth_claimed_count']}",
        f"duplicate_spam_authority_claimed_count: {avf['duplicate_spam_authority_claimed_count']}",
        f"high_score_direct_reuse_granted_count: {avf['high_score_direct_reuse_granted_count']}",
        f"avf_network_used_count: {avf['network_used_count']}",
        f"avf_gemini_used_count: {avf['gemini_used_count']}",
        f"avf_root_final_authority_preserved_count: {avf['root_final_authority_preserved_count']}",
        "",
        "Combined:",
        f"walkthrough_required_counters_match: {counters_match}",
        f"combined_direct_reuse_allowed_count: {combined_direct_reuse}",
        f"combined_action_permission_granted_count: {combined_action_permission}",
        f"combined_network_used_count: {combined_network}",
        f"combined_gemini_used_count: {combined_gemini}",
    ]


def build_walkthrough() -> str:
    drs_result = run_drs_scenarios()
    avf_result = run_avf_scenarios()
    drs = drs_result["counters"]
    avf = avf_result["counters"]

    lines = [
        TITLE,
        "",
        "WHAT THIS WALKTHROUGH IS",
        "This walkthrough explains already audited runtime behavior across DRS Resolver and CandidateVectorGenerator/AVF.",
        "It creates no new runtime capability, no new DRS behavior, no new AVF behavior, no GT/LGT implementation, no Root behavior, no production DRS, no public WOW, and no whitepaper.",
        "It is a human-readable story over committed runtime proofs.",
        "",
        "WHY THIS IS THE FIRST REAL SEMANTIC RUNTIME THREAD",
        "Before these layers, most behavior was proof/demo hardening.",
        "Now Hedgehog OS has a bounded local path: semantic memory can be written, semantic memory can be resolved, resolved candidates can become candidate vectors, and candidate vectors can receive deterministic AVF scores.",
        "All outputs remain candidates for review.",
        "Real Semantic Runtime MVP is not complete.",
        "",
        "THE PIPELINE",
        "write meaning",
        "→ resolve meaning",
        "→ candidate only",
        "→ generate candidate vector",
        "→ generate bounded candidate vectors",
        "→ deterministic AVF score",
        "→ ranked review report",
        "→ GT/LGT review required",
        "→ Root remains final authority",
        "Meaning is written locally, resolved deterministically, vectorized into bounded candidate artifacts, scored by AVF, and reported for review.",
        "",
        "ACT 1 — DRS WRITES MEANING",
        "Real Local DRS Resolver writes a local semantic DRS record using the existing DRSRecord shape.",
        "It preserves domain/content/time/provenance/trace/source context.",
        "write_then_resolve_semantic_record_candidate_only",
        "DRS record is not truth.",
        f"records_written_count: {drs['records_written_count']}",
        "",
        "ACT 2 — DRS RESOLVES MEMORY CANDIDATES",
        "Resolver finds deterministic local candidates.",
        "A DRS hit is not authority.",
        "Candidates are returned for review, not direct reuse.",
        f"candidates_returned_count: {drs['candidates_returned_count']}",
        f"direct_reuse_allowed_count: {drs['direct_reuse_allowed_count']}",
        "",
        "ACT 3 — SAFETY PRESSURE IN DRS",
        "Stale records, quarantine/deadend proximity, changed worldstate, conflicting provenance, and duplicate poisoning pressure block or force review.",
        "stale_record_forces_root_review",
        "quarantine_proximity_blocks_direct_reuse",
        "changed_worldstate_blocks_old_reuse",
        "conflicting_provenance_blocks_reuse",
        "duplicate_poisoning_pressure_does_not_create_authority",
        f"root_review_required_count: {drs['root_review_required_count']}",
        f"stale_record_reuse_blocked_count: {drs['stale_record_reuse_blocked_count']}",
        f"quarantine_reuse_blocked_count: {drs['quarantine_reuse_blocked_count']}",
        f"changed_worldstate_reuse_blocked_count: {drs['changed_worldstate_reuse_blocked_count']}",
        f"conflicting_provenance_blocked_count: {drs['conflicting_provenance_blocked_count']}",
        f"duplicate_poisoning_records_seen_count: {drs['duplicate_poisoning_records_seen_count']}",
        "",
        "ACT 4 — ROOTFINAL WRITEBACK IS LOCAL MEMORY, NOT ACTION",
        "RootFinal-derived writeback can record a local DRS memory outcome without connector/action side effects.",
        "Raw ValidationPacket-like, EvidenceCandidate-like, ResultProposal-like, and ConnectorObservation-like objects cannot become writeback authority even with Root-looking claims.",
        "writeback_records_root_final_without_action_side_effects",
        "ValidationPacket-like",
        "EvidenceCandidate-like",
        "ResultProposal-like",
        "ConnectorObservation-like",
        "",
        "ACT 5 — CANDIDATE VECTOR GENERATOR BUILDS BOUNDED VECTORS",
        "Resolved DRS candidates become bounded candidate vectors.",
        "Candidate vector is not truth.",
        "Candidate vector is not authority.",
        "Schema-valid vector is not semantic truth.",
        "drs_resolved_candidates_generate_candidate_vectors",
        "schema_valid_vector_is_not_semantic_truth",
        f"candidate_vectors_generated_count: {avf['candidate_vectors_generated_count']}",
        f"vector_truth_claimed_count: {avf['vector_truth_claimed_count']}",
        f"schema_validity_truth_claimed_count: {avf['schema_validity_truth_claimed_count']}",
        "",
        "ACT 6 — AVF SCORES AND RANKS, BUT DOES NOT DECIDE",
        "AVF deterministic score can rank candidates and explain review priority.",
        "AVF score is not authority.",
        "Top-ranked candidate is not action permission.",
        "Top-ranked candidate is not direct reuse permission.",
        "exact_domain_and_claim_match_scores_higher_but_not_authority",
        "high_score_candidate_still_requires_gt_lgt_root_review",
        f"high_score_direct_reuse_granted_count: {avf['high_score_direct_reuse_granted_count']}",
        f"avf_authority_claimed_count: {avf['avf_authority_claimed_count']}",
        f"action_permission_granted_count: {avf['action_permission_granted_count']}",
        "",
        "ACT 7 — AVF SAFETY PRESSURE",
        "Stale candidate gets review penalty, quarantine/deadend blocks direct reuse, conflicting provenance penalizes/blocks, and duplicate spam does not win by volume.",
        "stale_candidate_gets_review_required_penalty",
        "quarantine_deadend_candidate_blocked_from_top_reuse",
        "conflicting_provenance_penalizes_or_blocks_candidate",
        "duplicate_spam_candidates_do_not_win_by_volume",
        f"duplicate_spam_authority_claimed_count: {avf['duplicate_spam_authority_claimed_count']}",
        "",
        "ACT 8 — REVIEW BOUNDARY",
        "Both DRS resolver and AVF scoring produce reviewable artifacts.",
        "GT/LGT remains advisory.",
        "Root remains final authority.",
        "Neither DRS nor AVF creates FinalOutput.",
        "root_review_required_before_reuse_affects_final_output",
        "root_final_authority_preserved_across_avf_scoring",
        f"root_final_authority_preserved_count from DRS: {drs['root_final_authority_preserved_count']}",
        f"root_final_authority_preserved_count from AVF: {avf['root_final_authority_preserved_count']}",
        "",
        "COMBINED COUNTERS",
        *_combined_counter_lines(drs_result, avf_result),
        "",
        "VALIDATION SUMMARY",
        "DRS runtime checkpoint: 4f513d1",
        "DRS runtime commit: 2a18df5",
        "DRS technical audit: 6bb2422",
        "CandidateVector/AVF runtime commit: 1506eea",
        "CandidateVector/AVF technical audit: cf3da99",
        "CandidateVector/AVF focused tests: 51 passed, 1 warning",
        "CandidateVector/AVF full pytest: 1772 passed, 60 warnings in 957.62s",
        "DRS full pytest at checkpoint: 1754 passed, 60 warnings in 934.65s",
        "",
        "LIMITATIONS",
        "This walkthrough is explanatory only.",
        "It does not implement production AVF, production DRS, external/global DRS, network/Gemini, embeddings, LLM semantic matching, GT/LGT implementation, Fractal Cell Runtime integration, autonomous action, connector side effects, public WOW, whitepaper/public auditor packet, Marennya/UP, manifest mutation, transition matrix mutation, direct reuse permission, action permission, or final output authority.",
        "Real Semantic Runtime MVP is not complete.",
        "",
        "FINAL HUMAN SUMMARY",
        "Hedgehog OS can now write meaning into local memory, resolve candidate memory, turn candidates into bounded vectors, and score/rank them for review.",
        "But memory and ranking remain bounded.",
        "DRS hits do not become truth, AVF scores do not become authority, top-ranked candidates do not become permission, and Root remains final authority.",
    ]
    return "\n".join(lines)


def main() -> int:
    drs_result = run_drs_scenarios()
    avf_result = run_avf_scenarios()
    counters_ok = _required_counters_match(drs_result, avf_result)
    scenarios_ok = _required_scenarios_present(drs_result, avf_result)
    statuses_ok = (
        drs_result["final_status"] == "PASS" and avf_result["final_status"] == "PASS"
    )
    print(build_walkthrough())
    return 0 if counters_ok and scenarios_ok and statuses_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
