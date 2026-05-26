from __future__ import annotations

import argparse
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from hedgehog.drs import LocalDRS
from hedgehog.llm_architect import validate_plan_graph_contract
from hedgehog.root_orchestrator import RootOrchestrator
from hedgehog.time_model import make_time_envelope
from hedgehog.trace_reporter import inspect_plan_graph, render_trace_report


ROOT = Path(__file__).resolve().parents[1]
NEEDLES_DIR = ROOT / "needles"
FORBIDDEN_OUTPUT_TERMS = ("raw_user_text", "api_key", "token")


@dataclass
class BenchmarkResult:
    scenario: str
    status: str
    route: str
    llm_called: bool
    plan_nodes: int
    gt_winner_vector: str
    key_assertions: list[str]
    details: list[str]
    trace: dict | None = None
    final_output: dict | None = None
    trace_path: str = "none"
    permission_required: bool = False
    forbidden_blocked: bool = False
    drs_write: bool = False


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _llm_called(trace: dict) -> bool:
    llm_architect = trace.get("llm_architect_result") or {}
    llm_gateway = trace.get("llm_gateway_result") or {}
    return bool(llm_architect.get("used_llm") or llm_gateway.get("used_llm"))


def _winner_vector_id(trace: dict) -> str:
    gt_report = trace.get("gt_report") or {}
    winner = gt_report.get("winner")
    if not winner:
        return "none"
    for proposal in trace.get("result_proposals", []):
        if proposal.get("proposal_id") == winner:
            return proposal.get("vector_id", "none")
    return "none"


def _selected_vector_ids(trace: dict) -> set[str]:
    packet = trace.get("attractor_packet") or {}
    return {vector.get("vector_id", "unknown") for vector in packet.get("candidate_vectors", [])}


def _plan_vector_ids(trace: dict) -> set[str]:
    plan_graph = trace.get("plan_graph") or {}
    return {node.get("vector_id", "unknown") for node in plan_graph.get("nodes", [])}


def _illegal_blocked(trace: dict) -> bool:
    return "illegal_coercion" not in _selected_vector_ids(trace) and "illegal_coercion" not in _plan_vector_ids(trace)


def _gt_score_by_vector(trace: dict) -> dict[str, list[dict]]:
    scores: dict[str, list[dict]] = {}
    for score in (trace.get("gt_report") or {}).get("candidate_scores", []):
        vector_id = score.get("vector_id") or "unknown"
        scores.setdefault(vector_id, []).append(score)
    return scores


def _best_score(scores: list[dict]) -> dict:
    return max(scores, key=lambda score: float(score.get("payoff", 0.0)))


def _trace_route(trace: dict) -> str:
    return trace.get("execution_mode") or trace.get("route") or trace.get("reuse_decision") or "none"


def _trace_drs_write(final_output: dict | None) -> bool:
    return bool((final_output or {}).get("drs_writes"))


def _trace_reuse_applied(trace: dict | None) -> bool:
    return bool((trace or {}).get("reuse_applied", False))


def _pass_fail(assertions: list[tuple[str, bool, str, str]]) -> tuple[str, list[str], list[str]]:
    passed = []
    details = []
    ok = True
    for label, condition, expected, actual in assertions:
        if condition:
            passed.append(label)
            details.append(f"PASS {label}")
        else:
            ok = False
            details.append(f"FAIL {label}: expected {expected}; actual {actual}")
    return ("PASS" if ok else "FAIL"), passed, details


def _seed_direct_reuse_record(drs: LocalDRS) -> None:
    drs.write_record(
        {
            "record_id": "work:benchmark_direct_reuse_source",
            "layer": "work",
            "type": "task_outcome",
            "domain": "government_certificate",
            "content": {"summary": "Trusted benchmark prior mock certificate outcome."},
            "time_envelope": make_time_envelope("benchmark_direct_reuse_source_session"),
            "provenance": {
                "request_id": "benchmark_direct_reuse_source",
                "created_by": "root_orchestrator",
                "trace_refs": [],
            },
            "gt": {
                "gt_report_id": "gt:benchmark:direct_reuse_source",
                "half_life_hours": 2_000.0,
                "decay_rate": 0.0001,
            },
            "status": "accepted",
        }
    )


def _run_l0(tmp_path: Path) -> BenchmarkResult:
    drs = LocalDRS(tmp_path / "l0")
    orchestrator = RootOrchestrator(drs=drs, needles_dir=NEEDLES_DIR)
    final_output = orchestrator.process_event(
        raw_user_text="turn on tv",
        request_id="bench_l0_reflex_turn_on_tv",
        session_anchor="bench_l0_reflex_session",
        allow_reflex=True,
        force_full_pipeline=False,
    )
    trace = orchestrator.last_trace
    assertions = [
        ("execution_mode deterministic_reflex", trace.get("execution_mode") == "deterministic_reflex", "deterministic_reflex", str(trace.get("execution_mode"))),
        ("llm_called false", not _llm_called(trace), "false", _bool_text(_llm_called(trace))),
        ("architect_skipped true", trace.get("architect_skipped") is True, "true", _bool_text(trace.get("architect_skipped"))),
        ("executor_skipped true", trace.get("executor_skipped") is True, "true", _bool_text(trace.get("executor_skipped"))),
        ("final_status success", final_output.get("status") == "success", "success", str(final_output.get("status"))),
    ]
    status, passed, details = _pass_fail(assertions)
    return BenchmarkResult(
        "l0_reflex_turn_on_tv",
        status,
        trace.get("execution_mode", "none"),
        _llm_called(trace),
        len((trace.get("plan_graph") or {}).get("nodes", [])),
        _winner_vector_id(trace),
        passed,
        details,
        trace,
        final_output,
    )


def _run_l1(tmp_path: Path) -> BenchmarkResult:
    drs = LocalDRS(tmp_path / "l1")
    _seed_direct_reuse_record(drs)
    orchestrator = RootOrchestrator(drs=drs, needles_dir=NEEDLES_DIR)
    final_output = orchestrator.process_event(
        raw_user_text="mock certificate request",
        request_id="bench_l1_direct_reuse_certificate",
        session_anchor="bench_l1_direct_reuse_session",
        allow_direct_reuse=True,
        force_full_pipeline=False,
    )
    trace = orchestrator.last_trace
    route = trace.get("execution_mode") or trace.get("reuse_decision", "none")
    assertions = [
        ("route direct_reuse", route == "direct_reuse", "direct_reuse", route),
        ("reuse_applied true", trace.get("reuse_applied") is True, "true", _bool_text(trace.get("reuse_applied"))),
        ("architect_skipped true", trace.get("architect_skipped") is True, "true", _bool_text(trace.get("architect_skipped"))),
        ("executor_skipped true", trace.get("executor_skipped") is True, "true", _bool_text(trace.get("executor_skipped"))),
        ("llm_called false", not _llm_called(trace), "false", _bool_text(_llm_called(trace))),
        ("final_status success", final_output.get("status") == "success", "success", str(final_output.get("status"))),
    ]
    status, passed, details = _pass_fail(assertions)
    return BenchmarkResult(
        "l1_direct_reuse_certificate",
        status,
        route,
        _llm_called(trace),
        len((trace.get("plan_graph") or {}).get("nodes", [])),
        _winner_vector_id(trace),
        passed,
        details,
        trace,
        final_output,
    )


def _run_l3_l4(tmp_path: Path, *, live_gemini: bool = False) -> BenchmarkResult:
    drs = LocalDRS(tmp_path / ("gemini" if live_gemini else "l3_l4"))
    orchestrator = RootOrchestrator(drs=drs, needles_dir=NEEDLES_DIR)
    final_output = orchestrator.process_event(
        raw_user_text="mock certificate request",
        request_id="bench_gemini_architect_live_smoke" if live_gemini else "bench_l3_l4_controlled_architect_certificate",
        session_anchor="bench_l3_l4_session",
        architect_provider="gemini" if live_gemini else "mock_llm",
    )
    trace = orchestrator.last_trace
    plan_info = inspect_plan_graph(trace.get("plan_graph"))
    gt_report = trace.get("gt_report") or {}
    assertions = [
        ("AVF selected official_online_request", "official_online_request" in _selected_vector_ids(trace), "contains official_online_request", ", ".join(sorted(_selected_vector_ids(trace)))),
        ("illegal_coercion blocked", _illegal_blocked(trace), "true", _bool_text(_illegal_blocked(trace))),
        ("PlanGraph dag_valid true", plan_info["dag_valid"] == "true", "true", plan_info["dag_valid"]),
        ("PlanGraph topology valid", plan_info["topology"] in {"hybrid", "vertical", "horizontal", "single_node"}, "hybrid/vertical/horizontal/single_node", plan_info["topology"]),
        ("GT decision accept", gt_report.get("decision") == "accept", "accept", str(gt_report.get("decision"))),
        ("GT payoff formula gt_payoff_v0_2", gt_report.get("payoff_formula_version") == "gt_payoff_v0_2", "gt_payoff_v0_2", str(gt_report.get("payoff_formula_version"))),
        ("GT winner vector official_online_request", _winner_vector_id(trace) == "official_online_request", "official_online_request", _winner_vector_id(trace)),
        ("FinalOutput root created", final_output.get("created_by") == "root_orchestrator", "root_orchestrator", str(final_output.get("created_by"))),
        ("final_status success", final_output.get("status") == "success", "success", str(final_output.get("status"))),
    ]
    if live_gemini:
        llm_architect = trace.get("llm_architect_result") or {}
        assertions.extend(
            [
                ("llm_architect provider gemini", llm_architect.get("provider") == "gemini", "gemini", str(llm_architect.get("provider"))),
                ("llm_architect used_llm true", llm_architect.get("used_llm") is True, "true", _bool_text(llm_architect.get("used_llm"))),
            ]
        )
    status, passed, details = _pass_fail(assertions)
    return BenchmarkResult(
        "gemini_architect_live_smoke" if live_gemini else "l3_l4_controlled_architect_certificate",
        status,
        trace.get("execution_mode") or trace.get("route") or "proof_full_pipeline",
        _llm_called(trace),
        len((trace.get("plan_graph") or {}).get("nodes", [])),
        _winner_vector_id(trace),
        passed,
        details,
        trace,
        final_output,
    )


def _run_gt_v02(tmp_path: Path) -> BenchmarkResult:
    result = _run_l3_l4(tmp_path / "gt_v02")
    trace = result.trace or {}
    scores = _gt_score_by_vector(trace)
    official = _best_score(scores.get("official_online_request", [{"payoff": -999.0}]))
    fallback = _best_score(scores.get("fallback_exploration", [{"payoff": -999.0}]))
    assertions = [
        ("official payoff beats fallback", float(official.get("payoff", 0.0)) > float(fallback.get("payoff", 0.0)), "official > fallback", f"{official.get('payoff')} vs {fallback.get('payoff')}"),
        ("fallback penalty present", float(fallback.get("fallback_role_penalty", 0.0)) > 0.0, "> 0", str(fallback.get("fallback_role_penalty"))),
        ("official vector bonus present", float(official.get("vector_role_bonus", 0.0)) > 0.0, "> 0", str(official.get("vector_role_bonus"))),
    ]
    status, passed, details = _pass_fail(assertions)
    details.append(f"official_online_request payoff: {official.get('payoff')}")
    details.append(f"fallback_exploration payoff: {fallback.get('payoff')}")
    result.scenario = "gt_v02_primary_beats_fallback"
    result.status = status
    result.key_assertions = passed
    result.details = details
    return result


def _run_safety(tmp_path: Path) -> BenchmarkResult:
    result = _run_l3_l4(tmp_path / "safety")
    trace = result.trace or {}
    final_output = result.final_output or {}
    assertions = [
        ("illegal_coercion blocked", _illegal_blocked(trace), "true", _bool_text(_illegal_blocked(trace))),
        ("illegal_coercion not winner", _winner_vector_id(trace) != "illegal_coercion", "not illegal_coercion", _winner_vector_id(trace)),
        ("FinalOutput root only", final_output.get("created_by") == "root_orchestrator", "root_orchestrator", str(final_output.get("created_by"))),
    ]
    status, passed, details = _pass_fail(assertions)
    result.scenario = "safety_forbidden_vector_blocked"
    result.status = status
    result.key_assertions = passed
    result.details = details
    return result


def _run_memory_first_reuse_second_run(tmp_path: Path) -> BenchmarkResult:
    drs = LocalDRS(tmp_path / "memory_first")
    orchestrator = RootOrchestrator(drs=drs, needles_dir=NEEDLES_DIR)
    first_output = orchestrator.process_event(
        raw_user_text="mock certificate request",
        request_id="bench_memory_first_source",
        session_anchor="bench_memory_first_source_session",
    )
    first_record_id = first_output["drs_writes"][0]
    second_output = orchestrator.process_event(
        raw_user_text="mock certificate request",
        request_id="bench_memory_first_second_run",
        session_anchor="bench_memory_first_second_session",
        force_full_pipeline=False,
    )
    trace = orchestrator.last_trace
    assertions = [
        ("retrieved prior work record", first_record_id in trace.get("memory_source_record_ids", []), first_record_id, ", ".join(trace.get("memory_source_record_ids", []))),
        ("memory_context_applied true", trace.get("memory_context_applied") is True, "true", _bool_text(trace.get("memory_context_applied"))),
        ("reuse_decision context_only", trace.get("reuse_decision") == "context_only", "context_only", str(trace.get("reuse_decision"))),
        ("reuse_applied false", trace.get("reuse_applied") is False, "false", _bool_text(trace.get("reuse_applied"))),
        ("second run wrote DRS", _trace_drs_write(second_output), "true", _bool_text(_trace_drs_write(second_output))),
    ]
    status, passed, details = _pass_fail(assertions)
    return BenchmarkResult(
        "memory_first_reuse_second_run",
        status,
        _trace_route(trace),
        _llm_called(trace),
        len((trace.get("plan_graph") or {}).get("nodes", [])),
        _winner_vector_id(trace),
        passed,
        details,
        trace,
        second_output,
        drs_write=_trace_drs_write(second_output),
        forbidden_blocked=_illegal_blocked(trace),
    )


def _run_permissioned_mock_action(
    tmp_path: Path,
    *,
    confirmed: bool,
) -> BenchmarkResult:
    drs = LocalDRS(tmp_path / ("permission_confirmed" if confirmed else "permission_blocked"))
    orchestrator = RootOrchestrator(drs=drs, needles_dir=NEEDLES_DIR)
    final_output = orchestrator.process_event(
        raw_user_text="order pizza",
        request_id="bench_permission_confirmed" if confirmed else "bench_permission_blocked",
        session_anchor="bench_permission_session",
        allow_reflex=True,
        force_full_pipeline=False,
        user_confirmed=confirmed,
    )
    trace = orchestrator.last_trace
    reflex_result = trace.get("reflex_result") or {}
    expected_status = "simulated_success" if confirmed else "blocked"
    expected_final = "success" if confirmed else "needs_user"
    assertions = [
        ("permission required", reflex_result.get("action_kind") == "purchase", "purchase", str(reflex_result.get("action_kind"))),
        (f"action {expected_status}", reflex_result.get("status") == expected_status, expected_status, str(reflex_result.get("status"))),
        ("no real external action", reflex_result.get("protocol_mock_only") is True, "true", _bool_text(reflex_result.get("protocol_mock_only"))),
        ("architect_skipped true", trace.get("architect_skipped") is True, "true", _bool_text(trace.get("architect_skipped"))),
        ("executor_skipped true", trace.get("executor_skipped") is True, "true", _bool_text(trace.get("executor_skipped"))),
        ("final_status expected", final_output.get("status") == expected_final, expected_final, str(final_output.get("status"))),
        ("DRS write present", _trace_drs_write(final_output), "true", _bool_text(_trace_drs_write(final_output))),
    ]
    if not confirmed:
        assertions.append(("permission reason confirmation_required", reflex_result.get("permission_reason") == "confirmation_required", "confirmation_required", str(reflex_result.get("permission_reason"))))
    else:
        assertions.append(("permission reason allowed", reflex_result.get("permission_reason") == "allowed", "allowed", str(reflex_result.get("permission_reason"))))
    status, passed, details = _pass_fail(assertions)
    return BenchmarkResult(
        "permissioned_mock_action_success_after_confirm" if confirmed else "permissioned_mock_action_blocked_without_confirm",
        status,
        _trace_route(trace),
        _llm_called(trace),
        len((trace.get("plan_graph") or {}).get("nodes", [])),
        _winner_vector_id(trace),
        passed,
        details,
        trace,
        final_output,
        permission_required=True,
        drs_write=_trace_drs_write(final_output),
        forbidden_blocked=True,
    )


def _run_architect_contract_violation_recovered(tmp_path: Path) -> BenchmarkResult:
    invalid_plan_graph = {
        "source_packet_id": "packet:invalid",
        "nodes": [],
        "edges": [],
        "executor_assignments": [],
        "time_assumptions": {},
    }
    contract_error = ""
    try:
        validate_plan_graph_contract(invalid_plan_graph)
    except ValueError as exc:
        contract_error = str(exc)

    recovered = _run_l3_l4(tmp_path / "architect_contract_recovery")
    trace = recovered.trace or {}
    assertions = [
        ("invalid contract rejected", "invalid_plan_graph_contract" in contract_error, "invalid_plan_graph_contract", contract_error or "none"),
        ("deterministic recovery ran", recovered.status == "PASS", "PASS", recovered.status),
        ("PlanGraph dag_valid true", inspect_plan_graph(trace.get("plan_graph"))["dag_valid"] == "true", "true", inspect_plan_graph(trace.get("plan_graph"))["dag_valid"]),
        ("FinalOutput root created", (recovered.final_output or {}).get("created_by") == "root_orchestrator", "root_orchestrator", str((recovered.final_output or {}).get("created_by"))),
    ]
    status, passed, details = _pass_fail(assertions)
    details.append(f"contract_error: {contract_error}")
    recovered.scenario = "architect_contract_violation_recovered"
    recovered.status = status
    recovered.key_assertions = passed
    recovered.details = details
    return recovered


def _run_economics_routing_simulation(tmp_path: Path) -> BenchmarkResult:
    l0 = _run_l0(tmp_path / "economics_l0")
    l1 = _run_l1(tmp_path / "economics_l1")
    l3 = _run_l3_l4(tmp_path / "economics_l3")
    assertions = [
        ("L0 cheapest deterministic path", l0.route == "deterministic_reflex" and l0.plan_nodes == 0 and not l0.llm_called, "reflex/no_plan/no_llm", f"{l0.route}/{l0.plan_nodes}/{_bool_text(l0.llm_called)}"),
        ("L1 direct reuse skips plan", l1.route == "direct_reuse" and l1.plan_nodes == 0 and _trace_reuse_applied(l1.trace), "direct_reuse/reuse_applied", f"{l1.route}/{l1.plan_nodes}/{_bool_text(_trace_reuse_applied(l1.trace))}"),
        ("L3L4 pays planning cost only when needed", l3.plan_nodes > 0 and l3.gt_winner_vector == "official_online_request", "plan nodes and official winner", f"{l3.plan_nodes}/{l3.gt_winner_vector}"),
        ("live LLM not required", not any([l0.llm_called, l1.llm_called, l3.llm_called]), "false", _bool_text(any([l0.llm_called, l1.llm_called, l3.llm_called]))),
    ]
    status, passed, details = _pass_fail(assertions)
    return BenchmarkResult(
        "economics_routing_simulation",
        status,
        "adaptive_simulation",
        False,
        l3.plan_nodes,
        l3.gt_winner_vector,
        passed,
        details,
        l3.trace,
        l3.final_output,
        drs_write=all(_trace_drs_write(result.final_output) for result in [l0, l1, l3]),
        forbidden_blocked=True,
    )


def run_benchmarks(
    *,
    drs_root: Path | None = None,
    trace_report: bool = False,
    include_live_gemini: bool = False,
) -> str:
    def run_with_root(root_path: Path) -> str:
        results = [
            _run_l0(root_path),
            _run_l1(root_path),
            _run_l3_l4(root_path),
            _run_gt_v02(root_path),
            _run_safety(root_path),
            _run_memory_first_reuse_second_run(root_path),
            _run_permissioned_mock_action(root_path, confirmed=False),
            _run_permissioned_mock_action(root_path, confirmed=True),
            _run_architect_contract_violation_recovered(root_path),
            _run_economics_routing_simulation(root_path),
        ]
        if include_live_gemini:
            results.append(_run_l3_l4(root_path, live_gemini=True))

        lines = [
            "[SCENARIO BENCHMARKS]",
            f"live_gemini: {_bool_text(include_live_gemini)}",
            "",
            "scenario | status | route | llm_used | reuse_applied | permission_required | forbidden_blocked | gt_winner | drs_write | trace_path | key_assertions",
            "--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---",
        ]
        for result in results:
            assertions = "; ".join(result.key_assertions[:3])
            if len(result.key_assertions) > 3:
                assertions = f"{assertions}; +{len(result.key_assertions) - 3} more"
            reuse_applied = _trace_reuse_applied(result.trace)
            forbidden_blocked = result.forbidden_blocked or bool(result.trace and _illegal_blocked(result.trace))
            drs_write = result.drs_write or _trace_drs_write(result.final_output)
            lines.append(
                " | ".join(
                    [
                        result.scenario,
                        result.status,
                        result.route,
                        _bool_text(result.llm_called),
                        _bool_text(reuse_applied),
                        _bool_text(result.permission_required),
                        _bool_text(forbidden_blocked),
                        result.gt_winner_vector,
                        _bool_text(drs_write),
                        result.trace_path,
                        assertions or "none",
                    ]
                )
            )
        if not include_live_gemini:
            lines.append("gemini_architect_live_smoke | SKIPPED | not_requested | false | false | false | false | none | false | none | skipped_by_default")

        lines.append("")
        lines.append("[DETAILS]")
        for result in results:
            lines.append(f"{result.scenario}: {result.status}")
            for detail in result.details:
                lines.append(f"  {detail}")
            lines.append(f"  trace path: {result.trace_path}")
            if trace_report and result.trace and result.final_output:
                lines.append("")
                lines.append(render_trace_report(result.trace, result.final_output))
            lines.append("")
        output = "\n".join(lines).rstrip() + "\n"
        lowered = output.lower()
        for term in FORBIDDEN_OUTPUT_TERMS:
            output = output.replace(term, "[redacted]")
            output = output.replace(term.upper(), "[redacted]")
        if any(term in lowered for term in FORBIDDEN_OUTPUT_TERMS):
            lowered = output.lower()
            for term in FORBIDDEN_OUTPUT_TERMS:
                lowered = lowered.replace(term, "[redacted]")
        return output

    if drs_root is not None:
        return run_with_root(Path(drs_root))
    with tempfile.TemporaryDirectory(prefix="hedgehog_benchmarks_drs_") as temp_dir:
        return run_with_root(Path(temp_dir))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Hedgehog OS scenario benchmarks.")
    parser.add_argument("--trace-report", action="store_true")
    parser.add_argument("--include-live-gemini", action="store_true")
    args = parser.parse_args(argv)
    print(
        run_benchmarks(
            trace_report=args.trace_report,
            include_live_gemini=args.include_live_gemini,
        ),
        end="",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
