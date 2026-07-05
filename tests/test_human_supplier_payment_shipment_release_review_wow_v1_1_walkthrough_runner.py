from __future__ import annotations

import json
from pathlib import Path

from demo import (
    run_human_supplier_payment_shipment_release_review_wow_v1_1_walkthrough as runner,
)


SECRET_MARKERS = (
    "FAKE-IBAN-AL-0000-2042-SECRET",
    "sandbox_token_abc",
    "beneficiary_iban",
    "bank_token",
    "GOOGLE_API_KEY",
    "GEMINI_API_KEY",
)


def _summary() -> dict:
    return runner.build_human_walkthrough_summary()


def _report(summary: dict | None = None) -> str:
    return runner.render_human_walkthrough(summary or _summary())


def test_slice_e_human_walkthrough_returns_pass_without_claiming_full_wow() -> None:
    summary = _summary()

    assert summary["walkthrough_status"] == "PASS"
    assert summary["final_status"] == "PASS"
    assert summary["source_slice_id"] == (
        "supplier_payment_shipment_release_review_wow_v1_1_slice_d"
    )
    assert summary["wow_accepted"] is False
    assert summary["wow_completion_claimed"] is False
    assert summary["production_ready_claimed"] is False
    assert summary["public_auditor_ready_claimed"] is False
    assert summary["ready_for_audit_docs_sync"] is True


def test_slice_e_observes_slice_d_summary_without_new_execution_boundary() -> None:
    counters = _summary()["walkthrough_counters"]

    assert counters["source_slice_d_summary_observed_count"] == 1
    assert counters["walkthrough_created_action_commit_packet_count"] == 0
    assert counters["walkthrough_invoked_mock_bank_count"] == 0
    assert counters["walkthrough_created_receipt_count"] == 0
    assert counters["underlying_action_commit_packet_created_count"] == 1
    assert counters["underlying_mock_bank_receipt_created_count"] == 1


def test_slice_e_first_run_and_second_run_story_preserved() -> None:
    report = _report()

    assert "ACT 1 — Dirty business request" in report
    assert "ACT 2 — First run Root Final: NOT_READY" in report
    assert "water_filter short_by_2" in report
    assert "insurance certificate expired" in report
    assert "READY_FOR_HUMAN_REVIEWED_SUPPLIER_A_PAYMENT_APPROVAL" in report
    assert "SUPPLIER_B_REMAINS_BLOCKED" in report
    assert "SHIPMENT_RELEASE_STILL_HELD_OR_SEPARATE_APPROVAL_REQUIRED" in report


def test_slice_e_human_approval_story_is_scoped_supplier_a_only() -> None:
    summary = _summary()
    report = _report(summary)
    counters = summary["walkthrough_counters"]

    assert "Scoped human approval" in report
    assert "supplier_A_only" in report
    assert "Supplier B remains blocked" in report
    assert "shipment release remains held" in report
    assert counters["human_approval_scope_supplier_B_count"] == 0
    assert counters["human_approval_scope_shipment_release_count"] == 0
    assert counters["human_approval_is_broad_authority_count"] == 0


def test_slice_e_root_created_mock_action_commit_packet_story() -> None:
    summary = _summary()
    report = _report(summary)
    counters = summary["walkthrough_counters"]

    assert "Root-created mock ActionCommitPacket" in report
    assert "root_mock_approval_gate" in report
    assert "mock_action_commit_packet" in report
    assert "mock_only" in report
    assert "ActionCommitPacket is not FinalOutput" in report
    assert "ActionCommitPacket does not execute itself" in report
    assert counters["underlying_action_commit_packet_created_by_root_count"] == 1
    assert counters["underlying_action_commit_packet_created_by_llm_count"] == 0


def test_slice_e_mock_bank_receipt_story_is_evidence_only() -> None:
    summary = _summary()
    report = _report(summary)
    counters = summary["walkthrough_counters"]

    assert "MockBankSandbox" in report
    assert "Supplier A-only fake bank adapter path" in report
    assert "mock bank receipt" in report
    assert "receipt is evidence only" in report
    assert "receipt is not truth" in report
    assert "receipt is not action permission" in report
    assert "receipt is not FinalOutput" in report
    assert "mock payment receipt does not release shipment" in report
    assert counters["receipt_releases_shipment_count"] == 0


def test_slice_e_supplier_b_and_shipment_boundaries() -> None:
    summary = _summary()
    report = _report(summary)
    counters = summary["walkthrough_counters"]

    assert counters["supplier_B_remains_blocked_count"] == 1
    assert counters["shipment_release_remains_held_count"] == 1
    assert counters["underlying_supplier_B_payment_executed_count"] == 0
    assert counters["underlying_shipment_released_count"] == 0
    assert counters["underlying_mock_shipment_released_count"] == 0
    assert "Supplier B remains blocked" in report
    assert "shipment release remains held" in report


def test_slice_e_no_network_gemini_provider_calls() -> None:
    counters = _summary()["walkthrough_counters"]

    assert counters["network_used_count"] == 0
    assert counters["gemini_called_count"] == 0
    assert counters["real_model_call_count"] == 0
    assert counters["live_model_call_count"] == 0
    assert counters["orchestrator_provider_call_count"] == 0
    assert counters["architect_provider_call_count"] == 0


def test_slice_e_non_claims_are_visible() -> None:
    summary = _summary()
    report = _report(summary)
    counters = summary["walkthrough_counters"]

    assert "not production" in report
    assert "not real bank integration" in report
    assert "not real supplier API" in report
    assert "not real warehouse connector" in report
    assert "not real payment" in report
    assert "not real shipment release" in report
    assert "not production ActionCommitPacket" in report
    assert "not public auditor final package" in report
    assert counters["production_ready_claimed_count"] == 0
    assert counters["public_auditor_ready_claimed_count"] == 0


def test_slice_e_terminology_does_not_overclaim_generic_sandbox() -> None:
    summary = _summary()
    report = _report(summary)
    counters = summary["walkthrough_counters"]

    assert "MockBankSandbox" in report
    assert "inside the mock connector boundary" in report
    assert "not full generic MockConnectorSandbox three-adapter execution" in report
    assert "full generic MockConnectorSandbox executed" not in report
    assert counters["full_generic_mock_connector_sandbox_execution_claimed_count"] == 0
    assert counters["supplier_A_bank_only_mock_path_claimed_count"] == 1


def test_slice_e_report_is_human_readable_not_json_wall() -> None:
    report = _report()

    assert "ACT 1" in report
    assert "ACT 8" in report
    assert "The business process is visible, but sovereignty never leaves Root." in report
    assert "APIs return facts." in report
    assert "Hedgehog decides what those facts are allowed to become." in report
    assert "FINAL STATUS: PASS" in report
    assert "WOW ACCEPTED: false" in report
    assert not report.startswith("{")
    assert '"action_counters"' not in report


def test_slice_e_no_raw_secret_literals_in_summary_report_or_source() -> None:
    summary = _summary()
    report = _report(summary)
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


def test_slice_e_cli_prints_human_walkthrough(capsys) -> None:
    assert runner.main([]) == 0

    output = capsys.readouterr().out
    assert "Supplier Payment / Shipment Release Review LIVE-DUAL-ROLE WOW v1.1" in output
    assert "Human Walkthrough — Slice E" in output
    assert "FINAL STATUS: PASS" in output
    assert "WOW ACCEPTED: false" in output
