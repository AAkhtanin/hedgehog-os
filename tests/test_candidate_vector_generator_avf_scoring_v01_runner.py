from __future__ import annotations

import subprocess
import sys

import demo.run_candidate_vector_generator_avf_scoring_v01 as runner
import hedgehog.candidate_vector_generator as generator
from hedgehog.candidate_vector_generator import (
    CandidateVectorInput,
    CandidateVectorReport,
    CandidateVectorScore,
    GeneratedCandidateVector,
    build_avf_candidate_report,
    generate_candidate_vectors,
    rank_candidate_vectors,
    score_candidate_vector,
)


def _input(
    candidate_id: str,
    *,
    record_id: str | None = None,
    freshness_state: str = "normal",
    conflict_flags: tuple[str, ...] = (),
    quarantine_deadend_flags: tuple[str, ...] = (),
    poisoning_flags: tuple[str, ...] = (),
    schema_valid: bool = True,
) -> CandidateVectorInput:
    return CandidateVectorInput(
        resolved_candidate_id=candidate_id,
        source_record_id=record_id or candidate_id.replace("candidate:", "record:"),
        domain="mock_government_certificate",
        subject_key="certificate:demo-user",
        claim_key="document_readiness",
        content_summary="Root-reviewed certificate renewal memory.",
        semantic_tokens=(
            "certificate",
            "renewal",
            "document_readiness",
            "root_reviewed",
            "local_drs",
            "trace",
            "source",
            "provenance",
        ),
        time_envelope={"freshness_class": freshness_state},
        freshness_state=freshness_state,
        provenance_refs=({"created_by": "root_orchestrator"},),
        trace_refs=({"trace_id": "trace:test"},),
        source_refs=({"source": "local_drs", "source_id": "source:test"},),
        conflict_flags=conflict_flags,
        quarantine_deadend_flags=quarantine_deadend_flags,
        poisoning_flags=poisoning_flags,
        root_review_required=True,
        direct_reuse_allowed=False,
        schema_valid=schema_valid,
    )


def test_api_symbols_exist() -> None:
    assert generator.CandidateVectorInput is CandidateVectorInput
    assert generator.GeneratedCandidateVector is GeneratedCandidateVector
    assert generator.CandidateVectorScore is CandidateVectorScore
    assert generator.CandidateVectorReport is CandidateVectorReport
    assert callable(generator.generate_candidate_vectors)
    assert callable(generator.score_candidate_vector)
    assert callable(generator.rank_candidate_vectors)
    assert callable(generator.build_avf_candidate_report)


def test_generate_candidate_vectors_returns_bounded_vectors() -> None:
    vectors = generate_candidate_vectors((_input("candidate:clean"),))

    assert len(vectors) == 1
    vector = vectors[0]
    assert vector.advisory_only is True
    assert vector.truth_claimed is False
    assert vector.authority_claimed is False
    assert vector.action_permission_claimed is False
    assert vector.direct_reuse_allowed is False
    assert vector.vector.source == "local_drs"


def test_score_candidate_vector_returns_deterministic_score_object() -> None:
    vector = generate_candidate_vectors((_input("candidate:clean"),))[0]
    first = score_candidate_vector(vector)
    second = score_candidate_vector(vector)

    assert isinstance(first, CandidateVectorScore)
    assert first == second
    assert first.score_is_authority is False
    assert first.action_permission_granted is False
    assert first.direct_reuse_allowed is False
    assert first.gt_lgt_review_required is True
    assert first.root_review_required is True


def test_rank_candidate_vectors_orders_candidates_without_authorizing() -> None:
    vectors = generate_candidate_vectors(
        (
            _input("candidate:stale", freshness_state="stale"),
            _input("candidate:clean"),
        )
    )

    ranked = rank_candidate_vectors(vectors)

    assert ranked[0].candidate_id == "candidate:clean"
    assert all(score.direct_reuse_allowed is False for score in ranked)
    assert all(score.action_permission_granted is False for score in ranked)
    assert all(score.score_is_authority is False for score in ranked)


def test_build_avf_candidate_report_returns_structured_report() -> None:
    report = build_avf_candidate_report((_input("candidate:clean"),))

    assert isinstance(report, CandidateVectorReport)
    assert len(report.candidates) == 1
    assert report.top_candidate_ids == ("candidate:clean",)
    assert report.direct_reuse_allowed_count == 0
    assert report.root_review_required is True
    assert report.root_final_authority_preserved is True
    assert report.counters["direct_reuse_allowed_count"] == 0
    assert report.counters["action_permission_granted_count"] == 0
    assert report.counters["avf_authority_claimed_count"] == 0
    assert report.counters["vector_truth_claimed_count"] == 0
    assert report.counters["schema_validity_truth_claimed_count"] == 0
    assert report.counters["duplicate_spam_authority_claimed_count"] == 0
    assert report.counters["high_score_direct_reuse_granted_count"] == 0


def test_stale_candidate_has_review_required_penalty() -> None:
    report = build_avf_candidate_report(
        (_input("candidate:stale", freshness_state="stale"),)
    )

    assert report.counters["stale_candidate_review_required_count"] == 1
    assert "stale_direct_reuse_block" in report.reason_codes
    assert report.ranked_candidates[0].review_required is True


def test_quarantine_deadend_candidate_blocked_from_direct_reuse() -> None:
    report = build_avf_candidate_report(
        (_input("candidate:quarantine", quarantine_deadend_flags=("quarantine",)),)
    )

    assert report.counters["quarantine_deadend_blocked_count"] == 1
    assert "quarantine_deadend_direct_reuse_block" in report.reason_codes
    assert report.ranked_candidates[0].direct_reuse_allowed is False


def test_conflicting_provenance_penalized_or_blocked() -> None:
    report = build_avf_candidate_report(
        (_input("candidate:conflict", conflict_flags=("conflicting_provenance",)),)
    )

    assert report.counters["conflicting_provenance_penalized_count"] == 1
    assert "conflicting_provenance_penalty" in report.reason_codes
    assert "conflicting_provenance_direct_reuse_block" in report.reason_codes


def test_duplicate_spam_does_not_win_by_volume() -> None:
    report = build_avf_candidate_report(
        (
            _input("candidate:clean"),
            _input("candidate:spam:a", poisoning_flags=("poisoning_pressure",)),
            _input("candidate:spam:b", poisoning_flags=("poisoning_pressure",)),
        )
    )

    assert report.top_candidate_ids == ("candidate:clean",)
    assert report.counters["duplicate_spam_candidates_seen_count"] == 2
    assert report.counters["duplicate_spam_authority_claimed_count"] == 0
    assert "duplicate_count_not_authority" in report.reason_codes


def test_high_score_still_requires_gt_lgt_root_review() -> None:
    report = build_avf_candidate_report((_input("candidate:high_score"),))
    score = report.ranked_candidates[0]

    assert score.score >= 0.75
    assert score.gt_lgt_review_required is True
    assert score.root_review_required is True
    assert "high_score_review_required" in report.reason_codes
    assert report.counters["high_score_direct_reuse_granted_count"] == 0


def test_schema_valid_vector_is_not_semantic_truth() -> None:
    report = build_avf_candidate_report((_input("candidate:schema_valid"),))

    assert report.counters["schema_validity_truth_claimed_count"] == 0
    assert "schema_validity_shape_only" in report.reason_codes
    assert "schema_valid_vector_is_not_semantic_truth" in report.reason_codes


def test_runner_result_passes_required_counters_and_scenarios() -> None:
    result = runner.run_all_scenarios()
    counters = result["counters"]

    assert result["scenarios_total"] == 9
    assert result["scenarios_passed"] == result["scenarios_total"]
    assert {scenario["scenario_id"] for scenario in result["scenarios"]} == set(
        runner.SCENARIOS
    )
    assert all(scenario["status"] == "PASS" for scenario in result["scenarios"])
    assert counters["direct_reuse_allowed_count"] == 0
    assert counters["action_permission_granted_count"] == 0
    assert counters["avf_authority_claimed_count"] == 0
    assert counters["vector_truth_claimed_count"] == 0
    assert counters["schema_validity_truth_claimed_count"] == 0
    assert counters["duplicate_spam_authority_claimed_count"] == 0
    assert counters["high_score_direct_reuse_granted_count"] == 0
    assert counters["manifest_mutation_count"] == 0
    assert counters["transition_matrix_mutation_count"] == 0
    assert counters["network_used_count"] == 0
    assert counters["gemini_used_count"] == 0
    assert (
        counters["root_final_authority_preserved_count"]
        == result["scenarios_total"]
    )


def test_main_returns_zero_and_command_output_has_pass() -> None:
    assert runner.main() == 0

    completed = subprocess.run(
        [sys.executable, "-m", "demo.run_candidate_vector_generator_avf_scoring_v01"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    expected_markers = (
        "FINAL STATUS: PASS",
        "scenarios_total: 9",
        "scenarios_passed: 9",
        "direct_reuse_allowed_count: 0",
        "action_permission_granted_count: 0",
        "avf_authority_claimed_count: 0",
        "vector_truth_claimed_count: 0",
        "schema_validity_truth_claimed_count: 0",
        "duplicate_spam_authority_claimed_count: 0",
        "high_score_direct_reuse_granted_count: 0",
        "network_used_count: 0",
        "gemini_used_count: 0",
        "root_final_authority_preserved_count: 9",
    )
    for marker in expected_markers:
        assert marker in completed.stdout


def test_runner_output_does_not_claim_public_or_runtime_completion() -> None:
    output = runner.render_report(runner.run_all_scenarios())
    forbidden = (
        "production " + "ready",
        "public auditor " + "ready",
        "public launch " + "ready",
        "whitepaper " + "ready",
        "runtime " + "complete",
        "direct reuse " + "allowed",
        "action permission " + "granted",
        "AVF is " + "authority",
        "candidate vector is " + "truth",
    )

    assert not any(term in output for term in forbidden)
