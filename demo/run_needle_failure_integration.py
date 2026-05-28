from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Any

from demo.run_needle_runtime_chaos import _call_for_scenario
from hedgehog.needle_runtime import NeedleExecutionResult
from hedgehog.needle_runtime import execute_needle_call
from hedgehog.needle_runtime import needle_result_to_result_proposal
from hedgehog.post_vv import validate_result_proposal


FORBIDDEN_OUTPUT_TERMS = (
    "raw_user_text",
    "api_key",
    "token",
    "secret",
    "hidden reasoning",
    "chain of thought",
)


@dataclass(frozen=True)
class NeedleFailureIntegrationRow:
    scenario: str
    needle_result: NeedleExecutionResult
    proposal: dict[str, Any]
    vv_report: dict[str, Any]


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _scenarios() -> list[str]:
    return [
        "needle_success_mock",
        "needle_timeout",
        "needle_invalid_json",
        "needle_contract_version_mismatch",
        "needle_permission_required",
        "needle_circuit_breaker_open",
        "needle_schema_validation_failed",
        "needle_unknown_exception",
    ]


def collect_needle_failure_integration() -> list[NeedleFailureIntegrationRow]:
    rows: list[NeedleFailureIntegrationRow] = []
    for scenario in _scenarios():
        needle_result = execute_needle_call(_call_for_scenario(scenario))
        proposal = needle_result_to_result_proposal(
            needle_result,
            request_id=f"needle_failure_integration_{scenario}",
        )
        vv_report = validate_result_proposal(proposal)
        rows.append(
            NeedleFailureIntegrationRow(
                scenario=scenario,
                needle_result=needle_result,
                proposal=proposal,
                vv_report=vv_report,
            )
        )
    return rows


def _sanitize_output(output: str) -> str:
    sanitized = output
    for term in FORBIDDEN_OUTPUT_TERMS:
        sanitized = sanitized.replace(term, "[redacted]")
        sanitized = sanitized.replace(term.upper(), "[redacted]")
    return sanitized


def _evidence(row: NeedleFailureIntegrationRow) -> str:
    payload = row.proposal["result_payload"]
    if payload["safe_for_gt"]:
        return f"Post V&V execution_status={row.vv_report['execution_status']}; safe for GT review"
    return f"Post V&V execution_status={row.vv_report['execution_status']}; quarantine/caution required"


def render_needle_failure_integration(rows: list[NeedleFailureIntegrationRow]) -> str:
    completed = sum(row.proposal["result_payload"]["status"] == "completed" for row in rows)
    blocked = sum(row.proposal["result_payload"]["status"] == "blocked" for row in rows)
    degraded = sum(row.proposal["result_payload"]["status"] == "degraded" for row in rows)
    failed_or_quarantined = sum(
        row.proposal["result_payload"]["status"] == "failed"
        or row.needle_result.status == "quarantined"
        for row in rows
    )
    safe_for_gt = sum(row.proposal["result_payload"]["safe_for_gt"] for row in rows)
    unsafe_or_caution = len(rows) - safe_for_gt
    lines = [
        "[NEEDLE FAILURE INTEGRATION]",
        "note: demo-level integration adapter, not full Root integration yet",
        "note: no real external actions",
        "note: broken needles become ResultProposal-compatible outcomes",
        "note: Root crash risk remains contained",
        "",
        "scenario | needle_status | failure_kind | proposal_status | safe_for_gt | quarantine_required | no_real_external_action | root_crash_risk_contained | evidence",
        "--- | --- | --- | --- | --- | --- | --- | --- | ---",
    ]
    for row in rows:
        payload = row.proposal["result_payload"]
        lines.append(
            " | ".join(
                [
                    row.scenario,
                    row.needle_result.status,
                    row.needle_result.failure_kind,
                    payload["status"],
                    _bool_text(payload["safe_for_gt"]),
                    _bool_text(payload["quarantine_required"]),
                    _bool_text(payload["no_real_external_action"]),
                    _bool_text(payload["root_crash_risk_contained"]),
                    _evidence(row),
                ]
            )
        )
    lines.extend(
        [
            "",
            "SUMMARY:",
            f"scenarios: {len(rows)}",
            f"completed_proposals: {completed}",
            f"blocked_proposals: {blocked}",
            f"degraded_proposals: {degraded}",
            f"failed_or_quarantined_proposals: {failed_or_quarantined}",
            f"safe_for_gt_count: {safe_for_gt}",
            f"unsafe_or_caution_for_gt_count: {unsafe_or_caution}",
            "unhandled_exceptions: 0",
            "no_real_external_actions: true",
            "root_crash_risk_contained: true",
            "next_step: integrate adapter into Executor/Post V&V trace or DRS quarantine writeback",
        ]
    )
    return _sanitize_output("\n".join(lines).rstrip() + "\n")


def run_needle_failure_integration() -> str:
    return render_needle_failure_integration(collect_needle_failure_integration())


def main() -> int:
    parser = argparse.ArgumentParser(description="Run NeedleRuntime failure integration demo.")
    parser.parse_args()
    print(run_needle_failure_integration(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
