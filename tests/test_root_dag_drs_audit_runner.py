from __future__ import annotations

import json
from pathlib import Path

from demo.run_root_dag_drs_audit_smoke import run_smoke
from hedgehog.drs import LocalDRS
from hedgehog.root_orchestrator import _sensitive_terms_absent
from hedgehog.root_orchestrator import RootOrchestrator


ROOT = Path(__file__).resolve().parents[1]
NEEDLES_DIR = ROOT / "needles"
SENSITIVE_TERMS = {
    "raw_user_text",
    "api_key",
    "token",
    "secret",
    "password",
    "private_key",
    "passport_number",
    "card_number",
    "cvv",
}


def _run_root_native_dag(tmp_path):
    drs = LocalDRS(tmp_path)
    root = RootOrchestrator(drs=drs, needles_dir=NEEDLES_DIR)
    final_output = root.process_event(
        raw_user_text="mock certificate request",
        request_id="req_root_dag_drs_audit_test",
        session_anchor="sess_root_dag_drs_audit_test",
        force_full_pipeline=True,
        architect_provider="deterministic",
        use_fractal_dag_executor=True,
    )
    work_record = drs.read_record("work", final_output["drs_writes"][0])
    return root, final_output, work_record


def _contains_term(value, term: str) -> bool:
    return term in json.dumps(value, sort_keys=True).lower()


def test_root_native_dag_path_writes_work_record_with_time_and_provenance(tmp_path):
    _root, final_output, work_record = _run_root_native_dag(tmp_path)

    assert len(final_output["drs_writes"]) >= 1
    assert work_record["layer"] == "work"
    assert work_record["time_envelope"]
    assert work_record["provenance"]
    assert work_record["provenance"]["request_id"] == final_output["request_id"]
    assert work_record["provenance"]["created_by"] == "root_orchestrator"


def test_work_record_content_contains_root_native_dag_trace_fields(tmp_path):
    _root, _final_output, work_record = _run_root_native_dag(tmp_path)
    content = work_record["content"]

    assert content["execution_engine"] == "fractal_dag"
    assert content["fractal_dag_executor_used"] is True
    assert content["dag_runner_status"] == "completed"
    assert content["dag_result_proposals_count"] > 0
    assert content["dag_child_boundary_snapshots"] >= 0
    assert content["post_vv_after_dag_executor"] is True
    assert content["vv_reports_count"] > 0
    assert content["gt_after_post_vv"] is True
    assert content["gt_decision"] == "accept"
    assert content["root_received_dag_artifacts"] is True
    assert content["root_created_final_output"] is True
    assert content["executor_created_final_output"] is False
    assert content["gt_committed_final_output"] is False
    assert content["no_real_external_action"] is True
    assert content["uncontrolled_delegation"] is False


def test_work_record_provenance_contains_route_engine_plan_and_trace(tmp_path):
    _root, _final_output, work_record = _run_root_native_dag(tmp_path)
    provenance = work_record["provenance"]

    assert provenance["route"] == "proof_full_pipeline"
    assert provenance["execution_engine"] == "fractal_dag"
    assert provenance["plan_id"]
    assert provenance["gt_report_id"]
    assert provenance["gt_decision"] == "accept"
    assert provenance["trace_path"]
    assert provenance["trace_refs"]


def test_work_record_content_contains_audit_trace_proof_fields(tmp_path):
    _root, _final_output, work_record = _run_root_native_dag(tmp_path)
    content = work_record["content"]

    assert content["audit_trace_present"] is True
    assert content["root_native_dag_path"] is True
    assert content["root_final_authority_preserved"] is True
    assert content["post_vv_before_gt"] is True
    assert content["result_returned_to_root"] is True
    assert content["sensitive_input_absent"] is True


def test_work_record_content_contains_no_raw_input_or_secret_terms(tmp_path):
    _root, _final_output, work_record = _run_root_native_dag(tmp_path)
    content = work_record["content"]

    for term in SENSITIVE_TERMS:
        assert not _contains_term(content, term)


def test_sensitive_terms_absent_helper_detects_persistent_payload_terms():
    assert _sensitive_terms_absent(
        {"summary": "safe"},
        {"created_by": "root_orchestrator"},
    )
    assert not _sensitive_terms_absent({"raw_user_text": "do not persist this"})
    assert not _sensitive_terms_absent({"api_key": "do-not-persist"})


def test_root_dag_drs_audit_smoke_output_contains_required_sections_and_summary():
    output = run_smoke().output

    for section in [
        "[ROOT DAG DRS / AUDIT SMOKE]",
        "[ROOT NATIVE DAG RUN]",
        "[DRS WORK RECORD]",
        "[AUDIT / TRACE]",
        "[SUMMARY]",
    ]:
        assert section in output

    assert "execution_engine: fractal_dag" in output
    assert "fractal_dag_executor_used: true" in output
    assert "root_dag_drs_audit_status: PASS" in output
    assert "drs_writeback_stable: true" in output
    assert "dag_trace_fields_in_work_record: true" in output
    assert "audit_trace_present: true" in output
    assert "sensitive_input_absent: true" in output
    assert "secrets_absent: true" in output
    assert "no_real_external_actions: true" in output
    assert "uncontrolled_delegation: false" in output
