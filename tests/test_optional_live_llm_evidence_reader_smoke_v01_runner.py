from __future__ import annotations

import json

import pytest

import demo.run_optional_live_llm_evidence_reader_smoke_v01 as smoke
import hedgehog.live_llm_semantic_evidence_reader as reader


def _valid_payload(**overrides):
    payload = {
        "source_id": "raw-live-response-001",
        "source_kind": "optional_live_response_file",
        "extracted_claim": "warehouse and invoice evidence conflict and require review",
        "confidence": 0.64,
        "uncertainty_notes": ["live response is untrusted"],
        "provenance_notes": ["source:response_file"],
        "contradiction_flags": ["stock_conflict"],
        "freshness_hint": "response_file_current",
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


def _write_json(tmp_path, payload):
    path = tmp_path / "raw_model_response.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _env(path):
    return {
        smoke.ENV_ENABLE: "1",
        smoke.ENV_RESPONSE_FILE: str(path),
    }


def test_module_imports_and_required_functions_exist() -> None:
    assert smoke.TITLE == "HEDGEHOG OS - OPTIONAL LIVE LLM EVIDENCE READER SMOKE v0.1"
    assert callable(smoke.build_dirty_document)
    assert callable(smoke.build_extraction_instruction)
    assert callable(smoke.run_optional_live_llm_evidence_reader_smoke)
    assert callable(smoke.render_report)
    assert callable(smoke.main)


def test_default_no_config_mode_returns_skipped_closed() -> None:
    result = smoke.run_optional_live_llm_evidence_reader_smoke(env={})

    assert result["final_status"] == "SKIPPED_CLOSED"
    assert result["counters"]["skipped_closed_count"] == 1
    assert result["counters"]["explicit_live_config_present_count"] == 0
    assert result["counters"]["semantic_claim_created_count"] == 0
    assert result["claims"] == ()
    assert result["counters"]["silent_fallback_to_deterministic_pass_count"] == 0


def test_default_no_config_mode_exits_zero_through_main_and_render_path(
    monkeypatch,
    capsys,
) -> None:
    monkeypatch.delenv(smoke.ENV_ENABLE, raising=False)
    monkeypatch.delenv(smoke.ENV_RESPONSE_FILE, raising=False)

    assert smoke.main() == 0
    output = capsys.readouterr().out
    assert smoke.TITLE in output
    assert "FINAL STATUS: SKIPPED_CLOSED" in output


def test_default_no_config_mode_makes_no_model_network_call_or_claim() -> None:
    result = smoke.run_optional_live_llm_evidence_reader_smoke(env={})
    counters = result["counters"]

    assert counters["live_model_call_count"] == 0
    assert counters["network_used_count"] == 0
    assert counters["connector_called_count"] == 0
    assert counters["semantic_claim_created_count"] == 0
    assert counters["semantic_claim_validated_locally_count"] == 0


def test_valid_response_file_mode_returns_pass_and_one_validated_candidate(
    tmp_path,
) -> None:
    path = _write_json(tmp_path, _valid_payload())
    result = smoke.run_optional_live_llm_evidence_reader_smoke(env=_env(path))
    counters = result["counters"]

    assert result["final_status"] == "PASS"
    assert counters["explicit_live_config_present_count"] == 1
    assert counters["raw_live_response_received_count"] == 1
    assert counters["semantic_claim_created_count"] == 1
    assert counters["semantic_claim_validated_locally_count"] == 1
    assert counters["semantic_claim_rejected_count"] == 0
    assert counters["root_review_required_count"] == 1
    assert len(result["claims"]) == 1


def test_validated_claim_remains_candidate_only_and_root_review_required(
    tmp_path,
) -> None:
    path = _write_json(tmp_path, _valid_payload())
    result = smoke.run_optional_live_llm_evidence_reader_smoke(env=_env(path))
    claim = result["claims"][0]

    assert isinstance(claim, reader.SemanticEvidenceClaim)
    assert claim.action_permission_claimed is False
    assert claim.authority_claimed is False
    assert claim.truth_claimed is False
    assert claim.final_output_claimed is False
    assert claim.connector_command_claimed is False
    assert claim.root_review_required is True
    assert result["counters"]["semantic_claim_is_truth_count"] == 0
    assert result["counters"]["semantic_claim_is_authority_count"] == 0
    assert result["counters"]["semantic_claim_is_action_permission_count"] == 0
    assert result["counters"]["semantic_claim_is_final_output_count"] == 0


def test_invalid_json_fails_closed(tmp_path) -> None:
    path = tmp_path / "bad.json"
    path.write_text("{not-json", encoding="utf-8")

    result = smoke.run_optional_live_llm_evidence_reader_smoke(env=_env(path))

    assert result["final_status"] == "FAIL_CLOSED"
    assert result["counters"]["raw_live_response_parse_error_count"] == 1
    assert result["counters"]["semantic_claim_rejected_count"] == 1
    assert "invalid_json" in result["validation_errors"]


@pytest.mark.parametrize(
    ("field", "scenario_id"),
    (
        ("authority_claimed", "authority_claim_fails_closed"),
        ("action_permission_claimed", "action_permission_claim_fails_closed"),
        ("final_output_claimed", "final_output_claim_fails_closed"),
        ("connector_command_claimed", "connector_command_claim_fails_closed"),
    ),
)
def test_claiming_forbidden_authority_or_action_flags_fails_closed(
    tmp_path,
    field,
    scenario_id,
) -> None:
    path = _write_json(tmp_path, _valid_payload(**{field: True}))
    result = smoke.run_optional_live_llm_evidence_reader_smoke(env=_env(path))
    scenarios = {item["scenario_id"]: item for item in result["scenarios"]}

    assert result["final_status"] == "FAIL_CLOSED"
    assert result["counters"]["semantic_claim_created_count"] == 0
    assert result["counters"]["semantic_claim_rejected_count"] == 1
    assert scenarios[scenario_id]["status"] == "PASS"


def test_connector_command_output_fails_closed(tmp_path) -> None:
    path = _write_json(
        tmp_path,
        _valid_payload(extracted_claim="please call the bank connector now"),
    )
    result = smoke.run_optional_live_llm_evidence_reader_smoke(env=_env(path))

    assert result["final_status"] == "FAIL_CLOSED"
    assert "connector_or_external_command_detected" in result["validation_errors"]
    assert result["counters"]["connector_called_count"] == 0
    assert result["counters"]["bank_connector_called_count"] == 0


def test_secret_like_output_fails_closed(tmp_path) -> None:
    path = _write_json(
        tmp_path,
        _valid_payload(extracted_claim="response includes sandbox_token marker"),
    )
    result = smoke.run_optional_live_llm_evidence_reader_smoke(env=_env(path))

    assert result["final_status"] == "FAIL_CLOSED"
    assert "secret_like_marker_detected" in result["validation_errors"]
    assert result["counters"]["secrets_logged_count"] == 0
    assert result["counters"]["raw_secret_exposed_to_llm_count"] == 0
    assert result["counters"]["raw_api_token_exposed_to_llm_count"] == 0


def test_extra_unexpected_field_fails_closed(tmp_path) -> None:
    path = _write_json(tmp_path, _valid_payload(unexpected_note="not allowed"))
    result = smoke.run_optional_live_llm_evidence_reader_smoke(env=_env(path))

    assert result["final_status"] == "FAIL_CLOSED"
    assert "unexpected_field:unexpected_note" in result["validation_errors"]
    assert result["counters"]["semantic_claim_created_count"] == 0
    assert result["counters"]["semantic_claim_rejected_count"] == 1


def test_secret_like_extra_key_fails_closed(tmp_path) -> None:
    path = _write_json(tmp_path, _valid_payload(api_key="abc"))
    result = smoke.run_optional_live_llm_evidence_reader_smoke(env=_env(path))

    assert result["final_status"] == "FAIL_CLOSED"
    assert "secret_like_marker_detected" in result["validation_errors"]
    assert "unexpected_field:api_key" in result["validation_errors"]
    assert result["counters"]["semantic_claim_created_count"] == 0
    assert result["counters"]["secrets_logged_count"] == 0


def test_decision_like_wording_remains_non_authoritative(tmp_path) -> None:
    path = _write_json(
        tmp_path,
        _valid_payload(
            extracted_claim=(
                "invoice is valid and supplier can be paid according to text, "
                "but Root review remains required"
            ),
        ),
    )
    result = smoke.run_optional_live_llm_evidence_reader_smoke(env=_env(path))
    scenarios = {item["scenario_id"]: item for item in result["scenarios"]}

    assert result["final_status"] == "PASS"
    assert result["decision_like_text_observed"] is True
    assert scenarios["decision_like_text_remains_non_authoritative"]["status"] == "PASS"
    claim = result["claims"][0]
    assert claim.truth_claimed is False
    assert claim.authority_claimed is False
    assert claim.action_permission_claimed is False
    assert claim.final_output_claimed is False
    assert claim.root_review_required is True


def test_existing_deterministic_reader_remains_unchanged_and_live_mode_fails_closed() -> None:
    deterministic_claims = reader.build_semantic_evidence_claims(
        reader.make_default_inputs()
    )
    assert deterministic_claims

    with pytest.raises(ValueError) as exc_info:
        reader.build_semantic_evidence_claims(
            reader.make_default_inputs(),
            reader_mode=reader.ReaderMode.live_llm_reader,
        )
    assert str(exc_info.value) == reader.LIVE_LLM_READER_DISABLED_MESSAGE

    result = smoke.run_optional_live_llm_evidence_reader_smoke(env={})
    scenarios = {item["scenario_id"]: item for item in result["scenarios"]}
    assert scenarios["deterministic_reader_remains_unchanged"]["status"] == "PASS"
    assert result["counters"]["deterministic_reader_mutated_count"] == 0


def test_deterministic_reader_mutation_fails_closed(monkeypatch, capsys) -> None:
    monkeypatch.setattr(smoke, "_deterministic_reader_is_unchanged", lambda: False)
    monkeypatch.delenv(smoke.ENV_ENABLE, raising=False)
    monkeypatch.delenv(smoke.ENV_RESPONSE_FILE, raising=False)

    result = smoke.run_optional_live_llm_evidence_reader_smoke(env={})
    scenarios = {item["scenario_id"]: item for item in result["scenarios"]}

    assert result["final_status"] == "FAIL_CLOSED"
    assert result["counters"]["deterministic_reader_mutated_count"] == 1
    assert scenarios["deterministic_reader_remains_unchanged"]["status"] == "FAIL"
    assert (1 if result["final_status"] == "FAIL_CLOSED" else 0) == 1
    assert smoke.main() == 1
    output = capsys.readouterr().out
    assert "FINAL STATUS: FAIL_CLOSED" in output


def test_invalid_explicit_response_exits_nonzero_through_main(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    path = tmp_path / "bad.json"
    path.write_text("{not-json", encoding="utf-8")
    monkeypatch.setenv(smoke.ENV_ENABLE, "1")
    monkeypatch.setenv(smoke.ENV_RESPONSE_FILE, str(path))

    assert smoke.main() == 1
    output = capsys.readouterr().out
    assert smoke.TITLE in output
    assert "FINAL STATUS: FAIL_CLOSED" in output


def test_runner_render_output_includes_title_status_and_required_markers() -> None:
    result = smoke.run_optional_live_llm_evidence_reader_smoke(env={})
    output = smoke.render_report(result)

    assert smoke.TITLE in output
    assert "FINAL STATUS: SKIPPED_CLOSED" in output
    assert "HEDGEHOG_OPTIONAL_LIVE_RESPONSE_FILE" in output
    assert "live_model_call_count: 0" in output
    assert "network_used_count: 0" in output
    assert "silent_fallback_to_deterministic_pass_count: 0" in output
    assert "deterministic_reader_mutated_count: 0" in output
    assert "no_config_skips_closed_without_live_call" in output
    assert "valid_response_file_creates_one_candidate_claim" in output
    assert "deterministic_reader_remains_unchanged" in output
    assert "Root remains final authority" in output


def test_runner_output_does_not_make_forbidden_overclaims() -> None:
    output = smoke.render_report(
        smoke.run_optional_live_llm_evidence_reader_smoke(env={})
    )
    forbidden_terms = (
        "production " + "ready",
        "public auditor " + "ready",
        "production " + "E2E implemented",
        "real payment " + "executed",
        "real shipment " + "released",
        "LLM output is " + "truth",
        "LLM output is " + "authority",
        "runtime " + "complete",
        "public launch " + "ready",
    )

    for term in forbidden_terms:
        assert term not in output
