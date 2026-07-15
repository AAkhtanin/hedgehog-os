"""Airline Transaction Artifact Ledger v0.1 source collector.

This Slice C module is an Airline-domain source projection. It consumes one
explicit immutable bundle of already-created source artifacts and maps it into
the committed Ledger geometry. It is not Hedgehog OS universal kernel/core and
not an installed Needle.

The collector records exact source trace only. It creates no authority,
permission, action, packet, receipt, payment, ticket, booking, or FinalOutput.
It performs no provider, network, Gemini, file, Crypto Artifact Seal, or Replay
work.
"""

from __future__ import annotations

from collections.abc import Mapping as MappingABC
from dataclasses import dataclass, replace
from types import MappingProxyType
from typing import Any, Mapping

from hedgehog.domains.airline import (
    semantic_to_contract_binding_v01 as binding,
)
from hedgehog.domains.airline import (
    semantic_to_contract_causal_runtime_v01 as causal_runtime,
)
from hedgehog.domains.airline import (
    ticket_purchase_corridor_runtime_v01 as corridor_runtime,
)
from hedgehog.domains.airline import (
    ticket_purchase_corridor_v01 as corridor_contracts,
)
from hedgehog.domains.airline import transaction_artifact_ledger_v01 as ledger


MODULE_ID = "airline_transaction_artifact_ledger_collector_v01"
SLICE_ID = "airline_transaction_artifact_ledger_v01_slice_c"

STATUS_PASS = ledger.STATUS_PASS
STATUS_FAIL_CLOSED = ledger.STATUS_FAIL_CLOSED

SIDE_CLIENT = "client"
SIDE_AIRLINE = "airline"
SIDE_BANK = "bank"
SIDE_CROSS_ROOT_ADVISORY = "cross_root_advisory"

REASON_SOURCE_BUNDLE_WRONG_TYPE = "source_bundle_wrong_type"
REASON_SOURCE_BUNDLE_TRANSACTION_MISMATCH = "source_bundle_transaction_mismatch"
REASON_SOURCE_CAUSAL_REPORT_INVALID = "source_causal_report_invalid"
REASON_SOURCE_CORRIDOR_REPORT_INVALID = "source_corridor_report_invalid"
REASON_SOURCE_BSEP_PROJECTION_MISSING = "source_bsep_projection_missing"
REASON_SOURCE_BSEP_LINEAGE_MISMATCH = "source_bsep_lineage_mismatch"
REASON_SOURCE_ARTIFACT_MISSING = "source_artifact_missing"
REASON_SOURCE_ARTIFACT_WRONG_TYPE = "source_artifact_wrong_type"
REASON_SOURCE_ARTIFACT_ID_MISMATCH = "source_artifact_id_mismatch"
REASON_SOURCE_ARTIFACT_OFFER_MISMATCH = "source_artifact_offer_mismatch"
REASON_SOURCE_ARTIFACT_HOLD_MISMATCH = "source_artifact_hold_mismatch"
REASON_SOURCE_ARTIFACT_AMOUNT_MISMATCH = "source_artifact_amount_mismatch"
REASON_SOURCE_ARTIFACT_CURRENCY_MISMATCH = "source_artifact_currency_mismatch"
REASON_SOURCE_ARTIFACT_ROUTE_MISMATCH = "source_artifact_route_mismatch"
REASON_SOURCE_ARTIFACT_PASSENGER_MISMATCH = "source_artifact_passenger_mismatch"
REASON_SOURCE_PHASE_EVIDENCE_REF_MISMATCH = "source_phase_evidence_ref_mismatch"
REASON_SOURCE_ROOT_FINAL_MISSING = "source_root_final_missing"
REASON_SOURCE_ROOT_FINAL_WRONG_OWNER = "source_root_final_wrong_owner"
REASON_SOURCE_SHARED_SUMMARY_USED_AS_ROOT_FINAL = (
    "source_shared_summary_used_as_root_final"
)
REASON_SOURCE_REF_MISMATCH = ledger.REASON_SOURCE_REF_MISMATCH
REASON_SOURCE_PROVIDER_AUTHORITY_DETECTED = "source_provider_authority_detected"
REASON_SOURCE_REAL_EFFECT_DETECTED = "source_real_effect_detected"
REASON_SOURCE_RECONSTRUCTION_FORBIDDEN = "source_reconstruction_forbidden"
EXPECTED_AUXILIARY_OBSERVATION_REFS = (
    ledger.OPAQUE_PROMPT_REF,
    ledger.OPAQUE_RESPONSE_REF,
)
CONTRACT_CONTEXT_SNAPSHOT_FIELDS = (
    "transaction_id",
    "offer_id",
    "hold_id",
    "amount",
    "currency",
    "route_ref",
    "passenger_ref",
    "max_amount",
    "merchant_ref",
)
BSEP_PROJECTION_SNAPSHOT_FIELDS = (
    "projection_id",
    "projection_ref",
    "bsep_packet_id",
    "transaction_id",
    "side",
    "validation_status",
    "authority_created",
    "permission_created",
    "real_world_effects_count",
)
OFFER_PACKET_SNAPSHOT_FIELDS = (
    "packet_id",
    "transaction_id",
    "created_by",
    "root_owner",
    "airline_root_id",
    "offer_id",
    "passenger_ref",
    "route_ref",
    "departure_date",
    "return_date",
    "amount",
    "currency",
    "baggage_included",
    "seat_ref",
    "ttl_seconds",
    "expired",
    "evidence_only",
    "purchase_permission_created",
    "payment_permission_created",
    "ticket_permission_created",
    "real_world_effects_count",
)
HOLD_PACKET_SNAPSHOT_FIELDS = (
    "packet_id",
    "transaction_id",
    "parent_offer_packet_id",
    "created_by",
    "root_owner",
    "airline_root_id",
    "offer_id",
    "hold_id",
    "passenger_ref",
    "route_ref",
    "amount",
    "currency",
    "ttl_seconds",
    "expired",
    "idempotency_key",
    "allowed_action",
    "allowed_adapters",
    "forbidden_actions",
    "real_world_effects_allowed",
)
HOLD_RECEIPT_SNAPSHOT_FIELDS = (
    "receipt_id",
    "transaction_id",
    "source_hold_packet_id",
    "source_idempotency_key",
    "created_by",
    "root_owner",
    "offer_id",
    "hold_id",
    "passenger_ref",
    "route_ref",
    "amount",
    "currency",
    "evidence_only",
    "purchase_permission_created",
    "payment_permission_created",
    "ticket_permission_created",
    "future_permission_created",
    "real_world_effects_count",
)
APPROVAL_SNAPSHOT_FIELDS = (
    "approval_ref",
    "transaction_id",
    "client_root_id",
    "selected_offer_id",
    "max_amount",
    "currency",
    "passenger_ref",
    "approval_scope",
    "evidence_only",
    "creates_client_purchase_intent",
    "creates_action_commit_packet",
    "creates_receipt",
    "creates_payment_authorization",
    "creates_ticket",
    "creates_booking",
    "creates_future_permission",
    "real_world_effects_count",
)
PURCHASE_INTENT_SNAPSHOT_FIELDS = (
    "intent_id",
    "transaction_id",
    "created_by",
    "root_owner",
    "client_root_id",
    "source_human_approval_ref",
    "selected_offer_packet_id",
    "required_offer_hold_receipt_id",
    "offer_id",
    "hold_id",
    "passenger_ref",
    "route_ref",
    "max_amount",
    "selected_amount",
    "currency",
    "ttl_seconds",
    "expired",
    "idempotency_key",
    "allowed_action",
    "bank_authority_created",
    "airline_authority_created",
    "action_commit_packet_created_by_human",
    "payment_executed",
    "ticket_issued",
    "booking_created",
    "future_permission_created",
    "real_world_effects_count",
)
PAYMENT_AUTHORIZATION_SNAPSHOT_FIELDS = (
    "authorization_ref_id",
    "transaction_id",
    "created_by",
    "root_owner",
    "bank_root_id",
    "source_payment_receipt_id",
    "source_purchase_intent_id",
    "merchant_ref",
    "offer_id",
    "hold_id",
    "passenger_ref",
    "route_ref",
    "amount",
    "currency",
    "ttl_seconds",
    "expired",
    "idempotency_key",
    "evidence_only",
    "settlement_executed",
    "real_payment_executed",
    "ticket_permission_created",
    "future_permission_created",
    "real_world_effects_count",
)
TICKET_INTENT_SNAPSHOT_FIELDS = (
    "intent_id",
    "transaction_id",
    "created_by",
    "root_owner",
    "airline_root_id",
    "required_offer_packet_id",
    "required_hold_packet_id",
    "required_offer_hold_receipt_id",
    "required_client_purchase_intent_id",
    "required_payment_authorization_ref_id",
    "offer_id",
    "hold_id",
    "passenger_ref",
    "route_ref",
    "amount",
    "currency",
    "merchant_ref",
    "ttl_seconds",
    "expired",
    "idempotency_key",
    "allowed_action",
    "allowed_adapters",
    "forbidden_actions",
    "real_ticket_allowed",
    "real_booking_allowed",
    "real_airline_api_allowed",
    "real_world_effects_allowed",
)
TICKET_RECEIPT_SNAPSHOT_FIELDS = (
    "receipt_id",
    "transaction_id",
    "source_ticket_issue_intent_id",
    "source_idempotency_key",
    "created_by",
    "root_owner",
    "mock_ticket_id",
    "mock_pnr",
    "offer_id",
    "hold_id",
    "passenger_ref",
    "route_ref",
    "amount",
    "currency",
    "evidence_only",
    "real_ticket",
    "real_booking",
    "payment_created",
    "future_ticket_permission_created",
    "future_payment_permission_created",
    "real_world_effects_count",
)
PURCHASE_RECEIPT_SNAPSHOT_FIELDS = (
    "receipt_id",
    "transaction_id",
    "source_client_purchase_intent_id",
    "source_payment_authorization_ref_id",
    "source_mock_ticket_receipt_id",
    "client_root_id",
    "airline_root_id",
    "bank_root_id",
    "created_by",
    "root_owner",
    "evidence_only",
    "side_root_finals_replaced",
    "root_truth_rewritten",
    "future_permission_created",
    "real_payment_executed",
    "real_ticket_issued",
    "real_booking_created",
    "real_world_effects_count",
)
ROOT_FINAL_SNAPSHOT_FIELDS = (
    "final_id",
    "transaction_id",
    "root_owner",
    "created_by",
    "final_status",
    "source_artifact_refs",
    "authority_created_by_ledger",
    "permission_created_by_ledger",
    "real_world_effects_count",
)
SEMANTIC_CLAIM_SNAPSHOT_FIELDS = (
    "client_constraint_set_id",
    "candidate_set_snapshot_id",
    "candidate_set_digest",
    "selection_input_id",
    "proposal_id",
    "canonical_actor_review_ids",
    "synthesis_report_id",
    "canonical_selection_id",
    "causal_binding_report_ref",
    "recommended_offer_id",
)
CLIENT_ROOT_DECISION_SNAPSHOT_FIELDS = (
    "decision_id",
    "transaction_id",
    "client_root_id",
    "source_canonical_selection_id",
    "source_candidate_set_snapshot_id",
    "source_candidate_set_digest",
    "recommended_offer_id",
    "selected_offer_id",
    "decision_status",
    "recommendation_accepted",
    "root_override_used",
    "root_override_reason",
    "semantic_influence_claimed",
    "acceptance_reasons",
    "rejection_reasons",
    "created_by",
    "creates_purchase_permission",
    "creates_payment_permission",
    "creates_ticket_permission",
    "requires_human_approval_before_purchase_intent",
    "authority_transferred",
    "real_world_effects_count",
)
AIRLINE_ROOT_RESOLUTION_SNAPSHOT_FIELDS = (
    "resolution_id",
    "transaction_id",
    "created_by",
    "airline_root_id",
    "source_client_root_decision_ref",
    "source_candidate_set_snapshot_id",
    "source_candidate_set_digest",
    "selected_offer_id",
    "authoritative_offer_ref",
    "resolved_offer_record_ref",
    "resolved_from_same_candidate_snapshot",
    "resolved_amount",
    "resolved_currency",
    "resolved_route_ref",
    "resolved_baggage",
    "resolved_seat_characteristics",
    "resolved_changeability",
    "resolved_ttl",
    "offer_exists",
    "offer_unexpired",
    "airline_offer_validity_pass",
    "client_constraint_compatibility_pass",
    "semantic_values_used_as_authoritative_facts",
    "real_world_effects_count",
)

CANONICAL_SOURCE_SNAPSHOT_FIELDS_BY_ARTIFACT_TYPE: Mapping[str, tuple[str, ...]] = MappingProxyType({
    ledger.ARTIFACT_TRANSACTION_SCOPE: CONTRACT_CONTEXT_SNAPSHOT_FIELDS,
    ledger.ARTIFACT_CLIENT_BSEP_PROJECTION: BSEP_PROJECTION_SNAPSHOT_FIELDS,
    ledger.ARTIFACT_AIRLINE_BSEP_PROJECTION: BSEP_PROJECTION_SNAPSHOT_FIELDS,
    ledger.ARTIFACT_BANK_BSEP_PROJECTION: BSEP_PROJECTION_SNAPSHOT_FIELDS,
    ledger.ARTIFACT_CROSS_ROOT_BSEP_PROJECTION: BSEP_PROJECTION_SNAPSHOT_FIELDS,
    ledger.ARTIFACT_VALIDATED_CANONICAL_SEMANTIC_EVIDENCE: (
        SEMANTIC_CLAIM_SNAPSHOT_FIELDS
    ),
    ledger.ARTIFACT_CLIENT_ROOT_SELECTION_DECISION: (
        CLIENT_ROOT_DECISION_SNAPSHOT_FIELDS
    ),
    ledger.ARTIFACT_AIRLINE_ROOT_OFFER_RESOLUTION: (
        AIRLINE_ROOT_RESOLUTION_SNAPSHOT_FIELDS
    ),
    ledger.ARTIFACT_AIRLINE_OFFER_PACKET: OFFER_PACKET_SNAPSHOT_FIELDS,
    ledger.ARTIFACT_AIRLINE_HOLD_PACKET: HOLD_PACKET_SNAPSHOT_FIELDS,
    ledger.ARTIFACT_AIRLINE_OFFER_HOLD_RECEIPT: HOLD_RECEIPT_SNAPSHOT_FIELDS,
    ledger.ARTIFACT_CLIENT_PURCHASE_INTENT: PURCHASE_INTENT_SNAPSHOT_FIELDS,
    ledger.ARTIFACT_BANK_PAYMENT_AUTHORIZATION: PAYMENT_AUTHORIZATION_SNAPSHOT_FIELDS,
    ledger.ARTIFACT_AIRLINE_TICKET_ISSUE_INTENT: TICKET_INTENT_SNAPSHOT_FIELDS,
    ledger.ARTIFACT_MOCK_TICKET_RECEIPT: TICKET_RECEIPT_SNAPSHOT_FIELDS,
    ledger.ARTIFACT_MOCK_PURCHASE_RECEIPT: PURCHASE_RECEIPT_SNAPSHOT_FIELDS,
    ledger.ARTIFACT_CLIENT_ROOT_FINAL: ROOT_FINAL_SNAPSHOT_FIELDS,
    ledger.ARTIFACT_AIRLINE_ROOT_FINAL: ROOT_FINAL_SNAPSHOT_FIELDS,
    ledger.ARTIFACT_BANK_ROOT_FINAL: ROOT_FINAL_SNAPSHOT_FIELDS,
})
NON_CANONICAL_SOURCE_FIELDS_BY_ARTIFACT_TYPE: Mapping[str, Mapping[str, str]] = MappingProxyType({
    ledger.ARTIFACT_CLIENT_BSEP_PROJECTION: MappingProxyType({
        "raw_secrets_included": "validated source safety flag, not hash input",
        "raw_provider_text_included": "validated source safety flag, not hash input",
    }),
    ledger.ARTIFACT_AIRLINE_BSEP_PROJECTION: MappingProxyType({
        "raw_secrets_included": "validated source safety flag, not hash input",
        "raw_provider_text_included": "validated source safety flag, not hash input",
    }),
    ledger.ARTIFACT_BANK_BSEP_PROJECTION: MappingProxyType({
        "raw_secrets_included": "validated source safety flag, not hash input",
        "raw_provider_text_included": "validated source safety flag, not hash input",
    }),
    ledger.ARTIFACT_CROSS_ROOT_BSEP_PROJECTION: MappingProxyType({
        "raw_secrets_included": "validated source safety flag, not hash input",
        "raw_provider_text_included": "validated source safety flag, not hash input",
    }),
    ledger.ARTIFACT_VALIDATED_CANONICAL_SEMANTIC_EVIDENCE: MappingProxyType({
        "raw_provider_response": "raw provider material is auxiliary only",
        "raw_prompt": "raw prompt material is auxiliary only",
    }),
})


class _FrozenDict(MappingABC):
    __slots__ = ("_data",)

    def __init__(self, value: MappingABC) -> None:
        object.__setattr__(
            self,
            "_data",
            MappingProxyType({
                key: _freeze_json(item)
                for key, item in value.items()
            }),
        )

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __setattr__(self, name: str, value: Any) -> None:
        raise TypeError("frozen mapping cannot be mutated")

    def __repr__(self) -> str:
        return repr(dict(self._data))

    def __deepcopy__(self, memo: dict[int, Any]) -> "_FrozenDict":
        return self

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, MappingABC):
            return dict(self.items()) == dict(other.items())
        return False


def _freeze_json(value: Any) -> Any:
    if isinstance(value, MappingABC):
        return _FrozenDict(value)
    if type(value) is list:
        return tuple(_freeze_json(item) for item in value)
    if type(value) is tuple:
        return tuple(_freeze_json(item) for item in value)
    return value


def _freeze_actor_request(
    request: causal_runtime.AirlineInjectedSemanticActorRequestV01,
) -> causal_runtime.AirlineInjectedSemanticActorRequestV01:
    changes: dict[str, Any] = {}
    for field_name in (
        "client_hard_constraints",
        "client_soft_preferences",
        "authoritative_candidate_projection",
    ):
        value = getattr(request, field_name)
        if isinstance(value, MappingABC) or type(value) is tuple:
            changes[field_name] = _freeze_json(value)
    return replace(request, **changes) if changes else request


@dataclass(frozen=True)
class AirlineTransactionArtifactLedgerBSEPProjectionSourceV01:
    projection_id: str
    projection_ref: str
    bsep_packet_id: str
    transaction_id: str
    side: str
    validation_status: str
    raw_secrets_included: bool
    raw_provider_text_included: bool
    authority_created: bool
    permission_created: bool
    real_world_effects_count: int


@dataclass(frozen=True)
class AirlineTransactionArtifactLedgerRootFinalSourceV01:
    final_id: str
    transaction_id: str
    root_owner: str
    created_by: str
    final_status: str
    source_artifact_refs: tuple[str, ...]
    authority_created_by_ledger: bool
    permission_created_by_ledger: bool
    real_world_effects_count: int


@dataclass(frozen=True)
class AirlineTransactionArtifactLedgerSourceBundleV01:
    source_bundle_id: str
    transaction_id: str
    expected_source_refs: ledger.AirlineTransactionArtifactLedgerExpectedSourceRefsV01
    client_bsep_projection: AirlineTransactionArtifactLedgerBSEPProjectionSourceV01
    airline_bsep_projection: AirlineTransactionArtifactLedgerBSEPProjectionSourceV01
    bank_bsep_projection: AirlineTransactionArtifactLedgerBSEPProjectionSourceV01
    cross_root_bsep_projection: AirlineTransactionArtifactLedgerBSEPProjectionSourceV01
    causal_report: causal_runtime.AirlineSemanticCausalRunReportV01
    offer_packet: corridor_contracts.AirlineOfferPacketV01
    hold_packet: corridor_contracts.AirlineHoldCommitPacketV01
    hold_receipt: corridor_contracts.AirlineOfferHoldReceiptV01
    purchase_approval_evidence: corridor_contracts.AirlinePurchaseApprovalEvidenceRefV01
    purchase_intent: corridor_contracts.ClientPurchaseIntentV01
    payment_authorization_ref: corridor_contracts.BankPaymentAuthorizationRefV01
    ticket_issue_intent: corridor_contracts.AirlineTicketIssueIntentV01
    mock_ticket_receipt: corridor_contracts.MockTicketReceiptV01
    mock_purchase_receipt: corridor_contracts.MockPurchaseReceiptV01
    corridor_report: corridor_runtime.AirlineTicketPurchaseCorridorRunReportV01
    client_root_final: AirlineTransactionArtifactLedgerRootFinalSourceV01
    airline_root_final: AirlineTransactionArtifactLedgerRootFinalSourceV01
    bank_root_final: AirlineTransactionArtifactLedgerRootFinalSourceV01
    source_validation_refs: tuple[str, ...]
    auxiliary_observation_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if isinstance(self.causal_report, causal_runtime.AirlineSemanticCausalRunReportV01):
            causal_changes: dict[str, Any] = {}
            if isinstance(
                self.causal_report.proposer_request,
                causal_runtime.AirlineInjectedSemanticActorRequestV01,
            ):
                causal_changes["proposer_request"] = _freeze_actor_request(
                    self.causal_report.proposer_request,
                )
            if type(self.causal_report.reviewer_request_records) is tuple:
                causal_changes["reviewer_request_records"] = tuple(
                    _freeze_actor_request(request)
                    if isinstance(
                        request,
                        causal_runtime.AirlineInjectedSemanticActorRequestV01,
                    )
                    else request
                    for request in self.causal_report.reviewer_request_records
                )
            if isinstance(self.causal_report.proposer_payload, MappingABC):
                causal_changes["proposer_payload"] = _freeze_json(
                    self.causal_report.proposer_payload,
                )
            if causal_changes:
                object.__setattr__(
                    self,
                    "causal_report",
                    replace(self.causal_report, **causal_changes),
                )
        if isinstance(
            self.corridor_report,
            corridor_runtime.AirlineTicketPurchaseCorridorRunReportV01,
        ):
            corridor_changes: dict[str, Any] = {}
            for field_name in (
                "artifact_validation_summary",
                "root_boundary_summary",
                "receipt_boundary_summary",
                "counter_table",
            ):
                value = getattr(self.corridor_report, field_name)
                if isinstance(value, MappingABC) or type(value) is tuple:
                    corridor_changes[field_name] = _freeze_json(value)
            if corridor_changes:
                object.__setattr__(
                    self,
                    "corridor_report",
                    replace(self.corridor_report, **corridor_changes),
                )


@dataclass(frozen=True)
class AirlineTransactionArtifactLedgerSourceValidationReportV01:
    validation_status: str
    transaction_id: str
    source_bundle_valid: bool
    causal_report_valid: bool
    corridor_report_valid: bool
    bsep_lineage_valid: bool
    artifact_types_valid: bool
    artifact_ids_valid: bool
    transaction_identity_valid: bool
    offer_identity_valid: bool
    hold_identity_valid: bool
    amount_valid: bool
    currency_valid: bool
    route_valid: bool
    passenger_identity_valid: bool
    phase_evidence_refs_valid: bool
    root_finals_valid: bool
    authority_boundaries_valid: bool
    source_refs_valid: bool
    provider_authority_absent: bool
    real_effects_zero: bool
    validation_errors: tuple[str, ...]


def _append_reason(reasons: list[str], reason: str) -> None:
    if reason not in reasons:
        reasons.append(reason)


def _is_non_empty_string(value: Any) -> bool:
    return type(value) is str and bool(value.strip())


def _is_string_tuple(value: Any, *, allow_empty: bool = True) -> bool:
    if type(value) is not tuple:
        return False
    if not allow_empty and not value:
        return False
    return all(_is_non_empty_string(item) for item in value)


def _is_false(value: Any) -> bool:
    return type(value) is bool and value is False


def _is_zero_int(value: Any) -> bool:
    return type(value) is int and value == 0


def _is_int(value: Any) -> bool:
    return type(value) is int


SOURCE_STRING_FIELDS_BY_TYPE: Mapping[type, tuple[str, ...]] = MappingProxyType({
    corridor_contracts.AirlineTicketPurchaseContractContextV01: (
        "transaction_id",
        "offer_id",
        "hold_id",
        "currency",
        "route_ref",
        "passenger_ref",
        "merchant_ref",
    ),
    corridor_contracts.AirlineOfferPacketV01: (
        "packet_id",
        "transaction_id",
        "created_by",
        "root_owner",
        "airline_root_id",
        "offer_id",
        "passenger_ref",
        "route_ref",
        "departure_date",
        "return_date",
        "currency",
        "seat_ref",
    ),
    corridor_contracts.AirlineHoldCommitPacketV01: (
        "packet_id",
        "transaction_id",
        "parent_offer_packet_id",
        "created_by",
        "root_owner",
        "airline_root_id",
        "offer_id",
        "hold_id",
        "passenger_ref",
        "route_ref",
        "currency",
        "idempotency_key",
        "allowed_action",
    ),
    corridor_contracts.AirlineOfferHoldReceiptV01: (
        "receipt_id",
        "transaction_id",
        "source_hold_packet_id",
        "source_idempotency_key",
        "created_by",
        "root_owner",
        "offer_id",
        "hold_id",
        "passenger_ref",
        "route_ref",
        "currency",
    ),
    corridor_contracts.AirlinePurchaseApprovalEvidenceRefV01: (
        "approval_ref",
        "transaction_id",
        "client_root_id",
        "selected_offer_id",
        "currency",
        "passenger_ref",
        "approval_scope",
    ),
    corridor_contracts.ClientPurchaseIntentV01: (
        "intent_id",
        "transaction_id",
        "created_by",
        "root_owner",
        "client_root_id",
        "source_human_approval_ref",
        "selected_offer_packet_id",
        "required_offer_hold_receipt_id",
        "offer_id",
        "hold_id",
        "passenger_ref",
        "route_ref",
        "currency",
        "idempotency_key",
        "allowed_action",
    ),
    corridor_contracts.BankPaymentAuthorizationRefV01: (
        "authorization_ref_id",
        "transaction_id",
        "created_by",
        "root_owner",
        "bank_root_id",
        "source_payment_receipt_id",
        "source_purchase_intent_id",
        "merchant_ref",
        "offer_id",
        "hold_id",
        "passenger_ref",
        "route_ref",
        "currency",
        "idempotency_key",
    ),
    corridor_contracts.AirlineTicketIssueIntentV01: (
        "intent_id",
        "transaction_id",
        "created_by",
        "root_owner",
        "airline_root_id",
        "required_offer_packet_id",
        "required_hold_packet_id",
        "required_offer_hold_receipt_id",
        "required_client_purchase_intent_id",
        "required_payment_authorization_ref_id",
        "offer_id",
        "hold_id",
        "passenger_ref",
        "route_ref",
        "currency",
        "merchant_ref",
        "idempotency_key",
        "allowed_action",
    ),
    corridor_contracts.MockTicketReceiptV01: (
        "receipt_id",
        "transaction_id",
        "source_ticket_issue_intent_id",
        "source_idempotency_key",
        "created_by",
        "root_owner",
        "mock_ticket_id",
        "mock_pnr",
        "offer_id",
        "hold_id",
        "passenger_ref",
        "route_ref",
        "currency",
    ),
    corridor_contracts.MockPurchaseReceiptV01: (
        "receipt_id",
        "transaction_id",
        "source_client_purchase_intent_id",
        "source_payment_authorization_ref_id",
        "source_mock_ticket_receipt_id",
        "client_root_id",
        "airline_root_id",
        "bank_root_id",
        "created_by",
        "root_owner",
    ),
    AirlineTransactionArtifactLedgerBSEPProjectionSourceV01: (
        "projection_id",
        "projection_ref",
        "bsep_packet_id",
        "transaction_id",
        "side",
        "validation_status",
    ),
    AirlineTransactionArtifactLedgerRootFinalSourceV01: (
        "final_id",
        "transaction_id",
        "root_owner",
        "created_by",
        "final_status",
    ),
})

SOURCE_INT_FIELDS_BY_TYPE: Mapping[type, tuple[str, ...]] = MappingProxyType({
    corridor_contracts.AirlineTicketPurchaseContractContextV01: (
        "amount",
        "max_amount",
    ),
    corridor_contracts.AirlineOfferPacketV01: (
        "amount",
        "ttl_seconds",
        "real_world_effects_count",
    ),
    corridor_contracts.AirlineHoldCommitPacketV01: (
        "amount",
        "ttl_seconds",
    ),
    corridor_contracts.AirlineOfferHoldReceiptV01: (
        "amount",
        "real_world_effects_count",
    ),
    corridor_contracts.AirlinePurchaseApprovalEvidenceRefV01: (
        "max_amount",
        "real_world_effects_count",
    ),
    corridor_contracts.ClientPurchaseIntentV01: (
        "max_amount",
        "selected_amount",
        "ttl_seconds",
        "real_world_effects_count",
    ),
    corridor_contracts.BankPaymentAuthorizationRefV01: (
        "amount",
        "ttl_seconds",
        "real_world_effects_count",
    ),
    corridor_contracts.AirlineTicketIssueIntentV01: (
        "amount",
        "ttl_seconds",
    ),
    corridor_contracts.MockTicketReceiptV01: (
        "amount",
        "real_world_effects_count",
    ),
    corridor_contracts.MockPurchaseReceiptV01: ("real_world_effects_count",),
    AirlineTransactionArtifactLedgerBSEPProjectionSourceV01: (
        "real_world_effects_count",
    ),
    AirlineTransactionArtifactLedgerRootFinalSourceV01: (
        "real_world_effects_count",
    ),
})

SOURCE_BOOL_FIELDS_BY_TYPE: Mapping[type, tuple[str, ...]] = MappingProxyType({
    corridor_contracts.AirlineOfferPacketV01: (
        "baggage_included",
        "expired",
        "evidence_only",
        "purchase_permission_created",
        "payment_permission_created",
        "ticket_permission_created",
    ),
    corridor_contracts.AirlineHoldCommitPacketV01: (
        "expired",
        "real_world_effects_allowed",
    ),
    corridor_contracts.AirlineOfferHoldReceiptV01: (
        "evidence_only",
        "purchase_permission_created",
        "payment_permission_created",
        "ticket_permission_created",
        "future_permission_created",
    ),
    corridor_contracts.AirlinePurchaseApprovalEvidenceRefV01: (
        "evidence_only",
        "creates_client_purchase_intent",
        "creates_action_commit_packet",
        "creates_receipt",
        "creates_payment_authorization",
        "creates_ticket",
        "creates_booking",
        "creates_future_permission",
    ),
    corridor_contracts.ClientPurchaseIntentV01: (
        "expired",
        "bank_authority_created",
        "airline_authority_created",
        "action_commit_packet_created_by_human",
        "payment_executed",
        "ticket_issued",
        "booking_created",
        "future_permission_created",
    ),
    corridor_contracts.BankPaymentAuthorizationRefV01: (
        "expired",
        "evidence_only",
        "settlement_executed",
        "real_payment_executed",
        "ticket_permission_created",
        "future_permission_created",
    ),
    corridor_contracts.AirlineTicketIssueIntentV01: (
        "expired",
        "real_ticket_allowed",
        "real_booking_allowed",
        "real_airline_api_allowed",
        "real_world_effects_allowed",
    ),
    corridor_contracts.MockTicketReceiptV01: (
        "evidence_only",
        "real_ticket",
        "real_booking",
        "payment_created",
        "future_ticket_permission_created",
        "future_payment_permission_created",
    ),
    corridor_contracts.MockPurchaseReceiptV01: (
        "evidence_only",
        "side_root_finals_replaced",
        "root_truth_rewritten",
        "future_permission_created",
        "real_payment_executed",
        "real_ticket_issued",
        "real_booking_created",
    ),
    AirlineTransactionArtifactLedgerBSEPProjectionSourceV01: (
        "raw_secrets_included",
        "raw_provider_text_included",
        "authority_created",
        "permission_created",
    ),
    AirlineTransactionArtifactLedgerRootFinalSourceV01: (
        "authority_created_by_ledger",
        "permission_created_by_ledger",
    ),
})

SOURCE_TUPLE_STRING_FIELDS_BY_TYPE: Mapping[type, tuple[str, ...]] = MappingProxyType({
    corridor_contracts.AirlineHoldCommitPacketV01: (
        "allowed_adapters",
        "forbidden_actions",
    ),
    corridor_contracts.AirlineTicketIssueIntentV01: (
        "allowed_adapters",
        "forbidden_actions",
    ),
    AirlineTransactionArtifactLedgerRootFinalSourceV01: ("source_artifact_refs",),
})


def _source_run_ref(source_bundle_id: str) -> str:
    return f"source_run:{source_bundle_id}"


def _source_causal_report_ref(
    report: causal_runtime.AirlineSemanticCausalRunReportV01,
) -> str:
    return f"source_causal_report:{report.run_id}:{report.scenario_id}"


def _source_corridor_report_ref(
    report: corridor_runtime.AirlineTicketPurchaseCorridorRunReportV01,
) -> str:
    return f"source_corridor_report:{report.run_id}:{report.transaction_id}"


def _source_refs_profile(
    source_bundle: "AirlineTransactionArtifactLedgerSourceBundleV01",
) -> tuple[str, str, str]:
    return (
        _source_run_ref(source_bundle.source_bundle_id),
        _source_causal_report_ref(source_bundle.causal_report),
        _source_corridor_report_ref(source_bundle.corridor_report),
    )


def _source_report(
    *,
    transaction_id: Any,
    reasons: tuple[str, ...],
) -> AirlineTransactionArtifactLedgerSourceValidationReportV01:
    reason_set = set(reasons)
    return AirlineTransactionArtifactLedgerSourceValidationReportV01(
        validation_status=STATUS_PASS if not reasons else STATUS_FAIL_CLOSED,
        transaction_id=transaction_id if type(transaction_id) is str else "",
        source_bundle_valid=REASON_SOURCE_BUNDLE_WRONG_TYPE not in reason_set,
        causal_report_valid=REASON_SOURCE_CAUSAL_REPORT_INVALID not in reason_set,
        corridor_report_valid=(
            REASON_SOURCE_CORRIDOR_REPORT_INVALID not in reason_set
        ),
        bsep_lineage_valid=not reason_set.intersection(
            {
                REASON_SOURCE_BSEP_PROJECTION_MISSING,
                REASON_SOURCE_BSEP_LINEAGE_MISMATCH,
            },
        ),
        artifact_types_valid=not reason_set.intersection(
            {REASON_SOURCE_ARTIFACT_MISSING, REASON_SOURCE_ARTIFACT_WRONG_TYPE},
        ),
        artifact_ids_valid=REASON_SOURCE_ARTIFACT_ID_MISMATCH not in reason_set,
        transaction_identity_valid=not reason_set.intersection(
            {
                REASON_SOURCE_BUNDLE_TRANSACTION_MISMATCH,
                REASON_SOURCE_ARTIFACT_ID_MISMATCH,
            },
        ),
        offer_identity_valid=REASON_SOURCE_ARTIFACT_OFFER_MISMATCH not in reason_set,
        hold_identity_valid=REASON_SOURCE_ARTIFACT_HOLD_MISMATCH not in reason_set,
        amount_valid=REASON_SOURCE_ARTIFACT_AMOUNT_MISMATCH not in reason_set,
        currency_valid=REASON_SOURCE_ARTIFACT_CURRENCY_MISMATCH not in reason_set,
        route_valid=REASON_SOURCE_ARTIFACT_ROUTE_MISMATCH not in reason_set,
        passenger_identity_valid=(
            REASON_SOURCE_ARTIFACT_PASSENGER_MISMATCH not in reason_set
        ),
        phase_evidence_refs_valid=(
            REASON_SOURCE_PHASE_EVIDENCE_REF_MISMATCH not in reason_set
        ),
        root_finals_valid=not reason_set.intersection(
            {
                REASON_SOURCE_ROOT_FINAL_MISSING,
                REASON_SOURCE_ROOT_FINAL_WRONG_OWNER,
                REASON_SOURCE_SHARED_SUMMARY_USED_AS_ROOT_FINAL,
            },
        ),
        authority_boundaries_valid=not reason_set.intersection(
            {
                REASON_SOURCE_PROVIDER_AUTHORITY_DETECTED,
                REASON_SOURCE_REAL_EFFECT_DETECTED,
            },
        ),
        source_refs_valid=REASON_SOURCE_REF_MISMATCH not in reason_set,
        provider_authority_absent=(
            REASON_SOURCE_PROVIDER_AUTHORITY_DETECTED not in reason_set
        ),
        real_effects_zero=REASON_SOURCE_REAL_EFFECT_DETECTED not in reason_set,
        validation_errors=reasons,
    )


def _causal_report_shape_valid(value: Any) -> bool:
    return (
        isinstance(value, causal_runtime.AirlineSemanticCausalRunReportV01)
        and type(value.provider_call_records) is tuple
        and all(
            isinstance(
                record,
                causal_runtime.AirlineSemanticProviderCallRecordV01,
            )
            for record in value.provider_call_records
        )
        and _actor_request_shape_valid(value.proposer_request)
        and type(value.reviewer_request_records) is tuple
        and all(
            _actor_request_shape_valid(request)
            for request in value.reviewer_request_records
        )
        and type(value.reviewer_responses) is tuple
        and all(
            isinstance(
                response,
                causal_runtime.AirlineInjectedReviewerResponseV01,
            )
            for response in value.reviewer_responses
        )
        and type(value.actor_reviews) is tuple
        and all(
            isinstance(
                review,
                binding.AirlineCanonicalActorSelectionReviewV01,
            )
            for review in value.actor_reviews
        )
        and isinstance(value.proposal, binding.AirlineSemanticOfferSelectionProposalV01)
        and isinstance(value.synthesis, binding.AirlineSemanticSelectionSynthesisReportV01)
        and isinstance(
            value.canonical_evidence,
            binding.ValidatedAirlineSemanticSelectionEvidenceV01,
        )
        and isinstance(
            value.client_root_decision,
            binding.ClientRootOfferSelectionDecisionV01,
        )
        and isinstance(
            value.airline_root_resolution,
            binding.AirlineRootSelectedOfferResolutionV01,
        )
        and isinstance(value.hold_packet, corridor_contracts.AirlineHoldCommitPacketV01)
        and isinstance(
            value.hold_binding,
            binding.AirlineSemanticHoldContractBindingV01,
        )
        and isinstance(
            value.causal_binding_report,
            binding.AirlineSemanticToContractBindingReportV01,
        )
        and isinstance(
            value.local_chain_validation,
            binding.AirlineSemanticToContractValidationReportV01,
        )
    )


def _corridor_report_shape_valid(value: Any) -> bool:
    if not isinstance(value, corridor_runtime.AirlineTicketPurchaseCorridorRunReportV01):
        return False
    if not isinstance(
        value.contract_context,
        corridor_contracts.AirlineTicketPurchaseContractContextV01,
    ):
        return False
    if type(value.phase_results) is not tuple or any(
        not isinstance(phase, corridor_runtime.AirlineCorridorPhaseResultV01)
        for phase in value.phase_results
    ):
        return False
    if type(value.transitions) is not tuple or any(
        not isinstance(
            transition,
            corridor_runtime.AirlineCorridorTransitionV01,
        )
        for transition in value.transitions
    ):
        return False
    if type(value.core_domain_delegation_matrix) is not tuple or any(
        not isinstance(row, corridor_runtime.AirlineCoreDelegationRowV01)
        for row in value.core_domain_delegation_matrix
    ):
        return False
    if not isinstance(value.artifact_validation_summary, MappingABC):
        return False
    if type(value.root_boundary_summary) is not tuple or any(
        not isinstance(item, MappingABC)
        for item in value.root_boundary_summary
    ):
        return False
    if not isinstance(value.receipt_boundary_summary, MappingABC):
        return False
    if not isinstance(value.counter_table, MappingABC):
        return False
    if not _is_string_tuple(value.validation_errors):
        return False
    return True


def _expected_source_refs_valid(value: Any) -> bool:
    return (
        isinstance(
            value,
            ledger.AirlineTransactionArtifactLedgerExpectedSourceRefsV01,
        )
        and _is_non_empty_string(value.source_run_ref)
        and _is_non_empty_string(value.source_causal_report_ref)
        and _is_non_empty_string(value.source_corridor_report_ref)
    )


def _actor_request_shape_valid(value: Any) -> bool:
    return (
        isinstance(value, causal_runtime.AirlineInjectedSemanticActorRequestV01)
        and isinstance(value.client_hard_constraints, MappingABC)
        and isinstance(value.client_soft_preferences, MappingABC)
        and type(value.authoritative_candidate_projection) is tuple
        and all(
            isinstance(item, MappingABC)
            for item in value.authoritative_candidate_projection
        )
    )


def _projection_errors(
    projection: Any,
    *,
    side: str,
    transaction_id: str,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if not isinstance(
        projection,
        AirlineTransactionArtifactLedgerBSEPProjectionSourceV01,
    ):
        return (REASON_SOURCE_BSEP_PROJECTION_MISSING,)
    if (
        not _is_non_empty_string(projection.projection_id)
        or not _is_non_empty_string(projection.projection_ref)
        or not _is_non_empty_string(projection.bsep_packet_id)
        or projection.side != side
        or projection.transaction_id != transaction_id
        or projection.validation_status != STATUS_PASS
    ):
        _append_reason(reasons, REASON_SOURCE_BSEP_LINEAGE_MISMATCH)
    if (
        not _is_false(projection.raw_secrets_included)
        or not _is_false(projection.raw_provider_text_included)
        or not _is_false(projection.authority_created)
        or not _is_false(projection.permission_created)
    ):
        _append_reason(reasons, REASON_SOURCE_PROVIDER_AUTHORITY_DETECTED)
    if not _is_zero_int(projection.real_world_effects_count):
        _append_reason(reasons, REASON_SOURCE_REAL_EFFECT_DETECTED)
    return tuple(reasons)


def _source_artifact_type_errors(
    source_bundle: AirlineTransactionArtifactLedgerSourceBundleV01,
) -> tuple[str, ...]:
    reasons: list[str] = []
    expected = (
        ("offer_packet", corridor_contracts.AirlineOfferPacketV01),
        ("hold_packet", corridor_contracts.AirlineHoldCommitPacketV01),
        ("hold_receipt", corridor_contracts.AirlineOfferHoldReceiptV01),
        (
            "purchase_approval_evidence",
            corridor_contracts.AirlinePurchaseApprovalEvidenceRefV01,
        ),
        ("purchase_intent", corridor_contracts.ClientPurchaseIntentV01),
        (
            "payment_authorization_ref",
            corridor_contracts.BankPaymentAuthorizationRefV01,
        ),
        ("ticket_issue_intent", corridor_contracts.AirlineTicketIssueIntentV01),
        ("mock_ticket_receipt", corridor_contracts.MockTicketReceiptV01),
        ("mock_purchase_receipt", corridor_contracts.MockPurchaseReceiptV01),
    )
    for field_name, expected_type in expected:
        value = getattr(source_bundle, field_name)
        if value is None:
            _append_reason(reasons, REASON_SOURCE_ARTIFACT_MISSING)
        elif not isinstance(value, expected_type):
            _append_reason(reasons, REASON_SOURCE_ARTIFACT_WRONG_TYPE)
    return tuple(reasons)


def _source_object_shape_valid(value: Any) -> bool:
    value_type = type(value)
    for field_name in SOURCE_STRING_FIELDS_BY_TYPE.get(value_type, ()):
        if not _is_non_empty_string(getattr(value, field_name, None)):
            return False
    for field_name in SOURCE_INT_FIELDS_BY_TYPE.get(value_type, ()):
        if not _is_int(getattr(value, field_name, None)):
            return False
    for field_name in SOURCE_BOOL_FIELDS_BY_TYPE.get(value_type, ()):
        if type(getattr(value, field_name, None)) is not bool:
            return False
    for field_name in SOURCE_TUPLE_STRING_FIELDS_BY_TYPE.get(value_type, ()):
        if not _is_string_tuple(getattr(value, field_name, None)):
            return False
    return True


def _source_artifact_shape_errors(
    source_bundle: AirlineTransactionArtifactLedgerSourceBundleV01,
) -> tuple[str, ...]:
    source_objects = (
        source_bundle.corridor_report.contract_context,
        source_bundle.client_bsep_projection,
        source_bundle.airline_bsep_projection,
        source_bundle.bank_bsep_projection,
        source_bundle.cross_root_bsep_projection,
        source_bundle.offer_packet,
        source_bundle.hold_packet,
        source_bundle.hold_receipt,
        source_bundle.purchase_approval_evidence,
        source_bundle.purchase_intent,
        source_bundle.payment_authorization_ref,
        source_bundle.ticket_issue_intent,
        source_bundle.mock_ticket_receipt,
        source_bundle.mock_purchase_receipt,
        source_bundle.client_root_final,
        source_bundle.airline_root_final,
        source_bundle.bank_root_final,
    )
    if any(not _source_object_shape_valid(item) for item in source_objects):
        return (REASON_SOURCE_ARTIFACT_WRONG_TYPE,)
    return ()


def _safe_contract_report(
    factory: Any,
) -> corridor_contracts.AirlineCorridorValidationReportV01 | None:
    try:
        return factory()
    except (TypeError, AttributeError, ValueError):
        return None


def _contract_report_errors(
    source_bundle: AirlineTransactionArtifactLedgerSourceBundleV01,
) -> tuple[str, ...]:
    reasons: list[str] = []
    context = source_bundle.corridor_report.contract_context
    reports = (
        lambda: corridor_contracts.validate_airline_offer_packet_v01(
            source_bundle.offer_packet,
            contract_context=context,
        ),
        lambda: corridor_contracts.validate_airline_hold_commit_packet_v01(
            source_bundle.offer_packet,
            source_bundle.hold_packet,
            contract_context=context,
        ),
        lambda: corridor_contracts.validate_airline_offer_hold_receipt_v01(
            source_bundle.hold_packet,
            source_bundle.hold_receipt,
        ),
        lambda: corridor_contracts.validate_human_approval_evidence_ref_v01(
            source_bundle.purchase_approval_evidence,
            contract_context=context,
        ),
        lambda: corridor_contracts.validate_client_purchase_intent_v01(
            source_bundle.purchase_approval_evidence,
            source_bundle.offer_packet,
            source_bundle.hold_receipt,
            source_bundle.purchase_intent,
            contract_context=context,
        ),
        lambda: corridor_contracts.validate_bank_payment_authorization_ref_v01(
            source_bundle.purchase_intent,
            source_bundle.payment_authorization_ref,
            contract_context=context,
        ),
        lambda: corridor_contracts.validate_airline_ticket_issue_intent_v01(
            source_bundle.offer_packet,
            source_bundle.hold_packet,
            source_bundle.hold_receipt,
            source_bundle.purchase_intent,
            source_bundle.payment_authorization_ref,
            source_bundle.ticket_issue_intent,
            contract_context=context,
        ),
        lambda: corridor_contracts.validate_mock_ticket_receipt_v01(
            source_bundle.ticket_issue_intent,
            source_bundle.mock_ticket_receipt,
            contract_context=context,
        ),
        lambda: corridor_contracts.validate_mock_purchase_receipt_v01(
            source_bundle.purchase_intent,
            source_bundle.payment_authorization_ref,
            source_bundle.mock_ticket_receipt,
            source_bundle.mock_purchase_receipt,
        ),
    )
    for factory in reports:
        report = _safe_contract_report(factory)
        if report is None:
            _append_reason(reasons, REASON_SOURCE_ARTIFACT_WRONG_TYPE)
            continue
        if report.validation_status == corridor_contracts.PASS:
            continue
        for reason in report.reason_codes:
            if reason == corridor_contracts.REASON_SELECTED_OFFER_MISMATCH:
                _append_reason(reasons, REASON_SOURCE_ARTIFACT_OFFER_MISMATCH)
            elif reason == corridor_contracts.REASON_HOLD_ID_MISMATCH:
                _append_reason(reasons, REASON_SOURCE_ARTIFACT_HOLD_MISMATCH)
            elif reason in {
                corridor_contracts.REASON_AMOUNT_MISMATCH,
                corridor_contracts.REASON_AMOUNT_EXCEEDS_HUMAN_APPROVAL,
            }:
                _append_reason(reasons, REASON_SOURCE_ARTIFACT_AMOUNT_MISMATCH)
            elif reason == corridor_contracts.REASON_CURRENCY_MISMATCH:
                _append_reason(reasons, REASON_SOURCE_ARTIFACT_CURRENCY_MISMATCH)
            elif reason == corridor_contracts.REASON_ROUTE_REF_MISMATCH:
                _append_reason(reasons, REASON_SOURCE_ARTIFACT_ROUTE_MISMATCH)
            elif reason == corridor_contracts.REASON_PASSENGER_REF_MISMATCH:
                _append_reason(reasons, REASON_SOURCE_ARTIFACT_PASSENGER_MISMATCH)
            elif reason == corridor_contracts.REASON_NONZERO_REAL_WORLD_EFFECTS:
                _append_reason(reasons, REASON_SOURCE_REAL_EFFECT_DETECTED)
            elif reason in {
                corridor_contracts.REASON_CROSS_ROOT_AUTHORITY_TRANSFER,
                corridor_contracts.REASON_RECEIPT_CREATED_PERMISSION,
                corridor_contracts.REASON_RECEIPT_CREATED_FUTURE_PERMISSION,
            }:
                _append_reason(reasons, REASON_SOURCE_PROVIDER_AUTHORITY_DETECTED)
            else:
                _append_reason(reasons, REASON_SOURCE_ARTIFACT_ID_MISMATCH)
    return tuple(reasons)


def _values_all_equal(values: tuple[Any, ...]) -> bool:
    if not values:
        return False
    first = values[0]
    return all(value == first for value in values)


def _identity_errors(
    source_bundle: AirlineTransactionArtifactLedgerSourceBundleV01,
) -> tuple[str, ...]:
    reasons: list[str] = []
    causal_report = source_bundle.causal_report
    context = source_bundle.corridor_report.contract_context
    transaction_values = (
        source_bundle.transaction_id,
        causal_report.transaction_id,
        context.transaction_id,
        source_bundle.offer_packet.transaction_id,
        source_bundle.hold_packet.transaction_id,
        source_bundle.hold_receipt.transaction_id,
        source_bundle.purchase_approval_evidence.transaction_id,
        source_bundle.purchase_intent.transaction_id,
        source_bundle.payment_authorization_ref.transaction_id,
        source_bundle.ticket_issue_intent.transaction_id,
        source_bundle.mock_ticket_receipt.transaction_id,
        source_bundle.mock_purchase_receipt.transaction_id,
    )
    if not _values_all_equal(transaction_values) or transaction_values[0] != ledger.TRANSACTION_ID:
        _append_reason(reasons, REASON_SOURCE_BUNDLE_TRANSACTION_MISMATCH)

    offer_values = (
        causal_report.semantic_recommendation_id,
        causal_report.root_selected_offer_id,
        causal_report.hold_contract_offer_id,
        causal_report.proposal.recommended_offer_id if causal_report.proposal else "",
        causal_report.client_root_decision.selected_offer_id
        if causal_report.client_root_decision
        else "",
        causal_report.airline_root_resolution.selected_offer_id
        if causal_report.airline_root_resolution
        else "",
        context.offer_id,
        source_bundle.offer_packet.offer_id,
        source_bundle.hold_packet.offer_id,
        source_bundle.hold_receipt.offer_id,
        source_bundle.purchase_approval_evidence.selected_offer_id,
        source_bundle.purchase_intent.offer_id,
        source_bundle.payment_authorization_ref.offer_id,
        source_bundle.ticket_issue_intent.offer_id,
        source_bundle.mock_ticket_receipt.offer_id,
    )
    if (
        not _values_all_equal(offer_values)
        or offer_values[0] not in ledger.VALID_LEDGER_OFFER_IDS
    ):
        _append_reason(reasons, REASON_SOURCE_ARTIFACT_OFFER_MISMATCH)

    hold_values = (
        causal_report.hold_packet.hold_id if causal_report.hold_packet else "",
        context.hold_id,
        source_bundle.hold_packet.hold_id,
        source_bundle.hold_receipt.hold_id,
        source_bundle.purchase_intent.hold_id,
        source_bundle.payment_authorization_ref.hold_id,
        source_bundle.ticket_issue_intent.hold_id,
        source_bundle.mock_ticket_receipt.hold_id,
    )
    if not _values_all_equal(hold_values):
        _append_reason(reasons, REASON_SOURCE_ARTIFACT_HOLD_MISMATCH)

    amount_values = (
        causal_report.airline_root_resolution.resolved_amount
        if causal_report.airline_root_resolution
        else None,
        context.amount,
        source_bundle.offer_packet.amount,
        source_bundle.hold_packet.amount,
        source_bundle.hold_receipt.amount,
        source_bundle.purchase_intent.selected_amount,
        source_bundle.payment_authorization_ref.amount,
        source_bundle.ticket_issue_intent.amount,
        source_bundle.mock_ticket_receipt.amount,
    )
    if not _values_all_equal(amount_values):
        _append_reason(reasons, REASON_SOURCE_ARTIFACT_AMOUNT_MISMATCH)

    currency_values = (
        causal_report.airline_root_resolution.resolved_currency
        if causal_report.airline_root_resolution
        else None,
        context.currency,
        source_bundle.offer_packet.currency,
        source_bundle.hold_packet.currency,
        source_bundle.hold_receipt.currency,
        source_bundle.purchase_approval_evidence.currency,
        source_bundle.purchase_intent.currency,
        source_bundle.payment_authorization_ref.currency,
        source_bundle.ticket_issue_intent.currency,
        source_bundle.mock_ticket_receipt.currency,
    )
    if not _values_all_equal(currency_values):
        _append_reason(reasons, REASON_SOURCE_ARTIFACT_CURRENCY_MISMATCH)

    route_values = (
        causal_report.airline_root_resolution.resolved_route_ref
        if causal_report.airline_root_resolution
        else None,
        context.route_ref,
        source_bundle.offer_packet.route_ref,
        source_bundle.hold_packet.route_ref,
        source_bundle.hold_receipt.route_ref,
        source_bundle.purchase_intent.route_ref,
        source_bundle.payment_authorization_ref.route_ref,
        source_bundle.ticket_issue_intent.route_ref,
        source_bundle.mock_ticket_receipt.route_ref,
    )
    if not _values_all_equal(route_values):
        _append_reason(reasons, REASON_SOURCE_ARTIFACT_ROUTE_MISMATCH)

    passenger_values = (
        context.passenger_ref,
        source_bundle.offer_packet.passenger_ref,
        source_bundle.hold_packet.passenger_ref,
        source_bundle.hold_receipt.passenger_ref,
        source_bundle.purchase_approval_evidence.passenger_ref,
        source_bundle.purchase_intent.passenger_ref,
        source_bundle.payment_authorization_ref.passenger_ref,
        source_bundle.ticket_issue_intent.passenger_ref,
        source_bundle.mock_ticket_receipt.passenger_ref,
    )
    if not _values_all_equal(passenger_values):
        _append_reason(reasons, REASON_SOURCE_ARTIFACT_PASSENGER_MISMATCH)

    if (
        causal_report.hold_packet != source_bundle.hold_packet
        or not causal_report.hold_binding
        or causal_report.hold_binding.hold_packet_id
        != source_bundle.hold_packet.packet_id
        or not causal_report.causal_binding_report
        or causal_report.causal_binding_report.hold_packet_ref
        != source_bundle.hold_packet.packet_id
    ):
        _append_reason(reasons, REASON_SOURCE_ARTIFACT_HOLD_MISMATCH)

    id_pairs = (
        (source_bundle.hold_packet.parent_offer_packet_id, source_bundle.offer_packet.packet_id),
        (source_bundle.hold_receipt.source_hold_packet_id, source_bundle.hold_packet.packet_id),
        (
            source_bundle.purchase_intent.selected_offer_packet_id,
            source_bundle.offer_packet.packet_id,
        ),
        (
            source_bundle.purchase_intent.required_offer_hold_receipt_id,
            source_bundle.hold_receipt.receipt_id,
        ),
        (
            source_bundle.purchase_intent.source_human_approval_ref,
            source_bundle.purchase_approval_evidence.approval_ref,
        ),
        (
            source_bundle.payment_authorization_ref.source_purchase_intent_id,
            source_bundle.purchase_intent.intent_id,
        ),
        (
            source_bundle.ticket_issue_intent.required_offer_packet_id,
            source_bundle.offer_packet.packet_id,
        ),
        (
            source_bundle.ticket_issue_intent.required_hold_packet_id,
            source_bundle.hold_packet.packet_id,
        ),
        (
            source_bundle.ticket_issue_intent.required_offer_hold_receipt_id,
            source_bundle.hold_receipt.receipt_id,
        ),
        (
            source_bundle.ticket_issue_intent.required_client_purchase_intent_id,
            source_bundle.purchase_intent.intent_id,
        ),
        (
            source_bundle.ticket_issue_intent.required_payment_authorization_ref_id,
            source_bundle.payment_authorization_ref.authorization_ref_id,
        ),
        (
            source_bundle.mock_ticket_receipt.source_ticket_issue_intent_id,
            source_bundle.ticket_issue_intent.intent_id,
        ),
        (
            source_bundle.mock_purchase_receipt.source_client_purchase_intent_id,
            source_bundle.purchase_intent.intent_id,
        ),
        (
            source_bundle.mock_purchase_receipt.source_payment_authorization_ref_id,
            source_bundle.payment_authorization_ref.authorization_ref_id,
        ),
        (
            source_bundle.mock_purchase_receipt.source_mock_ticket_receipt_id,
            source_bundle.mock_ticket_receipt.receipt_id,
        ),
    )
    if any(left != right for left, right in id_pairs):
        _append_reason(reasons, REASON_SOURCE_ARTIFACT_ID_MISMATCH)

    return tuple(reasons)


def _bsep_lineage_errors(
    source_bundle: AirlineTransactionArtifactLedgerSourceBundleV01,
) -> tuple[str, ...]:
    reasons: list[str] = []
    projections = (
        source_bundle.client_bsep_projection,
        source_bundle.airline_bsep_projection,
        source_bundle.bank_bsep_projection,
        source_bundle.cross_root_bsep_projection,
    )
    for projection, side in zip(
        projections,
        (SIDE_CLIENT, SIDE_AIRLINE, SIDE_BANK, SIDE_CROSS_ROOT_ADVISORY),
    ):
        for reason in _projection_errors(
            projection,
            side=side,
            transaction_id=source_bundle.transaction_id,
        ):
            _append_reason(reasons, reason)
    if all(
        isinstance(
            projection,
            AirlineTransactionArtifactLedgerBSEPProjectionSourceV01,
        )
        for projection in projections
    ) and all(
        _source_object_shape_valid(projection)
        for projection in projections
    ):
        packet_ids = tuple(projection.bsep_packet_id for projection in projections)
        if len(set(packet_ids)) != 1:
            _append_reason(reasons, REASON_SOURCE_BSEP_LINEAGE_MISMATCH)
        causal_report = source_bundle.causal_report
        if isinstance(causal_report, causal_runtime.AirlineSemanticCausalRunReportV01):
            proposer_request = causal_report.proposer_request
            proposal = causal_report.proposal
            causal_refs = (
                proposer_request.source_bsep_projection_ref
                if isinstance(
                    proposer_request,
                    causal_runtime.AirlineInjectedSemanticActorRequestV01,
                )
                else "",
                proposal.source_bsep_projection_ref
                if isinstance(
                    proposal,
                    binding.AirlineSemanticOfferSelectionProposalV01,
                )
                else "",
            )
            if any(
                ref != source_bundle.airline_bsep_projection.projection_ref
                for ref in causal_refs
            ):
                _append_reason(reasons, REASON_SOURCE_BSEP_LINEAGE_MISMATCH)
    return tuple(reasons)


def _phase_evidence_errors(
    source_bundle: AirlineTransactionArtifactLedgerSourceBundleV01,
) -> tuple[str, ...]:
    expected = {
        corridor_runtime.PHASE_AIRLINE_OFFER_HOLD: (
            source_bundle.offer_packet.packet_id,
            source_bundle.hold_packet.packet_id,
            source_bundle.hold_receipt.receipt_id,
        ),
        corridor_runtime.PHASE_CLIENT_PURCHASE_INTENT: (
            source_bundle.purchase_approval_evidence.approval_ref,
            source_bundle.purchase_intent.intent_id,
        ),
        corridor_runtime.PHASE_BANK_PAYMENT_AUTHORIZATION: (
            source_bundle.payment_authorization_ref.authorization_ref_id,
        ),
        corridor_runtime.PHASE_AIRLINE_TICKET_ISSUE: (
            source_bundle.ticket_issue_intent.intent_id,
            source_bundle.mock_ticket_receipt.receipt_id,
        ),
        corridor_runtime.PHASE_CLIENT_COMPLETION: (
            source_bundle.mock_purchase_receipt.receipt_id,
        ),
    }
    phase_results = source_bundle.corridor_report.phase_results
    if (
        type(phase_results) is not tuple
        or len(phase_results) != 5
        or tuple(phase.phase_id for phase in phase_results)
        != corridor_runtime.PHASE_ORDER
    ):
        return (REASON_SOURCE_PHASE_EVIDENCE_REF_MISMATCH,)
    for phase in phase_results:
        if (
            phase.phase_status != STATUS_PASS
            or phase.evidence_refs_observed != expected.get(phase.phase_id)
        ):
            return (REASON_SOURCE_PHASE_EVIDENCE_REF_MISMATCH,)
    if source_bundle.corridor_report.counter_table.get("corridor_run_count") != 1:
        return (REASON_SOURCE_PHASE_EVIDENCE_REF_MISMATCH,)
    return ()


def _expected_root_final_source_refs(
    source_bundle: AirlineTransactionArtifactLedgerSourceBundleV01,
) -> MappingABC | None:
    if (
        not _causal_report_shape_valid(source_bundle.causal_report)
        or not isinstance(
            source_bundle.purchase_intent,
            corridor_contracts.ClientPurchaseIntentV01,
        )
        or not isinstance(
            source_bundle.mock_purchase_receipt,
            corridor_contracts.MockPurchaseReceiptV01,
        )
        or not isinstance(
            source_bundle.offer_packet,
            corridor_contracts.AirlineOfferPacketV01,
        )
        or not isinstance(
            source_bundle.hold_packet,
            corridor_contracts.AirlineHoldCommitPacketV01,
        )
        or not isinstance(
            source_bundle.ticket_issue_intent,
            corridor_contracts.AirlineTicketIssueIntentV01,
        )
        or not isinstance(
            source_bundle.mock_ticket_receipt,
            corridor_contracts.MockTicketReceiptV01,
        )
        or not isinstance(
            source_bundle.payment_authorization_ref,
            corridor_contracts.BankPaymentAuthorizationRefV01,
        )
    ):
        return None
    return {
        ledger.CLIENT_ROOT_ID: (
            source_bundle.causal_report.client_root_decision.decision_id,
            source_bundle.purchase_intent.intent_id,
            source_bundle.mock_purchase_receipt.receipt_id,
        ),
        ledger.AIRLINE_ROOT_ID: (
            source_bundle.causal_report.airline_root_resolution.resolution_id,
            source_bundle.offer_packet.packet_id,
            source_bundle.hold_packet.packet_id,
            source_bundle.ticket_issue_intent.intent_id,
            source_bundle.mock_ticket_receipt.receipt_id,
        ),
        ledger.BANK_ROOT_ID: (
            source_bundle.payment_authorization_ref.authorization_ref_id,
        ),
    }


def _root_final_errors(
    source_bundle: AirlineTransactionArtifactLedgerSourceBundleV01,
) -> tuple[str, ...]:
    reasons: list[str] = []
    expected_refs_by_root = _expected_root_final_source_refs(source_bundle)
    expected = (
        (source_bundle.client_root_final, ledger.CLIENT_ROOT_ID),
        (source_bundle.airline_root_final, ledger.AIRLINE_ROOT_ID),
        (source_bundle.bank_root_final, ledger.BANK_ROOT_ID),
    )
    for root_final, root_owner in expected:
        if not isinstance(root_final, AirlineTransactionArtifactLedgerRootFinalSourceV01):
            _append_reason(reasons, REASON_SOURCE_ROOT_FINAL_MISSING)
            continue
        if root_final.root_owner == ledger.ROOT_OWNER_BSEP_CROSS_ROOT:
            _append_reason(reasons, REASON_SOURCE_SHARED_SUMMARY_USED_AS_ROOT_FINAL)
        if (
            root_final.transaction_id != source_bundle.transaction_id
            or root_final.root_owner != root_owner
            or root_final.created_by != root_owner
            or root_final.final_status != STATUS_PASS
            or not _is_string_tuple(root_final.source_artifact_refs, allow_empty=False)
        ):
            _append_reason(reasons, REASON_SOURCE_ROOT_FINAL_WRONG_OWNER)
        elif (
            expected_refs_by_root is not None
            and root_final.source_artifact_refs != expected_refs_by_root[root_owner]
        ):
            _append_reason(reasons, REASON_SOURCE_ROOT_FINAL_WRONG_OWNER)
        if _is_string_tuple(root_final.source_artifact_refs, allow_empty=False) and any(
            "shared" in ref.lower() for ref in root_final.source_artifact_refs
        ):
            _append_reason(reasons, REASON_SOURCE_SHARED_SUMMARY_USED_AS_ROOT_FINAL)
        if (
            not _is_false(root_final.authority_created_by_ledger)
            or not _is_false(root_final.permission_created_by_ledger)
        ):
            _append_reason(reasons, REASON_SOURCE_PROVIDER_AUTHORITY_DETECTED)
        if not _is_zero_int(root_final.real_world_effects_count):
            _append_reason(reasons, REASON_SOURCE_REAL_EFFECT_DETECTED)
    return tuple(reasons)


def _provider_and_effect_errors(
    source_bundle: AirlineTransactionArtifactLedgerSourceBundleV01,
) -> tuple[str, ...]:
    reasons: list[str] = []
    causal_report = source_bundle.causal_report
    corridor_report = source_bundle.corridor_report
    if (
        causal_report.provider_created_authority_count != 0
        or causal_report.provider_created_contract_count != 0
        or causal_report.runtime_receipt_created_count != 0
    ):
        _append_reason(reasons, REASON_SOURCE_PROVIDER_AUTHORITY_DETECTED)
    if (
        causal_report.provider_network_call_count != 0
        or causal_report.gemini_call_count != 0
        or causal_report.real_world_effects_count != 0
    ):
        _append_reason(reasons, REASON_SOURCE_REAL_EFFECT_DETECTED)
    for key in (
        "provider_called_count",
        "network_used_count",
        "gemini_called_count",
        "real_world_effects_count",
    ):
        if corridor_report.counter_table.get(key) != 0:
            _append_reason(reasons, REASON_SOURCE_REAL_EFFECT_DETECTED)
    source_objects = (
        source_bundle.offer_packet,
        source_bundle.hold_receipt,
        source_bundle.purchase_approval_evidence,
        source_bundle.purchase_intent,
        source_bundle.payment_authorization_ref,
        source_bundle.mock_ticket_receipt,
        source_bundle.mock_purchase_receipt,
    )
    if any(
        getattr(source_object, "real_world_effects_count", 0) != 0
        for source_object in source_objects
    ):
        _append_reason(reasons, REASON_SOURCE_REAL_EFFECT_DETECTED)
    if (
        source_bundle.hold_packet.real_world_effects_allowed
        or source_bundle.ticket_issue_intent.real_world_effects_allowed
    ):
        _append_reason(reasons, REASON_SOURCE_REAL_EFFECT_DETECTED)
    return tuple(reasons)


def _source_refs_errors(
    source_bundle: AirlineTransactionArtifactLedgerSourceBundleV01,
) -> tuple[str, ...]:
    if not _expected_source_refs_valid(source_bundle.expected_source_refs):
        return (REASON_SOURCE_REF_MISMATCH,)
    if not _is_string_tuple(source_bundle.source_validation_refs):
        return (REASON_SOURCE_REF_MISMATCH,)
    if not _is_string_tuple(source_bundle.auxiliary_observation_refs):
        return (REASON_SOURCE_REF_MISMATCH,)
    if not (
        isinstance(
            source_bundle.causal_report,
            causal_runtime.AirlineSemanticCausalRunReportV01,
        )
        and isinstance(
            source_bundle.corridor_report,
            corridor_runtime.AirlineTicketPurchaseCorridorRunReportV01,
        )
    ):
        return (REASON_SOURCE_REF_MISMATCH,)
    required_top_level_refs = _source_refs_profile(source_bundle)
    if (
        source_bundle.expected_source_refs.source_run_ref != required_top_level_refs[0]
        or source_bundle.expected_source_refs.source_causal_report_ref
        != required_top_level_refs[1]
        or source_bundle.expected_source_refs.source_corridor_report_ref
        != required_top_level_refs[2]
        or source_bundle.source_validation_refs != required_top_level_refs
        or source_bundle.auxiliary_observation_refs
        != EXPECTED_AUXILIARY_OBSERVATION_REFS
    ):
        return (REASON_SOURCE_REF_MISMATCH,)
    combined_refs = source_bundle.source_validation_refs + source_bundle.auxiliary_observation_refs
    if len(set(combined_refs)) != len(combined_refs):
        return (REASON_SOURCE_REF_MISMATCH,)
    forbidden_tokens = (
        "authority",
        "permission",
        "secret",
        "raw",
        "passport",
        "card",
        "iban",
        "payment_token",
        "credential",
    )
    if any(any(token in ref.lower() for token in forbidden_tokens) for ref in combined_refs):
        return (REASON_SOURCE_REF_MISMATCH,)
    return ()


def validate_airline_transaction_artifact_ledger_source_bundle_v01(
    source_bundle: Any,
) -> AirlineTransactionArtifactLedgerSourceValidationReportV01:
    if not isinstance(source_bundle, AirlineTransactionArtifactLedgerSourceBundleV01):
        return _source_report(
            transaction_id="",
            reasons=(REASON_SOURCE_BUNDLE_WRONG_TYPE,),
        )

    reasons: list[str] = []
    if not _is_non_empty_string(source_bundle.source_bundle_id):
        _append_reason(reasons, REASON_SOURCE_BUNDLE_WRONG_TYPE)
    if not _is_non_empty_string(source_bundle.transaction_id):
        _append_reason(reasons, REASON_SOURCE_BUNDLE_TRANSACTION_MISMATCH)

    for reason in _source_refs_errors(source_bundle):
        _append_reason(reasons, reason)

    causal_shape_valid = _causal_report_shape_valid(source_bundle.causal_report)
    corridor_shape_valid = _corridor_report_shape_valid(source_bundle.corridor_report)

    if not causal_shape_valid:
        _append_reason(reasons, REASON_SOURCE_CAUSAL_REPORT_INVALID)
    else:
        try:
            causal_ok, _ = (
                causal_runtime.validate_airline_semantic_causal_run_report_v01(
                    source_bundle.causal_report,
                )
            )
        except (TypeError, AttributeError, ValueError):
            causal_ok = False
        if not causal_ok:
            _append_reason(reasons, REASON_SOURCE_CAUSAL_REPORT_INVALID)

    if not corridor_shape_valid:
        _append_reason(reasons, REASON_SOURCE_CORRIDOR_REPORT_INVALID)
    else:
        try:
            corridor_ok, _ = (
                corridor_runtime.validate_airline_ticket_purchase_corridor_run_v01(
                    source_bundle.corridor_report,
                )
            )
        except (TypeError, AttributeError, ValueError):
            corridor_ok = False
        if not corridor_ok:
            _append_reason(reasons, REASON_SOURCE_CORRIDOR_REPORT_INVALID)

    for reason in _bsep_lineage_errors(source_bundle):
        _append_reason(reasons, reason)

    artifact_type_errors = _source_artifact_type_errors(source_bundle)
    for reason in artifact_type_errors:
        _append_reason(reasons, reason)

    artifact_shape_errors: tuple[str, ...] = ()
    if (
        REASON_SOURCE_ARTIFACT_MISSING not in artifact_type_errors
        and REASON_SOURCE_ARTIFACT_WRONG_TYPE not in artifact_type_errors
        and corridor_shape_valid
    ):
        artifact_shape_errors = _source_artifact_shape_errors(source_bundle)
        for reason in artifact_shape_errors:
            _append_reason(reasons, reason)

    if (
        REASON_SOURCE_ARTIFACT_MISSING not in artifact_type_errors
        and REASON_SOURCE_ARTIFACT_WRONG_TYPE not in artifact_type_errors
        and REASON_SOURCE_ARTIFACT_WRONG_TYPE not in artifact_shape_errors
        and causal_shape_valid
        and corridor_shape_valid
    ):
        if REASON_SOURCE_CORRIDOR_REPORT_INVALID not in reasons:
            for reason in _contract_report_errors(source_bundle):
                _append_reason(reasons, reason)
        for reason in _identity_errors(source_bundle):
            _append_reason(reasons, reason)
        if REASON_SOURCE_CORRIDOR_REPORT_INVALID not in reasons:
            for reason in _phase_evidence_errors(source_bundle):
                _append_reason(reasons, reason)
        if REASON_SOURCE_CAUSAL_REPORT_INVALID not in reasons:
            for reason in _provider_and_effect_errors(source_bundle):
                _append_reason(reasons, reason)

    for reason in _root_final_errors(source_bundle):
        _append_reason(reasons, reason)

    return _source_report(
        transaction_id=source_bundle.transaction_id,
        reasons=tuple(reasons),
    )


def _fail_closed_ledger(
    *,
    validation_errors: tuple[str, ...],
    expected_source_refs: Any,
    transaction_id: Any,
) -> ledger.AirlineTransactionArtifactLedgerV01:
    source_run_ref = (
        expected_source_refs.source_run_ref
        if _expected_source_refs_valid(expected_source_refs)
        else ""
    )
    source_causal_report_ref = (
        expected_source_refs.source_causal_report_ref
        if _expected_source_refs_valid(expected_source_refs)
        else ""
    )
    source_corridor_report_ref = (
        expected_source_refs.source_corridor_report_ref
        if _expected_source_refs_valid(expected_source_refs)
        else ""
    )
    return ledger.AirlineTransactionArtifactLedgerV01(
        ledger_id="",
        ledger_version=ledger.LEDGER_VERSION,
        transaction_id=transaction_id if type(transaction_id) is str else "",
        source_run_ref=source_run_ref,
        source_causal_report_ref=source_causal_report_ref,
        source_corridor_report_ref=source_corridor_report_ref,
        entries=(),
        entry_count=0,
        dependency_edge_count=0,
        event_type_counts={},
        root_final_count=0,
        validation_status=STATUS_FAIL_CLOSED,
        validation_errors=validation_errors,
        ledger_created_authority_count=0,
        ledger_created_permission_count=0,
        ledger_created_action_count=0,
        provider_called_count=0,
        network_used_count=0,
        gemini_called_count=0,
        real_world_effects_count=0,
    )


def _source_artifact_ids(
    source_bundle: AirlineTransactionArtifactLedgerSourceBundleV01,
) -> dict[str, str]:
    return {
        ledger.ARTIFACT_TRANSACTION_SCOPE: (
            f"airline_transaction_scope:{source_bundle.transaction_id}"
        ),
        ledger.ARTIFACT_CLIENT_BSEP_PROJECTION: (
            source_bundle.client_bsep_projection.projection_id
        ),
        ledger.ARTIFACT_AIRLINE_BSEP_PROJECTION: (
            source_bundle.airline_bsep_projection.projection_id
        ),
        ledger.ARTIFACT_BANK_BSEP_PROJECTION: (
            source_bundle.bank_bsep_projection.projection_id
        ),
        ledger.ARTIFACT_CROSS_ROOT_BSEP_PROJECTION: (
            source_bundle.cross_root_bsep_projection.projection_id
        ),
        ledger.ARTIFACT_VALIDATED_CANONICAL_SEMANTIC_EVIDENCE: (
            source_bundle.causal_report.canonical_evidence.canonical_selection_id
        ),
        ledger.ARTIFACT_CLIENT_ROOT_SELECTION_DECISION: (
            source_bundle.causal_report.client_root_decision.decision_id
        ),
        ledger.ARTIFACT_AIRLINE_ROOT_OFFER_RESOLUTION: (
            source_bundle.causal_report.airline_root_resolution.resolution_id
        ),
        ledger.ARTIFACT_AIRLINE_OFFER_PACKET: source_bundle.offer_packet.packet_id,
        ledger.ARTIFACT_AIRLINE_HOLD_PACKET: source_bundle.hold_packet.packet_id,
        ledger.ARTIFACT_AIRLINE_OFFER_HOLD_RECEIPT: (
            source_bundle.hold_receipt.receipt_id
        ),
        ledger.ARTIFACT_CLIENT_PURCHASE_INTENT: (
            source_bundle.purchase_intent.intent_id
        ),
        ledger.ARTIFACT_BANK_PAYMENT_AUTHORIZATION: (
            source_bundle.payment_authorization_ref.authorization_ref_id
        ),
        ledger.ARTIFACT_AIRLINE_TICKET_ISSUE_INTENT: (
            source_bundle.ticket_issue_intent.intent_id
        ),
        ledger.ARTIFACT_MOCK_TICKET_RECEIPT: (
            source_bundle.mock_ticket_receipt.receipt_id
        ),
        ledger.ARTIFACT_MOCK_PURCHASE_RECEIPT: (
            source_bundle.mock_purchase_receipt.receipt_id
        ),
        ledger.ARTIFACT_CLIENT_ROOT_FINAL: source_bundle.client_root_final.final_id,
        ledger.ARTIFACT_AIRLINE_ROOT_FINAL: source_bundle.airline_root_final.final_id,
        ledger.ARTIFACT_BANK_ROOT_FINAL: source_bundle.bank_root_final.final_id,
    }


def _binding_report_source_ref(
    report: binding.AirlineSemanticToContractBindingReportV01,
) -> str:
    return (
        "AirlineSemanticToContractBindingReportV01:"
        f"{report.source_semantic_artifact_ref}:"
        f"{report.canonical_selection_ref}:"
        f"{report.client_root_decision_ref}:"
        f"{report.airline_root_resolution_ref}:"
        f"{report.hold_packet_ref}"
    )


def _semantic_source_refs(
    source_bundle: AirlineTransactionArtifactLedgerSourceBundleV01,
) -> tuple[str, ...]:
    return (
        source_bundle.causal_report.client_constraint_set_id,
        source_bundle.causal_report.candidate_set_snapshot_id,
        source_bundle.causal_report.proposer_request.source_selection_input_id,
        source_bundle.causal_report.proposal.proposal_id,
        *tuple(
            review.canonical_actor_output_id
            for review in source_bundle.causal_report.actor_reviews
        ),
        source_bundle.causal_report.synthesis.synthesis_report_id,
        _binding_report_source_ref(source_bundle.causal_report.causal_binding_report),
    )


def _source_validation_refs_by_artifact_type(
    source_bundle: AirlineTransactionArtifactLedgerSourceBundleV01,
) -> Mapping[str, tuple[str, ...]]:
    refs = {
        artifact_type: tuple(value)
        for artifact_type, value in ledger.EXPECTED_SOURCE_REFS_BY_ARTIFACT_TYPE.items()
    }
    refs[ledger.ARTIFACT_VALIDATED_CANONICAL_SEMANTIC_EVIDENCE] = (
        _semantic_source_refs(source_bundle)
    )
    refs[ledger.ARTIFACT_CLIENT_PURCHASE_INTENT] = (
        source_bundle.purchase_approval_evidence.approval_ref,
    )
    return refs


def _auxiliary_artifact_refs_by_artifact_type(
    source_bundle: AirlineTransactionArtifactLedgerSourceBundleV01,
) -> Mapping[str, tuple[str, ...]]:
    return {
        artifact_type: (
            EXPECTED_AUXILIARY_OBSERVATION_REFS
            if artifact_type == ledger.ARTIFACT_VALIDATED_CANONICAL_SEMANTIC_EVIDENCE
            else ()
        )
        for artifact_type in ledger.EXPECTED_ARTIFACT_TYPE_SEQUENCE
    }


def _source_dependencies_by_artifact_type(
    ids: MappingABC,
) -> dict[str, tuple[str, ...]]:
    return {
        ledger.ARTIFACT_TRANSACTION_SCOPE: (),
        ledger.ARTIFACT_CLIENT_BSEP_PROJECTION: (
            ids[ledger.ARTIFACT_TRANSACTION_SCOPE],
        ),
        ledger.ARTIFACT_AIRLINE_BSEP_PROJECTION: (
            ids[ledger.ARTIFACT_TRANSACTION_SCOPE],
        ),
        ledger.ARTIFACT_BANK_BSEP_PROJECTION: (
            ids[ledger.ARTIFACT_TRANSACTION_SCOPE],
        ),
        ledger.ARTIFACT_CROSS_ROOT_BSEP_PROJECTION: (
            ids[ledger.ARTIFACT_TRANSACTION_SCOPE],
        ),
        ledger.ARTIFACT_VALIDATED_CANONICAL_SEMANTIC_EVIDENCE: (
            ids[ledger.ARTIFACT_AIRLINE_BSEP_PROJECTION],
        ),
        ledger.ARTIFACT_CLIENT_ROOT_SELECTION_DECISION: (
            ids[ledger.ARTIFACT_VALIDATED_CANONICAL_SEMANTIC_EVIDENCE],
        ),
        ledger.ARTIFACT_AIRLINE_ROOT_OFFER_RESOLUTION: (
            ids[ledger.ARTIFACT_CLIENT_ROOT_SELECTION_DECISION],
        ),
        ledger.ARTIFACT_AIRLINE_OFFER_PACKET: (
            ids[ledger.ARTIFACT_AIRLINE_ROOT_OFFER_RESOLUTION],
        ),
        ledger.ARTIFACT_AIRLINE_HOLD_PACKET: (
            ids[ledger.ARTIFACT_AIRLINE_OFFER_PACKET],
        ),
        ledger.ARTIFACT_AIRLINE_OFFER_HOLD_RECEIPT: (
            ids[ledger.ARTIFACT_AIRLINE_HOLD_PACKET],
        ),
        ledger.ARTIFACT_CLIENT_PURCHASE_INTENT: (
            ids[ledger.ARTIFACT_AIRLINE_HOLD_PACKET],
        ),
        ledger.ARTIFACT_BANK_PAYMENT_AUTHORIZATION: (
            ids[ledger.ARTIFACT_CLIENT_PURCHASE_INTENT],
        ),
        ledger.ARTIFACT_AIRLINE_TICKET_ISSUE_INTENT: (
            ids[ledger.ARTIFACT_AIRLINE_HOLD_PACKET],
            ids[ledger.ARTIFACT_CLIENT_PURCHASE_INTENT],
            ids[ledger.ARTIFACT_BANK_PAYMENT_AUTHORIZATION],
        ),
        ledger.ARTIFACT_MOCK_TICKET_RECEIPT: (
            ids[ledger.ARTIFACT_AIRLINE_TICKET_ISSUE_INTENT],
        ),
        ledger.ARTIFACT_MOCK_PURCHASE_RECEIPT: (
            ids[ledger.ARTIFACT_MOCK_TICKET_RECEIPT],
            ids[ledger.ARTIFACT_BANK_PAYMENT_AUTHORIZATION],
            ids[ledger.ARTIFACT_CLIENT_PURCHASE_INTENT],
        ),
        ledger.ARTIFACT_CLIENT_ROOT_FINAL: (
            ids[ledger.ARTIFACT_CLIENT_ROOT_SELECTION_DECISION],
            ids[ledger.ARTIFACT_CLIENT_PURCHASE_INTENT],
            ids[ledger.ARTIFACT_MOCK_PURCHASE_RECEIPT],
        ),
        ledger.ARTIFACT_AIRLINE_ROOT_FINAL: (
            ids[ledger.ARTIFACT_AIRLINE_ROOT_OFFER_RESOLUTION],
            ids[ledger.ARTIFACT_AIRLINE_OFFER_PACKET],
            ids[ledger.ARTIFACT_AIRLINE_HOLD_PACKET],
            ids[ledger.ARTIFACT_AIRLINE_OFFER_HOLD_RECEIPT],
            ids[ledger.ARTIFACT_AIRLINE_TICKET_ISSUE_INTENT],
            ids[ledger.ARTIFACT_MOCK_TICKET_RECEIPT],
        ),
        ledger.ARTIFACT_BANK_ROOT_FINAL: (
            ids[ledger.ARTIFACT_BANK_PAYMENT_AUTHORIZATION],
        ),
    }


def _snapshot_from_fields(
    source_object: Any,
    field_names: tuple[str, ...],
) -> Mapping[str, Any]:
    return {
        field_name: _freeze_json(getattr(source_object, field_name))
        for field_name in field_names
    }


def _semantic_claim_source_snapshot(
    source_bundle: AirlineTransactionArtifactLedgerSourceBundleV01,
) -> Mapping[str, Any]:
    return {
        "client_constraint_set_id": source_bundle.causal_report.client_constraint_set_id,
        "candidate_set_snapshot_id": (
            source_bundle.causal_report.candidate_set_snapshot_id
        ),
        "candidate_set_digest": source_bundle.causal_report.candidate_set_digest,
        "selection_input_id": (
            source_bundle.causal_report.proposer_request.source_selection_input_id
        ),
        "proposal_id": source_bundle.causal_report.proposal.proposal_id,
        "canonical_actor_review_ids": tuple(
            review.canonical_actor_output_id
            for review in source_bundle.causal_report.actor_reviews
        ),
        "synthesis_report_id": (
            source_bundle.causal_report.synthesis.synthesis_report_id
        ),
        "canonical_selection_id": (
            source_bundle.causal_report.canonical_evidence.canonical_selection_id
        ),
        "causal_binding_report_ref": _binding_report_source_ref(
            source_bundle.causal_report.causal_binding_report,
        ),
        "recommended_offer_id": (
            source_bundle.causal_report.canonical_evidence.recommended_offer_id
        ),
    }


def _source_object_for_snapshot(
    source_bundle: AirlineTransactionArtifactLedgerSourceBundleV01,
    *,
    artifact_type: str,
) -> Any:
    source_by_artifact_type = {
        ledger.ARTIFACT_TRANSACTION_SCOPE: source_bundle.corridor_report.contract_context,
        ledger.ARTIFACT_CLIENT_BSEP_PROJECTION: source_bundle.client_bsep_projection,
        ledger.ARTIFACT_AIRLINE_BSEP_PROJECTION: source_bundle.airline_bsep_projection,
        ledger.ARTIFACT_BANK_BSEP_PROJECTION: source_bundle.bank_bsep_projection,
        ledger.ARTIFACT_CROSS_ROOT_BSEP_PROJECTION: (
            source_bundle.cross_root_bsep_projection
        ),
        ledger.ARTIFACT_VALIDATED_CANONICAL_SEMANTIC_EVIDENCE: None,
        ledger.ARTIFACT_CLIENT_ROOT_SELECTION_DECISION: (
            source_bundle.causal_report.client_root_decision
        ),
        ledger.ARTIFACT_AIRLINE_ROOT_OFFER_RESOLUTION: (
            source_bundle.causal_report.airline_root_resolution
        ),
        ledger.ARTIFACT_AIRLINE_OFFER_PACKET: source_bundle.offer_packet,
        ledger.ARTIFACT_AIRLINE_HOLD_PACKET: source_bundle.hold_packet,
        ledger.ARTIFACT_AIRLINE_OFFER_HOLD_RECEIPT: source_bundle.hold_receipt,
        ledger.ARTIFACT_CLIENT_PURCHASE_INTENT: source_bundle.purchase_intent,
        ledger.ARTIFACT_BANK_PAYMENT_AUTHORIZATION: (
            source_bundle.payment_authorization_ref
        ),
        ledger.ARTIFACT_AIRLINE_TICKET_ISSUE_INTENT: source_bundle.ticket_issue_intent,
        ledger.ARTIFACT_MOCK_TICKET_RECEIPT: source_bundle.mock_ticket_receipt,
        ledger.ARTIFACT_MOCK_PURCHASE_RECEIPT: source_bundle.mock_purchase_receipt,
        ledger.ARTIFACT_CLIENT_ROOT_FINAL: source_bundle.client_root_final,
        ledger.ARTIFACT_AIRLINE_ROOT_FINAL: source_bundle.airline_root_final,
        ledger.ARTIFACT_BANK_ROOT_FINAL: source_bundle.bank_root_final,
    }
    return source_by_artifact_type[artifact_type]


def _source_snapshot_for_artifact_type(
    source_bundle: AirlineTransactionArtifactLedgerSourceBundleV01,
    *,
    artifact_type: str,
) -> Mapping[str, Any]:
    if artifact_type == ledger.ARTIFACT_VALIDATED_CANONICAL_SEMANTIC_EVIDENCE:
        return _semantic_claim_source_snapshot(source_bundle)
    if artifact_type == ledger.ARTIFACT_CLIENT_PURCHASE_INTENT:
        return {
            "purchase_intent": _snapshot_from_fields(
                source_bundle.purchase_intent,
                PURCHASE_INTENT_SNAPSHOT_FIELDS,
            ),
            "purchase_approval_evidence": _snapshot_from_fields(
                source_bundle.purchase_approval_evidence,
                APPROVAL_SNAPSHOT_FIELDS,
            ),
        }
    return _snapshot_from_fields(
        _source_object_for_snapshot(source_bundle, artifact_type=artifact_type),
        CANONICAL_SOURCE_SNAPSHOT_FIELDS_BY_ARTIFACT_TYPE[artifact_type],
    )


def _source_identity_fields(
    source_bundle: AirlineTransactionArtifactLedgerSourceBundleV01,
    *,
    artifact_type: str,
) -> Mapping[str, Any]:
    base: dict[str, Any] = {
        "source_snapshot": _source_snapshot_for_artifact_type(
            source_bundle,
            artifact_type=artifact_type,
        ),
    }
    if artifact_type == ledger.ARTIFACT_TRANSACTION_SCOPE:
        base.update({
            "source_run_ref": source_bundle.expected_source_refs.source_run_ref,
            "source_causal_report_ref": (
                source_bundle.expected_source_refs.source_causal_report_ref
            ),
            "source_corridor_report_ref": (
                source_bundle.expected_source_refs.source_corridor_report_ref
            ),
        })
        return base
    projection_by_type = {
        ledger.ARTIFACT_CLIENT_BSEP_PROJECTION: (
            source_bundle.client_bsep_projection
        ),
        ledger.ARTIFACT_AIRLINE_BSEP_PROJECTION: (
            source_bundle.airline_bsep_projection
        ),
        ledger.ARTIFACT_BANK_BSEP_PROJECTION: source_bundle.bank_bsep_projection,
        ledger.ARTIFACT_CROSS_ROOT_BSEP_PROJECTION: (
            source_bundle.cross_root_bsep_projection
        ),
    }
    projection = projection_by_type.get(artifact_type)
    if isinstance(projection, AirlineTransactionArtifactLedgerBSEPProjectionSourceV01):
        base.update({
            "projection_id": projection.projection_id,
            "projection_ref": projection.projection_ref,
            "bsep_packet_id": projection.bsep_packet_id,
            "side": projection.side,
        })
        return base
    root_final_by_type = {
        ledger.ARTIFACT_CLIENT_ROOT_FINAL: source_bundle.client_root_final,
        ledger.ARTIFACT_AIRLINE_ROOT_FINAL: source_bundle.airline_root_final,
        ledger.ARTIFACT_BANK_ROOT_FINAL: source_bundle.bank_root_final,
    }
    root_final = root_final_by_type.get(artifact_type)
    if isinstance(root_final, AirlineTransactionArtifactLedgerRootFinalSourceV01):
        base["source_artifact_refs"] = root_final.source_artifact_refs
        return base
    return base


def _source_identity_fields_by_artifact_type(
    source_bundle: AirlineTransactionArtifactLedgerSourceBundleV01,
) -> Mapping[str, Mapping[str, Any]]:
    offer_id = source_bundle.causal_report.semantic_recommendation_id
    hold_id = source_bundle.hold_packet.hold_id
    amount = source_bundle.causal_report.airline_root_resolution.resolved_amount
    currency = source_bundle.causal_report.airline_root_resolution.resolved_currency
    route_ref = source_bundle.causal_report.airline_root_resolution.resolved_route_ref
    result: dict[str, Mapping[str, Any]] = {}
    for artifact_type in ledger.EXPECTED_ARTIFACT_TYPE_SEQUENCE:
        source_fields = _source_identity_fields(
            source_bundle,
            artifact_type=artifact_type,
        )
        values: dict[str, Any] = {}
        for key in ledger.CANONICAL_HASH_INPUT_EXTRA_KEYS_BY_ARTIFACT_TYPE[
            artifact_type
        ]:
            if key == "selected_offer_id":
                values[key] = offer_id
            elif key == "hold_id":
                values[key] = hold_id
            elif key == "amount":
                values[key] = amount
            elif key == "currency":
                values[key] = currency
            elif key == "route_ref":
                values[key] = route_ref
            else:
                values[key] = source_fields.get(key)
        result[artifact_type] = values
    return result


def _event_type_counts(
    entries: tuple[ledger.AirlineTransactionArtifactLedgerEntryV01, ...],
) -> Mapping[str, int]:
    counts: dict[str, int] = {}
    for entry in entries:
        if type(entry.event_type) is str:
            counts[entry.event_type] = counts.get(entry.event_type, 0) + 1
    return dict(sorted(counts.items()))


def _dependency_edge_count(
    entries: tuple[ledger.AirlineTransactionArtifactLedgerEntryV01, ...],
) -> int:
    return sum(
        len(entry.depends_on)
        for entry in entries
        if type(entry.depends_on) is tuple
    )


def _expected_identity_from_source(
    source_bundle: AirlineTransactionArtifactLedgerSourceBundleV01,
) -> ledger.AirlineTransactionArtifactLedgerExpectedIdentityV01:
    return ledger.AirlineTransactionArtifactLedgerExpectedIdentityV01(
        expected_source_refs=source_bundle.expected_source_refs,
        expected_artifact_ids=_source_artifact_ids(source_bundle),
        expected_source_validation_refs_by_type=(
            _source_validation_refs_by_artifact_type(source_bundle)
        ),
        expected_auxiliary_artifact_refs_by_type=(
            _auxiliary_artifact_refs_by_artifact_type(source_bundle)
        ),
        expected_source_identity_fields_by_type=(
            _source_identity_fields_by_artifact_type(source_bundle)
        ),
    )


def build_airline_transaction_artifact_ledger_expected_identity_from_source_v01(
    *,
    source_bundle: object,
) -> ledger.AirlineTransactionArtifactLedgerExpectedIdentityV01:
    if type(source_bundle) is not AirlineTransactionArtifactLedgerSourceBundleV01:
        raise ValueError(REASON_SOURCE_BUNDLE_WRONG_TYPE)
    try:
        source_report = validate_airline_transaction_artifact_ledger_source_bundle_v01(
            source_bundle,
        )
    except (TypeError, AttributeError, ValueError, KeyError, IndexError) as exc:
        raise ValueError(REASON_SOURCE_BUNDLE_WRONG_TYPE) from exc
    if (
        source_report.validation_status != STATUS_PASS
        or source_report.validation_errors != ()
    ):
        reason = (
            source_report.validation_errors[0]
            if source_report.validation_errors
            else REASON_SOURCE_BUNDLE_WRONG_TYPE
        )
        raise ValueError(reason)
    return _expected_identity_from_source(source_bundle)


def collect_airline_transaction_artifact_ledger_from_source_v01(
    *,
    source_bundle: Any,
) -> ledger.AirlineTransactionArtifactLedgerV01:
    source_report = validate_airline_transaction_artifact_ledger_source_bundle_v01(
        source_bundle,
    )
    if source_report.validation_status != STATUS_PASS or not isinstance(
        source_bundle,
        AirlineTransactionArtifactLedgerSourceBundleV01,
    ):
        expected_refs = (
            source_bundle.expected_source_refs
            if isinstance(source_bundle, AirlineTransactionArtifactLedgerSourceBundleV01)
            else None
        )
        transaction_id = (
            source_bundle.transaction_id
            if isinstance(source_bundle, AirlineTransactionArtifactLedgerSourceBundleV01)
            else ""
        )
        return _fail_closed_ledger(
            validation_errors=source_report.validation_errors,
            expected_source_refs=expected_refs,
            transaction_id=transaction_id,
        )

    offer_id = source_bundle.causal_report.semantic_recommendation_id
    record = source_bundle.causal_report.airline_root_resolution
    hold_id = source_bundle.hold_packet.hold_id
    ids = _source_artifact_ids(source_bundle)
    dependencies = _source_dependencies_by_artifact_type(ids)
    source_validation_refs_by_type = _source_validation_refs_by_artifact_type(
        source_bundle,
    )
    auxiliary_refs_by_type = _auxiliary_artifact_refs_by_artifact_type(
        source_bundle,
    )
    source_identity_fields_by_type = _source_identity_fields_by_artifact_type(
        source_bundle,
    )
    entries = tuple(
        ledger.build_airline_transaction_artifact_ledger_entry_from_source_v01(
            index=index,
            artifact_type=artifact_type,
            artifact_id=ids[artifact_type],
            depends_on=dependencies[artifact_type],
            offer_id=offer_id,
            hold_id=hold_id,
            amount=record.resolved_amount,
            currency=record.resolved_currency,
            route_ref=record.resolved_route_ref,
            source_validation_refs=source_validation_refs_by_type[artifact_type],
            auxiliary_artifact_refs=auxiliary_refs_by_type[artifact_type],
            source_identity_fields=source_identity_fields_by_type[artifact_type],
        )
        for index, artifact_type in enumerate(ledger.EXPECTED_ARTIFACT_TYPE_SEQUENCE)
    )
    expected_identity = _expected_identity_from_source(source_bundle)
    item = ledger.AirlineTransactionArtifactLedgerV01(
        ledger_id=f"airline_transaction_artifact_ledger:{offer_id}",
        ledger_version=ledger.LEDGER_VERSION,
        transaction_id=source_bundle.transaction_id,
        source_run_ref=source_bundle.expected_source_refs.source_run_ref,
        source_causal_report_ref=(
            source_bundle.expected_source_refs.source_causal_report_ref
        ),
        source_corridor_report_ref=(
            source_bundle.expected_source_refs.source_corridor_report_ref
        ),
        entries=entries,
        entry_count=len(entries),
        dependency_edge_count=_dependency_edge_count(entries),
        event_type_counts=_event_type_counts(entries),
        root_final_count=sum(
            1 for entry in entries if entry.event_type == ledger.EVENT_ROOT_FINAL_CREATED
        ),
        validation_status=STATUS_PASS,
        validation_errors=(),
        ledger_created_authority_count=0,
        ledger_created_permission_count=0,
        ledger_created_action_count=0,
        provider_called_count=0,
        network_used_count=0,
        gemini_called_count=0,
        real_world_effects_count=0,
    )
    report = ledger.validate_airline_transaction_artifact_ledger_v01(
        item,
        expected_identity=expected_identity,
    )
    if report.validation_status == STATUS_PASS:
        return item
    return ledger.AirlineTransactionArtifactLedgerV01(
        **{
            **item.__dict__,
            "validation_status": STATUS_FAIL_CLOSED,
            "validation_errors": report.validation_errors,
        },
    )
