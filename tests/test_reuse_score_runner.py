from __future__ import annotations

from demo.run_reuse_score import _raw_score
from demo.run_reuse_score import collect_reuse_score
from demo.run_reuse_score import run_reuse_score


def _candidate_by_id(report):
    return {candidate.record_id: candidate for candidate in report.candidates}


def _expected_score(candidate):
    return _raw_score(
        quality=candidate.quality,
        freshness=candidate.freshness,
        gt_trust=candidate.gt_trust,
        semantic_similarity=candidate.semantic_similarity,
        graph_proximity=candidate.graph_proximity,
        typed_positive_signal=candidate.typed_positive_signal,
        warning_penalty=candidate.warning_penalty,
        blocking_penalty=candidate.blocking_penalty,
        needs_user_penalty=candidate.needs_user_penalty,
        degraded_penalty=candidate.degraded_penalty,
        contradiction_penalty=candidate.contradiction_penalty,
        risk_penalty=candidate.risk_penalty,
    )


def test_runner_output_contains_required_sections():
    output = run_reuse_score()

    assert "[REUSESCORE]" in output
    assert "[DATASET]" in output
    assert "[SCORING MODEL]" in output
    assert "[REUSE CANDIDATES]" in output
    assert "[POLICY SAFETY]" in output
    assert "[SUMMARY]" in output
    assert "reuse_score_status: PASS" in output


def test_candidates_are_loaded_from_typed_edge_proof():
    report = collect_reuse_score()

    assert len(report.source_report.records) == 10
    assert len(report.candidates) == 10
    assert {candidate.record_id for candidate in report.candidates} == {
        "root_work",
        "child_work",
        "grandchild_work",
        "nearby_dead_end",
        "nearby_blocked_trace",
        "nearby_degraded_trace",
        "nearby_needs_user_trace",
        "nearby_quarantine",
        "supportive_work",
        "unrelated_fresh_work",
    }


def test_candidates_are_scored_with_numeric_components():
    report = collect_reuse_score()

    for candidate in report.candidates:
        assert isinstance(candidate.quality, float)
        assert isinstance(candidate.freshness, float)
        assert isinstance(candidate.gt_trust, float)
        assert isinstance(candidate.semantic_similarity, float)
        assert isinstance(candidate.graph_proximity, float)
        assert isinstance(candidate.raw_reuse_score, float)


def test_raw_reuse_score_is_computed_from_components():
    report = collect_reuse_score()

    for candidate in report.candidates:
        assert candidate.raw_reuse_score == _expected_score(candidate)


def test_graph_proximity_contributes_as_signal():
    rows = _candidate_by_id(collect_reuse_score())

    assert rows["root_work"].graph_proximity == 1.0
    assert rows["child_work"].graph_proximity > 0.0
    assert rows["unrelated_fresh_work"].graph_proximity == 0.0
    assert collect_reuse_score().summary["graph_proximity_used_as_signal"] is True


def test_typed_positive_signal_contributes_as_signal():
    rows = _candidate_by_id(collect_reuse_score())

    assert rows["child_work"].typed_positive_signal > 0.0
    assert rows["supportive_work"].typed_positive_signal > 0.0
    assert collect_reuse_score().summary["typed_edges_used_as_signals"] is True


def test_penalty_components_are_applied():
    rows = _candidate_by_id(collect_reuse_score())

    assert rows["nearby_dead_end"].warning_penalty > 0.0
    assert rows["nearby_blocked_trace"].blocking_penalty > 0.0
    assert rows["nearby_needs_user_trace"].needs_user_penalty > 0.0
    assert rows["nearby_degraded_trace"].degraded_penalty > 0.0
    assert rows["child_work"].contradiction_penalty > 0.0


def test_policy_gate_is_applied_separately_from_raw_score():
    blocked = _candidate_by_id(collect_reuse_score())["nearby_blocked_trace"]

    assert blocked.raw_reuse_score > 0.55
    assert blocked.policy_allowed is False
    assert blocked.direct_reuse_allowed_after_policy is False
    assert blocked.reuse_recommendation == "blocked"


def test_high_score_cannot_override_policy():
    report = collect_reuse_score()
    high_scoring_unsafe = [
        candidate
        for candidate in report.candidates
        if candidate.raw_reuse_score > 0.50
        and candidate.taxonomy_kind
        in {"quarantine", "dead_end", "blocked_trace", "degraded_trace", "needs_user_trace"}
    ]

    assert high_scoring_unsafe
    assert all(
        not candidate.direct_reuse_allowed_after_policy
        for candidate in high_scoring_unsafe
    )
    assert report.safety["high_score_unsafe_record_reused"] is False


def test_quarantine_is_not_direct_reuse_eligible():
    row = _candidate_by_id(collect_reuse_score())["nearby_quarantine"]

    assert row.taxonomy_kind == "quarantine"
    assert row.direct_reuse_allowed_after_policy is False
    assert row.reuse_recommendation == "quarantine"


def test_dead_end_is_not_direct_reuse_eligible():
    row = _candidate_by_id(collect_reuse_score())["nearby_dead_end"]

    assert row.taxonomy_kind == "dead_end"
    assert row.direct_reuse_allowed_after_policy is False
    assert row.reuse_recommendation == "dead_end"


def test_blocked_trace_is_not_direct_reuse_eligible():
    row = _candidate_by_id(collect_reuse_score())["nearby_blocked_trace"]

    assert row.taxonomy_kind == "blocked_trace"
    assert row.direct_reuse_allowed_after_policy is False
    assert row.reuse_recommendation == "blocked"


def test_degraded_trace_is_not_direct_reuse_eligible():
    row = _candidate_by_id(collect_reuse_score())["nearby_degraded_trace"]

    assert row.taxonomy_kind == "degraded_trace"
    assert row.direct_reuse_allowed_after_policy is False
    assert row.reuse_recommendation == "degraded"


def test_needs_user_trace_is_not_direct_reuse_eligible():
    row = _candidate_by_id(collect_reuse_score())["nearby_needs_user_trace"]

    assert row.taxonomy_kind == "needs_user_trace"
    assert row.direct_reuse_allowed_after_policy is False
    assert row.reuse_recommendation == "needs_user"


def test_contradiction_does_not_auto_reuse_and_requires_conflict_check():
    row = _candidate_by_id(collect_reuse_score())["child_work"]
    report = collect_reuse_score()

    assert row.contradiction_penalty > 0.0
    assert row.direct_reuse_allowed_after_policy is False
    assert row.reuse_recommendation == "needs_conflict_check"
    assert report.safety["contradiction_auto_reuse_candidates"] == 0
    assert report.safety["contradiction_requires_conflict_check"] is True


def test_only_successful_work_can_be_direct_reuse_candidate():
    report = collect_reuse_score()
    direct = [
        candidate
        for candidate in report.candidates
        if candidate.direct_reuse_allowed_after_policy
    ]

    assert direct
    assert all(candidate.taxonomy_kind == "work_candidate" for candidate in direct)
    assert all(candidate.source.record["layer"] == "work" for candidate in direct)
    assert report.safety["only_successful_work_can_be_direct_reuse_candidate"] is True


def test_direct_reuse_policy_remains_unchanged():
    report = collect_reuse_score()

    assert report.safety["direct_reuse_policy_unchanged"] is True
    assert report.summary["direct_reuse_candidates_after_policy"] >= 1
    assert report.summary["unsafe_direct_reuse_candidates"] == 0


def test_reuse_score_is_advisory_only():
    report = collect_reuse_score()
    output = run_reuse_score()

    assert report.summary["ReuseScore_is_advisory"] is True
    assert "ReuseScore is advisory/ranking only" in output
    assert "ReuseScore is not Root" in output
    assert "ReuseScore is not ReuseGate" in output


def test_root_is_not_bypassed():
    report = collect_reuse_score()

    assert report.safety["Root_authority_preserved"] is True
    assert report.summary["Root_not_bypassed"] is True


def test_reuse_gate_is_not_bypassed():
    report = collect_reuse_score()

    assert report.safety["ReuseGate_authority_preserved"] is True
    assert report.summary["ReuseGate_not_bypassed"] is True


def test_global_and_external_drs_are_not_implemented():
    report = collect_reuse_score()
    output = run_reuse_score()

    assert report.summary["local_drs_only"] is True
    assert report.summary["external_drs_network_implemented"] is False
    assert report.summary["global_drs_implemented"] is False
    assert "external_drs_network_implemented: false" in output
    assert "global_drs_implemented: false" in output


def test_production_conflict_check_is_not_implemented():
    output = run_reuse_score()

    assert "production_conflict_check_implemented: false" in output


def test_scoring_model_is_not_billing_or_policy_override():
    report = collect_reuse_score()

    assert report.scoring_model["compute_model"] == "illustrative_deterministic_reuse_score"
    assert report.scoring_model["real_token_billing_measured"] is False
    assert report.scoring_model["policy_gate_applied_after_score"] is True
    assert report.scoring_model["high_score_overrides_policy"] is False
    assert report.scoring_model["direct_reuse_requires_eligible_work"] is True
    assert report.scoring_model["context_memory_does_not_equal_reuse"] is True
