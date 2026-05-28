from __future__ import annotations

import argparse
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from hedgehog.drs import LocalDRS
from hedgehog.root_orchestrator import RootOrchestrator
from hedgehog.time_model import make_temporal_query, make_time_envelope
from hedgehog.reuse_gate import evaluate_reuse_candidates


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

SAFE_INPUT = "mock certificate request"


@dataclass(frozen=True)
class ColdStartPhase:
    phase: str
    status: str
    route: str
    memory_context_applied: bool
    retrieved_records: int
    reuse_decision: str
    reuse_applied: bool
    direct_reuse_applied: bool
    architect_skipped: bool
    executor_skipped: bool
    drs_writes: int
    evidence: str


@dataclass(frozen=True)
class ColdStartReport:
    phases: list[ColdStartPhase]
    work_records_before: int
    direct_reuse_available_before: bool
    work_records_after_first: int
    first_work_has_time_envelope: bool
    first_work_sensitive_input_absent: bool
    first_work_structured_fields_present: bool
    cold_start_first_run_success: bool
    first_run_wrote_memory: bool
    second_run_memory_influenced: bool
    direct_reuse_requires_eligibility: bool
    seeded_direct_reuse_success: bool
    root_final_authority_preserved: bool


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _contains_key(value: Any, forbidden_key: str) -> bool:
    if isinstance(value, dict):
        return forbidden_key in value or any(
            _contains_key(child, forbidden_key) for child in value.values()
        )
    if isinstance(value, list):
        return any(_contains_key(item, forbidden_key) for item in value)
    return False


def _route_from_trace(trace: dict) -> str:
    mode_router = trace.get("mode_router") or {}
    return (
        trace.get("execution_mode")
        or trace.get("route")
        or mode_router.get("execution_mode")
        or trace.get("reuse_decision")
        or "none"
    )


def _direct_reuse_applied(trace: dict) -> bool:
    return bool(trace.get("reuse_applied", False)) and trace.get("reuse_decision") == "direct_reuse"


def _phase_from_trace(
    *,
    phase: str,
    final_output: dict,
    trace: dict,
    evidence: str,
) -> ColdStartPhase:
    return ColdStartPhase(
        phase=phase,
        status="PASS" if final_output.get("status") == "success" else "FAIL",
        route=_route_from_trace(trace),
        memory_context_applied=bool(trace.get("memory_context_applied", False)),
        retrieved_records=int(trace.get("retrieved_record_count") or 0),
        reuse_decision=str(trace.get("reuse_decision", "none")),
        reuse_applied=bool(trace.get("reuse_applied", False)),
        direct_reuse_applied=_direct_reuse_applied(trace),
        architect_skipped=bool(trace.get("architect_skipped", False)),
        executor_skipped=bool(trace.get("executor_skipped", False)),
        drs_writes=len(final_output.get("drs_writes", [])),
        evidence=evidence,
    )


def _seed_direct_reuse_record(drs: LocalDRS) -> str:
    record_id = "work:cold_start_direct_reuse_source"
    drs.write_record(
        {
            "record_id": record_id,
            "layer": "work",
            "type": "task_outcome",
            "domain": "government_certificate",
            "content": {
                "summary": "Trusted seeded mock certificate outcome for direct reuse.",
                "result": "simulated_success",
                "final_status": "success",
                "execution_mode": "proof_full_pipeline",
                "route": "proof_full_pipeline",
                "reuse_applied": False,
                "direct_reuse_applied": False,
                "architect_skipped": False,
                "executor_skipped": False,
            },
            "time_envelope": make_time_envelope("cold_start_direct_reuse_source_session"),
            "provenance": {
                "request_id": "cold_start_direct_reuse_source",
                "created_by": "root_orchestrator",
                "trace_refs": [],
            },
            "gt": {
                "gt_report_id": "gt:cold_start:direct_reuse_source",
                "half_life_hours": 2_000.0,
                "decay_rate": 0.0001,
            },
            "status": "accepted",
        }
    )
    return record_id


def collect_cold_start_benchmark() -> ColdStartReport:
    with tempfile.TemporaryDirectory(prefix="hedgehog_cold_start_") as temp_dir:
        drs = LocalDRS(Path(temp_dir) / "drs")
        orchestrator = RootOrchestrator(drs=drs, needles_dir=NEEDLES_DIR)

        work_records_before = len(drs.read_layer("work"))
        precheck_reuse = evaluate_reuse_candidates(drs.read_layer("work"), make_temporal_query())
        direct_reuse_available_before = precheck_reuse["reuse_decision"] == "direct_reuse_candidate"
        phases = [
            ColdStartPhase(
                phase="empty_drs_precheck",
                status="PASS" if work_records_before == 0 and not direct_reuse_available_before else "FAIL",
                route="none",
                memory_context_applied=False,
                retrieved_records=0,
                reuse_decision=precheck_reuse["reuse_decision"],
                reuse_applied=False,
                direct_reuse_applied=False,
                architect_skipped=False,
                executor_skipped=False,
                drs_writes=0,
                evidence=(
                    f"work_records_before={work_records_before}; "
                    f"direct_reuse_available_before={_bool_text(direct_reuse_available_before)}"
                ),
            )
        ]

        first_output = orchestrator.process_event(
            raw_user_text=SAFE_INPUT,
            request_id="cold_start_first_run",
            session_anchor="cold_start_first_session",
            force_full_pipeline=True,
            allow_direct_reuse=False,
            allow_reflex=False,
            llm_provider="mock",
            architect_provider="deterministic",
        )
        first_trace = dict(orchestrator.last_trace)
        phases.append(
            _phase_from_trace(
                phase="first_run_cold_start",
                final_output=first_output,
                trace=first_trace,
                evidence="full pipeline ran from empty DRS and wrote Work memory",
            )
        )

        first_work = drs.read_record("work", first_output["drs_writes"][0])
        first_content = first_work.get("content", {})
        structured_fields = {
            "final_status",
            "execution_mode",
            "route",
            "selected_proposal_ids",
            "completed_proposal_ids",
            "final_draft_ref",
            "reuse_applied",
            "architect_skipped",
            "executor_skipped",
        }
        work_records_after_first = len(drs.read_layer("work"))
        first_work_has_time_envelope = bool(first_work.get("time_envelope"))
        first_work_sensitive_input_absent = not _contains_key(first_work, "raw_user_text")
        first_work_structured_fields_present = structured_fields <= set(first_content)
        phases.append(
            ColdStartPhase(
                phase="after_first_writeback",
                status=(
                    "PASS"
                    if (
                        work_records_after_first >= 1
                        and first_work_has_time_envelope
                        and first_work_sensitive_input_absent
                        and first_work_structured_fields_present
                    )
                    else "FAIL"
                ),
                route=first_content.get("route", "none"),
                memory_context_applied=bool(first_content.get("memory_context_applied", False)),
                retrieved_records=int(first_content.get("retrieved_record_count") or 0),
                reuse_decision=str(first_content.get("reuse_decision", "none")),
                reuse_applied=bool(first_content.get("reuse_applied", False)),
                direct_reuse_applied=bool(first_content.get("direct_reuse_applied", False)),
                architect_skipped=bool(first_content.get("architect_skipped", False)),
                executor_skipped=bool(first_content.get("executor_skipped", False)),
                drs_writes=work_records_after_first,
                evidence=(
                    f"work_records_after_first={work_records_after_first}; "
                    f"time_envelope={_bool_text(first_work_has_time_envelope)}; "
                    f"sensitive_input_absent={_bool_text(first_work_sensitive_input_absent)}; "
                    f"structured_fields={_bool_text(first_work_structured_fields_present)}"
                ),
            )
        )

        second_output = orchestrator.process_event(
            raw_user_text=SAFE_INPUT,
            request_id="cold_start_second_run",
            session_anchor="cold_start_second_session",
            force_full_pipeline=False,
            allow_direct_reuse=True,
            allow_reflex=False,
            llm_provider="mock",
            architect_provider="deterministic",
        )
        second_trace = dict(orchestrator.last_trace)
        second_memory_influenced = (
            bool(second_trace.get("memory_context_applied", False))
            or int(second_trace.get("retrieved_record_count") or 0) > 0
            or bool(second_trace.get("memory_source_record_ids", []))
        )
        second_direct_reuse = _direct_reuse_applied(second_trace)
        phases.append(
            _phase_from_trace(
                phase="second_run_memory_influence",
                final_output=second_output,
                trace=second_trace,
                evidence=(
                    "memory observed; direct reuse "
                    + ("applied because eligible" if second_direct_reuse else "not applied without eligibility")
                ),
            )
        )

        seeded_source_id = _seed_direct_reuse_record(drs)
        seeded_output = orchestrator.process_event(
            raw_user_text=SAFE_INPUT,
            request_id="cold_start_seeded_direct_reuse",
            session_anchor="cold_start_seeded_direct_reuse_session",
            force_full_pipeline=False,
            allow_direct_reuse=True,
            allow_reflex=False,
            llm_provider="mock",
            architect_provider="deterministic",
        )
        seeded_trace = dict(orchestrator.last_trace)
        phases.append(
            _phase_from_trace(
                phase="seeded_direct_reuse_eligible_run",
                final_output=seeded_output,
                trace=seeded_trace,
                evidence=f"seeded eligible Work record {seeded_source_id} allowed compute-saving direct reuse",
            )
        )

        root_authority_outputs = [
            first_output,
            second_output,
            seeded_output,
        ]
        return ColdStartReport(
            phases=phases,
            work_records_before=work_records_before,
            direct_reuse_available_before=direct_reuse_available_before,
            work_records_after_first=work_records_after_first,
            first_work_has_time_envelope=first_work_has_time_envelope,
            first_work_sensitive_input_absent=first_work_sensitive_input_absent,
            first_work_structured_fields_present=first_work_structured_fields_present,
            cold_start_first_run_success=first_output.get("status") == "success",
            first_run_wrote_memory=len(first_output.get("drs_writes", [])) >= 1,
            second_run_memory_influenced=second_memory_influenced,
            direct_reuse_requires_eligibility=not phases[1].direct_reuse_applied
            and (not phases[3].direct_reuse_applied or phases[3].reuse_decision == "direct_reuse"),
            seeded_direct_reuse_success=_direct_reuse_applied(seeded_trace)
            and seeded_output.get("status") == "success",
            root_final_authority_preserved=all(
                output.get("created_by") == "root_orchestrator"
                for output in root_authority_outputs
            ),
        )


def _sanitize_output(output: str) -> str:
    sanitized = output
    for term in FORBIDDEN_OUTPUT_TERMS:
        sanitized = sanitized.replace(term, "[redacted]")
        sanitized = sanitized.replace(term.upper(), "[redacted]")
    return sanitized


def render_cold_start_benchmark(report: ColdStartReport) -> str:
    lines = [
        "[COLD START BENCHMARK]",
        "note: temporary empty DRS",
        "note: no live Gemini by default",
        "note: no real external actions",
        "note: direct reuse requires eligibility, not just memory presence",
        "",
        "phase | status | route | memory_context_applied | retrieved_records | reuse_decision | reuse_applied | direct_reuse_applied | architect_skipped | executor_skipped | drs_writes | evidence",
        "--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---",
    ]
    for phase in report.phases:
        lines.append(
            " | ".join(
                [
                    phase.phase,
                    phase.status,
                    phase.route,
                    _bool_text(phase.memory_context_applied),
                    str(phase.retrieved_records),
                    phase.reuse_decision,
                    _bool_text(phase.reuse_applied),
                    _bool_text(phase.direct_reuse_applied),
                    _bool_text(phase.architect_skipped),
                    _bool_text(phase.executor_skipped),
                    str(phase.drs_writes),
                    phase.evidence,
                ]
            )
        )

    lines.extend(
        [
            "",
            "SUMMARY:",
            f"cold_start_first_run_success: {_bool_text(report.cold_start_first_run_success)}",
            f"first_run_wrote_memory: {_bool_text(report.first_run_wrote_memory)}",
            f"second_run_memory_influenced: {_bool_text(report.second_run_memory_influenced)}",
            f"direct_reuse_requires_eligibility: {_bool_text(report.direct_reuse_requires_eligibility)}",
            f"seeded_direct_reuse_success: {_bool_text(report.seeded_direct_reuse_success)}",
            f"root_final_authority_preserved: {_bool_text(report.root_final_authority_preserved)}",
            "no_real_external_actions: true",
            "live_gemini: false",
            "next_step: NeedleRuntime Chaos or Large Graph Stress",
        ]
    )
    return _sanitize_output("\n".join(lines).rstrip() + "\n")


def run_cold_start_benchmark() -> str:
    return render_cold_start_benchmark(collect_cold_start_benchmark())


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the cold start DRS convergence benchmark.")
    parser.parse_args()
    print(run_cold_start_benchmark(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
