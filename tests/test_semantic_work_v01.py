from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from dataclasses import FrozenInstanceError, fields, is_dataclass, replace
import ast
import inspect
import json
from pathlib import Path
from typing import Any

import jsonschema
import pytest

from demo import run_living_gauntlet_v01 as gauntlet
import hedgehog.kernel as kernel
from hedgehog.kernel import semantic_work_v01 as semantic


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "hedgehog/kernel/semantic_work_v01.py"
SCHEMA_PATH = ROOT / "schemas/semantic_work_v01.schema.json"

EXPECTED_FIELDS = {
    "SemanticWorkRequestV01": (
        "request_id",
        "transaction_id",
        "target_root_id",
        "runtime_topology_ref",
        "bounded_context_refs",
        "permitted_actor_ids",
        "permitted_contribution_modes",
        "requested_subjects",
        "required_evidence_classes",
        "forbidden_claims",
    ),
    "EvidenceBindingV01": (
        "evidence_id",
        "evidence_ref",
        "evidence_class",
        "source_component_id",
        "provenance_ref",
        "evidence_state",
    ),
    "ConstraintBindingV01": (
        "constraint_id",
        "subject",
        "predicate",
        "object_or_value",
        "source_ref",
        "constraint_class",
        "evaluation_state",
    ),
    "UncertaintyBindingV01": (
        "uncertainty_id",
        "claim_id",
        "uncertainty_kind",
        "statement",
        "confidence_micros",
        "source_ref",
    ),
    "NormalizedClaimV01": (
        "claim_id",
        "subject",
        "predicate",
        "object_or_value",
        "time_envelope_ref",
        "provenance_refs",
        "evidence_refs",
        "confidence_micros",
        "source_role",
        "source_mode",
        "authority_class",
    ),
    "ActorContributionV01": (
        "contribution_id",
        "request_id",
        "actor_id",
        "actor_role",
        "contribution_mode",
        "bsep_projection_ref",
        "scope",
        "bounded_context_refs",
        "claims",
        "evidence_bindings",
        "constraint_bindings",
        "uncertainty_bindings",
        "requested_validators",
        "forbidden_claims_observed",
    ),
    "ConflictSetV01": (
        "conflict_set_id",
        "subject",
        "predicate",
        "claim_ids",
        "conflicting_values",
        "source_modes",
        "resolution_state",
    ),
    "SynthesisProposalV01": (
        "proposal_id",
        "request_id",
        "source_contribution_ids",
        "normalized_claims",
        "conflict_sets",
        "missing_evidence_refs",
        "contribution_modes",
        "requested_validators",
        "synthesis_summary",
        "authority_class",
        "root_review_required",
    ),
    "RootReviewPacketV01": (
        "packet_id",
        "request_id",
        "transaction_id",
        "target_root_id",
        "runtime_topology_ref",
        "synthesis_proposal",
        "contribution_ids",
        "conflict_set_ids",
        "missing_evidence_refs",
        "required_validator_ids",
        "review_state",
        "authority_class",
        "root_decision_created",
        "permission_created",
        "final_output_created",
    ),
}
PUBLIC_FUNCTIONS = (
    "build_semantic_work_request_v01",
    "build_evidence_binding_v01",
    "build_constraint_binding_v01",
    "build_uncertainty_binding_v01",
    "build_normalized_claim_v01",
    "build_actor_contribution_v01",
    "build_root_review_packet_from_contributions_v01",
    "validate_semantic_work_request_v01",
    "validate_actor_contribution_v01",
    "validate_root_review_packet_v01",
    "semantic_work_to_plain_dict_v01",
)
COMMITTED_ALL = (
    "CanonicalArtifactRefV01",
    "ArtifactDependencyEdgeV01",
    "RootOwnershipBindingV01",
    "EvidenceClassBindingV01",
    "AuthorityClassBindingV01",
    "SealProfileV01",
    "ArtifactManifestV01",
    "SealVerificationResultV01",
    "ReplayVerificationResultV01",
    "build_default_seal_profile_v01",
    "canonical_json_bytes_v01",
    "domain_separated_sha256_hex_v01",
    "build_canonical_artifact_ref_v01",
    "build_artifact_manifest_v01",
    "verify_artifact_manifest_v01",
    "verify_artifact_replay_v01",
    "artifact_manifest_to_plain_dict_v01",
    "seal_verification_result_to_plain_dict_v01",
    "replay_verification_result_to_plain_dict_v01",
)


@pytest.fixture
def bundle() -> tuple[Any, tuple[Any, ...], tuple[Any, ...], Any]:
    return gauntlet._build_semantic_work_fixture_v01()


def _request_kwargs(request: semantic.SemanticWorkRequestV01) -> dict[str, object]:
    return {field.name: getattr(request, field.name) for field in fields(request)}


def _claim(value: object = "value", **changes: object) -> semantic.NormalizedClaimV01:
    kwargs: dict[str, object] = {
        "claim_id": "claim:test:001",
        "subject": "resource:alpha",
        "predicate": "state",
        "object_or_value": value,
        "time_envelope_ref": "time:test:001",
        "provenance_refs": ("provenance:test:001",),
        "evidence_refs": ("evidence:test:001",),
        "confidence_micros": 500_000,
        "source_role": "deterministic_runtime",
        "source_mode": "DETERMINISTIC",
    }
    kwargs.update(changes)
    return semantic.build_normalized_claim_v01(**kwargs)  # type: ignore[arg-type]


def _claim_from_existing(
    claim: semantic.NormalizedClaimV01,
    value: object,
) -> semantic.NormalizedClaimV01:
    return semantic.build_normalized_claim_v01(
        claim_id=claim.claim_id,
        subject=claim.subject,
        predicate=claim.predicate,
        object_or_value=value,
        time_envelope_ref=claim.time_envelope_ref,
        provenance_refs=claim.provenance_refs,
        evidence_refs=claim.evidence_refs,
        confidence_micros=claim.confidence_micros,
        source_role=claim.source_role,
        source_mode=claim.source_mode,
    )


def _packet_variant(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any],
    *,
    conflict: bool,
    missing: bool,
) -> semantic.RootReviewPacketV01:
    request, contributions, profiles, _ = bundle
    changed = list(contributions)
    if not conflict:
        local = changed[3]
        local_claim = replace(local.claims[0], object_or_value="ready")
        changed[3] = replace(local, claims=(local_claim,))
    if not missing:
        child = changed[4]
        present = replace(
            child.evidence_bindings[0],
            evidence_state=semantic.EVIDENCE_STATE_PRESENT,
        )
        changed[4] = replace(child, evidence_bindings=(present,))
    return semantic.build_root_review_packet_from_contributions_v01(
        request=request,
        contributions=tuple(changed),
        trust_profiles=profiles,
    )


@pytest.mark.parametrize("type_name", tuple(EXPECTED_FIELDS))
def test_each_public_dataclass_has_exact_field_order(type_name: str) -> None:
    value = getattr(semantic, type_name)
    assert tuple(field.name for field in fields(value)) == EXPECTED_FIELDS[type_name]


@pytest.mark.parametrize("type_name", tuple(EXPECTED_FIELDS))
def test_each_public_dataclass_is_frozen(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any], type_name: str
) -> None:
    request, contributions, _, packet = bundle
    examples = {
        "SemanticWorkRequestV01": request,
        "EvidenceBindingV01": contributions[0].evidence_bindings[0],
        "ConstraintBindingV01": contributions[0].constraint_bindings[0],
        "UncertaintyBindingV01": contributions[3].uncertainty_bindings[0],
        "NormalizedClaimV01": contributions[0].claims[0],
        "ActorContributionV01": contributions[0],
        "ConflictSetV01": packet.synthesis_proposal.conflict_sets[0],
        "SynthesisProposalV01": packet.synthesis_proposal,
        "RootReviewPacketV01": packet,
    }
    example = examples[type_name]
    with pytest.raises(FrozenInstanceError):
        setattr(example, fields(example)[0].name, "changed")


def test_public_dataclass_and_function_sets_are_exact() -> None:
    dataclasses = {
        name
        for name, value in vars(semantic).items()
        if not name.startswith("_")
        and inspect.isclass(value)
        and is_dataclass(value)
        and value.__module__ == semantic.__name__
    }
    functions = {
        name
        for name, value in vars(semantic).items()
        if not name.startswith("_")
        and inspect.isfunction(value)
        and value.__module__ == semantic.__name__
    }
    assert dataclasses == set(EXPECTED_FIELDS)
    assert functions == set(PUBLIC_FUNCTIONS)


@pytest.mark.parametrize(
    "attribute", (*tuple(EXPECTED_FIELDS), *PUBLIC_FUNCTIONS)
)
def test_package_exposes_g1b1_semantic_attributes_directly(attribute: str) -> None:
    assert getattr(kernel, attribute) is getattr(semantic, attribute)


def test_package_all_remains_unchanged() -> None:
    assert kernel.__all__ == COMMITTED_ALL


def test_valid_all_five_mode_request_passes(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any]
) -> None:
    request = bundle[0]
    assert request.permitted_contribution_modes == semantic.CONTRIBUTION_MODES
    assert semantic.validate_semantic_work_request_v01(request) == ()


@pytest.mark.parametrize(
    ("field_name", "bad_value", "reason"),
    (
        ("request_id", "", "semantic_work_request_invalid"),
        ("request_id", 1, "semantic_work_request_invalid"),
        ("request_id", "\ud800", "semantic_work_request_invalid"),
        ("transaction_id", "", "semantic_work_request_invalid"),
        ("transaction_id", None, "semantic_work_request_invalid"),
        ("transaction_id", "\udfff", "semantic_work_request_invalid"),
        ("target_root_id", "", "semantic_work_request_invalid"),
        ("target_root_id", False, "semantic_work_request_invalid"),
        ("target_root_id", "\ud800", "semantic_work_request_invalid"),
        ("runtime_topology_ref", "", "runtime_topology_ref_invalid"),
        ("runtime_topology_ref", object(), "runtime_topology_ref_invalid"),
        ("runtime_topology_ref", "\udfff", "runtime_topology_ref_invalid"),
    ),
)
def test_request_text_field_mutations_fail_closed(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any],
    field_name: str,
    bad_value: object,
    reason: str,
) -> None:
    malformed = replace(bundle[0], **{field_name: bad_value})
    assert reason in semantic.validate_semantic_work_request_v01(malformed)


@pytest.mark.parametrize(
    ("field_name", "bad_value", "reason"),
    (
        ("bounded_context_refs", [], "semantic_work_request_context_invalid"),
        ("bounded_context_refs", (), "semantic_work_request_context_invalid"),
        (
            "bounded_context_refs",
            ("context:1", "context:1"),
            "semantic_work_request_context_invalid",
        ),
        ("permitted_actor_ids", [], "semantic_work_request_actor_ids_invalid"),
        ("permitted_actor_ids", (), "semantic_work_request_actor_ids_invalid"),
        (
            "permitted_actor_ids",
            ("actor:1", "actor:1"),
            "semantic_work_request_actor_ids_invalid",
        ),
        ("permitted_contribution_modes", [], "semantic_work_request_modes_invalid"),
        ("permitted_contribution_modes", (), "semantic_work_request_modes_invalid"),
        (
            "permitted_contribution_modes",
            ("DETERMINISTIC", "DETERMINISTIC"),
            "semantic_work_request_modes_invalid",
        ),
        (
            "permitted_contribution_modes",
            ("UNKNOWN",),
            "semantic_work_request_modes_invalid",
        ),
        (
            "permitted_contribution_modes",
            tuple(reversed(semantic.CONTRIBUTION_MODES)),
            "semantic_work_request_modes_invalid",
        ),
        ("requested_subjects", [], "semantic_work_request_subjects_invalid"),
        ("requested_subjects", (), "semantic_work_request_subjects_invalid"),
        (
            "requested_subjects",
            ("resource:alpha", "resource:alpha"),
            "semantic_work_request_subjects_invalid",
        ),
        (
            "required_evidence_classes",
            [],
            "semantic_work_request_evidence_classes_invalid",
        ),
        (
            "required_evidence_classes",
            (),
            "semantic_work_request_evidence_classes_invalid",
        ),
        (
            "forbidden_claims",
            [],
            "semantic_work_request_forbidden_claims_invalid",
        ),
        (
            "forbidden_claims",
            (),
            "semantic_work_request_forbidden_claims_invalid",
        ),
    ),
)
def test_request_tuple_contract_mutations_fail_closed(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any],
    field_name: str,
    bad_value: object,
    reason: str,
) -> None:
    malformed = replace(bundle[0], **{field_name: bad_value})
    assert reason in semantic.validate_semantic_work_request_v01(malformed)


@pytest.mark.parametrize(
    "value",
    (
        None,
        True,
        7,
        1.25,
        "text",
        "Δ",
        [1, {"nested": [True, None]}],
        {"b": 2, "a": [1, 2]},
        ("array", 3),
    ),
)
def test_json_values_freeze_and_project_as_canonical_json(value: object) -> None:
    claim = _claim(value)
    first = semantic.semantic_work_to_plain_dict_v01(claim)
    second = semantic.semantic_work_to_plain_dict_v01(claim)
    assert first == second
    json.dumps(first, allow_nan=False, ensure_ascii=False)
    assert "_FrozenJSONObject" not in repr(first)


@pytest.mark.parametrize(
    "value",
    (
        float("nan"),
        float("inf"),
        float("-inf"),
        b"bytes",
        bytearray(b"bytes"),
        memoryview(b"bytes"),
        {1: "bad"},
        object(),
        {"bad": "\ud800"},
    ),
)
def test_invalid_json_values_are_rejected_with_stable_reason(value: object) -> None:
    with pytest.raises(ValueError, match="^claim_contract_invalid$") as exc:
        _claim(value)
    assert exc.value.__cause__ is None


def test_cyclic_json_value_is_rejected() -> None:
    value: list[object] = []
    value.append(value)
    with pytest.raises(ValueError, match="^claim_contract_invalid$"):
        _claim(value)


def test_hostile_mapping_is_rejected_without_original_error() -> None:
    class Hostile(dict[str, object]):
        def items(self) -> object:
            raise OSError("caller payload")

    with pytest.raises(ValueError, match="^claim_contract_invalid$") as exc:
        _claim(Hostile())
    assert exc.value.__cause__ is None
    assert "caller payload" not in str(exc.value)


def test_caller_json_mutation_does_not_change_claim_projection() -> None:
    value = {"nested": [1, 2]}
    claim = _claim(value)
    before = semantic.semantic_work_to_plain_dict_v01(claim)
    value["nested"].append(3)
    after = semantic.semantic_work_to_plain_dict_v01(claim)
    assert before == after
    before["object_or_value"]["nested"].append(4)  # type: ignore[index,union-attr]
    assert semantic.semantic_work_to_plain_dict_v01(claim) == after


@pytest.mark.parametrize("state", semantic.EVIDENCE_STATES)
def test_all_evidence_states_build_and_project(state: str) -> None:
    binding = semantic.build_evidence_binding_v01(
        evidence_id="evidence:test:001",
        evidence_ref="evidence-ref:test:001",
        evidence_class="OBSERVATION",
        source_component_id="actor:test:001",
        provenance_ref="provenance:test:001",
        evidence_state=state,
    )
    assert semantic.semantic_work_to_plain_dict_v01(binding)["evidence_state"] == state


@pytest.mark.parametrize(
    ("field_name", "bad_value"),
    (
        ("evidence_id", ""),
        ("evidence_ref", 1),
        ("evidence_class", ""),
        ("source_component_id", "\ud800"),
        ("provenance_ref", None),
        ("evidence_state", "UNKNOWN"),
    ),
)
def test_malformed_evidence_binding_is_rejected(
    field_name: str, bad_value: object
) -> None:
    kwargs = {
        "evidence_id": "evidence:test:001",
        "evidence_ref": "evidence-ref:test:001",
        "evidence_class": "OBSERVATION",
        "source_component_id": "actor:test:001",
        "provenance_ref": "provenance:test:001",
        "evidence_state": "PRESENT",
    }
    kwargs[field_name] = bad_value
    with pytest.raises(ValueError, match="^evidence_binding_invalid$"):
        semantic.build_evidence_binding_v01(**kwargs)  # type: ignore[arg-type]


@pytest.mark.parametrize("constraint_class", semantic.CONSTRAINT_CLASSES)
@pytest.mark.parametrize("evaluation_state", semantic.CONSTRAINT_EVALUATION_STATES)
def test_constraint_class_and_state_matrix_builds(
    constraint_class: str, evaluation_state: str
) -> None:
    binding = semantic.build_constraint_binding_v01(
        constraint_id="constraint:test:001",
        subject="resource:alpha",
        predicate="allowed",
        object_or_value={"value": True},
        source_ref="policy:test:001",
        constraint_class=constraint_class,
        evaluation_state=evaluation_state,
    )
    projected = semantic.semantic_work_to_plain_dict_v01(binding)
    assert projected["constraint_class"] == constraint_class
    assert projected["evaluation_state"] == evaluation_state


@pytest.mark.parametrize(
    ("constraint_class", "evaluation_state", "value"),
    (
        ("UNKNOWN", "SATISFIED", True),
        ("HARD", "INVALID", True),
        ("SOFT", "UNKNOWN", object()),
    ),
)
def test_invalid_constraint_contract_fails_closed(
    constraint_class: str, evaluation_state: str, value: object
) -> None:
    with pytest.raises(ValueError, match="^constraint_binding_invalid$"):
        semantic.build_constraint_binding_v01(
            constraint_id="constraint:test:001",
            subject="resource:alpha",
            predicate="allowed",
            object_or_value=value,
            source_ref="policy:test:001",
            constraint_class=constraint_class,
            evaluation_state=evaluation_state,
        )


@pytest.mark.parametrize("confidence", (0, 1, 500_000, 999_999, 1_000_000))
def test_uncertainty_confidence_boundaries_are_accepted(confidence: int) -> None:
    value = semantic.build_uncertainty_binding_v01(
        uncertainty_id="uncertainty:test:001",
        claim_id="claim:test:001",
        uncertainty_kind="bounded",
        statement="requires review",
        confidence_micros=confidence,
        source_ref="source:test:001",
    )
    assert value.confidence_micros == confidence


@pytest.mark.parametrize("confidence", (True, False, -1, 1_000_001, 1.0, "1"))
def test_uncertainty_confidence_invalid_values_are_rejected(confidence: object) -> None:
    with pytest.raises(ValueError, match="^uncertainty_binding_invalid$"):
        semantic.build_uncertainty_binding_v01(
            uncertainty_id="uncertainty:test:001",
            claim_id="claim:test:001",
            uncertainty_kind="bounded",
            statement="requires review",
            confidence_micros=confidence,  # type: ignore[arg-type]
            source_ref="source:test:001",
        )


@pytest.mark.parametrize("index", range(5))
def test_all_five_contribution_modes_validate(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any], index: int
) -> None:
    request, contributions, profiles, _ = bundle
    contribution = contributions[index]
    assert contribution.contribution_mode == semantic.CONTRIBUTION_MODES[index]
    assert semantic.validate_actor_contribution_v01(
        request=request,
        contribution=contribution,
        trust_profiles=profiles,
    ) == ()


@pytest.mark.parametrize("index", range(5))
def test_wrong_role_for_each_contribution_mode_fails(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any], index: int
) -> None:
    request, contributions, profiles, _ = bundle
    contribution = replace(contributions[index], actor_role="orchestrator")
    errors = semantic.validate_actor_contribution_v01(
        request=request,
        contribution=contribution,
        trust_profiles=profiles,
    )
    assert "contribution_mode_role_mismatch" in errors


@pytest.mark.parametrize(
    "forbidden_role",
    (
        "root",
        "effect_firewall",
        "corridor_adapter",
        "receipt",
        "ledger",
        "crypto",
        "replay",
        "renderer_showcase",
    ),
)
def test_forbidden_actor_roles_cannot_contribute(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any], forbidden_role: str
) -> None:
    request, contributions, profiles, _ = bundle
    contribution = replace(contributions[0], actor_role=forbidden_role)
    errors = semantic.validate_actor_contribution_v01(
        request=request,
        contribution=contribution,
        trust_profiles=profiles,
    )
    assert "semantic_actor_authority_escalation" in errors


@pytest.mark.parametrize(
    ("mutation", "reason"),
    (
        (lambda item: replace(item, request_id="wrong"), "request_binding_mismatch"),
        (lambda item: replace(item, actor_id="actor:unknown"), "actor_not_permitted"),
        (lambda item: replace(item, contribution_mode="UNKNOWN"), "contribution_mode_unknown"),
        (
            lambda item: replace(item, bounded_context_refs=("context:expanded",)),
            "bounded_context_violation",
        ),
        (lambda item: replace(item, claims=()), "claim_contract_invalid"),
        (
            lambda item: replace(item, forbidden_claims_observed=("permission",)),
            "forbidden_claim_observed",
        ),
        (
            lambda item: replace(
                item,
                claims=(replace(item.claims[0], subject="resource:unknown"),),
            ),
            "claim_subject_not_requested",
        ),
        (
            lambda item: replace(
                item,
                claims=(replace(item.claims[0], authority_class="ROOT"),),
            ),
            "claim_authority_forbidden",
        ),
    ),
)
def test_contribution_boundary_mutations_fail_with_expected_reason(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any],
    mutation: object,
    reason: str,
) -> None:
    request, contributions, profiles, _ = bundle
    malformed = mutation(contributions[1])  # type: ignore[operator]
    errors = semantic.validate_actor_contribution_v01(
        request=request,
        contribution=malformed,
        trust_profiles=profiles,
    )
    assert reason in errors


def test_unbound_and_rejected_evidence_do_not_satisfy_claim(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any]
) -> None:
    request, contributions, profiles, _ = bundle
    original = contributions[0]
    unbound = replace(original, evidence_bindings=())
    assert "evidence_binding_invalid" in semantic.validate_actor_contribution_v01(
        request=request, contribution=unbound, trust_profiles=profiles
    )
    rejected_binding = replace(
        original.evidence_bindings[0], evidence_state=semantic.EVIDENCE_STATE_REJECTED
    )
    rejected = replace(original, evidence_bindings=(rejected_binding,))
    assert "evidence_ref_unbound" in semantic.validate_actor_contribution_v01(
        request=request, contribution=rejected, trust_profiles=profiles
    )


def test_uncertainty_claim_reference_must_resolve(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any]
) -> None:
    request, contributions, profiles, _ = bundle
    local = contributions[3]
    uncertainty = replace(local.uncertainty_bindings[0], claim_id="claim:missing")
    malformed = replace(local, uncertainty_bindings=(uncertainty,))
    assert "uncertainty_claim_ref_invalid" in semantic.validate_actor_contribution_v01(
        request=request, contribution=malformed, trust_profiles=profiles
    )


def test_fixture_deduplicates_only_one_exact_claim(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any]
) -> None:
    _, contributions, _, packet = bundle
    assert sum(len(item.claims) for item in contributions) == 6
    assert len(packet.synthesis_proposal.normalized_claims) == 5
    assert packet.synthesis_proposal.normalized_claims[0] is contributions[0].claims[0]


@pytest.mark.parametrize("changed_field", ("provenance_refs", "confidence_micros"))
def test_nonidentical_semantically_similar_claims_are_preserved(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any], changed_field: str
) -> None:
    request, contributions, profiles, _ = bundle
    changed = list(contributions)
    first = changed[0].claims[0]
    replacement = replace(
        first,
        claim_id="claim:fixture:alpha:state:002",
        **{
            changed_field: ("provenance:alternate",)
            if changed_field == "provenance_refs"
            else 999_999
        },
    )
    changed[0] = replace(changed[0], claims=(first, replacement))
    packet = semantic.build_root_review_packet_from_contributions_v01(
        request=request, contributions=tuple(changed), trust_profiles=profiles
    )
    assert len(packet.synthesis_proposal.normalized_claims) == 6


def test_reused_claim_id_with_different_content_is_rejected(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any]
) -> None:
    request, contributions, profiles, _ = bundle
    changed = list(contributions)
    first = changed[0].claims[0]
    changed[0] = replace(
        changed[0], claims=(first, replace(first, confidence_micros=999_999))
    )
    with pytest.raises(ValueError, match="^claim_contract_invalid$"):
        semantic.build_root_review_packet_from_contributions_v01(
            request=request, contributions=tuple(changed), trust_profiles=profiles
        )


def test_duplicate_contribution_ids_fail_public_packet_validation(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any]
) -> None:
    request, contributions, profiles, packet = bundle
    errors = semantic.validate_root_review_packet_v01(
        request=request,
        contributions=(contributions[0], contributions[0]),
        packet=packet,
        trust_profiles=profiles,
    )
    assert "contribution_set_mismatch" in errors


def test_conflict_preserves_repeated_source_mode_provenance(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any]
) -> None:
    request, contributions, profiles, _ = bundle
    first = replace(contributions[0], claims=(contributions[0].claims[0],))
    second_evidence = replace(
        first.evidence_bindings[0],
        evidence_id="evidence:deterministic:002",
        evidence_ref="evidence:fixture:deterministic:002",
    )
    second_claim = replace(
        first.claims[0],
        claim_id="claim:fixture:alpha:state:002",
        object_or_value="changed",
        evidence_refs=(second_evidence.evidence_id,),
    )
    second = replace(
        first,
        contribution_id="contribution:deterministic:002",
        claims=(second_claim,),
        evidence_bindings=(second_evidence,),
    )
    packet = semantic.build_root_review_packet_from_contributions_v01(
        request=request,
        contributions=(first, second),
        trust_profiles=profiles,
    )
    conflict = packet.synthesis_proposal.conflict_sets[0]
    assert conflict.source_modes == ("DETERMINISTIC", "DETERMINISTIC")
    assert semantic.semantic_work_to_plain_dict_v01(packet)


def test_baseline_conflict_preserves_values_modes_and_root_review(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any]
) -> None:
    conflict = bundle[3].synthesis_proposal.conflict_sets[0]
    projected = semantic.semantic_work_to_plain_dict_v01(conflict)
    assert projected["conflicting_values"] == ["ready", "blocked"]
    assert projected["source_modes"] == ["CLOUD_LLM", "LOCAL_SLM"]
    assert conflict.resolution_state == semantic.CONFLICT_STATE
    assert len(conflict.conflict_set_id) == 64


@pytest.mark.parametrize(
    ("field_name", "new_value"),
    (
        ("object_or_value", "ready"),
        ("subject", "resource:alpha"),
        ("predicate", "alternate"),
        ("time_envelope_ref", "time:alternate"),
    ),
)
def test_claims_outside_same_conflict_key_or_value_do_not_conflict(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any],
    field_name: str,
    new_value: object,
) -> None:
    request, contributions, profiles, _ = bundle
    changed = list(contributions)
    local = changed[3]
    changed[3] = replace(
        local, claims=(replace(local.claims[0], **{field_name: new_value}),)
    )
    packet = semantic.build_root_review_packet_from_contributions_v01(
        request=request, contributions=tuple(changed), trust_profiles=profiles
    )
    assert packet.synthesis_proposal.conflict_sets == ()


def test_missing_evidence_is_visible_in_proposal_and_packet(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any]
) -> None:
    packet = bundle[3]
    assert packet.missing_evidence_refs == ("evidence:fixture:fractal:missing",)
    assert packet.synthesis_proposal.missing_evidence_refs == packet.missing_evidence_refs
    assert packet.synthesis_proposal.root_review_required is True
    assert packet.root_decision_created is False
    assert packet.permission_created is False


@pytest.mark.parametrize(
    ("conflict", "missing", "summary"),
    (
        (False, False, "advisory_claims_ready_for_root_review"),
        (True, False, "advisory_claims_with_visible_conflicts"),
        (False, True, "advisory_claims_with_missing_evidence"),
        (True, True, "advisory_claims_with_visible_conflicts_and_missing_evidence"),
    ),
)
def test_synthesis_summary_matrix_is_exact(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any],
    conflict: bool,
    missing: bool,
    summary: str,
) -> None:
    packet = _packet_variant(bundle, conflict=conflict, missing=missing)
    assert packet.synthesis_proposal.synthesis_summary == summary


def test_synthesis_preserves_mode_and_validator_order(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any]
) -> None:
    proposal = bundle[3].synthesis_proposal
    assert proposal.contribution_modes == semantic.CONTRIBUTION_MODES
    assert proposal.requested_validators == (
        "validator:contract:001",
        "validator:evidence:001",
    )
    assert proposal.authority_class == semantic.SYNTHESIS_AUTHORITY_ADVISORY
    assert proposal.root_review_required is True


def test_packet_identity_and_authority_geometry_is_exact(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any]
) -> None:
    request, contributions, _, packet = bundle
    assert packet.request_id == request.request_id
    assert packet.transaction_id == request.transaction_id
    assert packet.target_root_id == request.target_root_id
    assert packet.runtime_topology_ref == request.runtime_topology_ref
    assert packet.contribution_ids == tuple(item.contribution_id for item in contributions)
    assert packet.review_state == semantic.ROOT_REVIEW_STATE
    assert packet.authority_class == semantic.SYNTHESIS_AUTHORITY_ADVISORY
    assert packet.root_decision_created is False
    assert packet.permission_created is False
    assert packet.final_output_created is False


def test_proposal_and_packet_ids_are_deterministic_and_input_sensitive(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any]
) -> None:
    request, contributions, profiles, packet = bundle
    repeated = semantic.build_root_review_packet_from_contributions_v01(
        request=request, contributions=contributions, trust_profiles=profiles
    )
    assert repeated.synthesis_proposal.proposal_id == packet.synthesis_proposal.proposal_id
    assert repeated.packet_id == packet.packet_id
    changed_request = replace(request, runtime_topology_ref="runtime_topology:changed")
    changed = semantic.build_root_review_packet_from_contributions_v01(
        request=changed_request, contributions=contributions, trust_profiles=profiles
    )
    assert changed.packet_id != packet.packet_id


@pytest.mark.parametrize("field_name", EXPECTED_FIELDS["RootReviewPacketV01"])
def test_every_packet_field_mutation_fails_validation(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any], field_name: str
) -> None:
    request, contributions, profiles, packet = bundle
    values: dict[str, object] = {
        "packet_id": "0" * 64,
        "request_id": "changed",
        "transaction_id": "changed",
        "target_root_id": "changed",
        "runtime_topology_ref": "changed",
        "synthesis_proposal": object(),
        "contribution_ids": tuple(reversed(packet.contribution_ids)),
        "conflict_set_ids": (),
        "missing_evidence_refs": (),
        "required_validator_ids": (),
        "review_state": "CHANGED",
        "authority_class": "ROOT",
        "root_decision_created": True,
        "permission_created": True,
        "final_output_created": True,
    }
    mutated = replace(packet, **{field_name: values[field_name]})
    errors = semantic.validate_root_review_packet_v01(
        request=request,
        contributions=contributions,
        packet=mutated,
        trust_profiles=profiles,
    )
    assert errors


@pytest.mark.parametrize("field_name", EXPECTED_FIELDS["SynthesisProposalV01"])
def test_every_synthesis_field_mutation_fails_packet_validation(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any], field_name: str
) -> None:
    request, contributions, profiles, packet = bundle
    proposal = packet.synthesis_proposal
    values: dict[str, object] = {
        "proposal_id": "0" * 64,
        "request_id": "changed",
        "source_contribution_ids": tuple(reversed(proposal.source_contribution_ids)),
        "normalized_claims": tuple(reversed(proposal.normalized_claims)),
        "conflict_sets": (),
        "missing_evidence_refs": (),
        "contribution_modes": tuple(reversed(proposal.contribution_modes)),
        "requested_validators": (),
        "synthesis_summary": "advisory_claims_ready_for_root_review",
        "authority_class": "ROOT",
        "root_review_required": False,
    }
    mutated_proposal = replace(proposal, **{field_name: values[field_name]})
    mutated_packet = replace(packet, synthesis_proposal=mutated_proposal)
    assert semantic.validate_root_review_packet_v01(
        request=request,
        contributions=contributions,
        packet=mutated_packet,
        trust_profiles=profiles,
    )


@pytest.mark.parametrize("type_name", tuple(EXPECTED_FIELDS))
def test_valid_public_projections_are_independent_json_objects(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any], type_name: str
) -> None:
    request, contributions, _, packet = bundle
    examples = {
        "SemanticWorkRequestV01": request,
        "EvidenceBindingV01": contributions[0].evidence_bindings[0],
        "ConstraintBindingV01": contributions[0].constraint_bindings[0],
        "UncertaintyBindingV01": contributions[3].uncertainty_bindings[0],
        "NormalizedClaimV01": contributions[0].claims[0],
        "ActorContributionV01": contributions[0],
        "ConflictSetV01": packet.synthesis_proposal.conflict_sets[0],
        "SynthesisProposalV01": packet.synthesis_proposal,
        "RootReviewPacketV01": packet,
    }
    first = semantic.semantic_work_to_plain_dict_v01(examples[type_name])
    second = semantic.semantic_work_to_plain_dict_v01(examples[type_name])
    assert first == second
    assert json.loads(json.dumps(first, allow_nan=False)) == first
    first[fields(examples[type_name])[0].name] = "changed"
    assert first != second


@pytest.mark.parametrize("type_name", tuple(EXPECTED_FIELDS))
def test_malformed_exact_dataclass_projection_is_rejected(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any], type_name: str
) -> None:
    request, contributions, _, packet = bundle
    malformed = {
        "SemanticWorkRequestV01": replace(request, request_id=""),
        "EvidenceBindingV01": replace(contributions[0].evidence_bindings[0], evidence_state="BAD"),
        "ConstraintBindingV01": replace(contributions[0].constraint_bindings[0], constraint_class="BAD"),
        "UncertaintyBindingV01": replace(contributions[3].uncertainty_bindings[0], confidence_micros=True),
        "NormalizedClaimV01": replace(contributions[0].claims[0], authority_class="ROOT"),
        "ActorContributionV01": replace(contributions[0], actor_role="orchestrator"),
        "ConflictSetV01": replace(packet.synthesis_proposal.conflict_sets[0], resolution_state="BAD"),
        "SynthesisProposalV01": replace(packet.synthesis_proposal, authority_class="ROOT"),
        "RootReviewPacketV01": replace(packet, permission_created=True),
    }[type_name]
    with pytest.raises(ValueError, match="^semantic_work_projection_invalid$") as exc:
        semantic.semantic_work_to_plain_dict_v01(malformed)
    assert exc.value.__cause__ is None


def test_schema_is_valid_draft_2020_12_and_accepts_packet_projection(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any]
) -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(
        semantic.semantic_work_to_plain_dict_v01(bundle[3])
    )


@pytest.mark.parametrize("field_name", EXPECTED_FIELDS["RootReviewPacketV01"])
def test_schema_rejects_every_required_packet_field_deletion(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any], field_name: str
) -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    projected = semantic.semantic_work_to_plain_dict_v01(bundle[3])
    del projected[field_name]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(projected)


def test_schema_rejects_unexpected_packet_field(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any]
) -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    projected = semantic.semantic_work_to_plain_dict_v01(bundle[3])
    projected["unexpected"] = True
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(projected)


@pytest.mark.parametrize(
    ("path", "value"),
    (
        (("synthesis_proposal", "authority_class"), "ROOT"),
        (
            (
                "synthesis_proposal",
                "normalized_claims",
                0,
                "source_mode",
            ),
            "UNKNOWN",
        ),
        (
            (
                "synthesis_proposal",
                "normalized_claims",
                0,
                "confidence_micros",
            ),
            True,
        ),
    ),
)
def test_schema_rejects_unknown_enums_and_wrong_confidence(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any],
    path: tuple[object, ...],
    value: object,
) -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    projected = semantic.semantic_work_to_plain_dict_v01(bundle[3])
    target: Any = projected
    for key in path[:-1]:
        target = target[key]
    target[path[-1]] = value
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.Draft202012Validator(schema).validate(projected)


def test_schema_boolean_root_decision_is_semantically_rejected(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any]
) -> None:
    request, contributions, profiles, packet = bundle
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    projected = semantic.semantic_work_to_plain_dict_v01(packet)
    projected["root_decision_created"] = True
    jsonschema.Draft202012Validator(schema).validate(projected)
    errors = semantic.validate_root_review_packet_v01(
        request=request,
        contributions=contributions,
        packet=replace(packet, root_decision_created=True),
        trust_profiles=profiles,
    )
    assert "root_decision_creation_forbidden" in errors


def test_schema_has_local_refs_and_strict_contract_objects() -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    def walk(value: object) -> list[dict[str, object]]:
        objects: list[dict[str, object]] = []
        if isinstance(value, dict):
            objects.append(value)
            for nested in value.values():
                objects.extend(walk(nested))
        elif isinstance(value, list):
            for nested in value:
                objects.extend(walk(nested))
        return objects

    objects = walk(schema)
    assert all(
        not isinstance(item.get("$ref"), str) or item["$ref"].startswith("#/")
        for item in objects
    )
    for definition in EXPECTED_FIELDS:
        key = definition[0].lower() + definition[1:].replace("V01", "")
        assert schema["$defs"][key]["additionalProperties"] is False
    assert all(
        item.get("additionalProperties") is False
        for item in objects
        if item.get("type") == "object"
    )


@pytest.mark.parametrize("malformed", (object(), None, 1, True, "value", []))
def test_public_validators_never_leak_on_malformed_top_level(malformed: object) -> None:
    assert semantic.validate_semantic_work_request_v01(malformed)
    assert semantic.validate_actor_contribution_v01(
        request=malformed,
        contribution=malformed,
        trust_profiles=malformed,
    )
    assert semantic.validate_root_review_packet_v01(
        request=malformed,
        contributions=malformed,
        packet=malformed,
        trust_profiles=malformed,
    )


def test_validator_errors_do_not_expose_caller_content_or_exception_repr() -> None:
    class Hostile:
        def __eq__(self, other: object) -> bool:
            raise OSError("sensitive caller content")

    errors = semantic.validate_semantic_work_request_v01(Hostile())
    rendered = repr(errors)
    assert "sensitive caller content" not in rendered
    assert "object at" not in rendered


def test_five_mode_fixture_and_packet_are_deterministic(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any]
) -> None:
    second = gauntlet._build_semantic_work_fixture_v01()
    first_projection = semantic.semantic_work_to_plain_dict_v01(bundle[3])
    second_projection = semantic.semantic_work_to_plain_dict_v01(second[3])
    assert first_projection == second_projection
    assert bundle[3].synthesis_proposal.proposal_id == second[3].synthesis_proposal.proposal_id
    assert bundle[3].packet_id == second[3].packet_id


def test_runtime_topology_is_request_owned_and_contribution_has_no_plangraph_field(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any]
) -> None:
    request, contributions, _, packet = bundle
    assert packet.runtime_topology_ref == request.runtime_topology_ref
    assert "runtime_topology_ref" not in EXPECTED_FIELDS["ActorContributionV01"]
    assert "PlanGraph" not in EXPECTED_FIELDS["ActorContributionV01"]
    assert all(not hasattr(item, "runtime_topology_ref") for item in contributions)


def test_provider_authoritative_topology_claim_fails_closed(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any]
) -> None:
    request, contributions, profiles, _ = bundle
    cloud = replace(
        contributions[2],
        forbidden_claims_observed=("authoritative_execution_topology",),
    )
    errors = semantic.validate_actor_contribution_v01(
        request=request, contribution=cloud, trust_profiles=profiles
    )
    assert "forbidden_claim_observed" in errors


def test_module_has_no_forbidden_imports() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imports = {
        node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
    }
    imports.update(
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    )
    assert not any(name.startswith(("hedgehog.domains", "demo", "tests")) for name in imports)
    assert not any(
        name.startswith(
            (
                "requests",
                "socket",
                "urllib",
                "os",
                "pathlib",
                "tempfile",
                "shutil",
                "subprocess",
            )
        )
        for name in imports
    )


@pytest.mark.parametrize(
    "forbidden_token",
    (
        "open(",
        ".read_text(",
        ".write_text(",
        "getenv(",
        "Gemini",
        "provider_client",
        "llm_call",
        "callback=",
        "effect_hook",
        "RootDecisionV01",
        "PermissionV01",
        "FinalOutputV01",
        "PlanGraphV01",
        "hedgehog.domains",
        "Airline",
        "Supplier",
        "Water Filter",
        ".tmp",
    ),
)
def test_module_source_contains_no_forbidden_runtime_surface(
    forbidden_token: str,
) -> None:
    assert forbidden_token not in MODULE_PATH.read_text(encoding="utf-8")


def test_mapping_is_snapshotted_from_exactly_one_items_iteration() -> None:
    class StatefulMapping(Mapping[str, object]):
        def __init__(self) -> None:
            self.items_call_count = 0

        def __getitem__(self, key: str) -> object:
            raise AssertionError("mapping item lookup is forbidden")

        def __iter__(self) -> object:
            raise AssertionError("mapping iteration outside items is forbidden")

        def __len__(self) -> int:
            return 1

        def items(self) -> object:
            self.items_call_count += 1
            if self.items_call_count == 1:
                return iter((("observed", 1),))
            return iter((("changed", 2),))

    source = StatefulMapping()
    claim = _claim(source)
    assert source.items_call_count == 1
    assert semantic.semantic_work_to_plain_dict_v01(claim)["object_or_value"] == {
        "observed": 1
    }


def test_duplicate_keys_in_one_mapping_items_sequence_are_rejected() -> None:
    class DuplicateMapping(Mapping[str, object]):
        def __getitem__(self, key: str) -> object:
            raise KeyError(key)

        def __iter__(self) -> object:
            return iter(())

        def __len__(self) -> int:
            return 2

        def items(self) -> object:
            return iter((("duplicate", 1), ("duplicate", 2)))

    with pytest.raises(ValueError, match="^claim_contract_invalid$") as exc:
        _claim(DuplicateMapping())
    assert exc.value.__cause__ is None


@pytest.mark.parametrize(
    "row",
    (
        ["key", "value"],
        ("key",),
        ("key", "value", "extra"),
    ),
)
def test_malformed_mapping_items_rows_are_rejected(row: object) -> None:
    class MalformedMapping(Mapping[str, object]):
        def __getitem__(self, key: str) -> object:
            raise KeyError(key)

        def __iter__(self) -> object:
            return iter(())

        def __len__(self) -> int:
            return 1

        def items(self) -> object:
            return iter((row,))

    with pytest.raises(ValueError, match="^claim_contract_invalid$"):
        _claim(MalformedMapping())


@pytest.mark.parametrize(
    "forged",
    (
        semantic._FrozenJSONObject((("duplicate", 1), ("duplicate", 2))),
        semantic._FrozenJSONObject((("z", 1), ("a", 2))),
        semantic._FrozenJSONObject(((1, "value"),)),
    ),
)
def test_forged_frozen_json_objects_are_rejected(forged: object) -> None:
    malformed = replace(_claim(), object_or_value=forged)
    with pytest.raises(ValueError, match="^semantic_work_projection_invalid$"):
        semantic.semantic_work_to_plain_dict_v01(malformed)


def test_evidence_builder_sanitizes_hostile_equality_exception() -> None:
    class HostileEquality:
        def __eq__(self, other: object) -> bool:
            raise OSError("caller-controlled evidence text")

    with pytest.raises(ValueError, match="^evidence_binding_invalid$") as exc:
        semantic.build_evidence_binding_v01(
            evidence_id="evidence:test:001",
            evidence_ref="evidence-ref:test:001",
            evidence_class="OBSERVATION",
            source_component_id="actor:test:001",
            provenance_ref="provenance:test:001",
            evidence_state=HostileEquality(),  # type: ignore[arg-type]
        )
    assert exc.value.__cause__ is None
    assert "caller-controlled" not in str(exc.value)


def test_actor_builder_sanitizes_hostile_equality_exception(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any]
) -> None:
    class HostileEquality:
        def __eq__(self, other: object) -> bool:
            raise OSError("caller-controlled actor text")

    contribution = bundle[1][0]
    kwargs = {
        field.name: getattr(contribution, field.name) for field in fields(contribution)
    }
    kwargs["contribution_mode"] = HostileEquality()
    with pytest.raises(ValueError, match="^actor_contribution_invalid$") as exc:
        semantic.build_actor_contribution_v01(**kwargs)  # type: ignore[arg-type]
    assert exc.value.__cause__ is None
    assert "caller-controlled" not in str(exc.value)


class _SemanticStrSubclass(str):
    pass


def test_evidence_state_str_subclass_is_rejected() -> None:
    with pytest.raises(ValueError, match="^evidence_binding_invalid$"):
        semantic.build_evidence_binding_v01(
            evidence_id="evidence:test:001",
            evidence_ref="evidence-ref:test:001",
            evidence_class="OBSERVATION",
            source_component_id="actor:test:001",
            provenance_ref="provenance:test:001",
            evidence_state=_SemanticStrSubclass("PRESENT"),
        )


@pytest.mark.parametrize(
    ("field_name", "value"),
    (
        ("constraint_class", _SemanticStrSubclass("HARD")),
        ("evaluation_state", _SemanticStrSubclass("SATISFIED")),
    ),
)
def test_constraint_enum_str_subclasses_are_rejected(
    field_name: str, value: object
) -> None:
    kwargs: dict[str, object] = {
        "constraint_id": "constraint:test:001",
        "subject": "resource:alpha",
        "predicate": "allowed",
        "object_or_value": True,
        "source_ref": "policy:test:001",
        "constraint_class": "HARD",
        "evaluation_state": "SATISFIED",
    }
    kwargs[field_name] = value
    with pytest.raises(ValueError, match="^constraint_binding_invalid$"):
        semantic.build_constraint_binding_v01(**kwargs)  # type: ignore[arg-type]


def test_contribution_mode_str_subclass_is_rejected(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any]
) -> None:
    contribution = bundle[1][0]
    kwargs = {
        field.name: getattr(contribution, field.name) for field in fields(contribution)
    }
    kwargs["contribution_mode"] = _SemanticStrSubclass("DETERMINISTIC")
    with pytest.raises(ValueError, match="^actor_contribution_invalid$"):
        semantic.build_actor_contribution_v01(**kwargs)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "mutation",
    (
        lambda packet: replace(
            packet.synthesis_proposal.conflict_sets[0],
            resolution_state=_SemanticStrSubclass(semantic.CONFLICT_STATE),
        ),
        lambda packet: replace(
            packet.synthesis_proposal.conflict_sets[0],
            source_modes=(
                _SemanticStrSubclass("CLOUD_LLM"),
                "LOCAL_SLM",
            ),
        ),
        lambda packet: replace(
            packet.synthesis_proposal,
            synthesis_summary=_SemanticStrSubclass(
                packet.synthesis_proposal.synthesis_summary
            ),
        ),
        lambda packet: replace(
            packet.synthesis_proposal,
            authority_class=_SemanticStrSubclass("ADVISORY_ONLY"),
        ),
        lambda packet: replace(
            packet,
            review_state=_SemanticStrSubclass("ROOT_REVIEW_REQUIRED"),
        ),
        lambda packet: replace(
            packet,
            authority_class=_SemanticStrSubclass("ADVISORY_ONLY"),
        ),
    ),
)
def test_nested_enum_str_subclasses_fail_public_projection(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any], mutation: object
) -> None:
    malformed = mutation(bundle[3])  # type: ignore[operator]
    with pytest.raises(ValueError, match="^semantic_work_projection_invalid$"):
        semantic.semantic_work_to_plain_dict_v01(malformed)


@pytest.mark.parametrize(
    ("left_value", "right_value"),
    (
        (True, 1),
        (False, 0),
        (1, 1.0),
        (-0.0, 0.0),
        ({"nested": 1}, {"nested": 1.0}),
    ),
)
def test_reused_claim_id_uses_canonical_json_identity(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any],
    left_value: object,
    right_value: object,
) -> None:
    request, contributions, profiles, _ = bundle
    base = contributions[0]
    first = _claim_from_existing(base.claims[0], left_value)
    second = _claim_from_existing(base.claims[0], right_value)
    changed = (replace(base, claims=(first, second)),) + contributions[1:]
    with pytest.raises(ValueError, match="^claim_contract_invalid$"):
        semantic.build_root_review_packet_from_contributions_v01(
            request=request,
            contributions=changed,
            trust_profiles=profiles,
        )


def test_stale_packet_ids_cannot_hide_nested_integer_to_float_mutation(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any]
) -> None:
    request, contributions, profiles, _ = bundle
    base = contributions[0]
    integer_claim = _claim_from_existing(base.claims[0], 1)
    changed = (replace(base, claims=(integer_claim,)),) + contributions[1:]
    packet = semantic.build_root_review_packet_from_contributions_v01(
        request=request,
        contributions=changed,
        trust_profiles=profiles,
    )
    float_claim = _claim_from_existing(integer_claim, 1.0)
    stale_proposal = replace(
        packet.synthesis_proposal,
        normalized_claims=(float_claim,)
        + packet.synthesis_proposal.normalized_claims[1:],
    )
    stale_packet = replace(packet, synthesis_proposal=stale_proposal)
    errors = semantic.validate_root_review_packet_v01(
        request=request,
        contributions=changed,
        packet=stale_packet,
        trust_profiles=profiles,
    )
    assert "synthesis_proposal_invalid" in errors
    assert "normalized_claim_set_mismatch" in errors
    with pytest.raises(ValueError, match="^semantic_work_projection_invalid$"):
        semantic.semantic_work_to_plain_dict_v01(stale_packet)


@pytest.mark.parametrize("replacement_id", ("0" * 64, "f" * 64))
def test_standalone_arbitrary_conflict_id_is_rejected(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any], replacement_id: str
) -> None:
    conflict = bundle[3].synthesis_proposal.conflict_sets[0]
    with pytest.raises(ValueError, match="^semantic_work_projection_invalid$"):
        semantic.semantic_work_to_plain_dict_v01(
            replace(conflict, conflict_set_id=replacement_id)
        )


@pytest.mark.parametrize(
    ("field_name", "replacement"),
    (
        ("subject", "resource:changed"),
        ("predicate", "readiness_changed"),
        ("claim_ids", ("claim:changed:001", "claim:changed:002")),
        ("conflicting_values", ("changed", "blocked")),
        ("source_modes", ("DETERMINISTIC", "LOCAL_SLM")),
        ("source_modes", ("UNKNOWN", "LOCAL_SLM")),
        ("resolution_state", "UNKNOWN"),
    ),
)
def test_standalone_conflict_public_field_mutation_is_rejected(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any],
    field_name: str,
    replacement: object,
) -> None:
    conflict = bundle[3].synthesis_proposal.conflict_sets[0]
    malformed = replace(conflict, **{field_name: replacement})
    with pytest.raises(ValueError, match="^semantic_work_projection_invalid$"):
        semantic.semantic_work_to_plain_dict_v01(malformed)


def test_corrected_fixture_identity_and_geometry_are_repeatable() -> None:
    first = gauntlet._build_semantic_work_fixture_v01()
    second = gauntlet._build_semantic_work_fixture_v01()
    first_contributions = first[1]
    first_packet = first[3]
    second_packet = second[3]
    assert (
        sum(len(item.claims) for item in first_contributions),
        len(first_packet.synthesis_proposal.normalized_claims),
        6 - len(first_packet.synthesis_proposal.normalized_claims),
        len(first_packet.synthesis_proposal.conflict_sets),
        len(first_packet.missing_evidence_refs),
    ) == (6, 5, 1, 1, 1)
    assert first_packet.synthesis_proposal.proposal_id == (
        second_packet.synthesis_proposal.proposal_id
    )
    assert first_packet.packet_id == second_packet.packet_id
    assert semantic.semantic_work_to_plain_dict_v01(first_packet) == (
        semantic.semantic_work_to_plain_dict_v01(second_packet)
    )


def test_packet_builder_does_not_read_hostile_contribution_property_before_validation(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any]
) -> None:
    class HostileContribution:
        @property
        def contribution_id(self) -> object:
            raise ValueError("CALLER_SECRET_PAYLOAD")

    request, _, profiles, _ = bundle
    with pytest.raises(ValueError, match="^actor_contribution_invalid$") as exc:
        semantic.build_root_review_packet_from_contributions_v01(
            request=request,
            contributions=(HostileContribution(),),  # type: ignore[arg-type]
            trust_profiles=profiles,
        )
    assert exc.value.__cause__ is None
    assert "CALLER_SECRET_PAYLOAD" not in str(exc.value)


def test_packet_builder_rejects_hostile_contribution_id_hash_before_hashing(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any]
) -> None:
    class HostileHash:
        def __hash__(self) -> int:
            raise ValueError("CALLER_SECRET_HASH")

    request, contributions, profiles, _ = bundle
    malformed = replace(contributions[0], contribution_id=HostileHash())
    with pytest.raises(ValueError, match="^actor_contribution_invalid$") as exc:
        semantic.build_root_review_packet_from_contributions_v01(
            request=request,
            contributions=(malformed,),
            trust_profiles=profiles,
        )
    assert exc.value.__cause__ is None
    assert "CALLER_SECRET_HASH" not in str(exc.value)


@pytest.mark.parametrize("error_type", (ValueError, OSError))
def test_packet_builder_sanitizes_hostile_actor_equality(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any],
    error_type: type[Exception],
) -> None:
    class HostileEquality:
        def __eq__(self, other: object) -> bool:
            raise error_type("CALLER_SECRET_EQUALITY")

    request, contributions, profiles, _ = bundle
    malformed = replace(contributions[0], actor_role=HostileEquality())
    with pytest.raises(ValueError, match="^actor_contribution_invalid$") as exc:
        semantic.build_root_review_packet_from_contributions_v01(
            request=request,
            contributions=(malformed,),
            trust_profiles=profiles,
        )
    assert exc.value.__cause__ is None
    assert "CALLER_SECRET_EQUALITY" not in str(exc.value)


def test_packet_builder_sanitizes_hostile_property_oserror(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any]
) -> None:
    class HostileContribution:
        @property
        def contribution_id(self) -> object:
            raise OSError("CALLER_SECRET_OSERROR")

    request, _, profiles, _ = bundle
    with pytest.raises(ValueError, match="^actor_contribution_invalid$") as exc:
        semantic.build_root_review_packet_from_contributions_v01(
            request=request,
            contributions=(HostileContribution(),),  # type: ignore[arg-type]
            trust_profiles=profiles,
        )
    assert exc.value.__cause__ is None
    assert "CALLER_SECRET_OSERROR" not in str(exc.value)


def test_packet_builder_replaces_unallowlisted_valueerror_reason(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def hostile_internal(*args: object, **kwargs: object) -> object:
        raise ValueError("CALLER_SECRET_INTERNAL")

    request, contributions, profiles, _ = bundle
    monkeypatch.setattr(semantic, "_build_packet_from_validated", hostile_internal)
    with pytest.raises(
        ValueError, match="^semantic_work_unexpected_exception$"
    ) as exc:
        semantic.build_root_review_packet_from_contributions_v01(
            request=request,
            contributions=contributions,
            trust_profiles=profiles,
        )
    assert exc.value.__cause__ is None
    assert "CALLER_SECRET_INTERNAL" not in str(exc.value)


def test_packet_builder_preserves_known_claim_contract_reason(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any]
) -> None:
    request, contributions, profiles, _ = bundle
    first = contributions[0].claims[0]
    malformed = replace(
        contributions[0],
        claims=(first, replace(first, confidence_micros=999_999)),
    )
    with pytest.raises(ValueError, match="^claim_contract_invalid$") as exc:
        semantic.build_root_review_packet_from_contributions_v01(
            request=request,
            contributions=(malformed,) + contributions[1:],
            trust_profiles=profiles,
        )
    assert exc.value.__cause__ is None


@pytest.mark.parametrize(
    ("request_mutation", "expected_reason"),
    (
        ({"request_id": ""}, "semantic_work_request_invalid"),
        (
            {"bounded_context_refs": ()},
            "semantic_work_request_context_invalid",
        ),
        (
            {"permitted_contribution_modes": ("UNKNOWN",)},
            "semantic_work_request_modes_invalid",
        ),
        ({"runtime_topology_ref": ""}, "runtime_topology_ref_invalid"),
    ),
)
def test_packet_builder_preserves_known_request_validation_reasons(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any],
    request_mutation: dict[str, object],
    expected_reason: str,
) -> None:
    request, contributions, profiles, _ = bundle
    with pytest.raises(ValueError, match=f"^{expected_reason}$") as exc:
        semantic.build_root_review_packet_from_contributions_v01(
            request=replace(request, **request_mutation),
            contributions=contributions,
            trust_profiles=profiles,
        )
    assert exc.value.__cause__ is None


@pytest.mark.parametrize(
    ("identity", "expected"),
    (
        (
            "proposal",
            "cbbf1543d29077afe15fe09475be85cb3e55242d54dbddfe1ef88d749519ec8e",
        ),
        (
            "packet",
            "d30f90597b54d9e80693762089daad88a5ae4aaf8ff3dc41b97525f1f53f273f",
        ),
    ),
)
def test_packet_builder_valid_fixture_identities_remain_frozen(
    bundle: tuple[Any, tuple[Any, ...], tuple[Any, ...], Any],
    identity: str,
    expected: str,
) -> None:
    packet = bundle[3]
    observed = (
        packet.synthesis_proposal.proposal_id
        if identity == "proposal"
        else packet.packet_id
    )
    assert observed == expected
