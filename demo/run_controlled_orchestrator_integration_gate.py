from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Any

from demo.run_orchestrator_guard_completeness import GuardScenario
from demo.run_orchestrator_guard_completeness import audit_guard_scenario
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
class GateScenario:
    scenario: str
    expected_route: str
    proposed_route: str
    proposed_required_guards: list[str]
    controlled_execution_requested: bool = True
    root_final_authority_present: bool = True
    permission_confirmed: bool = True
    direct_reuse_eligible: bool = False
    no_real_external_action: bool = True
    proposed_authority: str = "route_advisor"
    wants_final_output: bool = False
    wants_direct_action: bool = False
    wants_direct_reuse: bool = False
    wants_skip_avf: bool = False
    wants_skip_plan_contract: bool = False
    forbidden_candidate_present: bool = False


@dataclass(frozen=True)
class GateResult:
    scenario: str
    proposed_route: str
    validation_decision: str
    route_correct: bool
    guards_complete: bool
    guard_completeness_score: float
    root_final_authority_present: bool
    integration_gate_decision: str
    eligible: bool
    controlled_execution_performed: bool
    reason: str


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _validator_result(scenario: GateScenario):
    return validate_route_proposal(
        RouteProposal(
            scenario=scenario.scenario,
            input_kind="controlled_orchestrator_integration_gate",
            suggested_route=scenario.proposed_route,
            confidence=0.9,
            required_guards=scenario.proposed_required_guards,
            proposed_authority=scenario.proposed_authority,
            wants_direct_action=scenario.wants_direct_action,
            wants_direct_reuse=scenario.wants_direct_reuse,
            wants_skip_avf=scenario.wants_skip_avf,
            wants_skip_plan_contract=scenario.wants_skip_plan_contract,
            wants_final_output=scenario.wants_final_output,
            permission_confirmed=scenario.permission_confirmed,
            direct_reuse_eligible=scenario.direct_reuse_eligible,
            forbidden_candidate_present=scenario.forbidden_candidate_present,
        )
    )


def _guard_result(scenario: GateScenario):
    return audit_guard_scenario(
        GuardScenario(
            scenario=scenario.scenario,
            expected_route=scenario.expected_route,
            proposed_route=scenario.proposed_route,
            proposed_required_guards=scenario.proposed_required_guards,
            wants_direct_reuse=scenario.wants_direct_reuse,
            direct_reuse_eligible=scenario.direct_reuse_eligible,
            wants_direct_action=scenario.wants_direct_action,
            permission_confirmed=scenario.permission_confirmed,
            forbidden_candidate_present=scenario.forbidden_candidate_present,
        )
    )


def _gate_decision(scenario: GateScenario) -> GateResult:
    validator = _validator_result(scenario)
    guard = _guard_result(scenario)

    decision = "eligible_for_controlled_dry_run"
    reason = "Proposal passes route, validator, guard, and authority gates."

    if not guard.route_correct:
        decision = "not_eligible_route_mismatch"
        reason = "Proposed route does not match expected deterministic route."
    elif scenario.proposed_authority == "orchestrator" or scenario.wants_final_output:
        decision = "not_eligible_orchestrator_final_output"
        reason = "Orchestrator may not create FinalOutput or become final authority."
    elif not scenario.root_final_authority_present:
        decision = "not_eligible_missing_root_authority"
        reason = "Root final authority guard is missing."
    elif not scenario.no_real_external_action:
        decision = "not_eligible_external_action_risk"
        reason = "Proposal includes real external action risk."
    elif validator.validation_decision == "needs_user":
        decision = "not_eligible_needs_user"
        reason = "Proposal needs user confirmation before controlled dry-run eligibility."
    elif scenario.proposed_route == "direct_reuse" and not scenario.direct_reuse_eligible:
        decision = "not_eligible_validator_denied"
        reason = "Direct reuse requires an eligible trusted memory record."
    elif not validator.allowed or validator.validation_decision not in {"allow", "allow_with_guards"}:
        decision = "not_eligible_validator_denied"
        reason = "Route Validator did not allow the proposal."
    elif not guard.guards_complete or guard.guard_completeness_score < 1.0:
        decision = "not_eligible_incomplete_guards"
        reason = "Proposal route is correct but required guards are incomplete."
    elif guard.proposal_quality_status != "PASS_COMPLETE":
        decision = "not_eligible_incomplete_guards"
        reason = "Proposal quality status is not PASS_COMPLETE."
    elif scenario.proposed_route in {"permission_required", "needs_user"} and not scenario.permission_confirmed:
        decision = "not_eligible_needs_user"
        reason = "Actionful route requires confirmation before eligibility."

    return GateResult(
        scenario=scenario.scenario,
        proposed_route=scenario.proposed_route,
        validation_decision=validator.validation_decision,
        route_correct=guard.route_correct,
        guards_complete=guard.guards_complete,
        guard_completeness_score=guard.guard_completeness_score,
        root_final_authority_present=scenario.root_final_authority_present,
        integration_gate_decision=decision,
        eligible=decision == "eligible_for_controlled_dry_run",
        controlled_execution_performed=False,
        reason=reason,
    )


def _scenarios() -> list[GateScenario]:
    return [
        GateScenario(
            scenario="gate_full_pipeline_complete_eligible",
            expected_route="proof_full_pipeline",
            proposed_route="proof_full_pipeline",
            proposed_required_guards=[
                "AVF",
                "HardMask",
                "PlanGraph contract",
                "Post V&V",
                "GT",
                "Root final authority",
            ],
            forbidden_candidate_present=True,
        ),
        GateScenario(
            scenario="gate_full_pipeline_incomplete_guards_not_eligible",
            expected_route="proof_full_pipeline",
            proposed_route="proof_full_pipeline",
            proposed_required_guards=["AVF", "PlanGraph"],
            forbidden_candidate_present=True,
        ),
        GateScenario(
            scenario="gate_wrong_route_not_eligible",
            expected_route="proof_full_pipeline",
            proposed_route="llm_general",
            proposed_required_guards=["Root final authority", "no external action", "budget check"],
        ),
        GateScenario(
            scenario="gate_validator_denied_not_eligible",
            expected_route="proof_full_pipeline",
            proposed_route="proof_full_pipeline",
            proposed_required_guards=["PlanGraph contract"],
            wants_skip_avf=True,
            forbidden_candidate_present=True,
        ),
        GateScenario(
            scenario="gate_needs_user_not_eligible",
            expected_route="permission_required",
            proposed_route="permission_required",
            proposed_required_guards=[
                "PermissionGate",
                "Root final authority",
                "no real external action",
                "audit",
            ],
            wants_direct_action=True,
            permission_confirmed=False,
        ),
        GateScenario(
            scenario="gate_missing_root_authority_not_eligible",
            expected_route="proof_full_pipeline",
            proposed_route="proof_full_pipeline",
            proposed_required_guards=[
                "AVF",
                "HardMask",
                "PlanGraph contract",
                "Post V&V",
                "GT",
                "Root final authority",
            ],
            root_final_authority_present=False,
            forbidden_candidate_present=True,
        ),
        GateScenario(
            scenario="gate_orchestrator_final_output_not_eligible",
            expected_route="llm_general",
            proposed_route="llm_general",
            proposed_required_guards=["Root final authority", "no external action", "budget check"],
            proposed_authority="orchestrator",
            wants_final_output=True,
        ),
        GateScenario(
            scenario="gate_direct_reuse_eligible",
            expected_route="direct_reuse",
            proposed_route="direct_reuse",
            proposed_required_guards=[
                "DirectReuseGate",
                "Freshness",
                "PolicyOK",
                "DRS writeback",
                "Root final authority",
            ],
            wants_direct_reuse=True,
            direct_reuse_eligible=True,
        ),
        GateScenario(
            scenario="gate_direct_reuse_not_eligible",
            expected_route="direct_reuse",
            proposed_route="direct_reuse",
            proposed_required_guards=[
                "DirectReuseGate",
                "Freshness",
                "PolicyOK",
                "DRS writeback",
                "Root final authority",
            ],
            wants_direct_reuse=True,
            direct_reuse_eligible=False,
        ),
    ]


def _sanitize_output(output: str) -> str:
    sanitized = output
    for term in FORBIDDEN_OUTPUT_TERMS:
        sanitized = sanitized.replace(term, "[redacted]")
        sanitized = sanitized.replace(term.upper(), "[redacted]")
    return sanitized


def run_controlled_orchestrator_integration_gate() -> str:
    results = [_gate_decision(scenario) for scenario in _scenarios()]
    eligible = sum(result.eligible for result in results)
    not_eligible = len(results) - eligible

    lines = [
        "[CONTROLLED ORCHESTRATOR INTEGRATION GATE]",
        "note: this decides eligibility for future controlled execution",
        "note: it does not execute controlled Orchestrator routes",
        "note: RootOrchestrator runtime is unchanged",
        "note: controlled_execution_performed: false",
        "note: no live Gemini by default",
        "",
        "scenario | proposed_route | validation_decision | route_correct | guards_complete | guard_completeness_score | root_final_authority_present | integration_gate_decision | eligible | controlled_execution_performed | reason",
        "--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---",
    ]
    for result in results:
        lines.append(
            " | ".join(
                [
                    result.scenario,
                    result.proposed_route,
                    result.validation_decision,
                    _bool_text(result.route_correct),
                    _bool_text(result.guards_complete),
                    f"{result.guard_completeness_score:.2f}",
                    _bool_text(result.root_final_authority_present),
                    result.integration_gate_decision,
                    _bool_text(result.eligible),
                    _bool_text(result.controlled_execution_performed),
                    result.reason,
                ]
            )
        )
    lines.extend(
        [
            "",
            "SUMMARY:",
            f"eligible: {eligible}",
            f"not_eligible: {not_eligible}",
            "controlled_execution_performed: false",
            "controlled_orchestrator_enabled: false",
            "next_step: controlled runtime only after explicit integration",
        ]
    )
    return _sanitize_output("\n".join(lines).rstrip() + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run controlled Orchestrator integration gate audit.")
    parser.parse_args()
    print(run_controlled_orchestrator_integration_gate(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
