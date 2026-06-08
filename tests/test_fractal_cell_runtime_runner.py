from __future__ import annotations

from demo.run_fractal_cell_runtime import (
    SCENARIOS_UNDER_TEST,
    collect_fractal_cell_runtime,
    run_fractal_cell_runtime,
)


def _report():
    return collect_fractal_cell_runtime()


def _snapshots():
    return {row["scenario"]: row for row in _report().child_boundary_snapshots}


def _executions():
    return {row["scenario"]: row for row in _report().child_mini_cell_execution}


def _adapters():
    return {row["scenario"]: row for row in _report().parent_adapter}


def _downstream():
    return {row["scenario"]: row for row in _report().post_vv_gt_root_final}


def test_runner_contains_required_sections():
    output = run_fractal_cell_runtime()
    for heading in (
        "[FRACTAL CELL RUNTIME]",
        "[PARENT PLAN GRAPH]",
        "[CHILD CELL REQUESTS]",
        "[CHILD MINI-CELL EXECUTION]",
        "[CHILD BOUNDARY SNAPSHOTS]",
        "[PARENT ADAPTER]",
        "[POST V&V / GT / ROOT FINAL]",
        "[NON-CHILD ROUTES]",
        "[BLOCKED / MALICIOUS INPUTS]",
        "[AUTHORITY / SAFETY]",
        "[SUMMARY]",
    ):
        assert heading in output


def test_parent_plan_graph_has_all_three_routes():
    parent = _report().parent_plan_graph
    assert set(parent["node_types_present"]) == {"atomic", "needle_bound", "non_atomic"}
    assert parent["topology_routes"] == {
        "atomic": "executor",
        "needle_bound": "needleruntime",
        "non_atomic": "child_cell",
    }


def test_non_atomic_node_creates_child_cell_requests():
    report = _report()
    assert len(report.child_cell_requests) == 4
    assert all(row["created_by"] == "fractal_dag_executor" for row in report.child_cell_requests)
    assert all(row["parent_drs_write_allowed"] is False for row in report.child_cell_requests)
    assert all(row["live_llm_allowed"] is False for row in report.child_cell_requests)


def test_completed_child_snapshot_reaches_accepted_root_final():
    snapshot = _snapshots()["non_atomic_child_cell_completed"]
    downstream = _downstream()["non_atomic_child_cell_completed"]
    assert snapshot["child_status"] == "completed"
    assert snapshot["child_event_log_present"] is True
    assert downstream["post_vv_status"] == "accepted"
    assert downstream["gt_decision"] == "accept"
    assert downstream["root_final_status"] == "accepted"


def test_degraded_budget_state_is_preserved():
    execution = _executions()["non_atomic_child_cell_degraded_budget_limit"]
    adapter = _adapters()["non_atomic_child_cell_degraded_budget_limit"]
    downstream = _downstream()["non_atomic_child_cell_degraded_budget_limit"]
    assert execution["child_status"] == "degraded"
    assert execution["failure_kind"] == "budget_limit_approached"
    assert adapter["degraded_or_blocked_preserved"] is True
    assert downstream["root_final_status"] == "degraded"
    assert downstream["unsafe_success_hidden"] is False


def test_max_depth_is_blocked_without_recursion_explosion():
    execution = _executions()["non_atomic_child_cell_blocked_max_depth"]
    downstream = _downstream()["non_atomic_child_cell_blocked_max_depth"]
    assert execution["child_status"] == "blocked"
    assert execution["failure_kind"] == "max_depth_exceeded"
    assert execution["child_orchestrator_ran"] is False
    assert downstream["root_final_status"] == "rejected"
    assert _report().authority_safety["recursion_bounded"] is True


def test_contract_mismatch_is_contained_without_crash():
    execution = _executions()["non_atomic_child_cell_failed_contract_mismatch"]
    downstream = _downstream()["non_atomic_child_cell_failed_contract_mismatch"]
    assert execution["child_status"] == "failed"
    assert execution["failure_kind"] == "contract_mismatch"
    assert execution["root_crash_risk_contained"] is True
    assert downstream["root_final_status"] == "rejected"


def test_atomic_and_needle_routes_do_not_spawn_child_cells():
    routes = _report().non_child_routes
    assert routes["atomic_node_does_not_spawn_child_cell"] is True
    assert routes["ordinary_executor_route_visible"] is True
    assert routes["needle_bound_node_does_not_spawn_child_cell"] is True
    assert routes["needleruntime_route_visible"] is True


def test_parent_adapter_preserves_snapshot_and_downstream_is_not_bypassed():
    snapshots = _snapshots()
    for scenario, adapter in _adapters().items():
        assert adapter["source_child_boundary_snapshot_id"] == snapshots[scenario][
            "child_boundary_snapshot_id"
        ]
        assert adapter["child_boundary_snapshot_preserved"] is True
        assert adapter["final_output_claim"] is False
        assert adapter["drs_write_claim"] is False
        assert adapter["real_external_action_claim"] is False
    for row in _report().post_vv_gt_root_final:
        assert row["post_vv_bypassed"] is False
        assert row["gt_bypassed"] is False
        assert row["root_bypassed"] is False
        assert row["unsafe_success_hidden"] is False


def test_raw_and_malicious_child_outputs_are_rejected():
    blocked = _report().blocked_malicious_inputs
    assert blocked["raw_child_output_blocked"] is True
    assert blocked["malicious_child_final_output_claim_rejected"] is True
    assert blocked["malicious_child_parent_drs_write_claim_rejected"] is True
    assert blocked["malicious_child_real_action_claim_rejected"] is True
    assert blocked["malicious_child_orchestrator_root_claim_rejected"] is True
    assert blocked["malicious_child_live_llm_claim_rejected"] is True


def test_authority_and_safety_boundaries():
    authority = _report().authority_safety
    assert authority["child_cell_is_authority"] is False
    assert authority["child_orchestrator_is_root"] is False
    assert authority["child_output_is_final_truth"] is False
    assert authority["root_remains_authority"] is True
    assert authority["root_is_only_final_output_authority"] is True
    assert authority["child_created_final_output"] is False
    assert authority["child_wrote_parent_drs"] is False
    assert authority["child_executed_real_action"] is False
    assert authority["child_used_live_llm"] is False
    assert authority["recursion_bounded"] is True
    assert authority["budget_bounded"] is True
    assert authority["parent_promotion_requires_root"] is True
    assert authority["production_persistence_claimed"] is False
    assert authority["global_drs_implemented"] is False
    assert authority["external_drs_network_implemented"] is False
    assert authority["marennya_invoked"] is False
    assert authority["up_invoked"] is False


def test_pass_summary_is_derived_from_routes_scenarios_and_authority():
    summary = _report().summary
    derived_pass = (
        summary["scenarios_verified"] == len(SCENARIOS_UNDER_TEST) == 12
        and summary["child_cell_completed_scenarios"] == 1
        and summary["child_cell_degraded_scenarios"] == 1
        and summary["child_cell_blocked_or_failed_scenarios"] == 2
        and summary["malicious_child_claims_rejected"] == 5
        and summary["raw_child_output_blocked"] is True
        and summary["atomic_route_preserved"] is True
        and summary["needle_route_preserved"] is True
        and summary["non_atomic_route_spawns_child_cell"] is True
        and summary["child_boundary_snapshot_preserved"] is True
        and summary["root_remains_authority"] is True
        and summary["root_is_only_final_output_authority"] is True
        and summary["no_child_final_output"] is True
        and summary["no_child_parent_drs_write"] is True
        and summary["no_real_external_actions"] is True
        and summary["recursion_bounded"] is True
        and summary["budget_bounded"] is True
    )
    assert derived_pass is True
    assert summary["fractal_cell_runtime_status"] == "PASS"
    assert summary["ready_for_drs_lifecycle_semantics_v0_2"] is True
    assert summary["production_autonomy_claimed"] is False
