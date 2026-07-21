from dataclasses import asdict, fields, replace
import json

import pytest

from hedgehog.domains.airline import semantic_provider_canonicalization_v01 as adapter
from hedgehog.domains.airline import semantic_to_contract_binding_v01 as binding
from hedgehog.domains.airline import semantic_to_contract_causal_runtime_v01 as runtime


PROPOSER_FIELDS = (
    "recommended_offer_id",
    "ranked_offer_ids",
    "decision_factors",
    "preference_matches",
    "uncertainty_notes",
    "requires_root_review",
    "semantic_summary",
)
REVIEWER_FIELDS = (
    "supports_proposed_offer",
    "semantic_factors",
    "blocking_conflicts",
)


def _context(actor_id: str, proposed_offer_id: str = ""):
    bsep = binding.build_valid_airline_bsep_projection_ref_v01()
    constraints = binding.build_client_constraints_preference_a_v01()
    snapshot = binding.build_airline_candidate_snapshot_v01()
    selection = binding.build_selection_input_v01(bsep, constraints, snapshot)
    request = runtime.build_airline_semantic_actor_request_v01(
        actor_id=actor_id,
        selection_input=selection,
        constraints=constraints,
        snapshot=snapshot,
        proposed_offer_id=proposed_offer_id,
    )
    return bsep, constraints, snapshot, selection, request


def _proposer_payload() -> dict[str, object]:
    return {
        "recommended_offer_id": binding.OFFER_A_ID,
        "ranked_offer_ids": [binding.OFFER_A_ID],
        "decision_factors": ["preference_a_exact_fit"],
        "preference_matches": ["lower_price", "window_seat"],
        "uncertainty_notes": ["requires_client_root_review"],
        "requires_root_review": True,
        "semantic_summary": "Offer A best matches the declared preferences.",
    }


def _reviewer_payload(*, support: bool = True) -> dict[str, object]:
    return {
        "supports_proposed_offer": support,
        "semantic_factors": ["offer_a_is_hard_compatible"],
        "blocking_conflicts": [] if support else ["reviewer_detected_conflict"],
    }


def _canonicalize(actor_id: str, payload: dict[str, object], proposed: str = ""):
    bsep, constraints, snapshot, selection, request = _context(actor_id, proposed)
    result = adapter.canonicalize_airline_causal_provider_response_v01(
        raw_provider_response=json.dumps(payload, sort_keys=True),
        request=request,
        bsep_projection=bsep,
        constraints=constraints,
        selection_input=selection,
        snapshot=snapshot,
    )
    return result, request


def test_public_semantic_field_contracts_are_exact():
    assert adapter.PROPOSER_SEMANTIC_FIELDS == PROPOSER_FIELDS
    assert adapter.REVIEWER_SEMANTIC_FIELDS == REVIEWER_FIELDS
    assert tuple(field.name for field in fields(adapter.AirlineCausalProposerSemanticEnvelopeV01)) == PROPOSER_FIELDS
    assert tuple(field.name for field in fields(adapter.AirlineCausalReviewerSemanticEnvelopeV01)) == REVIEWER_FIELDS


def test_proposer_semantics_are_canonicalized_by_runtime_and_existing_validator():
    result, request = _canonicalize(runtime.ACTOR_ORDER[0], _proposer_payload())
    assert result.final_status == adapter.STATUS_PASS
    proposal = result.runtime_canonical_artifact
    assert type(proposal) is binding.AirlineSemanticOfferSelectionProposalV01
    assert proposal.proposal_id == f"semantic_offer_selection_proposal:{binding.OFFER_A_ID}"
    assert proposal.transaction_id == request.transaction_id
    assert proposal.actor_id == request.actor_id
    assert proposal.source_candidate_set_digest == request.source_candidate_set_digest
    assert proposal.authority_created is False
    assert proposal.real_world_effects_count == 0


def test_reviewer_semantics_are_canonicalized_with_compatibility_identity():
    actor_id = runtime.ACTOR_ORDER[1]
    result, request = _canonicalize(actor_id, _reviewer_payload(), binding.OFFER_A_ID)
    assert result.final_status == adapter.STATUS_PASS
    response = result.runtime_canonical_artifact
    assert type(response) is runtime.AirlineInjectedReviewerResponseV01
    assert response.response_id == f"{actor_id}_response_001"
    assert response.source_request_id == request.request_id
    assert response.raw_output_used is False
    assert response.authority_created is False


def test_negative_reviewer_semantics_remain_negative_and_are_not_repaired():
    actor_id = runtime.ACTOR_ORDER[1]
    result, _ = _canonicalize(actor_id, _reviewer_payload(support=False), binding.OFFER_A_ID)
    assert result.semantic_validation.validation_status == adapter.STATUS_PASS
    assert result.final_status == adapter.STATUS_FAIL_CLOSED
    assert type(result.runtime_canonical_artifact) is runtime.AirlineInjectedReviewerResponseV01
    assert result.runtime_canonical_artifact.supports_proposed_offer is False
    assert result.runtime_canonical_artifact.validation_status == binding.STATUS_FAIL_CLOSED
    plain = adapter.airline_semantic_canonicalization_result_to_plain_dict_v01(result)
    assert plain["extracted_semantic_object"]["supports_proposed_offer"] is False
    assert plain["extracted_semantic_object"]["blocking_conflicts"] == (
        "reviewer_detected_conflict",
    )


@pytest.mark.parametrize("missing", PROPOSER_FIELDS)
def test_every_proposer_field_is_mandatory(missing):
    payload = _proposer_payload()
    payload.pop(missing)
    result, _ = _canonicalize(runtime.ACTOR_ORDER[0], payload)
    assert result.final_status == adapter.STATUS_FAIL_CLOSED
    assert result.runtime_canonical_artifact is None


@pytest.mark.parametrize("missing", REVIEWER_FIELDS)
def test_every_reviewer_field_is_mandatory(missing):
    payload = _reviewer_payload()
    payload.pop(missing)
    result, _ = _canonicalize(runtime.ACTOR_ORDER[1], payload, binding.OFFER_A_ID)
    assert result.final_status == adapter.STATUS_FAIL_CLOSED


@pytest.mark.parametrize(
    "mutation",
    (
        lambda value: value.update({"transaction_id": binding.TRANSACTION_ID}),
        lambda value: value.update({"actor_id": runtime.ACTOR_ORDER[0]}),
        lambda value: value.update({"source_candidate_set_digest": "0" * 64}),
        lambda value: value.update({"authority_created": False}),
        lambda value: value.update({"real_world_effects_count": 0}),
        lambda value: value.update({"raw_prompt": "private"}),
    ),
)
def test_provider_mechanical_or_private_fields_are_rejected(mutation):
    payload = _proposer_payload()
    mutation(payload)
    result, _ = _canonicalize(runtime.ACTOR_ORDER[0], payload)
    assert result.final_status == adapter.STATUS_FAIL_CLOSED


def test_reviewer_uncertainty_notes_is_unknown_not_dropped():
    payload = _reviewer_payload()
    payload["uncertainty_notes"] = ["not part of the frozen reviewer contract"]
    result, _ = _canonicalize(runtime.ACTOR_ORDER[1], payload, binding.OFFER_A_ID)
    assert result.final_status == adapter.STATUS_FAIL_CLOSED
    assert result.extracted_semantic_object is None


@pytest.mark.parametrize(
    "ranked",
    (
        [],
        [binding.OFFER_A_ID, binding.OFFER_A_ID],
        [binding.OFFER_B_ID],
        ["unknown_offer"],
    ),
)
def test_ranking_must_be_unique_include_recommendation_and_be_hard_compatible(ranked):
    payload = _proposer_payload()
    payload["ranked_offer_ids"] = ranked
    result, _ = _canonicalize(runtime.ACTOR_ORDER[0], payload)
    assert result.final_status == adapter.STATUS_FAIL_CLOSED


def test_ranking_may_include_every_hard_compatible_offer_in_semantic_order():
    payload = _proposer_payload()
    payload["ranked_offer_ids"] = [binding.OFFER_A_ID, binding.OFFER_B_ID]
    result, _ = _canonicalize(runtime.ACTOR_ORDER[0], payload)
    assert result.final_status == adapter.STATUS_PASS


@pytest.mark.parametrize(
    "field,value",
    (
        ("requires_root_review", 1),
        ("requires_root_review", False),
        ("recommended_offer_id", " Offer A "),
        ("decision_factors", [True]),
        ("preference_matches", []),
        ("semantic_summary", ""),
    ),
)
def test_exact_types_and_values_are_required_without_repair(field, value):
    payload = _proposer_payload()
    payload[field] = value
    result, _ = _canonicalize(runtime.ACTOR_ORDER[0], payload)
    assert result.final_status == adapter.STATUS_FAIL_CLOSED


def test_trusted_request_lineage_is_rebuilt_and_compared_exactly():
    bsep, constraints, snapshot, selection, request = _context(runtime.ACTOR_ORDER[0])
    forged = replace(request, source_candidate_set_digest="0" * 64)
    result = adapter.canonicalize_airline_causal_provider_response_v01(
        raw_provider_response=json.dumps(_proposer_payload()),
        request=forged,
        bsep_projection=bsep,
        constraints=constraints,
        selection_input=selection,
        snapshot=snapshot,
    )
    assert result.semantic_validation.reason_codes == (
        adapter.REASON_TRUSTED_CONTEXT_INVALID,
    )
    assert result.runtime_canonical_artifact is None


@pytest.mark.parametrize("actor_id", runtime.ACTOR_ORDER)
def test_field_ownership_is_complete_disjoint_and_actor_specific(actor_id):
    if actor_id == runtime.ACTOR_ORDER[0]:
        result, _ = _canonicalize(actor_id, _proposer_payload())
        expected_provider = PROPOSER_FIELDS
    else:
        result, _ = _canonicalize(actor_id, _reviewer_payload(), binding.OFFER_A_ID)
        expected_provider = REVIEWER_FIELDS
    assert result.final_status == adapter.STATUS_PASS
    ownership = result.field_ownership
    assert ownership.provider_field_names == expected_provider
    assert ownership.complete is True
    assert ownership.disjoint is True
    canonical_fields = set(asdict(result.runtime_canonical_artifact))
    assert set(ownership.provider_field_names).union(ownership.runtime_field_names) == canonical_fields
    assert not set(ownership.provider_field_names).intersection(ownership.runtime_field_names)


def test_raw_semantic_canonical_validation_and_provenance_are_separate_and_isolated():
    raw = json.dumps(_proposer_payload(), sort_keys=True)
    bsep, constraints, snapshot, selection, request = _context(runtime.ACTOR_ORDER[0])
    result = adapter.canonicalize_airline_causal_provider_response_v01(
        raw_provider_response=raw,
        request=request,
        bsep_projection=bsep,
        constraints=constraints,
        selection_input=selection,
        snapshot=snapshot,
    )
    assert result.raw_provider_response == raw
    assert type(result.extracted_semantic_object) is adapter.AirlineCausalProposerSemanticEnvelopeV01
    assert type(result.runtime_canonical_artifact) is binding.AirlineSemanticOfferSelectionProposalV01
    assert type(result.semantic_validation) is adapter.AirlineSemanticEnvelopeValidationV01
    assert type(result.canonical_validation) is adapter.AirlineSemanticCanonicalValidationV01
    assert type(result.field_ownership) is adapter.AirlineSemanticFieldOwnershipV01
    first = adapter.airline_semantic_canonicalization_result_to_plain_dict_v01(result)
    first["extracted_semantic_object"]["ranked_offer_ids"] = ["forged"]
    second = adapter.airline_semantic_canonicalization_result_to_plain_dict_v01(result)
    assert second["extracted_semantic_object"]["ranked_offer_ids"] == (
        binding.OFFER_A_ID,
    )


def test_equal_inputs_are_deterministic():
    first, _ = _canonicalize(runtime.ACTOR_ORDER[0], _proposer_payload())
    second, _ = _canonicalize(runtime.ACTOR_ORDER[0], _proposer_payload())
    assert first == second


@pytest.mark.parametrize(
    "raw",
    (
        "",
        "[]",
        "{not-json}",
        '{"recommended_offer_id":"a","recommended_offer_id":"b"}',
        '{"value":NaN}',
    ),
)
def test_malformed_or_non_object_raw_response_fails_closed(raw):
    bsep, constraints, snapshot, selection, request = _context(runtime.ACTOR_ORDER[0])
    result = adapter.canonicalize_airline_causal_provider_response_v01(
        raw_provider_response=raw,
        request=request,
        bsep_projection=bsep,
        constraints=constraints,
        selection_input=selection,
        snapshot=snapshot,
    )
    assert result.final_status == adapter.STATUS_FAIL_CLOSED
    assert result.runtime_canonical_artifact is None
    assert result.canonical_validation.reason_codes


def test_literal_lone_surrogate_is_total_and_uses_safe_empty_raw_marker():
    bsep, constraints, snapshot, selection, request = _context(runtime.ACTOR_ORDER[0])
    result = adapter.canonicalize_airline_causal_provider_response_v01(
        raw_provider_response="\ud800",
        request=request,
        bsep_projection=bsep,
        constraints=constraints,
        selection_input=selection,
        snapshot=snapshot,
    )
    assert result.final_status == adapter.STATUS_FAIL_CLOSED
    assert result.raw_provider_response == ""
    assert result.semantic_validation.reason_codes == (
        adapter.REASON_RAW_RESPONSE_INVALID,
    )
    assert result.canonical_validation.reason_codes


@pytest.mark.parametrize(
    "actor_id,proposed,field,index",
    (
        (runtime.ACTOR_ORDER[0], "", "recommended_offer_id", None),
        (runtime.ACTOR_ORDER[0], "", "ranked_offer_ids", 0),
        (runtime.ACTOR_ORDER[0], "", "decision_factors", 0),
        (runtime.ACTOR_ORDER[0], "", "preference_matches", 0),
        (runtime.ACTOR_ORDER[0], "", "uncertainty_notes", 0),
        (runtime.ACTOR_ORDER[0], "", "semantic_summary", None),
        (runtime.ACTOR_ORDER[1], binding.OFFER_A_ID, "semantic_factors", 0),
        (runtime.ACTOR_ORDER[1], binding.OFFER_A_ID, "blocking_conflicts", 0),
    ),
)
def test_json_escaped_lone_surrogate_is_rejected_on_every_semantic_string_surface(
    actor_id,
    proposed,
    field,
    index,
):
    payload = _proposer_payload() if actor_id == runtime.ACTOR_ORDER[0] else _reviewer_payload()
    if index is None:
        payload[field] = "\ud800"
    else:
        payload[field] = ["\ud800"]
    raw = json.dumps(payload, ensure_ascii=True, sort_keys=True)
    bsep, constraints, snapshot, selection, request = _context(actor_id, proposed)
    result = adapter.canonicalize_airline_causal_provider_response_v01(
        raw_provider_response=raw,
        request=request,
        bsep_projection=bsep,
        constraints=constraints,
        selection_input=selection,
        snapshot=snapshot,
    )
    assert result.final_status == adapter.STATUS_FAIL_CLOSED
    assert result.runtime_canonical_artifact is None


@pytest.mark.parametrize("raw", (None, object(), b"{}"))
def test_non_string_raw_provider_result_is_total_and_fail_closed(raw):
    bsep, constraints, snapshot, selection, request = _context(runtime.ACTOR_ORDER[0])
    result = adapter.canonicalize_airline_causal_provider_response_v01(
        raw_provider_response=raw,
        request=request,
        bsep_projection=bsep,
        constraints=constraints,
        selection_input=selection,
        snapshot=snapshot,
    )
    assert result.final_status == adapter.STATUS_FAIL_CLOSED
    assert result.raw_provider_response == ""
    assert result.canonical_validation.reason_codes


def test_unknown_actor_fails_as_trusted_context_before_semantic_parsing():
    bsep, constraints, snapshot, selection, request = _context(runtime.ACTOR_ORDER[0])
    forged = replace(request, actor_id="unknown_causal_actor")
    result = adapter.canonicalize_airline_causal_provider_response_v01(
        raw_provider_response="not-json",
        request=forged,
        bsep_projection=bsep,
        constraints=constraints,
        selection_input=selection,
        snapshot=snapshot,
    )
    assert result.semantic_validation.reason_codes == (
        adapter.REASON_TRUSTED_CONTEXT_INVALID,
    )
    assert result.canonical_validation.reason_codes


def test_malformed_trusted_selection_collection_is_total_and_fail_closed():
    bsep, constraints, snapshot, selection, request = _context(runtime.ACTOR_ORDER[0])
    forged_selection = replace(selection, visible_candidate_ids=(["unhashable"],))
    result = adapter.canonicalize_airline_causal_provider_response_v01(
        raw_provider_response=json.dumps(_proposer_payload()),
        request=request,
        bsep_projection=bsep,
        constraints=constraints,
        selection_input=forged_selection,
        snapshot=snapshot,
    )
    assert result.semantic_validation.reason_codes == (
        adapter.REASON_TRUSTED_CONTEXT_INVALID,
    )
    assert result.runtime_canonical_artifact is None


@pytest.mark.parametrize("proposed", ("unknown_offer", binding.OFFER_C_ID))
def test_reviewer_proposed_offer_must_be_visible_and_hard_compatible(proposed):
    bsep, constraints, snapshot, selection, request = _context(
        runtime.ACTOR_ORDER[1],
        proposed,
    )
    result = adapter.canonicalize_airline_causal_provider_response_v01(
        raw_provider_response=json.dumps(_reviewer_payload()),
        request=request,
        bsep_projection=bsep,
        constraints=constraints,
        selection_input=selection,
        snapshot=snapshot,
    )
    assert result.semantic_validation.reason_codes == (
        adapter.REASON_TRUSTED_CONTEXT_INVALID,
    )
    assert result.runtime_canonical_artifact is None


def test_raw_response_over_byte_ceiling_fails_closed():
    bsep, constraints, snapshot, selection, request = _context(runtime.ACTOR_ORDER[0])
    result = adapter.canonicalize_airline_causal_provider_response_v01(
        raw_provider_response="x" * 16385,
        request=request,
        bsep_projection=bsep,
        constraints=constraints,
        selection_input=selection,
        snapshot=snapshot,
    )
    assert result.semantic_validation.reason_codes == (
        adapter.REASON_RAW_RESPONSE_INVALID,
    )


@pytest.mark.parametrize(
    "field,value",
    (
        ("semantic_summary", "x" * 2049),
        ("decision_factors", [f"factor_{index}" for index in range(33)]),
    ),
)
def test_semantic_string_and_collection_bounds_fail_closed(field, value):
    payload = _proposer_payload()
    payload[field] = value
    result, _ = _canonicalize(runtime.ACTOR_ORDER[0], payload)
    assert result.final_status == adapter.STATUS_FAIL_CLOSED


@pytest.mark.parametrize("unsafe", ("Cafe\u0301", "factor\u200bhidden", "line\ncontrol"))
def test_non_nfc_format_and_control_semantic_strings_fail_closed(unsafe):
    payload = _proposer_payload()
    payload["decision_factors"] = [unsafe]
    result, _ = _canonicalize(runtime.ACTOR_ORDER[0], payload)
    assert result.final_status == adapter.STATUS_FAIL_CLOSED
    assert result.runtime_canonical_artifact is None


@pytest.mark.parametrize(
    "field",
    (
        "transaction_id",
        "actor_id",
        "source_request_id",
        "raw_prompt",
        "private_key",
        "authority_created",
        "permission_created",
        "payment_created",
        "final_output_created",
        "real_world_effects_count",
    ),
)
def test_reviewer_mechanical_private_authority_and_effect_fields_are_rejected(field):
    payload = _reviewer_payload()
    payload[field] = False
    result, _ = _canonicalize(
        runtime.ACTOR_ORDER[1],
        payload,
        binding.OFFER_A_ID,
    )
    assert result.final_status == adapter.STATUS_FAIL_CLOSED
    assert result.extracted_semantic_object is None


def test_hard_incompatible_proposer_recommendation_fails_with_consistent_ranking():
    payload = _proposer_payload()
    payload["recommended_offer_id"] = binding.OFFER_C_ID
    payload["ranked_offer_ids"] = [binding.OFFER_C_ID]
    result, _ = _canonicalize(runtime.ACTOR_ORDER[0], payload)
    assert result.final_status == adapter.STATUS_FAIL_CLOSED
    assert result.semantic_validation.reason_codes == (
        adapter.REASON_SEMANTIC_OFFER_INVALID,
    )


def test_module_has_no_transport_filesystem_or_demo_dependency():
    source = open(adapter.__file__, encoding="utf-8").read()
    for forbidden in (
        "from demo",
        "import demo",
        "pathlib",
        "subprocess",
        "requests",
        "urllib",
        "socket",
        "google",
        "gemini",
    ):
        assert forbidden not in source
