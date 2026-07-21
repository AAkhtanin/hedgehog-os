"""Canonicalize untrusted Airline causal semantics with trusted runtime context.

Provider responses at this boundary contain semantics only. Runtime-owned
identity, lineage, status, authority, and effect fields are derived locally and
then checked by the existing Airline binding and causal-runtime validators.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from typing import Any, Mapping
import unicodedata

from hedgehog.domains.airline import semantic_to_contract_binding_v01 as binding
from hedgehog.domains.airline import semantic_to_contract_causal_runtime_v01 as runtime


STATUS_PASS = binding.STATUS_PASS
STATUS_FAIL_CLOSED = binding.STATUS_FAIL_CLOSED

PROPOSER_SEMANTIC_FIELDS = (
    "recommended_offer_id",
    "ranked_offer_ids",
    "decision_factors",
    "preference_matches",
    "uncertainty_notes",
    "requires_root_review",
    "semantic_summary",
)
REVIEWER_SEMANTIC_FIELDS = (
    "supports_proposed_offer",
    "semantic_factors",
    "blocking_conflicts",
)

REASON_RAW_RESPONSE_INVALID = "airline_semantic_provider_raw_response_invalid"
REASON_SEMANTIC_SHAPE_INVALID = "airline_semantic_provider_envelope_invalid"
REASON_SEMANTIC_VALUE_INVALID = "airline_semantic_provider_value_invalid"
REASON_SEMANTIC_OFFER_INVALID = "airline_semantic_provider_offer_invalid"
REASON_TRUSTED_CONTEXT_INVALID = "airline_semantic_trusted_context_invalid"
REASON_CANONICAL_VALIDATION_FAILED = "airline_semantic_canonical_validation_failed"

_MAX_RAW_BYTES = 16384
_MAX_STRING_CHARS = 2048
_MAX_COLLECTION_ITEMS = 32


@dataclass(frozen=True, slots=True)
class AirlineCausalProposerSemanticEnvelopeV01:
    recommended_offer_id: str
    ranked_offer_ids: tuple[str, ...]
    decision_factors: tuple[str, ...]
    preference_matches: tuple[str, ...]
    uncertainty_notes: tuple[str, ...]
    requires_root_review: bool
    semantic_summary: str


@dataclass(frozen=True, slots=True)
class AirlineCausalReviewerSemanticEnvelopeV01:
    supports_proposed_offer: bool
    semantic_factors: tuple[str, ...]
    blocking_conflicts: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class AirlineSemanticEnvelopeValidationV01:
    validation_status: str
    reason_codes: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class AirlineSemanticCanonicalValidationV01:
    validation_status: str
    reason_codes: tuple[str, ...]
    canonical_artifact_type: str
    canonical_artifact_id: str


@dataclass(frozen=True, slots=True)
class AirlineSemanticFieldOwnershipV01:
    provider_field_names: tuple[str, ...]
    runtime_field_names: tuple[str, ...]
    complete: bool
    disjoint: bool


@dataclass(frozen=True, slots=True)
class AirlineSemanticProviderCanonicalizationResultV01:
    canonicalization_id: str
    actor_id: str
    semantic_kind: str
    final_status: str
    raw_provider_response: str
    extracted_semantic_object: (
        AirlineCausalProposerSemanticEnvelopeV01
        | AirlineCausalReviewerSemanticEnvelopeV01
        | None
    )
    semantic_validation: AirlineSemanticEnvelopeValidationV01
    runtime_canonical_artifact: (
        binding.AirlineSemanticOfferSelectionProposalV01
        | runtime.AirlineInjectedReviewerResponseV01
        | None
    )
    canonical_validation: AirlineSemanticCanonicalValidationV01
    field_ownership: AirlineSemanticFieldOwnershipV01


def canonicalize_airline_causal_provider_response_v01(
    *,
    raw_provider_response: object,
    request: object,
    bsep_projection: object,
    constraints: object,
    selection_input: object,
    snapshot: object,
) -> AirlineSemanticProviderCanonicalizationResultV01:
    """Validate semantic JSON and bind it to existing canonical contracts."""
    raw_bytes = _strict_raw_response_bytes(raw_provider_response)
    actor_id = _safe_actor_id(request)
    semantic_kind = _semantic_kind(actor_id)
    try:
        context_reasons = _trusted_context_reasons(
            request=request,
            bsep_projection=bsep_projection,
            constraints=constraints,
            selection_input=selection_input,
            snapshot=snapshot,
        )
    except Exception:
        context_reasons = (REASON_TRUSTED_CONTEXT_INVALID,)
    if context_reasons:
        return _failed_result(
            raw_provider_response=raw_provider_response,
            raw_bytes=raw_bytes,
            actor_id=actor_id,
            semantic_kind=semantic_kind,
            semantic_reasons=context_reasons,
        )

    try:
        return _canonicalize_valid_context(
            raw_provider_response=raw_provider_response,
            raw_bytes=raw_bytes,
            request=request,
            bsep_projection=bsep_projection,
            constraints=constraints,
            selection_input=selection_input,
            snapshot=snapshot,
            actor_id=actor_id,
            semantic_kind=semantic_kind,
        )
    except Exception:
        return _failed_result(
            raw_provider_response=raw_provider_response,
            raw_bytes=raw_bytes,
            actor_id=actor_id,
            semantic_kind=semantic_kind,
            semantic_reasons=(REASON_SEMANTIC_VALUE_INVALID,),
        )


def _canonicalize_valid_context(
    *,
    raw_provider_response: object,
    raw_bytes: bytes | None,
    request: runtime.AirlineInjectedSemanticActorRequestV01,
    bsep_projection: binding.AirlineBSEPProjectionRefV01,
    constraints: binding.ClientRootTravelConstraintSetV01,
    selection_input: binding.AirlineSemanticSelectionInputV01,
    snapshot: binding.AirlineRootOfferCandidateSetSnapshotV01,
    actor_id: str,
    semantic_kind: str,
) -> AirlineSemanticProviderCanonicalizationResultV01:
    parsed, parse_reasons = _parse_raw_response(raw_provider_response, raw_bytes)
    envelope: (
        AirlineCausalProposerSemanticEnvelopeV01
        | AirlineCausalReviewerSemanticEnvelopeV01
        | None
    ) = None
    semantic_reasons = list(parse_reasons)
    if not semantic_reasons:
        if semantic_kind == "causal_proposer":
            envelope, envelope_reasons = _proposer_envelope(
                parsed,
                selection_input,
            )
        else:
            envelope, envelope_reasons = _reviewer_envelope(parsed)
        semantic_reasons.extend(envelope_reasons)
    semantic_reasons = list(dict.fromkeys(semantic_reasons))
    semantic_validation = AirlineSemanticEnvelopeValidationV01(
        validation_status=STATUS_PASS if not semantic_reasons else STATUS_FAIL_CLOSED,
        reason_codes=tuple(semantic_reasons),
    )

    canonical_mapping: dict[str, object] = {}
    canonical_artifact: (
        binding.AirlineSemanticOfferSelectionProposalV01
        | runtime.AirlineInjectedReviewerResponseV01
        | None
    ) = None
    canonical_accepted = False
    canonical_reasons: tuple[str, ...] = (
        (REASON_CANONICAL_VALIDATION_FAILED,)
        if semantic_validation.validation_status != STATUS_PASS
        else ()
    )
    canonical_type = ""
    canonical_id = ""
    provider_fields = (
        PROPOSER_SEMANTIC_FIELDS
        if semantic_kind == "causal_proposer"
        else REVIEWER_SEMANTIC_FIELDS
    )
    runtime_fields: tuple[str, ...] = ()

    if semantic_validation.validation_status == STATUS_PASS and envelope is not None:
        if type(envelope) is AirlineCausalProposerSemanticEnvelopeV01:
            canonical_mapping = _proposer_mapping(envelope, request)
            canonical_artifact, report = (
                binding.build_airline_semantic_offer_selection_proposal_from_payload_v01(
                    selection_input,
                    canonical_mapping,
                )
            )
            canonical_reasons = tuple(report.reason_codes)
            canonical_accepted = canonical_artifact is not None
            canonical_type = "AirlineSemanticOfferSelectionProposalV01"
            canonical_id = str(canonical_mapping["proposal_id"])
        else:
            canonical_mapping = _reviewer_mapping(envelope, request)
            validated_artifact, canonical_reasons = (
                runtime.parse_injected_reviewer_response_v01(
                    request=request,
                    selection_input=selection_input,
                    proposed_offer_id=request.proposed_offer_id,
                    payload=canonical_mapping,
                )
            )
            canonical_artifact = (
                validated_artifact
                if validated_artifact is not None
                else runtime.AirlineInjectedReviewerResponseV01(
                    **{
                        **canonical_mapping,
                        "semantic_factors": tuple(
                            canonical_mapping["semantic_factors"]
                        ),
                        "blocking_conflicts": tuple(
                            canonical_mapping["blocking_conflicts"]
                        ),
                    }
                )
            )
            canonical_accepted = validated_artifact is not None
            canonical_type = "AirlineInjectedReviewerResponseV01"
            canonical_id = str(canonical_mapping["response_id"])
        runtime_fields = tuple(
            field for field in canonical_mapping if field not in provider_fields
        )

    canonical_validation = AirlineSemanticCanonicalValidationV01(
        validation_status=(
            STATUS_PASS
            if canonical_accepted and not canonical_reasons
            else STATUS_FAIL_CLOSED
        ),
        reason_codes=tuple(canonical_reasons),
        canonical_artifact_type=canonical_type,
        canonical_artifact_id=canonical_id,
    )
    complete = bool(canonical_mapping) and set(provider_fields).union(runtime_fields) == set(
        canonical_mapping
    )
    disjoint = not set(provider_fields).intersection(runtime_fields)
    ownership = AirlineSemanticFieldOwnershipV01(
        provider_field_names=tuple(provider_fields),
        runtime_field_names=runtime_fields,
        complete=complete,
        disjoint=disjoint,
    )
    final_status = (
        STATUS_PASS
        if semantic_validation.validation_status == STATUS_PASS
        and canonical_validation.validation_status == STATUS_PASS
        and ownership.complete
        and ownership.disjoint
        else STATUS_FAIL_CLOSED
    )
    identity_payload = {
        "actor_id": actor_id,
        "semantic_kind": semantic_kind,
        "final_status": final_status,
        "raw_provider_response_sha256": (
            hashlib.sha256(raw_bytes).hexdigest() if raw_bytes is not None else ""
        ),
        "semantic_envelope": asdict(envelope) if envelope is not None else None,
        "semantic_validation": asdict(semantic_validation),
        "canonical_artifact": asdict(canonical_artifact)
        if canonical_artifact is not None
        else None,
        "canonical_validation": asdict(canonical_validation),
        "field_ownership": asdict(ownership),
    }
    return AirlineSemanticProviderCanonicalizationResultV01(
        canonicalization_id="airline_semantic_provider_canonicalization:"
        + hashlib.sha256(_canonical_json(identity_payload)).hexdigest(),
        actor_id=actor_id,
        semantic_kind=semantic_kind,
        final_status=final_status,
        raw_provider_response=(
            raw_provider_response if raw_bytes is not None else ""
        ),
        extracted_semantic_object=envelope,
        semantic_validation=semantic_validation,
        runtime_canonical_artifact=canonical_artifact,
        canonical_validation=canonical_validation,
        field_ownership=ownership,
    )


def _failed_result(
    *,
    raw_provider_response: object,
    raw_bytes: bytes | None,
    actor_id: str,
    semantic_kind: str,
    semantic_reasons: tuple[str, ...],
) -> AirlineSemanticProviderCanonicalizationResultV01:
    provider_fields = (
        PROPOSER_SEMANTIC_FIELDS
        if semantic_kind == "causal_proposer"
        else REVIEWER_SEMANTIC_FIELDS
        if semantic_kind == "causal_reviewer"
        else ()
    )
    semantic_validation = AirlineSemanticEnvelopeValidationV01(
        validation_status=STATUS_FAIL_CLOSED,
        reason_codes=semantic_reasons or (REASON_SEMANTIC_VALUE_INVALID,),
    )
    canonical_validation = AirlineSemanticCanonicalValidationV01(
        validation_status=STATUS_FAIL_CLOSED,
        reason_codes=(REASON_CANONICAL_VALIDATION_FAILED,),
        canonical_artifact_type="",
        canonical_artifact_id="",
    )
    ownership = AirlineSemanticFieldOwnershipV01(
        provider_field_names=tuple(provider_fields),
        runtime_field_names=(),
        complete=False,
        disjoint=True,
    )
    identity_payload = {
        "actor_id": actor_id,
        "semantic_kind": semantic_kind,
        "final_status": STATUS_FAIL_CLOSED,
        "raw_provider_response_sha256": (
            hashlib.sha256(raw_bytes).hexdigest() if raw_bytes is not None else ""
        ),
        "semantic_envelope": None,
        "semantic_validation": asdict(semantic_validation),
        "canonical_artifact": None,
        "canonical_validation": asdict(canonical_validation),
        "field_ownership": asdict(ownership),
    }
    return AirlineSemanticProviderCanonicalizationResultV01(
        canonicalization_id="airline_semantic_provider_canonicalization:"
        + hashlib.sha256(_canonical_json(identity_payload)).hexdigest(),
        actor_id=actor_id,
        semantic_kind=semantic_kind,
        final_status=STATUS_FAIL_CLOSED,
        raw_provider_response=(
            raw_provider_response if raw_bytes is not None else ""
        ),
        extracted_semantic_object=None,
        semantic_validation=semantic_validation,
        runtime_canonical_artifact=None,
        canonical_validation=canonical_validation,
        field_ownership=ownership,
    )


def _safe_actor_id(request: object) -> str:
    if type(request) is not runtime.AirlineInjectedSemanticActorRequestV01:
        return ""
    actor_id = request.actor_id
    return actor_id if _exact_string(actor_id) else ""


def _semantic_kind(actor_id: str) -> str:
    if actor_id == runtime.ACTOR_ORDER[0]:
        return "causal_proposer"
    if actor_id in runtime.ACTOR_ORDER[1:]:
        return "causal_reviewer"
    return ""


def airline_semantic_canonicalization_result_to_plain_dict_v01(
    result: AirlineSemanticProviderCanonicalizationResultV01,
) -> dict[str, object]:
    if type(result) is not AirlineSemanticProviderCanonicalizationResultV01:
        raise ValueError(REASON_CANONICAL_VALIDATION_FAILED)
    return {
        "canonicalization_id": result.canonicalization_id,
        "actor_id": result.actor_id,
        "semantic_kind": result.semantic_kind,
        "final_status": result.final_status,
        "raw_provider_response": result.raw_provider_response,
        "extracted_semantic_object": (
            asdict(result.extracted_semantic_object)
            if result.extracted_semantic_object is not None
            else None
        ),
        "semantic_validation": asdict(result.semantic_validation),
        "runtime_canonical_artifact": (
            asdict(result.runtime_canonical_artifact)
            if result.runtime_canonical_artifact is not None
            else None
        ),
        "canonical_validation": asdict(result.canonical_validation),
        "field_ownership": asdict(result.field_ownership),
    }


def _strict_raw_response_bytes(raw: object) -> bytes | None:
    if type(raw) is not str:
        return None
    try:
        encoded = raw.encode("utf-8", errors="strict")
    except UnicodeError:
        return None
    if not encoded or len(encoded) > _MAX_RAW_BYTES:
        return None
    return encoded


def _parse_raw_response(
    raw: object,
    raw_bytes: bytes | None,
) -> tuple[dict[str, object], tuple[str, ...]]:
    if raw_bytes is None or type(raw) is not str:
        return {}, (REASON_RAW_RESPONSE_INVALID,)

    def pairs(items: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in items:
            if key in result:
                raise ValueError
            result[key] = value
        return result

    try:
        parsed = json.loads(
            raw,
            object_pairs_hook=pairs,
            parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)),
        )
    except (TypeError, ValueError, json.JSONDecodeError):
        return {}, (REASON_RAW_RESPONSE_INVALID,)
    if type(parsed) is not dict:
        return {}, (REASON_SEMANTIC_SHAPE_INVALID,)
    return parsed, ()


def _exact_string(value: object) -> bool:
    if (
        type(value) is not str
        or not value
        or value != value.strip()
        or len(value) > _MAX_STRING_CHARS
        or value != unicodedata.normalize("NFC", value)
    ):
        return False
    try:
        value.encode("utf-8", errors="strict")
    except UnicodeError:
        return False
    return all(not unicodedata.category(char).startswith("C") for char in value)


def _string_tuple(value: object, *, allow_empty: bool = False) -> tuple[str, ...] | None:
    if type(value) is not list or len(value) > _MAX_COLLECTION_ITEMS:
        return None
    if not allow_empty and not value:
        return None
    if any(not _exact_string(item) for item in value):
        return None
    return tuple(value)


def _proposer_envelope(
    payload: Mapping[str, object],
    selection_input: binding.AirlineSemanticSelectionInputV01,
) -> tuple[AirlineCausalProposerSemanticEnvelopeV01 | None, tuple[str, ...]]:
    if tuple(payload) == () or set(payload) != set(PROPOSER_SEMANTIC_FIELDS):
        return None, (REASON_SEMANTIC_SHAPE_INVALID,)
    ranked = _string_tuple(payload["ranked_offer_ids"])
    factors = _string_tuple(payload["decision_factors"])
    matches = _string_tuple(payload["preference_matches"])
    uncertainty = _string_tuple(payload["uncertainty_notes"])
    recommendation = payload["recommended_offer_id"]
    summary = payload["semantic_summary"]
    if (
        not _exact_string(recommendation)
        or ranked is None
        or factors is None
        or matches is None
        or uncertainty is None
        or type(payload["requires_root_review"]) is not bool
        or payload["requires_root_review"] is not True
        or not _exact_string(summary)
    ):
        return None, (REASON_SEMANTIC_VALUE_INVALID,)
    allowed = set(selection_input.visible_candidate_ids).intersection(
        selection_input.airline_valid_candidate_ids,
        selection_input.client_hard_compatible_candidate_ids,
    )
    if (
        len(set(ranked)) != len(ranked)
        or ranked.count(recommendation) != 1
        or any(offer_id not in allowed for offer_id in ranked)
    ):
        return None, (REASON_SEMANTIC_OFFER_INVALID,)
    return AirlineCausalProposerSemanticEnvelopeV01(
        recommended_offer_id=recommendation,
        ranked_offer_ids=ranked,
        decision_factors=factors,
        preference_matches=matches,
        uncertainty_notes=uncertainty,
        requires_root_review=True,
        semantic_summary=summary,
    ), ()


def _reviewer_envelope(
    payload: Mapping[str, object],
) -> tuple[AirlineCausalReviewerSemanticEnvelopeV01 | None, tuple[str, ...]]:
    if set(payload) != set(REVIEWER_SEMANTIC_FIELDS):
        return None, (REASON_SEMANTIC_SHAPE_INVALID,)
    factors = _string_tuple(payload["semantic_factors"])
    conflicts = _string_tuple(payload["blocking_conflicts"], allow_empty=True)
    if (
        type(payload["supports_proposed_offer"]) is not bool
        or factors is None
        or conflicts is None
    ):
        return None, (REASON_SEMANTIC_VALUE_INVALID,)
    return AirlineCausalReviewerSemanticEnvelopeV01(
        supports_proposed_offer=payload["supports_proposed_offer"],
        semantic_factors=factors,
        blocking_conflicts=conflicts,
    ), ()


def _trusted_context_reasons(
    *,
    request: object,
    bsep_projection: object,
    constraints: object,
    selection_input: object,
    snapshot: object,
) -> tuple[str, ...]:
    if (
        type(request) is not runtime.AirlineInjectedSemanticActorRequestV01
        or type(bsep_projection) is not binding.AirlineBSEPProjectionRefV01
        or type(constraints) is not binding.ClientRootTravelConstraintSetV01
        or type(selection_input) is not binding.AirlineSemanticSelectionInputV01
        or type(snapshot) is not binding.AirlineRootOfferCandidateSetSnapshotV01
        or request.actor_id not in runtime.ACTOR_ORDER
    ):
        return (REASON_TRUSTED_CONTEXT_INVALID,)
    allowed = set(selection_input.visible_candidate_ids).intersection(
        selection_input.airline_valid_candidate_ids,
        selection_input.client_hard_compatible_candidate_ids,
    )
    if request.actor_id == runtime.ACTOR_ORDER[0]:
        if request.proposed_offer_id != "":
            return (REASON_TRUSTED_CONTEXT_INVALID,)
    elif (
        not _exact_string(request.proposed_offer_id)
        or request.proposed_offer_id not in allowed
    ):
        return (REASON_TRUSTED_CONTEXT_INVALID,)
    reports = (
        binding.validate_airline_bsep_projection_ref_v01(bsep_projection),
        binding.validate_client_root_travel_constraint_set_v01(constraints),
        binding.validate_airline_candidate_snapshot_v01(snapshot),
        binding.validate_airline_semantic_selection_input_v01(
            bsep_projection,
            constraints,
            snapshot,
            selection_input,
        ),
    )
    if any(report.validation_status != STATUS_PASS for report in reports):
        return (REASON_TRUSTED_CONTEXT_INVALID,)
    expected = runtime.build_airline_semantic_actor_request_v01(
        actor_id=request.actor_id,
        selection_input=selection_input,
        constraints=constraints,
        snapshot=snapshot,
        proposed_offer_id=request.proposed_offer_id,
    )
    if request != expected:
        return (REASON_TRUSTED_CONTEXT_INVALID,)
    return ()


def _proposer_mapping(
    envelope: AirlineCausalProposerSemanticEnvelopeV01,
    request: runtime.AirlineInjectedSemanticActorRequestV01,
) -> dict[str, object]:
    result: dict[str, object] = {
        "proposal_id": f"semantic_offer_selection_proposal:{envelope.recommended_offer_id}",
        "transaction_id": request.transaction_id,
        "actor_id": request.actor_id,
        "source_selection_input_id": request.source_selection_input_id,
        "source_bsep_projection_ref": request.source_bsep_projection_ref,
        "source_client_constraint_set_id": request.source_client_constraint_set_id,
        "source_candidate_set_snapshot_id": request.source_candidate_set_snapshot_id,
        "source_candidate_set_digest": request.source_candidate_set_digest,
        "candidate_set_ref": request.source_candidate_set_ref,
        **asdict(envelope),
        "authority_created": False,
        "action_permission_created": False,
        "packet_created": False,
        "receipt_created": False,
        "payment_created": False,
        "ticket_created": False,
        "booking_created": False,
        "final_output_created": False,
        "real_world_effects_count": 0,
    }
    return result


def _reviewer_mapping(
    envelope: AirlineCausalReviewerSemanticEnvelopeV01,
    request: runtime.AirlineInjectedSemanticActorRequestV01,
) -> dict[str, object]:
    accepted = envelope.supports_proposed_offer and not envelope.blocking_conflicts
    status = STATUS_PASS if accepted else STATUS_FAIL_CLOSED
    return {
        "response_id": f"{request.actor_id}_response_001",
        "transaction_id": request.transaction_id,
        "actor_id": request.actor_id,
        "source_request_id": request.request_id,
        "source_selection_input_id": request.source_selection_input_id,
        "source_candidate_set_snapshot_id": request.source_candidate_set_snapshot_id,
        "source_candidate_set_digest": request.source_candidate_set_digest,
        "reviewed_offer_id": request.proposed_offer_id,
        "review_role": request.actor_role,
        "review_status": status,
        **asdict(envelope),
        "validation_status": status,
        "raw_output_used": False,
        "authority_created": False,
        "permission_created": False,
        "real_world_effects_count": 0,
    }


def _canonical_json(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
