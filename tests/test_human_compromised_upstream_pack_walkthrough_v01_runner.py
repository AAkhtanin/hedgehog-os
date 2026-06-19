from __future__ import annotations

import subprocess
import sys

from demo.run_human_compromised_upstream_pack_walkthrough_v01 import (
    build_walkthrough,
    main,
)


def test_human_walkthrough_module_imports_and_main_returns_zero(capsys):
    assert main() == 0
    captured = capsys.readouterr()
    assert "underlying_proof_status: PASS" in captured.out
    assert "walkthrough_required_counters_match: True" in captured.out


def test_command_execution_exits_zero():
    result = subprocess.run(
        [sys.executable, "-m", "demo.run_human_compromised_upstream_pack_walkthrough_v01"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "HEDGEHOG OS — HUMAN COMPROMISED UPSTREAM WALKTHROUGH v0.1" in result.stdout
    assert "Root remains final authority" in result.stdout


def test_title_sections_and_acts_present():
    output = build_walkthrough()
    assert "HEDGEHOG OS — HUMAN COMPROMISED UPSTREAM WALKTHROUGH v0.1" in output
    assert "1. WHAT THIS WALKTHROUGH IS" in output
    assert "2. CORE RULE" in output
    assert "3. ACT 1 — COMPROMISED BANK SOURCE" in output
    assert "4. ACT 2 — STALE SIGNED-LOOKING LEGAL SOURCE" in output
    assert "5. ACT 3 — WAREHOUSE CONTRADICTION" in output
    assert "6. ACT 4 — EXTERNAL POINTER TRUST LAUNDERING" in output
    assert "7. ACT 5 — ACCEPTED EVIDENCE IS NOT ACTION PERMISSION" in output
    assert "8. ACT 6 — COMPOSITE PRESSURE" in output
    assert "9. COUNTERS" in output
    assert "10. LIMITATIONS" in output
    assert "11. FINAL HUMAN SUMMARY" in output


def test_core_rule_is_present():
    output = build_walkthrough()
    for rule in (
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
    ):
        assert rule in output


def test_all_reason_codes_are_present():
    output = build_walkthrough()
    for reason in (
        "compromised_source_not_truth",
        "stale_signed_source_requires_review",
        "conflicting_warehouse_provenance_blocks_ready",
        "external_pointer_trust_laundering_rejected",
        "accepted_evidence_not_action_permission",
        "root_final_authority_preserved_under_compromised_upstream_pressure",
    ):
        assert reason in output


def test_required_counters_are_present():
    output = build_walkthrough()
    for counter in (
        "underlying_proof_status: PASS",
        "walkthrough_required_counters_match: True",
        "scenarios_total: 6",
        "scenarios_passed: 6",
        "direct_ready_allowed_count: 0",
        "direct_reuse_allowed_count: 0",
        "action_permission_granted_count: 0",
        "source_truth_claimed_count: 0",
        "schema_validity_truth_claimed_count: 0",
        "signed_source_truth_claimed_count: 0",
        "pointer_trust_claimed_count: 0",
        "evidence_candidate_authority_claimed_count: 0",
        "validation_packet_authority_claimed_count: 0",
        "accepted_evidence_action_permission_claimed_count: 0",
        "conflictcheck_authority_count: 0",
        "gt_authority_count: 0",
        "root_final_authority_preserved_count: 6",
        "production_connector_used_count: 0",
        "production_drs_used_count: 0",
        "external_drs_used_count: 0",
        "network_used_count: 0",
        "gemini_used_count: 0",
        "negative_trace_implemented_count: 0",
        "auto_governance_implemented_count: 0",
        "manifest_hardening_implemented_count: 0",
        "transition_matrix_mutated_count: 0",
        "marennya_activated_count: 0",
        "up_activated_count: 0",
    ):
        assert counter in output


def test_limitations_and_final_summary_are_present():
    output = build_walkthrough()
    for text in (
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
        "A normal agent may confuse official-looking sources, signed-looking stale documents, repeated external pointers, schema-valid content, validation packets, or accepted evidence with truth or permission.",
        "Hedgehog OS keeps them bounded.",
        "They may inform or force review, but they do not become authority.",
        "Root remains final authority.",
    ):
        assert text in output


def test_walkthrough_does_not_claim_production_or_public_auditor_readiness():
    output = build_walkthrough().lower()
    assert ("production " + "ready") not in output
    assert ("public auditor " + "ready") not in output
    assert ("production " + "readiness") not in output
    assert ("public auditor " + "readiness") not in output
