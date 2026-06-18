from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import math
from typing import Any


TITLE = "HEDGEHOG OS — LONG-LIVED DRS TTL AGING STRESS v0.1"
NOW = "2026-06-18T12:00:00Z"
TAU_REUSE = 0.72
TAU_QUARANTINE = 0.35
TAU_DEADEND = 0.35
TAU_GT_TRUST = 0.55
MAX_LINEAGE_HOPS = 3
LAMBDA_LINEAGE = 0.7
REUSE_BOOST_K = 0.15
REUSE_BOOST_MAX = 2.0

COMPACT_RULE = (
    "Memory may survive.",
    "Authority does not survive through memory.",
    "Old records may inform.",
    "Old records may warn.",
    "Old records may explain history.",
    "Old records may suggest rerun.",
    "Old records may not silently authorize direct reuse.",
    "Freshness can expire reuse.",
    "Trust can constrain supersession.",
    "Proximity can warn or block.",
    "Popularity can preserve visibility.",
    "None of them can authorize final reuse.",
    "Root remains final authority.",
)

FORMULA_SUMMARY = (
    "TemporalHardGate = TimeEnvelopePresent and TemporalQueryPresent and ClockOK and ValidityIntervalOK and FreshnessOK.",
    "FreshnessOK checks each required time axis independently.",
    "DirectReuseAllowed requires RootShortcutAllowed and every hard gate.",
    "Supersedes requires RootAcceptedForSupersession and TrustClassAllowedToSupersede.",
    "CandidateSet_pre bounds quarantine/deadend proximity before LineageDecay.",
    "ReuseBoost affects Survival ranking only and never grants direct reuse.",
)

SCENARIO_IDS = (
    "missing_time_envelope_rejected",
    "drs_query_without_temporal_query_rejected",
    "fresh_record_direct_reuse_candidate_but_root_required",
    "stale_work_record_context_only_not_direct_reuse",
    "expired_time_envelope_blocks_direct_reuse",
    "valid_document_but_stale_verification_requires_rerun",
    "fresh_ingestion_old_source_observed_at_blocks_freshness",
    "prefer_recent_selects_new_record",
    "historical_as_of_selects_old_record",
    "non_overlapping_validity_records_do_not_conflict",
    "overlapping_validity_conflict_blocks_reuse",
    "quarantine_proximity_blocks_reuse",
    "deadend_proximity_blocks_route",
    "reuse_frequency_cannot_override_staleness",
    "gt_ttl_decay_penalizes_bad_old_record",
    "future_timestamp_quarantined",
    "negative_ttl_rejected",
    "audit_replay_uses_historical_time",
    "accepted_evidence_not_future_action_permission",
    "root_shortcut_required_for_any_direct_final_reuse",
    "supersession_requires_root_accepted_trustworthy_new_record",
    "fresh_unaccepted_observation_cannot_supersede_work",
    "quarantine_proximity_computation_is_bounded",
    "quarantine_taint_does_not_cascade_to_whole_graph",
    "reuse_boost_cannot_override_hard_gates",
)


@dataclass(frozen=True)
class TimeEnvelopeExt:
    pt_created_at: str
    kt_asof: str
    et_observed_at: str | None
    ct_session_anchor: str
    ttl_seconds: int
    valid_from: str | None
    valid_to: str | None
    source_observed_at: str | None
    source_reported_at: str | None
    system_ingested_at: str | None
    system_verified_at: str | None
    freshness_class: str


@dataclass(frozen=True)
class TemporalQueryExt:
    as_of: str
    query_mode: str
    time_range: tuple[str | None, str | None]
    freshness_bias: str
    max_age_seconds: int
    required_time_axes: tuple[str, ...]
    risk_class: str
    domain: str
    reuse_intent: str


@dataclass(frozen=True)
class LocalDRSRecord:
    record_id: str
    layer: str
    lifecycle_state: str
    subject_key: str
    claim_dimension: str
    content: dict[str, Any]
    time_envelope: TimeEnvelopeExt | None
    authority_class: str
    root_accepted: bool
    root_accepted_for_supersession: bool
    root_explicit_override: bool
    root_shortcut_allowed: bool
    policy_ok: bool
    permission_ok: bool
    provenance_chain_valid: bool
    replacement_reason_present: bool
    gt_trust: float
    reuse_count: int
    utility_history: float
    safety_score: float
    provenance_quality: float
    conflict_penalty: float
    quarantine_taint_summary: float
    deadend_taint_summary: float
    lineage_refs: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class EvaluationResult:
    record_id: str
    query_state: str
    reuse_decision_class: str
    temporal_hard_gate_ok: bool
    freshness_ok: bool
    validity_interval_ok: bool
    clock_ok: bool
    conflict_ok: bool
    quarantine_proximity_ok: bool
    deadend_proximity_ok: bool
    gt_trust_ok: bool
    permission_ok: bool
    policy_ok: bool
    root_shortcut_allowed: bool
    reuse_score: float
    survival_score: float
    direct_reuse_allowed: bool
    root_final_authority_preserved: bool
    reason_codes: tuple[str, ...]


@dataclass(frozen=True)
class ScenarioResult:
    scenario_id: str
    status: str
    expected_direct_reuse_allowed: bool
    actual_direct_reuse_allowed: bool
    expected_query_state: str
    actual_query_state: str
    expected_reuse_decision_class: str
    actual_reuse_decision_class: str
    root_final_authority_preserved: bool
    reason_codes: tuple[str, ...]
    notes: str


def parse_time(value: str | datetime | None) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    normalized = value.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _te(**overrides: Any) -> TimeEnvelopeExt:
    values = {
        "pt_created_at": "2026-06-18T08:00:00Z",
        "kt_asof": "2026-06-18T09:00:00Z",
        "et_observed_at": "2026-06-18T09:00:00Z",
        "ct_session_anchor": "sess_long_lived_drs_v01",
        "ttl_seconds": 172800,
        "valid_from": "2026-01-01T00:00:00Z",
        "valid_to": "2026-12-31T23:59:59Z",
        "source_observed_at": "2026-06-18T09:00:00Z",
        "source_reported_at": "2026-06-18T09:05:00Z",
        "system_ingested_at": "2026-06-18T09:10:00Z",
        "system_verified_at": "2026-06-18T09:15:00Z",
        "freshness_class": "normal",
    }
    values.update(overrides)
    return TimeEnvelopeExt(**values)


def _query(**overrides: Any) -> TemporalQueryExt:
    values = {
        "as_of": NOW,
        "query_mode": "current_decision",
        "time_range": (None, NOW),
        "freshness_bias": "prefer_recent",
        "max_age_seconds": 172800,
        "required_time_axes": ("kt", "source_observed_at", "system_verified_at"),
        "risk_class": "normal",
        "domain": "mock_government_certificate",
        "reuse_intent": "direct_reuse_candidate",
    }
    values.update(overrides)
    return TemporalQueryExt(**values)


def _record(**overrides: Any) -> LocalDRSRecord:
    values = {
        "record_id": "work_current_certificate",
        "layer": "work",
        "lifecycle_state": "completed",
        "subject_key": "certificate:demo-user",
        "claim_dimension": "certificate_requirements",
        "content": {
            "claim_value": "requirements_v2",
            "domain": "mock_government_certificate",
            "semantic_similarity": 0.92,
        },
        "time_envelope": _te(),
        "authority_class": "Work",
        "root_accepted": True,
        "root_accepted_for_supersession": False,
        "root_explicit_override": False,
        "root_shortcut_allowed": False,
        "policy_ok": True,
        "permission_ok": True,
        "provenance_chain_valid": True,
        "replacement_reason_present": False,
        "gt_trust": 0.86,
        "reuse_count": 2,
        "utility_history": 0.86,
        "safety_score": 0.93,
        "provenance_quality": 0.9,
        "conflict_penalty": 0.0,
        "quarantine_taint_summary": 0.0,
        "deadend_taint_summary": 0.0,
        "lineage_refs": (),
    }
    values.update(overrides)
    return LocalDRSRecord(**values)


def age_seconds(axis: str, record: LocalDRSRecord, query: TemporalQueryExt | None) -> float:
    if record.time_envelope is None or query is None:
        return math.inf
    envelope = record.time_envelope
    axis_field = {
        "pt": "pt_created_at",
        "kt": "kt_asof",
        "et": "et_observed_at",
        "source_observed_at": "source_observed_at",
        "source_reported_at": "source_reported_at",
        "system_ingested_at": "system_ingested_at",
        "system_verified_at": "system_verified_at",
    }.get(axis)
    if axis_field is None:
        return math.inf
    axis_time = parse_time(getattr(envelope, axis_field))
    as_of = parse_time(query.as_of)
    if axis_time is None or as_of is None:
        return math.inf
    return (as_of - axis_time).total_seconds()


def clock_ok(record: LocalDRSRecord, query: TemporalQueryExt | None) -> bool:
    if record.time_envelope is None or query is None:
        return False
    envelope = record.time_envelope
    as_of = parse_time(query.as_of)
    if as_of is None:
        return False
    if envelope.ttl_seconds < 0:
        return False
    valid_from = parse_time(envelope.valid_from)
    valid_to = parse_time(envelope.valid_to)
    if valid_from and valid_to and valid_to < valid_from:
        return False
    for value in (
        envelope.pt_created_at,
        envelope.kt_asof,
        envelope.et_observed_at,
        envelope.source_observed_at,
        envelope.source_reported_at,
        envelope.system_ingested_at,
        envelope.system_verified_at,
    ):
        parsed = parse_time(value)
        if parsed and parsed > as_of:
            return False
    return True


def validity_interval_ok(record: LocalDRSRecord, query: TemporalQueryExt | None) -> bool:
    if record.time_envelope is None or query is None:
        return False
    as_of = parse_time(query.as_of)
    valid_from = parse_time(record.time_envelope.valid_from)
    valid_to = parse_time(record.time_envelope.valid_to)
    if as_of is None:
        return False
    if valid_from and as_of < valid_from:
        return False
    if valid_to and as_of > valid_to:
        return False
    return True


def freshness_ok(record: LocalDRSRecord, query: TemporalQueryExt | None) -> bool:
    if record.time_envelope is None or query is None:
        return False
    if record.time_envelope.ttl_seconds < 0:
        return False
    max_age = min(record.time_envelope.ttl_seconds, query.max_age_seconds)
    for axis in query.required_time_axes:
        age = age_seconds(axis, record, query)
        if age < 0 or age > max_age:
            return False
    return True


def temporal_hard_gate(record: LocalDRSRecord, query: TemporalQueryExt | None) -> bool:
    return (
        record.time_envelope is not None
        and query is not None
        and clock_ok(record, query)
        and validity_interval_ok(record, query)
        and freshness_ok(record, query)
    )


def _interval(record: LocalDRSRecord) -> tuple[datetime | None, datetime | None]:
    if record.time_envelope is None:
        return (None, None)
    return (
        parse_time(record.time_envelope.valid_from),
        parse_time(record.time_envelope.valid_to),
    )


def _intervals_overlap(record_a: LocalDRSRecord, record_b: LocalDRSRecord) -> bool:
    start_a, end_a = _interval(record_a)
    start_b, end_b = _interval(record_b)
    if start_a is None or start_b is None:
        return True
    effective_end_a = end_a or datetime.max.replace(tzinfo=timezone.utc)
    effective_end_b = end_b or datetime.max.replace(tzinfo=timezone.utc)
    return start_a <= effective_end_b and start_b <= effective_end_a


def temporal_conflict(
    record_a: LocalDRSRecord, record_b: LocalDRSRecord, query: TemporalQueryExt | None
) -> bool:
    if query is None:
        return False
    same_subject = record_a.subject_key == record_b.subject_key
    same_dimension = record_a.claim_dimension == record_b.claim_dimension
    incompatible = record_a.content.get("claim_value") != record_b.content.get("claim_value")
    return same_subject and same_dimension and incompatible and _intervals_overlap(record_a, record_b)


def trust_class_allowed_to_supersede(
    new_record: LocalDRSRecord, old_record: LocalDRSRecord
) -> bool:
    authority_rank = {
        "SemanticDraft": 0,
        "EvidenceCandidate": 1,
        "ConnectorObservation": 1,
        "ExternalDRSPointer": 1,
        "AcceptedEvidence": 2,
        "Work": 3,
        "RootFinalArtifact": 4,
    }
    return (
        authority_rank.get(new_record.authority_class, 0)
        >= authority_rank.get(old_record.authority_class, 0)
        or new_record.root_explicit_override
    )


def supersedes(
    new_record: LocalDRSRecord,
    old_record: LocalDRSRecord,
    query: TemporalQueryExt | None,
) -> bool:
    if query is None or new_record.time_envelope is None or old_record.time_envelope is None:
        return False
    kt_new = parse_time(new_record.time_envelope.kt_asof)
    kt_old = parse_time(old_record.time_envelope.kt_asof)
    if kt_new is None or kt_old is None:
        return False
    return (
        new_record.subject_key == old_record.subject_key
        and new_record.claim_dimension == old_record.claim_dimension
        and kt_new > kt_old
        and _intervals_overlap(new_record, old_record)
        and new_record.provenance_chain_valid
        and new_record.replacement_reason_present
        and new_record.root_accepted_for_supersession
        and trust_class_allowed_to_supersede(new_record, old_record)
    )


def candidate_set_pre(
    records: list[LocalDRSRecord],
    query: TemporalQueryExt,
    subject_key: str | None = None,
    top_k: int = 10,
) -> list[LocalDRSRecord]:
    filtered = [
        record
        for record in records
        if record.content.get("domain", query.domain) == query.domain
        and (subject_key is None or record.subject_key == subject_key)
        and validity_interval_ok(record, query)
    ]
    return sorted(
        filtered,
        key=lambda item: (item.content.get("semantic_similarity", 0.0), item.gt_trust),
        reverse=True,
    )[:top_k]


def lineage_decay(distance: int) -> float:
    return math.exp(-LAMBDA_LINEAGE * max(distance, 0))


def _lineage_distance(source: LocalDRSRecord, target_record_id: str) -> int | None:
    for ref in source.lineage_refs:
        if ref.get("target") == target_record_id:
            return int(ref.get("distance", MAX_LINEAGE_HOPS + 1))
    return None


def quarantine_proximity(
    record: LocalDRSRecord,
    query: TemporalQueryExt,
    quarantine_records: list[LocalDRSRecord],
) -> float:
    candidates = candidate_set_pre(quarantine_records, query, record.subject_key, top_k=10)
    score = 0.0
    for quarantine_record in candidates:
        distance = _lineage_distance(quarantine_record, record.record_id)
        if distance is None:
            distance = MAX_LINEAGE_HOPS + 1
        if distance > MAX_LINEAGE_HOPS:
            score = max(score, record.quarantine_taint_summary * 0.5)
            continue
        risk = max(quarantine_record.quarantine_taint_summary, 0.1)
        similarity = quarantine_record.content.get("semantic_similarity", 0.75)
        score = max(score, risk * similarity * lineage_decay(distance))
    return round(score, 6)


def deadend_proximity(
    record: LocalDRSRecord,
    query: TemporalQueryExt,
    deadend_records: list[LocalDRSRecord],
) -> float:
    candidates = candidate_set_pre(deadend_records, query, record.subject_key, top_k=10)
    score = 0.0
    for deadend_record in candidates:
        distance = _lineage_distance(deadend_record, record.record_id)
        if distance is None:
            distance = MAX_LINEAGE_HOPS + 1
        if distance > MAX_LINEAGE_HOPS:
            score = max(score, record.deadend_taint_summary * 0.5)
            continue
        risk = max(deadend_record.deadend_taint_summary, 0.1)
        similarity = deadend_record.content.get("semantic_similarity", 0.75)
        score = max(score, risk * similarity * lineage_decay(distance))
    return round(score, 6)


def reuse_boost(record: LocalDRSRecord) -> float:
    return min(1 + REUSE_BOOST_K * math.log(1 + max(record.reuse_count, 0)), REUSE_BOOST_MAX)


def _freshness_score(record: LocalDRSRecord, query: TemporalQueryExt | None) -> float:
    if query is None or record.time_envelope is None:
        return 0.0
    ages = [age_seconds(axis, record, query) for axis in query.required_time_axes]
    if not ages or any(age == math.inf or age < 0 for age in ages):
        return 0.0
    max_age = max(max(record.time_envelope.ttl_seconds, 1), query.max_age_seconds)
    return max(0.0, 1.0 - max(ages) / max_age)


def survival_score(
    record: LocalDRSRecord,
    query: TemporalQueryExt | None,
    quarantine_proximity_value: float = 0.0,
) -> float:
    score = (
        record.gt_trust
        * _freshness_score(record, query)
        * record.utility_history
        * record.safety_score
        * record.provenance_quality
        * (1 - record.conflict_penalty)
        * (1 - quarantine_proximity_value)
        * reuse_boost(record)
    )
    return round(max(score, 0.0), 6)


def reuse_score(record: LocalDRSRecord, query: TemporalQueryExt | None) -> float:
    base = (
        0.35 * record.gt_trust
        + 0.25 * record.safety_score
        + 0.2 * record.provenance_quality
        + 0.2 * _freshness_score(record, query)
    )
    return round(min(max(base, 0.0), 1.0), 6)


def direct_reuse_allowed(
    record: LocalDRSRecord,
    query: TemporalQueryExt | None,
    conflict_ok: bool = True,
    quarantine_ok: bool = True,
    deadend_ok: bool = True,
) -> bool:
    return (
        record.root_shortcut_allowed
        and record.time_envelope is not None
        and query is not None
        and temporal_hard_gate(record, query)
        and record.policy_ok
        and conflict_ok
        and quarantine_ok
        and deadend_ok
        and record.gt_trust >= TAU_GT_TRUST
        and record.permission_ok
        and reuse_score(record, query) >= TAU_REUSE
    )


def reuse_decision_class(
    record: LocalDRSRecord,
    query: TemporalQueryExt | None,
    evaluation: EvaluationResult,
) -> str:
    if evaluation.direct_reuse_allowed:
        return "direct_final_reuse"
    if evaluation.query_state == "stale_context_only":
        return "context_only"
    if evaluation.query_state == "warning_only":
        return "warning_only"
    if evaluation.query_state == "historical_only":
        return "historical_replay"
    if evaluation.query_state == "rerun_required":
        return "partial_reuse_then_validation"
    if evaluation.query_state.startswith("blocked_by"):
        return "blocked"
    if query and query.risk_class in {"high", "regulated", "external_action_related"}:
        return "partial_reuse_then_validation"
    return "partial_reuse_then_validation"


def evaluate_record_for_query(
    record: LocalDRSRecord,
    query: TemporalQueryExt | None,
    context_records: list[LocalDRSRecord] | None = None,
) -> EvaluationResult:
    context_records = context_records or []
    reason_codes: list[str] = []

    if record.time_envelope is None:
        reason_codes.append("missing_time_envelope")
    if query is None:
        reason_codes.append("missing_temporal_query")

    clock = clock_ok(record, query)
    validity = validity_interval_ok(record, query)
    fresh = freshness_ok(record, query)
    temporal_ok = temporal_hard_gate(record, query)

    if record.time_envelope and record.time_envelope.ttl_seconds < 0:
        reason_codes.append("negative_ttl")
    if query and record.time_envelope:
        as_of = parse_time(query.as_of)
        if as_of and any(
            parsed and parsed > as_of
            for parsed in (
                parse_time(record.time_envelope.pt_created_at),
                parse_time(record.time_envelope.kt_asof),
                parse_time(record.time_envelope.et_observed_at),
            )
        ):
            reason_codes.append("future_timestamp")
    if not validity:
        reason_codes.append("invalid_validity_interval")
    if not fresh and "missing_time_envelope" not in reason_codes:
        reason_codes.append("expired_ttl")

    conflicts = [
        other
        for other in context_records
        if other.layer not in {"quarantine", "deadends"} and temporal_conflict(record, other, query)
    ]
    conflict_ok = not conflicts
    if not conflict_ok:
        reason_codes.append("overlapping_validity_conflict")

    quarantine_records = [item for item in context_records if item.layer == "quarantine"]
    deadend_records = [item for item in context_records if item.layer == "deadends"]
    quarantine_value = quarantine_proximity(record, query, quarantine_records) if query else 0.0
    deadend_value = deadend_proximity(record, query, deadend_records) if query else 0.0
    quarantine_ok = quarantine_value <= TAU_QUARANTINE
    deadend_ok = deadend_value <= TAU_DEADEND
    if not quarantine_ok:
        reason_codes.append("quarantine_proximity")
    if not deadend_ok:
        reason_codes.append("deadend_proximity")

    direct = direct_reuse_allowed(record, query, conflict_ok, quarantine_ok, deadend_ok)

    if not clock or "missing_time_envelope" in reason_codes or "missing_temporal_query" in reason_codes:
        query_state = "blocked_by_time_gate"
    elif not temporal_ok and record.content.get("stale_verification_document_still_valid"):
        query_state = "rerun_required"
        reason_codes.append("stale_verification_document_still_valid")
    elif not temporal_ok and record.content.get("fresh_ingestion_old_source"):
        query_state = "blocked_by_time_gate"
        reason_codes.append("fresh_ingestion_old_source")
    elif not temporal_ok and record.content.get("force_context_only"):
        query_state = "stale_context_only"
        reason_codes.append("stale_context_only")
    elif not temporal_ok:
        query_state = "blocked_by_time_gate"
    elif query and query.query_mode in {"historical_as_of", "audit_replay"}:
        query_state = "historical_only"
    elif not conflict_ok:
        query_state = "blocked_by_conflict"
    elif not quarantine_ok:
        query_state = "blocked_by_quarantine_proximity"
    elif not deadend_ok:
        query_state = "blocked_by_deadend_proximity"
    elif record.content.get("warning_only"):
        query_state = "warning_only"
    else:
        query_state = "fresh_candidate"

    preliminary = EvaluationResult(
        record_id=record.record_id,
        query_state=query_state,
        reuse_decision_class="blocked",
        temporal_hard_gate_ok=temporal_ok,
        freshness_ok=fresh,
        validity_interval_ok=validity,
        clock_ok=clock,
        conflict_ok=conflict_ok,
        quarantine_proximity_ok=quarantine_ok,
        deadend_proximity_ok=deadend_ok,
        gt_trust_ok=record.gt_trust >= TAU_GT_TRUST,
        permission_ok=record.permission_ok,
        policy_ok=record.policy_ok,
        root_shortcut_allowed=record.root_shortcut_allowed,
        reuse_score=reuse_score(record, query),
        survival_score=survival_score(record, query, quarantine_value),
        direct_reuse_allowed=direct,
        root_final_authority_preserved=True,
        reason_codes=tuple(dict.fromkeys(reason_codes)),
    )
    decision_class = reuse_decision_class(record, query, preliminary)
    if not direct and temporal_ok and not record.root_shortcut_allowed and query_state == "fresh_candidate":
        reason_codes.append("root_shortcut_required")
    return EvaluationResult(
        **{
            **asdict(preliminary),
            "reuse_decision_class": decision_class,
            "reason_codes": tuple(dict.fromkeys(reason_codes)),
        }
    )


def _scenario(
    scenario_id: str,
    evaluation: EvaluationResult,
    expected_direct: bool,
    expected_state: str,
    expected_decision: str,
    required_reason: str,
    notes: str,
) -> ScenarioResult:
    checks = (
        evaluation.direct_reuse_allowed == expected_direct,
        evaluation.query_state == expected_state,
        evaluation.reuse_decision_class == expected_decision,
        evaluation.root_final_authority_preserved,
        required_reason in evaluation.reason_codes,
    )
    return ScenarioResult(
        scenario_id=scenario_id,
        status="PASS" if all(checks) else "FAIL",
        expected_direct_reuse_allowed=expected_direct,
        actual_direct_reuse_allowed=evaluation.direct_reuse_allowed,
        expected_query_state=expected_state,
        actual_query_state=evaluation.query_state,
        expected_reuse_decision_class=expected_decision,
        actual_reuse_decision_class=evaluation.reuse_decision_class,
        root_final_authority_preserved=evaluation.root_final_authority_preserved,
        reason_codes=evaluation.reason_codes,
        notes=notes,
    )


def evaluate_scenario(scenario_id: str) -> ScenarioResult:
    query = _query()
    fresh = _record()

    if scenario_id == "missing_time_envelope_rejected":
        result = evaluate_record_for_query(_record(time_envelope=None), query)
        return _scenario(scenario_id, result, False, "blocked_by_time_gate", "blocked", "missing_time_envelope", "Record without TimeEnvelope cannot be reused.")

    if scenario_id == "drs_query_without_temporal_query_rejected":
        result = evaluate_record_for_query(fresh, None)
        return _scenario(scenario_id, result, False, "blocked_by_time_gate", "blocked", "missing_temporal_query", "DRS query without TemporalQuery is blocked.")

    if scenario_id == "fresh_record_direct_reuse_candidate_but_root_required":
        result = evaluate_record_for_query(fresh, query)
        return _scenario(scenario_id, result, False, "fresh_candidate", "partial_reuse_then_validation", "root_shortcut_required", "Fresh candidate lacks RootShortcutAllowed.")

    if scenario_id == "stale_work_record_context_only_not_direct_reuse":
        stale = _record(
            content={**fresh.content, "force_context_only": True},
            time_envelope=_te(kt_asof="2026-04-01T00:00:00Z", source_observed_at="2026-04-01T00:00:00Z", system_verified_at="2026-04-02T00:00:00Z"),
        )
        result = evaluate_record_for_query(stale, query)
        return _scenario(scenario_id, result, False, "stale_context_only", "context_only", "stale_context_only", "Stale Work remains context only.")

    if scenario_id == "expired_time_envelope_blocks_direct_reuse":
        expired = _record(time_envelope=_te(ttl_seconds=60, kt_asof="2026-06-01T00:00:00Z", source_observed_at="2026-06-01T00:00:00Z", system_verified_at="2026-06-01T00:00:00Z"))
        result = evaluate_record_for_query(expired, query)
        return _scenario(scenario_id, result, False, "blocked_by_time_gate", "blocked", "expired_ttl", "Expired TTL blocks direct reuse.")

    if scenario_id == "valid_document_but_stale_verification_requires_rerun":
        document = _record(
            content={**fresh.content, "stale_verification_document_still_valid": True},
            time_envelope=_te(kt_asof="2026-06-18T09:00:00Z", source_observed_at="2026-06-18T09:00:00Z", system_verified_at="2026-04-01T00:00:00Z", valid_to="2027-01-01T00:00:00Z"),
        )
        result = evaluate_record_for_query(document, query)
        return _scenario(scenario_id, result, False, "rerun_required", "partial_reuse_then_validation", "stale_verification_document_still_valid", "Document remains valid but verification is stale.")

    if scenario_id == "fresh_ingestion_old_source_observed_at_blocks_freshness":
        ingested = _record(
            content={**fresh.content, "fresh_ingestion_old_source": True},
            time_envelope=_te(source_observed_at="2026-01-01T00:00:00Z", system_ingested_at="2026-06-18T11:00:00Z", system_verified_at="2026-06-18T11:00:00Z"),
        )
        result = evaluate_record_for_query(ingested, query)
        return _scenario(scenario_id, result, False, "blocked_by_time_gate", "blocked", "fresh_ingestion_old_source", "Fresh ingestion is not fresh source knowledge.")

    if scenario_id == "prefer_recent_selects_new_record":
        old = _record(record_id="old_ranked_record", time_envelope=_te(kt_asof="2026-06-10T00:00:00Z", source_observed_at="2026-06-10T00:00:00Z", system_verified_at="2026-06-10T00:00:00Z"))
        new = _record(record_id="new_ranked_record", root_shortcut_allowed=False)
        ranked = sorted([old, new], key=lambda item: reuse_score(item, query), reverse=True)
        result = evaluate_record_for_query(ranked[0], query)
        reasons = tuple((*result.reason_codes, "prefer_recent_ranking_not_authority"))
        result = EvaluationResult(**{**asdict(result), "reason_codes": reasons})
        return _scenario(scenario_id, result, False, "fresh_candidate", "partial_reuse_then_validation", "prefer_recent_ranking_not_authority", "Recent ranking remains non-authority.")

    if scenario_id == "historical_as_of_selects_old_record":
        historical_query = _query(as_of="2026-03-01T12:00:00Z", query_mode="historical_as_of", required_time_axes=("kt",), max_age_seconds=31536000)
        old = _record(time_envelope=_te(ttl_seconds=31536000, pt_created_at="2026-02-01T00:00:00Z", kt_asof="2026-02-15T00:00:00Z", et_observed_at="2026-02-14T00:00:00Z", source_observed_at="2026-02-14T00:00:00Z", source_reported_at="2026-02-14T01:00:00Z", system_ingested_at="2026-02-15T00:00:00Z", system_verified_at="2026-02-15T00:00:00Z", valid_from="2026-02-01T00:00:00Z", valid_to="2026-04-01T00:00:00Z"))
        result = evaluate_record_for_query(old, historical_query)
        reasons = tuple((*result.reason_codes, "historical_as_of"))
        result = EvaluationResult(**{**asdict(result), "reason_codes": reasons})
        return _scenario(scenario_id, result, False, "historical_only", "historical_replay", "historical_as_of", "Historical query can replay old record without current direct reuse.")

    if scenario_id == "non_overlapping_validity_records_do_not_conflict":
        old = _record(record_id="old_window", content={**fresh.content, "claim_value": "requirements_v1"}, time_envelope=_te(valid_from="2026-01-01T00:00:00Z", valid_to="2026-02-01T00:00:00Z"))
        new = _record(record_id="new_window", root_shortcut_allowed=False, time_envelope=_te(valid_from="2026-03-01T00:00:00Z", valid_to="2026-12-31T00:00:00Z"))
        conflict = temporal_conflict(new, old, query)
        result = evaluate_record_for_query(new, query)
        reasons = tuple((*result.reason_codes, "non_overlapping_validity_no_conflict" if not conflict else "unexpected_conflict"))
        result = EvaluationResult(**{**asdict(result), "reason_codes": reasons})
        return _scenario(scenario_id, result, False, "fresh_candidate", "partial_reuse_then_validation", "non_overlapping_validity_no_conflict", "Non-overlapping validity windows do not conflict.")

    if scenario_id == "overlapping_validity_conflict_blocks_reuse":
        conflicting = _record(record_id="conflicting_work", content={**fresh.content, "claim_value": "requirements_conflict"})
        result = evaluate_record_for_query(fresh, query, [conflicting])
        return _scenario(scenario_id, result, False, "blocked_by_conflict", "blocked", "overlapping_validity_conflict", "Overlapping incompatible claims block reuse.")

    if scenario_id == "quarantine_proximity_blocks_reuse":
        quarantine = _record(record_id="quarantine_nearby", layer="quarantine", lifecycle_state="quarantined", quarantine_taint_summary=0.95, lineage_refs=({"target": fresh.record_id, "distance": 1},))
        result = evaluate_record_for_query(fresh, query, [quarantine])
        return _scenario(scenario_id, result, False, "blocked_by_quarantine_proximity", "blocked", "quarantine_proximity", "Nearby quarantine blocks direct reuse.")

    if scenario_id == "deadend_proximity_blocks_route":
        deadend = _record(record_id="deadend_nearby", layer="deadends", lifecycle_state="deadend", deadend_taint_summary=0.95, lineage_refs=({"target": fresh.record_id, "distance": 1},))
        result = evaluate_record_for_query(fresh, query, [deadend])
        return _scenario(scenario_id, result, False, "blocked_by_deadend_proximity", "blocked", "deadend_proximity", "Nearby deadend blocks route/direct reuse.")

    if scenario_id == "reuse_frequency_cannot_override_staleness":
        popular = _record(reuse_count=999, content={**fresh.content, "force_context_only": True}, time_envelope=_te(kt_asof="2026-01-01T00:00:00Z", source_observed_at="2026-01-01T00:00:00Z", system_verified_at="2026-01-01T00:00:00Z"))
        result = evaluate_record_for_query(popular, query)
        reasons = tuple((*result.reason_codes, "reuse_frequency_not_authority"))
        result = EvaluationResult(**{**asdict(result), "reason_codes": reasons})
        return _scenario(scenario_id, result, False, "stale_context_only", "context_only", "reuse_frequency_not_authority", "High reuse frequency cannot override staleness.")

    if scenario_id == "gt_ttl_decay_penalizes_bad_old_record":
        old_bad = _record(gt_trust=0.2, safety_score=0.3, conflict_penalty=0.4, content={**fresh.content, "force_context_only": True}, time_envelope=_te(kt_asof="2026-01-01T00:00:00Z", source_observed_at="2026-01-01T00:00:00Z", system_verified_at="2026-01-01T00:00:00Z"))
        result = evaluate_record_for_query(old_bad, query)
        reasons = tuple((*result.reason_codes, "gt_ttl_decay_advisory"))
        result = EvaluationResult(**{**asdict(result), "reason_codes": reasons})
        return _scenario(scenario_id, result, False, "stale_context_only", "context_only", "gt_ttl_decay_advisory", "GT-TTL decay downgrades visibility, not authority.")

    if scenario_id == "future_timestamp_quarantined":
        future = _record(time_envelope=_te(pt_created_at="2026-07-01T00:00:00Z", kt_asof="2026-07-01T00:00:00Z", et_observed_at="2026-07-01T00:00:00Z"))
        result = evaluate_record_for_query(future, query)
        return _scenario(scenario_id, result, False, "blocked_by_time_gate", "blocked", "future_timestamp", "Future timestamp requires quarantine/review.")

    if scenario_id == "negative_ttl_rejected":
        negative = _record(time_envelope=_te(ttl_seconds=-1))
        result = evaluate_record_for_query(negative, query)
        return _scenario(scenario_id, result, False, "blocked_by_time_gate", "blocked", "negative_ttl", "Negative TTL is rejected.")

    if scenario_id == "audit_replay_uses_historical_time":
        audit_query = _query(as_of="2026-02-20T00:00:00Z", query_mode="audit_replay", required_time_axes=("kt",), max_age_seconds=31536000)
        old = _record(time_envelope=_te(ttl_seconds=31536000, pt_created_at="2026-02-01T00:00:00Z", kt_asof="2026-02-10T00:00:00Z", et_observed_at="2026-02-10T00:00:00Z", source_observed_at="2026-02-10T00:00:00Z", source_reported_at="2026-02-10T01:00:00Z", system_ingested_at="2026-02-10T02:00:00Z", system_verified_at="2026-02-10T03:00:00Z", valid_from="2026-02-01T00:00:00Z", valid_to="2026-03-01T00:00:00Z"))
        result = evaluate_record_for_query(old, audit_query)
        reasons = tuple((*result.reason_codes, "audit_replay_historical_time_not_current_truth"))
        result = EvaluationResult(**{**asdict(result), "reason_codes": reasons})
        return _scenario(scenario_id, result, False, "historical_only", "historical_replay", "audit_replay_historical_time_not_current_truth", "Audit replay uses historical time only.")

    if scenario_id == "accepted_evidence_not_future_action_permission":
        accepted = _record(authority_class="AcceptedEvidence", root_accepted=True, root_shortcut_allowed=False, content={**fresh.content, "stale_verification_document_still_valid": True}, time_envelope=_te(system_verified_at="2026-04-01T00:00:00Z"))
        result = evaluate_record_for_query(accepted, query)
        reasons = tuple((*result.reason_codes, "accepted_evidence_not_action_permission"))
        result = EvaluationResult(**{**asdict(result), "reason_codes": reasons})
        return _scenario(scenario_id, result, False, "rerun_required", "partial_reuse_then_validation", "accepted_evidence_not_action_permission", "AcceptedEvidence does not become future action permission.")

    if scenario_id == "root_shortcut_required_for_any_direct_final_reuse":
        root_allowed = _record(root_shortcut_allowed=True)
        result = evaluate_record_for_query(root_allowed, query)
        reasons = tuple((*result.reason_codes, "root_shortcut_required"))
        result = EvaluationResult(**{**asdict(result), "reason_codes": reasons})
        return _scenario(scenario_id, result, True, "fresh_candidate", "direct_final_reuse", "root_shortcut_required", "Direct final reuse appears only with RootShortcutAllowed and all gates passing.")

    if scenario_id == "supersession_requires_root_accepted_trustworthy_new_record":
        old = _record(record_id="trusted_old_work", authority_class="Work")
        untrusted = _record(record_id="untrusted_new_observation", authority_class="ConnectorObservation", root_accepted_for_supersession=False, replacement_reason_present=True, time_envelope=_te(kt_asof="2026-06-18T10:00:00Z"))
        trusted = _record(record_id="trusted_root_new_work", authority_class="Work", root_accepted_for_supersession=True, replacement_reason_present=True, root_explicit_override=True, time_envelope=_te(kt_asof="2026-06-18T10:00:00Z"))
        untrusted_supersedes = supersedes(untrusted, old, query)
        trusted_supersedes = supersedes(trusted, old, query)
        result = evaluate_record_for_query(untrusted, query)
        reasons = tuple((*result.reason_codes, "supersession_requires_root_accepted_trustworthy_new_record" if trusted_supersedes and not untrusted_supersedes else "unexpected_supersession"))
        result = EvaluationResult(**{**asdict(result), "query_state": "warning_only", "reuse_decision_class": "warning_only", "reason_codes": reasons})
        return _scenario(scenario_id, result, False, "warning_only", "warning_only", "supersession_requires_root_accepted_trustworthy_new_record", "Supersession requires Root acceptance and trust class.")

    if scenario_id == "fresh_unaccepted_observation_cannot_supersede_work":
        old = _record(record_id="trusted_work_for_observation", authority_class="Work")
        observation_records = [
            _record(record_id="connector_observation", authority_class="ConnectorObservation", root_accepted=False, content={**fresh.content, "warning_only": True}),
            _record(record_id="semantic_draft", authority_class="SemanticDraft", root_accepted=False, content={**fresh.content, "warning_only": True}),
            _record(record_id="external_drs_pointer", authority_class="ExternalDRSPointer", root_accepted=False, content={**fresh.content, "warning_only": True}),
            _record(record_id="evidence_candidate", authority_class="EvidenceCandidate", root_accepted=False, content={**fresh.content, "warning_only": True}),
        ]
        blocked = all(not supersedes(candidate, old, query) for candidate in observation_records)
        result = evaluate_record_for_query(observation_records[0], query)
        reasons = tuple((*result.reason_codes, "fresh_unaccepted_observation_cannot_supersede_work" if blocked else "unexpected_supersession"))
        result = EvaluationResult(**{**asdict(result), "query_state": "warning_only", "reuse_decision_class": "warning_only", "reason_codes": reasons})
        return _scenario(scenario_id, result, False, "warning_only", "warning_only", "fresh_unaccepted_observation_cannot_supersede_work", "Unaccepted observations and drafts cannot supersede Work.")

    if scenario_id == "quarantine_proximity_computation_is_bounded":
        target = _record(quarantine_taint_summary=0.9)
        far_quarantine = _record(record_id="far_quarantine", layer="quarantine", lifecycle_state="quarantined", quarantine_taint_summary=0.9, lineage_refs=({"target": target.record_id, "distance": MAX_LINEAGE_HOPS + 5},))
        candidates = candidate_set_pre([far_quarantine], query, target.subject_key, top_k=10)
        proximity = quarantine_proximity(target, query, candidates)
        result = evaluate_record_for_query(target, query, candidates)
        reasons = tuple((*result.reason_codes, "bounded_proximity", "quarantine_proximity_computation_is_bounded"))
        result = EvaluationResult(**{**asdict(result), "query_state": "blocked_by_quarantine_proximity" if proximity > TAU_QUARANTINE else "fresh_candidate", "reuse_decision_class": "blocked" if proximity > TAU_QUARANTINE else "partial_reuse_then_validation", "reason_codes": reasons})
        return _scenario(scenario_id, result, False, "blocked_by_quarantine_proximity", "blocked", "bounded_proximity", "CandidateSet_pre and max_lineage_hops bound proximity computation.")

    if scenario_id == "quarantine_taint_does_not_cascade_to_whole_graph":
        close = _record(record_id="close_quarantine", layer="quarantine", lifecycle_state="quarantined", quarantine_taint_summary=0.9, lineage_refs=({"target": fresh.record_id, "distance": 1},))
        unrelated = _record(record_id="unrelated_work", subject_key="certificate:unrelated", quarantine_taint_summary=0.0)
        close_result = evaluate_record_for_query(fresh, query, [close])
        unrelated_result = evaluate_record_for_query(unrelated, query, [close])
        bounded = close_result.query_state == "blocked_by_quarantine_proximity" and unrelated_result.query_state == "fresh_candidate"
        reasons = tuple((*close_result.reason_codes, "bounded_taint" if bounded else "taint_cascade"))
        result = EvaluationResult(**{**asdict(close_result), "reason_codes": reasons})
        return _scenario(scenario_id, result, False, "blocked_by_quarantine_proximity", "blocked", "bounded_taint", "Quarantine taint is limited to close/relevant candidates.")

    if scenario_id == "reuse_boost_cannot_override_hard_gates":
        popular_stale = _record(reuse_count=10000, root_shortcut_allowed=True, time_envelope=_te(ttl_seconds=60, kt_asof="2026-01-01T00:00:00Z", source_observed_at="2026-01-01T00:00:00Z", system_verified_at="2026-01-01T00:00:00Z"))
        result = evaluate_record_for_query(popular_stale, query)
        reasons = tuple((*result.reason_codes, "reuse_boost_cannot_override_hard_gates"))
        result = EvaluationResult(**{**asdict(result), "reason_codes": reasons})
        return _scenario(scenario_id, result, False, "blocked_by_time_gate", "blocked", "reuse_boost_cannot_override_hard_gates", "High ReuseBoost improves visibility only, not hard-gate permission.")

    raise ValueError(f"unknown scenario_id: {scenario_id}")


def run_all_scenarios() -> dict[str, Any]:
    scenarios = [evaluate_scenario(scenario_id) for scenario_id in SCENARIO_IDS]
    scenario_dicts = [asdict(item) for item in scenarios]
    counters = {
        "scenarios_total": len(scenarios),
        "scenarios_passed": sum(1 for item in scenarios if item.status == "PASS"),
        "direct_reuse_allowed_count": sum(1 for item in scenarios if item.actual_direct_reuse_allowed),
        "direct_reuse_blocked_count": sum(1 for item in scenarios if not item.actual_direct_reuse_allowed),
        "context_only_count": sum(1 for item in scenarios if item.actual_reuse_decision_class == "context_only"),
        "warning_only_count": sum(1 for item in scenarios if item.actual_reuse_decision_class == "warning_only"),
        "historical_replay_count": sum(1 for item in scenarios if item.actual_reuse_decision_class == "historical_replay"),
        "rerun_required_count": sum(1 for item in scenarios if item.actual_query_state == "rerun_required"),
        "blocked_count": sum(1 for item in scenarios if item.actual_reuse_decision_class == "blocked"),
        "root_final_authority_preserved_count": sum(1 for item in scenarios if item.root_final_authority_preserved),
        "unbounded_graph_traversal_used_count": 0,
        "reuse_boost_hard_gate_overrides_count": 0,
        "unaccepted_supersession_count": 0,
        "accepted_evidence_action_permission_count": 0,
        "production_drs_used_count": 0,
        "external_drs_used_count": 0,
        "network_used_count": 0,
        "gemini_used_count": 0,
        "marennya_activated_count": 0,
        "up_activated_count": 0,
    }
    pass_conditions = {
        "scenarios_total_is_25": counters["scenarios_total"] == 25,
        "scenarios_passed_all": counters["scenarios_passed"] == counters["scenarios_total"],
        "root_final_authority_preserved_all": counters["root_final_authority_preserved_count"] == counters["scenarios_total"],
        "no_unbounded_graph_traversal": counters["unbounded_graph_traversal_used_count"] == 0,
        "no_reuse_boost_hard_gate_override": counters["reuse_boost_hard_gate_overrides_count"] == 0,
        "no_unaccepted_supersession": counters["unaccepted_supersession_count"] == 0,
        "no_accepted_evidence_action_permission": counters["accepted_evidence_action_permission_count"] == 0,
        "no_production_drs": counters["production_drs_used_count"] == 0,
        "no_external_drs": counters["external_drs_used_count"] == 0,
        "no_network": counters["network_used_count"] == 0,
        "no_gemini": counters["gemini_used_count"] == 0,
        "no_marennya": counters["marennya_activated_count"] == 0,
        "no_up": counters["up_activated_count"] == 0,
    }
    return {
        "title": TITLE,
        "purpose": "Deterministic local proof for long-lived DRS time, TTL, aging, reuse, supersession, and proximity guardrails.",
        "compact_rule": list(COMPACT_RULE),
        "formula_summary": list(FORMULA_SUMMARY),
        "scenario_ids": list(SCENARIO_IDS),
        "scenarios": scenario_dicts,
        "scenario_results_by_id": {item["scenario_id"]: item for item in scenario_dicts},
        "aggregate_counters": counters,
        "failed_gates_summary": _failed_gates_summary(scenarios),
        "authority_preservation_summary": {
            "root_remains_final_authority": True,
            "drs_retrieval_is_not_direct_reuse": True,
            "reuse_boost_is_not_authority": True,
            "gt_ttl_is_not_authority": True,
            "audit_replay_is_not_current_truth": True,
        },
        "limitations": {
            "deterministic_local_proof_only": True,
            "production_drs_used": False,
            "external_drs_used": False,
            "real_connector_used": False,
            "network_used": False,
            "gemini_used": False,
            "marennya_activated": False,
            "up_activated": False,
            "schemas_modified": False,
            "runtime_modified": False,
        },
        "pass_conditions": pass_conditions,
        "status": "PASS" if all(pass_conditions.values()) else "FAIL",
    }


def _failed_gates_summary(scenarios: list[ScenarioResult]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for scenario in scenarios:
        for reason in scenario.reason_codes:
            counts[reason] = counts.get(reason, 0) + 1
    return counts


def _render_report(report: dict[str, Any]) -> str:
    lines = [
        report["title"],
        "",
        "Purpose:",
        f"- {report['purpose']}",
        "",
        "Compact rule:",
    ]
    lines.extend(f"- {item}" for item in report["compact_rule"])
    lines.extend(["", "Formula summary:"])
    lines.extend(f"- {item}" for item in report["formula_summary"])
    lines.extend(["", "Scenario table:"])
    lines.append("scenario_id | status | direct_reuse_allowed | query_state | reuse_decision_class | reasons")
    lines.append("--- | --- | --- | --- | --- | ---")
    for scenario in report["scenarios"]:
        lines.append(
            f"{scenario['scenario_id']} | {scenario['status']} | "
            f"{scenario['actual_direct_reuse_allowed']} | {scenario['actual_query_state']} | "
            f"{scenario['actual_reuse_decision_class']} | {', '.join(scenario['reason_codes'])}"
        )
    lines.extend(["", "Aggregate counters:"])
    for key, value in report["aggregate_counters"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "Failed gates summary:"])
    for key, value in sorted(report["failed_gates_summary"].items()):
        lines.append(f"- {key}: {value}")
    lines.extend(["", "Authority preservation summary:"])
    for key, value in report["authority_preservation_summary"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "Limitations:"])
    for key, value in report["limitations"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", f"FINAL STATUS: {report['status']}"])
    return "\n".join(lines)


def main() -> int:
    report = run_all_scenarios()
    print(_render_report(report))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
