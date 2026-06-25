from __future__ import annotations

import sys
from typing import Any

from hedgehog.live_llm_semantic_evidence_reader import (
    HOSTILE_PROMPT_EXAMPLES,
    INPUT_KINDS,
    LIVE_LLM_READER_DISABLED_MESSAGE,
    SCENARIOS,
    ReaderMode,
    build_semantic_evidence_claims,
    make_default_inputs,
    run_live_llm_semantic_evidence_reader_scenarios,
)


TITLE = "HEDGEHOG OS — HUMAN LIVE LLM SEMANTIC EVIDENCE READER WALKTHROUGH v0.1"

REQUIRED_COUNTER_VALUES = {
    "scenarios_total": 10,
    "scenarios_passed": 10,
    "llm_inputs_seen_count": 11,
    "semantic_claims_created_count": 11,
    "contradiction_flags_created_count": 2,
    "unsafe_instruction_flags_created_count": 6,
    "deterministic_fixture_reader_used_count": 1,
    "live_llm_default_enabled_count": 0,
    "live_llm_core_pass_dependency_count": 0,
    "live_model_call_count": 0,
    "network_used_count": 0,
    "gemini_used_count": 0,
    "secrets_accessed_count": 0,
    "truth_claimed_count": 0,
    "authority_claimed_count": 0,
    "action_permission_claimed_count": 0,
    "final_output_claimed_count": 0,
    "connector_command_created_count": 0,
    "payment_executed_count": 0,
    "shipment_released_count": 0,
    "prompt_injection_escalation_count": 0,
    "root_final_authority_preserved_count": 10,
}


def _live_mode_guard_message() -> str:
    try:
        build_semantic_evidence_claims(
            make_default_inputs(),
            reader_mode=ReaderMode.live_llm_reader,
        )
    except ValueError as exc:
        return str(exc)
    return "live_llm_reader unexpectedly produced claims"


def _walkthrough_required_counters_match(counters: dict[str, int]) -> bool:
    return all(counters.get(key) == value for key, value in REQUIRED_COUNTER_VALUES.items())


def run_walkthrough() -> dict[str, Any]:
    runtime_result = run_live_llm_semantic_evidence_reader_scenarios()
    counters = runtime_result["counters"]
    live_mode_guard_message = _live_mode_guard_message()
    walkthrough_required_counters_match = _walkthrough_required_counters_match(
        counters
    )
    pass_conditions = {
        "underlying_runtime_passed": runtime_result["final_status"] == "PASS",
        "required_counters_match": walkthrough_required_counters_match,
        "live_mode_fails_closed": (
            live_mode_guard_message == LIVE_LLM_READER_DISABLED_MESSAGE
        ),
    }
    return {
        "runtime_result": runtime_result,
        "counters": counters,
        "live_mode_guard_message": live_mode_guard_message,
        "walkthrough_required_counters_match": walkthrough_required_counters_match,
        "pass_conditions": pass_conditions,
        "final_status": "PASS" if all(pass_conditions.values()) else "FAIL",
    }


def _counter_lines(counters: dict[str, int]) -> list[str]:
    return [
        f"{key}: {counters[key]}"
        for key in REQUIRED_COUNTER_VALUES
    ]


def render_walkthrough(result: dict[str, Any] | None = None) -> str:
    result = result or run_walkthrough()
    runtime_result = result["runtime_result"]
    counters = result["counters"]
    lines = [
        TITLE,
        "",
        "1. WHAT THIS WALKTHROUGH IS",
        "This is a human explanation only for the already implemented Live LLM Semantic Evidence Reader / Extractor v0.1.",
        "It creates no new capability, no live model call, and no network/Gemini/secret/connector behavior.",
        "Live LLM is not active in this layer.",
        "",
        "2. CORE IDEA",
        "This layer creates the bounded contract for future live LLM evidence reading.",
        "It is the socket/adapter/contract where a future live LLM can return bounded semantic claims.",
        "The current v0.1 active reader is deterministic_fixture_reader only.",
        "",
        "3. ACT 1 — DIRTY BUSINESS EVIDENCE ENTERS READER BOUNDARY",
        "Invoice, warehouse note, supplier email, bank slot, compliance note, stale memory, and prompt injection document enter as SemanticEvidenceInput.",
        *[f"- {kind}" for kind in INPUT_KINDS],
        "",
        "4. ACT 2 — READER CREATES SEMANTIC EVIDENCE CLAIMS",
        "SemanticEvidenceClaim is created with confidence, uncertainty, provenance, contradiction flags, and unsafe instruction flags.",
        "SemanticEvidenceClaim is not truth.",
        "",
        "5. ACT 3 — CLAIMS ARE CANDIDATES ONLY",
        "Claims route to DRS/AVF/advisory as candidates.",
        "They are not direct reuse.",
        "SemanticEvidenceClaim is not action permission.",
        "SemanticEvidenceClaim is not FinalOutput.",
        "SemanticEvidenceClaim is not authority.",
        "",
        "6. ACT 4 — LIVE LLM MODE IS DISABLED AND FAILS CLOSED",
        "deterministic_fixture_reader is active default.",
        "live_llm_reader default off.",
        f"Explicit ReaderMode.live_llm_reader raises ValueError(\"{result['live_mode_guard_message']}\").",
        "",
        "7. ACT 5 — PROMPT INJECTION IS PRESERVED AS EVIDENCE, NOT OBEYED",
        "Prompt injection text is evidence, not instruction.",
        "Hostile text examples are preserved.",
        *[f"- {text}" for text in HOSTILE_PROMPT_EXAMPLES],
        "unsafe_instruction_flags are created.",
        "No escalation occurs.",
        "No bank/supplier/warehouse/connector/Architect/Executor/Fractal Cell command is created.",
        "",
        "8. ACT 6 — ZERO TRUST SUPPLIER PAYMENT WOW CONNECTION",
        "Bank/supplier/warehouse examples are demo-domain stress cases, not the limit of the construct.",
        "The construct is universal across dirty evidence domains.",
        "Zero Trust WOW is used because money/actions/secrets expose boundary mistakes clearly.",
        "",
        "9. ACT 7 — ROOT FINAL AUTHORITY PRESERVED",
        "Root remains final authority.",
        "Real Semantic Runtime MVP is not complete.",
        "",
        "Scenario coverage:",
        *[
            f"- {scenario['scenario_id']}: {scenario['status']}"
            for scenario in runtime_result["scenarios"]
        ],
        "",
        "Counters:",
        *_counter_lines(counters),
        f"walkthrough_required_counters_match: {result['walkthrough_required_counters_match']}",
        "",
        "Authority summary:",
        "SemanticEvidenceClaim is not truth.",
        "SemanticEvidenceClaim is not authority.",
        "SemanticEvidenceClaim is not action permission.",
        "SemanticEvidenceClaim is not FinalOutput.",
        "Root remains final authority.",
        "",
        f"FINAL STATUS: {result['final_status']}",
    ]
    return "\n".join(lines)


def main() -> int:
    result = run_walkthrough()
    print(render_walkthrough(result))
    return 0 if result["final_status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
