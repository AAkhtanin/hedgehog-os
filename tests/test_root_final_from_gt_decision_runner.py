from __future__ import annotations

from demo.run_root_final_from_gt_decision import (
    collect_root_final_from_gt_decision,
    run_root_final_from_gt_decision,
)


def _filters_by_scenario():
    report = collect_root_final_from_gt_decision()
    return {row["scenario"]: row for row in report.root_final_input_filter}


def _artifacts_by_scenario():
    report = collect_root_final_from_gt_decision()
    return {row["scenario"]: row for row in report.root_final_artifacts}


def test_runner_output_contains_title():
    output = run_root_final_from_gt_decision()

    assert "[ROOT FINAL FROM GT DECISION]" in output
    assert "[INPUT GT DECISIONS]" in output
    assert "[ROOT FINAL INPUT FILTER]" in output
    assert "[ROOT FINAL ARTIFACTS]" in output
    assert "[CONTAINMENT]" in output
    assert "[AUTHORITY / SAFETY]" in output
    assert "[SUMMARY]" in output


def test_source_gt_proof_status_is_pass():
    report = collect_root_final_from_gt_decision()

    assert report.input_gt_decisions["source_gt_report_status"] == "PASS"
    assert report.summary["source_gt_status"] == "PASS"
    assert report.input_gt_decisions["accepted_gt_decisions"] == 1
    assert report.input_gt_decisions["degraded_gt_decisions"] == 1
    assert report.input_gt_decisions["rejected_gt_decisions"] == 5
    assert len(report.input_gt_decisions["gt_decisions_imported"]) == 7


def test_accept_gt_decision_creates_accepted_root_final_artifact():
    filter_row = _filters_by_scenario()["accept_gt_decision_root_final_accept"]
    artifact = _artifacts_by_scenario()["accept_gt_decision_root_final_accept"]

    assert filter_row["root_final_invoked"] is True
    assert filter_row["input_is_gt_decision"] is True
    assert artifact["created_by"] == "root_orchestrator"
    assert artifact["input_is_gt_decision"] is True
    assert artifact["gt_decision_schema_valid"] is True
    assert artifact["gt_decision_seen"] == "accept"
    assert artifact["root_final_status"] == "accepted"
    assert artifact["root_created_final_output"] is True
    assert artifact["gt_created_final_output"] is False
    assert artifact["root_writes_drs"] is False
    assert artifact["drs_writeback_invoked"] is False
    assert artifact["root_executes_actions"] is False


def test_degrade_gt_decision_creates_degraded_root_final_artifact():
    artifact = _artifacts_by_scenario()["degrade_gt_decision_root_final_degraded"]

    assert artifact["gt_decision_schema_valid"] is True
    assert artifact["gt_decision_seen"] == "degrade"
    assert artifact["root_final_status"] == "degraded"
    assert artifact["root_selection_reason"] == "gt_decision_degraded_by_root"
    assert "degraded" in artifact["user_facing_summary"]
    assert artifact["root_created_final_output"] is True
    assert artifact["drs_writeback_invoked"] is False


def test_reject_gt_decision_creates_rejected_root_final_artifact():
    artifact = _artifacts_by_scenario()["reject_gt_decision_root_final_rejected"]

    assert artifact["gt_decision_schema_valid"] is True
    assert artifact["gt_decision_seen"] == "reject"
    assert artifact["root_final_status"] == "rejected"
    assert artifact["root_selection_reason"] == "gt_decision_rejected_by_root"
    assert artifact["root_created_final_output"] is True
    assert artifact["root_writes_drs"] is False


def test_raw_validation_report_is_blocked():
    filter_row = _filters_by_scenario()["raw_validation_report_blocked"]

    assert filter_row["root_final_invoked"] is False
    assert filter_row["blocked_before_root_final"] is True
    assert "raw_validation_report_not_allowed" in filter_row["block_reasons"]


def test_raw_result_proposal_is_blocked():
    filter_row = _filters_by_scenario()["raw_result_proposal_blocked"]

    assert filter_row["root_final_invoked"] is False
    assert filter_row["blocked_before_root_final"] is True
    assert "raw_result_proposal_not_allowed" in filter_row["block_reasons"]


def test_raw_executor_text_is_blocked():
    filter_row = _filters_by_scenario()["raw_executor_text_blocked"]

    assert filter_row["root_final_invoked"] is False
    assert filter_row["blocked_before_root_final"] is True
    assert "raw_executor_text_not_allowed" in filter_row["block_reasons"]


def test_raw_architect_plan_graph_is_blocked():
    filter_row = _filters_by_scenario()["raw_architect_plan_graph_blocked"]

    assert filter_row["root_final_invoked"] is False
    assert filter_row["blocked_before_root_final"] is True
    assert "raw_architect_plan_graph_not_allowed" in filter_row["block_reasons"]


def test_raw_orchestrator_matrix_is_blocked():
    filter_row = _filters_by_scenario()["raw_orchestrator_matrix_blocked"]

    assert filter_row["root_final_invoked"] is False
    assert filter_row["blocked_before_root_final"] is True
    assert "raw_orchestrator_matrix_not_allowed" in filter_row["block_reasons"]


def test_raw_user_intent_is_blocked():
    filter_row = _filters_by_scenario()["raw_user_intent_blocked"]

    assert filter_row["root_final_invoked"] is False
    assert filter_row["blocked_before_root_final"] is True
    assert "raw_user_intent_not_allowed" in filter_row["block_reasons"]


def test_real_action_output_is_blocked():
    filter_row = _filters_by_scenario()["real_action_output_blocked"]

    assert filter_row["root_final_invoked"] is False
    assert filter_row["blocked_before_root_final"] is True
    assert "real_action_output_not_allowed" in filter_row["block_reasons"]


def test_malicious_gt_final_output_claim_is_rejected():
    artifact = _artifacts_by_scenario()[
        "malicious_gt_decision_claiming_final_output_rejected"
    ]

    assert artifact["root_final_status"] == "rejected"
    assert artifact["gt_final_output_claim_detected"] is True
    assert artifact["root_selection_reason"] == "gt_final_output_claim_rejected"
    assert artifact["root_created_final_output"] is True
    assert artifact["gt_created_final_output"] is False
    assert artifact["drs_writeback_invoked"] is False


def test_malicious_gt_drs_write_claim_is_rejected():
    artifact = _artifacts_by_scenario()[
        "malicious_gt_decision_claiming_drs_write_rejected"
    ]

    assert artifact["root_final_status"] == "rejected"
    assert artifact["gt_drs_write_claim_detected"] is True
    assert artifact["root_selection_reason"] == "gt_drs_write_claim_rejected"
    assert artifact["root_writes_drs"] is False
    assert artifact["drs_writeback_invoked"] is False


def test_malicious_gt_action_claim_is_rejected():
    artifact = _artifacts_by_scenario()[
        "malicious_gt_decision_claiming_action_rejected"
    ]

    assert artifact["root_final_status"] == "rejected"
    assert artifact["gt_action_claim_detected"] is True
    assert artifact["root_selection_reason"] == "gt_action_claim_rejected"
    assert artifact["root_executes_actions"] is False
    assert artifact["production_external_action_executed"] is False


def test_malformed_gt_decision_is_rejected():
    filter_row = _filters_by_scenario()["malformed_gt_decision_rejected"]
    artifact = _artifacts_by_scenario()["malformed_gt_decision_rejected"]

    assert filter_row["root_final_invoked"] is True
    assert filter_row["input_is_gt_decision"] is True
    assert artifact["gt_decision_schema_valid"] is False
    assert artifact["root_final_status"] == "rejected"
    assert artifact["root_selection_reason"] == "gt_decision_shape_invalid"
    assert artifact["root_created_final_output"] is True
    assert artifact["root_writes_drs"] is False
    assert artifact["drs_writeback_invoked"] is False


def test_root_final_receives_only_gt_decision():
    authority = collect_root_final_from_gt_decision().authority_safety

    assert authority["root_final_receives_only_gt_decision"] is True
    assert authority["root_receives_raw_validation_report"] is False
    assert authority["root_receives_raw_result_proposal"] is False
    assert authority["root_receives_raw_executor_text"] is False
    assert authority["root_receives_raw_architect_plan_graph"] is False
    assert authority["root_receives_raw_orchestrator_matrix"] is False
    assert authority["root_receives_raw_user_intent"] is False
    assert authority["root_receives_real_action_output"] is False


def test_root_is_only_final_output_authority():
    report = collect_root_final_from_gt_decision()

    assert report.authority_safety["root_is_only_final_output_authority"] is True
    assert report.authority_safety["root_created_final_output"] is True
    assert report.authority_safety["gt_created_final_output"] is False
    assert all(
        artifact["created_by"] == "root_orchestrator"
        for artifact in report.root_final_artifacts
    )


def test_gt_does_not_create_final_output():
    authority = collect_root_final_from_gt_decision().authority_safety

    assert authority["gt_created_final_output"] is False


def test_root_does_not_write_drs_in_this_layer():
    authority = collect_root_final_from_gt_decision().authority_safety

    assert authority["root_writes_drs"] is False


def test_drs_writeback_is_not_invoked():
    authority = collect_root_final_from_gt_decision().authority_safety

    assert authority["drs_writeback_invoked"] is False


def test_root_does_not_execute_actions():
    authority = collect_root_final_from_gt_decision().authority_safety

    assert authority["root_executes_actions"] is False


def test_no_production_external_actions_or_persistence():
    authority = collect_root_final_from_gt_decision().authority_safety

    assert authority["production_external_action_executed"] is False
    assert authority["production_persistence_claimed"] is False


def test_no_global_or_external_drs():
    authority = collect_root_final_from_gt_decision().authority_safety

    assert authority["global_drs_implemented"] is False
    assert authority["external_drs_network_implemented"] is False


def test_marennya_and_up_not_invoked():
    authority = collect_root_final_from_gt_decision().authority_safety

    assert authority["marennya_invoked"] is False
    assert authority["up_invoked"] is False


def test_pass_summary_derived_from_source_artifacts_blocks_and_boundaries():
    report = collect_root_final_from_gt_decision()
    expected_pass = (
        report.input_gt_decisions["source_gt_report_status"] == "PASS"
        and report.summary["scenarios_verified"] == len(report.root_final_input_filter)
        and report.summary["scenarios_verified"] == 14
        and report.summary["root_final_artifacts_created"]
        == len(report.root_final_artifacts)
        and report.summary["root_final_artifacts_created"] == 7
        and report.summary["accepted_root_final_artifacts"] == 1
        and report.summary["degraded_root_final_artifacts"] == 1
        and report.summary["rejected_root_final_artifacts"] == 5
        and report.summary["raw_validation_report_blocked"] is True
        and report.summary["raw_result_proposal_blocked"] is True
        and report.summary["raw_executor_text_blocked"] is True
        and report.summary["raw_architect_plan_graph_blocked"] is True
        and report.summary["raw_orchestrator_matrix_blocked"] is True
        and report.summary["raw_user_intent_blocked"] is True
        and report.summary["real_action_output_blocked"] is True
        and report.summary["malicious_gt_final_output_claim_rejected"] is True
        and report.summary["malicious_gt_drs_write_claim_rejected"] is True
        and report.summary["malicious_gt_action_claim_rejected"] is True
        and report.summary["malformed_gt_decision_rejected"] is True
        and report.authority_safety["root_final_receives_only_gt_decision"]
        and report.authority_safety["root_is_only_final_output_authority"]
        and not report.authority_safety["drs_writeback_invoked"]
        and not report.authority_safety["production_external_action_executed"]
        and not report.authority_safety["production_persistence_claimed"]
    )

    assert report.summary["root_final_from_gt_decision_status"] == "PASS"
    assert expected_pass is True
    assert report.summary["ready_for_full_canonical_chain_trace"] is True
