"""Airline semantic-to-contract causal binding domain projection.

This module is an Airline domain causal-binding projection. It is not
Hedgehog OS universal kernel/core. Exact boundary phrase:
not Hedgehog OS universal kernel/core. This module is not an installed Needle.

No provider or semantic recommender is implemented here.
No corridor execution is implemented here. This Slice B module validates the path from bounded
semantic artifacts to Root-owned contract references. Provider output remains
advisory, and Root remains authority.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, replace
from typing import Any, Mapping

from hedgehog.domains.airline import (
    ticket_purchase_corridor_v01 as corridor_contracts,
)


MODULE_ID = "airline_semantic_to_contract_binding_v01"
SLICE_ID = "airline_semantic_to_contract_binding_v01_slice_b"

TRANSACTION_ID = corridor_contracts.TRANSACTION_ID
CLIENT_ROOT_ID = corridor_contracts.CLIENT_ROOT_ID
AIRLINE_ROOT_ID = corridor_contracts.AIRLINE_ROOT_ID
BANK_ROOT_ID = corridor_contracts.BANK_ROOT_ID

STATUS_PASS = "PASS"
STATUS_FAIL_CLOSED = "FAIL_CLOSED"
STATUS_ROOT_OVERRIDE = "ROOT_OVERRIDE"
STATUS_REQUIRES_ROOT_REVIEW = "REQUIRES_ROOT_REVIEW"
STATUS_CAUSAL_PASS = "CAUSAL_PASS"
STATUS_REJECTED = "REJECTED"
STATUS_LOCAL_MODEL_PASS = "LOCAL_MODEL_PASS"
STATUS_NOT_YET_BOUND_IN_SLICE_B = "NOT_YET_BOUND_IN_SLICE_B"

OFFER_A_ID = "offer:mock_airline_al:PAR-LIM:001"
OFFER_B_ID = "offer:mock_airline_al:PAR-LIM:002"
OFFER_C_ID = "offer:mock_airline_al:PAR-LIM:003"

CANDIDATE_SET_REF = "candidate_set:mock_airline_al:PAR-LIM:2026-08-12:v01"
CANDIDATE_SET_SNAPSHOT_ID = "candidate_snapshot:mock_airline_al:PAR-LIM:001"
CANDIDATE_SET_VERSION = "v1"
BSEP_PROJECTION_REF = "bsep_projection:airline_offer_selection:001"

ROLE_PROPOSER = "proposer"
ROLE_AIRLINE_COMPATIBILITY_REVIEWER = "airline_compatibility_reviewer"
ROLE_FARE_RULES_REVIEWER = "fare_rules_reviewer"
ROLE_SEAT_BAGGAGE_REVIEWER = "seat_baggage_reviewer"
ROLE_EVIDENCE_CONSISTENCY_REVIEWER = "evidence_consistency_reviewer"

ACTOR_CLIENT_PURCHASE_INTENT_REVIEWER = "client_purchase_intent_reviewer_llm"
ACTOR_AIRLINE_OFFER_POLICY_REVIEWER = "airline_offer_policy_reviewer_llm"
ACTOR_AIRLINE_FARE_RULES_VERTICAL_CELL = "airline_fare_rules_vertical_cell_llm"
ACTOR_AIRLINE_SEAT_BAGGAGE_VERTICAL_CELL = (
    "airline_seat_baggage_vertical_cell_llm"
)
ACTOR_TRI_PARTY_EVIDENCE_CONSISTENCY_REVIEWER = (
    "tri_party_evidence_consistency_reviewer_llm"
)

REQUIRED_ACTOR_ROLES = {
    ACTOR_CLIENT_PURCHASE_INTENT_REVIEWER: ROLE_PROPOSER,
    ACTOR_AIRLINE_OFFER_POLICY_REVIEWER: ROLE_AIRLINE_COMPATIBILITY_REVIEWER,
    ACTOR_AIRLINE_FARE_RULES_VERTICAL_CELL: ROLE_FARE_RULES_REVIEWER,
    ACTOR_AIRLINE_SEAT_BAGGAGE_VERTICAL_CELL: ROLE_SEAT_BAGGAGE_REVIEWER,
    ACTOR_TRI_PARTY_EVIDENCE_CONSISTENCY_REVIEWER: (
        ROLE_EVIDENCE_CONSISTENCY_REVIEWER
    ),
}

REASON_WRONG_TRANSACTION_ID = "wrong_transaction_id"
REASON_WRONG_ROOT_OWNER = "wrong_root_owner"
REASON_PROVIDER_CREATED_CANDIDATE_SNAPSHOT = "provider_created_candidate_snapshot"
REASON_CANDIDATE_SNAPSHOT_DIGEST_MISMATCH = "candidate_snapshot_digest_mismatch"
REASON_CANDIDATE_SNAPSHOT_VERSION_MISMATCH = "candidate_snapshot_version_mismatch"
REASON_CANDIDATE_SNAPSHOT_EXPIRED = "candidate_snapshot_expired"
REASON_RAW_SECRET_IN_CANDIDATE_SNAPSHOT = "raw_secret_in_candidate_snapshot"
REASON_CLIENT_CONSTRAINT_SET_INVALID = "client_constraint_set_invalid"
REASON_SOFT_PREFERENCE_REWROTE_HARD_CONSTRAINT = (
    "soft_preference_rewrote_hard_constraint"
)
REASON_SELECTION_INPUT_SNAPSHOT_MISMATCH = "selection_input_snapshot_mismatch"
REASON_UNKNOWN_CANDIDATE_ID = "unknown_candidate_id"
REASON_DUPLICATE_RANKED_OFFER_ID = "duplicate_ranked_offer_id"
REASON_RECOMMENDED_OFFER_MISSING_FROM_RANKING = (
    "recommended_offer_missing_from_ranking"
)
REASON_FORBIDDEN_PROVIDER_AUTHORITATIVE_FIELD = (
    "forbidden_provider_authoritative_field"
)
REASON_UNKNOWN_PROVIDER_OUTPUT_FIELD = "unknown_provider_output_field"
REASON_PROVIDER_CLAIMED_AUTHORITY = "provider_claimed_authority"
REASON_PROVIDER_CLAIMED_ACTION = "provider_claimed_action"
REASON_PROVIDER_CLAIMED_EFFECT = "provider_claimed_effect"
REASON_ACTOR_ROLE_MISMATCH = "actor_role_mismatch"
REASON_ACTOR_OUTPUT_NOT_VALIDATED = "actor_output_not_validated"
REASON_MISSING_REQUIRED_ACTOR_OUTPUT = "missing_required_actor_output"
REASON_DUPLICATE_ACTOR_OUTPUT = "duplicate_actor_output"
REASON_MULTI_ACTOR_CONFLICT = "multi_actor_conflict"
REASON_UNRESOLVED_CONFLICT = "unresolved_conflict"
REASON_HIDDEN_ACTOR_PRIORITY_FORBIDDEN = "hidden_actor_priority_forbidden"
REASON_SYNTHESIS_NOT_PASS = "synthesis_not_pass"
REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH = (
    "canonical_selection_lineage_mismatch"
)
REASON_CLIENT_CONSTRAINT_COMPATIBILITY_FAILED = (
    "client_constraint_compatibility_failed"
)
REASON_AIRLINE_OFFER_VALIDITY_FAILED = "airline_offer_validity_failed"
REASON_ROOT_OVERRIDE_CANNOT_CLAIM_SEMANTIC_CAUSALITY = (
    "root_override_cannot_claim_semantic_causality"
)
REASON_RESOLUTION_FACT_MISMATCH = "resolution_fact_mismatch"
REASON_SNAPSHOT_SUBSTITUTION_DETECTED = "snapshot_substitution_detected"
REASON_HOLD_CONTRACT_BINDING_MISMATCH = "hold_contract_binding_mismatch"
REASON_HARDCODED_DEFAULT_OFFER_FORBIDDEN = "hardcoded_default_offer_forbidden"
REASON_SILENT_FALLBACK_FORBIDDEN = "silent_fallback_forbidden"
REASON_PROVIDER_CREATED_TARGET_FORBIDDEN = "provider_created_target_forbidden"
REASON_AUTHORITY_TRANSFER_FORBIDDEN = "authority_transfer_forbidden"
REASON_NONZERO_REAL_WORLD_EFFECTS = "nonzero_real_world_effects"
REASON_MISSING_PROVIDER_OUTPUT_FIELD = "missing_provider_output_field"
REASON_INVALID_PROVIDER_OUTPUT_TYPE = "invalid_provider_output_type"
REASON_EMPTY_PROVIDER_OUTPUT_FIELD = "empty_provider_output_field"
REASON_INVALID_PROVIDER_OUTPUT_CONTAINER = "invalid_provider_output_container"
REASON_VALIDATION_FAILED = "validation_failed"
REASON_CLIENT_ROOT_DECISION_REJECTED = "client_root_decision_rejected"
REASON_INTEGRATED_CORRIDOR_PASS_FORBIDDEN_IN_SLICE_B = (
    "integrated_corridor_pass_forbidden_in_slice_b"
)

FORBIDDEN_PROVIDER_PROPOSAL_FIELDS = frozenset(
    {
        "amount",
        "currency",
        "passenger_ref",
        "route_ref",
        "departure_date",
        "return_date",
        "hold_id",
        "merchant_ref",
        "ttl",
        "ttl_seconds",
        "idempotency_key",
        "adapter_id",
        "packet_id",
        "receipt_id",
        "root_owner",
        "created_by",
        "human_approval_ref",
        "purchase_intent_id",
        "payment_authorization_ref",
        "ticket_issue_intent_id",
    },
)

REQUIRED_LOCAL_BINDING_IDS = (
    "bsep_projection_to_selection_input",
    "client_constraints_to_selection_input",
    "candidate_snapshot_to_selection_input",
    "selection_input_to_actor_prompts",
    "validated_actor_outputs_to_synthesis",
    "synthesis_to_canonical_selection",
    "semantic_proposal_to_canonical_selection",
    "canonical_selection_to_client_root_decision",
    "client_root_decision_to_airline_root_resolution",
    "airline_root_resolution_to_hold_packet",
)

EXPECTED_BINDING_ROW_SURFACES = {
    "bsep_projection_to_selection_input": (
        "AirlineBSEPProjectionRefV01",
        "projection_ref",
        "AirlineSemanticSelectionInputV01",
        "source_bsep_projection_ref",
    ),
    "client_constraints_to_selection_input": (
        "ClientRootTravelConstraintSetV01",
        "constraint_set_id",
        "AirlineSemanticSelectionInputV01",
        "source_client_constraint_set_id",
    ),
    "candidate_snapshot_to_selection_input": (
        "AirlineRootOfferCandidateSetSnapshotV01",
        "candidate_set_digest",
        "AirlineSemanticSelectionInputV01",
        "source_candidate_set_digest",
    ),
    "selection_input_to_actor_prompts": (
        "AirlineSemanticSelectionInputV01",
        "selection_input_id",
        "AirlineCanonicalActorSelectionReviewV01",
        "source_selection_input_id",
    ),
    "validated_actor_outputs_to_synthesis": (
        "AirlineCanonicalActorSelectionReviewV01",
        "canonical_actor_output_id",
        "AirlineSemanticSelectionSynthesisReportV01",
        "canonical_actor_output_refs",
    ),
    "synthesis_to_canonical_selection": (
        "AirlineSemanticSelectionSynthesisReportV01",
        "synthesized_recommended_offer_id",
        "ValidatedAirlineSemanticSelectionEvidenceV01",
        "recommended_offer_id",
    ),
    "semantic_proposal_to_canonical_selection": (
        "AirlineSemanticOfferSelectionProposalV01",
        "proposal_id",
        "ValidatedAirlineSemanticSelectionEvidenceV01",
        "source_proposal_id",
    ),
    "canonical_selection_to_client_root_decision": (
        "ValidatedAirlineSemanticSelectionEvidenceV01",
        "recommended_offer_id",
        "ClientRootOfferSelectionDecisionV01",
        "recommended_offer_id",
    ),
    "client_root_decision_to_airline_root_resolution": (
        "ClientRootOfferSelectionDecisionV01",
        "selected_offer_id",
        "AirlineRootSelectedOfferResolutionV01",
        "selected_offer_id",
    ),
    "airline_root_resolution_to_hold_packet": (
        "AirlineRootSelectedOfferResolutionV01",
        "selected_offer_id",
        "AirlineHoldCommitPacketV01",
        "offer_id",
    ),
}


@dataclass(frozen=True)
class AirlineAuthoritativeOfferRecordV01:
    offer_id: str
    transaction_id: str
    airline_root_id: str
    amount: int
    currency: str
    route_ref: str
    departure_date: str
    return_date: str
    baggage_included: bool
    seat_characteristics: tuple[str, ...]
    changeable: bool
    overnight_layover: bool
    change_penalty_class: str
    inventory_available: bool
    airline_policy_valid: bool
    ttl_seconds: int
    expired: bool
    raw_secret_included: bool
    provider_created: bool
    real_world_effects_count: int


@dataclass(frozen=True)
class AirlineRootOfferCandidateSetSnapshotV01:
    candidate_set_ref: str
    candidate_set_snapshot_id: str
    candidate_set_version: str
    candidate_set_digest: str
    transaction_id: str
    airline_root_id: str
    authoritative_offer_records: tuple[AirlineAuthoritativeOfferRecordV01, ...]
    snapshot_created_at: str
    snapshot_ttl_seconds: int
    snapshot_expired: bool
    raw_secret_included: bool
    provider_created: bool
    real_world_effects_count: int


@dataclass(frozen=True)
class AirlineBSEPProjectionRefV01:
    projection_ref: str
    transaction_id: str
    projection_side: str
    validation_status: str
    raw_secret_included: bool
    authority_created: bool
    real_world_effects_count: int


@dataclass(frozen=True)
class ClientRootTravelConstraintSetV01:
    constraint_set_id: str
    transaction_id: str
    client_root_id: str
    travel_intent_ref: str
    origin: str
    destination: str
    departure_date: str
    return_date: str
    max_amount: int
    currency: str
    baggage_required: bool
    avoid_overnight_layover: bool
    preferred_seat_characteristics: tuple[str, ...]
    changeable_preferred: bool
    soft_preference_priority: tuple[str, ...]
    raw_passport_included: bool
    raw_payment_data_included: bool
    authority_transferred: bool
    real_world_effects_count: int


@dataclass(frozen=True)
class AirlineSemanticSelectionInputV01:
    selection_input_id: str
    transaction_id: str
    source_bsep_projection_ref: str
    source_client_constraint_set_id: str
    source_candidate_set_ref: str
    source_candidate_set_snapshot_id: str
    source_candidate_set_digest: str
    visible_candidate_ids: tuple[str, ...]
    airline_valid_candidate_ids: tuple[str, ...]
    client_hard_compatible_candidate_ids: tuple[str, ...]
    soft_tradeoff_candidate_ids: tuple[str, ...]
    raw_secret_included: bool
    provider_authority_created: bool
    real_world_effects_count: int


@dataclass(frozen=True)
class AirlineSemanticOfferSelectionProposalV01:
    proposal_id: str
    transaction_id: str
    actor_id: str
    source_selection_input_id: str
    source_bsep_projection_ref: str
    source_client_constraint_set_id: str
    source_candidate_set_snapshot_id: str
    source_candidate_set_digest: str
    candidate_set_ref: str
    recommended_offer_id: str
    ranked_offer_ids: tuple[str, ...]
    decision_factors: tuple[str, ...]
    preference_matches: tuple[str, ...]
    uncertainty_notes: tuple[str, ...]
    requires_root_review: bool
    semantic_summary: str
    authority_created: bool
    action_permission_created: bool
    packet_created: bool
    receipt_created: bool
    payment_created: bool
    ticket_created: bool
    booking_created: bool
    final_output_created: bool
    real_world_effects_count: int


@dataclass(frozen=True)
class AirlineCanonicalActorSelectionReviewV01:
    canonical_actor_output_id: str
    transaction_id: str
    actor_id: str
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
class AirlineSemanticSelectionSynthesisReportV01:
    synthesis_report_id: str
    transaction_id: str
    source_selection_input_id: str
    source_candidate_set_snapshot_id: str
    source_candidate_set_digest: str
    canonical_actor_output_refs: tuple[str, ...]
    proposer_actor_id: str
    compatibility_reviewer_actor_ids: tuple[str, ...]
    consistency_reviewer_actor_id: str
    actor_recommended_offer_ids: tuple[tuple[str, str], ...]
    actor_conflicts: tuple[str, ...]
    synthesis_status: str
    synthesized_recommended_offer_id: str
    accepted_semantic_factors: tuple[str, ...]
    rejected_semantic_factors: tuple[str, ...]
    unresolved_conflict_present: bool
    requires_client_root_review: bool
    what_runtime_used: tuple[str, ...]
    what_runtime_rejected: tuple[str, ...]
    authority_created: bool
    permission_created: bool
    provider_created_contract_artifact_count: int


@dataclass(frozen=True)
class ValidatedAirlineSemanticSelectionEvidenceV01:
    canonical_selection_id: str
    transaction_id: str
    source_actor_id: str
    source_proposal_id: str
    source_candidate_set_ref: str
    source_selection_input_id: str
    source_candidate_set_snapshot_id: str
    source_candidate_set_digest: str
    source_synthesis_report_id: str
    recommended_offer_id: str
    accepted_semantic_factors: tuple[str, ...]
    rejected_semantic_factors: tuple[str, ...]
    validation_status: str
    validation_errors: tuple[str, ...]
    what_runtime_used: tuple[str, ...]
    what_runtime_rejected: tuple[str, ...]
    advisory_only: bool
    evidence_only: bool
    authority_created: bool
    permission_created: bool
    real_world_effects_count: int


@dataclass(frozen=True)
class ClientRootOfferSelectionDecisionV01:
    decision_id: str
    transaction_id: str
    client_root_id: str
    source_canonical_selection_id: str
    source_candidate_set_snapshot_id: str
    source_candidate_set_digest: str
    recommended_offer_id: str
    selected_offer_id: str
    decision_status: str
    recommendation_accepted: bool
    root_override_used: bool
    root_override_reason: str
    semantic_influence_claimed: bool
    acceptance_reasons: tuple[str, ...]
    rejection_reasons: tuple[str, ...]
    created_by: str
    creates_purchase_permission: bool
    creates_payment_permission: bool
    creates_ticket_permission: bool
    requires_human_approval_before_purchase_intent: bool
    authority_transferred: bool
    real_world_effects_count: int


@dataclass(frozen=True)
class AirlineRootSelectedOfferResolutionV01:
    resolution_id: str
    transaction_id: str
    created_by: str
    airline_root_id: str
    source_client_root_decision_ref: str
    source_candidate_set_snapshot_id: str
    source_candidate_set_digest: str
    selected_offer_id: str
    authoritative_offer_ref: str
    resolved_offer_record_ref: str
    resolved_from_same_candidate_snapshot: bool
    resolved_amount: int
    resolved_currency: str
    resolved_route_ref: str
    resolved_baggage: bool
    resolved_seat_characteristics: tuple[str, ...]
    resolved_changeability: bool
    resolved_ttl: int
    offer_exists: bool
    offer_unexpired: bool
    airline_offer_validity_pass: bool
    client_constraint_compatibility_pass: bool
    semantic_values_used_as_authoritative_facts: bool
    real_world_effects_count: int


@dataclass(frozen=True)
class AirlineSemanticHoldContractBindingV01:
    binding_id: str
    transaction_id: str
    source_offer_resolution_ref: str
    source_candidate_set_snapshot_id: str
    source_candidate_set_digest: str
    hold_packet_id: str
    selected_offer_id: str
    values_match: bool
    authority_transferred: bool
    provider_created_target: bool
    real_world_effects_count: int


@dataclass(frozen=True)
class AirlineSemanticToContractBindingRowV01:
    binding_id: str
    transaction_id: str
    source_artifact_type: str
    source_artifact_id: str
    source_field: str
    source_value: str
    target_artifact_type: str
    target_artifact_id: str
    target_field: str
    target_value: str
    values_match: bool
    source_snapshot_id: str
    target_snapshot_id: str
    snapshot_match: bool
    causal_input_present: bool
    semantic_influence_present: bool
    authority_transferred: bool
    provider_created_target: bool


@dataclass(frozen=True)
class AirlineSemanticToContractBindingReportV01:
    binding_status: str
    transaction_id: str
    source_semantic_artifact_ref: str
    canonical_selection_ref: str
    client_root_decision_ref: str
    airline_root_resolution_ref: str
    selected_offer_id: str
    hold_packet_ref: str
    human_approval_ref: str
    purchase_intent_ref: str
    causal_binding_rows: tuple[AirlineSemanticToContractBindingRowV01, ...]
    silent_fallback_used: bool
    hardcoded_default_offer_used: bool
    provider_created_contract_artifact_count: int
    authority_transferred_count: int
    real_world_effects_count: int
    root_override_used: bool
    semantic_causality_claimed: bool
    required_binding_ids: tuple[str, ...]
    validation_errors: tuple[str, ...]
    integrated_corridor_causal_pass_claimed: bool


@dataclass(frozen=True)
class AirlineSemanticToContractValidationReportV01:
    validation_id: str
    artifact_type: str
    artifact_id: str
    transaction_id: str
    validation_status: str
    reason_codes: tuple[str, ...]
    return_to_root_required: bool
    relevant_root_id: str
    authority_created: bool
    permission_created: bool
    contract_artifact_created: bool
    real_world_effects_count: int


PROPOSAL_PAYLOAD_FIELDS = frozenset(
    AirlineSemanticOfferSelectionProposalV01.__dataclass_fields__,
)


def _dedupe(reasons: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    output: list[str] = []
    for reason in reasons:
        if reason not in output:
            output.append(reason)
    return tuple(output)


def _append_reason(reasons: list[str], reason: str) -> None:
    if reason not in reasons:
        reasons.append(reason)


def _report(
    *,
    artifact_type: str,
    artifact_id: str,
    transaction_id: str,
    reasons: list[str] | tuple[str, ...],
    relevant_root_id: str,
    validation_status: str | None = None,
    authority_created: bool = False,
    permission_created: bool = False,
    contract_artifact_created: bool = False,
    real_world_effects_count: int = 0,
) -> AirlineSemanticToContractValidationReportV01:
    status = validation_status or (STATUS_PASS if not reasons else STATUS_FAIL_CLOSED)
    if status == STATUS_FAIL_CLOSED and not reasons:
        reasons = (REASON_VALIDATION_FAILED,)
    reason_tuple = _dedupe(reasons)
    if reason_tuple and status in {
        STATUS_PASS,
        STATUS_ROOT_OVERRIDE,
        STATUS_LOCAL_MODEL_PASS,
    }:
        status = STATUS_FAIL_CLOSED
    return_to_root_required = status == STATUS_FAIL_CLOSED or bool(reason_tuple)
    return AirlineSemanticToContractValidationReportV01(
        validation_id=f"validation:{artifact_type}:{artifact_id}",
        artifact_type=artifact_type,
        artifact_id=artifact_id,
        transaction_id=transaction_id,
        validation_status=status,
        reason_codes=reason_tuple,
        return_to_root_required=return_to_root_required,
        relevant_root_id=relevant_root_id,
        authority_created=authority_created,
        permission_created=permission_created,
        contract_artifact_created=contract_artifact_created,
        real_world_effects_count=real_world_effects_count,
    )


def _route_ref_for_constraints(
    constraints: ClientRootTravelConstraintSetV01,
) -> str:
    return (
        f"route:{constraints.origin}-{constraints.destination}:"
        f"{constraints.departure_date}:{constraints.return_date}"
    )


def _records_by_offer_id(
    snapshot: AirlineRootOfferCandidateSetSnapshotV01,
) -> dict[str, AirlineAuthoritativeOfferRecordV01]:
    return {
        record.offer_id: record
        for record in snapshot.authoritative_offer_records
    }


def _snapshot_digest_matches(
    snapshot: AirlineRootOfferCandidateSetSnapshotV01,
) -> bool:
    return snapshot.candidate_set_digest == compute_airline_candidate_set_digest_v01(
        snapshot,
    )


def _snapshot_base_reasons(
    snapshot: AirlineRootOfferCandidateSetSnapshotV01,
) -> list[str]:
    reasons: list[str] = []
    if snapshot.transaction_id != TRANSACTION_ID:
        _append_reason(reasons, REASON_WRONG_TRANSACTION_ID)
    if snapshot.airline_root_id != AIRLINE_ROOT_ID:
        _append_reason(reasons, REASON_WRONG_ROOT_OWNER)
    if snapshot.candidate_set_version != CANDIDATE_SET_VERSION:
        _append_reason(reasons, REASON_CANDIDATE_SNAPSHOT_VERSION_MISMATCH)
    if snapshot.snapshot_expired or snapshot.snapshot_ttl_seconds <= 0:
        _append_reason(reasons, REASON_CANDIDATE_SNAPSHOT_EXPIRED)
    if snapshot.provider_created:
        _append_reason(reasons, REASON_PROVIDER_CREATED_CANDIDATE_SNAPSHOT)
    if snapshot.raw_secret_included:
        _append_reason(reasons, REASON_RAW_SECRET_IN_CANDIDATE_SNAPSHOT)
    if snapshot.real_world_effects_count != 0:
        _append_reason(reasons, REASON_NONZERO_REAL_WORLD_EFFECTS)
    if not _snapshot_digest_matches(snapshot):
        _append_reason(reasons, REASON_CANDIDATE_SNAPSHOT_DIGEST_MISMATCH)
    seen: set[str] = set()
    for record in snapshot.authoritative_offer_records:
        if record.offer_id in seen:
            _append_reason(reasons, REASON_UNKNOWN_CANDIDATE_ID)
        seen.add(record.offer_id)
        if record.transaction_id != snapshot.transaction_id:
            _append_reason(reasons, REASON_WRONG_TRANSACTION_ID)
        if record.airline_root_id != snapshot.airline_root_id:
            _append_reason(reasons, REASON_WRONG_ROOT_OWNER)
        if record.raw_secret_included:
            _append_reason(reasons, REASON_RAW_SECRET_IN_CANDIDATE_SNAPSHOT)
        if record.provider_created:
            _append_reason(reasons, REASON_PROVIDER_CREATED_CANDIDATE_SNAPSHOT)
        if record.real_world_effects_count != 0:
            _append_reason(reasons, REASON_NONZERO_REAL_WORLD_EFFECTS)
    return reasons


def _airline_valid_candidate_ids(
    snapshot: AirlineRootOfferCandidateSetSnapshotV01,
) -> tuple[str, ...]:
    if _snapshot_base_reasons(snapshot):
        return ()
    return tuple(
        record.offer_id
        for record in sorted(snapshot.authoritative_offer_records, key=lambda item: item.offer_id)
        if record.inventory_available
        and record.airline_policy_valid
        and not record.expired
        and record.ttl_seconds > 0
    )


def _client_hard_compatible_candidate_ids(
    constraints: ClientRootTravelConstraintSetV01,
    snapshot: AirlineRootOfferCandidateSetSnapshotV01,
) -> tuple[str, ...]:
    route_ref = _route_ref_for_constraints(constraints)
    return tuple(
        record.offer_id
        for record in sorted(snapshot.authoritative_offer_records, key=lambda item: item.offer_id)
        if record.offer_id in _airline_valid_candidate_ids(snapshot)
        and record.amount <= constraints.max_amount
        and record.currency == constraints.currency
        and record.route_ref == route_ref
        and record.departure_date == constraints.departure_date
        and record.return_date == constraints.return_date
        and (not constraints.baggage_required or record.baggage_included)
        and (
            not constraints.avoid_overnight_layover
            or not record.overnight_layover
        )
    )


def canonicalize_airline_candidate_snapshot_payload_v01(
    snapshot: AirlineRootOfferCandidateSetSnapshotV01,
) -> bytes:
    """Return stable JSON bytes for the local snapshot content identifier.

    This is a deterministic content identifier only. It is not a Crypto
    Artifact Seal: no signature, key management, or production integrity claim
    exists in Slice B.
    """

    records = [
        asdict(record)
        for record in sorted(
            snapshot.authoritative_offer_records,
            key=lambda item: item.offer_id,
        )
    ]
    payload = {
        "candidate_set_ref": snapshot.candidate_set_ref,
        "candidate_set_snapshot_id": snapshot.candidate_set_snapshot_id,
        "candidate_set_version": snapshot.candidate_set_version,
        "transaction_id": snapshot.transaction_id,
        "airline_root_id": snapshot.airline_root_id,
        "authoritative_offer_records": records,
        "snapshot_created_at": snapshot.snapshot_created_at,
        "snapshot_ttl_seconds": snapshot.snapshot_ttl_seconds,
        "snapshot_expired": snapshot.snapshot_expired,
        "raw_secret_included": snapshot.raw_secret_included,
        "provider_created": snapshot.provider_created,
        "real_world_effects_count": snapshot.real_world_effects_count,
    }
    return json.dumps(
        payload,
        ensure_ascii=True,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def compute_airline_candidate_set_digest_v01(
    snapshot: AirlineRootOfferCandidateSetSnapshotV01,
) -> str:
    return hashlib.sha256(
        canonicalize_airline_candidate_snapshot_payload_v01(snapshot),
    ).hexdigest()


def validate_airline_candidate_snapshot_v01(
    snapshot: AirlineRootOfferCandidateSetSnapshotV01,
) -> AirlineSemanticToContractValidationReportV01:
    reasons = _snapshot_base_reasons(snapshot)
    return _report(
        artifact_type="AirlineRootOfferCandidateSetSnapshotV01",
        artifact_id=snapshot.candidate_set_snapshot_id,
        transaction_id=snapshot.transaction_id,
        relevant_root_id=AIRLINE_ROOT_ID,
        reasons=reasons,
        authority_created=snapshot.provider_created,
        real_world_effects_count=snapshot.real_world_effects_count,
    )


def validate_airline_bsep_projection_ref_v01(
    projection: AirlineBSEPProjectionRefV01,
) -> AirlineSemanticToContractValidationReportV01:
    reasons: list[str] = []
    if projection.transaction_id != TRANSACTION_ID:
        _append_reason(reasons, REASON_WRONG_TRANSACTION_ID)
    if projection.projection_side != "airline_offer_selection":
        _append_reason(reasons, REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH)
    if projection.validation_status != STATUS_PASS:
        _append_reason(reasons, REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH)
    if projection.raw_secret_included:
        _append_reason(reasons, REASON_RAW_SECRET_IN_CANDIDATE_SNAPSHOT)
    if projection.authority_created:
        _append_reason(reasons, REASON_PROVIDER_CLAIMED_AUTHORITY)
    if projection.real_world_effects_count != 0:
        _append_reason(reasons, REASON_NONZERO_REAL_WORLD_EFFECTS)
    return _report(
        artifact_type="AirlineBSEPProjectionRefV01",
        artifact_id=projection.projection_ref,
        transaction_id=projection.transaction_id,
        relevant_root_id=CLIENT_ROOT_ID,
        reasons=reasons,
        authority_created=projection.authority_created,
        real_world_effects_count=projection.real_world_effects_count,
    )


def validate_client_root_travel_constraint_set_v01(
    constraints: ClientRootTravelConstraintSetV01,
) -> AirlineSemanticToContractValidationReportV01:
    reasons: list[str] = []
    if constraints.transaction_id != TRANSACTION_ID:
        _append_reason(reasons, REASON_WRONG_TRANSACTION_ID)
    if constraints.client_root_id != CLIENT_ROOT_ID:
        _append_reason(reasons, REASON_WRONG_ROOT_OWNER)
    required_values = (
        constraints.constraint_set_id,
        constraints.travel_intent_ref,
        constraints.origin,
        constraints.destination,
        constraints.departure_date,
        constraints.return_date,
        constraints.currency,
    )
    if any(not value for value in required_values) or constraints.max_amount <= 0:
        _append_reason(reasons, REASON_CLIENT_CONSTRAINT_SET_INVALID)
    if constraints.raw_passport_included or constraints.raw_payment_data_included:
        _append_reason(reasons, REASON_CLIENT_CONSTRAINT_SET_INVALID)
    if constraints.authority_transferred:
        _append_reason(reasons, REASON_AUTHORITY_TRANSFER_FORBIDDEN)
    if constraints.real_world_effects_count != 0:
        _append_reason(reasons, REASON_NONZERO_REAL_WORLD_EFFECTS)
    return _report(
        artifact_type="ClientRootTravelConstraintSetV01",
        artifact_id=constraints.constraint_set_id,
        transaction_id=constraints.transaction_id,
        relevant_root_id=CLIENT_ROOT_ID,
        reasons=reasons,
        authority_created=constraints.authority_transferred,
        real_world_effects_count=constraints.real_world_effects_count,
    )


def validate_airline_semantic_selection_input_v01(
    bsep_projection: AirlineBSEPProjectionRefV01,
    constraints: ClientRootTravelConstraintSetV01,
    snapshot: AirlineRootOfferCandidateSetSnapshotV01,
    selection_input: AirlineSemanticSelectionInputV01,
) -> AirlineSemanticToContractValidationReportV01:
    reasons = list(
        validate_airline_bsep_projection_ref_v01(bsep_projection).reason_codes,
    )
    reasons.extend(
        validate_client_root_travel_constraint_set_v01(constraints).reason_codes,
    )
    reasons.extend(validate_airline_candidate_snapshot_v01(snapshot).reason_codes)
    expected_visible = tuple(
        record.offer_id
        for record in sorted(snapshot.authoritative_offer_records, key=lambda item: item.offer_id)
    )
    expected_airline_valid = _airline_valid_candidate_ids(snapshot)
    expected_client_compatible = _client_hard_compatible_candidate_ids(
        constraints,
        snapshot,
    )
    if selection_input.transaction_id != TRANSACTION_ID:
        _append_reason(reasons, REASON_WRONG_TRANSACTION_ID)
    if selection_input.source_bsep_projection_ref != bsep_projection.projection_ref:
        _append_reason(reasons, REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH)
    if selection_input.source_client_constraint_set_id != constraints.constraint_set_id:
        _append_reason(reasons, REASON_CLIENT_CONSTRAINT_SET_INVALID)
    if selection_input.source_candidate_set_ref != snapshot.candidate_set_ref:
        _append_reason(reasons, REASON_SELECTION_INPUT_SNAPSHOT_MISMATCH)
    if (
        selection_input.source_candidate_set_snapshot_id
        != snapshot.candidate_set_snapshot_id
        or selection_input.source_candidate_set_digest != snapshot.candidate_set_digest
    ):
        _append_reason(reasons, REASON_SELECTION_INPUT_SNAPSHOT_MISMATCH)
    if selection_input.visible_candidate_ids != expected_visible:
        _append_reason(reasons, REASON_UNKNOWN_CANDIDATE_ID)
    if selection_input.airline_valid_candidate_ids != expected_airline_valid:
        _append_reason(reasons, REASON_AIRLINE_OFFER_VALIDITY_FAILED)
    if (
        selection_input.client_hard_compatible_candidate_ids
        != expected_client_compatible
    ):
        _append_reason(reasons, REASON_CLIENT_CONSTRAINT_COMPATIBILITY_FAILED)
    if selection_input.soft_tradeoff_candidate_ids != expected_client_compatible:
        _append_reason(reasons, REASON_SOFT_PREFERENCE_REWROTE_HARD_CONSTRAINT)
    if selection_input.raw_secret_included:
        _append_reason(reasons, REASON_CLIENT_CONSTRAINT_SET_INVALID)
    if selection_input.provider_authority_created:
        _append_reason(reasons, REASON_PROVIDER_CLAIMED_AUTHORITY)
    if selection_input.real_world_effects_count != 0:
        _append_reason(reasons, REASON_NONZERO_REAL_WORLD_EFFECTS)
    return _report(
        artifact_type="AirlineSemanticSelectionInputV01",
        artifact_id=selection_input.selection_input_id,
        transaction_id=selection_input.transaction_id,
        relevant_root_id=AIRLINE_ROOT_ID,
        reasons=reasons,
        authority_created=selection_input.provider_authority_created,
        real_world_effects_count=selection_input.real_world_effects_count,
    )


STRING_PROPOSAL_FIELDS = frozenset(
    {
        "proposal_id",
        "transaction_id",
        "actor_id",
        "source_selection_input_id",
        "source_bsep_projection_ref",
        "source_client_constraint_set_id",
        "source_candidate_set_snapshot_id",
        "source_candidate_set_digest",
        "candidate_set_ref",
        "recommended_offer_id",
        "semantic_summary",
    },
)
SEQUENCE_PROPOSAL_FIELDS = frozenset(
    {
        "ranked_offer_ids",
        "decision_factors",
        "preference_matches",
        "uncertainty_notes",
    },
)
BOOLEAN_PROPOSAL_FIELDS = frozenset(
    {
        "requires_root_review",
        "authority_created",
        "action_permission_created",
        "packet_created",
        "receipt_created",
        "payment_created",
        "ticket_created",
        "booking_created",
        "final_output_created",
    },
)


def _proposal_artifact_id_from_payload(payload: Any) -> str:
    if isinstance(payload, Mapping):
        proposal_id = payload.get("proposal_id")
        if type(proposal_id) is str and proposal_id.strip():
            return proposal_id
    return "untyped_payload"


def _proposal_transaction_id_from_payload(
    selection_input: AirlineSemanticSelectionInputV01,
    payload: Any,
) -> str:
    if isinstance(payload, Mapping):
        transaction_id = payload.get("transaction_id")
        if type(transaction_id) is str and transaction_id.strip():
            return transaction_id
    return selection_input.transaction_id


def _validate_proposal_payload_shape_v01(
    payload: Any,
) -> list[str]:
    reasons: list[str] = []
    if not isinstance(payload, Mapping):
        _append_reason(reasons, REASON_INVALID_PROVIDER_OUTPUT_CONTAINER)
        return reasons
    payload_keys = set(payload.keys())
    missing = PROPOSAL_PAYLOAD_FIELDS - payload_keys
    if missing:
        _append_reason(reasons, REASON_MISSING_PROVIDER_OUTPUT_FIELD)
    if payload_keys & FORBIDDEN_PROVIDER_PROPOSAL_FIELDS:
        _append_reason(reasons, REASON_FORBIDDEN_PROVIDER_AUTHORITATIVE_FIELD)
    unknown = payload_keys - PROPOSAL_PAYLOAD_FIELDS
    if unknown:
        _append_reason(reasons, REASON_UNKNOWN_PROVIDER_OUTPUT_FIELD)
    for field in sorted(STRING_PROPOSAL_FIELDS & payload_keys):
        value = payload[field]
        if type(value) is not str:
            _append_reason(reasons, REASON_INVALID_PROVIDER_OUTPUT_TYPE)
        elif not value.strip():
            _append_reason(reasons, REASON_EMPTY_PROVIDER_OUTPUT_FIELD)
    for field in sorted(SEQUENCE_PROPOSAL_FIELDS & payload_keys):
        value = payload[field]
        if type(value) not in {tuple, list}:
            _append_reason(reasons, REASON_INVALID_PROVIDER_OUTPUT_CONTAINER)
            continue
        if not value:
            _append_reason(reasons, REASON_EMPTY_PROVIDER_OUTPUT_FIELD)
        for item in value:
            if type(item) is not str:
                _append_reason(reasons, REASON_INVALID_PROVIDER_OUTPUT_TYPE)
            elif not item.strip():
                _append_reason(reasons, REASON_EMPTY_PROVIDER_OUTPUT_FIELD)
    for field in sorted(BOOLEAN_PROPOSAL_FIELDS & payload_keys):
        if type(payload[field]) is not bool:
            _append_reason(reasons, REASON_INVALID_PROVIDER_OUTPUT_TYPE)
    if "real_world_effects_count" in payload_keys:
        effect_count = payload["real_world_effects_count"]
        if type(effect_count) is not int or type(effect_count) is bool:
            _append_reason(reasons, REASON_INVALID_PROVIDER_OUTPUT_TYPE)
        elif effect_count != 0:
            _append_reason(reasons, REASON_PROVIDER_CLAIMED_EFFECT)
    return reasons


def _proposal_from_validated_payload_v01(
    payload: Mapping[str, Any],
) -> AirlineSemanticOfferSelectionProposalV01:
    return AirlineSemanticOfferSelectionProposalV01(
        proposal_id=payload["proposal_id"],
        transaction_id=payload["transaction_id"],
        actor_id=payload["actor_id"],
        source_selection_input_id=payload["source_selection_input_id"],
        source_bsep_projection_ref=payload["source_bsep_projection_ref"],
        source_client_constraint_set_id=payload["source_client_constraint_set_id"],
        source_candidate_set_snapshot_id=payload["source_candidate_set_snapshot_id"],
        source_candidate_set_digest=payload["source_candidate_set_digest"],
        candidate_set_ref=payload["candidate_set_ref"],
        recommended_offer_id=payload["recommended_offer_id"],
        ranked_offer_ids=tuple(payload["ranked_offer_ids"]),
        decision_factors=tuple(payload["decision_factors"]),
        preference_matches=tuple(payload["preference_matches"]),
        uncertainty_notes=tuple(payload["uncertainty_notes"]),
        requires_root_review=payload["requires_root_review"],
        semantic_summary=payload["semantic_summary"],
        authority_created=payload["authority_created"],
        action_permission_created=payload["action_permission_created"],
        packet_created=payload["packet_created"],
        receipt_created=payload["receipt_created"],
        payment_created=payload["payment_created"],
        ticket_created=payload["ticket_created"],
        booking_created=payload["booking_created"],
        final_output_created=payload["final_output_created"],
        real_world_effects_count=payload["real_world_effects_count"],
    )


def validate_airline_semantic_offer_selection_proposal_payload_v01(
    selection_input: AirlineSemanticSelectionInputV01,
    payload: Any,
) -> AirlineSemanticToContractValidationReportV01:
    reasons = _validate_proposal_payload_shape_v01(payload)
    proposal_id = _proposal_artifact_id_from_payload(payload)
    transaction_id = _proposal_transaction_id_from_payload(selection_input, payload)
    if reasons:
        return _report(
            artifact_type="AirlineSemanticOfferSelectionProposalPayloadV01",
            artifact_id=proposal_id,
            transaction_id=transaction_id,
            relevant_root_id=CLIENT_ROOT_ID,
            reasons=reasons,
        )
    proposal = _proposal_from_validated_payload_v01(payload)
    return validate_airline_semantic_offer_selection_proposal_v01(
        selection_input,
        proposal,
    )


def build_airline_semantic_offer_selection_proposal_from_payload_v01(
    selection_input: AirlineSemanticSelectionInputV01,
    payload: Any,
) -> tuple[AirlineSemanticOfferSelectionProposalV01 | None, AirlineSemanticToContractValidationReportV01]:
    report = validate_airline_semantic_offer_selection_proposal_payload_v01(
        selection_input,
        payload,
    )
    if report.validation_status != STATUS_PASS:
        return None, report
    proposal = _proposal_from_validated_payload_v01(payload)
    return proposal, report


def validate_airline_semantic_offer_selection_proposal_v01(
    selection_input: AirlineSemanticSelectionInputV01,
    proposal: AirlineSemanticOfferSelectionProposalV01,
) -> AirlineSemanticToContractValidationReportV01:
    reasons: list[str] = []
    if proposal.transaction_id != selection_input.transaction_id:
        _append_reason(reasons, REASON_WRONG_TRANSACTION_ID)
    if proposal.actor_id != ACTOR_CLIENT_PURCHASE_INTENT_REVIEWER:
        _append_reason(reasons, REASON_ACTOR_ROLE_MISMATCH)
    if proposal.source_selection_input_id != selection_input.selection_input_id:
        _append_reason(reasons, REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH)
    if proposal.source_bsep_projection_ref != selection_input.source_bsep_projection_ref:
        _append_reason(reasons, REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH)
    if (
        proposal.source_client_constraint_set_id
        != selection_input.source_client_constraint_set_id
    ):
        _append_reason(reasons, REASON_CLIENT_CONSTRAINT_SET_INVALID)
    if proposal.candidate_set_ref != selection_input.source_candidate_set_ref:
        _append_reason(reasons, REASON_SELECTION_INPUT_SNAPSHOT_MISMATCH)
    if (
        proposal.source_candidate_set_snapshot_id
        != selection_input.source_candidate_set_snapshot_id
        or proposal.source_candidate_set_digest
        != selection_input.source_candidate_set_digest
    ):
        _append_reason(reasons, REASON_SELECTION_INPUT_SNAPSHOT_MISMATCH)
    visible = set(selection_input.visible_candidate_ids)
    if proposal.recommended_offer_id not in visible:
        _append_reason(reasons, REASON_UNKNOWN_CANDIDATE_ID)
    if len(set(proposal.ranked_offer_ids)) != len(proposal.ranked_offer_ids):
        _append_reason(reasons, REASON_DUPLICATE_RANKED_OFFER_ID)
    if any(offer_id not in visible for offer_id in proposal.ranked_offer_ids):
        _append_reason(reasons, REASON_UNKNOWN_CANDIDATE_ID)
    if proposal.ranked_offer_ids.count(proposal.recommended_offer_id) != 1:
        _append_reason(reasons, REASON_RECOMMENDED_OFFER_MISSING_FROM_RANKING)
    if not proposal.requires_root_review:
        _append_reason(reasons, REASON_ACTOR_OUTPUT_NOT_VALIDATED)
    if (
        not proposal.decision_factors
        or not proposal.preference_matches
        or not proposal.uncertainty_notes
        or not proposal.semantic_summary
    ):
        _append_reason(reasons, REASON_ACTOR_OUTPUT_NOT_VALIDATED)
    if proposal.authority_created:
        _append_reason(reasons, REASON_PROVIDER_CLAIMED_AUTHORITY)
    if (
        proposal.action_permission_created
        or proposal.packet_created
        or proposal.receipt_created
        or proposal.payment_created
        or proposal.ticket_created
        or proposal.booking_created
        or proposal.final_output_created
    ):
        _append_reason(reasons, REASON_PROVIDER_CLAIMED_ACTION)
    if proposal.real_world_effects_count != 0:
        _append_reason(reasons, REASON_PROVIDER_CLAIMED_EFFECT)
    return _report(
        artifact_type="AirlineSemanticOfferSelectionProposalV01",
        artifact_id=proposal.proposal_id,
        transaction_id=proposal.transaction_id,
        relevant_root_id=CLIENT_ROOT_ID,
        reasons=reasons,
        authority_created=proposal.authority_created,
        permission_created=proposal.action_permission_created,
        contract_artifact_created=proposal.packet_created or proposal.receipt_created,
        real_world_effects_count=proposal.real_world_effects_count,
    )


def validate_airline_canonical_actor_selection_review_v01(
    selection_input: AirlineSemanticSelectionInputV01,
    review: AirlineCanonicalActorSelectionReviewV01,
) -> AirlineSemanticToContractValidationReportV01:
    reasons: list[str] = []
    if not review.canonical_actor_output_id:
        _append_reason(reasons, REASON_ACTOR_OUTPUT_NOT_VALIDATED)
    if review.transaction_id != selection_input.transaction_id:
        _append_reason(reasons, REASON_WRONG_TRANSACTION_ID)
    if review.source_selection_input_id != selection_input.selection_input_id:
        _append_reason(reasons, REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH)
    if (
        review.source_candidate_set_snapshot_id
        != selection_input.source_candidate_set_snapshot_id
        or review.source_candidate_set_digest
        != selection_input.source_candidate_set_digest
    ):
        _append_reason(reasons, REASON_SELECTION_INPUT_SNAPSHOT_MISMATCH)
    if REQUIRED_ACTOR_ROLES.get(review.actor_id) != review.review_role:
        _append_reason(reasons, REASON_ACTOR_ROLE_MISMATCH)
    if review.reviewed_offer_id not in selection_input.visible_candidate_ids:
        _append_reason(reasons, REASON_UNKNOWN_CANDIDATE_ID)
    if review.validation_status != STATUS_PASS or review.review_status != STATUS_PASS:
        _append_reason(reasons, REASON_ACTOR_OUTPUT_NOT_VALIDATED)
    if not review.semantic_factors:
        _append_reason(reasons, REASON_ACTOR_OUTPUT_NOT_VALIDATED)
    if review.review_status == STATUS_PASS and review.blocking_conflicts:
        _append_reason(reasons, REASON_MULTI_ACTOR_CONFLICT)
    if review.review_status == STATUS_PASS and not review.supports_proposed_offer:
        _append_reason(reasons, REASON_ACTOR_OUTPUT_NOT_VALIDATED)
    if review.raw_output_used:
        _append_reason(reasons, REASON_ACTOR_OUTPUT_NOT_VALIDATED)
    if review.authority_created:
        _append_reason(reasons, REASON_PROVIDER_CLAIMED_AUTHORITY)
    if review.permission_created:
        _append_reason(reasons, REASON_PROVIDER_CLAIMED_ACTION)
    if review.real_world_effects_count != 0:
        _append_reason(reasons, REASON_NONZERO_REAL_WORLD_EFFECTS)
    return _report(
        artifact_type="AirlineCanonicalActorSelectionReviewV01",
        artifact_id=review.canonical_actor_output_id,
        transaction_id=review.transaction_id,
        relevant_root_id=CLIENT_ROOT_ID,
        reasons=reasons,
        authority_created=review.authority_created,
        permission_created=review.permission_created,
        real_world_effects_count=review.real_world_effects_count,
    )


def validate_airline_semantic_selection_synthesis_report_v01(
    selection_input: AirlineSemanticSelectionInputV01,
    actor_reviews: tuple[AirlineCanonicalActorSelectionReviewV01, ...],
    synthesis: AirlineSemanticSelectionSynthesisReportV01,
) -> AirlineSemanticToContractValidationReportV01:
    reasons: list[str] = []
    if synthesis.transaction_id != selection_input.transaction_id:
        _append_reason(reasons, REASON_WRONG_TRANSACTION_ID)
    if synthesis.source_selection_input_id != selection_input.selection_input_id:
        _append_reason(reasons, REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH)
    if (
        synthesis.source_candidate_set_snapshot_id
        != selection_input.source_candidate_set_snapshot_id
        or synthesis.source_candidate_set_digest
        != selection_input.source_candidate_set_digest
    ):
        _append_reason(reasons, REASON_SELECTION_INPUT_SNAPSHOT_MISMATCH)
    actor_ids = tuple(review.actor_id for review in actor_reviews)
    if len(actor_reviews) != 5:
        _append_reason(reasons, REASON_MISSING_REQUIRED_ACTOR_OUTPUT)
    if len(actor_ids) != len(set(actor_ids)):
        _append_reason(reasons, REASON_DUPLICATE_ACTOR_OUTPUT)
    if set(actor_ids) != set(REQUIRED_ACTOR_ROLES):
        _append_reason(reasons, REASON_MISSING_REQUIRED_ACTOR_OUTPUT)
    canonical_ids = tuple(review.canonical_actor_output_id for review in actor_reviews)
    if len(canonical_ids) != len(set(canonical_ids)):
        _append_reason(reasons, REASON_DUPLICATE_ACTOR_OUTPUT)
    if synthesis.proposer_actor_id != ACTOR_CLIENT_PURCHASE_INTENT_REVIEWER:
        _append_reason(reasons, REASON_ACTOR_ROLE_MISMATCH)
    if set(synthesis.compatibility_reviewer_actor_ids) != {
        ACTOR_AIRLINE_OFFER_POLICY_REVIEWER,
        ACTOR_AIRLINE_FARE_RULES_VERTICAL_CELL,
        ACTOR_AIRLINE_SEAT_BAGGAGE_VERTICAL_CELL,
    }:
        _append_reason(reasons, REASON_ACTOR_ROLE_MISMATCH)
    if (
        synthesis.consistency_reviewer_actor_id
        != ACTOR_TRI_PARTY_EVIDENCE_CONSISTENCY_REVIEWER
    ):
        _append_reason(reasons, REASON_ACTOR_ROLE_MISMATCH)
    for review in actor_reviews:
        reasons.extend(
            validate_airline_canonical_actor_selection_review_v01(
                selection_input,
                review,
            ).reason_codes,
        )
    refs = tuple(review.canonical_actor_output_id for review in actor_reviews)
    if refs != synthesis.canonical_actor_output_refs:
        _append_reason(reasons, REASON_MISSING_REQUIRED_ACTOR_OUTPUT)
    actor_offer_pairs = tuple(
        (review.actor_id, review.reviewed_offer_id)
        for review in actor_reviews
    )
    if actor_offer_pairs != synthesis.actor_recommended_offer_ids:
        _append_reason(reasons, REASON_MULTI_ACTOR_CONFLICT)
    reviewed_offer_ids = tuple(review.reviewed_offer_id for review in actor_reviews)
    if any(
        offer_id != synthesis.synthesized_recommended_offer_id
        for offer_id in reviewed_offer_ids
    ):
        _append_reason(reasons, REASON_MULTI_ACTOR_CONFLICT)
        _append_reason(reasons, REASON_HIDDEN_ACTOR_PRIORITY_FORBIDDEN)
    if any(
        review.review_status == STATUS_PASS and not review.supports_proposed_offer
        for review in actor_reviews
    ):
        _append_reason(reasons, REASON_ACTOR_OUTPUT_NOT_VALIDATED)
    if any(review.blocking_conflicts for review in actor_reviews):
        _append_reason(reasons, REASON_MULTI_ACTOR_CONFLICT)
    if synthesis.actor_conflicts or synthesis.unresolved_conflict_present:
        _append_reason(reasons, REASON_UNRESOLVED_CONFLICT)
    if not synthesis.requires_client_root_review:
        _append_reason(reasons, REASON_SYNTHESIS_NOT_PASS)
    if synthesis.synthesis_status != STATUS_PASS:
        _append_reason(reasons, REASON_SYNTHESIS_NOT_PASS)
    if synthesis.synthesized_recommended_offer_id not in selection_input.visible_candidate_ids:
        _append_reason(reasons, REASON_UNKNOWN_CANDIDATE_ID)
    if (
        not synthesis.accepted_semantic_factors
        or not synthesis.rejected_semantic_factors
        or not synthesis.what_runtime_used
        or not synthesis.what_runtime_rejected
    ):
        _append_reason(reasons, REASON_SYNTHESIS_NOT_PASS)
    if synthesis.authority_created:
        _append_reason(reasons, REASON_PROVIDER_CLAIMED_AUTHORITY)
    if synthesis.permission_created or synthesis.provider_created_contract_artifact_count:
        _append_reason(reasons, REASON_PROVIDER_CLAIMED_ACTION)
    return _report(
        artifact_type="AirlineSemanticSelectionSynthesisReportV01",
        artifact_id=synthesis.synthesis_report_id,
        transaction_id=synthesis.transaction_id,
        relevant_root_id=CLIENT_ROOT_ID,
        reasons=reasons,
        authority_created=synthesis.authority_created,
        permission_created=synthesis.permission_created,
        contract_artifact_created=bool(
            synthesis.provider_created_contract_artifact_count,
        ),
    )


def validate_validated_airline_semantic_selection_evidence_v01(
    selection_input: AirlineSemanticSelectionInputV01,
    proposal: AirlineSemanticOfferSelectionProposalV01,
    actor_reviews: tuple[AirlineCanonicalActorSelectionReviewV01, ...],
    synthesis: AirlineSemanticSelectionSynthesisReportV01,
    evidence: ValidatedAirlineSemanticSelectionEvidenceV01,
) -> AirlineSemanticToContractValidationReportV01:
    reasons = list(
        validate_airline_semantic_offer_selection_proposal_v01(
            selection_input,
            proposal,
        ).reason_codes,
    )
    reasons.extend(
        validate_airline_semantic_selection_synthesis_report_v01(
            selection_input,
            actor_reviews,
            synthesis,
        ).reason_codes,
    )
    if evidence.transaction_id != selection_input.transaction_id:
        _append_reason(reasons, REASON_WRONG_TRANSACTION_ID)
    if (
        not proposal.proposal_id
        or not evidence.canonical_selection_id
        or not evidence.source_proposal_id
        or not evidence.source_actor_id
        or not evidence.source_candidate_set_ref
    ):
        _append_reason(reasons, REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH)
    if evidence.source_proposal_id != proposal.proposal_id:
        _append_reason(reasons, REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH)
    if evidence.source_actor_id != proposal.actor_id:
        _append_reason(reasons, REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH)
    if evidence.source_candidate_set_ref != proposal.candidate_set_ref:
        _append_reason(reasons, REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH)
    if evidence.source_candidate_set_ref != selection_input.source_candidate_set_ref:
        _append_reason(reasons, REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH)
    if (
        evidence.source_selection_input_id != proposal.source_selection_input_id
        or proposal.source_selection_input_id != selection_input.selection_input_id
    ):
        _append_reason(reasons, REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH)
    if evidence.source_synthesis_report_id != synthesis.synthesis_report_id:
        _append_reason(reasons, REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH)
    if (
        evidence.source_candidate_set_snapshot_id != proposal.source_candidate_set_snapshot_id
        or proposal.source_candidate_set_snapshot_id
        != selection_input.source_candidate_set_snapshot_id
        or evidence.source_candidate_set_digest != proposal.source_candidate_set_digest
        or proposal.source_candidate_set_digest
        != selection_input.source_candidate_set_digest
    ):
        _append_reason(reasons, REASON_SELECTION_INPUT_SNAPSHOT_MISMATCH)
    if evidence.recommended_offer_id != proposal.recommended_offer_id:
        _append_reason(reasons, REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH)
    if evidence.recommended_offer_id != synthesis.synthesized_recommended_offer_id:
        _append_reason(reasons, REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH)
    if evidence.accepted_semantic_factors != synthesis.accepted_semantic_factors:
        _append_reason(reasons, REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH)
    if evidence.rejected_semantic_factors != synthesis.rejected_semantic_factors:
        _append_reason(reasons, REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH)
    if evidence.recommended_offer_id not in selection_input.visible_candidate_ids:
        _append_reason(reasons, REASON_UNKNOWN_CANDIDATE_ID)
    if evidence.validation_status != STATUS_PASS or evidence.validation_errors:
        _append_reason(reasons, REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH)
    if not evidence.advisory_only or not evidence.evidence_only:
        _append_reason(reasons, REASON_PROVIDER_CLAIMED_AUTHORITY)
    if evidence.authority_created:
        _append_reason(reasons, REASON_PROVIDER_CLAIMED_AUTHORITY)
    if evidence.permission_created:
        _append_reason(reasons, REASON_PROVIDER_CLAIMED_ACTION)
    if evidence.real_world_effects_count != 0:
        _append_reason(reasons, REASON_NONZERO_REAL_WORLD_EFFECTS)
    required_rejections = {
        "provider_output_as_truth_rejected",
        "provider_output_as_authority_rejected",
        "provider_supplied_authoritative_facts_rejected",
        "provider_created_contract_artifacts_rejected",
    }
    if not evidence.what_runtime_used or not required_rejections.issubset(
        set(evidence.what_runtime_rejected),
    ):
        _append_reason(reasons, REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH)
    return _report(
        artifact_type="ValidatedAirlineSemanticSelectionEvidenceV01",
        artifact_id=evidence.canonical_selection_id,
        transaction_id=evidence.transaction_id,
        relevant_root_id=CLIENT_ROOT_ID,
        reasons=reasons,
        authority_created=evidence.authority_created,
        permission_created=evidence.permission_created,
        real_world_effects_count=evidence.real_world_effects_count,
    )


def validate_client_root_offer_selection_decision_v01(
    selection_input: AirlineSemanticSelectionInputV01,
    evidence: ValidatedAirlineSemanticSelectionEvidenceV01,
    decision: ClientRootOfferSelectionDecisionV01,
) -> AirlineSemanticToContractValidationReportV01:
    reasons: list[str] = []
    if decision.transaction_id != selection_input.transaction_id:
        _append_reason(reasons, REASON_WRONG_TRANSACTION_ID)
    if decision.client_root_id != CLIENT_ROOT_ID or decision.created_by != CLIENT_ROOT_ID:
        _append_reason(reasons, REASON_WRONG_ROOT_OWNER)
    if decision.source_canonical_selection_id != evidence.canonical_selection_id:
        _append_reason(reasons, REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH)
    if (
        decision.source_candidate_set_snapshot_id
        != selection_input.source_candidate_set_snapshot_id
        or decision.source_candidate_set_digest
        != selection_input.source_candidate_set_digest
    ):
        _append_reason(reasons, REASON_SELECTION_INPUT_SNAPSHOT_MISMATCH)
    if decision.recommended_offer_id != evidence.recommended_offer_id:
        _append_reason(reasons, REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH)
    if decision.selected_offer_id not in selection_input.client_hard_compatible_candidate_ids:
        _append_reason(reasons, REASON_CLIENT_CONSTRAINT_COMPATIBILITY_FAILED)
    if decision.decision_status == STATUS_CAUSAL_PASS:
        expected_status = STATUS_PASS
        if not decision.recommendation_accepted or decision.root_override_used:
            _append_reason(reasons, REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH)
        if decision.root_override_reason:
            _append_reason(reasons, REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH)
        if decision.selected_offer_id != decision.recommended_offer_id:
            _append_reason(reasons, REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH)
        if not decision.semantic_influence_claimed:
            _append_reason(reasons, REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH)
        if not decision.acceptance_reasons or decision.rejection_reasons:
            _append_reason(reasons, REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH)
    elif decision.decision_status == STATUS_ROOT_OVERRIDE:
        expected_status = STATUS_ROOT_OVERRIDE
        if decision.recommendation_accepted or not decision.root_override_used:
            _append_reason(reasons, REASON_ROOT_OVERRIDE_CANNOT_CLAIM_SEMANTIC_CAUSALITY)
        if not decision.root_override_reason:
            _append_reason(reasons, REASON_ROOT_OVERRIDE_CANNOT_CLAIM_SEMANTIC_CAUSALITY)
        if decision.semantic_influence_claimed:
            _append_reason(reasons, REASON_ROOT_OVERRIDE_CANNOT_CLAIM_SEMANTIC_CAUSALITY)
    elif decision.decision_status == STATUS_REJECTED:
        expected_status = STATUS_FAIL_CLOSED
        _append_reason(reasons, REASON_CLIENT_ROOT_DECISION_REJECTED)
        if decision.recommendation_accepted or decision.semantic_influence_claimed:
            _append_reason(reasons, REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH)
        if not decision.rejection_reasons:
            _append_reason(reasons, REASON_CLIENT_CONSTRAINT_COMPATIBILITY_FAILED)
    else:
        expected_status = STATUS_FAIL_CLOSED
        _append_reason(reasons, REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH)
    if (
        decision.creates_purchase_permission
        or decision.creates_payment_permission
        or decision.creates_ticket_permission
    ):
        _append_reason(reasons, REASON_PROVIDER_CLAIMED_ACTION)
    if not decision.requires_human_approval_before_purchase_intent:
        _append_reason(reasons, REASON_PROVIDER_CLAIMED_ACTION)
    if decision.authority_transferred:
        _append_reason(reasons, REASON_AUTHORITY_TRANSFER_FORBIDDEN)
    if decision.real_world_effects_count != 0:
        _append_reason(reasons, REASON_NONZERO_REAL_WORLD_EFFECTS)
    if reasons:
        expected_status = STATUS_FAIL_CLOSED
    return _report(
        artifact_type="ClientRootOfferSelectionDecisionV01",
        artifact_id=decision.decision_id,
        transaction_id=decision.transaction_id,
        relevant_root_id=CLIENT_ROOT_ID,
        reasons=reasons,
        validation_status=expected_status,
        authority_created=decision.authority_transferred,
        permission_created=(
            decision.creates_purchase_permission
            or decision.creates_payment_permission
            or decision.creates_ticket_permission
        ),
        real_world_effects_count=decision.real_world_effects_count,
    )


def validate_airline_root_selected_offer_resolution_v01(
    selection_input: AirlineSemanticSelectionInputV01,
    snapshot: AirlineRootOfferCandidateSetSnapshotV01,
    evidence: ValidatedAirlineSemanticSelectionEvidenceV01,
    decision: ClientRootOfferSelectionDecisionV01,
    resolution: AirlineRootSelectedOfferResolutionV01,
) -> AirlineSemanticToContractValidationReportV01:
    decision_report = validate_client_root_offer_selection_decision_v01(
        selection_input,
        evidence,
        decision,
    )
    reasons: list[str] = list(decision_report.reason_codes)
    if decision_report.validation_status not in {STATUS_PASS, STATUS_ROOT_OVERRIDE}:
        _append_reason(reasons, REASON_CLIENT_ROOT_DECISION_REJECTED)
    if resolution.transaction_id != TRANSACTION_ID:
        _append_reason(reasons, REASON_WRONG_TRANSACTION_ID)
    if resolution.airline_root_id != AIRLINE_ROOT_ID or resolution.created_by != AIRLINE_ROOT_ID:
        _append_reason(reasons, REASON_WRONG_ROOT_OWNER)
    if resolution.source_client_root_decision_ref != decision.decision_id:
        _append_reason(reasons, REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH)
    if resolution.selected_offer_id != decision.selected_offer_id:
        _append_reason(reasons, REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH)
    if (
        resolution.source_candidate_set_snapshot_id != snapshot.candidate_set_snapshot_id
        or resolution.source_candidate_set_digest != snapshot.candidate_set_digest
        or resolution.source_candidate_set_snapshot_id
        != selection_input.source_candidate_set_snapshot_id
        or resolution.source_candidate_set_digest
        != selection_input.source_candidate_set_digest
    ):
        _append_reason(reasons, REASON_SNAPSHOT_SUBSTITUTION_DETECTED)
    if validate_airline_candidate_snapshot_v01(snapshot).validation_status != STATUS_PASS:
        _append_reason(reasons, REASON_AIRLINE_OFFER_VALIDITY_FAILED)
    records = _records_by_offer_id(snapshot)
    record = records.get(resolution.selected_offer_id)
    if record is None:
        _append_reason(reasons, REASON_AIRLINE_OFFER_VALIDITY_FAILED)
    else:
        if not (
            record.inventory_available
            and record.airline_policy_valid
            and not record.expired
            and record.ttl_seconds > 0
        ):
            _append_reason(reasons, REASON_AIRLINE_OFFER_VALIDITY_FAILED)
        if resolution.selected_offer_id not in selection_input.client_hard_compatible_candidate_ids:
            _append_reason(reasons, REASON_CLIENT_CONSTRAINT_COMPATIBILITY_FAILED)
        if (
            resolution.authoritative_offer_ref != record.offer_id
            or resolution.resolved_offer_record_ref != record.offer_id
            or resolution.resolved_amount != record.amount
            or resolution.resolved_currency != record.currency
            or resolution.resolved_route_ref != record.route_ref
            or resolution.resolved_baggage != record.baggage_included
            or resolution.resolved_seat_characteristics != record.seat_characteristics
            or resolution.resolved_changeability != record.changeable
            or resolution.resolved_ttl != record.ttl_seconds
        ):
            _append_reason(reasons, REASON_RESOLUTION_FACT_MISMATCH)
    if not resolution.resolved_from_same_candidate_snapshot:
        _append_reason(reasons, REASON_SNAPSHOT_SUBSTITUTION_DETECTED)
    if not resolution.offer_exists or not resolution.offer_unexpired:
        _append_reason(reasons, REASON_AIRLINE_OFFER_VALIDITY_FAILED)
    if not resolution.airline_offer_validity_pass:
        _append_reason(reasons, REASON_AIRLINE_OFFER_VALIDITY_FAILED)
    if not resolution.client_constraint_compatibility_pass:
        _append_reason(reasons, REASON_CLIENT_CONSTRAINT_COMPATIBILITY_FAILED)
    if resolution.semantic_values_used_as_authoritative_facts:
        _append_reason(reasons, REASON_RESOLUTION_FACT_MISMATCH)
    if resolution.real_world_effects_count != 0:
        _append_reason(reasons, REASON_NONZERO_REAL_WORLD_EFFECTS)
    return _report(
        artifact_type="AirlineRootSelectedOfferResolutionV01",
        artifact_id=resolution.resolution_id,
        transaction_id=resolution.transaction_id,
        relevant_root_id=AIRLINE_ROOT_ID,
        reasons=reasons,
        real_world_effects_count=resolution.real_world_effects_count,
    )


def validate_airline_semantic_hold_contract_binding_v01(
    resolution: AirlineRootSelectedOfferResolutionV01,
    hold_packet: corridor_contracts.AirlineHoldCommitPacketV01,
    binding: AirlineSemanticHoldContractBindingV01,
    *,
    resolution_report: AirlineSemanticToContractValidationReportV01 | None = None,
) -> AirlineSemanticToContractValidationReportV01:
    reasons: list[str] = []
    if resolution_report is not None and resolution_report.validation_status not in {
        STATUS_PASS,
        STATUS_ROOT_OVERRIDE,
    }:
        _append_reason(reasons, REASON_AIRLINE_OFFER_VALIDITY_FAILED)
    if binding.transaction_id != resolution.transaction_id or hold_packet.transaction_id != resolution.transaction_id:
        _append_reason(reasons, REASON_WRONG_TRANSACTION_ID)
    if (
        hold_packet.created_by != AIRLINE_ROOT_ID
        or hold_packet.root_owner != AIRLINE_ROOT_ID
        or hold_packet.airline_root_id != AIRLINE_ROOT_ID
    ):
        _append_reason(reasons, REASON_WRONG_ROOT_OWNER)
    if binding.source_offer_resolution_ref != resolution.resolution_id:
        _append_reason(reasons, REASON_HOLD_CONTRACT_BINDING_MISMATCH)
    if (
        binding.source_candidate_set_snapshot_id
        != resolution.source_candidate_set_snapshot_id
        or binding.source_candidate_set_digest
        != resolution.source_candidate_set_digest
    ):
        _append_reason(reasons, REASON_SNAPSHOT_SUBSTITUTION_DETECTED)
    if binding.hold_packet_id != hold_packet.packet_id:
        _append_reason(reasons, REASON_HOLD_CONTRACT_BINDING_MISMATCH)
    if (
        binding.selected_offer_id != resolution.selected_offer_id
        or hold_packet.offer_id != resolution.selected_offer_id
        or hold_packet.amount != resolution.resolved_amount
        or hold_packet.currency != resolution.resolved_currency
        or hold_packet.route_ref != resolution.resolved_route_ref
        or hold_packet.ttl_seconds > resolution.resolved_ttl
    ):
        _append_reason(reasons, REASON_HOLD_CONTRACT_BINDING_MISMATCH)
    if hold_packet.expired:
        _append_reason(reasons, REASON_HOLD_CONTRACT_BINDING_MISMATCH)
    if not hold_packet.idempotency_key:
        _append_reason(reasons, corridor_contracts.REASON_MISSING_IDEMPOTENCY_KEY)
    if hold_packet.allowed_action != corridor_contracts.ACTION_MOCK_OFFER_HOLD:
        _append_reason(reasons, corridor_contracts.REASON_FORBIDDEN_ACTION_REQUESTED)
    if corridor_contracts.ADAPTER_AIRLINE_HOLD_SANDBOX not in hold_packet.allowed_adapters:
        _append_reason(reasons, corridor_contracts.REASON_ADAPTER_NOT_ALLOWED)
    required_forbidden = {
        corridor_contracts.ACTION_REAL_PAYMENT,
        corridor_contracts.ACTION_REAL_TICKET_ISSUE,
        corridor_contracts.ACTION_REAL_BOOKING,
        corridor_contracts.ACTION_REAL_AIRLINE_API,
        corridor_contracts.ACTION_REAL_BANK_API,
        corridor_contracts.ACTION_REAL_GDS_API,
        corridor_contracts.ACTION_POST_ROOT_LLM_REASONING,
    }
    if not required_forbidden.issubset(set(hold_packet.forbidden_actions)):
        _append_reason(reasons, corridor_contracts.REASON_FORBIDDEN_ACTION_REQUESTED)
    if not binding.values_match:
        _append_reason(reasons, REASON_HOLD_CONTRACT_BINDING_MISMATCH)
    if binding.provider_created_target:
        _append_reason(reasons, REASON_PROVIDER_CREATED_TARGET_FORBIDDEN)
    if binding.authority_transferred:
        _append_reason(reasons, REASON_AUTHORITY_TRANSFER_FORBIDDEN)
    if binding.real_world_effects_count != 0:
        _append_reason(reasons, REASON_NONZERO_REAL_WORLD_EFFECTS)
    if hold_packet.real_world_effects_allowed:
        _append_reason(reasons, REASON_NONZERO_REAL_WORLD_EFFECTS)
    return _report(
        artifact_type="AirlineSemanticHoldContractBindingV01",
        artifact_id=binding.binding_id,
        transaction_id=binding.transaction_id,
        relevant_root_id=AIRLINE_ROOT_ID,
        reasons=reasons,
        authority_created=binding.authority_transferred,
        contract_artifact_created=False,
        real_world_effects_count=binding.real_world_effects_count,
    )


def validate_airline_semantic_to_contract_binding_report_v01(
    report: AirlineSemanticToContractBindingReportV01,
) -> AirlineSemanticToContractValidationReportV01:
    reasons = list(report.validation_errors)
    if report.transaction_id != TRANSACTION_ID:
        _append_reason(reasons, REASON_WRONG_TRANSACTION_ID)
    if report.required_binding_ids != REQUIRED_LOCAL_BINDING_IDS:
        _append_reason(reasons, REASON_HOLD_CONTRACT_BINDING_MISMATCH)
    if len(report.causal_binding_rows) != len(REQUIRED_LOCAL_BINDING_IDS):
        _append_reason(reasons, REASON_HOLD_CONTRACT_BINDING_MISMATCH)
    row_ids = tuple(row.binding_id for row in report.causal_binding_rows)
    if len(row_ids) != len(set(row_ids)):
        _append_reason(reasons, REASON_HOLD_CONTRACT_BINDING_MISMATCH)
    if set(row_ids) != set(REQUIRED_LOCAL_BINDING_IDS):
        _append_reason(reasons, REASON_HOLD_CONTRACT_BINDING_MISMATCH)
    rows_by_id = {row.binding_id: row for row in report.causal_binding_rows}
    for binding_id in REQUIRED_LOCAL_BINDING_IDS:
        row = rows_by_id.get(binding_id)
        if row is None:
            _append_reason(reasons, REASON_HOLD_CONTRACT_BINDING_MISMATCH)
            continue
        expected_surface = EXPECTED_BINDING_ROW_SURFACES[binding_id]
        actual_surface = (
            row.source_artifact_type,
            row.source_field,
            row.target_artifact_type,
            row.target_field,
        )
        if actual_surface != expected_surface:
            _append_reason(reasons, REASON_HOLD_CONTRACT_BINDING_MISMATCH)
        if row.transaction_id != report.transaction_id:
            _append_reason(reasons, REASON_WRONG_TRANSACTION_ID)
        recomputed_values_match = row.source_value == row.target_value
        if row.values_match != recomputed_values_match or not recomputed_values_match:
            _append_reason(reasons, REASON_HOLD_CONTRACT_BINDING_MISMATCH)
        recomputed_snapshot_match = row.source_snapshot_id == row.target_snapshot_id
        if row.snapshot_match != recomputed_snapshot_match or not recomputed_snapshot_match:
            _append_reason(reasons, REASON_SNAPSHOT_SUBSTITUTION_DETECTED)
        if not row.causal_input_present:
            _append_reason(reasons, REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH)
        if report.semantic_causality_claimed and not row.semantic_influence_present:
            _append_reason(reasons, REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH)
        if row.authority_transferred:
            _append_reason(reasons, REASON_AUTHORITY_TRANSFER_FORBIDDEN)
        if row.provider_created_target:
            _append_reason(reasons, REASON_PROVIDER_CREATED_TARGET_FORBIDDEN)
    synthesis_row = rows_by_id.get("synthesis_to_canonical_selection")
    canonical_row = rows_by_id.get("canonical_selection_to_client_root_decision")
    decision_row = rows_by_id.get("client_root_decision_to_airline_root_resolution")
    hold_row = rows_by_id.get("airline_root_resolution_to_hold_packet")
    if synthesis_row and report.source_semantic_artifact_ref != synthesis_row.source_artifact_id:
        _append_reason(reasons, REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH)
    if synthesis_row and report.canonical_selection_ref != synthesis_row.target_artifact_id:
        _append_reason(reasons, REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH)
    if canonical_row and report.client_root_decision_ref != canonical_row.target_artifact_id:
        _append_reason(reasons, REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH)
    if decision_row:
        if report.airline_root_resolution_ref != decision_row.target_artifact_id:
            _append_reason(reasons, REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH)
        if report.selected_offer_id != decision_row.source_value:
            _append_reason(reasons, REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH)
    if hold_row and report.hold_packet_ref != hold_row.target_artifact_id:
        _append_reason(reasons, REASON_HOLD_CONTRACT_BINDING_MISMATCH)
    if report.human_approval_ref != STATUS_NOT_YET_BOUND_IN_SLICE_B:
        _append_reason(reasons, REASON_INTEGRATED_CORRIDOR_PASS_FORBIDDEN_IN_SLICE_B)
    if report.purchase_intent_ref != STATUS_NOT_YET_BOUND_IN_SLICE_B:
        _append_reason(reasons, REASON_INTEGRATED_CORRIDOR_PASS_FORBIDDEN_IN_SLICE_B)
    if report.silent_fallback_used:
        _append_reason(reasons, REASON_SILENT_FALLBACK_FORBIDDEN)
    if report.hardcoded_default_offer_used:
        _append_reason(reasons, REASON_HARDCODED_DEFAULT_OFFER_FORBIDDEN)
    if report.provider_created_contract_artifact_count:
        _append_reason(reasons, REASON_PROVIDER_CREATED_TARGET_FORBIDDEN)
    if report.authority_transferred_count:
        _append_reason(reasons, REASON_AUTHORITY_TRANSFER_FORBIDDEN)
    if report.real_world_effects_count != 0:
        _append_reason(reasons, REASON_NONZERO_REAL_WORLD_EFFECTS)
    if report.root_override_used and report.semantic_causality_claimed:
        _append_reason(reasons, REASON_ROOT_OVERRIDE_CANNOT_CLAIM_SEMANTIC_CAUSALITY)
    if report.binding_status == STATUS_ROOT_OVERRIDE and not report.root_override_used:
        _append_reason(reasons, REASON_ROOT_OVERRIDE_CANNOT_CLAIM_SEMANTIC_CAUSALITY)
    if report.binding_status == STATUS_LOCAL_MODEL_PASS and report.root_override_used:
        _append_reason(reasons, REASON_ROOT_OVERRIDE_CANNOT_CLAIM_SEMANTIC_CAUSALITY)
    if report.binding_status == STATUS_CAUSAL_PASS or report.integrated_corridor_causal_pass_claimed:
        _append_reason(reasons, REASON_INTEGRATED_CORRIDOR_PASS_FORBIDDEN_IN_SLICE_B)
    if report.binding_status not in {
        STATUS_LOCAL_MODEL_PASS,
        STATUS_ROOT_OVERRIDE,
        STATUS_FAIL_CLOSED,
    }:
        _append_reason(reasons, REASON_INTEGRATED_CORRIDOR_PASS_FORBIDDEN_IN_SLICE_B)
    return _report(
        artifact_type="AirlineSemanticToContractBindingReportV01",
        artifact_id=report.source_semantic_artifact_ref,
        transaction_id=report.transaction_id,
        relevant_root_id=CLIENT_ROOT_ID,
        reasons=reasons,
        validation_status=(
            STATUS_ROOT_OVERRIDE
            if not reasons and report.binding_status == STATUS_ROOT_OVERRIDE
            else None
        ),
        authority_created=bool(report.authority_transferred_count),
        contract_artifact_created=False,
        real_world_effects_count=report.real_world_effects_count,
    )


def _offer_record(
    *,
    offer_id: str,
    amount: int,
    baggage_included: bool,
    seat_characteristics: tuple[str, ...],
    overnight_layover: bool,
    change_penalty_class: str,
) -> AirlineAuthoritativeOfferRecordV01:
    return AirlineAuthoritativeOfferRecordV01(
        offer_id=offer_id,
        transaction_id=TRANSACTION_ID,
        airline_root_id=AIRLINE_ROOT_ID,
        amount=amount,
        currency=corridor_contracts.CURRENCY,
        route_ref=corridor_contracts.ROUTE_REF,
        departure_date=corridor_contracts.DEPARTURE_DATE,
        return_date=corridor_contracts.RETURN_DATE,
        baggage_included=baggage_included,
        seat_characteristics=seat_characteristics,
        changeable=True,
        overnight_layover=overnight_layover,
        change_penalty_class=change_penalty_class,
        inventory_available=True,
        airline_policy_valid=True,
        ttl_seconds=900,
        expired=False,
        raw_secret_included=False,
        provider_created=False,
        real_world_effects_count=0,
    )


def build_client_constraints_preference_a_v01() -> ClientRootTravelConstraintSetV01:
    return ClientRootTravelConstraintSetV01(
        constraint_set_id="client_constraints:client_001:preference_a",
        transaction_id=TRANSACTION_ID,
        client_root_id=CLIENT_ROOT_ID,
        travel_intent_ref="travel_intent:client_001:PAR-LIM:001",
        origin="PAR",
        destination="LIM",
        departure_date=corridor_contracts.DEPARTURE_DATE,
        return_date=corridor_contracts.RETURN_DATE,
        max_amount=840,
        currency=corridor_contracts.CURRENCY,
        baggage_required=True,
        avoid_overnight_layover=True,
        preferred_seat_characteristics=("window",),
        changeable_preferred=True,
        soft_preference_priority=("lower_price", "window_seat"),
        raw_passport_included=False,
        raw_payment_data_included=False,
        authority_transferred=False,
        real_world_effects_count=0,
    )


def build_client_constraints_preference_b_v01() -> ClientRootTravelConstraintSetV01:
    base = build_client_constraints_preference_a_v01()
    return replace(
        base,
        constraint_set_id="client_constraints:client_001:preference_b",
        preferred_seat_characteristics=("extra_legroom", "aisle"),
        soft_preference_priority=("extra_legroom_aisle", "price_delta_under_30_eur"),
    )


def build_airline_candidate_snapshot_v01() -> AirlineRootOfferCandidateSetSnapshotV01:
    draft = AirlineRootOfferCandidateSetSnapshotV01(
        candidate_set_ref=CANDIDATE_SET_REF,
        candidate_set_snapshot_id=CANDIDATE_SET_SNAPSHOT_ID,
        candidate_set_version=CANDIDATE_SET_VERSION,
        candidate_set_digest="",
        transaction_id=TRANSACTION_ID,
        airline_root_id=AIRLINE_ROOT_ID,
        authoritative_offer_records=(
            _offer_record(
                offer_id=OFFER_A_ID,
                amount=782,
                baggage_included=True,
                seat_characteristics=("window", "standard"),
                overnight_layover=False,
                change_penalty_class="low",
            ),
            _offer_record(
                offer_id=OFFER_B_ID,
                amount=806,
                baggage_included=True,
                seat_characteristics=("extra_legroom", "aisle"),
                overnight_layover=False,
                change_penalty_class="low",
            ),
            _offer_record(
                offer_id=OFFER_C_ID,
                amount=741,
                baggage_included=False,
                seat_characteristics=("middle", "standard"),
                overnight_layover=True,
                change_penalty_class="high",
            ),
        ),
        snapshot_created_at="2026-07-11T09:00:00Z",
        snapshot_ttl_seconds=900,
        snapshot_expired=False,
        raw_secret_included=False,
        provider_created=False,
        real_world_effects_count=0,
    )
    return replace(
        draft,
        candidate_set_digest=compute_airline_candidate_set_digest_v01(draft),
    )


def build_valid_airline_bsep_projection_ref_v01() -> AirlineBSEPProjectionRefV01:
    return AirlineBSEPProjectionRefV01(
        projection_ref=BSEP_PROJECTION_REF,
        transaction_id=TRANSACTION_ID,
        projection_side="airline_offer_selection",
        validation_status=STATUS_PASS,
        raw_secret_included=False,
        authority_created=False,
        real_world_effects_count=0,
    )


def build_selection_input_v01(
    bsep_projection: AirlineBSEPProjectionRefV01,
    constraints: ClientRootTravelConstraintSetV01,
    snapshot: AirlineRootOfferCandidateSetSnapshotV01,
) -> AirlineSemanticSelectionInputV01:
    visible_ids = tuple(
        record.offer_id
        for record in sorted(snapshot.authoritative_offer_records, key=lambda item: item.offer_id)
    )
    client_compatible = _client_hard_compatible_candidate_ids(
        constraints,
        snapshot,
    )
    return AirlineSemanticSelectionInputV01(
        selection_input_id="selection_input:airline:PAR-LIM:001",
        transaction_id=TRANSACTION_ID,
        source_bsep_projection_ref=bsep_projection.projection_ref,
        source_client_constraint_set_id=constraints.constraint_set_id,
        source_candidate_set_ref=snapshot.candidate_set_ref,
        source_candidate_set_snapshot_id=snapshot.candidate_set_snapshot_id,
        source_candidate_set_digest=snapshot.candidate_set_digest,
        visible_candidate_ids=visible_ids,
        airline_valid_candidate_ids=_airline_valid_candidate_ids(snapshot),
        client_hard_compatible_candidate_ids=client_compatible,
        soft_tradeoff_candidate_ids=client_compatible,
        raw_secret_included=False,
        provider_authority_created=False,
        real_world_effects_count=0,
    )


def build_valid_proposal_v01(
    *,
    selection_input: AirlineSemanticSelectionInputV01,
    recommended_offer_id: str,
    ranked_offer_ids: tuple[str, ...],
) -> AirlineSemanticOfferSelectionProposalV01:
    payload: dict[str, Any] = {
        "proposal_id": f"semantic_offer_selection_proposal:{recommended_offer_id}",
        "transaction_id": selection_input.transaction_id,
        "actor_id": ACTOR_CLIENT_PURCHASE_INTENT_REVIEWER,
        "source_selection_input_id": selection_input.selection_input_id,
        "source_bsep_projection_ref": selection_input.source_bsep_projection_ref,
        "source_client_constraint_set_id": (
            selection_input.source_client_constraint_set_id
        ),
        "source_candidate_set_snapshot_id": (
            selection_input.source_candidate_set_snapshot_id
        ),
        "source_candidate_set_digest": selection_input.source_candidate_set_digest,
        "candidate_set_ref": selection_input.source_candidate_set_ref,
        "recommended_offer_id": recommended_offer_id,
        "ranked_offer_ids": ranked_offer_ids,
        "decision_factors": ("bounded_candidate_semantics",),
        "preference_matches": ("explicit_recommendation_supplied",),
        "uncertainty_notes": ("requires_client_root_review",),
        "requires_root_review": True,
        "semantic_summary": "Advisory offer recommendation over visible candidates.",
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
    proposal, report = build_airline_semantic_offer_selection_proposal_from_payload_v01(
        selection_input,
        payload,
    )
    if proposal is None:
        raise ValueError(report.reason_codes)
    return proposal


def build_valid_actor_reviews_v01(
    *,
    selection_input: AirlineSemanticSelectionInputV01,
    reviewed_offer_id: str,
) -> tuple[AirlineCanonicalActorSelectionReviewV01, ...]:
    return tuple(
        AirlineCanonicalActorSelectionReviewV01(
            canonical_actor_output_id=(
                f"canonical_actor_output:{actor_id}:{reviewed_offer_id}"
            ),
            transaction_id=selection_input.transaction_id,
            actor_id=actor_id,
            source_selection_input_id=selection_input.selection_input_id,
            source_candidate_set_snapshot_id=(
                selection_input.source_candidate_set_snapshot_id
            ),
            source_candidate_set_digest=selection_input.source_candidate_set_digest,
            reviewed_offer_id=reviewed_offer_id,
            review_role=role,
            review_status=STATUS_PASS,
            semantic_factors=(f"{role}:validated",),
            blocking_conflicts=(),
            supports_proposed_offer=True,
            validation_status=STATUS_PASS,
            raw_output_used=False,
            authority_created=False,
            permission_created=False,
            real_world_effects_count=0,
        )
        for actor_id, role in REQUIRED_ACTOR_ROLES.items()
    )


def build_valid_synthesis_report_v01(
    *,
    selection_input: AirlineSemanticSelectionInputV01,
    actor_reviews: tuple[AirlineCanonicalActorSelectionReviewV01, ...],
    synthesized_recommended_offer_id: str,
) -> AirlineSemanticSelectionSynthesisReportV01:
    return AirlineSemanticSelectionSynthesisReportV01(
        synthesis_report_id=(
            f"semantic_selection_synthesis:{synthesized_recommended_offer_id}"
        ),
        transaction_id=selection_input.transaction_id,
        source_selection_input_id=selection_input.selection_input_id,
        source_candidate_set_snapshot_id=selection_input.source_candidate_set_snapshot_id,
        source_candidate_set_digest=selection_input.source_candidate_set_digest,
        canonical_actor_output_refs=tuple(
            review.canonical_actor_output_id for review in actor_reviews
        ),
        proposer_actor_id=ACTOR_CLIENT_PURCHASE_INTENT_REVIEWER,
        compatibility_reviewer_actor_ids=(
            ACTOR_AIRLINE_OFFER_POLICY_REVIEWER,
            ACTOR_AIRLINE_FARE_RULES_VERTICAL_CELL,
            ACTOR_AIRLINE_SEAT_BAGGAGE_VERTICAL_CELL,
        ),
        consistency_reviewer_actor_id=(
            ACTOR_TRI_PARTY_EVIDENCE_CONSISTENCY_REVIEWER
        ),
        actor_recommended_offer_ids=tuple(
            (review.actor_id, review.reviewed_offer_id)
            for review in actor_reviews
        ),
        actor_conflicts=(),
        synthesis_status=STATUS_PASS,
        synthesized_recommended_offer_id=synthesized_recommended_offer_id,
        accepted_semantic_factors=("all_canonical_actor_outputs_support_offer",),
        rejected_semantic_factors=("raw_sibling_outputs",),
        unresolved_conflict_present=False,
        requires_client_root_review=True,
        what_runtime_used=("canonical_actor_outputs", "explicit_recommended_offer_id"),
        what_runtime_rejected=("raw_actor_outputs", "provider_authority"),
        authority_created=False,
        permission_created=False,
        provider_created_contract_artifact_count=0,
    )


def build_valid_canonical_selection_evidence_v01(
    *,
    selection_input: AirlineSemanticSelectionInputV01,
    proposal: AirlineSemanticOfferSelectionProposalV01,
    synthesis: AirlineSemanticSelectionSynthesisReportV01,
) -> ValidatedAirlineSemanticSelectionEvidenceV01:
    return ValidatedAirlineSemanticSelectionEvidenceV01(
        canonical_selection_id=f"canonical_selection:{proposal.recommended_offer_id}",
        transaction_id=selection_input.transaction_id,
        source_actor_id=proposal.actor_id,
        source_proposal_id=proposal.proposal_id,
        source_candidate_set_ref=proposal.candidate_set_ref,
        source_selection_input_id=selection_input.selection_input_id,
        source_candidate_set_snapshot_id=selection_input.source_candidate_set_snapshot_id,
        source_candidate_set_digest=selection_input.source_candidate_set_digest,
        source_synthesis_report_id=synthesis.synthesis_report_id,
        recommended_offer_id=proposal.recommended_offer_id,
        accepted_semantic_factors=synthesis.accepted_semantic_factors,
        rejected_semantic_factors=synthesis.rejected_semantic_factors,
        validation_status=STATUS_PASS,
        validation_errors=(),
        what_runtime_used=(
            "accepted_validated_recommendation_id",
            "accepted_validated_soft_preference_interpretation",
            "accepted_snapshot_lineage",
        ),
        what_runtime_rejected=(
            "provider_output_as_truth_rejected",
            "provider_output_as_authority_rejected",
            "provider_supplied_authoritative_facts_rejected",
            "provider_created_contract_artifacts_rejected",
        ),
        advisory_only=True,
        evidence_only=True,
        authority_created=False,
        permission_created=False,
        real_world_effects_count=0,
    )


def build_valid_client_root_decision_v01(
    *,
    selection_input: AirlineSemanticSelectionInputV01,
    evidence: ValidatedAirlineSemanticSelectionEvidenceV01,
    selected_offer_id: str,
    recommendation_accepted: bool,
    root_override_used: bool,
) -> ClientRootOfferSelectionDecisionV01:
    status = STATUS_ROOT_OVERRIDE if root_override_used else STATUS_CAUSAL_PASS
    return ClientRootOfferSelectionDecisionV01(
        decision_id=f"client_root_offer_selection_decision:{selected_offer_id}",
        transaction_id=selection_input.transaction_id,
        client_root_id=CLIENT_ROOT_ID,
        source_canonical_selection_id=evidence.canonical_selection_id,
        source_candidate_set_snapshot_id=selection_input.source_candidate_set_snapshot_id,
        source_candidate_set_digest=selection_input.source_candidate_set_digest,
        recommended_offer_id=evidence.recommended_offer_id,
        selected_offer_id=selected_offer_id,
        decision_status=status,
        recommendation_accepted=recommendation_accepted,
        root_override_used=root_override_used,
        root_override_reason=(
            "client_root_selected_alternate_compatible_offer"
            if root_override_used
            else ""
        ),
        semantic_influence_claimed=not root_override_used,
        acceptance_reasons=("selected_offer_passes_client_hard_constraints",),
        rejection_reasons=(),
        created_by=CLIENT_ROOT_ID,
        creates_purchase_permission=False,
        creates_payment_permission=False,
        creates_ticket_permission=False,
        requires_human_approval_before_purchase_intent=True,
        authority_transferred=False,
        real_world_effects_count=0,
    )


def build_valid_airline_root_resolution_v01(
    *,
    selection_input: AirlineSemanticSelectionInputV01,
    snapshot: AirlineRootOfferCandidateSetSnapshotV01,
    decision: ClientRootOfferSelectionDecisionV01,
) -> AirlineRootSelectedOfferResolutionV01:
    record = _records_by_offer_id(snapshot)[decision.selected_offer_id]
    return AirlineRootSelectedOfferResolutionV01(
        resolution_id=f"airline_root_selected_offer_resolution:{record.offer_id}",
        transaction_id=TRANSACTION_ID,
        created_by=AIRLINE_ROOT_ID,
        airline_root_id=AIRLINE_ROOT_ID,
        source_client_root_decision_ref=decision.decision_id,
        source_candidate_set_snapshot_id=snapshot.candidate_set_snapshot_id,
        source_candidate_set_digest=snapshot.candidate_set_digest,
        selected_offer_id=record.offer_id,
        authoritative_offer_ref=record.offer_id,
        resolved_offer_record_ref=record.offer_id,
        resolved_from_same_candidate_snapshot=True,
        resolved_amount=record.amount,
        resolved_currency=record.currency,
        resolved_route_ref=record.route_ref,
        resolved_baggage=record.baggage_included,
        resolved_seat_characteristics=record.seat_characteristics,
        resolved_changeability=record.changeable,
        resolved_ttl=record.ttl_seconds,
        offer_exists=True,
        offer_unexpired=not record.expired,
        airline_offer_validity_pass=(
            record.inventory_available
            and record.airline_policy_valid
            and not record.expired
        ),
        client_constraint_compatibility_pass=(
            record.offer_id in selection_input.client_hard_compatible_candidate_ids
        ),
        semantic_values_used_as_authoritative_facts=False,
        real_world_effects_count=0,
    )


def build_hold_packet_for_offer_v01(
    snapshot: AirlineRootOfferCandidateSetSnapshotV01,
    selected_offer_id: str,
) -> corridor_contracts.AirlineHoldCommitPacketV01:
    record = _records_by_offer_id(snapshot)[selected_offer_id]
    suffix = selected_offer_id.rsplit(":", 1)[-1]
    base = corridor_contracts.build_valid_airline_hold_commit_packet_v01()
    return replace(
        base,
        packet_id=f"airline_hold_commit_packet:mock_airline_al:{suffix}",
        parent_offer_packet_id=f"airline_offer_packet:mock_airline_al:{suffix}",
        offer_id=record.offer_id,
        hold_id=f"hold:mock_airline_al:{suffix}",
        route_ref=record.route_ref,
        amount=record.amount,
        currency=record.currency,
        ttl_seconds=record.ttl_seconds,
        expired=record.expired,
        idempotency_key=f"idem:airline_hold:{suffix}",
    )


def build_valid_hold_contract_binding_v01(
    *,
    resolution: AirlineRootSelectedOfferResolutionV01,
    hold_packet: corridor_contracts.AirlineHoldCommitPacketV01,
) -> AirlineSemanticHoldContractBindingV01:
    return AirlineSemanticHoldContractBindingV01(
        binding_id=f"semantic_hold_contract_binding:{resolution.selected_offer_id}",
        transaction_id=resolution.transaction_id,
        source_offer_resolution_ref=resolution.resolution_id,
        source_candidate_set_snapshot_id=resolution.source_candidate_set_snapshot_id,
        source_candidate_set_digest=resolution.source_candidate_set_digest,
        hold_packet_id=hold_packet.packet_id,
        selected_offer_id=resolution.selected_offer_id,
        values_match=True,
        authority_transferred=False,
        provider_created_target=False,
        real_world_effects_count=0,
    )


def build_valid_binding_rows_v01(
    *,
    bsep_projection: AirlineBSEPProjectionRefV01,
    constraints: ClientRootTravelConstraintSetV01,
    snapshot: AirlineRootOfferCandidateSetSnapshotV01,
    selection_input: AirlineSemanticSelectionInputV01,
    proposal: AirlineSemanticOfferSelectionProposalV01,
    actor_reviews: tuple[AirlineCanonicalActorSelectionReviewV01, ...],
    synthesis: AirlineSemanticSelectionSynthesisReportV01,
    evidence: ValidatedAirlineSemanticSelectionEvidenceV01,
    decision: ClientRootOfferSelectionDecisionV01,
    resolution: AirlineRootSelectedOfferResolutionV01,
    hold_packet: corridor_contracts.AirlineHoldCommitPacketV01,
    hold_binding: AirlineSemanticHoldContractBindingV01,
) -> tuple[AirlineSemanticToContractBindingRowV01, ...]:
    semantic_chain_present = (
        proposal.recommended_offer_id
        == synthesis.synthesized_recommended_offer_id
        == evidence.recommended_offer_id
        == decision.recommended_offer_id
        and proposal.proposal_id == evidence.source_proposal_id
        and proposal.actor_id == evidence.source_actor_id
        and proposal.candidate_set_ref == evidence.source_candidate_set_ref
        and proposal.source_candidate_set_snapshot_id
        == evidence.source_candidate_set_snapshot_id
        and proposal.source_candidate_set_digest == evidence.source_candidate_set_digest
        and evidence.accepted_semantic_factors == synthesis.accepted_semantic_factors
        and evidence.rejected_semantic_factors == synthesis.rejected_semantic_factors
        and not decision.root_override_used
        and decision.semantic_influence_claimed
    )

    def unique_or_join(values: tuple[str, ...]) -> str:
        unique_values = tuple(dict.fromkeys(values))
        return unique_values[0] if len(unique_values) == 1 else ",".join(values)

    def proposal_lineage(
        snapshot_id: str,
        digest: str,
        transaction_id: str,
        actor_id: str,
    ) -> str:
        return "|".join((snapshot_id, digest, transaction_id, actor_id))

    def row(
        binding_id: str,
        source_type: str,
        source_id: str,
        source_field: str,
        source_value: str,
        target_type: str,
        target_id: str,
        target_field: str,
        target_value: str,
        source_snapshot_id: str,
        target_snapshot_id: str,
        semantic_influence: bool,
    ) -> AirlineSemanticToContractBindingRowV01:
        return AirlineSemanticToContractBindingRowV01(
            binding_id=binding_id,
            transaction_id=TRANSACTION_ID,
            source_artifact_type=source_type,
            source_artifact_id=source_id,
            source_field=source_field,
            source_value=source_value,
            target_artifact_type=target_type,
            target_artifact_id=target_id,
            target_field=target_field,
            target_value=target_value,
            values_match=source_value == target_value,
            source_snapshot_id=source_snapshot_id,
            target_snapshot_id=target_snapshot_id,
            snapshot_match=source_snapshot_id == target_snapshot_id,
            causal_input_present=all(
                (source_id, target_id, source_value, target_value),
            ),
            semantic_influence_present=semantic_influence,
            authority_transferred=False,
            provider_created_target=False,
        )

    return (
        row(
            "bsep_projection_to_selection_input",
            "AirlineBSEPProjectionRefV01",
            bsep_projection.projection_ref,
            "projection_ref",
            bsep_projection.projection_ref,
            "AirlineSemanticSelectionInputV01",
            selection_input.selection_input_id,
            "source_bsep_projection_ref",
            selection_input.source_bsep_projection_ref,
            snapshot.candidate_set_snapshot_id,
            selection_input.source_candidate_set_snapshot_id,
            semantic_chain_present,
        ),
        row(
            "client_constraints_to_selection_input",
            "ClientRootTravelConstraintSetV01",
            constraints.constraint_set_id,
            "constraint_set_id",
            constraints.constraint_set_id,
            "AirlineSemanticSelectionInputV01",
            selection_input.selection_input_id,
            "source_client_constraint_set_id",
            selection_input.source_client_constraint_set_id,
            snapshot.candidate_set_snapshot_id,
            selection_input.source_candidate_set_snapshot_id,
            semantic_chain_present,
        ),
        row(
            "candidate_snapshot_to_selection_input",
            "AirlineRootOfferCandidateSetSnapshotV01",
            snapshot.candidate_set_snapshot_id,
            "candidate_set_digest",
            snapshot.candidate_set_digest,
            "AirlineSemanticSelectionInputV01",
            selection_input.selection_input_id,
            "source_candidate_set_digest",
            selection_input.source_candidate_set_digest,
            snapshot.candidate_set_snapshot_id,
            selection_input.source_candidate_set_snapshot_id,
            semantic_chain_present,
        ),
        row(
            "selection_input_to_actor_prompts",
            "AirlineSemanticSelectionInputV01",
            selection_input.selection_input_id,
            "selection_input_id",
            selection_input.selection_input_id,
            "AirlineCanonicalActorSelectionReviewV01",
            ",".join(review.canonical_actor_output_id for review in actor_reviews),
            "source_selection_input_id",
            unique_or_join(
                tuple(review.source_selection_input_id for review in actor_reviews),
            ),
            selection_input.source_candidate_set_snapshot_id,
            unique_or_join(
                tuple(
                    review.source_candidate_set_snapshot_id
                    for review in actor_reviews
                ),
            ),
            semantic_chain_present,
        ),
        row(
            "validated_actor_outputs_to_synthesis",
            "AirlineCanonicalActorSelectionReviewV01",
            ",".join(review.canonical_actor_output_id for review in actor_reviews),
            "canonical_actor_output_id",
            ",".join(review.canonical_actor_output_id for review in actor_reviews),
            "AirlineSemanticSelectionSynthesisReportV01",
            synthesis.synthesis_report_id,
            "canonical_actor_output_refs",
            ",".join(synthesis.canonical_actor_output_refs),
            unique_or_join(
                tuple(
                    review.source_candidate_set_snapshot_id
                    for review in actor_reviews
                ),
            ),
            synthesis.source_candidate_set_snapshot_id,
            semantic_chain_present,
        ),
        row(
            "synthesis_to_canonical_selection",
            "AirlineSemanticSelectionSynthesisReportV01",
            synthesis.synthesis_report_id,
            "synthesized_recommended_offer_id",
            synthesis.synthesized_recommended_offer_id,
            "ValidatedAirlineSemanticSelectionEvidenceV01",
            evidence.canonical_selection_id,
            "recommended_offer_id",
            evidence.recommended_offer_id,
            synthesis.source_candidate_set_snapshot_id,
            evidence.source_candidate_set_snapshot_id,
            semantic_chain_present,
        ),
        row(
            "semantic_proposal_to_canonical_selection",
            "AirlineSemanticOfferSelectionProposalV01",
            proposal.proposal_id,
            "proposal_id",
            proposal.proposal_id,
            "ValidatedAirlineSemanticSelectionEvidenceV01",
            evidence.canonical_selection_id,
            "source_proposal_id",
            evidence.source_proposal_id,
            proposal_lineage(
                proposal.source_candidate_set_snapshot_id,
                proposal.source_candidate_set_digest,
                proposal.transaction_id,
                proposal.actor_id,
            ),
            proposal_lineage(
                evidence.source_candidate_set_snapshot_id,
                evidence.source_candidate_set_digest,
                evidence.transaction_id,
                evidence.source_actor_id,
            ),
            semantic_chain_present,
        ),
        row(
            "canonical_selection_to_client_root_decision",
            "ValidatedAirlineSemanticSelectionEvidenceV01",
            evidence.canonical_selection_id,
            "recommended_offer_id",
            evidence.recommended_offer_id,
            "ClientRootOfferSelectionDecisionV01",
            decision.decision_id,
            "recommended_offer_id",
            decision.recommended_offer_id,
            evidence.source_candidate_set_snapshot_id,
            decision.source_candidate_set_snapshot_id,
            semantic_chain_present,
        ),
        row(
            "client_root_decision_to_airline_root_resolution",
            "ClientRootOfferSelectionDecisionV01",
            decision.decision_id,
            "selected_offer_id",
            decision.selected_offer_id,
            "AirlineRootSelectedOfferResolutionV01",
            resolution.resolution_id,
            "selected_offer_id",
            resolution.selected_offer_id,
            decision.source_candidate_set_snapshot_id,
            resolution.source_candidate_set_snapshot_id,
            semantic_chain_present,
        ),
        row(
            "airline_root_resolution_to_hold_packet",
            "AirlineRootSelectedOfferResolutionV01",
            resolution.resolution_id,
            "selected_offer_id",
            resolution.selected_offer_id,
            "AirlineHoldCommitPacketV01",
            hold_packet.packet_id,
            "offer_id",
            hold_packet.offer_id,
            resolution.source_candidate_set_snapshot_id,
            hold_binding.source_candidate_set_snapshot_id,
            semantic_chain_present,
        ),
    )


def build_valid_semantic_to_contract_binding_report_v01(
    *,
    bsep_projection: AirlineBSEPProjectionRefV01,
    constraints: ClientRootTravelConstraintSetV01,
    snapshot: AirlineRootOfferCandidateSetSnapshotV01,
    selection_input: AirlineSemanticSelectionInputV01,
    proposal: AirlineSemanticOfferSelectionProposalV01,
    actor_reviews: tuple[AirlineCanonicalActorSelectionReviewV01, ...],
    synthesis: AirlineSemanticSelectionSynthesisReportV01,
    evidence: ValidatedAirlineSemanticSelectionEvidenceV01,
    decision: ClientRootOfferSelectionDecisionV01,
    resolution: AirlineRootSelectedOfferResolutionV01,
    hold_packet: corridor_contracts.AirlineHoldCommitPacketV01,
    hold_binding: AirlineSemanticHoldContractBindingV01,
) -> AirlineSemanticToContractBindingReportV01:
    rows = build_valid_binding_rows_v01(
        bsep_projection=bsep_projection,
        constraints=constraints,
        snapshot=snapshot,
        selection_input=selection_input,
        proposal=proposal,
        actor_reviews=actor_reviews,
        synthesis=synthesis,
        evidence=evidence,
        decision=decision,
        resolution=resolution,
        hold_packet=hold_packet,
        hold_binding=hold_binding,
    )
    return AirlineSemanticToContractBindingReportV01(
        binding_status=(
            STATUS_ROOT_OVERRIDE if decision.root_override_used else STATUS_LOCAL_MODEL_PASS
        ),
        transaction_id=TRANSACTION_ID,
        source_semantic_artifact_ref=synthesis.synthesis_report_id,
        canonical_selection_ref=evidence.canonical_selection_id,
        client_root_decision_ref=decision.decision_id,
        airline_root_resolution_ref=resolution.resolution_id,
        selected_offer_id=decision.selected_offer_id,
        hold_packet_ref=hold_packet.packet_id,
        human_approval_ref=STATUS_NOT_YET_BOUND_IN_SLICE_B,
        purchase_intent_ref=STATUS_NOT_YET_BOUND_IN_SLICE_B,
        causal_binding_rows=rows,
        silent_fallback_used=False,
        hardcoded_default_offer_used=False,
        provider_created_contract_artifact_count=0,
        authority_transferred_count=0,
        real_world_effects_count=0,
        root_override_used=decision.root_override_used,
        semantic_causality_claimed=not decision.root_override_used,
        required_binding_ids=REQUIRED_LOCAL_BINDING_IDS,
        validation_errors=(),
        integrated_corridor_causal_pass_claimed=False,
    )


def validate_airline_semantic_to_contract_local_chain_v01(
    *,
    bsep_projection: AirlineBSEPProjectionRefV01,
    constraints: ClientRootTravelConstraintSetV01,
    snapshot: AirlineRootOfferCandidateSetSnapshotV01,
    selection_input: AirlineSemanticSelectionInputV01,
    proposal: AirlineSemanticOfferSelectionProposalV01,
    actor_reviews: tuple[AirlineCanonicalActorSelectionReviewV01, ...],
    synthesis: AirlineSemanticSelectionSynthesisReportV01,
    evidence: ValidatedAirlineSemanticSelectionEvidenceV01,
    decision: ClientRootOfferSelectionDecisionV01,
    resolution: AirlineRootSelectedOfferResolutionV01,
    hold_packet: corridor_contracts.AirlineHoldCommitPacketV01,
    hold_binding: AirlineSemanticHoldContractBindingV01,
    binding_report: AirlineSemanticToContractBindingReportV01,
) -> AirlineSemanticToContractValidationReportV01:
    reasons: list[str] = []

    validation_reports = (
        validate_airline_bsep_projection_ref_v01(bsep_projection),
        validate_client_root_travel_constraint_set_v01(constraints),
        validate_airline_candidate_snapshot_v01(snapshot),
        validate_airline_semantic_selection_input_v01(
            bsep_projection,
            constraints,
            snapshot,
            selection_input,
        ),
        validate_airline_semantic_offer_selection_proposal_v01(
            selection_input,
            proposal,
        ),
        *(
            validate_airline_canonical_actor_selection_review_v01(
                selection_input,
                actor_review,
            )
            for actor_review in actor_reviews
        ),
        validate_airline_semantic_selection_synthesis_report_v01(
            selection_input,
            actor_reviews,
            synthesis,
        ),
        validate_validated_airline_semantic_selection_evidence_v01(
            selection_input,
            proposal,
            actor_reviews,
            synthesis,
            evidence,
        ),
        validate_client_root_offer_selection_decision_v01(
            selection_input,
            evidence,
            decision,
        ),
    )
    for report in validation_reports:
        reasons.extend(report.reason_codes)

    decision_report = validation_reports[-1]
    resolution_report = validate_airline_root_selected_offer_resolution_v01(
        selection_input,
        snapshot,
        evidence,
        decision,
        resolution,
    )
    reasons.extend(resolution_report.reason_codes)

    hold_report = validate_airline_semantic_hold_contract_binding_v01(
        resolution,
        hold_packet,
        hold_binding,
        resolution_report=resolution_report,
    )
    reasons.extend(hold_report.reason_codes)

    expected_rows = build_valid_binding_rows_v01(
        bsep_projection=bsep_projection,
        constraints=constraints,
        snapshot=snapshot,
        selection_input=selection_input,
        proposal=proposal,
        actor_reviews=actor_reviews,
        synthesis=synthesis,
        evidence=evidence,
        decision=decision,
        resolution=resolution,
        hold_packet=hold_packet,
        hold_binding=hold_binding,
    )
    if binding_report.causal_binding_rows != expected_rows:
        _append_reason(reasons, REASON_HOLD_CONTRACT_BINDING_MISMATCH)

    report_validation = validate_airline_semantic_to_contract_binding_report_v01(
        binding_report,
    )
    reasons.extend(report_validation.reason_codes)

    if binding_report.integrated_corridor_causal_pass_claimed:
        _append_reason(reasons, REASON_INTEGRATED_CORRIDOR_PASS_FORBIDDEN_IN_SLICE_B)
    if decision.decision_status == STATUS_REJECTED:
        _append_reason(reasons, REASON_CLIENT_ROOT_DECISION_REJECTED)

    status = STATUS_FAIL_CLOSED
    if not reasons:
        if (
            decision_report.validation_status == STATUS_ROOT_OVERRIDE
            or binding_report.binding_status == STATUS_ROOT_OVERRIDE
        ):
            status = STATUS_ROOT_OVERRIDE
        else:
            status = STATUS_LOCAL_MODEL_PASS

    return _report(
        artifact_type="AirlineSemanticToContractLocalChainV01",
        artifact_id=f"local_chain:{binding_report.selected_offer_id}",
        transaction_id=binding_report.transaction_id,
        relevant_root_id=CLIENT_ROOT_ID,
        reasons=reasons,
        validation_status=status,
        authority_created=False,
        contract_artifact_created=False,
        real_world_effects_count=binding_report.real_world_effects_count,
    )
