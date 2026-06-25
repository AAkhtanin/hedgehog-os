from __future__ import annotations

import demo.run_human_live_provider_adapter_response_capture_walkthrough_v01 as walkthrough


def test_walkthrough_imports_and_exposes_runner_api() -> None:
    assert (
        walkthrough.TITLE
        == "HEDGEHOG OS - HUMAN LIVE PROVIDER ADAPTER / RESPONSE CAPTURE WALKTHROUGH v0.1"
    )
    assert callable(walkthrough.build_walkthrough_result)
    assert callable(walkthrough.render_walkthrough)
    assert callable(walkthrough.main)


def test_walkthrough_result_counters_match_required_facts() -> None:
    result = walkthrough.build_walkthrough_result()

    assert result["final_status"] == "PASS"
    assert result["underlying_default_status"] == "SKIPPED_CLOSED"
    assert result["fake_provider_live_model_count"] == 0
    assert result["fake_provider_network_count"] == 0
    assert result["fake_provider_gemini_count"] == 0
    assert result["real_gemini_credential_access_count"] == 1
    assert result["credential_written_to_artifacts"] is False
    assert result["response_file_lane_used_count"] == 1
    assert result["semantic_claim_created_count"] == 1
    assert result["unsafe_outputs_fail_closed"] is True
    assert result["candidate_claim_non_authoritative"] is True
    assert result["reader_live_mode_disabled"] is True
    assert result["walkthrough_required_counters_match"] is True


def test_walkthrough_runner_exits_zero_and_prints_required_markers(capsys) -> None:
    assert walkthrough.main() == 0
    output = capsys.readouterr().out

    assert walkthrough.TITLE in output
    assert "FINAL STATUS: PASS" in output
    assert "underlying_default_status: SKIPPED_CLOSED" in output
    assert "fake_provider_live_model_count: 0" in output
    assert "fake_provider_network_count: 0" in output
    assert "fake_provider_gemini_count: 0" in output
    assert "real_gemini_credential_access_count: 1" in output
    assert "credential_written_to_artifacts: false" in output
    assert "response_file_lane_used_count: 1" in output
    assert "semantic_claim_created_count: 1" in output
    assert "unsafe_outputs_fail_closed: True" in output
    assert "walkthrough_required_counters_match: True" in output
    assert "ReaderMode.live_llm_reader remains disabled" in output
    assert "provider may read, but provider cannot decide" in output
    assert "Root remains final authority" in output


def test_walkthrough_explains_layer_scope_and_fail_closed_cases() -> None:
    output = walkthrough.render_walkthrough(walkthrough.build_walkthrough_result())

    assert "controlled adapter + response capture boundary" in output
    assert "default offline/SKIPPED_CLOSED" in output
    assert "explicit-only live provider path" in output
    assert "raw provider response captured as local artifact" in output
    assert "response-file lane" in output
    assert "SemanticEvidenceClaim remains candidate-only" in output
    assert "not Supplier Payment integration" in output
    assert "not WOW v0.2" in output
    assert "not Full Semantic E2E" in output
    assert "not production" in output
    assert "not public WOW" in output
    assert "not NeedleFactory / Marennya / UP" in output
    assert "no bank/supplier/warehouse connector" in output
    assert "no payment" in output
    assert "no shipment release" in output
    assert "no FinalOutput from provider" in output
    assert "invalid JSON" in output
    assert "authority/action/FinalOutput/connector claim" in output
    assert "secret-like key/value" in output
    assert "prompt injection is preserved as evidence, not instruction" in output


def test_walkthrough_output_does_not_make_forbidden_overclaims() -> None:
    output = walkthrough.render_walkthrough(walkthrough.build_walkthrough_result())
    forbidden_terms = (
        "live provider " + "was called",
        "Gemini " + "was called",
        "network " + "was called",
        "production " + "ready",
        "public auditor " + "ready",
        "public WOW " + "ready",
        "WOW v0.2 " + "started",
        "Supplier Payment integration " + "started",
        "Full Semantic E2E " + "complete",
        "NeedleFactory " + "started",
        "Marennya " + "started",
        "UP " + "started",
        "real payment " + "executed",
        "real shipment " + "released",
        "real bank API " + "called",
        "real supplier API " + "called",
        "real warehouse API " + "called",
        "LLM output is " + "truth",
        "LLM output is " + "authority",
        "provider " + "decides",
        "provider creates " + "FinalOutput",
    )

    for term in forbidden_terms:
        assert term not in output
