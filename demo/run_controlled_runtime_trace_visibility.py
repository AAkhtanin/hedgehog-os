from __future__ import annotations

import argparse
import tempfile
from pathlib import Path
from typing import Any

from demo.run_controlled_orchestrator_integration_gate import _gate_decision
from demo.run_controlled_orchestrator_integration_gate import _guard_result
from demo.run_controlled_orchestrator_integration_gate import _validator_result
from demo.run_controlled_orchestrator_runtime_prototype import RuntimeResult
from demo.run_controlled_orchestrator_runtime_prototype import RuntimeScenario
from demo.run_controlled_orchestrator_runtime_prototype import _runtime_result
from demo.run_controlled_orchestrator_runtime_prototype import _scenarios


FORBIDDEN_OUTPUT_TERMS = (
    "raw_user_text",
    "api_key",
    "token",
    "secret",
    "hidden reasoning",
    "chain of thought",
)


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _join(values: list[str]) -> str:
    return ", ".join(values) if values else "none"


def _verdict(runtime: RuntimeResult) -> str:
    if runtime.root_executed and not runtime.root_final_authority:
        return "FAIL_ROOT_AUTHORITY_MISSING"
    if runtime.root_executed and not runtime.eligible:
        return "FAIL_UNEXPECTED_EXECUTION"
    if runtime.root_executed and runtime.route == "direct_reuse":
        return "PASS_DIRECT_REUSE_EXECUTED_BY_ROOT"
    if runtime.root_executed:
        return "PASS_EXECUTED_BY_ROOT"
    if runtime.gate_decision == "not_eligible_needs_user":
        return "PASS_NEEDS_USER_BLOCKED"
    return "PASS_BLOCKED_BY_GATE"


def _trace_block(scenario: RuntimeScenario, runtime: RuntimeResult) -> tuple[list[str], str]:
    gate_scenario = scenario.gate_scenario
    validator = _validator_result(gate_scenario)
    guard = _guard_result(gate_scenario)
    gate = _gate_decision(gate_scenario)
    verdict = _verdict(runtime)

    lines = [
        f"[TRACE] {gate_scenario.scenario}",
        (
            "PROPOSAL: "
            f"proposed_route={gate_scenario.proposed_route}; "
            f"expected_route={gate_scenario.expected_route}; "
            f"guards={_join(gate_scenario.proposed_required_guards)}; "
            f"authority={gate_scenario.proposed_authority}"
        ),
        (
            "VALIDATOR: "
            f"{validator.validation_decision}; "
            f"allowed={_bool_text(validator.allowed)}; "
            f"violations={_join(validator.violations)}; "
            f"required_guards_after_validator={_join(validator.required_guards)}"
        ),
        (
            "GUARDS: "
            f"route_correct={_bool_text(guard.route_correct)}; "
            f"guards_complete={_bool_text(guard.guards_complete)}; "
            f"score={guard.guard_completeness_score:.2f}; "
            f"missing={_join(guard.missing_required_guards)}; "
            f"quality={guard.proposal_quality_status}"
        ),
        (
            "GATE: "
            f"{gate.integration_gate_decision}; "
            f"eligible={_bool_text(gate.eligible)}; "
            f"controlled_execution_requested={_bool_text(gate_scenario.controlled_execution_requested)}; "
            f"controlled_execution_performed={_bool_text(runtime.controlled_execution_performed)}"
        ),
        (
            "ROOT: "
            f"executed={_bool_text(runtime.root_executed)}; "
            f"mode={runtime.execution_mode}; "
            f"route={runtime.route}; "
            f"final_status={runtime.final_status}; "
            f"root_final_authority={_bool_text(runtime.root_final_authority)}; "
            f"root_created_final_output={_bool_text(runtime.root_created_final_output)}; "
            f"architect_skipped={_bool_text(runtime.architect_skipped)}; "
            f"executor_skipped={_bool_text(runtime.executor_skipped)}; "
            f"reuse_applied={_bool_text(runtime.reuse_applied)}; "
            f"direct_reuse_applied={_bool_text(runtime.direct_reuse_applied)}; "
            f"gt_decision={runtime.gt_decision}; "
            f"drs_writes={runtime.drs_write_count}; "
            "no_real_external_action=true"
        ),
        f"VERDICT: {verdict}",
        "",
    ]
    return lines, verdict


def _sanitize_output(output: str) -> str:
    sanitized = output
    for term in FORBIDDEN_OUTPUT_TERMS:
        sanitized = sanitized.replace(term, "[redacted]")
        sanitized = sanitized.replace(term.upper(), "[redacted]")
    return sanitized


def run_controlled_runtime_trace_visibility() -> str:
    scenarios = _scenarios()
    with tempfile.TemporaryDirectory(prefix="hedgehog_controlled_trace_") as temp_dir:
        base = Path(temp_dir)
        runtime_results = [
            _runtime_result(scenario, base / scenario.gate_scenario.scenario)
            for scenario in scenarios
        ]

    blocks: list[str] = []
    verdicts: list[str] = []
    for scenario, runtime in zip(scenarios, runtime_results, strict=True):
        lines, verdict = _trace_block(scenario, runtime)
        blocks.extend(lines)
        verdicts.append(verdict)

    executed_by_root = sum(verdict == "PASS_EXECUTED_BY_ROOT" for verdict in verdicts)
    blocked_by_gate = sum(verdict == "PASS_BLOCKED_BY_GATE" for verdict in verdicts)
    needs_user_blocked = sum(verdict == "PASS_NEEDS_USER_BLOCKED" for verdict in verdicts)
    direct_reuse_executed = sum(
        verdict == "PASS_DIRECT_REUSE_EXECUTED_BY_ROOT" for verdict in verdicts
    )
    unexpected_execution = sum(verdict == "FAIL_UNEXPECTED_EXECUTION" for verdict in verdicts)
    root_authority_failures = sum(
        verdict == "FAIL_ROOT_AUTHORITY_MISSING" for verdict in verdicts
    )

    lines = [
        "[CONTROLLED RUNTIME TRACE VISIBILITY]",
        "note: explains why controlled proposals executed or were blocked",
        "note: Root remains final authority",
        "note: no live Gemini by default",
        "note: no real external actions",
        "",
        *blocks,
        "SUMMARY:",
        f"traces: {len(verdicts)}",
        f"executed_by_root: {executed_by_root}",
        f"blocked_by_gate: {blocked_by_gate}",
        f"needs_user_blocked: {needs_user_blocked}",
        f"direct_reuse_executed: {direct_reuse_executed}",
        f"unexpected_execution: {unexpected_execution}",
        f"root_authority_failures: {root_authority_failures}",
        "uncontrolled_delegation: false",
        "controlled_orchestrator_enabled: prototype_only",
        "next_step: live controlled smoke after safety review",
    ]
    return _sanitize_output("\n".join(lines).rstrip() + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Render controlled runtime trace visibility.")
    parser.parse_args()
    print(run_controlled_runtime_trace_visibility(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
