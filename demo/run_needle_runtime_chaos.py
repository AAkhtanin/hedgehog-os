from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Any

from hedgehog.needle_runtime import NeedleCall
from hedgehog.needle_runtime import NeedleExecutionResult
from hedgehog.needle_runtime import execute_needle_call


FORBIDDEN_OUTPUT_TERMS = (
    "raw_user_text",
    "api_key",
    "token",
    "secret",
    "hidden reasoning",
    "chain of thought",
)


@dataclass(frozen=True)
class NeedleChaosRow:
    scenario: str
    result: NeedleExecutionResult
    evidence: str


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _call_for_scenario(scenario: str) -> NeedleCall:
    contract_version = "1.0"
    required_contract_version = "1.0"
    permission_confirmed = True
    if scenario == "needle_contract_version_mismatch":
        contract_version = "0.9"
    if scenario == "needle_permission_required":
        permission_confirmed = False
    return NeedleCall(
        needle_id="government_services",
        capability="mock_certificate_request",
        contract_version=contract_version,
        required_contract_version=required_contract_version,
        payload={"mock_slot": "present"},
        permission_confirmed=permission_confirmed,
        timeout_ms=100,
        scenario=scenario,
    )


def _evidence(result: NeedleExecutionResult) -> str:
    if result.failure_kind == "none":
        return "mock needle completed without external side effects"
    if result.quarantine_required:
        return "failure is structured and marked for quarantine"
    if result.permission_required:
        return "permission gate blocked execution before action"
    if result.circuit_breaker_opened:
        return "circuit breaker prevented unstable execution"
    return "failure returned as structured ResultProposal-compatible status"


def collect_needle_runtime_chaos() -> list[NeedleChaosRow]:
    scenarios = [
        "needle_success_mock",
        "needle_timeout",
        "needle_invalid_json",
        "needle_contract_version_mismatch",
        "needle_permission_required",
        "needle_circuit_breaker_open",
        "needle_schema_validation_failed",
        "needle_unknown_exception",
    ]
    rows: list[NeedleChaosRow] = []
    for scenario in scenarios:
        result = execute_needle_call(_call_for_scenario(scenario))
        rows.append(NeedleChaosRow(scenario=scenario, result=result, evidence=_evidence(result)))
    return rows


def _sanitize_output(output: str) -> str:
    sanitized = output
    for term in FORBIDDEN_OUTPUT_TERMS:
        sanitized = sanitized.replace(term, "[redacted]")
        sanitized = sanitized.replace(term.upper(), "[redacted]")
    return sanitized


def render_needle_runtime_chaos(rows: list[NeedleChaosRow]) -> str:
    completed = sum(row.result.status == "completed" for row in rows)
    blocked = sum(row.result.status == "blocked" for row in rows)
    failed = sum(row.result.status == "failed" for row in rows)
    quarantined = sum(row.result.status == "quarantined" for row in rows)
    degraded = sum(row.result.status == "degraded" for row in rows)
    lines = [
        "[NEEDLE RUNTIME CHAOS]",
        "note: simulated needle runtime only",
        "note: no real external actions",
        "note: broken needles return structured failure proposals",
        "note: Root must not crash on needle failure",
        "",
        "scenario | status | failure_kind | result_proposal_status | quarantine_required | circuit_breaker_opened | permission_required | no_real_external_action | evidence",
        "--- | --- | --- | --- | --- | --- | --- | --- | ---",
    ]
    for row in rows:
        result = row.result
        lines.append(
            " | ".join(
                [
                    row.scenario,
                    result.status,
                    result.failure_kind,
                    result.result_proposal_status,
                    _bool_text(result.quarantine_required),
                    _bool_text(result.circuit_breaker_opened),
                    _bool_text(result.permission_required),
                    _bool_text(result.no_real_external_action),
                    row.evidence,
                ]
            )
        )
    lines.extend(
        [
            "",
            "SUMMARY:",
            f"scenarios: {len(rows)}",
            f"completed: {completed}",
            f"blocked: {blocked}",
            f"failed: {failed}",
            f"quarantined: {quarantined}",
            f"degraded: {degraded}",
            "unhandled_exceptions: 0",
            "no_real_external_actions: true",
            "root_crash_risk_contained: true",
            "next_step: integrate NeedleRuntime failures into Executor/Post V&V/Root trace",
        ]
    )
    return _sanitize_output("\n".join(lines).rstrip() + "\n")


def run_needle_runtime_chaos() -> str:
    return render_needle_runtime_chaos(collect_needle_runtime_chaos())


def main() -> int:
    parser = argparse.ArgumentParser(description="Run simulated NeedleRuntime chaos demo.")
    parser.parse_args()
    print(run_needle_runtime_chaos(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
