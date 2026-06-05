from __future__ import annotations

import demo.run_controlled_orchestrator_matrix_gate as gate
from demo.run_controlled_orchestrator_matrix_gate import (
    ORDERED_LIVE_SUCCESS_MARKERS,
    collect_controlled_orchestrator_matrix_gate,
    run_controlled_orchestrator_matrix_gate,
    _verify_ordered_live_success_report,
)


def _decisions_by_scenario():
    report = collect_controlled_orchestrator_matrix_gate()
    return {decision["scenario"]: decision for decision in report.gate_decisions}


def test_runner_output_contains_title():
    output = run_controlled_orchestrator_matrix_gate()

    assert "[CONTROLLED ORCHESTRATOR MATRIX GATE]" in output
    assert "[INPUT MATRICES]" in output
    assert "[GATE DECISIONS]" in output
    assert "[ROOT AUTHORITY]" in output
    assert "[BOUNDARY CHECKS]" in output
    assert "[ORDERED LIVE GEMINI CONTEXT]" in output
    assert "[SUMMARY]" in output


def test_all_7_scenarios_exist():
    report = collect_controlled_orchestrator_matrix_gate()

    assert report.summary["scenarios_verified"] == 7
    assert {
        "valid_matrix_accept",
        "missing_temporal_query_reject",
        "incomplete_guards_downgrade_or_reject",
        "wrong_downstream_actors_reject",
        "forbidden_bypass_reject",
        "high_confidence_policy_block",
        "fallback_route_visible",
    } == {decision["scenario"] for decision in report.gate_decisions}


def test_valid_matrix_accept_is_accepted():
    decision = _decisions_by_scenario()["valid_matrix_accept"]

    assert decision["gate_decision"] == "accept"
    assert decision["accepted_for_future_avf"] is True
    assert decision["root_gate_reason"] == "valid_matrix"
    assert decision["temporal_query_ok"] is True
    assert decision["guard_set_complete"] is True
    assert decision["downstream_actors_complete"] is True
    assert decision["proposal_only"] is True


def test_missing_temporal_query_reject_is_rejected():
    decision = _decisions_by_scenario()["missing_temporal_query_reject"]

    assert decision["gate_decision"] == "reject"
    assert decision["accepted_for_future_avf"] is False
    assert "missing_or_false_temporal_query" in decision["rejection_reasons"]
    assert decision["temporal_query_ok"] is False
    assert decision["architect_reached"] is False
    assert decision["avf_invoked"] is False


def test_incomplete_guards_scenario_is_downgraded_by_explicit_policy():
    decision = _decisions_by_scenario()["incomplete_guards_downgrade_or_reject"]

    assert decision["gate_decision"] == "downgrade"
    assert decision["accepted_for_future_avf"] is True
    assert decision["downgraded_matrix_created"] is True
    assert decision["unsafe_claims_removed"] is True
    assert "incomplete_guard_set" in decision["downgrade_reasons"]
    assert decision["missing_guards"] == ["ReuseGate boundary"]


def test_wrong_downstream_actors_reject_reports_missing_and_extra_actors():
    decision = _decisions_by_scenario()["wrong_downstream_actors_reject"]

    assert decision["gate_decision"] == "reject"
    assert decision["accepted_for_future_avf"] is False
    assert "downstream_actors_incomplete" in decision["rejection_reasons"]
    assert decision["missing_downstream_actors"] == ["Post V&V"]
    assert decision["extra_downstream_actors"] == ["PostVV"]
    assert decision["architect_reached"] is False
    assert decision["avf_invoked"] is False


def test_forbidden_bypass_reject_is_rejected():
    decision = _decisions_by_scenario()["forbidden_bypass_reject"]

    assert decision["gate_decision"] == "reject"
    assert decision["forbidden_bypass_detected"] is True
    assert "forbidden_bypass_attempt" in decision["rejection_reasons"]
    assert decision["accepted_for_future_avf"] is False


def test_high_confidence_policy_block_is_rejected_despite_high_confidence():
    decision = _decisions_by_scenario()["high_confidence_policy_block"]

    assert decision["gate_decision"] == "reject"
    assert decision["forbidden_bypass_detected"] is True
    assert decision["high_confidence_overrides_policy"] is False
    assert decision["policy_beats_orchestrator_confidence"] is True


def test_fallback_route_visible_but_not_executed():
    decision = _decisions_by_scenario()["fallback_route_visible"]

    assert decision["gate_decision"] == "reject"
    assert decision["fallback_route_visible"] is True
    assert decision["fallback_route_executed"] is False
    assert decision["accepted_for_future_avf"] is False


def test_root_creates_all_gate_decisions_and_matrix_is_not_authority():
    report = collect_controlled_orchestrator_matrix_gate()

    assert report.root_authority["root_created_gate_decisions"] is True
    assert all(decision["created_by"] == "root_orchestrator" for decision in report.gate_decisions)
    assert report.root_authority["orchestrator_matrix_is_authority"] is False


def test_root_may_accept_reject_and_downgrade():
    root = collect_controlled_orchestrator_matrix_gate().root_authority

    assert root["root_may_accept"] is True
    assert root["root_may_reject"] is True
    assert root["root_may_downgrade"] is True


def test_avf_and_attractor_are_not_invoked():
    boundary = collect_controlled_orchestrator_matrix_gate().boundary_checks

    assert boundary["avf_invoked"] is False
    assert boundary["attractor_packet_created"] is False


def test_architect_is_not_reached_from_rejected_matrix():
    boundary = collect_controlled_orchestrator_matrix_gate().boundary_checks

    assert boundary["architect_reached_from_rejected_matrix"] is False


def test_no_production_final_output_or_external_action():
    boundary = collect_controlled_orchestrator_matrix_gate().boundary_checks

    assert boundary["production_final_output_created"] is False
    assert boundary["production_external_action_executed"] is False
    assert boundary["executor_reached"] is False
    assert boundary["post_vv_reached"] is False
    assert boundary["gt_reached"] is False


def test_orchestrator_drs_write_and_final_output_are_false():
    boundary = collect_controlled_orchestrator_matrix_gate().boundary_checks

    assert boundary["orchestrator_wrote_drs"] is False
    assert boundary["orchestrator_created_final_output"] is False


def test_global_external_drs_false():
    boundary = collect_controlled_orchestrator_matrix_gate().boundary_checks

    assert boundary["global_drs_implemented"] is False
    assert boundary["external_drs_network_implemented"] is False


def test_marennya_and_up_not_invoked():
    boundary = collect_controlled_orchestrator_matrix_gate().boundary_checks

    assert boundary["marennya_invoked"] is False
    assert boundary["up_invoked"] is False


def test_ordered_live_gemini_context_verifies_success_report():
    context = collect_controlled_orchestrator_matrix_gate().ordered_live_gemini_context

    assert context["ordered_live_gemini_smoke_available"] is True
    assert context["success_report_exists"] is True
    assert context["success_report_verified"] is True
    assert context["success_report_missing_markers"] == []
    assert context["ordered_live_context_mode"] == "success_report_verified"
    assert context["ordered_live_roles_preserved"] is True
    assert context["live_orchestrator_can_create_valid_matrix"] is True
    assert context["live_architect_can_create_valid_artifact"] is True
    assert context["success_report_path"].endswith(
        "auditor_live_gemini_ordered_orchestrator_architect_25_success_report.log"
    )


def test_missing_ordered_live_success_report_is_not_verified(monkeypatch, tmp_path):
    missing_report = tmp_path / "missing_ordered_success.log"
    monkeypatch.setattr(gate, "SUCCESS_REPORT_PATH", str(missing_report))

    report = gate.collect_controlled_orchestrator_matrix_gate()
    context = report.ordered_live_gemini_context

    assert context["success_report_exists"] is False
    assert context["success_report_verified"] is False
    assert context["success_report_missing_markers"] == list(ORDERED_LIVE_SUCCESS_MARKERS)
    assert context["ordered_live_context_mode"] == "documented_success_report_reference_unverified"
    assert context["live_orchestrator_can_create_valid_matrix"] is False
    assert context["live_architect_can_create_valid_artifact"] is False
    assert report.summary["controlled_orchestrator_matrix_gate_status"] == "FAIL"


def test_fallback_style_success_report_missing_marker_is_not_verified(tmp_path):
    fallback_report = tmp_path / "fallback_report.log"
    fallback_report.write_text(
        "\n".join(
            marker
            for marker in ORDERED_LIVE_SUCCESS_MARKERS
            if marker != "orchestrator_active_proposal_is_fallback: false"
        ),
        encoding="utf-8",
    )

    verification = _verify_ordered_live_success_report(str(fallback_report))

    assert verification["success_report_exists"] is True
    assert verification["success_report_verified"] is False
    assert verification["success_report_missing_markers"] == [
        "orchestrator_active_proposal_is_fallback: false"
    ]


def test_pass_summary_is_derived_from_scenario_and_boundary_facts():
    report = collect_controlled_orchestrator_matrix_gate()
    accepted = sum(1 for decision in report.gate_decisions if decision["gate_decision"] == "accept")
    rejected = sum(1 for decision in report.gate_decisions if decision["gate_decision"] == "reject")
    downgraded = sum(1 for decision in report.gate_decisions if decision["gate_decision"] == "downgrade")
    expected_pass = (
        len(report.gate_decisions) == 7
        and accepted == report.summary["accepted_count"]
        and rejected == report.summary["rejected_count"]
        and downgraded == report.summary["downgraded_count"]
        and report.root_authority["root_created_gate_decisions"]
        and not report.boundary_checks["avf_invoked"]
        and not report.boundary_checks["production_final_output_created"]
        and not report.boundary_checks["production_external_action_executed"]
        and not report.boundary_checks["orchestrator_wrote_drs"]
        and report.ordered_live_gemini_context["success_report_verified"]
    )

    assert report.summary["controlled_orchestrator_matrix_gate_status"] == "PASS"
    assert expected_pass is True
    assert report.summary["accepted_count"] == 1
    assert report.summary["rejected_count"] == 5
    assert report.summary["downgraded_count"] == 1
    assert report.summary["ready_for_avf_attractor_from_accepted_matrix"] is True
