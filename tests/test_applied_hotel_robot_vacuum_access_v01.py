from __future__ import annotations

import demo.run_applied_hotel_robot_vacuum_access_v01 as demo


def _result():
    return demo.run_applied_hotel_robot_vacuum_access_demo()


def test_module_imports_and_public_api_exists() -> None:
    assert demo.TITLE == "HOTEL ROBOT VACUUM ACCESS DEMO v0.1"
    assert callable(demo.run_applied_hotel_robot_vacuum_access_demo)
    assert callable(demo.render_report)
    assert callable(demo.main)


def test_default_demo_passes_and_root_not_ready() -> None:
    result = _result()
    root = result["root_final_output_boundary"]
    rooms = {room["room_id"]: room for room in result["room_access_evidence"]}

    assert result["final_status"] == "PASS"
    assert root["decision"] == "not_ready"
    assert rooms["R-101"]["candidate_only"] is True
    assert rooms["R-101"]["eligible_signal"] == "explicit_consent_candidate"
    assert "missing_consent" in rooms["R-102"]["block_reasons"]
    assert "vip_private_do_not_enter" in rooms["R-303"]["block_reasons"]
    assert "manual_review_required" in rooms["R-404"]["block_reasons"]
    assert "Robot vacuum may not be sent into all requested rooms" in (
        root["safe_human_summary"]
    )


def test_no_robot_api_door_unlock_dispatch_or_real_effects() -> None:
    result = _result()
    counters = result["counters"]
    root = result["root_final_output_boundary"]

    assert counters["robot_api_called_count"] == 0
    assert counters["door_unlock_called_count"] == 0
    assert counters["robot_dispatch_called_count"] == 0
    assert counters["room_entry_authorized_count"] == 0
    assert counters["action_permission_created_count"] == 0
    assert counters["action_commit_packet_created_count"] == 0
    assert counters["connector_called_count"] == 0
    assert counters["payment_executed_count"] == 0
    assert counters["shipment_released_count"] == 0
    assert counters["real_world_effects_count"] == 0
    assert root["robot_api_called"] is False
    assert root["door_unlock_called"] is False
    assert root["robot_dispatch_called"] is False
    assert root["room_entry_authorized"] is False
    assert root["action_commit_packet_created"] is False


def test_context_packets_validate_and_preserve_authority() -> None:
    result = _result()
    orchestrator_packet = result["orchestrator_route_context_packet"]
    architect_packet = result["architect_plan_context_packet"]

    assert result["orchestrator_route_context_packet_validation"]["accepted"] is True
    assert result["architect_plan_context_packet_validation"]["accepted"] is True
    for packet in (orchestrator_packet, architect_packet):
        assert packet["packet_type"] in (
            "OrchestratorRouteContextPacket",
            "ArchitectPlanContextPacket",
        )
        assert packet["truth_claimed"] is False
        assert packet["authority_claimed"] is False
        assert packet["action_permission_claimed"] is False
        assert packet["final_output_claimed"] is False
        assert packet["connector_command_claimed"] is False
        assert packet["drs_write_claimed"] is False
        assert packet["root_bypass_claimed"] is False
        assert packet["real_world_effects_allowed"] is False
        assert packet["root_final_authority_preserved"] is True
        assert packet["Root remains final authority"] is True


def test_structured_rationales_validate_and_preserve_authority() -> None:
    result = _result()
    orchestrator = result["structured_orchestrator_rationale"]
    architect = result["structured_architect_rationale"]

    assert result["structured_orchestrator_rationale_validation"]["accepted"] is True
    assert result["structured_architect_rationale_validation"]["accepted"] is True
    assert orchestrator["rationale_type"] == "structured_orchestrator_rationale"
    assert architect["rationale_type"] == "structured_architect_rationale"
    for rationale in (orchestrator, architect):
        assert rationale["truth_claimed"] is False
        assert rationale["authority_claimed"] is False
        assert rationale["action_permission_claimed"] is False
        assert rationale["final_output_claimed"] is False
        assert rationale["connector_command_claimed"] is False
        assert rationale["drs_write_claimed"] is False
        assert rationale["action_commit_packet_claimed"] is False
        assert rationale["root_bypass_claimed"] is False
        assert rationale["creates_action_commit_packet"] is False
        assert rationale["calls_connectors"] is False
        assert rationale["root_final_authority_preserved"] is True
        assert rationale["Root remains final authority"] is True
    assert orchestrator["orchestrator_is_root"] is False
    assert architect["architect_is_root"] is False


def test_plan_graph_and_result_proposal_are_not_authority() -> None:
    result = _result()
    plan_graph = result["plan_graph_context"]
    proposal = result["result_proposal"]
    root = result["root_final_output_boundary"]
    counters = result["counters"]

    assert plan_graph["PlanGraph is not authority"] is True
    assert plan_graph["authority_claimed"] is False
    assert plan_graph["action_permission_claimed"] is False
    assert plan_graph["connector_command_claimed"] is False
    assert plan_graph["creates_final_output"] is False
    assert proposal["ResultProposal is not FinalOutput"] is True
    assert proposal["is_final_output"] is False
    assert proposal["creates_final_output"] is False
    assert root["final_output_created_by"] == "Root"
    assert counters["final_output_created_by_root_count"] == 1
    assert counters["final_output_created_by_non_root_count"] == 0


def test_missing_consent_and_privacy_boundary_drive_not_ready() -> None:
    result = _result()
    root = result["root_final_output_boundary"]
    privacy_context = result["privacy_boundary_context"]

    assert "missing_consent" in root["blocked_rooms"]["R-102"]
    assert "vip_private_do_not_enter" in root["blocked_rooms"]["R-303"]
    assert "manual_review_required" in root["blocked_rooms"]["R-404"]
    assert "privacy_boundary" in privacy_context["block_reasons"]
    assert "R-101" in root["candidate_only_rooms"]
    assert root["approved_rooms"] == ()
    assert root["decision"] == "not_ready"


def test_fail_closed_probes_block_unsafe_robot_access() -> None:
    result = _result()
    probes = result["fail_closed_probes"]
    counters = result["counters"]

    assert probes["unsafe_all_rooms_robot_dispatch_probe"]["rejected"] is True
    assert "missing_consent:R-102" in (
        probes["unsafe_all_rooms_robot_dispatch_probe"]["reasons"]
    )
    assert "privacy_boundary:R-303" in (
        probes["unsafe_all_rooms_robot_dispatch_probe"]["reasons"]
    )
    assert probes["vip_private_room_probe"]["rejected"] is True
    assert "vip_private_do_not_enter" in probes["vip_private_room_probe"]["reasons"]
    assert probes["physical_action_claim_probe"]["rejected"] is True
    assert probes["physical_action_claim_probe"]["real_counters_remain_zero"] is True
    assert probes["non_root_final_output_probe"]["rejected"] is True
    assert "non_root_final_output_forbidden" in (
        probes["non_root_final_output_probe"]["reasons"]
    )
    assert counters["robot_api_called_count"] == 0
    assert counters["door_unlock_called_count"] == 0
    assert counters["robot_dispatch_called_count"] == 0
    assert counters["real_world_effects_count"] == 0


def test_report_contains_required_markers() -> None:
    report = demo.render_report(_result())

    for marker in (
        "HOTEL ROBOT VACUUM ACCESS",
        "R-101",
        "R-102",
        "R-303",
        "R-404",
        "missing consent",
        "VIP/private",
        "manual review",
        "robot API called: 0",
        "door unlock called: 0",
        "Root remains final authority",
        "FINAL STATUS: PASS",
    ):
        assert marker in report
