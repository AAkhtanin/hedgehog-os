from __future__ import annotations

import pytest

from demo.run_audit_hash_chain import canonical_hash
from demo.run_read_only_enterprise_connector_sandbox_v01 import (
    collect_read_only_enterprise_connector_sandbox_v01,
    render_read_only_enterprise_connector_sandbox_v01,
)


@pytest.fixture(scope="module")
def report():
    return collect_read_only_enterprise_connector_sandbox_v01()


def _by_id(rows, key):
    return {row[key]: row for row in rows}


def test_runner_title_and_sections(report):
    output = render_read_only_enterprise_connector_sandbox_v01(report)
    for heading in (
        "[READ-ONLY ENTERPRISE CONNECTOR SANDBOX v0.1]",
        "[SOURCE EVIDENCE]",
        "[CONNECTOR REQUESTS]",
        "[SOURCE PROFILES]",
        "[CONNECTOR OBSERVATIONS]",
        "[READ-ONLY REPORTS]",
        "[CONNECTOR BOUNDARY MATRIX]",
        "[ADVERSARIAL ATTEMPTS]",
        "[CONFLICTCHECK]",
        "[GT ADVISORY]",
        "[ROOT FINAL]",
        "[AUDIT]",
        "[SUMMARY]",
    ):
        assert heading in output


def test_closed_checkpoint_metadata_without_replay(report):
    assert report.source_evidence["external_drs_pointer_protocol_source_status"] == "PASS"
    assert report.source_evidence["source_evidence_mode"] == "closed_checkpoint_metadata_only"
    assert report.source_evidence["source_collectors_replayed"] is False


def test_four_connector_domains_are_observed(report):
    assert {row["connector_domain"] for row in report.connector_requests} == {
        "bank_source",
        "legal_registry_source",
        "warehouse_source",
        "logistics_source",
    }
    assert len(report.connector_observations) == 4


def test_all_connector_outputs_are_observations_only(report):
    for row in report.connector_observations:
        assert row["observation_created"] is True
        assert row["root_review_required"] is True
        assert row["trusted_evidence_created"] is False
        assert row["truth_proven"] is False
        assert row["ready_status_created"] is False


def test_clean_bank_observation_remains_untrusted(report):
    rows = _by_id(report.connector_observations, "scenario_id")
    bank = rows["clean_bank_observation"]
    assert "payment_status:observed_paid" in bank["observed_signal"]
    assert "transaction_id:" in bank["observed_signal"]
    assert bank["final_effect"] == "observation_only"


def test_stale_legal_observation_is_blocked_or_quarantined(report):
    rows = _by_id(report.connector_observations, "scenario_id")
    legal = rows["stale_legal_registry_observation"]
    assert legal["stale_or_expired"] is True
    assert legal["blocked_or_quarantined"] is True


def test_warehouse_and_logistics_signals_do_not_finalize_or_execute(report):
    rows = _by_id(report.connector_observations, "scenario_id")
    warehouse = rows["warehouse_stock_observation"]
    logistics = rows["logistics_window_observation"]
    assert warehouse["inventory_signal_available"] is True
    assert warehouse["connector_root_result"] == "not_finalized_by_connector"
    assert logistics["dispatch_window_signal_available"] is True
    assert logistics["dispatch_executed"] is False
    assert logistics["external_action_executed"] is False


def test_read_only_reports_show_no_mutation_write_action_or_bypass(report):
    assert all(
        row["read_only"] is True
        and row["state_mutated"] is False
        and row["drs_written"] is False
        and row["action_executed"] is False
        and row["root_bypassed"] is False
        for row in report.connector_read_only_reports
    )


def test_connector_boundary_invariants_hold(report):
    assert all(value is True for value in report.connector_boundary_matrix.values())


def test_all_six_adversarial_escalations_are_blocked(report):
    assert len(report.adversarial_attempts) == 6
    assert all(row["detected"] is True and row["blocked"] is True for row in report.adversarial_attempts)


def test_unknown_connector_laundering_is_quarantined_and_blocked(report):
    attempts = _by_id(report.adversarial_attempts, "attempt_id")
    laundering = attempts["adversary_unknown_connector_laundering"]
    assert laundering["quarantined"] is True
    assert laundering["final_effect"] == "quarantined_blocked"
    assert laundering["trusted_evidence_created"] is False


def test_no_escalation_creates_truth_ready_action_write_or_needle(report):
    for row in report.adversarial_attempts:
        for field in (
            "trusted_evidence_created",
            "truth_proven",
            "ready_status_created",
            "authority_transferred",
            "external_action_executed",
            "global_drs_write",
            "external_drs_write",
            "installed_needle_created",
            "production_persistence",
            "network_called",
        ):
            assert row[field] is False


def test_conflictcheck_and_gt_are_advisory(report):
    assert report.conflictcheck_result["conflict_count"] == 6
    assert report.conflictcheck_result["conflictcheck_is_authority"] is False
    assert report.gt_advisory["gt_recommendation"] == "block_or_quarantine_connector_escalations"
    assert report.gt_advisory["gt_is_advisory"] is True
    assert all(
        report.gt_advisory[field] is False
        for field in (
            "gt_can_mark_observation_trusted",
            "gt_can_mark_truth",
            "gt_can_execute_action",
            "gt_can_write_external_drs",
            "gt_can_install_needle",
        )
    )


def test_root_final_preserves_observation_only_boundary(report):
    root = report.root_final
    assert root["root_result"] == "read_only_observations_collected_with_escalations_blocked"
    assert root["safe_secondary_outcome"] == "needs_external_evidence_acceptance_gate"
    assert root["connector_observations_created"] == 4
    assert root["root_remains_final_authority"] is True


def test_no_network_gemini_telegram_marennya_or_up(report):
    summary = report.summary
    for field in ("network_called", "gemini_called", "telegram_used", "marennya_invoked", "up_invoked"):
        assert summary[field] is False


def test_external_evidence_acceptance_gate_is_not_implemented(report):
    assert report.summary["external_evidence_acceptance_gate_implemented"] is False
    assert report.root_final["trusted_evidence_created"] is False


def test_audit_hash_matches_proof_artifact(report):
    assert report.audit_entry["canonical_payload_hash"] == canonical_hash(report.proof_artifact)
    assert report.audit_entry["audit_chain_decides_truth"] is False


def test_summary_pass(report):
    summary = report.summary
    assert summary["read_only_enterprise_connector_sandbox_v01_status"] == "PASS"
    assert summary["connector_observations_created"] == 4
    assert summary["adversarial_attempts_observed"] == 6
    assert summary["adversarial_attempts_blocked"] == 6
    assert summary["quarantined_attempts_observed"] == 1
    assert summary["ready_for_read_only_enterprise_connector_sandbox_v01_tests"] is True
