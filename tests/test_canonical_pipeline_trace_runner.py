from __future__ import annotations

from demo.run_canonical_pipeline_trace import run_canonical_pipeline_trace


def _trace():
    return run_canonical_pipeline_trace()


def test_demo_prints_all_required_sections():
    output = _trace().output

    for section in [
        "[ROOT INTAKE]",
        "[TEMPORAL / DRS PRECHECK]",
        "[CANDIDATE VECTORS]",
        "[AVF / HARDMASK]",
        "[ATTRACTOR PACKET]",
        "[ARCHITECT PLAN GRAPH]",
        "[FRACTAL DAG EXECUTOR]",
        "[POST V&V]",
        "[GT]",
        "[ROOT FINAL OUTPUT]",
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


def test_candidate_vectors_are_not_free_llm_hallucinated():
    candidates = _trace().sections["candidate_vectors"]

    assert candidates["candidate_vectors_total"] > 0
    assert "official_online_request" in candidates["candidate_vector_ids"]
    assert candidates["free_llm_hallucinated_vectors"] is False


def test_summary_preserves_canonical_invariants():
    output = _trace().output

    assert "canonical_trace_status: PASS" in output
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
