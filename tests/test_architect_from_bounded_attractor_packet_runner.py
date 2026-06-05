from __future__ import annotations

from demo.run_architect_from_bounded_attractor_packet import (
    collect_architect_from_bounded_attractor_packet,
    run_architect_from_bounded_attractor_packet,
)


def _filters_by_scenario():
    report = collect_architect_from_bounded_attractor_packet()
    return {row["scenario"]: row for row in report.architect_input_filter}


def _proposals_by_scenario():
    report = collect_architect_from_bounded_attractor_packet()
    return {proposal["scenario"]: proposal for proposal in report.architect_plan_proposals}


def test_runner_output_contains_title():
    output = run_architect_from_bounded_attractor_packet()

    assert "[ARCHITECT FROM BOUNDED ATTRACTOR PACKET]" in output
    assert "[INPUT ATTRACTOR PACKETS]" in output
    assert "[ARCHITECT INPUT FILTER]" in output
    assert "[ARCHITECT PLAN PROPOSALS]" in output
    assert "[CONTAINMENT]" in output
    assert "[AUTHORITY / SAFETY]" in output
    assert "[SUMMARY]" in output


def test_source_avf_status_is_pass():
    report = collect_architect_from_bounded_attractor_packet()

    assert report.input_attractor_packets["source_avf_report_status"] == "PASS"
    assert report.summary["source_avf_attractor_status"] == "PASS"
    assert report.input_attractor_packets["accepted_matrix_packets"] == 1
    assert report.input_attractor_packets["downgraded_matrix_packets"] == 1
    assert report.input_attractor_packets["rejected_matrix_packets"] == 0


def test_accepted_packet_creates_valid_architect_plan_graph_proposal():
    filter_row = _filters_by_scenario()["accepted_packet_architect_plan_valid"]
    proposal = _proposals_by_scenario()["accepted_packet_architect_plan_valid"]

    assert filter_row["architect_invoked"] is True
    assert filter_row["input_is_bounded_attractor_packet"] is True
    assert proposal["input_is_bounded_attractor_packet"] is True
    assert proposal["plan_graph_present"] is True
    assert proposal["plan_graph_contract_checked"] is True
    assert proposal["plan_graph_contract_valid"] is True
    assert proposal["created_by"] == "architect"
    assert proposal["nodes"]
    assert proposal["forbidden_vectors_absent"] is True
    assert proposal["architect_creates_final_output"] is False
    assert proposal["architect_writes_drs"] is False
    assert proposal["architect_executes_actions"] is False
    assert proposal["executor_invoked"] is False


def test_downgraded_packet_creates_limited_valid_architect_plan_graph_proposal():
    proposal = _proposals_by_scenario()["downgraded_packet_architect_plan_limited"]

    assert proposal["plan_graph_contract_valid"] is True
    assert "missing_guard:ReuseGate boundary" in proposal["downgraded_claims_visible"]
    assert all(node["vector_id"] != "official_online_request" for node in proposal["nodes"])
    assert proposal["forbidden_vectors_absent"] is True
    assert proposal["executor_invoked"] is False


def test_rejected_matrix_never_reaches_architect():
    filter_row = _filters_by_scenario()["rejected_matrix_never_reaches_architect"]

    assert filter_row["architect_invoked"] is False
    assert filter_row["blocked_before_architect"] is True
    assert "rejected_matrix_not_allowed" in filter_row["block_reasons"]
    assert filter_row["rejected_matrix_received"] is False
    assert filter_row["raw_orchestrator_matrix_received"] is False


def test_raw_orchestrator_matrix_is_blocked():
    filter_row = _filters_by_scenario()["raw_orchestrator_matrix_blocked"]

    assert filter_row["architect_invoked"] is False
    assert filter_row["blocked_before_architect"] is True
    assert "raw_orchestrator_matrix_not_allowed" in filter_row["block_reasons"]


def test_raw_user_intent_is_blocked():
    filter_row = _filters_by_scenario()["raw_user_intent_blocked"]

    assert filter_row["input_kind"] == "raw_user_intent"
    assert filter_row["architect_invoked"] is False
    assert filter_row["blocked_before_architect"] is True
    assert "raw_unchecked_user_intent_not_allowed" in filter_row["block_reasons"]
    assert filter_row["input_is_bounded_attractor_packet"] is False
    assert filter_row["raw_orchestrator_matrix_received"] is False
    assert filter_row["raw_user_intent_received"] is False
    assert filter_row["rejected_matrix_received"] is False


def test_invalid_unbounded_attractor_packet_is_blocked():
    filter_row = _filters_by_scenario()["invalid_attractor_packet_blocked"]

    assert filter_row["architect_invoked"] is False
    assert filter_row["blocked_before_architect"] is True
    assert "invalid_or_unbounded_attractor_packet" in filter_row["block_reasons"]


def test_invalid_architect_artifact_is_contained():
    report = collect_architect_from_bounded_attractor_packet()
    proposal = _proposals_by_scenario()["invalid_architect_artifact_contained"]

    assert proposal["plan_graph_contract_checked"] is True
    assert proposal["plan_graph_contract_valid"] is False
    assert report.containment["invalid_architect_artifact_caught"] is True
    assert report.containment["invalid_architect_reached_executor"] is False
    assert report.containment["invalid_architect_created_final_output"] is False
    assert report.containment["invalid_architect_wrote_drs"] is False


def test_plan_graph_contract_is_checked():
    report = collect_architect_from_bounded_attractor_packet()

    assert report.authority_safety["plan_graph_contract_required"] is True
    assert report.authority_safety["plan_graph_contract_checked"] is True
    assert all(
        proposal["plan_graph_contract_checked"]
        for proposal in report.architect_plan_proposals
    )


def test_architect_does_not_receive_raw_orchestrator_matrix():
    authority = collect_architect_from_bounded_attractor_packet().authority_safety

    assert authority["architect_receives_raw_orchestrator_matrix"] is False


def test_architect_does_not_receive_raw_user_intent():
    authority = collect_architect_from_bounded_attractor_packet().authority_safety

    assert authority["architect_receives_raw_user_intent"] is False


def test_architect_does_not_receive_rejected_matrix():
    authority = collect_architect_from_bounded_attractor_packet().authority_safety

    assert authority["architect_receives_rejected_matrix"] is False


def test_architect_does_not_create_final_output():
    authority = collect_architect_from_bounded_attractor_packet().authority_safety

    assert authority["architect_creates_final_output"] is False
    assert authority["production_final_output_created"] is False


def test_architect_does_not_write_drs():
    authority = collect_architect_from_bounded_attractor_packet().authority_safety

    assert authority["architect_writes_drs"] is False


def test_architect_does_not_execute_actions():
    authority = collect_architect_from_bounded_attractor_packet().authority_safety

    assert authority["architect_executes_actions"] is False


def test_executor_is_not_invoked():
    authority = collect_architect_from_bounded_attractor_packet().authority_safety

    assert authority["executor_invoked"] is False


def test_post_vv_is_not_invoked():
    authority = collect_architect_from_bounded_attractor_packet().authority_safety

    assert authority["post_vv_invoked"] is False


def test_gt_is_not_invoked():
    authority = collect_architect_from_bounded_attractor_packet().authority_safety

    assert authority["gt_invoked"] is False


def test_no_production_external_actions():
    authority = collect_architect_from_bounded_attractor_packet().authority_safety

    assert authority["production_external_action_executed"] is False


def test_no_global_or_external_drs():
    authority = collect_architect_from_bounded_attractor_packet().authority_safety

    assert authority["global_drs_implemented"] is False
    assert authority["external_drs_network_implemented"] is False


def test_marennya_and_up_not_invoked():
    authority = collect_architect_from_bounded_attractor_packet().authority_safety

    assert authority["marennya_invoked"] is False
    assert authority["up_invoked"] is False


def test_pass_summary_derived_from_source_proposals_blocks_and_boundaries():
    report = collect_architect_from_bounded_attractor_packet()
    valid_proposals = [
        proposal for proposal in report.architect_plan_proposals
        if proposal["plan_graph_contract_valid"]
    ]
    expected_pass = (
        report.input_attractor_packets["source_avf_report_status"] == "PASS"
        and len(report.architect_input_filter) == report.summary["scenarios_verified"]
        and report.summary["valid_plan_graph_proposals_created"] == len(valid_proposals)
        and report.summary["accepted_packet_plan_proposals"] == 1
        and report.summary["downgraded_packet_plan_proposals"] == 1
        and report.summary["raw_orchestrator_matrix_blocked"] is True
        and report.summary["raw_user_intent_blocked"] is True
        and report.summary["rejected_matrix_blocked"] is True
        and report.summary["invalid_packet_blocked"] is True
        and report.summary["invalid_architect_artifact_contained"] is True
        and report.authority_safety["architect_receives_only_bounded_attractor_packet"]
        and not report.authority_safety["executor_invoked"]
        and not report.authority_safety["production_final_output_created"]
        and not report.authority_safety["production_external_action_executed"]
    )

    assert report.summary["architect_from_bounded_attractor_packet_status"] == "PASS"
    assert expected_pass is True
    assert report.summary["ready_for_dag_executor_from_valid_plan_graph"] is True
