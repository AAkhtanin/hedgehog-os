from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from pathlib import Path
from typing import Any, Mapping

from demo import run_tri_party_airline_ticket_purchase_mock_e2e_v01 as runner
from hedgehog.domains.airline import (
    semantic_to_contract_binding_v01 as binding,
)
from hedgehog.domains.airline import (
    semantic_to_contract_causal_runtime_v01 as causal_runtime,
)


def _report() -> dict[str, object]:
    return runner.collect_tri_party_airline_ticket_purchase_mock_e2e_v01()


def _proposal_payload(request: Mapping[str, Any], offer_id: str) -> dict[str, Any]:
    return {
        "proposal_id": f"semantic_offer_selection_proposal:{offer_id}",
        "transaction_id": request["transaction_id"],
        "actor_id": request["actor_id"],
        "source_selection_input_id": request["source_selection_input_id"],
        "source_bsep_projection_ref": request["source_bsep_projection_ref"],
        "source_client_constraint_set_id": request["source_client_constraint_set_id"],
        "source_candidate_set_snapshot_id": request[
            "source_candidate_set_snapshot_id"
        ],
        "source_candidate_set_digest": request["source_candidate_set_digest"],
        "candidate_set_ref": request["source_candidate_set_ref"],
        "recommended_offer_id": offer_id,
        "ranked_offer_ids": (offer_id,),
        "decision_factors": ("deterministic_test_semantics",),
        "preference_matches": ("explicit_offer_from_test_provider",),
        "uncertainty_notes": ("requires_client_root_review",),
        "requires_root_review": True,
        "semantic_summary": "Test-only injected advisory semantics.",
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


def _reviewer_payload(request: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "response_id": (
            f"canonical_actor_output:{request['actor_id']}:"
            f"{request['proposed_offer_id']}"
        ),
        "transaction_id": request["transaction_id"],
        "actor_id": request["actor_id"],
        "source_request_id": request["request_id"],
        "source_selection_input_id": request["source_selection_input_id"],
        "source_candidate_set_snapshot_id": request[
            "source_candidate_set_snapshot_id"
        ],
        "source_candidate_set_digest": request["source_candidate_set_digest"],
        "reviewed_offer_id": request["proposed_offer_id"],
        "review_role": request["actor_role"],
        "review_status": binding.STATUS_PASS,
        "semantic_factors": ("review_supports_explicit_offer",),
        "blocking_conflicts": (),
        "supports_proposed_offer": True,
        "validation_status": binding.STATUS_PASS,
        "raw_output_used": False,
        "authority_created": False,
        "permission_created": False,
        "real_world_effects_count": 0,
    }


def _semantic_provider_for_offer(
    offer_id: str,
) -> causal_runtime.AirlineInjectedSemanticProviderV01:
    def provider(actor_id: str, request: Mapping[str, Any]) -> Mapping[str, Any]:
        if actor_id == binding.ACTOR_CLIENT_PURCHASE_INTENT_REVIEWER:
            return _proposal_payload(request, offer_id)
        return _reviewer_payload(request)

    return provider


def _causal_run_for_offer(
    offer_id: str,
) -> causal_runtime.AirlineSemanticCausalRunReportV01:
    constraints = (
        binding.build_client_constraints_preference_b_v01()
        if offer_id == binding.OFFER_B_ID
        else binding.build_client_constraints_preference_a_v01()
    )
    return causal_runtime.collect_airline_semantic_to_contract_causal_run_v01(
        scenario_id=f"deterministic_runner:{offer_id}",
        constraints=constraints,
        semantic_provider=_semantic_provider_for_offer(offer_id),
    )


def test_airline_slice_b_collects_pass_report() -> None:
    report = _report()

    assert report["final_status"] == runner.STATUS_PASS
    assert report["transaction_id"] == runner.TRANSACTION_ID
    assert set(report["participants"]) == {"ClientRoot", "AirlineRoot", "BankRoot"}
    assert report["client_root_view"]
    assert report["airline_root_view"]
    assert report["bank_root_view"]
    assert report["validation_errors"] == ()


def test_airline_slice_b_one_transaction_shared_ledger() -> None:
    report = _report()
    ledger = report["shared_transaction_ledger"]

    assert {row["transaction_id"] for row in ledger} == {runner.TRANSACTION_ID}
    assert report["counter_table"]["shared_transaction_id_count"] == 1
    assert report["counter_table"]["shared_ledger_entry_count"] == 15

    mutated = deepcopy(report)
    mutated["shared_transaction_ledger"][0]["transaction_id"] = "tri_airline_purchase:wrong"
    errors = runner._validate_report(mutated)
    assert "ledger_transaction_id_mismatch" in errors


def test_airline_slice_b_three_root_boundaries() -> None:
    report = _report()
    boundaries = {row["boundary"]: row for row in report["root_boundary_matrix"]}

    assert boundaries["ClientRoot cannot issue ticket."]["violation_count"] == 0
    assert boundaries[
        "AirlineRoot cannot authorize client payment."
    ]["violation_count"] == 0
    assert boundaries["BankRoot cannot create airline ticket."]["violation_count"] == 0
    assert boundaries["No Root becomes God over the others."]["boundary_preserved"] is True
    assert all(row["violation_count"] == 0 for row in boundaries.values())


def test_airline_slice_b_receipts_are_evidence_only() -> None:
    report = _report()
    fixtures = report["mock_protocol_fixtures"]
    boundaries = {row["boundary"]: row for row in report["receipt_boundary_matrix"]}

    assert fixtures["AirlineOfferHoldReceiptV01"]["evidence_only"] is True
    assert fixtures["BankPaymentAuthorizationReceiptV01"]["evidence_only"] is True
    assert fixtures["MockTicketReceiptV01"]["evidence_only"] is True
    assert boundaries["PaymentAuthorizationReceipt is not ticket permission."][
        "boundary_preserved"
    ] is True
    assert boundaries["OfferHoldReceipt is not payment permission."][
        "boundary_preserved"
    ] is True


def test_airline_slice_b_privacy_sealed_refs() -> None:
    report = _report()
    privacy = report["privacy_boundary_matrix"]
    sealed_refs = report["sealed_refs"]

    assert privacy["raw_passport_exposed_count"] == 0
    assert privacy["raw_card_exposed_count"] == 0
    assert privacy["raw_iban_exposed_count"] == 0
    assert privacy["raw_payment_token_exposed_count"] == 0
    assert sealed_refs["PassengerSealedRefsV01"]["passenger_ref"].startswith(
        "sealed_passenger_ref:",
    )
    assert sealed_refs["PaymentProfileSealedRefV01"]["payment_profile_ref"].startswith(
        "sealed_payment_profile_ref:",
    )
    assert privacy["no_raw_secrets_in_artifacts"] is True


def test_airline_slice_b_non_action_reuse_constraints() -> None:
    report = _report()
    constraints = report["non_action_reuse_constraints"]
    text = "\n".join(constraints["constraints"])

    assert "old quote is not ticket permission" in text
    assert "old ticket receipt is not future ticket permission" in text
    assert constraints["non_action_reuse_cannot_buy_ticket"] is True


def test_airline_slice_b_future_semantic_actor_topology_planned_not_executed() -> None:
    report = _report()
    actors = report["future_semantic_actor_topology"]
    sides = {actor["side"] for actor in actors}

    assert len(actors) == 6
    assert sides == {"client", "airline", "bank"}
    for actor in actors:
        assert actor["planned_for_later_live_lane"] is True
        assert actor["executed_in_slice_b"] is False
        assert actor["creates_authority"] is False
        assert actor["creates_action_commit_packet"] is False
        assert actor["creates_receipt"] is False
        assert actor["creates_ticket"] is False
        assert actor["executes_payment"] is False
        assert actor["calls_real_api"] is False


def test_airline_slice_b_future_vertical_fractal_map_planned_not_executed() -> None:
    report = _report()
    fractal_map = report["future_vertical_fractal_map"]
    cells = [cell for root_cells in fractal_map.values() for cell in root_cells]

    assert set(fractal_map) == {"ClientRoot", "AirlineRoot", "BankRoot"}
    assert len(cells) >= 14
    for cell in cells:
        assert cell["planned_for_later"] is True
        assert cell["executed_in_slice_b"] is False
        assert cell["creates_authority"] is False
        assert cell["real_world_effects_count"] == 0


def test_airline_slice_b_counters_zero_for_real_effects() -> None:
    counters = _report()["counter_table"]

    assert counters["real_airline_api_called_count"] == 0
    assert counters["real_bank_api_called_count"] == 0
    assert counters["real_payment_executed_count"] == 0
    assert counters["real_ticket_issued_count"] == 0
    assert counters["real_world_effects_count"] == 0
    assert counters["provider_called_count"] == 0
    assert counters["network_used_count"] == 0
    assert counters["gemini_called_count"] == 0


def test_airline_slice_b_renderer_sections_and_human_meaning() -> None:
    rendered = runner.render_tri_party_airline_ticket_purchase_mock_e2e_v01(_report())

    for section in runner.REQUIRED_SECTIONS:
        assert section in rendered
    assert "one mock airline purchase transaction skeleton" in rendered
    assert "not three unrelated demos" in rendered
    assert "Receipt crosses roots as evidence, not authority" in rendered
    assert "Old quote is not ticket permission" in rendered
    assert "Non-Action Direct Reuse cannot buy ticket" in rendered
    assert "Future LLM actors are planned" in rendered
    assert "Future vertical fractal cells are planned" in rendered
    assert "No real airline API" in rendered


def test_airline_slice_c_offer_hold_sandbox_passes() -> None:
    report = _report()
    sandbox = report["airline_offer_hold_sandbox"]

    assert report["final_status"] == runner.STATUS_PASS
    assert sandbox["sandbox_status"] == runner.STATUS_PASS
    assert sandbox["offer_request_validated"] is True
    assert sandbox["mock_inventory_checked"] is True
    assert sandbox["mock_fare_checked"] is True
    assert sandbox["baggage_rule_checked"] is True
    assert sandbox["offer_ttl_checked"] is True


def test_airline_slice_c_airline_root_creates_offer_hold_packet() -> None:
    report = _report()
    sandbox = report["airline_offer_hold_sandbox"]
    packet = report["mock_protocol_fixtures"]["AirlineOfferHoldCommitPacketV01"]
    counters = report["counter_table"]

    assert sandbox["offer_hold_commit_packet_created_by"] == "airline_root"
    assert packet["created_by"] == "airline_root"
    assert packet["root_created"] is True
    assert counters["airline_offer_hold_commit_packet_created_count"] == 1
    assert (
        counters["airline_offer_hold_commit_packet_created_by_airline_root_count"]
        == 1
    )
    assert (
        counters["airline_offer_hold_commit_packet_created_by_client_root_count"]
        == 0
    )
    assert (
        counters["airline_offer_hold_commit_packet_created_by_bank_root_count"]
        == 0
    )
    assert sandbox["offer_hold_commit_packet_validated"] is True


def test_airline_slice_c_offer_hold_receipt_evidence_only() -> None:
    report = _report()
    sandbox = report["airline_offer_hold_sandbox"]
    receipt = report["mock_protocol_fixtures"]["AirlineOfferHoldReceiptV01"]
    counters = report["counter_table"]

    assert sandbox["offer_hold_receipt_created"] is True
    assert sandbox["offer_hold_receipt_validated"] is True
    assert sandbox["offer_hold_receipt_evidence_only"] is True
    assert receipt["evidence_only"] is True
    assert sandbox["offer_hold_receipt_payment_permission_created"] is False
    assert sandbox["offer_hold_receipt_ticket_permission_created"] is False
    assert counters["offer_hold_receipt_payment_permission_created_count"] == 0
    assert counters["offer_hold_receipt_ticket_permission_created_count"] == 0


def test_airline_slice_c_no_real_airline_api_or_booking() -> None:
    counters = _report()["counter_table"]

    assert counters["real_airline_api_called_count"] == 0
    assert counters["real_booking_created_count"] == 0
    assert counters["real_ticket_issued_count"] == 0
    assert counters["real_world_effects_count"] == 0


def test_airline_slice_c_preserves_slice_b_boundaries() -> None:
    report = _report()
    ledger = report["shared_transaction_ledger"]
    offer_rows = [
        row for row in ledger if row.get("sandbox_stage") == "airline_offer_hold_sandbox"
    ]

    assert set(report["participants"]) == {"ClientRoot", "AirlineRoot", "BankRoot"}
    assert {row["transaction_id"] for row in ledger} == {runner.TRANSACTION_ID}
    assert len(offer_rows) == 4
    assert all(row["validated_by_airline_root"] is True for row in offer_rows)
    assert all(row["boundary_preserved"] for row in report["receipt_boundary_matrix"])
    assert report["privacy_boundary_matrix"]["raw_passport_exposed_count"] == 0
    assert report["privacy_boundary_matrix"]["raw_card_exposed_count"] == 0
    assert all(
        actor["executed_in_slice_b"] is False
        for actor in report["future_semantic_actor_topology"]
    )
    assert all(
        cell["executed_in_slice_b"] is False
        for cells in report["future_vertical_fractal_map"].values()
        for cell in cells
    )


def test_airline_slice_c_renderer_section() -> None:
    rendered = runner.render_tri_party_airline_ticket_purchase_mock_e2e_v01(_report())

    assert "[AIRLINEROOT OFFER HOLD SANDBOX]" in rendered
    assert "OfferHoldReceipt is evidence only" in rendered
    assert "not payment permission" in rendered
    assert "not ticket permission" in rendered
    assert "No real airline API was called" in rendered
    assert "real_airline_api_called_count: 0" in rendered
    assert "real_booking_created_count: 0" in rendered


def test_airline_slice_c_fail_closed_on_wrong_offer_hold_packet_creator() -> None:
    report = deepcopy(_report())

    report["airline_offer_hold_sandbox"][
        "offer_hold_commit_packet_created_by"
    ] = "client_root"
    errors = runner._validate_report(report)

    assert "offer_hold_commit_packet_creator_not_airline_root" in errors


def test_airline_slice_d_bank_payment_authorization_sandbox_passes() -> None:
    report = _report()
    sandbox = report["bank_payment_authorization_sandbox"]

    assert report["final_status"] == runner.STATUS_PASS
    assert sandbox["sandbox_status"] == runner.STATUS_PASS
    assert sandbox["amount_currency_validated"] is True
    assert sandbox["merchant_airline_ref_validated"] is True
    assert sandbox["payment_token_ref_validated"] is True
    assert sandbox["debtor_slot_ref_validated"] is True
    assert sandbox["idempotency_checked"] is True
    assert sandbox["expiry_ttl_checked"] is True


def test_airline_slice_d_bank_root_creates_payment_authorization_packet() -> None:
    report = _report()
    sandbox = report["bank_payment_authorization_sandbox"]
    packet = report["mock_protocol_fixtures"][
        "BankPaymentAuthorizationCommitPacketV01"
    ]
    counters = report["counter_table"]

    assert (
        sandbox["bank_payment_authorization_commit_packet_created_by"]
        == "bank_root"
    )
    assert packet["created_by"] == "bank_root"
    assert packet["root_created"] is True
    assert counters["bank_payment_authorization_commit_packet_created_count"] == 1
    assert (
        counters[
            "bank_payment_authorization_commit_packet_created_by_bank_root_count"
        ]
        == 1
    )
    assert (
        counters[
            "bank_payment_authorization_commit_packet_created_by_client_root_count"
        ]
        == 0
    )
    assert (
        counters[
            "bank_payment_authorization_commit_packet_created_by_airline_root_count"
        ]
        == 0
    )
    assert sandbox["bank_payment_authorization_commit_packet_validated"] is True


def test_airline_slice_d_payment_receipts_evidence_only() -> None:
    report = _report()
    sandbox = report["bank_payment_authorization_sandbox"]
    auth_receipt = report["mock_protocol_fixtures"][
        "BankPaymentAuthorizationReceiptV01"
    ]
    status_receipt = report["mock_protocol_fixtures"]["BankPaymentStatusReceiptV01"]

    assert sandbox["payment_authorization_receipt_created"] is True
    assert sandbox["payment_authorization_receipt_validated"] is True
    assert sandbox["payment_status_receipt_created"] is True
    assert sandbox["payment_status_receipt_validated"] is True
    assert sandbox["payment_authorization_receipt_evidence_only"] is True
    assert sandbox["payment_status_receipt_evidence_only"] is True
    assert auth_receipt["evidence_only"] is True
    assert status_receipt["evidence_only"] is True
    assert sandbox["payment_authorization_receipt_ticket_permission_created"] is False
    assert sandbox["payment_status_receipt_ticket_permission_created"] is False
    assert sandbox["payment_authorization_receipt_real_payment_executed"] is False
    assert sandbox["payment_status_receipt_settlement_executed"] is False


def test_airline_slice_d_no_real_bank_api_payment_or_settlement() -> None:
    counters = _report()["counter_table"]

    assert counters["real_bank_api_called_count"] == 0
    assert counters["real_payment_executed_count"] == 0
    assert counters["real_settlement_executed_count"] == 0
    assert counters["real_ticket_issued_count"] == 0
    assert counters["real_world_effects_count"] == 0


def test_airline_slice_d_preserves_slice_b_c_boundaries() -> None:
    report = _report()
    ledger = report["shared_transaction_ledger"]
    bank_rows = [
        row
        for row in ledger
        if row.get("sandbox_stage") == "bank_payment_authorization_sandbox"
    ]

    assert set(report["participants"]) == {"ClientRoot", "AirlineRoot", "BankRoot"}
    assert {row["transaction_id"] for row in ledger} == {runner.TRANSACTION_ID}
    assert report["airline_offer_hold_sandbox"]["sandbox_status"] == runner.STATUS_PASS
    assert (
        report["airline_offer_hold_sandbox"]["offer_hold_receipt_evidence_only"]
        is True
    )
    assert len(bank_rows) == 4
    assert all(row["validated_by_bank_root"] is True for row in bank_rows)
    assert report["privacy_boundary_matrix"]["raw_passport_exposed_count"] == 0
    assert report["privacy_boundary_matrix"]["raw_card_exposed_count"] == 0
    assert all(
        actor["executed_in_slice_b"] is False
        for actor in report["future_semantic_actor_topology"]
    )
    assert all(
        cell["executed_in_slice_b"] is False
        for cells in report["future_vertical_fractal_map"].values()
        for cell in cells
    )


def test_airline_slice_d_renderer_section() -> None:
    rendered = runner.render_tri_party_airline_ticket_purchase_mock_e2e_v01(_report())

    assert "[BANKROOT PAYMENT AUTHORIZATION SANDBOX]" in rendered
    assert "PaymentAuthorizationReceipt is evidence only" in rendered
    assert "PaymentStatusReceipt is evidence only" in rendered
    assert "not ticket permission" in rendered
    assert "real bank API" in rendered
    assert "no real payment was executed" in rendered.lower()
    assert "no real settlement happened" in rendered.lower()
    assert "real_bank_api_called_count: 0" in rendered
    assert "real_payment_executed_count: 0" in rendered
    assert "real_settlement_executed_count: 0" in rendered


def test_airline_slice_d_fail_closed_on_wrong_payment_packet_creator() -> None:
    report = deepcopy(_report())

    report["bank_payment_authorization_sandbox"][
        "bank_payment_authorization_commit_packet_created_by"
    ] = "airline_root"
    errors = runner._validate_report(report)

    assert "bank_payment_authorization_packet_creator_not_bank_root" in errors


def test_airline_slice_d_fail_closed_on_payment_receipt_ticket_permission() -> None:
    report = deepcopy(_report())

    report["bank_payment_authorization_sandbox"][
        "payment_authorization_receipt_ticket_permission_created"
    ] = True
    errors = runner._validate_report(report)

    assert (
        "bank_payment_authorization_sandbox_flag_true:"
        "payment_authorization_receipt_ticket_permission_created"
    ) in errors


def test_airline_slice_e_client_purchase_orchestration_passes() -> None:
    report = _report()
    orchestration = report["client_purchase_orchestration"]

    assert report["final_status"] == runner.STATUS_PASS
    assert orchestration["orchestration_status"] == runner.STATUS_PASS
    assert orchestration["travel_intent_observed"] is True
    assert orchestration["passenger_sealed_refs_observed"] is True
    assert orchestration["payment_profile_sealed_ref_observed"] is True
    assert orchestration["offer_response_observed"] is True
    assert orchestration["offer_hold_receipt_observed"] is True
    assert orchestration["selected_offer_within_user_max_price"] is True


def test_airline_slice_e_client_root_creates_purchase_approval_evidence() -> None:
    report = _report()
    orchestration = report["client_purchase_orchestration"]
    evidence = report["mock_protocol_fixtures"]["ClientPurchaseApprovalEvidenceV01"]
    counters = report["counter_table"]

    assert orchestration["client_purchase_approval_evidence_created"] is True
    assert orchestration["client_purchase_approval_evidence_created_by"] == "client_root"
    assert evidence["created_by"] == "client_root"
    assert evidence["root_created"] is True
    assert evidence["evidence_only"] is True
    assert counters["client_purchase_approval_evidence_created_count"] == 1
    assert (
        counters["client_purchase_approval_evidence_created_by_client_root_count"]
        == 1
    )
    assert (
        counters["client_purchase_approval_evidence_created_by_airline_root_count"]
        == 0
    )
    assert (
        counters["client_purchase_approval_evidence_created_by_bank_root_count"]
        == 0
    )
    assert orchestration["client_purchase_approval_evidence_validated"] is True


def test_airline_slice_e_client_routes_bounded_evidence() -> None:
    orchestration = _report()["client_purchase_orchestration"]

    assert orchestration["routed_to_bank_root"] is True
    assert orchestration["routed_to_airline_root"] is True
    assert orchestration["bank_payment_authorization_receipt_observed"] is True
    assert orchestration["bank_payment_status_receipt_observed"] is True


def test_airline_slice_e_client_root_cannot_authorize_payment_or_issue_ticket() -> None:
    counters = _report()["counter_table"]

    assert counters["client_root_authorized_bank_payment_count"] == 0
    assert counters["client_root_issued_ticket_count"] == 0
    assert counters["client_root_created_airline_order_count"] == 0
    assert counters["client_root_created_bank_receipt_count"] == 0
    assert counters["client_root_created_action_commit_packet_count"] == 0


def test_airline_slice_e_privacy_and_no_real_effects() -> None:
    counters = _report()["counter_table"]

    assert counters["client_raw_passport_exposed_count"] == 0
    assert counters["client_raw_card_exposed_count"] == 0
    assert counters["client_raw_iban_exposed_count"] == 0
    assert counters["client_raw_payment_token_exposed_count"] == 0
    assert counters["real_payment_executed_count"] == 0
    assert counters["real_ticket_issued_count"] == 0
    assert counters["real_booking_created_count"] == 0
    assert counters["real_world_effects_count"] == 0


def test_airline_slice_e_preserves_slice_b_c_d_boundaries() -> None:
    report = _report()
    ledger = report["shared_transaction_ledger"]
    client_rows = [
        row
        for row in ledger
        if row.get("orchestration_stage") == "client_purchase_orchestration"
    ]

    assert set(report["participants"]) == {"ClientRoot", "AirlineRoot", "BankRoot"}
    assert {row["transaction_id"] for row in ledger} == {runner.TRANSACTION_ID}
    assert report["airline_offer_hold_sandbox"]["sandbox_status"] == runner.STATUS_PASS
    assert (
        report["bank_payment_authorization_sandbox"]["sandbox_status"]
        == runner.STATUS_PASS
    )
    assert (
        report["airline_offer_hold_sandbox"]["offer_hold_receipt_evidence_only"]
        is True
    )
    assert (
        report["bank_payment_authorization_sandbox"][
            "payment_authorization_receipt_evidence_only"
        ]
        is True
    )
    assert len(client_rows) == 1
    assert client_rows[0]["validated_by_client_root"] is True
    assert all(
        actor["executed_in_slice_b"] is False
        for actor in report["future_semantic_actor_topology"]
    )
    assert all(
        cell["executed_in_slice_b"] is False
        for cells in report["future_vertical_fractal_map"].values()
        for cell in cells
    )


def test_airline_slice_e_renderer_section() -> None:
    rendered = runner.render_tri_party_airline_ticket_purchase_mock_e2e_v01(_report())

    assert "[CLIENTROOT PURCHASE ORCHESTRATION]" in rendered
    assert "ClientRoot selected the mock offer" in rendered
    assert "ClientPurchaseApprovalEvidence" in rendered
    assert "routed bounded purchase approval evidence to BankRoot" in rendered
    assert "routed bounded selected-offer evidence to AirlineRoot" in rendered
    assert "ClientRoot does not authorize bank payment" in rendered
    assert "ClientRoot does not issue ticket" in rendered
    assert "no real payment was executed" in rendered.lower()
    assert "no real ticket was issued" in rendered.lower()
    assert "real_payment_executed_count: 0" in rendered
    assert "real_ticket_issued_count: 0" in rendered


def test_airline_slice_e_fail_closed_on_wrong_purchase_approval_creator() -> None:
    report = deepcopy(_report())

    report["client_purchase_orchestration"][
        "client_purchase_approval_evidence_created_by"
    ] = "airline_root"
    errors = runner._validate_report(report)

    assert "client_purchase_approval_creator_not_client_root" in errors


def test_airline_slice_e_fail_closed_on_client_issuing_ticket() -> None:
    report = deepcopy(_report())

    report["client_purchase_orchestration"]["client_root_issued_ticket"] = True
    errors = runner._validate_report(report)

    assert "client_purchase_orchestration_flag_true:client_root_issued_ticket" in errors


def test_airline_slice_f_ticket_issue_mock_corridor_passes() -> None:
    report = _report()
    corridor = report["airline_ticket_issue_mock_corridor"]

    assert report["final_status"] == runner.STATUS_PASS
    assert corridor["corridor_status"] == runner.STATUS_PASS
    assert corridor["offer_hold_receipt_observed"] is True
    assert corridor["client_purchase_approval_evidence_observed"] is True
    assert corridor["payment_authorization_receipt_observed"] is True
    assert corridor["payment_status_receipt_observed"] is True
    assert corridor["selected_offer_match_validated"] is True
    assert corridor["amount_currency_match_validated"] is True


def test_airline_slice_f_airline_root_creates_ticket_issue_packet() -> None:
    report = _report()
    corridor = report["airline_ticket_issue_mock_corridor"]
    packet = report["mock_protocol_fixtures"]["AirlineTicketIssueCommitPacketV01"]
    counters = report["counter_table"]

    assert corridor["airline_ticket_issue_commit_packet_created_by"] == "airline_root"
    assert packet["created_by"] == "airline_root"
    assert packet["root_created"] is True
    assert counters["airline_ticket_issue_commit_packet_created_count"] == 1
    assert (
        counters["airline_ticket_issue_commit_packet_created_by_airline_root_count"]
        == 1
    )
    assert (
        counters["airline_ticket_issue_commit_packet_created_by_client_root_count"]
        == 0
    )
    assert (
        counters["airline_ticket_issue_commit_packet_created_by_bank_root_count"]
        == 0
    )
    assert corridor["airline_ticket_issue_commit_packet_validated"] is True


def test_airline_slice_f_order_ticket_pnr_receipts_created_as_mock_evidence() -> None:
    report = _report()
    corridor = report["airline_ticket_issue_mock_corridor"]
    ticket_receipt = report["mock_protocol_fixtures"]["MockTicketReceiptV01"]
    mock_pnr = report["mock_protocol_fixtures"]["MockPNRV01"]

    assert corridor["airline_order_created_receipt_created"] is True
    assert corridor["airline_order_created_receipt_validated"] is True
    assert corridor["mock_ticket_receipt_created"] is True
    assert corridor["mock_ticket_receipt_validated"] is True
    assert corridor["mock_pnr_created"] is True
    assert corridor["mock_pnr_validated"] is True
    assert corridor["mock_ticket_receipt_evidence_only"] is True
    assert ticket_receipt["evidence_only"] is True
    assert ticket_receipt["real_ticket"] is False
    assert mock_pnr["real_booking"] is False


def test_airline_slice_f_receipts_do_not_cross_authorize_ticket_or_payment() -> None:
    report = _report()
    counters = report["counter_table"]
    ticket_receipt = report["mock_protocol_fixtures"]["MockTicketReceiptV01"]

    assert counters["payment_authorization_receipt_created_ticket_count"] == 0
    assert counters["client_purchase_approval_created_ticket_count"] == 0
    assert counters["offer_hold_receipt_created_ticket_count"] == 0
    assert counters["airline_root_authorized_payment_count"] == 0
    assert ticket_receipt["payment_created"] is False


def test_airline_slice_f_client_summary_gets_mock_ticket_evidence_only() -> None:
    summary = _report()["mock_protocol_fixtures"]["ClientFinalTravelSummaryV01"]

    assert summary["mock_ticket_receipt_id"] == "mock_ticket_receipt:mock_airline_al:001"
    assert (
        summary["current_client_status"]
        == "mock_ticket_evidence_received_no_real_travel_booking"
    )
    assert summary["mock_ticket_evidence_received"] is True
    assert summary["ticket_issued"] is False
    assert summary["real_ticket_issued"] is False
    assert summary["real_booking_created"] is False


def test_airline_slice_f_no_real_airline_gds_ticket_booking_or_payment() -> None:
    counters = _report()["counter_table"]

    assert counters["airline_root_called_real_airline_api_count"] == 0
    assert counters["airline_root_called_real_gds_api_count"] == 0
    assert counters["real_ticket_issued_count"] == 0
    assert counters["real_booking_created_count"] == 0
    assert counters["real_payment_executed_count"] == 0
    assert counters["real_settlement_executed_count"] == 0
    assert counters["real_world_effects_count"] == 0


def test_airline_slice_f_preserves_slice_b_c_d_e_boundaries() -> None:
    report = _report()
    ledger = report["shared_transaction_ledger"]
    ticket_rows = [
        row
        for row in ledger
        if row.get("corridor_stage") == "airline_ticket_issue_mock_corridor"
    ]

    assert set(report["participants"]) == {"ClientRoot", "AirlineRoot", "BankRoot"}
    assert {row["transaction_id"] for row in ledger} == {runner.TRANSACTION_ID}
    assert report["airline_offer_hold_sandbox"]["sandbox_status"] == runner.STATUS_PASS
    assert (
        report["bank_payment_authorization_sandbox"]["sandbox_status"]
        == runner.STATUS_PASS
    )
    assert (
        report["client_purchase_orchestration"]["orchestration_status"]
        == runner.STATUS_PASS
    )
    assert (
        report["airline_offer_hold_sandbox"]["offer_hold_receipt_evidence_only"]
        is True
    )
    assert (
        report["bank_payment_authorization_sandbox"][
            "payment_authorization_receipt_evidence_only"
        ]
        is True
    )
    assert (
        report["client_purchase_orchestration"][
            "client_purchase_approval_evidence_evidence_only"
        ]
        is True
    )
    assert len(ticket_rows) == 5
    assert all(row["validated_by_airline_root"] is True for row in ticket_rows)
    assert all(
        actor["executed_in_slice_b"] is False
        for actor in report["future_semantic_actor_topology"]
    )
    assert all(
        cell["executed_in_slice_b"] is False
        for cells in report["future_vertical_fractal_map"].values()
        for cell in cells
    )


def test_airline_slice_f_renderer_section() -> None:
    rendered = runner.render_tri_party_airline_ticket_purchase_mock_e2e_v01(_report())

    assert "[AIRLINEROOT TICKET ISSUE MOCK CORRIDOR]" in rendered
    assert "AirlineRoot created AirlineTicketIssueCommitPacket" in rendered
    assert "MockTicketReceipt is evidence only" in rendered
    assert "not a real ticket" in rendered
    assert "no real airline api" in rendered.lower()
    assert "no real ticket was issued" in rendered.lower()
    assert "no real booking was created" in rendered.lower()
    assert "real_ticket_issued_count: 0" in rendered
    assert "real_booking_created_count: 0" in rendered


def test_airline_slice_f_fail_closed_on_wrong_ticket_packet_creator() -> None:
    report = deepcopy(_report())

    report["airline_ticket_issue_mock_corridor"][
        "airline_ticket_issue_commit_packet_created_by"
    ] = "bank_root"
    errors = runner._validate_report(report)

    assert "airline_ticket_issue_packet_creator_not_airline_root" in errors


def test_airline_slice_f_fail_closed_on_mock_ticket_becoming_real_ticket() -> None:
    report = deepcopy(_report())

    report["airline_ticket_issue_mock_corridor"][
        "mock_ticket_receipt_real_ticket"
    ] = True
    errors = runner._validate_report(report)

    assert (
        "airline_ticket_issue_corridor_flag_true:mock_ticket_receipt_real_ticket"
    ) in errors


def test_airline_slice_g_integrated_trace_passes() -> None:
    report = _report()
    trace = report["integrated_transaction_trace"]

    assert report["final_status"] == runner.STATUS_PASS
    assert trace
    assert len(trace) == 17
    assert {row["transaction_id"] for row in trace} == {runner.TRANSACTION_ID}


def test_airline_slice_g_trace_is_one_transaction_not_three_demos() -> None:
    report = _report()
    trace = report["integrated_transaction_trace"]
    counters = report["counter_table"]
    final_summary = report["final_tri_party_mock_summary"]

    assert counters["integrated_tri_party_transaction_trace_created_count"] == 1
    assert counters["shared_transaction_id_count"] == 1
    assert all(row["transaction_id"] == runner.TRANSACTION_ID for row in trace)
    assert final_summary["transaction_id"] == runner.TRANSACTION_ID


def test_airline_slice_g_cross_root_evidence_routing_matrix() -> None:
    routing = _report()["cross_root_evidence_routing_matrix"]
    route_pairs = [
        (row["source_root_id"], row["target_root_id"]) for row in routing
    ]

    assert len(routing) == 6
    assert all(row["authority_transferred"] is False for row in routing)
    assert route_pairs == [
        (runner.CLIENT_ROOT_ID, runner.AIRLINE_ROOT_ID),
        (runner.AIRLINE_ROOT_ID, runner.CLIENT_ROOT_ID),
        (runner.CLIENT_ROOT_ID, runner.BANK_ROOT_ID),
        (runner.BANK_ROOT_ID, runner.CLIENT_ROOT_ID),
        (runner.CLIENT_ROOT_ID, runner.AIRLINE_ROOT_ID),
        (runner.AIRLINE_ROOT_ID, runner.CLIENT_ROOT_ID),
    ]


def test_airline_slice_g_no_authority_transfer_or_real_effects() -> None:
    counters = _report()["counter_table"]

    assert counters["cross_root_authority_transfer_count"] == 0
    assert counters["cross_root_real_world_effects_count"] == 0
    assert counters["final_authority_transferred_between_roots_count"] == 0
    assert counters["real_world_effects_count"] == 0


def test_airline_slice_g_final_tri_party_mock_summary() -> None:
    summary = _report()["final_tri_party_mock_summary"]

    assert summary["final_status"] == runner.STATUS_PASS
    assert (
        summary["client_view_status"]
        == "mock_ticket_evidence_received_no_real_travel_booking"
    )
    assert summary["airline_view_status"] == "mock_order_ticket_pnr_evidence_created"
    assert summary["bank_view_status"] == "mock_payment_authorized_not_settled"
    assert summary["real_ticket_issued"] is False
    assert summary["real_payment_executed"] is False
    assert summary["real_booking_created"] is False


def test_airline_slice_g_preserves_slice_b_c_d_e_f_boundaries() -> None:
    report = _report()

    assert set(report["participants"]) == {"ClientRoot", "AirlineRoot", "BankRoot"}
    assert report["airline_offer_hold_sandbox"]["sandbox_status"] == runner.STATUS_PASS
    assert (
        report["bank_payment_authorization_sandbox"]["sandbox_status"]
        == runner.STATUS_PASS
    )
    assert (
        report["client_purchase_orchestration"]["orchestration_status"]
        == runner.STATUS_PASS
    )
    assert (
        report["airline_ticket_issue_mock_corridor"]["corridor_status"]
        == runner.STATUS_PASS
    )
    assert (
        report["airline_offer_hold_sandbox"]["offer_hold_receipt_evidence_only"]
        is True
    )
    assert (
        report["bank_payment_authorization_sandbox"][
            "payment_authorization_receipt_evidence_only"
        ]
        is True
    )
    assert (
        report["client_purchase_orchestration"][
            "client_purchase_approval_evidence_evidence_only"
        ]
        is True
    )
    assert (
        report["airline_ticket_issue_mock_corridor"][
            "mock_ticket_receipt_evidence_only"
        ]
        is True
    )
    assert all(
        actor["executed_in_slice_b"] is False
        for actor in report["future_semantic_actor_topology"]
    )
    assert all(
        cell["executed_in_slice_b"] is False
        for cells in report["future_vertical_fractal_map"].values()
        for cell in cells
    )


def test_airline_slice_g_renderer_sections() -> None:
    rendered = runner.render_tri_party_airline_ticket_purchase_mock_e2e_v01(_report())

    assert "[INTEGRATED TRI-PARTY TRANSACTION TRACE]" in rendered
    assert "[CROSS-ROOT EVIDENCE ROUTING MATRIX]" in rendered
    assert "[FINAL TRI-PARTY MOCK SUMMARY]" in rendered
    assert "one transaction, not three unrelated demos" in rendered
    assert "exchange evidence, not authority" in rendered
    assert "No real-world effect occurred" in rendered
    assert "cross_root_authority_transfer_count: 0" in rendered


def test_airline_slice_g_fail_closed_on_mixed_transaction_id_in_integrated_trace() -> None:
    report = deepcopy(_report())

    report["integrated_transaction_trace"][3]["transaction_id"] = (
        "tri_airline_purchase:wrong"
    )
    errors = runner._validate_report(report)

    assert "integrated_trace_transaction_id_mismatch" in errors


def test_airline_slice_g_fail_closed_on_cross_root_authority_transfer() -> None:
    report = deepcopy(_report())

    report["cross_root_evidence_routing_matrix"][0]["authority_transferred"] = True
    errors = runner._validate_report(report)

    assert "cross_root_routing_authority_transfer" in errors


def test_airline_slice_g_source_import_boundary() -> None:
    source = Path(runner.__file__).read_text()

    assert "google.genai" not in source
    assert "import requests" not in source
    assert "import urllib" not in source
    assert "import openai" not in source
    assert "import subprocess" not in source
    assert "manual_live" not in source
    assert "run_live" not in source
    assert "provider adapter" not in source
    assert "GDS connector" not in source
    assert "NDC connector" not in source
    assert "OpenBanking connector" not in source
    assert "production " + "ready" not in source
    assert "public auditor " + "ready" not in source
    for left, right in (
        ("AI bought a", " real ticket"),
        ("AI paid", " real money"),
        ("receipt grants", " permission"),
        ("payment receipt creates", " ticket"),
        ("ticket receipt creates", " payment"),
        ("old quote grants", " ticket"),
        ("PaymentAuthorizationReceipt grants", " ticket"),
        ("PaymentStatusReceipt grants", " ticket"),
        ("ClientPurchaseApprovalEvidence grants", " payment"),
        ("ClientPurchaseApprovalEvidence grants", " ticket"),
        ("MockTicketReceipt grants", " payment"),
        ("MockTicketReceipt is", " real ticket"),
        ("authority transferred", " between roots"),
    ):
        assert left + right not in source


def _assert_corridor_source_mutation_fails(report: dict[str, object]) -> None:
    errors = runner._validate_report(report)

    assert errors
    assert (
        "airline_corridor_binding_matrix_mismatch" in errors
        or "airline_corridor_projected_source_not_pass" in errors
        or "airline_corridor_fixture_report_binding_failed" in errors
        or "airline_corridor_projection_failed" in errors
    )


def test_airline_corridor_slice_d_integrates_into_existing_runner() -> None:
    report = _report()
    integration = report["airline_ticket_purchase_corridor_integration"]

    assert report["final_status"] == runner.STATUS_PASS
    assert "airline_ticket_purchase_corridor_v0_1" in report
    assert integration["integration_status"] == runner.STATUS_PASS
    assert integration["corridor_public_validation_accepted"] is True


def test_airline_corridor_slice_d_uses_one_existing_transaction() -> None:
    report = _report()
    corridor = report["airline_ticket_purchase_corridor_v0_1"]
    binding_matrix = report["airline_ticket_purchase_corridor_binding_matrix"]

    assert corridor.transaction_id == report["transaction_id"]
    assert {row["transaction_id"] for row in binding_matrix} == {
        report["transaction_id"],
    }
    assert report["counter_table"]["shared_transaction_id_count"] == 1


def test_airline_corridor_slice_d_exact_five_root_centered_phases() -> None:
    corridor = _report()["airline_ticket_purchase_corridor_v0_1"]

    assert tuple(phase.phase_id for phase in corridor.phase_results) == (
        runner.corridor_runtime.PHASE_AIRLINE_OFFER_HOLD,
        runner.corridor_runtime.PHASE_CLIENT_PURCHASE_INTENT,
        runner.corridor_runtime.PHASE_BANK_PAYMENT_AUTHORIZATION,
        runner.corridor_runtime.PHASE_AIRLINE_TICKET_ISSUE,
        runner.corridor_runtime.PHASE_CLIENT_COMPLETION,
    )
    assert all(
        phase.phase_status == runner.corridor_runtime.STATUS_PASS
        for phase in corridor.phase_results
    )


def test_airline_corridor_slice_d_binding_matrix_all_matches() -> None:
    report = _report()
    matrix = report["airline_ticket_purchase_corridor_binding_matrix"]
    counters = report["counter_table"]

    assert len(matrix) >= 14
    assert all(row["values_match"] is True for row in matrix)
    assert all(row["raw_secret_used"] is False for row in matrix)
    assert all(row["authority_transferred"] is False for row in matrix)
    assert counters["airline_ticket_purchase_corridor_binding_match_count"] == len(
        matrix,
    )
    assert counters["airline_ticket_purchase_corridor_binding_mismatch_count"] == 0


def test_airline_corridor_slice_d_no_parallel_fixture_transaction() -> None:
    report = _report()
    integration = report["airline_ticket_purchase_corridor_integration"]
    counters = report["counter_table"]

    assert integration["parallel_fixture_transaction_created"] is False
    assert counters["airline_ticket_purchase_corridor_parallel_transaction_count"] == 0
    assert counters["airline_ticket_purchase_corridor_duplicate_execution_count"] == 0


def test_airline_corridor_slice_d_existing_receipts_observed_not_created() -> None:
    report = _report()
    corridor = report["airline_ticket_purchase_corridor_v0_1"]
    counters = report["counter_table"]

    assert corridor.counter_table["fixture_receipts_observed_count"] == 3
    assert corridor.counter_table["runtime_receipts_created_count"] == 0
    assert counters["airline_ticket_purchase_corridor_fixture_receipts_observed_count"] == 3
    assert counters["airline_ticket_purchase_corridor_runtime_receipts_created_count"] == 0
    assert counters["airline_ticket_purchase_corridor_runtime_packets_created_count"] == 0


def test_airline_corridor_slice_d_core_domain_delegation_visible() -> None:
    corridor = _report()["airline_ticket_purchase_corridor_v0_1"]
    matrix = {row.check_id: row for row in corridor.core_domain_delegation_matrix}

    assert matrix["no_post_root_reasoning"].directly_delegated_to_core is True
    assert matrix["corridor_deterministic_only"].directly_delegated_to_core is True
    assert matrix["airline_offer_hold_bindings"].directly_delegated_to_core is False
    assert corridor.counter_table["core_delegated_check_count"] == 2
    assert corridor.counter_table["domain_projection_check_count"] == 6


def test_airline_corridor_slice_d_offer_hold_source_mutation_fails_closed() -> None:
    report = deepcopy(_report())

    report["mock_protocol_fixtures"]["AirlineOfferHoldReceiptV01"]["receipt_id"] = (
        "offer_hold_receipt:wrong"
    )

    _assert_corridor_source_mutation_fails(report)


def test_airline_corridor_slice_d_amount_source_mutation_fails_closed() -> None:
    report = deepcopy(_report())

    report["mock_protocol_fixtures"]["AirlineOfferCandidateV01"][
        "price_amount"
    ] += 1

    _assert_corridor_source_mutation_fails(report)


def test_airline_corridor_slice_d_passenger_source_mutation_fails_closed() -> None:
    report = deepcopy(_report())

    report["mock_protocol_fixtures"]["AirlineOfferRequestV01"]["passenger_ref"] = (
        "sealed_passenger_ref:wrong"
    )

    _assert_corridor_source_mutation_fails(report)


def test_airline_corridor_slice_d_route_source_mutation_fails_closed() -> None:
    report = deepcopy(_report())

    report["mock_protocol_fixtures"]["AirlineOfferHoldCommitPacketV01"][
        "allowed_route_ref"
    ] = "route:wrong"

    _assert_corridor_source_mutation_fails(report)


def test_airline_corridor_slice_d_bank_authorization_source_mutation_fails_closed() -> None:
    report = deepcopy(_report())

    report["mock_protocol_fixtures"]["BankPaymentAuthorizationReceiptV01"][
        "authorized_amount"
    ] += 1

    _assert_corridor_source_mutation_fails(report)


def test_airline_corridor_slice_d_no_cross_root_authority_transfer() -> None:
    report = _report()
    corridor = report["airline_ticket_purchase_corridor_v0_1"]

    assert all(not phase.authority_transferred for phase in corridor.phase_results)
    assert report["counter_table"][
        "airline_ticket_purchase_corridor_cross_root_authority_transfer_count"
    ] == 0


def test_airline_corridor_slice_d_zero_real_effects() -> None:
    counters = _report()["counter_table"]

    assert counters["airline_ticket_purchase_corridor_provider_called_count"] == 0
    assert counters["airline_ticket_purchase_corridor_network_used_count"] == 0
    assert counters["airline_ticket_purchase_corridor_gemini_called_count"] == 0
    assert counters["airline_ticket_purchase_corridor_real_world_effects_count"] == 0


def test_airline_corridor_slice_d_renderer_section() -> None:
    rendered = runner.render_tri_party_airline_ticket_purchase_mock_e2e_v01(_report())

    assert (
        "[AIRLINE TICKET/PURCHASE CORRIDOR V0.1 ROOT-CENTERED INTEGRATION]"
        in rendered
    )
    assert "existing Airline transaction, not a second demo" in rendered
    assert "The universal core no-post-Root reasoning guard ran for all five phases" in rendered
    assert "The corridor created zero runtime receipts" in rendered
    assert "Evidence crossed Root boundaries; authority did not" in rendered
    assert "airline_offer_hold_phase" in rendered
    assert "binding_matrix:" in rendered


def test_airline_corridor_slice_d_demo_does_not_reimplement_corridor_engine() -> None:
    source = Path(runner.__file__).read_text()

    assert "ticket_purchase_corridor_runtime_v01 as corridor_runtime" in source
    assert "ticket_purchase_corridor_v01 as corridor_contracts" in source
    assert "collect_airline_ticket_purchase_corridor_state_machine_v01" in source
    assert "validate_airline_ticket_purchase_corridor_run_v01" in source
    assert "_run_airline_ticket_purchase_corridor_state_machine_v01" not in source
    assert "PHASE_VALIDATORS" not in source
    assert "def validate_airline_offer_packet_v01" not in source
    assert "def validate_airline_hold_commit_packet_v01" not in source
    assert "build_" + "supplier_a" not in source
    assert "SUBJECT_" + "SUPPLIER_A" not in source
    assert "SUBJECT_" + "SUPPLIER_B" not in source
    assert "parallel " + "Airline transaction created" not in source


def test_airline_corridor_slice_d_public_collector_called_once(monkeypatch) -> None:
    call_count = 0
    original = (
        runner.corridor_runtime.collect_airline_ticket_purchase_corridor_state_machine_v01
    )

    def counted_collector(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        return original(*args, **kwargs)

    monkeypatch.setattr(
        runner.corridor_runtime,
        "collect_airline_ticket_purchase_corridor_state_machine_v01",
        counted_collector,
    )

    report = runner.collect_tri_party_airline_ticket_purchase_mock_e2e_v01()

    assert report["final_status"] == runner.STATUS_PASS
    assert call_count == 1
    assert report["airline_ticket_purchase_corridor_integration"][
        "duplicate_corridor_execution_count"
    ] == 0


def test_airline_corridor_slice_d_source_has_one_direct_collector_call() -> None:
    source = Path(runner.__file__).read_text()
    direct_call = (
        "corridor_runtime."
        "collect_airline_ticket_purchase_corridor_state_machine_v01("
    )
    validate_source = source.split("def _validate_report", maxsplit=1)[1]

    assert source.count(direct_call) == 1
    assert direct_call not in validate_source
    assert "validate_airline_ticket_purchase_corridor_fixture_bundle_v01" in (
        validate_source
    )


def test_airline_corridor_slice_d_human_approval_and_purchase_intent_are_distinct() -> None:
    report = _report()
    bundle = runner._build_airline_ticket_purchase_corridor_fixture_bundle_v01(
        report,
    )
    rows = {
        row["binding_id"]: row
        for row in report["airline_ticket_purchase_corridor_binding_matrix"]
    }

    assert bundle["human_approval"].approval_ref == (
        "client_purchase_approval:client_001:001"
    )
    assert bundle["purchase_intent"].intent_id == (
        "client_purchase_intent:client_001:001"
    )
    assert bundle["human_approval"].approval_ref != bundle["purchase_intent"].intent_id
    assert (
        bundle["purchase_intent"].source_human_approval_ref
        == bundle["human_approval"].approval_ref
    )
    assert rows["client_purchase_approval_ref"]["values_match"] is True
    assert rows["client_purchase_intent_id"]["values_match"] is True
    assert rows["purchase_intent_source_human_approval_ref"]["values_match"] is True


def test_airline_corridor_slice_d_bank_receipt_and_authorization_ref_are_distinct() -> None:
    report = _report()
    bundle = runner._build_airline_ticket_purchase_corridor_fixture_bundle_v01(
        report,
    )
    rows = {
        row["binding_id"]: row
        for row in report["airline_ticket_purchase_corridor_binding_matrix"]
    }

    assert bundle["authorization_ref"].source_payment_receipt_id == (
        "payment_authorization_receipt:mock_bank_a:001"
    )
    assert bundle["authorization_ref"].authorization_ref_id == (
        "bank_payment_authorization_ref:mock_bank_a:001"
    )
    assert (
        bundle["authorization_ref"].authorization_ref_id
        != bundle["authorization_ref"].source_payment_receipt_id
    )
    assert rows["payment_authorization_receipt_id"]["values_match"] is True
    assert rows["payment_authorization_ref_id"]["values_match"] is True
    assert rows["authorization_ref_source_receipt_id"]["values_match"] is True


def test_airline_corridor_slice_d_mock_purchase_receipt_and_final_summary_are_distinct() -> None:
    report = _report()
    fixtures = report["mock_protocol_fixtures"]
    bundle = runner._build_airline_ticket_purchase_corridor_fixture_bundle_v01(
        report,
    )
    rows = {
        row["binding_id"]: row
        for row in report["airline_ticket_purchase_corridor_binding_matrix"]
    }

    assert fixtures["MockPurchaseReceiptV01"]["receipt_id"] == (
        "mock_purchase_receipt:client_001:001"
    )
    assert fixtures["ClientFinalTravelSummaryV01"]["summary_id"] == (
        "client_final_travel_summary:client_001:001"
    )
    assert (
        fixtures["MockPurchaseReceiptV01"]["receipt_id"]
        != fixtures["ClientFinalTravelSummaryV01"]["summary_id"]
    )
    assert bundle["purchase_receipt"].receipt_id == (
        fixtures["MockPurchaseReceiptV01"]["receipt_id"]
    )
    assert rows["mock_purchase_receipt_id"]["values_match"] is True
    assert (
        rows["client_final_summary_mock_purchase_receipt_id"]["values_match"]
        is True
    )
    assert report["airline_ticket_purchase_corridor_v0_1"].counter_table[
        "fixture_receipts_observed_count"
    ] == 3


def test_airline_corridor_slice_d_transaction_binding_uses_all_projection_ids() -> None:
    report = _report()
    transaction_row = next(
        row
        for row in report["airline_ticket_purchase_corridor_binding_matrix"]
        if row["binding_id"] == "transaction_id"
    )
    integration = report["airline_ticket_purchase_corridor_integration"]

    assert transaction_row["source_value"] == runner.TRANSACTION_ID
    assert transaction_row["projected_value"] == (runner.TRANSACTION_ID,)
    assert transaction_row["unique_transaction_id_count"] == 1
    assert transaction_row["all_transaction_ids_match"] is True
    assert integration["unique_transaction_id_count"] == 1
    assert integration["all_transaction_ids_match"] is True


def test_airline_corridor_slice_d_derived_existing_projection_tamper_rejected() -> None:
    report = deepcopy(_report())

    report["airline_ticket_purchase_corridor_binding_matrix"][1][
        "values_match"
    ] = False

    errors = runner._validate_report(report)

    assert "airline_corridor_binding_mismatch" in errors
    assert "airline_corridor_binding_matrix_mismatch" in errors


def test_airline_corridor_slice_d_derived_parallel_transaction_tamper_rejected() -> None:
    report = deepcopy(_report())
    corridor = report["airline_ticket_purchase_corridor_v0_1"]
    bad_phase = replace(
        corridor.phase_results[0],
        transaction_id="tri_airline_purchase:wrong",
    )
    report["airline_ticket_purchase_corridor_v0_1"] = (
        replace(
            corridor,
            phase_results=(bad_phase,) + corridor.phase_results[1:],
        )
    )

    errors = runner._validate_report(report)

    assert "transaction_id_set_mismatch" in errors
    assert "airline_corridor_public_validation_rejected" in errors


def test_airline_corridor_slice_d_derived_duplicate_execution_tamper_rejected() -> None:
    report = deepcopy(_report())

    report["airline_ticket_purchase_corridor_integration"][
        "duplicate_corridor_execution_count"
    ] = 1

    errors = runner._validate_report(report)

    assert (
        "airline_corridor_integration_mismatch:duplicate_corridor_execution_count"
        in errors
    )
    assert "airline_corridor_integration_mismatch:derived_fields" in errors


def test_airline_corridor_slice_d_derived_authority_transfer_tamper_rejected() -> None:
    report = deepcopy(_report())

    report["root_boundary_matrix"][0]["violation_count"] = 1

    errors = runner._validate_report(report)

    assert "root_boundary_violation" in errors
    assert "airline_corridor_integration_mismatch:derived_fields" in errors


def test_airline_corridor_slice_d_source_offer_hold_expiry_fails_phase_one() -> None:
    report = deepcopy(_report())
    report["mock_protocol_fixtures"]["AirlineOfferHoldCommitPacketV01"][
        "offer_hold_expired"
    ] = True
    bundle = runner._build_airline_ticket_purchase_corridor_fixture_bundle_v01(
        report,
    )
    corridor = runner.corridor_runtime.collect_airline_ticket_purchase_corridor_state_machine_v01(
        fixtures=bundle,
    )

    assert corridor.final_status == runner.corridor_runtime.STATUS_FAIL_CLOSED
    assert corridor.failed_phase_id == runner.corridor_runtime.PHASE_AIRLINE_OFFER_HOLD
    assert all(
        phase.phase_status == runner.corridor_runtime.STATUS_NOT_RUN
        for phase in corridor.phase_results[1:]
    )
    _assert_corridor_source_mutation_fails(report)


def test_airline_corridor_slice_d_source_payment_expiry_fails_bank_phase() -> None:
    report = deepcopy(_report())
    report["mock_protocol_fixtures"]["BankPaymentAuthorizationReceiptV01"][
        "payment_authorization_expired"
    ] = True
    bundle = runner._build_airline_ticket_purchase_corridor_fixture_bundle_v01(
        report,
    )
    corridor = runner.corridor_runtime.collect_airline_ticket_purchase_corridor_state_machine_v01(
        fixtures=bundle,
    )

    assert corridor.final_status == runner.corridor_runtime.STATUS_FAIL_CLOSED
    assert (
        corridor.failed_phase_id
        == runner.corridor_runtime.PHASE_BANK_PAYMENT_AUTHORIZATION
    )
    assert all(
        phase.phase_status == runner.corridor_runtime.STATUS_NOT_RUN
        for phase in corridor.phase_results[3:]
    )
    _assert_corridor_source_mutation_fails(report)


def test_corridor_report_is_bound_to_exact_projected_fixture_bundle() -> None:
    report = _report()
    fixture_bundle = runner._build_airline_ticket_purchase_corridor_fixture_bundle_v01(
        report,
    )

    accepted, errors = (
        runner.corridor_runtime
        .validate_airline_ticket_purchase_corridor_report_against_fixture_bundle_v01(
            fixture_bundle,
            report["airline_ticket_purchase_corridor_v0_1"],
        )
    )

    assert accepted is True
    assert errors == ()
    assert report["airline_ticket_purchase_corridor_integration"][
        "corridor_report_bound_to_projected_fixtures"
    ] is True
    assert report["counter_table"][
        "airline_ticket_purchase_corridor_fixture_report_binding_pass_count"
    ] == 1


def test_corridor_report_wrong_phase_evidence_ref_rejected() -> None:
    report = _report()
    fixture_bundle = runner._build_airline_ticket_purchase_corridor_fixture_bundle_v01(
        report,
    )
    corridor = report["airline_ticket_purchase_corridor_v0_1"]
    bad_phase = replace(
        corridor.phase_results[0],
        evidence_refs_observed=("offer_packet:wrong",),
    )
    corrupted = replace(
        corridor,
        phase_results=(bad_phase,) + corridor.phase_results[1:],
    )

    accepted, errors = (
        runner.corridor_runtime
        .validate_airline_ticket_purchase_corridor_report_against_fixture_bundle_v01(
            fixture_bundle,
            corrupted,
        )
    )

    assert accepted is False
    assert (
        runner.corridor_runtime.REASON_PHASE_EVIDENCE_REFS_MISMATCH
        in errors
    )
    assert (
        runner.corridor_runtime.REASON_FIXTURE_REPORT_BINDING_FAILED
        in errors
    )


def test_valid_unrelated_corridor_report_cannot_replace_projected_report() -> None:
    report = deepcopy(_report())
    report["mock_protocol_fixtures"]["AirlineOfferHoldReceiptV01"][
        "receipt_id"
    ] = "offer_hold_receipt:mock_airline_al:unrelated"
    fixture_bundle = runner._build_airline_ticket_purchase_corridor_fixture_bundle_v01(
        report,
    )
    unrelated = (
        runner.corridor_runtime
        .collect_airline_ticket_purchase_corridor_state_machine_v01()
    )
    accepted, _ = runner.corridor_runtime.validate_airline_ticket_purchase_corridor_run_v01(
        unrelated,
    )
    binding_matrix = runner._airline_ticket_purchase_corridor_binding_matrix_v01(
        report,
        fixture_bundle,
        unrelated,
    )

    report["airline_ticket_purchase_corridor_v0_1"] = unrelated
    report["airline_ticket_purchase_corridor_binding_matrix"] = binding_matrix
    report["airline_ticket_purchase_corridor_integration"] = (
        runner._airline_ticket_purchase_corridor_integration_summary(
            report,
            fixture_bundle,
            unrelated,
            accepted,
            binding_matrix,
            1,
        )
    )

    errors = runner._validate_report(report)

    assert "airline_corridor_fixture_report_binding_failed" in errors


def test_offer_hold_receipt_creator_is_hold_sandbox() -> None:
    report = _report()
    fixture = report["mock_protocol_fixtures"]["AirlineOfferHoldReceiptV01"]
    bundle = runner._build_airline_ticket_purchase_corridor_fixture_bundle_v01(
        report,
    )

    assert fixture["created_by"] == runner.corridor_contracts.ADAPTER_AIRLINE_HOLD_SANDBOX
    assert fixture["root_owner"] == runner.AIRLINE_ROOT_ID
    assert bundle["hold_receipt"].created_by == fixture["created_by"]
    assert bundle["hold_receipt"].root_owner == fixture["root_owner"]


def test_mock_ticket_receipt_creator_is_ticket_sandbox() -> None:
    report = _report()
    fixture = report["mock_protocol_fixtures"]["MockTicketReceiptV01"]
    bundle = runner._build_airline_ticket_purchase_corridor_fixture_bundle_v01(
        report,
    )

    assert fixture["created_by"] == (
        runner.corridor_contracts.ADAPTER_AIRLINE_TICKET_SANDBOX
    )
    assert fixture["root_owner"] == runner.AIRLINE_ROOT_ID
    assert bundle["ticket_receipt"].created_by == fixture["created_by"]
    assert bundle["ticket_receipt"].root_owner == fixture["root_owner"]


def test_mock_purchase_receipt_creator_is_completion_observer() -> None:
    report = _report()
    fixture = report["mock_protocol_fixtures"]["MockPurchaseReceiptV01"]
    bundle = runner._build_airline_ticket_purchase_corridor_fixture_bundle_v01(
        report,
    )

    assert fixture["created_by"] == "client_completion_observer"
    assert fixture["root_owner"] == runner.CLIENT_ROOT_ID
    assert bundle["purchase_receipt"].created_by == fixture["created_by"]
    assert bundle["purchase_receipt"].root_owner == fixture["root_owner"]


def test_receipt_creator_and_root_owner_binding_rows_match() -> None:
    rows = {
        row["binding_id"]: row
        for row in _report()["airline_ticket_purchase_corridor_binding_matrix"]
    }

    for binding_id in (
        "offer_hold_receipt_created_by",
        "offer_hold_receipt_root_owner",
        "mock_ticket_receipt_created_by",
        "mock_ticket_receipt_root_owner",
        "mock_purchase_receipt_created_by",
        "mock_purchase_receipt_root_owner",
    ):
        assert rows[binding_id]["values_match"] is True
        assert rows[binding_id]["raw_secret_used"] is False
        assert rows[binding_id]["authority_transferred"] is False


def test_source_receipt_creator_tamper_fails_closed() -> None:
    cases = (
        (
            "AirlineOfferHoldReceiptV01",
            "created_by",
            "provider",
            "offer_hold_receipt_fixture_creator_not_hold_sandbox",
        ),
        (
            "AirlineOfferHoldReceiptV01",
            "root_owner",
            runner.CLIENT_ROOT_ID,
            "offer_hold_receipt_fixture_wrong_root_owner",
        ),
        (
            "MockTicketReceiptV01",
            "created_by",
            "airline_root",
            "mock_ticket_receipt_fixture_creator_not_ticket_sandbox",
        ),
        (
            "MockTicketReceiptV01",
            "root_owner",
            runner.CLIENT_ROOT_ID,
            "mock_ticket_receipt_fixture_wrong_root_owner",
        ),
        (
            "MockPurchaseReceiptV01",
            "created_by",
            "client_root",
            "mock_purchase_receipt_creator_not_completion_observer",
        ),
        (
            "MockPurchaseReceiptV01",
            "root_owner",
            runner.AIRLINE_ROOT_ID,
            "mock_purchase_receipt_wrong_root_owner",
        ),
    )

    for fixture_name, field_name, bad_value, expected_error in cases:
        report = deepcopy(_report())
        report["mock_protocol_fixtures"][fixture_name][field_name] = bad_value

        errors = runner._validate_report(report)

        assert expected_error in errors
        _assert_corridor_source_mutation_fails(report)


def test_no_argument_deterministic_runner_remains_pass() -> None:
    report = runner.collect_tri_party_airline_ticket_purchase_mock_e2e_v01()

    assert report["final_status"] == runner.STATUS_PASS
    assert (
        report["mock_protocol_fixtures"]["AirlineOfferCandidateV01"]["offer_id"]
        == binding.OFFER_A_ID
    )


def test_valid_causal_offer_a_drives_existing_transaction_a() -> None:
    causal_run = _causal_run_for_offer(binding.OFFER_A_ID)
    report = runner.collect_tri_party_airline_ticket_purchase_mock_e2e_v01(
        semantic_causal_run=causal_run,
    )

    assert report["final_status"] == runner.STATUS_PASS
    assert (
        report["mock_protocol_fixtures"]["AirlineOfferCandidateV01"]["offer_id"]
        == binding.OFFER_A_ID
    )


def test_valid_causal_offer_b_drives_existing_transaction_b() -> None:
    causal_run = _causal_run_for_offer(binding.OFFER_B_ID)
    report = runner.collect_tri_party_airline_ticket_purchase_mock_e2e_v01(
        semantic_causal_run=causal_run,
    )

    assert report["final_status"] == runner.STATUS_PASS
    assert (
        report["mock_protocol_fixtures"]["AirlineOfferCandidateV01"]["offer_id"]
        == binding.OFFER_B_ID
    )
    assert report["final_tri_party_mock_summary"]["selected_offer_id"] == (
        binding.OFFER_B_ID
    )


def test_deterministic_runner_has_no_direct_offer_id_argument() -> None:
    import inspect

    signature = inspect.signature(
        runner.collect_tri_party_airline_ticket_purchase_mock_e2e_v01,
    )

    assert "offer_id" not in signature.parameters
    assert "selected_offer_id" not in signature.parameters
    assert "recommended_offer_id" not in signature.parameters


def test_airline_root_resolution_is_authoritative_source() -> None:
    causal_run = _causal_run_for_offer(binding.OFFER_B_ID)
    report = runner.collect_tri_party_airline_ticket_purchase_mock_e2e_v01(
        semantic_causal_run=causal_run,
    )
    offer = report["mock_protocol_fixtures"]["AirlineOfferCandidateV01"]

    assert causal_run.airline_root_resolution is not None
    assert offer["price_amount"] == causal_run.airline_root_resolution.resolved_amount
    assert offer["currency"] == causal_run.airline_root_resolution.resolved_currency
    assert offer["route_ref"] == causal_run.airline_root_resolution.resolved_route_ref


def test_provider_proposal_amount_is_not_used_as_authority() -> None:
    def provider(actor_id: str, request: Mapping[str, Any]) -> Mapping[str, Any]:
        if actor_id == binding.ACTOR_CLIENT_PURCHASE_INTENT_REVIEWER:
            payload = _proposal_payload(request, binding.OFFER_B_ID)
            payload["amount"] = 1
            return payload
        return _reviewer_payload(request)

    causal_run = causal_runtime.collect_airline_semantic_to_contract_causal_run_v01(
        scenario_id="provider_amount_injection",
        constraints=binding.build_client_constraints_preference_b_v01(),
        semantic_provider=provider,
    )
    report = runner.collect_tri_party_airline_ticket_purchase_mock_e2e_v01(
        semantic_causal_run=causal_run,
    )

    assert report["final_status"] == runner.STATUS_FAIL_CLOSED
    assert "semantic_causal_run_validation_rejected" in report["validation_errors"]


def test_invalid_causal_run_fails_before_corridor() -> None:
    causal_run = _causal_run_for_offer(binding.OFFER_A_ID)
    invalid = replace(causal_run, final_status=causal_runtime.STATUS_FAIL_CLOSED)
    report = runner.collect_tri_party_airline_ticket_purchase_mock_e2e_v01(
        semantic_causal_run=invalid,
    )

    assert report["final_status"] == runner.STATUS_FAIL_CLOSED
    assert report["counter_table"]["ticket_purchase_corridor_execution_count"] == 0


def test_causal_offer_mismatch_fails_closed() -> None:
    causal_run = _causal_run_for_offer(binding.OFFER_B_ID)
    invalid = replace(causal_run, root_selected_offer_id=binding.OFFER_A_ID)
    report = runner.collect_tri_party_airline_ticket_purchase_mock_e2e_v01(
        semantic_causal_run=invalid,
    )

    assert report["final_status"] == runner.STATUS_FAIL_CLOSED
    assert "semantic_causal_offer_chain_mismatch" in report["validation_errors"]


def test_one_deterministic_collection_one_corridor_execution() -> None:
    causal_run = _causal_run_for_offer(binding.OFFER_A_ID)
    report = runner.collect_tri_party_airline_ticket_purchase_mock_e2e_v01(
        semantic_causal_run=causal_run,
    )
    counters = report["counter_table"]

    assert counters["deterministic_airline_collection_count"] == 1
    assert counters["ticket_purchase_corridor_execution_count"] == 1


def test_no_default_or_silent_fallback() -> None:
    causal_run = _causal_run_for_offer(binding.OFFER_B_ID)
    report = runner.collect_tri_party_airline_ticket_purchase_mock_e2e_v01(
        semantic_causal_run=causal_run,
    )
    counters = report["counter_table"]

    assert counters["default_offer_count"] == 0
    assert counters["silent_fallback_count"] == 0


def test_deterministic_runner_contains_no_corridor_global_assignment() -> None:
    source = Path(runner.__file__).read_text()

    assert "corridor_contracts.OFFER_ID =" not in source
    assert "corridor_contracts.HOLD_ID =" not in source
    assert "corridor_contracts.AMOUNT =" not in source


def test_independent_a_b_a_runs_do_not_share_mutable_contract_state() -> None:
    original_constants = (
        runner.corridor_contracts.OFFER_ID,
        runner.corridor_contracts.HOLD_ID,
        runner.corridor_contracts.AMOUNT,
    )

    first_a = runner.collect_tri_party_airline_ticket_purchase_mock_e2e_v01(
        semantic_causal_run=_causal_run_for_offer(binding.OFFER_A_ID),
    )
    b_report = runner.collect_tri_party_airline_ticket_purchase_mock_e2e_v01(
        semantic_causal_run=_causal_run_for_offer(binding.OFFER_B_ID),
    )
    second_a = runner.collect_tri_party_airline_ticket_purchase_mock_e2e_v01(
        semantic_causal_run=_causal_run_for_offer(binding.OFFER_A_ID),
    )

    assert first_a["final_status"] == runner.STATUS_PASS
    assert b_report["final_status"] == runner.STATUS_PASS
    assert second_a["final_status"] == runner.STATUS_PASS
    assert first_a["final_tri_party_mock_summary"]["selected_offer_id"] == (
        binding.OFFER_A_ID
    )
    assert b_report["final_tri_party_mock_summary"]["selected_offer_id"] == (
        binding.OFFER_B_ID
    )
    assert second_a["final_tri_party_mock_summary"]["selected_offer_id"] == (
        binding.OFFER_A_ID
    )
    assert (
        runner.corridor_contracts.OFFER_ID,
        runner.corridor_contracts.HOLD_ID,
        runner.corridor_contracts.AMOUNT,
    ) == original_constants


def test_independent_b_a_b_runs_do_not_share_mutable_contract_state() -> None:
    first_b = runner.collect_tri_party_airline_ticket_purchase_mock_e2e_v01(
        semantic_causal_run=_causal_run_for_offer(binding.OFFER_B_ID),
    )
    a_report = runner.collect_tri_party_airline_ticket_purchase_mock_e2e_v01(
        semantic_causal_run=_causal_run_for_offer(binding.OFFER_A_ID),
    )
    second_b = runner.collect_tri_party_airline_ticket_purchase_mock_e2e_v01(
        semantic_causal_run=_causal_run_for_offer(binding.OFFER_B_ID),
    )

    assert first_b["final_status"] == runner.STATUS_PASS
    assert a_report["final_status"] == runner.STATUS_PASS
    assert second_b["final_status"] == runner.STATUS_PASS
    assert first_b["final_tri_party_mock_summary"]["selected_offer_id"] == (
        binding.OFFER_B_ID
    )
    assert a_report["final_tri_party_mock_summary"]["selected_offer_id"] == (
        binding.OFFER_A_ID
    )
    assert second_b["final_tri_party_mock_summary"]["selected_offer_id"] == (
        binding.OFFER_B_ID
    )


def test_a_report_validates_after_b_collection_under_a_context() -> None:
    a_report = runner.collect_tri_party_airline_ticket_purchase_mock_e2e_v01(
        semantic_causal_run=_causal_run_for_offer(binding.OFFER_A_ID),
    )
    runner.collect_tri_party_airline_ticket_purchase_mock_e2e_v01(
        semantic_causal_run=_causal_run_for_offer(binding.OFFER_B_ID),
    )
    fixture_bundle = runner._build_airline_ticket_purchase_corridor_fixture_bundle_v01(
        a_report,
    )
    corridor_report = a_report["airline_ticket_purchase_corridor_v0_1"]

    accepted, errors = (
        runner.corridor_runtime
        .validate_airline_ticket_purchase_corridor_report_against_fixture_bundle_v01(
            fixture_bundle,
            corridor_report,
            contract_context=corridor_report.contract_context,
        )
    )

    assert accepted is True
    assert errors == ()
    assert runner._validate_report(a_report) == ()


def test_b_report_validates_after_a_collection_under_b_context() -> None:
    b_report = runner.collect_tri_party_airline_ticket_purchase_mock_e2e_v01(
        semantic_causal_run=_causal_run_for_offer(binding.OFFER_B_ID),
    )
    runner.collect_tri_party_airline_ticket_purchase_mock_e2e_v01(
        semantic_causal_run=_causal_run_for_offer(binding.OFFER_A_ID),
    )
    fixture_bundle = runner._build_airline_ticket_purchase_corridor_fixture_bundle_v01(
        b_report,
    )
    corridor_report = b_report["airline_ticket_purchase_corridor_v0_1"]

    accepted, errors = (
        runner.corridor_runtime
        .validate_airline_ticket_purchase_corridor_report_against_fixture_bundle_v01(
            fixture_bundle,
            corridor_report,
            contract_context=corridor_report.contract_context,
        )
    )

    assert accepted is True
    assert errors == ()
    assert runner._validate_report(b_report) == ()
