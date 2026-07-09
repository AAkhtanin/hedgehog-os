from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from demo import run_tri_party_airline_ticket_purchase_mock_e2e_v01 as runner


def _report() -> dict[str, object]:
    return runner.collect_tri_party_airline_ticket_purchase_mock_e2e_v01()


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
    assert report["counter_table"]["shared_ledger_entry_count"] == 14

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


def test_airline_slice_c_source_import_boundary() -> None:
    source = Path(runner.__file__).read_text()

    assert "google.genai" not in source
    assert "import requests" not in source
    assert "import urllib" not in source
    assert "import openai" not in source
    assert "import subprocess" not in source
    assert "from hedgehog" not in source
    assert "import hedgehog" not in source
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
    ):
        assert left + right not in source
