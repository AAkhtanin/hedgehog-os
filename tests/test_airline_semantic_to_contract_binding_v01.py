from __future__ import annotations

import inspect
from dataclasses import replace
from pathlib import Path

import pytest

from hedgehog.domains.airline import semantic_to_contract_binding_v01 as binding


def _assert_pass(report: binding.AirlineSemanticToContractValidationReportV01) -> None:
    assert report.validation_status == binding.STATUS_PASS
    assert report.reason_codes == ()
    assert report.return_to_root_required is False
    assert report.real_world_effects_count == 0


def _assert_status(
    report: binding.AirlineSemanticToContractValidationReportV01,
    status: str,
) -> None:
    assert report.validation_status == status
    assert report.reason_codes == ()


def _assert_fails_with(
    report: binding.AirlineSemanticToContractValidationReportV01,
    reason: str,
) -> None:
    assert report.validation_status == binding.STATUS_FAIL_CLOSED
    assert report.return_to_root_required is True
    assert reason in report.reason_codes


def _base(
    explicit_offer_id: str,
) -> dict[str, object]:
    constraints = binding.build_client_constraints_preference_a_v01()
    snapshot = binding.build_airline_candidate_snapshot_v01()
    bsep_projection = binding.build_valid_airline_bsep_projection_ref_v01()
    selection_input = binding.build_selection_input_v01(
        bsep_projection,
        constraints,
        snapshot,
    )
    proposal = binding.build_valid_proposal_v01(
        selection_input=selection_input,
        recommended_offer_id=explicit_offer_id,
        ranked_offer_ids=(explicit_offer_id,),
    )
    actor_reviews = binding.build_valid_actor_reviews_v01(
        selection_input=selection_input,
        reviewed_offer_id=explicit_offer_id,
    )
    synthesis = binding.build_valid_synthesis_report_v01(
        selection_input=selection_input,
        actor_reviews=actor_reviews,
        synthesized_recommended_offer_id=explicit_offer_id,
    )
    evidence = binding.build_valid_canonical_selection_evidence_v01(
        selection_input=selection_input,
        proposal=proposal,
        synthesis=synthesis,
    )
    decision = binding.build_valid_client_root_decision_v01(
        selection_input=selection_input,
        evidence=evidence,
        selected_offer_id=explicit_offer_id,
        recommendation_accepted=True,
        root_override_used=False,
    )
    resolution = binding.build_valid_airline_root_resolution_v01(
        selection_input=selection_input,
        snapshot=snapshot,
        decision=decision,
    )
    hold_packet = binding.build_hold_packet_for_offer_v01(snapshot, explicit_offer_id)
    hold_binding = binding.build_valid_hold_contract_binding_v01(
        resolution=resolution,
        hold_packet=hold_packet,
    )
    binding_report = binding.build_valid_semantic_to_contract_binding_report_v01(
        bsep_projection=bsep_projection,
        constraints=constraints,
        snapshot=snapshot,
        selection_input=selection_input,
        proposal=proposal,
        actor_reviews=actor_reviews,
        synthesis=synthesis,
        evidence=evidence,
        decision=decision,
        resolution=resolution,
        hold_packet=hold_packet,
        hold_binding=hold_binding,
    )
    return {
        "bsep_projection": bsep_projection,
        "constraints": constraints,
        "snapshot": snapshot,
        "selection_input": selection_input,
        "proposal": proposal,
        "actor_reviews": actor_reviews,
        "synthesis": synthesis,
        "evidence": evidence,
        "decision": decision,
        "resolution": resolution,
        "hold_packet": hold_packet,
        "hold_binding": hold_binding,
        "binding_report": binding_report,
    }


def _payload(
    selection_input: binding.AirlineSemanticSelectionInputV01,
    explicit_offer_id: str,
) -> dict[str, object]:
    return {
        "proposal_id": f"semantic_offer_selection_proposal:{explicit_offer_id}",
        "transaction_id": selection_input.transaction_id,
        "actor_id": binding.ACTOR_CLIENT_PURCHASE_INTENT_REVIEWER,
        "source_selection_input_id": selection_input.selection_input_id,
        "source_bsep_projection_ref": selection_input.source_bsep_projection_ref,
        "source_client_constraint_set_id": (
            selection_input.source_client_constraint_set_id
        ),
        "source_candidate_set_snapshot_id": (
            selection_input.source_candidate_set_snapshot_id
        ),
        "source_candidate_set_digest": selection_input.source_candidate_set_digest,
        "candidate_set_ref": selection_input.source_candidate_set_ref,
        "recommended_offer_id": explicit_offer_id,
        "ranked_offer_ids": (explicit_offer_id,),
        "decision_factors": ("bounded_candidate_semantics",),
        "preference_matches": ("explicit_recommendation_supplied",),
        "uncertainty_notes": ("requires_client_root_review",),
        "requires_root_review": True,
        "semantic_summary": "Advisory proposal over bounded candidate ids.",
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


def _offer_record(
    snapshot: binding.AirlineRootOfferCandidateSetSnapshotV01,
    explicit_offer_id: str,
) -> binding.AirlineAuthoritativeOfferRecordV01:
    return {
        record.offer_id: record
        for record in snapshot.authoritative_offer_records
    }[explicit_offer_id]


def _local_chain(
    bundle: dict[str, object],
) -> binding.AirlineSemanticToContractValidationReportV01:
    return binding.validate_airline_semantic_to_contract_local_chain_v01(
        bsep_projection=bundle["bsep_projection"],
        constraints=bundle["constraints"],
        snapshot=bundle["snapshot"],
        selection_input=bundle["selection_input"],
        proposal=bundle["proposal"],
        actor_reviews=bundle["actor_reviews"],
        synthesis=bundle["synthesis"],
        evidence=bundle["evidence"],
        decision=bundle["decision"],
        resolution=bundle["resolution"],
        hold_packet=bundle["hold_packet"],
        hold_binding=bundle["hold_binding"],
        binding_report=bundle["binding_report"],
    )


def _proposal_binding_row(
    report: binding.AirlineSemanticToContractBindingReportV01,
) -> binding.AirlineSemanticToContractBindingRowV01:
    return {
        row.binding_id: row
        for row in report.causal_binding_rows
    }["semantic_proposal_to_canonical_selection"]


def test_valid_snapshot_passes() -> None:
    _assert_pass(
        binding.validate_airline_candidate_snapshot_v01(
            binding.build_airline_candidate_snapshot_v01(),
        ),
    )


def test_canonical_digest_stable() -> None:
    first = binding.build_airline_candidate_snapshot_v01()
    second = binding.build_airline_candidate_snapshot_v01()

    assert first.candidate_set_digest == second.candidate_set_digest
    assert (
        binding.compute_airline_candidate_set_digest_v01(first)
        == first.candidate_set_digest
    )


def test_record_input_order_does_not_change_digest() -> None:
    snapshot = binding.build_airline_candidate_snapshot_v01()
    reordered = replace(
        snapshot,
        authoritative_offer_records=tuple(reversed(snapshot.authoritative_offer_records)),
    )

    assert (
        binding.compute_airline_candidate_set_digest_v01(reordered)
        == snapshot.candidate_set_digest
    )


def test_changing_any_offer_fact_changes_digest() -> None:
    snapshot = binding.build_airline_candidate_snapshot_v01()
    changed_records = tuple(
        replace(record, amount=record.amount + 1)
        if record.offer_id == binding.OFFER_A_ID
        else record
        for record in snapshot.authoritative_offer_records
    )
    changed = replace(snapshot, authoritative_offer_records=changed_records)

    assert (
        binding.compute_airline_candidate_set_digest_v01(changed)
        != snapshot.candidate_set_digest
    )


def test_forged_digest_rejected() -> None:
    snapshot = replace(
        binding.build_airline_candidate_snapshot_v01(),
        candidate_set_digest="forged",
    )

    _assert_fails_with(
        binding.validate_airline_candidate_snapshot_v01(snapshot),
        binding.REASON_CANDIDATE_SNAPSHOT_DIGEST_MISMATCH,
    )


def test_substituted_snapshot_id_rejected() -> None:
    bundle = _base(binding.OFFER_A_ID)
    selection_input = bundle["selection_input"]
    snapshot = bundle["snapshot"]
    proposal = replace(
        bundle["proposal"],
        source_candidate_set_snapshot_id="candidate_snapshot:other",
    )

    _assert_fails_with(
        binding.validate_airline_semantic_offer_selection_proposal_v01(
            selection_input,
            proposal,
        ),
        binding.REASON_SELECTION_INPUT_SNAPSHOT_MISMATCH,
    )
    resolution = replace(
        bundle["resolution"],
        source_candidate_set_snapshot_id="candidate_snapshot:other",
    )
    _assert_fails_with(
        binding.validate_airline_root_selected_offer_resolution_v01(
            selection_input,
            snapshot,
            bundle["evidence"],
            bundle["decision"],
            resolution,
        ),
        binding.REASON_SNAPSHOT_SUBSTITUTION_DETECTED,
    )


def test_version_mismatch_rejected() -> None:
    snapshot = replace(
        binding.build_airline_candidate_snapshot_v01(),
        candidate_set_version="v2",
    )

    _assert_fails_with(
        binding.validate_airline_candidate_snapshot_v01(snapshot),
        binding.REASON_CANDIDATE_SNAPSHOT_VERSION_MISMATCH,
    )


def test_expired_snapshot_rejected() -> None:
    snapshot = replace(
        binding.build_airline_candidate_snapshot_v01(),
        snapshot_expired=True,
    )

    _assert_fails_with(
        binding.validate_airline_candidate_snapshot_v01(snapshot),
        binding.REASON_CANDIDATE_SNAPSHOT_EXPIRED,
    )


def test_provider_created_snapshot_rejected() -> None:
    snapshot = replace(
        binding.build_airline_candidate_snapshot_v01(),
        provider_created=True,
    )

    _assert_fails_with(
        binding.validate_airline_candidate_snapshot_v01(snapshot),
        binding.REASON_PROVIDER_CREATED_CANDIDATE_SNAPSHOT,
    )


def test_raw_secret_flag_rejected() -> None:
    snapshot = replace(
        binding.build_airline_candidate_snapshot_v01(),
        raw_secret_included=True,
    )

    _assert_fails_with(
        binding.validate_airline_candidate_snapshot_v01(snapshot),
        binding.REASON_RAW_SECRET_IN_CANDIDATE_SNAPSHOT,
    )


def test_preference_a_constraints_valid() -> None:
    _assert_pass(
        binding.validate_client_root_travel_constraint_set_v01(
            binding.build_client_constraints_preference_a_v01(),
        ),
    )


def test_preference_b_constraints_valid() -> None:
    _assert_pass(
        binding.validate_client_root_travel_constraint_set_v01(
            binding.build_client_constraints_preference_b_v01(),
        ),
    )


def test_valid_airline_bsep_projection_ref_passes() -> None:
    _assert_pass(
        binding.validate_airline_bsep_projection_ref_v01(
            binding.build_valid_airline_bsep_projection_ref_v01(),
        ),
    )


def test_invalid_airline_bsep_projection_ref_rejected() -> None:
    projection = replace(
        binding.build_valid_airline_bsep_projection_ref_v01(),
        projection_side="wrong_side",
    )

    _assert_fails_with(
        binding.validate_airline_bsep_projection_ref_v01(projection),
        binding.REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH,
    )


def test_hard_constraints_identical_across_a_b() -> None:
    a = binding.build_client_constraints_preference_a_v01()
    b = binding.build_client_constraints_preference_b_v01()

    assert a.origin == b.origin
    assert a.destination == b.destination
    assert a.departure_date == b.departure_date
    assert a.return_date == b.return_date
    assert a.max_amount == b.max_amount
    assert a.currency == b.currency
    assert a.baggage_required == b.baggage_required
    assert a.avoid_overnight_layover == b.avoid_overnight_layover


def test_only_soft_preference_fields_differ_across_a_b() -> None:
    a = binding.build_client_constraints_preference_a_v01()
    b = binding.build_client_constraints_preference_b_v01()

    assert a.preferred_seat_characteristics != b.preferred_seat_characteristics
    assert a.soft_preference_priority != b.soft_preference_priority
    assert replace(
        a,
        constraint_set_id=b.constraint_set_id,
        preferred_seat_characteristics=b.preferred_seat_characteristics,
        soft_preference_priority=b.soft_preference_priority,
    ) == b


def test_current_snapshot_classifies_a_b_compatible_and_c_incompatible() -> None:
    constraints = binding.build_client_constraints_preference_a_v01()
    snapshot = binding.build_airline_candidate_snapshot_v01()
    bsep_projection = binding.build_valid_airline_bsep_projection_ref_v01()
    selection_input = binding.build_selection_input_v01(
        bsep_projection,
        constraints,
        snapshot,
    )

    _assert_pass(
        binding.validate_airline_semantic_selection_input_v01(
            bsep_projection,
            constraints,
            snapshot,
            selection_input,
        ),
    )
    assert selection_input.airline_valid_candidate_ids == (
        binding.OFFER_A_ID,
        binding.OFFER_B_ID,
        binding.OFFER_C_ID,
    )
    assert selection_input.client_hard_compatible_candidate_ids == (
        binding.OFFER_A_ID,
        binding.OFFER_B_ID,
    )
    assert binding.OFFER_C_ID in selection_input.visible_candidate_ids


def test_wrong_bsep_constraint_snapshot_lineage_rejected() -> None:
    constraints = binding.build_client_constraints_preference_a_v01()
    snapshot = binding.build_airline_candidate_snapshot_v01()
    bsep_projection = binding.build_valid_airline_bsep_projection_ref_v01()
    selection_input = replace(
        binding.build_selection_input_v01(
            bsep_projection,
            constraints,
            snapshot,
        ),
        source_bsep_projection_ref="bsep_projection:wrong",
        source_client_constraint_set_id="client_constraints:wrong",
        source_candidate_set_digest="wrong_digest",
    )

    report = binding.validate_airline_semantic_selection_input_v01(
        bsep_projection,
        constraints,
        snapshot,
        selection_input,
    )

    assert report.validation_status == binding.STATUS_FAIL_CLOSED
    assert binding.REASON_CLIENT_CONSTRAINT_SET_INVALID in report.reason_codes
    assert binding.REASON_SELECTION_INPUT_SNAPSHOT_MISMATCH in report.reason_codes


def test_valid_explicit_offer_a_proposal_passes() -> None:
    selection_input = _base(binding.OFFER_A_ID)["selection_input"]

    _assert_pass(
        binding.validate_airline_semantic_offer_selection_proposal_v01(
            selection_input,
            binding.build_valid_proposal_v01(
                selection_input=selection_input,
                recommended_offer_id=binding.OFFER_A_ID,
                ranked_offer_ids=(binding.OFFER_A_ID,),
            ),
        ),
    )


def test_valid_explicit_offer_b_proposal_passes() -> None:
    selection_input = _base(binding.OFFER_B_ID)["selection_input"]

    _assert_pass(
        binding.validate_airline_semantic_offer_selection_proposal_v01(
            selection_input,
            binding.build_valid_proposal_v01(
                selection_input=selection_input,
                recommended_offer_id=binding.OFFER_B_ID,
                ranked_offer_ids=(binding.OFFER_B_ID,),
            ),
        ),
    )


def test_no_default_recommendation_exists() -> None:
    proposal_sig = inspect.signature(binding.build_valid_proposal_v01)
    decision_sig = inspect.signature(binding.build_valid_client_root_decision_v01)

    assert (
        proposal_sig.parameters["recommended_offer_id"].default
        is inspect.Parameter.empty
    )
    assert (
        decision_sig.parameters["selected_offer_id"].default
        is inspect.Parameter.empty
    )


@pytest.mark.parametrize("field", sorted(binding.PROPOSAL_PAYLOAD_FIELDS))
def test_missing_provider_field_fails_closed(field: str) -> None:
    selection_input = _base(binding.OFFER_A_ID)["selection_input"]
    payload = _payload(selection_input, binding.OFFER_A_ID)
    payload.pop(field)

    _assert_fails_with(
        binding.validate_airline_semantic_offer_selection_proposal_payload_v01(
            selection_input,
            payload,
        ),
        binding.REASON_MISSING_PROVIDER_OUTPUT_FIELD,
    )


@pytest.mark.parametrize("payload", ([], "text", 42, None))
def test_malformed_provider_payload_type_fails_closed(payload: object) -> None:
    selection_input = _base(binding.OFFER_A_ID)["selection_input"]

    _assert_fails_with(
        binding.validate_airline_semantic_offer_selection_proposal_payload_v01(
            selection_input,
            payload,
        ),
        binding.REASON_INVALID_PROVIDER_OUTPUT_CONTAINER,
    )


@pytest.mark.parametrize(
    "payload_update, reason",
    (
        ({"requires_root_review": "false"}, binding.REASON_INVALID_PROVIDER_OUTPUT_TYPE),
        ({"semantic_summary": ""}, binding.REASON_EMPTY_PROVIDER_OUTPUT_FIELD),
        ({"ranked_offer_ids": binding.OFFER_A_ID}, binding.REASON_INVALID_PROVIDER_OUTPUT_CONTAINER),
        ({"ranked_offer_ids": (binding.OFFER_A_ID, 7)}, binding.REASON_INVALID_PROVIDER_OUTPUT_TYPE),
        ({"real_world_effects_count": False}, binding.REASON_INVALID_PROVIDER_OUTPUT_TYPE),
    ),
)
def test_strict_provider_payload_types_rejected(
    payload_update: dict[str, object],
    reason: str,
) -> None:
    selection_input = _base(binding.OFFER_A_ID)["selection_input"]
    payload = _payload(selection_input, binding.OFFER_A_ID)
    payload.update(payload_update)

    _assert_fails_with(
        binding.validate_airline_semantic_offer_selection_proposal_payload_v01(
            selection_input,
            payload,
        ),
        reason,
    )


@pytest.mark.parametrize("payload", ([], "text", 42, None, {"proposal_id": 7}))
def test_no_malformed_payload_raises_exception(payload: object) -> None:
    selection_input = _base(binding.OFFER_A_ID)["selection_input"]

    report = binding.validate_airline_semantic_offer_selection_proposal_payload_v01(
        selection_input,
        payload,
    )

    assert report.validation_status == binding.STATUS_FAIL_CLOSED


def test_unknown_offer_rejected() -> None:
    selection_input = _base(binding.OFFER_A_ID)["selection_input"]
    payload = _payload(selection_input, "offer:unknown")

    _assert_fails_with(
        binding.validate_airline_semantic_offer_selection_proposal_payload_v01(
            selection_input,
            payload,
        ),
        binding.REASON_UNKNOWN_CANDIDATE_ID,
    )


def test_duplicate_ranked_id_rejected() -> None:
    selection_input = _base(binding.OFFER_A_ID)["selection_input"]
    proposal = binding.build_valid_proposal_v01(
        selection_input=selection_input,
        recommended_offer_id=binding.OFFER_A_ID,
        ranked_offer_ids=(binding.OFFER_A_ID,),
    )
    proposal = replace(
        proposal,
        ranked_offer_ids=(binding.OFFER_A_ID, binding.OFFER_A_ID),
    )

    _assert_fails_with(
        binding.validate_airline_semantic_offer_selection_proposal_v01(
            selection_input,
            proposal,
        ),
        binding.REASON_DUPLICATE_RANKED_OFFER_ID,
    )


def test_recommended_id_absent_from_ranking_rejected() -> None:
    selection_input = _base(binding.OFFER_A_ID)["selection_input"]
    proposal = binding.build_valid_proposal_v01(
        selection_input=selection_input,
        recommended_offer_id=binding.OFFER_A_ID,
        ranked_offer_ids=(binding.OFFER_A_ID,),
    )
    proposal = replace(proposal, ranked_offer_ids=(binding.OFFER_B_ID,))

    _assert_fails_with(
        binding.validate_airline_semantic_offer_selection_proposal_v01(
            selection_input,
            proposal,
        ),
        binding.REASON_RECOMMENDED_OFFER_MISSING_FROM_RANKING,
    )


@pytest.mark.parametrize(
    "field",
    sorted(binding.FORBIDDEN_PROVIDER_PROPOSAL_FIELDS),
)
def test_each_forbidden_authoritative_provider_field_rejected(field: str) -> None:
    selection_input = _base(binding.OFFER_A_ID)["selection_input"]
    payload = _payload(selection_input, binding.OFFER_A_ID)
    payload[field] = "provider_attempted_authority"

    _assert_fails_with(
        binding.validate_airline_semantic_offer_selection_proposal_payload_v01(
            selection_input,
            payload,
        ),
        binding.REASON_FORBIDDEN_PROVIDER_AUTHORITATIVE_FIELD,
    )


def test_unknown_output_field_rejected() -> None:
    selection_input = _base(binding.OFFER_A_ID)["selection_input"]
    payload = _payload(selection_input, binding.OFFER_A_ID)
    payload["unexpected_field"] = "nope"

    _assert_fails_with(
        binding.validate_airline_semantic_offer_selection_proposal_payload_v01(
            selection_input,
            payload,
        ),
        binding.REASON_UNKNOWN_PROVIDER_OUTPUT_FIELD,
    )


@pytest.mark.parametrize(
    ("field", "reason"),
    (
        ("authority_created", binding.REASON_PROVIDER_CLAIMED_AUTHORITY),
        ("packet_created", binding.REASON_PROVIDER_CLAIMED_ACTION),
        ("real_world_effects_count", binding.REASON_PROVIDER_CLAIMED_EFFECT),
    ),
)
def test_authority_action_effect_claim_rejected(field: str, reason: str) -> None:
    selection_input = _base(binding.OFFER_A_ID)["selection_input"]
    payload = _payload(selection_input, binding.OFFER_A_ID)
    payload[field] = 1 if field == "real_world_effects_count" else True

    _assert_fails_with(
        binding.validate_airline_semantic_offer_selection_proposal_payload_v01(
            selection_input,
            payload,
        ),
        reason,
    )


def test_proposal_snapshot_digest_mismatch_rejected() -> None:
    selection_input = _base(binding.OFFER_A_ID)["selection_input"]
    proposal = binding.build_valid_proposal_v01(
        selection_input=selection_input,
        recommended_offer_id=binding.OFFER_A_ID,
        ranked_offer_ids=(binding.OFFER_A_ID,),
    )
    proposal = replace(proposal, source_candidate_set_digest="wrong")

    _assert_fails_with(
        binding.validate_airline_semantic_offer_selection_proposal_v01(
            selection_input,
            proposal,
        ),
        binding.REASON_SELECTION_INPUT_SNAPSHOT_MISMATCH,
    )


@pytest.mark.parametrize(
    "field, value, reason",
    (
        (
            "actor_id",
            "airline_offer_policy_reviewer_llm",
            binding.REASON_ACTOR_ROLE_MISMATCH,
        ),
        (
            "source_client_constraint_set_id",
            "client_constraints:wrong",
            binding.REASON_CLIENT_CONSTRAINT_SET_INVALID,
        ),
        (
            "candidate_set_ref",
            "candidate_set:wrong",
            binding.REASON_SELECTION_INPUT_SNAPSHOT_MISMATCH,
        ),
        (
            "source_bsep_projection_ref",
            "bsep_projection:wrong",
            binding.REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH,
        ),
        (
            "requires_root_review",
            False,
            binding.REASON_ACTOR_OUTPUT_NOT_VALIDATED,
        ),
    ),
)
def test_complete_proposal_lineage_mutations_rejected(
    field: str,
    value: object,
    reason: str,
) -> None:
    selection_input = _base(binding.OFFER_A_ID)["selection_input"]
    proposal = replace(
        binding.build_valid_proposal_v01(
            selection_input=selection_input,
            recommended_offer_id=binding.OFFER_A_ID,
            ranked_offer_ids=(binding.OFFER_A_ID,),
        ),
        **{field: value},
    )

    _assert_fails_with(
        binding.validate_airline_semantic_offer_selection_proposal_v01(
            selection_input,
            proposal,
        ),
        reason,
    )


def test_exact_five_actor_roles_pass() -> None:
    bundle = _base(binding.OFFER_A_ID)

    _assert_pass(
        binding.validate_airline_semantic_selection_synthesis_report_v01(
            bundle["selection_input"],
            bundle["actor_reviews"],
            bundle["synthesis"],
        ),
    )


def test_missing_actor_rejected() -> None:
    bundle = _base(binding.OFFER_A_ID)

    _assert_fails_with(
        binding.validate_airline_semantic_selection_synthesis_report_v01(
            bundle["selection_input"],
            bundle["actor_reviews"][:-1],
            bundle["synthesis"],
        ),
        binding.REASON_MISSING_REQUIRED_ACTOR_OUTPUT,
    )


def test_duplicate_actor_rejected() -> None:
    bundle = _base(binding.OFFER_A_ID)
    actor_reviews = bundle["actor_reviews"]

    _assert_fails_with(
        binding.validate_airline_semantic_selection_synthesis_report_v01(
            bundle["selection_input"],
            actor_reviews[:-1] + (actor_reviews[0],),
            bundle["synthesis"],
        ),
        binding.REASON_DUPLICATE_ACTOR_OUTPUT,
    )


def test_role_mismatch_rejected() -> None:
    bundle = _base(binding.OFFER_A_ID)
    actor_reviews = (
        replace(bundle["actor_reviews"][0], review_role="wrong_role"),
    ) + bundle["actor_reviews"][1:]

    _assert_fails_with(
        binding.validate_airline_semantic_selection_synthesis_report_v01(
            bundle["selection_input"],
            actor_reviews,
            bundle["synthesis"],
        ),
        binding.REASON_ACTOR_ROLE_MISMATCH,
    )


def test_unvalidated_actor_output_rejected() -> None:
    bundle = _base(binding.OFFER_A_ID)
    actor_reviews = (
        replace(bundle["actor_reviews"][0], validation_status=binding.STATUS_FAIL_CLOSED),
    ) + bundle["actor_reviews"][1:]

    _assert_fails_with(
        binding.validate_airline_semantic_selection_synthesis_report_v01(
            bundle["selection_input"],
            actor_reviews,
            bundle["synthesis"],
        ),
        binding.REASON_ACTOR_OUTPUT_NOT_VALIDATED,
    )


def test_raw_output_usage_rejected() -> None:
    bundle = _base(binding.OFFER_A_ID)
    actor_reviews = (
        replace(bundle["actor_reviews"][0], raw_output_used=True),
    ) + bundle["actor_reviews"][1:]

    _assert_fails_with(
        binding.validate_airline_semantic_selection_synthesis_report_v01(
            bundle["selection_input"],
            actor_reviews,
            bundle["synthesis"],
        ),
        binding.REASON_ACTOR_OUTPUT_NOT_VALIDATED,
    )


def test_conflicting_reviewed_offer_rejected() -> None:
    bundle = _base(binding.OFFER_A_ID)
    actor_reviews = (
        replace(bundle["actor_reviews"][0], reviewed_offer_id=binding.OFFER_B_ID),
    ) + bundle["actor_reviews"][1:]

    _assert_fails_with(
        binding.validate_airline_semantic_selection_synthesis_report_v01(
            bundle["selection_input"],
            actor_reviews,
            bundle["synthesis"],
        ),
        binding.REASON_MULTI_ACTOR_CONFLICT,
    )


def test_blocking_reviewer_conflict_rejected() -> None:
    bundle = _base(binding.OFFER_A_ID)
    actor_reviews = (
        replace(bundle["actor_reviews"][1], blocking_conflicts=("policy_conflict",)),
    ) + bundle["actor_reviews"][2:]

    _assert_fails_with(
        binding.validate_airline_semantic_selection_synthesis_report_v01(
            bundle["selection_input"],
            actor_reviews,
            bundle["synthesis"],
        ),
        binding.REASON_MULTI_ACTOR_CONFLICT,
    )


def test_no_last_writer_wins_behavior() -> None:
    bundle = _base(binding.OFFER_A_ID)
    actor_reviews = bundle["actor_reviews"][:-1] + (
        replace(bundle["actor_reviews"][-1], reviewed_offer_id=binding.OFFER_B_ID),
    )

    report = binding.validate_airline_semantic_selection_synthesis_report_v01(
        bundle["selection_input"],
        actor_reviews,
        bundle["synthesis"],
    )

    assert binding.REASON_MULTI_ACTOR_CONFLICT in report.reason_codes
    assert binding.REASON_HIDDEN_ACTOR_PRIORITY_FORBIDDEN in report.reason_codes


def test_no_majority_vote_behavior() -> None:
    bundle = _base(binding.OFFER_A_ID)
    actor_reviews = tuple(
        replace(review, reviewed_offer_id=binding.OFFER_B_ID)
        if index >= 3
        else review
        for index, review in enumerate(bundle["actor_reviews"])
    )

    _assert_fails_with(
        binding.validate_airline_semantic_selection_synthesis_report_v01(
            bundle["selection_input"],
            actor_reviews,
            bundle["synthesis"],
        ),
        binding.REASON_MULTI_ACTOR_CONFLICT,
    )


def test_unresolved_conflict_creates_no_canonical_selection() -> None:
    bundle = _base(binding.OFFER_A_ID)
    synthesis = replace(
        bundle["synthesis"],
        synthesis_status=binding.STATUS_REQUIRES_ROOT_REVIEW,
        actor_conflicts=("unresolved_offer_conflict",),
        unresolved_conflict_present=True,
    )
    evidence = replace(bundle["evidence"], source_synthesis_report_id=synthesis.synthesis_report_id)

    _assert_fails_with(
        binding.validate_airline_semantic_selection_synthesis_report_v01(
            bundle["selection_input"],
            bundle["actor_reviews"],
            synthesis,
        ),
        binding.REASON_UNRESOLVED_CONFLICT,
    )
    _assert_fails_with(
        binding.validate_validated_airline_semantic_selection_evidence_v01(
            bundle["selection_input"],
            bundle["proposal"],
            bundle["actor_reviews"],
            synthesis,
            evidence,
        ),
        binding.REASON_SYNTHESIS_NOT_PASS,
    )


def test_synthesis_remains_advisory() -> None:
    bundle = _base(binding.OFFER_A_ID)
    synthesis = replace(bundle["synthesis"], authority_created=True)

    _assert_fails_with(
        binding.validate_airline_semantic_selection_synthesis_report_v01(
            bundle["selection_input"],
            bundle["actor_reviews"],
            synthesis,
        ),
        binding.REASON_PROVIDER_CLAIMED_AUTHORITY,
    )


def test_forged_actor_recommended_offer_ids_rejected() -> None:
    bundle = _base(binding.OFFER_A_ID)
    synthesis = replace(
        bundle["synthesis"],
        actor_recommended_offer_ids=(
            (binding.ACTOR_CLIENT_PURCHASE_INTENT_REVIEWER, binding.OFFER_B_ID),
        )
        + bundle["synthesis"].actor_recommended_offer_ids[1:],
    )

    _assert_fails_with(
        binding.validate_airline_semantic_selection_synthesis_report_v01(
            bundle["selection_input"],
            bundle["actor_reviews"],
            synthesis,
        ),
        binding.REASON_MULTI_ACTOR_CONFLICT,
    )


def test_duplicate_canonical_output_id_rejected() -> None:
    bundle = _base(binding.OFFER_A_ID)
    actor_reviews = (
        bundle["actor_reviews"][0],
        replace(
            bundle["actor_reviews"][1],
            canonical_actor_output_id=bundle["actor_reviews"][0].canonical_actor_output_id,
        ),
    ) + bundle["actor_reviews"][2:]

    _assert_fails_with(
        binding.validate_airline_semantic_selection_synthesis_report_v01(
            bundle["selection_input"],
            actor_reviews,
            bundle["synthesis"],
        ),
        binding.REASON_DUPLICATE_ACTOR_OUTPUT,
    )


def test_supports_proposed_offer_false_rejected() -> None:
    bundle = _base(binding.OFFER_A_ID)
    actor_reviews = (
        replace(bundle["actor_reviews"][0], supports_proposed_offer=False),
    ) + bundle["actor_reviews"][1:]

    _assert_fails_with(
        binding.validate_airline_semantic_selection_synthesis_report_v01(
            bundle["selection_input"],
            actor_reviews,
            bundle["synthesis"],
        ),
        binding.REASON_ACTOR_OUTPUT_NOT_VALIDATED,
    )


def test_empty_semantic_factors_rejected() -> None:
    bundle = _base(binding.OFFER_A_ID)
    actor_reviews = (
        replace(bundle["actor_reviews"][0], semantic_factors=()),
    ) + bundle["actor_reviews"][1:]

    _assert_fails_with(
        binding.validate_airline_semantic_selection_synthesis_report_v01(
            bundle["selection_input"],
            actor_reviews,
            bundle["synthesis"],
        ),
        binding.REASON_ACTOR_OUTPUT_NOT_VALIDATED,
    )


def test_requires_client_root_review_false_rejected() -> None:
    bundle = _base(binding.OFFER_A_ID)
    synthesis = replace(bundle["synthesis"], requires_client_root_review=False)

    _assert_fails_with(
        binding.validate_airline_semantic_selection_synthesis_report_v01(
            bundle["selection_input"],
            bundle["actor_reviews"],
            synthesis,
        ),
        binding.REASON_SYNTHESIS_NOT_PASS,
    )


def test_invalid_actor_set_cannot_create_valid_canonical_evidence() -> None:
    bundle = _base(binding.OFFER_A_ID)
    actor_reviews = bundle["actor_reviews"][:-1]

    _assert_fails_with(
        binding.validate_validated_airline_semantic_selection_evidence_v01(
            bundle["selection_input"],
            bundle["proposal"],
            actor_reviews,
            bundle["synthesis"],
            bundle["evidence"],
        ),
        binding.REASON_MISSING_REQUIRED_ACTOR_OUTPUT,
    )


def test_forged_proposal_id_breaks_local_chain() -> None:
    bundle = _base(binding.OFFER_A_ID)
    bundle = {
        **bundle,
        "proposal": replace(bundle["proposal"], proposal_id="proposal:forged"),
    }

    _assert_fails_with(
        _local_chain(bundle),
        binding.REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH,
    )


@pytest.mark.parametrize(
    "field, value",
    (
        ("source_proposal_id", "proposal:forged"),
        ("source_actor_id", "actor:forged"),
        ("source_candidate_set_ref", "candidate_set:forged"),
        ("accepted_semantic_factors", ("rewritten_acceptance",)),
        ("rejected_semantic_factors", ("rewritten_rejection",)),
    ),
)
def test_forged_evidence_lineage_rejected(field: str, value: object) -> None:
    bundle = _base(binding.OFFER_A_ID)
    evidence = replace(bundle["evidence"], **{field: value})

    _assert_fails_with(
        binding.validate_validated_airline_semantic_selection_evidence_v01(
            bundle["selection_input"],
            bundle["proposal"],
            bundle["actor_reviews"],
            bundle["synthesis"],
            evidence,
        ),
        binding.REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH,
    )


def _assert_evidence_lineage_field_rejected(field: str, value: object) -> None:
    bundle = _base(binding.OFFER_A_ID)
    evidence = replace(bundle["evidence"], **{field: value})

    _assert_fails_with(
        binding.validate_validated_airline_semantic_selection_evidence_v01(
            bundle["selection_input"],
            bundle["proposal"],
            bundle["actor_reviews"],
            bundle["synthesis"],
            evidence,
        ),
        binding.REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH,
    )


def test_forged_evidence_source_proposal_id_rejected() -> None:
    _assert_evidence_lineage_field_rejected("source_proposal_id", "proposal:forged")


def test_forged_evidence_source_actor_id_rejected() -> None:
    _assert_evidence_lineage_field_rejected("source_actor_id", "actor:forged")


def test_forged_evidence_candidate_set_ref_rejected() -> None:
    _assert_evidence_lineage_field_rejected(
        "source_candidate_set_ref",
        "candidate_set:forged",
    )


def test_evidence_accepted_semantic_factors_must_match_synthesis() -> None:
    _assert_evidence_lineage_field_rejected(
        "accepted_semantic_factors",
        ("rewritten_acceptance",),
    )


def test_evidence_rejected_semantic_factors_must_match_synthesis() -> None:
    _assert_evidence_lineage_field_rejected(
        "rejected_semantic_factors",
        ("rewritten_rejection",),
    )


def test_empty_typed_proposal_id_rejected() -> None:
    bundle = _base(binding.OFFER_A_ID)
    proposal = replace(bundle["proposal"], proposal_id="")

    _assert_fails_with(
        binding.validate_validated_airline_semantic_selection_evidence_v01(
            bundle["selection_input"],
            proposal,
            bundle["actor_reviews"],
            bundle["synthesis"],
            bundle["evidence"],
        ),
        binding.REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH,
    )


def test_explicit_a_causal_decision_passes() -> None:
    bundle = _base(binding.OFFER_A_ID)

    _assert_pass(
        binding.validate_client_root_offer_selection_decision_v01(
            bundle["selection_input"],
            bundle["evidence"],
            bundle["decision"],
        ),
    )


def test_explicit_b_causal_decision_passes() -> None:
    bundle = _base(binding.OFFER_B_ID)

    _assert_pass(
        binding.validate_client_root_offer_selection_decision_v01(
            bundle["selection_input"],
            bundle["evidence"],
            bundle["decision"],
        ),
    )


def test_offer_c_rejected_by_clientroot_compatibility() -> None:
    bundle = _base(binding.OFFER_C_ID)

    _assert_fails_with(
        binding.validate_client_root_offer_selection_decision_v01(
            bundle["selection_input"],
            bundle["evidence"],
            bundle["decision"],
        ),
        binding.REASON_CLIENT_CONSTRAINT_COMPATIBILITY_FAILED,
    )


def test_root_override_safe_but_status_root_override() -> None:
    bundle = _base(binding.OFFER_A_ID)
    decision = binding.build_valid_client_root_decision_v01(
        selection_input=bundle["selection_input"],
        evidence=bundle["evidence"],
        selected_offer_id=binding.OFFER_B_ID,
        recommendation_accepted=False,
        root_override_used=True,
    )

    _assert_status(
        binding.validate_client_root_offer_selection_decision_v01(
            bundle["selection_input"],
            bundle["evidence"],
            decision,
        ),
        binding.STATUS_ROOT_OVERRIDE,
    )


def test_root_override_cannot_claim_semantic_causality() -> None:
    bundle = _base(binding.OFFER_A_ID)
    decision = replace(
        binding.build_valid_client_root_decision_v01(
            selection_input=bundle["selection_input"],
            evidence=bundle["evidence"],
            selected_offer_id=binding.OFFER_B_ID,
            recommendation_accepted=False,
            root_override_used=True,
        ),
        semantic_influence_claimed=True,
    )

    _assert_fails_with(
        binding.validate_client_root_offer_selection_decision_v01(
            bundle["selection_input"],
            bundle["evidence"],
            decision,
        ),
        binding.REASON_ROOT_OVERRIDE_CANNOT_CLAIM_SEMANTIC_CAUSALITY,
    )


def test_rejected_decision_creates_no_downstream_binding() -> None:
    bundle = _base(binding.OFFER_A_ID)
    decision = replace(
        bundle["decision"],
        decision_status=binding.STATUS_REJECTED,
        recommendation_accepted=False,
        rejection_reasons=("client_root_rejected_semantic_proposal",),
    )

    report = binding.validate_client_root_offer_selection_decision_v01(
        bundle["selection_input"],
        bundle["evidence"],
        decision,
    )

    assert report.validation_status == binding.STATUS_FAIL_CLOSED
    assert binding.REASON_CLIENT_ROOT_DECISION_REJECTED in report.reason_codes


def test_rejected_clientroot_decision_returns_to_root() -> None:
    bundle = _base(binding.OFFER_A_ID)
    decision = replace(
        bundle["decision"],
        decision_status=binding.STATUS_REJECTED,
        recommendation_accepted=False,
        semantic_influence_claimed=False,
        rejection_reasons=("client_root_rejected_semantic_proposal",),
    )

    report = binding.validate_client_root_offer_selection_decision_v01(
        bundle["selection_input"],
        bundle["evidence"],
        decision,
    )

    _assert_fails_with(report, binding.REASON_CLIENT_ROOT_DECISION_REJECTED)
    assert report.relevant_root_id == binding.CLIENT_ROOT_ID


def test_rejected_clientroot_decision_cannot_resolve_airline_offer() -> None:
    bundle = _base(binding.OFFER_A_ID)
    decision = replace(
        bundle["decision"],
        decision_status=binding.STATUS_REJECTED,
        recommendation_accepted=False,
        semantic_influence_claimed=False,
        rejection_reasons=("client_root_rejected_semantic_proposal",),
    )

    _assert_fails_with(
        binding.validate_airline_root_selected_offer_resolution_v01(
            bundle["selection_input"],
            bundle["snapshot"],
            bundle["evidence"],
            decision,
            bundle["resolution"],
        ),
        binding.REASON_CLIENT_ROOT_DECISION_REJECTED,
    )


def test_invalid_clientroot_decision_cannot_create_hold_binding() -> None:
    bundle = _base(binding.OFFER_A_ID)
    invalid_decision = replace(bundle["decision"], recommendation_accepted=False)
    bundle = {**bundle, "decision": invalid_decision}

    _assert_fails_with(
        _local_chain(bundle),
        binding.REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH,
    )


def test_malformed_root_override_mode_rejected() -> None:
    bundle = _base(binding.OFFER_A_ID)
    decision = replace(
        bundle["decision"],
        decision_status=binding.STATUS_ROOT_OVERRIDE,
        recommendation_accepted=True,
        root_override_used=True,
        root_override_reason="override",
        semantic_influence_claimed=False,
    )

    _assert_fails_with(
        binding.validate_client_root_offer_selection_decision_v01(
            bundle["selection_input"],
            bundle["evidence"],
            decision,
        ),
        binding.REASON_ROOT_OVERRIDE_CANNOT_CLAIM_SEMANTIC_CAUSALITY,
    )


def test_a_facts_resolved_from_snapshot() -> None:
    bundle = _base(binding.OFFER_A_ID)

    _assert_pass(
        binding.validate_airline_root_selected_offer_resolution_v01(
            bundle["selection_input"],
            bundle["snapshot"],
            bundle["evidence"],
            bundle["decision"],
            bundle["resolution"],
        ),
    )


def test_b_facts_resolved_from_snapshot() -> None:
    bundle = _base(binding.OFFER_B_ID)

    _assert_pass(
        binding.validate_airline_root_selected_offer_resolution_v01(
            bundle["selection_input"],
            bundle["snapshot"],
            bundle["evidence"],
            bundle["decision"],
            bundle["resolution"],
        ),
    )


def test_unknown_offer_rejected_by_airlineroot() -> None:
    bundle = _base(binding.OFFER_A_ID)
    decision = replace(bundle["decision"], selected_offer_id="offer:unknown")
    resolution = replace(bundle["resolution"], selected_offer_id="offer:unknown")

    _assert_fails_with(
        binding.validate_airline_root_selected_offer_resolution_v01(
            bundle["selection_input"],
            bundle["snapshot"],
            bundle["evidence"],
            decision,
            resolution,
        ),
        binding.REASON_AIRLINE_OFFER_VALIDITY_FAILED,
    )


def test_expired_offer_rejected_by_airlineroot() -> None:
    bundle = _base(binding.OFFER_A_ID)
    snapshot = bundle["snapshot"]
    expired_records = tuple(
        replace(record, expired=True)
        if record.offer_id == binding.OFFER_A_ID
        else record
        for record in snapshot.authoritative_offer_records
    )
    snapshot = replace(snapshot, authoritative_offer_records=expired_records)
    snapshot = replace(
        snapshot,
        candidate_set_digest=binding.compute_airline_candidate_set_digest_v01(snapshot),
    )

    _assert_fails_with(
        binding.validate_airline_root_selected_offer_resolution_v01(
            bundle["selection_input"],
            snapshot,
            bundle["evidence"],
            bundle["decision"],
            bundle["resolution"],
        ),
        binding.REASON_AIRLINE_OFFER_VALIDITY_FAILED,
    )


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("resolved_amount", 999),
        ("resolved_currency", "USD"),
        ("resolved_route_ref", "route:WRONG"),
        ("resolved_baggage", False),
        ("resolved_seat_characteristics", ("wrong",)),
        ("resolved_ttl", 1200),
    ),
)
def test_resolution_fact_override_rejected(field: str, value: object) -> None:
    bundle = _base(binding.OFFER_A_ID)
    resolution = replace(bundle["resolution"], **{field: value})

    _assert_fails_with(
        binding.validate_airline_root_selected_offer_resolution_v01(
            bundle["selection_input"],
            bundle["snapshot"],
            bundle["evidence"],
            bundle["decision"],
            resolution,
        ),
        binding.REASON_RESOLUTION_FACT_MISMATCH,
    )


def test_resolution_snapshot_substitution_rejected() -> None:
    bundle = _base(binding.OFFER_A_ID)
    resolution = replace(
        bundle["resolution"],
        source_candidate_set_digest="wrong_digest",
    )

    _assert_fails_with(
        binding.validate_airline_root_selected_offer_resolution_v01(
            bundle["selection_input"],
            bundle["snapshot"],
            bundle["evidence"],
            bundle["decision"],
            resolution,
        ),
        binding.REASON_SNAPSHOT_SUBSTITUTION_DETECTED,
    )


def test_semantic_facts_never_become_authoritative_facts() -> None:
    bundle = _base(binding.OFFER_A_ID)
    resolution = replace(
        bundle["resolution"],
        semantic_values_used_as_authoritative_facts=True,
    )

    _assert_fails_with(
        binding.validate_airline_root_selected_offer_resolution_v01(
            bundle["selection_input"],
            bundle["snapshot"],
            bundle["evidence"],
            bundle["decision"],
            resolution,
        ),
        binding.REASON_RESOLUTION_FACT_MISMATCH,
    )


def test_explicit_a_resolution_binds_to_a_hold() -> None:
    bundle = _base(binding.OFFER_A_ID)

    _assert_pass(
        binding.validate_airline_semantic_hold_contract_binding_v01(
            bundle["resolution"],
            bundle["hold_packet"],
            bundle["hold_binding"],
        ),
    )


def test_explicit_b_resolution_binds_to_b_hold() -> None:
    bundle = _base(binding.OFFER_B_ID)

    _assert_pass(
        binding.validate_airline_semantic_hold_contract_binding_v01(
            bundle["resolution"],
            bundle["hold_packet"],
            bundle["hold_binding"],
        ),
    )


def test_a_resolution_cannot_bind_b_hold() -> None:
    bundle = _base(binding.OFFER_A_ID)
    hold_packet = binding.build_hold_packet_for_offer_v01(
        bundle["snapshot"],
        binding.OFFER_B_ID,
    )

    _assert_fails_with(
        binding.validate_airline_semantic_hold_contract_binding_v01(
            bundle["resolution"],
            hold_packet,
            bundle["hold_binding"],
        ),
        binding.REASON_HOLD_CONTRACT_BINDING_MISMATCH,
    )


def test_ttl_expansion_rejected() -> None:
    bundle = _base(binding.OFFER_A_ID)
    hold_packet = replace(bundle["hold_packet"], ttl_seconds=9999)

    _assert_fails_with(
        binding.validate_airline_semantic_hold_contract_binding_v01(
            bundle["resolution"],
            hold_packet,
            bundle["hold_binding"],
        ),
        binding.REASON_HOLD_CONTRACT_BINDING_MISMATCH,
    )


def test_provider_created_target_rejected() -> None:
    bundle = _base(binding.OFFER_A_ID)
    hold_binding = replace(bundle["hold_binding"], provider_created_target=True)

    _assert_fails_with(
        binding.validate_airline_semantic_hold_contract_binding_v01(
            bundle["resolution"],
            bundle["hold_packet"],
            hold_binding,
        ),
        binding.REASON_PROVIDER_CREATED_TARGET_FORBIDDEN,
    )


def test_authority_transfer_rejected() -> None:
    bundle = _base(binding.OFFER_A_ID)
    hold_binding = replace(bundle["hold_binding"], authority_transferred=True)

    _assert_fails_with(
        binding.validate_airline_semantic_hold_contract_binding_v01(
            bundle["resolution"],
            bundle["hold_packet"],
            hold_binding,
        ),
        binding.REASON_AUTHORITY_TRANSFER_FORBIDDEN,
    )


def test_required_local_rows_present() -> None:
    bundle = _base(binding.OFFER_A_ID)
    report = bundle["binding_report"]

    assert {
        row.binding_id for row in report.causal_binding_rows
    } == set(binding.REQUIRED_LOCAL_BINDING_IDS)


def test_all_local_rows_values_and_snapshots_match() -> None:
    bundle = _base(binding.OFFER_A_ID)
    report = bundle["binding_report"]

    _assert_pass(
        binding.validate_airline_semantic_to_contract_binding_report_v01(report),
    )
    assert all(row.values_match for row in report.causal_binding_rows)
    assert all(row.snapshot_match for row in report.causal_binding_rows)


def test_root_override_report_cannot_say_causal_pass() -> None:
    bundle = _base(binding.OFFER_A_ID)
    report = replace(
        bundle["binding_report"],
        root_override_used=True,
        semantic_causality_claimed=True,
    )

    _assert_fails_with(
        binding.validate_airline_semantic_to_contract_binding_report_v01(report),
        binding.REASON_ROOT_OVERRIDE_CANNOT_CLAIM_SEMANTIC_CAUSALITY,
    )


def test_missing_row_rejected() -> None:
    bundle = _base(binding.OFFER_A_ID)
    report = replace(
        bundle["binding_report"],
        causal_binding_rows=bundle["binding_report"].causal_binding_rows[:-1],
    )

    _assert_fails_with(
        binding.validate_airline_semantic_to_contract_binding_report_v01(report),
        binding.REASON_HOLD_CONTRACT_BINDING_MISMATCH,
    )


def test_altered_source_target_value_rejected() -> None:
    bundle = _base(binding.OFFER_A_ID)
    rows = (
        replace(
            bundle["binding_report"].causal_binding_rows[0],
            target_value="different",
            values_match=False,
        ),
    ) + bundle["binding_report"].causal_binding_rows[1:]
    report = replace(bundle["binding_report"], causal_binding_rows=rows)

    _assert_fails_with(
        binding.validate_airline_semantic_to_contract_binding_report_v01(report),
        binding.REASON_HOLD_CONTRACT_BINDING_MISMATCH,
    )


def test_altered_snapshot_id_rejected() -> None:
    bundle = _base(binding.OFFER_A_ID)
    rows = (
        replace(
            bundle["binding_report"].causal_binding_rows[0],
            target_snapshot_id="other",
            snapshot_match=False,
        ),
    ) + bundle["binding_report"].causal_binding_rows[1:]
    report = replace(bundle["binding_report"], causal_binding_rows=rows)

    _assert_fails_with(
        binding.validate_airline_semantic_to_contract_binding_report_v01(report),
        binding.REASON_SNAPSHOT_SUBSTITUTION_DETECTED,
    )


def test_silent_fallback_flag_rejected() -> None:
    bundle = _base(binding.OFFER_A_ID)
    report = replace(bundle["binding_report"], silent_fallback_used=True)

    _assert_fails_with(
        binding.validate_airline_semantic_to_contract_binding_report_v01(report),
        binding.REASON_SILENT_FALLBACK_FORBIDDEN,
    )


def test_hardcoded_default_flag_rejected() -> None:
    bundle = _base(binding.OFFER_A_ID)
    report = replace(bundle["binding_report"], hardcoded_default_offer_used=True)

    _assert_fails_with(
        binding.validate_airline_semantic_to_contract_binding_report_v01(report),
        binding.REASON_HARDCODED_DEFAULT_OFFER_FORBIDDEN,
    )


def test_no_integrated_corridor_pass_claimed_in_slice_b() -> None:
    bundle = _base(binding.OFFER_A_ID)
    report = replace(
        bundle["binding_report"],
        binding_status=binding.STATUS_CAUSAL_PASS,
        integrated_corridor_causal_pass_claimed=True,
    )

    _assert_fails_with(
        binding.validate_airline_semantic_to_contract_binding_report_v01(report),
        binding.REASON_INTEGRATED_CORRIDOR_PASS_FORBIDDEN_IN_SLICE_B,
    )


def test_binding_value_mismatch_with_true_flag_rejected() -> None:
    bundle = _base(binding.OFFER_A_ID)
    rows = (
        replace(
            bundle["binding_report"].causal_binding_rows[0],
            target_value="different",
            values_match=True,
        ),
    ) + bundle["binding_report"].causal_binding_rows[1:]
    report = replace(bundle["binding_report"], causal_binding_rows=rows)

    _assert_fails_with(
        binding.validate_airline_semantic_to_contract_binding_report_v01(report),
        binding.REASON_HOLD_CONTRACT_BINDING_MISMATCH,
    )


def test_snapshot_id_mismatch_with_true_flag_rejected() -> None:
    bundle = _base(binding.OFFER_A_ID)
    rows = (
        replace(
            bundle["binding_report"].causal_binding_rows[0],
            target_snapshot_id="other",
            snapshot_match=True,
        ),
    ) + bundle["binding_report"].causal_binding_rows[1:]
    report = replace(bundle["binding_report"], causal_binding_rows=rows)

    _assert_fails_with(
        binding.validate_airline_semantic_to_contract_binding_report_v01(report),
        binding.REASON_SNAPSHOT_SUBSTITUTION_DETECTED,
    )


def test_semantic_influence_present_false_rejected() -> None:
    bundle = _base(binding.OFFER_A_ID)
    rows = (
        replace(
            bundle["binding_report"].causal_binding_rows[0],
            semantic_influence_present=False,
        ),
    ) + bundle["binding_report"].causal_binding_rows[1:]
    report = replace(bundle["binding_report"], causal_binding_rows=rows)

    _assert_fails_with(
        binding.validate_airline_semantic_to_contract_binding_report_v01(report),
        binding.REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH,
    )


def test_duplicate_binding_row_rejected() -> None:
    bundle = _base(binding.OFFER_A_ID)
    rows = bundle["binding_report"].causal_binding_rows
    report = replace(bundle["binding_report"], causal_binding_rows=rows[:-1] + (rows[0],))

    _assert_fails_with(
        binding.validate_airline_semantic_to_contract_binding_report_v01(report),
        binding.REASON_HOLD_CONTRACT_BINDING_MISMATCH,
    )


def test_extra_binding_row_rejected() -> None:
    bundle = _base(binding.OFFER_A_ID)
    rows = bundle["binding_report"].causal_binding_rows
    report = replace(bundle["binding_report"], causal_binding_rows=rows + (rows[0],))

    _assert_fails_with(
        binding.validate_airline_semantic_to_contract_binding_report_v01(report),
        binding.REASON_HOLD_CONTRACT_BINDING_MISMATCH,
    )


def test_wrong_binding_artifact_type_or_field_rejected() -> None:
    bundle = _base(binding.OFFER_A_ID)
    rows = (
        replace(
            bundle["binding_report"].causal_binding_rows[0],
            source_artifact_type="WrongArtifact",
            source_field="wrong_field",
        ),
    ) + bundle["binding_report"].causal_binding_rows[1:]
    report = replace(bundle["binding_report"], causal_binding_rows=rows)

    _assert_fails_with(
        binding.validate_airline_semantic_to_contract_binding_report_v01(report),
        binding.REASON_HOLD_CONTRACT_BINDING_MISMATCH,
    )


def test_report_selected_offer_id_mismatch_rejected() -> None:
    bundle = _base(binding.OFFER_A_ID)
    report = replace(bundle["binding_report"], selected_offer_id=binding.OFFER_B_ID)

    _assert_fails_with(
        binding.validate_airline_semantic_to_contract_binding_report_v01(report),
        binding.REASON_CANONICAL_SELECTION_LINEAGE_MISMATCH,
    )


def test_semantic_proposal_to_canonical_selection_row_present() -> None:
    bundle = _base(binding.OFFER_A_ID)
    row = _proposal_binding_row(bundle["binding_report"])

    assert row.source_artifact_type == "AirlineSemanticOfferSelectionProposalV01"
    assert row.source_artifact_id == bundle["proposal"].proposal_id
    assert row.source_field == "proposal_id"
    assert row.source_value == bundle["proposal"].proposal_id
    assert row.target_artifact_type == "ValidatedAirlineSemanticSelectionEvidenceV01"
    assert row.target_artifact_id == bundle["evidence"].canonical_selection_id
    assert row.target_field == "source_proposal_id"
    assert row.target_value == bundle["evidence"].source_proposal_id
    assert row.values_match is True
    assert row.snapshot_match is True


def test_semantic_proposal_binding_row_mismatch_rejected_even_when_flag_true() -> None:
    bundle = _base(binding.OFFER_A_ID)
    rows = tuple(
        replace(row, target_value="proposal:forged", values_match=True)
        if row.binding_id == "semantic_proposal_to_canonical_selection"
        else row
        for row in bundle["binding_report"].causal_binding_rows
    )
    report = replace(bundle["binding_report"], causal_binding_rows=rows)

    _assert_fails_with(
        binding.validate_airline_semantic_to_contract_binding_report_v01(report),
        binding.REASON_HOLD_CONTRACT_BINDING_MISMATCH,
    )


def test_changing_upstream_artifact_without_report_change_fails() -> None:
    bundle = _base(binding.OFFER_A_ID)
    proposal = replace(bundle["proposal"], recommended_offer_id=binding.OFFER_B_ID)
    bundle = {**bundle, "proposal": proposal}

    _assert_fails_with(
        _local_chain(bundle),
        binding.REASON_HOLD_CONTRACT_BINDING_MISMATCH,
    )


def test_full_valid_explicit_offer_a_chain_passes_local_model() -> None:
    report = _local_chain(_base(binding.OFFER_A_ID))

    _assert_status(report, binding.STATUS_LOCAL_MODEL_PASS)


def test_full_valid_explicit_offer_b_chain_passes_local_model() -> None:
    report = _local_chain(_base(binding.OFFER_B_ID))

    _assert_status(report, binding.STATUS_LOCAL_MODEL_PASS)


def test_offer_c_chain_fails_at_clientroot() -> None:
    report = _local_chain(_base(binding.OFFER_C_ID))

    _assert_fails_with(
        report,
        binding.REASON_CLIENT_CONSTRAINT_COMPATIBILITY_FAILED,
    )


def test_module_is_under_airline_domain() -> None:
    assert binding.__name__ == (
        "hedgehog.domains.airline.semantic_to_contract_binding_v01"
    )


def test_module_docstring_declares_domain_boundary() -> None:
    doc = binding.__doc__ or ""

    assert "Airline domain causal-binding projection" in doc
    assert "not Hedgehog OS universal kernel/core" in doc
    assert "not an installed Needle" in doc
    assert "No provider or semantic recommender is implemented" in doc
    assert "No corridor execution is implemented" in doc


def test_source_boundary() -> None:
    source = Path(binding.__file__).read_text(encoding="utf-8")

    for token in (
        "demo/",
        "google." + "genai",
        "re" + "quests",
        "url" + "lib",
        "open" + "ai",
        "sub" + "process",
        "import " + "config",
        "provider_adapter",
        "recommended_offer_id=" + "OFFER_A_ID",
        "selected_offer_id=" + "OFFER_A_ID",
        "return " + "OFFER_A_ID",
        "fallback" + " to Offer A",
        "Ledger " + "implementation",
        "Crypto " + "implementation",
        "Replay " + "implementation",
        "prod" + "uction ready",
        "public " + "auditor ready",
    ):
        assert token not in source


def test_no_semantic_recommendation_algorithm_by_preference_mapping() -> None:
    source = Path(binding.__file__).read_text(encoding="utf-8")

    assert "preference_A -> Offer A" not in source
    assert "preference_B -> Offer B" not in source
    assert "soft_preference_priority[0]" not in source
