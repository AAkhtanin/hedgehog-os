from __future__ import annotations

import json
from pathlib import Path

from demo import run_supplier_payment_shipment_release_review_wow_v1_1 as runner


SECRET_MARKERS = (
    "FAKE-IBAN-AL-0000-2042-SECRET",
    "sandbox_token_abc",
    "beneficiary_iban",
    "bank_token",
    "GOOGLE_API_KEY",
    "GEMINI_API_KEY",
)


def _summary() -> dict:
    return runner.run_supplier_payment_shipment_release_review_wow_v1_1()


def test_slice_d_runner_returns_pass_without_claiming_full_wow() -> None:
    summary = _summary()

    assert summary["final_status"] == "PASS"
    assert summary["slice_status"] == "PASS"
    assert summary["slice_id"] == (
        "supplier_payment_shipment_release_review_wow_v1_1_slice_d"
    )
    assert summary["wow_accepted"] is False
    assert summary["wow_completion_claimed"] is False


def test_slice_d_preserves_prior_slice_business_outcomes() -> None:
    summary = _summary()

    assert summary["first_run"]["root_final_decision"] == "NOT_READY"
    assert summary["corrected_evidence"]["corrected_evidence_is_authority_count"] == 0
    assert summary["corrected_evidence"]["prior_root_final_mutated_count"] == 0
    assert "READY_FOR_HUMAN_REVIEWED_SUPPLIER_A_PAYMENT_APPROVAL" in summary[
        "second_run"
    ]["root_outcome"]
    assert "SHIPMENT_RELEASE_STILL_HELD_OR_SEPARATE_APPROVAL_REQUIRED" in summary[
        "second_run"
    ]["root_outcome"]
    assert "SUPPLIER_B_REMAINS_BLOCKED" in summary["second_run"]["root_outcome"]
    assert summary["second_run"]["supplier_B_payment_blocked_count"] == 1
    assert summary["second_run"]["shipment_release_still_held_count"] == 1
    assert summary["canonical_correction"]["shipment_release_remains_held"] is True


def test_slice_d_human_approval_is_scoped_supplier_a_only() -> None:
    summary = _summary()
    approval = summary["human_approval"]
    counters = summary["action_counters"]

    assert approval["status"] == "EXECUTED_IN_SLICE_D"
    assert approval["approval_present"] is True
    assert approval["permission_scope"] == "supplier_A_only"
    assert approval["supplier_id"] == "supplier_A"
    assert approval["payment_slot"] == "payment_slot_A_2042"
    assert approval["supplier_B_in_scope"] is False
    assert approval["shipment_release_in_scope"] is False
    assert counters["human_approval_present_count"] == 1
    assert counters["human_approval_scope_supplier_A_only_count"] == 1
    assert counters["human_approval_scope_supplier_B_count"] == 0
    assert counters["human_approval_scope_shipment_release_count"] == 0
    assert counters["human_approval_is_broad_authority_count"] == 0
    assert counters["human_approval_created_final_output_count"] == 0


def test_slice_d_root_creates_valid_mock_action_commit_packet() -> None:
    summary = _summary()
    packet_section = summary["mock_action_commit_packet"]
    counters = summary["action_counters"]

    assert packet_section["status"] == "EXECUTED_IN_SLICE_D"
    assert counters["action_commit_packet_created_count"] == 1
    assert counters["action_commit_packet_created_by_root_count"] == 1
    assert counters["action_commit_packet_created_by_llm_count"] == 0
    assert counters["action_commit_packet_validated_count"] == 1
    assert packet_section["packet_type"] == "mock_action_commit_packet"
    assert packet_section["created_by"] == "root_mock_approval_gate"
    assert packet_section["mock_only"] is True
    assert packet_section["real_world_effects_allowed"] is False
    assert packet_section["business_scope"] == "supplier_A_only"
    assert packet_section["supplier_B_included"] is False
    assert packet_section["shipment_release_included"] is False
    assert packet_section["validation_accepted"] is True
    assert packet_section["final_output_claimed"] is False
    assert packet_section["executes_itself"] is False
    assert counters["action_commit_packet_supplier_A_only_count"] == 1
    assert counters["action_commit_packet_contains_supplier_B_count"] == 0
    assert counters["action_commit_packet_contains_shipment_release_count"] == 0
    assert counters["action_commit_packet_is_final_output_count"] == 0
    assert counters["action_commit_packet_executes_itself_count"] == 0


def test_slice_d_action_commit_packet_fail_closed_probes() -> None:
    summary = _summary()
    probes = summary["action_commit_packet_fail_closed_probes"]
    counters = summary["action_counters"]

    assert probes["non_root_action_commit_packet_rejected"] is True
    assert probes["supplier_B_scope_action_commit_packet_rejected"] is True
    assert probes["shipment_release_scope_action_commit_packet_rejected"] is True
    assert probes["real_world_effects_allowed_action_commit_packet_rejected"] is True
    assert probes["missing_human_approval_action_commit_packet_rejected"] is True
    assert counters["non_root_action_commit_packet_rejected_count"] == 1
    assert counters["supplier_B_scope_action_commit_packet_rejected_count"] == 1
    assert counters["shipment_release_scope_action_commit_packet_rejected_count"] == 1
    assert counters["real_world_effects_allowed_action_commit_packet_rejected_count"] == 1
    assert counters["missing_human_approval_action_commit_packet_rejected_count"] == 1


def test_slice_d_mock_bank_sandbox_executes_supplier_a_only() -> None:
    summary = _summary()
    execution = summary["mock_execution"]
    counters = summary["action_counters"]

    assert execution["status"] == "EXECUTED_IN_SLICE_D"
    assert counters["mock_connector_sandbox_invoked_count"] == 1
    assert counters["mock_bank_adapter_invoked_count"] == 1
    assert counters["mock_payment_executed_count"] == 1
    assert execution["supplier_id"] == "supplier_A"
    assert execution["invoice_id"] == "INV-2042"
    assert execution["payment_slot"] == "payment_slot_A_2042"
    assert counters["supplier_B_payment_executed_count"] == 0
    assert counters["real_payment_executed_count"] == 0
    assert counters["real_bank_api_called_count"] == 0
    assert counters["real_supplier_api_called_count"] == 0
    assert counters["real_warehouse_api_called_count"] == 0
    assert counters["real_world_effects_count"] == 0


def test_slice_d_receipt_is_evidence_only() -> None:
    summary = _summary()
    receipt = summary["receipt"]
    counters = summary["action_counters"]

    assert receipt["status"] == "EXECUTED_IN_SLICE_D"
    assert receipt["receipt_created"] is True
    assert receipt["receipt_type"] == "mock_bank_receipt"
    assert receipt["receipt_scope"] == "supplier_A_only"
    assert counters["mock_bank_receipt_created_count"] == 1
    assert counters["receipt_validated_count"] == 1
    assert counters["receipt_is_evidence_count"] == 1
    assert counters["receipt_is_truth_count"] == 0
    assert counters["receipt_is_action_permission_count"] == 0
    assert counters["receipt_is_final_output_count"] == 0
    assert counters["receipt_releases_shipment_count"] == 0
    assert counters["receipt_contains_supplier_B_count"] == 0
    assert receipt["receipt_is_evidence"] is True
    assert receipt["receipt_is_truth"] is False
    assert receipt["receipt_is_action_permission"] is False
    assert receipt["receipt_is_final_output"] is False
    assert receipt["receipt_releases_shipment"] is False


def test_slice_d_supplier_b_remains_blocked() -> None:
    summary = _summary()
    supplier_b = summary["second_run"]["supplier_B_status"]

    assert summary["action_counters"]["supplier_B_payment_blocked_count"] == 1
    assert summary["action_counters"]["supplier_B_payment_executed_count"] == 0
    assert supplier_b["invoice_B"] == "mismatch_with_PO"
    assert supplier_b["supplier_B_delivery"] == "delayed"
    assert summary["human_approval"]["supplier_B_in_scope"] is False
    assert summary["mock_action_commit_packet"]["supplier_B_included"] is False
    assert summary["receipt"]["supplier_B_included"] is False


def test_slice_d_shipment_release_still_held() -> None:
    summary = _summary()
    counters = summary["action_counters"]

    assert counters["shipment_release_still_held_count"] == 1
    assert counters["shipment_released_count"] == 0
    assert counters["mock_shipment_released_count"] == 0
    assert summary["canonical_correction"]["shipment_release_executed"] is False
    assert counters["receipt_releases_shipment_count"] == 0
    assert summary["mock_action_commit_packet"]["shipment_release_included"] is False


def test_slice_d_no_network_gemini_provider_calls() -> None:
    counters = _summary()["action_counters"]

    assert counters["deterministic_lane_passed_count"] == 1
    assert counters["network_used_count"] == 0
    assert counters["gemini_called_count"] == 0
    assert counters["real_model_call_count"] == 0
    assert counters["live_model_call_count"] == 0
    assert counters["orchestrator_provider_call_count"] == 0
    assert counters["architect_provider_call_count"] == 0


def test_slice_d_no_real_actions_or_connectors() -> None:
    counters = _summary()["action_counters"]

    assert counters["real_payment_executed_count"] == 0
    assert counters["real_bank_api_called_count"] == 0
    assert counters["real_supplier_api_called_count"] == 0
    assert counters["real_warehouse_api_called_count"] == 0
    assert counters["shipment_released_count"] == 0
    assert counters["mock_shipment_released_count"] == 0
    assert counters["connector_called_count"] == 0
    assert counters["real_world_effects_count"] == 0
    assert counters["production_action_commit_packet_claimed_count"] == 0
    assert counters["production_permission_ux_claimed_count"] == 0


def test_slice_d_no_raw_secret_literals_in_summary_report_or_source() -> None:
    summary = _summary()
    report = runner.render_report(summary)
    source = Path(runner.__file__).read_text(encoding="utf-8")

    for text in (json.dumps(summary, sort_keys=True), report, source):
        for marker in SECRET_MARKERS:
            assert marker not in text
    for forbidden in (
        "google",
        "genai",
        "requests",
        "httpx",
        "urllib",
        "socket",
        "provider_adapter",
        "run_live_unknown_request",
    ):
        assert forbidden not in source


def test_slice_d_report_contains_mock_action_boundary() -> None:
    report = runner.render_report(_summary())

    assert "Slice D" in report
    assert "scoped human approval" in report
    assert "Root-created mock ActionCommitPacket" in report
    assert "MockBankSandbox" in report
    assert "MockConnectorSandbox" in report
    assert "supplier_A_only" in report
    assert "mock_bank_receipt" in report
    assert "receipt_is_evidence: true" in report
    assert "Supplier B remains blocked" in report
    assert "Shipment release remains held" in report
    assert "FINAL STATUS: PASS" in report
    assert "WOW ACCEPTED: false" in report


def test_slice_d_summary_is_json_serializable() -> None:
    json.dumps(_summary(), sort_keys=True)
