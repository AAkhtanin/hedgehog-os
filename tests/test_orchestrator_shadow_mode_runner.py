from __future__ import annotations

from demo.run_orchestrator_shadow_mode import run_orchestrator_shadow_mode


FORBIDDEN_TERMS = {
    "raw_user_text",
    "api_key",
    "token",
    "secret",
    "hidden reasoning",
    "chain of thought",
}


def test_shadow_mode_prints_all_required_scenarios(tmp_path):
    output = run_orchestrator_shadow_mode(drs_root=tmp_path)

    assert "shadow_reflex_turn_on_tv" in output
    assert "shadow_general_explain_bicycles" in output
    assert "shadow_certificate_request" in output
    assert "shadow_repeated_certificate_direct_reuse" in output
    assert "shadow_permissioned_order_pizza" in output
    assert "shadow_forbidden_certificate_route" in output


def test_shadow_mode_declares_advisory_only(tmp_path):
    output = run_orchestrator_shadow_mode(drs_root=tmp_path)

    assert "shadow suggestions are advisory; deterministic route still used" in output
    assert "not LLM Orchestrator control yet" in output
    assert "no live Gemini by default" in output


def test_shadow_mode_never_controls_execution(tmp_path):
    output = run_orchestrator_shadow_mode(drs_root=tmp_path)

    assert output.count("true | false") >= 6
    assert "shadow_controlled_execution: false" in output
    assert " | true | true | " not in output


def test_shadow_mode_reflex_general_certificate_and_direct_reuse_match(tmp_path):
    output = run_orchestrator_shadow_mode(drs_root=tmp_path)

    assert "shadow_reflex_turn_on_tv | simple_device_command | deterministic_reflex | deterministic_reflex | MATCH" in output
    assert "shadow_general_explain_bicycles | general_explanation_request | llm_general | llm_general | MATCH" in output
    assert "shadow_certificate_request | certificate_request | proof_full_pipeline | proof_full_pipeline | MATCH" in output
    assert "shadow_repeated_certificate_direct_reuse | repeated_certificate_request | direct_reuse | direct_reuse | MATCH" in output


def test_shadow_mode_permission_scenario_has_permission_gate(tmp_path):
    output = run_orchestrator_shadow_mode(drs_root=tmp_path)

    assert "shadow_permissioned_order_pizza" in output
    assert "permission_required | MATCH_WITH_PERMISSION_GUARD" in output
    assert "PermissionGate" in output


def test_shadow_mode_forbidden_scenario_has_safety_guards(tmp_path):
    output = run_orchestrator_shadow_mode(drs_root=tmp_path)

    assert "shadow_forbidden_certificate_route" in output
    assert "AVF" in output
    assert "HardMask" in output
    assert "forbidden vector block" in output


def test_shadow_mode_summary_counts(tmp_path):
    output = run_orchestrator_shadow_mode(drs_root=tmp_path)

    assert "matches: 5" in output
    assert "guarded_matches: 1" in output
    assert "mismatches: 0" in output
    assert "next_step: route validator / controlled orchestrator later" in output


def test_shadow_mode_does_not_leak_sensitive_terms(tmp_path):
    output = run_orchestrator_shadow_mode(drs_root=tmp_path)
    lowered = output.lower()

    for term in FORBIDDEN_TERMS:
        assert term not in lowered
