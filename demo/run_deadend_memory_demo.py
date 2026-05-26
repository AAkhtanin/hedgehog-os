from __future__ import annotations

import argparse
import tempfile
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
    "hidden reasoning",
    "chain of thought",
)
DEADEND_RECORD_ID = "deadend:demo:illegal_coercion"


def _bool_text(value: Any) -> str:
    return "true" if bool(value) else "false"


def _selected_vector_ids(trace: dict) -> set[str]:
    packet = trace.get("attractor_packet") or {}
    return {vector.get("vector_id", "unknown") for vector in packet.get("candidate_vectors", [])}


def _plan_vector_ids(trace: dict) -> set[str]:
    plan_graph = trace.get("plan_graph") or {}
    return {node.get("vector_id", "unknown") for node in plan_graph.get("nodes", [])}


def _illegal_coercion_avoided(trace: dict) -> bool:
    return "illegal_coercion" not in _selected_vector_ids(trace) and "illegal_coercion" not in _plan_vector_ids(trace)


def _write_deadend_signal(drs: LocalDRS, *, request_id: str) -> str:
    record = {
        "record_id": DEADEND_RECORD_ID,
        "layer": "deadends",
        "type": "dead_end",
        "domain": "government_certificate",
        "content": {
            "summary": "Demo-level memory signal for a blocked forbidden vector.",
            "signal_kind": "deadend_fraud_like_demo_signal",
            "vector_id": "illegal_coercion",
            "reason": "forbidden_vector_blocked",
            "domain": "government_certificate",
            "demo_created_by": "deadend_memory_demo",
            "demo_level": True,
            "production_deadend_routing": False,
        },
        "time_envelope": make_time_envelope("deadend_memory_demo_session"),
        "provenance": {
            "request_id": request_id,
            "created_by": "root_orchestrator",
            "trace_refs": [
                {
                    "trace_id": "deadend_memory_demo_first_pass",
                }
            ],
        },
        "viability_feedback": {
            "vector_id": "illegal_coercion",
            "predicted": 0.0,
            "actual": 0.0,
            "delta": 0.0,
            "failure_modes": ["forbidden_vector_blocked"],
        },
        "status": "accepted",
    }
    drs.write_record(record)
    return record["record_id"]


def _find_deadend_signal(drs: LocalDRS) -> dict | None:
    for record in drs.read_layer("deadends"):
        content = record.get("content") or {}
        if (
            record.get("type") == "dead_end"
            and content.get("vector_id") == "illegal_coercion"
            and content.get("reason") == "forbidden_vector_blocked"
        ):
            return record
    return None


def _status(condition: bool) -> str:
    return "PASS" if condition else "FAIL"


def _sanitize_output(output: str) -> str:
    sanitized = output
    for term in FORBIDDEN_OUTPUT_TERMS:
        sanitized = sanitized.replace(term, "[redacted]")
        sanitized = sanitized.replace(term.upper(), "[redacted]")
    return sanitized


def run_deadend_memory_demo(*, drs_root: Path | None = None) -> str:
    def run_with_root(root_path: Path) -> str:
        drs = LocalDRS(root_path)
        orchestrator = RootOrchestrator(drs=drs, needles_dir=NEEDLES_DIR)

        first_output = orchestrator.process_event(
            raw_user_text="mock certificate request",
            request_id="deadend_demo_first_pass",
            session_anchor="deadend_demo_first_session",
        )
        first_trace = orchestrator.last_trace
        first_blocked = _illegal_coercion_avoided(first_trace)

        deadend_record_id = _write_deadend_signal(
            drs,
            request_id="deadend_demo_first_pass",
        )
        written_record = drs.read_record("deadends", deadend_record_id)
        signal_written = (
            written_record.get("layer") == "deadends"
            and written_record.get("type") == "dead_end"
            and (written_record.get("content") or {}).get("vector_id") == "illegal_coercion"
            and "raw_user_text" not in str(written_record)
        )

        second_output = orchestrator.process_event(
            raw_user_text="mock certificate request",
            request_id="deadend_demo_second_pass",
            session_anchor="deadend_demo_second_session",
        )
        second_trace = orchestrator.last_trace
        remembered_signal = _find_deadend_signal(drs)
        retrieved_signal = deadend_record_id in second_trace.get("memory_source_record_ids", [])
        second_avoidance = _illegal_coercion_avoided(second_trace)
        final_authority = second_output.get("created_by") == "root_orchestrator"

        phases = [
            (
                "first_pass_block",
                first_blocked,
                "illegal_coercion blocked before Architect",
            ),
            (
                "deadend_record_written",
                signal_written,
                "deadend/fraud-like memory signal written",
            ),
            (
                "second_pass_retrieval",
                remembered_signal is not None and retrieved_signal,
                "remembered bad route found",
            ),
            (
                "second_pass_avoidance",
                second_avoidance,
                "illegal_coercion not sent to Architect",
            ),
            (
                "final_authority",
                final_authority,
                "Root created final output",
            ),
        ]

        lines = [
            "[DEADEND MEMORY DEMO]",
            "live_gemini: false",
            "note: demo-level deadend signal, not full Marennya/UP mutation",
            "note: no real external actions",
            "",
            "phase | status | evidence",
            "--- | --- | ---",
        ]
        for phase, condition, evidence in phases:
            lines.append(f"{phase} | {_status(condition)} | {evidence}")

        lines.extend(
            [
                "",
                "[SIGNAL]",
                f"record_id: {deadend_record_id}",
                "layer: deadends",
                "type: dead_end",
                "vector_id: illegal_coercion",
                "reason: forbidden_vector_blocked",
                "demo_created_by: deadend_memory_demo",
                f"retrieved_on_second_pass: {_bool_text(retrieved_signal)}",
                f"architect_received_bad_route: {_bool_text(not second_avoidance)}",
                f"final_output_created_by: {second_output.get('created_by')}",
                f"first_pass_drs_writes: {len(first_output.get('drs_writes', []))}",
                f"second_pass_drs_writes: {len(second_output.get('drs_writes', []))}",
            ]
        )
        return _sanitize_output("\n".join(lines).rstrip() + "\n")

    if drs_root is not None:
        return run_with_root(Path(drs_root))
    with tempfile.TemporaryDirectory(prefix="hedgehog_deadend_demo_drs_") as temp_dir:
        return run_with_root(Path(temp_dir))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Hedgehog OS DeadEnd/Fraud Memory demo.")
    parser.parse_args(argv)
    print(run_deadend_memory_demo(), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
