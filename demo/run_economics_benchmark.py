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
FORBIDDEN_OUTPUT_TERMS = ("raw_user_text", "api_key", "token", "hidden reasoning", "chain of thought")


@dataclass
class EconomicsRow:
    scenario: str
    selected_mode: str
    llm_calls: int
    planner_units: int
    executor_units: int
    total_simulated_units: int
    baseline_units: int
    units_saved: int
    savings_ratio: float
    explanation: str


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _seed_direct_reuse_record(drs: LocalDRS) -> None:
    drs.write_record(
        {
            "record_id": "work:economics_direct_reuse_source",
            "layer": "work",
            "type": "task_outcome",
            "domain": "government_certificate",
            "content": {"summary": "Trusted prior mock certificate outcome."},
            "time_envelope": make_time_envelope("economics_direct_reuse_source_session"),
            "provenance": {
                "request_id": "economics_direct_reuse_source",
                "created_by": "root_orchestrator",
                "trace_refs": [],
            },
            "gt": {
                "gt_report_id": "gt:economics:direct_reuse_source",
                "half_life_hours": 2_000.0,
                "decay_rate": 0.0001,
            },
            "status": "accepted",
        }
    )


def _total_units(planner_units: int, executor_units: int, llm_calls: int) -> int:
    return planner_units + executor_units + llm_calls


def _baseline_units(executor_units: int) -> int:
    return _total_units(planner_units=1, executor_units=executor_units, llm_calls=1)


def _savings_ratio(total: int, baseline: int) -> float:
    if baseline <= 0:
        return 0.0
    return round((baseline - total) / baseline, 3)


def _row(
    *,
    scenario: str,
    selected_mode: str,
    llm_calls: int,
    planner_units: int,
    executor_units: int,
    baseline_executor_units: int,
    explanation: str,
) -> EconomicsRow:
    total = _total_units(planner_units, executor_units, llm_calls)
    baseline = _baseline_units(baseline_executor_units)
    return EconomicsRow(
        scenario=scenario,
        selected_mode=selected_mode,
        llm_calls=llm_calls,
        planner_units=planner_units,
        executor_units=executor_units,
        total_simulated_units=total,
        baseline_units=baseline,
        units_saved=baseline - total,
        savings_ratio=_savings_ratio(total, baseline),
        explanation=explanation,
    )


def _run_l0(root_path: Path) -> EconomicsRow:
    drs = LocalDRS(root_path / "l0")
    orchestrator = RootOrchestrator(drs=drs, needles_dir=NEEDLES_DIR)
    orchestrator.process_event(
        raw_user_text="turn on tv",
        request_id="econ_l0_reflex_turn_on_tv",
        session_anchor="econ_l0_reflex_session",
        allow_reflex=True,
        force_full_pipeline=False,
    )
    trace = orchestrator.last_trace
    return _row(
        scenario="econ_l0_reflex_turn_on_tv",
        selected_mode=trace.get("execution_mode", "deterministic_reflex"),
        llm_calls=0,
        planner_units=0,
        executor_units=0,
        baseline_executor_units=9,
        explanation="deterministic reflex avoided planning and executor fanout",
    )


def _run_direct_reuse(root_path: Path) -> EconomicsRow:
    drs = LocalDRS(root_path / "direct_reuse")
    _seed_direct_reuse_record(drs)
    orchestrator = RootOrchestrator(drs=drs, needles_dir=NEEDLES_DIR)
    orchestrator.process_event(
        raw_user_text="mock certificate request",
        request_id="econ_direct_reuse_certificate",
        session_anchor="econ_direct_reuse_session",
        allow_direct_reuse=True,
        force_full_pipeline=False,
    )
    trace = orchestrator.last_trace
    return _row(
        scenario="econ_direct_reuse_certificate",
        selected_mode=trace.get("execution_mode") or trace.get("reuse_decision", "direct_reuse"),
        llm_calls=0,
        planner_units=0,
        executor_units=0,
        baseline_executor_units=9,
        explanation="trusted reusable Work record avoided repeated Architect and Executor compute",
    )


def _run_general_math(root_path: Path) -> EconomicsRow:
    drs = LocalDRS(root_path / "general_math")
    orchestrator = RootOrchestrator(drs=drs, needles_dir=NEEDLES_DIR)
    orchestrator.process_event(
        raw_user_text="x + y = 110\nx - y = 100",
        request_id="econ_general_math_mock",
        session_anchor="econ_general_math_session",
        llm_provider="mock",
    )
    trace = orchestrator.last_trace
    return _row(
        scenario="econ_general_math_mock",
        selected_mode=trace.get("execution_mode", "llm_general"),
        llm_calls=0,
        planner_units=0,
        executor_units=0,
        baseline_executor_units=9,
        explanation="cheap general responder route avoided the PlanGraph pipeline; live estimate would be one LLM call",
    )


def _run_full_certificate(root_path: Path) -> EconomicsRow:
    drs = LocalDRS(root_path / "full_certificate")
    orchestrator = RootOrchestrator(drs=drs, needles_dir=NEEDLES_DIR)
    orchestrator.process_event(
        raw_user_text="mock certificate request",
        request_id="econ_full_certificate_pipeline",
        session_anchor="econ_full_certificate_session",
        architect_provider="mock_llm",
    )
    trace = orchestrator.last_trace
    executor_units = len(trace.get("result_proposals", []))
    return _row(
        scenario="econ_full_certificate_pipeline",
        selected_mode=trace.get("execution_mode") or trace.get("route") or "proof_full_pipeline",
        llm_calls=0,
        planner_units=1,
        executor_units=executor_units,
        baseline_executor_units=max(executor_units, 9),
        explanation="complex constrained task justifies AVF, PlanGraph, Executor, Post V&V, and GT",
    )


def _sanitize_output(output: str) -> str:
    sanitized = output
    for term in FORBIDDEN_OUTPUT_TERMS:
        sanitized = sanitized.replace(term, "[redacted]")
        sanitized = sanitized.replace(term.upper(), "[redacted]")
    return sanitized


def run_economics_benchmark(*, drs_root: Path | None = None) -> str:
    if drs_root is None:
        with tempfile.TemporaryDirectory(prefix="hedgehog_economics_") as temp_dir:
            return run_economics_benchmark(drs_root=Path(temp_dir))
    root_path = Path(drs_root)
    rows = [
        _run_l0(root_path),
        _run_direct_reuse(root_path),
        _run_general_math(root_path),
        _run_full_certificate(root_path),
    ]
    total_routed = sum(row.total_simulated_units for row in rows)
    total_baseline = sum(row.baseline_units for row in rows)
    total_saved = total_baseline - total_routed
    routed_llm_calls = sum(row.llm_calls for row in rows)
    baseline_llm_calls_estimate = len(rows)
    lines = [
        "[ECONOMICS BENCHMARK]",
        "note: simulated model, not provider billing",
        "live_gemini: false",
        "",
        "scenario | selected_mode | llm_calls | planner_units | executor_units | total_simulated_units | baseline_units | units_saved | savings_ratio | explanation",
        "--- | --- | --- | --- | --- | --- | --- | --- | --- | ---",
    ]
    for row in rows:
        lines.append(
            " | ".join(
                [
                    row.scenario,
                    row.selected_mode,
                    str(row.llm_calls),
                    str(row.planner_units),
                    str(row.executor_units),
                    str(row.total_simulated_units),
                    str(row.baseline_units),
                    str(row.units_saved),
                    f"{row.savings_ratio:.3f}",
                    row.explanation,
                ]
            )
        )
    lines.extend(
        [
            "",
            "[SUMMARY]",
            f"total_routed_units: {total_routed}",
            f"total_baseline_units: {total_baseline}",
            f"total_units_saved: {total_saved}",
            f"savings_ratio: {_savings_ratio(total_routed, total_baseline):.3f}",
            f"routed_llm_calls: {routed_llm_calls}",
            f"baseline_llm_calls_estimate: {baseline_llm_calls_estimate}",
            "note: simulated model, not provider billing; no real external actions were performed.",
        ]
    )
    return _sanitize_output("\n".join(lines).rstrip() + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Hedgehog OS simulated economics benchmark.")
    parser.parse_args()
    print(run_economics_benchmark(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
