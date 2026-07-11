"""Airline semantic-to-contract causal test runtime.

This is an Airline-domain causal test runtime, not Hedgehog OS universal core
and not an installed Needle. It uses an injected semantic provider only. It
does not call network or Gemini, contains no preference-to-offer selection
algorithm, does not execute corridor, and does not create receipts or real
effects. Provider semantics remain advisory. Root remains authority.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Any, Callable, Mapping

from hedgehog.domains.airline import (
    semantic_to_contract_binding_v01 as binding,
)
from hedgehog.domains.airline import (
    ticket_purchase_corridor_v01 as corridor_contracts,
)


MODULE_ID = "airline_semantic_to_contract_causal_runtime_v01"
SLICE_ID = "airline_semantic_to_contract_causal_binding_v01_slice_c"
RUN_ID = "airline_semantic_to_contract_causal_runtime_v01"
NEXT_GATE = (
    "airline_semantic_to_contract_causal_binding_v01_slice_d_existing_lane_integration"
)
CAUSAL_PROBE_CONSTRAINT_ID_X = "client_constraints:causal_probe:7f3a"
CAUSAL_PROBE_CONSTRAINT_ID_Y = "client_constraints:causal_probe:c91d"

STATUS_LOCAL_MODEL_PASS = binding.STATUS_LOCAL_MODEL_PASS
STATUS_ROOT_OVERRIDE = binding.STATUS_ROOT_OVERRIDE
STATUS_FAIL_CLOSED = binding.STATUS_FAIL_CLOSED

STAGE_BSEP = "bsep_projection_validation"
STAGE_CONSTRAINTS = "client_constraints_validation"
STAGE_SNAPSHOT = "candidate_snapshot_validation"
STAGE_SELECTION_INPUT = "selection_input_validation"
STAGE_PROPOSER_CALL = "proposer_call"
STAGE_PROPOSAL_VALIDATION = "proposal_validation"
STAGE_PROPOSER_REVIEW = "proposer_canonical_review_validation"
STAGE_REVIEWER_CALLS = "reviewer_calls"
STAGE_ACTOR_REVIEWS = "actor_reviews_validation"
STAGE_SYNTHESIS = "synthesis_validation"
STAGE_CANONICAL_EVIDENCE = "canonical_evidence_validation"
STAGE_CLIENT_ROOT_DECISION = "client_root_decision_validation"
STAGE_AIRLINE_ROOT_RESOLUTION = "airline_root_resolution_validation"
STAGE_HOLD_BINDING = "hold_binding_validation"
STAGE_BINDING_REPORT = "causal_binding_report_validation"
STAGE_LOCAL_CHAIN = "local_chain_validation"

REASON_PROVIDER_CALL_FAILED = "provider_call_failed"
REASON_REVIEWER_RESPONSE_INVALID = "reviewer_response_invalid"
REASON_EXACT_FIVE_SEMANTIC_ACTOR_CALLS_REQUIRED = (
    "exact_five_semantic_actor_calls_required"
)
REASON_ACTOR_CALL_ORDER_MISMATCH = "actor_call_order_mismatch"
REASON_SEMANTIC_CHANGE_DID_NOT_PROPAGATE_TO_CONTRACT = (
    "semantic_change_did_not_propagate_to_contract"
)
REASON_HARDCODED_DEFAULT_DETECTED = "hardcoded_default_detected"
REASON_SILENT_FALLBACK_DETECTED = "silent_fallback_detected"
REASON_CAUSAL_RUN_REPORT_IDENTITY_MISMATCH = (
    "causal_run_report_identity_mismatch"
)
REASON_CAUSAL_RUN_PROVIDER_CALL_SHAPE_MISMATCH = (
    "causal_run_provider_call_shape_mismatch"
)
REASON_CAUSAL_RUN_ACTOR_ORDER_MISMATCH = "causal_run_actor_order_mismatch"
REASON_CAUSAL_RUN_DERIVED_FIELD_MISMATCH = "causal_run_derived_field_mismatch"
REASON_CAUSAL_RUN_DOWNSTREAM_ARTIFACT_AFTER_FAILURE = (
    "causal_run_downstream_artifact_after_failure"
)
REASON_CAUSAL_RUN_COUNTER_MISMATCH = "causal_run_counter_mismatch"
REASON_CAUSAL_RUN_CHAIN_VALIDATION_FAILED = (
    "causal_run_chain_validation_failed"
)
REASON_CAUSAL_RUN_HARD_CONSTRAINT_FINGERPRINT_MISMATCH = (
    "causal_run_hard_constraint_fingerprint_mismatch"
)
REASON_CAUSAL_RUN_SOFT_PREFERENCE_FINGERPRINT_MISMATCH = (
    "causal_run_soft_preference_fingerprint_mismatch"
)
REASON_CAUSAL_RUN_REQUEST_CONTENT_MISMATCH = (
    "causal_run_request_content_mismatch"
)
REASON_CAUSAL_RUN_CALL_RECORD_REQUEST_MISMATCH = (
    "causal_run_call_record_request_mismatch"
)
REASON_CAUSAL_RUN_RESPONSE_REQUEST_MISMATCH = (
    "causal_run_response_request_mismatch"
)
REASON_CAUSAL_RUN_RESPONSE_REVIEW_MISMATCH = (
    "causal_run_response_review_mismatch"
)
REASON_PROVIDER_IDENTITY_INVARIANCE_FAILED = (
    "provider_identity_invariance_failed"
)
REASON_PROVIDER_IDENTITY_PROBE_BINDING_MISMATCH = (
    "provider_identity_probe_binding_mismatch"
)

ACTOR_ORDER = (
    binding.ACTOR_CLIENT_PURCHASE_INTENT_REVIEWER,
    binding.ACTOR_AIRLINE_OFFER_POLICY_REVIEWER,
    binding.ACTOR_AIRLINE_FARE_RULES_VERTICAL_CELL,
    binding.ACTOR_AIRLINE_SEAT_BAGGAGE_VERTICAL_CELL,
    binding.ACTOR_TRI_PARTY_EVIDENCE_CONSISTENCY_REVIEWER,
)

AirlineInjectedSemanticProviderV01 = Callable[
    [str, Mapping[str, Any]],
    Mapping[str, Any],
]


@dataclass(frozen=True)
class AirlineInjectedSemanticActorRequestV01:
    request_id: str
    transaction_id: str
    actor_id: str
    actor_role: str
    source_selection_input_id: str
    source_bsep_projection_ref: str
    source_client_constraint_set_id: str
    source_candidate_set_ref: str
    source_candidate_set_snapshot_id: str
    source_candidate_set_digest: str
    visible_candidate_ids: tuple[str, ...]
    airline_valid_candidate_ids: tuple[str, ...]
    client_hard_compatible_candidate_ids: tuple[str, ...]
    soft_tradeoff_candidate_ids: tuple[str, ...]
    client_hard_constraints: Mapping[str, Any]
    client_soft_preferences: Mapping[str, Any]
    proposed_offer_id: str
    authoritative_candidate_projection: tuple[Mapping[str, Any], ...]
    provider_may_create_authority: bool
    provider_may_create_contract: bool
    provider_may_create_packet: bool
    provider_may_create_receipt: bool
    provider_may_execute_action: bool
    raw_secret_included: bool


@dataclass(frozen=True)
class AirlineInjectedReviewerResponseV01:
    response_id: str
    transaction_id: str
    actor_id: str
    source_request_id: str
    source_selection_input_id: str
    source_candidate_set_snapshot_id: str
    source_candidate_set_digest: str
    reviewed_offer_id: str
    review_role: str
    review_status: str
    semantic_factors: tuple[str, ...]
    blocking_conflicts: tuple[str, ...]
    supports_proposed_offer: bool
    validation_status: str
    raw_output_used: bool
    authority_created: bool
    permission_created: bool
    real_world_effects_count: int


@dataclass(frozen=True)
class AirlineSemanticProviderCallRecordV01:
    call_index: int
    actor_id: str
    actor_role: str
    request_id: str
    proposed_offer_id: str
    provider_returned: bool
    validation_status: str
    reason_codes: tuple[str, ...]


@dataclass(frozen=True)
class AirlineSemanticCausalRunReportV01:
    run_id: str
    slice_id: str
    scenario_id: str
    final_status: str
    failed_stage: str
    transaction_id: str
    client_constraint_set_id: str
    candidate_set_snapshot_id: str
    candidate_set_digest: str
    soft_preference_fingerprint: str
    hard_constraint_fingerprint: str
    provider_call_records: tuple[AirlineSemanticProviderCallRecordV01, ...]
    provider_call_count: int
    proposer_request: AirlineInjectedSemanticActorRequestV01 | None
    proposer_payload: Mapping[str, Any]
    proposal: binding.AirlineSemanticOfferSelectionProposalV01 | None
    reviewer_request_records: tuple[AirlineInjectedSemanticActorRequestV01, ...]
    reviewer_responses: tuple[AirlineInjectedReviewerResponseV01, ...]
    actor_reviews: tuple[binding.AirlineCanonicalActorSelectionReviewV01, ...]
    synthesis: binding.AirlineSemanticSelectionSynthesisReportV01 | None
    canonical_evidence: binding.ValidatedAirlineSemanticSelectionEvidenceV01 | None
    client_root_decision: binding.ClientRootOfferSelectionDecisionV01 | None
    airline_root_resolution: binding.AirlineRootSelectedOfferResolutionV01 | None
    hold_packet: corridor_contracts.AirlineHoldCommitPacketV01 | None
    hold_binding: binding.AirlineSemanticHoldContractBindingV01 | None
    causal_binding_report: binding.AirlineSemanticToContractBindingReportV01 | None
    local_chain_validation: binding.AirlineSemanticToContractValidationReportV01 | None
    semantic_recommendation_id: str
    root_selected_offer_id: str
    hold_contract_offer_id: str
    semantic_to_root_binding_match: bool
    root_to_hold_binding_match: bool
    default_offer_used: bool
    silent_fallback_used: bool
    provider_created_authority_count: int
    provider_created_contract_count: int
    runtime_receipt_created_count: int
    corridor_execution_count: int
    provider_network_call_count: int
    gemini_call_count: int
    real_world_effects_count: int
    validation_errors: tuple[str, ...]
    next_gate: str


@dataclass(frozen=True)
class AirlineSemanticCounterfactualPairReportV01:
    pair_id: str
    final_status: str
    scenario_a: AirlineSemanticCausalRunReportV01
    scenario_b: AirlineSemanticCausalRunReportV01
    identity_invariance_report: "AirlineSemanticIdentityInvarianceReportV01"
    identity_invariance_passed: bool
    provider_identity_sensitive_detected: bool
    same_candidate_snapshot_id: bool
    same_candidate_snapshot_digest: bool
    hard_constraints_identical: bool
    soft_preferences_different: bool
    semantic_recommendations_different: bool
    root_selected_offers_different: bool
    hold_contract_offers_different: bool
    scenario_a_recommendation: str
    scenario_b_recommendation: str
    scenario_a_hold_offer: str
    scenario_b_hold_offer: str
    fixed_safety_invariants_identical: bool
    provider_call_count: int
    semantic_change_propagated_to_contract: bool
    hardcoded_default_detected: bool
    silent_fallback_detected: bool
    validation_errors: tuple[str, ...]
    real_world_effects_count: int


@dataclass(frozen=True)
class AirlineSemanticIdentityInvarianceReportV01:
    report_id: str
    final_status: str
    probe_constraint_id_x: str
    probe_constraint_id_y: str
    preference_a_first: AirlineSemanticCausalRunReportV01
    preference_a_second: AirlineSemanticCausalRunReportV01
    preference_b_first: AirlineSemanticCausalRunReportV01
    preference_b_second: AirlineSemanticCausalRunReportV01
    a_content_identical: bool
    b_content_identical: bool
    a_ids_different: bool
    b_ids_different: bool
    a_recommendations_identical: bool
    b_recommendations_identical: bool
    swapped_id_recommendations_follow_content: bool
    provider_identity_invariant: bool
    validation_errors: tuple[str, ...]
    provider_call_count: int
    real_world_effects_count: int


def _dedupe(reasons: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(reason for reason in reasons if reason))


def _failure_validation_report(
    *,
    validation_id: str,
    artifact_type: str,
    artifact_id: str,
    transaction_id: str,
    relevant_root_id: str,
    reasons: tuple[str, ...] | list[str],
) -> binding.AirlineSemanticToContractValidationReportV01:
    reason_tuple = _dedupe(reasons) or (binding.REASON_VALIDATION_FAILED,)
    return binding.AirlineSemanticToContractValidationReportV01(
        validation_id=validation_id,
        artifact_type=artifact_type,
        artifact_id=artifact_id,
        transaction_id=transaction_id,
        validation_status=STATUS_FAIL_CLOSED,
        reason_codes=reason_tuple,
        return_to_root_required=True,
        relevant_root_id=relevant_root_id,
        authority_created=False,
        permission_created=False,
        contract_artifact_created=False,
        real_world_effects_count=0,
    )


def _hard_constraint_fingerprint(
    constraints: binding.ClientRootTravelConstraintSetV01,
) -> str:
    return "|".join(
        str(value)
        for value in (
            constraints.transaction_id,
            constraints.client_root_id,
            constraints.origin,
            constraints.destination,
            constraints.departure_date,
            constraints.return_date,
            constraints.max_amount,
            constraints.currency,
            constraints.baggage_required,
            constraints.avoid_overnight_layover,
        )
    )


def _soft_preference_fingerprint(
    constraints: binding.ClientRootTravelConstraintSetV01,
) -> str:
    return "|".join(
        (
            ",".join(constraints.preferred_seat_characteristics),
            str(constraints.changeable_preferred),
            ",".join(constraints.soft_preference_priority),
        )
    )


def _mapping_fingerprint(mapping: Mapping[str, Any]) -> str:
    return "|".join(f"{key}={mapping[key]}" for key in sorted(mapping))


def hard_constraint_fingerprint_from_request_v01(
    request: AirlineInjectedSemanticActorRequestV01,
) -> str:
    return "|".join(
        (
            str(request.transaction_id),
            _mapping_fingerprint(request.client_hard_constraints),
        ),
    )


def soft_preference_fingerprint_from_request_v01(
    request: AirlineInjectedSemanticActorRequestV01,
) -> str:
    return "|".join(
        (
            str(request.transaction_id),
            _mapping_fingerprint(request.client_soft_preferences),
        ),
    )


def _client_hard_constraints(
    constraints: binding.ClientRootTravelConstraintSetV01,
) -> Mapping[str, Any]:
    return {
        "origin": constraints.origin,
        "destination": constraints.destination,
        "departure_date": constraints.departure_date,
        "return_date": constraints.return_date,
        "max_amount": constraints.max_amount,
        "currency": constraints.currency,
        "baggage_required": constraints.baggage_required,
        "avoid_overnight_layover": constraints.avoid_overnight_layover,
    }


def _client_soft_preferences(
    constraints: binding.ClientRootTravelConstraintSetV01,
) -> Mapping[str, Any]:
    return {
        "preferred_seat_characteristics": constraints.preferred_seat_characteristics,
        "changeable_preferred": constraints.changeable_preferred,
        "soft_preference_priority": constraints.soft_preference_priority,
    }


def _candidate_projection(
    snapshot: binding.AirlineRootOfferCandidateSetSnapshotV01,
) -> tuple[Mapping[str, Any], ...]:
    return tuple(
        {
            "offer_id": record.offer_id,
            "amount": record.amount,
            "currency": record.currency,
            "baggage_included": record.baggage_included,
            "seat_characteristics": record.seat_characteristics,
            "changeable": record.changeable,
            "overnight_layover": record.overnight_layover,
        }
        for record in sorted(
            snapshot.authoritative_offer_records,
            key=lambda item: item.offer_id,
        )
    )


def _actor_request(
    *,
    actor_id: str,
    selection_input: binding.AirlineSemanticSelectionInputV01,
    constraints: binding.ClientRootTravelConstraintSetV01,
    snapshot: binding.AirlineRootOfferCandidateSetSnapshotV01,
    proposed_offer_id: str,
) -> AirlineInjectedSemanticActorRequestV01:
    return AirlineInjectedSemanticActorRequestV01(
        request_id=(
            f"{selection_input.selection_input_id}:semantic_actor_request:{actor_id}"
        ),
        transaction_id=selection_input.transaction_id,
        actor_id=actor_id,
        actor_role=binding.REQUIRED_ACTOR_ROLES[actor_id],
        source_selection_input_id=selection_input.selection_input_id,
        source_bsep_projection_ref=selection_input.source_bsep_projection_ref,
        source_client_constraint_set_id=selection_input.source_client_constraint_set_id,
        source_candidate_set_ref=selection_input.source_candidate_set_ref,
        source_candidate_set_snapshot_id=(
            selection_input.source_candidate_set_snapshot_id
        ),
        source_candidate_set_digest=selection_input.source_candidate_set_digest,
        visible_candidate_ids=selection_input.visible_candidate_ids,
        airline_valid_candidate_ids=selection_input.airline_valid_candidate_ids,
        client_hard_compatible_candidate_ids=(
            selection_input.client_hard_compatible_candidate_ids
        ),
        soft_tradeoff_candidate_ids=selection_input.soft_tradeoff_candidate_ids,
        client_hard_constraints=_client_hard_constraints(constraints),
        client_soft_preferences=_client_soft_preferences(constraints),
        proposed_offer_id=proposed_offer_id,
        authoritative_candidate_projection=_candidate_projection(snapshot),
        provider_may_create_authority=False,
        provider_may_create_contract=False,
        provider_may_create_packet=False,
        provider_may_create_receipt=False,
        provider_may_execute_action=False,
        raw_secret_included=False,
    )


def _call_provider(
    *,
    semantic_provider: AirlineInjectedSemanticProviderV01,
    request: AirlineInjectedSemanticActorRequestV01,
) -> tuple[Mapping[str, Any], tuple[str, ...]]:
    try:
        payload = semantic_provider(request.actor_id, asdict(request))
    except Exception:
        return {}, (REASON_PROVIDER_CALL_FAILED,)
    if not isinstance(payload, Mapping):
        return {}, (binding.REASON_INVALID_PROVIDER_OUTPUT_CONTAINER,)
    return payload, ()


def _string_reason(value: Any, *, allow_empty: bool = False) -> tuple[str, ...]:
    if type(value) is not str:
        return (binding.REASON_INVALID_PROVIDER_OUTPUT_TYPE,)
    if not allow_empty and not value.strip():
        return (binding.REASON_EMPTY_PROVIDER_OUTPUT_FIELD,)
    return ()


def _string_tuple_reason(
    value: Any,
    *,
    allow_empty: bool = False,
) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)) or isinstance(value, str):
        return (binding.REASON_INVALID_PROVIDER_OUTPUT_TYPE,)
    if not allow_empty and not value:
        return (binding.REASON_EMPTY_PROVIDER_OUTPUT_FIELD,)
    for item in value:
        if type(item) is not str:
            return (binding.REASON_INVALID_PROVIDER_OUTPUT_TYPE,)
        if not item.strip():
            return (binding.REASON_EMPTY_PROVIDER_OUTPUT_FIELD,)
    return ()


def _bool_reason(value: Any) -> tuple[str, ...]:
    return () if type(value) is bool else (binding.REASON_INVALID_PROVIDER_OUTPUT_TYPE,)


def _zero_int_reason(value: Any) -> tuple[str, ...]:
    if type(value) is not int:
        return (binding.REASON_INVALID_PROVIDER_OUTPUT_TYPE,)
    if value != 0:
        return (binding.REASON_NONZERO_REAL_WORLD_EFFECTS,)
    return ()


def parse_injected_reviewer_response_v01(
    *,
    request: AirlineInjectedSemanticActorRequestV01,
    selection_input: binding.AirlineSemanticSelectionInputV01,
    proposed_offer_id: str,
    payload: Any,
) -> tuple[AirlineInjectedReviewerResponseV01 | None, tuple[str, ...]]:
    if not isinstance(payload, Mapping):
        return None, (binding.REASON_INVALID_PROVIDER_OUTPUT_CONTAINER,)

    allowed = set(AirlineInjectedReviewerResponseV01.__dataclass_fields__)
    fields = set(payload)
    reasons: list[str] = []
    missing = allowed - fields
    unknown = fields - allowed
    if missing:
        reasons.append(binding.REASON_MISSING_PROVIDER_OUTPUT_FIELD)
    if unknown:
        reasons.append(binding.REASON_UNKNOWN_PROVIDER_OUTPUT_FIELD)
    if reasons:
        return None, _dedupe(reasons)

    for field in (
        "response_id",
        "transaction_id",
        "actor_id",
        "source_request_id",
        "source_selection_input_id",
        "source_candidate_set_snapshot_id",
        "source_candidate_set_digest",
        "reviewed_offer_id",
        "review_role",
        "review_status",
        "validation_status",
    ):
        reasons.extend(_string_reason(payload[field]))
    reasons.extend(_string_tuple_reason(payload["semantic_factors"]))
    reasons.extend(_string_tuple_reason(payload["blocking_conflicts"], allow_empty=True))
    for field in (
        "supports_proposed_offer",
        "raw_output_used",
        "authority_created",
        "permission_created",
    ):
        reasons.extend(_bool_reason(payload[field]))
    reasons.extend(_zero_int_reason(payload["real_world_effects_count"]))
    if reasons:
        return None, _dedupe(reasons)

    response = AirlineInjectedReviewerResponseV01(
        response_id=payload["response_id"],
        transaction_id=payload["transaction_id"],
        actor_id=payload["actor_id"],
        source_request_id=payload["source_request_id"],
        source_selection_input_id=payload["source_selection_input_id"],
        source_candidate_set_snapshot_id=payload["source_candidate_set_snapshot_id"],
        source_candidate_set_digest=payload["source_candidate_set_digest"],
        reviewed_offer_id=payload["reviewed_offer_id"],
        review_role=payload["review_role"],
        review_status=payload["review_status"],
        semantic_factors=tuple(payload["semantic_factors"]),
        blocking_conflicts=tuple(payload["blocking_conflicts"]),
        supports_proposed_offer=payload["supports_proposed_offer"],
        validation_status=payload["validation_status"],
        raw_output_used=payload["raw_output_used"],
        authority_created=payload["authority_created"],
        permission_created=payload["permission_created"],
        real_world_effects_count=payload["real_world_effects_count"],
    )

    if response.transaction_id != selection_input.transaction_id:
        reasons.append(binding.REASON_WRONG_TRANSACTION_ID)
    if response.actor_id != request.actor_id:
        reasons.append(binding.REASON_ACTOR_ROLE_MISMATCH)
    if response.review_role != request.actor_role:
        reasons.append(binding.REASON_ACTOR_ROLE_MISMATCH)
    if response.source_request_id != request.request_id:
        reasons.append(binding.REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH)
    if response.source_selection_input_id != selection_input.selection_input_id:
        reasons.append(binding.REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH)
    if (
        response.source_candidate_set_snapshot_id
        != selection_input.source_candidate_set_snapshot_id
        or response.source_candidate_set_digest
        != selection_input.source_candidate_set_digest
    ):
        reasons.append(binding.REASON_SELECTION_INPUT_SNAPSHOT_MISMATCH)
    if response.reviewed_offer_id != proposed_offer_id:
        reasons.append(binding.REASON_MULTI_ACTOR_CONFLICT)
    if response.review_status != binding.STATUS_PASS:
        reasons.append(binding.REASON_ACTOR_OUTPUT_NOT_VALIDATED)
    if response.validation_status != binding.STATUS_PASS:
        reasons.append(binding.REASON_ACTOR_OUTPUT_NOT_VALIDATED)
    if response.blocking_conflicts:
        reasons.append(binding.REASON_MULTI_ACTOR_CONFLICT)
    if not response.supports_proposed_offer:
        reasons.append(binding.REASON_ACTOR_OUTPUT_NOT_VALIDATED)
    if response.raw_output_used:
        reasons.append(binding.REASON_ACTOR_OUTPUT_NOT_VALIDATED)
    if response.authority_created:
        reasons.append(binding.REASON_PROVIDER_CLAIMED_AUTHORITY)
    if response.permission_created:
        reasons.append(binding.REASON_PROVIDER_CLAIMED_ACTION)
    if response.real_world_effects_count != 0:
        reasons.append(binding.REASON_NONZERO_REAL_WORLD_EFFECTS)

    if reasons:
        return None, _dedupe(reasons)
    return response, ()


def _review_from_response(
    response: AirlineInjectedReviewerResponseV01,
) -> binding.AirlineCanonicalActorSelectionReviewV01:
    return binding.AirlineCanonicalActorSelectionReviewV01(
        canonical_actor_output_id=response.response_id,
        transaction_id=response.transaction_id,
        actor_id=response.actor_id,
        source_selection_input_id=response.source_selection_input_id,
        source_candidate_set_snapshot_id=response.source_candidate_set_snapshot_id,
        source_candidate_set_digest=response.source_candidate_set_digest,
        reviewed_offer_id=response.reviewed_offer_id,
        review_role=response.review_role,
        review_status=response.review_status,
        semantic_factors=response.semantic_factors,
        blocking_conflicts=response.blocking_conflicts,
        supports_proposed_offer=response.supports_proposed_offer,
        validation_status=response.validation_status,
        raw_output_used=response.raw_output_used,
        authority_created=response.authority_created,
        permission_created=response.permission_created,
        real_world_effects_count=response.real_world_effects_count,
    )


def _proposer_review_from_proposal(
    proposal: binding.AirlineSemanticOfferSelectionProposalV01,
) -> binding.AirlineCanonicalActorSelectionReviewV01:
    return binding.AirlineCanonicalActorSelectionReviewV01(
        canonical_actor_output_id=(
            f"canonical_actor_output:{proposal.actor_id}:{proposal.proposal_id}"
        ),
        transaction_id=proposal.transaction_id,
        actor_id=proposal.actor_id,
        source_selection_input_id=proposal.source_selection_input_id,
        source_candidate_set_snapshot_id=proposal.source_candidate_set_snapshot_id,
        source_candidate_set_digest=proposal.source_candidate_set_digest,
        reviewed_offer_id=proposal.recommended_offer_id,
        review_role=binding.REQUIRED_ACTOR_ROLES[proposal.actor_id],
        review_status=binding.STATUS_PASS,
        semantic_factors=(
            proposal.decision_factors
            + proposal.preference_matches
            + proposal.uncertainty_notes
        ),
        blocking_conflicts=(),
        supports_proposed_offer=True,
        validation_status=binding.STATUS_PASS,
        raw_output_used=False,
        authority_created=False,
        permission_created=False,
        real_world_effects_count=0,
    )


def project_airline_hold_packet_from_resolution_v01(
    resolution: binding.AirlineRootSelectedOfferResolutionV01,
) -> corridor_contracts.AirlineHoldCommitPacketV01:
    suffix = resolution.selected_offer_id.rsplit(":", 1)[-1]
    base = corridor_contracts.build_valid_airline_hold_commit_packet_v01()
    return replace(
        base,
        packet_id=f"airline_hold_commit_packet:semantic_causal:{suffix}",
        parent_offer_packet_id=f"airline_offer_packet:semantic_causal:{suffix}",
        transaction_id=resolution.transaction_id,
        created_by=binding.AIRLINE_ROOT_ID,
        root_owner=binding.AIRLINE_ROOT_ID,
        airline_root_id=binding.AIRLINE_ROOT_ID,
        offer_id=resolution.selected_offer_id,
        hold_id=f"hold:semantic_causal:{suffix}",
        route_ref=resolution.resolved_route_ref,
        passenger_ref=corridor_contracts.PASSENGER_REF,
        amount=resolution.resolved_amount,
        currency=resolution.resolved_currency,
        ttl_seconds=resolution.resolved_ttl,
        expired=False,
        idempotency_key=f"idem:semantic_causal_hold:{suffix}",
        allowed_action=corridor_contracts.ACTION_MOCK_OFFER_HOLD,
        allowed_adapters=(corridor_contracts.ADAPTER_AIRLINE_HOLD_SANDBOX,),
        forbidden_actions=(
            corridor_contracts.ACTION_REAL_PAYMENT,
            corridor_contracts.ACTION_REAL_TICKET_ISSUE,
            corridor_contracts.ACTION_REAL_BOOKING,
            corridor_contracts.ACTION_REAL_AIRLINE_API,
            corridor_contracts.ACTION_REAL_BANK_API,
            corridor_contracts.ACTION_REAL_GDS_API,
            corridor_contracts.ACTION_POST_ROOT_LLM_REASONING,
        ),
        real_world_effects_allowed=False,
    )


def _call_record(
    *,
    call_index: int,
    request: AirlineInjectedSemanticActorRequestV01,
    provider_returned: bool,
    validation_status: str,
    reason_codes: tuple[str, ...],
) -> AirlineSemanticProviderCallRecordV01:
    return AirlineSemanticProviderCallRecordV01(
        call_index=call_index,
        actor_id=request.actor_id,
        actor_role=request.actor_role,
        request_id=request.request_id,
        proposed_offer_id=request.proposed_offer_id,
        provider_returned=provider_returned,
        validation_status=validation_status,
        reason_codes=reason_codes,
    )


def _provider_created_authority_count(
    proposal: binding.AirlineSemanticOfferSelectionProposalV01 | None,
    reviewer_responses: tuple[AirlineInjectedReviewerResponseV01, ...],
) -> int:
    proposal_count = 1 if proposal is not None and proposal.authority_created else 0
    return proposal_count + sum(1 for response in reviewer_responses if response.authority_created)


def _provider_created_contract_count(
    proposal: binding.AirlineSemanticOfferSelectionProposalV01 | None,
) -> int:
    if proposal is None:
        return 0
    return sum(
        1
        for value in (
            proposal.packet_created,
            proposal.receipt_created,
            proposal.payment_created,
            proposal.ticket_created,
            proposal.booking_created,
            proposal.final_output_created,
        )
        if value
    )


def _selection_input_from_report(
    report: AirlineSemanticCausalRunReportV01,
) -> binding.AirlineSemanticSelectionInputV01 | None:
    request = report.proposer_request
    if request is None:
        return None
    return binding.AirlineSemanticSelectionInputV01(
        selection_input_id=request.source_selection_input_id,
        transaction_id=request.transaction_id,
        source_bsep_projection_ref=request.source_bsep_projection_ref,
        source_client_constraint_set_id=request.source_client_constraint_set_id,
        source_candidate_set_ref=request.source_candidate_set_ref,
        source_candidate_set_snapshot_id=request.source_candidate_set_snapshot_id,
        source_candidate_set_digest=request.source_candidate_set_digest,
        visible_candidate_ids=request.visible_candidate_ids,
        airline_valid_candidate_ids=request.airline_valid_candidate_ids,
        client_hard_compatible_candidate_ids=request.client_hard_compatible_candidate_ids,
        soft_tradeoff_candidate_ids=request.soft_tradeoff_candidate_ids,
        raw_secret_included=False,
        provider_authority_created=False,
        real_world_effects_count=0,
    )


def _nested_transaction_ids(
    report: AirlineSemanticCausalRunReportV01,
) -> tuple[str, ...]:
    values: list[str] = [report.transaction_id]
    if report.proposer_request is not None:
        values.append(report.proposer_request.transaction_id)
    values.extend(request.transaction_id for request in report.reviewer_request_records)
    values.extend(record.actor_id and report.transaction_id for record in report.provider_call_records)
    if report.proposal is not None:
        values.append(report.proposal.transaction_id)
    values.extend(review.transaction_id for review in report.actor_reviews)
    if report.synthesis is not None:
        values.append(report.synthesis.transaction_id)
    if report.canonical_evidence is not None:
        values.append(report.canonical_evidence.transaction_id)
    if report.client_root_decision is not None:
        values.append(report.client_root_decision.transaction_id)
    if report.airline_root_resolution is not None:
        values.append(report.airline_root_resolution.transaction_id)
    if report.hold_packet is not None:
        values.append(report.hold_packet.transaction_id)
    if report.hold_binding is not None:
        values.append(report.hold_binding.transaction_id)
    if report.causal_binding_report is not None:
        values.append(report.causal_binding_report.transaction_id)
    return tuple(value for value in values if value)


def _fail_stage_index(stage: str) -> int:
    stages = (
        STAGE_BSEP,
        STAGE_CONSTRAINTS,
        STAGE_SNAPSHOT,
        STAGE_SELECTION_INPUT,
        STAGE_PROPOSER_CALL,
        STAGE_PROPOSAL_VALIDATION,
        STAGE_PROPOSER_REVIEW,
        STAGE_REVIEWER_CALLS,
        STAGE_ACTOR_REVIEWS,
        STAGE_SYNTHESIS,
        STAGE_CANONICAL_EVIDENCE,
        STAGE_CLIENT_ROOT_DECISION,
        STAGE_AIRLINE_ROOT_RESOLUTION,
        STAGE_HOLD_BINDING,
        STAGE_BINDING_REPORT,
        STAGE_LOCAL_CHAIN,
    )
    try:
        return stages.index(stage)
    except ValueError:
        return -1


def _later_artifact_survived_after_failure(
    report: AirlineSemanticCausalRunReportV01,
) -> bool:
    failed = _fail_stage_index(report.failed_stage)
    if failed < 0:
        return True
    if report.proposal is not None and _fail_stage_index(STAGE_PROPOSAL_VALIDATION) > failed:
        return True
    if (
        report.reviewer_request_records
        and _fail_stage_index(STAGE_REVIEWER_CALLS) > failed
    ):
        return True
    if (
        report.reviewer_responses
        and _fail_stage_index(STAGE_REVIEWER_CALLS) > failed
    ):
        return True
    if failed < _fail_stage_index(STAGE_PROPOSER_REVIEW) and report.actor_reviews:
        return True
    if (
        failed < _fail_stage_index(STAGE_ACTOR_REVIEWS)
        and len(report.actor_reviews) > 1
    ):
        return True
    artifact_stages = (
        (STAGE_SYNTHESIS, report.synthesis),
        (STAGE_CANONICAL_EVIDENCE, report.canonical_evidence),
        (STAGE_CLIENT_ROOT_DECISION, report.client_root_decision),
        (STAGE_AIRLINE_ROOT_RESOLUTION, report.airline_root_resolution),
        (STAGE_HOLD_BINDING, report.hold_packet),
        (STAGE_HOLD_BINDING, report.hold_binding),
        (STAGE_BINDING_REPORT, report.causal_binding_report),
    )
    return any(
        artifact is not None and _fail_stage_index(stage) > failed
        for stage, artifact in artifact_stages
    )


def _request_lineage_tuple(
    request: AirlineInjectedSemanticActorRequestV01,
) -> tuple[Any, ...]:
    return (
        request.client_hard_constraints,
        request.client_soft_preferences,
        request.source_client_constraint_set_id,
        request.source_selection_input_id,
        request.source_bsep_projection_ref,
        request.source_candidate_set_ref,
        request.source_candidate_set_snapshot_id,
        request.source_candidate_set_digest,
    )


def _reviewer_request_content_matches_proposer(
    proposer_request: AirlineInjectedSemanticActorRequestV01,
    reviewer_requests: tuple[AirlineInjectedSemanticActorRequestV01, ...],
) -> bool:
    proposer_lineage = _request_lineage_tuple(proposer_request)
    return all(
        _request_lineage_tuple(request) == proposer_lineage
        for request in reviewer_requests
    )


def _call_record_matches_request(
    record: AirlineSemanticProviderCallRecordV01,
    request: AirlineInjectedSemanticActorRequestV01,
) -> bool:
    return (
        record.actor_id == request.actor_id
        and record.actor_role == request.actor_role
        and record.request_id == request.request_id
        and record.proposed_offer_id == request.proposed_offer_id
    )


def validate_airline_semantic_causal_run_report_v01(
    report: AirlineSemanticCausalRunReportV01,
) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if (
        report.run_id != RUN_ID
        or report.slice_id != SLICE_ID
        or report.next_gate != NEXT_GATE
    ):
        reasons.append(REASON_CAUSAL_RUN_REPORT_IDENTITY_MISMATCH)
    if len(set(_nested_transaction_ids(report))) != 1:
        reasons.append(REASON_CAUSAL_RUN_REPORT_IDENTITY_MISMATCH)

    if report.final_status == STATUS_LOCAL_MODEL_PASS:
        selection_input = _selection_input_from_report(report)
        if selection_input is None:
            reasons.append(REASON_CAUSAL_RUN_REPORT_IDENTITY_MISMATCH)
        if (
            report.provider_call_count != 5
            or len(report.provider_call_records) != 5
            or tuple(record.call_index for record in report.provider_call_records)
            != (1, 2, 3, 4, 5)
        ):
            reasons.append(REASON_CAUSAL_RUN_PROVIDER_CALL_SHAPE_MISMATCH)
        if tuple(record.actor_id for record in report.provider_call_records) != ACTOR_ORDER:
            reasons.append(REASON_CAUSAL_RUN_ACTOR_ORDER_MISMATCH)
        if any(
            not record.provider_returned
            or record.validation_status != binding.STATUS_PASS
            or record.reason_codes
            for record in report.provider_call_records
        ):
            reasons.append(REASON_CAUSAL_RUN_PROVIDER_CALL_SHAPE_MISMATCH)
        if report.proposer_request is None or report.proposer_request.proposed_offer_id:
            reasons.append(REASON_CAUSAL_RUN_PROVIDER_CALL_SHAPE_MISMATCH)
        elif (
            report.client_constraint_set_id
            != report.proposer_request.source_client_constraint_set_id
        ):
            reasons.append(REASON_CAUSAL_RUN_REPORT_IDENTITY_MISMATCH)
        if report.proposer_request is not None:
            if (
                report.hard_constraint_fingerprint
                != hard_constraint_fingerprint_from_request_v01(
                    report.proposer_request,
                )
            ):
                reasons.append(
                    REASON_CAUSAL_RUN_HARD_CONSTRAINT_FINGERPRINT_MISMATCH,
                )
            if (
                report.soft_preference_fingerprint
                != soft_preference_fingerprint_from_request_v01(
                    report.proposer_request,
                )
            ):
                reasons.append(
                    REASON_CAUSAL_RUN_SOFT_PREFERENCE_FINGERPRINT_MISMATCH,
                )
            if not _reviewer_request_content_matches_proposer(
                report.proposer_request,
                report.reviewer_request_records,
            ):
                reasons.append(REASON_CAUSAL_RUN_REQUEST_CONTENT_MISMATCH)
        if (
            len(report.reviewer_request_records) != 4
            or len(report.reviewer_responses) != 4
            or len(report.actor_reviews) != 5
        ):
            reasons.append(REASON_CAUSAL_RUN_PROVIDER_CALL_SHAPE_MISMATCH)
        if report.proposer_request is not None and report.provider_call_records:
            if not _call_record_matches_request(
                report.provider_call_records[0],
                report.proposer_request,
            ):
                reasons.append(REASON_CAUSAL_RUN_CALL_RECORD_REQUEST_MISMATCH)
        if report.proposal is None:
            reasons.append(REASON_CAUSAL_RUN_CHAIN_VALIDATION_FAILED)
        elif selection_input is not None:
            reasons.extend(
                binding.validate_airline_semantic_offer_selection_proposal_v01(
                    selection_input,
                    report.proposal,
                ).reason_codes,
            )
            if any(
                request.proposed_offer_id != report.proposal.recommended_offer_id
                for request in report.reviewer_request_records
            ):
                reasons.append(REASON_CAUSAL_RUN_PROVIDER_CALL_SHAPE_MISMATCH)
            if report.proposal.source_selection_input_id != selection_input.selection_input_id:
                reasons.append(REASON_CAUSAL_RUN_REPORT_IDENTITY_MISMATCH)
            if report.proposal.candidate_set_ref != selection_input.source_candidate_set_ref:
                reasons.append(REASON_CAUSAL_RUN_REPORT_IDENTITY_MISMATCH)
            if (
                report.provider_call_records
                and report.provider_call_records[0].actor_id != report.proposal.actor_id
            ):
                reasons.append(REASON_CAUSAL_RUN_CALL_RECORD_REQUEST_MISMATCH)
        if (
            len(report.reviewer_request_records) == 4
            and len(report.reviewer_responses) == 4
            and len(report.provider_call_records) == 5
            and len(report.actor_reviews) == 5
        ):
            for index, (request, response, review) in enumerate(
                zip(
                    report.reviewer_request_records,
                    report.reviewer_responses,
                    report.actor_reviews[1:],
                ),
                start=1,
            ):
                call_record = report.provider_call_records[index]
                if not _call_record_matches_request(call_record, request):
                    reasons.append(REASON_CAUSAL_RUN_CALL_RECORD_REQUEST_MISMATCH)
                if (
                    response.actor_id != request.actor_id
                    or response.source_request_id != request.request_id
                    or response.source_selection_input_id
                    != request.source_selection_input_id
                    or response.reviewed_offer_id != request.proposed_offer_id
                ):
                    reasons.append(REASON_CAUSAL_RUN_RESPONSE_REQUEST_MISMATCH)
                if review != _review_from_response(response):
                    reasons.append(REASON_CAUSAL_RUN_RESPONSE_REVIEW_MISMATCH)
        if len(report.actor_reviews) != 5:
            reasons.append(REASON_CAUSAL_RUN_CHAIN_VALIDATION_FAILED)
        elif selection_input is not None:
            for review in report.actor_reviews:
                reasons.extend(
                    binding.validate_airline_canonical_actor_selection_review_v01(
                        selection_input,
                        review,
                    ).reason_codes,
                )
        if report.synthesis is None or selection_input is None:
            reasons.append(REASON_CAUSAL_RUN_CHAIN_VALIDATION_FAILED)
        else:
            reasons.extend(
                binding.validate_airline_semantic_selection_synthesis_report_v01(
                    selection_input,
                    report.actor_reviews,
                    report.synthesis,
                ).reason_codes,
            )
        if (
            report.canonical_evidence is None
            or report.proposal is None
            or report.synthesis is None
            or selection_input is None
        ):
            reasons.append(REASON_CAUSAL_RUN_CHAIN_VALIDATION_FAILED)
        else:
            reasons.extend(
                binding.validate_validated_airline_semantic_selection_evidence_v01(
                    selection_input,
                    report.proposal,
                    report.actor_reviews,
                    report.synthesis,
                    report.canonical_evidence,
                ).reason_codes,
            )
        if (
            report.client_root_decision is None
            or report.canonical_evidence is None
            or selection_input is None
        ):
            reasons.append(REASON_CAUSAL_RUN_CHAIN_VALIDATION_FAILED)
        else:
            reasons.extend(
                binding.validate_client_root_offer_selection_decision_v01(
                    selection_input,
                    report.canonical_evidence,
                    report.client_root_decision,
                ).reason_codes,
            )
        if (
            report.airline_root_resolution is None
            or report.hold_packet is None
            or report.hold_binding is None
            or report.causal_binding_report is None
        ):
            reasons.append(REASON_CAUSAL_RUN_CHAIN_VALIDATION_FAILED)
        if report.hold_binding is not None and report.hold_packet is not None and report.airline_root_resolution is not None:
            reasons.extend(
                binding.validate_airline_semantic_hold_contract_binding_v01(
                    report.airline_root_resolution,
                    report.hold_packet,
                    report.hold_binding,
                ).reason_codes,
            )
        if report.causal_binding_report is not None:
            reasons.extend(
                binding.validate_airline_semantic_to_contract_binding_report_v01(
                    report.causal_binding_report,
                ).reason_codes,
            )
        if (
            report.local_chain_validation is None
            or report.local_chain_validation.validation_status
            != binding.STATUS_LOCAL_MODEL_PASS
        ):
            reasons.append(REASON_CAUSAL_RUN_CHAIN_VALIDATION_FAILED)

        expected_semantic = (
            report.proposal.recommended_offer_id if report.proposal is not None else ""
        )
        expected_root = (
            report.client_root_decision.selected_offer_id
            if report.client_root_decision is not None
            else ""
        )
        expected_hold = report.hold_packet.offer_id if report.hold_packet is not None else ""
        expected_authority_count = _provider_created_authority_count(
            report.proposal,
            report.reviewer_responses,
        )
        expected_contract_count = _provider_created_contract_count(report.proposal)
        if (
            report.semantic_recommendation_id != expected_semantic
            or report.root_selected_offer_id != expected_root
            or report.hold_contract_offer_id != expected_hold
            or report.semantic_to_root_binding_match
            != (expected_semantic != "" and expected_semantic == expected_root)
            or report.root_to_hold_binding_match
            != (expected_root != "" and expected_root == expected_hold)
            or report.provider_created_authority_count != expected_authority_count
            or report.provider_created_contract_count != expected_contract_count
            or report.provider_call_count != len(report.provider_call_records)
        ):
            reasons.append(REASON_CAUSAL_RUN_DERIVED_FIELD_MISMATCH)
        if (
            report.default_offer_used
            or report.silent_fallback_used
            or report.runtime_receipt_created_count != 0
            or report.corridor_execution_count != 0
            or report.provider_network_call_count != 0
            or report.gemini_call_count != 0
            or report.real_world_effects_count != 0
        ):
            reasons.append(REASON_CAUSAL_RUN_COUNTER_MISMATCH)
    elif report.final_status == STATUS_FAIL_CLOSED:
        if not report.failed_stage or not report.validation_errors:
            reasons.append(REASON_CAUSAL_RUN_CHAIN_VALIDATION_FAILED)
        if report.hold_packet is not None or report.hold_binding is not None:
            reasons.append(REASON_CAUSAL_RUN_DOWNSTREAM_ARTIFACT_AFTER_FAILURE)
        if _later_artifact_survived_after_failure(report):
            reasons.append(REASON_CAUSAL_RUN_DOWNSTREAM_ARTIFACT_AFTER_FAILURE)
        if (
            report.runtime_receipt_created_count != 0
            or report.corridor_execution_count != 0
            or report.provider_network_call_count != 0
            or report.gemini_call_count != 0
            or report.real_world_effects_count != 0
        ):
            reasons.append(REASON_CAUSAL_RUN_COUNTER_MISMATCH)
    else:
        reasons.append(REASON_CAUSAL_RUN_REPORT_IDENTITY_MISMATCH)

    return not reasons, _dedupe(reasons)


def _run_report(
    *,
    scenario_id: str,
    final_status: str,
    failed_stage: str,
    constraints: binding.ClientRootTravelConstraintSetV01,
    snapshot: binding.AirlineRootOfferCandidateSetSnapshotV01,
    provider_call_records: tuple[AirlineSemanticProviderCallRecordV01, ...],
    proposer_request: AirlineInjectedSemanticActorRequestV01 | None,
    proposer_payload: Mapping[str, Any],
    proposal: binding.AirlineSemanticOfferSelectionProposalV01 | None,
    reviewer_request_records: tuple[AirlineInjectedSemanticActorRequestV01, ...],
    reviewer_responses: tuple[AirlineInjectedReviewerResponseV01, ...],
    actor_reviews: tuple[binding.AirlineCanonicalActorSelectionReviewV01, ...],
    synthesis: binding.AirlineSemanticSelectionSynthesisReportV01 | None,
    canonical_evidence: binding.ValidatedAirlineSemanticSelectionEvidenceV01 | None,
    client_root_decision: binding.ClientRootOfferSelectionDecisionV01 | None,
    airline_root_resolution: binding.AirlineRootSelectedOfferResolutionV01 | None,
    hold_packet: corridor_contracts.AirlineHoldCommitPacketV01 | None,
    hold_binding: binding.AirlineSemanticHoldContractBindingV01 | None,
    causal_binding_report: binding.AirlineSemanticToContractBindingReportV01 | None,
    local_chain_validation: binding.AirlineSemanticToContractValidationReportV01 | None,
    validation_errors: tuple[str, ...],
) -> AirlineSemanticCausalRunReportV01:
    semantic_recommendation_id = (
        proposal.recommended_offer_id if proposal is not None else ""
    )
    root_selected_offer_id = (
        client_root_decision.selected_offer_id
        if client_root_decision is not None
        else ""
    )
    hold_contract_offer_id = hold_packet.offer_id if hold_packet is not None else ""
    hard_fingerprint = (
        hard_constraint_fingerprint_from_request_v01(proposer_request)
        if proposer_request is not None
        else _hard_constraint_fingerprint(constraints)
    )
    soft_fingerprint = (
        soft_preference_fingerprint_from_request_v01(proposer_request)
        if proposer_request is not None
        else _soft_preference_fingerprint(constraints)
    )
    return AirlineSemanticCausalRunReportV01(
        run_id=RUN_ID,
        slice_id=SLICE_ID,
        scenario_id=scenario_id,
        final_status=final_status,
        failed_stage=failed_stage,
        transaction_id=constraints.transaction_id,
        client_constraint_set_id=constraints.constraint_set_id,
        candidate_set_snapshot_id=snapshot.candidate_set_snapshot_id,
        candidate_set_digest=snapshot.candidate_set_digest,
        soft_preference_fingerprint=soft_fingerprint,
        hard_constraint_fingerprint=hard_fingerprint,
        provider_call_records=provider_call_records,
        provider_call_count=len(provider_call_records),
        proposer_request=proposer_request,
        proposer_payload=proposer_payload,
        proposal=proposal,
        reviewer_request_records=reviewer_request_records,
        reviewer_responses=reviewer_responses,
        actor_reviews=actor_reviews,
        synthesis=synthesis,
        canonical_evidence=canonical_evidence,
        client_root_decision=client_root_decision,
        airline_root_resolution=airline_root_resolution,
        hold_packet=hold_packet,
        hold_binding=hold_binding,
        causal_binding_report=causal_binding_report,
        local_chain_validation=local_chain_validation,
        semantic_recommendation_id=semantic_recommendation_id,
        root_selected_offer_id=root_selected_offer_id,
        hold_contract_offer_id=hold_contract_offer_id,
        semantic_to_root_binding_match=(
            semantic_recommendation_id != ""
            and semantic_recommendation_id == root_selected_offer_id
        ),
        root_to_hold_binding_match=(
            root_selected_offer_id != ""
            and root_selected_offer_id == hold_contract_offer_id
        ),
        default_offer_used=False,
        silent_fallback_used=False,
        provider_created_authority_count=_provider_created_authority_count(
            proposal,
            reviewer_responses,
        ),
        provider_created_contract_count=_provider_created_contract_count(proposal),
        runtime_receipt_created_count=0,
        corridor_execution_count=0,
        provider_network_call_count=0,
        gemini_call_count=0,
        real_world_effects_count=0,
        validation_errors=_dedupe(validation_errors),
        next_gate=NEXT_GATE,
    )


def _fail_run(
    *,
    scenario_id: str,
    failed_stage: str,
    constraints: binding.ClientRootTravelConstraintSetV01,
    snapshot: binding.AirlineRootOfferCandidateSetSnapshotV01,
    provider_call_records: tuple[AirlineSemanticProviderCallRecordV01, ...] = (),
    proposer_request: AirlineInjectedSemanticActorRequestV01 | None = None,
    proposer_payload: Mapping[str, Any] | None = None,
    proposal: binding.AirlineSemanticOfferSelectionProposalV01 | None = None,
    reviewer_request_records: tuple[AirlineInjectedSemanticActorRequestV01, ...] = (),
    reviewer_responses: tuple[AirlineInjectedReviewerResponseV01, ...] = (),
    actor_reviews: tuple[binding.AirlineCanonicalActorSelectionReviewV01, ...] = (),
    synthesis: binding.AirlineSemanticSelectionSynthesisReportV01 | None = None,
    canonical_evidence: binding.ValidatedAirlineSemanticSelectionEvidenceV01 | None = None,
    client_root_decision: binding.ClientRootOfferSelectionDecisionV01 | None = None,
    airline_root_resolution: binding.AirlineRootSelectedOfferResolutionV01 | None = None,
    local_chain_validation: binding.AirlineSemanticToContractValidationReportV01 | None = None,
    validation_errors: tuple[str, ...] | list[str] = (),
) -> AirlineSemanticCausalRunReportV01:
    return _run_report(
        scenario_id=scenario_id,
        final_status=STATUS_FAIL_CLOSED,
        failed_stage=failed_stage,
        constraints=constraints,
        snapshot=snapshot,
        provider_call_records=provider_call_records,
        proposer_request=proposer_request,
        proposer_payload=proposer_payload or {},
        proposal=proposal,
        reviewer_request_records=reviewer_request_records,
        reviewer_responses=reviewer_responses,
        actor_reviews=actor_reviews,
        synthesis=synthesis,
        canonical_evidence=canonical_evidence,
        client_root_decision=client_root_decision,
        airline_root_resolution=airline_root_resolution,
        hold_packet=None,
        hold_binding=None,
        causal_binding_report=None,
        local_chain_validation=local_chain_validation,
        validation_errors=_dedupe(validation_errors),
    )


def collect_airline_semantic_to_contract_causal_run_v01(
    *,
    scenario_id: str,
    constraints: binding.ClientRootTravelConstraintSetV01,
    semantic_provider: AirlineInjectedSemanticProviderV01,
    snapshot: binding.AirlineRootOfferCandidateSetSnapshotV01 | None = None,
    bsep_projection: binding.AirlineBSEPProjectionRefV01 | None = None,
) -> AirlineSemanticCausalRunReportV01:
    actual_snapshot = snapshot or binding.build_airline_candidate_snapshot_v01()
    actual_bsep = bsep_projection or binding.build_valid_airline_bsep_projection_ref_v01()
    provider_call_records: list[AirlineSemanticProviderCallRecordV01] = []

    bsep_report = binding.validate_airline_bsep_projection_ref_v01(actual_bsep)
    if bsep_report.validation_status != binding.STATUS_PASS:
        return _fail_run(
            scenario_id=scenario_id,
            failed_stage=STAGE_BSEP,
            constraints=constraints,
            snapshot=actual_snapshot,
            local_chain_validation=bsep_report,
            validation_errors=bsep_report.reason_codes,
        )

    constraints_report = binding.validate_client_root_travel_constraint_set_v01(
        constraints,
    )
    if constraints_report.validation_status != binding.STATUS_PASS:
        return _fail_run(
            scenario_id=scenario_id,
            failed_stage=STAGE_CONSTRAINTS,
            constraints=constraints,
            snapshot=actual_snapshot,
            local_chain_validation=constraints_report,
            validation_errors=constraints_report.reason_codes,
        )

    snapshot_report = binding.validate_airline_candidate_snapshot_v01(actual_snapshot)
    if snapshot_report.validation_status != binding.STATUS_PASS:
        return _fail_run(
            scenario_id=scenario_id,
            failed_stage=STAGE_SNAPSHOT,
            constraints=constraints,
            snapshot=actual_snapshot,
            local_chain_validation=snapshot_report,
            validation_errors=snapshot_report.reason_codes,
        )

    selection_input = binding.build_selection_input_v01(
        actual_bsep,
        constraints,
        actual_snapshot,
    )
    selection_report = binding.validate_airline_semantic_selection_input_v01(
        actual_bsep,
        constraints,
        actual_snapshot,
        selection_input,
    )
    if selection_report.validation_status != binding.STATUS_PASS:
        return _fail_run(
            scenario_id=scenario_id,
            failed_stage=STAGE_SELECTION_INPUT,
            constraints=constraints,
            snapshot=actual_snapshot,
            local_chain_validation=selection_report,
            validation_errors=selection_report.reason_codes,
        )

    proposer_request = _actor_request(
        actor_id=ACTOR_ORDER[0],
        selection_input=selection_input,
        constraints=constraints,
        snapshot=actual_snapshot,
        proposed_offer_id="",
    )
    proposer_payload, call_reasons = _call_provider(
        semantic_provider=semantic_provider,
        request=proposer_request,
    )
    if call_reasons:
        provider_call_records.append(
            _call_record(
                call_index=1,
                request=proposer_request,
                provider_returned=False,
                validation_status=STATUS_FAIL_CLOSED,
                reason_codes=call_reasons,
            ),
        )
        return _fail_run(
            scenario_id=scenario_id,
            failed_stage=STAGE_PROPOSER_CALL,
            constraints=constraints,
            snapshot=actual_snapshot,
            provider_call_records=tuple(provider_call_records),
            proposer_request=proposer_request,
            validation_errors=call_reasons,
        )

    proposal, proposal_report = (
        binding.build_airline_semantic_offer_selection_proposal_from_payload_v01(
            selection_input,
            proposer_payload,
        )
    )
    provider_call_records.append(
        _call_record(
            call_index=1,
            request=proposer_request,
            provider_returned=True,
            validation_status=proposal_report.validation_status,
            reason_codes=proposal_report.reason_codes,
        ),
    )
    if proposal is None or proposal_report.validation_status != binding.STATUS_PASS:
        return _fail_run(
            scenario_id=scenario_id,
            failed_stage=STAGE_PROPOSAL_VALIDATION,
            constraints=constraints,
            snapshot=actual_snapshot,
            provider_call_records=tuple(provider_call_records),
            proposer_request=proposer_request,
            proposer_payload=proposer_payload,
            validation_errors=proposal_report.reason_codes,
        )

    proposer_review = _proposer_review_from_proposal(proposal)
    proposer_review_report = binding.validate_airline_canonical_actor_selection_review_v01(
        selection_input,
        proposer_review,
    )
    if proposer_review_report.validation_status != binding.STATUS_PASS:
        return _fail_run(
            scenario_id=scenario_id,
            failed_stage=STAGE_PROPOSER_REVIEW,
            constraints=constraints,
            snapshot=actual_snapshot,
            provider_call_records=tuple(provider_call_records),
            proposer_request=proposer_request,
            proposer_payload=proposer_payload,
            proposal=proposal,
            actor_reviews=(proposer_review,),
            local_chain_validation=proposer_review_report,
            validation_errors=proposer_review_report.reason_codes,
        )

    reviewer_request_records: list[AirlineInjectedSemanticActorRequestV01] = []
    reviewer_responses: list[AirlineInjectedReviewerResponseV01] = []
    actor_reviews: list[binding.AirlineCanonicalActorSelectionReviewV01] = [
        proposer_review,
    ]

    for call_index, actor_id in enumerate(ACTOR_ORDER[1:], start=2):
        request = _actor_request(
            actor_id=actor_id,
            selection_input=selection_input,
            constraints=constraints,
            snapshot=actual_snapshot,
            proposed_offer_id=proposal.recommended_offer_id,
        )
        reviewer_request_records.append(request)
        payload, reviewer_call_reasons = _call_provider(
            semantic_provider=semantic_provider,
            request=request,
        )
        if reviewer_call_reasons:
            provider_call_records.append(
                _call_record(
                    call_index=call_index,
                    request=request,
                    provider_returned=False,
                    validation_status=STATUS_FAIL_CLOSED,
                    reason_codes=reviewer_call_reasons,
                ),
            )
            return _fail_run(
                scenario_id=scenario_id,
                failed_stage=STAGE_REVIEWER_CALLS,
                constraints=constraints,
                snapshot=actual_snapshot,
                provider_call_records=tuple(provider_call_records),
                proposer_request=proposer_request,
                proposer_payload=proposer_payload,
                proposal=proposal,
                reviewer_request_records=tuple(reviewer_request_records),
                reviewer_responses=tuple(reviewer_responses),
                actor_reviews=tuple(actor_reviews),
                validation_errors=reviewer_call_reasons,
            )
        response, response_reasons = parse_injected_reviewer_response_v01(
            request=request,
            selection_input=selection_input,
            proposed_offer_id=proposal.recommended_offer_id,
            payload=payload,
        )
        provider_call_records.append(
            _call_record(
                call_index=call_index,
                request=request,
                provider_returned=True,
                validation_status=(
                    binding.STATUS_PASS if not response_reasons else STATUS_FAIL_CLOSED
                ),
                reason_codes=response_reasons,
            ),
        )
        if response is None:
            return _fail_run(
                scenario_id=scenario_id,
                failed_stage=STAGE_REVIEWER_CALLS,
                constraints=constraints,
                snapshot=actual_snapshot,
                provider_call_records=tuple(provider_call_records),
                proposer_request=proposer_request,
                proposer_payload=proposer_payload,
                proposal=proposal,
                reviewer_request_records=tuple(reviewer_request_records),
                reviewer_responses=tuple(reviewer_responses),
                actor_reviews=tuple(actor_reviews),
                validation_errors=(
                    (REASON_REVIEWER_RESPONSE_INVALID,) + response_reasons
                ),
            )
        reviewer_responses.append(response)
        actor_reviews.append(_review_from_response(response))

    actor_reviews_tuple = tuple(actor_reviews)
    if tuple(record.actor_id for record in provider_call_records) != ACTOR_ORDER:
        return _fail_run(
            scenario_id=scenario_id,
            failed_stage=STAGE_ACTOR_REVIEWS,
            constraints=constraints,
            snapshot=actual_snapshot,
            provider_call_records=tuple(provider_call_records),
            proposer_request=proposer_request,
            proposer_payload=proposer_payload,
            proposal=proposal,
            reviewer_request_records=tuple(reviewer_request_records),
            reviewer_responses=tuple(reviewer_responses),
            actor_reviews=actor_reviews_tuple,
            validation_errors=(REASON_ACTOR_CALL_ORDER_MISMATCH,),
        )
    if len(provider_call_records) != 5:
        return _fail_run(
            scenario_id=scenario_id,
            failed_stage=STAGE_ACTOR_REVIEWS,
            constraints=constraints,
            snapshot=actual_snapshot,
            provider_call_records=tuple(provider_call_records),
            proposer_request=proposer_request,
            proposer_payload=proposer_payload,
            proposal=proposal,
            reviewer_request_records=tuple(reviewer_request_records),
            reviewer_responses=tuple(reviewer_responses),
            actor_reviews=actor_reviews_tuple,
            validation_errors=(REASON_EXACT_FIVE_SEMANTIC_ACTOR_CALLS_REQUIRED,),
        )

    review_reasons: list[str] = []
    for review in actor_reviews_tuple:
        review_reasons.extend(
            binding.validate_airline_canonical_actor_selection_review_v01(
                selection_input,
                review,
            ).reason_codes,
        )
    if review_reasons:
        return _fail_run(
            scenario_id=scenario_id,
            failed_stage=STAGE_ACTOR_REVIEWS,
            constraints=constraints,
            snapshot=actual_snapshot,
            provider_call_records=tuple(provider_call_records),
            proposer_request=proposer_request,
            proposer_payload=proposer_payload,
            proposal=proposal,
            reviewer_request_records=tuple(reviewer_request_records),
            reviewer_responses=tuple(reviewer_responses),
            actor_reviews=actor_reviews_tuple,
            validation_errors=review_reasons,
        )

    synthesis = binding.build_valid_synthesis_report_v01(
        selection_input=selection_input,
        actor_reviews=actor_reviews_tuple,
        synthesized_recommended_offer_id=proposal.recommended_offer_id,
    )
    synthesis_report = binding.validate_airline_semantic_selection_synthesis_report_v01(
        selection_input,
        actor_reviews_tuple,
        synthesis,
    )
    if synthesis_report.validation_status != binding.STATUS_PASS:
        return _fail_run(
            scenario_id=scenario_id,
            failed_stage=STAGE_SYNTHESIS,
            constraints=constraints,
            snapshot=actual_snapshot,
            provider_call_records=tuple(provider_call_records),
            proposer_request=proposer_request,
            proposer_payload=proposer_payload,
            proposal=proposal,
            reviewer_request_records=tuple(reviewer_request_records),
            reviewer_responses=tuple(reviewer_responses),
            actor_reviews=actor_reviews_tuple,
            synthesis=synthesis,
            local_chain_validation=synthesis_report,
            validation_errors=synthesis_report.reason_codes,
        )

    evidence = binding.build_valid_canonical_selection_evidence_v01(
        selection_input=selection_input,
        proposal=proposal,
        synthesis=synthesis,
    )
    evidence_report = binding.validate_validated_airline_semantic_selection_evidence_v01(
        selection_input,
        proposal,
        actor_reviews_tuple,
        synthesis,
        evidence,
    )
    if evidence_report.validation_status != binding.STATUS_PASS:
        return _fail_run(
            scenario_id=scenario_id,
            failed_stage=STAGE_CANONICAL_EVIDENCE,
            constraints=constraints,
            snapshot=actual_snapshot,
            provider_call_records=tuple(provider_call_records),
            proposer_request=proposer_request,
            proposer_payload=proposer_payload,
            proposal=proposal,
            reviewer_request_records=tuple(reviewer_request_records),
            reviewer_responses=tuple(reviewer_responses),
            actor_reviews=actor_reviews_tuple,
            synthesis=synthesis,
            canonical_evidence=evidence,
            local_chain_validation=evidence_report,
            validation_errors=evidence_report.reason_codes,
        )

    decision = binding.build_valid_client_root_decision_v01(
        selection_input=selection_input,
        evidence=evidence,
        selected_offer_id=evidence.recommended_offer_id,
        recommendation_accepted=True,
        root_override_used=False,
    )
    decision_report = binding.validate_client_root_offer_selection_decision_v01(
        selection_input,
        evidence,
        decision,
    )
    if decision_report.validation_status != binding.STATUS_PASS:
        return _fail_run(
            scenario_id=scenario_id,
            failed_stage=STAGE_CLIENT_ROOT_DECISION,
            constraints=constraints,
            snapshot=actual_snapshot,
            provider_call_records=tuple(provider_call_records),
            proposer_request=proposer_request,
            proposer_payload=proposer_payload,
            proposal=proposal,
            reviewer_request_records=tuple(reviewer_request_records),
            reviewer_responses=tuple(reviewer_responses),
            actor_reviews=actor_reviews_tuple,
            synthesis=synthesis,
            canonical_evidence=evidence,
            client_root_decision=decision,
            local_chain_validation=decision_report,
            validation_errors=decision_report.reason_codes,
        )

    resolution = binding.build_valid_airline_root_resolution_v01(
        selection_input=selection_input,
        snapshot=actual_snapshot,
        decision=decision,
    )
    resolution_report = binding.validate_airline_root_selected_offer_resolution_v01(
        selection_input,
        actual_snapshot,
        evidence,
        decision,
        resolution,
    )
    if resolution_report.validation_status != binding.STATUS_PASS:
        return _fail_run(
            scenario_id=scenario_id,
            failed_stage=STAGE_AIRLINE_ROOT_RESOLUTION,
            constraints=constraints,
            snapshot=actual_snapshot,
            provider_call_records=tuple(provider_call_records),
            proposer_request=proposer_request,
            proposer_payload=proposer_payload,
            proposal=proposal,
            reviewer_request_records=tuple(reviewer_request_records),
            reviewer_responses=tuple(reviewer_responses),
            actor_reviews=actor_reviews_tuple,
            synthesis=synthesis,
            canonical_evidence=evidence,
            client_root_decision=decision,
            airline_root_resolution=resolution,
            local_chain_validation=resolution_report,
            validation_errors=resolution_report.reason_codes,
        )

    hold_packet = project_airline_hold_packet_from_resolution_v01(resolution)
    hold_binding = binding.build_valid_hold_contract_binding_v01(
        resolution=resolution,
        hold_packet=hold_packet,
    )
    hold_report = binding.validate_airline_semantic_hold_contract_binding_v01(
        resolution,
        hold_packet,
        hold_binding,
        resolution_report=resolution_report,
    )
    if hold_report.validation_status != binding.STATUS_PASS:
        return _fail_run(
            scenario_id=scenario_id,
            failed_stage=STAGE_HOLD_BINDING,
            constraints=constraints,
            snapshot=actual_snapshot,
            provider_call_records=tuple(provider_call_records),
            proposer_request=proposer_request,
            proposer_payload=proposer_payload,
            proposal=proposal,
            reviewer_request_records=tuple(reviewer_request_records),
            reviewer_responses=tuple(reviewer_responses),
            actor_reviews=actor_reviews_tuple,
            synthesis=synthesis,
            canonical_evidence=evidence,
            client_root_decision=decision,
            airline_root_resolution=resolution,
            local_chain_validation=hold_report,
            validation_errors=hold_report.reason_codes,
        )

    causal_binding_report = binding.build_valid_semantic_to_contract_binding_report_v01(
        bsep_projection=actual_bsep,
        constraints=constraints,
        snapshot=actual_snapshot,
        selection_input=selection_input,
        proposal=proposal,
        actor_reviews=actor_reviews_tuple,
        synthesis=synthesis,
        evidence=evidence,
        decision=decision,
        resolution=resolution,
        hold_packet=hold_packet,
        hold_binding=hold_binding,
    )
    binding_report = binding.validate_airline_semantic_to_contract_binding_report_v01(
        causal_binding_report,
    )
    if binding_report.validation_status != binding.STATUS_PASS:
        return _fail_run(
            scenario_id=scenario_id,
            failed_stage=STAGE_BINDING_REPORT,
            constraints=constraints,
            snapshot=actual_snapshot,
            provider_call_records=tuple(provider_call_records),
            proposer_request=proposer_request,
            proposer_payload=proposer_payload,
            proposal=proposal,
            reviewer_request_records=tuple(reviewer_request_records),
            reviewer_responses=tuple(reviewer_responses),
            actor_reviews=actor_reviews_tuple,
            synthesis=synthesis,
            canonical_evidence=evidence,
            client_root_decision=decision,
            airline_root_resolution=resolution,
            local_chain_validation=binding_report,
            validation_errors=binding_report.reason_codes,
        )

    local_chain = binding.validate_airline_semantic_to_contract_local_chain_v01(
        bsep_projection=actual_bsep,
        constraints=constraints,
        snapshot=actual_snapshot,
        selection_input=selection_input,
        proposal=proposal,
        actor_reviews=actor_reviews_tuple,
        synthesis=synthesis,
        evidence=evidence,
        decision=decision,
        resolution=resolution,
        hold_packet=hold_packet,
        hold_binding=hold_binding,
        binding_report=causal_binding_report,
    )
    if local_chain.validation_status != binding.STATUS_LOCAL_MODEL_PASS:
        return _fail_run(
            scenario_id=scenario_id,
            failed_stage=STAGE_LOCAL_CHAIN,
            constraints=constraints,
            snapshot=actual_snapshot,
            provider_call_records=tuple(provider_call_records),
            proposer_request=proposer_request,
            proposer_payload=proposer_payload,
            proposal=proposal,
            reviewer_request_records=tuple(reviewer_request_records),
            reviewer_responses=tuple(reviewer_responses),
            actor_reviews=actor_reviews_tuple,
            synthesis=synthesis,
            canonical_evidence=evidence,
            client_root_decision=decision,
            airline_root_resolution=resolution,
            local_chain_validation=local_chain,
            validation_errors=local_chain.reason_codes,
        )

    if not (
        proposal.recommended_offer_id
        == decision.selected_offer_id
        == hold_packet.offer_id
    ):
        return _fail_run(
            scenario_id=scenario_id,
            failed_stage=STAGE_LOCAL_CHAIN,
            constraints=constraints,
            snapshot=actual_snapshot,
            provider_call_records=tuple(provider_call_records),
            proposer_request=proposer_request,
            proposer_payload=proposer_payload,
            proposal=proposal,
            reviewer_request_records=tuple(reviewer_request_records),
            reviewer_responses=tuple(reviewer_responses),
            actor_reviews=actor_reviews_tuple,
            synthesis=synthesis,
            canonical_evidence=evidence,
            client_root_decision=decision,
            airline_root_resolution=resolution,
            local_chain_validation=local_chain,
            validation_errors=(REASON_SEMANTIC_CHANGE_DID_NOT_PROPAGATE_TO_CONTRACT,),
        )

    return _run_report(
        scenario_id=scenario_id,
        final_status=STATUS_LOCAL_MODEL_PASS,
        failed_stage="",
        constraints=constraints,
        snapshot=actual_snapshot,
        provider_call_records=tuple(provider_call_records),
        proposer_request=proposer_request,
        proposer_payload=proposer_payload,
        proposal=proposal,
        reviewer_request_records=tuple(reviewer_request_records),
        reviewer_responses=tuple(reviewer_responses),
        actor_reviews=actor_reviews_tuple,
        synthesis=synthesis,
        canonical_evidence=evidence,
        client_root_decision=decision,
        airline_root_resolution=resolution,
        hold_packet=hold_packet,
        hold_binding=hold_binding,
        causal_binding_report=causal_binding_report,
        local_chain_validation=local_chain,
        validation_errors=(),
    )


def _same_hard_constraints(
    first: binding.ClientRootTravelConstraintSetV01,
    second: binding.ClientRootTravelConstraintSetV01,
) -> bool:
    return _hard_constraint_fingerprint(first) == _hard_constraint_fingerprint(second)


def _different_soft_preferences(
    first: binding.ClientRootTravelConstraintSetV01,
    second: binding.ClientRootTravelConstraintSetV01,
) -> bool:
    return _soft_preference_fingerprint(first) != _soft_preference_fingerprint(second)


def _with_opaque_constraint_id(
    constraints: binding.ClientRootTravelConstraintSetV01,
    opaque_id: str,
) -> binding.ClientRootTravelConstraintSetV01:
    return replace(constraints, constraint_set_id=opaque_id)


def _fixed_safety_invariants_identical(
    first: AirlineSemanticCausalRunReportV01,
    second: AirlineSemanticCausalRunReportV01,
) -> bool:
    if (
        first.proposer_request is None
        or second.proposer_request is None
        or first.hold_packet is None
        or second.hold_packet is None
    ):
        return False
    all_request_flags_false = all(
        not any(
            (
                request.provider_may_create_authority,
                request.provider_may_create_contract,
                request.provider_may_create_packet,
                request.provider_may_create_receipt,
                request.provider_may_execute_action,
                request.raw_secret_included,
            ),
        )
        for request in (
            (first.proposer_request,)
            + first.reviewer_request_records
            + (second.proposer_request,)
            + second.reviewer_request_records
        )
    )
    return (
        first.proposer_request.source_bsep_projection_ref
        == second.proposer_request.source_bsep_projection_ref
        and
        first.candidate_set_snapshot_id == second.candidate_set_snapshot_id
        and first.candidate_set_digest == second.candidate_set_digest
        and first.proposer_request.visible_candidate_ids
        == second.proposer_request.visible_candidate_ids
        and first.proposer_request.airline_valid_candidate_ids
        == second.proposer_request.airline_valid_candidate_ids
        and first.proposer_request.client_hard_compatible_candidate_ids
        == second.proposer_request.client_hard_compatible_candidate_ids
        and first.hard_constraint_fingerprint == second.hard_constraint_fingerprint
        and all_request_flags_false
        and first.hold_packet.created_by == binding.AIRLINE_ROOT_ID
        and second.hold_packet.created_by == binding.AIRLINE_ROOT_ID
        and first.hold_packet.root_owner == binding.AIRLINE_ROOT_ID
        and second.hold_packet.root_owner == binding.AIRLINE_ROOT_ID
        and first.hold_packet.allowed_action == second.hold_packet.allowed_action
        and first.hold_packet.allowed_action == corridor_contracts.ACTION_MOCK_OFFER_HOLD
        and first.hold_packet.allowed_adapters == second.hold_packet.allowed_adapters
        and first.hold_packet.allowed_adapters
        == (corridor_contracts.ADAPTER_AIRLINE_HOLD_SANDBOX,)
        and first.hold_packet.forbidden_actions == second.hold_packet.forbidden_actions
        and not first.hold_packet.real_world_effects_allowed
        and not second.hold_packet.real_world_effects_allowed
    )


def _request_hard_constraints_identical(
    first: AirlineSemanticCausalRunReportV01,
    second: AirlineSemanticCausalRunReportV01,
) -> bool:
    return (
        first.proposer_request is not None
        and second.proposer_request is not None
        and first.proposer_request.client_hard_constraints
        == second.proposer_request.client_hard_constraints
    )


def _request_soft_preferences_different(
    first: AirlineSemanticCausalRunReportV01,
    second: AirlineSemanticCausalRunReportV01,
) -> bool:
    return (
        first.proposer_request is not None
        and second.proposer_request is not None
        and first.proposer_request.client_soft_preferences
        != second.proposer_request.client_soft_preferences
    )


def _stored_fingerprints_match_request(
    report: AirlineSemanticCausalRunReportV01,
) -> bool:
    return (
        report.proposer_request is not None
        and report.hard_constraint_fingerprint
        == hard_constraint_fingerprint_from_request_v01(report.proposer_request)
        and report.soft_preference_fingerprint
        == soft_preference_fingerprint_from_request_v01(report.proposer_request)
    )


def _constraint_id(report: AirlineSemanticCausalRunReportV01) -> str:
    if report.proposer_request is None:
        return ""
    return report.proposer_request.source_client_constraint_set_id


def _request_surface(
    report: AirlineSemanticCausalRunReportV01,
) -> tuple[Any, ...]:
    if report.proposer_request is None:
        return ()
    return (
        report.transaction_id,
        report.candidate_set_snapshot_id,
        report.candidate_set_digest,
        report.proposer_request.source_bsep_projection_ref,
        report.proposer_request.visible_candidate_ids,
        report.proposer_request.airline_valid_candidate_ids,
        report.proposer_request.client_hard_compatible_candidate_ids,
    )


def _identity_runs_use_probe_ids(
    report: AirlineSemanticIdentityInvarianceReportV01,
) -> bool:
    return (
        _constraint_id(report.preference_a_first) == report.probe_constraint_id_x
        and _constraint_id(report.preference_a_second) == report.probe_constraint_id_y
        and _constraint_id(report.preference_b_first) == report.probe_constraint_id_x
        and _constraint_id(report.preference_b_second) == report.probe_constraint_id_y
        and report.probe_constraint_id_x != report.probe_constraint_id_y
    )


def _identity_runs_share_surface(
    report: AirlineSemanticIdentityInvarianceReportV01,
) -> bool:
    surfaces = (
        _request_surface(report.preference_a_first),
        _request_surface(report.preference_a_second),
        _request_surface(report.preference_b_first),
        _request_surface(report.preference_b_second),
    )
    return all(surface and surface == surfaces[0] for surface in surfaces)


def _pair_and_identity_probe_binding_matches(
    pair: AirlineSemanticCounterfactualPairReportV01,
) -> bool:
    identity = pair.identity_invariance_report
    if (
        _constraint_id(pair.scenario_a) != identity.probe_constraint_id_x
        or _constraint_id(pair.scenario_b) != identity.probe_constraint_id_y
    ):
        return False
    pair_surfaces = (_request_surface(pair.scenario_a), _request_surface(pair.scenario_b))
    identity_surfaces = (
        _request_surface(identity.preference_a_first),
        _request_surface(identity.preference_a_second),
        _request_surface(identity.preference_b_first),
        _request_surface(identity.preference_b_second),
    )
    return all(
        surface and surface in pair_surfaces and surface == pair_surfaces[0]
        for surface in identity_surfaces + pair_surfaces
    )


def validate_airline_semantic_counterfactual_pair_v01(
    pair: AirlineSemanticCounterfactualPairReportV01,
) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    scenario_a_valid, scenario_a_reasons = validate_airline_semantic_causal_run_report_v01(
        pair.scenario_a,
    )
    scenario_b_valid, scenario_b_reasons = validate_airline_semantic_causal_run_report_v01(
        pair.scenario_b,
    )
    if not scenario_a_valid:
        reasons.extend(scenario_a_reasons)
    if not scenario_b_valid:
        reasons.extend(scenario_b_reasons)
    identity_valid, identity_reasons = (
        validate_airline_semantic_identity_invariance_report_v01(
            pair.identity_invariance_report,
        )
    )
    if not identity_valid:
        reasons.extend(identity_reasons)
    probe_binding_matches = _pair_and_identity_probe_binding_matches(pair)

    same_snapshot_id = (
        pair.scenario_a.candidate_set_snapshot_id
        == pair.scenario_b.candidate_set_snapshot_id
    )
    same_snapshot_digest = (
        pair.scenario_a.candidate_set_digest == pair.scenario_b.candidate_set_digest
    )
    hard_constraints_identical = _request_hard_constraints_identical(
        pair.scenario_a,
        pair.scenario_b,
    )
    soft_preferences_different = _request_soft_preferences_different(
        pair.scenario_a,
        pair.scenario_b,
    )
    semantic_recommendations_different = (
        pair.scenario_a.semantic_recommendation_id
        != pair.scenario_b.semantic_recommendation_id
    )
    root_selected_offers_different = (
        pair.scenario_a.root_selected_offer_id != pair.scenario_b.root_selected_offer_id
    )
    hold_contract_offers_different = (
        pair.scenario_a.hold_contract_offer_id
        != pair.scenario_b.hold_contract_offer_id
    )
    provider_call_count = (
        pair.scenario_a.provider_call_count + pair.scenario_b.provider_call_count
    )
    semantic_change_propagated = (
        semantic_recommendations_different
        and root_selected_offers_different
        and hold_contract_offers_different
    )
    hardcoded_default_detected = (
        pair.scenario_a.hold_contract_offer_id != ""
        and pair.scenario_a.hold_contract_offer_id
        == pair.scenario_b.hold_contract_offer_id
    )
    silent_fallback_detected = (
        pair.scenario_a.silent_fallback_used or pair.scenario_b.silent_fallback_used
    )
    real_world_effects_count = (
        pair.scenario_a.real_world_effects_count
        + pair.scenario_b.real_world_effects_count
    )
    fixed_safety_identical = _fixed_safety_invariants_identical(
        pair.scenario_a,
        pair.scenario_b,
    )

    if (
        pair.same_candidate_snapshot_id != same_snapshot_id
        or pair.same_candidate_snapshot_digest != same_snapshot_digest
        or pair.hard_constraints_identical != hard_constraints_identical
        or pair.soft_preferences_different != soft_preferences_different
        or pair.semantic_recommendations_different
        != semantic_recommendations_different
        or pair.root_selected_offers_different != root_selected_offers_different
        or pair.hold_contract_offers_different != hold_contract_offers_different
        or pair.scenario_a_recommendation
        != pair.scenario_a.semantic_recommendation_id
        or pair.scenario_b_recommendation
        != pair.scenario_b.semantic_recommendation_id
        or pair.scenario_a_hold_offer != pair.scenario_a.hold_contract_offer_id
        or pair.scenario_b_hold_offer != pair.scenario_b.hold_contract_offer_id
        or pair.provider_call_count != provider_call_count
        or pair.semantic_change_propagated_to_contract != semantic_change_propagated
        or pair.hardcoded_default_detected != hardcoded_default_detected
        or pair.silent_fallback_detected != silent_fallback_detected
        or pair.real_world_effects_count != real_world_effects_count
        or pair.fixed_safety_invariants_identical != fixed_safety_identical
        or pair.identity_invariance_passed
        != (pair.identity_invariance_report.final_status == STATUS_LOCAL_MODEL_PASS)
        or pair.provider_identity_sensitive_detected
        != (pair.identity_invariance_report.final_status != STATUS_LOCAL_MODEL_PASS)
    ):
        reasons.append(REASON_CAUSAL_RUN_DERIVED_FIELD_MISMATCH)
    if not probe_binding_matches:
        reasons.append(REASON_PROVIDER_IDENTITY_PROBE_BINDING_MISMATCH)
    if not pair.identity_invariance_passed or pair.provider_identity_sensitive_detected:
        reasons.append(REASON_PROVIDER_IDENTITY_INVARIANCE_FAILED)
    if not (
        _stored_fingerprints_match_request(pair.scenario_a)
        and _stored_fingerprints_match_request(pair.scenario_b)
    ):
        reasons.append(REASON_CAUSAL_RUN_DERIVED_FIELD_MISMATCH)

    if not same_snapshot_id or not same_snapshot_digest:
        reasons.append(binding.REASON_SNAPSHOT_SUBSTITUTION_DETECTED)
    if not hard_constraints_identical:
        reasons.append(binding.REASON_CLIENT_CONSTRAINT_SET_INVALID)
    if not soft_preferences_different:
        reasons.append(REASON_SEMANTIC_CHANGE_DID_NOT_PROPAGATE_TO_CONTRACT)
    if not (
        semantic_recommendations_different
        and root_selected_offers_different
        and hold_contract_offers_different
        and semantic_change_propagated
    ):
        reasons.append(REASON_SEMANTIC_CHANGE_DID_NOT_PROPAGATE_TO_CONTRACT)
    if not fixed_safety_identical:
        reasons.append(binding.REASON_SELECTION_INPUT_SNAPSHOT_MISMATCH)
    if hardcoded_default_detected:
        reasons.append(REASON_HARDCODED_DEFAULT_DETECTED)
    if silent_fallback_detected:
        reasons.append(REASON_SILENT_FALLBACK_DETECTED)
    if real_world_effects_count != 0:
        reasons.append(binding.REASON_NONZERO_REAL_WORLD_EFFECTS)
    return not reasons, _dedupe(reasons)


def _same_semantic_request_content(
    first: AirlineSemanticCausalRunReportV01,
    second: AirlineSemanticCausalRunReportV01,
) -> bool:
    return (
        first.proposer_request is not None
        and second.proposer_request is not None
        and first.proposer_request.client_hard_constraints
        == second.proposer_request.client_hard_constraints
        and first.proposer_request.client_soft_preferences
        == second.proposer_request.client_soft_preferences
    )


def _constraint_ids_different(
    first: AirlineSemanticCausalRunReportV01,
    second: AirlineSemanticCausalRunReportV01,
) -> bool:
    return (
        first.proposer_request is not None
        and second.proposer_request is not None
        and first.proposer_request.source_client_constraint_set_id
        != second.proposer_request.source_client_constraint_set_id
    )


def validate_airline_semantic_identity_invariance_report_v01(
    report: AirlineSemanticIdentityInvarianceReportV01,
) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    run_results = (
        validate_airline_semantic_causal_run_report_v01(report.preference_a_first),
        validate_airline_semantic_causal_run_report_v01(report.preference_a_second),
        validate_airline_semantic_causal_run_report_v01(report.preference_b_first),
        validate_airline_semantic_causal_run_report_v01(report.preference_b_second),
    )
    for accepted, run_reasons in run_results:
        if not accepted:
            reasons.extend(run_reasons)
    if not _identity_runs_use_probe_ids(report):
        reasons.append(REASON_PROVIDER_IDENTITY_PROBE_BINDING_MISMATCH)
    if not _identity_runs_share_surface(report):
        reasons.append(REASON_PROVIDER_IDENTITY_PROBE_BINDING_MISMATCH)
    expected_a_content = _same_semantic_request_content(
        report.preference_a_first,
        report.preference_a_second,
    )
    expected_b_content = _same_semantic_request_content(
        report.preference_b_first,
        report.preference_b_second,
    )
    expected_a_ids_different = _constraint_ids_different(
        report.preference_a_first,
        report.preference_a_second,
    )
    expected_b_ids_different = _constraint_ids_different(
        report.preference_b_first,
        report.preference_b_second,
    )
    expected_a_recommendations_identical = (
        report.preference_a_first.semantic_recommendation_id
        == report.preference_a_second.semantic_recommendation_id
    )
    expected_b_recommendations_identical = (
        report.preference_b_first.semantic_recommendation_id
        == report.preference_b_second.semantic_recommendation_id
    )
    expected_swapped = (
        expected_a_recommendations_identical
        and expected_b_recommendations_identical
    )
    expected_identity_invariant = (
        expected_a_content
        and expected_b_content
        and expected_a_ids_different
        and expected_b_ids_different
        and expected_a_recommendations_identical
        and expected_b_recommendations_identical
        and expected_swapped
    )
    expected_call_count = sum(
        run.provider_call_count
        for run in (
            report.preference_a_first,
            report.preference_a_second,
            report.preference_b_first,
            report.preference_b_second,
        )
    )
    expected_effects = sum(
        run.real_world_effects_count
        for run in (
            report.preference_a_first,
            report.preference_a_second,
            report.preference_b_first,
            report.preference_b_second,
        )
    )
    if (
        report.a_content_identical != expected_a_content
        or report.b_content_identical != expected_b_content
        or report.a_ids_different != expected_a_ids_different
        or report.b_ids_different != expected_b_ids_different
        or report.a_recommendations_identical
        != expected_a_recommendations_identical
        or report.b_recommendations_identical
        != expected_b_recommendations_identical
        or report.swapped_id_recommendations_follow_content != expected_swapped
        or report.provider_identity_invariant != expected_identity_invariant
        or report.provider_call_count != expected_call_count
        or report.real_world_effects_count != expected_effects
    ):
        reasons.append(REASON_CAUSAL_RUN_DERIVED_FIELD_MISMATCH)
    if not expected_identity_invariant:
        reasons.append(REASON_PROVIDER_IDENTITY_INVARIANCE_FAILED)
    if expected_effects != 0:
        reasons.append(binding.REASON_NONZERO_REAL_WORLD_EFFECTS)
    return not reasons, _dedupe(reasons)


def collect_airline_semantic_identity_invariance_control_v01(
    *,
    semantic_provider: AirlineInjectedSemanticProviderV01,
    snapshot: binding.AirlineRootOfferCandidateSetSnapshotV01 | None = None,
    bsep_projection: binding.AirlineBSEPProjectionRefV01 | None = None,
    probe_constraint_id_x: str = CAUSAL_PROBE_CONSTRAINT_ID_X,
    probe_constraint_id_y: str = CAUSAL_PROBE_CONSTRAINT_ID_Y,
) -> AirlineSemanticIdentityInvarianceReportV01:
    actual_snapshot = snapshot or binding.build_airline_candidate_snapshot_v01()
    actual_bsep = bsep_projection or binding.build_valid_airline_bsep_projection_ref_v01()
    preference_a_first = collect_airline_semantic_to_contract_causal_run_v01(
        scenario_id="identity_control_a_first",
        constraints=_with_opaque_constraint_id(
            binding.build_client_constraints_preference_a_v01(),
            probe_constraint_id_x,
        ),
        semantic_provider=semantic_provider,
        snapshot=actual_snapshot,
        bsep_projection=actual_bsep,
    )
    preference_a_second = collect_airline_semantic_to_contract_causal_run_v01(
        scenario_id="identity_control_a_second",
        constraints=_with_opaque_constraint_id(
            binding.build_client_constraints_preference_a_v01(),
            probe_constraint_id_y,
        ),
        semantic_provider=semantic_provider,
        snapshot=actual_snapshot,
        bsep_projection=actual_bsep,
    )
    preference_b_first = collect_airline_semantic_to_contract_causal_run_v01(
        scenario_id="identity_control_b_first",
        constraints=_with_opaque_constraint_id(
            binding.build_client_constraints_preference_b_v01(),
            probe_constraint_id_x,
        ),
        semantic_provider=semantic_provider,
        snapshot=actual_snapshot,
        bsep_projection=actual_bsep,
    )
    preference_b_second = collect_airline_semantic_to_contract_causal_run_v01(
        scenario_id="identity_control_b_second",
        constraints=_with_opaque_constraint_id(
            binding.build_client_constraints_preference_b_v01(),
            probe_constraint_id_y,
        ),
        semantic_provider=semantic_provider,
        snapshot=actual_snapshot,
        bsep_projection=actual_bsep,
    )
    a_content_identical = _same_semantic_request_content(
        preference_a_first,
        preference_a_second,
    )
    b_content_identical = _same_semantic_request_content(
        preference_b_first,
        preference_b_second,
    )
    a_ids_different = _constraint_ids_different(
        preference_a_first,
        preference_a_second,
    )
    b_ids_different = _constraint_ids_different(
        preference_b_first,
        preference_b_second,
    )
    a_recommendations_identical = (
        preference_a_first.semantic_recommendation_id
        == preference_a_second.semantic_recommendation_id
    )
    b_recommendations_identical = (
        preference_b_first.semantic_recommendation_id
        == preference_b_second.semantic_recommendation_id
    )
    swapped_follows_content = (
        a_recommendations_identical
        and b_recommendations_identical
    )
    provider_identity_invariant = (
        a_content_identical
        and b_content_identical
        and a_ids_different
        and b_ids_different
        and a_recommendations_identical
        and b_recommendations_identical
        and swapped_follows_content
    )
    provider_call_count = sum(
        run.provider_call_count
        for run in (
            preference_a_first,
            preference_a_second,
            preference_b_first,
            preference_b_second,
        )
    )
    real_world_effects_count = sum(
        run.real_world_effects_count
        for run in (
            preference_a_first,
            preference_a_second,
            preference_b_first,
            preference_b_second,
        )
    )
    draft = AirlineSemanticIdentityInvarianceReportV01(
        report_id="airline_semantic_identity_invariance_control:v01",
        final_status=STATUS_FAIL_CLOSED,
        probe_constraint_id_x=probe_constraint_id_x,
        probe_constraint_id_y=probe_constraint_id_y,
        preference_a_first=preference_a_first,
        preference_a_second=preference_a_second,
        preference_b_first=preference_b_first,
        preference_b_second=preference_b_second,
        a_content_identical=a_content_identical,
        b_content_identical=b_content_identical,
        a_ids_different=a_ids_different,
        b_ids_different=b_ids_different,
        a_recommendations_identical=a_recommendations_identical,
        b_recommendations_identical=b_recommendations_identical,
        swapped_id_recommendations_follow_content=swapped_follows_content,
        provider_identity_invariant=provider_identity_invariant,
        validation_errors=(),
        provider_call_count=provider_call_count,
        real_world_effects_count=real_world_effects_count,
    )
    accepted, reasons = validate_airline_semantic_identity_invariance_report_v01(
        draft,
    )
    return replace(
        draft,
        final_status=STATUS_LOCAL_MODEL_PASS if accepted else STATUS_FAIL_CLOSED,
        validation_errors=reasons,
    )


def collect_airline_semantic_counterfactual_pair_v01(
    *,
    semantic_provider: AirlineInjectedSemanticProviderV01,
) -> AirlineSemanticCounterfactualPairReportV01:
    constraints_a = _with_opaque_constraint_id(
        binding.build_client_constraints_preference_a_v01(),
        CAUSAL_PROBE_CONSTRAINT_ID_X,
    )
    constraints_b = _with_opaque_constraint_id(
        binding.build_client_constraints_preference_b_v01(),
        CAUSAL_PROBE_CONSTRAINT_ID_Y,
    )
    snapshot = binding.build_airline_candidate_snapshot_v01()
    bsep_projection = binding.build_valid_airline_bsep_projection_ref_v01()

    scenario_a = collect_airline_semantic_to_contract_causal_run_v01(
        scenario_id="preference_a",
        constraints=constraints_a,
        semantic_provider=semantic_provider,
        snapshot=snapshot,
        bsep_projection=bsep_projection,
    )
    scenario_b = collect_airline_semantic_to_contract_causal_run_v01(
        scenario_id="preference_b",
        constraints=constraints_b,
        semantic_provider=semantic_provider,
        snapshot=snapshot,
        bsep_projection=bsep_projection,
    )
    identity_invariance_report = (
        collect_airline_semantic_identity_invariance_control_v01(
            semantic_provider=semantic_provider,
            snapshot=snapshot,
            bsep_projection=bsep_projection,
        )
    )
    identity_invariance_passed = (
        identity_invariance_report.final_status == STATUS_LOCAL_MODEL_PASS
    )

    same_snapshot_id = (
        scenario_a.candidate_set_snapshot_id == scenario_b.candidate_set_snapshot_id
    )
    same_snapshot_digest = scenario_a.candidate_set_digest == scenario_b.candidate_set_digest
    hard_constraints_identical = _request_hard_constraints_identical(
        scenario_a,
        scenario_b,
    )
    soft_preferences_different = _request_soft_preferences_different(
        scenario_a,
        scenario_b,
    )
    semantic_recommendations_different = (
        scenario_a.semantic_recommendation_id
        != scenario_b.semantic_recommendation_id
    )
    root_selected_offers_different = (
        scenario_a.root_selected_offer_id != scenario_b.root_selected_offer_id
    )
    hold_contract_offers_different = (
        scenario_a.hold_contract_offer_id != scenario_b.hold_contract_offer_id
    )
    fixed_safety_identical = _fixed_safety_invariants_identical(
        scenario_a,
        scenario_b,
    )
    semantic_change_propagated = (
        semantic_recommendations_different
        and root_selected_offers_different
        and hold_contract_offers_different
    )
    hardcoded_default_detected = (
        scenario_a.hold_contract_offer_id != ""
        and scenario_a.hold_contract_offer_id == scenario_b.hold_contract_offer_id
    )
    silent_fallback_detected = (
        scenario_a.silent_fallback_used or scenario_b.silent_fallback_used
    )

    draft = AirlineSemanticCounterfactualPairReportV01(
        pair_id="airline_semantic_counterfactual_pair:preference_a_vs_b",
        final_status=STATUS_FAIL_CLOSED,
        scenario_a=scenario_a,
        scenario_b=scenario_b,
        identity_invariance_report=identity_invariance_report,
        identity_invariance_passed=identity_invariance_passed,
        provider_identity_sensitive_detected=not identity_invariance_passed,
        same_candidate_snapshot_id=same_snapshot_id,
        same_candidate_snapshot_digest=same_snapshot_digest,
        hard_constraints_identical=hard_constraints_identical,
        soft_preferences_different=soft_preferences_different,
        semantic_recommendations_different=semantic_recommendations_different,
        root_selected_offers_different=root_selected_offers_different,
        hold_contract_offers_different=hold_contract_offers_different,
        scenario_a_recommendation=scenario_a.semantic_recommendation_id,
        scenario_b_recommendation=scenario_b.semantic_recommendation_id,
        scenario_a_hold_offer=scenario_a.hold_contract_offer_id,
        scenario_b_hold_offer=scenario_b.hold_contract_offer_id,
        fixed_safety_invariants_identical=fixed_safety_identical,
        provider_call_count=scenario_a.provider_call_count + scenario_b.provider_call_count,
        semantic_change_propagated_to_contract=semantic_change_propagated,
        hardcoded_default_detected=hardcoded_default_detected,
        silent_fallback_detected=silent_fallback_detected,
        validation_errors=(),
        real_world_effects_count=(
            scenario_a.real_world_effects_count + scenario_b.real_world_effects_count
        ),
    )
    accepted, reasons = validate_airline_semantic_counterfactual_pair_v01(draft)
    return replace(
        draft,
        final_status=STATUS_LOCAL_MODEL_PASS if accepted else STATUS_FAIL_CLOSED,
        validation_errors=reasons,
    )
