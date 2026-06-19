from __future__ import annotations

from demo.run_human_drs_lineage_provenance_pressure_walkthrough_v01 import (
    build_walkthrough,
    main,
)


def test_walkthrough_title_and_required_sections_present():
    output = build_walkthrough()
    assert "HEDGEHOG OS — HUMAN DRS LINEAGE / PROVENANCE PRESSURE WALKTHROUGH" in output
    assert "1. WHAT THIS WALKTHROUGH IS" in output
    assert "2. CORE RULE" in output
    for act in (
        "ACT 1",
        "ACT 2",
        "ACT 3",
        "ACT 4",
        "ACT 5",
        "ACT 6",
        "ACT 7",
        "ACT 8",
        "ACT 9",
    ):
        assert act in output
    assert "12. WHAT THE PROOF COUNTERS SHOW" in output
    assert "13. LIMITATIONS" in output
    assert "14. FINAL HUMAN SUMMARY" in output


def test_core_rules_are_present():
    output = build_walkthrough()
    for rule in (
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
    ):
        assert rule in output


def test_all_scenario_concepts_and_reason_codes_are_present():
    output = build_walkthrough()
    required = (
        "trace_derived_from_trace_informs_only",
        "lineage_informs_only",
        "reuse_candidate_derived_from_old_accepted_evidence_requires_review",
        "accepted_evidence_ancestry_not_action_permission",
        "bridge_traversal_across_domain_informs_only",
        "bridge_informs_only",
        "quarantine_near_reuse_candidate_warns_or_blocks",
        "quarantine_proximity_bounded",
        "deadend_near_reuse_candidate_warns_or_blocks",
        "deadend_proximity_bounded",
        "conflicting_provenance_blocks_direct_reuse",
        "conflictcheck_advisory_root_required",
        "trusted_newer_provenance_can_request_supersession_review_but_not_self_authorize",
        "supersession_review_required",
        "audit_hash_continuity_does_not_create_truth",
        "audit_hash_continuity_not_truth",
        "high_reuse_lineage_does_not_create_authority",
        "popularity_not_authority",
        "root_final_authority_preserved_across_lineage_pressure",
        "root_final_authority_preserved",
    )
    for item in required:
        assert item in output


def test_exact_counters_are_shown():
    output = build_walkthrough()
    for counter in (
        "scenarios_total: 10",
        "scenarios_passed: 10",
        "direct_reuse_allowed_count: 0",
        "direct_reuse_blocked_count: 10",
        "root_review_required_count: 10",
        "root_final_authority_preserved_count: 10",
        "lineage_decides_count: 0",
        "provenance_truth_claimed_count: 0",
        "audit_hash_truth_claimed_count: 0",
        "bridge_authority_transfer_count: 0",
        "quarantine_global_taint_count: 0",
        "deadend_global_taint_count: 0",
        "conflictcheck_authority_count: 0",
        "gt_authority_count: 0",
        "production_drs_used_count: 0",
        "external_drs_used_count: 0",
        "network_used_count: 0",
        "gemini_used_count: 0",
        "marennya_activated_count: 0",
        "up_activated_count: 0",
    ):
        assert counter in output


def test_limitations_and_no_overclaim_language():
    output = build_walkthrough()
    for limitation in (
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
    ):
        assert limitation in output
    assert ("production DRS " + "implemented") not in output
    assert ("external DRS " + "implemented") not in output
    assert ("global DRS " + "implemented") not in output
    assert ("production " + "ready") not in output.lower()
    assert ("public auditor " + "ready") not in output.lower()


def test_final_human_summary_and_root_authority_present():
    output = build_walkthrough()
    assert "A normal agent might confuse ancestry, provenance, audit history, bridge context, or popularity with truth." in output
    assert "Hedgehog OS keeps them as bounded pressure signals." in output
    assert "They can inform, warn, or block." in output
    assert "They cannot decide." in output
    assert "Root remains final authority." in output


def test_main_exits_successfully(capsys):
    assert main() == 0
    captured = capsys.readouterr()
    assert "underlying_proof_status: PASS" in captured.out
    assert "walkthrough_required_counters_match: True" in captured.out
