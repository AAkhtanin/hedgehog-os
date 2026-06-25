from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any, Mapping

import demo.run_live_provider_adapter_response_capture_v01 as adapter
import hedgehog.live_llm_semantic_evidence_reader as reader


TITLE = "HEDGEHOG OS - HUMAN LIVE PROVIDER ADAPTER / RESPONSE CAPTURE WALKTHROUGH v0.1"


def _valid_payload(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "source_id": "human-walkthrough-provider-response-001",
        "source_kind": "live_provider_response_capture_walkthrough",
        "extracted_claim": "warehouse, invoice, and legal evidence require Root review",
        "confidence": 0.62,
        "uncertainty_notes": ["captured provider artifact is untrusted"],
        "provenance_notes": ["source:human_walkthrough_local_capture"],
        "contradiction_flags": ["stock_conflict"],
        "freshness_hint": "walkthrough_current",
        "unsafe_instruction_flags": [],
        "action_requested": "pay_and_release",
        "action_permission_claimed": False,
        "authority_claimed": False,
        "truth_claimed": False,
        "final_output_claimed": False,
        "connector_command_claimed": False,
        "root_review_required": True,
    }
    payload.update(overrides)
    return payload


def _capture_env(output_dir: str, **overrides: str) -> dict[str, str]:
    env = {
        adapter.ENV_CAPTURE: "1",
        adapter.ENV_PROVIDER_NAME: "gemini",
        adapter.ENV_PROVIDER_MODEL: "walkthrough-local-model",
        adapter.ENV_OUTPUT_DIR: output_dir,
        adapter.ENV_CAPTURE_ID: "human-walkthrough-capture",
    }
    env.update(overrides)
    return env


def _provider_returning(raw_text: str):
    def provider(
        prompt: str,
        model_name: str,
        timeout_seconds: int,
        env: Mapping[str, str],
    ) -> str:
        assert "SemanticEvidenceClaim-compatible JSON object" in prompt
        assert model_name
        assert timeout_seconds >= 1
        assert env[adapter.ENV_PROVIDER_NAME] == "gemini"
        return raw_text

    return provider


def _artifact_contains(paths: tuple[str, ...], needle: str) -> bool:
    for path in paths:
        if needle in Path(path).read_text(encoding="utf-8"):
            return True
    return False


def _run_monkeypatched_real_gemini_path(output_dir: str) -> dict[str, Any]:
    fake_key = "walkthrough-fake-key"

    def fake_gemini_provider(
        prompt: str,
        model_name: str,
        timeout_seconds: int,
        env: Mapping[str, str],
    ) -> str:
        assert env[adapter.ENV_GEMINI_API_KEY] == fake_key
        return json.dumps(_valid_payload())

    original = adapter._call_gemini_provider
    adapter._call_gemini_provider = fake_gemini_provider
    try:
        result = adapter.run_live_provider_adapter_response_capture(
            env=_capture_env(output_dir, **{adapter.ENV_GEMINI_API_KEY: fake_key})
        )
    finally:
        adapter._call_gemini_provider = original

    return {
        "result": result,
        "credential_written_to_artifacts": _artifact_contains(result["artifacts"], fake_key),
    }


def _unsafe_outputs_fail_closed(output_dir: str) -> bool:
    unsafe_payloads = (
        "{not-json",
        json.dumps(_valid_payload(authority_claimed=True)),
        json.dumps(_valid_payload(action_permission_claimed=True)),
        json.dumps(_valid_payload(final_output_claimed=True)),
        json.dumps(_valid_payload(connector_command_claimed=True)),
        json.dumps(_valid_payload(api_key="abc")),
    )
    for index, raw_text in enumerate(unsafe_payloads):
        result = adapter.run_live_provider_adapter_response_capture(
            env=_capture_env(output_dir, **{adapter.ENV_CAPTURE_ID: f"unsafe-{index}"}),
            provider=_provider_returning(raw_text),
        )
        if result["final_status"] != "FAIL_CLOSED":
            return False
    return True


def _reader_live_mode_disabled() -> bool:
    try:
        reader.build_semantic_evidence_claims(
            reader.make_default_inputs(),
            reader_mode=reader.ReaderMode.live_llm_reader,
        )
    except ValueError as exc:
        return str(exc) == reader.LIVE_LLM_READER_DISABLED_MESSAGE
    return False


def build_walkthrough_result() -> dict[str, Any]:
    default_result = adapter.run_live_provider_adapter_response_capture(env={})

    with TemporaryDirectory(prefix="hedgehog-live-provider-walkthrough-") as temp_dir:
        fake_result = adapter.run_live_provider_adapter_response_capture(
            env=_capture_env(temp_dir),
            provider=_provider_returning(json.dumps(_valid_payload())),
        )
        patched_result = _run_monkeypatched_real_gemini_path(temp_dir)
        unsafe_outputs_fail_closed = _unsafe_outputs_fail_closed(temp_dir)

    fake_counters = fake_result["counters"]
    patched_counters = patched_result["result"]["counters"]
    response_file_result = fake_result["response_file_result"]
    candidate_claim = response_file_result["claims"][0]

    candidate_non_authoritative = (
        candidate_claim.truth_claimed is False
        and candidate_claim.authority_claimed is False
        and candidate_claim.action_permission_claimed is False
        and candidate_claim.final_output_claimed is False
        and candidate_claim.root_review_required is True
    )
    walkthrough_required_counters_match = (
        default_result["final_status"] == "SKIPPED_CLOSED"
        and fake_counters["live_model_call_count"] == 0
        and fake_counters["network_used_count"] == 0
        and fake_counters["gemini_called_count"] == 0
        and patched_counters["secrets_accessed_count"] == 1
        and patched_result["credential_written_to_artifacts"] is False
        and fake_counters["response_file_lane_used_count"] == 1
        and fake_counters["semantic_claim_created_count"] == 1
        and unsafe_outputs_fail_closed is True
        and candidate_non_authoritative is True
        and _reader_live_mode_disabled() is True
    )

    return {
        "title": TITLE,
        "final_status": "PASS" if walkthrough_required_counters_match else "FAIL",
        "underlying_default_status": default_result["final_status"],
        "fake_provider_live_model_count": fake_counters["live_model_call_count"],
        "fake_provider_network_count": fake_counters["network_used_count"],
        "fake_provider_gemini_count": fake_counters["gemini_called_count"],
        "real_gemini_credential_access_count": patched_counters["secrets_accessed_count"],
        "credential_written_to_artifacts": patched_result[
            "credential_written_to_artifacts"
        ],
        "response_file_lane_used_count": fake_counters["response_file_lane_used_count"],
        "semantic_claim_created_count": fake_counters["semantic_claim_created_count"],
        "unsafe_outputs_fail_closed": unsafe_outputs_fail_closed,
        "candidate_claim_non_authoritative": candidate_non_authoritative,
        "reader_live_mode_disabled": _reader_live_mode_disabled(),
        "walkthrough_required_counters_match": walkthrough_required_counters_match,
        "root_final_authority_preserved_count": fake_counters[
            "root_final_authority_preserved_count"
        ],
    }


def render_walkthrough(result: dict[str, Any] | None = None) -> str:
    result = result or build_walkthrough_result()
    credential_written = str(result["credential_written_to_artifacts"]).lower()
    lines = [
        TITLE,
        "",
        "1. WHAT THIS LAYER IS",
        "- controlled adapter + response capture boundary",
        "- default offline/SKIPPED_CLOSED",
        "- explicit-only live provider path",
        "- raw provider response captured as local artifact",
        "- artifact validated through the existing Optional Live LLM Evidence Reader Smoke response-file lane",
        "- SemanticEvidenceClaim remains candidate-only",
        "- Root remains final authority",
        "",
        "2. WHAT THIS LAYER IS NOT",
        "- not Supplier Payment integration",
        "- not WOW v0.2",
        "- not Full Semantic E2E",
        "- not production",
        "- not public WOW",
        "- not NeedleFactory / Marennya / UP",
        "- no bank/supplier/warehouse connector",
        "- no payment",
        "- no shipment release",
        "- no FinalOutput from provider",
        "",
        "3. HUMAN SCENARIO NARRATION",
        "Act 1: default run has no config and returns SKIPPED_CLOSED.",
        "Act 2: fake provider test proves artifact capture and validation without live model/network/Gemini counting.",
        "Act 3: monkeypatched real-Gemini path proves env credential access is counted while key is not written to artifacts.",
        "Act 4: unsafe provider outputs fail closed: invalid JSON, authority/action/FinalOutput/connector claim, secret-like key/value.",
        "Act 5: prompt injection is preserved as evidence, not instruction.",
        "Act 6: response-file lane and underlying ReaderMode.live_llm_reader remain bounded/fail-closed.",
        "Conclusion: provider may read, but provider cannot decide.",
        "",
        "4. WALKTHROUGH FACTS",
        f"underlying_default_status: {result['underlying_default_status']}",
        f"fake_provider_live_model_count: {result['fake_provider_live_model_count']}",
        f"fake_provider_network_count: {result['fake_provider_network_count']}",
        f"fake_provider_gemini_count: {result['fake_provider_gemini_count']}",
        f"real_gemini_credential_access_count: {result['real_gemini_credential_access_count']}",
        f"credential_written_to_artifacts: {credential_written}",
        f"response_file_lane_used_count: {result['response_file_lane_used_count']}",
        f"semantic_claim_created_count: {result['semantic_claim_created_count']}",
        f"unsafe_outputs_fail_closed: {result['unsafe_outputs_fail_closed']}",
        f"candidate_claim_non_authoritative: {result['candidate_claim_non_authoritative']}",
        f"walkthrough_required_counters_match: {result['walkthrough_required_counters_match']}",
        f"root_final_authority_preserved_count: {result['root_final_authority_preserved_count']}",
        "ReaderMode.live_llm_reader remains disabled",
        "Root remains final authority",
        "",
        f"FINAL STATUS: {result['final_status']}",
    ]
    return "\n".join(lines)


def main() -> int:
    result = build_walkthrough_result()
    print(render_walkthrough(result))
    return 0 if result["final_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
