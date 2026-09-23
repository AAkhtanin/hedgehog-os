from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


TIME_ENVELOPE_CONCEPT = "TimeEnvelope"
TEMPORAL_QUERY_CONCEPT = "TemporalQuery"

REUSE_CONTEXT_ONLY = "context_only"
REUSE_PARTIAL_REUSE_THEN_VALIDATION = "partial_reuse_then_validation"
REUSE_WARNING_ONLY = "warning_only"
REUSE_RERUN_REQUIRED = "rerun_required"
REUSE_BLOCKED = "blocked"
REUSE_DIRECT_REUSE_CANDIDATE = "direct_reuse_candidate"
REUSE_DIRECT_REUSE_ALLOWED = "direct_reuse_allowed"

FRESHNESS_FRESH_CONTEXT = "fresh_context"
FRESHNESS_STALE_WARNING = "stale_warning"
FRESHNESS_EXPIRED_RERUN_REQUIRED = "expired_rerun_required"
FRESHNESS_CHANGED_FACT_RERUN_REQUIRED = "changed_fact_rerun_required"
FRESHNESS_BLOCKED_BY_POLICY_OR_CONFLICT = "blocked_by_policy_or_conflict"

REASON_MISSING_TIME_ENVELOPE = "missing_time_envelope"
REASON_MISSING_TEMPORAL_QUERY = "missing_temporal_query"
REASON_INVALID_TTL_SECONDS = "invalid_ttl_seconds"
REASON_STALE_RECORD_NOT_PERMISSION = "stale_record_not_permission"
REASON_OLD_RECEIPT_NOT_PERMISSION = "old_receipt_not_permission"
REASON_PRIOR_ROOT_FINAL_NOT_SILENT_REUSE = "prior_root_final_not_silent_reuse"
REASON_ACCEPTED_EVIDENCE_NOT_FUTURE_ACTION_PERMISSION = (
    "accepted_evidence_not_future_action_permission"
)
REASON_CHANGED_FACTS_REQUIRE_RERUN_VALIDATION = "changed_facts_require_rerun_validation"
REASON_QUARANTINE_PROXIMITY_BLOCKS_DIRECT_REUSE = (
    "quarantine_proximity_blocks_direct_reuse"
)
REASON_DEADEND_PROXIMITY_BLOCKS_OR_DOWNGRADES_REUSE = (
    "deadend_proximity_blocks_or_downgrades_reuse"
)
REASON_CONFLICT_REQUIRES_RERUN_VALIDATION = "conflict_requires_rerun_validation"
REASON_ROOT_REVIEW_REQUIRED = "root_review_required"
REASON_DIRECT_REUSE_DEFAULT_FALSE = "direct_reuse_default_false"
REASON_LINEAGE_REFS_PRESERVED = "lineage_refs_preserved"
REASON_PROVENANCE_REFS_PRESERVED = "provenance_refs_preserved"
REASON_CONTEXT_ONLY_NOT_AUTHORITY = "context_only_not_authority"
REASON_PERMISSION_TRACE_NOT_COMPLETED_ACTION = "permission_trace_not_completed_action"
REASON_WRONG_DOMAIN_NEAR_MATCH_NOT_DIRECT_REUSE = (
    "wrong_domain_near_match_not_direct_reuse"
)
REASON_DUPLICATE_POISONING_PRESSURE_DOES_NOT_CREATE_AUTHORITY = (
    "duplicate_poisoning_pressure_does_not_create_authority"
)
REASON_CONFLICTING_PROVENANCE_BLOCKS_REUSE = "conflicting_provenance_blocks_reuse"
REASON_REUSE_SCORE_NOT_ROOT = "reuse_score_not_root"
REASON_SEMANTIC_SIMILARITY_NOT_AUTHORITY = "semantic_similarity_not_authority"

_STALE_FRESHNESS_CLASSES = {
    FRESHNESS_STALE_WARNING,
    FRESHNESS_EXPIRED_RERUN_REQUIRED,
    FRESHNESS_CHANGED_FACT_RERUN_REQUIRED,
    FRESHNESS_BLOCKED_BY_POLICY_OR_CONFLICT,
}


@dataclass(frozen=True)
class DRSLineageRef:
    ref_id: str
    ref_kind: str
    relation: str
    source_observed_at: str | None = None
    system_ingested_at: str | None = None
    notes: tuple[str, ...] = ()


@dataclass(frozen=True)
class DRSFreshnessEnvelope:
    physical_time: str
    knowledge_time: str
    event_time: str
    context_time: str
    ttl_seconds: int | None
    validity_start: str | None = None
    validity_end: str | None = None
    source_observed_at: str | None = None
    system_ingested_at: str | None = None
    freshness_class: str = FRESHNESS_FRESH_CONTEXT


@dataclass(frozen=True)
class TemporalQueryV02:
    query_id: str
    as_of: str
    context_time: str
    freshness_bias: str = "current"
    time_range_start: str | None = None
    time_range_end: str | None = None
    require_root_review: bool = True
    allow_direct_reuse_if_all_gates_pass: bool = False


@dataclass(frozen=True)
class DRSRecordV02:
    record_id: str
    record_kind: str
    summary: str
    time_envelope: DRSFreshnessEnvelope | None
    lineage_refs: tuple[DRSLineageRef, ...] = ()
    source_refs: tuple[str, ...] = ()
    provenance_refs: tuple[str, ...] = ()
    prior_trace_ref: str | None = None
    root_final_ref: str | None = None
    artifact_refs: tuple[str, ...] = ()
    validation_refs: tuple[str, ...] = ()
    contains_receipt: bool = False
    contains_action_permission: bool = False
    accepted_evidence: bool = False
    changed_facts: bool = False
    conflict_pressure: bool = False
    conflicting_provenance: bool = False
    duplicate_poisoning_pressure: bool = False
    wrong_domain_near_match: bool = False
    quarantine_proximity: bool = False
    deadend_proximity: bool = False
    policy_ok: bool = True
    permission_ok: bool = False
    root_shortcut_allowed: bool = False
    reuse_score: float = 0.0
    semantic_similarity_score: float | None = None
    truth_claimed: bool = False
    authority_claimed: bool = False
    action_permission_claimed: bool = False
    final_output_claimed: bool = False


@dataclass(frozen=True)
class DRSReuseDecision:
    record_id: str
    reuse_decision_class: str
    freshness_class: str
    direct_reuse_allowed: bool
    context_only: bool
    root_review_required: bool
    reason_codes: tuple[str, ...]
    lineage_refs: tuple[DRSLineageRef, ...]
    source_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    authority_claimed: bool = False
    truth_claimed: bool = False
    action_permission_claimed: bool = False
    final_output_claimed: bool = False


@dataclass(frozen=True)
class DRSResolveReport:
    query_id: str
    temporal_query_present: bool
    records_evaluated_count: int
    decisions: tuple[DRSReuseDecision, ...]
    direct_reuse_allowed_count: int
    context_only_count: int
    root_review_required_count: int
    lineage_refs_preserved_count: int
    production_ready_claimed: bool = False
    public_auditor_ready_claimed: bool = False
    real_world_effects_count: int = 0


@dataclass(frozen=True)
class LocalDRSResolveInputV02:
    temporal_query: TemporalQueryV02 | None
    records: tuple[DRSRecordV02, ...]
    query_scope: str = "local_drs_v0_2"
    resolver_mode: str = "deterministic_local"
    production_ready_claimed: bool = False
    public_auditor_ready_claimed: bool = False


@dataclass(frozen=True)
class DRSResolveTableRowV02:
    record_id: str
    record_kind: str
    freshness_class: str
    reuse_decision_class: str
    direct_reuse_allowed: bool
    context_only: bool
    root_review_required: bool
    reason_codes: tuple[str, ...]
    lineage_ref_count: int
    source_ref_count: int
    provenance_ref_count: int


@dataclass(frozen=True)
class DRSReuseDecisionReportV02:
    report_id: str
    query_id: str
    resolver_mode: str
    temporal_query_present: bool
    records_evaluated_count: int
    rows: tuple[DRSResolveTableRowV02, ...]
    decisions: tuple[DRSReuseDecision, ...]
    freshness_table: tuple[dict[str, object], ...]
    lineage_table: tuple[dict[str, object], ...]
    provenance_table: tuple[dict[str, object], ...]
    reuse_decision_table: tuple[dict[str, object], ...]
    direct_reuse_allowed_count: int
    direct_reuse_candidate_count: int
    context_only_count: int
    warning_only_count: int
    rerun_required_count: int
    blocked_count: int
    root_review_required_count: int
    production_ready_claimed: bool = False
    public_auditor_ready_claimed: bool = False
    real_world_effects_count: int = 0


def _non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _append_reason(reasons: list[str], reason: str) -> None:
    if reason not in reasons:
        reasons.append(reason)


def _with_boundary_reasons(record: DRSRecordV02, reasons: list[str]) -> None:
    if record.lineage_refs:
        _append_reason(reasons, REASON_LINEAGE_REFS_PRESERVED)
    if record.provenance_refs:
        _append_reason(reasons, REASON_PROVENANCE_REFS_PRESERVED)
    _append_reason(reasons, REASON_CONTEXT_ONLY_NOT_AUTHORITY)


def _with_advisory_score_reasons(
    record: DRSRecordV02,
    reasons: list[str],
    tau_reuse: float,
) -> None:
    if record.reuse_score >= tau_reuse:
        _append_reason(reasons, REASON_REUSE_SCORE_NOT_ROOT)
    if record.semantic_similarity_score is not None:
        _append_reason(reasons, REASON_SEMANTIC_SIMILARITY_NOT_AUTHORITY)


def _has_conflicting_provenance(record: DRSRecordV02) -> bool:
    provenance_fragments = record.provenance_refs + record.source_refs
    return record.conflicting_provenance or any(
        "conflict" in fragment or "contradict" in fragment
        for fragment in provenance_fragments
    )


def validate_freshness_envelope(
    envelope: DRSFreshnessEnvelope | None,
) -> tuple[bool, tuple[str, ...]]:
    if envelope is None:
        return False, (REASON_MISSING_TIME_ENVELOPE,)

    reasons: list[str] = []
    invalid_required_time = not (
        _non_empty_string(envelope.physical_time)
        and _non_empty_string(envelope.knowledge_time)
        and _non_empty_string(envelope.event_time)
        and _non_empty_string(envelope.context_time)
    )
    if invalid_required_time:
        reasons.append(REASON_MISSING_TIME_ENVELOPE)
    invalid_ttl = not (
        envelope.ttl_seconds is None
        or (isinstance(envelope.ttl_seconds, int) and envelope.ttl_seconds >= 0)
    )
    if invalid_ttl:
        reasons.append(REASON_INVALID_TTL_SECONDS)
    if reasons:
        return False, tuple(reasons)
    return True, ()


def validate_temporal_query(
    query: TemporalQueryV02 | None,
) -> tuple[bool, tuple[str, ...]]:
    if query is None:
        return False, (REASON_MISSING_TEMPORAL_QUERY,)
    if not (
        _non_empty_string(query.query_id)
        and _non_empty_string(query.as_of)
        and _non_empty_string(query.context_time)
    ):
        return False, (REASON_MISSING_TEMPORAL_QUERY,)
    return True, ()


def _freshness_class(record: DRSRecordV02) -> str:
    if record.time_envelope is None:
        return FRESHNESS_BLOCKED_BY_POLICY_OR_CONFLICT
    return record.time_envelope.freshness_class


def _claims_boundary(record: DRSRecordV02) -> bool:
    return any(
        (
            record.truth_claimed,
            record.authority_claimed,
            record.action_permission_claimed,
            record.final_output_claimed,
            record.contains_action_permission,
        )
    )


def _hard_gates_allow_direct_reuse(
    record: DRSRecordV02,
    query: TemporalQueryV02,
    *,
    tau_reuse: float,
) -> bool:
    return (
        query.allow_direct_reuse_if_all_gates_pass
        and record.root_shortcut_allowed
        and record.policy_ok
        and record.permission_ok
        and record.reuse_score >= tau_reuse
        and _freshness_class(record) == FRESHNESS_FRESH_CONTEXT
        and not record.changed_facts
        and not record.conflict_pressure
        and not _has_conflicting_provenance(record)
        and not record.duplicate_poisoning_pressure
        and not record.wrong_domain_near_match
        and not record.quarantine_proximity
        and not record.deadend_proximity
        and not record.contains_receipt
        and not record.accepted_evidence
        and record.root_final_ref is None
        and not _claims_boundary(record)
    )


def _candidate_shape(record: DRSRecordV02, tau_reuse: float) -> bool:
    return record.policy_ok and record.reuse_score >= tau_reuse and not (
        record.changed_facts
        or record.conflict_pressure
        or _has_conflicting_provenance(record)
        or record.duplicate_poisoning_pressure
        or record.wrong_domain_near_match
        or record.quarantine_proximity
        or record.deadend_proximity
        or _freshness_class(record) in _STALE_FRESHNESS_CLASSES
        or _claims_boundary(record)
    )


def _make_decision(
    record: DRSRecordV02,
    *,
    decision_class: str,
    direct_reuse_allowed: bool,
    reason_codes: Iterable[str],
    query: TemporalQueryV02 | None,
) -> DRSReuseDecision:
    root_review_required = True if query is None else (
        query.require_root_review or not direct_reuse_allowed
    )
    reasons = list(reason_codes)
    if root_review_required:
        _append_reason(reasons, REASON_ROOT_REVIEW_REQUIRED)
    return DRSReuseDecision(
        record_id=record.record_id,
        reuse_decision_class=decision_class,
        freshness_class=_freshness_class(record),
        direct_reuse_allowed=direct_reuse_allowed,
        context_only=decision_class == REUSE_CONTEXT_ONLY,
        root_review_required=root_review_required,
        reason_codes=tuple(reasons),
        lineage_refs=record.lineage_refs,
        source_refs=record.source_refs,
        provenance_refs=record.provenance_refs,
        authority_claimed=False,
        truth_claimed=False,
        action_permission_claimed=False,
        final_output_claimed=False,
    )


def evaluate_drs_record_v02(
    record: DRSRecordV02,
    query: TemporalQueryV02 | None,
    *,
    tau_reuse: float = 0.92,
) -> DRSReuseDecision:
    query_valid, query_reasons = validate_temporal_query(query)
    envelope_valid, envelope_reasons = validate_freshness_envelope(record.time_envelope)
    reasons: list[str] = []
    _with_boundary_reasons(record, reasons)
    _with_advisory_score_reasons(record, reasons, tau_reuse)

    if not query_valid:
        reasons.extend(query_reasons)
        return _make_decision(
            record,
            decision_class=REUSE_BLOCKED,
            direct_reuse_allowed=False,
            reason_codes=reasons,
            query=query,
        )

    if not envelope_valid:
        reasons.extend(envelope_reasons)
        return _make_decision(
            record,
            decision_class=REUSE_BLOCKED,
            direct_reuse_allowed=False,
            reason_codes=reasons,
            query=query,
        )

    if record.contains_action_permission:
        _append_reason(reasons, REASON_PERMISSION_TRACE_NOT_COMPLETED_ACTION)

    if _claims_boundary(record):
        return _make_decision(
            record,
            decision_class=REUSE_BLOCKED,
            direct_reuse_allowed=False,
            reason_codes=reasons,
            query=query,
        )

    if record.contains_receipt:
        _append_reason(reasons, REASON_OLD_RECEIPT_NOT_PERMISSION)
    if record.root_final_ref is not None:
        _append_reason(reasons, REASON_PRIOR_ROOT_FINAL_NOT_SILENT_REUSE)
    if record.accepted_evidence:
        _append_reason(reasons, REASON_ACCEPTED_EVIDENCE_NOT_FUTURE_ACTION_PERMISSION)

    if record.duplicate_poisoning_pressure:
        _append_reason(
            reasons,
            REASON_DUPLICATE_POISONING_PRESSURE_DOES_NOT_CREATE_AUTHORITY,
        )
        return _make_decision(
            record,
            decision_class=REUSE_BLOCKED,
            direct_reuse_allowed=False,
            reason_codes=reasons,
            query=query,
        )

    if record.wrong_domain_near_match:
        _append_reason(reasons, REASON_WRONG_DOMAIN_NEAR_MATCH_NOT_DIRECT_REUSE)
        return _make_decision(
            record,
            decision_class=REUSE_RERUN_REQUIRED,
            direct_reuse_allowed=False,
            reason_codes=reasons,
            query=query,
        )

    if record.quarantine_proximity:
        _append_reason(reasons, REASON_QUARANTINE_PROXIMITY_BLOCKS_DIRECT_REUSE)
        return _make_decision(
            record,
            decision_class=REUSE_BLOCKED,
            direct_reuse_allowed=False,
            reason_codes=reasons,
            query=query,
        )

    if record.deadend_proximity:
        _append_reason(reasons, REASON_DEADEND_PROXIMITY_BLOCKS_OR_DOWNGRADES_REUSE)
        return _make_decision(
            record,
            decision_class=REUSE_BLOCKED,
            direct_reuse_allowed=False,
            reason_codes=reasons,
            query=query,
        )

    if record.changed_facts:
        _append_reason(reasons, REASON_CHANGED_FACTS_REQUIRE_RERUN_VALIDATION)
        return _make_decision(
            record,
            decision_class=REUSE_RERUN_REQUIRED,
            direct_reuse_allowed=False,
            reason_codes=reasons,
            query=query,
        )

    if record.conflict_pressure or _has_conflicting_provenance(record):
        _append_reason(reasons, REASON_CONFLICT_REQUIRES_RERUN_VALIDATION)
        if _has_conflicting_provenance(record):
            _append_reason(reasons, REASON_CONFLICTING_PROVENANCE_BLOCKS_REUSE)
        return _make_decision(
            record,
            decision_class=REUSE_RERUN_REQUIRED,
            direct_reuse_allowed=False,
            reason_codes=reasons,
            query=query,
        )

    freshness_class = _freshness_class(record)
    if freshness_class == FRESHNESS_STALE_WARNING:
        _append_reason(reasons, REASON_STALE_RECORD_NOT_PERMISSION)
        return _make_decision(
            record,
            decision_class=REUSE_WARNING_ONLY,
            direct_reuse_allowed=False,
            reason_codes=reasons,
            query=query,
        )
    if freshness_class in {
        FRESHNESS_EXPIRED_RERUN_REQUIRED,
        FRESHNESS_CHANGED_FACT_RERUN_REQUIRED,
    }:
        _append_reason(reasons, REASON_STALE_RECORD_NOT_PERMISSION)
        return _make_decision(
            record,
            decision_class=REUSE_RERUN_REQUIRED,
            direct_reuse_allowed=False,
            reason_codes=reasons,
            query=query,
        )
    if freshness_class == FRESHNESS_BLOCKED_BY_POLICY_OR_CONFLICT:
        _append_reason(reasons, REASON_STALE_RECORD_NOT_PERMISSION)
        return _make_decision(
            record,
            decision_class=REUSE_BLOCKED,
            direct_reuse_allowed=False,
            reason_codes=reasons,
            query=query,
        )

    if (
        record.contains_receipt
        or record.root_final_ref is not None
        or record.accepted_evidence
    ):
        return _make_decision(
            record,
            decision_class=REUSE_CONTEXT_ONLY,
            direct_reuse_allowed=False,
            reason_codes=reasons,
            query=query,
        )

    if query is not None and _hard_gates_allow_direct_reuse(
        record,
        query,
        tau_reuse=tau_reuse,
    ):
        return _make_decision(
            record,
            decision_class=REUSE_DIRECT_REUSE_ALLOWED,
            direct_reuse_allowed=True,
            reason_codes=reasons,
            query=query,
        )

    if _candidate_shape(record, tau_reuse):
        _append_reason(reasons, REASON_DIRECT_REUSE_DEFAULT_FALSE)
        return _make_decision(
            record,
            decision_class=REUSE_DIRECT_REUSE_CANDIDATE,
            direct_reuse_allowed=False,
            reason_codes=reasons,
            query=query,
        )

    return _make_decision(
        record,
        decision_class=REUSE_CONTEXT_ONLY,
        direct_reuse_allowed=False,
        reason_codes=reasons,
        query=query,
    )


def build_drs_resolve_report_v02(
    query: TemporalQueryV02 | None,
    records: tuple[DRSRecordV02, ...] | list[DRSRecordV02],
) -> DRSResolveReport:
    decisions = tuple(evaluate_drs_record_v02(record, query) for record in records)
    return DRSResolveReport(
        query_id=query.query_id if query is not None else "",
        temporal_query_present=validate_temporal_query(query)[0],
        records_evaluated_count=len(records),
        decisions=decisions,
        direct_reuse_allowed_count=sum(
            1 for decision in decisions if decision.direct_reuse_allowed
        ),
        context_only_count=sum(1 for decision in decisions if decision.context_only),
        root_review_required_count=sum(
            1 for decision in decisions if decision.root_review_required
        ),
        lineage_refs_preserved_count=sum(
            1 for decision in decisions if decision.lineage_refs
        ),
        production_ready_claimed=False,
        public_auditor_ready_claimed=False,
        real_world_effects_count=0,
    )


def _row_for_decision(
    record: DRSRecordV02,
    decision: DRSReuseDecision,
) -> DRSResolveTableRowV02:
    return DRSResolveTableRowV02(
        record_id=record.record_id,
        record_kind=record.record_kind,
        freshness_class=decision.freshness_class,
        reuse_decision_class=decision.reuse_decision_class,
        direct_reuse_allowed=decision.direct_reuse_allowed,
        context_only=decision.context_only,
        root_review_required=decision.root_review_required,
        reason_codes=decision.reason_codes,
        lineage_ref_count=len(record.lineage_refs),
        source_ref_count=len(record.source_refs),
        provenance_ref_count=len(record.provenance_refs),
    )


def _freshness_row(record: DRSRecordV02, decision: DRSReuseDecision) -> dict[str, object]:
    envelope = record.time_envelope
    return {
        "record_id": record.record_id,
        "freshness_class": decision.freshness_class,
        "has_time_envelope": envelope is not None,
        "physical_time": envelope.physical_time if envelope else None,
        "knowledge_time": envelope.knowledge_time if envelope else None,
        "event_time": envelope.event_time if envelope else None,
        "context_time": envelope.context_time if envelope else None,
        "ttl_seconds": envelope.ttl_seconds if envelope else None,
    }


def _lineage_rows(record: DRSRecordV02) -> tuple[dict[str, object], ...]:
    return tuple(
        {
            "record_id": record.record_id,
            "ref_id": ref.ref_id,
            "ref_kind": ref.ref_kind,
            "relation": ref.relation,
            "source_observed_at": ref.source_observed_at,
            "system_ingested_at": ref.system_ingested_at,
            "notes": ref.notes,
        }
        for ref in record.lineage_refs
    )


def _provenance_row(record: DRSRecordV02) -> dict[str, object]:
    return {
        "record_id": record.record_id,
        "source_refs": record.source_refs,
        "provenance_refs": record.provenance_refs,
        "prior_trace_ref": record.prior_trace_ref,
        "root_final_ref": record.root_final_ref,
        "artifact_refs": record.artifact_refs,
        "validation_refs": record.validation_refs,
    }


def _reuse_decision_row(decision: DRSReuseDecision) -> dict[str, object]:
    return {
        "record_id": decision.record_id,
        "reuse_decision_class": decision.reuse_decision_class,
        "direct_reuse_allowed": decision.direct_reuse_allowed,
        "context_only": decision.context_only,
        "root_review_required": decision.root_review_required,
        "reason_codes": decision.reason_codes,
        "truth_claimed": decision.truth_claimed,
        "authority_claimed": decision.authority_claimed,
        "action_permission_claimed": decision.action_permission_claimed,
        "final_output_claimed": decision.final_output_claimed,
    }


def resolve_drs_records_v02(
    input: LocalDRSResolveInputV02,
) -> DRSReuseDecisionReportV02:
    decisions = tuple(
        evaluate_drs_record_v02(record, input.temporal_query) for record in input.records
    )
    rows = tuple(
        _row_for_decision(record, decision)
        for record, decision in zip(input.records, decisions, strict=True)
    )
    lineage_table = tuple(
        row
        for record in input.records
        for row in _lineage_rows(record)
    )
    return DRSReuseDecisionReportV02(
        report_id="local_drs_v0_2_reuse_decision_report",
        query_id=input.temporal_query.query_id if input.temporal_query else "",
        resolver_mode=input.resolver_mode,
        temporal_query_present=validate_temporal_query(input.temporal_query)[0],
        records_evaluated_count=len(input.records),
        rows=rows,
        decisions=decisions,
        freshness_table=tuple(
            _freshness_row(record, decision)
            for record, decision in zip(input.records, decisions, strict=True)
        ),
        lineage_table=lineage_table,
        provenance_table=tuple(_provenance_row(record) for record in input.records),
        reuse_decision_table=tuple(_reuse_decision_row(decision) for decision in decisions),
        direct_reuse_allowed_count=sum(
            1 for decision in decisions if decision.direct_reuse_allowed
        ),
        direct_reuse_candidate_count=sum(
            1
            for decision in decisions
            if decision.reuse_decision_class == REUSE_DIRECT_REUSE_CANDIDATE
        ),
        context_only_count=sum(
            1 for decision in decisions if decision.reuse_decision_class == REUSE_CONTEXT_ONLY
        ),
        warning_only_count=sum(
            1 for decision in decisions if decision.reuse_decision_class == REUSE_WARNING_ONLY
        ),
        rerun_required_count=sum(
            1 for decision in decisions if decision.reuse_decision_class == REUSE_RERUN_REQUIRED
        ),
        blocked_count=sum(
            1 for decision in decisions if decision.reuse_decision_class == REUSE_BLOCKED
        ),
        root_review_required_count=sum(
            1 for decision in decisions if decision.root_review_required
        ),
        production_ready_claimed=False,
        public_auditor_ready_claimed=False,
        real_world_effects_count=0,
    )


def _wow_time(
    freshness_class: str = FRESHNESS_FRESH_CONTEXT,
) -> DRSFreshnessEnvelope:
    return DRSFreshnessEnvelope(
        physical_time="2026-07-06T17:00:24Z",
        knowledge_time="2026-07-06T17:00:24Z",
        event_time="2026-07-06T17:00:24Z",
        context_time="full_wow_v1_2",
        ttl_seconds=3600,
        validity_start="2026-07-06T17:00:24Z",
        validity_end="2026-07-06T18:00:24Z",
        source_observed_at="2026-07-06T17:00:24Z",
        system_ingested_at="2026-07-06T17:00:25Z",
        freshness_class=freshness_class,
    )


def _wow_lineage(record_id: str, relation: str) -> tuple[DRSLineageRef, ...]:
    return (
        DRSLineageRef(
            ref_id=f"full_wow_v1_2:{record_id}",
            ref_kind="full_wow_v1_2_trace",
            relation=relation,
            source_observed_at="2026-07-06T17:00:24Z",
            system_ingested_at="2026-07-06T17:00:25Z",
            notes=("local proof-level WOW v1.2 regression record",),
        ),
    )


def _wow_record(
    *,
    record_id: str,
    record_kind: str,
    summary: str,
    relation: str,
    freshness_class: str = FRESHNESS_FRESH_CONTEXT,
    **overrides: object,
) -> DRSRecordV02:
    values = {
        "record_id": record_id,
        "record_kind": record_kind,
        "summary": summary,
        "time_envelope": _wow_time(freshness_class),
        "lineage_refs": _wow_lineage(record_id, relation),
        "source_refs": (f"source:{record_id}",),
        "provenance_refs": ("audit:full_wow_v1_2",),
        "prior_trace_ref": "full_wow_v1_2_manual_live_multillm_fractal_real_run",
        "artifact_refs": (f"artifact:{record_id}",),
        "validation_refs": (f"validation:{record_id}",),
    }
    values.update(overrides)
    return DRSRecordV02(**values)


def build_wow_v1_2_drs_v02_regression_records() -> tuple[DRSRecordV02, ...]:
    return (
        _wow_record(
            record_id="supplier_a_prior_scoped_trace",
            record_kind="supplier_a_prior_scoped_trace",
            summary="Supplier A prior scoped trace may inform context only.",
            relation="supports_context",
            accepted_evidence=True,
            reuse_score=0.88,
        ),
        _wow_record(
            record_id="supplier_b_blocker_trace",
            record_kind="supplier_b_blocker_trace",
            summary="Supplier B blocker trace warns against reuse.",
            relation="warns_against",
            conflict_pressure=True,
            reuse_score=0.1,
        ),
        _wow_record(
            record_id="old_receipt_trace",
            record_kind="old_receipt_trace",
            summary="Old receipt trace remains evidence only.",
            relation="evidence_only",
            contains_receipt=True,
            reuse_score=0.95,
        ),
        _wow_record(
            record_id="old_shipment_held_trace",
            record_kind="old_shipment_held_trace",
            summary="Old shipment-held trace warns that shipment remains held.",
            relation="warns_against",
            freshness_class=FRESHNESS_STALE_WARNING,
            reuse_score=0.7,
        ),
        _wow_record(
            record_id="old_root_final_trace",
            record_kind="old_root_final_trace",
            summary="Old Root Final trace is lineage/provenance only.",
            relation="root_final_lineage",
            root_final_ref="root-final:full_wow_v1_2",
            reuse_score=0.96,
        ),
        _wow_record(
            record_id="changed_warehouse_fact",
            record_kind="changed_warehouse_fact",
            summary="Changed warehouse fact requires rerun validation.",
            relation="requires_rerun",
            changed_facts=True,
            reuse_score=0.2,
        ),
        _wow_record(
            record_id="stale_legal_accounting_evidence",
            record_kind="stale_legal_accounting_evidence",
            summary="Stale legal/accounting evidence gets freshness downgrade.",
            relation="stale_warning",
            freshness_class=FRESHNESS_STALE_WARNING,
            reuse_score=0.97,
            semantic_similarity_score=0.98,
        ),
        _wow_record(
            record_id="quarantined_record",
            record_kind="quarantined_record",
            summary="Quarantine proximity blocks direct reuse.",
            relation="blocked_by_quarantine",
            quarantine_proximity=True,
            reuse_score=0.99,
        ),
        _wow_record(
            record_id="deadend_record",
            record_kind="deadend_record",
            summary="Deadend proximity blocks or downgrades reuse.",
            relation="blocked_by_deadend",
            deadend_proximity=True,
            reuse_score=0.99,
        ),
        _wow_record(
            record_id="wrong_domain_near_match",
            record_kind="wrong_domain_near_match",
            summary="Wrong-domain near match cannot be reused directly.",
            relation="conflicts_with_scope",
            wrong_domain_near_match=True,
            semantic_similarity_score=0.99,
            reuse_score=0.97,
        ),
        _wow_record(
            record_id="permission_trace_completed_action_attempt",
            record_kind="permission_trace_completed_action_attempt",
            summary="Permission trace cannot become completed action.",
            relation="blocked_permission_trace",
            contains_action_permission=True,
            reuse_score=0.99,
        ),
    )
