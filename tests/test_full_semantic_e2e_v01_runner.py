from __future__ import annotations

import json

import demo.run_full_semantic_e2e_v01 as runner
import demo.run_supplier_payment_live_evidence_integration_v02 as supplier_live


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


def test_default_main_exits_zero_and_prints_pass(monkeypatch, capsys) -> None:
    monkeypatch.delenv(supplier_live.ENV_ENABLE, raising=False)
    monkeypatch.delenv(supplier_live.ENV_RESPONSE_FILE, raising=False)
    monkeypatch.delenv(supplier_live.ENV_OUTPUT_DIR, raising=False)

    assert runner.main() == 0
    output = capsys.readouterr().out
    assert runner.TITLE in output
    assert "FINAL STATUS: PASS" in output


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


def test_slice1_stages_are_invoked_and_later_stages_remain_represented() -> None:
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

    assert stage_map["bounded_orchestrator"]["status"] == "represented"
    assert stage_map["architect"]["status"] == "represented"
    assert stage_map["plangraph"]["status"] == "represented"
    assert stage_map["fractal_cell_executor_branch"]["status"] == "represented"
    assert stage_map["result_proposal"]["status"] == "represented"
    assert stage_map["post_vv"]["status"] == "represented"
    assert stage_map["gt_lgt"]["status"] == "represented"
    assert stage_map["drs_writeback"]["status"] == "represented"
    assert counters["post_vv_represented_count"] == 1
    assert counters["post_vv_invoked_count"] == 0
    assert counters["gt_lgt_represented_count"] == 1
    assert counters["gt_lgt_invoked_count"] == 0
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


def test_stale_and_conflicting_drs_memory_remain_review_only() -> None:
    result = runner.run_full_semantic_e2e(env={})
    counters = result["counters"]
    drs_context = result["drs_candidate_context"]
    candidate_context = result["candidate_vector_context"]

    assert counters["stale_drs_reuse_blocked_count"] == 1
    assert counters["conflicting_drs_review_only_count"] == 1
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
