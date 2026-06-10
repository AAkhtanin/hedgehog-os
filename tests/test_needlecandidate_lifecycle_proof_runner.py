from __future__ import annotations

from copy import deepcopy
from dataclasses import replace

from demo.run_audit_hash_chain import canonical_hash
from demo.run_needlecandidate_lifecycle_proof import (
    collect_needlecandidate_lifecycle_proof,
    run_needlecandidate_lifecycle_proof,
    validate_needlecandidate_lifecycle_report_consistency,
)


def _report():
    return collect_needlecandidate_lifecycle_proof()


def _by_id(rows, key):
    return {row[key]: row for row in rows}


def test_runner_contains_required_sections():
    output = run_needlecandidate_lifecycle_proof()
    for heading in (
        "[NEEDLECANDIDATE LIFECYCLE PROOF]",
        "[INPUT / MODE]",
        "[SOURCE EVIDENCE]",
        "[NEEDLE CANDIDATE ARTIFACTS]",
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
    assert mode["mode"] == "deterministic_needlecandidate_lifecycle_proof"
    assert mode["local_proof_level_only"] is True
    for key in (
        "live_network_used",
        "telegram_used",
        "real_external_action",
        "production_persistence",
        "global_drs_implemented",
        "external_drs_network_implemented",
        "production_needleforge_implemented",
        "marennya_invoked",
        "up_invoked",
    ):
        assert mode[key] is False


def test_source_proofs_are_consumed_and_pass():
    source = _report().source_evidence
    assert source["warehouse_applied_source_status"] == "PASS"
    assert "water_filter short_by_2" in source["warehouse_source_evidence"]
    assert source["certificate_applied_source_status"] == "PASS"
    assert "insurance expired" in source["certificate_source_evidence"]
    assert source["permission_needsuser_source_status"] == "PASS"
    assert source["permission_boundary_present"] is True
    assert source["drs_lifecycle_source_status"] == "PASS"
    assert source["conflictcheck_source_status"] == "PASS"
    assert source["audit_hash_chain_source_status"] == "PASS"


def test_safe_candidates_exist_with_bounded_contracts():
    candidates = _by_id(_report().needle_candidate_artifacts, "candidate_id")
    warehouse = candidates["needle_candidate_warehouse_restock_readiness_v0_1"]
    certificate = candidates[
        "needle_candidate_certificate_document_update_v0_1"
    ]
    assert warehouse["candidate_type"] == "bounded_action_candidate"
    assert warehouse["allowed_action_class"] == "prepare_restock_request_only"
    assert {"execute_dispatch", "execute_restock"}.issubset(
        set(warehouse["forbidden_actions"])
    )
    assert certificate["candidate_type"] == "bounded_needs_user_candidate"
    assert certificate["allowed_action_class"] == (
        "prepare_user_document_update_request_only"
    )
    assert {"submit_certificate_request", "mark_ready_without_documents"}.issubset(
        set(certificate["forbidden_actions"])
    )
    for candidate in (warehouse, certificate):
        assert candidate["requires_permission"] is True
        assert candidate["candidate_status"] == "proposed"
        assert candidate["installable_now"] is False
        assert candidate["installed_needle_created"] is False


def test_warehouse_candidate_boundary_is_granular():
    candidates = _by_id(_report().needle_candidate_artifacts, "candidate_id")
    warehouse = candidates["needle_candidate_warehouse_restock_readiness_v0_1"]
    assert warehouse["candidate_id"] == (
        "needle_candidate_warehouse_restock_readiness_v0_1"
    )
    assert warehouse["allowed_action_class"] == "prepare_restock_request_only"
    assert {"execute_dispatch", "execute_restock", "submit_external_order"}.issubset(
        set(warehouse["forbidden_actions"])
    )
    assert warehouse["requires_permission"] is True
    assert warehouse["installable_now"] is False
    assert warehouse["installed_needle_created"] is False
    assert warehouse["root_review_required"] is True


def test_certificate_candidate_boundary_is_granular():
    candidates = _by_id(_report().needle_candidate_artifacts, "candidate_id")
    certificate = candidates[
        "needle_candidate_certificate_document_update_v0_1"
    ]
    assert certificate["candidate_id"] == (
        "needle_candidate_certificate_document_update_v0_1"
    )
    assert certificate["allowed_action_class"] == (
        "prepare_user_document_update_request_only"
    )
    assert {
        "submit_certificate_request",
        "contact_government_api",
        "mark_ready_without_documents",
    }.issubset(set(certificate["forbidden_actions"]))
    assert certificate["requires_permission"] is True
    assert certificate["installable_now"] is False
    assert certificate["installed_needle_created"] is False
    assert certificate["root_review_required"] is True


def test_unsafe_candidates_are_rejected_or_quarantined():
    candidates = _by_id(_report().needle_candidate_artifacts, "candidate_id")
    assert candidates["unsafe_auto_submit_candidate"]["candidate_status"] == (
        "rejected_quarantined"
    )
    assert candidates["unsafe_ready_override_candidate"]["candidate_status"] == (
        "rejected_conflict"
    )
    assert candidates["unsafe_permission_bypass_candidate"][
        "candidate_status"
    ] == "rejected_quarantined"
    assert all(
        candidate["installed_needle_created"] is False
        for candidate in candidates.values()
    )


def test_unsafe_candidate_rejection_reasons_are_explicit():
    candidates = _by_id(_report().needle_candidate_artifacts, "candidate_id")
    assert candidates["unsafe_auto_submit_candidate"]["rejection_reason"] == (
        "external submission forbidden in proof-level layer"
    )
    assert candidates["unsafe_ready_override_candidate"]["rejection_reason"] == (
        "contradicts applied evidence"
    )
    assert candidates["unsafe_permission_bypass_candidate"]["rejection_reason"] == (
        "violates Permission/NeedsUser proof"
    )


def test_validation_rows_enforce_candidate_boundary():
    rows = _by_id(_report().needle_candidate_validation_rows, "validation_row_id")
    assert rows["warehouse_restock_candidate"]["validation_status"] == (
        "accepted_as_candidate_pending_review"
    )
    assert rows["certificate_document_update_candidate"]["validation_status"] == (
        "accepted_as_candidate_pending_review"
    )
    assert rows["unsafe_auto_submit_candidate"]["validation_status"] == (
        "rejected_quarantined"
    )
    assert rows["unsafe_ready_override_candidate"]["validation_status"] == (
        "rejected_conflict"
    )
    assert rows["unsafe_permission_bypass_candidate"]["validation_status"] == (
        "rejected_quarantined"
    )
    assert rows["installed_needle_without_root_install"]["validation_status"] == (
        "rejected"
    )
    assert not any(
        row["validation_status"].startswith("accepted")
        and "installed_needle" in row["validation_status"]
        for row in rows.values()
    )
    assert {
        rows["warehouse_restock_candidate"]["validation_status"],
        rows["certificate_document_update_candidate"]["validation_status"],
    } == {"accepted_as_candidate_pending_review"}


def test_gt_recommends_only_pending_review_and_cannot_install():
    gt = _report().needle_candidate_gt_selection
    assert gt["recommended_candidate_status"] == "candidate_pending_review"
    assert set(gt["recommended_candidate_ids"]) == {
        "needle_candidate_warehouse_restock_readiness_v0_1",
        "needle_candidate_certificate_document_update_v0_1",
    }
    assert "unsafe_auto_submit_candidate" in gt["rejected_candidate_ids"]
    assert "unsafe_ready_override_candidate" in gt["rejected_candidate_ids"]
    assert "unsafe_permission_bypass_candidate" in gt["rejected_candidate_ids"]
    assert "malicious_installed_needle_claim" in gt["rejected_candidate_ids"]
    assert gt["gt_is_not_truth_proof"] is True
    assert gt["gt_cannot_install_needles"] is True
    assert gt["gt_remains_advisory_until_root"] is True


def test_root_final_never_installs_or_claims_action_completion():
    finals = _report().needle_candidate_root_final_artifacts
    assert len(finals) == 5
    assert all(final["installed_needle_created"] is False for final in finals)
    assert all(final["completed_action_claimed"] is False for final in finals)
    statuses = {final["root_candidate_status"] for final in finals}
    assert statuses == {
        "candidate_pending_review",
        "candidate_quarantined",
        "candidate_rejected",
    }
    forbidden_outcomes = {
        "completed_dispatch",
        "completed_restock",
        "completed_submission",
        "executable_external_action",
        "production_needle",
        "installed_needle",
    }
    assert not any(
        value in forbidden_outcomes for final in finals for value in final.values()
    )


def test_drs_lifecycle_has_required_proof_records():
    records = _by_id(_report().needle_candidate_drs_lifecycle_records, "record_id")
    expected = {
        "needle_candidate_experience_record": "experience_record",
        "needle_candidate_reuse_pattern_record": "reuse_pattern",
        "needle_candidate_pending_review_record": "needle_candidate",
        "needle_candidate_quarantine_auto_submit": "quarantine",
        "needle_candidate_quarantine_permission_bypass": "quarantine",
        "needle_candidate_conflict_ready_override": "conflict",
    }
    assert {
        record_id: records[record_id]["record_type"] for record_id in expected
    } == expected
    assert all(record["proof_only"] for record in records.values())
    assert all(
        record.get("production_persistence", False) is False
        for record in records.values()
    )
    assert all(
        record.get("global_drs_write", False) is False
        for record in records.values()
    )
    assert records["needle_candidate_pending_review_record"]["status"] == (
        "candidate_pending_review"
    )
    assert records["needle_candidate_pending_review_record"]["status"] != (
        "installed"
    )


def test_conflictcheck_has_three_conflicts_and_two_safe_no_conflicts():
    conflicts = _by_id(
        _report().needle_candidate_conflict_reports, "conflict_report_id"
    )
    for conflict_id in (
        "conflict_auto_submit_candidate_vs_no_external_action_boundary",
        "conflict_ready_override_candidate_vs_applied_evidence",
        "conflict_permission_bypass_candidate_vs_permission_needsuser_boundary",
    ):
        assert conflicts[conflict_id]["conflict_detected"] is True
    for conflict_id in (
        "no_conflict_safe_warehouse_restock_candidate",
        "no_conflict_safe_certificate_document_update_candidate",
    ):
        assert conflicts[conflict_id]["conflict_detected"] is False
        assert conflicts[conflict_id]["root_review_required"] is True
    assert conflicts[
        "conflict_auto_submit_candidate_vs_no_external_action_boundary"
    ]["candidate_id"] == "unsafe_auto_submit_candidate"
    assert conflicts[
        "conflict_ready_override_candidate_vs_applied_evidence"
    ]["candidate_id"] == "unsafe_ready_override_candidate"
    assert conflicts[
        "conflict_permission_bypass_candidate_vs_permission_needsuser_boundary"
    ]["candidate_id"] == "unsafe_permission_bypass_candidate"
    assert all(
        conflict["conflictcheck_is_authority"] is False
        for conflict in conflicts.values()
    )


def test_audit_entry_hashes_needlecandidate_proof_artifact():
    report = _report()
    assert report.needle_candidate_audit_entry["audit_entry_id"] == (
        "audit_needlecandidate_lifecycle_v0_1"
    )
    assert report.needle_candidate_audit_entry["canonical_payload_hash"] == (
        canonical_hash(report.needle_candidate_proof_artifact)
    )
    assert report.needle_candidate_audit_entry["previous_chain_last_entry_hash"] == (
        report.audit_hash_chain["previous_chain_last_entry_hash"]
    )
    assert report.needle_candidate_audit_entry["proof_only"] is True
    assert report.needle_candidate_audit_entry["production_persistence"] is False
    assert report.needle_candidate_audit_entry["global_drs_write"] is False
    assert report.needle_candidate_audit_entry["audit_chain_decides_truth"] is False


def test_consistency_validator_rejects_wrong_audit_hash():
    report = _report()
    audit = deepcopy(report.needle_candidate_audit_entry)
    audit["canonical_payload_hash"] = "0" * 64
    assert validate_needlecandidate_lifecycle_report_consistency(
        replace(report, needle_candidate_audit_entry=audit)
    ) is False


def test_consistency_validator_rejects_missing_safe_warehouse_candidate():
    report = _report()
    candidates = [
        candidate
        for candidate in report.needle_candidate_artifacts
        if candidate["candidate_id"]
        != "needle_candidate_warehouse_restock_readiness_v0_1"
    ]
    assert validate_needlecandidate_lifecycle_report_consistency(
        replace(report, needle_candidate_artifacts=candidates)
    ) is False


def test_consistency_validator_rejects_missing_unsafe_conflict_report():
    report = _report()
    conflicts = [
        conflict
        for conflict in report.needle_candidate_conflict_reports
        if conflict["conflict_report_id"]
        != "conflict_ready_override_candidate_vs_applied_evidence"
    ]
    assert validate_needlecandidate_lifecycle_report_consistency(
        replace(report, needle_candidate_conflict_reports=conflicts)
    ) is False


def test_consistency_validator_rejects_installed_needle_claim():
    report = _report()
    candidates = deepcopy(report.needle_candidate_artifacts)
    candidates[0]["installed_needle_created"] = True
    assert validate_needlecandidate_lifecycle_report_consistency(
        replace(report, needle_candidate_artifacts=candidates)
    ) is False


def test_consistency_validator_rejects_warehouse_installable_now():
    report = _report()
    candidates = deepcopy(report.needle_candidate_artifacts)
    candidates[0]["installable_now"] = True
    assert validate_needlecandidate_lifecycle_report_consistency(
        replace(report, needle_candidate_artifacts=candidates)
    ) is False


def test_consistency_validator_rejects_certificate_installed_needle_claim():
    report = _report()
    candidates = deepcopy(report.needle_candidate_artifacts)
    candidates[1]["installed_needle_created"] = True
    assert validate_needlecandidate_lifecycle_report_consistency(
        replace(report, needle_candidate_artifacts=candidates)
    ) is False


def test_consistency_validator_rejects_gt_recommending_unsafe_candidate():
    report = _report()
    gt = deepcopy(report.needle_candidate_gt_selection)
    gt["recommended_candidate_ids"].append("unsafe_auto_submit_candidate")
    assert validate_needlecandidate_lifecycle_report_consistency(
        replace(report, needle_candidate_gt_selection=gt)
    ) is False


def test_consistency_validator_rejects_unsafe_root_pending_review():
    report = _report()
    finals = deepcopy(report.needle_candidate_root_final_artifacts)
    finals[2]["root_candidate_status"] = "candidate_pending_review"
    assert validate_needlecandidate_lifecycle_report_consistency(
        replace(report, needle_candidate_root_final_artifacts=finals)
    ) is False


def test_consistency_validator_rejects_audit_truth_claim():
    report = _report()
    audit = deepcopy(report.needle_candidate_audit_entry)
    audit["audit_chain_decides_truth"] = True
    assert validate_needlecandidate_lifecycle_report_consistency(
        replace(report, needle_candidate_audit_entry=audit)
    ) is False


def test_consistency_validator_rejects_authority_candidate_false():
    report = _report()
    authority = deepcopy(report.authority_safety)
    authority["needle_candidate_created"] = False
    assert validate_needlecandidate_lifecycle_report_consistency(
        replace(report, authority_safety=authority)
    ) is False


def test_consistency_validator_rejects_authority_installed_needle_true():
    report = _report()
    authority = deepcopy(report.authority_safety)
    authority["installed_needle_created"] = True
    assert validate_needlecandidate_lifecycle_report_consistency(
        replace(report, authority_safety=authority)
    ) is False


def test_consistency_validator_rejects_summary_candidate_or_install_corruption():
    report = _report()
    summary = deepcopy(report.summary)
    summary["needle_candidate_created"] = False
    assert validate_needlecandidate_lifecycle_report_consistency(
        replace(report, summary=summary)
    ) is False
    summary = deepcopy(report.summary)
    summary["installed_needle_created"] = True
    assert validate_needlecandidate_lifecycle_report_consistency(
        replace(report, summary=summary)
    ) is False


def test_authority_and_safety_boundaries_are_preserved():
    report = _report()
    assert all(report.malicious_unsafe_claims.values())
    authority = report.authority_safety
    assert authority["needlecandidate_is_installed_needle"] is False
    assert authority["needleforge_is_production_needlefactory"] is False
    assert authority["needle_candidate_created"] is True
    assert authority["protocol_candidate_created"] is False
    assert authority["installed_needle_created"] is False
    assert authority["gt_cannot_install_needles"] is True
    assert authority["root_remains_final_authority"] is True
    assert authority["no_real_external_action_executed"] is True
    assert authority["no_production_persistence"] is True
    assert authority["no_global_drs_write"] is True
    assert authority["production_autonomy_claimed"] is False


def test_summary_pass_derives_from_explicit_artifacts():
    summary = _report().summary
    assert summary["needlecandidate_lifecycle_proof_status"] == "PASS"
    assert summary["scenarios_verified"] == 5
    for key in (
        "safe_warehouse_candidate_created",
        "safe_certificate_candidate_created",
        "unsafe_auto_submit_candidate_rejected",
        "unsafe_ready_override_candidate_rejected",
        "unsafe_permission_bypass_candidate_rejected",
        "needle_candidate_created",
        "gt_cannot_install_needles",
        "root_remains_final_authority",
        "no_real_external_action_executed",
        "no_production_persistence",
        "no_global_drs_write",
        "explicit_needlecandidate_artifacts_consistent",
        "ready_for_needlecandidate_docs_sync",
    ):
        assert summary[key] is True
    assert summary["installed_needle_created"] is False
    assert summary["protocol_candidate_created"] is False
    assert summary["production_autonomy_claimed"] is False
