"""Immutable G2-B query, resolution, and controlled-descent transport."""

from __future__ import annotations

from dataclasses import dataclass as _dataclass
from dataclasses import replace as _replace

from hedgehog.drs_g2b_compatibility_v01 import LegacyDRSProjectionV01
from hedgehog.drs_g2b_compatibility_v01 import (
    _FIELDS as _LEGACY_PROJECTION_FIELDS,
)
from hedgehog.drs_g2b_compatibility_v01 import (
    legacy_drs_projection_to_plain_data_v01,
    validate_legacy_drs_projection_v01,
)
from hedgehog.drs_semantic_address_v01 import (
    DRS_G2B_PROFILE_VERSION_V01 as _PROFILE_VERSION,
)
from hedgehog.drs_semantic_address_v01 import MeaningRecordV01
from hedgehog.drs_semantic_address_v01 import SemanticAddressV01
from hedgehog.drs_semantic_address_v01 import (
    _bounded_text,
    _canonical_json_bytes_v01,
    _canonical_plain_value,
    _dedupe,
    _domain_separated_sha256_hex_v01,
    _is_int64,
    _is_nonnegative_int,
    _is_reference,
    _is_sha256,
    _is_token,
    _plain_data_value,
    _reference_tuple_reasons,
    _safe_text_tuple_reasons,
    _sha256_tuple_reasons,
    _token_tuple_reasons,
    _typed_id_tuple_reasons,
    meaning_record_to_plain_data_v01,
    semantic_address_to_plain_data_v01,
    validate_meaning_record_v01,
    validate_semantic_address_v01,
)
from hedgehog.reuse_certificate_v01 import ReuseCertificateV01
from hedgehog.reuse_certificate_v01 import (
    RootShortcutAuthorizationProjectionV01,
)
from hedgehog.reuse_certificate_v01 import (
    _REUSE_CERTIFICATE_FIELDS,
    _ROOT_SHORTCUT_FIELDS,
    reuse_certificate_to_plain_data_v01,
    root_shortcut_authorization_projection_to_plain_data_v01,
    validate_reuse_certificate_v01,
    validate_root_shortcut_authorization_projection_v01,
)


DRS_QUERY_MODES_V01 = (
    "CURRENT_DECISION",
    "HISTORICAL_AS_OF",
    "AUDIT_REPLAY",
    "TREND_ANALYSIS",
    "MEMORY_CONTEXT_ONLY",
    "DIRECT_REUSE_CANDIDATE",
)
DRS_QUERY_STATES_V01 = (
    "FRESH_CANDIDATE",
    "STALE_CONTEXT_ONLY",
    "HISTORICAL_ONLY",
    "WARNING_ONLY",
    "RERUN_REQUIRED",
    "BLOCKED_BY_TIME",
    "BLOCKED_BY_SCOPE",
    "BLOCKED_BY_POLICY",
    "BLOCKED_BY_PROVENANCE",
    "BLOCKED_BY_CONFLICT",
    "BLOCKED_BY_QUARANTINE",
    "BLOCKED_BY_DEADEND",
    "BLOCKED_BY_REQUIRED_EVIDENCE",
    "BLOCKED_BY_FORBIDDEN_CHANGE",
    "BLOCKED_BY_ACTION_HISTORY",
    "BLOCKED_BY_ACTION_INTENT",
)
DRS_REUSE_CLASSES_V01 = (
    "CONTEXT_ONLY",
    "ANSWER_SHORTCUT",
    "ROUTE_SHORTCUT",
    "SEALED_REPLAY_SHORTCUT",
    "PROTOCOL_PREPARATION_SHORTCUT",
    "ACTION_SHORTCUT_NOT_ENABLED_IN_REFERENCE_KERNEL",
)
DRS_ENABLED_REUSE_CLASSES_V01 = (
    "CONTEXT_ONLY",
    "ANSWER_SHORTCUT",
)
DRS_MEMORY_DESCENT_CLASSES_V01 = (
    "SUMMARY_ONLY",
    "OPEN_ONE_ARTIFACT",
    "OPEN_LINEAGE_NEIGHBORHOOD",
    "OPEN_CONFLICT_SET",
    "OPEN_DEADEND_PROOF",
    "OPEN_FULL_TRACE",
)
DRS_REFERENCE_MEMORY_DESCENT_CEILINGS_V01 = (
    ("max_depth", 3),
    ("max_records_opened", 32),
    ("max_pointers_opened", 16),
    ("max_artifacts_opened", 4),
    ("max_bytes_opened", 1048576),
    ("max_lineage_edges", 32),
    ("max_conflict_records", 16),
)
DRS_RANKING_WEIGHTS_V01 = (
    ("semantic_similarity_units", 3000),
    ("freshness_units", 2000),
    ("source_authority_prior_units", 1500),
    ("lineage_proximity_units", 1000),
    ("historical_utility_units", 1500),
    ("gt_advisory_prior_units", 1000),
    ("conflict_penalty_units", 1500),
    ("risk_penalty_units", 1000),
    ("retrieval_cost_units", 500),
)

_EVALUATION_TIME_SOURCES = (
    "INJECTED_CURRENT_DECISION_TIME",
    "RECORDED_HISTORICAL_AS_OF_TIME",
    "RECORDED_AUDIT_REPLAY_TIME",
    "INJECTED_ANALYSIS_TIME",
)
_REUSE_INTENTS = (
    "CONTEXT",
    "INFORMATIONAL_SHORTCUT_CONSIDERATION",
    "WARNING_LOOKUP",
    "HISTORY_INSPECTION",
)
_TIME_AXES = (
    "PT",
    "KT",
    "ET",
    "CT",
    "TTL",
    "VALIDITY",
    "SOURCE_OBSERVED",
    "SOURCE_REPORTED",
    "SYSTEM_INGESTED",
    "SYSTEM_VERIFIED",
)
_INT64_MIN = -(2**63)
_INT64_MAX = 2**63 - 1

_QUERY_FIELDS = (
    "temporal_query_version",
    "query_id",
    "query_mode",
    "semantic_address_id",
    "scope_fingerprint",
    "as_of",
    "evaluation_time",
    "evaluation_time_source",
    "time_range_start",
    "time_range_end",
    "required_time_axes",
    "freshness_policy_id",
    "max_age_seconds",
    "domain",
    "risk_class",
    "reuse_intent",
    "requested_reuse_classes",
    "required_evidence_classes",
    "forbidden_changes",
    "policy_version",
    "schema_versions",
    "owning_local_root_id",
)
_QUERY_EVALUATION_FIELDS = (
    "query_evaluation_version",
    "query_evaluation_id",
    "query_id",
    "semantic_address_id",
    "meaning_record_id",
    "query_state",
    "evaluated_at",
    "evaluation_time_source",
    "temporal_hard_gate_passed",
    "validity_interval_passed",
    "ttl_freshness_passed",
    "required_time_axes_passed",
    "scope_passed",
    "lifecycle_passed",
    "policy_compatible",
    "schema_compatible",
    "provenance_passed",
    "authority_envelope_passed",
    "required_evidence_passed",
    "forbidden_changes_passed",
    "conflict_passed",
    "quarantine_passed",
    "deadend_passed",
    "action_intent_passed",
    "g2a_action_history_passed",
    "permission_boundary_passed",
    "current_freshness_units",
    "observed_evidence_fingerprint",
    "checked_dependency_fingerprint",
    "source_history_hash",
    "action_history_binding_id",
    "eligible_for_ranking",
    "reason_codes",
    "creates_authority",
    "creates_permission",
)
_CANDIDATE_FIELDS = (
    "resolution_candidate_version",
    "resolution_candidate_id",
    "query_id",
    "semantic_address_id",
    "meaning_record_id",
    "query_evaluation_id",
    "safe_summary",
    "evidence_ref_ids",
    "source_history_hash",
    "action_history_binding_id",
    "semantic_similarity_units",
    "freshness_units",
    "source_authority_prior_units",
    "lineage_proximity_units",
    "historical_utility_units",
    "gt_advisory_prior_units",
    "conflict_penalty_units",
    "risk_penalty_units",
    "retrieval_cost_units",
    "total_score_units",
    "eligible_for_ranking",
    "reason_codes",
    "creates_authority",
    "creates_permission",
    "creates_final_output",
)
_PLAN_FIELDS = (
    "retrieval_plan_version",
    "retrieval_plan_id",
    "query_id",
    "semantic_address_id",
    "proposed_record_ids",
    "proposed_memory_pointer_ids",
    "proposed_artifact_pointer_ids",
    "requested_descent_class",
    "proposed_budget_id",
    "required_access_policy_ids",
    "reason_codes",
    "root_approval_required",
    "creates_authority",
    "creates_permission",
    "executes_read",
)
_BUDGET_FIELDS = (
    "memory_descent_budget_version",
    "memory_descent_budget_id",
    "max_depth",
    "max_records_opened",
    "max_pointers_opened",
    "max_artifacts_opened",
    "max_bytes_opened",
    "max_lineage_edges",
    "max_conflict_records",
)
_REQUEST_FIELDS = (
    "memory_descent_request_version",
    "memory_descent_request_id",
    "retrieval_plan_id",
    "query_id",
    "owning_local_root_id",
    "root_kernel_id",
    "root_decision_input_id",
    "root_decision_id",
    "root_decision_hash",
    "requested_descent_class",
    "approved_descent_class",
    "proposed_budget_id",
    "approved_budget",
    "approved_record_ids",
    "approved_memory_pointer_ids",
    "approved_artifact_pointer_ids",
    "root_approved",
    "reason_codes",
    "creates_permission",
    "creates_authority",
)
_RESULT_FIELDS = (
    "memory_descent_result_version",
    "memory_descent_result_id",
    "memory_descent_request_id",
    "retrieval_plan_id",
    "query_id",
    "executed_descent_class",
    "applied_budget_id",
    "opened_record_ids",
    "opened_memory_pointer_ids",
    "opened_artifact_pointer_ids",
    "traversed_lineage_edge_ids",
    "opened_conflict_record_ids",
    "depth_reached",
    "records_opened",
    "pointers_opened",
    "artifacts_opened",
    "bytes_opened",
    "lineage_edges_traversed",
    "conflict_records_opened",
    "safe_summaries",
    "opened_payload_fingerprints",
    "limits_respected",
    "reason_codes",
    "creates_authority",
    "creates_permission",
    "real_world_effects_count",
)
_REPORT_FIELDS = (
    "report_version",
    "report_id",
    "semantic_address",
    "query",
    "source_projections",
    "source_records",
    "query_evaluations",
    "eligible_candidates",
    "ranked_candidate_ids",
    "selected_candidate_id",
    "retrieval_plan",
    "memory_descent_result",
    "root_shortcut_projection",
    "reuse_certificate",
    "context_only_record_ids",
    "historical_only_record_ids",
    "warning_only_record_ids",
    "rerun_required_record_ids",
    "blocked_record_ids",
    "persistent_records_unchanged",
    "provider_calls",
    "network_calls",
    "gemini_calls",
    "external_drs_calls",
    "connector_calls",
    "real_world_effects_count",
    "final_status",
    "reason_codes",
)
_IDENTITY_PROFILES = (
    ("DRSTemporalQueryV01", "query_id", "hedgehog:drs:temporal_query:v01", "drsquery_v01:", _QUERY_FIELDS),
    ("QueryEvaluationStateV01", "query_evaluation_id", "hedgehog:drs:query_evaluation:v01", "drsqeval_v01:", _QUERY_EVALUATION_FIELDS),
    ("ResolutionCandidateV01", "resolution_candidate_id", "hedgehog:drs:resolution_candidate:v01", "drscandidate_v01:", _CANDIDATE_FIELDS),
    ("RetrievalPlanV01", "retrieval_plan_id", "hedgehog:drs:retrieval_plan:v01", "drsplan_v01:", _PLAN_FIELDS),
    ("MemoryDescentBudgetV01", "memory_descent_budget_id", "hedgehog:drs:memory_descent_budget:v01", "drsbudget_v01:", _BUDGET_FIELDS),
    ("MemoryDescentRequestV01", "memory_descent_request_id", "hedgehog:drs:memory_descent_request:v01", "drsdescentreq_v01:", _REQUEST_FIELDS),
    ("MemoryDescentResultV01", "memory_descent_result_id", "hedgehog:drs:memory_descent_result:v01", "drsdescentres_v01:", _RESULT_FIELDS),
    ("DRSResolutionReportV01", "report_id", "hedgehog:drs:resolution_report:v01", "drsreport_v01:", _REPORT_FIELDS),
)


@_dataclass(frozen=True)
class DRSTemporalQueryV01:
    temporal_query_version: str
    query_id: str
    query_mode: str
    semantic_address_id: str
    scope_fingerprint: str
    as_of: int
    evaluation_time: int
    evaluation_time_source: str
    time_range_start: int
    time_range_end: int
    required_time_axes: tuple[str, ...]
    freshness_policy_id: str
    max_age_seconds: int
    domain: str
    risk_class: str
    reuse_intent: str
    requested_reuse_classes: tuple[str, ...]
    required_evidence_classes: tuple[str, ...]
    forbidden_changes: tuple[str, ...]
    policy_version: str
    schema_versions: tuple[str, ...]
    owning_local_root_id: str


@_dataclass(frozen=True)
class QueryEvaluationStateV01:
    query_evaluation_version: str
    query_evaluation_id: str
    query_id: str
    semantic_address_id: str
    meaning_record_id: str
    query_state: str
    evaluated_at: int
    evaluation_time_source: str
    temporal_hard_gate_passed: bool
    validity_interval_passed: bool
    ttl_freshness_passed: bool
    required_time_axes_passed: bool
    scope_passed: bool
    lifecycle_passed: bool
    policy_compatible: bool
    schema_compatible: bool
    provenance_passed: bool
    authority_envelope_passed: bool
    required_evidence_passed: bool
    forbidden_changes_passed: bool
    conflict_passed: bool
    quarantine_passed: bool
    deadend_passed: bool
    action_intent_passed: bool
    g2a_action_history_passed: bool
    permission_boundary_passed: bool
    current_freshness_units: int
    observed_evidence_fingerprint: str
    checked_dependency_fingerprint: str
    source_history_hash: str
    action_history_binding_id: str | None
    eligible_for_ranking: bool
    reason_codes: tuple[str, ...]
    creates_authority: bool
    creates_permission: bool


@_dataclass(frozen=True)
class ResolutionCandidateV01:
    resolution_candidate_version: str
    resolution_candidate_id: str
    query_id: str
    semantic_address_id: str
    meaning_record_id: str
    query_evaluation_id: str
    safe_summary: str
    evidence_ref_ids: tuple[str, ...]
    source_history_hash: str
    action_history_binding_id: str | None
    semantic_similarity_units: int
    freshness_units: int
    source_authority_prior_units: int
    lineage_proximity_units: int
    historical_utility_units: int
    gt_advisory_prior_units: int
    conflict_penalty_units: int
    risk_penalty_units: int
    retrieval_cost_units: int
    total_score_units: int
    eligible_for_ranking: bool
    reason_codes: tuple[str, ...]
    creates_authority: bool
    creates_permission: bool
    creates_final_output: bool


@_dataclass(frozen=True)
class RetrievalPlanV01:
    retrieval_plan_version: str
    retrieval_plan_id: str
    query_id: str
    semantic_address_id: str
    proposed_record_ids: tuple[str, ...]
    proposed_memory_pointer_ids: tuple[str, ...]
    proposed_artifact_pointer_ids: tuple[str, ...]
    requested_descent_class: str
    proposed_budget_id: str
    required_access_policy_ids: tuple[str, ...]
    reason_codes: tuple[str, ...]
    root_approval_required: bool
    creates_authority: bool
    creates_permission: bool
    executes_read: bool


@_dataclass(frozen=True)
class MemoryDescentBudgetV01:
    memory_descent_budget_version: str
    memory_descent_budget_id: str
    max_depth: int
    max_records_opened: int
    max_pointers_opened: int
    max_artifacts_opened: int
    max_bytes_opened: int
    max_lineage_edges: int
    max_conflict_records: int


@_dataclass(frozen=True)
class MemoryDescentRequestV01:
    memory_descent_request_version: str
    memory_descent_request_id: str
    retrieval_plan_id: str
    query_id: str
    owning_local_root_id: str
    root_kernel_id: str
    root_decision_input_id: str
    root_decision_id: str
    root_decision_hash: str
    requested_descent_class: str
    approved_descent_class: str
    proposed_budget_id: str
    approved_budget: MemoryDescentBudgetV01
    approved_record_ids: tuple[str, ...]
    approved_memory_pointer_ids: tuple[str, ...]
    approved_artifact_pointer_ids: tuple[str, ...]
    root_approved: bool
    reason_codes: tuple[str, ...]
    creates_permission: bool
    creates_authority: bool


@_dataclass(frozen=True)
class MemoryDescentResultV01:
    memory_descent_result_version: str
    memory_descent_result_id: str
    memory_descent_request_id: str
    retrieval_plan_id: str
    query_id: str
    executed_descent_class: str
    applied_budget_id: str
    opened_record_ids: tuple[str, ...]
    opened_memory_pointer_ids: tuple[str, ...]
    opened_artifact_pointer_ids: tuple[str, ...]
    traversed_lineage_edge_ids: tuple[str, ...]
    opened_conflict_record_ids: tuple[str, ...]
    depth_reached: int
    records_opened: int
    pointers_opened: int
    artifacts_opened: int
    bytes_opened: int
    lineage_edges_traversed: int
    conflict_records_opened: int
    safe_summaries: tuple[str, ...]
    opened_payload_fingerprints: tuple[str, ...]
    limits_respected: bool
    reason_codes: tuple[str, ...]
    creates_authority: bool
    creates_permission: bool
    real_world_effects_count: int


@_dataclass(frozen=True)
class DRSResolutionReportV01:
    report_version: str
    report_id: str
    semantic_address: SemanticAddressV01
    query: DRSTemporalQueryV01
    source_projections: tuple[LegacyDRSProjectionV01, ...]
    source_records: tuple[MeaningRecordV01, ...]
    query_evaluations: tuple[QueryEvaluationStateV01, ...]
    eligible_candidates: tuple[ResolutionCandidateV01, ...]
    ranked_candidate_ids: tuple[str, ...]
    selected_candidate_id: str | None
    retrieval_plan: RetrievalPlanV01
    memory_descent_result: MemoryDescentResultV01 | None
    root_shortcut_projection: RootShortcutAuthorizationProjectionV01 | None
    reuse_certificate: ReuseCertificateV01 | None
    context_only_record_ids: tuple[str, ...]
    historical_only_record_ids: tuple[str, ...]
    warning_only_record_ids: tuple[str, ...]
    rerun_required_record_ids: tuple[str, ...]
    blocked_record_ids: tuple[str, ...]
    persistent_records_unchanged: bool
    provider_calls: int
    network_calls: int
    gemini_calls: int
    external_drs_calls: int
    connector_calls: int
    real_world_effects_count: int
    final_status: str
    reason_codes: tuple[str, ...]


def _profile(type_name: str) -> tuple[str, str, str, tuple[str, ...]]:
    for name, identity_field, domain, prefix, fields in _IDENTITY_PROFILES:
        if name == type_name:
            return identity_field, domain, prefix, fields
    raise ValueError("drs_identity_profile_invalid")


def _identity_plain(value: object) -> object:
    if type(value) is tuple:
        return [_identity_plain(item) for item in value]
    if type(value) is DRSTemporalQueryV01:
        return [_identity_plain(getattr(value, name)) for name in _QUERY_FIELDS]
    if type(value) is QueryEvaluationStateV01:
        return [
            _identity_plain(getattr(value, name))
            for name in _QUERY_EVALUATION_FIELDS
        ]
    if type(value) is ResolutionCandidateV01:
        return [_identity_plain(getattr(value, name)) for name in _CANDIDATE_FIELDS]
    if type(value) is RetrievalPlanV01:
        return [_identity_plain(getattr(value, name)) for name in _PLAN_FIELDS]
    if type(value) is MemoryDescentBudgetV01:
        return [_identity_plain(getattr(value, name)) for name in _BUDGET_FIELDS]
    if type(value) is MemoryDescentRequestV01:
        return [_identity_plain(getattr(value, name)) for name in _REQUEST_FIELDS]
    if type(value) is MemoryDescentResultV01:
        return [_identity_plain(getattr(value, name)) for name in _RESULT_FIELDS]
    if type(value) is DRSResolutionReportV01:
        return [_identity_plain(getattr(value, name)) for name in _REPORT_FIELDS]
    if type(value) is LegacyDRSProjectionV01:
        return [
            _identity_plain(getattr(value, name))
            for name in _LEGACY_PROJECTION_FIELDS
        ]
    if type(value) is RootShortcutAuthorizationProjectionV01:
        return [_identity_plain(getattr(value, name)) for name in _ROOT_SHORTCUT_FIELDS]
    if type(value) is ReuseCertificateV01:
        return [_identity_plain(getattr(value, name)) for name in _REUSE_CERTIFICATE_FIELDS]
    return _canonical_plain_value(value)


def _plain_value(value: object) -> object:
    if type(value) is tuple:
        return [_plain_value(item) for item in value]
    if type(value) is DRSTemporalQueryV01:
        return {name: _plain_value(getattr(value, name)) for name in _QUERY_FIELDS}
    if type(value) is QueryEvaluationStateV01:
        return {
            name: _plain_value(getattr(value, name))
            for name in _QUERY_EVALUATION_FIELDS
        }
    if type(value) is ResolutionCandidateV01:
        return {name: _plain_value(getattr(value, name)) for name in _CANDIDATE_FIELDS}
    if type(value) is RetrievalPlanV01:
        return {name: _plain_value(getattr(value, name)) for name in _PLAN_FIELDS}
    if type(value) is MemoryDescentBudgetV01:
        return {name: _plain_value(getattr(value, name)) for name in _BUDGET_FIELDS}
    if type(value) is MemoryDescentRequestV01:
        return {name: _plain_value(getattr(value, name)) for name in _REQUEST_FIELDS}
    if type(value) is MemoryDescentResultV01:
        return {name: _plain_value(getattr(value, name)) for name in _RESULT_FIELDS}
    if type(value) is DRSResolutionReportV01:
        return {name: _plain_value(getattr(value, name)) for name in _REPORT_FIELDS}
    if type(value) is SemanticAddressV01:
        return semantic_address_to_plain_data_v01(value)
    if type(value) is MeaningRecordV01:
        return meaning_record_to_plain_data_v01(value)
    if type(value) is LegacyDRSProjectionV01:
        return legacy_drs_projection_to_plain_data_v01(value)
    if type(value) is RootShortcutAuthorizationProjectionV01:
        return root_shortcut_authorization_projection_to_plain_data_v01(value)
    if type(value) is ReuseCertificateV01:
        return reuse_certificate_to_plain_data_v01(value)
    return _plain_data_value(value)


def _identity(value: object, type_name: str) -> str:
    identity_field, domain, prefix, fields = _profile(type_name)
    material = [
        _identity_plain(getattr(value, name))
        for name in fields
        if name != identity_field
    ]
    digest = _domain_separated_sha256_hex_v01(
        domain=domain,
        payload=_canonical_json_bytes_v01(material),
    )
    return prefix + digest


def _id_reason(value: object, type_name: str) -> str | None:
    identity_field, _, prefix, _ = _profile(type_name)
    actual = getattr(value, identity_field)
    if (
        type(actual) is not str
        or not actual.startswith(prefix)
        or len(actual) != len(prefix) + 64
        or not _is_sha256(actual[len(prefix):])
        or actual != _identity(value, type_name)
    ):
        return "drs_identity_invalid"
    return None


def _finish(
    provisional: object,
    *,
    type_name: str,
    reasons: tuple[str, ...],
    validator: object,
) -> object:
    if reasons:
        raise ValueError(reasons[0]) from None
    identity_field, _, _, _ = _profile(type_name)
    final = _replace(provisional, **{identity_field: _identity(provisional, type_name)})
    if not callable(validator):
        raise ValueError("drs_builder_invalid") from None
    valid, final_reasons = validator(final)
    if not valid:
        raise ValueError(final_reasons[0]) from None
    return final


def _version_reasons(value: object) -> list[str]:
    if type(value) is not str:
        return ["drs_exact_type_required"]
    if value != _PROFILE_VERSION:
        return ["drs_schema_version_mismatch"]
    return []


def _prefixed_id(value: object, prefix: str) -> bool:
    return (
        type(value) is str
        and value.startswith(prefix)
        and len(value) == len(prefix) + 64
        and _is_sha256(value[len(prefix):])
    )


def _exact_bool_reasons(values: tuple[object, ...]) -> list[str]:
    return [] if all(type(value) is bool for value in values) else ["drs_exact_type_required"]


def _query_reasons(value: object, *, check_identity: bool) -> tuple[str, ...]:
    if type(value) is not DRSTemporalQueryV01:
        return ("drs_exact_type_required",)
    reasons = _version_reasons(value.temporal_query_version)
    if type(value.query_mode) is not str or value.query_mode not in DRS_QUERY_MODES_V01:
        reasons.append("drs_query_mode_invalid")
    if not _prefixed_id(value.semantic_address_id, "drsaddr_v01:"):
        reasons.append("drs_address_scope_mismatch")
    if not _is_sha256(value.scope_fingerprint):
        reasons.append("drs_sha256_invalid")
    for item in (
        value.as_of,
        value.evaluation_time,
        value.time_range_start,
        value.time_range_end,
    ):
        if not _is_int64(item):
            reasons.append("drs_time_type_invalid")
    if (
        type(value.time_range_start) is int
        and type(value.as_of) is int
        and type(value.time_range_end) is int
        and not (value.time_range_start <= value.as_of < value.time_range_end)
    ):
        reasons.append("drs_time_validity_interval_invalid")
    if type(value.evaluation_time_source) is not str or value.evaluation_time_source not in _EVALUATION_TIME_SOURCES:
        reasons.append("drs_evaluation_time_source_invalid")
    reasons.extend(
        _token_tuple_reasons(value.required_time_axes, maximum_items=16)
    )
    if type(value.required_time_axes) is tuple and any(
        item not in _TIME_AXES for item in value.required_time_axes if type(item) is str
    ):
        reasons.append("drs_time_axis_missing")
    if not _is_reference(value.freshness_policy_id):
        reasons.append("drs_freshness_policy_invalid")
    if not _is_nonnegative_int(value.max_age_seconds):
        reasons.append("drs_exact_int_required")
    for item in (value.domain, value.risk_class, value.policy_version):
        if not _is_token(item):
            reasons.append("drs_query_component_invalid")
    if type(value.reuse_intent) is not str or value.reuse_intent not in _REUSE_INTENTS:
        reasons.append("drs_query_component_invalid")
    reasons.extend(
        _token_tuple_reasons(
            value.requested_reuse_classes, maximum_items=16
        )
    )
    if type(value.requested_reuse_classes) is tuple and any(
        item not in DRS_REUSE_CLASSES_V01
        for item in value.requested_reuse_classes
        if type(item) is str
    ):
        reasons.append("drs_reuse_class_invalid")
    reasons.extend(
        _token_tuple_reasons(
            value.required_evidence_classes, maximum_items=32
        )
    )
    reasons.extend(
        _token_tuple_reasons(value.forbidden_changes, maximum_items=32)
    )
    reasons.extend(
        _token_tuple_reasons(value.schema_versions, maximum_items=32)
    )
    if not _is_reference(value.owning_local_root_id):
        reasons.append("drs_root_owner_mismatch")
    if check_identity and not reasons:
        reason = _id_reason(value, "DRSTemporalQueryV01")
        if reason:
            reasons.append(reason)
    return _dedupe(reasons)


def build_drs_temporal_query_v01(
    *,
    query_mode: str,
    semantic_address_id: str,
    scope_fingerprint: str,
    as_of: int,
    evaluation_time: int,
    evaluation_time_source: str,
    time_range_start: int,
    time_range_end: int,
    required_time_axes: tuple[str, ...],
    freshness_policy_id: str,
    max_age_seconds: int,
    domain: str,
    risk_class: str,
    reuse_intent: str,
    requested_reuse_classes: tuple[str, ...],
    required_evidence_classes: tuple[str, ...],
    forbidden_changes: tuple[str, ...],
    policy_version: str,
    schema_versions: tuple[str, ...],
    owning_local_root_id: str,
) -> DRSTemporalQueryV01:
    try:
        provisional = DRSTemporalQueryV01(
            temporal_query_version=_PROFILE_VERSION,
            query_id="drsquery_v01:" + "0" * 64,
            query_mode=query_mode,
            semantic_address_id=semantic_address_id,
            scope_fingerprint=scope_fingerprint,
            as_of=as_of,
            evaluation_time=evaluation_time,
            evaluation_time_source=evaluation_time_source,
            time_range_start=time_range_start,
            time_range_end=time_range_end,
            required_time_axes=required_time_axes,
            freshness_policy_id=freshness_policy_id,
            max_age_seconds=max_age_seconds,
            domain=domain,
            risk_class=risk_class,
            reuse_intent=reuse_intent,
            requested_reuse_classes=requested_reuse_classes,
            required_evidence_classes=required_evidence_classes,
            forbidden_changes=forbidden_changes,
            policy_version=policy_version,
            schema_versions=schema_versions,
            owning_local_root_id=owning_local_root_id,
        )
        return _finish(provisional, type_name="DRSTemporalQueryV01", reasons=_query_reasons(provisional, check_identity=False), validator=validate_drs_temporal_query_v01)
    except ValueError as exc:
        reason = str(exc)
        raise ValueError(reason if reason.startswith("drs_") else "drs_temporal_query_invalid") from None
    except Exception:
        raise ValueError("drs_temporal_query_invalid") from None


def validate_drs_temporal_query_v01(value: object) -> tuple[bool, tuple[str, ...]]:
    try:
        reasons = _query_reasons(value, check_identity=True)
        return not reasons, reasons
    except Exception:
        return False, ("drs_temporal_query_invalid",)


def drs_temporal_query_to_plain_data_v01(value: object) -> dict[str, object]:
    if type(value) is not DRSTemporalQueryV01:
        raise ValueError("drs_exact_type_required") from None
    return {name: _plain_value(getattr(value, name)) for name in _QUERY_FIELDS}


def _query_evaluation_reasons(value: object, *, check_identity: bool) -> tuple[str, ...]:
    if type(value) is not QueryEvaluationStateV01:
        return ("drs_exact_type_required",)
    reasons = _version_reasons(value.query_evaluation_version)
    for item, prefix in (
        (value.query_id, "drsquery_v01:"),
        (value.semantic_address_id, "drsaddr_v01:"),
        (value.meaning_record_id, "drsmeaning_v01:"),
    ):
        if not _prefixed_id(item, prefix):
            reasons.append("drs_query_evaluation_binding_invalid")
    if type(value.query_state) is not str or value.query_state not in DRS_QUERY_STATES_V01:
        reasons.append("drs_query_state_persistence_forbidden")
    if not _is_int64(value.evaluated_at):
        reasons.append("drs_time_type_invalid")
    if type(value.evaluation_time_source) is not str or value.evaluation_time_source not in _EVALUATION_TIME_SOURCES:
        reasons.append("drs_evaluation_time_source_invalid")
    gates = (
        value.temporal_hard_gate_passed,
        value.validity_interval_passed,
        value.ttl_freshness_passed,
        value.required_time_axes_passed,
        value.scope_passed,
        value.lifecycle_passed,
        value.policy_compatible,
        value.schema_compatible,
        value.provenance_passed,
        value.authority_envelope_passed,
        value.required_evidence_passed,
        value.forbidden_changes_passed,
        value.conflict_passed,
        value.quarantine_passed,
        value.deadend_passed,
        value.action_intent_passed,
        value.g2a_action_history_passed,
        value.permission_boundary_passed,
    )
    reasons.extend(_exact_bool_reasons(gates))
    if type(value.current_freshness_units) is not int or not 0 <= value.current_freshness_units <= 10000:
        reasons.append("drs_exact_int_required")
    for digest in (
        value.observed_evidence_fingerprint,
        value.checked_dependency_fingerprint,
        value.source_history_hash,
    ):
        if not _is_sha256(digest):
            reasons.append("drs_sha256_invalid")
    if value.action_history_binding_id is not None and not _prefixed_id(
        value.action_history_binding_id, "drsg2ahistory_v01:"
    ):
        reasons.append("drs_action_history_binding_invalid")
    if type(value.eligible_for_ranking) is not bool:
        reasons.append("drs_exact_type_required")
    reasons.extend(
        _token_tuple_reasons(value.reason_codes, maximum_items=32)
    )
    if value.eligible_for_ranking is True:
        if not all(item is True for item in gates) or value.query_state != "FRESH_CANDIDATE" or value.reason_codes:
            reasons.append("drs_eligibility_transport_invalid")
    elif type(value.eligible_for_ranking) is bool and not value.reason_codes:
        reasons.append("drs_eligibility_transport_invalid")
    if value.creates_authority is not False:
        reasons.append("drs_non_authority_law_invalid")
    if value.creates_permission is not False:
        reasons.append("drs_non_permission_law_invalid")
    if check_identity and not reasons:
        reason = _id_reason(value, "QueryEvaluationStateV01")
        if reason:
            reasons.append(reason)
    return _dedupe(reasons)


def build_query_evaluation_state_v01(
    *,
    query_id: str,
    semantic_address_id: str,
    meaning_record_id: str,
    query_state: str,
    evaluated_at: int,
    evaluation_time_source: str,
    temporal_hard_gate_passed: bool,
    validity_interval_passed: bool,
    ttl_freshness_passed: bool,
    required_time_axes_passed: bool,
    scope_passed: bool,
    lifecycle_passed: bool,
    policy_compatible: bool,
    schema_compatible: bool,
    provenance_passed: bool,
    authority_envelope_passed: bool,
    required_evidence_passed: bool,
    forbidden_changes_passed: bool,
    conflict_passed: bool,
    quarantine_passed: bool,
    deadend_passed: bool,
    action_intent_passed: bool,
    g2a_action_history_passed: bool,
    permission_boundary_passed: bool,
    current_freshness_units: int,
    observed_evidence_fingerprint: str,
    checked_dependency_fingerprint: str,
    source_history_hash: str,
    action_history_binding_id: str | None,
    eligible_for_ranking: bool,
    reason_codes: tuple[str, ...],
) -> QueryEvaluationStateV01:
    try:
        provisional = QueryEvaluationStateV01(
            query_evaluation_version=_PROFILE_VERSION,
            query_evaluation_id="drsqeval_v01:" + "0" * 64,
            query_id=query_id,
            semantic_address_id=semantic_address_id,
            meaning_record_id=meaning_record_id,
            query_state=query_state,
            evaluated_at=evaluated_at,
            evaluation_time_source=evaluation_time_source,
            temporal_hard_gate_passed=temporal_hard_gate_passed,
            validity_interval_passed=validity_interval_passed,
            ttl_freshness_passed=ttl_freshness_passed,
            required_time_axes_passed=required_time_axes_passed,
            scope_passed=scope_passed,
            lifecycle_passed=lifecycle_passed,
            policy_compatible=policy_compatible,
            schema_compatible=schema_compatible,
            provenance_passed=provenance_passed,
            authority_envelope_passed=authority_envelope_passed,
            required_evidence_passed=required_evidence_passed,
            forbidden_changes_passed=forbidden_changes_passed,
            conflict_passed=conflict_passed,
            quarantine_passed=quarantine_passed,
            deadend_passed=deadend_passed,
            action_intent_passed=action_intent_passed,
            g2a_action_history_passed=g2a_action_history_passed,
            permission_boundary_passed=permission_boundary_passed,
            current_freshness_units=current_freshness_units,
            observed_evidence_fingerprint=observed_evidence_fingerprint,
            checked_dependency_fingerprint=checked_dependency_fingerprint,
            source_history_hash=source_history_hash,
            action_history_binding_id=action_history_binding_id,
            eligible_for_ranking=eligible_for_ranking,
            reason_codes=reason_codes,
            creates_authority=False,
            creates_permission=False,
        )
        return _finish(provisional, type_name="QueryEvaluationStateV01", reasons=_query_evaluation_reasons(provisional, check_identity=False), validator=validate_query_evaluation_state_v01)
    except ValueError as exc:
        reason = str(exc)
        raise ValueError(reason if reason.startswith("drs_") else "drs_query_evaluation_invalid") from None
    except Exception:
        raise ValueError("drs_query_evaluation_invalid") from None


def validate_query_evaluation_state_v01(value: object) -> tuple[bool, tuple[str, ...]]:
    try:
        reasons = _query_evaluation_reasons(value, check_identity=True)
        return not reasons, reasons
    except Exception:
        return False, ("drs_query_evaluation_invalid",)


def query_evaluation_state_to_plain_data_v01(value: object) -> dict[str, object]:
    if type(value) is not QueryEvaluationStateV01:
        raise ValueError("drs_exact_type_required") from None
    return {name: _plain_value(getattr(value, name)) for name in _QUERY_EVALUATION_FIELDS}


def _score_total(value: ResolutionCandidateV01) -> int:
    return (
        3000 * value.semantic_similarity_units
        + 2000 * value.freshness_units
        + 1500 * value.source_authority_prior_units
        + 1000 * value.lineage_proximity_units
        + 1500 * value.historical_utility_units
        + 1000 * value.gt_advisory_prior_units
        - 1500 * value.conflict_penalty_units
        - 1000 * value.risk_penalty_units
        - 500 * value.retrieval_cost_units
    )


def _candidate_reasons(value: object, *, check_identity: bool) -> tuple[str, ...]:
    if type(value) is not ResolutionCandidateV01:
        return ("drs_exact_type_required",)
    reasons = _version_reasons(value.resolution_candidate_version)
    for item, prefix in (
        (value.query_id, "drsquery_v01:"),
        (value.semantic_address_id, "drsaddr_v01:"),
        (value.meaning_record_id, "drsmeaning_v01:"),
        (value.query_evaluation_id, "drsqeval_v01:"),
    ):
        if not _prefixed_id(item, prefix):
            reasons.append("drs_resolution_candidate_binding_invalid")
    reason = _bounded_text(value.safe_summary, maximum=1024)
    if reason:
        reasons.append(reason)
    reasons.extend(
        _reference_tuple_reasons(value.evidence_ref_ids, maximum_items=64)
    )
    if not _is_sha256(value.source_history_hash):
        reasons.append("drs_sha256_invalid")
    if value.action_history_binding_id is not None and not _prefixed_id(value.action_history_binding_id, "drsg2ahistory_v01:"):
        reasons.append("drs_action_history_binding_invalid")
    components = (
        value.semantic_similarity_units,
        value.freshness_units,
        value.source_authority_prior_units,
        value.lineage_proximity_units,
        value.historical_utility_units,
        value.gt_advisory_prior_units,
        value.conflict_penalty_units,
        value.risk_penalty_units,
        value.retrieval_cost_units,
    )
    if any(type(item) is not int or not 0 <= item <= 10000 for item in components):
        reasons.append("drs_exact_int_required")
    if type(value.total_score_units) is not int or not _INT64_MIN <= value.total_score_units <= _INT64_MAX:
        reasons.append("drs_exact_int_required")
    elif all(type(item) is int for item in components) and value.total_score_units != _score_total(value):
        reasons.append("drs_ranking_score_invalid")
    if value.eligible_for_ranking is not True:
        reasons.append("drs_eligibility_transport_invalid")
    if type(value.reason_codes) is not tuple or value.reason_codes:
        reasons.append("drs_eligibility_transport_invalid")
    if value.creates_authority is not False or value.creates_permission is not False or value.creates_final_output is not False:
        reasons.append("drs_non_authority_law_invalid")
    if check_identity and not reasons:
        reason = _id_reason(value, "ResolutionCandidateV01")
        if reason:
            reasons.append(reason)
    return _dedupe(reasons)


def build_resolution_candidate_v01(
    *,
    query_id: str,
    semantic_address_id: str,
    meaning_record_id: str,
    query_evaluation_id: str,
    safe_summary: str,
    evidence_ref_ids: tuple[str, ...],
    source_history_hash: str,
    action_history_binding_id: str | None,
    semantic_similarity_units: int,
    freshness_units: int,
    source_authority_prior_units: int,
    lineage_proximity_units: int,
    historical_utility_units: int,
    gt_advisory_prior_units: int,
    conflict_penalty_units: int,
    risk_penalty_units: int,
    retrieval_cost_units: int,
) -> ResolutionCandidateV01:
    try:
        provisional = ResolutionCandidateV01(
            resolution_candidate_version=_PROFILE_VERSION,
            resolution_candidate_id="drscandidate_v01:" + "0" * 64,
            query_id=query_id,
            semantic_address_id=semantic_address_id,
            meaning_record_id=meaning_record_id,
            query_evaluation_id=query_evaluation_id,
            safe_summary=safe_summary,
            evidence_ref_ids=evidence_ref_ids,
            source_history_hash=source_history_hash,
            action_history_binding_id=action_history_binding_id,
            semantic_similarity_units=semantic_similarity_units,
            freshness_units=freshness_units,
            source_authority_prior_units=source_authority_prior_units,
            lineage_proximity_units=lineage_proximity_units,
            historical_utility_units=historical_utility_units,
            gt_advisory_prior_units=gt_advisory_prior_units,
            conflict_penalty_units=conflict_penalty_units,
            risk_penalty_units=risk_penalty_units,
            retrieval_cost_units=retrieval_cost_units,
            total_score_units=0,
            eligible_for_ranking=True,
            reason_codes=(),
            creates_authority=False,
            creates_permission=False,
            creates_final_output=False,
        )
        provisional = _replace(provisional, total_score_units=_score_total(provisional))
        return _finish(provisional, type_name="ResolutionCandidateV01", reasons=_candidate_reasons(provisional, check_identity=False), validator=validate_resolution_candidate_v01)
    except ValueError as exc:
        reason = str(exc)
        raise ValueError(reason if reason.startswith("drs_") else "drs_resolution_candidate_invalid") from None
    except Exception:
        raise ValueError("drs_resolution_candidate_invalid") from None


def validate_resolution_candidate_v01(value: object) -> tuple[bool, tuple[str, ...]]:
    try:
        reasons = _candidate_reasons(value, check_identity=True)
        return not reasons, reasons
    except Exception:
        return False, ("drs_resolution_candidate_invalid",)


def resolution_candidate_to_plain_data_v01(value: object) -> dict[str, object]:
    if type(value) is not ResolutionCandidateV01:
        raise ValueError("drs_exact_type_required") from None
    return {name: _plain_value(getattr(value, name)) for name in _CANDIDATE_FIELDS}


def _plan_reasons(value: object, *, check_identity: bool) -> tuple[str, ...]:
    if type(value) is not RetrievalPlanV01:
        return ("drs_exact_type_required",)
    reasons = _version_reasons(value.retrieval_plan_version)
    if not _prefixed_id(value.query_id, "drsquery_v01:") or not _prefixed_id(value.semantic_address_id, "drsaddr_v01:"):
        reasons.append("drs_retrieval_plan_binding_invalid")
    for tuple_value, prefix in (
        (value.proposed_record_ids, "drsmeaning_v01:"),
        (value.proposed_memory_pointer_ids, "drsmem_v01:"),
        (value.proposed_artifact_pointer_ids, "drsart_v01:"),
    ):
        reasons.extend(
            _typed_id_tuple_reasons(
                tuple_value,
                prefix=prefix,
                maximum_items=64,
                invalid_reason="drs_retrieval_plan_binding_invalid",
            )
        )
    reasons.extend(
        _reference_tuple_reasons(
            value.required_access_policy_ids, maximum_items=64
        )
    )
    reasons.extend(
        _token_tuple_reasons(value.reason_codes, maximum_items=64)
    )
    if type(value.requested_descent_class) is not str or value.requested_descent_class not in DRS_MEMORY_DESCENT_CLASSES_V01:
        reasons.append("drs_memory_descent_class_invalid")
    if not _prefixed_id(value.proposed_budget_id, "drsbudget_v01:"):
        reasons.append("drs_memory_descent_budget_invalid")
    if value.root_approval_required is not True or value.creates_authority is not False or value.creates_permission is not False or value.executes_read is not False:
        reasons.append("drs_retrieval_plan_non_execution_invalid")
    if check_identity and not reasons:
        reason = _id_reason(value, "RetrievalPlanV01")
        if reason:
            reasons.append(reason)
    return _dedupe(reasons)


def build_retrieval_plan_v01(
    *,
    query_id: str,
    semantic_address_id: str,
    proposed_record_ids: tuple[str, ...],
    proposed_memory_pointer_ids: tuple[str, ...],
    proposed_artifact_pointer_ids: tuple[str, ...],
    requested_descent_class: str,
    proposed_budget_id: str,
    required_access_policy_ids: tuple[str, ...],
    reason_codes: tuple[str, ...],
) -> RetrievalPlanV01:
    try:
        provisional = RetrievalPlanV01(
            retrieval_plan_version=_PROFILE_VERSION,
            retrieval_plan_id="drsplan_v01:" + "0" * 64,
            query_id=query_id,
            semantic_address_id=semantic_address_id,
            proposed_record_ids=proposed_record_ids,
            proposed_memory_pointer_ids=proposed_memory_pointer_ids,
            proposed_artifact_pointer_ids=proposed_artifact_pointer_ids,
            requested_descent_class=requested_descent_class,
            proposed_budget_id=proposed_budget_id,
            required_access_policy_ids=required_access_policy_ids,
            reason_codes=reason_codes,
            root_approval_required=True,
            creates_authority=False,
            creates_permission=False,
            executes_read=False,
        )
        return _finish(provisional, type_name="RetrievalPlanV01", reasons=_plan_reasons(provisional, check_identity=False), validator=validate_retrieval_plan_v01)
    except ValueError as exc:
        reason = str(exc)
        raise ValueError(reason if reason.startswith("drs_") else "drs_retrieval_plan_invalid") from None
    except Exception:
        raise ValueError("drs_retrieval_plan_invalid") from None


def validate_retrieval_plan_v01(value: object) -> tuple[bool, tuple[str, ...]]:
    try:
        reasons = _plan_reasons(value, check_identity=True)
        return not reasons, reasons
    except Exception:
        return False, ("drs_retrieval_plan_invalid",)


def retrieval_plan_to_plain_data_v01(value: object) -> dict[str, object]:
    if type(value) is not RetrievalPlanV01:
        raise ValueError("drs_exact_type_required") from None
    return {name: _plain_value(getattr(value, name)) for name in _PLAN_FIELDS}


def _ceiling(name: str) -> int:
    for field_name, value in DRS_REFERENCE_MEMORY_DESCENT_CEILINGS_V01:
        if field_name == name:
            return value
    raise ValueError("drs_memory_descent_budget_invalid")


def _budget_reasons(value: object, *, check_identity: bool) -> tuple[str, ...]:
    if type(value) is not MemoryDescentBudgetV01:
        return ("drs_exact_type_required",)
    reasons = _version_reasons(value.memory_descent_budget_version)
    for name in _BUDGET_FIELDS[2:]:
        item = getattr(value, name)
        if type(item) is not int:
            reasons.append("drs_exact_int_required")
        elif item < 0 or item > _ceiling(name):
            reasons.append("drs_memory_descent_budget_expansion")
    if check_identity and not reasons:
        reason = _id_reason(value, "MemoryDescentBudgetV01")
        if reason:
            reasons.append(reason)
    return _dedupe(reasons)


def build_memory_descent_budget_v01(
    *,
    max_depth: int,
    max_records_opened: int,
    max_pointers_opened: int,
    max_artifacts_opened: int,
    max_bytes_opened: int,
    max_lineage_edges: int,
    max_conflict_records: int,
) -> MemoryDescentBudgetV01:
    try:
        provisional = MemoryDescentBudgetV01(
            memory_descent_budget_version=_PROFILE_VERSION,
            memory_descent_budget_id="drsbudget_v01:" + "0" * 64,
            max_depth=max_depth,
            max_records_opened=max_records_opened,
            max_pointers_opened=max_pointers_opened,
            max_artifacts_opened=max_artifacts_opened,
            max_bytes_opened=max_bytes_opened,
            max_lineage_edges=max_lineage_edges,
            max_conflict_records=max_conflict_records,
        )
        return _finish(provisional, type_name="MemoryDescentBudgetV01", reasons=_budget_reasons(provisional, check_identity=False), validator=validate_memory_descent_budget_v01)
    except ValueError as exc:
        reason = str(exc)
        raise ValueError(reason if reason.startswith("drs_") else "drs_memory_descent_budget_invalid") from None
    except Exception:
        raise ValueError("drs_memory_descent_budget_invalid") from None


def validate_memory_descent_budget_v01(value: object) -> tuple[bool, tuple[str, ...]]:
    try:
        reasons = _budget_reasons(value, check_identity=True)
        return not reasons, reasons
    except Exception:
        return False, ("drs_memory_descent_budget_invalid",)


def memory_descent_budget_to_plain_data_v01(value: object) -> dict[str, object]:
    if type(value) is not MemoryDescentBudgetV01:
        raise ValueError("drs_exact_type_required") from None
    return {name: _plain_value(getattr(value, name)) for name in _BUDGET_FIELDS}


def _request_reasons(value: object, *, check_identity: bool) -> tuple[str, ...]:
    if type(value) is not MemoryDescentRequestV01:
        return ("drs_exact_type_required",)
    reasons = _version_reasons(value.memory_descent_request_version)
    for item, prefix in (
        (value.retrieval_plan_id, "drsplan_v01:"),
        (value.query_id, "drsquery_v01:"),
        (value.proposed_budget_id, "drsbudget_v01:"),
    ):
        if not _prefixed_id(item, prefix):
            reasons.append("drs_memory_descent_request_invalid")
    for item in (
        value.owning_local_root_id,
        value.root_kernel_id,
        value.root_decision_input_id,
        value.root_decision_id,
    ):
        if not _is_reference(item):
            reasons.append("drs_memory_descent_request_invalid")
    if not _is_sha256(value.root_decision_hash):
        reasons.append("drs_memory_descent_request_invalid")
    for item in (value.requested_descent_class, value.approved_descent_class):
        if type(item) is not str or item not in DRS_MEMORY_DESCENT_CLASSES_V01:
            reasons.append("drs_memory_descent_class_invalid")
    if (
        type(value.requested_descent_class) is str
        and type(value.approved_descent_class) is str
        and value.approved_descent_class not in (
            value.requested_descent_class,
            "SUMMARY_ONLY",
        )
    ):
        reasons.append("drs_memory_descent_budget_expansion")
    budget_valid, budget_reasons = validate_memory_descent_budget_v01(value.approved_budget)
    if not budget_valid:
        reasons.extend(budget_reasons)
    for tuple_value, prefix in (
        (value.approved_record_ids, "drsmeaning_v01:"),
        (value.approved_memory_pointer_ids, "drsmem_v01:"),
        (value.approved_artifact_pointer_ids, "drsart_v01:"),
    ):
        reasons.extend(
            _typed_id_tuple_reasons(
                tuple_value,
                prefix=prefix,
                maximum_items=64,
                invalid_reason="drs_memory_descent_request_invalid",
            )
        )
    reasons.extend(
        _token_tuple_reasons(value.reason_codes, maximum_items=64)
    )
    if type(value.approved_budget) is MemoryDescentBudgetV01:
        if len(value.approved_record_ids) > value.approved_budget.max_records_opened or len(value.approved_memory_pointer_ids) + len(value.approved_artifact_pointer_ids) > value.approved_budget.max_pointers_opened or len(value.approved_artifact_pointer_ids) > value.approved_budget.max_artifacts_opened:
            reasons.append("drs_memory_descent_budget_expansion")
    if value.root_approved is not True or value.reason_codes:
        reasons.append("drs_memory_descent_request_invalid")
    if value.creates_permission is not False or value.creates_authority is not False:
        reasons.append("drs_non_authority_law_invalid")
    if check_identity and not reasons:
        reason = _id_reason(value, "MemoryDescentRequestV01")
        if reason:
            reasons.append(reason)
    return _dedupe(reasons)


def build_memory_descent_request_v01(
    *,
    retrieval_plan_id: str,
    query_id: str,
    owning_local_root_id: str,
    root_kernel_id: str,
    root_decision_input_id: str,
    root_decision_id: str,
    root_decision_hash: str,
    requested_descent_class: str,
    approved_descent_class: str,
    proposed_budget_id: str,
    approved_budget: MemoryDescentBudgetV01,
    approved_record_ids: tuple[str, ...],
    approved_memory_pointer_ids: tuple[str, ...],
    approved_artifact_pointer_ids: tuple[str, ...],
) -> MemoryDescentRequestV01:
    try:
        provisional = MemoryDescentRequestV01(
            memory_descent_request_version=_PROFILE_VERSION,
            memory_descent_request_id="drsdescentreq_v01:" + "0" * 64,
            retrieval_plan_id=retrieval_plan_id,
            query_id=query_id,
            owning_local_root_id=owning_local_root_id,
            root_kernel_id=root_kernel_id,
            root_decision_input_id=root_decision_input_id,
            root_decision_id=root_decision_id,
            root_decision_hash=root_decision_hash,
            requested_descent_class=requested_descent_class,
            approved_descent_class=approved_descent_class,
            proposed_budget_id=proposed_budget_id,
            approved_budget=approved_budget,
            approved_record_ids=approved_record_ids,
            approved_memory_pointer_ids=approved_memory_pointer_ids,
            approved_artifact_pointer_ids=approved_artifact_pointer_ids,
            root_approved=True,
            reason_codes=(),
            creates_permission=False,
            creates_authority=False,
        )
        return _finish(provisional, type_name="MemoryDescentRequestV01", reasons=_request_reasons(provisional, check_identity=False), validator=validate_memory_descent_request_v01)
    except ValueError as exc:
        reason = str(exc)
        raise ValueError(reason if reason.startswith("drs_") else "drs_memory_descent_request_invalid") from None
    except Exception:
        raise ValueError("drs_memory_descent_request_invalid") from None


def validate_memory_descent_request_v01(value: object) -> tuple[bool, tuple[str, ...]]:
    try:
        reasons = _request_reasons(value, check_identity=True)
        return not reasons, reasons
    except Exception:
        return False, ("drs_memory_descent_request_invalid",)


def memory_descent_request_to_plain_data_v01(value: object) -> dict[str, object]:
    if type(value) is not MemoryDescentRequestV01:
        raise ValueError("drs_exact_type_required") from None
    return {name: _plain_value(getattr(value, name)) for name in _REQUEST_FIELDS}


def _result_reasons(value: object, *, check_identity: bool) -> tuple[str, ...]:
    if type(value) is not MemoryDescentResultV01:
        return ("drs_exact_type_required",)
    reasons = _version_reasons(value.memory_descent_result_version)
    for item, prefix in (
        (value.memory_descent_request_id, "drsdescentreq_v01:"),
        (value.retrieval_plan_id, "drsplan_v01:"),
        (value.query_id, "drsquery_v01:"),
        (value.applied_budget_id, "drsbudget_v01:"),
    ):
        if not _prefixed_id(item, prefix):
            reasons.append("drs_memory_descent_result_invalid")
    if type(value.executed_descent_class) is not str or value.executed_descent_class not in DRS_MEMORY_DESCENT_CLASSES_V01:
        reasons.append("drs_memory_descent_class_invalid")
    tuple_specs = (
        (value.opened_record_ids, "drsmeaning_v01:"),
        (value.opened_memory_pointer_ids, "drsmem_v01:"),
        (value.opened_artifact_pointer_ids, "drsart_v01:"),
        (value.traversed_lineage_edge_ids, "drsedge_v01:"),
        (value.opened_conflict_record_ids, "drsmeaning_v01:"),
    )
    for tuple_value, prefix in tuple_specs:
        reasons.extend(
            _typed_id_tuple_reasons(
                tuple_value,
                prefix=prefix,
                maximum_items=64,
                invalid_reason="drs_memory_descent_result_invalid",
            )
        )
    counter_pairs = (
        (value.depth_reached, _ceiling("max_depth")),
        (value.records_opened, _ceiling("max_records_opened")),
        (value.pointers_opened, _ceiling("max_pointers_opened")),
        (value.artifacts_opened, _ceiling("max_artifacts_opened")),
        (value.bytes_opened, _ceiling("max_bytes_opened")),
        (value.lineage_edges_traversed, _ceiling("max_lineage_edges")),
        (value.conflict_records_opened, _ceiling("max_conflict_records")),
    )
    if any(type(item) is not int or not 0 <= item <= ceiling for item, ceiling in counter_pairs):
        reasons.append("drs_memory_descent_accounting_invalid")
    if (
        type(value.records_opened) is int
        and value.records_opened != len(value.opened_record_ids)
    ) or (
        type(value.pointers_opened) is int
        and value.pointers_opened != len(value.opened_memory_pointer_ids) + len(value.opened_artifact_pointer_ids)
    ) or (
        type(value.artifacts_opened) is int
        and value.artifacts_opened != len(value.opened_artifact_pointer_ids)
    ) or (
        type(value.lineage_edges_traversed) is int
        and value.lineage_edges_traversed != len(value.traversed_lineage_edge_ids)
    ) or (
        type(value.conflict_records_opened) is int
        and value.conflict_records_opened != len(value.opened_conflict_record_ids)
    ):
        reasons.append("drs_memory_descent_accounting_invalid")
    reasons.extend(
        _safe_text_tuple_reasons(
            value.safe_summaries,
            maximum_items=32,
            maximum_chars=1024,
            require_unique=False,
        )
    )
    fingerprint_reasons = _sha256_tuple_reasons(
        value.opened_payload_fingerprints,
        maximum_items=4,
    )
    if fingerprint_reasons:
        reasons.append("drs_memory_descent_accounting_invalid")
    reasons.extend(
        _token_tuple_reasons(value.reason_codes, maximum_items=32)
    )
    if value.limits_respected is not True or value.reason_codes:
        reasons.append("drs_memory_descent_result_invalid")
    if value.creates_authority is not False or value.creates_permission is not False:
        reasons.append("drs_non_authority_law_invalid")
    if type(value.real_world_effects_count) is not int:
        reasons.append("drs_exact_int_required")
    elif value.real_world_effects_count != 0:
        reasons.append("drs_memory_descent_result_invalid")
    if check_identity and not reasons:
        reason = _id_reason(value, "MemoryDescentResultV01")
        if reason:
            reasons.append(reason)
    return _dedupe(reasons)


def build_memory_descent_result_v01(
    *,
    memory_descent_request_id: str,
    retrieval_plan_id: str,
    query_id: str,
    executed_descent_class: str,
    applied_budget_id: str,
    opened_record_ids: tuple[str, ...],
    opened_memory_pointer_ids: tuple[str, ...],
    opened_artifact_pointer_ids: tuple[str, ...],
    traversed_lineage_edge_ids: tuple[str, ...],
    opened_conflict_record_ids: tuple[str, ...],
    depth_reached: int,
    bytes_opened: int,
    safe_summaries: tuple[str, ...],
    opened_payload_fingerprints: tuple[str, ...],
) -> MemoryDescentResultV01:
    try:
        provisional = MemoryDescentResultV01(
            memory_descent_result_version=_PROFILE_VERSION,
            memory_descent_result_id="drsdescentres_v01:" + "0" * 64,
            memory_descent_request_id=memory_descent_request_id,
            retrieval_plan_id=retrieval_plan_id,
            query_id=query_id,
            executed_descent_class=executed_descent_class,
            applied_budget_id=applied_budget_id,
            opened_record_ids=opened_record_ids,
            opened_memory_pointer_ids=opened_memory_pointer_ids,
            opened_artifact_pointer_ids=opened_artifact_pointer_ids,
            traversed_lineage_edge_ids=traversed_lineage_edge_ids,
            opened_conflict_record_ids=opened_conflict_record_ids,
            depth_reached=depth_reached,
            records_opened=len(opened_record_ids),
            pointers_opened=len(opened_memory_pointer_ids) + len(opened_artifact_pointer_ids),
            artifacts_opened=len(opened_artifact_pointer_ids),
            bytes_opened=bytes_opened,
            lineage_edges_traversed=len(traversed_lineage_edge_ids),
            conflict_records_opened=len(opened_conflict_record_ids),
            safe_summaries=safe_summaries,
            opened_payload_fingerprints=opened_payload_fingerprints,
            limits_respected=True,
            reason_codes=(),
            creates_authority=False,
            creates_permission=False,
            real_world_effects_count=0,
        )
        return _finish(provisional, type_name="MemoryDescentResultV01", reasons=_result_reasons(provisional, check_identity=False), validator=validate_memory_descent_result_v01)
    except ValueError as exc:
        reason = str(exc)
        raise ValueError(reason if reason.startswith("drs_") else "drs_memory_descent_result_invalid") from None
    except Exception:
        raise ValueError("drs_memory_descent_result_invalid") from None


def validate_memory_descent_result_v01(value: object) -> tuple[bool, tuple[str, ...]]:
    try:
        reasons = _result_reasons(value, check_identity=True)
        return not reasons, reasons
    except Exception:
        return False, ("drs_memory_descent_result_invalid",)


def memory_descent_result_to_plain_data_v01(value: object) -> dict[str, object]:
    if type(value) is not MemoryDescentResultV01:
        raise ValueError("drs_exact_type_required") from None
    return {name: _plain_value(getattr(value, name)) for name in _RESULT_FIELDS}


def _exact_nested_tuple(value: object, exact_type: type, validator: object) -> tuple[str, ...]:
    if type(value) is not tuple:
        return ("drs_exact_type_required",)
    reasons: list[str] = []
    for item in value:
        if type(item) is not exact_type:
            reasons.append("drs_exact_type_required")
            continue
        valid, nested = validator(item)
        if not valid:
            reasons.extend(nested)
    return _dedupe(reasons)


def _report_reasons(value: object, *, check_identity: bool) -> tuple[str, ...]:
    if type(value) is not DRSResolutionReportV01:
        return ("drs_exact_type_required",)
    reasons = _version_reasons(value.report_version)
    valid, nested = validate_semantic_address_v01(value.semantic_address)
    if not valid:
        reasons.extend(nested)
    valid, nested = validate_drs_temporal_query_v01(value.query)
    if not valid:
        reasons.extend(nested)
    if type(value.semantic_address) is SemanticAddressV01 and type(value.query) is DRSTemporalQueryV01 and value.semantic_address.semantic_address_id != value.query.semantic_address_id:
        reasons.append("drs_resolution_report_binding_invalid")
    reasons.extend(_exact_nested_tuple(value.source_projections, LegacyDRSProjectionV01, validate_legacy_drs_projection_v01))
    reasons.extend(_exact_nested_tuple(value.source_records, MeaningRecordV01, validate_meaning_record_v01))
    reasons.extend(_exact_nested_tuple(value.query_evaluations, QueryEvaluationStateV01, validate_query_evaluation_state_v01))
    reasons.extend(_exact_nested_tuple(value.eligible_candidates, ResolutionCandidateV01, validate_resolution_candidate_v01))
    candidate_ids = (
        tuple(item.resolution_candidate_id for item in value.eligible_candidates)
        if type(value.eligible_candidates) is tuple and all(type(item) is ResolutionCandidateV01 for item in value.eligible_candidates)
        else ()
    )
    reasons.extend(
        _typed_id_tuple_reasons(
            value.ranked_candidate_ids,
            prefix="drscandidate_v01:",
            maximum_items=64,
            invalid_reason="drs_resolution_report_binding_invalid",
        )
    )
    if type(value.ranked_candidate_ids) is tuple and set(value.ranked_candidate_ids) != set(candidate_ids):
        reasons.append("drs_resolution_report_binding_invalid")
    if value.selected_candidate_id is not None:
        if type(value.selected_candidate_id) is not str or not value.ranked_candidate_ids or value.selected_candidate_id != value.ranked_candidate_ids[0]:
            reasons.append("drs_resolution_report_binding_invalid")
    elif value.ranked_candidate_ids:
        reasons.append("drs_resolution_report_binding_invalid")
    valid, nested = validate_retrieval_plan_v01(value.retrieval_plan)
    if not valid:
        reasons.extend(nested)
    if type(value.query) is DRSTemporalQueryV01 and type(value.retrieval_plan) is RetrievalPlanV01 and (value.retrieval_plan.query_id != value.query.query_id or value.retrieval_plan.semantic_address_id != value.query.semantic_address_id):
        reasons.append("drs_resolution_report_binding_invalid")
    if value.memory_descent_result is not None:
        valid, nested = validate_memory_descent_result_v01(value.memory_descent_result)
        if not valid:
            reasons.extend(nested)
    if value.root_shortcut_projection is not None:
        valid, nested = validate_root_shortcut_authorization_projection_v01(value.root_shortcut_projection)
        if not valid:
            reasons.extend(nested)
    if value.reuse_certificate is not None:
        valid, nested = validate_reuse_certificate_v01(value.reuse_certificate)
        if not valid:
            reasons.extend(nested)
        if type(value.root_shortcut_projection) is not RootShortcutAuthorizationProjectionV01 or type(value.reuse_certificate) is not ReuseCertificateV01 or value.reuse_certificate.root_shortcut_authorization_projection_id != value.root_shortcut_projection.root_shortcut_projection_id:
            reasons.append("reuse_certificate_cross_profile_mismatch")
    for tuple_value in (
        value.context_only_record_ids,
        value.historical_only_record_ids,
        value.warning_only_record_ids,
        value.rerun_required_record_ids,
        value.blocked_record_ids,
    ):
        reasons.extend(
            _typed_id_tuple_reasons(
                tuple_value,
                prefix="drsmeaning_v01:",
                maximum_items=64,
                invalid_reason="drs_resolution_report_binding_invalid",
            )
        )
    reasons.extend(
        _token_tuple_reasons(value.reason_codes, maximum_items=64)
    )
    if value.persistent_records_unchanged is not True:
        reasons.append("drs_retrieval_read_mutation_detected")
    counters = (
        value.provider_calls,
        value.network_calls,
        value.gemini_calls,
        value.external_drs_calls,
        value.connector_calls,
        value.real_world_effects_count,
    )
    if any(type(item) is not int or item not in (-1, 0) for item in counters):
        reasons.append("drs_operation_accounting_invalid")
    if type(value.final_status) is not str or value.final_status not in ("PASS", "FAIL_CLOSED"):
        reasons.append("drs_resolution_report_status_invalid")
    elif value.final_status == "PASS":
        if any(item != 0 for item in counters) or value.reason_codes:
            reasons.append("drs_resolution_report_status_invalid")
    elif not value.reason_codes:
        reasons.append("drs_resolution_report_status_invalid")
    if check_identity and not reasons:
        reason = _id_reason(value, "DRSResolutionReportV01")
        if reason:
            reasons.append(reason)
    return _dedupe(reasons)


def build_drs_resolution_report_v01(
    *,
    semantic_address: SemanticAddressV01,
    query: DRSTemporalQueryV01,
    source_projections: tuple[LegacyDRSProjectionV01, ...],
    source_records: tuple[MeaningRecordV01, ...],
    query_evaluations: tuple[QueryEvaluationStateV01, ...],
    eligible_candidates: tuple[ResolutionCandidateV01, ...],
    ranked_candidate_ids: tuple[str, ...],
    selected_candidate_id: str | None,
    retrieval_plan: RetrievalPlanV01,
    memory_descent_result: MemoryDescentResultV01 | None,
    root_shortcut_projection: RootShortcutAuthorizationProjectionV01 | None,
    reuse_certificate: ReuseCertificateV01 | None,
    context_only_record_ids: tuple[str, ...],
    historical_only_record_ids: tuple[str, ...],
    warning_only_record_ids: tuple[str, ...],
    rerun_required_record_ids: tuple[str, ...],
    blocked_record_ids: tuple[str, ...],
    provider_calls: int,
    network_calls: int,
    gemini_calls: int,
    external_drs_calls: int,
    connector_calls: int,
    real_world_effects_count: int,
    final_status: str,
    reason_codes: tuple[str, ...],
) -> DRSResolutionReportV01:
    try:
        provisional = DRSResolutionReportV01(
            report_version=_PROFILE_VERSION,
            report_id="drsreport_v01:" + "0" * 64,
            semantic_address=semantic_address,
            query=query,
            source_projections=source_projections,
            source_records=source_records,
            query_evaluations=query_evaluations,
            eligible_candidates=eligible_candidates,
            ranked_candidate_ids=ranked_candidate_ids,
            selected_candidate_id=selected_candidate_id,
            retrieval_plan=retrieval_plan,
            memory_descent_result=memory_descent_result,
            root_shortcut_projection=root_shortcut_projection,
            reuse_certificate=reuse_certificate,
            context_only_record_ids=context_only_record_ids,
            historical_only_record_ids=historical_only_record_ids,
            warning_only_record_ids=warning_only_record_ids,
            rerun_required_record_ids=rerun_required_record_ids,
            blocked_record_ids=blocked_record_ids,
            persistent_records_unchanged=True,
            provider_calls=provider_calls,
            network_calls=network_calls,
            gemini_calls=gemini_calls,
            external_drs_calls=external_drs_calls,
            connector_calls=connector_calls,
            real_world_effects_count=real_world_effects_count,
            final_status=final_status,
            reason_codes=reason_codes,
        )
        return _finish(provisional, type_name="DRSResolutionReportV01", reasons=_report_reasons(provisional, check_identity=False), validator=validate_drs_resolution_report_v01)
    except ValueError as exc:
        reason = str(exc)
        raise ValueError(reason if reason.startswith(("drs_", "reuse_certificate_")) else "drs_resolution_report_invalid") from None
    except Exception:
        raise ValueError("drs_resolution_report_invalid") from None


def validate_drs_resolution_report_v01(value: object) -> tuple[bool, tuple[str, ...]]:
    try:
        reasons = _report_reasons(value, check_identity=True)
        return not reasons, reasons
    except Exception:
        return False, ("drs_resolution_report_invalid",)


def drs_resolution_report_to_plain_data_v01(value: object) -> dict[str, object]:
    if type(value) is not DRSResolutionReportV01:
        raise ValueError("drs_exact_type_required") from None
    return {name: _plain_value(getattr(value, name)) for name in _REPORT_FIELDS}


__all__ = (
    "DRS_QUERY_MODES_V01",
    "DRS_QUERY_STATES_V01",
    "DRS_REUSE_CLASSES_V01",
    "DRS_ENABLED_REUSE_CLASSES_V01",
    "DRS_MEMORY_DESCENT_CLASSES_V01",
    "DRS_REFERENCE_MEMORY_DESCENT_CEILINGS_V01",
    "DRS_RANKING_WEIGHTS_V01",
    "DRSTemporalQueryV01",
    "QueryEvaluationStateV01",
    "ResolutionCandidateV01",
    "RetrievalPlanV01",
    "MemoryDescentBudgetV01",
    "MemoryDescentRequestV01",
    "MemoryDescentResultV01",
    "DRSResolutionReportV01",
    "build_drs_temporal_query_v01",
    "validate_drs_temporal_query_v01",
    "drs_temporal_query_to_plain_data_v01",
    "build_query_evaluation_state_v01",
    "validate_query_evaluation_state_v01",
    "query_evaluation_state_to_plain_data_v01",
    "build_resolution_candidate_v01",
    "validate_resolution_candidate_v01",
    "resolution_candidate_to_plain_data_v01",
    "build_retrieval_plan_v01",
    "validate_retrieval_plan_v01",
    "retrieval_plan_to_plain_data_v01",
    "build_memory_descent_budget_v01",
    "validate_memory_descent_budget_v01",
    "memory_descent_budget_to_plain_data_v01",
    "build_memory_descent_request_v01",
    "validate_memory_descent_request_v01",
    "memory_descent_request_to_plain_data_v01",
    "build_memory_descent_result_v01",
    "validate_memory_descent_result_v01",
    "memory_descent_result_to_plain_data_v01",
    "build_drs_resolution_report_v01",
    "validate_drs_resolution_report_v01",
    "drs_resolution_report_to_plain_data_v01",
)
