from __future__ import annotations

from demo.run_deadend_memory_demo import DEADEND_RECORD_ID, run_deadend_memory_demo
from hedgehog.drs import LocalDRS


FORBIDDEN_TERMS = {
    "api_key",
    "token",
    "raw_user_text",
    "hidden reasoning",
    "chain of thought",
}


def test_deadend_memory_demo_prints_required_phases(tmp_path):
    output = run_deadend_memory_demo(drs_root=tmp_path)

    assert "[DEADEND MEMORY DEMO]" in output
    assert "first_pass_block | PASS | illegal_coercion blocked before Architect" in output
    assert "deadend_record_written | PASS | deadend/fraud-like memory signal written" in output
    assert "second_pass_retrieval | PASS | remembered bad route found" in output
    assert "second_pass_avoidance | PASS | illegal_coercion not sent to Architect" in output
    assert "final_authority | PASS | Root created final output" in output


def test_deadend_memory_demo_writes_signal_without_sensitive_input(tmp_path):
    output = run_deadend_memory_demo(drs_root=tmp_path)
    drs = LocalDRS(tmp_path)
    record = drs.read_record("deadends", DEADEND_RECORD_ID)

    assert "deadend_record_written | PASS" in output
    assert record["layer"] == "deadends"
    assert record["type"] == "dead_end"
    assert record["content"]["vector_id"] == "illegal_coercion"
    assert record["content"]["reason"] == "forbidden_vector_blocked"
    assert record["content"]["demo_created_by"] == "deadend_memory_demo"
    assert "raw_user_text" not in str(record)


def test_deadend_memory_demo_second_pass_finds_remembered_bad_route(tmp_path):
    output = run_deadend_memory_demo(drs_root=tmp_path)

    assert "retrieved_on_second_pass: true" in output
    assert "architect_received_bad_route: false" in output
    assert "second_pass_avoidance | PASS" in output


def test_deadend_memory_demo_is_honest_demo_level_and_no_live_gemini(tmp_path):
    output = run_deadend_memory_demo(drs_root=tmp_path)

    assert "demo-level deadend signal" in output
    assert "not full Marennya/UP mutation" in output
    assert "no real external actions" in output
    assert "live_gemini: false" in output


def test_deadend_memory_demo_final_output_remains_root_authority(tmp_path):
    output = run_deadend_memory_demo(drs_root=tmp_path)

    assert "final_output_created_by: root_orchestrator" in output
    assert "final_authority | PASS" in output


def test_deadend_memory_demo_output_does_not_contain_sensitive_terms(tmp_path):
    output = run_deadend_memory_demo(drs_root=tmp_path)
    lowered = output.lower()

    for term in FORBIDDEN_TERMS:
        assert term not in lowered
