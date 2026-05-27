from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Any

from demo.run_orchestrator_route_validator import RouteProposal
from demo.run_orchestrator_route_validator import validate_route_proposal


FORBIDDEN_OUTPUT_TERMS = (
    "raw_user_text",
    "api_key",
    "token",
    "secret",
    "hidden reasoning",
    "chain of thought",
)


@dataclass(frozen=True)
class DryRunScenario:
    proposal: RouteProposal
    expected_route: str
    deterministic_fallback_route: str | None = None


@dataclass(frozen=True)
class DryRunResult:
    scenario: str
    suggested_route: str
    validation_decision: str
    allowed: bool
    would_execute_route: str
    controlled_execution_performed: bool
    required_guards: list[str]
    violations: list[str]
    reason: str


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _scenarios() -> list[DryRunScenario]:
    return [
        DryRunScenario(
            proposal=RouteProposal(
                scenario="dryrun_reflex_allowed",
                input_kind="simple_device_command",
                suggested_route="deterministic_reflex",
                confidence=0.96,
                required_guards=["audit", "DRS writeback"],
            ),
            expected_route="deterministic_reflex",
        ),
        DryRunScenario(
            proposal=RouteProposal(
                scenario="dryrun_general_allowed_with_guards",
                input_kind="general_explanation_request",
                suggested_route="llm_general",
                confidence=0.91,
                required_guards=["Root final authority", "budget check", "no external action"],
            ),
            expected_route="llm_general",
        ),
        DryRunScenario(
            proposal=RouteProposal(
                scenario="dryrun_full_pipeline_allowed_with_guards",
                input_kind="certificate_request",
                suggested_route="proof_full_pipeline",
                confidence=0.88,
                required_guards=["AVF", "HardMask", "PlanGraph contract", "Post V&V", "GT"],
                forbidden_candidate_present=True,
            ),
            expected_route="proof_full_pipeline",
        ),
        DryRunScenario(
            proposal=RouteProposal(
                scenario="dryrun_permission_needs_user",
                input_kind="permissioned_mock_purchase",
                suggested_route="permission_required",
                confidence=0.94,
                required_guards=["PermissionGate"],
                wants_direct_action=True,
                permission_confirmed=False,
            ),
            expected_route="deterministic_reflex",
        ),
        DryRunScenario(
            proposal=RouteProposal(
                scenario="dryrun_direct_reuse_allowed",
                input_kind="repeated_certificate_request",
                suggested_route="direct_reuse",
                confidence=0.9,
                required_guards=["DirectReuseGate", "Freshness", "PolicyOK", "DRS writeback"],
                wants_direct_reuse=True,
                direct_reuse_eligible=True,
            ),
            expected_route="direct_reuse",
        ),
        DryRunScenario(
            proposal=RouteProposal(
                scenario="dryrun_direct_reuse_not_eligible_fallback",
                input_kind="repeated_certificate_request",
                suggested_route="direct_reuse",
                confidence=0.82,
                required_guards=["DirectReuseGate"],
                wants_direct_reuse=True,
                direct_reuse_eligible=False,
            ),
            expected_route="proof_full_pipeline",
            deterministic_fallback_route="proof_full_pipeline",
        ),
        DryRunScenario(
            proposal=RouteProposal(
                scenario="dryrun_skip_avf_blocked",
                input_kind="certificate_request_with_forbidden_candidate",
                suggested_route="proof_full_pipeline",
                confidence=0.75,
                required_guards=["PlanGraph contract"],
                wants_skip_avf=True,
                forbidden_candidate_present=True,
            ),
            expected_route="proof_full_pipeline",
        ),
        DryRunScenario(
            proposal=RouteProposal(
                scenario="dryrun_orchestrator_final_output_blocked",
                input_kind="general_explanation_request",
                suggested_route="llm_general",
                confidence=0.8,
                required_guards=["Root final authority"],
                proposed_authority="orchestrator",
                wants_final_output=True,
            ),
            expected_route="llm_general",
        ),
        DryRunScenario(
            proposal=RouteProposal(
                scenario="dryrun_forbidden_reject_or_block",
                input_kind="certificate_request_with_forbidden_candidate",
                suggested_route="reject_or_block",
                confidence=0.86,
                required_guards=["AVF", "HardMask", "forbidden vector block"],
                forbidden_candidate_present=True,
            ),
            expected_route="proof_full_pipeline",
        ),
    ]


def _would_execute_route(scenario: DryRunScenario, validation_decision: str) -> str:
    if validation_decision in {"allow", "allow_with_guards"}:
        return scenario.proposal.suggested_route
    if validation_decision == "needs_user":
        return "needs_user"
    if validation_decision == "fallback_to_deterministic":
        return scenario.deterministic_fallback_route or scenario.expected_route
    return "blocked"


def _dry_run_result(scenario: DryRunScenario) -> DryRunResult:
    validation = validate_route_proposal(scenario.proposal)
    would_execute = _would_execute_route(scenario, validation.validation_decision)
    reason = validation.reason
    if scenario.proposal.scenario == "dryrun_direct_reuse_not_eligible_fallback":
        reason = "Direct reuse not eligible; deterministic fallback route would be used."
    if scenario.proposal.scenario == "dryrun_forbidden_reject_or_block":
        reason = "Safety block / no execution route for forbidden proposal."
    return DryRunResult(
        scenario=scenario.proposal.scenario,
        suggested_route=scenario.proposal.suggested_route,
        validation_decision=validation.validation_decision,
        allowed=validation.allowed,
        would_execute_route=would_execute,
        controlled_execution_performed=False,
        required_guards=validation.required_guards,
        violations=validation.violations,
        reason=reason,
    )


def _sanitize_output(output: str) -> str:
    sanitized = output
    for term in FORBIDDEN_OUTPUT_TERMS:
        sanitized = sanitized.replace(term, "[redacted]")
        sanitized = sanitized.replace(term.upper(), "[redacted]")
    return sanitized


def run_controlled_orchestrator_dry_run() -> str:
    results = [_dry_run_result(scenario) for scenario in _scenarios()]
    would_allowed = sum(
        result.validation_decision in {"allow", "allow_with_guards"}
        for result in results
    )
    would_needs_user = sum(result.would_execute_route == "needs_user" for result in results)
    would_fallback = sum(
        result.validation_decision == "fallback_to_deterministic"
        for result in results
    )
    would_block = sum(result.would_execute_route == "blocked" for result in results)

    lines = [
        "[CONTROLLED ORCHESTRATOR DRY-RUN]",
        "note: computes would_execute_route only",
        "note: does not execute Orchestrator-selected routes",
        "note: RootOrchestrator runtime is unchanged",
        "note: controlled_execution_performed: false",
        "note: no live Gemini by default",
        "",
        "scenario | suggested_route | validation_decision | allowed | would_execute_route | controlled_execution_performed | required_guards | violations | reason",
        "--- | --- | --- | --- | --- | --- | --- | --- | ---",
    ]
    for result in results:
        lines.append(
            " | ".join(
                [
                    result.scenario,
                    result.suggested_route,
                    result.validation_decision,
                    _bool_text(result.allowed),
                    result.would_execute_route,
                    _bool_text(result.controlled_execution_performed),
                    ",".join(result.required_guards) or "none",
                    ",".join(result.violations) or "none",
                    result.reason,
                ]
            )
        )
    lines.extend(
        [
            "",
            "SUMMARY:",
            f"would_execute_allowed: {would_allowed}",
            f"would_needs_user: {would_needs_user}",
            f"would_fallback: {would_fallback}",
            f"would_block: {would_block}",
            "controlled_execution_performed: false",
            "next_step: controlled Orchestrator requires runtime integration and additional safety review",
        ]
    )
    return _sanitize_output("\n".join(lines).rstrip() + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Render controlled Orchestrator dry-run.")
    parser.parse_args()
    print(run_controlled_orchestrator_dry_run(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
