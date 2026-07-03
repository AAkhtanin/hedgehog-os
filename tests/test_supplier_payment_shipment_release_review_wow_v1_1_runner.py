from __future__ import annotations

import json
from pathlib import Path

from demo import run_supplier_payment_shipment_release_review_wow_v1_1 as runner


REQUIRED_TOP_LEVEL_KEYS = (
    "run_id",
    "title",
    "short_name",
    "slice_id",
    "slice_status",
    "final_status",
    "wow_accepted",
    "wow_completion_claimed",
    "lane",
    "phase_results",
    "first_run",
    "corrected_evidence",
    "second_run",
    "human_approval",
    "mock_action_commit_packet",
    "mock_execution",
    "receipt",
    "inline_fixtures",
    "prompt_secret_scan",
    "action_counters",
    "non_claim_counters",
    "validation_errors",
    "audit_summary_path",
)

PHASE_IDS = (
    "phase_1_first_run_not_ready",
    "phase_2_corrected_evidence_drs_writeback_context_only",
    "phase_3_second_run_ready_for_human_reviewed_supplier_a_payment_approval",
    "phase_4_human_approval_creates_supplier_a_scoped_action_commit_packet",
    "phase_5_mock_bank_sandbox_executes_supplier_a_only",
)


def _summary() -> dict:
    return runner.run_supplier_payment_shipment_release_review_wow_v1_1()


def test_slice_a_runner_returns_pass_without_claiming_full_wow() -> None:
    summary = _summary()

    assert summary["final_status"] == "PASS"
    assert summary["slice_status"] == "PASS"
    assert summary["slice_id"] == (
        "supplier_payment_shipment_release_review_wow_v1_1_slice_a"
    )
    assert summary["wow_accepted"] is False
    assert summary["wow_completion_claimed"] is False


def test_slice_a_cli_prints_expected_markers(capsys) -> None:
    exit_code = runner.main([])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Supplier Payment / Shipment Release Review LIVE-DUAL-ROLE WOW v1.1" in output
    assert "HEDGEHOG OS — ZERO-TRUST SUPPLIER PAYMENT WOW v1.1" in output
    for phase_id in PHASE_IDS:
        assert phase_id in output
    assert "FINAL STATUS: PASS" in output
    assert "WOW ACCEPTED: false" in output


def test_slice_a_machine_summary_has_required_sections() -> None:
    summary = _summary()

    for key in REQUIRED_TOP_LEVEL_KEYS:
        assert key in summary
    for section in (
        "first_run",
        "corrected_evidence",
        "second_run",
        "human_approval",
        "mock_action_commit_packet",
        "mock_execution",
        "receipt",
    ):
        assert summary[section]["status"] == "NOT_EXECUTED_IN_SLICE_A"


def test_slice_a_phase_machine_declares_all_five_phases() -> None:
    phases = runner.build_phase_machine()

    assert tuple(phase["phase_id"] for phase in phases) == PHASE_IDS
    assert len(phases) == 5
    assert {phase["status"] for phase in phases} == {"SKELETON_DEFINED"}
    assert {phase["execution_status"] for phase in phases} == {
        "NOT_EXECUTED_IN_SLICE_A"
    }
    assert "PASS" not in {phase["status"] for phase in phases}


def test_slice_a_inline_fixtures_model_business_story_without_raw_secrets() -> None:
    fixtures = runner.build_inline_fixtures()
    fixture_text = json.dumps(fixtures, sort_keys=True)

    assert fixtures["supplier_A"]["supplier"] == "Adriatic Filters LLC"
    assert fixtures["supplier_A"]["product"] == "water_filter"
    assert fixtures["supplier_A"]["invoice"] == "INV-2042"
    assert fixtures["supplier_A"]["payment_permission_status"] == "not_granted"
    assert fixtures["supplier_B"]["supplier"] == "Balkan Pumps SHPK"
    assert fixtures["supplier_B"]["product"] == "pump_valve"
    assert fixtures["supplier_B"]["invoice"] == "INV-2043"
    assert fixtures["supplier_B"]["payment_permission_status"] == "not_granted"
    assert (
        fixtures["masked_payment_slot_supplier_A"]["payment_slot"]
        == "payment_slot_A_2042"
    )
    assert "beneficiary_iban" not in fixture_text
    assert "bank_token" not in fixture_text
    assert "FAKE-IBAN-AL-0000-2042-SECRET" not in fixture_text
    assert "sandbox_token_abc" not in fixture_text


def test_slice_a_deterministic_lane_has_no_network_gemini_or_provider_calls() -> None:
    counters = _summary()["action_counters"]

    assert counters["deterministic_lane_passed_count"] == 1
    assert counters["network_used_count"] == 0
    assert counters["gemini_called_count"] == 0
    assert counters["real_model_call_count"] == 0
    assert counters["live_model_call_count"] == 0
    assert counters["orchestrator_provider_call_count"] == 0
    assert counters["architect_provider_call_count"] == 0


def test_slice_a_no_actions_no_shipments_no_action_commit_packets() -> None:
    counters = _summary()["action_counters"]

    for key in (
        "payment_executed_count",
        "real_payment_executed_count",
        "real_bank_api_called_count",
        "real_supplier_api_called_count",
        "real_warehouse_api_called_count",
        "shipment_released_count",
        "mock_shipment_released_count",
        "connector_called_count",
        "real_world_effects_count",
        "action_commit_packet_created_count",
        "action_commit_packet_created_by_root_count",
        "action_commit_packet_created_by_llm_count",
        "mock_payment_executed_count",
    ):
        assert counters[key] == 0


def test_slice_a_preserves_shipment_release_review_only() -> None:
    correction = _summary()["canonical_correction"]

    assert correction["shipment_release_review_only"] is True
    assert correction["shipment_release_remains_held"] is True
    assert correction["real_shipment_release_claimed"] is False
    assert correction["mock_shipment_release_claimed"] is False
    assert correction["supplier_A_mock_payment_executed"] is False
    assert correction["supplier_B_payment_executed"] is False
    assert correction["shipment_release_executed"] is False


def test_slice_a_authority_invariants() -> None:
    invariants = _summary()["authority_invariants"]

    for value in invariants.values():
        assert value is True
    assert invariants["BSEP is not truth"] is True
    assert invariants["BSEP is not authority"] is True
    assert invariants["DRS hit is not authority"] is True
    assert invariants["AVF score is not authority"] is True
    assert (
        invariants["Mock receipt is evidence, not truth/action permission/final output"]
        is True
    )
    assert invariants["Root remains final authority"] is True


def test_slice_a_legacy_api_vs_hedgehog_sentence_present() -> None:
    report = runner.render_report(_summary())

    assert "APIs return facts." in report
    assert "Hedgehog decides what those facts are allowed to become." in report


def test_slice_a_summary_is_json_serializable() -> None:
    json.dumps(_summary(), sort_keys=True)


def test_slice_a_runner_source_has_no_provider_network_imports_or_raw_secret_literals() -> None:
    source = Path(runner.__file__).read_text(encoding="utf-8")

    for forbidden in (
        "google",
        "genai",
        "requests",
        "httpx",
        "urllib",
        "socket",
        "provider_adapter",
        "run_live_unknown_request",
        "HEDGEHOG_UNKNOWN_REQUEST_LIVE_GEMINI",
        "GOOGLE_API_KEY",
        "GEMINI_API_KEY",
        "FAKE-IBAN-AL-0000-2042-SECRET",
        "sandbox_token_abc",
        "beneficiary_iban",
        "bank_token",
        "call_robot_api",
        "unlock_door",
        "dispatch_robot_now",
        "enter_all_rooms_now",
    ):
        assert forbidden not in source
