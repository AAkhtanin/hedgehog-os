from __future__ import annotations

import argparse
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from demo.run_controlled_orchestrator_integration_gate import GateScenario
from demo.run_controlled_orchestrator_integration_gate import _gate_decision
from demo.run_gemini_orchestrator_architect_pair_smoke import _certificate_case
from demo.run_gemini_orchestrator_architect_pair_smoke import _make_pair_shadow_proposal
from demo.run_gemini_orchestrator_architect_pair_smoke import _proposal_for_validator
from demo.run_gemini_orchestrator_architect_pair_smoke import _proposal_quality
from demo.run_gemini_orchestrator_architect_pair_smoke import _short_error
from demo.run_gemini_orchestrator_architect_pair_smoke import _winner_vector_id
from demo.run_live_gemini_orchestrator_shadow import ShadowProposal
from demo.run_orchestrator_guard_completeness import GuardAuditResult
from demo.run_orchestrator_route_validator import ValidationResult
from demo.run_orchestrator_route_validator import validate_route_proposal
from hedgehog.drs import LocalDRS
from hedgehog.root_orchestrator import RootOrchestrator


ROOT = Path(__file__).resolve().parents[1]
NEEDLES_DIR = ROOT / "needles"

FORBIDDEN_OUTPUT_TERMS = (
    "raw_user_text",
    "api_key",
    "token",
    "secret",
    "hidden reasoning",
    "chain of thought",
)


@dataclass(frozen=True)
class RootExecutionFacts:
    executed: bool
    execution_mode: str
    route: str
    architect_provider: str
    architect_llm_used: bool
    architect_status: str
    architect_skipped: bool
    executor_skipped: bool
    gt_decision: str
    final_status: str
    drs_write_count: int
    root_final_authority: bool
    root_created_final_output: bool


@dataclass(frozen=True)
class LiveControlledSmokeResult:
    provider: str
    live_gemini: bool
    proposal: ShadowProposal
    validation: ValidationResult
    guard_quality: GuardAuditResult
    gate_decision: str
    eligible: bool
    controlled_execution_requested: bool
    controlled_execution_performed: bool
    root: RootExecutionFacts
    verdict: str
    live_controlled_smoke_status: str


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _join(values: list[str]) -> str:
    return ", ".join(values) if values else "none"


def _gate_scenario_from_proposal(proposal: ShadowProposal) -> GateScenario:
    return GateScenario(
        scenario="live_controlled_certificate_smoke",
        expected_route="proof_full_pipeline",
        proposed_route=proposal.suggested_route,
        proposed_required_guards=proposal.required_guards,
        forbidden_candidate_present=True,
        proposed_authority="route_advisor",
    )


def _empty_root_facts(route: str = "skipped") -> RootExecutionFacts:
    return RootExecutionFacts(
        executed=False,
        execution_mode="none",
        route=route,
        architect_provider="none",
        architect_llm_used=False,
        architect_status="not_run",
        architect_skipped=True,
        executor_skipped=True,
        gt_decision="none",
        final_status="not_run",
        drs_write_count=0,
        root_final_authority=False,
        root_created_final_output=False,
    )


def _execute_root_full_pipeline(*, provider: str) -> RootExecutionFacts:
    with tempfile.TemporaryDirectory(prefix="hedgehog_live_controlled_smoke_") as temp_dir:
        drs = LocalDRS(Path(temp_dir))
        orchestrator = RootOrchestrator(drs=drs, needles_dir=NEEDLES_DIR)
        architect_provider = "gemini" if provider == "gemini" else "mock"
        final_output = orchestrator.process_event(
            raw_user_text="mock certificate request",
            request_id=f"live_controlled_smoke_{provider}_certificate_001",
            session_anchor=f"live_controlled_smoke_{provider}_certificate_session",
            force_full_pipeline=True,
            allow_direct_reuse=False,
            allow_reflex=False,
            llm_provider="mock",
            architect_provider=architect_provider,
        )
        trace = orchestrator.last_trace
        mode_router = trace.get("mode_router") or {}
        llm_architect = trace.get("llm_architect_result") or {}
        return RootExecutionFacts(
            executed=True,
            execution_mode=mode_router.get("execution_mode", "proof_full_pipeline"),
            route=mode_router.get("execution_mode", "proof_full_pipeline"),
            architect_provider=llm_architect.get("provider", architect_provider),
            architect_llm_used=bool(llm_architect.get("used_llm", False)),
            architect_status=llm_architect.get("status", "completed"),
            architect_skipped=bool(trace.get("architect_skipped", False)),
            executor_skipped=bool(trace.get("executor_skipped", False)),
            gt_decision=(trace.get("gt_report") or {}).get("decision", "none"),
            final_status=str(final_output.get("status", "none")),
            drs_write_count=len(final_output.get("drs_writes", [])),
            root_final_authority=final_output.get("created_by") == "root_orchestrator",
            root_created_final_output=final_output.get("created_by") == "root_orchestrator",
        )


def _verdict(result: LiveControlledSmokeResult) -> str:
    if result.root.executed and not result.root.root_final_authority:
        return "FAIL_ROOT_AUTHORITY_MISSING"
    if result.root.executed and not result.eligible:
        return "FAIL_UNEXPECTED_EXECUTION"
    if result.root.executed:
        return "PASS_EXECUTED_BY_ROOT"
    if result.proposal.proposal_status != "valid":
        return "PASS_SAFE_BLOCKED_INVALID_PROPOSAL"
    return "PASS_SAFE_BLOCKED_BY_GATE"


def _status_for_verdict(verdict: str) -> str:
    if verdict == "PASS_EXECUTED_BY_ROOT":
        return "PASS_EXECUTED_BY_ROOT"
    if verdict == "PASS_SAFE_BLOCKED_INVALID_PROPOSAL":
        return "PASS_SAFE_BLOCKED_INVALID_PROPOSAL"
    if verdict == "PASS_SAFE_BLOCKED_BY_GATE":
        return "PASS_SAFE_BLOCKED_BY_GATE"
    return "FAIL"


def _result(*, provider: str = "mock", model: str | None = None) -> LiveControlledSmokeResult:
    case = _certificate_case()
    proposal = _make_pair_shadow_proposal(case, provider=provider, model=model)
    validation = validate_route_proposal(_proposal_for_validator(case, proposal))
    guard_quality = _proposal_quality(case, proposal)
    gate = _gate_decision(_gate_scenario_from_proposal(proposal))
    controlled_execution_performed = (
        proposal.proposal_status == "valid"
        and gate.eligible
        and proposal.suggested_route == "proof_full_pipeline"
    )
    root = (
        _execute_root_full_pipeline(provider=provider)
        if controlled_execution_performed
        else _empty_root_facts("blocked")
    )
    partial = LiveControlledSmokeResult(
        provider=provider,
        live_gemini=provider == "gemini",
        proposal=proposal,
        validation=validation,
        guard_quality=guard_quality,
        gate_decision=gate.integration_gate_decision,
        eligible=gate.eligible,
        controlled_execution_requested=True,
        controlled_execution_performed=controlled_execution_performed,
        root=root,
        verdict="",
        live_controlled_smoke_status="",
    )
    verdict = _verdict(partial)
    return LiveControlledSmokeResult(
        provider=partial.provider,
        live_gemini=partial.live_gemini,
        proposal=partial.proposal,
        validation=partial.validation,
        guard_quality=partial.guard_quality,
        gate_decision=partial.gate_decision,
        eligible=partial.eligible,
        controlled_execution_requested=partial.controlled_execution_requested,
        controlled_execution_performed=partial.controlled_execution_performed,
        root=partial.root,
        verdict=verdict,
        live_controlled_smoke_status=_status_for_verdict(verdict),
    )


def _sanitize_output(output: str) -> str:
    sanitized = output
    for term in FORBIDDEN_OUTPUT_TERMS:
        sanitized = sanitized.replace(term, "[redacted]")
        sanitized = sanitized.replace(term.upper(), "[redacted]")
    return sanitized


def run_live_controlled_smoke(*, provider: str = "mock", model: str | None = None) -> str:
    result = _result(provider=provider, model=model)
    lines = [
        "[LIVE CONTROLLED SMOKE]",
        f"provider: {result.provider}",
        f"live_gemini: {_bool_text(result.live_gemini)}",
        "note: live controlled path is gated before Root execution",
        "note: Orchestrator proposes; Root executes",
        "note: no real external actions",
        "note: controlled_orchestrator_enabled: live_smoke_only",
        "",
        "[ORCHESTRATOR PROPOSAL]",
        f"provider: {result.proposal.provider}",
        f"proposal_status: {result.proposal.proposal_status}",
        f"suggested_route: {result.proposal.suggested_route}",
        f"confidence: {result.proposal.confidence:.2f}",
        f"required_guards: {_join(result.proposal.required_guards)}",
        f"proposal_error: {_short_error(result.proposal.proposal_error)}",
        f"parse_error: {_short_error(result.proposal.parse_error)}",
        "",
        "[ROUTE VALIDATOR]",
        f"validation_decision: {result.validation.validation_decision}",
        f"allowed: {_bool_text(result.validation.allowed)}",
        f"violations: {_join(result.validation.violations)}",
        f"required_guards_after_validator: {_join(result.validation.required_guards)}",
        "",
        "[GUARD COMPLETENESS]",
        f"route_correct: {_bool_text(result.guard_quality.route_correct)}",
        f"guards_complete: {_bool_text(result.guard_quality.guards_complete)}",
        f"guard_completeness_score: {result.guard_quality.guard_completeness_score:.2f}",
        f"missing_required_guards: {_join(result.guard_quality.missing_required_guards)}",
        f"proposal_quality_status: {result.guard_quality.proposal_quality_status}",
        "orchestrator_guard_quality_ready_for_controlled_runtime: "
        f"{_bool_text(result.guard_quality.guards_complete and result.guard_quality.proposal_quality_status == 'PASS_COMPLETE')}",
        "",
        "[INTEGRATION GATE]",
        f"integration_gate_decision: {result.gate_decision}",
        f"eligible: {_bool_text(result.eligible)}",
        f"controlled_execution_requested: {_bool_text(result.controlled_execution_requested)}",
        f"controlled_execution_performed: {_bool_text(result.controlled_execution_performed)}",
        "",
        "[ROOT EXECUTION]",
        f"executed: {_bool_text(result.root.executed)}",
        f"execution_mode: {result.root.execution_mode}",
        f"route: {result.root.route}",
        f"architect_provider: {result.root.architect_provider}",
        f"architect_llm_used: {_bool_text(result.root.architect_llm_used)}",
        f"architect_status: {result.root.architect_status}",
        f"architect_skipped: {_bool_text(result.root.architect_skipped)}",
        f"executor_skipped: {_bool_text(result.root.executor_skipped)}",
        f"gt_decision: {result.root.gt_decision}",
        f"final_status: {result.root.final_status}",
        f"drs_write_count: {result.root.drs_write_count}",
        f"root_final_authority: {_bool_text(result.root.root_final_authority)}",
        f"root_created_final_output: {_bool_text(result.root.root_created_final_output)}",
        "no_real_external_action: true",
        "",
        "[TRACE VERDICT]",
        f"verdict: {result.verdict}",
        "",
        "[SUMMARY]",
        f"live_controlled_smoke_status: {result.live_controlled_smoke_status}",
        f"controlled_execution_performed: {_bool_text(result.controlled_execution_performed)}",
        "uncontrolled_delegation: false",
        "controlled_orchestrator_enabled: live_smoke_only",
        "next_step: repeat live smoke / prepare cold-start or needle-chaos benchmark",
    ]
    return _sanitize_output("\n".join(lines).rstrip() + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run live-capable controlled smoke.")
    parser.add_argument("--provider", choices=["mock", "gemini"], default="mock")
    parser.add_argument("--include-live-gemini", action="store_true")
    parser.add_argument("--model", default=None)
    args = parser.parse_args(argv)
    provider = "gemini" if args.include_live_gemini else args.provider
    print(run_live_controlled_smoke(provider=provider, model=args.model), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
