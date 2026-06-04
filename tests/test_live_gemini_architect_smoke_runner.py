from __future__ import annotations

from demo.run_live_gemini_architect_smoke import (
    collect_live_gemini_architect_smoke,
    run_live_gemini_architect_smoke,
)


def test_runner_output_contains_title_and_sections():
    output = run_live_gemini_architect_smoke()

    assert "[LIVE GEMINI ARCHITECT SMOKE]" in output
    assert "[INPUT]" in output
    assert "[ROLE SUBSTITUTION]" in output
    assert "[ARCHITECT ARTIFACT]" in output
    assert "[BOUNDARY CHECKS]" in output
    assert "[FULL CANONICAL E2E CONTEXT]" in output
    assert "[AUTHORITY / SAFETY]" in output
    assert "[SUMMARY]" in output


def test_default_mode_is_dry_run_default():
    report = collect_live_gemini_architect_smoke()

    assert report.input["mode"] == "dry_run_default"
    assert report.summary["mode"] == "dry_run_default"


def test_default_mode_does_not_call_live_gemini():
    report = collect_live_gemini_architect_smoke()

    assert report.input["live_requested"] is False
    assert report.input["live_gemini_used"] is False
    assert report.summary["live_gemini_used"] is False
    assert report.summary["live_gemini_called"] is False


def test_live_mode_requires_explicit_gate_and_config(monkeypatch):
    monkeypatch.delenv("HEDGEHOG_ALLOW_LIVE_GEMINI", raising=False)
    for key in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_GEMINI_API_KEY"):
        monkeypatch.delenv(key, raising=False)

    report = collect_live_gemini_architect_smoke(
        live_requested=True,
        allow_config=False,
    )

    assert report.input["mode"] == "live_opt_in"
    assert report.input["live_requested"] is True
    assert report.input["live_gemini_available"] is False
    assert report.input["live_gemini_used"] is False
    assert report.input["skip_reason"] == "missing_live_gemini_configuration"
    assert report.summary["live_gemini_architect_smoke_status"] == "SKIPPED"


def test_missing_live_config_skips_not_crashes(monkeypatch):
    monkeypatch.setenv("HEDGEHOG_ALLOW_LIVE_GEMINI", "1")
    for key in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_GEMINI_API_KEY"):
        monkeypatch.delenv(key, raising=False)

    report = collect_live_gemini_architect_smoke(
        live_requested=True,
        allow_config=False,
    )

    assert report.input["live_gemini_available"] is False
    assert report.summary["live_gemini_architect_smoke_status"] == "SKIPPED"
    assert report.summary["ready_for_future_orchestrator_live_smoke"] is True


def test_substituted_role_is_architect_only():
    role = collect_live_gemini_architect_smoke().role_substitution

    assert role["substituted_role"] == "architect"
    assert role["gemini_is_root"] is False
    assert role["gemini_is_orchestrator"] is False
    assert role["gemini_is_executor"] is False
    assert role["gemini_is_final_renderer"] is False
    assert role["gemini_is_gt"] is False


def test_gemini_does_not_create_final_output_write_drs_or_execute_actions():
    report = collect_live_gemini_architect_smoke()
    role = report.role_substitution

    assert role["gemini_creates_final_output"] is False
    assert role["gemini_writes_drs"] is False
    assert role["gemini_executes_actions"] is False
    assert report.authority_safety["gemini_created_final_output"] is False
    assert report.authority_safety["gemini_wrote_drs"] is False
    assert report.authority_safety["gemini_executed_action"] is False


def test_plan_graph_contract_is_checked():
    artifact = collect_live_gemini_architect_smoke().architect_artifact

    assert artifact["plan_graph_contract_checked"] is True
    assert artifact["architect_artifact_source"] == "deterministic_mock"
    assert artifact["architect_artifact_valid"] is True
    assert artifact["plan_graph_present"] is True


def test_invalid_artifact_path_is_contained():
    report = collect_live_gemini_architect_smoke(
        injected_artifact={"nodes": []},
    )
    artifact = report.architect_artifact

    assert artifact["architect_artifact_source"] == "injected_invalid"
    assert artifact["architect_artifact_valid"] is False
    assert artifact["invalid_artifact_caught"] is True
    assert artifact["contract_violation_contained"] is True
    assert artifact["fallback_to_deterministic_architect"] is True
    assert artifact["executor_reached"] is False
    assert artifact["root_final_output_created_from_live_gemini"] is False
    assert report.summary["live_gemini_architect_smoke_status"] == "PASS"


def test_fallback_visible_when_live_artifact_missing_or_invalid(monkeypatch):
    monkeypatch.setenv("HEDGEHOG_ALLOW_LIVE_GEMINI", "1")
    for key in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_GEMINI_API_KEY"):
        monkeypatch.delenv(key, raising=False)

    report = collect_live_gemini_architect_smoke(
        live_requested=True,
        allow_config=False,
    )

    assert report.architect_artifact["fallback_to_deterministic_architect"] is True
    assert report.architect_artifact["contract_violation_contained"] is True


def test_boundaries_are_preserved():
    boundary = collect_live_gemini_architect_smoke().boundary_checks

    assert boundary["avf_boundary_preserved"] is True
    assert boundary["executor_boundary_preserved"] is True
    assert boundary["post_vv_boundary_preserved"] is True
    assert boundary["gt_boundary_preserved"] is True
    assert boundary["root_boundary_preserved"] is True
    assert boundary["reuse_gate_boundary_preserved"] is True
    assert boundary["gemini_bypassed_root"] is False
    assert boundary["gemini_bypassed_avf"] is False
    assert boundary["gemini_bypassed_plan_graph_contract"] is False
    assert boundary["gemini_bypassed_post_vv"] is False
    assert boundary["gemini_bypassed_gt"] is False
    assert boundary["gemini_bypassed_policy"] is False


def test_boundary_checks_are_derived_from_source_role_and_artifact():
    report = collect_live_gemini_architect_smoke()
    boundary = report.boundary_checks
    source = report.source_report
    first_sections = source.first_run_source.sections
    artifact = report.architect_artifact
    role = report.role_substitution
    full_canonical_pass = (
        report.full_canonical_e2e_context["full_canonical_e2e_status"] == "PASS"
    )
    architect_only = (
        role["substituted_role"] == "architect"
        and not role["gemini_is_root"]
        and not role["gemini_is_orchestrator"]
        and not role["gemini_is_executor"]
        and not role["gemini_is_final_renderer"]
        and not role["gemini_is_gt"]
        and not role["gemini_writes_drs"]
        and not role["gemini_executes_actions"]
        and not role["gemini_creates_final_output"]
    )

    expected_avf = (
        full_canonical_pass
        and first_sections["avf_attractor"]["avf_runs_before_architect"]
        and first_sections["avf_attractor"]["attractor_packet_created"]
        and not first_sections["avf_attractor"][
            "architect_received_forbidden_vectors"
        ]
    )
    expected_post_vv = (
        full_canonical_pass
        and first_sections["post_vv_gt"]["post_vv_after_dag_executor"]
        and first_sections["post_vv_gt"]["vv_reports_count"] > 0
    )
    expected_gt = (
        full_canonical_pass
        and first_sections["post_vv_gt"]["gt_after_post_vv"]
        and not first_sections["post_vv_gt"]["gt_committed_final_output"]
    )
    expected_root = (
        source.summary["first_run_root_authority_preserved"]
        and source.summary["second_run_root_authority_preserved"]
        and not artifact["root_final_output_created_from_live_gemini"]
    )

    assert boundary["avf_boundary_preserved"] == expected_avf
    assert boundary["plan_graph_contract_preserved"] == artifact[
        "plan_graph_contract_checked"
    ]
    assert boundary["executor_boundary_preserved"] == (
        not artifact["executor_reached"]
    )
    assert boundary["post_vv_boundary_preserved"] == expected_post_vv
    assert boundary["gt_boundary_preserved"] == expected_gt
    assert boundary["root_boundary_preserved"] == expected_root
    assert boundary["reuse_gate_boundary_preserved"] == source.authority_safety[
        "reuse_gate_boundary_preserved"
    ]
    assert boundary["gemini_bypassed_root"] == (
        not expected_root or not architect_only
    )


def test_full_canonical_e2e_collector_is_consumed():
    report = collect_live_gemini_architect_smoke()
    context = report.full_canonical_e2e_context

    assert report.source_report.summary["root_native_full_canonical_e2e_trace_status"] == "PASS"
    assert context["full_canonical_e2e_available"] is True
    assert context["full_canonical_e2e_status"] == "PASS"
    assert context["first_run_stages_passed"] == 9
    assert context["second_run_stages_passed"] == 12


def test_production_persistence_and_reuse_claims_remain_false():
    context = collect_live_gemini_architect_smoke().full_canonical_e2e_context

    assert context["production_persistence_claimed"] is False
    assert context["production_reuse_claimed"] is False
    assert context["production_direct_reuse_executed"] is False
    assert context["production_final_output_created"] is False


def test_no_telegram_action_or_global_external_drs():
    report = collect_live_gemini_architect_smoke()

    assert report.input["telegram_used"] is False
    assert report.authority_safety["live_telegram_action_executed"] is False
    assert report.authority_safety["no_global_drs"] is True
    assert report.authority_safety["no_external_drs_network"] is True


def test_production_autonomy_is_not_claimed():
    report = collect_live_gemini_architect_smoke()

    assert report.authority_safety["production_autonomy_claimed"] is False
    assert report.summary["gemini_authority_granted"] is False


def test_ready_for_future_orchestrator_live_smoke_requires_boundaries_and_containment():
    report = collect_live_gemini_architect_smoke(
        injected_artifact={"nodes": []},
    )

    assert report.boundary_checks["root_boundary_preserved"] is True
    assert report.architect_artifact["contract_violation_contained"] is True
    assert report.summary["ready_for_future_orchestrator_live_smoke"] is True


def test_rendered_output_omits_credential_env_names_and_secret_terms():
    output = run_live_gemini_architect_smoke()

    forbidden_terms = (
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "GOOGLE_GEMINI_API_KEY",
        "api_key",
        "password",
        "private_key",
        "passport_number",
        "card_number",
        "cvv",
    )
    for term in forbidden_terms:
        assert term not in output
