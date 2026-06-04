from __future__ import annotations

from demo.run_live_gemini_orchestrator_smoke import REQUIRED_MATRIX_FIELDS
from demo.run_live_gemini_orchestrator_smoke import collect_live_gemini_orchestrator_smoke
from demo.run_live_gemini_orchestrator_smoke import run_live_gemini_orchestrator_smoke


def test_runner_output_contains_title_and_sections():
    output = run_live_gemini_orchestrator_smoke()

    assert "[LIVE GEMINI ORCHESTRATOR SMOKE]" in output
    assert "[INPUT]" in output
    assert "[ROLE SUBSTITUTION]" in output
    assert "[ORCHESTRATION MATRIX]" in output
    assert "[PROPOSAL VALIDATION]" in output
    assert "[BOUNDARY CHECKS]" in output
    assert "[FULL CANONICAL E2E CONTEXT]" in output
    assert "[AUTHORITY / SAFETY]" in output
    assert "[SUMMARY]" in output


def test_default_mode_is_dry_run_default():
    report = collect_live_gemini_orchestrator_smoke()

    assert report.input["mode"] == "dry_run_default"
    assert report.input["network_free"] is True
    assert report.summary["mode"] == "dry_run_default"


def test_default_mode_does_not_call_live_gemini():
    report = collect_live_gemini_orchestrator_smoke()

    assert report.input["live_requested"] is False
    assert report.input["live_gemini_used"] is False
    assert report.summary["live_gemini_used"] is False
    assert report.summary["live_gemini_called"] is False
    assert report.orchestration_matrix["proposal_source"] == "deterministic_mock_orchestrator"
    assert report.proposal_validation["attempted_proposal_valid"] is True
    assert report.proposal_validation["active_proposal_valid"] is True
    assert report.proposal_validation["active_proposal_source"] == "deterministic_mock_orchestrator"
    assert report.proposal_validation["active_proposal_is_fallback"] is False


def test_live_mode_requires_explicit_gate_and_config(monkeypatch):
    monkeypatch.delenv("HEDGEHOG_ALLOW_LIVE_GEMINI", raising=False)
    for key in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_GEMINI_API_KEY"):
        monkeypatch.delenv(key, raising=False)

    report = collect_live_gemini_orchestrator_smoke(
        live_requested=True,
        allow_config=False,
    )

    assert report.input["mode"] == "live_opt_in"
    assert report.input["live_requested"] is True
    assert report.input["live_gemini_available"] is False
    assert report.input["live_gemini_used"] is False
    assert report.input["skip_reason"] == "missing_live_gemini_configuration"
    assert report.summary["live_gemini_orchestrator_smoke_status"] == "SKIPPED"


def test_missing_live_config_skips_not_crashes(monkeypatch):
    monkeypatch.setenv("HEDGEHOG_ALLOW_LIVE_GEMINI", "1")
    for key in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_GEMINI_API_KEY"):
        monkeypatch.delenv(key, raising=False)

    report = collect_live_gemini_orchestrator_smoke(
        live_requested=True,
        allow_config=False,
    )

    assert report.input["live_gemini_available"] is False
    assert report.proposal_validation["fallback_to_deterministic_orchestrator"] is True
    assert report.proposal_validation["attempted_proposal_valid"] is False
    assert report.proposal_validation["active_proposal_valid"] is True
    assert report.proposal_validation["active_proposal_source"] == "deterministic_mock_orchestrator"
    assert report.proposal_validation["active_proposal_is_fallback"] is True
    assert report.summary["live_gemini_orchestrator_smoke_status"] == "SKIPPED"
    assert report.summary["ready_for_future_controlled_orchestrator_integration"] is True


def test_substituted_role_is_orchestrator_proposal_actor_only():
    role = collect_live_gemini_orchestrator_smoke().role_substitution

    assert role["substituted_role"] == "orchestrator_proposal_actor"
    assert role["gemini_is_root"] is False
    assert role["gemini_is_architect"] is False
    assert role["gemini_is_executor"] is False
    assert role["gemini_is_final_renderer"] is False
    assert role["gemini_is_gt"] is False


def test_gemini_does_not_create_final_output_write_drs_or_execute_actions():
    report = collect_live_gemini_orchestrator_smoke()
    role = report.role_substitution

    assert role["gemini_creates_final_output"] is False
    assert role["gemini_writes_drs"] is False
    assert role["gemini_executes_actions"] is False
    assert report.authority_safety["gemini_created_final_output"] is False
    assert report.authority_safety["gemini_wrote_drs"] is False
    assert report.authority_safety["gemini_executed_action"] is False


def test_orchestration_matrix_has_all_required_fields():
    matrix = collect_live_gemini_orchestrator_smoke().orchestration_matrix

    assert all(field in matrix for field in REQUIRED_MATRIX_FIELDS)
    assert matrix["proposal_is_action"] is False
    assert matrix["proposal_creates_final_output"] is False
    assert matrix["proposal_writes_drs"] is False
    assert matrix["proposal_executes_actions"] is False


def test_route_recommendation_is_validated():
    report = collect_live_gemini_orchestrator_smoke()

    assert report.orchestration_matrix["route_recommendation"] == "proof_full_pipeline"
    assert report.proposal_validation["route_allowed_by_validator"] is True


def test_guard_set_completeness_is_validated():
    report = collect_live_gemini_orchestrator_smoke()
    guards = set(report.orchestration_matrix["guard_set"])

    assert "Root final authority" in guards
    assert "AVF boundary" in guards
    assert "PlanGraph contract" in guards
    assert "Executor boundary" in guards
    assert "Post V&V" in guards
    assert "GT" in guards
    assert "ReuseGate boundary" in guards
    assert report.proposal_validation["guard_set_complete"] is True


def test_local_drs_only_is_validated():
    report = collect_live_gemini_orchestrator_smoke()

    assert report.orchestration_matrix["drs_scope"] == "local_only"
    assert report.proposal_validation["local_drs_only"] is True


def test_invalid_proposal_path_is_contained():
    report = collect_live_gemini_orchestrator_smoke(
        injected_proposal={"proposal_id": "bad_route", "route_recommendation": "global_drs"}
    )
    validation = report.proposal_validation

    assert validation["orchestrator_proposal_valid"] is True
    assert validation["attempted_proposal_valid"] is False
    assert validation["active_proposal_valid"] is True
    assert validation["active_proposal_source"] == "deterministic_mock_orchestrator"
    assert validation["active_proposal_is_fallback"] is True
    assert validation["invalid_proposal_caught"] is True
    assert validation["contract_violation_contained"] is True
    assert validation["fallback_to_deterministic_orchestrator"] is True
    assert validation["architect_reached_from_invalid_orchestrator"] is False
    assert validation["executor_reached_from_invalid_orchestrator"] is False
    assert validation["root_final_output_created_from_live_orchestrator"] is False
    assert report.orchestration_matrix["proposal_source"] == validation["active_proposal_source"]
    assert report.summary["live_gemini_orchestrator_smoke_status"] == "PASS"


def test_fallback_visible_when_live_proposal_missing_or_invalid(monkeypatch):
    monkeypatch.setenv("HEDGEHOG_ALLOW_LIVE_GEMINI", "1")
    for key in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_GEMINI_API_KEY"):
        monkeypatch.delenv(key, raising=False)

    report = collect_live_gemini_orchestrator_smoke(
        live_requested=True,
        allow_config=False,
    )

    assert report.proposal_validation["fallback_to_deterministic_orchestrator"] is True
    assert report.proposal_validation["contract_violation_contained"] is True
    assert report.proposal_validation["attempted_proposal_valid"] is False
    assert report.proposal_validation["active_proposal_valid"] is True
    assert report.proposal_validation["active_proposal_is_fallback"] is True
    assert report.orchestration_matrix["proposal_source"] == "deterministic_mock_orchestrator"


def test_displayed_orchestration_matrix_source_matches_active_proposal_source():
    report = collect_live_gemini_orchestrator_smoke(
        injected_proposal={"proposal_id": "bad"}
    )

    assert report.orchestration_matrix["proposal_source"] == report.proposal_validation[
        "active_proposal_source"
    ]
    assert report.proposal_validation["active_proposal_valid"] is True
    assert report.proposal_validation["active_proposal_is_fallback"] is True


def test_boundaries_are_preserved():
    boundary = collect_live_gemini_orchestrator_smoke().boundary_checks

    assert boundary["root_boundary_preserved"] is True
    assert boundary["avf_boundary_preserved"] is True
    assert boundary["architect_contract_boundary_preserved"] is True
    assert boundary["executor_boundary_preserved"] is True
    assert boundary["post_vv_boundary_preserved"] is True
    assert boundary["gt_boundary_preserved"] is True
    assert boundary["reuse_gate_boundary_preserved"] is True
    assert boundary["permission_boundary_preserved"] is True
    assert boundary["policy_boundary_preserved"] is True
    assert boundary["gemini_bypassed_root"] is False
    assert boundary["gemini_bypassed_avf"] is False
    assert boundary["gemini_bypassed_architect_contract"] is False
    assert boundary["gemini_bypassed_executor"] is False
    assert boundary["gemini_bypassed_post_vv"] is False
    assert boundary["gemini_bypassed_gt"] is False
    assert boundary["gemini_bypassed_policy"] is False
    assert boundary["gemini_bypassed_permissions"] is False


def test_boundary_checks_are_derived_from_source_role_and_validation():
    report = collect_live_gemini_orchestrator_smoke()
    source = report.source_report
    first_sections = source.first_run_source.sections
    validation = report.proposal_validation
    role = report.role_substitution
    full_canonical_pass = (
        report.full_canonical_e2e_context["full_canonical_e2e_status"] == "PASS"
    )
    role_bounded = (
        role["substituted_role"] == "orchestrator_proposal_actor"
        and not role["gemini_is_root"]
        and not role["gemini_is_architect"]
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
    expected_root = (
        source.summary["first_run_root_authority_preserved"]
        and source.summary["second_run_root_authority_preserved"]
        and not validation["root_final_output_created_from_live_orchestrator"]
    )

    assert report.boundary_checks["avf_boundary_preserved"] == expected_avf
    assert report.boundary_checks["root_boundary_preserved"] == expected_root
    assert report.boundary_checks["reuse_gate_boundary_preserved"] == source.authority_safety[
        "reuse_gate_boundary_preserved"
    ]
    assert report.boundary_checks["gemini_bypassed_root"] == (
        not expected_root or not role_bounded
    )


def test_full_canonical_e2e_collector_is_consumed():
    report = collect_live_gemini_orchestrator_smoke()
    context = report.full_canonical_e2e_context

    assert report.source_report.summary["root_native_full_canonical_e2e_trace_status"] == "PASS"
    assert context["full_canonical_e2e_available"] is True
    assert context["full_canonical_e2e_status"] == "PASS"
    assert context["first_run_stages_passed"] == 9
    assert context["second_run_stages_passed"] == 12


def test_production_persistence_and_reuse_claims_remain_false():
    context = collect_live_gemini_orchestrator_smoke().full_canonical_e2e_context

    assert context["production_persistence_claimed"] is False
    assert context["production_reuse_claimed"] is False
    assert context["production_direct_reuse_executed"] is False
    assert context["production_final_output_created"] is False


def test_no_telegram_action_or_global_external_drs():
    report = collect_live_gemini_orchestrator_smoke()

    assert report.input["telegram_used"] is False
    assert report.authority_safety["live_telegram_action_executed"] is False
    assert report.authority_safety["no_global_drs"] is True
    assert report.authority_safety["no_external_drs_network"] is True


def test_production_autonomy_is_not_claimed():
    report = collect_live_gemini_orchestrator_smoke()

    assert report.authority_safety["production_autonomy_claimed"] is False
    assert report.summary["gemini_authority_granted"] is False


def test_ready_for_future_controlled_orchestrator_integration_requires_boundaries_and_containment():
    report = collect_live_gemini_orchestrator_smoke(
        injected_proposal={"proposal_id": "bad"}
    )

    assert report.boundary_checks["root_boundary_preserved"] is True
    assert report.proposal_validation["contract_violation_contained"] is True
    assert report.summary["ready_for_future_controlled_orchestrator_integration"] is True


def test_rendered_output_omits_credential_env_names_and_secret_terms():
    output = run_live_gemini_orchestrator_smoke()

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
