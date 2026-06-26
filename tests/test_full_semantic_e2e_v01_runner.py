from __future__ import annotations

import json

import demo.run_live_provider_adapter_response_capture_v01 as provider_adapter
import demo.run_full_semantic_e2e_v01 as runner
import demo.run_supplier_payment_live_evidence_integration_v02 as supplier_live
from hedgehog.llm_architect import validate_plan_graph_contract


def _valid_payload(**overrides):
    payload = {
        "source_id": "full-e2e-test-evidence-001",
        "source_kind": "full_semantic_e2e_test_response",
        "extracted_claim": (
            "invoice INV-2042 looks payable, warehouse reports water_filter short by 2, "
            "legal note says insurance certificate may be expired"
        ),
        "confidence": 0.64,
        "uncertainty_notes": ["test fixture is untrusted"],
        "provenance_notes": ["source:test_response_file"],
        "contradiction_flags": ["stock_conflict", "legal_hold"],
        "freshness_hint": "test_fixture_current",
        "unsafe_instruction_flags": [],
        "action_requested": "pay_and_release",
        "action_permission_claimed": False,
        "authority_claimed": False,
        "truth_claimed": False,
        "final_output_claimed": False,
        "connector_command_claimed": False,
        "root_review_required": True,
    }
    payload.update(overrides)
    return payload


def _response_file_env(tmp_path, payload_text):
    path = tmp_path / "full_e2e_response.json"
    path.write_text(payload_text, encoding="utf-8")
    return {
        supplier_live.ENV_ENABLE: "1",
        supplier_live.ENV_RESPONSE_FILE: str(path),
    }


def _full_e2e_live_env(tmp_path, **overrides):
    env = {
        runner.ENV_FULL_E2E_LIVE_EVIDENCE: "1",
        provider_adapter.ENV_CAPTURE: "1",
        provider_adapter.ENV_PROVIDER_NAME: "gemini",
        provider_adapter.ENV_PROVIDER_MODEL: "full-e2e-live-test-model",
        provider_adapter.ENV_OUTPUT_DIR: str(tmp_path),
        provider_adapter.ENV_CAPTURE_ID: "full-e2e-live-test",
    }
    env.update(overrides)
    return env


def _provider_returning(raw_text):
    def provider(prompt, model_name, timeout_seconds, env):
        assert "Extract one bounded SemanticEvidenceClaim-compatible JSON object." in prompt
        assert model_name == "full-e2e-live-test-model"
        assert timeout_seconds >= 1
        assert env[provider_adapter.ENV_PROVIDER_NAME] == "gemini"
        return raw_text

    return provider


def _scenario_statuses(result):
    return {item["scenario_id"]: item["status"] for item in result["scenarios"]}


def test_module_imports_and_public_api_exists() -> None:
    assert runner.TITLE == "HEDGEHOG OS - FULL SEMANTIC E2E v0.1"
    assert callable(runner.run_full_semantic_e2e)
    assert callable(runner.render_report)
    assert callable(runner.main)


def test_default_runner_returns_pass_and_runs_deterministic_full_spine() -> None:
    result = runner.run_full_semantic_e2e(env={})
    counters = result["counters"]
    statuses = _scenario_statuses(result)

    assert result["final_status"] == "PASS"
    assert statuses["no_config_runs_deterministic_full_spine_without_live_provider"] == "PASS"
    assert counters["full_semantic_e2e_invoked_count"] == 1
    assert counters["live_evidence_lane_invoked_count"] == 1
    assert counters["live_model_call_count"] == 0
    assert counters["network_used_count"] == 0
    assert counters["gemini_called_count"] == 0
    assert counters["secrets_logged_count"] == 0
    assert counters["full_e2e_live_evidence_mode_count"] == 0
    assert counters["live_provider_adapter_invoked_count"] == 0
    assert counters["raw_provider_response_artifact_created_count"] == 0
    assert counters["raw_provider_response_validated_count"] == 0
    assert counters["live_evidence_semantic_claim_created_count"] == 0


def test_default_main_exits_zero_and_prints_pass(monkeypatch, capsys) -> None:
    monkeypatch.delenv(runner.ENV_FULL_E2E_LIVE_EVIDENCE, raising=False)
    monkeypatch.delenv(supplier_live.ENV_ENABLE, raising=False)
    monkeypatch.delenv(supplier_live.ENV_RESPONSE_FILE, raising=False)
    monkeypatch.delenv(supplier_live.ENV_OUTPUT_DIR, raising=False)

    assert runner.main() == 0
    output = capsys.readouterr().out
    assert runner.TITLE in output
    assert "FINAL STATUS: PASS" in output


def test_explicit_fake_live_evidence_mode_invokes_adapter_and_creates_artifact(tmp_path) -> None:
    result = runner.run_full_semantic_e2e(
        env=_full_e2e_live_env(tmp_path),
        provider=_provider_returning(json.dumps(_valid_payload())),
    )
    counters = result["counters"]
    upstream = result["supplier_live_result"]["provider_adapter_result"]

    assert result["final_status"] == "PASS"
    assert counters["full_e2e_live_evidence_mode_count"] == 1
    assert counters["live_provider_adapter_invoked_count"] == 1
    assert counters["raw_provider_response_artifact_created_count"] == 1
    assert counters["raw_provider_response_validated_count"] == 1
    assert counters["live_evidence_semantic_claim_created_count"] == 1
    assert counters["live_evidence_claim_candidate_only_count"] == 1
    assert counters["provider_output_used_as_truth_count"] == 0
    assert counters["provider_output_used_as_authority_count"] == 0
    assert counters["provider_final_output_created_count"] == 0
    assert counters["bounded_gemini_actor_role_started_count"] == 0
    assert counters["payment_executed_count"] == 0
    assert counters["shipment_released_count"] == 0
    assert counters["connector_called_count"] == 0
    assert counters["live_model_call_count"] == 0
    assert counters["network_used_count"] == 0
    assert counters["gemini_called_count"] == 0
    assert len(upstream["artifacts"]) == 2
    for artifact in upstream["artifacts"]:
        assert (tmp_path / artifact.split("/")[-1]).exists()


def test_validated_live_evidence_enters_full_e2e_as_candidate_only(tmp_path) -> None:
    result = runner.run_full_semantic_e2e(
        env=_full_e2e_live_env(tmp_path),
        provider=_provider_returning(json.dumps(_valid_payload())),
    )
    claim = result["semantic_evidence_claim"]
    supplier_context = result["supplier_payment_context"]

    assert claim["candidate_only"] is True
    assert claim["truth_claimed"] is False
    assert claim["authority_claimed"] is False
    assert claim["action_permission_claimed"] is False
    assert claim["final_output_claimed"] is False
    assert supplier_context["claim_added_as"] == "candidate-only SemanticEvidenceClaim"
    assert supplier_context["provider_output_entered_full_e2e_after_response_file_validation"] is True
    assert result["root_final_output_boundary"]["source_claim_is_candidate_only"] is True
    assert result["root_final_output_boundary"]["provider_output_used_as_truth"] is False
    assert result["counters"]["live_evidence_root_final_authority_preserved_count"] == 1
    assert result["counters"]["root_final_authority_preserved_count"] == 1


def test_unsafe_live_provider_output_fails_closed_before_root(tmp_path) -> None:
    result = runner.run_full_semantic_e2e(
        env=_full_e2e_live_env(tmp_path),
        provider=_provider_returning(json.dumps(_valid_payload(authority_claimed=True))),
    )
    counters = result["counters"]

    assert result["final_status"] == "FAIL_CLOSED"
    assert "authority_claimed_must_be_false" in result["validation_errors"]
    assert counters["full_e2e_live_evidence_mode_count"] == 1
    assert counters["live_provider_adapter_invoked_count"] == 1
    assert counters["raw_provider_response_artifact_created_count"] == 1
    assert counters["raw_provider_response_validated_count"] == 0
    assert counters["live_evidence_semantic_claim_created_count"] == 0
    assert counters["root_final_output_created_count"] == 0
    assert counters["payment_executed_count"] == 0
    assert counters["shipment_released_count"] == 0
    assert counters["connector_called_count"] == 0


def test_stage_map_contains_all_required_stages() -> None:
    result = runner.run_full_semantic_e2e(env={})

    assert tuple(result["stage_map"]) == runner.STAGES
    for stage in result["stage_map"].values():
        assert stage["status"] in {"invoked", "represented", "skipped", "fail_closed"}
        assert stage["authority"] in {"none", "candidate", "advisory", "root_only"}
        assert "creates_final_output" in stage
        assert stage["notes"]


def test_only_root_final_output_boundary_creates_final_output() -> None:
    result = runner.run_full_semantic_e2e(env={})
    creators = [
        name
        for name, stage in result["stage_map"].items()
        if stage["creates_final_output"]
    ]

    assert creators == ["root_final_output_boundary"]
    assert result["root_final_output_boundary"]["created_by"] == "root_boundary"
    assert result["counters"]["root_final_output_created_count"] == 1


def test_slice1_stages_are_invoked() -> None:
    result = runner.run_full_semantic_e2e(env={})
    counters = result["counters"]
    stage_map = result["stage_map"]

    assert stage_map["drs_resolve_reuse"]["status"] == "invoked"
    assert stage_map["candidate_vector_generation"]["status"] == "invoked"
    assert stage_map["avf_scoring"]["status"] == "invoked"
    assert stage_map["advisory_review"]["status"] == "invoked"
    assert counters["drs_resolve_invoked_count"] == 1
    assert counters["drs_resolve_represented_count"] == 0
    assert counters["candidate_vector_invoked_count"] == 1
    assert counters["candidate_vector_represented_count"] == 0
    assert counters["avf_invoked_count"] == 1
    assert counters["avf_represented_count"] == 0
    assert counters["advisory_invoked_count"] == 1
    assert counters["advisory_represented_count"] == 0
    assert counters["slice1_core_promoted_count"] == 4


def test_slice2_stages_are_invoked() -> None:
    result = runner.run_full_semantic_e2e(env={})
    counters = result["counters"]
    stage_map = result["stage_map"]

    assert stage_map["bounded_orchestrator"]["status"] == "invoked"
    assert stage_map["architect"]["status"] == "invoked"
    assert stage_map["plangraph"]["status"] == "invoked"
    assert stage_map["fractal_cell_executor_branch"]["status"] == "invoked"
    assert counters["bounded_orchestrator_invoked_count"] == 1
    assert counters["bounded_orchestrator_represented_count"] == 0
    assert counters["architect_invoked_count"] == 1
    assert counters["architect_represented_count"] == 0
    assert counters["plangraph_invoked_count"] == 1
    assert counters["plangraph_represented_count"] == 0
    assert counters["fractal_branch_invoked_count"] == 1
    assert counters["fractal_branch_represented_count"] == 0
    assert counters["executor_invoked_count"] == 1
    assert counters["executor_represented_count"] == 0
    assert counters["slice2_core_promoted_count"] == 5

    assert result["pass_conditions"]["represented_counts_honest"] is True


def test_slice3_stages_are_invoked() -> None:
    result = runner.run_full_semantic_e2e(env={})
    counters = result["counters"]
    stage_map = result["stage_map"]

    assert stage_map["result_proposal"]["status"] == "invoked"
    assert stage_map["post_vv"]["status"] == "invoked"
    assert stage_map["gt_lgt"]["status"] == "invoked"
    assert stage_map["root_final_output_boundary"]["status"] == "invoked"
    assert stage_map["drs_writeback"]["status"] == "invoked"
    assert counters["result_proposal_invoked_count"] == 1
    assert counters["result_proposal_represented_count"] == 0
    assert counters["post_vv_invoked_count"] == 1
    assert counters["post_vv_represented_count"] == 0
    assert counters["gt_lgt_invoked_count"] == 1
    assert counters["gt_lgt_represented_count"] == 0
    assert counters["drs_writeback_invoked_count"] == 1
    assert counters["drs_writeback_represented_count"] == 0
    assert counters["slice3_core_promoted_count"] == 5
    assert result["pass_conditions"]["represented_counts_honest"] is True


def test_semantic_evidence_claim_remains_candidate_only() -> None:
    result = runner.run_full_semantic_e2e(env={})
    claim = result["semantic_evidence_claim"]

    assert claim["candidate_only"] is True
    assert claim["truth_claimed"] is False
    assert claim["authority_claimed"] is False
    assert claim["action_permission_claimed"] is False
    assert claim["final_output_claimed"] is False
    assert result["counters"]["semantic_claim_candidate_only_count"] == 1


def test_drs_candidate_context_is_from_actual_local_drs_resolve_reuse() -> None:
    result = runner.run_full_semantic_e2e(env={})
    context = result["drs_candidate_context"]
    counters = result["counters"]

    assert context["implementation"] == (
        "hedgehog.local_drs_resolver.resolve_semantic_candidates"
    )
    assert context["resolved_as"] == "actual_local_drs_candidate_context"
    assert context["candidate_count"] == 3
    assert counters["drs_candidates_resolved_count"] == 3
    assert context["truth_claimed"] is False
    assert context["authority_claimed"] is False
    assert context["action_permission_granted"] is False
    assert context["direct_reuse_applied"] is False
    assert any(candidate["stale"] for candidate in context["candidates"])
    assert any(candidate["conflicting_provenance"] for candidate in context["candidates"])


def test_candidate_vector_and_avf_report_are_real_structured_outputs() -> None:
    result = runner.run_full_semantic_e2e(env={})
    candidate_context = result["candidate_vector_context"]
    avf_context = result["avf_context"]
    counters = result["counters"]

    assert candidate_context["implementation"] == (
        "hedgehog.candidate_vector_generator.build_avf_candidate_report"
    )
    assert candidate_context["report_type"] == "CandidateVectorReport"
    assert candidate_context["candidate_vector_count"] == 3
    assert candidate_context["counters"]["candidate_vectors_generated_count"] == 3
    assert candidate_context["counters"]["avf_scores_computed_count"] == 3
    assert candidate_context["truth_claimed"] is False
    assert candidate_context["authority_claimed"] is False
    assert candidate_context["action_permission_claimed"] is False
    assert candidate_context["direct_reuse_allowed"] is False

    assert avf_context["AVF"] == "invoked score/rank"
    assert avf_context["hard_masked_count"] == 2
    assert len(avf_context["scores"]) == 3
    assert all(score["score_is_authority"] is False for score in avf_context["scores"])
    assert all(
        score["action_permission_granted"] is False for score in avf_context["scores"]
    )
    assert counters["candidate_vector_ranked_count"] == 3
    assert counters["avf_hard_mask_applied_count"] == 2


def test_bounded_route_uses_only_slice1_vector_ids_and_no_raw_text() -> None:
    result = runner.run_full_semantic_e2e(env={})
    route = result["bounded_orchestrator_context"]
    candidate_context = result["candidate_vector_context"]

    assert route["implementation"] == (
        "bounded route decision inside existing Full Semantic E2E route"
    )
    assert route["consumed_raw_provider_text"] is False
    assert route["consumed_raw_user_text"] is False
    assert route["creates_final_output"] is False
    assert route["executes_action"] is False
    assert route["root_review_required"] is True
    assert set(route["selected_vector_ids"]) <= set(route["allowed_vector_ids"])
    assert set(route["allowed_vector_ids"]) == set(candidate_context["ranked_vector_ids"])
    assert route["raw_text_blocked"] is True
    assert result["counters"]["bounded_route_created_count"] == 1
    assert result["counters"]["raw_text_blocked_from_architect_count"] == 1


def test_plangraph_is_real_structured_output_from_architect_and_contract_validator() -> None:
    result = runner.run_full_semantic_e2e(env={})
    architect = result["architect_context"]
    plangraph = result["plangraph_context"]
    route = result["bounded_orchestrator_context"]
    plan_graph = plangraph["plan_graph"]

    assert architect["implementation"] == "hedgehog.architect.make_plan_graph"
    assert architect["architect_provider"] == "deterministic"
    assert architect["allow_config"] is False
    assert architect["consumed_raw_provider_text"] is False
    assert architect["consumed_raw_user_text"] is False
    assert architect["creates_final_output"] is False

    assert plangraph["created_by"] == "hedgehog.architect.make_plan_graph"
    assert plangraph["validated_by"] == (
        "hedgehog.llm_architect.validate_plan_graph_contract"
    )
    assert plangraph["contract_validated"] is True
    assert plangraph["dag_validated"] is True
    assert plangraph["node_count"] > 0
    assert plangraph["edge_count"] >= 0
    assert set(plangraph["node_vector_ids"]) <= set(route["selected_vector_ids"])
    assert set(plangraph["node_vector_ids"]) <= set(plangraph["allowed_vector_ids"])
    assert plangraph["raw_user_text_present"] is False
    assert plangraph["final_output_present"] is False
    assert plangraph["connector_command_present"] is False
    assert plangraph["payment_or_shipment_command_present"] is False
    assert all(node["expected_output"] == "result_proposal" for node in plangraph["nodes"])

    validator_packet = {
        "request_id": result["dirty_business_request"]["request_id"],
        "candidate_vectors": list(route["candidate_vectors"]),
    }
    validate_plan_graph_contract(plan_graph, validator_packet)
    assert result["counters"]["plangraph_invoked_count"] == 1
    assert result["counters"]["plan_graph_contract_validated_count"] == 1
    assert result["counters"]["plan_graph_nodes_created_count"] == plangraph["node_count"]
    assert result["counters"]["plan_graph_dag_validated_count"] == 1


def test_executor_branch_is_real_structured_output_and_proposal_only() -> None:
    result = runner.run_full_semantic_e2e(env={})
    fractal = result["fractal_executor_context"]
    report = fractal["runner_report"]
    proposal = result["result_proposal"]

    assert fractal["implementation"] == (
        "hedgehog.fractal_dag_executor.run_fractal_dag_executor"
    )
    assert fractal["run_fractal_dag_executor_invoked"] is True
    assert fractal["status"] == "completed"
    assert fractal["result_proposals_created"] > 0
    assert fractal["executor_created_final_output"] is False
    assert fractal["no_real_external_action"] is True
    assert report["result_proposals"]
    assert all("final_output" not in item for item in report["result_proposals"])
    assert proposal["proposal_count"] == fractal["result_proposals_created"]
    assert proposal["terminal_stage_promoted"] is True
    assert proposal["final_output_claimed"] is False
    assert result["counters"]["executor_invoked_count"] == 1
    assert result["counters"]["executor_result_proposals_created_count"] > 0
    assert result["counters"]["executor_final_output_created_count"] == 0
    assert result["counters"]["executor_external_action_executed_count"] == 0


def test_resultproposal_terminal_context_uses_executor_generated_artifacts() -> None:
    result = runner.run_full_semantic_e2e(env={})
    proposal_context = result["result_proposal"]
    dag_report = result["fractal_executor_context"]["runner_report"]
    dag_proposal_ids = tuple(
        proposal["proposal_id"] for proposal in dag_report["result_proposals"]
    )

    assert proposal_context["implementation"] == (
        "executor-generated ResultProposal artifacts from Slice 2 DAG runner"
    )
    assert proposal_context["proposal_count"] > 0
    assert proposal_context["proposal_ids"] == dag_proposal_ids
    assert proposal_context["proposal_artifacts"] == tuple(dag_report["result_proposals"])
    assert proposal_context["terminal_stage_promoted"] is True
    assert proposal_context["final_output_claimed"] is False
    assert result["counters"]["result_proposal_created_count"] == len(dag_proposal_ids)
    assert result["counters"]["result_proposal_final_output_claimed_count"] == 0


def test_post_vv_is_real_and_creates_no_finaloutput() -> None:
    result = runner.run_full_semantic_e2e(env={})
    post_vv = result["post_vv_context"]
    proposal_context = result["result_proposal"]

    assert post_vv["implementation"] == "hedgehog.post_vv.validate_result_proposals"
    assert post_vv["vv_report_count"] == proposal_context["proposal_count"]
    assert post_vv["vv_report_count"] > 0
    for report in post_vv["vv_reports"]:
        assert {"vv_report_id", "proposal_id", "status", "decision"} <= set(report)
        assert report["decision"] in {"accept", "reject", "revise"}
    assert post_vv["final_output_created_count"] == 0
    assert post_vv["finalizes"] is False
    assert result["counters"]["post_vv_reports_created_count"] == post_vv["vv_report_count"]
    assert result["counters"]["post_vv_final_output_created_count"] == 0


def test_gt_lgt_is_real_and_does_not_finalize_or_claim_root() -> None:
    result = runner.run_full_semantic_e2e(env={})
    gt_lgt = result["gt_lgt_context"]

    assert gt_lgt["implementation"] == "hedgehog.gt_validator.validate_gt"
    assert gt_lgt["gt_report_id"]
    assert gt_lgt["decision"] in {"accept", "revise", "no_update"}
    assert gt_lgt["final_output_created_count"] == 0
    assert gt_lgt["root_authority_claimed"] is False
    assert gt_lgt["finalizes"] is False
    assert result["counters"]["gt_report_created_count"] == 1
    assert result["counters"]["gt_final_output_created_count"] == 0
    assert result["counters"]["gt_root_authority_claimed_count"] == 0


def test_drs_writeback_is_real_local_and_after_root() -> None:
    result = runner.run_full_semantic_e2e(env={})
    writeback = result["drs_writeback_record"]
    root = result["root_final_output_boundary"]

    assert writeback["implementation"] == (
        "hedgehog.local_drs_resolver.write_root_final_record"
    )
    assert writeback["fallback_used"] is False
    assert writeback["written_after_root_boundary"] is True
    assert writeback["root_decision"] == root["decision"]
    assert writeback["root_final_artifact_id"] == (
        root["root_reviewed_semantic_outcome"]["final_artifact_id"]
    )
    assert writeback["local_writeback_only"] is True
    assert writeback["external_global_drs_write"] is False
    assert writeback["production_persistence_claimed"] is False
    assert writeback["record"]["content"]["local_writeback_only"] is True
    assert result["counters"]["drs_writeback_after_root_count"] == 1
    assert result["counters"]["local_drs_writeback_only_count"] == 1
    assert result["counters"]["external_global_drs_write_count"] == 0
    assert result["counters"]["production_persistence_claimed_count"] == 0
    assert result["counters"]["pre_root_writeback_blocked_count"] == 1


def test_slice3_hardening_rejects_malformed_finaloutput_and_pre_root_writeback() -> None:
    result = runner.run_full_semantic_e2e(env={})

    assert result["counters"]["post_vv_fail_closed_count"] >= 0
    assert result["counters"]["writeback_before_root_blocked_count"] == 1
    malformed_report = runner._validate_result_proposals_runtime([{"proposal_id": "bad"}])[0]
    assert malformed_report["decision"] == "reject"
    final_output_probe = json.loads(
        json.dumps(result["result_proposal"]["proposal_artifacts"][0])
    )
    final_output_probe["final_output"] = {"status": "forbidden"}
    final_output_report = runner._validate_result_proposals_runtime([final_output_probe])[0]
    assert final_output_report["decision"] == "reject"


def test_resultproposal_authority_action_and_finaloutput_claims_are_blocked() -> None:
    result = runner.run_full_semantic_e2e(env={})
    checks = result["runtime_hardening_checks"]
    counters = result["counters"]

    assert checks["result_proposal_authority_claim_blocked"] is True
    assert checks["result_proposal_action_claim_blocked"] is True
    assert checks["result_proposal_final_output_blocked"] is True
    assert checks["result_proposal_authority_claim_block_reasons"]
    assert checks["result_proposal_action_claim_block_reasons"]
    assert checks["result_proposal_final_output_block_reasons"]
    assert counters["result_proposal_authority_claim_blocked_count"] == 1
    assert counters["result_proposal_action_claim_blocked_count"] == 1
    assert counters["result_proposal_final_output_blocked_count"] == 1
    assert counters["result_proposal_final_output_claimed_count"] == 0
    assert counters["payment_executed_count"] == 0
    assert counters["shipment_released_count"] == 0
    assert counters["connector_called_count"] == 0


def test_post_vv_finaloutput_and_action_permission_claims_are_blocked() -> None:
    result = runner.run_full_semantic_e2e(env={})
    checks = result["runtime_hardening_checks"]
    counters = result["counters"]

    assert checks["post_vv_final_output_blocked"] is True
    assert checks["post_vv_action_permission_blocked"] is True
    assert checks["post_vv_final_output_block_reasons"]
    assert checks["post_vv_action_permission_block_reasons"]
    assert counters["post_vv_final_output_blocked_count"] == 1
    assert counters["post_vv_action_permission_blocked_count"] == 1
    assert counters["post_vv_final_output_created_count"] == 0
    assert counters["action_permission_created_count"] == 0


def test_gt_lgt_finalization_and_root_claims_are_blocked() -> None:
    result = runner.run_full_semantic_e2e(env={})
    checks = result["runtime_hardening_checks"]
    counters = result["counters"]

    assert checks["gt_lgt_finalization_blocked"] is True
    assert checks["gt_lgt_root_claim_blocked"] is True
    assert checks["gt_lgt_finalization_block_reasons"]
    assert checks["gt_lgt_root_claim_block_reasons"]
    assert counters["gt_lgt_finalization_blocked_count"] == 1
    assert counters["gt_lgt_root_claim_blocked_count"] == 1
    assert counters["gt_final_output_created_count"] == 0
    assert counters["gt_root_authority_claimed_count"] == 0


def test_slice2_hardening_probes_block_invalid_plangraphs() -> None:
    result = runner.run_full_semantic_e2e(env={})
    counters = result["counters"]

    assert counters["disallowed_vector_blocked_count"] == 1
    assert counters["cyclic_plan_graph_blocked_count"] == 1
    assert counters["child_overreach_blocked_count"] == 1


def test_local_slice2_plan_validation_rejects_disallowed_vector_cycle_and_overreach() -> None:
    result = runner.run_full_semantic_e2e(env={})
    packet = result["bounded_orchestrator_context"]["candidate_vectors"]
    attractor_packet = {
        "request_id": result["dirty_business_request"]["request_id"],
        "candidate_vectors": list(packet),
    }
    plan_graph = result["plangraph_context"]["plan_graph"]

    disallowed = json.loads(json.dumps(plan_graph))
    disallowed["nodes"][0]["vector_id"] = "vector:not_from_slice1"
    try:
        runner._validate_slice2_plan_graph(disallowed, attractor_packet)
    except ValueError as exc:
        assert "disallowed_vector" in str(exc)
    else:
        raise AssertionError("disallowed vector id was accepted")

    cyclic = json.loads(json.dumps(plan_graph))
    first_node_id = cyclic["nodes"][0]["node_id"]
    cyclic["edges"] = [{"from": first_node_id, "to": first_node_id}]
    try:
        runner._validate_slice2_plan_graph(cyclic, attractor_packet)
    except ValueError as exc:
        assert "cycle" in str(exc) or "DAG" in str(exc)
    else:
        raise AssertionError("cyclic PlanGraph was accepted")

    overreach = json.loads(json.dumps(plan_graph))
    overreach["nodes"][0]["target_boundary"] = "final_output"
    try:
        runner._validate_slice2_plan_graph(overreach, attractor_packet)
    except ValueError as exc:
        assert "child_overreach" in str(exc)
    else:
        raise AssertionError("child final-output overreach was accepted")


def test_legal_hold_beats_payable_invoice_in_slice1_core_path() -> None:
    result = runner.run_full_semantic_e2e(env={})
    counters = result["counters"]
    root = result["root_final_output_boundary"]

    assert counters["legal_hold_overrode_payable_invoice_count"] == 1
    assert "legal hold" in root["reason"]
    assert root["payment_executed"] is False
    assert root["shipment_released"] is False
    assert result["advisory_context"]["action_permission_granted"] is False
    assert result["advisory_context"]["root_finality_claimed"] is False
    assert counters["high_avf_override_blocked_count"] == 1


def test_stale_and_conflicting_drs_memory_remain_review_only() -> None:
    result = runner.run_full_semantic_e2e(env={})
    counters = result["counters"]
    drs_context = result["drs_candidate_context"]
    candidate_context = result["candidate_vector_context"]

    assert counters["stale_drs_reuse_blocked_count"] == 1
    assert counters["conflicting_drs_review_only_count"] == 1
    assert counters["stale_drs_memory_blocked_count"] == 1
    assert counters["conflicting_drs_memory_blocked_count"] == 1
    assert drs_context["stale_candidates"] == 1
    assert drs_context["conflicting_candidates"] == 1
    assert drs_context["direct_reuse_applied"] is False
    assert drs_context["action_permission_granted"] is False
    assert candidate_context["direct_reuse_allowed"] is False
    assert candidate_context["counters"]["stale_candidate_review_required_count"] == 1
    assert candidate_context["counters"]["conflicting_provenance_penalized_count"] == 1


def test_drs_candidate_vector_avf_and_advisory_boundaries() -> None:
    result = runner.run_full_semantic_e2e(env={})

    assert result["drs_candidate_context"]["truth_claimed"] is False
    assert result["candidate_vector_context"]["truth_claimed"] is False
    assert result["avf_context"]["authority_claimed"] is False
    assert result["advisory_context"]["authority_claimed"] is False
    assert result["advisory_context"]["root_finality_claimed"] is False


def test_result_proposal_post_vv_and_gt_lgt_do_not_finalize() -> None:
    result = runner.run_full_semantic_e2e(env={})

    assert result["result_proposal"]["final_output_claimed"] is False
    assert result["post_vv_context"]["finalizes"] is False
    assert result["gt_lgt_context"]["finalizes"] is False
    assert result["gt_lgt_context"]["root_authority_claimed"] is False
    assert result["counters"]["result_proposal_final_output_claimed_count"] == 0


def test_root_boundary_fields_block_payment_and_shipment() -> None:
    result = runner.run_full_semantic_e2e(env={})
    root = result["root_final_output_boundary"]

    assert root["decision"] == "not_ready"
    assert root["payment_executed"] is False
    assert root["shipment_released"] is False
    assert root["connector_called"] is False
    assert "legal hold" in root["reason"]
    assert "water_filter" in root["reason"]
    assert root["source_claim_is_candidate_only"] is True
    assert root["provider_output_used_as_truth"] is False


def test_legal_hold_and_stock_shortage_scenarios_pass() -> None:
    result = runner.run_full_semantic_e2e(env={})
    statuses = _scenario_statuses(result)

    assert statuses["legal_hold_blocks_payment_even_with_payable_invoice"] == "PASS"
    assert statuses["stock_shortage_blocks_shipment_release"] == "PASS"
    assert result["counters"]["payment_executed_count"] == 0
    assert result["counters"]["shipment_released_count"] == 0


def test_no_payment_shipment_connector_or_overclaim_counters() -> None:
    result = runner.run_full_semantic_e2e(env={})
    counters = result["counters"]

    assert counters["connector_called_count"] == 0
    assert counters["payment_executed_count"] == 0
    assert counters["shipment_released_count"] == 0
    assert counters["provider_final_output_created_count"] == 0
    assert counters["action_permission_created_count"] == 0
    assert counters["public_wow_claimed_count"] == 0
    assert counters["production_ready_claimed_count"] == 0
    assert counters["needlefactory_started_count"] == 0
    assert counters["marennya_started_count"] == 0
    assert counters["up_started_count"] == 0


def test_prompt_injection_preserved_as_evidence() -> None:
    result = runner.run_full_semantic_e2e(env={})
    statuses = _scenario_statuses(result)

    assert statuses["prompt_injection_preserved_as_evidence"] == "PASS"
    assert "prompt_injection" in result["semantic_evidence_claim"]["unsafe_instruction_flags"]
    assert result["counters"]["action_permission_created_count"] == 0


def test_invalid_json_fails_closed(tmp_path) -> None:
    result = runner.run_full_semantic_e2e(
        env=_response_file_env(tmp_path, "{bad-json"),
    )
    statuses = _scenario_statuses(result)

    assert result["final_status"] == "FAIL_CLOSED"
    assert statuses["unsafe_provider_claims_fail_closed"] == "PASS"
    assert "invalid_json" in result["validation_errors"]
    assert result["counters"]["root_final_output_created_count"] == 0


def test_unsafe_provider_claims_fail_closed(tmp_path) -> None:
    unsafe_payloads = (
        _valid_payload(authority_claimed=True),
        _valid_payload(action_permission_claimed=True),
        _valid_payload(final_output_claimed=True),
        _valid_payload(extracted_claim="call the bank connector now"),
        _valid_payload(api_key="abc"),
    )
    for payload in unsafe_payloads:
        result = runner.run_full_semantic_e2e(
            env=_response_file_env(tmp_path, json.dumps(payload)),
        )
        assert result["final_status"] == "FAIL_CLOSED"
        assert result["counters"]["root_final_output_created_count"] == 0
        assert result["counters"]["payment_executed_count"] == 0
        assert result["counters"]["shipment_released_count"] == 0


def test_drs_writeback_after_root_boundary() -> None:
    result = runner.run_full_semantic_e2e(env={})
    writeback = result["drs_writeback_record"]

    assert writeback["written_after_root_boundary"] is True
    assert writeback["root_decision"] == result["root_final_output_boundary"]["decision"]
    assert writeback["payment_executed"] is False
    assert writeback["shipment_released"] is False
    assert writeback["local_writeback_only"] is True
    assert writeback["external_global_drs_write"] is False
    assert result["counters"]["pre_root_writeback_blocked_count"] == 1


def test_report_contains_required_markers() -> None:
    output = runner.render_report(runner.run_full_semantic_e2e(env={}))

    assert runner.TITLE in output
    assert "FINAL STATUS: PASS" in output
    assert "stage_map" in output
    assert "root_final_output_boundary" in output
    assert "root_boundary" in output
    assert "SemanticEvidenceClaim" in output
    assert "candidate-only" in output
    assert "DRS candidate context" in output
    assert "CandidateVector" in output
    assert "AVF" in output
    assert "Post V&V" in output
    assert "GT-LGT" in output
    assert "represented_count" in output
    assert "invoked_count" in output
    assert "full_semantic_e2e_invoked_count: 1" in output
    assert "result_proposal_final_output_claimed_count: 0" in output
    assert "provider_final_output_created_count: 0" in output
    assert "payment_executed_count: 0" in output
    assert "shipment_released_count: 0" in output
    assert "connector_called_count: 0" in output
    assert "public_wow_claimed_count: 0" in output
    assert "production_ready_claimed_count: 0" in output
    assert "root_final_authority_preserved_count: 1" in output
    assert "legal hold" in output
    assert "water_filter" in output
