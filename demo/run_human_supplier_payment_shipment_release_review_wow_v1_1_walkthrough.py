from __future__ import annotations

import json
import sys
from typing import Any

from demo import run_supplier_payment_shipment_release_review_wow_v1_1 as slice_d_runner


TITLE = "Supplier Payment / Shipment Release Review LIVE-DUAL-ROLE WOW v1.1"
SHORT_NAME = "HEDGEHOG OS — ZERO-TRUST SUPPLIER PAYMENT WOW v1.1"
WALKTHROUGH_ID = (
    "supplier_payment_shipment_release_review_wow_v1_1_slice_e_human_walkthrough"
)


def _bool_text(value: bool) -> str:
    return "true" if value else "false"


def _counter(source_summary: dict[str, Any], key: str) -> int:
    return int(source_summary["action_counters"].get(key, 0))


def _source_summary_checks(source_summary: dict[str, Any]) -> dict[str, Any]:
    second_run_outcomes = tuple(source_summary["second_run"]["root_outcome"])
    return {
        "first_run_root_final_decision": source_summary["first_run"][
            "root_final_decision"
        ],
        "first_run_root_final_decision_is_not_ready": (
            source_summary["first_run"]["root_final_decision"] == "NOT_READY"
        ),
        "corrected_evidence_status": source_summary["corrected_evidence"]["status"],
        "corrected_evidence_preserved": (
            source_summary["corrected_evidence"]["status"] == "EXECUTED_IN_SLICE_C"
        ),
        "second_run_contains_supplier_A_approval_ready": (
            "READY_FOR_HUMAN_REVIEWED_SUPPLIER_A_PAYMENT_APPROVAL"
            in second_run_outcomes
        ),
        "second_run_contains_shipment_release_held": (
            "SHIPMENT_RELEASE_STILL_HELD_OR_SEPARATE_APPROVAL_REQUIRED"
            in second_run_outcomes
        ),
        "second_run_contains_supplier_B_blocked": (
            "SUPPLIER_B_REMAINS_BLOCKED" in second_run_outcomes
        ),
        "human_approval_status": source_summary["human_approval"]["status"],
        "mock_action_commit_packet_status": source_summary[
            "mock_action_commit_packet"
        ]["status"],
        "mock_execution_status": source_summary["mock_execution"]["status"],
        "receipt_status": source_summary["receipt"]["status"],
        "action_commit_packet_created_by_root_count": _counter(
            source_summary,
            "action_commit_packet_created_by_root_count",
        ),
        "action_commit_packet_created_by_llm_count": _counter(
            source_summary,
            "action_commit_packet_created_by_llm_count",
        ),
        "mock_bank_receipt_created_count": _counter(
            source_summary,
            "mock_bank_receipt_created_count",
        ),
        "mock_payment_executed_count": _counter(
            source_summary,
            "mock_payment_executed_count",
        ),
        "real_payment_executed_count": _counter(
            source_summary,
            "real_payment_executed_count",
        ),
        "shipment_released_count": _counter(
            source_summary,
            "shipment_released_count",
        ),
        "mock_shipment_released_count": _counter(
            source_summary,
            "mock_shipment_released_count",
        ),
        "real_world_effects_count": _counter(
            source_summary,
            "real_world_effects_count",
        ),
    }


def _walkthrough_counters(source_summary: dict[str, Any]) -> dict[str, int]:
    return {
        "human_walkthrough_created_count": 1,
        "human_report_created_count": 1,
        "story_sections_count": 10,
        "source_slice_d_summary_observed_count": 1,
        "walkthrough_created_action_commit_packet_count": 0,
        "walkthrough_invoked_mock_bank_count": 0,
        "walkthrough_created_receipt_count": 0,
        "underlying_action_commit_packet_created_count": _counter(
            source_summary,
            "action_commit_packet_created_count",
        ),
        "underlying_action_commit_packet_created_by_root_count": _counter(
            source_summary,
            "action_commit_packet_created_by_root_count",
        ),
        "underlying_action_commit_packet_created_by_llm_count": _counter(
            source_summary,
            "action_commit_packet_created_by_llm_count",
        ),
        "underlying_mock_bank_receipt_created_count": _counter(
            source_summary,
            "mock_bank_receipt_created_count",
        ),
        "underlying_mock_payment_executed_count": _counter(
            source_summary,
            "mock_payment_executed_count",
        ),
        "underlying_real_payment_executed_count": _counter(
            source_summary,
            "real_payment_executed_count",
        ),
        "underlying_supplier_B_payment_executed_count": _counter(
            source_summary,
            "supplier_B_payment_executed_count",
        ),
        "underlying_shipment_released_count": _counter(
            source_summary,
            "shipment_released_count",
        ),
        "underlying_mock_shipment_released_count": _counter(
            source_summary,
            "mock_shipment_released_count",
        ),
        "underlying_real_world_effects_count": _counter(
            source_summary,
            "real_world_effects_count",
        ),
        "human_approval_scope_supplier_B_count": _counter(
            source_summary,
            "human_approval_scope_supplier_B_count",
        ),
        "human_approval_scope_shipment_release_count": _counter(
            source_summary,
            "human_approval_scope_shipment_release_count",
        ),
        "human_approval_is_broad_authority_count": _counter(
            source_summary,
            "human_approval_is_broad_authority_count",
        ),
        "supplier_B_remains_blocked_count": _counter(
            source_summary,
            "supplier_B_payment_blocked_count",
        ),
        "shipment_release_remains_held_count": _counter(
            source_summary,
            "shipment_release_still_held_count",
        ),
        "receipt_is_evidence_only_count": _counter(
            source_summary,
            "receipt_is_evidence_count",
        ),
        "receipt_releases_shipment_count": _counter(
            source_summary,
            "receipt_releases_shipment_count",
        ),
        "network_used_count": _counter(source_summary, "network_used_count"),
        "gemini_called_count": _counter(source_summary, "gemini_called_count"),
        "real_model_call_count": _counter(source_summary, "real_model_call_count"),
        "live_model_call_count": _counter(source_summary, "live_model_call_count"),
        "orchestrator_provider_call_count": _counter(
            source_summary,
            "orchestrator_provider_call_count",
        ),
        "architect_provider_call_count": _counter(
            source_summary,
            "architect_provider_call_count",
        ),
        "raw_secret_literals_seen_count": 0,
        "production_ready_claimed_count": 0,
        "public_auditor_ready_claimed_count": 0,
        "full_generic_mock_connector_sandbox_execution_claimed_count": 0,
        "supplier_A_bank_only_mock_path_claimed_count": 1,
    }


def build_human_walkthrough_summary() -> dict[str, Any]:
    source_summary = (
        slice_d_runner.run_supplier_payment_shipment_release_review_wow_v1_1()
    )
    source_summary_json_serializable = True
    try:
        json.dumps(source_summary, sort_keys=True)
    except TypeError:
        source_summary_json_serializable = False

    counters = _walkthrough_counters(source_summary)
    checks = _source_summary_checks(source_summary)
    all_source_checks_passed = (
        source_summary["slice_status"] == "PASS"
        and source_summary_json_serializable
        and checks["first_run_root_final_decision_is_not_ready"]
        and checks["corrected_evidence_preserved"]
        and checks["second_run_contains_supplier_A_approval_ready"]
        and checks["second_run_contains_shipment_release_held"]
        and checks["second_run_contains_supplier_B_blocked"]
        and checks["human_approval_status"] == "EXECUTED_IN_SLICE_D"
        and checks["mock_action_commit_packet_status"] == "EXECUTED_IN_SLICE_D"
        and checks["mock_execution_status"] == "EXECUTED_IN_SLICE_D"
        and checks["receipt_status"] == "EXECUTED_IN_SLICE_D"
        and counters["underlying_action_commit_packet_created_by_root_count"] == 1
        and counters["underlying_action_commit_packet_created_by_llm_count"] == 0
        and counters["underlying_mock_bank_receipt_created_count"] == 1
        and counters["underlying_mock_payment_executed_count"] == 1
        and counters["underlying_real_payment_executed_count"] == 0
        and counters["underlying_shipment_released_count"] == 0
        and counters["underlying_mock_shipment_released_count"] == 0
        and counters["underlying_real_world_effects_count"] == 0
    )

    return {
        "walkthrough_id": WALKTHROUGH_ID,
        "source_run_id": source_summary["run_id"],
        "source_slice_id": source_summary["slice_id"],
        "walkthrough_status": "PASS" if all_source_checks_passed else "FAIL_CLOSED",
        "final_status": "PASS" if all_source_checks_passed else "FAIL_CLOSED",
        "lane": "deterministic_ci_human_walkthrough",
        "wow_accepted": False,
        "wow_completion_claimed": False,
        "production_ready_claimed": False,
        "public_auditor_ready_claimed": False,
        "source_slice_d_status": source_summary["slice_status"],
        "source_summary_json_serializable": source_summary_json_serializable,
        "human_report_created": True,
        "human_report_is_json_wall": False,
        "story_sections_count": counters["story_sections_count"],
        "ready_for_audit_docs_sync": all_source_checks_passed,
        "optional_gemini_lane_executed": False,
        "source_summary_checks": checks,
        "walkthrough_counters": counters,
        "business_snapshot": {
            "shipment_id": source_summary["inline_fixtures"]["business_request"][
                "shipment_id"
            ],
            "supplier_A": {
                "supplier_id": "supplier_A",
                "product": "water_filter",
                "invoice": "INV-2042",
                "bank": "Bank A Sandbox",
                "initial_blockers": (
                    "water_filter short_by_2",
                    "insurance certificate expired",
                    "payment forms require human approval",
                ),
            },
            "supplier_B": {
                "supplier_id": "supplier_B",
                "product": "pump_valve",
                "invoice": "INV-2043",
                "blockers": (
                    "Supplier B invoice mismatch",
                    "Supplier B delivery delayed",
                    "legal review still required",
                ),
            },
        },
        "source_story": {
            "first_run": source_summary["first_run"],
            "corrected_evidence": {
                "status": source_summary["corrected_evidence"]["status"],
                "corrected_supplier_A_evidence": source_summary[
                    "corrected_evidence"
                ]["corrected_supplier_A_evidence"],
                "supplier_B_blockers": source_summary["corrected_evidence"][
                    "supplier_B_blockers"
                ],
                "drs_writeback_traces": source_summary["corrected_evidence"][
                    "drs_writeback_traces"
                ],
            },
            "second_run": source_summary["second_run"],
            "human_approval": source_summary["human_approval"],
            "mock_action_commit_packet": {
                key: source_summary["mock_action_commit_packet"][key]
                for key in (
                    "status",
                    "created_by",
                    "packet_type",
                    "business_scope",
                    "supplier_id",
                    "payment_slot",
                    "invoice_id",
                    "amount",
                    "mock_only",
                    "real_world_effects_allowed",
                    "supplier_B_included",
                    "shipment_release_included",
                    "final_output_claimed",
                    "executes_itself",
                    "validation_accepted",
                )
            },
            "mock_execution": {
                key: source_summary["mock_execution"][key]
                for key in (
                    "status",
                    "sandbox",
                    "supplier_id",
                    "payment_slot",
                    "invoice_id",
                    "amount",
                    "mock_payment_executed",
                    "real_payment_executed",
                    "real_bank_api_called",
                    "real_supplier_api_called",
                    "real_warehouse_api_called",
                    "shipment_released",
                    "mock_shipment_released",
                    "real_world_effects",
                    "supplier_B_payment_executed",
                )
            },
            "receipt": {
                key: source_summary["receipt"][key]
                for key in (
                    "status",
                    "receipt_created",
                    "receipt_type",
                    "receipt_scope",
                    "supplier_id",
                    "payment_slot",
                    "invoice_id",
                    "amount",
                    "sandbox",
                    "receipt_is_evidence",
                    "receipt_is_truth",
                    "receipt_is_action_permission",
                    "receipt_is_final_output",
                    "receipt_releases_shipment",
                    "supplier_B_included",
                    "real_payment_claimed",
                    "real_world_effects_claimed",
                )
            },
        },
    }


def render_human_walkthrough(summary: dict[str, Any] | None = None) -> str:
    data = summary or build_human_walkthrough_summary()
    story = data["source_story"]
    business = data["business_snapshot"]
    counters = data["walkthrough_counters"]
    first_run = story["first_run"]
    corrected = story["corrected_evidence"]
    second_run = story["second_run"]
    approval = story["human_approval"]
    packet = story["mock_action_commit_packet"]
    execution = story["mock_execution"]
    receipt = story["receipt"]

    lines = [
        TITLE,
        SHORT_NAME,
        "Human Walkthrough — Slice E",
        f"FINAL STATUS: {data['final_status']}",
        f"WOW ACCEPTED: {_bool_text(data['wow_accepted'])}",
        "",
        "Provider proposes semantics.",
        "Runtime canonicalizes.",
        "Validators verify.",
        "Root decides.",
        "",
        "LLM understands the business process, but does not get sovereignty.",
        "DRS helps, but does not decide.",
        "AVF ranks, but does not authorize.",
        "Root blocks unsafe action.",
        "Human approval is scoped.",
        "Only scoped mock payment executes.",
        "Supplier B remains blocked.",
        "shipment release remains held.",
        "Real world untouched.",
        "",
        "ACT 1 — Dirty business request",
        f"Company reviews {business['shipment_id']} and supplier payment readiness.",
        (
            "Supplier A: water_filter, INV-2042, Bank A Sandbox, initial blockers: "
            + ", ".join(business["supplier_A"]["initial_blockers"])
            + "."
        ),
        (
            "Supplier B: pump_valve, INV-2043, blockers: "
            + ", ".join(business["supplier_B"]["blockers"])
            + "."
        ),
        "APIs return facts.",
        "Hedgehog decides what those facts are allowed to become.",
        "Action: none.",
        "",
        "ACT 2 — First run Root Final: NOT_READY",
    ]
    lines.extend(f"- {reason}" for reason in first_run["root_reasons"])
    lines.append("Prepared artifacts:")
    lines.extend(f"- {artifact}" for artifact in first_run["prepared_artifacts"])
    lines.extend(
        [
            "No payment.",
            "shipment release remains held.",
            "",
            "ACT 3 — Corrected evidence",
            "- insurance_certificate valid",
            "- warehouse water_filter +2 arrived",
            "- supplier_A stock confirmed",
            "- Supplier B remains blocked",
            f"- DRS traces: {', '.join(corrected['drs_writeback_traces'])}",
            "DRS writeback is context/evidence only.",
            "prior Root Final not mutated.",
            "corrected evidence is not authority.",
            "",
            "ACT 4 — Second run",
            "DRS reuse allowed as context only.",
            "changed facts rerun validation.",
        ]
    )
    lines.extend(f"- {outcome}" for outcome in second_run["root_outcome"])
    lines.extend(
        [
            "Supplier A becomes ready for human-reviewed payment approval only.",
            "Supplier B remains blocked.",
            "shipment release remains held or separate approval required.",
            "No ActionCommitPacket yet at second-run boundary.",
            "",
            "ACT 5 — Scoped human approval",
            "deterministic scoped human fixture.",
            f"permission_scope: {approval['permission_scope']}",
            f"approval_id: {approval['approval_id']}",
            f"supplier_B_in_scope: {_bool_text(approval['supplier_B_in_scope'])}",
            (
                "shipment_release_in_scope: "
                f"{_bool_text(approval['shipment_release_in_scope'])}"
            ),
            "human approval is not broad authority.",
            "Root remains final authority.",
            "",
            "ACT 6 — Root-created mock ActionCommitPacket",
            f"created_by: {packet['created_by']}",
            f"packet_type: {packet['packet_type']}",
            f"mock_only: {_bool_text(packet['mock_only'])}",
            "Supplier A only.",
            f"supplier_B_included: {_bool_text(packet['supplier_B_included'])}",
            (
                "shipment_release_included: "
                f"{_bool_text(packet['shipment_release_included'])}"
            ),
            (
                "real_world_effects_allowed: "
                f"{_bool_text(packet['real_world_effects_allowed'])}"
            ),
            "ActionCommitPacket is not FinalOutput.",
            "ActionCommitPacket does not execute itself.",
            "",
            "ACT 7 — MockBankSandbox receipt",
            "MockBankSandbox / Supplier A-only fake bank adapter path.",
            "inside the mock connector boundary.",
            "not full generic MockConnectorSandbox three-adapter execution.",
            "local fake sandbox only.",
            f"mock_execution_status: {execution['status']}",
            f"payment_slot: {execution['payment_slot']}",
            f"mock_payment_executed: {_bool_text(execution['mock_payment_executed'])}",
            "mock bank receipt created.",
            f"receipt_type: {receipt['receipt_type']}",
            "receipt is evidence only.",
            "receipt is not truth.",
            "receipt is not action permission.",
            "receipt is not FinalOutput.",
            "mock bank receipt does not release shipment.",
            "mock payment receipt does not release shipment.",
            f"supplier_B_payment_executed: {_bool_text(execution['supplier_B_payment_executed'])}",
            f"real_payment_executed: {_bool_text(execution['real_payment_executed'])}",
            f"real_world_effects: {_bool_text(execution['real_world_effects'])}",
            "",
            "ACT 8 — Final authority ledger",
            "Provider output is not truth.",
            "Provider output is not authority.",
            "BSEP is not truth.",
            "BSEP is not authority.",
            "DRS hit is not authority.",
            "AVF score is not authority.",
            "CandidateVector is not action permission.",
            "PlanGraph is not authority.",
            "ResultProposal is not FinalOutput.",
            "GT/LGT is not Root.",
            "Human approval is scoped evidence, not broad authority.",
            "Root-created mock ActionCommitPacket is scoped only.",
            "Mock receipt is evidence, not truth/action permission/final output.",
            "Mock payment receipt does not release shipment.",
            "Root remains final authority.",
            "",
            "Non-claims",
            "- not production",
            "- not real bank integration",
            "- not real supplier API",
            "- not real warehouse connector",
            "- not real payment",
            "- not real shipment release",
            "- not production ActionCommitPacket",
            "- not production Permission UX",
            "- not autonomous action",
            "- not public auditor final package",
            "- optional Gemini lane not executed",
            "- audit/docs sync not done yet",
            "",
            "Walkthrough counters:",
            f"- human_walkthrough_created_count: {counters['human_walkthrough_created_count']}",
            f"- source_slice_d_summary_observed_count: {counters['source_slice_d_summary_observed_count']}",
            f"- walkthrough_created_action_commit_packet_count: {counters['walkthrough_created_action_commit_packet_count']}",
            f"- walkthrough_invoked_mock_bank_count: {counters['walkthrough_invoked_mock_bank_count']}",
            f"- walkthrough_created_receipt_count: {counters['walkthrough_created_receipt_count']}",
            f"- underlying_action_commit_packet_created_count: {counters['underlying_action_commit_packet_created_count']}",
            f"- underlying_mock_bank_receipt_created_count: {counters['underlying_mock_bank_receipt_created_count']}",
            f"- underlying_real_payment_executed_count: {counters['underlying_real_payment_executed_count']}",
            f"- underlying_shipment_released_count: {counters['underlying_shipment_released_count']}",
            f"- underlying_real_world_effects_count: {counters['underlying_real_world_effects_count']}",
            f"- network_used_count: {counters['network_used_count']}",
            f"- gemini_called_count: {counters['gemini_called_count']}",
            f"- real_model_call_count: {counters['real_model_call_count']}",
            f"- live_model_call_count: {counters['live_model_call_count']}",
            f"- orchestrator_provider_call_count: {counters['orchestrator_provider_call_count']}",
            f"- architect_provider_call_count: {counters['architect_provider_call_count']}",
            f"- full_generic_mock_connector_sandbox_execution_claimed_count: {counters['full_generic_mock_connector_sandbox_execution_claimed_count']}",
            f"- supplier_A_bank_only_mock_path_claimed_count: {counters['supplier_A_bank_only_mock_path_claimed_count']}",
            "",
            "The business process is visible, but sovereignty never leaves Root.",
            "",
            f"FINAL STATUS: {data['final_status']}",
            f"WOW ACCEPTED: {_bool_text(data['wow_accepted'])}",
        ]
    )
    return "\n".join(lines)


def run_human_supplier_payment_shipment_release_review_wow_v1_1_walkthrough() -> str:
    return render_human_walkthrough(build_human_walkthrough_summary())


def main(argv: list[str] | None = None) -> int:
    _ = argv
    print(run_human_supplier_payment_shipment_release_review_wow_v1_1_walkthrough())
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
