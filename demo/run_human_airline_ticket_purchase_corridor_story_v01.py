from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Mapping


RUN_ID = "human_airline_ticket_purchase_corridor_story_v01"
REPORT_ID = "human_airline_ticket_purchase_corridor_story_v01"
STORY_TYPE = "artifact_backed_airline_ticket_purchase_corridor_human_story"

PASS = "PASS"
FAIL_CLOSED = "FAIL_CLOSED"
SKIPPED_CLOSED = "SKIPPED_CLOSED"

SOURCE_JSON_ENV = "HEDGEHOG_AIRLINE_CORRIDOR_STORY_SOURCE_JSON"

EXPECTED_TRANSACTION_ID = "tri_airline_purchase:PAR-LIM:2026-08-12:client_001"
CLIENT_ROOT_ID = "root:client_os_001"
AIRLINE_ROOT_ID = "root:mock_airline_al"
BANK_ROOT_ID = "root:mock_bank_a"

PHASE_ORDER = (
    "airline_offer_hold_phase",
    "client_purchase_intent_phase",
    "bank_payment_authorization_phase",
    "airline_ticket_issue_phase",
    "client_completion_phase",
)
PHASE_ROOTS = {
    "airline_offer_hold_phase": AIRLINE_ROOT_ID,
    "client_purchase_intent_phase": CLIENT_ROOT_ID,
    "bank_payment_authorization_phase": BANK_ROOT_ID,
    "airline_ticket_issue_phase": AIRLINE_ROOT_ID,
    "client_completion_phase": CLIENT_ROOT_ID,
}

EXPECTED_CORE_CHECK_IDS = {
    "no_post_root_reasoning",
    "corridor_deterministic_only",
    "root_phase_ownership",
    "ttl_and_expiry",
    "idempotency",
    "receipt_evidence_only",
    "airline_offer_hold_bindings",
    "airline_ticket_issue_bindings",
}
DIRECT_CORE_CHECK_IDS = {
    "no_post_root_reasoning",
    "corridor_deterministic_only",
}

HOLD_SANDBOX = "airline_hold_sandbox_v01"
TICKET_SANDBOX = "airline_ticket_sandbox_v01"
COMPLETION_OBSERVER = "client_completion_observer"

ONE_SCREEN_SUMMARY = (
    "Одна уже существующая mock-авиасделка прошла через пять последовательных "
    "Root-границ: AirlineRoot разрешил удержание предложения, ClientRoot создал "
    "отдельное намерение покупки на основании человеческого согласия, BankRoot "
    "предоставил bounded mock-авторизацию, AirlineRoot разрешил mock-выпуск билета, "
    "а ClientRoot наблюдал завершение. Универсальный Hedgehog guard запрещал "
    "возобновление LLM-рассуждений после каждого Root, Airline-домен проверял "
    "offer, hold, пассажира, маршрут, сумму, валюту и merchant, а sandbox и "
    "completion observer создавали только evidence-only receipts. Вся цепочка "
    "осталась одной транзакцией без передачи власти, реального платежа, билета, "
    "бронирования или внешнего API-вызова."
)

CORE_DOMAIN_SENTENCE = (
    "Ядро не знает, что такое авиабилет или PNR. Ядро охраняет общую контрактную "
    "геометрию. Airline-домен объясняет ядру, какие авиационные связи должны "
    "совпасть."
)

NEXT_GATE = "airline_ticket_purchase_corridor_v01_integrated_audit"


def collect_human_airline_ticket_purchase_corridor_story_v01(
    *,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    active_env = os.environ if env is None else env
    source_json = active_env.get(SOURCE_JSON_ENV, "")
    base = _empty_report(source_json=source_json)
    if not source_json:
        return base

    try:
        source = json.loads(Path(source_json).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return _failed_report(
            source_json=source_json,
            errors=(f"source_report_json_unreadable:{type(exc).__name__}",),
        )
    if not isinstance(source, Mapping):
        return _failed_report(
            source_json=source_json,
            errors=("source_report_json_top_level_not_object",),
        )

    validation_errors = _validate_source(source)
    final_status = PASS if not validation_errors else FAIL_CLOSED
    if final_status != PASS:
        return _failed_report(source_json=source_json, errors=validation_errors)

    phase_cards = _phase_cards(source)
    identity_lineage_story = _identity_lineage_story(source)
    receipt_creator_story = _receipt_creator_story(source)
    binding_matrix_story = _binding_matrix_story(source)
    counter_table = _counter_table(source, phase_cards, identity_lineage_story, receipt_creator_story)

    return {
        "run_id": RUN_ID,
        "report_id": REPORT_ID,
        "story_type": STORY_TYPE,
        "final_status": final_status,
        "skip_reason": "",
        "source_report_json": source_json,
        "source_identity": _source_identity(source),
        "one_screen_summary": ONE_SCREEN_SUMMARY,
        "business_scene": _business_scene(source),
        "one_transaction_three_roots": _one_transaction_three_roots(source),
        "semantic_to_contract_boundary": _semantic_to_contract_boundary(),
        "root_centered_phase_story": _root_centered_phase_story(source),
        "phase_cards": phase_cards,
        "transition_story": _transition_story(source),
        "core_domain_delegation_story": _core_domain_delegation_story(source),
        "identity_lineage_story": identity_lineage_story,
        "receipt_creator_story": receipt_creator_story,
        "binding_matrix_story": binding_matrix_story,
        "evidence_crosses_authority_does_not_story": (
            _evidence_crosses_authority_does_not_story(source)
        ),
        "fail_closed_story": _fail_closed_story(),
        "mock_happy_path": _mock_happy_path(source),
        "root_boundary_story": _root_boundary_story(source),
        "counter_table": counter_table,
        "source_validation": {
            "accepted": final_status == PASS,
            "error_count": len(validation_errors),
            "source_final_status": source.get("final_status"),
            "source_transaction_id": source.get("transaction_id"),
        },
        "validation_errors": validation_errors,
        "non_claims": _non_claims(),
        "next_gate": NEXT_GATE,
    }


def render_human_airline_ticket_purchase_corridor_story_v01(
    report: Mapping[str, Any],
) -> str:
    lines = [
        "[HEDGEHOG OS — AIRLINE TICKET/PURCHASE CORRIDOR HUMAN STORY]",
        f"run_id: {report['run_id']}",
        f"report_id: {report['report_id']}",
        f"story_type: {report['story_type']}",
        "",
        "[ONE-SCREEN SUMMARY]",
        str(report["one_screen_summary"]),
    ]
    if report["final_status"] != PASS:
        lines.extend(
            (
                "",
                "[FINAL STATUS]",
                f"final_status: {report['final_status']}",
            ),
        )
        if report.get("skip_reason"):
            lines.append(f"skip_reason: {report['skip_reason']}")
        if report.get("validation_errors"):
            lines.append("validation_errors:")
            for error in report["validation_errors"]:
                lines.append(f"- {error}")
        return "\n".join(lines)

    lines.extend(
        (
            "",
            "[BUSINESS SCENE]",
            _format_mapping(report["business_scene"]),
            "",
            "[ONE TRANSACTION / THREE ROOTS]",
            _format_mapping(report["one_transaction_three_roots"]),
            "",
            "[SEMANTIC PLANE → CONTRACT PLANE]",
            _format_lines(report["semantic_to_contract_boundary"]),
            "",
            "[FIVE ROOT-CENTERED PHASES]",
            _format_lines(report["root_centered_phase_story"]),
        ),
    )
    section_names = (
        "[PHASE 1 — AIRLINE OFFER / HOLD]",
        "[PHASE 2 — CLIENT PURCHASE INTENT]",
        "[PHASE 3 — BANK PAYMENT AUTHORIZATION]",
        "[PHASE 4 — AIRLINE MOCK TICKET ISSUE]",
        "[PHASE 5 — CLIENT COMPLETION]",
    )
    for section_name, card in zip(section_names, report["phase_cards"]):
        lines.extend(("", section_name, _format_mapping(card)))

    lines.extend(
        (
            "",
            "[UNIVERSAL CORE VS AIRLINE DOMAIN]",
            _format_mapping(report["core_domain_delegation_story"]),
            "",
            "[IDENTITY AND LINEAGE]",
        ),
    )
    for card in report["identity_lineage_story"]:
        lines.append(_format_mapping(card))
    lines.extend(("", "[WHO CREATES RECEIPTS]"))
    for card in report["receipt_creator_story"]:
        lines.append(_format_mapping(card))

    lines.extend(
        (
            "",
            "[BINDING MATRIX — WHY THIS IS NOT A SECOND DEMO]",
            report["binding_matrix_story"]["human_introduction"],
        ),
    )
    for row in report["binding_matrix_story"]["rows"]:
        lines.append(_format_mapping(row))

    lines.extend(
        (
            "",
            "[EVIDENCE CROSSES ROOTS; AUTHORITY DOES NOT]",
            _format_lines(report["evidence_crosses_authority_does_not_story"]),
            "",
            "[FAIL-CLOSED BOUNDARIES]",
            _format_lines(report["fail_closed_story"]),
            "",
            "[MOCK HAPPY PATH]",
            _format_lines(report["mock_happy_path"]),
            "",
            "[COUNTER TABLE]",
        ),
    )
    for key in sorted(report["counter_table"]):
        lines.append(f"{key}: {report['counter_table'][key]}")
    lines.extend(("", "[NON-CLAIMS]", _format_lines(report["non_claims"])))
    lines.extend(("", "[NEXT GATE]", str(report["next_gate"])))
    lines.extend(
        (
            "",
            "[FINAL STATUS]",
            f"final_status: {report['final_status']}",
        ),
    )
    if report["validation_errors"]:
        lines.append("validation_errors:")
        for error in report["validation_errors"]:
            lines.append(f"- {error}")
    return "\n".join(lines)


def run_human_airline_ticket_purchase_corridor_story_v01(
    *,
    env: Mapping[str, str] | None = None,
) -> str:
    return render_human_airline_ticket_purchase_corridor_story_v01(
        collect_human_airline_ticket_purchase_corridor_story_v01(env=env),
    )


def main() -> int:
    print(run_human_airline_ticket_purchase_corridor_story_v01())
    return 0


def _empty_report(*, source_json: str) -> dict[str, Any]:
    return {
        "run_id": RUN_ID,
        "report_id": REPORT_ID,
        "story_type": STORY_TYPE,
        "final_status": SKIPPED_CLOSED,
        "skip_reason": "source_report_json_not_selected",
        "source_report_json": source_json,
        "source_identity": {},
        "one_screen_summary": ONE_SCREEN_SUMMARY,
        "business_scene": {},
        "one_transaction_three_roots": {},
        "semantic_to_contract_boundary": (),
        "root_centered_phase_story": (),
        "phase_cards": (),
        "transition_story": (),
        "core_domain_delegation_story": {},
        "identity_lineage_story": (),
        "receipt_creator_story": (),
        "binding_matrix_story": {"human_introduction": "", "rows": ()},
        "evidence_crosses_authority_does_not_story": (),
        "fail_closed_story": (),
        "mock_happy_path": (),
        "root_boundary_story": (),
        "counter_table": {
            "renderer_source_json_read_count": 0,
            "renderer_corridor_execution_count": 0,
            "renderer_provider_called_count": 0,
            "renderer_network_used_count": 0,
            "renderer_gemini_called_count": 0,
            "renderer_real_world_effects_count": 0,
        },
        "source_validation": {"accepted": False},
        "validation_errors": (),
        "non_claims": _non_claims(),
        "next_gate": NEXT_GATE,
    }


def _failed_report(*, source_json: str, errors: tuple[str, ...]) -> dict[str, Any]:
    report = _empty_report(source_json=source_json)
    report["final_status"] = FAIL_CLOSED
    report["skip_reason"] = ""
    report["validation_errors"] = errors
    report["counter_table"] = {
        **report["counter_table"],
        "renderer_source_json_read_count": 1,
    }
    report["source_validation"] = {
        "accepted": False,
        "error_count": len(errors),
    }
    return report


def _validate_source(source: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    fixtures = _mapping(source.get("mock_protocol_fixtures"))
    corridor = _mapping(source.get("airline_ticket_purchase_corridor_v0_1"))
    integration = _mapping(source.get("airline_ticket_purchase_corridor_integration"))
    binding_rows = _sequence(source.get("airline_ticket_purchase_corridor_binding_matrix"))
    counters = _mapping(source.get("counter_table"))

    if source.get("final_status") != PASS:
        errors.append("source_final_status_not_pass")
    if source.get("transaction_id") != EXPECTED_TRANSACTION_ID:
        errors.append("source_transaction_id_mismatch")
    identity = _mapping(source.get("transaction_identity"))
    if identity.get("transaction_id") != EXPECTED_TRANSACTION_ID:
        errors.append("transaction_identity_transaction_mismatch")
    if identity.get("client_root_id") != CLIENT_ROOT_ID:
        errors.append("transaction_identity_client_root_mismatch")
    if identity.get("airline_root_id") != AIRLINE_ROOT_ID:
        errors.append("transaction_identity_airline_root_mismatch")
    if identity.get("bank_root_id") != BANK_ROOT_ID:
        errors.append("transaction_identity_bank_root_mismatch")
    if identity.get("mock_only") is not True:
        errors.append("transaction_identity_not_mock_only")
    participants = _mapping(source.get("participants"))
    if set(participants) != {"ClientRoot", "AirlineRoot", "BankRoot"}:
        errors.append("source_roots_not_exactly_three")
        errors.append("shared_or_fourth_root_detected")
    else:
        for participant, root_id in (
            ("ClientRoot", CLIENT_ROOT_ID),
            ("AirlineRoot", AIRLINE_ROOT_ID),
            ("BankRoot", BANK_ROOT_ID),
        ):
            if _mapping(participants.get(participant)).get("root_id") != root_id:
                errors.append(f"participant_root_id_mismatch:{participant}")
    if source.get("validation_errors") not in ((), [], None):
        errors.append("source_validation_errors_present")

    for section, status_key in (
        ("airline_offer_hold_sandbox", "sandbox_status"),
        ("bank_payment_authorization_sandbox", "sandbox_status"),
        ("client_purchase_orchestration", "orchestration_status"),
        ("airline_ticket_issue_mock_corridor", "corridor_status"),
        ("final_tri_party_mock_summary", "final_status"),
    ):
        if _mapping(source.get(section)).get(status_key) != PASS:
            errors.append(f"source_section_not_pass:{section}")

    expected_integration = {
        "integration_status": PASS,
        "corridor_final_status": PASS,
        "corridor_public_validation_accepted": True,
        "corridor_report_bound_to_projected_fixtures": True,
        "existing_runner_artifacts_projected": True,
        "five_root_centered_phases_observed": True,
        "parallel_fixture_transaction_created": False,
        "duplicate_corridor_execution_count": 0,
        "runtime_packets_created_count": 0,
        "runtime_receipts_created_count": 0,
        "adapter_execution_count": 0,
        "authority_transferred": False,
        "real_world_effects_count": 0,
    }
    for key, expected in expected_integration.items():
        if integration.get(key) != expected:
            errors.append(f"integration_fact_mismatch:{key}")

    phases = tuple(_mapping(phase) for phase in _sequence(corridor.get("phase_results")))
    transitions = tuple(_mapping(item) for item in _sequence(corridor.get("transitions")))
    if tuple(phase.get("phase_id") for phase in phases) != PHASE_ORDER:
        errors.append("corridor_phase_order_mismatch")
    if len(phases) != 5:
        errors.append("corridor_phase_count_mismatch")
    if len(transitions) != 4:
        errors.append("corridor_transition_count_mismatch")
    expected_evidence = _expected_phase_evidence(source)
    for phase in phases:
        phase_id = phase.get("phase_id")
        if phase.get("phase_status") != PASS:
            errors.append(f"corridor_phase_not_pass:{phase_id}")
        for key in (
            "root_gate_validated",
            "core_corridor_guard_validated",
            "domain_contracts_validated",
            "later_phases_allowed",
        ):
            if phase.get(key) is not True:
                errors.append(f"corridor_phase_required_true_mismatch:{phase_id}:{key}")
        if phase.get("transaction_id") != EXPECTED_TRANSACTION_ID:
            errors.append(f"corridor_phase_transaction_mismatch:{phase_id}")
        if phase.get("relevant_root_id") != PHASE_ROOTS.get(str(phase_id)):
            errors.append(f"corridor_phase_root_mismatch:{phase_id}")
        if tuple(phase.get("evidence_refs_observed", ())) != expected_evidence.get(phase_id):
            errors.append(f"corridor_phase_evidence_mismatch:{phase_id}")
        if phase.get("return_to_relevant_root") is not False:
            errors.append(f"corridor_phase_return_to_root_mismatch:{phase_id}")
        if phase.get("authority_transferred") is not False:
            errors.append(f"corridor_phase_authority_transfer:{phase_id}")
        if phase.get("runtime_receipt_created") is not False:
            errors.append(f"corridor_phase_runtime_receipt_created:{phase_id}")
        for key in ("provider_called", "network_used", "gemini_called"):
            if phase.get(key) is not False:
                errors.append(f"corridor_phase_provider_boundary:{phase_id}:{key}")
        if phase.get("real_world_effects_count") != 0:
            errors.append(f"corridor_phase_effects_nonzero:{phase_id}")
        if tuple(phase.get("reason_codes", ())) != ():
            errors.append(f"corridor_phase_reason_codes_not_empty:{phase_id}")
    expected_transitions = tuple(zip(PHASE_ORDER[:-1], PHASE_ORDER[1:]))
    for index, transition in enumerate(transitions, start=1):
        expected_from, expected_to = (
            expected_transitions[index - 1]
            if index <= len(expected_transitions)
            else ("", "")
        )
        if transition.get("transition_index") != index:
            errors.append("corridor_transition_index_mismatch")
        if (
            transition.get("from_phase_id") != expected_from
            or transition.get("to_phase_id") != expected_to
        ):
            errors.append("corridor_transition_adjacency_mismatch")
        if transition.get("source_phase_passed") is not True:
            errors.append("corridor_transition_source_not_passed")
        if transition.get("dependency_satisfied") is not True:
            errors.append("corridor_transition_dependency_unsatisfied")
        if transition.get("transition_status") != PASS:
            errors.append("corridor_transition_not_pass")
        if transition.get("transaction_id") != EXPECTED_TRANSACTION_ID:
            errors.append("corridor_transition_transaction_mismatch")
        if transition.get("authority_transferred") is not False:
            errors.append("corridor_transition_authority_transfer")
        if transition.get("semantic_reasoning_restarted") is not False:
            errors.append("corridor_transition_semantic_reasoning_restarted")
        if tuple(transition.get("reason_codes", ())) != ():
            errors.append("corridor_transition_reason_codes_not_empty")

    root_counts = {
        CLIENT_ROOT_ID: sum(1 for phase in phases if phase.get("relevant_root_id") == CLIENT_ROOT_ID),
        AIRLINE_ROOT_ID: sum(1 for phase in phases if phase.get("relevant_root_id") == AIRLINE_ROOT_ID),
        BANK_ROOT_ID: sum(1 for phase in phases if phase.get("relevant_root_id") == BANK_ROOT_ID),
    }
    if root_counts != {CLIENT_ROOT_ID: 2, AIRLINE_ROOT_ID: 2, BANK_ROOT_ID: 1}:
        errors.append("corridor_root_phase_counts_mismatch")

    corridor_counters = _mapping(corridor.get("counter_table"))
    for key, expected in (
        ("fixture_receipts_observed_count", 3),
        ("runtime_receipts_created_count", 0),
        ("runtime_packets_created_count", 0),
        ("adapter_execution_count", 0),
        ("cross_root_authority_transfer_count", 0),
    ):
        if corridor_counters.get(key) != expected:
            errors.append(f"corridor_counter_mismatch:{key}")
    for key, expected in (
        ("shared_root_created_count", 0),
        ("fourth_root_created_count", 0),
        ("supplier_specific_core_fixture_used_count", 0),
        ("dishonest_field_mapping_count", 0),
        ("second_universal_authority_engine_created_count", 0),
        ("core_imports_airline_domain_count", 0),
    ):
        if corridor_counters.get(key) != expected:
            if key == "shared_root_created_count" or key == "fourth_root_created_count":
                errors.append("shared_or_fourth_root_detected")
            elif key == "supplier_specific_core_fixture_used_count":
                errors.append("supplier_specific_core_fixture_detected")
            elif key == "dishonest_field_mapping_count":
                errors.append("dishonest_field_mapping_detected")
            elif key == "second_universal_authority_engine_created_count":
                errors.append("second_universal_authority_engine_detected")
            elif key == "core_imports_airline_domain_count":
                errors.append("core_imports_airline_domain_detected")
    _validate_core_domain_delegation(corridor, errors)
    _validate_root_boundary_matrix(source, errors)
    _validate_cross_root_matrix(source, errors)

    if not binding_rows:
        errors.append("binding_matrix_missing")
    if {row.get("transaction_id") for row in binding_rows} != {EXPECTED_TRANSACTION_ID}:
        errors.append("binding_matrix_transaction_mismatch")
    for row in binding_rows:
        if row.get("values_match") is not True:
            errors.append(f"binding_row_mismatch:{row.get('binding_id')}")
        if row.get("raw_secret_used") is not False:
            errors.append(f"binding_row_raw_secret_used:{row.get('binding_id')}")
        if row.get("authority_transferred") is not False:
            errors.append(f"binding_row_authority_transfer:{row.get('binding_id')}")
    row_by_id = {row.get("binding_id"): row for row in binding_rows}
    transaction_row = _mapping(row_by_id.get("transaction_id"))
    if (
        transaction_row.get("unique_transaction_id_count") != 1
        or transaction_row.get("all_transaction_ids_match") is not True
        or not isinstance(transaction_row.get("projected_value"), list)
    ):
        errors.append("transaction_binding_not_artifact_backed")
    required_binding_ids = {
        "offer_hold_receipt_created_by",
        "offer_hold_receipt_root_owner",
        "mock_ticket_receipt_created_by",
        "mock_ticket_receipt_root_owner",
        "mock_purchase_receipt_created_by",
        "mock_purchase_receipt_root_owner",
        "client_purchase_approval_ref",
        "client_purchase_intent_id",
        "purchase_intent_source_human_approval_ref",
        "payment_authorization_receipt_id",
        "payment_authorization_ref_id",
        "authorization_ref_source_receipt_id",
        "mock_purchase_receipt_id",
        "client_final_summary_mock_purchase_receipt_id",
    }
    missing_bindings = sorted(required_binding_ids - set(row_by_id))
    if missing_bindings:
        errors.append(f"binding_rows_missing:{','.join(missing_bindings)}")

    client_approval = _mapping(fixtures.get("ClientPurchaseApprovalEvidenceV01"))
    bank_receipt = _mapping(fixtures.get("BankPaymentAuthorizationReceiptV01"))
    purchase_receipt = _mapping(fixtures.get("MockPurchaseReceiptV01"))
    final_summary = _mapping(fixtures.get("ClientFinalTravelSummaryV01"))
    if client_approval.get("approval_id") == client_approval.get("client_purchase_intent_id"):
        errors.append("human_approval_reused_as_purchase_intent")
    if row_by_id.get("purchase_intent_source_human_approval_ref", {}).get("projected_value") != client_approval.get("approval_id"):
        errors.append("purchase_intent_human_approval_lineage_mismatch")
    if bank_receipt.get("receipt_id") == bank_receipt.get("payment_authorization_ref_id"):
        errors.append("bank_receipt_reused_as_authorization_ref")
    if row_by_id.get("authorization_ref_source_receipt_id", {}).get("projected_value") != bank_receipt.get("receipt_id"):
        errors.append("authorization_ref_receipt_lineage_mismatch")
    if purchase_receipt.get("receipt_id") == final_summary.get("summary_id"):
        errors.append("purchase_receipt_reused_as_final_summary")

    _validate_receipts(fixtures, errors)
    _validate_required_source_counters(counters, binding_rows, errors)
    for key, aliases in (
        ("provider_called_count", ()),
        ("network_used_count", ()),
        ("gemini_called_count", ()),
        ("real_airline_api_called_count", ()),
        ("real_bank_api_called_count", ()),
        ("real_gds_api_called_count", ("airline_root_called_real_gds_api_count",)),
        ("real_payment_executed_count", ()),
        ("real_ticket_issued_count", ()),
        ("real_booking_created_count", ()),
        ("real_world_effects_count", ()),
    ):
        if _counter_value(counters, key, aliases) != 0:
            errors.append(f"source_zero_effect_counter_nonzero:{key}")

    return tuple(dict.fromkeys(errors))


def _validate_receipts(fixtures: Mapping[str, Any], errors: list[str]) -> None:
    hold = _mapping(fixtures.get("AirlineOfferHoldReceiptV01"))
    ticket = _mapping(fixtures.get("MockTicketReceiptV01"))
    purchase = _mapping(fixtures.get("MockPurchaseReceiptV01"))
    if hold.get("created_by") != HOLD_SANDBOX:
        errors.append("offer_hold_receipt_creator_mismatch")
    if hold.get("root_owner") != AIRLINE_ROOT_ID:
        errors.append("offer_hold_receipt_root_owner_mismatch")
    if ticket.get("created_by") != TICKET_SANDBOX:
        errors.append("mock_ticket_receipt_creator_mismatch")
    if ticket.get("root_owner") != AIRLINE_ROOT_ID:
        errors.append("mock_ticket_receipt_root_owner_mismatch")
    if purchase.get("created_by") != COMPLETION_OBSERVER:
        errors.append("mock_purchase_receipt_creator_mismatch")
    if purchase.get("root_owner") != CLIENT_ROOT_ID:
        errors.append("mock_purchase_receipt_root_owner_mismatch")
    for name, receipt in (
        ("offer_hold", hold),
        ("mock_ticket", ticket),
        ("mock_purchase", purchase),
    ):
        if receipt.get("evidence_only") is not True:
            errors.append(f"{name}_receipt_not_evidence_only")
    for key in (
        "purchase_permission_created",
        "payment_permission_created",
        "ticket_permission_created",
        "future_permission_created",
    ):
        if key in hold and hold.get(key) is not False:
            errors.append(f"offer_hold_receipt_forbidden_flag:{key}")
    if "real_world_effects_count" in hold and hold.get("real_world_effects_count") != 0:
        errors.append("offer_hold_receipt_forbidden_flag:real_world_effects_count")
    for key in (
        "real_ticket",
        "real_booking",
        "future_ticket_permission_created",
        "future_payment_permission_created",
        "payment_created",
    ):
        if key in ticket and ticket.get(key) is not False:
            errors.append(f"mock_ticket_receipt_forbidden_flag:{key}")
    if "real_travel_booking_created" in ticket and ticket.get("real_travel_booking_created") is not False:
        errors.append("mock_ticket_receipt_forbidden_flag:real_booking")
    if "real_world_effects_count" in ticket and ticket.get("real_world_effects_count") != 0:
        errors.append("mock_ticket_receipt_forbidden_flag:real_world_effects_count")
    for key in (
        "side_root_finals_replaced",
        "root_truth_rewritten",
        "future_permission_created",
        "real_payment_executed",
        "real_ticket_issued",
        "real_booking_created",
    ):
        if key in purchase and purchase.get(key) is not False:
            errors.append(f"mock_purchase_receipt_forbidden_flag:{key}")
    if (
        "real_world_effects_count" in purchase
        and purchase.get("real_world_effects_count") != 0
    ):
        errors.append("mock_purchase_receipt_forbidden_flag:real_world_effects_count")


def _validate_cross_root_matrix(source: Mapping[str, Any], errors: list[str]) -> None:
    rows = tuple(_mapping(row) for row in _sequence(source.get("cross_root_evidence_routing_matrix")))
    if not rows:
        errors.append("cross_root_evidence_matrix_missing")
        return
    for row in rows:
        if row.get("transaction_id") not in (None, EXPECTED_TRANSACTION_ID):
            errors.append("cross_root_transaction_mismatch")
        if row.get("authority_transferred") is not False:
            errors.append("cross_root_authority_transfer_detected")
        if row.get("evidence_only") is not True:
            errors.append("cross_root_authority_transfer_detected")
        for key, value in row.items():
            if key != "authority_transferred" and "authority" in key and value is True:
                errors.append("cross_root_authority_transfer_detected")


def _validate_root_boundary_matrix(source: Mapping[str, Any], errors: list[str]) -> None:
    rows = tuple(_mapping(row) for row in _sequence(source.get("root_boundary_matrix")))
    if not rows:
        errors.append("root_boundary_matrix_missing")
        return
    for row in rows:
        if row.get("boundary_preserved") is not True:
            errors.append("root_boundary_not_preserved")
        if row.get("violation_count") != 0:
            errors.append("root_boundary_violation_nonzero")
    participants = _mapping(source.get("participants"))
    if set(participants) != {"ClientRoot", "AirlineRoot", "BankRoot"}:
        errors.append("shared_or_fourth_root_detected")
    for row in rows:
        boundary = str(row.get("boundary", "")).lower()
        if ("fourth root" in boundary or "shared root" in boundary) and (
            row.get("boundary_preserved") is not True
            or row.get("violation_count") != 0
        ):
            errors.append("shared_or_fourth_root_detected")


def _validate_core_domain_delegation(
    corridor: Mapping[str, Any],
    errors: list[str],
) -> None:
    rows = tuple(
        _mapping(row)
        for row in _sequence(corridor.get("core_domain_delegation_matrix"))
    )
    if not rows:
        errors.append("core_domain_delegation_matrix_missing")
        return
    if len(rows) != 8:
        errors.append("core_domain_delegation_row_count_mismatch")
    check_ids = tuple(row.get("check_id") for row in rows)
    if len(set(check_ids)) != len(check_ids):
        errors.append("core_domain_delegation_check_missing")
    missing = EXPECTED_CORE_CHECK_IDS - set(check_ids)
    if missing:
        errors.append("core_domain_delegation_check_missing")
    direct_ids = {
        row.get("check_id")
        for row in rows
        if row.get("directly_delegated_to_core") is True
    }
    if direct_ids != DIRECT_CORE_CHECK_IDS:
        errors.append("core_direct_delegation_count_mismatch")
    counters = _mapping(corridor.get("counter_table"))
    for key, reason in (
        ("supplier_specific_core_fixture_used_count", "supplier_specific_core_fixture_detected"),
        ("dishonest_field_mapping_count", "dishonest_field_mapping_detected"),
        ("second_universal_authority_engine_created_count", "second_universal_authority_engine_detected"),
        ("core_imports_airline_domain_count", "core_imports_airline_domain_detected"),
    ):
        if counters.get(key) != 0:
            errors.append(reason)


def _validate_required_source_counters(
    counters: Mapping[str, Any],
    binding_rows: tuple[Any, ...],
    errors: list[str],
) -> None:
    expected = {
        "airline_ticket_purchase_corridor_integration_count": 1,
        "airline_ticket_purchase_corridor_pass_count": 1,
        "airline_ticket_purchase_corridor_fail_count": 0,
        "airline_ticket_purchase_corridor_phase_count": 5,
        "airline_ticket_purchase_corridor_phase_pass_count": 5,
        "airline_ticket_purchase_corridor_transition_count": 4,
        "airline_ticket_purchase_corridor_transition_pass_count": 4,
        "airline_ticket_purchase_corridor_binding_row_count": len(binding_rows),
        "airline_ticket_purchase_corridor_binding_match_count": len(binding_rows),
        "airline_ticket_purchase_corridor_binding_mismatch_count": 0,
        "airline_ticket_purchase_corridor_parallel_transaction_count": 0,
        "airline_ticket_purchase_corridor_duplicate_execution_count": 0,
        "airline_ticket_purchase_corridor_fixture_receipts_observed_count": 3,
        "airline_ticket_purchase_corridor_runtime_receipts_created_count": 0,
        "airline_ticket_purchase_corridor_runtime_packets_created_count": 0,
        "airline_ticket_purchase_corridor_adapter_execution_count": 0,
        "airline_ticket_purchase_corridor_cross_root_authority_transfer_count": 0,
        "airline_ticket_purchase_corridor_post_root_reasoning_restart_count": 0,
        "airline_ticket_purchase_corridor_provider_called_count": 0,
        "airline_ticket_purchase_corridor_network_used_count": 0,
        "airline_ticket_purchase_corridor_gemini_called_count": 0,
        "provider_called_count": 0,
        "network_used_count": 0,
        "gemini_called_count": 0,
        "real_airline_api_called_count": 0,
        "real_bank_api_called_count": 0,
        "real_payment_executed_count": 0,
        "real_ticket_issued_count": 0,
        "real_booking_created_count": 0,
        "real_world_effects_count": 0,
    }
    for key, expected_value in expected.items():
        if counters.get(key) != expected_value:
            errors.append(f"source_counter_mismatch:{key}")
    if _counter_value(counters, "real_gds_api_called_count", ("airline_root_called_real_gds_api_count",)) != 0:
        errors.append("source_counter_mismatch:real_gds_api_called_count")


def _expected_phase_evidence(source: Mapping[str, Any]) -> dict[str, tuple[Any, ...]]:
    fixtures = _mapping(source.get("mock_protocol_fixtures"))
    offer_response = _mapping(fixtures.get("AirlineOfferResponseV01"))
    hold_packet = _mapping(fixtures.get("AirlineOfferHoldCommitPacketV01"))
    hold_receipt = _mapping(fixtures.get("AirlineOfferHoldReceiptV01"))
    approval = _mapping(fixtures.get("ClientPurchaseApprovalEvidenceV01"))
    bank_receipt = _mapping(fixtures.get("BankPaymentAuthorizationReceiptV01"))
    ticket_packet = _mapping(fixtures.get("AirlineTicketIssueCommitPacketV01"))
    ticket_receipt = _mapping(fixtures.get("MockTicketReceiptV01"))
    purchase_receipt = _mapping(fixtures.get("MockPurchaseReceiptV01"))
    return {
        "airline_offer_hold_phase": (
            offer_response.get("response_id"),
            hold_packet.get("packet_id"),
            hold_receipt.get("receipt_id"),
        ),
        "client_purchase_intent_phase": (
            approval.get("approval_id"),
            approval.get("client_purchase_intent_id"),
        ),
        "bank_payment_authorization_phase": (
            bank_receipt.get("payment_authorization_ref_id"),
        ),
        "airline_ticket_issue_phase": (
            ticket_packet.get("packet_id"),
            ticket_receipt.get("receipt_id"),
        ),
        "client_completion_phase": (
            purchase_receipt.get("receipt_id"),
        ),
    }


def _source_identity(source: Mapping[str, Any]) -> dict[str, Any]:
    identity = _mapping(source.get("transaction_identity"))
    return {
        "source_run_id": source.get("run_id"),
        "source_report_id": source.get("report_id"),
        "transaction_id": source.get("transaction_id"),
        "client_root_id": identity.get("client_root_id"),
        "airline_root_id": identity.get("airline_root_id"),
        "bank_root_id": identity.get("bank_root_id"),
        "mock_only": identity.get("mock_only"),
    }


def _business_scene(source: Mapping[str, Any]) -> dict[str, Any]:
    intent = _mapping(source.get("travel_intent"))
    summary = _mapping(source.get("final_tri_party_mock_summary"))
    return {
        "origin": intent.get("origin"),
        "destination": intent.get("destination"),
        "departure_date": intent.get("depart_date"),
        "return_date": intent.get("return_date"),
        "passengers_count": intent.get("passengers_count"),
        "cabin": intent.get("cabin"),
        "budget": f"{intent.get('max_price_amount')} {intent.get('currency')}",
        "user_goal": intent.get("user_goal"),
        "final_summary_id": summary.get("summary_id"),
    }


def _one_transaction_three_roots(source: Mapping[str, Any]) -> dict[str, Any]:
    identity = _mapping(source.get("transaction_identity"))
    fourth_root_created = _fourth_root_created(source)
    return {
        "transaction_id": source.get("transaction_id"),
        "client_root_id": identity.get("client_root_id"),
        "airline_root_id": identity.get("airline_root_id"),
        "bank_root_id": identity.get("bank_root_id"),
        "fourth_root_created": fourth_root_created,
        "mock_only": identity.get("mock_only"),
    }


def _semantic_to_contract_boundary() -> tuple[str, ...]:
    return (
        "Initial travel intent remains semantic/reasoning input.",
        "Root-owned contract artifacts drive the corridor.",
        "No post-Root LLM reasoning restarts inside a contract phase.",
        "Provider output does not mint packets, receipts, payment, ticket, booking, or authority.",
    )


def _root_centered_phase_story(source: Mapping[str, Any]) -> tuple[str, ...]:
    phase_ids = [
        phase.get("phase_id")
        for phase in _sequence(_mapping(source.get("airline_ticket_purchase_corridor_v0_1")).get("phase_results"))
    ]
    return (
        "The integrated corridor is five side-local Root loops, not one global Root approval.",
        "Phase order: " + " -> ".join(str(phase_id) for phase_id in phase_ids),
        "Failure would stop later phases and return to the relevant Root.",
    )


def _phase_cards(source: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    corridor = _mapping(source.get("airline_ticket_purchase_corridor_v0_1"))
    phases = tuple(_mapping(item) for item in _sequence(corridor.get("phase_results")))
    names = {
        "airline_offer_hold_phase": "AirlineRoot проверяет и разрешает удержание выбранного предложения",
        "client_purchase_intent_phase": "ClientRoot создаёт намерение покупки из scoped human approval evidence",
        "bank_payment_authorization_phase": "BankRoot подтверждает bounded mock-авторизацию платежа",
        "airline_ticket_issue_phase": "AirlineRoot разрешает mock-выпуск билета",
        "client_completion_phase": "ClientRoot наблюдает mock-завершение покупки",
    }
    entered = {
        "airline_offer_hold_phase": "selected offer facts and hold packet evidence",
        "client_purchase_intent_phase": "OfferHoldReceipt plus scoped human approval evidence",
        "bank_payment_authorization_phase": "ClientPurchaseIntent and bounded payment facts",
        "airline_ticket_issue_phase": "hold, client intent, and BankRoot authorization reference",
        "client_completion_phase": "mock ticket receipt, mock PNR, and purchase evidence",
    }
    authorized = {
        "airline_offer_hold_phase": "AirlineRoot authorized offer/hold scope",
        "client_purchase_intent_phase": "ClientRoot created ClientPurchaseIntent",
        "bank_payment_authorization_phase": "BankRoot owned the mock authorization reference",
        "airline_ticket_issue_phase": "AirlineRoot created ticket issue intent",
        "client_completion_phase": "ClientRoot observed completion status",
    }
    validated = {
        "airline_offer_hold_phase": "offer_id, hold_id, passenger_ref, route_ref, amount, currency, TTL",
        "client_purchase_intent_phase": "human approval scope, selected offer, hold receipt, passenger, amount, currency",
        "bank_payment_authorization_phase": "merchant_ref, amount, currency, hold, passenger, idempotency, expiry",
        "airline_ticket_issue_phase": "offer/hold/client/bank dependencies, passenger, route, amount, currency, merchant",
        "client_completion_phase": "mock purchase receipt lineage and evidence-only status",
    }
    possible = {
        "airline_offer_hold_phase": "ClientRoot purchase-intent review may start",
        "client_purchase_intent_phase": "BankRoot payment authorization review may start",
        "bank_payment_authorization_phase": "AirlineRoot ticket-issue review may start",
        "airline_ticket_issue_phase": "ClientRoot completion observation may start",
        "client_completion_phase": "side-specific completion status may be observed",
    }
    cards = []
    for phase in phases:
        phase_id = str(phase.get("phase_id"))
        cards.append(
            {
                "phase_index": phase.get("phase_index"),
                "phase_id": phase_id,
                "human_phase_name": names.get(phase_id, phase_id),
                "relevant_root_id": phase.get("relevant_root_id"),
                "phase_status": phase.get("phase_status"),
                "what_entered_the_phase": entered.get(phase_id, ""),
                "what_root_authorized": authorized.get(phase_id, ""),
                "what_domain_validated": validated.get(phase_id, ""),
                "what_universal_core_guarded": "deterministic-only corridor and no post-Root LLM reasoning restart",
                "evidence_returned": tuple(phase.get("evidence_refs_observed", ())),
                "what_became_possible_next": possible.get(phase_id, ""),
                "authority_transferred": phase.get("authority_transferred"),
                "runtime_receipt_created": phase.get("runtime_receipt_created"),
                "real_world_effects_count": phase.get("real_world_effects_count"),
            },
        )
    return tuple(cards)


def _transition_story(source: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    corridor = _mapping(source.get("airline_ticket_purchase_corridor_v0_1"))
    return tuple(_mapping(item) for item in _sequence(corridor.get("transitions")))


def _core_domain_delegation_story(source: Mapping[str, Any]) -> dict[str, Any]:
    matrix = tuple(
        _mapping(row)
        for row in _sequence(
            _mapping(source.get("airline_ticket_purchase_corridor_v0_1")).get(
                "core_domain_delegation_matrix",
            ),
        )
    )
    return {
        "required_sentence": CORE_DOMAIN_SENTENCE,
        "universal_core_guarded": (
            "deterministic-only contract corridor",
            "no post-Root LLM reasoning restart",
            "no authority expansion",
            "fail-closed return to the relevant Root",
        ),
        "airline_domain_validated": (
            "offer_id",
            "hold_id",
            "passenger_ref",
            "route_ref",
            "amount",
            "currency",
            "merchant_ref",
            "ticket / PNR dependencies",
            "domain Root ownership",
            "receipt evidence classification",
        ),
        "source_delegation_rows": len(matrix),
        "validated_source_rows": matrix,
        "not_every_airline_check_is_core": True,
    }


def _identity_lineage_story(source: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    fixtures = _mapping(source.get("mock_protocol_fixtures"))
    approval = _mapping(fixtures.get("ClientPurchaseApprovalEvidenceV01"))
    bank_receipt = _mapping(fixtures.get("BankPaymentAuthorizationReceiptV01"))
    purchase_receipt = _mapping(fixtures.get("MockPurchaseReceiptV01"))
    final_summary = _mapping(fixtures.get("ClientFinalTravelSummaryV01"))
    return (
        {
            "card": "Human approval",
            "artifact_id": approval.get("approval_id"),
            "meaning": "scoped evidence only",
            "creates_intent_by_itself": False,
        },
        {
            "card": "ClientPurchaseIntent",
            "artifact_id": approval.get("client_purchase_intent_id"),
            "created_by": CLIENT_ROOT_ID,
            "source_human_approval_ref": approval.get("approval_id"),
            "distinct_from_human_approval": approval.get("approval_id") != approval.get("client_purchase_intent_id"),
        },
        {
            "card": "Bank payment receipt",
            "artifact_id": bank_receipt.get("receipt_id"),
            "meaning": "evidence from Bank phase",
        },
        {
            "card": "BankPaymentAuthorizationRef",
            "artifact_id": bank_receipt.get("payment_authorization_ref_id"),
            "source_payment_receipt_id": bank_receipt.get("receipt_id"),
            "root_owner": BANK_ROOT_ID,
            "distinct_from_receipt": bank_receipt.get("receipt_id") != bank_receipt.get("payment_authorization_ref_id"),
        },
        {
            "card": "MockPurchaseReceipt",
            "artifact_id": purchase_receipt.get("receipt_id"),
            "evidence_only": purchase_receipt.get("evidence_only"),
        },
        {
            "card": "ClientFinalTravelSummary",
            "artifact_id": final_summary.get("summary_id"),
            "mock_purchase_receipt_id": final_summary.get("mock_purchase_receipt_id"),
            "distinct_from_receipt": final_summary.get("summary_id") != purchase_receipt.get("receipt_id"),
            "fourth_root_created": _fourth_root_created(source),
        },
    )


def _receipt_creator_story(source: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    fixtures = _mapping(source.get("mock_protocol_fixtures"))
    hold = _mapping(fixtures.get("AirlineOfferHoldReceiptV01"))
    ticket = _mapping(fixtures.get("MockTicketReceiptV01"))
    purchase = _mapping(fixtures.get("MockPurchaseReceiptV01"))
    return (
        {
            "receipt": "OfferHoldReceipt",
            "receipt_id": hold.get("receipt_id"),
            "root_authorization": "AirlineRoot authorizes the offer/hold phase",
            "created_by": hold.get("created_by"),
            "root_owner": hold.get("root_owner"),
            "evidence_only": hold.get("evidence_only"),
            "purchase_permission_created": hold.get("purchase_permission_created"),
            "payment_permission_created": hold.get("payment_permission_created"),
            "ticket_permission_created": hold.get("ticket_permission_created"),
            "future_permission_created": hold.get("future_permission_created"),
            "real_world_effects_count": hold.get("real_world_effects_count"),
        },
        {
            "receipt": "MockTicketReceipt",
            "receipt_id": ticket.get("receipt_id"),
            "root_authorization": "AirlineRoot authorizes ticket-issue intent",
            "created_by": ticket.get("created_by"),
            "root_owner": ticket.get("root_owner"),
            "evidence_only": ticket.get("evidence_only"),
            "future_ticket_permission_created": ticket.get("future_ticket_permission_created"),
            "future_payment_permission_created": ticket.get("future_payment_permission_created"),
            "real_ticket": ticket.get("real_ticket"),
            "real_booking": ticket.get("real_booking", ticket.get("real_travel_booking_created")),
            "real_world_effects_count": ticket.get("real_world_effects_count"),
        },
        {
            "receipt": "MockPurchaseReceipt",
            "receipt_id": purchase.get("receipt_id"),
            "root_authorization": "ClientRoot observes completion",
            "created_by": purchase.get("created_by"),
            "root_owner": purchase.get("root_owner"),
            "evidence_only": purchase.get("evidence_only"),
            "future_permission_created": purchase.get("future_permission_created"),
            "real_payment_executed": purchase.get("real_payment_executed"),
            "real_ticket_issued": purchase.get("real_ticket_issued"),
            "real_booking_created": purchase.get("real_booking_created"),
            "root_truth_rewritten": purchase.get("root_truth_rewritten"),
            "side_root_finals_replaced": purchase.get("side_root_finals_replaced"),
            "real_world_effects_count": purchase.get("real_world_effects_count"),
            "replaces_root_final_status": purchase.get("side_root_finals_replaced"),
        },
    )


def _binding_matrix_story(source: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "human_introduction": (
            "Эта таблица доказывает, что corridor не запустил вторую красивую "
            "тестовую сделку. Он получил значения из уже существующей "
            "Airline-транзакции и связал их с доменными контрактами."
        ),
        "rows": tuple(
            {
                "binding_id": row.get("binding_id"),
                "source_report_path": row.get("source_report_path"),
                "source_value": row.get("source_value"),
                "corridor_artifact_type": row.get("corridor_artifact_type"),
                "corridor_field": row.get("corridor_field"),
                "projected_value": row.get("projected_value"),
                "values_match": row.get("values_match"),
                "transaction_id": row.get("transaction_id"),
                "raw_secret_used": row.get("raw_secret_used"),
                "authority_transferred": row.get("authority_transferred"),
            }
            for row in _sequence(source.get("airline_ticket_purchase_corridor_binding_matrix"))
        ),
    }


def _evidence_crosses_authority_does_not_story(source: Mapping[str, Any]) -> tuple[str, ...]:
    rows = _sequence(source.get("cross_root_evidence_routing_matrix"))
    return tuple(
        f"{row.get('source_root_id')} -> {row.get('target_root_id')}: {row.get('artifact')}; authority_transferred={row.get('authority_transferred')}"
        for row in rows
    )


def _fail_closed_story() -> tuple[str, ...]:
    return (
        "wrong transaction id",
        "wrong Root",
        "missing hold",
        "intent before hold",
        "missing human approval",
        "missing Bank authorization",
        "passenger mismatch",
        "route mismatch",
        "amount mismatch",
        "currency mismatch",
        "merchant mismatch",
        "expired hold",
        "expired payment authorization",
        "receipt permission claim",
        "cross-Root authority transfer",
        "post-Root reasoning restart",
        "nonzero real effect",
    )


def _mock_happy_path(source: Mapping[str, Any]) -> tuple[str, ...]:
    fixtures = _mapping(source.get("mock_protocol_fixtures"))
    ticket = _mapping(fixtures.get("MockTicketReceiptV01"))
    return (
        "selected offer",
        "→ mock hold evidence",
        "→ ClientRoot purchase intent",
        "→ BankRoot mock authorization reference",
        "→ AirlineRoot ticket issue intent",
        "→ mock ticket receipt",
        f"→ mock PNR {ticket.get('mock_pnr')}",
        "→ mock purchase receipt",
        "→ ClientRoot completion status",
        "This is mock fulfilment evidence.",
        "No real payment was settled.",
        "No real airline ticket was issued.",
        "No real booking was created.",
        "No external API was called.",
    )


def _root_boundary_story(source: Mapping[str, Any]) -> tuple[str, ...]:
    return tuple(
        f"{row.get('boundary')}: preserved={row.get('boundary_preserved')}; violations={row.get('violation_count')}"
        for row in _sequence(source.get("root_boundary_matrix"))
    )


def _fourth_root_created(source: Mapping[str, Any]) -> bool:
    participants = _mapping(source.get("participants"))
    if set(participants) != {"ClientRoot", "AirlineRoot", "BankRoot"}:
        return True
    corridor = _mapping(source.get("airline_ticket_purchase_corridor_v0_1"))
    counters = _mapping(corridor.get("counter_table"))
    if counters.get("shared_root_created_count", 0) != 0:
        return True
    if counters.get("fourth_root_created_count", 0) != 0:
        return True
    for row in _sequence(source.get("root_boundary_matrix")):
        boundary = _mapping(row)
        if boundary.get("boundary_preserved") is not True:
            return True
        if boundary.get("violation_count") != 0:
            return True
    return False


def _counter_table(
    source: Mapping[str, Any],
    phase_cards: tuple[dict[str, Any], ...],
    identity_cards: tuple[dict[str, Any], ...],
    receipt_cards: tuple[dict[str, Any], ...],
) -> dict[str, int]:
    counters = _mapping(source.get("counter_table"))
    binding_rows = _sequence(source.get("airline_ticket_purchase_corridor_binding_matrix"))
    integration = _mapping(source.get("airline_ticket_purchase_corridor_integration"))
    return {
        "source_corridor_integration_count": int(counters.get("airline_ticket_purchase_corridor_integration_count", 0)),
        "source_corridor_pass_count": int(counters.get("airline_ticket_purchase_corridor_pass_count", 0)),
        "source_phase_count": int(counters.get("airline_ticket_purchase_corridor_phase_count", 0)),
        "source_phase_pass_count": int(counters.get("airline_ticket_purchase_corridor_phase_pass_count", 0)),
        "source_transition_count": int(counters.get("airline_ticket_purchase_corridor_transition_count", 0)),
        "source_transition_pass_count": int(counters.get("airline_ticket_purchase_corridor_transition_pass_count", 0)),
        "source_binding_row_count": len(binding_rows),
        "source_binding_match_count": sum(1 for row in binding_rows if row.get("values_match") is True),
        "source_unique_transaction_id_count": int(integration.get("unique_transaction_id_count", 0)),
        "source_fixture_receipts_observed_count": int(counters.get("airline_ticket_purchase_corridor_fixture_receipts_observed_count", 0)),
        "source_runtime_receipts_created_count": int(counters.get("airline_ticket_purchase_corridor_runtime_receipts_created_count", 0)),
        "source_runtime_packets_created_count": int(counters.get("airline_ticket_purchase_corridor_runtime_packets_created_count", 0)),
        "source_adapter_execution_count": int(counters.get("airline_ticket_purchase_corridor_adapter_execution_count", 0)),
        "source_duplicate_execution_count": int(counters.get("airline_ticket_purchase_corridor_duplicate_execution_count", 0)),
        "source_parallel_transaction_count": int(counters.get("airline_ticket_purchase_corridor_parallel_transaction_count", 0)),
        "source_cross_root_authority_transfer_count": int(counters.get("airline_ticket_purchase_corridor_cross_root_authority_transfer_count", 0)),
        "source_provider_called_count": int(counters.get("provider_called_count", 0)),
        "source_network_used_count": int(counters.get("network_used_count", 0)),
        "source_gemini_called_count": int(counters.get("gemini_called_count", 0)),
        "source_real_world_effects_count": int(counters.get("real_world_effects_count", 0)),
        "human_story_created_count": 1,
        "phase_cards_created_count": len(phase_cards),
        "identity_lineage_cards_created_count": len(identity_cards),
        "receipt_creator_cards_created_count": len(receipt_cards),
        "binding_rows_rendered_count": len(binding_rows),
        "renderer_source_json_read_count": 1,
        "renderer_corridor_execution_count": 0,
        "renderer_provider_called_count": 0,
        "renderer_network_used_count": 0,
        "renderer_gemini_called_count": 0,
        "renderer_packet_created_count": 0,
        "renderer_receipt_created_count": 0,
        "renderer_payment_created_count": 0,
        "renderer_ticket_created_count": 0,
        "renderer_booking_created_count": 0,
        "renderer_real_world_effects_count": 0,
    }


def _non_claims() -> tuple[str, ...]:
    return (
        "not production",
        "not a real airline booking system",
        "not a real payment system",
        "no live semantic rerun",
        "no deterministic corridor rerun by renderer",
        "no provider/network/Gemini call",
        "no config/API key access",
        "no real airline API",
        "no real bank API",
        "no real GDS/NDC/ONE Order call",
        "no real payment",
        "no real ticket",
        "no real booking",
        "no Transaction Artifact Ledger implementation",
        "no Crypto Artifact Seal implementation",
        "no Sealed Trace Replay Verifier implementation",
        "not public auditor final package",
    )


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> tuple[Any, ...]:
    if isinstance(value, (list, tuple)):
        return tuple(value)
    return ()


def _counter_value(
    counters: Mapping[str, Any],
    key: str,
    aliases: tuple[str, ...],
) -> Any:
    if key in counters:
        return counters.get(key)
    for alias in aliases:
        if alias in counters:
            return counters.get(alias)
    return 0


def _format_mapping(value: Mapping[str, Any]) -> str:
    return "\n".join(f"{key}: {value[key]}" for key in value)


def _format_lines(value: Any) -> str:
    return "\n".join(f"- {item}" for item in _sequence(value))


if __name__ == "__main__":
    raise SystemExit(main())
