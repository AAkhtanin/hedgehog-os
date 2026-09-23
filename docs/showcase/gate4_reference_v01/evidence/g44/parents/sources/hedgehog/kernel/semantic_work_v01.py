"""Pure deterministic domain-neutral SemanticWork grammar for G1-B1.

The module canonicalizes advisory contributions without invoking a provider,
LLM, network, filesystem, domain runtime, permission, Root decision,
FinalOutput, or effect. Provider output remains untrusted, contradictions and
missing evidence remain visible, and runtime-owned topology remains canonical.
This is not the Kernel ABI, CausalConsumptionRef, or Root Decision Kernel.
"""

from __future__ import annotations

from collections.abc import Mapping as _Mapping
from dataclasses import dataclass as _dataclass
from types import MappingProxyType as _MappingProxyType

from hedgehog.kernel.integrity_replay_v01 import (
    canonical_json_bytes_v01 as _canonical_json_bytes_v01,
    domain_separated_sha256_hex_v01 as _domain_separated_sha256_hex_v01,
)
from hedgehog.kernel.trust_model_v01 import (
    ComponentTrustProfileV01 as _ComponentTrustProfileV01,
    validate_component_trust_profiles_v01 as _validate_trust_profiles_v01,
)


MODULE_ID = "kernel_semantic_work_v01"
SLICE_ID = "domain_neutral_reference_kernel_gate1_g1b1"
SEMANTIC_WORK_VERSION = "v0.1"
STATUS_PASS = "PASS"
STATUS_BLOCKED_FAIL_CLOSED = "BLOCKED_FAIL_CLOSED"

CONTRIBUTION_MODE_DETERMINISTIC = "DETERMINISTIC"
CONTRIBUTION_MODE_INFORMATIONAL_REUSE = "INFORMATIONAL_REUSE"
CONTRIBUTION_MODE_CLOUD_LLM = "CLOUD_LLM"
CONTRIBUTION_MODE_LOCAL_SLM = "LOCAL_SLM"
CONTRIBUTION_MODE_FRACTAL_CHILD = "FRACTAL_CHILD"
CONTRIBUTION_MODES = (
    CONTRIBUTION_MODE_DETERMINISTIC,
    CONTRIBUTION_MODE_INFORMATIONAL_REUSE,
    CONTRIBUTION_MODE_CLOUD_LLM,
    CONTRIBUTION_MODE_LOCAL_SLM,
    CONTRIBUTION_MODE_FRACTAL_CHILD,
)

CLAIM_AUTHORITY_NONE = "NONE"
SYNTHESIS_AUTHORITY_ADVISORY = "ADVISORY_ONLY"
ROOT_REVIEW_STATE = "ROOT_REVIEW_REQUIRED"
CONFLICT_STATE = "UNRESOLVED_ROOT_REVIEW_REQUIRED"

EVIDENCE_STATE_PRESENT = "PRESENT"
EVIDENCE_STATE_MISSING = "MISSING"
EVIDENCE_STATE_REJECTED = "REJECTED"
EVIDENCE_STATES = (
    EVIDENCE_STATE_PRESENT,
    EVIDENCE_STATE_MISSING,
    EVIDENCE_STATE_REJECTED,
)

CONSTRAINT_CLASS_HARD = "HARD"
CONSTRAINT_CLASS_SOFT = "SOFT"
CONSTRAINT_CLASSES = (CONSTRAINT_CLASS_HARD, CONSTRAINT_CLASS_SOFT)

CONSTRAINT_STATE_SATISFIED = "SATISFIED"
CONSTRAINT_STATE_VIOLATED = "VIOLATED"
CONSTRAINT_STATE_UNKNOWN = "UNKNOWN"
CONSTRAINT_EVALUATION_STATES = (
    CONSTRAINT_STATE_SATISFIED,
    CONSTRAINT_STATE_VIOLATED,
    CONSTRAINT_STATE_UNKNOWN,
)

_MODE_ROLE_MAP = _MappingProxyType(
    {
        CONTRIBUTION_MODE_DETERMINISTIC: "deterministic_runtime",
        CONTRIBUTION_MODE_INFORMATIONAL_REUSE: "drs",
        CONTRIBUTION_MODE_CLOUD_LLM: "provider_llm",
        CONTRIBUTION_MODE_LOCAL_SLM: "provider_llm",
        CONTRIBUTION_MODE_FRACTAL_CHILD: "executor_fractal_child",
    }
)
_FORBIDDEN_ACTOR_ROLES = frozenset(
    {
        "root",
        "effect_firewall",
        "corridor_adapter",
        "receipt",
        "ledger",
        "crypto",
        "replay",
        "renderer_showcase",
    }
)
_CONFLICT_DOMAIN = "hedgehog.kernel.semantic_conflict.v01"
_SYNTHESIS_DOMAIN = "hedgehog.kernel.semantic_synthesis.v01"
_PACKET_DOMAIN = "hedgehog.kernel.root_review_packet.v01"
_ROOT_REVIEW_PACKET_BUILDER_REASONS = (
    "semantic_work_request_invalid",
    "semantic_work_request_context_invalid",
    "semantic_work_request_actor_ids_invalid",
    "semantic_work_request_modes_invalid",
    "semantic_work_request_subjects_invalid",
    "semantic_work_request_evidence_classes_invalid",
    "semantic_work_request_forbidden_claims_invalid",
    "runtime_topology_ref_invalid",
    "actor_contribution_invalid",
    "actor_not_permitted",
    "actor_role_invalid",
    "actor_role_trust_profile_missing",
    "contribution_mode_unknown",
    "contribution_mode_not_permitted",
    "contribution_mode_role_mismatch",
    "bounded_context_violation",
    "request_binding_mismatch",
    "claim_contract_invalid",
    "claim_subject_not_requested",
    "claim_authority_forbidden",
    "evidence_binding_invalid",
    "evidence_ref_unbound",
    "constraint_binding_invalid",
    "uncertainty_binding_invalid",
    "uncertainty_claim_ref_invalid",
    "requested_validator_invalid",
    "forbidden_claim_observed",
    "semantic_actor_authority_escalation",
)


@_dataclass(frozen=True)
class _FrozenJSONObject:
    items: tuple[tuple[str, object], ...]


@_dataclass(frozen=True)
class SemanticWorkRequestV01:
    request_id: str
    transaction_id: str
    target_root_id: str
    runtime_topology_ref: str
    bounded_context_refs: tuple[str, ...]
    permitted_actor_ids: tuple[str, ...]
    permitted_contribution_modes: tuple[str, ...]
    requested_subjects: tuple[str, ...]
    required_evidence_classes: tuple[str, ...]
    forbidden_claims: tuple[str, ...]


@_dataclass(frozen=True)
class EvidenceBindingV01:
    evidence_id: str
    evidence_ref: str
    evidence_class: str
    source_component_id: str
    provenance_ref: str
    evidence_state: str


@_dataclass(frozen=True)
class ConstraintBindingV01:
    constraint_id: str
    subject: str
    predicate: str
    object_or_value: object
    source_ref: str
    constraint_class: str
    evaluation_state: str


@_dataclass(frozen=True)
class UncertaintyBindingV01:
    uncertainty_id: str
    claim_id: str
    uncertainty_kind: str
    statement: str
    confidence_micros: int
    source_ref: str


@_dataclass(frozen=True)
class NormalizedClaimV01:
    claim_id: str
    subject: str
    predicate: str
    object_or_value: object
    time_envelope_ref: str
    provenance_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    confidence_micros: int
    source_role: str
    source_mode: str
    authority_class: str


@_dataclass(frozen=True)
class ActorContributionV01:
    contribution_id: str
    request_id: str
    actor_id: str
    actor_role: str
    contribution_mode: str
    bsep_projection_ref: str
    scope: str
    bounded_context_refs: tuple[str, ...]
    claims: tuple[NormalizedClaimV01, ...]
    evidence_bindings: tuple[EvidenceBindingV01, ...]
    constraint_bindings: tuple[ConstraintBindingV01, ...]
    uncertainty_bindings: tuple[UncertaintyBindingV01, ...]
    requested_validators: tuple[str, ...]
    forbidden_claims_observed: tuple[str, ...]


@_dataclass(frozen=True)
class ConflictSetV01:
    conflict_set_id: str
    subject: str
    predicate: str
    claim_ids: tuple[str, ...]
    conflicting_values: tuple[object, ...]
    source_modes: tuple[str, ...]
    resolution_state: str


@_dataclass(frozen=True)
class SynthesisProposalV01:
    proposal_id: str
    request_id: str
    source_contribution_ids: tuple[str, ...]
    normalized_claims: tuple[NormalizedClaimV01, ...]
    conflict_sets: tuple[ConflictSetV01, ...]
    missing_evidence_refs: tuple[str, ...]
    contribution_modes: tuple[str, ...]
    requested_validators: tuple[str, ...]
    synthesis_summary: str
    authority_class: str
    root_review_required: bool


@_dataclass(frozen=True)
class RootReviewPacketV01:
    packet_id: str
    request_id: str
    transaction_id: str
    target_root_id: str
    runtime_topology_ref: str
    synthesis_proposal: SynthesisProposalV01
    contribution_ids: tuple[str, ...]
    conflict_set_ids: tuple[str, ...]
    missing_evidence_refs: tuple[str, ...]
    required_validator_ids: tuple[str, ...]
    review_state: str
    authority_class: str
    root_decision_created: bool
    permission_created: bool
    final_output_created: bool


def build_semantic_work_request_v01(
    *,
    request_id: str,
    transaction_id: str,
    target_root_id: str,
    runtime_topology_ref: str,
    bounded_context_refs: tuple[str, ...],
    permitted_actor_ids: tuple[str, ...],
    permitted_contribution_modes: tuple[str, ...],
    requested_subjects: tuple[str, ...],
    required_evidence_classes: tuple[str, ...],
    forbidden_claims: tuple[str, ...],
) -> SemanticWorkRequestV01:
    request = SemanticWorkRequestV01(
        request_id=request_id,
        transaction_id=transaction_id,
        target_root_id=target_root_id,
        runtime_topology_ref=runtime_topology_ref,
        bounded_context_refs=bounded_context_refs,
        permitted_actor_ids=permitted_actor_ids,
        permitted_contribution_modes=permitted_contribution_modes,
        requested_subjects=requested_subjects,
        required_evidence_classes=required_evidence_classes,
        forbidden_claims=forbidden_claims,
    )
    errors = validate_semantic_work_request_v01(request)
    if errors:
        raise ValueError(errors[0]) from None
    return request


def build_evidence_binding_v01(
    *,
    evidence_id: str,
    evidence_ref: str,
    evidence_class: str,
    source_component_id: str,
    provenance_ref: str,
    evidence_state: str,
) -> EvidenceBindingV01:
    try:
        binding = EvidenceBindingV01(
            evidence_id=evidence_id,
            evidence_ref=evidence_ref,
            evidence_class=evidence_class,
            source_component_id=source_component_id,
            provenance_ref=provenance_ref,
            evidence_state=evidence_state,
        )
        if _evidence_errors(binding):
            raise ValueError("evidence_binding_invalid")
        return binding
    except Exception:
        raise ValueError("evidence_binding_invalid") from None


def build_constraint_binding_v01(
    *,
    constraint_id: str,
    subject: str,
    predicate: str,
    object_or_value: object,
    source_ref: str,
    constraint_class: str,
    evaluation_state: str,
) -> ConstraintBindingV01:
    try:
        frozen_value = _freeze_json_value(object_or_value)
        binding = ConstraintBindingV01(
            constraint_id=constraint_id,
            subject=subject,
            predicate=predicate,
            object_or_value=frozen_value,
            source_ref=source_ref,
            constraint_class=constraint_class,
            evaluation_state=evaluation_state,
        )
        if _constraint_errors(binding):
            raise ValueError("constraint_binding_invalid")
        return binding
    except Exception:
        raise ValueError("constraint_binding_invalid") from None


def build_uncertainty_binding_v01(
    *,
    uncertainty_id: str,
    claim_id: str,
    uncertainty_kind: str,
    statement: str,
    confidence_micros: int,
    source_ref: str,
) -> UncertaintyBindingV01:
    binding = UncertaintyBindingV01(
        uncertainty_id=uncertainty_id,
        claim_id=claim_id,
        uncertainty_kind=uncertainty_kind,
        statement=statement,
        confidence_micros=confidence_micros,
        source_ref=source_ref,
    )
    if _uncertainty_errors(binding):
        raise ValueError("uncertainty_binding_invalid") from None
    return binding


def build_normalized_claim_v01(
    *,
    claim_id: str,
    subject: str,
    predicate: str,
    object_or_value: object,
    time_envelope_ref: str,
    provenance_refs: tuple[str, ...],
    evidence_refs: tuple[str, ...],
    confidence_micros: int,
    source_role: str,
    source_mode: str,
) -> NormalizedClaimV01:
    try:
        claim = NormalizedClaimV01(
            claim_id=claim_id,
            subject=subject,
            predicate=predicate,
            object_or_value=_freeze_json_value(object_or_value),
            time_envelope_ref=time_envelope_ref,
            provenance_refs=provenance_refs,
            evidence_refs=evidence_refs,
            confidence_micros=confidence_micros,
            source_role=source_role,
            source_mode=source_mode,
            authority_class=CLAIM_AUTHORITY_NONE,
        )
        if _claim_errors(claim):
            raise ValueError("claim_contract_invalid")
        return claim
    except Exception:
        raise ValueError("claim_contract_invalid") from None


def build_actor_contribution_v01(
    *,
    contribution_id: str,
    request_id: str,
    actor_id: str,
    actor_role: str,
    contribution_mode: str,
    bsep_projection_ref: str,
    scope: str,
    bounded_context_refs: tuple[str, ...],
    claims: tuple[NormalizedClaimV01, ...],
    evidence_bindings: tuple[EvidenceBindingV01, ...],
    constraint_bindings: tuple[ConstraintBindingV01, ...],
    uncertainty_bindings: tuple[UncertaintyBindingV01, ...],
    requested_validators: tuple[str, ...],
    forbidden_claims_observed: tuple[str, ...],
) -> ActorContributionV01:
    try:
        contribution = ActorContributionV01(
            contribution_id=contribution_id,
            request_id=request_id,
            actor_id=actor_id,
            actor_role=actor_role,
            contribution_mode=contribution_mode,
            bsep_projection_ref=bsep_projection_ref,
            scope=scope,
            bounded_context_refs=bounded_context_refs,
            claims=claims,
            evidence_bindings=evidence_bindings,
            constraint_bindings=constraint_bindings,
            uncertainty_bindings=uncertainty_bindings,
            requested_validators=requested_validators,
            forbidden_claims_observed=forbidden_claims_observed,
        )
        errors = _contribution_contract_errors(contribution)
        if errors:
            raise ValueError(errors[0])
        return contribution
    except Exception:
        raise ValueError("actor_contribution_invalid") from None


def build_root_review_packet_from_contributions_v01(
    *,
    request: SemanticWorkRequestV01,
    contributions: tuple[ActorContributionV01, ...],
    trust_profiles: tuple[_ComponentTrustProfileV01, ...],
) -> RootReviewPacketV01:
    try:
        request_errors = validate_semantic_work_request_v01(request)
        if request_errors:
            raise ValueError(request_errors[0])
        if type(contributions) is not tuple or not contributions:
            raise ValueError("actor_contribution_invalid")
        if _validate_trust_profiles_v01(profiles=trust_profiles):
            raise ValueError("actor_role_trust_profile_missing")
        for contribution in contributions:
            errors = validate_actor_contribution_v01(
                request=request,
                contribution=contribution,
                trust_profiles=trust_profiles,
            )
            if errors:
                raise ValueError(errors[0])
        contribution_ids = tuple(item.contribution_id for item in contributions)
        if len(contribution_ids) != len(set(contribution_ids)):
            raise ValueError("actor_contribution_invalid")
        return _build_packet_from_validated(request, contributions)
    except ValueError as exc:
        reason = exc.args[0] if len(exc.args) == 1 and type(exc.args[0]) is str else None
        if reason not in _ROOT_REVIEW_PACKET_BUILDER_REASONS:
            reason = "semantic_work_unexpected_exception"
        raise ValueError(reason) from None
    except Exception:
        raise ValueError("semantic_work_unexpected_exception") from None


def validate_semantic_work_request_v01(
    request: object,
) -> tuple[str, ...]:
    try:
        return _request_errors(request)
    except Exception:
        return ("semantic_work_request_invalid",)


def validate_actor_contribution_v01(
    *,
    request: object,
    contribution: object,
    trust_profiles: object,
) -> tuple[str, ...]:
    try:
        errors: list[str] = list(_request_errors(request))
        if type(contribution) is not ActorContributionV01:
            errors.append("actor_contribution_invalid")
            return tuple(dict.fromkeys(errors))
        errors.extend(_contribution_contract_errors(contribution))
        if _validate_trust_profiles_v01(profiles=trust_profiles):
            errors.append("actor_role_trust_profile_missing")
            return tuple(dict.fromkeys(errors))
        if type(request) is not SemanticWorkRequestV01:
            return tuple(dict.fromkeys(errors))
        if contribution.request_id != request.request_id:
            errors.append("request_binding_mismatch")
        if contribution.actor_id not in request.permitted_actor_ids:
            errors.append("actor_not_permitted")
        if (
            type(contribution.contribution_mode) is not str
            or contribution.contribution_mode not in CONTRIBUTION_MODES
        ):
            errors.append("contribution_mode_unknown")
        elif contribution.contribution_mode not in request.permitted_contribution_modes:
            errors.append("contribution_mode_not_permitted")
        expected_role = (
            _MODE_ROLE_MAP.get(contribution.contribution_mode)
            if type(contribution.contribution_mode) is str
            else None
        )
        if contribution.actor_role in _FORBIDDEN_ACTOR_ROLES:
            errors.append("semantic_actor_authority_escalation")
        if expected_role is None or contribution.actor_role != expected_role:
            errors.append("contribution_mode_role_mismatch")
        profile_by_id = {profile.component_id: profile for profile in trust_profiles}
        profile = profile_by_id.get(contribution.actor_role)
        if profile is None:
            errors.append("actor_role_trust_profile_missing")
        elif any(
            (
                profile.may_create_root_decision,
                profile.may_create_permission,
                profile.may_request_effect,
                profile.may_hold_effect_handle,
            )
        ):
            errors.append("semantic_actor_authority_escalation")
        if not set(contribution.bounded_context_refs).issubset(
            request.bounded_context_refs
        ):
            errors.append("bounded_context_violation")
        for claim in contribution.claims:
            if claim.subject not in request.requested_subjects:
                errors.append("claim_subject_not_requested")
            if claim.source_role != contribution.actor_role:
                errors.append("actor_role_invalid")
            if claim.source_mode != contribution.contribution_mode:
                errors.append("contribution_mode_role_mismatch")
            if claim.authority_class != CLAIM_AUTHORITY_NONE:
                errors.append("claim_authority_forbidden")
        if contribution.forbidden_claims_observed:
            errors.append("forbidden_claim_observed")
        return tuple(dict.fromkeys(errors))
    except Exception:
        return ("actor_contribution_invalid",)


def validate_root_review_packet_v01(
    *,
    request: object,
    contributions: object,
    packet: object,
    trust_profiles: object,
) -> tuple[str, ...]:
    try:
        errors: list[str] = list(_request_errors(request))
        if type(contributions) is not tuple or not contributions:
            errors.append("contribution_set_mismatch")
            return tuple(dict.fromkeys(errors))
        contribution_ids = tuple(
            contribution.contribution_id
            for contribution in contributions
            if type(contribution) is ActorContributionV01
        )
        if len(contribution_ids) != len(contributions) or len(
            contribution_ids
        ) != len(set(contribution_ids)):
            errors.append("contribution_set_mismatch")
        if _validate_trust_profiles_v01(profiles=trust_profiles):
            errors.append("actor_role_trust_profile_missing")
        for contribution in contributions:
            errors.extend(
                validate_actor_contribution_v01(
                    request=request,
                    contribution=contribution,
                    trust_profiles=trust_profiles,
                )
            )
        if errors:
            return tuple(dict.fromkeys(errors))
        if type(packet) is not RootReviewPacketV01:
            return ("root_review_packet_invalid",)
        proposal = packet.synthesis_proposal
        if not _synthesis_valid(proposal):
            errors.append("synthesis_proposal_invalid")
        if not _packet_structurally_valid(packet):
            errors.append("root_review_packet_invalid")
        expected = _build_packet_from_validated(request, contributions)
        expected_proposal = expected.synthesis_proposal
        if type(proposal) is not SynthesisProposalV01:
            return ("synthesis_proposal_invalid",)
        if proposal.proposal_id != expected_proposal.proposal_id:
            errors.append("synthesis_proposal_id_mismatch")
        if proposal.request_id != expected_proposal.request_id:
            errors.append("synthesis_proposal_invalid")
        if proposal.source_contribution_ids != expected_proposal.source_contribution_ids:
            errors.append("contribution_set_mismatch")
        if not _canonical_claim_sequences_equal(
            proposal.normalized_claims,
            expected_proposal.normalized_claims,
        ):
            errors.append("normalized_claim_set_mismatch")
        if not _canonical_conflict_sequences_equal(
            proposal.conflict_sets,
            expected_proposal.conflict_sets,
        ):
            errors.append("conflict_set_mismatch")
        if proposal.missing_evidence_refs != expected_proposal.missing_evidence_refs:
            errors.append("missing_evidence_set_mismatch")
        if proposal.contribution_modes != expected_proposal.contribution_modes:
            errors.append("contribution_mode_set_mismatch")
        if proposal.requested_validators != expected_proposal.requested_validators:
            errors.append("validator_set_mismatch")
        if (
            proposal.synthesis_summary != expected_proposal.synthesis_summary
            or not proposal.root_review_required
        ):
            errors.append("synthesis_proposal_invalid")
        if proposal.authority_class != SYNTHESIS_AUTHORITY_ADVISORY:
            errors.append("semantic_authority_class_invalid")
        if packet.packet_id != expected.packet_id:
            errors.append("root_review_packet_id_mismatch")
        if packet.contribution_ids != expected.contribution_ids:
            errors.append("contribution_set_mismatch")
        if packet.conflict_set_ids != expected.conflict_set_ids:
            errors.append("conflict_set_mismatch")
        if packet.missing_evidence_refs != expected.missing_evidence_refs:
            errors.append("missing_evidence_set_mismatch")
        if packet.required_validator_ids != expected.required_validator_ids:
            errors.append("validator_set_mismatch")
        if (
            packet.request_id != request.request_id
            or packet.transaction_id != request.transaction_id
            or packet.target_root_id != request.target_root_id
        ):
            errors.append("root_review_packet_invalid")
        if packet.runtime_topology_ref != request.runtime_topology_ref:
            errors.append("runtime_topology_binding_mismatch")
        if packet.review_state != ROOT_REVIEW_STATE:
            errors.append("root_review_state_invalid")
        if packet.authority_class != SYNTHESIS_AUTHORITY_ADVISORY:
            errors.append("semantic_authority_class_invalid")
        if packet.root_decision_created:
            errors.append("root_decision_creation_forbidden")
        if packet.permission_created:
            errors.append("permission_creation_forbidden")
        if packet.final_output_created:
            errors.append("final_output_creation_forbidden")
        return tuple(dict.fromkeys(errors))
    except Exception:
        return ("semantic_work_unexpected_exception",)


def semantic_work_to_plain_dict_v01(
    value: object,
) -> dict[str, object]:
    try:
        projected = _semantic_projection(value)
        _canonical_json_bytes_v01(projected)
        return projected
    except Exception:
        raise ValueError("semantic_work_projection_invalid") from None


def _valid_text(value: object) -> bool:
    return bool(
        type(value) is str
        and value
        and not any(0xD800 <= ord(character) <= 0xDFFF for character in value)
    )


def _valid_text_tuple(value: object, *, allow_empty: bool = False) -> bool:
    return bool(
        type(value) is tuple
        and (allow_empty or bool(value))
        and all(_valid_text(item) for item in value)
        and len(value) == len(set(value))
    )


def _valid_confidence(value: object) -> bool:
    return type(value) is int and 0 <= value <= 1_000_000


def _valid_sha256(value: object) -> bool:
    return bool(
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _freeze_json_value(value: object) -> object:
    frozen = _freeze_json_snapshot(value, set())
    if not _frozen_json_valid(frozen):
        raise ValueError("json_value_invalid")
    return frozen


def _freeze_json_snapshot(value: object, active: set[int]) -> object:
    if value is None or type(value) in {bool, int, float, str}:
        return value
    identity = id(value)
    if identity in active:
        raise ValueError("json_cycle_invalid")
    active.add(identity)
    try:
        if type(value) in {tuple, list}:
            return tuple(_freeze_json_snapshot(item, active) for item in value)
        if isinstance(value, _Mapping):
            frozen_rows: list[tuple[str, object]] = []
            observed_keys: set[str] = set()
            rows = value.items()
            for row in rows:
                if type(row) is not tuple or len(row) != 2:
                    raise ValueError("json_mapping_invalid")
                key, item = row
                if type(key) is not str:
                    raise ValueError("json_mapping_invalid")
                if key in observed_keys:
                    raise ValueError("json_mapping_duplicate_key")
                observed_keys.add(key)
                frozen_rows.append((key, _freeze_json_snapshot(item, active)))
            frozen_rows.sort(key=lambda row: row[0])
            return _FrozenJSONObject(tuple(frozen_rows))
        raise ValueError("json_value_invalid")
    finally:
        active.remove(identity)


def _thaw_json_value(value: object) -> object:
    if not _frozen_json_structure_valid(value, set()):
        raise ValueError("frozen_json_invalid")
    thawed = _thaw_json_validated(value)
    _canonical_json_bytes_v01(thawed)
    return thawed


def _thaw_json_validated(value: object) -> object:
    if type(value) is _FrozenJSONObject:
        return {key: _thaw_json_validated(item) for key, item in value.items}
    if type(value) is tuple:
        return [_thaw_json_validated(item) for item in value]
    if value is None or type(value) in {bool, int, float, str}:
        return value
    raise ValueError("frozen_json_invalid")


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
            if type(key) is not str:
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
        thawed = _thaw_json_validated(value)
        _canonical_json_bytes_v01(thawed)
        return True
    except Exception:
        return False


def _request_errors(request: object) -> tuple[str, ...]:
    if type(request) is not SemanticWorkRequestV01:
        return ("semantic_work_request_invalid",)
    errors: list[str] = []
    if not all(
        _valid_text(value)
        for value in (request.request_id, request.transaction_id, request.target_root_id)
    ):
        errors.append("semantic_work_request_invalid")
    if not _valid_text(request.runtime_topology_ref):
        errors.append("runtime_topology_ref_invalid")
    tuple_checks = (
        (
            request.bounded_context_refs,
            "semantic_work_request_context_invalid",
        ),
        (
            request.permitted_actor_ids,
            "semantic_work_request_actor_ids_invalid",
        ),
        (
            request.requested_subjects,
            "semantic_work_request_subjects_invalid",
        ),
        (
            request.required_evidence_classes,
            "semantic_work_request_evidence_classes_invalid",
        ),
        (
            request.forbidden_claims,
            "semantic_work_request_forbidden_claims_invalid",
        ),
    )
    for value, reason in tuple_checks:
        if not _valid_text_tuple(value):
            errors.append(reason)
    modes = request.permitted_contribution_modes
    if (
        not _valid_text_tuple(modes)
        or any(mode not in CONTRIBUTION_MODES for mode in modes)
        or tuple(mode for mode in CONTRIBUTION_MODES if mode in modes) != modes
    ):
        errors.append("semantic_work_request_modes_invalid")
    return tuple(dict.fromkeys(errors))


def _evidence_errors(binding: object) -> tuple[str, ...]:
    if type(binding) is not EvidenceBindingV01:
        return ("evidence_binding_invalid",)
    if not all(
        _valid_text(value)
        for value in (
            binding.evidence_id,
            binding.evidence_ref,
            binding.evidence_class,
            binding.source_component_id,
            binding.provenance_ref,
        )
    ) or type(binding.evidence_state) is not str or binding.evidence_state not in EVIDENCE_STATES:
        return ("evidence_binding_invalid",)
    return ()


def _constraint_errors(binding: object) -> tuple[str, ...]:
    if type(binding) is not ConstraintBindingV01:
        return ("constraint_binding_invalid",)
    if not all(
        _valid_text(value)
        for value in (
            binding.constraint_id,
            binding.subject,
            binding.predicate,
            binding.source_ref,
        )
    ):
        return ("constraint_binding_invalid",)
    if (
        type(binding.constraint_class) is not str
        or binding.constraint_class not in CONSTRAINT_CLASSES
        or type(binding.evaluation_state) is not str
        or binding.evaluation_state not in CONSTRAINT_EVALUATION_STATES
        or not _frozen_json_valid(binding.object_or_value)
    ):
        return ("constraint_binding_invalid",)
    return ()


def _uncertainty_errors(binding: object) -> tuple[str, ...]:
    if type(binding) is not UncertaintyBindingV01:
        return ("uncertainty_binding_invalid",)
    if not all(
        _valid_text(value)
        for value in (
            binding.uncertainty_id,
            binding.claim_id,
            binding.uncertainty_kind,
            binding.statement,
            binding.source_ref,
        )
    ) or not _valid_confidence(binding.confidence_micros):
        return ("uncertainty_binding_invalid",)
    return ()


def _claim_errors(claim: object) -> tuple[str, ...]:
    if type(claim) is not NormalizedClaimV01:
        return ("claim_contract_invalid",)
    if not all(
        _valid_text(value)
        for value in (
            claim.claim_id,
            claim.subject,
            claim.predicate,
            claim.time_envelope_ref,
            claim.source_role,
            claim.source_mode,
            claim.authority_class,
        )
    ):
        return ("claim_contract_invalid",)
    if (
        not _valid_text_tuple(claim.provenance_refs)
        or not _valid_text_tuple(claim.evidence_refs)
        or not _valid_confidence(claim.confidence_micros)
        or claim.source_mode not in CONTRIBUTION_MODES
        or claim.authority_class != CLAIM_AUTHORITY_NONE
        or not _frozen_json_valid(claim.object_or_value)
    ):
        return ("claim_contract_invalid",)
    return ()


def _canonical_claim_bytes(claim: object) -> bytes:
    if _claim_errors(claim):
        raise ValueError("claim_contract_invalid")
    return _canonical_json_bytes_v01(_claim_plain(claim))


def _contribution_contract_errors(
    contribution: object,
) -> tuple[str, ...]:
    if type(contribution) is not ActorContributionV01:
        return ("actor_contribution_invalid",)
    errors: list[str] = []
    if not all(
        _valid_text(value)
        for value in (
            contribution.contribution_id,
            contribution.request_id,
            contribution.actor_id,
            contribution.actor_role,
            contribution.contribution_mode,
            contribution.bsep_projection_ref,
            contribution.scope,
        )
    ):
        errors.append("actor_contribution_invalid")
    if (
        type(contribution.contribution_mode) is not str
        or contribution.contribution_mode not in CONTRIBUTION_MODES
    ):
        errors.append("contribution_mode_unknown")
    elif contribution.actor_role != _MODE_ROLE_MAP[contribution.contribution_mode]:
        errors.append("contribution_mode_role_mismatch")
    if not _valid_text_tuple(contribution.bounded_context_refs):
        errors.append("bounded_context_violation")
    nested_checks = (
        (contribution.claims, NormalizedClaimV01, False, "claim_contract_invalid"),
        (
            contribution.evidence_bindings,
            EvidenceBindingV01,
            False,
            "evidence_binding_invalid",
        ),
        (
            contribution.constraint_bindings,
            ConstraintBindingV01,
            True,
            "constraint_binding_invalid",
        ),
        (
            contribution.uncertainty_bindings,
            UncertaintyBindingV01,
            True,
            "uncertainty_binding_invalid",
        ),
    )
    for value, expected_type, allow_empty, reason in nested_checks:
        if type(value) is not tuple or (not allow_empty and not value) or any(
            type(item) is not expected_type for item in value
        ):
            errors.append(reason)
    if type(contribution.claims) is tuple:
        for claim in contribution.claims:
            errors.extend(_claim_errors(claim))
            if type(claim) is NormalizedClaimV01:
                if claim.source_role != contribution.actor_role:
                    errors.append("actor_role_invalid")
                if claim.source_mode != contribution.contribution_mode:
                    errors.append("contribution_mode_role_mismatch")
    if type(contribution.evidence_bindings) is tuple:
        for binding in contribution.evidence_bindings:
            errors.extend(_evidence_errors(binding))
    if type(contribution.constraint_bindings) is tuple:
        for binding in contribution.constraint_bindings:
            errors.extend(_constraint_errors(binding))
    if type(contribution.uncertainty_bindings) is tuple:
        for binding in contribution.uncertainty_bindings:
            errors.extend(_uncertainty_errors(binding))
    if not _valid_text_tuple(contribution.requested_validators, allow_empty=True):
        errors.append("requested_validator_invalid")
    if not _valid_text_tuple(
        contribution.forbidden_claims_observed, allow_empty=True
    ):
        errors.append("actor_contribution_invalid")
    if contribution.forbidden_claims_observed:
        errors.append("forbidden_claim_observed")
    if type(contribution.evidence_bindings) is tuple:
        evidence_ids = tuple(item.evidence_id for item in contribution.evidence_bindings)
        if len(evidence_ids) != len(set(evidence_ids)):
            errors.append("evidence_binding_invalid")
        evidence_by_id = {
            item.evidence_id: item for item in contribution.evidence_bindings
        }
        if type(contribution.claims) is tuple:
            for claim in contribution.claims:
                if type(claim) is not NormalizedClaimV01:
                    continue
                for evidence_id in claim.evidence_refs:
                    binding = evidence_by_id.get(evidence_id)
                    if binding is None or binding.evidence_state == EVIDENCE_STATE_REJECTED:
                        errors.append("evidence_ref_unbound")
    for values, reason in (
        (contribution.constraint_bindings, "constraint_binding_invalid"),
        (contribution.uncertainty_bindings, "uncertainty_binding_invalid"),
    ):
        if type(values) is tuple:
            ids = tuple(
                item.constraint_id
                if type(item) is ConstraintBindingV01
                else item.uncertainty_id
                for item in values
            )
            if len(ids) != len(set(ids)):
                errors.append(reason)
    if type(contribution.uncertainty_bindings) is tuple and type(
        contribution.claims
    ) is tuple:
        claim_ids = {item.claim_id for item in contribution.claims}
        if any(
            item.claim_id not in claim_ids
            for item in contribution.uncertainty_bindings
            if type(item) is UncertaintyBindingV01
        ):
            errors.append("uncertainty_claim_ref_invalid")
    return tuple(dict.fromkeys(errors))


def _build_packet_from_validated(
    request: SemanticWorkRequestV01,
    contributions: tuple[ActorContributionV01, ...],
) -> RootReviewPacketV01:
    claims: list[NormalizedClaimV01] = []
    claim_identity_by_id: dict[str, bytes] = {}
    observed_claim_identities: set[bytes] = set()
    for contribution in contributions:
        for claim in contribution.claims:
            identity = _canonical_claim_bytes(claim)
            existing_identity = claim_identity_by_id.get(claim.claim_id)
            if existing_identity is not None and existing_identity != identity:
                raise ValueError("claim_contract_invalid")
            if existing_identity is None:
                claim_identity_by_id[claim.claim_id] = identity
            if identity not in observed_claim_identities:
                observed_claim_identities.add(identity)
                claims.append(claim)
    normalized_claims = tuple(claims)
    conflict_sets = _build_conflict_sets(normalized_claims)
    missing_refs: list[str] = []
    validators: list[str] = []
    for contribution in contributions:
        for binding in contribution.evidence_bindings:
            if (
                binding.evidence_state == EVIDENCE_STATE_MISSING
                and binding.evidence_ref not in missing_refs
            ):
                missing_refs.append(binding.evidence_ref)
        for validator in contribution.requested_validators:
            if validator not in validators:
                validators.append(validator)
    modes = tuple(
        mode
        for mode in CONTRIBUTION_MODES
        if any(item.contribution_mode == mode for item in contributions)
    )
    if conflict_sets and missing_refs:
        summary = "advisory_claims_with_visible_conflicts_and_missing_evidence"
    elif conflict_sets:
        summary = "advisory_claims_with_visible_conflicts"
    elif missing_refs:
        summary = "advisory_claims_with_missing_evidence"
    else:
        summary = "advisory_claims_ready_for_root_review"
    proposal_without_id = {
        "request_id": request.request_id,
        "source_contribution_ids": [item.contribution_id for item in contributions],
        "normalized_claims": [_claim_plain(item) for item in normalized_claims],
        "conflict_sets": [_conflict_plain(item) for item in conflict_sets],
        "missing_evidence_refs": list(missing_refs),
        "contribution_modes": list(modes),
        "requested_validators": list(validators),
        "synthesis_summary": summary,
        "authority_class": SYNTHESIS_AUTHORITY_ADVISORY,
        "root_review_required": True,
    }
    proposal_id = _domain_separated_sha256_hex_v01(
        domain=_SYNTHESIS_DOMAIN,
        payload=_canonical_json_bytes_v01(proposal_without_id),
    )
    proposal = SynthesisProposalV01(
        proposal_id=proposal_id,
        request_id=request.request_id,
        source_contribution_ids=tuple(item.contribution_id for item in contributions),
        normalized_claims=normalized_claims,
        conflict_sets=conflict_sets,
        missing_evidence_refs=tuple(missing_refs),
        contribution_modes=modes,
        requested_validators=tuple(validators),
        synthesis_summary=summary,
        authority_class=SYNTHESIS_AUTHORITY_ADVISORY,
        root_review_required=True,
    )
    packet_without_id = {
        "request_id": request.request_id,
        "transaction_id": request.transaction_id,
        "target_root_id": request.target_root_id,
        "runtime_topology_ref": request.runtime_topology_ref,
        "synthesis_proposal": _synthesis_plain(proposal),
        "contribution_ids": [item.contribution_id for item in contributions],
        "conflict_set_ids": [item.conflict_set_id for item in conflict_sets],
        "missing_evidence_refs": list(missing_refs),
        "required_validator_ids": list(validators),
        "review_state": ROOT_REVIEW_STATE,
        "authority_class": SYNTHESIS_AUTHORITY_ADVISORY,
        "root_decision_created": False,
        "permission_created": False,
        "final_output_created": False,
    }
    packet_id = _domain_separated_sha256_hex_v01(
        domain=_PACKET_DOMAIN,
        payload=_canonical_json_bytes_v01(packet_without_id),
    )
    return RootReviewPacketV01(
        packet_id=packet_id,
        request_id=request.request_id,
        transaction_id=request.transaction_id,
        target_root_id=request.target_root_id,
        runtime_topology_ref=request.runtime_topology_ref,
        synthesis_proposal=proposal,
        contribution_ids=tuple(item.contribution_id for item in contributions),
        conflict_set_ids=tuple(item.conflict_set_id for item in conflict_sets),
        missing_evidence_refs=tuple(missing_refs),
        required_validator_ids=tuple(validators),
        review_state=ROOT_REVIEW_STATE,
        authority_class=SYNTHESIS_AUTHORITY_ADVISORY,
        root_decision_created=False,
        permission_created=False,
        final_output_created=False,
    )


def _build_conflict_sets(
    claims: tuple[NormalizedClaimV01, ...],
) -> tuple[ConflictSetV01, ...]:
    groups: dict[tuple[str, str, str], list[NormalizedClaimV01]] = {}
    for claim in claims:
        key = (claim.subject, claim.predicate, claim.time_envelope_ref)
        groups.setdefault(key, []).append(claim)
    conflicts: list[ConflictSetV01] = []
    for (subject, predicate, _time_ref), grouped in groups.items():
        value_bytes = tuple(
            _canonical_json_bytes_v01(_thaw_json_value(item.object_or_value))
            for item in grouped
        )
        if len(set(value_bytes)) < 2:
            continue
        claim_ids = tuple(item.claim_id for item in grouped)
        conflicting_values = tuple(item.object_or_value for item in grouped)
        source_modes = tuple(item.source_mode for item in grouped)
        material = _conflict_hash_material(
            subject=subject,
            predicate=predicate,
            claim_ids=claim_ids,
            conflicting_values=conflicting_values,
            source_modes=source_modes,
            resolution_state=CONFLICT_STATE,
        )
        conflict_id = _domain_separated_sha256_hex_v01(
            domain=_CONFLICT_DOMAIN,
            payload=_canonical_json_bytes_v01(material),
        )
        conflicts.append(
            ConflictSetV01(
                conflict_set_id=conflict_id,
                subject=subject,
                predicate=predicate,
                claim_ids=claim_ids,
                conflicting_values=conflicting_values,
                source_modes=source_modes,
                resolution_state=CONFLICT_STATE,
            )
        )
    return tuple(conflicts)


def _conflict_hash_material(
    *,
    subject: str,
    predicate: str,
    claim_ids: tuple[str, ...],
    conflicting_values: tuple[object, ...],
    source_modes: tuple[str, ...],
    resolution_state: str,
) -> dict[str, object]:
    return {
        "subject": subject,
        "predicate": predicate,
        "claim_ids": list(claim_ids),
        "conflicting_values": [
            _thaw_json_value(item) for item in conflicting_values
        ],
        "source_modes": list(source_modes),
        "resolution_state": resolution_state,
    }


def _conflict_valid(conflict: object) -> bool:
    if type(conflict) is not ConflictSetV01:
        return False
    if not all(_valid_text(value) for value in (conflict.subject, conflict.predicate)):
        return False
    if (
        not _valid_sha256(conflict.conflict_set_id)
        or type(conflict.resolution_state) is not str
        or conflict.resolution_state != CONFLICT_STATE
        or not _valid_text_tuple(conflict.claim_ids)
        or type(conflict.conflicting_values) is not tuple
        or len(conflict.conflicting_values) != len(conflict.claim_ids)
        or type(conflict.source_modes) is not tuple
        or not conflict.source_modes
        or any(
            type(mode) is not str or mode not in CONTRIBUTION_MODES
            for mode in conflict.source_modes
        )
        or len(conflict.source_modes) != len(conflict.claim_ids)
        or any(not _frozen_json_valid(value) for value in conflict.conflicting_values)
    ):
        return False
    value_bytes = tuple(
        _canonical_json_bytes_v01(_thaw_json_value(item))
        for item in conflict.conflicting_values
    )
    if len(set(value_bytes)) < 2:
        return False
    material = _conflict_hash_material(
        subject=conflict.subject,
        predicate=conflict.predicate,
        claim_ids=conflict.claim_ids,
        conflicting_values=conflict.conflicting_values,
        source_modes=conflict.source_modes,
        resolution_state=conflict.resolution_state,
    )
    expected = _domain_separated_sha256_hex_v01(
        domain=_CONFLICT_DOMAIN,
        payload=_canonical_json_bytes_v01(material),
    )
    return conflict.conflict_set_id == expected


def _canonical_conflict_bytes(conflict: object) -> bytes:
    if not _conflict_valid(conflict):
        raise ValueError("conflict_set_invalid")
    return _canonical_json_bytes_v01(_conflict_plain(conflict))


def _synthesis_valid(proposal: object) -> bool:
    if type(proposal) is not SynthesisProposalV01:
        return False
    if not all(_valid_text(value) for value in (proposal.proposal_id, proposal.request_id)):
        return False
    claim_identities = tuple(
        _canonical_claim_bytes(item) for item in proposal.normalized_claims
    ) if type(proposal.normalized_claims) is tuple and all(
        not _claim_errors(item) for item in proposal.normalized_claims
    ) else ()
    if (
        not _valid_text_tuple(proposal.source_contribution_ids)
        or type(proposal.normalized_claims) is not tuple
        or not proposal.normalized_claims
        or any(_claim_errors(item) for item in proposal.normalized_claims)
        or len({item.claim_id for item in proposal.normalized_claims})
        != len(proposal.normalized_claims)
        or len(set(claim_identities)) != len(proposal.normalized_claims)
        or type(proposal.conflict_sets) is not tuple
        or any(not _conflict_valid(item) for item in proposal.conflict_sets)
        or not _canonical_conflict_sequences_equal(
            proposal.conflict_sets,
            _build_conflict_sets(proposal.normalized_claims),
        )
        or not _valid_text_tuple(proposal.missing_evidence_refs, allow_empty=True)
        or not _valid_text_tuple(proposal.contribution_modes)
        or tuple(mode for mode in CONTRIBUTION_MODES if mode in proposal.contribution_modes)
        != proposal.contribution_modes
        or not _valid_text_tuple(proposal.requested_validators, allow_empty=True)
        or type(proposal.synthesis_summary) is not str
        or proposal.synthesis_summary
        not in {
            "advisory_claims_ready_for_root_review",
            "advisory_claims_with_visible_conflicts",
            "advisory_claims_with_missing_evidence",
            "advisory_claims_with_visible_conflicts_and_missing_evidence",
        }
        or type(proposal.authority_class) is not str
        or proposal.authority_class != SYNTHESIS_AUTHORITY_ADVISORY
        or proposal.root_review_required is not True
    ):
        return False
    expected_summary = (
        "advisory_claims_with_visible_conflicts_and_missing_evidence"
        if proposal.conflict_sets and proposal.missing_evidence_refs
        else "advisory_claims_with_visible_conflicts"
        if proposal.conflict_sets
        else "advisory_claims_with_missing_evidence"
        if proposal.missing_evidence_refs
        else "advisory_claims_ready_for_root_review"
    )
    if proposal.synthesis_summary != expected_summary:
        return False
    material = _synthesis_plain(proposal)
    material.pop("proposal_id")
    expected = _domain_separated_sha256_hex_v01(
        domain=_SYNTHESIS_DOMAIN,
        payload=_canonical_json_bytes_v01(material),
    )
    return proposal.proposal_id == expected


def _packet_structurally_valid(packet: object) -> bool:
    if type(packet) is not RootReviewPacketV01 or not _synthesis_valid(
        packet.synthesis_proposal
    ):
        return False
    if not all(
        _valid_text(value)
        for value in (
            packet.packet_id,
            packet.request_id,
            packet.transaction_id,
            packet.target_root_id,
            packet.runtime_topology_ref,
        )
    ):
        return False
    if (
        not _valid_text_tuple(packet.contribution_ids)
        or not _valid_text_tuple(packet.conflict_set_ids, allow_empty=True)
        or not _valid_text_tuple(packet.missing_evidence_refs, allow_empty=True)
        or not _valid_text_tuple(packet.required_validator_ids, allow_empty=True)
        or type(packet.review_state) is not str
        or packet.review_state != ROOT_REVIEW_STATE
        or type(packet.authority_class) is not str
        or packet.authority_class != SYNTHESIS_AUTHORITY_ADVISORY
        or packet.root_decision_created is not False
        or packet.permission_created is not False
        or packet.final_output_created is not False
        or packet.contribution_ids
        != packet.synthesis_proposal.source_contribution_ids
        or packet.request_id != packet.synthesis_proposal.request_id
        or packet.conflict_set_ids
        != tuple(item.conflict_set_id for item in packet.synthesis_proposal.conflict_sets)
        or packet.missing_evidence_refs
        != packet.synthesis_proposal.missing_evidence_refs
        or packet.required_validator_ids
        != packet.synthesis_proposal.requested_validators
    ):
        return False
    material = _packet_plain(packet)
    material.pop("packet_id")
    expected = _domain_separated_sha256_hex_v01(
        domain=_PACKET_DOMAIN,
        payload=_canonical_json_bytes_v01(material),
    )
    return packet.packet_id == expected


def _canonical_claim_sequences_equal(left: object, right: object) -> bool:
    try:
        return bool(
            type(left) is tuple
            and type(right) is tuple
            and tuple(_canonical_claim_bytes(item) for item in left)
            == tuple(_canonical_claim_bytes(item) for item in right)
        )
    except Exception:
        return False


def _canonical_conflict_sequences_equal(left: object, right: object) -> bool:
    try:
        return bool(
            type(left) is tuple
            and type(right) is tuple
            and tuple(_canonical_conflict_bytes(item) for item in left)
            == tuple(_canonical_conflict_bytes(item) for item in right)
        )
    except Exception:
        return False


def _semantic_projection(value: object) -> dict[str, object]:
    if type(value) is SemanticWorkRequestV01 and not _request_errors(value):
        return _request_plain(value)
    if type(value) is EvidenceBindingV01 and not _evidence_errors(value):
        return _evidence_plain(value)
    if type(value) is ConstraintBindingV01 and not _constraint_errors(value):
        return _constraint_plain(value)
    if type(value) is UncertaintyBindingV01 and not _uncertainty_errors(value):
        return _uncertainty_plain(value)
    if type(value) is NormalizedClaimV01 and not _claim_errors(value):
        return _claim_plain(value)
    if type(value) is ActorContributionV01 and not _contribution_contract_errors(value):
        return _contribution_plain(value)
    if type(value) is ConflictSetV01 and _conflict_valid(value):
        return _conflict_plain(value)
    if type(value) is SynthesisProposalV01 and _synthesis_valid(value):
        return _synthesis_plain(value)
    if type(value) is RootReviewPacketV01 and _packet_structurally_valid(value):
        return _packet_plain(value)
    raise ValueError("semantic_work_projection_invalid")


def _request_plain(value: SemanticWorkRequestV01) -> dict[str, object]:
    return {
        "request_id": value.request_id,
        "transaction_id": value.transaction_id,
        "target_root_id": value.target_root_id,
        "runtime_topology_ref": value.runtime_topology_ref,
        "bounded_context_refs": list(value.bounded_context_refs),
        "permitted_actor_ids": list(value.permitted_actor_ids),
        "permitted_contribution_modes": list(value.permitted_contribution_modes),
        "requested_subjects": list(value.requested_subjects),
        "required_evidence_classes": list(value.required_evidence_classes),
        "forbidden_claims": list(value.forbidden_claims),
    }


def _evidence_plain(value: EvidenceBindingV01) -> dict[str, object]:
    return {
        "evidence_id": value.evidence_id,
        "evidence_ref": value.evidence_ref,
        "evidence_class": value.evidence_class,
        "source_component_id": value.source_component_id,
        "provenance_ref": value.provenance_ref,
        "evidence_state": value.evidence_state,
    }


def _constraint_plain(value: ConstraintBindingV01) -> dict[str, object]:
    return {
        "constraint_id": value.constraint_id,
        "subject": value.subject,
        "predicate": value.predicate,
        "object_or_value": _thaw_json_value(value.object_or_value),
        "source_ref": value.source_ref,
        "constraint_class": value.constraint_class,
        "evaluation_state": value.evaluation_state,
    }


def _uncertainty_plain(value: UncertaintyBindingV01) -> dict[str, object]:
    return {
        "uncertainty_id": value.uncertainty_id,
        "claim_id": value.claim_id,
        "uncertainty_kind": value.uncertainty_kind,
        "statement": value.statement,
        "confidence_micros": value.confidence_micros,
        "source_ref": value.source_ref,
    }


def _claim_plain(value: NormalizedClaimV01) -> dict[str, object]:
    return {
        "claim_id": value.claim_id,
        "subject": value.subject,
        "predicate": value.predicate,
        "object_or_value": _thaw_json_value(value.object_or_value),
        "time_envelope_ref": value.time_envelope_ref,
        "provenance_refs": list(value.provenance_refs),
        "evidence_refs": list(value.evidence_refs),
        "confidence_micros": value.confidence_micros,
        "source_role": value.source_role,
        "source_mode": value.source_mode,
        "authority_class": value.authority_class,
    }


def _contribution_plain(value: ActorContributionV01) -> dict[str, object]:
    return {
        "contribution_id": value.contribution_id,
        "request_id": value.request_id,
        "actor_id": value.actor_id,
        "actor_role": value.actor_role,
        "contribution_mode": value.contribution_mode,
        "bsep_projection_ref": value.bsep_projection_ref,
        "scope": value.scope,
        "bounded_context_refs": list(value.bounded_context_refs),
        "claims": [_claim_plain(item) for item in value.claims],
        "evidence_bindings": [_evidence_plain(item) for item in value.evidence_bindings],
        "constraint_bindings": [
            _constraint_plain(item) for item in value.constraint_bindings
        ],
        "uncertainty_bindings": [
            _uncertainty_plain(item) for item in value.uncertainty_bindings
        ],
        "requested_validators": list(value.requested_validators),
        "forbidden_claims_observed": list(value.forbidden_claims_observed),
    }


def _conflict_plain(value: ConflictSetV01) -> dict[str, object]:
    return {
        "conflict_set_id": value.conflict_set_id,
        "subject": value.subject,
        "predicate": value.predicate,
        "claim_ids": list(value.claim_ids),
        "conflicting_values": [
            _thaw_json_value(item) for item in value.conflicting_values
        ],
        "source_modes": list(value.source_modes),
        "resolution_state": value.resolution_state,
    }


def _synthesis_plain(value: SynthesisProposalV01) -> dict[str, object]:
    return {
        "proposal_id": value.proposal_id,
        "request_id": value.request_id,
        "source_contribution_ids": list(value.source_contribution_ids),
        "normalized_claims": [_claim_plain(item) for item in value.normalized_claims],
        "conflict_sets": [_conflict_plain(item) for item in value.conflict_sets],
        "missing_evidence_refs": list(value.missing_evidence_refs),
        "contribution_modes": list(value.contribution_modes),
        "requested_validators": list(value.requested_validators),
        "synthesis_summary": value.synthesis_summary,
        "authority_class": value.authority_class,
        "root_review_required": value.root_review_required,
    }


def _packet_plain(value: RootReviewPacketV01) -> dict[str, object]:
    return {
        "packet_id": value.packet_id,
        "request_id": value.request_id,
        "transaction_id": value.transaction_id,
        "target_root_id": value.target_root_id,
        "runtime_topology_ref": value.runtime_topology_ref,
        "synthesis_proposal": _synthesis_plain(value.synthesis_proposal),
        "contribution_ids": list(value.contribution_ids),
        "conflict_set_ids": list(value.conflict_set_ids),
        "missing_evidence_refs": list(value.missing_evidence_refs),
        "required_validator_ids": list(value.required_validator_ids),
        "review_state": value.review_state,
        "authority_class": value.authority_class,
        "root_decision_created": value.root_decision_created,
        "permission_created": value.permission_created,
        "final_output_created": value.final_output_created,
    }
