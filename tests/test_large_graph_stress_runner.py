from __future__ import annotations

from demo.run_large_graph_stress import STRESS_CONFIG
from demo.run_large_graph_stress import collect_large_graph_stress
from demo.run_large_graph_stress import run_large_graph_stress


def _rows_by_scenario():
    return {row.scenario: row for row in collect_large_graph_stress()}


def test_runner_output_contains_title_and_summary():
    output = run_large_graph_stress()

    assert "[LARGE GRAPH / BOUNDED FRACTAL STRESS]" in output
    assert "[STRESS CONFIG]" in output
    assert "[SCENARIO RESULTS]" in output
    assert "[BOUNDARY / AUTHORITY]" in output
    assert "[SUMMARY]" in output
    assert "large_graph_stress_status: PASS" in output
    assert "scenarios: 9" in output


def test_normal_graph_completes_with_result_proposals():
    row = _rows_by_scenario()["normal_graph"]

    assert row.report["status"] == "completed"
    assert len(row.report["result_proposals"]) > 0
    assert row.report["executor_created_final_output"] is False
    assert row.root_final_authority_preserved is True


def test_wide_graph_respects_max_parallelism():
    row = _rows_by_scenario()["wide_graph"]

    assert row.report["status"] == "completed"
    assert row.report["budget_limits_applied"]["parallelism_limited"] is True
    assert len(row.report["execution_batches"]) > 1
    assert all(
        len(batch) <= row.plan_graph["branch_budget"]["max_parallelism"]
        for batch in row.report["execution_batches"]
    )


def test_deep_graph_checks_max_depth_and_blocks_when_exceeded():
    row = _rows_by_scenario()["deep_graph"]

    assert row.max_depth_exceeded is True
    assert row.report["status"] == "blocked"
    assert row.report["result_proposals"] == []
    assert row.report["unhandled_exceptions"] == 0


def test_oversized_graph_blocks_before_execution():
    row = _rows_by_scenario()["oversized_graph"]

    assert row.report["status"] == "blocked"
    assert row.report["max_nodes_exceeded"] is True
    assert row.report["execution_batches"] == []
    assert row.report["result_proposals"] == []


def test_too_many_edges_graph_blocks_before_execution():
    row = _rows_by_scenario()["too_many_edges_graph"]

    assert row.max_edges_exceeded is True
    assert row.report["status"] == "blocked"
    assert row.report["execution_batches"] == []
    assert row.report["result_proposals"] == []


def test_cycle_graph_is_detected_and_blocked():
    row = _rows_by_scenario()["cycle_graph"]

    assert row.report["cycle_detected"] is True
    assert row.report["status"] == "blocked"
    assert row.report["execution_batches"] == []
    assert row.report["result_proposals"] == []


def test_unknown_dependency_graph_is_detected_and_blocked():
    row = _rows_by_scenario()["unknown_dependency_graph"]

    assert row.unknown_dependency_detected is True
    assert row.report["cycle_detected"] is False
    assert row.report["status"] == "blocked"
    assert row.report["execution_batches"] == []
    assert row.report["result_proposals"] == []


def test_child_boundary_graph_creates_boundary_snapshot():
    row = _rows_by_scenario()["child_boundary_graph"]
    payloads = [proposal["result_payload"] for proposal in row.report["result_proposals"]]
    child_payloads = [payload for payload in payloads if payload["atomic"] is False]

    assert row.report["status"] == "completed"
    assert row.report["child_boundary_snapshots"] > 0
    assert child_payloads
    for payload in child_payloads:
        assert payload["status"] == "boundary_snapshot"
        assert payload["task_completed"] is False
        assert payload["executed_domain_action"] is False
        assert payload["not_executed_in_v0_1"] is True
        assert payload["root_does_not_manage_internal_state"] is True


def test_gt_summary_boundary_keeps_candidate_count_bounded():
    row = _rows_by_scenario()["gt_summary_boundary"]

    assert row.report["status"] == "completed"
    assert len(row.report["result_proposals"]) > STRESS_CONFIG["gt_candidate_limit"]
    assert row.gt_candidate_count <= STRESS_CONFIG["gt_candidate_limit"]
    assert row.boundary_summary_used is True
    assert row.raw_large_graph_not_sent_to_gt is True


def test_gt_boundary_is_summary_check_not_runtime_call():
    output = run_large_graph_stress()
    row = _rows_by_scenario()["gt_summary_boundary"]

    assert "gt_runtime_called: false" in output
    assert "gt_boundary_mode: bounded_summary_check" in output
    assert "gt_candidate_limit_applied: true" in output
    assert len(row.report["result_proposals"]) > STRESS_CONFIG["gt_candidate_limit"]
    assert row.gt_candidate_count <= STRESS_CONFIG["gt_candidate_limit"]


def test_authority_invariants_hold_for_all_scenarios():
    for row in collect_large_graph_stress():
        assert row.root_final_authority_preserved is True
        assert row.report["executor_created_final_output"] is False
        assert row.report["no_real_external_action"] is True
        for proposal in row.report["result_proposals"]:
            assert "final_output" not in proposal
            assert proposal["result_payload"]["global_commit_claimed"] is False


def test_output_contains_no_sensitive_terms():
    output = run_large_graph_stress().lower()

    assert "api_key" not in output
    assert "token" not in output
    assert "secret" not in output
    assert "raw_user_text" not in output
    assert "chain of thought" not in output
