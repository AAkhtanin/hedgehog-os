from __future__ import annotations

from dataclasses import is_dataclass
import subprocess
import sys

import pytest

import demo.run_live_llm_semantic_evidence_reader_v01 as runner
import hedgehog.live_llm_semantic_evidence_reader as reader


def _claim_by_kind(
    claims: tuple[reader.SemanticEvidenceClaim, ...],
    source_kind: str,
) -> reader.SemanticEvidenceClaim:
    for claim in claims:
        if claim.source_kind == source_kind:
            return claim
    raise AssertionError(f"missing claim for {source_kind}")


def test_module_imports_api_dataclasses_and_functions_exist() -> None:
    assert runner.TITLE == "HEDGEHOG OS — LIVE LLM SEMANTIC EVIDENCE READER v0.1"
    assert is_dataclass(reader.SemanticEvidenceInput)
    assert is_dataclass(reader.SemanticEvidenceClaim)
    assert is_dataclass(reader.SemanticEvidenceReaderReport)
    assert reader.ReaderMode.deterministic_fixture_reader.value == (
        "deterministic_fixture_reader"
    )
    assert callable(reader.build_semantic_evidence_claims)
    assert callable(reader.evaluate_semantic_evidence_inputs)
    assert callable(reader.run_live_llm_semantic_evidence_reader_scenarios)


def test_reader_mode_defaults_are_safe() -> None:
    default_inputs = reader.make_default_inputs()
    assert all(
        item.reader_mode is reader.ReaderMode.deterministic_fixture_reader
        for item in default_inputs
    )

    result = reader.run_live_llm_semantic_evidence_reader_scenarios()
    counters = result["counters"]

    assert result["reader_mode"] == "deterministic_fixture_reader"
    assert result["live_llm_reader_default_enabled"] is False
    assert result["live_llm_reader_core_pass_dependency"] is False
    assert counters["deterministic_fixture_reader_used_count"] == 1
    assert counters["live_llm_default_enabled_count"] == 0
    assert counters["live_llm_core_pass_dependency_count"] == 0
    assert counters["live_model_call_count"] == 0


def test_live_llm_reader_mode_fails_closed_when_explicitly_requested() -> None:
    with pytest.raises(ValueError) as exc_info:
        reader.build_semantic_evidence_claims(
            reader.make_default_inputs(),
            reader_mode=reader.ReaderMode.live_llm_reader,
        )

    message = str(exc_info.value)
    assert "disabled" in message
    assert "v0.1 deterministic runner" in message
    assert (
        message
        == "live_llm_reader is disabled in v0.1 deterministic runner"
    )


def test_evaluate_live_llm_reader_mode_fails_closed_when_explicitly_requested() -> None:
    with pytest.raises(ValueError) as exc_info:
        reader.evaluate_semantic_evidence_inputs(
            reader.make_default_inputs(),
            reader_mode=reader.ReaderMode.live_llm_reader,
        )

    message = str(exc_info.value)
    assert "disabled" in message
    assert "v0.1 deterministic runner" in message

    deterministic_result = reader.run_live_llm_semantic_evidence_reader_scenarios()
    counters = deterministic_result["counters"]
    assert counters["live_model_call_count"] == 0
    assert counters["network_used_count"] == 0
    assert counters["gemini_used_count"] == 0
    assert counters["secrets_accessed_count"] == 0
    assert counters["connector_command_created_count"] == 0


def test_build_claims_and_evaluate_report_return_structured_outputs() -> None:
    inputs = reader.make_default_inputs()
    claims = reader.build_semantic_evidence_claims(inputs)
    report = reader.evaluate_semantic_evidence_inputs(inputs)

    assert len(inputs) == len(reader.INPUT_KINDS)
    assert len(claims) == len(inputs)
    assert report.final_status == "PASS"
    assert report.reader_mode is reader.ReaderMode.deterministic_fixture_reader
    assert report.inputs_seen == len(inputs)
    assert report.claims_created == len(claims)
    assert report.claims == claims
    assert report.counters["semantic_claims_created_count"] == len(claims)
    assert report.counters["semantic_claim_routed_as_candidate_count"] == len(claims)

    for claim in claims:
        assert claim.action_permission_claimed is False
        assert claim.authority_claimed is False
        assert claim.truth_claimed is False
        assert claim.final_output_claimed is False
        assert claim.connector_command_claimed is False
        assert claim.root_review_required is True


def test_semantic_behavior_boundaries_per_input_kind() -> None:
    report = reader.evaluate_semantic_evidence_inputs(reader.make_default_inputs())
    claims = report.claims

    invoice = _claim_by_kind(claims, "dirty_supplier_invoice")
    warehouse = _claim_by_kind(claims, "warehouse_stock_note")
    supplier_email = _claim_by_kind(claims, "business_email_request")
    bank_slot = _claim_by_kind(claims, "bank_payment_slot_note")
    conflict = _claim_by_kind(claims, "contradictory_evidence_bundle")
    legal = _claim_by_kind(claims, "legal_compliance_note")
    stale = _claim_by_kind(claims, "stale_drs_memory_text")

    assert invoice.truth_claimed is False
    assert "invoice" in invoice.extracted_claim
    assert warehouse.action_requested == "release_shipment"
    assert report.counters["shipment_released_count"] == 0
    assert supplier_email.action_requested == "pay_and_release"
    assert report.counters["supplier_command_created_count"] == 0
    assert bank_slot.action_requested == "execute_payment"
    assert report.counters["payment_executed_count"] == 0
    assert conflict.contradiction_flags
    assert conflict.authority_claimed is False
    assert legal.final_output_claimed is False
    assert legal.root_review_required is True
    assert stale.freshness_hint == "stale"
    assert "stale_memory_uncertain_context_only" in stale.uncertainty_notes


def test_claims_route_to_drs_avf_advisory_as_candidates_only() -> None:
    result = reader.run_live_llm_semantic_evidence_reader_scenarios()
    scenarios = {item["scenario_id"]: item for item in result["scenarios"]}
    routed = scenarios[
        "live_llm_claims_are_routed_to_drs_avf_advisory_as_candidates_only"
    ]

    assert routed["status"] == "PASS"
    assert "semantic_claims_candidates_only" in routed["reason_codes"]
    assert routed["details"]["semantic_claim_routed_as_candidate_count"] == result[
        "counters"
    ]["semantic_claims_created_count"]
    assert result["counters"]["semantic_claim_routed_as_candidate_count"] == result[
        "counters"
    ]["semantic_claims_created_count"]


def test_prompt_injection_cannot_escalate_authority() -> None:
    result = reader.run_live_llm_semantic_evidence_reader_scenarios()
    scenarios = {item["scenario_id"]: item for item in result["scenarios"]}
    injection = scenarios["live_llm_prompt_injection_cannot_escalate_authority"]
    injection_claim = _claim_by_kind(result["report"].claims, "prompt_injection_document")

    assert injection["status"] == "PASS"
    assert injection["details"]["hostile_text_preserved"] is True
    assert injection_claim.unsafe_instruction_flags == (
        "pay_now_instruction_blocked",
        "root_impersonation_blocked",
        "bank_connector_command_blocked",
        "hidden_credentials_request_blocked",
        "executor_route_bypass_blocked",
        "post_vv_gt_skip_blocked",
    )
    assert result["counters"]["unsafe_instruction_flags_created_count"] == 6
    assert result["counters"]["prompt_injection_escalation_count"] == 0
    assert result["counters"]["connector_command_created_count"] == 0
    assert result["counters"]["bank_command_created_count"] == 0
    assert result["counters"]["supplier_command_created_count"] == 0
    assert result["counters"]["warehouse_command_created_count"] == 0
    assert result["counters"]["architect_commanded_count"] == 0
    assert result["counters"]["executor_commanded_count"] == 0
    assert result["counters"]["fractal_cell_commanded_count"] == 0


def test_all_zero_authority_action_external_counters_are_zero() -> None:
    result = reader.run_live_llm_semantic_evidence_reader_scenarios()
    counters = result["counters"]

    assert result["final_status"] == "PASS"
    assert counters["scenarios_total"] == 10
    assert counters["scenarios_passed"] == 10
    assert result["pass_conditions"]["zero_authority_action_external_counters"] is True
    for key in reader.ZERO_COUNTER_KEYS:
        assert counters[key] == 0
    assert counters["root_final_authority_preserved_count"] == counters[
        "scenarios_total"
    ]


def test_runner_main_and_command_output_exit_zero(capsys) -> None:
    assert runner.main() == 0
    output = capsys.readouterr().out
    assert runner.TITLE in output
    assert "FINAL STATUS: PASS" in output

    completed = subprocess.run(
        [sys.executable, "-m", "demo.run_live_llm_semantic_evidence_reader_v01"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0
    assert runner.TITLE in completed.stdout
    assert "FINAL STATUS: PASS" in completed.stdout


def test_runner_output_includes_required_sections_scenarios_and_counters() -> None:
    output = runner.render_report()

    required_markers = (
        "Reader mode summary:",
        "Input evidence summary:",
        "Topology summary:",
        "Semantic claim shape summary:",
        "Prompt injection boundary summary:",
        "Connection to Zero Trust Supplier Payment WOW:",
        "Aggregate counters:",
        "Authority boundary summary:",
        "Limitations:",
        "scenarios_total: 10",
        "scenarios_passed: 10",
        "live_llm_default_enabled_count: 0",
        "live_llm_core_pass_dependency_count: 0",
        "live_model_call_count: 0",
        "network_used_count: 0",
        "gemini_used_count: 0",
        "secrets_accessed_count: 0",
        "truth_claimed_count: 0",
        "authority_claimed_count: 0",
        "action_permission_claimed_count: 0",
        "final_output_claimed_count: 0",
        "payment_executed_count: 0",
        "shipment_released_count: 0",
        "prompt_injection_escalation_count: 0",
        "root_final_authority_preserved_count: 10",
        "Root remains final authority",
        "Real Semantic Runtime MVP is not complete",
    )
    for marker in required_markers:
        assert marker in output

    for scenario_id in reader.SCENARIOS:
        assert scenario_id in output


def test_runner_output_does_not_claim_forbidden_readiness_or_authority() -> None:
    output = runner.render_report()
    forbidden = (
        "production " + "ready",
        "public auditor " + "ready",
        "production E2E " + "implemented",
        "live LLM is " + "authority",
        "LLM output is " + "truth",
        "LLM output is " + "authority",
        "payment " + "executed",
        "shipment " + "released",
        "real bank API " + "called",
        "real supplier API " + "called",
        "secrets " + "accessed",
        "network used: " + "true",
        "Gemini used: " + "true",
        "real model call " + "required",
        "runtime " + "complete",
        "Real Semantic Runtime MVP " + "implemented",
        "public launch " + "ready",
        "whitepaper " + "ready",
    )

    for marker in forbidden:
        assert marker not in output
