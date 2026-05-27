from __future__ import annotations

from demo.run_intent_route_matrix import run_intent_route_matrix


FORBIDDEN_TERMS = {
    "api_key",
    "token",
    "secret",
    "raw_user_text",
    "hidden reasoning",
    "chain of thought",
}


def test_intent_route_matrix_prints_all_required_scenarios(tmp_path):
    output = run_intent_route_matrix(drs_root=tmp_path)

    assert "intent_reflex_turn_on_tv" in output
    assert "intent_general_explain_bicycles" in output
    assert "intent_certificate_request" in output
    assert "intent_repeated_certificate_direct_reuse" in output
    assert "intent_permissioned_order_pizza" in output
    assert "intent_forbidden_certificate_route" in output


def test_intent_route_matrix_all_scenarios_pass(tmp_path):
    output = run_intent_route_matrix(drs_root=tmp_path)

    assert " | FAIL | " not in output
    assert output.count(" | PASS | ") == 6


def test_intent_route_matrix_reflex_route(tmp_path):
    output = run_intent_route_matrix(drs_root=tmp_path)

    assert "intent_reflex_turn_on_tv | simple_device_command | deterministic_reflex | deterministic_reflex | PASS" in output
    assert "known deterministic reflex command" in output


def test_intent_route_matrix_general_route(tmp_path):
    output = run_intent_route_matrix(drs_root=tmp_path)

    assert "intent_general_explain_bicycles | general_explanation_request | llm_general | llm_general | PASS" in output
    assert "general_provider=mock" in output


def test_intent_route_matrix_certificate_route(tmp_path):
    output = run_intent_route_matrix(drs_root=tmp_path)

    assert "intent_certificate_request | certificate_request | proof_full_pipeline | proof_full_pipeline | PASS" in output
    assert "certificate_demo intake requires AVF and full proof pipeline" in output
    assert "official_online_request" in output


def test_intent_route_matrix_direct_reuse_route(tmp_path):
    output = run_intent_route_matrix(drs_root=tmp_path)

    assert "intent_repeated_certificate_direct_reuse | repeated_certificate_request | direct_reuse | direct_reuse | PASS" in output
    assert "| true | false | true | none | eligible trusted memory record" in output


def test_intent_route_matrix_permission_route(tmp_path):
    output = run_intent_route_matrix(drs_root=tmp_path)

    assert "intent_permissioned_order_pizza | permissioned_mock_purchase | deterministic_reflex | deterministic_reflex | PASS" in output
    assert "permission_required=true" in output
    assert "blocked mock action asks user confirmation" in output


def test_intent_route_matrix_forbidden_route_blocks_illegal_coercion(tmp_path):
    output = run_intent_route_matrix(drs_root=tmp_path)

    assert "intent_forbidden_certificate_route | certificate_request_with_forbidden_candidate | proof_full_pipeline | proof_full_pipeline | PASS" in output
    assert "AVF hardmask blocks illegal_coercion before Architect" in output
    assert "illegal_coercion" in output


def test_intent_route_matrix_summary_marks_not_llm_orchestrator(tmp_path):
    output = run_intent_route_matrix(drs_root=tmp_path)

    assert "This is deterministic expected-route matrix, not LLM Orchestrator yet." in output
    assert "Future LLM/SLM Orchestrator must match or justify deviations from this matrix." in output
    assert "No live Gemini is used by default." in output


def test_intent_route_matrix_does_not_leak_sensitive_terms(tmp_path):
    output = run_intent_route_matrix(drs_root=tmp_path)
    lowered = output.lower()

    for term in FORBIDDEN_TERMS:
        assert term not in lowered
