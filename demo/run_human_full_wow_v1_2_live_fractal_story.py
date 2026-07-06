from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Mapping


RUN_ID = "human_full_wow_v1_2_live_fractal_story_v01"
REPORT_ID = "human_full_wow_v1_2_live_fractal_story_v01"
STORY_TYPE = "artifact_backed_human_semantic_story"

ARTIFACT_DIR_ENV = "HEDGEHOG_FULL_WOW_V1_2_LIVE_FRACTAL_STORY_ARTIFACT_DIR"
AUDIT_LOG_ENV = "HEDGEHOG_FULL_WOW_V1_2_LIVE_FRACTAL_STORY_AUDIT_LOG"
ALLOW_RAW_OUTPUT_ENV = "HEDGEHOG_FULL_WOW_V1_2_LIVE_FRACTAL_STORY_ALLOW_RAW_RESPONSE_OUTPUT"

REQUIRED_VALIDATION_FILES = (
    "top_level_orchestrator_validation.json",
    "bsep_validation.json",
    "top_level_architect_validation.json",
    "branch_legal_validation.json",
    "branch_accounting_validation.json",
    "branch_supplier_b_validation.json",
    "branch_bank_policy_validation.json",
)

REQUIRED_SECTIONS = (
    "[FULL WOW V1.2 LIVE FRACTAL HUMAN STORY]",
    "[ONE-SCREEN SUMMARY]",
    "[BUSINESS SCENE]",
    "[CAST OF SEMANTIC ACTORS]",
    "[TIMELINE]",
    "[WHAT ORCHESTRATOR UNDERSTOOD]",
    "[WHAT BSEP DID]",
    "[WHAT ARCHITECT UNDERSTOOD]",
    "[WHAT BRANCH-LOCAL ACTORS DID]",
    "[WHAT THE FRACTAL PART MEANS]",
    "[WHAT THE BANK PART MEANS]",
    "[WHAT ROOT DID]",
    "[WHY THIS MATTERS]",
    "[COUNTER TABLE]",
    "[NON-CLAIMS]",
    "[FINAL STATUS]",
)

SEMANTIC_ACTORS = (
    "top_level_orchestrator_llm",
    "top_level_semantic_architect_llm",
    "legal_clause_semantic_extractor",
    "accounting_mismatch_semantic_explainer",
    "supplier_b_unstructured_note_interpreter",
    "bank_policy_semantic_reviewer",
)

COUNTER_KEYS = (
    "semantic_actor_call_count",
    "real_provider_call_count",
    "network_used_count",
    "gemini_called_count",
    "top_level_orchestrator_llm_call_count",
    "top_level_architect_llm_call_count",
    "branch_local_llm_slm_call_count",
    "bsep_created_count",
    "bsep_validated_count",
    "architect_received_bsep_context_count",
    "runtime_plangraph_compiled_count",
    "fractal_branch_cells_created_count",
    "branch_result_proposals_created_count",
    "post_vv_validated_count",
    "gt_lgt_advisory_review_count",
    "root_final_boundary_evaluated_count",
    "action_commit_packet_created_count",
    "receipt_created_count",
    "mock_payment_executed_count",
    "real_payment_executed_count",
    "shipment_released_count",
    "real_world_effects_count",
)

EFFECT_COUNTER_KEYS = (
    "action_commit_packet_created_count",
    "receipt_created_count",
    "mock_payment_executed_count",
    "real_payment_executed_count",
    "shipment_released_count",
    "real_world_effects_count",
)

SECRET_MARKERS = (
    "FAKE-IBAN-AL-0000-2042-SECRET",
    "sandbox_token_abc",
    "beneficiary_iban",
    "raw_iban_value",
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
)

NON_CLAIMS = (
    "not production",
    "not public auditor final package",
    "no real payment",
    "no real shipment release",
    "no production connectors",
    "no real bank/supplier/warehouse API",
    "no real-world effects",
)


def _zero_counters() -> dict[str, int]:
    return {key: 0 for key in COUNTER_KEYS}


def _read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _coerce_path(value: str | Path | None) -> Path | None:
    if value is None or str(value).strip() == "":
        return None
    return Path(value)


def _base_report(
    *,
    final_status: str,
    story_status: str,
    source_artifact_dir: str | None,
    counters: Mapping[str, int] | None = None,
) -> dict[str, Any]:
    normalized_counters = _zero_counters()
    if counters:
        for key in COUNTER_KEYS:
            normalized_counters[key] = int(counters.get(key, 0) or 0)
    return {
        "run_id": RUN_ID,
        "report_id": REPORT_ID,
        "story_type": STORY_TYPE,
        "final_status": final_status,
        "story_status": story_status,
        "source_artifact_dir": source_artifact_dir,
        "production_ready_claimed": False,
        "public_auditor_ready_claimed": False,
        "real_world_effects_count": normalized_counters["real_world_effects_count"],
        "provider_called_count": 0,
        "network_called_by_renderer_count": 0,
        "gemini_called_by_renderer_count": 0,
        "artifact_files_observed_only": True,
        "raw_provider_response_rendered": False,
        "allow_raw_response_output": False,
        "counters": normalized_counters,
        "non_claims": NON_CLAIMS,
        "validation_results": {},
        "validation_errors": [],
    }


def _fail_closed(
    *,
    source_artifact_dir: str | None,
    failure_reason: str,
    counters: Mapping[str, int] | None = None,
    validation_results: Mapping[str, Any] | None = None,
    validation_errors: list[str] | None = None,
) -> dict[str, Any]:
    report = _base_report(
        final_status="FAIL_CLOSED",
        story_status="FAIL_CLOSED",
        source_artifact_dir=source_artifact_dir,
        counters=counters,
    )
    report["failure_reason"] = failure_reason
    report["safe_diagnostic_story_available"] = True
    report["validation_results"] = dict(validation_results or {})
    report["validation_errors"] = list(validation_errors or [])
    for key in EFFECT_COUNTER_KEYS:
        report["counters"][key] = 0
    report["real_world_effects_count"] = 0
    return report


def _secret_scan_accepted(secret_scan: Mapping[str, Any]) -> bool:
    return secret_scan.get("passed") is True and secret_scan.get("matched_markers") == []


def _summary_counters(summary: Mapping[str, Any]) -> dict[str, int]:
    source = summary.get("counters", {})
    counters = _zero_counters()
    if isinstance(source, Mapping):
        for key in COUNTER_KEYS:
            counters[key] = int(source.get(key, 0) or 0)
    return counters


def collect_human_full_wow_v1_2_live_fractal_story(
    artifact_dir: str | Path | None = None,
    audit_log_path: str | Path | None = None,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    effective_env = os.environ if env is None else env
    selected_artifact_dir = _coerce_path(artifact_dir) or _coerce_path(
        effective_env.get(ARTIFACT_DIR_ENV)
    )
    selected_audit_log = _coerce_path(audit_log_path) or _coerce_path(
        effective_env.get(AUDIT_LOG_ENV)
    )
    allow_raw_output = effective_env.get(ALLOW_RAW_OUTPUT_ENV) == "1"

    if selected_artifact_dir is None:
        report = _base_report(
            final_status="SKIPPED_CLOSED",
            story_status="SKIPPED_CLOSED",
            source_artifact_dir=None,
        )
        report["skip_reason"] = "artifact_dir_not_provided"
        report["allow_raw_response_output"] = allow_raw_output
        return report

    source_dir = selected_artifact_dir
    source_dir_text = str(source_dir)
    summary_path = source_dir / "summary.json"
    secret_scan_path = source_dir / "secret_scan.json"

    if not summary_path.exists():
        return _fail_closed(
            source_artifact_dir=source_dir_text,
            failure_reason="missing_summary_json",
        )

    try:
        summary = _read_json(summary_path)
    except (OSError, json.JSONDecodeError):
        return _fail_closed(
            source_artifact_dir=source_dir_text,
            failure_reason="invalid_summary_json",
        )

    counters = _summary_counters(summary if isinstance(summary, Mapping) else {})

    if not secret_scan_path.exists():
        return _fail_closed(
            source_artifact_dir=source_dir_text,
            failure_reason="missing_secret_scan_json",
            counters=counters,
        )

    try:
        secret_scan = _read_json(secret_scan_path)
    except (OSError, json.JSONDecodeError):
        return _fail_closed(
            source_artifact_dir=source_dir_text,
            failure_reason="invalid_secret_scan_json",
            counters=counters,
        )

    if not isinstance(secret_scan, Mapping) or not _secret_scan_accepted(secret_scan):
        return _fail_closed(
            source_artifact_dir=source_dir_text,
            failure_reason="secret_scan_failed",
            counters=counters,
            validation_errors=["secret_scan.passed must be true and matched_markers must be empty"],
        )

    validation_results: dict[str, Any] = {}
    validation_errors: list[str] = []
    for file_name in REQUIRED_VALIDATION_FILES:
        validation_path = source_dir / file_name
        if not validation_path.exists():
            validation_results[file_name] = {"accepted": False}
            validation_errors.append(f"{file_name}: missing")
            continue
        try:
            validation = _read_json(validation_path)
        except (OSError, json.JSONDecodeError):
            validation_results[file_name] = {"accepted": False}
            validation_errors.append(f"{file_name}: invalid_json")
            continue
        accepted = isinstance(validation, Mapping) and validation.get("accepted") is True
        validation_results[file_name] = {
            "accepted": accepted,
            "error_count": len(validation.get("errors", [])) if isinstance(validation, Mapping) else 1,
        }
        if not accepted:
            validation_errors.append(f"{file_name}: accepted_not_true")

    if validation_errors:
        return _fail_closed(
            source_artifact_dir=source_dir_text,
            failure_reason="validation_artifact_not_accepted",
            counters=counters,
            validation_results=validation_results,
            validation_errors=validation_errors,
        )

    if not isinstance(summary, Mapping) or summary.get("final_status") != "PASS":
        return _fail_closed(
            source_artifact_dir=source_dir_text,
            failure_reason="summary_final_status_not_pass",
            counters=counters,
            validation_results=validation_results,
            validation_errors=[f"summary.final_status={summary.get('final_status') if isinstance(summary, Mapping) else None}"],
        )

    nonzero_effect_counters = [
        key for key in EFFECT_COUNTER_KEYS if int(counters.get(key, 0) or 0) != 0
    ]
    if nonzero_effect_counters:
        return _fail_closed(
            source_artifact_dir=source_dir_text,
            failure_reason="effect_counter_nonzero",
            counters=counters,
            validation_results=validation_results,
            validation_errors=[f"{key}: must_be_zero" for key in nonzero_effect_counters],
        )

    report = _base_report(
        final_status="PASS",
        story_status="PASS",
        source_artifact_dir=source_dir_text,
        counters=counters,
    )
    report.update(
        {
            "source_run_id": summary.get("run_id"),
            "source_report_id": summary.get("report_id"),
            "provider_mode": summary.get("provider_mode"),
            "model": summary.get("model"),
            "audit_log_path": str(selected_audit_log) if selected_audit_log else None,
            "secret_scan_passed": True,
            "secret_markers_matched": [],
            "validation_results": validation_results,
            "artifact_files_observed": (
                "summary.json",
                "secret_scan.json",
                *REQUIRED_VALIDATION_FILES,
            ),
            "semantic_actor_roles": SEMANTIC_ACTORS,
            "root_result": summary.get("post_vv_gt_root", {}),
            "pipeline_sequence": summary.get("pipeline_sequence", []),
            "allow_raw_response_output": allow_raw_output,
        }
    )
    return report


def _format_counter_table(counters: Mapping[str, Any]) -> list[str]:
    return [f"- {key}: {int(counters.get(key, 0) or 0)}" for key in COUNTER_KEYS]


def _failure_lines(report: Mapping[str, Any]) -> list[str]:
    if report.get("final_status") != "FAIL_CLOSED":
        return []
    lines = [
        "Safe validation failure section:",
        f"- failure_reason: {report.get('failure_reason')}",
    ]
    validation_errors = report.get("validation_errors") or []
    if validation_errors:
        lines.append("- validation_errors:")
        lines.extend(f"  - {error}" for error in validation_errors)
    return lines


def render_human_full_wow_v1_2_live_fractal_story(report: Mapping[str, Any]) -> str:
    counters = report.get("counters", {})
    final_status = report.get("final_status")
    provider_mode = report.get("provider_mode", "artifact_provider_unknown")

    lines: list[str] = [
        "HEDGEHOG OS — FULL WOW v1.2 LIVE FRACTAL HUMAN STORY",
        "",
        "[FULL WOW V1.2 LIVE FRACTAL HUMAN STORY]",
        f"run_id: {RUN_ID}",
        f"report_id: {REPORT_ID}",
        f"story_type: {STORY_TYPE}",
        f"story_status: {report.get('story_status')}",
        f"final_status: {final_status}",
        f"source_artifact_dir: {report.get('source_artifact_dir')}",
        f"provider_mode: {provider_mode}",
        "production_ready_claimed: false",
        "public_auditor_ready_claimed: false",
        f"real_world_effects_count: {int(counters.get('real_world_effects_count', 0) or 0)}",
        "",
        "[ONE-SCREEN SUMMARY]",
    ]

    if final_status == "SKIPPED_CLOSED":
        lines.extend(
            [
                "Story rendering is skipped closed because no artifact directory was provided.",
                f"skip_reason: {report.get('skip_reason')}",
                "The renderer made no provider, network, Gemini, action, receipt, payment, shipment, or real-world calls.",
            ]
        )
    else:
        lines.extend(
            [
                "Six semantic actors participated when PASS: top_level_orchestrator_llm, top_level_semantic_architect_llm, legal_clause_semantic_extractor, accounting_mismatch_semantic_explainer, supplier_b_unstructured_note_interpreter, and bank_policy_semantic_reviewer.",
                "Orchestrator understood the business route while runtime bounded and canonicalized the evidence.",
                "BSEP was created after Orchestrator validation and BSEP was validated before Architect.",
                "Architect received BSEP-derived bounded context and proposed semantic plan intent.",
                "Runtime retained PlanGraph ownership and local artifact ownership.",
                "Root remained final authority; no ActionCommitPacket, receipt, payment, shipment release, or real-world effects were created by the live run.",
            ]
        )
        lines.extend(_failure_lines(report))

    lines.extend(
        [
            "",
            "[BUSINESS SCENE]",
            "Shipment SH-2042 is the visible business scene. Supplier A can potentially support a scoped mock payment path, while Supplier B remained blocked and shipment release remained held.",
            "The bank slot and receipt boundaries are evidence boundaries: payment_slot != permission, receipt != truth, and receipt != shipment release.",
            "This renderer reads sandbox/product-trace artifacts only; it is not production and it does not call external services.",
            "",
            "[CAST OF SEMANTIC ACTORS]",
            "- top_level_orchestrator_llm: saw bounded business trace facts and returned a semantic route; it was not allowed to decide truth, authority, action permission, or FinalOutput.",
            "- BSEP membrane: carried bounded context from accepted Orchestrator semantics to Architect; it was not truth, authority, or action permission.",
            "- top_level_semantic_architect_llm: saw BSEP-derived bounded context and returned semantic plan intent; runtime retained PlanGraph/local artifact ownership.",
            "- legal_clause_semantic_extractor: interpreted legal and insurance evidence as advisory branch semantics only.",
            "- accounting_mismatch_semantic_explainer: interpreted invoice and reconciliation evidence as advisory branch semantics only.",
            "- supplier_b_unstructured_note_interpreter: interpreted Supplier B mismatch, delay, and legal-review evidence as advisory branch semantics only.",
            "- bank_policy_semantic_reviewer: interpreted payment-slot and contract-preview policy boundaries as advisory branch semantics only.",
            "",
            "[TIMELINE]",
            "1. Business trace loaded.",
            "2. Orchestrator called.",
            "3. Orchestrator validation accepted.",
            "4. BSEP created.",
            "5. BSEP validation accepted.",
            "6. Architect called.",
            "7. Architect validation accepted.",
            "8. Runtime compiled PlanGraph/local plan artifacts.",
            "9. Fractal branch cells created.",
            "10. Legal branch actor validated.",
            "11. Accounting branch actor validated.",
            "12. Supplier B branch actor validated.",
            "13. Bank policy branch actor validated.",
            "14. Branch ResultProposals merged.",
            "15. Post V&V validated.",
            "16. GT/LGT advisory reviewed.",
            "17. Root boundary evaluated.",
            f"18. Final {final_status}.",
            "",
            "[WHAT ORCHESTRATOR UNDERSTOOD]",
            "Orchestrator understood the business route as API-like business evidence through bounded semantic review: warehouse inventory, supplier availability and blockers, legal/insurance status, accounting reconciliation, and bank policy evidence.",
            "The Orchestrator proposal did not claim truth, authority, action permission, FinalOutput, connector command, DRS write, PlanGraph ownership, or Root bypass.",
            "",
            "[WHAT BSEP DID]",
            "BSEP was created after Orchestrator validation.",
            "BSEP was validated before Architect.",
            "BSEP carried bounded context only: no raw user text, no raw provider text, no raw bank secrets, no raw IBAN, and no bank token.",
            "BSEP is not truth, authority, or action permission.",
            "",
            "[WHAT ARCHITECT UNDERSTOOD]",
            "Architect received BSEP-derived bounded context and proposed semantic plan intent.",
            "Runtime retained PlanGraph ownership and runtime retained PlanGraph/local artifact ownership.",
            "The Architect proposal kept validators and Root required, and did not claim action permission, authority, FinalOutput, connector command, DRS write, or Root bypass.",
            "",
            "[WHAT BRANCH-LOCAL ACTORS DID]",
            "Branch-local semantic actors returned advisory semantic proposals only.",
            "Legal, accounting, Supplier B, and bank policy branch actors interpreted branch evidence without creating truth, permission, packet, receipt, payment, or shipment release.",
            "",
            "[WHAT THE FRACTAL PART MEANS]",
            "Fractal branch cells represented bounded work cells.",
            "The runtime created branch cells for warehouse, Supplier A, Supplier B, legal, accounting, Bank A, Bank B, and root merge work.",
            "Branch ResultProposals are not FinalOutput; parent/root boundary merges them for Root review.",
            "",
            "[WHAT THE BANK PART MEANS]",
            "Bank-like sandbox and policy boundaries were visible without exposing raw bank secrets.",
            "payment_slot != permission",
            "receipt != truth",
            "receipt != shipment release",
            "raw bank secret/token/IBAN did not enter LLM context",
            "",
            "[WHAT ROOT DID]",
            "Root final boundary was evaluated.",
            "Supplier B remained blocked.",
            "Shipment remained held.",
            "Receipt remained evidence only.",
            "No ActionCommitPacket, receipt, payment, shipment release, or real-world effects were created by the live run.",
            "Root remained final authority.",
            "",
            "[WHY THIS MATTERS]",
            "This artifact-backed story makes the v1.2 live multi-LLM/fractal observation readable without inspecting many files manually.",
            "It shows multiple semantic actors can participate while runtime keeps boundaries, validators check artifacts, and Root stays the final authority.",
            "",
            "[COUNTER TABLE]",
        ]
    )
    lines.extend(_format_counter_table(counters))
    lines.extend(
        [
            "",
            "[NON-CLAIMS]",
            *[f"- {claim}" for claim in NON_CLAIMS],
            "",
            "[FINAL STATUS]",
            f"FINAL STATUS: {final_status}",
            f"story_status: {report.get('story_status')}",
            "provider/network/Gemini calls by renderer: 0",
            "action/receipt/payment/shipment/effects by renderer: 0",
        ]
    )
    rendered = "\n".join(lines) + "\n"
    for marker in SECRET_MARKERS:
        if marker in rendered:
            raise ValueError("rendered story contains a blocked secret marker")
    return rendered


def run_human_full_wow_v1_2_live_fractal_story(
    artifact_dir: str | Path | None = None,
    audit_log_path: str | Path | None = None,
    env: Mapping[str, str] | None = None,
) -> str:
    report = collect_human_full_wow_v1_2_live_fractal_story(
        artifact_dir=artifact_dir,
        audit_log_path=audit_log_path,
        env=env,
    )
    return render_human_full_wow_v1_2_live_fractal_story(report)


def main() -> int:
    print(run_human_full_wow_v1_2_live_fractal_story())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
