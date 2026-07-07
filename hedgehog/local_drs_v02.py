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
    quarantine_proximity: bool = False
    deadend_proximity: bool = False
    policy_ok: bool = True
    permission_ok: bool = False
    root_shortcut_allowed: bool = False
    reuse_score: float = 0.0
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


def validate_freshness_envelope(
    envelope: DRSFreshnessEnvelope | None,
) -> tuple[bool, tuple[str, ...]]:
    if envelope is None:
        return False, (REASON_MISSING_TIME_ENVELOPE,)

    invalid = not (
        _non_empty_string(envelope.physical_time)
        and _non_empty_string(envelope.knowledge_time)
        and _non_empty_string(envelope.event_time)
        and _non_empty_string(envelope.context_time)
    )
    invalid = invalid or not (
        envelope.ttl_seconds is None
        or (isinstance(envelope.ttl_seconds, int) and envelope.ttl_seconds >= 0)
    )
    if invalid:
        return False, (REASON_MISSING_TIME_ENVELOPE,)
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

    if record.conflict_pressure:
        _append_reason(reasons, REASON_CONFLICT_REQUIRES_RERUN_VALIDATION)
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
