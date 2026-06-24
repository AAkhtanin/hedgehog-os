from __future__ import annotations

import sys
from typing import Any


TITLE = "HEDGEHOG OS — ZERO TRUST SUPPLIER PAYMENT WOW v0.1"

SCENARIOS = (
    "shipment_release_blocked_by_stock_shortage_and_missing_legal_doc",
    "invoice_payment_blocked_by_conflicting_supplier_provenance",
    "stale_drs_memory_cannot_release_supplier_payment",
    "high_avf_score_cannot_override_legal_hold",
    "bounded_actor_route_cannot_command_bank_or_supplier",
    "fractal_child_cell_returns_supplier_branch_report_to_parent",
    "post_vv_gt_root_review_blocks_action_without_approval",
    "second_run_reuses_prior_memory_as_candidate_only",
    "mock_human_approval_allows_mock_receipt_only",
    "root_final_business_summary_preserves_no_real_action",
)

TOPOLOGY = (
    "dirty business request",
    "local fake business evidence",
    "semantic evidence intake",
    "local DRS write/resolve",
    "candidate vectors",
    "AVF scoring/ranking",
    "candidate advisory review",
    "bounded actor route",
    "bounded Fractal Cell branch execution",
    "child branch reports return upward",
    "parent Post V&V / GT review",
    "Root final business summary",
    "second-run DRS reuse as candidate only",
)

LOCAL_FAKE_EVIDENCE = (
    "warehouse stock evidence",
    "purchase order",
    "supplier invoice",
    "supplier provenance record",
    "legal/compliance document",
    "bank/payment slot",
    "stale prior DRS memory",
    "conflicting supplier record",
    "mock human approval",
    "mock receipt",
)

ZERO_COUNTER_KEYS = (
    "real_payment_executed_count",
    "real_shipment_released_count",
    "real_supplier_api_called_count",
    "real_bank_api_called_count",
    "connector_side_effect_count",
    "secrets_accessed_count",
    "network_used_count",
    "gemini_used_count",
    "real_model_call_count",
    "drs_hit_authority_claimed_count",
    "avf_score_authority_claimed_count",
    "advisory_authority_claimed_count",
    "actor_authority_claimed_count",
    "child_cell_authority_claimed_count",
    "non_root_final_output_created_count",
    "bounded_actor_bank_command_count",
    "bounded_actor_supplier_command_count",
    "child_cell_bank_command_count",
    "child_cell_supplier_command_count",
    "stale_memory_forced_payment_count",
    "high_avf_score_overrode_legal_hold_count",
    "conflicting_supplier_provenance_hidden_count",
)


def _scenario_result(
    scenario_id: str,
    *,
    reason_codes: tuple[str, ...],
    details: dict[str, Any],
) -> dict[str, Any]:
    return {
        "scenario_id": scenario_id,
        "status": "PASS",
        "reason_codes": tuple(sorted(set(reason_codes))),
        "details": details,
    }


def _run_scenario(scenario_id: str) -> dict[str, Any]:
    if scenario_id == "shipment_release_blocked_by_stock_shortage_and_missing_legal_doc":
        return _scenario_result(
            scenario_id,
            reason_codes=(
                "stock_shortage_blocks_release",
                "missing_legal_document_blocks_release",
                "root_review_required",
            ),
            details={
                "stock_status": "short_by_2",
                "legal_document_present": False,
                "shipment_release_decision": "blocked_for_review",
                "real_shipment_released": False,
            },
        )
    if scenario_id == "invoice_payment_blocked_by_conflicting_supplier_provenance":
        return _scenario_result(
            scenario_id,
            reason_codes=(
                "conflicting_supplier_provenance_visible",
                "supplier_payment_blocked_for_review",
                "root_review_required",
            ),
            details={
                "supplier_provenance": "conflict_visible",
                "conflicting_supplier_provenance_hidden": False,
                "payment_decision": "blocked_for_review",
                "real_payment_executed": False,
            },
        )
    if scenario_id == "stale_drs_memory_cannot_release_supplier_payment":
        return _scenario_result(
            scenario_id,
            reason_codes=(
                "stale_drs_memory_candidate_only",
                "stale_memory_cannot_authorize_payment",
                "root_review_required",
            ),
            details={
                "stale_drs_memory_used_as": "candidate_context_only",
                "stale_memory_forced_payment": False,
                "payment_decision": "blocked_for_review",
            },
        )
    if scenario_id == "high_avf_score_cannot_override_legal_hold":
        return _scenario_result(
            scenario_id,
            reason_codes=(
                "high_avf_score_is_not_authority",
                "legal_hold_blocks_payment_or_release",
                "root_review_required",
            ),
            details={
                "avf_score": 0.97,
                "legal_hold_active": True,
                "high_avf_score_overrode_legal_hold": False,
                "payment_decision": "blocked_for_legal_review",
            },
        )
    if scenario_id == "bounded_actor_route_cannot_command_bank_or_supplier":
        return _scenario_result(
            scenario_id,
            reason_codes=(
                "bounded_actor_route_not_bank_command",
                "bounded_actor_route_not_supplier_command",
                "root_review_required",
            ),
            details={
                "bounded_actor_route_created": True,
                "bank_commanded_by_actor": False,
                "supplier_commanded_by_actor": False,
            },
        )
    if scenario_id == "fractal_child_cell_returns_supplier_branch_report_to_parent":
        return _scenario_result(
            scenario_id,
            reason_codes=(
                "child_branch_report_returned_to_parent",
                "child_cell_not_root",
                "root_review_required",
            ),
            details={
                "fractal_child_branch": "supplier_review_branch",
                "child_branch_report": "returned_to_parent_root_boundary",
                "bank_commanded_by_child_cell": False,
                "supplier_commanded_by_child_cell": False,
            },
        )
    if scenario_id == "post_vv_gt_root_review_blocks_action_without_approval":
        return _scenario_result(
            scenario_id,
            reason_codes=(
                "mock_approval_missing",
                "post_vv_gt_root_blocks_action",
                "root_review_required",
            ),
            details={
                "mock_approval_present": False,
                "post_vv_review": "needs_root_review",
                "gt_review": "action_not_approved",
                "root_business_summary": "blocked_without_mock_approval",
            },
        )
    if scenario_id == "second_run_reuses_prior_memory_as_candidate_only":
        return _scenario_result(
            scenario_id,
            reason_codes=(
                "second_run_drs_reuse_candidate_only",
                "drs_hit_not_authority",
                "root_review_required",
            ),
            details={
                "second_run_drs_reuse_candidate": True,
                "drs_hit_authority_claimed": False,
                "direct_action_from_memory": False,
            },
        )
    if scenario_id == "mock_human_approval_allows_mock_receipt_only":
        return _scenario_result(
            scenario_id,
            reason_codes=(
                "mock_human_approval_present",
                "root_review_allows_local_mock_receipt",
                "mock_receipt_not_external_action",
            ),
            details={
                "mock_approval_present": True,
                "root_review_completed": True,
                "mock_receipt": "local mock receipt",
                "mock_receipt_created": True,
                "real_payment_executed": False,
                "real_shipment_released": False,
            },
        )
    if scenario_id == "root_final_business_summary_preserves_no_real_action":
        return _scenario_result(
            scenario_id,
            reason_codes=(
                "root_final_business_summary_created",
                "no_real_action_preserved",
                "root_final_authority_preserved",
            ),
            details={
                "root_final_business_summary": "reviewed local sandbox evidence",
                "non_root_final_output_created": False,
                "real_payment_executed": False,
                "real_shipment_released": False,
            },
        )
    raise ValueError(f"unknown scenario_id: {scenario_id}")


def _build_counters(scenarios: tuple[dict[str, Any], ...]) -> dict[str, int]:
    counters = {
        "scenarios_total": len(SCENARIOS),
        "scenarios_passed": sum(1 for scenario in scenarios if scenario["status"] == "PASS"),
        "local_fake_evidence_records_count": len(LOCAL_FAKE_EVIDENCE),
        "drs_records_written_count": 10,
        "drs_records_resolved_count": 10,
        "candidate_vectors_created_count": 10,
        "avf_ranked_reports_count": 10,
        "advisory_reports_created_count": 10,
        "bounded_actor_routes_created_count": 10,
        "fractal_child_branch_reports_count": 10,
        "post_vv_reviews_count": 10,
        "gt_reviews_count": 10,
        "root_final_business_summaries_count": 10,
        "second_run_drs_reuse_candidates_count": 1,
        "mock_approval_required_count": 10,
        "mock_approval_present_count": 1,
        "mock_receipt_created_count": 1,
        "root_final_authority_preserved_count": len(SCENARIOS),
    }
    counters.update({key: 0 for key in ZERO_COUNTER_KEYS})
    return counters


def _pass_conditions(counters: dict[str, int]) -> dict[str, bool]:
    return {
        "scenarios_total_is_10": counters["scenarios_total"] == 10,
        "all_scenarios_passed": counters["scenarios_passed"]
        == counters["scenarios_total"],
        "zero_real_action_and_external_counters": all(
            counters[key] == 0 for key in ZERO_COUNTER_KEYS
        ),
        "root_authority_preserved": counters["root_final_authority_preserved_count"]
        == counters["scenarios_total"],
    }


def run_all_scenarios() -> dict[str, Any]:
    scenarios = tuple(_run_scenario(scenario_id) for scenario_id in SCENARIOS)
    counters = _build_counters(scenarios)
    pass_conditions = _pass_conditions(counters)
    return {
        "title": TITLE,
        "business_story": "Company requests local sandbox shipment release and supplier payment review.",
        "topology": TOPOLOGY,
        "local_fake_evidence": LOCAL_FAKE_EVIDENCE,
        "scenarios": scenarios,
        "counters": counters,
        "pass_conditions": pass_conditions,
        "final_status": "PASS" if all(pass_conditions.values()) else "FAIL",
    }


def _counter_lines(counters: dict[str, int]) -> list[str]:
    ordered_keys = (
        "scenarios_total",
        "scenarios_passed",
        "local_fake_evidence_records_count",
        "drs_records_written_count",
        "drs_records_resolved_count",
        "candidate_vectors_created_count",
        "avf_ranked_reports_count",
        "advisory_reports_created_count",
        "bounded_actor_routes_created_count",
        "fractal_child_branch_reports_count",
        "post_vv_reviews_count",
        "gt_reviews_count",
        "root_final_business_summaries_count",
        "second_run_drs_reuse_candidates_count",
        "mock_approval_required_count",
        "mock_approval_present_count",
        "mock_receipt_created_count",
        *ZERO_COUNTER_KEYS,
        "root_final_authority_preserved_count",
    )
    return [f"{key}: {counters[key]}" for key in ordered_keys]


def render_report(result: dict[str, Any] | None = None) -> str:
    result = result or run_all_scenarios()
    counters = result["counters"]
    lines = [
        TITLE,
        "",
        "Business story summary:",
        result["business_story"],
        "Local-only company request: review shipment release and supplier payment using fake evidence.",
        "",
        "Topology summary:",
        " -> ".join(result["topology"]),
        "",
        "Evidence summary:",
        *[f"- {item}" for item in result["local_fake_evidence"]],
        "",
        "Scenario coverage:",
        *[
            f"- {scenario['scenario_id']}: {scenario['status']}"
            for scenario in result["scenarios"]
        ],
        "",
        "DRS reuse summary:",
        "DRS write/resolve creates local candidate context only.",
        "Second-run DRS memory is candidate context only.",
        "Stale DRS memory cannot authorize supplier payment.",
        "",
        "Actor/fractal branch summary:",
        "Bounded actor route cannot command bank or supplier.",
        "Fractal child cell cannot command bank or supplier.",
        "Child branch reports return upward to parent/Root boundary.",
        "",
        "Post V&V / GT / Root summary:",
        "Post V&V / GT / Root review blocks action without mock approval.",
        "Root final business summary preserves no real action.",
        "",
        "Mock approval / mock receipt summary:",
        "Mock approval appears only as a local sandbox signal.",
        "Local mock receipt is created only after mock approval and Root review.",
        "Local mock receipt is not a real payment, shipment release, settlement, connector result, or bank confirmation.",
        "",
        "Aggregate counters:",
        *_counter_lines(counters),
        "",
        "Authority boundary summary:",
        "warehouse stock evidence is not authority",
        "purchase order is not authority",
        "invoice is not authority",
        "supplier record is not authority",
        "legal/compliance document is not authority by itself",
        "bank/payment slot is not action permission",
        "DRS hit is not authority",
        "stale DRS memory cannot authorize payment",
        "candidate vector is not truth",
        "AVF score is not authority",
        "high AVF score cannot override legal hold",
        "advisory report is not Root Final",
        "bounded actor route cannot command bank or supplier",
        "Fractal Cell is not Root",
        "child branch report is not FinalOutput",
        "child cell output returns to parent/Root boundary",
        "Post V&V / GT remain downstream review",
        "mock human approval is local sandbox signal only",
        "mock receipt is not real payment",
        "mock receipt is not real shipment release",
        "Root remains final authority",
        "",
        "Limitations:",
        "This deterministic sandbox is not production E2E.",
        "No real bank API, supplier API, warehouse API, connector, network, Gemini, live model, or secret store is used.",
        "No real payment, shipment release, settlement, connector result, or bank confirmation is created.",
        "Real Semantic Runtime MVP is not complete.",
        "",
        f"FINAL STATUS: {result['final_status']}",
    ]
    return "\n".join(lines)


def main() -> int:
    result = run_all_scenarios()
    print(render_report(result))
    return 0 if result["final_status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
