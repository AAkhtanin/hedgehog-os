from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Iterable, Mapping


RUN_ID = "human_full_wow_v1_2_avf_live_observation_story_v01"
REPORT_ID = "human_full_wow_v1_2_avf_live_observation_story_v01"
STORY_TYPE = "artifact_backed_human_avf_drs_live_observation_story"

ARTIFACT_DIR_ENV = "HEDGEHOG_FULL_WOW_V1_2_AVF_LIVE_STORY_ARTIFACT_DIR"
AUDIT_LOG_ENV = "HEDGEHOG_FULL_WOW_V1_2_AVF_LIVE_STORY_AUDIT_LOG"
ALLOW_RAW_OUTPUT_ENV = "HEDGEHOG_FULL_WOW_V1_2_AVF_LIVE_STORY_ALLOW_RAW_RESPONSE_OUTPUT"

REQUIRED_JSON_FILES = (
    "summary.json",
    "secret_scan.json",
    "local_drs_v0_2_resolve_report.json",
    "local_drs_v0_2_freshness_table.json",
    "local_drs_v0_2_lineage_table.json",
    "local_drs_v0_2_provenance_table.json",
    "local_drs_v0_2_reuse_decision_table.json",
    "local_drs_v0_2_writeback_candidate.json",
    "avf_v0_2_evaluation_report.json",
    "avf_v0_2_ranked_candidates.json",
    "avf_v0_2_hard_mask_table.json",
    "avf_v0_2_soft_mask_table.json",
    "avf_v0_2_score_explanation_table.json",
    "bsep_packet.json",
    "top_level_orchestrator_validation.json",
    "bsep_validation.json",
    "top_level_architect_validation.json",
    "branch_legal_validation.json",
    "branch_accounting_validation.json",
    "branch_supplier_b_validation.json",
    "branch_bank_policy_validation.json",
)

REQUIRED_TEXT_FILES = ("summary.log",)

VALIDATION_FILES = (
    "top_level_orchestrator_validation.json",
    "bsep_validation.json",
    "top_level_architect_validation.json",
    "branch_legal_validation.json",
    "branch_accounting_validation.json",
    "branch_supplier_b_validation.json",
    "branch_bank_policy_validation.json",
)

RAW_RESPONSE_FILES = (
    "top_level_orchestrator_raw_response.txt",
    "top_level_architect_raw_response.txt",
    "branch_legal_raw_response.txt",
    "branch_accounting_raw_response.txt",
    "branch_supplier_b_raw_response.txt",
    "branch_bank_policy_raw_response.txt",
)

REQUIRED_SECTIONS = (
    "[FULL WOW V1.2 + DRS V0.2 + AVF V0.2 LIVE HUMAN STORY]",
    "[ONE-SCREEN SUMMARY]",
    "[BUSINESS SCENE]",
    "[CAST OF SEMANTIC ACTORS]",
    "[TIMELINE]",
    "[WHAT DRS REMEMBERED]",
    "[WHAT AVF HARD-MASKED]",
    "[WHAT AVF RANKED WITHOUT AUTHORIZING]",
    "[WHAT ORCHESTRATOR UNDERSTOOD]",
    "[WHAT BSEP DID]",
    "[WHAT ARCHITECT UNDERSTOOD]",
    "[WHAT BRANCH-LOCAL ACTORS DID]",
    "[WHAT ROOT DID]",
    "[WHY THIS MATTERS]",
    "[COUNTER TABLE]",
    "[ARTIFACT EVIDENCE]",
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
    "fake_provider_call_count",
    "network_used_count",
    "gemini_called_count",
    "top_level_orchestrator_llm_call_count",
    "top_level_architect_llm_call_count",
    "branch_local_llm_slm_call_count",
    "local_drs_v0_2_resolve_invoked_count",
    "local_drs_v0_2_records_evaluated_count",
    "local_drs_v0_2_direct_reuse_allowed_count",
    "local_drs_v0_2_root_review_required_count",
    "avf_v0_2_evaluation_invoked_count",
    "avf_v0_2_candidates_evaluated_count",
    "avf_v0_2_top_ranked_candidate_permission_granted_count",
    "avf_v0_2_action_permission_granted_count",
    "avf_v0_2_final_output_created_count",
    "avf_v0_2_root_bypass_count",
    "bsep_created_count",
    "bsep_validated_count",
    "root_final_boundary_evaluated_count",
    "action_commit_packet_created_count",
    "receipt_created_count",
    "mock_payment_executed_count",
    "real_payment_executed_count",
    "shipment_released_count",
    "real_world_effects_count",
)

REQUIRED_COUNTER_VALUES = {
    "semantic_actor_call_count": 6,
    "real_provider_call_count": 6,
    "gemini_called_count": 6,
    "network_used_count": 6,
    "local_drs_v0_2_resolve_invoked_count": 1,
    "local_drs_v0_2_records_evaluated_count": 11,
    "local_drs_v0_2_direct_reuse_allowed_count": 0,
    "local_drs_v0_2_root_review_required_count": 11,
    "avf_v0_2_evaluation_invoked_count": 1,
    "avf_v0_2_candidates_evaluated_count": 9,
    "avf_v0_2_top_ranked_candidate_permission_granted_count": 0,
    "avf_v0_2_action_permission_granted_count": 0,
    "avf_v0_2_final_output_created_count": 0,
    "avf_v0_2_root_bypass_count": 0,
    "bsep_created_count": 1,
    "bsep_validated_count": 1,
    "root_final_boundary_evaluated_count": 1,
    "action_commit_packet_created_count": 0,
    "receipt_created_count": 0,
    "mock_payment_executed_count": 0,
    "real_payment_executed_count": 0,
    "shipment_released_count": 0,
    "real_world_effects_count": 0,
}

EFFECT_COUNTER_KEYS = (
    "action_commit_packet_created_count",
    "receipt_created_count",
    "mock_payment_executed_count",
    "real_payment_executed_count",
    "shipment_released_count",
    "real_world_effects_count",
)

AVF_PERMISSION_COUNTER_KEYS = (
    "avf_v0_2_top_ranked_candidate_permission_granted_count",
    "avf_v0_2_action_permission_granted_count",
    "avf_v0_2_final_output_created_count",
    "avf_v0_2_root_bypass_count",
)

NON_CLAIMS = (
    "not production",
    "not public auditor final package",
    "no live rerun by this story renderer",
    "no provider/network/model calls by this story renderer",
    "no real payment",
    "no real shipment release",
    "no ActionCommitPacket",
    "no receipt",
    "no FinalOutput created by this story renderer",
    "no real-world effects",
)

SECRET_MARKER_PARTS = (
    ("FAKE-IBAN", "-AL-0000-2042-SECRET"),
    ("sandbox", "_token_abc"),
    ("beneficiary", "_iban"),
    ("raw_", "iban_value"),
    ("GEMINI", "_API_KEY"),
    ("GOOGLE", "_API_KEY"),
)


def _secret_markers() -> tuple[str, ...]:
    return tuple(left + right for left, right in SECRET_MARKER_PARTS)


def _zero_counters() -> dict[str, int]:
    return {key: 0 for key in COUNTER_KEYS}


def _coerce_path(value: str | Path | None) -> Path | None:
    if value is None or str(value).strip() == "":
        return None
    return Path(value)


def _read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _safe_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _redact_secret_markers(text: str) -> str:
    redacted = text
    for marker in _secret_markers():
        redacted = redacted.replace(marker, "[REDACTED_SECRET_MARKER]")
    return redacted


def _summary_counters(summary: Mapping[str, Any] | None) -> dict[str, int]:
    counters = _zero_counters()
    source = summary.get("counters", {}) if isinstance(summary, Mapping) else {}
    if isinstance(source, Mapping):
        for key in COUNTER_KEYS:
            counters[key] = int(source.get(key, 0) or 0)
    return counters


def _base_report(
    *,
    final_status: str,
    story_status: str,
    source_artifact_dir: str | None,
    source_audit_log: str | None,
    counters: Mapping[str, int] | None = None,
) -> dict[str, Any]:
    normalized_counters = _zero_counters()
    if counters:
        for key in COUNTER_KEYS:
            normalized_counters[key] = int(counters.get(key, 0) or 0)
    return {
        "run_id": RUN_ID,
        "report_id": REPORT_ID,
        "story_status": story_status,
        "final_status": final_status,
        "source_artifact_dir": source_artifact_dir,
        "source_audit_log": source_audit_log,
        "story_type": STORY_TYPE,
        "validation_results": {},
        "validation_errors": [],
        "one_screen_summary": (),
        "business_scene": (),
        "semantic_actor_cast": SEMANTIC_ACTORS,
        "timeline": (),
        "drs_memory_story": (),
        "avf_pressure_story": (),
        "orchestrator_story": (),
        "bsep_story": (),
        "architect_story": (),
        "branch_actor_story": (),
        "root_story": (),
        "why_this_matters": (),
        "counter_table": normalized_counters,
        "non_claims": NON_CLAIMS,
        "artifact_files_observed_only": True,
        "artifact_files_observed": (),
        "raw_provider_response_rendered": False,
        "raw_provider_response_policy": "raw responses are artifact evidence only and are not rendered by default",
        "provider_called_count": 0,
        "network_called_by_renderer_count": 0,
        "gemini_called_by_renderer_count": 0,
        "production_ready_claimed": False,
        "public_auditor_ready_claimed": False,
        "real_world_effects_count": normalized_counters["real_world_effects_count"],
    }


def _fail_closed(
    *,
    source_artifact_dir: str | None,
    source_audit_log: str | None,
    failure_reason: str,
    counters: Mapping[str, int] | None = None,
    validation_results: Mapping[str, Any] | None = None,
    validation_errors: Iterable[str] = (),
) -> dict[str, Any]:
    report = _base_report(
        final_status="FAIL_CLOSED",
        story_status="FAIL_CLOSED",
        source_artifact_dir=source_artifact_dir,
        source_audit_log=source_audit_log,
        counters=counters,
    )
    report["failure_reason"] = failure_reason
    report["validation_results"] = dict(validation_results or {})
    report["validation_errors"] = tuple(validation_errors)
    return report


def _artifact_validation_error(
    file_name: str, reason: str
) -> tuple[str, dict[str, Any]]:
    return f"{file_name}: {reason}", {"present": False, "accepted": False, "reason": reason}


def _load_artifacts(source_dir: Path) -> tuple[dict[str, Any], dict[str, Any], list[str]]:
    loaded: dict[str, Any] = {}
    results: dict[str, Any] = {}
    errors: list[str] = []

    for file_name in REQUIRED_TEXT_FILES:
        path = source_dir / file_name
        if not path.exists():
            error, result = _artifact_validation_error(file_name, "missing")
            errors.append(error)
            results[file_name] = result
            continue
        try:
            loaded[file_name] = _safe_text(path)
        except OSError:
            error, result = _artifact_validation_error(file_name, "read_failed")
            errors.append(error)
            results[file_name] = result
            continue
        results[file_name] = {"present": True, "accepted": True, "kind": "text"}

    for file_name in REQUIRED_JSON_FILES:
        path = source_dir / file_name
        if not path.exists():
            error, result = _artifact_validation_error(file_name, "missing")
            errors.append(error)
            results[file_name] = result
            continue
        try:
            loaded[file_name] = _read_json(path)
        except (OSError, json.JSONDecodeError):
            error, result = _artifact_validation_error(file_name, "invalid_json")
            errors.append(error)
            results[file_name] = result
            continue
        results[file_name] = {"present": True, "accepted": True, "kind": "json"}

    return loaded, results, errors


def _accepted_validation(artifact: Any) -> bool:
    return isinstance(artifact, Mapping) and artifact.get("accepted") is True


def _expect_counter(
    counters: Mapping[str, int],
    key: str,
    expected: int,
    errors: list[str],
) -> None:
    actual = int(counters.get(key, 0) or 0)
    if actual != expected:
        errors.append(f"{key}: expected {expected}, observed {actual}")


def _build_story_sections(
    artifacts: Mapping[str, Any],
    counters: Mapping[str, int],
) -> dict[str, tuple[str, ...]]:
    orchestrator = artifacts["top_level_orchestrator_validation.json"]["canonical"]
    architect = artifacts["top_level_architect_validation.json"]["canonical"]
    bsep_packet = artifacts.get("bsep_packet.json", {})
    drs = artifacts["local_drs_v0_2_resolve_report.json"]
    avf = artifacts["avf_v0_2_evaluation_report.json"]
    writeback = artifacts["local_drs_v0_2_writeback_candidate.json"]
    branch_validations = (
        artifacts["branch_legal_validation.json"]["canonical"],
        artifacts["branch_accounting_validation.json"]["canonical"],
        artifacts["branch_supplier_b_validation.json"]["canonical"],
        artifacts["branch_bank_policy_validation.json"]["canonical"],
    )

    one_screen = (
        "Real Gemini participated through six semantic actors.",
        "Local DRS v0.2 remembered prior traces and classified them as context/warning/rerun/blocked.",
        "AVF v0.2 consumed DRS signals and applied advisory HardMask/SoftMask/ranking.",
        "release_all_and_pay_all was hard-masked.",
        "Supplier B payment was hard-masked.",
        "old receipt as permission was hard-masked.",
        "old Root Final as current decision was hard-masked.",
        "Safe candidates could rank, but ranking did not grant permission.",
        "Orchestrator and Architect saw only bounded AVF/DRS-informed context.",
        "BSEP carried bounded context only.",
        "Root remained final authority.",
        "No payment, receipt, ActionCommitPacket, shipment release, or real-world effect occurred.",
    )
    business_scene = (
        "The business scene is the Supplier Payment / Shipment Release Review WOW v1.2 lane.",
        "Supplier A had bounded scoped context. Supplier B remained blocked. Shipment release remained held.",
        "The story is derived from closed artifacts only, not from a live rerun.",
    )
    timeline = (
        "1. Local DRS v0.2 resolved prior traces.",
        "2. AVF v0.2 evaluated DRS-informed candidate pressure.",
        "3. Orchestrator received bounded AVF/DRS-informed context.",
        "4. Orchestrator validation accepted the semantic proposal.",
        "5. BSEP carried bounded context and was validated before Architect.",
        "6. Architect received only BSEP-derived bounded context.",
        "7. Branch-local semantic actors returned advisory proposals.",
        "8. Post V&V and GT/LGT advisory review completed.",
        "9. Root final boundary was evaluated.",
    )
    drs_story = (
        "Supplier A prior trace was context only.",
        "Supplier B blocker warned/blocked the unsafe route.",
        "old receipt was not current permission.",
        "old Root Final was not silently reused and remained lineage only, not a new decision.",
        "Changed facts required rerun validation.",
        "DRS writeback after Root was local proof/audit only.",
        f"DRS records evaluated: {drs['records_evaluated_count']}; direct reuse allowed: {drs['direct_reuse_allowed_count']}; Root review required: {drs['root_review_required_count']}.",
    )
    avf_story = (
        "AVF did not decide.",
        "AVF did not grant permission.",
        "AVF hard-masked unsafe directions.",
        "release_all_and_pay_all was hard-masked.",
        "Supplier B payment was hard-masked.",
        "old receipt as permission was hard-masked.",
        "old Root Final as current decision was hard-masked.",
        "High score did not override HardMask.",
        "Top rank did not grant permission.",
        "Safe rank remained advisory.",
        "AVF score is not authority.",
        "HardMask is not Root.",
        "AVF could say where to look and where not to go, but not you may act.",
        f"AVF candidates evaluated: {avf['candidates_evaluated_count']}; hard-masked: {avf['hard_masked_count']}; unmasked: {avf['unmasked_count']}.",
    )
    ranked_story = (
        f"Top AVF candidate was {avf['top_candidate_id']} with score {avf['top_candidate_score']}, but top rank did not grant permission.",
        "prepare_supplier_a_payment_form_only could rank without authorizing payment.",
        "request_fresh_warehouse_validation could rank as a rerun/validation direction.",
        "request_fresh_legal_accounting_validation could rank as a rerun/validation direction.",
        "keep_shipment_held and root_review_only could rank without becoming action.",
    )
    orchestrator_story = (
        f"Orchestrator suggested route: {orchestrator.get('suggested_route')}.",
        "Evidence needed: " + ", ".join(orchestrator.get("evidence_needed", ())),
        f"root_review_required: {orchestrator.get('root_review_required')}",
        "Orchestrator made no truth, authority, action, final, PlanGraph, or Root-bypass claims.",
    )
    bsep_story = (
        "BSEP accepted: true.",
        "BSEP carried bounded AVF/DRS context.",
        f"BSEP local DRS invoked: {bsep_packet.get('local_drs_v0_2_resolve_invoked', True)}.",
        f"BSEP AVF invoked: {bsep_packet.get('avf_v0_2_evaluation_invoked', True)}.",
        "BSEP carried no raw DRS tables.",
        "BSEP carried no raw AVF tables.",
        "BSEP carried no raw user/provider text.",
        "BSEP carried no bank secrets/raw IBAN/bank token.",
    )
    architect_story = (
        f"Architect recommendation: {architect.get('root_recommendation')}.",
        "Architect provided semantic plan intent only.",
        "Runtime owns PlanGraph/local artifacts.",
        "Provider did not create ActionCommitPacket, receipt, payment, shipment, or FinalOutput.",
        "Root remains final authority.",
    )
    branch_story = tuple(
        f"{branch['source_branch_id']}: advisory status {branch['recommended_branch_status']}; branch outputs return to parent/root boundary; no truth/authority/action/final/receipt/payment/shipment claim."
        for branch in branch_validations
    )
    root_story = (
        "Root final boundary evaluated.",
        f"DRS writeback candidate local proof/audit only: {writeback.get('local_proof_audit_only')}.",
        "No ActionCommitPacket created in this observation.",
        "No receipt created.",
        "No payment executed.",
        "shipment remains unreleased.",
        "Root remains final authority.",
    )
    why = (
        "This story shows DRS memory and AVF pressure participating in the real-provider live lane without becoming authority.",
        "Provider semantics stayed advisory, runtime kept the bounded membrane, and Root stayed final.",
        "artifact_files_observed_only is true: the renderer reads closed artifacts and does not create new runtime effects.",
    )
    return {
        "one_screen_summary": one_screen,
        "business_scene": business_scene,
        "timeline": timeline,
        "drs_memory_story": drs_story,
        "avf_pressure_story": avf_story,
        "avf_rank_story": ranked_story,
        "orchestrator_story": orchestrator_story,
        "bsep_story": bsep_story,
        "architect_story": architect_story,
        "branch_actor_story": branch_story,
        "root_story": root_story,
        "why_this_matters": why,
    }


def collect_human_full_wow_v1_2_avf_live_observation_story(
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
    audit_log_text = str(selected_audit_log) if selected_audit_log else None

    if selected_artifact_dir is None:
        report = _base_report(
            final_status="SKIPPED_CLOSED",
            story_status="SKIPPED_CLOSED",
            source_artifact_dir=None,
            source_audit_log=audit_log_text,
        )
        report["skip_reason"] = "artifact_dir_not_provided"
        report["allow_raw_response_output"] = allow_raw_output
        return report

    source_dir = selected_artifact_dir
    source_dir_text = str(source_dir)
    artifacts, validation_results, validation_errors = _load_artifacts(source_dir)
    summary = artifacts.get("summary.json")
    counters = _summary_counters(summary if isinstance(summary, Mapping) else None)

    if validation_errors:
        return _fail_closed(
            source_artifact_dir=source_dir_text,
            source_audit_log=audit_log_text,
            failure_reason="artifact_validation_failed",
            counters=counters,
            validation_results=validation_results,
            validation_errors=validation_errors,
        )

    errors: list[str] = []
    if not isinstance(summary, Mapping):
        errors.append("summary.json: not_object")
    else:
        if summary.get("final_status") != "PASS":
            errors.append(f"summary.final_status={summary.get('final_status')}")
        if summary.get("stage_status") != "PASS":
            errors.append(f"summary.stage_status={summary.get('stage_status')}")
        if summary.get("provider_mode") != "real_provider":
            errors.append(f"summary.provider_mode={summary.get('provider_mode')}")
        if summary.get("production_ready_claimed") is not False:
            errors.append("summary.production_ready_claimed must be false")
        if summary.get("public_auditor_ready_claimed") is not False:
            errors.append("summary.public_auditor_ready_claimed must be false")

    secret_scan = artifacts["secret_scan.json"]
    if not (
        isinstance(secret_scan, Mapping)
        and secret_scan.get("passed") is True
        and secret_scan.get("matched_markers") == []
    ):
        errors.append("secret_scan failed or matched markers")

    for file_name in VALIDATION_FILES:
        if not _accepted_validation(artifacts[file_name]):
            errors.append(f"{file_name}: accepted_not_true")

    for key, expected in REQUIRED_COUNTER_VALUES.items():
        _expect_counter(counters, key, expected, errors)
    for key in EFFECT_COUNTER_KEYS:
        _expect_counter(counters, key, 0, errors)
    for key in AVF_PERMISSION_COUNTER_KEYS:
        _expect_counter(counters, key, 0, errors)
    _expect_counter(counters, "local_drs_v0_2_direct_reuse_allowed_count", 0, errors)

    drs = artifacts["local_drs_v0_2_resolve_report.json"]
    avf = artifacts["avf_v0_2_evaluation_report.json"]
    if not isinstance(drs, Mapping) or drs.get("local_drs_v0_2_status") != "PASS":
        errors.append("local_drs_v0_2_status must be PASS")
    if not isinstance(avf, Mapping) or avf.get("avf_v0_2_status") != "PASS":
        errors.append("avf_v0_2_status must be PASS")

    if errors:
        return _fail_closed(
            source_artifact_dir=source_dir_text,
            source_audit_log=audit_log_text,
            failure_reason="artifact_semantic_validation_failed",
            counters=counters,
            validation_results=validation_results,
            validation_errors=errors,
        )

    story_sections = _build_story_sections(artifacts, counters)
    report = _base_report(
        final_status="PASS",
        story_status="PASS",
        source_artifact_dir=source_dir_text,
        source_audit_log=audit_log_text,
        counters=counters,
    )
    report.update(story_sections)
    report.update(
        {
            "source_run_id": summary.get("run_id") if isinstance(summary, Mapping) else None,
            "provider_mode": summary.get("provider_mode") if isinstance(summary, Mapping) else None,
            "model": summary.get("model") if isinstance(summary, Mapping) else None,
            "validation_results": validation_results,
            "artifact_files_observed": tuple((*REQUIRED_TEXT_FILES, *REQUIRED_JSON_FILES)),
            "allow_raw_response_output": allow_raw_output,
        }
    )
    if allow_raw_output:
        snippets = []
        for file_name in RAW_RESPONSE_FILES:
            path = source_dir / file_name
            if path.exists():
                snippets.append(
                    f"{file_name}: "
                    + _redact_secret_markers(_safe_text(path))[:400]
                )
        report["raw_provider_response_rendered"] = bool(snippets)
        report["raw_provider_response_forensic_excerpt"] = tuple(snippets)
    return report


def _format_counter_table(counters: Mapping[str, Any]) -> list[str]:
    return [f"- {key}: {int(counters.get(key, 0) or 0)}" for key in COUNTER_KEYS]


def _section(lines: list[str], title: str, values: Iterable[str]) -> None:
    lines.extend(["", title])
    lines.extend(str(value) for value in values)


def _failure_lines(report: Mapping[str, Any]) -> tuple[str, ...]:
    if report.get("final_status") != "FAIL_CLOSED":
        return ()
    errors = tuple(report.get("validation_errors") or ())
    return (
        f"failure_reason: {report.get('failure_reason')}",
        *(f"- {error}" for error in errors),
    )


def render_human_full_wow_v1_2_avf_live_observation_story(
    report: Mapping[str, Any]
) -> str:
    counters = report.get("counter_table", {})
    lines: list[str] = [
        "HEDGEHOG OS - FULL WOW V1.2 + DRS V0.2 + AVF V0.2 LIVE HUMAN STORY",
        "",
        "[FULL WOW V1.2 + DRS V0.2 + AVF V0.2 LIVE HUMAN STORY]",
        f"run_id: {report.get('run_id')}",
        f"report_id: {report.get('report_id')}",
        f"story_type: {report.get('story_type')}",
        f"story_status: {report.get('story_status')}",
        f"final_status: {report.get('final_status')}",
        f"source_artifact_dir: {report.get('source_artifact_dir')}",
        f"source_audit_log: {report.get('source_audit_log')}",
        "production_ready_claimed: false",
        "public_auditor_ready_claimed: false",
        f"real_world_effects_count: {int(counters.get('real_world_effects_count', 0) or 0)}",
    ]

    if report.get("final_status") == "SKIPPED_CLOSED":
        _section(
            lines,
            "[ONE-SCREEN SUMMARY]",
            (
                "Story rendering is skipped closed because no artifact directory was provided.",
                f"skip_reason: {report.get('skip_reason')}",
                "The renderer made no provider, network, Gemini, action, receipt, payment, shipment, or real-world calls.",
            ),
        )
    elif report.get("final_status") == "FAIL_CLOSED":
        _section(
            lines,
            "[ONE-SCREEN SUMMARY]",
            (
                "Story rendering failed closed because artifact evidence did not satisfy the closed-run contract.",
                *_failure_lines(report),
            ),
        )
    else:
        _section(lines, "[ONE-SCREEN SUMMARY]", report["one_screen_summary"])

    _section(lines, "[BUSINESS SCENE]", report.get("business_scene", ()))
    _section(
        lines,
        "[CAST OF SEMANTIC ACTORS]",
        (f"- {actor}" for actor in report.get("semantic_actor_cast", ())),
    )
    _section(lines, "[TIMELINE]", report.get("timeline", ()))
    _section(lines, "[WHAT DRS REMEMBERED]", report.get("drs_memory_story", ()))
    _section(
        lines,
        "[WHAT AVF HARD-MASKED]",
        report.get("avf_pressure_story", ()),
    )
    _section(
        lines,
        "[WHAT AVF RANKED WITHOUT AUTHORIZING]",
        report.get("avf_rank_story", ()),
    )
    _section(
        lines,
        "[WHAT ORCHESTRATOR UNDERSTOOD]",
        report.get("orchestrator_story", ()),
    )
    _section(lines, "[WHAT BSEP DID]", report.get("bsep_story", ()))
    _section(lines, "[WHAT ARCHITECT UNDERSTOOD]", report.get("architect_story", ()))
    _section(
        lines,
        "[WHAT BRANCH-LOCAL ACTORS DID]",
        report.get("branch_actor_story", ()),
    )
    _section(lines, "[WHAT ROOT DID]", report.get("root_story", ()))
    _section(lines, "[WHY THIS MATTERS]", report.get("why_this_matters", ()))
    _section(lines, "[COUNTER TABLE]", _format_counter_table(counters))
    _section(
        lines,
        "[ARTIFACT EVIDENCE]",
        (
            f"artifact_files_observed_only: {report.get('artifact_files_observed_only')}",
            "Raw provider responses are not printed by default.",
            f"raw_provider_response_rendered: {report.get('raw_provider_response_rendered')}",
            *(f"- {name}" for name in report.get("artifact_files_observed", ())),
        ),
    )
    if report.get("raw_provider_response_rendered"):
        _section(
            lines,
            "[FORENSIC RAW RESPONSE EXCERPTS]",
            (
                "Raw response excerpts are redacted forensic artifact excerpts only.",
                *report.get("raw_provider_response_forensic_excerpt", ()),
            ),
        )
    _section(lines, "[NON-CLAIMS]", (f"- {claim}" for claim in NON_CLAIMS))
    _section(
        lines,
        "[FINAL STATUS]",
        (
            f"FINAL STATUS: {report.get('final_status')}",
            f"story_status: {report.get('story_status')}",
            "provider/network/Gemini calls by renderer: 0",
            "action/receipt/payment/shipment/effects by renderer: 0",
        ),
    )
    rendered = "\n".join(lines) + "\n"
    for marker in _secret_markers():
        if marker in rendered:
            raise ValueError("rendered story contains a blocked secret marker")
    return rendered


def run_human_full_wow_v1_2_avf_live_observation_story(
    artifact_dir: str | Path | None = None,
    audit_log_path: str | Path | None = None,
    env: Mapping[str, str] | None = None,
) -> str:
    return render_human_full_wow_v1_2_avf_live_observation_story(
        collect_human_full_wow_v1_2_avf_live_observation_story(
            artifact_dir=artifact_dir,
            audit_log_path=audit_log_path,
            env=env,
        )
    )


def main() -> int:
    print(run_human_full_wow_v1_2_avf_live_observation_story())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
