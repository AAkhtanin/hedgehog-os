from __future__ import annotations

from demo.run_dag_executor_from_valid_plan_graph import (
    collect_dag_executor_from_valid_plan_graph,
    run_dag_executor_from_valid_plan_graph,
)


def _filters_by_scenario():
    report = collect_dag_executor_from_valid_plan_graph()
    return {row["scenario"]: row for row in report.executor_input_filter}


def _results_by_scenario():
    report = collect_dag_executor_from_valid_plan_graph()
    return {result["scenario"]: result for result in report.result_proposals}


def test_runner_output_contains_title():
    output = run_dag_executor_from_valid_plan_graph()

    assert "[DAG EXECUTOR FROM VALID PLAN GRAPH]" in output
    assert "[INPUT PLAN GRAPHS]" in output
    assert "[EXECUTOR INPUT FILTER]" in output
    assert "[RESULT PROPOSALS]" in output
    assert "[CONTAINMENT]" in output
    assert "[AUTHORITY / SAFETY]" in output
    assert "[SUMMARY]" in output


def test_source_architect_proof_status_is_pass():
    report = collect_dag_executor_from_valid_plan_graph()

    assert report.input_plan_graphs["source_architect_report_status"] == "PASS"
    assert report.summary["source_architect_from_attractor_status"] == "PASS"
    assert report.input_plan_graphs["accepted_packet_plan_proposals"] == 1
    assert report.input_plan_graphs["downgraded_packet_plan_proposals"] == 1
    assert len(report.input_plan_graphs["valid_proposals_imported"]) == 2


def test_accepted_valid_plan_graph_creates_result_proposal():
    filter_row = _filters_by_scenario()["accepted_plan_graph_executor_result_proposal"]
    result = _results_by_scenario()["accepted_plan_graph_executor_result_proposal"]

    assert filter_row["executor_invoked"] is True
    assert filter_row["executor_input_is_validated_plan_graph"] is True
    assert result["created_by"] == "executor"
    assert result["executor_input_is_validated_plan_graph"] is True
    assert result["result_status"] == "completed"
    assert result["node_results"]
    assert result["executor_creates_final_output"] is False
    assert result["executor_writes_drs"] is False
    assert result["executor_executes_real_action"] is False


def test_downgraded_valid_plan_graph_creates_limited_result_proposal():
    result = _results_by_scenario()[
        "downgraded_plan_graph_executor_limited_result_proposal"
    ]

    assert result["result_status"] == "degraded"
    assert "missing_guard:ReuseGate boundary" in result["downgraded_claims_visible"]
    assert result["node_results"]
    assert all(node["vector_id"] != "official_online_request" for node in result["node_results"])
    assert result["executor_creates_final_output"] is False
    assert result["executor_writes_drs"] is False


def test_invalid_architect_artifact_is_blocked_before_executor():
    filter_row = _filters_by_scenario()[
        "invalid_architect_artifact_blocked_before_executor"
    ]

    assert filter_row["executor_invoked"] is False
    assert filter_row["blocked_before_executor"] is True
    assert "invalid_architect_artifact_not_allowed" in filter_row["block_reasons"]


def test_raw_architect_text_is_blocked():
    filter_row = _filters_by_scenario()["raw_architect_text_blocked"]

    assert filter_row["executor_invoked"] is False
    assert filter_row["blocked_before_executor"] is True
    assert "raw_architect_text_not_allowed" in filter_row["block_reasons"]


def test_raw_orchestrator_matrix_is_blocked():
    filter_row = _filters_by_scenario()["raw_orchestrator_matrix_blocked"]

    assert filter_row["executor_invoked"] is False
    assert filter_row["blocked_before_executor"] is True
    assert "raw_orchestrator_matrix_not_allowed" in filter_row["block_reasons"]


def test_raw_user_intent_is_blocked():
    filter_row = _filters_by_scenario()["raw_user_intent_blocked"]

    assert filter_row["executor_invoked"] is False
    assert filter_row["blocked_before_executor"] is True
    assert "raw_user_intent_not_allowed" in filter_row["block_reasons"]


def test_unvalidated_plan_graph_is_blocked():
    filter_row = _filters_by_scenario()["unvalidated_plan_graph_blocked"]

    assert filter_row["executor_invoked"] is False
    assert filter_row["blocked_before_executor"] is True
    assert "unvalidated_plan_graph_not_allowed" in filter_row["block_reasons"]


def test_executor_receives_only_validated_plan_graph_nodes():
    report = collect_dag_executor_from_valid_plan_graph()

    assert report.authority_safety["executor_receives_only_validated_plan_graph_nodes"] is True
    assert all(
        row["executor_input_is_validated_plan_graph"]
        for row in report.executor_input_filter
        if row["executor_invoked"]
    )


def test_executor_returns_result_proposal_only():
    report = collect_dag_executor_from_valid_plan_graph()

    assert report.authority_safety["result_proposal_only"] is True
    assert report.summary["result_proposals_created"] == 2
    assert all(result["created_by"] == "executor" for result in report.result_proposals)


def test_executor_does_not_create_final_output():
    authority = collect_dag_executor_from_valid_plan_graph().authority_safety

    assert authority["executor_creates_final_output"] is False
    assert authority["production_final_output_created"] is False


def test_executor_does_not_write_drs_directly():
    authority = collect_dag_executor_from_valid_plan_graph().authority_safety

    assert authority["executor_writes_drs"] is False


def test_executor_does_not_execute_real_external_actions():
    authority = collect_dag_executor_from_valid_plan_graph().authority_safety

    assert authority["executor_executes_real_action"] is False
    assert authority["production_external_action_executed"] is False


def test_post_vv_is_not_invoked():
    authority = collect_dag_executor_from_valid_plan_graph().authority_safety

    assert authority["post_vv_invoked"] is False


def test_gt_is_not_invoked():
    authority = collect_dag_executor_from_valid_plan_graph().authority_safety

    assert authority["gt_invoked"] is False


def test_no_production_external_actions():
    authority = collect_dag_executor_from_valid_plan_graph().authority_safety

    assert authority["production_external_action_executed"] is False


def test_no_global_or_external_drs():
    authority = collect_dag_executor_from_valid_plan_graph().authority_safety

    assert authority["global_drs_implemented"] is False
    assert authority["external_drs_network_implemented"] is False


def test_marennya_and_up_not_invoked():
    authority = collect_dag_executor_from_valid_plan_graph().authority_safety

    assert authority["marennya_invoked"] is False
    assert authority["up_invoked"] is False


def test_pass_summary_derived_from_source_results_blocks_and_boundaries():
    report = collect_dag_executor_from_valid_plan_graph()
    expected_pass = (
        report.input_plan_graphs["source_architect_report_status"] == "PASS"
        and report.summary["scenarios_verified"] == len(report.executor_input_filter)
        and report.summary["result_proposals_created"] == len(report.result_proposals)
        and report.summary["accepted_plan_result_proposals"] == 1
        and report.summary["downgraded_plan_result_proposals"] == 1
        and report.summary["invalid_architect_artifact_blocked"] is True
        and report.summary["raw_architect_text_blocked"] is True
        and report.summary["raw_orchestrator_matrix_blocked"] is True
        and report.summary["raw_user_intent_blocked"] is True
        and report.summary["unvalidated_plan_graph_blocked"] is True
        and report.authority_safety["executor_receives_only_validated_plan_graph_nodes"]
        and report.authority_safety["result_proposal_only"]
        and not report.authority_safety["post_vv_invoked"]
        and not report.authority_safety["gt_invoked"]
        and not report.authority_safety["production_final_output_created"]
        and not report.authority_safety["production_external_action_executed"]
    )

    assert report.summary["dag_executor_from_valid_plan_graph_status"] == "PASS"
    assert expected_pass is True
    assert report.summary["ready_for_post_vv_from_result_proposal"] is True
