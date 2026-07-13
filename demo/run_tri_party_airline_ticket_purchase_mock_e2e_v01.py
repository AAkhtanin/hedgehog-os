from __future__ import annotations

from collections.abc import Mapping as MappingABC
from dataclasses import fields, is_dataclass, replace
from typing import Any, Mapping

from hedgehog.domains.airline import semantic_to_contract_causal_runtime_v01 as causal_runtime
from hedgehog.domains.airline import ticket_purchase_corridor_runtime_v01 as corridor_runtime
from hedgehog.domains.airline import ticket_purchase_corridor_v01 as corridor_contracts
from hedgehog.domains.airline import (
    transaction_artifact_ledger_collector_v01 as ledger_collector,
)
from hedgehog.domains.airline import transaction_artifact_ledger_v01 as ledger_contracts


RUN_ID = "tri_party_airline_ticket_purchase_mock_e2e_v01"
REPORT_ID = "tri_party_airline_ticket_purchase_mock_e2e_v01"
SLICE_ID = "tri_party_airline_ticket_purchase_mock_e2e_v01_slice_g"
TRANSACTION_ID = "tri_airline_purchase:PAR-LIM:2026-08-12:client_001"

STATUS_PASS = "PASS"
STATUS_FAIL_CLOSED = "FAIL_CLOSED"

REASON_ACTUAL_LEDGER_ENTRY_COUNT_MISMATCH = "actual_ledger_entry_count_mismatch"
REASON_ACTUAL_LEDGER_DEPENDENCY_EDGE_MISMATCH = (
    "actual_ledger_dependency_edge_count_mismatch"
)
REASON_ACTUAL_LEDGER_ROOT_FINAL_MISMATCH = "actual_ledger_root_final_count_mismatch"
REASON_LEDGER_STORED_ACTUAL_DERIVED_FIELD_MISMATCH = (
    "ledger_stored_actual_derived_field_mismatch"
)
REASON_LEDGER_ARTIFACT_TYPE_SEQUENCE_MISMATCH = (
    "actual_ledger_artifact_type_sequence_mismatch"
)
REASON_LEDGER_ROOT_FINAL_SET_MISMATCH = "actual_ledger_root_final_set_mismatch"
REASON_LEDGER_PUBLIC_TYPED_VIEW_MISMATCH = "ledger_public_typed_view_mismatch"
REASON_PRECOLLECTED_CAUSAL_BSEP_PROJECTIONS_REQUIRED = (
    "precollected_causal_bsep_projections_required"
)

CLIENT_ROOT_ID = "root:client_os_001"
AIRLINE_ROOT_ID = "root:mock_airline_al"
BANK_ROOT_ID = "root:mock_bank_a"

REQUIRED_SECTIONS = (
    "[TRI-PARTY AIRLINE TICKET PURCHASE MOCK E2E V0.1]",
    "[WHAT THIS SLICE IS]",
    "[ONE TRANSACTION / THREE ROOTS]",
    "[CLIENT ROOT VIEW]",
    "[AIRLINE ROOT VIEW]",
    "[BANK ROOT VIEW]",
    "[AIRLINEROOT OFFER HOLD SANDBOX]",
    "[BANKROOT PAYMENT AUTHORIZATION SANDBOX]",
    "[CLIENTROOT PURCHASE ORCHESTRATION]",
    "[AIRLINEROOT TICKET ISSUE MOCK CORRIDOR]",
    "[INTEGRATED TRI-PARTY TRANSACTION TRACE]",
    "[CROSS-ROOT EVIDENCE ROUTING MATRIX]",
    "[FINAL TRI-PARTY MOCK SUMMARY]",
    "[AIRLINE TICKET/PURCHASE CORRIDOR V0.1 ROOT-CENTERED INTEGRATION]",
    "[AIRLINE TRANSACTION ARTIFACT LEDGER V0.1]",
    "[MOCK PROTOCOL FIXTURES]",
    "[SHARED TRANSACTION LEDGER]",
    "[ROOT BOUNDARY MATRIX]",
    "[RECEIPT BOUNDARY MATRIX]",
    "[PRIVACY / SEALED REF BOUNDARY]",
    "[NON-ACTION REUSE CONSTRAINTS]",
    "[FUTURE SEMANTIC ACTOR TOPOLOGY]",
    "[FUTURE VERTICAL FRACTAL MAP]",
    "[COUNTER TABLE]",
    "[NON-CLAIMS]",
    "[NEXT GATE]",
    "[FINAL STATUS]",
)


def build_tri_party_airline_semantic_source_context_v01() -> dict[str, Any]:
    snapshot = causal_runtime.binding.build_airline_candidate_snapshot_v01()
    return {
        "run_id": "tri_party_airline_semantic_source_context_v01",
        "report_id": "tri_party_airline_semantic_source_context_v01",
        "final_status": STATUS_PASS,
        "transaction_id": TRANSACTION_ID,
        "transaction_identity": _transaction_identity(),
        "participants": _participants(),
        "travel_intent": _travel_intent(),
        "sealed_refs": _sealed_refs(),
        "bounded_offer_candidates": tuple(
            {
                "offer_id": record.offer_id,
                "amount": record.amount,
                "currency": record.currency,
                "route_ref": record.route_ref,
                "baggage_included": record.baggage_included,
                "seat_characteristics": record.seat_characteristics,
                "changeable": record.changeable,
                "overnight_layover": record.overnight_layover,
                "ttl_seconds": record.ttl_seconds,
                "inventory_available": record.inventory_available,
                "airline_policy_valid": record.airline_policy_valid,
            }
            for record in snapshot.authoritative_offer_records
        ),
        "candidate_set_snapshot_id": snapshot.candidate_set_snapshot_id,
        "candidate_set_digest": snapshot.candidate_set_digest,
        "selected_offer_id": "",
        "corridor_executed": False,
        "receipts_created": 0,
        "real_world_effects_count": 0,
    }


def _validate_semantic_causal_run_for_deterministic(
    semantic_causal_run: causal_runtime.AirlineSemanticCausalRunReportV01 | None,
) -> tuple[str, ...]:
    if semantic_causal_run is None:
        return ()
    accepted, reasons = causal_runtime.validate_airline_semantic_causal_run_report_v01(
        semantic_causal_run,
    )
    errors = list(reasons)
    if not accepted:
        errors.append("semantic_causal_run_validation_rejected")
    if semantic_causal_run.final_status != causal_runtime.STATUS_LOCAL_MODEL_PASS:
        errors.append("semantic_causal_run_validation_rejected")
        errors.append("semantic_causal_run_not_local_model_pass")
    if not (
        semantic_causal_run.semantic_recommendation_id
        and semantic_causal_run.semantic_recommendation_id
        == semantic_causal_run.root_selected_offer_id
        == semantic_causal_run.hold_contract_offer_id
    ):
        errors.append("semantic_causal_offer_chain_mismatch")
    if (
        semantic_causal_run.default_offer_used
        or semantic_causal_run.silent_fallback_used
        or semantic_causal_run.provider_created_authority_count != 0
        or semantic_causal_run.provider_created_contract_count != 0
        or semantic_causal_run.real_world_effects_count != 0
    ):
        errors.append("semantic_causal_safety_boundary_rejected")
    if (
        semantic_causal_run.airline_root_resolution is None
        or semantic_causal_run.hold_packet is None
    ):
        errors.append("semantic_causal_missing_resolution_or_hold")
    return tuple(dict.fromkeys(errors))


def _semantic_causal_fail_closed_report(
    semantic_causal_run: causal_runtime.AirlineSemanticCausalRunReportV01 | None,
    errors: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "run_id": RUN_ID,
        "report_id": REPORT_ID,
        "slice_id": SLICE_ID,
        "final_status": STATUS_FAIL_CLOSED,
        "transaction_id": TRANSACTION_ID,
        "transaction_identity": _transaction_identity(),
        "participants": _participants(),
        "travel_intent": _travel_intent(),
        "sealed_refs": _sealed_refs(),
        "semantic_to_contract_causal_source": _semantic_causal_source_summary(
            semantic_causal_run,
        ),
        "counter_table": {
            "deterministic_airline_collection_count": 0,
            "deterministic_bsep_source_creation_count": 0,
            "local_injected_semantic_callback_count": 0,
            "provider_network_call_count": 0,
            "gemini_call_count": 0,
            "ticket_purchase_corridor_execution_count": 0,
            "default_offer_count": 0,
            "silent_fallback_count": 0,
            "provider_created_authority_count": 0,
            "real_world_effects_count": 0,
        },
        "validation_errors": errors,
        "next_gate": "airline_semantic_to_contract_causal_run_required",
    }


def _semantic_causal_source_summary(
    semantic_causal_run: causal_runtime.AirlineSemanticCausalRunReportV01 | None,
) -> dict[str, Any]:
    if semantic_causal_run is None:
        return {
            "semantic_causal_run_supplied": False,
            "causal_report_validation_accepted": False,
            "direct_offer_override_used": False,
            "default_offer_used": False,
            "silent_fallback_used": False,
            "real_world_effects_count": 0,
        }
    accepted, reasons = causal_runtime.validate_airline_semantic_causal_run_report_v01(
        semantic_causal_run,
    )
    return {
        "semantic_causal_run_supplied": True,
        "causal_report_validation_accepted": accepted,
        "causal_report_validation_errors": reasons,
        "semantic_recommendation_id": semantic_causal_run.semantic_recommendation_id,
        "client_root_selected_offer_id": semantic_causal_run.root_selected_offer_id,
        "airline_root_resolved_offer_id": (
            semantic_causal_run.airline_root_resolution.selected_offer_id
            if semantic_causal_run.airline_root_resolution is not None
            else ""
        ),
        "hold_contract_offer_id": semantic_causal_run.hold_contract_offer_id,
        "direct_offer_override_used": False,
        "default_offer_used": semantic_causal_run.default_offer_used,
        "silent_fallback_used": semantic_causal_run.silent_fallback_used,
        "provider_created_authority_count": (
            semantic_causal_run.provider_created_authority_count
        ),
        "real_world_effects_count": semantic_causal_run.real_world_effects_count,
    }


def _deterministic_semantic_proposal_payload(
    request: Mapping[str, Any],
    offer_id: str,
) -> dict[str, Any]:
    return {
        "proposal_id": f"semantic_offer_selection_proposal:{offer_id}",
        "transaction_id": request["transaction_id"],
        "actor_id": request["actor_id"],
        "source_selection_input_id": request["source_selection_input_id"],
        "source_bsep_projection_ref": request["source_bsep_projection_ref"],
        "source_client_constraint_set_id": request["source_client_constraint_set_id"],
        "source_candidate_set_snapshot_id": request[
            "source_candidate_set_snapshot_id"
        ],
        "source_candidate_set_digest": request["source_candidate_set_digest"],
        "candidate_set_ref": request["source_candidate_set_ref"],
        "recommended_offer_id": offer_id,
        "ranked_offer_ids": (offer_id,),
        "decision_factors": ("deterministic_airline_semantic_offer_match",),
        "preference_matches": ("client_preferences_satisfied",),
        "uncertainty_notes": ("requires_client_root_review",),
        "requires_root_review": True,
        "semantic_summary": "Deterministic local advisory semantics.",
        "authority_created": False,
        "action_permission_created": False,
        "packet_created": False,
        "receipt_created": False,
        "payment_created": False,
        "ticket_created": False,
        "booking_created": False,
        "final_output_created": False,
        "real_world_effects_count": 0,
    }


def _deterministic_semantic_reviewer_payload(
    request: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "response_id": (
            f"canonical_actor_output:{request['actor_id']}:"
            f"{request['proposed_offer_id']}"
        ),
        "transaction_id": request["transaction_id"],
        "actor_id": request["actor_id"],
        "source_request_id": request["request_id"],
        "source_selection_input_id": request["source_selection_input_id"],
        "source_candidate_set_snapshot_id": request[
            "source_candidate_set_snapshot_id"
        ],
        "source_candidate_set_digest": request["source_candidate_set_digest"],
        "reviewed_offer_id": request["proposed_offer_id"],
        "review_role": request["actor_role"],
        "review_status": causal_runtime.binding.STATUS_PASS,
        "semantic_factors": ("review_supports_explicit_offer",),
        "blocking_conflicts": (),
        "supports_proposed_offer": True,
        "validation_status": causal_runtime.binding.STATUS_PASS,
        "raw_output_used": False,
        "authority_created": False,
        "permission_created": False,
        "real_world_effects_count": 0,
    }


def _deterministic_semantic_provider_for_offer(
    offer_id: str,
) -> causal_runtime.AirlineInjectedSemanticProviderV01:
    def provider(actor_id: str, request: Mapping[str, Any]) -> Mapping[str, Any]:
        if actor_id == causal_runtime.binding.ACTOR_CLIENT_PURCHASE_INTENT_REVIEWER:
            return _deterministic_semantic_proposal_payload(request, offer_id)
        return _deterministic_semantic_reviewer_payload(request)

    return provider


def _build_deterministic_bsep_source_context_v01(
    *,
    scenario_id: str,
) -> dict[str, ledger_collector.AirlineTransactionArtifactLedgerBSEPProjectionSourceV01]:
    packet_id = f"bsep_packet:{RUN_ID}:{scenario_id}"

    def projection(
        *,
        projection_id: str,
        projection_ref: str,
        side: str,
    ) -> ledger_collector.AirlineTransactionArtifactLedgerBSEPProjectionSourceV01:
        return ledger_collector.AirlineTransactionArtifactLedgerBSEPProjectionSourceV01(
            projection_id=projection_id,
            projection_ref=projection_ref,
            bsep_packet_id=packet_id,
            transaction_id=TRANSACTION_ID,
            side=side,
            validation_status=ledger_contracts.STATUS_PASS,
            raw_secrets_included=False,
            raw_provider_text_included=False,
            authority_created=False,
            permission_created=False,
            real_world_effects_count=0,
        )

    return {
        "client_bsep_projection": projection(
            projection_id="client_bsep_projection:deterministic_airline:001",
            projection_ref="client_bsep_projection:deterministic_airline:001",
            side=ledger_collector.SIDE_CLIENT,
        ),
        "airline_bsep_projection": projection(
            projection_id="airline_bsep_projection:deterministic_airline:001",
            projection_ref=causal_runtime.binding.BSEP_PROJECTION_REF,
            side=ledger_collector.SIDE_AIRLINE,
        ),
        "bank_bsep_projection": projection(
            projection_id="bank_bsep_projection:deterministic_airline:001",
            projection_ref="bank_bsep_projection:deterministic_airline:001",
            side=ledger_collector.SIDE_BANK,
        ),
        "cross_root_bsep_projection": projection(
            projection_id="cross_root_bsep_projection:deterministic_airline:001",
            projection_ref="cross_root_bsep_projection:deterministic_airline:001",
            side=ledger_collector.SIDE_CROSS_ROOT_ADVISORY,
        ),
    }


def _typed_airline_bsep_projection_from_source_v01(
    source: ledger_collector.AirlineTransactionArtifactLedgerBSEPProjectionSourceV01,
) -> causal_runtime.binding.AirlineBSEPProjectionRefV01:
    return causal_runtime.binding.AirlineBSEPProjectionRefV01(
        projection_ref=source.projection_ref,
        transaction_id=source.transaction_id,
        projection_side="airline_offer_selection",
        validation_status=source.validation_status,
        raw_secret_included=source.raw_secrets_included,
        authority_created=source.authority_created,
        real_world_effects_count=source.real_world_effects_count,
    )


def _collect_default_semantic_causal_run_v01(
    *,
    bsep_projection: causal_runtime.binding.AirlineBSEPProjectionRefV01,
) -> tuple[causal_runtime.AirlineSemanticCausalRunReportV01, int]:
    constraints = causal_runtime.binding.build_client_constraints_preference_a_v01()
    callback_count = {"value": 0}
    provider = _deterministic_semantic_provider_for_offer(
        causal_runtime.binding.OFFER_A_ID,
    )

    def counting_provider(
        actor_id: str,
        request: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        callback_count["value"] += 1
        return provider(actor_id, request)

    return causal_runtime.collect_airline_semantic_to_contract_causal_run_v01(
        scenario_id=f"{RUN_ID}:deterministic_semantic_causal_run",
        constraints=constraints,
        semantic_provider=counting_provider,
        bsep_projection=bsep_projection,
    ), callback_count["value"]


def collect_tri_party_airline_ticket_purchase_mock_e2e_v01(
    *,
    semantic_causal_run: causal_runtime.AirlineSemanticCausalRunReportV01 | None = None,
    bsep_side_projections: Mapping[str, Any] | None = None,
    ledger_source_bundle_id: str | None = None,
) -> dict[str, Any]:
    deterministic_bsep_source_creation_count = 0
    local_injected_semantic_callback_count = 0
    if semantic_causal_run is None:
        scenario_id = f"{RUN_ID}:deterministic_semantic_causal_run"
        bsep_sources_for_ledger = _build_deterministic_bsep_source_context_v01(
            scenario_id=scenario_id,
        )
        deterministic_bsep_source_creation_count = 1
        actual_semantic_causal_run, local_injected_semantic_callback_count = (
            _collect_default_semantic_causal_run_v01(
                bsep_projection=_typed_airline_bsep_projection_from_source_v01(
                    bsep_sources_for_ledger["airline_bsep_projection"],
                ),
            )
        )
    else:
        actual_semantic_causal_run = semantic_causal_run
        if bsep_side_projections is None:
            return _semantic_causal_fail_closed_report(
                actual_semantic_causal_run,
                (REASON_PRECOLLECTED_CAUSAL_BSEP_PROJECTIONS_REQUIRED,),
            )
        bsep_sources_for_ledger = bsep_side_projections
    causal_validation_errors = _validate_semantic_causal_run_for_deterministic(
        actual_semantic_causal_run,
    )
    if causal_validation_errors:
        return _semantic_causal_fail_closed_report(
            actual_semantic_causal_run,
            causal_validation_errors,
        )

    transaction_identity = _transaction_identity()
    participants = _participants()
    travel_intent = _travel_intent()
    sealed_refs = _sealed_refs()
    mock_protocol_fixtures = _mock_protocol_fixtures(
        travel_intent,
        sealed_refs,
        semantic_causal_run=actual_semantic_causal_run,
    )
    airline_offer_hold_sandbox = _airline_offer_hold_sandbox(mock_protocol_fixtures)
    bank_payment_authorization_sandbox = _bank_payment_authorization_sandbox(
        mock_protocol_fixtures,
        sealed_refs,
    )
    client_purchase_orchestration = _client_purchase_orchestration(
        travel_intent,
        sealed_refs,
        mock_protocol_fixtures,
    )
    airline_ticket_issue_mock_corridor = _airline_ticket_issue_mock_corridor(
        mock_protocol_fixtures,
    )
    shared_transaction_ledger = _shared_transaction_ledger(mock_protocol_fixtures)
    integrated_transaction_trace = _integrated_transaction_trace(
        mock_protocol_fixtures,
    )
    cross_root_evidence_routing_matrix = _cross_root_evidence_routing_matrix()
    final_tri_party_mock_summary = _final_tri_party_mock_summary(
        mock_protocol_fixtures,
    )
    future_semantic_actor_topology = _future_semantic_actor_topology()
    future_vertical_fractal_map = _future_vertical_fractal_map()
    privacy_boundary_matrix = _privacy_boundary_matrix()
    root_boundary_matrix = _root_boundary_matrix()
    receipt_boundary_matrix = _receipt_boundary_matrix()
    source_report_for_corridor: dict[str, Any] = {
        "transaction_id": TRANSACTION_ID,
        "transaction_identity": transaction_identity,
        "travel_intent": travel_intent,
        "sealed_refs": sealed_refs,
        "mock_protocol_fixtures": mock_protocol_fixtures,
        "airline_offer_hold_sandbox": airline_offer_hold_sandbox,
        "bank_payment_authorization_sandbox": bank_payment_authorization_sandbox,
        "client_purchase_orchestration": client_purchase_orchestration,
        "airline_ticket_issue_mock_corridor": airline_ticket_issue_mock_corridor,
        "cross_root_evidence_routing_matrix": cross_root_evidence_routing_matrix,
        "root_boundary_matrix": root_boundary_matrix,
        "final_tri_party_mock_summary": final_tri_party_mock_summary,
    }
    corridor_contract_context = (
        corridor_contracts
        .build_airline_ticket_purchase_contract_context_from_resolution_v01(
            resolution=actual_semantic_causal_run.airline_root_resolution,
            hold_packet=actual_semantic_causal_run.hold_packet,
        )
    )
    corridor_fixture_bundle = (
        _build_airline_ticket_purchase_corridor_fixture_bundle_v01(
            source_report_for_corridor,
        )
    )
    corridor_collector_invocation_count = 0
    corridor_collector_invocation_count += 1
    corridor_execution_result = (
        corridor_runtime.collect_airline_ticket_purchase_corridor_execution_result_v01(
            fixtures=corridor_fixture_bundle,
            contract_context=corridor_contract_context,
        )
    )
    airline_ticket_purchase_corridor_v0_1 = corridor_execution_result.report
    corridor_public_validation_accepted, corridor_public_validation_errors = (
        corridor_runtime.validate_airline_ticket_purchase_corridor_run_v01(
            airline_ticket_purchase_corridor_v0_1,
        )
    )
    airline_ticket_purchase_corridor_binding_matrix = (
        _airline_ticket_purchase_corridor_binding_matrix_v01(
            source_report_for_corridor,
            corridor_fixture_bundle,
            airline_ticket_purchase_corridor_v0_1,
        )
    )
    airline_ticket_purchase_corridor_integration = (
        _airline_ticket_purchase_corridor_integration_summary(
            source_report_for_corridor,
            corridor_fixture_bundle,
            airline_ticket_purchase_corridor_v0_1,
            corridor_public_validation_accepted,
            airline_ticket_purchase_corridor_binding_matrix,
            corridor_collector_invocation_count,
            contract_context=corridor_contract_context,
        )
    )
    source_bundle_id = (
        ledger_source_bundle_id
        or f"{RUN_ID}:{REPORT_ID}:{actual_semantic_causal_run.scenario_id}"
    )
    (
        airline_transaction_artifact_ledger_source_bundle,
        airline_transaction_artifact_ledger_source_validation,
        airline_transaction_artifact_ledger_v0_1,
        airline_transaction_artifact_ledger_integration,
    ) = _collect_airline_transaction_artifact_ledger_integration_v01(
        semantic_causal_run=actual_semantic_causal_run,
        bsep_side_projections=bsep_sources_for_ledger,
        corridor_execution_result=corridor_execution_result,
        source_bundle_id=source_bundle_id,
        corridor_execution_count=corridor_collector_invocation_count,
    )
    counter_table = _counter_table(
        shared_transaction_ledger,
        future_semantic_actor_topology,
        future_vertical_fractal_map,
        airline_offer_hold_sandbox,
        bank_payment_authorization_sandbox,
        client_purchase_orchestration,
        airline_ticket_issue_mock_corridor,
        integrated_transaction_trace,
        cross_root_evidence_routing_matrix,
        final_tri_party_mock_summary,
        airline_ticket_purchase_corridor_v0_1,
        airline_ticket_purchase_corridor_binding_matrix,
        airline_ticket_purchase_corridor_integration,
        airline_transaction_artifact_ledger_integration,
        deterministic_bsep_source_creation_count,
        local_injected_semantic_callback_count,
    )

    report: dict[str, Any] = {
        "run_id": RUN_ID,
        "report_id": REPORT_ID,
        "slice_id": SLICE_ID,
        "final_status": STATUS_PASS,
        "transaction_id": TRANSACTION_ID,
        "transaction_identity": transaction_identity,
        "participants": participants,
        "travel_intent": travel_intent,
        "sealed_refs": sealed_refs,
        "client_root_view": _client_root_view(participants, mock_protocol_fixtures),
        "airline_root_view": _airline_root_view(participants, mock_protocol_fixtures),
        "bank_root_view": _bank_root_view(participants, mock_protocol_fixtures),
        "airline_offer_hold_sandbox": airline_offer_hold_sandbox,
        "bank_payment_authorization_sandbox": bank_payment_authorization_sandbox,
        "client_purchase_orchestration": client_purchase_orchestration,
        "airline_ticket_issue_mock_corridor": airline_ticket_issue_mock_corridor,
        "integrated_transaction_trace": integrated_transaction_trace,
        "cross_root_evidence_routing_matrix": cross_root_evidence_routing_matrix,
        "final_tri_party_mock_summary": final_tri_party_mock_summary,
        "airline_ticket_purchase_corridor_v0_1": airline_ticket_purchase_corridor_v0_1,
        "airline_ticket_purchase_corridor_binding_matrix": (
            airline_ticket_purchase_corridor_binding_matrix
        ),
        "airline_ticket_purchase_corridor_integration": (
            airline_ticket_purchase_corridor_integration
        ),
        "airline_transaction_artifact_ledger_source_bundle_v0_1": (
            airline_transaction_artifact_ledger_source_bundle
        ),
        "airline_transaction_artifact_ledger_source_validation_v0_1": (
            airline_transaction_artifact_ledger_source_validation
        ),
        "airline_transaction_artifact_ledger_v0_1": (
            airline_transaction_artifact_ledger_v0_1
        ),
        "airline_transaction_artifact_ledger_integration": (
            airline_transaction_artifact_ledger_integration
        ),
        "mock_protocol_fixtures": mock_protocol_fixtures,
        "shared_transaction_ledger": shared_transaction_ledger,
        "root_boundary_matrix": root_boundary_matrix,
        "receipt_boundary_matrix": receipt_boundary_matrix,
        "privacy_boundary_matrix": privacy_boundary_matrix,
        "non_action_reuse_constraints": _non_action_reuse_constraints(),
        "future_semantic_actor_topology": future_semantic_actor_topology,
        "future_vertical_fractal_map": future_vertical_fractal_map,
        "counter_table": counter_table,
        "semantic_to_contract_causal_source": _semantic_causal_source_summary(
            actual_semantic_causal_run,
        ),
        "non_claims": _non_claims(),
        "validation_errors": (),
        "next_gate": "airline_ticket_purchase_corridor_v01_slice_e_audit_and_human_story",
    }
    if not corridor_public_validation_accepted:
        report["validation_errors"] = tuple(corridor_public_validation_errors)
    errors = _validate_report(report)
    if errors:
        report["final_status"] = STATUS_FAIL_CLOSED
        report["validation_errors"] = errors
    return _publish_report_with_typed_ledger_objects(
        report,
        source_bundle=airline_transaction_artifact_ledger_source_bundle,
        source_validation_report=airline_transaction_artifact_ledger_source_validation,
        artifact_ledger=airline_transaction_artifact_ledger_v0_1,
    )


def render_tri_party_airline_ticket_purchase_mock_e2e_v01(
    report: Mapping[str, Any],
) -> str:
    lines: list[str] = [
        "[TRI-PARTY AIRLINE TICKET PURCHASE MOCK E2E V0.1]",
        f"run_id: {report['run_id']}",
        f"report_id: {report['report_id']}",
        f"slice_id: {report['slice_id']}",
        "",
        "[WHAT THIS SLICE IS]",
        (
            "This slice creates one mock airline purchase transaction skeleton, "
            "not three unrelated demos."
        ),
        "The fixtures look like real airline/payment protocol phases but are mock-only.",
        "",
        "[ONE TRANSACTION / THREE ROOTS]",
        f"transaction_id: {report['transaction_id']}",
        "ClientRoot, AirlineRoot, and BankRoot each see a bounded view of the same transaction.",
        "",
        "[CLIENT ROOT VIEW]",
        _format_view(report["client_root_view"]),
        "",
        "[AIRLINE ROOT VIEW]",
        _format_view(report["airline_root_view"]),
        "",
        "[BANK ROOT VIEW]",
        _format_view(report["bank_root_view"]),
        "",
        "[AIRLINEROOT OFFER HOLD SANDBOX]",
        "AirlineRoot received offer request.",
        "AirlineRoot checked mock inventory.",
        "AirlineRoot checked mock fare.",
        "AirlineRoot checked baggage rule.",
        "AirlineRoot checked offer TTL.",
        "AirlineRoot created OfferResponse.",
        "AirlineRoot created AirlineOfferHoldCommitPacket.",
        "AirlineRoot authorized the offer/hold contract phase.",
        "Airline hold sandbox produced OfferHoldReceipt evidence.",
        "OfferHoldReceipt is evidence only.",
        "OfferHoldReceipt is not payment permission.",
        "OfferHoldReceipt is not ticket permission.",
        "No real airline API was called.",
        "No real booking was created.",
        f"sandbox_status: {report['airline_offer_hold_sandbox']['sandbox_status']}",
        "",
        "[BANKROOT PAYMENT AUTHORIZATION SANDBOX]",
        "BankRoot received mock payment authorization request.",
        "BankRoot validated selected offer amount/currency against OfferHoldReceipt.",
        "BankRoot validated merchant/airline ref.",
        "BankRoot validated payment token sealed ref.",
        "BankRoot validated debtor slot ref.",
        "BankRoot validated idempotency.",
        "BankRoot validated expiry/TTL.",
        "BankRoot created BankPaymentIntent.",
        "BankRoot created BankPaymentConsent.",
        "BankRoot created BankPaymentAuthorizationCommitPacket.",
        "BankRoot created PaymentAuthorizationReceipt.",
        "BankRoot created PaymentStatusReceipt.",
        "PaymentAuthorizationReceipt is evidence only.",
        "PaymentAuthorizationReceipt is not ticket permission.",
        "PaymentStatusReceipt is evidence only.",
        "BankRoot does not create ticket.",
        "BankRoot does not call real bank API.",
        "No real payment was executed.",
        "No real settlement happened.",
        f"sandbox_status: {report['bank_payment_authorization_sandbox']['sandbox_status']}",
        "",
        "[CLIENTROOT PURCHASE ORCHESTRATION]",
        "ClientRoot received the travel intent.",
        "ClientRoot observed AirlineRoot OfferResponse.",
        "ClientRoot observed OfferHoldReceipt as evidence only.",
        "ClientRoot selected the mock offer.",
        "ClientRoot created ClientPurchaseApprovalEvidence.",
        "ClientRoot routed bounded purchase approval evidence to BankRoot.",
        "ClientRoot routed bounded selected-offer evidence to AirlineRoot.",
        "ClientRoot observed BankRoot PaymentAuthorizationReceipt as evidence only.",
        "ClientRoot observed PaymentStatusReceipt as evidence only.",
        "ClientRoot does not authorize bank payment.",
        "ClientRoot does not issue ticket.",
        "ClientRoot does not create airline order.",
        "ClientRoot does not create bank receipt.",
        "ClientRoot does not expose raw passport/card/IBAN/payment token.",
        "No real payment was executed.",
        "No real ticket was issued.",
        "No real booking was created.",
        f"orchestration_status: {report['client_purchase_orchestration']['orchestration_status']}",
        "",
        "[AIRLINEROOT TICKET ISSUE MOCK CORRIDOR]",
        "AirlineRoot observed OfferHoldReceipt as evidence only.",
        "AirlineRoot observed ClientPurchaseApprovalEvidence as evidence only.",
        "AirlineRoot observed BankRoot PaymentAuthorizationReceipt as evidence only.",
        "AirlineRoot observed PaymentStatusReceipt as evidence only.",
        "AirlineRoot validated offer hold TTL / freshness.",
        "AirlineRoot validated amount/currency/merchant match.",
        "AirlineRoot validated passenger sealed ref only.",
        "AirlineRoot validated no raw passport/card/payment token exposure.",
        "AirlineRoot authorized the mock ticket-issue intent.",
        "AirlineRoot created AirlineTicketIssueCommitPacket.",
        "AirlineRoot created AirlineOrderCreatedReceipt.",
        "Airline ticket sandbox produced MockTicketReceipt evidence.",
        "AirlineRoot created MockPNR.",
        "MockTicketReceipt is evidence only.",
        "MockTicketReceipt is not a real ticket.",
        "MockPNR is not a real booking.",
        "PaymentAuthorizationReceipt does not automatically create ticket.",
        "ClientPurchaseApprovalEvidence does not authorize AirlineRoot by itself.",
        "No real airline API was called.",
        "No real ticket was issued.",
        "No real booking was created.",
        "No real payment or settlement happened.",
        f"corridor_status: {report['airline_ticket_issue_mock_corridor']['corridor_status']}",
        "",
        "[INTEGRATED TRI-PARTY TRANSACTION TRACE]",
        "This is one transaction, not three unrelated demos.",
        "Every phase carries the same transaction_id.",
        "ClientRoot, AirlineRoot, and BankRoot exchange evidence, not authority.",
        "Offer hold, payment authorization, and mock ticket evidence all remain evidence-only.",
        "No real payment, ticket, booking, API, provider, network, or Gemini call occurs.",
    ]
    for row in report["integrated_transaction_trace"]:
        lines.append(
            "{trace_index}. {phase_id}: {source_root_id} -> {target_root_id}".format(
                **row,
            ),
        )

    lines.extend(
        (
            "",
            "[CROSS-ROOT EVIDENCE ROUTING MATRIX]",
            "ClientRoot sends bounded offer request to AirlineRoot.",
            "AirlineRoot returns offer/hold evidence.",
            "ClientRoot sends purchase approval and payment profile sealed ref to BankRoot.",
            "BankRoot returns payment authorization/status evidence.",
            "ClientRoot forwards payment evidence to AirlineRoot.",
            "AirlineRoot returns mock order/ticket/PNR evidence.",
            "Every route transfers evidence only, not authority.",
        ),
    )
    for row in report["cross_root_evidence_routing_matrix"]:
        lines.append(
            "- {route_id}: {source_root_id} -> {target_root_id}; {artifact}".format(
                **row,
            ),
        )

    final_summary = report["final_tri_party_mock_summary"]
    lines.extend(
        (
            "",
            "[FINAL TRI-PARTY MOCK SUMMARY]",
            (
                "Client view: mock ticket evidence received, "
                "no real travel booking."
            ),
            (
                "Airline view: mock order/ticket/PNR evidence created, "
                "no real airline API."
            ),
            "Bank view: mock payment authorized/not settled, no real payment.",
            "Receipts remain evidence only.",
            "Root boundaries remain side-specific.",
            "No real-world effect occurred.",
            f"summary_id: {final_summary['summary_id']}",
            f"final_status: {final_summary['final_status']}",
        ),
    )

    corridor_report = report["airline_ticket_purchase_corridor_v0_1"]
    corridor_integration = report["airline_ticket_purchase_corridor_integration"]
    lines.extend(
        (
            "",
            "[AIRLINE TICKET/PURCHASE CORRIDOR V0.1 ROOT-CENTERED INTEGRATION]",
            "The existing Airline transaction, not a second demo, entered the corridor.",
            "Existing deterministic artifacts were projected into Airline domain contracts.",
            "The universal core no-post-Root reasoning guard ran for all five phases.",
            (
                "Airline-specific offer/hold/passenger/route/payment/ticket "
                "bindings were validated by the Airline domain projection."
            ),
            "AirlineRoot reviewed offer/hold.",
            "ClientRoot reviewed purchase intent.",
            "BankRoot reviewed payment authorization.",
            "AirlineRoot reviewed mock ticket issue.",
            "ClientRoot observed mock completion.",
            "Completion observer produced MockPurchaseReceipt evidence.",
            "Three existing fixture receipts were observed.",
            "The corridor created zero runtime receipts.",
            "Receipts are evidence only and do not create future permission.",
            "Evidence crossed Root boundaries; authority did not.",
            "No real payment, ticket, booking, API, provider, network, or Gemini call occurred.",
            f"integration_status: {corridor_integration['integration_status']}",
            f"corridor_final_status: {corridor_report.final_status}",
        ),
    )
    for phase in corridor_report.phase_results:
        lines.append(
            (
                "- phase {phase_index}: {phase_id}; root={relevant_root_id}; "
                "status={phase_status}"
            ).format(
                phase_index=phase.phase_index,
                phase_id=phase.phase_id,
                relevant_root_id=phase.relevant_root_id,
                phase_status=phase.phase_status,
            ),
        )
    lines.append("binding_matrix:")
    for row in report["airline_ticket_purchase_corridor_binding_matrix"]:
        lines.append(
            (
                "- {binding_id}: {source_report_path} -> "
                "{corridor_artifact_type}.{corridor_field}; "
                "values_match={values_match}"
            ).format(**row),
        )

    ledger_integration = report["airline_transaction_artifact_ledger_integration"]
    lines.extend(
        (
            "",
            "[AIRLINE TRANSACTION ARTIFACT LEDGER V0.1]",
            f"integration_status: {ledger_integration['integration_status']}",
            f"ledger_id: {ledger_integration['ledger_id']}",
            f"transaction_id: {ledger_integration['transaction_id']}",
            f"selected_offer: {ledger_integration['selected_offer_id']}",
            f"source_run_ref: {ledger_integration['source_run_ref']}",
            f"source_causal_report_ref: {ledger_integration['source_causal_report_ref']}",
            f"source_corridor_report_ref: {ledger_integration['source_corridor_report_ref']}",
            (
                "source_bundle_validation: "
                f"{ledger_integration['source_bundle_validation_status']}"
            ),
            f"ledger_validation: {ledger_integration['ledger_validation_status']}",
            f"entries: {ledger_integration['entry_count']}",
            f"dependency_edges: {ledger_integration['dependency_edge_count']}",
            f"Root finals: {ledger_integration['root_final_count']}",
            f"corridor_executions: {ledger_integration['corridor_execution_count']}",
            f"Ledger collections: {ledger_integration['ledger_collection_count']}",
            f"artifact_written: {ledger_integration['artifact_written_count'] == 1}",
            (
                "Ledger-created authority: "
                f"{ledger_integration['ledger_created_authority_count']}"
            ),
            (
                "Ledger-created permission: "
                f"{ledger_integration['ledger_created_permission_count']}"
            ),
            (
                "Ledger-created action: "
                f"{ledger_integration['ledger_created_action_count']}"
            ),
            (
                "provider/network/Gemini calls added by Ledger: "
                f"{ledger_integration['provider_calls_added_by_ledger_count']}/"
                f"{ledger_integration['network_calls_added_by_ledger_count']}/"
                f"{ledger_integration['gemini_calls_added_by_ledger_count']}"
            ),
            f"real-world effects: {ledger_integration['real_world_effects_count']}",
        ),
    )

    lines.extend(
        (
            "",
        "[MOCK PROTOCOL FIXTURES]",
        ),
    )
    for fixture_name in report["mock_protocol_fixtures"]:
        lines.append(f"- {fixture_name}")

    lines.extend(("", "[SHARED TRANSACTION LEDGER]"))
    lines.append("shared transaction ledger")
    for row in report["shared_transaction_ledger"]:
        lines.append(
            "{ledger_index}. {event_type} -> {artifact_ref}".format(**row),
        )

    lines.extend(("", "[ROOT BOUNDARY MATRIX]"))
    for row in report["root_boundary_matrix"]:
        lines.append(
            f"- {row['boundary']}: preserved={row['boundary_preserved']}, violations={row['violation_count']}",
        )

    lines.extend(("", "[RECEIPT BOUNDARY MATRIX]"))
    lines.append("Receipt crosses roots as evidence, not authority.")
    for row in report["receipt_boundary_matrix"]:
        lines.append(
            f"- {row['boundary']}: preserved={row['boundary_preserved']}, violations={row['violation_count']}",
        )

    privacy = report["privacy_boundary_matrix"]
    lines.extend(
        (
            "",
            "[PRIVACY / SEALED REF BOUNDARY]",
            f"raw_passport_exposed_count: {privacy['raw_passport_exposed_count']}",
            f"raw_card_exposed_count: {privacy['raw_card_exposed_count']}",
            f"raw_iban_exposed_count: {privacy['raw_iban_exposed_count']}",
            f"raw_payment_token_exposed_count: {privacy['raw_payment_token_exposed_count']}",
        ),
    )

    lines.extend(("", "[NON-ACTION REUSE CONSTRAINTS]"))
    lines.append("Old quote is not ticket permission.")
    lines.append("Non-Action Direct Reuse cannot buy ticket.")
    for item in report["non_action_reuse_constraints"]["constraints"]:
        lines.append(f"- {item}")

    lines.extend(("", "[FUTURE SEMANTIC ACTOR TOPOLOGY]"))
    lines.append("Future LLM actors are planned, but none execute in this slice.")
    for actor in report["future_semantic_actor_topology"]:
        lines.append(
            "- {role} ({side}): executed_in_slice_b={executed_in_slice_b}".format(
                **actor,
            ),
        )

    lines.extend(("", "[FUTURE VERTICAL FRACTAL MAP]"))
    lines.append("Future vertical fractal cells are planned, but none execute in this slice.")
    for root_name, cells in report["future_vertical_fractal_map"].items():
        lines.append(f"{root_name}:")
        for cell in cells:
            lines.append(
                "  - {cell_id}: executed_in_slice_b={executed_in_slice_b}".format(
                    **cell,
                ),
            )

    lines.extend(("", "[COUNTER TABLE]"))
    for key in sorted(report["counter_table"]):
        lines.append(f"{key}: {report['counter_table'][key]}")

    lines.extend(
        (
            "",
            "[NON-CLAIMS]",
            (
                "The standalone default path uses five local deterministic "
                "semantic callbacks; no provider network call or Gemini call occurs."
            ),
            "Ledger integration adds no semantic/provider call.",
        ),
    )
    lines.extend(f"- {claim}" for claim in report["non_claims"])
    lines.extend(
        (
            "",
            "[NEXT GATE]",
            str(report["next_gate"]),
            "",
            "[FINAL STATUS]",
            str(report["final_status"]),
        ),
    )
    return "\n".join(lines)


def run_tri_party_airline_ticket_purchase_mock_e2e_v01() -> str:
    return render_tri_party_airline_ticket_purchase_mock_e2e_v01(
        collect_tri_party_airline_ticket_purchase_mock_e2e_v01(),
    )


def main() -> int:
    print(run_tri_party_airline_ticket_purchase_mock_e2e_v01())
    return 0


def _transaction_identity() -> dict[str, Any]:
    return {
        "transaction_id": TRANSACTION_ID,
        "client_root_id": CLIENT_ROOT_ID,
        "airline_root_id": AIRLINE_ROOT_ID,
        "bank_root_id": BANK_ROOT_ID,
        "mock_only": True,
        "real_world_effects_allowed": False,
    }


def _participants() -> dict[str, dict[str, Any]]:
    return {
        "ClientRoot": {
            "root_id": CLIENT_ROOT_ID,
            "role": "client_travel_purchase_root",
            "knows": (
                "travel intent",
                "passenger sealed refs",
                "payment profile sealed ref",
                "selected offer ref",
                "user approval evidence",
            ),
            "does_not": (
                "expose raw passport",
                "expose raw card",
                "expose raw IBAN",
                "issue ticket",
                "authorize bank payment",
            ),
            "produces": "client purchase approval evidence only",
        },
        "AirlineRoot": {
            "root_id": AIRLINE_ROOT_ID,
            "role": "airline_offer_order_ticket_root",
            "knows": (
                "mock inventory",
                "mock fares",
                "mock seats",
                "baggage rule",
                "offer TTL",
                "order creation rule",
                "ticket issue rule",
            ),
            "creates": (
                "OfferResponse fixture",
                "OfferHoldReceipt fixture",
                "future OrderCreatedReceipt fixture",
                "future MockTicketReceipt / mock PNR fixture",
            ),
            "validates": "payment evidence later",
            "does_not": (
                "charge card",
                "authorize client payment",
                "request raw passport",
                "call real airline API",
            ),
        },
        "BankRoot": {
            "root_id": BANK_ROOT_ID,
            "role": "bank_payment_authorization_root",
            "knows": (
                "payment token ref",
                "debtor slot",
                "merchant/airline ref",
                "amount/currency",
                "idempotency",
                "consent/payment order/status",
            ),
            "creates": (
                "future PaymentIntent fixture",
                "future PaymentConsent fixture",
                "future PaymentAuthorizationReceipt fixture",
                "future PaymentStatusReceipt fixture",
            ),
            "does_not": (
                "create ticket",
                "call real bank API",
                "execute real payment",
            ),
        },
    }


def _travel_intent() -> dict[str, Any]:
    return {
        "origin": "PAR",
        "destination": "LIM",
        "depart_date": "2026-08-12",
        "return_date": "2026-08-21",
        "passengers_count": 1,
        "cabin": "economy",
        "baggage_needed": True,
        "max_price_amount": 840,
        "currency": "EUR",
        "user_goal": (
            "Find and hold a safe mock airline offer, authorize mock payment, "
            "and receive mock ticket evidence."
        ),
    }


def _sealed_refs() -> dict[str, dict[str, Any]]:
    return {
        "PassengerSealedRefsV01": {
            "passenger_ref": "sealed_passenger_ref:client_001:pax_001",
            "passport_ref": "sealed_passport_ref:client_001:pax_001",
            "loyalty_ref": "sealed_loyalty_ref:optional:none",
            "raw_passport_exposed": False,
            "raw_birthdate_exposed": False,
            "raw_document_number_exposed": False,
        },
        "PaymentProfileSealedRefV01": {
            "payment_profile_ref": "sealed_payment_profile_ref:client_001:pay_001",
            "payment_token_ref": "sealed_payment_token_ref:client_001:token_001",
            "debtor_slot_ref": "sealed_debtor_slot_ref:client_001:bank_a",
            "raw_card_exposed": False,
            "raw_iban_exposed": False,
            "raw_payment_token_exposed": False,
        },
    }


def _semantic_offer_fixture_values(
    semantic_causal_run: causal_runtime.AirlineSemanticCausalRunReportV01 | None,
) -> dict[str, Any]:
    if semantic_causal_run is None:
        return {
            "offer_id": "offer:mock_airline_al:PAR-LIM:001",
            "hold_id": "hold:mock_airline_al:001",
            "suffix": "001",
            "amount": 782,
            "currency": "EUR",
            "ttl_seconds": 900,
            "route_ref": None,
            "baggage_included": True,
            "seat_characteristics": ("window", "standard"),
            "changeable": True,
            "fare_basis": "ECON_SAFE_1",
        }
    resolution = semantic_causal_run.airline_root_resolution
    hold_packet = semantic_causal_run.hold_packet
    if resolution is None or hold_packet is None:
        raise ValueError("semantic causal run missing resolution or hold packet")
    suffix = resolution.selected_offer_id.rsplit(":", 1)[-1]
    return {
        "offer_id": resolution.selected_offer_id,
        "hold_id": hold_packet.hold_id,
        "suffix": suffix,
        "amount": resolution.resolved_amount,
        "currency": resolution.resolved_currency,
        "ttl_seconds": min(hold_packet.ttl_seconds, resolution.resolved_ttl),
        "route_ref": resolution.resolved_route_ref,
        "baggage_included": resolution.resolved_baggage,
        "seat_characteristics": resolution.resolved_seat_characteristics,
        "changeable": resolution.resolved_changeability,
        "fare_basis": f"ECON_SEMANTIC_{suffix}",
        "hold_packet_id": hold_packet.packet_id,
        "parent_offer_packet_id": hold_packet.parent_offer_packet_id,
        "idempotency_key": hold_packet.idempotency_key,
    }


def _mock_protocol_fixtures(
    travel_intent: Mapping[str, Any],
    sealed_refs: Mapping[str, Mapping[str, Any]],
    *,
    semantic_causal_run: causal_runtime.AirlineSemanticCausalRunReportV01 | None = None,
) -> dict[str, dict[str, Any]]:
    passenger = sealed_refs["PassengerSealedRefsV01"]
    payment = sealed_refs["PaymentProfileSealedRefV01"]
    offer_values = _semantic_offer_fixture_values(semantic_causal_run)
    offer_id = offer_values["offer_id"]
    hold_id = offer_values["hold_id"]
    suffix = offer_values["suffix"]
    client_purchase_approval_ref = "client_purchase_approval:client_001:001"
    client_purchase_intent_id = "client_purchase_intent:client_001:001"
    payment_authorization_receipt_id = "payment_authorization_receipt:mock_bank_a:001"
    payment_authorization_ref_id = "bank_payment_authorization_ref:mock_bank_a:001"
    mock_purchase_receipt_id = "mock_purchase_receipt:client_001:001"
    route_ref = (
        f"route:{travel_intent['origin']}-{travel_intent['destination']}:"
        f"{travel_intent['depart_date']}:{travel_intent['return_date']}"
    )
    if offer_values["route_ref"] is not None:
        route_ref = offer_values["route_ref"]
    amount = offer_values["amount"]
    currency = offer_values["currency"]
    ttl_seconds = offer_values["ttl_seconds"]
    mock_pnr = "PNR-EEH01" if suffix == "001" else f"PNR-EEH{suffix}"
    return {
        "AirlineOfferRequestV01": {
            "transaction_id": TRANSACTION_ID,
            "origin": travel_intent["origin"],
            "destination": travel_intent["destination"],
            "depart_date": travel_intent["depart_date"],
            "return_date": travel_intent["return_date"],
            "passengers_count": travel_intent["passengers_count"],
            "cabin": travel_intent["cabin"],
            "baggage_needed": travel_intent["baggage_needed"],
            "passenger_ref": passenger["passenger_ref"],
            "route_ref": route_ref,
            "raw_passport_exposed": False,
        },
        "AirlineOfferCandidateV01": {
            "transaction_id": TRANSACTION_ID,
            "offer_id": offer_id,
            "hold_id": hold_id,
            "passenger_ref": passenger["passenger_ref"],
            "route_ref": route_ref,
            "route": "PAR -> LIM",
            "fare_basis": offer_values["fare_basis"],
            "price_amount": amount,
            "currency": currency,
            "baggage_included": offer_values["baggage_included"],
            "refundable": False,
            "changeable": offer_values["changeable"],
            "seat_characteristics": offer_values["seat_characteristics"],
            "inventory_class": "Y",
            "offer_ttl_seconds": ttl_seconds,
            "mock_only": True,
        },
        "AirlineOfferResponseV01": {
            "response_id": offer_values.get(
                "parent_offer_packet_id",
                f"offer_response:{TRANSACTION_ID}",
            ),
            "transaction_id": TRANSACTION_ID,
            "offer_candidates_count": 1,
            "selected_candidate_ref": offer_id,
            "route_ref": route_ref,
        },
        "AirlineOfferHoldCommitPacketV01": {
            "packet_id": offer_values.get(
                "hold_packet_id",
                "airline_offer_hold_commit_packet:mock_airline_al:001",
            ),
            "transaction_id": TRANSACTION_ID,
            "created_by": "airline_root",
            "root_created": True,
            "allowed_root_id": AIRLINE_ROOT_ID,
            "allowed_action": "mock_offer_hold",
            "allowed_offer_id": offer_id,
            "allowed_hold_id": hold_id,
            "allowed_passenger_ref": passenger["passenger_ref"],
            "allowed_route_ref": route_ref,
            "allowed_amount": amount,
            "currency": currency,
            "ttl_seconds": ttl_seconds,
            "offer_hold_expired": False,
            "idempotency_key": offer_values.get(
                "idempotency_key",
                "idem:airline_offer_hold:001",
            ),
            "evidence_only_downstream": True,
            "payment_permission_created": False,
            "ticket_permission_created": False,
            "real_airline_api_allowed": False,
            "real_booking_allowed": False,
        },
        "AirlineOfferHoldReceiptV01": {
            "receipt_id": f"offer_hold_receipt:mock_airline_al:{suffix}",
            "transaction_id": TRANSACTION_ID,
            "created_by": corridor_contracts.ADAPTER_AIRLINE_HOLD_SANDBOX,
            "root_owner": AIRLINE_ROOT_ID,
            "offer_id": offer_id,
            "hold_id": hold_id,
            "passenger_ref": passenger["passenger_ref"],
            "route_ref": route_ref,
            "amount": amount,
            "currency": currency,
            "hold_status": "held_mock",
            "expires_in_seconds": 900,
            "evidence_only": True,
            "payment_permission_created": False,
            "ticket_permission_created": False,
        },
        "ClientPurchaseApprovalEvidenceV01": {
            "approval_id": client_purchase_approval_ref,
            "transaction_id": TRANSACTION_ID,
            "client_purchase_intent_id": client_purchase_intent_id,
            "selected_offer_id": offer_id,
            "hold_id": hold_id,
            "passenger_ref": passenger["passenger_ref"],
            "route_ref": route_ref,
            "selected_amount": amount,
            "max_price_amount": travel_intent["max_price_amount"],
            "currency": currency,
            "created_by": "client_root",
            "root_created": True,
            "evidence_only": True,
            "scoped_evidence_only": True,
            "bank_authority_created": False,
            "airline_authority_created": False,
            "payment_permission_created": False,
            "ticket_permission_created": False,
            "action_commit_packet_created": False,
            "receipt_created": False,
        },
        "BankPaymentIntentV01": {
            "intent_id": "bank_payment_intent:mock_bank_a:001",
            "transaction_id": TRANSACTION_ID,
            "merchant_ref": "merchant_ref:mock_airline_al",
            "offer_id": offer_id,
            "hold_id": hold_id,
            "passenger_ref": passenger["passenger_ref"],
            "route_ref": route_ref,
            "amount": amount,
            "currency": currency,
            "payment_token_ref": payment["payment_token_ref"],
            "raw_card_exposed": False,
            "real_payment_executed": False,
        },
        "BankPaymentConsentV01": {
            "consent_id": "bank_payment_consent:mock_bank_a:001",
            "transaction_id": TRANSACTION_ID,
            "consent_status": "consented_mock",
            "evidence_only": True,
            "ticket_permission_created": False,
        },
        "BankPaymentAuthorizationCommitPacketV01": {
            "packet_id": "bank_payment_authorization_commit_packet:mock_bank_a:001",
            "transaction_id": TRANSACTION_ID,
            "created_by": "bank_root",
            "root_created": True,
            "allowed_root_id": BANK_ROOT_ID,
            "allowed_action": "mock_payment_authorization",
            "allowed_merchant_ref": "merchant_ref:mock_airline_al",
            "allowed_offer_id": offer_id,
            "allowed_hold_id": hold_id,
            "allowed_passenger_ref": passenger["passenger_ref"],
            "allowed_route_ref": route_ref,
            "allowed_payment_token_ref": payment["payment_token_ref"],
            "allowed_debtor_slot_ref": payment["debtor_slot_ref"],
            "allowed_amount": amount,
            "currency": currency,
            "idempotency_key": "idem:bank_payment_authorization:001",
            "ttl_seconds": 900,
            "evidence_only_downstream": True,
            "ticket_permission_created": False,
            "real_payment_allowed": False,
            "real_bank_api_allowed": False,
            "real_settlement_allowed": False,
        },
        "BankPaymentAuthorizationReceiptV01": {
            "receipt_id": payment_authorization_receipt_id,
            "transaction_id": TRANSACTION_ID,
            "payment_authorization_ref_id": payment_authorization_ref_id,
            "merchant_ref": "merchant_ref:mock_airline_al",
            "offer_id": offer_id,
            "hold_id": hold_id,
            "passenger_ref": passenger["passenger_ref"],
            "route_ref": route_ref,
            "authorized_amount": amount,
            "currency": currency,
            "authorization_status": "authorized_mock",
            "payment_authorization_expired": False,
            "evidence_only": True,
            "ticket_created": False,
            "real_payment_executed": False,
        },
        "BankPaymentStatusReceiptV01": {
            "receipt_id": "payment_status_receipt:mock_bank_a:001",
            "transaction_id": TRANSACTION_ID,
            "payment_status": "authorized_not_settled_mock",
            "evidence_only": True,
            "settlement_executed": False,
            "real_payment_executed": False,
        },
        "AirlineTicketIssueCommitPacketV01": {
            "packet_id": f"airline_ticket_issue_commit_packet:mock_airline_al:{suffix}",
            "transaction_id": TRANSACTION_ID,
            "created_by": "airline_root",
            "root_created": True,
            "allowed_root_id": AIRLINE_ROOT_ID,
            "allowed_action": "mock_airline_ticket_issue",
            "allowed_offer_id": offer_id,
            "allowed_hold_id": hold_id,
            "allowed_order_id": f"order:mock_airline_al:{suffix}",
            "allowed_passenger_ref": passenger["passenger_ref"],
            "allowed_route_ref": route_ref,
            "merchant_ref": "merchant_ref:mock_airline_al",
            "required_offer_hold_receipt_id": f"offer_hold_receipt:mock_airline_al:{suffix}",
            "required_payment_authorization_receipt_id": (
                payment_authorization_receipt_id
            ),
            "required_payment_authorization_ref_id": (
                payment_authorization_ref_id
            ),
            "required_client_purchase_approval_id": (
                client_purchase_approval_ref
            ),
            "required_client_purchase_intent_id": (
                client_purchase_intent_id
            ),
            "allowed_amount": amount,
            "currency": currency,
            "ttl_seconds": ttl_seconds,
            "idempotency_key": f"idem:airline_ticket_issue:{suffix}",
            "mock_only": True,
            "evidence_only_downstream": True,
            "real_ticket_allowed": False,
            "real_booking_allowed": False,
            "real_airline_api_allowed": False,
            "real_payment_allowed": False,
        },
        "AirlineOrderCreatedReceiptV01": {
            "receipt_id": f"order_created_receipt:mock_airline_al:{suffix}",
            "transaction_id": TRANSACTION_ID,
            "order_id": f"order:mock_airline_al:{suffix}",
            "created_by": "airline_root",
            "evidence_only": True,
            "payment_created": False,
            "real_ticket_issued": False,
            "real_booking_created": False,
        },
        "MockTicketReceiptV01": {
            "receipt_id": f"mock_ticket_receipt:mock_airline_al:{suffix}",
            "transaction_id": TRANSACTION_ID,
            "mock_ticket_id": f"mock_ticket:{suffix}",
            "mock_pnr": mock_pnr,
            "created_by": corridor_contracts.ADAPTER_AIRLINE_TICKET_SANDBOX,
            "root_owner": AIRLINE_ROOT_ID,
            "offer_id": offer_id,
            "hold_id": hold_id,
            "passenger_ref": passenger["passenger_ref"],
            "route_ref": route_ref,
            "amount": amount,
            "currency": currency,
            "evidence_only": True,
            "real_ticket": False,
            "real_travel_booking_created": False,
            "payment_created": False,
            "future_payment_permission_created": False,
        },
        "MockPNRV01": {
            "pnr": mock_pnr,
            "transaction_id": TRANSACTION_ID,
            "created_by": "airline_root",
            "mock_only": True,
            "real_booking": False,
        },
        "MockPurchaseReceiptV01": {
            "receipt_id": mock_purchase_receipt_id,
            "transaction_id": TRANSACTION_ID,
            "source_client_purchase_intent_id": client_purchase_intent_id,
            "source_payment_authorization_ref_id": payment_authorization_ref_id,
            "source_mock_ticket_receipt_id": f"mock_ticket_receipt:mock_airline_al:{suffix}",
            "client_root_id": CLIENT_ROOT_ID,
            "airline_root_id": AIRLINE_ROOT_ID,
            "bank_root_id": BANK_ROOT_ID,
            "created_by": "client_completion_observer",
            "root_owner": CLIENT_ROOT_ID,
            "evidence_only": True,
            "side_root_finals_replaced": False,
            "root_truth_rewritten": False,
            "future_permission_created": False,
            "real_payment_executed": False,
            "real_ticket_issued": False,
            "real_booking_created": False,
            "real_world_effects_count": 0,
        },
        "ClientFinalTravelSummaryV01": {
            "summary_id": "client_final_travel_summary:client_001:001",
            "transaction_id": TRANSACTION_ID,
            "client_root_id": CLIENT_ROOT_ID,
            "mock_purchase_receipt_id": mock_purchase_receipt_id,
            "selected_offer_id": offer_id,
            "hold_id": hold_id,
            "passenger_ref": passenger["passenger_ref"],
            "route_ref": route_ref,
            "amount": amount,
            "currency": currency,
            "offer_hold_receipt_id": f"offer_hold_receipt:mock_airline_al:{suffix}",
            "payment_authorization_receipt_id": (
                payment_authorization_receipt_id
            ),
            "payment_authorization_ref_id": (
                payment_authorization_ref_id
            ),
            "payment_status_receipt_id": "payment_status_receipt:mock_bank_a:001",
            "mock_ticket_receipt_id": f"mock_ticket_receipt:mock_airline_al:{suffix}",
            "current_client_status": "mock_ticket_evidence_received_no_real_travel_booking",
            "evidence_only": True,
            "ticket_issued": False,
            "mock_ticket_evidence_received": True,
            "real_ticket_issued": False,
            "real_payment_executed": False,
            "real_booking_created": False,
        },
    }


def _airline_ticket_issue_mock_corridor(
    fixtures: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    ticket_packet = fixtures["AirlineTicketIssueCommitPacketV01"]
    order_receipt = fixtures["AirlineOrderCreatedReceiptV01"]
    ticket_receipt = fixtures["MockTicketReceiptV01"]
    mock_pnr = fixtures["MockPNRV01"]
    return {
        "corridor_id": "airline_ticket_issue_mock_corridor_v01",
        "transaction_id": TRANSACTION_ID,
        "airline_root_id": AIRLINE_ROOT_ID,
        "corridor_status": STATUS_PASS,
        "offer_hold_receipt_observed": True,
        "client_purchase_approval_evidence_observed": True,
        "payment_authorization_receipt_observed": True,
        "payment_status_receipt_observed": True,
        "offer_hold_ttl_freshness_validated": True,
        "selected_offer_match_validated": True,
        "amount_currency_match_validated": True,
        "merchant_airline_ref_match_validated": True,
        "passenger_sealed_ref_validated": True,
        "payment_evidence_validated_against_offer_hold": True,
        "raw_passport_absent": True,
        "raw_card_absent": True,
        "raw_payment_token_absent": True,
        "airline_ticket_issue_commit_packet_created": True,
        "airline_ticket_issue_commit_packet_created_by": "airline_root",
        "airline_ticket_issue_commit_packet_root_created": True,
        "airline_ticket_issue_commit_packet_validated": True,
        "airline_ticket_issue_commit_packet_ref": ticket_packet["packet_id"],
        "airline_order_created_receipt_created": True,
        "airline_order_created_receipt_validated": True,
        "airline_order_created_receipt_ref": order_receipt["receipt_id"],
        "mock_ticket_receipt_created": True,
        "mock_ticket_receipt_validated": True,
        "mock_ticket_receipt_ref": ticket_receipt["receipt_id"],
        "mock_pnr_created": True,
        "mock_pnr_validated": True,
        "mock_pnr": mock_pnr["pnr"],
        "mock_ticket_receipt_evidence_only": True,
        "mock_ticket_receipt_real_ticket": False,
        "mock_ticket_receipt_payment_created": False,
        "mock_pnr_real_booking": False,
        "payment_authorization_receipt_created_ticket": False,
        "client_purchase_approval_created_ticket": False,
        "offer_hold_receipt_created_ticket": False,
        "airline_root_authorized_payment": False,
        "airline_root_called_real_airline_api": False,
        "airline_root_called_real_gds_api": False,
        "real_ticket_issued": False,
        "real_booking_created": False,
        "real_payment_executed": False,
        "real_settlement_executed": False,
        "real_world_effects_count": 0,
    }


def _client_purchase_orchestration(
    travel_intent: Mapping[str, Any],
    sealed_refs: Mapping[str, Mapping[str, Any]],
    fixtures: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    passenger = sealed_refs["PassengerSealedRefsV01"]
    payment = sealed_refs["PaymentProfileSealedRefV01"]
    offer_response = fixtures["AirlineOfferResponseV01"]
    offer_candidate = fixtures["AirlineOfferCandidateV01"]
    approval = fixtures["ClientPurchaseApprovalEvidenceV01"]
    return {
        "orchestration_id": "client_purchase_orchestration_v01",
        "transaction_id": TRANSACTION_ID,
        "client_root_id": CLIENT_ROOT_ID,
        "orchestration_status": STATUS_PASS,
        "travel_intent_observed": True,
        "passenger_sealed_refs_observed": True,
        "passenger_ref": passenger["passenger_ref"],
        "payment_profile_sealed_ref_observed": True,
        "payment_profile_ref": payment["payment_profile_ref"],
        "offer_response_observed": True,
        "offer_hold_receipt_observed": True,
        "selected_offer_id": offer_response["selected_candidate_ref"],
        "selected_offer_amount": offer_candidate["price_amount"],
        "selected_offer_currency": offer_candidate["currency"],
        "selected_offer_within_user_max_price": (
            offer_candidate["price_amount"] <= travel_intent["max_price_amount"]
        ),
        "client_purchase_approval_evidence_created": True,
        "client_purchase_approval_evidence_created_by": "client_root",
        "client_purchase_approval_evidence_root_created": True,
        "client_purchase_approval_evidence_validated": True,
        "client_purchase_approval_evidence_evidence_only": True,
        "client_purchase_approval_evidence_ref": approval["approval_id"],
        "routed_to_bank_root": True,
        "routed_to_airline_root": True,
        "bank_payment_authorization_receipt_observed": True,
        "bank_payment_status_receipt_observed": True,
        "client_final_purchase_summary_created": True,
        "client_root_authorized_bank_payment": False,
        "client_root_issued_ticket": False,
        "client_root_created_airline_order": False,
        "client_root_created_bank_receipt": False,
        "client_root_created_action_commit_packet": False,
        "raw_passport_exposed": False,
        "raw_card_exposed": False,
        "raw_iban_exposed": False,
        "raw_payment_token_exposed": False,
        "real_payment_executed": False,
        "real_ticket_issued": False,
        "real_booking_created": False,
        "real_world_effects_count": 0,
    }


def _bank_payment_authorization_sandbox(
    fixtures: Mapping[str, Mapping[str, Any]],
    sealed_refs: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    payment = sealed_refs["PaymentProfileSealedRefV01"]
    payment_packet = fixtures["BankPaymentAuthorizationCommitPacketV01"]
    payment_auth_receipt = fixtures["BankPaymentAuthorizationReceiptV01"]
    payment_status_receipt = fixtures["BankPaymentStatusReceiptV01"]
    return {
        "sandbox_id": "bank_payment_authorization_sandbox_v01",
        "transaction_id": TRANSACTION_ID,
        "bank_root_id": BANK_ROOT_ID,
        "sandbox_status": STATUS_PASS,
        "offer_hold_receipt_observed": True,
        "client_purchase_approval_evidence_observed": True,
        "payment_profile_sealed_ref_observed": True,
        "amount_currency_validated": True,
        "merchant_airline_ref_validated": True,
        "payment_token_ref_validated": True,
        "payment_token_ref": payment["payment_token_ref"],
        "debtor_slot_ref_validated": True,
        "debtor_slot_ref": payment["debtor_slot_ref"],
        "idempotency_checked": True,
        "expiry_ttl_checked": True,
        "bank_payment_intent_created": True,
        "bank_payment_consent_created": True,
        "bank_payment_authorization_commit_packet_created": True,
        "bank_payment_authorization_commit_packet_created_by": "bank_root",
        "bank_payment_authorization_commit_packet_root_created": True,
        "bank_payment_authorization_commit_packet_validated": True,
        "bank_payment_authorization_commit_packet_ref": payment_packet["packet_id"],
        "payment_authorization_receipt_created": True,
        "payment_authorization_receipt_validated": True,
        "payment_authorization_receipt_ref": payment_auth_receipt["receipt_id"],
        "payment_status_receipt_created": True,
        "payment_status_receipt_validated": True,
        "payment_status_receipt_ref": payment_status_receipt["receipt_id"],
        "payment_authorization_receipt_evidence_only": True,
        "payment_authorization_receipt_ticket_permission_created": False,
        "payment_authorization_receipt_real_payment_executed": False,
        "payment_status_receipt_evidence_only": True,
        "payment_status_receipt_settlement_executed": False,
        "payment_status_receipt_ticket_permission_created": False,
        "bank_root_created_ticket": False,
        "real_bank_api_called": False,
        "real_payment_executed": False,
        "real_settlement_executed": False,
        "real_ticket_issued": False,
        "real_world_effects_count": 0,
    }


def _airline_offer_hold_sandbox(
    fixtures: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    offer_response = fixtures["AirlineOfferResponseV01"]
    offer_hold_packet = fixtures["AirlineOfferHoldCommitPacketV01"]
    offer_hold_receipt = fixtures["AirlineOfferHoldReceiptV01"]
    return {
        "sandbox_id": "airline_offer_hold_sandbox_v01",
        "transaction_id": TRANSACTION_ID,
        "airline_root_id": AIRLINE_ROOT_ID,
        "sandbox_status": STATUS_PASS,
        "offer_request_validated": True,
        "mock_inventory_checked": True,
        "mock_fare_checked": True,
        "baggage_rule_checked": True,
        "offer_ttl_checked": True,
        "selected_offer_id": offer_response["selected_candidate_ref"],
        "offer_response_created": True,
        "offer_hold_commit_packet_created": True,
        "offer_hold_commit_packet_created_by": "airline_root",
        "offer_hold_commit_packet_root_created": True,
        "offer_hold_commit_packet_validated": True,
        "offer_hold_commit_packet_ref": offer_hold_packet["packet_id"],
        "offer_hold_receipt_created": True,
        "offer_hold_receipt_validated": True,
        "offer_hold_receipt_ref": offer_hold_receipt["receipt_id"],
        "offer_hold_receipt_evidence_only": True,
        "offer_hold_receipt_payment_permission_created": False,
        "offer_hold_receipt_ticket_permission_created": False,
        "real_airline_api_called": False,
        "real_booking_created": False,
        "real_ticket_issued": False,
        "real_world_effects_count": 0,
    }


def _shared_transaction_ledger(
    fixtures: Mapping[str, Mapping[str, Any]],
) -> tuple[dict[str, Any], ...]:
    rows = (
        (CLIENT_ROOT_ID, "client_travel_intent_recorded", "TravelIntentV01", True),
        (AIRLINE_ROOT_ID, "airline_offer_request_fixture_created", "AirlineOfferRequestV01", True),
        (AIRLINE_ROOT_ID, "airline_offer_candidate_fixture_created", "AirlineOfferCandidateV01", True),
        (AIRLINE_ROOT_ID, "airline_offer_response_fixture_created", "AirlineOfferResponseV01", True),
        (AIRLINE_ROOT_ID, "airline_offer_hold_receipt_fixture_created", "AirlineOfferHoldReceiptV01", True),
        (CLIENT_ROOT_ID, "client_purchase_approval_evidence_fixture_created", "ClientPurchaseApprovalEvidenceV01", True),
        (BANK_ROOT_ID, "bank_payment_intent_fixture_created", "BankPaymentIntentV01", True),
        (BANK_ROOT_ID, "bank_payment_consent_fixture_created", "BankPaymentConsentV01", True),
        (BANK_ROOT_ID, "bank_payment_authorization_receipt_fixture_created", "BankPaymentAuthorizationReceiptV01", True),
        (BANK_ROOT_ID, "bank_payment_status_receipt_fixture_created", "BankPaymentStatusReceiptV01", True),
        (AIRLINE_ROOT_ID, "airline_order_created_receipt_fixture_created", "AirlineOrderCreatedReceiptV01", True),
        (AIRLINE_ROOT_ID, "mock_ticket_receipt_fixture_created", "MockTicketReceiptV01", True),
        (AIRLINE_ROOT_ID, "mock_pnr_fixture_created", "MockPNRV01", True),
        (CLIENT_ROOT_ID, "mock_purchase_receipt_fixture_created", "MockPurchaseReceiptV01", True),
        (CLIENT_ROOT_ID, "final_shared_summary_fixture_created", "ClientFinalTravelSummaryV01", True),
    )
    sandbox_stage_events = {
        "airline_offer_request_fixture_created",
        "airline_offer_candidate_fixture_created",
        "airline_offer_response_fixture_created",
        "airline_offer_hold_receipt_fixture_created",
    }
    bank_sandbox_stage_events = {
        "bank_payment_intent_fixture_created",
        "bank_payment_consent_fixture_created",
        "bank_payment_authorization_receipt_fixture_created",
        "bank_payment_status_receipt_fixture_created",
    }
    ticket_issue_corridor_events = {
        "airline_order_created_receipt_fixture_created",
        "mock_ticket_receipt_fixture_created",
        "mock_pnr_fixture_created",
        "mock_purchase_receipt_fixture_created",
        "final_shared_summary_fixture_created",
    }
    ledger_rows = []
    for index, (actor_root_id, event_type, artifact_name, evidence_only) in enumerate(
        rows,
        start=1,
    ):
        row = {
            "ledger_index": index,
            "transaction_id": TRANSACTION_ID,
            "actor_root_id": actor_root_id,
            "event_type": event_type,
            "artifact_ref": _artifact_ref(artifact_name, fixtures),
            "evidence_only": evidence_only,
            "authority_created": False,
            "real_world_effects_count": 0,
        }
        if event_type in sandbox_stage_events:
            row["sandbox_stage"] = "airline_offer_hold_sandbox"
            row["validated_by_airline_root"] = True
        if event_type in bank_sandbox_stage_events:
            row["sandbox_stage"] = "bank_payment_authorization_sandbox"
            row["validated_by_bank_root"] = True
        if event_type == "client_purchase_approval_evidence_fixture_created":
            row["orchestration_stage"] = "client_purchase_orchestration"
            row["validated_by_client_root"] = True
        if event_type in ticket_issue_corridor_events:
            row["corridor_stage"] = "airline_ticket_issue_mock_corridor"
            row["validated_by_airline_root"] = True
        ledger_rows.append(row)
    return tuple(ledger_rows)


def _integrated_transaction_trace(
    fixtures: Mapping[str, Mapping[str, Any]],
) -> tuple[dict[str, Any], ...]:
    offer_id = fixtures["AirlineOfferCandidateV01"]["offer_id"]
    phases = (
        (
            "client_travel_intent_recorded",
            CLIENT_ROOT_ID,
            CLIENT_ROOT_ID,
            ("TravelIntentV01",),
        ),
        (
            "client_to_airline_offer_request",
            CLIENT_ROOT_ID,
            AIRLINE_ROOT_ID,
            ("AirlineOfferRequestV01",),
        ),
        (
            "airline_offer_hold_sandbox_completed",
            AIRLINE_ROOT_ID,
            AIRLINE_ROOT_ID,
            (
                "AirlineOfferResponseV01",
                "AirlineOfferHoldCommitPacketV01",
                "AirlineOfferHoldReceiptV01",
            ),
        ),
        (
            "airline_to_client_offer_hold_receipt_returned",
            AIRLINE_ROOT_ID,
            CLIENT_ROOT_ID,
            ("AirlineOfferResponseV01", "AirlineOfferHoldReceiptV01"),
        ),
        (
            "client_offer_selected",
            CLIENT_ROOT_ID,
            CLIENT_ROOT_ID,
            (offer_id,),
        ),
        (
            "client_purchase_approval_evidence_created",
            CLIENT_ROOT_ID,
            CLIENT_ROOT_ID,
            ("ClientPurchaseApprovalEvidenceV01",),
        ),
        (
            "client_to_bank_payment_authorization_request",
            CLIENT_ROOT_ID,
            BANK_ROOT_ID,
            ("ClientPurchaseApprovalEvidenceV01", "PaymentProfileSealedRefV01"),
        ),
        (
            "bank_payment_authorization_sandbox_completed",
            BANK_ROOT_ID,
            BANK_ROOT_ID,
            (
                "BankPaymentIntentV01",
                "BankPaymentConsentV01",
                "BankPaymentAuthorizationCommitPacketV01",
                "BankPaymentAuthorizationReceiptV01",
                "BankPaymentStatusReceiptV01",
            ),
        ),
        (
            "bank_to_client_payment_authorization_receipt_returned",
            BANK_ROOT_ID,
            CLIENT_ROOT_ID,
            ("BankPaymentAuthorizationReceiptV01",),
        ),
        (
            "bank_to_client_payment_status_receipt_returned",
            BANK_ROOT_ID,
            CLIENT_ROOT_ID,
            ("BankPaymentStatusReceiptV01",),
        ),
        (
            "client_to_airline_payment_evidence_forwarded",
            CLIENT_ROOT_ID,
            AIRLINE_ROOT_ID,
            (
                "ClientPurchaseApprovalEvidenceV01",
                "BankPaymentAuthorizationReceiptV01",
                "BankPaymentStatusReceiptV01",
            ),
        ),
        (
            "airline_ticket_issue_mock_corridor_completed",
            AIRLINE_ROOT_ID,
            AIRLINE_ROOT_ID,
            (
                "AirlineTicketIssueCommitPacketV01",
                "AirlineOrderCreatedReceiptV01",
                "MockTicketReceiptV01",
                "MockPNRV01",
            ),
        ),
        (
            "airline_to_client_order_created_receipt_returned",
            AIRLINE_ROOT_ID,
            CLIENT_ROOT_ID,
            ("AirlineOrderCreatedReceiptV01",),
        ),
        (
            "airline_to_client_mock_ticket_receipt_returned",
            AIRLINE_ROOT_ID,
            CLIENT_ROOT_ID,
            ("MockTicketReceiptV01",),
        ),
        (
            "airline_to_client_mock_pnr_returned",
            AIRLINE_ROOT_ID,
            CLIENT_ROOT_ID,
            ("MockPNRV01",),
        ),
        (
            "client_final_mock_travel_summary_created",
            CLIENT_ROOT_ID,
            CLIENT_ROOT_ID,
            ("MockPurchaseReceiptV01", "ClientFinalTravelSummaryV01"),
        ),
        (
            "final_shared_summary_fixture_created",
            CLIENT_ROOT_ID,
            CLIENT_ROOT_ID,
            (
                "MockPurchaseReceiptV01",
                "ClientFinalTravelSummaryV01",
                "FinalTriPartyMockSummaryV01",
            ),
        ),
    )
    return tuple(
        {
            "trace_index": index,
            "transaction_id": TRANSACTION_ID,
            "phase_id": phase_id,
            "source_root_id": source_root_id,
            "target_root_id": target_root_id,
            "artifact_refs": tuple(
                _artifact_ref(artifact_name, fixtures)
                for artifact_name in artifact_names
            ),
            "evidence_only": True,
            "authority_transferred": False,
            "raw_secrets_exposed": False,
            "real_ticket_claimed": False,
            "real_payment_claimed": False,
            "real_booking_claimed": False,
            "real_world_effects_count": 0,
        }
        for index, (phase_id, source_root_id, target_root_id, artifact_names)
        in enumerate(phases, start=1)
    )


def _cross_root_evidence_routing_matrix() -> tuple[dict[str, Any], ...]:
    rows = (
        {
            "route_id": "A",
            "source_root_id": CLIENT_ROOT_ID,
            "target_root_id": AIRLINE_ROOT_ID,
            "artifact": "AirlineOfferRequestV01",
            "purpose": "request mock offers",
            "evidence_only": True,
            "authority_transferred": False,
            "raw_passport_exposed": False,
            "raw_card_exposed": False,
        },
        {
            "route_id": "B",
            "source_root_id": AIRLINE_ROOT_ID,
            "target_root_id": CLIENT_ROOT_ID,
            "artifact": "AirlineOfferResponseV01 + OfferHoldReceipt",
            "purpose": "return mock offer and hold evidence",
            "evidence_only": True,
            "payment_permission_created": False,
            "ticket_permission_created": False,
            "authority_transferred": False,
        },
        {
            "route_id": "C",
            "source_root_id": CLIENT_ROOT_ID,
            "target_root_id": BANK_ROOT_ID,
            "artifact": "ClientPurchaseApprovalEvidence + PaymentProfileSealedRef",
            "purpose": "request mock payment authorization",
            "evidence_only": True,
            "bank_authority_created_by_client": False,
            "raw_card_exposed": False,
            "raw_iban_exposed": False,
            "authority_transferred": False,
        },
        {
            "route_id": "D",
            "source_root_id": BANK_ROOT_ID,
            "target_root_id": CLIENT_ROOT_ID,
            "artifact": "PaymentAuthorizationReceipt + PaymentStatusReceipt",
            "purpose": "return mock payment authorization evidence",
            "evidence_only": True,
            "ticket_permission_created": False,
            "real_payment_executed": False,
            "authority_transferred": False,
        },
        {
            "route_id": "E",
            "source_root_id": CLIENT_ROOT_ID,
            "target_root_id": AIRLINE_ROOT_ID,
            "artifact": (
                "ClientPurchaseApprovalEvidence + PaymentAuthorizationReceipt "
                "+ PaymentStatusReceipt"
            ),
            "purpose": (
                "ask AirlineRoot to validate payment evidence and issue mock "
                "ticket evidence"
            ),
            "evidence_only": True,
            "airline_authority_created_by_client": False,
            "ticket_permission_created_by_payment_receipt": False,
            "authority_transferred": False,
        },
        {
            "route_id": "F",
            "source_root_id": AIRLINE_ROOT_ID,
            "target_root_id": CLIENT_ROOT_ID,
            "artifact": "OrderCreatedReceipt + MockTicketReceipt + MockPNR",
            "purpose": "return mock order/ticket/PNR evidence",
            "evidence_only": True,
            "real_ticket_issued": False,
            "real_booking_created": False,
            "payment_created": False,
            "authority_transferred": False,
        },
    )
    return tuple({**row, "transaction_id": TRANSACTION_ID, "real_world_effects_count": 0} for row in rows)


def _final_tri_party_mock_summary(
    fixtures: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    final_summary = fixtures["ClientFinalTravelSummaryV01"]
    order_receipt = fixtures["AirlineOrderCreatedReceiptV01"]
    mock_pnr = fixtures["MockPNRV01"]
    return {
        "summary_id": f"final_tri_party_mock_summary:{TRANSACTION_ID}",
        "transaction_id": TRANSACTION_ID,
        "final_status": STATUS_PASS,
        "client_view_status": "mock_ticket_evidence_received_no_real_travel_booking",
        "airline_view_status": "mock_order_ticket_pnr_evidence_created",
        "bank_view_status": "mock_payment_authorized_not_settled",
        "selected_offer_id": final_summary["selected_offer_id"],
        "offer_hold_receipt_id": final_summary["offer_hold_receipt_id"],
        "payment_authorization_receipt_id": final_summary[
            "payment_authorization_receipt_id"
        ],
        "payment_authorization_ref_id": final_summary[
            "payment_authorization_ref_id"
        ],
        "payment_status_receipt_id": final_summary["payment_status_receipt_id"],
        "order_created_receipt_id": order_receipt["receipt_id"],
        "mock_ticket_receipt_id": final_summary["mock_ticket_receipt_id"],
        "mock_purchase_receipt_id": final_summary["mock_purchase_receipt_id"],
        "mock_pnr": mock_pnr["pnr"],
        "receipts_evidence_only": True,
        "authority_transferred_between_roots": False,
        "client_root_issued_ticket": False,
        "airline_root_authorized_payment": False,
        "bank_root_created_ticket": False,
        "real_airline_api_called": False,
        "real_bank_api_called": False,
        "real_gds_api_called": False,
        "real_payment_executed": False,
        "real_settlement_executed": False,
        "real_ticket_issued": False,
        "real_booking_created": False,
        "provider_called": False,
        "network_used": False,
        "gemini_called": False,
        "real_world_effects_count": 0,
    }


def _artifact_ref(artifact_name: str, fixtures: Mapping[str, Mapping[str, Any]]) -> str:
    fixture = fixtures.get(artifact_name)
    if fixture is None:
        return f"artifact_ref:{artifact_name}"
    return str(
        fixture.get("receipt_id")
        or fixture.get("summary_id")
        or fixture.get("packet_id")
        or fixture.get("response_id")
        or fixture.get("offer_id")
        or fixture.get("approval_id")
        or fixture.get("intent_id")
        or fixture.get("consent_id")
        or fixture.get("pnr")
        or f"artifact_ref:{artifact_name}"
    )


def _build_airline_ticket_purchase_corridor_fixture_bundle_v01(
    report: Mapping[str, Any],
) -> dict[str, Any]:
    values = _airline_ticket_purchase_corridor_projection_values(report)
    offer_packet = replace(
        corridor_contracts.build_valid_airline_offer_packet_v01(),
        packet_id=values["offer_packet_id"],
        transaction_id=values["offer_transaction_id"],
        created_by=values["airline_root_id"],
        root_owner=values["airline_root_id"],
        airline_root_id=values["airline_root_id"],
        offer_id=values["offer_id"],
        passenger_ref=values["offer_passenger_ref"],
        route_ref=values["offer_route_ref"],
        departure_date=values["departure_date"],
        return_date=values["return_date"],
        amount=values["offer_amount"],
        currency=values["offer_currency"],
        ttl_seconds=values["offer_ttl_seconds"],
    )
    hold_packet = replace(
        corridor_contracts.build_valid_airline_hold_commit_packet_v01(),
        packet_id=values["hold_packet_id"],
        transaction_id=values["hold_packet_transaction_id"],
        parent_offer_packet_id=offer_packet.packet_id,
        created_by=values["airline_root_id"],
        root_owner=values["airline_root_id"],
        airline_root_id=values["airline_root_id"],
        offer_id=values["hold_offer_id"],
        hold_id=values["hold_id"],
        passenger_ref=values["hold_passenger_ref"],
        route_ref=values["hold_route_ref"],
        amount=values["hold_amount"],
        currency=values["hold_currency"],
        ttl_seconds=values["hold_ttl_seconds"],
        expired=values["hold_expired"],
        idempotency_key=values["hold_idempotency_key"],
    )
    hold_receipt = replace(
        corridor_contracts.build_valid_airline_offer_hold_receipt_v01(),
        receipt_id=values["offer_hold_receipt_id"],
        transaction_id=values["hold_receipt_transaction_id"],
        source_hold_packet_id=hold_packet.packet_id,
        source_idempotency_key=hold_packet.idempotency_key,
        created_by=values["offer_hold_receipt_created_by"],
        root_owner=values["offer_hold_receipt_root_owner"],
        offer_id=values["hold_receipt_offer_id"],
        hold_id=values["hold_receipt_hold_id"],
        passenger_ref=values["hold_receipt_passenger_ref"],
        route_ref=values["hold_receipt_route_ref"],
        amount=values["hold_receipt_amount"],
        currency=values["hold_receipt_currency"],
        evidence_only=values["offer_hold_receipt_evidence_only"],
        payment_permission_created=values[
            "offer_hold_receipt_payment_permission_created"
        ],
        ticket_permission_created=values[
            "offer_hold_receipt_ticket_permission_created"
        ],
    )
    human_approval = replace(
        corridor_contracts.build_valid_human_approval_evidence_ref_v01(),
        approval_ref=values["client_purchase_approval_ref"],
        transaction_id=values["client_approval_transaction_id"],
        client_root_id=values["client_root_id"],
        selected_offer_id=values["client_selected_offer_id"],
        max_amount=values["client_max_amount"],
        currency=values["client_currency"],
        passenger_ref=values["client_passenger_ref"],
        evidence_only=values["client_approval_evidence_only"],
    )
    purchase_intent = replace(
        corridor_contracts.build_valid_client_purchase_intent_v01(),
        intent_id=values["client_purchase_intent_id"],
        transaction_id=values["client_approval_transaction_id"],
        created_by=values["client_root_id"],
        root_owner=values["client_root_id"],
        client_root_id=values["client_root_id"],
        source_human_approval_ref=human_approval.approval_ref,
        selected_offer_packet_id=offer_packet.packet_id,
        required_offer_hold_receipt_id=hold_receipt.receipt_id,
        offer_id=values["client_selected_offer_id"],
        hold_id=values["client_hold_id"],
        passenger_ref=values["client_passenger_ref"],
        route_ref=values["client_route_ref"],
        max_amount=values["client_max_amount"],
        selected_amount=values["client_selected_amount"],
        currency=values["client_currency"],
    )
    authorization_ref = replace(
        corridor_contracts.build_valid_bank_payment_authorization_ref_v01(),
        authorization_ref_id=values["payment_authorization_ref_id"],
        transaction_id=values["payment_authorization_transaction_id"],
        created_by=values["bank_root_id"],
        root_owner=values["bank_root_id"],
        bank_root_id=values["bank_root_id"],
        source_payment_receipt_id=values["payment_authorization_receipt_id"],
        source_purchase_intent_id=purchase_intent.intent_id,
        merchant_ref=values["merchant_ref"],
        offer_id=values["payment_offer_id"],
        hold_id=values["payment_hold_id"],
        passenger_ref=values["payment_passenger_ref"],
        route_ref=values["payment_route_ref"],
        amount=values["payment_amount"],
        currency=values["payment_currency"],
        ttl_seconds=values["payment_ttl_seconds"],
        expired=values["payment_expired"],
        idempotency_key=values["payment_idempotency_key"],
        evidence_only=values["payment_authorization_evidence_only"],
        real_payment_executed=values["payment_real_payment_executed"],
        ticket_permission_created=values["payment_ticket_permission_created"],
    )
    ticket_issue_intent = replace(
        corridor_contracts.build_valid_airline_ticket_issue_intent_v01(),
        intent_id=values["ticket_issue_intent_id"],
        transaction_id=values["ticket_issue_transaction_id"],
        created_by=values["airline_root_id"],
        root_owner=values["airline_root_id"],
        airline_root_id=values["airline_root_id"],
        required_offer_packet_id=offer_packet.packet_id,
        required_hold_packet_id=hold_packet.packet_id,
        required_offer_hold_receipt_id=hold_receipt.receipt_id,
        required_client_purchase_intent_id=purchase_intent.intent_id,
        required_payment_authorization_ref_id=authorization_ref.authorization_ref_id,
        offer_id=values["ticket_offer_id"],
        hold_id=values["ticket_hold_id"],
        passenger_ref=values["ticket_passenger_ref"],
        route_ref=values["ticket_route_ref"],
        amount=values["ticket_amount"],
        currency=values["ticket_currency"],
        merchant_ref=values["ticket_merchant_ref"],
        ttl_seconds=values["ticket_ttl_seconds"],
        idempotency_key=values["ticket_idempotency_key"],
    )
    ticket_receipt = replace(
        corridor_contracts.build_valid_mock_ticket_receipt_v01(),
        receipt_id=values["mock_ticket_receipt_id"],
        transaction_id=values["mock_ticket_transaction_id"],
        source_ticket_issue_intent_id=ticket_issue_intent.intent_id,
        source_idempotency_key=ticket_issue_intent.idempotency_key,
        created_by=values["mock_ticket_receipt_created_by"],
        root_owner=values["mock_ticket_receipt_root_owner"],
        mock_ticket_id=values["mock_ticket_id"],
        mock_pnr=values["mock_pnr"],
        offer_id=values["mock_ticket_offer_id"],
        hold_id=values["mock_ticket_hold_id"],
        passenger_ref=values["mock_ticket_passenger_ref"],
        route_ref=values["mock_ticket_route_ref"],
        amount=values["mock_ticket_amount"],
        currency=values["mock_ticket_currency"],
        evidence_only=values["mock_ticket_evidence_only"],
        real_ticket=values["mock_ticket_real_ticket"],
        real_booking=values["mock_ticket_real_booking"],
        payment_created=values["mock_ticket_payment_created"],
        future_payment_permission_created=values[
            "mock_ticket_future_payment_permission_created"
        ],
    )
    purchase_receipt = replace(
        corridor_contracts.build_valid_mock_purchase_receipt_v01(),
        receipt_id=values["mock_purchase_receipt_id"],
        transaction_id=values["mock_purchase_transaction_id"],
        source_client_purchase_intent_id=purchase_intent.intent_id,
        source_payment_authorization_ref_id=authorization_ref.authorization_ref_id,
        source_mock_ticket_receipt_id=ticket_receipt.receipt_id,
        client_root_id=values["client_root_id"],
        airline_root_id=values["airline_root_id"],
        bank_root_id=values["bank_root_id"],
        created_by=values["mock_purchase_receipt_created_by"],
        root_owner=values["mock_purchase_receipt_root_owner"],
        evidence_only=values["mock_purchase_evidence_only"],
        real_payment_executed=values["mock_purchase_real_payment_executed"],
        real_ticket_issued=values["mock_purchase_real_ticket_issued"],
        real_booking_created=values["mock_purchase_real_booking_created"],
    )
    return {
        "airline_offer_hold_gate": replace(
            corridor_contracts.build_valid_airline_root_offer_hold_gate_v01(),
            transaction_id=values["offer_hold_gate_transaction_id"],
            root_id=values["airline_root_id"],
        ),
        "offer_packet": offer_packet,
        "hold_packet": hold_packet,
        "hold_receipt": hold_receipt,
        "client_purchase_gate": replace(
            corridor_contracts.build_valid_client_root_purchase_intent_gate_v01(),
            transaction_id=values["client_gate_transaction_id"],
            root_id=values["client_root_id"],
        ),
        "human_approval": human_approval,
        "purchase_intent": purchase_intent,
        "bank_gate": replace(
            corridor_contracts.build_valid_bank_root_payment_authorization_gate_v01(),
            transaction_id=values["bank_gate_transaction_id"],
            root_id=values["bank_root_id"],
        ),
        "authorization_ref": authorization_ref,
        "airline_ticket_gate": replace(
            corridor_contracts.build_valid_airline_root_ticket_issue_gate_v01(),
            transaction_id=values["ticket_gate_transaction_id"],
            root_id=values["airline_root_id"],
        ),
        "ticket_issue_intent": ticket_issue_intent,
        "ticket_receipt": ticket_receipt,
        "completion_gate": replace(
            corridor_contracts.build_valid_client_root_completion_gate_v01(),
            transaction_id=values["completion_gate_transaction_id"],
            root_id=values["client_root_id"],
        ),
        "purchase_receipt": purchase_receipt,
    }


def _airline_ticket_purchase_corridor_projection_values(
    report: Mapping[str, Any],
) -> dict[str, Any]:
    fixtures = report["mock_protocol_fixtures"]
    transaction_identity = report["transaction_identity"]
    travel_intent = report["travel_intent"]
    offer_request = fixtures["AirlineOfferRequestV01"]
    offer_candidate = fixtures["AirlineOfferCandidateV01"]
    offer_response = fixtures["AirlineOfferResponseV01"]
    hold_packet = fixtures["AirlineOfferHoldCommitPacketV01"]
    hold_receipt = fixtures["AirlineOfferHoldReceiptV01"]
    client_approval = fixtures["ClientPurchaseApprovalEvidenceV01"]
    bank_packet = fixtures["BankPaymentAuthorizationCommitPacketV01"]
    bank_receipt = fixtures["BankPaymentAuthorizationReceiptV01"]
    ticket_packet = fixtures["AirlineTicketIssueCommitPacketV01"]
    ticket_receipt = fixtures["MockTicketReceiptV01"]
    purchase_receipt = fixtures["MockPurchaseReceiptV01"]
    final_summary = fixtures["ClientFinalTravelSummaryV01"]
    return {
        "transaction_id": report["transaction_id"],
        "client_root_id": transaction_identity["client_root_id"],
        "airline_root_id": transaction_identity["airline_root_id"],
        "bank_root_id": transaction_identity["bank_root_id"],
        "offer_hold_gate_transaction_id": report["airline_offer_hold_sandbox"][
            "transaction_id"
        ],
        "client_gate_transaction_id": report["client_purchase_orchestration"][
            "transaction_id"
        ],
        "bank_gate_transaction_id": report["bank_payment_authorization_sandbox"][
            "transaction_id"
        ],
        "ticket_gate_transaction_id": report["airline_ticket_issue_mock_corridor"][
            "transaction_id"
        ],
        "completion_gate_transaction_id": final_summary["transaction_id"],
        "offer_packet_id": offer_response["response_id"],
        "offer_transaction_id": offer_candidate["transaction_id"],
        "offer_id": offer_candidate["offer_id"],
        "offer_passenger_ref": offer_request["passenger_ref"],
        "offer_route_ref": offer_request["route_ref"],
        "departure_date": travel_intent["depart_date"],
        "return_date": travel_intent["return_date"],
        "offer_amount": offer_candidate["price_amount"],
        "offer_currency": offer_candidate["currency"],
        "offer_ttl_seconds": offer_candidate["offer_ttl_seconds"],
        "hold_packet_id": hold_packet["packet_id"],
        "hold_packet_transaction_id": hold_packet["transaction_id"],
        "hold_offer_id": hold_packet["allowed_offer_id"],
        "hold_id": hold_packet["allowed_hold_id"],
        "hold_passenger_ref": hold_packet["allowed_passenger_ref"],
        "hold_route_ref": hold_packet["allowed_route_ref"],
        "hold_amount": hold_packet["allowed_amount"],
        "hold_currency": hold_packet["currency"],
        "hold_ttl_seconds": hold_packet["ttl_seconds"],
        "hold_expired": hold_packet["offer_hold_expired"],
        "hold_idempotency_key": hold_packet["idempotency_key"],
        "offer_hold_receipt_id": hold_receipt["receipt_id"],
        "hold_receipt_transaction_id": hold_receipt["transaction_id"],
        "offer_hold_receipt_created_by": hold_receipt["created_by"],
        "offer_hold_receipt_root_owner": hold_receipt["root_owner"],
        "hold_receipt_offer_id": hold_receipt["offer_id"],
        "hold_receipt_hold_id": hold_receipt["hold_id"],
        "hold_receipt_passenger_ref": hold_receipt["passenger_ref"],
        "hold_receipt_route_ref": hold_receipt["route_ref"],
        "hold_receipt_amount": hold_receipt["amount"],
        "hold_receipt_currency": hold_receipt["currency"],
        "offer_hold_receipt_evidence_only": hold_receipt["evidence_only"],
        "offer_hold_receipt_payment_permission_created": hold_receipt[
            "payment_permission_created"
        ],
        "offer_hold_receipt_ticket_permission_created": hold_receipt[
            "ticket_permission_created"
        ],
        "client_purchase_approval_ref": client_approval["approval_id"],
        "client_purchase_intent_id": client_approval["client_purchase_intent_id"],
        "client_approval_transaction_id": client_approval["transaction_id"],
        "client_selected_offer_id": client_approval["selected_offer_id"],
        "client_hold_id": client_approval["hold_id"],
        "client_passenger_ref": client_approval["passenger_ref"],
        "client_route_ref": client_approval["route_ref"],
        "client_selected_amount": client_approval["selected_amount"],
        "client_max_amount": client_approval["max_price_amount"],
        "client_currency": client_approval["currency"],
        "client_approval_evidence_only": client_approval["evidence_only"],
        "payment_authorization_receipt_id": bank_receipt["receipt_id"],
        "payment_authorization_ref_id": bank_receipt[
            "payment_authorization_ref_id"
        ],
        "payment_authorization_transaction_id": bank_receipt["transaction_id"],
        "merchant_ref": bank_receipt["merchant_ref"],
        "payment_offer_id": bank_receipt["offer_id"],
        "payment_hold_id": bank_receipt["hold_id"],
        "payment_passenger_ref": bank_receipt["passenger_ref"],
        "payment_route_ref": bank_receipt["route_ref"],
        "payment_amount": bank_receipt["authorized_amount"],
        "payment_currency": bank_receipt["currency"],
        "payment_ttl_seconds": bank_packet["ttl_seconds"],
        "payment_expired": bank_receipt["payment_authorization_expired"],
        "payment_idempotency_key": bank_packet["idempotency_key"],
        "payment_authorization_evidence_only": bank_receipt["evidence_only"],
        "payment_real_payment_executed": bank_receipt["real_payment_executed"],
        "payment_ticket_permission_created": bank_receipt["ticket_created"],
        "ticket_issue_intent_id": ticket_packet["packet_id"],
        "ticket_issue_transaction_id": ticket_packet["transaction_id"],
        "ticket_offer_id": ticket_packet["allowed_offer_id"],
        "ticket_hold_id": ticket_packet["allowed_hold_id"],
        "ticket_passenger_ref": ticket_packet["allowed_passenger_ref"],
        "ticket_route_ref": ticket_packet["allowed_route_ref"],
        "ticket_amount": ticket_packet["allowed_amount"],
        "ticket_currency": ticket_packet["currency"],
        "ticket_merchant_ref": ticket_packet["merchant_ref"],
        "ticket_ttl_seconds": ticket_packet["ttl_seconds"],
        "ticket_idempotency_key": ticket_packet["idempotency_key"],
        "mock_ticket_receipt_id": ticket_receipt["receipt_id"],
        "mock_ticket_transaction_id": ticket_receipt["transaction_id"],
        "mock_ticket_receipt_created_by": ticket_receipt["created_by"],
        "mock_ticket_receipt_root_owner": ticket_receipt["root_owner"],
        "mock_ticket_id": ticket_receipt["mock_ticket_id"],
        "mock_pnr": ticket_receipt["mock_pnr"],
        "mock_ticket_offer_id": ticket_receipt["offer_id"],
        "mock_ticket_hold_id": ticket_receipt["hold_id"],
        "mock_ticket_passenger_ref": ticket_receipt["passenger_ref"],
        "mock_ticket_route_ref": ticket_receipt["route_ref"],
        "mock_ticket_amount": ticket_receipt["amount"],
        "mock_ticket_currency": ticket_receipt["currency"],
        "mock_ticket_evidence_only": ticket_receipt["evidence_only"],
        "mock_ticket_real_ticket": ticket_receipt["real_ticket"],
        "mock_ticket_real_booking": ticket_receipt[
            "real_travel_booking_created"
        ],
        "mock_ticket_payment_created": ticket_receipt["payment_created"],
        "mock_ticket_future_payment_permission_created": ticket_receipt[
            "future_payment_permission_created"
        ],
        "mock_purchase_receipt_id": purchase_receipt["receipt_id"],
        "mock_purchase_transaction_id": purchase_receipt["transaction_id"],
        "mock_purchase_receipt_created_by": purchase_receipt["created_by"],
        "mock_purchase_receipt_root_owner": purchase_receipt["root_owner"],
        "mock_purchase_evidence_only": purchase_receipt["evidence_only"],
        "mock_purchase_real_payment_executed": purchase_receipt[
            "real_payment_executed"
        ],
        "mock_purchase_real_ticket_issued": purchase_receipt["real_ticket_issued"],
        "mock_purchase_real_booking_created": purchase_receipt[
            "real_booking_created"
        ],
        "client_final_summary_id": final_summary["summary_id"],
        "client_final_mock_purchase_receipt_id": final_summary[
            "mock_purchase_receipt_id"
        ],
    }


def _iter_transaction_ids_from_value(value: Any) -> tuple[str, ...]:
    transaction_ids: list[str] = []
    if isinstance(value, Mapping):
        if isinstance(value.get("transaction_id"), str):
            transaction_ids.append(value["transaction_id"])
        for item in value.values():
            transaction_ids.extend(_iter_transaction_ids_from_value(item))
    elif isinstance(value, (tuple, list)):
        for item in value:
            transaction_ids.extend(_iter_transaction_ids_from_value(item))
    elif hasattr(value, "transaction_id"):
        transaction_id = getattr(value, "transaction_id")
        if isinstance(transaction_id, str):
            transaction_ids.append(transaction_id)
    return tuple(transaction_ids)


def _airline_ticket_purchase_corridor_transaction_binding_summary_v01(
    report: Mapping[str, Any],
    fixture_bundle: Mapping[str, Any],
    corridor_report: corridor_runtime.AirlineTicketPurchaseCorridorRunReportV01,
) -> dict[str, Any]:
    transaction_ids: list[str] = []
    transaction_ids.extend(_iter_transaction_ids_from_value(report))
    transaction_ids.extend(_iter_transaction_ids_from_value(tuple(fixture_bundle.values())))
    transaction_ids.append(corridor_report.transaction_id)
    transaction_ids.extend(phase.transaction_id for phase in corridor_report.phase_results)
    transaction_ids.extend(
        transition.transaction_id for transition in corridor_report.transitions
    )
    non_empty_transaction_ids = tuple(
        transaction_id for transaction_id in transaction_ids if transaction_id
    )
    unique_transaction_ids = tuple(sorted(set(non_empty_transaction_ids)))
    source_transaction_id = report["transaction_id"]
    all_transaction_ids_match = unique_transaction_ids == (source_transaction_id,)
    return {
        "source_transaction_id": source_transaction_id,
        "unique_transaction_ids": unique_transaction_ids,
        "unique_transaction_id_count": len(unique_transaction_ids),
        "all_transaction_ids_match": all_transaction_ids_match,
    }


def _airline_ticket_purchase_corridor_binding_matrix_v01(
    report: Mapping[str, Any],
    fixture_bundle: Mapping[str, Any],
    corridor_report: corridor_runtime.AirlineTicketPurchaseCorridorRunReportV01,
) -> tuple[dict[str, Any], ...]:
    values = _airline_ticket_purchase_corridor_projection_values(report)
    transaction_binding = (
        _airline_ticket_purchase_corridor_transaction_binding_summary_v01(
            report,
            fixture_bundle,
            corridor_report,
        )
    )

    def binding(
        binding_id: str,
        source_report_path: str,
        source_value: Any,
        corridor_artifact_type: str,
        corridor_field: str,
        projected_value: Any,
    ) -> dict[str, Any]:
        return {
            "binding_id": binding_id,
            "source_report_path": source_report_path,
            "source_value": source_value,
            "corridor_artifact_type": corridor_artifact_type,
            "corridor_field": corridor_field,
            "projected_value": projected_value,
            "values_match": source_value == projected_value,
            "transaction_id": values["transaction_id"],
            "raw_secret_used": False,
            "authority_transferred": False,
        }

    return (
        {
            **binding(
                "transaction_id",
                "transaction_id",
                transaction_binding["source_transaction_id"],
                "SourceProjectionAndCorridorV01",
                "all_transaction_ids",
                transaction_binding["unique_transaction_ids"],
            ),
            "values_match": transaction_binding["all_transaction_ids_match"],
            "unique_transaction_id_count": transaction_binding[
                "unique_transaction_id_count"
            ],
            "all_transaction_ids_match": transaction_binding[
                "all_transaction_ids_match"
            ],
        },
        binding(
            "offer_id",
            "mock_protocol_fixtures.AirlineOfferCandidateV01.offer_id",
            values["offer_id"],
            "AirlineOfferPacketV01",
            "offer_id",
            fixture_bundle["offer_packet"].offer_id,
        ),
        binding(
            "hold_id",
            "mock_protocol_fixtures.AirlineOfferHoldCommitPacketV01.allowed_hold_id",
            values["hold_id"],
            "AirlineHoldCommitPacketV01",
            "hold_id",
            fixture_bundle["hold_packet"].hold_id,
        ),
        binding(
            "passenger_ref",
            "mock_protocol_fixtures.AirlineOfferRequestV01.passenger_ref",
            values["offer_passenger_ref"],
            "AirlineOfferPacketV01",
            "passenger_ref",
            fixture_bundle["offer_packet"].passenger_ref,
        ),
        binding(
            "route_ref",
            "mock_protocol_fixtures.AirlineOfferRequestV01.route_ref",
            values["offer_route_ref"],
            "AirlineOfferPacketV01",
            "route_ref",
            fixture_bundle["offer_packet"].route_ref,
        ),
        binding(
            "amount",
            "mock_protocol_fixtures.AirlineOfferCandidateV01.price_amount",
            values["offer_amount"],
            "AirlineOfferPacketV01",
            "amount",
            fixture_bundle["offer_packet"].amount,
        ),
        binding(
            "currency",
            "mock_protocol_fixtures.AirlineOfferCandidateV01.currency",
            values["offer_currency"],
            "AirlineOfferPacketV01",
            "currency",
            fixture_bundle["offer_packet"].currency,
        ),
        binding(
            "merchant_ref",
            "mock_protocol_fixtures.BankPaymentAuthorizationReceiptV01.merchant_ref",
            values["merchant_ref"],
            "BankPaymentAuthorizationRefV01",
            "merchant_ref",
            fixture_bundle["authorization_ref"].merchant_ref,
        ),
        binding(
            "offer_hold_receipt_id",
            "mock_protocol_fixtures.AirlineOfferHoldReceiptV01.receipt_id",
            values["offer_hold_receipt_id"],
            "AirlineOfferHoldReceiptV01",
            "receipt_id",
            fixture_bundle["hold_receipt"].receipt_id,
        ),
        binding(
            "offer_hold_receipt_created_by",
            "mock_protocol_fixtures.AirlineOfferHoldReceiptV01.created_by",
            values["offer_hold_receipt_created_by"],
            "AirlineOfferHoldReceiptV01",
            "created_by",
            fixture_bundle["hold_receipt"].created_by,
        ),
        binding(
            "offer_hold_receipt_root_owner",
            "mock_protocol_fixtures.AirlineOfferHoldReceiptV01.root_owner",
            values["offer_hold_receipt_root_owner"],
            "AirlineOfferHoldReceiptV01",
            "root_owner",
            fixture_bundle["hold_receipt"].root_owner,
        ),
        binding(
            "client_purchase_approval_ref",
            "mock_protocol_fixtures.ClientPurchaseApprovalEvidenceV01.approval_id",
            values["client_purchase_approval_ref"],
            "AirlinePurchaseApprovalEvidenceRefV01",
            "approval_ref",
            fixture_bundle["human_approval"].approval_ref,
        ),
        binding(
            "client_purchase_intent_id",
            (
                "mock_protocol_fixtures.ClientPurchaseApprovalEvidenceV01."
                "client_purchase_intent_id"
            ),
            values["client_purchase_intent_id"],
            "ClientPurchaseIntentV01",
            "intent_id",
            fixture_bundle["purchase_intent"].intent_id,
        ),
        binding(
            "purchase_intent_source_human_approval_ref",
            "mock_protocol_fixtures.ClientPurchaseApprovalEvidenceV01.approval_id",
            values["client_purchase_approval_ref"],
            "ClientPurchaseIntentV01",
            "source_human_approval_ref",
            fixture_bundle["purchase_intent"].source_human_approval_ref,
        ),
        binding(
            "payment_authorization_receipt_id",
            "mock_protocol_fixtures.BankPaymentAuthorizationReceiptV01.receipt_id",
            values["payment_authorization_receipt_id"],
            "BankPaymentAuthorizationRefV01",
            "source_payment_receipt_id",
            fixture_bundle["authorization_ref"].source_payment_receipt_id,
        ),
        binding(
            "payment_authorization_ref_id",
            (
                "mock_protocol_fixtures.BankPaymentAuthorizationReceiptV01."
                "payment_authorization_ref_id"
            ),
            values["payment_authorization_ref_id"],
            "BankPaymentAuthorizationRefV01",
            "authorization_ref_id",
            fixture_bundle["authorization_ref"].authorization_ref_id,
        ),
        binding(
            "authorization_ref_source_receipt_id",
            "mock_protocol_fixtures.BankPaymentAuthorizationReceiptV01.receipt_id",
            values["payment_authorization_receipt_id"],
            "BankPaymentAuthorizationRefV01",
            "source_payment_receipt_id",
            fixture_bundle["authorization_ref"].source_payment_receipt_id,
        ),
        binding(
            "ticket_issue_intent_id",
            "mock_protocol_fixtures.AirlineTicketIssueCommitPacketV01.packet_id",
            values["ticket_issue_intent_id"],
            "AirlineTicketIssueIntentV01",
            "intent_id",
            fixture_bundle["ticket_issue_intent"].intent_id,
        ),
        binding(
            "mock_ticket_receipt_id",
            "mock_protocol_fixtures.MockTicketReceiptV01.receipt_id",
            values["mock_ticket_receipt_id"],
            "MockTicketReceiptV01",
            "receipt_id",
            fixture_bundle["ticket_receipt"].receipt_id,
        ),
        binding(
            "mock_ticket_receipt_created_by",
            "mock_protocol_fixtures.MockTicketReceiptV01.created_by",
            values["mock_ticket_receipt_created_by"],
            "MockTicketReceiptV01",
            "created_by",
            fixture_bundle["ticket_receipt"].created_by,
        ),
        binding(
            "mock_ticket_receipt_root_owner",
            "mock_protocol_fixtures.MockTicketReceiptV01.root_owner",
            values["mock_ticket_receipt_root_owner"],
            "MockTicketReceiptV01",
            "root_owner",
            fixture_bundle["ticket_receipt"].root_owner,
        ),
        binding(
            "mock_purchase_receipt_id",
            "mock_protocol_fixtures.MockPurchaseReceiptV01.receipt_id",
            values["mock_purchase_receipt_id"],
            "MockPurchaseReceiptV01",
            "receipt_id",
            fixture_bundle["purchase_receipt"].receipt_id,
        ),
        binding(
            "mock_purchase_receipt_created_by",
            "mock_protocol_fixtures.MockPurchaseReceiptV01.created_by",
            values["mock_purchase_receipt_created_by"],
            "MockPurchaseReceiptV01",
            "created_by",
            fixture_bundle["purchase_receipt"].created_by,
        ),
        binding(
            "mock_purchase_receipt_root_owner",
            "mock_protocol_fixtures.MockPurchaseReceiptV01.root_owner",
            values["mock_purchase_receipt_root_owner"],
            "MockPurchaseReceiptV01",
            "root_owner",
            fixture_bundle["purchase_receipt"].root_owner,
        ),
        binding(
            "client_final_summary_mock_purchase_receipt_id",
            "mock_protocol_fixtures.ClientFinalTravelSummaryV01.mock_purchase_receipt_id",
            values["client_final_mock_purchase_receipt_id"],
            "ClientFinalTravelSummaryV01",
            "mock_purchase_receipt_id",
            fixture_bundle["purchase_receipt"].receipt_id,
        ),
        binding(
            "mock_pnr",
            "mock_protocol_fixtures.MockTicketReceiptV01.mock_pnr",
            values["mock_pnr"],
            "MockTicketReceiptV01",
            "mock_pnr",
            fixture_bundle["ticket_receipt"].mock_pnr,
        ),
    )


def _airline_ticket_purchase_corridor_integration_summary(
    report: Mapping[str, Any],
    fixture_bundle: Mapping[str, Any],
    corridor_report: corridor_runtime.AirlineTicketPurchaseCorridorRunReportV01,
    corridor_public_validation_accepted: bool,
    binding_matrix: tuple[dict[str, Any], ...],
    corridor_collector_invocation_count: int,
    contract_context: (
        corridor_contracts.AirlineTicketPurchaseContractContextV01 | None
    ) = None,
) -> dict[str, Any]:
    fixture_bundle_accepted, _ = (
        corridor_runtime.validate_airline_ticket_purchase_corridor_fixture_bundle_v01(
            fixture_bundle,
            contract_context=contract_context,
        )
    )
    fixture_report_binding_accepted, _ = (
        corridor_runtime
        .validate_airline_ticket_purchase_corridor_report_against_fixture_bundle_v01(
            fixture_bundle,
            corridor_report,
            contract_context=contract_context,
        )
    )
    binding_match_count = sum(1 for row in binding_matrix if row["values_match"])
    transaction_binding = (
        _airline_ticket_purchase_corridor_transaction_binding_summary_v01(
            report,
            fixture_bundle,
            corridor_report,
        )
    )
    existing_runner_artifacts_projected = (
        fixture_bundle_accepted
        and binding_match_count == len(binding_matrix)
        and corridor_public_validation_accepted
        and fixture_report_binding_accepted
    )
    parallel_fixture_transaction_created = (
        transaction_binding["unique_transaction_id_count"] != 1
        or not transaction_binding["all_transaction_ids_match"]
    )
    duplicate_corridor_execution_count = max(
        0,
        corridor_collector_invocation_count - 1,
    )
    authority_transferred = (
        any(phase.authority_transferred for phase in corridor_report.phase_results)
        or any(
            transition.authority_transferred
            for transition in corridor_report.transitions
        )
        or any(row["authority_transferred"] for row in binding_matrix)
        or any(
            not row.get("boundary_preserved", True)
            or row.get("violation_count", 0) != 0
            for row in report.get("root_boundary_matrix", ())
        )
        or any(
            row.get("authority_transferred") is True
            for row in report.get("cross_root_evidence_routing_matrix", ())
        )
        or report.get("final_tri_party_mock_summary", {}).get(
            "authority_transferred_between_roots",
        )
        is True
    )
    return {
        "integration_status": (
            STATUS_PASS
            if (
                corridor_report.final_status == corridor_runtime.STATUS_PASS
                and corridor_public_validation_accepted
                and fixture_report_binding_accepted
                and existing_runner_artifacts_projected
                and not parallel_fixture_transaction_created
                and duplicate_corridor_execution_count == 0
                and not authority_transferred
            )
            else STATUS_FAIL_CLOSED
        ),
        "transaction_id": TRANSACTION_ID,
        "source_runner_id": RUN_ID,
        "corridor_run_id": corridor_report.run_id,
        "corridor_slice_id": corridor_report.slice_id,
        "corridor_final_status": corridor_report.final_status,
        "corridor_public_validation_accepted": corridor_public_validation_accepted,
        "corridor_report_bound_to_projected_fixtures": (
            fixture_report_binding_accepted
        ),
        "five_root_centered_phases_observed": len(corridor_report.phase_results) == 5,
        "existing_runner_artifacts_projected": existing_runner_artifacts_projected,
        "parallel_fixture_transaction_created": parallel_fixture_transaction_created,
        "duplicate_corridor_execution_count": duplicate_corridor_execution_count,
        "unique_transaction_id_count": transaction_binding[
            "unique_transaction_id_count"
        ],
        "all_transaction_ids_match": transaction_binding[
            "all_transaction_ids_match"
        ],
        "runtime_packets_created_count": corridor_report.counter_table[
            "runtime_packets_created_count"
        ],
        "runtime_receipts_created_count": corridor_report.counter_table[
            "runtime_receipts_created_count"
        ],
        "adapter_execution_count": corridor_report.counter_table[
            "adapter_execution_count"
        ],
        "authority_transferred": authority_transferred,
        "real_world_effects_count": corridor_report.counter_table[
            "real_world_effects_count"
        ],
        "next_gate": "airline_ticket_purchase_corridor_v01_slice_e_audit_and_human_story",
    }


def _ledger_expected_source_refs(
    *,
    source_bundle_id: str,
    semantic_causal_run: causal_runtime.AirlineSemanticCausalRunReportV01,
    corridor_report: corridor_runtime.AirlineTicketPurchaseCorridorRunReportV01,
) -> ledger_contracts.AirlineTransactionArtifactLedgerExpectedSourceRefsV01:
    return ledger_contracts.AirlineTransactionArtifactLedgerExpectedSourceRefsV01(
        source_run_ref=f"source_run:{source_bundle_id}",
        source_causal_report_ref=(
            f"source_causal_report:{semantic_causal_run.run_id}:"
            f"{semantic_causal_run.scenario_id}"
        ),
        source_corridor_report_ref=(
            f"source_corridor_report:{corridor_report.run_id}:"
            f"{corridor_report.transaction_id}"
        ),
    )


def _ledger_bsep_projection_source_from_mapping(
    *,
    projection: Mapping[str, Any],
    expected_side: str,
) -> ledger_collector.AirlineTransactionArtifactLedgerBSEPProjectionSourceV01:
    required_string_fields = (
        "projection_id",
        "projection_ref",
        "source_bsep_packet_id",
        "transaction_id",
        "side",
        "validation_status",
    )
    if any(
        type(projection.get(field_name)) is not str
        or not projection.get(field_name)
        for field_name in required_string_fields
    ):
        raise ValueError("bsep_projection_required_field_missing")
    if projection["side"] != expected_side:
        raise ValueError("bsep_projection_side_mismatch")
    for flag_name in (
        "raw_secrets_included",
        "raw_provider_text_included",
        "authority_created",
        "permission_created",
    ):
        if projection.get(flag_name) is not False:
            raise ValueError(f"bsep_projection_forbidden_flag:{flag_name}")
    if projection.get("real_world_effects_count") != 0:
        raise ValueError("bsep_projection_real_effect")
    return ledger_collector.AirlineTransactionArtifactLedgerBSEPProjectionSourceV01(
        projection_id=projection["projection_id"],
        projection_ref=projection["projection_ref"],
        bsep_packet_id=projection["source_bsep_packet_id"],
        transaction_id=projection["transaction_id"],
        side=projection["side"],
        validation_status=projection["validation_status"],
        raw_secrets_included=projection["raw_secrets_included"],
        raw_provider_text_included=projection["raw_provider_text_included"],
        authority_created=projection["authority_created"],
        permission_created=projection["permission_created"],
        real_world_effects_count=projection["real_world_effects_count"],
    )


def _ledger_bsep_projection_sources(
    *,
    semantic_causal_run: causal_runtime.AirlineSemanticCausalRunReportV01,
    bsep_side_projections: Mapping[str, Any] | None,
) -> dict[str, ledger_collector.AirlineTransactionArtifactLedgerBSEPProjectionSourceV01]:
    if bsep_side_projections is None:
        raise ValueError("bsep_projection_sources_required")
    keys_and_sides = (
        ("client_bsep_projection", ledger_collector.SIDE_CLIENT),
        ("airline_bsep_projection", ledger_collector.SIDE_AIRLINE),
        ("bank_bsep_projection", ledger_collector.SIDE_BANK),
        ("cross_root_bsep_projection", ledger_collector.SIDE_CROSS_ROOT_ADVISORY),
    )
    result: dict[
        str,
        ledger_collector.AirlineTransactionArtifactLedgerBSEPProjectionSourceV01,
    ] = {}
    packet_ids: set[str] = set()
    for key, expected_side in keys_and_sides:
        source_projection = bsep_side_projections.get(key)
        if isinstance(
            source_projection,
            ledger_collector.AirlineTransactionArtifactLedgerBSEPProjectionSourceV01,
        ):
            projection = source_projection
            if projection.side != expected_side:
                raise ValueError(f"bsep_projection_side_mismatch:{key}")
            if projection.transaction_id != TRANSACTION_ID:
                raise ValueError(f"bsep_projection_transaction_mismatch:{key}")
            if projection.validation_status != ledger_contracts.STATUS_PASS:
                raise ValueError(f"bsep_projection_not_pass:{key}")
            if (
                projection.raw_secrets_included
                or projection.raw_provider_text_included
                or projection.authority_created
                or projection.permission_created
                or projection.real_world_effects_count != 0
            ):
                raise ValueError(f"bsep_projection_forbidden_boundary:{key}")
        elif not isinstance(source_projection, Mapping):
            raise ValueError(f"bsep_projection_missing:{key}")
        else:
            projection = _ledger_bsep_projection_source_from_mapping(
                projection=source_projection,
                expected_side=expected_side,
            )
        packet_ids.add(projection.bsep_packet_id)
        result[key] = projection
    if len(packet_ids) != 1:
        raise ValueError("bsep_projection_packet_mismatch")
    airline_projection = result["airline_bsep_projection"]
    if (
        airline_projection.projection_ref
        != semantic_causal_run.proposer_request.source_bsep_projection_ref
    ):
        raise ValueError("bsep_projection_causal_lineage_mismatch")
    return result


def _ledger_root_final_sources(
    *,
    semantic_causal_run: causal_runtime.AirlineSemanticCausalRunReportV01,
    corridor_execution_result: corridor_runtime.AirlineTicketPurchaseCorridorExecutionResultV01,
) -> dict[str, ledger_collector.AirlineTransactionArtifactLedgerRootFinalSourceV01]:
    suffix = semantic_causal_run.semantic_recommendation_id.rsplit(":", 1)[-1]

    def root_final(
        *,
        final_id: str,
        root_owner: str,
        refs: tuple[str, ...],
    ) -> ledger_collector.AirlineTransactionArtifactLedgerRootFinalSourceV01:
        return ledger_collector.AirlineTransactionArtifactLedgerRootFinalSourceV01(
            final_id=final_id,
            transaction_id=TRANSACTION_ID,
            root_owner=root_owner,
            created_by=root_owner,
            final_status=STATUS_PASS,
            source_artifact_refs=refs,
            authority_created_by_ledger=False,
            permission_created_by_ledger=False,
            real_world_effects_count=0,
        )

    return {
        "client_root_final": root_final(
            final_id=f"client_root_final:{suffix}",
            root_owner=CLIENT_ROOT_ID,
            refs=(
                semantic_causal_run.client_root_decision.decision_id,
                corridor_execution_result.purchase_intent.intent_id,
                corridor_execution_result.mock_purchase_receipt.receipt_id,
            ),
        ),
        "airline_root_final": root_final(
            final_id=f"airline_root_final:{suffix}",
            root_owner=AIRLINE_ROOT_ID,
            refs=(
                semantic_causal_run.airline_root_resolution.resolution_id,
                corridor_execution_result.offer_packet.packet_id,
                corridor_execution_result.hold_packet.packet_id,
                corridor_execution_result.ticket_issue_intent.intent_id,
                corridor_execution_result.mock_ticket_receipt.receipt_id,
            ),
        ),
        "bank_root_final": root_final(
            final_id=f"bank_root_final:{suffix}",
            root_owner=BANK_ROOT_ID,
            refs=(
                corridor_execution_result.payment_authorization_ref.authorization_ref_id,
            ),
        ),
    }


def _build_airline_transaction_artifact_ledger_source_bundle_v01(
    *,
    semantic_causal_run: causal_runtime.AirlineSemanticCausalRunReportV01,
    bsep_side_projections: Mapping[str, Any] | None,
    corridor_execution_result: corridor_runtime.AirlineTicketPurchaseCorridorExecutionResultV01,
    source_bundle_id: str,
) -> ledger_collector.AirlineTransactionArtifactLedgerSourceBundleV01:
    expected_refs = _ledger_expected_source_refs(
        source_bundle_id=source_bundle_id,
        semantic_causal_run=semantic_causal_run,
        corridor_report=corridor_execution_result.report,
    )
    bsep_sources = _ledger_bsep_projection_sources(
        semantic_causal_run=semantic_causal_run,
        bsep_side_projections=bsep_side_projections,
    )
    root_finals = _ledger_root_final_sources(
        semantic_causal_run=semantic_causal_run,
        corridor_execution_result=corridor_execution_result,
    )
    return ledger_collector.AirlineTransactionArtifactLedgerSourceBundleV01(
        source_bundle_id=source_bundle_id,
        transaction_id=TRANSACTION_ID,
        expected_source_refs=expected_refs,
        client_bsep_projection=bsep_sources["client_bsep_projection"],
        airline_bsep_projection=bsep_sources["airline_bsep_projection"],
        bank_bsep_projection=bsep_sources["bank_bsep_projection"],
        cross_root_bsep_projection=bsep_sources["cross_root_bsep_projection"],
        causal_report=semantic_causal_run,
        offer_packet=corridor_execution_result.offer_packet,
        hold_packet=corridor_execution_result.hold_packet,
        hold_receipt=corridor_execution_result.hold_receipt,
        purchase_approval_evidence=(
            corridor_execution_result.purchase_approval_evidence
        ),
        purchase_intent=corridor_execution_result.purchase_intent,
        payment_authorization_ref=(
            corridor_execution_result.payment_authorization_ref
        ),
        ticket_issue_intent=corridor_execution_result.ticket_issue_intent,
        mock_ticket_receipt=corridor_execution_result.mock_ticket_receipt,
        mock_purchase_receipt=corridor_execution_result.mock_purchase_receipt,
        corridor_report=corridor_execution_result.report,
        client_root_final=root_finals["client_root_final"],
        airline_root_final=root_finals["airline_root_final"],
        bank_root_final=root_finals["bank_root_final"],
        source_validation_refs=(
            expected_refs.source_run_ref,
            expected_refs.source_causal_report_ref,
            expected_refs.source_corridor_report_ref,
        ),
        auxiliary_observation_refs=(
            ledger_collector.EXPECTED_AUXILIARY_OBSERVATION_REFS
        ),
    )


ROOT_FINAL_ARTIFACT_TYPES = (
    "ClientRootFinalV01",
    "AirlineRootFinalV01",
    "BankRootFinalV01",
)


class AirlineMockE2EReportV01(dict):
    """JSON-safe public report plus typed local source objects."""


def _json_safe(value: Any) -> Any:
    if is_dataclass(value):
        return {
            field.name: _json_safe(getattr(value, field.name))
            for field in fields(value)
        }
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, MappingABC):
        return {str(key): _json_safe(item) for key, item in value.items()}
    return value


def _publish_report_with_typed_ledger_objects(
    report: dict[str, Any],
    *,
    source_bundle: (
        ledger_collector.AirlineTransactionArtifactLedgerSourceBundleV01 | None
    ),
    source_validation_report: (
        ledger_collector.AirlineTransactionArtifactLedgerSourceValidationReportV01
        | None
    ),
    artifact_ledger: (
        ledger_contracts.AirlineTransactionArtifactLedgerV01 | None
    ),
) -> AirlineMockE2EReportV01:
    published = AirlineMockE2EReportV01(report)
    published._airline_transaction_artifact_ledger_source_bundle_v0_1 = source_bundle
    published._airline_transaction_artifact_ledger_source_validation_v0_1 = (
        source_validation_report
    )
    published._airline_transaction_artifact_ledger_v0_1 = artifact_ledger
    published["airline_transaction_artifact_ledger_source_bundle_v0_1"] = _json_safe(
        source_bundle,
    )
    published["airline_transaction_artifact_ledger_source_validation_v0_1"] = (
        _json_safe(source_validation_report)
    )
    published["airline_transaction_artifact_ledger_v0_1"] = _json_safe(
        artifact_ledger,
    )
    return published


def _typed_airline_transaction_artifact_ledger_source_bundle_from_report(
    report: Mapping[str, Any],
) -> Any:
    return getattr(
        report,
        "_airline_transaction_artifact_ledger_source_bundle_v0_1",
        report.get("airline_transaction_artifact_ledger_source_bundle_v0_1"),
    )


def _typed_airline_transaction_artifact_ledger_source_validation_from_report(
    report: Mapping[str, Any],
) -> Any:
    return getattr(
        report,
        "_airline_transaction_artifact_ledger_source_validation_v0_1",
        report.get("airline_transaction_artifact_ledger_source_validation_v0_1"),
    )


def _typed_airline_transaction_artifact_ledger_from_report(
    report: Mapping[str, Any],
) -> Any:
    return getattr(
        report,
        "_airline_transaction_artifact_ledger_v0_1",
        report.get("airline_transaction_artifact_ledger_v0_1"),
    )


def _airline_transaction_artifact_ledger_public_typed_coherence_errors(
    report: Mapping[str, Any],
) -> tuple[str, ...]:
    hidden_names = (
        "_airline_transaction_artifact_ledger_source_bundle_v0_1",
        "_airline_transaction_artifact_ledger_source_validation_v0_1",
        "_airline_transaction_artifact_ledger_v0_1",
    )
    if not any(hasattr(report, name) for name in hidden_names):
        return ()
    expected_pairs = (
        (
            "airline_transaction_artifact_ledger_source_bundle_v0_1",
            getattr(
                report,
                "_airline_transaction_artifact_ledger_source_bundle_v0_1",
                None,
            ),
        ),
        (
            "airline_transaction_artifact_ledger_source_validation_v0_1",
            getattr(
                report,
                "_airline_transaction_artifact_ledger_source_validation_v0_1",
                None,
            ),
        ),
        (
            "airline_transaction_artifact_ledger_v0_1",
            getattr(report, "_airline_transaction_artifact_ledger_v0_1", None),
        ),
    )
    for public_key, typed_value in expected_pairs:
        if report.get(public_key) != _json_safe(typed_value):
            return (REASON_LEDGER_PUBLIC_TYPED_VIEW_MISMATCH,)
    return ()


def _actual_airline_transaction_artifact_ledger_geometry(
    ledger: ledger_contracts.AirlineTransactionArtifactLedgerV01 | None,
) -> dict[str, int]:
    if not isinstance(ledger, ledger_contracts.AirlineTransactionArtifactLedgerV01):
        return {
            "entry_count": 0,
            "dependency_edge_count": 0,
            "root_final_count": 0,
        }
    entries = tuple(ledger.entries)
    return {
        "entry_count": len(entries),
        "dependency_edge_count": sum(len(entry.depends_on) for entry in entries),
        "root_final_count": sum(
            1 for entry in entries if entry.artifact_type in ROOT_FINAL_ARTIFACT_TYPES
        ),
    }


def _airline_transaction_artifact_ledger_geometry_errors(
    ledger: ledger_contracts.AirlineTransactionArtifactLedgerV01 | None,
) -> tuple[str, ...]:
    if not isinstance(ledger, ledger_contracts.AirlineTransactionArtifactLedgerV01):
        return ()
    actual = _actual_airline_transaction_artifact_ledger_geometry(ledger)
    errors: list[str] = []
    if actual["entry_count"] != 19:
        errors.append(REASON_ACTUAL_LEDGER_ENTRY_COUNT_MISMATCH)
    if actual["dependency_edge_count"] != 29:
        errors.append(REASON_ACTUAL_LEDGER_DEPENDENCY_EDGE_MISMATCH)
    if actual["root_final_count"] != 3:
        errors.append(REASON_ACTUAL_LEDGER_ROOT_FINAL_MISMATCH)
    artifact_type_sequence = tuple(entry.artifact_type for entry in ledger.entries)
    if artifact_type_sequence != ledger_contracts.EXPECTED_ARTIFACT_TYPE_SEQUENCE:
        errors.append(REASON_LEDGER_ARTIFACT_TYPE_SEQUENCE_MISMATCH)
    root_final_counts = {
        artifact_type: artifact_type_sequence.count(artifact_type)
        for artifact_type in ROOT_FINAL_ARTIFACT_TYPES
    }
    if any(count != 1 for count in root_final_counts.values()):
        errors.append(REASON_LEDGER_ROOT_FINAL_SET_MISMATCH)
    if (
        ledger.entry_count != actual["entry_count"]
        or ledger.dependency_edge_count != actual["dependency_edge_count"]
        or ledger.root_final_count != actual["root_final_count"]
    ):
        errors.append(REASON_LEDGER_STORED_ACTUAL_DERIVED_FIELD_MISMATCH)
    return tuple(dict.fromkeys(errors))


def _ledger_integration_summary(
    *,
    source_bundle: (
        ledger_collector.AirlineTransactionArtifactLedgerSourceBundleV01 | None
    ),
    source_validation_report: (
        ledger_collector.AirlineTransactionArtifactLedgerSourceValidationReportV01
        | None
    ),
    collected_ledger: (
        ledger_contracts.AirlineTransactionArtifactLedgerV01 | None
    ),
    selected_offer_id: str,
    corridor_execution_count: int,
    source_bundle_collection_count: int,
    ledger_collection_count: int,
) -> dict[str, Any]:
    source_bundle_is_valid_type = isinstance(
        source_bundle,
        ledger_collector.AirlineTransactionArtifactLedgerSourceBundleV01,
    )
    source_status = (
        source_validation_report.validation_status
        if source_validation_report is not None
        else STATUS_FAIL_CLOSED
    )
    source_errors = (
        source_validation_report.validation_errors
        if source_validation_report is not None
        else ("source_bundle_not_validated",)
    )
    ledger_status = (
        collected_ledger.validation_status
        if collected_ledger is not None
        else STATUS_FAIL_CLOSED
    )
    ledger_errors = (
        collected_ledger.validation_errors
        if collected_ledger is not None
        else ("ledger_not_collected",)
    )
    actual_geometry = _actual_airline_transaction_artifact_ledger_geometry(
        collected_ledger,
    )
    geometry_errors = _airline_transaction_artifact_ledger_geometry_errors(
        collected_ledger,
    )
    entry_count = actual_geometry["entry_count"]
    dependency_edge_count = actual_geometry["dependency_edge_count"]
    root_final_count = actual_geometry["root_final_count"]
    geometry_valid = (
        entry_count == 19 and dependency_edge_count == 29 and root_final_count == 3
    )
    duplicate_corridor_count = max(0, corridor_execution_count - 1)
    duplicate_ledger_count = max(0, ledger_collection_count - 1)
    duplicate_transaction_count = int(
        source_bundle_is_valid_type
        and source_bundle.transaction_id != TRANSACTION_ID
    )
    pass_status = (
        source_status == ledger_collector.STATUS_PASS
        and source_errors == ()
        and ledger_status == ledger_contracts.STATUS_PASS
        and ledger_errors == ()
        and geometry_errors == ()
        and geometry_valid
        and source_bundle_collection_count == 1
        and ledger_collection_count == 1
        and corridor_execution_count == 1
        and duplicate_transaction_count == 0
        and duplicate_corridor_count == 0
        and duplicate_ledger_count == 0
    )
    return {
        "integration_status": STATUS_PASS if pass_status else STATUS_FAIL_CLOSED,
        "source_bundle_validation_status": source_status,
        "source_bundle_validation_errors": source_errors,
        "ledger_validation_status": ledger_status,
        "ledger_validation_errors": tuple(dict.fromkeys(ledger_errors + geometry_errors)),
        "actual_entry_count": entry_count,
        "actual_dependency_edge_count": dependency_edge_count,
        "actual_root_final_count": root_final_count,
        "stored_entry_count": (
            collected_ledger.entry_count if collected_ledger is not None else 0
        ),
        "stored_dependency_edge_count": (
            collected_ledger.dependency_edge_count if collected_ledger is not None else 0
        ),
        "stored_root_final_count": (
            collected_ledger.root_final_count if collected_ledger is not None else 0
        ),
        "ledger_id": collected_ledger.ledger_id if collected_ledger is not None else "",
        "transaction_id": (
            source_bundle.transaction_id
            if source_bundle_is_valid_type
            else TRANSACTION_ID
        ),
        "source_run_ref": (
            source_bundle.expected_source_refs.source_run_ref
            if source_bundle_is_valid_type
            else ""
        ),
        "source_causal_report_ref": (
            source_bundle.expected_source_refs.source_causal_report_ref
            if source_bundle_is_valid_type
            else ""
        ),
        "source_corridor_report_ref": (
            source_bundle.expected_source_refs.source_corridor_report_ref
            if source_bundle_is_valid_type
            else ""
        ),
        "selected_offer_id": selected_offer_id,
        "entry_count": entry_count,
        "dependency_edge_count": dependency_edge_count,
        "root_final_count": root_final_count,
        "source_bundle_collection_count": source_bundle_collection_count,
        "ledger_collection_count": ledger_collection_count,
        "ledger_validation_count": ledger_collection_count,
        "corridor_execution_count": corridor_execution_count,
        "duplicate_transaction_count": duplicate_transaction_count,
        "duplicate_corridor_execution_count": duplicate_corridor_count,
        "duplicate_ledger_collection_count": duplicate_ledger_count,
        "source_reconstruction_count": 0,
        "provider_calls_added_by_ledger_count": (
            collected_ledger.provider_called_count if collected_ledger else 0
        ),
        "network_calls_added_by_ledger_count": (
            collected_ledger.network_used_count if collected_ledger else 0
        ),
        "gemini_calls_added_by_ledger_count": (
            collected_ledger.gemini_called_count if collected_ledger else 0
        ),
        "ledger_created_authority_count": (
            collected_ledger.ledger_created_authority_count if collected_ledger else 0
        ),
        "ledger_created_permission_count": (
            collected_ledger.ledger_created_permission_count if collected_ledger else 0
        ),
        "ledger_created_action_count": (
            collected_ledger.ledger_created_action_count if collected_ledger else 0
        ),
        "real_world_effects_count": (
            collected_ledger.real_world_effects_count if collected_ledger else 0
        ),
        "artifact_written_count": 0,
    }


def _collect_airline_transaction_artifact_ledger_integration_v01(
    *,
    semantic_causal_run: causal_runtime.AirlineSemanticCausalRunReportV01,
    bsep_side_projections: Mapping[str, Any] | None,
    corridor_execution_result: corridor_runtime.AirlineTicketPurchaseCorridorExecutionResultV01,
    source_bundle_id: str,
    corridor_execution_count: int,
) -> tuple[
    ledger_collector.AirlineTransactionArtifactLedgerSourceBundleV01 | None,
    ledger_collector.AirlineTransactionArtifactLedgerSourceValidationReportV01 | None,
    ledger_contracts.AirlineTransactionArtifactLedgerV01 | None,
    dict[str, Any],
]:
    source_bundle_collection_count = 0
    ledger_collection_count = 0
    selected_offer_id = semantic_causal_run.semantic_recommendation_id
    try:
        source_bundle_collection_count += 1
        source_bundle = _build_airline_transaction_artifact_ledger_source_bundle_v01(
            semantic_causal_run=semantic_causal_run,
            bsep_side_projections=bsep_side_projections,
            corridor_execution_result=corridor_execution_result,
            source_bundle_id=source_bundle_id,
        )
    except (AttributeError, KeyError, TypeError, ValueError) as exc:
        summary = _ledger_integration_summary(
            source_bundle=None,
            source_validation_report=None,
            collected_ledger=None,
            selected_offer_id=selected_offer_id,
            corridor_execution_count=corridor_execution_count,
            source_bundle_collection_count=source_bundle_collection_count,
            ledger_collection_count=ledger_collection_count,
        )
        summary = {
            **summary,
            "source_bundle_validation_errors": (f"source_bundle_assembly_failed:{exc}",),
        }
        return None, None, None, summary

    source_validation_report = (
        ledger_collector.validate_airline_transaction_artifact_ledger_source_bundle_v01(
            source_bundle,
        )
    )
    collected_ledger = None
    if (
        source_validation_report.validation_status == ledger_collector.STATUS_PASS
        and source_validation_report.validation_errors == ()
    ):
        ledger_collection_count += 1
        collected_ledger = (
            ledger_collector.collect_airline_transaction_artifact_ledger_from_source_v01(
                source_bundle=source_bundle,
            )
        )
    summary = _ledger_integration_summary(
        source_bundle=source_bundle,
        source_validation_report=source_validation_report,
        collected_ledger=collected_ledger,
        selected_offer_id=selected_offer_id,
        corridor_execution_count=corridor_execution_count,
        source_bundle_collection_count=source_bundle_collection_count,
        ledger_collection_count=ledger_collection_count,
    )
    return source_bundle, source_validation_report, collected_ledger, summary


def _client_root_view(
    participants: Mapping[str, Mapping[str, Any]],
    fixtures: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    return {
        "root_id": participants["ClientRoot"]["root_id"],
        "role": participants["ClientRoot"]["role"],
        "bounded_view": (
            "travel intent",
            "sealed passenger refs",
            "sealed payment profile refs",
            "selected offer ref",
            "client purchase approval evidence",
            "mock ticket evidence after AirlineRoot fixture",
        ),
        "selected_offer_ref": fixtures["AirlineOfferResponseV01"]["selected_candidate_ref"],
        "approval_evidence_ref": fixtures["ClientPurchaseApprovalEvidenceV01"]["approval_id"],
        "does_not_issue_ticket": True,
        "does_not_authorize_bank_payment": True,
        "raw_secret_exposure_count": 0,
    }


def _airline_root_view(
    participants: Mapping[str, Mapping[str, Any]],
    fixtures: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    return {
        "root_id": participants["AirlineRoot"]["root_id"],
        "role": participants["AirlineRoot"]["role"],
        "bounded_view": (
            "mock inventory",
            "mock fares",
            "mock seat availability",
            "baggage rule",
            "offer hold receipt",
            "future mock order/ticket evidence",
        ),
        "offer_response_ref": fixtures["AirlineOfferResponseV01"]["response_id"],
        "offer_hold_receipt_ref": fixtures["AirlineOfferHoldReceiptV01"]["receipt_id"],
        "future_mock_ticket_receipt_ref": fixtures["MockTicketReceiptV01"]["receipt_id"],
        "does_not_charge_card": True,
        "does_not_authorize_client_payment": True,
        "real_airline_api_called": False,
    }


def _bank_root_view(
    participants: Mapping[str, Mapping[str, Any]],
    fixtures: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    return {
        "root_id": participants["BankRoot"]["root_id"],
        "role": participants["BankRoot"]["role"],
        "bounded_view": (
            "payment token ref",
            "debtor slot",
            "merchant ref",
            "amount/currency",
            "idempotency",
            "payment authorization receipt",
        ),
        "payment_intent_ref": fixtures["BankPaymentIntentV01"]["intent_id"],
        "payment_authorization_receipt_ref": fixtures[
            "BankPaymentAuthorizationReceiptV01"
        ]["receipt_id"],
        "does_not_create_ticket": True,
        "real_bank_api_called": False,
        "real_payment_executed": False,
    }


def _root_boundary_matrix() -> tuple[dict[str, Any], ...]:
    return tuple(
        {
            "boundary": boundary,
            "boundary_preserved": True,
            "violation_count": 0,
        }
        for boundary in (
            "ClientRoot cannot issue ticket.",
            "ClientRoot cannot authorize bank payment.",
            "AirlineRoot cannot authorize client payment.",
            "AirlineRoot cannot charge card.",
            "BankRoot cannot create airline ticket.",
            "BankRoot cannot create airline order.",
            "Payment receipt does not automatically create ticket.",
            "Ticket receipt does not automatically create payment.",
            "Receipt from one Root is evidence for another Root, not authority over it.",
            "Each Root consumes evidence, not foreign authority.",
            "No Root becomes God over the others.",
            "Root boundaries remain side-specific.",
        )
    )


def _receipt_boundary_matrix() -> tuple[dict[str, Any], ...]:
    return tuple(
        {
            "boundary": boundary,
            "boundary_preserved": True,
            "violation_count": 0,
        }
        for boundary in (
            "OfferHoldReceipt is evidence only.",
            "PaymentAuthorizationReceipt is evidence only.",
            "PaymentStatusReceipt is evidence only.",
            "OrderCreatedReceipt is evidence only.",
            "MockTicketReceipt is evidence only.",
            "MockTicketReceipt is not real ticket.",
            "PaymentAuthorizationReceipt is not ticket permission.",
            "OfferHoldReceipt is not payment permission.",
            "ClientPurchaseApprovalEvidence is evidence for BankRoot and AirlineRoot, not their authority.",
        )
    )


def _privacy_boundary_matrix() -> dict[str, Any]:
    return {
        "raw_passport_exposed_count": 0,
        "raw_card_exposed_count": 0,
        "raw_iban_exposed_count": 0,
        "raw_payment_token_exposed_count": 0,
        "raw_birthdate_exposed_count": 0,
        "raw_document_number_exposed_count": 0,
        "passenger_sealed_ref_only": True,
        "payment_profile_sealed_ref_only": True,
        "vault_refs_not_llm_context": True,
        "no_raw_private_profile_in_provider_context": True,
        "no_raw_secrets_in_artifacts": True,
    }


def _non_action_reuse_constraints() -> dict[str, Any]:
    return {
        "constraints": (
            "old route preference may inform context only.",
            "old quote is not ticket permission.",
            "old payment receipt is not current payment authorization.",
            "old ticket receipt is not future ticket permission.",
            "old traveler refs cannot expose raw passport.",
            "DRS hit is context only unless RootShortcutGate allows informational reuse.",
            "action-like Airline requests must route to Root/corridor, not direct reuse.",
        ),
        "non_action_reuse_cannot_buy_ticket": True,
    }


def _future_semantic_actor_topology() -> tuple[dict[str, Any], ...]:
    role_specs = (
        (
            "client",
            "client_purchase_orchestrator_llm",
            "interpret user travel intent, passenger constraints, selected offer approval, and user-facing risk explanation.",
        ),
        (
            "client",
            "client_profile_privacy_reviewer_llm",
            "explain which sealed refs are safe to share and which raw private fields remain sealed.",
        ),
        (
            "airline",
            "airline_offer_policy_reviewer_llm",
            "interpret fare, baggage, TTL, route, refund/change, and offer-hold constraints.",
        ),
        (
            "airline",
            "airline_ticketing_policy_reviewer_llm",
            "interpret when payment evidence is sufficient for mock ticket issue.",
        ),
        (
            "bank",
            "bank_payment_policy_reviewer_llm",
            "interpret consent, amount, merchant, idempotency, expiry, and risk policy.",
        ),
        (
            "bank",
            "bank_payment_status_explainer_llm",
            "explain payment authorization vs settlement vs evidence-only status.",
        ),
    )
    return tuple(
        {
            "side": side,
            "role": role,
            "semantic_work": semantic_work,
            "planned_for_later_live_lane": True,
            "executed_in_slice_b": False,
            "creates_authority": False,
            "creates_action_commit_packet": False,
            "creates_receipt": False,
            "creates_ticket": False,
            "executes_payment": False,
            "calls_real_api": False,
        }
        for side, role, semantic_work in role_specs
    )


def _future_vertical_fractal_map() -> dict[str, tuple[dict[str, Any], ...]]:
    cells_by_root = {
        "ClientRoot": (
            "client_intent_cell",
            "passenger_sealed_ref_cell",
            "payment_profile_sealed_ref_cell",
            "purchase_approval_cell",
        ),
        "AirlineRoot": (
            "airline_offer_root_cell",
            "fare_rules_child_cell",
            "baggage_policy_child_cell",
            "offer_ttl_child_cell",
            "ticket_issue_policy_child_cell",
        ),
        "BankRoot": (
            "bank_payment_root_cell",
            "consent_child_cell",
            "merchant_amount_match_child_cell",
            "idempotency_child_cell",
            "risk_policy_child_cell",
        ),
    }
    return {
        root_name: tuple(
            {
                "cell_id": cell_id,
                "planned_for_later": True,
                "executed_in_slice_b": False,
                "creates_authority": False,
                "real_world_effects_count": 0,
            }
            for cell_id in cell_ids
        )
        for root_name, cell_ids in cells_by_root.items()
    }


def _counter_table(
    ledger: tuple[dict[str, Any], ...],
    actors: tuple[dict[str, Any], ...],
    fractal_map: Mapping[str, tuple[dict[str, Any], ...]],
    airline_offer_hold_sandbox: Mapping[str, Any],
    bank_payment_authorization_sandbox: Mapping[str, Any],
    client_purchase_orchestration: Mapping[str, Any],
    airline_ticket_issue_mock_corridor: Mapping[str, Any],
    integrated_transaction_trace: tuple[dict[str, Any], ...],
    cross_root_evidence_routing_matrix: tuple[dict[str, Any], ...],
    final_tri_party_mock_summary: Mapping[str, Any],
    airline_ticket_purchase_corridor_v0_1: (
        corridor_runtime.AirlineTicketPurchaseCorridorRunReportV01
    ),
    airline_ticket_purchase_corridor_binding_matrix: tuple[dict[str, Any], ...],
    airline_ticket_purchase_corridor_integration: Mapping[str, Any],
    airline_transaction_artifact_ledger_integration: Mapping[str, Any],
    deterministic_bsep_source_creation_count: int,
    local_injected_semantic_callback_count: int,
) -> dict[str, int]:
    fractal_cells = tuple(
        cell for cells in fractal_map.values() for cell in cells
    )
    corridor_counters = airline_ticket_purchase_corridor_v0_1.counter_table
    binding_row_count = len(airline_ticket_purchase_corridor_binding_matrix)
    binding_match_count = sum(
        int(row["values_match"])
        for row in airline_ticket_purchase_corridor_binding_matrix
    )
    return {
        "tri_party_airline_transaction_count": 1,
        "client_root_count": 1,
        "airline_root_count": 1,
        "bank_root_count": 1,
        "deterministic_airline_collection_count": 1,
        "deterministic_airline_pass_count": 1,
        "deterministic_bsep_source_creation_count": (
            deterministic_bsep_source_creation_count
        ),
        "local_injected_semantic_callback_count": (
            local_injected_semantic_callback_count
        ),
        "provider_network_call_count": 0,
        "gemini_call_count": 0,
        "ticket_purchase_corridor_execution_count": 1,
        "ticket_purchase_corridor_pass_count": int(
            airline_ticket_purchase_corridor_v0_1.final_status
            == corridor_runtime.STATUS_PASS,
        ),
        "direct_offer_override_count": 0,
        "default_offer_count": 0,
        "silent_fallback_count": 0,
        "provider_created_authority_count": 0,
        "provider_created_contract_count": 0,
        "runtime_receipt_created_count": 0,
        "shared_transaction_id_count": 1,
        "shared_ledger_entry_count": len(ledger),
        "offer_candidates_created_count": 1,
        "offer_hold_receipt_fixture_count": 1,
        "airline_offer_hold_sandbox_invoked_count": 1,
        "airline_offer_request_validated_count": int(
            airline_offer_hold_sandbox["offer_request_validated"],
        ),
        "mock_inventory_checked_count": int(
            airline_offer_hold_sandbox["mock_inventory_checked"],
        ),
        "mock_fare_checked_count": int(
            airline_offer_hold_sandbox["mock_fare_checked"],
        ),
        "baggage_rule_checked_count": int(
            airline_offer_hold_sandbox["baggage_rule_checked"],
        ),
        "offer_ttl_checked_count": int(
            airline_offer_hold_sandbox["offer_ttl_checked"],
        ),
        "airline_offer_response_created_count": int(
            airline_offer_hold_sandbox["offer_response_created"],
        ),
        "airline_offer_hold_commit_packet_created_count": int(
            airline_offer_hold_sandbox["offer_hold_commit_packet_created"],
        ),
        "airline_offer_hold_commit_packet_created_by_airline_root_count": int(
            airline_offer_hold_sandbox["offer_hold_commit_packet_created_by"]
            == "airline_root",
        ),
        "airline_offer_hold_commit_packet_created_by_client_root_count": int(
            airline_offer_hold_sandbox["offer_hold_commit_packet_created_by"]
            == "client_root",
        ),
        "airline_offer_hold_commit_packet_created_by_bank_root_count": int(
            airline_offer_hold_sandbox["offer_hold_commit_packet_created_by"]
            == "bank_root",
        ),
        "airline_offer_hold_commit_packet_validated_count": int(
            airline_offer_hold_sandbox["offer_hold_commit_packet_validated"],
        ),
        "airline_offer_hold_receipt_created_count": int(
            airline_offer_hold_sandbox["offer_hold_receipt_created"],
        ),
        "airline_offer_hold_receipt_validated_count": int(
            airline_offer_hold_sandbox["offer_hold_receipt_validated"],
        ),
        "offer_hold_receipt_payment_permission_created_count": int(
            airline_offer_hold_sandbox[
                "offer_hold_receipt_payment_permission_created"
            ],
        ),
        "offer_hold_receipt_ticket_permission_created_count": int(
            airline_offer_hold_sandbox[
                "offer_hold_receipt_ticket_permission_created"
            ],
        ),
        "client_purchase_approval_evidence_fixture_count": 1,
        "client_purchase_orchestration_invoked_count": 1,
        "client_travel_intent_observed_count": int(
            client_purchase_orchestration["travel_intent_observed"],
        ),
        "client_passenger_sealed_refs_observed_count": int(
            client_purchase_orchestration["passenger_sealed_refs_observed"],
        ),
        "client_payment_profile_sealed_ref_observed_count": int(
            client_purchase_orchestration[
                "payment_profile_sealed_ref_observed"
            ],
        ),
        "client_offer_response_observed_count": int(
            client_purchase_orchestration["offer_response_observed"],
        ),
        "client_offer_hold_receipt_observed_count": int(
            client_purchase_orchestration["offer_hold_receipt_observed"],
        ),
        "client_offer_selected_count": int(
            bool(client_purchase_orchestration["selected_offer_id"]),
        ),
        "client_selected_offer_within_user_max_price_count": int(
            client_purchase_orchestration["selected_offer_within_user_max_price"],
        ),
        "client_purchase_approval_evidence_created_count": int(
            client_purchase_orchestration[
                "client_purchase_approval_evidence_created"
            ],
        ),
        "client_purchase_approval_evidence_created_by_client_root_count": int(
            client_purchase_orchestration[
                "client_purchase_approval_evidence_created_by"
            ]
            == "client_root",
        ),
        "client_purchase_approval_evidence_created_by_airline_root_count": int(
            client_purchase_orchestration[
                "client_purchase_approval_evidence_created_by"
            ]
            == "airline_root",
        ),
        "client_purchase_approval_evidence_created_by_bank_root_count": int(
            client_purchase_orchestration[
                "client_purchase_approval_evidence_created_by"
            ]
            == "bank_root",
        ),
        "client_purchase_approval_evidence_validated_count": int(
            client_purchase_orchestration[
                "client_purchase_approval_evidence_validated"
            ],
        ),
        "client_purchase_approval_evidence_routed_to_bank_root_count": int(
            client_purchase_orchestration["routed_to_bank_root"],
        ),
        "client_purchase_approval_evidence_routed_to_airline_root_count": int(
            client_purchase_orchestration["routed_to_airline_root"],
        ),
        "client_bank_payment_authorization_receipt_observed_count": int(
            client_purchase_orchestration[
                "bank_payment_authorization_receipt_observed"
            ],
        ),
        "client_bank_payment_status_receipt_observed_count": int(
            client_purchase_orchestration["bank_payment_status_receipt_observed"],
        ),
        "client_final_purchase_summary_created_count": int(
            client_purchase_orchestration["client_final_purchase_summary_created"],
        ),
        "client_root_authorized_bank_payment_count": int(
            client_purchase_orchestration["client_root_authorized_bank_payment"],
        ),
        "client_root_created_airline_order_count": int(
            client_purchase_orchestration["client_root_created_airline_order"],
        ),
        "client_root_created_bank_receipt_count": int(
            client_purchase_orchestration["client_root_created_bank_receipt"],
        ),
        "client_root_created_action_commit_packet_count": int(
            client_purchase_orchestration[
                "client_root_created_action_commit_packet"
            ],
        ),
        "client_raw_passport_exposed_count": int(
            client_purchase_orchestration["raw_passport_exposed"],
        ),
        "client_raw_card_exposed_count": int(
            client_purchase_orchestration["raw_card_exposed"],
        ),
        "client_raw_iban_exposed_count": int(
            client_purchase_orchestration["raw_iban_exposed"],
        ),
        "client_raw_payment_token_exposed_count": int(
            client_purchase_orchestration["raw_payment_token_exposed"],
        ),
        "bank_payment_intent_fixture_count": 1,
        "bank_payment_consent_fixture_count": 1,
        "bank_payment_authorization_receipt_fixture_count": 1,
        "bank_payment_status_receipt_fixture_count": 1,
        "bank_payment_authorization_sandbox_invoked_count": 1,
        "bank_offer_hold_receipt_observed_count": int(
            bank_payment_authorization_sandbox["offer_hold_receipt_observed"],
        ),
        "bank_client_purchase_approval_evidence_observed_count": int(
            bank_payment_authorization_sandbox[
                "client_purchase_approval_evidence_observed"
            ],
        ),
        "bank_payment_profile_sealed_ref_observed_count": int(
            bank_payment_authorization_sandbox[
                "payment_profile_sealed_ref_observed"
            ],
        ),
        "bank_amount_currency_validated_count": int(
            bank_payment_authorization_sandbox["amount_currency_validated"],
        ),
        "bank_merchant_airline_ref_validated_count": int(
            bank_payment_authorization_sandbox["merchant_airline_ref_validated"],
        ),
        "bank_payment_token_ref_validated_count": int(
            bank_payment_authorization_sandbox["payment_token_ref_validated"],
        ),
        "bank_debtor_slot_ref_validated_count": int(
            bank_payment_authorization_sandbox["debtor_slot_ref_validated"],
        ),
        "bank_idempotency_checked_count": int(
            bank_payment_authorization_sandbox["idempotency_checked"],
        ),
        "bank_expiry_ttl_checked_count": int(
            bank_payment_authorization_sandbox["expiry_ttl_checked"],
        ),
        "bank_payment_intent_created_count": int(
            bank_payment_authorization_sandbox["bank_payment_intent_created"],
        ),
        "bank_payment_consent_created_count": int(
            bank_payment_authorization_sandbox["bank_payment_consent_created"],
        ),
        "bank_payment_authorization_commit_packet_created_count": int(
            bank_payment_authorization_sandbox[
                "bank_payment_authorization_commit_packet_created"
            ],
        ),
        "bank_payment_authorization_commit_packet_created_by_bank_root_count": int(
            bank_payment_authorization_sandbox[
                "bank_payment_authorization_commit_packet_created_by"
            ]
            == "bank_root",
        ),
        "bank_payment_authorization_commit_packet_created_by_client_root_count": int(
            bank_payment_authorization_sandbox[
                "bank_payment_authorization_commit_packet_created_by"
            ]
            == "client_root",
        ),
        "bank_payment_authorization_commit_packet_created_by_airline_root_count": int(
            bank_payment_authorization_sandbox[
                "bank_payment_authorization_commit_packet_created_by"
            ]
            == "airline_root",
        ),
        "bank_payment_authorization_commit_packet_validated_count": int(
            bank_payment_authorization_sandbox[
                "bank_payment_authorization_commit_packet_validated"
            ],
        ),
        "payment_authorization_receipt_created_count": int(
            bank_payment_authorization_sandbox[
                "payment_authorization_receipt_created"
            ],
        ),
        "payment_authorization_receipt_validated_count": int(
            bank_payment_authorization_sandbox[
                "payment_authorization_receipt_validated"
            ],
        ),
        "payment_status_receipt_created_count": int(
            bank_payment_authorization_sandbox["payment_status_receipt_created"],
        ),
        "payment_status_receipt_validated_count": int(
            bank_payment_authorization_sandbox["payment_status_receipt_validated"],
        ),
        "payment_authorization_receipt_ticket_permission_created_count": int(
            bank_payment_authorization_sandbox[
                "payment_authorization_receipt_ticket_permission_created"
            ],
        ),
        "payment_authorization_receipt_real_payment_executed_count": int(
            bank_payment_authorization_sandbox[
                "payment_authorization_receipt_real_payment_executed"
            ],
        ),
        "payment_status_receipt_ticket_permission_created_count": int(
            bank_payment_authorization_sandbox[
                "payment_status_receipt_ticket_permission_created"
            ],
        ),
        "payment_status_receipt_settlement_executed_count": int(
            bank_payment_authorization_sandbox[
                "payment_status_receipt_settlement_executed"
            ],
        ),
        "airline_order_created_receipt_fixture_count": 1,
        "mock_ticket_receipt_fixture_count": 1,
        "mock_pnr_fixture_count": 1,
        "mock_purchase_receipt_fixture_count": 1,
        "airline_ticket_issue_mock_corridor_invoked_count": 1,
        "airline_ticket_issue_offer_hold_receipt_observed_count": int(
            airline_ticket_issue_mock_corridor["offer_hold_receipt_observed"],
        ),
        "airline_ticket_issue_client_purchase_approval_observed_count": int(
            airline_ticket_issue_mock_corridor[
                "client_purchase_approval_evidence_observed"
            ],
        ),
        "airline_ticket_issue_payment_authorization_receipt_observed_count": int(
            airline_ticket_issue_mock_corridor[
                "payment_authorization_receipt_observed"
            ],
        ),
        "airline_ticket_issue_payment_status_receipt_observed_count": int(
            airline_ticket_issue_mock_corridor["payment_status_receipt_observed"],
        ),
        "airline_ticket_issue_offer_hold_ttl_freshness_validated_count": int(
            airline_ticket_issue_mock_corridor[
                "offer_hold_ttl_freshness_validated"
            ],
        ),
        "airline_ticket_issue_selected_offer_match_validated_count": int(
            airline_ticket_issue_mock_corridor["selected_offer_match_validated"],
        ),
        "airline_ticket_issue_amount_currency_match_validated_count": int(
            airline_ticket_issue_mock_corridor["amount_currency_match_validated"],
        ),
        "airline_ticket_issue_merchant_airline_ref_match_validated_count": int(
            airline_ticket_issue_mock_corridor[
                "merchant_airline_ref_match_validated"
            ],
        ),
        "airline_ticket_issue_passenger_sealed_ref_validated_count": int(
            airline_ticket_issue_mock_corridor["passenger_sealed_ref_validated"],
        ),
        "airline_ticket_issue_payment_evidence_validated_against_offer_hold_count": int(
            airline_ticket_issue_mock_corridor[
                "payment_evidence_validated_against_offer_hold"
            ],
        ),
        "airline_ticket_issue_commit_packet_created_count": int(
            airline_ticket_issue_mock_corridor[
                "airline_ticket_issue_commit_packet_created"
            ],
        ),
        "airline_ticket_issue_commit_packet_created_by_airline_root_count": int(
            airline_ticket_issue_mock_corridor[
                "airline_ticket_issue_commit_packet_created_by"
            ]
            == "airline_root",
        ),
        "airline_ticket_issue_commit_packet_created_by_client_root_count": int(
            airline_ticket_issue_mock_corridor[
                "airline_ticket_issue_commit_packet_created_by"
            ]
            == "client_root",
        ),
        "airline_ticket_issue_commit_packet_created_by_bank_root_count": int(
            airline_ticket_issue_mock_corridor[
                "airline_ticket_issue_commit_packet_created_by"
            ]
            == "bank_root",
        ),
        "airline_ticket_issue_commit_packet_validated_count": int(
            airline_ticket_issue_mock_corridor[
                "airline_ticket_issue_commit_packet_validated"
            ],
        ),
        "airline_order_created_receipt_created_count": int(
            airline_ticket_issue_mock_corridor[
                "airline_order_created_receipt_created"
            ],
        ),
        "airline_order_created_receipt_validated_count": int(
            airline_ticket_issue_mock_corridor[
                "airline_order_created_receipt_validated"
            ],
        ),
        "mock_ticket_receipt_created_count": int(
            airline_ticket_issue_mock_corridor["mock_ticket_receipt_created"],
        ),
        "mock_ticket_receipt_validated_count": int(
            airline_ticket_issue_mock_corridor["mock_ticket_receipt_validated"],
        ),
        "mock_pnr_created_count": int(
            airline_ticket_issue_mock_corridor["mock_pnr_created"],
        ),
        "mock_pnr_validated_count": int(
            airline_ticket_issue_mock_corridor["mock_pnr_validated"],
        ),
        "mock_ticket_receipt_evidence_only_count": int(
            airline_ticket_issue_mock_corridor[
                "mock_ticket_receipt_evidence_only"
            ],
        ),
        "mock_ticket_receipt_real_ticket_count": int(
            airline_ticket_issue_mock_corridor["mock_ticket_receipt_real_ticket"],
        ),
        "mock_pnr_real_booking_count": int(
            airline_ticket_issue_mock_corridor["mock_pnr_real_booking"],
        ),
        "payment_authorization_receipt_created_ticket_count": int(
            airline_ticket_issue_mock_corridor[
                "payment_authorization_receipt_created_ticket"
            ],
        ),
        "client_purchase_approval_created_ticket_count": int(
            airline_ticket_issue_mock_corridor[
                "client_purchase_approval_created_ticket"
            ],
        ),
        "offer_hold_receipt_created_ticket_count": int(
            airline_ticket_issue_mock_corridor["offer_hold_receipt_created_ticket"],
        ),
        "airline_root_called_real_airline_api_count": int(
            airline_ticket_issue_mock_corridor[
                "airline_root_called_real_airline_api"
            ],
        ),
        "airline_root_called_real_gds_api_count": int(
            airline_ticket_issue_mock_corridor["airline_root_called_real_gds_api"],
        ),
        "integrated_tri_party_transaction_trace_created_count": int(
            bool(integrated_transaction_trace),
        ),
        "integrated_trace_phase_count": len(integrated_transaction_trace),
        "cross_root_evidence_routing_rows_count": len(
            cross_root_evidence_routing_matrix,
        ),
        "cross_root_authority_transfer_count": sum(
            int(row["authority_transferred"])
            for row in cross_root_evidence_routing_matrix
        ),
        "cross_root_real_world_effects_count": sum(
            int(row["real_world_effects_count"])
            for row in cross_root_evidence_routing_matrix
        ),
        "final_tri_party_mock_summary_created_count": int(
            final_tri_party_mock_summary.get("final_status") == STATUS_PASS,
        ),
        "final_client_view_mock_ticket_evidence_received_count": int(
            final_tri_party_mock_summary.get("client_view_status")
            == "mock_ticket_evidence_received_no_real_travel_booking",
        ),
        "final_airline_view_mock_order_ticket_pnr_evidence_created_count": int(
            final_tri_party_mock_summary.get("airline_view_status")
            == "mock_order_ticket_pnr_evidence_created",
        ),
        "final_bank_view_mock_payment_authorized_not_settled_count": int(
            final_tri_party_mock_summary.get("bank_view_status")
            == "mock_payment_authorized_not_settled",
        ),
        "final_real_ticket_issued_count": int(
            final_tri_party_mock_summary["real_ticket_issued"],
        ),
        "final_real_payment_executed_count": int(
            final_tri_party_mock_summary["real_payment_executed"],
        ),
        "final_real_booking_created_count": int(
            final_tri_party_mock_summary["real_booking_created"],
        ),
        "final_authority_transferred_between_roots_count": int(
            final_tri_party_mock_summary["authority_transferred_between_roots"],
        ),
        "airline_ticket_purchase_corridor_integration_count": 1,
        "airline_ticket_purchase_corridor_pass_count": int(
            airline_ticket_purchase_corridor_v0_1.final_status
            == corridor_runtime.STATUS_PASS,
        ),
        "airline_ticket_purchase_corridor_fail_count": int(
            airline_ticket_purchase_corridor_v0_1.final_status
            != corridor_runtime.STATUS_PASS,
        ),
        "airline_ticket_purchase_corridor_phase_count": len(
            airline_ticket_purchase_corridor_v0_1.phase_results,
        ),
        "airline_ticket_purchase_corridor_phase_pass_count": sum(
            int(phase.phase_status == corridor_runtime.STATUS_PASS)
            for phase in airline_ticket_purchase_corridor_v0_1.phase_results
        ),
        "airline_ticket_purchase_corridor_transition_count": len(
            airline_ticket_purchase_corridor_v0_1.transitions,
        ),
        "airline_ticket_purchase_corridor_transition_pass_count": sum(
            int(transition.transition_status == corridor_runtime.STATUS_PASS)
            for transition in airline_ticket_purchase_corridor_v0_1.transitions
        ),
        "airline_ticket_purchase_corridor_binding_row_count": binding_row_count,
        "airline_ticket_purchase_corridor_binding_match_count": binding_match_count,
        "airline_ticket_purchase_corridor_binding_mismatch_count": (
            binding_row_count - binding_match_count
        ),
        "airline_ticket_purchase_corridor_fixture_report_binding_pass_count": int(
            airline_ticket_purchase_corridor_integration[
                "corridor_report_bound_to_projected_fixtures"
            ],
        ),
        "airline_ticket_purchase_corridor_parallel_transaction_count": int(
            airline_ticket_purchase_corridor_integration[
                "parallel_fixture_transaction_created"
            ],
        ),
        "airline_ticket_purchase_corridor_duplicate_execution_count": int(
            airline_ticket_purchase_corridor_integration[
                "duplicate_corridor_execution_count"
            ],
        ),
        "airline_ticket_purchase_corridor_fixture_receipts_observed_count": (
            corridor_counters["fixture_receipts_observed_count"]
        ),
        "airline_ticket_purchase_corridor_runtime_receipts_created_count": (
            corridor_counters["runtime_receipts_created_count"]
        ),
        "airline_ticket_purchase_corridor_runtime_packets_created_count": (
            corridor_counters["runtime_packets_created_count"]
        ),
        "airline_ticket_purchase_corridor_adapter_execution_count": (
            corridor_counters["adapter_execution_count"]
        ),
        "airline_ticket_purchase_corridor_cross_root_authority_transfer_count": (
            corridor_counters["cross_root_authority_transfer_count"]
        ),
        "airline_ticket_purchase_corridor_post_root_reasoning_restart_count": sum(
            int(transition.semantic_reasoning_restarted)
            for transition in airline_ticket_purchase_corridor_v0_1.transitions
        ),
        "airline_ticket_purchase_corridor_provider_called_count": (
            corridor_counters["provider_called_count"]
        ),
        "airline_ticket_purchase_corridor_network_used_count": (
            corridor_counters["network_used_count"]
        ),
        "airline_ticket_purchase_corridor_gemini_called_count": (
            corridor_counters["gemini_called_count"]
        ),
        "airline_ticket_purchase_corridor_real_world_effects_count": (
            corridor_counters["real_world_effects_count"]
        ),
        "airline_transaction_artifact_ledger_source_bundle_collection_count": int(
            airline_transaction_artifact_ledger_integration[
                "source_bundle_collection_count"
            ],
        ),
        "airline_transaction_artifact_ledger_source_bundle_pass_count": int(
            airline_transaction_artifact_ledger_integration[
                "source_bundle_validation_status"
            ]
            == STATUS_PASS,
        ),
        "airline_transaction_artifact_ledger_collection_count": int(
            airline_transaction_artifact_ledger_integration[
                "ledger_collection_count"
            ],
        ),
        "airline_transaction_artifact_ledger_validation_count": int(
            airline_transaction_artifact_ledger_integration[
                "ledger_validation_count"
            ],
        ),
        "airline_transaction_artifact_ledger_pass_count": int(
            airline_transaction_artifact_ledger_integration[
                "ledger_validation_status"
            ]
            == STATUS_PASS,
        ),
        "airline_transaction_artifact_ledger_entry_count": int(
            airline_transaction_artifact_ledger_integration["entry_count"],
        ),
        "airline_transaction_artifact_ledger_dependency_edge_count": int(
            airline_transaction_artifact_ledger_integration[
                "dependency_edge_count"
            ],
        ),
        "airline_transaction_artifact_ledger_root_final_count": int(
            airline_transaction_artifact_ledger_integration["root_final_count"],
        ),
        "airline_transaction_artifact_ledger_duplicate_transaction_count": int(
            airline_transaction_artifact_ledger_integration[
                "duplicate_transaction_count"
            ],
        ),
        "airline_transaction_artifact_ledger_duplicate_corridor_execution_count": int(
            airline_transaction_artifact_ledger_integration[
                "duplicate_corridor_execution_count"
            ],
        ),
        "airline_transaction_artifact_ledger_duplicate_collection_count": int(
            airline_transaction_artifact_ledger_integration[
                "duplicate_ledger_collection_count"
            ],
        ),
        "airline_transaction_artifact_ledger_source_reconstruction_count": int(
            airline_transaction_artifact_ledger_integration[
                "source_reconstruction_count"
            ],
        ),
        "airline_transaction_artifact_ledger_provider_calls_added_count": int(
            airline_transaction_artifact_ledger_integration[
                "provider_calls_added_by_ledger_count"
            ],
        ),
        "airline_transaction_artifact_ledger_network_calls_added_count": int(
            airline_transaction_artifact_ledger_integration[
                "network_calls_added_by_ledger_count"
            ],
        ),
        "airline_transaction_artifact_ledger_gemini_calls_added_count": int(
            airline_transaction_artifact_ledger_integration[
                "gemini_calls_added_by_ledger_count"
            ],
        ),
        "airline_transaction_artifact_ledger_created_authority_count": int(
            airline_transaction_artifact_ledger_integration[
                "ledger_created_authority_count"
            ],
        ),
        "airline_transaction_artifact_ledger_created_permission_count": int(
            airline_transaction_artifact_ledger_integration[
                "ledger_created_permission_count"
            ],
        ),
        "airline_transaction_artifact_ledger_created_action_count": int(
            airline_transaction_artifact_ledger_integration[
                "ledger_created_action_count"
            ],
        ),
        "airline_transaction_artifact_ledger_artifact_written_count": int(
            airline_transaction_artifact_ledger_integration[
                "artifact_written_count"
            ],
        ),
        "airline_transaction_artifact_ledger_real_world_effects_count": int(
            airline_transaction_artifact_ledger_integration[
                "real_world_effects_count"
            ],
        ),
        "future_semantic_actor_roles_planned_count": len(actors),
        "future_semantic_actor_roles_executed_count": sum(
            int(actor["executed_in_slice_b"]) for actor in actors
        ),
        "future_vertical_fractal_cells_planned_count": len(fractal_cells),
        "future_vertical_fractal_cells_executed_count": sum(
            int(cell["executed_in_slice_b"]) for cell in fractal_cells
        ),
        "client_root_issued_ticket_count": 0,
        "airline_root_authorized_payment_count": 0,
        "bank_root_created_ticket_count": 0,
        "payment_receipt_created_ticket_count": 0,
        "ticket_receipt_created_payment_count": 0,
        "raw_passport_exposed_count": 0,
        "raw_card_exposed_count": 0,
        "raw_iban_exposed_count": 0,
        "raw_payment_token_exposed_count": 0,
        "real_airline_api_called_count": 0,
        "real_bank_api_called_count": 0,
        "real_payment_executed_count": 0,
        "real_settlement_executed_count": 0,
        "real_booking_created_count": 0,
        "real_ticket_issued_count": 0,
        "real_travel_booking_created_count": 0,
        "provider_called_count": 0,
        "network_used_count": 0,
        "gemini_called_count": 0,
        "real_world_effects_count": 0,
    }


def _non_claims() -> tuple[str, ...]:
    return (
        "not production",
        "not public auditor package",
        "not real airline booking",
        "not real payment",
        "not real ticket",
        "not core extraction",
        "no real airline API",
        "no real bank API",
        "no GDS, NDC, or Open Banking connector",
        "five local deterministic semantic callbacks in the standalone default path",
        "no provider network call",
        "no Gemini call",
        "Ledger added no semantic/provider call",
        "no raw passport/card/IBAN/payment token exposure",
        "no real-world effects",
    )


def _validate_report(report: Mapping[str, Any]) -> tuple[str, ...]:
    errors: tuple[str, ...] = ()
    ledger = report["shared_transaction_ledger"]
    counters = report["counter_table"]
    sandbox = report["airline_offer_hold_sandbox"]
    bank_sandbox = report["bank_payment_authorization_sandbox"]
    client_orchestration = report["client_purchase_orchestration"]
    ticket_corridor = report["airline_ticket_issue_mock_corridor"]
    integrated_trace = report["integrated_transaction_trace"]
    routing_matrix = report["cross_root_evidence_routing_matrix"]
    final_summary = report["final_tri_party_mock_summary"]
    fixtures = report["mock_protocol_fixtures"]
    corridor_report = report.get("airline_ticket_purchase_corridor_v0_1")
    corridor_contract_context = (
        corridor_report.contract_context
        if isinstance(
            corridor_report,
            corridor_runtime.AirlineTicketPurchaseCorridorRunReportV01,
        )
        else (
            corridor_contracts
            .build_canonical_airline_ticket_purchase_contract_context_v01()
        )
    )
    binding_matrix = tuple(
        report.get("airline_ticket_purchase_corridor_binding_matrix", ()),
    )
    corridor_integration = report.get(
        "airline_ticket_purchase_corridor_integration",
        {},
    )
    ledger_source_bundle = (
        _typed_airline_transaction_artifact_ledger_source_bundle_from_report(report)
    )
    ledger_source_validation = (
        _typed_airline_transaction_artifact_ledger_source_validation_from_report(
            report,
        )
    )
    artifact_ledger = _typed_airline_transaction_artifact_ledger_from_report(report)
    artifact_ledger_integration = report.get(
        "airline_transaction_artifact_ledger_integration",
        {},
    )
    errors += _airline_transaction_artifact_ledger_public_typed_coherence_errors(
        report,
    )

    if report.get("transaction_id") != TRANSACTION_ID:
        errors += ("transaction_id_mismatch",)
    transaction_ids = {
        report.get("transaction_id"),
        report["transaction_identity"].get("transaction_id"),
    }
    transaction_ids.update(row["transaction_id"] for row in ledger)
    transaction_ids.update(
        fixture["transaction_id"]
        for fixture in fixtures.values()
        if "transaction_id" in fixture
    )
    transaction_ids.add(sandbox.get("transaction_id"))
    transaction_ids.add(bank_sandbox.get("transaction_id"))
    transaction_ids.add(client_orchestration.get("transaction_id"))
    transaction_ids.add(ticket_corridor.get("transaction_id"))
    transaction_ids.update(row["transaction_id"] for row in integrated_trace)
    transaction_ids.update(row["transaction_id"] for row in routing_matrix)
    transaction_ids.add(final_summary.get("transaction_id"))
    if isinstance(
        corridor_report,
        corridor_runtime.AirlineTicketPurchaseCorridorRunReportV01,
    ):
        transaction_ids.add(corridor_report.transaction_id)
        transaction_ids.update(phase.transaction_id for phase in corridor_report.phase_results)
        transaction_ids.update(
            transition.transaction_id for transition in corridor_report.transitions
        )
    if isinstance(
        ledger_source_bundle,
        ledger_collector.AirlineTransactionArtifactLedgerSourceBundleV01,
    ):
        transaction_ids.add(ledger_source_bundle.transaction_id)
    if isinstance(
        artifact_ledger,
        ledger_contracts.AirlineTransactionArtifactLedgerV01,
    ):
        transaction_ids.add(artifact_ledger.transaction_id)
    transaction_ids.update(row.get("transaction_id") for row in binding_matrix)
    if transaction_ids != {TRANSACTION_ID}:
        errors += ("transaction_id_set_mismatch",)
    if {row["transaction_id"] for row in ledger} != {TRANSACTION_ID}:
        errors += ("ledger_transaction_id_mismatch",)
    if len(ledger) != 15:
        errors += ("ledger_entry_count_mismatch",)
    if set(report["participants"]) != {"ClientRoot", "AirlineRoot", "BankRoot"}:
        errors += ("participant_set_mismatch",)
    for view_key in ("client_root_view", "airline_root_view", "bank_root_view"):
        if not report.get(view_key):
            errors += (f"missing_root_view:{view_key}",)
    if sandbox.get("sandbox_status") != STATUS_PASS:
        errors += ("airline_offer_hold_sandbox_not_pass",)
    if sandbox.get("transaction_id") != TRANSACTION_ID:
        errors += ("airline_offer_hold_sandbox_transaction_id_mismatch",)
    for key in (
        "offer_request_validated",
        "mock_inventory_checked",
        "mock_fare_checked",
        "baggage_rule_checked",
        "offer_ttl_checked",
        "offer_response_created",
        "offer_hold_commit_packet_created",
        "offer_hold_commit_packet_root_created",
        "offer_hold_commit_packet_validated",
        "offer_hold_receipt_created",
        "offer_hold_receipt_validated",
        "offer_hold_receipt_evidence_only",
    ):
        if sandbox.get(key) is not True:
            errors += (f"airline_offer_hold_sandbox_flag_false:{key}",)
    if sandbox.get("offer_hold_commit_packet_created_by") != "airline_root":
        errors += ("offer_hold_commit_packet_creator_not_airline_root",)
    for key in (
        "offer_hold_receipt_payment_permission_created",
        "offer_hold_receipt_ticket_permission_created",
        "real_airline_api_called",
        "real_booking_created",
        "real_ticket_issued",
    ):
        if sandbox.get(key) is not False:
            errors += (f"airline_offer_hold_sandbox_flag_true:{key}",)
    if sandbox.get("real_world_effects_count") != 0:
        errors += ("airline_offer_hold_sandbox_effects_nonzero",)

    offer_hold_packet = fixtures["AirlineOfferHoldCommitPacketV01"]
    if offer_hold_packet.get("created_by") != "airline_root":
        errors += ("offer_hold_packet_fixture_creator_not_airline_root",)
    if offer_hold_packet.get("root_created") is not True:
        errors += ("offer_hold_packet_fixture_not_root_created",)
    if offer_hold_packet.get("allowed_root_id") != AIRLINE_ROOT_ID:
        errors += ("offer_hold_packet_fixture_wrong_root",)
    for key in (
        "payment_permission_created",
        "ticket_permission_created",
        "real_airline_api_allowed",
        "real_booking_allowed",
    ):
        if offer_hold_packet.get(key) is not False:
            errors += (f"offer_hold_packet_forbidden_flag_true:{key}",)

    offer_hold_receipt = fixtures["AirlineOfferHoldReceiptV01"]
    if (
        offer_hold_receipt.get("created_by")
        != corridor_contracts.ADAPTER_AIRLINE_HOLD_SANDBOX
    ):
        errors += ("offer_hold_receipt_fixture_creator_not_hold_sandbox",)
    if offer_hold_receipt.get("root_owner") != AIRLINE_ROOT_ID:
        errors += ("offer_hold_receipt_fixture_wrong_root_owner",)
    if offer_hold_receipt.get("evidence_only") is not True:
        errors += ("offer_hold_receipt_not_evidence_only",)
    if offer_hold_receipt.get("payment_permission_created") is not False:
        errors += ("offer_hold_receipt_payment_permission_created",)
    if offer_hold_receipt.get("ticket_permission_created") is not False:
        errors += ("offer_hold_receipt_ticket_permission_created",)

    if bank_sandbox.get("sandbox_status") != STATUS_PASS:
        errors += ("bank_payment_authorization_sandbox_not_pass",)
    if bank_sandbox.get("transaction_id") != TRANSACTION_ID:
        errors += ("bank_payment_authorization_sandbox_transaction_id_mismatch",)
    for key in (
        "offer_hold_receipt_observed",
        "client_purchase_approval_evidence_observed",
        "payment_profile_sealed_ref_observed",
        "amount_currency_validated",
        "merchant_airline_ref_validated",
        "payment_token_ref_validated",
        "debtor_slot_ref_validated",
        "idempotency_checked",
        "expiry_ttl_checked",
        "bank_payment_intent_created",
        "bank_payment_consent_created",
        "bank_payment_authorization_commit_packet_created",
        "bank_payment_authorization_commit_packet_root_created",
        "bank_payment_authorization_commit_packet_validated",
        "payment_authorization_receipt_created",
        "payment_authorization_receipt_validated",
        "payment_status_receipt_created",
        "payment_status_receipt_validated",
        "payment_authorization_receipt_evidence_only",
        "payment_status_receipt_evidence_only",
    ):
        if bank_sandbox.get(key) is not True:
            errors += (f"bank_payment_authorization_sandbox_flag_false:{key}",)
    if bank_sandbox.get("bank_payment_authorization_commit_packet_created_by") != "bank_root":
        errors += ("bank_payment_authorization_packet_creator_not_bank_root",)
    for key in (
        "payment_authorization_receipt_ticket_permission_created",
        "payment_authorization_receipt_real_payment_executed",
        "payment_status_receipt_settlement_executed",
        "payment_status_receipt_ticket_permission_created",
        "bank_root_created_ticket",
        "real_bank_api_called",
        "real_payment_executed",
        "real_settlement_executed",
        "real_ticket_issued",
    ):
        if bank_sandbox.get(key) is not False:
            errors += (f"bank_payment_authorization_sandbox_flag_true:{key}",)
    if bank_sandbox.get("real_world_effects_count") != 0:
        errors += ("bank_payment_authorization_sandbox_effects_nonzero",)

    bank_payment_packet = fixtures["BankPaymentAuthorizationCommitPacketV01"]
    if bank_payment_packet.get("created_by") != "bank_root":
        errors += ("bank_payment_packet_fixture_creator_not_bank_root",)
    if bank_payment_packet.get("root_created") is not True:
        errors += ("bank_payment_packet_fixture_not_root_created",)
    if bank_payment_packet.get("allowed_root_id") != BANK_ROOT_ID:
        errors += ("bank_payment_packet_fixture_wrong_root",)
    for key in (
        "ticket_permission_created",
        "real_payment_allowed",
        "real_bank_api_allowed",
        "real_settlement_allowed",
    ):
        if bank_payment_packet.get(key) is not False:
            errors += (f"bank_payment_packet_forbidden_flag_true:{key}",)

    payment_authorization_receipt = fixtures["BankPaymentAuthorizationReceiptV01"]
    if payment_authorization_receipt.get("evidence_only") is not True:
        errors += ("payment_authorization_receipt_not_evidence_only",)
    if payment_authorization_receipt.get("ticket_created") is not False:
        errors += ("payment_authorization_receipt_ticket_created",)
    if payment_authorization_receipt.get("real_payment_executed") is not False:
        errors += ("payment_authorization_receipt_real_payment_executed",)

    payment_status_receipt = fixtures["BankPaymentStatusReceiptV01"]
    if payment_status_receipt.get("evidence_only") is not True:
        errors += ("payment_status_receipt_not_evidence_only",)
    if payment_status_receipt.get("settlement_executed") is not False:
        errors += ("payment_status_receipt_settlement_executed",)
    if payment_status_receipt.get("real_payment_executed") is not False:
        errors += ("payment_status_receipt_real_payment_executed",)

    if client_orchestration.get("orchestration_status") != STATUS_PASS:
        errors += ("client_purchase_orchestration_not_pass",)
    if client_orchestration.get("transaction_id") != TRANSACTION_ID:
        errors += ("client_purchase_orchestration_transaction_id_mismatch",)
    for key in (
        "travel_intent_observed",
        "passenger_sealed_refs_observed",
        "payment_profile_sealed_ref_observed",
        "offer_response_observed",
        "offer_hold_receipt_observed",
        "selected_offer_within_user_max_price",
        "client_purchase_approval_evidence_created",
        "client_purchase_approval_evidence_root_created",
        "client_purchase_approval_evidence_validated",
        "client_purchase_approval_evidence_evidence_only",
        "routed_to_bank_root",
        "routed_to_airline_root",
        "bank_payment_authorization_receipt_observed",
        "bank_payment_status_receipt_observed",
        "client_final_purchase_summary_created",
    ):
        if client_orchestration.get(key) is not True:
            errors += (f"client_purchase_orchestration_flag_false:{key}",)
    if (
        client_orchestration.get("client_purchase_approval_evidence_created_by")
        != "client_root"
    ):
        errors += ("client_purchase_approval_creator_not_client_root",)
    for key in (
        "client_root_authorized_bank_payment",
        "client_root_issued_ticket",
        "client_root_created_airline_order",
        "client_root_created_bank_receipt",
        "client_root_created_action_commit_packet",
        "raw_passport_exposed",
        "raw_card_exposed",
        "raw_iban_exposed",
        "raw_payment_token_exposed",
        "real_payment_executed",
        "real_ticket_issued",
        "real_booking_created",
    ):
        if client_orchestration.get(key) is not False:
            errors += (f"client_purchase_orchestration_flag_true:{key}",)
    if client_orchestration.get("real_world_effects_count") != 0:
        errors += ("client_purchase_orchestration_effects_nonzero",)

    client_purchase_approval = fixtures["ClientPurchaseApprovalEvidenceV01"]
    if client_purchase_approval.get("created_by") != "client_root":
        errors += ("client_purchase_approval_fixture_creator_not_client_root",)
    if client_purchase_approval.get("root_created") is not True:
        errors += ("client_purchase_approval_fixture_not_root_created",)
    if client_purchase_approval.get("evidence_only") is not True:
        errors += ("client_purchase_approval_fixture_not_evidence_only",)
    for key in (
        "bank_authority_created",
        "airline_authority_created",
        "payment_permission_created",
        "ticket_permission_created",
        "action_commit_packet_created",
        "receipt_created",
    ):
        if client_purchase_approval.get(key) is not False:
            errors += (f"client_purchase_approval_forbidden_flag_true:{key}",)

    client_summary = fixtures["ClientFinalTravelSummaryV01"]
    if client_summary.get("evidence_only") is not True:
        errors += ("client_final_summary_not_evidence_only",)
    for key in (
        "ticket_issued",
        "real_ticket_issued",
        "real_payment_executed",
        "real_booking_created",
    ):
        if client_summary.get(key) is not False:
            errors += (f"client_final_summary_forbidden_flag_true:{key}",)

    if ticket_corridor.get("corridor_status") != STATUS_PASS:
        errors += ("airline_ticket_issue_mock_corridor_not_pass",)
    if ticket_corridor.get("transaction_id") != TRANSACTION_ID:
        errors += ("airline_ticket_issue_mock_corridor_transaction_id_mismatch",)
    for key in (
        "offer_hold_receipt_observed",
        "client_purchase_approval_evidence_observed",
        "payment_authorization_receipt_observed",
        "payment_status_receipt_observed",
        "offer_hold_ttl_freshness_validated",
        "selected_offer_match_validated",
        "amount_currency_match_validated",
        "merchant_airline_ref_match_validated",
        "passenger_sealed_ref_validated",
        "payment_evidence_validated_against_offer_hold",
        "raw_passport_absent",
        "raw_card_absent",
        "raw_payment_token_absent",
        "airline_ticket_issue_commit_packet_created",
        "airline_ticket_issue_commit_packet_root_created",
        "airline_ticket_issue_commit_packet_validated",
        "airline_order_created_receipt_created",
        "airline_order_created_receipt_validated",
        "mock_ticket_receipt_created",
        "mock_ticket_receipt_validated",
        "mock_pnr_created",
        "mock_pnr_validated",
        "mock_ticket_receipt_evidence_only",
    ):
        if ticket_corridor.get(key) is not True:
            errors += (f"airline_ticket_issue_corridor_flag_false:{key}",)
    if ticket_corridor.get("airline_ticket_issue_commit_packet_created_by") != "airline_root":
        errors += ("airline_ticket_issue_packet_creator_not_airline_root",)
    for key in (
        "mock_ticket_receipt_real_ticket",
        "mock_ticket_receipt_payment_created",
        "mock_pnr_real_booking",
        "payment_authorization_receipt_created_ticket",
        "client_purchase_approval_created_ticket",
        "offer_hold_receipt_created_ticket",
        "airline_root_authorized_payment",
        "airline_root_called_real_airline_api",
        "airline_root_called_real_gds_api",
        "real_ticket_issued",
        "real_booking_created",
        "real_payment_executed",
        "real_settlement_executed",
    ):
        if ticket_corridor.get(key) is not False:
            errors += (f"airline_ticket_issue_corridor_flag_true:{key}",)
    if ticket_corridor.get("real_world_effects_count") != 0:
        errors += ("airline_ticket_issue_corridor_effects_nonzero",)

    ticket_issue_packet = fixtures["AirlineTicketIssueCommitPacketV01"]
    if ticket_issue_packet.get("created_by") != "airline_root":
        errors += ("ticket_issue_packet_fixture_creator_not_airline_root",)
    if ticket_issue_packet.get("root_created") is not True:
        errors += ("ticket_issue_packet_fixture_not_root_created",)
    if ticket_issue_packet.get("allowed_root_id") != AIRLINE_ROOT_ID:
        errors += ("ticket_issue_packet_fixture_wrong_root",)
    for key in (
        "real_ticket_allowed",
        "real_booking_allowed",
        "real_airline_api_allowed",
        "real_payment_allowed",
    ):
        if ticket_issue_packet.get(key) is not False:
            errors += (f"ticket_issue_packet_forbidden_flag_true:{key}",)

    order_receipt = fixtures["AirlineOrderCreatedReceiptV01"]
    if order_receipt.get("created_by") != "airline_root":
        errors += ("order_receipt_fixture_creator_not_airline_root",)
    if order_receipt.get("evidence_only") is not True:
        errors += ("order_receipt_not_evidence_only",)
    for key in ("payment_created", "real_ticket_issued", "real_booking_created"):
        if order_receipt.get(key) is not False:
            errors += (f"order_receipt_forbidden_flag_true:{key}",)

    mock_ticket_receipt = fixtures["MockTicketReceiptV01"]
    if (
        mock_ticket_receipt.get("created_by")
        != corridor_contracts.ADAPTER_AIRLINE_TICKET_SANDBOX
    ):
        errors += ("mock_ticket_receipt_fixture_creator_not_ticket_sandbox",)
    if mock_ticket_receipt.get("root_owner") != AIRLINE_ROOT_ID:
        errors += ("mock_ticket_receipt_fixture_wrong_root_owner",)
    if mock_ticket_receipt.get("evidence_only") is not True:
        errors += ("mock_ticket_receipt_not_evidence_only",)
    for key in (
        "real_ticket",
        "real_travel_booking_created",
        "payment_created",
        "future_payment_permission_created",
    ):
        if mock_ticket_receipt.get(key) is not False:
            errors += (f"mock_ticket_receipt_forbidden_flag_true:{key}",)

    mock_pnr = fixtures["MockPNRV01"]
    if mock_pnr.get("created_by") != "airline_root":
        errors += ("mock_pnr_fixture_creator_not_airline_root",)
    if mock_pnr.get("mock_only") is not True:
        errors += ("mock_pnr_fixture_not_mock_only",)
    if mock_pnr.get("real_booking") is not False:
        errors += ("mock_pnr_real_booking",)

    mock_purchase_receipt = fixtures["MockPurchaseReceiptV01"]
    if mock_purchase_receipt.get("created_by") != "client_completion_observer":
        errors += ("mock_purchase_receipt_creator_not_completion_observer",)
    if mock_purchase_receipt.get("root_owner") != CLIENT_ROOT_ID:
        errors += ("mock_purchase_receipt_wrong_root_owner",)
    if mock_purchase_receipt.get("receipt_id") == client_summary.get("summary_id"):
        errors += ("mock_purchase_receipt_reused_client_final_summary_id",)
    if mock_purchase_receipt.get("source_client_purchase_intent_id") != (
        "client_purchase_intent:client_001:001"
    ):
        errors += ("mock_purchase_receipt_wrong_purchase_intent_source",)
    if mock_purchase_receipt.get("source_payment_authorization_ref_id") != (
        "bank_payment_authorization_ref:mock_bank_a:001"
    ):
        errors += ("mock_purchase_receipt_wrong_payment_ref_source",)
    if mock_purchase_receipt.get("source_mock_ticket_receipt_id") != (
        fixtures["MockTicketReceiptV01"]["receipt_id"]
    ):
        errors += ("mock_purchase_receipt_wrong_ticket_receipt_source",)
    if mock_purchase_receipt.get("evidence_only") is not True:
        errors += ("mock_purchase_receipt_not_evidence_only",)
    for key in (
        "side_root_finals_replaced",
        "root_truth_rewritten",
        "future_permission_created",
        "real_payment_executed",
        "real_ticket_issued",
        "real_booking_created",
    ):
        if mock_purchase_receipt.get(key) is not False:
            errors += (f"mock_purchase_receipt_forbidden_flag_true:{key}",)
    if mock_purchase_receipt.get("real_world_effects_count") != 0:
        errors += ("mock_purchase_receipt_effects_nonzero",)

    if client_summary.get("mock_ticket_receipt_id") != (
        fixtures["MockTicketReceiptV01"]["receipt_id"]
    ):
        errors += ("client_final_summary_missing_mock_ticket_receipt",)
    if client_summary.get("mock_purchase_receipt_id") != (
        "mock_purchase_receipt:client_001:001"
    ):
        errors += ("client_final_summary_missing_mock_purchase_receipt",)
    if (
        client_summary.get("current_client_status")
        != "mock_ticket_evidence_received_no_real_travel_booking"
    ):
        errors += ("client_final_summary_status_mismatch",)
    if client_summary.get("mock_ticket_evidence_received") is not True:
        errors += ("client_final_summary_mock_ticket_evidence_missing",)

    if len(integrated_trace) != 17:
        errors += ("integrated_trace_phase_count_mismatch",)
    if {row["transaction_id"] for row in integrated_trace} != {TRANSACTION_ID}:
        errors += ("integrated_trace_transaction_id_mismatch",)
    expected_phase_ids = (
        "client_travel_intent_recorded",
        "client_to_airline_offer_request",
        "airline_offer_hold_sandbox_completed",
        "airline_to_client_offer_hold_receipt_returned",
        "client_offer_selected",
        "client_purchase_approval_evidence_created",
        "client_to_bank_payment_authorization_request",
        "bank_payment_authorization_sandbox_completed",
        "bank_to_client_payment_authorization_receipt_returned",
        "bank_to_client_payment_status_receipt_returned",
        "client_to_airline_payment_evidence_forwarded",
        "airline_ticket_issue_mock_corridor_completed",
        "airline_to_client_order_created_receipt_returned",
        "airline_to_client_mock_ticket_receipt_returned",
        "airline_to_client_mock_pnr_returned",
        "client_final_mock_travel_summary_created",
        "final_shared_summary_fixture_created",
    )
    if tuple(row["phase_id"] for row in integrated_trace) != expected_phase_ids:
        errors += ("integrated_trace_phase_order_mismatch",)
    for row in integrated_trace:
        if row.get("authority_transferred") is not False:
            errors += ("integrated_trace_authority_transfer",)
        if row.get("real_world_effects_count") != 0:
            errors += ("integrated_trace_effects_nonzero",)
        for key in (
            "raw_secrets_exposed",
            "real_ticket_claimed",
            "real_payment_claimed",
            "real_booking_claimed",
        ):
            if row.get(key) is not False:
                errors += (f"integrated_trace_forbidden_flag_true:{key}",)

    if len(routing_matrix) != 6:
        errors += ("cross_root_routing_row_count_mismatch",)
    expected_routes = (
        (CLIENT_ROOT_ID, AIRLINE_ROOT_ID),
        (AIRLINE_ROOT_ID, CLIENT_ROOT_ID),
        (CLIENT_ROOT_ID, BANK_ROOT_ID),
        (BANK_ROOT_ID, CLIENT_ROOT_ID),
        (CLIENT_ROOT_ID, AIRLINE_ROOT_ID),
        (AIRLINE_ROOT_ID, CLIENT_ROOT_ID),
    )
    actual_routes = tuple(
        (row["source_root_id"], row["target_root_id"]) for row in routing_matrix
    )
    if actual_routes != expected_routes:
        errors += ("cross_root_routing_order_mismatch",)
    for row in routing_matrix:
        if row.get("evidence_only") is not True:
            errors += ("cross_root_routing_not_evidence_only",)
        if row.get("authority_transferred") is not False:
            errors += ("cross_root_routing_authority_transfer",)
        if row.get("real_world_effects_count") != 0:
            errors += ("cross_root_routing_effects_nonzero",)
    for key in (
        "raw_passport_exposed",
        "raw_card_exposed",
        "payment_permission_created",
        "ticket_permission_created",
        "bank_authority_created_by_client",
        "raw_iban_exposed",
        "real_payment_executed",
        "airline_authority_created_by_client",
        "ticket_permission_created_by_payment_receipt",
        "real_ticket_issued",
        "real_booking_created",
        "payment_created",
    ):
        for row in routing_matrix:
            if key in row and row[key] is not False:
                errors += (f"cross_root_routing_forbidden_flag_true:{key}",)

    if final_summary.get("final_status") != STATUS_PASS:
        errors += ("final_tri_party_mock_summary_not_pass",)
    if final_summary.get("transaction_id") != TRANSACTION_ID:
        errors += ("final_tri_party_mock_summary_transaction_id_mismatch",)
    expected_selected_offer_id = fixtures["AirlineOfferCandidateV01"]["offer_id"]
    expected_offer_hold_receipt_id = fixtures["AirlineOfferHoldReceiptV01"][
        "receipt_id"
    ]
    expected_order_created_receipt_id = fixtures["AirlineOrderCreatedReceiptV01"][
        "receipt_id"
    ]
    expected_mock_ticket_receipt_id = fixtures["MockTicketReceiptV01"]["receipt_id"]
    expected_mock_purchase_receipt_id = fixtures["MockPurchaseReceiptV01"][
        "receipt_id"
    ]
    expected_mock_pnr = fixtures["MockPNRV01"]["pnr"]
    for key, expected in (
        (
            "client_view_status",
            "mock_ticket_evidence_received_no_real_travel_booking",
        ),
        ("airline_view_status", "mock_order_ticket_pnr_evidence_created"),
        ("bank_view_status", "mock_payment_authorized_not_settled"),
        ("selected_offer_id", expected_selected_offer_id),
        ("offer_hold_receipt_id", expected_offer_hold_receipt_id),
        (
            "payment_authorization_receipt_id",
            "payment_authorization_receipt:mock_bank_a:001",
        ),
        (
            "payment_authorization_ref_id",
            "bank_payment_authorization_ref:mock_bank_a:001",
        ),
        ("payment_status_receipt_id", "payment_status_receipt:mock_bank_a:001"),
        ("order_created_receipt_id", expected_order_created_receipt_id),
        ("mock_ticket_receipt_id", expected_mock_ticket_receipt_id),
        ("mock_purchase_receipt_id", expected_mock_purchase_receipt_id),
        ("mock_pnr", expected_mock_pnr),
    ):
        if final_summary.get(key) != expected:
            errors += (f"final_tri_party_mock_summary_value_mismatch:{key}",)
    if final_summary.get("receipts_evidence_only") is not True:
        errors += ("final_tri_party_mock_summary_receipts_not_evidence_only",)
    for key in (
        "authority_transferred_between_roots",
        "client_root_issued_ticket",
        "airline_root_authorized_payment",
        "bank_root_created_ticket",
        "real_airline_api_called",
        "real_bank_api_called",
        "real_gds_api_called",
        "real_payment_executed",
        "real_settlement_executed",
        "real_ticket_issued",
        "real_booking_created",
        "provider_called",
        "network_used",
        "gemini_called",
    ):
        if final_summary.get(key) is not False:
            errors += (f"final_tri_party_mock_summary_flag_true:{key}",)
    if final_summary.get("real_world_effects_count") != 0:
        errors += ("final_tri_party_mock_summary_effects_nonzero",)

    if not isinstance(
        corridor_report,
        corridor_runtime.AirlineTicketPurchaseCorridorRunReportV01,
    ):
        errors += ("airline_corridor_report_missing",)
    else:
        corridor_accepted, corridor_errors = (
            corridor_runtime.validate_airline_ticket_purchase_corridor_run_v01(
                corridor_report,
            )
        )
        if not corridor_accepted or corridor_errors:
            errors += ("airline_corridor_public_validation_rejected",)
        if corridor_report.final_status != corridor_runtime.STATUS_PASS:
            errors += ("airline_corridor_not_pass",)
        if corridor_report.transaction_id != report["transaction_id"]:
            errors += ("airline_corridor_transaction_id_mismatch",)
        if tuple(phase.phase_id for phase in corridor_report.phase_results) != (
            corridor_runtime.PHASE_ORDER
        ):
            errors += ("airline_corridor_phase_order_mismatch",)
        if len(corridor_report.phase_results) != 5:
            errors += ("airline_corridor_phase_count_mismatch",)
        if any(
            phase.phase_status != corridor_runtime.STATUS_PASS
            for phase in corridor_report.phase_results
        ):
            errors += ("airline_corridor_phase_not_pass",)
        if len(corridor_report.transitions) != 4:
            errors += ("airline_corridor_transition_count_mismatch",)
        if any(
            transition.transition_status != corridor_runtime.STATUS_PASS
            for transition in corridor_report.transitions
        ):
            errors += ("airline_corridor_transition_not_pass",)
        corridor_counter_table = corridor_report.counter_table
        for key, expected in (
            ("client_root_phase_gate_pass_count", 2),
            ("airline_root_phase_gate_pass_count", 2),
            ("bank_root_phase_gate_pass_count", 1),
            ("fixture_receipts_observed_count", 3),
            ("runtime_receipts_created_count", 0),
            ("runtime_packets_created_count", 0),
            ("adapter_execution_count", 0),
            ("cross_root_authority_transfer_count", 0),
            ("core_no_post_root_reasoning_validation_count", 5),
            ("provider_called_count", 0),
            ("network_used_count", 0),
            ("gemini_called_count", 0),
            ("real_world_effects_count", 0),
        ):
            if corridor_counter_table.get(key) != expected:
                errors += (f"airline_corridor_counter_mismatch:{key}",)
        if any(phase.authority_transferred for phase in corridor_report.phase_results):
            errors += ("airline_corridor_authority_transfer",)
        if any(
            transition.semantic_reasoning_restarted
            for transition in corridor_report.transitions
        ):
            errors += ("airline_corridor_post_root_reasoning_restart",)

    if len(binding_matrix) < 14:
        errors += ("airline_corridor_binding_row_count_low",)
    if any(row.get("values_match") is not True for row in binding_matrix):
        errors += ("airline_corridor_binding_mismatch",)
    if any(row.get("raw_secret_used") is not False for row in binding_matrix):
        errors += ("airline_corridor_binding_raw_secret_used",)
    if any(row.get("authority_transferred") is not False for row in binding_matrix):
        errors += ("airline_corridor_binding_authority_transfer",)
    if {
        row.get("transaction_id")
        for row in binding_matrix
    } != {report["transaction_id"]}:
        errors += ("airline_corridor_binding_transaction_id_mismatch",)
    transaction_binding_rows = [
        row for row in binding_matrix if row.get("binding_id") == "transaction_id"
    ]
    if len(transaction_binding_rows) != 1:
        errors += ("airline_corridor_transaction_binding_row_mismatch",)
    elif (
        transaction_binding_rows[0].get("unique_transaction_id_count") != 1
        or transaction_binding_rows[0].get("all_transaction_ids_match") is not True
    ):
        errors += ("airline_corridor_transaction_binding_row_mismatch",)

    if not hasattr(corridor_integration, "get"):
        errors += ("airline_corridor_integration_missing",)
    else:
        for key, expected in (
            ("integration_status", STATUS_PASS),
            ("transaction_id", report["transaction_id"]),
            ("source_runner_id", RUN_ID),
            ("corridor_final_status", corridor_runtime.STATUS_PASS),
            ("corridor_public_validation_accepted", True),
            ("corridor_report_bound_to_projected_fixtures", True),
            ("five_root_centered_phases_observed", True),
            ("existing_runner_artifacts_projected", True),
            ("parallel_fixture_transaction_created", False),
            ("duplicate_corridor_execution_count", 0),
            ("unique_transaction_id_count", 1),
            ("all_transaction_ids_match", True),
            ("runtime_packets_created_count", 0),
            ("runtime_receipts_created_count", 0),
            ("adapter_execution_count", 0),
            ("authority_transferred", False),
            ("real_world_effects_count", 0),
            (
                "next_gate",
                "airline_ticket_purchase_corridor_v01_slice_e_audit_and_human_story",
            ),
        ):
            if corridor_integration.get(key) != expected:
                errors += (f"airline_corridor_integration_mismatch:{key}",)

    try:
        expected_fixture_bundle = (
            _build_airline_ticket_purchase_corridor_fixture_bundle_v01(report)
        )
        fixture_bundle_accepted, fixture_bundle_errors = (
            corridor_runtime.validate_airline_ticket_purchase_corridor_fixture_bundle_v01(
                expected_fixture_bundle,
                contract_context=corridor_contract_context,
            )
        )
        expected_binding_matrix = _airline_ticket_purchase_corridor_binding_matrix_v01(
            report,
            expected_fixture_bundle,
            corridor_report,
        )
        expected_integration = _airline_ticket_purchase_corridor_integration_summary(
            report,
            expected_fixture_bundle,
            corridor_report,
            corridor_accepted if "corridor_accepted" in locals() else False,
            expected_binding_matrix,
            1,
            contract_context=corridor_contract_context,
        )
    except (AttributeError, KeyError, TypeError, ValueError):
        errors += ("airline_corridor_projection_failed",)
    else:
        if tuple(binding_matrix) != expected_binding_matrix:
            errors += ("airline_corridor_binding_matrix_mismatch",)
        if not fixture_bundle_accepted or fixture_bundle_errors:
            errors += ("airline_corridor_projected_source_not_pass",)
        fixture_report_binding_accepted, fixture_report_binding_errors = (
            corridor_runtime
            .validate_airline_ticket_purchase_corridor_report_against_fixture_bundle_v01(
                expected_fixture_bundle,
                corridor_report,
                contract_context=corridor_contract_context,
            )
        )
        if not fixture_report_binding_accepted or fixture_report_binding_errors:
            errors += ("airline_corridor_fixture_report_binding_failed",)
        if dict(corridor_integration) != expected_integration:
            errors += ("airline_corridor_integration_mismatch:derived_fields",)

    if not isinstance(
        ledger_source_bundle,
        ledger_collector.AirlineTransactionArtifactLedgerSourceBundleV01,
    ):
        errors += ("airline_transaction_artifact_ledger_source_bundle_missing",)
    if not isinstance(
        ledger_source_validation,
        ledger_collector.AirlineTransactionArtifactLedgerSourceValidationReportV01,
    ):
        errors += ("airline_transaction_artifact_ledger_source_validation_missing",)
    elif (
        ledger_source_validation.validation_status != ledger_collector.STATUS_PASS
        or ledger_source_validation.validation_errors != ()
    ):
        errors += ("airline_transaction_artifact_ledger_source_validation_failed",)
    if not isinstance(
        artifact_ledger,
        ledger_contracts.AirlineTransactionArtifactLedgerV01,
    ):
        errors += ("airline_transaction_artifact_ledger_missing",)
    else:
        actual_geometry = _actual_airline_transaction_artifact_ledger_geometry(
            artifact_ledger,
        )
        geometry_errors = _airline_transaction_artifact_ledger_geometry_errors(
            artifact_ledger,
        )
        if artifact_ledger.validation_status != ledger_contracts.STATUS_PASS:
            errors += ("airline_transaction_artifact_ledger_not_pass",)
        if artifact_ledger.validation_errors != ():
            errors += ("airline_transaction_artifact_ledger_errors_not_empty",)
        if actual_geometry["entry_count"] != 19:
            errors += ("airline_transaction_artifact_ledger_entry_count_mismatch",)
        if actual_geometry["dependency_edge_count"] != 29:
            errors += ("airline_transaction_artifact_ledger_edge_count_mismatch",)
        if actual_geometry["root_final_count"] != 3:
            errors += ("airline_transaction_artifact_ledger_root_final_mismatch",)
        for geometry_error in geometry_errors:
            errors += (f"airline_transaction_artifact_ledger:{geometry_error}",)
        for key, expected in (
            ("provider_called_count", 0),
            ("network_used_count", 0),
            ("gemini_called_count", 0),
            ("ledger_created_authority_count", 0),
            ("ledger_created_permission_count", 0),
            ("ledger_created_action_count", 0),
            ("real_world_effects_count", 0),
        ):
            if getattr(artifact_ledger, key) != expected:
                errors += (f"airline_transaction_artifact_ledger_counter_mismatch:{key}",)
    if not hasattr(artifact_ledger_integration, "get"):
        errors += ("airline_transaction_artifact_ledger_integration_missing",)
    else:
        for key, expected in (
            ("integration_status", STATUS_PASS),
            ("source_bundle_validation_status", STATUS_PASS),
            ("ledger_validation_status", STATUS_PASS),
            ("transaction_id", report["transaction_id"]),
            ("entry_count", 19),
            ("dependency_edge_count", 29),
            ("root_final_count", 3),
            ("actual_entry_count", 19),
            ("actual_dependency_edge_count", 29),
            ("actual_root_final_count", 3),
            ("stored_entry_count", 19),
            ("stored_dependency_edge_count", 29),
            ("stored_root_final_count", 3),
            ("source_bundle_collection_count", 1),
            ("ledger_collection_count", 1),
            ("ledger_validation_count", 1),
            ("corridor_execution_count", 1),
            ("duplicate_transaction_count", 0),
            ("duplicate_corridor_execution_count", 0),
            ("duplicate_ledger_collection_count", 0),
            ("source_reconstruction_count", 0),
            ("provider_calls_added_by_ledger_count", 0),
            ("network_calls_added_by_ledger_count", 0),
            ("gemini_calls_added_by_ledger_count", 0),
            ("ledger_created_authority_count", 0),
            ("ledger_created_permission_count", 0),
            ("ledger_created_action_count", 0),
            ("real_world_effects_count", 0),
            ("artifact_written_count", 0),
        ):
            if artifact_ledger_integration.get(key) != expected:
                errors += (f"airline_transaction_artifact_ledger_mismatch:{key}",)
        if artifact_ledger_integration.get("source_bundle_validation_errors") != ():
            errors += ("airline_transaction_artifact_ledger_source_errors",)
        if artifact_ledger_integration.get("ledger_validation_errors") != ():
            errors += ("airline_transaction_artifact_ledger_validation_errors",)
    if isinstance(
        ledger_source_bundle,
        ledger_collector.AirlineTransactionArtifactLedgerSourceBundleV01,
    ) and isinstance(
        artifact_ledger,
        ledger_contracts.AirlineTransactionArtifactLedgerV01,
    ):
        refs = ledger_source_bundle.expected_source_refs
        if (
            artifact_ledger.source_run_ref != refs.source_run_ref
            or artifact_ledger.source_causal_report_ref
            != refs.source_causal_report_ref
            or artifact_ledger.source_corridor_report_ref
            != refs.source_corridor_report_ref
        ):
            errors += ("airline_transaction_artifact_ledger_source_ref_mismatch",)

    if not all(row["boundary_preserved"] and row["violation_count"] == 0 for row in report["root_boundary_matrix"]):
        errors += ("root_boundary_violation",)
    if not all(row["boundary_preserved"] and row["violation_count"] == 0 for row in report["receipt_boundary_matrix"]):
        errors += ("receipt_boundary_violation",)

    privacy = report["privacy_boundary_matrix"]
    for key in (
        "raw_passport_exposed_count",
        "raw_card_exposed_count",
        "raw_iban_exposed_count",
        "raw_payment_token_exposed_count",
        "raw_birthdate_exposed_count",
        "raw_document_number_exposed_count",
    ):
        if privacy.get(key) != 0:
            errors += (f"privacy_counter_nonzero:{key}",)
    for key in (
        "passenger_sealed_ref_only",
        "payment_profile_sealed_ref_only",
        "vault_refs_not_llm_context",
        "no_raw_private_profile_in_provider_context",
        "no_raw_secrets_in_artifacts",
    ):
        if privacy.get(key) is not True:
            errors += (f"privacy_flag_false:{key}",)

    if any(actor["executed_in_slice_b"] for actor in report["future_semantic_actor_topology"]):
        errors += ("future_semantic_actor_executed",)
    if any(
        actor["creates_authority"]
        or actor["creates_action_commit_packet"]
        or actor["creates_receipt"]
        or actor["creates_ticket"]
        or actor["executes_payment"]
        or actor["calls_real_api"]
        for actor in report["future_semantic_actor_topology"]
    ):
        errors += ("future_semantic_actor_boundary_violation",)

    fractal_cells = tuple(
        cell
        for cells in report["future_vertical_fractal_map"].values()
        for cell in cells
    )
    if len(fractal_cells) < 14:
        errors += ("future_vertical_fractal_cell_count_low",)
    if any(cell["executed_in_slice_b"] for cell in fractal_cells):
        errors += ("future_vertical_fractal_cell_executed",)
    if any(cell["creates_authority"] or cell["real_world_effects_count"] != 0 for cell in fractal_cells):
        errors += ("future_vertical_fractal_cell_boundary_violation",)

    required_zero_counter_keys = (
        "future_semantic_actor_roles_executed_count",
        "future_vertical_fractal_cells_executed_count",
        "client_root_issued_ticket_count",
        "airline_root_authorized_payment_count",
        "bank_root_created_ticket_count",
        "payment_receipt_created_ticket_count",
        "ticket_receipt_created_payment_count",
        "raw_passport_exposed_count",
        "raw_card_exposed_count",
        "raw_iban_exposed_count",
        "raw_payment_token_exposed_count",
        "real_airline_api_called_count",
        "real_bank_api_called_count",
        "real_payment_executed_count",
        "real_settlement_executed_count",
        "real_booking_created_count",
        "real_ticket_issued_count",
        "real_travel_booking_created_count",
        "provider_called_count",
        "network_used_count",
        "gemini_called_count",
        "real_world_effects_count",
        "provider_network_call_count",
        "gemini_call_count",
        "bank_payment_authorization_commit_packet_created_by_client_root_count",
        "bank_payment_authorization_commit_packet_created_by_airline_root_count",
        "payment_authorization_receipt_ticket_permission_created_count",
        "payment_authorization_receipt_real_payment_executed_count",
        "payment_status_receipt_ticket_permission_created_count",
        "payment_status_receipt_settlement_executed_count",
        "client_purchase_approval_evidence_created_by_airline_root_count",
        "client_purchase_approval_evidence_created_by_bank_root_count",
        "client_root_authorized_bank_payment_count",
        "client_root_created_airline_order_count",
        "client_root_created_bank_receipt_count",
        "client_root_created_action_commit_packet_count",
        "client_raw_passport_exposed_count",
        "client_raw_card_exposed_count",
        "client_raw_iban_exposed_count",
        "client_raw_payment_token_exposed_count",
        "airline_ticket_issue_commit_packet_created_by_client_root_count",
        "airline_ticket_issue_commit_packet_created_by_bank_root_count",
        "mock_ticket_receipt_real_ticket_count",
        "mock_pnr_real_booking_count",
        "payment_authorization_receipt_created_ticket_count",
        "client_purchase_approval_created_ticket_count",
        "offer_hold_receipt_created_ticket_count",
        "airline_root_called_real_airline_api_count",
        "airline_root_called_real_gds_api_count",
        "cross_root_authority_transfer_count",
        "cross_root_real_world_effects_count",
        "final_real_ticket_issued_count",
        "final_real_payment_executed_count",
        "final_real_booking_created_count",
        "final_authority_transferred_between_roots_count",
        "airline_ticket_purchase_corridor_fail_count",
        "airline_ticket_purchase_corridor_binding_mismatch_count",
        "airline_ticket_purchase_corridor_parallel_transaction_count",
        "airline_ticket_purchase_corridor_duplicate_execution_count",
        "airline_ticket_purchase_corridor_runtime_receipts_created_count",
        "airline_ticket_purchase_corridor_runtime_packets_created_count",
        "airline_ticket_purchase_corridor_adapter_execution_count",
        "airline_ticket_purchase_corridor_cross_root_authority_transfer_count",
        "airline_ticket_purchase_corridor_post_root_reasoning_restart_count",
        "airline_ticket_purchase_corridor_provider_called_count",
        "airline_ticket_purchase_corridor_network_used_count",
        "airline_ticket_purchase_corridor_gemini_called_count",
        "airline_ticket_purchase_corridor_real_world_effects_count",
    )
    for key in required_zero_counter_keys:
        if counters.get(key) != 0:
            errors += (f"counter_nonzero:{key}",)
    local_callbacks = counters.get("local_injected_semantic_callback_count")
    if local_callbacks not in (0, 5):
        errors += ("local_injected_semantic_callback_count_mismatch",)
    for key, expected in (
        ("tri_party_airline_transaction_count", 1),
        ("client_root_count", 1),
        ("airline_root_count", 1),
        ("bank_root_count", 1),
        ("shared_transaction_id_count", 1),
        ("shared_ledger_entry_count", 15),
        ("offer_candidates_created_count", 1),
        ("offer_hold_receipt_fixture_count", 1),
        ("airline_offer_hold_sandbox_invoked_count", 1),
        ("airline_offer_request_validated_count", 1),
        ("mock_inventory_checked_count", 1),
        ("mock_fare_checked_count", 1),
        ("baggage_rule_checked_count", 1),
        ("offer_ttl_checked_count", 1),
        ("airline_offer_response_created_count", 1),
        ("airline_offer_hold_commit_packet_created_count", 1),
        ("airline_offer_hold_commit_packet_created_by_airline_root_count", 1),
        ("airline_offer_hold_commit_packet_created_by_client_root_count", 0),
        ("airline_offer_hold_commit_packet_created_by_bank_root_count", 0),
        ("airline_offer_hold_commit_packet_validated_count", 1),
        ("airline_offer_hold_receipt_created_count", 1),
        ("airline_offer_hold_receipt_validated_count", 1),
        ("offer_hold_receipt_payment_permission_created_count", 0),
        ("offer_hold_receipt_ticket_permission_created_count", 0),
        ("client_purchase_approval_evidence_fixture_count", 1),
        ("client_purchase_orchestration_invoked_count", 1),
        ("client_travel_intent_observed_count", 1),
        ("client_passenger_sealed_refs_observed_count", 1),
        ("client_payment_profile_sealed_ref_observed_count", 1),
        ("client_offer_response_observed_count", 1),
        ("client_offer_hold_receipt_observed_count", 1),
        ("client_offer_selected_count", 1),
        ("client_selected_offer_within_user_max_price_count", 1),
        ("client_purchase_approval_evidence_created_count", 1),
        ("client_purchase_approval_evidence_created_by_client_root_count", 1),
        ("client_purchase_approval_evidence_created_by_airline_root_count", 0),
        ("client_purchase_approval_evidence_created_by_bank_root_count", 0),
        ("client_purchase_approval_evidence_validated_count", 1),
        ("client_purchase_approval_evidence_routed_to_bank_root_count", 1),
        ("client_purchase_approval_evidence_routed_to_airline_root_count", 1),
        ("client_bank_payment_authorization_receipt_observed_count", 1),
        ("client_bank_payment_status_receipt_observed_count", 1),
        ("client_final_purchase_summary_created_count", 1),
        ("client_root_authorized_bank_payment_count", 0),
        ("client_root_issued_ticket_count", 0),
        ("client_root_created_airline_order_count", 0),
        ("client_root_created_bank_receipt_count", 0),
        ("client_root_created_action_commit_packet_count", 0),
        ("client_raw_passport_exposed_count", 0),
        ("client_raw_card_exposed_count", 0),
        ("client_raw_iban_exposed_count", 0),
        ("client_raw_payment_token_exposed_count", 0),
        ("bank_payment_intent_fixture_count", 1),
        ("bank_payment_consent_fixture_count", 1),
        ("bank_payment_authorization_receipt_fixture_count", 1),
        ("bank_payment_status_receipt_fixture_count", 1),
        ("bank_payment_authorization_sandbox_invoked_count", 1),
        ("bank_offer_hold_receipt_observed_count", 1),
        ("bank_client_purchase_approval_evidence_observed_count", 1),
        ("bank_payment_profile_sealed_ref_observed_count", 1),
        ("bank_amount_currency_validated_count", 1),
        ("bank_merchant_airline_ref_validated_count", 1),
        ("bank_payment_token_ref_validated_count", 1),
        ("bank_debtor_slot_ref_validated_count", 1),
        ("bank_idempotency_checked_count", 1),
        ("bank_expiry_ttl_checked_count", 1),
        ("bank_payment_intent_created_count", 1),
        ("bank_payment_consent_created_count", 1),
        ("bank_payment_authorization_commit_packet_created_count", 1),
        ("bank_payment_authorization_commit_packet_created_by_bank_root_count", 1),
        ("bank_payment_authorization_commit_packet_created_by_client_root_count", 0),
        ("bank_payment_authorization_commit_packet_created_by_airline_root_count", 0),
        ("bank_payment_authorization_commit_packet_validated_count", 1),
        ("payment_authorization_receipt_created_count", 1),
        ("payment_authorization_receipt_validated_count", 1),
        ("payment_status_receipt_created_count", 1),
        ("payment_status_receipt_validated_count", 1),
        ("payment_authorization_receipt_ticket_permission_created_count", 0),
        ("payment_authorization_receipt_real_payment_executed_count", 0),
        ("payment_status_receipt_ticket_permission_created_count", 0),
        ("payment_status_receipt_settlement_executed_count", 0),
        ("airline_order_created_receipt_fixture_count", 1),
        ("mock_ticket_receipt_fixture_count", 1),
        ("mock_pnr_fixture_count", 1),
        ("airline_ticket_issue_mock_corridor_invoked_count", 1),
        ("airline_ticket_issue_offer_hold_receipt_observed_count", 1),
        ("airline_ticket_issue_client_purchase_approval_observed_count", 1),
        ("airline_ticket_issue_payment_authorization_receipt_observed_count", 1),
        ("airline_ticket_issue_payment_status_receipt_observed_count", 1),
        ("airline_ticket_issue_offer_hold_ttl_freshness_validated_count", 1),
        ("airline_ticket_issue_selected_offer_match_validated_count", 1),
        ("airline_ticket_issue_amount_currency_match_validated_count", 1),
        ("airline_ticket_issue_merchant_airline_ref_match_validated_count", 1),
        ("airline_ticket_issue_passenger_sealed_ref_validated_count", 1),
        (
            "airline_ticket_issue_payment_evidence_validated_against_offer_hold_count",
            1,
        ),
        ("airline_ticket_issue_commit_packet_created_count", 1),
        ("airline_ticket_issue_commit_packet_created_by_airline_root_count", 1),
        ("airline_ticket_issue_commit_packet_created_by_client_root_count", 0),
        ("airline_ticket_issue_commit_packet_created_by_bank_root_count", 0),
        ("airline_ticket_issue_commit_packet_validated_count", 1),
        ("airline_order_created_receipt_created_count", 1),
        ("airline_order_created_receipt_validated_count", 1),
        ("mock_ticket_receipt_created_count", 1),
        ("mock_ticket_receipt_validated_count", 1),
        ("mock_pnr_created_count", 1),
        ("mock_purchase_receipt_fixture_count", 1),
        ("mock_pnr_validated_count", 1),
        ("mock_ticket_receipt_evidence_only_count", 1),
        ("mock_ticket_receipt_real_ticket_count", 0),
        ("mock_pnr_real_booking_count", 0),
        ("payment_authorization_receipt_created_ticket_count", 0),
        ("client_purchase_approval_created_ticket_count", 0),
        ("offer_hold_receipt_created_ticket_count", 0),
        ("airline_root_called_real_airline_api_count", 0),
        ("airline_root_called_real_gds_api_count", 0),
        ("integrated_tri_party_transaction_trace_created_count", 1),
        ("integrated_trace_phase_count", 17),
        ("cross_root_evidence_routing_rows_count", 6),
        ("cross_root_authority_transfer_count", 0),
        ("cross_root_real_world_effects_count", 0),
        ("final_tri_party_mock_summary_created_count", 1),
        ("final_client_view_mock_ticket_evidence_received_count", 1),
        ("final_airline_view_mock_order_ticket_pnr_evidence_created_count", 1),
        ("final_bank_view_mock_payment_authorized_not_settled_count", 1),
        ("final_real_ticket_issued_count", 0),
        ("final_real_payment_executed_count", 0),
        ("final_real_booking_created_count", 0),
        ("final_authority_transferred_between_roots_count", 0),
        ("airline_ticket_purchase_corridor_integration_count", 1),
        ("airline_ticket_purchase_corridor_pass_count", 1),
        ("airline_ticket_purchase_corridor_fail_count", 0),
        ("airline_ticket_purchase_corridor_phase_count", 5),
        ("airline_ticket_purchase_corridor_phase_pass_count", 5),
        ("airline_ticket_purchase_corridor_transition_count", 4),
        ("airline_ticket_purchase_corridor_transition_pass_count", 4),
        (
            "airline_ticket_purchase_corridor_binding_row_count",
            len(binding_matrix),
        ),
        (
            "airline_ticket_purchase_corridor_binding_match_count",
            len(binding_matrix),
        ),
        ("airline_ticket_purchase_corridor_binding_mismatch_count", 0),
        ("airline_ticket_purchase_corridor_fixture_report_binding_pass_count", 1),
        ("airline_ticket_purchase_corridor_parallel_transaction_count", 0),
        ("airline_ticket_purchase_corridor_duplicate_execution_count", 0),
        ("airline_ticket_purchase_corridor_fixture_receipts_observed_count", 3),
        ("airline_ticket_purchase_corridor_runtime_receipts_created_count", 0),
        ("airline_ticket_purchase_corridor_runtime_packets_created_count", 0),
        ("airline_ticket_purchase_corridor_adapter_execution_count", 0),
        (
            "airline_ticket_purchase_corridor_cross_root_authority_transfer_count",
            0,
        ),
        (
            "airline_ticket_purchase_corridor_post_root_reasoning_restart_count",
            0,
        ),
        ("airline_ticket_purchase_corridor_provider_called_count", 0),
        ("airline_ticket_purchase_corridor_network_used_count", 0),
        ("airline_ticket_purchase_corridor_gemini_called_count", 0),
        ("airline_ticket_purchase_corridor_real_world_effects_count", 0),
        ("future_semantic_actor_roles_planned_count", 6),
        ("future_vertical_fractal_cells_planned_count", 14),
    ):
        if counters.get(key) != expected:
            errors += (f"counter_mismatch:{key}",)

    return errors


def _format_view(view: Mapping[str, Any]) -> str:
    return (
        f"root_id: {view['root_id']}; role: {view['role']}; "
        f"bounded_view_count: {len(view['bounded_view'])}"
    )


if __name__ == "__main__":
    raise SystemExit(main())
