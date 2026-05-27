from __future__ import annotations

import argparse
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from demo.run_live_gemini_orchestrator_shadow import ShadowCase
from demo.run_live_gemini_orchestrator_shadow import ShadowProposal
from demo.run_live_gemini_orchestrator_shadow import make_shadow_proposal
from demo.run_orchestrator_route_validator import RouteProposal
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
class PairSmokeResult:
    provider: str
    live_gemini: bool
    proposal: ShadowProposal
    validation: ValidationResult
    would_execute_route: str
    executed: bool
    execution_mode: str
    route: str
    architect_provider: str
    architect_llm_used: bool
    architect_status: str
    architect_fallback: str
    architect_error: str
    architect_skipped: bool
    executor_skipped: bool
    gt_decision: str
    final_status: str
    drs_write_count: int
    trace_path_present: bool
    gt_winner_vector: str
    plan_graph_node_count: int
    accepted_branch_count: int
    pair_smoke_status: str


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _certificate_case() -> ShadowCase:
    return ShadowCase(
        scenario="pair_certificate_full_pipeline",
        input_kind="certificate_request",
        input_text="mock certificate request",
        expected_route="proof_full_pipeline",
        forbidden_candidate_present=True,
    )


def _make_pair_shadow_proposal(
    case: ShadowCase,
    *,
    provider: str,
    model: str | None,
) -> ShadowProposal:
    if provider == "mock":
        return ShadowProposal(
            proposal_status="valid",
            suggested_route="proof_full_pipeline",
            confidence=0.88,
            reason="certificate request needs bounded full-pipeline planning",
            required_guards=[
                "AVF",
                "HardMask",
                "PlanGraph contract",
                "Post V&V",
                "GT",
                "Root final authority",
            ],
            shadow_only=True,
            provider="mock",
        )

    gemini_case = ShadowCase(
        scenario="live_shadow_certificate_request",
        input_kind=case.input_kind,
        input_text=case.input_text,
        expected_route=case.expected_route,
        forbidden_candidate_present=case.forbidden_candidate_present,
    )
    return make_shadow_proposal(gemini_case, provider=provider, model=model)


def _proposal_for_validator(case: ShadowCase, proposal: ShadowProposal) -> RouteProposal:
    return RouteProposal(
        scenario=case.scenario,
        input_kind=case.input_kind,
        suggested_route=proposal.suggested_route,
        confidence=proposal.confidence,
        required_guards=proposal.required_guards,
        proposed_authority="route_advisor",
        uses_live_llm=proposal.provider == "gemini" and proposal.proposal_status == "valid",
        wants_direct_action=False,
        wants_direct_reuse=False,
        wants_skip_avf=False,
        wants_skip_plan_contract=False,
        wants_final_output=False,
        permission_confirmed=False,
        direct_reuse_eligible=False,
        forbidden_candidate_present=case.forbidden_candidate_present,
        budget_class="normal",
    )


def _would_execute_route(validation: ValidationResult) -> str:
    if validation.validation_decision in {"allow", "allow_with_guards"}:
        return validation.suggested_route
    if validation.validation_decision == "needs_user":
        return "needs_user"
    if validation.validation_decision == "fallback_to_deterministic":
        return "proof_full_pipeline"
    return "blocked"


def _winner_vector_id(trace: dict) -> str:
    gt_report = trace.get("gt_report") or {}
    winner = gt_report.get("winner")
    if not winner:
        return "none"
    for proposal in trace.get("result_proposals") or []:
        if proposal.get("proposal_id") == winner:
            return proposal.get("vector_id", "none")
    return "none"


def _short_error(value: str | None, limit: int = 180) -> str:
    if not value:
        return "none"
    text = " ".join(str(value).split())
    if len(text) <= limit:
        return text
    return f"{text[: limit - 3]}..."


def _execution_facts(
    *,
    provider: str,
    would_execute_route: str,
    validation: ValidationResult,
) -> dict:
    if would_execute_route != "proof_full_pipeline" or not validation.allowed:
        return {
            "executed": False,
            "execution_mode": "none",
            "route": would_execute_route,
            "architect_provider": "none",
            "architect_llm_used": False,
            "architect_status": "not_run",
            "architect_fallback": "none",
            "architect_error": "none",
            "architect_skipped": True,
            "executor_skipped": True,
            "gt_decision": "none",
            "final_status": "not_run",
            "drs_write_count": 0,
            "trace_path_present": False,
            "gt_winner_vector": "none",
            "plan_graph_node_count": 0,
            "accepted_branch_count": 0,
        }

    with tempfile.TemporaryDirectory(prefix="hedgehog_pair_smoke_drs_") as temp_dir:
        drs = LocalDRS(Path(temp_dir))
        orchestrator = RootOrchestrator(drs=drs, needles_dir=NEEDLES_DIR)
        architect_provider = "gemini" if provider == "gemini" else "mock"
        final_output = orchestrator.process_event(
            raw_user_text="mock certificate request",
            request_id=f"pair_smoke_{provider}_certificate_001",
            session_anchor=f"pair_smoke_{provider}_certificate_session",
            force_full_pipeline=True,
            allow_direct_reuse=False,
            allow_reflex=False,
            llm_provider="mock",
            architect_provider=architect_provider,
        )
        trace = orchestrator.last_trace
        mode_router = trace.get("mode_router") or {}
        llm_architect = trace.get("llm_architect_result") or {}
        plan_graph = trace.get("plan_graph") or {}
        vv_reports = trace.get("vv_reports") or []
        final_draft = trace.get("final_draft_proposal") or {}
        return {
            "executed": True,
            "execution_mode": mode_router.get("execution_mode", "proof_full_pipeline"),
            "route": mode_router.get("execution_mode", "proof_full_pipeline"),
            "architect_provider": llm_architect.get("provider", architect_provider),
            "architect_llm_used": bool(llm_architect.get("used_llm", False)),
            "architect_status": llm_architect.get("status", "completed"),
            "architect_fallback": llm_architect.get("fallback", "none"),
            "architect_error": _short_error(llm_architect.get("error")),
            "architect_skipped": False,
            "executor_skipped": False,
            "gt_decision": (trace.get("gt_report") or {}).get("decision", "none"),
            "final_status": final_output.get("status", "none"),
            "drs_write_count": len(final_output.get("drs_writes", [])),
            "trace_path_present": False,
            "gt_winner_vector": _winner_vector_id(trace),
            "plan_graph_node_count": len(plan_graph.get("nodes") or []),
            "accepted_branch_count": len(final_draft.get("completed_proposal_ids") or [
                report for report in vv_reports if report.get("decision") == "accept"
            ]),
        }


def _pair_smoke_result(*, provider: str, model: str | None = None) -> PairSmokeResult:
    case = _certificate_case()
    proposal = _make_pair_shadow_proposal(case, provider=provider, model=model)
    validation = validate_route_proposal(_proposal_for_validator(case, proposal))
    would_execute_route = _would_execute_route(validation)
    execution = _execution_facts(
        provider=provider,
        would_execute_route=would_execute_route,
        validation=validation,
    )
    pair_pass = (
        proposal.proposal_status == "valid"
        and validation.validation_decision == "allow_with_guards"
        and would_execute_route == "proof_full_pipeline"
        and execution["executed"]
        and execution["final_status"] == "success"
        and execution["gt_decision"] == "accept"
    )
    if provider == "gemini" and proposal.proposal_status != "valid":
        pair_pass = not execution["executed"] and would_execute_route in {
            "blocked",
            "needs_user",
        }
    elif provider == "gemini" and not validation.allowed:
        pair_pass = not execution["executed"]
    return PairSmokeResult(
        provider=provider,
        live_gemini=provider == "gemini",
        proposal=proposal,
        validation=validation,
        would_execute_route=would_execute_route,
        pair_smoke_status="PASS" if pair_pass else "FAIL",
        **execution,
    )


def _sanitize_output(output: str) -> str:
    sanitized = output
    for term in FORBIDDEN_OUTPUT_TERMS:
        sanitized = sanitized.replace(term, "[redacted]")
        sanitized = sanitized.replace(term.upper(), "[redacted]")
    return sanitized


def run_gemini_orchestrator_architect_pair_smoke(
    *,
    provider: str = "mock",
    model: str | None = None,
) -> str:
    result = _pair_smoke_result(provider=provider, model=model)
    route_match_status = (
        "MATCH"
        if result.proposal.suggested_route == "proof_full_pipeline"
        else "GUARDED_NON_EXECUTION"
    )
    lines = [
        "[GEMINI ORCHESTRATOR + ARCHITECT PAIR SMOKE]",
        f"provider: {result.provider}",
        f"live_gemini: {_bool_text(result.live_gemini)}",
        "note: Orchestrator proposal is validated before execution",
        "note: Root executes approved equivalent route",
        "note: Gemini Orchestrator does not directly control runtime",
        "note: no real external actions",
        "",
        "[ORCHESTRATOR PROPOSAL]",
        f"provider: {result.proposal.provider}",
        f"proposal_status: {result.proposal.proposal_status}",
        f"orchestrator_proposal_valid: {_bool_text(result.proposal.proposal_status == 'valid')}",
        f"suggested_route: {result.proposal.suggested_route}",
        f"confidence: {result.proposal.confidence:.2f}",
        f"required_guards: {', '.join(result.proposal.required_guards) or 'none'}",
        f"route_match_status: {route_match_status}",
        f"proposal_error: {result.proposal.proposal_error}",
        f"parse_error: {result.proposal.parse_error}",
        f"raw_response_preview: {result.proposal.raw_response_preview}",
        f"reason: {result.proposal.reason}",
        "",
        "[ROUTE VALIDATION]",
        f"validation_decision: {result.validation.validation_decision}",
        f"allowed: {_bool_text(result.validation.allowed)}",
        f"route_validator_allowed: {_bool_text(result.validation.allowed)}",
        f"violations: {', '.join(result.validation.violations) or 'none'}",
        f"required_guards: {', '.join(result.validation.required_guards) or 'none'}",
        f"would_execute_route: {result.would_execute_route}",
        "",
        "[ROOT EXECUTION]",
        f"executed: {_bool_text(result.executed)}",
        f"live_pair_executed: {_bool_text(result.live_gemini and result.executed)}",
        f"architect_invoked: {_bool_text(result.executed and not result.architect_skipped)}",
        f"execution_mode: {result.execution_mode}",
        f"route: {result.route}",
        f"architect_provider: {result.architect_provider}",
        f"architect_llm_used: {_bool_text(result.architect_llm_used)}",
        f"architect_status: {result.architect_status}",
        f"architect_fallback: {result.architect_fallback}",
        f"architect_error: {result.architect_error}",
        f"architect_skipped: {_bool_text(result.architect_skipped)}",
        f"executor_skipped: {_bool_text(result.executor_skipped)}",
        f"gt_decision: {result.gt_decision}",
        f"final_status: {result.final_status}",
        f"drs_write_count: {result.drs_write_count}",
        f"trace_path_present: {_bool_text(result.trace_path_present)}",
        f"gt_winner_vector: {result.gt_winner_vector}",
        f"plan_graph_node_count: {result.plan_graph_node_count}",
        f"accepted_branch_count: {result.accepted_branch_count}",
        "no_real_external_action: true",
        "",
        "[SUMMARY]",
        f"orchestrator_provider: {result.proposal.provider}",
        f"architect_provider: {result.architect_provider}",
        f"pair_smoke_status: {result.pair_smoke_status}",
        f"live_pair_executed: {_bool_text(result.live_gemini and result.executed)}",
        "root_final_authority: true",
        "controlled_orchestrator_enabled: false",
        "next_step: controlled orchestrator runtime integration later",
    ]
    return _sanitize_output("\n".join(lines).rstrip() + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the Gemini Orchestrator + Architect pair smoke."
    )
    parser.add_argument("--provider", choices=["mock", "gemini"], default="mock")
    parser.add_argument("--include-live-gemini", action="store_true")
    parser.add_argument("--model", default=None)
    args = parser.parse_args(argv)
    provider = "gemini" if args.include_live_gemini else args.provider
    print(
        run_gemini_orchestrator_architect_pair_smoke(
            provider=provider,
            model=args.model,
        ),
        end="",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
