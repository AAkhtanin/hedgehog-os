from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import asdict, is_dataclass
from pathlib import Path

from demo import run_human_airline_ticket_purchase_corridor_story_v01 as story
from demo import run_tri_party_airline_ticket_purchase_mock_e2e_v01 as source_runner


def _json_safe(value):
    if is_dataclass(value):
        return _json_safe(asdict(value))
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


def _write_source_json(tmp_path: Path, mutate=None) -> Path:
    report = _json_safe(
        source_runner.collect_tri_party_airline_ticket_purchase_mock_e2e_v01(),
    )
    if mutate is not None:
        mutate(report)
    path = tmp_path / "airline_corridor_source_report.json"
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def _collect_from_path(path: Path) -> dict:
    return story.collect_human_airline_ticket_purchase_corridor_story_v01(
        env={story.SOURCE_JSON_ENV: str(path)},
    )


def _write_raw_json(tmp_path: Path, value, name: str = "raw.json") -> Path:
    path = tmp_path / name
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
    return path


def test_airline_corridor_story_default_skipped_closed() -> None:
    report = story.collect_human_airline_ticket_purchase_corridor_story_v01(env={})

    assert report["final_status"] == story.SKIPPED_CLOSED
    assert report["skip_reason"] == "source_report_json_not_selected"
    assert report["counter_table"]["renderer_provider_called_count"] == 0
    assert report["counter_table"]["renderer_network_used_count"] == 0
    assert report["counter_table"]["renderer_gemini_called_count"] == 0


def test_airline_corridor_story_non_object_json_fails_closed(tmp_path: Path) -> None:
    for index, value in enumerate(([], "text", 42, None), start=1):
        report = _collect_from_path(
            _write_raw_json(tmp_path, value, name=f"non_object_{index}.json"),
        )

        assert report["final_status"] == story.FAIL_CLOSED
        assert report["validation_errors"] == (
            "source_report_json_top_level_not_object",
        )


def test_airline_corridor_story_valid_source_passes(tmp_path: Path) -> None:
    path = _write_source_json(tmp_path)
    report = _collect_from_path(path)

    assert report["final_status"] == story.PASS
    assert report["source_report_json"] == str(path)
    assert report["validation_errors"] == ()
    assert report["counter_table"]["human_story_created_count"] == 1


def test_airline_corridor_story_does_not_call_source_runner(tmp_path: Path, monkeypatch) -> None:
    path = _write_source_json(tmp_path)

    def forbidden_call():
        raise AssertionError("source runner was called")

    monkeypatch.setattr(
        source_runner,
        "collect_tri_party_airline_ticket_purchase_mock_e2e_v01",
        forbidden_call,
    )

    report = _collect_from_path(path)

    assert report["final_status"] == story.PASS


def test_airline_corridor_story_has_five_phase_cards(tmp_path: Path) -> None:
    report = _collect_from_path(_write_source_json(tmp_path))

    assert len(report["phase_cards"]) == 5
    assert [card["phase_id"] for card in report["phase_cards"]] == list(
        story.PHASE_ORDER,
    )
    assert report["counter_table"]["phase_cards_created_count"] == 5


def test_airline_corridor_story_has_one_transaction_three_roots(tmp_path: Path) -> None:
    summary = _collect_from_path(_write_source_json(tmp_path))[
        "one_transaction_three_roots"
    ]

    assert summary["transaction_id"] == story.EXPECTED_TRANSACTION_ID
    assert summary["client_root_id"] == story.CLIENT_ROOT_ID
    assert summary["airline_root_id"] == story.AIRLINE_ROOT_ID
    assert summary["bank_root_id"] == story.BANK_ROOT_ID
    assert summary["fourth_root_created"] is False


def test_airline_corridor_story_core_domain_boundary_is_explicit(tmp_path: Path) -> None:
    core_domain = _collect_from_path(_write_source_json(tmp_path))[
        "core_domain_delegation_story"
    ]

    assert story.CORE_DOMAIN_SENTENCE in core_domain["required_sentence"]
    assert "no post-Root LLM reasoning restart" in core_domain[
        "universal_core_guarded"
    ]
    assert "PNR" in core_domain["airline_domain_validated"][7]
    assert core_domain["not_every_airline_check_is_core"] is True


def test_airline_corridor_story_distinct_human_approval_and_purchase_intent(
    tmp_path: Path,
) -> None:
    cards = {
        card["card"]: card
        for card in _collect_from_path(_write_source_json(tmp_path))[
            "identity_lineage_story"
        ]
    }

    assert cards["Human approval"]["artifact_id"] != (
        cards["ClientPurchaseIntent"]["artifact_id"]
    )
    assert cards["ClientPurchaseIntent"]["source_human_approval_ref"] == (
        cards["Human approval"]["artifact_id"]
    )
    assert cards["Human approval"]["creates_intent_by_itself"] is False


def test_airline_corridor_story_distinct_bank_receipt_and_authorization_ref(
    tmp_path: Path,
) -> None:
    cards = {
        card["card"]: card
        for card in _collect_from_path(_write_source_json(tmp_path))[
            "identity_lineage_story"
        ]
    }

    assert cards["Bank payment receipt"]["artifact_id"] != (
        cards["BankPaymentAuthorizationRef"]["artifact_id"]
    )
    assert cards["BankPaymentAuthorizationRef"]["source_payment_receipt_id"] == (
        cards["Bank payment receipt"]["artifact_id"]
    )


def test_airline_corridor_story_distinct_purchase_receipt_and_final_summary(
    tmp_path: Path,
) -> None:
    cards = {
        card["card"]: card
        for card in _collect_from_path(_write_source_json(tmp_path))[
            "identity_lineage_story"
        ]
    }

    assert cards["MockPurchaseReceipt"]["artifact_id"] != (
        cards["ClientFinalTravelSummary"]["artifact_id"]
    )
    assert cards["ClientFinalTravelSummary"]["mock_purchase_receipt_id"] == (
        cards["MockPurchaseReceipt"]["artifact_id"]
    )


def test_airline_corridor_story_receipt_creator_geometry(tmp_path: Path) -> None:
    cards = {
        card["receipt"]: card
        for card in _collect_from_path(_write_source_json(tmp_path))[
            "receipt_creator_story"
        ]
    }

    assert cards["OfferHoldReceipt"]["created_by"] == story.HOLD_SANDBOX
    assert cards["OfferHoldReceipt"]["root_owner"] == story.AIRLINE_ROOT_ID
    assert cards["MockTicketReceipt"]["created_by"] == story.TICKET_SANDBOX
    assert cards["MockTicketReceipt"]["root_owner"] == story.AIRLINE_ROOT_ID
    assert cards["MockPurchaseReceipt"]["created_by"] == story.COMPLETION_OBSERVER
    assert cards["MockPurchaseReceipt"]["root_owner"] == story.CLIENT_ROOT_ID
    assert all(card["evidence_only"] is True for card in cards.values())


def test_airline_corridor_story_all_binding_rows_match(tmp_path: Path) -> None:
    matrix = _collect_from_path(_write_source_json(tmp_path))["binding_matrix_story"]
    rows = matrix["rows"]

    assert rows
    assert all(row["values_match"] is True for row in rows)
    assert all(row["raw_secret_used"] is False for row in rows)
    assert all(row["authority_transferred"] is False for row in rows)
    assert matrix["human_introduction"].startswith("Эта таблица доказывает")


def test_airline_corridor_story_semantics_come_from_source_artifact(tmp_path: Path) -> None:
    marker = "Custom artifact-backed corridor story goal"

    def mutate(report: dict) -> None:
        report["travel_intent"]["user_goal"] = marker

    path = _write_source_json(tmp_path, mutate=mutate)
    report = _collect_from_path(path)
    rendered = story.render_human_airline_ticket_purchase_corridor_story_v01(report)

    assert report["business_scene"]["user_goal"] == marker
    assert marker in rendered


def test_airline_corridor_story_wrong_phase_order_fails_closed(tmp_path: Path) -> None:
    def mutate(report: dict) -> None:
        phases = report["airline_ticket_purchase_corridor_v0_1"]["phase_results"]
        phases[0], phases[1] = phases[1], phases[0]

    report = _collect_from_path(_write_source_json(tmp_path, mutate=mutate))

    assert report["final_status"] == story.FAIL_CLOSED
    assert "corridor_phase_order_mismatch" in report["validation_errors"]


def test_airline_corridor_story_binding_mismatch_fails_closed(tmp_path: Path) -> None:
    def mutate(report: dict) -> None:
        report["airline_ticket_purchase_corridor_binding_matrix"][1][
            "values_match"
        ] = False

    report = _collect_from_path(_write_source_json(tmp_path, mutate=mutate))

    assert report["final_status"] == story.FAIL_CLOSED
    assert "binding_row_mismatch:offer_id" in report["validation_errors"]


def test_airline_corridor_story_phase_evidence_mismatch_fails_closed(tmp_path: Path) -> None:
    def mutate(report: dict) -> None:
        report["airline_ticket_purchase_corridor_v0_1"]["phase_results"][0][
            "evidence_refs_observed"
        ] = ["wrong:evidence"]

    report = _collect_from_path(_write_source_json(tmp_path, mutate=mutate))

    assert report["final_status"] == story.FAIL_CLOSED
    assert (
        "corridor_phase_evidence_mismatch:airline_offer_hold_phase"
        in report["validation_errors"]
    )


def test_airline_corridor_story_parallel_transaction_claim_fails_closed(
    tmp_path: Path,
) -> None:
    def mutate(report: dict) -> None:
        report["airline_ticket_purchase_corridor_integration"][
            "parallel_fixture_transaction_created"
        ] = True

    report = _collect_from_path(_write_source_json(tmp_path, mutate=mutate))

    assert report["final_status"] == story.FAIL_CLOSED
    assert (
        "integration_fact_mismatch:parallel_fixture_transaction_created"
        in report["validation_errors"]
    )


def test_airline_corridor_story_duplicate_execution_claim_fails_closed(
    tmp_path: Path,
) -> None:
    def mutate(report: dict) -> None:
        report["airline_ticket_purchase_corridor_integration"][
            "duplicate_corridor_execution_count"
        ] = 1

    report = _collect_from_path(_write_source_json(tmp_path, mutate=mutate))

    assert report["final_status"] == story.FAIL_CLOSED
    assert (
        "integration_fact_mismatch:duplicate_corridor_execution_count"
        in report["validation_errors"]
    )


def test_airline_corridor_story_wrong_receipt_creator_fails_closed(
    tmp_path: Path,
) -> None:
    def mutate(report: dict) -> None:
        report["mock_protocol_fixtures"]["MockTicketReceiptV01"][
            "created_by"
        ] = "airline_root"

    report = _collect_from_path(_write_source_json(tmp_path, mutate=mutate))

    assert report["final_status"] == story.FAIL_CLOSED
    assert "mock_ticket_receipt_creator_mismatch" in report["validation_errors"]


def test_airline_corridor_story_nonzero_effect_fails_closed(tmp_path: Path) -> None:
    def mutate(report: dict) -> None:
        report["counter_table"]["real_world_effects_count"] = 1

    report = _collect_from_path(_write_source_json(tmp_path, mutate=mutate))

    assert report["final_status"] == story.FAIL_CLOSED
    assert (
        "source_zero_effect_counter_nonzero:real_world_effects_count"
        in report["validation_errors"]
    )


def test_airline_corridor_story_complete_receipt_safety_fails_closed(
    tmp_path: Path,
) -> None:
    cases = (
        (
            "AirlineOfferHoldReceiptV01",
            "purchase_permission_created",
            True,
            "offer_hold_receipt_forbidden_flag:purchase_permission_created",
        ),
        (
            "AirlineOfferHoldReceiptV01",
            "future_permission_created",
            True,
            "offer_hold_receipt_forbidden_flag:future_permission_created",
        ),
        (
            "MockTicketReceiptV01",
            "future_ticket_permission_created",
            True,
            "mock_ticket_receipt_forbidden_flag:future_ticket_permission_created",
        ),
        (
            "MockTicketReceiptV01",
            "real_booking",
            True,
            "mock_ticket_receipt_forbidden_flag:real_booking",
        ),
        (
            "MockTicketReceiptV01",
            "real_world_effects_count",
            1,
            "mock_ticket_receipt_forbidden_flag:real_world_effects_count",
        ),
        (
            "MockPurchaseReceiptV01",
            "real_payment_executed",
            True,
            "mock_purchase_receipt_forbidden_flag:real_payment_executed",
        ),
        (
            "MockPurchaseReceiptV01",
            "real_ticket_issued",
            True,
            "mock_purchase_receipt_forbidden_flag:real_ticket_issued",
        ),
        (
            "MockPurchaseReceiptV01",
            "real_booking_created",
            True,
            "mock_purchase_receipt_forbidden_flag:real_booking_created",
        ),
        (
            "MockPurchaseReceiptV01",
            "real_world_effects_count",
            1,
            "mock_purchase_receipt_forbidden_flag:real_world_effects_count",
        ),
    )

    for fixture_name, field_name, value, expected_error in cases:
        def mutate(report: dict, fixture_name=fixture_name, field_name=field_name, value=value) -> None:
            report["mock_protocol_fixtures"][fixture_name][field_name] = value

        report = _collect_from_path(_write_source_json(tmp_path, mutate=mutate))

        assert report["final_status"] == story.FAIL_CLOSED
        assert expected_error in report["validation_errors"]


def test_airline_corridor_story_cross_root_matrix_mutations_fail_closed(
    tmp_path: Path,
) -> None:
    cases = (
        (
            lambda report: report["cross_root_evidence_routing_matrix"].clear(),
            "cross_root_evidence_matrix_missing",
        ),
        (
            lambda report: report["cross_root_evidence_routing_matrix"][0].update(
                {"authority_transferred": True},
            ),
            "cross_root_authority_transfer_detected",
        ),
        (
            lambda report: report["cross_root_evidence_routing_matrix"][0].update(
                {"transaction_id": "wrong"},
            ),
            "cross_root_transaction_mismatch",
        ),
    )

    for mutate, expected_error in cases:
        report = _collect_from_path(_write_source_json(tmp_path, mutate=mutate))

        assert report["final_status"] == story.FAIL_CLOSED
        assert expected_error in report["validation_errors"]


def test_airline_corridor_story_root_boundary_matrix_mutations_fail_closed(
    tmp_path: Path,
) -> None:
    cases = (
        (
            lambda report: report["root_boundary_matrix"].clear(),
            "root_boundary_matrix_missing",
        ),
        (
            lambda report: report["root_boundary_matrix"][0].update(
                {"boundary_preserved": False},
            ),
            "root_boundary_not_preserved",
        ),
        (
            lambda report: report["root_boundary_matrix"][0].update(
                {"violation_count": 1},
            ),
            "root_boundary_violation_nonzero",
        ),
        (
            lambda report: report["participants"].update(
                {"SharedRoot": {"root_id": "root:shared"}},
            ),
            "shared_or_fourth_root_detected",
        ),
    )

    for mutate, expected_error in cases:
        report = _collect_from_path(_write_source_json(tmp_path, mutate=mutate))

        assert report["final_status"] == story.FAIL_CLOSED
        assert expected_error in report["validation_errors"]


def test_airline_corridor_story_core_domain_delegation_mutations_fail_closed(
    tmp_path: Path,
) -> None:
    matrix_path = ("airline_ticket_purchase_corridor_v0_1", "core_domain_delegation_matrix")

    def matrix(report: dict) -> list[dict]:
        parent = report
        for key in matrix_path:
            parent = parent[key]
        return parent

    cases = (
        (
            lambda report: matrix(report).clear(),
            "core_domain_delegation_matrix_missing",
        ),
        (
            lambda report: matrix(report).pop(),
            "core_domain_delegation_row_count_mismatch",
        ),
        (
            lambda report: matrix(report)[0].update({"check_id": "missing"}),
            "core_domain_delegation_check_missing",
        ),
        (
            lambda report: matrix(report)[2].update(
                {"directly_delegated_to_core": True},
            ),
            "core_direct_delegation_count_mismatch",
        ),
        (
            lambda report: report["airline_ticket_purchase_corridor_v0_1"][
                "counter_table"
            ].update({"supplier_specific_core_fixture_used_count": 1}),
            "supplier_specific_core_fixture_detected",
        ),
        (
            lambda report: report["airline_ticket_purchase_corridor_v0_1"][
                "counter_table"
            ].update({"dishonest_field_mapping_count": 1}),
            "dishonest_field_mapping_detected",
        ),
        (
            lambda report: report["airline_ticket_purchase_corridor_v0_1"][
                "counter_table"
            ].update({"second_universal_authority_engine_created_count": 1}),
            "second_universal_authority_engine_detected",
        ),
        (
            lambda report: report["airline_ticket_purchase_corridor_v0_1"][
                "counter_table"
            ].update({"core_imports_airline_domain_count": 1}),
            "core_imports_airline_domain_detected",
        ),
    )

    for mutate, expected_error in cases:
        report = _collect_from_path(_write_source_json(tmp_path, mutate=mutate))

        assert report["final_status"] == story.FAIL_CLOSED
        assert expected_error in report["validation_errors"]


def test_airline_corridor_story_transaction_identity_mutation_fails_closed(
    tmp_path: Path,
) -> None:
    def mutate(report: dict) -> None:
        report["transaction_identity"]["airline_root_id"] = "root:wrong"

    report = _collect_from_path(_write_source_json(tmp_path, mutate=mutate))

    assert report["final_status"] == story.FAIL_CLOSED
    assert "transaction_identity_airline_root_mismatch" in report["validation_errors"]


def test_airline_corridor_story_phase_and_transition_derived_mutations_fail_closed(
    tmp_path: Path,
) -> None:
    cases = (
        (
            lambda report: report["airline_ticket_purchase_corridor_v0_1"][
                "phase_results"
            ][0].update({"core_corridor_guard_validated": False}),
            "corridor_phase_required_true_mismatch:airline_offer_hold_phase:core_corridor_guard_validated",
        ),
        (
            lambda report: report["airline_ticket_purchase_corridor_v0_1"][
                "phase_results"
            ][0].update({"domain_contracts_validated": False}),
            "corridor_phase_required_true_mismatch:airline_offer_hold_phase:domain_contracts_validated",
        ),
        (
            lambda report: report["airline_ticket_purchase_corridor_v0_1"][
                "transitions"
            ][0].update({"to_phase_id": "wrong_phase"}),
            "corridor_transition_adjacency_mismatch",
        ),
        (
            lambda report: report["airline_ticket_purchase_corridor_v0_1"][
                "transitions"
            ][0].update({"semantic_reasoning_restarted": True}),
            "corridor_transition_semantic_reasoning_restarted",
        ),
        (
            lambda report: report["airline_ticket_purchase_corridor_v0_1"][
                "transitions"
            ][0].update({"dependency_satisfied": False}),
            "corridor_transition_dependency_unsatisfied",
        ),
        (
            lambda report: report["airline_ticket_purchase_corridor_v0_1"][
                "transitions"
            ][0].update({"reason_codes": ["unexpected"]}),
            "corridor_transition_reason_codes_not_empty",
        ),
    )

    for mutate, expected_error in cases:
        report = _collect_from_path(_write_source_json(tmp_path, mutate=mutate))

        assert report["final_status"] == story.FAIL_CLOSED
        assert expected_error in report["validation_errors"]


def test_airline_corridor_story_counter_drift_fails_closed(tmp_path: Path) -> None:
    def mutate(report: dict) -> None:
        report["counter_table"]["airline_ticket_purchase_corridor_phase_count"] = 4

    report = _collect_from_path(_write_source_json(tmp_path, mutate=mutate))

    assert report["final_status"] == story.FAIL_CLOSED
    assert (
        "source_counter_mismatch:airline_ticket_purchase_corridor_phase_count"
        in report["validation_errors"]
    )


def test_airline_corridor_story_failed_source_content_not_normally_rendered(
    tmp_path: Path,
) -> None:
    marker = "TAMPERED SOURCE SHOULD NOT RENDER"

    def mutate(report: dict) -> None:
        report["travel_intent"]["user_goal"] = marker
        report["airline_ticket_purchase_corridor_binding_matrix"][1][
            "values_match"
        ] = False

    report = _collect_from_path(_write_source_json(tmp_path, mutate=mutate))
    rendered = story.render_human_airline_ticket_purchase_corridor_story_v01(report)

    assert report["final_status"] == story.FAIL_CLOSED
    assert marker not in rendered
    assert "[BINDING MATRIX — WHY THIS IS NOT A SECOND DEMO]" not in rendered
    assert "validation_errors:" in rendered


def test_airline_corridor_story_renderer_sections(tmp_path: Path) -> None:
    rendered = story.run_human_airline_ticket_purchase_corridor_story_v01(
        env={story.SOURCE_JSON_ENV: str(_write_source_json(tmp_path))},
    )

    for section in (
        "[HEDGEHOG OS — AIRLINE TICKET/PURCHASE CORRIDOR HUMAN STORY]",
        "[ONE-SCREEN SUMMARY]",
        "[BUSINESS SCENE]",
        "[ONE TRANSACTION / THREE ROOTS]",
        "[SEMANTIC PLANE → CONTRACT PLANE]",
        "[FIVE ROOT-CENTERED PHASES]",
        "[PHASE 1 — AIRLINE OFFER / HOLD]",
        "[PHASE 2 — CLIENT PURCHASE INTENT]",
        "[PHASE 3 — BANK PAYMENT AUTHORIZATION]",
        "[PHASE 4 — AIRLINE MOCK TICKET ISSUE]",
        "[PHASE 5 — CLIENT COMPLETION]",
        "[UNIVERSAL CORE VS AIRLINE DOMAIN]",
        "[IDENTITY AND LINEAGE]",
        "[WHO CREATES RECEIPTS]",
        "[BINDING MATRIX — WHY THIS IS NOT A SECOND DEMO]",
        "[EVIDENCE CROSSES ROOTS; AUTHORITY DOES NOT]",
        "[FAIL-CLOSED BOUNDARIES]",
        "[MOCK HAPPY PATH]",
        "[COUNTER TABLE]",
        "[NON-CLAIMS]",
        "[NEXT GATE]",
        "[FINAL STATUS]",
    ):
        assert section in rendered
    assert "mock PNR" in rendered
    assert "human_story_created_count: 1" in rendered
    assert "renderer_corridor_execution_count: 0" in rendered


def test_airline_corridor_story_source_boundary() -> None:
    source = Path(story.__file__).read_text(encoding="utf-8")

    for forbidden in (
        "run_tri_party_airline_ticket_purchase_mock_e2e_v01",
        "ticket_purchase_corridor_runtime_v01",
        "ticket_purchase_corridor_v01 as",
        "google.genai",
        "import requests",
        "import urllib",
        "import openai",
        "import subprocess",
        "import config",
        "provider adapter",
        "collect_tri_party_airline",
        "collect_airline_ticket_purchase_corridor",
        "create packets",
        "create receipts",
        "production " + "ready",
        "public auditor " + "ready",
    ):
        assert forbidden not in source
    for left, right in (
        ("Ledger", " implemented"),
        ("Crypto Artifact Seal", " implemented"),
        ("Sealed Trace Replay Verifier", " implemented"),
    ):
        assert left + right not in source
