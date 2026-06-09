from __future__ import annotations

from copy import deepcopy
from dataclasses import replace

from demo.run_applied_certificate_readiness_demo import (
    LOCAL_DOCUMENTS,
    collect_applied_certificate_readiness_demo,
    run_applied_certificate_readiness_demo,
    validate_applied_certificate_report_consistency,
)
from demo.run_audit_hash_chain import canonical_hash


def _report():
    return collect_applied_certificate_readiness_demo()


def _proposals():
    return {row["result_proposal_id"]: row for row in _report().result_proposals}


def test_runner_contains_all_required_sections():
    output = run_applied_certificate_readiness_demo()
    for heading in (
        "[APPLIED CERTIFICATE READINESS DEMO]",
        "[INPUT / MODE]",
        "[USER EVENT]",
        "[WORLDSTATE]",
        "[DRS RETRIEVAL]",
        "[CONTROLLED ROUTE ASSEMBLY]",
        "[MATRIX GATE / ROUTE GATE]",
        "[AVF / ATTRACTOR PACKET]",
        "[APPLIED PLAN GRAPH]",
        "[DOCUMENT CHECK RESULTS]",
        "[ARCHITECT / PLAN]",
        "[DAG / EXECUTION]",
        "[RESULT PROPOSALS]",
        "[APPLIED VALIDATION ROWS]",
        "[POST V&V]",
        "[APPLIED GT SELECTION]",
        "[GT]",
        "[ROOT FINAL]",
        "[APPLIED DRS LIFECYCLE RECORDS]",
        "[DRS LIFECYCLE]",
        "[APPLIED CONFLICT REPORTS]",
        "[CONFLICTCHECK]",
        "[APPLIED AUDIT ENTRY]",
        "[AUDIT HASH-CHAIN]",
        "[MALICIOUS / UNSAFE CLAIMS]",
        "[AUTHORITY / SAFETY]",
        "[SUMMARY]",
    ):
        assert heading in output


def test_mode_is_deterministic_local_proof_only_without_external_effects():
    mode = _report().input_mode
    assert mode["mode"] == "deterministic_applied_certificate_readiness_demo"
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


def test_user_event_identifies_application_and_certificate_request():
    event = _report().user_event
    assert event["application_id"] == "APP-77"
    assert event["certificate_request_id"] == "CERT-310"
    assert event["requested_certificate_type"] == "travel_document_readiness"
    assert "Do not submit anything externally" in event["user_task"]


def test_worldstate_has_expired_insurance_and_missing_receipt():
    world = _report().worldstate
    assert world["local_documents"] == LOCAL_DOCUMENTS
    assert world["local_documents"]["insurance_certificate"]["expiry_status"] == (
        "expired"
    )
    assert world["local_documents"]["payment_receipt"]["status"] == "missing"
    assert world["blocking_items"] == {
        "insurance_certificate": "expired",
        "payment_receipt": "missing",
    }


def test_collectors_and_controlled_boundaries_are_consumed():
    report = _report()
    assert report.controlled_route_assembly[
        "controlled_route_assembly_source_status"
    ] == "PASS"
    assert report.avf_attractor_packet["avf_source_status"] == "PASS"
    assert report.architect_plan["architect_source_status"] == "PASS"
    assert report.dag_execution["dag_source_status"] == "PASS"
    assert report.post_vv["post_vv_source_status"] == "PASS"
    assert report.gt["gt_source_status"] == "PASS"
    assert report.root_final["root_final_source_status"] == "PASS"
    assert report.drs_lifecycle["drs_lifecycle_source_status"] == "PASS"
    assert report.conflictcheck["conflictcheck_source_status"] == "PASS"
    assert report.audit_hash_chain["audit_hash_chain_source_status"] == "PASS"
    assert report.controlled_route_assembly["orchestrator_manages_avf"] is False
    assert report.avf_attractor_packet["hardmask_beats_orchestrator_confidence"]


def test_applied_plan_graph_has_required_nodes():
    graph = _report().applied_certificate_plan_graph
    assert graph["plan_graph_id"] == "applied_certificate_plan_graph_APP77_CERT310"
    assert graph["raw_user_text_received"] is False
    assert {node["node_id"] for node in graph["nodes"]} == {
        "document_presence_check_node",
        "document_expiry_check_node",
        "readiness_certificate_draft_node",
        "no_external_submission_guard_node",
    }
    assert graph["contract_valid"] is True


def test_document_results_derive_blocking_reasons_and_no_submission():
    results = _report().document_check_results
    assert results["document_presence_check_result"]["payment_receipt"] == "missing"
    assert (
        results["document_expiry_check_result"]["insurance_certificate"]
        == "expired"
    )
    assert results["readiness_certificate_draft_result"] == {
        "certificate_readiness": "not_ready",
        "blocking_reasons": [
            "insurance_certificate expired",
            "payment_receipt missing",
        ],
    }
    assert results["no_external_submission_guard_result"][
        "no_external_submission_executed"
    ] is True


def test_result_proposals_preserve_safe_invalid_and_needs_user_branches():
    proposals = _proposals()
    assert proposals["completed_not_ready_certificate"]["status"] == "completed"
    assert proposals["completed_not_ready_certificate"]["safe_for_root_final"] is True
    assert proposals["invalid_ready_certificate"]["status"] == "rejected"
    assert proposals["invalid_ready_certificate"]["safe_for_root_final"] is False
    assert proposals["needs_user_document_update"]["status"] == "needs_user"
    assert proposals["needs_user_document_update"]["safe_for_root_final"] is True


def test_validation_rows_accept_reject_and_preserve_needs_user():
    rows = {
        row["result_proposal_id"]: row for row in _report().applied_validation_rows
    }
    assert rows["completed_not_ready_certificate"]["validation_status"] == "accepted"
    assert rows["invalid_ready_certificate"]["validation_status"] == "rejected"
    assert rows["invalid_ready_certificate"]["consistency_valid"] is False
    assert (
        rows["needs_user_document_update"]["validation_status"]
        == "needs_user_valid"
    )
    assert _report().post_vv["invalid_ready_certificate_rejected"] is True


def test_gt_selects_not_ready_and_preserves_needs_user_secondary():
    selection = _report().applied_gt_selection
    assert selection["selected_result_proposal_id"] == (
        "completed_not_ready_certificate"
    )
    assert selection["secondary_result_proposal_id"] == "needs_user_document_update"
    assert selection["rejected_result_proposal_ids"] == [
        "invalid_ready_certificate"
    ]


def test_root_final_reports_not_ready_and_no_external_submission():
    final = _report().root_final
    assert final["certificate_readiness"] == "not_ready"
    assert final["blocking_reasons"] == [
        "insurance_certificate expired",
        "payment_receipt missing",
    ]
    assert final["ready_documents"] == ["passport_scan", "residency_proof"]
    assert final["invalid_ready_claim_rejected"] is True
    assert final["no_external_submission_executed"] is True
    assert final["proof_level_certificate_only"] is True


def test_lifecycle_records_exist_without_protocol_or_needle_candidates():
    report = _report()
    records = {
        row["record_id"]: row for row in report.applied_drs_lifecycle_records
    }
    assert records["certificate_experience_record_APP77_CERT310"]["record_type"] == (
        "experience_record"
    )
    assert records["certificate_reuse_candidate_APP77_CERT310"]["record_type"] == (
        "reuse_candidate"
    )
    assert records[
        "certificate_invalid_ready_quarantine_APP77_CERT310"
    ]["record_type"] == "quarantine"
    assert records[
        "certificate_external_submission_deadend_APP77_CERT310"
    ]["record_type"] == "deadend"
    assert report.drs_lifecycle["protocol_candidate_created"] is False
    assert report.drs_lifecycle["needle_candidate_created"] is False
    assert report.drs_lifecycle["installed_needle_created"] is False


def test_conflict_reports_flag_invalid_ready_and_accept_not_ready():
    reports = {
        row["conflict_report_id"]: row for row in _report().applied_conflict_reports
    }
    conflict = reports[
        "conflict_invalid_ready_vs_missing_expired_docs_APP77_CERT310"
    ]
    assert conflict["conflict_type"] == (
        "missing_or_expired_docs_vs_ready_certificate"
    )
    assert conflict["conflict_detected"] is True
    assert conflict["conflictcheck_is_authority"] is False
    assert reports["no_conflict_completed_not_ready_APP77_CERT310"][
        "conflict_detected"
    ] is False


def test_applied_audit_entry_hashes_applied_artifact():
    report = _report()
    entry = report.applied_audit_entry
    assert entry["audit_entry_id"] == "audit_applied_certificate_APP77_CERT310"
    assert entry["canonical_payload_hash"] == canonical_hash(report.applied_artifact)
    assert entry["previous_chain_last_entry_hash"] == report.audit_hash_chain[
        "previous_chain_last_entry_hash"
    ]
    assert entry["proof_only"] is True
    assert entry["production_persistence"] is False


def test_consistency_validator_rejects_wrong_audit_hash():
    report = _report()
    entry = deepcopy(report.applied_audit_entry)
    entry["canonical_payload_hash"] = "0" * 64
    assert validate_applied_certificate_report_consistency(
        replace(report, applied_audit_entry=entry)
    ) is False


def test_consistency_validator_rejects_missing_validation_row():
    report = _report()
    rows = [
        row
        for row in report.applied_validation_rows
        if row["result_proposal_id"] != "invalid_ready_certificate"
    ]
    assert validate_applied_certificate_report_consistency(
        replace(report, applied_validation_rows=rows)
    ) is False


def test_consistency_validator_rejects_missing_conflict_report():
    report = _report()
    rows = [
        row
        for row in report.applied_conflict_reports
        if row["conflict_type"] != "missing_or_expired_docs_vs_ready_certificate"
    ]
    assert validate_applied_certificate_report_consistency(
        replace(report, applied_conflict_reports=rows)
    ) is False


def test_malicious_claims_rejected_and_root_remains_authority():
    report = _report()
    assert all(report.malicious_unsafe_claims.values())
    assert report.authority_safety["root_remains_final_authority"] is True
    assert report.authority_safety["gt_remains_advisory_until_root"] is True
    assert report.authority_safety[
        "conflictcheck_remains_advisory_until_root"
    ] is True
    assert report.authority_safety["production_autonomy_claimed"] is False


def test_summary_pass_derives_from_explicit_artifacts_and_boundaries():
    summary = _report().summary
    assert summary["applied_certificate_readiness_demo_status"] == "PASS"
    assert summary["application_id"] == "APP-77"
    assert summary["certificate_request_id"] == "CERT-310"
    assert summary["certificate_readiness"] == "not_ready"
    assert summary["blocking_reasons"] == [
        "insurance_certificate expired",
        "payment_receipt missing",
    ]
    assert summary["invalid_ready_certificate_rejected"] is True
    assert summary["no_external_submission_executed"] is True
    assert summary["protocol_candidate_created"] is False
    assert summary["needle_candidate_created"] is False
    assert summary["applied_audit_entry_created"] is True
    assert summary["explicit_applied_artifacts_consistent"] is True
    assert summary["ready_for_applied_certificate_docs_sync"] is True
    assert summary["production_autonomy_claimed"] is False
