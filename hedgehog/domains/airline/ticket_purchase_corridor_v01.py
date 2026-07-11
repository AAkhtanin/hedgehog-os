"""Airline domain contract projection for the mock ticket/purchase corridor.

This module is an Airline domain contract projection. It is not Hedgehog OS
universal kernel/core. Exact boundary phrase: not Hedgehog OS universal kernel/core.
It reuses universal Root/ActionCommitPacket/corridor invariants and does not
create a second authority engine.

This module is not an installed Needle. A future Airline Needle/Capability Pack
may compose these contracts. No runtime execution is implemented in Slice B.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from hedgehog import action_commit_packet_v02 as action_commit_packet


MODULE_ID = "airline_ticket_purchase_corridor_v01"
SLICE_ID = "airline_ticket_purchase_corridor_v01_slice_b"

TRANSACTION_ID = "tri_airline_purchase:PAR-LIM:2026-08-12:client_001"
CLIENT_ROOT_ID = "root:client_os_001"
AIRLINE_ROOT_ID = "root:mock_airline_al"
BANK_ROOT_ID = "root:mock_bank_a"

PASS = "PASS"
FAIL_CLOSED = "FAIL_CLOSED"
RETURN_TO_RELEVANT_ROOT = "RETURN_TO_RELEVANT_ROOT"

REAL_WORLD_EFFECTS_ALLOWED = False
REAL_AIRLINE_API_ALLOWED = False
REAL_BANK_API_ALLOWED = False
REAL_GDS_API_ALLOWED = False
REAL_PAYMENT_ALLOWED = False
REAL_TICKET_ALLOWED = False
REAL_BOOKING_ALLOWED = False

ACTION_MOCK_OFFER_HOLD = "mock_offer_hold"
ACTION_CLIENT_PURCHASE_INTENT = "client_purchase_intent"
ACTION_MOCK_PAYMENT_AUTHORIZATION = "mock_payment_authorization"
ACTION_MOCK_TICKET_ISSUE = "mock_ticket_issue"
ACTION_MOCK_PURCHASE_COMPLETION = "mock_purchase_completion"

ACTION_REAL_PAYMENT = "real_payment"
ACTION_REAL_TICKET_ISSUE = "real_ticket_issue"
ACTION_REAL_BOOKING = "real_booking"
ACTION_REAL_AIRLINE_API = "real_airline_api"
ACTION_REAL_BANK_API = "real_bank_api"
ACTION_REAL_GDS_API = "real_gds_api"
ACTION_POST_ROOT_LLM_REASONING = "post_root_llm_reasoning"

ADAPTER_AIRLINE_HOLD_SANDBOX = "airline_hold_sandbox_v01"
ADAPTER_BANK_PAYMENT_SANDBOX = "bank_payment_sandbox_v01"
ADAPTER_AIRLINE_TICKET_SANDBOX = "airline_ticket_sandbox_v01"

PHASE_AIRLINE_OFFER_HOLD = "airline_offer_hold"
PHASE_CLIENT_PURCHASE_INTENT = "client_purchase_intent"
PHASE_BANK_PAYMENT_AUTHORIZATION = "bank_payment_authorization"
PHASE_AIRLINE_TICKET_ISSUE = "airline_ticket_issue"
PHASE_CLIENT_COMPLETION = "client_completion"
PHASE_GLOBAL_SIDE_ROOT_REVIEWS_COMPLETED = "side_root_reviews_completed"

OFFER_ID = "offer:mock_airline_al:PAR-LIM:001"
HOLD_ID = "hold:mock_airline_al:001"
PASSENGER_REF = "sealed_passenger_ref:client_001:pax_001"
ROUTE_REF = "route:PAR-LIM:2026-08-12:2026-08-21"
DEPARTURE_DATE = "2026-08-12"
RETURN_DATE = "2026-08-21"
AMOUNT = 782
MAX_AMOUNT = 840
CURRENCY = "EUR"
MERCHANT_REF = "merchant_ref:mock_airline_al"
MOCK_TICKET_ID = "mock_ticket:001"
MOCK_PNR = "PNR-EEH01"


@dataclass(frozen=True)
class AirlineTicketPurchaseContractContextV01:
    transaction_id: str
    offer_id: str
    hold_id: str
    amount: int
    currency: str
    route_ref: str
    passenger_ref: str
    max_amount: int
    merchant_ref: str


def build_canonical_airline_ticket_purchase_contract_context_v01() -> (
    AirlineTicketPurchaseContractContextV01
):
    return AirlineTicketPurchaseContractContextV01(
        transaction_id=TRANSACTION_ID,
        offer_id=OFFER_ID,
        hold_id=HOLD_ID,
        amount=AMOUNT,
        currency=CURRENCY,
        route_ref=ROUTE_REF,
        passenger_ref=PASSENGER_REF,
        max_amount=MAX_AMOUNT,
        merchant_ref=MERCHANT_REF,
    )


def _contract_context(
    contract_context: AirlineTicketPurchaseContractContextV01 | None,
) -> AirlineTicketPurchaseContractContextV01:
    return (
        contract_context
        if contract_context is not None
        else build_canonical_airline_ticket_purchase_contract_context_v01()
    )


def build_airline_ticket_purchase_contract_context_from_resolution_v01(
    *,
    resolution: Any,
    hold_packet: AirlineHoldCommitPacketV01,
) -> AirlineTicketPurchaseContractContextV01:
    return AirlineTicketPurchaseContractContextV01(
        transaction_id=resolution.transaction_id,
        offer_id=resolution.selected_offer_id,
        hold_id=hold_packet.hold_id,
        amount=resolution.resolved_amount,
        currency=resolution.resolved_currency,
        route_ref=resolution.resolved_route_ref,
        passenger_ref=hold_packet.passenger_ref,
        max_amount=MAX_AMOUNT,
        merchant_ref=MERCHANT_REF,
    )


ARTIFACT_AIRLINE_OFFER_PACKET = "AirlineOfferPacketV01"
ARTIFACT_AIRLINE_HOLD_COMMIT_PACKET = "AirlineHoldCommitPacketV01"
ARTIFACT_AIRLINE_OFFER_HOLD_RECEIPT = "AirlineOfferHoldReceiptV01"
ARTIFACT_CLIENT_PURCHASE_INTENT = "ClientPurchaseIntentV01"
ARTIFACT_BANK_PAYMENT_AUTHORIZATION_REF = "BankPaymentAuthorizationRefV01"
ARTIFACT_AIRLINE_TICKET_ISSUE_INTENT = "AirlineTicketIssueIntentV01"
ARTIFACT_MOCK_TICKET_RECEIPT = "MockTicketReceiptV01"
ARTIFACT_MOCK_PURCHASE_RECEIPT = "MockPurchaseReceiptV01"

ACTIONCOMMITPACKET_CONTAINMENT_LAWS_REUSED = (
    action_commit_packet.CONTAINMENT_LAWS_V02
)

REASON_WRONG_TRANSACTION_ID = "wrong_transaction_id"
REASON_MIXED_TRANSACTION_ID = "mixed_transaction_id"
REASON_WRONG_ROOT_OWNER = "wrong_root_owner"
REASON_WRONG_CREATED_BY = "wrong_created_by"
REASON_PROVIDER_CANNOT_CREATE_CONTRACT_ARTIFACT = (
    "provider_cannot_create_contract_artifact"
)
REASON_HUMAN_APPROVAL_IS_EVIDENCE_ONLY = "human_approval_is_evidence_only"
REASON_HUMAN_APPROVAL_CANNOT_CREATE_PURCHASE_INTENT = (
    "human_approval_cannot_create_purchase_intent"
)
REASON_HUMAN_APPROVAL_CANNOT_CREATE_ACTION_COMMIT_PACKET = (
    "human_approval_cannot_create_action_commit_packet"
)
REASON_MISSING_AIRLINE_ROOT_OFFER_HOLD_REVIEW = (
    "missing_airline_root_offer_hold_review"
)
REASON_MISSING_OFFER_PACKET = "missing_offer_packet"
REASON_MISSING_HOLD_PACKET = "missing_hold_packet"
REASON_MISSING_OFFER_HOLD_RECEIPT = "missing_offer_hold_receipt"
REASON_PURCHASE_INTENT_BEFORE_OFFER_HOLD = "purchase_intent_before_offer_hold"
REASON_SELECTED_OFFER_MISMATCH = "selected_offer_mismatch"
REASON_HOLD_ID_MISMATCH = "hold_id_mismatch"
REASON_PASSENGER_REF_MISMATCH = "passenger_ref_mismatch"
REASON_ROUTE_REF_MISMATCH = "route_ref_mismatch"
REASON_AMOUNT_MISMATCH = "amount_mismatch"
REASON_AMOUNT_EXCEEDS_HUMAN_APPROVAL = "amount_exceeds_human_approval"
REASON_CURRENCY_MISMATCH = "currency_mismatch"
REASON_MERCHANT_MISMATCH = "merchant_mismatch"
REASON_EXPIRED_OFFER = "expired_offer"
REASON_EXPIRED_HOLD = "expired_hold"
REASON_EXPIRED_PURCHASE_INTENT = "expired_purchase_intent"
REASON_EXPIRED_PAYMENT_AUTHORIZATION = "expired_payment_authorization"
REASON_DUPLICATE_IDEMPOTENCY_KEY = "duplicate_idempotency_key"
REASON_ADAPTER_NOT_ALLOWED = "adapter_not_allowed"
REASON_FORBIDDEN_ACTION_REQUESTED = "forbidden_action_requested"
REASON_TICKET_ISSUE_WITHOUT_CLIENT_PURCHASE_INTENT = (
    "ticket_issue_without_client_purchase_intent"
)
REASON_TICKET_ISSUE_WITHOUT_BANK_AUTHORIZATION = (
    "ticket_issue_without_bank_authorization"
)
REASON_RECEIPT_NOT_EVIDENCE_ONLY = "receipt_not_evidence_only"
REASON_RECEIPT_CREATED_PERMISSION = "receipt_created_permission"
REASON_RECEIPT_CREATED_FUTURE_PERMISSION = "receipt_created_future_permission"
REASON_RECEIPT_REWROTE_ROOT_TRUTH = "receipt_rewrote_root_truth"
REASON_SHARED_SUMMARY_BECAME_FOURTH_ROOT = "shared_summary_became_fourth_root"
REASON_CROSS_ROOT_AUTHORITY_TRANSFER = "cross_root_authority_transfer"
REASON_POST_ROOT_REASONING_RESTART_FORBIDDEN = (
    "post_root_reasoning_restart_forbidden"
)
REASON_REAL_AIRLINE_API_FORBIDDEN = "real_airline_api_forbidden"
REASON_REAL_BANK_API_FORBIDDEN = "real_bank_api_forbidden"
REASON_REAL_GDS_API_FORBIDDEN = "real_gds_api_forbidden"
REASON_REAL_PAYMENT_FORBIDDEN = "real_payment_forbidden"
REASON_REAL_TICKET_FORBIDDEN = "real_ticket_forbidden"
REASON_REAL_BOOKING_FORBIDDEN = "real_booking_forbidden"
REASON_NONZERO_REAL_WORLD_EFFECTS = "nonzero_real_world_effects"
REASON_CHILD_TTL_EXCEEDS_PARENT_TTL = "child_ttl_exceeds_parent_ttl"
REASON_PARENT_ARTIFACT_BINDING_MISMATCH = "parent_artifact_binding_mismatch"
REASON_MISSING_IDEMPOTENCY_KEY = "missing_idempotency_key"
REASON_GLOBAL_SIDE_ROOT_REVIEWS_COMPLETED_SHORTCUT_REJECTED = (
    "global_side_root_reviews_completed_shortcut_rejected"
)
REASON_MISSING_CLIENT_ROOT_PURCHASE_INTENT_REVIEW = (
    "missing_client_root_purchase_intent_review"
)
REASON_MISSING_BANK_ROOT_PAYMENT_AUTHORIZATION_REVIEW = (
    "missing_bank_root_payment_authorization_review"
)
REASON_MISSING_AIRLINE_ROOT_TICKET_ISSUE_REVIEW = (
    "missing_airline_root_ticket_issue_review"
)
REASON_MISSING_CLIENT_ROOT_COMPLETION_REVIEW = (
    "missing_client_root_completion_review"
)
REASON_PHASE_FAILURE_CANNOT_BE_REPAIRED_BY_LATER_PHASE = (
    "phase_failure_cannot_be_repaired_by_later_phase"
)


@dataclass(frozen=True)
class AirlineRootPhaseGateV01:
    gate_id: str
    transaction_id: str
    root_id: str
    phase_id: str
    review_status: str
    authorized_artifact_types: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    provider_created: bool
    foreign_root_authority_granted: bool
    post_root_reasoning_restarted: bool
    real_world_effects_count: int


@dataclass(frozen=True)
class AirlinePurchaseApprovalEvidenceRefV01:
    approval_ref: str
    transaction_id: str
    client_root_id: str
    selected_offer_id: str
    max_amount: int
    currency: str
    passenger_ref: str
    approval_scope: str
    evidence_only: bool
    creates_client_purchase_intent: bool
    creates_action_commit_packet: bool
    creates_receipt: bool
    creates_payment_authorization: bool
    creates_ticket: bool
    creates_booking: bool
    creates_future_permission: bool
    real_world_effects_count: int


@dataclass(frozen=True)
class AirlineOfferPacketV01:
    packet_id: str
    transaction_id: str
    created_by: str
    root_owner: str
    airline_root_id: str
    offer_id: str
    passenger_ref: str
    route_ref: str
    departure_date: str
    return_date: str
    amount: int
    currency: str
    baggage_included: bool
    seat_ref: str
    ttl_seconds: int
    expired: bool
    evidence_only: bool
    purchase_permission_created: bool
    payment_permission_created: bool
    ticket_permission_created: bool
    real_world_effects_count: int


@dataclass(frozen=True)
class AirlineHoldCommitPacketV01:
    packet_id: str
    transaction_id: str
    parent_offer_packet_id: str
    created_by: str
    root_owner: str
    airline_root_id: str
    offer_id: str
    hold_id: str
    passenger_ref: str
    route_ref: str
    amount: int
    currency: str
    ttl_seconds: int
    expired: bool
    idempotency_key: str
    allowed_action: str
    allowed_adapters: tuple[str, ...]
    forbidden_actions: tuple[str, ...]
    real_world_effects_allowed: bool


@dataclass(frozen=True)
class AirlineOfferHoldReceiptV01:
    receipt_id: str
    transaction_id: str
    source_hold_packet_id: str
    source_idempotency_key: str
    created_by: str
    root_owner: str
    offer_id: str
    hold_id: str
    passenger_ref: str
    route_ref: str
    amount: int
    currency: str
    evidence_only: bool
    purchase_permission_created: bool
    payment_permission_created: bool
    ticket_permission_created: bool
    future_permission_created: bool
    real_world_effects_count: int


@dataclass(frozen=True)
class ClientPurchaseIntentV01:
    intent_id: str
    transaction_id: str
    created_by: str
    root_owner: str
    client_root_id: str
    source_human_approval_ref: str
    selected_offer_packet_id: str
    required_offer_hold_receipt_id: str
    offer_id: str
    hold_id: str
    passenger_ref: str
    route_ref: str
    max_amount: int
    selected_amount: int
    currency: str
    ttl_seconds: int
    expired: bool
    idempotency_key: str
    allowed_action: str
    bank_authority_created: bool
    airline_authority_created: bool
    action_commit_packet_created_by_human: bool
    payment_executed: bool
    ticket_issued: bool
    booking_created: bool
    future_permission_created: bool
    real_world_effects_count: int


@dataclass(frozen=True)
class BankPaymentAuthorizationRefV01:
    authorization_ref_id: str
    transaction_id: str
    created_by: str
    root_owner: str
    bank_root_id: str
    source_payment_receipt_id: str
    source_purchase_intent_id: str
    merchant_ref: str
    offer_id: str
    hold_id: str
    passenger_ref: str
    route_ref: str
    amount: int
    currency: str
    ttl_seconds: int
    expired: bool
    idempotency_key: str
    evidence_only: bool
    settlement_executed: bool
    real_payment_executed: bool
    ticket_permission_created: bool
    future_permission_created: bool
    real_world_effects_count: int


@dataclass(frozen=True)
class AirlineTicketIssueIntentV01:
    intent_id: str
    transaction_id: str
    created_by: str
    root_owner: str
    airline_root_id: str
    required_offer_packet_id: str
    required_hold_packet_id: str
    required_offer_hold_receipt_id: str
    required_client_purchase_intent_id: str
    required_payment_authorization_ref_id: str
    offer_id: str
    hold_id: str
    passenger_ref: str
    route_ref: str
    amount: int
    currency: str
    merchant_ref: str
    ttl_seconds: int
    expired: bool
    idempotency_key: str
    allowed_action: str
    allowed_adapters: tuple[str, ...]
    forbidden_actions: tuple[str, ...]
    real_ticket_allowed: bool
    real_booking_allowed: bool
    real_airline_api_allowed: bool
    real_world_effects_allowed: bool


@dataclass(frozen=True)
class MockTicketReceiptV01:
    receipt_id: str
    transaction_id: str
    source_ticket_issue_intent_id: str
    source_idempotency_key: str
    created_by: str
    root_owner: str
    mock_ticket_id: str
    mock_pnr: str
    offer_id: str
    hold_id: str
    passenger_ref: str
    route_ref: str
    amount: int
    currency: str
    evidence_only: bool
    real_ticket: bool
    real_booking: bool
    payment_created: bool
    future_ticket_permission_created: bool
    future_payment_permission_created: bool
    real_world_effects_count: int


@dataclass(frozen=True)
class MockPurchaseReceiptV01:
    receipt_id: str
    transaction_id: str
    source_client_purchase_intent_id: str
    source_payment_authorization_ref_id: str
    source_mock_ticket_receipt_id: str
    client_root_id: str
    airline_root_id: str
    bank_root_id: str
    created_by: str
    root_owner: str
    evidence_only: bool
    side_root_finals_replaced: bool
    root_truth_rewritten: bool
    future_permission_created: bool
    real_payment_executed: bool
    real_ticket_issued: bool
    real_booking_created: bool
    real_world_effects_count: int


@dataclass(frozen=True)
class AirlineCorridorValidationReportV01:
    validation_id: str
    artifact_type: str
    artifact_id: str
    transaction_id: str
    validation_status: str
    return_to_root_required: bool
    relevant_root_id: str
    reason_codes: tuple[str, ...]
    authority_created: bool
    permission_created: bool
    real_world_effects_count: int


def _append_reason(reasons: list[str], reason: str) -> None:
    if reason not in reasons:
        reasons.append(reason)


def _is_provider_creator(created_by: str) -> bool:
    lowered = created_by.lower()
    return any(token in lowered for token in ("provider", "gemini", "llm", "model"))


def _report(
    *,
    artifact_type: str,
    artifact_id: str,
    transaction_id: str,
    relevant_root_id: str,
    reasons: list[str],
    authority_created: bool = False,
    permission_created: bool = False,
    real_world_effects_count: int = 0,
) -> AirlineCorridorValidationReportV01:
    return AirlineCorridorValidationReportV01(
        validation_id=f"validation:{artifact_type}:{artifact_id}",
        artifact_type=artifact_type,
        artifact_id=artifact_id,
        transaction_id=transaction_id,
        validation_status=PASS if not reasons else FAIL_CLOSED,
        return_to_root_required=bool(reasons),
        relevant_root_id=relevant_root_id,
        reason_codes=tuple(reasons),
        authority_created=authority_created,
        permission_created=permission_created,
        real_world_effects_count=real_world_effects_count,
    )


def _check_transaction(reasons: list[str], *artifacts: Any) -> None:
    values = [
        artifact.transaction_id
        for artifact in artifacts
        if artifact is not None and hasattr(artifact, "transaction_id")
    ]
    if any(value != TRANSACTION_ID for value in values):
        _append_reason(reasons, REASON_WRONG_TRANSACTION_ID)
    if len(set(values)) > 1:
        _append_reason(reasons, REASON_MIXED_TRANSACTION_ID)


def _check_idempotency(reasons: list[str], value: str) -> None:
    if not value:
        _append_reason(reasons, REASON_MISSING_IDEMPOTENCY_KEY)
    if "duplicate" in value:
        _append_reason(reasons, REASON_DUPLICATE_IDEMPOTENCY_KEY)


def _check_created_by_root(
    reasons: list[str],
    *,
    created_by: str,
    expected_root_id: str,
) -> None:
    if _is_provider_creator(created_by):
        _append_reason(reasons, REASON_PROVIDER_CANNOT_CREATE_CONTRACT_ARTIFACT)
    if created_by != expected_root_id:
        _append_reason(reasons, REASON_WRONG_CREATED_BY)


def _check_root_owner(
    reasons: list[str],
    *,
    root_owner: str,
    expected_root_id: str,
) -> None:
    if root_owner != expected_root_id:
        _append_reason(reasons, REASON_WRONG_ROOT_OWNER)


def _check_real_effects(reasons: list[str], artifact: Any) -> None:
    if getattr(artifact, "real_world_effects_count", 0) != 0:
        _append_reason(reasons, REASON_NONZERO_REAL_WORLD_EFFECTS)
    if getattr(artifact, "real_world_effects_allowed", False):
        _append_reason(reasons, REASON_NONZERO_REAL_WORLD_EFFECTS)
    if getattr(artifact, "real_airline_api_allowed", False):
        _append_reason(reasons, REASON_REAL_AIRLINE_API_FORBIDDEN)
    if getattr(artifact, "real_payment_executed", False) or getattr(
        artifact,
        "payment_executed",
        False,
    ):
        _append_reason(reasons, REASON_REAL_PAYMENT_FORBIDDEN)
    if getattr(artifact, "real_ticket", False) or getattr(
        artifact,
        "ticket_issued",
        False,
    ) or getattr(artifact, "real_ticket_allowed", False) or getattr(
        artifact,
        "real_ticket_issued",
        False,
    ):
        _append_reason(reasons, REASON_REAL_TICKET_FORBIDDEN)
    if getattr(artifact, "real_booking", False) or getattr(
        artifact,
        "booking_created",
        False,
    ) or getattr(artifact, "real_booking_allowed", False) or getattr(
        artifact,
        "real_booking_created",
        False,
    ):
        _append_reason(reasons, REASON_REAL_BOOKING_FORBIDDEN)
    if getattr(artifact, "settlement_executed", False):
        _append_reason(reasons, REASON_REAL_PAYMENT_FORBIDDEN)


def _check_receipt_evidence(
    reasons: list[str],
    *,
    evidence_only: bool,
    permission_flags: tuple[bool, ...],
    future_permission_created: bool,
) -> None:
    if not evidence_only:
        _append_reason(reasons, REASON_RECEIPT_NOT_EVIDENCE_ONLY)
    if any(permission_flags):
        _append_reason(reasons, REASON_RECEIPT_CREATED_PERMISSION)
    if future_permission_created:
        _append_reason(reasons, REASON_RECEIPT_CREATED_FUTURE_PERMISSION)


def validate_root_phase_gate_v01(
    gate: AirlineRootPhaseGateV01,
) -> AirlineCorridorValidationReportV01:
    reasons: list[str] = []
    expected_roots = {
        PHASE_AIRLINE_OFFER_HOLD: AIRLINE_ROOT_ID,
        PHASE_CLIENT_PURCHASE_INTENT: CLIENT_ROOT_ID,
        PHASE_BANK_PAYMENT_AUTHORIZATION: BANK_ROOT_ID,
        PHASE_AIRLINE_TICKET_ISSUE: AIRLINE_ROOT_ID,
        PHASE_CLIENT_COMPLETION: CLIENT_ROOT_ID,
    }
    if gate.phase_id == PHASE_GLOBAL_SIDE_ROOT_REVIEWS_COMPLETED:
        _append_reason(
            reasons,
            REASON_GLOBAL_SIDE_ROOT_REVIEWS_COMPLETED_SHORTCUT_REJECTED,
        )
    if gate.transaction_id != TRANSACTION_ID:
        _append_reason(reasons, REASON_WRONG_TRANSACTION_ID)
    if gate.root_id != expected_roots.get(gate.phase_id, gate.root_id):
        _append_reason(reasons, REASON_WRONG_ROOT_OWNER)
    if gate.review_status != PASS:
        if gate.phase_id == PHASE_AIRLINE_OFFER_HOLD:
            _append_reason(reasons, REASON_MISSING_AIRLINE_ROOT_OFFER_HOLD_REVIEW)
        elif gate.phase_id == PHASE_CLIENT_PURCHASE_INTENT:
            _append_reason(
                reasons,
                REASON_MISSING_CLIENT_ROOT_PURCHASE_INTENT_REVIEW,
            )
        elif gate.phase_id == PHASE_BANK_PAYMENT_AUTHORIZATION:
            _append_reason(
                reasons,
                REASON_MISSING_BANK_ROOT_PAYMENT_AUTHORIZATION_REVIEW,
            )
        elif gate.phase_id == PHASE_AIRLINE_TICKET_ISSUE:
            _append_reason(reasons, REASON_MISSING_AIRLINE_ROOT_TICKET_ISSUE_REVIEW)
        elif gate.phase_id == PHASE_CLIENT_COMPLETION:
            _append_reason(reasons, REASON_MISSING_CLIENT_ROOT_COMPLETION_REVIEW)
    if gate.provider_created:
        _append_reason(reasons, REASON_PROVIDER_CANNOT_CREATE_CONTRACT_ARTIFACT)
    if gate.foreign_root_authority_granted:
        _append_reason(reasons, REASON_CROSS_ROOT_AUTHORITY_TRANSFER)
    if gate.post_root_reasoning_restarted:
        _append_reason(reasons, REASON_POST_ROOT_REASONING_RESTART_FORBIDDEN)
    _check_real_effects(reasons, gate)
    return _report(
        artifact_type="AirlineRootPhaseGateV01",
        artifact_id=gate.gate_id,
        transaction_id=gate.transaction_id,
        relevant_root_id=gate.root_id,
        reasons=reasons,
        authority_created=gate.foreign_root_authority_granted,
        real_world_effects_count=gate.real_world_effects_count,
    )


def validate_human_approval_evidence_ref_v01(
    evidence: AirlinePurchaseApprovalEvidenceRefV01,
    contract_context: AirlineTicketPurchaseContractContextV01 | None = None,
) -> AirlineCorridorValidationReportV01:
    context = _contract_context(contract_context)
    reasons: list[str] = []
    if evidence.transaction_id != context.transaction_id:
        _append_reason(reasons, REASON_WRONG_TRANSACTION_ID)
    if evidence.client_root_id != CLIENT_ROOT_ID:
        _append_reason(reasons, REASON_WRONG_ROOT_OWNER)
    if evidence.selected_offer_id != context.offer_id:
        _append_reason(reasons, REASON_SELECTED_OFFER_MISMATCH)
    if evidence.passenger_ref != context.passenger_ref:
        _append_reason(reasons, REASON_PASSENGER_REF_MISMATCH)
    if evidence.currency != context.currency:
        _append_reason(reasons, REASON_CURRENCY_MISMATCH)
    if evidence.max_amount != context.max_amount:
        _append_reason(reasons, REASON_AMOUNT_EXCEEDS_HUMAN_APPROVAL)
    if not evidence.evidence_only:
        _append_reason(reasons, REASON_HUMAN_APPROVAL_IS_EVIDENCE_ONLY)
    if evidence.creates_client_purchase_intent:
        _append_reason(reasons, REASON_HUMAN_APPROVAL_CANNOT_CREATE_PURCHASE_INTENT)
    if evidence.creates_action_commit_packet:
        _append_reason(
            reasons,
            REASON_HUMAN_APPROVAL_CANNOT_CREATE_ACTION_COMMIT_PACKET,
        )
    if (
        evidence.creates_receipt
        or evidence.creates_payment_authorization
        or evidence.creates_ticket
        or evidence.creates_booking
    ):
        _append_reason(reasons, REASON_RECEIPT_CREATED_PERMISSION)
    if evidence.creates_future_permission:
        _append_reason(reasons, REASON_RECEIPT_CREATED_FUTURE_PERMISSION)
    _check_real_effects(reasons, evidence)
    return _report(
        artifact_type="AirlinePurchaseApprovalEvidenceRefV01",
        artifact_id=evidence.approval_ref,
        transaction_id=evidence.transaction_id,
        relevant_root_id=CLIENT_ROOT_ID,
        reasons=reasons,
        permission_created=evidence.creates_client_purchase_intent,
        real_world_effects_count=evidence.real_world_effects_count,
    )


def validate_airline_offer_packet_v01(
    packet: AirlineOfferPacketV01,
    contract_context: AirlineTicketPurchaseContractContextV01 | None = None,
) -> AirlineCorridorValidationReportV01:
    context = _contract_context(contract_context)
    reasons: list[str] = []
    _check_transaction(reasons, packet)
    _check_created_by_root(
        reasons,
        created_by=packet.created_by,
        expected_root_id=AIRLINE_ROOT_ID,
    )
    _check_root_owner(
        reasons,
        root_owner=packet.root_owner,
        expected_root_id=AIRLINE_ROOT_ID,
    )
    if packet.airline_root_id != AIRLINE_ROOT_ID:
        _append_reason(reasons, REASON_WRONG_ROOT_OWNER)
    if packet.transaction_id != context.transaction_id:
        _append_reason(reasons, REASON_WRONG_TRANSACTION_ID)
    if packet.offer_id != context.offer_id:
        _append_reason(reasons, REASON_SELECTED_OFFER_MISMATCH)
    if packet.passenger_ref != context.passenger_ref:
        _append_reason(reasons, REASON_PASSENGER_REF_MISMATCH)
    if packet.route_ref != context.route_ref:
        _append_reason(reasons, REASON_ROUTE_REF_MISMATCH)
    if packet.amount != context.amount:
        _append_reason(reasons, REASON_AMOUNT_MISMATCH)
    if packet.currency != context.currency:
        _append_reason(reasons, REASON_CURRENCY_MISMATCH)
    if packet.expired:
        _append_reason(reasons, REASON_EXPIRED_OFFER)
    if packet.ttl_seconds <= 0:
        _append_reason(reasons, REASON_EXPIRED_OFFER)
    if (
        not packet.evidence_only
        or packet.purchase_permission_created
        or packet.payment_permission_created
        or packet.ticket_permission_created
    ):
        _append_reason(reasons, REASON_RECEIPT_CREATED_PERMISSION)
    _check_real_effects(reasons, packet)
    return _report(
        artifact_type=ARTIFACT_AIRLINE_OFFER_PACKET,
        artifact_id=packet.packet_id,
        transaction_id=packet.transaction_id,
        relevant_root_id=AIRLINE_ROOT_ID,
        reasons=reasons,
        permission_created=(
            packet.purchase_permission_created
            or packet.payment_permission_created
            or packet.ticket_permission_created
        ),
        real_world_effects_count=packet.real_world_effects_count,
    )


def validate_airline_hold_commit_packet_v01(
    offer_packet: AirlineOfferPacketV01,
    hold_packet: AirlineHoldCommitPacketV01,
    contract_context: AirlineTicketPurchaseContractContextV01 | None = None,
) -> AirlineCorridorValidationReportV01:
    context = _contract_context(contract_context)
    reasons: list[str] = list(
        validate_airline_offer_packet_v01(
            offer_packet,
            contract_context=context,
        ).reason_codes,
    )
    _check_transaction(reasons, offer_packet, hold_packet)
    _check_created_by_root(
        reasons,
        created_by=hold_packet.created_by,
        expected_root_id=AIRLINE_ROOT_ID,
    )
    _check_root_owner(
        reasons,
        root_owner=hold_packet.root_owner,
        expected_root_id=AIRLINE_ROOT_ID,
    )
    if hold_packet.parent_offer_packet_id != offer_packet.packet_id:
        _append_reason(reasons, REASON_PARENT_ARTIFACT_BINDING_MISMATCH)
        _append_reason(reasons, REASON_MISSING_OFFER_PACKET)
    if hold_packet.hold_id != context.hold_id:
        _append_reason(reasons, REASON_HOLD_ID_MISMATCH)
    _check_offer_hold_match(reasons, offer_packet, hold_packet)
    if hold_packet.ttl_seconds > offer_packet.ttl_seconds:
        _append_reason(reasons, REASON_CHILD_TTL_EXCEEDS_PARENT_TTL)
    if hold_packet.expired:
        _append_reason(reasons, REASON_EXPIRED_HOLD)
    _check_idempotency(reasons, hold_packet.idempotency_key)
    if hold_packet.allowed_action != ACTION_MOCK_OFFER_HOLD:
        _append_reason(reasons, REASON_FORBIDDEN_ACTION_REQUESTED)
    if ADAPTER_AIRLINE_HOLD_SANDBOX not in hold_packet.allowed_adapters:
        _append_reason(reasons, REASON_ADAPTER_NOT_ALLOWED)
    if not set(
        (
            ACTION_REAL_PAYMENT,
            ACTION_REAL_TICKET_ISSUE,
            ACTION_REAL_BOOKING,
            ACTION_REAL_AIRLINE_API,
            ACTION_REAL_BANK_API,
            ACTION_REAL_GDS_API,
            ACTION_POST_ROOT_LLM_REASONING,
        ),
    ).issubset(set(hold_packet.forbidden_actions)):
        _append_reason(reasons, REASON_FORBIDDEN_ACTION_REQUESTED)
    _check_real_effects(reasons, hold_packet)
    return _report(
        artifact_type=ARTIFACT_AIRLINE_HOLD_COMMIT_PACKET,
        artifact_id=hold_packet.packet_id,
        transaction_id=hold_packet.transaction_id,
        relevant_root_id=AIRLINE_ROOT_ID,
        reasons=reasons,
        real_world_effects_count=0,
    )


def validate_airline_offer_hold_receipt_v01(
    hold_packet: AirlineHoldCommitPacketV01,
    receipt: AirlineOfferHoldReceiptV01,
) -> AirlineCorridorValidationReportV01:
    reasons: list[str] = []
    _check_transaction(reasons, hold_packet, receipt)
    if receipt.created_by != ADAPTER_AIRLINE_HOLD_SANDBOX:
        _append_reason(reasons, REASON_ADAPTER_NOT_ALLOWED)
    _check_root_owner(
        reasons,
        root_owner=receipt.root_owner,
        expected_root_id=AIRLINE_ROOT_ID,
    )
    if receipt.source_hold_packet_id != hold_packet.packet_id:
        _append_reason(reasons, REASON_PARENT_ARTIFACT_BINDING_MISMATCH)
        _append_reason(reasons, REASON_MISSING_HOLD_PACKET)
    if receipt.source_idempotency_key != hold_packet.idempotency_key:
        _append_reason(reasons, REASON_DUPLICATE_IDEMPOTENCY_KEY)
    _check_hold_receipt_match(reasons, hold_packet, receipt)
    _check_receipt_evidence(
        reasons,
        evidence_only=receipt.evidence_only,
        permission_flags=(
            receipt.purchase_permission_created,
            receipt.payment_permission_created,
            receipt.ticket_permission_created,
        ),
        future_permission_created=receipt.future_permission_created,
    )
    _check_real_effects(reasons, receipt)
    return _report(
        artifact_type=ARTIFACT_AIRLINE_OFFER_HOLD_RECEIPT,
        artifact_id=receipt.receipt_id,
        transaction_id=receipt.transaction_id,
        relevant_root_id=AIRLINE_ROOT_ID,
        reasons=reasons,
        permission_created=(
            receipt.purchase_permission_created
            or receipt.payment_permission_created
            or receipt.ticket_permission_created
            or receipt.future_permission_created
        ),
        real_world_effects_count=receipt.real_world_effects_count,
    )


def validate_client_purchase_intent_v01(
    human_approval: AirlinePurchaseApprovalEvidenceRefV01,
    offer_packet: AirlineOfferPacketV01 | None,
    hold_receipt: AirlineOfferHoldReceiptV01 | None,
    purchase_intent: ClientPurchaseIntentV01,
    contract_context: AirlineTicketPurchaseContractContextV01 | None = None,
) -> AirlineCorridorValidationReportV01:
    context = _contract_context(contract_context)
    reasons: list[str] = list(
        validate_human_approval_evidence_ref_v01(
            human_approval,
            contract_context=context,
        ).reason_codes,
    )
    if offer_packet is None:
        _append_reason(reasons, REASON_MISSING_OFFER_PACKET)
    if hold_receipt is None:
        _append_reason(reasons, REASON_MISSING_OFFER_HOLD_RECEIPT)
        _append_reason(reasons, REASON_PURCHASE_INTENT_BEFORE_OFFER_HOLD)
    _check_transaction(
        reasons,
        human_approval,
        *(item for item in (offer_packet, hold_receipt) if item is not None),
        purchase_intent,
    )
    _check_created_by_root(
        reasons,
        created_by=purchase_intent.created_by,
        expected_root_id=CLIENT_ROOT_ID,
    )
    if "human" in purchase_intent.created_by.lower():
        _append_reason(reasons, REASON_HUMAN_APPROVAL_CANNOT_CREATE_PURCHASE_INTENT)
    _check_root_owner(
        reasons,
        root_owner=purchase_intent.root_owner,
        expected_root_id=CLIENT_ROOT_ID,
    )
    if purchase_intent.client_root_id != CLIENT_ROOT_ID:
        _append_reason(reasons, REASON_WRONG_ROOT_OWNER)
    if purchase_intent.offer_id != context.offer_id:
        _append_reason(reasons, REASON_SELECTED_OFFER_MISMATCH)
    if purchase_intent.hold_id != context.hold_id:
        _append_reason(reasons, REASON_HOLD_ID_MISMATCH)
    if purchase_intent.route_ref != context.route_ref:
        _append_reason(reasons, REASON_ROUTE_REF_MISMATCH)
    if purchase_intent.selected_amount != context.amount:
        _append_reason(reasons, REASON_AMOUNT_MISMATCH)
    if purchase_intent.currency != context.currency:
        _append_reason(reasons, REASON_CURRENCY_MISMATCH)
    if purchase_intent.source_human_approval_ref != human_approval.approval_ref:
        _append_reason(reasons, REASON_HUMAN_APPROVAL_IS_EVIDENCE_ONLY)
    if offer_packet is not None:
        if purchase_intent.selected_offer_packet_id != offer_packet.packet_id:
            _append_reason(reasons, REASON_SELECTED_OFFER_MISMATCH)
        if purchase_intent.offer_id != offer_packet.offer_id:
            _append_reason(reasons, REASON_SELECTED_OFFER_MISMATCH)
    if hold_receipt is not None:
        if purchase_intent.required_offer_hold_receipt_id != hold_receipt.receipt_id:
            _append_reason(reasons, REASON_MISSING_OFFER_HOLD_RECEIPT)
        _check_purchase_hold_match(reasons, purchase_intent, hold_receipt)
    if purchase_intent.offer_id != human_approval.selected_offer_id:
        _append_reason(reasons, REASON_SELECTED_OFFER_MISMATCH)
    if purchase_intent.passenger_ref != human_approval.passenger_ref:
        _append_reason(reasons, REASON_PASSENGER_REF_MISMATCH)
    if purchase_intent.currency != human_approval.currency:
        _append_reason(reasons, REASON_CURRENCY_MISMATCH)
    if purchase_intent.selected_amount > human_approval.max_amount:
        _append_reason(reasons, REASON_AMOUNT_EXCEEDS_HUMAN_APPROVAL)
    if purchase_intent.selected_amount > purchase_intent.max_amount:
        _append_reason(reasons, REASON_AMOUNT_EXCEEDS_HUMAN_APPROVAL)
    if purchase_intent.expired:
        _append_reason(reasons, REASON_EXPIRED_PURCHASE_INTENT)
    _check_idempotency(reasons, purchase_intent.idempotency_key)
    if purchase_intent.allowed_action != ACTION_CLIENT_PURCHASE_INTENT:
        _append_reason(reasons, REASON_FORBIDDEN_ACTION_REQUESTED)
    if purchase_intent.bank_authority_created or purchase_intent.airline_authority_created:
        _append_reason(reasons, REASON_CROSS_ROOT_AUTHORITY_TRANSFER)
    if purchase_intent.action_commit_packet_created_by_human:
        _append_reason(
            reasons,
            REASON_HUMAN_APPROVAL_CANNOT_CREATE_ACTION_COMMIT_PACKET,
        )
    if purchase_intent.future_permission_created:
        _append_reason(reasons, REASON_RECEIPT_CREATED_FUTURE_PERMISSION)
    _check_real_effects(reasons, purchase_intent)
    return _report(
        artifact_type=ARTIFACT_CLIENT_PURCHASE_INTENT,
        artifact_id=purchase_intent.intent_id,
        transaction_id=purchase_intent.transaction_id,
        relevant_root_id=CLIENT_ROOT_ID,
        reasons=reasons,
        authority_created=(
            purchase_intent.bank_authority_created
            or purchase_intent.airline_authority_created
        ),
        permission_created=purchase_intent.future_permission_created,
        real_world_effects_count=purchase_intent.real_world_effects_count,
    )


def validate_bank_payment_authorization_ref_v01(
    purchase_intent: ClientPurchaseIntentV01,
    authorization_ref: BankPaymentAuthorizationRefV01,
    contract_context: AirlineTicketPurchaseContractContextV01 | None = None,
) -> AirlineCorridorValidationReportV01:
    context = _contract_context(contract_context)
    reasons: list[str] = []
    _check_transaction(reasons, purchase_intent, authorization_ref)
    _check_created_by_root(
        reasons,
        created_by=authorization_ref.created_by,
        expected_root_id=BANK_ROOT_ID,
    )
    _check_root_owner(
        reasons,
        root_owner=authorization_ref.root_owner,
        expected_root_id=BANK_ROOT_ID,
    )
    if authorization_ref.bank_root_id != BANK_ROOT_ID:
        _append_reason(reasons, REASON_WRONG_ROOT_OWNER)
    if authorization_ref.source_purchase_intent_id != purchase_intent.intent_id:
        _append_reason(reasons, REASON_TICKET_ISSUE_WITHOUT_CLIENT_PURCHASE_INTENT)
    _check_auth_purchase_match(reasons, authorization_ref, purchase_intent)
    if authorization_ref.merchant_ref != context.merchant_ref:
        _append_reason(reasons, REASON_MERCHANT_MISMATCH)
    if authorization_ref.offer_id != context.offer_id:
        _append_reason(reasons, REASON_SELECTED_OFFER_MISMATCH)
    if authorization_ref.hold_id != context.hold_id:
        _append_reason(reasons, REASON_HOLD_ID_MISMATCH)
    if authorization_ref.route_ref != context.route_ref:
        _append_reason(reasons, REASON_ROUTE_REF_MISMATCH)
    if authorization_ref.amount != context.amount:
        _append_reason(reasons, REASON_AMOUNT_MISMATCH)
    if authorization_ref.currency != context.currency:
        _append_reason(reasons, REASON_CURRENCY_MISMATCH)
    if authorization_ref.expired:
        _append_reason(reasons, REASON_EXPIRED_PAYMENT_AUTHORIZATION)
    _check_idempotency(reasons, authorization_ref.idempotency_key)
    if not authorization_ref.evidence_only:
        _append_reason(reasons, REASON_RECEIPT_NOT_EVIDENCE_ONLY)
    if authorization_ref.ticket_permission_created:
        _append_reason(reasons, REASON_RECEIPT_CREATED_PERMISSION)
    if authorization_ref.future_permission_created:
        _append_reason(reasons, REASON_RECEIPT_CREATED_FUTURE_PERMISSION)
    _check_real_effects(reasons, authorization_ref)
    return _report(
        artifact_type=ARTIFACT_BANK_PAYMENT_AUTHORIZATION_REF,
        artifact_id=authorization_ref.authorization_ref_id,
        transaction_id=authorization_ref.transaction_id,
        relevant_root_id=BANK_ROOT_ID,
        reasons=reasons,
        permission_created=(
            authorization_ref.ticket_permission_created
            or authorization_ref.future_permission_created
        ),
        real_world_effects_count=authorization_ref.real_world_effects_count,
    )


def validate_airline_ticket_issue_intent_v01(
    offer_packet: AirlineOfferPacketV01,
    hold_packet: AirlineHoldCommitPacketV01,
    hold_receipt: AirlineOfferHoldReceiptV01,
    purchase_intent: ClientPurchaseIntentV01 | None,
    authorization_ref: BankPaymentAuthorizationRefV01 | None,
    ticket_issue_intent: AirlineTicketIssueIntentV01,
    contract_context: AirlineTicketPurchaseContractContextV01 | None = None,
) -> AirlineCorridorValidationReportV01:
    context = _contract_context(contract_context)
    reasons: list[str] = []
    if purchase_intent is None:
        _append_reason(reasons, REASON_TICKET_ISSUE_WITHOUT_CLIENT_PURCHASE_INTENT)
    if authorization_ref is None:
        _append_reason(reasons, REASON_TICKET_ISSUE_WITHOUT_BANK_AUTHORIZATION)
    _check_transaction(
        reasons,
        offer_packet,
        hold_packet,
        hold_receipt,
        *(item for item in (purchase_intent, authorization_ref) if item is not None),
        ticket_issue_intent,
    )
    _check_created_by_root(
        reasons,
        created_by=ticket_issue_intent.created_by,
        expected_root_id=AIRLINE_ROOT_ID,
    )
    _check_root_owner(
        reasons,
        root_owner=ticket_issue_intent.root_owner,
        expected_root_id=AIRLINE_ROOT_ID,
    )
    if ticket_issue_intent.airline_root_id != AIRLINE_ROOT_ID:
        _append_reason(reasons, REASON_WRONG_ROOT_OWNER)
    if ticket_issue_intent.offer_id != context.offer_id:
        _append_reason(reasons, REASON_SELECTED_OFFER_MISMATCH)
    if ticket_issue_intent.hold_id != context.hold_id:
        _append_reason(reasons, REASON_HOLD_ID_MISMATCH)
    if ticket_issue_intent.route_ref != context.route_ref:
        _append_reason(reasons, REASON_ROUTE_REF_MISMATCH)
    if ticket_issue_intent.amount != context.amount:
        _append_reason(reasons, REASON_AMOUNT_MISMATCH)
    if ticket_issue_intent.currency != context.currency:
        _append_reason(reasons, REASON_CURRENCY_MISMATCH)
    if ticket_issue_intent.merchant_ref != context.merchant_ref:
        _append_reason(reasons, REASON_MERCHANT_MISMATCH)
    if ticket_issue_intent.required_offer_packet_id != offer_packet.packet_id:
        _append_reason(reasons, REASON_MISSING_OFFER_PACKET)
    if ticket_issue_intent.required_hold_packet_id != hold_packet.packet_id:
        _append_reason(reasons, REASON_MISSING_HOLD_PACKET)
    if ticket_issue_intent.required_offer_hold_receipt_id != hold_receipt.receipt_id:
        _append_reason(reasons, REASON_MISSING_OFFER_HOLD_RECEIPT)
    if purchase_intent and ticket_issue_intent.required_client_purchase_intent_id != purchase_intent.intent_id:
        _append_reason(reasons, REASON_TICKET_ISSUE_WITHOUT_CLIENT_PURCHASE_INTENT)
    if authorization_ref and ticket_issue_intent.required_payment_authorization_ref_id != authorization_ref.authorization_ref_id:
        _append_reason(reasons, REASON_TICKET_ISSUE_WITHOUT_BANK_AUTHORIZATION)
    _check_ticket_matches_offer_hold(reasons, ticket_issue_intent, offer_packet, hold_packet, hold_receipt)
    if purchase_intent:
        _check_ticket_matches_purchase(reasons, ticket_issue_intent, purchase_intent)
    if authorization_ref:
        _check_ticket_matches_auth(reasons, ticket_issue_intent, authorization_ref)
    if ticket_issue_intent.expired:
        _append_reason(reasons, REASON_EXPIRED_HOLD)
    if ticket_issue_intent.ttl_seconds > hold_packet.ttl_seconds:
        _append_reason(reasons, REASON_CHILD_TTL_EXCEEDS_PARENT_TTL)
    _check_idempotency(reasons, ticket_issue_intent.idempotency_key)
    if ticket_issue_intent.allowed_action != ACTION_MOCK_TICKET_ISSUE:
        _append_reason(reasons, REASON_FORBIDDEN_ACTION_REQUESTED)
    if ADAPTER_AIRLINE_TICKET_SANDBOX not in ticket_issue_intent.allowed_adapters:
        _append_reason(reasons, REASON_ADAPTER_NOT_ALLOWED)
    if any(
        action not in ticket_issue_intent.forbidden_actions
        for action in (
            ACTION_REAL_PAYMENT,
            ACTION_REAL_TICKET_ISSUE,
            ACTION_REAL_BOOKING,
            ACTION_REAL_AIRLINE_API,
            ACTION_REAL_BANK_API,
            ACTION_REAL_GDS_API,
            ACTION_POST_ROOT_LLM_REASONING,
        )
    ):
        _append_reason(reasons, REASON_FORBIDDEN_ACTION_REQUESTED)
    _check_real_effects(reasons, ticket_issue_intent)
    return _report(
        artifact_type=ARTIFACT_AIRLINE_TICKET_ISSUE_INTENT,
        artifact_id=ticket_issue_intent.intent_id,
        transaction_id=ticket_issue_intent.transaction_id,
        relevant_root_id=AIRLINE_ROOT_ID,
        reasons=reasons,
        real_world_effects_count=0,
    )


def validate_mock_ticket_receipt_v01(
    ticket_issue_intent: AirlineTicketIssueIntentV01,
    receipt: MockTicketReceiptV01,
    contract_context: AirlineTicketPurchaseContractContextV01 | None = None,
) -> AirlineCorridorValidationReportV01:
    context = _contract_context(contract_context)
    reasons: list[str] = []
    _check_transaction(reasons, ticket_issue_intent, receipt)
    if receipt.created_by != ADAPTER_AIRLINE_TICKET_SANDBOX:
        _append_reason(reasons, REASON_ADAPTER_NOT_ALLOWED)
    _check_root_owner(
        reasons,
        root_owner=receipt.root_owner,
        expected_root_id=AIRLINE_ROOT_ID,
    )
    if receipt.source_ticket_issue_intent_id != ticket_issue_intent.intent_id:
        _append_reason(reasons, REASON_PARENT_ARTIFACT_BINDING_MISMATCH)
    if receipt.source_idempotency_key != ticket_issue_intent.idempotency_key:
        _append_reason(reasons, REASON_DUPLICATE_IDEMPOTENCY_KEY)
    if receipt.offer_id != context.offer_id:
        _append_reason(reasons, REASON_SELECTED_OFFER_MISMATCH)
    if receipt.hold_id != context.hold_id:
        _append_reason(reasons, REASON_HOLD_ID_MISMATCH)
    if receipt.route_ref != context.route_ref:
        _append_reason(reasons, REASON_ROUTE_REF_MISMATCH)
    if receipt.amount != context.amount:
        _append_reason(reasons, REASON_AMOUNT_MISMATCH)
    if receipt.currency != context.currency:
        _append_reason(reasons, REASON_CURRENCY_MISMATCH)
    _check_ticket_receipt_match(reasons, ticket_issue_intent, receipt)
    _check_receipt_evidence(
        reasons,
        evidence_only=receipt.evidence_only,
        permission_flags=(
            receipt.payment_created,
            receipt.future_ticket_permission_created,
            receipt.future_payment_permission_created,
        ),
        future_permission_created=(
            receipt.future_ticket_permission_created
            or receipt.future_payment_permission_created
        ),
    )
    _check_real_effects(reasons, receipt)
    return _report(
        artifact_type=ARTIFACT_MOCK_TICKET_RECEIPT,
        artifact_id=receipt.receipt_id,
        transaction_id=receipt.transaction_id,
        relevant_root_id=AIRLINE_ROOT_ID,
        reasons=reasons,
        permission_created=(
            receipt.payment_created
            or receipt.future_ticket_permission_created
            or receipt.future_payment_permission_created
        ),
        real_world_effects_count=receipt.real_world_effects_count,
    )


def validate_mock_purchase_receipt_v01(
    purchase_intent: ClientPurchaseIntentV01,
    authorization_ref: BankPaymentAuthorizationRefV01,
    ticket_receipt: MockTicketReceiptV01,
    purchase_receipt: MockPurchaseReceiptV01,
) -> AirlineCorridorValidationReportV01:
    reasons: list[str] = []
    _check_transaction(reasons, purchase_intent, authorization_ref, ticket_receipt, purchase_receipt)
    if purchase_receipt.source_client_purchase_intent_id != purchase_intent.intent_id:
        _append_reason(reasons, REASON_PARENT_ARTIFACT_BINDING_MISMATCH)
    if purchase_receipt.source_payment_authorization_ref_id != authorization_ref.authorization_ref_id:
        _append_reason(reasons, REASON_TICKET_ISSUE_WITHOUT_BANK_AUTHORIZATION)
    if purchase_receipt.source_mock_ticket_receipt_id != ticket_receipt.receipt_id:
        _append_reason(reasons, REASON_PARENT_ARTIFACT_BINDING_MISMATCH)
    if purchase_receipt.client_root_id != CLIENT_ROOT_ID or purchase_receipt.root_owner != CLIENT_ROOT_ID:
        _append_reason(reasons, REASON_WRONG_ROOT_OWNER)
    if purchase_receipt.airline_root_id != AIRLINE_ROOT_ID or purchase_receipt.bank_root_id != BANK_ROOT_ID:
        _append_reason(reasons, REASON_WRONG_ROOT_OWNER)
    _check_receipt_evidence(
        reasons,
        evidence_only=purchase_receipt.evidence_only,
        permission_flags=(purchase_receipt.future_permission_created,),
        future_permission_created=purchase_receipt.future_permission_created,
    )
    if purchase_receipt.side_root_finals_replaced:
        _append_reason(reasons, REASON_SHARED_SUMMARY_BECAME_FOURTH_ROOT)
    if purchase_receipt.root_truth_rewritten:
        _append_reason(reasons, REASON_RECEIPT_REWROTE_ROOT_TRUTH)
    _check_real_effects(reasons, purchase_receipt)
    return _report(
        artifact_type=ARTIFACT_MOCK_PURCHASE_RECEIPT,
        artifact_id=purchase_receipt.receipt_id,
        transaction_id=purchase_receipt.transaction_id,
        relevant_root_id=CLIENT_ROOT_ID,
        reasons=reasons,
        authority_created=purchase_receipt.side_root_finals_replaced,
        permission_created=purchase_receipt.future_permission_created,
        real_world_effects_count=purchase_receipt.real_world_effects_count,
    )


def validate_corridor_dependency_chain_v01(
    airline_offer_hold_gate: AirlineRootPhaseGateV01,
    offer_packet: AirlineOfferPacketV01,
    hold_packet: AirlineHoldCommitPacketV01,
    hold_receipt: AirlineOfferHoldReceiptV01,
    client_purchase_gate: AirlineRootPhaseGateV01,
    human_approval: AirlinePurchaseApprovalEvidenceRefV01,
    purchase_intent: ClientPurchaseIntentV01,
    bank_gate: AirlineRootPhaseGateV01,
    authorization_ref: BankPaymentAuthorizationRefV01,
    airline_ticket_gate: AirlineRootPhaseGateV01,
    ticket_issue_intent: AirlineTicketIssueIntentV01,
    ticket_receipt: MockTicketReceiptV01,
    completion_gate: AirlineRootPhaseGateV01,
    purchase_receipt: MockPurchaseReceiptV01,
    contract_context: AirlineTicketPurchaseContractContextV01 | None = None,
) -> AirlineCorridorValidationReportV01:
    context = _contract_context(contract_context)
    reports = (
        validate_root_phase_gate_v01(airline_offer_hold_gate),
        validate_airline_offer_packet_v01(offer_packet, contract_context=context),
        validate_airline_hold_commit_packet_v01(
            offer_packet,
            hold_packet,
            contract_context=context,
        ),
        validate_airline_offer_hold_receipt_v01(hold_packet, hold_receipt),
        validate_root_phase_gate_v01(client_purchase_gate),
        validate_client_purchase_intent_v01(
            human_approval,
            offer_packet,
            hold_receipt,
            purchase_intent,
            contract_context=context,
        ),
        validate_root_phase_gate_v01(bank_gate),
        validate_bank_payment_authorization_ref_v01(
            purchase_intent,
            authorization_ref,
            contract_context=context,
        ),
        validate_root_phase_gate_v01(airline_ticket_gate),
        validate_airline_ticket_issue_intent_v01(
            offer_packet,
            hold_packet,
            hold_receipt,
            purchase_intent,
            authorization_ref,
            ticket_issue_intent,
            contract_context=context,
        ),
        validate_mock_ticket_receipt_v01(
            ticket_issue_intent,
            ticket_receipt,
            contract_context=context,
        ),
        validate_root_phase_gate_v01(completion_gate),
        validate_mock_purchase_receipt_v01(
            purchase_intent,
            authorization_ref,
            ticket_receipt,
            purchase_receipt,
        ),
    )
    reasons: list[str] = []
    for report in reports:
        for reason in report.reason_codes:
            _append_reason(reasons, reason)
    if any(report.validation_status != PASS for report in reports):
        _append_reason(
            reasons,
            REASON_PHASE_FAILURE_CANNOT_BE_REPAIRED_BY_LATER_PHASE,
        )
    return _report(
        artifact_type="AirlineTicketPurchaseCorridorDependencyChainV01",
        artifact_id=f"dependency_chain:{TRANSACTION_ID}",
        transaction_id=TRANSACTION_ID,
        relevant_root_id=CLIENT_ROOT_ID,
        reasons=reasons,
        authority_created=any(report.authority_created for report in reports),
        permission_created=any(report.permission_created for report in reports),
        real_world_effects_count=sum(report.real_world_effects_count for report in reports),
    )


def validate_no_cross_root_authority_transfer_v01(
    *artifacts: Any,
) -> AirlineCorridorValidationReportV01:
    reasons: list[str] = []
    for artifact in artifacts:
        if getattr(artifact, "foreign_root_authority_granted", False):
            _append_reason(reasons, REASON_CROSS_ROOT_AUTHORITY_TRANSFER)
        if getattr(artifact, "bank_authority_created", False):
            _append_reason(reasons, REASON_CROSS_ROOT_AUTHORITY_TRANSFER)
        if getattr(artifact, "airline_authority_created", False):
            _append_reason(reasons, REASON_CROSS_ROOT_AUTHORITY_TRANSFER)
        if getattr(artifact, "side_root_finals_replaced", False):
            _append_reason(reasons, REASON_SHARED_SUMMARY_BECAME_FOURTH_ROOT)
        if getattr(artifact, "root_truth_rewritten", False):
            _append_reason(reasons, REASON_RECEIPT_REWROTE_ROOT_TRUTH)
    return _report(
        artifact_type="CrossRootAuthorityBoundaryV01",
        artifact_id=f"cross_root_authority:{TRANSACTION_ID}",
        transaction_id=TRANSACTION_ID,
        relevant_root_id=CLIENT_ROOT_ID,
        reasons=reasons,
        authority_created=bool(reasons),
        real_world_effects_count=0,
    )


def validate_receipts_evidence_only_v01(
    *receipts: Any,
) -> AirlineCorridorValidationReportV01:
    reasons: list[str] = []
    for receipt in receipts:
        if not getattr(receipt, "evidence_only", False):
            _append_reason(reasons, REASON_RECEIPT_NOT_EVIDENCE_ONLY)
        if any(
            getattr(receipt, name, False)
            for name in (
                "purchase_permission_created",
                "payment_permission_created",
                "ticket_permission_created",
                "future_permission_created",
                "future_ticket_permission_created",
                "future_payment_permission_created",
                "payment_created",
            )
        ):
            _append_reason(reasons, REASON_RECEIPT_CREATED_PERMISSION)
    return _report(
        artifact_type="ReceiptEvidenceOnlyBoundaryV01",
        artifact_id=f"receipt_boundary:{TRANSACTION_ID}",
        transaction_id=TRANSACTION_ID,
        relevant_root_id=CLIENT_ROOT_ID,
        reasons=reasons,
        permission_created=bool(reasons),
        real_world_effects_count=0,
    )


def validate_no_real_effects_v01(*artifacts: Any) -> AirlineCorridorValidationReportV01:
    reasons: list[str] = []
    for artifact in artifacts:
        _check_real_effects(reasons, artifact)
    return _report(
        artifact_type="NoRealEffectsBoundaryV01",
        artifact_id=f"no_real_effects:{TRANSACTION_ID}",
        transaction_id=TRANSACTION_ID,
        relevant_root_id=CLIENT_ROOT_ID,
        reasons=reasons,
        real_world_effects_count=0,
    )


def _check_offer_hold_match(
    reasons: list[str],
    offer_packet: AirlineOfferPacketV01,
    hold_packet: AirlineHoldCommitPacketV01,
) -> None:
    if hold_packet.offer_id != offer_packet.offer_id:
        _append_reason(reasons, REASON_SELECTED_OFFER_MISMATCH)
    if hold_packet.passenger_ref != offer_packet.passenger_ref:
        _append_reason(reasons, REASON_PASSENGER_REF_MISMATCH)
    if hold_packet.route_ref != offer_packet.route_ref:
        _append_reason(reasons, REASON_ROUTE_REF_MISMATCH)
    if hold_packet.amount != offer_packet.amount:
        _append_reason(reasons, REASON_AMOUNT_MISMATCH)
    if hold_packet.currency != offer_packet.currency:
        _append_reason(reasons, REASON_CURRENCY_MISMATCH)


def _check_hold_receipt_match(
    reasons: list[str],
    hold_packet: AirlineHoldCommitPacketV01,
    receipt: AirlineOfferHoldReceiptV01,
) -> None:
    if receipt.offer_id != hold_packet.offer_id:
        _append_reason(reasons, REASON_SELECTED_OFFER_MISMATCH)
    if receipt.hold_id != hold_packet.hold_id:
        _append_reason(reasons, REASON_HOLD_ID_MISMATCH)
    if receipt.passenger_ref != hold_packet.passenger_ref:
        _append_reason(reasons, REASON_PASSENGER_REF_MISMATCH)
    if receipt.route_ref != hold_packet.route_ref:
        _append_reason(reasons, REASON_ROUTE_REF_MISMATCH)
    if receipt.amount != hold_packet.amount:
        _append_reason(reasons, REASON_AMOUNT_MISMATCH)
    if receipt.currency != hold_packet.currency:
        _append_reason(reasons, REASON_CURRENCY_MISMATCH)


def _check_purchase_hold_match(
    reasons: list[str],
    purchase_intent: ClientPurchaseIntentV01,
    hold_receipt: AirlineOfferHoldReceiptV01,
) -> None:
    if purchase_intent.offer_id != hold_receipt.offer_id:
        _append_reason(reasons, REASON_SELECTED_OFFER_MISMATCH)
    if purchase_intent.hold_id != hold_receipt.hold_id:
        _append_reason(reasons, REASON_HOLD_ID_MISMATCH)
    if purchase_intent.passenger_ref != hold_receipt.passenger_ref:
        _append_reason(reasons, REASON_PASSENGER_REF_MISMATCH)
    if purchase_intent.route_ref != hold_receipt.route_ref:
        _append_reason(reasons, REASON_ROUTE_REF_MISMATCH)
    if purchase_intent.selected_amount != hold_receipt.amount:
        _append_reason(reasons, REASON_AMOUNT_MISMATCH)
    if purchase_intent.currency != hold_receipt.currency:
        _append_reason(reasons, REASON_CURRENCY_MISMATCH)


def _check_auth_purchase_match(
    reasons: list[str],
    authorization_ref: BankPaymentAuthorizationRefV01,
    purchase_intent: ClientPurchaseIntentV01,
) -> None:
    if authorization_ref.offer_id != purchase_intent.offer_id:
        _append_reason(reasons, REASON_SELECTED_OFFER_MISMATCH)
    if authorization_ref.hold_id != purchase_intent.hold_id:
        _append_reason(reasons, REASON_HOLD_ID_MISMATCH)
    if authorization_ref.passenger_ref != purchase_intent.passenger_ref:
        _append_reason(reasons, REASON_PASSENGER_REF_MISMATCH)
    if authorization_ref.route_ref != purchase_intent.route_ref:
        _append_reason(reasons, REASON_ROUTE_REF_MISMATCH)
    if authorization_ref.amount != purchase_intent.selected_amount:
        _append_reason(reasons, REASON_AMOUNT_MISMATCH)
    if authorization_ref.currency != purchase_intent.currency:
        _append_reason(reasons, REASON_CURRENCY_MISMATCH)


def _check_ticket_matches_offer_hold(
    reasons: list[str],
    ticket_issue_intent: AirlineTicketIssueIntentV01,
    offer_packet: AirlineOfferPacketV01,
    hold_packet: AirlineHoldCommitPacketV01,
    hold_receipt: AirlineOfferHoldReceiptV01,
) -> None:
    if ticket_issue_intent.offer_id != offer_packet.offer_id:
        _append_reason(reasons, REASON_SELECTED_OFFER_MISMATCH)
    if ticket_issue_intent.hold_id != hold_packet.hold_id or ticket_issue_intent.hold_id != hold_receipt.hold_id:
        _append_reason(reasons, REASON_HOLD_ID_MISMATCH)
    if ticket_issue_intent.passenger_ref != offer_packet.passenger_ref:
        _append_reason(reasons, REASON_PASSENGER_REF_MISMATCH)
    if ticket_issue_intent.route_ref != offer_packet.route_ref:
        _append_reason(reasons, REASON_ROUTE_REF_MISMATCH)
    if ticket_issue_intent.amount != offer_packet.amount:
        _append_reason(reasons, REASON_AMOUNT_MISMATCH)
    if ticket_issue_intent.currency != offer_packet.currency:
        _append_reason(reasons, REASON_CURRENCY_MISMATCH)


def _check_ticket_matches_purchase(
    reasons: list[str],
    ticket_issue_intent: AirlineTicketIssueIntentV01,
    purchase_intent: ClientPurchaseIntentV01,
) -> None:
    if ticket_issue_intent.offer_id != purchase_intent.offer_id:
        _append_reason(reasons, REASON_SELECTED_OFFER_MISMATCH)
    if ticket_issue_intent.hold_id != purchase_intent.hold_id:
        _append_reason(reasons, REASON_HOLD_ID_MISMATCH)
    if ticket_issue_intent.passenger_ref != purchase_intent.passenger_ref:
        _append_reason(reasons, REASON_PASSENGER_REF_MISMATCH)
    if ticket_issue_intent.route_ref != purchase_intent.route_ref:
        _append_reason(reasons, REASON_ROUTE_REF_MISMATCH)
    if ticket_issue_intent.amount != purchase_intent.selected_amount:
        _append_reason(reasons, REASON_AMOUNT_MISMATCH)
    if ticket_issue_intent.currency != purchase_intent.currency:
        _append_reason(reasons, REASON_CURRENCY_MISMATCH)


def _check_ticket_matches_auth(
    reasons: list[str],
    ticket_issue_intent: AirlineTicketIssueIntentV01,
    authorization_ref: BankPaymentAuthorizationRefV01,
) -> None:
    if ticket_issue_intent.required_payment_authorization_ref_id != authorization_ref.authorization_ref_id:
        _append_reason(reasons, REASON_TICKET_ISSUE_WITHOUT_BANK_AUTHORIZATION)
    if ticket_issue_intent.merchant_ref != authorization_ref.merchant_ref:
        _append_reason(reasons, REASON_MERCHANT_MISMATCH)
    if ticket_issue_intent.amount != authorization_ref.amount:
        _append_reason(reasons, REASON_AMOUNT_MISMATCH)
    if ticket_issue_intent.currency != authorization_ref.currency:
        _append_reason(reasons, REASON_CURRENCY_MISMATCH)


def _check_ticket_receipt_match(
    reasons: list[str],
    ticket_issue_intent: AirlineTicketIssueIntentV01,
    receipt: MockTicketReceiptV01,
) -> None:
    if receipt.offer_id != ticket_issue_intent.offer_id:
        _append_reason(reasons, REASON_SELECTED_OFFER_MISMATCH)
    if receipt.hold_id != ticket_issue_intent.hold_id:
        _append_reason(reasons, REASON_HOLD_ID_MISMATCH)
    if receipt.passenger_ref != ticket_issue_intent.passenger_ref:
        _append_reason(reasons, REASON_PASSENGER_REF_MISMATCH)
    if receipt.route_ref != ticket_issue_intent.route_ref:
        _append_reason(reasons, REASON_ROUTE_REF_MISMATCH)
    if receipt.amount != ticket_issue_intent.amount:
        _append_reason(reasons, REASON_AMOUNT_MISMATCH)
    if receipt.currency != ticket_issue_intent.currency:
        _append_reason(reasons, REASON_CURRENCY_MISMATCH)


def build_valid_airline_root_offer_hold_gate_v01() -> AirlineRootPhaseGateV01:
    return AirlineRootPhaseGateV01(
        gate_id="gate:airline_offer_hold:001",
        transaction_id=TRANSACTION_ID,
        root_id=AIRLINE_ROOT_ID,
        phase_id=PHASE_AIRLINE_OFFER_HOLD,
        review_status=PASS,
        authorized_artifact_types=(
            ARTIFACT_AIRLINE_OFFER_PACKET,
            ARTIFACT_AIRLINE_HOLD_COMMIT_PACKET,
        ),
        evidence_refs=("semantic_lane:airline_offer_policy_reviewer_llm",),
        provider_created=False,
        foreign_root_authority_granted=False,
        post_root_reasoning_restarted=False,
        real_world_effects_count=0,
    )


def build_valid_client_root_purchase_intent_gate_v01() -> AirlineRootPhaseGateV01:
    return AirlineRootPhaseGateV01(
        gate_id="gate:client_purchase_intent:001",
        transaction_id=TRANSACTION_ID,
        root_id=CLIENT_ROOT_ID,
        phase_id=PHASE_CLIENT_PURCHASE_INTENT,
        review_status=PASS,
        authorized_artifact_types=(ARTIFACT_CLIENT_PURCHASE_INTENT,),
        evidence_refs=("offer_hold_receipt:mock_airline_al:001",),
        provider_created=False,
        foreign_root_authority_granted=False,
        post_root_reasoning_restarted=False,
        real_world_effects_count=0,
    )


def build_valid_bank_root_payment_authorization_gate_v01() -> AirlineRootPhaseGateV01:
    return AirlineRootPhaseGateV01(
        gate_id="gate:bank_payment_authorization:001",
        transaction_id=TRANSACTION_ID,
        root_id=BANK_ROOT_ID,
        phase_id=PHASE_BANK_PAYMENT_AUTHORIZATION,
        review_status=PASS,
        authorized_artifact_types=(ARTIFACT_BANK_PAYMENT_AUTHORIZATION_REF,),
        evidence_refs=("client_purchase_intent:client_001:001",),
        provider_created=False,
        foreign_root_authority_granted=False,
        post_root_reasoning_restarted=False,
        real_world_effects_count=0,
    )


def build_valid_airline_root_ticket_issue_gate_v01() -> AirlineRootPhaseGateV01:
    return AirlineRootPhaseGateV01(
        gate_id="gate:airline_ticket_issue:001",
        transaction_id=TRANSACTION_ID,
        root_id=AIRLINE_ROOT_ID,
        phase_id=PHASE_AIRLINE_TICKET_ISSUE,
        review_status=PASS,
        authorized_artifact_types=(ARTIFACT_AIRLINE_TICKET_ISSUE_INTENT,),
        evidence_refs=(
            "client_purchase_intent:client_001:001",
            "bank_payment_authorization_ref:mock_bank_a:001",
        ),
        provider_created=False,
        foreign_root_authority_granted=False,
        post_root_reasoning_restarted=False,
        real_world_effects_count=0,
    )


def build_valid_client_root_completion_gate_v01() -> AirlineRootPhaseGateV01:
    return AirlineRootPhaseGateV01(
        gate_id="gate:client_completion:001",
        transaction_id=TRANSACTION_ID,
        root_id=CLIENT_ROOT_ID,
        phase_id=PHASE_CLIENT_COMPLETION,
        review_status=PASS,
        authorized_artifact_types=(ARTIFACT_MOCK_PURCHASE_RECEIPT,),
        evidence_refs=("mock_ticket_receipt:mock_airline_al:001",),
        provider_created=False,
        foreign_root_authority_granted=False,
        post_root_reasoning_restarted=False,
        real_world_effects_count=0,
    )


def build_valid_human_approval_evidence_ref_v01() -> AirlinePurchaseApprovalEvidenceRefV01:
    return AirlinePurchaseApprovalEvidenceRefV01(
        approval_ref="human_approval:client_001:airline_purchase:001",
        transaction_id=TRANSACTION_ID,
        client_root_id=CLIENT_ROOT_ID,
        selected_offer_id=OFFER_ID,
        max_amount=MAX_AMOUNT,
        currency=CURRENCY,
        passenger_ref=PASSENGER_REF,
        approval_scope="selected_mock_offer_purchase_intent_only",
        evidence_only=True,
        creates_client_purchase_intent=False,
        creates_action_commit_packet=False,
        creates_receipt=False,
        creates_payment_authorization=False,
        creates_ticket=False,
        creates_booking=False,
        creates_future_permission=False,
        real_world_effects_count=0,
    )


def build_valid_airline_offer_packet_v01() -> AirlineOfferPacketV01:
    return AirlineOfferPacketV01(
        packet_id="airline_offer_packet:mock_airline_al:001",
        transaction_id=TRANSACTION_ID,
        created_by=AIRLINE_ROOT_ID,
        root_owner=AIRLINE_ROOT_ID,
        airline_root_id=AIRLINE_ROOT_ID,
        offer_id=OFFER_ID,
        passenger_ref=PASSENGER_REF,
        route_ref=ROUTE_REF,
        departure_date=DEPARTURE_DATE,
        return_date=RETURN_DATE,
        amount=AMOUNT,
        currency=CURRENCY,
        baggage_included=True,
        seat_ref="seat:18A",
        ttl_seconds=900,
        expired=False,
        evidence_only=True,
        purchase_permission_created=False,
        payment_permission_created=False,
        ticket_permission_created=False,
        real_world_effects_count=0,
    )


def build_valid_airline_hold_commit_packet_v01() -> AirlineHoldCommitPacketV01:
    offer_packet = build_valid_airline_offer_packet_v01()
    return AirlineHoldCommitPacketV01(
        packet_id="airline_hold_commit_packet:mock_airline_al:001",
        transaction_id=TRANSACTION_ID,
        parent_offer_packet_id=offer_packet.packet_id,
        created_by=AIRLINE_ROOT_ID,
        root_owner=AIRLINE_ROOT_ID,
        airline_root_id=AIRLINE_ROOT_ID,
        offer_id=OFFER_ID,
        hold_id=HOLD_ID,
        passenger_ref=PASSENGER_REF,
        route_ref=ROUTE_REF,
        amount=AMOUNT,
        currency=CURRENCY,
        ttl_seconds=900,
        expired=False,
        idempotency_key="idem:airline_hold:001",
        allowed_action=ACTION_MOCK_OFFER_HOLD,
        allowed_adapters=(ADAPTER_AIRLINE_HOLD_SANDBOX,),
        forbidden_actions=(
            ACTION_REAL_PAYMENT,
            ACTION_REAL_TICKET_ISSUE,
            ACTION_REAL_BOOKING,
            ACTION_REAL_AIRLINE_API,
            ACTION_REAL_BANK_API,
            ACTION_REAL_GDS_API,
            ACTION_POST_ROOT_LLM_REASONING,
        ),
        real_world_effects_allowed=False,
    )


def build_valid_airline_offer_hold_receipt_v01() -> AirlineOfferHoldReceiptV01:
    hold_packet = build_valid_airline_hold_commit_packet_v01()
    return AirlineOfferHoldReceiptV01(
        receipt_id="offer_hold_receipt:mock_airline_al:001",
        transaction_id=TRANSACTION_ID,
        source_hold_packet_id=hold_packet.packet_id,
        source_idempotency_key=hold_packet.idempotency_key,
        created_by=ADAPTER_AIRLINE_HOLD_SANDBOX,
        root_owner=AIRLINE_ROOT_ID,
        offer_id=OFFER_ID,
        hold_id=HOLD_ID,
        passenger_ref=PASSENGER_REF,
        route_ref=ROUTE_REF,
        amount=AMOUNT,
        currency=CURRENCY,
        evidence_only=True,
        purchase_permission_created=False,
        payment_permission_created=False,
        ticket_permission_created=False,
        future_permission_created=False,
        real_world_effects_count=0,
    )


def build_valid_client_purchase_intent_v01() -> ClientPurchaseIntentV01:
    return ClientPurchaseIntentV01(
        intent_id="client_purchase_intent:client_001:001",
        transaction_id=TRANSACTION_ID,
        created_by=CLIENT_ROOT_ID,
        root_owner=CLIENT_ROOT_ID,
        client_root_id=CLIENT_ROOT_ID,
        source_human_approval_ref=build_valid_human_approval_evidence_ref_v01().approval_ref,
        selected_offer_packet_id=build_valid_airline_offer_packet_v01().packet_id,
        required_offer_hold_receipt_id=build_valid_airline_offer_hold_receipt_v01().receipt_id,
        offer_id=OFFER_ID,
        hold_id=HOLD_ID,
        passenger_ref=PASSENGER_REF,
        route_ref=ROUTE_REF,
        max_amount=MAX_AMOUNT,
        selected_amount=AMOUNT,
        currency=CURRENCY,
        ttl_seconds=900,
        expired=False,
        idempotency_key="idem:client_purchase_intent:001",
        allowed_action=ACTION_CLIENT_PURCHASE_INTENT,
        bank_authority_created=False,
        airline_authority_created=False,
        action_commit_packet_created_by_human=False,
        payment_executed=False,
        ticket_issued=False,
        booking_created=False,
        future_permission_created=False,
        real_world_effects_count=0,
    )


def build_valid_bank_payment_authorization_ref_v01() -> BankPaymentAuthorizationRefV01:
    return BankPaymentAuthorizationRefV01(
        authorization_ref_id="bank_payment_authorization_ref:mock_bank_a:001",
        transaction_id=TRANSACTION_ID,
        created_by=BANK_ROOT_ID,
        root_owner=BANK_ROOT_ID,
        bank_root_id=BANK_ROOT_ID,
        source_payment_receipt_id="payment_authorization_receipt:mock_bank_a:001",
        source_purchase_intent_id=build_valid_client_purchase_intent_v01().intent_id,
        merchant_ref=MERCHANT_REF,
        offer_id=OFFER_ID,
        hold_id=HOLD_ID,
        passenger_ref=PASSENGER_REF,
        route_ref=ROUTE_REF,
        amount=AMOUNT,
        currency=CURRENCY,
        ttl_seconds=900,
        expired=False,
        idempotency_key="idem:bank_payment_authorization:001",
        evidence_only=True,
        settlement_executed=False,
        real_payment_executed=False,
        ticket_permission_created=False,
        future_permission_created=False,
        real_world_effects_count=0,
    )


def build_valid_airline_ticket_issue_intent_v01() -> AirlineTicketIssueIntentV01:
    return AirlineTicketIssueIntentV01(
        intent_id="airline_ticket_issue_intent:mock_airline_al:001",
        transaction_id=TRANSACTION_ID,
        created_by=AIRLINE_ROOT_ID,
        root_owner=AIRLINE_ROOT_ID,
        airline_root_id=AIRLINE_ROOT_ID,
        required_offer_packet_id=build_valid_airline_offer_packet_v01().packet_id,
        required_hold_packet_id=build_valid_airline_hold_commit_packet_v01().packet_id,
        required_offer_hold_receipt_id=build_valid_airline_offer_hold_receipt_v01().receipt_id,
        required_client_purchase_intent_id=build_valid_client_purchase_intent_v01().intent_id,
        required_payment_authorization_ref_id=build_valid_bank_payment_authorization_ref_v01().authorization_ref_id,
        offer_id=OFFER_ID,
        hold_id=HOLD_ID,
        passenger_ref=PASSENGER_REF,
        route_ref=ROUTE_REF,
        amount=AMOUNT,
        currency=CURRENCY,
        merchant_ref=MERCHANT_REF,
        ttl_seconds=900,
        expired=False,
        idempotency_key="idem:airline_ticket_issue:001",
        allowed_action=ACTION_MOCK_TICKET_ISSUE,
        allowed_adapters=(ADAPTER_AIRLINE_TICKET_SANDBOX,),
        forbidden_actions=(
            ACTION_REAL_PAYMENT,
            ACTION_REAL_TICKET_ISSUE,
            ACTION_REAL_BOOKING,
            ACTION_REAL_AIRLINE_API,
            ACTION_REAL_BANK_API,
            ACTION_REAL_GDS_API,
            ACTION_POST_ROOT_LLM_REASONING,
        ),
        real_ticket_allowed=False,
        real_booking_allowed=False,
        real_airline_api_allowed=False,
        real_world_effects_allowed=False,
    )


def build_valid_mock_ticket_receipt_v01() -> MockTicketReceiptV01:
    ticket_issue_intent = build_valid_airline_ticket_issue_intent_v01()
    return MockTicketReceiptV01(
        receipt_id="mock_ticket_receipt:mock_airline_al:001",
        transaction_id=TRANSACTION_ID,
        source_ticket_issue_intent_id=ticket_issue_intent.intent_id,
        source_idempotency_key=ticket_issue_intent.idempotency_key,
        created_by=ADAPTER_AIRLINE_TICKET_SANDBOX,
        root_owner=AIRLINE_ROOT_ID,
        mock_ticket_id=MOCK_TICKET_ID,
        mock_pnr=MOCK_PNR,
        offer_id=OFFER_ID,
        hold_id=HOLD_ID,
        passenger_ref=PASSENGER_REF,
        route_ref=ROUTE_REF,
        amount=AMOUNT,
        currency=CURRENCY,
        evidence_only=True,
        real_ticket=False,
        real_booking=False,
        payment_created=False,
        future_ticket_permission_created=False,
        future_payment_permission_created=False,
        real_world_effects_count=0,
    )


def build_valid_mock_purchase_receipt_v01() -> MockPurchaseReceiptV01:
    return MockPurchaseReceiptV01(
        receipt_id="mock_purchase_receipt:client_001:001",
        transaction_id=TRANSACTION_ID,
        source_client_purchase_intent_id=build_valid_client_purchase_intent_v01().intent_id,
        source_payment_authorization_ref_id=build_valid_bank_payment_authorization_ref_v01().authorization_ref_id,
        source_mock_ticket_receipt_id=build_valid_mock_ticket_receipt_v01().receipt_id,
        client_root_id=CLIENT_ROOT_ID,
        airline_root_id=AIRLINE_ROOT_ID,
        bank_root_id=BANK_ROOT_ID,
        created_by="client_completion_observer",
        root_owner=CLIENT_ROOT_ID,
        evidence_only=True,
        side_root_finals_replaced=False,
        root_truth_rewritten=False,
        future_permission_created=False,
        real_payment_executed=False,
        real_ticket_issued=False,
        real_booking_created=False,
        real_world_effects_count=0,
    )
