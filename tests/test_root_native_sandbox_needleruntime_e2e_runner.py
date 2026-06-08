from __future__ import annotations

from demo.run_root_native_sandbox_needleruntime_e2e import (
    SCENARIOS_UNDER_TEST,
    collect_root_native_sandbox_needleruntime_e2e,
    run_root_native_sandbox_needleruntime_e2e,
)


def _report():
    return collect_root_native_sandbox_needleruntime_e2e()


def _executions():
    return {row["scenario"]: row for row in _report().needleruntime_executions}


def _adapters():
    return {row["scenario"]: row for row in _report().result_proposal_adapter}


def _downstream():
    return {row["scenario"]: row for row in _report().post_vv_gt_root_final}


def test_runner_contains_required_sections():
    output = run_root_native_sandbox_needleruntime_e2e()
    for heading in (
        "[ROOT-NATIVE SANDBOX NEEDLERUNTIME E2E]",
        "[INPUT / MODE]",
        "[ROOT-APPROVED PLAN NODE]",
        "[NEEDLERUNTIME EXECUTIONS]",
        "[RESULT PROPOSAL ADAPTER]",
        "[POST V&V / GT / ROOT FINAL]",
        "[BLOCKED / MALICIOUS INPUTS]",
        "[AUTHORITY / SAFETY]",
        "[SUMMARY]",
    ):
        assert heading in output


def test_completed_scenario_reaches_root_final():
    execution = _executions()["sandbox_needle_completed"]
    downstream = _downstream()["sandbox_needle_completed"]
    assert execution["execution_status"] == "completed"
    assert downstream["post_vv_status"] == "accepted"
    assert downstream["gt_decision"] == "accept"
    assert downstream["root_final_status"] == "accepted"
    assert downstream["root_final_artifact_created"] is True


def test_timeout_is_degraded_and_not_hidden():
    execution = _executions()["sandbox_needle_timeout_degraded"]
    downstream = _downstream()["sandbox_needle_timeout_degraded"]
    assert execution["execution_status"] == "degraded"
    assert execution["failure_kind"] == "timeout"
    assert downstream["post_vv_status"] == "degraded"
    assert downstream["gt_decision"] == "degrade"
    assert downstream["root_final_status"] == "degraded"
    assert downstream["unsafe_success_hidden"] is False


def test_invalid_json_is_failed_and_quarantined():
    execution = _executions()["sandbox_needle_invalid_json_failed"]
    downstream = _downstream()["sandbox_needle_invalid_json_failed"]
    assert execution["execution_status"] == "failed"
    assert execution["failure_kind"] == "invalid_json"
    assert execution["quarantine_required"] is True
    assert execution["safe_for_gt"] is False
    assert downstream["gt_decision"] == "reject"
    assert downstream["unsafe_success_hidden"] is False


def test_contract_mismatch_is_contained():
    execution = _executions()["sandbox_needle_contract_mismatch_blocked"]
    downstream = _downstream()["sandbox_needle_contract_mismatch_blocked"]
    assert execution["execution_status"] in {"blocked", "failed"}
    assert execution["failure_kind"] == "contract_mismatch"
    assert execution["root_crash_risk_contained"] is True
    assert downstream["root_final_status"] == "rejected"


def test_permission_and_external_action_are_blocked_without_action():
    executions = _executions()
    permission = executions["sandbox_needle_permission_required_blocked"]
    external = executions["sandbox_needle_forbidden_external_action_blocked"]
    assert permission["execution_status"] == "blocked"
    assert permission["failure_kind"] == "permission_required"
    assert permission["permission_required"] is True
    assert external["execution_status"] == "blocked"
    assert external["failure_kind"] == "forbidden_external_action"
    assert permission["real_external_action_executed"] is False
    assert external["real_external_action_executed"] is False


def test_raw_and_malicious_inputs_are_rejected():
    blocked = _report().blocked_malicious_inputs
    assert blocked["raw_needleruntime_output_blocked"] is True
    assert blocked["malicious_needle_claiming_final_output_rejected"] is True
    assert blocked["malicious_needle_claiming_drs_write_rejected"] is True
    assert blocked["malicious_needle_claiming_root_bypass_rejected"] is True
    assert blocked["malicious_needle_claiming_real_external_action_rejected"] is True


def test_result_proposal_adapter_preserves_needle_reference_and_outcome():
    executions = _executions()
    adapters = _adapters()
    for scenario, execution in executions.items():
        adapter = adapters[scenario]
        assert adapter["result_proposal_created"] is True
        assert adapter["source_needle_execution_result_id"] == execution[
            "needle_execution_result_id"
        ]
        assert adapter["result_status"] == execution["execution_status"]
        assert adapter["final_output_claim"] is False
        assert adapter["drs_write_claim"] is False
        assert adapter["real_external_action_claim"] is False


def test_post_vv_gt_and_root_are_not_bypassed():
    for row in _report().post_vv_gt_root_final:
        assert row["post_vv_bypassed"] is False
        assert row["gt_bypassed"] is False
        assert row["root_bypassed"] is False
        assert row["root_final_artifact_created"] is True
        assert row["root_is_only_final_output_authority"] is True


def test_authority_and_safety_boundaries():
    authority = _report().authority_safety
    assert authority["needleruntime_is_authority"] is False
    assert authority["needle_execution_result_is_final_truth"] is False
    assert authority["root_remains_authority"] is True
    assert authority["root_is_only_final_output_authority"] is True
    assert authority["needle_created_final_output"] is False
    assert authority["needle_wrote_drs"] is False
    assert authority["needle_bypassed_root"] is False
    assert authority["production_external_action_executed"] is False
    assert authority["production_persistence_claimed"] is False
    assert authority["global_drs_implemented"] is False
    assert authority["external_drs_network_implemented"] is False
    assert authority["telegram_action_executed"] is False
    assert authority["marennya_invoked"] is False
    assert authority["up_invoked"] is False


def test_pass_summary_is_derived_from_scenarios_and_authority():
    report = _report()
    summary = report.summary
    derived_pass = (
        summary["scenarios_verified"] == len(SCENARIOS_UNDER_TEST) == 11
        and summary["completed_scenarios"] == 1
        and summary["degraded_scenarios"] == 1
        and summary["blocked_or_failed_scenarios"] == 4
        and summary["malicious_claims_rejected"] == 4
        and summary["raw_needleruntime_output_blocked"] is True
        and summary["needleruntime_is_authority"] is False
        and summary["root_remains_authority"] is True
        and summary["root_is_only_final_output_authority"] is True
        and summary["no_real_external_actions"] is True
        and summary["no_drs_write_by_needle"] is True
        and summary["no_production_persistence"] is True
    )
    assert derived_pass is True
    assert summary["root_native_sandbox_needleruntime_e2e_status"] == "PASS"
    assert summary["ready_for_drs_lifecycle_semantics_v0_2"] is True
    assert summary["production_autonomy_claimed"] is False
