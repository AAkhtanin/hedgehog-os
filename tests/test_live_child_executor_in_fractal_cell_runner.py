from __future__ import annotations

import demo.run_live_child_executor_in_fractal_cell as live_child
from demo.run_live_child_executor_in_fractal_cell import (
    ACTION_SCENARIO,
    PROOF_SCENARIO,
    collect_live_child_executor_in_fractal_cell,
    fake_live_child_execution_result,
    run_live_child_executor_in_fractal_cell,
)


def _fallback_report():
    return collect_live_child_executor_in_fractal_cell(live_requested=False)


def _fake_live_report():
    return collect_live_child_executor_in_fractal_cell(
        live_requested=True,
        injected_proof_result=fake_live_child_execution_result(),
        injected_action_result=fake_live_child_execution_result(action_like=True),
    )


def _executions(report=None):
    report = report or _fallback_report()
    return {row["scenario"]: row for row in report.live_child_executor}


def _snapshots(report=None):
    report = report or _fallback_report()
    return {row["scenario"]: row for row in report.child_boundary_snapshot}


def _adapters(report=None):
    report = report or _fallback_report()
    return {row["scenario"]: row for row in report.parent_adapter}


def _downstream(report=None):
    report = report or _fallback_report()
    return {row["scenario"]: row for row in report.post_vv_gt_root_final}


def test_runner_contains_required_sections():
    output = run_live_child_executor_in_fractal_cell()
    for heading in (
        "[LIVE CHILD EXECUTOR IN FRACTAL CELL]",
        "[INPUT / MODE]",
        "[CHILD NODE CONTRACT]",
        "[LIVE CHILD EXECUTOR]",
        "[CHILD BOUNDARY SNAPSHOT]",
        "[PARENT ADAPTER]",
        "[POST V&V / GT / ROOT FINAL]",
        "[BLOCKED / MALICIOUS INPUTS]",
        "[AUTHORITY / SAFETY]",
        "[SUMMARY]",
    ):
        assert heading in output


def test_default_mode_does_not_call_network_or_claim_live_success(monkeypatch):
    monkeypatch.delenv("HEDGEHOG_ALLOW_LIVE_GEMINI", raising=False)

    def fail_call(**_kwargs):
        raise AssertionError("Gemini must not be called in deterministic mode")

    monkeypatch.setattr(live_child, "_gemini_call", fail_call)
    report = collect_live_child_executor_in_fractal_cell(live_requested=False)
    assert report.input_mode["live_network_used"] is False
    assert report.summary["live_child_executor_used"] is False
    assert report.summary["live_child_executor_valid"] is False
    assert report.summary["live_child_executor_in_fractal_cell_status"] == (
        "SAFE_FALLBACK_NOT_LIVE_SUCCESS"
    )


def test_bounded_contract_forbids_free_instruction_and_external_capabilities():
    contract = _fallback_report().child_node_contract
    assert contract["task_kind"] == "proof_only_cognitive_task"
    assert contract["expected_output_schema"] == "child_execution_result_v0_1"
    assert contract["allowed_capability"] == "local_reasoning_only"
    assert contract["permission_mode"] == "no_external_action"
    assert contract["result_must_be"] == "ChildExecutionResult"
    assert contract["sandbox_mode"] is True
    assert contract["free_instruction_allowed"] is False
    assert set(live_child.FORBIDDEN_ACTIONS) == set(contract["forbidden_actions"])


def test_fake_live_valid_results_can_pass_without_network(monkeypatch):
    monkeypatch.delenv("HEDGEHOG_ALLOW_LIVE_GEMINI", raising=False)
    report = _fake_live_report()
    assert report.input_mode["live_network_used"] is False
    assert report.summary["live_child_executor_in_fractal_cell_status"] == "PASS"
    assert report.summary["live_child_executor_used"] is True
    assert report.summary["live_child_executor_valid"] is True


def test_live_role_is_exactly_child_executor_only():
    for row in _fake_live_report().live_child_executor:
        assert row["child_executor_role"] == "child_executor_only"
        assert row["child_orchestrator_live"] is False
        assert row["child_architect_live"] is False
        assert row["bounded_node_contract_received"] is True
        assert row["free_instruction_received"] is False


def test_completed_proof_task_reaches_root_through_all_boundaries():
    report = _fake_live_report()
    execution = _executions(report)[PROOF_SCENARIO]
    snapshot = _snapshots(report)[PROOF_SCENARIO]
    adapter = _adapters(report)[PROOF_SCENARIO]
    downstream = _downstream(report)[PROOF_SCENARIO]
    assert execution["execution_status"] == "completed"
    assert snapshot["source_child_execution_result_id"].endswith(PROOF_SCENARIO)
    assert snapshot["child_execution_result_preserved"] is True
    assert adapter["source_child_boundary_snapshot_id"] == snapshot[
        "child_boundary_snapshot_id"
    ]
    assert downstream["post_vv_status"] == "accepted"
    assert downstream["gt_decision"] == "accept"
    assert downstream["root_final_status"] == "accepted"
    assert downstream["root_is_only_final_output_authority"] is True


def test_action_like_request_is_blocked_and_not_hidden_as_success():
    report = _fake_live_report()
    execution = _executions(report)[ACTION_SCENARIO]
    adapter = _adapters(report)[ACTION_SCENARIO]
    downstream = _downstream(report)[ACTION_SCENARIO]
    assert execution["execution_status"] in {"blocked", "degraded"}
    assert execution["failure_kind"] in {
        "action_like_request_blocked",
        "permission_required",
        "sandbox_only",
    }
    assert execution["action_like_request_detected"] is True
    assert execution["child_executed_real_action"] is False
    assert execution["child_called_api_or_tool"] is False
    assert adapter["degraded_or_blocked_preserved"] is True
    assert downstream["root_final_status"] != "accepted"
    assert downstream["unsafe_success_hidden"] is False


def test_invalid_child_execution_json_is_rejected_before_clean_success():
    contract = live_child.child_node_contract()
    validation = live_child._validate_child_execution_result(
        {"child_execution_result_id": "malformed"}, contract, action_like=False
    )
    assert validation["valid"] is False
    assert any(reason.startswith("missing:") for reason in validation["errors"])
    assert _fallback_report().blocked_malicious_inputs[
        "invalid_child_execution_json_rejected"
    ] is True


def test_all_malicious_claims_are_rejected():
    blocked = _fallback_report().blocked_malicious_inputs
    assert blocked["malicious_child_final_output_claim_rejected"] is True
    assert blocked["malicious_child_parent_drs_write_claim_rejected"] is True
    assert blocked["malicious_child_real_action_claim_rejected"] is True
    assert blocked["malicious_child_api_tool_call_claim_rejected"] is True
    assert blocked["malicious_child_root_bypass_claim_rejected"] is True
    assert blocked["malicious_child_post_vv_gt_root_bypass_claim_rejected"] is True


def test_malicious_result_cannot_create_boundary_snapshot():
    contract = live_child.child_node_contract()
    malicious = fake_live_child_execution_result()
    malicious["child_called_api_or_tool"] = True
    validation = live_child._validate_child_execution_result(
        malicious, contract, action_like=False
    )
    row = {
        "scenario": "malicious",
        "active_result_valid": validation["valid"],
        "live_child_executor_used": True,
        "child_executor_source": "live_gemini",
    }
    assert "child_api_tool_call_claim_rejected" in validation["errors"]
    assert live_child._boundary_snapshot(malicious, row, contract) is None


def test_child_result_snapshot_adapter_and_downstream_are_not_bypassed():
    report = _fallback_report()
    assert len(report.child_boundary_snapshot) == 2
    assert len(report.parent_adapter) == 2
    assert len(report.post_vv_gt_root_final) == 2
    for row in report.parent_adapter:
        assert row["child_execution_result_preserved"] is True
        assert row["final_output_claim"] is False
        assert row["drs_write_claim"] is False
        assert row["real_external_action_claim"] is False
        assert row["api_tool_call_claim"] is False
    for row in report.post_vv_gt_root_final:
        assert row["post_vv_bypassed"] is False
        assert row["gt_bypassed"] is False
        assert row["root_bypassed"] is False


def test_authority_and_safety_boundaries():
    authority = _fallback_report().authority_safety
    assert authority["live_child_executor_is_authority"] is False
    assert authority["child_executor_is_root"] is False
    assert authority["child_execution_result_is_final_truth"] is False
    assert authority["root_remains_authority"] is True
    assert authority["root_is_only_final_output_authority"] is True
    assert authority["no_child_final_output"] is True
    assert authority["no_child_parent_drs_write"] is True
    assert authority["no_real_external_actions"] is True
    assert authority["no_api_tool_calls"] is True
    assert authority["no_root_bypass"] is True
    assert authority["no_post_vv_gt_root_bypass"] is True
    assert authority["production_persistence_claimed"] is False
    assert authority["global_drs_implemented"] is False
    assert authority["external_drs_network_implemented"] is False
    assert authority["telegram_action_executed"] is False
    assert authority["marennya_invoked"] is False
    assert authority["up_invoked"] is False


def test_summary_is_derived_from_live_fallback_blocking_and_authority():
    fallback = _fallback_report().summary
    live = _fake_live_report().summary
    for summary in (fallback, live):
        assert summary["action_like_request_blocked"] is True
        assert summary["child_boundary_snapshot_created"] is True
        assert summary["parent_adapter_created_result_proposal"] is True
        assert summary["post_vv_gt_root_reached"] is True
        assert summary["root_remains_authority"] is True
        assert summary["root_is_only_final_output_authority"] is True
        assert summary["malicious_claims_rejected"] == 6
        assert summary["no_child_final_output"] is True
        assert summary["no_child_parent_drs_write"] is True
        assert summary["no_real_external_actions"] is True
        assert summary["no_api_tool_calls"] is True
        assert summary["ready_for_drs_lifecycle_semantics_v0_2"] is True
        assert summary["production_autonomy_claimed"] is False
    assert fallback["live_child_executor_in_fractal_cell_status"] == (
        "SAFE_FALLBACK_NOT_LIVE_SUCCESS"
    )
    assert live["live_child_executor_in_fractal_cell_status"] == "PASS"
