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
    "bsep_summary",
    "drs_context",
    "candidate_vectors",
    "avf_ranking",
    "root_first_run",
    "prompt_secret_scan",
    "action_counters",
    "non_claim_counters",
    "validation_errors",
    "audit_summary_path",
    "authority_invariants",
    "legacy_api_vs_hedgehog",
)

PHASE_IDS = (
    "phase_1_first_run_not_ready",
    "phase_2_corrected_evidence_drs_writeback_context_only",
    "phase_3_second_run_ready_for_human_reviewed_supplier_a_payment_approval",
    "phase_4_human_approval_creates_supplier_a_scoped_action_commit_packet",
    "phase_5_mock_bank_sandbox_executes_supplier_a_only",
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
    return runner.run_supplier_payment_shipment_release_review_wow_v1_1()


def test_slice_b_runner_returns_pass_without_claiming_full_wow() -> None:
    summary = _summary()

    assert summary["final_status"] == "PASS"
    assert summary["slice_status"] == "PASS"
    assert summary["slice_id"] == (
        "supplier_payment_shipment_release_review_wow_v1_1_slice_b"
    )
    assert summary["wow_accepted"] is False
    assert summary["wow_completion_claimed"] is False


def test_slice_b_cli_prints_expected_markers(capsys) -> None:
    exit_code = runner.main([])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Supplier Payment / Shipment Release Review LIVE-DUAL-ROLE WOW v1.1" in output
    assert "HEDGEHOG OS — ZERO-TRUST SUPPLIER PAYMENT WOW v1.1" in output
    for phase_id in PHASE_IDS:
        assert phase_id in output
    assert "BSEP summary" in output
    assert "Root Final: NOT_READY" in output
    assert "FINAL STATUS: PASS" in output
    assert "WOW ACCEPTED: false" in output


def test_slice_b_bsep_created_and_validated() -> None:
    summary = _summary()
    counters = summary["action_counters"]
    bsep = summary["bsep_summary"]
    bsep_text = json.dumps(bsep, sort_keys=True)

    assert counters["bsep_created_count"] == 1
    assert counters["bsep_validated_count"] == 1
    assert bsep["packet_type"] == "BoundedSemanticEvidencePacket"
    assert bsep["validation_accepted"] is True
    assert bsep["validation"]["accepted"] is True
    assert bsep["truth_claimed"] is False
    assert bsep["authority_claimed"] is False
    assert bsep["action_permission_claimed"] is False
    assert bsep["final_output_claimed"] is False
    assert counters["bsep_contains_raw_user_text_count"] == 0
    assert counters["bsep_contains_raw_gemini_text_count"] == 0
    assert counters["bsep_truth_claimed_count"] == 0
    assert counters["bsep_authority_claimed_count"] == 0
    assert counters["bsep_action_permission_claimed_count"] == 0
    assert counters["bsep_final_output_claimed_count"] == 0
    for marker in SECRET_MARKERS:
        assert marker not in bsep_text


def test_slice_b_drs_lookup_is_context_only() -> None:
    drs = _summary()["drs_context"]

    assert drs["drs_candidates_found"] is True
    assert drs["drs_candidates_found_count"] == 1
    assert drs["drs_hit_is_authority"] is False
    assert drs["direct_reuse_allowed"] is False
    assert drs["prior_successful_payment_trace_cannot_authorize_current_payment"] is True
    assert drs["drs_prior_success_used_as_permission_count"] == 0
    assert drs["drs_writeback_count"] == 0
    assert drs["prior_root_final_mutated"] is False


def test_slice_b_candidate_vectors_are_advisory_only() -> None:
    candidates = _summary()["candidate_vectors"]
    candidate_ids = {candidate["candidate_id"] for candidate in candidates}

    assert len(candidates) == 7
    for candidate in candidates:
        assert candidate["candidate_only"] is True
        assert candidate["truth_claimed"] is False
        assert candidate["authority_claimed"] is False
        assert candidate["action_permission_claimed"] is False
    assert "release_all_and_pay_all" in candidate_ids
    assert "prepare_payment_forms_but_do_not_execute" in candidate_ids
    assert "block_supplier_B_due_invoice_mismatch" in candidate_ids


def test_slice_b_avf_ranking_blocks_unsafe_paths() -> None:
    avf = _summary()["avf_ranking"]
    ranked_by_id = {
        candidate["candidate_id"]: candidate for candidate in avf["ranked_candidates"]
    }

    assert avf["avf_scored"] is True
    assert avf["avf_scored_count"] == 1
    assert ranked_by_id["release_all_and_pay_all"]["avf_status"] == "hard_masked"
    assert (
        ranked_by_id["block_supplier_B_due_invoice_mismatch"]["avf_status"]
        == "blocked_or_penalized"
    )
    assert (
        ranked_by_id["prepare_payment_forms_but_do_not_execute"]["avf_status"]
        == "ranked_safe"
    )
    assert ranked_by_id["hold_release_request_documents"]["avf_status"] == "ranked_safe"
    assert (
        ranked_by_id["ask_human_approval_after_corrections"]["avf_status"]
        == "ranked_safe"
    )
    assert avf["avf_score_is_authority_count"] == 0
    assert avf["top_ranked_candidate_is_permission_count"] == 0
    assert avf["high_score_did_not_create_permission_count"] == 1


def test_slice_b_first_run_root_final_not_ready() -> None:
    summary = _summary()
    first_run = summary["first_run"]
    counters = summary["action_counters"]

    assert first_run["status"] == "EXECUTED_IN_SLICE_B"
    assert first_run["root_final_decision"] == "NOT_READY"
    assert first_run["root_final_created"] is True
    for reason in (
        "water_filter short_by_2",
        "insurance certificate expired",
        "supplier_B invoice mismatch",
        "supplier_B delivery delayed",
        "payment forms require human approval",
    ):
        assert reason in first_run["root_reasons"]
    for artifact in (
        "supplier_A_restock_request_draft",
        "bank_A_payment_form_masked",
        "legal_update_request",
        "supplier_B_review_request",
    ):
        assert artifact in first_run["prepared_artifacts"]
    assert counters["root_final_created_count"] == 1
    assert counters["root_decision_not_ready_count"] == 1


def test_slice_b_future_phases_not_executed() -> None:
    summary = _summary()

    for section in (
        "corrected_evidence",
        "second_run",
        "human_approval",
        "mock_action_commit_packet",
        "mock_execution",
        "receipt",
    ):
        assert summary[section]["status"] == "NOT_EXECUTED_IN_SLICE_B"
    assert summary["corrected_evidence"]["corrected_evidence_drs_writeback_count"] == 0
    assert summary["second_run"]["ready_for_human_supplier_a_payment_approval_count"] == 0
    assert summary["human_approval"]["human_approval_present_count"] == 0
    assert summary["mock_action_commit_packet"]["action_commit_packet_created_count"] == 0
    assert summary["mock_execution"]["mock_payment_executed_count"] == 0
    assert summary["receipt"]["mock_bank_receipt_created_count"] == 0


def test_slice_b_no_network_gemini_provider_calls() -> None:
    counters = _summary()["action_counters"]

    assert counters["deterministic_lane_passed_count"] == 1
    assert counters["network_used_count"] == 0
    assert counters["gemini_called_count"] == 0
    assert counters["real_model_call_count"] == 0
    assert counters["live_model_call_count"] == 0
    assert counters["orchestrator_provider_call_count"] == 0
    assert counters["architect_provider_call_count"] == 0


def test_slice_b_no_actions_no_shipments_no_action_commit_packets() -> None:
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
        "mock_connector_sandbox_invoked_count",
        "mock_bank_adapter_invoked_count",
        "mock_payment_executed_count",
        "mock_bank_receipt_created_count",
    ):
        assert counters[key] == 0


def test_slice_b_summary_sections_and_json_serializable() -> None:
    summary = _summary()

    for key in REQUIRED_TOP_LEVEL_KEYS:
        assert key in summary
    json.dumps(summary, sort_keys=True)


def test_slice_b_report_contains_bsep_drs_avf_root_not_ready() -> None:
    report = runner.render_report(_summary())

    assert "BSEP summary" in report
    assert "DRS context-only summary" in report
    assert "CandidateVector summary" in report
    assert "AVF ranking summary" in report
    assert "Root Final: NOT_READY" in report
    assert "supplier_A_restock_request_draft" in report
    assert "bank_A_payment_form_masked" in report
    assert "legal_update_request" in report
    assert "supplier_B_review_request" in report
    assert "FINAL STATUS: PASS" in report
    assert "WOW ACCEPTED: false" in report


def test_slice_b_preserves_shipment_review_only() -> None:
    correction = _summary()["canonical_correction"]

    assert correction["shipment_release_review_only"] is True
    assert correction["shipment_release_remains_held"] is True
    assert correction["real_shipment_release_claimed"] is False
    assert correction["mock_shipment_release_claimed"] is False
    assert correction["only_future_allowed_mock_execution_crossing"] == (
        "supplier_A_mock_payment_after_root_and_scoped_human_approval"
    )
    assert correction["supplier_A_mock_payment_executed"] is False
    assert correction["supplier_B_payment_executed"] is False
    assert correction["shipment_release_executed"] is False


def test_slice_b_authority_invariants() -> None:
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


def test_slice_b_legacy_api_vs_hedgehog_sentence_present() -> None:
    report = runner.render_report(_summary())

    assert "APIs return facts." in report
    assert "Hedgehog decides what those facts are allowed to become." in report


def test_slice_b_no_raw_secret_literals_in_summary_report_or_source() -> None:
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
        "HEDGEHOG_UNKNOWN_REQUEST_LIVE_GEMINI",
        "call_robot_api",
        "unlock_door",
        "dispatch_robot_now",
        "enter_all_rooms_now",
    ):
        assert forbidden not in source
