from __future__ import annotations

import demo.run_gemini_orchestrator_architect_pair_smoke as pair_smoke
from demo.run_live_gemini_orchestrator_shadow import ShadowProposal
from demo.run_gemini_orchestrator_architect_pair_smoke import (
    run_gemini_orchestrator_architect_pair_smoke,
)


FORBIDDEN_TERMS = {
    "raw_user_text",
    "api_key",
    "token",
    "secret",
    "hidden reasoning",
    "chain of thought",
}


def test_pair_smoke_prints_required_sections():
    output = run_gemini_orchestrator_architect_pair_smoke()

    assert "[GEMINI ORCHESTRATOR + ARCHITECT PAIR SMOKE]" in output
    assert "[ORCHESTRATOR PROPOSAL]" in output
    assert "[ROUTE VALIDATION]" in output
    assert "[ROOT EXECUTION]" in output
    assert "[SUMMARY]" in output


def test_pair_smoke_default_is_mock_offline():
    output = run_gemini_orchestrator_architect_pair_smoke()

    assert "provider: mock" in output
    assert "live_gemini: false" in output
    assert "architect_provider: mock" in output
    assert "architect_llm_used: false" in output


def test_mock_orchestrator_proposal_validated_before_root_execution():
    output = run_gemini_orchestrator_architect_pair_smoke()

    assert "note: Orchestrator proposal is validated before execution" in output
    assert "suggested_route: proof_full_pipeline" in output
    assert "validation_decision: allow_with_guards" in output
    assert "allowed: true" in output
    assert "would_execute_route: proof_full_pipeline" in output
    assert output.index("[ROUTE VALIDATION]") < output.index("[ROOT EXECUTION]")


def test_mock_root_execution_uses_full_pipeline_and_mock_architect():
    output = run_gemini_orchestrator_architect_pair_smoke()

    assert "executed: true" in output
    assert "execution_mode: proof_full_pipeline" in output
    assert "route: proof_full_pipeline" in output
    assert "architect_provider: mock" in output
    assert "architect_status: completed" in output
    assert "architect_skipped: false" in output
    assert "executor_skipped: false" in output


def test_mock_pair_gt_accepts_and_final_status_success():
    output = run_gemini_orchestrator_architect_pair_smoke()

    assert "gt_decision: accept" in output
    assert "final_status: success" in output
    assert "drs_write_count: 1" in output
    assert "gt_winner_vector: official_online_request" in output
    assert "plan_graph_node_count:" in output
    assert "accepted_branch_count:" in output


def test_pair_smoke_preserves_root_authority_and_no_controlled_orchestrator():
    output = run_gemini_orchestrator_architect_pair_smoke()

    assert "Root executes approved equivalent route" in output
    assert "Gemini Orchestrator does not directly control runtime" in output
    assert "root_final_authority: true" in output
    assert "controlled_orchestrator_enabled: false" in output
    assert "pair_smoke_status: PASS" in output
    assert "live_pair_executed: false" in output
    assert "architect_invoked: true" in output


def test_pair_smoke_no_real_actions_and_required_guards_present():
    output = run_gemini_orchestrator_architect_pair_smoke()

    assert "no_real_external_action: true" in output
    assert "AVF" in output
    assert "HardMask" in output
    assert "PlanGraph contract" in output
    assert "Post V&V" in output
    assert "GT" in output
    assert "Root final authority" in output


def test_pair_smoke_does_not_leak_sensitive_terms():
    output = run_gemini_orchestrator_architect_pair_smoke()
    lowered = output.lower()

    for term in FORBIDDEN_TERMS:
        assert term not in lowered


def test_invalid_live_proposal_path_reports_diagnostics_without_execution(monkeypatch):
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

    monkeypatch.setattr(pair_smoke, "_make_pair_shadow_proposal", fake_invalid_proposal)

    output = run_gemini_orchestrator_architect_pair_smoke(provider="gemini")

    assert "proposal_status: invalid" in output
    assert "orchestrator_proposal_valid: false" in output
    assert "proposal_error: ValueError: no JSON object found" in output
    assert "parse_error: ValueError: no JSON object found" in output
    assert "raw_response_preview: not-json" in output
    assert "executed: false" in output
    assert "live_pair_executed: false" in output
    assert "architect_invoked: false" in output
    assert "pair_smoke_status: PASS" in output
