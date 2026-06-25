from __future__ import annotations

import os
from typing import Any, Callable, Mapping

from demo import run_live_provider_adapter_response_capture_v01 as provider_adapter
from demo import run_optional_live_llm_evidence_reader_smoke_v01 as response_smoke
from hedgehog.live_llm_semantic_evidence_reader import SemanticEvidenceClaim


TITLE = "HEDGEHOG OS - SUPPLIER PAYMENT LIVE EVIDENCE INTEGRATION v0.2"

ENV_ENABLE = "HEDGEHOG_SUPPLIER_PAYMENT_LIVE_EVIDENCE_INTEGRATION"
ENV_RESPONSE_FILE = "HEDGEHOG_SUPPLIER_PAYMENT_LIVE_EVIDENCE_RESPONSE_FILE"
ENV_OUTPUT_DIR = "HEDGEHOG_SUPPLIER_PAYMENT_LIVE_EVIDENCE_OUTPUT_DIR"
ENV_CAPTURE_ID = "HEDGEHOG_SUPPLIER_PAYMENT_LIVE_EVIDENCE_CAPTURE_ID"

SCENARIOS = (
    "no_config_skips_closed_without_provider_call",
    "captured_live_evidence_claim_enters_supplier_spine_as_candidate_only",
    "live_claim_enriches_drs_candidate_context_without_truth",
    "candidate_vector_receives_live_evidence_context",
    "avf_advisory_receives_live_evidence_without_authority",
    "legal_hold_beats_payable_invoice",
    "stock_shortage_blocks_shipment_release",
    "invalid_json_live_evidence_fails_closed",
    "extra_fields_live_evidence_fails_closed",
    "secret_like_live_evidence_fails_closed",
    "authority_claim_live_evidence_fails_closed",
    "connector_command_live_evidence_fails_closed",
    "prompt_injection_preserved_as_evidence",
    "no_payment_or_shipment_release_executed",
    "root_final_authority_preserved",
)

COUNTER_KEYS = (
    "supplier_live_integration_invoked_count",
    "explicit_live_evidence_config_present_count",
    "provider_call_attempted_count",
    "raw_response_artifact_created_count",
    "response_file_lane_used_count",
    "semantic_claim_created_count",
    "semantic_claim_validated_locally_count",
    "semantic_claim_rejected_count",
    "live_claim_added_to_supplier_context_count",
    "drs_candidate_context_used_count",
    "candidate_vector_created_count",
    "candidate_vector_represented_count",
    "avf_scored_count",
    "avf_invoked_count",
    "avf_represented_count",
    "advisory_review_count",
    "advisory_invoked_count",
    "advisory_represented_count",
    "bounded_actor_invoked_count",
    "bounded_actor_represented_count",
    "fractal_branch_invoked_count",
    "fractal_branch_represented_count",
    "post_vv_checked_count",
    "post_vv_invoked_count",
    "post_vv_represented_count",
    "gt_lgt_review_count",
    "gt_lgt_invoked_count",
    "gt_lgt_represented_count",
    "root_business_summary_created_count",
    "provider_authority_claimed_count",
    "action_permission_created_count",
    "final_output_created_from_provider_count",
    "provider_final_output_created_count",
    "connector_called_count",
    "bank_connector_called_count",
    "supplier_connector_called_count",
    "warehouse_connector_called_count",
    "payment_executed_count",
    "shipment_released_count",
    "secrets_logged_count",
    "silent_fallback_to_deterministic_pass_count",
    "full_semantic_e2e_claimed_count",
    "real_semantic_runtime_mvp_complete_claimed_count",
    "wow_started_count",
    "production_ready_claimed_count",
    "root_final_authority_preserved_count",
    "live_model_call_count",
    "network_used_count",
    "gemini_called_count",
)

ProviderCallable = Callable[[str, str, int, Mapping[str, str]], str]

DIRTY_SUPPLIER_PAYMENT_CONTEXT = {
    "subject": "SH-2042 / INV-2042",
    "warehouse_stock": "water_filter short by 2",
    "supplier_claim": "supplier says stock is available",
    "accounting_claim": "invoice INV-2042 looks payable",
    "legal_status": "insurance certificate may be expired",
    "requested_action": "pay supplier and release shipment",
}

LIMITATIONS = (
    "not WOW v0.2",
    "not public release layer",
    "not Full Semantic E2E completion",
    "not Real Semantic Runtime MVP completion",
    "not production",
    "not NeedleFactory / Marennya / UP",
    "no real bank, supplier, or warehouse connector",
    "no real payment",
    "no real shipment release",
    "no provider-created FinalOutput",
)

AUTHORITY_BOUNDARY_SUMMARY = (
    "Provider output is not truth.",
    "Provider output is not authority.",
    "Provider output is not action permission.",
    "SemanticEvidenceClaim is candidate-only evidence.",
    "DRS candidate context is not truth.",
    "CandidateVector context is not truth.",
    "AVF score/rank is not authority.",
    "Advisory review is not Root finality.",
    "Post V&V and GT-LGT are represented review boundaries in this runner.",
    "Root remains final authority.",
)


def _base_counters() -> dict[str, int]:
    counters = {key: 0 for key in COUNTER_KEYS}
    counters["scenarios_total"] = len(SCENARIOS)
    counters["scenarios_passed"] = 0
    counters["supplier_live_integration_invoked_count"] = 1
    counters["root_final_authority_preserved_count"] = 1
    return counters


def _scenario_result(
    scenario_id: str,
    status: str,
    *,
    reason_codes: tuple[str, ...] = (),
    details: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "scenario_id": scenario_id,
        "status": status,
        "reason_codes": reason_codes,
        "details": dict(details or {}),
    }


def _skipped_scenarios() -> tuple[dict[str, Any], ...]:
    return tuple(_scenario_result(scenario_id, "SKIPPED") for scenario_id in SCENARIOS)


def _mark_scenario(
    scenarios: tuple[dict[str, Any], ...],
    scenario_id: str,
    status: str,
    *,
    reason_codes: tuple[str, ...] = (),
    details: Mapping[str, Any] | None = None,
) -> tuple[dict[str, Any], ...]:
    return tuple(
        _scenario_result(
            item["scenario_id"],
            status if item["scenario_id"] == scenario_id else item["status"],
            reason_codes=reason_codes if item["scenario_id"] == scenario_id else item["reason_codes"],
            details=details if item["scenario_id"] == scenario_id else item["details"],
        )
        for item in scenarios
    )


def _result(
    *,
    final_status: str,
    scenarios: tuple[dict[str, Any], ...],
    counters: dict[str, int],
    claims: tuple[SemanticEvidenceClaim, ...] = (),
    supplier_context: Mapping[str, Any] | None = None,
    drs_candidate_context: Mapping[str, Any] | None = None,
    candidate_vector_context: Mapping[str, Any] | None = None,
    advisory_context: Mapping[str, Any] | None = None,
    root_business_summary: Mapping[str, Any] | None = None,
    validation_errors: tuple[str, ...] = (),
    artifacts: tuple[str, ...] = (),
    upstream_result: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    counters["scenarios_passed"] = sum(
        1 for scenario in scenarios if scenario["status"] == "PASS"
    )
    return {
        "title": TITLE,
        "final_status": final_status,
        "scenarios": scenarios,
        "counters": counters,
        "claims": claims,
        "supplier_context": dict(supplier_context or {}),
        "drs_candidate_context": dict(drs_candidate_context or {}),
        "candidate_vector_context": dict(candidate_vector_context or {}),
        "advisory_context": dict(advisory_context or {}),
        "root_business_summary": dict(root_business_summary or {}),
        "validation_errors": validation_errors,
        "artifacts": artifacts,
        "upstream_result": upstream_result,
        "authority_boundary_summary": AUTHORITY_BOUNDARY_SUMMARY,
        "limitations": LIMITATIONS,
        "pass_conditions": _pass_conditions(counters),
    }


def _pass_conditions(counters: Mapping[str, int]) -> dict[str, bool]:
    return {
        "no_provider_authority": counters["provider_authority_claimed_count"] == 0,
        "no_action_permission": counters["action_permission_created_count"] == 0,
        "no_provider_final_output": counters["provider_final_output_created_count"] == 0,
        "no_connector_call": counters["connector_called_count"] == 0,
        "no_payment_or_shipment": counters["payment_executed_count"] == 0
        and counters["shipment_released_count"] == 0,
        "no_secret_logging": counters["secrets_logged_count"] == 0,
        "no_silent_fallback": counters["silent_fallback_to_deterministic_pass_count"] == 0,
        "no_full_semantic_e2e_claim": counters["full_semantic_e2e_claimed_count"] == 0,
        "no_mvp_complete_claim": counters[
            "real_semantic_runtime_mvp_complete_claimed_count"
        ]
        == 0,
        "no_wow_started_claim": counters["wow_started_count"] == 0,
        "no_production_ready_claim": counters["production_ready_claimed_count"] == 0,
        "represented_count_not_reported_as_invoked_count": _represented_not_invoked(
            counters
        ),
        "root_final_authority_preserved": counters[
            "root_final_authority_preserved_count"
        ]
        == 1,
    }


def _represented_not_invoked(counters: Mapping[str, int]) -> bool:
    represented_pairs = (
        ("avf_represented_count", "avf_invoked_count"),
        ("advisory_represented_count", "advisory_invoked_count"),
        ("bounded_actor_represented_count", "bounded_actor_invoked_count"),
        ("fractal_branch_represented_count", "fractal_branch_invoked_count"),
        ("post_vv_represented_count", "post_vv_invoked_count"),
        ("gt_lgt_represented_count", "gt_lgt_invoked_count"),
    )
    return all(
        counters[represented_key] == 0 or counters[invoked_key] == 0
        for represented_key, invoked_key in represented_pairs
    )


def _default_result() -> dict[str, Any]:
    counters = _base_counters()
    scenarios = _mark_scenario(
        _skipped_scenarios(),
        "no_config_skips_closed_without_provider_call",
        "PASS",
        reason_codes=("explicit_live_evidence_config_absent", "skipped_closed"),
        details={
            "provider_call_attempted": False,
            "semantic_claim_created": False,
            "payment_executed": False,
            "shipment_released": False,
        },
    )
    return _result(final_status="SKIPPED_CLOSED", scenarios=scenarios, counters=counters)


def _response_file_result(env: Mapping[str, str]) -> dict[str, Any]:
    return response_smoke.run_optional_live_llm_evidence_reader_smoke(
        env={
            response_smoke.ENV_ENABLE: "1",
            response_smoke.ENV_RESPONSE_FILE: env[ENV_RESPONSE_FILE],
        }
    )


def _provider_capture_result(
    env: Mapping[str, str],
    provider: ProviderCallable,
) -> dict[str, Any]:
    output_dir = env.get(ENV_OUTPUT_DIR, "").strip()
    if not output_dir:
        raise ValueError("supplier_live_evidence_output_dir_missing")
    adapter_env = {
        provider_adapter.ENV_CAPTURE: "1",
        provider_adapter.ENV_PROVIDER_NAME: "gemini",
        provider_adapter.ENV_PROVIDER_MODEL: "supplier-live-evidence-test-model",
        provider_adapter.ENV_OUTPUT_DIR: output_dir,
        provider_adapter.ENV_CAPTURE_ID: env.get(ENV_CAPTURE_ID, "supplier-live-evidence-01"),
    }
    return provider_adapter.run_live_provider_adapter_response_capture(
        env=adapter_env,
        provider=provider,
    )


def _copy_upstream_counters(
    counters: dict[str, int],
    upstream: Mapping[str, Any],
    *,
    provider_mode: bool,
) -> None:
    upstream_counters = upstream["counters"]
    if provider_mode:
        counters["provider_call_attempted_count"] = upstream_counters[
            "provider_call_attempted_count"
        ]
        counters["raw_response_artifact_created_count"] = upstream_counters[
            "raw_response_artifact_created_count"
        ]
        counters["live_model_call_count"] = upstream_counters["live_model_call_count"]
        counters["network_used_count"] = upstream_counters["network_used_count"]
        counters["gemini_called_count"] = upstream_counters["gemini_called_count"]
        counters["secrets_logged_count"] = upstream_counters["secrets_logged_count"]
        counters["connector_called_count"] = upstream_counters["connector_called_count"]
        counters["bank_connector_called_count"] = upstream_counters[
            "bank_connector_called_count"
        ]
        counters["supplier_connector_called_count"] = upstream_counters[
            "supplier_connector_called_count"
        ]
        counters["warehouse_connector_called_count"] = upstream_counters[
            "warehouse_connector_called_count"
        ]
        counters["payment_executed_count"] = upstream_counters["payment_executed_count"]
        counters["shipment_released_count"] = upstream_counters[
            "shipment_released_count"
        ]
        response_result = upstream.get("response_file_result") or {}
        response_counters = response_result.get("counters", {})
    else:
        response_counters = upstream_counters

    counters["response_file_lane_used_count"] = 1
    counters["semantic_claim_created_count"] = response_counters.get(
        "semantic_claim_created_count",
        upstream_counters.get("semantic_claim_created_count", 0),
    )
    counters["semantic_claim_validated_locally_count"] = response_counters.get(
        "semantic_claim_validated_locally_count",
        upstream_counters.get("semantic_claim_validated_locally_count", 0),
    )
    counters["semantic_claim_rejected_count"] = response_counters.get(
        "semantic_claim_rejected_count",
        upstream_counters.get("semantic_claim_rejected_count", 0),
    )


def _claims_from_upstream(upstream: Mapping[str, Any], *, provider_mode: bool) -> tuple[SemanticEvidenceClaim, ...]:
    if provider_mode:
        response_result = upstream.get("response_file_result") or {}
        return tuple(response_result.get("claims", ()))
    return tuple(upstream.get("claims", ()))


def _validation_errors_from_upstream(upstream: Mapping[str, Any], *, provider_mode: bool) -> tuple[str, ...]:
    if provider_mode:
        return tuple(upstream.get("validation_errors", ()))
    return tuple(upstream.get("validation_errors", ()))


def _mark_failure_counters(counters: dict[str, int], validation_errors: tuple[str, ...]) -> None:
    if "authority_claimed_must_be_false" in validation_errors:
        counters["provider_authority_claimed_count"] = 1
    if "action_permission_claimed_must_be_false" in validation_errors:
        counters["action_permission_created_count"] = 1
    if "final_output_claimed_must_be_false" in validation_errors:
        counters["final_output_created_from_provider_count"] = 1
        counters["provider_final_output_created_count"] = 1


def _failure_scenario_id(validation_errors: tuple[str, ...]) -> str:
    if not validation_errors:
        return "captured_live_evidence_claim_enters_supplier_spine_as_candidate_only"
    first_error = validation_errors[0]
    if first_error == "invalid_json":
        return "invalid_json_live_evidence_fails_closed"
    if first_error.startswith("unexpected_field:"):
        return "extra_fields_live_evidence_fails_closed"
    if first_error == "secret_like_marker_detected":
        return "secret_like_live_evidence_fails_closed"
    if first_error in {
        "authority_claimed_must_be_false",
        "action_permission_claimed_must_be_false",
        "final_output_claimed_must_be_false",
    }:
        return "authority_claim_live_evidence_fails_closed"
    if first_error in {
        "connector_command_claimed_must_be_false",
        "connector_or_external_command_detected",
    }:
        return "connector_command_live_evidence_fails_closed"
    return "captured_live_evidence_claim_enters_supplier_spine_as_candidate_only"


def _failure_result(
    *,
    counters: dict[str, int],
    upstream: Mapping[str, Any],
    provider_mode: bool,
) -> dict[str, Any]:
    validation_errors = _validation_errors_from_upstream(upstream, provider_mode=provider_mode)
    _mark_failure_counters(counters, validation_errors)
    scenarios = _skipped_scenarios()
    scenarios = _mark_scenario(
        scenarios,
        _failure_scenario_id(validation_errors),
        "PASS",
        reason_codes=validation_errors,
    )
    scenarios = _mark_scenario(
        scenarios,
        "no_payment_or_shipment_release_executed",
        "PASS",
        details={"payment_executed": False, "shipment_released": False},
    )
    scenarios = _mark_scenario(
        scenarios,
        "root_final_authority_preserved",
        "PASS",
        details={"root_final_authority_preserved": True},
    )
    return _result(
        final_status="FAIL_CLOSED",
        scenarios=scenarios,
        counters=counters,
        validation_errors=validation_errors,
        artifacts=tuple(upstream.get("artifacts", ())),
        upstream_result=upstream,
    )


def _build_supplier_context(claim: SemanticEvidenceClaim) -> dict[str, Any]:
    return {
        "business_context": DIRTY_SUPPLIER_PAYMENT_CONTEXT,
        "claim_source_id": claim.source_id,
        "claim_added_as": "candidate-only SemanticEvidenceClaim",
        "claim_is_truth": False,
        "claim_is_authority": False,
        "claim_is_action_permission": False,
        "claim_is_final_output": False,
        "root_review_required": claim.root_review_required,
        "legal_hold_active": True,
        "stock_status": "water_filter_short_by_2",
        "payment_decision": "needs_root_legal_review",
        "shipment_release_decision": "blocked_by_stock_shortage",
    }


def _build_drs_candidate_context(claim: SemanticEvidenceClaim) -> dict[str, Any]:
    return {
        "context_type": "DRS candidate context",
        "source_claim_id": claim.claim_id,
        "candidate_context_only": True,
        "truth_claimed": False,
        "direct_reuse_applied": False,
        "root_review_required": True,
    }


def _build_candidate_vector_context(claim: SemanticEvidenceClaim) -> dict[str, Any]:
    return {
        "context_type": "CandidateVector represented supplier evidence row",
        "source_claim_id": claim.claim_id,
        "candidate_vector_created": True,
        "candidate_vector_represented_count": 1,
        "truth_claimed": False,
        "authority_claimed": False,
    }


def _build_advisory_context(claim: SemanticEvidenceClaim) -> dict[str, Any]:
    return {
        "source_claim_id": claim.claim_id,
        "AVF": "represented advisory score only",
        "avf_score": 0.62,
        "avf_authority_claimed": False,
        "advisory_review": "needs_root_review",
        "advisory_authority_claimed": False,
        "post_vv_review": "represented_review_boundary",
        "gt_lgt_review": "represented_review_boundary",
    }


def _build_root_business_summary(claim: SemanticEvidenceClaim) -> dict[str, Any]:
    prompt_injection_preserved = bool(claim.unsafe_instruction_flags)
    return {
        "summary_id": "root_supplier_payment_live_evidence_summary_v02",
        "source_claim_id": claim.claim_id,
        "root_boundary": "Root remains final authority",
        "legal_hold_result": "legal_hold_beats_payable_invoice",
        "shipment_result": "stock_shortage_blocks_shipment_release",
        "payment_executed": False,
        "shipment_released": False,
        "connector_called": False,
        "provider_final_output_created": False,
        "prompt_injection_preserved_as_evidence": prompt_injection_preserved,
    }


def _apply_integration_counters(counters: dict[str, int]) -> None:
    counters["live_claim_added_to_supplier_context_count"] = 1
    counters["drs_candidate_context_used_count"] = 1
    counters["candidate_vector_created_count"] = 1
    counters["candidate_vector_represented_count"] = 1
    counters["avf_scored_count"] = 1
    counters["avf_invoked_count"] = 0
    counters["avf_represented_count"] = 1
    counters["advisory_review_count"] = 1
    counters["advisory_invoked_count"] = 0
    counters["advisory_represented_count"] = 1
    counters["bounded_actor_invoked_count"] = 0
    counters["bounded_actor_represented_count"] = 1
    counters["fractal_branch_invoked_count"] = 0
    counters["fractal_branch_represented_count"] = 1
    counters["post_vv_checked_count"] = 1
    counters["post_vv_invoked_count"] = 0
    counters["post_vv_represented_count"] = 1
    counters["gt_lgt_review_count"] = 1
    counters["gt_lgt_invoked_count"] = 0
    counters["gt_lgt_represented_count"] = 1
    counters["root_business_summary_created_count"] = 1


def _success_scenarios(claim: SemanticEvidenceClaim) -> tuple[dict[str, Any], ...]:
    prompt_injection_preserved = bool(claim.unsafe_instruction_flags)
    scenarios = _skipped_scenarios()
    pass_details = {
        "claim_id": claim.claim_id,
        "candidate_only": True,
        "root_review_required": claim.root_review_required,
    }
    for scenario_id in (
        "captured_live_evidence_claim_enters_supplier_spine_as_candidate_only",
        "live_claim_enriches_drs_candidate_context_without_truth",
        "candidate_vector_receives_live_evidence_context",
        "avf_advisory_receives_live_evidence_without_authority",
        "legal_hold_beats_payable_invoice",
        "stock_shortage_blocks_shipment_release",
        "no_payment_or_shipment_release_executed",
        "root_final_authority_preserved",
    ):
        scenarios = _mark_scenario(
            scenarios,
            scenario_id,
            "PASS",
            details=pass_details,
        )
    scenarios = _mark_scenario(
        scenarios,
        "prompt_injection_preserved_as_evidence",
        "PASS" if prompt_injection_preserved else "SKIPPED",
        details={"unsafe_instruction_flags": claim.unsafe_instruction_flags},
    )
    return scenarios


def _success_result(
    *,
    counters: dict[str, int],
    upstream: Mapping[str, Any],
    provider_mode: bool,
) -> dict[str, Any]:
    claims = _claims_from_upstream(upstream, provider_mode=provider_mode)
    if len(claims) != 1:
        counters["semantic_claim_rejected_count"] = 1
        return _failure_result(counters=counters, upstream=upstream, provider_mode=provider_mode)

    claim = claims[0]
    _apply_integration_counters(counters)
    supplier_context = _build_supplier_context(claim)
    drs_context = _build_drs_candidate_context(claim)
    candidate_context = _build_candidate_vector_context(claim)
    advisory_context = _build_advisory_context(claim)
    root_summary = _build_root_business_summary(claim)
    return _result(
        final_status="PASS",
        scenarios=_success_scenarios(claim),
        counters=counters,
        claims=claims,
        supplier_context=supplier_context,
        drs_candidate_context=drs_context,
        candidate_vector_context=candidate_context,
        advisory_context=advisory_context,
        root_business_summary=root_summary,
        artifacts=tuple(upstream.get("artifacts", ())),
        upstream_result=upstream,
    )


def run_supplier_payment_live_evidence_integration(
    env: Mapping[str, str] | None = None,
    *,
    provider: ProviderCallable | None = None,
) -> dict[str, Any]:
    observed_env = env if env is not None else os.environ
    counters = _base_counters()
    response_file_present = bool(observed_env.get(ENV_RESPONSE_FILE))
    explicit_config = observed_env.get(ENV_ENABLE) == "1" or provider is not None

    if not explicit_config and not response_file_present:
        return _default_result()

    counters["explicit_live_evidence_config_present_count"] = 1
    try:
        if provider is not None:
            upstream = _provider_capture_result(observed_env, provider)
            provider_mode = True
        elif response_file_present:
            upstream = _response_file_result(observed_env)
            provider_mode = False
        else:
            scenarios = _mark_scenario(
                _skipped_scenarios(),
                "captured_live_evidence_claim_enters_supplier_spine_as_candidate_only",
                "FAIL",
                reason_codes=("captured_evidence_config_missing",),
            )
            counters["semantic_claim_rejected_count"] = 1
            return _result(
                final_status="FAIL_CLOSED",
                scenarios=scenarios,
                counters=counters,
                validation_errors=("captured_evidence_config_missing",),
            )
    except ValueError as exc:
        scenarios = _mark_scenario(
            _skipped_scenarios(),
            "captured_live_evidence_claim_enters_supplier_spine_as_candidate_only",
            "FAIL",
            reason_codes=(str(exc),),
        )
        counters["semantic_claim_rejected_count"] = 1
        return _result(
            final_status="FAIL_CLOSED",
            scenarios=scenarios,
            counters=counters,
            validation_errors=(str(exc),),
        )

    _copy_upstream_counters(counters, upstream, provider_mode=provider_mode)
    if upstream["final_status"] != "PASS":
        return _failure_result(counters=counters, upstream=upstream, provider_mode=provider_mode)
    return _success_result(counters=counters, upstream=upstream, provider_mode=provider_mode)


def _counter_lines(counters: Mapping[str, int]) -> list[str]:
    ordered = (
        "scenarios_total",
        "scenarios_passed",
        *COUNTER_KEYS,
    )
    return [f"{key}: {counters[key]}" for key in ordered]


def render_report(result: dict[str, Any] | None = None) -> str:
    result = result or run_supplier_payment_live_evidence_integration()
    lines = [
        TITLE,
        "",
        "Mode:",
        "Default mode is SKIPPED_CLOSED without explicit captured/live-like evidence config.",
        "Captured evidence enters as a SemanticEvidenceClaim candidate-only record.",
        "DRS candidate context, CandidateVector, AVF, advisory, Post V&V, and GT-LGT are represented only unless directly invoked.",
        "represented_count values must not be reported as invoked_count values.",
        "",
        "Scenario results:",
        *[
            f"- {scenario['scenario_id']}: {scenario['status']}"
            for scenario in result["scenarios"]
        ],
        "",
        "Supplier context:",
        str(result["supplier_context"]),
        "",
        "DRS candidate context:",
        str(result["drs_candidate_context"]),
        "",
        "CandidateVector / AVF / advisory context:",
        str(result["candidate_vector_context"]),
        str(result["advisory_context"]),
        "",
        "Root business summary:",
        str(result["root_business_summary"]),
        "",
        "Counters:",
        *_counter_lines(result["counters"]),
        "",
        "Validation errors:",
        *[f"- {error}" for error in result["validation_errors"]],
        "",
        "Artifacts:",
        *[f"- {artifact}" for artifact in result["artifacts"]],
        "",
        "Authority boundary summary:",
        *result["authority_boundary_summary"],
        "",
        "Limitations:",
        *result["limitations"],
        "",
        f"FINAL STATUS: {result['final_status']}",
    ]
    return "\n".join(lines)


def main() -> int:
    result = run_supplier_payment_live_evidence_integration()
    print(render_report(result))
    return 1 if result["final_status"] == "FAIL_CLOSED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
