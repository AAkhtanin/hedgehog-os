from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from hedgehog.domains.airline import ticket_purchase_corridor_v01 as corridor


def _fixtures() -> dict[str, object]:
    return {
        "airline_offer_hold_gate": (
            corridor.build_valid_airline_root_offer_hold_gate_v01()
        ),
        "offer_packet": corridor.build_valid_airline_offer_packet_v01(),
        "hold_packet": corridor.build_valid_airline_hold_commit_packet_v01(),
        "hold_receipt": corridor.build_valid_airline_offer_hold_receipt_v01(),
        "client_purchase_gate": (
            corridor.build_valid_client_root_purchase_intent_gate_v01()
        ),
        "human_approval": corridor.build_valid_human_approval_evidence_ref_v01(),
        "purchase_intent": corridor.build_valid_client_purchase_intent_v01(),
        "bank_gate": corridor.build_valid_bank_root_payment_authorization_gate_v01(),
        "authorization_ref": (
            corridor.build_valid_bank_payment_authorization_ref_v01()
        ),
        "airline_ticket_gate": (
            corridor.build_valid_airline_root_ticket_issue_gate_v01()
        ),
        "ticket_issue_intent": (
            corridor.build_valid_airline_ticket_issue_intent_v01()
        ),
        "ticket_receipt": corridor.build_valid_mock_ticket_receipt_v01(),
        "completion_gate": corridor.build_valid_client_root_completion_gate_v01(),
        "purchase_receipt": corridor.build_valid_mock_purchase_receipt_v01(),
    }


def _chain_report(**overrides: object) -> corridor.AirlineCorridorValidationReportV01:
    fixtures = _fixtures()
    fixtures.update(overrides)
    return corridor.validate_corridor_dependency_chain_v01(
        fixtures["airline_offer_hold_gate"],
        fixtures["offer_packet"],
        fixtures["hold_packet"],
        fixtures["hold_receipt"],
        fixtures["client_purchase_gate"],
        fixtures["human_approval"],
        fixtures["purchase_intent"],
        fixtures["bank_gate"],
        fixtures["authorization_ref"],
        fixtures["airline_ticket_gate"],
        fixtures["ticket_issue_intent"],
        fixtures["ticket_receipt"],
        fixtures["completion_gate"],
        fixtures["purchase_receipt"],
    )


def _assert_pass(report: corridor.AirlineCorridorValidationReportV01) -> None:
    assert report.validation_status == corridor.PASS
    assert report.reason_codes == ()
    assert report.return_to_root_required is False
    assert report.real_world_effects_count == 0


def _assert_fails_with(
    report: corridor.AirlineCorridorValidationReportV01,
    reason: str,
) -> None:
    assert report.validation_status == corridor.FAIL_CLOSED
    assert report.return_to_root_required is True
    assert reason in report.reason_codes


def test_valid_airline_offer_packet_passes() -> None:
    report = corridor.validate_airline_offer_packet_v01(
        corridor.build_valid_airline_offer_packet_v01(),
    )

    _assert_pass(report)


def test_valid_airline_hold_commit_packet_passes() -> None:
    report = corridor.validate_airline_hold_commit_packet_v01(
        corridor.build_valid_airline_offer_packet_v01(),
        corridor.build_valid_airline_hold_commit_packet_v01(),
    )

    _assert_pass(report)


def test_valid_offer_hold_receipt_is_evidence_only() -> None:
    receipt = corridor.build_valid_airline_offer_hold_receipt_v01()
    report = corridor.validate_airline_offer_hold_receipt_v01(
        corridor.build_valid_airline_hold_commit_packet_v01(),
        receipt,
    )

    _assert_pass(report)
    assert receipt.evidence_only is True
    assert receipt.payment_permission_created is False
    assert receipt.ticket_permission_created is False


def test_valid_client_purchase_intent_after_offer_hold_passes() -> None:
    report = corridor.validate_client_purchase_intent_v01(
        corridor.build_valid_human_approval_evidence_ref_v01(),
        corridor.build_valid_airline_offer_packet_v01(),
        corridor.build_valid_airline_offer_hold_receipt_v01(),
        corridor.build_valid_client_purchase_intent_v01(),
    )

    _assert_pass(report)


def test_valid_bank_payment_authorization_ref_passes() -> None:
    report = corridor.validate_bank_payment_authorization_ref_v01(
        corridor.build_valid_client_purchase_intent_v01(),
        corridor.build_valid_bank_payment_authorization_ref_v01(),
    )

    _assert_pass(report)


def test_valid_airline_ticket_issue_intent_passes() -> None:
    report = corridor.validate_airline_ticket_issue_intent_v01(
        corridor.build_valid_airline_offer_packet_v01(),
        corridor.build_valid_airline_hold_commit_packet_v01(),
        corridor.build_valid_airline_offer_hold_receipt_v01(),
        corridor.build_valid_client_purchase_intent_v01(),
        corridor.build_valid_bank_payment_authorization_ref_v01(),
        corridor.build_valid_airline_ticket_issue_intent_v01(),
    )

    _assert_pass(report)


def test_valid_mock_ticket_receipt_is_evidence_only() -> None:
    receipt = corridor.build_valid_mock_ticket_receipt_v01()
    report = corridor.validate_mock_ticket_receipt_v01(
        corridor.build_valid_airline_ticket_issue_intent_v01(),
        receipt,
    )

    _assert_pass(report)
    assert receipt.evidence_only is True
    assert receipt.real_ticket is False


def test_valid_mock_purchase_receipt_is_evidence_only() -> None:
    receipt = corridor.build_valid_mock_purchase_receipt_v01()
    report = corridor.validate_mock_purchase_receipt_v01(
        corridor.build_valid_client_purchase_intent_v01(),
        corridor.build_valid_bank_payment_authorization_ref_v01(),
        corridor.build_valid_mock_ticket_receipt_v01(),
        receipt,
    )

    _assert_pass(report)
    assert receipt.evidence_only is True
    assert receipt.future_permission_created is False


def test_full_contract_dependency_chain_passes() -> None:
    _assert_pass(_chain_report())


def test_side_specific_root_phase_gates_pass() -> None:
    for gate in (
        corridor.build_valid_airline_root_offer_hold_gate_v01(),
        corridor.build_valid_client_root_purchase_intent_gate_v01(),
        corridor.build_valid_bank_root_payment_authorization_gate_v01(),
        corridor.build_valid_airline_root_ticket_issue_gate_v01(),
        corridor.build_valid_client_root_completion_gate_v01(),
    ):
        _assert_pass(corridor.validate_root_phase_gate_v01(gate))


def test_human_approval_is_scoped_evidence_for_client_root() -> None:
    evidence = corridor.build_valid_human_approval_evidence_ref_v01()
    report = corridor.validate_human_approval_evidence_ref_v01(evidence)

    _assert_pass(report)
    assert evidence.evidence_only is True
    assert evidence.creates_client_purchase_intent is False
    assert evidence.creates_action_commit_packet is False


def test_receipts_do_not_create_future_permission() -> None:
    report = corridor.validate_receipts_evidence_only_v01(
        corridor.build_valid_airline_offer_hold_receipt_v01(),
        corridor.build_valid_mock_ticket_receipt_v01(),
        corridor.build_valid_mock_purchase_receipt_v01(),
    )

    _assert_pass(report)


def test_no_cross_root_authority_transfer() -> None:
    report = corridor.validate_no_cross_root_authority_transfer_v01(
        corridor.build_valid_airline_root_offer_hold_gate_v01(),
        corridor.build_valid_client_purchase_intent_v01(),
        corridor.build_valid_mock_purchase_receipt_v01(),
    )

    _assert_pass(report)


def test_all_valid_fixtures_have_zero_real_effects() -> None:
    report = corridor.validate_no_real_effects_v01(*_fixtures().values())

    _assert_pass(report)


def test_client_purchase_intent_before_offer_hold_rejected() -> None:
    report = corridor.validate_client_purchase_intent_v01(
        corridor.build_valid_human_approval_evidence_ref_v01(),
        corridor.build_valid_airline_offer_packet_v01(),
        None,
        corridor.build_valid_client_purchase_intent_v01(),
    )

    _assert_fails_with(report, corridor.REASON_PURCHASE_INTENT_BEFORE_OFFER_HOLD)


def test_client_purchase_intent_without_selected_offer_rejected() -> None:
    report = corridor.validate_client_purchase_intent_v01(
        corridor.build_valid_human_approval_evidence_ref_v01(),
        None,
        corridor.build_valid_airline_offer_hold_receipt_v01(),
        corridor.build_valid_client_purchase_intent_v01(),
    )

    _assert_fails_with(report, corridor.REASON_MISSING_OFFER_PACKET)


def test_global_side_root_reviews_completed_shortcut_rejected() -> None:
    gate = replace(
        corridor.build_valid_client_root_purchase_intent_gate_v01(),
        phase_id=corridor.PHASE_GLOBAL_SIDE_ROOT_REVIEWS_COMPLETED,
    )
    report = corridor.validate_root_phase_gate_v01(gate)

    _assert_fails_with(
        report,
        corridor.REASON_GLOBAL_SIDE_ROOT_REVIEWS_COMPLETED_SHORTCUT_REJECTED,
    )


def test_airline_root_review_cannot_replace_client_root_review() -> None:
    gate = replace(
        corridor.build_valid_client_root_purchase_intent_gate_v01(),
        root_id=corridor.AIRLINE_ROOT_ID,
    )
    report = corridor.validate_root_phase_gate_v01(gate)

    _assert_fails_with(report, corridor.REASON_WRONG_ROOT_OWNER)


def test_client_root_review_cannot_replace_bank_root_review() -> None:
    gate = replace(
        corridor.build_valid_bank_root_payment_authorization_gate_v01(),
        root_id=corridor.CLIENT_ROOT_ID,
    )
    report = corridor.validate_root_phase_gate_v01(gate)

    _assert_fails_with(report, corridor.REASON_WRONG_ROOT_OWNER)


def test_bank_root_review_cannot_replace_airline_ticket_issue_review() -> None:
    gate = replace(
        corridor.build_valid_airline_root_ticket_issue_gate_v01(),
        root_id=corridor.BANK_ROOT_ID,
    )
    report = corridor.validate_root_phase_gate_v01(gate)

    _assert_fails_with(report, corridor.REASON_WRONG_ROOT_OWNER)


def test_phase_failure_cannot_be_repaired_by_later_phase() -> None:
    hold_packet = replace(
        corridor.build_valid_airline_hold_commit_packet_v01(),
        expired=True,
    )
    report = _chain_report(hold_packet=hold_packet)

    _assert_fails_with(report, corridor.REASON_EXPIRED_HOLD)
    assert corridor.REASON_PHASE_FAILURE_CANNOT_BE_REPAIRED_BY_LATER_PHASE in (
        report.reason_codes
    )


def test_human_approval_directly_creating_purchase_intent_rejected() -> None:
    evidence = replace(
        corridor.build_valid_human_approval_evidence_ref_v01(),
        creates_client_purchase_intent=True,
    )
    report = corridor.validate_human_approval_evidence_ref_v01(evidence)

    _assert_fails_with(
        report,
        corridor.REASON_HUMAN_APPROVAL_CANNOT_CREATE_PURCHASE_INTENT,
    )


def test_human_approval_directly_creating_action_commit_packet_rejected() -> None:
    evidence = replace(
        corridor.build_valid_human_approval_evidence_ref_v01(),
        creates_action_commit_packet=True,
    )
    report = corridor.validate_human_approval_evidence_ref_v01(evidence)

    _assert_fails_with(
        report,
        corridor.REASON_HUMAN_APPROVAL_CANNOT_CREATE_ACTION_COMMIT_PACKET,
    )


def test_human_approval_amount_scope_mismatch_rejected() -> None:
    purchase_intent = replace(
        corridor.build_valid_client_purchase_intent_v01(),
        selected_amount=corridor.MAX_AMOUNT + 1,
    )
    report = corridor.validate_client_purchase_intent_v01(
        corridor.build_valid_human_approval_evidence_ref_v01(),
        corridor.build_valid_airline_offer_packet_v01(),
        corridor.build_valid_airline_offer_hold_receipt_v01(),
        purchase_intent,
    )

    _assert_fails_with(report, corridor.REASON_AMOUNT_EXCEEDS_HUMAN_APPROVAL)


def test_human_approval_offer_scope_mismatch_rejected() -> None:
    evidence = replace(
        corridor.build_valid_human_approval_evidence_ref_v01(),
        selected_offer_id="offer:mock_airline_al:PAR-LIM:other",
    )
    report = corridor.validate_client_purchase_intent_v01(
        evidence,
        corridor.build_valid_airline_offer_packet_v01(),
        corridor.build_valid_airline_offer_hold_receipt_v01(),
        corridor.build_valid_client_purchase_intent_v01(),
    )

    _assert_fails_with(report, corridor.REASON_SELECTED_OFFER_MISMATCH)


def test_provider_created_offer_packet_rejected() -> None:
    packet = replace(
        corridor.build_valid_airline_offer_packet_v01(),
        created_by="semantic_provider_llm",
    )
    report = corridor.validate_airline_offer_packet_v01(packet)

    _assert_fails_with(
        report,
        corridor.REASON_PROVIDER_CANNOT_CREATE_CONTRACT_ARTIFACT,
    )


def test_provider_created_purchase_intent_rejected() -> None:
    purchase_intent = replace(
        corridor.build_valid_client_purchase_intent_v01(),
        created_by="semantic_provider_llm",
    )
    report = corridor.validate_client_purchase_intent_v01(
        corridor.build_valid_human_approval_evidence_ref_v01(),
        corridor.build_valid_airline_offer_packet_v01(),
        corridor.build_valid_airline_offer_hold_receipt_v01(),
        purchase_intent,
    )

    _assert_fails_with(
        report,
        corridor.REASON_PROVIDER_CANNOT_CREATE_CONTRACT_ARTIFACT,
    )


def test_provider_created_ticket_issue_intent_rejected() -> None:
    ticket_issue_intent = replace(
        corridor.build_valid_airline_ticket_issue_intent_v01(),
        created_by="semantic_provider_llm",
    )
    report = corridor.validate_airline_ticket_issue_intent_v01(
        corridor.build_valid_airline_offer_packet_v01(),
        corridor.build_valid_airline_hold_commit_packet_v01(),
        corridor.build_valid_airline_offer_hold_receipt_v01(),
        corridor.build_valid_client_purchase_intent_v01(),
        corridor.build_valid_bank_payment_authorization_ref_v01(),
        ticket_issue_intent,
    )

    _assert_fails_with(
        report,
        corridor.REASON_PROVIDER_CANNOT_CREATE_CONTRACT_ARTIFACT,
    )


def test_wrong_root_owner_rejected() -> None:
    packet = replace(
        corridor.build_valid_airline_offer_packet_v01(),
        root_owner=corridor.CLIENT_ROOT_ID,
    )
    report = corridor.validate_airline_offer_packet_v01(packet)

    _assert_fails_with(report, corridor.REASON_WRONG_ROOT_OWNER)


def test_cross_root_evidence_does_not_transfer_authority() -> None:
    purchase_intent = replace(
        corridor.build_valid_client_purchase_intent_v01(),
        bank_authority_created=True,
    )
    report = corridor.validate_no_cross_root_authority_transfer_v01(
        purchase_intent,
    )

    _assert_fails_with(report, corridor.REASON_CROSS_ROOT_AUTHORITY_TRANSFER)


def test_mixed_transaction_id_rejected() -> None:
    authorization_ref = replace(
        corridor.build_valid_bank_payment_authorization_ref_v01(),
        transaction_id="tri_airline_purchase:mixed",
    )
    report = corridor.validate_bank_payment_authorization_ref_v01(
        corridor.build_valid_client_purchase_intent_v01(),
        authorization_ref,
    )

    _assert_fails_with(report, corridor.REASON_MIXED_TRANSACTION_ID)


def test_offer_id_mismatch_rejected() -> None:
    hold_packet = replace(
        corridor.build_valid_airline_hold_commit_packet_v01(),
        offer_id="offer:mock_airline_al:PAR-LIM:wrong",
    )
    report = corridor.validate_airline_hold_commit_packet_v01(
        corridor.build_valid_airline_offer_packet_v01(),
        hold_packet,
    )

    _assert_fails_with(report, corridor.REASON_SELECTED_OFFER_MISMATCH)


def test_hold_id_mismatch_rejected() -> None:
    receipt = replace(
        corridor.build_valid_airline_offer_hold_receipt_v01(),
        hold_id="hold:mock_airline_al:wrong",
    )
    report = corridor.validate_airline_offer_hold_receipt_v01(
        corridor.build_valid_airline_hold_commit_packet_v01(),
        receipt,
    )

    _assert_fails_with(report, corridor.REASON_HOLD_ID_MISMATCH)


def test_passenger_ref_mismatch_rejected() -> None:
    authorization_ref = replace(
        corridor.build_valid_bank_payment_authorization_ref_v01(),
        passenger_ref="sealed_passenger_ref:client_001:pax_wrong",
    )
    report = corridor.validate_bank_payment_authorization_ref_v01(
        corridor.build_valid_client_purchase_intent_v01(),
        authorization_ref,
    )

    _assert_fails_with(report, corridor.REASON_PASSENGER_REF_MISMATCH)


def test_route_ref_mismatch_rejected() -> None:
    purchase_intent = replace(
        corridor.build_valid_client_purchase_intent_v01(),
        route_ref="route:PAR-LIM:wrong",
    )
    report = corridor.validate_client_purchase_intent_v01(
        corridor.build_valid_human_approval_evidence_ref_v01(),
        corridor.build_valid_airline_offer_packet_v01(),
        corridor.build_valid_airline_offer_hold_receipt_v01(),
        purchase_intent,
    )

    _assert_fails_with(report, corridor.REASON_ROUTE_REF_MISMATCH)


def test_amount_mismatch_rejected() -> None:
    ticket_issue_intent = replace(
        corridor.build_valid_airline_ticket_issue_intent_v01(),
        amount=corridor.AMOUNT + 1,
    )
    report = corridor.validate_airline_ticket_issue_intent_v01(
        corridor.build_valid_airline_offer_packet_v01(),
        corridor.build_valid_airline_hold_commit_packet_v01(),
        corridor.build_valid_airline_offer_hold_receipt_v01(),
        corridor.build_valid_client_purchase_intent_v01(),
        corridor.build_valid_bank_payment_authorization_ref_v01(),
        ticket_issue_intent,
    )

    _assert_fails_with(report, corridor.REASON_AMOUNT_MISMATCH)


def test_currency_mismatch_rejected() -> None:
    hold_packet = replace(
        corridor.build_valid_airline_hold_commit_packet_v01(),
        currency="USD",
    )
    report = corridor.validate_airline_hold_commit_packet_v01(
        corridor.build_valid_airline_offer_packet_v01(),
        hold_packet,
    )

    _assert_fails_with(report, corridor.REASON_CURRENCY_MISMATCH)


def test_merchant_mismatch_rejected() -> None:
    authorization_ref = replace(
        corridor.build_valid_bank_payment_authorization_ref_v01(),
        merchant_ref="merchant_ref:wrong",
    )
    report = corridor.validate_bank_payment_authorization_ref_v01(
        corridor.build_valid_client_purchase_intent_v01(),
        authorization_ref,
    )

    _assert_fails_with(report, corridor.REASON_MERCHANT_MISMATCH)


def test_expired_hold_rejected() -> None:
    hold_packet = replace(
        corridor.build_valid_airline_hold_commit_packet_v01(),
        expired=True,
    )
    report = corridor.validate_airline_hold_commit_packet_v01(
        corridor.build_valid_airline_offer_packet_v01(),
        hold_packet,
    )

    _assert_fails_with(report, corridor.REASON_EXPIRED_HOLD)


def test_expired_payment_authorization_rejected() -> None:
    authorization_ref = replace(
        corridor.build_valid_bank_payment_authorization_ref_v01(),
        expired=True,
    )
    report = corridor.validate_bank_payment_authorization_ref_v01(
        corridor.build_valid_client_purchase_intent_v01(),
        authorization_ref,
    )

    _assert_fails_with(report, corridor.REASON_EXPIRED_PAYMENT_AUTHORIZATION)


def test_child_ttl_cannot_exceed_parent_ttl() -> None:
    hold_packet = replace(
        corridor.build_valid_airline_hold_commit_packet_v01(),
        ttl_seconds=901,
    )
    report = corridor.validate_airline_hold_commit_packet_v01(
        corridor.build_valid_airline_offer_packet_v01(),
        hold_packet,
    )

    _assert_fails_with(report, corridor.REASON_CHILD_TTL_EXCEEDS_PARENT_TTL)


def test_duplicate_idempotency_key_pressure_rejected() -> None:
    hold_packet = replace(
        corridor.build_valid_airline_hold_commit_packet_v01(),
        idempotency_key="duplicate_idempotency_key:airline_hold:001",
    )
    report = corridor.validate_airline_hold_commit_packet_v01(
        corridor.build_valid_airline_offer_packet_v01(),
        hold_packet,
    )

    _assert_fails_with(report, corridor.REASON_DUPLICATE_IDEMPOTENCY_KEY)


def test_receipt_classified_as_permission_rejected() -> None:
    receipt = replace(
        corridor.build_valid_airline_offer_hold_receipt_v01(),
        purchase_permission_created=True,
    )
    report = corridor.validate_airline_offer_hold_receipt_v01(
        corridor.build_valid_airline_hold_commit_packet_v01(),
        receipt,
    )

    _assert_fails_with(report, corridor.REASON_RECEIPT_CREATED_PERMISSION)


def test_receipt_future_permission_rejected() -> None:
    receipt = replace(
        corridor.build_valid_mock_ticket_receipt_v01(),
        future_ticket_permission_created=True,
    )
    report = corridor.validate_mock_ticket_receipt_v01(
        corridor.build_valid_airline_ticket_issue_intent_v01(),
        receipt,
    )

    _assert_fails_with(report, corridor.REASON_RECEIPT_CREATED_FUTURE_PERMISSION)


def test_purchase_receipt_root_truth_rewrite_rejected() -> None:
    receipt = replace(
        corridor.build_valid_mock_purchase_receipt_v01(),
        root_truth_rewritten=True,
    )
    report = corridor.validate_mock_purchase_receipt_v01(
        corridor.build_valid_client_purchase_intent_v01(),
        corridor.build_valid_bank_payment_authorization_ref_v01(),
        corridor.build_valid_mock_ticket_receipt_v01(),
        receipt,
    )

    _assert_fails_with(report, corridor.REASON_RECEIPT_REWROTE_ROOT_TRUTH)


def test_mock_ticket_becoming_real_ticket_rejected() -> None:
    receipt = replace(corridor.build_valid_mock_ticket_receipt_v01(), real_ticket=True)
    report = corridor.validate_mock_ticket_receipt_v01(
        corridor.build_valid_airline_ticket_issue_intent_v01(),
        receipt,
    )

    _assert_fails_with(report, corridor.REASON_REAL_TICKET_FORBIDDEN)


def test_mock_purchase_becoming_real_payment_rejected() -> None:
    receipt = replace(
        corridor.build_valid_mock_purchase_receipt_v01(),
        real_payment_executed=True,
    )
    report = corridor.validate_mock_purchase_receipt_v01(
        corridor.build_valid_client_purchase_intent_v01(),
        corridor.build_valid_bank_payment_authorization_ref_v01(),
        corridor.build_valid_mock_ticket_receipt_v01(),
        receipt,
    )

    _assert_fails_with(report, corridor.REASON_REAL_PAYMENT_FORBIDDEN)


def test_real_booking_claim_rejected() -> None:
    receipt = replace(
        corridor.build_valid_mock_purchase_receipt_v01(),
        real_booking_created=True,
    )
    report = corridor.validate_mock_purchase_receipt_v01(
        corridor.build_valid_client_purchase_intent_v01(),
        corridor.build_valid_bank_payment_authorization_ref_v01(),
        corridor.build_valid_mock_ticket_receipt_v01(),
        receipt,
    )

    _assert_fails_with(report, corridor.REASON_REAL_BOOKING_FORBIDDEN)


def test_post_root_reasoning_restart_rejected() -> None:
    gate = replace(
        corridor.build_valid_airline_root_offer_hold_gate_v01(),
        post_root_reasoning_restarted=True,
    )
    report = corridor.validate_root_phase_gate_v01(gate)

    _assert_fails_with(
        report,
        corridor.REASON_POST_ROOT_REASONING_RESTART_FORBIDDEN,
    )


def test_nonzero_real_world_effects_rejected() -> None:
    packet = replace(
        corridor.build_valid_airline_offer_packet_v01(),
        real_world_effects_count=1,
    )
    report = corridor.validate_airline_offer_packet_v01(packet)

    _assert_fails_with(report, corridor.REASON_NONZERO_REAL_WORLD_EFFECTS)


def test_airline_corridor_source_boundary() -> None:
    source = Path(corridor.__file__).read_text(encoding="utf-8")

    for forbidden in (
        "google.genai",
        "requests",
        "urllib",
        "openai",
        "subprocess",
        "import config",
        "run_tri_party_airline_live_semantic_lane",
        "build_real_airline_semantic_provider",
        "ArtifactLedger",
        "CryptoArtifactSeal",
        "SealedTraceReplay",
        "production " + "ready",
        "public " + "auditor " + "ready",
    ):
        assert forbidden not in source
    assert "provider(" not in source
    assert "generate_content" not in source
    assert corridor.ACTIONCOMMITPACKET_CONTAINMENT_LAWS_REUSED


def test_airline_corridor_module_is_domain_projection_not_flat_core() -> None:
    assert (
        corridor.__name__
        == "hedgehog.domains.airline.ticket_purchase_corridor_v01"
    )
    assert not Path("hedgehog/airline_ticket_purchase_corridor_v01.py").exists()
    assert corridor.__doc__ is not None
    assert "Airline domain contract projection" in corridor.__doc__
    assert "not Hedgehog OS universal kernel/core" in corridor.__doc__
    assert "not an installed Needle" in corridor.__doc__


def test_universal_core_does_not_import_airline_domain() -> None:
    for path in (
        Path("hedgehog/action_commit_packet_v02.py"),
        Path("hedgehog/avf_v02.py"),
        Path("hedgehog/local_drs_v02.py"),
    ):
        source = path.read_text(encoding="utf-8")
        assert "hedgehog.domains.airline" not in source
        assert "AirlineOfferPacket" not in source
        assert "AirlineTicketIssueIntent" not in source
        assert "MockPNR" not in source
        assert "airline_ticket_purchase_corridor" not in source
