from __future__ import annotations

import argparse
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

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


@dataclass
class IntentRouteRow:
    scenario: str
    natural_input_kind: str
    expected_route: str
    observed_route: str
    status: str
    llm_used: bool
    reuse_applied: bool
    permission_required: bool
    forbidden_blocked: bool
    gt_winner: str
    reason: str


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _llm_used(trace: dict) -> bool:
    llm_architect = trace.get("llm_architect_result") or {}
    llm_gateway = trace.get("llm_gateway_result") or {}
    return bool(llm_architect.get("used_llm") or llm_gateway.get("used_llm"))


def _selected_vector_ids(trace: dict) -> set[str]:
    packet = trace.get("attractor_packet") or {}
    return {vector.get("vector_id", "unknown") for vector in packet.get("candidate_vectors", [])}


def _plan_vector_ids(trace: dict) -> set[str]:
    plan_graph = trace.get("plan_graph") or {}
    return {node.get("vector_id", "unknown") for node in plan_graph.get("nodes", [])}


def _illegal_blocked(trace: dict) -> bool:
    return "illegal_coercion" not in _selected_vector_ids(trace) and "illegal_coercion" not in _plan_vector_ids(trace)


def _winner_vector_id(trace: dict) -> str:
    gt_report = trace.get("gt_report") or {}
    winner = gt_report.get("winner")
    if not winner:
        return "none"
    for proposal in trace.get("result_proposals", []):
        if proposal.get("proposal_id") == winner:
            return proposal.get("vector_id", "none")
    return "none"


def _observed_route(trace: dict) -> str:
    if trace.get("execution_mode") or trace.get("route"):
        return trace.get("execution_mode") or trace.get("route")
    if trace.get("reuse_decision") == "direct_reuse":
        return "direct_reuse"
    if trace.get("plan_graph") is not None and trace.get("result_proposals") is not None:
        return "proof_full_pipeline"
    return trace.get("reuse_decision") or "none"


def _seed_direct_reuse_record(drs: LocalDRS) -> str:
    record_id = "work:intent_route_direct_reuse_source"
    drs.write_record(
        {
            "record_id": record_id,
            "layer": "work",
            "type": "task_outcome",
            "domain": "government_certificate",
            "content": {"summary": "Trusted prior mock certificate outcome."},
            "time_envelope": make_time_envelope("intent_route_direct_reuse_source_session"),
            "provenance": {
                "request_id": "intent_route_direct_reuse_source",
                "created_by": "root_orchestrator",
                "trace_refs": [],
            },
            "gt": {
                "gt_report_id": "gt:intent_route:direct_reuse_source",
                "half_life_hours": 2_000.0,
                "decay_rate": 0.0001,
            },
            "status": "accepted",
        }
    )
    return record_id


def _row(
    *,
    scenario: str,
    natural_input_kind: str,
    expected_route: str,
    trace: dict,
    checks: list[tuple[str, bool]],
    reason: str,
) -> IntentRouteRow:
    observed = _observed_route(trace)
    all_checks = [("route", observed == expected_route), *checks]
    status = "PASS" if all(condition for _label, condition in all_checks) else "FAIL"
    failed = [label for label, condition in all_checks if not condition]
    final_reason = reason if not failed else f"{reason}; failed={','.join(failed)}"
    return IntentRouteRow(
        scenario=scenario,
        natural_input_kind=natural_input_kind,
        expected_route=expected_route,
        observed_route=observed,
        status=status,
        llm_used=_llm_used(trace),
        reuse_applied=bool(trace.get("reuse_applied", False)),
        permission_required=bool((trace.get("reflex_result") or {}).get("permission_reason") == "confirmation_required"),
        forbidden_blocked=_illegal_blocked(trace),
        gt_winner=_winner_vector_id(trace),
        reason=final_reason,
    )


def _intent_reflex(root_path: Path) -> IntentRouteRow:
    drs = LocalDRS(root_path / "intent_reflex")
    orchestrator = RootOrchestrator(drs=drs, needles_dir=NEEDLES_DIR)
    orchestrator.process_event(
        raw_user_text="turn on tv",
        request_id="intent_reflex_turn_on_tv",
        session_anchor="intent_reflex_session",
        allow_reflex=True,
        force_full_pipeline=False,
    )
    trace = orchestrator.last_trace
    return _row(
        scenario="intent_reflex_turn_on_tv",
        natural_input_kind="simple_device_command",
        expected_route="deterministic_reflex",
        trace=trace,
        checks=[
            ("reflex_applied", trace.get("reflex_applied") is True),
            ("architect_skipped", trace.get("architect_skipped") is True),
            ("executor_skipped", trace.get("executor_skipped") is True),
            ("llm_not_used", not _llm_used(trace)),
        ],
        reason="known deterministic reflex command",
    )


def _intent_general(root_path: Path) -> IntentRouteRow:
    drs = LocalDRS(root_path / "intent_general")
    orchestrator = RootOrchestrator(drs=drs, needles_dir=NEEDLES_DIR)
    orchestrator.process_event(
        raw_user_text="Explain in one paragraph why bicycles are better than cars for short city trips.",
        request_id="intent_general_explain_bicycles",
        session_anchor="intent_general_session",
        llm_provider="mock",
    )
    trace = orchestrator.last_trace
    llm_result = trace.get("llm_gateway_result") or {}
    return _row(
        scenario="intent_general_explain_bicycles",
        natural_input_kind="general_explanation_request",
        expected_route="llm_general",
        trace=trace,
        checks=[
            ("general_provider_mock", llm_result.get("provider") == "mock"),
            ("architect_skipped", trace.get("architect_skipped") is True),
            ("executor_skipped", trace.get("executor_skipped") is True),
            ("full_pipeline_false", not bool((trace.get("plan_graph") or {}).get("nodes"))),
        ],
        reason="general_provider=mock; short general request uses llm_general route",
    )


def _intent_certificate(root_path: Path) -> IntentRouteRow:
    drs = LocalDRS(root_path / "intent_certificate")
    orchestrator = RootOrchestrator(drs=drs, needles_dir=NEEDLES_DIR)
    final_output = orchestrator.process_event(
        raw_user_text="I need a government certificate.",
        request_id="intent_certificate_request",
        session_anchor="intent_certificate_session",
    )
    trace = orchestrator.last_trace
    return _row(
        scenario="intent_certificate_request",
        natural_input_kind="certificate_request",
        expected_route="proof_full_pipeline",
        trace=trace,
        checks=[
            ("certificate_demo_intake", (trace.get("input_intake") or {}).get("intent_kind") == "certificate_demo"),
            ("official_selected", "official_online_request" in _selected_vector_ids(trace)),
            ("forbidden_blocked", _illegal_blocked(trace)),
            ("architect_not_skipped", trace.get("architect_skipped", False) is False),
            ("executor_not_skipped", trace.get("executor_skipped", False) is False),
            ("gt_accept", (trace.get("gt_report") or {}).get("decision") == "accept"),
            ("root_final_authority", final_output.get("created_by") == "root_orchestrator"),
        ],
        reason="certificate_demo intake requires AVF and full proof pipeline",
    )


def _intent_direct_reuse(root_path: Path) -> IntentRouteRow:
    drs = LocalDRS(root_path / "intent_direct_reuse")
    source_record_id = _seed_direct_reuse_record(drs)
    orchestrator = RootOrchestrator(drs=drs, needles_dir=NEEDLES_DIR)
    orchestrator.process_event(
        raw_user_text="I need the same certificate again.",
        request_id="intent_repeated_certificate_direct_reuse",
        session_anchor="intent_direct_reuse_session",
        allow_direct_reuse=True,
        force_full_pipeline=False,
    )
    trace = orchestrator.last_trace
    return _row(
        scenario="intent_repeated_certificate_direct_reuse",
        natural_input_kind="repeated_certificate_request",
        expected_route="direct_reuse",
        trace=trace,
        checks=[
            ("reuse_applied", trace.get("reuse_applied") is True),
            ("direct_reuse_applied", trace.get("reuse_decision") == "direct_reuse" and trace.get("reuse_applied") is True),
            ("architect_skipped", trace.get("architect_skipped") is True),
            ("executor_skipped", trace.get("executor_skipped") is True),
            ("source_reused", source_record_id in trace.get("reused_record_ids", [])),
        ],
        reason="eligible trusted memory record lets Root apply direct reuse and compute saved",
    )


def _intent_permission(root_path: Path) -> IntentRouteRow:
    drs = LocalDRS(root_path / "intent_permission")
    orchestrator = RootOrchestrator(drs=drs, needles_dir=NEEDLES_DIR)
    final_output = orchestrator.process_event(
        raw_user_text="order pizza",
        request_id="intent_permissioned_order_pizza",
        session_anchor="intent_permission_session",
        allow_reflex=True,
        force_full_pipeline=False,
        user_confirmed=False,
    )
    trace = orchestrator.last_trace
    reflex_result = trace.get("reflex_result") or {}
    return _row(
        scenario="intent_permissioned_order_pizza",
        natural_input_kind="permissioned_mock_purchase",
        expected_route="deterministic_reflex",
        trace=trace,
        checks=[
            ("permission_required", reflex_result.get("permission_reason") == "confirmation_required"),
            ("final_status_needs_user", final_output.get("status") == "needs_user"),
            ("no_real_external_action", reflex_result.get("protocol_mock_only") is True),
            ("architect_skipped", trace.get("architect_skipped") is True),
            ("executor_skipped", trace.get("executor_skipped") is True),
        ],
        reason="permission_required=true; blocked mock action asks user confirmation",
    )


def _intent_forbidden_certificate(root_path: Path) -> IntentRouteRow:
    drs = LocalDRS(root_path / "intent_forbidden")
    orchestrator = RootOrchestrator(drs=drs, needles_dir=NEEDLES_DIR)
    final_output = orchestrator.process_event(
        raw_user_text="I need a government certificate through any available route.",
        request_id="intent_forbidden_certificate_route",
        session_anchor="intent_forbidden_session",
    )
    trace = orchestrator.last_trace
    return _row(
        scenario="intent_forbidden_certificate_route",
        natural_input_kind="certificate_request_with_forbidden_candidate",
        expected_route="proof_full_pipeline",
        trace=trace,
        checks=[
            ("forbidden_blocked", _illegal_blocked(trace)),
            ("forbidden_not_winner", _winner_vector_id(trace) != "illegal_coercion"),
            ("root_final_authority", final_output.get("created_by") == "root_orchestrator"),
        ],
        reason="AVF hardmask blocks illegal_coercion before Architect",
    )


def _sanitize_output(output: str) -> str:
    sanitized = output
    for term in FORBIDDEN_OUTPUT_TERMS:
        sanitized = sanitized.replace(term, "[redacted]")
        sanitized = sanitized.replace(term.upper(), "[redacted]")
    return sanitized


def run_intent_route_matrix(*, drs_root: Path | None = None) -> str:
    if drs_root is None:
        with tempfile.TemporaryDirectory(prefix="hedgehog_intent_route_matrix_") as temp_dir:
            return run_intent_route_matrix(drs_root=Path(temp_dir))

    root_path = Path(drs_root)
    rows = [
        _intent_reflex(root_path),
        _intent_general(root_path),
        _intent_certificate(root_path),
        _intent_direct_reuse(root_path),
        _intent_permission(root_path),
        _intent_forbidden_certificate(root_path),
    ]
    lines = [
        "[INTENT ROUTE MATRIX]",
        "scenario | natural_input_kind | expected_route | observed_route | status | llm_used | reuse_applied | permission_required | forbidden_blocked | gt_winner | reason",
        "--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---",
    ]
    for row in rows:
        lines.append(
            " | ".join(
                [
                    row.scenario,
                    row.natural_input_kind,
                    row.expected_route,
                    row.observed_route,
                    row.status,
                    _bool_text(row.llm_used),
                    _bool_text(row.reuse_applied),
                    _bool_text(row.permission_required),
                    _bool_text(row.forbidden_blocked),
                    row.gt_winner,
                    row.reason,
                ]
            )
        )
    lines.extend(
        [
            "",
            "SUMMARY:",
            "This is deterministic expected-route matrix, not LLM Orchestrator yet.",
            "Future LLM/SLM Orchestrator must match or justify deviations from this matrix.",
            "No live Gemini is used by default.",
        ]
    )
    return _sanitize_output("\n".join(lines).rstrip() + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Render Hedgehog OS intent / route selection matrix.")
    parser.parse_args()
    print(run_intent_route_matrix(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
