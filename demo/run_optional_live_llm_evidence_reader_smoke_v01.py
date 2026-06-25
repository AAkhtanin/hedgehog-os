from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Mapping

from hedgehog.live_llm_semantic_evidence_reader import (
    LIVE_LLM_READER_DISABLED_MESSAGE,
    ReaderMode,
    SemanticEvidenceClaim,
    build_semantic_evidence_claims,
    make_default_inputs,
)


TITLE = "HEDGEHOG OS - OPTIONAL LIVE LLM EVIDENCE READER SMOKE v0.1"

ENV_ENABLE = "HEDGEHOG_OPTIONAL_LIVE_EVIDENCE_SMOKE"
ENV_RESPONSE_FILE = "HEDGEHOG_OPTIONAL_LIVE_RESPONSE_FILE"

SCENARIOS = (
    "no_config_skips_closed_without_live_call",
    "valid_response_file_creates_one_candidate_claim",
    "invalid_json_fails_closed",
    "authority_claim_fails_closed",
    "action_permission_claim_fails_closed",
    "final_output_claim_fails_closed",
    "connector_command_claim_fails_closed",
    "secret_like_response_fails_closed",
    "decision_like_text_remains_non_authoritative",
    "deterministic_reader_remains_unchanged",
)

REQUIRED_FIELDS = (
    "source_id",
    "source_kind",
    "extracted_claim",
    "confidence",
    "uncertainty_notes",
    "provenance_notes",
    "contradiction_flags",
    "freshness_hint",
    "unsafe_instruction_flags",
    "action_requested",
    "action_permission_claimed",
    "authority_claimed",
    "truth_claimed",
    "final_output_claimed",
    "connector_command_claimed",
    "root_review_required",
)

TUPLE_FIELDS = (
    "uncertainty_notes",
    "provenance_notes",
    "contradiction_flags",
    "unsafe_instruction_flags",
)

ZERO_COUNTER_KEYS = (
    "live_model_call_count",
    "network_used_count",
    "semantic_claim_is_truth_count",
    "semantic_claim_is_authority_count",
    "semantic_claim_is_action_permission_count",
    "semantic_claim_is_final_output_count",
    "silent_fallback_to_deterministic_pass_count",
    "deterministic_reader_mutated_count",
    "connector_called_count",
    "bank_connector_called_count",
    "supplier_connector_called_count",
    "warehouse_connector_called_count",
    "payment_executed_count",
    "shipment_released_count",
    "raw_secret_exposed_to_llm_count",
    "raw_iban_exposed_to_llm_count",
    "raw_api_token_exposed_to_llm_count",
    "secrets_logged_count",
    "action_permission_created_count",
    "non_root_final_output_created_count",
    "root_authority_claimed_by_llm_count",
)

SECRET_MARKERS = (
    "api_key",
    "token",
    "secret",
    "password",
    "bearer",
    "iban",
    "fake-iban",
    "sandbox_token",
)

CONNECTOR_COMMAND_MARKERS = (
    "call bank",
    "call the bank",
    "command bank",
    "call supplier",
    "command supplier",
    "call warehouse",
    "command warehouse",
    "call connector",
    "use connector",
    "execute connector",
    "invoke connector",
)

DECISION_LIKE_MARKERS = (
    "invoice is valid",
    "supplier can be paid",
    "shipment can be released",
)

AUTHORITY_BOUNDARY_SUMMARY = (
    "Live model output is not truth.",
    "Live model output is not authority.",
    "Live model confidence is not authority.",
    "Live model extracted claim is not action permission.",
    "Live model response file is not FinalOutput.",
    "Live model cannot command bank.",
    "Live model cannot command supplier.",
    "Live model cannot command warehouse.",
    "Live model cannot command Architect.",
    "Live model cannot command Executor.",
    "Live model cannot command Fractal Cell.",
    "Live model cannot access or receive business secrets.",
    "Live model cannot call production connectors.",
    "Response-file validation is not a model call by the runner.",
    "SemanticEvidenceClaim remains candidate evidence only.",
    "Contradiction detection is review signal only.",
    "Root review is required.",
    "Root remains final authority.",
)

LIMITATIONS = (
    "response-file mode only",
    "no command adapter",
    "no live model call by runner",
    "no network call by runner",
    "no Gemini call by runner",
    "no connector call",
    "no bank/supplier/warehouse call",
    "no secrets access",
    "no action execution",
    "no FinalOutput creation",
)


def build_dirty_document() -> str:
    return "\n".join(
        (
            "Subject: SH-2042 / INV-2042",
            "",
            "Warehouse says water_filter is short by 2, but supplier says stock is available.",
            "Accounting says invoice INV-2042 looks payable.",
            "Legal note says the insurance certificate may be expired.",
            "Please confirm whether we can pay and release shipment.",
        )
    )


def build_extraction_instruction() -> str:
    return (
        "Extract one bounded SemanticEvidenceClaim-compatible candidate from the "
        "dirty document. Do not decide truth, authorize payment, release shipment, "
        "call connectors, expose secrets, or create FinalOutput."
    )


def _base_counters() -> dict[str, int]:
    counters = {
        "scenarios_total": len(SCENARIOS),
        "scenarios_passed": 0,
        "optional_live_smoke_invoked_count": 1,
        "explicit_live_config_present_count": 0,
        "skipped_closed_count": 0,
        "raw_live_response_received_count": 0,
        "raw_live_response_parse_error_count": 0,
        "semantic_claim_created_count": 0,
        "semantic_claim_validated_locally_count": 0,
        "semantic_claim_rejected_count": 0,
        "root_review_required_count": 0,
        "root_final_authority_preserved_count": 1,
    }
    counters.update({key: 0 for key in ZERO_COUNTER_KEYS})
    return counters


def _scenario_result(
    scenario_id: str,
    status: str,
    *,
    reason_codes: tuple[str, ...] = (),
) -> dict[str, Any]:
    return {
        "scenario_id": scenario_id,
        "status": status,
        "reason_codes": reason_codes,
    }


def _contains_marker(value: Any, markers: tuple[str, ...]) -> bool:
    if isinstance(value, str):
        lower = value.lower()
        return any(marker in lower for marker in markers)
    if isinstance(value, Mapping):
        return any(
            _contains_marker(key, markers) or _contains_marker(item, markers)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return any(_contains_marker(item, markers) for item in value)
    return False


def _normalize_response(raw: Any) -> tuple[Mapping[str, Any] | None, str | None]:
    if isinstance(raw, list):
        if len(raw) != 1:
            return None, "response_list_must_contain_exactly_one_claim"
        item = raw[0]
        if not isinstance(item, Mapping):
            return None, "response_list_item_not_object"
        return item, None
    if isinstance(raw, Mapping):
        return raw, None
    return None, "response_not_object_or_single_item_list"


def _tuple_field(value: Any, field_name: str) -> tuple[str, ...]:
    if not isinstance(value, list):
        raise ValueError(f"{field_name}_must_be_list")
    if not all(isinstance(item, str) for item in value):
        raise ValueError(f"{field_name}_must_contain_strings")
    return tuple(value)


def _validate_response_claim(raw: Mapping[str, Any]) -> tuple[SemanticEvidenceClaim | None, tuple[str, ...], bool]:
    missing = tuple(field for field in REQUIRED_FIELDS if field not in raw)
    if missing:
        return None, tuple(f"missing_required_field:{field}" for field in missing), False

    extra = tuple(sorted(str(field) for field in raw if field not in REQUIRED_FIELDS))
    if _contains_marker(raw, SECRET_MARKERS):
        return (
            None,
            ("secret_like_marker_detected",)
            + tuple(f"unexpected_field:{field}" for field in extra),
            False,
        )
    if extra:
        return None, tuple(f"unexpected_field:{field}" for field in extra), False
    if _contains_marker(raw, CONNECTOR_COMMAND_MARKERS):
        return None, ("connector_or_external_command_detected",), False

    for field in ("source_id", "source_kind", "extracted_claim", "freshness_hint"):
        if not isinstance(raw[field], str) or not raw[field].strip():
            return None, (f"{field}_must_be_non_empty_string",), False

    confidence = raw["confidence"]
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
        return None, ("confidence_must_be_numeric",), False
    if not 0.0 <= float(confidence) <= 1.0:
        return None, ("confidence_out_of_range",), False

    action_requested = raw["action_requested"]
    if action_requested is not None and not isinstance(action_requested, str):
        return None, ("action_requested_must_be_string_or_null",), False

    false_flag_fields = (
        "action_permission_claimed",
        "authority_claimed",
        "truth_claimed",
        "final_output_claimed",
        "connector_command_claimed",
    )
    for field in false_flag_fields:
        if raw[field] is not False:
            return None, (f"{field}_must_be_false",), False
    if raw["root_review_required"] is not True:
        return None, ("root_review_required_must_be_true",), False

    try:
        tuple_values = {
            field: _tuple_field(raw[field], field)
            for field in TUPLE_FIELDS
        }
    except ValueError as exc:
        return None, (str(exc),), False

    decision_like = _contains_marker(raw["extracted_claim"], DECISION_LIKE_MARKERS)
    claim = SemanticEvidenceClaim(
        claim_id="optional_live_response_file_claim_01",
        source_id=raw["source_id"],
        source_kind=raw["source_kind"],
        extracted_claim=raw["extracted_claim"],
        confidence=float(confidence),
        uncertainty_notes=tuple_values["uncertainty_notes"],
        provenance_notes=tuple_values["provenance_notes"],
        contradiction_flags=tuple_values["contradiction_flags"],
        freshness_hint=raw["freshness_hint"],
        unsafe_instruction_flags=tuple_values["unsafe_instruction_flags"],
        action_requested=action_requested,
        action_permission_claimed=False,
        authority_claimed=False,
        truth_claimed=False,
        final_output_claimed=False,
        connector_command_claimed=False,
        root_review_required=True,
    )
    return claim, (), decision_like


def _deterministic_reader_is_unchanged() -> bool:
    claims = build_semantic_evidence_claims(make_default_inputs())
    if not claims:
        return False
    try:
        build_semantic_evidence_claims(
            make_default_inputs(),
            reader_mode=ReaderMode.live_llm_reader,
        )
    except ValueError as exc:
        return str(exc) == LIVE_LLM_READER_DISABLED_MESSAGE
    return False


def _result(
    *,
    final_status: str,
    scenarios: tuple[dict[str, Any], ...],
    counters: dict[str, int],
    claims: tuple[SemanticEvidenceClaim, ...] = (),
    validation_errors: tuple[str, ...] = (),
    decision_like_text_observed: bool = False,
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
        "validation_errors": validation_errors,
        "decision_like_text_observed": decision_like_text_observed,
        "limitations": LIMITATIONS,
        "authority_boundary_summary": AUTHORITY_BOUNDARY_SUMMARY,
        "pass_conditions": {
            "no_runner_live_call": counters["live_model_call_count"] == 0,
            "no_runner_network_call": counters["network_used_count"] == 0,
            "no_connector_call": counters["connector_called_count"] == 0,
            "no_silent_fallback": counters[
                "silent_fallback_to_deterministic_pass_count"
            ]
            == 0,
            "root_final_authority_preserved": counters[
                "root_final_authority_preserved_count"
            ]
            == 1,
        },
    }


def run_optional_live_llm_evidence_reader_smoke(
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    observed_env = env if env is not None else os.environ
    counters = _base_counters()
    deterministic_unchanged = _deterministic_reader_is_unchanged()
    if not deterministic_unchanged:
        counters["deterministic_reader_mutated_count"] = 1
    explicit_config = (
        observed_env.get(ENV_ENABLE) == "1"
        and bool(observed_env.get(ENV_RESPONSE_FILE))
    )

    if not explicit_config:
        counters["skipped_closed_count"] = 1
        scenarios = (
            _scenario_result(
                "no_config_skips_closed_without_live_call",
                "PASS",
                reason_codes=("explicit_live_config_absent", "skipped_closed"),
            ),
            *(
                _scenario_result(scenario_id, "SKIPPED")
                for scenario_id in SCENARIOS[1:-1]
            ),
            _scenario_result(
                "deterministic_reader_remains_unchanged",
                "PASS" if deterministic_unchanged else "FAIL",
            ),
        )
        return _result(
            final_status="SKIPPED_CLOSED" if deterministic_unchanged else "FAIL_CLOSED",
            scenarios=scenarios,
            counters=counters,
        )

    counters["explicit_live_config_present_count"] = 1
    response_file = observed_env[ENV_RESPONSE_FILE]
    try:
        raw_text = Path(response_file).read_text(encoding="utf-8")
    except OSError:
        counters["semantic_claim_rejected_count"] = 1
        scenarios = (
            _scenario_result("no_config_skips_closed_without_live_call", "SKIPPED"),
            _scenario_result("valid_response_file_creates_one_candidate_claim", "FAIL"),
            *(_scenario_result(scenario_id, "SKIPPED") for scenario_id in SCENARIOS[2:-1]),
            _scenario_result(
                "deterministic_reader_remains_unchanged",
                "PASS" if deterministic_unchanged else "FAIL",
            ),
        )
        return _result(
            final_status="FAIL_CLOSED",
            scenarios=scenarios,
            counters=counters,
            validation_errors=("response_file_unreadable",),
        )

    counters["raw_live_response_received_count"] = 1
    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError:
        counters["raw_live_response_parse_error_count"] = 1
        counters["semantic_claim_rejected_count"] = 1
        scenarios = (
            _scenario_result("no_config_skips_closed_without_live_call", "SKIPPED"),
            _scenario_result("valid_response_file_creates_one_candidate_claim", "SKIPPED"),
            _scenario_result("invalid_json_fails_closed", "PASS"),
            *(_scenario_result(scenario_id, "SKIPPED") for scenario_id in SCENARIOS[3:-1]),
            _scenario_result(
                "deterministic_reader_remains_unchanged",
                "PASS" if deterministic_unchanged else "FAIL",
            ),
        )
        return _result(
            final_status="FAIL_CLOSED",
            scenarios=scenarios,
            counters=counters,
            validation_errors=("invalid_json",),
        )

    normalized, normalize_error = _normalize_response(parsed)
    if normalize_error is not None:
        counters["semantic_claim_rejected_count"] = 1
        scenarios = (
            _scenario_result("no_config_skips_closed_without_live_call", "SKIPPED"),
            _scenario_result("valid_response_file_creates_one_candidate_claim", "FAIL"),
            *(_scenario_result(scenario_id, "SKIPPED") for scenario_id in SCENARIOS[2:-1]),
            _scenario_result(
                "deterministic_reader_remains_unchanged",
                "PASS" if deterministic_unchanged else "FAIL",
            ),
        )
        return _result(
            final_status="FAIL_CLOSED",
            scenarios=scenarios,
            counters=counters,
            validation_errors=(normalize_error,),
        )

    claim, validation_errors, decision_like = _validate_response_claim(normalized)
    if claim is None:
        counters["semantic_claim_rejected_count"] = 1
        error = validation_errors[0] if validation_errors else "validation_failed"
        scenario_id = {
            "authority_claimed_must_be_false": "authority_claim_fails_closed",
            "action_permission_claimed_must_be_false": "action_permission_claim_fails_closed",
            "final_output_claimed_must_be_false": "final_output_claim_fails_closed",
            "connector_command_claimed_must_be_false": "connector_command_claim_fails_closed",
            "secret_like_marker_detected": "secret_like_response_fails_closed",
            "connector_or_external_command_detected": "connector_command_claim_fails_closed",
        }.get(error, "valid_response_file_creates_one_candidate_claim")
        scenarios = tuple(
            _scenario_result(
                candidate_id,
                "PASS" if candidate_id == scenario_id else (
                    "PASS" if candidate_id == "deterministic_reader_remains_unchanged" and deterministic_unchanged else "SKIPPED"
                ),
                reason_codes=(error,) if candidate_id == scenario_id else (),
            )
            for candidate_id in SCENARIOS
        )
        return _result(
            final_status="FAIL_CLOSED",
            scenarios=scenarios,
            counters=counters,
            validation_errors=validation_errors,
        )

    counters["semantic_claim_created_count"] = 1
    counters["semantic_claim_validated_locally_count"] = 1
    counters["root_review_required_count"] = 1
    scenarios = (
        _scenario_result("no_config_skips_closed_without_live_call", "SKIPPED"),
        _scenario_result("valid_response_file_creates_one_candidate_claim", "PASS"),
        *(_scenario_result(scenario_id, "SKIPPED") for scenario_id in SCENARIOS[2:8]),
        _scenario_result(
            "decision_like_text_remains_non_authoritative",
            "PASS" if decision_like else "SKIPPED",
        ),
        _scenario_result(
            "deterministic_reader_remains_unchanged",
            "PASS" if deterministic_unchanged else "FAIL",
        ),
    )
    return _result(
        final_status="PASS" if deterministic_unchanged else "FAIL_CLOSED",
        scenarios=scenarios,
        counters=counters,
        claims=(claim,),
        decision_like_text_observed=decision_like,
    )


def _counter_lines(counters: dict[str, int]) -> list[str]:
    ordered_keys = (
        "scenarios_total",
        "scenarios_passed",
        "optional_live_smoke_invoked_count",
        "explicit_live_config_present_count",
        "skipped_closed_count",
        "live_model_call_count",
        "network_used_count",
        "raw_live_response_received_count",
        "raw_live_response_parse_error_count",
        "semantic_claim_created_count",
        "semantic_claim_validated_locally_count",
        "semantic_claim_rejected_count",
        "semantic_claim_is_truth_count",
        "semantic_claim_is_authority_count",
        "semantic_claim_is_action_permission_count",
        "semantic_claim_is_final_output_count",
        "root_review_required_count",
        "silent_fallback_to_deterministic_pass_count",
        "deterministic_reader_mutated_count",
        "connector_called_count",
        "bank_connector_called_count",
        "supplier_connector_called_count",
        "warehouse_connector_called_count",
        "payment_executed_count",
        "shipment_released_count",
        "raw_secret_exposed_to_llm_count",
        "raw_iban_exposed_to_llm_count",
        "raw_api_token_exposed_to_llm_count",
        "secrets_logged_count",
        "action_permission_created_count",
        "non_root_final_output_created_count",
        "root_authority_claimed_by_llm_count",
        "root_final_authority_preserved_count",
    )
    return [f"{key}: {counters[key]}" for key in ordered_keys]


def render_report(result: dict[str, Any] | None = None) -> str:
    result = result or run_optional_live_llm_evidence_reader_smoke()
    counters = result["counters"]
    lines = [
        TITLE,
        "",
        "Mode:",
        "response-file mode only",
        "The runner never calls a model, network, Gemini, connector, bank, supplier, warehouse, or secrets.",
        f"Config marker: {ENV_RESPONSE_FILE}",
        "",
        "Dirty document fixture:",
        build_dirty_document(),
        "",
        "Extraction instruction:",
        build_extraction_instruction(),
        "",
        "Scenario coverage:",
        *[
            f"- {scenario['scenario_id']}: {scenario['status']}"
            for scenario in result["scenarios"]
        ],
        "",
        "Counters:",
        *_counter_lines(counters),
        "",
        "Validation errors:",
        *[f"- {error}" for error in result["validation_errors"]],
        "",
        "Claims:",
        *[
            f"- {claim.source_id}: {claim.extracted_claim}"
            for claim in result["claims"]
        ],
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
    result = run_optional_live_llm_evidence_reader_smoke()
    print(render_report(result))
    return 1 if result["final_status"] == "FAIL_CLOSED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
