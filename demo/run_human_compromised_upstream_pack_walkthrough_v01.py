from __future__ import annotations

from typing import Any

from demo.run_compromised_upstream_pack_v01 import run_all_scenarios


TITLE = "HEDGEHOG OS — HUMAN COMPROMISED UPSTREAM WALKTHROUGH v0.1"

CORE_RULE = (
    "compromised upstream source is not truth",
    "signed-looking source is not truth",
    "external pointer is not trust",
    "schema-valid upstream content is not semantic truth",
    "ValidationPacket is not Root acceptance",
    "EvidenceCandidate is candidate-only before Root",
    "AcceptedEvidence is bounded evidence, not future action permission",
    "ConflictCheck remains advisory",
    "GT remains advisory",
    "Root remains final authority",
)

REQUIRED_COUNTERS = {
    "scenarios_total": 6,
    "scenarios_passed": 6,
    "direct_ready_allowed_count": 0,
    "direct_reuse_allowed_count": 0,
    "action_permission_granted_count": 0,
    "source_truth_claimed_count": 0,
    "schema_validity_truth_claimed_count": 0,
    "signed_source_truth_claimed_count": 0,
    "pointer_trust_claimed_count": 0,
    "evidence_candidate_authority_claimed_count": 0,
    "validation_packet_authority_claimed_count": 0,
    "accepted_evidence_action_permission_claimed_count": 0,
    "conflictcheck_authority_count": 0,
    "gt_authority_count": 0,
    "root_final_authority_preserved_count": 6,
    "production_connector_used_count": 0,
    "production_drs_used_count": 0,
    "external_drs_used_count": 0,
    "network_used_count": 0,
    "gemini_used_count": 0,
    "negative_trace_implemented_count": 0,
    "auto_governance_implemented_count": 0,
    "manifest_hardening_implemented_count": 0,
    "transition_matrix_mutated_count": 0,
    "marennya_activated_count": 0,
    "up_activated_count": 0,
}


def _required_counters_match(report: dict[str, Any]) -> bool:
    counters = report["aggregate_counters"]
    return report["status"] == "PASS" and all(
        counters.get(key) == expected for key, expected in REQUIRED_COUNTERS.items()
    )


def _counter_lines(report: dict[str, Any]) -> list[str]:
    counters = report["aggregate_counters"]
    return [f"* {key}: {counters[key]}" for key in REQUIRED_COUNTERS]


def build_walkthrough() -> str:
    report = run_all_scenarios()
    counters = report["aggregate_counters"]
    counters_match = _required_counters_match(report)

    lines = [
        TITLE,
        "",
        "1. WHAT THIS WALKTHROUGH IS",
        "",
        "This is a human-readable walkthrough over the already audited Compromised Upstream Pack v0.1 proof.",
        "It does not create a new proof layer, runtime capability, connector, DRS authority, or production behavior.",
        "It imports the existing proof runner, checks the expected counters, and explains the result in plain language.",
        "Root remains final authority.",
        "",
        "2. CORE RULE",
        "",
        *CORE_RULE,
        "",
        "3. ACT 1 — COMPROMISED BANK SOURCE",
        "",
        "A bank-like upstream source can look important and claim payment/readiness.",
        "The system treats it as observation/candidate only.",
        "Result: blocked_or_review_required / needs_root_review.",
        "No ready, no action, no truth.",
        "Scenario: compromised_bank_source_cannot_create_truth",
        "Reason code: compromised_source_not_truth",
        "",
        "4. ACT 2 — STALE SIGNED-LOOKING LEGAL SOURCE",
        "",
        "A source can look signed/formal but be stale.",
        "Signed-looking is not truth.",
        "Result: stale_source_review_required / needs_root_review.",
        "Scenario: stale_legal_source_signed_looking_forces_review",
        "Reason code: stale_signed_source_requires_review",
        "",
        "5. ACT 3 — WAREHOUSE CONTRADICTION",
        "",
        "A warehouse source claims ready, but known stock/world-state says shortage/not_ready.",
        "ConflictCheck can warn/block route, but it is still advisory until Root.",
        "Result: not_ready.",
        "Scenario: warehouse_source_contradiction_blocks_ready",
        "Reason code: conflicting_warehouse_provenance_blocks_ready",
        "",
        "6. ACT 4 — EXTERNAL POINTER TRUST LAUNDERING",
        "",
        "A repeated external pointer tries to become trust or external/global DRS.",
        "Pointer is not trust.",
        "Result: blocked.",
        "Scenario: external_pointer_trust_laundering_rejected",
        "Reason code: external_pointer_trust_laundering_rejected",
        "",
        "7. ACT 5 — ACCEPTED EVIDENCE IS NOT ACTION PERMISSION",
        "",
        "Even if Root creates bounded AcceptedEvidence, it does not become future action permission.",
        "Evidence is not permission.",
        "Result: needs_root_review.",
        "Scenario: accepted_evidence_from_compromised_source_is_not_action_permission",
        "Reason code: accepted_evidence_not_action_permission",
        "",
        "8. ACT 6 — COMPOSITE PRESSURE",
        "",
        "Bank pressure + stale legal pressure + warehouse contradiction + pointer laundering + candidate pressure still does not bypass Root.",
        "Root remains final authority.",
        "Scenario: root_final_authority_preserved_under_compromised_upstream_pressure",
        "Reason code: root_final_authority_preserved_under_compromised_upstream_pressure",
        "",
        "9. COUNTERS",
        "",
        f"* underlying_proof_status: {report['status']}",
        f"* walkthrough_required_counters_match: {counters_match}",
        *_counter_lines(report),
        "",
        "10. LIMITATIONS",
        "",
        "This walkthrough is deterministic/local and explanatory only.",
        "No production connector.",
        "No production DRS.",
        "No external/global DRS.",
        "No network.",
        "No Gemini.",
        "No Negative Trace.",
        "No DRS Poisoning Resistance.",
        "No Economic Adversary.",
        "No Marennya/UP.",
        "No manifest hardening.",
        "No transition matrix mutation.",
        "",
        "11. FINAL HUMAN SUMMARY",
        "",
        "A normal agent may confuse official-looking sources, signed-looking stale documents, repeated external pointers, schema-valid content, validation packets, or accepted evidence with truth or permission.",
        "Hedgehog OS keeps them bounded.",
        "They may inform or force review, but they do not become authority.",
        "Root remains final authority.",
        "",
        f"underlying_proof_status: {report['status']}",
        f"walkthrough_required_counters_match: {counters_match}",
        f"root_final_authority_preserved_count: {counters['root_final_authority_preserved_count']}",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    report = run_all_scenarios()
    walkthrough = build_walkthrough()
    print(walkthrough, end="")
    return 0 if _required_counters_match(report) else 1


if __name__ == "__main__":
    raise SystemExit(main())
