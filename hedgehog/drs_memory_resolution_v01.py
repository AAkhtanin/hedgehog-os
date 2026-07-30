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
from hedgehog.reuse_certificate_v01 import G2AActionHistoryBindingV01
from hedgehog.reuse_certificate_v01 import (
    RootShortcutAuthorizationProjectionV01,
)
from hedgehog.reuse_certificate_v01 import (
    _REUSE_CERTIFICATE_FIELDS,
    _ROOT_SHORTCUT_FIELDS,
    g2a_action_history_binding_to_plain_data_v01,
    reuse_certificate_to_plain_data_v01,
    root_shortcut_authorization_projection_to_plain_data_v01,
    validate_g2a_action_history_binding_v01,
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

_B2_EVIDENCE_CLASS_ORDER_V01 = (
    "SOURCE_IDENTITY",
    "SOURCE_INTEGRITY",
    "PROVENANCE_CHAIN",
    "TIME_FITNESS",
    "POLICY_COMPATIBILITY",
    "SCHEMA_COMPATIBILITY",
    "CONFLICT_CLEARANCE",
    "ROOT_DECISION",
    "SOURCE_HISTORY",
)
_B2_REQUIRED_TIME_AXES_BY_MODE_V01 = (
    ("CURRENT_DECISION", ("PT", "KT", "ET", "CT", "TTL", "VALIDITY")),
    (
        "DIRECT_REUSE_CANDIDATE",
        ("PT", "KT", "ET", "CT", "TTL", "VALIDITY"),
    ),
    ("HISTORICAL_AS_OF", ("KT", "VALIDITY")),
    ("AUDIT_REPLAY", ("PT", "KT", "ET", "CT", "VALIDITY")),
    ("TREND_ANALYSIS", ("KT", "ET", "VALIDITY")),
    ("MEMORY_CONTEXT_ONLY", ("KT", "TTL", "VALIDITY")),
)
_B2_EVALUATION_TIME_SOURCE_BY_MODE_V01 = (
    ("CURRENT_DECISION", "INJECTED_CURRENT_DECISION_TIME"),
    ("DIRECT_REUSE_CANDIDATE", "INJECTED_CURRENT_DECISION_TIME"),
    ("HISTORICAL_AS_OF", "RECORDED_HISTORICAL_AS_OF_TIME"),
    ("AUDIT_REPLAY", "RECORDED_AUDIT_REPLAY_TIME"),
    ("TREND_ANALYSIS", "INJECTED_ANALYSIS_TIME"),
    ("MEMORY_CONTEXT_ONLY", "INJECTED_ANALYSIS_TIME"),
)
_B2_INFORMATIONAL_INTENT_CLASSES_V01 = (
    "informational_summary",
    "informational_lookup",
    "informational_explanation",
    "context_lookup",
    "warning_lookup",
    "historical_inspection",
    "trend_analysis",
)
_B2_CHANGE_RELATION_CLASSES_V01 = (
    "CONTRADICTS",
    "SUPERSEDES",
    "REPLACES",
    "BLOCKED_BY_POLICY",
    "DEGRADED_FROM",
)

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


def _b2_profile_value(
    profile: tuple[tuple[str, object], ...],
    key: str,
) -> object:
    for profile_key, profile_value in profile:
        if profile_key == key:
            return profile_value
    raise ValueError("drs_exact_type_or_identity_invalid")


def _b2_digest(*, domain: str, material: tuple[object, ...]) -> str:
    payload = _canonical_json_bytes_v01(material)
    return _domain_separated_sha256_hex_v01(
        domain=domain,
        payload=payload,
    )


def _b2_ordered_unique(values: tuple[str, ...]) -> tuple[str, ...]:
    observed: list[str] = []
    for value in values:
        if value not in observed:
            observed.append(value)
    return tuple(observed)


def _b2_source_history_hash(
    meaning_record: MeaningRecordV01,
    action_history_binding_id: str | None,
) -> str:
    return _b2_digest(
        domain="hedgehog:drs:source_history:v01",
        material=(
            meaning_record.meaning_record_id,
            meaning_record.content_fingerprint,
            meaning_record.predecessor_record_id,
            tuple(
                edge.lineage_edge_id
                for edge in meaning_record.lineage_edges
            ),
            tuple(
                edge.source_history_hash
                for edge in meaning_record.lineage_edges
            ),
            meaning_record.source_reference_ids,
            meaning_record.authority_envelope.authority_envelope_id,
            meaning_record.time_envelope.time_envelope_id,
            action_history_binding_id,
        ),
    )


def _b2_observed_evidence_fingerprint(
    *,
    evidence_classes: tuple[str, ...],
    meaning_record: MeaningRecordV01,
    action_history_binding_id: str | None,
) -> str:
    source_reference_ids = _b2_ordered_unique(
        meaning_record.source_reference_ids
    )
    observed_refs = list(source_reference_ids)
    lineage_evidence_refs: list[str] = []
    for edge in meaning_record.lineage_edges:
        for evidence_ref_id in edge.evidence_ref_ids:
            if evidence_ref_id not in observed_refs:
                observed_refs.append(evidence_ref_id)
                lineage_evidence_refs.append(evidence_ref_id)
    authority = meaning_record.authority_envelope
    return _b2_digest(
        domain="hedgehog:drs:observed_evidence:v01",
        material=(
            evidence_classes,
            source_reference_ids,
            tuple(lineage_evidence_refs),
            authority.source_root_decision_input_id,
            authority.source_root_decision_id,
            authority.source_root_decision_hash,
            action_history_binding_id,
        ),
    )


def _b2_observed_changes(
    meaning_record: MeaningRecordV01,
) -> tuple[str, ...]:
    values = list(meaning_record.risk_hints)
    values.extend(meaning_record.conflict_hints)
    values.extend(
        edge.relation_class
        for edge in meaning_record.lineage_edges
        if edge.relation_class in _B2_CHANGE_RELATION_CLASSES_V01
    )
    if meaning_record.predecessor_record_id is not None:
        values.append("SUPERSESSION_PRESENT")
    return _b2_ordered_unique(tuple(values))


def _b2_required_axes_are_ordered(
    actual: tuple[str, ...],
    required: tuple[str, ...],
) -> bool:
    position = 0
    for axis in actual:
        if position < len(required) and axis == required[position]:
            position += 1
    return position == len(required)


def _b2_history_reason(
    binding: G2AActionHistoryBindingV01 | None,
) -> str | None:
    if binding is None:
        return None
    if binding.lifecycle_state == "EXPIRED":
        return "drs_action_history_expired"
    if binding.lifecycle_state == "REVOKED":
        return "drs_action_history_revoked"
    if binding.lifecycle_state == "SUPERSEDED":
        return "drs_action_history_superseded"
    if binding.lifecycle_state in ("BLOCKED", "FAILED"):
        return "drs_action_history_blocked"
    if binding.disposition == "CONSUMED":
        return "drs_action_history_consumed"
    if binding.disposition == "UNCERTAIN_CLOSED":
        return "drs_action_history_uncertain_closed"
    if binding.terminal_receipt_ref is not None:
        return "drs_prior_receipt_shortcut_forbidden"
    return "drs_action_history_shortcut_forbidden"


def evaluate_drs_candidate_v01(
    *,
    semantic_address: SemanticAddressV01,
    query: DRSTemporalQueryV01,
    meaning_record: MeaningRecordV01,
    action_history_binding: G2AActionHistoryBindingV01 | None = None,
) -> QueryEvaluationStateV01:
    try:
        if type(semantic_address) is not SemanticAddressV01:
            raise ValueError("drs_exact_type_or_identity_invalid")
        valid, reasons = validate_semantic_address_v01(semantic_address)
        if not valid or reasons:
            raise ValueError("drs_exact_type_or_identity_invalid")
        if type(query) is not DRSTemporalQueryV01:
            raise ValueError("drs_exact_type_or_identity_invalid")
        valid, reasons = validate_drs_temporal_query_v01(query)
        if not valid or reasons:
            raise ValueError("drs_exact_type_or_identity_invalid")
        if type(meaning_record) is not MeaningRecordV01:
            raise ValueError("drs_exact_type_or_identity_invalid")
        valid, reasons = validate_meaning_record_v01(meaning_record)
        if not valid or reasons:
            raise ValueError("drs_exact_type_or_identity_invalid")
        action_history_binding_id = None
        if action_history_binding is not None:
            if type(action_history_binding) is not G2AActionHistoryBindingV01:
                raise ValueError("drs_exact_type_or_identity_invalid")
            valid, reasons = validate_g2a_action_history_binding_v01(
                action_history_binding
            )
            if not valid or reasons:
                raise ValueError("drs_exact_type_or_identity_invalid")
            binding_data = g2a_action_history_binding_to_plain_data_v01(
                action_history_binding
            )
            action_history_binding_id = binding_data["binding_id"]

        time_envelope = meaning_record.time_envelope
        authority = meaning_record.authority_envelope
        required_axes = _b2_profile_value(
            _B2_REQUIRED_TIME_AXES_BY_MODE_V01,
            query.query_mode,
        )
        expected_time_source = _b2_profile_value(
            _B2_EVALUATION_TIME_SOURCE_BY_MODE_V01,
            query.query_mode,
        )
        if type(required_axes) is not tuple or type(expected_time_source) is not str:
            raise ValueError("drs_exact_type_or_identity_invalid")

        validity_interval_passed = (
            time_envelope.valid_from
            <= query.as_of
            < time_envelope.valid_to
        )
        ttl_expiry = (
            time_envelope.pt_created_at + time_envelope.ttl_seconds
        )
        ttl_arithmetic_safe = _INT64_MIN <= ttl_expiry <= _INT64_MAX
        ttl_interval_passed = ttl_arithmetic_safe and query.as_of < ttl_expiry
        age_seconds = query.as_of - time_envelope.pt_created_at
        if query.max_age_seconds == 0:
            max_age_passed = age_seconds == 0
            current_freshness_units = 10000 if age_seconds == 0 else 0
        else:
            max_age_passed = 0 <= age_seconds < query.max_age_seconds
            current_freshness_units = (
                0
                if age_seconds < 0
                else max(
                    0,
                    (
                        (query.max_age_seconds - age_seconds)
                        * 10000
                    )
                    // query.max_age_seconds,
                )
            )
        freshness_policy_passed = (
            query.freshness_policy_id
            == time_envelope.freshness_policy_id
        )
        ttl_freshness_passed = (
            ttl_interval_passed
            and max_age_passed
            and freshness_policy_passed
        )
        mode_required_axes_present = _b2_required_axes_are_ordered(
            query.required_time_axes,
            required_axes,
        )
        requested_point_axes_available = True
        if "PT" in query.required_time_axes:
            requested_point_axes_available = (
                requested_point_axes_available
                and time_envelope.pt_created_at <= query.as_of
            )
        if "KT" in query.required_time_axes:
            requested_point_axes_available = (
                requested_point_axes_available
                and time_envelope.kt_as_of <= query.as_of
            )
        if "ET" in query.required_time_axes:
            requested_point_axes_available = (
                requested_point_axes_available
                and time_envelope.et_observed_at <= query.as_of
            )
        if "CT" in query.required_time_axes:
            requested_point_axes_available = (
                requested_point_axes_available
                and time_envelope.ct_context_anchor
                <= query.evaluation_time
            )
        if "SOURCE_OBSERVED" in query.required_time_axes:
            requested_point_axes_available = (
                requested_point_axes_available
                and time_envelope.source_observed_at <= query.as_of
            )
        if "SOURCE_REPORTED" in query.required_time_axes:
            requested_point_axes_available = (
                requested_point_axes_available
                and time_envelope.source_reported_at <= query.as_of
            )
        if "SYSTEM_INGESTED" in query.required_time_axes:
            requested_point_axes_available = (
                requested_point_axes_available
                and time_envelope.system_ingested_at
                <= query.evaluation_time
            )
        if "SYSTEM_VERIFIED" in query.required_time_axes:
            requested_point_axes_available = (
                requested_point_axes_available
                and time_envelope.system_verified_at
                <= query.evaluation_time
            )
        if "TTL" in query.required_time_axes:
            requested_point_axes_available = (
                requested_point_axes_available
                and ttl_freshness_passed
            )
        if "VALIDITY" in query.required_time_axes:
            requested_point_axes_available = (
                requested_point_axes_available
                and validity_interval_passed
            )
        required_time_axes_passed = (
            mode_required_axes_present
            and requested_point_axes_available
        )
        source_mapping_passed = (
            query.evaluation_time_source == expected_time_source
        )
        current_time_binding_passed = (
            query.query_mode
            not in ("CURRENT_DECISION", "DIRECT_REUSE_CANDIDATE")
            or query.evaluation_time == query.as_of
        )
        temporal_hard_gate_passed = (
            validity_interval_passed
            and ttl_freshness_passed
            and required_time_axes_passed
            and source_mapping_passed
            and current_time_binding_passed
        )

        scope_passed = (
            meaning_record.semantic_address == semantic_address
            and semantic_address.semantic_address_id
            == query.semantic_address_id
            and semantic_address.domain == query.domain
            and authority.authority_scope_fingerprint
            == query.scope_fingerprint
        )
        shortcut_requested = (
            "ANSWER_SHORTCUT" in query.requested_reuse_classes
            or query.reuse_intent
            == "INFORMATIONAL_SHORTCUT_CONSIDERATION"
        )
        lifecycle_passed = (
            meaning_record.persistent_lifecycle_state == "ACTIVE"
            or (
                meaning_record.persistent_lifecycle_state == "COMPLETED"
                and not shortcut_requested
            )
            or meaning_record.persistent_lifecycle_state
            in ("QUARANTINED", "DEADEND")
        )
        requested_reuse_classes_enabled = all(
            reuse_class in DRS_ENABLED_REUSE_CLASSES_V01
            for reuse_class in query.requested_reuse_classes
        )
        record_reuse_class_enabled = (
            meaning_record.reuse_policy_class
            in DRS_ENABLED_REUSE_CLASSES_V01
        )
        disabled_reuse_class_present = (
            not requested_reuse_classes_enabled
            or not record_reuse_class_enabled
        )
        enabled_class_binding_passed = (
            meaning_record.reuse_policy_class
            in query.requested_reuse_classes
            and (
                "ANSWER_SHORTCUT" not in query.requested_reuse_classes
                or meaning_record.reuse_policy_class == "ANSWER_SHORTCUT"
            )
        )
        independent_policy_mismatch = (
            meaning_record.policy_version != query.policy_version
            or (
                requested_reuse_classes_enabled
                and record_reuse_class_enabled
                and not enabled_class_binding_passed
            )
        )
        policy_compatible = (
            not disabled_reuse_class_present
            and not independent_policy_mismatch
        )
        schema_compatible = (
            meaning_record.schema_versions == query.schema_versions
        )
        is_root_accepted = (
            authority.authority_class
            in ("ROOT_ACCEPTED_CONTEXT", "ROOT_ACCEPTED_WORK")
            and authority.owning_local_root_id
            == query.owning_local_root_id
            and authority.source_root_decision_input_id is not None
            and authority.source_root_decision_id is not None
            and authority.source_root_decision_hash is not None
            and (
                (
                    authority.authority_class
                    == "ROOT_ACCEPTED_CONTEXT"
                    and authority.root_acceptance_state
                    == "ACCEPTED_CONTEXT"
                )
                or (
                    authority.authority_class
                    == "ROOT_ACCEPTED_WORK"
                    and authority.root_acceptance_state
                    == "ACCEPTED_WORK"
                )
            )
            and bool(meaning_record.source_reference_ids)
        )
        is_action_history_reference = (
            authority.authority_class == "ACTION_HISTORY_REFERENCE"
        )
        provenance_passed = (
            is_root_accepted or is_action_history_reference
        )
        authority_envelope_passed = is_root_accepted
        conflict_passed = (
            not meaning_record.conflict_hints
            and all(
                edge.relation_class
                not in (
                    "CONTRADICTS",
                    "WARNS_AGAINST",
                    "BLOCKED_BY_POLICY",
                )
                for edge in meaning_record.lineage_edges
            )
        )
        quarantine_passed = (
            meaning_record.persistent_lifecycle_state != "QUARANTINED"
            and authority.root_acceptance_state != "QUARANTINED"
        )
        deadend_passed = (
            meaning_record.persistent_lifecycle_state != "DEADEND"
        )
        action_intent_passed = (
            semantic_address.intent_class
            in _B2_INFORMATIONAL_INTENT_CLASSES_V01
        )
        history_reason = _b2_history_reason(action_history_binding)
        if is_action_history_reference and action_history_binding is None:
            history_reason = "drs_action_history_shortcut_forbidden"
        g2a_action_history_passed = history_reason is None
        permission_boundary_passed = (
            authority.action_permission_present is False
            and authority.creates_permission is False
            and all(
                not source_ref.startswith("permission:")
                for source_ref in meaning_record.source_reference_ids
            )
        )

        source_history_hash = _b2_source_history_hash(
            meaning_record,
            action_history_binding_id,
        )
        evidence_presence = (
            ("SOURCE_IDENTITY", True),
            ("SOURCE_INTEGRITY", True),
            (
                "PROVENANCE_CHAIN",
                bool(meaning_record.source_reference_ids),
            ),
            ("TIME_FITNESS", temporal_hard_gate_passed),
            ("POLICY_COMPATIBILITY", policy_compatible),
            ("SCHEMA_COMPATIBILITY", schema_compatible),
            ("CONFLICT_CLEARANCE", conflict_passed),
            ("ROOT_DECISION", is_root_accepted),
            ("SOURCE_HISTORY", True),
        )
        evidence_classes = tuple(
            evidence_class
            for evidence_class in _B2_EVIDENCE_CLASS_ORDER_V01
            if any(
                candidate_class == evidence_class and present is True
                for candidate_class, present in evidence_presence
            )
        )
        required_evidence_passed = all(
            required in evidence_classes
            for required in query.required_evidence_classes
        )
        observed_changes = _b2_observed_changes(meaning_record)
        forbidden_changes_passed = all(
            forbidden not in observed_changes
            for forbidden in query.forbidden_changes
        )
        observed_evidence_fingerprint = (
            _b2_observed_evidence_fingerprint(
                evidence_classes=evidence_classes,
                meaning_record=meaning_record,
                action_history_binding_id=action_history_binding_id,
            )
        )
        checked_dependency_fingerprint = _b2_digest(
            domain="hedgehog:drs:checked_dependencies:v01",
            material=(
                query.forbidden_changes,
                observed_changes,
            ),
        )

        failure_reasons: list[str] = []
        failure_states: list[str] = []
        if not scope_passed:
            failure_reasons.append("drs_address_scope_mismatch")
            failure_states.append("BLOCKED_BY_SCOPE")
        if not lifecycle_passed:
            failure_reasons.append("drs_persistent_lifecycle_blocked")
            failure_states.append("BLOCKED_BY_POLICY")
        temporal_reasons: list[str] = []
        if not validity_interval_passed:
            temporal_reasons.append("drs_time_validity_interval_invalid")
        if not ttl_interval_passed:
            temporal_reasons.append("drs_time_ttl_expired")
        if not mode_required_axes_present:
            temporal_reasons.append("drs_time_axis_missing")
        if (
            not temporal_hard_gate_passed
            and not temporal_reasons
        ):
            temporal_reasons.append("drs_temporal_hard_gate_failed")
        if temporal_reasons:
            failure_reasons.extend(temporal_reasons)
            failure_states.extend(
                "BLOCKED_BY_TIME" for _ in temporal_reasons
            )
        if disabled_reuse_class_present:
            failure_reasons.append("drs_reuse_class_disabled")
            failure_states.append("BLOCKED_BY_POLICY")
        if independent_policy_mismatch:
            failure_reasons.append("drs_policy_version_mismatch")
            failure_states.append("BLOCKED_BY_POLICY")
        if not schema_compatible:
            failure_reasons.append("drs_schema_version_mismatch")
            failure_states.append("BLOCKED_BY_POLICY")
        if authority.authority_class == "ROOT_FINAL_REFERENCE":
            failure_reasons.append(
                "drs_prior_root_final_shortcut_forbidden"
            )
            failure_states.append("BLOCKED_BY_PROVENANCE")
        elif not provenance_passed:
            failure_reasons.append("drs_provenance_invalid")
            failure_states.append("BLOCKED_BY_PROVENANCE")
        if not required_evidence_passed:
            failure_reasons.append("drs_required_evidence_missing")
            failure_states.append("BLOCKED_BY_REQUIRED_EVIDENCE")
        if not forbidden_changes_passed:
            failure_reasons.append("drs_forbidden_change_detected")
            failure_states.append("BLOCKED_BY_FORBIDDEN_CHANGE")
        if not conflict_passed:
            failure_reasons.append("drs_conflict_blocked")
            failure_states.append("BLOCKED_BY_CONFLICT")
        if not quarantine_passed:
            failure_reasons.append("drs_quarantine_blocked")
            failure_states.append("BLOCKED_BY_QUARANTINE")
        if not deadend_passed:
            failure_reasons.append("drs_deadend_blocked")
            failure_states.append("BLOCKED_BY_DEADEND")
        if not action_intent_passed:
            failure_reasons.append(
                "drs_action_intent_shortcut_forbidden"
            )
            failure_states.append("BLOCKED_BY_ACTION_INTENT")
        if history_reason is not None:
            failure_reasons.append(history_reason)
            failure_states.append("BLOCKED_BY_ACTION_HISTORY")
        if not permission_boundary_passed:
            failure_reasons.append("drs_permission_boundary_failed")
            failure_states.append("BLOCKED_BY_ACTION_HISTORY")

        mode_rankable = query.query_mode in (
            "CURRENT_DECISION",
            "DIRECT_REUSE_CANDIDATE",
        ) and not disabled_reuse_class_present
        if query.query_mode == "DIRECT_REUSE_CANDIDATE":
            mode_rankable = (
                query.reuse_intent
                == "INFORMATIONAL_SHORTCUT_CONSIDERATION"
                and "ANSWER_SHORTCUT"
                in query.requested_reuse_classes
                and action_intent_passed
            )
        if not failure_reasons and not mode_rankable:
            failure_reasons.append(
                "drs_query_mode_invalid_for_shortcut"
            )
            if query.query_mode in (
                "HISTORICAL_AS_OF",
                "AUDIT_REPLAY",
                "TREND_ANALYSIS",
            ):
                failure_states.append("HISTORICAL_ONLY")
            elif (
                query.query_mode == "MEMORY_CONTEXT_ONLY"
                and query.reuse_intent == "WARNING_LOOKUP"
            ):
                failure_states.append("WARNING_ONLY")
            else:
                failure_states.append("STALE_CONTEXT_ONLY")

        failure_reasons_tuple = _dedupe(failure_reasons)
        eligible_for_ranking = (
            not failure_reasons_tuple and mode_rankable
        )
        query_state = (
            "FRESH_CANDIDATE"
            if eligible_for_ranking
            else failure_states[0]
        )
        return build_query_evaluation_state_v01(
            query_id=query.query_id,
            semantic_address_id=semantic_address.semantic_address_id,
            meaning_record_id=meaning_record.meaning_record_id,
            query_state=query_state,
            evaluated_at=query.evaluation_time,
            evaluation_time_source=query.evaluation_time_source,
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
            observed_evidence_fingerprint=(
                observed_evidence_fingerprint
            ),
            checked_dependency_fingerprint=(
                checked_dependency_fingerprint
            ),
            source_history_hash=source_history_hash,
            action_history_binding_id=action_history_binding_id,
            eligible_for_ranking=eligible_for_ranking,
            reason_codes=failure_reasons_tuple,
        )
    except ValueError as exc:
        if str(exc) == "drs_exact_type_or_identity_invalid":
            raise
        raise ValueError("drs_exact_type_or_identity_invalid") from None
    except Exception:
        raise ValueError("drs_exact_type_or_identity_invalid") from None


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


def rank_eligible_drs_candidates_v01(
    *,
    query: DRSTemporalQueryV01,
    query_evaluations: tuple[QueryEvaluationStateV01, ...],
    candidates: tuple[ResolutionCandidateV01, ...],
) -> tuple[ResolutionCandidateV01, ...]:
    try:
        if type(query) is not DRSTemporalQueryV01:
            raise ValueError("drs_exact_type_or_identity_invalid")
        valid, reasons = validate_drs_temporal_query_v01(query)
        if not valid or reasons:
            raise ValueError("drs_exact_type_or_identity_invalid")
        if type(query_evaluations) is not tuple or type(candidates) is not tuple:
            raise ValueError("drs_exact_type_or_identity_invalid")

        evaluations_by_id: dict[str, QueryEvaluationStateV01] = {}
        meaning_record_ids: set[str] = set()
        for evaluation in query_evaluations:
            if type(evaluation) is not QueryEvaluationStateV01:
                raise ValueError("drs_exact_type_or_identity_invalid")
            valid, reasons = validate_query_evaluation_state_v01(evaluation)
            if not valid or reasons:
                raise ValueError("drs_exact_type_or_identity_invalid")
            if (
                evaluation.query_id != query.query_id
                or evaluation.semantic_address_id
                != query.semantic_address_id
                or evaluation.evaluated_at != query.evaluation_time
                or evaluation.evaluation_time_source
                != query.evaluation_time_source
            ):
                raise ValueError("drs_ranking_tie_break_invalid")
            if (
                evaluation.query_evaluation_id in evaluations_by_id
                or evaluation.meaning_record_id in meaning_record_ids
            ):
                raise ValueError("drs_ranking_tie_break_invalid")
            evaluations_by_id[evaluation.query_evaluation_id] = evaluation
            meaning_record_ids.add(evaluation.meaning_record_id)

        candidate_ids: set[str] = set()
        candidate_evaluation_ids: set[str] = set()
        candidate_by_evaluation_id: dict[
            str,
            ResolutionCandidateV01,
        ] = {}
        for candidate in candidates:
            if type(candidate) is not ResolutionCandidateV01:
                raise ValueError("drs_exact_type_or_identity_invalid")
            valid, reasons = validate_resolution_candidate_v01(candidate)
            if not valid or reasons:
                raise ValueError("drs_exact_type_or_identity_invalid")
            if (
                candidate.resolution_candidate_id in candidate_ids
                or candidate.query_evaluation_id
                in candidate_evaluation_ids
            ):
                raise ValueError("drs_ranking_tie_break_invalid")
            candidate_ids.add(candidate.resolution_candidate_id)
            candidate_evaluation_ids.add(candidate.query_evaluation_id)
            evaluation = evaluations_by_id.get(
                candidate.query_evaluation_id
            )
            if (
                evaluation is None
                or evaluation.eligible_for_ranking is not True
                or evaluation.query_state != "FRESH_CANDIDATE"
                or evaluation.reason_codes
                or candidate.query_id != query.query_id
                or candidate.semantic_address_id
                != query.semantic_address_id
                or evaluation.query_id != query.query_id
                or evaluation.semantic_address_id
                != query.semantic_address_id
                or candidate.meaning_record_id
                != evaluation.meaning_record_id
                or candidate.source_history_hash
                != evaluation.source_history_hash
                or candidate.action_history_binding_id
                != evaluation.action_history_binding_id
                or candidate.freshness_units
                != evaluation.current_freshness_units
            ):
                raise ValueError("drs_ineligible_candidate_selected")
            candidate_by_evaluation_id[
                evaluation.query_evaluation_id
            ] = candidate

        eligible_evaluation_ids = tuple(
            evaluation.query_evaluation_id
            for evaluation in query_evaluations
            if evaluation.eligible_for_ranking is True
            and evaluation.query_state == "FRESH_CANDIDATE"
            and not evaluation.reason_codes
        )
        if (
            len(candidate_by_evaluation_id)
            != len(eligible_evaluation_ids)
            or any(
                evaluation_id not in candidate_by_evaluation_id
                for evaluation_id in eligible_evaluation_ids
            )
        ):
            raise ValueError("drs_ranking_tie_break_invalid")
        return tuple(
            sorted(
                candidates,
                key=lambda candidate: (
                    -candidate.total_score_units,
                    candidate.resolution_candidate_id,
                ),
            )
        )
    except ValueError as exc:
        reason = str(exc)
        if reason in (
            "drs_exact_type_or_identity_invalid",
            "drs_ineligible_candidate_selected",
            "drs_ranking_tie_break_invalid",
        ):
            raise
        raise ValueError("drs_exact_type_or_identity_invalid") from None
    except Exception:
        raise ValueError("drs_exact_type_or_identity_invalid") from None


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


def _b2_pre_descent_report_reasons(
    value: DRSResolutionReportV01,
) -> tuple[str, ...]:
    try:
        if (
            type(value.source_records) is not tuple
            or type(value.query_evaluations) is not tuple
            or type(value.eligible_candidates) is not tuple
            or len(value.source_records) != len(value.query_evaluations)
        ):
            return ("drs_resolution_report_binding_invalid",)
        rebuilt_evaluations: list[QueryEvaluationStateV01] = []
        for source_record, transported_evaluation in zip(
            value.source_records,
            value.query_evaluations,
        ):
            if (
                type(source_record) is not MeaningRecordV01
                or type(transported_evaluation)
                is not QueryEvaluationStateV01
                or source_record.meaning_record_id
                != transported_evaluation.meaning_record_id
            ):
                return ("drs_resolution_report_binding_invalid",)
            rebuilt = evaluate_drs_candidate_v01(
                semantic_address=value.semantic_address,
                query=value.query,
                meaning_record=source_record,
                action_history_binding=None,
            )
            rebuilt_evaluations.append(rebuilt)
            if rebuilt != transported_evaluation:
                return ("drs_resolution_report_binding_invalid",)

        ranked = rank_eligible_drs_candidates_v01(
            query=value.query,
            query_evaluations=tuple(rebuilt_evaluations),
            candidates=value.eligible_candidates,
        )
        ranked_ids = tuple(
            candidate.resolution_candidate_id
            for candidate in ranked
        )
        selected_id = (
            ranked[0].resolution_candidate_id if ranked else None
        )
        if (
            value.ranked_candidate_ids != ranked_ids
            or value.selected_candidate_id != selected_id
        ):
            return ("drs_resolution_report_binding_invalid",)

        context_only: list[str] = []
        historical_only: list[str] = []
        warning_only: list[str] = []
        rerun_required: list[str] = []
        blocked: list[str] = []
        for source_record, evaluation in zip(
            value.source_records,
            rebuilt_evaluations,
        ):
            if evaluation.query_state == "STALE_CONTEXT_ONLY":
                context_only.append(source_record.meaning_record_id)
            elif evaluation.query_state == "HISTORICAL_ONLY":
                historical_only.append(source_record.meaning_record_id)
            elif evaluation.query_state == "WARNING_ONLY":
                warning_only.append(source_record.meaning_record_id)
            elif evaluation.query_state == "RERUN_REQUIRED":
                rerun_required.append(source_record.meaning_record_id)
            elif evaluation.query_state.startswith("BLOCKED_"):
                blocked.append(source_record.meaning_record_id)
        if (
            value.context_only_record_ids != tuple(context_only)
            or value.historical_only_record_ids
            != tuple(historical_only)
            or value.warning_only_record_ids != tuple(warning_only)
            or value.rerun_required_record_ids
            != tuple(rerun_required)
            or value.blocked_record_ids != tuple(blocked)
        ):
            return ("drs_resolution_report_binding_invalid",)

        record_ids = tuple(
            record.meaning_record_id
            for record in value.source_records
        )
        plan = value.retrieval_plan
        if (
            type(plan) is not RetrievalPlanV01
            or plan.query_id != value.query.query_id
            or plan.semantic_address_id
            != value.query.semantic_address_id
            or plan.proposed_record_ids != record_ids
            or plan.requested_descent_class != "SUMMARY_ONLY"
            or plan.proposed_memory_pointer_ids
            or plan.proposed_artifact_pointer_ids
            or plan.executes_read is not False
        ):
            return ("drs_resolution_report_binding_invalid",)
        counters = (
            value.provider_calls,
            value.network_calls,
            value.gemini_calls,
            value.external_drs_calls,
            value.connector_calls,
            value.real_world_effects_count,
        )
        if (
            value.persistent_records_unchanged is not True
            or any(type(counter) is not int or counter != 0 for counter in counters)
            or value.final_status != "PASS"
            or value.reason_codes
        ):
            return ("drs_resolution_report_binding_invalid",)
        return ()
    except Exception:
        return ("drs_resolution_report_binding_invalid",)


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
    if (
        value.memory_descent_result is None
        and value.root_shortcut_projection is None
        and value.reuse_certificate is None
    ):
        reasons.extend(_b2_pre_descent_report_reasons(value))
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
    "evaluate_drs_candidate_v01",
    "rank_eligible_drs_candidates_v01",
)
