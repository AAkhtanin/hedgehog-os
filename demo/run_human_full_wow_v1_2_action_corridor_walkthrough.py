from __future__ import annotations

from typing import Any, Mapping

from demo import run_full_wow_v1_2_product_trace as product_trace


RUN_ID = "human_full_wow_v1_2_action_corridor_walkthrough_v01"
REPORT_ID = "human_full_wow_v1_2_action_corridor_walkthrough_v01"
WALKTHROUGH_TYPE = "human_product_action_corridor_walkthrough"

REQUIRED_COUNTER_KEYS = (
    "local_drs_v0_2_records_evaluated_count",
    "local_drs_v0_2_direct_reuse_allowed_count",
    "avf_v0_2_candidates_evaluated_count",
    "avf_v0_2_action_permission_granted_count",
    "action_commit_packet_v0_2_root_created_model_packet_count",
    "action_commit_packet_v0_2_created_by_root_count",
    "action_commit_packet_v0_2_created_by_llm_count",
    "action_commit_packet_v0_2_created_by_drs_count",
    "action_commit_packet_v0_2_created_by_avf_count",
    "action_commit_packet_v0_2_created_by_gt_lgt_count",
    "mock_bank_sandbox_v0_2_mock_payment_intent_created_count",
    "mock_bank_sandbox_v0_2_mock_payment_consent_created_count",
    "mock_bank_sandbox_v0_2_mock_payment_order_created_count",
    "mock_bank_sandbox_v0_2_mock_receipt_evidence_created_count",
    "mock_bank_sandbox_v0_2_receipt_permission_created_count",
    "mock_bank_sandbox_v0_2_receipt_supplier_b_authorization_count",
    "mock_bank_sandbox_v0_2_receipt_shipment_release_count",
    "mock_bank_sandbox_v0_2_real_payment_executed_count",
    "mock_bank_sandbox_v0_2_shipment_released_count",
    "real_world_effects_count",
)

NON_CLAIMS = (
    "not production",
    "not public-auditor package",
    "not live",
    "no provider/network/model calls",
    "no real bank",
    "no real payment",
    "no real shipment release",
    "no production connectors",
    "no real-world effects",
)

REQUIRED_SECTIONS = (
    "[HEDGEHOG OS — FULL WOW V1.2 HUMAN ACTION CORRIDOR WALKTHROUGH]",
    "[ONE-SCREEN SUMMARY]",
    "[BUSINESS SCENE]",
    "[TIMELINE]",
    "[WHAT THE BUSINESS MODULES SAW]",
    "[WHAT DRS REMEMBERED]",
    "[WHAT AVF BLOCKED AND RANKED]",
    "[WHAT ROOT APPROVED]",
    "[ACTIONCOMMITPACKET BOUNDARY]",
    "[MOCKBANKSANDBOX CONTRACT FULFILLMENT CORRIDOR]",
    "[MOCK RECEIPT BOUNDARY]",
    "[SUPPLIER B AND SHIPMENT SAFETY]",
    "[WHY THIS MATTERS]",
    "[COUNTER TABLE]",
    "[NON-CLAIMS]",
    "[FINAL STATUS]",
)


def _counter(source_counters: Mapping[str, Any], key: str) -> int:
    return int(source_counters.get(key, 0) or 0)


def _counter_table(source_report: Mapping[str, Any]) -> dict[str, int]:
    counters = source_report.get("counters", {})
    if not isinstance(counters, Mapping):
        counters = {}
    table = {
        "local_drs_v0_2_records_evaluated_count": _counter(
            counters,
            "drs_v0_2_records_evaluated_count",
        ),
        "local_drs_v0_2_direct_reuse_allowed_count": _counter(
            counters,
            "drs_v0_2_direct_reuse_allowed_count",
        ),
    }
    for key in REQUIRED_COUNTER_KEYS:
        if key not in table:
            table[key] = _counter(counters, key)
    table["real_world_effects_count"] = int(
        source_report.get(
            "real_world_effects_count",
            table["real_world_effects_count"],
        )
        or 0
    )
    return table


def _validate_source_report(source_report: Mapping[str, Any]) -> tuple[dict[str, bool], tuple[str, ...]]:
    counters = source_report.get("counters", {})
    if not isinstance(counters, Mapping):
        counters = {}
    table = _counter_table(source_report)

    validation_results = {
        "source_product_trace_pass": source_report.get("product_trace_status")
        == "PASS",
        "drs_direct_reuse_zero": table[
            "local_drs_v0_2_direct_reuse_allowed_count"
        ]
        == 0,
        "avf_permission_action_final_root_bypass_zero": (
            _counter(counters, "avf_v0_2_top_ranked_candidate_permission_granted_count")
            == 0
            and table["avf_v0_2_action_permission_granted_count"] == 0
            and _counter(counters, "avf_v0_2_final_output_created_count") == 0
            and _counter(counters, "avf_v0_2_root_bypass_count") == 0
        ),
        "root_created_packet_count_one": table[
            "action_commit_packet_v0_2_root_created_model_packet_count"
        ]
        == 1,
        "non_root_packet_creator_counts_zero": (
            table["action_commit_packet_v0_2_created_by_llm_count"] == 0
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
            and _counter(
                counters,
                "mock_bank_sandbox_v0_2_receipt_future_permission_created_count",
            )
            == 0
            and _counter(
                counters,
                "mock_bank_sandbox_v0_2_receipt_final_output_created_count",
            )
            == 0
            and table[
                "mock_bank_sandbox_v0_2_receipt_supplier_b_authorization_count"
            ]
            == 0
            and table["mock_bank_sandbox_v0_2_receipt_shipment_release_count"] == 0
            and _counter(
                counters,
                "mock_bank_sandbox_v0_2_receipt_scope_mutation_count",
            )
            == 0
            and _counter(
                counters,
                "mock_bank_sandbox_v0_2_receipt_production_drs_write_count",
            )
            == 0
        ),
        "real_api_counters_zero": (
            _counter(counters, "mock_bank_sandbox_v0_2_real_bank_api_called_count")
            == 0
            and _counter(
                counters,
                "mock_bank_sandbox_v0_2_real_supplier_api_called_count",
            )
            == 0
            and _counter(
                counters,
                "mock_bank_sandbox_v0_2_real_warehouse_api_called_count",
            )
            == 0
        ),
        "provider_network_gemini_counters_zero": (
            _counter(counters, "mock_bank_sandbox_v0_2_provider_called_count") == 0
            and _counter(counters, "mock_bank_sandbox_v0_2_network_called_count")
            == 0
            and _counter(counters, "mock_bank_sandbox_v0_2_gemini_called_count")
            == 0
        ),
        "real_world_effects_zero": table["real_world_effects_count"] == 0,
    }
    errors = tuple(
        key for key, passed in validation_results.items() if passed is not True
    )
    return validation_results, errors


def _business_story() -> tuple[str, ...]:
    return (
        "The user wants to check shipment SH-2042 and the supplier payment path.",
        "Supplier A / Adriatic Filters may be paid in mock sandbox only.",
        "Supplier B / Balkan Pumps remains blocked.",
        "Shipment release remains held.",
    )


def _timeline() -> tuple[str, ...]:
    return (
        "1. Dirty business request.",
        "2. Warehouse and supplier evidence.",
        "3. Legal/accounting/bank preview.",
        "4. DRS memory/reuse classification.",
        "5. AVF hard masks and ranks.",
        "6. Root approval boundary.",
        "7. ActionCommitPacket v0.2 boundary.",
        "8. Contract Fulfillment Corridor.",
        "9. MockBankSandbox mock intent/consent/order.",
        "10. Mock receipt evidence.",
        "11. Supplier B blocked.",
        "12. Shipment held.",
        "13. Final PASS.",
    )


def _business_modules_story(source_report: Mapping[str, Any]) -> tuple[str, ...]:
    modules = source_report.get("business_modules", ())
    lines = []
    for module in modules:
        if isinstance(module, Mapping):
            lines.append(
                "{display_name}: {meaning}".format(
                    display_name=module.get("display_name", module.get("module_id")),
                    meaning=module.get("meaning", "observed evidence"),
                )
            )
    return tuple(lines)


def _drs_story(source_report: Mapping[str, Any]) -> tuple[str, ...]:
    drs = source_report["drs_v0_2_resolve"]
    return (
        "DRS is memory/context only.",
        f"DRS evaluated {drs['records_evaluated_count']} prior traces.",
        f"DRS direct reuse allowed count remains {drs['direct_reuse_allowed_count']}.",
        f"DRS root review required count remains {drs['root_review_required_count']}.",
        "Old receipt is not current permission.",
        "Old Root Final is not silently reused.",
        "DRS is not truth, authority, permission, or FinalOutput.",
    )


def _avf_story(source_report: Mapping[str, Any]) -> tuple[str, ...]:
    avf = source_report["avf_v0_2_evaluation"]
    return (
        f"AVF evaluated {avf['candidates_evaluated_count']} candidate directions.",
        "release_all_and_pay_all was hard-masked.",
        "Supplier B payment was hard-masked.",
        "Old receipt as permission was hard-masked.",
        "Old Root Final as current decision was hard-masked.",
        "Safe candidates may rank but do not grant permission.",
        "Top-ranked candidate is not permission.",
        "AVF score is not authority.",
        "HardMask is not Root.",
    )


def _root_packet_story(source_report: Mapping[str, Any]) -> tuple[str, ...]:
    packet = source_report["action_commit_packet_v0_2_integration"]
    return (
        "Root created one scoped Supplier A ActionCommitPacket v0.2 model.",
        "Human approval is scoped evidence only.",
        "LLM/DRS/AVF/GT-LGT did not create the packet.",
        "Supplier A allowed.",
        "Supplier B forbidden.",
        "Shipment release forbidden.",
        "Real bank/supplier/warehouse APIs forbidden.",
        "Packet accepted for future mock corridor validation.",
        "Registry is local proof-only, not authority, not permission.",
        f"packet_id: {packet['packet_id']}",
    )


def _mock_bank_corridor_story(source_report: Mapping[str, Any]) -> tuple[str, ...]:
    corridor = source_report["mock_bank_sandbox_v0_2_corridor_execution"]
    return (
        "MockBankSandbox corridor consumed the validated Supplier A packet.",
        "The corridor validated packet shape, Root creation, scope, adapter, expiry, idempotency, amount, creditor, payment slot, and forbidden surfaces.",
        "It created mock payment intent, mock consent, and mock payment order.",
        "It returned mock receipt evidence.",
        "Terminal receipt observation was stored only in local proof-only registry.",
        "The corridor is deterministic, not reasoning.",
        "No post-Root reasoning restarted.",
        f"source_packet_id: {corridor['source_packet_id']}",
    )


def _receipt_story() -> tuple[str, ...]:
    return (
        "Receipt is evidence only.",
        "Receipt did not create permission.",
        "Receipt did not create future permission.",
        "Receipt did not create FinalOutput.",
        "Receipt did not authorize Supplier B.",
        "Receipt did not release shipment.",
        "Receipt did not mutate packet scope.",
        "Receipt did not create production DRS record.",
    )


def _supplier_b_and_shipment_story() -> tuple[str, ...]:
    return (
        "Supplier B remained blocked.",
        "Shipment remained held.",
        "Supplier A mock payment evidence does not leak to Supplier B.",
        "Mock receipt does not release shipment.",
    )


def _authority_boundary_story() -> tuple[str, ...]:
    return (
        "DRS remembered but did not decide.",
        "AVF ranked and hard-masked but did not authorize.",
        "Root created the scoped packet.",
        "The deterministic corridor consumed scope and returned evidence/status.",
        "Receipt is not permission.",
        "No real-world effect happened.",
        "Root remained final authority.",
    )


def _one_screen_summary() -> tuple[str, ...]:
    return (
        "The system reviewed shipment SH-2042 and supplier payments.",
        "Warehouse, Supplier A, Supplier B, Legal, Accounting, Bank A, and Bank B evidence were visible.",
        "DRS remembered prior traces but did not decide.",
        "AVF hard-masked unsafe routes and ranked safe directions but did not authorize.",
        "Root created one scoped Supplier A ActionCommitPacket model.",
        "MockBankSandbox consumed only that scoped Supplier A packet.",
        "The corridor checked scope, adapter, expiry, idempotency, amount, creditor, and payment slot.",
        "The corridor created mock payment intent, mock consent, mock order, and mock receipt evidence.",
        "Receipt is evidence only.",
        "Supplier B remained blocked.",
        "Shipment remained held.",
        "No real bank, real payment, real shipment release, or real-world effect happened.",
        "Root remained final authority.",
    )


def collect_human_full_wow_v1_2_action_corridor_walkthrough(
    source_report: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    source = (
        source_report
        if source_report is not None
        else product_trace.collect_full_wow_v1_2_product_trace()
    )
    validation_results, validation_errors = _validate_source_report(source)
    final_status = "PASS" if not validation_errors else "FAIL_CLOSED"
    counter_table = _counter_table(source)
    return {
        "run_id": RUN_ID,
        "report_id": REPORT_ID,
        "walkthrough_status": final_status,
        "final_status": final_status,
        "source_run_id": source.get("run_id", ""),
        "source_report_id": source.get("report_id", ""),
        "source_product_trace_status": source.get("product_trace_status", ""),
        "walkthrough_type": WALKTHROUGH_TYPE,
        "validation_results": validation_results,
        "validation_errors": validation_errors,
        "one_screen_summary": _one_screen_summary(),
        "business_story": _business_story(),
        "timeline": _timeline(),
        "business_modules_story": _business_modules_story(source),
        "drs_story": _drs_story(source),
        "avf_story": _avf_story(source),
        "root_packet_story": _root_packet_story(source),
        "mock_bank_corridor_story": _mock_bank_corridor_story(source),
        "receipt_boundary_story": _receipt_story(),
        "supplier_b_and_shipment_story": _supplier_b_and_shipment_story(),
        "authority_boundary_story": _authority_boundary_story(),
        "counter_table": counter_table,
        "non_claims": NON_CLAIMS,
    }


def _append_section(lines: list[str], title: str, values: tuple[str, ...]) -> None:
    lines.extend(["", title])
    lines.extend(f"- {value}" for value in values)


def render_human_full_wow_v1_2_action_corridor_walkthrough(
    report: Mapping[str, Any],
) -> str:
    lines: list[str] = [
        "[HEDGEHOG OS — FULL WOW V1.2 HUMAN ACTION CORRIDOR WALKTHROUGH]",
        f"run_id: {report['run_id']}",
        f"report_id: {report['report_id']}",
        f"walkthrough_type: {report['walkthrough_type']}",
        f"walkthrough_status: {report['walkthrough_status']}",
        f"source_run_id: {report['source_run_id']}",
        f"source_product_trace_status: {report['source_product_trace_status']}",
    ]
    _append_section(lines, "[ONE-SCREEN SUMMARY]", report["one_screen_summary"])
    _append_section(lines, "[BUSINESS SCENE]", report["business_story"])
    _append_section(lines, "[TIMELINE]", report["timeline"])
    _append_section(
        lines,
        "[WHAT THE BUSINESS MODULES SAW]",
        report["business_modules_story"],
    )
    _append_section(lines, "[WHAT DRS REMEMBERED]", report["drs_story"])
    _append_section(lines, "[WHAT AVF BLOCKED AND RANKED]", report["avf_story"])
    _append_section(lines, "[WHAT ROOT APPROVED]", report["root_packet_story"])
    _append_section(
        lines,
        "[ACTIONCOMMITPACKET BOUNDARY]",
        report["root_packet_story"],
    )
    _append_section(
        lines,
        "[MOCKBANKSANDBOX CONTRACT FULFILLMENT CORRIDOR]",
        report["mock_bank_corridor_story"],
    )
    _append_section(
        lines,
        "[MOCK RECEIPT BOUNDARY]",
        report["receipt_boundary_story"],
    )
    _append_section(
        lines,
        "[SUPPLIER B AND SHIPMENT SAFETY]",
        report["supplier_b_and_shipment_story"],
    )
    _append_section(lines, "[WHY THIS MATTERS]", report["authority_boundary_story"])
    lines.extend(["", "[COUNTER TABLE]"])
    for key in REQUIRED_COUNTER_KEYS:
        lines.append(f"{key}: {report['counter_table'][key]}")
    _append_section(lines, "[NON-CLAIMS]", report["non_claims"])
    lines.extend(
        [
            "",
            "[FINAL STATUS]",
            f"FINAL STATUS: {report['final_status']}",
        ]
    )
    if report.get("validation_errors"):
        lines.append("validation_errors:")
        lines.extend(f"- {error}" for error in report["validation_errors"])
    return "\n".join(lines)


def run_human_full_wow_v1_2_action_corridor_walkthrough() -> str:
    return render_human_full_wow_v1_2_action_corridor_walkthrough(
        collect_human_full_wow_v1_2_action_corridor_walkthrough()
    )


def main() -> int:
    report = collect_human_full_wow_v1_2_action_corridor_walkthrough()
    print(render_human_full_wow_v1_2_action_corridor_walkthrough(report))
    return 0 if report["final_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
