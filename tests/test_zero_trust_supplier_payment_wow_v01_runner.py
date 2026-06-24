from __future__ import annotations

import subprocess
import sys

import demo.run_zero_trust_supplier_payment_wow_v01 as wow


def test_module_imports_and_main_returns_zero(capsys) -> None:
    assert wow.TITLE == "HEDGEHOG OS — ZERO TRUST SUPPLIER PAYMENT WOW v0.1"
    assert wow.main() == 0
    output = capsys.readouterr().out
    assert wow.TITLE in output
    assert "FINAL STATUS: PASS" in output


def test_command_execution_exits_zero() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "demo.run_zero_trust_supplier_payment_wow_v01"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
    assert wow.TITLE in completed.stdout
    assert "FINAL STATUS: PASS" in completed.stdout


def test_output_includes_sections_scenarios_and_topology() -> None:
    output = wow.render_report()

    required_markers = (
        "Business story summary:",
        "Topology summary:",
        "Evidence summary:",
        "DRS reuse summary:",
        "Actor/fractal branch summary:",
        "Post V&V / GT / Root summary:",
        "Mock approval / mock receipt summary:",
        "Aggregate counters:",
        "Authority boundary summary:",
        "Limitations:",
        "dirty business request",
        "local fake business evidence",
        "semantic evidence intake",
        "local DRS write/resolve",
        "candidate vectors",
        "AVF scoring/ranking",
        "candidate advisory review",
        "bounded actor route",
        "bounded Fractal Cell branch execution",
        "child branch reports return upward",
        "parent Post V&V / GT review",
        "Root final business summary",
        "second-run DRS reuse as candidate only",
    )
    for marker in required_markers:
        assert marker in output

    for scenario_id in wow.SCENARIOS:
        assert scenario_id in output


def test_output_includes_required_counters() -> None:
    output = wow.render_report()

    required_lines = (
        "scenarios_total: 10",
        "scenarios_passed: 10",
        "local_fake_evidence_records_count: 10",
        "real_payment_executed_count: 0",
        "real_shipment_released_count: 0",
        "real_supplier_api_called_count: 0",
        "real_bank_api_called_count: 0",
        "connector_side_effect_count: 0",
        "secrets_accessed_count: 0",
        "network_used_count: 0",
        "gemini_used_count: 0",
        "real_model_call_count: 0",
        "drs_hit_authority_claimed_count: 0",
        "avf_score_authority_claimed_count: 0",
        "advisory_authority_claimed_count: 0",
        "actor_authority_claimed_count: 0",
        "child_cell_authority_claimed_count: 0",
        "non_root_final_output_created_count: 0",
        "bounded_actor_bank_command_count: 0",
        "bounded_actor_supplier_command_count: 0",
        "child_cell_bank_command_count: 0",
        "child_cell_supplier_command_count: 0",
        "stale_memory_forced_payment_count: 0",
        "high_avf_score_overrode_legal_hold_count: 0",
        "conflicting_supplier_provenance_hidden_count: 0",
        "root_final_authority_preserved_count: 10",
    )
    for line in required_lines:
        assert line in output


def test_structured_result_preserves_required_semantics() -> None:
    result = wow.run_all_scenarios()
    scenarios = {item["scenario_id"]: item for item in result["scenarios"]}

    assert result["final_status"] == "PASS"
    assert set(wow.SCENARIOS) == set(scenarios)
    assert scenarios[
        "shipment_release_blocked_by_stock_shortage_and_missing_legal_doc"
    ]["details"]["shipment_release_decision"] == "blocked_for_review"
    assert scenarios[
        "invoice_payment_blocked_by_conflicting_supplier_provenance"
    ]["details"]["conflicting_supplier_provenance_hidden"] is False
    assert scenarios[
        "stale_drs_memory_cannot_release_supplier_payment"
    ]["details"]["stale_memory_forced_payment"] is False
    assert scenarios[
        "high_avf_score_cannot_override_legal_hold"
    ]["details"]["high_avf_score_overrode_legal_hold"] is False
    assert scenarios[
        "bounded_actor_route_cannot_command_bank_or_supplier"
    ]["details"]["bank_commanded_by_actor"] is False
    assert scenarios[
        "bounded_actor_route_cannot_command_bank_or_supplier"
    ]["details"]["supplier_commanded_by_actor"] is False
    assert scenarios[
        "fractal_child_cell_returns_supplier_branch_report_to_parent"
    ]["details"]["child_branch_report"] == "returned_to_parent_root_boundary"
    assert scenarios[
        "fractal_child_cell_returns_supplier_branch_report_to_parent"
    ]["details"]["bank_commanded_by_child_cell"] is False
    assert scenarios[
        "fractal_child_cell_returns_supplier_branch_report_to_parent"
    ]["details"]["supplier_commanded_by_child_cell"] is False
    assert scenarios[
        "post_vv_gt_root_review_blocks_action_without_approval"
    ]["details"]["root_business_summary"] == "blocked_without_mock_approval"
    assert scenarios[
        "second_run_reuses_prior_memory_as_candidate_only"
    ]["details"]["drs_hit_authority_claimed"] is False


def test_mock_receipt_is_local_only_after_approval_and_root_review() -> None:
    result = wow.run_all_scenarios()
    receipt_scenarios = [
        scenario
        for scenario in result["scenarios"]
        if scenario["details"].get("mock_receipt_created")
    ]

    assert len(receipt_scenarios) == 1
    receipt = receipt_scenarios[0]
    assert receipt["scenario_id"] == "mock_human_approval_allows_mock_receipt_only"
    assert receipt["details"]["mock_approval_present"] is True
    assert receipt["details"]["root_review_completed"] is True
    assert receipt["details"]["mock_receipt"] == "local mock receipt"
    assert receipt["details"]["real_payment_executed"] is False
    assert receipt["details"]["real_shipment_released"] is False


def test_all_zero_and_authority_pass_conditions_hold() -> None:
    result = wow.run_all_scenarios()
    counters = result["counters"]

    assert result["pass_conditions"]["scenarios_total_is_10"] is True
    assert result["pass_conditions"]["all_scenarios_passed"] is True
    assert result["pass_conditions"]["zero_real_action_and_external_counters"] is True
    assert result["pass_conditions"]["root_authority_preserved"] is True
    for key in wow.ZERO_COUNTER_KEYS:
        assert counters[key] == 0
    assert counters["root_final_authority_preserved_count"] == counters[
        "scenarios_total"
    ]


def test_output_includes_authority_boundaries_and_limitations() -> None:
    output = wow.render_report()

    required_markers = (
        "warehouse stock evidence is not authority",
        "purchase order is not authority",
        "invoice is not authority",
        "supplier record is not authority",
        "legal/compliance document is not authority by itself",
        "bank/payment slot is not action permission",
        "DRS hit is not authority",
        "stale DRS memory cannot authorize payment",
        "candidate vector is not truth",
        "AVF score is not authority",
        "high AVF score cannot override legal hold",
        "advisory report is not Root Final",
        "bounded actor route cannot command bank or supplier",
        "Fractal Cell is not Root",
        "child branch report is not FinalOutput",
        "child cell output returns to parent/Root boundary",
        "Post V&V / GT remain downstream review",
        "mock human approval is local sandbox signal only",
        "mock receipt is not real payment",
        "mock receipt is not real shipment release",
        "Root remains final authority",
        "Real Semantic Runtime MVP is not complete",
    )
    for marker in required_markers:
        assert marker in output


def test_output_does_not_claim_production_public_or_external_readiness() -> None:
    output = wow.render_report()
    forbidden = (
        "production " + "ready",
        "public auditor " + "ready",
        "production E2E " + "implemented",
        "real payment " + "executed",
        "real shipment " + "released",
        "real supplier API " + "called",
        "real bank API " + "called",
        "secrets " + "accessed",
        "network used: " + "true",
        "Gemini used: " + "true",
        "real model call " + "required",
        "LLM output is " + "authority",
        "runtime " + "complete",
        "Real Semantic Runtime MVP " + "implemented",
        "public launch " + "ready",
        "whitepaper " + "ready",
    )

    for marker in forbidden:
        assert marker not in output
