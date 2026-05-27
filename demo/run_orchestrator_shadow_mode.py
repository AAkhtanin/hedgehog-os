from __future__ import annotations

import argparse
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from demo.run_intent_route_matrix import (
    IntentRouteRow,
    _intent_certificate,
    _intent_direct_reuse,
    _intent_forbidden_certificate,
    _intent_general,
    _intent_permission,
    _intent_reflex,
)


FORBIDDEN_OUTPUT_TERMS = (
    "raw_user_text",
    "api_key",
    "token",
    "secret",
    "hidden reasoning",
    "chain of thought",
)


@dataclass
class ShadowSuggestion:
    suggested_route: str
    confidence: float
    reason: str
    required_guards: list[str]
    model_provider: str = "mock"
    shadow_only: bool = True


@dataclass
class ShadowRow:
    scenario: str
    input_kind: str
    expected_route: str
    shadow_suggested_route: str
    status: str
    confidence: float
    deterministic_route_used: bool
    shadow_controlled_execution: bool
    required_guards: list[str]
    reason: str


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _shadow_suggestion(scenario: str) -> ShadowSuggestion:
    suggestions = {
        "intent_reflex_turn_on_tv": ShadowSuggestion(
            suggested_route="deterministic_reflex",
            confidence=0.96,
            reason="simple known deterministic action",
            required_guards=["PermissionGate", "DRS writeback"],
        ),
        "intent_general_explain_bicycles": ShadowSuggestion(
            suggested_route="llm_general",
            confidence=0.91,
            reason="general explanatory request",
            required_guards=["Root final authority", "No external action"],
        ),
        "intent_certificate_request": ShadowSuggestion(
            suggested_route="proof_full_pipeline",
            confidence=0.88,
            reason="certificate task needs bounded planning",
            required_guards=["AVF", "PlanGraph contract", "Post V&V", "GT"],
        ),
        "intent_repeated_certificate_direct_reuse": ShadowSuggestion(
            suggested_route="direct_reuse",
            confidence=0.87,
            reason="repeat request may use trusted eligible memory",
            required_guards=["DirectReuseGate", "Freshness", "PolicyOK", "DRS writeback"],
        ),
        "intent_permissioned_order_pizza": ShadowSuggestion(
            suggested_route="permission_required",
            confidence=0.94,
            reason="purchase-like action requires confirmation before mock execution",
            required_guards=["PermissionGate", "Audit", "No real external action"],
        ),
        "intent_forbidden_certificate_route": ShadowSuggestion(
            suggested_route="proof_full_pipeline",
            confidence=0.86,
            reason="certificate task may include unsafe candidate but must be hard-masked",
            required_guards=["AVF", "HardMask", "forbidden vector block", "Root final authority"],
        ),
    }
    return suggestions[scenario]


def _row_status(expected_route: str, suggestion: ShadowSuggestion) -> str:
    if expected_route == suggestion.suggested_route:
        return "MATCH"
    if suggestion.suggested_route == "permission_required" and expected_route == "deterministic_reflex":
        return "MATCH_WITH_PERMISSION_GUARD"
    if suggestion.suggested_route in {"proof_full_pipeline", "reject_or_block"} and expected_route == "proof_full_pipeline":
        return "MATCH_WITH_SAFETY_GUARD"
    return "MISMATCH"


def _to_shadow_row(route_row: IntentRouteRow) -> ShadowRow:
    suggestion = _shadow_suggestion(route_row.scenario)
    status = _row_status(route_row.expected_route, suggestion)
    return ShadowRow(
        scenario=route_row.scenario.replace("intent_", "shadow_", 1),
        input_kind=route_row.natural_input_kind,
        expected_route=route_row.expected_route,
        shadow_suggested_route=suggestion.suggested_route,
        status=status,
        confidence=suggestion.confidence,
        deterministic_route_used=True,
        shadow_controlled_execution=False,
        required_guards=suggestion.required_guards,
        reason=suggestion.reason,
    )


def _sanitize_output(output: str) -> str:
    sanitized = output
    for term in FORBIDDEN_OUTPUT_TERMS:
        sanitized = sanitized.replace(term, "[redacted]")
        sanitized = sanitized.replace(term.upper(), "[redacted]")
    return sanitized


def _intent_rows(root_path: Path) -> list[IntentRouteRow]:
    return [
        _intent_reflex(root_path),
        _intent_general(root_path),
        _intent_certificate(root_path),
        _intent_direct_reuse(root_path),
        _intent_permission(root_path),
        _intent_forbidden_certificate(root_path),
    ]


def run_orchestrator_shadow_mode(*, drs_root: Path | None = None) -> str:
    if drs_root is None:
        with tempfile.TemporaryDirectory(prefix="hedgehog_orchestrator_shadow_") as temp_dir:
            return run_orchestrator_shadow_mode(drs_root=Path(temp_dir))

    rows = [_to_shadow_row(row) for row in _intent_rows(Path(drs_root))]
    matches = sum(row.status == "MATCH" for row in rows)
    guarded_matches = sum(row.status.startswith("MATCH_WITH_") for row in rows)
    mismatches = sum(row.status == "MISMATCH" for row in rows)

    lines = [
        "[ORCHESTRATOR SHADOW MODE]",
        "note: shadow suggestions are advisory; deterministic route still used",
        "note: not LLM Orchestrator control yet",
        "note: no live Gemini by default",
        "",
        "scenario | input_kind | expected_route | shadow_suggested_route | status | confidence | deterministic_route_used | shadow_controlled_execution | required_guards | reason",
        "--- | --- | --- | --- | --- | --- | --- | --- | --- | ---",
    ]
    for row in rows:
        lines.append(
            " | ".join(
                [
                    row.scenario,
                    row.input_kind,
                    row.expected_route,
                    row.shadow_suggested_route,
                    row.status,
                    f"{row.confidence:.2f}",
                    _bool_text(row.deterministic_route_used),
                    _bool_text(row.shadow_controlled_execution),
                    ",".join(row.required_guards),
                    row.reason,
                ]
            )
        )
    lines.extend(
        [
            "",
            "SUMMARY:",
            f"matches: {matches}",
            f"guarded_matches: {guarded_matches}",
            f"mismatches: {mismatches}",
            "shadow_controlled_execution: false",
            "next_step: route validator / controlled orchestrator later",
        ]
    )
    return _sanitize_output("\n".join(lines).rstrip() + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Render Hedgehog OS Orchestrator shadow mode matrix.")
    parser.parse_args()
    print(run_orchestrator_shadow_mode(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
