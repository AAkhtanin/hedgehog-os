from __future__ import annotations

from demo.run_canonical_pipeline_trace import run_canonical_pipeline_trace


def _trace():
    return run_canonical_pipeline_trace()


def test_demo_prints_all_required_sections():
    output = _trace().output

    for section in [
        "[ROOT INTAKE]",
        "[ROOT ORCHESTRATOR / ROUTE ASSEMBLY]",
        "[TEMPORAL / DRS PRECHECK]",
        "[CANDIDATE VECTORS]",
        "[AVF / HARDMASK]",
        "[AVF / ATTRACTOR FORMATION]",
        "[ATTRACTOR PACKET]",
        "[ARCHITECT INPUT]",
        "[ARCHITECT PLAN GRAPH]",
        "[FRACTAL DAG EXECUTOR]",
        "[POST V&V]",
        "[GT]",
        "[ROOT FINAL OUTPUT]",
        "[ROOT FINALIZATION]",
        "[DRS WRITEBACK / AUDIT]",
        "[SUMMARY]",
    ]:
        assert section in output


def test_trace_uses_fractal_dag_executor_and_produces_result_proposals():
    sections = _trace().sections
    executor = sections["fractal_dag_executor"]

    assert executor["executor_runner_used"] is True
    assert executor["runner_status"] == "completed"
    assert executor["ready_sequence"]
    assert executor["execution_batches"]
    assert executor["result_proposals_count"] > 0


def test_executor_architect_and_gt_do_not_create_final_output():
    sections = _trace().sections

    assert sections["architect_plan_graph"]["architect_created_final_output"] is False
    assert sections["fractal_dag_executor"]["executor_created_final_output"] is False
    assert sections["gt"]["gt_committed_final_output"] is False


def test_root_creates_final_output_and_preserves_authority():
    root = _trace().sections["root_final_output"]

    assert root["root_created_final_output"] is True
    assert root["root_final_authority"] is True
    assert root["created_by"] == "root_orchestrator"
    assert root["uncontrolled_delegation"] is False
    assert root["final_status"] == "success"


def test_forbidden_vector_blocked_before_architect():
    sections = _trace().sections
    avf = sections["avf_hardmask"]

    assert avf["forbidden_vector_blocked_before_architect"] is True
    assert "illegal_coercion" in avf["hard_masked_vectors"]
    assert avf["architect_received_forbidden_vectors"] is False


def test_root_orchestrator_route_assembly_is_explicit_and_bounded():
    assembly = _trace().sections["root_orchestrator_route_assembly"]

    assert assembly["root_authority"] is True
    assert assembly["orchestrator_stage_explicit"] is True
    assert assembly["orchestrator_provider"] == "deterministic"
    assert assembly["orchestrator_model"] == "none"
    assert assembly["llm_or_slm_used"] is False
    assert assembly["orchestrator_control_scope"] == "route_context_assembly_only"
    assert assembly["intent_normalized"] is True
    assert assembly["temporal_query_created"] is True
    assert assembly["world_state_assembled"] is True
    assert assembly["drs_precheck_completed"] is True
    assert assembly["candidate_vectors_requested"] is True
    assert assembly["candidate_vector_sources_allowed_only"] is True
    assert assembly["free_llm_hallucinated_vectors"] is False
    assert assembly["avf_requested"] is True
    assert assembly["attractor_packet_created"] is True
    assert assembly["orchestrator_created_final_output"] is False
    assert assembly["orchestrator_bypassed_avf"] is False
    assert assembly["orchestrator_bypassed_root_authority"] is False


def test_avf_attractor_formation_is_explicit_before_architect():
    formation = _trace().sections["avf_attractor_formation"]

    assert formation["avf_runs_before_architect"] is True
    assert formation["feature_scores_present"] is True
    assert formation["hardmask_applied"] is True
    assert formation["softmask_applied"] is True
    assert formation["topk_selected"] is True
    assert "illegal_coercion" in formation["hard_masked_vectors"]
    assert "illegal_coercion" not in formation["selected_vectors"]
    assert formation["forbidden_vectors_removed_before_architect"] is True
    assert formation["exploration_cannot_bypass_hardmask"] is True
    assert formation["avf_created_plan_graph"] is False
    assert formation["attractor_packet_created"] is True
    assert formation["attractor_packet_created_by"] == "root_orchestrator"


def test_architect_input_contract_is_attractor_packet_only():
    architect_input = _trace().sections["architect_input"]

    assert architect_input["architect_received_raw_user_text"] is False
    assert architect_input["architect_received_attractor_packet"] is True
    assert architect_input["architect_input_contains_forbidden_vectors"] is False
    assert architect_input["architect_input_contract"] == "AttractorPacket only"
    assert architect_input["architect_must_return"] == "PlanGraph"
    assert architect_input["architect_created_final_output"] is False
    assert architect_input["architect_must_respect_branch_budgets"] is True
    assert architect_input["architect_must_not_expand_forbidden_regions"] is True


def test_post_vv_runs_before_gt_and_gt_accepts():
    sections = _trace().sections

    assert sections["post_vv"]["post_vv_before_gt"] is True
    assert sections["post_vv"]["vv_reports_count"] > 0
    assert sections["post_vv"]["completed_reports"] > 0
    assert sections["gt"]["gt_decision"] == "accept"
    assert sections["gt"]["gt_winner_proposal"] != "none"


def test_drs_writeback_is_present_with_time_envelope_and_no_sensitive_input_key():
    sections = _trace().sections
    drs = sections["drs_writeback_audit"]

    assert drs["drs_write_count"] == 1
    assert drs["work_record_written"] is True
    assert drs["time_envelope_present"] is True
    assert drs["sensitive_input_absent"] is True
    assert drs["audit_trace_present"] is True


def test_root_finalization_receives_results_and_keeps_renderer_subordinate():
    finalization = _trace().sections["root_finalization"]

    assert finalization["received_result_proposals"] is True
    assert finalization["received_vv_reports"] is True
    assert finalization["received_gt_report"] is True
    assert finalization["root_decision"] == "final_output"
    assert finalization["root_may_rerun_or_narrow_or_expand"] is True
    assert finalization["final_output_created_by"] == "root_orchestrator"
    assert finalization["final_renderer_is_subordinate"] is True
    assert finalization["final_renderer_committed_output"] is False
    assert finalization["result_returned_to_root"] is True
    assert finalization["root_received_pipeline_artifacts"] is True
    assert finalization["root_finalization_after_gt"] is True


def test_candidate_vectors_are_not_free_llm_hallucinated():
    candidates = _trace().sections["candidate_vectors"]

    assert candidates["candidate_vectors_total"] > 0
    assert "official_online_request" in candidates["candidate_vector_ids"]
    assert candidates["free_llm_hallucinated_vectors"] is False


def test_summary_preserves_canonical_invariants():
    output = _trace().output

    assert "canonical_trace_status: PASS" in output
    assert "orchestrator_stage_explicit: true" in output
    assert "candidate_vector_sources_allowed_only: true" in output
    assert "orchestrator_created_final_output: false" in output
    assert "avf_runs_before_architect: true" in output
    assert "forbidden_vectors_removed_before_architect: true" in output
    assert "attractor_packet_created_by_root: true" in output
    assert "architect_input_contains_forbidden_vectors: false" in output
    assert "architect_received_attractor_packet_only: true" in output
    assert "result_returned_to_root: true" in output
    assert "root_received_pipeline_artifacts: true" in output
    assert "root_finalization_after_gt: true" in output
    assert "root_final_authority_preserved: true" in output
    assert "architect_created_final_output: false" in output
    assert "executor_created_final_output: false" in output
    assert "gt_committed_final_output: false" in output
    assert "forbidden_vector_blocked_before_architect: true" in output
    assert "post_vv_before_gt: true" in output
    assert "drs_writeback_done: true" in output
    assert "no_real_external_actions: true" in output
    assert "uncontrolled_delegation: false" in output


def test_output_contains_no_sensitive_terms():
    output = _trace().output.lower()

    assert "api_key" not in output
    assert "token" not in output
    assert "secret" not in output
    assert "raw_user_text" not in output
    assert "chain of thought" not in output
