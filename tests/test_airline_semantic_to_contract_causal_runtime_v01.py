from __future__ import annotations

import ast
import inspect
from dataclasses import replace
from pathlib import Path
from typing import Any, Mapping

from hedgehog.domains.airline import (
    semantic_to_contract_binding_v01 as binding,
)
from hedgehog.domains.airline import (
    semantic_to_contract_causal_runtime_v01 as runtime,
)
from hedgehog.domains.airline import (
    ticket_purchase_corridor_v01 as corridor_contracts,
)


def _proposal_payload(
    request: Mapping[str, Any],
    offer_id: str,
    *,
    overrides: Mapping[str, Any] | None = None,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "proposal_id": f"semantic_offer_selection_proposal:{offer_id}",
        "transaction_id": request["transaction_id"],
        "actor_id": request["actor_id"],
        "source_selection_input_id": request["source_selection_input_id"],
        "source_bsep_projection_ref": request["source_bsep_projection_ref"],
        "source_client_constraint_set_id": request["source_client_constraint_set_id"],
        "source_candidate_set_snapshot_id": (
            request["source_candidate_set_snapshot_id"]
        ),
        "source_candidate_set_digest": request["source_candidate_set_digest"],
        "candidate_set_ref": request["source_candidate_set_ref"],
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
    if overrides:
        payload.update(overrides)
    if extra:
        payload.update(extra)
    return payload


def _reviewer_payload(
    request: Mapping[str, Any],
    *,
    reviewed_offer_id: str | None = None,
    overrides: Mapping[str, Any] | None = None,
    extra: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    offer_id = reviewed_offer_id or request["proposed_offer_id"]
    payload: dict[str, Any] = {
        "response_id": f"canonical_actor_output:{request['actor_id']}:{offer_id}",
        "transaction_id": request["transaction_id"],
        "actor_id": request["actor_id"],
        "source_request_id": request["request_id"],
        "source_selection_input_id": request["source_selection_input_id"],
        "source_candidate_set_snapshot_id": (
            request["source_candidate_set_snapshot_id"]
        ),
        "source_candidate_set_digest": request["source_candidate_set_digest"],
        "reviewed_offer_id": offer_id,
        "review_role": request["actor_role"],
        "review_status": binding.STATUS_PASS,
        "semantic_factors": (f"{request['actor_role']}:supports_offer",),
        "blocking_conflicts": (),
        "supports_proposed_offer": True,
        "validation_status": binding.STATUS_PASS,
        "raw_output_used": False,
        "authority_created": False,
        "permission_created": False,
        "real_world_effects_count": 0,
    }
    if overrides:
        payload.update(overrides)
    if extra:
        payload.update(extra)
    return payload


def _preference_sensitive_semantic_provider(
    actor_id: str,
    request: Mapping[str, Any],
) -> Mapping[str, Any]:
    if actor_id == binding.ACTOR_CLIENT_PURCHASE_INTENT_REVIEWER:
        soft_priority = tuple(
            request["client_soft_preferences"]["soft_preference_priority"],
        )
        seat = tuple(
            request["client_soft_preferences"]["preferred_seat_characteristics"],
        )
        if "extra_legroom_aisle" in soft_priority or "extra_legroom" in seat:
            return _proposal_payload(request, binding.OFFER_B_ID)
        return _proposal_payload(request, binding.OFFER_A_ID)
    return _reviewer_payload(request)


def _always_a_provider(
    actor_id: str,
    request: Mapping[str, Any],
) -> Mapping[str, Any]:
    if actor_id == binding.ACTOR_CLIENT_PURCHASE_INTENT_REVIEWER:
        return _proposal_payload(request, binding.OFFER_A_ID)
    return _reviewer_payload(request)


def _unknown_offer_provider(
    actor_id: str,
    request: Mapping[str, Any],
) -> Mapping[str, Any]:
    if actor_id == binding.ACTOR_CLIENT_PURCHASE_INTENT_REVIEWER:
        return _proposal_payload(request, "offer:unknown")
    return _reviewer_payload(request)


def _hard_invalid_c_provider(
    actor_id: str,
    request: Mapping[str, Any],
) -> Mapping[str, Any]:
    if actor_id == binding.ACTOR_CLIENT_PURCHASE_INTENT_REVIEWER:
        return _proposal_payload(request, binding.OFFER_C_ID)
    return _reviewer_payload(request)


def _authoritative_field_injection_provider(
    actor_id: str,
    request: Mapping[str, Any],
) -> Mapping[str, Any]:
    if actor_id == binding.ACTOR_CLIENT_PURCHASE_INTENT_REVIEWER:
        return _proposal_payload(
            request,
            binding.OFFER_A_ID,
            extra={"amount": 1},
        )
    return _reviewer_payload(request)


def _malformed_provider(
    actor_id: str,
    request: Mapping[str, Any],
) -> Mapping[str, Any]:
    return []  # type: ignore[return-value]


def _reviewer_conflict_provider(
    actor_id: str,
    request: Mapping[str, Any],
) -> Mapping[str, Any]:
    if actor_id == binding.ACTOR_CLIENT_PURCHASE_INTENT_REVIEWER:
        return _proposal_payload(request, binding.OFFER_A_ID)
    return _reviewer_payload(
        request,
        overrides={
            "blocking_conflicts": ("reviewer_conflict",),
            "supports_proposed_offer": False,
        },
    )


def _reviewer_wrong_offer_provider(
    actor_id: str,
    request: Mapping[str, Any],
) -> Mapping[str, Any]:
    if actor_id == binding.ACTOR_CLIENT_PURCHASE_INTENT_REVIEWER:
        return _proposal_payload(request, binding.OFFER_A_ID)
    return _reviewer_payload(request, reviewed_offer_id=binding.OFFER_B_ID)


def _reviewer_authority_claim_provider(
    actor_id: str,
    request: Mapping[str, Any],
) -> Mapping[str, Any]:
    if actor_id == binding.ACTOR_CLIENT_PURCHASE_INTENT_REVIEWER:
        return _proposal_payload(request, binding.OFFER_A_ID)
    return _reviewer_payload(request, overrides={"authority_created": True})


def _missing_reviewer_output_provider(
    actor_id: str,
    request: Mapping[str, Any],
) -> Mapping[str, Any]:
    if actor_id == binding.ACTOR_CLIENT_PURCHASE_INTENT_REVIEWER:
        return _proposal_payload(request, binding.OFFER_A_ID)
    payload = _reviewer_payload(request)
    payload.pop("response_id")
    return payload


def _provider_failure_after_proposer(
    actor_id: str,
    request: Mapping[str, Any],
) -> Mapping[str, Any]:
    if actor_id == binding.ACTOR_CLIENT_PURCHASE_INTENT_REVIEWER:
        return _proposal_payload(request, binding.OFFER_A_ID)
    raise RuntimeError("injected failure")


def _provider_failure_at_proposer(
    actor_id: str,
    request: Mapping[str, Any],
) -> Mapping[str, Any]:
    raise RuntimeError("injected proposer failure")


def _request_id_sensitive_provider(
    actor_id: str,
    request: Mapping[str, Any],
) -> Mapping[str, Any]:
    if actor_id == binding.ACTOR_CLIENT_PURCHASE_INTENT_REVIEWER:
        offer_id = (
            binding.OFFER_B_ID
            if "preference_b" in request["request_id"]
            else binding.OFFER_A_ID
        )
        return _proposal_payload(request, offer_id)
    return _reviewer_payload(request)


def _constraint_id_sensitive_provider(
    actor_id: str,
    request: Mapping[str, Any],
) -> Mapping[str, Any]:
    if actor_id == binding.ACTOR_CLIENT_PURCHASE_INTENT_REVIEWER:
        constraint_id = request["source_client_constraint_set_id"]
        offer_id = (
            binding.OFFER_A_ID
            if constraint_id == runtime.CAUSAL_PROBE_CONSTRAINT_ID_X
            or constraint_id.endswith(":001")
            or "preference_a" in constraint_id
            else binding.OFFER_B_ID
        )
        return _proposal_payload(request, offer_id)
    return _reviewer_payload(request)


def _exact_probe_id_sensitive_provider(
    actor_id: str,
    request: Mapping[str, Any],
) -> Mapping[str, Any]:
    if actor_id == binding.ACTOR_CLIENT_PURCHASE_INTENT_REVIEWER:
        constraint_id = request["source_client_constraint_set_id"]
        if constraint_id == runtime.CAUSAL_PROBE_CONSTRAINT_ID_X:
            return _proposal_payload(request, binding.OFFER_A_ID)
        if constraint_id == runtime.CAUSAL_PROBE_CONSTRAINT_ID_Y:
            return _proposal_payload(request, binding.OFFER_B_ID)
        return _preference_sensitive_semantic_provider(actor_id, request)
    return _reviewer_payload(request)


def _wrong_selection_input_lineage_provider(
    actor_id: str,
    request: Mapping[str, Any],
) -> Mapping[str, Any]:
    if actor_id == binding.ACTOR_CLIENT_PURCHASE_INTENT_REVIEWER:
        return _proposal_payload(
            request,
            binding.OFFER_A_ID,
            overrides={"source_selection_input_id": "selection_input:wrong"},
        )
    return _reviewer_payload(request)


def _wrong_candidate_set_ref_provider(
    actor_id: str,
    request: Mapping[str, Any],
) -> Mapping[str, Any]:
    if actor_id == binding.ACTOR_CLIENT_PURCHASE_INTENT_REVIEWER:
        return _proposal_payload(
            request,
            binding.OFFER_A_ID,
            overrides={"candidate_set_ref": "candidate_set:wrong"},
        )
    return _reviewer_payload(request)


def _proposal_with_empty_id_provider(
    actor_id: str,
    request: Mapping[str, Any],
) -> Mapping[str, Any]:
    if actor_id == binding.ACTOR_CLIENT_PURCHASE_INTENT_REVIEWER:
        return _proposal_payload(
            request,
            binding.OFFER_A_ID,
            overrides={"proposal_id": ""},
        )
    return _reviewer_payload(request)


def _run_a() -> runtime.AirlineSemanticCausalRunReportV01:
    return runtime.collect_airline_semantic_to_contract_causal_run_v01(
        scenario_id="preference_a",
        constraints=binding.build_client_constraints_preference_a_v01(),
        semantic_provider=_preference_sensitive_semantic_provider,
    )


def _run_b() -> runtime.AirlineSemanticCausalRunReportV01:
    return runtime.collect_airline_semantic_to_contract_causal_run_v01(
        scenario_id="preference_b",
        constraints=binding.build_client_constraints_preference_b_v01(),
        semantic_provider=_preference_sensitive_semantic_provider,
    )


def _pair() -> runtime.AirlineSemanticCounterfactualPairReportV01:
    return runtime.collect_airline_semantic_counterfactual_pair_v01(
        semantic_provider=_preference_sensitive_semantic_provider,
    )


def _with_constraint_id(
    constraints: binding.ClientRootTravelConstraintSetV01,
    constraint_set_id: str,
) -> binding.ClientRootTravelConstraintSetV01:
    return replace(constraints, constraint_set_id=constraint_set_id)


def _run_with_constraints(
    constraints: binding.ClientRootTravelConstraintSetV01,
    scenario_id: str,
    provider: runtime.AirlineInjectedSemanticProviderV01 = (
        _preference_sensitive_semantic_provider
    ),
) -> runtime.AirlineSemanticCausalRunReportV01:
    return runtime.collect_airline_semantic_to_contract_causal_run_v01(
        scenario_id=scenario_id,
        constraints=constraints,
        semantic_provider=provider,
    )


def test_preference_a_semantics_produces_offer_a_contract() -> None:
    report = _run_a()

    assert report.final_status == binding.STATUS_LOCAL_MODEL_PASS
    assert report.semantic_recommendation_id == binding.OFFER_A_ID
    assert report.root_selected_offer_id == binding.OFFER_A_ID
    assert report.hold_contract_offer_id == binding.OFFER_A_ID


def test_preference_b_semantics_produces_offer_b_contract() -> None:
    report = _run_b()

    assert report.final_status == binding.STATUS_LOCAL_MODEL_PASS
    assert report.semantic_recommendation_id == binding.OFFER_B_ID
    assert report.root_selected_offer_id == binding.OFFER_B_ID
    assert report.hold_contract_offer_id == binding.OFFER_B_ID


def test_same_candidate_snapshot_used_for_a_and_b() -> None:
    pair = _pair()

    assert pair.final_status == binding.STATUS_LOCAL_MODEL_PASS
    assert pair.same_candidate_snapshot_id is True
    assert pair.same_candidate_snapshot_digest is True


def test_hard_constraints_identical_for_a_and_b() -> None:
    assert _pair().hard_constraints_identical is True


def test_only_soft_preferences_change_between_a_and_b() -> None:
    assert _pair().soft_preferences_different is True


def test_semantic_recommendation_changes_a_to_b() -> None:
    pair = _pair()

    assert pair.semantic_recommendations_different is True
    assert pair.scenario_a_recommendation == binding.OFFER_A_ID
    assert pair.scenario_b_recommendation == binding.OFFER_B_ID


def test_clientroot_selected_offer_changes_a_to_b() -> None:
    assert _pair().root_selected_offers_different is True


def test_hold_contract_changes_a_to_b() -> None:
    pair = _pair()

    assert pair.hold_contract_offers_different is True
    assert pair.scenario_a_hold_offer == binding.OFFER_A_ID
    assert pair.scenario_b_hold_offer == binding.OFFER_B_ID


def test_fixed_safety_invariants_do_not_change() -> None:
    assert _pair().fixed_safety_invariants_identical is True


def test_main_pair_and_identity_control_use_exact_same_probe_ids() -> None:
    pair = _pair()

    assert pair.scenario_a.proposer_request.source_client_constraint_set_id == (
        runtime.CAUSAL_PROBE_CONSTRAINT_ID_X
    )
    assert pair.scenario_b.proposer_request.source_client_constraint_set_id == (
        runtime.CAUSAL_PROBE_CONSTRAINT_ID_Y
    )
    identity = pair.identity_invariance_report
    assert identity.probe_constraint_id_x == runtime.CAUSAL_PROBE_CONSTRAINT_ID_X
    assert identity.probe_constraint_id_y == runtime.CAUSAL_PROBE_CONSTRAINT_ID_Y
    assert identity.preference_a_first.proposer_request.source_client_constraint_set_id == (
        runtime.CAUSAL_PROBE_CONSTRAINT_ID_X
    )
    assert identity.preference_a_second.proposer_request.source_client_constraint_set_id == (
        runtime.CAUSAL_PROBE_CONSTRAINT_ID_Y
    )
    assert identity.preference_b_first.proposer_request.source_client_constraint_set_id == (
        runtime.CAUSAL_PROBE_CONSTRAINT_ID_X
    )
    assert identity.preference_b_second.proposer_request.source_client_constraint_set_id == (
        runtime.CAUSAL_PROBE_CONSTRAINT_ID_Y
    )


def test_provider_request_ids_contain_no_scenario_answer_labels() -> None:
    pair = _pair()
    request_ids = (
        (pair.scenario_a.proposer_request.request_id,)
        + tuple(request.request_id for request in pair.scenario_a.reviewer_request_records)
        + (pair.scenario_b.proposer_request.request_id,)
        + tuple(request.request_id for request in pair.scenario_b.reviewer_request_records)
    )
    constraint_ids = (
        (pair.scenario_a.proposer_request.source_client_constraint_set_id,)
        + tuple(
            request.source_client_constraint_set_id
            for request in pair.scenario_a.reviewer_request_records
        )
        + (pair.scenario_b.proposer_request.source_client_constraint_set_id,)
        + tuple(
            request.source_client_constraint_set_id
            for request in pair.scenario_b.reviewer_request_records
        )
    )

    visible_ids = request_ids + constraint_ids
    assert all("preference_a" not in value for value in visible_ids)
    assert all("preference_b" not in value for value in visible_ids)
    assert all("scenario_a" not in value for value in visible_ids)
    assert all("scenario_b" not in value for value in visible_ids)


def test_changing_scenario_id_alone_does_not_change_recommendation() -> None:
    constraints = binding.build_client_constraints_preference_a_v01()
    first = _run_with_constraints(constraints, "opaque_scenario_one")
    second = _run_with_constraints(constraints, "opaque_scenario_two")

    assert first.semantic_recommendation_id == second.semantic_recommendation_id
    assert first.root_selected_offer_id == second.root_selected_offer_id
    assert first.hold_contract_offer_id == second.hold_contract_offer_id


def test_request_id_sensitive_provider_fails_causal_proof() -> None:
    pair = runtime.collect_airline_semantic_counterfactual_pair_v01(
        semantic_provider=_request_id_sensitive_provider,
    )

    assert pair.final_status == binding.STATUS_FAIL_CLOSED
    assert runtime.REASON_SEMANTIC_CHANGE_DID_NOT_PROPAGATE_TO_CONTRACT in (
        pair.validation_errors
    )


def test_identity_invariance_control_passes_for_content_sensitive_provider() -> None:
    report = runtime.collect_airline_semantic_identity_invariance_control_v01(
        semantic_provider=_preference_sensitive_semantic_provider,
    )

    assert report.final_status == binding.STATUS_LOCAL_MODEL_PASS
    assert report.provider_identity_invariant is True
    assert report.a_recommendations_identical is True
    assert report.b_recommendations_identical is True


def test_constraint_id_sensitive_provider_fails_counterfactual_pair() -> None:
    pair = runtime.collect_airline_semantic_counterfactual_pair_v01(
        semantic_provider=_constraint_id_sensitive_provider,
    )

    assert pair.final_status == binding.STATUS_FAIL_CLOSED
    assert pair.identity_invariance_passed is False
    assert pair.provider_identity_sensitive_detected is True
    assert runtime.REASON_PROVIDER_IDENTITY_INVARIANCE_FAILED in (
        pair.validation_errors
    )


def test_exact_pair_probe_id_sensitive_provider_fails_counterfactual_pair() -> None:
    pair = runtime.collect_airline_semantic_counterfactual_pair_v01(
        semantic_provider=_exact_probe_id_sensitive_provider,
    )

    assert pair.final_status == binding.STATUS_FAIL_CLOSED
    assert pair.identity_invariance_passed is False
    assert pair.provider_identity_sensitive_detected is True
    assert runtime.REASON_PROVIDER_IDENTITY_INVARIANCE_FAILED in (
        pair.validation_errors
    )


def test_constraint_id_sensitive_provider_fails_identity_invariance_proof() -> None:
    content_a = binding.build_client_constraints_preference_a_v01()
    first = _run_with_constraints(
        _with_constraint_id(content_a, "client_constraints:identity:001"),
        "same_content_first",
        _constraint_id_sensitive_provider,
    )
    second = _run_with_constraints(
        _with_constraint_id(content_a, "client_constraints:identity:002"),
        "same_content_second",
        _constraint_id_sensitive_provider,
    )

    assert first.semantic_recommendation_id != second.semantic_recommendation_id


def test_same_preference_a_content_under_different_opaque_ids_recommends_a() -> None:
    content_a = binding.build_client_constraints_preference_a_v01()
    first = _run_with_constraints(
        _with_constraint_id(content_a, "client_constraints:opaque:x1"),
        "same_a_first",
    )
    second = _run_with_constraints(
        _with_constraint_id(content_a, "client_constraints:opaque:x2"),
        "same_a_second",
    )

    assert first.semantic_recommendation_id == binding.OFFER_A_ID
    assert second.semantic_recommendation_id == binding.OFFER_A_ID


def test_same_preference_b_content_under_different_opaque_ids_recommends_b() -> None:
    content_b = binding.build_client_constraints_preference_b_v01()
    first = _run_with_constraints(
        _with_constraint_id(content_b, "client_constraints:opaque:y1"),
        "same_b_first",
    )
    second = _run_with_constraints(
        _with_constraint_id(content_b, "client_constraints:opaque:y2"),
        "same_b_second",
    )

    assert first.semantic_recommendation_id == binding.OFFER_B_ID
    assert second.semantic_recommendation_id == binding.OFFER_B_ID


def test_swapped_opaque_constraint_ids_do_not_change_content_recommendation() -> None:
    content_a = _with_constraint_id(
        binding.build_client_constraints_preference_a_v01(),
        "client_constraints:opaque:shared_b",
    )
    content_b = _with_constraint_id(
        binding.build_client_constraints_preference_b_v01(),
        "client_constraints:opaque:shared_a",
    )

    assert _run_with_constraints(content_a, "swapped_a").semantic_recommendation_id == (
        binding.OFFER_A_ID
    )
    assert _run_with_constraints(content_b, "swapped_b").semantic_recommendation_id == (
        binding.OFFER_B_ID
    )


def test_wrong_request_selection_input_id_rejected() -> None:
    report = _run_with_constraints(
        binding.build_client_constraints_preference_a_v01(),
        "wrong_selection_lineage",
        _wrong_selection_input_lineage_provider,
    )

    assert report.final_status == binding.STATUS_FAIL_CLOSED
    assert binding.REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH in (
        report.validation_errors
    )


def test_wrong_request_candidate_set_ref_rejected() -> None:
    report = _run_with_constraints(
        binding.build_client_constraints_preference_a_v01(),
        "wrong_candidate_ref",
        _wrong_candidate_set_ref_provider,
    )

    assert report.final_status == binding.STATUS_FAIL_CLOSED
    assert binding.REASON_SELECTION_INPUT_SNAPSHOT_MISMATCH in (
        report.validation_errors
    )


def test_provider_payload_builders_use_request_lineage_only() -> None:
    report = _run_a()
    assert report.proposer_request is not None
    assert report.proposal is not None

    assert report.proposal.source_selection_input_id == (
        report.proposer_request.source_selection_input_id
    )
    assert report.proposal.candidate_set_ref == (
        report.proposer_request.source_candidate_set_ref
    )
    assert "SELECTION_INPUT_ID" not in globals()
    assert "CANDIDATE_SET_REF" not in inspect.getsource(_proposal_payload)


def test_exact_five_semantic_actor_calls_per_run() -> None:
    report = _run_a()

    assert report.provider_call_count == 5, "exact five semantic actor calls"
    assert len(report.provider_call_records) == 5


def test_exact_actor_call_order() -> None:
    report = _run_a()

    assert tuple(record.actor_id for record in report.provider_call_records) == (
        runtime.ACTOR_ORDER
    )


def test_proposer_review_is_derived_from_actual_proposal() -> None:
    report = _run_a()
    assert report.proposal is not None

    proposer_review = report.actor_reviews[0]
    assert proposer_review.actor_id == report.proposal.actor_id
    assert proposer_review.reviewed_offer_id == report.proposal.recommended_offer_id
    assert report.proposal.proposal_id in proposer_review.canonical_actor_output_id


def test_all_reviewer_request_records_receive_validated_proposed_offer() -> None:
    report = _run_b()

    assert report.proposal is not None
    assert {
        request.proposed_offer_id for request in report.reviewer_request_records
    } == {report.proposal.recommended_offer_id}


def test_full_a_local_chain_passes() -> None:
    report = _run_a()

    assert report.local_chain_validation is not None
    assert report.local_chain_validation.validation_status == (
        binding.STATUS_LOCAL_MODEL_PASS
    )
    assert runtime.validate_airline_semantic_causal_run_report_v01(report) == (
        True,
        (),
    )


def test_full_b_local_chain_passes() -> None:
    report = _run_b()

    assert report.local_chain_validation is not None
    assert report.local_chain_validation.validation_status == (
        binding.STATUS_LOCAL_MODEL_PASS
    )
    assert runtime.validate_airline_semantic_causal_run_report_v01(report) == (
        True,
        (),
    )


def test_always_a_provider_fails_counterfactual_pair() -> None:
    pair = runtime.collect_airline_semantic_counterfactual_pair_v01(
        semantic_provider=_always_a_provider,
    )

    assert pair.final_status == binding.STATUS_FAIL_CLOSED
    assert runtime.REASON_SEMANTIC_CHANGE_DID_NOT_PROPAGATE_TO_CONTRACT in (
        pair.validation_errors
    )


def test_changed_semantics_but_unchanged_root_decision_fails() -> None:
    pair = _pair()
    tampered = replace(
        pair,
        root_selected_offers_different=False,
        semantic_change_propagated_to_contract=False,
    )

    accepted, reasons = runtime.validate_airline_semantic_counterfactual_pair_v01(
        tampered,
    )

    assert accepted is False
    assert runtime.REASON_CAUSAL_RUN_DERIVED_FIELD_MISMATCH in reasons


def test_changed_root_decision_but_unchanged_hold_contract_fails() -> None:
    pair = _pair()
    tampered = replace(
        pair,
        hold_contract_offers_different=False,
        semantic_change_propagated_to_contract=False,
    )

    accepted, reasons = runtime.validate_airline_semantic_counterfactual_pair_v01(
        tampered,
    )

    assert accepted is False
    assert runtime.REASON_CAUSAL_RUN_DERIVED_FIELD_MISMATCH in reasons


def test_single_run_validator_rejects_lied_derived_recommendation() -> None:
    report = _run_a()
    tampered = replace(report, semantic_recommendation_id=binding.OFFER_B_ID)

    accepted, reasons = runtime.validate_airline_semantic_causal_run_report_v01(
        tampered,
    )

    assert accepted is False
    assert runtime.REASON_CAUSAL_RUN_DERIVED_FIELD_MISMATCH in reasons


def test_single_run_validator_rejects_lied_provider_call_count() -> None:
    report = _run_a()
    tampered = replace(report, provider_call_count=99)

    accepted, reasons = runtime.validate_airline_semantic_causal_run_report_v01(
        tampered,
    )

    assert accepted is False
    assert runtime.REASON_CAUSAL_RUN_PROVIDER_CALL_SHAPE_MISMATCH in reasons


def test_single_run_fail_closed_rejects_downstream_artifact_after_failure() -> None:
    failed = runtime.collect_airline_semantic_to_contract_causal_run_v01(
        scenario_id="unknown_offer",
        constraints=binding.build_client_constraints_preference_a_v01(),
        semantic_provider=_unknown_offer_provider,
    )
    valid = _run_a()
    tampered = replace(failed, hold_packet=valid.hold_packet)

    accepted, reasons = runtime.validate_airline_semantic_causal_run_report_v01(
        tampered,
    )

    assert accepted is False
    assert runtime.REASON_CAUSAL_RUN_DOWNSTREAM_ARTIFACT_AFTER_FAILURE in reasons


def test_soft_preference_request_tamper_with_old_fingerprint_rejected() -> None:
    report = _run_a()
    assert report.proposer_request is not None
    tampered_request = replace(
        report.proposer_request,
        client_soft_preferences={
            **dict(report.proposer_request.client_soft_preferences),
            "soft_preference_priority": ("tampered_soft_preference",),
        },
    )
    tampered = replace(report, proposer_request=tampered_request)

    accepted, reasons = runtime.validate_airline_semantic_causal_run_report_v01(
        tampered,
    )

    assert accepted is False
    assert runtime.REASON_CAUSAL_RUN_SOFT_PREFERENCE_FINGERPRINT_MISMATCH in (
        reasons
    )


def test_hard_constraint_request_tamper_with_old_fingerprint_rejected() -> None:
    report = _run_a()
    assert report.proposer_request is not None
    tampered_request = replace(
        report.proposer_request,
        client_hard_constraints={
            **dict(report.proposer_request.client_hard_constraints),
            "max_amount": 1,
        },
    )
    tampered = replace(report, proposer_request=tampered_request)

    accepted, reasons = runtime.validate_airline_semantic_causal_run_report_v01(
        tampered,
    )

    assert accepted is False
    assert runtime.REASON_CAUSAL_RUN_HARD_CONSTRAINT_FINGERPRINT_MISMATCH in (
        reasons
    )


def test_pair_identical_soft_content_with_lied_different_fingerprints_rejected() -> None:
    pair = _pair()
    assert pair.scenario_b.proposer_request is not None
    tampered_request = replace(
        pair.scenario_b.proposer_request,
        client_soft_preferences=pair.scenario_a.proposer_request.client_soft_preferences,
    )
    tampered_b = replace(pair.scenario_b, proposer_request=tampered_request)
    tampered_pair = replace(pair, scenario_b=tampered_b)

    accepted, reasons = runtime.validate_airline_semantic_counterfactual_pair_v01(
        tampered_pair,
    )

    assert accepted is False
    assert runtime.REASON_CAUSAL_RUN_SOFT_PREFERENCE_FINGERPRINT_MISMATCH in (
        reasons
    )


def test_pair_different_hard_content_with_lied_equal_fingerprints_rejected() -> None:
    pair = _pair()
    assert pair.scenario_b.proposer_request is not None
    tampered_request = replace(
        pair.scenario_b.proposer_request,
        client_hard_constraints={
            **dict(pair.scenario_b.proposer_request.client_hard_constraints),
            "max_amount": 999,
        },
    )
    tampered_b = replace(pair.scenario_b, proposer_request=tampered_request)
    tampered_pair = replace(pair, scenario_b=tampered_b)

    accepted, reasons = runtime.validate_airline_semantic_counterfactual_pair_v01(
        tampered_pair,
    )

    assert accepted is False
    assert runtime.REASON_CAUSAL_RUN_HARD_CONSTRAINT_FINGERPRINT_MISMATCH in (
        reasons
    )


def test_tampered_call_record_request_id_rejected() -> None:
    report = _run_a()
    tampered_records = list(report.provider_call_records)
    tampered_records[1] = replace(tampered_records[1], request_id="wrong_request")
    tampered = replace(report, provider_call_records=tuple(tampered_records))

    accepted, reasons = runtime.validate_airline_semantic_causal_run_report_v01(
        tampered,
    )

    assert accepted is False
    assert runtime.REASON_CAUSAL_RUN_CALL_RECORD_REQUEST_MISMATCH in reasons


def test_tampered_reviewer_response_source_request_id_rejected() -> None:
    report = _run_a()
    tampered_responses = list(report.reviewer_responses)
    tampered_responses[0] = replace(
        tampered_responses[0],
        source_request_id="wrong_request",
    )
    tampered = replace(report, reviewer_responses=tuple(tampered_responses))

    accepted, reasons = runtime.validate_airline_semantic_causal_run_report_v01(
        tampered,
    )

    assert accepted is False
    assert runtime.REASON_CAUSAL_RUN_RESPONSE_REQUEST_MISMATCH in reasons


def test_tampered_reviewer_response_actor_id_rejected() -> None:
    report = _run_a()
    tampered_responses = list(report.reviewer_responses)
    tampered_responses[0] = replace(tampered_responses[0], actor_id="wrong_actor")
    tampered = replace(report, reviewer_responses=tuple(tampered_responses))

    accepted, reasons = runtime.validate_airline_semantic_causal_run_report_v01(
        tampered,
    )

    assert accepted is False
    assert runtime.REASON_CAUSAL_RUN_RESPONSE_REQUEST_MISMATCH in reasons


def test_tampered_canonical_review_factors_rejected_even_if_response_valid() -> None:
    report = _run_a()
    tampered_reviews = list(report.actor_reviews)
    tampered_reviews[1] = replace(
        tampered_reviews[1],
        semantic_factors=("tampered_factor",),
    )
    tampered = replace(report, actor_reviews=tuple(tampered_reviews))

    accepted, reasons = runtime.validate_airline_semantic_causal_run_report_v01(
        tampered,
    )

    assert accepted is False
    assert runtime.REASON_CAUSAL_RUN_RESPONSE_REVIEW_MISMATCH in reasons


def test_missing_or_extra_reviewer_request_or_response_rejected() -> None:
    report = _run_a()
    missing_request = replace(
        report,
        reviewer_request_records=report.reviewer_request_records[:-1],
    )
    extra_response = replace(
        report,
        reviewer_responses=report.reviewer_responses
        + (report.reviewer_responses[-1],),
    )

    accepted_missing, reasons_missing = (
        runtime.validate_airline_semantic_causal_run_report_v01(missing_request)
    )
    accepted_extra, reasons_extra = (
        runtime.validate_airline_semantic_causal_run_report_v01(extra_response)
    )

    assert accepted_missing is False
    assert accepted_extra is False
    assert runtime.REASON_CAUSAL_RUN_PROVIDER_CALL_SHAPE_MISMATCH in reasons_missing
    assert runtime.REASON_CAUSAL_RUN_PROVIDER_CALL_SHAPE_MISMATCH in reasons_extra


def test_proposer_call_failure_with_forged_proposal_rejected() -> None:
    failed = runtime.collect_airline_semantic_to_contract_causal_run_v01(
        scenario_id="proposer_call_failure",
        constraints=binding.build_client_constraints_preference_a_v01(),
        semantic_provider=_provider_failure_at_proposer,
    )
    valid = _run_a()
    tampered = replace(failed, proposal=valid.proposal)

    accepted, reasons = runtime.validate_airline_semantic_causal_run_report_v01(
        tampered,
    )

    assert accepted is False
    assert runtime.REASON_CAUSAL_RUN_DOWNSTREAM_ARTIFACT_AFTER_FAILURE in reasons


def test_reviewer_call_failure_with_forged_later_actor_reviews_rejected() -> None:
    failed = runtime.collect_airline_semantic_to_contract_causal_run_v01(
        scenario_id="reviewer_call_failure",
        constraints=binding.build_client_constraints_preference_a_v01(),
        semantic_provider=_provider_failure_after_proposer,
    )
    valid = _run_a()
    tampered = replace(failed, actor_reviews=valid.actor_reviews)

    accepted, reasons = runtime.validate_airline_semantic_causal_run_report_v01(
        tampered,
    )

    assert accepted is False
    assert runtime.REASON_CAUSAL_RUN_DOWNSTREAM_ARTIFACT_AFTER_FAILURE in reasons


def test_nested_scenario_b_root_decision_changed_to_a_rejected() -> None:
    pair = _pair()
    assert pair.scenario_b.client_root_decision is not None
    tampered_decision = replace(
        pair.scenario_b.client_root_decision,
        selected_offer_id=binding.OFFER_A_ID,
    )
    tampered_b = replace(pair.scenario_b, client_root_decision=tampered_decision)
    tampered_pair = replace(pair, scenario_b=tampered_b)

    accepted, reasons = runtime.validate_airline_semantic_counterfactual_pair_v01(
        tampered_pair,
    )

    assert accepted is False
    assert runtime.REASON_CAUSAL_RUN_CHAIN_VALIDATION_FAILED in reasons or (
        runtime.REASON_CAUSAL_RUN_DERIVED_FIELD_MISMATCH in reasons
    )


def test_nested_scenario_b_hold_offer_changed_to_a_rejected() -> None:
    pair = _pair()
    assert pair.scenario_b.hold_packet is not None
    tampered_hold = replace(pair.scenario_b.hold_packet, offer_id=binding.OFFER_A_ID)
    tampered_b = replace(pair.scenario_b, hold_packet=tampered_hold)
    tampered_pair = replace(pair, scenario_b=tampered_b)

    accepted, reasons = runtime.validate_airline_semantic_counterfactual_pair_v01(
        tampered_pair,
    )

    assert accepted is False
    assert runtime.REASON_CAUSAL_RUN_DERIVED_FIELD_MISMATCH in reasons or (
        runtime.REASON_CAUSAL_RUN_CHAIN_VALIDATION_FAILED in reasons
    )


def test_pair_scenario_recommendation_fields_lie_rejected() -> None:
    pair = _pair()
    tampered = replace(pair, scenario_a_recommendation=binding.OFFER_B_ID)

    accepted, reasons = runtime.validate_airline_semantic_counterfactual_pair_v01(
        tampered,
    )

    assert accepted is False
    assert runtime.REASON_CAUSAL_RUN_DERIVED_FIELD_MISMATCH in reasons


def test_pair_provider_call_count_lie_rejected() -> None:
    pair = _pair()
    tampered = replace(pair, provider_call_count=99)

    accepted, reasons = runtime.validate_airline_semantic_counterfactual_pair_v01(
        tampered,
    )

    assert accepted is False
    assert runtime.REASON_CAUSAL_RUN_DERIVED_FIELD_MISMATCH in reasons


def test_pair_snapshot_flags_lie_rejected() -> None:
    pair = _pair()
    tampered = replace(pair, same_candidate_snapshot_id=False)

    accepted, reasons = runtime.validate_airline_semantic_counterfactual_pair_v01(
        tampered,
    )

    assert accepted is False
    assert runtime.REASON_CAUSAL_RUN_DERIVED_FIELD_MISMATCH in reasons


def test_pair_fixed_safety_flag_lie_with_hold_surface_drift_rejected() -> None:
    pair = _pair()
    assert pair.scenario_b.hold_packet is not None
    tampered_hold = replace(
        pair.scenario_b.hold_packet,
        allowed_action="provider_supplied_action",
    )
    tampered_b = replace(pair.scenario_b, hold_packet=tampered_hold)
    tampered_pair = replace(
        pair,
        scenario_b=tampered_b,
        fixed_safety_invariants_identical=True,
    )

    accepted, reasons = runtime.validate_airline_semantic_counterfactual_pair_v01(
        tampered_pair,
    )

    assert accepted is False
    assert runtime.REASON_CAUSAL_RUN_DERIVED_FIELD_MISMATCH in reasons or (
        runtime.REASON_CAUSAL_RUN_CHAIN_VALIDATION_FAILED in reasons
    )


def test_identity_report_with_substitute_probe_namespace_rejected() -> None:
    pair = _pair()
    alternate_identity = runtime.collect_airline_semantic_identity_invariance_control_v01(
        semantic_provider=_preference_sensitive_semantic_provider,
        probe_constraint_id_x="client_constraints:substitute_probe:1111",
        probe_constraint_id_y="client_constraints:substitute_probe:2222",
    )
    assert alternate_identity.final_status == binding.STATUS_LOCAL_MODEL_PASS
    tampered = replace(pair, identity_invariance_report=alternate_identity)

    accepted, reasons = runtime.validate_airline_semantic_counterfactual_pair_v01(
        tampered,
    )

    assert accepted is False
    assert runtime.REASON_PROVIDER_IDENTITY_PROBE_BINDING_MISMATCH in reasons


def test_identity_report_probe_id_field_lie_rejected() -> None:
    pair = _pair()
    tampered_identity = replace(
        pair.identity_invariance_report,
        probe_constraint_id_x="client_constraints:probe_lie:ffff",
    )
    tampered = replace(pair, identity_invariance_report=tampered_identity)

    accepted, reasons = runtime.validate_airline_semantic_counterfactual_pair_v01(
        tampered,
    )

    assert accepted is False
    assert runtime.REASON_PROVIDER_IDENTITY_PROBE_BINDING_MISMATCH in reasons


def test_proposal_but_synthesis_a_fails() -> None:
    report = runtime.collect_airline_semantic_to_contract_causal_run_v01(
        scenario_id="proposal_b_synthesis_a",
        constraints=binding.build_client_constraints_preference_b_v01(),
        semantic_provider=_reviewer_wrong_offer_provider,
    )

    assert report.final_status == binding.STATUS_FAIL_CLOSED
    assert report.hold_packet is None


def test_forged_proposal_identity_fails() -> None:
    report = runtime.collect_airline_semantic_to_contract_causal_run_v01(
        scenario_id="forged_proposal",
        constraints=binding.build_client_constraints_preference_a_v01(),
        semantic_provider=_proposal_with_empty_id_provider,
    )

    assert report.final_status == binding.STATUS_FAIL_CLOSED
    assert binding.REASON_EMPTY_PROVIDER_OUTPUT_FIELD in report.validation_errors


def test_forged_canonical_evidence_lineage_fails() -> None:
    report = _run_a()
    assert report.proposal is not None
    assert report.synthesis is not None
    assert report.canonical_evidence is not None

    forged_evidence = replace(
        report.canonical_evidence,
        source_proposal_id="forged_proposal",
    )
    validation = binding.validate_validated_airline_semantic_selection_evidence_v01(
        binding.build_selection_input_v01(
            binding.build_valid_airline_bsep_projection_ref_v01(),
            binding.build_client_constraints_preference_a_v01(),
            binding.build_airline_candidate_snapshot_v01(),
        ),
        report.proposal,
        report.actor_reviews,
        report.synthesis,
        forged_evidence,
    )

    assert validation.validation_status == binding.STATUS_FAIL_CLOSED
    assert binding.REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH in (
        validation.reason_codes
    )


def test_no_runtime_default_offer() -> None:
    signature = inspect.signature(
        runtime.collect_airline_semantic_to_contract_causal_run_v01,
    )
    source = Path(runtime.__file__).read_text(encoding="utf-8")

    assert "offer_id" not in signature.parameters
    assert "selected_offer_id" not in signature.parameters
    assert "OFFER_A_ID" not in source
    assert "OFFER_B_ID" not in source


def test_no_silent_fallback_after_invalid_provider_output() -> None:
    report = runtime.collect_airline_semantic_to_contract_causal_run_v01(
        scenario_id="unknown_offer",
        constraints=binding.build_client_constraints_preference_a_v01(),
        semantic_provider=_unknown_offer_provider,
    )

    assert report.final_status == binding.STATUS_FAIL_CLOSED
    assert report.provider_call_count == 1
    assert report.silent_fallback_used is False
    assert report.hold_packet is None


def test_unknown_offer_fails_closed_without_hold() -> None:
    report = runtime.collect_airline_semantic_to_contract_causal_run_v01(
        scenario_id="unknown_offer",
        constraints=binding.build_client_constraints_preference_a_v01(),
        semantic_provider=_unknown_offer_provider,
    )

    assert report.final_status == binding.STATUS_FAIL_CLOSED
    assert binding.REASON_UNKNOWN_CANDIDATE_ID in report.validation_errors
    assert report.hold_packet is None


def test_offer_c_fails_clientroot_compatibility_without_hold() -> None:
    report = runtime.collect_airline_semantic_to_contract_causal_run_v01(
        scenario_id="offer_c",
        constraints=binding.build_client_constraints_preference_a_v01(),
        semantic_provider=_hard_invalid_c_provider,
    )

    assert report.final_status == binding.STATUS_FAIL_CLOSED
    assert report.provider_call_count == 5
    assert binding.REASON_CLIENT_CONSTRAINT_COMPATIBILITY_FAILED in (
        report.validation_errors
    )
    assert report.hold_packet is None


def test_authoritative_field_injection_fails_closed() -> None:
    report = runtime.collect_airline_semantic_to_contract_causal_run_v01(
        scenario_id="authoritative_field_injection",
        constraints=binding.build_client_constraints_preference_a_v01(),
        semantic_provider=_authoritative_field_injection_provider,
    )

    assert report.final_status == binding.STATUS_FAIL_CLOSED
    assert binding.REASON_FORBIDDEN_PROVIDER_AUTHORITATIVE_FIELD in (
        report.validation_errors
    )
    assert report.provider_call_count == 1


def test_malformed_provider_output_never_raises() -> None:
    report = runtime.collect_airline_semantic_to_contract_causal_run_v01(
        scenario_id="malformed_provider",
        constraints=binding.build_client_constraints_preference_a_v01(),
        semantic_provider=_malformed_provider,
    )

    assert report.final_status == binding.STATUS_FAIL_CLOSED
    assert binding.REASON_INVALID_PROVIDER_OUTPUT_CONTAINER in (
        report.validation_errors
    )


def test_reviewer_conflict_prevents_synthesis() -> None:
    report = runtime.collect_airline_semantic_to_contract_causal_run_v01(
        scenario_id="reviewer_conflict",
        constraints=binding.build_client_constraints_preference_a_v01(),
        semantic_provider=_reviewer_conflict_provider,
    )

    assert report.final_status == binding.STATUS_FAIL_CLOSED
    assert report.synthesis is None
    assert binding.REASON_MULTI_ACTOR_CONFLICT in report.validation_errors


def test_reviewer_wrong_offer_prevents_synthesis() -> None:
    report = runtime.collect_airline_semantic_to_contract_causal_run_v01(
        scenario_id="reviewer_wrong_offer",
        constraints=binding.build_client_constraints_preference_a_v01(),
        semantic_provider=_reviewer_wrong_offer_provider,
    )

    assert report.final_status == binding.STATUS_FAIL_CLOSED
    assert report.synthesis is None
    assert binding.REASON_MULTI_ACTOR_CONFLICT in report.validation_errors


def test_reviewer_authority_claim_fails_closed() -> None:
    report = runtime.collect_airline_semantic_to_contract_causal_run_v01(
        scenario_id="reviewer_authority",
        constraints=binding.build_client_constraints_preference_a_v01(),
        semantic_provider=_reviewer_authority_claim_provider,
    )

    assert report.final_status == binding.STATUS_FAIL_CLOSED
    assert binding.REASON_PROVIDER_CLAIMED_AUTHORITY in report.validation_errors


def test_missing_reviewer_output_fails_closed() -> None:
    report = runtime.collect_airline_semantic_to_contract_causal_run_v01(
        scenario_id="missing_reviewer",
        constraints=binding.build_client_constraints_preference_a_v01(),
        semantic_provider=_missing_reviewer_output_provider,
    )

    assert report.final_status == binding.STATUS_FAIL_CLOSED
    assert binding.REASON_MISSING_PROVIDER_OUTPUT_FIELD in report.validation_errors


def test_provider_failure_stops_later_calls() -> None:
    report = runtime.collect_airline_semantic_to_contract_causal_run_v01(
        scenario_id="provider_failure",
        constraints=binding.build_client_constraints_preference_a_v01(),
        semantic_provider=_provider_failure_after_proposer,
    )

    assert report.final_status == binding.STATUS_FAIL_CLOSED
    assert report.provider_call_count == 2
    assert runtime.REASON_PROVIDER_CALL_FAILED in report.validation_errors


def test_root_authoritative_facts_come_from_snapshot() -> None:
    report = _run_b()
    assert report.airline_root_resolution is not None

    record = {
        item.offer_id: item
        for item in binding.build_airline_candidate_snapshot_v01().authoritative_offer_records
    }[binding.OFFER_B_ID]
    assert report.airline_root_resolution.resolved_amount == record.amount
    assert report.airline_root_resolution.resolved_currency == record.currency
    assert report.airline_root_resolution.resolved_route_ref == record.route_ref
    assert report.airline_root_resolution.resolved_ttl == record.ttl_seconds


def test_provider_cannot_supply_amount_currency_route_ttl() -> None:
    for forbidden in ("amount", "currency", "route_ref", "ttl_seconds"):
        def provider(
            actor_id: str,
            request: Mapping[str, Any],
            field: str = forbidden,
        ) -> Mapping[str, Any]:
            if actor_id == binding.ACTOR_CLIENT_PURCHASE_INTENT_REVIEWER:
                return _proposal_payload(
                    request,
                    binding.OFFER_A_ID,
                    extra={field: "provider_value"},
                )
            return _reviewer_payload(request)

        report = runtime.collect_airline_semantic_to_contract_causal_run_v01(
            scenario_id=f"provider_injected_{forbidden}",
            constraints=binding.build_client_constraints_preference_a_v01(),
            semantic_provider=provider,
        )
        assert report.final_status == binding.STATUS_FAIL_CLOSED
        assert binding.REASON_FORBIDDEN_PROVIDER_AUTHORITATIVE_FIELD in (
            report.validation_errors
        )


def test_hold_packet_is_airlineroot_created() -> None:
    report = _run_a()
    assert report.hold_packet is not None

    assert report.hold_packet.created_by == binding.AIRLINE_ROOT_ID
    assert report.hold_packet.root_owner == binding.AIRLINE_ROOT_ID
    assert report.hold_packet.allowed_action == corridor_contracts.ACTION_MOCK_OFFER_HOLD
    assert report.hold_packet.real_world_effects_allowed is False


def test_no_runtime_receipt_or_corridor_execution() -> None:
    report = _run_a()

    assert report.runtime_receipt_created_count == 0
    assert report.corridor_execution_count == 0


def test_no_provider_network_gemini_or_real_effects() -> None:
    report = _run_a()

    assert report.provider_network_call_count == 0
    assert report.gemini_call_count == 0
    assert report.real_world_effects_count == 0


def test_runtime_contains_no_preference_to_offer_algorithm() -> None:
    source = Path(runtime.__file__).read_text(encoding="utf-8")

    assert "preference_A" not in source
    assert "preference_B" not in source
    assert "OFFER_A_ID" not in source
    assert "OFFER_B_ID" not in source
    assert "extra_legroom" not in source


def test_runtime_has_no_default_offer_argument() -> None:
    signature = inspect.signature(
        runtime.collect_airline_semantic_to_contract_causal_run_v01,
    )

    assert "recommended_offer_id" not in signature.parameters
    assert "selected_offer_id" not in signature.parameters
    assert "default_offer" not in signature.parameters


def test_runtime_does_not_import_demo_or_provider_adapter() -> None:
    source = Path(runtime.__file__).read_text(encoding="utf-8")

    assert "demo." not in source
    assert "provider_adapter" not in source
    assert "semantic_provider_adapter" not in source


def test_runtime_does_not_import_google_requests_openai_config_subprocess() -> None:
    source = Path(runtime.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.add(node.module)

    assert "requests" not in imported_modules
    assert "urllib" not in imported_modules
    assert "openai" not in imported_modules
    assert "google.genai" not in imported_modules
    assert "subprocess" not in imported_modules
    assert "config" not in imported_modules
    assert all(not module.startswith("demo") for module in imported_modules)
    assert all("provider_adapter" not in module for module in imported_modules)


def test_runtime_has_no_split_literals_or_grep_marker_constants() -> None:
    source = Path(runtime.__file__).read_text(encoding="utf-8")

    assert "__getattr__" not in source
    assert '"reviewer_" + "re" + "quests"' not in source
    assert "EXACT_FIVE_SEMANTIC_ACTOR_PROOF" not in source


def test_runtime_does_not_implement_ledger_crypto_replay() -> None:
    source = Path(runtime.__file__).read_text(encoding="utf-8")

    assert "Ledger implementation" not in source
    assert "Crypto implementation" not in source
    assert "Replay implementation" not in source
