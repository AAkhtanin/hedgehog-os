from __future__ import annotations

import json
import sys
import types

from demo.run_live_gemini_ordered_orchestrator_architect_smoke import (
    ORCHESTRATOR_PROPOSAL_JSON_SCHEMA,
    collect_live_gemini_ordered_orchestrator_architect_smoke,
    run_live_gemini_ordered_orchestrator_architect_smoke,
)
from demo.run_live_gemini_orchestrator_smoke import (
    LIVE_ENV_GATE,
    REQUIRED_DOWNSTREAM_ACTORS,
    REQUIRED_FORBIDDEN_VECTOR_CLASSES,
    REQUIRED_GUARDS,
    _deterministic_orchestrator_proposal,
)


def _install_fake_genai(monkeypatch, responses, calls):
    fake_google = types.ModuleType("google")
    fake_genai = types.ModuleType("google.genai")

    class FakeResponse:
        def __init__(self, text: str):
            self.text = text

    class FakeModels:
        def generate_content(self, *, model, contents, config):
            calls.append({"model": model, "contents": contents, "config": config})
            response = responses.pop(0) if responses else {}
            return FakeResponse(json.dumps(response))

    class FakeClient:
        def __init__(self, *, api_key):
            self.models = FakeModels()

    fake_genai.Client = FakeClient
    fake_google.genai = fake_genai
    monkeypatch.setitem(sys.modules, "google", fake_google)
    monkeypatch.setitem(sys.modules, "google.genai", fake_genai)


def test_runner_output_contains_title_and_sections():
    output = run_live_gemini_ordered_orchestrator_architect_smoke()

    assert "[LIVE GEMINI ORDERED ORCHESTRATOR ARCHITECT SMOKE]" in output
    assert "[INPUT]" in output
    assert "[ORDERED ROLE FLOW]" in output
    assert "[ORCHESTRATOR STAGE]" in output
    assert "[ARCHITECT STAGE]" in output
    assert "[BOUNDARY CHECKS]" in output
    assert "[FULL CANONICAL E2E CONTEXT]" in output
    assert "[AUTHORITY / SAFETY]" in output
    assert "[SUMMARY]" in output


def test_orchestrator_schema_exists_and_contains_required_fields():
    schema = ORCHESTRATOR_PROPOSAL_JSON_SCHEMA

    assert schema["type"] == "object"
    for field in (
        "proposal_id",
        "proposal_source",
        "input_task",
        "intent_classification",
        "route_recommendation",
        "route_confidence",
        "temporal_query_required",
        "drs_retrieval_intent",
        "drs_scope",
        "avf_context",
        "candidate_vector_hints",
        "forbidden_vector_classes",
        "guard_set",
        "permission_requirements",
        "risk_flags",
        "budget_hints",
        "downstream_actors",
        "fallback_route",
        "audit_tags",
        "explanation",
        "proposal_is_action",
        "proposal_creates_final_output",
        "proposal_writes_drs",
        "proposal_executes_actions",
    ):
        assert field in schema["required"]
        assert field in schema["properties"]


def test_schema_route_and_drs_scope_are_narrow_enums():
    properties = ORCHESTRATOR_PROPOSAL_JSON_SCHEMA["properties"]

    assert properties["route_recommendation"]["enum"] == ["proof_full_pipeline"]
    assert properties["drs_scope"]["enum"] == ["local_only"]
    assert properties["temporal_query_required"]["type"] == "boolean"


def test_schema_represents_required_guards_downstream_actors_and_forbidden_vector_classes():
    properties = ORCHESTRATOR_PROPOSAL_JSON_SCHEMA["properties"]

    assert set(properties["guard_set"]["items"]["enum"]) == REQUIRED_GUARDS
    assert set(properties["downstream_actors"]["items"]["enum"]) == REQUIRED_DOWNSTREAM_ACTORS
    assert set(properties["forbidden_vector_classes"]["items"]["enum"]) == REQUIRED_FORBIDDEN_VECTOR_CLASSES


def test_default_mode_is_deterministic_and_network_free():
    report = collect_live_gemini_ordered_orchestrator_architect_smoke()

    assert report.input["mode"] == "dry_run_default"
    assert report.input["network_free"] is True
    assert report.input["live_gemini_used"] is False
    assert report.summary["live_gemini_used"] is False


def test_ordered_flow_has_orchestrator_before_architect():
    flow = collect_live_gemini_ordered_orchestrator_architect_smoke().ordered_role_flow

    assert flow["root_boundary_entered"] is True
    assert flow["orchestrator_runs_before_architect"] is True
    assert flow["architect_runs_after_valid_orchestrator"] is True


def test_architect_runs_only_after_valid_active_orchestrator_proposal():
    report = collect_live_gemini_ordered_orchestrator_architect_smoke()

    assert report.orchestrator_stage["orchestrator_active_proposal_valid"] is True
    assert report.architect_stage["plan_graph_contract_checked"] is True
    assert report.ordered_role_flow["architect_runs_after_valid_orchestrator"] is True


def test_invalid_orchestrator_proposal_does_not_reach_architect():
    report = collect_live_gemini_ordered_orchestrator_architect_smoke(
        injected_orchestrator_proposal={"proposal_id": "bad", "route_recommendation": "global_drs"}
    )

    assert report.orchestrator_stage["orchestrator_initial_attempt_valid"] is False
    assert report.orchestrator_stage["invalid_orchestrator_caught"] is True
    assert report.orchestrator_stage["architect_reached_from_invalid_orchestrator"] is False
    assert report.ordered_role_flow["executor_not_reached_from_invalid_orchestrator"] is True


def test_invalid_orchestrator_proposal_can_fallback_to_deterministic_orchestrator():
    report = collect_live_gemini_ordered_orchestrator_architect_smoke(
        injected_orchestrator_proposal={"proposal_id": "bad"}
    )

    assert report.orchestrator_stage["fallback_to_deterministic_orchestrator"] is True
    assert report.orchestrator_stage["orchestrator_active_proposal_valid"] is True
    assert report.orchestrator_stage["orchestrator_active_proposal_source"] == "deterministic_mock_orchestrator"
    assert report.orchestrator_stage["orchestrator_active_proposal_is_fallback"] is True


def test_one_shot_repair_fields_exist():
    stage = collect_live_gemini_ordered_orchestrator_architect_smoke().orchestrator_stage

    assert "orchestrator_repair_attempted" in stage
    assert "orchestrator_repair_valid" in stage
    assert stage["orchestrator_repair_attempted"] is False
    assert stage["orchestrator_repair_valid"] is False


def test_default_mode_reports_no_structured_live_schema_request():
    stage = collect_live_gemini_ordered_orchestrator_architect_smoke().orchestrator_stage

    assert stage["orchestrator_structured_output_requested"] is False
    assert stage["orchestrator_schema_used"] is False
    assert stage["orchestrator_schema_name"] == "orchestrator_proposal_v0_1"
    assert stage["orchestrator_schema_config_key"] == "none"
    assert stage["orchestrator_initial_validation_errors"] == []
    assert stage["orchestrator_repair_validation_errors"] == []
    assert stage["temporal_query_required_value"] is True
    assert stage["downstream_actors_missing"] == []
    assert stage["downstream_actors_extra"] == []
    assert set(stage["required_downstream_actors"]) == REQUIRED_DOWNSTREAM_ACTORS


def test_injected_proposal_missing_downstream_actor_reports_missing_actor():
    proposal = _deterministic_orchestrator_proposal(source="injected_missing_actor")
    removed = "DRS audit/writeback proof"
    proposal["downstream_actors"] = [
        actor for actor in proposal["downstream_actors"] if actor != removed
    ]

    report = collect_live_gemini_ordered_orchestrator_architect_smoke(
        injected_orchestrator_proposal=proposal
    )
    stage = report.orchestrator_stage

    assert stage["orchestrator_initial_attempt_valid"] is False
    assert "downstream_actors_complete" in stage["orchestrator_initial_validation_errors"]
    assert stage["orchestrator_initial_downstream_actors_missing"] == [removed]
    assert stage["orchestrator_initial_downstream_actors_extra"] == []
    assert stage["orchestrator_active_proposal_valid"] is True
    assert stage["downstream_actors_missing"] == []
    assert stage["fallback_to_deterministic_orchestrator"] is True


def test_injected_proposal_with_false_temporal_query_reports_actual_value():
    proposal = _deterministic_orchestrator_proposal(source="injected_temporal_false")
    proposal["temporal_query_required"] = False

    report = collect_live_gemini_ordered_orchestrator_architect_smoke(
        injected_orchestrator_proposal=proposal
    )
    stage = report.orchestrator_stage

    assert stage["orchestrator_initial_attempt_valid"] is False
    assert "temporal_query_required" in stage["orchestrator_initial_validation_errors"]
    assert stage["orchestrator_initial_temporal_query_required_value"] is False
    assert stage["temporal_query_required_value"] is True
    assert stage["orchestrator_active_proposal_valid"] is True


def test_live_orchestrator_call_requests_structured_output_schema(monkeypatch):
    proposal = _deterministic_orchestrator_proposal(source="live_gemini")
    calls = []
    _install_fake_genai(monkeypatch, [proposal], calls)
    monkeypatch.setenv(LIVE_ENV_GATE, "1")
    monkeypatch.setenv("GEMINI_API_KEY", "test-only")

    report = collect_live_gemini_ordered_orchestrator_architect_smoke(
        live_requested=True,
        allow_config=False,
    )

    assert report.orchestrator_stage["orchestrator_structured_output_requested"] is True
    assert report.orchestrator_stage["orchestrator_schema_used"] is True
    assert report.orchestrator_stage["orchestrator_schema_config_key"] == "response_json_schema"
    assert report.orchestrator_stage["orchestrator_initial_attempt_valid"] is True
    assert report.orchestrator_stage["orchestrator_active_proposal_source"] == "live_gemini"
    assert report.orchestrator_stage["temporal_query_required_value"] is True
    assert report.orchestrator_stage["downstream_actors_missing"] == []
    assert report.orchestrator_stage["downstream_actors_extra"] == []
    assert calls[0]["config"]["response_mime_type"] == "application/json"
    assert calls[0]["config"]["response_json_schema"] == ORCHESTRATOR_PROPOSAL_JSON_SCHEMA
    prompt = json.loads(calls[0]["contents"])
    assert prompt["temporal_query_required"] == "temporal_query_required MUST be true."
    assert set(prompt["required_downstream_actors"]) == REQUIRED_DOWNSTREAM_ACTORS
    assert "Do not rename downstream actors" in prompt["downstream_actors_rule"]


def test_live_orchestrator_call_can_fallback_to_response_schema_key(monkeypatch):
    proposal = _deterministic_orchestrator_proposal(source="live_gemini")
    calls = []
    fake_google = types.ModuleType("google")
    fake_genai = types.ModuleType("google.genai")

    class FakeResponse:
        def __init__(self, text: str):
            self.text = text

    class FakeModels:
        def generate_content(self, *, model, contents, config):
            calls.append({"model": model, "contents": contents, "config": config})
            if "response_json_schema" in config:
                raise RuntimeError("unsupported schema key")
            return FakeResponse(json.dumps(proposal))

    class FakeClient:
        def __init__(self, *, api_key):
            self.models = FakeModels()

    fake_genai.Client = FakeClient
    fake_google.genai = fake_genai
    monkeypatch.setitem(sys.modules, "google", fake_google)
    monkeypatch.setitem(sys.modules, "google.genai", fake_genai)
    monkeypatch.setenv(LIVE_ENV_GATE, "1")
    monkeypatch.setenv("GEMINI_API_KEY", "test-only")

    report = collect_live_gemini_ordered_orchestrator_architect_smoke(
        live_requested=True,
        allow_config=False,
    )

    assert report.orchestrator_stage["orchestrator_initial_attempt_valid"] is True
    assert report.orchestrator_stage["orchestrator_schema_used"] is True
    assert report.orchestrator_stage["orchestrator_schema_config_key"] == "response_schema"
    assert "response_json_schema" in calls[0]["config"]
    assert "response_schema" in calls[1]["config"]


def test_repair_path_also_requests_structured_output_schema(monkeypatch):
    repaired = _deterministic_orchestrator_proposal(source="live_gemini")
    calls = []
    _install_fake_genai(monkeypatch, [{"proposal_id": "bad"}, repaired], calls)
    monkeypatch.setenv(LIVE_ENV_GATE, "1")
    monkeypatch.setenv("GEMINI_API_KEY", "test-only")

    report = collect_live_gemini_ordered_orchestrator_architect_smoke(
        live_requested=True,
        allow_config=False,
    )

    assert report.orchestrator_stage["orchestrator_initial_attempt_valid"] is False
    assert report.orchestrator_stage["orchestrator_repair_attempted"] is True
    assert report.orchestrator_stage["orchestrator_repair_valid"] is True
    assert report.orchestrator_stage["orchestrator_active_proposal_source"] == "live_gemini_repair"
    assert report.orchestrator_stage["orchestrator_schema_used"] is True
    assert report.orchestrator_stage["orchestrator_schema_config_key"] == "response_json_schema"
    assert "matrix_fields_present" in report.orchestrator_stage["orchestrator_initial_validation_errors"]
    assert report.orchestrator_stage["orchestrator_repair_validation_errors"] == []
    assert report.orchestrator_stage["orchestrator_repair_temporal_query_required_value"] is True
    assert calls[0]["config"]["response_json_schema"] == ORCHESTRATOR_PROPOSAL_JSON_SCHEMA
    assert calls[1]["config"]["response_json_schema"] == ORCHESTRATOR_PROPOSAL_JSON_SCHEMA
    repair_prompt = json.loads(calls[1]["contents"])
    assert repair_prompt["repair_instruction"] == "Return only corrected JSON."
    assert set(repair_prompt["required_downstream_actors"]) == REQUIRED_DOWNSTREAM_ACTORS


def test_active_proposal_source_is_explicit():
    stage = collect_live_gemini_ordered_orchestrator_architect_smoke().orchestrator_stage

    assert stage["orchestrator_active_proposal_source"] == "deterministic_mock_orchestrator"
    assert stage["orchestrator_active_proposal_is_fallback"] is False


def test_route_recommendation_is_proof_full_pipeline():
    stage = collect_live_gemini_ordered_orchestrator_architect_smoke().orchestrator_stage

    assert stage["route_recommendation"] == "proof_full_pipeline"


def test_drs_scope_is_local_only():
    stage = collect_live_gemini_ordered_orchestrator_architect_smoke().orchestrator_stage

    assert stage["drs_scope"] == "local_only"
    assert stage["local_drs_only"] is True


def test_guard_set_complete_is_true():
    stage = collect_live_gemini_ordered_orchestrator_architect_smoke().orchestrator_stage

    assert stage["guard_set_complete"] is True
    assert stage["route_allowed_by_validator"] is True
    assert stage["proposal_only"] is True


def test_architect_plan_graph_contract_is_checked():
    architect = collect_live_gemini_ordered_orchestrator_architect_smoke().architect_stage

    assert architect["architect_artifact_source"] == "deterministic_mock_architect"
    assert architect["architect_artifact_valid"] is True
    assert architect["plan_graph_contract_checked"] is True
    assert architect["plan_graph_present"] is True


def test_invalid_architect_output_is_contained_if_injected():
    report = collect_live_gemini_ordered_orchestrator_architect_smoke(
        injected_architect_artifact={"nodes": []}
    )
    architect = report.architect_stage

    assert architect["invalid_architect_artifact_caught"] is True
    assert architect["fallback_to_deterministic_architect"] is True
    assert architect["executor_reached_from_invalid_architect"] is False
    assert architect["root_final_output_created_from_live_architect"] is False
    assert report.summary["live_gemini_ordered_orchestrator_architect_smoke_status"] == "PASS"


def test_gemini_does_not_create_final_output_write_drs_or_execute_actions():
    authority = collect_live_gemini_ordered_orchestrator_architect_smoke().authority_safety

    assert authority["gemini_created_final_output"] is False
    assert authority["gemini_wrote_drs"] is False
    assert authority["gemini_executed_action"] is False
    assert authority["gemini_authority_granted"] is False


def test_no_telegram_action_global_or_external_drs():
    report = collect_live_gemini_ordered_orchestrator_architect_smoke()

    assert report.input["telegram_used"] is False
    assert report.authority_safety["live_telegram_action_executed"] is False
    assert report.authority_safety["no_global_drs"] is True
    assert report.authority_safety["no_external_drs_network"] is True


def test_full_canonical_e2e_source_consumed():
    report = collect_live_gemini_ordered_orchestrator_architect_smoke()

    assert report.source_report.summary["root_native_full_canonical_e2e_trace_status"] == "PASS"
    assert report.full_canonical_e2e_context["full_canonical_e2e_status"] == "PASS"
    assert report.full_canonical_e2e_context["first_run_stages_passed"] == 9
    assert report.full_canonical_e2e_context["second_run_stages_passed"] == 12


def test_production_persistence_and_reuse_claims_false():
    context = collect_live_gemini_ordered_orchestrator_architect_smoke().full_canonical_e2e_context

    assert context["production_persistence_claimed"] is False
    assert context["production_reuse_claimed"] is False
    assert context["production_direct_reuse_executed"] is False
    assert context["production_final_output_created"] is False


def test_pass_summary_derived_from_structured_facts():
    report = collect_live_gemini_ordered_orchestrator_architect_smoke()
    expected_ready = (
        report.ordered_role_flow["orchestrator_runs_before_architect"]
        and report.ordered_role_flow["architect_runs_after_valid_orchestrator"]
        and report.orchestrator_stage["orchestrator_active_proposal_valid"]
        and report.architect_stage["architect_artifact_valid"]
        and report.boundary_checks["root_boundary_preserved"]
        and report.boundary_checks["policy_boundary_preserved"]
        and not report.authority_safety["production_final_output_created"]
        and not report.authority_safety["production_external_action_executed"]
    )

    assert report.summary["ready_for_future_controlled_orchestrator_integration"] == expected_ready
    assert report.summary["live_gemini_ordered_orchestrator_architect_smoke_status"] == "PASS"


def test_rendered_output_omits_credential_env_names_and_secret_terms():
    output = run_live_gemini_ordered_orchestrator_architect_smoke()

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
