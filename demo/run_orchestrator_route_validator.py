from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Any


FORBIDDEN_OUTPUT_TERMS = (
    "raw_user_text",
    "api_key",
    "token",
    "secret",
    "hidden reasoning",
    "chain of thought",
)


@dataclass(frozen=True)
class RouteProposal:
    scenario: str
    input_kind: str
    suggested_route: str
    confidence: float
    required_guards: list[str]
    proposed_authority: str = "route_advisor"
    uses_live_llm: bool = False
    wants_direct_action: bool = False
    wants_direct_reuse: bool = False
    wants_skip_avf: bool = False
    wants_skip_plan_contract: bool = False
    wants_final_output: bool = False
    permission_confirmed: bool = False
    direct_reuse_eligible: bool = False
    forbidden_candidate_present: bool = False
    protocol_mock_only: bool = True
    budget_class: str = "low"


@dataclass(frozen=True)
class ValidationResult:
    scenario: str
    suggested_route: str
    validation_decision: str
    allowed: bool
    required_guards: list[str]
    violations: list[str]
    reason: str


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _merge_guards(*guard_lists: list[str]) -> list[str]:
    guards: list[str] = []
    for guard_list in guard_lists:
        for guard in guard_list:
            if guard not in guards:
                guards.append(guard)
    return guards


def validate_route_proposal(proposal: RouteProposal) -> ValidationResult:
    guards = _merge_guards(proposal.required_guards, ["Root final authority"])
    violations: list[str] = []

    if proposal.wants_final_output or proposal.proposed_authority == "orchestrator":
        violations.append("orchestrator_cannot_create_final_output")

    if proposal.wants_skip_avf and proposal.forbidden_candidate_present:
        violations.append("cannot_skip_avf_when_forbidden_candidate_present")

    if proposal.wants_skip_plan_contract:
        violations.append("cannot_skip_plan_graph_contract")

    if proposal.wants_direct_reuse and not proposal.direct_reuse_eligible:
        violations.append("direct_reuse_requires_eligible_record")

    if proposal.wants_direct_action and not proposal.permission_confirmed:
        guards = _merge_guards(guards, ["PermissionGate", "no real external action", "audit"])
        return ValidationResult(
            scenario=proposal.scenario,
            suggested_route=proposal.suggested_route,
            validation_decision="needs_user",
            allowed=False,
            required_guards=guards,
            violations=["permission_required"],
            reason="Actionful route requires user confirmation before execution.",
        )

    if violations:
        decision = (
            "fallback_to_deterministic"
            if violations == ["direct_reuse_requires_eligible_record"]
            else "deny"
        )
        return ValidationResult(
            scenario=proposal.scenario,
            suggested_route=proposal.suggested_route,
            validation_decision=decision,
            allowed=False,
            required_guards=guards,
            violations=violations,
            reason="Route proposal violates required Hedgehog OS execution guards.",
        )

    if proposal.suggested_route == "deterministic_reflex" and not proposal.wants_direct_action:
        guards = _merge_guards(guards, ["audit", "DRS writeback"])
        return ValidationResult(
            scenario=proposal.scenario,
            suggested_route=proposal.suggested_route,
            validation_decision="allow",
            allowed=True,
            required_guards=guards,
            violations=[],
            reason="Low-risk deterministic reflex route can be advised under Root authority.",
        )

    if proposal.suggested_route == "llm_general":
        guards = _merge_guards(guards, ["no external action", "budget check"])
        return ValidationResult(
            scenario=proposal.scenario,
            suggested_route=proposal.suggested_route,
            validation_decision="allow_with_guards",
            allowed=True,
            required_guards=guards,
            violations=[],
            reason="General responder route is allowed only as subordinate answer drafting.",
        )

    if proposal.suggested_route == "proof_full_pipeline":
        guards = _merge_guards(
            guards,
            ["AVF", "HardMask", "PlanGraph contract", "Post V&V", "GT"],
        )
        return ValidationResult(
            scenario=proposal.scenario,
            suggested_route=proposal.suggested_route,
            validation_decision="allow_with_guards",
            allowed=True,
            required_guards=guards,
            violations=[],
            reason="Full pipeline route is allowed with AVF, contract validation, V&V, and GT.",
        )

    if proposal.wants_direct_action and proposal.permission_confirmed:
        guards = _merge_guards(guards, ["PermissionGate", "no real external action", "audit"])
        return ValidationResult(
            scenario=proposal.scenario,
            suggested_route=proposal.suggested_route,
            validation_decision="allow_with_guards",
            allowed=True,
            required_guards=guards,
            violations=[],
            reason="Confirmed mock action may proceed only under permission and audit guards.",
        )

    if proposal.wants_direct_reuse and proposal.direct_reuse_eligible:
        guards = _merge_guards(
            guards,
            ["DirectReuseGate", "Freshness", "PolicyOK", "DRS writeback"],
        )
        return ValidationResult(
            scenario=proposal.scenario,
            suggested_route=proposal.suggested_route,
            validation_decision="allow_with_guards",
            allowed=True,
            required_guards=guards,
            violations=[],
            reason="Direct reuse route is allowed only with eligible memory and writeback.",
        )

    return ValidationResult(
        scenario=proposal.scenario,
        suggested_route=proposal.suggested_route,
        validation_decision="deny",
        allowed=False,
        required_guards=guards,
        violations=["unsupported_route_proposal"],
        reason="Route proposal is not yet supported by the validator.",
    )


def _proposals() -> list[RouteProposal]:
    return [
        RouteProposal(
            scenario="validator_allows_reflex_route",
            input_kind="simple_device_command",
            suggested_route="deterministic_reflex",
            confidence=0.96,
            required_guards=["audit", "DRS writeback"],
        ),
        RouteProposal(
            scenario="validator_allows_general_route",
            input_kind="general_explanation_request",
            suggested_route="llm_general",
            confidence=0.91,
            required_guards=["Root final authority", "no external action", "budget check"],
            budget_class="low",
        ),
        RouteProposal(
            scenario="validator_allows_full_pipeline_with_guards",
            input_kind="certificate_request",
            suggested_route="proof_full_pipeline",
            confidence=0.88,
            required_guards=["AVF", "HardMask", "PlanGraph contract", "Post V&V", "GT"],
            forbidden_candidate_present=True,
        ),
        RouteProposal(
            scenario="validator_blocks_skip_avf",
            input_kind="certificate_request_with_forbidden_candidate",
            suggested_route="proof_full_pipeline",
            confidence=0.75,
            required_guards=["PlanGraph contract"],
            forbidden_candidate_present=True,
            wants_skip_avf=True,
        ),
        RouteProposal(
            scenario="validator_blocks_skip_plan_contract",
            input_kind="certificate_request",
            suggested_route="proof_full_pipeline",
            confidence=0.75,
            required_guards=["AVF", "HardMask"],
            wants_skip_plan_contract=True,
        ),
        RouteProposal(
            scenario="validator_blocks_orchestrator_final_output",
            input_kind="general_explanation_request",
            suggested_route="llm_general",
            confidence=0.8,
            required_guards=["Root final authority"],
            proposed_authority="orchestrator",
            wants_final_output=True,
        ),
        RouteProposal(
            scenario="validator_requires_permission_for_purchase",
            input_kind="permissioned_mock_purchase",
            suggested_route="permission_required",
            confidence=0.94,
            required_guards=["PermissionGate"],
            wants_direct_action=True,
            permission_confirmed=False,
        ),
        RouteProposal(
            scenario="validator_allows_permission_after_confirmation_mock",
            input_kind="permissioned_mock_purchase",
            suggested_route="deterministic_reflex",
            confidence=0.92,
            required_guards=["PermissionGate", "audit"],
            wants_direct_action=True,
            permission_confirmed=True,
            protocol_mock_only=True,
        ),
        RouteProposal(
            scenario="validator_blocks_direct_reuse_without_gate",
            input_kind="repeated_certificate_request",
            suggested_route="direct_reuse",
            confidence=0.82,
            required_guards=["DirectReuseGate"],
            wants_direct_reuse=True,
            direct_reuse_eligible=False,
        ),
        RouteProposal(
            scenario="validator_allows_direct_reuse_when_eligible",
            input_kind="repeated_certificate_request",
            suggested_route="direct_reuse",
            confidence=0.9,
            required_guards=["DirectReuseGate", "Freshness", "PolicyOK", "DRS writeback"],
            wants_direct_reuse=True,
            direct_reuse_eligible=True,
        ),
    ]


def _sanitize_output(output: str) -> str:
    sanitized = output
    for term in FORBIDDEN_OUTPUT_TERMS:
        sanitized = sanitized.replace(term, "[redacted]")
        sanitized = sanitized.replace(term.upper(), "[redacted]")
    return sanitized


def run_orchestrator_route_validator() -> str:
    results = [validate_route_proposal(proposal) for proposal in _proposals()]
    counts = {
        "allow": sum(result.validation_decision == "allow" for result in results),
        "allow_with_guards": sum(result.validation_decision == "allow_with_guards" for result in results),
        "deny": sum(result.validation_decision == "deny" for result in results),
        "needs_user": sum(result.validation_decision == "needs_user" for result in results),
        "fallback_to_deterministic": sum(result.validation_decision == "fallback_to_deterministic" for result in results),
    }
    lines = [
        "[ORCHESTRATOR ROUTE VALIDATOR]",
        "note: validates shadow route proposals before any future controlled Orchestrator execution",
        "note: this does not delegate control yet",
        "note: no live Gemini by default",
        "",
        "scenario | suggested_route | validation_decision | allowed | required_guards | violations | reason",
        "--- | --- | --- | --- | --- | --- | ---",
    ]
    for result in results:
        lines.append(
            " | ".join(
                [
                    result.scenario,
                    result.suggested_route,
                    result.validation_decision,
                    _bool_text(result.allowed),
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
            f"allowed: {counts['allow']}",
            f"allowed_with_guards: {counts['allow_with_guards']}",
            f"denied: {counts['deny']}",
            f"needs_user: {counts['needs_user']}",
            f"fallback_to_deterministic: {counts['fallback_to_deterministic']}",
            "controlled_orchestrator_enabled: false",
            "next_step: controlled orchestrator only after validator enforcement",
        ]
    )
    return _sanitize_output("\n".join(lines).rstrip() + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate mock Orchestrator route proposals.")
    parser.parse_args()
    print(run_orchestrator_route_validator(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
