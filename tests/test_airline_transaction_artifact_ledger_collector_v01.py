from __future__ import annotations

import ast
import inspect
from copy import deepcopy
from dataclasses import fields, replace
from pathlib import Path
from typing import Any, Mapping

import pytest

from hedgehog.domains.airline import (
    semantic_to_contract_binding_v01 as binding,
)
from hedgehog.domains.airline import (
    semantic_to_contract_causal_runtime_v01 as causal_runtime,
)
from hedgehog.domains.airline import (
    ticket_purchase_corridor_runtime_v01 as corridor_runtime,
)
from hedgehog.domains.airline import ticket_purchase_corridor_v01 as contracts
from hedgehog.domains.airline import (
    transaction_artifact_ledger_collector_v01 as collector,
)
from hedgehog.domains.airline import transaction_artifact_ledger_v01 as ledger


MODULE_PATH = Path(
    "hedgehog/domains/airline/transaction_artifact_ledger_collector_v01.py",
)


def _offer_record(
    offer_id: str,
) -> binding.AirlineAuthoritativeOfferRecordV01:
    snapshot = binding.build_airline_candidate_snapshot_v01()
    return next(
        record
        for record in snapshot.authoritative_offer_records
        if record.offer_id == offer_id
    )


def _suffix(offer_id: str) -> str:
    return offer_id.rsplit(":", 1)[-1]


def _corridor_artifact_ids_for_offer(offer_id: str) -> dict[str, str]:
    suffix = _suffix(offer_id)
    return {
        "offer_packet": f"airline_offer_packet:mock_airline_al:{suffix}",
        "hold_packet": f"airline_hold_commit_packet:mock_airline_al:{suffix}",
        "hold_receipt": f"offer_hold_receipt:mock_airline_al:{suffix}",
        "purchase_intent": f"client_purchase_intent:client_001:{suffix}",
        "authorization": f"bank_payment_authorization_ref:mock_bank_a:{suffix}",
        "ticket_intent": f"airline_ticket_issue_intent:mock_airline_al:{suffix}",
        "ticket_receipt": f"mock_ticket_receipt:mock_airline_al:{suffix}",
        "purchase_receipt": f"mock_purchase_receipt:client_001:{suffix}",
        "client_root_final": f"client_root_final:{suffix}",
        "airline_root_final": f"airline_root_final:{suffix}",
        "bank_root_final": f"bank_root_final:{suffix}",
    }


def _context_for_offer(
    offer_id: str,
) -> contracts.AirlineTicketPurchaseContractContextV01:
    suffix = _suffix(offer_id)
    record = _offer_record(offer_id)
    return contracts.AirlineTicketPurchaseContractContextV01(
        transaction_id=contracts.TRANSACTION_ID,
        offer_id=offer_id,
        hold_id=f"hold:mock_airline_al:{suffix}",
        amount=record.amount,
        currency=record.currency,
        route_ref=record.route_ref,
        passenger_ref=contracts.PASSENGER_REF,
        max_amount=contracts.MAX_AMOUNT,
        merchant_ref=contracts.MERCHANT_REF,
    )


def _typed_corridor_artifacts(offer_id: str) -> dict[str, object]:
    suffix = _suffix(offer_id)
    ids = _corridor_artifact_ids_for_offer(offer_id)
    record = _offer_record(offer_id)
    context = _context_for_offer(offer_id)
    offer_packet = replace(
        contracts.build_valid_airline_offer_packet_v01(),
        packet_id=ids["offer_packet"],
        offer_id=offer_id,
        route_ref=record.route_ref,
        amount=record.amount,
        currency=record.currency,
    )
    hold_packet = replace(
        contracts.build_valid_airline_hold_commit_packet_v01(),
        packet_id=ids["hold_packet"],
        parent_offer_packet_id=offer_packet.packet_id,
        offer_id=offer_id,
        hold_id=context.hold_id,
        route_ref=record.route_ref,
        amount=record.amount,
        currency=record.currency,
        idempotency_key=f"idem:airline_hold:{suffix}",
    )
    hold_receipt = replace(
        contracts.build_valid_airline_offer_hold_receipt_v01(),
        receipt_id=ids["hold_receipt"],
        source_hold_packet_id=hold_packet.packet_id,
        source_idempotency_key=hold_packet.idempotency_key,
        offer_id=offer_id,
        hold_id=context.hold_id,
        route_ref=record.route_ref,
        amount=record.amount,
        currency=record.currency,
    )
    approval = replace(
        contracts.build_valid_human_approval_evidence_ref_v01(),
        selected_offer_id=offer_id,
        currency=record.currency,
    )
    purchase_intent = replace(
        contracts.build_valid_client_purchase_intent_v01(),
        intent_id=ids["purchase_intent"],
        source_human_approval_ref=approval.approval_ref,
        selected_offer_packet_id=offer_packet.packet_id,
        required_offer_hold_receipt_id=hold_receipt.receipt_id,
        offer_id=offer_id,
        hold_id=context.hold_id,
        route_ref=record.route_ref,
        selected_amount=record.amount,
        currency=record.currency,
        idempotency_key=f"idem:client_purchase_intent:{suffix}",
    )
    authorization = replace(
        contracts.build_valid_bank_payment_authorization_ref_v01(),
        authorization_ref_id=ids["authorization"],
        source_purchase_intent_id=purchase_intent.intent_id,
        offer_id=offer_id,
        hold_id=context.hold_id,
        route_ref=record.route_ref,
        amount=record.amount,
        currency=record.currency,
        idempotency_key=f"idem:bank_payment_authorization:{suffix}",
    )
    ticket_intent = replace(
        contracts.build_valid_airline_ticket_issue_intent_v01(),
        intent_id=ids["ticket_intent"],
        required_offer_packet_id=offer_packet.packet_id,
        required_hold_packet_id=hold_packet.packet_id,
        required_offer_hold_receipt_id=hold_receipt.receipt_id,
        required_client_purchase_intent_id=purchase_intent.intent_id,
        required_payment_authorization_ref_id=authorization.authorization_ref_id,
        offer_id=offer_id,
        hold_id=context.hold_id,
        route_ref=record.route_ref,
        amount=record.amount,
        currency=record.currency,
        idempotency_key=f"idem:airline_ticket_issue:{suffix}",
    )
    ticket_receipt = replace(
        contracts.build_valid_mock_ticket_receipt_v01(),
        receipt_id=ids["ticket_receipt"],
        source_ticket_issue_intent_id=ticket_intent.intent_id,
        source_idempotency_key=ticket_intent.idempotency_key,
        offer_id=offer_id,
        hold_id=context.hold_id,
        route_ref=record.route_ref,
        amount=record.amount,
        currency=record.currency,
    )
    purchase_receipt = replace(
        contracts.build_valid_mock_purchase_receipt_v01(),
        receipt_id=ids["purchase_receipt"],
        source_client_purchase_intent_id=purchase_intent.intent_id,
        source_payment_authorization_ref_id=authorization.authorization_ref_id,
        source_mock_ticket_receipt_id=ticket_receipt.receipt_id,
    )
    return {
        "context": context,
        "offer_packet": offer_packet,
        "hold_packet": hold_packet,
        "hold_receipt": hold_receipt,
        "approval": approval,
        "purchase_intent": purchase_intent,
        "authorization": authorization,
        "ticket_intent": ticket_intent,
        "ticket_receipt": ticket_receipt,
        "purchase_receipt": purchase_receipt,
    }


def _proposal_payload(
    request: causal_runtime.AirlineInjectedSemanticActorRequestV01,
    offer_id: str,
) -> dict[str, object]:
    return {
        "proposal_id": f"semantic_offer_selection_proposal:{offer_id}",
        "transaction_id": request.transaction_id,
        "actor_id": request.actor_id,
        "source_selection_input_id": request.source_selection_input_id,
        "source_bsep_projection_ref": request.source_bsep_projection_ref,
        "source_client_constraint_set_id": request.source_client_constraint_set_id,
        "source_candidate_set_snapshot_id": request.source_candidate_set_snapshot_id,
        "source_candidate_set_digest": request.source_candidate_set_digest,
        "candidate_set_ref": request.source_candidate_set_ref,
        "recommended_offer_id": offer_id,
        "ranked_offer_ids": (offer_id,),
        "decision_factors": ("semantic_actor_recommended_bounded_offer",),
        "preference_matches": ("soft_preference_interpreted",),
        "uncertainty_notes": ("requires_client_root_review",),
        "requires_root_review": True,
        "semantic_summary": "Injected deterministic advisory semantics.",
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


def _public_runtime_proposal_payload(
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
        "decision_factors": ("public_causal_runtime_semantics",),
        "preference_matches": ("explicit_offer_from_test_provider",),
        "uncertainty_notes": ("requires_client_root_review",),
        "requires_root_review": True,
        "semantic_summary": "Test-only injected advisory semantics.",
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


def _public_runtime_reviewer_payload(
    request: Mapping[str, Any],
    *,
    real_shaped_response_id: bool = False,
) -> dict[str, Any]:
    return {
        "response_id": (
            f"{request['actor_id']}_response_001"
            if real_shaped_response_id
            else (
                f"canonical_actor_output:{request['actor_id']}:"
                f"{request['proposed_offer_id']}"
            )
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
        "review_status": binding.STATUS_PASS,
        "semantic_factors": ("review_supports_explicit_offer",),
        "blocking_conflicts": (),
        "supports_proposed_offer": True,
        "validation_status": binding.STATUS_PASS,
        "raw_output_used": False,
        "authority_created": False,
        "permission_created": False,
        "real_world_effects_count": 0,
    }


def _public_runtime_provider_for_offer(
    offer_id: str,
    *,
    real_shaped_response_ids: bool = False,
) -> causal_runtime.AirlineInjectedSemanticProviderV01:
    def provider(actor_id: str, request: Mapping[str, Any]) -> Mapping[str, Any]:
        if actor_id == binding.ACTOR_CLIENT_PURCHASE_INTENT_REVIEWER:
            return _public_runtime_proposal_payload(request, offer_id)
        return _public_runtime_reviewer_payload(
            request,
            real_shaped_response_id=real_shaped_response_ids,
        )

    return provider


def _public_runtime_causal_report_for_offer(
    offer_id: str,
    *,
    real_shaped_response_ids: bool = False,
) -> causal_runtime.AirlineSemanticCausalRunReportV01:
    constraints = (
        binding.build_client_constraints_preference_b_v01()
        if offer_id == binding.OFFER_B_ID
        else binding.build_client_constraints_preference_a_v01()
    )
    return causal_runtime.collect_airline_semantic_to_contract_causal_run_v01(
        scenario_id=f"public_causal_runtime_hold_lineage:{offer_id}",
        constraints=constraints,
        semantic_provider=_public_runtime_provider_for_offer(
            offer_id,
            real_shaped_response_ids=real_shaped_response_ids,
        ),
    )


def _reviewer_response(
    request: causal_runtime.AirlineInjectedSemanticActorRequestV01,
    offer_id: str,
) -> causal_runtime.AirlineInjectedReviewerResponseV01:
    return causal_runtime.AirlineInjectedReviewerResponseV01(
        response_id=f"canonical_actor_output:{request.actor_id}:{offer_id}",
        transaction_id=request.transaction_id,
        actor_id=request.actor_id,
        source_request_id=request.request_id,
        source_selection_input_id=request.source_selection_input_id,
        source_candidate_set_snapshot_id=request.source_candidate_set_snapshot_id,
        source_candidate_set_digest=request.source_candidate_set_digest,
        reviewed_offer_id=offer_id,
        review_role=request.actor_role,
        review_status=binding.STATUS_PASS,
        semantic_factors=(f"{request.actor_role}:supports_offer",),
        blocking_conflicts=(),
        supports_proposed_offer=True,
        validation_status=binding.STATUS_PASS,
        raw_output_used=False,
        authority_created=False,
        permission_created=False,
        real_world_effects_count=0,
    )


def _call_record(
    index: int,
    request: causal_runtime.AirlineInjectedSemanticActorRequestV01,
) -> causal_runtime.AirlineSemanticProviderCallRecordV01:
    return causal_runtime.AirlineSemanticProviderCallRecordV01(
        call_index=index,
        actor_id=request.actor_id,
        actor_role=request.actor_role,
        request_id=request.request_id,
        proposed_offer_id=request.proposed_offer_id,
        provider_returned=True,
        validation_status=binding.STATUS_PASS,
        reason_codes=(),
    )


def _causal_report_for_offer(
    offer_id: str,
    hold_packet: contracts.AirlineHoldCommitPacketV01,
) -> causal_runtime.AirlineSemanticCausalRunReportV01:
    constraints = (
        binding.build_client_constraints_preference_b_v01()
        if offer_id == binding.OFFER_B_ID
        else binding.build_client_constraints_preference_a_v01()
    )
    snapshot = binding.build_airline_candidate_snapshot_v01()
    bsep = binding.build_valid_airline_bsep_projection_ref_v01()
    selection_input = binding.build_selection_input_v01(
        bsep,
        constraints,
        snapshot,
    )
    proposer_request = causal_runtime.build_airline_semantic_actor_request_v01(
        actor_id=causal_runtime.ACTOR_ORDER[0],
        selection_input=selection_input,
        constraints=constraints,
        snapshot=snapshot,
        proposed_offer_id="",
    )
    payload = _proposal_payload(proposer_request, offer_id)
    proposal, proposal_report = (
        binding.build_airline_semantic_offer_selection_proposal_from_payload_v01(
            selection_input,
            payload,
        )
    )
    assert proposal is not None
    assert proposal_report.validation_status == binding.STATUS_PASS
    proposer_review = causal_runtime._proposer_review_from_proposal(proposal)
    reviewer_requests = []
    reviewer_responses = []
    actor_reviews = [proposer_review]
    call_records = [_call_record(1, proposer_request)]
    for index, actor_id in enumerate(causal_runtime.ACTOR_ORDER[1:], start=2):
        request = causal_runtime.build_airline_semantic_actor_request_v01(
            actor_id=actor_id,
            selection_input=selection_input,
            constraints=constraints,
            snapshot=snapshot,
            proposed_offer_id=offer_id,
        )
        response = _reviewer_response(request, offer_id)
        reviewer_requests.append(request)
        reviewer_responses.append(response)
        actor_reviews.append(causal_runtime._review_from_response(response))
        call_records.append(_call_record(index, request))
    actor_review_tuple = tuple(actor_reviews)
    synthesis = binding.build_valid_synthesis_report_v01(
        selection_input=selection_input,
        actor_reviews=actor_review_tuple,
        synthesized_recommended_offer_id=offer_id,
    )
    evidence = binding.build_valid_canonical_selection_evidence_v01(
        selection_input=selection_input,
        proposal=proposal,
        synthesis=synthesis,
    )
    decision = binding.build_valid_client_root_decision_v01(
        selection_input=selection_input,
        evidence=evidence,
        selected_offer_id=offer_id,
        recommendation_accepted=True,
        root_override_used=False,
    )
    resolution = binding.build_valid_airline_root_resolution_v01(
        selection_input=selection_input,
        snapshot=snapshot,
        decision=decision,
    )
    hold_binding = binding.build_valid_hold_contract_binding_v01(
        resolution=resolution,
        hold_packet=hold_packet,
    )
    binding_report = binding.build_valid_semantic_to_contract_binding_report_v01(
        bsep_projection=bsep,
        constraints=constraints,
        snapshot=snapshot,
        selection_input=selection_input,
        proposal=proposal,
        actor_reviews=actor_review_tuple,
        synthesis=synthesis,
        evidence=evidence,
        decision=decision,
        resolution=resolution,
        hold_packet=hold_packet,
        hold_binding=hold_binding,
    )
    local_chain = binding.validate_airline_semantic_to_contract_local_chain_v01(
        bsep_projection=bsep,
        constraints=constraints,
        snapshot=snapshot,
        selection_input=selection_input,
        proposal=proposal,
        actor_reviews=actor_review_tuple,
        synthesis=synthesis,
        evidence=evidence,
        decision=decision,
        resolution=resolution,
        hold_packet=hold_packet,
        hold_binding=hold_binding,
        binding_report=binding_report,
    )
    assert local_chain.validation_status == binding.STATUS_LOCAL_MODEL_PASS
    report = causal_runtime.AirlineSemanticCausalRunReportV01(
        run_id=causal_runtime.RUN_ID,
        slice_id=causal_runtime.SLICE_ID,
        scenario_id=f"source_fixture:{offer_id}",
        final_status=causal_runtime.STATUS_LOCAL_MODEL_PASS,
        failed_stage="",
        transaction_id=constraints.transaction_id,
        client_constraint_set_id=constraints.constraint_set_id,
        candidate_set_snapshot_id=snapshot.candidate_set_snapshot_id,
        candidate_set_digest=snapshot.candidate_set_digest,
        soft_preference_fingerprint=(
            causal_runtime.soft_preference_fingerprint_from_request_v01(
                proposer_request,
            )
        ),
        hard_constraint_fingerprint=(
            causal_runtime.hard_constraint_fingerprint_from_request_v01(
                proposer_request,
            )
        ),
        provider_call_records=tuple(call_records),
        provider_call_count=5,
        proposer_request=proposer_request,
        proposer_payload=payload,
        proposal=proposal,
        reviewer_request_records=tuple(reviewer_requests),
        reviewer_responses=tuple(reviewer_responses),
        actor_reviews=actor_review_tuple,
        synthesis=synthesis,
        canonical_evidence=evidence,
        client_root_decision=decision,
        airline_root_resolution=resolution,
        hold_packet=hold_packet,
        hold_binding=hold_binding,
        causal_binding_report=binding_report,
        local_chain_validation=local_chain,
        semantic_recommendation_id=offer_id,
        root_selected_offer_id=offer_id,
        hold_contract_offer_id=offer_id,
        semantic_to_root_binding_match=True,
        root_to_hold_binding_match=True,
        default_offer_used=False,
        silent_fallback_used=False,
        provider_created_authority_count=0,
        provider_created_contract_count=0,
        runtime_receipt_created_count=0,
        corridor_execution_count=0,
        externally_observed_provider_call_count=5,
        provider_calls_performed_inside_precollected_entrypoint=0,
        duplicate_provider_call_count=0,
        provider_network_call_count=0,
        gemini_call_count=0,
        real_world_effects_count=0,
        validation_errors=(),
        next_gate=causal_runtime.NEXT_GATE,
    )
    assert causal_runtime.validate_airline_semantic_causal_run_report_v01(report) == (
        True,
        (),
    )
    return report


def _corridor_report_for_artifacts(
    artifacts: dict[str, object],
) -> corridor_runtime.AirlineTicketPurchaseCorridorRunReportV01:
    base = corridor_runtime.build_valid_airline_ticket_purchase_corridor_run_v01()
    expected_refs = {
        corridor_runtime.PHASE_AIRLINE_OFFER_HOLD: (
            artifacts["offer_packet"].packet_id,
            artifacts["hold_packet"].packet_id,
            artifacts["hold_receipt"].receipt_id,
        ),
        corridor_runtime.PHASE_CLIENT_PURCHASE_INTENT: (
            artifacts["approval"].approval_ref,
            artifacts["purchase_intent"].intent_id,
        ),
        corridor_runtime.PHASE_BANK_PAYMENT_AUTHORIZATION: (
            artifacts["authorization"].authorization_ref_id,
        ),
        corridor_runtime.PHASE_AIRLINE_TICKET_ISSUE: (
            artifacts["ticket_intent"].intent_id,
            artifacts["ticket_receipt"].receipt_id,
        ),
        corridor_runtime.PHASE_CLIENT_COMPLETION: (
            artifacts["purchase_receipt"].receipt_id,
        ),
    }
    phases = tuple(
        replace(
            phase,
            evidence_refs_observed=expected_refs[phase.phase_id],
        )
        for phase in base.phase_results
    )
    report = replace(
        base,
        phase_results=phases,
        contract_context=artifacts["context"],
    )
    assert corridor_runtime.validate_airline_ticket_purchase_corridor_run_v01(report) == (
        True,
        (),
    )
    return report


def _expected_refs(
    *,
    source_bundle_id: str,
    causal_report: causal_runtime.AirlineSemanticCausalRunReportV01,
    corridor_report: corridor_runtime.AirlineTicketPurchaseCorridorRunReportV01,
) -> ledger.AirlineTransactionArtifactLedgerExpectedSourceRefsV01:
    return ledger.AirlineTransactionArtifactLedgerExpectedSourceRefsV01(
        source_run_ref=f"source_run:{source_bundle_id}",
        source_causal_report_ref=(
            f"source_causal_report:{causal_report.run_id}:"
            f"{causal_report.scenario_id}"
        ),
        source_corridor_report_ref=(
            f"source_corridor_report:{corridor_report.run_id}:"
            f"{corridor_report.transaction_id}"
        ),
    )


def _bsep_projection(
    *,
    projection_id: str,
    projection_ref: str,
    side: str,
) -> collector.AirlineTransactionArtifactLedgerBSEPProjectionSourceV01:
    return collector.AirlineTransactionArtifactLedgerBSEPProjectionSourceV01(
        projection_id=projection_id,
        projection_ref=projection_ref,
        bsep_packet_id="bsep_packet:collector_fixture:001",
        transaction_id=contracts.TRANSACTION_ID,
        side=side,
        validation_status=ledger.STATUS_PASS,
        raw_secrets_included=False,
        raw_provider_text_included=False,
        authority_created=False,
        permission_created=False,
        real_world_effects_count=0,
    )


def _root_final(
    *,
    final_id: str,
    root_owner: str,
    refs: tuple[str, ...],
) -> collector.AirlineTransactionArtifactLedgerRootFinalSourceV01:
    return collector.AirlineTransactionArtifactLedgerRootFinalSourceV01(
        final_id=final_id,
        transaction_id=contracts.TRANSACTION_ID,
        root_owner=root_owner,
        created_by=root_owner,
        final_status=ledger.STATUS_PASS,
        source_artifact_refs=refs,
        authority_created_by_ledger=False,
        permission_created_by_ledger=False,
        real_world_effects_count=0,
    )


def _source_bundle(
    offer_id: str,
) -> collector.AirlineTransactionArtifactLedgerSourceBundleV01:
    artifacts = _typed_corridor_artifacts(offer_id)
    causal_report = _causal_report_for_offer(
        offer_id,
        artifacts["hold_packet"],
    )
    corridor_report = _corridor_report_for_artifacts(artifacts)
    ids = _corridor_artifact_ids_for_offer(offer_id)
    source_bundle_id = f"source_bundle:{offer_id}"
    expected_refs = _expected_refs(
        source_bundle_id=source_bundle_id,
        causal_report=causal_report,
        corridor_report=corridor_report,
    )
    return collector.AirlineTransactionArtifactLedgerSourceBundleV01(
        source_bundle_id=source_bundle_id,
        transaction_id=contracts.TRANSACTION_ID,
        expected_source_refs=expected_refs,
        client_bsep_projection=_bsep_projection(
            projection_id="client_bsep_projection",
            projection_ref="bsep_projection:client:001",
            side=collector.SIDE_CLIENT,
        ),
        airline_bsep_projection=_bsep_projection(
            projection_id="airline_bsep_projection",
            projection_ref=binding.BSEP_PROJECTION_REF,
            side=collector.SIDE_AIRLINE,
        ),
        bank_bsep_projection=_bsep_projection(
            projection_id="bank_bsep_projection",
            projection_ref="bsep_projection:bank:001",
            side=collector.SIDE_BANK,
        ),
        cross_root_bsep_projection=_bsep_projection(
            projection_id="cross_root_bsep_projection",
            projection_ref="bsep_projection:cross_root:001",
            side=collector.SIDE_CROSS_ROOT_ADVISORY,
        ),
        causal_report=causal_report,
        offer_packet=artifacts["offer_packet"],
        hold_packet=artifacts["hold_packet"],
        hold_receipt=artifacts["hold_receipt"],
        purchase_approval_evidence=artifacts["approval"],
        purchase_intent=artifacts["purchase_intent"],
        payment_authorization_ref=artifacts["authorization"],
        ticket_issue_intent=artifacts["ticket_intent"],
        mock_ticket_receipt=artifacts["ticket_receipt"],
        mock_purchase_receipt=artifacts["purchase_receipt"],
        corridor_report=corridor_report,
        client_root_final=_root_final(
            final_id=ids["client_root_final"],
            root_owner=ledger.CLIENT_ROOT_ID,
            refs=(
                causal_report.client_root_decision.decision_id,
                artifacts["purchase_intent"].intent_id,
                artifacts["purchase_receipt"].receipt_id,
            ),
        ),
        airline_root_final=_root_final(
            final_id=ids["airline_root_final"],
            root_owner=ledger.AIRLINE_ROOT_ID,
            refs=(
                causal_report.airline_root_resolution.resolution_id,
                artifacts["offer_packet"].packet_id,
                artifacts["hold_packet"].packet_id,
                artifacts["ticket_intent"].intent_id,
                artifacts["ticket_receipt"].receipt_id,
            ),
        ),
        bank_root_final=_root_final(
            final_id=ids["bank_root_final"],
            root_owner=ledger.BANK_ROOT_ID,
            refs=(artifacts["authorization"].authorization_ref_id,),
        ),
        source_validation_refs=(
            expected_refs.source_run_ref,
            expected_refs.source_causal_report_ref,
            expected_refs.source_corridor_report_ref,
        ),
        auxiliary_observation_refs=collector.EXPECTED_AUXILIARY_OBSERVATION_REFS,
    )


def _typed_corridor_artifacts_from_public_causal_report(
    causal_report: causal_runtime.AirlineSemanticCausalRunReportV01,
) -> dict[str, object]:
    assert causal_report.hold_packet is not None
    offer_id = causal_report.semantic_recommendation_id
    suffix = _suffix(offer_id)
    record = _offer_record(offer_id)
    hold_packet = causal_report.hold_packet
    context = contracts.AirlineTicketPurchaseContractContextV01(
        transaction_id=contracts.TRANSACTION_ID,
        offer_id=offer_id,
        hold_id=hold_packet.hold_id,
        amount=record.amount,
        currency=record.currency,
        route_ref=record.route_ref,
        passenger_ref=hold_packet.passenger_ref,
        max_amount=contracts.MAX_AMOUNT,
        merchant_ref=contracts.MERCHANT_REF,
    )
    offer_packet = replace(
        contracts.build_valid_airline_offer_packet_v01(),
        packet_id=hold_packet.parent_offer_packet_id,
        offer_id=offer_id,
        passenger_ref=hold_packet.passenger_ref,
        route_ref=record.route_ref,
        amount=record.amount,
        currency=record.currency,
        ttl_seconds=hold_packet.ttl_seconds,
        expired=hold_packet.expired,
    )
    hold_receipt = replace(
        contracts.build_valid_airline_offer_hold_receipt_v01(),
        receipt_id=f"offer_hold_receipt:semantic_causal:{suffix}",
        source_hold_packet_id=hold_packet.packet_id,
        source_idempotency_key=hold_packet.idempotency_key,
        offer_id=offer_id,
        hold_id=hold_packet.hold_id,
        passenger_ref=hold_packet.passenger_ref,
        route_ref=record.route_ref,
        amount=record.amount,
        currency=record.currency,
    )
    approval = replace(
        contracts.build_valid_human_approval_evidence_ref_v01(),
        selected_offer_id=offer_id,
        max_amount=contracts.MAX_AMOUNT,
        currency=record.currency,
        passenger_ref=hold_packet.passenger_ref,
    )
    purchase_intent = replace(
        contracts.build_valid_client_purchase_intent_v01(),
        intent_id=f"client_purchase_intent:semantic_causal:{suffix}",
        source_human_approval_ref=approval.approval_ref,
        selected_offer_packet_id=offer_packet.packet_id,
        required_offer_hold_receipt_id=hold_receipt.receipt_id,
        offer_id=offer_id,
        hold_id=hold_packet.hold_id,
        passenger_ref=hold_packet.passenger_ref,
        route_ref=record.route_ref,
        max_amount=contracts.MAX_AMOUNT,
        selected_amount=record.amount,
        currency=record.currency,
        ttl_seconds=hold_packet.ttl_seconds,
        expired=hold_packet.expired,
        idempotency_key=f"idem:client_purchase_intent:semantic_causal:{suffix}",
    )
    authorization = replace(
        contracts.build_valid_bank_payment_authorization_ref_v01(),
        authorization_ref_id=f"bank_payment_authorization_ref:semantic_causal:{suffix}",
        source_purchase_intent_id=purchase_intent.intent_id,
        merchant_ref=contracts.MERCHANT_REF,
        offer_id=offer_id,
        hold_id=hold_packet.hold_id,
        passenger_ref=hold_packet.passenger_ref,
        route_ref=record.route_ref,
        amount=record.amount,
        currency=record.currency,
        ttl_seconds=hold_packet.ttl_seconds,
        expired=hold_packet.expired,
        idempotency_key=f"idem:bank_payment_authorization:semantic_causal:{suffix}",
    )
    ticket_intent = replace(
        contracts.build_valid_airline_ticket_issue_intent_v01(),
        intent_id=f"airline_ticket_issue_intent:semantic_causal:{suffix}",
        required_offer_packet_id=offer_packet.packet_id,
        required_hold_packet_id=hold_packet.packet_id,
        required_offer_hold_receipt_id=hold_receipt.receipt_id,
        required_client_purchase_intent_id=purchase_intent.intent_id,
        required_payment_authorization_ref_id=authorization.authorization_ref_id,
        offer_id=offer_id,
        hold_id=hold_packet.hold_id,
        passenger_ref=hold_packet.passenger_ref,
        route_ref=record.route_ref,
        amount=record.amount,
        currency=record.currency,
        merchant_ref=contracts.MERCHANT_REF,
        ttl_seconds=hold_packet.ttl_seconds,
        expired=hold_packet.expired,
        idempotency_key=f"idem:airline_ticket_issue:semantic_causal:{suffix}",
    )
    ticket_receipt = replace(
        contracts.build_valid_mock_ticket_receipt_v01(),
        receipt_id=f"mock_ticket_receipt:semantic_causal:{suffix}",
        source_ticket_issue_intent_id=ticket_intent.intent_id,
        source_idempotency_key=ticket_intent.idempotency_key,
        offer_id=offer_id,
        hold_id=hold_packet.hold_id,
        passenger_ref=hold_packet.passenger_ref,
        route_ref=record.route_ref,
        amount=record.amount,
        currency=record.currency,
    )
    purchase_receipt = replace(
        contracts.build_valid_mock_purchase_receipt_v01(),
        receipt_id=f"mock_purchase_receipt:semantic_causal:{suffix}",
        source_client_purchase_intent_id=purchase_intent.intent_id,
        source_payment_authorization_ref_id=authorization.authorization_ref_id,
        source_mock_ticket_receipt_id=ticket_receipt.receipt_id,
    )
    return {
        "context": context,
        "offer_packet": offer_packet,
        "hold_packet": hold_packet,
        "hold_receipt": hold_receipt,
        "approval": approval,
        "purchase_intent": purchase_intent,
        "authorization": authorization,
        "ticket_intent": ticket_intent,
        "ticket_receipt": ticket_receipt,
        "purchase_receipt": purchase_receipt,
    }


def _source_bundle_from_public_causal_runtime(
    offer_id: str,
    *,
    real_shaped_response_ids: bool = False,
) -> collector.AirlineTransactionArtifactLedgerSourceBundleV01:
    causal_report = _public_runtime_causal_report_for_offer(
        offer_id,
        real_shaped_response_ids=real_shaped_response_ids,
    )
    artifacts = _typed_corridor_artifacts_from_public_causal_report(causal_report)
    corridor_report = _corridor_report_for_artifacts(artifacts)
    suffix = _suffix(offer_id)
    source_bundle_id = f"source_bundle:public_causal_runtime:{offer_id}"
    expected_refs = _expected_refs(
        source_bundle_id=source_bundle_id,
        causal_report=causal_report,
        corridor_report=corridor_report,
    )
    return collector.AirlineTransactionArtifactLedgerSourceBundleV01(
        source_bundle_id=source_bundle_id,
        transaction_id=contracts.TRANSACTION_ID,
        expected_source_refs=expected_refs,
        client_bsep_projection=_bsep_projection(
            projection_id=f"client_bsep_projection:semantic_causal:{suffix}",
            projection_ref="bsep_projection:client:semantic_causal",
            side=collector.SIDE_CLIENT,
        ),
        airline_bsep_projection=_bsep_projection(
            projection_id=f"airline_bsep_projection:semantic_causal:{suffix}",
            projection_ref=binding.BSEP_PROJECTION_REF,
            side=collector.SIDE_AIRLINE,
        ),
        bank_bsep_projection=_bsep_projection(
            projection_id=f"bank_bsep_projection:semantic_causal:{suffix}",
            projection_ref="bsep_projection:bank:semantic_causal",
            side=collector.SIDE_BANK,
        ),
        cross_root_bsep_projection=_bsep_projection(
            projection_id=f"cross_root_bsep_projection:semantic_causal:{suffix}",
            projection_ref="bsep_projection:cross_root:semantic_causal",
            side=collector.SIDE_CROSS_ROOT_ADVISORY,
        ),
        causal_report=causal_report,
        offer_packet=artifacts["offer_packet"],
        hold_packet=artifacts["hold_packet"],
        hold_receipt=artifacts["hold_receipt"],
        purchase_approval_evidence=artifacts["approval"],
        purchase_intent=artifacts["purchase_intent"],
        payment_authorization_ref=artifacts["authorization"],
        ticket_issue_intent=artifacts["ticket_intent"],
        mock_ticket_receipt=artifacts["ticket_receipt"],
        mock_purchase_receipt=artifacts["purchase_receipt"],
        corridor_report=corridor_report,
        client_root_final=_root_final(
            final_id=f"client_root_final:semantic_causal:{suffix}",
            root_owner=ledger.CLIENT_ROOT_ID,
            refs=(
                causal_report.client_root_decision.decision_id,
                artifacts["purchase_intent"].intent_id,
                artifacts["purchase_receipt"].receipt_id,
            ),
        ),
        airline_root_final=_root_final(
            final_id=f"airline_root_final:semantic_causal:{suffix}",
            root_owner=ledger.AIRLINE_ROOT_ID,
            refs=(
                causal_report.airline_root_resolution.resolution_id,
                artifacts["offer_packet"].packet_id,
                artifacts["hold_packet"].packet_id,
                artifacts["ticket_intent"].intent_id,
                artifacts["ticket_receipt"].receipt_id,
            ),
        ),
        bank_root_final=_root_final(
            final_id=f"bank_root_final:semantic_causal:{suffix}",
            root_owner=ledger.BANK_ROOT_ID,
            refs=(artifacts["authorization"].authorization_ref_id,),
        ),
        source_validation_refs=(
            expected_refs.source_run_ref,
            expected_refs.source_causal_report_ref,
            expected_refs.source_corridor_report_ref,
        ),
        auxiliary_observation_refs=collector.EXPECTED_AUXILIARY_OBSERVATION_REFS,
    )


def _collect(
    source_bundle: object,
) -> ledger.AirlineTransactionArtifactLedgerV01:
    return collector.collect_airline_transaction_artifact_ledger_from_source_v01(
        source_bundle=source_bundle,
    )


def _expected_artifact_ids(
    source_bundle: collector.AirlineTransactionArtifactLedgerSourceBundleV01,
) -> dict[str, str]:
    return {
        ledger.ARTIFACT_TRANSACTION_SCOPE: (
            f"airline_transaction_scope:{source_bundle.transaction_id}"
        ),
        ledger.ARTIFACT_CLIENT_BSEP_PROJECTION: (
            source_bundle.client_bsep_projection.projection_id
        ),
        ledger.ARTIFACT_AIRLINE_BSEP_PROJECTION: (
            source_bundle.airline_bsep_projection.projection_id
        ),
        ledger.ARTIFACT_BANK_BSEP_PROJECTION: (
            source_bundle.bank_bsep_projection.projection_id
        ),
        ledger.ARTIFACT_CROSS_ROOT_BSEP_PROJECTION: (
            source_bundle.cross_root_bsep_projection.projection_id
        ),
        ledger.ARTIFACT_VALIDATED_CANONICAL_SEMANTIC_EVIDENCE: (
            source_bundle.causal_report.canonical_evidence.canonical_selection_id
        ),
        ledger.ARTIFACT_CLIENT_ROOT_SELECTION_DECISION: (
            source_bundle.causal_report.client_root_decision.decision_id
        ),
        ledger.ARTIFACT_AIRLINE_ROOT_OFFER_RESOLUTION: (
            source_bundle.causal_report.airline_root_resolution.resolution_id
        ),
        ledger.ARTIFACT_AIRLINE_OFFER_PACKET: source_bundle.offer_packet.packet_id,
        ledger.ARTIFACT_AIRLINE_HOLD_PACKET: source_bundle.hold_packet.packet_id,
        ledger.ARTIFACT_AIRLINE_OFFER_HOLD_RECEIPT: (
            source_bundle.hold_receipt.receipt_id
        ),
        ledger.ARTIFACT_CLIENT_PURCHASE_INTENT: source_bundle.purchase_intent.intent_id,
        ledger.ARTIFACT_BANK_PAYMENT_AUTHORIZATION: (
            source_bundle.payment_authorization_ref.authorization_ref_id
        ),
        ledger.ARTIFACT_AIRLINE_TICKET_ISSUE_INTENT: (
            source_bundle.ticket_issue_intent.intent_id
        ),
        ledger.ARTIFACT_MOCK_TICKET_RECEIPT: (
            source_bundle.mock_ticket_receipt.receipt_id
        ),
        ledger.ARTIFACT_MOCK_PURCHASE_RECEIPT: (
            source_bundle.mock_purchase_receipt.receipt_id
        ),
        ledger.ARTIFACT_CLIENT_ROOT_FINAL: source_bundle.client_root_final.final_id,
        ledger.ARTIFACT_AIRLINE_ROOT_FINAL: source_bundle.airline_root_final.final_id,
        ledger.ARTIFACT_BANK_ROOT_FINAL: source_bundle.bank_root_final.final_id,
    }


def _expected_identity(
    source_bundle: collector.AirlineTransactionArtifactLedgerSourceBundleV01,
) -> ledger.AirlineTransactionArtifactLedgerExpectedIdentityV01:
    return collector._expected_identity_from_source(source_bundle)


def _assert_collected_pass(
    source_bundle: collector.AirlineTransactionArtifactLedgerSourceBundleV01,
) -> ledger.AirlineTransactionArtifactLedgerV01:
    item = _collect(source_bundle)
    report = ledger.validate_airline_transaction_artifact_ledger_v01(
        item,
        expected_identity=_expected_identity(source_bundle),
    )
    assert item.validation_status == ledger.STATUS_PASS
    assert report.validation_status == ledger.STATUS_PASS
    return item


def _assert_source_fails(
    source_bundle: object,
    reason: str,
) -> ledger.AirlineTransactionArtifactLedgerV01:
    report = collector.validate_airline_transaction_artifact_ledger_source_bundle_v01(
        source_bundle,
    )
    assert report.validation_status == collector.STATUS_FAIL_CLOSED
    assert reason in report.validation_errors
    item = _collect(source_bundle)
    assert item.validation_status == ledger.STATUS_FAIL_CLOSED
    assert reason in item.validation_errors
    return item


def _entry_by_type(
    item: ledger.AirlineTransactionArtifactLedgerV01,
    artifact_type: str,
) -> ledger.AirlineTransactionArtifactLedgerEntryV01:
    return next(entry for entry in item.entries if entry.artifact_type == artifact_type)


def _mutable_json(value: object) -> object:
    if hasattr(value, "items"):
        return {key: _mutable_json(item) for key, item in value.items()}  # type: ignore[attr-defined]
    if isinstance(value, tuple):
        return tuple(_mutable_json(item) for item in value)
    return value


def _replace_deep_value(value: object, old: object, new: object) -> object:
    if hasattr(value, "items"):
        return {
            key: _replace_deep_value(item, old, new)
            for key, item in value.items()  # type: ignore[attr-defined]
        }
    if isinstance(value, tuple):
        return tuple(_replace_deep_value(item, old, new) for item in value)
    if isinstance(value, list):
        return [_replace_deep_value(item, old, new) for item in value]
    return new if value == old else value


def _replace_entry(
    item: ledger.AirlineTransactionArtifactLedgerV01,
    artifact_type: str,
    **changes: object,
) -> ledger.AirlineTransactionArtifactLedgerV01:
    entries = list(item.entries)
    for index, entry in enumerate(entries):
        if entry.artifact_type == artifact_type:
            entries[index] = replace(entry, **changes)
            return replace(item, entries=tuple(entries))
    raise AssertionError(f"missing artifact type: {artifact_type}")


def _replace_hash(
    item: ledger.AirlineTransactionArtifactLedgerV01,
    artifact_type: str,
    **updates: object,
) -> ledger.AirlineTransactionArtifactLedgerV01:
    entry = _entry_by_type(item, artifact_type)
    value = _mutable_json(entry.canonical_hash_input)
    assert isinstance(value, dict)
    value.update(updates)
    return _replace_entry(item, artifact_type, canonical_hash_input=value)


def _replace_hold_id_everywhere_in_ledger(
    item: ledger.AirlineTransactionArtifactLedgerV01,
    *,
    old_hold_id: str,
    new_hold_id: str,
) -> ledger.AirlineTransactionArtifactLedgerV01:
    entries = []
    for entry in item.entries:
        value = _mutable_json(entry.canonical_hash_input)
        value = _replace_deep_value(value, old_hold_id, new_hold_id)
        entries.append(replace(entry, canonical_hash_input=value))
    return replace(item, entries=tuple(entries))


def _assert_lineage_tamper_fails(
    source_bundle: collector.AirlineTransactionArtifactLedgerSourceBundleV01,
    item: ledger.AirlineTransactionArtifactLedgerV01,
    reason: str,
) -> None:
    report = ledger.validate_airline_transaction_artifact_ledger_v01(
        item,
        expected_identity=_expected_identity(source_bundle),
    )
    assert report.validation_status == ledger.STATUS_FAIL_CLOSED
    assert reason in report.validation_errors


def _source_bundle_with_approval_ref(
    source_bundle: collector.AirlineTransactionArtifactLedgerSourceBundleV01,
    approval_ref: str,
) -> collector.AirlineTransactionArtifactLedgerSourceBundleV01:
    approval = replace(
        source_bundle.purchase_approval_evidence,
        approval_ref=approval_ref,
    )
    purchase_intent = replace(
        source_bundle.purchase_intent,
        source_human_approval_ref=approval_ref,
    )
    phases = list(source_bundle.corridor_report.phase_results)
    for index, phase in enumerate(phases):
        if phase.phase_id == corridor_runtime.PHASE_CLIENT_PURCHASE_INTENT:
            phases[index] = replace(
                phase,
                evidence_refs_observed=(approval_ref, purchase_intent.intent_id),
            )
            break
    return replace(
        source_bundle,
        purchase_approval_evidence=approval,
        purchase_intent=purchase_intent,
        corridor_report=replace(
            source_bundle.corridor_report,
            phase_results=tuple(phases),
        ),
    )


def _source_bundle_with_approval_scope(
    source_bundle: collector.AirlineTransactionArtifactLedgerSourceBundleV01,
    approval_scope: str,
) -> collector.AirlineTransactionArtifactLedgerSourceBundleV01:
    return replace(
        source_bundle,
        purchase_approval_evidence=replace(
            source_bundle.purchase_approval_evidence,
            approval_scope=approval_scope,
        ),
    )


def _replace_phase_refs(
    source_bundle: collector.AirlineTransactionArtifactLedgerSourceBundleV01,
    *,
    phase_id: str,
    refs: tuple[str, ...],
) -> corridor_runtime.AirlineTicketPurchaseCorridorRunReportV01:
    phases = list(source_bundle.corridor_report.phase_results)
    for index, phase in enumerate(phases):
        if phase.phase_id == phase_id:
            phases[index] = replace(phase, evidence_refs_observed=refs)
            break
    return replace(source_bundle.corridor_report, phase_results=tuple(phases))


def _source_bundle_with_passenger_ref(
    source_bundle: collector.AirlineTransactionArtifactLedgerSourceBundleV01,
    passenger_ref: str,
) -> collector.AirlineTransactionArtifactLedgerSourceBundleV01:
    hold_packet = replace(source_bundle.hold_packet, passenger_ref=passenger_ref)
    return replace(
        source_bundle,
        offer_packet=replace(source_bundle.offer_packet, passenger_ref=passenger_ref),
        hold_packet=hold_packet,
        hold_receipt=replace(source_bundle.hold_receipt, passenger_ref=passenger_ref),
        purchase_approval_evidence=replace(
            source_bundle.purchase_approval_evidence,
            passenger_ref=passenger_ref,
        ),
        purchase_intent=replace(
            source_bundle.purchase_intent,
            passenger_ref=passenger_ref,
        ),
        payment_authorization_ref=replace(
            source_bundle.payment_authorization_ref,
            passenger_ref=passenger_ref,
        ),
        ticket_issue_intent=replace(
            source_bundle.ticket_issue_intent,
            passenger_ref=passenger_ref,
        ),
        mock_ticket_receipt=replace(
            source_bundle.mock_ticket_receipt,
            passenger_ref=passenger_ref,
        ),
        corridor_report=replace(
            source_bundle.corridor_report,
            contract_context=replace(
                source_bundle.corridor_report.contract_context,
                passenger_ref=passenger_ref,
            ),
        ),
        causal_report=replace(source_bundle.causal_report, hold_packet=hold_packet),
    )


def _source_bundle_with_hold_idempotency(
    source_bundle: collector.AirlineTransactionArtifactLedgerSourceBundleV01,
    idempotency_key: str,
) -> collector.AirlineTransactionArtifactLedgerSourceBundleV01:
    hold_packet = replace(
        source_bundle.hold_packet,
        idempotency_key=idempotency_key,
    )
    return replace(
        source_bundle,
        hold_packet=hold_packet,
        hold_receipt=replace(
            source_bundle.hold_receipt,
            source_idempotency_key=idempotency_key,
        ),
        causal_report=replace(source_bundle.causal_report, hold_packet=hold_packet),
    )


def _source_bundle_with_purchase_idempotency(
    source_bundle: collector.AirlineTransactionArtifactLedgerSourceBundleV01,
    idempotency_key: str,
) -> collector.AirlineTransactionArtifactLedgerSourceBundleV01:
    return replace(
        source_bundle,
        purchase_intent=replace(
            source_bundle.purchase_intent,
            idempotency_key=idempotency_key,
        ),
    )


def _source_bundle_with_payment_idempotency(
    source_bundle: collector.AirlineTransactionArtifactLedgerSourceBundleV01,
    idempotency_key: str,
) -> collector.AirlineTransactionArtifactLedgerSourceBundleV01:
    return replace(
        source_bundle,
        payment_authorization_ref=replace(
            source_bundle.payment_authorization_ref,
            idempotency_key=idempotency_key,
        ),
    )


def _source_bundle_with_ticket_idempotency(
    source_bundle: collector.AirlineTransactionArtifactLedgerSourceBundleV01,
    idempotency_key: str,
) -> collector.AirlineTransactionArtifactLedgerSourceBundleV01:
    return replace(
        source_bundle,
        ticket_issue_intent=replace(
            source_bundle.ticket_issue_intent,
            idempotency_key=idempotency_key,
        ),
        mock_ticket_receipt=replace(
            source_bundle.mock_ticket_receipt,
            source_idempotency_key=idempotency_key,
        ),
    )


def _source_bundle_with_full_idempotency_chain(
    source_bundle: collector.AirlineTransactionArtifactLedgerSourceBundleV01,
) -> collector.AirlineTransactionArtifactLedgerSourceBundleV01:
    changed = _source_bundle_with_hold_idempotency(
        source_bundle,
        "idem:airline_hold:anti_collapse",
    )
    changed = _source_bundle_with_purchase_idempotency(
        changed,
        "idem:client_purchase_intent:anti_collapse",
    )
    changed = _source_bundle_with_payment_idempotency(
        changed,
        "idem:bank_payment_authorization:anti_collapse",
    )
    return _source_bundle_with_ticket_idempotency(
        changed,
        "idem:airline_ticket_issue:anti_collapse",
    )


def _source_bundle_with_max_amount(
    source_bundle: collector.AirlineTransactionArtifactLedgerSourceBundleV01,
    max_amount: int,
) -> collector.AirlineTransactionArtifactLedgerSourceBundleV01:
    return replace(
        source_bundle,
        purchase_approval_evidence=replace(
            source_bundle.purchase_approval_evidence,
            max_amount=max_amount,
        ),
        purchase_intent=replace(
            source_bundle.purchase_intent,
            max_amount=max_amount,
        ),
        corridor_report=replace(
            source_bundle.corridor_report,
            contract_context=replace(
                source_bundle.corridor_report.contract_context,
                max_amount=max_amount,
            ),
        ),
    )


def _source_bundle_with_merchant_ref(
    source_bundle: collector.AirlineTransactionArtifactLedgerSourceBundleV01,
    merchant_ref: str,
) -> collector.AirlineTransactionArtifactLedgerSourceBundleV01:
    return replace(
        source_bundle,
        payment_authorization_ref=replace(
            source_bundle.payment_authorization_ref,
            merchant_ref=merchant_ref,
        ),
        ticket_issue_intent=replace(
            source_bundle.ticket_issue_intent,
            merchant_ref=merchant_ref,
        ),
        corridor_report=replace(
            source_bundle.corridor_report,
            contract_context=replace(
                source_bundle.corridor_report.contract_context,
                merchant_ref=merchant_ref,
            ),
        ),
    )


def _source_bundle_with_ttl_seconds(
    source_bundle: collector.AirlineTransactionArtifactLedgerSourceBundleV01,
    ttl_seconds: int,
) -> collector.AirlineTransactionArtifactLedgerSourceBundleV01:
    hold_packet = replace(source_bundle.hold_packet, ttl_seconds=ttl_seconds)
    resolution = replace(
        source_bundle.causal_report.airline_root_resolution,
        resolved_ttl=ttl_seconds,
    )
    return replace(
        source_bundle,
        offer_packet=replace(source_bundle.offer_packet, ttl_seconds=ttl_seconds),
        hold_packet=hold_packet,
        purchase_intent=replace(
            source_bundle.purchase_intent,
            ttl_seconds=ttl_seconds,
        ),
        payment_authorization_ref=replace(
            source_bundle.payment_authorization_ref,
            ttl_seconds=ttl_seconds,
        ),
        ticket_issue_intent=replace(
            source_bundle.ticket_issue_intent,
            ttl_seconds=ttl_seconds,
        ),
        causal_report=replace(
            source_bundle.causal_report,
            airline_root_resolution=resolution,
            hold_packet=hold_packet,
        ),
    )


def _source_bundle_with_mock_ticket_identity(
    source_bundle: collector.AirlineTransactionArtifactLedgerSourceBundleV01,
    *,
    mock_ticket_id: str,
    mock_pnr: str,
) -> collector.AirlineTransactionArtifactLedgerSourceBundleV01:
    return replace(
        source_bundle,
        mock_ticket_receipt=replace(
            source_bundle.mock_ticket_receipt,
            mock_ticket_id=mock_ticket_id,
            mock_pnr=mock_pnr,
        ),
    )


def _tamper_source_snapshot(
    item: ledger.AirlineTransactionArtifactLedgerV01,
    artifact_type: str,
    **updates: object,
) -> ledger.AirlineTransactionArtifactLedgerV01:
    entry = _entry_by_type(item, artifact_type)
    value = _mutable_json(entry.canonical_hash_input)
    assert isinstance(value, dict)
    snapshot = dict(value["source_snapshot"])
    snapshot.update(updates)
    value["source_snapshot"] = snapshot
    return _replace_entry(item, artifact_type, canonical_hash_input=value)


def _tamper_purchase_approval_snapshot(
    item: ledger.AirlineTransactionArtifactLedgerV01,
    **updates: object,
) -> ledger.AirlineTransactionArtifactLedgerV01:
    entry = _entry_by_type(item, ledger.ARTIFACT_CLIENT_PURCHASE_INTENT)
    value = _mutable_json(entry.canonical_hash_input)
    assert isinstance(value, dict)
    snapshot = dict(value["source_snapshot"])
    approval = dict(snapshot["purchase_approval_evidence"])
    approval.update(updates)
    snapshot["purchase_approval_evidence"] = approval
    value["source_snapshot"] = snapshot
    return _replace_entry(
        item,
        ledger.ARTIFACT_CLIENT_PURCHASE_INTENT,
        canonical_hash_input=value,
    )


def _assert_snapshot_change_does_not_collapse(
    mutated: collector.AirlineTransactionArtifactLedgerSourceBundleV01,
    baseline: ledger.AirlineTransactionArtifactLedgerV01,
    *,
    artifact_type: str,
    field_name: str | tuple[str, ...],
    expected_value: object,
) -> ledger.AirlineTransactionArtifactLedgerV01:
    source_report = collector.validate_airline_transaction_artifact_ledger_source_bundle_v01(
        mutated,
    )
    assert source_report.validation_status == collector.STATUS_PASS
    item = _assert_collected_pass(mutated)
    entry = _entry_by_type(item, artifact_type)
    observed = entry.canonical_hash_input["source_snapshot"]
    if type(field_name) is tuple:
        for key in field_name:
            observed = observed[key]
    else:
        observed = observed[field_name]
    assert observed == expected_value
    assert item != baseline
    return item


def _assert_lineage_change_does_not_collapse(
    mutated: collector.AirlineTransactionArtifactLedgerSourceBundleV01,
    baseline: ledger.AirlineTransactionArtifactLedgerV01,
) -> None:
    source_report = collector.validate_airline_transaction_artifact_ledger_source_bundle_v01(
        mutated,
    )
    item = _collect(mutated)
    if source_report.validation_status == collector.STATUS_PASS:
        assert item.validation_status == ledger.STATUS_PASS
        assert item != baseline
    else:
        assert item.validation_status == ledger.STATUS_FAIL_CLOSED


def test_01_valid_offer_a_source_bundle_produces_pass_ledger() -> None:
    item = _assert_collected_pass(_source_bundle(binding.OFFER_A_ID))
    assert item.entries[5].canonical_hash_input["selected_offer_id"] == binding.OFFER_A_ID


def test_02_valid_offer_b_source_bundle_produces_pass_ledger() -> None:
    item = _assert_collected_pass(_source_bundle(binding.OFFER_B_ID))
    assert item.entries[5].canonical_hash_input["selected_offer_id"] == binding.OFFER_B_ID


def test_03_collected_ledgers_have_19_entries_29_edges_3_root_finals() -> None:
    for offer_id in (binding.OFFER_A_ID, binding.OFFER_B_ID):
        source_bundle = _source_bundle(offer_id)
        item = _assert_collected_pass(source_bundle)
        report = ledger.validate_airline_transaction_artifact_ledger_v01(
            item,
            expected_identity=_expected_identity(source_bundle),
        )
        assert report.entry_count == 19
        assert report.dependency_edge_count == 29
        assert report.root_final_count == 3


def test_public_causal_runtime_semantic_hold_lineage_passes_collection() -> None:
    source_bundle = _source_bundle_from_public_causal_runtime(binding.OFFER_A_ID)
    causal_report = source_bundle.causal_report
    accepted, reasons = causal_runtime.validate_airline_semantic_causal_run_report_v01(
        causal_report,
    )
    assert accepted is True
    assert reasons == ()
    assert causal_report.hold_packet is source_bundle.hold_packet
    assert causal_report.hold_packet.packet_id.startswith(
        "airline_hold_commit_packet:semantic_causal:",
    )
    assert causal_report.hold_packet.hold_id.startswith("hold:semantic_causal:")

    source_report = collector.validate_airline_transaction_artifact_ledger_source_bundle_v01(
        source_bundle,
    )
    assert source_report.validation_status == collector.STATUS_PASS
    item = _assert_collected_pass(source_bundle)
    hold_entry = _entry_by_type(item, ledger.ARTIFACT_AIRLINE_HOLD_PACKET)
    assert hold_entry.artifact_id == causal_report.hold_packet.packet_id
    assert hold_entry.canonical_hash_input["hold_id"] == causal_report.hold_packet.hold_id
    assert hold_entry.canonical_hash_input["source_snapshot"]["hold_id"] == (
        causal_report.hold_packet.hold_id
    )
    assert item.entry_count == 19
    assert item.dependency_edge_count == 29
    assert item.root_final_count == 3
    assert item.provider_called_count == 0
    assert item.network_used_count == 0
    assert item.gemini_called_count == 0
    assert item.real_world_effects_count == 0
    assert causal_report.provider_network_call_count == 0
    assert causal_report.gemini_call_count == 0


def test_real_shaped_reviewer_response_ids_preserve_ledger_continuity() -> None:
    source_bundle = _source_bundle_from_public_causal_runtime(
        binding.OFFER_A_ID,
        real_shaped_response_ids=True,
    )
    causal_report = source_bundle.causal_report
    expected_response_ids = tuple(
        f"{response.actor_id}_response_001"
        for response in causal_report.reviewer_responses
    )
    assert tuple(
        response.response_id
        for response in causal_report.reviewer_responses
    ) == expected_response_ids
    assert tuple(
        review.canonical_actor_output_id
        for review in causal_report.actor_reviews[1:]
    ) == expected_response_ids
    assert all("response" in value for value in expected_response_ids)

    source_validation = (
        collector.validate_airline_transaction_artifact_ledger_source_bundle_v01(
            source_bundle,
        )
    )
    assert source_validation.validation_status == collector.STATUS_PASS
    assert source_validation.validation_errors == ()

    item = _collect(source_bundle)
    expected_identity = _expected_identity(source_bundle)
    independent_validation = ledger.validate_airline_transaction_artifact_ledger_v01(
        item,
        expected_identity=expected_identity,
    )
    semantic_entry = _entry_by_type(
        item,
        ledger.ARTIFACT_VALIDATED_CANONICAL_SEMANTIC_EVIDENCE,
    )
    assert item.validation_status == ledger.STATUS_PASS
    assert item.validation_errors == ()
    assert independent_validation.validation_status == ledger.STATUS_PASS
    assert independent_validation.validation_errors == ()
    assert (
        semantic_entry.source_validation_refs
        == expected_identity.expected_source_validation_refs_by_type[
            ledger.ARTIFACT_VALIDATED_CANONICAL_SEMANTIC_EVIDENCE
        ]
    )
    assert all(
        value in semantic_entry.source_validation_refs
        for value in expected_response_ids
    )
    assert (
        independent_validation.entry_count,
        independent_validation.dependency_edge_count,
        independent_validation.root_final_count,
    ) == (19, 29, 3)
    assert item.provider_called_count == 0
    assert item.network_used_count == 0
    assert item.gemini_called_count == 0
    assert item.real_world_effects_count == 0


def test_actual_causal_hold_lineage_rewrite_fails_expected_identity() -> None:
    source_bundle = _source_bundle_from_public_causal_runtime(binding.OFFER_A_ID)
    item = _assert_collected_pass(source_bundle)
    original_hold_id = source_bundle.hold_packet.hold_id
    mutated = _replace_hold_id_everywhere_in_ledger(
        item,
        old_hold_id=original_hold_id,
        new_hold_id="hold:semantic_causal:forged",
    )
    _assert_lineage_tamper_fails(
        source_bundle,
        mutated,
        ledger.REASON_CANONICAL_SOURCE_LINEAGE_MISMATCH,
    )


def test_04_output_refs_match_independently_supplied_expected_refs() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    item = _assert_collected_pass(source_bundle)
    assert item.source_run_ref == source_bundle.expected_source_refs.source_run_ref
    assert (
        item.source_causal_report_ref
        == source_bundle.expected_source_refs.source_causal_report_ref
    )
    assert (
        item.source_corridor_report_ref
        == source_bundle.expected_source_refs.source_corridor_report_ref
    )


def test_natural_clientroot_and_airlineroot_ids_pass_without_replacement() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    item = _assert_collected_pass(source_bundle)
    decision = _entry_by_type(item, ledger.ARTIFACT_CLIENT_ROOT_SELECTION_DECISION)
    resolution = _entry_by_type(item, ledger.ARTIFACT_AIRLINE_ROOT_OFFER_RESOLUTION)
    assert decision.artifact_id == source_bundle.causal_report.client_root_decision.decision_id
    assert (
        resolution.artifact_id
        == source_bundle.causal_report.airline_root_resolution.resolution_id
    )
    assert decision.artifact_id.startswith("client_root_offer_selection_decision:")
    assert resolution.artifact_id.startswith(
        "airline_root_selected_offer_resolution:",
    )


def test_source_fixture_helper_performs_no_ledger_id_normalization() -> None:
    for helper in (_causal_report_for_offer, _source_bundle):
        source = inspect.getsource(helper)
        assert "ledger._artifact_ids_for_offer" not in source
        assert "decision_id=" not in source
        assert "resolution_id=" not in source
        assert "ARTIFACT_CLIENT_BSEP_PROJECTION" not in source
        assert "ARTIFACT_AIRLINE_BSEP_PROJECTION" not in source
        assert "ARTIFACT_BANK_BSEP_PROJECTION" not in source
        assert "ARTIFACT_CROSS_ROOT_BSEP_PROJECTION" not in source


def test_actual_shaped_bsep_projection_ids_pass_without_replacement() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    item = _assert_collected_pass(source_bundle)
    assert source_bundle.client_bsep_projection.projection_id == "client_bsep_projection"
    assert source_bundle.airline_bsep_projection.projection_id == "airline_bsep_projection"
    assert source_bundle.bank_bsep_projection.projection_id == "bank_bsep_projection"
    assert (
        source_bundle.cross_root_bsep_projection.projection_id
        == "cross_root_bsep_projection"
    )
    assert (
        _entry_by_type(item, ledger.ARTIFACT_CLIENT_BSEP_PROJECTION).artifact_id
        == "client_bsep_projection"
    )
    assert (
        _entry_by_type(item, ledger.ARTIFACT_AIRLINE_BSEP_PROJECTION).artifact_id
        == "airline_bsep_projection"
    )


def test_every_exact_source_artifact_id_reaches_ledger_unchanged() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    item = _assert_collected_pass(source_bundle)
    entries_by_type = {entry.artifact_type: entry for entry in item.entries}
    for artifact_type, artifact_id in _expected_artifact_ids(source_bundle).items():
        assert entries_by_type[artifact_type].artifact_id == artifact_id


def test_actual_semantic_source_ids_are_preserved() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    item = _assert_collected_pass(source_bundle)
    semantic = _entry_by_type(
        item,
        ledger.ARTIFACT_VALIDATED_CANONICAL_SEMANTIC_EVIDENCE,
    )
    expected_refs = (
        source_bundle.causal_report.client_constraint_set_id,
        source_bundle.causal_report.candidate_set_snapshot_id,
        source_bundle.causal_report.proposer_request.source_selection_input_id,
        source_bundle.causal_report.proposal.proposal_id,
        *tuple(
            review.canonical_actor_output_id
            for review in source_bundle.causal_report.actor_reviews
        ),
        source_bundle.causal_report.synthesis.synthesis_report_id,
        collector._binding_report_source_ref(
            source_bundle.causal_report.causal_binding_report,
        ),
    )
    assert semantic.source_validation_refs == expected_refs
    assert semantic.canonical_hash_input["source_validation_refs"] == expected_refs


def test_exact_human_approval_ref_is_preserved() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    item = _assert_collected_pass(source_bundle)
    purchase = _entry_by_type(item, ledger.ARTIFACT_CLIENT_PURCHASE_INTENT)
    expected_ref = source_bundle.purchase_approval_evidence.approval_ref
    assert purchase.source_validation_refs == (expected_ref,)
    assert purchase.canonical_hash_input["source_validation_refs"] == (expected_ref,)
    approval_snapshot = purchase.canonical_hash_input["source_snapshot"][
        "purchase_approval_evidence"
    ]
    assert approval_snapshot["approval_ref"] == expected_ref
    assert (
        approval_snapshot["approval_scope"]
        == source_bundle.purchase_approval_evidence.approval_scope
    )
    assert approval_snapshot["evidence_only"] is True
    assert approval_snapshot["creates_client_purchase_intent"] is False
    assert approval_snapshot["creates_action_commit_packet"] is False
    assert approval_snapshot["creates_payment_authorization"] is False
    assert approval_snapshot["creates_ticket"] is False
    assert approval_snapshot["creates_booking"] is False
    assert approval_snapshot["creates_future_permission"] is False


def test_05_invalid_causal_report_blocks_collection() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    bad = replace(
        source_bundle,
        causal_report=replace(
            source_bundle.causal_report,
            final_status=collector.STATUS_FAIL_CLOSED,
        ),
    )
    _assert_source_fails(bad, collector.REASON_SOURCE_CAUSAL_REPORT_INVALID)


def test_06_invalid_corridor_report_blocks_collection() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    bad = replace(
        source_bundle,
        corridor_report=replace(
            source_bundle.corridor_report,
            final_status=collector.STATUS_FAIL_CLOSED,
        ),
    )
    _assert_source_fails(bad, collector.REASON_SOURCE_CORRIDOR_REPORT_INVALID)


@pytest.mark.parametrize(
    "field_name",
    [
        "client_bsep_projection",
        "airline_bsep_projection",
        "bank_bsep_projection",
        "cross_root_bsep_projection",
    ],
)
def test_07_each_missing_bsep_projection_blocks_collection(field_name: str) -> None:
    bad = replace(_source_bundle(binding.OFFER_A_ID), **{field_name: None})
    _assert_source_fails(bad, collector.REASON_SOURCE_BSEP_PROJECTION_MISSING)


def test_08_bsep_packet_or_transaction_mismatch_blocks_collection() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    bad = replace(
        source_bundle,
        client_bsep_projection=replace(
            source_bundle.client_bsep_projection,
            bsep_packet_id="bsep_packet:wrong",
        ),
    )
    _assert_source_fails(bad, collector.REASON_SOURCE_BSEP_LINEAGE_MISMATCH)


def test_09_airline_bsep_causal_lineage_mismatch_blocks_collection() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    bad = replace(
        source_bundle,
        airline_bsep_projection=replace(
            source_bundle.airline_bsep_projection,
            projection_ref="bsep_projection:wrong",
        ),
    )
    _assert_source_fails(bad, collector.REASON_SOURCE_BSEP_LINEAGE_MISMATCH)


def test_10_semantic_recommendation_clientroot_mismatch_blocks_collection() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    bad = replace(
        source_bundle,
        causal_report=replace(
            source_bundle.causal_report,
            root_selected_offer_id=binding.OFFER_B_ID,
        ),
    )
    _assert_source_fails(bad, collector.REASON_SOURCE_ARTIFACT_OFFER_MISMATCH)


def test_11_clientroot_airlineroot_mismatch_blocks_collection() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    assert source_bundle.causal_report.airline_root_resolution is not None
    bad = replace(
        source_bundle,
        causal_report=replace(
            source_bundle.causal_report,
            airline_root_resolution=replace(
                source_bundle.causal_report.airline_root_resolution,
                selected_offer_id=binding.OFFER_B_ID,
            ),
        ),
    )
    _assert_source_fails(bad, collector.REASON_SOURCE_ARTIFACT_OFFER_MISMATCH)


def test_12_airlineroot_hold_mismatch_blocks_collection() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    bad = replace(
        source_bundle,
        hold_packet=replace(
            source_bundle.hold_packet,
            offer_id=binding.OFFER_B_ID,
        ),
    )
    _assert_source_fails(bad, collector.REASON_SOURCE_ARTIFACT_OFFER_MISMATCH)


def test_13_causal_hold_corridor_hold_mismatch_blocks_collection() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    bad = replace(
        source_bundle,
        hold_packet=replace(source_bundle.hold_packet, hold_id="hold:wrong"),
    )
    _assert_source_fails(bad, collector.REASON_SOURCE_ARTIFACT_HOLD_MISMATCH)


def test_14_corridor_context_source_offer_mismatch_blocks_collection() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    bad = replace(
        source_bundle,
        corridor_report=replace(
            source_bundle.corridor_report,
            contract_context=replace(
                source_bundle.corridor_report.contract_context,
                offer_id=binding.OFFER_B_ID,
            ),
        ),
    )
    _assert_source_fails(bad, collector.REASON_SOURCE_ARTIFACT_OFFER_MISMATCH)


@pytest.mark.parametrize(
    ("field_name", "value", "reason"),
    [
        ("amount", 9999, collector.REASON_SOURCE_ARTIFACT_AMOUNT_MISMATCH),
        ("currency", "BAD", collector.REASON_SOURCE_ARTIFACT_CURRENCY_MISMATCH),
        ("route_ref", "route:wrong", collector.REASON_SOURCE_ARTIFACT_ROUTE_MISMATCH),
        (
            "passenger_ref",
            "sealed_passenger_ref:wrong",
            collector.REASON_SOURCE_ARTIFACT_PASSENGER_MISMATCH,
        ),
    ],
)
def test_15_to_18_source_fact_mismatches_block_collection(
    field_name: str,
    value: object,
    reason: str,
) -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    bad = replace(
        source_bundle,
        offer_packet=replace(source_bundle.offer_packet, **{field_name: value}),
    )
    _assert_source_fails(bad, reason)


def test_19_phase_evidence_ref_mismatch_blocks_collection() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    phases = list(source_bundle.corridor_report.phase_results)
    phases[0] = replace(phases[0], evidence_refs_observed=("wrong:evidence",))
    bad = replace(
        source_bundle,
        corridor_report=replace(
            source_bundle.corridor_report,
            phase_results=tuple(phases),
        ),
    )
    _assert_source_fails(bad, collector.REASON_SOURCE_PHASE_EVIDENCE_REF_MISMATCH)


@pytest.mark.parametrize(
    "field_name",
    ["client_root_final", "airline_root_final", "bank_root_final"],
)
def test_20_each_missing_root_final_blocks_collection(field_name: str) -> None:
    bad = replace(_source_bundle(binding.OFFER_A_ID), **{field_name: None})
    _assert_source_fails(bad, collector.REASON_SOURCE_ROOT_FINAL_MISSING)


def test_21_wrong_root_final_owner_blocks_collection() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    bad = replace(
        source_bundle,
        bank_root_final=replace(
            source_bundle.bank_root_final,
            root_owner=ledger.CLIENT_ROOT_ID,
        ),
    )
    _assert_source_fails(bad, collector.REASON_SOURCE_ROOT_FINAL_WRONG_OWNER)


def test_22_shared_summary_as_fourth_root_blocks_collection() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    bad = replace(
        source_bundle,
        client_root_final=replace(
            source_bundle.client_root_final,
            root_owner=ledger.ROOT_OWNER_BSEP_CROSS_ROOT,
        ),
    )
    _assert_source_fails(
        bad,
        collector.REASON_SOURCE_SHARED_SUMMARY_USED_AS_ROOT_FINAL,
    )


@pytest.mark.parametrize(
    "refs",
    [
        ("unrelated:artifact",),
        (
            "shared_summary:root_final",
            "client_purchase_intent:client_001:001",
            "mock_purchase_receipt:client_001:001",
        ),
        (),
        (
            "client_root_offer_selection_decision:wrong",
            "client_purchase_intent:client_001:001",
            "mock_purchase_receipt:client_001:001",
            "extra:artifact",
        ),
    ],
)
def test_root_final_source_refs_are_exact(refs: tuple[str, ...]) -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    bad = replace(
        source_bundle,
        client_root_final=replace(
            source_bundle.client_root_final,
            source_artifact_refs=refs,
        ),
    )
    report = collector.validate_airline_transaction_artifact_ledger_source_bundle_v01(
        bad,
    )
    assert report.validation_status == collector.STATUS_FAIL_CLOSED
    assert (
        collector.REASON_SOURCE_ROOT_FINAL_WRONG_OWNER in report.validation_errors
        or collector.REASON_SOURCE_SHARED_SUMMARY_USED_AS_ROOT_FINAL
        in report.validation_errors
    )


def test_foreign_airline_authority_ref_in_client_root_final_fails() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    bad = replace(
        source_bundle,
        client_root_final=replace(
            source_bundle.client_root_final,
            source_artifact_refs=(
                source_bundle.causal_report.client_root_decision.decision_id,
                source_bundle.ticket_issue_intent.intent_id,
                source_bundle.mock_purchase_receipt.receipt_id,
            ),
        ),
    )
    _assert_source_fails(bad, collector.REASON_SOURCE_ROOT_FINAL_WRONG_OWNER)


def test_23_raw_provider_response_cannot_become_canonical_source() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    bad = replace(
        source_bundle,
        source_validation_refs=(
            *source_bundle.source_validation_refs,
            "raw_provider_response:forbidden",
        ),
    )
    _assert_source_fails(bad, collector.REASON_SOURCE_REF_MISMATCH)


def test_coherent_forged_top_level_source_refs_fail() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    forged_refs = ledger.AirlineTransactionArtifactLedgerExpectedSourceRefsV01(
        source_run_ref="source_run:forged",
        source_causal_report_ref="source_causal_report:forged",
        source_corridor_report_ref="source_corridor_report:forged",
    )
    bad = replace(
        source_bundle,
        expected_source_refs=forged_refs,
        source_validation_refs=(
            forged_refs.source_run_ref,
            forged_refs.source_causal_report_ref,
            forged_refs.source_corridor_report_ref,
        ),
    )
    _assert_source_fails(bad, collector.REASON_SOURCE_REF_MISMATCH)


def test_arbitrary_extra_source_validation_ref_fails() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    bad = replace(
        source_bundle,
        source_validation_refs=(
            *source_bundle.source_validation_refs,
            "source_validation_ref:extra_observation",
        ),
    )
    _assert_source_fails(bad, collector.REASON_SOURCE_REF_MISMATCH)


def test_arbitrary_extra_auxiliary_observation_ref_fails() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    bad = replace(
        source_bundle,
        auxiliary_observation_refs=(
            *source_bundle.auxiliary_observation_refs,
            "auxiliary_observation_ref:extra_observation",
        ),
    )
    _assert_source_fails(bad, collector.REASON_SOURCE_REF_MISMATCH)


def test_24_stored_pass_cannot_override_source_object_contradiction() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    bad = replace(
        source_bundle,
        offer_packet=replace(
            source_bundle.offer_packet,
            offer_id=binding.OFFER_B_ID,
        ),
    )
    _assert_source_fails(bad, collector.REASON_SOURCE_ARTIFACT_OFFER_MISMATCH)


def _collector_tree() -> ast.Module:
    return ast.parse(MODULE_PATH.read_text(encoding="utf-8"))


def test_25_collector_never_calls_ledger_fixture_builders() -> None:
    forbidden = {
        "build_airline_transaction_artifact_ledger_fixture_v01",
        "build_valid_airline_transaction_artifact_ledger_offer_a_v01",
        "build_valid_airline_transaction_artifact_ledger_offer_b_v01",
        "_build_valid_fixture_bundle_v01",
    }
    for node in ast.walk(_collector_tree()):
        if isinstance(node, ast.Call):
            func = node.func
            name = func.id if isinstance(func, ast.Name) else getattr(func, "attr", "")
            assert name not in forbidden


def test_collector_never_calls_private_fixture_entry_constructors() -> None:
    forbidden = {
        "_entry",
        "_artifact_ids_for_offer",
        "_expected_dependencies_by_artifact_type",
        "build_airline_transaction_artifact_ledger_fixture_v01",
        "build_valid_airline_transaction_artifact_ledger_offer_a_v01",
        "build_valid_airline_transaction_artifact_ledger_offer_b_v01",
    }
    for node in ast.walk(_collector_tree()):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
            if func.value.id == "ledger":
                assert func.attr not in forbidden
        name = func.id if isinstance(func, ast.Name) else getattr(func, "attr", "")
        assert name not in forbidden


def test_source_aware_builder_requires_exact_refs() -> None:
    signature = inspect.signature(
        ledger.build_airline_transaction_artifact_ledger_entry_from_source_v01,
    )
    assert "source_validation_refs" in signature.parameters
    assert "auxiliary_artifact_refs" in signature.parameters
    assert "source_identity_fields" in signature.parameters


def test_26_collector_never_calls_semantic_collector_functions() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "collect_airline_semantic_to_contract_causal_run_v01" not in source
    assert (
        "collect_airline_semantic_to_contract_causal_run_from_precollected_payloads_v01"
        not in source
    )


def test_27_collector_never_calls_corridor_collector_functions() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "collect_airline_ticket_purchase_corridor_state_machine_v01" not in source


def test_28_collector_performs_no_file_reads_or_writes() -> None:
    tree = _collector_tree()
    for node in ast.walk(tree):
        assert not isinstance(node, (ast.With, ast.AsyncWith))
        assert not (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "open"
        )
        assert not (
            isinstance(node, ast.Attribute)
            and node.attr in {"read_text", "write_text", "read_bytes", "write_bytes"}
        )


def test_29_collector_does_not_mutate_source_bundle() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    before = deepcopy(source_bundle)
    _assert_collected_pass(source_bundle)
    assert source_bundle == before


def test_30_collector_does_not_mutate_causal_report() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    before = deepcopy(source_bundle.causal_report)
    _assert_collected_pass(source_bundle)
    assert source_bundle.causal_report == before


def test_31_collector_does_not_mutate_corridor_report() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    before = deepcopy(source_bundle.corridor_report)
    _assert_collected_pass(source_bundle)
    assert source_bundle.corridor_report == before


def test_32_a_b_a_isolation_passes() -> None:
    _assert_collected_pass(_source_bundle(binding.OFFER_A_ID))
    _assert_collected_pass(_source_bundle(binding.OFFER_B_ID))
    _assert_collected_pass(_source_bundle(binding.OFFER_A_ID))


def test_33_b_a_b_isolation_passes() -> None:
    _assert_collected_pass(_source_bundle(binding.OFFER_B_ID))
    _assert_collected_pass(_source_bundle(binding.OFFER_A_ID))
    _assert_collected_pass(_source_bundle(binding.OFFER_B_ID))


@pytest.mark.parametrize(
    "source_bundle",
    [
        object(),
        replace(_source_bundle(binding.OFFER_A_ID), transaction_id=["bad"]),
        replace(
            _source_bundle(binding.OFFER_A_ID),
            client_bsep_projection=replace(
                _source_bundle(binding.OFFER_A_ID).client_bsep_projection,
                projection_id=["bad"],
            ),
        ),
        replace(
            _source_bundle(binding.OFFER_A_ID),
            source_validation_refs=(["bad"],),
        ),
    ],
)
def test_34_malformed_nested_python_values_fail_without_exception(
    source_bundle: object,
) -> None:
    report = collector.validate_airline_transaction_artifact_ledger_source_bundle_v01(
        source_bundle,
    )
    assert report.validation_status == collector.STATUS_FAIL_CLOSED
    item = _collect(source_bundle)
    assert item.validation_status == ledger.STATUS_FAIL_CLOSED


@pytest.mark.parametrize(
    "bad_source_bundle",
    [
        replace(_source_bundle(binding.OFFER_A_ID), causal_report=object()),
        replace(_source_bundle(binding.OFFER_A_ID), corridor_report=object()),
        replace(
            _source_bundle(binding.OFFER_A_ID),
            corridor_report=replace(
                _source_bundle(binding.OFFER_A_ID).corridor_report,
                contract_context=object(),
            ),
        ),
        replace(
            _source_bundle(binding.OFFER_A_ID),
            corridor_report=replace(
                _source_bundle(binding.OFFER_A_ID).corridor_report,
                phase_results=(object(),),
            ),
        ),
        replace(
            _source_bundle(binding.OFFER_A_ID),
            corridor_report=replace(
                _source_bundle(binding.OFFER_A_ID).corridor_report,
                counter_table=[],
            ),
        ),
        replace(
            _source_bundle(binding.OFFER_A_ID),
            causal_report=replace(
                _source_bundle(binding.OFFER_A_ID).causal_report,
                provider_call_records=object(),
            ),
        ),
        replace(
            _source_bundle(binding.OFFER_A_ID),
            causal_report=replace(
                _source_bundle(binding.OFFER_A_ID).causal_report,
                reviewer_responses=object(),
            ),
        ),
        replace(
            _source_bundle(binding.OFFER_A_ID),
            causal_report=replace(
                _source_bundle(binding.OFFER_A_ID).causal_report,
                actor_reviews=object(),
            ),
        ),
        replace(
            _source_bundle(binding.OFFER_A_ID),
            causal_report=replace(
                _source_bundle(binding.OFFER_A_ID).causal_report,
                local_chain_validation=object(),
            ),
        ),
        replace(
            _source_bundle(binding.OFFER_A_ID),
            corridor_report=replace(
                _source_bundle(binding.OFFER_A_ID).corridor_report,
                transitions=object(),
            ),
        ),
        replace(
            _source_bundle(binding.OFFER_A_ID),
            corridor_report=replace(
                _source_bundle(binding.OFFER_A_ID).corridor_report,
                core_domain_delegation_matrix=object(),
            ),
        ),
        replace(
            _source_bundle(binding.OFFER_A_ID),
            corridor_report=replace(
                _source_bundle(binding.OFFER_A_ID).corridor_report,
                receipt_boundary_summary=object(),
            ),
        ),
        replace(
            _source_bundle(binding.OFFER_A_ID),
            causal_report=replace(
                _source_bundle(binding.OFFER_A_ID).causal_report,
                proposal=object(),
            ),
        ),
        replace(
            _source_bundle(binding.OFFER_A_ID),
            causal_report=replace(
                _source_bundle(binding.OFFER_A_ID).causal_report,
                client_root_decision=object(),
            ),
        ),
        replace(
            _source_bundle(binding.OFFER_A_ID),
            causal_report=replace(
                _source_bundle(binding.OFFER_A_ID).causal_report,
                airline_root_resolution=object(),
            ),
        ),
    ],
)
def test_malformed_reports_fail_closed_without_exception(
    bad_source_bundle: object,
) -> None:
    report = collector.validate_airline_transaction_artifact_ledger_source_bundle_v01(
        bad_source_bundle,
    )
    assert report.validation_status == collector.STATUS_FAIL_CLOSED
    item = _collect(bad_source_bundle)
    assert item.validation_status == ledger.STATUS_FAIL_CLOSED


@pytest.mark.parametrize(
    "bad_source_bundle",
    [
        replace(
            _source_bundle(binding.OFFER_A_ID),
            offer_packet=replace(
                _source_bundle(binding.OFFER_A_ID).offer_packet,
                created_by=object(),
            ),
        ),
        replace(
            _source_bundle(binding.OFFER_A_ID),
            hold_packet=replace(
                _source_bundle(binding.OFFER_A_ID).hold_packet,
                ttl_seconds=object(),
            ),
        ),
        replace(
            _source_bundle(binding.OFFER_A_ID),
            hold_packet=replace(
                _source_bundle(binding.OFFER_A_ID).hold_packet,
                idempotency_key=object(),
            ),
        ),
        replace(
            _source_bundle(binding.OFFER_A_ID),
            hold_packet=replace(
                _source_bundle(binding.OFFER_A_ID).hold_packet,
                allowed_adapters=object(),
            ),
        ),
        replace(
            _source_bundle(binding.OFFER_A_ID),
            hold_packet=replace(
                _source_bundle(binding.OFFER_A_ID).hold_packet,
                forbidden_actions=object(),
            ),
        ),
        replace(
            _source_bundle(binding.OFFER_A_ID),
            purchase_approval_evidence=replace(
                _source_bundle(binding.OFFER_A_ID).purchase_approval_evidence,
                max_amount=object(),
            ),
        ),
        replace(
            _source_bundle(binding.OFFER_A_ID),
            payment_authorization_ref=replace(
                _source_bundle(binding.OFFER_A_ID).payment_authorization_ref,
                merchant_ref=object(),
            ),
        ),
        replace(
            _source_bundle(binding.OFFER_A_ID),
            ticket_issue_intent=replace(
                _source_bundle(binding.OFFER_A_ID).ticket_issue_intent,
                ttl_seconds=object(),
            ),
        ),
        replace(
            _source_bundle(binding.OFFER_A_ID),
            ticket_issue_intent=replace(
                _source_bundle(binding.OFFER_A_ID).ticket_issue_intent,
                expired=object(),
            ),
        ),
    ],
)
def test_malformed_contract_fields_fail_closed_without_exception(
    bad_source_bundle: object,
) -> None:
    _assert_source_fails(
        bad_source_bundle,
        collector.REASON_SOURCE_ARTIFACT_WRONG_TYPE,
    )


def test_35_wrong_expected_source_refs_fail_closed() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    bad = replace(
        source_bundle,
        expected_source_refs=replace(
            source_bundle.expected_source_refs,
            source_run_ref="source_run:wrong",
        ),
    )
    _assert_source_fails(bad, collector.REASON_SOURCE_REF_MISMATCH)


def test_36_no_provider_network_gemini_config_demo_imports() -> None:
    forbidden = {
        "demo",
        "config",
        "google",
        "requests",
        "urllib",
        "openai",
        "subprocess",
        "socket",
    }
    imports: set[str] = set()
    for node in ast.walk(_collector_tree()):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        if isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    assert not imports.intersection(forbidden)


def test_37_no_crypto_or_replay_implementation() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "hashlib" not in source
    assert "sha256" not in source
    assert "cryptography" not in source
    assert "Replay implementation" not in source


def test_38_real_world_effects_remain_zero_or_fail_closed() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    bad = replace(
        source_bundle,
        mock_ticket_receipt=replace(
            source_bundle.mock_ticket_receipt,
            real_world_effects_count=1,
        ),
    )
    _assert_source_fails(bad, collector.REASON_SOURCE_REAL_EFFECT_DETECTED)


def test_39_no_default_or_fallback_source_bundle() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "default Offer A" not in source
    assert "fallback" not in source
    item = collector.collect_airline_transaction_artifact_ledger_from_source_v01(
        source_bundle=object(),
    )
    assert item.validation_status == ledger.STATUS_FAIL_CLOSED


def test_40_one_bundle_produces_exactly_one_ledger() -> None:
    item = _collect(_source_bundle(binding.OFFER_A_ID))
    assert isinstance(item, ledger.AirlineTransactionArtifactLedgerV01)
    assert item.entry_count == 19


def test_bsep_packet_id_mutation_is_preserved_when_consistent() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    base = _assert_collected_pass(source_bundle)
    changed_packet = "bsep_packet:changed_source_packet"
    bad = replace(
        source_bundle,
        client_bsep_projection=replace(
            source_bundle.client_bsep_projection,
            bsep_packet_id=changed_packet,
        ),
        airline_bsep_projection=replace(
            source_bundle.airline_bsep_projection,
            bsep_packet_id=changed_packet,
        ),
        bank_bsep_projection=replace(
            source_bundle.bank_bsep_projection,
            bsep_packet_id=changed_packet,
        ),
        cross_root_bsep_projection=replace(
            source_bundle.cross_root_bsep_projection,
            bsep_packet_id=changed_packet,
        ),
    )
    changed = _assert_collected_pass(bad)
    base_airline = _entry_by_type(base, ledger.ARTIFACT_AIRLINE_BSEP_PROJECTION)
    changed_airline = _entry_by_type(changed, ledger.ARTIFACT_AIRLINE_BSEP_PROJECTION)
    assert base_airline.canonical_hash_input != changed_airline.canonical_hash_input
    assert changed_airline.canonical_hash_input["bsep_packet_id"] == changed_packet


@pytest.mark.parametrize(
    ("field_name", "artifact_type"),
    [
        ("client_bsep_projection", ledger.ARTIFACT_CLIENT_BSEP_PROJECTION),
        ("bank_bsep_projection", ledger.ARTIFACT_BANK_BSEP_PROJECTION),
        (
            "cross_root_bsep_projection",
            ledger.ARTIFACT_CROSS_ROOT_BSEP_PROJECTION,
        ),
    ],
)
def test_non_airline_bsep_projection_ref_mutation_is_preserved(
    field_name: str,
    artifact_type: str,
) -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    projection = getattr(source_bundle, field_name)
    bad = replace(
        source_bundle,
        **{
            field_name: replace(
                projection,
                projection_ref=f"{projection.projection_ref}:changed",
            ),
        },
    )
    item = _assert_collected_pass(bad)
    entry = _entry_by_type(item, artifact_type)
    assert entry.canonical_hash_input["projection_ref"].endswith(":changed")


def test_bsep_projection_id_mutation_reaches_ledger_identity() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    changed_id = "client_bsep_projection_changed"
    bad = replace(
        source_bundle,
        client_bsep_projection=replace(
            source_bundle.client_bsep_projection,
            projection_id=changed_id,
        ),
    )
    item = _assert_collected_pass(bad)
    entry = _entry_by_type(item, ledger.ARTIFACT_CLIENT_BSEP_PROJECTION)
    assert entry.artifact_id == changed_id
    assert entry.canonical_hash_input["projection_id"] == changed_id


def test_root_final_lineage_is_preserved_in_ledger_canonical_source() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    item = _assert_collected_pass(source_bundle)
    client_final = _entry_by_type(item, ledger.ARTIFACT_CLIENT_ROOT_FINAL)
    airline_final = _entry_by_type(item, ledger.ARTIFACT_AIRLINE_ROOT_FINAL)
    bank_final = _entry_by_type(item, ledger.ARTIFACT_BANK_ROOT_FINAL)
    assert (
        client_final.canonical_hash_input["source_artifact_refs"]
        == source_bundle.client_root_final.source_artifact_refs
    )
    assert (
        airline_final.canonical_hash_input["source_artifact_refs"]
        == source_bundle.airline_root_final.source_artifact_refs
    )
    assert (
        bank_final.canonical_hash_input["source_artifact_refs"]
        == source_bundle.bank_root_final.source_artifact_refs
    )


def test_forged_client_bsep_projection_ref_in_ledger_fails_closed() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    item = _assert_collected_pass(source_bundle)
    tampered = _replace_hash(
        item,
        ledger.ARTIFACT_CLIENT_BSEP_PROJECTION,
        projection_ref="bsep_projection:client:forged",
    )
    _assert_lineage_tamper_fails(
        source_bundle,
        tampered,
        ledger.REASON_CANONICAL_SOURCE_LINEAGE_MISMATCH,
    )


def test_coherently_forged_bsep_packet_ids_in_ledger_fail_closed() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    item = _assert_collected_pass(source_bundle)
    tampered = item
    for artifact_type in (
        ledger.ARTIFACT_CLIENT_BSEP_PROJECTION,
        ledger.ARTIFACT_AIRLINE_BSEP_PROJECTION,
        ledger.ARTIFACT_BANK_BSEP_PROJECTION,
        ledger.ARTIFACT_CROSS_ROOT_BSEP_PROJECTION,
    ):
        tampered = _replace_hash(
            tampered,
            artifact_type,
            bsep_packet_id="bsep_packet:coherently_forged",
        )
    _assert_lineage_tamper_fails(
        source_bundle,
        tampered,
        ledger.REASON_CANONICAL_SOURCE_LINEAGE_MISMATCH,
    )


@pytest.mark.parametrize(
    "artifact_type",
    [
        ledger.ARTIFACT_CLIENT_ROOT_FINAL,
        ledger.ARTIFACT_AIRLINE_ROOT_FINAL,
        ledger.ARTIFACT_BANK_ROOT_FINAL,
    ],
)
def test_forged_root_final_source_artifact_refs_in_ledger_fail_closed(
    artifact_type: str,
) -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    item = _assert_collected_pass(source_bundle)
    tampered = _replace_hash(
        item,
        artifact_type,
        source_artifact_refs=("forged:root_final_source_ref",),
    )
    _assert_lineage_tamper_fails(
        source_bundle,
        tampered,
        ledger.REASON_CANONICAL_SOURCE_LINEAGE_MISMATCH,
    )


def test_forged_semantic_source_refs_in_ledger_fail_closed() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    item = _assert_collected_pass(source_bundle)
    semantic = _entry_by_type(
        item,
        ledger.ARTIFACT_VALIDATED_CANONICAL_SEMANTIC_EVIDENCE,
    )
    forged_refs = (
        "client_constraints:forged",
        "candidate_snapshot:forged",
        "selection_input:forged",
        "proposal:forged",
        *semantic.source_validation_refs[4:9],
        "synthesis:forged",
        "binding_report:forged",
    )
    tampered = _replace_entry(
        item,
        ledger.ARTIFACT_VALIDATED_CANONICAL_SEMANTIC_EVIDENCE,
        source_validation_refs=forged_refs,
        canonical_hash_input={
            **dict(semantic.canonical_hash_input),
            "source_validation_refs": forged_refs,
        },
    )
    _assert_lineage_tamper_fails(
        source_bundle,
        tampered,
        ledger.REASON_SOURCE_VALIDATION_REF_LINEAGE_MISMATCH,
    )


def test_forged_purchase_approval_ref_in_ledger_only_fails_closed() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    item = _assert_collected_pass(source_bundle)
    purchase = _entry_by_type(item, ledger.ARTIFACT_CLIENT_PURCHASE_INTENT)
    forged_refs = ("human_approval:forged",)
    tampered = _replace_entry(
        item,
        ledger.ARTIFACT_CLIENT_PURCHASE_INTENT,
        source_validation_refs=forged_refs,
        canonical_hash_input={
            **dict(purchase.canonical_hash_input),
            "source_validation_refs": forged_refs,
        },
    )
    _assert_lineage_tamper_fails(
        source_bundle,
        tampered,
        ledger.REASON_SOURCE_VALIDATION_REF_LINEAGE_MISMATCH,
    )


def test_coordinated_valid_approval_ref_change_produces_distinct_pass_ledger() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    baseline = _assert_collected_pass(source_bundle)
    changed_ref = "human_approval:client_001:airline_purchase:changed"
    changed_bundle = _source_bundle_with_approval_ref(source_bundle, changed_ref)
    source_report = collector.validate_airline_transaction_artifact_ledger_source_bundle_v01(
        changed_bundle,
    )
    assert source_report.validation_status == collector.STATUS_PASS
    changed = _assert_collected_pass(changed_bundle)
    purchase = _entry_by_type(changed, ledger.ARTIFACT_CLIENT_PURCHASE_INTENT)
    assert purchase.source_validation_refs == (changed_ref,)
    assert purchase.canonical_hash_input["source_validation_refs"] == (changed_ref,)
    assert changed != baseline


def test_same_approval_ref_with_changed_scope_cannot_collapse() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    baseline = _assert_collected_pass(source_bundle)
    changed_scope = "selected_mock_offer_purchase_intent_only:scope_probe"
    changed_bundle = _source_bundle_with_approval_scope(
        source_bundle,
        changed_scope,
    )
    source_report = collector.validate_airline_transaction_artifact_ledger_source_bundle_v01(
        changed_bundle,
    )
    if source_report.validation_status == collector.STATUS_PASS:
        changed = _assert_collected_pass(changed_bundle)
        purchase = _entry_by_type(changed, ledger.ARTIFACT_CLIENT_PURCHASE_INTENT)
        assert (
            purchase.canonical_hash_input["source_snapshot"][
                "purchase_approval_evidence"
            ]["approval_scope"]
            == changed_scope
        )
        assert changed != baseline
    else:
        assert _collect(changed_bundle).validation_status == ledger.STATUS_FAIL_CLOSED


def test_distinct_valid_source_lineage_cannot_collapse_to_same_ledger() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    baseline = _assert_collected_pass(source_bundle)
    approval_changed = _source_bundle_with_approval_ref(
        source_bundle,
        "human_approval:client_001:airline_purchase:anti_collapse",
    )
    bsep_ref_changed = replace(
        source_bundle,
        client_bsep_projection=replace(
            source_bundle.client_bsep_projection,
            projection_ref="bsep_projection:client:anti_collapse",
        ),
    )
    packet_changed = replace(
        source_bundle,
        client_bsep_projection=replace(
            source_bundle.client_bsep_projection,
            bsep_packet_id="bsep_packet:anti_collapse",
        ),
        airline_bsep_projection=replace(
            source_bundle.airline_bsep_projection,
            bsep_packet_id="bsep_packet:anti_collapse",
        ),
        bank_bsep_projection=replace(
            source_bundle.bank_bsep_projection,
            bsep_packet_id="bsep_packet:anti_collapse",
        ),
        cross_root_bsep_projection=replace(
            source_bundle.cross_root_bsep_projection,
            bsep_packet_id="bsep_packet:anti_collapse",
        ),
    )
    root_refs_changed = replace(
        source_bundle,
        client_root_final=replace(
            source_bundle.client_root_final,
            source_artifact_refs=(
                source_bundle.causal_report.client_root_decision.decision_id,
                source_bundle.purchase_intent.intent_id,
                "mock_purchase_receipt:forged",
            ),
        ),
    )
    proposal_changed = replace(
        source_bundle,
        causal_report=replace(
            source_bundle.causal_report,
            proposal=replace(
                source_bundle.causal_report.proposal,
                proposal_id="semantic_offer_selection_proposal:anti_collapse",
            ),
        ),
    )
    actor_reviews = list(source_bundle.causal_report.actor_reviews)
    actor_reviews[0] = replace(
        actor_reviews[0],
        canonical_actor_output_id="canonical_actor_output:anti_collapse",
    )
    review_changed = replace(
        source_bundle,
        causal_report=replace(
            source_bundle.causal_report,
            actor_reviews=tuple(actor_reviews),
        ),
    )
    synthesis_changed = replace(
        source_bundle,
        causal_report=replace(
            source_bundle.causal_report,
            synthesis=replace(
                source_bundle.causal_report.synthesis,
                synthesis_report_id="semantic_selection_synthesis:anti_collapse",
            ),
        ),
    )
    for mutated in (
        approval_changed,
        proposal_changed,
        review_changed,
        synthesis_changed,
        bsep_ref_changed,
        packet_changed,
        root_refs_changed,
    ):
        _assert_lineage_change_does_not_collapse(mutated, baseline)


@pytest.mark.parametrize(
    "mutator,artifact_type,field_name,expected_value",
    [
        (
            lambda source_bundle: _source_bundle_with_passenger_ref(
                source_bundle,
                "passenger:anti_collapse",
            ),
            ledger.ARTIFACT_AIRLINE_OFFER_PACKET,
            "passenger_ref",
            "passenger:anti_collapse",
        ),
        (
            lambda source_bundle: _source_bundle_with_hold_idempotency(
                source_bundle,
                "idem:airline_hold:anti_collapse",
            ),
            ledger.ARTIFACT_AIRLINE_HOLD_PACKET,
            "idempotency_key",
            "idem:airline_hold:anti_collapse",
        ),
        (
            lambda source_bundle: _source_bundle_with_purchase_idempotency(
                source_bundle,
                "idem:client_purchase_intent:anti_collapse",
            ),
            ledger.ARTIFACT_CLIENT_PURCHASE_INTENT,
            ("purchase_intent", "idempotency_key"),
            "idem:client_purchase_intent:anti_collapse",
        ),
        (
            lambda source_bundle: _source_bundle_with_payment_idempotency(
                source_bundle,
                "idem:bank_payment_authorization:anti_collapse",
            ),
            ledger.ARTIFACT_BANK_PAYMENT_AUTHORIZATION,
            "idempotency_key",
            "idem:bank_payment_authorization:anti_collapse",
        ),
        (
            lambda source_bundle: _source_bundle_with_ticket_idempotency(
                source_bundle,
                "idem:airline_ticket_issue:anti_collapse",
            ),
            ledger.ARTIFACT_AIRLINE_TICKET_ISSUE_INTENT,
            "idempotency_key",
            "idem:airline_ticket_issue:anti_collapse",
        ),
        (
            lambda source_bundle: _source_bundle_with_max_amount(
                source_bundle,
                1500,
            ),
            ledger.ARTIFACT_CLIENT_PURCHASE_INTENT,
            ("purchase_intent", "max_amount"),
            1500,
        ),
        (
            lambda source_bundle: _source_bundle_with_merchant_ref(
                source_bundle,
                "merchant:anti_collapse",
            ),
            ledger.ARTIFACT_BANK_PAYMENT_AUTHORIZATION,
            "merchant_ref",
            "merchant:anti_collapse",
        ),
        (
            lambda source_bundle: _source_bundle_with_ttl_seconds(
                source_bundle,
                7200,
            ),
            ledger.ARTIFACT_AIRLINE_HOLD_PACKET,
            "ttl_seconds",
            7200,
        ),
        (
            lambda source_bundle: _source_bundle_with_mock_ticket_identity(
                source_bundle,
                mock_ticket_id="mock_ticket:anti_collapse",
                mock_pnr="PNRANTI",
            ),
            ledger.ARTIFACT_MOCK_TICKET_RECEIPT,
            "mock_ticket_id",
            "mock_ticket:anti_collapse",
        ),
        (
            lambda source_bundle: _source_bundle_with_mock_ticket_identity(
                source_bundle,
                mock_ticket_id="mock_ticket:anti_collapse",
                mock_pnr="PNRANTI",
            ),
            ledger.ARTIFACT_MOCK_TICKET_RECEIPT,
            "mock_pnr",
            "PNRANTI",
        ),
    ],
)
def test_exact_source_snapshot_changes_cannot_collapse_to_same_pass_ledger(
    mutator: object,
    artifact_type: str,
    field_name: str,
    expected_value: object,
) -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    baseline = _assert_collected_pass(source_bundle)
    mutated = mutator(source_bundle)
    _assert_snapshot_change_does_not_collapse(
        mutated,
        baseline,
        artifact_type=artifact_type,
        field_name=field_name,
        expected_value=expected_value,
    )


def test_coordinated_full_idempotency_chain_change_produces_distinct_ledger() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    baseline = _assert_collected_pass(source_bundle)
    mutated = _source_bundle_with_full_idempotency_chain(source_bundle)
    item = _assert_snapshot_change_does_not_collapse(
        mutated,
        baseline,
        artifact_type=ledger.ARTIFACT_MOCK_TICKET_RECEIPT,
        field_name="source_idempotency_key",
        expected_value="idem:airline_ticket_issue:anti_collapse",
    )
    assert (
        _entry_by_type(
            item,
            ledger.ARTIFACT_AIRLINE_HOLD_PACKET,
        ).canonical_hash_input["source_snapshot"]["idempotency_key"]
        == "idem:airline_hold:anti_collapse"
    )
    assert (
        _entry_by_type(
            item,
            ledger.ARTIFACT_CLIENT_PURCHASE_INTENT,
        ).canonical_hash_input["source_snapshot"]["purchase_intent"][
            "idempotency_key"
        ]
        == "idem:client_purchase_intent:anti_collapse"
    )
    assert (
        _entry_by_type(
            item,
            ledger.ARTIFACT_BANK_PAYMENT_AUTHORIZATION,
        ).canonical_hash_input["source_snapshot"]["idempotency_key"]
        == "idem:bank_payment_authorization:anti_collapse"
    )


def test_coordinated_expired_state_fails_closed_without_exception() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    expired = replace(
        source_bundle,
        offer_packet=replace(source_bundle.offer_packet, expired=True),
        hold_packet=replace(source_bundle.hold_packet, expired=True),
        purchase_intent=replace(source_bundle.purchase_intent, expired=True),
        payment_authorization_ref=replace(
            source_bundle.payment_authorization_ref,
            expired=True,
        ),
        ticket_issue_intent=replace(source_bundle.ticket_issue_intent, expired=True),
    )
    report = collector.validate_airline_transaction_artifact_ledger_source_bundle_v01(
        expired,
    )
    assert report.validation_status == collector.STATUS_FAIL_CLOSED
    assert report.validation_errors
    assert _collect(expired).validation_status == ledger.STATUS_FAIL_CLOSED


@pytest.mark.parametrize(
    "artifact_type,updates",
    [
        (
            ledger.ARTIFACT_AIRLINE_OFFER_PACKET,
            {"passenger_ref": "passenger:forged"},
        ),
        (
            ledger.ARTIFACT_AIRLINE_HOLD_PACKET,
            {"idempotency_key": "idem:forged"},
        ),
        (
            ledger.ARTIFACT_CLIENT_PURCHASE_INTENT,
            {"purchase_intent": {"max_amount": 9999}},
        ),
        (
            ledger.ARTIFACT_BANK_PAYMENT_AUTHORIZATION,
            {"merchant_ref": "merchant:forged"},
        ),
        (
            ledger.ARTIFACT_MOCK_TICKET_RECEIPT,
            {"mock_ticket_id": "mock_ticket:forged"},
        ),
    ],
)
def test_post_collection_source_snapshot_tampering_fails_expected_identity(
    artifact_type: str,
    updates: dict[str, object],
) -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    item = _assert_collected_pass(source_bundle)
    tampered = _tamper_source_snapshot(item, artifact_type, **updates)
    _assert_lineage_tamper_fails(
        source_bundle,
        tampered,
        ledger.REASON_CANONICAL_SOURCE_LINEAGE_MISMATCH,
    )


def test_post_collection_approval_scope_tampering_fails_expected_identity() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    item = _assert_collected_pass(source_bundle)
    tampered = _tamper_purchase_approval_snapshot(
        item,
        approval_scope="selected_mock_offer_purchase_intent_only:forged",
    )
    _assert_lineage_tamper_fails(
        source_bundle,
        tampered,
        ledger.REASON_CANONICAL_SOURCE_LINEAGE_MISMATCH,
    )


def test_source_snapshot_allowlists_cover_every_current_typed_source_field() -> None:
    expected_types = {
        ledger.ARTIFACT_TRANSACTION_SCOPE: (
            contracts.AirlineTicketPurchaseContractContextV01
        ),
        ledger.ARTIFACT_CLIENT_BSEP_PROJECTION: (
            collector.AirlineTransactionArtifactLedgerBSEPProjectionSourceV01
        ),
        ledger.ARTIFACT_AIRLINE_BSEP_PROJECTION: (
            collector.AirlineTransactionArtifactLedgerBSEPProjectionSourceV01
        ),
        ledger.ARTIFACT_BANK_BSEP_PROJECTION: (
            collector.AirlineTransactionArtifactLedgerBSEPProjectionSourceV01
        ),
        ledger.ARTIFACT_CROSS_ROOT_BSEP_PROJECTION: (
            collector.AirlineTransactionArtifactLedgerBSEPProjectionSourceV01
        ),
        ledger.ARTIFACT_CLIENT_ROOT_SELECTION_DECISION: (
            binding.ClientRootOfferSelectionDecisionV01
        ),
        ledger.ARTIFACT_AIRLINE_ROOT_OFFER_RESOLUTION: (
            binding.AirlineRootSelectedOfferResolutionV01
        ),
        ledger.ARTIFACT_AIRLINE_OFFER_PACKET: contracts.AirlineOfferPacketV01,
        ledger.ARTIFACT_AIRLINE_HOLD_PACKET: contracts.AirlineHoldCommitPacketV01,
        ledger.ARTIFACT_AIRLINE_OFFER_HOLD_RECEIPT: (
            contracts.AirlineOfferHoldReceiptV01
        ),
        ledger.ARTIFACT_CLIENT_PURCHASE_INTENT: contracts.ClientPurchaseIntentV01,
        ledger.ARTIFACT_BANK_PAYMENT_AUTHORIZATION: (
            contracts.BankPaymentAuthorizationRefV01
        ),
        ledger.ARTIFACT_AIRLINE_TICKET_ISSUE_INTENT: (
            contracts.AirlineTicketIssueIntentV01
        ),
        ledger.ARTIFACT_MOCK_TICKET_RECEIPT: contracts.MockTicketReceiptV01,
        ledger.ARTIFACT_MOCK_PURCHASE_RECEIPT: contracts.MockPurchaseReceiptV01,
        ledger.ARTIFACT_CLIENT_ROOT_FINAL: (
            collector.AirlineTransactionArtifactLedgerRootFinalSourceV01
        ),
        ledger.ARTIFACT_AIRLINE_ROOT_FINAL: (
            collector.AirlineTransactionArtifactLedgerRootFinalSourceV01
        ),
        ledger.ARTIFACT_BANK_ROOT_FINAL: (
            collector.AirlineTransactionArtifactLedgerRootFinalSourceV01
        ),
    }
    for artifact_type, source_type in expected_types.items():
        included = set(
            collector.CANONICAL_SOURCE_SNAPSHOT_FIELDS_BY_ARTIFACT_TYPE[
                artifact_type
            ],
        )
        excluded = set(
            collector.NON_CANONICAL_SOURCE_FIELDS_BY_ARTIFACT_TYPE.get(
                artifact_type,
                {},
            ),
        )
        actual = {field.name for field in fields(source_type)}
        assert included.isdisjoint(excluded)
        assert included | excluded == actual
    approval_fields = {field.name for field in fields(contracts.AirlinePurchaseApprovalEvidenceRefV01)}
    approval_included = set(collector.APPROVAL_SNAPSHOT_FIELDS)
    approval_excluded = set(
        collector.NON_CANONICAL_SOURCE_FIELDS_BY_ARTIFACT_TYPE.get(
            "AirlinePurchaseApprovalEvidenceRefV01",
            {},
        ),
    )
    assert approval_included.isdisjoint(approval_excluded)
    assert approval_included | approval_excluded == approval_fields


def test_approval_snapshot_fields_are_used_by_production_collector() -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    loads = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Name)
        and node.id == "APPROVAL_SNAPSHOT_FIELDS"
        and isinstance(node.ctx, ast.Load)
    ]
    assert loads


def test_source_bundle_nested_mappings_are_immutable() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    mutable_payload = dict(source_bundle.causal_report.proposer_payload)
    rebuilt = replace(
        source_bundle,
        causal_report=replace(
            source_bundle.causal_report,
            proposer_payload=mutable_payload,
        ),
    )
    mutable_payload["recommended_offer_id"] = binding.OFFER_B_ID
    assert rebuilt.causal_report.proposer_payload["recommended_offer_id"] == binding.OFFER_A_ID
    with pytest.raises(TypeError):
        rebuilt.causal_report.proposer_payload["recommended_offer_id"] = binding.OFFER_B_ID
    with pytest.raises(TypeError):
        rebuilt.corridor_report.counter_table["corridor_run_count"] = 2
    with pytest.raises(TypeError):
        rebuilt.corridor_report.artifact_validation_summary["extra"] = True


def test_proposer_request_nested_mappings_are_deeply_immutable() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    request = source_bundle.causal_report.proposer_request
    hard_constraints = {"max_amount": 1200, "nested": {"currency": "USD"}}
    soft_preferences = {"seat": "window", "nested": {"changeable": True}}
    projection = ({"offer_id": binding.OFFER_A_ID, "nested": {"amount": 1000}},)
    rebuilt = replace(
        source_bundle,
        causal_report=replace(
            source_bundle.causal_report,
            proposer_request=replace(
                request,
                client_hard_constraints=hard_constraints,
                client_soft_preferences=soft_preferences,
                authoritative_candidate_projection=projection,
            ),
        ),
    )
    hard_constraints["max_amount"] = 99
    hard_constraints["nested"]["currency"] = "BAD"
    soft_preferences["seat"] = "aisle"
    projection[0]["offer_id"] = binding.OFFER_B_ID
    assert rebuilt.causal_report.proposer_request.client_hard_constraints["max_amount"] == 1200
    assert (
        rebuilt.causal_report.proposer_request.client_hard_constraints["nested"][
            "currency"
        ]
        == "USD"
    )
    assert rebuilt.causal_report.proposer_request.client_soft_preferences["seat"] == "window"
    assert (
        rebuilt.causal_report.proposer_request.authoritative_candidate_projection[0][
            "offer_id"
        ]
        == binding.OFFER_A_ID
    )
    with pytest.raises(TypeError):
        rebuilt.causal_report.proposer_request.client_hard_constraints["max_amount"] = 1
    with pytest.raises(TypeError):
        rebuilt.causal_report.proposer_request.client_hard_constraints["nested"][
            "currency"
        ] = "BAD"
    with pytest.raises(TypeError):
        rebuilt.causal_report.proposer_request.authoritative_candidate_projection[0][
            "offer_id"
        ] = binding.OFFER_B_ID


def test_reviewer_request_nested_mappings_are_deeply_immutable() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    requests = list(source_bundle.causal_report.reviewer_request_records)
    hard_constraints = {"max_amount": 1200, "nested": {"currency": "USD"}}
    soft_preferences = {"seat": "window", "nested": {"changeable": True}}
    projection = ({"offer_id": binding.OFFER_A_ID, "nested": {"amount": 1000}},)
    requests[0] = replace(
        requests[0],
        client_hard_constraints=hard_constraints,
        client_soft_preferences=soft_preferences,
        authoritative_candidate_projection=projection,
    )
    rebuilt = replace(
        source_bundle,
        causal_report=replace(
            source_bundle.causal_report,
            reviewer_request_records=tuple(requests),
        ),
    )
    hard_constraints["nested"]["currency"] = "BAD"
    soft_preferences["seat"] = "aisle"
    projection[0]["offer_id"] = binding.OFFER_B_ID
    stored = rebuilt.causal_report.reviewer_request_records[0]
    assert stored.client_hard_constraints["nested"]["currency"] == "USD"
    assert stored.client_soft_preferences["seat"] == "window"
    assert stored.authoritative_candidate_projection[0]["offer_id"] == binding.OFFER_A_ID
    with pytest.raises(TypeError):
        stored.client_soft_preferences["seat"] = "aisle"
    with pytest.raises(TypeError):
        stored.authoritative_candidate_projection[0]["offer_id"] = binding.OFFER_B_ID


def test_malformed_request_mapping_shapes_fail_closed_without_repair() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    bad = replace(
        source_bundle,
        causal_report=replace(
            source_bundle.causal_report,
            proposer_request=replace(
                source_bundle.causal_report.proposer_request,
                client_hard_constraints=["not", "mapping"],
            ),
        ),
    )
    _assert_source_fails(bad, collector.REASON_SOURCE_CAUSAL_REPORT_INVALID)


def test_direct_probe_wrong_independent_source_ref_fails_closed() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    item = _assert_collected_pass(source_bundle)
    wrong_identity = replace(
        _expected_identity(source_bundle),
        expected_source_refs=replace(
            source_bundle.expected_source_refs,
            source_run_ref="source_run:wrong",
        ),
    )
    report = ledger.validate_airline_transaction_artifact_ledger_v01(
        item,
        expected_identity=wrong_identity,
    )
    assert report.validation_status == ledger.STATUS_FAIL_CLOSED
    assert ledger.REASON_SOURCE_REF_MISMATCH in report.validation_errors


@pytest.mark.parametrize("offer_id", (binding.OFFER_A_ID, binding.OFFER_B_ID))
def test_public_expected_identity_builder_matches_fixture_source(
    offer_id: str,
) -> None:
    source_bundle = _source_bundle(offer_id)
    identity = (
        collector
        .build_airline_transaction_artifact_ledger_expected_identity_from_source_v01(
            source_bundle=source_bundle,
        )
    )
    item = _assert_collected_pass(source_bundle)
    validation = ledger.validate_airline_transaction_artifact_ledger_v01(
        item,
        expected_identity=identity,
    )
    assert identity == _expected_identity(source_bundle)
    assert validation.validation_status == ledger.STATUS_PASS
    assert validation.validation_errors == ()


def test_public_expected_identity_preserves_semantic_causal_hold_lineage() -> None:
    source_bundle = _source_bundle_from_public_causal_runtime(binding.OFFER_A_ID)
    identity = (
        collector
        .build_airline_transaction_artifact_ledger_expected_identity_from_source_v01(
            source_bundle=source_bundle,
        )
    )
    item = _assert_collected_pass(source_bundle)
    hold = next(
        entry
        for entry in item.entries
        if entry.artifact_type == ledger.ARTIFACT_AIRLINE_HOLD_PACKET
    )
    assert hold.artifact_id.startswith("airline_hold_commit_packet:semantic_causal:")
    assert hold.canonical_hash_input["hold_id"].startswith("hold:semantic_causal:")
    assert (
        ledger.validate_airline_transaction_artifact_ledger_v01(
            item,
            expected_identity=identity,
        ).validation_status
        == ledger.STATUS_PASS
    )


def test_public_expected_identity_builder_rejects_wrong_or_invalid_source() -> None:
    with pytest.raises(ValueError, match=f"^{collector.REASON_SOURCE_BUNDLE_WRONG_TYPE}$"):
        collector.build_airline_transaction_artifact_ledger_expected_identity_from_source_v01(
            source_bundle=object(),
        )
    invalid = replace(_source_bundle(binding.OFFER_A_ID), transaction_id="foreign")
    with pytest.raises(ValueError) as exc_info:
        collector.build_airline_transaction_artifact_ledger_expected_identity_from_source_v01(
            source_bundle=invalid,
        )
    assert str(exc_info.value) == collector.REASON_SOURCE_BSEP_LINEAGE_MISMATCH


def test_public_expected_identity_builder_is_deterministic_and_immutable() -> None:
    source_bundle = _source_bundle(binding.OFFER_A_ID)
    first = (
        collector
        .build_airline_transaction_artifact_ledger_expected_identity_from_source_v01(
            source_bundle=source_bundle,
        )
    )
    second = (
        collector
        .build_airline_transaction_artifact_ledger_expected_identity_from_source_v01(
            source_bundle=source_bundle,
        )
    )
    assert first == second
    with pytest.raises(AttributeError):
        first.expected_source_refs = replace(  # type: ignore[misc]
            first.expected_source_refs,
            source_run_ref="foreign",
        )
    artifact_type = ledger.EXPECTED_ARTIFACT_TYPE_SEQUENCE[0]
    with pytest.raises(TypeError):
        first.expected_artifact_ids[artifact_type] = "foreign"


def test_public_expected_identity_builder_signature_accepts_source_not_ledger() -> None:
    signature = inspect.signature(
        collector
        .build_airline_transaction_artifact_ledger_expected_identity_from_source_v01,
    )
    assert tuple(signature.parameters) == ("source_bundle",)
    assert signature.parameters["source_bundle"].kind is inspect.Parameter.KEYWORD_ONLY
    assert "ledger_item" not in signature.parameters
