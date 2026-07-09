from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import hedgehog.non_action_reuse_positive_control as reuse


def _report() -> reuse.NonActionDirectReuseReportV01:
    return reuse.build_non_action_direct_reuse_positive_control_report_v01()


def _decision(
    report: reuse.NonActionDirectReuseReportV01,
    candidate_class: str,
) -> reuse.NonActionReuseDecisionV01:
    for decision in report.decisions:
        if decision.candidate_class == candidate_class:
            return decision
    raise AssertionError(f"missing decision: {candidate_class}")


def test_positive_informational_direct_reuse_allowed_only_for_information() -> None:
    report = _report()
    positive = _decision(
        report,
        reuse.CANDIDATE_INFORMATIONAL_POLICY_SUMMARY_DIRECT_REUSE,
    )

    assert report.final_status == reuse.STATUS_PASS
    assert report.scenarios_total == 6
    assert report.scenarios_passed == 6
    assert report.counters["direct_reuse_allowed_count"] == 1
    assert report.counters["non_action_direct_reuse_allowed_count"] == 1
    assert report.positive_control["direct_reuse_allowed"] is True
    assert positive.direct_reuse_allowed is True
    assert positive.direct_reuse_allowed_for_information_only is True
    assert report.positive_control["action_intent"] is False
    assert positive.root_shortcut_allowed is True
    assert positive.root_final_from_reuse_created is True
    assert reuse.REASON_OLD_MEMORY_CAN_HELP_BUT_CANNOT_ACT in positive.reason_codes
    assert reuse.REASON_INFORMATIONAL_ANSWER_ONLY in positive.reason_codes


def test_positive_reuse_skips_heavy_pipeline_without_action() -> None:
    report = _report()
    positive = _decision(
        report,
        reuse.CANDIDATE_INFORMATIONAL_POLICY_SUMMARY_DIRECT_REUSE,
    )

    assert positive.architect_skipped is True
    assert positive.executor_skipped is True
    assert positive.heavy_pipeline_skipped is True
    assert report.counters[
        "architect_skipped_for_safe_informational_reuse_count"
    ] == 1
    assert report.counters[
        "executor_skipped_for_safe_informational_reuse_count"
    ] == 1
    assert report.counters["heavy_pipeline_skipped_count"] == 1
    assert report.counters["provider_called_count"] == 0
    assert report.counters["network_used_count"] == 0
    assert report.counters["gemini_called_count"] == 0


def test_root_creates_informational_reuse_artifact() -> None:
    report = _report()

    assert len(report.informational_artifacts) == 1
    artifact = report.informational_artifacts[0]
    assert artifact.created_by == "root"
    assert artifact.root_created is True
    assert artifact.direct_reuse_allowed_for_information_only is True
    assert artifact.final_output_created is False
    assert artifact.action_permission_granted is False
    assert artifact.payment_permission_created is False
    assert artifact.shipment_permission_created is False
    assert artifact.ticket_permission_created is False
    assert artifact.action_commit_packet_created is False
    assert artifact.receipt_created is False
    assert artifact.payment_executed is False
    assert artifact.shipment_released is False
    assert artifact.ticket_issued is False
    assert artifact.real_world_effects_count == 0


def test_payment_request_blocks_direct_reuse() -> None:
    report = _report()
    decision = _decision(
        report,
        reuse.CANDIDATE_SAME_POLICY_RECORD_AS_PAYMENT_PERMISSION,
    )

    assert report.negative_controls["payment_direct_reuse_allowed"] is False
    assert decision.direct_reuse_allowed is False
    assert decision.action_reuse_blocked is True
    assert decision.payment_permission_created is False
    assert decision.action_commit_packet_created is False
    assert decision.receipt_created is False
    assert reuse.REASON_ACTION_REUSE_BLOCKED in decision.reason_codes
    assert reuse.REASON_NO_PAYMENT_PERMISSION in decision.reason_codes


def test_shipment_request_blocks_direct_reuse() -> None:
    report = _report()
    decision = _decision(
        report,
        reuse.CANDIDATE_SAME_POLICY_RECORD_AS_SHIPMENT_RELEASE,
    )

    assert report.negative_controls["shipment_direct_reuse_allowed"] is False
    assert decision.direct_reuse_allowed is False
    assert decision.action_reuse_blocked is True
    assert decision.shipment_permission_created is False
    assert decision.shipment_released is False
    assert reuse.REASON_NO_SHIPMENT_PERMISSION in decision.reason_codes


def test_ticket_request_blocks_direct_reuse() -> None:
    report = _report()
    decision = _decision(
        report,
        reuse.CANDIDATE_SAME_POLICY_RECORD_AS_TICKET_PURCHASE,
    )

    assert report.negative_controls["ticket_purchase_direct_reuse_allowed"] is False
    assert decision.direct_reuse_allowed is False
    assert decision.action_reuse_blocked is True
    assert decision.ticket_permission_created is False
    assert decision.ticket_issued is False
    assert reuse.REASON_NO_TICKET_PERMISSION in decision.reason_codes


def test_action_commit_packet_and_receipt_creation_requests_blocked() -> None:
    record = reuse.build_fresh_root_approved_policy_summary_record_v01()
    requests = {
        request.request_id: request
        for request in reuse.build_action_like_reuse_requests_v01()
    }

    packet_decision = reuse.evaluate_non_action_reuse_decision_v01(
        "scenario:packet_creation_direct_check",
        "same_policy_record_as_action_commit_packet_creation",
        record,
        requests["request:action_commit_packet"],
    )
    receipt_decision = reuse.evaluate_non_action_reuse_decision_v01(
        "scenario:receipt_creation_direct_check",
        "same_policy_record_as_receipt_creation",
        record,
        requests["request:receipt_creation"],
    )

    assert packet_decision.direct_reuse_allowed is False
    assert packet_decision.action_reuse_blocked is True
    assert packet_decision.action_commit_packet_created is False
    assert receipt_decision.direct_reuse_allowed is False
    assert receipt_decision.action_reuse_blocked is True
    assert receipt_decision.receipt_created is False
    assert _report().counters["action_commit_packet_created_count"] == 0
    assert _report().counters["receipt_created_count"] == 0


def test_stale_policy_summary_is_context_only_or_rerun_required() -> None:
    report = _report()
    decision = _decision(
        report,
        reuse.CANDIDATE_STALE_POLICY_SUMMARY_CONTEXT_ONLY,
    )

    assert decision.decision_class in (
        reuse.DECISION_CONTEXT_ONLY,
        reuse.DECISION_RERUN_REQUIRED,
    )
    assert decision.direct_reuse_allowed is False
    assert decision.root_shortcut_allowed is False
    assert decision.action_permission_granted is False
    assert reuse.REASON_TEMPORAL_HARD_GATE_FAILED in decision.reason_codes


def test_high_score_without_root_shortcut_does_not_authorize() -> None:
    report = _report()
    decision = _decision(
        report,
        reuse.CANDIDATE_HIGH_SCORE_WITHOUT_ROOT_SHORTCUT,
    )

    assert decision.direct_reuse_allowed is False
    assert decision.root_shortcut_allowed is False
    assert decision.reuse_score_is_authority is False
    assert decision.semantic_similarity_is_authority is False
    assert reuse.REASON_REUSE_SCORE_NOT_AUTHORITY in decision.reason_codes
    assert reuse.REASON_SEMANTIC_SIMILARITY_NOT_AUTHORITY in decision.reason_codes


def test_quarantine_near_policy_summary_blocks_direct_reuse() -> None:
    record = replace(
        reuse.build_fresh_root_approved_policy_summary_record_v01(),
        quarantine_ok=False,
        record_id="non_action_policy_summary:quarantine_near:sh_2042",
    )
    request = reuse.build_non_action_reuse_request_v01()

    decision = reuse.evaluate_non_action_reuse_decision_v01(
        "scenario:quarantine_near_policy_summary_blocked",
        reuse.CANDIDATE_QUARANTINE_NEAR_POLICY_SUMMARY_BLOCKED,
        record,
        request,
    )

    assert decision.direct_reuse_allowed is False
    assert decision.direct_reuse_allowed_for_information_only is False
    assert decision.root_shortcut_allowed is False
    assert decision.decision_class == reuse.DECISION_BLOCKED
    assert decision.root_review_required is True
    assert decision.action_permission_granted is False
    assert decision.payment_permission_created is False
    assert decision.shipment_permission_created is False
    assert decision.ticket_permission_created is False
    assert decision.action_commit_packet_created is False
    assert decision.receipt_created is False
    assert decision.real_world_effects_count == 0
    assert reuse.REASON_QUARANTINE_GATE_FAILED in decision.reason_codes
    assert reuse.REASON_ROOT_REMAINS_FINAL_AUTHORITY in decision.reason_codes


def test_drs_avf_reuse_gate_are_not_authority() -> None:
    report = _report()

    for decision in report.decisions:
        assert decision.drs_is_authority is False
        assert decision.avf_is_authority is False
        assert decision.reuse_gate_is_authority is False
        assert decision.reuse_score_is_authority is False
        assert decision.semantic_similarity_is_authority is False
        assert reuse.REASON_ROOT_REMAINS_FINAL_AUTHORITY in decision.reason_codes


def test_validate_report_rejects_bad_effect_counter() -> None:
    report = _report()
    bad_counters = dict(report.counters)
    bad_counters["real_world_effects_count"] = 1
    bad_report = replace(report, counters=bad_counters)

    valid, reasons = reuse.validate_non_action_direct_reuse_report_v01(bad_report)

    assert valid is False
    assert "counter_mismatch:real_world_effects_count" in reasons


def test_validate_report_rejects_extra_direct_reuse() -> None:
    report = _report()
    payment = _decision(
        report,
        reuse.CANDIDATE_SAME_POLICY_RECORD_AS_PAYMENT_PERMISSION,
    )
    mutated_payment = replace(payment, direct_reuse_allowed=True)
    decisions = tuple(
        mutated_payment if decision is payment else decision
        for decision in report.decisions
    )
    bad_report = replace(report, decisions=decisions)

    valid, reasons = reuse.validate_non_action_direct_reuse_report_v01(bad_report)

    assert valid is False
    assert "direct_reuse_count_mismatch" in reasons


def test_source_import_boundary() -> None:
    source = Path("hedgehog/non_action_reuse_positive_control.py").read_text()

    disallowed_imports = (
        "import google.genai",
        "from google import genai",
        "import requests",
        "from requests",
        "import urllib",
        "from urllib",
        "import openai",
        "from openai",
        "import subprocess",
        "from subprocess",
        "run_full_wow",
        "run_full_semantic",
        "hedgehog.action_commit_packet",
        "hedgehog.mock_connector_sandbox",
        "call_real_bank",
        "call_real_supplier",
        "call_real_warehouse",
        "production " + "ready",
        "public auditor " + "ready",
    )
    for marker in disallowed_imports:
        assert marker not in source

    forbidden_phrases = (
        "direct reuse grants " + "permission",
        "DRS " + "decides",
        "reuse score is " + "authority",
        "semantic similarity is " + "authority",
        "old receipt grants " + "permission",
        "old quote grants " + "ticket",
        "receipt grants " + "permission",
        "ticket receipt grants " + "permission",
        "ActionCommitPacket created " + "by reuse",
    )
    for phrase in forbidden_phrases:
        assert phrase not in source
