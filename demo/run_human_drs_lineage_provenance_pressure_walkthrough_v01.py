from __future__ import annotations

from typing import Any

from demo.run_drs_lineage_provenance_pressure_v01 import run_all_scenarios


TITLE = "HEDGEHOG OS — HUMAN DRS LINEAGE / PROVENANCE PRESSURE WALKTHROUGH"

CORE_RULE = (
    "lineage informs",
    "lineage does not decide",
    "provenance does not become truth",
    "audit/hash-chain proves continuity, not truth",
    "accepted evidence ancestry is not future action permission",
    "bridge traversal is not authority transfer",
    "quarantine/deadend proximity is bounded",
    "ConflictCheck remains advisory",
    "GT remains advisory",
    "Root remains final authority",
)

REQUIRED_COUNTERS = {
    "scenarios_total": 10,
    "scenarios_passed": 10,
    "direct_reuse_allowed_count": 0,
    "direct_reuse_blocked_count": 10,
    "root_review_required_count": 10,
    "root_final_authority_preserved_count": 10,
    "lineage_decides_count": 0,
    "provenance_truth_claimed_count": 0,
    "audit_hash_truth_claimed_count": 0,
    "bridge_authority_transfer_count": 0,
    "quarantine_global_taint_count": 0,
    "deadend_global_taint_count": 0,
    "conflictcheck_authority_count": 0,
    "gt_authority_count": 0,
    "production_drs_used_count": 0,
    "external_drs_used_count": 0,
    "network_used_count": 0,
    "gemini_used_count": 0,
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
    lines = [
        TITLE,
        "",
        "1. WHAT THIS WALKTHROUGH IS",
        "",
        "This is a human-readable walkthrough over completed deterministic proof behavior.",
        "It does not create new runtime capability, schema, production DRS, external/global DRS, action permission, or authority.",
        "It does not create production persistence, execute external action, or change runtime integration.",
        "Root remains final authority.",
        "",
        "2. CORE RULE",
        "",
        *CORE_RULE,
        "",
        "3. ACT 1 — TRACE CAN COME FROM TRACE, BUT TRACE DOES NOT DECIDE",
        "",
        "A candidate trace is derived from an older trace.",
        "The old trace may help explain context.",
        "But derived ancestry does not authorize direct reuse.",
        "Scenario: trace_derived_from_trace_informs_only",
        "Reason code: lineage_informs_only",
        "direct_reuse_allowed: false",
        "Root review required",
        "",
        "4. ACT 2 — ACCEPTED EVIDENCE ANCESTRY IS NOT FUTURE ACTION PERMISSION",
        "",
        "A reuse candidate descends from older Root-created AcceptedEvidence.",
        "That history is useful.",
        "But old AcceptedEvidence is not future action permission.",
        "Scenario: reuse_candidate_derived_from_old_accepted_evidence_requires_review",
        "Reason code: accepted_evidence_ancestry_not_action_permission",
        "direct_reuse_allowed: false",
        "Root review required",
        "",
        "5. ACT 3 — BRIDGE TRAVERSAL INFORMS, BUT DOES NOT TRANSFER AUTHORITY",
        "",
        "A certificate-domain record helps a travel-domain question.",
        "The bridge carries context across domains.",
        "But the source domain cannot finalize the target domain.",
        "Scenario: bridge_traversal_across_domain_informs_only",
        "Reason code: bridge_informs_only",
        "bridge traversal is not authority transfer",
        "direct_reuse_allowed: false",
        "",
        "6. ACT 4 — QUARANTINE AND DEADEND ARE BOUNDED PRESSURE, NOT GLOBAL INFECTION",
        "",
        "A reuse candidate is near quarantine or deadend records.",
        "The system can warn or block reuse.",
        "But it must not globally taint the entire graph.",
        "Scenario: quarantine_near_reuse_candidate_warns_or_blocks",
        "Scenario: deadend_near_reuse_candidate_warns_or_blocks",
        "Reason code: quarantine_proximity_bounded",
        "Reason code: deadend_proximity_bounded",
        f"quarantine_global_taint_count: {report['aggregate_counters']['quarantine_global_taint_count']}",
        f"deadend_global_taint_count: {report['aggregate_counters']['deadend_global_taint_count']}",
        "",
        "7. ACT 5 — CONFLICTING PROVENANCE BLOCKS DIRECT REUSE, BUT DOES NOT DECIDE TRUTH",
        "",
        "Two records disagree about the same subject/claim.",
        "ConflictCheck blocks direct reuse.",
        "But ConflictCheck remains advisory until Root.",
        "Scenario: conflicting_provenance_blocks_direct_reuse",
        "Reason code: conflictcheck_advisory_root_required",
        "direct_reuse_allowed: false",
        "ConflictCheck remains advisory",
        "Root remains final authority",
        "",
        "8. ACT 6 — NEWER TRUSTED PROVENANCE CAN REQUEST REVIEW, NOT SELF-AUTHORIZE SUPERSESSION",
        "",
        "A newer trusted record points to older trusted work and requests replacement.",
        "It can request supersession review.",
        "It cannot replace older work by itself.",
        "Scenario: trusted_newer_provenance_can_request_supersession_review_but_not_self_authorize",
        "Reason code: supersession_review_required",
        "direct_reuse_allowed: false",
        "Root review required",
        "",
        "9. ACT 7 — AUDIT CHAIN PROVES CONTINUITY, NOT TRUTH",
        "",
        "The hash chain is valid.",
        "This proves continuity/history.",
        "It does not prove the claim is true now.",
        "Scenario: audit_hash_continuity_does_not_create_truth",
        "Reason code: audit_hash_continuity_not_truth",
        "audit/hash-chain proves continuity, not truth",
        "direct_reuse_allowed: false",
        "",
        "10. ACT 8 — POPULAR LINEAGE IS NOT AUTHORITY",
        "",
        "A candidate has high reuse count / many descendants.",
        "Popularity can preserve visibility.",
        "Popularity cannot make the candidate authoritative.",
        "Scenario: high_reuse_lineage_does_not_create_authority",
        "Reason code: popularity_not_authority",
        f"lineage_decides_count: {report['aggregate_counters']['lineage_decides_count']}",
        "direct_reuse_allowed: false",
        "",
        "11. ACT 9 — COMPOSITE PRESSURE STILL ENDS AT ROOT",
        "",
        "One candidate has derived trace, old AcceptedEvidence, bridge, quarantine, deadend, conflict, and audit links.",
        "Even in the composite case, non-Root artifacts do not decide.",
        "Root final authority is preserved.",
        "Scenario: root_final_authority_preserved_across_lineage_pressure",
        "Reason code: root_final_authority_preserved",
        f"root_final_authority_preserved_count: {report['aggregate_counters']['root_final_authority_preserved_count']}",
        f"direct_reuse_allowed_count: {report['aggregate_counters']['direct_reuse_allowed_count']}",
        "Root remains final authority",
        "",
        "12. WHAT THE PROOF COUNTERS SHOW",
        "",
        *_counter_lines(report),
        "",
        "13. LIMITATIONS",
        "",
        "This is deterministic local proof walkthrough only.",
        "No production DRS.",
        "No external/global DRS.",
        "No real connector.",
        "No network.",
        "No Gemini.",
        "No Marennya.",
        "No UP.",
        "No production persistence.",
        "No runtime integration.",
        "No schema mutation.",
        "No external action.",
        "No public auditor readiness claim.",
        "No production readiness claim.",
        "",
        "14. FINAL HUMAN SUMMARY",
        "",
        "A normal agent might confuse ancestry, provenance, audit history, bridge context, or popularity with truth.",
        "Hedgehog OS keeps them as bounded pressure signals.",
        "They can inform, warn, or block.",
        "They cannot decide.",
        "Root remains final authority.",
        "",
        f"underlying_proof_status: {report['status']}",
        f"walkthrough_required_counters_match: {_required_counters_match(report)}",
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
