from __future__ import annotations

from demo.run_gt_from_validation_report import (
    collect_gt_from_validation_report,
    run_gt_from_validation_report,
)


def _filters_by_scenario():
    report = collect_gt_from_validation_report()
    return {row["scenario"]: row for row in report.gt_input_filter}


def _decisions_by_scenario():
    report = collect_gt_from_validation_report()
    return {row["scenario"]: row for row in report.gt_decisions}


def test_runner_output_contains_title():
    output = run_gt_from_validation_report()

    assert "[GT FROM VALIDATION REPORT]" in output
    assert "[INPUT VALIDATION REPORTS]" in output
    assert "[GT INPUT FILTER]" in output
    assert "[GT DECISIONS]" in output
    assert "[CONTAINMENT]" in output
    assert "[AUTHORITY / SAFETY]" in output
    assert "[SUMMARY]" in output


def test_source_post_vv_proof_status_is_pass():
    report = collect_gt_from_validation_report()

    assert report.input_validation_reports["source_post_vv_report_status"] == "PASS"
    assert report.summary["source_post_vv_status"] == "PASS"
    assert report.input_validation_reports["accepted_validation_reports"] == 1
    assert report.input_validation_reports["degraded_validation_reports"] == 1
    assert report.input_validation_reports["rejected_validation_reports"] == 3
    assert len(report.input_validation_reports["validation_reports_imported"]) == 5


def test_accepted_validation_report_creates_accept_gt_decision():
    filter_row = _filters_by_scenario()["accepted_validation_report_gt_accept"]
    decision = _decisions_by_scenario()["accepted_validation_report_gt_accept"]

    assert filter_row["gt_invoked"] is True
    assert filter_row["input_is_validation_report"] is True
    assert decision["created_by"] == "gt_validator"
    assert decision["input_is_validation_report"] is True
    assert decision["validation_report_schema_valid"] is True
    assert decision["validation_status_seen"] == "accepted"
    assert decision["gt_decision"] == "accept"
    assert decision["gt_creates_final_output"] is False
    assert decision["gt_writes_drs"] is False
    assert decision["gt_executes_actions"] is False
    assert decision["root_final_invoked"] is False


def test_degraded_validation_report_creates_degrade_gt_decision():
    decision = _decisions_by_scenario()["degraded_validation_report_gt_degrade"]

    assert decision["validation_report_schema_valid"] is True
    assert decision["validation_status_seen"] == "degraded"
    assert decision["gt_decision"] == "degrade"
    assert decision["selection_reason"] == "validation_report_degraded"
    assert "degraded_result_preserved" in decision["risk_basis"]
    assert "downgraded_claims_limit_executor_scope" in decision["risk_basis"]
    assert decision["gt_creates_final_output"] is False


def test_rejected_validation_report_creates_reject_gt_decision():
    decision = _decisions_by_scenario()["rejected_validation_report_gt_reject"]

    assert decision["validation_status_seen"] == "rejected"
    assert decision["gt_decision"] == "reject"
    assert decision["selection_reason"] == "validation_report_rejected"
    assert "malformed_result_proposal_rejected" in decision["risk_basis"]
    assert decision["gt_creates_final_output"] is False
    assert decision["root_final_invoked"] is False


def test_raw_result_proposal_is_blocked():
    filter_row = _filters_by_scenario()["raw_result_proposal_blocked"]

    assert filter_row["gt_invoked"] is False
    assert filter_row["blocked_before_gt"] is True
    assert "raw_result_proposal_not_allowed" in filter_row["block_reasons"]


def test_raw_executor_text_is_blocked():
    filter_row = _filters_by_scenario()["raw_executor_text_blocked"]

    assert filter_row["gt_invoked"] is False
    assert filter_row["blocked_before_gt"] is True
    assert "raw_executor_text_not_allowed" in filter_row["block_reasons"]


def test_raw_architect_plan_graph_is_blocked():
    filter_row = _filters_by_scenario()["raw_architect_plan_graph_blocked"]

    assert filter_row["gt_invoked"] is False
    assert filter_row["blocked_before_gt"] is True
    assert "raw_architect_plan_graph_not_allowed" in filter_row["block_reasons"]


def test_raw_orchestrator_matrix_is_blocked():
    filter_row = _filters_by_scenario()["raw_orchestrator_matrix_blocked"]

    assert filter_row["gt_invoked"] is False
    assert filter_row["blocked_before_gt"] is True
    assert "raw_orchestrator_matrix_not_allowed" in filter_row["block_reasons"]


def test_raw_user_intent_is_blocked():
    filter_row = _filters_by_scenario()["raw_user_intent_blocked"]

    assert filter_row["gt_invoked"] is False
    assert filter_row["blocked_before_gt"] is True
    assert "raw_user_intent_not_allowed" in filter_row["block_reasons"]


def test_real_action_output_is_blocked():
    filter_row = _filters_by_scenario()["real_action_output_blocked"]

    assert filter_row["gt_invoked"] is False
    assert filter_row["blocked_before_gt"] is True
    assert "real_action_output_not_allowed" in filter_row["block_reasons"]


def test_malicious_final_output_claim_is_rejected():
    decision = _decisions_by_scenario()[
        "malicious_validation_report_claiming_final_output_rejected"
    ]

    assert decision["gt_decision"] == "reject"
    assert decision["final_output_claim_detected"] is True
    assert decision["selection_reason"] == "final_output_claim_rejected"
    assert decision["gt_creates_final_output"] is False
    assert decision["root_final_invoked"] is False


def test_malicious_drs_write_claim_is_rejected():
    decision = _decisions_by_scenario()[
        "malicious_validation_report_claiming_drs_write_rejected"
    ]

    assert decision["gt_decision"] == "reject"
    assert decision["drs_write_claim_detected"] is True
    assert decision["selection_reason"] == "drs_write_claim_rejected"
    assert decision["gt_writes_drs"] is False
    assert decision["root_final_invoked"] is False


def test_malicious_action_claim_is_rejected():
    decision = _decisions_by_scenario()[
        "malicious_validation_report_claiming_action_rejected"
    ]

    assert decision["gt_decision"] == "reject"
    assert decision["action_claim_detected"] is True
    assert decision["selection_reason"] == "action_claim_rejected"
    assert decision["gt_executes_actions"] is False
    assert decision["gt_creates_final_output"] is False
    assert decision["gt_writes_drs"] is False
    assert decision["root_final_invoked"] is False


def test_malformed_validation_report_is_rejected():
    filter_row = _filters_by_scenario()["malformed_validation_report_rejected"]
    decision = _decisions_by_scenario()["malformed_validation_report_rejected"]

    assert filter_row["gt_invoked"] is True
    assert filter_row["input_is_validation_report"] is True
    assert decision["validation_report_schema_valid"] is False
    assert decision["gt_decision"] == "reject"
    assert decision["selection_reason"] == "validation_report_shape_invalid"
    assert "invalid_validation_findings_shape" in decision["risk_basis"]
    assert "invalid_validation_risks_shape" in decision["risk_basis"]
    assert decision["gt_creates_final_output"] is False
    assert decision["gt_writes_drs"] is False
    assert decision["root_final_invoked"] is False


def test_gt_receives_only_validation_report():
    authority = collect_gt_from_validation_report().authority_safety

    assert authority["gt_receives_only_validation_report"] is True
    assert authority["gt_receives_raw_result_proposal"] is False
    assert authority["gt_receives_raw_executor_text"] is False
    assert authority["gt_receives_raw_architect_plan_graph"] is False
    assert authority["gt_receives_raw_orchestrator_matrix"] is False
    assert authority["gt_receives_raw_user_intent"] is False
    assert authority["gt_receives_real_action_output"] is False


def test_gt_decision_only():
    report = collect_gt_from_validation_report()

    assert report.authority_safety["gt_decision_only"] is True
    assert all(row["created_by"] == "gt_validator" for row in report.gt_decisions)


def test_gt_does_not_create_final_output():
    authority = collect_gt_from_validation_report().authority_safety

    assert authority["gt_creates_final_output"] is False
    assert authority["production_final_output_created"] is False


def test_gt_does_not_write_drs():
    authority = collect_gt_from_validation_report().authority_safety

    assert authority["gt_writes_drs"] is False


def test_gt_does_not_execute_actions():
    authority = collect_gt_from_validation_report().authority_safety

    assert authority["gt_executes_actions"] is False


def test_root_final_is_not_invoked():
    authority = collect_gt_from_validation_report().authority_safety

    assert authority["root_final_invoked"] is False


def test_no_production_external_actions():
    authority = collect_gt_from_validation_report().authority_safety

    assert authority["production_external_action_executed"] is False


def test_no_global_or_external_drs():
    authority = collect_gt_from_validation_report().authority_safety

    assert authority["global_drs_implemented"] is False
    assert authority["external_drs_network_implemented"] is False


def test_marennya_and_up_not_invoked():
    authority = collect_gt_from_validation_report().authority_safety

    assert authority["marennya_invoked"] is False
    assert authority["up_invoked"] is False


def test_pass_summary_derived_from_source_reports_decisions_blocks_and_boundaries():
    report = collect_gt_from_validation_report()
    expected_pass = (
        report.input_validation_reports["source_post_vv_report_status"] == "PASS"
        and report.summary["scenarios_verified"] == len(report.gt_input_filter)
        and report.summary["scenarios_verified"] == 13
        and report.summary["gt_decisions_created"] == len(report.gt_decisions)
        and report.summary["gt_decisions_created"] == 7
        and report.summary["accepted_gt_decisions"] == 1
        and report.summary["degraded_gt_decisions"] == 1
        and report.summary["rejected_gt_decisions"] == 5
        and report.summary["raw_result_proposal_blocked"] is True
        and report.summary["raw_executor_text_blocked"] is True
        and report.summary["raw_architect_plan_graph_blocked"] is True
        and report.summary["raw_orchestrator_matrix_blocked"] is True
        and report.summary["raw_user_intent_blocked"] is True
        and report.summary["real_action_output_blocked"] is True
        and report.summary["malicious_final_output_claim_rejected"] is True
        and report.summary["malicious_drs_write_claim_rejected"] is True
        and report.summary["malicious_action_claim_rejected"] is True
        and report.summary["malformed_validation_report_rejected"] is True
        and report.authority_safety["gt_receives_only_validation_report"]
        and report.authority_safety["gt_decision_only"]
        and not report.authority_safety["root_final_invoked"]
        and not report.authority_safety["production_final_output_created"]
        and not report.authority_safety["production_external_action_executed"]
    )

    assert report.summary["gt_from_validation_report_status"] == "PASS"
    assert expected_pass is True
    assert report.summary["ready_for_root_final_from_gt_decision"] is True
