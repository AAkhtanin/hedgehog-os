from __future__ import annotations

from typing import Any

from demo.run_optional_live_llm_evidence_reader_smoke_v01 import (
    run_optional_live_llm_evidence_reader_smoke,
)


TITLE = "HEDGEHOG OS - HUMAN OPTIONAL LIVE LLM EVIDENCE READER SMOKE WALKTHROUGH v0.1"


REQUIRED_COUNTERS = (
    "live_model_call_count",
    "network_used_count",
    "semantic_claim_created_count",
    "silent_fallback_to_deterministic_pass_count",
    "deterministic_reader_mutated_count",
    "root_final_authority_preserved_count",
)


def _walkthrough_required_counters_match(result: dict[str, Any]) -> bool:
    counters = result["counters"]
    return (
        result["final_status"] == "SKIPPED_CLOSED"
        and counters["live_model_call_count"] == 0
        and counters["network_used_count"] == 0
        and counters["semantic_claim_created_count"] == 0
        and counters["silent_fallback_to_deterministic_pass_count"] == 0
        and counters["deterministic_reader_mutated_count"] == 0
        and counters["root_final_authority_preserved_count"] == 1
    )


def _counter_lines(result: dict[str, Any]) -> list[str]:
    counters = result["counters"]
    return [f"{key}: {counters[key]}" for key in REQUIRED_COUNTERS]


def render_walkthrough(result: dict[str, Any] | None = None) -> str:
    result = result or run_optional_live_llm_evidence_reader_smoke(env={})
    counters_match = _walkthrough_required_counters_match(result)
    final_status = "PASS" if counters_match else "FAIL"
    lines = [
        TITLE,
        "",
        "1. WHAT THIS LAYER IS",
        "This is a human explanation of the already implemented Optional Live LLM Evidence Reader Smoke v0.1 runtime.",
        "The walkthrough adds no runtime capability and calls the committed optional smoke runner.",
        "The layer is response-file mode only.",
        "",
        "2. WHAT THIS LAYER IS NOT",
        "It is not a live provider integration.",
        "It is not a core PASS dependency.",
        "It is not production live integration.",
        "It does not prove production end-to-end behavior.",
        "It does not start WOW v0.2.",
        "It does not add production connectors, secrets, ActionCommitPacket, Permission UX, Marennya, UP, or NeedleFactory.",
        "",
        "3. DEFAULT MODE: SKIPPED_CLOSED",
        f"underlying_runtime_status: {result['final_status']}",
        "Default runner result is FINAL STATUS: SKIPPED_CLOSED.",
        "No config means no live call, no model call, no network call, no connector call.",
        "SKIPPED_CLOSED is safe closure, not proof that a live provider call occurred.",
        "walkthrough_required_counters_match: " + str(counters_match),
        *_counter_lines(result),
        "",
        "4. RESPONSE-FILE MODE",
        "Explicit response-file mode is the future live-smoke path.",
        "The runner consumes a response file; it does not call Gemini/model/network.",
        "In explicit response-file mode, any live provider read would happen outside the runner; this default walkthrough does not execute it.",
        "The response-file artifact is treated as untrusted input.",
        "command adapter absent/deferred",
        "",
        "5. VALID CLAIM BOUNDARY",
        "A valid response file can create exactly one locally validated SemanticEvidenceClaim candidate.",
        "SemanticEvidenceClaim is candidate evidence only.",
        "The claim is not truth.",
        "The claim is not authority.",
        "The claim is not action permission.",
        "The claim is not FinalOutput.",
        "Root review is required.",
        "decision-like wording remains non-authoritative",
        "",
        "6. FAIL-CLOSED CASES",
        "invalid JSON fails closed",
        "Authority/action/FinalOutput/connector claims fail closed.",
        "unexpected fields fail closed",
        "secret-like keys and values fail closed",
        "Invalid or unsafe responses do not fall back to deterministic PASS.",
        "",
        "7. DETERMINISTIC READER BOUNDARY",
        "deterministic_fixture_reader remains unchanged",
        "ReaderMode.live_llm_reader remains fail-closed in the closed deterministic runtime.",
        "The optional smoke lane does not mutate the closed deterministic reader.",
        "",
        "8. WHY THIS MATTERS FOR WOW v0.2",
        "This is useful before a future WOW iteration because it proves the handoff shape for externally captured evidence.",
        "The lane can show how one raw response-file artifact becomes bounded candidate evidence while preserving local validation.",
        "",
        "9. LIMITATIONS",
        "This walkthrough does not execute an explicit response-file run.",
        "It does not validate a real provider session.",
        "It does not add connectors, secrets, action permission, payment execution, shipment release, or FinalOutput authority.",
        "Root remains final authority.",
        "",
        "10. FINAL STATUS",
        f"FINAL STATUS: {final_status}",
    ]
    return "\n".join(lines)


def main() -> int:
    result = run_optional_live_llm_evidence_reader_smoke(env={})
    output = render_walkthrough(result)
    print(output)
    return 0 if "FINAL STATUS: PASS" in output else 1


if __name__ == "__main__":
    raise SystemExit(main())
