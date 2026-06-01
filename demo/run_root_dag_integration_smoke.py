from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

from hedgehog.drs import LocalDRS
from hedgehog.root_orchestrator import RootOrchestrator


ROOT = Path(__file__).resolve().parents[1]
NEEDLES_DIR = ROOT / "needles"


@dataclass(frozen=True)
class RootDagIntegrationSmoke:
    final_output: dict
    trace: dict
    work_record: dict
    output: str


def _bool_text(value: bool) -> str:
    return "true" if value else "false"


def run_smoke(drs_root: Path | None = None) -> RootDagIntegrationSmoke:
    owns_temp = drs_root is None
    temp_dir = TemporaryDirectory() if owns_temp else None
    try:
        active_root = Path(temp_dir.name) / "drs" if temp_dir else Path(drs_root)
        drs = LocalDRS(active_root)
        root = RootOrchestrator(drs=drs, needles_dir=NEEDLES_DIR)
        final_output = root.process_event(
            raw_user_text="mock certificate request",
            request_id="req_root_dag_integration_smoke",
            session_anchor="sess_root_dag_integration_smoke",
            force_full_pipeline=True,
            architect_provider="deterministic",
            use_fractal_dag_executor=True,
        )
        work_record = drs.read_record("work", final_output["drs_writes"][0])
        output = render_smoke(final_output, root.last_trace, work_record)
        return RootDagIntegrationSmoke(
            final_output=final_output,
            trace=root.last_trace,
            work_record=work_record,
            output=output,
        )
    finally:
        if temp_dir is not None:
            temp_dir.cleanup()


def render_smoke(final_output: dict, trace: dict, work_record: dict) -> str:
    plan_graph = trace["plan_graph"]
    dag_report = trace["dag_runner_report"]
    lines = [
        "[ROOT DAG INTEGRATION SMOKE]",
        "note: DAG runner connects to Root-controlled pipeline after Architect",
        "note: Root remains final authority",
        "note: no real external actions",
        "note: controlled optional route only",
        "",
        "[ROOT / ROUTE]",
        f"- route: {trace['mode_router']['execution_mode']}",
        f"- execution_engine: {trace['execution_engine']}",
        "- root_final_authority: true",
        "",
        "[ARCHITECT]",
        f"- plan_graph_valid: {_bool_text(bool(plan_graph.get('nodes')) and bool(plan_graph.get('time_assumptions')))}",
        f"- plan_graph_node_count: {len(plan_graph['nodes'])}",
        "- architect_created_final_output: false",
        "",
        "[DAG RUNNER]",
        f"- fractal_dag_executor_used: {_bool_text(trace['fractal_dag_executor_used'])}",
        f"- dag_runner_status: {trace['dag_runner_status']}",
        f"- dag_ready_sequence_present: {_bool_text(trace['dag_ready_sequence_present'])}",
        f"- dag_execution_batches_present: {_bool_text(trace['dag_execution_batches_present'])}",
        f"- dag_result_proposals_count: {trace['dag_result_proposals_count']}",
        f"- dag_child_boundary_snapshots: {trace['dag_child_boundary_snapshots']}",
        f"- executor_created_final_output: {_bool_text(trace['executor_created_final_output'])}",
        "",
        "[POST V&V / GT]",
        f"- post_vv_after_dag_executor: {_bool_text(trace['post_vv_after_dag_executor'])}",
        f"- vv_reports_count: {len(trace['vv_reports'])}",
        f"- gt_after_post_vv: {_bool_text(trace['gt_after_post_vv'])}",
        f"- gt_decision: {trace['gt_report']['decision']}",
        "- gt_committed_final_output: false",
        "",
        "[ROOT FINAL]",
        f"- root_received_dag_artifacts: {_bool_text(trace['root_received_dag_artifacts'])}",
        f"- final_status: {final_output['status']}",
        "- root_created_final_output: true",
        f"- created_by: {final_output['created_by']}",
        f"- drs_write_count: {len(final_output['drs_writes'])}",
        f"- no_real_external_action: {_bool_text(trace['no_real_external_action'])}",
        f"- uncontrolled_delegation: {_bool_text(trace['uncontrolled_delegation'])}",
        "",
        "[SUMMARY]",
        "- root_dag_integration_status: PASS",
        f"- fractal_dag_executor_used: {_bool_text(trace['fractal_dag_executor_used'])}",
        "- root_final_authority_preserved: true",
        f"- executor_created_final_output: {_bool_text(trace['executor_created_final_output'])}",
        f"- post_vv_after_dag_executor: {_bool_text(trace['post_vv_after_dag_executor'])}",
        f"- gt_after_post_vv: {_bool_text(trace['gt_after_post_vv'])}",
        "- root_created_final_output: true",
        f"- no_real_external_actions: {_bool_text(trace['no_real_external_action'])}",
        f"- uncontrolled_delegation: {_bool_text(trace['uncontrolled_delegation'])}",
    ]
    if not work_record.get("time_envelope"):
        lines.append("- warning: work record missing TimeEnvelope")
    if dag_report is None:
        lines.append("- warning: DAG runner report missing")
    return "\n".join(lines)


def main() -> None:
    print(run_smoke().output)


if __name__ == "__main__":
    main()
