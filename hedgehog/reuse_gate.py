from __future__ import annotations

from datetime import datetime


REUSE_THRESHOLD = 0.75
FRESHNESS_THRESHOLD = 0.5
GT_TRUST_THRESHOLD = 0.5


def _clamp_01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def compute_freshness_score(record: dict, temporal_query: dict) -> float:
    envelope = record.get("time_envelope", {})
    record_time = envelope.get("kt_asof") or envelope.get("pt_created_at")
    as_of = temporal_query.get("as_of")
    if not record_time or not as_of:
        return 0.0

    age_seconds = max(
        0.0,
        (_parse_timestamp(as_of) - _parse_timestamp(record_time)).total_seconds(),
    )
    max_age_seconds = float(temporal_query.get("max_age_seconds") or 2_592_000)
    if max_age_seconds <= 0:
        return 0.0
    return _clamp_01(1.0 - (age_seconds / max_age_seconds))


def compute_gt_trust_score(record: dict) -> float:
    gt = record.get("gt", {})
    half_life_hours = float(gt.get("half_life_hours") or 0.0)
    decay_rate = float(gt.get("decay_rate") or 1.0)
    half_life_score = _clamp_01(half_life_hours / 1_000.0)
    decay_score = _clamp_01(1.0 / (1.0 + decay_rate * 1_000.0))
    return (half_life_score + decay_score) / 2


def compute_policy_score(record: dict) -> float:
    status = record.get("status")
    if status in {"rejected", "archived"}:
        return 0.0
    if status in {"accepted", "active"}:
        return 1.0
    return 0.5


def compute_conflict_score(record: dict) -> float:
    content = record.get("content", {})
    text = str(content).lower()
    conflict_markers = ("failure", "failed", "dead_end", "deadend", "conflict")
    if any(marker in text for marker in conflict_markers):
        return 0.0
    return 1.0


def compute_reuse_score(record: dict, temporal_query: dict) -> dict:
    freshness = compute_freshness_score(record, temporal_query)
    gt_trust = compute_gt_trust_score(record)
    policy = compute_policy_score(record)
    conflict = compute_conflict_score(record)
    reuse_score = (
        0.30 * freshness
        + 0.30 * gt_trust
        + 0.25 * policy
        + 0.15 * conflict
    )
    eligible = (
        reuse_score >= REUSE_THRESHOLD
        and freshness >= FRESHNESS_THRESHOLD
        and gt_trust >= GT_TRUST_THRESHOLD
        and policy == 1.0
        and conflict == 1.0
    )
    reason = "eligible" if eligible else "below_direct_reuse_threshold"
    if policy == 0.0:
        reason = "policy_rejected"
    elif conflict == 0.0:
        reason = "conflict_detected"

    return {
        "record_id": record.get("record_id"),
        "freshness": freshness,
        "gt_trust": gt_trust,
        "policy": policy,
        "conflict": conflict,
        "reuse_score": reuse_score,
        "eligible": eligible,
        "reason": reason,
    }


def evaluate_reuse_candidates(records: list[dict], temporal_query: dict) -> dict:
    if not records:
        return {
            "reuse_decision": "none",
            "best_record_id": None,
            "reused_record_ids": [],
            "candidate_scores": [],
        }

    candidate_scores = [
        compute_reuse_score(record, temporal_query)
        for record in records
    ]
    best = max(
        candidate_scores,
        key=lambda score: (score["reuse_score"], score["record_id"] or ""),
    )
    eligible_scores = [score for score in candidate_scores if score["eligible"]]
    reuse_decision = "direct_reuse_candidate" if eligible_scores else "context_only"

    return {
        "reuse_decision": reuse_decision,
        "best_record_id": best["record_id"],
        "reused_record_ids": [],
        "candidate_scores": candidate_scores,
    }
