"""Canonical G2-B semantic address and immutable base record contracts."""

from __future__ import annotations

from dataclasses import dataclass as _dataclass
from dataclasses import fields as _fields
from dataclasses import replace as _replace
import re as _re

from hedgehog.kernel.integrity_replay_v01 import (
    canonical_json_bytes_v01 as _canonical_json_bytes_v01,
)
from hedgehog.kernel.integrity_replay_v01 import (
    domain_separated_sha256_hex_v01 as _domain_separated_sha256_hex_v01,
)


DRS_G2B_PROFILE_VERSION_V01 = "v0.1"
SEMANTIC_ADDRESS_PROFILE_VERSION_V01 = "v0.1"

DRS_MEMORY_POINTER_STORAGE_CLASSES_V01 = (
    "LOCAL_MEANING_RECORD",
    "LOCAL_LINEAGE_SET",
    "LOCAL_CONFLICT_SET",
    "LOCAL_DEADEND_PROOF",
)
DRS_ARTIFACT_POINTER_STORAGE_CLASSES_V01 = (
    "LOCAL_DOCUMENT",
    "LOCAL_AUDIT_TRACE",
    "LOCAL_SEALED_EVIDENCE",
)
DRS_PERSISTENT_LIFECYCLE_STATES_V01 = (
    "ACTIVE",
    "COMPLETED",
    "REJECTED",
    "QUARANTINED",
    "DEADEND",
    "ARCHIVED",
)

_SENSITIVITY_CLASSES = (
    "PUBLIC",
    "INTERNAL",
    "CONFIDENTIAL_REFERENCE_ONLY",
    "SECRET_REFERENCE_ONLY",
)
_LINEAGE_RELATION_CLASSES = (
    "DERIVED_FROM",
    "SUPPORTS",
    "WARNS_AGAINST",
    "CONTRADICTS",
    "SUPERSEDES",
    "REPLACES",
    "SAME_TRACE",
    "REFERENCES",
    "BLOCKED_BY_POLICY",
    "DEGRADED_FROM",
)
_AUTHORITY_CLASSES = (
    "UNTRUSTED_SEMANTIC_DRAFT",
    "CONNECTOR_OBSERVATION",
    "EVIDENCE_CANDIDATE",
    "ROOT_ACCEPTED_CONTEXT",
    "ROOT_ACCEPTED_WORK",
    "ROOT_FINAL_REFERENCE",
    "ACTION_HISTORY_REFERENCE",
)
_ROOT_ACCEPTANCE_STATES = (
    "UNREVIEWED",
    "ACCEPTED_CONTEXT",
    "ACCEPTED_WORK",
    "REJECTED",
    "QUARANTINED",
)
_ROOT_EVIDENCE_AUTHORITY_CLASSES = (
    "ROOT_ACCEPTED_CONTEXT",
    "ROOT_ACCEPTED_WORK",
    "ROOT_FINAL_REFERENCE",
)
_INT64_MIN = -(2**63)
_INT64_MAX = 2**63 - 1
_SHA256_HEX = _re.compile(r"\A[0-9a-f]{64}\Z")
_TOKEN = _re.compile(r"\A[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}\Z")
_MEDIA_TYPE = _re.compile(
    r"\A[A-Za-z0-9][A-Za-z0-9.+-]*/"
    r"[A-Za-z0-9][A-Za-z0-9.+-]{0,126}\Z"
)
_REFERENCE = _re.compile(
    r"\A[A-Za-z0-9][A-Za-z0-9._:/#-]{0,255}\Z"
)
_FIELD_NAME = _re.compile(r"\A[a-z][a-z0-9_]{0,127}\Z")
_SEALED_REFERENCE = _re.compile(
    r"\A(?:"
    r"sealed-secret-ref:[A-Za-z0-9][A-Za-z0-9._:/#-]{0,237}|"
    r"audit-ref:[A-Za-z0-9][A-Za-z0-9._:/#-]{0,245}|"
    r"scope-ref:[A-Za-z0-9][A-Za-z0-9._:/#-]{0,245}"
    r")\Z"
)
_G2B_CANONICAL_ID = _re.compile(
    r"\A(?:drsaddr|drsmem|drsart|drsedge|drsauth|drstime|drsmeaning|"
    r"drsquery|drsqeval|drscandidate|drsplan|drsbudget|drsdescentreq|"
    r"drsdescentres|drsrootshortcut|reusecert|drsreport|drslegacyproj|"
    r"drsg2ahistory)_v01:[0-9a-f]{64}\Z"
)
_PRIVATE_KEY = _re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----", _re.IGNORECASE)
_KEY_VALUE_SECRET = _re.compile(
    r"(?<![A-Za-z0-9])(?:"
    r"api_key|api-key|apikey|x-api-key|password|passwd|secret|token|"
    r"access_token|access-token|refresh_token|refresh-token|"
    r"client_secret|client-secret|"
    r"authentication_secret|authentication-secret|"
    r"bank_account|bank-account|iban|cvv"
    r")[=:]",
    _re.IGNORECASE,
)
_AUTHENTICATION_HEADER = _re.compile(
    r"(?<![A-Za-z0-9])(?:"
    r"(?:bearer|basic)[ \t]+\S|"
    r"authorization:[ \t]*\S"
    r")",
    _re.IGNORECASE,
)
_IBAN = _re.compile(
    r"(?<![A-Za-z0-9])"
    r"[A-Z][ ]?[A-Z][ ]?[0-9][ ]?[0-9]"
    r"(?:[ ]?[A-Z0-9]){11,30}"
    r"(?![ ]?[A-Z0-9])",
    _re.IGNORECASE,
)
_CARD_NUMBER = _re.compile(
    r"(?<![0-9])(?<![0-9][ -])"
    r"[0-9](?:[ -]?[0-9]){12,18}"
    r"(?![ -]?[0-9])"
)
_PASSPORT = _re.compile(
    r"(?<![A-Za-z0-9])passport[:_][ \t-]?"
    r"[A-Za-z0-9]*[0-9][A-Za-z0-9]*(?![A-Za-z0-9])",
    _re.IGNORECASE,
)

_SEMANTIC_ADDRESS_FIELDS = (
    "address_profile_version",
    "namespace",
    "domain",
    "subject_class",
    "intent_class",
    "meaning_schema_id",
    "meaning_schema_version",
    "semantic_address_id",
)
_MEMORY_POINTER_FIELDS = (
    "pointer_version",
    "pointer_id",
    "storage_class",
    "object_reference",
    "content_sha256",
    "record_class",
    "byte_length",
    "access_policy_id",
    "sensitivity_class",
    "allowed_use_classes",
    "forbidden_use_classes",
    "summary_read_permitted",
    "payload_read_permitted",
    "creates_authority",
    "creates_permission",
)
_ARTIFACT_POINTER_FIELDS = (
    "pointer_version",
    "pointer_id",
    "storage_class",
    "object_reference",
    "content_sha256",
    "media_type",
    "byte_length",
    "access_policy_id",
    "sensitivity_class",
    "allowed_use_classes",
    "forbidden_use_classes",
    "summary_read_permitted",
    "payload_read_permitted",
    "creates_authority",
    "creates_permission",
)
_LINEAGE_EDGE_FIELDS = (
    "lineage_edge_version",
    "lineage_edge_id",
    "source_meaning_record_id",
    "target_meaning_record_id",
    "relation_class",
    "claim_dimension",
    "source_history_hash",
    "evidence_ref_ids",
    "created_at",
    "recording_component",
    "creates_authority",
    "transfers_authority",
)
_AUTHORITY_ENVELOPE_FIELDS = (
    "authority_envelope_version",
    "authority_envelope_id",
    "authority_class",
    "owning_local_root_id",
    "source_root_decision_input_id",
    "source_root_decision_id",
    "source_root_decision_hash",
    "authority_scope_fingerprint",
    "root_acceptance_state",
    "recording_component",
    "creates_authority",
    "creates_permission",
    "action_permission_present",
)
_TIME_ENVELOPE_FIELDS = (
    "time_envelope_version",
    "time_envelope_id",
    "pt_created_at",
    "kt_as_of",
    "et_observed_at",
    "ct_context_anchor",
    "ttl_seconds",
    "valid_from",
    "valid_to",
    "source_observed_at",
    "source_reported_at",
    "system_ingested_at",
    "system_verified_at",
    "freshness_policy_id",
)
_MEANING_RECORD_FIELDS = (
    "meaning_record_version",
    "meaning_record_id",
    "semantic_address",
    "predecessor_record_id",
    "supersession_reason",
    "safe_summary",
    "semantic_tags",
    "resonance_reason",
    "memory_pointers",
    "artifact_pointers",
    "source_reference_ids",
    "lineage_edges",
    "time_envelope",
    "authority_envelope",
    "persistent_lifecycle_state",
    "risk_hints",
    "conflict_hints",
    "reuse_policy_class",
    "policy_version",
    "schema_versions",
    "content_fingerprint",
    "recording_component",
    "local_reference_kernel_scope",
    "creates_authority",
    "creates_permission",
)

_IDENTITY_PROFILES = (
    (
        "SemanticAddressV01",
        "semantic_address_id",
        "hedgehog:drs:semantic_address:v01",
        "drsaddr_v01:",
        _SEMANTIC_ADDRESS_FIELDS,
    ),
    (
        "MemoryPointerV01",
        "pointer_id",
        "hedgehog:drs:memory_pointer:v01",
        "drsmem_v01:",
        _MEMORY_POINTER_FIELDS,
    ),
    (
        "ArtifactPointerV01",
        "pointer_id",
        "hedgehog:drs:artifact_pointer:v01",
        "drsart_v01:",
        _ARTIFACT_POINTER_FIELDS,
    ),
    (
        "LineageEdgeV01",
        "lineage_edge_id",
        "hedgehog:drs:lineage_edge:v01",
        "drsedge_v01:",
        _LINEAGE_EDGE_FIELDS,
    ),
    (
        "DRSAuthorityEnvelopeV01",
        "authority_envelope_id",
        "hedgehog:drs:authority_envelope:v01",
        "drsauth_v01:",
        _AUTHORITY_ENVELOPE_FIELDS,
    ),
    (
        "DRSTimeEnvelopeV01",
        "time_envelope_id",
        "hedgehog:drs:time_envelope:v01",
        "drstime_v01:",
        _TIME_ENVELOPE_FIELDS,
    ),
    (
        "MeaningRecordV01",
        "meaning_record_id",
        "hedgehog:drs:meaning_record:v01",
        "drsmeaning_v01:",
        _MEANING_RECORD_FIELDS,
    ),
)


@_dataclass(frozen=True)
class SemanticAddressV01:
    address_profile_version: str
    namespace: str
    domain: str
    subject_class: str
    intent_class: str
    meaning_schema_id: str
    meaning_schema_version: str
    semantic_address_id: str


@_dataclass(frozen=True)
class MemoryPointerV01:
    pointer_version: str
    pointer_id: str
    storage_class: str
    object_reference: str
    content_sha256: str
    record_class: str
    byte_length: int | None
    access_policy_id: str
    sensitivity_class: str
    allowed_use_classes: tuple[str, ...]
    forbidden_use_classes: tuple[str, ...]
    summary_read_permitted: bool
    payload_read_permitted: bool
    creates_authority: bool
    creates_permission: bool


@_dataclass(frozen=True)
class ArtifactPointerV01:
    pointer_version: str
    pointer_id: str
    storage_class: str
    object_reference: str
    content_sha256: str
    media_type: str
    byte_length: int | None
    access_policy_id: str
    sensitivity_class: str
    allowed_use_classes: tuple[str, ...]
    forbidden_use_classes: tuple[str, ...]
    summary_read_permitted: bool
    payload_read_permitted: bool
    creates_authority: bool
    creates_permission: bool


@_dataclass(frozen=True)
class LineageEdgeV01:
    lineage_edge_version: str
    lineage_edge_id: str
    source_meaning_record_id: str
    target_meaning_record_id: str
    relation_class: str
    claim_dimension: str
    source_history_hash: str
    evidence_ref_ids: tuple[str, ...]
    created_at: int
    recording_component: str
    creates_authority: bool
    transfers_authority: bool


@_dataclass(frozen=True)
class DRSAuthorityEnvelopeV01:
    authority_envelope_version: str
    authority_envelope_id: str
    authority_class: str
    owning_local_root_id: str | None
    source_root_decision_input_id: str | None
    source_root_decision_id: str | None
    source_root_decision_hash: str | None
    authority_scope_fingerprint: str
    root_acceptance_state: str
    recording_component: str
    creates_authority: bool
    creates_permission: bool
    action_permission_present: bool


@_dataclass(frozen=True)
class DRSTimeEnvelopeV01:
    time_envelope_version: str
    time_envelope_id: str
    pt_created_at: int
    kt_as_of: int
    et_observed_at: int
    ct_context_anchor: int
    ttl_seconds: int
    valid_from: int
    valid_to: int
    source_observed_at: int
    source_reported_at: int
    system_ingested_at: int
    system_verified_at: int
    freshness_policy_id: str


@_dataclass(frozen=True)
class MeaningRecordV01:
    meaning_record_version: str
    meaning_record_id: str
    semantic_address: SemanticAddressV01
    predecessor_record_id: str | None
    supersession_reason: str | None
    safe_summary: str
    semantic_tags: tuple[str, ...]
    resonance_reason: str
    memory_pointers: tuple[MemoryPointerV01, ...]
    artifact_pointers: tuple[ArtifactPointerV01, ...]
    source_reference_ids: tuple[str, ...]
    lineage_edges: tuple[LineageEdgeV01, ...]
    time_envelope: DRSTimeEnvelopeV01
    authority_envelope: DRSAuthorityEnvelopeV01
    persistent_lifecycle_state: str
    risk_hints: tuple[str, ...]
    conflict_hints: tuple[str, ...]
    reuse_policy_class: str
    policy_version: str
    schema_versions: tuple[str, ...]
    content_fingerprint: str
    recording_component: str
    local_reference_kernel_scope: str
    creates_authority: bool
    creates_permission: bool


def _dedupe(reasons: list[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(reasons))


def _is_exact_str(value: object) -> bool:
    return type(value) is str


def _is_token(value: object) -> bool:
    return _token_reason(value) is None


def _is_sha256(value: object) -> bool:
    return type(value) is str and _SHA256_HEX.fullmatch(value) is not None


def _is_int64(value: object) -> bool:
    return type(value) is int and _INT64_MIN <= value <= _INT64_MAX


def _is_nonnegative_int(value: object) -> bool:
    return type(value) is int and 0 <= value <= _INT64_MAX


def _is_reference(value: object, *, allow_none: bool = False) -> bool:
    if allow_none and value is None:
        return True
    return _reference_reason(value) is None


def _token_reason(value: object) -> str | None:
    if type(value) is not str:
        return "drs_exact_type_required"
    if _TOKEN.fullmatch(value) is None:
        return "drs_text_bound_invalid"
    return _secret_reason(value)


def _reference_reason(value: object) -> str | None:
    if type(value) is not str:
        return "drs_exact_type_required"
    if _REFERENCE.fullmatch(value) is None:
        secret = _secret_reason(value)
        return secret or "drs_text_bound_invalid"
    return _secret_reason(value)


def _media_type_reason(value: object) -> str | None:
    if type(value) is not str:
        return "drs_exact_type_required"
    if len(value) > 128 or _MEDIA_TYPE.fullmatch(value) is None:
        return "drs_text_bound_invalid"
    return None


def _typed_id_reason(value: object, prefix: str) -> str | None:
    if type(value) is not str:
        return "drs_exact_type_required"
    if (
        not value.startswith(prefix)
        or len(value) != len(prefix) + 64
        or not _is_sha256(value[len(prefix):])
    ):
        return "drs_text_bound_invalid"
    return None


def _secret_reason(value: str) -> str | None:
    if _SHA256_HEX.fullmatch(value) or _G2B_CANONICAL_ID.fullmatch(value):
        return None
    if value.startswith(("sealed-secret-ref:", "audit-ref:", "scope-ref:")):
        if _SEALED_REFERENCE.fullmatch(value) is None:
            return "drs_secret_payload_forbidden"
    if _KEY_VALUE_SECRET.search(value) or _AUTHENTICATION_HEADER.search(value):
        return "drs_secret_payload_forbidden"
    if _PRIVATE_KEY.search(value) or _IBAN.search(value):
        return "drs_secret_payload_forbidden"
    if _CARD_NUMBER.search(value) or _PASSPORT.search(value):
        return "drs_secret_payload_forbidden"
    return None


def _bounded_text(value: object, *, maximum: int) -> str | None:
    if type(value) is not str or not value:
        return "drs_exact_type_required"
    if len(value) > maximum:
        return "drs_text_bound_invalid"
    if any(
        (ord(char) < 32 and char not in "\n\t") or ord(char) == 127
        for char in value
    ):
        return "drs_text_bound_invalid"
    return _secret_reason(value)


def _tuple_reasons(
    value: object,
    *,
    item_reason: object,
    maximum_items: int,
    require_unique: bool = True,
) -> tuple[str, ...]:
    if type(value) is not tuple:
        return ("drs_exact_type_required",)
    if len(value) > maximum_items:
        return ("drs_tuple_bound_invalid",)
    reasons: list[str] = []
    for item in value:
        reason = item_reason(item)
        if reason:
            reasons.append(reason)
    if require_unique and all(type(item) is str for item in value):
        if len(set(value)) != len(value):
            reasons.append("drs_tuple_duplicate_invalid")
    return _dedupe(reasons)


def _token_tuple_reasons(
    value: object,
    *,
    maximum_items: int = 64,
    require_unique: bool = True,
) -> tuple[str, ...]:
    return _tuple_reasons(
        value,
        item_reason=_token_reason,
        maximum_items=maximum_items,
        require_unique=require_unique,
    )


def _reference_tuple_reasons(
    value: object,
    *,
    maximum_items: int = 64,
    require_unique: bool = True,
) -> tuple[str, ...]:
    return _tuple_reasons(
        value,
        item_reason=_reference_reason,
        maximum_items=maximum_items,
        require_unique=require_unique,
    )


def _safe_text_tuple_reasons(
    value: object,
    *,
    maximum_items: int,
    maximum_chars: int,
    require_unique: bool = True,
) -> tuple[str, ...]:
    return _tuple_reasons(
        value,
        item_reason=lambda item: _bounded_text(
            item, maximum=maximum_chars
        ),
        maximum_items=maximum_items,
        require_unique=require_unique,
    )


def _sha256_tuple_reasons(
    value: object,
    *,
    maximum_items: int,
    require_unique: bool = True,
) -> tuple[str, ...]:
    return _tuple_reasons(
        value,
        item_reason=lambda item: (
            None if _is_sha256(item) else "drs_sha256_invalid"
        ),
        maximum_items=maximum_items,
        require_unique=require_unique,
    )


def _typed_id_tuple_reasons(
    value: object,
    *,
    prefix: str,
    maximum_items: int,
    invalid_reason: str,
    require_unique: bool = True,
) -> tuple[str, ...]:
    reasons = _tuple_reasons(
        value,
        item_reason=lambda item: _typed_id_reason(item, prefix),
        maximum_items=maximum_items,
        require_unique=require_unique,
    )
    return tuple(
        invalid_reason if reason == "drs_text_bound_invalid" else reason
        for reason in reasons
    )


def _field_name_tuple_reasons(
    value: object,
    *,
    maximum_items: int,
) -> tuple[str, ...]:
    return _tuple_reasons(
        value,
        item_reason=lambda item: (
            None
            if type(item) is str and _FIELD_NAME.fullmatch(item)
            else (
                "drs_exact_type_required"
                if type(item) is not str
                else "drs_text_bound_invalid"
            )
        ),
        maximum_items=maximum_items,
    )


def _string_tuple_reasons(
    value: object,
    *,
    maximum_items: int = 64,
    maximum_bytes: int = 256,
    require_unique: bool = True,
) -> tuple[str, ...]:
    return _safe_text_tuple_reasons(
        value,
        maximum_items=maximum_items,
        maximum_chars=maximum_bytes,
        require_unique=require_unique,
    )


def _canonical_plain_value(value: object) -> object:
    if value is None or type(value) in (str, int, bool):
        return value
    if type(value) is tuple:
        return [_canonical_plain_value(item) for item in value]
    if type(value) is SemanticAddressV01:
        return [
            _canonical_plain_value(getattr(value, name))
            for name in _SEMANTIC_ADDRESS_FIELDS
        ]
    if type(value) is MemoryPointerV01:
        return [
            _canonical_plain_value(getattr(value, name))
            for name in _MEMORY_POINTER_FIELDS
        ]
    if type(value) is ArtifactPointerV01:
        return [
            _canonical_plain_value(getattr(value, name))
            for name in _ARTIFACT_POINTER_FIELDS
        ]
    if type(value) is LineageEdgeV01:
        return [
            _canonical_plain_value(getattr(value, name))
            for name in _LINEAGE_EDGE_FIELDS
        ]
    if type(value) is DRSAuthorityEnvelopeV01:
        return [
            _canonical_plain_value(getattr(value, name))
            for name in _AUTHORITY_ENVELOPE_FIELDS
        ]
    if type(value) is DRSTimeEnvelopeV01:
        return [
            _canonical_plain_value(getattr(value, name))
            for name in _TIME_ENVELOPE_FIELDS
        ]
    if type(value) is MeaningRecordV01:
        return [
            _canonical_plain_value(getattr(value, name))
            for name in _MEANING_RECORD_FIELDS
        ]
    raise ValueError("canonical_json_value_invalid")


def _plain_data(value: object, field_names: tuple[str, ...]) -> dict[str, object]:
    return {
        name: _plain_data_value(getattr(value, name))
        for name in field_names
    }


def _plain_data_value(value: object) -> object:
    if value is None or type(value) in (str, int, bool):
        return value
    if type(value) is tuple:
        return [_plain_data_value(item) for item in value]
    if type(value) is SemanticAddressV01:
        return _plain_data(value, _SEMANTIC_ADDRESS_FIELDS)
    if type(value) is MemoryPointerV01:
        return _plain_data(value, _MEMORY_POINTER_FIELDS)
    if type(value) is ArtifactPointerV01:
        return _plain_data(value, _ARTIFACT_POINTER_FIELDS)
    if type(value) is LineageEdgeV01:
        return _plain_data(value, _LINEAGE_EDGE_FIELDS)
    if type(value) is DRSAuthorityEnvelopeV01:
        return _plain_data(value, _AUTHORITY_ENVELOPE_FIELDS)
    if type(value) is DRSTimeEnvelopeV01:
        return _plain_data(value, _TIME_ENVELOPE_FIELDS)
    if type(value) is MeaningRecordV01:
        return _plain_data(value, _MEANING_RECORD_FIELDS)
    raise ValueError("drs_exact_type_required")


def _identity(
    value: object,
    *,
    identity_field: str,
    domain: str,
    prefix: str,
    field_names: tuple[str, ...],
) -> str:
    material = [
        _canonical_plain_value(getattr(value, name))
        for name in field_names
        if name != identity_field
    ]
    digest = _domain_separated_sha256_hex_v01(
        domain=domain,
        payload=_canonical_json_bytes_v01(material),
    )
    return prefix + digest


def _profile_for(type_name: str) -> tuple[str, str, str, tuple[str, ...]]:
    for name, identity_field, domain, prefix, field_names in _IDENTITY_PROFILES:
        if name == type_name:
            return identity_field, domain, prefix, field_names
    raise ValueError("drs_identity_profile_invalid")


def _finish_build(
    provisional: object,
    *,
    type_name: str,
    reasons_without_identity: tuple[str, ...],
    validator: object,
) -> object:
    if reasons_without_identity:
        raise ValueError(reasons_without_identity[0]) from None
    identity_field, domain, prefix, field_names = _profile_for(type_name)
    identity = _identity(
        provisional,
        identity_field=identity_field,
        domain=domain,
        prefix=prefix,
        field_names=field_names,
    )
    final = _replace(provisional, **{identity_field: identity})
    if not callable(validator):
        raise ValueError("drs_builder_invalid") from None
    valid, reasons = validator(final)
    if not valid:
        raise ValueError(reasons[0]) from None
    return final


def _id_reason(
    value: object,
    *,
    type_name: str,
) -> str | None:
    identity_field, domain, prefix, field_names = _profile_for(type_name)
    actual = getattr(value, identity_field)
    if type(actual) is not str or not actual.startswith(prefix):
        return "drs_identity_invalid"
    if len(actual) != len(prefix) + 64 or not _is_sha256(actual[len(prefix):]):
        return "drs_identity_invalid"
    expected = _identity(
        value,
        identity_field=identity_field,
        domain=domain,
        prefix=prefix,
        field_names=field_names,
    )
    if actual != expected:
        if type_name == "MeaningRecordV01":
            return "drs_meaning_record_identity_invalid"
        if type_name in ("MemoryPointerV01", "ArtifactPointerV01"):
            return "drs_pointer_identity_invalid"
        return "drs_identity_invalid"
    return None


def _version_reason(value: object) -> str | None:
    if type(value) is not str:
        return "drs_exact_type_required"
    if value != DRS_G2B_PROFILE_VERSION_V01:
        return "drs_schema_version_mismatch"
    return None


def _semantic_address_reasons(
    value: object,
    *,
    check_identity: bool,
) -> tuple[str, ...]:
    if type(value) is not SemanticAddressV01:
        return ("drs_exact_type_required",)
    reasons: list[str] = []
    reason = _version_reason(value.address_profile_version)
    if reason:
        reasons.append(reason)
    for item in (
        value.namespace,
        value.domain,
        value.subject_class,
        value.intent_class,
        value.meaning_schema_id,
        value.meaning_schema_version,
    ):
        token_reason = _token_reason(item)
        if token_reason:
            reasons.append(
                token_reason
                if token_reason == "drs_secret_payload_forbidden"
                else "drs_address_component_invalid"
            )
    if type(value.namespace) is str and value.namespace.lower().startswith(
        ("user:", "person:", "query:")
    ):
        reasons.append("drs_address_dynamic_material_forbidden")
    if check_identity and not reasons:
        reason = _id_reason(value, type_name="SemanticAddressV01")
        if reason:
            reasons.append(reason)
    return _dedupe(reasons)


def build_semantic_address_v01(
    *,
    namespace: str,
    domain: str,
    subject_class: str,
    intent_class: str,
    meaning_schema_id: str,
    meaning_schema_version: str,
) -> SemanticAddressV01:
    try:
        provisional = SemanticAddressV01(
            address_profile_version=SEMANTIC_ADDRESS_PROFILE_VERSION_V01,
            namespace=namespace,
            domain=domain,
            subject_class=subject_class,
            intent_class=intent_class,
            meaning_schema_id=meaning_schema_id,
            meaning_schema_version=meaning_schema_version,
            semantic_address_id="drsaddr_v01:" + "0" * 64,
        )
        return _finish_build(
            provisional,
            type_name="SemanticAddressV01",
            reasons_without_identity=_semantic_address_reasons(
                provisional, check_identity=False
            ),
            validator=validate_semantic_address_v01,
        )
    except ValueError as exc:
        reason = str(exc)
        allowed = {
            "drs_exact_type_required",
            "drs_schema_version_mismatch",
            "drs_address_component_invalid",
            "drs_address_dynamic_material_forbidden",
            "drs_identity_invalid",
        }
        raise ValueError(reason if reason in allowed else "drs_address_invalid") from None
    except Exception:
        raise ValueError("drs_address_invalid") from None


def validate_semantic_address_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    try:
        reasons = _semantic_address_reasons(value, check_identity=True)
        return not reasons, reasons
    except Exception:
        return False, ("drs_address_invalid",)


def semantic_address_to_plain_data_v01(value: object) -> dict[str, object]:
    if type(value) is not SemanticAddressV01:
        raise ValueError("drs_exact_type_required") from None
    return _plain_data(value, _SEMANTIC_ADDRESS_FIELDS)


def _pointer_common_reasons(
    value: object,
    *,
    artifact: bool,
    check_identity: bool,
) -> tuple[str, ...]:
    expected_type = ArtifactPointerV01 if artifact else MemoryPointerV01
    if type(value) is not expected_type:
        return ("drs_exact_type_required",)
    reasons: list[str] = []
    reason = _version_reason(value.pointer_version)
    if reason:
        reasons.append(reason)
    allowed_storage = (
        DRS_ARTIFACT_POINTER_STORAGE_CLASSES_V01
        if artifact
        else DRS_MEMORY_POINTER_STORAGE_CLASSES_V01
    )
    if type(value.storage_class) is not str or value.storage_class not in allowed_storage:
        reasons.append("drs_pointer_storage_class_invalid")
    if not _is_reference(value.object_reference):
        reasons.append(
            _secret_reason(value.object_reference)
            if type(value.object_reference) is str
            and _secret_reason(value.object_reference)
            else "drs_pointer_reference_invalid"
        )
    if not _is_sha256(value.content_sha256):
        reasons.append("drs_sha256_invalid")
    descriptor = value.media_type if artifact else value.record_class
    descriptor_reason = (
        _media_type_reason(descriptor)
        if artifact
        else _token_reason(descriptor)
    )
    if descriptor_reason:
        reasons.append("drs_pointer_descriptor_invalid")
    if value.byte_length is not None and not _is_nonnegative_int(value.byte_length):
        reasons.append("drs_exact_int_required")
    if not _is_reference(value.access_policy_id):
        reasons.append("drs_pointer_access_policy_denied")
    if type(value.sensitivity_class) is not str or value.sensitivity_class not in _SENSITIVITY_CLASSES:
        reasons.append("drs_pointer_sensitivity_invalid")
    reasons.extend(_token_tuple_reasons(value.allowed_use_classes))
    reasons.extend(_token_tuple_reasons(value.forbidden_use_classes))
    if (
        type(value.allowed_use_classes) is tuple
        and type(value.forbidden_use_classes) is tuple
        and all(type(item) is str for item in value.allowed_use_classes)
        and all(type(item) is str for item in value.forbidden_use_classes)
        and set(value.allowed_use_classes) & set(value.forbidden_use_classes)
    ):
        reasons.append("drs_pointer_access_policy_denied")
    if type(value.summary_read_permitted) is not bool:
        reasons.append("drs_exact_type_required")
    if type(value.payload_read_permitted) is not bool:
        reasons.append("drs_exact_type_required")
    if value.payload_read_permitted is True and value.summary_read_permitted is not True:
        reasons.append("drs_pointer_access_policy_denied")
    if (
        value.sensitivity_class == "SECRET_REFERENCE_ONLY"
        and value.payload_read_permitted is True
    ):
        reasons.append("drs_pointer_access_policy_denied")
    if value.creates_authority is not False:
        reasons.append("drs_non_authority_law_invalid")
    if value.creates_permission is not False:
        reasons.append("drs_non_permission_law_invalid")
    if check_identity and not reasons:
        reason = _id_reason(
            value,
            type_name="ArtifactPointerV01" if artifact else "MemoryPointerV01",
        )
        if reason:
            reasons.append(reason)
    return _dedupe(reasons)


def build_memory_pointer_v01(
    *,
    storage_class: str,
    object_reference: str,
    content_sha256: str,
    record_class: str,
    byte_length: int | None,
    access_policy_id: str,
    sensitivity_class: str,
    allowed_use_classes: tuple[str, ...],
    forbidden_use_classes: tuple[str, ...],
    summary_read_permitted: bool,
    payload_read_permitted: bool,
) -> MemoryPointerV01:
    try:
        provisional = MemoryPointerV01(
            pointer_version=DRS_G2B_PROFILE_VERSION_V01,
            pointer_id="drsmem_v01:" + "0" * 64,
            storage_class=storage_class,
            object_reference=object_reference,
            content_sha256=content_sha256,
            record_class=record_class,
            byte_length=byte_length,
            access_policy_id=access_policy_id,
            sensitivity_class=sensitivity_class,
            allowed_use_classes=allowed_use_classes,
            forbidden_use_classes=forbidden_use_classes,
            summary_read_permitted=summary_read_permitted,
            payload_read_permitted=payload_read_permitted,
            creates_authority=False,
            creates_permission=False,
        )
        return _finish_build(
            provisional,
            type_name="MemoryPointerV01",
            reasons_without_identity=_pointer_common_reasons(
                provisional, artifact=False, check_identity=False
            ),
            validator=validate_memory_pointer_v01,
        )
    except ValueError as exc:
        reason = str(exc)
        allowed = {
            "drs_exact_type_required",
            "drs_exact_int_required",
            "drs_schema_version_mismatch",
            "drs_pointer_storage_class_invalid",
            "drs_pointer_reference_invalid",
            "drs_pointer_descriptor_invalid",
            "drs_pointer_access_policy_denied",
            "drs_pointer_sensitivity_invalid",
            "drs_secret_payload_forbidden",
            "drs_sha256_invalid",
            "drs_tuple_bound_invalid",
            "drs_tuple_duplicate_invalid",
        }
        raise ValueError(reason if reason in allowed else "drs_pointer_invalid") from None
    except Exception:
        raise ValueError("drs_pointer_invalid") from None


def validate_memory_pointer_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    try:
        reasons = _pointer_common_reasons(
            value, artifact=False, check_identity=True
        )
        return not reasons, reasons
    except Exception:
        return False, ("drs_pointer_invalid",)


def memory_pointer_to_plain_data_v01(value: object) -> dict[str, object]:
    if type(value) is not MemoryPointerV01:
        raise ValueError("drs_exact_type_required") from None
    return _plain_data(value, _MEMORY_POINTER_FIELDS)


def build_artifact_pointer_v01(
    *,
    storage_class: str,
    object_reference: str,
    content_sha256: str,
    media_type: str,
    byte_length: int | None,
    access_policy_id: str,
    sensitivity_class: str,
    allowed_use_classes: tuple[str, ...],
    forbidden_use_classes: tuple[str, ...],
    summary_read_permitted: bool,
    payload_read_permitted: bool,
) -> ArtifactPointerV01:
    try:
        provisional = ArtifactPointerV01(
            pointer_version=DRS_G2B_PROFILE_VERSION_V01,
            pointer_id="drsart_v01:" + "0" * 64,
            storage_class=storage_class,
            object_reference=object_reference,
            content_sha256=content_sha256,
            media_type=media_type,
            byte_length=byte_length,
            access_policy_id=access_policy_id,
            sensitivity_class=sensitivity_class,
            allowed_use_classes=allowed_use_classes,
            forbidden_use_classes=forbidden_use_classes,
            summary_read_permitted=summary_read_permitted,
            payload_read_permitted=payload_read_permitted,
            creates_authority=False,
            creates_permission=False,
        )
        return _finish_build(
            provisional,
            type_name="ArtifactPointerV01",
            reasons_without_identity=_pointer_common_reasons(
                provisional, artifact=True, check_identity=False
            ),
            validator=validate_artifact_pointer_v01,
        )
    except ValueError as exc:
        reason = str(exc)
        allowed = {
            "drs_exact_type_required",
            "drs_exact_int_required",
            "drs_schema_version_mismatch",
            "drs_pointer_storage_class_invalid",
            "drs_pointer_reference_invalid",
            "drs_pointer_descriptor_invalid",
            "drs_pointer_access_policy_denied",
            "drs_pointer_sensitivity_invalid",
            "drs_secret_payload_forbidden",
            "drs_sha256_invalid",
            "drs_tuple_bound_invalid",
            "drs_tuple_duplicate_invalid",
        }
        raise ValueError(reason if reason in allowed else "drs_pointer_invalid") from None
    except Exception:
        raise ValueError("drs_pointer_invalid") from None


def validate_artifact_pointer_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    try:
        reasons = _pointer_common_reasons(
            value, artifact=True, check_identity=True
        )
        return not reasons, reasons
    except Exception:
        return False, ("drs_pointer_invalid",)


def artifact_pointer_to_plain_data_v01(value: object) -> dict[str, object]:
    if type(value) is not ArtifactPointerV01:
        raise ValueError("drs_exact_type_required") from None
    return _plain_data(value, _ARTIFACT_POINTER_FIELDS)


def _lineage_edge_reasons(
    value: object,
    *,
    check_identity: bool,
) -> tuple[str, ...]:
    if type(value) is not LineageEdgeV01:
        return ("drs_exact_type_required",)
    reasons: list[str] = []
    reason = _version_reason(value.lineage_edge_version)
    if reason:
        reasons.append(reason)
    for record_id in (
        value.source_meaning_record_id,
        value.target_meaning_record_id,
    ):
        if type(record_id) is not str or not record_id.startswith("drsmeaning_v01:"):
            reasons.append("drs_lineage_record_id_invalid")
        elif len(record_id) != len("drsmeaning_v01:") + 64 or not _is_sha256(
            record_id[len("drsmeaning_v01:"):]
        ):
            reasons.append("drs_lineage_record_id_invalid")
    if (
        type(value.source_meaning_record_id) is str
        and type(value.target_meaning_record_id) is str
        and value.source_meaning_record_id == value.target_meaning_record_id
    ):
        reasons.append("drs_lineage_self_edge_invalid")
    if type(value.relation_class) is not str or value.relation_class not in _LINEAGE_RELATION_CLASSES:
        reasons.append("drs_lineage_relation_invalid")
    if not _is_token(value.claim_dimension):
        reasons.append("drs_lineage_claim_dimension_invalid")
    if not _is_sha256(value.source_history_hash):
        reasons.append("drs_sha256_invalid")
    reasons.extend(_reference_tuple_reasons(value.evidence_ref_ids))
    if not _is_int64(value.created_at):
        reasons.append("drs_exact_int_required")
    if not _is_token(value.recording_component):
        reasons.append("drs_recording_component_invalid")
    if value.creates_authority is not False:
        reasons.append("drs_non_authority_law_invalid")
    if value.transfers_authority is not False:
        reasons.append("drs_non_authority_law_invalid")
    if check_identity and not reasons:
        reason = _id_reason(value, type_name="LineageEdgeV01")
        if reason:
            reasons.append(reason)
    return _dedupe(reasons)


def build_lineage_edge_v01(
    *,
    source_meaning_record_id: str,
    target_meaning_record_id: str,
    relation_class: str,
    claim_dimension: str,
    source_history_hash: str,
    evidence_ref_ids: tuple[str, ...],
    created_at: int,
    recording_component: str,
) -> LineageEdgeV01:
    try:
        provisional = LineageEdgeV01(
            lineage_edge_version=DRS_G2B_PROFILE_VERSION_V01,
            lineage_edge_id="drsedge_v01:" + "0" * 64,
            source_meaning_record_id=source_meaning_record_id,
            target_meaning_record_id=target_meaning_record_id,
            relation_class=relation_class,
            claim_dimension=claim_dimension,
            source_history_hash=source_history_hash,
            evidence_ref_ids=evidence_ref_ids,
            created_at=created_at,
            recording_component=recording_component,
            creates_authority=False,
            transfers_authority=False,
        )
        return _finish_build(
            provisional,
            type_name="LineageEdgeV01",
            reasons_without_identity=_lineage_edge_reasons(
                provisional, check_identity=False
            ),
            validator=validate_lineage_edge_v01,
        )
    except ValueError as exc:
        reason = str(exc)
        raise ValueError(
            reason if reason.startswith("drs_") else "drs_lineage_edge_invalid"
        ) from None
    except Exception:
        raise ValueError("drs_lineage_edge_invalid") from None


def validate_lineage_edge_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    try:
        reasons = _lineage_edge_reasons(value, check_identity=True)
        return not reasons, reasons
    except Exception:
        return False, ("drs_lineage_edge_invalid",)


def lineage_edge_to_plain_data_v01(value: object) -> dict[str, object]:
    if type(value) is not LineageEdgeV01:
        raise ValueError("drs_exact_type_required") from None
    return _plain_data(value, _LINEAGE_EDGE_FIELDS)


def _authority_envelope_reasons(
    value: object,
    *,
    check_identity: bool,
) -> tuple[str, ...]:
    if type(value) is not DRSAuthorityEnvelopeV01:
        return ("drs_exact_type_required",)
    reasons: list[str] = []
    reason = _version_reason(value.authority_envelope_version)
    if reason:
        reasons.append(reason)
    if type(value.authority_class) is not str or value.authority_class not in _AUTHORITY_CLASSES:
        reasons.append("drs_authority_class_invalid")
    root_fields = (
        value.owning_local_root_id,
        value.source_root_decision_input_id,
        value.source_root_decision_id,
        value.source_root_decision_hash,
    )
    if value.authority_class in _ROOT_EVIDENCE_AUTHORITY_CLASSES:
        if not all(_is_reference(item) for item in root_fields[:3]):
            reasons.append("drs_root_evidence_invalid")
        if not _is_sha256(root_fields[3]):
            reasons.append("drs_root_evidence_invalid")
    elif any(item is not None for item in root_fields):
        reasons.append("drs_root_evidence_invalid")
    if not _is_sha256(value.authority_scope_fingerprint):
        reasons.append("drs_sha256_invalid")
    if type(value.root_acceptance_state) is not str or value.root_acceptance_state not in _ROOT_ACCEPTANCE_STATES:
        reasons.append("drs_root_acceptance_state_invalid")
    expected_states = {
        "ROOT_ACCEPTED_CONTEXT": "ACCEPTED_CONTEXT",
        "ROOT_ACCEPTED_WORK": "ACCEPTED_WORK",
        "ROOT_FINAL_REFERENCE": "ACCEPTED_WORK",
    }
    if (
        type(value.authority_class) is str
        and value.authority_class in expected_states
        and value.root_acceptance_state != expected_states[value.authority_class]
    ):
        reasons.append("drs_root_evidence_invalid")
    if (
        type(value.authority_class) is str
        and value.authority_class not in _ROOT_EVIDENCE_AUTHORITY_CLASSES
        and value.root_acceptance_state in ("ACCEPTED_CONTEXT", "ACCEPTED_WORK")
    ):
        reasons.append("drs_root_evidence_invalid")
    if not _is_token(value.recording_component):
        reasons.append("drs_recording_component_invalid")
    if value.creates_authority is not False:
        reasons.append("drs_non_authority_law_invalid")
    if value.creates_permission is not False or value.action_permission_present is not False:
        reasons.append("drs_non_permission_law_invalid")
    if check_identity and not reasons:
        reason = _id_reason(value, type_name="DRSAuthorityEnvelopeV01")
        if reason:
            reasons.append(reason)
    return _dedupe(reasons)


def build_drs_authority_envelope_v01(
    *,
    authority_class: str,
    owning_local_root_id: str | None,
    source_root_decision_input_id: str | None,
    source_root_decision_id: str | None,
    source_root_decision_hash: str | None,
    authority_scope_fingerprint: str,
    root_acceptance_state: str,
    recording_component: str,
) -> DRSAuthorityEnvelopeV01:
    try:
        provisional = DRSAuthorityEnvelopeV01(
            authority_envelope_version=DRS_G2B_PROFILE_VERSION_V01,
            authority_envelope_id="drsauth_v01:" + "0" * 64,
            authority_class=authority_class,
            owning_local_root_id=owning_local_root_id,
            source_root_decision_input_id=source_root_decision_input_id,
            source_root_decision_id=source_root_decision_id,
            source_root_decision_hash=source_root_decision_hash,
            authority_scope_fingerprint=authority_scope_fingerprint,
            root_acceptance_state=root_acceptance_state,
            recording_component=recording_component,
            creates_authority=False,
            creates_permission=False,
            action_permission_present=False,
        )
        return _finish_build(
            provisional,
            type_name="DRSAuthorityEnvelopeV01",
            reasons_without_identity=_authority_envelope_reasons(
                provisional, check_identity=False
            ),
            validator=validate_drs_authority_envelope_v01,
        )
    except ValueError as exc:
        reason = str(exc)
        raise ValueError(
            reason if reason.startswith("drs_") else "drs_authority_envelope_invalid"
        ) from None
    except Exception:
        raise ValueError("drs_authority_envelope_invalid") from None


def validate_drs_authority_envelope_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    try:
        reasons = _authority_envelope_reasons(value, check_identity=True)
        return not reasons, reasons
    except Exception:
        return False, ("drs_authority_envelope_invalid",)


def drs_authority_envelope_to_plain_data_v01(
    value: object,
) -> dict[str, object]:
    if type(value) is not DRSAuthorityEnvelopeV01:
        raise ValueError("drs_exact_type_required") from None
    return _plain_data(value, _AUTHORITY_ENVELOPE_FIELDS)


def _time_envelope_reasons(
    value: object,
    *,
    check_identity: bool,
) -> tuple[str, ...]:
    if type(value) is not DRSTimeEnvelopeV01:
        return ("drs_exact_type_required",)
    reasons: list[str] = []
    reason = _version_reason(value.time_envelope_version)
    if reason:
        reasons.append(reason)
    time_fields = (
        value.pt_created_at,
        value.kt_as_of,
        value.et_observed_at,
        value.ct_context_anchor,
        value.ttl_seconds,
        value.valid_from,
        value.valid_to,
        value.source_observed_at,
        value.source_reported_at,
        value.system_ingested_at,
        value.system_verified_at,
    )
    if not all(_is_int64(item) for item in time_fields):
        reasons.append("drs_time_type_invalid")
    if type(value.ttl_seconds) is not int or value.ttl_seconds <= 0:
        reasons.append("drs_time_ttl_invalid")
    if (
        type(value.valid_from) is int
        and type(value.valid_to) is int
        and value.valid_from >= value.valid_to
    ):
        reasons.append("drs_time_validity_interval_invalid")
    if (
        type(value.pt_created_at) is int
        and type(value.ttl_seconds) is int
        and not (_INT64_MIN <= value.pt_created_at + value.ttl_seconds <= _INT64_MAX)
    ):
        reasons.append("drs_time_overflow_invalid")
    if not _is_reference(value.freshness_policy_id):
        reasons.append("drs_freshness_policy_invalid")
    if check_identity and not reasons:
        reason = _id_reason(value, type_name="DRSTimeEnvelopeV01")
        if reason:
            reasons.append(reason)
    return _dedupe(reasons)


def build_drs_time_envelope_v01(
    *,
    pt_created_at: int,
    kt_as_of: int,
    et_observed_at: int,
    ct_context_anchor: int,
    ttl_seconds: int,
    valid_from: int,
    valid_to: int,
    source_observed_at: int,
    source_reported_at: int,
    system_ingested_at: int,
    system_verified_at: int,
    freshness_policy_id: str,
) -> DRSTimeEnvelopeV01:
    try:
        provisional = DRSTimeEnvelopeV01(
            time_envelope_version=DRS_G2B_PROFILE_VERSION_V01,
            time_envelope_id="drstime_v01:" + "0" * 64,
            pt_created_at=pt_created_at,
            kt_as_of=kt_as_of,
            et_observed_at=et_observed_at,
            ct_context_anchor=ct_context_anchor,
            ttl_seconds=ttl_seconds,
            valid_from=valid_from,
            valid_to=valid_to,
            source_observed_at=source_observed_at,
            source_reported_at=source_reported_at,
            system_ingested_at=system_ingested_at,
            system_verified_at=system_verified_at,
            freshness_policy_id=freshness_policy_id,
        )
        return _finish_build(
            provisional,
            type_name="DRSTimeEnvelopeV01",
            reasons_without_identity=_time_envelope_reasons(
                provisional, check_identity=False
            ),
            validator=validate_drs_time_envelope_v01,
        )
    except ValueError as exc:
        reason = str(exc)
        raise ValueError(
            reason if reason.startswith("drs_") else "drs_time_envelope_invalid"
        ) from None
    except Exception:
        raise ValueError("drs_time_envelope_invalid") from None


def validate_drs_time_envelope_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    try:
        reasons = _time_envelope_reasons(value, check_identity=True)
        return not reasons, reasons
    except Exception:
        return False, ("drs_time_envelope_invalid",)


def drs_time_envelope_to_plain_data_v01(value: object) -> dict[str, object]:
    if type(value) is not DRSTimeEnvelopeV01:
        raise ValueError("drs_exact_type_required") from None
    return _plain_data(value, _TIME_ENVELOPE_FIELDS)


def _meaning_record_reasons(
    value: object,
    *,
    check_identity: bool,
) -> tuple[str, ...]:
    if type(value) is not MeaningRecordV01:
        return ("drs_exact_type_required",)
    reasons: list[str] = []
    reason = _version_reason(value.meaning_record_version)
    if reason:
        reasons.append(reason)
    valid, nested = validate_semantic_address_v01(value.semantic_address)
    if not valid:
        reasons.extend(nested)
    if (value.predecessor_record_id is None) != (value.supersession_reason is None):
        reasons.append("drs_supersession_evidence_invalid")
    if value.predecessor_record_id is not None:
        if _typed_id_reason(
            value.predecessor_record_id, "drsmeaning_v01:"
        ):
            reasons.append("drs_supersession_evidence_invalid")
        reason = _bounded_text(value.supersession_reason, maximum=256)
        if reason:
            reasons.append(
                reason
                if reason == "drs_secret_payload_forbidden"
                else "drs_supersession_evidence_invalid"
            )
    reason = _bounded_text(value.safe_summary, maximum=1024)
    if reason:
        reasons.append(reason)
    reasons.extend(_token_tuple_reasons(value.semantic_tags, maximum_items=32))
    reason = _bounded_text(value.resonance_reason, maximum=512)
    if reason:
        reasons.append(reason)
    for tuple_value, exact_type, validator in (
        (value.memory_pointers, MemoryPointerV01, validate_memory_pointer_v01),
        (value.artifact_pointers, ArtifactPointerV01, validate_artifact_pointer_v01),
        (value.lineage_edges, LineageEdgeV01, validate_lineage_edge_v01),
    ):
        if type(tuple_value) is not tuple:
            reasons.append("drs_exact_type_required")
            continue
        for item in tuple_value:
            if type(item) is not exact_type:
                reasons.append("drs_exact_type_required")
                continue
            item_valid, item_reasons = validator(item)
            if not item_valid:
                reasons.extend(item_reasons)
    if type(value.memory_pointers) is tuple and all(
        type(item) is MemoryPointerV01 for item in value.memory_pointers
    ):
        ids = tuple(item.pointer_id for item in value.memory_pointers)
        if len(set(ids)) != len(ids):
            reasons.append("drs_tuple_duplicate_invalid")
    if type(value.artifact_pointers) is tuple and all(
        type(item) is ArtifactPointerV01 for item in value.artifact_pointers
    ):
        ids = tuple(item.pointer_id for item in value.artifact_pointers)
        if len(set(ids)) != len(ids):
            reasons.append("drs_tuple_duplicate_invalid")
    if type(value.lineage_edges) is tuple and all(
        type(item) is LineageEdgeV01 for item in value.lineage_edges
    ):
        ids = tuple(item.lineage_edge_id for item in value.lineage_edges)
        if len(set(ids)) != len(ids):
            reasons.append("drs_tuple_duplicate_invalid")
        if value.predecessor_record_id is not None:
            replacement_edges = tuple(
                edge
                for edge in value.lineage_edges
                if edge.relation_class in ("SUPERSEDES", "REPLACES")
                and edge.source_meaning_record_id == value.predecessor_record_id
            )
            if len(replacement_edges) != 1:
                reasons.append("drs_supersession_evidence_invalid")
    reasons.extend(_reference_tuple_reasons(value.source_reference_ids))
    valid, nested = validate_drs_time_envelope_v01(value.time_envelope)
    if not valid:
        reasons.extend(nested)
    valid, nested = validate_drs_authority_envelope_v01(value.authority_envelope)
    if not valid:
        reasons.extend(nested)
    if type(value.persistent_lifecycle_state) is not str or value.persistent_lifecycle_state not in DRS_PERSISTENT_LIFECYCLE_STATES_V01:
        reasons.append("drs_persistent_lifecycle_invalid")
    reasons.extend(
        _safe_text_tuple_reasons(
            value.risk_hints,
            maximum_items=32,
            maximum_chars=256,
        )
    )
    reasons.extend(
        _safe_text_tuple_reasons(
            value.conflict_hints,
            maximum_items=32,
            maximum_chars=256,
        )
    )
    if not _is_token(value.reuse_policy_class):
        reasons.append("drs_reuse_policy_class_invalid")
    if not _is_token(value.policy_version):
        reasons.append("drs_policy_version_invalid")
    reasons.extend(
        _token_tuple_reasons(value.schema_versions, maximum_items=32)
    )
    if not _is_sha256(value.content_fingerprint):
        reasons.append("drs_sha256_invalid")
    if not _is_token(value.recording_component):
        reasons.append("drs_recording_component_invalid")
    if value.local_reference_kernel_scope != "LOCAL_REFERENCE_KERNEL" or type(
        value.local_reference_kernel_scope
    ) is not str:
        reasons.append("drs_kernel_scope_invalid")
    if value.creates_authority is not False:
        reasons.append("drs_non_authority_law_invalid")
    if value.creates_permission is not False:
        reasons.append("drs_non_permission_law_invalid")
    if check_identity and not reasons:
        reason = _id_reason(value, type_name="MeaningRecordV01")
        if reason:
            reasons.append(reason)
    return _dedupe(reasons)


def build_meaning_record_v01(
    *,
    semantic_address: SemanticAddressV01,
    predecessor_record_id: str | None,
    supersession_reason: str | None,
    safe_summary: str,
    semantic_tags: tuple[str, ...],
    resonance_reason: str,
    memory_pointers: tuple[MemoryPointerV01, ...],
    artifact_pointers: tuple[ArtifactPointerV01, ...],
    source_reference_ids: tuple[str, ...],
    lineage_edges: tuple[LineageEdgeV01, ...],
    time_envelope: DRSTimeEnvelopeV01,
    authority_envelope: DRSAuthorityEnvelopeV01,
    persistent_lifecycle_state: str,
    risk_hints: tuple[str, ...],
    conflict_hints: tuple[str, ...],
    reuse_policy_class: str,
    policy_version: str,
    schema_versions: tuple[str, ...],
    content_fingerprint: str,
    recording_component: str,
) -> MeaningRecordV01:
    try:
        provisional = MeaningRecordV01(
            meaning_record_version=DRS_G2B_PROFILE_VERSION_V01,
            meaning_record_id="drsmeaning_v01:" + "0" * 64,
            semantic_address=semantic_address,
            predecessor_record_id=predecessor_record_id,
            supersession_reason=supersession_reason,
            safe_summary=safe_summary,
            semantic_tags=semantic_tags,
            resonance_reason=resonance_reason,
            memory_pointers=memory_pointers,
            artifact_pointers=artifact_pointers,
            source_reference_ids=source_reference_ids,
            lineage_edges=lineage_edges,
            time_envelope=time_envelope,
            authority_envelope=authority_envelope,
            persistent_lifecycle_state=persistent_lifecycle_state,
            risk_hints=risk_hints,
            conflict_hints=conflict_hints,
            reuse_policy_class=reuse_policy_class,
            policy_version=policy_version,
            schema_versions=schema_versions,
            content_fingerprint=content_fingerprint,
            recording_component=recording_component,
            local_reference_kernel_scope="LOCAL_REFERENCE_KERNEL",
            creates_authority=False,
            creates_permission=False,
        )
        return _finish_build(
            provisional,
            type_name="MeaningRecordV01",
            reasons_without_identity=_meaning_record_reasons(
                provisional, check_identity=False
            ),
            validator=validate_meaning_record_v01,
        )
    except ValueError as exc:
        reason = str(exc)
        raise ValueError(
            reason if reason.startswith("drs_") else "drs_meaning_record_invalid"
        ) from None
    except Exception:
        raise ValueError("drs_meaning_record_invalid") from None


def validate_meaning_record_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    try:
        reasons = _meaning_record_reasons(value, check_identity=True)
        return not reasons, reasons
    except Exception:
        return False, ("drs_meaning_record_invalid",)


def meaning_record_to_plain_data_v01(value: object) -> dict[str, object]:
    if type(value) is not MeaningRecordV01:
        raise ValueError("drs_exact_type_required") from None
    return _plain_data(value, _MEANING_RECORD_FIELDS)


__all__ = (
    "DRS_G2B_PROFILE_VERSION_V01",
    "SEMANTIC_ADDRESS_PROFILE_VERSION_V01",
    "DRS_MEMORY_POINTER_STORAGE_CLASSES_V01",
    "DRS_ARTIFACT_POINTER_STORAGE_CLASSES_V01",
    "DRS_PERSISTENT_LIFECYCLE_STATES_V01",
    "SemanticAddressV01",
    "MemoryPointerV01",
    "ArtifactPointerV01",
    "LineageEdgeV01",
    "DRSAuthorityEnvelopeV01",
    "DRSTimeEnvelopeV01",
    "MeaningRecordV01",
    "build_semantic_address_v01",
    "validate_semantic_address_v01",
    "semantic_address_to_plain_data_v01",
    "build_memory_pointer_v01",
    "validate_memory_pointer_v01",
    "memory_pointer_to_plain_data_v01",
    "build_artifact_pointer_v01",
    "validate_artifact_pointer_v01",
    "artifact_pointer_to_plain_data_v01",
    "build_lineage_edge_v01",
    "validate_lineage_edge_v01",
    "lineage_edge_to_plain_data_v01",
    "build_drs_authority_envelope_v01",
    "validate_drs_authority_envelope_v01",
    "drs_authority_envelope_to_plain_data_v01",
    "build_drs_time_envelope_v01",
    "validate_drs_time_envelope_v01",
    "drs_time_envelope_to_plain_data_v01",
    "build_meaning_record_v01",
    "validate_meaning_record_v01",
    "meaning_record_to_plain_data_v01",
)
