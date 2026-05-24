from pathlib import Path

from hedgehog.drs import LocalDRS
from hedgehog.root_orchestrator import RootOrchestrator
from hedgehog.trace_reporter import render_trace_report


ROOT = Path(__file__).resolve().parents[1]
NEEDLES_DIR = ROOT / "needles"


def make_orchestrator(tmp_path):
    drs = LocalDRS(tmp_path / "drs")
    return RootOrchestrator(drs=drs, needles_dir=NEEDLES_DIR)


def test_render_trace_report_handles_normal_full_pipeline_trace(tmp_path):
    orchestrator = make_orchestrator(tmp_path)
    final_output = orchestrator.process_event(
        raw_user_text="mock certificate request",
        request_id="req_trace_report_full",
        session_anchor="sess_trace_report_full",
    )
    report = render_trace_report(orchestrator.last_trace, final_output)

    assert "[ROOT]" in report
    assert "[DRS]" in report
    assert "[AVF]" in report
    assert "[ARCHITECT]" in report
    assert "[EXECUTOR]" in report
    assert "[POST_VV]" in report
    assert "[GT]" in report
    assert "[FINAL]" in report
    assert "illegal_coercion blocked: true" in report


def test_render_trace_report_handles_llm_general_trace(tmp_path):
    orchestrator = make_orchestrator(tmp_path)
    final_output = orchestrator.process_event(
        raw_user_text="x + y = 110\nx - y = 100",
        request_id="req_trace_report_general",
        session_anchor="sess_trace_report_general",
        llm_provider="mock",
    )
    report = render_trace_report(orchestrator.last_trace, final_output)

    assert "execution_mode: llm_general" in report
    assert "input_intake: general_request" in report
    assert "created_by: root_orchestrator" in report


def test_render_trace_report_handles_llm_architect_fallback_trace(tmp_path):
    orchestrator = make_orchestrator(tmp_path)
    final_output = orchestrator.process_event(
        raw_user_text="mock certificate request",
        request_id="req_trace_report_llm_architect",
        session_anchor="sess_trace_report_llm_architect",
        architect_provider="gemini",
        architect_allow_config=False,
    )
    report = render_trace_report(orchestrator.last_trace, final_output)

    assert "llm_architect status: error" in report
    assert "llm_architect fallback: deterministic" in report
    assert "llm_architect used_llm: false" in report
    assert "Final" not in report or "[FINAL]" in report


def test_render_trace_report_preserves_used_llm_true_for_post_call_error():
    trace = {
        "execution_mode": "proof_full_pipeline",
        "route": "proof_full_pipeline",
        "llm_architect_result": {
            "status": "error",
            "provider": "gemini",
            "model": "gemini-test",
            "used_llm": True,
            "error": "invalid_plan_graph_contract: missing required fields: plan_id",
            "fallback": "deterministic",
        },
        "result_proposals": [
            {
                "result_payload": {
                    "blocked_reason": "needs_human_input",
                }
            }
        ],
        "vv_reports": [
            {"decision": "accept", "status": "accepted"},
            {"decision": "revise", "status": "needs_revision"},
        ],
    }
    report = render_trace_report(trace, {"request_id": "req", "status": "success"})

    assert "llm_architect used_llm: true" in report
    assert "count note: categories may overlap" in report
    assert "completed reports: 1" in report
    assert "needs_user reports: 1" in report
    assert "blocked proposals: 1" in report


def test_render_trace_report_redacts_forbidden_terms():
    trace = {
        "execution_mode": "llm_general",
        "route": "llm_general",
        "llm_architect_result": {
            "status": "error",
            "provider": "gemini",
            "model": "gemini-test",
            "used_llm": False,
            "error": "api_key token raw_user_text should not print",
            "fallback": "deterministic",
        },
    }
    report = render_trace_report(trace, {"request_id": "req", "status": "failed"})

    lowered = report.lower()
    assert "raw_user_text" not in lowered
    assert "api_key" not in lowered
    assert "token" not in lowered
