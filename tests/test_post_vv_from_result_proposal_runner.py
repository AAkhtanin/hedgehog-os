from __future__ import annotations

from demo.run_post_vv_from_result_proposal import (
    collect_post_vv_from_result_proposal,
    run_post_vv_from_result_proposal,
)


def _filters_by_scenario():
    report = collect_post_vv_from_result_proposal()
    return {row["scenario"]: row for row in report.post_vv_input_filter}


def _reports_by_scenario():
    report = collect_post_vv_from_result_proposal()
    return {row["scenario"]: row for row in report.validation_reports}


def test_runner_output_contains_title():
    output = run_post_vv_from_result_proposal()

    assert "[POST V&V FROM RESULT PROPOSAL]" in output
    assert "[INPUT RESULT PROPOSALS]" in output
    assert "[POST V&V INPUT FILTER]" in output
    assert "[VALIDATION REPORTS]" in output
    assert "[CONTAINMENT]" in output
    assert "[AUTHORITY / SAFETY]" in output
    assert "[SUMMARY]" in output


def test_source_dag_executor_proof_status_is_pass():
    report = collect_post_vv_from_result_proposal()

    assert report.input_result_proposals["source_dag_executor_report_status"] == "PASS"
    assert report.summary["source_dag_executor_status"] == "PASS"
    assert report.input_result_proposals["accepted_plan_result_proposals"] == 1
    assert report.input_result_proposals["downgraded_plan_result_proposals"] == 1
    assert len(report.input_result_proposals["result_proposals_imported"]) == 2


def test_completed_result_proposal_creates_accepted_validation_report():
    filter_row = _filters_by_scenario()["completed_result_proposal_validated"]
    validation_report = _reports_by_scenario()["completed_result_proposal_validated"]

    assert filter_row["post_vv_invoked"] is True
    assert filter_row["input_is_result_proposal"] is True
    assert validation_report["created_by"] == "post_vv"
    assert validation_report["result_proposal_schema_valid"] is True
    assert validation_report["node_results_checked"] is True
    assert validation_report["evidence_checked"] is True
    assert validation_report["risks_checked"] is True
    assert validation_report["validation_status"] == "accepted"
    assert validation_report["post_vv_creates_final_output"] is False
    assert validation_report["post_vv_writes_drs"] is False
    assert validation_report["gt_invoked"] is False


def test_degraded_result_proposal_creates_degraded_validation_report():
    validation_report = _reports_by_scenario()[
        "degraded_result_proposal_validated_as_degraded"
    ]

    assert validation_report["validation_status"] == "degraded"
    assert validation_report["result_status"] == "degraded"
    assert "degraded_result_preserved" in validation_report["validation_findings"]
    assert "downgraded_claims_limit_executor_scope" in validation_report["validation_risks"]
    assert "missing_guard:ReuseGate boundary" in validation_report["downgraded_claims_visible"]
    assert validation_report["post_vv_creates_final_output"] is False


def test_raw_executor_text_is_blocked():
    filter_row = _filters_by_scenario()["raw_executor_text_blocked"]

    assert filter_row["post_vv_invoked"] is False
    assert filter_row["blocked_before_post_vv"] is True
    assert "raw_executor_text_not_allowed" in filter_row["block_reasons"]


def test_raw_architect_plan_graph_is_blocked():
    filter_row = _filters_by_scenario()["raw_architect_plan_graph_blocked"]

    assert filter_row["post_vv_invoked"] is False
    assert filter_row["blocked_before_post_vv"] is True
    assert "raw_architect_plan_graph_not_allowed" in filter_row["block_reasons"]


def test_raw_orchestrator_matrix_is_blocked():
    filter_row = _filters_by_scenario()["raw_orchestrator_matrix_blocked"]

    assert filter_row["post_vv_invoked"] is False
    assert filter_row["blocked_before_post_vv"] is True
    assert "raw_orchestrator_matrix_not_allowed" in filter_row["block_reasons"]


def test_raw_user_intent_is_blocked():
    filter_row = _filters_by_scenario()["raw_user_intent_blocked"]

    assert filter_row["post_vv_invoked"] is False
    assert filter_row["blocked_before_post_vv"] is True
    assert "raw_user_intent_not_allowed" in filter_row["block_reasons"]


def test_real_action_output_is_blocked():
    filter_row = _filters_by_scenario()["real_action_output_blocked"]

    assert filter_row["post_vv_invoked"] is False
    assert filter_row["blocked_before_post_vv"] is True
    assert "real_action_output_not_allowed" in filter_row["block_reasons"]


def test_malformed_result_proposal_is_rejected():
    filter_row = _filters_by_scenario()["malformed_result_proposal_rejected"]
    validation_report = _reports_by_scenario()["malformed_result_proposal_rejected"]

    assert filter_row["post_vv_invoked"] is True
    assert filter_row["input_is_result_proposal"] is True
    assert validation_report["result_proposal_schema_valid"] is False
    assert validation_report["validation_status"] == "rejected"
    assert "result_proposal_shape_invalid" in validation_report["validation_findings"]
    assert "malformed_result_proposal_rejected" in validation_report["validation_findings"]
    assert validation_report["post_vv_creates_final_output"] is False
    assert validation_report["post_vv_writes_drs"] is False
    assert validation_report["post_vv_executes_actions"] is False
    assert validation_report["gt_invoked"] is False
    assert validation_report["root_final_invoked"] is False


def test_malicious_final_output_claim_is_rejected():
    validation_report = _reports_by_scenario()[
        "malicious_result_proposal_claiming_final_output_rejected"
    ]

    assert validation_report["validation_status"] == "rejected"
    assert validation_report["final_output_claim_detected"] is True
    assert "final_output_claim_rejected" in validation_report["validation_findings"]
    assert validation_report["post_vv_creates_final_output"] is False
    assert validation_report["gt_invoked"] is False
    assert validation_report["root_final_invoked"] is False


def test_malicious_drs_write_claim_is_rejected():
    validation_report = _reports_by_scenario()[
        "malicious_result_proposal_claiming_drs_write_rejected"
    ]

    assert validation_report["validation_status"] == "rejected"
    assert validation_report["drs_write_claim_detected"] is True
    assert "drs_write_claim_rejected" in validation_report["validation_findings"]
    assert validation_report["post_vv_writes_drs"] is False
    assert validation_report["gt_invoked"] is False
    assert validation_report["root_final_invoked"] is False


def test_post_vv_receives_only_result_proposal():
    authority = collect_post_vv_from_result_proposal().authority_safety

    assert authority["post_vv_receives_only_result_proposal"] is True
    assert authority["post_vv_receives_raw_executor_text"] is False
    assert authority["post_vv_receives_raw_architect_plan_graph"] is False
    assert authority["post_vv_receives_raw_orchestrator_matrix"] is False
    assert authority["post_vv_receives_raw_user_intent"] is False
    assert authority["post_vv_receives_real_action_output"] is False


def test_validation_report_only():
    report = collect_post_vv_from_result_proposal()

    assert report.authority_safety["validation_report_only"] is True
    assert all(row["created_by"] == "post_vv" for row in report.validation_reports)


def test_post_vv_does_not_create_final_output():
    authority = collect_post_vv_from_result_proposal().authority_safety

    assert authority["post_vv_creates_final_output"] is False
    assert authority["production_final_output_created"] is False


def test_post_vv_does_not_write_drs():
    authority = collect_post_vv_from_result_proposal().authority_safety

    assert authority["post_vv_writes_drs"] is False


def test_post_vv_does_not_execute_actions():
    authority = collect_post_vv_from_result_proposal().authority_safety

    assert authority["post_vv_executes_actions"] is False


def test_gt_is_not_invoked():
    authority = collect_post_vv_from_result_proposal().authority_safety

    assert authority["gt_invoked"] is False


def test_root_final_is_not_invoked():
    authority = collect_post_vv_from_result_proposal().authority_safety

    assert authority["root_final_invoked"] is False


def test_no_production_external_actions():
    authority = collect_post_vv_from_result_proposal().authority_safety

    assert authority["production_external_action_executed"] is False


def test_no_global_or_external_drs():
    authority = collect_post_vv_from_result_proposal().authority_safety

    assert authority["global_drs_implemented"] is False
    assert authority["external_drs_network_implemented"] is False


def test_marennya_and_up_not_invoked():
    authority = collect_post_vv_from_result_proposal().authority_safety

    assert authority["marennya_invoked"] is False
    assert authority["up_invoked"] is False


def test_pass_summary_derived_from_source_reports_blocks_rejections_and_boundaries():
    report = collect_post_vv_from_result_proposal()
    expected_pass = (
        report.input_result_proposals["source_dag_executor_report_status"] == "PASS"
        and report.summary["scenarios_verified"] == len(report.post_vv_input_filter)
        and report.summary["scenarios_verified"] == 10
        and report.summary["validation_reports_created"] == len(report.validation_reports)
        and report.summary["validation_reports_created"] == 5
        and report.summary["accepted_validation_reports"] == 1
        and report.summary["degraded_validation_reports"] == 1
        and report.summary["rejected_validation_reports"] == 3
        and report.summary["raw_executor_text_blocked"] is True
        and report.summary["raw_architect_plan_graph_blocked"] is True
        and report.summary["raw_orchestrator_matrix_blocked"] is True
        and report.summary["raw_user_intent_blocked"] is True
        and report.summary["real_action_output_blocked"] is True
        and report.summary["malformed_result_proposal_rejected"] is True
        and report.summary["malicious_final_output_claim_rejected"] is True
        and report.summary["malicious_drs_write_claim_rejected"] is True
        and report.authority_safety["post_vv_receives_only_result_proposal"]
        and report.authority_safety["validation_report_only"]
        and not report.authority_safety["gt_invoked"]
        and not report.authority_safety["root_final_invoked"]
        and not report.authority_safety["production_final_output_created"]
        and not report.authority_safety["production_external_action_executed"]
    )

    assert report.summary["post_vv_from_result_proposal_status"] == "PASS"
    assert expected_pass is True
    assert report.summary["ready_for_gt_from_validation_report"] is True
