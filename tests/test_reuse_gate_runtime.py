from copy import deepcopy

from hedgehog.reuse_gate import (
    compute_conflict_score,
    compute_freshness_score,
    compute_gt_trust_score,
    compute_policy_score,
    compute_reuse_score,
    evaluate_reuse_candidates,
)
from hedgehog.time_model import make_temporal_query, make_time_envelope


def make_record(
    record_id="work_reuse_001",
    status="accepted",
    half_life_hours=400.0,
    decay_rate=0.002,
):
    return {
        "record_id": record_id,
        "layer": "work",
        "type": "task_outcome",
        "domain": "government_certificate",
        "content": {
            "summary": "Mock certificate request pipeline completed."
        },
        "time_envelope": make_time_envelope("sess_reuse_gate_001"),
        "provenance": {
            "request_id": "req_reuse_gate_001",
            "created_by": "root_orchestrator",
            "trace_refs": [],
        },
        "gt": {
            "gt_report_id": "gt:reuse_gate:test",
            "half_life_hours": half_life_hours,
            "decay_rate": decay_rate,
        },
        "status": status,
    }


def test_reuse_gate_returns_none_without_records():
    result = evaluate_reuse_candidates([], make_temporal_query())

    assert result["reuse_decision"] == "none"
    assert result["best_record_id"] is None
    assert result["reused_record_ids"] == []
    assert result["candidate_scores"] == []


def test_reuse_gate_scores_accepted_gt_record():
    record = make_record()
    temporal_query = make_temporal_query()

    assert compute_freshness_score(record, temporal_query) > 0.9
    assert compute_gt_trust_score(record) > 0.0
    assert compute_policy_score(record) == 1.0
    assert compute_conflict_score(record) == 1.0

    score = compute_reuse_score(record, temporal_query)
    assert score["record_id"] == record["record_id"]
    assert 0.0 <= score["reuse_score"] <= 1.0
    assert score["policy"] == 1.0
    assert score["reason"] == "gt_trust_below_threshold"


def test_reuse_gate_reports_low_gt_trust_when_score_is_high_enough():
    temporal_query = make_temporal_query()
    record = make_record(
        record_id="work_low_gt_high_score",
        half_life_hours=800.0,
        decay_rate=10.0,
    )

    score = compute_reuse_score(record, temporal_query)

    assert score["reuse_score"] >= 0.75
    assert score["gt_trust"] < 0.5
    assert score["eligible"] is False
    assert score["reason"] == "gt_trust_below_threshold"


def test_reuse_gate_reports_low_reuse_score():
    temporal_query = make_temporal_query()
    record = make_record(
        record_id="work_low_score",
        half_life_hours=0.0,
        decay_rate=10.0,
    )

    score = compute_reuse_score(record, temporal_query)

    assert score["reuse_score"] < 0.75
    assert score["eligible"] is False
    assert score["reason"] == "reuse_score_below_threshold"


def test_reuse_gate_rejects_rejected_or_archived_records():
    temporal_query = make_temporal_query()
    rejected = make_record(record_id="work_rejected", status="rejected")
    archived = make_record(record_id="work_archived", status="archived")

    for record in [rejected, archived]:
        score = compute_reuse_score(record, temporal_query)
        assert score["policy"] == 0.0
        assert score["eligible"] is False
        assert score["reason"] == "policy_rejected"

    result = evaluate_reuse_candidates([rejected, archived], temporal_query)
    assert result["reuse_decision"] == "context_only"
    assert result["reused_record_ids"] == []


def test_reuse_gate_can_mark_direct_reuse_candidate_without_applying_reuse():
    temporal_query = make_temporal_query()
    strong_record = make_record(
        record_id="work_strong_candidate",
        half_life_hours=2_000.0,
        decay_rate=0.0001,
    )

    result = evaluate_reuse_candidates([strong_record], temporal_query)

    assert result["reuse_decision"] == "direct_reuse_candidate"
    assert result["best_record_id"] == "work_strong_candidate"
    assert result["reused_record_ids"] == []
    assert result["candidate_scores"][0]["eligible"] is True
    assert result["candidate_scores"][0]["reason"] == "eligible"


def test_reuse_gate_conflict_marker_blocks_eligibility():
    temporal_query = make_temporal_query()
    record = make_record(half_life_hours=2_000.0, decay_rate=0.0001)
    conflicted = deepcopy(record)
    conflicted["content"]["summary"] = "Prior path has conflict marker."

    score = compute_reuse_score(conflicted, temporal_query)

    assert score["conflict"] == 0.0
    assert score["eligible"] is False
    assert score["reason"] == "conflict_detected"
