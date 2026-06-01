from __future__ import annotations

from demo.run_root_native_canonical_trace import run_trace


def _trace():
    return run_trace()


def test_output_prints_root_native_title_and_sections():
    output = _trace().output

    assert "[ROOT-NATIVE CANONICAL TRACE]" in output
    for section in [
        "[ROOT INTAKE]",
        "[ROOT ORCHESTRATOR / ROUTE ASSEMBLY]",
        "[AVF / ATTRACTOR]",
        "[ARCHITECT]",
        "[DAG RUNNER]",
        "[POST V&V / GT]",
        "[ROOT FINAL]",
        "[DRS WRITEBACK / AUDIT]",
        "[SUMMARY]",
    ]:
        assert section in output


def test_runner_uses_real_root_orchestrator_opt_in_dag_route():
    result = _trace()
    route = result.sections["root_orchestrator_route_assembly"]

    assert result.final_output["created_by"] == "root_orchestrator"
    assert result.trace["mode_router"]["execution_mode"] == "proof_full_pipeline"
    assert route["route"] == "proof_full_pipeline"
    assert route["execution_engine"] == "fractal_dag"
    assert route["force_full_pipeline"] is True
    assert route["use_fractal_dag_executor"] is True
    assert route["orchestrator_provider"] == "deterministic"
    assert route["llm_or_slm_used"] is False


def test_avf_and_attractor_fields_come_from_root_trace():
    avf = _trace().sections["avf_attractor"]

    assert avf["avf_runs_before_architect"] is True
    assert avf["hardmask_applied"] is True
    assert avf["forbidden_vector_blocked_before_architect"] is True
    assert avf["architect_received_forbidden_vectors"] is False
    assert avf["attractor_packet_created"] is True
    assert avf["attractor_packet_created_by"] == "root_orchestrator"
    assert "official_online_request" in avf["selected_vectors"]
    assert "illegal_coercion" in avf["forbidden_regions"]
    assert "illegal_coercion" not in avf["selected_vectors"]


def test_architect_returns_plan_graph_without_final_output():
    architect = _trace().sections["architect"]

    assert architect["architect_provider"] == "deterministic"
    assert architect["plan_graph_valid"] is True
    assert architect["plan_graph_node_count"] > 0
    assert architect["architect_created_final_output"] is False
    assert architect["architect_returned_plan_graph"] is True


def test_dag_runner_completed_and_produced_result_proposals():
    dag = _trace().sections["dag_runner"]

    assert dag["fractal_dag_executor_used"] is True
    assert dag["dag_runner_status"] == "completed"
    assert dag["dag_ready_sequence_present"] is True
    assert dag["dag_execution_batches_present"] is True
    assert dag["dag_result_proposals_count"] > 0
    assert dag["executor_created_final_output"] is False
    assert dag["no_real_external_action"] is True


def test_post_vv_and_gt_order_is_visible():
    post_gt = _trace().sections["post_vv_gt"]

    assert post_gt["post_vv_after_dag_executor"] is True
    assert post_gt["vv_reports_count"] > 0
    assert post_gt["gt_after_post_vv"] is True
    assert post_gt["gt_decision"] == "accept"
    assert post_gt["gt_committed_final_output"] is False


def test_root_receives_dag_artifacts_and_creates_final_output():
    root_final = _trace().sections["root_final"]

    assert root_final["root_received_dag_artifacts"] is True
    assert root_final["final_status"] == "success"
    assert root_final["root_created_final_output"] is True
    assert root_final["created_by"] == "root_orchestrator"
    assert root_final["uncontrolled_delegation"] is False


def test_drs_work_record_contains_dag_engine_fields():
    drs = _trace().sections["drs_writeback_audit"]

    assert drs["drs_write_count"] == 1
    assert drs["work_record_written"] is True
    assert drs["time_envelope_present"] is True
    assert drs["execution_engine_in_work_record"] == "fractal_dag"
    assert drs["fractal_dag_executor_used_in_work_record"] is True
    assert drs["sensitive_input_absent"] is True


def test_summary_contains_canonical_root_native_proof_fields():
    output = _trace().output

    assert "root_native_canonical_trace_status: PASS" in output
    assert "real_root_orchestrator_used: true" in output
    assert "execution_engine: fractal_dag" in output
    assert "fractal_dag_executor_used: true" in output
    assert "root_final_authority_preserved: true" in output
    assert "architect_created_final_output: false" in output
    assert "executor_created_final_output: false" in output
    assert "gt_committed_final_output: false" in output
    assert "post_vv_after_dag_executor: true" in output
    assert "gt_after_post_vv: true" in output
    assert "root_created_final_output: true" in output
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
