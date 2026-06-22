from __future__ import annotations

from typing import Any

from demo.run_real_local_drs_resolver_writeback_v01 import run_all_scenarios


TITLE = "HEDGEHOG OS — HUMAN REAL LOCAL DRS RESOLVER WALKTHROUGH v0.1"

REQUIRED_COUNTERS = {
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
    "manifest_mutation_count": 0,
    "transition_matrix_mutation_count": 0,
    "production_drs_used_count": 0,
    "external_drs_used_count": 0,
    "network_used_count": 0,
    "gemini_used_count": 0,
    "root_final_authority_preserved_count": 8,
}

SAFETY_BOUNDARIES = (
    "DRS record is not truth",
    "DRS hit is not authority",
    "DRS reuse candidate is not action permission",
    "DRS freshness is advisory, not final authority",
    "stale DRS record cannot silently reuse",
    "quarantined/deadend proximity forces review",
    "conflicting provenance blocks direct ready/reuse",
    "Root remains final authority",
    "resolver cannot mutate manifest",
    "resolver cannot mutate transition matrix",
    "resolver cannot call network/Gemini/connectors",
    "writeback cannot create production persistence claims",
    "local file-backed DRS is still not production DRS",
)


def _counters_match(result: dict[str, Any]) -> bool:
    counters = result["counters"]
    observed = {
        "scenarios_total": result["scenarios_total"],
        "scenarios_passed": result["scenarios_passed"],
        **{key: counters.get(key) for key in REQUIRED_COUNTERS if key in counters},
    }
    return all(observed.get(key) == expected for key, expected in REQUIRED_COUNTERS.items())


def _scenario_names(result: dict[str, Any]) -> set[str]:
    return {scenario["scenario_id"] for scenario in result["scenarios"]}


def _required_scenarios_present(result: dict[str, Any]) -> bool:
    expected = {
        "write_then_resolve_semantic_record_candidate_only",
        "stale_record_forces_root_review",
        "quarantine_proximity_blocks_direct_reuse",
        "changed_worldstate_blocks_old_reuse",
        "conflicting_provenance_blocks_reuse",
        "duplicate_poisoning_pressure_does_not_create_authority",
        "root_review_required_before_reuse_affects_final_output",
        "writeback_records_root_final_without_action_side_effects",
    }
    return expected <= _scenario_names(result)


def _counter_lines(result: dict[str, Any]) -> list[str]:
    counters = result["counters"]
    lines = [
        f"underlying_runtime_status: {result['final_status']}",
        f"walkthrough_required_counters_match: {_counters_match(result)}",
        f"scenarios_total: {result['scenarios_total']}",
        f"scenarios_passed: {result['scenarios_passed']}",
    ]
    for key in (
        "records_written_count",
        "resolve_queries_count",
        "candidates_returned_count",
        "direct_reuse_allowed_count",
        "root_review_required_count",
        "stale_record_reuse_blocked_count",
        "quarantine_reuse_blocked_count",
        "changed_worldstate_reuse_blocked_count",
        "conflicting_provenance_blocked_count",
        "duplicate_poisoning_records_seen_count",
        "poisoning_pressure_authority_claimed_count",
        "action_permission_granted_count",
        "manifest_mutation_count",
        "transition_matrix_mutation_count",
        "production_drs_used_count",
        "external_drs_used_count",
        "network_used_count",
        "gemini_used_count",
        "root_final_authority_preserved_count",
    ):
        lines.append(f"{key}: {counters[key]}")
    return lines


def build_walkthrough() -> str:
    result = run_all_scenarios()
    counters = result["counters"]
    lines = [
        TITLE,
        "",
        "WHAT THIS WALKTHROUGH IS",
        "This is a human-readable walkthrough over the already audited Real Local DRS Resolver / Writeback v0.1 runtime layer.",
        "It creates no new runtime capability, no new proof layer, no production DRS, no external/global DRS, no connector, no network, no Gemini, and no autonomous action.",
        "It explains observed behavior from the committed runtime layer.",
        "",
        "WHY THIS LAYER MATTERS",
        "This is the first runtime-facing layer under Real Semantic Runtime MVP.",
        "Before this, DRS behavior was mostly proof/demo memory behavior.",
        "Now a bounded local primitive exists for semantic write, deterministic resolve, and Root-reviewed reuse.",
        "This is still not complete Real Semantic Runtime MVP.",
        "",
        "CORE PIPELINE",
        "write meaning",
        "→ resolve meaning",
        "→ candidate only",
        "→ Root review required",
        "→ optional local writeback from RootFinal",
        "→ no action side effects",
        "Write records preserve meaning locally. Resolve returns candidates. Root review is required before any reuse affects final output. Local writeback records RootFinal-derived outcomes without action side effects.",
        "",
        "ACT 1 — WRITE MEANING",
        "A semantic DRS record is written locally using the existing DRSRecord shape.",
        "The record preserves domain, content, TimeEnvelope, provenance, trace_refs, and source_refs.",
        "Scenario: write_then_resolve_semantic_record_candidate_only.",
        "DRS record is not truth.",
        "",
        "ACT 2 — RESOLVE MEANING",
        "The resolver finds deterministic candidates by domain, content keys, controlled tokens, source_refs, trace_refs, provenance, status, and TimeEnvelope.",
        "It returns candidates only.",
        "DRS hit is not authority.",
        "",
        "ACT 3 — ROOT REVIEW BEFORE REUSE",
        "Even a good candidate cannot affect final output before Root review.",
        "Direct reuse remains blocked in v0.1.",
        "Scenario: root_review_required_before_reuse_affects_final_output.",
        f"direct_reuse_allowed_count: {counters['direct_reuse_allowed_count']}",
        "DRS reuse candidate is not action permission.",
        "",
        "ACT 4 — STALE / TTL PRESSURE",
        "A stale record can remain visible, but it forces Root review and cannot silently reuse.",
        "Scenario: stale_record_forces_root_review.",
        "",
        "ACT 5 — QUARANTINE / DEADEND PRESSURE",
        "Quarantine/deadend proximity blocks direct reuse and forces review.",
        "Scenario: quarantine_proximity_blocks_direct_reuse.",
        "",
        "ACT 6 — WORLDSTATE CHANGE",
        "Old compatible memory is blocked when current WorldState changes.",
        "Scenario: changed_worldstate_blocks_old_reuse.",
        "",
        "ACT 7 — CONFLICTING PROVENANCE",
        "Conflicting provenance blocks reuse.",
        "Provenance informs; it does not decide.",
        "Scenario: conflicting_provenance_blocks_reuse.",
        "",
        "ACT 8 — POISONING PRESSURE",
        "Duplicate/spam records and repeated external pointer pressure can create review pressure, but cannot create authority.",
        "Scenario: duplicate_poisoning_pressure_does_not_create_authority.",
        "",
        "ACT 9 — ROOTFINAL WRITEBACK",
        "A RootFinal-derived artifact can be written back locally without connector/action side effects.",
        "Raw ValidationPacket / EvidenceCandidate / ResultProposal / ConnectorObservation shapes are rejected even if they claim root_reviewed=true and created_by=root_orchestrator.",
        "Scenario: writeback_records_root_final_without_action_side_effects.",
        "ValidationPacket-like",
        "EvidenceCandidate-like",
        "ResultProposal-like",
        "ConnectorObservation-like",
        "",
        "SAFETY BOUNDARIES",
    ]
    lines.extend(f"- {boundary}" for boundary in SAFETY_BOUNDARIES)
    lines.extend(
        [
            "",
            "COUNTERS",
            *_counter_lines(result),
            "",
            "VALIDATION SUMMARY",
            "runtime audit commit: 6bb2422",
            "runtime commit: 2a18df5",
            "full pytest: 1754 passed, 60 warnings in 934.65s",
            "focused tests: 35 passed, 2 warnings",
            "runner: FINAL STATUS: PASS",
            "",
            "LIMITATIONS",
            "This walkthrough is explanatory only.",
            "It does not implement production DRS, external/global DRS, network/Gemini behavior, autonomous actions, connector side effects, public WOW, whitepaper/public auditor packet, Marennya/UP, self-modifying manifest, transition matrix mutation, separate DRS Poisoning Resistance v0.1, or Economic Adversary v0.1.",
            "Real Semantic Runtime MVP is not complete.",
            "",
            "FINAL HUMAN SUMMARY",
            "Hedgehog OS can now locally write semantic memory, resolve candidate memory, and record RootFinal-derived outcomes.",
            "But memory remains bounded: it can inform review, not decide reality.",
            "DRS hits do not become truth, reuse candidates do not become permission, and writeback does not become action.",
            "Root remains final authority.",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    result = run_all_scenarios()
    counters_ok = _counters_match(result)
    scenarios_ok = _required_scenarios_present(result)
    print(build_walkthrough())
    return 0 if result["final_status"] == "PASS" and counters_ok and scenarios_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
