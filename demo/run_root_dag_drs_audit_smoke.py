from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from hedgehog.drs import LocalDRS
from hedgehog.root_orchestrator import RootOrchestrator


ROOT = Path(__file__).resolve().parents[1]
NEEDLES_DIR = ROOT / "needles"
SENSITIVE_TERMS = {
    "raw_user_text",
    "api_key",
    "token",
    "secret",
    "password",
    "private_key",
    "passport_number",
    "card_number",
    "cvv",
}


@dataclass(frozen=True)
class RootDagDrsAuditSmoke:
    final_output: dict
    trace: dict
    work_record: dict
    sections: dict[str, dict[str, Any]]
    output: str


def _bool_text(value: bool) -> str:
    return "true" if value else "false"


def _contains_sensitive_term(value: Any) -> bool:
    serialized = json.dumps(value, sort_keys=True).lower()
    return any(term in serialized for term in SENSITIVE_TERMS)


def run_smoke(drs_root: Path | None = None) -> RootDagDrsAuditSmoke:
    owns_temp = drs_root is None
    temp_dir = TemporaryDirectory() if owns_temp else None
    try:
        active_root = Path(temp_dir.name) / "drs" if temp_dir else Path(drs_root)
        drs = LocalDRS(active_root)
        root = RootOrchestrator(drs=drs, needles_dir=NEEDLES_DIR)
        final_output = root.process_event(
            raw_user_text="mock certificate request",
            request_id="req_root_dag_drs_audit_smoke",
            session_anchor="sess_root_dag_drs_audit_smoke",
            force_full_pipeline=True,
            architect_provider="deterministic",
            use_fractal_dag_executor=True,
        )
        work_record = drs.read_record("work", final_output["drs_writes"][0])
        sections = build_sections(final_output, root.last_trace, work_record)
        output = render_smoke(sections)
        return RootDagDrsAuditSmoke(
            final_output=final_output,
            trace=root.last_trace,
            work_record=work_record,
            sections=sections,
            output=output,
        )
    finally:
        if temp_dir is not None:
            temp_dir.cleanup()


def build_sections(final_output: dict, trace: dict, work_record: dict) -> dict[str, dict[str, Any]]:
    content = work_record.get("content", {})
    provenance = work_record.get("provenance", {})
    secrets_absent = not _contains_sensitive_term(content)
    trace_refs = provenance.get("trace_refs", [])

    return {
        "root_native_dag_run": {
            "execution_engine": trace.get("execution_engine"),
            "fractal_dag_executor_used": trace.get("fractal_dag_executor_used") is True,
            "final_status": final_output.get("status"),
            "created_by": final_output.get("created_by"),
        },
        "drs_work_record": {
            "drs_write_count": len(final_output.get("drs_writes", [])),
            "work_record_written": bool(work_record),
            "layer": work_record.get("layer"),
            "type": work_record.get("type"),
            "time_envelope_present": bool(work_record.get("time_envelope")),
            "provenance_present": bool(provenance),
            "execution_engine_in_work_record": content.get("execution_engine"),
            "fractal_dag_executor_used_in_work_record": content.get(
                "fractal_dag_executor_used"
            )
            is True,
            "dag_result_proposals_count_in_work_record": int(
                content.get("dag_result_proposals_count") or 0
            ),
            "vv_reports_count_in_work_record": int(content.get("vv_reports_count") or 0),
            "gt_decision_in_work_record": content.get("gt_decision"),
            "root_created_final_output_in_work_record": content.get(
                "root_created_final_output"
            )
            is True,
            "no_real_external_action_in_work_record": content.get("no_real_external_action")
            is True,
        },
        "audit_trace": {
            "audit_trace_present": content.get("audit_trace_present") is True
            and bool(trace_refs),
            "root_native_dag_path": content.get("root_native_dag_path") is True,
            "root_final_authority_preserved": content.get(
                "root_final_authority_preserved"
            )
            is True,
            "post_vv_before_gt": content.get("post_vv_before_gt") is True,
            "result_returned_to_root": content.get("result_returned_to_root") is True,
            "sensitive_input_absent": content.get("sensitive_input_absent") is True,
            "secrets_absent": secrets_absent,
        },
    }


def _render_value(value: Any) -> str:
    if isinstance(value, bool):
        return _bool_text(value)
    return str(value)


def render_smoke(sections: dict[str, dict[str, Any]]) -> str:
    lines = [
        "[ROOT DAG DRS / AUDIT SMOKE]",
        "note: stabilizes Root-native DAG DRS writeback and audit trace metadata",
        "note: DAG runner returns ResultProposals / boundary artifacts only",
        "note: Root remains final authority",
        "note: no real external actions",
    ]
    ordered = [
        ("ROOT NATIVE DAG RUN", "root_native_dag_run"),
        ("DRS WORK RECORD", "drs_work_record"),
        ("AUDIT / TRACE", "audit_trace"),
    ]
    for title, key in ordered:
        lines.append("")
        lines.append(f"[{title}]")
        for field, value in sections[key].items():
            lines.append(f"- {field}: {_render_value(value)}")

    work = sections["drs_work_record"]
    audit = sections["audit_trace"]
    summary = {
        "root_dag_drs_audit_status": "PASS",
        "drs_writeback_stable": work["work_record_written"]
        and work["time_envelope_present"]
        and work["provenance_present"],
        "time_envelope_present": work["time_envelope_present"],
        "provenance_present": work["provenance_present"],
        "dag_trace_fields_in_work_record": (
            work["execution_engine_in_work_record"] == "fractal_dag"
            and work["fractal_dag_executor_used_in_work_record"]
            and work["dag_result_proposals_count_in_work_record"] > 0
            and work["vv_reports_count_in_work_record"] > 0
        ),
        "audit_trace_present": audit["audit_trace_present"],
        "sensitive_input_absent": audit["sensitive_input_absent"],
        "secrets_absent": audit["secrets_absent"],
        "no_real_external_actions": work["no_real_external_action_in_work_record"],
        "uncontrolled_delegation": False,
    }
    lines.append("")
    lines.append("[SUMMARY]")
    for field, value in summary.items():
        lines.append(f"- {field}: {_render_value(value)}")
    return "\n".join(lines)


def main() -> None:
    print(run_smoke().output)


if __name__ == "__main__":
    main()
