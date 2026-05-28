from __future__ import annotations

import demo.run_live_controlled_smoke as live_smoke
from demo.run_live_gemini_orchestrator_shadow import ShadowProposal
from demo.run_live_controlled_smoke import run_live_controlled_smoke


FORBIDDEN_TERMS = {
    "raw_user_text",
    "api_key",
    "token",
    "secret",
    "hidden reasoning",
    "chain of thought",
}


def test_live_controlled_smoke_prints_required_sections():
    output = run_live_controlled_smoke()

    assert "[LIVE CONTROLLED SMOKE]" in output
    assert "[ORCHESTRATOR PROPOSAL]" in output
    assert "[ROUTE VALIDATOR]" in output
    assert "[GUARD COMPLETENESS]" in output
    assert "[INTEGRATION GATE]" in output
    assert "[ROOT EXECUTION]" in output
    assert "[TRACE VERDICT]" in output
    assert "[SUMMARY]" in output


def test_default_mock_provider_is_offline():
    output = run_live_controlled_smoke()

    assert "provider: mock" in output
    assert "live_gemini: false" in output
    assert "note: controlled_orchestrator_enabled: live_smoke_only" in output


def test_mock_proposal_valid_and_gate_eligible():
    output = run_live_controlled_smoke()

    assert "proposal_status: valid" in output
    assert "suggested_route: proof_full_pipeline" in output
    assert "validation_decision: allow_with_guards" in output
    assert "allowed: true" in output
    assert "guards_complete: true" in output
    assert "guard_completeness_score: 1.00" in output
    assert "proposal_quality_status: PASS_COMPLETE" in output
    assert "integration_gate_decision: eligible_for_controlled_dry_run" in output
    assert "eligible: true" in output


def test_mock_controlled_execution_performed_by_root():
    output = run_live_controlled_smoke()

    assert "controlled_execution_performed: true" in output
    assert "executed: true" in output
    assert "execution_mode: proof_full_pipeline" in output
    assert "route: proof_full_pipeline" in output
    assert "architect_provider: mock" in output
    assert "architect_llm_used: false" in output
    assert "architect_skipped: false" in output
    assert "executor_skipped: false" in output


def test_mock_root_execution_success_and_root_authority():
    output = run_live_controlled_smoke()

    assert "gt_decision: accept" in output
    assert "final_status: success" in output
    assert "drs_write_count: 1" in output
    assert "root_final_authority: true" in output
    assert "root_created_final_output: true" in output
    assert "verdict: PASS_EXECUTED_BY_ROOT" in output
    assert "live_controlled_smoke_status: PASS_EXECUTED_BY_ROOT" in output


def test_mock_uncontrolled_delegation_false_and_no_real_action():
    output = run_live_controlled_smoke()

    assert "note: Orchestrator proposes; Root executes" in output
    assert "no_real_external_action: true" in output
    assert "uncontrolled_delegation: false" in output
    assert "controlled_orchestrator_enabled: live_smoke_only" in output


def test_invalid_proposal_path_is_safe_blocked(monkeypatch):
    def fake_invalid_proposal(_case, *, provider, model):
        assert provider == "gemini"
        assert model is None
        return ShadowProposal(
            proposal_status="invalid",
            suggested_route="fallback_to_deterministic",
            confidence=0.0,
            reason="Invalid shadow proposal; deterministic route remains in force.",
            required_guards=["Route Validator", "Root final authority"],
            shadow_only=True,
            provider="gemini",
            error="ValueError: no JSON object found",
            proposal_error="ValueError: no JSON object found",
            raw_response_preview="not-json",
            parse_error="ValueError: no JSON object found",
        )

    monkeypatch.setattr(live_smoke, "_make_pair_shadow_proposal", fake_invalid_proposal)

    output = run_live_controlled_smoke(provider="gemini")

    assert "provider: gemini" in output
    assert "live_gemini: true" in output
    assert "proposal_status: invalid" in output
    assert "proposal_error: ValueError: no JSON object found" in output
    assert "parse_error: ValueError: no JSON object found" in output
    assert "controlled_execution_performed: false" in output
    assert "executed: false" in output
    assert "verdict: PASS_SAFE_BLOCKED_INVALID_PROPOSAL" in output
    assert "live_controlled_smoke_status: PASS_SAFE_BLOCKED_INVALID_PROPOSAL" in output


def test_live_controlled_smoke_does_not_leak_sensitive_terms():
    output = run_live_controlled_smoke()
    lowered = output.lower()

    for term in FORBIDDEN_TERMS:
        assert term not in lowered
