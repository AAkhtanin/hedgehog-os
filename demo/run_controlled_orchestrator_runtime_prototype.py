from __future__ import annotations

import argparse
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from demo.run_controlled_orchestrator_integration_gate import GateScenario
from demo.run_controlled_orchestrator_integration_gate import _gate_decision
from hedgehog.drs import LocalDRS
from hedgehog.root_orchestrator import RootOrchestrator
from hedgehog.time_model import make_time_envelope


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
class RuntimeScenario:
    gate_scenario: GateScenario
    execution_text: str = "mock certificate request"
    architect_provider: str = "mock"
    deterministic_fallback_allowed: bool = False


@dataclass(frozen=True)
class RuntimeResult:
    scenario: str
    proposed_route: str
    gate_decision: str
    eligible: bool
    controlled_execution_performed: bool
    root_executed: bool
    execution_mode: str
    route: str
    final_status: str
    root_final_authority: bool
    architect_skipped: bool
    executor_skipped: bool
    reuse_applied: bool
    reason: str


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _seed_direct_reuse_record(drs: LocalDRS) -> None:
    drs.write_record(
        {
            "record_id": "work:controlled_runtime_direct_reuse_source",
            "layer": "work",
            "type": "task_outcome",
            "domain": "government_certificate",
            "content": {"summary": "Trusted controlled runtime prior mock certificate outcome."},
            "time_envelope": make_time_envelope("controlled_runtime_direct_reuse_source_session"),
            "provenance": {
                "request_id": "controlled_runtime_direct_reuse_source",
                "created_by": "root_orchestrator",
                "trace_refs": [],
            },
            "gt": {
                "gt_report_id": "gt:controlled_runtime:direct_reuse_source",
                "half_life_hours": 2_000.0,
                "decay_rate": 0.0001,
            },
            "status": "accepted",
        }
    )


def _root_route(trace: dict, fallback: str) -> str:
    for key in ("execution_mode", "route", "reuse_decision"):
        value = trace.get(key)
        if value and value != "none":
            return str(value)
    return fallback


def _execute_approved_route(scenario: RuntimeScenario, root_path: Path) -> tuple[dict, dict]:
    drs = LocalDRS(root_path)
    orchestrator = RootOrchestrator(drs=drs, needles_dir=NEEDLES_DIR)
    route = scenario.gate_scenario.proposed_route

    if route == "direct_reuse":
        _seed_direct_reuse_record(drs)
        final_output = orchestrator.process_event(
            raw_user_text=scenario.execution_text,
            request_id=f"{scenario.gate_scenario.scenario}_root",
            session_anchor=f"{scenario.gate_scenario.scenario}_session",
            allow_direct_reuse=True,
            force_full_pipeline=False,
        )
        return final_output, orchestrator.last_trace

    if route == "proof_full_pipeline":
        final_output = orchestrator.process_event(
            raw_user_text=scenario.execution_text,
            request_id=f"{scenario.gate_scenario.scenario}_root",
            session_anchor=f"{scenario.gate_scenario.scenario}_session",
            architect_provider=scenario.architect_provider,
            force_full_pipeline=True,
            allow_direct_reuse=False,
            allow_reflex=False,
        )
        return final_output, orchestrator.last_trace

    raise ValueError(f"controlled runtime prototype cannot execute route: {route}")


def _runtime_result(scenario: RuntimeScenario, root_path: Path) -> RuntimeResult:
    gate = _gate_decision(scenario.gate_scenario)
    should_execute = gate.eligible and scenario.gate_scenario.proposed_route in {
        "proof_full_pipeline",
        "direct_reuse",
    }

    if not should_execute:
        return RuntimeResult(
            scenario=scenario.gate_scenario.scenario,
            proposed_route=scenario.gate_scenario.proposed_route,
            gate_decision=gate.integration_gate_decision,
            eligible=gate.eligible,
            controlled_execution_performed=False,
            root_executed=False,
            execution_mode="none",
            route="skipped",
            final_status="not_run",
            root_final_authority=False,
            architect_skipped=True,
            executor_skipped=True,
            reuse_applied=False,
            reason=gate.reason,
        )

    final_output, trace = _execute_approved_route(scenario, root_path)
    return RuntimeResult(
        scenario=scenario.gate_scenario.scenario,
        proposed_route=scenario.gate_scenario.proposed_route,
        gate_decision=gate.integration_gate_decision,
        eligible=gate.eligible,
        controlled_execution_performed=True,
        root_executed=True,
        execution_mode=_root_route(trace, scenario.gate_scenario.proposed_route),
        route=_root_route(trace, scenario.gate_scenario.proposed_route),
        final_status=str(final_output.get("status", "none")),
        root_final_authority=final_output.get("created_by") == "root_orchestrator",
        architect_skipped=bool(trace.get("architect_skipped", False)),
        executor_skipped=bool(trace.get("executor_skipped", False)),
        reuse_applied=bool(trace.get("reuse_applied", False)),
        reason="Root executed the approved equivalent route after all controlled gates passed.",
    )


def _scenarios() -> list[RuntimeScenario]:
    full_guards = [
        "AVF",
        "HardMask",
        "PlanGraph contract",
        "Post V&V",
        "GT",
        "Root final authority",
    ]
    direct_reuse_guards = [
        "DirectReuseGate",
        "Freshness",
        "PolicyOK",
        "DRS writeback",
        "Root final authority",
    ]
    return [
        RuntimeScenario(
            gate_scenario=GateScenario(
                scenario="controlled_full_pipeline_eligible_executes",
                expected_route="proof_full_pipeline",
                proposed_route="proof_full_pipeline",
                proposed_required_guards=full_guards,
                forbidden_candidate_present=True,
            )
        ),
        RuntimeScenario(
            gate_scenario=GateScenario(
                scenario="controlled_full_pipeline_incomplete_guards_blocked",
                expected_route="proof_full_pipeline",
                proposed_route="proof_full_pipeline",
                proposed_required_guards=["AVF", "PlanGraph"],
                forbidden_candidate_present=True,
            )
        ),
        RuntimeScenario(
            gate_scenario=GateScenario(
                scenario="controlled_wrong_route_blocked",
                expected_route="proof_full_pipeline",
                proposed_route="llm_general",
                proposed_required_guards=["Root final authority", "no external action", "budget check"],
            )
        ),
        RuntimeScenario(
            gate_scenario=GateScenario(
                scenario="controlled_permission_needs_user_blocked",
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
            )
        ),
        RuntimeScenario(
            gate_scenario=GateScenario(
                scenario="controlled_direct_reuse_eligible_executes_reuse",
                expected_route="direct_reuse",
                proposed_route="direct_reuse",
                proposed_required_guards=direct_reuse_guards,
                wants_direct_reuse=True,
                direct_reuse_eligible=True,
            )
        ),
        RuntimeScenario(
            gate_scenario=GateScenario(
                scenario="controlled_direct_reuse_not_eligible_blocked_or_fallback",
                expected_route="direct_reuse",
                proposed_route="direct_reuse",
                proposed_required_guards=direct_reuse_guards,
                wants_direct_reuse=True,
                direct_reuse_eligible=False,
            )
        ),
        RuntimeScenario(
            gate_scenario=GateScenario(
                scenario="controlled_orchestrator_final_output_blocked",
                expected_route="llm_general",
                proposed_route="llm_general",
                proposed_required_guards=["Root final authority", "no external action", "budget check"],
                proposed_authority="orchestrator",
                wants_final_output=True,
            )
        ),
    ]


def _sanitize_output(output: str) -> str:
    sanitized = output
    for term in FORBIDDEN_OUTPUT_TERMS:
        sanitized = sanitized.replace(term, "[redacted]")
        sanitized = sanitized.replace(term.upper(), "[redacted]")
    return sanitized


def run_controlled_orchestrator_runtime_prototype() -> str:
    with tempfile.TemporaryDirectory(prefix="hedgehog_controlled_runtime_") as temp_dir:
        base = Path(temp_dir)
        results = [
            _runtime_result(scenario, base / scenario.gate_scenario.scenario)
            for scenario in _scenarios()
        ]

    eligible = sum(result.eligible for result in results)
    executed = sum(result.controlled_execution_performed for result in results)
    blocked = sum(not result.eligible for result in results)
    fallback_or_skipped = sum(not result.root_executed for result in results)
    executed_results = [result for result in results if result.root_executed]
    root_authority_all = all(result.root_final_authority for result in executed_results)

    lines = [
        "[CONTROLLED ORCHESTRATOR RUNTIME PROTOTYPE]",
        "note: Root executes approved equivalent routes only after validator + guard + integration gate",
        "note: Orchestrator does not directly control runtime",
        "note: Orchestrator cannot create FinalOutput",
        "note: no real external actions",
        "note: no live Gemini by default",
        "",
        "scenario | proposed_route | gate_decision | eligible | controlled_execution_performed | root_executed | execution_mode | route | final_status | root_final_authority | architect_skipped | executor_skipped | reuse_applied | reason",
        "--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---",
    ]
    for result in results:
        lines.append(
            " | ".join(
                [
                    result.scenario,
                    result.proposed_route,
                    result.gate_decision,
                    _bool_text(result.eligible),
                    _bool_text(result.controlled_execution_performed),
                    _bool_text(result.root_executed),
                    result.execution_mode,
                    result.route,
                    result.final_status,
                    _bool_text(result.root_final_authority),
                    _bool_text(result.architect_skipped),
                    _bool_text(result.executor_skipped),
                    _bool_text(result.reuse_applied),
                    result.reason,
                ]
            )
        )
    lines.extend(
        [
            "",
            "SUMMARY:",
            f"eligible: {eligible}",
            f"executed: {executed}",
            f"blocked: {blocked}",
            f"fallback_or_skipped: {fallback_or_skipped}",
            f"root_final_authority_all_executed: {_bool_text(root_authority_all)}",
            "uncontrolled_delegation: false",
            "controlled_orchestrator_enabled: prototype_only",
            "next_step: live controlled prototype only after explicit safety review",
        ]
    )
    return _sanitize_output("\n".join(lines).rstrip() + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run controlled Orchestrator runtime prototype.")
    parser.parse_args()
    print(run_controlled_orchestrator_runtime_prototype(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
