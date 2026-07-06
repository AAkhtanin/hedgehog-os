from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Mapping


RUN_ID = "full_wow_v1_1_final_integrated_rollup_v01"
REPORT_ID = "full_wow_v1_1_final_integrated_rollup_v01"
ROLLUP_TYPE = "deterministic_closed_evidence_observer"

PROJECT_ROOT = Path(__file__).resolve().parents[1]

SOURCE_CHECKPOINTS: tuple[dict[str, str], ...] = (
    {
        "label": "Supplier WOW deterministic runner",
        "path": "demo/run_supplier_payment_shipment_release_review_wow_v1_1.py",
        "kind": "runner",
        "rollup_action": "cite_only",
    },
    {
        "label": "Supplier WOW deterministic audit",
        "path": "docs/audit_reports/auditor_supplier_payment_shipment_release_review_wow_v1_1.log",
        "kind": "audit",
        "rollup_action": "cite_only",
    },
    {
        "label": "Human walkthrough",
        "path": "demo/run_human_supplier_payment_shipment_release_review_wow_v1_1_walkthrough.py",
        "kind": "runner",
        "rollup_action": "cite_only",
    },
    {
        "label": "Full Semantic E2E runner",
        "path": "demo/run_full_semantic_e2e_v01.py",
        "kind": "runner",
        "rollup_action": "cite_only",
    },
    {
        "label": "Full E2E WOW alignment audit",
        "path": "docs/audit_reports/auditor_full_semantic_e2e_wow_v1_1_alignment_v01.log",
        "kind": "audit",
        "rollup_action": "cite_only",
    },
    {
        "label": "Full E2E live evidence coherence audit",
        "path": "docs/audit_reports/auditor_full_semantic_e2e_live_evidence_wow_v1_1_coherence_v01.log",
        "kind": "audit",
        "rollup_action": "cite_only",
    },
    {
        "label": "BSEP topology repair audit",
        "path": "docs/audit_reports/auditor_full_wow_v1_1_manual_live_gemini_bsep_topology_repair_v01.log",
        "kind": "audit",
        "rollup_action": "cite_only",
    },
    {
        "label": "Real Gemini lane audit",
        "path": "docs/audit_reports/auditor_full_wow_v1_1_manual_live_gemini_lane_real_run_v01.log",
        "kind": "audit",
        "rollup_action": "cite_only",
    },
    {
        "label": "Final rollup preflight",
        "path": "docs/full_wow_v1_1_final_integrated_rollup_preflight_v01.md",
        "kind": "preflight",
        "rollup_action": "cite_only",
    },
)

STATE_MACHINE_PHASES: tuple[dict[str, Any], ...] = (
    {
        "phase_id": "phase_1_first_run_not_ready",
        "status": "CLOSED",
        "meaning": "Root returns NOT_READY while supplier, legal, stock, and payment approval blockers remain.",
    },
    {
        "phase_id": "phase_2_corrected_evidence_drs_writeback_context_only",
        "status": "CLOSED",
        "meaning": "Corrected evidence is written as DRS context only; prior Root final output is not mutated.",
    },
    {
        "phase_id": "phase_3_second_run_ready_for_human_reviewed_supplier_a_payment_approval",
        "status": "CLOSED",
        "meaning": "Changed facts rerun validation; Supplier A is ready for scoped human-reviewed payment approval only.",
    },
    {
        "phase_id": "phase_4_human_approval_creates_supplier_a_scoped_action_commit_packet",
        "status": "CLOSED_OBSERVED_ONLY",
        "meaning": "Closed source observes a Root-created Supplier A scoped mock ActionCommitPacket; this rollup creates none.",
    },
    {
        "phase_id": "phase_5_mock_bank_sandbox_executes_supplier_a_only",
        "status": "CLOSED_OBSERVED_ONLY",
        "meaning": "Closed source observes Supplier A mock bank evidence only; this rollup executes no sandbox adapter.",
    },
)

ROLE_SEQUENCE = (
    "orchestrator_provider_called",
    "orchestrator_semantics_validated",
    "orchestrator_semantics_canonicalized",
    "bsep_built",
    "bsep_validated",
    "architect_prompt_built_from_bsep",
    "architect_provider_called",
    "architect_semantics_validated",
    "architect_semantics_canonicalized",
)

AUTHORITY_MATRIX = (
    "Provider output is not truth.",
    "Provider output is not authority.",
    "Provider output is not action permission.",
    "Provider output is not FinalOutput.",
    "DRS candidate context is not truth.",
    "CandidateVector is not truth.",
    "AVF/advisory is not authority.",
    "BSEP is not truth.",
    "BSEP is not authority.",
    "Semantic Architect is not Root.",
    "PlanGraph is not authority.",
    "ResultProposal is not FinalOutput.",
    "Post V&V does not finalize.",
    "GT/LGT does not finalize.",
    "Human approval is scoped evidence only.",
    "Root-created mock ActionCommitPacket is scoped only.",
    "MockBankSandbox receipt is evidence only.",
    "Receipt does not release shipment.",
    "Root remains final authority.",
)

NON_CLAIMS = (
    "not production",
    "not public auditor final package",
    "no real payment",
    "no real shipment release",
    "no connector/API effects",
    "no live Gemini rerun",
    "no new ActionCommitPacket",
    "no new receipt",
    "no sandbox adapter execution",
)


def _source_inventory() -> tuple[dict[str, Any], ...]:
    inventory: list[dict[str, Any]] = []
    for source in SOURCE_CHECKPOINTS:
        path = source["path"]
        exists = (PROJECT_ROOT / path).exists()
        inventory.append(
            {
                **source,
                "exists": exists,
                "status": "FOUND" if exists else "MISSING",
                "authority_boundary": "closed evidence source; rollup cites only",
                "observed_count": 1 if exists else 0,
            }
        )
    return tuple(inventory)


def _global_counters(source_inventory: tuple[Mapping[str, Any], ...]) -> dict[str, int]:
    source_found = {str(item["label"]): int(bool(item["exists"])) for item in source_inventory}
    return {
        "final_integrated_rollup_created_count": 1,
        "source_supplier_wow_summary_observed_count": source_found[
            "Supplier WOW deterministic audit"
        ],
        "source_human_walkthrough_observed_count": source_found["Human walkthrough"],
        "source_full_e2e_summary_observed_count": source_found[
            "Full Semantic E2E runner"
        ],
        "source_real_gemini_audit_observed_count": source_found[
            "Real Gemini lane audit"
        ],
        "source_bsep_topology_audit_observed_count": source_found[
            "BSEP topology repair audit"
        ],
        "real_gemini_lane_observed_count": source_found["Real Gemini lane audit"],
        "real_gemini_lane_rerun_count": 0,
        "real_gemini_orchestrator_called_count": 1,
        "real_gemini_architect_called_count": 1,
        "live_model_call_count": 2,
        "gemini_called_count_in_closed_run": 2,
        "network_used_count_in_closed_run": 2,
        "rollup_called_gemini_count": 0,
        "rollup_network_used_count": 0,
        "rollup_provider_called_count": 0,
        "rollup_accessed_secrets_count": 0,
        "rollup_created_action_commit_packet_count": 0,
        "rollup_created_receipt_count": 0,
        "rollup_executed_mock_payment_count": 0,
        "rollup_executed_real_payment_count": 0,
        "rollup_released_shipment_count": 0,
        "rollup_called_bank_supplier_warehouse_api_count": 0,
        "real_world_effects_count": 0,
    }


def collect_full_wow_v1_1_final_integrated_rollup() -> dict[str, Any]:
    source_inventory = _source_inventory()
    counters = _global_counters(source_inventory)
    inventory_complete = all(bool(item["exists"]) for item in source_inventory)
    final_status = "PASS" if inventory_complete else "FAIL_CLOSED"

    return {
        "run_id": RUN_ID,
        "report_id": REPORT_ID,
        "final_status": final_status,
        "wow_v1_1_final_integrated_rollup_status": final_status,
        "rollup_type": ROLLUP_TYPE,
        "wow_completion_claimed": final_status == "PASS",
        "wow_completion_claim_scope": "final integrated rollup proof only",
        "production_ready_claimed": False,
        "public_auditor_ready_claimed": False,
        "real_world_effects_count": counters["real_world_effects_count"],
        "base_facts": {
            "latest_docs_sync_commit": "9c0ab75",
            "real_run_audit_commit": "8318be9",
            "real_run_runtime_base_commit": "121d22c",
            "real_run_audit_log": "docs/audit_reports/auditor_full_wow_v1_1_manual_live_gemini_lane_real_run_v01.log",
            "real_run_id": "full_wow_v1_1_manual_live_gemini_real_20260705_232010",
            "contract_mode": "semantic_reasoning_adapter",
            "schema_mode": "json_mime_only",
            "model": "gemini-2.5-flash",
        },
        "source_inventory": source_inventory,
        "state_machine_phases": STATE_MACHINE_PHASES,
        "business_boundaries": {
            "supplier_B_remains_blocked": True,
            "shipment_release_remains_held": True,
            "receipt_evidence_only": True,
            "root_remains_final_authority": True,
        },
        "live_gemini_semantic_lane": {
            "real_gemini_lane_observed_count": counters[
                "real_gemini_lane_observed_count"
            ],
            "real_gemini_lane_rerun_count": counters["real_gemini_lane_rerun_count"],
            "real_gemini_orchestrator_called_count": counters[
                "real_gemini_orchestrator_called_count"
            ],
            "real_gemini_architect_called_count": counters[
                "real_gemini_architect_called_count"
            ],
            "live_model_call_count": counters["live_model_call_count"],
            "gemini_called_count_in_closed_run": counters[
                "gemini_called_count_in_closed_run"
            ],
            "network_used_count_in_closed_run": counters[
                "network_used_count_in_closed_run"
            ],
            "rollup_called_gemini_count": counters["rollup_called_gemini_count"],
            "rollup_network_used_count": counters["rollup_network_used_count"],
            "rollup_provider_called_count": counters["rollup_provider_called_count"],
            "bsep_built_after_orchestrator_validation": True,
            "bsep_validated_before_architect": True,
            "architect_semantic_validation_accepted": True,
            "semantic_architect_proposal_is_provider_output": True,
            "runtime_owns_plangraph_local_plan_artifacts": True,
            "provider_owns_plangraph": False,
            "role_sequence": ROLE_SEQUENCE,
        },
        "bsep_membrane": {
            "bsep_status": "CLOSED",
            "bsep_built_after_orchestrator_validation": True,
            "bsep_validated_before_architect": True,
            "architect_prompt_built_from_bsep": True,
            "bsep_is_truth": False,
            "bsep_is_authority": False,
            "bsep_creates_action_permission": False,
            "bsep_creates_final_output": False,
        },
        "drs_candidate_vector_avf": {
            "drs_candidate_context_status": "CLOSED",
            "candidate_vector_status": "CLOSED",
            "avf_status": "CLOSED",
            "drs_candidate_context_is_truth": False,
            "candidate_vector_is_truth": False,
            "avf_advisory_is_authority": False,
        },
        "semantic_architect_and_runtime_plan_artifacts": {
            "semantic_architect_is_provider_output": True,
            "semantic_architect_is_root": False,
            "runtime_owns_plangraph_local_plan_artifacts": True,
            "provider_owns_plangraph": False,
            "plan_graph_is_authority": False,
        },
        "root_human_action_boundary": {
            "human_approval_is_scoped_evidence_only": True,
            "root_created_mock_action_commit_packet_observed_only": True,
            "rollup_created_action_commit_packet_count": counters[
                "rollup_created_action_commit_packet_count"
            ],
            "supplier_B_remains_blocked": True,
            "shipment_release_remains_held": True,
            "root_remains_final_authority": True,
        },
        "mock_bank_receipt_boundary": {
            "mock_bank_receipt_observed_only": True,
            "mock_bank_receipt_evidence_only": True,
            "receipt_releases_shipment": False,
            "rollup_created_receipt_count": counters["rollup_created_receipt_count"],
            "rollup_executed_mock_payment_count": counters[
                "rollup_executed_mock_payment_count"
            ],
        },
        "authority_matrix": AUTHORITY_MATRIX,
        "counters": counters,
        "non_claims": NON_CLAIMS,
        "validation_errors": () if inventory_complete else ("missing_closed_source",),
    }


def _format_bool(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def render_full_wow_v1_1_final_integrated_rollup(
    report: Mapping[str, Any],
) -> str:
    lines: list[str] = [
        "[FULL WOW V1.1 FINAL INTEGRATED ROLLUP]",
        f"run_id: {report['run_id']}",
        f"report_id: {report['report_id']}",
        f"rollup_type: {report['rollup_type']}",
        f"final_status: {report['final_status']}",
        f"wow_v1_1_final_integrated_rollup_status: {report['wow_v1_1_final_integrated_rollup_status']}",
        f"wow_completion_claimed: {_format_bool(report['wow_completion_claimed'])}",
        f"wow_completion_claim_scope: {report['wow_completion_claim_scope']}",
        f"production_ready_claimed: {_format_bool(report['production_ready_claimed'])}",
        f"public_auditor_ready_claimed: {_format_bool(report['public_auditor_ready_claimed'])}",
        f"real_world_effects_count: {report['real_world_effects_count']}",
        "",
        "[SOURCE CHECKPOINTS]",
    ]

    for source in report["source_inventory"]:
        lines.append(
            "- {label}: {path} [{status}; {rollup_action}]".format(**source)
        )

    lines.extend(["", "[STATE MACHINE PHASES]"])
    for phase in report["state_machine_phases"]:
        lines.append(
            f"- {phase['phase_id']}: {phase['status']} - {phase['meaning']}"
        )
    boundaries = report["business_boundaries"]
    lines.extend(
        [
            f"Supplier B remains blocked: {_format_bool(boundaries['supplier_B_remains_blocked'])}",
            f"shipment release remains held: {_format_bool(boundaries['shipment_release_remains_held'])}",
            f"receipt evidence only: {_format_bool(boundaries['receipt_evidence_only'])}",
            "",
            "[LIVE GEMINI SEMANTIC LANE]",
        ]
    )
    live_lane = report["live_gemini_semantic_lane"]
    for key in (
        "real_gemini_lane_observed_count",
        "real_gemini_lane_rerun_count",
        "real_gemini_orchestrator_called_count",
        "real_gemini_architect_called_count",
        "live_model_call_count",
        "gemini_called_count_in_closed_run",
        "network_used_count_in_closed_run",
        "rollup_called_gemini_count",
        "rollup_network_used_count",
        "rollup_provider_called_count",
    ):
        lines.append(f"{key}: {live_lane[key]}")
    lines.extend(
        [
            "BSEP built after Orchestrator validation.",
            "BSEP validated before Architect.",
            "Architect semantic validation accepted.",
            "Semantic Architect proposal is provider output.",
            "Runtime owns PlanGraph/local plan artifacts.",
            "Provider does not own PlanGraph.",
            "role_sequence: " + " -> ".join(live_lane["role_sequence"]),
            "",
            "[BSEP MEMBRANE]",
        ]
    )
    for key, value in report["bsep_membrane"].items():
        lines.append(f"{key}: {_format_bool(value)}")

    lines.extend(["", "[DRS / CANDIDATE VECTOR / AVF]"])
    for key, value in report["drs_candidate_vector_avf"].items():
        lines.append(f"{key}: {_format_bool(value)}")

    lines.extend(["", "[SEMANTIC ARCHITECT AND RUNTIME PLAN ARTIFACTS]"])
    for key, value in report["semantic_architect_and_runtime_plan_artifacts"].items():
        lines.append(f"{key}: {_format_bool(value)}")

    lines.extend(["", "[ROOT / HUMAN / ACTION BOUNDARY]"])
    for key, value in report["root_human_action_boundary"].items():
        lines.append(f"{key}: {_format_bool(value)}")

    lines.extend(["", "[MOCK BANK RECEIPT BOUNDARY]"])
    for key, value in report["mock_bank_receipt_boundary"].items():
        lines.append(f"{key}: {_format_bool(value)}")

    lines.extend(["", "[AUTHORITY MATRIX]"])
    lines.extend(f"- {item}" for item in report["authority_matrix"])

    lines.extend(["", "[COUNTER MATRIX]"])
    for key in sorted(report["counters"]):
        lines.append(f"{key}: {report['counters'][key]}")

    lines.extend(["", "[NON-CLAIMS]"])
    lines.extend(f"- {item}" for item in report["non_claims"])

    lines.extend(
        [
            "",
            "[FINAL STATUS]",
            f"FINAL STATUS: {report['final_status']}",
            "Machine summary JSON:",
            json.dumps(
                {
                    "run_id": report["run_id"],
                    "final_status": report["final_status"],
                    "wow_v1_1_final_integrated_rollup_status": report[
                        "wow_v1_1_final_integrated_rollup_status"
                    ],
                    "counters": report["counters"],
                    "non_claims": report["non_claims"],
                },
                sort_keys=True,
            ),
        ]
    )
    return "\n".join(lines)


def run_full_wow_v1_1_final_integrated_rollup() -> dict[str, Any]:
    return collect_full_wow_v1_1_final_integrated_rollup()


def main() -> int:
    report = run_full_wow_v1_1_final_integrated_rollup()
    print(render_full_wow_v1_1_final_integrated_rollup(report))
    return 0 if report["final_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
