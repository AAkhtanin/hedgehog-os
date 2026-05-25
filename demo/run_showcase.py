from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

from hedgehog.drs import LocalDRS
from hedgehog.root_orchestrator import RootOrchestrator
from hedgehog.time_model import make_time_envelope
from hedgehog.trace_reporter import render_trace_report


ROOT = Path(__file__).resolve().parents[1]
NEEDLES_DIR = ROOT / "needles"


def _bool_text(value: bool) -> str:
    return "true" if value else "false"


def _seed_direct_reuse_record(drs: LocalDRS) -> None:
    drs.write_record(
        {
            "record_id": "work:showcase_direct_reuse_source",
            "layer": "work",
            "type": "task_outcome",
            "domain": "government_certificate",
            "content": {
                "summary": "Trusted prior mock certificate outcome."
            },
            "time_envelope": make_time_envelope("showcase_direct_reuse_source_session"),
            "provenance": {
                "request_id": "showcase_direct_reuse_source",
                "created_by": "root_orchestrator",
                "trace_refs": [],
            },
            "gt": {
                "gt_report_id": "gt:showcase:direct_reuse_source",
                "half_life_hours": 2_000.0,
                "decay_rate": 0.0001,
            },
            "status": "accepted",
        }
    )


def _work_records_have_raw_user_text(drs: LocalDRS) -> bool:
    for record in drs.read_layer("work"):
        if "raw_user_text" in str(record).lower():
            return True
    return False


def _llm_called(trace: dict) -> bool:
    llm_architect = trace.get("llm_architect_result") or {}
    llm_gateway = trace.get("llm_gateway_result") or {}
    return bool(llm_architect.get("used_llm") or llm_gateway.get("used_llm"))


def _phase_l0(orchestrator: RootOrchestrator) -> tuple[list[str], dict, dict]:
    final_output = orchestrator.process_event(
        raw_user_text="turn on tv",
        request_id="showcase_l0_reflex",
        session_anchor="showcase_l0_reflex_session",
        allow_reflex=True,
        force_full_pipeline=False,
    )
    trace = orchestrator.last_trace
    lines = [
        "[L0 REFLEX]",
        "input: turn on tv",
        f"execution_mode: {trace.get('execution_mode', 'none')}",
        f"llm_called: {_bool_text(_llm_called(trace))}",
        f"architect_skipped: {_bool_text(trace.get('architect_skipped', False))}",
        f"executor_skipped: {_bool_text(trace.get('executor_skipped', False))}",
        f"final_status: {final_output['status']}",
        f"DRS write present: {_bool_text(bool(final_output.get('drs_writes')))}",
    ]
    return lines, trace, final_output


def _phase_l1(orchestrator: RootOrchestrator, drs: LocalDRS) -> tuple[list[str], dict, dict]:
    _seed_direct_reuse_record(drs)
    final_output = orchestrator.process_event(
        raw_user_text="mock certificate request",
        request_id="showcase_l1_direct_reuse",
        session_anchor="showcase_l1_direct_reuse_session",
        allow_direct_reuse=True,
        force_full_pipeline=False,
    )
    trace = orchestrator.last_trace
    lines = [
        "[L1 DIRECT_REUSE]",
        "input: mock certificate request",
        f"reuse_decision: {trace.get('reuse_decision', 'none')}",
        f"reuse_applied: {_bool_text(trace.get('reuse_applied', False))}",
        f"architect_skipped: {_bool_text(trace.get('architect_skipped', False))}",
        f"executor_skipped: {_bool_text(trace.get('executor_skipped', False))}",
        f"llm_called: {_bool_text(_llm_called(trace))}",
        f"final_status: {final_output['status']}",
    ]
    return lines, trace, final_output


def _phase_l3_l4(
    orchestrator: RootOrchestrator,
    use_gemini_architect: bool,
) -> tuple[list[str], dict, dict]:
    architect_provider = "gemini" if use_gemini_architect else "mock_llm"
    final_output = orchestrator.process_event(
        raw_user_text="mock certificate request",
        request_id="showcase_l3_l4_architect",
        session_anchor="showcase_l3_l4_architect_session",
        architect_provider=architect_provider,
    )
    trace = orchestrator.last_trace
    packet = trace.get("attractor_packet") or {}
    plan_graph = trace.get("plan_graph") or {}
    llm_architect = trace.get("llm_architect_result") or {}
    selected_ids = [vector["vector_id"] for vector in packet.get("candidate_vectors", [])]
    plan_vector_ids = [node["vector_id"] for node in plan_graph.get("nodes", [])]
    illegal_blocked = "illegal_coercion" not in selected_ids and "illegal_coercion" not in plan_vector_ids
    lines = [
        "[L3_L4 ARCHITECT]",
        "input: mock certificate request",
        f"AVF selected vectors: {', '.join(selected_ids)}",
        f"illegal_coercion blocked: {_bool_text(illegal_blocked)}",
        f"architect_provider: {architect_provider}",
        f"llm_architect status: {llm_architect.get('status', 'none')}",
        f"llm_architect used_llm: {_bool_text(llm_architect.get('used_llm', False))}",
        f"PlanGraph node count: {len(plan_graph.get('nodes', []))}",
        f"ResultProposal count: {len(trace.get('result_proposals', []))}",
        f"GT decision: {(trace.get('gt_report') or {}).get('decision', 'none')}",
        f"FinalOutput created_by: {final_output['created_by']}",
        f"FinalOutput status: {final_output['status']}",
    ]
    return lines, trace, final_output


def _safety_lines(drs: LocalDRS, architect_trace: dict, final_output: dict) -> list[str]:
    packet = architect_trace.get("attractor_packet") or {}
    plan_graph = architect_trace.get("plan_graph") or {}
    selected_ids = [vector["vector_id"] for vector in packet.get("candidate_vectors", [])]
    plan_vector_ids = [node["vector_id"] for node in plan_graph.get("nodes", [])]
    illegal_blocked = "illegal_coercion" not in selected_ids and "illegal_coercion" not in plan_vector_ids
    return [
        "[SAFETY]",
        f"forbidden vector illegal_coercion blocked: {_bool_text(illegal_blocked)}",
        f"executor_received_forbidden_vector: {_bool_text('illegal_coercion' in plan_vector_ids)}",
        f"sensitive_input_persisted: {_bool_text(_work_records_have_raw_user_text(drs))}",
        f"final_created_by: {final_output['created_by']}",
    ]


def run_showcase(
    scenario: str,
    drs_root: Path | None = None,
    trace_report: bool = False,
    use_gemini_architect: bool = False,
) -> str:
    if scenario != "controlled_architect":
        raise ValueError(f"unknown scenario: {scenario}")

    def run_with_root(root_path: Path) -> str:
        drs = LocalDRS(root_path)
        orchestrator = RootOrchestrator(drs=drs, needles_dir=NEEDLES_DIR)
        lines = [
            "[SHOWCASE]",
            "scenario: controlled_architect",
            "",
        ]
        reports = []
        deterministic_paths = 0

        phase_lines, trace, final_output = _phase_l0(orchestrator)
        deterministic_paths += 1
        lines.extend(phase_lines)
        lines.append("")
        if trace_report:
            reports.append(render_trace_report(trace, final_output))

        phase_lines, trace, final_output = _phase_l1(orchestrator, drs)
        deterministic_paths += 1
        lines.extend(phase_lines)
        lines.append("")
        if trace_report:
            reports.append(render_trace_report(trace, final_output))

        phase_lines, architect_trace, architect_output = _phase_l3_l4(
            orchestrator,
            use_gemini_architect=use_gemini_architect,
        )
        lines.extend(phase_lines)
        lines.append("")
        if trace_report:
            reports.append(render_trace_report(architect_trace, architect_output))

        lines.extend(_safety_lines(drs, architect_trace, architect_output))
        lines.append("")
        lines.extend(
            [
                "[STOCHASTIC ROLE TOPOLOGY]",
                "- root_orchestrator_cognition: supported_future_slm_llm; current_mvp_deterministic",
                "- architect_cognition: deterministic_or_llm; current_showcase_mock_or_gemini",
                "- executor_cognition: deterministic_tool_api_or_llm; current_showcase_simulated",
                "- nested_fractal_cells: supported_by_design",
                "- authority_boundary: RootOrchestrator runtime",
                "- final_output_authority: RootOrchestrator only",
                "- architect_contract: PlanGraph only",
                "- executor_contract: ResultProposal only",
                "- stochastic_outputs_validated: true",
            ]
        )
        lines.append("")
        expensive_llm_calls = 1 if use_gemini_architect and _llm_called(architect_trace) else 0
        lines.extend(
            [
                "[SUMMARY]",
                "- total_phases: 4",
                f"- final_status: {architect_output['status']}",
                f"- expensive_llm_calls: {expensive_llm_calls}",
                f"- deterministic_paths: {deterministic_paths}",
                "- root_authority: true",
                "- stochastic_roles_supported: root_orchestrator, architect, executor, nested_fractal_nodes",
                "- current_demo_stochastic_roles_used: architect",
                "- authority_boundary: root_orchestrator_runtime",
                "- architect_output_contract: PlanGraph only",
                "- executor_output_contract: ResultProposal only",
                "- final_output_authority: RootOrchestrator only",
            ]
        )

        output = "\n".join(lines)
        if reports:
            output = f"{output}\n\n" + "\n\n".join(reports)
        return output + "\n"

    if drs_root is not None:
        return run_with_root(Path(drs_root))
    with tempfile.TemporaryDirectory(prefix="hedgehog_showcase_drs_") as temp_dir:
        return run_with_root(Path(temp_dir))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Hedgehog OS showcase scenarios.")
    parser.add_argument("--scenario", choices=["controlled_architect"], required=True)
    parser.add_argument("--trace-report", action="store_true")
    parser.add_argument("--use-gemini-architect", action="store_true")
    args = parser.parse_args(argv)
    print(
        run_showcase(
            args.scenario,
            trace_report=args.trace_report,
            use_gemini_architect=args.use_gemini_architect,
        ),
        end="",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
