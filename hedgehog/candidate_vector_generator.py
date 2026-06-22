from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Any, Iterable

from hedgehog.avf import score_candidate_vector as _score_avf_candidate_vector
from hedgehog.candidate_vectors import load_candidate_vectors_from_needles
from hedgehog.local_drs_resolver import ResolvedDRSCandidate, ResolvedDRSReport
from hedgehog.models import CandidateFeatures, CandidateVector
from hedgehog.reuse_gate import compute_freshness_score
from hedgehog.time_model import make_temporal_query


FRESHNESS_BY_STATE = {
    "fresh": 1.0,
    "normal": 1.0,
    "current": 1.0,
    "review_required": 0.65,
    "stale": 0.25,
    "expired": 0.0,
}


@dataclass(frozen=True)
class CandidateVectorInput:
    resolved_candidate_id: str
    source_record_id: str
    domain: str
    subject_key: str | None = None
    claim_key: str | None = None
    content_summary: str = ""
    semantic_tokens: tuple[str, ...] = ()
    time_envelope: dict[str, Any] | None = None
    freshness_state: str = "normal"
    provenance_refs: tuple[dict[str, Any], ...] = ()
    trace_refs: tuple[dict[str, Any], ...] = ()
    source_refs: tuple[dict[str, Any], ...] = ()
    conflict_flags: tuple[str, ...] = ()
    quarantine_deadend_flags: tuple[str, ...] = ()
    poisoning_flags: tuple[str, ...] = ()
    root_review_required: bool = True
    direct_reuse_allowed: bool = False
    schema_valid: bool = False
    reason_codes: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.direct_reuse_allowed:
            raise ValueError("CandidateVectorInput requires direct_reuse_allowed false")

    @classmethod
    def from_resolved_candidate(
        cls,
        candidate: ResolvedDRSCandidate,
        *,
        record: dict[str, Any] | None = None,
        extra_tokens: Iterable[str] = (),
    ) -> "CandidateVectorInput":
        content = (record or {}).get("content") or {}
        time_envelope = (record or {}).get("time_envelope")
        freshness_state = "stale" if candidate.stale else str(
            (time_envelope or {}).get("freshness_class") or "normal"
        )
        conflict_flags = ("conflicting_provenance",) if candidate.conflicting_provenance else ()
        quarantine_deadend_flags: tuple[str, ...] = tuple(
            flag
            for flag, present in (
                ("quarantine", candidate.quarantine_pressure),
                ("deadend", candidate.deadend_pressure),
            )
            if present
        )
        poisoning_flags = ("poisoning_pressure",) if candidate.poisoning_pressure else ()
        semantic_tokens = _dedupe_tokens(
            (
                *candidate.match_reasons,
                *candidate.reason_codes,
                *content.get("semantic_keys", ()),
                content.get("subject_key"),
                content.get("claim_key"),
                content.get("claim_value"),
                content.get("summary"),
                *extra_tokens,
            )
        )
        provenance = (record or {}).get("provenance")
        provenance_refs = (provenance,) if isinstance(provenance, dict) else ()
        return cls(
            resolved_candidate_id=candidate.candidate_id,
            source_record_id=candidate.record_id,
            domain=candidate.domain,
            subject_key=content.get("subject_key"),
            claim_key=content.get("claim_key"),
            content_summary=str(content.get("summary") or ""),
            semantic_tokens=semantic_tokens,
            time_envelope=dict(time_envelope) if isinstance(time_envelope, dict) else None,
            freshness_state=freshness_state,
            provenance_refs=provenance_refs,
            trace_refs=tuple(dict(ref) for ref in (record or {}).get("trace_refs", ())),
            source_refs=tuple(dict(ref) for ref in (record or {}).get("source_refs", ())),
            conflict_flags=conflict_flags,
            quarantine_deadend_flags=quarantine_deadend_flags,
            poisoning_flags=poisoning_flags,
            root_review_required=candidate.review_required,
            direct_reuse_allowed=False,
            schema_valid=bool(content.get("schema_valid")),
            reason_codes=tuple(candidate.reason_codes),
        )


@dataclass(frozen=True)
class GeneratedCandidateVector:
    vector_id: str
    candidate_id: str
    vector: CandidateVector
    source_input: CandidateVectorInput
    vector_features: dict[str, float]
    forbidden_or_masked_features: tuple[str, ...] = ()
    advisory_only: bool = True
    truth_claimed: bool = False
    authority_claimed: bool = False
    action_permission_claimed: bool = False
    direct_reuse_allowed: bool = False


@dataclass(frozen=True)
class CandidateVectorScore:
    vector_id: str
    candidate_id: str
    score: float
    score_components: dict[str, float]
    penalties: dict[str, float]
    hard_blocks: tuple[str, ...]
    review_required: bool
    score_is_authority: bool = False
    direct_reuse_allowed: bool = False
    action_permission_granted: bool = False
    gt_lgt_review_required: bool = True
    root_review_required: bool = True
    reason_codes: tuple[str, ...] = ()


@dataclass(frozen=True)
class CandidateVectorReport:
    candidates: tuple[GeneratedCandidateVector, ...]
    ranked_candidates: tuple[CandidateVectorScore, ...]
    top_candidate_ids: tuple[str, ...]
    review_required_count: int
    blocked_count: int
    direct_reuse_allowed_count: int = 0
    root_review_required: bool = True
    root_final_authority_preserved: bool = True
    counters: dict[str, int] = field(default_factory=dict)
    reason_codes: tuple[str, ...] = ()


def _clamp_01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _safe_id(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_.-]+", "_", value).strip("_") or "candidate"


def _tokens(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, dict):
        items: list[str] = []
        for key, child in value.items():
            items.extend(_tokens(key))
            items.extend(_tokens(child))
        return tuple(items)
    if isinstance(value, (list, tuple, set)):
        items = []
        for item in value:
            items.extend(_tokens(item))
        return tuple(items)
    return tuple(re.findall(r"[a-z0-9_]+", str(value).lower()))


def _dedupe_tokens(values: Iterable[Any]) -> tuple[str, ...]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        for token in _tokens(value):
            if token and token not in seen:
                seen.add(token)
                ordered.append(token)
    return tuple(ordered)


def _freshness_score(candidate_input: CandidateVectorInput) -> float:
    state = candidate_input.freshness_state.lower()
    if state in FRESHNESS_BY_STATE:
        return FRESHNESS_BY_STATE[state]
    if candidate_input.time_envelope:
        record = {"time_envelope": candidate_input.time_envelope}
        return compute_freshness_score(record, make_temporal_query())
    return 0.5


def _score_components(candidate_input: CandidateVectorInput) -> dict[str, float]:
    domain_match_score = 1.0 if candidate_input.domain else 0.0
    subject_claim_match_score = (
        float(bool(candidate_input.subject_key))
        + float(bool(candidate_input.claim_key))
    ) / 2.0
    token_overlap_score = _clamp_01(len(candidate_input.semantic_tokens) / 8.0)
    freshness_score = _freshness_score(candidate_input)
    provenance_quality_score = _clamp_01(
        (
            float(bool(candidate_input.provenance_refs))
            + float(candidate_input.schema_valid)
            + float(bool(candidate_input.content_summary))
        )
        / 3.0
    )
    trace_source_overlap_score = _clamp_01(
        (
            float(bool(candidate_input.trace_refs))
            + float(bool(candidate_input.source_refs))
        )
        / 2.0
    )
    return {
        "domain_match_score": round(domain_match_score, 6),
        "subject_claim_match_score": round(subject_claim_match_score, 6),
        "token_overlap_score": round(token_overlap_score, 6),
        "freshness_score": round(freshness_score, 6),
        "provenance_quality_score": round(provenance_quality_score, 6),
        "trace_source_overlap_score": round(trace_source_overlap_score, 6),
        "root_review_requirement_flag": 1.0 if candidate_input.root_review_required else 0.0,
    }


def _penalties(candidate_input: CandidateVectorInput) -> dict[str, float]:
    stale_penalty = 1.0 if _freshness_score(candidate_input) < 0.5 else 0.0
    return {
        "conflict_penalty": 1.0 if candidate_input.conflict_flags else 0.0,
        "quarantine_deadend_penalty": 1.0
        if candidate_input.quarantine_deadend_flags
        else 0.0,
        "poisoning_pressure_penalty": 1.0 if candidate_input.poisoning_flags else 0.0,
        "stale_penalty": stale_penalty,
    }


def _hard_blocks(candidate_input: CandidateVectorInput) -> tuple[str, ...]:
    penalties = _penalties(candidate_input)
    blocks: list[str] = []
    if penalties["quarantine_deadend_penalty"]:
        blocks.append("quarantine_deadend_direct_reuse_block")
    if penalties["conflict_penalty"]:
        blocks.append("conflicting_provenance_direct_reuse_block")
    if penalties["stale_penalty"]:
        blocks.append("stale_direct_reuse_block")
    if penalties["poisoning_pressure_penalty"]:
        blocks.append("poisoning_pressure_direct_reuse_block")
    return tuple(blocks)


def _candidate_features(candidate_input: CandidateVectorInput) -> CandidateFeatures:
    components = _score_components(candidate_input)
    penalties = _penalties(candidate_input)
    max_penalty = max(penalties.values())
    rel = _clamp_01(
        0.45 * components["domain_match_score"]
        + 0.35 * components["subject_claim_match_score"]
        + 0.20 * components["token_overlap_score"]
    )
    p_success = _clamp_01(
        0.45 * components["freshness_score"]
        + 0.25 * components["provenance_quality_score"]
        + 0.20 * components["trace_source_overlap_score"]
        + 0.10 * (1.0 - max_penalty)
    )
    utility = _clamp_01(0.75 - 0.35 * max_penalty)
    cost = _clamp_01(0.20 + 0.10 * components["root_review_requirement_flag"])
    risk = _clamp_01(max_penalty)
    time_penalty = _clamp_01(1.0 - components["freshness_score"])
    policy_conflict = _clamp_01(
        max(
            penalties["conflict_penalty"],
            penalties["quarantine_deadend_penalty"],
            penalties["poisoning_pressure_penalty"],
        )
    )
    gt_prior = 0.35 if candidate_input.root_review_required else 0.0
    novelty = 0.10
    return CandidateFeatures(
        rel=round(rel, 6),
        p_success=round(p_success, 6),
        utility=round(utility, 6),
        cost=round(cost, 6),
        risk=round(risk, 6),
        time_penalty=round(time_penalty, 6),
        policy_conflict=round(policy_conflict, 6),
        gt_prior=round(gt_prior, 6),
        novelty=round(novelty, 6),
    )


def generate_candidate_vectors(
    candidate_inputs: Iterable[CandidateVectorInput],
) -> tuple[GeneratedCandidateVector, ...]:
    generated: list[GeneratedCandidateVector] = []
    for candidate_input in candidate_inputs:
        features = _candidate_features(candidate_input)
        blocks = _hard_blocks(candidate_input)
        vector_id = f"vector_{_safe_id(candidate_input.source_record_id)}"
        vector = CandidateVector(
            vector_id=vector_id,
            source="local_drs",
            domain=candidate_input.domain,
            branching_hint="forbidden" if blocks else "hybrid",
            features=features,
            description=candidate_input.content_summary or None,
            history_confidence="normal",
            requires_architect_creativity=False,
            hard_forbidden=bool(blocks),
            forbidden_reason=";".join(blocks) if blocks else None,
            source_record_ref=candidate_input.source_record_id,
        )
        generated.append(
            GeneratedCandidateVector(
                vector_id=vector_id,
                candidate_id=candidate_input.resolved_candidate_id,
                vector=vector,
                source_input=candidate_input,
                vector_features=features.to_dict(),
                forbidden_or_masked_features=blocks,
                advisory_only=True,
                truth_claimed=False,
                authority_claimed=False,
                action_permission_claimed=False,
                direct_reuse_allowed=False,
            )
        )
    return tuple(generated)


def score_candidate_vector(
    candidate: GeneratedCandidateVector,
) -> CandidateVectorScore:
    avf_score = _score_avf_candidate_vector(candidate.vector)
    components = _score_components(candidate.source_input)
    penalties = _penalties(candidate.source_input)
    hard_blocks = candidate.forbidden_or_masked_features
    score = round(float(avf_score["final_viability"]), 6)
    reasons = [
        *candidate.source_input.reason_codes,
        "drs_candidate_vector_generated",
        "avf_score_is_advisory",
        "ranking_not_authority",
        "gt_lgt_root_review_required",
    ]
    if components["domain_match_score"] == 1.0:
        reasons.append("exact_domain_match")
    if components["subject_claim_match_score"] > 0.0:
        reasons.append("subject_claim_match_score_applied")
    if hard_blocks:
        reasons.extend(hard_blocks)
        reasons.append("hard_block_applied")
    if penalties["conflict_penalty"]:
        reasons.append("conflicting_provenance_penalty")
    if penalties["poisoning_pressure_penalty"]:
        reasons.append("duplicate_spam_pressure_detected")
        reasons.append("duplicate_count_not_authority")
    if score >= 0.75:
        reasons.append("high_score_review_required")
    if candidate.source_input.schema_valid:
        reasons.append("schema_validity_shape_only")
        reasons.append("schema_valid_vector_is_not_semantic_truth")
    reasons.append("root_final_authority_preserved_across_avf_scoring")
    return CandidateVectorScore(
        vector_id=candidate.vector_id,
        candidate_id=candidate.candidate_id,
        score=score,
        score_components={
            **components,
            "avf_viability_score": round(float(avf_score["viability_score"]), 6),
            "avf_final_viability": score,
            "avf_soft_mask": round(float(avf_score["soft_mask"]), 6),
        },
        penalties=penalties,
        hard_blocks=hard_blocks,
        review_required=True,
        score_is_authority=False,
        direct_reuse_allowed=False,
        action_permission_granted=False,
        gt_lgt_review_required=True,
        root_review_required=True,
        reason_codes=tuple(dict.fromkeys(reasons)),
    )


def rank_candidate_vectors(
    candidates: Iterable[GeneratedCandidateVector],
) -> tuple[CandidateVectorScore, ...]:
    scores = [score_candidate_vector(candidate) for candidate in candidates]
    return tuple(
        sorted(
            scores,
            key=lambda item: (
                -item.score,
                len(item.hard_blocks),
                item.vector_id,
            ),
        )
    )


def _report_counters(
    inputs: tuple[CandidateVectorInput, ...],
    candidates: tuple[GeneratedCandidateVector, ...],
    ranked: tuple[CandidateVectorScore, ...],
    top_n: int,
) -> dict[str, int]:
    top = ranked[:top_n] if top_n > 0 else ()
    return {
        "drs_candidates_input_count": len(inputs),
        "candidate_vectors_generated_count": len(candidates),
        "avf_scores_computed_count": len(ranked),
        "ranked_candidates_count": len(ranked),
        "top_ranked_candidates_count": len(top),
        "direct_reuse_allowed_count": 0,
        "action_permission_granted_count": 0,
        "avf_authority_claimed_count": 0,
        "vector_truth_claimed_count": 0,
        "schema_validity_truth_claimed_count": 0,
        "stale_candidate_review_required_count": sum(
            1 for item in inputs if _freshness_score(item) < 0.5
        ),
        "quarantine_deadend_blocked_count": sum(
            1 for item in inputs if item.quarantine_deadend_flags
        ),
        "conflicting_provenance_penalized_count": sum(
            1 for item in inputs if item.conflict_flags
        ),
        "duplicate_spam_candidates_seen_count": sum(
            1 for item in inputs if item.poisoning_flags
        ),
        "duplicate_spam_authority_claimed_count": 0,
        "high_score_direct_reuse_granted_count": 0,
        "gt_lgt_review_required_count": sum(
            1 for item in ranked if item.gt_lgt_review_required
        ),
        "root_review_required_count": sum(1 for item in ranked if item.root_review_required),
        "manifest_mutation_count": 0,
        "transition_matrix_mutation_count": 0,
        "network_used_count": 0,
        "gemini_used_count": 0,
        "root_final_authority_preserved_count": 1,
    }


def build_avf_candidate_report(
    candidate_inputs: Iterable[CandidateVectorInput],
    *,
    top_n: int = 1,
    declared_vector_paths: Iterable[Any] | None = None,
) -> CandidateVectorReport:
    # Optional composition point for the existing needle vector loader. The
    # loaded vectors are intentionally not merged into DRS-derived vectors in
    # v0.1; the report proves the local DRS adapter boundary.
    if declared_vector_paths:
        load_candidate_vectors_from_needles(declared_vector_paths)

    inputs = tuple(candidate_inputs)
    candidates = generate_candidate_vectors(inputs)
    ranked = rank_candidate_vectors(candidates)
    top = ranked[:top_n] if top_n > 0 else ()
    counters = _report_counters(inputs, candidates, ranked, top_n)
    reason_codes = tuple(
        dict.fromkeys(
            reason
            for score in ranked
            for reason in score.reason_codes
        )
    )
    return CandidateVectorReport(
        candidates=candidates,
        ranked_candidates=ranked,
        top_candidate_ids=tuple(score.candidate_id for score in top),
        review_required_count=counters["root_review_required_count"],
        blocked_count=sum(1 for score in ranked if score.hard_blocks),
        direct_reuse_allowed_count=0,
        root_review_required=True,
        root_final_authority_preserved=True,
        counters=counters,
        reason_codes=reason_codes,
    )


def candidate_inputs_from_resolved_report(
    report: ResolvedDRSReport,
    *,
    records_by_id: dict[str, dict[str, Any]] | None = None,
    extra_tokens: Iterable[str] = (),
) -> tuple[CandidateVectorInput, ...]:
    records = records_by_id or {}
    return tuple(
        CandidateVectorInput.from_resolved_candidate(
            candidate,
            record=records.get(candidate.record_id),
            extra_tokens=extra_tokens,
        )
        for candidate in report.candidates
    )
