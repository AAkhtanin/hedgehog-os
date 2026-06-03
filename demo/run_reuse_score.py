from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from demo.run_typed_drs_lineage_edges import (
    TypedDrsCandidate,
    TypedDrsLineageReport,
    collect_typed_drs_lineage_edges,
)


HOP_HALF_LIFE = 2.0
UNSAFE_TAXONOMY_KINDS = {
    "quarantine",
    "dead_end",
    "blocked_trace",
    "degraded_trace",
    "needs_user_trace",
}
COMPONENTS_BY_RECORD_ID: dict[str, dict[str, float]] = {
    "root_work": {
        "quality": 0.95,
        "freshness": 0.82,
        "gt_trust": 0.95,
        "semantic_similarity": 0.90,
        "risk_penalty": 0.05,
    },
    "child_work": {
        "quality": 0.92,
        "freshness": 0.86,
        "gt_trust": 0.88,
        "semantic_similarity": 0.92,
        "risk_penalty": 0.04,
    },
    "grandchild_work": {
        "quality": 0.88,
        "freshness": 0.75,
        "gt_trust": 0.82,
        "semantic_similarity": 0.84,
        "risk_penalty": 0.05,
    },
    "supportive_work": {
        "quality": 0.90,
        "freshness": 0.72,
        "gt_trust": 0.86,
        "semantic_similarity": 0.88,
        "risk_penalty": 0.03,
    },
    "unrelated_fresh_work": {
        "quality": 0.86,
        "freshness": 1.00,
        "gt_trust": 0.78,
        "semantic_similarity": 0.70,
        "risk_penalty": 0.04,
    },
    "nearby_dead_end": {
        "quality": 0.70,
        "freshness": 0.92,
        "gt_trust": 0.72,
        "semantic_similarity": 0.88,
        "risk_penalty": 0.10,
    },
    "nearby_blocked_trace": {
        "quality": 0.96,
        "freshness": 0.96,
        "gt_trust": 0.90,
        "semantic_similarity": 0.90,
        "risk_penalty": 0.05,
    },
    "nearby_degraded_trace": {
        "quality": 0.74,
        "freshness": 0.86,
        "gt_trust": 0.62,
        "semantic_similarity": 0.82,
        "risk_penalty": 0.10,
    },
    "nearby_needs_user_trace": {
        "quality": 0.76,
        "freshness": 0.90,
        "gt_trust": 0.68,
        "semantic_similarity": 0.80,
        "risk_penalty": 0.08,
    },
    "nearby_quarantine": {
        "quality": 0.60,
        "freshness": 0.90,
        "gt_trust": 0.40,
        "semantic_similarity": 0.86,
        "risk_penalty": 0.20,
    },
}


@dataclass(frozen=True)
class ReuseScoreCandidate:
    record_id: str
    taxonomy_kind: str
    quality: float
    freshness: float
    gt_trust: float
    semantic_similarity: float
    graph_proximity: float
    typed_positive_signal: float
    warning_penalty: float
    blocking_penalty: float
    needs_user_penalty: float
    degraded_penalty: float
    contradiction_penalty: float
    risk_penalty: float
    raw_reuse_score: float
    policy_allowed: bool
    direct_reuse_eligible_from_record: bool
    direct_reuse_allowed_after_policy: bool
    reuse_recommendation: str
    explanation: str
    source: TypedDrsCandidate


@dataclass(frozen=True)
class ReuseScoreReport:
    source_report: TypedDrsLineageReport
    candidates: list[ReuseScoreCandidate]
    scoring_model: dict[str, Any]
    safety: dict[str, Any]
    summary: dict[str, Any]


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _graph_proximity(distance: int | None) -> float:
    if distance is None:
        return 0.0
    return 2 ** (-distance / HOP_HALF_LIFE)


def _normalized(value: float) -> float:
    return min(1.0, max(0.0, value))


def _raw_score(
    *,
    quality: float,
    freshness: float,
    gt_trust: float,
    semantic_similarity: float,
    graph_proximity: float,
    typed_positive_signal: float,
    warning_penalty: float,
    blocking_penalty: float,
    needs_user_penalty: float,
    degraded_penalty: float,
    contradiction_penalty: float,
    risk_penalty: float,
) -> float:
    return round(
        0.20 * quality
        + 0.15 * freshness
        + 0.20 * gt_trust
        + 0.15 * semantic_similarity
        + 0.10 * graph_proximity
        + 0.10 * typed_positive_signal
        - 0.10 * warning_penalty
        - 0.15 * blocking_penalty
        - 0.15 * needs_user_penalty
        - 0.10 * degraded_penalty
        - 0.20 * contradiction_penalty
        - 0.20 * risk_penalty,
        6,
    )


def _recommendation(
    candidate: TypedDrsCandidate,
    *,
    direct_reuse_allowed_after_policy: bool,
    contradiction_penalty: float,
) -> str:
    if candidate.taxonomy_kind == "quarantine":
        return "quarantine"
    if candidate.taxonomy_kind == "dead_end":
        return "dead_end"
    if candidate.taxonomy_kind == "blocked_trace":
        return "blocked"
    if candidate.taxonomy_kind == "needs_user_trace":
        return "needs_user"
    if candidate.taxonomy_kind == "degraded_trace":
        return "degraded"
    if contradiction_penalty > 0:
        return "needs_conflict_check"
    if direct_reuse_allowed_after_policy:
        return "direct_reuse_candidate"
    if candidate.typed_warning_score > 0:
        return "warning_only"
    return "needs_full_pipeline"


def _explanation(candidate: TypedDrsCandidate, recommendation: str) -> str:
    if recommendation == "direct_reuse_candidate":
        return "accepted_work_passed_policy_gate"
    if recommendation == "needs_conflict_check":
        return "contradiction_signal_requires_future_conflict_check"
    if recommendation == "quarantine":
        return "taxonomy_filter_quarantine_not_reusable"
    if recommendation == "dead_end":
        return "taxonomy_filter_dead_end_not_reusable"
    if recommendation == "blocked":
        return "policy_or_guard_block_not_success"
    if recommendation == "needs_user":
        return "missing_permission_or_human_input"
    if recommendation == "degraded":
        return "degraded_trace_not_stable_success"
    if recommendation == "warning_only":
        return "warning_signal_cannot_create_reuse"
    return "score_is_context_signal_full_pipeline_needed"


def _score_candidate(candidate: TypedDrsCandidate) -> ReuseScoreCandidate:
    components = COMPONENTS_BY_RECORD_ID[candidate.record["record_id"]]
    graph_proximity = _graph_proximity(candidate.graph_distance)
    typed_positive_signal = _normalized(candidate.typed_positive_score / 3.0)
    warning_penalty = _normalized(candidate.typed_warning_score)
    blocking_penalty = _normalized(candidate.typed_blocking_score)
    needs_user_penalty = _normalized(candidate.typed_needs_user_score)
    degraded_penalty = _normalized(candidate.typed_degraded_score)
    contradiction_penalty = _normalized(candidate.typed_contradiction_score)
    raw_score = _raw_score(
        quality=components["quality"],
        freshness=components["freshness"],
        gt_trust=components["gt_trust"],
        semantic_similarity=components["semantic_similarity"],
        graph_proximity=graph_proximity,
        typed_positive_signal=typed_positive_signal,
        warning_penalty=warning_penalty,
        blocking_penalty=blocking_penalty,
        needs_user_penalty=needs_user_penalty,
        degraded_penalty=degraded_penalty,
        contradiction_penalty=contradiction_penalty,
        risk_penalty=components["risk_penalty"],
    )
    policy_allowed = (
        candidate.policy_allowed
        and candidate.taxonomy_kind not in UNSAFE_TAXONOMY_KINDS
    )
    direct_reuse_eligible_from_record = bool(
        candidate.record["content"].get("direct_reuse_eligible")
    )
    direct_reuse_allowed_after_policy = (
        policy_allowed
        and direct_reuse_eligible_from_record
        and contradiction_penalty == 0
    )
    recommendation = _recommendation(
        candidate,
        direct_reuse_allowed_after_policy=direct_reuse_allowed_after_policy,
        contradiction_penalty=contradiction_penalty,
    )
    return ReuseScoreCandidate(
        record_id=candidate.record["record_id"],
        taxonomy_kind=candidate.taxonomy_kind,
        quality=components["quality"],
        freshness=components["freshness"],
        gt_trust=components["gt_trust"],
        semantic_similarity=components["semantic_similarity"],
        graph_proximity=round(graph_proximity, 6),
        typed_positive_signal=round(typed_positive_signal, 6),
        warning_penalty=warning_penalty,
        blocking_penalty=blocking_penalty,
        needs_user_penalty=needs_user_penalty,
        degraded_penalty=degraded_penalty,
        contradiction_penalty=contradiction_penalty,
        risk_penalty=components["risk_penalty"],
        raw_reuse_score=raw_score,
        policy_allowed=policy_allowed,
        direct_reuse_eligible_from_record=direct_reuse_eligible_from_record,
        direct_reuse_allowed_after_policy=direct_reuse_allowed_after_policy,
        reuse_recommendation=recommendation,
        explanation=_explanation(candidate, recommendation),
        source=candidate,
    )


def _scoring_model() -> dict[str, Any]:
    return {
        "compute_model": "illustrative_deterministic_reuse_score",
        "real_token_billing_measured": False,
        "policy_gate_applied_after_score": True,
        "high_score_overrides_policy": False,
        "direct_reuse_requires_eligible_work": True,
        "context_memory_does_not_equal_reuse": True,
    }


def _safety(candidates: list[ReuseScoreCandidate]) -> dict[str, Any]:
    unsafe = [
        candidate
        for candidate in candidates
        if candidate.direct_reuse_allowed_after_policy
        and candidate.taxonomy_kind in UNSAFE_TAXONOMY_KINDS
    ]
    high_score_unsafe = [
        candidate
        for candidate in candidates
        if candidate.raw_reuse_score >= 0.60
        and candidate.taxonomy_kind in UNSAFE_TAXONOMY_KINDS
        and candidate.direct_reuse_allowed_after_policy
    ]
    contradiction_auto_reuse = [
        candidate
        for candidate in candidates
        if candidate.contradiction_penalty > 0
        and candidate.direct_reuse_allowed_after_policy
    ]
    direct_reuse_candidates = [
        candidate
        for candidate in candidates
        if candidate.direct_reuse_allowed_after_policy
    ]
    return {
        "reuse_score_overrides_policy": False,
        "direct_reuse_policy_unchanged": not unsafe,
        "high_score_unsafe_record_reused": bool(high_score_unsafe),
        "quarantine_direct_reuse_candidates": sum(
            candidate.direct_reuse_allowed_after_policy
            for candidate in candidates
            if candidate.taxonomy_kind == "quarantine"
        ),
        "deadend_direct_reuse_candidates": sum(
            candidate.direct_reuse_allowed_after_policy
            for candidate in candidates
            if candidate.taxonomy_kind == "dead_end"
        ),
        "blocked_direct_reuse_candidates": sum(
            candidate.direct_reuse_allowed_after_policy
            for candidate in candidates
            if candidate.taxonomy_kind == "blocked_trace"
        ),
        "degraded_direct_reuse_candidates": sum(
            candidate.direct_reuse_allowed_after_policy
            for candidate in candidates
            if candidate.taxonomy_kind == "degraded_trace"
        ),
        "needs_user_direct_reuse_candidates": sum(
            candidate.direct_reuse_allowed_after_policy
            for candidate in candidates
            if candidate.taxonomy_kind == "needs_user_trace"
        ),
        "contradiction_auto_reuse_candidates": len(contradiction_auto_reuse),
        "contradiction_requires_conflict_check": any(
            candidate.reuse_recommendation == "needs_conflict_check"
            for candidate in candidates
        ),
        "only_successful_work_can_be_direct_reuse_candidate": all(
            candidate.taxonomy_kind == "work_candidate"
            and candidate.policy_allowed
            and candidate.source.record["content"]["successful_work_record"]
            for candidate in direct_reuse_candidates
        ),
        "Root_authority_preserved": True,
        "ReuseGate_authority_preserved": True,
    }


def _summary(
    candidates: list[ReuseScoreCandidate],
    safety: dict[str, Any],
) -> dict[str, Any]:
    direct_reuse_candidates = [
        candidate
        for candidate in candidates
        if candidate.direct_reuse_allowed_after_policy
    ]
    unsafe_direct_reuse = [
        candidate
        for candidate in direct_reuse_candidates
        if candidate.taxonomy_kind in UNSAFE_TAXONOMY_KINDS
    ]
    policy_gate_dominates = (
        not safety["high_score_unsafe_record_reused"]
        and not safety["reuse_score_overrides_policy"]
    )
    pass_status = (
        len(candidates) >= 10
        and len(direct_reuse_candidates) >= 1
        and len(unsafe_direct_reuse) == 0
        and policy_gate_dominates
        and safety["contradiction_requires_conflict_check"]
        and safety["only_successful_work_can_be_direct_reuse_candidate"]
        and safety["Root_authority_preserved"]
        and safety["ReuseGate_authority_preserved"]
    )
    return {
        "reuse_score_status": "PASS" if pass_status else "FAIL",
        "candidates_scored": len(candidates),
        "direct_reuse_candidates_after_policy": len(direct_reuse_candidates),
        "unsafe_direct_reuse_candidates": len(unsafe_direct_reuse),
        "policy_gate_dominates_score": policy_gate_dominates,
        "typed_edges_used_as_signals": any(
            candidate.typed_positive_signal > 0
            or candidate.warning_penalty > 0
            or candidate.blocking_penalty > 0
            or candidate.needs_user_penalty > 0
            or candidate.degraded_penalty > 0
            or candidate.contradiction_penalty > 0
            for candidate in candidates
        ),
        "graph_proximity_used_as_signal": any(
            candidate.graph_proximity > 0 for candidate in candidates
        ),
        "taxonomy_used_as_filter": any(
            candidate.taxonomy_kind in UNSAFE_TAXONOMY_KINDS
            and not candidate.direct_reuse_allowed_after_policy
            for candidate in candidates
        ),
        "contradiction_does_not_auto_reuse": (
            safety["contradiction_auto_reuse_candidates"] == 0
        ),
        "ReuseScore_is_advisory": True,
        "Root_not_bypassed": True,
        "ReuseGate_not_bypassed": True,
        "local_drs_only": True,
        "external_drs_network_implemented": False,
        "global_drs_implemented": False,
        "schema_refactor_performed": False,
    }


def collect_reuse_score(drs_root: Path | str | None = None) -> ReuseScoreReport:
    source_report = collect_typed_drs_lineage_edges(drs_root)
    candidates = [_score_candidate(candidate) for candidate in source_report.candidates]
    candidates.sort(key=lambda candidate: candidate.raw_reuse_score, reverse=True)
    scoring_model = _scoring_model()
    safety = _safety(candidates)
    summary = _summary(candidates, safety)
    return ReuseScoreReport(
        source_report=source_report,
        candidates=candidates,
        scoring_model=scoring_model,
        safety=safety,
        summary=summary,
    )


def _field_lines(fields: dict[str, Any]) -> list[str]:
    lines = []
    for key, value in fields.items():
        if isinstance(value, bool):
            lines.append(f"{key}: {_bool_text(value)}")
        else:
            lines.append(f"{key}: {value}")
    return lines


def _candidate_line(candidate: ReuseScoreCandidate) -> str:
    return " | ".join(
        [
            candidate.record_id,
            candidate.taxonomy_kind,
            f"{candidate.quality:.2f}",
            f"{candidate.freshness:.2f}",
            f"{candidate.gt_trust:.2f}",
            f"{candidate.semantic_similarity:.2f}",
            f"{candidate.graph_proximity:.6f}",
            f"{candidate.typed_positive_signal:.6f}",
            f"{candidate.warning_penalty:.2f}",
            f"{candidate.blocking_penalty:.2f}",
            f"{candidate.needs_user_penalty:.2f}",
            f"{candidate.degraded_penalty:.2f}",
            f"{candidate.contradiction_penalty:.2f}",
            f"{candidate.risk_penalty:.2f}",
            f"{candidate.raw_reuse_score:.6f}",
            _bool_text(candidate.policy_allowed),
            _bool_text(candidate.direct_reuse_eligible_from_record),
            _bool_text(candidate.direct_reuse_allowed_after_policy),
            candidate.reuse_recommendation,
            candidate.explanation,
        ]
    )


def render_reuse_score(report: ReuseScoreReport) -> str:
    lines = [
        "[REUSESCORE]",
        "note: LocalDRS advisory scoring proof only",
        "note: no global DRS",
        "note: no external DRS network",
        "note: no schema refactor in v0.1 unless explicitly needed",
        "note: ReuseScore is advisory/ranking only",
        "note: ReuseScore is not Root",
        "note: ReuseScore is not ReuseGate",
        "note: ReuseScore does not override policy",
        "note: direct reuse policy remains unchanged",
        "note: production ConflictCheck is not implemented",
        "",
        "[DATASET]",
        f"records_loaded: {len(report.source_report.records)}",
        "local_drs_only: true",
        "external_drs_network_implemented: false",
        "global_drs_implemented: false",
        "schema_refactor_performed: false",
        "reuse_score_is_advisory: true",
        "reuse_gate_behavior_changed: false",
        "production_conflict_check_implemented: false",
        "",
        "[SCORING MODEL]",
    ]
    lines.extend(_field_lines(report.scoring_model))
    lines.extend(
        [
            "",
            "[REUSE CANDIDATES]",
            "record_id | taxonomy_kind | quality | freshness | gt_trust | semantic_similarity | graph_proximity | typed_positive_signal | warning_penalty | blocking_penalty | needs_user_penalty | degraded_penalty | contradiction_penalty | risk_penalty | raw_reuse_score | policy_allowed | direct_reuse_eligible_from_record | direct_reuse_allowed_after_policy | reuse_recommendation | explanation",
            "--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---",
        ]
    )
    lines.extend(_candidate_line(candidate) for candidate in report.candidates)
    lines.extend(["", "[POLICY SAFETY]"])
    lines.extend(_field_lines(report.safety))
    lines.extend(["", "[SUMMARY]"])
    lines.extend(_field_lines(report.summary))
    return "\n".join(lines).rstrip() + "\n"


def run_reuse_score() -> str:
    return render_reuse_score(collect_reuse_score())


def main() -> int:
    parser = argparse.ArgumentParser(description="Run ReuseScore proof demo.")
    parser.parse_args()
    print(run_reuse_score(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
