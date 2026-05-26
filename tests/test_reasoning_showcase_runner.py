from demo.run_reasoning_showcase import run_reasoning_showcase


FORBIDDEN_TERMS = {
    "api_key",
    "token",
    "raw_user_text",
    "chain of thought",
    "hidden reasoning",
}


def test_reasoning_showcase_prints_all_required_stories(tmp_path):
    output = run_reasoning_showcase(drs_root=tmp_path)

    assert "[STORY] story_l0_reflex_turn_on_tv" in output
    assert "[STORY] story_memory_first_direct_reuse" in output
    assert "[STORY] story_full_certificate_pipeline" in output
    assert "[STORY] story_permission_blocked_without_confirm" in output
    assert "[STORY] story_architect_contract_violation_recovered" in output


def test_reasoning_showcase_l0_story_contains_reflex_artifacts(tmp_path):
    output = run_reasoning_showcase(drs_root=tmp_path)

    assert "ModeRouter selected deterministic_reflex" in output
    assert "LLM called: false" in output
    assert "No LLM was called: false" not in output
    assert "Architect skipped: true" in output
    assert "Executor skipped: true" in output
    assert "Root wrote Work memory: true" in output


def test_reasoning_showcase_direct_reuse_story_contains_compute_saved(tmp_path):
    output = run_reasoning_showcase(drs_root=tmp_path)

    assert "Prior eligible Work record" in output or "prior eligible Work record" in output
    assert "ReuseGate marked best candidate as direct_reuse_candidate" in output
    assert "Root applied reuse decision direct_reuse" in output
    assert "Compute saved" in output
    assert "Root wrote new Work memory: true" in output


def test_reasoning_showcase_full_pipeline_story_contains_core_artifacts(tmp_path):
    output = run_reasoning_showcase(drs_root=tmp_path)

    assert "InputIntake classified the request as certificate_demo" in output
    assert "DRS found no direct reuse" in output
    assert "official_online_request" in output
    assert "personal_visit" in output
    assert "legal_representative" in output
    assert "fallback_exploration" in output
    assert "AVF blocked illegal_coercion before Architect" in output
    assert "PlanGraph with 9 nodes" in output
    assert "Executor produced 9 ResultProposals" in output
    assert "Post V&V accepted 6" in output
    assert "GT selected official_online_request using gt_payoff_v0_2" in output
    assert "RootOrchestrator created FinalOutput as root_orchestrator" in output


def test_reasoning_showcase_permission_story_is_safe(tmp_path):
    output = run_reasoning_showcase(drs_root=tmp_path)

    assert "Permission policy required confirmation" in output
    assert "Action result was blocked without confirmation" in output
    assert "No real external action occurred" in output
    assert "Final status is needs_user" in output


def test_reasoning_showcase_contract_recovery_story(tmp_path):
    output = run_reasoning_showcase(drs_root=tmp_path)

    assert "Invalid PlanGraph contract rejected" in output
    assert "invalid_plan_graph_contract" in output
    assert "Deterministic recovery/fallback used" in output
    assert "Root still created FinalOutput as root_orchestrator" in output


def test_reasoning_showcase_has_why_this_matters_per_story(tmp_path):
    output = run_reasoning_showcase(drs_root=tmp_path)

    assert output.count("WHY THIS MATTERS:") == 5


def test_reasoning_showcase_does_not_leak_sensitive_or_hidden_reasoning_terms(tmp_path):
    output = run_reasoning_showcase(drs_root=tmp_path)
    lowered = output.lower()

    for term in FORBIDDEN_TERMS:
        assert term not in lowered
