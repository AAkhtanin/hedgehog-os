from __future__ import annotations

import demo.run_human_optional_live_llm_evidence_reader_smoke_walkthrough_v01 as walkthrough
import demo.run_optional_live_llm_evidence_reader_smoke_v01 as smoke


def _default_result():
    return smoke.run_optional_live_llm_evidence_reader_smoke(env={})


def test_runner_imports_and_exposes_required_api() -> None:
    assert (
        walkthrough.TITLE
        == "HEDGEHOG OS - HUMAN OPTIONAL LIVE LLM EVIDENCE READER SMOKE WALKTHROUGH v0.1"
    )
    assert callable(walkthrough.render_walkthrough)
    assert callable(walkthrough.main)


def test_render_walkthrough_calls_committed_optional_smoke_runtime(monkeypatch) -> None:
    calls = {"count": 0}

    def fake_runtime(*, env):
        calls["count"] += 1
        assert env == {}
        return _default_result()

    monkeypatch.setattr(
        walkthrough,
        "run_optional_live_llm_evidence_reader_smoke",
        fake_runtime,
    )

    output = walkthrough.render_walkthrough()

    assert calls["count"] == 1
    assert "underlying_runtime_status: SKIPPED_CLOSED" in output
    assert "FINAL STATUS: PASS" in output


def test_main_exits_zero_and_prints_required_title(capsys) -> None:
    assert walkthrough.main() == 0
    output = capsys.readouterr().out

    assert walkthrough.TITLE in output
    assert "FINAL STATUS: PASS" in output


def test_walkthrough_output_contains_required_sections() -> None:
    output = walkthrough.render_walkthrough(_default_result())

    required_sections = (
        "1. WHAT THIS LAYER IS",
        "2. WHAT THIS LAYER IS NOT",
        "3. DEFAULT MODE: SKIPPED_CLOSED",
        "4. RESPONSE-FILE MODE",
        "5. VALID CLAIM BOUNDARY",
        "6. FAIL-CLOSED CASES",
        "7. DETERMINISTIC READER BOUNDARY",
        "8. WHY THIS MATTERS FOR WOW v0.2",
        "9. LIMITATIONS",
        "10. FINAL STATUS",
    )
    for section in required_sections:
        assert section in output


def test_walkthrough_output_contains_required_markers_and_counters() -> None:
    output = walkthrough.render_walkthrough(_default_result())

    required_markers = (
        "underlying_runtime_status: SKIPPED_CLOSED",
        "walkthrough_required_counters_match: True",
        "live_model_call_count: 0",
        "network_used_count: 0",
        "semantic_claim_created_count: 0",
        "silent_fallback_to_deterministic_pass_count: 0",
        "deterministic_reader_mutated_count: 0",
        "root_final_authority_preserved_count: 1",
        "response-file mode only",
        "command adapter absent/deferred",
        "Root remains final authority",
    )
    for marker in required_markers:
        assert marker in output


def test_walkthrough_explains_response_file_and_claim_boundary() -> None:
    output = walkthrough.render_walkthrough(_default_result())

    assert "Default runner result is FINAL STATUS: SKIPPED_CLOSED." in output
    assert "No config means no live call, no model call, no network call, no connector call." in output
    assert "SKIPPED_CLOSED is safe closure" in output
    assert "Explicit response-file mode is the future live-smoke path." in output
    assert "The runner consumes a response file; it does not call Gemini/model/network." in output
    assert (
        "In explicit response-file mode, any live provider read would happen outside the runner; "
        "this default walkthrough does not execute it."
    ) in output
    assert "The response-file artifact is treated as untrusted input." in output
    assert "A valid response file can create exactly one locally validated SemanticEvidenceClaim candidate." in output
    assert "SemanticEvidenceClaim is candidate evidence only." in output
    assert "The claim is not truth." in output
    assert "The claim is not authority." in output
    assert "The claim is not action permission." in output
    assert "The claim is not FinalOutput." in output
    assert "Root review is required." in output


def test_walkthrough_explains_fail_closed_and_reader_boundaries() -> None:
    output = walkthrough.render_walkthrough(_default_result())

    assert "invalid JSON fails closed" in output
    assert "Authority/action/FinalOutput/connector claims fail closed." in output
    assert "unexpected fields fail closed" in output
    assert "secret-like keys and values fail closed" in output
    assert "decision-like wording remains non-authoritative" in output
    assert "deterministic_fixture_reader remains unchanged" in output
    assert "ReaderMode.live_llm_reader remains fail-closed" in output


def test_walkthrough_output_avoids_forbidden_claims() -> None:
    output = walkthrough.render_walkthrough(_default_result())
    forbidden_terms = (
        "live model was " + "called",
        "Gemini was " + "called",
        "network was " + "called",
        "production " + "ready",
        "public auditor " + "ready",
        "production " + "E2E",
        "real payment " + "executed",
        "real shipment " + "released",
        "WOW v0.2 " + "started",
        "NeedleFactory " + "started",
        "Marennya " + "started",
        "UP " + "started",
        "LLM output is " + "truth",
        "LLM output is " + "authority",
    )

    for term in forbidden_terms:
        assert term not in output
