from __future__ import annotations

import subprocess
import sys

from demo.run_human_real_local_drs_resolver_walkthrough_v01 import (
    build_walkthrough,
    main,
)


TITLE = "HEDGEHOG OS — HUMAN REAL LOCAL DRS RESOLVER WALKTHROUGH v0.1"

SECTION_HEADINGS = (
    "WHAT THIS WALKTHROUGH IS",
    "WHY THIS LAYER MATTERS",
    "CORE PIPELINE",
    "ACT 1 — WRITE MEANING",
    "ACT 2 — RESOLVE MEANING",
    "ACT 3 — ROOT REVIEW BEFORE REUSE",
    "ACT 4 — STALE / TTL PRESSURE",
    "ACT 5 — QUARANTINE / DEADEND PRESSURE",
    "ACT 6 — WORLDSTATE CHANGE",
    "ACT 7 — CONFLICTING PROVENANCE",
    "ACT 8 — POISONING PRESSURE",
    "ACT 9 — ROOTFINAL WRITEBACK",
    "SAFETY BOUNDARIES",
    "COUNTERS",
    "VALIDATION SUMMARY",
    "LIMITATIONS",
    "FINAL HUMAN SUMMARY",
)

ACT_HEADINGS = tuple(heading for heading in SECTION_HEADINGS if heading.startswith("ACT "))

SCENARIO_IDS = (
    "write_then_resolve_semantic_record_candidate_only",
    "stale_record_forces_root_review",
    "quarantine_proximity_blocks_direct_reuse",
    "changed_worldstate_blocks_old_reuse",
    "conflicting_provenance_blocks_reuse",
    "duplicate_poisoning_pressure_does_not_create_authority",
    "root_review_required_before_reuse_affects_final_output",
    "writeback_records_root_final_without_action_side_effects",
)

COUNTER_LINES = (
    "underlying_runtime_status: PASS",
    "walkthrough_required_counters_match: True",
    "scenarios_total: 8",
    "scenarios_passed: 8",
    "records_written_count: 9",
    "resolve_queries_count: 7",
    "candidates_returned_count: 8",
    "direct_reuse_allowed_count: 0",
    "root_review_required_count: 8",
    "poisoning_pressure_authority_claimed_count: 0",
    "action_permission_granted_count: 0",
    "production_drs_used_count: 0",
    "external_drs_used_count: 0",
    "network_used_count: 0",
    "gemini_used_count: 0",
    "root_final_authority_preserved_count: 8",
)


def test_build_walkthrough_contains_required_human_story():
    output = build_walkthrough()

    assert TITLE in output
    for heading in SECTION_HEADINGS:
        assert heading in output
    for heading in ACT_HEADINGS:
        assert heading in output
    for scenario_id in SCENARIO_IDS:
        assert scenario_id in output
    for marker in (
        "ValidationPacket-like",
        "EvidenceCandidate-like",
        "ResultProposal-like",
        "ConnectorObservation-like",
    ):
        assert marker in output
    for counter_line in COUNTER_LINES:
        assert counter_line in output
    assert "Root remains final authority" in output
    assert "Real Semantic Runtime MVP is not complete" in output


def test_main_returns_zero(capsys):
    assert main() == 0
    output = capsys.readouterr().out
    assert TITLE in output
    assert "underlying_runtime_status: PASS" in output


def test_command_execution_exits_zero():
    completed = subprocess.run(
        [sys.executable, "-m", "demo.run_human_real_local_drs_resolver_walkthrough_v01"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    output = completed.stdout
    assert TITLE in output
    assert "FINAL HUMAN SUMMARY" in output
    assert "underlying_runtime_status: PASS" in output
    assert "walkthrough_required_counters_match: True" in output


def test_walkthrough_avoids_public_or_production_readiness_claims():
    output = build_walkthrough()
    forbidden = (
        "production-ready",
        "public-ready",
        "runtime-complete",
    )
    assert not any(term in output for term in forbidden)
