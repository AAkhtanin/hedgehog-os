from __future__ import annotations

import argparse
import json
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from hedgehog.telegram_shell import handle_telegram_text
from hedgehog.trace_reporter import render_trace_report


ROOT = Path(__file__).resolve().parents[1]
NEEDLES_DIR = ROOT / "needles"
FORBIDDEN_OUTPUT_TERMS = ("raw_user_text", "api_key", "token")
TELEGRAM_SAFE_LIMIT = 3900


@dataclass
class TelegramBenchmarkResult:
    scenario: str
    status: str
    route: str
    provider: str
    llm_used: bool
    final_status: str
    key_assertions: list[str]
    details: list[str]
    shell_result: dict | None = None
    trace_payload: dict | None = None
    trace_path: str = "none"


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _read_trace(result: dict) -> dict:
    path = Path(result["trace_path"])
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


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


def _combined_response(result: dict) -> str:
    if result.get("debug_text"):
        return f"{result.get('reply_text', '')}\n\n{result['debug_text']}"
    return result.get("reply_text", "")


def _response_length_assertion(result: dict) -> tuple[str, bool, str, str]:
    combined = _combined_response(result)
    if len(combined) <= TELEGRAM_SAFE_LIMIT:
        return ("response length safe", True, f"<= {TELEGRAM_SAFE_LIMIT}", str(len(combined)))
    if "[truncated]" in combined:
        return ("response length explicitly truncated", True, "[truncated]", str(len(combined)))
    return ("response length safe", False, f"<= {TELEGRAM_SAFE_LIMIT} or [truncated]", str(len(combined)))


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


def _make_result(
    *,
    scenario: str,
    shell_result: dict,
    trace_payload: dict,
    assertions: list[tuple[str, bool, str, str]],
) -> TelegramBenchmarkResult:
    status, passed, details = _pass_fail(assertions)
    return TelegramBenchmarkResult(
        scenario=scenario,
        status=status,
        route=shell_result.get("route", "none"),
        provider=shell_result.get("llm_provider") or shell_result.get("provider", "none"),
        llm_used=bool(shell_result.get("llm_used", False)),
        final_status=shell_result.get("final_status", "unknown"),
        key_assertions=passed,
        details=details,
        shell_result=shell_result,
        trace_payload=trace_payload,
        trace_path=shell_result.get("trace_path", "none"),
    )


def _run_general_math_mock(drs_root: Path) -> TelegramBenchmarkResult:
    result = handle_telegram_text(
        text="x + y = 110\nx - y = 100",
        chat_id="bench_math_mock",
        drs_root=drs_root / "general_math_mock",
        needles_dir=NEEDLES_DIR,
        debug=True,
        llm_provider="mock",
    )
    trace_payload = _read_trace(result)
    trace = trace_payload["trace"]
    assertions = [
        ("execution_mode llm_general", result["execution_mode"] == "llm_general", "llm_general", result["execution_mode"]),
        ("route llm_general", result["route"] == "llm_general", "llm_general", result["route"]),
        ("final_status success", result["final_status"] == "success", "success", result["final_status"]),
        ("architect_skipped true", trace.get("architect_skipped") is True, "true", _bool_text(trace.get("architect_skipped"))),
        ("executor_skipped true", trace.get("executor_skipped") is True, "true", _bool_text(trace.get("executor_skipped"))),
        ("response not empty", bool(result["reply_text"].strip()), "non-empty", str(len(result["reply_text"]))),
        ("debug has llm_status", "llm_status:" in result["debug_text"], "present", result["debug_text"]),
        ("debug has llm_provider", "llm_provider:" in result["debug_text"], "present", result["debug_text"]),
        ("debug has trace_path", "trace_path:" in result["debug_text"], "present", result["debug_text"]),
        _response_length_assertion(result),
    ]
    return _make_result(
        scenario="telegram_general_math_mock",
        shell_result=result,
        trace_payload=trace_payload,
        assertions=assertions,
    )


def _run_general_math_gemini(drs_root: Path) -> TelegramBenchmarkResult:
    result = handle_telegram_text(
        text="x + y = 110\nx - y = 100",
        chat_id="bench_math_gemini",
        drs_root=drs_root / "general_math_gemini",
        needles_dir=NEEDLES_DIR,
        debug=True,
        llm_provider="gemini",
    )
    trace_payload = _read_trace(result)
    if result.get("llm_status") != "completed" or result.get("final_status") != "success":
        details = [
            "SAFE_FAIL Gemini live path did not complete",
            f"llm_status: {result.get('llm_status')}",
            f"llm_error: {result.get('llm_error')}",
            f"trace path: {result.get('trace_path')}",
        ]
        return TelegramBenchmarkResult(
            scenario="telegram_general_math_gemini_optional",
            status="SAFE_FAIL",
            route=result.get("route", "llm_general"),
            provider=result.get("llm_provider", "gemini"),
            llm_used=bool(result.get("llm_used", False)),
            final_status=result.get("final_status", "unknown"),
            key_assertions=[],
            details=details,
            shell_result=result,
            trace_payload=trace_payload,
            trace_path=result.get("trace_path", "none"),
        )
    assertions = [
        ("provider gemini", result.get("llm_provider") == "gemini", "gemini", str(result.get("llm_provider"))),
        ("used_llm true", result.get("llm_used") is True, "true", _bool_text(result.get("llm_used"))),
        ("final_status success", result.get("final_status") == "success", "success", str(result.get("final_status"))),
        ("response not empty", bool(result.get("reply_text", "").strip()), "non-empty", str(len(result.get("reply_text", "")))),
        _response_length_assertion(result),
    ]
    return _make_result(
        scenario="telegram_general_math_gemini_optional",
        shell_result=result,
        trace_payload=trace_payload,
        assertions=assertions,
    )


def _run_l0_reflex(drs_root: Path) -> TelegramBenchmarkResult:
    result = handle_telegram_text(
        text="turn on tv",
        chat_id="bench_l0_reflex",
        drs_root=drs_root / "l0_reflex",
        needles_dir=NEEDLES_DIR,
        debug=True,
        force_full_pipeline=False,
        allow_reflex=True,
    )
    trace_payload = _read_trace(result)
    trace = trace_payload["trace"]
    assertions = [
        ("execution_mode deterministic_reflex", result["execution_mode"] == "deterministic_reflex", "deterministic_reflex", result["execution_mode"]),
        ("reflex_applied true", trace.get("reflex_applied") is True, "true", _bool_text(trace.get("reflex_applied"))),
        ("architect_skipped true", trace.get("architect_skipped") is True, "true", _bool_text(trace.get("architect_skipped"))),
        ("executor_skipped true", trace.get("executor_skipped") is True, "true", _bool_text(trace.get("executor_skipped"))),
        ("final_status success", result["final_status"] == "success", "success", result["final_status"]),
        _response_length_assertion(result),
    ]
    return _make_result(
        scenario="telegram_l0_reflex_turn_on_tv",
        shell_result=result,
        trace_payload=trace_payload,
        assertions=assertions,
    )


def _run_certificate_controlled(drs_root: Path) -> TelegramBenchmarkResult:
    result = handle_telegram_text(
        text="mock certificate request",
        chat_id="bench_certificate",
        drs_root=drs_root / "certificate_controlled",
        needles_dir=NEEDLES_DIR,
        debug=True,
        force_full_pipeline=True,
        llm_provider="mock",
    )
    trace_payload = _read_trace(result)
    trace = trace_payload["trace"]
    gt_report = trace.get("gt_report") or {}
    route_ok = result["route"] in {"proof_full_pipeline", "avf_architect_execution", "context_only"}
    assertions = [
        ("route controlled", route_ok, "proof_full_pipeline/controlled", result["route"]),
        ("AVF selected official_online_request", "official_online_request" in _selected_vector_ids(trace), "contains official_online_request", ", ".join(sorted(_selected_vector_ids(trace)))),
        ("illegal_coercion blocked", _illegal_blocked(trace), "true", _bool_text(_illegal_blocked(trace))),
        ("GT decision accept", gt_report.get("decision") == "accept", "accept", str(gt_report.get("decision"))),
        ("GT payoff formula gt_payoff_v0_2", gt_report.get("payoff_formula_version") == "gt_payoff_v0_2", "gt_payoff_v0_2", str(gt_report.get("payoff_formula_version"))),
        ("GT winner vector official_online_request", _winner_vector_id(trace) == "official_online_request", "official_online_request", _winner_vector_id(trace)),
        ("final_status success", result["final_status"] == "success", "success", result["final_status"]),
        _response_length_assertion(result),
    ]
    return _make_result(
        scenario="telegram_certificate_request_controlled",
        shell_result=result,
        trace_payload=trace_payload,
        assertions=assertions,
    )


def _run_debug_trace_visible(base: TelegramBenchmarkResult) -> TelegramBenchmarkResult:
    result = dict(base.shell_result or {})
    debug_text = result.get("debug_text", "")
    assertions = [
        ("debug has request_id", "request_id:" in debug_text, "present", debug_text),
        ("debug has execution_mode", "execution_mode:" in debug_text, "present", debug_text),
        ("debug has route", "route:" in debug_text, "present", debug_text),
        ("debug has final_status", "final_status:" in debug_text, "present", debug_text),
        ("debug has gt_decision", "gt_decision:" in debug_text, "present", debug_text),
        ("debug has trace_path", "trace_path:" in debug_text, "present", debug_text),
        ("debug has llm_status", "llm_status:" in debug_text, "present", debug_text),
        _response_length_assertion(result),
    ]
    status, passed, details = _pass_fail(assertions)
    return TelegramBenchmarkResult(
        scenario="telegram_debug_trace_visible",
        status=status,
        route=result.get("route", "none"),
        provider=result.get("llm_provider", "none"),
        llm_used=bool(result.get("llm_used", False)),
        final_status=result.get("final_status", "unknown"),
        key_assertions=passed,
        details=details,
        shell_result=result,
        trace_payload=base.trace_payload,
        trace_path=result.get("trace_path", "none"),
    )


def _run_no_secret_leak(results: list[TelegramBenchmarkResult]) -> TelegramBenchmarkResult:
    chunks: list[str] = []
    for result in results:
        chunks.extend(
            [
            result.scenario,
            result.route,
            result.provider,
            result.final_status,
            "\n".join(result.details),
            (result.shell_result or {}).get("reply_text", ""),
            (result.shell_result or {}).get("debug_text", ""),
        ]
        )
    combined = "\n".join(chunks)
    lowered = combined.lower()
    assertions = [
        ("sensitive terms absent", not any(term in lowered for term in FORBIDDEN_OUTPUT_TERMS), "absent", "present" if any(term in lowered for term in FORBIDDEN_OUTPUT_TERMS) else "absent"),
    ]
    status, passed, details = _pass_fail(assertions)
    return TelegramBenchmarkResult(
        scenario="telegram_no_secret_leak",
        status=status,
        route="audit",
        provider="none",
        llm_used=False,
        final_status="checked",
        key_assertions=passed,
        details=details,
    )


def _run_response_length_safe(results: list[TelegramBenchmarkResult]) -> TelegramBenchmarkResult:
    assertions = []
    for result in results:
        if not result.shell_result:
            continue
        assertion = _response_length_assertion(result.shell_result)
        label, ok, expected, actual = assertion
        assertions.append((f"{result.scenario} {label}", ok, expected, actual))
    status, passed, details = _pass_fail(assertions)
    return TelegramBenchmarkResult(
        scenario="telegram_response_length_safe",
        status=status,
        route="audit",
        provider="none",
        llm_used=False,
        final_status="checked",
        key_assertions=passed,
        details=details,
    )


def _skipped_live_gemini() -> TelegramBenchmarkResult:
    return TelegramBenchmarkResult(
        scenario="telegram_general_math_gemini_optional",
        status="SKIPPED",
        route="not_requested",
        provider="gemini",
        llm_used=False,
        final_status="skipped",
        key_assertions=["skipped_by_default"],
        details=["SKIPPED live Gemini is disabled unless --include-live-gemini is passed"],
    )


def _summary_assertions(assertions: list[str]) -> str:
    if not assertions:
        return "none"
    if len(assertions) <= 3:
        return "; ".join(assertions)
    return f"{'; '.join(assertions[:3])}; +{len(assertions) - 3} more"


def _sanitize_output(output: str) -> str:
    sanitized = output
    for term in FORBIDDEN_OUTPUT_TERMS:
        sanitized = sanitized.replace(term, "[sensitive]")
        sanitized = sanitized.replace(term.upper(), "[sensitive]")
    return sanitized


def _render_results(results: list[TelegramBenchmarkResult], *, trace_report: bool, include_live_gemini: bool) -> str:
    lines = [
        "[TELEGRAM E2E BENCHMARKS]",
        f"live_gemini: {_bool_text(include_live_gemini)}",
        "",
        "scenario | status | route | provider | llm_used | final_status | key_assertions",
        "--- | --- | --- | --- | --- | --- | ---",
    ]
    for result in results:
        lines.append(
            " | ".join(
                [
                    result.scenario,
                    result.status,
                    result.route,
                    result.provider,
                    _bool_text(result.llm_used),
                    result.final_status,
                    _summary_assertions(result.key_assertions),
                ]
            )
        )
    lines.extend(["", "[DETAILS]"])
    for result in results:
        lines.append(f"{result.scenario}: {result.status}")
        for detail in result.details:
            lines.append(f"  {detail}")
        lines.append(f"  trace path: {result.trace_path}")
        if trace_report and result.trace_payload:
            trace = result.trace_payload.get("trace") or {}
            final_output = result.trace_payload.get("final_output")
            lines.extend(["", render_trace_report(trace, final_output), ""])
        else:
            lines.append("")
    return _sanitize_output("\n".join(lines).rstrip() + "\n")


def run_telegram_e2e_benchmarks(
    *,
    drs_root: Path | None = None,
    trace_report: bool = False,
    include_live_gemini: bool = False,
) -> str:
    if drs_root is None:
        with tempfile.TemporaryDirectory(prefix="hedgehog_telegram_bench_") as temp_dir:
            return run_telegram_e2e_benchmarks(
                drs_root=Path(temp_dir),
                trace_report=trace_report,
                include_live_gemini=include_live_gemini,
            )
    drs_root = Path(drs_root)
    required_results = [
        _run_general_math_mock(drs_root),
        _run_l0_reflex(drs_root),
        _run_certificate_controlled(drs_root),
    ]
    live_result = _run_general_math_gemini(drs_root) if include_live_gemini else _skipped_live_gemini()
    audit_results = [
        _run_debug_trace_visible(required_results[0]),
        _run_no_secret_leak(required_results + [live_result]),
        _run_response_length_safe(required_results + [live_result]),
    ]
    results = [
        required_results[0],
        live_result,
        required_results[1],
        required_results[2],
        *audit_results,
    ]
    return _render_results(results, trace_report=trace_report, include_live_gemini=include_live_gemini)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Telegram shell E2E benchmark scenarios.")
    parser.add_argument("--trace-report", action="store_true", help="Append compact trace reports for scenarios with traces.")
    parser.add_argument("--include-live-gemini", action="store_true", help="Run the optional live Gemini Telegram general responder scenario.")
    args = parser.parse_args()
    print(
        run_telegram_e2e_benchmarks(
            trace_report=args.trace_report,
            include_live_gemini=args.include_live_gemini,
        ),
        end="",
    )


if __name__ == "__main__":
    main()
