"""Root-centered Airline corridor state machine for deterministic Slice C.

This module consumes Airline domain fixtures/contracts from Slice B and records
side-local phase validation results. It does not execute adapters, create
runtime packets or receipts, call providers, or integrate with demo runners.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Mapping

from hedgehog.action_commit_packet_v02 import (
    CONTAINMENT_LAWS_V02,
    STATUS_FAIL_CLOSED as CORE_STATUS_FAIL_CLOSED,
    STATUS_PASS as CORE_STATUS_PASS,
    ContractFulfillmentCorridorV01,
    validate_corridor_no_post_root_reasoning_v01,
)
from hedgehog.domains.airline import ticket_purchase_corridor_v01 as contracts


MODULE_ID = "airline_ticket_purchase_corridor_runtime_v01"
SLICE_ID = "airline_ticket_purchase_corridor_v01_slice_c"

RUN_ID = "airline_ticket_purchase_corridor_runtime_v01"

STATUS_PASS = "PASS"
STATUS_FAIL_CLOSED = "FAIL_CLOSED"
STATUS_NOT_RUN = "NOT_RUN"
STATUS_RETURN_TO_RELEVANT_ROOT = "RETURN_TO_RELEVANT_ROOT"

PHASE_AIRLINE_OFFER_HOLD = "airline_offer_hold_phase"
PHASE_CLIENT_PURCHASE_INTENT = "client_purchase_intent_phase"
PHASE_BANK_PAYMENT_AUTHORIZATION = "bank_payment_authorization_phase"
PHASE_AIRLINE_TICKET_ISSUE = "airline_ticket_issue_phase"
PHASE_CLIENT_COMPLETION = "client_completion_phase"

PHASE_ORDER = (
    PHASE_AIRLINE_OFFER_HOLD,
    PHASE_CLIENT_PURCHASE_INTENT,
    PHASE_BANK_PAYMENT_AUTHORIZATION,
    PHASE_AIRLINE_TICKET_ISSUE,
    PHASE_CLIENT_COMPLETION,
)

STATE_SEQUENCE = (
    "semantic_lane_observed_as_closed_basis",
    "airline_root_offer_hold_review_completed",
    "airline_offer_packet_validated",
    "airline_hold_packet_validated",
    "airline_offer_hold_receipt_validated",
    "client_root_purchase_intent_review_completed",
    "client_purchase_intent_validated",
    "bank_root_payment_authorization_review_completed",
    "bank_payment_authorization_ref_validated",
    "airline_root_ticket_issue_review_completed",
    "airline_ticket_issue_intent_validated",
    "mock_ticket_receipt_validated",
    "mock_purchase_receipt_validated",
    "client_root_completion_review_completed",
    "side_specific_final_statuses_observed",
)

PHASE_ROOTS = {
    PHASE_AIRLINE_OFFER_HOLD: contracts.AIRLINE_ROOT_ID,
    PHASE_CLIENT_PURCHASE_INTENT: contracts.CLIENT_ROOT_ID,
    PHASE_BANK_PAYMENT_AUTHORIZATION: contracts.BANK_ROOT_ID,
    PHASE_AIRLINE_TICKET_ISSUE: contracts.AIRLINE_ROOT_ID,
    PHASE_CLIENT_COMPLETION: contracts.CLIENT_ROOT_ID,
}

NEXT_GATE = "airline_ticket_purchase_corridor_v01_slice_e_audit_and_human_story"

REASON_ROOT_PHASE_GATE_VALIDATION_FAILED = "root_phase_gate_validation_failed"
REASON_CORE_CORRIDOR_GUARD_VALIDATION_FAILED = (
    "core_corridor_guard_validation_failed"
)
REASON_DOMAIN_CONTRACT_VALIDATION_FAILED = "domain_contract_validation_failed"
REASON_NONZERO_PHASE_REAL_WORLD_EFFECTS = "nonzero_phase_real_world_effects"
REASON_PHASE_ROOT_MISMATCH = "phase_root_mismatch"
REASON_FAILED_PHASE_ID_MISMATCH = "failed_phase_id_mismatch"
REASON_RETURN_TO_ROOT_ID_MISMATCH = "return_to_root_id_mismatch"
REASON_COUNTER_TABLE_MISMATCH = "counter_table_mismatch"
REASON_TRANSITION_SHAPE_MISMATCH = "transition_shape_mismatch"
REASON_FIXTURE_REPORT_TRANSACTION_MISMATCH = "fixture_report_transaction_mismatch"
REASON_PHASE_EVIDENCE_REFS_MISMATCH = "phase_evidence_refs_mismatch"
REASON_PHASE_FIXTURE_ROOT_MISMATCH = "phase_fixture_root_mismatch"
REASON_ARTIFACT_VALIDATION_SUMMARY_MISMATCH = (
    "artifact_validation_summary_mismatch"
)
REASON_FIXTURE_REPORT_BINDING_FAILED = "fixture_report_binding_failed"
REASON_FIXTURE_BUNDLE_EMPTY = "fixture_bundle_empty"
REASON_FIXTURE_BUNDLE_MISSING_KEYS = "fixture_bundle_missing_keys"

REQUIRED_FIXTURE_KEYS = (
    "airline_offer_hold_gate",
    "offer_packet",
    "hold_packet",
    "hold_receipt",
    "client_purchase_gate",
    "human_approval",
    "purchase_intent",
    "bank_gate",
    "authorization_ref",
    "airline_ticket_gate",
    "ticket_issue_intent",
    "ticket_receipt",
    "completion_gate",
    "purchase_receipt",
)


@dataclass(frozen=True)
class AirlineCorridorPhaseResultV01:
    phase_index: int
    phase_id: str
    transaction_id: str
    relevant_root_id: str
    phase_status: str
    root_gate_validated: bool
    core_corridor_guard_validated: bool
    domain_contracts_validated: bool
    evidence_refs_observed: tuple[str, ...]
    reason_codes: tuple[str, ...]
    return_to_relevant_root: bool
    later_phases_allowed: bool
    authority_transferred: bool
    runtime_receipt_created: bool
    provider_called: bool
    network_used: bool
    gemini_called: bool
    real_world_effects_count: int


@dataclass(frozen=True)
class AirlineCorridorTransitionV01:
    transition_index: int
    from_phase_id: str
    to_phase_id: str
    transaction_id: str
    source_phase_passed: bool
    dependency_satisfied: bool
    authority_transferred: bool
    semantic_reasoning_restarted: bool
    transition_status: str
    reason_codes: tuple[str, ...]


@dataclass(frozen=True)
class AirlineCoreDelegationRowV01:
    check_id: str
    owner: str
    implementation: str
    directly_delegated_to_core: bool
    follows_core_invariant: str
    airline_specific_fields: tuple[str, ...]
    notes: str


@dataclass(frozen=True)
class AirlineTicketPurchaseCorridorRunReportV01:
    run_id: str
    slice_id: str
    transaction_id: str
    final_status: str
    failed_phase_id: str
    return_to_root_id: str
    phase_results: tuple[AirlineCorridorPhaseResultV01, ...]
    transitions: tuple[AirlineCorridorTransitionV01, ...]
    core_domain_delegation_matrix: tuple[AirlineCoreDelegationRowV01, ...]
    artifact_validation_summary: Mapping[str, Any]
    root_boundary_summary: tuple[Mapping[str, Any], ...]
    receipt_boundary_summary: Mapping[str, Any]
    counter_table: Mapping[str, int]
    contract_context: contracts.AirlineTicketPurchaseContractContextV01
    validation_errors: tuple[str, ...]
    next_gate: str


@dataclass(frozen=True)
class AirlineTicketPurchaseCorridorExecutionResultV01:
    report: AirlineTicketPurchaseCorridorRunReportV01
    contract_context: contracts.AirlineTicketPurchaseContractContextV01
    offer_packet: contracts.AirlineOfferPacketV01
    hold_packet: contracts.AirlineHoldCommitPacketV01
    hold_receipt: contracts.AirlineOfferHoldReceiptV01
    purchase_approval_evidence: contracts.AirlinePurchaseApprovalEvidenceRefV01
    purchase_intent: contracts.ClientPurchaseIntentV01
    payment_authorization_ref: contracts.BankPaymentAuthorizationRefV01
    ticket_issue_intent: contracts.AirlineTicketIssueIntentV01
    mock_ticket_receipt: contracts.MockTicketReceiptV01
    mock_purchase_receipt: contracts.MockPurchaseReceiptV01


def _append_reason(reasons: list[str], reason: str) -> None:
    if reason not in reasons:
        reasons.append(reason)


def _merge_report_reasons(
    reasons: list[str],
    *reports: contracts.AirlineCorridorValidationReportV01,
) -> None:
    for report in reports:
        for reason in report.reason_codes:
            _append_reason(reasons, reason)


def _status_from_reasons(reasons: tuple[str, ...]) -> str:
    return STATUS_PASS if not reasons else STATUS_FAIL_CLOSED


def _contract_context(
    contract_context: (
        contracts.AirlineTicketPurchaseContractContextV01 | None
    ),
) -> contracts.AirlineTicketPurchaseContractContextV01:
    return (
        contract_context
        if contract_context is not None
        else contracts.build_canonical_airline_ticket_purchase_contract_context_v01()
    )


def _core_phase_corridor(
    *,
    phase_id: str,
    packet_id: str,
    overrides: Mapping[str, Any] | None = None,
) -> ContractFulfillmentCorridorV01:
    corridor = ContractFulfillmentCorridorV01(
        corridor_id=f"airline_corridor:{phase_id}:{contracts.TRANSACTION_ID}",
        packet_id=packet_id,
        corridor_kind=f"airline_{phase_id}_corridor_v01",
        deterministic_only=True,
        post_root_llm_reasoning_allowed=False,
        reasoning_restarted_after_root=False,
        allowed_steps=(phase_id,),
        root_review_required_on_mismatch=True,
    )
    if overrides:
        corridor = replace(corridor, **dict(overrides))
    return corridor


def _validate_core_guard(
    *,
    phase_id: str,
    packet_id: str,
    core_corridor_overrides: Mapping[str, Mapping[str, Any]] | None,
) -> tuple[bool, tuple[str, ...]]:
    corridor = _core_phase_corridor(
        phase_id=phase_id,
        packet_id=packet_id,
        overrides=(
            core_corridor_overrides.get(phase_id)
            if core_corridor_overrides
            else None
        ),
    )
    core_valid, core_reasons = validate_corridor_no_post_root_reasoning_v01(
        corridor,
    )
    return core_valid, core_reasons


def _phase_result(
    *,
    phase_index: int,
    phase_id: str,
    relevant_root_id: str,
    root_gate_validated: bool,
    core_corridor_guard_validated: bool,
    domain_contracts_validated: bool,
    evidence_refs_observed: tuple[str, ...],
    reason_codes: tuple[str, ...],
    real_world_effects_count: int = 0,
) -> AirlineCorridorPhaseResultV01:
    reasons = list(reason_codes)
    if not root_gate_validated:
        _append_reason(reasons, REASON_ROOT_PHASE_GATE_VALIDATION_FAILED)
    if not core_corridor_guard_validated:
        _append_reason(reasons, REASON_CORE_CORRIDOR_GUARD_VALIDATION_FAILED)
    if not domain_contracts_validated:
        _append_reason(reasons, REASON_DOMAIN_CONTRACT_VALIDATION_FAILED)
    if real_world_effects_count != 0:
        _append_reason(reasons, REASON_NONZERO_PHASE_REAL_WORLD_EFFECTS)
    reason_codes = tuple(reasons)
    phase_status = _status_from_reasons(reason_codes)
    return AirlineCorridorPhaseResultV01(
        phase_index=phase_index,
        phase_id=phase_id,
        transaction_id=contracts.TRANSACTION_ID,
        relevant_root_id=relevant_root_id,
        phase_status=phase_status,
        root_gate_validated=root_gate_validated,
        core_corridor_guard_validated=core_corridor_guard_validated,
        domain_contracts_validated=domain_contracts_validated,
        evidence_refs_observed=evidence_refs_observed,
        reason_codes=reason_codes,
        return_to_relevant_root=phase_status != STATUS_PASS,
        later_phases_allowed=phase_status == STATUS_PASS,
        authority_transferred=False,
        runtime_receipt_created=False,
        provider_called=False,
        network_used=False,
        gemini_called=False,
        real_world_effects_count=real_world_effects_count,
    )


def _not_run_phase_result(
    *,
    phase_index: int,
    phase_id: str,
    relevant_root_id: str,
    blocked_by_phase_id: str,
) -> AirlineCorridorPhaseResultV01:
    return AirlineCorridorPhaseResultV01(
        phase_index=phase_index,
        phase_id=phase_id,
        transaction_id=contracts.TRANSACTION_ID,
        relevant_root_id=relevant_root_id,
        phase_status=STATUS_NOT_RUN,
        root_gate_validated=False,
        core_corridor_guard_validated=False,
        domain_contracts_validated=False,
        evidence_refs_observed=(),
        reason_codes=(f"blocked_by_failed_phase:{blocked_by_phase_id}",),
        return_to_relevant_root=False,
        later_phases_allowed=False,
        authority_transferred=False,
        runtime_receipt_created=False,
        provider_called=False,
        network_used=False,
        gemini_called=False,
        real_world_effects_count=0,
    )


def _build_valid_fixture_bundle_v01() -> dict[str, Any]:
    return {
        "airline_offer_hold_gate": (
            contracts.build_valid_airline_root_offer_hold_gate_v01()
        ),
        "offer_packet": contracts.build_valid_airline_offer_packet_v01(),
        "hold_packet": contracts.build_valid_airline_hold_commit_packet_v01(),
        "hold_receipt": contracts.build_valid_airline_offer_hold_receipt_v01(),
        "client_purchase_gate": (
            contracts.build_valid_client_root_purchase_intent_gate_v01()
        ),
        "human_approval": contracts.build_valid_human_approval_evidence_ref_v01(),
        "purchase_intent": contracts.build_valid_client_purchase_intent_v01(),
        "bank_gate": contracts.build_valid_bank_root_payment_authorization_gate_v01(),
        "authorization_ref": (
            contracts.build_valid_bank_payment_authorization_ref_v01()
        ),
        "airline_ticket_gate": (
            contracts.build_valid_airline_root_ticket_issue_gate_v01()
        ),
        "ticket_issue_intent": (
            contracts.build_valid_airline_ticket_issue_intent_v01()
        ),
        "ticket_receipt": contracts.build_valid_mock_ticket_receipt_v01(),
        "completion_gate": contracts.build_valid_client_root_completion_gate_v01(),
        "purchase_receipt": contracts.build_valid_mock_purchase_receipt_v01(),
    }


def _fixture_bundle_from_input(
    fixtures: Mapping[str, Any] | None,
) -> dict[str, Any]:
    if fixtures is None:
        return dict(_build_valid_fixture_bundle_v01())
    if not isinstance(fixtures, Mapping):
        raise ValueError("fixture_bundle_wrong_type")
    fixture_bundle = dict(fixtures)
    if not fixture_bundle:
        raise ValueError(REASON_FIXTURE_BUNDLE_EMPTY)
    missing = tuple(key for key in REQUIRED_FIXTURE_KEYS if key not in fixture_bundle)
    if missing:
        raise ValueError(
            f"{REASON_FIXTURE_BUNDLE_MISSING_KEYS}:{','.join(missing)}",
        )
    return fixture_bundle


def _core_domain_delegation_matrix() -> tuple[AirlineCoreDelegationRowV01, ...]:
    invariant_vocabulary = "; ".join(CONTAINMENT_LAWS_V02)
    return (
        AirlineCoreDelegationRowV01(
            check_id="no_post_root_reasoning",
            owner="universal_core",
            implementation="validate_corridor_no_post_root_reasoning_v01",
            directly_delegated_to_core=True,
            follows_core_invariant="NoExpansionAfterRoot = true",
            airline_specific_fields=(),
            notes=f"Uses core guard; vocabulary: {invariant_vocabulary}",
        ),
        AirlineCoreDelegationRowV01(
            check_id="corridor_deterministic_only",
            owner="universal_core_contract",
            implementation="ContractFulfillmentCorridorV01",
            directly_delegated_to_core=True,
            follows_core_invariant="deterministic_only",
            airline_specific_fields=(),
            notes="Local phase corridors use deterministic-only core contract fields.",
        ),
        AirlineCoreDelegationRowV01(
            check_id="root_phase_ownership",
            owner="airline_domain_projection",
            implementation="contracts.validate_root_phase_gate_v01",
            directly_delegated_to_core=False,
            follows_core_invariant="root_only_authority",
            airline_specific_fields=("root_id", "phase_id"),
            notes="Airline side-local gates preserve Root-centered ownership.",
        ),
        AirlineCoreDelegationRowV01(
            check_id="ttl_and_expiry",
            owner="airline_domain_projection",
            implementation="existing Slice B validators",
            directly_delegated_to_core=False,
            follows_core_invariant="TTL(child) <= TTL(parent)",
            airline_specific_fields=("ttl_seconds", "expired"),
            notes="Airline validators enforce local TTL and expiry fields.",
        ),
        AirlineCoreDelegationRowV01(
            check_id="idempotency",
            owner="airline_domain_projection",
            implementation="existing Slice B validators",
            directly_delegated_to_core=False,
            follows_core_invariant="idempotency_required",
            airline_specific_fields=("idempotency_key",),
            notes="Airline validators reject duplicate idempotency pressure.",
        ),
        AirlineCoreDelegationRowV01(
            check_id="receipt_evidence_only",
            owner="airline_domain_projection",
            implementation="existing Slice B receipt validators",
            directly_delegated_to_core=False,
            follows_core_invariant="receipt_is_evidence_only",
            airline_specific_fields=("evidence_only",),
            notes="Receipt fixtures are observed and must not create permission.",
        ),
        AirlineCoreDelegationRowV01(
            check_id="airline_offer_hold_bindings",
            owner="airline_domain_only",
            implementation="existing Slice B validators",
            directly_delegated_to_core=False,
            follows_core_invariant="parent_binding_must_match",
            airline_specific_fields=(
                "offer_id",
                "hold_id",
                "passenger_ref",
                "route_ref",
            ),
            notes="Airline fields are not mapped into supplier-specific fields.",
        ),
        AirlineCoreDelegationRowV01(
            check_id="airline_ticket_issue_bindings",
            owner="airline_domain_only",
            implementation="existing Slice B validators",
            directly_delegated_to_core=False,
            follows_core_invariant="dependency_binding_must_match",
            airline_specific_fields=(
                "offer_id",
                "hold_id",
                "passenger_ref",
                "route_ref",
                "merchant_ref",
            ),
            notes="Ticket issue bindings remain Airline-domain checks.",
        ),
    )


def _validate_airline_offer_hold_phase(
    fixtures: Mapping[str, Any],
    core_corridor_overrides: Mapping[str, Mapping[str, Any]] | None,
    contract_context: contracts.AirlineTicketPurchaseContractContextV01,
) -> AirlineCorridorPhaseResultV01:
    gate_report = contracts.validate_root_phase_gate_v01(
        fixtures["airline_offer_hold_gate"],
    )
    offer_report = contracts.validate_airline_offer_packet_v01(
        fixtures["offer_packet"],
        contract_context=contract_context,
    )
    hold_report = contracts.validate_airline_hold_commit_packet_v01(
        fixtures["offer_packet"],
        fixtures["hold_packet"],
        contract_context=contract_context,
    )
    receipt_report = contracts.validate_airline_offer_hold_receipt_v01(
        fixtures["hold_packet"],
        fixtures["hold_receipt"],
    )
    core_valid, core_reasons = _validate_core_guard(
        phase_id=PHASE_AIRLINE_OFFER_HOLD,
        packet_id=fixtures["hold_packet"].packet_id,
        core_corridor_overrides=core_corridor_overrides,
    )
    reasons = list(core_reasons)
    _merge_report_reasons(
        reasons,
        gate_report,
        offer_report,
        hold_report,
        receipt_report,
    )
    reason_codes = tuple(reasons)
    return _phase_result(
        phase_index=1,
        phase_id=PHASE_AIRLINE_OFFER_HOLD,
        relevant_root_id=contracts.AIRLINE_ROOT_ID,
        root_gate_validated=gate_report.validation_status == contracts.PASS,
        core_corridor_guard_validated=core_valid,
        domain_contracts_validated=all(
            report.validation_status == contracts.PASS
            for report in (offer_report, hold_report, receipt_report)
        ),
        evidence_refs_observed=(
            fixtures["offer_packet"].packet_id,
            fixtures["hold_packet"].packet_id,
            fixtures["hold_receipt"].receipt_id,
        ),
        reason_codes=reason_codes,
        real_world_effects_count=sum(
            report.real_world_effects_count
            for report in (gate_report, offer_report, hold_report, receipt_report)
        ),
    )


def _validate_client_purchase_intent_phase(
    fixtures: Mapping[str, Any],
    core_corridor_overrides: Mapping[str, Mapping[str, Any]] | None,
    contract_context: contracts.AirlineTicketPurchaseContractContextV01,
) -> AirlineCorridorPhaseResultV01:
    gate_report = contracts.validate_root_phase_gate_v01(
        fixtures["client_purchase_gate"],
    )
    human_report = contracts.validate_human_approval_evidence_ref_v01(
        fixtures["human_approval"],
        contract_context=contract_context,
    )
    purchase_report = contracts.validate_client_purchase_intent_v01(
        fixtures["human_approval"],
        fixtures["offer_packet"],
        fixtures["hold_receipt"],
        fixtures["purchase_intent"],
        contract_context=contract_context,
    )
    core_valid, core_reasons = _validate_core_guard(
        phase_id=PHASE_CLIENT_PURCHASE_INTENT,
        packet_id=fixtures["purchase_intent"].intent_id,
        core_corridor_overrides=core_corridor_overrides,
    )
    reasons = list(core_reasons)
    _merge_report_reasons(reasons, gate_report, human_report, purchase_report)
    return _phase_result(
        phase_index=2,
        phase_id=PHASE_CLIENT_PURCHASE_INTENT,
        relevant_root_id=contracts.CLIENT_ROOT_ID,
        root_gate_validated=gate_report.validation_status == contracts.PASS,
        core_corridor_guard_validated=core_valid,
        domain_contracts_validated=(
            human_report.validation_status == contracts.PASS
            and purchase_report.validation_status == contracts.PASS
        ),
        evidence_refs_observed=(
            fixtures["human_approval"].approval_ref,
            fixtures["purchase_intent"].intent_id,
        ),
        reason_codes=tuple(reasons),
        real_world_effects_count=sum(
            report.real_world_effects_count
            for report in (gate_report, human_report, purchase_report)
        ),
    )


def _validate_bank_payment_authorization_phase(
    fixtures: Mapping[str, Any],
    core_corridor_overrides: Mapping[str, Mapping[str, Any]] | None,
    contract_context: contracts.AirlineTicketPurchaseContractContextV01,
) -> AirlineCorridorPhaseResultV01:
    gate_report = contracts.validate_root_phase_gate_v01(fixtures["bank_gate"])
    auth_report = contracts.validate_bank_payment_authorization_ref_v01(
        fixtures["purchase_intent"],
        fixtures["authorization_ref"],
        contract_context=contract_context,
    )
    core_valid, core_reasons = _validate_core_guard(
        phase_id=PHASE_BANK_PAYMENT_AUTHORIZATION,
        packet_id=fixtures["authorization_ref"].authorization_ref_id,
        core_corridor_overrides=core_corridor_overrides,
    )
    reasons = list(core_reasons)
    _merge_report_reasons(reasons, gate_report, auth_report)
    return _phase_result(
        phase_index=3,
        phase_id=PHASE_BANK_PAYMENT_AUTHORIZATION,
        relevant_root_id=contracts.BANK_ROOT_ID,
        root_gate_validated=gate_report.validation_status == contracts.PASS,
        core_corridor_guard_validated=core_valid,
        domain_contracts_validated=auth_report.validation_status == contracts.PASS,
        evidence_refs_observed=(
            fixtures["authorization_ref"].authorization_ref_id,
        ),
        reason_codes=tuple(reasons),
        real_world_effects_count=sum(
            report.real_world_effects_count for report in (gate_report, auth_report)
        ),
    )


def _validate_airline_ticket_issue_phase(
    fixtures: Mapping[str, Any],
    core_corridor_overrides: Mapping[str, Mapping[str, Any]] | None,
    contract_context: contracts.AirlineTicketPurchaseContractContextV01,
) -> AirlineCorridorPhaseResultV01:
    gate_report = contracts.validate_root_phase_gate_v01(
        fixtures["airline_ticket_gate"],
    )
    ticket_intent_report = contracts.validate_airline_ticket_issue_intent_v01(
        fixtures["offer_packet"],
        fixtures["hold_packet"],
        fixtures["hold_receipt"],
        fixtures["purchase_intent"],
        fixtures["authorization_ref"],
        fixtures["ticket_issue_intent"],
        contract_context=contract_context,
    )
    ticket_receipt_report = contracts.validate_mock_ticket_receipt_v01(
        fixtures["ticket_issue_intent"],
        fixtures["ticket_receipt"],
        contract_context=contract_context,
    )
    core_valid, core_reasons = _validate_core_guard(
        phase_id=PHASE_AIRLINE_TICKET_ISSUE,
        packet_id=fixtures["ticket_issue_intent"].intent_id,
        core_corridor_overrides=core_corridor_overrides,
    )
    reasons = list(core_reasons)
    _merge_report_reasons(
        reasons,
        gate_report,
        ticket_intent_report,
        ticket_receipt_report,
    )
    return _phase_result(
        phase_index=4,
        phase_id=PHASE_AIRLINE_TICKET_ISSUE,
        relevant_root_id=contracts.AIRLINE_ROOT_ID,
        root_gate_validated=gate_report.validation_status == contracts.PASS,
        core_corridor_guard_validated=core_valid,
        domain_contracts_validated=(
            ticket_intent_report.validation_status == contracts.PASS
            and ticket_receipt_report.validation_status == contracts.PASS
        ),
        evidence_refs_observed=(
            fixtures["ticket_issue_intent"].intent_id,
            fixtures["ticket_receipt"].receipt_id,
        ),
        reason_codes=tuple(reasons),
        real_world_effects_count=sum(
            report.real_world_effects_count
            for report in (gate_report, ticket_intent_report, ticket_receipt_report)
        ),
    )


def _validate_client_completion_phase(
    fixtures: Mapping[str, Any],
    core_corridor_overrides: Mapping[str, Mapping[str, Any]] | None,
    contract_context: contracts.AirlineTicketPurchaseContractContextV01,
) -> AirlineCorridorPhaseResultV01:
    gate_report = contracts.validate_root_phase_gate_v01(fixtures["completion_gate"])
    purchase_receipt_report = contracts.validate_mock_purchase_receipt_v01(
        fixtures["purchase_intent"],
        fixtures["authorization_ref"],
        fixtures["ticket_receipt"],
        fixtures["purchase_receipt"],
    )
    core_valid, core_reasons = _validate_core_guard(
        phase_id=PHASE_CLIENT_COMPLETION,
        packet_id=fixtures["purchase_receipt"].receipt_id,
        core_corridor_overrides=core_corridor_overrides,
    )
    reasons = list(core_reasons)
    _merge_report_reasons(reasons, gate_report, purchase_receipt_report)
    return _phase_result(
        phase_index=5,
        phase_id=PHASE_CLIENT_COMPLETION,
        relevant_root_id=contracts.CLIENT_ROOT_ID,
        root_gate_validated=gate_report.validation_status == contracts.PASS,
        core_corridor_guard_validated=core_valid,
        domain_contracts_validated=(
            purchase_receipt_report.validation_status == contracts.PASS
        ),
        evidence_refs_observed=(fixtures["purchase_receipt"].receipt_id,),
        reason_codes=tuple(reasons),
        real_world_effects_count=sum(
            report.real_world_effects_count
            for report in (gate_report, purchase_receipt_report)
        ),
    )


PHASE_VALIDATORS = {
    PHASE_AIRLINE_OFFER_HOLD: _validate_airline_offer_hold_phase,
    PHASE_CLIENT_PURCHASE_INTENT: _validate_client_purchase_intent_phase,
    PHASE_BANK_PAYMENT_AUTHORIZATION: _validate_bank_payment_authorization_phase,
    PHASE_AIRLINE_TICKET_ISSUE: _validate_airline_ticket_issue_phase,
    PHASE_CLIENT_COMPLETION: _validate_client_completion_phase,
}


def validate_airline_ticket_purchase_corridor_fixture_bundle_v01(
    fixtures: Mapping[str, Any],
    *,
    core_corridor_overrides: Mapping[str, Mapping[str, Any]] | None = None,
    contract_context: (
        contracts.AirlineTicketPurchaseContractContextV01 | None
    ) = None,
) -> tuple[bool, tuple[str, ...]]:
    """Validate projected fixtures without constructing a corridor run report."""

    context = _contract_context(contract_context)
    reasons: list[str] = []
    gate_report = contracts.validate_root_phase_gate_v01(
        fixtures["airline_offer_hold_gate"],
    )
    offer_report = contracts.validate_airline_offer_packet_v01(
        fixtures["offer_packet"],
        contract_context=context,
    )
    hold_report = contracts.validate_airline_hold_commit_packet_v01(
        fixtures["offer_packet"],
        fixtures["hold_packet"],
        contract_context=context,
    )
    hold_receipt_report = contracts.validate_airline_offer_hold_receipt_v01(
        fixtures["hold_packet"],
        fixtures["hold_receipt"],
    )
    offer_core_valid, offer_core_reasons = _validate_core_guard(
        phase_id=PHASE_AIRLINE_OFFER_HOLD,
        packet_id=fixtures["hold_packet"].packet_id,
        core_corridor_overrides=core_corridor_overrides,
    )
    for reason in offer_core_reasons:
        _append_reason(reasons, reason)
    if not offer_core_valid:
        _append_reason(reasons, REASON_CORE_CORRIDOR_GUARD_VALIDATION_FAILED)
    _merge_report_reasons(
        reasons,
        gate_report,
        offer_report,
        hold_report,
        hold_receipt_report,
    )

    human_gate_report = contracts.validate_root_phase_gate_v01(
        fixtures["client_purchase_gate"],
    )
    human_report = contracts.validate_human_approval_evidence_ref_v01(
        fixtures["human_approval"],
        contract_context=context,
    )
    purchase_report = contracts.validate_client_purchase_intent_v01(
        fixtures["human_approval"],
        fixtures["offer_packet"],
        fixtures["hold_receipt"],
        fixtures["purchase_intent"],
        contract_context=context,
    )
    client_core_valid, client_core_reasons = _validate_core_guard(
        phase_id=PHASE_CLIENT_PURCHASE_INTENT,
        packet_id=fixtures["purchase_intent"].intent_id,
        core_corridor_overrides=core_corridor_overrides,
    )
    for reason in client_core_reasons:
        _append_reason(reasons, reason)
    if not client_core_valid:
        _append_reason(reasons, REASON_CORE_CORRIDOR_GUARD_VALIDATION_FAILED)
    _merge_report_reasons(
        reasons,
        human_gate_report,
        human_report,
        purchase_report,
    )

    bank_gate_report = contracts.validate_root_phase_gate_v01(
        fixtures["bank_gate"],
    )
    auth_report = contracts.validate_bank_payment_authorization_ref_v01(
        fixtures["purchase_intent"],
        fixtures["authorization_ref"],
        contract_context=context,
    )
    bank_core_valid, bank_core_reasons = _validate_core_guard(
        phase_id=PHASE_BANK_PAYMENT_AUTHORIZATION,
        packet_id=fixtures["authorization_ref"].authorization_ref_id,
        core_corridor_overrides=core_corridor_overrides,
    )
    for reason in bank_core_reasons:
        _append_reason(reasons, reason)
    if not bank_core_valid:
        _append_reason(reasons, REASON_CORE_CORRIDOR_GUARD_VALIDATION_FAILED)
    _merge_report_reasons(reasons, bank_gate_report, auth_report)

    airline_gate_report = contracts.validate_root_phase_gate_v01(
        fixtures["airline_ticket_gate"],
    )
    ticket_intent_report = contracts.validate_airline_ticket_issue_intent_v01(
        fixtures["offer_packet"],
        fixtures["hold_packet"],
        fixtures["hold_receipt"],
        fixtures["purchase_intent"],
        fixtures["authorization_ref"],
        fixtures["ticket_issue_intent"],
        contract_context=context,
    )
    ticket_receipt_report = contracts.validate_mock_ticket_receipt_v01(
        fixtures["ticket_issue_intent"],
        fixtures["ticket_receipt"],
        contract_context=context,
    )
    ticket_core_valid, ticket_core_reasons = _validate_core_guard(
        phase_id=PHASE_AIRLINE_TICKET_ISSUE,
        packet_id=fixtures["ticket_issue_intent"].intent_id,
        core_corridor_overrides=core_corridor_overrides,
    )
    for reason in ticket_core_reasons:
        _append_reason(reasons, reason)
    if not ticket_core_valid:
        _append_reason(reasons, REASON_CORE_CORRIDOR_GUARD_VALIDATION_FAILED)
    _merge_report_reasons(
        reasons,
        airline_gate_report,
        ticket_intent_report,
        ticket_receipt_report,
    )

    completion_gate_report = contracts.validate_root_phase_gate_v01(
        fixtures["completion_gate"],
    )
    purchase_receipt_report = contracts.validate_mock_purchase_receipt_v01(
        fixtures["purchase_intent"],
        fixtures["authorization_ref"],
        fixtures["ticket_receipt"],
        fixtures["purchase_receipt"],
    )
    completion_core_valid, completion_core_reasons = _validate_core_guard(
        phase_id=PHASE_CLIENT_COMPLETION,
        packet_id=fixtures["purchase_receipt"].receipt_id,
        core_corridor_overrides=core_corridor_overrides,
    )
    for reason in completion_core_reasons:
        _append_reason(reasons, reason)
    if not completion_core_valid:
        _append_reason(reasons, REASON_CORE_CORRIDOR_GUARD_VALIDATION_FAILED)
    _merge_report_reasons(reasons, completion_gate_report, purchase_receipt_report)

    return not reasons, tuple(reasons)


def validate_airline_ticket_purchase_corridor_report_against_fixture_bundle_v01(
    fixtures: Mapping[str, Any],
    report: AirlineTicketPurchaseCorridorRunReportV01,
    *,
    contract_context: (
        contracts.AirlineTicketPurchaseContractContextV01 | None
    ) = None,
) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    context = _contract_context(contract_context or report.contract_context)
    fixture_transaction_ids = tuple(
        getattr(artifact, "transaction_id")
        for artifact in fixtures.values()
        if hasattr(artifact, "transaction_id")
    )
    if (
        report.transaction_id != contracts.TRANSACTION_ID
        or report.contract_context != context
        or any(transaction_id != report.transaction_id for transaction_id in fixture_transaction_ids)
        or any(phase.transaction_id != report.transaction_id for phase in report.phase_results)
        or any(transition.transaction_id != report.transaction_id for transition in report.transitions)
    ):
        _append_reason(reasons, REASON_FIXTURE_REPORT_TRANSACTION_MISMATCH)

    phase_results = tuple(report.phase_results)
    if (
        len(phase_results) != 5
        or tuple(phase.phase_id for phase in phase_results) != PHASE_ORDER
    ):
        _append_reason(reasons, "phase_order_mismatch")

    expected_roots = {
        PHASE_AIRLINE_OFFER_HOLD: fixtures["airline_offer_hold_gate"].root_id,
        PHASE_CLIENT_PURCHASE_INTENT: fixtures["client_purchase_gate"].root_id,
        PHASE_BANK_PAYMENT_AUTHORIZATION: fixtures["bank_gate"].root_id,
        PHASE_AIRLINE_TICKET_ISSUE: fixtures["airline_ticket_gate"].root_id,
        PHASE_CLIENT_COMPLETION: fixtures["completion_gate"].root_id,
    }
    expected_evidence = {
        PHASE_AIRLINE_OFFER_HOLD: (
            fixtures["offer_packet"].packet_id,
            fixtures["hold_packet"].packet_id,
            fixtures["hold_receipt"].receipt_id,
        ),
        PHASE_CLIENT_PURCHASE_INTENT: (
            fixtures["human_approval"].approval_ref,
            fixtures["purchase_intent"].intent_id,
        ),
        PHASE_BANK_PAYMENT_AUTHORIZATION: (
            fixtures["authorization_ref"].authorization_ref_id,
        ),
        PHASE_AIRLINE_TICKET_ISSUE: (
            fixtures["ticket_issue_intent"].intent_id,
            fixtures["ticket_receipt"].receipt_id,
        ),
        PHASE_CLIENT_COMPLETION: (
            fixtures["purchase_receipt"].receipt_id,
        ),
    }

    for phase in phase_results:
        if phase.relevant_root_id != expected_roots.get(phase.phase_id):
            _append_reason(reasons, REASON_PHASE_FIXTURE_ROOT_MISMATCH)
        if (
            phase.phase_status == STATUS_PASS
            and phase.evidence_refs_observed != expected_evidence.get(phase.phase_id)
        ):
            _append_reason(reasons, REASON_PHASE_EVIDENCE_REFS_MISMATCH)
        if phase.authority_transferred:
            _append_reason(reasons, contracts.REASON_CROSS_ROOT_AUTHORITY_TRANSFER)
        if phase.runtime_receipt_created:
            _append_reason(reasons, "runtime_receipt_created")
        if phase.real_world_effects_count != 0:
            _append_reason(reasons, contracts.REASON_NONZERO_REAL_WORLD_EFFECTS)

    if any(transition.authority_transferred for transition in report.transitions):
        _append_reason(reasons, contracts.REASON_CROSS_ROOT_AUTHORITY_TRANSFER)
    if dict(report.artifact_validation_summary) != _artifact_validation_summary(
        phase_results,
    ):
        _append_reason(reasons, REASON_ARTIFACT_VALIDATION_SUMMARY_MISMATCH)
    for key in (
        "runtime_receipts_created_count",
        "runtime_packets_created_count",
        "real_world_effects_count",
    ):
        if report.counter_table.get(key) != 0:
            _append_reason(reasons, REASON_COUNTER_TABLE_MISMATCH)

    if reasons:
        _append_reason(reasons, REASON_FIXTURE_REPORT_BINDING_FAILED)
    return not reasons, tuple(reasons)


def _build_transitions(
    phase_results: tuple[AirlineCorridorPhaseResultV01, ...],
) -> tuple[AirlineCorridorTransitionV01, ...]:
    transitions: list[AirlineCorridorTransitionV01] = []
    for index, source in enumerate(phase_results[:-1], start=1):
        target = phase_results[index]
        source_passed = source.phase_status == STATUS_PASS
        dependency_satisfied = source_passed and target.phase_status != STATUS_NOT_RUN
        transition_status = (
            STATUS_PASS
            if dependency_satisfied
            else STATUS_NOT_RUN
            if source.phase_status == STATUS_NOT_RUN or target.phase_status == STATUS_NOT_RUN
            else STATUS_FAIL_CLOSED
        )
        reasons: tuple[str, ...] = ()
        if transition_status != STATUS_PASS:
            reasons = (f"dependency_not_satisfied:{source.phase_id}",)
        transitions.append(
            AirlineCorridorTransitionV01(
                transition_index=index,
                from_phase_id=source.phase_id,
                to_phase_id=target.phase_id,
                transaction_id=contracts.TRANSACTION_ID,
                source_phase_passed=source_passed,
                dependency_satisfied=dependency_satisfied,
                authority_transferred=False,
                semantic_reasoning_restarted=False,
                transition_status=transition_status,
                reason_codes=reasons,
            ),
        )
    return tuple(transitions)


def _root_boundary_summary() -> tuple[Mapping[str, Any], ...]:
    return (
        {
            "root_id": contracts.CLIENT_ROOT_ID,
            "may": ("authorize ClientPurchaseIntent", "observe completion"),
            "cannot": ("issue ticket", "authorize BankRoot payment"),
        },
        {
            "root_id": contracts.AIRLINE_ROOT_ID,
            "may": ("authorize offer/hold", "authorize mock ticket issue"),
            "cannot": ("authorize BankRoot payment",),
        },
        {
            "root_id": contracts.BANK_ROOT_ID,
            "may": ("authorize mock payment evidence",),
            "cannot": ("issue airline ticket", "create Airline order"),
        },
        {
            "root_id": "shared_summary",
            "may": ("aggregate observed side statuses",),
            "cannot": (
                "be fourth Root",
                "override side Root",
                "create permission",
                "create FinalOutput",
            ),
        },
    )


def _artifact_validation_summary(
    phase_results: tuple[AirlineCorridorPhaseResultV01, ...],
) -> dict[str, Any]:
    phase_statuses = {phase.phase_id: phase.phase_status for phase in phase_results}
    all_pass = all(phase.phase_status == STATUS_PASS for phase in phase_results)
    return {
        "state_sequence": STATE_SEQUENCE,
        "phase_statuses": phase_statuses,
        "one_transaction_id": contracts.TRANSACTION_ID,
        "no_state_skipped": all_pass,
        "later_phase_cannot_repair_earlier_failure": True,
        "offer_packet_validated": (
            phase_statuses.get(PHASE_AIRLINE_OFFER_HOLD) == STATUS_PASS
        ),
        "hold_packet_validated": (
            phase_statuses.get(PHASE_AIRLINE_OFFER_HOLD) == STATUS_PASS
        ),
        "offer_hold_receipt_validated": (
            phase_statuses.get(PHASE_AIRLINE_OFFER_HOLD) == STATUS_PASS
        ),
        "purchase_intent_validated": (
            phase_statuses.get(PHASE_CLIENT_PURCHASE_INTENT) == STATUS_PASS
        ),
        "payment_authorization_ref_validated": (
            phase_statuses.get(PHASE_BANK_PAYMENT_AUTHORIZATION) == STATUS_PASS
        ),
        "ticket_issue_intent_validated": (
            phase_statuses.get(PHASE_AIRLINE_TICKET_ISSUE) == STATUS_PASS
        ),
        "mock_ticket_receipt_validated": (
            phase_statuses.get(PHASE_AIRLINE_TICKET_ISSUE) == STATUS_PASS
        ),
        "mock_purchase_receipt_validated": (
            phase_statuses.get(PHASE_CLIENT_COMPLETION) == STATUS_PASS
        ),
    }


def _receipt_boundary_summary(
    phase_results: tuple[AirlineCorridorPhaseResultV01, ...],
) -> dict[str, Any]:
    return {
        "fixture_receipts_observed_count": 3,
        "runtime_receipts_created_count": sum(
            1 for phase in phase_results if phase.runtime_receipt_created
        ),
        "receipts_are_evidence_only": True,
        "offer_hold_receipt_is_fixture": True,
        "mock_ticket_receipt_is_fixture": True,
        "mock_purchase_receipt_is_fixture": True,
    }


def _counter_table(
    phase_results: tuple[AirlineCorridorPhaseResultV01, ...],
    transitions: tuple[AirlineCorridorTransitionV01, ...],
) -> dict[str, int]:
    phase_statuses = {phase.phase_id: phase.phase_status for phase in phase_results}
    phase_pass_count = sum(1 for phase in phase_results if phase.phase_status == STATUS_PASS)
    phase_fail_count = sum(
        1 for phase in phase_results if phase.phase_status == STATUS_FAIL_CLOSED
    )
    return {
        "corridor_run_count": 1,
        "phase_count": len(phase_results),
        "phase_pass_count": phase_pass_count,
        "phase_fail_count": phase_fail_count,
        "transition_count": len(transitions),
        "transition_pass_count": sum(
            1 for transition in transitions if transition.transition_status == STATUS_PASS
        ),
        "root_phase_gate_validation_count": sum(
            1 for phase in phase_results if phase.root_gate_validated
        ),
        "core_no_post_root_reasoning_validation_count": sum(
            1
            for phase in phase_results
            if phase.core_corridor_guard_validated
            or phase.phase_status == STATUS_FAIL_CLOSED
        ),
        "domain_contract_validation_group_count": sum(
            1 for phase in phase_results if phase.domain_contracts_validated
        ),
        "offer_packet_validated_count": int(
            phase_statuses.get(PHASE_AIRLINE_OFFER_HOLD) == STATUS_PASS,
        ),
        "hold_packet_validated_count": int(
            phase_statuses.get(PHASE_AIRLINE_OFFER_HOLD) == STATUS_PASS,
        ),
        "offer_hold_receipt_validated_count": int(
            phase_statuses.get(PHASE_AIRLINE_OFFER_HOLD) == STATUS_PASS,
        ),
        "purchase_intent_validated_count": int(
            phase_statuses.get(PHASE_CLIENT_PURCHASE_INTENT) == STATUS_PASS,
        ),
        "payment_authorization_ref_validated_count": int(
            phase_statuses.get(PHASE_BANK_PAYMENT_AUTHORIZATION) == STATUS_PASS,
        ),
        "ticket_issue_intent_validated_count": int(
            phase_statuses.get(PHASE_AIRLINE_TICKET_ISSUE) == STATUS_PASS,
        ),
        "mock_ticket_receipt_validated_count": int(
            phase_statuses.get(PHASE_AIRLINE_TICKET_ISSUE) == STATUS_PASS,
        ),
        "mock_purchase_receipt_validated_count": int(
            phase_statuses.get(PHASE_CLIENT_COMPLETION) == STATUS_PASS,
        ),
        "fixture_receipts_observed_count": 3,
        "runtime_receipts_created_count": 0,
        "runtime_packets_created_count": 0,
        "adapter_execution_count": 0,
        "provider_called_count": 0,
        "network_used_count": 0,
        "gemini_called_count": 0,
        "real_airline_api_called_count": 0,
        "real_bank_api_called_count": 0,
        "real_gds_api_called_count": 0,
        "real_payment_executed_count": 0,
        "real_ticket_issued_count": 0,
        "real_booking_created_count": 0,
        "real_world_effects_count": sum(
            phase.real_world_effects_count for phase in phase_results
        ),
        "client_root_phase_gate_pass_count": sum(
            1
            for phase in phase_results
            if phase.relevant_root_id == contracts.CLIENT_ROOT_ID
            and phase.root_gate_validated
        ),
        "airline_root_phase_gate_pass_count": sum(
            1
            for phase in phase_results
            if phase.relevant_root_id == contracts.AIRLINE_ROOT_ID
            and phase.root_gate_validated
        ),
        "bank_root_phase_gate_pass_count": sum(
            1
            for phase in phase_results
            if phase.relevant_root_id == contracts.BANK_ROOT_ID
            and phase.root_gate_validated
        ),
        "shared_root_created_count": 0,
        "fourth_root_created_count": 0,
        "cross_root_authority_transfer_count": sum(
            1 for phase in phase_results if phase.authority_transferred
        ),
        "core_delegated_check_count": 2,
        "domain_projection_check_count": 6,
        "supplier_specific_core_fixture_used_count": 0,
        "dishonest_field_mapping_count": 0,
        "second_universal_authority_engine_created_count": 0,
        "core_imports_airline_domain_count": 0,
    }


def _run_airline_ticket_purchase_corridor_state_machine_v01(
    fixtures: Mapping[str, Any] | None = None,
    *,
    core_corridor_overrides: Mapping[str, Mapping[str, Any]] | None = None,
    contract_context: (
        contracts.AirlineTicketPurchaseContractContextV01 | None
    ) = None,
) -> AirlineTicketPurchaseCorridorRunReportV01:
    fixture_bundle = _fixture_bundle_from_input(fixtures)
    context = _contract_context(contract_context)
    phase_results: list[AirlineCorridorPhaseResultV01] = []
    failed_phase_id = ""
    return_to_root_id = ""

    for phase_index, phase_id in enumerate(PHASE_ORDER, start=1):
        if failed_phase_id:
            phase_results.append(
                _not_run_phase_result(
                    phase_index=phase_index,
                    phase_id=phase_id,
                    relevant_root_id=PHASE_ROOTS[phase_id],
                    blocked_by_phase_id=failed_phase_id,
                ),
            )
            continue

        phase_result = PHASE_VALIDATORS[phase_id](
            fixture_bundle,
            core_corridor_overrides,
            context,
        )
        phase_results.append(phase_result)
        if phase_result.phase_status != STATUS_PASS:
            failed_phase_id = phase_id
            return_to_root_id = phase_result.relevant_root_id

    phase_tuple = tuple(phase_results)
    transitions = _build_transitions(phase_tuple)
    final_status = STATUS_PASS if not failed_phase_id else STATUS_FAIL_CLOSED
    counter_table = _counter_table(phase_tuple, transitions)
    validation_errors = tuple(
        reason
        for phase in phase_tuple
        if phase.phase_status == STATUS_FAIL_CLOSED
        for reason in phase.reason_codes
    )
    return AirlineTicketPurchaseCorridorRunReportV01(
        run_id=RUN_ID,
        slice_id=SLICE_ID,
        transaction_id=contracts.TRANSACTION_ID,
        final_status=final_status,
        failed_phase_id=failed_phase_id,
        return_to_root_id=return_to_root_id,
        phase_results=phase_tuple,
        transitions=transitions,
        core_domain_delegation_matrix=_core_domain_delegation_matrix(),
        artifact_validation_summary=_artifact_validation_summary(phase_tuple),
        root_boundary_summary=_root_boundary_summary(),
        receipt_boundary_summary=_receipt_boundary_summary(phase_tuple),
        counter_table=counter_table,
        contract_context=context,
        validation_errors=validation_errors,
        next_gate=NEXT_GATE,
    )


def build_valid_airline_ticket_purchase_corridor_run_v01() -> (
    AirlineTicketPurchaseCorridorRunReportV01
):
    return _run_airline_ticket_purchase_corridor_state_machine_v01()


def validate_airline_ticket_purchase_corridor_run_v01(
    report: AirlineTicketPurchaseCorridorRunReportV01,
) -> tuple[bool, tuple[str, ...]]:
    errors: list[str] = []
    if not isinstance(
        report.contract_context,
        contracts.AirlineTicketPurchaseContractContextV01,
    ):
        _append_reason(errors, REASON_FIXTURE_REPORT_BINDING_FAILED)
    elif report.contract_context.transaction_id != report.transaction_id:
        _append_reason(errors, contracts.REASON_WRONG_TRANSACTION_ID)
    if report.run_id != RUN_ID:
        _append_reason(errors, "run_id_mismatch")
    if report.slice_id != SLICE_ID:
        _append_reason(errors, "slice_id_mismatch")
    if report.transaction_id != contracts.TRANSACTION_ID:
        _append_reason(errors, contracts.REASON_WRONG_TRANSACTION_ID)
    if report.next_gate != NEXT_GATE:
        _append_reason(errors, "next_gate_mismatch")

    phase_results = tuple(report.phase_results)
    transitions = tuple(report.transitions)
    phase_ids = tuple(phase.phase_id for phase in phase_results)
    if len(phase_results) != 5 or phase_ids != PHASE_ORDER:
        _append_reason(errors, "phase_order_mismatch")

    for expected_index, phase in enumerate(phase_results, start=1):
        if phase.phase_index != expected_index:
            _append_reason(errors, "phase_index_mismatch")
        if phase.transaction_id != contracts.TRANSACTION_ID:
            _append_reason(errors, contracts.REASON_MIXED_TRANSACTION_ID)
        expected_root = PHASE_ROOTS.get(phase.phase_id)
        if expected_root is not None and phase.relevant_root_id != expected_root:
            _append_reason(errors, REASON_PHASE_ROOT_MISMATCH)
        if phase.authority_transferred:
            _append_reason(errors, contracts.REASON_CROSS_ROOT_AUTHORITY_TRANSFER)
        if phase.runtime_receipt_created:
            _append_reason(errors, "runtime_receipt_created")
        if phase.provider_called or phase.network_used or phase.gemini_called:
            _append_reason(errors, "provider_or_network_called")
        if phase.real_world_effects_count != 0:
            _append_reason(errors, contracts.REASON_NONZERO_REAL_WORLD_EFFECTS)
        if phase.phase_status == STATUS_PASS:
            if phase.return_to_relevant_root is not False:
                _append_reason(errors, "phase_derived_field_mismatch")
            if phase.later_phases_allowed is not True:
                _append_reason(errors, "phase_derived_field_mismatch")
        elif phase.phase_status == STATUS_FAIL_CLOSED:
            if phase.return_to_relevant_root is not True:
                _append_reason(errors, "phase_derived_field_mismatch")
            if phase.later_phases_allowed is not False:
                _append_reason(errors, "phase_derived_field_mismatch")
        elif phase.phase_status == STATUS_NOT_RUN:
            if phase.return_to_relevant_root is not False:
                _append_reason(errors, "phase_derived_field_mismatch")
            if phase.later_phases_allowed is not False:
                _append_reason(errors, "phase_derived_field_mismatch")
        else:
            _append_reason(errors, "phase_status_mismatch")

    if len(transitions) != 4:
        _append_reason(errors, REASON_TRANSITION_SHAPE_MISMATCH)
    for expected_index, transition in enumerate(transitions, start=1):
        if transition.transition_index != expected_index:
            _append_reason(errors, REASON_TRANSITION_SHAPE_MISMATCH)
        if transition.transaction_id != contracts.TRANSACTION_ID:
            _append_reason(errors, contracts.REASON_MIXED_TRANSACTION_ID)
        if transition.authority_transferred:
            _append_reason(errors, contracts.REASON_CROSS_ROOT_AUTHORITY_TRANSFER)
        if transition.semantic_reasoning_restarted:
            _append_reason(
                errors,
                contracts.REASON_POST_ROOT_REASONING_RESTART_FORBIDDEN,
            )
        if expected_index <= 4:
            expected_from = PHASE_ORDER[expected_index - 1]
            expected_to = PHASE_ORDER[expected_index]
            if (
                transition.from_phase_id != expected_from
                or transition.to_phase_id != expected_to
            ):
                _append_reason(errors, REASON_TRANSITION_SHAPE_MISMATCH)
            if len(phase_results) == 5:
                source = phase_results[expected_index - 1]
                target = phase_results[expected_index]
                expected_source_passed = source.phase_status == STATUS_PASS
                expected_dependency_satisfied = (
                    expected_source_passed
                    and target.phase_status != STATUS_NOT_RUN
                )
                if transition.source_phase_passed != expected_source_passed:
                    _append_reason(errors, REASON_TRANSITION_SHAPE_MISMATCH)
                if transition.dependency_satisfied != expected_dependency_satisfied:
                    _append_reason(errors, REASON_TRANSITION_SHAPE_MISMATCH)
                if (
                    source.phase_status == STATUS_PASS
                    and target.phase_status != STATUS_NOT_RUN
                    and transition.transition_status != STATUS_PASS
                ):
                    _append_reason(errors, REASON_TRANSITION_SHAPE_MISMATCH)
                if (
                    source.phase_status != STATUS_PASS
                    or target.phase_status == STATUS_NOT_RUN
                ) and transition.transition_status == STATUS_PASS:
                    _append_reason(errors, REASON_TRANSITION_SHAPE_MISMATCH)
                expected_status = (
                    STATUS_PASS
                    if expected_dependency_satisfied
                    else STATUS_NOT_RUN
                    if (
                        source.phase_status == STATUS_NOT_RUN
                        or target.phase_status == STATUS_NOT_RUN
                    )
                    else STATUS_FAIL_CLOSED
                )
                if transition.transition_status != expected_status:
                    _append_reason(errors, REASON_TRANSITION_SHAPE_MISMATCH)
                if transition.transition_status == STATUS_PASS:
                    if transition.reason_codes != ():
                        _append_reason(errors, REASON_TRANSITION_SHAPE_MISMATCH)
                elif transition.reason_codes != (
                    f"dependency_not_satisfied:{source.phase_id}",
                ):
                    _append_reason(errors, REASON_TRANSITION_SHAPE_MISMATCH)

    failed_phases = [
        phase for phase in phase_results if phase.phase_status == STATUS_FAIL_CLOSED
    ]
    if report.final_status == STATUS_PASS:
        if report.failed_phase_id:
            _append_reason(errors, REASON_FAILED_PHASE_ID_MISMATCH)
        if report.return_to_root_id:
            _append_reason(errors, REASON_RETURN_TO_ROOT_ID_MISMATCH)
        if any(phase.phase_status != STATUS_PASS for phase in phase_results):
            _append_reason(errors, "pass_report_contains_failed_or_unrun_phase")
        if any(not phase.root_gate_validated for phase in phase_results):
            _append_reason(errors, REASON_ROOT_PHASE_GATE_VALIDATION_FAILED)
        if any(not phase.core_corridor_guard_validated for phase in phase_results):
            _append_reason(errors, REASON_CORE_CORRIDOR_GUARD_VALIDATION_FAILED)
        if any(not phase.domain_contracts_validated for phase in phase_results):
            _append_reason(errors, REASON_DOMAIN_CONTRACT_VALIDATION_FAILED)
        if any(
            transition.transition_status != STATUS_PASS for transition in transitions
        ):
            _append_reason(errors, REASON_TRANSITION_SHAPE_MISMATCH)
        if report.validation_errors:
            _append_reason(errors, "validation_errors_mismatch")
    elif report.final_status == STATUS_FAIL_CLOSED:
        if len(failed_phases) != 1:
            _append_reason(errors, "failed_phase_count_mismatch")
        if failed_phases:
            failed_phase = failed_phases[0]
            failed_index = failed_phase.phase_index
            if report.failed_phase_id != failed_phase.phase_id:
                _append_reason(errors, REASON_FAILED_PHASE_ID_MISMATCH)
            if report.return_to_root_id != PHASE_ROOTS[failed_phase.phase_id]:
                _append_reason(errors, REASON_RETURN_TO_ROOT_ID_MISMATCH)
            later_phases = [
                phase for phase in phase_results if phase.phase_index > failed_index
            ]
            if any(phase.phase_status != STATUS_NOT_RUN for phase in later_phases):
                _append_reason(errors, "later_phase_status_mismatch")
            if any(phase.phase_status == STATUS_PASS for phase in later_phases):
                _append_reason(errors, "later_phase_repaired_failure")
            if report.validation_errors != failed_phase.reason_codes:
                _append_reason(errors, "validation_errors_mismatch")
    else:
        _append_reason(errors, "final_status_mismatch")

    expected_counter_table = _counter_table(phase_results, transitions)
    if dict(report.counter_table) != expected_counter_table:
        _append_reason(errors, REASON_COUNTER_TABLE_MISMATCH)
    required_zero_counter_keys = (
        "runtime_receipts_created_count",
        "runtime_packets_created_count",
        "adapter_execution_count",
        "shared_root_created_count",
        "fourth_root_created_count",
        "cross_root_authority_transfer_count",
        "provider_called_count",
        "network_used_count",
        "gemini_called_count",
        "real_airline_api_called_count",
        "real_bank_api_called_count",
        "real_gds_api_called_count",
        "real_payment_executed_count",
        "real_ticket_issued_count",
        "real_booking_created_count",
        "real_world_effects_count",
        "supplier_specific_core_fixture_used_count",
        "dishonest_field_mapping_count",
        "second_universal_authority_engine_created_count",
        "core_imports_airline_domain_count",
    )
    if report.counter_table.get("corridor_run_count") != 1:
        _append_reason(errors, REASON_COUNTER_TABLE_MISMATCH)
    if report.counter_table.get("phase_count") != 5:
        _append_reason(errors, REASON_COUNTER_TABLE_MISMATCH)
    if report.counter_table.get("transition_count") != 4:
        _append_reason(errors, REASON_COUNTER_TABLE_MISMATCH)
    if report.counter_table.get("fixture_receipts_observed_count") != 3:
        _append_reason(errors, REASON_COUNTER_TABLE_MISMATCH)
    for key in required_zero_counter_keys:
        if report.counter_table.get(key) != 0:
            _append_reason(errors, REASON_COUNTER_TABLE_MISMATCH)

    matrix = tuple(report.core_domain_delegation_matrix)
    if len(matrix) != 8:
        _append_reason(errors, "delegation_matrix_mismatch")
    if sum(1 for row in matrix if row.directly_delegated_to_core) != 2:
        _append_reason(errors, "delegation_matrix_mismatch")
    if report.counter_table.get("supplier_specific_core_fixture_used_count") != 0:
        _append_reason(errors, "supplier_specific_core_fixture_used")
    if report.counter_table.get("dishonest_field_mapping_count") != 0:
        _append_reason(errors, "dishonest_field_mapping")
    if report.counter_table.get("second_universal_authority_engine_created_count") != 0:
        _append_reason(errors, "second_universal_authority_engine_created")
    if report.counter_table.get("core_imports_airline_domain_count") != 0:
        _append_reason(errors, "core_imports_airline_domain")

    receipt_summary = report.receipt_boundary_summary
    if receipt_summary.get("fixture_receipts_observed_count") != 3:
        _append_reason(errors, "receipt_boundary_mismatch")
    if receipt_summary.get("runtime_receipts_created_count") != 0:
        _append_reason(errors, "receipt_boundary_mismatch")
    for key in (
        "offer_hold_receipt_is_fixture",
        "mock_ticket_receipt_is_fixture",
        "mock_purchase_receipt_is_fixture",
        "receipts_are_evidence_only",
    ):
        if receipt_summary.get(key) is not True:
            _append_reason(errors, "receipt_boundary_mismatch")
    return not errors, tuple(errors)


def collect_airline_ticket_purchase_corridor_state_machine_v01(
    *,
    fixtures: Mapping[str, Any] | None = None,
    core_corridor_overrides: Mapping[str, Mapping[str, Any]] | None = None,
    contract_context: (
        contracts.AirlineTicketPurchaseContractContextV01 | None
    ) = None,
) -> AirlineTicketPurchaseCorridorRunReportV01:
    return collect_airline_ticket_purchase_corridor_execution_result_v01(
        fixtures=fixtures,
        core_corridor_overrides=core_corridor_overrides,
        contract_context=contract_context,
    ).report


def collect_airline_ticket_purchase_corridor_execution_result_v01(
    *,
    fixtures: Mapping[str, Any] | None = None,
    core_corridor_overrides: Mapping[str, Mapping[str, Any]] | None = None,
    contract_context: (
        contracts.AirlineTicketPurchaseContractContextV01 | None
    ) = None,
) -> AirlineTicketPurchaseCorridorExecutionResultV01:
    fixture_bundle = _fixture_bundle_from_input(fixtures)
    report = _run_airline_ticket_purchase_corridor_state_machine_v01(
        fixture_bundle,
        core_corridor_overrides=core_corridor_overrides,
        contract_context=contract_context,
    )
    return AirlineTicketPurchaseCorridorExecutionResultV01(
        report=report,
        contract_context=report.contract_context,
        offer_packet=fixture_bundle["offer_packet"],
        hold_packet=fixture_bundle["hold_packet"],
        hold_receipt=fixture_bundle["hold_receipt"],
        purchase_approval_evidence=fixture_bundle["human_approval"],
        purchase_intent=fixture_bundle["purchase_intent"],
        payment_authorization_ref=fixture_bundle["authorization_ref"],
        ticket_issue_intent=fixture_bundle["ticket_issue_intent"],
        mock_ticket_receipt=fixture_bundle["ticket_receipt"],
        mock_purchase_receipt=fixture_bundle["purchase_receipt"],
    )


def render_airline_ticket_purchase_corridor_state_machine_v01(
    report: AirlineTicketPurchaseCorridorRunReportV01,
) -> str:
    lines = [
        "[AIRLINE TICKET/PURCHASE CORRIDOR STATE MACHINE]",
        f"run_id: {report.run_id}",
        f"slice_id: {report.slice_id}",
        f"transaction_id: {report.transaction_id}",
        "",
        "[ROOT-CENTERED SIDE-LOCAL PHASES]",
    ]
    for phase in report.phase_results:
        lines.append(
            f"{phase.phase_index}. {phase.phase_id}: "
            f"{phase.phase_status} root={phase.relevant_root_id}",
        )
    lines.extend(
        [
            "",
            "[CORE / DOMAIN DELEGATION]",
            f"core_delegated_check_count: {report.counter_table['core_delegated_check_count']}",
            f"domain_projection_check_count: {report.counter_table['domain_projection_check_count']}",
            "validate_corridor_no_post_root_reasoning_v01 invoked for phase guards",
            "",
            "[COUNTER TABLE]",
        ],
    )
    for key in sorted(report.counter_table):
        lines.append(f"{key}: {report.counter_table[key]}")
    lines.extend(
        [
            "",
            "[FINAL STATUS]",
            f"final_status: {report.final_status}",
            f"failed_phase_id: {report.failed_phase_id or 'none'}",
        ],
    )
    return "\n".join(lines)


def run_airline_ticket_purchase_corridor_state_machine_v01() -> str:
    return render_airline_ticket_purchase_corridor_state_machine_v01(
        collect_airline_ticket_purchase_corridor_state_machine_v01(),
    )
