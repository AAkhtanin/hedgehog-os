from __future__ import annotations

from copy import deepcopy
from dataclasses import replace

from demo.run_audit_hash_chain import canonical_hash
from demo.run_permission_needsuser_ux_proof import (
    collect_permission_needsuser_ux_proof,
    run_permission_needsuser_ux_proof,
    validate_permission_needsuser_report_consistency,
)


def _report():
    return collect_permission_needsuser_ux_proof()


def _by_id(rows, key):
    return {row[key]: row for row in rows}


def test_runner_contains_required_sections():
    output = run_permission_needsuser_ux_proof()
    for heading in (
        "[PERMISSION NEEDSUSER UX PROOF]",
        "[INPUT / MODE]",
        "[SOURCE APPLIED CONTEXTS]",
        "[PERMISSION REQUEST ARTIFACTS]",
        "[NEEDSUSER ARTIFACTS]",
        "[PERMISSION RESPONSE ARTIFACTS]",
        "[VALIDATION ROWS]",
        "[GT]",
        "[ROOT FINAL]",
        "[DRS LIFECYCLE]",
        "[CONFLICTCHECK]",
        "[AUDIT HASH-CHAIN]",
        "[MALICIOUS / UNSAFE CLAIMS]",
        "[AUTHORITY / SAFETY]",
        "[SUMMARY]",
    ):
        assert heading in output


def test_mode_is_deterministic_local_proof_only():
    mode = _report().input_mode
    assert mode["mode"] == "deterministic_permission_needsuser_ux_proof"
    assert mode["local_proof_level_only"] is True
    for key in (
        "live_network_used",
        "telegram_used",
        "real_external_action",
        "production_persistence",
        "global_drs_implemented",
        "external_drs_network_implemented",
        "marennya_invoked",
        "up_invoked",
        "needleforge_invoked",
    ):
        assert mode[key] is False


def test_warehouse_and_certificate_contexts_are_consumed():
    contexts = _report().source_applied_contexts
    assert contexts["warehouse_source_status"] == "PASS"
    assert contexts["warehouse_id"] == "W-17"
    assert contexts["warehouse_blocking_reason"] == "water_filter short by 2"
    assert contexts["certificate_source_status"] == "PASS"
    assert contexts["application_id"] == "APP-77"
    assert contexts["certificate_request_id"] == "CERT-310"


def test_permission_request_and_needs_user_artifacts_exist():
    report = _report()
    assert len(report.permission_request_artifacts) == 2
    assert len(report.needs_user_artifacts) == 2
    assert all(
        row["no_action_until_root_accepts_permission"]
        for row in report.permission_request_artifacts
    )
    assert all(row["proof_only"] for row in report.needs_user_artifacts)


def test_warehouse_permission_scenario_blocks_dispatch_and_restock():
    needs = _by_id(_report().needs_user_artifacts, "needs_user_id")
    warehouse = needs["needs_user_warehouse_W17_D2042"]
    assert warehouse["source_scenario"] == "warehouse_restock_permission_required"
    assert warehouse["safe_next_step"] == "wait_for_operator_confirmation"
    assert warehouse["no_external_action_executed"] is True


def test_certificate_scenario_blocks_external_submission():
    needs = _by_id(_report().needs_user_artifacts, "needs_user_id")
    certificate = needs["needs_user_certificate_APP77_CERT310"]
    assert set(certificate["missing_inputs"]) == {
        "updated_insurance_certificate",
        "payment_receipt",
    }
    assert certificate["no_external_action_executed"] is True


def test_unsafe_bypass_and_completed_action_claim_are_rejected():
    rows = _by_id(_report().permission_validation_rows, "validation_row_id")
    assert rows["invalid_permission_bypass"]["validation_status"] == "rejected"
    assert rows["invalid_permission_bypass"]["result_status"] == "quarantined"
    assert rows["completed_action_without_execution"]["validation_status"] == (
        "rejected"
    )


def test_explicit_user_denial_blocks_action():
    responses = _by_id(
        _report().permission_response_artifacts, "permission_response_id"
    )
    denial = responses["permission_response_explicit_denial"]
    assert denial["response_status"] == "denied"
    assert denial["user_permission_granted"] is False
    assert denial["action_allowed"] is False
    assert denial["real_action_executed"] is False


def test_explicit_user_approval_is_future_permission_only():
    responses = _by_id(
        _report().permission_response_artifacts, "permission_response_id"
    )
    approval = responses["permission_response_proof_approval"]
    assert approval["response_status"] == "approved_for_proof"
    assert approval["user_permission_granted"] is True
    assert approval["action_allowed_for_future_layer"] is True
    assert approval["real_action_executed"] is False
    assert approval["completed_action_claimed"] is False


def test_gt_selects_safe_needs_user_or_blocked_result():
    gt = _report().permission_gt_selection
    assert gt["selected_result_status"] == "needs_user_or_blocked"
    assert "invalid_permission_bypass" in gt["rejected_result_ids"]
    assert "completed_action_without_execution" in gt["rejected_result_ids"]
    assert gt["gt_is_not_truth_proof"] is True
    assert gt["gt_remains_advisory_until_root"] is True


def test_root_final_never_claims_completed_action():
    finals = _report().permission_root_final_artifacts
    assert len(finals) == 5
    assert all(row["completed_action_claimed"] is False for row in finals)
    outcomes = {row["outcome"] for row in finals}
    assert "blocked_pending_permission" in outcomes
    assert "denied_by_user" in outcomes
    assert "permission_ready_for_future_action_layer" in outcomes
    assert not outcomes.intersection(
        {
            "completed_external_action",
            "completed_dispatch",
            "completed_submission",
            "completed_restock",
        }
    )


def test_drs_lifecycle_has_required_local_record_types():
    records = _by_id(_report().permission_drs_lifecycle_records, "record_id")
    assert records["permission_experience_record"]["record_type"] == (
        "experience_record"
    )
    assert records["permission_blocked_trace"]["record_type"] == "blocked_trace"
    assert records["permission_denial_deadend"]["record_type"] == "deadend"
    assert records["permission_bypass_quarantine"]["record_type"] == "quarantine"
    assert records["permission_future_action_reuse_candidate"]["record_type"] == (
        "reuse_candidate"
    )
    assert all(record["proof_only"] for record in records.values())


def test_no_protocol_needle_candidate_or_installed_needle():
    authority = _report().authority_safety
    assert authority["protocol_candidate_created"] is False
    assert authority["needle_candidate_created"] is False
    assert authority["installed_needle_created"] is False


def test_conflictcheck_has_required_conflict_and_no_conflict_reports():
    reports = _by_id(_report().permission_conflict_reports, "conflict_report_id")
    assert reports[
        "conflict_permission_bypass_vs_missing_user_confirmation"
    ]["conflict_detected"] is True
    assert reports[
        "conflict_completed_action_claim_vs_no_real_execution"
    ]["conflict_detected"] is True
    assert reports["no_conflict_needs_user_pending_permission"][
        "conflict_detected"
    ] is False
    assert all(not row["conflictcheck_is_authority"] for row in reports.values())


def test_audit_entry_hashes_permission_proof_artifact():
    report = _report()
    assert report.permission_audit_entry["audit_entry_id"] == (
        "audit_permission_needsuser_v0_1"
    )
    assert report.permission_audit_entry["canonical_payload_hash"] == canonical_hash(
        report.permission_proof_artifact
    )
    assert report.permission_audit_entry["previous_chain_last_entry_hash"] == (
        report.audit_hash_chain["previous_chain_last_entry_hash"]
    )
    assert report.permission_audit_entry["production_persistence"] is False


def test_consistency_validator_rejects_wrong_audit_hash():
    report = _report()
    entry = deepcopy(report.permission_audit_entry)
    entry["canonical_payload_hash"] = "0" * 64
    assert validate_permission_needsuser_report_consistency(
        replace(report, permission_audit_entry=entry)
    ) is False


def test_consistency_validator_rejects_missing_permission_request():
    report = _report()
    requests = [
        row
        for row in report.permission_request_artifacts
        if row["permission_request_id"] != "permission_request_warehouse_W17_D2042"
    ]
    assert validate_permission_needsuser_report_consistency(
        replace(report, permission_request_artifacts=requests)
    ) is False


def test_consistency_validator_rejects_missing_conflict_report():
    report = _report()
    conflicts = [
        row
        for row in report.permission_conflict_reports
        if row["conflict_report_id"]
        != "conflict_completed_action_claim_vs_no_real_execution"
    ]
    assert validate_permission_needsuser_report_consistency(
        replace(report, permission_conflict_reports=conflicts)
    ) is False


def test_malicious_claims_rejected_and_authority_preserved():
    report = _report()
    assert all(report.malicious_unsafe_claims.values())
    authority = report.authority_safety
    assert authority["root_remains_final_authority"] is True
    assert authority["gt_remains_advisory_until_root"] is True
    assert authority["conflictcheck_remains_advisory_until_root"] is True
    assert authority["no_real_external_action_executed"] is True
    assert authority["no_completed_action_claimed"] is True
    assert authority["production_persistence"] is False
    assert authority["production_autonomy_claimed"] is False


def test_summary_pass_derives_from_explicit_permission_artifacts():
    summary = _report().summary
    assert summary["permission_needsuser_ux_proof_status"] == "PASS"
    assert summary["scenarios_verified"] == 5
    for key in (
        "permission_request_artifacts_created",
        "needs_user_artifacts_created",
        "invalid_permission_bypass_rejected",
        "completed_action_without_execution_rejected",
        "explicit_user_denial_blocks_action",
        "explicit_user_approval_is_future_permission_only",
        "no_real_external_action_executed",
        "no_completed_action_claimed",
        "root_remains_final_authority",
        "explicit_permission_artifacts_consistent",
        "ready_for_permission_needsuser_docs_sync",
    ):
        assert summary[key] is True
    assert summary["protocol_candidate_created"] is False
    assert summary["needle_candidate_created"] is False
    assert summary["installed_needle_created"] is False
    assert summary["production_autonomy_claimed"] is False
