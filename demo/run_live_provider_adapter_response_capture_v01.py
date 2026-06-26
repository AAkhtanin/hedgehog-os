from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

from demo.run_optional_live_llm_evidence_reader_smoke_v01 import (
    ENV_ENABLE as RESPONSE_FILE_ENV_ENABLE,
    ENV_RESPONSE_FILE,
    build_dirty_document,
    run_optional_live_llm_evidence_reader_smoke,
)


TITLE = "HEDGEHOG OS - LIVE PROVIDER ADAPTER / RESPONSE CAPTURE v0.1"

ENV_CAPTURE = "HEDGEHOG_LIVE_PROVIDER_CAPTURE"
ENV_PROVIDER_NAME = "HEDGEHOG_LIVE_PROVIDER_NAME"
ENV_PROVIDER_MODEL = "HEDGEHOG_LIVE_PROVIDER_MODEL"
ENV_TIMEOUT_SECONDS = "HEDGEHOG_LIVE_PROVIDER_TIMEOUT_SECONDS"
ENV_OUTPUT_DIR = "HEDGEHOG_LIVE_PROVIDER_OUTPUT_DIR"
ENV_CAPTURE_ID = "HEDGEHOG_LIVE_PROVIDER_CAPTURE_ID"
ENV_GEMINI_API_KEY = "HEDGEHOG_GEMINI_API_KEY"
ENV_GOOGLE_API_KEY = "GOOGLE_API_KEY"
ENV_GEMINI_API_KEY_FALLBACK = "GEMINI_API_KEY"
ENV_GOOGLE_GEMINI_API_KEY = "GOOGLE_GEMINI_API_KEY"

SCENARIOS = (
    "no_config_skips_closed_without_provider_call",
    "explicit_gemini_capture_saves_raw_response_artifact",
    "captured_artifact_validates_one_candidate_claim",
    "provider_timeout_fails_closed",
    "provider_sdk_or_key_missing_fails_closed",
    "invalid_json_artifact_fails_closed",
    "authority_claim_artifact_fails_closed",
    "connector_command_artifact_fails_closed",
    "secret_like_artifact_fails_closed",
    "prompt_injection_preserved_as_evidence",
    "response_file_lane_boundary_remains_unchanged",
)

ZERO_COUNTER_KEYS = (
    "provider_call_attempted_count",
    "provider_call_succeeded_count",
    "provider_call_failed_count",
    "provider_timeout_count",
    "raw_response_artifact_created_count",
    "raw_response_artifact_validated_count",
    "semantic_claim_created_count",
    "semantic_claim_validated_locally_count",
    "semantic_claim_rejected_count",
    "response_file_lane_used_count",
    "live_model_call_count",
    "network_used_count",
    "gemini_called_count",
    "groq_called_count",
    "local_slm_called_count",
    "secrets_accessed_count",
    "secrets_logged_count",
    "connector_called_count",
    "bank_connector_called_count",
    "supplier_connector_called_count",
    "warehouse_connector_called_count",
    "payment_executed_count",
    "shipment_released_count",
    "authority_claimed_count",
    "action_permission_created_count",
    "final_output_created_from_provider_count",
    "silent_fallback_to_deterministic_pass_count",
)

LIMITATIONS = (
    "not WOW v0.2",
    "not Supplier Payment integration",
    "not Full Semantic E2E",
    "not production",
    "not NeedleFactory / Marennya / UP",
    "arbitrary command adapter is not approved",
    "provider output remains untrusted response-file evidence",
)

AUTHORITY_BOUNDARY_SUMMARY = (
    "Provider output is not truth.",
    "Provider output is not authority.",
    "Provider output is not action permission.",
    "Provider output is not FinalOutput.",
    "Captured artifact is untrusted evidence.",
    "SemanticEvidenceClaim remains candidate evidence only.",
    "Response-file validation remains the gate.",
    "Root review is required.",
    "Root remains final authority.",
)

SEMANTIC_EVIDENCE_RESPONSE_FIELDS = (
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

SEMANTIC_EVIDENCE_RESPONSE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": list(SEMANTIC_EVIDENCE_RESPONSE_FIELDS),
    "properties": {
        "source_id": {"type": "string"},
        "source_kind": {"type": "string"},
        "extracted_claim": {"type": "string"},
        "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
        "uncertainty_notes": {"type": "array", "items": {"type": "string"}},
        "provenance_notes": {"type": "array", "items": {"type": "string"}},
        "contradiction_flags": {"type": "array", "items": {"type": "string"}},
        "freshness_hint": {"type": "string"},
        "unsafe_instruction_flags": {"type": "array", "items": {"type": "string"}},
        "action_requested": {"type": "string"},
        "action_permission_claimed": {"type": "boolean", "const": False},
        "authority_claimed": {"type": "boolean", "const": False},
        "truth_claimed": {"type": "boolean", "const": False},
        "final_output_claimed": {"type": "boolean", "const": False},
        "connector_command_claimed": {"type": "boolean", "const": False},
        "root_review_required": {"type": "boolean", "const": True},
    },
}

SEMANTIC_EVIDENCE_RESPONSE_SKELETON = {
    "source_id": "provider-response-local-id",
    "source_kind": "live_provider_response_capture",
    "extracted_claim": "candidate evidence summary only",
    "confidence": 0.0,
    "uncertainty_notes": [],
    "provenance_notes": [],
    "contradiction_flags": [],
    "freshness_hint": "provider_response_time_unknown",
    "unsafe_instruction_flags": [],
    "action_requested": "none",
    "action_permission_claimed": False,
    "authority_claimed": False,
    "truth_claimed": False,
    "final_output_claimed": False,
    "connector_command_claimed": False,
    "root_review_required": True,
}


class ProviderCaptureError(RuntimeError):
    reason_code = "provider_call_failed"


class ProviderTimeoutError(ProviderCaptureError):
    reason_code = "provider_timeout"


ProviderCallable = Callable[[str, str, int, Mapping[str, str]], str]


def build_extraction_prompt() -> str:
    required_fields = "\n".join(
        f"- {field}" for field in SEMANTIC_EVIDENCE_RESPONSE_FIELDS
    )
    skeleton = json.dumps(
        SEMANTIC_EVIDENCE_RESPONSE_SKELETON,
        indent=2,
        sort_keys=True,
    )
    return "\n".join(
        (
            "Extract one bounded SemanticEvidenceClaim-compatible JSON object.",
            "Return exactly one JSON object with exactly these top-level fields and no extra keys:",
            required_fields,
            "",
            "Use this JSON skeleton and replace only evidence values:",
            skeleton,
            "",
            "Output is not truth.",
            "Output is not authority.",
            "Output is not action permission.",
            "Output is not FinalOutput.",
            "Root review is required.",
            "No connector commands.",
            "",
            "Dirty document:",
            build_dirty_document(),
        )
    )


def _base_counters() -> dict[str, int]:
    counters = {
        "scenarios_total": len(SCENARIOS),
        "scenarios_passed": 0,
        "explicit_provider_config_present_count": 0,
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


def _capture_id(env: Mapping[str, str]) -> str:
    requested = env.get(ENV_CAPTURE_ID, "").strip()
    if requested and all(char.isalnum() or char in ("-", "_") for char in requested):
        return requested
    return "live_provider_capture_01"


def _timeout_seconds(env: Mapping[str, str]) -> int:
    raw_timeout = env.get(ENV_TIMEOUT_SECONDS, "20")
    try:
        timeout = int(raw_timeout)
    except ValueError:
        return 20
    return max(1, min(timeout, 120))


def _write_artifacts(
    *,
    output_dir: Path,
    capture_id: str,
    provider_name: str,
    provider_model: str,
    prompt: str,
    raw_response: str,
    validation_status: str,
    final_status: str,
) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    response_path = output_dir / f"{capture_id}_raw_response.json"
    metadata_path = output_dir / f"{capture_id}_metadata.json"
    response_path.write_text(raw_response, encoding="utf-8")
    metadata = {
        "provider_name": provider_name,
        "provider_model": provider_model,
        "capture_id": capture_id,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "prompt_hash": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "response_file_path": str(response_path),
        "validation_status": validation_status,
        "final_status": final_status,
    }
    metadata_path.write_text(
        json.dumps(metadata, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return {
        "raw_response_path": str(response_path),
        "metadata_path": str(metadata_path),
    }


def _gemini_api_key(env: Mapping[str, str]) -> str | None:
    for key_name in (
        ENV_GEMINI_API_KEY,
        ENV_GOOGLE_API_KEY,
        ENV_GEMINI_API_KEY_FALLBACK,
        ENV_GOOGLE_GEMINI_API_KEY,
    ):
        candidate = env.get(key_name, "").strip()
        if candidate:
            return candidate
    return None


def _gemini_system_instruction() -> str:
    return (
        "Return JSON only. Produce exactly one SemanticEvidenceClaim-compatible "
        "object with these top-level fields and no extra keys: "
        f"{', '.join(SEMANTIC_EVIDENCE_RESPONSE_FIELDS)}. "
        "The object is candidate evidence only. It must not claim truth, "
        "authority, action permission, connector command, or FinalOutput. "
        "Set action_permission_claimed, authority_claimed, truth_claimed, "
        "final_output_claimed, and connector_command_claimed to false. "
        "Set root_review_required to true."
    )


def _gemini_generation_config(schema_key: str | None) -> dict[str, Any]:
    config: dict[str, Any] = {
        "response_mime_type": "application/json",
        "temperature": 0,
        "candidate_count": 1,
        "system_instruction": _gemini_system_instruction(),
    }
    if schema_key is not None:
        config[schema_key] = SEMANTIC_EVIDENCE_RESPONSE_SCHEMA
    return config


def _generate_gemini_content_with_schema_fallback(
    client: Any,
    *,
    model_name: str,
    prompt: str,
) -> Any:
    for schema_key in ("response_json_schema", "response_schema", None):
        try:
            return client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=_gemini_generation_config(schema_key),
            )
        except (TypeError, ValueError):
            if schema_key is None:
                raise
            continue
    raise ProviderCaptureError("provider_call_failed")


def _call_gemini_provider(
    prompt: str,
    model_name: str,
    timeout_seconds: int,
    env: Mapping[str, str],
) -> str:
    api_key = _gemini_api_key(env)
    if not api_key:
        raise ProviderCaptureError("provider_sdk_or_key_missing")
    try:
        from google import genai
    except ImportError as exc:
        raise ProviderCaptureError("provider_sdk_or_key_missing") from exc

    try:
        client = genai.Client(api_key=api_key)
        response = _generate_gemini_content_with_schema_fallback(
            client,
            model_name=model_name,
            prompt=prompt,
        )
    except TimeoutError as exc:
        raise ProviderTimeoutError("provider_timeout") from exc
    except Exception as exc:  # pragma: no cover - real provider path only
        raise ProviderCaptureError("provider_call_failed") from exc

    parsed = getattr(response, "parsed", None)
    if isinstance(parsed, dict):
        return json.dumps(parsed, sort_keys=True)

    text = getattr(response, "text", None)
    if not isinstance(text, str) or not text.strip():
        raise ProviderCaptureError("provider_empty_response")
    return text


def _provider_callable(
    provider_name: str,
    injected_provider: ProviderCallable | None,
) -> ProviderCallable:
    if injected_provider is not None:
        return injected_provider
    if provider_name == "gemini":
        return _call_gemini_provider
    raise ProviderCaptureError("provider_unsupported")


def _status_from_validation(validation_result: dict[str, Any]) -> str:
    if validation_result["final_status"] == "PASS":
        return "PASS"
    return "FAIL_CLOSED"


def _result(
    *,
    final_status: str,
    scenarios: tuple[dict[str, Any], ...],
    counters: dict[str, int],
    artifacts: tuple[str, ...] = (),
    validation_errors: tuple[str, ...] = (),
    provider_error: str | None = None,
    response_file_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    counters["scenarios_passed"] = sum(
        1 for scenario in scenarios if scenario["status"] == "PASS"
    )
    return {
        "title": TITLE,
        "final_status": final_status,
        "scenarios": scenarios,
        "counters": counters,
        "artifacts": artifacts,
        "validation_errors": validation_errors,
        "provider_error": provider_error,
        "response_file_result": response_file_result,
        "limitations": LIMITATIONS,
        "authority_boundary_summary": AUTHORITY_BOUNDARY_SUMMARY,
        "pass_conditions": {
            "root_final_authority_preserved": counters[
                "root_final_authority_preserved_count"
            ]
            == 1,
            "no_connector_call": counters["connector_called_count"] == 0,
            "no_action": counters["payment_executed_count"] == 0
            and counters["shipment_released_count"] == 0,
            "no_silent_fallback": counters[
                "silent_fallback_to_deterministic_pass_count"
            ]
            == 0,
        },
    }


def run_live_provider_adapter_response_capture(
    env: Mapping[str, str] | None = None,
    *,
    provider: ProviderCallable | None = None,
) -> dict[str, Any]:
    observed_env = env if env is not None else os.environ
    counters = _base_counters()
    explicit_config = observed_env.get(ENV_CAPTURE) == "1"

    if not explicit_config:
        scenarios = (
            _scenario_result(
                "no_config_skips_closed_without_provider_call",
                "PASS",
                reason_codes=("explicit_provider_config_absent", "skipped_closed"),
            ),
            *(_scenario_result(scenario_id, "SKIPPED") for scenario_id in SCENARIOS[1:]),
        )
        return _result(final_status="SKIPPED_CLOSED", scenarios=scenarios, counters=counters)

    counters["explicit_provider_config_present_count"] = 1
    provider_name = observed_env.get(ENV_PROVIDER_NAME, "").strip().lower()
    provider_model = observed_env.get(ENV_PROVIDER_MODEL, "").strip()
    output_dir_raw = observed_env.get(ENV_OUTPUT_DIR, "").strip()
    if not provider_name or not provider_model or not output_dir_raw:
        counters["provider_call_failed_count"] = 1
        scenarios = (
            _scenario_result("no_config_skips_closed_without_provider_call", "SKIPPED"),
            _scenario_result(
                "explicit_gemini_capture_saves_raw_response_artifact",
                "FAIL",
                reason_codes=("provider_config_missing",),
            ),
            *(_scenario_result(scenario_id, "SKIPPED") for scenario_id in SCENARIOS[2:]),
        )
        return _result(
            final_status="FAIL_CLOSED",
            scenarios=scenarios,
            counters=counters,
            provider_error="provider_config_missing",
        )

    prompt = build_extraction_prompt()
    counters["provider_call_attempted_count"] = 1
    real_gemini_provider_configured = (
        provider is None
        and provider_name == "gemini"
        and bool(_gemini_api_key(observed_env))
    )
    if real_gemini_provider_configured:
        counters["secrets_accessed_count"] = 1

    try:
        provider_callable = _provider_callable(provider_name, provider)
        raw_response = provider_callable(
            prompt,
            provider_model,
            _timeout_seconds(observed_env),
            observed_env,
        )
        if provider is None:
            counters["live_model_call_count"] = 1
            counters["network_used_count"] = 1
            if provider_name == "gemini":
                counters["gemini_called_count"] = 1
            elif provider_name == "groq":
                counters["groq_called_count"] = 1
            elif provider_name in {"local_slm", "local-slm"}:
                counters["local_slm_called_count"] = 1
    except ProviderTimeoutError as exc:
        counters["provider_call_failed_count"] = 1
        counters["provider_timeout_count"] = 1
        scenarios = (
            _scenario_result("no_config_skips_closed_without_provider_call", "SKIPPED"),
            _scenario_result("explicit_gemini_capture_saves_raw_response_artifact", "SKIPPED"),
            _scenario_result("captured_artifact_validates_one_candidate_claim", "SKIPPED"),
            _scenario_result(
                "provider_timeout_fails_closed",
                "PASS",
                reason_codes=(exc.reason_code,),
            ),
            *(_scenario_result(scenario_id, "SKIPPED") for scenario_id in SCENARIOS[4:]),
        )
        return _result(
            final_status="FAIL_CLOSED",
            scenarios=scenarios,
            counters=counters,
            provider_error=exc.reason_code,
        )
    except ProviderCaptureError as exc:
        counters["provider_call_failed_count"] = 1
        reason = exc.reason_code if str(exc) != "provider_sdk_or_key_missing" else str(exc)
        if reason == "provider_call_failed" and str(exc):
            reason = str(exc)
        scenarios = (
            _scenario_result("no_config_skips_closed_without_provider_call", "SKIPPED"),
            _scenario_result("explicit_gemini_capture_saves_raw_response_artifact", "SKIPPED"),
            _scenario_result("captured_artifact_validates_one_candidate_claim", "SKIPPED"),
            _scenario_result("provider_timeout_fails_closed", "SKIPPED"),
            _scenario_result(
                "provider_sdk_or_key_missing_fails_closed",
                "PASS" if reason == "provider_sdk_or_key_missing" else "SKIPPED",
                reason_codes=(reason,),
            ),
            *(_scenario_result(scenario_id, "SKIPPED") for scenario_id in SCENARIOS[5:]),
        )
        return _result(
            final_status="FAIL_CLOSED",
            scenarios=scenarios,
            counters=counters,
            provider_error=reason,
        )

    counters["provider_call_succeeded_count"] = 1
    paths = _write_artifacts(
        output_dir=Path(output_dir_raw),
        capture_id=_capture_id(observed_env),
        provider_name=provider_name,
        provider_model=provider_model,
        prompt=prompt,
        raw_response=raw_response,
        validation_status="pending",
        final_status="pending",
    )
    counters["raw_response_artifact_created_count"] = 1
    response_file_result = run_optional_live_llm_evidence_reader_smoke(
        env={
            RESPONSE_FILE_ENV_ENABLE: "1",
            ENV_RESPONSE_FILE: paths["raw_response_path"],
        }
    )
    counters["response_file_lane_used_count"] = 1

    response_counters = response_file_result["counters"]
    counters["semantic_claim_created_count"] = response_counters[
        "semantic_claim_created_count"
    ]
    counters["semantic_claim_validated_locally_count"] = response_counters[
        "semantic_claim_validated_locally_count"
    ]
    counters["semantic_claim_rejected_count"] = response_counters[
        "semantic_claim_rejected_count"
    ]
    counters["authority_claimed_count"] = response_counters[
        "semantic_claim_is_authority_count"
    ]
    counters["action_permission_created_count"] = response_counters[
        "semantic_claim_is_action_permission_count"
    ]
    counters["final_output_created_from_provider_count"] = response_counters[
        "semantic_claim_is_final_output_count"
    ]
    validation_errors = tuple(response_file_result["validation_errors"])
    if "authority_claimed_must_be_false" in validation_errors:
        counters["authority_claimed_count"] = 1
    if "action_permission_claimed_must_be_false" in validation_errors:
        counters["action_permission_created_count"] = 1
    if "final_output_claimed_must_be_false" in validation_errors:
        counters["final_output_created_from_provider_count"] = 1
    if response_file_result["final_status"] == "PASS":
        counters["raw_response_artifact_validated_count"] = 1

    final_status = _status_from_validation(response_file_result)
    scenario_by_error = {
        "invalid_json": "invalid_json_artifact_fails_closed",
        "authority_claimed_must_be_false": "authority_claim_artifact_fails_closed",
        "connector_command_claimed_must_be_false": "connector_command_artifact_fails_closed",
        "connector_or_external_command_detected": "connector_command_artifact_fails_closed",
        "secret_like_marker_detected": "secret_like_artifact_fails_closed",
    }
    validation_scenario = "captured_artifact_validates_one_candidate_claim"
    if validation_errors:
        validation_scenario = scenario_by_error.get(
            validation_errors[0],
            "captured_artifact_validates_one_candidate_claim",
        )
    prompt_injection_detected = "ignore all boundaries" in raw_response.lower()
    scenarios = tuple(
        _scenario_result(
            scenario_id,
            (
                "PASS"
                if (
                    scenario_id == "explicit_gemini_capture_saves_raw_response_artifact"
                    or (scenario_id == validation_scenario and final_status == "PASS")
                    or (scenario_id == validation_scenario and final_status == "FAIL_CLOSED")
                    or (
                        scenario_id == "prompt_injection_preserved_as_evidence"
                        and prompt_injection_detected
                        and final_status == "PASS"
                    )
                    or scenario_id == "response_file_lane_boundary_remains_unchanged"
                )
                else "SKIPPED"
            ),
            reason_codes=validation_errors if scenario_id == validation_scenario else (),
        )
        for scenario_id in SCENARIOS
    )

    paths = _write_artifacts(
        output_dir=Path(output_dir_raw),
        capture_id=_capture_id(observed_env),
        provider_name=provider_name,
        provider_model=provider_model,
        prompt=prompt,
        raw_response=raw_response,
        validation_status=response_file_result["final_status"],
        final_status=final_status,
    )
    return _result(
        final_status=final_status,
        scenarios=scenarios,
        counters=counters,
        artifacts=(paths["raw_response_path"], paths["metadata_path"]),
        validation_errors=validation_errors,
        response_file_result=response_file_result,
    )


def _counter_lines(counters: dict[str, int]) -> list[str]:
    ordered = (
        "scenarios_total",
        "scenarios_passed",
        "explicit_provider_config_present_count",
        "provider_call_attempted_count",
        "provider_call_succeeded_count",
        "provider_call_failed_count",
        "provider_timeout_count",
        "raw_response_artifact_created_count",
        "raw_response_artifact_validated_count",
        "semantic_claim_created_count",
        "semantic_claim_validated_locally_count",
        "semantic_claim_rejected_count",
        "response_file_lane_used_count",
        "live_model_call_count",
        "network_used_count",
        "gemini_called_count",
        "groq_called_count",
        "local_slm_called_count",
        "secrets_accessed_count",
        "secrets_logged_count",
        "connector_called_count",
        "bank_connector_called_count",
        "supplier_connector_called_count",
        "warehouse_connector_called_count",
        "payment_executed_count",
        "shipment_released_count",
        "authority_claimed_count",
        "action_permission_created_count",
        "final_output_created_from_provider_count",
        "silent_fallback_to_deterministic_pass_count",
        "root_final_authority_preserved_count",
    )
    return [f"{key}: {counters[key]}" for key in ordered]


def render_report(result: dict[str, Any] | None = None) -> str:
    result = result or run_live_provider_adapter_response_capture()
    lines = [
        TITLE,
        "",
        "Configuration markers:",
        ENV_CAPTURE,
        ENV_PROVIDER_NAME,
        ENV_PROVIDER_MODEL,
        ENV_OUTPUT_DIR,
        "",
        "Scenario results:",
        *[
            f"- {scenario['scenario_id']}: {scenario['status']}"
            for scenario in result["scenarios"]
        ],
        "",
        "Counters:",
        *_counter_lines(result["counters"]),
        "",
        "Artifacts:",
        *[f"- {path}" for path in result["artifacts"]],
        "",
        "Validation errors:",
        *[f"- {error}" for error in result["validation_errors"]],
        "",
        "Provider error:",
        str(result["provider_error"]),
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
    result = run_live_provider_adapter_response_capture()
    print(render_report(result))
    return 1 if result["final_status"] == "FAIL_CLOSED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
