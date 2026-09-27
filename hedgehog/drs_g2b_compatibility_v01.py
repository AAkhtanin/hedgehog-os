"""Read-only in-memory legacy DRS projection into the canonical G2-B family."""

from __future__ import annotations

from dataclasses import dataclass as _dataclass
from dataclasses import fields as _dataclass_fields
from dataclasses import replace as _replace
import math as _math
import re as _re

from hedgehog.drs_semantic_address_v01 import (
    DRS_G2B_PROFILE_VERSION_V01 as _PROFILE_VERSION,
)
from hedgehog.drs_semantic_address_v01 import MeaningRecordV01
from hedgehog.drs_semantic_address_v01 import SemanticAddressV01
from hedgehog.drs_semantic_address_v01 import (
    _canonical_json_bytes_v01,
    _canonical_plain_value,
    _dedupe,
    _domain_separated_sha256_hex_v01,
    _is_reference,
    _is_sha256,
    _plain_data_value,
    _secret_reason,
    _field_name_tuple_reasons,
    _token_tuple_reasons,
    validate_meaning_record_v01,
    validate_semantic_address_v01,
)
from hedgehog.local_drs_resolver import SemanticDRSRecordInput as _SemanticDRSRecordInput
from hedgehog.local_drs_v02 import DRSFreshnessEnvelope as _DRSFreshnessEnvelope
from hedgehog.local_drs_v02 import DRSLineageRef as _DRSLineageRef
from hedgehog.local_drs_v02 import DRSRecordV02 as _DRSRecordV02
from hedgehog.local_drs_v02 import TemporalQueryV02 as _TemporalQueryV02
from hedgehog.local_drs_v02 import (
    validate_freshness_envelope as _validate_legacy_freshness_envelope,
)
from hedgehog.local_drs_v02 import (
    validate_temporal_query as _validate_legacy_temporal_query,
)


_SOURCE_FAMILIES = (
    "LOCAL_DRS_DICT",
    "DRS_RECORD_SCHEMA_V0",
    "SEMANTIC_DRS_RECORD_INPUT",
    "DRS_RECORD_V02",
    "DRS_FRESHNESS_ENVELOPE_V02",
    "TEMPORAL_QUERY_V02",
)
_PROJECTION_STATUSES = (
    "CANONICAL_CONTEXT_ONLY",
    "RERUN_REQUIRED",
    "BLOCKED",
    "PROJECTION_REJECTED",
    "CANONICAL_COMPLETE",
)
_FIELDS = (
    "projection_version",
    "projection_id",
    "source_family",
    "source_version",
    "source_identity",
    "source_hash",
    "target_semantic_address_id",
    "target_meaning_record_id",
    "projection_profile_version",
    "fields_preserved",
    "fields_synthesized",
    "fields_unavailable",
    "downgrade_restrictions",
    "projection_status",
    "answer_shortcut_eligible",
    "reason_codes",
    "creates_authority",
    "creates_permission",
)
_DOMAIN = "hedgehog:drs:legacy_projection:v01"
_PREFIX = "drslegacyproj_v01:"
_LOCAL_REQUIRED_FIELDS = (
    "record_id",
    "layer",
    "type",
    "domain",
    "content",
    "time_envelope",
    "provenance",
    "status",
)
_LOCAL_ALLOWED_FIELDS = (
    "record_id",
    "layer",
    "type",
    "domain",
    "content",
    "pointer",
    "time_envelope",
    "provenance",
    "status",
    "gt",
    "viability_feedback",
    "validation",
    "hash",
    "previous_hash",
    "trace_refs",
    "source_refs",
)
_SEMANTIC_INPUT_FIELDS = (
    "record_id",
    "domain",
    "content",
    "semantic_keys",
    "layer",
    "record_type",
    "time_envelope",
    "provenance",
    "trace_refs",
    "source_refs",
    "status",
    "gt",
    "validation",
    "root_final_ref",
    "worldstate_ref",
    "poisoning_markers",
)
_LINEAGE_FIELDS = (
    "ref_id",
    "ref_kind",
    "relation",
    "source_observed_at",
    "system_ingested_at",
    "notes",
)
_FRESHNESS_FIELDS = (
    "physical_time",
    "knowledge_time",
    "event_time",
    "context_time",
    "ttl_seconds",
    "validity_start",
    "validity_end",
    "source_observed_at",
    "system_ingested_at",
    "freshness_class",
)
_RECORD_V02_FIELDS = (
    "record_id",
    "record_kind",
    "summary",
    "time_envelope",
    "lineage_refs",
    "source_refs",
    "provenance_refs",
    "prior_trace_ref",
    "root_final_ref",
    "artifact_refs",
    "validation_refs",
    "contains_receipt",
    "contains_action_permission",
    "accepted_evidence",
    "changed_facts",
    "conflict_pressure",
    "conflicting_provenance",
    "duplicate_poisoning_pressure",
    "wrong_domain_near_match",
    "quarantine_proximity",
    "deadend_proximity",
    "policy_ok",
    "permission_ok",
    "root_shortcut_allowed",
    "reuse_score",
    "semantic_similarity_score",
    "truth_claimed",
    "authority_claimed",
    "action_permission_claimed",
    "final_output_claimed",
)
_TEMPORAL_FIELDS = (
    "query_id",
    "as_of",
    "context_time",
    "freshness_bias",
    "time_range_start",
    "time_range_end",
    "require_root_review",
    "allow_direct_reuse_if_all_gates_pass",
)
_LAYERS = ("work", "thoughts", "up", "quarantine", "deadends")
_RECORD_TYPES = (
    "task_outcome",
    "profile",
    "identity_pointer",
    "document_pointer",
    "reflection",
    "protocol_patch",
    "validator_patch",
    "dead_end",
    "opportunity",
    "protocol_template",
    "trace_summary",
    "generic",
)
_RECORD_STATUSES = (
    "draft",
    "active",
    "accepted",
    "rejected",
    "quarantined",
    "archived",
    "no_update",
)
_CREATED_BY = (
    "root_orchestrator",
    "marenna",
    "up",
    "gt_validator",
    "post_vv",
    "executor",
)
_POINTER_STORAGE_KINDS = (
    "inline",
    "local_json",
    "local_secure_vault",
    "local_memory",
    "vector_store",
    "document_store",
    "project_store",
    "external_drs_pointer",
)
_FRESHNESS_CLASSES = (
    "fresh_context",
    "stale_warning",
    "expired_rerun_required",
    "changed_fact_rerun_required",
    "blocked_by_policy_or_conflict",
)
_SCHEMA_FRESHNESS_CLASSES = (
    "static",
    "slow_changing",
    "normal",
    "fast_changing",
    "real_time",
)
_FRESHNESS_BIASES = (
    "current",
    "historical",
    "balanced",
    "prefer_recent",
)
_RFC3339 = _re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T"
    r"[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?(?:Z|[+-][0-9]{2}:[0-9]{2})$"
)
_LEGACY_ID = _re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,255}$")


@_dataclass(frozen=True)
class LegacyDRSProjectionV01:
    projection_version: str
    projection_id: str
    source_family: str
    source_version: str
    source_identity: str
    source_hash: str
    target_semantic_address_id: str
    target_meaning_record_id: str | None
    projection_profile_version: str
    fields_preserved: tuple[str, ...]
    fields_synthesized: tuple[str, ...]
    fields_unavailable: tuple[str, ...]
    downgrade_restrictions: tuple[str, ...]
    projection_status: str
    answer_shortcut_eligible: bool
    reason_codes: tuple[str, ...]
    creates_authority: bool
    creates_permission: bool


_GENERATED_MEANING_WRAPPER_ID = _re.compile(
    r"\A(?:request|trace):drsmeaning_v01:[0-9a-f]{64}\Z"
)


def _legacy_string_secret_reason(value: str) -> str | None:
    # Lexical classification only; provenance and Root bindings are still checked.
    if _GENERATED_MEANING_WRAPPER_ID.fullmatch(value):
        return None
    return _secret_reason(value)


def _strict_json_plain(value: object, seen: set[int] | None = None) -> object:
    if seen is None:
        seen = set()
    if value is None or type(value) in (bool, int, str):
        if type(value) is str:
            reason = _legacy_string_secret_reason(value)
            if reason:
                raise ValueError(reason)
        return value
    if type(value) is float:
        if not _math.isfinite(value):
            raise ValueError("drs_legacy_source_invalid")
        return value
    if type(value) is list:
        marker = id(value)
        if marker in seen:
            raise ValueError("drs_legacy_source_invalid")
        seen.add(marker)
        result = [_strict_json_plain(item, seen) for item in value]
        seen.remove(marker)
        return result
    if type(value) is tuple:
        marker = id(value)
        if marker in seen:
            raise ValueError("drs_legacy_source_invalid")
        seen.add(marker)
        result = [_strict_json_plain(item, seen) for item in value]
        seen.remove(marker)
        return result
    if type(value) is dict:
        marker = id(value)
        if marker in seen:
            raise ValueError("drs_legacy_source_invalid")
        seen.add(marker)
        result: dict[str, object] = {}
        for key, item in value.items():
            if type(key) is not str:
                raise ValueError("drs_legacy_source_invalid")
            result[key] = _strict_json_plain(item, seen)
        seen.remove(marker)
        return result
    raise ValueError("drs_legacy_source_invalid")


def _fail() -> None:
    raise ValueError("drs_legacy_source_invalid")


def _exact_dict_keys(
    value: object,
    *,
    required: tuple[str, ...],
    allowed: tuple[str, ...],
) -> dict[str, object]:
    if type(value) is not dict or any(type(key) is not str for key in value):
        _fail()
    if any(name not in value for name in required):
        _fail()
    if any(name not in allowed for name in value):
        _fail()
    return value


def _legacy_id(value: object) -> bool:
    return (
        type(value) is str
        and _LEGACY_ID.fullmatch(value) is not None
        and _legacy_string_secret_reason(value) is None
    )


def _nonempty_text(value: object) -> bool:
    return (
        type(value) is str
        and bool(value)
        and len(value) <= 1024
        and _secret_reason(value) is None
    )


def _rfc3339(value: object, *, allow_none: bool = False) -> bool:
    return (
        value is None
        if allow_none
        else False
    ) or (
        type(value) is str
        and _RFC3339.fullmatch(value) is not None
        and _secret_reason(value) is None
    )


def _exact_string_sequence(
    value: object,
    *,
    container_type: type,
    references: bool = True,
) -> bool:
    if type(value) is not container_type:
        return False
    predicate = _legacy_id if references else _nonempty_text
    return all(predicate(item) for item in value)


def _exact_dataclass_fields(value: object, expected: tuple[str, ...]) -> bool:
    try:
        return tuple(field.name for field in _dataclass_fields(type(value))) == expected
    except (TypeError, AttributeError):
        return False


def _validate_trace_ref(value: object) -> None:
    mapping = _exact_dict_keys(
        value,
        required=("trace_id",),
        allowed=("trace_id", "span_id", "kind"),
    )
    if not _legacy_id(mapping["trace_id"]):
        _fail()
    if "span_id" in mapping and not _legacy_id(mapping["span_id"]):
        _fail()
    if "kind" in mapping and not _nonempty_text(mapping["kind"]):
        _fail()


def _validate_source_ref(value: object) -> None:
    mapping = _exact_dict_keys(
        value,
        required=("source",),
        allowed=("source", "source_id", "trace_ref"),
    )
    if mapping["source"] not in (
        "user",
        "system",
        "needle",
        "local_drs",
        "external_drs",
        "fallback",
        "executor",
        "validator",
    ):
        _fail()
    if "source_id" in mapping and not _legacy_id(mapping["source_id"]):
        _fail()
    if "trace_ref" in mapping:
        _validate_trace_ref(mapping["trace_ref"])


def _validate_time_envelope_dict(value: object) -> None:
    allowed = (
        "pt_created_at",
        "kt_asof",
        "et_observed_at",
        "ct_session_anchor",
        "ttl_seconds",
        "freshness_class",
        "valid_from",
        "valid_to",
    )
    mapping = _exact_dict_keys(
        value,
        required=("pt_created_at", "kt_asof", "ct_session_anchor", "ttl_seconds"),
        allowed=allowed,
    )
    if not _rfc3339(mapping["pt_created_at"]) or not _rfc3339(mapping["kt_asof"]):
        _fail()
    if "et_observed_at" in mapping and not _rfc3339(
        mapping["et_observed_at"], allow_none=True
    ):
        _fail()
    if not _legacy_id(mapping["ct_session_anchor"]):
        _fail()
    if type(mapping["ttl_seconds"]) is not int or mapping["ttl_seconds"] < 0:
        _fail()
    if (
        "freshness_class" in mapping
        and mapping["freshness_class"] not in _SCHEMA_FRESHNESS_CLASSES
    ):
        _fail()
    for name in ("valid_from", "valid_to"):
        if name in mapping and not _rfc3339(mapping[name], allow_none=True):
            _fail()


def _validate_provenance_dict(value: object) -> None:
    mapping = _exact_dict_keys(
        value,
        required=("request_id", "created_by", "trace_refs"),
        allowed=("request_id", "created_by", "trace_refs"),
    )
    if not _legacy_id(mapping["request_id"]) or mapping["created_by"] not in _CREATED_BY:
        _fail()
    if type(mapping["trace_refs"]) is not list:
        _fail()
    for item in mapping["trace_refs"]:
        _validate_trace_ref(item)


def _validate_pointer_dict(value: object) -> None:
    mapping = _exact_dict_keys(
        value,
        required=("storage_kind", "ref"),
        allowed=("storage_kind", "ref", "access_policy", "summary", "hash"),
    )
    if mapping["storage_kind"] not in _POINTER_STORAGE_KINDS:
        _fail()
    if not _nonempty_text(mapping["ref"]):
        _fail()
    if "summary" in mapping and not _nonempty_text(mapping["summary"]):
        _fail()
    if "hash" in mapping and not _nonempty_text(mapping["hash"]):
        _fail()
    if "access_policy" in mapping:
        policy = _exact_dict_keys(
            mapping["access_policy"],
            required=(),
            allowed=(
                "visibility",
                "requires_user_confirmation",
                "read_summary_only",
                "read_payload_allowed",
                "write_allowed",
                "allowed_use",
                "forbidden_use",
            ),
        )
        if "visibility" in policy and policy["visibility"] not in (
            "private",
            "team",
            "project",
            "public",
        ):
            _fail()
        for name in (
            "requires_user_confirmation",
            "read_summary_only",
            "read_payload_allowed",
            "write_allowed",
        ):
            if name in policy and type(policy[name]) is not bool:
                _fail()
        for name in ("allowed_use", "forbidden_use"):
            if name in policy and not _exact_string_sequence(
                policy[name], container_type=list, references=False
            ):
                _fail()


def _validate_optional_schema_objects(mapping: dict[str, object]) -> None:
    if "gt" in mapping:
        gt = _exact_dict_keys(
            mapping["gt"],
            required=(),
            allowed=("gt_report_id", "elo", "regret", "half_life_hours", "decay_rate"),
        )
        if "gt_report_id" in gt and not _legacy_id(gt["gt_report_id"]):
            _fail()
        for name in ("elo", "regret", "half_life_hours", "decay_rate"):
            if name in gt and (
                type(gt[name]) not in (int, float)
                or not _math.isfinite(gt[name])
                or (name != "elo" and gt[name] < 0)
            ):
                _fail()
    if "viability_feedback" in mapping:
        feedback = _exact_dict_keys(
            mapping["viability_feedback"],
            required=(),
            allowed=("vector_id", "predicted", "actual", "delta", "failure_modes"),
        )
        if "vector_id" in feedback and not _legacy_id(feedback["vector_id"]):
            _fail()
        for name in ("predicted", "actual"):
            if name in feedback and (
                type(feedback[name]) not in (int, float)
                or not _math.isfinite(feedback[name])
                or not 0 <= feedback[name] <= 1
            ):
                _fail()
        if "delta" in feedback and (
            type(feedback["delta"]) not in (int, float)
            or not _math.isfinite(feedback["delta"])
        ):
            _fail()
        if "failure_modes" in feedback and not _exact_string_sequence(
            feedback["failure_modes"], container_type=list, references=False
        ):
            _fail()
    if "validation" in mapping:
        validation = _exact_dict_keys(
            mapping["validation"],
            required=(),
            allowed=("vv_report_id", "validated_at", "decision"),
        )
        if "vv_report_id" in validation and not _legacy_id(validation["vv_report_id"]):
            _fail()
        if "validated_at" in validation and not _rfc3339(validation["validated_at"]):
            _fail()
        if "decision" in validation and validation["decision"] not in (
            "accept",
            "reject",
            "revise",
            "no_update",
        ):
            _fail()


def _validate_schema_record_mapping(value: object) -> dict[str, object]:
    mapping = _exact_dict_keys(
        value,
        required=_LOCAL_REQUIRED_FIELDS,
        allowed=_LOCAL_ALLOWED_FIELDS,
    )
    if not _legacy_id(mapping["record_id"]):
        raise ValueError("drs_legacy_source_identity_invalid")
    if mapping["layer"] not in _LAYERS or mapping["type"] not in _RECORD_TYPES:
        _fail()
    if not _legacy_id(mapping["domain"]) or mapping["status"] not in _RECORD_STATUSES:
        _fail()
    if type(mapping["content"]) is not dict:
        _fail()
    _strict_json_plain(mapping["content"])
    _validate_time_envelope_dict(mapping["time_envelope"])
    _validate_provenance_dict(mapping["provenance"])
    if "pointer" in mapping:
        _validate_pointer_dict(mapping["pointer"])
    _validate_optional_schema_objects(mapping)
    for name in ("hash", "previous_hash"):
        if name in mapping and not _nonempty_text(mapping[name]):
            _fail()
    if "trace_refs" in mapping:
        if type(mapping["trace_refs"]) is not list:
            _fail()
        for item in mapping["trace_refs"]:
            _validate_trace_ref(item)
    if "source_refs" in mapping:
        if type(mapping["source_refs"]) is not list:
            _fail()
        for item in mapping["source_refs"]:
            _validate_source_ref(item)
    return mapping


def _validate_local_drs_dict_source(value: object) -> None:
    _validate_schema_record_mapping(value)


def _validate_drs_record_schema_v0_source(value: object) -> None:
    _validate_schema_record_mapping(value)


def _validate_lineage_source(value: object) -> None:
    if type(value) is not _DRSLineageRef or not _exact_dataclass_fields(
        value, _LINEAGE_FIELDS
    ):
        _fail()
    if not all(
        _legacy_id(item)
        for item in (value.ref_id, value.ref_kind, value.relation)
    ):
        _fail()
    if not _rfc3339(value.source_observed_at, allow_none=True):
        _fail()
    if not _rfc3339(value.system_ingested_at, allow_none=True):
        _fail()
    if not _exact_string_sequence(
        value.notes, container_type=tuple, references=False
    ):
        _fail()


def _validate_freshness_source(value: object) -> None:
    if type(value) is not _DRSFreshnessEnvelope or not _exact_dataclass_fields(
        value, _FRESHNESS_FIELDS
    ):
        _fail()
    for item in (value.physical_time, value.knowledge_time, value.event_time):
        if not _rfc3339(item):
            _fail()
    if not _legacy_id(value.context_time):
        _fail()
    if value.ttl_seconds is not None and (
        type(value.ttl_seconds) is not int or value.ttl_seconds < 0
    ):
        _fail()
    for item in (
        value.validity_start,
        value.validity_end,
        value.source_observed_at,
        value.system_ingested_at,
    ):
        if not _rfc3339(item, allow_none=True):
            _fail()
    if value.freshness_class not in _FRESHNESS_CLASSES:
        _fail()
    if _validate_legacy_freshness_envelope(value) != (True, ()):
        _fail()


def _validate_temporal_source(value: object) -> None:
    if type(value) is not _TemporalQueryV02 or not _exact_dataclass_fields(
        value, _TEMPORAL_FIELDS
    ):
        _fail()
    if not _legacy_id(value.query_id):
        raise ValueError("drs_legacy_source_identity_invalid")
    if not _rfc3339(value.as_of) or not _legacy_id(value.context_time):
        _fail()
    if value.freshness_bias not in _FRESHNESS_BIASES:
        _fail()
    if not _rfc3339(value.time_range_start, allow_none=True):
        _fail()
    if not _rfc3339(value.time_range_end, allow_none=True):
        _fail()
    if type(value.require_root_review) is not bool:
        _fail()
    if type(value.allow_direct_reuse_if_all_gates_pass) is not bool:
        _fail()
    if _validate_legacy_temporal_query(value) != (True, ()):
        _fail()


def _validate_record_v02_source(value: object) -> None:
    if type(value) is not _DRSRecordV02 or not _exact_dataclass_fields(
        value, _RECORD_V02_FIELDS
    ):
        _fail()
    if not _legacy_id(value.record_id):
        raise ValueError("drs_legacy_source_identity_invalid")
    if not _legacy_id(value.record_kind) or not _nonempty_text(value.summary):
        _fail()
    if value.time_envelope is not None:
        _validate_freshness_source(value.time_envelope)
    if type(value.lineage_refs) is not tuple:
        _fail()
    for item in value.lineage_refs:
        _validate_lineage_source(item)
    for sequence in (
        value.source_refs,
        value.provenance_refs,
        value.artifact_refs,
        value.validation_refs,
    ):
        if not _exact_string_sequence(
            sequence, container_type=tuple, references=True
        ):
            _fail()
    for item in (value.prior_trace_ref, value.root_final_ref):
        if item is not None and not _legacy_id(item):
            _fail()
    for name in _RECORD_V02_FIELDS[11:24]:
        if type(getattr(value, name)) is not bool:
            _fail()
    if type(value.reuse_score) is not float or not _math.isfinite(value.reuse_score):
        _fail()
    if value.semantic_similarity_score is not None and (
        type(value.semantic_similarity_score) is not float
        or not _math.isfinite(value.semantic_similarity_score)
    ):
        _fail()
    for name in _RECORD_V02_FIELDS[26:]:
        if type(getattr(value, name)) is not bool:
            _fail()


def _validate_semantic_input_source(value: object) -> None:
    if type(value) is not _SemanticDRSRecordInput or not _exact_dataclass_fields(
        value, _SEMANTIC_INPUT_FIELDS
    ):
        _fail()
    if not _legacy_id(value.record_id):
        raise ValueError("drs_legacy_source_identity_invalid")
    if not _legacy_id(value.domain) or type(value.content) is not dict:
        _fail()
    _strict_json_plain(value.content)
    if not _exact_string_sequence(
        value.semantic_keys, container_type=tuple, references=True
    ):
        _fail()
    if value.layer not in _LAYERS or value.record_type not in _RECORD_TYPES:
        _fail()
    if value.time_envelope is not None:
        if type(value.time_envelope) is not dict:
            _fail()
        _strict_json_plain(value.time_envelope)
    if value.provenance is not None:
        if type(value.provenance) is not dict:
            _fail()
        _strict_json_plain(value.provenance)
    for sequence, validator in (
        (value.trace_refs, _validate_trace_ref),
        (value.source_refs, _validate_source_ref),
    ):
        if type(sequence) is not tuple:
            _fail()
        for item in sequence:
            validator(item)
    if value.status not in _RECORD_STATUSES:
        _fail()
    for mapping in (value.gt, value.validation):
        if mapping is not None:
            if type(mapping) is not dict:
                _fail()
            _strict_json_plain(mapping)
    for item in (value.root_final_ref, value.worldstate_ref):
        if item is not None and not _legacy_id(item):
            _fail()
    if not _exact_string_sequence(
        value.poisoning_markers, container_type=tuple, references=False
    ):
        _fail()


def _lineage_plain(value: _DRSLineageRef) -> dict[str, object]:
    _validate_lineage_source(value)
    return {
        "ref_id": _strict_json_plain(value.ref_id),
        "ref_kind": _strict_json_plain(value.ref_kind),
        "relation": _strict_json_plain(value.relation),
        "source_observed_at": _strict_json_plain(value.source_observed_at),
        "system_ingested_at": _strict_json_plain(value.system_ingested_at),
        "notes": _strict_json_plain(value.notes),
    }


def _freshness_plain(value: _DRSFreshnessEnvelope) -> dict[str, object]:
    _validate_freshness_source(value)
    return {
        "physical_time": _strict_json_plain(value.physical_time),
        "knowledge_time": _strict_json_plain(value.knowledge_time),
        "event_time": _strict_json_plain(value.event_time),
        "context_time": _strict_json_plain(value.context_time),
        "ttl_seconds": _strict_json_plain(value.ttl_seconds),
        "validity_start": _strict_json_plain(value.validity_start),
        "validity_end": _strict_json_plain(value.validity_end),
        "source_observed_at": _strict_json_plain(value.source_observed_at),
        "system_ingested_at": _strict_json_plain(value.system_ingested_at),
        "freshness_class": _strict_json_plain(value.freshness_class),
    }


def _temporal_plain(value: _TemporalQueryV02) -> dict[str, object]:
    _validate_temporal_source(value)
    return {
        "query_id": _strict_json_plain(value.query_id),
        "as_of": _strict_json_plain(value.as_of),
        "context_time": _strict_json_plain(value.context_time),
        "freshness_bias": _strict_json_plain(value.freshness_bias),
        "time_range_start": _strict_json_plain(value.time_range_start),
        "time_range_end": _strict_json_plain(value.time_range_end),
        "require_root_review": _strict_json_plain(value.require_root_review),
        "allow_direct_reuse_if_all_gates_pass": _strict_json_plain(
            value.allow_direct_reuse_if_all_gates_pass
        ),
    }


def _record_v02_plain(value: _DRSRecordV02) -> dict[str, object]:
    _validate_record_v02_source(value)
    return {
        "record_id": _strict_json_plain(value.record_id),
        "record_kind": _strict_json_plain(value.record_kind),
        "summary": _strict_json_plain(value.summary),
        "time_envelope": (
            None
            if value.time_envelope is None
            else _freshness_plain(value.time_envelope)
        ),
        "lineage_refs": [_lineage_plain(item) for item in value.lineage_refs],
        "source_refs": _strict_json_plain(value.source_refs),
        "provenance_refs": _strict_json_plain(value.provenance_refs),
        "prior_trace_ref": _strict_json_plain(value.prior_trace_ref),
        "root_final_ref": _strict_json_plain(value.root_final_ref),
        "artifact_refs": _strict_json_plain(value.artifact_refs),
        "validation_refs": _strict_json_plain(value.validation_refs),
        "contains_receipt": value.contains_receipt,
        "contains_action_permission": value.contains_action_permission,
        "accepted_evidence": value.accepted_evidence,
        "changed_facts": value.changed_facts,
        "conflict_pressure": value.conflict_pressure,
        "conflicting_provenance": value.conflicting_provenance,
        "duplicate_poisoning_pressure": value.duplicate_poisoning_pressure,
        "wrong_domain_near_match": value.wrong_domain_near_match,
        "quarantine_proximity": value.quarantine_proximity,
        "deadend_proximity": value.deadend_proximity,
        "policy_ok": value.policy_ok,
        "permission_ok": value.permission_ok,
        "root_shortcut_allowed": value.root_shortcut_allowed,
        "reuse_score": _strict_json_plain(value.reuse_score),
        "semantic_similarity_score": _strict_json_plain(
            value.semantic_similarity_score
        ),
        "truth_claimed": value.truth_claimed,
        "authority_claimed": value.authority_claimed,
        "action_permission_claimed": value.action_permission_claimed,
        "final_output_claimed": value.final_output_claimed,
    }


def _semantic_input_plain(value: _SemanticDRSRecordInput) -> dict[str, object]:
    _validate_semantic_input_source(value)
    return {
        "record_id": _strict_json_plain(value.record_id),
        "domain": _strict_json_plain(value.domain),
        "content": _strict_json_plain(value.content),
        "semantic_keys": _strict_json_plain(value.semantic_keys),
        "layer": _strict_json_plain(value.layer),
        "record_type": _strict_json_plain(value.record_type),
        "time_envelope": _strict_json_plain(value.time_envelope),
        "provenance": _strict_json_plain(value.provenance),
        "trace_refs": _strict_json_plain(value.trace_refs),
        "source_refs": _strict_json_plain(value.source_refs),
        "status": _strict_json_plain(value.status),
        "gt": _strict_json_plain(value.gt),
        "validation": _strict_json_plain(value.validation),
        "root_final_ref": _strict_json_plain(value.root_final_ref),
        "worldstate_ref": _strict_json_plain(value.worldstate_ref),
        "poisoning_markers": _strict_json_plain(value.poisoning_markers),
    }


def _dict_source_plain(
    value: object,
    *,
    validator: object,
    field_order: tuple[str, ...],
) -> dict[str, object]:
    if not callable(validator):
        _fail()
    validator(value)
    return {
        name: _strict_json_plain(value[name])
        for name in field_order
        if name in value
    }


_SOURCE_PROFILES = (
    (
        "LOCAL_DRS_DICT",
        dict,
        _LOCAL_REQUIRED_FIELDS,
        _LOCAL_ALLOWED_FIELDS,
        "record_id",
        "legacy_local_drs_dict_v0",
        _validate_local_drs_dict_source,
    ),
    (
        "DRS_RECORD_SCHEMA_V0",
        dict,
        _LOCAL_REQUIRED_FIELDS,
        _LOCAL_ALLOWED_FIELDS,
        "record_id",
        "drs_record_schema_v0",
        _validate_drs_record_schema_v0_source,
    ),
    (
        "SEMANTIC_DRS_RECORD_INPUT",
        _SemanticDRSRecordInput,
        _SEMANTIC_INPUT_FIELDS,
        _SEMANTIC_INPUT_FIELDS,
        "record_id",
        "semantic_drs_record_input_v0",
        _validate_semantic_input_source,
    ),
    (
        "DRS_RECORD_V02",
        _DRSRecordV02,
        _RECORD_V02_FIELDS,
        _RECORD_V02_FIELDS,
        "record_id",
        "drs_record_v02",
        _validate_record_v02_source,
    ),
    (
        "DRS_FRESHNESS_ENVELOPE_V02",
        _DRSFreshnessEnvelope,
        _FRESHNESS_FIELDS,
        _FRESHNESS_FIELDS,
        None,
        "drs_freshness_envelope_v02",
        _validate_freshness_source,
    ),
    (
        "TEMPORAL_QUERY_V02",
        _TemporalQueryV02,
        _TEMPORAL_FIELDS,
        _TEMPORAL_FIELDS,
        "query_id",
        "temporal_query_v02",
        _validate_temporal_source,
    ),
)


def _source_profile(source_family: str) -> tuple[object, ...]:
    for profile in _SOURCE_PROFILES:
        if profile[0] == source_family:
            return profile
    raise ValueError("drs_legacy_source_family_invalid")


def _source_version(source_family: str) -> str:
    return _source_profile(source_family)[5]


def _source_plain(source_family: str, source: object) -> dict[str, object]:
    profile = _source_profile(source_family)
    if type(source) is not profile[1]:
        raise ValueError("drs_legacy_source_family_type_mismatch")
    if source_family == "LOCAL_DRS_DICT":
        return _dict_source_plain(
            source,
            validator=_validate_local_drs_dict_source,
            field_order=_LOCAL_ALLOWED_FIELDS,
        )
    if source_family == "DRS_RECORD_SCHEMA_V0":
        return _dict_source_plain(
            source,
            validator=_validate_drs_record_schema_v0_source,
            field_order=_LOCAL_ALLOWED_FIELDS,
        )
    if source_family == "SEMANTIC_DRS_RECORD_INPUT":
        return _semantic_input_plain(source)
    if source_family == "DRS_RECORD_V02":
        return _record_v02_plain(source)
    if source_family == "DRS_FRESHNESS_ENVELOPE_V02":
        return _freshness_plain(source)
    if source_family == "TEMPORAL_QUERY_V02":
        return _temporal_plain(source)
    raise ValueError("drs_legacy_source_family_invalid")


def _source_identity(
    source_family: str,
    source_plain: dict[str, object],
    source_hash: str,
) -> str:
    if source_family in (
        "LOCAL_DRS_DICT",
        "DRS_RECORD_SCHEMA_V0",
        "SEMANTIC_DRS_RECORD_INPUT",
        "DRS_RECORD_V02",
    ):
        value = source_plain.get("record_id")
        if not _legacy_id(value):
            raise ValueError("drs_legacy_source_identity_invalid")
        return value
    if source_family == "TEMPORAL_QUERY_V02":
        value = source_plain.get("query_id")
        if not _legacy_id(value):
            raise ValueError("drs_legacy_source_identity_invalid")
        return value
    return "legacy_freshness_v02:" + source_hash


def _profile_evidence(
    source_family: str,
    source_plain: dict[str, object],
    *,
    target_record_present: bool,
) -> tuple[
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
    str,
    tuple[str, ...],
]:
    profile = _source_profile(source_family)
    preserved = tuple(name for name in profile[3] if name in source_plain)
    synthesized = (
        "target_semantic_address_id",
        "projection_profile_version",
    )
    unavailable_by_family = (
        ("LOCAL_DRS_DICT", ("root_decision_evidence", "exact_epoch_time")),
        ("DRS_RECORD_SCHEMA_V0", ("root_decision_evidence", "exact_epoch_time")),
        (
            "SEMANTIC_DRS_RECORD_INPUT",
            ("canonical_authority_envelope", "exact_epoch_time"),
        ),
        (
            "DRS_RECORD_V02",
            ()
            if target_record_present
            else ("canonical_meaning_record", "exact_epoch_time"),
        ),
        (
            "DRS_FRESHNESS_ENVELOPE_V02",
            ("semantic_address_source", "meaning_record_source"),
        ),
        (
            "TEMPORAL_QUERY_V02",
            ("canonical_meaning_record", "root_decision_evidence"),
        ),
    )
    unavailable = next(
        fields for family, fields in unavailable_by_family if family == source_family
    )
    restrictions = (
        "answer_shortcut_forbidden_in_g2b1",
        "root_review_required",
        "legacy_object_not_canonical",
    )
    if source_family in ("LOCAL_DRS_DICT", "DRS_RECORD_SCHEMA_V0"):
        status = "CANONICAL_CONTEXT_ONLY"
        reasons = ("drs_legacy_context_only",)
    elif source_family == "SEMANTIC_DRS_RECORD_INPUT":
        status = "RERUN_REQUIRED"
        reasons = ("drs_legacy_rerun_required",)
    elif source_family == "DRS_RECORD_V02":
        status = (
            "CANONICAL_COMPLETE"
            if target_record_present
            else "RERUN_REQUIRED"
        )
        reasons = (
            ()
            if target_record_present
            else ("drs_legacy_rerun_required",)
        )
    elif source_family == "DRS_FRESHNESS_ENVELOPE_V02":
        status = "PROJECTION_REJECTED"
        reasons = ("drs_legacy_projection_incomplete",)
    else:
        status = (
            "BLOCKED"
            if source_plain.get("allow_direct_reuse_if_all_gates_pass") is True
            else "CANONICAL_CONTEXT_ONLY"
        )
        reasons = (
            ("drs_legacy_projection_shortcut_forbidden",)
            if status == "BLOCKED"
            else ("drs_legacy_context_only",)
        )
    return preserved, synthesized, unavailable, restrictions, status, reasons


def _projection_profile_coherent(value: LegacyDRSProjectionV01) -> bool:
    profile = _source_profile(value.source_family)
    if value.source_version != profile[5]:
        return False
    if value.source_family == "DRS_FRESHNESS_ENVELOPE_V02":
        if (
            type(value.source_identity) is not str
            or not value.source_identity.startswith("legacy_freshness_v02:")
            or len(value.source_identity)
            != len("legacy_freshness_v02:") + 64
            or not _is_sha256(
                value.source_identity[len("legacy_freshness_v02:"):]
            )
        ):
            return False
    elif not _is_reference(value.source_identity):
        return False

    if value.source_family in ("LOCAL_DRS_DICT", "DRS_RECORD_SCHEMA_V0"):
        positions = tuple(
            profile[3].index(field_name)
            for field_name in value.fields_preserved
            if field_name in profile[3]
        )
        if (
            len(positions) != len(value.fields_preserved)
            or tuple(sorted(positions)) != positions
            or not set(profile[2]).issubset(value.fields_preserved)
        ):
            return False
    elif value.fields_preserved != profile[3]:
        return False

    expected_synthesized = (
        "target_semantic_address_id",
        "projection_profile_version",
    )
    expected_restrictions = (
        "answer_shortcut_forbidden_in_g2b1",
        "root_review_required",
        "legacy_object_not_canonical",
    )
    if (
        value.fields_synthesized != expected_synthesized
        or value.downgrade_restrictions != expected_restrictions
    ):
        return False

    target_present = value.target_meaning_record_id is not None
    expected_unavailable = {
        "LOCAL_DRS_DICT": (
            "root_decision_evidence",
            "exact_epoch_time",
        ),
        "DRS_RECORD_SCHEMA_V0": (
            "root_decision_evidence",
            "exact_epoch_time",
        ),
        "SEMANTIC_DRS_RECORD_INPUT": (
            "canonical_authority_envelope",
            "exact_epoch_time",
        ),
        "DRS_RECORD_V02": (
            ()
            if target_present
            else ("canonical_meaning_record", "exact_epoch_time")
        ),
        "DRS_FRESHNESS_ENVELOPE_V02": (
            "semantic_address_source",
            "meaning_record_source",
        ),
        "TEMPORAL_QUERY_V02": (
            "canonical_meaning_record",
            "root_decision_evidence",
        ),
    }[value.source_family]
    if value.fields_unavailable != expected_unavailable:
        return False
    if value.source_family != "DRS_RECORD_V02" and target_present:
        return False

    exact_status_reason = {
        "LOCAL_DRS_DICT": (
            "CANONICAL_CONTEXT_ONLY",
            ("drs_legacy_context_only",),
        ),
        "DRS_RECORD_SCHEMA_V0": (
            "CANONICAL_CONTEXT_ONLY",
            ("drs_legacy_context_only",),
        ),
        "SEMANTIC_DRS_RECORD_INPUT": (
            "RERUN_REQUIRED",
            ("drs_legacy_rerun_required",),
        ),
        "DRS_FRESHNESS_ENVELOPE_V02": (
            "PROJECTION_REJECTED",
            ("drs_legacy_projection_incomplete",),
        ),
    }
    if value.source_family == "DRS_RECORD_V02":
        expected = (
            ("CANONICAL_COMPLETE", ())
            if target_present
            else (
                "RERUN_REQUIRED",
                ("drs_legacy_rerun_required",),
            )
        )
        return (
            value.projection_status,
            value.reason_codes,
        ) == expected
    if value.source_family == "TEMPORAL_QUERY_V02":
        return (
            value.projection_status,
            value.reason_codes,
        ) in (
            (
                "BLOCKED",
                ("drs_legacy_projection_shortcut_forbidden",),
            ),
            (
                "CANONICAL_CONTEXT_ONLY",
                ("drs_legacy_context_only",),
            ),
        )
    return (
        value.projection_status,
        value.reason_codes,
    ) == exact_status_reason[value.source_family]


def _identity(value: LegacyDRSProjectionV01) -> str:
    material = [
        _canonical_plain_value(getattr(value, name))
        for name in _FIELDS
        if name != "projection_id"
    ]
    digest = _domain_separated_sha256_hex_v01(
        domain=_DOMAIN,
        payload=_canonical_json_bytes_v01(material),
    )
    return _PREFIX + digest


def _projection_reasons(
    value: object,
    *,
    check_identity: bool,
) -> tuple[str, ...]:
    if type(value) is not LegacyDRSProjectionV01:
        return ("drs_exact_type_required",)
    reasons: list[str] = []
    if type(value.projection_version) is not str:
        reasons.append("drs_exact_type_required")
    elif value.projection_version != _PROFILE_VERSION:
        reasons.append("drs_schema_version_mismatch")
    if type(value.source_family) is not str or value.source_family not in _SOURCE_FAMILIES:
        reasons.append("drs_legacy_source_family_invalid")
    if type(value.source_version) is not str:
        reasons.append("drs_legacy_source_invalid")
    if not _is_reference(value.source_identity):
        reasons.append("drs_legacy_source_identity_invalid")
    if not _is_sha256(value.source_hash):
        reasons.append("drs_legacy_source_invalid")
    if (
        type(value.target_semantic_address_id) is not str
        or not value.target_semantic_address_id.startswith("drsaddr_v01:")
        or len(value.target_semantic_address_id) != len("drsaddr_v01:") + 64
        or not _is_sha256(value.target_semantic_address_id[len("drsaddr_v01:"):])
    ):
        reasons.append("drs_legacy_projection_incomplete")
    if value.target_meaning_record_id is not None and (
        type(value.target_meaning_record_id) is not str
        or not value.target_meaning_record_id.startswith("drsmeaning_v01:")
        or len(value.target_meaning_record_id) != len("drsmeaning_v01:") + 64
        or not _is_sha256(value.target_meaning_record_id[len("drsmeaning_v01:"):])
    ):
        reasons.append("drs_legacy_projection_incomplete")
    if value.projection_profile_version != _PROFILE_VERSION or type(
        value.projection_profile_version
    ) is not str:
        reasons.append("drs_schema_version_mismatch")
    for tuple_value in (
        value.fields_preserved,
        value.fields_synthesized,
        value.fields_unavailable,
    ):
        reasons.extend(
            _field_name_tuple_reasons(tuple_value, maximum_items=128)
        )
    for tuple_value in (
        value.downgrade_restrictions,
        value.reason_codes,
    ):
        reasons.extend(
            _token_tuple_reasons(tuple_value, maximum_items=128)
        )
    if type(value.projection_status) is not str or value.projection_status not in _PROJECTION_STATUSES:
        reasons.append("drs_legacy_projection_incomplete")
    if value.answer_shortcut_eligible is not False:
        reasons.append("drs_legacy_projection_shortcut_forbidden")
    if value.creates_authority is not False:
        reasons.append("drs_non_authority_law_invalid")
    if value.creates_permission is not False:
        reasons.append("drs_non_permission_law_invalid")
    if (
        type(value.source_family) is str
        and value.source_family in _SOURCE_FAMILIES
        and type(value.source_version) is str
        and type(value.source_identity) is str
        and type(value.fields_preserved) is tuple
        and type(value.fields_synthesized) is tuple
        and type(value.fields_unavailable) is tuple
        and type(value.downgrade_restrictions) is tuple
        and type(value.reason_codes) is tuple
        and not _projection_profile_coherent(value)
    ):
        reasons.append("drs_legacy_projection_incomplete")
    if check_identity and not reasons:
        if (
            type(value.projection_id) is not str
            or not value.projection_id.startswith(_PREFIX)
            or len(value.projection_id) != len(_PREFIX) + 64
            or not _is_sha256(value.projection_id[len(_PREFIX):])
            or value.projection_id != _identity(value)
        ):
            reasons.append("drs_identity_invalid")
    return _dedupe(reasons)


def _project(
    *,
    source_family: str,
    source: object,
    target_semantic_address: SemanticAddressV01,
    target_meaning_record: MeaningRecordV01 | None,
) -> LegacyDRSProjectionV01:
    if type(source_family) is not str or source_family not in _SOURCE_FAMILIES:
        raise ValueError("drs_legacy_source_family_invalid")
    address_valid, address_reasons = validate_semantic_address_v01(
        target_semantic_address
    )
    if not address_valid:
        raise ValueError(address_reasons[0])
    if target_meaning_record is not None:
        record_valid, record_reasons = validate_meaning_record_v01(
            target_meaning_record
        )
        if not record_valid:
            raise ValueError(record_reasons[0])
        if type(target_meaning_record) is not MeaningRecordV01:
            raise ValueError("drs_exact_type_required")
        if (
            target_meaning_record.semantic_address.semantic_address_id
            != target_semantic_address.semantic_address_id
        ):
            raise ValueError("drs_legacy_projection_incomplete")
    plain = _source_plain(source_family, source)
    source_hash = _domain_separated_sha256_hex_v01(
        domain="hedgehog:drs:legacy_source:" + source_family.lower() + ":v01",
        payload=_canonical_json_bytes_v01(plain),
    )
    source_identity = _source_identity(source_family, plain, source_hash)
    (
        preserved,
        synthesized,
        unavailable,
        restrictions,
        status,
        reasons,
    ) = _profile_evidence(
        source_family,
        plain,
        target_record_present=target_meaning_record is not None,
    )
    provisional = LegacyDRSProjectionV01(
        projection_version=_PROFILE_VERSION,
        projection_id=_PREFIX + "0" * 64,
        source_family=source_family,
        source_version=_source_version(source_family),
        source_identity=source_identity,
        source_hash=source_hash,
        target_semantic_address_id=target_semantic_address.semantic_address_id,
        target_meaning_record_id=(
            None
            if target_meaning_record is None
            else target_meaning_record.meaning_record_id
        ),
        projection_profile_version=_PROFILE_VERSION,
        fields_preserved=preserved,
        fields_synthesized=synthesized,
        fields_unavailable=unavailable,
        downgrade_restrictions=restrictions,
        projection_status=status,
        answer_shortcut_eligible=False,
        reason_codes=reasons,
        creates_authority=False,
        creates_permission=False,
    )
    intrinsic = _projection_reasons(provisional, check_identity=False)
    if intrinsic:
        raise ValueError(intrinsic[0])
    final = _replace(provisional, projection_id=_identity(provisional))
    valid, final_reasons = validate_legacy_drs_projection_v01(final)
    if not valid:
        raise ValueError(final_reasons[0])
    return final


def build_legacy_drs_projection_v01(
    *,
    source_family: str,
    source: object,
    target_semantic_address: SemanticAddressV01,
    target_meaning_record: MeaningRecordV01 | None = None,
) -> LegacyDRSProjectionV01:
    try:
        return _project(
            source_family=source_family,
            source=source,
            target_semantic_address=target_semantic_address,
            target_meaning_record=target_meaning_record,
        )
    except ValueError as exc:
        reason = str(exc)
        raise ValueError(
            reason if reason.startswith("drs_") else "drs_legacy_projection_invalid"
        ) from None
    except Exception:
        raise ValueError("drs_legacy_projection_invalid") from None


def project_legacy_drs_source_v01(
    *,
    source_family: str,
    source: object,
    target_semantic_address: SemanticAddressV01,
    target_meaning_record: MeaningRecordV01 | None = None,
) -> LegacyDRSProjectionV01:
    return build_legacy_drs_projection_v01(
        source_family=source_family,
        source=source,
        target_semantic_address=target_semantic_address,
        target_meaning_record=target_meaning_record,
    )


def validate_legacy_drs_projection_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    try:
        reasons = _projection_reasons(value, check_identity=True)
        return not reasons, reasons
    except Exception:
        return False, ("drs_legacy_projection_invalid",)


def legacy_drs_projection_to_plain_data_v01(
    value: object,
) -> dict[str, object]:
    if type(value) is not LegacyDRSProjectionV01:
        raise ValueError("drs_exact_type_required") from None
    return {
        name: _plain_data_value(getattr(value, name))
        for name in _FIELDS
    }


__all__ = (
    "LegacyDRSProjectionV01",
    "build_legacy_drs_projection_v01",
    "validate_legacy_drs_projection_v01",
    "legacy_drs_projection_to_plain_data_v01",
    "project_legacy_drs_source_v01",
)
