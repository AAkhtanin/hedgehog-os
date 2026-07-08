from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Mapping


RUN_ID = "human_full_wow_v1_2_live_action_corridor_integrated_story_v01"
REPORT_ID = "human_full_wow_v1_2_live_action_corridor_integrated_story_v01"
STORY_TYPE = "artifact_backed_full_wow_v1_2_live_action_corridor_integrated_story"

ARTIFACT_DIR_ENV = "HEDGEHOG_FULL_WOW_V1_2_LIVE_ACTION_CORRIDOR_STORY_ARTIFACT_DIR"
AUDIT_LOG_ENV = "HEDGEHOG_FULL_WOW_V1_2_LIVE_ACTION_CORRIDOR_STORY_AUDIT_LOG"
ALLOW_RAW_RESPONSE_OUTPUT_ENV = (
    "HEDGEHOG_FULL_WOW_V1_2_LIVE_ACTION_CORRIDOR_STORY_ALLOW_RAW_RESPONSE_OUTPUT"
)

DEFAULT_AUDIT_LOG = (
    "docs/audit_reports/"
    "auditor_full_wow_v1_2_live_action_corridor_integrated_organism_real_run_v01.log"
)

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
    "bsep_validation.json",
    "top_level_orchestrator_validation.json",
    "top_level_architect_validation.json",
    "branch_legal_validation.json",
    "branch_accounting_validation.json",
    "branch_supplier_b_validation.json",
    "branch_bank_policy_validation.json",
    "action_commit_packet_v0_2_integration.json",
    "action_commit_packet_v0_2_packet_validation.json",
    "action_commit_packet_v0_2_registry_validation.json",
    "action_commit_packet_v0_2_corridor_entry_validation.json",
    "mock_bank_sandbox_v0_2_corridor_execution.json",
    "mock_bank_sandbox_v0_2_corridor_sequence.json",
    "mock_bank_sandbox_v0_2_mock_payment_intent.json",
    "mock_bank_sandbox_v0_2_mock_payment_consent.json",
    "mock_bank_sandbox_v0_2_mock_payment_order.json",
    "mock_bank_sandbox_v0_2_mock_receipt_evidence.json",
    "mock_bank_sandbox_v0_2_receipt_validation.json",
)

REQUIRED_SECTIONS = (
    "[HEDGEHOG OS — FULL WOW V1.2 LIVE ACTION CORRIDOR INTEGRATED STORY]",
    "[ONE-SCREEN SUMMARY]",
    "[BUSINESS SCENE]",
    "[CAST OF REAL SEMANTIC ACTORS]",
    "[TIMELINE FROM REQUEST TO RECEIPT EVIDENCE]",
    "[WHAT DRS REMEMBERED]",
    "[WHAT AVF HARD-MASKED AND RANKED]",
    "[WHAT ORCHESTRATOR UNDERSTOOD]",
    "[WHAT BSEP CARRIED]",
    "[WHAT ARCHITECT UNDERSTOOD]",
    "[WHAT BRANCH ACTORS RETURNED]",
    "[WHAT ROOT DID]",
    "[ACTIONCOMMITPACKET BOUNDARY]",
    "[MOCKBANKSANDBOX CONTRACT FULFILLMENT CORRIDOR]",
    "[MOCK RECEIPT BOUNDARY]",
    "[SUPPLIER B AND SHIPMENT SAFETY]",
    "[BANK A VS BANK B POSITIONING]",
    "[WHY THIS IS READY FOR FUTURE CRYPTOGRAPHY]",
    "[ARTIFACT EVIDENCE MAP]",
    "[COUNTER TABLE]",
    "[NON-CLAIMS]",
    "[FINAL STATUS]",
)

COUNTER_KEYS = (
    "semantic_actor_call_count",
    "real_provider_call_count",
    "gemini_called_count",
    "network_used_count",
    "local_drs_v0_2_records_evaluated_count",
    "local_drs_v0_2_direct_reuse_allowed_count",
    "local_drs_v0_2_root_review_required_count",
    "avf_v0_2_candidates_evaluated_count",
    "avf_v0_2_action_permission_granted_count",
    "avf_v0_2_final_output_created_count",
    "avf_v0_2_root_bypass_count",
    "action_commit_packet_v0_2_root_created_model_packet_count",
    "action_commit_packet_v0_2_created_by_root_count",
    "action_commit_packet_v0_2_created_by_human_count",
    "action_commit_packet_v0_2_created_by_llm_count",
    "action_commit_packet_v0_2_created_by_drs_count",
    "action_commit_packet_v0_2_created_by_avf_count",
    "action_commit_packet_v0_2_created_by_gt_lgt_count",
    "mock_bank_sandbox_v0_2_corridor_invoked_count",
    "mock_bank_sandbox_v0_2_mock_payment_intent_created_count",
    "mock_bank_sandbox_v0_2_mock_payment_consent_created_count",
    "mock_bank_sandbox_v0_2_mock_payment_order_created_count",
    "mock_bank_sandbox_v0_2_mock_receipt_evidence_created_count",
    "mock_bank_sandbox_v0_2_terminal_receipt_observed_count",
    "mock_bank_sandbox_v0_2_receipt_permission_created_count",
    "mock_bank_sandbox_v0_2_receipt_future_permission_created_count",
    "mock_bank_sandbox_v0_2_receipt_final_output_created_count",
    "mock_bank_sandbox_v0_2_receipt_supplier_b_authorization_count",
    "mock_bank_sandbox_v0_2_receipt_shipment_release_count",
    "mock_bank_sandbox_v0_2_receipt_scope_mutation_count",
    "mock_bank_sandbox_v0_2_receipt_production_drs_write_count",
    "mock_bank_sandbox_v0_2_real_bank_api_called_count",
    "mock_bank_sandbox_v0_2_real_supplier_api_called_count",
    "mock_bank_sandbox_v0_2_real_warehouse_api_called_count",
    "mock_bank_sandbox_v0_2_real_payment_executed_count",
    "mock_bank_sandbox_v0_2_shipment_released_count",
    "mock_bank_sandbox_v0_2_real_world_effects_count",
    "real_payment_executed_count",
    "shipment_released_count",
    "real_world_effects_count",
)

SEMANTIC_ROLE_FILES = {
    "top_level_orchestrator_llm": "top_level_orchestrator_validation.json",
    "top_level_semantic_architect_llm": "top_level_architect_validation.json",
    "legal_clause_semantic_extractor": "branch_legal_validation.json",
    "accounting_mismatch_semantic_explainer": "branch_accounting_validation.json",
    "supplier_b_unstructured_note_interpreter": "branch_supplier_b_validation.json",
    "bank_policy_semantic_reviewer": "branch_bank_policy_validation.json",
}


def _read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _counter(counters: Mapping[str, Any], key: str) -> int:
    return int(counters.get(key, 0) or 0)


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _load_artifacts(artifact_dir: Path) -> tuple[dict[str, Any], tuple[str, ...]]:
    loaded: dict[str, Any] = {}
    errors: list[str] = []
    for file_name in REQUIRED_JSON_FILES:
        path = artifact_dir / file_name
        if not path.exists():
            errors.append(f"missing:{file_name}")
            continue
        try:
            loaded[file_name] = _read_json(path)
        except (OSError, json.JSONDecodeError):
            errors.append(f"invalid_json:{file_name}")
    return loaded, tuple(errors)


def _counter_table(summary: Mapping[str, Any]) -> dict[str, int]:
    counters = _as_mapping(summary.get("counters"))
    return {key: _counter(counters, key) for key in COUNTER_KEYS}


def _validation_errors(
    artifacts: Mapping[str, Any],
    artifact_errors: tuple[str, ...],
) -> tuple[str, ...]:
    errors = list(artifact_errors)
    summary = _as_mapping(artifacts.get("summary.json"))
    counters = _as_mapping(summary.get("counters"))
    table = _counter_table(summary)
    secret_scan = _as_mapping(artifacts.get("secret_scan.json"))

    checks = {
        "summary_final_status_pass": summary.get("final_status") == "PASS",
        "stage_status_pass": summary.get("stage_status") == "PASS",
        "provider_mode_real_provider": summary.get("provider_mode") == "real_provider",
        "semantic_actor_call_count_six": table["semantic_actor_call_count"] == 6,
        "real_provider_call_count_six": table["real_provider_call_count"] == 6,
        "drs_direct_reuse_allowed_zero": table[
            "local_drs_v0_2_direct_reuse_allowed_count"
        ]
        == 0,
        "avf_permission_action_final_root_bypass_zero": (
            table["avf_v0_2_action_permission_granted_count"] == 0
            and table["avf_v0_2_final_output_created_count"] == 0
            and table["avf_v0_2_root_bypass_count"] == 0
        ),
        "root_created_packet_count_one": table[
            "action_commit_packet_v0_2_root_created_model_packet_count"
        ]
        == 1,
        "non_root_packet_creator_counts_zero": (
            table["action_commit_packet_v0_2_created_by_human_count"] == 0
            and table["action_commit_packet_v0_2_created_by_llm_count"] == 0
            and table["action_commit_packet_v0_2_created_by_drs_count"] == 0
            and table["action_commit_packet_v0_2_created_by_avf_count"] == 0
            and table["action_commit_packet_v0_2_created_by_gt_lgt_count"] == 0
        ),
        "mock_receipt_evidence_created_once": table[
            "mock_bank_sandbox_v0_2_mock_receipt_evidence_created_count"
        ]
        == 1,
        "receipt_boundary_counters_zero": (
            table["mock_bank_sandbox_v0_2_receipt_permission_created_count"] == 0
            and table[
                "mock_bank_sandbox_v0_2_receipt_future_permission_created_count"
            ]
            == 0
            and table["mock_bank_sandbox_v0_2_receipt_final_output_created_count"]
            == 0
            and table[
                "mock_bank_sandbox_v0_2_receipt_supplier_b_authorization_count"
            ]
            == 0
            and table["mock_bank_sandbox_v0_2_receipt_shipment_release_count"] == 0
            and table["mock_bank_sandbox_v0_2_receipt_scope_mutation_count"] == 0
            and table["mock_bank_sandbox_v0_2_receipt_production_drs_write_count"]
            == 0
        ),
        "real_api_counters_zero": (
            table["mock_bank_sandbox_v0_2_real_bank_api_called_count"] == 0
            and table["mock_bank_sandbox_v0_2_real_supplier_api_called_count"] == 0
            and table["mock_bank_sandbox_v0_2_real_warehouse_api_called_count"] == 0
        ),
        "real_payment_zero": table["real_payment_executed_count"] == 0,
        "shipment_release_zero": table["shipment_released_count"] == 0,
        "real_world_effects_zero": (
            table["real_world_effects_count"] == 0
            and table["mock_bank_sandbox_v0_2_real_world_effects_count"] == 0
        ),
        "secret_scan_passed": (
            secret_scan.get("passed") is True
            and secret_scan.get("matched_markers", []) == []
        ),
    }
    for key, passed in checks.items():
        if passed is not True:
            errors.append(key)
    if _counter(counters, "mock_bank_sandbox_v0_2_provider_called_count") != 0:
        errors.append("mock_corridor_provider_called")
    if _counter(counters, "mock_bank_sandbox_v0_2_network_called_count") != 0:
        errors.append("mock_corridor_network_called")
    if _counter(counters, "mock_bank_sandbox_v0_2_gemini_called_count") != 0:
        errors.append("mock_corridor_gemini_called")
    return tuple(errors)


def _role_meaning(role: str, validation: Mapping[str, Any]) -> str:
    canonical = _as_mapping(validation.get("canonical"))
    if role == "top_level_orchestrator_llm":
        return str(canonical.get("suggested_route", "bounded business route"))
    if role == "top_level_semantic_architect_llm":
        return str(canonical.get("result_proposal_summary", "semantic intent"))
    if "semantic_summary" in canonical:
        return str(canonical["semantic_summary"])
    return str(canonical.get("evidence_interpretation", "advisory semantic evidence"))


def _semantic_actor_story(
    summary: Mapping[str, Any],
    artifacts: Mapping[str, Any],
) -> tuple[dict[str, Any], ...]:
    actors = summary.get("semantic_actor_calls", ())
    rows: list[dict[str, Any]] = []
    for actor in actors if isinstance(actors, list) else ():
        if not isinstance(actor, Mapping):
            continue
        role = str(actor.get("role", "unknown_role"))
        validation = _as_mapping(artifacts.get(SEMANTIC_ROLE_FILES.get(role, "")))
        rows.append(
            {
                "role": role,
                "validation_status": actor.get("validation_status", "UNKNOWN"),
                "provider_mode": actor.get("provider_mode", "unknown"),
                "semantic_meaning": _role_meaning(role, validation),
                "non_authority_boundary": (
                    "This actor returns advisory semantic evidence only."
                ),
            }
        )
    return tuple(rows)


def _artifact_evidence_map() -> dict[str, tuple[str, ...]]:
    return {
        "one_screen_summary": ("summary.json", "secret_scan.json"),
        "drs_story": ("local_drs_v0_2_resolve_report.json",),
        "avf_story": ("avf_v0_2_evaluation_report.json",),
        "orchestrator_story": ("top_level_orchestrator_validation.json",),
        "bsep_story": ("bsep_packet.json", "bsep_validation.json"),
        "architect_story": ("top_level_architect_validation.json",),
        "branch_actor_story": (
            "branch_legal_validation.json",
            "branch_accounting_validation.json",
            "branch_supplier_b_validation.json",
            "branch_bank_policy_validation.json",
        ),
        "action_commit_packet_story": ("action_commit_packet_v0_2_integration.json",),
        "mock_bank_corridor_story": (
            "mock_bank_sandbox_v0_2_corridor_execution.json",
            "mock_bank_sandbox_v0_2_mock_payment_order.json",
        ),
        "receipt_boundary_story": (
            "mock_bank_sandbox_v0_2_mock_receipt_evidence.json",
            "mock_bank_sandbox_v0_2_receipt_validation.json",
        ),
    }


def _non_claims() -> tuple[str, ...]:
    return (
        "This is not production.",
        "This is not public auditor final package.",
        "This is not real payment.",
        "This is not real shipment release.",
        "This is not real bank connector integration.",
        "This is not Bank B Hedgehog-native bank-to-bank corridor.",
        "This is not cryptographic sealing.",
    )


def _timeline() -> tuple[str, ...]:
    return (
        "1. Dirty business request.",
        "2. DRS live observation.",
        "3. AVF live observation.",
        "4. Real Orchestrator call.",
        "5. BSEP creation/validation.",
        "6. Real Architect call.",
        "7. Runtime PlanGraph/fractal cells.",
        "8. Branch actor calls.",
        "9. Branch ResultProposals.",
        "10. Post V&V.",
        "11. GT/LGT.",
        "12. Root boundary.",
        "13. ActionCommitPacket v0.2.",
        "14. MockBankSandbox corridor.",
        "15. Mock payment intent/consent/order.",
        "16. Mock receipt evidence.",
        "17. Supplier B blocked.",
        "18. Shipment held.",
        "19. Final PASS.",
    )


def collect_human_full_wow_v1_2_live_action_corridor_integrated_story(
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    effective_env = dict(os.environ if env is None else env)
    artifact_dir_raw = effective_env.get(ARTIFACT_DIR_ENV, "").strip()
    audit_log = effective_env.get(AUDIT_LOG_ENV, DEFAULT_AUDIT_LOG).strip()

    if not artifact_dir_raw:
        return {
            "run_id": RUN_ID,
            "report_id": REPORT_ID,
            "story_type": STORY_TYPE,
            "story_status": "SKIPPED_CLOSED",
            "final_status": "SKIPPED_CLOSED",
            "source_artifact_dir": "",
            "source_audit_log": audit_log,
            "one_screen_summary": (),
            "business_scene": (),
            "semantic_actor_story": (),
            "timeline": (),
            "drs_story": (),
            "avf_story": (),
            "orchestrator_story": (),
            "bsep_story": (),
            "architect_story": (),
            "branch_actor_story": (),
            "root_story": (),
            "action_commit_packet_story": (),
            "mock_bank_corridor_story": (),
            "receipt_boundary_story": (),
            "supplier_b_and_shipment_story": (),
            "bank_a_bank_b_story": (),
            "crypto_readiness_story": (),
            "artifact_evidence_map": {},
            "counter_table": {},
            "non_claims": _non_claims(),
            "validation_errors": ("artifact_dir_missing",),
        }

    artifact_dir = Path(artifact_dir_raw)
    if not artifact_dir.exists():
        report = collect_human_full_wow_v1_2_live_action_corridor_integrated_story(
            env={AUDIT_LOG_ENV: audit_log}
        )
        report["source_artifact_dir"] = artifact_dir_raw
        report["validation_errors"] = ("artifact_dir_not_found",)
        return report

    artifacts, artifact_errors = _load_artifacts(artifact_dir)
    summary = _as_mapping(artifacts.get("summary.json"))
    counters = _as_mapping(summary.get("counters"))
    table = _counter_table(summary)
    action = _as_mapping(summary.get("action_commit_packet_v0_2_integration"))
    mock = _as_mapping(summary.get("mock_bank_sandbox_v0_2_corridor_execution"))
    drs = _as_mapping(artifacts.get("local_drs_v0_2_resolve_report.json"))
    avf = _as_mapping(artifacts.get("avf_v0_2_evaluation_report.json"))
    orchestrator = _as_mapping(artifacts.get("top_level_orchestrator_validation.json"))
    architect = _as_mapping(artifacts.get("top_level_architect_validation.json"))

    validation_errors = _validation_errors(artifacts, artifact_errors)
    final_status = "PASS" if not validation_errors else "FAIL_CLOSED"

    one_screen = (
        "Six real Gemini semantic actors participated.",
        "DRS remembered prior traces but did not decide.",
        "AVF hard-masked unsafe routes and ranked safe directions but did not authorize.",
        "Orchestrator understood the bounded business route.",
        "BSEP carried bounded context only.",
        "Architect proposed semantic intent only.",
        "Branch actors returned advisory ResultProposals only.",
        "Root remained final authority.",
        "Root created one scoped Supplier A ActionCommitPacket model.",
        "MockBankSandbox consumed only that scoped Supplier A packet.",
        "The corridor created mock payment intent, mock consent, mock order, and mock receipt evidence.",
        "Receipt is evidence only.",
        "Supplier B remained blocked.",
        "Shipment remained held.",
        "Real bank, real payment, real shipment release, and real-world effects remained zero.",
    )

    business_scene = (
        "Shipment SH-2042 is the reviewed shipment.",
        "Supplier A / Adriatic Filters is the scoped mock-payment supplier.",
        "Supplier B / Balkan Pumps remains blocked.",
        "Bank A is the legacy/API-like deterministic corridor.",
        "Bank B remains Hedgehog-native preview/future path.",
        "Supplier A mock payment proceeds inside scoped corridor only.",
        "Shipment remains held.",
    )

    drs_story = (
        f"DRS record count: {drs.get('records_evaluated_count', table['local_drs_v0_2_records_evaluated_count'])}.",
        "direct_reuse_allowed_count == 0.",
        f"root_review_required_count == {drs.get('root_review_required_count', table['local_drs_v0_2_root_review_required_count'])}.",
        "Old receipt is not current permission.",
        "Old Root Final is not silently reused.",
        "DRS is not truth/authority/permission/FinalOutput.",
    )

    avf_story = (
        "release_all_and_pay_all hard-masked.",
        "Supplier B payment hard-masked.",
        "Unsafe routes blocked.",
        "Safe candidates may rank but do not grant permission.",
        f"Top ranked candidate: {avf.get('top_candidate_id', 'block_supplier_b_and_hold_shipment')}.",
        "Top rank is not permission.",
        "AVF score is not authority.",
        "HardMask is not Root.",
    )

    orchestrator_canonical = _as_mapping(orchestrator.get("canonical"))
    architect_canonical = _as_mapping(architect.get("canonical"))
    orchestrator_story = (
        f"Suggested route: {orchestrator_canonical.get('suggested_route', 'supplier_payment_shipment_review_v1_2')}.",
        "Evidence needed: "
        + ", ".join(orchestrator_canonical.get("evidence_needed", ())),
        "Required guards: "
        + ", ".join(orchestrator_canonical.get("required_guards", ())),
        "No authority/action/final/connector claims.",
    )

    bsep_story = (
        "BSEP created and validated.",
        "BSEP carried bounded context only.",
        "BSEP carried no raw secrets.",
        "BSEP carried no raw action packet/receipt/order/registry tables.",
        "BSEP is not truth or authority.",
    )

    architect_story = (
        str(
            architect_canonical.get(
                "result_proposal_summary",
                "Supplier A may proceed only to scoped review.",
            )
        ),
        "Runtime owns PlanGraph/local artifacts.",
        "Architect output is not action permission, not FinalOutput, not ActionCommitPacket.",
    )

    branch_actor_story = (
        "Legal branch is advisory only and returns to parent/root review.",
        "Accounting branch is advisory only and returns to parent/root review.",
        "Supplier B branch is advisory only and returns to parent/root review.",
        "Bank policy branch is advisory only and returns to parent/root review.",
        "No branch creates ActionCommitPacket, receipt, payment, shipment release, or authority.",
    )

    root_story = (
        "Root boundary evaluated.",
        "Root remains final authority.",
        "Human approval is scoped evidence only.",
        "Root-created packet is scoped to Supplier A only.",
    )

    action_story = (
        "Root created one scoped Supplier A ActionCommitPacket model.",
        "Human approval did not create the packet.",
        "LLM/DRS/AVF/GT-LGT did not create packet.",
        f"Supplier A allowed: {tuple(action.get('allowed_subjects', ()))!r}.",
        "Supplier B forbidden.",
        "Shipment release forbidden.",
        "Real bank/supplier/warehouse APIs forbidden.",
        "Packet accepted for deterministic mock corridor only.",
    )

    mock_story = (
        "MockBankSandbox consumed validated Root-created Supplier A packet.",
        "It checked scope, amount, creditor, payment slot, adapter binding, idempotency, expiry/TTL, and forbidden surfaces.",
        "It created mock payment intent.",
        "It created mock payment consent.",
        "It created mock payment order.",
        "It created mock receipt evidence.",
        "Terminal receipt observation recorded only in local proof-only registry.",
        "Corridor is deterministic contract/commit plane, not reasoning.",
    )

    receipt_story = (
        "Receipt is evidence only.",
        "Receipt did not create permission.",
        "Receipt did not create future permission.",
        "Receipt did not create FinalOutput.",
        "Receipt did not authorize Supplier B.",
        "Receipt did not release shipment.",
        "Receipt did not mutate packet scope.",
        "Receipt did not write production DRS.",
        "Receipt did not cause real-world effects.",
    )

    supplier_story = (
        "Supplier B remained blocked.",
        "Shipment remained held.",
        "Supplier A mock receipt does not leak permission to Supplier B.",
        "Supplier A mock receipt does not release SH-2042.",
    )

    bank_story = (
        "Bank A in this checkpoint is legacy/API-like deterministic mock corridor.",
        "Bank B remains Hedgehog-native preview/future path.",
        "Bank B does not execute in this checkpoint.",
        "Future Bank B can become Hedgehog-to-Hedgehog contract exchange with its own Root boundary.",
        "Not implemented now.",
    )

    crypto_story = (
        "Current run is not cryptographically sealed.",
        "Current run is future crypto-ready only in the limited artifact-set sense: stable artifact names, summary, counters, validations, source commit, and auditable references exist.",
        "A future layer can add artifact_manifest.json, canonical hashes, hash-chain, signatures, or Merkle-style proof.",
        "No cryptographic proof layer is claimed here.",
    )

    return {
        "run_id": RUN_ID,
        "report_id": REPORT_ID,
        "story_type": STORY_TYPE,
        "story_status": final_status,
        "final_status": final_status,
        "source_artifact_dir": artifact_dir_raw,
        "source_audit_log": audit_log,
        "one_screen_summary": one_screen,
        "business_scene": business_scene,
        "semantic_actor_story": _semantic_actor_story(summary, artifacts),
        "timeline": _timeline(),
        "drs_story": drs_story,
        "avf_story": avf_story,
        "orchestrator_story": orchestrator_story,
        "bsep_story": bsep_story,
        "architect_story": architect_story,
        "branch_actor_story": branch_actor_story,
        "root_story": root_story,
        "action_commit_packet_story": action_story,
        "mock_bank_corridor_story": mock_story,
        "receipt_boundary_story": receipt_story,
        "supplier_b_and_shipment_story": supplier_story,
        "bank_a_bank_b_story": bank_story,
        "crypto_readiness_story": crypto_story,
        "artifact_evidence_map": _artifact_evidence_map(),
        "counter_table": table,
        "non_claims": _non_claims(),
        "validation_errors": validation_errors,
        "raw_response_output_allowed": effective_env.get(
            ALLOW_RAW_RESPONSE_OUTPUT_ENV, ""
        )
        == "1",
        "source_model": summary.get("model"),
        "source_provider_mode": summary.get("provider_mode"),
        "source_mock_status": mock.get("status") or mock.get("mock_bank_sandbox_v0_2_status"),
        "source_counters_seen": len(counters),
    }


def _render_lines(title: str, lines: Any) -> list[str]:
    output = [title]
    if isinstance(lines, Mapping):
        for key, value in lines.items():
            output.append(f"{key}: {value}")
    else:
        for line in lines:
            output.append(str(line))
    output.append("")
    return output


def render_human_full_wow_v1_2_live_action_corridor_integrated_story(
    report: Mapping[str, Any],
) -> str:
    lines: list[str] = []
    lines.extend(_render_lines(REQUIRED_SECTIONS[0], (f"final_status: {report.get('final_status')}",)))
    section_map = (
        ("[ONE-SCREEN SUMMARY]", report.get("one_screen_summary", ())),
        ("[BUSINESS SCENE]", report.get("business_scene", ())),
        (
            "[CAST OF REAL SEMANTIC ACTORS]",
            tuple(
                f"{actor.get('role')}: validation_status={actor.get('validation_status')}; "
                f"provider_mode={actor.get('provider_mode')}; "
                f"meaning={actor.get('semantic_meaning')}; "
                f"{actor.get('non_authority_boundary')}"
                for actor in report.get("semantic_actor_story", ())
                if isinstance(actor, Mapping)
            ),
        ),
        ("[TIMELINE FROM REQUEST TO RECEIPT EVIDENCE]", report.get("timeline", ())),
        ("[WHAT DRS REMEMBERED]", report.get("drs_story", ())),
        ("[WHAT AVF HARD-MASKED AND RANKED]", report.get("avf_story", ())),
        ("[WHAT ORCHESTRATOR UNDERSTOOD]", report.get("orchestrator_story", ())),
        ("[WHAT BSEP CARRIED]", report.get("bsep_story", ())),
        ("[WHAT ARCHITECT UNDERSTOOD]", report.get("architect_story", ())),
        ("[WHAT BRANCH ACTORS RETURNED]", report.get("branch_actor_story", ())),
        ("[WHAT ROOT DID]", report.get("root_story", ())),
        ("[ACTIONCOMMITPACKET BOUNDARY]", report.get("action_commit_packet_story", ())),
        (
            "[MOCKBANKSANDBOX CONTRACT FULFILLMENT CORRIDOR]",
            report.get("mock_bank_corridor_story", ()),
        ),
        ("[MOCK RECEIPT BOUNDARY]", report.get("receipt_boundary_story", ())),
        (
            "[SUPPLIER B AND SHIPMENT SAFETY]",
            report.get("supplier_b_and_shipment_story", ()),
        ),
        ("[BANK A VS BANK B POSITIONING]", report.get("bank_a_bank_b_story", ())),
        (
            "[WHY THIS IS READY FOR FUTURE CRYPTOGRAPHY]",
            report.get("crypto_readiness_story", ()),
        ),
        ("[ARTIFACT EVIDENCE MAP]", report.get("artifact_evidence_map", {})),
        ("[COUNTER TABLE]", report.get("counter_table", {})),
        ("[NON-CLAIMS]", report.get("non_claims", ())),
        (
            "[FINAL STATUS]",
            (
                f"story_status: {report.get('story_status')}",
                f"final_status: {report.get('final_status')}",
                f"validation_errors: {tuple(report.get('validation_errors', ()))!r}",
                "Root remained final authority.",
            ),
        ),
    )
    for title, value in section_map:
        lines.extend(_render_lines(title, value))
    return "\n".join(lines).rstrip() + "\n"


def main() -> None:
    report = collect_human_full_wow_v1_2_live_action_corridor_integrated_story()
    print(render_human_full_wow_v1_2_live_action_corridor_integrated_story(report))


if __name__ == "__main__":
    main()
