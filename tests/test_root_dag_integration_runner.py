from __future__ import annotations

from pathlib import Path

from demo.run_root_dag_integration_smoke import run_smoke
from hedgehog.drs import LocalDRS
from hedgehog.root_orchestrator import RootOrchestrator


ROOT = Path(__file__).resolve().parents[1]
NEEDLES_DIR = ROOT / "needles"


def _make_root(tmp_path):
    drs = LocalDRS(tmp_path)
    return RootOrchestrator(drs=drs, needles_dir=NEEDLES_DIR), drs


def _contains_key(value, forbidden_key: str) -> bool:
    if isinstance(value, dict):
        return forbidden_key in value or any(
            _contains_key(child, forbidden_key) for child in value.values()
        )
    if isinstance(value, list):
        return any(_contains_key(item, forbidden_key) for item in value)
    return False


def test_default_proof_full_pipeline_keeps_legacy_executor(tmp_path):
    root, _drs = _make_root(tmp_path)
    final_output = root.process_event(
        raw_user_text="mock certificate request",
        request_id="req_default_legacy_executor",
        session_anchor="sess_default_legacy_executor",
    )

    assert final_output["created_by"] == "root_orchestrator"
    assert root.last_trace["mode_router"]["execution_mode"] == "proof_full_pipeline"
    assert root.last_trace["execution_engine"] == "legacy_executor"
    assert root.last_trace["fractal_dag_executor_used"] is False
    assert root.last_trace["dag_runner_report"] is None
    assert root.last_trace["result_proposals"]


def test_direct_reuse_still_skips_architect_and_executor(tmp_path):
    from hedgehog.time_model import make_time_envelope

    root, drs = _make_root(tmp_path)
    drs.write_record(
        {
            "record_id": "work:trusted_direct_reuse_source",
            "layer": "work",
            "type": "task_outcome",
            "domain": "government_certificate",
            "content": {
                "summary": "Trusted reusable certificate outcome.",
                "canonical_goal": "Prepare a mock government certificate request plan.",
                "final_status": "success",
                "route": "proof_full_pipeline",
                "selected_proposal_ids": ["proposal:trusted"],
                "completed_proposal_ids": ["proposal:trusted"],
                "reuse_applied": False,
            },
            "time_envelope": make_time_envelope("sess_reuse_source"),
            "provenance": {
                "request_id": "req_reuse_source",
                "created_by": "root_orchestrator",
                "trace_refs": [
                    {
                        "trace_id": "trace:req_reuse_source",
                        "span_id": "seed",
                        "kind": "test",
                    }
                ],
            },
            "gt": {
                "gt_report_id": "gt:trusted",
                "half_life_hours": 720.0,
                "decay_rate": 0.001,
            },
            "status": "accepted",
        }
    )

    final_output = root.process_event(
        raw_user_text="mock certificate request",
        request_id="req_direct_reuse_still_skips",
        session_anchor="sess_direct_reuse_still_skips",
        allow_direct_reuse=True,
        force_full_pipeline=False,
    )

    assert final_output["created_by"] == "root_orchestrator"
    assert root.last_trace["reuse_applied"] is True
    assert root.last_trace["architect_skipped"] is True
    assert root.last_trace["executor_skipped"] is True
    assert "execution_engine" not in root.last_trace


def test_reflex_and_llm_general_routes_are_unchanged(tmp_path):
    root, _drs = _make_root(tmp_path)
    reflex = root.process_event(
        raw_user_text="turn on tv",
        request_id="req_reflex_unchanged",
        session_anchor="sess_reflex_unchanged",
        force_full_pipeline=False,
        allow_reflex=True,
    )
    assert reflex["created_by"] == "root_orchestrator"
    assert root.last_trace["architect_skipped"] is True
    assert root.last_trace["executor_skipped"] is True
    assert root.last_trace["reflex_applied"] is True

    general = root.process_event(
        raw_user_text="x + y = 110\nx - y = 100",
        request_id="req_general_unchanged",
        session_anchor="sess_general_unchanged",
        llm_provider="mock",
    )
    assert general["created_by"] == "root_orchestrator"
    assert root.last_trace["execution_mode"] == "llm_general"
    assert root.last_trace["architect_skipped"] is True
    assert root.last_trace["executor_skipped"] is True


def test_opt_in_dag_route_uses_fractal_dag_executor_and_root_commits(tmp_path):
    root, drs = _make_root(tmp_path)
    final_output = root.process_event(
        raw_user_text="mock certificate request",
        request_id="req_opt_in_fractal_dag",
        session_anchor="sess_opt_in_fractal_dag",
        use_fractal_dag_executor=True,
    )
    trace = root.last_trace
    work_record = drs.read_record("work", final_output["drs_writes"][0])

    assert trace["execution_engine"] == "fractal_dag"
    assert trace["fractal_dag_executor_used"] is True
    assert trace["dag_runner_report"]["status"] == "completed"
    assert trace["dag_ready_sequence_present"] is True
    assert trace["dag_execution_batches_present"] is True
    assert trace["dag_result_proposals_count"] == len(trace["result_proposals"])
    assert trace["dag_result_proposals_count"] > 0
    assert trace["post_vv_after_dag_executor"] is True
    assert len(trace["vv_reports"]) == len(trace["result_proposals"])
    assert trace["gt_after_post_vv"] is True
    assert trace["root_received_dag_artifacts"] is True
    assert trace["executor_created_final_output"] is False
    assert trace["gt_report"]["decision"] == "accept"
    assert final_output["created_by"] == "root_orchestrator"
    assert final_output["status"] == "success"
    assert work_record["content"]["execution_engine"] == "fractal_dag"
    assert work_record["content"]["fractal_dag_executor_used"] is True
    assert work_record["time_envelope"]


def test_dag_route_has_no_external_action_or_uncontrolled_delegation(tmp_path):
    root, _drs = _make_root(tmp_path)
    final_output = root.process_event(
        raw_user_text="mock certificate request",
        request_id="req_dag_safety",
        session_anchor="sess_dag_safety",
        use_fractal_dag_executor=True,
    )
    trace = root.last_trace

    assert trace["no_real_external_action"] is True
    assert trace["uncontrolled_delegation"] is False
    assert not _contains_key(final_output, "raw_user_text")
    assert not _contains_key(final_output, "api_key")
    assert not _contains_key(final_output, "token")
    assert not _contains_key(final_output, "secret")
    assert not _contains_key(trace["result_proposals"], "final_output")


def test_root_dag_integration_smoke_output_contains_required_sections():
    output = run_smoke().output

    for section in [
        "[ROOT DAG INTEGRATION SMOKE]",
        "[ROOT / ROUTE]",
        "[ARCHITECT]",
        "[DAG RUNNER]",
        "[POST V&V / GT]",
        "[ROOT FINAL]",
        "[SUMMARY]",
    ]:
        assert section in output
    assert "execution_engine: fractal_dag" in output
    assert "fractal_dag_executor_used: true" in output
    assert "root_created_final_output: true" in output
    assert "executor_created_final_output: false" in output
    assert "gt_committed_final_output: false" in output
    assert "no_real_external_actions: true" in output
    assert "uncontrolled_delegation: false" in output


def test_root_dag_integration_smoke_output_contains_no_sensitive_terms():
    output = run_smoke().output.lower()

    assert "api_key" not in output
    assert "token" not in output
    assert "secret" not in output
    assert "raw_user_text" not in output
    assert "chain of thought" not in output
