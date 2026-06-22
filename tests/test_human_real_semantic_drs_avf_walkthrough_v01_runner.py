from __future__ import annotations

import subprocess
import sys

from demo.run_human_real_semantic_drs_avf_walkthrough_v01 import (
    AVF_SCENARIOS,
    DRS_SCENARIOS,
    SECTION_HEADINGS,
    TITLE,
    build_walkthrough,
    main,
)


ACT_HEADINGS = tuple(heading for heading in SECTION_HEADINGS if heading.startswith("ACT "))

RAW_SHAPE_MARKERS = (
    "ValidationPacket-like",
    "EvidenceCandidate-like",
    "ResultProposal-like",
    "ConnectorObservation-like",
)

DRS_COUNTER_LINES = (
    "drs_underlying_runtime_status: PASS",
    "drs_scenarios_total: 8",
    "drs_scenarios_passed: 8",
    "records_written_count: 9",
    "resolve_queries_count: 7",
    "candidates_returned_count: 8",
    "drs_direct_reuse_allowed_count: 0",
    "root_review_required_count: 8",
    "stale_record_reuse_blocked_count: 1",
    "quarantine_reuse_blocked_count: 1",
    "changed_worldstate_reuse_blocked_count: 1",
    "conflicting_provenance_blocked_count: 1",
    "duplicate_poisoning_records_seen_count: 2",
    "poisoning_pressure_authority_claimed_count: 0",
    "drs_action_permission_granted_count: 0",
    "drs_production_drs_used_count: 0",
    "drs_external_drs_used_count: 0",
    "drs_network_used_count: 0",
    "drs_gemini_used_count: 0",
    "drs_root_final_authority_preserved_count: 8",
)

AVF_COUNTER_LINES = (
    "avf_underlying_runtime_status: PASS",
    "avf_scenarios_total: 9",
    "avf_scenarios_passed: 9",
    "drs_candidates_input_count: 17",
    "candidate_vectors_generated_count: 17",
    "avf_scores_computed_count: 17",
    "ranked_candidates_count: 17",
    "top_ranked_candidates_count: 9",
    "avf_direct_reuse_allowed_count: 0",
    "avf_action_permission_granted_count: 0",
    "avf_authority_claimed_count: 0",
    "vector_truth_claimed_count: 0",
    "schema_validity_truth_claimed_count: 0",
    "duplicate_spam_authority_claimed_count: 0",
    "high_score_direct_reuse_granted_count: 0",
    "avf_network_used_count: 0",
    "avf_gemini_used_count: 0",
    "avf_root_final_authority_preserved_count: 9",
)

COMBINED_COUNTER_LINES = (
    "walkthrough_required_counters_match: True",
    "combined_direct_reuse_allowed_count: 0",
    "combined_action_permission_granted_count: 0",
    "combined_network_used_count: 0",
    "combined_gemini_used_count: 0",
)

VALIDATION_MARKERS = (
    "DRS runtime checkpoint: 4f513d1",
    "DRS runtime commit: 2a18df5",
    "DRS technical audit: 6bb2422",
    "CandidateVector/AVF runtime commit: 1506eea",
    "CandidateVector/AVF technical audit: cf3da99",
    "CandidateVector/AVF focused tests: 51 passed, 1 warning",
    "CandidateVector/AVF full pytest: 1772 passed, 60 warnings in 957.62s",
    "DRS full pytest at checkpoint: 1754 passed, 60 warnings in 934.65s",
)


def test_module_imports_and_main_returns_zero(capsys) -> None:
    assert main() == 0
    output = capsys.readouterr().out
    assert TITLE in output
    assert "walkthrough_required_counters_match: True" in output


def test_command_execution_exits_zero() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "demo.run_human_real_semantic_drs_avf_walkthrough_v01"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    assert TITLE in completed.stdout
    assert "FINAL HUMAN SUMMARY" in completed.stdout
    assert "combined_direct_reuse_allowed_count: 0" in completed.stdout


def test_output_includes_required_sections_and_acts() -> None:
    output = build_walkthrough()

    assert TITLE in output
    for heading in SECTION_HEADINGS:
        assert heading in output
    for heading in ACT_HEADINGS:
        assert heading in output


def test_output_includes_drs_and_avf_scenario_names() -> None:
    output = build_walkthrough()

    for scenario_id in DRS_SCENARIOS:
        assert scenario_id in output
    for scenario_id in AVF_SCENARIOS:
        assert scenario_id in output


def test_output_includes_raw_shape_rejection_concepts() -> None:
    output = build_walkthrough()

    for marker in RAW_SHAPE_MARKERS:
        assert marker in output


def test_output_includes_required_counters() -> None:
    output = build_walkthrough()

    for line in DRS_COUNTER_LINES:
        assert line in output
    for line in AVF_COUNTER_LINES:
        assert line in output
    for line in COMBINED_COUNTER_LINES:
        assert line in output


def test_output_includes_validation_summary_and_boundaries() -> None:
    output = build_walkthrough()

    for marker in VALIDATION_MARKERS:
        assert marker in output
    for marker in (
        "DRS record is not truth",
        "DRS hit is not authority",
        "Candidate vector is not truth",
        "AVF score is not authority",
        "Top-ranked candidate is not action permission",
        "GT/LGT remains advisory",
        "Root remains final authority",
        "Real Semantic Runtime MVP is not complete",
    ):
        assert marker in output


def test_output_does_not_claim_readiness_or_completion() -> None:
    output = build_walkthrough()
    forbidden = (
        "production " + "ready",
        "public auditor " + "ready",
        "public " + "ready",
        "runtime " + "complete",
        "public launch " + "ready",
        "whitepaper " + "ready",
        "direct reuse " + "allowed",
        "action permission " + "granted",
        "AVF is " + "authority",
        "candidate vector is " + "truth",
    )

    assert not any(marker in output for marker in forbidden)
