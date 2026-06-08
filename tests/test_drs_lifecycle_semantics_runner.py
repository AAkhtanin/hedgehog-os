from __future__ import annotations

from demo.run_drs_lifecycle_semantics import (
    RECORD_SCENARIOS,
    SUPPORTED_STAGES,
    SUPPORTED_STATUSES,
    collect_drs_lifecycle_semantics,
    run_drs_lifecycle_semantics,
)


def _report():
    return collect_drs_lifecycle_semantics()


def _records():
    return {row["scenario"]: row for row in _report().lifecycle_records}


def test_runner_contains_required_sections():
    output = run_drs_lifecycle_semantics()
    for heading in (
        "[DRS LIFECYCLE SEMANTICS]",
        "[SOURCE EXPERIENCE TYPES]",
        "[LIFECYCLE RECORDS]",
        "[PROMOTION LADDER]",
        "[QUARANTINE / DEADENDS]",
        "[TRUST / TTL]",
        "[MALICIOUS CLAIMS]",
        "[AUTHORITY / SAFETY]",
        "[SUMMARY]",
    ):
        assert heading in output


def test_current_proof_collectors_are_consumed_without_live_network():
    report = _report()
    sources = report.source_experience_types
    assert set(sources["collectors_consumed"]) == {
        "collect_drs_writeback_from_root_final",
        "collect_root_native_sandbox_needleruntime_e2e",
        "collect_fractal_cell_runtime",
        "collect_live_child_executor_in_fractal_cell",
    }
    assert sources["source_drs_writeback_status"] == "PASS"
    assert sources["source_needleruntime_status"] == "PASS"
    assert sources["source_fractal_cell_status"] == "PASS"
    assert sources["source_live_child_reference_status"] in {
        "PASS",
        "SAFE_FALLBACK_NOT_LIVE_SUCCESS",
    }
    assert report.input_mode["live_network_used"] is False


def test_root_final_and_completed_needle_experiences_are_pointer_first():
    records = _records()
    root = records["root_final_completed_experience"]
    needle = records["sandbox_needle_completed_experience"]
    assert root["source_artifact_type"] == "DRSWritebackAuditRecord"
    assert root["status"] == "completed"
    assert "source_root_final_artifact_ref" in root["artifact_pointers"]
    assert needle["source_artifact_type"] == "NeedleExecutionResult"
    assert needle["status"] == "completed"
    assert needle["promotion_state"]["promotion_state"] == "reuse_candidate"
    assert needle["promotion_state"]["installed_needle"] is False


def test_needle_degraded_quarantine_blocked_and_failed_states_are_represented():
    records = _records()
    timeout = records["sandbox_needle_timeout_degraded_experience"]
    invalid = records["sandbox_needle_invalid_json_quarantined_experience"]
    permission = records["sandbox_needle_permission_required_blocked_experience"]
    mismatch = records["sandbox_needle_contract_mismatch_failed_experience"]
    assert timeout["status"] == "degraded"
    assert timeout["ttl_state"]["ttl_class"] in {"short", "medium"}
    assert timeout["direct_reuse_allowed"] is False
    assert invalid["status"] == "quarantined"
    assert invalid["quarantine_state"]["quarantine_required"] is True
    assert invalid["quarantine_state"]["quarantine_layer"] == "local_quarantine"
    assert permission["status"] == "blocked"
    assert permission["permission_required"] is True
    assert permission["direct_reuse_allowed"] is False
    assert mismatch["status"] == "failed"


def test_child_cell_completed_degraded_and_deadend_experiences_are_represented():
    records = _records()
    completed = records["child_cell_completed_boundary_experience"]
    degraded = records["child_cell_degraded_budget_experience"]
    deadend = records["child_cell_blocked_max_depth_deadend_experience"]
    assert completed["source_artifact_type"] == "ChildBoundarySnapshot"
    assert completed["status"] == "completed"
    assert "source_child_boundary_snapshot_ref" in completed["artifact_pointers"]
    assert degraded["status"] == "degraded"
    assert "budget_limit_approached" in degraded["risks"]
    assert degraded["direct_reuse_allowed"] is False
    assert deadend["status"] == "deadend"
    assert deadend["deadend_state"]["deadend_marker"] is True
    assert deadend["deadend_state"]["deadend_reuse_blocked"] is True
    assert deadend["deadend_state"]["deadend_requires_root_override"] is True


def test_live_child_executor_experiences_are_represented_without_network():
    records = _records()
    completed = records["live_child_executor_completed_experience"]
    blocked = records["live_child_executor_action_like_blocked_experience"]
    assert completed["source_artifact_type"] == "ChildExecutionResult"
    assert completed["status"] == "completed"
    assert completed["automatic_protocol_template_created"] is False
    assert completed["promotion_state"]["installed_needle"] is False
    assert blocked["status"] == "rejected"
    assert blocked["action_like_request_detected"] is True
    assert blocked["real_external_action_executed"] is False
    assert blocked["direct_reuse_allowed"] is False
    assert _report().input_mode["live_network_used"] is False


def test_protocol_and_needle_candidates_are_not_installed():
    records = _records()
    protocol = records["repeated_success_protocol_candidate"]
    needle = records["draft_needle_candidate_with_root_policy"]
    assert protocol["lifecycle_stage"] == "protocol_candidate"
    assert protocol["promotion_state"]["repeated_validation_count"] >= protocol[
        "promotion_state"
    ]["repeated_validation_threshold"]
    assert protocol["promotion_state"]["installed_needle"] is False
    assert needle["lifecycle_stage"] == "needle_candidate"
    assert needle["promotion_state"]["policy_mode"] == "developer_local"
    assert needle["promotion_state"]["root_approval_required"] is True
    assert needle["promotion_state"]["sandbox_tests_required"] is True
    assert needle["promotion_state"]["manifest_required"] is True
    assert needle["promotion_state"]["permission_model_required"] is True
    assert needle["promotion_state"]["installed_needle"] is False


def test_promotion_ladder_blocks_automatic_needle_creation():
    ladder = _report().promotion_ladder
    assert ladder["experience_record_count"] == 11
    assert ladder["protocol_candidate_count"] == 1
    assert ladder["needle_candidate_count"] == 1
    assert ladder["installed_needle_count"] == 0
    assert set(ladder["supported_lifecycle_stages"]) == SUPPORTED_STAGES
    assert ladder["automatic_needle_creation_blocked"] is True
    assert ladder["root_approval_required_for_promotion"] is True
    assert ladder["repeated_validation_required_for_strict_mode"] is True


def test_malicious_authority_install_and_persistence_claims_are_rejected():
    malicious = _report().malicious_claims
    assert malicious["malicious_installed_needle_claim_rejected"] is True
    assert malicious["malicious_drs_authority_claim_rejected"] is True
    assert malicious["malicious_global_drs_write_claim_rejected"] is True
    assert malicious["malicious_external_drs_network_claim_rejected"] is True
    assert malicious["malicious_production_persistence_claim_rejected"] is True
    assert malicious["installed_needle"] is False
    assert malicious["drs_is_authority"] is False
    assert malicious["production_persistence"] is False


def test_quarantine_and_deadend_release_require_root():
    section = _report().quarantine_deadends
    assert section["quarantined_records"]
    assert section["deadend_records"]
    assert section["direct_reuse_blocked_records"]
    assert section["quarantine_release_requires_root"] is True
    assert section["deadend_override_requires_root"] is True


def test_trust_ttl_are_advisory_and_conflict_check_is_deferred():
    section = _report().trust_ttl
    assert section["completed_records"] >= 1
    assert section["degraded_records"] >= 1
    assert section["blocked_records"] >= 1
    assert section["failed_records"] >= 1
    assert section["ttl_advisory_only"] is True
    assert section["trust_update_advisory_only"] is True
    assert section["conflict_status_default"] == "not_checked"
    assert section["conflict_check_next_layer"] is True


def test_all_records_are_root_authorized_local_proof_pointer_records():
    for record in _report().lifecycle_records:
        assert record["created_by"] == "root_authorized_lifecycle_adapter"
        assert record["root_authorized"] is True
        assert record["drs_is_authority"] is False
        assert record["production_persistence"] is False
        assert record["global_drs_write"] is False
        assert record["external_drs_network_write"] is False
        assert record["artifact_pointers"]
        assert record["provenance"]["proof_only"] is True


def test_authority_and_safety_boundaries():
    authority = _report().authority_safety
    assert authority["drs_lifecycle_is_authority"] is False
    assert authority["drs_is_full_memory"] is False
    assert authority["drs_is_vector_store"] is False
    assert authority["drs_is_automatic_needle_factory"] is False
    assert authority["root_remains_commit_authority"] is True
    assert authority["lifecycle_records_are_local_only"] is True
    assert authority["lifecycle_records_are_proof_level"] is True
    assert authority["production_persistence_claimed"] is False
    assert authority["global_drs_implemented"] is False
    assert authority["external_drs_network_implemented"] is False
    assert authority["production_external_action_executed"] is False
    assert authority["marennya_invoked"] is False
    assert authority["up_invoked"] is False


def test_required_statuses_and_stages_are_represented():
    report = _report()
    assert set(report.summary["statuses_represented"]) == SUPPORTED_STATUSES
    assert set(report.summary["lifecycle_stages_represented"]) == SUPPORTED_STAGES
    assert {row["scenario"] for row in report.lifecycle_records} == set(
        RECORD_SCENARIOS
    )


def test_pass_summary_is_derived_from_records_promotion_and_authority():
    summary = _report().summary
    assert summary["drs_lifecycle_semantics_status"] == "PASS"
    assert summary["records_created"] == len(RECORD_SCENARIOS) == 13
    assert summary["promotion_ladder_represented"] is True
    assert summary["automatic_needle_creation_blocked"] is True
    assert summary["malicious_claims_rejected"] == 5
    assert summary["quarantine_and_deadends_represented"] is True
    assert summary["trust_ttl_advisory_represented"] is True
    assert summary["conflict_check_deferred_to_next_layer"] is True
    assert summary["root_remains_commit_authority"] is True
    assert summary["local_proof_level_only"] is True
    assert summary["ready_for_conflictcheck_v0_1"] is True
    assert summary["production_autonomy_claimed"] is False
