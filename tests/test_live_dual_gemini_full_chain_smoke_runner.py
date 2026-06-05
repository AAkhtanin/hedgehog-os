from __future__ import annotations

import demo.run_live_dual_gemini_full_chain_smoke as smoke
from demo.run_live_dual_gemini_full_chain_smoke import (
    PLAN_SCHEMA,
    collect_live_dual_gemini_full_chain_smoke,
    fake_live_architect_plan,
    fake_live_orchestrator_matrix,
    run_live_dual_gemini_full_chain_smoke,
)


def _valid_fake_report():
    matrix = fake_live_orchestrator_matrix()
    packet_stub = {
        "packet_id": f"attractor_packet_{matrix['matrix_id']}",
        "source_gate_decision_id": f"root_gate_decision_{matrix['matrix_id']}",
        "source_matrix_id": matrix["matrix_id"],
    }
    return collect_live_dual_gemini_full_chain_smoke(
        live_requested=True,
        injected_orchestrator_matrix=matrix,
        injected_architect_plan=fake_live_architect_plan(packet_stub),
    )


def test_runner_refuses_live_claim_when_not_live_enabled(monkeypatch):
    monkeypatch.delenv("HEDGEHOG_ALLOW_LIVE_GEMINI", raising=False)
    monkeypatch.delenv("HEDGEHOG_GEMINI_CALL_PAUSE_SECONDS", raising=False)
    output = run_live_dual_gemini_full_chain_smoke(live_requested=False)
    report = collect_live_dual_gemini_full_chain_smoke(live_requested=False)

    assert "[LIVE DUAL-GEMINI FULL CHAIN SMOKE]" in output
    assert "[INPUT]" in output
    assert report.input_live_mode["network_required"] is False
    assert report.input_live_mode["gemini_call_pause_seconds"] == 5.0
    assert report.summary["live_dual_gemini_full_chain_smoke_status"] == (
        "NOT_LIVE_NOT_RUN"
    )
    assert report.summary["both_gemini_roles_live"] is False


def test_fake_live_valid_artifacts_pass_through_one_continuous_chain(monkeypatch):
    monkeypatch.delenv("HEDGEHOG_ALLOW_LIVE_GEMINI", raising=False)
    report = _valid_fake_report()

    assert report.summary["live_dual_gemini_full_chain_smoke_status"] == "PASS"
    assert report.summary["both_gemini_roles_live"] is True
    assert report.summary["orchestrator_live_no_fallback"] is True
    assert report.summary["architect_live_no_fallback"] is True
    assert report.live_orchestrator["orchestrator_matrix_valid"] is True
    assert report.live_architect["architect_plan_graph_valid"] is True
    assert report.summary["one_continuous_chain"] is True
    assert report.summary["root_final_reached"] is True


def test_fake_live_architect_sample_uses_required_node_shape():
    matrix = fake_live_orchestrator_matrix()
    packet_stub = {
        "packet_id": f"attractor_packet_{matrix['matrix_id']}",
        "source_gate_decision_id": f"root_gate_decision_{matrix['matrix_id']}",
        "source_matrix_id": matrix["matrix_id"],
    }
    plan = fake_live_architect_plan(packet_stub)

    assert len(plan["nodes"]) >= 2
    for node in plan["nodes"]:
        assert set(
            [
                "node_id",
                "node_kind",
                "task",
                "depends_on",
                "executor",
                "expected_artifact",
            ]
        ).issubset(node)
    assert plan["edges"] == [
        {"from": "node_collect_requirements", "to": "node_build_trace_plan"}
    ]


def test_architect_prompt_forces_non_empty_nodes_and_node_id():
    packet = {
        "packet_id": "packet_1",
        "source_gate_decision_id": "gate_1",
        "source_matrix_id": "matrix_1",
    }
    prompt = smoke._live_architect_prompt(
        packet, ["nodes_present", "node_missing_node_id"]
    )
    prompt_text = str(prompt)

    assert "nodes must be a non-empty array" in prompt_text
    assert "node_id" in prompt_text
    assert "node_collect_requirements" in prompt_text
    assert "node_build_trace_plan" in prompt_text
    assert "Your previous answer failed because nodes was empty or nodes lacked node_id" in prompt_text


def test_plan_schema_requires_structured_node_items():
    node_schema = PLAN_SCHEMA["properties"]["nodes"]["items"]

    assert PLAN_SCHEMA["properties"]["nodes"]["minItems"] == 2
    assert set(
        [
            "node_id",
            "node_kind",
            "task",
            "depends_on",
            "executor",
            "expected_artifact",
        ]
    ).issubset(node_schema["required"])
    assert node_schema["properties"]["node_id"]["type"] == "string"
    assert node_schema["properties"]["depends_on"]["items"]["type"] == "string"


def test_plan_schema_requires_edge_refs():
    edge_schema = PLAN_SCHEMA["properties"]["edges"]["items"]

    assert set(["from", "to"]).issubset(edge_schema["required"])
    assert edge_schema["properties"]["from"]["type"] == "string"
    assert edge_schema["properties"]["to"]["type"] == "string"


def test_fallback_orchestrator_is_safe_fallback_not_live_success(monkeypatch):
    monkeypatch.delenv("HEDGEHOG_ALLOW_LIVE_GEMINI", raising=False)
    bad_matrix = fake_live_orchestrator_matrix()
    bad_matrix["temporal_query_required"] = False
    packet_stub = {
        "packet_id": "attractor_packet_fallback_matrix_certificate",
        "source_gate_decision_id": "root_gate_decision_fallback_matrix_certificate",
        "source_matrix_id": "fallback_matrix_certificate",
    }
    report = collect_live_dual_gemini_full_chain_smoke(
        live_requested=True,
        injected_orchestrator_matrix=bad_matrix,
        injected_architect_plan=fake_live_architect_plan(packet_stub),
    )

    assert report.live_orchestrator["orchestrator_fallback_used"] is True
    assert report.live_orchestrator["orchestrator_matrix_valid"] is False
    assert "temporal_query_required" in report.live_orchestrator[
        "orchestrator_initial_validation_errors"
    ]
    assert report.live_orchestrator["orchestrator_initial_parse_error"] is None
    assert "temporal_query_required" in report.live_orchestrator[
        "orchestrator_initial_raw_shape_summary"
    ]["top_level_keys"]
    assert report.summary["live_dual_gemini_full_chain_smoke_status"] == (
        "SAFE_FALLBACK_NOT_LIVE_SUCCESS"
    )
    assert report.summary["orchestrator_live_no_fallback"] is False


def test_fallback_architect_is_safe_fallback_not_live_success(monkeypatch):
    monkeypatch.delenv("HEDGEHOG_ALLOW_LIVE_GEMINI", raising=False)
    matrix = fake_live_orchestrator_matrix()
    bad_plan = {"proposal_id": "bad_plan", "source": "live_gemini"}
    report = collect_live_dual_gemini_full_chain_smoke(
        live_requested=True,
        injected_orchestrator_matrix=matrix,
        injected_architect_plan=bad_plan,
    )

    assert report.live_architect["architect_fallback_used"] is True
    assert report.live_architect["architect_plan_graph_valid"] is False
    assert "schema_valid" in report.live_architect[
        "architect_initial_validation_errors"
    ]
    assert "contract_valid" in report.live_architect["plan_graph_contract_errors"]
    assert report.live_architect["architect_initial_parse_error"] is None
    assert report.live_architect["architect_initial_raw_shape_summary"][
        "top_level_keys"
    ] == ["proposal_id", "source"]
    assert report.summary["live_dual_gemini_full_chain_smoke_status"] == (
        "SAFE_FALLBACK_NOT_LIVE_SUCCESS"
    )
    assert report.summary["architect_live_no_fallback"] is False


def test_architect_node_missing_node_id_is_contained_before_executor(monkeypatch):
    monkeypatch.delenv("HEDGEHOG_ALLOW_LIVE_GEMINI", raising=False)
    matrix = fake_live_orchestrator_matrix()
    packet_stub = {
        "packet_id": f"attractor_packet_{matrix['matrix_id']}",
        "source_gate_decision_id": f"root_gate_decision_{matrix['matrix_id']}",
        "source_matrix_id": matrix["matrix_id"],
    }
    bad_plan = fake_live_architect_plan(packet_stub)
    bad_plan["proposal_id"] = "bad_plan_missing_node_id"
    bad_plan["nodes"] = [{"task": "collect certificate requirements"}]
    result_plan_ids: list[str] = []
    original_result_from_plan = smoke._result_from_plan

    def recording_result_from_plan(plan):
        result_plan_ids.append(plan["proposal_id"])
        return original_result_from_plan(plan)

    monkeypatch.setattr(smoke, "_result_from_plan", recording_result_from_plan)

    report = smoke.collect_live_dual_gemini_full_chain_smoke(
        live_requested=True,
        injected_orchestrator_matrix=matrix,
        injected_architect_plan=bad_plan,
    )

    assert report.live_architect["architect_fallback_used"] is True
    assert report.live_architect["architect_plan_graph_valid"] is False
    assert "node_missing_node_id" in report.live_architect[
        "architect_initial_validation_errors"
    ]
    assert "node_missing_node_id" in report.live_architect[
        "plan_graph_contract_errors"
    ]
    assert report.live_architect["architect_initial_node_count"] == 1
    assert report.live_architect["architect_initial_first_node_keys"] == ["task"]
    assert (
        report.live_architect["architect_initial_nodes_missing_node_id_count"] == 1
    )
    assert report.summary["live_dual_gemini_full_chain_smoke_status"] == (
        "SAFE_FALLBACK_NOT_LIVE_SUCCESS"
    )
    assert report.summary["live_dual_gemini_full_chain_smoke_status"] != "PASS"
    assert "bad_plan_missing_node_id" not in result_plan_ids


def test_broken_linkage_fails(monkeypatch):
    monkeypatch.delenv("HEDGEHOG_ALLOW_LIVE_GEMINI", raising=False)
    matrix = fake_live_orchestrator_matrix()
    packet_stub = {
        "packet_id": f"attractor_packet_{matrix['matrix_id']}",
        "source_gate_decision_id": f"root_gate_decision_{matrix['matrix_id']}",
        "source_matrix_id": matrix["matrix_id"],
    }
    report = collect_live_dual_gemini_full_chain_smoke(
        live_requested=True,
        injected_orchestrator_matrix=matrix,
        injected_architect_plan=fake_live_architect_plan(packet_stub),
        break_linkage=True,
    )

    assert report.linkage_proof["result_uses_live_architect_plan"] is False
    assert report.linkage_proof["one_continuous_chain"] is False
    assert report.summary["live_dual_gemini_full_chain_smoke_status"] == "FAIL"


def test_root_remains_only_final_authority():
    report = _valid_fake_report()

    assert report.authority_safety["root_is_only_final_output_authority"] is True
    assert report.authority_safety["root_created_final_output"] is True
    assert report.authority_safety["live_orchestrator_created_final_output"] is False
    assert report.authority_safety["live_architect_created_final_output"] is False
    assert report.authority_safety["gt_created_final_output"] is False


def test_no_drs_writeback():
    report = _valid_fake_report()

    assert report.authority_safety["gemini_wrote_drs"] is False
    assert report.authority_safety["executor_wrote_drs"] is False
    assert report.authority_safety["post_vv_wrote_drs"] is False
    assert report.authority_safety["gt_wrote_drs"] is False
    assert report.authority_safety["root_wrote_drs"] is False
    assert report.authority_safety["drs_writeback_invoked"] is False
    assert report.summary["drs_writeback_invoked"] is False


def test_no_production_persistence():
    report = _valid_fake_report()

    assert report.deterministic_downstream["production_persistence_claimed"] is False
    assert report.summary["production_persistence_claimed"] is False


def test_no_real_external_action():
    report = _valid_fake_report()

    assert report.input_live_mode["real_external_action"] is False
    assert report.authority_safety["gemini_executed_action"] is False
    assert report.authority_safety["production_external_action_executed"] is False
    assert report.summary["production_external_action_executed"] is False


def test_marennya_and_up_not_invoked():
    report = _valid_fake_report()

    assert report.authority_safety["marennya_invoked"] is False
    assert report.authority_safety["up_invoked"] is False


def test_pass_requires_both_live_roles_and_no_fallback():
    report = _valid_fake_report()

    required_success_claim = (
        report.summary["live_dual_gemini_full_chain_smoke_status"] == "PASS"
        and report.summary["both_gemini_roles_live"] is True
        and report.summary["orchestrator_live_no_fallback"] is True
        and report.summary["architect_live_no_fallback"] is True
        and report.summary["one_continuous_chain"] is True
        and report.summary["root_final_reached"] is True
        and report.summary["root_is_only_final_output_authority"] is True
    )

    assert required_success_claim is True
