"""Pure in-memory, deterministic, domain-neutral G1-B2 Kernel contracts.

This module defines a versioned Kernel artifact envelope and field-level
causal-consumption evidence. It has no provider, LLM, network, filesystem, or
domain imports; no transition registry, Root Decision Kernel, or Effect
Firewall; and no Root decision creation, permission creation, FinalOutput
creation, or effect. Authority and lifecycle remain independent. ABI envelope
data does not itself create authority, and causal evidence does not prove
semantic truth. This is not production API stability certification.
"""

from __future__ import annotations

from collections.abc import Mapping as _Mapping
from dataclasses import dataclass as _dataclass
from datetime import datetime as _datetime
import re as _re
import unicodedata as _unicodedata

from hedgehog.kernel.integrity_replay_v01 import (
    CanonicalArtifactRefV01,
    build_canonical_artifact_ref_v01 as _build_canonical_artifact_ref_v01,
    build_default_seal_profile_v01 as _build_default_seal_profile_v01,
    canonical_json_bytes_v01 as _canonical_json_bytes_v01,
)


MODULE_ID = "kernel_abi_v01"
SLICE_ID = "domain_neutral_reference_kernel_gate1_g1b2"
KERNEL_ABI_VERSION = "v1.0"
KERNEL_ABI_MAJOR_VERSION = 1
KERNEL_ABI_MINOR_VERSION = 0
SUPPORTED_ABI_VERSIONS = ("v1.0",)

STATUS_PASS = "PASS"
STATUS_BLOCKED_FAIL_CLOSED = "BLOCKED_FAIL_CLOSED"

AUTHORITY_CLASSES = (
    "ROOT_OWNED",
    "ROOT_AUTHORIZED",
    "ADVISORY",
    "EVIDENCE_ONLY",
    "NON_AUTHORITY",
)

LIFECYCLE_STATES = (
    "PROPOSED",
    "VALIDATED",
    "ROOT_REVIEWED",
    "ROOT_ACCEPTED",
    "ROOT_REJECTED",
    "BLOCKED_FAIL_CLOSED",
    "EXECUTED_MOCK",
    "RECEIPT_RECORDED",
    "FINALIZED",
)

ACTION_PACKET_LIFECYCLE_PROFILE_ID_V01 = (
    "action_packet_lifecycle_profile_v01"
)
ACTION_PACKET_LIFECYCLE_ABI_FAMILY_V01 = "hedgehog_kernel_abi"
ACTION_PACKET_TRANSITION_REGISTRY_FAMILY_V01 = "TransitionRegistryV01"
ACTION_PACKET_LIFECYCLE_STATES_V01 = (
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

ARTIFACT_TYPES = (
    "OrchestratorRouteProposal",
    "RootAcceptedRoute",
    "BSEPPacket",
    "BSEPProjection",
    "SemanticArchitectProposal",
    "RuntimeExecutionTopology",
    "ActorContribution",
    "SemanticEvidence",
    "ValidatedEvidence",
    "ResultProposal",
    "PostVVReport",
    "GTAdvisoryReport",
    "RootOwnedIntent",
    "RootDecision",
    "ExecutionRequest",
    "EvidenceReceipt",
    "RootFinal",
    "CrossRootEvidenceRef",
    "TransactionOutcomeEnvelope",
    "CausalConsumptionRef",
    "ExecutionModeProposal",
    "RootExecutionModeDecision",
    "ExecutionModeRouteEligibility",
    "FractalCellQueueEntry",
    "FractalCellResult",
    "FractalRuntimeReport",
)

CAUSAL_DISPOSITIONS = (
    "USED",
    "REJECTED",
    "IGNORED_WITH_REASON",
    "BLOCKED_BY_GATE",
)

_FRESHNESS_CLASSES = (
    "static",
    "slow_changing",
    "normal",
    "fast_changing",
    "real_time",
)
_ARTIFACT_FIELD_NAMES = (
    "abi_version",
    "artifact_id",
    "artifact_type",
    "schema_version",
    "transaction_id",
    "owner_root_id",
    "source_component",
    "authority_class",
    "lifecycle_state",
    "payload",
    "trace_refs",
    "parent_refs",
    "time_envelope",
)
_RESERVED_PAYLOAD_FIELDS = frozenset(_ARTIFACT_FIELD_NAMES)
_TIME_ENVELOPE_FIELDS = (
    "ct_session_anchor",
    "et_observed_at",
    "freshness_class",
    "kt_asof",
    "pt_created_at",
    "ttl_seconds",
    "valid_from",
    "valid_to",
)
_ABI_VERSION_PATTERN = _re.compile(r"^v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
_SCHEMA_VERSION_PATTERN = _re.compile(
    r"^v(?:0|[1-9][0-9]*)(?:\.(?:0|[1-9][0-9]*))?$"
)
_AWARE_TIMESTAMP_PATTERN = _re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T"
    r"[0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:\.[0-9]+)?(?:Z|[+-][0-9]{2}:[0-9]{2})$"
)
_REASON_PREFIX = {
    "USED": "used:",
    "REJECTED": "rejected:",
    "IGNORED_WITH_REASON": "ignored:",
    "BLOCKED_BY_GATE": "gate:",
}
_ARTIFACT_BUILDER_REASONS = (
    "kernel_artifact_invalid",
    "abi_version_invalid",
    "abi_major_version_unknown",
    "abi_minor_version_unsupported",
    "artifact_id_invalid",
    "artifact_type_unknown",
    "schema_version_invalid",
    "transaction_id_invalid",
    "owner_root_id_invalid",
    "source_component_invalid",
    "authority_class_unknown",
    "lifecycle_state_unknown",
    "payload_invalid",
    "payload_reserved_field",
    "trace_refs_invalid",
    "parent_refs_invalid",
    "time_envelope_invalid",
)
_CAUSAL_BUILDER_REASONS = (
    "causal_consumption_ref_invalid",
    "causal_disposition_unknown",
    "causal_output_field_invalid",
    "causal_reason_required",
    "causal_reason_disposition_mismatch",
    "causal_trace_refs_invalid",
)


@_dataclass(frozen=True)
class _FrozenJSONObject:
    items: tuple[tuple[str, object], ...]


@_dataclass(frozen=True)
class KernelArtifactV01:
    abi_version: str
    artifact_id: str
    artifact_type: str
    schema_version: str
    transaction_id: str
    owner_root_id: str
    source_component: str
    authority_class: str
    lifecycle_state: str
    payload: object
    trace_refs: tuple[str, ...]
    parent_refs: tuple[str, ...]
    time_envelope: object


@_dataclass(frozen=True)
class CausalConsumptionRefV01:
    producer_actor_id: str
    source_artifact_id: str
    output_field: str
    consumer_component: str
    downstream_artifact_id: str
    decision_effect: str
    disposition: str
    reason_code: str
    trace_refs: tuple[str, ...]


@_dataclass(frozen=True)
class ActionPacketLifecycleProfileV01:
    profile_id: str
    abi_family: str
    transition_registry_family: str
    lifecycle_states: tuple[str, ...]


def build_action_packet_lifecycle_profile_v01(
) -> ActionPacketLifecycleProfileV01:
    """Build the explicitly selected G2-A lifecycle ABI profile."""

    return ActionPacketLifecycleProfileV01(
        profile_id=ACTION_PACKET_LIFECYCLE_PROFILE_ID_V01,
        abi_family=ACTION_PACKET_LIFECYCLE_ABI_FAMILY_V01,
        transition_registry_family=(
            ACTION_PACKET_TRANSITION_REGISTRY_FAMILY_V01
        ),
        lifecycle_states=tuple(ACTION_PACKET_LIFECYCLE_STATES_V01),
    )


def validate_action_packet_lifecycle_profile_v01(
    profile: object,
) -> tuple[str, ...]:
    try:
        if type(profile) is not ActionPacketLifecycleProfileV01:
            return ("action_packet_lifecycle_profile_invalid",)
        values = (
            profile.profile_id,
            profile.abi_family,
            profile.transition_registry_family,
        )
        if any(not _action_packet_profile_text_valid(value) for value in values):
            return ("action_packet_lifecycle_profile_invalid",)
        if type(profile.lifecycle_states) is not tuple:
            return ("action_packet_lifecycle_states_invalid",)
        if any(
            not _action_packet_profile_text_valid(state)
            for state in profile.lifecycle_states
        ):
            return ("action_packet_lifecycle_states_invalid",)
        if len(profile.lifecycle_states) != len(set(profile.lifecycle_states)):
            return ("action_packet_lifecycle_states_duplicate",)
        expected = build_action_packet_lifecycle_profile_v01()
        errors: list[str] = []
        if profile.profile_id != expected.profile_id:
            errors.append("action_packet_lifecycle_profile_id_mismatch")
        if profile.abi_family != expected.abi_family:
            errors.append("action_packet_lifecycle_abi_family_mismatch")
        if (
            profile.transition_registry_family
            != expected.transition_registry_family
        ):
            errors.append(
                "action_packet_lifecycle_registry_family_mismatch"
            )
        if profile.lifecycle_states != expected.lifecycle_states:
            errors.append("action_packet_lifecycle_states_mismatch")
        return _dedupe(errors)
    except Exception:
        return ("action_packet_lifecycle_profile_invalid",)


def action_packet_lifecycle_profile_to_plain_dict_v01(
    profile: ActionPacketLifecycleProfileV01,
) -> dict[str, object]:
    try:
        if validate_action_packet_lifecycle_profile_v01(profile):
            raise ValueError("action_packet_lifecycle_profile_invalid")
        result = {
            "profile_id": profile.profile_id,
            "abi_family": profile.abi_family,
            "transition_registry_family": (
                profile.transition_registry_family
            ),
            "lifecycle_states": list(profile.lifecycle_states),
        }
        _canonical_json_bytes_v01(result)
        return result
    except Exception:
        raise ValueError("action_packet_lifecycle_profile_invalid") from None


def _action_packet_profile_text_valid(value: object) -> bool:
    if type(value) is not str or not value or "\x00" in value:
        return False
    try:
        value.encode("utf-8", errors="strict")
        return _unicodedata.normalize("NFC", value) == value
    except Exception:
        return False


def build_kernel_artifact_v01(
    *,
    abi_version: str,
    artifact_id: str,
    artifact_type: str,
    schema_version: str,
    transaction_id: str,
    owner_root_id: str,
    source_component: str,
    authority_class: str,
    lifecycle_state: str,
    payload: object,
    trace_refs: tuple[str, ...],
    parent_refs: tuple[str, ...],
    time_envelope: object,
) -> KernelArtifactV01:
    try:
        try:
            frozen_payload = _freeze_json_value(payload)
        except Exception:
            raise ValueError("payload_invalid") from None
        try:
            frozen_time = _freeze_json_value(time_envelope)
        except Exception:
            raise ValueError("time_envelope_invalid") from None
        artifact = KernelArtifactV01(
            abi_version=abi_version,
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            schema_version=schema_version,
            transaction_id=transaction_id,
            owner_root_id=owner_root_id,
            source_component=source_component,
            authority_class=authority_class,
            lifecycle_state=lifecycle_state,
            payload=frozen_payload,
            trace_refs=trace_refs,
            parent_refs=parent_refs,
            time_envelope=frozen_time,
        )
        errors = _kernel_artifact_errors(artifact)
        if errors:
            raise ValueError(errors[0])
        return artifact
    except ValueError as exc:
        reason = _allowed_reason(exc, _ARTIFACT_BUILDER_REASONS)
        raise ValueError(reason or "kernel_artifact_invalid") from None
    except Exception:
        raise ValueError("kernel_artifact_invalid") from None


def validate_kernel_artifact_v01(
    artifact: object,
) -> tuple[str, ...]:
    try:
        return _kernel_artifact_errors(artifact)
    except Exception:
        return ("kernel_artifact_unexpected_exception",)


def validate_kernel_artifact_bundle_v01(
    *,
    artifacts: object,
) -> tuple[str, ...]:
    try:
        if type(artifacts) is not tuple or not artifacts:
            return ("artifact_bundle_invalid",)
        if any(type(item) is not KernelArtifactV01 for item in artifacts):
            return ("artifact_bundle_invalid",)
        errors: list[str] = []
        for artifact in artifacts:
            errors.extend(_kernel_artifact_errors(artifact))
        if not all(_valid_text(item.artifact_id) for item in artifacts):
            return _dedupe(errors or ("artifact_bundle_invalid",))
        if not all(_valid_text(item.transaction_id) for item in artifacts):
            return _dedupe(errors or ("artifact_bundle_invalid",))
        if not all(
            type(item.parent_refs) is tuple
            and all(_valid_text(parent_id) for parent_id in item.parent_refs)
            for item in artifacts
        ):
            return _dedupe(errors or ("artifact_bundle_invalid",))
        artifact_ids = tuple(item.artifact_id for item in artifacts)
        if len(artifact_ids) != len(set(artifact_ids)):
            errors.append("artifact_id_duplicate")
        transactions = tuple(item.transaction_id for item in artifacts)
        if len(set(transactions)) != 1:
            errors.append("artifact_transaction_mismatch")
        known_ids = set(artifact_ids)
        edges: list[tuple[str, str]] = []
        for artifact in artifacts:
            if artifact.artifact_id in artifact.parent_refs:
                errors.append("parent_ref_self")
            if len(artifact.parent_refs) != len(set(artifact.parent_refs)):
                errors.append("parent_edge_duplicate")
            for parent_id in artifact.parent_refs:
                edge = (artifact.artifact_id, parent_id)
                if edge in edges:
                    errors.append("parent_edge_duplicate")
                edges.append(edge)
                if parent_id not in known_ids:
                    errors.append("parent_ref_unknown")
        graph_resolvable = all(parent_id in known_ids for _child, parent_id in edges)
        if graph_resolvable and _parent_graph_has_cycle(artifact_ids, tuple(edges)):
            errors.append("parent_graph_cycle")
        return _dedupe(errors)
    except Exception:
        return ("artifact_bundle_invalid",)


def kernel_artifact_to_plain_dict_v01(
    artifact: KernelArtifactV01,
) -> dict[str, object]:
    try:
        if _kernel_artifact_errors(artifact):
            raise ValueError("kernel_artifact_invalid")
        projected = _kernel_artifact_plain(artifact)
        _canonical_json_bytes_v01(projected)
        return projected
    except Exception:
        raise ValueError("kernel_artifact_invalid") from None


def kernel_artifacts_to_plain_list_v01(
    artifacts: tuple[KernelArtifactV01, ...],
) -> list[dict[str, object]]:
    try:
        if validate_kernel_artifact_bundle_v01(artifacts=artifacts):
            raise ValueError("artifact_bundle_invalid")
        projected = [_kernel_artifact_plain(item) for item in artifacts]
        _canonical_json_bytes_v01(projected)
        return projected
    except Exception:
        raise ValueError("artifact_bundle_invalid") from None


def kernel_artifact_to_canonical_ref_v01(
    artifact: KernelArtifactV01,
) -> CanonicalArtifactRefV01:
    try:
        if _kernel_artifact_errors(artifact):
            raise ValueError("kernel_artifact_invalid")
        return _build_canonical_artifact_ref_v01(
            artifact_id=artifact.artifact_id,
            artifact_type=artifact.artifact_type,
            schema_version=artifact.schema_version,
            transaction_id=artifact.transaction_id,
            owner_root_id=artifact.owner_root_id,
            authority_class=artifact.authority_class,
            lifecycle_state=artifact.lifecycle_state,
            payload=_thaw_json_value(artifact.payload),
            profile=_build_default_seal_profile_v01(),
        )
    except Exception:
        raise ValueError("canonical_artifact_ref_conversion_failed") from None


def build_causal_consumption_ref_v01(
    *,
    producer_actor_id: str,
    source_artifact_id: str,
    output_field: str,
    consumer_component: str,
    downstream_artifact_id: str,
    decision_effect: str,
    disposition: str,
    reason_code: str,
    trace_refs: tuple[str, ...],
) -> CausalConsumptionRefV01:
    try:
        causal_ref = CausalConsumptionRefV01(
            producer_actor_id=producer_actor_id,
            source_artifact_id=source_artifact_id,
            output_field=output_field,
            consumer_component=consumer_component,
            downstream_artifact_id=downstream_artifact_id,
            decision_effect=decision_effect,
            disposition=disposition,
            reason_code=reason_code,
            trace_refs=trace_refs,
        )
        errors = _causal_ref_errors(causal_ref)
        if errors:
            raise ValueError(errors[0])
        return causal_ref
    except ValueError as exc:
        reason = _allowed_reason(exc, _CAUSAL_BUILDER_REASONS)
        raise ValueError(reason or "causal_consumption_ref_invalid") from None
    except Exception:
        raise ValueError("causal_consumption_ref_invalid") from None


def validate_causal_consumption_ref_v01(
    causal_ref: object,
) -> tuple[str, ...]:
    try:
        return _causal_ref_errors(causal_ref)
    except Exception:
        return ("causal_consumption_unexpected_exception",)


def validate_causal_consumption_bundle_v01(
    *,
    artifacts: object,
    causal_refs: object,
) -> tuple[str, ...]:
    try:
        if type(artifacts) is not tuple or type(causal_refs) is not tuple:
            return ("causal_bundle_invalid",)
        if not artifacts or not causal_refs:
            return ("causal_bundle_invalid",)
        errors: list[str] = []
        artifact_errors = validate_kernel_artifact_bundle_v01(artifacts=artifacts)
        if artifact_errors:
            errors.extend(("causal_bundle_invalid", *artifact_errors))
        if any(type(item) is not KernelArtifactV01 for item in artifacts):
            return _dedupe(errors or ("causal_bundle_invalid",))
        for causal_ref in causal_refs:
            errors.extend(_causal_ref_errors(causal_ref))
        if any(type(item) is not CausalConsumptionRefV01 for item in causal_refs):
            return _dedupe(errors)
        valid_refs = tuple(
            item for item in causal_refs if not _causal_ref_errors(item)
        )
        identities = tuple(_causal_ref_identity(item) for item in valid_refs)
        if len(identities) != len(set(identities)):
            errors.append("causal_ref_duplicate")
        artifact_by_id = {
            item.artifact_id: item
            for item in artifacts
            if _valid_text(item.artifact_id)
        }
        for causal_ref in valid_refs:
            source = artifact_by_id.get(causal_ref.source_artifact_id)
            downstream = artifact_by_id.get(causal_ref.downstream_artifact_id)
            if source is None:
                errors.append("causal_source_artifact_missing")
            if downstream is None:
                errors.append("causal_downstream_artifact_missing")
            if source is None or downstream is None:
                continue
            if source.artifact_id == downstream.artifact_id:
                errors.append("causal_bundle_invalid")
            if source.transaction_id != downstream.transaction_id:
                errors.append("causal_transaction_mismatch")
            if causal_ref.consumer_component != downstream.source_component:
                errors.append("causal_consumer_mismatch")
            if source.artifact_id not in downstream.parent_refs:
                errors.append("causal_parent_binding_missing")
            try:
                _resolve_json_pointer(source.payload, causal_ref.output_field)
            except ValueError:
                errors.append("causal_output_field_missing")
        return _dedupe(errors)
    except Exception:
        return ("causal_bundle_invalid",)


def validate_causal_counterfactual_v01(
    *,
    causal_ref: object,
    baseline_source_artifact: object,
    mutated_source_artifact: object,
    baseline_downstream_artifact: object,
    mutated_downstream_artifact: object,
    baseline_authority_state: object,
    mutated_authority_state: object,
) -> tuple[str, ...]:
    try:
        if _causal_ref_errors(causal_ref):
            return ("causal_counterfactual_invalid",)
        artifacts = (
            baseline_source_artifact,
            mutated_source_artifact,
            baseline_downstream_artifact,
            mutated_downstream_artifact,
        )
        if any(_kernel_artifact_errors(item) for item in artifacts):
            return ("causal_counterfactual_invalid",)
        baseline_source, mutated_source, baseline_downstream, mutated_downstream = (
            artifacts
        )
        errors: list[str] = []
        if (
            baseline_source.artifact_id != mutated_source.artifact_id
            or baseline_source.artifact_id != causal_ref.source_artifact_id
            or _artifact_envelope_bytes(baseline_source)
            != _artifact_envelope_bytes(mutated_source)
        ):
            errors.append("causal_source_binding_mismatch")
        if (
            baseline_downstream.artifact_id != mutated_downstream.artifact_id
            or baseline_downstream.artifact_id != causal_ref.downstream_artifact_id
            or causal_ref.source_artifact_id == causal_ref.downstream_artifact_id
            or baseline_source.artifact_id == baseline_downstream.artifact_id
            or mutated_source.artifact_id == mutated_downstream.artifact_id
            or causal_ref.consumer_component
            != baseline_downstream.source_component
            or causal_ref.consumer_component
            != mutated_downstream.source_component
            or baseline_source.artifact_id not in baseline_downstream.parent_refs
            or mutated_source.artifact_id not in mutated_downstream.parent_refs
            or _artifact_envelope_bytes(baseline_downstream)
            != _artifact_envelope_bytes(mutated_downstream)
        ):
            errors.append("causal_downstream_binding_mismatch")
        transactions = tuple(item.transaction_id for item in artifacts)
        if len(set(transactions)) != 1:
            errors.append("causal_counterfactual_invalid")
        try:
            baseline_field = _resolve_json_pointer(
                baseline_source.payload, causal_ref.output_field
            )
            mutated_field = _resolve_json_pointer(
                mutated_source.payload, causal_ref.output_field
            )
        except ValueError:
            errors.append("causal_source_binding_mismatch")
            return _dedupe(errors)
        if _canonical_json_bytes_v01(baseline_field) == _canonical_json_bytes_v01(
            mutated_field
        ):
            errors.append("causal_source_mutation_missing")
        if not _payload_non_target_branches_equal(
            baseline_source.payload,
            mutated_source.payload,
            causal_ref.output_field,
        ):
            errors.append("causal_source_binding_mismatch")
        baseline_authority = _canonical_owned_json_bytes(baseline_authority_state)
        mutated_authority = _canonical_owned_json_bytes(mutated_authority_state)
        downstream_equal = _canonical_json_bytes_v01(
            _thaw_json_value(baseline_downstream.payload)
        ) == _canonical_json_bytes_v01(
            _thaw_json_value(mutated_downstream.payload)
        )
        authority_equal = baseline_authority == mutated_authority
        if causal_ref.disposition == "USED":
            if downstream_equal:
                errors.append("causal_used_influence_missing")
        elif causal_ref.disposition == "REJECTED":
            if not authority_equal:
                errors.append("causal_rejected_authority_changed")
        elif causal_ref.disposition == "IGNORED_WITH_REASON":
            if not downstream_equal:
                errors.append("causal_ignored_downstream_changed")
            if not authority_equal:
                errors.append("causal_ignored_authority_changed")
        elif causal_ref.disposition == "BLOCKED_BY_GATE":
            if not authority_equal:
                errors.append("causal_blocked_authority_changed")
        else:
            errors.append("causal_counterfactual_invalid")
        return _dedupe(errors)
    except Exception:
        return ("causal_counterfactual_invalid",)


def causal_consumption_ref_to_plain_dict_v01(
    causal_ref: CausalConsumptionRefV01,
) -> dict[str, object]:
    try:
        if _causal_ref_errors(causal_ref):
            raise ValueError("causal_consumption_ref_invalid")
        projected = _causal_ref_plain(causal_ref)
        _canonical_json_bytes_v01(projected)
        return projected
    except Exception:
        raise ValueError("causal_consumption_ref_invalid") from None


def causal_consumption_refs_to_plain_list_v01(
    causal_refs: tuple[CausalConsumptionRefV01, ...],
) -> list[dict[str, object]]:
    try:
        if type(causal_refs) is not tuple or not causal_refs:
            raise ValueError("causal_bundle_invalid")
        projected: list[dict[str, object]] = []
        identities: set[bytes] = set()
        for causal_ref in causal_refs:
            if _causal_ref_errors(causal_ref):
                raise ValueError("causal_bundle_invalid")
            identity = _causal_ref_identity(causal_ref)
            if identity in identities:
                raise ValueError("causal_bundle_invalid")
            identities.add(identity)
            projected.append(_causal_ref_plain(causal_ref))
        _canonical_json_bytes_v01(projected)
        return projected
    except Exception:
        raise ValueError("causal_bundle_invalid") from None


def _allowed_reason(error: ValueError, allowed: tuple[str, ...]) -> str | None:
    if (
        type(error) is ValueError
        and len(error.args) == 1
        and type(error.args[0]) is str
        and error.args[0] in allowed
    ):
        return error.args[0]
    return None


def _contains_surrogate(value: str) -> bool:
    return any(0xD800 <= ord(character) <= 0xDFFF for character in value)


def _valid_text(value: object) -> bool:
    return type(value) is str and bool(value) and not _contains_surrogate(value)


def _valid_text_tuple(value: object, *, allow_empty: bool) -> bool:
    return bool(
        type(value) is tuple
        and (allow_empty or value)
        and all(_valid_text(item) for item in value)
        and len(value) == len(set(value))
    )


def _dedupe(errors: object) -> tuple[str, ...]:
    return tuple(dict.fromkeys(errors))


def _abi_version_errors(value: object) -> tuple[str, ...]:
    if type(value) is not str:
        return ("abi_version_invalid",)
    match = _ABI_VERSION_PATTERN.fullmatch(value)
    if match is None:
        return ("abi_version_invalid",)
    major, _minor = match.groups()
    if major != str(KERNEL_ABI_MAJOR_VERSION):
        return ("abi_major_version_unknown",)
    if value not in SUPPORTED_ABI_VERSIONS:
        return ("abi_minor_version_unsupported",)
    return ()


def _kernel_artifact_errors(artifact: object) -> tuple[str, ...]:
    if type(artifact) is not KernelArtifactV01:
        return ("kernel_artifact_invalid",)
    errors: list[str] = list(_abi_version_errors(artifact.abi_version))
    for value, reason in (
        (artifact.artifact_id, "artifact_id_invalid"),
        (artifact.transaction_id, "transaction_id_invalid"),
        (artifact.owner_root_id, "owner_root_id_invalid"),
        (artifact.source_component, "source_component_invalid"),
    ):
        if not _valid_text(value):
            errors.append(reason)
    if type(artifact.artifact_type) is not str or artifact.artifact_type not in ARTIFACT_TYPES:
        errors.append("artifact_type_unknown")
    if type(artifact.schema_version) is not str or _SCHEMA_VERSION_PATTERN.fullmatch(
        artifact.schema_version
    ) is None:
        errors.append("schema_version_invalid")
    if type(artifact.authority_class) is not str or artifact.authority_class not in AUTHORITY_CLASSES:
        errors.append("authority_class_unknown")
    if type(artifact.lifecycle_state) is not str or artifact.lifecycle_state not in LIFECYCLE_STATES:
        errors.append("lifecycle_state_unknown")
    if not _frozen_json_valid(artifact.payload):
        errors.append("payload_invalid")
    elif _payload_has_reserved_field(artifact.payload):
        errors.append("payload_reserved_field")
    if not _valid_text_tuple(artifact.trace_refs, allow_empty=False):
        errors.append("trace_refs_invalid")
    if not _valid_text_tuple(artifact.parent_refs, allow_empty=True):
        errors.append("parent_refs_invalid")
    elif _valid_text(artifact.artifact_id) and artifact.artifact_id in artifact.parent_refs:
        errors.append("parent_refs_invalid")
    if not _time_envelope_valid(artifact.time_envelope):
        errors.append("time_envelope_invalid")
    return _dedupe(errors)


def _causal_ref_errors(causal_ref: object) -> tuple[str, ...]:
    if type(causal_ref) is not CausalConsumptionRefV01:
        return ("causal_consumption_ref_invalid",)
    errors: list[str] = []
    for value in (
        causal_ref.producer_actor_id,
        causal_ref.source_artifact_id,
        causal_ref.consumer_component,
        causal_ref.downstream_artifact_id,
        causal_ref.decision_effect,
    ):
        if not _valid_text(value):
            errors.append("causal_consumption_ref_invalid")
            break
    if not _json_pointer_valid(causal_ref.output_field):
        errors.append("causal_output_field_invalid")
    if type(causal_ref.disposition) is not str or causal_ref.disposition not in CAUSAL_DISPOSITIONS:
        errors.append("causal_disposition_unknown")
    if not _valid_text(causal_ref.reason_code):
        errors.append("causal_reason_required")
    elif type(causal_ref.disposition) is str and causal_ref.disposition in _REASON_PREFIX:
        prefix = _REASON_PREFIX[causal_ref.disposition]
        if (
            not causal_ref.reason_code.startswith(prefix)
            or not causal_ref.reason_code[len(prefix) :].strip()
        ):
            errors.append("causal_reason_disposition_mismatch")
    if not _valid_text_tuple(causal_ref.trace_refs, allow_empty=False):
        errors.append("causal_trace_refs_invalid")
    return _dedupe(errors)


def _freeze_json_value(value: object) -> object:
    frozen = _freeze_json_snapshot(value, set())
    if not _frozen_json_valid(frozen):
        raise ValueError("json_value_invalid")
    return frozen


def _freeze_json_snapshot(value: object, active: set[int]) -> object:
    if value is None or type(value) in {bool, int, float, str}:
        return value
    if type(value) in {bytes, bytearray, memoryview, set, frozenset}:
        raise ValueError("json_value_invalid")
    identity = id(value)
    if identity in active:
        raise ValueError("json_cycle_invalid")
    active.add(identity)
    try:
        if type(value) in {tuple, list}:
            return tuple(_freeze_json_snapshot(item, active) for item in value)
        if isinstance(value, _Mapping):
            rows: list[tuple[str, object]] = []
            keys: set[str] = set()
            for row in value.items():
                if type(row) is not tuple or len(row) != 2:
                    raise ValueError("json_mapping_invalid")
                key, item = row
                if type(key) is not str or _contains_surrogate(key):
                    raise ValueError("json_mapping_invalid")
                if key in keys:
                    raise ValueError("json_mapping_duplicate_key")
                keys.add(key)
                rows.append((key, _freeze_json_snapshot(item, active)))
            rows.sort(key=lambda item: item[0])
            return _FrozenJSONObject(tuple(rows))
        raise ValueError("json_value_invalid")
    finally:
        active.remove(identity)


def _frozen_json_structure_valid(value: object, active: set[int]) -> bool:
    if value is None or type(value) in {bool, int, float, str}:
        return True
    if type(value) not in {tuple, _FrozenJSONObject}:
        return False
    identity = id(value)
    if identity in active:
        return False
    active.add(identity)
    try:
        if type(value) is tuple:
            return all(_frozen_json_structure_valid(item, active) for item in value)
        if type(value.items) is not tuple:
            return False
        keys: list[str] = []
        for row in value.items:
            if type(row) is not tuple or len(row) != 2:
                return False
            key, item = row
            if type(key) is not str or _contains_surrogate(key):
                return False
            keys.append(key)
            if not _frozen_json_structure_valid(item, active):
                return False
        return keys == sorted(keys) and len(keys) == len(set(keys))
    finally:
        active.remove(identity)


def _frozen_json_valid(value: object) -> bool:
    try:
        if not _frozen_json_structure_valid(value, set()):
            return False
        _canonical_json_bytes_v01(_thaw_json_validated(value))
        return True
    except Exception:
        return False


def _thaw_json_validated(value: object) -> object:
    if type(value) is _FrozenJSONObject:
        return {key: _thaw_json_validated(item) for key, item in value.items}
    if type(value) is tuple:
        return [_thaw_json_validated(item) for item in value]
    if value is None or type(value) in {bool, int, float, str}:
        return value
    raise ValueError("frozen_json_invalid")


def _thaw_json_value(value: object) -> object:
    if not _frozen_json_valid(value):
        raise ValueError("frozen_json_invalid")
    return _thaw_json_validated(value)


def _payload_has_reserved_field(payload: object) -> bool:
    return bool(
        type(payload) is _FrozenJSONObject
        and any(key in _RESERVED_PAYLOAD_FIELDS for key, _value in payload.items)
    )


def _time_envelope_valid(value: object) -> bool:
    try:
        if type(value) is not _FrozenJSONObject:
            return False
        if tuple(key for key, _item in value.items) != _TIME_ENVELOPE_FIELDS:
            return False
        plain = _thaw_json_value(value)
        if type(plain) is not dict or set(plain) != set(_TIME_ENVELOPE_FIELDS):
            return False
        if not _aware_timestamp_valid(plain["pt_created_at"]):
            return False
        if not _aware_timestamp_valid(plain["kt_asof"]):
            return False
        if plain["et_observed_at"] is not None and not _aware_timestamp_valid(
            plain["et_observed_at"]
        ):
            return False
        if not _valid_text(plain["ct_session_anchor"]):
            return False
        if type(plain["ttl_seconds"]) is not int or plain["ttl_seconds"] < 0:
            return False
        if type(plain["freshness_class"]) is not str or plain[
            "freshness_class"
        ] not in _FRESHNESS_CLASSES:
            return False
        for key in ("valid_from", "valid_to"):
            if plain[key] is not None and not _aware_timestamp_valid(plain[key]):
                return False
        if plain["valid_from"] is not None and plain["valid_to"] is not None:
            if _parse_timestamp(plain["valid_to"]) < _parse_timestamp(
                plain["valid_from"]
            ):
                return False
        return True
    except Exception:
        return False


def _aware_timestamp_valid(value: object) -> bool:
    try:
        if (
            type(value) is not str
            or _contains_surrogate(value)
            or _AWARE_TIMESTAMP_PATTERN.fullmatch(value) is None
        ):
            return False
        parsed = _parse_timestamp(value)
        return parsed.tzinfo is not None and parsed.utcoffset() is not None
    except Exception:
        return False


def _parse_timestamp(value: str) -> _datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    return _datetime.fromisoformat(normalized)


def _parent_graph_has_cycle(
    artifact_ids: tuple[str, ...], edges: tuple[tuple[str, str], ...]
) -> bool:
    parents = {artifact_id: [] for artifact_id in artifact_ids}
    for artifact_id, parent_id in edges:
        parents[artifact_id].append(parent_id)
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(artifact_id: str) -> bool:
        if artifact_id in visiting:
            return True
        if artifact_id in visited:
            return False
        visiting.add(artifact_id)
        try:
            if any(visit(parent_id) for parent_id in parents[artifact_id]):
                return True
        finally:
            visiting.remove(artifact_id)
        visited.add(artifact_id)
        return False

    return any(visit(artifact_id) for artifact_id in artifact_ids)


def _json_pointer_valid(pointer: object) -> bool:
    try:
        if (
            type(pointer) is not str
            or _contains_surrogate(pointer)
            or not pointer.startswith("/")
        ):
            return False
        for encoded in pointer.split("/")[1:]:
            _decode_pointer_segment(encoded)
        return True
    except Exception:
        return False


def _decode_pointer_segment(encoded: str) -> str:
    output: list[str] = []
    index = 0
    while index < len(encoded):
        character = encoded[index]
        if character != "~":
            output.append(character)
            index += 1
            continue
        if index + 1 >= len(encoded) or encoded[index + 1] not in {"0", "1"}:
            raise ValueError("causal_output_field_invalid")
        output.append("~" if encoded[index + 1] == "0" else "/")
        index += 2
    return "".join(output)


def _resolve_json_pointer(payload: object, pointer: str) -> object:
    if not _json_pointer_valid(pointer):
        raise ValueError("causal_output_field_invalid")
    current = _thaw_json_value(payload)
    for encoded in pointer.split("/")[1:]:
        segment = _decode_pointer_segment(encoded)
        if type(current) is dict:
            if segment not in current:
                raise ValueError("causal_output_field_missing")
            current = current[segment]
        elif type(current) is list:
            index = _array_index(segment)
            if index is None:
                raise ValueError("causal_output_field_missing")
            if index >= len(current):
                raise ValueError("causal_output_field_missing")
            current = current[index]
        else:
            raise ValueError("causal_output_field_missing")
    return current


def _array_index(segment: str) -> int | None:
    if segment == "0":
        return 0
    if (
        not segment
        or segment[0] not in "123456789"
        or any(character not in "0123456789" for character in segment[1:])
    ):
        return None
    return int(segment)


def _artifact_envelope_bytes(artifact: KernelArtifactV01) -> bytes:
    return _canonical_json_bytes_v01(
        {
            "abi_version": artifact.abi_version,
            "artifact_id": artifact.artifact_id,
            "artifact_type": artifact.artifact_type,
            "schema_version": artifact.schema_version,
            "transaction_id": artifact.transaction_id,
            "owner_root_id": artifact.owner_root_id,
            "source_component": artifact.source_component,
            "authority_class": artifact.authority_class,
            "lifecycle_state": artifact.lifecycle_state,
            "trace_refs": list(artifact.trace_refs),
            "parent_refs": list(artifact.parent_refs),
            "time_envelope": _thaw_json_value(artifact.time_envelope),
        }
    )


def _payload_non_target_branches_equal(
    baseline_payload: object,
    mutated_payload: object,
    pointer: str,
) -> bool:
    baseline = _thaw_json_value(baseline_payload)
    mutated = _thaw_json_value(mutated_payload)
    segments = tuple(
        _decode_pointer_segment(encoded) for encoded in pointer.split("/")[1:]
    )
    return _json_non_target_branches_equal(baseline, mutated, segments)


def _json_non_target_branches_equal(
    baseline: object,
    mutated: object,
    segments: tuple[str, ...],
) -> bool:
    if not segments:
        return True
    if type(baseline) is not type(mutated):
        return False
    segment, remaining = segments[0], segments[1:]
    if type(baseline) is dict:
        if set(baseline) != set(mutated) or segment not in baseline:
            return False
        for key in baseline:
            if key == segment:
                if not _json_non_target_branches_equal(
                    baseline[key], mutated[key], remaining
                ):
                    return False
            elif _canonical_json_bytes_v01(
                baseline[key]
            ) != _canonical_json_bytes_v01(mutated[key]):
                return False
        return True
    if type(baseline) is list:
        index = _array_index(segment)
        if index is None or len(baseline) != len(mutated) or index >= len(baseline):
            return False
        for current_index, baseline_value in enumerate(baseline):
            if current_index == index:
                if not _json_non_target_branches_equal(
                    baseline_value, mutated[current_index], remaining
                ):
                    return False
            elif _canonical_json_bytes_v01(
                baseline_value
            ) != _canonical_json_bytes_v01(mutated[current_index]):
                return False
        return True
    return False


def _kernel_artifact_plain(artifact: KernelArtifactV01) -> dict[str, object]:
    return {
        "abi_version": artifact.abi_version,
        "artifact_id": artifact.artifact_id,
        "artifact_type": artifact.artifact_type,
        "schema_version": artifact.schema_version,
        "transaction_id": artifact.transaction_id,
        "owner_root_id": artifact.owner_root_id,
        "source_component": artifact.source_component,
        "authority_class": artifact.authority_class,
        "lifecycle_state": artifact.lifecycle_state,
        "payload": _thaw_json_value(artifact.payload),
        "trace_refs": list(artifact.trace_refs),
        "parent_refs": list(artifact.parent_refs),
        "time_envelope": _thaw_json_value(artifact.time_envelope),
    }


def _causal_ref_plain(causal_ref: CausalConsumptionRefV01) -> dict[str, object]:
    return {
        "producer_actor_id": causal_ref.producer_actor_id,
        "source_artifact_id": causal_ref.source_artifact_id,
        "output_field": causal_ref.output_field,
        "consumer_component": causal_ref.consumer_component,
        "downstream_artifact_id": causal_ref.downstream_artifact_id,
        "decision_effect": causal_ref.decision_effect,
        "disposition": causal_ref.disposition,
        "reason_code": causal_ref.reason_code,
        "trace_refs": list(causal_ref.trace_refs),
    }


def _causal_ref_identity(causal_ref: CausalConsumptionRefV01) -> bytes:
    return _canonical_json_bytes_v01(_causal_ref_plain(causal_ref))


def _artifact_projection_bytes(artifact: KernelArtifactV01) -> bytes:
    return _canonical_json_bytes_v01(_kernel_artifact_plain(artifact))


def _canonical_owned_json_bytes(value: object) -> bytes:
    return _canonical_json_bytes_v01(_thaw_json_value(_freeze_json_value(value)))
