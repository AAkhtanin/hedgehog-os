from __future__ import annotations

import sys
from typing import Any

from hedgehog.live_llm_semantic_evidence_reader import (
    AUTHORITY_BOUNDARY_SUMMARY,
    HOSTILE_PROMPT_EXAMPLES,
    INPUT_KINDS,
    LIMITATIONS,
    SCENARIOS,
    ZERO_COUNTER_KEYS,
    ReaderMode,
    SemanticEvidenceClaim,
    SemanticEvidenceInput,
    SemanticEvidenceReaderReport,
    build_semantic_evidence_claims,
    evaluate_semantic_evidence_inputs,
    make_default_inputs,
    run_live_llm_semantic_evidence_reader_scenarios,
)


TITLE = "HEDGEHOG OS — LIVE LLM SEMANTIC EVIDENCE READER v0.1"

TOPOLOGY = (
    "dirty business evidence text",
    "deterministic fixture reader",
    "SemanticEvidenceInput",
    "SemanticEvidenceClaim",
    "bounded semantic claims",
    "DRS / AVF / advisory candidate route",
    "Root-shaped route",
    "Root final review",
)


def _counter_lines(counters: dict[str, int]) -> list[str]:
    ordered_keys = (
        "scenarios_total",
        "scenarios_passed",
        "llm_inputs_seen_count",
        "semantic_claims_created_count",
        "uncertainty_notes_created_count",
        "contradiction_flags_created_count",
        "unsafe_instruction_flags_created_count",
        "root_review_required_count",
        "deterministic_fixture_reader_used_count",
        *ZERO_COUNTER_KEYS,
        "semantic_claim_routed_as_candidate_count",
        "root_final_authority_preserved_count",
    )
    return [f"{key}: {counters[key]}" for key in ordered_keys]


def _claim_lines(result: dict[str, Any]) -> list[str]:
    report = result["report"]
    return [
        f"- {claim.source_kind}: {claim.extracted_claim}"
        for claim in report.claims
    ]


def render_report(result: dict[str, Any] | None = None) -> str:
    result = result or run_live_llm_semantic_evidence_reader_scenarios()
    counters = result["counters"]
    report = result["report"]
    lines = [
        TITLE,
        "",
        "Reader mode summary:",
        f"active_reader_mode: {result['reader_mode']}",
        "deterministic_fixture_reader is default and active.",
        "live_llm_reader exists only as a disabled/default-off mode marker.",
        f"live_llm_default_enabled_count: {counters['live_llm_default_enabled_count']}",
        f"live_llm_core_pass_dependency_count: {counters['live_llm_core_pass_dependency_count']}",
        "Live model output is untrusted evidence text, not truth or authority.",
        "",
        "Input evidence summary:",
        *[f"- {kind}" for kind in INPUT_KINDS],
        "",
        "Topology summary:",
        " -> ".join(TOPOLOGY),
        "",
        "Semantic claim shape summary:",
        "SemanticEvidenceInput -> SemanticEvidenceClaim -> SemanticEvidenceReaderReport",
        "ReaderMode, build_semantic_evidence_claims, and evaluate_semantic_evidence_inputs are deterministic in v0.1.",
        "SemanticEvidenceClaim is candidate evidence only.",
        "Required claim flags remain false: action_permission_claimed, authority_claimed, truth_claimed, final_output_claimed, connector_command_claimed.",
        "",
        "Scenario coverage:",
        *[
            f"- {scenario['scenario_id']}: {scenario['status']}"
            for scenario in result["scenarios"]
        ],
        "",
        "Claim extraction summary:",
        *_claim_lines(result),
        "",
        "Prompt injection boundary summary:",
        "Hostile prompt text is preserved as evidence text.",
        *[f"- {text}" for text in HOSTILE_PROMPT_EXAMPLES],
        "unsafe_instruction_flags_created_count: "
        f"{counters['unsafe_instruction_flags_created_count']}",
        "prompt_injection_escalation_count: 0",
        "No Root, Architect, Executor, Fractal Cell, bank, supplier, warehouse, or connector command is created.",
        "Claims return as candidates to Root-shaped route.",
        "",
        "Connection to Zero Trust Supplier Payment WOW:",
        "Dirty invoice, stock, supplier, bank slot, legal, memory, approval, and prompt-injection evidence can become bounded semantic claims.",
        "Those claims can later feed DRS / AVF / advisory review as candidates only.",
        "The reader cannot execute payment, release shipment, call connectors, access secrets, or create FinalOutput.",
        "",
        "Aggregate counters:",
        *_counter_lines(counters),
        "",
        "Authority boundary summary:",
        *AUTHORITY_BOUNDARY_SUMMARY,
        "",
        "Limitations:",
        *LIMITATIONS,
        "Default run does not use network/Gemini/real model calls.",
        "Real Semantic Runtime MVP is not complete.",
        "",
        f"FINAL STATUS: {result['final_status']}",
    ]
    return "\n".join(lines)


def main() -> int:
    result = run_live_llm_semantic_evidence_reader_scenarios()
    print(render_report(result))
    return 0 if result["final_status"] == "PASS" else 1


__all__ = (
    "TITLE",
    "TOPOLOGY",
    "ReaderMode",
    "SemanticEvidenceInput",
    "SemanticEvidenceClaim",
    "SemanticEvidenceReaderReport",
    "build_semantic_evidence_claims",
    "evaluate_semantic_evidence_inputs",
    "make_default_inputs",
    "run_live_llm_semantic_evidence_reader_scenarios",
    "render_report",
    "main",
)


if __name__ == "__main__":
    sys.exit(main())
