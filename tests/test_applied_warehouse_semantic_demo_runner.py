from __future__ import annotations

from copy import deepcopy
from dataclasses import replace

from demo.run_audit_hash_chain import canonical_hash
from demo.run_applied_warehouse_semantic_demo import (
    CURRENT_STOCK,
    REQUESTED_ITEMS,
    collect_applied_warehouse_semantic_demo,
    run_applied_warehouse_semantic_demo,
    validate_applied_report_consistency,
)


def _report():
    return collect_applied_warehouse_semantic_demo()


def _proposals():
    return {row["result_proposal_id"]: row for row in _report().result_proposals}


def test_runner_contains_all_required_sections():
    output = run_applied_warehouse_semantic_demo()
    for heading in (
        "[APPLIED WAREHOUSE SEMANTIC DEMO]",
        "[INPUT / MODE]",
        "[USER EVENT]",
        "[WORLDSTATE]",
        "[DRS RETRIEVAL]",
        "[CONTROLLED ROUTE ASSEMBLY]",
        "[MATRIX GATE / ROUTE GATE]",
        "[AVF / ATTRACTOR PACKET]",
        "[APPLIED PLAN GRAPH]",
        "[ARCHITECT / PLAN]",
        "[APPLIED NODE RESULTS]",
        "[DAG / EXECUTION]",
        "[NEEDLERUNTIME / CHILD CELL]",
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
    assert mode["mode"] == "deterministic_applied_warehouse_semantic_demo"
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


def test_user_event_identifies_warehouse_dispatch_and_proof_certificate():
    event = _report().user_event
    assert event["warehouse_id"] == "W-17"
    assert event["dispatch_id"] == "D-2042"
    assert event["requested_certificate_type"] == "inventory_readiness_certificate"
    assert "Do not contact external services" in event["user_task"]
    assert event["proof_only"] is True


def test_worldstate_is_structured_local_fixture_with_exact_stock():
    world = _report().worldstate
    assert world["requested_items"] == REQUESTED_ITEMS
    assert world["current_stock"] == CURRENT_STOCK
    assert world["blocked_items"] == {"water_filter": "short_by_2"}
    assert world["freshness_status"] == "current_for_demo"
    assert world["worldstate_assembled"] is True
    assert world["worldstate_source"] == "deterministic_local_fixture"
    assert world["no_external_api_used"] is True


def test_local_drs_context_contains_success_deadend_conflict_and_reuse_patterns():
    drs = _report().drs_retrieval
    assert drs["drs_retrieval_requested"] is True
    assert drs["drs_retrieval_scope"] == "local_proof_only"
    assert drs["retrieved_records_count"] == 4
    assert drs["retrieved_context_applied"] is True
    assert set(drs["retrieved_context_types"]) == {
        "previous_successful_inventory_certificate_pattern",
        "previous_deadend_external_dispatch_without_confirmation",
        "previous_conflict_short_stock_vs_ready_certificate",
        "previous_reuse_candidate_local_stock_readiness_template",
    }
    assert drs["no_global_drs_used"] is True
    assert drs["no_external_drs_network_used"] is True


def test_controlled_route_assembly_is_consumed_and_bounded():
    route = _report().controlled_route_assembly
    assert route["controlled_route_assembly_source_status"] == "PASS"
    assert route["orchestrator_has_bounded_delegated_authority"] is True
    assert route["orchestrator_can_propose_route"] is True
    assert route["orchestrator_can_assemble_worldstate"] is True
    assert route["orchestrator_can_request_drs_retrieval"] is True
    assert route["orchestrator_can_propose_candidate_vectors"] is True
    assert route["orchestrator_can_propose_guard_set"] is True
    assert route["orchestrator_can_propose_attractor_packet_draft"] is True
    assert route["orchestrator_proposes_avf_inputs"] is True
    assert route["orchestrator_manages_avf"] is False
    assert route["orchestrator_is_root"] is False
    assert route["orchestrator_writes_drs"] is False
    assert route["orchestrator_creates_final_output"] is False
    assert route["orchestrator_executes_actions"] is False
    assert route["orchestrator_calls_needles_directly"] is False


def test_matrix_route_gate_blocks_false_ready_and_external_action():
    gate = _report().matrix_route_gate
    assert gate["root_validates_orchestrator_proposal"] is True
    assert gate["matrix_gate_after_orchestrator"] is True
    assert gate["route_gate_after_orchestrator"] is True
    assert gate["policy_constraints_applied"] is True
    assert gate["no_external_action_allowed"] is True
    assert gate["forbidden_ready_certificate_blocked_if_stock_short"] is True
    assert gate["permission_required_for_real_dispatch"] is True
    assert gate["proposal_allowed_to_avf"] is True


def test_avf_preserves_shortage_and_blocks_false_ready_and_external_dispatch():
    avf = _report().avf_attractor_packet
    assert avf["avf_source_status"] == "PASS"
    assert avf["avf_after_matrix_gate"] is True
    assert avf["avf_independent_filter_scoring_layer"] is True
    assert avf["hardmask_beats_orchestrator_confidence"] is True
    assert avf["stock_shortage_vector_preserved"] is True
    assert avf["false_ready_vector_blocked"] is True
    assert avf["no_external_dispatch_vector_blocked"] is True
    assert avf["attractor_packet_created"] is True
    assert avf["attractor_packet_contains_worldstate"] is True
    assert avf["attractor_packet_contains_drs_context"] is True


def test_architect_receives_bounded_packet_and_builds_required_plan_nodes():
    architect = _report().architect_plan
    assert architect["architect_source_status"] == "PASS"
    assert architect["architect_receives_bounded_attractor_packet"] is True
    assert architect["architect_receives_raw_user_text"] is False
    assert architect["plan_graph_created"] is True
    assert architect["plan_graph_contains_stock_check_node"] is True
    assert architect["plan_graph_contains_missing_items_node"] is True
    assert architect["plan_graph_contains_certificate_draft_node"] is True
    assert architect["plan_graph_contains_no_external_action_guard"] is True
    assert architect["plan_graph_contract_valid"] is True


def test_applied_plan_graph_has_required_nodes_and_edges():
    graph = _report().applied_plan_graph
    assert graph["plan_graph_id"] == "applied_warehouse_plan_graph_W17_D2042"
    assert graph["source"] == "bounded_attractor_packet"
    assert graph["raw_user_text_received"] is False
    assert {node["node_id"] for node in graph["nodes"]} == {
        "stock_check_node",
        "missing_items_node",
        "certificate_draft_node",
        "no_external_action_guard_node",
    }
    assert {(edge["from"], edge["to"]) for edge in graph["edges"]} == {
        ("stock_check_node", "missing_items_node"),
        ("missing_items_node", "certificate_draft_node"),
        ("no_external_action_guard_node", "certificate_draft_node"),
    }
    assert graph["contract_valid"] is True


def test_applied_node_results_explicitly_prove_shortage_and_not_ready_draft():
    results = _report().applied_node_results
    assert results["stock_check_result"]["water_filter"] == "short_by_2"
    assert results["stock_check_result"]["battery_pack"] == "surplus_3"
    assert results["missing_items_result"] == {"water_filter": 2}
    assert results["certificate_draft_result"] == {
        "dispatch_readiness": "not_ready",
        "blocking_reason": "water_filter short by 2",
    }
    assert results["no_external_action_guard_result"] == {
        "no_external_action_executed": True,
        "real_dispatch_blocked": True,
    }


def test_dag_executes_bounded_plan_and_blocks_false_ready():
    dag = _report().dag_execution
    assert dag["dag_source_status"] == "PASS"
    assert dag["executor_receives_plan_graph_not_raw_user_text"] is True
    assert dag["stock_check_completed"] is True
    assert dag["missing_items_detected"] is True
    assert dag["false_ready_result_blocked"] is True
    assert dag["no_real_dispatch_executed"] is True
    assert dag["node_results_created"] >= 3


def test_needleruntime_and_child_cell_remain_bounded_non_authorities():
    boundary = _report().needleruntime_child_cell
    assert boundary["needleruntime_source_status"] == "PASS"
    assert boundary["fractal_cell_source_status"] == "PASS"
    assert boundary["live_child_reference_status"] in {
        "PASS",
        "SAFE_FALLBACK_NOT_LIVE_SUCCESS",
    }
    assert boundary["needleruntime_reached_only_through_root_approved_plan_graph"] is True
    assert boundary["sandbox_needle_used_for_local_inventory_check"] is True
    assert boundary["child_cell_used_for_non_atomic_reconciliation"] is True
    assert boundary["child_cell_bounded"] is True
    assert boundary["child_cell_is_root"] is False
    assert boundary["no_child_final_output"] is True
    assert boundary["no_direct_needle_call_by_orchestrator"] is True
    assert boundary["live_child_executor_reference_mode_only"] is True
    assert boundary["live_network_used"] is False


def test_three_semantic_result_proposals_preserve_safe_and_unsafe_branches():
    proposals = _proposals()
    completed = proposals["completed_not_ready_certificate"]
    invalid = proposals["invalid_ready_certificate"]
    needs_user = proposals["needs_user_restock_confirmation"]
    assert completed["status"] == "completed"
    assert completed["dispatch_readiness"] == "not_ready"
    assert completed["missing_items"] == {"water_filter": 2}
    assert completed["safe_for_root_final"] is True
    assert invalid["status"] == "rejected"
    assert invalid["dispatch_readiness"] == "ready"
    assert invalid["safe_for_root_final"] is False
    assert needs_user["status"] == "needs_user"
    assert needs_user["safe_for_root_final"] is True


def test_post_vv_accepts_safe_branches_and_rejects_invalid_ready():
    post = _report().post_vv
    assert post["post_vv_source_status"] == "PASS"
    assert post["post_vv_reached"] is True
    assert post["completed_not_ready_certificate_valid"] is True
    assert post["invalid_ready_certificate_rejected"] is True
    assert post["needs_user_restock_confirmation_valid"] is True
    for key in (
        "schema_valid",
        "evidence_valid",
        "policy_valid",
        "time_valid",
        "safety_valid",
        "consistency_valid",
    ):
        assert post[key] is True


def test_applied_validation_rows_preserve_accepted_rejected_and_needs_user():
    rows = {
        row["result_proposal_id"]: row for row in _report().applied_validation_rows
    }
    assert rows["completed_not_ready_certificate"]["validation_status"] == "accepted"
    assert rows["invalid_ready_certificate"]["validation_status"] == "rejected"
    assert rows["invalid_ready_certificate"]["consistency_valid"] is False
    assert (
        rows["invalid_ready_certificate"]["reason"]
        == "contradicts water_filter short_by_2"
    )
    assert (
        rows["needs_user_restock_confirmation"]["validation_status"]
        == "needs_user_valid"
    )


def test_gt_selects_not_ready_and_preserves_needs_user_secondary():
    gt = _report().gt
    assert gt["gt_source_status"] == "PASS"
    assert gt["gt_reached"] is True
    assert gt["gt_is_not_truth_proof"] is True
    assert gt["gt_selects_completed_not_ready_over_invalid_ready"] is True
    assert gt["gt_preserves_needs_user_as_secondary"] is True
    assert gt["selected_result_proposal_id"] == "completed_not_ready_certificate"
    assert gt["rejected_result_proposal_ids"] == ["invalid_ready_certificate"]


def test_applied_gt_selection_selects_safe_result_and_rejects_invalid_ready():
    selection = _report().applied_gt_selection
    assert (
        selection["selected_result_proposal_id"]
        == "completed_not_ready_certificate"
    )
    assert (
        selection["secondary_result_proposal_id"]
        == "needs_user_restock_confirmation"
    )
    assert selection["rejected_result_proposal_ids"] == [
        "invalid_ready_certificate"
    ]
    assert selection["gt_is_not_truth_proof"] is True


def test_root_final_reports_not_ready_shortage_and_no_action():
    final = _report().root_final
    assert final["root_final_source_status"] == "PASS"
    assert final["root_final_created"] is True
    assert final["root_created_final_output"] is True
    assert final["root_is_only_final_output_authority"] is True
    assert final["final_status"] == "completed"
    assert final["dispatch_readiness"] == "not_ready"
    assert final["blocking_reason"] == "water_filter short by 2"
    assert final["ready_items"] == ["med_kit", "battery_pack", "thermal_blanket"]
    assert final["missing_items"] == {"water_filter": 2}
    assert "restock / delay dispatch" in final["recommended_next_step"]
    assert final["no_external_action_executed"] is True
    assert final["proof_level_certificate_only"] is True


def test_drs_lifecycle_records_safe_reuse_quarantine_and_deadend_semantics():
    lifecycle = _report().drs_lifecycle
    assert lifecycle["drs_lifecycle_source_status"] == "PASS"
    assert lifecycle["drs_lifecycle_after_root_final"] is True
    assert lifecycle["experience_record_created"] is True
    assert lifecycle["experience_status"] == "completed_not_ready"
    assert lifecycle["lifecycle_stage"] == "experience_record"
    assert lifecycle["reuse_candidate_created"] is True
    assert lifecycle["protocol_candidate_created"] is False
    assert lifecycle["needle_candidate_created"] is False
    assert lifecycle["installed_needle_created"] is False
    assert lifecycle["work_record_allowed"] is True
    assert lifecycle["quarantine_record_created_for_invalid_ready_certificate"] is True
    assert lifecycle["deadend_record_created_for_external_dispatch_without_confirmation"] is True
    assert lifecycle["root_authorized_writeback"] is True
    assert lifecycle["orchestrator_writes_drs"] is False


def test_applied_lifecycle_records_have_exact_types_and_source_links():
    records = {
        row["record_id"]: row for row in _report().applied_drs_lifecycle_records
    }
    assert records["warehouse_experience_record_W17_D2042"]["record_type"] == (
        "experience_record"
    )
    assert records["warehouse_reuse_candidate_W17_D2042"]["record_type"] == (
        "reuse_candidate"
    )
    quarantine = records["warehouse_invalid_ready_quarantine_W17_D2042"]
    assert quarantine["record_type"] == "quarantine"
    assert quarantine["source_result_proposal_id"] == "invalid_ready_certificate"
    deadend = records["warehouse_external_dispatch_deadend_W17_D2042"]
    assert deadend["record_type"] == "deadend"
    assert "external dispatch without operator confirmation" in deadend[
        "deadend_reason"
    ]


def test_conflictcheck_flags_invalid_ready_but_not_completed_not_ready():
    conflict = _report().conflictcheck
    assert conflict["conflictcheck_source_status"] == "PASS"
    assert conflict["conflictcheck_after_drs_lifecycle"] is True
    assert conflict["conflict_short_stock_vs_ready_certificate_detected"] is True
    assert conflict["invalid_ready_certificate_conflict_flagged"] is True
    assert conflict["completed_not_ready_certificate_no_conflict"] is True
    assert conflict["root_review_required_for_conflict"] is True
    assert conflict["conflictcheck_is_authority"] is False


def test_applied_conflict_reports_include_conflict_and_compatible_no_conflict():
    reports = {
        row["conflict_report_id"]: row for row in _report().applied_conflict_reports
    }
    conflict = reports["conflict_invalid_ready_vs_short_stock_W17_D2042"]
    assert conflict["conflict_type"] == "short_stock_vs_ready_certificate"
    assert conflict["conflict_detected"] is True
    assert conflict["root_review_required"] is True
    compatible = reports["no_conflict_completed_not_ready_W17_D2042"]
    assert compatible["conflict_type"] == "no_conflict"
    assert compatible["conflict_detected"] is False


def test_audit_hash_chain_follows_conflictcheck_and_proves_continuity_not_truth():
    audit = _report().audit_hash_chain
    assert audit["audit_hash_chain_source_status"] == "PASS"
    assert audit["audit_hash_chain_after_conflictcheck"] is True
    assert audit["hash_chain_proves_continuity_not_truth"] is True
    assert len(audit["applied_demo_artifact_hash"]) == 64
    assert audit["applied_audit_entry_created"] is True
    assert audit["applied_demo_artifact_hash_linked"] is True
    assert audit["source_artifacts_unchanged"] is True
    assert audit["production_persistence"] is False


def test_applied_audit_entry_hashes_the_explicit_applied_artifact():
    report = _report()
    entry = report.applied_audit_entry
    assert entry["audit_entry_id"] == "audit_applied_warehouse_W17_D2042"
    assert entry["canonical_payload_hash"] == canonical_hash(report.applied_artifact)
    assert (
        entry["previous_chain_last_entry_hash"]
        == report.audit_hash_chain["previous_chain_last_entry_hash"]
    )
    assert report.audit_hash_chain["applied_demo_artifact_hash_linked"] is (
        entry["canonical_payload_hash"] == canonical_hash(report.applied_artifact)
    )


def test_consistency_validator_rejects_wrong_applied_audit_hash():
    report = _report()
    entry = deepcopy(report.applied_audit_entry)
    entry["canonical_payload_hash"] = "0" * 64
    assert validate_applied_report_consistency(
        replace(report, applied_audit_entry=entry)
    ) is False


def test_consistency_validator_rejects_missing_validation_row():
    report = _report()
    rows = [
        row
        for row in report.applied_validation_rows
        if row["result_proposal_id"] != "invalid_ready_certificate"
    ]
    assert validate_applied_report_consistency(
        replace(report, applied_validation_rows=rows)
    ) is False


def test_consistency_validator_rejects_missing_conflict_report():
    report = _report()
    reports = [
        row
        for row in report.applied_conflict_reports
        if row["conflict_type"] != "short_stock_vs_ready_certificate"
    ]
    assert validate_applied_report_consistency(
        replace(report, applied_conflict_reports=reports)
    ) is False


def test_all_malicious_unsafe_claims_are_rejected():
    malicious = _report().malicious_unsafe_claims
    assert len(malicious) == 15
    assert all(malicious.values())


def test_authority_safety_preserves_root_and_all_bounded_layers():
    authority = _report().authority_safety
    assert authority["root_sovereign"] is True
    assert authority["orchestrator_has_bounded_delegated_authority"] is True
    assert authority["orchestrator_is_root"] is False
    assert authority["orchestrator_creates_final_output"] is False
    assert authority["orchestrator_writes_drs"] is False
    assert authority["orchestrator_executes_actions"] is False
    assert authority["orchestrator_calls_needles_directly"] is False
    assert authority["avf_remains_independent"] is True
    assert authority["hardmask_remains_stronger_than_orchestrator_confidence"] is True
    assert authority["architect_receives_bounded_attractor_packet"] is True
    assert authority["executor_receives_plan_graph_not_raw_user_text"] is True
    assert authority["gt_remains_advisory_until_root"] is True
    assert authority["conflictcheck_remains_advisory_until_root"] is True
    assert authority["audit_hash_chain_proves_continuity_not_truth"] is True
    assert authority["root_remains_final_authority"] is True
    assert authority["production_autonomy_claimed"] is False


def test_summary_pass_derives_from_semantics_and_full_boundary_continuity():
    summary = _report().summary
    assert summary["applied_warehouse_semantic_demo_status"] == "PASS"
    assert summary["warehouse_id"] == "W-17"
    assert summary["dispatch_id"] == "D-2042"
    assert summary["dispatch_readiness"] == "not_ready"
    assert summary["blocking_reason"] == "water_filter short by 2"
    assert summary["scenarios_or_branches_verified"] == 3
    for key in (
        "worldstate_assembled",
        "drs_context_applied",
        "controlled_route_assembly_applied",
        "matrix_gate_passed",
        "avf_attractor_packet_created",
        "architect_plan_graph_created",
        "dag_execution_completed",
        "post_vv_reached",
        "gt_reached",
        "root_final_created",
        "drs_lifecycle_after_root_final",
        "conflictcheck_after_drs_lifecycle",
        "audit_hash_chain_after_conflictcheck",
        "root_remains_final_authority",
        "ready_for_applied_warehouse_docs_sync",
    ):
        assert summary[key] is True
    assert summary["malicious_claims_rejected"] == 15
    assert summary["explicit_applied_artifacts_consistent"] is True
    assert summary["production_autonomy_claimed"] is False
