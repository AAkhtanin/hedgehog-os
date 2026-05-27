from __future__ import annotations

from demo.run_live_gemini_orchestrator_shadow import run_live_gemini_orchestrator_shadow


FORBIDDEN_TERMS = {
    "raw_user_text",
    "api_key",
    "token",
    "secret",
    "hidden reasoning",
    "chain of thought",
}


def test_live_shadow_default_prints_all_mock_scenarios():
    output = run_live_gemini_orchestrator_shadow()

    assert "live_shadow_reflex_turn_on_tv" in output
    assert "live_shadow_general_explain_bicycles" in output
    assert "live_shadow_certificate_request" in output
    assert "live_shadow_repeated_certificate_direct_reuse" in output
    assert "live_shadow_permissioned_order_pizza" in output
    assert "live_shadow_forbidden_certificate_route" in output


def test_live_shadow_default_is_mock_offline():
    output = run_live_gemini_orchestrator_shadow()

    assert "provider: mock" in output
    assert "live_gemini: false" in output
    assert "provider | proposal_status" in output


def test_live_shadow_declares_advisory_and_validator_boundary():
    output = run_live_gemini_orchestrator_shadow()

    assert "shadow Orchestrator suggestions are advisory only" in output
    assert "deterministic route still used" in output
    assert "Route Validator stands between proposal and any future execution" in output
    assert "controlled_orchestrator_enabled: false" in output


def test_live_shadow_includes_validator_decision_for_every_scenario():
    output = run_live_gemini_orchestrator_shadow()

    assert output.count(" | true | true | false | ") >= 5
    assert "validation_decision" in output
    assert "allow_with_guards" in output
    assert "needs_user" in output


def test_live_shadow_permission_scenario_includes_permission_gate():
    output = run_live_gemini_orchestrator_shadow()

    assert "live_shadow_permissioned_order_pizza" in output
    assert "MATCH_WITH_PERMISSION_GUARD" in output
    assert "PermissionGate" in output


def test_live_shadow_certificate_scenario_includes_pipeline_guards():
    output = run_live_gemini_orchestrator_shadow()

    assert "live_shadow_certificate_request" in output
    assert "AVF" in output
    assert "PlanGraph contract" in output
    assert "GT" in output


def test_live_shadow_direct_reuse_scenario_includes_direct_reuse_gate():
    output = run_live_gemini_orchestrator_shadow()

    assert "live_shadow_repeated_certificate_direct_reuse" in output
    assert "DirectReuseGate" in output
    assert "Freshness" in output
    assert "PolicyOK" in output


def test_live_shadow_summary_counts_for_mock_provider():
    output = run_live_gemini_orchestrator_shadow()

    assert "valid_proposals: 6" in output
    assert "invalid_proposals: 0" in output
    assert "matches: 5" in output
    assert "guarded_matches: 1" in output
    assert "mismatches: 0" in output


def test_live_shadow_does_not_leak_sensitive_terms():
    output = run_live_gemini_orchestrator_shadow()
    lowered = output.lower()

    for term in FORBIDDEN_TERMS:
        assert term not in lowered
