from __future__ import annotations

from demo.run_avf_attractor_from_accepted_matrix import (
    collect_avf_attractor_from_accepted_matrix,
    run_avf_attractor_from_accepted_matrix,
)


def _results_by_scenario():
    report = collect_avf_attractor_from_accepted_matrix()
    return {row["scenario"]: row for row in report.avf_formation_results}


def _packets_by_gate_decision():
    report = collect_avf_attractor_from_accepted_matrix()
    return {packet["gate_decision"]: packet for packet in report.attractor_packets}


def test_runner_output_contains_title():
    output = run_avf_attractor_from_accepted_matrix()

    assert "[AVF ATTRACTOR FROM ACCEPTED MATRIX]" in output
    assert "[INPUT GATE DECISIONS]" in output
    assert "[AVF FORMATION RESULTS]" in output
    assert "[ATTRACTOR PACKETS]" in output
    assert "[AUTHORITY / SAFETY]" in output
    assert "[SUMMARY]" in output


def test_source_matrix_gate_status_is_pass():
    report = collect_avf_attractor_from_accepted_matrix()

    assert report.input_gate_decisions["source_gate_report_status"] == "PASS"
    assert report.summary["source_matrix_gate_status"] == "PASS"
    assert report.input_gate_decisions["accepted_count"] == 1
    assert report.input_gate_decisions["rejected_count"] == 5
    assert report.input_gate_decisions["downgraded_count"] == 1


def test_accepted_matrix_forms_attractor_packet():
    result = _results_by_scenario()["valid_matrix_accept"]
    packet = _packets_by_gate_decision()["accept"]

    assert result["gate_decision"] == "accept"
    assert result["avf_invoked"] is True
    assert result["attractor_packet_created"] is True
    assert result["architect_input_bounded"] is True
    assert result["packet_id"] == packet["packet_id"]
    assert packet["created_by"] == "avf"
    assert packet["candidate_vector_hints_used"]
    assert packet["hardmask_blocks"]
    assert packet["avf_creates_final_output"] is False
    assert packet["avf_writes_drs"] is False
    assert packet["avf_executes_actions"] is False


def test_downgraded_matrix_forms_limited_attractor_packet():
    result = _results_by_scenario()["incomplete_guards_downgrade_or_reject"]
    packet = _packets_by_gate_decision()["downgrade"]

    assert result["gate_decision"] == "downgrade"
    assert result["avf_invoked"] is True
    assert result["attractor_packet_created"] is True
    assert result["architect_input_bounded"] is True
    assert result["missing_guards"] == ["ReuseGate boundary"]
    assert "missing_guard:ReuseGate boundary" in packet["downgraded_claims"]
    assert "official_online_request" in packet["candidate_vector_hints_ignored"]
    assert packet["root_override_applied"] is True


def test_rejected_temporal_matrix_does_not_reach_avf():
    result = _results_by_scenario()["missing_temporal_query_reject"]

    assert result["gate_decision"] == "reject"
    assert result["avf_invoked"] is False
    assert result["attractor_packet_created"] is False
    assert result["rejected_matrix_reached_avf"] is False


def test_high_confidence_policy_block_does_not_form_attractor_packet():
    result = _results_by_scenario()["high_confidence_policy_block"]

    assert result["gate_decision"] == "reject"
    assert result["route_confidence"] == 0.99
    assert result["policy_beats_orchestrator_confidence"] is True
    assert result["hardmask_blocks"]
    assert result["policy_blocks"]
    assert result["avf_invoked"] is False
    assert result["attractor_packet_created"] is False


def test_forbidden_bypass_does_not_form_attractor_packet():
    result = _results_by_scenario()["forbidden_bypass_reject"]

    assert result["gate_decision"] == "reject"
    assert result["forbidden_bypass_detected"] is True
    assert result["avf_invoked"] is False
    assert result["attractor_packet_created"] is False
    assert result["architect_reached"] is False


def test_wrong_downstream_actors_do_not_form_attractor_packet():
    result = _results_by_scenario()["wrong_downstream_actors_reject"]

    assert result["gate_decision"] == "reject"
    assert result["missing_downstream_actors"] == ["Post V&V"]
    assert result["extra_downstream_actors"] == ["PostVV"]
    assert result["avf_invoked"] is False
    assert result["attractor_packet_created"] is False


def test_rejected_matrix_packets_are_zero():
    report = collect_avf_attractor_from_accepted_matrix()

    assert report.summary["rejected_matrix_packets"] == 0
    assert report.summary["rejected_matrices_blocked_before_avf"] is True
    assert all(
        not row["attractor_packet_created"]
        for row in report.avf_formation_results
        if row["gate_decision"] == "reject"
    )


def test_hardmask_beats_orchestrator_confidence():
    authority = collect_avf_attractor_from_accepted_matrix().authority_safety

    assert authority["hardmask_beats_orchestrator_confidence"] is True


def test_policy_beats_orchestrator_confidence():
    authority = collect_avf_attractor_from_accepted_matrix().authority_safety

    assert authority["policy_beats_orchestrator_confidence"] is True


def test_orchestrator_hints_are_not_commands():
    authority = collect_avf_attractor_from_accepted_matrix().authority_safety

    assert authority["orchestrator_hints_are_commands"] is False


def test_avf_remains_independent():
    report = collect_avf_attractor_from_accepted_matrix()

    assert report.authority_safety["avf_independent"] is True
    assert report.summary["avf_independent"] is True


def test_architect_is_not_invoked():
    authority = collect_avf_attractor_from_accepted_matrix().authority_safety

    assert authority["architect_reached"] is False
    assert authority["architect_reached_from_rejected_matrix"] is False


def test_executor_is_not_invoked():
    authority = collect_avf_attractor_from_accepted_matrix().authority_safety

    assert authority["executor_reached"] is False


def test_avf_does_not_create_final_output():
    authority = collect_avf_attractor_from_accepted_matrix().authority_safety

    assert authority["avf_creates_final_output"] is False
    assert authority["production_final_output_created"] is False


def test_avf_does_not_write_drs():
    authority = collect_avf_attractor_from_accepted_matrix().authority_safety

    assert authority["avf_writes_drs"] is False
    assert authority["orchestrator_writes_drs"] is False


def test_no_production_external_actions():
    authority = collect_avf_attractor_from_accepted_matrix().authority_safety

    assert authority["avf_executes_actions"] is False
    assert authority["production_external_action_executed"] is False


def test_no_global_or_external_drs():
    authority = collect_avf_attractor_from_accepted_matrix().authority_safety

    assert authority["global_drs_implemented"] is False
    assert authority["external_drs_network_implemented"] is False


def test_marennya_and_up_not_invoked():
    authority = collect_avf_attractor_from_accepted_matrix().authority_safety

    assert authority["marennya_invoked"] is False
    assert authority["up_invoked"] is False


def test_pass_summary_derived_from_source_packets_and_boundary_facts():
    report = collect_avf_attractor_from_accepted_matrix()
    accepted_packets = [
        packet for packet in report.attractor_packets
        if packet["gate_decision"] == "accept"
    ]
    downgraded_packets = [
        packet for packet in report.attractor_packets
        if packet["gate_decision"] == "downgrade"
    ]
    expected_pass = (
        report.input_gate_decisions["source_gate_report_status"] == "PASS"
        and len(report.avf_formation_results) == report.summary["scenarios_verified"]
        and report.summary["attractor_packets_created"] == len(report.attractor_packets)
        and report.summary["accepted_matrix_packets"] == len(accepted_packets)
        and report.summary["downgraded_matrix_packets"] == len(downgraded_packets)
        and report.summary["rejected_matrix_packets"] == 0
        and report.summary["rejected_matrices_blocked_before_avf"]
        and report.authority_safety["avf_independent"]
        and report.authority_safety["root_gate_before_avf"]
        and not report.authority_safety["architect_reached"]
        and not report.authority_safety["executor_reached"]
        and not report.authority_safety["production_final_output_created"]
        and not report.authority_safety["production_external_action_executed"]
    )

    assert report.summary["avf_attractor_from_accepted_matrix_status"] == "PASS"
    assert expected_pass is True
    assert report.summary["attractor_packets_created"] == 2
    assert report.summary["accepted_matrix_packets"] == 1
    assert report.summary["downgraded_matrix_packets"] == 1
    assert report.summary["ready_for_architect_from_bounded_attractor_packet"] is True
