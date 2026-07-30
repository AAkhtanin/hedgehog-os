"""Immutable G2-B Root evidence, reuse certificate, and G2-A history transport."""

from __future__ import annotations

from dataclasses import dataclass as _dataclass
from dataclasses import replace as _replace
from typing import TYPE_CHECKING as _TYPE_CHECKING

from hedgehog.drs_semantic_address_v01 import (
    DRS_G2B_PROFILE_VERSION_V01 as _PROFILE_VERSION,
)
from hedgehog.drs_semantic_address_v01 import (
    _canonical_json_bytes_v01,
    _canonical_plain_value,
    _dedupe,
    _domain_separated_sha256_hex_v01,
    _is_int64,
    _is_reference,
    _is_sha256,
    _is_token,
    _plain_data_value,
    _token_tuple_reasons,
)

if _TYPE_CHECKING:
    from hedgehog.drs_memory_resolution_v01 import DRSResolutionReportV01
    from hedgehog.kernel.root_decision_v01 import (
        RootDecisionInputV01,
        RootDecisionKernelV01,
        RootDecisionResultV01,
    )


_ENABLED_REUSE_CLASSES = (
    "CONTEXT_ONLY",
    "ANSWER_SHORTCUT",
)
_ACTION_LIFECYCLE_STATES = (
    "CREATED",
    "ROOT_AUTHORIZED",
    "QUEUED",
    "PENDING_FULFILLMENT",
    "FULFILLED_MOCK",
    "RECEIPT_RECEIVED",
    "FAILED",
    "BLOCKED",
    "EXPIRED",
    "REVOKED",
    "SUPERSEDED",
)
_IDEMPOTENCY_DISPOSITIONS = (
    "UNCLAIMED",
    "RESERVED",
    "CONSUMED",
    "UNCERTAIN_CLOSED",
)
_EVALUATION_TIME_SOURCES = (
    "INJECTED_CURRENT_DECISION_TIME",
    "RECORDED_HISTORICAL_AS_OF_TIME",
    "RECORDED_AUDIT_REPLAY_TIME",
    "INJECTED_ANALYSIS_TIME",
)
_B4_ROOT_RESULT_BINDING_DOMAIN_V01 = (
    "hedgehog:drs:root_shortcut_root_result_binding:v01"
)
_B4_ROOT_SHORTCUT_PREDICATE_V01 = (
    "authorize_non_action_informational_answer_shortcut_v01"
)
_B4_ROOT_SHORTCUT_POLICY_REF_V01 = "policy:drs_answer_shortcut:v0.1"
_B4_INFORMATIONAL_INTENT_CLASSES_V01 = (
    "informational_summary",
    "informational_lookup",
    "informational_explanation",
    "context_lookup",
    "warning_lookup",
    "historical_inspection",
    "trend_analysis",
)

_ROOT_SHORTCUT_FIELDS = (
    "root_shortcut_projection_version",
    "root_shortcut_projection_id",
    "owning_local_root_id",
    "root_kernel_id",
    "root_decision_input_id",
    "root_decision_id",
    "root_decision_hash",
    "selected_candidate_id",
    "semantic_address_id",
    "meaning_record_id",
    "query_id",
    "query_evaluation_id",
    "allowed_reuse_class",
    "scope_fingerprint",
    "policy_version",
    "schema_versions",
    "valid_from",
    "valid_to",
    "root_shortcut_policy_ref",
    "carries_validated_authority_evidence",
    "creates_authority",
    "creates_permission",
    "creates_action_commit_packet",
    "creates_receipt",
    "creates_effect",
    "creates_final_output",
)
_REUSE_CERTIFICATE_FIELDS = (
    "certificate_version",
    "certificate_id",
    "semantic_address_id",
    "meaning_record_id",
    "query_id",
    "query_evaluation_id",
    "resolution_candidate_id",
    "root_shortcut_authorization_projection_id",
    "owning_local_root_id",
    "root_decision_input_id",
    "root_decision_id",
    "root_decision_hash",
    "case_type",
    "scope_fingerprint",
    "required_evidence_classes",
    "observed_evidence_fingerprint",
    "forbidden_changes",
    "checked_dependency_fingerprint",
    "valid_from",
    "valid_to",
    "reuse_class",
    "policy_version",
    "schema_versions",
    "root_shortcut_policy_ref",
    "source_history_hash",
    "action_history_binding_id",
    "issued_at",
    "evaluated_at",
    "creates_authority",
    "creates_permission",
    "creates_final_output",
    "creates_action_commit_packet",
    "creates_receipt",
    "creates_capability",
    "creates_effect_handle",
    "creates_effect",
    "real_world_effects_count",
    "proves_external_truth",
    "proves_action_occurred",
)
_G2A_HISTORY_FIELDS = (
    "binding_version",
    "binding_id",
    "packet_id",
    "registry_id",
    "transition_history_sha256",
    "disposition_history_sha256",
    "lifecycle_state",
    "disposition",
    "reservation_owner_packet_id",
    "terminal_receipt_ref",
    "current_status_validation_id",
    "current_status_evaluated_at",
    "current_status_evaluation_time_source",
    "shortcut_eligible",
    "reason_codes",
    "creates_authority",
    "creates_permission",
)
_IDENTITY_PROFILES = (
    (
        "RootShortcutAuthorizationProjectionV01",
        "root_shortcut_projection_id",
        "hedgehog:drs:root_shortcut_projection:v01",
        "drsrootshortcut_v01:",
        _ROOT_SHORTCUT_FIELDS,
    ),
    (
        "ReuseCertificateV01",
        "certificate_id",
        "hedgehog:drs:reuse_certificate:v01",
        "reusecert_v01:",
        _REUSE_CERTIFICATE_FIELDS,
    ),
    (
        "G2AActionHistoryBindingV01",
        "binding_id",
        "hedgehog:drs:g2a_history_binding:v01",
        "drsg2ahistory_v01:",
        _G2A_HISTORY_FIELDS,
    ),
)


@_dataclass(frozen=True)
class RootShortcutAuthorizationProjectionV01:
    root_shortcut_projection_version: str
    root_shortcut_projection_id: str
    owning_local_root_id: str
    root_kernel_id: str
    root_decision_input_id: str
    root_decision_id: str
    root_decision_hash: str
    selected_candidate_id: str
    semantic_address_id: str
    meaning_record_id: str
    query_id: str
    query_evaluation_id: str
    allowed_reuse_class: str
    scope_fingerprint: str
    policy_version: str
    schema_versions: tuple[str, ...]
    valid_from: int
    valid_to: int
    root_shortcut_policy_ref: str
    carries_validated_authority_evidence: bool
    creates_authority: bool
    creates_permission: bool
    creates_action_commit_packet: bool
    creates_receipt: bool
    creates_effect: bool
    creates_final_output: bool


@_dataclass(frozen=True)
class ReuseCertificateV01:
    certificate_version: str
    certificate_id: str
    semantic_address_id: str
    meaning_record_id: str
    query_id: str
    query_evaluation_id: str
    resolution_candidate_id: str
    root_shortcut_authorization_projection_id: str
    owning_local_root_id: str
    root_decision_input_id: str
    root_decision_id: str
    root_decision_hash: str
    case_type: str
    scope_fingerprint: str
    required_evidence_classes: tuple[str, ...]
    observed_evidence_fingerprint: str
    forbidden_changes: tuple[str, ...]
    checked_dependency_fingerprint: str
    valid_from: int
    valid_to: int
    reuse_class: str
    policy_version: str
    schema_versions: tuple[str, ...]
    root_shortcut_policy_ref: str
    source_history_hash: str
    action_history_binding_id: str | None
    issued_at: int
    evaluated_at: int
    creates_authority: bool
    creates_permission: bool
    creates_final_output: bool
    creates_action_commit_packet: bool
    creates_receipt: bool
    creates_capability: bool
    creates_effect_handle: bool
    creates_effect: bool
    real_world_effects_count: int
    proves_external_truth: bool
    proves_action_occurred: bool


@_dataclass(frozen=True)
class G2AActionHistoryBindingV01:
    binding_version: str
    binding_id: str
    packet_id: str
    registry_id: str
    transition_history_sha256: str
    disposition_history_sha256: str
    lifecycle_state: str
    disposition: str
    reservation_owner_packet_id: str | None
    terminal_receipt_ref: str | None
    current_status_validation_id: str
    current_status_evaluated_at: int
    current_status_evaluation_time_source: str
    shortcut_eligible: bool
    reason_codes: tuple[str, ...]
    creates_authority: bool
    creates_permission: bool


def _plain_value(value: object) -> object:
    if type(value) is RootShortcutAuthorizationProjectionV01:
        return {
            name: _plain_value(getattr(value, name))
            for name in _ROOT_SHORTCUT_FIELDS
        }
    if type(value) is ReuseCertificateV01:
        return {
            name: _plain_value(getattr(value, name))
            for name in _REUSE_CERTIFICATE_FIELDS
        }
    if type(value) is G2AActionHistoryBindingV01:
        return {
            name: _plain_value(getattr(value, name))
            for name in _G2A_HISTORY_FIELDS
        }
    return _plain_data_value(value)


def _identity_value(value: object) -> object:
    if type(value) is tuple:
        return [_identity_value(item) for item in value]
    return _canonical_plain_value(value)


def _profile(type_name: str) -> tuple[str, str, str, tuple[str, ...]]:
    for name, identity_field, domain, prefix, fields in _IDENTITY_PROFILES:
        if name == type_name:
            return identity_field, domain, prefix, fields
    raise ValueError("drs_identity_profile_invalid")


def _identity(value: object, type_name: str) -> str:
    identity_field, domain, prefix, fields = _profile(type_name)
    material = [
        _identity_value(getattr(value, name))
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
    ):
        return "drs_identity_invalid"
    if actual != _identity(value, type_name):
        if type_name == "ReuseCertificateV01":
            return "reuse_certificate_identity_invalid"
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
    final = _replace(
        provisional,
        **{identity_field: _identity(provisional, type_name)},
    )
    if not callable(validator):
        raise ValueError("drs_builder_invalid") from None
    valid, final_reasons = validator(final)
    if not valid:
        raise ValueError(final_reasons[0]) from None
    return final


def _version_reason(value: object) -> str | None:
    if type(value) is not str:
        return "drs_exact_type_required"
    if value != _PROFILE_VERSION:
        return "drs_schema_version_mismatch"
    return None


def _canonical_prefixed_id(value: object, prefix: str) -> bool:
    return (
        type(value) is str
        and value.startswith(prefix)
        and len(value) == len(prefix) + 64
        and _is_sha256(value[len(prefix):])
    )


def _root_projection_reasons(
    value: object,
    *,
    check_identity: bool,
) -> tuple[str, ...]:
    if type(value) is not RootShortcutAuthorizationProjectionV01:
        return ("drs_exact_type_required",)
    reasons: list[str] = []
    reason = _version_reason(value.root_shortcut_projection_version)
    if reason:
        reasons.append(reason)
    for item in (
        value.owning_local_root_id,
        value.root_kernel_id,
        value.root_decision_input_id,
        value.root_decision_id,
        value.policy_version,
        value.root_shortcut_policy_ref,
    ):
        if not _is_reference(item):
            reasons.append("drs_root_projection_invalid")
    if not _is_sha256(value.root_decision_hash):
        reasons.append("drs_root_projection_invalid")
    for item, prefix in (
        (value.selected_candidate_id, "drscandidate_v01:"),
        (value.semantic_address_id, "drsaddr_v01:"),
        (value.meaning_record_id, "drsmeaning_v01:"),
        (value.query_id, "drsquery_v01:"),
        (value.query_evaluation_id, "drsqeval_v01:"),
    ):
        if not _canonical_prefixed_id(item, prefix):
            reasons.append("drs_root_projection_invalid")
    if type(value.allowed_reuse_class) is not str or value.allowed_reuse_class not in _ENABLED_REUSE_CLASSES:
        reasons.append("drs_reuse_class_disabled")
    if not _is_sha256(value.scope_fingerprint):
        reasons.append("drs_root_projection_invalid")
    reasons.extend(
        _token_tuple_reasons(value.schema_versions, maximum_items=32)
    )
    if not _is_int64(value.valid_from) or not _is_int64(value.valid_to):
        reasons.append("drs_time_type_invalid")
    elif value.valid_from >= value.valid_to:
        reasons.append("drs_time_validity_interval_invalid")
    if value.carries_validated_authority_evidence is not True:
        reasons.append("drs_root_projection_invalid")
    for flag in (
        value.creates_authority,
        value.creates_permission,
        value.creates_action_commit_packet,
        value.creates_receipt,
        value.creates_effect,
        value.creates_final_output,
    ):
        if flag is not False:
            reasons.append("drs_root_projection_invalid")
    if check_identity and not reasons:
        reason = _id_reason(value, "RootShortcutAuthorizationProjectionV01")
        if reason:
            reasons.append(reason)
    return _dedupe(reasons)


def build_root_shortcut_authorization_projection_v01(
    *,
    owning_local_root_id: str,
    root_kernel_id: str,
    root_decision_input_id: str,
    root_decision_id: str,
    root_decision_hash: str,
    selected_candidate_id: str,
    semantic_address_id: str,
    meaning_record_id: str,
    query_id: str,
    query_evaluation_id: str,
    allowed_reuse_class: str,
    scope_fingerprint: str,
    policy_version: str,
    schema_versions: tuple[str, ...],
    valid_from: int,
    valid_to: int,
    root_shortcut_policy_ref: str,
) -> RootShortcutAuthorizationProjectionV01:
    try:
        provisional = RootShortcutAuthorizationProjectionV01(
            root_shortcut_projection_version=_PROFILE_VERSION,
            root_shortcut_projection_id="drsrootshortcut_v01:" + "0" * 64,
            owning_local_root_id=owning_local_root_id,
            root_kernel_id=root_kernel_id,
            root_decision_input_id=root_decision_input_id,
            root_decision_id=root_decision_id,
            root_decision_hash=root_decision_hash,
            selected_candidate_id=selected_candidate_id,
            semantic_address_id=semantic_address_id,
            meaning_record_id=meaning_record_id,
            query_id=query_id,
            query_evaluation_id=query_evaluation_id,
            allowed_reuse_class=allowed_reuse_class,
            scope_fingerprint=scope_fingerprint,
            policy_version=policy_version,
            schema_versions=schema_versions,
            valid_from=valid_from,
            valid_to=valid_to,
            root_shortcut_policy_ref=root_shortcut_policy_ref,
            carries_validated_authority_evidence=True,
            creates_authority=False,
            creates_permission=False,
            creates_action_commit_packet=False,
            creates_receipt=False,
            creates_effect=False,
            creates_final_output=False,
        )
        return _finish(
            provisional,
            type_name="RootShortcutAuthorizationProjectionV01",
            reasons=_root_projection_reasons(
                provisional, check_identity=False
            ),
            validator=validate_root_shortcut_authorization_projection_v01,
        )
    except ValueError as exc:
        reason = str(exc)
        raise ValueError(
            reason if reason.startswith("drs_") else "drs_root_projection_invalid"
        ) from None
    except Exception:
        raise ValueError("drs_root_projection_invalid") from None


def validate_root_shortcut_authorization_projection_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    try:
        reasons = _root_projection_reasons(value, check_identity=True)
        return not reasons, reasons
    except Exception:
        return False, ("drs_root_projection_invalid",)


def root_shortcut_authorization_projection_to_plain_data_v01(
    value: object,
) -> dict[str, object]:
    if type(value) is not RootShortcutAuthorizationProjectionV01:
        raise ValueError("drs_exact_type_required") from None
    return {
        name: _plain_value(getattr(value, name))
        for name in _ROOT_SHORTCUT_FIELDS
    }


def _certificate_reasons(
    value: object,
    *,
    check_identity: bool,
) -> tuple[str, ...]:
    if type(value) is not ReuseCertificateV01:
        return ("drs_exact_type_required",)
    reasons: list[str] = []
    reason = _version_reason(value.certificate_version)
    if reason:
        reasons.append(reason)
    for item, prefix in (
        (value.semantic_address_id, "drsaddr_v01:"),
        (value.meaning_record_id, "drsmeaning_v01:"),
        (value.resolution_candidate_id, "drscandidate_v01:"),
        (
            value.root_shortcut_authorization_projection_id,
            "drsrootshortcut_v01:",
        ),
    ):
        if not _canonical_prefixed_id(item, prefix):
            reasons.append("reuse_certificate_cross_profile_mismatch")
    for item in (
        value.owning_local_root_id,
        value.root_decision_input_id,
        value.root_decision_id,
        value.policy_version,
        value.root_shortcut_policy_ref,
    ):
        if not _is_reference(item):
            reasons.append("reuse_certificate_cross_profile_mismatch")
    for item, prefix in (
        (value.query_id, "drsquery_v01:"),
        (value.query_evaluation_id, "drsqeval_v01:"),
    ):
        if not _canonical_prefixed_id(item, prefix):
            reasons.append("reuse_certificate_cross_profile_mismatch")
    if not _is_sha256(value.root_decision_hash):
        reasons.append("reuse_certificate_cross_profile_mismatch")
    if value.case_type != "NON_ACTION_INFORMATIONAL" or type(value.case_type) is not str:
        reasons.append("drs_action_intent_shortcut_forbidden")
    for digest in (
        value.scope_fingerprint,
        value.observed_evidence_fingerprint,
        value.checked_dependency_fingerprint,
        value.source_history_hash,
    ):
        if not _is_sha256(digest):
            reasons.append("reuse_certificate_cross_profile_mismatch")
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
    if not _is_int64(value.valid_from) or not _is_int64(value.valid_to):
        reasons.append("drs_time_type_invalid")
    elif value.valid_from >= value.valid_to:
        reasons.append("drs_time_validity_interval_invalid")
    if type(value.reuse_class) is not str or value.reuse_class not in _ENABLED_REUSE_CLASSES:
        reasons.append("drs_reuse_class_disabled")
    if value.action_history_binding_id is not None and not _canonical_prefixed_id(
        value.action_history_binding_id, "drsg2ahistory_v01:"
    ):
        reasons.append("reuse_certificate_cross_profile_mismatch")
    if value.reuse_class == "ANSWER_SHORTCUT" and value.action_history_binding_id is not None:
        reasons.append("drs_action_history_shortcut_forbidden")
    if not _is_int64(value.issued_at) or not _is_int64(value.evaluated_at):
        reasons.append("drs_time_type_invalid")
    if (
        type(value.issued_at) is int
        and type(value.evaluated_at) is int
        and value.issued_at > value.evaluated_at
    ):
        reasons.append("reuse_certificate_cross_profile_mismatch")
    for flag in (
        value.creates_authority,
        value.creates_permission,
        value.creates_final_output,
        value.creates_action_commit_packet,
        value.creates_receipt,
        value.creates_capability,
        value.creates_effect_handle,
        value.creates_effect,
        value.proves_external_truth,
        value.proves_action_occurred,
    ):
        if flag is not False:
            reasons.append("reuse_certificate_non_authority_invalid")
    if type(value.real_world_effects_count) is not int:
        reasons.append("drs_exact_int_required")
    elif value.real_world_effects_count != 0:
        reasons.append("reuse_certificate_non_authority_invalid")
    if check_identity and not reasons:
        reason = _id_reason(value, "ReuseCertificateV01")
        if reason:
            reasons.append(reason)
    return _dedupe(reasons)


def build_reuse_certificate_v01(
    *,
    semantic_address_id: str,
    meaning_record_id: str,
    query_id: str,
    query_evaluation_id: str,
    resolution_candidate_id: str,
    root_shortcut_authorization_projection: RootShortcutAuthorizationProjectionV01,
    case_type: str,
    required_evidence_classes: tuple[str, ...],
    observed_evidence_fingerprint: str,
    forbidden_changes: tuple[str, ...],
    checked_dependency_fingerprint: str,
    valid_from: int,
    valid_to: int,
    reuse_class: str,
    source_history_hash: str,
    action_history_binding_id: str | None,
    issued_at: int,
    evaluated_at: int,
) -> ReuseCertificateV01:
    try:
        projection_valid, projection_reasons = (
            validate_root_shortcut_authorization_projection_v01(
                root_shortcut_authorization_projection
            )
        )
        if not projection_valid:
            raise ValueError(projection_reasons[0])
        projection = root_shortcut_authorization_projection
        if type(projection) is not RootShortcutAuthorizationProjectionV01:
            raise ValueError("drs_exact_type_required")
        if (
            semantic_address_id != projection.semantic_address_id
            or meaning_record_id != projection.meaning_record_id
            or query_id != projection.query_id
            or query_evaluation_id != projection.query_evaluation_id
            or resolution_candidate_id != projection.selected_candidate_id
            or reuse_class != projection.allowed_reuse_class
            or valid_from != projection.valid_from
            or valid_to != projection.valid_to
        ):
            raise ValueError("reuse_certificate_cross_profile_mismatch")
        provisional = ReuseCertificateV01(
            certificate_version=_PROFILE_VERSION,
            certificate_id="reusecert_v01:" + "0" * 64,
            semantic_address_id=semantic_address_id,
            meaning_record_id=meaning_record_id,
            query_id=query_id,
            query_evaluation_id=query_evaluation_id,
            resolution_candidate_id=resolution_candidate_id,
            root_shortcut_authorization_projection_id=(
                projection.root_shortcut_projection_id
            ),
            owning_local_root_id=projection.owning_local_root_id,
            root_decision_input_id=projection.root_decision_input_id,
            root_decision_id=projection.root_decision_id,
            root_decision_hash=projection.root_decision_hash,
            case_type=case_type,
            scope_fingerprint=projection.scope_fingerprint,
            required_evidence_classes=required_evidence_classes,
            observed_evidence_fingerprint=observed_evidence_fingerprint,
            forbidden_changes=forbidden_changes,
            checked_dependency_fingerprint=checked_dependency_fingerprint,
            valid_from=valid_from,
            valid_to=valid_to,
            reuse_class=reuse_class,
            policy_version=projection.policy_version,
            schema_versions=projection.schema_versions,
            root_shortcut_policy_ref=projection.root_shortcut_policy_ref,
            source_history_hash=source_history_hash,
            action_history_binding_id=action_history_binding_id,
            issued_at=issued_at,
            evaluated_at=evaluated_at,
            creates_authority=False,
            creates_permission=False,
            creates_final_output=False,
            creates_action_commit_packet=False,
            creates_receipt=False,
            creates_capability=False,
            creates_effect_handle=False,
            creates_effect=False,
            real_world_effects_count=0,
            proves_external_truth=False,
            proves_action_occurred=False,
        )
        return _finish(
            provisional,
            type_name="ReuseCertificateV01",
            reasons=_certificate_reasons(provisional, check_identity=False),
            validator=validate_reuse_certificate_v01,
        )
    except ValueError as exc:
        reason = str(exc)
        allowed_prefixes = ("drs_", "reuse_certificate_")
        raise ValueError(
            reason
            if reason.startswith(allowed_prefixes)
            else "reuse_certificate_invalid"
        ) from None
    except Exception:
        raise ValueError("reuse_certificate_invalid") from None


def validate_reuse_certificate_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    try:
        reasons = _certificate_reasons(value, check_identity=True)
        return not reasons, reasons
    except Exception:
        return False, ("reuse_certificate_invalid",)


def reuse_certificate_to_plain_data_v01(value: object) -> dict[str, object]:
    if type(value) is not ReuseCertificateV01:
        raise ValueError("drs_exact_type_required") from None
    return {
        name: _plain_value(getattr(value, name))
        for name in _REUSE_CERTIFICATE_FIELDS
    }


def _b4_root_claim_preimage_v01(
    *,
    report: object,
    candidate: object,
    evaluation: object,
    certificate: ReuseCertificateV01,
) -> dict[str, object]:
    query = report.query
    return {
        "profile_version": _PROFILE_VERSION,
        "semantic_address_id": report.semantic_address.semantic_address_id,
        "meaning_record_id": candidate.meaning_record_id,
        "query_id": query.query_id,
        "query_evaluation_id": evaluation.query_evaluation_id,
        "resolution_candidate_id": candidate.resolution_candidate_id,
        "reuse_class": "ANSWER_SHORTCUT",
        "case_type": "NON_ACTION_INFORMATIONAL",
        "scope_fingerprint": query.scope_fingerprint,
        "policy_version": query.policy_version,
        "schema_versions": list(query.schema_versions),
        "required_evidence_classes": list(
            query.required_evidence_classes
        ),
        "observed_evidence_fingerprint": (
            evaluation.observed_evidence_fingerprint
        ),
        "forbidden_changes": list(query.forbidden_changes),
        "checked_dependency_fingerprint": (
            evaluation.checked_dependency_fingerprint
        ),
        "source_history_hash": evaluation.source_history_hash,
        "action_history_binding_id": None,
        "valid_from": certificate.valid_from,
        "valid_to": certificate.valid_to,
        "issued_at": certificate.issued_at,
        "evaluated_at": evaluation.evaluated_at,
        "root_shortcut_policy_ref": (
            _B4_ROOT_SHORTCUT_POLICY_REF_V01
        ),
    }


def validate_existing_root_shortcut_decision_v01(
    *,
    resolution_report: DRSResolutionReportV01,
    root_kernel: RootDecisionKernelV01,
    root_decision_input: RootDecisionInputV01,
    root_decision_result: RootDecisionResultV01,
    use_time: int,
) -> tuple[bool, tuple[str, ...]]:
    try:
        from hedgehog.drs_memory_resolution_v01 import (
            DRSResolutionReportV01 as _DRSResolutionReportV01,
            QueryEvaluationStateV01 as _QueryEvaluationStateV01,
            ResolutionCandidateV01 as _ResolutionCandidateV01,
            validate_drs_resolution_report_v01 as _validate_report,
        )
        from hedgehog.drs_semantic_address_v01 import (
            MeaningRecordV01 as _MeaningRecordV01,
            validate_meaning_record_v01 as _validate_record,
        )
        from hedgehog.kernel.root_decision_v01 import (
            ROOT_DECISION_ACCEPT as _ROOT_DECISION_ACCEPT,
            RootDecisionInputV01 as _RootDecisionInputV01,
            RootDecisionKernelV01 as _RootDecisionKernelV01,
            RootDecisionResultV01 as _RootDecisionResultV01,
            root_decision_input_to_plain_dict_v01 as _root_input_plain,
            root_decision_result_to_plain_dict_v01 as _root_result_plain,
            validate_root_decision_input_v01 as _validate_root_input,
            validate_root_decision_kernel_v01 as _validate_root_kernel,
            validate_root_decision_result_v01 as _validate_root_result,
        )

        if (
            type(resolution_report) is not _DRSResolutionReportV01
            or type(root_kernel) is not _RootDecisionKernelV01
            or type(root_decision_input) is not _RootDecisionInputV01
            or type(root_decision_result) is not _RootDecisionResultV01
            or type(use_time) is not int
            or not _is_int64(use_time)
        ):
            return False, ("drs_exact_type_or_identity_invalid",)

        report_valid, report_reasons = _validate_report(
            resolution_report
        )
        if not report_valid or report_reasons:
            return False, ("drs_exact_type_or_identity_invalid",)
        report = resolution_report
        projection = report.root_shortcut_projection
        certificate = report.reuse_certificate
        if type(projection) is not RootShortcutAuthorizationProjectionV01:
            return False, ("drs_root_projection_invalid",)
        projection_valid, projection_reasons = (
            validate_root_shortcut_authorization_projection_v01(projection)
        )
        if not projection_valid or projection_reasons:
            return False, ("drs_root_projection_invalid",)
        if type(certificate) is not ReuseCertificateV01:
            return False, ("reuse_certificate_identity_invalid",)
        certificate_valid, certificate_reasons = (
            validate_reuse_certificate_v01(certificate)
        )
        if not certificate_valid:
            if "reuse_certificate_identity_invalid" in certificate_reasons:
                return False, ("reuse_certificate_identity_invalid",)
            return False, ("reuse_certificate_cross_profile_mismatch",)

        if (
            report.final_status != "PASS"
            or report.reason_codes
            or report.persistent_records_unchanged is not True
            or any(
                value != 0 or type(value) is not int
                for value in (
                    report.provider_calls,
                    report.network_calls,
                    report.gemini_calls,
                    report.external_drs_calls,
                    report.connector_calls,
                    report.real_world_effects_count,
                )
            )
            or report.selected_candidate_id is None
            or not report.ranked_candidate_ids
            or report.selected_candidate_id
            != report.ranked_candidate_ids[0]
        ):
            return False, ("reuse_certificate_cross_profile_mismatch",)

        if (
            len(report.source_records) != len(report.query_evaluations)
            or tuple(
                record.meaning_record_id
                for record in report.source_records
            )
            != tuple(
                evaluation.meaning_record_id
                for evaluation in report.query_evaluations
            )
            or tuple(
                record.meaning_record_id
                for record in report.source_records
            )
            != report.retrieval_plan.proposed_record_ids
            or tuple(
                candidate.resolution_candidate_id
                for candidate in sorted(
                    report.eligible_candidates,
                    key=lambda item: (
                        -item.total_score_units,
                        item.resolution_candidate_id,
                    ),
                )
            )
            != report.ranked_candidate_ids
        ):
            return False, ("reuse_certificate_cross_profile_mismatch",)
        evaluation_by_id = {
            item.query_evaluation_id: item
            for item in report.query_evaluations
        }
        candidate_counts: dict[str, int] = {}
        for item in report.eligible_candidates:
            candidate_counts[item.query_evaluation_id] = (
                candidate_counts.get(item.query_evaluation_id, 0) + 1
            )
        if any(
            candidate_counts.get(item.query_evaluation_id, 0)
            != (1 if item.eligible_for_ranking else 0)
            for item in report.query_evaluations
        ) or any(
            item.query_evaluation_id not in evaluation_by_id
            or not evaluation_by_id[
                item.query_evaluation_id
            ].eligible_for_ranking
            for item in report.eligible_candidates
        ):
            return False, ("reuse_certificate_cross_profile_mismatch",)

        candidates = tuple(
            item
            for item in report.eligible_candidates
            if (
                type(item) is _ResolutionCandidateV01
                and item.resolution_candidate_id
                == report.selected_candidate_id
            )
        )
        if len(candidates) != 1:
            return False, ("reuse_certificate_cross_profile_mismatch",)
        candidate = candidates[0]
        evaluations = tuple(
            item
            for item in report.query_evaluations
            if (
                type(item) is _QueryEvaluationStateV01
                and item.query_evaluation_id
                == candidate.query_evaluation_id
            )
        )
        if len(evaluations) != 1:
            return False, ("reuse_certificate_cross_profile_mismatch",)
        evaluation = evaluations[0]
        records = tuple(
            item
            for item in report.source_records
            if (
                type(item) is _MeaningRecordV01
                and item.meaning_record_id == candidate.meaning_record_id
            )
        )
        if len(records) != 1:
            return False, ("reuse_certificate_cross_profile_mismatch",)
        record = records[0]
        record_valid, record_reasons = _validate_record(record)
        if not record_valid or record_reasons:
            return False, ("drs_exact_type_or_identity_invalid",)

        query = report.query
        address_id = report.semantic_address.semantic_address_id
        if (
            candidate.query_id != query.query_id
            or candidate.semantic_address_id != address_id
            or candidate.query_evaluation_id
            != evaluation.query_evaluation_id
            or candidate.meaning_record_id != record.meaning_record_id
            or candidate.source_history_hash
            != evaluation.source_history_hash
            or candidate.action_history_binding_id
            != evaluation.action_history_binding_id
            or candidate.freshness_units
            != evaluation.current_freshness_units
            or evaluation.query_state != "FRESH_CANDIDATE"
            or evaluation.eligible_for_ranking is not True
            or evaluation.reason_codes
            or evaluation.query_id != query.query_id
            or evaluation.semantic_address_id != address_id
            or evaluation.meaning_record_id != record.meaning_record_id
            or evaluation.evaluated_at != query.evaluation_time
            or evaluation.evaluation_time_source
            != query.evaluation_time_source
        ):
            return False, ("reuse_certificate_cross_profile_mismatch",)

        authority = record.authority_envelope
        if (
            record.semantic_address != report.semantic_address
            or record.semantic_address.intent_class
            not in _B4_INFORMATIONAL_INTENT_CLASSES_V01
            or authority.authority_class
            not in ("ROOT_ACCEPTED_CONTEXT", "ROOT_ACCEPTED_WORK")
            or authority.root_acceptance_state
            not in ("ACCEPTED_CONTEXT", "ACCEPTED_WORK")
            or authority.action_permission_present is not False
            or authority.creates_permission is not False
            or record.creates_authority is not False
            or record.creates_permission is not False
            or record.persistent_lifecycle_state != "ACTIVE"
            or record.conflict_hints
        ):
            return False, ("drs_action_intent_shortcut_forbidden",)

        if (
            evaluation.action_history_binding_id is not None
            or candidate.action_history_binding_id is not None
            or certificate.action_history_binding_id is not None
        ):
            return False, ("drs_action_history_shortcut_forbidden",)

        if (
            projection.owning_local_root_id
            != query.owning_local_root_id
            or projection.owning_local_root_id
            != authority.owning_local_root_id
        ):
            return False, ("drs_root_owner_mismatch",)
        if (
            projection.selected_candidate_id
            != candidate.resolution_candidate_id
            or projection.semantic_address_id != address_id
            or projection.meaning_record_id != record.meaning_record_id
            or projection.query_id != query.query_id
            or projection.query_evaluation_id
            != evaluation.query_evaluation_id
            or projection.allowed_reuse_class != "ANSWER_SHORTCUT"
            or projection.scope_fingerprint != query.scope_fingerprint
            or projection.policy_version != query.policy_version
            or projection.policy_version != record.policy_version
            or projection.schema_versions != query.schema_versions
            or projection.schema_versions != record.schema_versions
            or projection.root_shortcut_policy_ref
            != _B4_ROOT_SHORTCUT_POLICY_REF_V01
            or projection.carries_validated_authority_evidence is not True
            or any(
                value is not False
                for value in (
                    projection.creates_authority,
                    projection.creates_permission,
                    projection.creates_action_commit_packet,
                    projection.creates_receipt,
                    projection.creates_effect,
                    projection.creates_final_output,
                )
            )
        ):
            return False, ("drs_root_projection_invalid",)

        if (
            certificate.root_shortcut_authorization_projection_id
            != projection.root_shortcut_projection_id
            or certificate.semantic_address_id != address_id
            or certificate.meaning_record_id != record.meaning_record_id
            or certificate.query_id != query.query_id
            or certificate.query_evaluation_id
            != evaluation.query_evaluation_id
            or certificate.resolution_candidate_id
            != candidate.resolution_candidate_id
            or certificate.owning_local_root_id
            != projection.owning_local_root_id
            or certificate.root_decision_input_id
            != projection.root_decision_input_id
            or certificate.root_decision_id
            != projection.root_decision_id
            or certificate.root_decision_hash
            != projection.root_decision_hash
            or certificate.case_type != "NON_ACTION_INFORMATIONAL"
            or certificate.scope_fingerprint
            != projection.scope_fingerprint
            or certificate.scope_fingerprint != query.scope_fingerprint
            or certificate.required_evidence_classes
            != query.required_evidence_classes
            or certificate.observed_evidence_fingerprint
            != evaluation.observed_evidence_fingerprint
            or certificate.forbidden_changes != query.forbidden_changes
            or certificate.checked_dependency_fingerprint
            != evaluation.checked_dependency_fingerprint
            or certificate.reuse_class != "ANSWER_SHORTCUT"
            or certificate.reuse_class
            != projection.allowed_reuse_class
            or certificate.policy_version != query.policy_version
            or certificate.policy_version != record.policy_version
            or certificate.schema_versions != query.schema_versions
            or certificate.schema_versions != record.schema_versions
            or certificate.root_shortcut_policy_ref
            != _B4_ROOT_SHORTCUT_POLICY_REF_V01
            or certificate.source_history_hash
            != evaluation.source_history_hash
            or certificate.source_history_hash
            != candidate.source_history_hash
            or certificate.evaluated_at != evaluation.evaluated_at
            or any(
                value is not False
                for value in (
                    certificate.creates_authority,
                    certificate.creates_permission,
                    certificate.creates_final_output,
                    certificate.creates_action_commit_packet,
                    certificate.creates_receipt,
                    certificate.creates_capability,
                    certificate.creates_effect_handle,
                    certificate.creates_effect,
                    certificate.proves_external_truth,
                    certificate.proves_action_occurred,
                )
            )
            or certificate.real_world_effects_count != 0
        ):
            return False, ("reuse_certificate_cross_profile_mismatch",)

        if (
            projection.valid_from != certificate.valid_from
            or projection.valid_to != certificate.valid_to
        ):
            return False, ("reuse_certificate_cross_profile_mismatch",)
        if not (
            certificate.valid_from
            <= use_time
            < certificate.valid_to
        ):
            return False, ("reuse_certificate_expired",)
        if not (
            certificate.issued_at
            <= certificate.evaluated_at
            <= use_time
        ):
            return False, ("reuse_certificate_expired",)

        if _validate_root_kernel(root_kernel):
            return False, ("drs_exact_type_or_identity_invalid",)
        if _validate_root_input(
            kernel=root_kernel,
            decision_input=root_decision_input,
        ):
            return False, ("drs_exact_type_or_identity_invalid",)
        if _validate_root_result(
            kernel=root_kernel,
            decision_input=root_decision_input,
            result=root_decision_result,
        ):
            return False, ("drs_exact_type_or_identity_invalid",)

        if (
            root_decision_input.target_root_id
            != projection.owning_local_root_id
            or root_decision_result.target_root_id
            != projection.owning_local_root_id
        ):
            return False, ("drs_root_owner_mismatch",)
        if (
            projection.root_kernel_id != root_kernel.kernel_id
            or projection.root_decision_input_id
            != root_decision_input.decision_input_id
            or projection.root_decision_id
            != root_decision_result.decision_id
            or root_decision_result.decision_input_id
            != root_decision_input.decision_input_id
            or root_decision_input.transaction_id != query.query_id
            or root_decision_result.transaction_id != query.query_id
        ):
            return False, ("drs_root_decision_binding_invalid",)
        root_hash = _domain_separated_sha256_hex_v01(
            domain=_B4_ROOT_RESULT_BINDING_DOMAIN_V01,
            payload=_canonical_json_bytes_v01(
                _root_result_plain(root_decision_result)
            ),
        )
        if (
            projection.root_decision_hash != root_hash
            or certificate.root_decision_hash != root_hash
            or root_decision_result.decision != _ROOT_DECISION_ACCEPT
            or root_decision_result.reason_code
            != "validated_candidate_accepted"
            or root_decision_result.selected_candidate_id
            != report.selected_candidate_id
            or root_decision_result.root_commit_created is not True
            or root_decision_result.permission_created is not False
            or root_decision_result.final_output_created is not False
            or root_decision_result.effect_requested is not False
        ):
            return False, ("drs_root_decision_binding_invalid",)

        input_plain = _root_input_plain(root_decision_input)
        claims = input_plain["root_review_packet"][
            "synthesis_proposal"
        ]["normalized_claims"]
        if type(claims) is not list or len(claims) != 1:
            return False, ("drs_root_decision_binding_invalid",)
        claim = claims[0]
        if (
            type(claim) is not dict
            or claim.get("claim_id")
            != candidate.resolution_candidate_id
            or claim.get("subject") != address_id
            or claim.get("predicate")
            != _B4_ROOT_SHORTCUT_PREDICATE_V01
            or claim.get("object_or_value")
            != _b4_root_claim_preimage_v01(
                report=report,
                candidate=candidate,
                evaluation=evaluation,
                certificate=certificate,
            )
            or claim.get("authority_class") != "NONE"
        ):
            return False, ("drs_root_decision_binding_invalid",)
        return True, ()
    except Exception:
        return False, ("drs_exact_type_or_identity_invalid",)


def _g2a_history_reasons(
    value: object,
    *,
    check_identity: bool,
) -> tuple[str, ...]:
    if type(value) is not G2AActionHistoryBindingV01:
        return ("drs_exact_type_required",)
    reasons: list[str] = []
    reason = _version_reason(value.binding_version)
    if reason:
        reasons.append(reason)
    for item in (
        value.packet_id,
        value.registry_id,
        value.current_status_validation_id,
    ):
        if not _is_reference(item):
            reasons.append("drs_action_history_binding_invalid")
    if (
        type(value.current_status_evaluation_time_source) is not str
        or value.current_status_evaluation_time_source
        not in _EVALUATION_TIME_SOURCES
    ):
        reasons.append("drs_action_history_binding_invalid")
    if not _is_sha256(value.transition_history_sha256) or not _is_sha256(
        value.disposition_history_sha256
    ):
        reasons.append("drs_action_history_binding_invalid")
    if type(value.lifecycle_state) is not str or value.lifecycle_state not in _ACTION_LIFECYCLE_STATES:
        reasons.append("drs_action_history_binding_invalid")
    if type(value.disposition) is not str or value.disposition not in _IDEMPOTENCY_DISPOSITIONS:
        reasons.append("drs_action_history_binding_invalid")
    for item in (
        value.reservation_owner_packet_id,
        value.terminal_receipt_ref,
    ):
        if item is not None and not _is_reference(item):
            reasons.append("drs_action_history_binding_invalid")
    if not _is_int64(value.current_status_evaluated_at):
        reasons.append("drs_time_type_invalid")
    if value.shortcut_eligible is not False:
        reasons.append("drs_action_history_shortcut_forbidden")
    reasons.extend(
        _token_tuple_reasons(value.reason_codes, maximum_items=32)
    )
    if not value.reason_codes:
        reasons.append("drs_action_history_binding_invalid")
    if value.creates_authority is not False:
        reasons.append("drs_non_authority_law_invalid")
    if value.creates_permission is not False:
        reasons.append("drs_non_permission_law_invalid")
    if check_identity and not reasons:
        reason = _id_reason(value, "G2AActionHistoryBindingV01")
        if reason:
            reasons.append(reason)
    return _dedupe(reasons)


def build_g2a_action_history_binding_v01(
    *,
    packet_id: str,
    registry_id: str,
    transition_history_sha256: str,
    disposition_history_sha256: str,
    lifecycle_state: str,
    disposition: str,
    reservation_owner_packet_id: str | None,
    terminal_receipt_ref: str | None,
    current_status_validation_id: str,
    current_status_evaluated_at: int,
    current_status_evaluation_time_source: str,
    reason_codes: tuple[str, ...],
) -> G2AActionHistoryBindingV01:
    try:
        provisional = G2AActionHistoryBindingV01(
            binding_version=_PROFILE_VERSION,
            binding_id="drsg2ahistory_v01:" + "0" * 64,
            packet_id=packet_id,
            registry_id=registry_id,
            transition_history_sha256=transition_history_sha256,
            disposition_history_sha256=disposition_history_sha256,
            lifecycle_state=lifecycle_state,
            disposition=disposition,
            reservation_owner_packet_id=reservation_owner_packet_id,
            terminal_receipt_ref=terminal_receipt_ref,
            current_status_validation_id=current_status_validation_id,
            current_status_evaluated_at=current_status_evaluated_at,
            current_status_evaluation_time_source=(
                current_status_evaluation_time_source
            ),
            shortcut_eligible=False,
            reason_codes=reason_codes,
            creates_authority=False,
            creates_permission=False,
        )
        return _finish(
            provisional,
            type_name="G2AActionHistoryBindingV01",
            reasons=_g2a_history_reasons(provisional, check_identity=False),
            validator=validate_g2a_action_history_binding_v01,
        )
    except ValueError as exc:
        reason = str(exc)
        raise ValueError(
            reason if reason.startswith("drs_") else "drs_action_history_binding_invalid"
        ) from None
    except Exception:
        raise ValueError("drs_action_history_binding_invalid") from None


def validate_g2a_action_history_binding_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    try:
        reasons = _g2a_history_reasons(value, check_identity=True)
        return not reasons, reasons
    except Exception:
        return False, ("drs_action_history_binding_invalid",)


def g2a_action_history_binding_to_plain_data_v01(
    value: object,
) -> dict[str, object]:
    if type(value) is not G2AActionHistoryBindingV01:
        raise ValueError("drs_exact_type_required") from None
    return {
        name: _plain_value(getattr(value, name))
        for name in _G2A_HISTORY_FIELDS
    }


__all__ = (
    "RootShortcutAuthorizationProjectionV01",
    "ReuseCertificateV01",
    "G2AActionHistoryBindingV01",
    "build_root_shortcut_authorization_projection_v01",
    "validate_root_shortcut_authorization_projection_v01",
    "root_shortcut_authorization_projection_to_plain_data_v01",
    "build_reuse_certificate_v01",
    "validate_reuse_certificate_v01",
    "reuse_certificate_to_plain_data_v01",
    "validate_existing_root_shortcut_decision_v01",
    "build_g2a_action_history_binding_v01",
    "validate_g2a_action_history_binding_v01",
    "g2a_action_history_binding_to_plain_data_v01",
)
