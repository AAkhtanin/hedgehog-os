from __future__ import annotations

from demo.run_fractal_dag_executor_core import build_scenarios, render_report, run_scenarios
from hedgehog.fractal_dag_executor import run_fractal_dag_executor


def _scenario(name: str):
    return {row.name: row for row in run_scenarios()}[name]


def _plan(name: str):
    return {scenario: plan for scenario, plan in build_scenarios()}[name]


def _contains_key(value, forbidden_key: str) -> bool:
    if isinstance(value, dict):
        return forbidden_key in value or any(
            _contains_key(child, forbidden_key) for child in value.values()
        )
    if isinstance(value, list):
        return any(_contains_key(item, forbidden_key) for item in value)
    return False


def test_horizontal_branches_ready_and_execute_in_one_batch():
    report = _scenario("horizontal_parallel_branches").report

    assert report["ready_sequence"][0] == ["A", "B", "C"]
    assert report["execution_batches"] == [["A", "B", "C"]]
    assert report["status"] == "completed"


def test_vertical_chain_executes_in_dependency_order():
    report = _scenario("vertical_chain").report

    assert report["ready_sequence"] == [["A"], ["B"], ["C"]]
    assert report["execution_batches"] == [["A"], ["B"], ["C"]]
    assert report["status"] == "completed"


def test_hybrid_graph_unlocks_dependents_from_completed_deps():
    report = _scenario("hybrid_graph").report

    assert report["ready_sequence"][0] == ["A", "B"]
    assert "C" in report["ready_sequence"][1]
    d_batch_index = next(
        index
        for index, batch in enumerate(report["execution_batches"])
        if "D" in batch
    )
    a_batch_index = next(
        index
        for index, batch in enumerate(report["execution_batches"])
        if "A" in batch
    )
    b_batch_index = next(
        index
        for index, batch in enumerate(report["execution_batches"])
        if "B" in batch
    )
    assert d_batch_index > a_batch_index
    assert d_batch_index > b_batch_index
    assert report["status"] == "completed"


def test_non_atomic_node_returns_child_boundary_snapshot():
    report = _scenario("non_atomic_child_cell_placeholder").report
    proposal = report["result_proposals"][0]
    payload = proposal["result_payload"]

    assert report["child_boundary_snapshots"] == 1
    assert payload["status"] == "boundary_snapshot"
    assert payload["atomic"] is False
    assert payload["child_cell_placeholder"] is True
    assert payload["not_executed_in_v0_1"] is True
    assert payload["root_does_not_manage_internal_state"] is True
    assert payload["executed_domain_action"] is False
    assert payload["task_completed"] is False


def test_parallelism_limit_is_respected_by_batches():
    report = _scenario("parallelism_budget_limit").report

    assert report["ready_sequence"][0] == ["A", "B", "C", "D"]
    assert report["execution_batches"] == [["A", "B"], ["C", "D"]]
    assert report["budget_limits_applied"]["parallelism_limited"] is True
    assert report["status"] == "completed"


def test_cycle_is_detected_before_execution_and_does_not_hang():
    report = _scenario("cycle_detected").report

    assert report["cycle_detected"] is True
    assert report["status"] == "blocked"
    assert report["result_proposals"] == []
    assert report["execution_batches"] == []
    assert report["unhandled_exceptions"] == 0


def test_max_nodes_exceeded_is_blocked_before_execution():
    report = _scenario("max_nodes_exceeded").report

    assert report["max_nodes_exceeded"] is True
    assert report["status"] == "blocked"
    assert report["result_proposals"] == []
    assert report["execution_batches"] == []
    assert report["unhandled_exceptions"] == 0


def test_executor_never_creates_final_output():
    for row in run_scenarios():
        assert row.report["executor_created_final_output"] is False
        for proposal in row.report["result_proposals"]:
            assert not _contains_key(proposal, "final_output")
            assert not _contains_key(proposal, "FinalOutput")
            assert proposal["result_payload"]["global_commit_claimed"] is False


def test_atomic_nodes_produce_result_proposal_shaped_dicts_with_time_envelope():
    report = _scenario("horizontal_parallel_branches").report
    required_fields = {
        "proposal_id",
        "request_id",
        "producer",
        "vector_id",
        "plan_id",
        "node_id",
        "result_payload",
        "evidence",
        "cost",
        "risks",
        "time_envelope",
        "trace_refs",
    }
    time_fields = {
        "pt_created_at",
        "kt_asof",
        "ct_session_anchor",
        "ttl_seconds",
    }

    for proposal in report["result_proposals"]:
        assert required_fields <= set(proposal)
        assert "executor_id" in proposal["producer"]
        assert time_fields <= set(proposal["time_envelope"])
        assert proposal["result_payload"]["status"] == "completed"
        assert proposal["result_payload"]["atomic"] is True
        assert proposal["result_payload"]["executed_domain_action"] is False


def test_runner_report_includes_ready_sequence_and_execution_batches():
    report = _scenario("vertical_chain").report

    assert "ready_sequence" in report
    assert "execution_batches" in report
    assert report["ready_sequence"]
    assert report["execution_batches"]


def test_node_deps_field_is_supported_without_edges():
    plan = _plan("vertical_chain")
    plan["edges"] = []
    plan["nodes"][1]["deps"] = ["A"]
    plan["nodes"][2]["deps"] = ["B"]

    report = run_fractal_dag_executor(plan)

    assert report["ready_sequence"] == [["A"], ["B"], ["C"]]
    assert report["status"] == "completed"


def test_demo_prints_all_scenarios_and_safe_summary():
    output = render_report()

    for name, _plan_graph in build_scenarios():
        assert name in output
    assert "[FRACTAL DAG EXECUTOR CORE]" in output
    assert "ready sets are computed from nodes and edges" in output
    assert "Executor returns ResultProposal only" in output
    assert "non-atomic nodes create boundary snapshots" in output
    assert "no_real_external_actions: true" in output
    assert "unhandled_exceptions: 0" in output
    assert "executor_created_final_output: false" in output


def test_demo_output_contains_no_sensitive_terms():
    output = render_report().lower()

    assert "api_key" not in output
    assert "token" not in output
    assert "secret" not in output
    assert "raw_user_text" not in output
    assert "chain of thought" not in output
