from __future__ import annotations

from typing import Any, Mapping


RUN_ID = "tri_party_airline_ticket_purchase_mock_e2e_v01"
REPORT_ID = "tri_party_airline_ticket_purchase_mock_e2e_v01"
SLICE_ID = "tri_party_airline_ticket_purchase_mock_e2e_v01_slice_g"
TRANSACTION_ID = "tri_airline_purchase:PAR-LIM:2026-08-12:client_001"

STATUS_PASS = "PASS"
STATUS_FAIL_CLOSED = "FAIL_CLOSED"

CLIENT_ROOT_ID = "root:client_os_001"
AIRLINE_ROOT_ID = "root:mock_airline_al"
BANK_ROOT_ID = "root:mock_bank_a"

REQUIRED_SECTIONS = (
    "[TRI-PARTY AIRLINE TICKET PURCHASE MOCK E2E V0.1]",
    "[WHAT THIS SLICE IS]",
    "[ONE TRANSACTION / THREE ROOTS]",
    "[CLIENT ROOT VIEW]",
    "[AIRLINE ROOT VIEW]",
    "[BANK ROOT VIEW]",
    "[AIRLINEROOT OFFER HOLD SANDBOX]",
    "[BANKROOT PAYMENT AUTHORIZATION SANDBOX]",
    "[CLIENTROOT PURCHASE ORCHESTRATION]",
    "[AIRLINEROOT TICKET ISSUE MOCK CORRIDOR]",
    "[INTEGRATED TRI-PARTY TRANSACTION TRACE]",
    "[CROSS-ROOT EVIDENCE ROUTING MATRIX]",
    "[FINAL TRI-PARTY MOCK SUMMARY]",
    "[MOCK PROTOCOL FIXTURES]",
    "[SHARED TRANSACTION LEDGER]",
    "[ROOT BOUNDARY MATRIX]",
    "[RECEIPT BOUNDARY MATRIX]",
    "[PRIVACY / SEALED REF BOUNDARY]",
    "[NON-ACTION REUSE CONSTRAINTS]",
    "[FUTURE SEMANTIC ACTOR TOPOLOGY]",
    "[FUTURE VERTICAL FRACTAL MAP]",
    "[COUNTER TABLE]",
    "[NON-CLAIMS]",
    "[NEXT GATE]",
    "[FINAL STATUS]",
)


def collect_tri_party_airline_ticket_purchase_mock_e2e_v01() -> dict[str, Any]:
    transaction_identity = _transaction_identity()
    participants = _participants()
    travel_intent = _travel_intent()
    sealed_refs = _sealed_refs()
    mock_protocol_fixtures = _mock_protocol_fixtures(travel_intent, sealed_refs)
    airline_offer_hold_sandbox = _airline_offer_hold_sandbox(mock_protocol_fixtures)
    bank_payment_authorization_sandbox = _bank_payment_authorization_sandbox(
        mock_protocol_fixtures,
        sealed_refs,
    )
    client_purchase_orchestration = _client_purchase_orchestration(
        travel_intent,
        sealed_refs,
        mock_protocol_fixtures,
    )
    airline_ticket_issue_mock_corridor = _airline_ticket_issue_mock_corridor(
        mock_protocol_fixtures,
    )
    shared_transaction_ledger = _shared_transaction_ledger(mock_protocol_fixtures)
    integrated_transaction_trace = _integrated_transaction_trace(
        mock_protocol_fixtures,
    )
    cross_root_evidence_routing_matrix = _cross_root_evidence_routing_matrix()
    final_tri_party_mock_summary = _final_tri_party_mock_summary()
    future_semantic_actor_topology = _future_semantic_actor_topology()
    future_vertical_fractal_map = _future_vertical_fractal_map()
    privacy_boundary_matrix = _privacy_boundary_matrix()
    counter_table = _counter_table(
        shared_transaction_ledger,
        future_semantic_actor_topology,
        future_vertical_fractal_map,
        airline_offer_hold_sandbox,
        bank_payment_authorization_sandbox,
        client_purchase_orchestration,
        airline_ticket_issue_mock_corridor,
        integrated_transaction_trace,
        cross_root_evidence_routing_matrix,
        final_tri_party_mock_summary,
    )

    report: dict[str, Any] = {
        "run_id": RUN_ID,
        "report_id": REPORT_ID,
        "slice_id": SLICE_ID,
        "final_status": STATUS_PASS,
        "transaction_id": TRANSACTION_ID,
        "transaction_identity": transaction_identity,
        "participants": participants,
        "travel_intent": travel_intent,
        "sealed_refs": sealed_refs,
        "client_root_view": _client_root_view(participants, mock_protocol_fixtures),
        "airline_root_view": _airline_root_view(participants, mock_protocol_fixtures),
        "bank_root_view": _bank_root_view(participants, mock_protocol_fixtures),
        "airline_offer_hold_sandbox": airline_offer_hold_sandbox,
        "bank_payment_authorization_sandbox": bank_payment_authorization_sandbox,
        "client_purchase_orchestration": client_purchase_orchestration,
        "airline_ticket_issue_mock_corridor": airline_ticket_issue_mock_corridor,
        "integrated_transaction_trace": integrated_transaction_trace,
        "cross_root_evidence_routing_matrix": cross_root_evidence_routing_matrix,
        "final_tri_party_mock_summary": final_tri_party_mock_summary,
        "mock_protocol_fixtures": mock_protocol_fixtures,
        "shared_transaction_ledger": shared_transaction_ledger,
        "root_boundary_matrix": _root_boundary_matrix(),
        "receipt_boundary_matrix": _receipt_boundary_matrix(),
        "privacy_boundary_matrix": privacy_boundary_matrix,
        "non_action_reuse_constraints": _non_action_reuse_constraints(),
        "future_semantic_actor_topology": future_semantic_actor_topology,
        "future_vertical_fractal_map": future_vertical_fractal_map,
        "counter_table": counter_table,
        "non_claims": _non_claims(),
        "validation_errors": (),
        "next_gate": "Slice H three human renderers",
    }
    errors = _validate_report(report)
    if errors:
        report["final_status"] = STATUS_FAIL_CLOSED
        report["validation_errors"] = errors
    return report


def render_tri_party_airline_ticket_purchase_mock_e2e_v01(
    report: Mapping[str, Any],
) -> str:
    lines: list[str] = [
        "[TRI-PARTY AIRLINE TICKET PURCHASE MOCK E2E V0.1]",
        f"run_id: {report['run_id']}",
        f"report_id: {report['report_id']}",
        f"slice_id: {report['slice_id']}",
        "",
        "[WHAT THIS SLICE IS]",
        (
            "This slice creates one mock airline purchase transaction skeleton, "
            "not three unrelated demos."
        ),
        "The fixtures look like real airline/payment protocol phases but are mock-only.",
        "",
        "[ONE TRANSACTION / THREE ROOTS]",
        f"transaction_id: {report['transaction_id']}",
        "ClientRoot, AirlineRoot, and BankRoot each see a bounded view of the same transaction.",
        "",
        "[CLIENT ROOT VIEW]",
        _format_view(report["client_root_view"]),
        "",
        "[AIRLINE ROOT VIEW]",
        _format_view(report["airline_root_view"]),
        "",
        "[BANK ROOT VIEW]",
        _format_view(report["bank_root_view"]),
        "",
        "[AIRLINEROOT OFFER HOLD SANDBOX]",
        "AirlineRoot received offer request.",
        "AirlineRoot checked mock inventory.",
        "AirlineRoot checked mock fare.",
        "AirlineRoot checked baggage rule.",
        "AirlineRoot checked offer TTL.",
        "AirlineRoot created OfferResponse.",
        "AirlineRoot created AirlineOfferHoldCommitPacket.",
        "AirlineRoot created OfferHoldReceipt.",
        "OfferHoldReceipt is evidence only.",
        "OfferHoldReceipt is not payment permission.",
        "OfferHoldReceipt is not ticket permission.",
        "No real airline API was called.",
        "No real booking was created.",
        f"sandbox_status: {report['airline_offer_hold_sandbox']['sandbox_status']}",
        "",
        "[BANKROOT PAYMENT AUTHORIZATION SANDBOX]",
        "BankRoot received mock payment authorization request.",
        "BankRoot validated selected offer amount/currency against OfferHoldReceipt.",
        "BankRoot validated merchant/airline ref.",
        "BankRoot validated payment token sealed ref.",
        "BankRoot validated debtor slot ref.",
        "BankRoot validated idempotency.",
        "BankRoot validated expiry/TTL.",
        "BankRoot created BankPaymentIntent.",
        "BankRoot created BankPaymentConsent.",
        "BankRoot created BankPaymentAuthorizationCommitPacket.",
        "BankRoot created PaymentAuthorizationReceipt.",
        "BankRoot created PaymentStatusReceipt.",
        "PaymentAuthorizationReceipt is evidence only.",
        "PaymentAuthorizationReceipt is not ticket permission.",
        "PaymentStatusReceipt is evidence only.",
        "BankRoot does not create ticket.",
        "BankRoot does not call real bank API.",
        "No real payment was executed.",
        "No real settlement happened.",
        f"sandbox_status: {report['bank_payment_authorization_sandbox']['sandbox_status']}",
        "",
        "[CLIENTROOT PURCHASE ORCHESTRATION]",
        "ClientRoot received the travel intent.",
        "ClientRoot observed AirlineRoot OfferResponse.",
        "ClientRoot observed OfferHoldReceipt as evidence only.",
        "ClientRoot selected the mock offer.",
        "ClientRoot created ClientPurchaseApprovalEvidence.",
        "ClientRoot routed bounded purchase approval evidence to BankRoot.",
        "ClientRoot routed bounded selected-offer evidence to AirlineRoot.",
        "ClientRoot observed BankRoot PaymentAuthorizationReceipt as evidence only.",
        "ClientRoot observed PaymentStatusReceipt as evidence only.",
        "ClientRoot does not authorize bank payment.",
        "ClientRoot does not issue ticket.",
        "ClientRoot does not create airline order.",
        "ClientRoot does not create bank receipt.",
        "ClientRoot does not expose raw passport/card/IBAN/payment token.",
        "No real payment was executed.",
        "No real ticket was issued.",
        "No real booking was created.",
        f"orchestration_status: {report['client_purchase_orchestration']['orchestration_status']}",
        "",
        "[AIRLINEROOT TICKET ISSUE MOCK CORRIDOR]",
        "AirlineRoot observed OfferHoldReceipt as evidence only.",
        "AirlineRoot observed ClientPurchaseApprovalEvidence as evidence only.",
        "AirlineRoot observed BankRoot PaymentAuthorizationReceipt as evidence only.",
        "AirlineRoot observed PaymentStatusReceipt as evidence only.",
        "AirlineRoot validated offer hold TTL / freshness.",
        "AirlineRoot validated amount/currency/merchant match.",
        "AirlineRoot validated passenger sealed ref only.",
        "AirlineRoot validated no raw passport/card/payment token exposure.",
        "AirlineRoot created AirlineTicketIssueCommitPacket.",
        "AirlineRoot created AirlineOrderCreatedReceipt.",
        "AirlineRoot created MockTicketReceipt.",
        "AirlineRoot created MockPNR.",
        "MockTicketReceipt is evidence only.",
        "MockTicketReceipt is not a real ticket.",
        "MockPNR is not a real booking.",
        "PaymentAuthorizationReceipt does not automatically create ticket.",
        "ClientPurchaseApprovalEvidence does not authorize AirlineRoot by itself.",
        "No real airline API was called.",
        "No real ticket was issued.",
        "No real booking was created.",
        "No real payment or settlement happened.",
        f"corridor_status: {report['airline_ticket_issue_mock_corridor']['corridor_status']}",
        "",
        "[INTEGRATED TRI-PARTY TRANSACTION TRACE]",
        "This is one transaction, not three unrelated demos.",
        "Every phase carries the same transaction_id.",
        "ClientRoot, AirlineRoot, and BankRoot exchange evidence, not authority.",
        "Offer hold, payment authorization, and mock ticket evidence all remain evidence-only.",
        "No real payment, ticket, booking, API, provider, network, or Gemini call occurs.",
    ]
    for row in report["integrated_transaction_trace"]:
        lines.append(
            "{trace_index}. {phase_id}: {source_root_id} -> {target_root_id}".format(
                **row,
            ),
        )

    lines.extend(
        (
            "",
            "[CROSS-ROOT EVIDENCE ROUTING MATRIX]",
            "ClientRoot sends bounded offer request to AirlineRoot.",
            "AirlineRoot returns offer/hold evidence.",
            "ClientRoot sends purchase approval and payment profile sealed ref to BankRoot.",
            "BankRoot returns payment authorization/status evidence.",
            "ClientRoot forwards payment evidence to AirlineRoot.",
            "AirlineRoot returns mock order/ticket/PNR evidence.",
            "Every route transfers evidence only, not authority.",
        ),
    )
    for row in report["cross_root_evidence_routing_matrix"]:
        lines.append(
            "- {route_id}: {source_root_id} -> {target_root_id}; {artifact}".format(
                **row,
            ),
        )

    final_summary = report["final_tri_party_mock_summary"]
    lines.extend(
        (
            "",
            "[FINAL TRI-PARTY MOCK SUMMARY]",
            (
                "Client view: mock ticket evidence received, "
                "no real travel booking."
            ),
            (
                "Airline view: mock order/ticket/PNR evidence created, "
                "no real airline API."
            ),
            "Bank view: mock payment authorized/not settled, no real payment.",
            "Receipts remain evidence only.",
            "Root boundaries remain side-specific.",
            "No real-world effect occurred.",
            f"summary_id: {final_summary['summary_id']}",
            f"final_status: {final_summary['final_status']}",
        ),
    )
    lines.extend(
        (
            "",
        "[MOCK PROTOCOL FIXTURES]",
        ),
    )
    for fixture_name in report["mock_protocol_fixtures"]:
        lines.append(f"- {fixture_name}")

    lines.extend(("", "[SHARED TRANSACTION LEDGER]"))
    lines.append("shared transaction ledger")
    for row in report["shared_transaction_ledger"]:
        lines.append(
            "{ledger_index}. {event_type} -> {artifact_ref}".format(**row),
        )

    lines.extend(("", "[ROOT BOUNDARY MATRIX]"))
    for row in report["root_boundary_matrix"]:
        lines.append(
            f"- {row['boundary']}: preserved={row['boundary_preserved']}, violations={row['violation_count']}",
        )

    lines.extend(("", "[RECEIPT BOUNDARY MATRIX]"))
    lines.append("Receipt crosses roots as evidence, not authority.")
    for row in report["receipt_boundary_matrix"]:
        lines.append(
            f"- {row['boundary']}: preserved={row['boundary_preserved']}, violations={row['violation_count']}",
        )

    privacy = report["privacy_boundary_matrix"]
    lines.extend(
        (
            "",
            "[PRIVACY / SEALED REF BOUNDARY]",
            f"raw_passport_exposed_count: {privacy['raw_passport_exposed_count']}",
            f"raw_card_exposed_count: {privacy['raw_card_exposed_count']}",
            f"raw_iban_exposed_count: {privacy['raw_iban_exposed_count']}",
            f"raw_payment_token_exposed_count: {privacy['raw_payment_token_exposed_count']}",
        ),
    )

    lines.extend(("", "[NON-ACTION REUSE CONSTRAINTS]"))
    lines.append("Old quote is not ticket permission.")
    lines.append("Non-Action Direct Reuse cannot buy ticket.")
    for item in report["non_action_reuse_constraints"]["constraints"]:
        lines.append(f"- {item}")

    lines.extend(("", "[FUTURE SEMANTIC ACTOR TOPOLOGY]"))
    lines.append("Future LLM actors are planned, but none execute in this slice.")
    for actor in report["future_semantic_actor_topology"]:
        lines.append(
            "- {role} ({side}): executed_in_slice_b={executed_in_slice_b}".format(
                **actor,
            ),
        )

    lines.extend(("", "[FUTURE VERTICAL FRACTAL MAP]"))
    lines.append("Future vertical fractal cells are planned, but none execute in this slice.")
    for root_name, cells in report["future_vertical_fractal_map"].items():
        lines.append(f"{root_name}:")
        for cell in cells:
            lines.append(
                "  - {cell_id}: executed_in_slice_b={executed_in_slice_b}".format(
                    **cell,
                ),
            )

    lines.extend(("", "[COUNTER TABLE]"))
    for key in sorted(report["counter_table"]):
        lines.append(f"{key}: {report['counter_table'][key]}")

    lines.extend(
        (
            "",
            "[NON-CLAIMS]",
            "No real airline API, bank API, payment, ticket, booking, provider, network, or Gemini call occurs.",
        ),
    )
    lines.extend(f"- {claim}" for claim in report["non_claims"])
    lines.extend(
        (
            "",
            "[NEXT GATE]",
            str(report["next_gate"]),
            "",
            "[FINAL STATUS]",
            str(report["final_status"]),
        ),
    )
    return "\n".join(lines)


def run_tri_party_airline_ticket_purchase_mock_e2e_v01() -> str:
    return render_tri_party_airline_ticket_purchase_mock_e2e_v01(
        collect_tri_party_airline_ticket_purchase_mock_e2e_v01(),
    )


def main() -> int:
    print(run_tri_party_airline_ticket_purchase_mock_e2e_v01())
    return 0


def _transaction_identity() -> dict[str, Any]:
    return {
        "transaction_id": TRANSACTION_ID,
        "client_root_id": CLIENT_ROOT_ID,
        "airline_root_id": AIRLINE_ROOT_ID,
        "bank_root_id": BANK_ROOT_ID,
        "mock_only": True,
        "real_world_effects_allowed": False,
    }


def _participants() -> dict[str, dict[str, Any]]:
    return {
        "ClientRoot": {
            "root_id": CLIENT_ROOT_ID,
            "role": "client_travel_purchase_root",
            "knows": (
                "travel intent",
                "passenger sealed refs",
                "payment profile sealed ref",
                "selected offer ref",
                "user approval evidence",
            ),
            "does_not": (
                "expose raw passport",
                "expose raw card",
                "expose raw IBAN",
                "issue ticket",
                "authorize bank payment",
            ),
            "produces": "client purchase approval evidence only",
        },
        "AirlineRoot": {
            "root_id": AIRLINE_ROOT_ID,
            "role": "airline_offer_order_ticket_root",
            "knows": (
                "mock inventory",
                "mock fares",
                "mock seats",
                "baggage rule",
                "offer TTL",
                "order creation rule",
                "ticket issue rule",
            ),
            "creates": (
                "OfferResponse fixture",
                "OfferHoldReceipt fixture",
                "future OrderCreatedReceipt fixture",
                "future MockTicketReceipt / mock PNR fixture",
            ),
            "validates": "payment evidence later",
            "does_not": (
                "charge card",
                "authorize client payment",
                "request raw passport",
                "call real airline API",
            ),
        },
        "BankRoot": {
            "root_id": BANK_ROOT_ID,
            "role": "bank_payment_authorization_root",
            "knows": (
                "payment token ref",
                "debtor slot",
                "merchant/airline ref",
                "amount/currency",
                "idempotency",
                "consent/payment order/status",
            ),
            "creates": (
                "future PaymentIntent fixture",
                "future PaymentConsent fixture",
                "future PaymentAuthorizationReceipt fixture",
                "future PaymentStatusReceipt fixture",
            ),
            "does_not": (
                "create ticket",
                "call real bank API",
                "execute real payment",
            ),
        },
    }


def _travel_intent() -> dict[str, Any]:
    return {
        "origin": "PAR",
        "destination": "LIM",
        "depart_date": "2026-08-12",
        "return_date": "2026-08-21",
        "passengers_count": 1,
        "cabin": "economy",
        "baggage_needed": True,
        "max_price_amount": 840,
        "currency": "EUR",
        "user_goal": (
            "Find and hold a safe mock airline offer, authorize mock payment, "
            "and receive mock ticket evidence."
        ),
    }


def _sealed_refs() -> dict[str, dict[str, Any]]:
    return {
        "PassengerSealedRefsV01": {
            "passenger_ref": "sealed_passenger_ref:client_001:pax_001",
            "passport_ref": "sealed_passport_ref:client_001:pax_001",
            "loyalty_ref": "sealed_loyalty_ref:optional:none",
            "raw_passport_exposed": False,
            "raw_birthdate_exposed": False,
            "raw_document_number_exposed": False,
        },
        "PaymentProfileSealedRefV01": {
            "payment_profile_ref": "sealed_payment_profile_ref:client_001:pay_001",
            "payment_token_ref": "sealed_payment_token_ref:client_001:token_001",
            "debtor_slot_ref": "sealed_debtor_slot_ref:client_001:bank_a",
            "raw_card_exposed": False,
            "raw_iban_exposed": False,
            "raw_payment_token_exposed": False,
        },
    }


def _mock_protocol_fixtures(
    travel_intent: Mapping[str, Any],
    sealed_refs: Mapping[str, Mapping[str, Any]],
) -> dict[str, dict[str, Any]]:
    passenger = sealed_refs["PassengerSealedRefsV01"]
    payment = sealed_refs["PaymentProfileSealedRefV01"]
    offer_id = "offer:mock_airline_al:PAR-LIM:001"
    amount = 782
    currency = "EUR"
    return {
        "AirlineOfferRequestV01": {
            "transaction_id": TRANSACTION_ID,
            "origin": travel_intent["origin"],
            "destination": travel_intent["destination"],
            "depart_date": travel_intent["depart_date"],
            "return_date": travel_intent["return_date"],
            "passengers_count": travel_intent["passengers_count"],
            "cabin": travel_intent["cabin"],
            "baggage_needed": travel_intent["baggage_needed"],
            "passenger_ref": passenger["passenger_ref"],
            "raw_passport_exposed": False,
        },
        "AirlineOfferCandidateV01": {
            "transaction_id": TRANSACTION_ID,
            "offer_id": offer_id,
            "route": "PAR -> LIM",
            "fare_basis": "ECON_SAFE_1",
            "price_amount": amount,
            "currency": currency,
            "baggage_included": True,
            "refundable": False,
            "changeable": True,
            "inventory_class": "Y",
            "offer_ttl_seconds": 900,
            "mock_only": True,
        },
        "AirlineOfferResponseV01": {
            "response_id": f"offer_response:{TRANSACTION_ID}",
            "transaction_id": TRANSACTION_ID,
            "offer_candidates_count": 1,
            "selected_candidate_ref": offer_id,
        },
        "AirlineOfferHoldCommitPacketV01": {
            "packet_id": "airline_offer_hold_commit_packet:mock_airline_al:001",
            "transaction_id": TRANSACTION_ID,
            "created_by": "airline_root",
            "root_created": True,
            "allowed_root_id": AIRLINE_ROOT_ID,
            "allowed_action": "mock_offer_hold",
            "allowed_offer_id": offer_id,
            "allowed_passenger_ref": passenger["passenger_ref"],
            "allowed_amount": amount,
            "currency": currency,
            "ttl_seconds": 900,
            "idempotency_key": "idem:airline_offer_hold:001",
            "evidence_only_downstream": True,
            "payment_permission_created": False,
            "ticket_permission_created": False,
            "real_airline_api_allowed": False,
            "real_booking_allowed": False,
        },
        "AirlineOfferHoldReceiptV01": {
            "receipt_id": "offer_hold_receipt:mock_airline_al:001",
            "transaction_id": TRANSACTION_ID,
            "offer_id": offer_id,
            "hold_status": "held_mock",
            "expires_in_seconds": 900,
            "evidence_only": True,
            "payment_permission_created": False,
            "ticket_permission_created": False,
        },
        "ClientPurchaseApprovalEvidenceV01": {
            "approval_id": "client_purchase_approval:client_001:001",
            "transaction_id": TRANSACTION_ID,
            "selected_offer_id": offer_id,
            "max_price_amount": travel_intent["max_price_amount"],
            "currency": currency,
            "created_by": "client_root",
            "root_created": True,
            "evidence_only": True,
            "scoped_evidence_only": True,
            "bank_authority_created": False,
            "airline_authority_created": False,
            "payment_permission_created": False,
            "ticket_permission_created": False,
            "action_commit_packet_created": False,
            "receipt_created": False,
        },
        "BankPaymentIntentV01": {
            "intent_id": "bank_payment_intent:mock_bank_a:001",
            "transaction_id": TRANSACTION_ID,
            "merchant_ref": "merchant_ref:mock_airline_al",
            "amount": amount,
            "currency": currency,
            "payment_token_ref": payment["payment_token_ref"],
            "raw_card_exposed": False,
            "real_payment_executed": False,
        },
        "BankPaymentConsentV01": {
            "consent_id": "bank_payment_consent:mock_bank_a:001",
            "transaction_id": TRANSACTION_ID,
            "consent_status": "consented_mock",
            "evidence_only": True,
            "ticket_permission_created": False,
        },
        "BankPaymentAuthorizationCommitPacketV01": {
            "packet_id": "bank_payment_authorization_commit_packet:mock_bank_a:001",
            "transaction_id": TRANSACTION_ID,
            "created_by": "bank_root",
            "root_created": True,
            "allowed_root_id": BANK_ROOT_ID,
            "allowed_action": "mock_payment_authorization",
            "allowed_merchant_ref": "merchant_ref:mock_airline_al",
            "allowed_payment_token_ref": payment["payment_token_ref"],
            "allowed_debtor_slot_ref": payment["debtor_slot_ref"],
            "allowed_amount": amount,
            "currency": currency,
            "idempotency_key": "idem:bank_payment_authorization:001",
            "ttl_seconds": 900,
            "evidence_only_downstream": True,
            "ticket_permission_created": False,
            "real_payment_allowed": False,
            "real_bank_api_allowed": False,
            "real_settlement_allowed": False,
        },
        "BankPaymentAuthorizationReceiptV01": {
            "receipt_id": "payment_authorization_receipt:mock_bank_a:001",
            "transaction_id": TRANSACTION_ID,
            "authorized_amount": amount,
            "currency": currency,
            "authorization_status": "authorized_mock",
            "evidence_only": True,
            "ticket_created": False,
            "real_payment_executed": False,
        },
        "BankPaymentStatusReceiptV01": {
            "receipt_id": "payment_status_receipt:mock_bank_a:001",
            "transaction_id": TRANSACTION_ID,
            "payment_status": "authorized_not_settled_mock",
            "evidence_only": True,
            "settlement_executed": False,
            "real_payment_executed": False,
        },
        "AirlineTicketIssueCommitPacketV01": {
            "packet_id": "airline_ticket_issue_commit_packet:mock_airline_al:001",
            "transaction_id": TRANSACTION_ID,
            "created_by": "airline_root",
            "root_created": True,
            "allowed_root_id": AIRLINE_ROOT_ID,
            "allowed_action": "mock_airline_ticket_issue",
            "allowed_offer_id": offer_id,
            "allowed_order_id": "order:mock_airline_al:001",
            "allowed_passenger_ref": passenger["passenger_ref"],
            "required_offer_hold_receipt_id": "offer_hold_receipt:mock_airline_al:001",
            "required_payment_authorization_receipt_id": (
                "payment_authorization_receipt:mock_bank_a:001"
            ),
            "required_client_purchase_approval_id": (
                "client_purchase_approval:client_001:001"
            ),
            "allowed_amount": amount,
            "currency": currency,
            "ttl_seconds": 900,
            "idempotency_key": "idem:airline_ticket_issue:001",
            "mock_only": True,
            "evidence_only_downstream": True,
            "real_ticket_allowed": False,
            "real_booking_allowed": False,
            "real_airline_api_allowed": False,
            "real_payment_allowed": False,
        },
        "AirlineOrderCreatedReceiptV01": {
            "receipt_id": "order_created_receipt:mock_airline_al:001",
            "transaction_id": TRANSACTION_ID,
            "order_id": "order:mock_airline_al:001",
            "created_by": "airline_root",
            "evidence_only": True,
            "payment_created": False,
            "real_ticket_issued": False,
            "real_booking_created": False,
        },
        "MockTicketReceiptV01": {
            "receipt_id": "mock_ticket_receipt:mock_airline_al:001",
            "transaction_id": TRANSACTION_ID,
            "mock_ticket_id": "mock_ticket:001",
            "mock_pnr": "PNR-EEH01",
            "created_by": "airline_root",
            "evidence_only": True,
            "real_ticket": False,
            "real_travel_booking_created": False,
            "payment_created": False,
            "future_payment_permission_created": False,
        },
        "MockPNRV01": {
            "pnr": "PNR-EEH01",
            "transaction_id": TRANSACTION_ID,
            "created_by": "airline_root",
            "mock_only": True,
            "real_booking": False,
        },
        "ClientFinalTravelSummaryV01": {
            "summary_id": "client_final_travel_summary:client_001:001",
            "transaction_id": TRANSACTION_ID,
            "client_root_id": CLIENT_ROOT_ID,
            "selected_offer_id": offer_id,
            "offer_hold_receipt_id": "offer_hold_receipt:mock_airline_al:001",
            "payment_authorization_receipt_id": (
                "payment_authorization_receipt:mock_bank_a:001"
            ),
            "payment_status_receipt_id": "payment_status_receipt:mock_bank_a:001",
            "mock_ticket_receipt_id": "mock_ticket_receipt:mock_airline_al:001",
            "current_client_status": "mock_ticket_evidence_received_no_real_travel_booking",
            "evidence_only": True,
            "ticket_issued": False,
            "mock_ticket_evidence_received": True,
            "real_ticket_issued": False,
            "real_payment_executed": False,
            "real_booking_created": False,
        },
    }


def _airline_ticket_issue_mock_corridor(
    fixtures: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    ticket_packet = fixtures["AirlineTicketIssueCommitPacketV01"]
    order_receipt = fixtures["AirlineOrderCreatedReceiptV01"]
    ticket_receipt = fixtures["MockTicketReceiptV01"]
    mock_pnr = fixtures["MockPNRV01"]
    return {
        "corridor_id": "airline_ticket_issue_mock_corridor_v01",
        "transaction_id": TRANSACTION_ID,
        "airline_root_id": AIRLINE_ROOT_ID,
        "corridor_status": STATUS_PASS,
        "offer_hold_receipt_observed": True,
        "client_purchase_approval_evidence_observed": True,
        "payment_authorization_receipt_observed": True,
        "payment_status_receipt_observed": True,
        "offer_hold_ttl_freshness_validated": True,
        "selected_offer_match_validated": True,
        "amount_currency_match_validated": True,
        "merchant_airline_ref_match_validated": True,
        "passenger_sealed_ref_validated": True,
        "payment_evidence_validated_against_offer_hold": True,
        "raw_passport_absent": True,
        "raw_card_absent": True,
        "raw_payment_token_absent": True,
        "airline_ticket_issue_commit_packet_created": True,
        "airline_ticket_issue_commit_packet_created_by": "airline_root",
        "airline_ticket_issue_commit_packet_root_created": True,
        "airline_ticket_issue_commit_packet_validated": True,
        "airline_ticket_issue_commit_packet_ref": ticket_packet["packet_id"],
        "airline_order_created_receipt_created": True,
        "airline_order_created_receipt_validated": True,
        "airline_order_created_receipt_ref": order_receipt["receipt_id"],
        "mock_ticket_receipt_created": True,
        "mock_ticket_receipt_validated": True,
        "mock_ticket_receipt_ref": ticket_receipt["receipt_id"],
        "mock_pnr_created": True,
        "mock_pnr_validated": True,
        "mock_pnr": mock_pnr["pnr"],
        "mock_ticket_receipt_evidence_only": True,
        "mock_ticket_receipt_real_ticket": False,
        "mock_ticket_receipt_payment_created": False,
        "mock_pnr_real_booking": False,
        "payment_authorization_receipt_created_ticket": False,
        "client_purchase_approval_created_ticket": False,
        "offer_hold_receipt_created_ticket": False,
        "airline_root_authorized_payment": False,
        "airline_root_called_real_airline_api": False,
        "airline_root_called_real_gds_api": False,
        "real_ticket_issued": False,
        "real_booking_created": False,
        "real_payment_executed": False,
        "real_settlement_executed": False,
        "real_world_effects_count": 0,
    }


def _client_purchase_orchestration(
    travel_intent: Mapping[str, Any],
    sealed_refs: Mapping[str, Mapping[str, Any]],
    fixtures: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    passenger = sealed_refs["PassengerSealedRefsV01"]
    payment = sealed_refs["PaymentProfileSealedRefV01"]
    offer_response = fixtures["AirlineOfferResponseV01"]
    offer_candidate = fixtures["AirlineOfferCandidateV01"]
    approval = fixtures["ClientPurchaseApprovalEvidenceV01"]
    return {
        "orchestration_id": "client_purchase_orchestration_v01",
        "transaction_id": TRANSACTION_ID,
        "client_root_id": CLIENT_ROOT_ID,
        "orchestration_status": STATUS_PASS,
        "travel_intent_observed": True,
        "passenger_sealed_refs_observed": True,
        "passenger_ref": passenger["passenger_ref"],
        "payment_profile_sealed_ref_observed": True,
        "payment_profile_ref": payment["payment_profile_ref"],
        "offer_response_observed": True,
        "offer_hold_receipt_observed": True,
        "selected_offer_id": offer_response["selected_candidate_ref"],
        "selected_offer_amount": offer_candidate["price_amount"],
        "selected_offer_currency": offer_candidate["currency"],
        "selected_offer_within_user_max_price": (
            offer_candidate["price_amount"] <= travel_intent["max_price_amount"]
        ),
        "client_purchase_approval_evidence_created": True,
        "client_purchase_approval_evidence_created_by": "client_root",
        "client_purchase_approval_evidence_root_created": True,
        "client_purchase_approval_evidence_validated": True,
        "client_purchase_approval_evidence_evidence_only": True,
        "client_purchase_approval_evidence_ref": approval["approval_id"],
        "routed_to_bank_root": True,
        "routed_to_airline_root": True,
        "bank_payment_authorization_receipt_observed": True,
        "bank_payment_status_receipt_observed": True,
        "client_final_purchase_summary_created": True,
        "client_root_authorized_bank_payment": False,
        "client_root_issued_ticket": False,
        "client_root_created_airline_order": False,
        "client_root_created_bank_receipt": False,
        "client_root_created_action_commit_packet": False,
        "raw_passport_exposed": False,
        "raw_card_exposed": False,
        "raw_iban_exposed": False,
        "raw_payment_token_exposed": False,
        "real_payment_executed": False,
        "real_ticket_issued": False,
        "real_booking_created": False,
        "real_world_effects_count": 0,
    }


def _bank_payment_authorization_sandbox(
    fixtures: Mapping[str, Mapping[str, Any]],
    sealed_refs: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    payment = sealed_refs["PaymentProfileSealedRefV01"]
    payment_packet = fixtures["BankPaymentAuthorizationCommitPacketV01"]
    payment_auth_receipt = fixtures["BankPaymentAuthorizationReceiptV01"]
    payment_status_receipt = fixtures["BankPaymentStatusReceiptV01"]
    return {
        "sandbox_id": "bank_payment_authorization_sandbox_v01",
        "transaction_id": TRANSACTION_ID,
        "bank_root_id": BANK_ROOT_ID,
        "sandbox_status": STATUS_PASS,
        "offer_hold_receipt_observed": True,
        "client_purchase_approval_evidence_observed": True,
        "payment_profile_sealed_ref_observed": True,
        "amount_currency_validated": True,
        "merchant_airline_ref_validated": True,
        "payment_token_ref_validated": True,
        "payment_token_ref": payment["payment_token_ref"],
        "debtor_slot_ref_validated": True,
        "debtor_slot_ref": payment["debtor_slot_ref"],
        "idempotency_checked": True,
        "expiry_ttl_checked": True,
        "bank_payment_intent_created": True,
        "bank_payment_consent_created": True,
        "bank_payment_authorization_commit_packet_created": True,
        "bank_payment_authorization_commit_packet_created_by": "bank_root",
        "bank_payment_authorization_commit_packet_root_created": True,
        "bank_payment_authorization_commit_packet_validated": True,
        "bank_payment_authorization_commit_packet_ref": payment_packet["packet_id"],
        "payment_authorization_receipt_created": True,
        "payment_authorization_receipt_validated": True,
        "payment_authorization_receipt_ref": payment_auth_receipt["receipt_id"],
        "payment_status_receipt_created": True,
        "payment_status_receipt_validated": True,
        "payment_status_receipt_ref": payment_status_receipt["receipt_id"],
        "payment_authorization_receipt_evidence_only": True,
        "payment_authorization_receipt_ticket_permission_created": False,
        "payment_authorization_receipt_real_payment_executed": False,
        "payment_status_receipt_evidence_only": True,
        "payment_status_receipt_settlement_executed": False,
        "payment_status_receipt_ticket_permission_created": False,
        "bank_root_created_ticket": False,
        "real_bank_api_called": False,
        "real_payment_executed": False,
        "real_settlement_executed": False,
        "real_ticket_issued": False,
        "real_world_effects_count": 0,
    }


def _airline_offer_hold_sandbox(
    fixtures: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    offer_response = fixtures["AirlineOfferResponseV01"]
    offer_hold_packet = fixtures["AirlineOfferHoldCommitPacketV01"]
    offer_hold_receipt = fixtures["AirlineOfferHoldReceiptV01"]
    return {
        "sandbox_id": "airline_offer_hold_sandbox_v01",
        "transaction_id": TRANSACTION_ID,
        "airline_root_id": AIRLINE_ROOT_ID,
        "sandbox_status": STATUS_PASS,
        "offer_request_validated": True,
        "mock_inventory_checked": True,
        "mock_fare_checked": True,
        "baggage_rule_checked": True,
        "offer_ttl_checked": True,
        "selected_offer_id": offer_response["selected_candidate_ref"],
        "offer_response_created": True,
        "offer_hold_commit_packet_created": True,
        "offer_hold_commit_packet_created_by": "airline_root",
        "offer_hold_commit_packet_root_created": True,
        "offer_hold_commit_packet_validated": True,
        "offer_hold_commit_packet_ref": offer_hold_packet["packet_id"],
        "offer_hold_receipt_created": True,
        "offer_hold_receipt_validated": True,
        "offer_hold_receipt_ref": offer_hold_receipt["receipt_id"],
        "offer_hold_receipt_evidence_only": True,
        "offer_hold_receipt_payment_permission_created": False,
        "offer_hold_receipt_ticket_permission_created": False,
        "real_airline_api_called": False,
        "real_booking_created": False,
        "real_ticket_issued": False,
        "real_world_effects_count": 0,
    }


def _shared_transaction_ledger(
    fixtures: Mapping[str, Mapping[str, Any]],
) -> tuple[dict[str, Any], ...]:
    rows = (
        (CLIENT_ROOT_ID, "client_travel_intent_recorded", "TravelIntentV01", True),
        (AIRLINE_ROOT_ID, "airline_offer_request_fixture_created", "AirlineOfferRequestV01", True),
        (AIRLINE_ROOT_ID, "airline_offer_candidate_fixture_created", "AirlineOfferCandidateV01", True),
        (AIRLINE_ROOT_ID, "airline_offer_response_fixture_created", "AirlineOfferResponseV01", True),
        (AIRLINE_ROOT_ID, "airline_offer_hold_receipt_fixture_created", "AirlineOfferHoldReceiptV01", True),
        (CLIENT_ROOT_ID, "client_purchase_approval_evidence_fixture_created", "ClientPurchaseApprovalEvidenceV01", True),
        (BANK_ROOT_ID, "bank_payment_intent_fixture_created", "BankPaymentIntentV01", True),
        (BANK_ROOT_ID, "bank_payment_consent_fixture_created", "BankPaymentConsentV01", True),
        (BANK_ROOT_ID, "bank_payment_authorization_receipt_fixture_created", "BankPaymentAuthorizationReceiptV01", True),
        (BANK_ROOT_ID, "bank_payment_status_receipt_fixture_created", "BankPaymentStatusReceiptV01", True),
        (AIRLINE_ROOT_ID, "airline_order_created_receipt_fixture_created", "AirlineOrderCreatedReceiptV01", True),
        (AIRLINE_ROOT_ID, "mock_ticket_receipt_fixture_created", "MockTicketReceiptV01", True),
        (AIRLINE_ROOT_ID, "mock_pnr_fixture_created", "MockPNRV01", True),
        (CLIENT_ROOT_ID, "final_shared_summary_fixture_created", "ClientFinalTravelSummaryV01", True),
    )
    sandbox_stage_events = {
        "airline_offer_request_fixture_created",
        "airline_offer_candidate_fixture_created",
        "airline_offer_response_fixture_created",
        "airline_offer_hold_receipt_fixture_created",
    }
    bank_sandbox_stage_events = {
        "bank_payment_intent_fixture_created",
        "bank_payment_consent_fixture_created",
        "bank_payment_authorization_receipt_fixture_created",
        "bank_payment_status_receipt_fixture_created",
    }
    ticket_issue_corridor_events = {
        "airline_order_created_receipt_fixture_created",
        "mock_ticket_receipt_fixture_created",
        "mock_pnr_fixture_created",
        "final_shared_summary_fixture_created",
    }
    ledger_rows = []
    for index, (actor_root_id, event_type, artifact_name, evidence_only) in enumerate(
        rows,
        start=1,
    ):
        row = {
            "ledger_index": index,
            "transaction_id": TRANSACTION_ID,
            "actor_root_id": actor_root_id,
            "event_type": event_type,
            "artifact_ref": _artifact_ref(artifact_name, fixtures),
            "evidence_only": evidence_only,
            "authority_created": False,
            "real_world_effects_count": 0,
        }
        if event_type in sandbox_stage_events:
            row["sandbox_stage"] = "airline_offer_hold_sandbox"
            row["validated_by_airline_root"] = True
        if event_type in bank_sandbox_stage_events:
            row["sandbox_stage"] = "bank_payment_authorization_sandbox"
            row["validated_by_bank_root"] = True
        if event_type == "client_purchase_approval_evidence_fixture_created":
            row["orchestration_stage"] = "client_purchase_orchestration"
            row["validated_by_client_root"] = True
        if event_type in ticket_issue_corridor_events:
            row["corridor_stage"] = "airline_ticket_issue_mock_corridor"
            row["validated_by_airline_root"] = True
        ledger_rows.append(row)
    return tuple(ledger_rows)


def _integrated_transaction_trace(
    fixtures: Mapping[str, Mapping[str, Any]],
) -> tuple[dict[str, Any], ...]:
    offer_id = fixtures["AirlineOfferCandidateV01"]["offer_id"]
    phases = (
        (
            "client_travel_intent_recorded",
            CLIENT_ROOT_ID,
            CLIENT_ROOT_ID,
            ("TravelIntentV01",),
        ),
        (
            "client_to_airline_offer_request",
            CLIENT_ROOT_ID,
            AIRLINE_ROOT_ID,
            ("AirlineOfferRequestV01",),
        ),
        (
            "airline_offer_hold_sandbox_completed",
            AIRLINE_ROOT_ID,
            AIRLINE_ROOT_ID,
            (
                "AirlineOfferResponseV01",
                "AirlineOfferHoldCommitPacketV01",
                "AirlineOfferHoldReceiptV01",
            ),
        ),
        (
            "airline_to_client_offer_hold_receipt_returned",
            AIRLINE_ROOT_ID,
            CLIENT_ROOT_ID,
            ("AirlineOfferResponseV01", "AirlineOfferHoldReceiptV01"),
        ),
        (
            "client_offer_selected",
            CLIENT_ROOT_ID,
            CLIENT_ROOT_ID,
            (offer_id,),
        ),
        (
            "client_purchase_approval_evidence_created",
            CLIENT_ROOT_ID,
            CLIENT_ROOT_ID,
            ("ClientPurchaseApprovalEvidenceV01",),
        ),
        (
            "client_to_bank_payment_authorization_request",
            CLIENT_ROOT_ID,
            BANK_ROOT_ID,
            ("ClientPurchaseApprovalEvidenceV01", "PaymentProfileSealedRefV01"),
        ),
        (
            "bank_payment_authorization_sandbox_completed",
            BANK_ROOT_ID,
            BANK_ROOT_ID,
            (
                "BankPaymentIntentV01",
                "BankPaymentConsentV01",
                "BankPaymentAuthorizationCommitPacketV01",
                "BankPaymentAuthorizationReceiptV01",
                "BankPaymentStatusReceiptV01",
            ),
        ),
        (
            "bank_to_client_payment_authorization_receipt_returned",
            BANK_ROOT_ID,
            CLIENT_ROOT_ID,
            ("BankPaymentAuthorizationReceiptV01",),
        ),
        (
            "bank_to_client_payment_status_receipt_returned",
            BANK_ROOT_ID,
            CLIENT_ROOT_ID,
            ("BankPaymentStatusReceiptV01",),
        ),
        (
            "client_to_airline_payment_evidence_forwarded",
            CLIENT_ROOT_ID,
            AIRLINE_ROOT_ID,
            (
                "ClientPurchaseApprovalEvidenceV01",
                "BankPaymentAuthorizationReceiptV01",
                "BankPaymentStatusReceiptV01",
            ),
        ),
        (
            "airline_ticket_issue_mock_corridor_completed",
            AIRLINE_ROOT_ID,
            AIRLINE_ROOT_ID,
            (
                "AirlineTicketIssueCommitPacketV01",
                "AirlineOrderCreatedReceiptV01",
                "MockTicketReceiptV01",
                "MockPNRV01",
            ),
        ),
        (
            "airline_to_client_order_created_receipt_returned",
            AIRLINE_ROOT_ID,
            CLIENT_ROOT_ID,
            ("AirlineOrderCreatedReceiptV01",),
        ),
        (
            "airline_to_client_mock_ticket_receipt_returned",
            AIRLINE_ROOT_ID,
            CLIENT_ROOT_ID,
            ("MockTicketReceiptV01",),
        ),
        (
            "airline_to_client_mock_pnr_returned",
            AIRLINE_ROOT_ID,
            CLIENT_ROOT_ID,
            ("MockPNRV01",),
        ),
        (
            "client_final_mock_travel_summary_created",
            CLIENT_ROOT_ID,
            CLIENT_ROOT_ID,
            ("ClientFinalTravelSummaryV01",),
        ),
        (
            "final_shared_summary_fixture_created",
            CLIENT_ROOT_ID,
            CLIENT_ROOT_ID,
            ("ClientFinalTravelSummaryV01", "FinalTriPartyMockSummaryV01"),
        ),
    )
    return tuple(
        {
            "trace_index": index,
            "transaction_id": TRANSACTION_ID,
            "phase_id": phase_id,
            "source_root_id": source_root_id,
            "target_root_id": target_root_id,
            "artifact_refs": tuple(
                _artifact_ref(artifact_name, fixtures)
                for artifact_name in artifact_names
            ),
            "evidence_only": True,
            "authority_transferred": False,
            "raw_secrets_exposed": False,
            "real_ticket_claimed": False,
            "real_payment_claimed": False,
            "real_booking_claimed": False,
            "real_world_effects_count": 0,
        }
        for index, (phase_id, source_root_id, target_root_id, artifact_names)
        in enumerate(phases, start=1)
    )


def _cross_root_evidence_routing_matrix() -> tuple[dict[str, Any], ...]:
    rows = (
        {
            "route_id": "A",
            "source_root_id": CLIENT_ROOT_ID,
            "target_root_id": AIRLINE_ROOT_ID,
            "artifact": "AirlineOfferRequestV01",
            "purpose": "request mock offers",
            "evidence_only": True,
            "authority_transferred": False,
            "raw_passport_exposed": False,
            "raw_card_exposed": False,
        },
        {
            "route_id": "B",
            "source_root_id": AIRLINE_ROOT_ID,
            "target_root_id": CLIENT_ROOT_ID,
            "artifact": "AirlineOfferResponseV01 + OfferHoldReceipt",
            "purpose": "return mock offer and hold evidence",
            "evidence_only": True,
            "payment_permission_created": False,
            "ticket_permission_created": False,
            "authority_transferred": False,
        },
        {
            "route_id": "C",
            "source_root_id": CLIENT_ROOT_ID,
            "target_root_id": BANK_ROOT_ID,
            "artifact": "ClientPurchaseApprovalEvidence + PaymentProfileSealedRef",
            "purpose": "request mock payment authorization",
            "evidence_only": True,
            "bank_authority_created_by_client": False,
            "raw_card_exposed": False,
            "raw_iban_exposed": False,
            "authority_transferred": False,
        },
        {
            "route_id": "D",
            "source_root_id": BANK_ROOT_ID,
            "target_root_id": CLIENT_ROOT_ID,
            "artifact": "PaymentAuthorizationReceipt + PaymentStatusReceipt",
            "purpose": "return mock payment authorization evidence",
            "evidence_only": True,
            "ticket_permission_created": False,
            "real_payment_executed": False,
            "authority_transferred": False,
        },
        {
            "route_id": "E",
            "source_root_id": CLIENT_ROOT_ID,
            "target_root_id": AIRLINE_ROOT_ID,
            "artifact": (
                "ClientPurchaseApprovalEvidence + PaymentAuthorizationReceipt "
                "+ PaymentStatusReceipt"
            ),
            "purpose": (
                "ask AirlineRoot to validate payment evidence and issue mock "
                "ticket evidence"
            ),
            "evidence_only": True,
            "airline_authority_created_by_client": False,
            "ticket_permission_created_by_payment_receipt": False,
            "authority_transferred": False,
        },
        {
            "route_id": "F",
            "source_root_id": AIRLINE_ROOT_ID,
            "target_root_id": CLIENT_ROOT_ID,
            "artifact": "OrderCreatedReceipt + MockTicketReceipt + MockPNR",
            "purpose": "return mock order/ticket/PNR evidence",
            "evidence_only": True,
            "real_ticket_issued": False,
            "real_booking_created": False,
            "payment_created": False,
            "authority_transferred": False,
        },
    )
    return tuple({**row, "transaction_id": TRANSACTION_ID, "real_world_effects_count": 0} for row in rows)


def _final_tri_party_mock_summary() -> dict[str, Any]:
    return {
        "summary_id": f"final_tri_party_mock_summary:{TRANSACTION_ID}",
        "transaction_id": TRANSACTION_ID,
        "final_status": STATUS_PASS,
        "client_view_status": "mock_ticket_evidence_received_no_real_travel_booking",
        "airline_view_status": "mock_order_ticket_pnr_evidence_created",
        "bank_view_status": "mock_payment_authorized_not_settled",
        "selected_offer_id": "offer:mock_airline_al:PAR-LIM:001",
        "offer_hold_receipt_id": "offer_hold_receipt:mock_airline_al:001",
        "payment_authorization_receipt_id": "payment_authorization_receipt:mock_bank_a:001",
        "payment_status_receipt_id": "payment_status_receipt:mock_bank_a:001",
        "order_created_receipt_id": "order_created_receipt:mock_airline_al:001",
        "mock_ticket_receipt_id": "mock_ticket_receipt:mock_airline_al:001",
        "mock_pnr": "PNR-EEH01",
        "receipts_evidence_only": True,
        "authority_transferred_between_roots": False,
        "client_root_issued_ticket": False,
        "airline_root_authorized_payment": False,
        "bank_root_created_ticket": False,
        "real_airline_api_called": False,
        "real_bank_api_called": False,
        "real_gds_api_called": False,
        "real_payment_executed": False,
        "real_settlement_executed": False,
        "real_ticket_issued": False,
        "real_booking_created": False,
        "provider_called": False,
        "network_used": False,
        "gemini_called": False,
        "real_world_effects_count": 0,
    }


def _artifact_ref(artifact_name: str, fixtures: Mapping[str, Mapping[str, Any]]) -> str:
    fixture = fixtures.get(artifact_name)
    if fixture is None:
        return f"artifact_ref:{artifact_name}"
    return str(
        fixture.get("receipt_id")
        or fixture.get("summary_id")
        or fixture.get("packet_id")
        or fixture.get("response_id")
        or fixture.get("offer_id")
        or fixture.get("approval_id")
        or fixture.get("intent_id")
        or fixture.get("consent_id")
        or fixture.get("pnr")
        or f"artifact_ref:{artifact_name}"
    )


def _client_root_view(
    participants: Mapping[str, Mapping[str, Any]],
    fixtures: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    return {
        "root_id": participants["ClientRoot"]["root_id"],
        "role": participants["ClientRoot"]["role"],
        "bounded_view": (
            "travel intent",
            "sealed passenger refs",
            "sealed payment profile refs",
            "selected offer ref",
            "client purchase approval evidence",
            "mock ticket evidence after AirlineRoot fixture",
        ),
        "selected_offer_ref": fixtures["AirlineOfferResponseV01"]["selected_candidate_ref"],
        "approval_evidence_ref": fixtures["ClientPurchaseApprovalEvidenceV01"]["approval_id"],
        "does_not_issue_ticket": True,
        "does_not_authorize_bank_payment": True,
        "raw_secret_exposure_count": 0,
    }


def _airline_root_view(
    participants: Mapping[str, Mapping[str, Any]],
    fixtures: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    return {
        "root_id": participants["AirlineRoot"]["root_id"],
        "role": participants["AirlineRoot"]["role"],
        "bounded_view": (
            "mock inventory",
            "mock fares",
            "mock seat availability",
            "baggage rule",
            "offer hold receipt",
            "future mock order/ticket evidence",
        ),
        "offer_response_ref": fixtures["AirlineOfferResponseV01"]["response_id"],
        "offer_hold_receipt_ref": fixtures["AirlineOfferHoldReceiptV01"]["receipt_id"],
        "future_mock_ticket_receipt_ref": fixtures["MockTicketReceiptV01"]["receipt_id"],
        "does_not_charge_card": True,
        "does_not_authorize_client_payment": True,
        "real_airline_api_called": False,
    }


def _bank_root_view(
    participants: Mapping[str, Mapping[str, Any]],
    fixtures: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    return {
        "root_id": participants["BankRoot"]["root_id"],
        "role": participants["BankRoot"]["role"],
        "bounded_view": (
            "payment token ref",
            "debtor slot",
            "merchant ref",
            "amount/currency",
            "idempotency",
            "payment authorization receipt",
        ),
        "payment_intent_ref": fixtures["BankPaymentIntentV01"]["intent_id"],
        "payment_authorization_receipt_ref": fixtures[
            "BankPaymentAuthorizationReceiptV01"
        ]["receipt_id"],
        "does_not_create_ticket": True,
        "real_bank_api_called": False,
        "real_payment_executed": False,
    }


def _root_boundary_matrix() -> tuple[dict[str, Any], ...]:
    return tuple(
        {
            "boundary": boundary,
            "boundary_preserved": True,
            "violation_count": 0,
        }
        for boundary in (
            "ClientRoot cannot issue ticket.",
            "ClientRoot cannot authorize bank payment.",
            "AirlineRoot cannot authorize client payment.",
            "AirlineRoot cannot charge card.",
            "BankRoot cannot create airline ticket.",
            "BankRoot cannot create airline order.",
            "Payment receipt does not automatically create ticket.",
            "Ticket receipt does not automatically create payment.",
            "Receipt from one Root is evidence for another Root, not authority over it.",
            "Each Root consumes evidence, not foreign authority.",
            "No Root becomes God over the others.",
            "Root boundaries remain side-specific.",
        )
    )


def _receipt_boundary_matrix() -> tuple[dict[str, Any], ...]:
    return tuple(
        {
            "boundary": boundary,
            "boundary_preserved": True,
            "violation_count": 0,
        }
        for boundary in (
            "OfferHoldReceipt is evidence only.",
            "PaymentAuthorizationReceipt is evidence only.",
            "PaymentStatusReceipt is evidence only.",
            "OrderCreatedReceipt is evidence only.",
            "MockTicketReceipt is evidence only.",
            "MockTicketReceipt is not real ticket.",
            "PaymentAuthorizationReceipt is not ticket permission.",
            "OfferHoldReceipt is not payment permission.",
            "ClientPurchaseApprovalEvidence is evidence for BankRoot and AirlineRoot, not their authority.",
        )
    )


def _privacy_boundary_matrix() -> dict[str, Any]:
    return {
        "raw_passport_exposed_count": 0,
        "raw_card_exposed_count": 0,
        "raw_iban_exposed_count": 0,
        "raw_payment_token_exposed_count": 0,
        "raw_birthdate_exposed_count": 0,
        "raw_document_number_exposed_count": 0,
        "passenger_sealed_ref_only": True,
        "payment_profile_sealed_ref_only": True,
        "vault_refs_not_llm_context": True,
        "no_raw_private_profile_in_provider_context": True,
        "no_raw_secrets_in_artifacts": True,
    }


def _non_action_reuse_constraints() -> dict[str, Any]:
    return {
        "constraints": (
            "old route preference may inform context only.",
            "old quote is not ticket permission.",
            "old payment receipt is not current payment authorization.",
            "old ticket receipt is not future ticket permission.",
            "old traveler refs cannot expose raw passport.",
            "DRS hit is context only unless RootShortcutGate allows informational reuse.",
            "action-like Airline requests must route to Root/corridor, not direct reuse.",
        ),
        "non_action_reuse_cannot_buy_ticket": True,
    }


def _future_semantic_actor_topology() -> tuple[dict[str, Any], ...]:
    role_specs = (
        (
            "client",
            "client_purchase_orchestrator_llm",
            "interpret user travel intent, passenger constraints, selected offer approval, and user-facing risk explanation.",
        ),
        (
            "client",
            "client_profile_privacy_reviewer_llm",
            "explain which sealed refs are safe to share and which raw private fields remain sealed.",
        ),
        (
            "airline",
            "airline_offer_policy_reviewer_llm",
            "interpret fare, baggage, TTL, route, refund/change, and offer-hold constraints.",
        ),
        (
            "airline",
            "airline_ticketing_policy_reviewer_llm",
            "interpret when payment evidence is sufficient for mock ticket issue.",
        ),
        (
            "bank",
            "bank_payment_policy_reviewer_llm",
            "interpret consent, amount, merchant, idempotency, expiry, and risk policy.",
        ),
        (
            "bank",
            "bank_payment_status_explainer_llm",
            "explain payment authorization vs settlement vs evidence-only status.",
        ),
    )
    return tuple(
        {
            "side": side,
            "role": role,
            "semantic_work": semantic_work,
            "planned_for_later_live_lane": True,
            "executed_in_slice_b": False,
            "creates_authority": False,
            "creates_action_commit_packet": False,
            "creates_receipt": False,
            "creates_ticket": False,
            "executes_payment": False,
            "calls_real_api": False,
        }
        for side, role, semantic_work in role_specs
    )


def _future_vertical_fractal_map() -> dict[str, tuple[dict[str, Any], ...]]:
    cells_by_root = {
        "ClientRoot": (
            "client_intent_cell",
            "passenger_sealed_ref_cell",
            "payment_profile_sealed_ref_cell",
            "purchase_approval_cell",
        ),
        "AirlineRoot": (
            "airline_offer_root_cell",
            "fare_rules_child_cell",
            "baggage_policy_child_cell",
            "offer_ttl_child_cell",
            "ticket_issue_policy_child_cell",
        ),
        "BankRoot": (
            "bank_payment_root_cell",
            "consent_child_cell",
            "merchant_amount_match_child_cell",
            "idempotency_child_cell",
            "risk_policy_child_cell",
        ),
    }
    return {
        root_name: tuple(
            {
                "cell_id": cell_id,
                "planned_for_later": True,
                "executed_in_slice_b": False,
                "creates_authority": False,
                "real_world_effects_count": 0,
            }
            for cell_id in cell_ids
        )
        for root_name, cell_ids in cells_by_root.items()
    }


def _counter_table(
    ledger: tuple[dict[str, Any], ...],
    actors: tuple[dict[str, Any], ...],
    fractal_map: Mapping[str, tuple[dict[str, Any], ...]],
    airline_offer_hold_sandbox: Mapping[str, Any],
    bank_payment_authorization_sandbox: Mapping[str, Any],
    client_purchase_orchestration: Mapping[str, Any],
    airline_ticket_issue_mock_corridor: Mapping[str, Any],
    integrated_transaction_trace: tuple[dict[str, Any], ...],
    cross_root_evidence_routing_matrix: tuple[dict[str, Any], ...],
    final_tri_party_mock_summary: Mapping[str, Any],
) -> dict[str, int]:
    fractal_cells = tuple(
        cell for cells in fractal_map.values() for cell in cells
    )
    return {
        "tri_party_airline_transaction_count": 1,
        "client_root_count": 1,
        "airline_root_count": 1,
        "bank_root_count": 1,
        "shared_transaction_id_count": 1,
        "shared_ledger_entry_count": len(ledger),
        "offer_candidates_created_count": 1,
        "offer_hold_receipt_fixture_count": 1,
        "airline_offer_hold_sandbox_invoked_count": 1,
        "airline_offer_request_validated_count": int(
            airline_offer_hold_sandbox["offer_request_validated"],
        ),
        "mock_inventory_checked_count": int(
            airline_offer_hold_sandbox["mock_inventory_checked"],
        ),
        "mock_fare_checked_count": int(
            airline_offer_hold_sandbox["mock_fare_checked"],
        ),
        "baggage_rule_checked_count": int(
            airline_offer_hold_sandbox["baggage_rule_checked"],
        ),
        "offer_ttl_checked_count": int(
            airline_offer_hold_sandbox["offer_ttl_checked"],
        ),
        "airline_offer_response_created_count": int(
            airline_offer_hold_sandbox["offer_response_created"],
        ),
        "airline_offer_hold_commit_packet_created_count": int(
            airline_offer_hold_sandbox["offer_hold_commit_packet_created"],
        ),
        "airline_offer_hold_commit_packet_created_by_airline_root_count": int(
            airline_offer_hold_sandbox["offer_hold_commit_packet_created_by"]
            == "airline_root",
        ),
        "airline_offer_hold_commit_packet_created_by_client_root_count": int(
            airline_offer_hold_sandbox["offer_hold_commit_packet_created_by"]
            == "client_root",
        ),
        "airline_offer_hold_commit_packet_created_by_bank_root_count": int(
            airline_offer_hold_sandbox["offer_hold_commit_packet_created_by"]
            == "bank_root",
        ),
        "airline_offer_hold_commit_packet_validated_count": int(
            airline_offer_hold_sandbox["offer_hold_commit_packet_validated"],
        ),
        "airline_offer_hold_receipt_created_count": int(
            airline_offer_hold_sandbox["offer_hold_receipt_created"],
        ),
        "airline_offer_hold_receipt_validated_count": int(
            airline_offer_hold_sandbox["offer_hold_receipt_validated"],
        ),
        "offer_hold_receipt_payment_permission_created_count": int(
            airline_offer_hold_sandbox[
                "offer_hold_receipt_payment_permission_created"
            ],
        ),
        "offer_hold_receipt_ticket_permission_created_count": int(
            airline_offer_hold_sandbox[
                "offer_hold_receipt_ticket_permission_created"
            ],
        ),
        "client_purchase_approval_evidence_fixture_count": 1,
        "client_purchase_orchestration_invoked_count": 1,
        "client_travel_intent_observed_count": int(
            client_purchase_orchestration["travel_intent_observed"],
        ),
        "client_passenger_sealed_refs_observed_count": int(
            client_purchase_orchestration["passenger_sealed_refs_observed"],
        ),
        "client_payment_profile_sealed_ref_observed_count": int(
            client_purchase_orchestration[
                "payment_profile_sealed_ref_observed"
            ],
        ),
        "client_offer_response_observed_count": int(
            client_purchase_orchestration["offer_response_observed"],
        ),
        "client_offer_hold_receipt_observed_count": int(
            client_purchase_orchestration["offer_hold_receipt_observed"],
        ),
        "client_offer_selected_count": int(
            bool(client_purchase_orchestration["selected_offer_id"]),
        ),
        "client_selected_offer_within_user_max_price_count": int(
            client_purchase_orchestration["selected_offer_within_user_max_price"],
        ),
        "client_purchase_approval_evidence_created_count": int(
            client_purchase_orchestration[
                "client_purchase_approval_evidence_created"
            ],
        ),
        "client_purchase_approval_evidence_created_by_client_root_count": int(
            client_purchase_orchestration[
                "client_purchase_approval_evidence_created_by"
            ]
            == "client_root",
        ),
        "client_purchase_approval_evidence_created_by_airline_root_count": int(
            client_purchase_orchestration[
                "client_purchase_approval_evidence_created_by"
            ]
            == "airline_root",
        ),
        "client_purchase_approval_evidence_created_by_bank_root_count": int(
            client_purchase_orchestration[
                "client_purchase_approval_evidence_created_by"
            ]
            == "bank_root",
        ),
        "client_purchase_approval_evidence_validated_count": int(
            client_purchase_orchestration[
                "client_purchase_approval_evidence_validated"
            ],
        ),
        "client_purchase_approval_evidence_routed_to_bank_root_count": int(
            client_purchase_orchestration["routed_to_bank_root"],
        ),
        "client_purchase_approval_evidence_routed_to_airline_root_count": int(
            client_purchase_orchestration["routed_to_airline_root"],
        ),
        "client_bank_payment_authorization_receipt_observed_count": int(
            client_purchase_orchestration[
                "bank_payment_authorization_receipt_observed"
            ],
        ),
        "client_bank_payment_status_receipt_observed_count": int(
            client_purchase_orchestration["bank_payment_status_receipt_observed"],
        ),
        "client_final_purchase_summary_created_count": int(
            client_purchase_orchestration["client_final_purchase_summary_created"],
        ),
        "client_root_authorized_bank_payment_count": int(
            client_purchase_orchestration["client_root_authorized_bank_payment"],
        ),
        "client_root_created_airline_order_count": int(
            client_purchase_orchestration["client_root_created_airline_order"],
        ),
        "client_root_created_bank_receipt_count": int(
            client_purchase_orchestration["client_root_created_bank_receipt"],
        ),
        "client_root_created_action_commit_packet_count": int(
            client_purchase_orchestration[
                "client_root_created_action_commit_packet"
            ],
        ),
        "client_raw_passport_exposed_count": int(
            client_purchase_orchestration["raw_passport_exposed"],
        ),
        "client_raw_card_exposed_count": int(
            client_purchase_orchestration["raw_card_exposed"],
        ),
        "client_raw_iban_exposed_count": int(
            client_purchase_orchestration["raw_iban_exposed"],
        ),
        "client_raw_payment_token_exposed_count": int(
            client_purchase_orchestration["raw_payment_token_exposed"],
        ),
        "bank_payment_intent_fixture_count": 1,
        "bank_payment_consent_fixture_count": 1,
        "bank_payment_authorization_receipt_fixture_count": 1,
        "bank_payment_status_receipt_fixture_count": 1,
        "bank_payment_authorization_sandbox_invoked_count": 1,
        "bank_offer_hold_receipt_observed_count": int(
            bank_payment_authorization_sandbox["offer_hold_receipt_observed"],
        ),
        "bank_client_purchase_approval_evidence_observed_count": int(
            bank_payment_authorization_sandbox[
                "client_purchase_approval_evidence_observed"
            ],
        ),
        "bank_payment_profile_sealed_ref_observed_count": int(
            bank_payment_authorization_sandbox[
                "payment_profile_sealed_ref_observed"
            ],
        ),
        "bank_amount_currency_validated_count": int(
            bank_payment_authorization_sandbox["amount_currency_validated"],
        ),
        "bank_merchant_airline_ref_validated_count": int(
            bank_payment_authorization_sandbox["merchant_airline_ref_validated"],
        ),
        "bank_payment_token_ref_validated_count": int(
            bank_payment_authorization_sandbox["payment_token_ref_validated"],
        ),
        "bank_debtor_slot_ref_validated_count": int(
            bank_payment_authorization_sandbox["debtor_slot_ref_validated"],
        ),
        "bank_idempotency_checked_count": int(
            bank_payment_authorization_sandbox["idempotency_checked"],
        ),
        "bank_expiry_ttl_checked_count": int(
            bank_payment_authorization_sandbox["expiry_ttl_checked"],
        ),
        "bank_payment_intent_created_count": int(
            bank_payment_authorization_sandbox["bank_payment_intent_created"],
        ),
        "bank_payment_consent_created_count": int(
            bank_payment_authorization_sandbox["bank_payment_consent_created"],
        ),
        "bank_payment_authorization_commit_packet_created_count": int(
            bank_payment_authorization_sandbox[
                "bank_payment_authorization_commit_packet_created"
            ],
        ),
        "bank_payment_authorization_commit_packet_created_by_bank_root_count": int(
            bank_payment_authorization_sandbox[
                "bank_payment_authorization_commit_packet_created_by"
            ]
            == "bank_root",
        ),
        "bank_payment_authorization_commit_packet_created_by_client_root_count": int(
            bank_payment_authorization_sandbox[
                "bank_payment_authorization_commit_packet_created_by"
            ]
            == "client_root",
        ),
        "bank_payment_authorization_commit_packet_created_by_airline_root_count": int(
            bank_payment_authorization_sandbox[
                "bank_payment_authorization_commit_packet_created_by"
            ]
            == "airline_root",
        ),
        "bank_payment_authorization_commit_packet_validated_count": int(
            bank_payment_authorization_sandbox[
                "bank_payment_authorization_commit_packet_validated"
            ],
        ),
        "payment_authorization_receipt_created_count": int(
            bank_payment_authorization_sandbox[
                "payment_authorization_receipt_created"
            ],
        ),
        "payment_authorization_receipt_validated_count": int(
            bank_payment_authorization_sandbox[
                "payment_authorization_receipt_validated"
            ],
        ),
        "payment_status_receipt_created_count": int(
            bank_payment_authorization_sandbox["payment_status_receipt_created"],
        ),
        "payment_status_receipt_validated_count": int(
            bank_payment_authorization_sandbox["payment_status_receipt_validated"],
        ),
        "payment_authorization_receipt_ticket_permission_created_count": int(
            bank_payment_authorization_sandbox[
                "payment_authorization_receipt_ticket_permission_created"
            ],
        ),
        "payment_authorization_receipt_real_payment_executed_count": int(
            bank_payment_authorization_sandbox[
                "payment_authorization_receipt_real_payment_executed"
            ],
        ),
        "payment_status_receipt_ticket_permission_created_count": int(
            bank_payment_authorization_sandbox[
                "payment_status_receipt_ticket_permission_created"
            ],
        ),
        "payment_status_receipt_settlement_executed_count": int(
            bank_payment_authorization_sandbox[
                "payment_status_receipt_settlement_executed"
            ],
        ),
        "airline_order_created_receipt_fixture_count": 1,
        "mock_ticket_receipt_fixture_count": 1,
        "mock_pnr_fixture_count": 1,
        "airline_ticket_issue_mock_corridor_invoked_count": 1,
        "airline_ticket_issue_offer_hold_receipt_observed_count": int(
            airline_ticket_issue_mock_corridor["offer_hold_receipt_observed"],
        ),
        "airline_ticket_issue_client_purchase_approval_observed_count": int(
            airline_ticket_issue_mock_corridor[
                "client_purchase_approval_evidence_observed"
            ],
        ),
        "airline_ticket_issue_payment_authorization_receipt_observed_count": int(
            airline_ticket_issue_mock_corridor[
                "payment_authorization_receipt_observed"
            ],
        ),
        "airline_ticket_issue_payment_status_receipt_observed_count": int(
            airline_ticket_issue_mock_corridor["payment_status_receipt_observed"],
        ),
        "airline_ticket_issue_offer_hold_ttl_freshness_validated_count": int(
            airline_ticket_issue_mock_corridor[
                "offer_hold_ttl_freshness_validated"
            ],
        ),
        "airline_ticket_issue_selected_offer_match_validated_count": int(
            airline_ticket_issue_mock_corridor["selected_offer_match_validated"],
        ),
        "airline_ticket_issue_amount_currency_match_validated_count": int(
            airline_ticket_issue_mock_corridor["amount_currency_match_validated"],
        ),
        "airline_ticket_issue_merchant_airline_ref_match_validated_count": int(
            airline_ticket_issue_mock_corridor[
                "merchant_airline_ref_match_validated"
            ],
        ),
        "airline_ticket_issue_passenger_sealed_ref_validated_count": int(
            airline_ticket_issue_mock_corridor["passenger_sealed_ref_validated"],
        ),
        "airline_ticket_issue_payment_evidence_validated_against_offer_hold_count": int(
            airline_ticket_issue_mock_corridor[
                "payment_evidence_validated_against_offer_hold"
            ],
        ),
        "airline_ticket_issue_commit_packet_created_count": int(
            airline_ticket_issue_mock_corridor[
                "airline_ticket_issue_commit_packet_created"
            ],
        ),
        "airline_ticket_issue_commit_packet_created_by_airline_root_count": int(
            airline_ticket_issue_mock_corridor[
                "airline_ticket_issue_commit_packet_created_by"
            ]
            == "airline_root",
        ),
        "airline_ticket_issue_commit_packet_created_by_client_root_count": int(
            airline_ticket_issue_mock_corridor[
                "airline_ticket_issue_commit_packet_created_by"
            ]
            == "client_root",
        ),
        "airline_ticket_issue_commit_packet_created_by_bank_root_count": int(
            airline_ticket_issue_mock_corridor[
                "airline_ticket_issue_commit_packet_created_by"
            ]
            == "bank_root",
        ),
        "airline_ticket_issue_commit_packet_validated_count": int(
            airline_ticket_issue_mock_corridor[
                "airline_ticket_issue_commit_packet_validated"
            ],
        ),
        "airline_order_created_receipt_created_count": int(
            airline_ticket_issue_mock_corridor[
                "airline_order_created_receipt_created"
            ],
        ),
        "airline_order_created_receipt_validated_count": int(
            airline_ticket_issue_mock_corridor[
                "airline_order_created_receipt_validated"
            ],
        ),
        "mock_ticket_receipt_created_count": int(
            airline_ticket_issue_mock_corridor["mock_ticket_receipt_created"],
        ),
        "mock_ticket_receipt_validated_count": int(
            airline_ticket_issue_mock_corridor["mock_ticket_receipt_validated"],
        ),
        "mock_pnr_created_count": int(
            airline_ticket_issue_mock_corridor["mock_pnr_created"],
        ),
        "mock_pnr_validated_count": int(
            airline_ticket_issue_mock_corridor["mock_pnr_validated"],
        ),
        "mock_ticket_receipt_evidence_only_count": int(
            airline_ticket_issue_mock_corridor[
                "mock_ticket_receipt_evidence_only"
            ],
        ),
        "mock_ticket_receipt_real_ticket_count": int(
            airline_ticket_issue_mock_corridor["mock_ticket_receipt_real_ticket"],
        ),
        "mock_pnr_real_booking_count": int(
            airline_ticket_issue_mock_corridor["mock_pnr_real_booking"],
        ),
        "payment_authorization_receipt_created_ticket_count": int(
            airline_ticket_issue_mock_corridor[
                "payment_authorization_receipt_created_ticket"
            ],
        ),
        "client_purchase_approval_created_ticket_count": int(
            airline_ticket_issue_mock_corridor[
                "client_purchase_approval_created_ticket"
            ],
        ),
        "offer_hold_receipt_created_ticket_count": int(
            airline_ticket_issue_mock_corridor["offer_hold_receipt_created_ticket"],
        ),
        "airline_root_called_real_airline_api_count": int(
            airline_ticket_issue_mock_corridor[
                "airline_root_called_real_airline_api"
            ],
        ),
        "airline_root_called_real_gds_api_count": int(
            airline_ticket_issue_mock_corridor["airline_root_called_real_gds_api"],
        ),
        "integrated_tri_party_transaction_trace_created_count": int(
            bool(integrated_transaction_trace),
        ),
        "integrated_trace_phase_count": len(integrated_transaction_trace),
        "cross_root_evidence_routing_rows_count": len(
            cross_root_evidence_routing_matrix,
        ),
        "cross_root_authority_transfer_count": sum(
            int(row["authority_transferred"])
            for row in cross_root_evidence_routing_matrix
        ),
        "cross_root_real_world_effects_count": sum(
            int(row["real_world_effects_count"])
            for row in cross_root_evidence_routing_matrix
        ),
        "final_tri_party_mock_summary_created_count": int(
            final_tri_party_mock_summary.get("final_status") == STATUS_PASS,
        ),
        "final_client_view_mock_ticket_evidence_received_count": int(
            final_tri_party_mock_summary.get("client_view_status")
            == "mock_ticket_evidence_received_no_real_travel_booking",
        ),
        "final_airline_view_mock_order_ticket_pnr_evidence_created_count": int(
            final_tri_party_mock_summary.get("airline_view_status")
            == "mock_order_ticket_pnr_evidence_created",
        ),
        "final_bank_view_mock_payment_authorized_not_settled_count": int(
            final_tri_party_mock_summary.get("bank_view_status")
            == "mock_payment_authorized_not_settled",
        ),
        "final_real_ticket_issued_count": int(
            final_tri_party_mock_summary["real_ticket_issued"],
        ),
        "final_real_payment_executed_count": int(
            final_tri_party_mock_summary["real_payment_executed"],
        ),
        "final_real_booking_created_count": int(
            final_tri_party_mock_summary["real_booking_created"],
        ),
        "final_authority_transferred_between_roots_count": int(
            final_tri_party_mock_summary["authority_transferred_between_roots"],
        ),
        "future_semantic_actor_roles_planned_count": len(actors),
        "future_semantic_actor_roles_executed_count": sum(
            int(actor["executed_in_slice_b"]) for actor in actors
        ),
        "future_vertical_fractal_cells_planned_count": len(fractal_cells),
        "future_vertical_fractal_cells_executed_count": sum(
            int(cell["executed_in_slice_b"]) for cell in fractal_cells
        ),
        "client_root_issued_ticket_count": 0,
        "airline_root_authorized_payment_count": 0,
        "bank_root_created_ticket_count": 0,
        "payment_receipt_created_ticket_count": 0,
        "ticket_receipt_created_payment_count": 0,
        "raw_passport_exposed_count": 0,
        "raw_card_exposed_count": 0,
        "raw_iban_exposed_count": 0,
        "raw_payment_token_exposed_count": 0,
        "real_airline_api_called_count": 0,
        "real_bank_api_called_count": 0,
        "real_payment_executed_count": 0,
        "real_settlement_executed_count": 0,
        "real_booking_created_count": 0,
        "real_ticket_issued_count": 0,
        "real_travel_booking_created_count": 0,
        "provider_called_count": 0,
        "network_used_count": 0,
        "gemini_called_count": 0,
        "real_world_effects_count": 0,
    }


def _non_claims() -> tuple[str, ...]:
    return (
        "not production",
        "not public auditor package",
        "not real airline booking",
        "not real payment",
        "not real ticket",
        "not core extraction",
        "no real airline API",
        "no real bank API",
        "no GDS, NDC, or Open Banking connector",
        "no provider/network/Gemini call",
        "no raw passport/card/IBAN/payment token exposure",
        "no real-world effects",
    )


def _validate_report(report: Mapping[str, Any]) -> tuple[str, ...]:
    errors: tuple[str, ...] = ()
    ledger = report["shared_transaction_ledger"]
    counters = report["counter_table"]
    sandbox = report["airline_offer_hold_sandbox"]
    bank_sandbox = report["bank_payment_authorization_sandbox"]
    client_orchestration = report["client_purchase_orchestration"]
    ticket_corridor = report["airline_ticket_issue_mock_corridor"]
    integrated_trace = report["integrated_transaction_trace"]
    routing_matrix = report["cross_root_evidence_routing_matrix"]
    final_summary = report["final_tri_party_mock_summary"]
    fixtures = report["mock_protocol_fixtures"]

    if report.get("transaction_id") != TRANSACTION_ID:
        errors += ("transaction_id_mismatch",)
    transaction_ids = {
        report.get("transaction_id"),
        report["transaction_identity"].get("transaction_id"),
    }
    transaction_ids.update(row["transaction_id"] for row in ledger)
    transaction_ids.update(
        fixture["transaction_id"]
        for fixture in fixtures.values()
        if "transaction_id" in fixture
    )
    transaction_ids.add(sandbox.get("transaction_id"))
    transaction_ids.add(bank_sandbox.get("transaction_id"))
    transaction_ids.add(client_orchestration.get("transaction_id"))
    transaction_ids.add(ticket_corridor.get("transaction_id"))
    transaction_ids.update(row["transaction_id"] for row in integrated_trace)
    transaction_ids.update(row["transaction_id"] for row in routing_matrix)
    transaction_ids.add(final_summary.get("transaction_id"))
    if transaction_ids != {TRANSACTION_ID}:
        errors += ("transaction_id_set_mismatch",)
    if {row["transaction_id"] for row in ledger} != {TRANSACTION_ID}:
        errors += ("ledger_transaction_id_mismatch",)
    if len(ledger) != 14:
        errors += ("ledger_entry_count_mismatch",)
    if set(report["participants"]) != {"ClientRoot", "AirlineRoot", "BankRoot"}:
        errors += ("participant_set_mismatch",)
    for view_key in ("client_root_view", "airline_root_view", "bank_root_view"):
        if not report.get(view_key):
            errors += (f"missing_root_view:{view_key}",)
    if sandbox.get("sandbox_status") != STATUS_PASS:
        errors += ("airline_offer_hold_sandbox_not_pass",)
    if sandbox.get("transaction_id") != TRANSACTION_ID:
        errors += ("airline_offer_hold_sandbox_transaction_id_mismatch",)
    for key in (
        "offer_request_validated",
        "mock_inventory_checked",
        "mock_fare_checked",
        "baggage_rule_checked",
        "offer_ttl_checked",
        "offer_response_created",
        "offer_hold_commit_packet_created",
        "offer_hold_commit_packet_root_created",
        "offer_hold_commit_packet_validated",
        "offer_hold_receipt_created",
        "offer_hold_receipt_validated",
        "offer_hold_receipt_evidence_only",
    ):
        if sandbox.get(key) is not True:
            errors += (f"airline_offer_hold_sandbox_flag_false:{key}",)
    if sandbox.get("offer_hold_commit_packet_created_by") != "airline_root":
        errors += ("offer_hold_commit_packet_creator_not_airline_root",)
    for key in (
        "offer_hold_receipt_payment_permission_created",
        "offer_hold_receipt_ticket_permission_created",
        "real_airline_api_called",
        "real_booking_created",
        "real_ticket_issued",
    ):
        if sandbox.get(key) is not False:
            errors += (f"airline_offer_hold_sandbox_flag_true:{key}",)
    if sandbox.get("real_world_effects_count") != 0:
        errors += ("airline_offer_hold_sandbox_effects_nonzero",)

    offer_hold_packet = fixtures["AirlineOfferHoldCommitPacketV01"]
    if offer_hold_packet.get("created_by") != "airline_root":
        errors += ("offer_hold_packet_fixture_creator_not_airline_root",)
    if offer_hold_packet.get("root_created") is not True:
        errors += ("offer_hold_packet_fixture_not_root_created",)
    if offer_hold_packet.get("allowed_root_id") != AIRLINE_ROOT_ID:
        errors += ("offer_hold_packet_fixture_wrong_root",)
    for key in (
        "payment_permission_created",
        "ticket_permission_created",
        "real_airline_api_allowed",
        "real_booking_allowed",
    ):
        if offer_hold_packet.get(key) is not False:
            errors += (f"offer_hold_packet_forbidden_flag_true:{key}",)

    offer_hold_receipt = fixtures["AirlineOfferHoldReceiptV01"]
    if offer_hold_receipt.get("evidence_only") is not True:
        errors += ("offer_hold_receipt_not_evidence_only",)
    if offer_hold_receipt.get("payment_permission_created") is not False:
        errors += ("offer_hold_receipt_payment_permission_created",)
    if offer_hold_receipt.get("ticket_permission_created") is not False:
        errors += ("offer_hold_receipt_ticket_permission_created",)

    if bank_sandbox.get("sandbox_status") != STATUS_PASS:
        errors += ("bank_payment_authorization_sandbox_not_pass",)
    if bank_sandbox.get("transaction_id") != TRANSACTION_ID:
        errors += ("bank_payment_authorization_sandbox_transaction_id_mismatch",)
    for key in (
        "offer_hold_receipt_observed",
        "client_purchase_approval_evidence_observed",
        "payment_profile_sealed_ref_observed",
        "amount_currency_validated",
        "merchant_airline_ref_validated",
        "payment_token_ref_validated",
        "debtor_slot_ref_validated",
        "idempotency_checked",
        "expiry_ttl_checked",
        "bank_payment_intent_created",
        "bank_payment_consent_created",
        "bank_payment_authorization_commit_packet_created",
        "bank_payment_authorization_commit_packet_root_created",
        "bank_payment_authorization_commit_packet_validated",
        "payment_authorization_receipt_created",
        "payment_authorization_receipt_validated",
        "payment_status_receipt_created",
        "payment_status_receipt_validated",
        "payment_authorization_receipt_evidence_only",
        "payment_status_receipt_evidence_only",
    ):
        if bank_sandbox.get(key) is not True:
            errors += (f"bank_payment_authorization_sandbox_flag_false:{key}",)
    if bank_sandbox.get("bank_payment_authorization_commit_packet_created_by") != "bank_root":
        errors += ("bank_payment_authorization_packet_creator_not_bank_root",)
    for key in (
        "payment_authorization_receipt_ticket_permission_created",
        "payment_authorization_receipt_real_payment_executed",
        "payment_status_receipt_settlement_executed",
        "payment_status_receipt_ticket_permission_created",
        "bank_root_created_ticket",
        "real_bank_api_called",
        "real_payment_executed",
        "real_settlement_executed",
        "real_ticket_issued",
    ):
        if bank_sandbox.get(key) is not False:
            errors += (f"bank_payment_authorization_sandbox_flag_true:{key}",)
    if bank_sandbox.get("real_world_effects_count") != 0:
        errors += ("bank_payment_authorization_sandbox_effects_nonzero",)

    bank_payment_packet = fixtures["BankPaymentAuthorizationCommitPacketV01"]
    if bank_payment_packet.get("created_by") != "bank_root":
        errors += ("bank_payment_packet_fixture_creator_not_bank_root",)
    if bank_payment_packet.get("root_created") is not True:
        errors += ("bank_payment_packet_fixture_not_root_created",)
    if bank_payment_packet.get("allowed_root_id") != BANK_ROOT_ID:
        errors += ("bank_payment_packet_fixture_wrong_root",)
    for key in (
        "ticket_permission_created",
        "real_payment_allowed",
        "real_bank_api_allowed",
        "real_settlement_allowed",
    ):
        if bank_payment_packet.get(key) is not False:
            errors += (f"bank_payment_packet_forbidden_flag_true:{key}",)

    payment_authorization_receipt = fixtures["BankPaymentAuthorizationReceiptV01"]
    if payment_authorization_receipt.get("evidence_only") is not True:
        errors += ("payment_authorization_receipt_not_evidence_only",)
    if payment_authorization_receipt.get("ticket_created") is not False:
        errors += ("payment_authorization_receipt_ticket_created",)
    if payment_authorization_receipt.get("real_payment_executed") is not False:
        errors += ("payment_authorization_receipt_real_payment_executed",)

    payment_status_receipt = fixtures["BankPaymentStatusReceiptV01"]
    if payment_status_receipt.get("evidence_only") is not True:
        errors += ("payment_status_receipt_not_evidence_only",)
    if payment_status_receipt.get("settlement_executed") is not False:
        errors += ("payment_status_receipt_settlement_executed",)
    if payment_status_receipt.get("real_payment_executed") is not False:
        errors += ("payment_status_receipt_real_payment_executed",)

    if client_orchestration.get("orchestration_status") != STATUS_PASS:
        errors += ("client_purchase_orchestration_not_pass",)
    if client_orchestration.get("transaction_id") != TRANSACTION_ID:
        errors += ("client_purchase_orchestration_transaction_id_mismatch",)
    for key in (
        "travel_intent_observed",
        "passenger_sealed_refs_observed",
        "payment_profile_sealed_ref_observed",
        "offer_response_observed",
        "offer_hold_receipt_observed",
        "selected_offer_within_user_max_price",
        "client_purchase_approval_evidence_created",
        "client_purchase_approval_evidence_root_created",
        "client_purchase_approval_evidence_validated",
        "client_purchase_approval_evidence_evidence_only",
        "routed_to_bank_root",
        "routed_to_airline_root",
        "bank_payment_authorization_receipt_observed",
        "bank_payment_status_receipt_observed",
        "client_final_purchase_summary_created",
    ):
        if client_orchestration.get(key) is not True:
            errors += (f"client_purchase_orchestration_flag_false:{key}",)
    if (
        client_orchestration.get("client_purchase_approval_evidence_created_by")
        != "client_root"
    ):
        errors += ("client_purchase_approval_creator_not_client_root",)
    for key in (
        "client_root_authorized_bank_payment",
        "client_root_issued_ticket",
        "client_root_created_airline_order",
        "client_root_created_bank_receipt",
        "client_root_created_action_commit_packet",
        "raw_passport_exposed",
        "raw_card_exposed",
        "raw_iban_exposed",
        "raw_payment_token_exposed",
        "real_payment_executed",
        "real_ticket_issued",
        "real_booking_created",
    ):
        if client_orchestration.get(key) is not False:
            errors += (f"client_purchase_orchestration_flag_true:{key}",)
    if client_orchestration.get("real_world_effects_count") != 0:
        errors += ("client_purchase_orchestration_effects_nonzero",)

    client_purchase_approval = fixtures["ClientPurchaseApprovalEvidenceV01"]
    if client_purchase_approval.get("created_by") != "client_root":
        errors += ("client_purchase_approval_fixture_creator_not_client_root",)
    if client_purchase_approval.get("root_created") is not True:
        errors += ("client_purchase_approval_fixture_not_root_created",)
    if client_purchase_approval.get("evidence_only") is not True:
        errors += ("client_purchase_approval_fixture_not_evidence_only",)
    for key in (
        "bank_authority_created",
        "airline_authority_created",
        "payment_permission_created",
        "ticket_permission_created",
        "action_commit_packet_created",
        "receipt_created",
    ):
        if client_purchase_approval.get(key) is not False:
            errors += (f"client_purchase_approval_forbidden_flag_true:{key}",)

    client_summary = fixtures["ClientFinalTravelSummaryV01"]
    if client_summary.get("evidence_only") is not True:
        errors += ("client_final_summary_not_evidence_only",)
    for key in (
        "ticket_issued",
        "real_ticket_issued",
        "real_payment_executed",
        "real_booking_created",
    ):
        if client_summary.get(key) is not False:
            errors += (f"client_final_summary_forbidden_flag_true:{key}",)

    if ticket_corridor.get("corridor_status") != STATUS_PASS:
        errors += ("airline_ticket_issue_mock_corridor_not_pass",)
    if ticket_corridor.get("transaction_id") != TRANSACTION_ID:
        errors += ("airline_ticket_issue_mock_corridor_transaction_id_mismatch",)
    for key in (
        "offer_hold_receipt_observed",
        "client_purchase_approval_evidence_observed",
        "payment_authorization_receipt_observed",
        "payment_status_receipt_observed",
        "offer_hold_ttl_freshness_validated",
        "selected_offer_match_validated",
        "amount_currency_match_validated",
        "merchant_airline_ref_match_validated",
        "passenger_sealed_ref_validated",
        "payment_evidence_validated_against_offer_hold",
        "raw_passport_absent",
        "raw_card_absent",
        "raw_payment_token_absent",
        "airline_ticket_issue_commit_packet_created",
        "airline_ticket_issue_commit_packet_root_created",
        "airline_ticket_issue_commit_packet_validated",
        "airline_order_created_receipt_created",
        "airline_order_created_receipt_validated",
        "mock_ticket_receipt_created",
        "mock_ticket_receipt_validated",
        "mock_pnr_created",
        "mock_pnr_validated",
        "mock_ticket_receipt_evidence_only",
    ):
        if ticket_corridor.get(key) is not True:
            errors += (f"airline_ticket_issue_corridor_flag_false:{key}",)
    if ticket_corridor.get("airline_ticket_issue_commit_packet_created_by") != "airline_root":
        errors += ("airline_ticket_issue_packet_creator_not_airline_root",)
    for key in (
        "mock_ticket_receipt_real_ticket",
        "mock_ticket_receipt_payment_created",
        "mock_pnr_real_booking",
        "payment_authorization_receipt_created_ticket",
        "client_purchase_approval_created_ticket",
        "offer_hold_receipt_created_ticket",
        "airline_root_authorized_payment",
        "airline_root_called_real_airline_api",
        "airline_root_called_real_gds_api",
        "real_ticket_issued",
        "real_booking_created",
        "real_payment_executed",
        "real_settlement_executed",
    ):
        if ticket_corridor.get(key) is not False:
            errors += (f"airline_ticket_issue_corridor_flag_true:{key}",)
    if ticket_corridor.get("real_world_effects_count") != 0:
        errors += ("airline_ticket_issue_corridor_effects_nonzero",)

    ticket_issue_packet = fixtures["AirlineTicketIssueCommitPacketV01"]
    if ticket_issue_packet.get("created_by") != "airline_root":
        errors += ("ticket_issue_packet_fixture_creator_not_airline_root",)
    if ticket_issue_packet.get("root_created") is not True:
        errors += ("ticket_issue_packet_fixture_not_root_created",)
    if ticket_issue_packet.get("allowed_root_id") != AIRLINE_ROOT_ID:
        errors += ("ticket_issue_packet_fixture_wrong_root",)
    for key in (
        "real_ticket_allowed",
        "real_booking_allowed",
        "real_airline_api_allowed",
        "real_payment_allowed",
    ):
        if ticket_issue_packet.get(key) is not False:
            errors += (f"ticket_issue_packet_forbidden_flag_true:{key}",)

    order_receipt = fixtures["AirlineOrderCreatedReceiptV01"]
    if order_receipt.get("created_by") != "airline_root":
        errors += ("order_receipt_fixture_creator_not_airline_root",)
    if order_receipt.get("evidence_only") is not True:
        errors += ("order_receipt_not_evidence_only",)
    for key in ("payment_created", "real_ticket_issued", "real_booking_created"):
        if order_receipt.get(key) is not False:
            errors += (f"order_receipt_forbidden_flag_true:{key}",)

    mock_ticket_receipt = fixtures["MockTicketReceiptV01"]
    if mock_ticket_receipt.get("created_by") != "airline_root":
        errors += ("mock_ticket_receipt_fixture_creator_not_airline_root",)
    if mock_ticket_receipt.get("evidence_only") is not True:
        errors += ("mock_ticket_receipt_not_evidence_only",)
    for key in (
        "real_ticket",
        "real_travel_booking_created",
        "payment_created",
        "future_payment_permission_created",
    ):
        if mock_ticket_receipt.get(key) is not False:
            errors += (f"mock_ticket_receipt_forbidden_flag_true:{key}",)

    mock_pnr = fixtures["MockPNRV01"]
    if mock_pnr.get("created_by") != "airline_root":
        errors += ("mock_pnr_fixture_creator_not_airline_root",)
    if mock_pnr.get("mock_only") is not True:
        errors += ("mock_pnr_fixture_not_mock_only",)
    if mock_pnr.get("real_booking") is not False:
        errors += ("mock_pnr_real_booking",)

    if client_summary.get("mock_ticket_receipt_id") != "mock_ticket_receipt:mock_airline_al:001":
        errors += ("client_final_summary_missing_mock_ticket_receipt",)
    if (
        client_summary.get("current_client_status")
        != "mock_ticket_evidence_received_no_real_travel_booking"
    ):
        errors += ("client_final_summary_status_mismatch",)
    if client_summary.get("mock_ticket_evidence_received") is not True:
        errors += ("client_final_summary_mock_ticket_evidence_missing",)

    if len(integrated_trace) != 17:
        errors += ("integrated_trace_phase_count_mismatch",)
    if {row["transaction_id"] for row in integrated_trace} != {TRANSACTION_ID}:
        errors += ("integrated_trace_transaction_id_mismatch",)
    expected_phase_ids = (
        "client_travel_intent_recorded",
        "client_to_airline_offer_request",
        "airline_offer_hold_sandbox_completed",
        "airline_to_client_offer_hold_receipt_returned",
        "client_offer_selected",
        "client_purchase_approval_evidence_created",
        "client_to_bank_payment_authorization_request",
        "bank_payment_authorization_sandbox_completed",
        "bank_to_client_payment_authorization_receipt_returned",
        "bank_to_client_payment_status_receipt_returned",
        "client_to_airline_payment_evidence_forwarded",
        "airline_ticket_issue_mock_corridor_completed",
        "airline_to_client_order_created_receipt_returned",
        "airline_to_client_mock_ticket_receipt_returned",
        "airline_to_client_mock_pnr_returned",
        "client_final_mock_travel_summary_created",
        "final_shared_summary_fixture_created",
    )
    if tuple(row["phase_id"] for row in integrated_trace) != expected_phase_ids:
        errors += ("integrated_trace_phase_order_mismatch",)
    for row in integrated_trace:
        if row.get("authority_transferred") is not False:
            errors += ("integrated_trace_authority_transfer",)
        if row.get("real_world_effects_count") != 0:
            errors += ("integrated_trace_effects_nonzero",)
        for key in (
            "raw_secrets_exposed",
            "real_ticket_claimed",
            "real_payment_claimed",
            "real_booking_claimed",
        ):
            if row.get(key) is not False:
                errors += (f"integrated_trace_forbidden_flag_true:{key}",)

    if len(routing_matrix) != 6:
        errors += ("cross_root_routing_row_count_mismatch",)
    expected_routes = (
        (CLIENT_ROOT_ID, AIRLINE_ROOT_ID),
        (AIRLINE_ROOT_ID, CLIENT_ROOT_ID),
        (CLIENT_ROOT_ID, BANK_ROOT_ID),
        (BANK_ROOT_ID, CLIENT_ROOT_ID),
        (CLIENT_ROOT_ID, AIRLINE_ROOT_ID),
        (AIRLINE_ROOT_ID, CLIENT_ROOT_ID),
    )
    actual_routes = tuple(
        (row["source_root_id"], row["target_root_id"]) for row in routing_matrix
    )
    if actual_routes != expected_routes:
        errors += ("cross_root_routing_order_mismatch",)
    for row in routing_matrix:
        if row.get("evidence_only") is not True:
            errors += ("cross_root_routing_not_evidence_only",)
        if row.get("authority_transferred") is not False:
            errors += ("cross_root_routing_authority_transfer",)
        if row.get("real_world_effects_count") != 0:
            errors += ("cross_root_routing_effects_nonzero",)
    for key in (
        "raw_passport_exposed",
        "raw_card_exposed",
        "payment_permission_created",
        "ticket_permission_created",
        "bank_authority_created_by_client",
        "raw_iban_exposed",
        "real_payment_executed",
        "airline_authority_created_by_client",
        "ticket_permission_created_by_payment_receipt",
        "real_ticket_issued",
        "real_booking_created",
        "payment_created",
    ):
        for row in routing_matrix:
            if key in row and row[key] is not False:
                errors += (f"cross_root_routing_forbidden_flag_true:{key}",)

    if final_summary.get("final_status") != STATUS_PASS:
        errors += ("final_tri_party_mock_summary_not_pass",)
    if final_summary.get("transaction_id") != TRANSACTION_ID:
        errors += ("final_tri_party_mock_summary_transaction_id_mismatch",)
    for key, expected in (
        (
            "client_view_status",
            "mock_ticket_evidence_received_no_real_travel_booking",
        ),
        ("airline_view_status", "mock_order_ticket_pnr_evidence_created"),
        ("bank_view_status", "mock_payment_authorized_not_settled"),
        ("selected_offer_id", "offer:mock_airline_al:PAR-LIM:001"),
        ("offer_hold_receipt_id", "offer_hold_receipt:mock_airline_al:001"),
        (
            "payment_authorization_receipt_id",
            "payment_authorization_receipt:mock_bank_a:001",
        ),
        ("payment_status_receipt_id", "payment_status_receipt:mock_bank_a:001"),
        ("order_created_receipt_id", "order_created_receipt:mock_airline_al:001"),
        ("mock_ticket_receipt_id", "mock_ticket_receipt:mock_airline_al:001"),
        ("mock_pnr", "PNR-EEH01"),
    ):
        if final_summary.get(key) != expected:
            errors += (f"final_tri_party_mock_summary_value_mismatch:{key}",)
    if final_summary.get("receipts_evidence_only") is not True:
        errors += ("final_tri_party_mock_summary_receipts_not_evidence_only",)
    for key in (
        "authority_transferred_between_roots",
        "client_root_issued_ticket",
        "airline_root_authorized_payment",
        "bank_root_created_ticket",
        "real_airline_api_called",
        "real_bank_api_called",
        "real_gds_api_called",
        "real_payment_executed",
        "real_settlement_executed",
        "real_ticket_issued",
        "real_booking_created",
        "provider_called",
        "network_used",
        "gemini_called",
    ):
        if final_summary.get(key) is not False:
            errors += (f"final_tri_party_mock_summary_flag_true:{key}",)
    if final_summary.get("real_world_effects_count") != 0:
        errors += ("final_tri_party_mock_summary_effects_nonzero",)

    if not all(row["boundary_preserved"] and row["violation_count"] == 0 for row in report["root_boundary_matrix"]):
        errors += ("root_boundary_violation",)
    if not all(row["boundary_preserved"] and row["violation_count"] == 0 for row in report["receipt_boundary_matrix"]):
        errors += ("receipt_boundary_violation",)

    privacy = report["privacy_boundary_matrix"]
    for key in (
        "raw_passport_exposed_count",
        "raw_card_exposed_count",
        "raw_iban_exposed_count",
        "raw_payment_token_exposed_count",
        "raw_birthdate_exposed_count",
        "raw_document_number_exposed_count",
    ):
        if privacy.get(key) != 0:
            errors += (f"privacy_counter_nonzero:{key}",)
    for key in (
        "passenger_sealed_ref_only",
        "payment_profile_sealed_ref_only",
        "vault_refs_not_llm_context",
        "no_raw_private_profile_in_provider_context",
        "no_raw_secrets_in_artifacts",
    ):
        if privacy.get(key) is not True:
            errors += (f"privacy_flag_false:{key}",)

    if any(actor["executed_in_slice_b"] for actor in report["future_semantic_actor_topology"]):
        errors += ("future_semantic_actor_executed",)
    if any(
        actor["creates_authority"]
        or actor["creates_action_commit_packet"]
        or actor["creates_receipt"]
        or actor["creates_ticket"]
        or actor["executes_payment"]
        or actor["calls_real_api"]
        for actor in report["future_semantic_actor_topology"]
    ):
        errors += ("future_semantic_actor_boundary_violation",)

    fractal_cells = tuple(
        cell
        for cells in report["future_vertical_fractal_map"].values()
        for cell in cells
    )
    if len(fractal_cells) < 14:
        errors += ("future_vertical_fractal_cell_count_low",)
    if any(cell["executed_in_slice_b"] for cell in fractal_cells):
        errors += ("future_vertical_fractal_cell_executed",)
    if any(cell["creates_authority"] or cell["real_world_effects_count"] != 0 for cell in fractal_cells):
        errors += ("future_vertical_fractal_cell_boundary_violation",)

    required_zero_counter_keys = (
        "future_semantic_actor_roles_executed_count",
        "future_vertical_fractal_cells_executed_count",
        "client_root_issued_ticket_count",
        "airline_root_authorized_payment_count",
        "bank_root_created_ticket_count",
        "payment_receipt_created_ticket_count",
        "ticket_receipt_created_payment_count",
        "raw_passport_exposed_count",
        "raw_card_exposed_count",
        "raw_iban_exposed_count",
        "raw_payment_token_exposed_count",
        "real_airline_api_called_count",
        "real_bank_api_called_count",
        "real_payment_executed_count",
        "real_settlement_executed_count",
        "real_booking_created_count",
        "real_ticket_issued_count",
        "real_travel_booking_created_count",
        "provider_called_count",
        "network_used_count",
        "gemini_called_count",
        "real_world_effects_count",
        "bank_payment_authorization_commit_packet_created_by_client_root_count",
        "bank_payment_authorization_commit_packet_created_by_airline_root_count",
        "payment_authorization_receipt_ticket_permission_created_count",
        "payment_authorization_receipt_real_payment_executed_count",
        "payment_status_receipt_ticket_permission_created_count",
        "payment_status_receipt_settlement_executed_count",
        "client_purchase_approval_evidence_created_by_airline_root_count",
        "client_purchase_approval_evidence_created_by_bank_root_count",
        "client_root_authorized_bank_payment_count",
        "client_root_created_airline_order_count",
        "client_root_created_bank_receipt_count",
        "client_root_created_action_commit_packet_count",
        "client_raw_passport_exposed_count",
        "client_raw_card_exposed_count",
        "client_raw_iban_exposed_count",
        "client_raw_payment_token_exposed_count",
        "airline_ticket_issue_commit_packet_created_by_client_root_count",
        "airline_ticket_issue_commit_packet_created_by_bank_root_count",
        "mock_ticket_receipt_real_ticket_count",
        "mock_pnr_real_booking_count",
        "payment_authorization_receipt_created_ticket_count",
        "client_purchase_approval_created_ticket_count",
        "offer_hold_receipt_created_ticket_count",
        "airline_root_called_real_airline_api_count",
        "airline_root_called_real_gds_api_count",
        "cross_root_authority_transfer_count",
        "cross_root_real_world_effects_count",
        "final_real_ticket_issued_count",
        "final_real_payment_executed_count",
        "final_real_booking_created_count",
        "final_authority_transferred_between_roots_count",
    )
    for key in required_zero_counter_keys:
        if counters.get(key) != 0:
            errors += (f"counter_nonzero:{key}",)
    for key, expected in (
        ("tri_party_airline_transaction_count", 1),
        ("client_root_count", 1),
        ("airline_root_count", 1),
        ("bank_root_count", 1),
        ("shared_transaction_id_count", 1),
        ("shared_ledger_entry_count", 14),
        ("offer_candidates_created_count", 1),
        ("offer_hold_receipt_fixture_count", 1),
        ("airline_offer_hold_sandbox_invoked_count", 1),
        ("airline_offer_request_validated_count", 1),
        ("mock_inventory_checked_count", 1),
        ("mock_fare_checked_count", 1),
        ("baggage_rule_checked_count", 1),
        ("offer_ttl_checked_count", 1),
        ("airline_offer_response_created_count", 1),
        ("airline_offer_hold_commit_packet_created_count", 1),
        ("airline_offer_hold_commit_packet_created_by_airline_root_count", 1),
        ("airline_offer_hold_commit_packet_created_by_client_root_count", 0),
        ("airline_offer_hold_commit_packet_created_by_bank_root_count", 0),
        ("airline_offer_hold_commit_packet_validated_count", 1),
        ("airline_offer_hold_receipt_created_count", 1),
        ("airline_offer_hold_receipt_validated_count", 1),
        ("offer_hold_receipt_payment_permission_created_count", 0),
        ("offer_hold_receipt_ticket_permission_created_count", 0),
        ("client_purchase_approval_evidence_fixture_count", 1),
        ("client_purchase_orchestration_invoked_count", 1),
        ("client_travel_intent_observed_count", 1),
        ("client_passenger_sealed_refs_observed_count", 1),
        ("client_payment_profile_sealed_ref_observed_count", 1),
        ("client_offer_response_observed_count", 1),
        ("client_offer_hold_receipt_observed_count", 1),
        ("client_offer_selected_count", 1),
        ("client_selected_offer_within_user_max_price_count", 1),
        ("client_purchase_approval_evidence_created_count", 1),
        ("client_purchase_approval_evidence_created_by_client_root_count", 1),
        ("client_purchase_approval_evidence_created_by_airline_root_count", 0),
        ("client_purchase_approval_evidence_created_by_bank_root_count", 0),
        ("client_purchase_approval_evidence_validated_count", 1),
        ("client_purchase_approval_evidence_routed_to_bank_root_count", 1),
        ("client_purchase_approval_evidence_routed_to_airline_root_count", 1),
        ("client_bank_payment_authorization_receipt_observed_count", 1),
        ("client_bank_payment_status_receipt_observed_count", 1),
        ("client_final_purchase_summary_created_count", 1),
        ("client_root_authorized_bank_payment_count", 0),
        ("client_root_issued_ticket_count", 0),
        ("client_root_created_airline_order_count", 0),
        ("client_root_created_bank_receipt_count", 0),
        ("client_root_created_action_commit_packet_count", 0),
        ("client_raw_passport_exposed_count", 0),
        ("client_raw_card_exposed_count", 0),
        ("client_raw_iban_exposed_count", 0),
        ("client_raw_payment_token_exposed_count", 0),
        ("bank_payment_intent_fixture_count", 1),
        ("bank_payment_consent_fixture_count", 1),
        ("bank_payment_authorization_receipt_fixture_count", 1),
        ("bank_payment_status_receipt_fixture_count", 1),
        ("bank_payment_authorization_sandbox_invoked_count", 1),
        ("bank_offer_hold_receipt_observed_count", 1),
        ("bank_client_purchase_approval_evidence_observed_count", 1),
        ("bank_payment_profile_sealed_ref_observed_count", 1),
        ("bank_amount_currency_validated_count", 1),
        ("bank_merchant_airline_ref_validated_count", 1),
        ("bank_payment_token_ref_validated_count", 1),
        ("bank_debtor_slot_ref_validated_count", 1),
        ("bank_idempotency_checked_count", 1),
        ("bank_expiry_ttl_checked_count", 1),
        ("bank_payment_intent_created_count", 1),
        ("bank_payment_consent_created_count", 1),
        ("bank_payment_authorization_commit_packet_created_count", 1),
        ("bank_payment_authorization_commit_packet_created_by_bank_root_count", 1),
        ("bank_payment_authorization_commit_packet_created_by_client_root_count", 0),
        ("bank_payment_authorization_commit_packet_created_by_airline_root_count", 0),
        ("bank_payment_authorization_commit_packet_validated_count", 1),
        ("payment_authorization_receipt_created_count", 1),
        ("payment_authorization_receipt_validated_count", 1),
        ("payment_status_receipt_created_count", 1),
        ("payment_status_receipt_validated_count", 1),
        ("payment_authorization_receipt_ticket_permission_created_count", 0),
        ("payment_authorization_receipt_real_payment_executed_count", 0),
        ("payment_status_receipt_ticket_permission_created_count", 0),
        ("payment_status_receipt_settlement_executed_count", 0),
        ("airline_order_created_receipt_fixture_count", 1),
        ("mock_ticket_receipt_fixture_count", 1),
        ("mock_pnr_fixture_count", 1),
        ("airline_ticket_issue_mock_corridor_invoked_count", 1),
        ("airline_ticket_issue_offer_hold_receipt_observed_count", 1),
        ("airline_ticket_issue_client_purchase_approval_observed_count", 1),
        ("airline_ticket_issue_payment_authorization_receipt_observed_count", 1),
        ("airline_ticket_issue_payment_status_receipt_observed_count", 1),
        ("airline_ticket_issue_offer_hold_ttl_freshness_validated_count", 1),
        ("airline_ticket_issue_selected_offer_match_validated_count", 1),
        ("airline_ticket_issue_amount_currency_match_validated_count", 1),
        ("airline_ticket_issue_merchant_airline_ref_match_validated_count", 1),
        ("airline_ticket_issue_passenger_sealed_ref_validated_count", 1),
        (
            "airline_ticket_issue_payment_evidence_validated_against_offer_hold_count",
            1,
        ),
        ("airline_ticket_issue_commit_packet_created_count", 1),
        ("airline_ticket_issue_commit_packet_created_by_airline_root_count", 1),
        ("airline_ticket_issue_commit_packet_created_by_client_root_count", 0),
        ("airline_ticket_issue_commit_packet_created_by_bank_root_count", 0),
        ("airline_ticket_issue_commit_packet_validated_count", 1),
        ("airline_order_created_receipt_created_count", 1),
        ("airline_order_created_receipt_validated_count", 1),
        ("mock_ticket_receipt_created_count", 1),
        ("mock_ticket_receipt_validated_count", 1),
        ("mock_pnr_created_count", 1),
        ("mock_pnr_validated_count", 1),
        ("mock_ticket_receipt_evidence_only_count", 1),
        ("mock_ticket_receipt_real_ticket_count", 0),
        ("mock_pnr_real_booking_count", 0),
        ("payment_authorization_receipt_created_ticket_count", 0),
        ("client_purchase_approval_created_ticket_count", 0),
        ("offer_hold_receipt_created_ticket_count", 0),
        ("airline_root_called_real_airline_api_count", 0),
        ("airline_root_called_real_gds_api_count", 0),
        ("integrated_tri_party_transaction_trace_created_count", 1),
        ("integrated_trace_phase_count", 17),
        ("cross_root_evidence_routing_rows_count", 6),
        ("cross_root_authority_transfer_count", 0),
        ("cross_root_real_world_effects_count", 0),
        ("final_tri_party_mock_summary_created_count", 1),
        ("final_client_view_mock_ticket_evidence_received_count", 1),
        ("final_airline_view_mock_order_ticket_pnr_evidence_created_count", 1),
        ("final_bank_view_mock_payment_authorized_not_settled_count", 1),
        ("final_real_ticket_issued_count", 0),
        ("final_real_payment_executed_count", 0),
        ("final_real_booking_created_count", 0),
        ("final_authority_transferred_between_roots_count", 0),
        ("future_semantic_actor_roles_planned_count", 6),
        ("future_vertical_fractal_cells_planned_count", 14),
    ):
        if counters.get(key) != expected:
            errors += (f"counter_mismatch:{key}",)

    return errors


def _format_view(view: Mapping[str, Any]) -> str:
    return (
        f"root_id: {view['root_id']}; role: {view['role']}; "
        f"bounded_view_count: {len(view['bounded_view'])}"
    )


if __name__ == "__main__":
    raise SystemExit(main())
