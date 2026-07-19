from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, fields, is_dataclass, replace
import hashlib
import inspect
import json
from pathlib import Path

import pytest

import hedgehog.kernel as kernel_package
from hedgehog.kernel.integrity_replay_v01 import (
    canonical_json_bytes_v01,
    domain_separated_sha256_hex_v01,
)
import hedgehog.kernel.multiroot_v01 as multiroot


MODULE_PATH = Path(multiroot.__file__)
TRANSACTION_ID = "txn:neutral:multiroot:001"
ROOTS_THREE = ("root:alpha", "root:beta", "root:gamma")
ROOTS_FOUR = (*ROOTS_THREE, "root:delta")
EXPECTED_ALL = (
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
PUBLIC_FUNCTIONS = (
    "build_root_decision_envelope_v01",
    "validate_root_decision_envelope_v01",
    "build_cross_root_evidence_ref_v01",
    "validate_cross_root_evidence_ref_v01",
    "build_transaction_outcome_envelope_v01",
    "validate_transaction_outcome_envelope_v01",
    "validate_multiroot_v01",
    "root_decision_envelope_to_plain_dict_v01",
    "cross_root_evidence_ref_to_plain_dict_v01",
    "transaction_outcome_envelope_to_plain_dict_v01",
    "multiroot_validation_result_to_plain_dict_v01",
)
ROOT_FIELDS = (
    "envelope_id",
    "transaction_id",
    "root_id",
    "root_decision_id",
    "source_decision_ref",
    "outcome_class",
    "reason_code",
    "selected_subject_id",
    "root_commit_created",
    "authority_class",
    "evidence_refs",
    "cross_root_input_refs",
    "real_world_effects_count",
)
CROSS_FIELDS = (
    "ref_id",
    "transaction_id",
    "source_root_id",
    "target_root_id",
    "evidence_artifact_id",
    "evidence_artifact_hash",
    "evidence_class",
    "receipt_validated",
    "authority_transferred",
    "permission_created",
    "effect_authorized",
    "trace_refs",
    "real_world_effects_count",
)
OUTCOME_FIELDS = (
    "outcome_id",
    "transaction_id",
    "expected_root_ids",
    "root_decisions",
    "cross_root_evidence_refs",
    "observed_root_ids",
    "accepted_root_ids",
    "non_accepted_root_ids",
    "outcome_status",
    "mixed_outcomes_visible",
    "super_root_created",
    "authority_transfer_count",
    "permission_creation_count",
    "real_world_effects_count",
)
VALIDATION_FIELDS = (
    "validation_id",
    "transaction_id",
    "expected_root_ids",
    "observed_root_ids",
    "root_decision_count",
    "cross_root_evidence_count",
    "accepted_root_count",
    "non_accepted_root_count",
    "unknown_root_ids",
    "duplicate_root_ids",
    "missing_root_ids",
    "mixed_outcomes_visible",
    "authority_transfer_count",
    "permission_creation_count",
    "super_root_created",
    "final_status",
    "errors",
    "real_world_effects_count",
)


def _root(
    root_id: str,
    outcome_class: str = "ACCEPTED",
    *,
    transaction_id: str = TRANSACTION_ID,
    suffix: str = "001",
) -> multiroot.RootDecisionEnvelopeV01:
    selected = f"subject:{root_id}:{suffix}" if outcome_class == "ACCEPTED" else None
    return multiroot.build_root_decision_envelope_v01(
        transaction_id=transaction_id,
        root_id=root_id,
        root_decision_id=f"decision:{root_id}:{suffix}",
        source_decision_ref=f"source:{root_id}:{suffix}",
        outcome_class=outcome_class,
        reason_code=f"reason:{outcome_class.lower()}",
        selected_subject_id=selected,
        evidence_refs=(f"evidence:{root_id}:{suffix}",),
        cross_root_input_refs=(),
    )


def _cross(
    source_root_id: str = ROOTS_THREE[0],
    target_root_id: str = ROOTS_THREE[1],
    *,
    evidence_class: str = "VALIDATED_EVIDENCE",
    artifact_suffix: str = "001",
    transaction_id: str = TRANSACTION_ID,
) -> multiroot.CrossRootEvidenceRefV01:
    return multiroot.build_cross_root_evidence_ref_v01(
        transaction_id=transaction_id,
        source_root_id=source_root_id,
        target_root_id=target_root_id,
        evidence_artifact_id=f"evidence:cross:{artifact_suffix}",
        evidence_artifact_hash=hashlib.sha256(
            f"neutral:{artifact_suffix}".encode("ascii")
        ).hexdigest(),
        evidence_class=evidence_class,
        receipt_validated=evidence_class == "EVIDENCE_RECEIPT",
        trace_refs=(f"trace:cross:{artifact_suffix}",),
    )


def _outcome(
    expected_root_ids: tuple[str, ...] = ROOTS_THREE,
    outcome_classes: tuple[str, ...] | None = None,
    *,
    observed_count: int | None = None,
    refs: tuple[multiroot.CrossRootEvidenceRefV01, ...] = (),
) -> multiroot.TransactionOutcomeEnvelopeV01:
    classes = outcome_classes or tuple("ACCEPTED" for _ in expected_root_ids)
    count = len(expected_root_ids) if observed_count is None else observed_count
    decisions = tuple(
        _root(root_id, classes[index], suffix=f"{index + 1:03d}")
        for index, root_id in enumerate(expected_root_ids[:count])
    )
    return multiroot.build_transaction_outcome_envelope_v01(
        transaction_id=TRANSACTION_ID,
        expected_root_ids=expected_root_ids,
        root_decisions=decisions,
        cross_root_evidence_refs=refs,
    )


def _plain_root(value: multiroot.RootDecisionEnvelopeV01) -> dict[str, object]:
    return {
        "envelope_id": value.envelope_id,
        "transaction_id": value.transaction_id,
        "root_id": value.root_id,
        "root_decision_id": value.root_decision_id,
        "source_decision_ref": value.source_decision_ref,
        "outcome_class": value.outcome_class,
        "reason_code": value.reason_code,
        "selected_subject_id": value.selected_subject_id,
        "root_commit_created": value.root_commit_created,
        "authority_class": value.authority_class,
        "evidence_refs": list(value.evidence_refs),
        "cross_root_input_refs": list(value.cross_root_input_refs),
        "real_world_effects_count": value.real_world_effects_count,
    }


def _plain_cross(value: multiroot.CrossRootEvidenceRefV01) -> dict[str, object]:
    return {
        "ref_id": value.ref_id,
        "transaction_id": value.transaction_id,
        "source_root_id": value.source_root_id,
        "target_root_id": value.target_root_id,
        "evidence_artifact_id": value.evidence_artifact_id,
        "evidence_artifact_hash": value.evidence_artifact_hash,
        "evidence_class": value.evidence_class,
        "receipt_validated": value.receipt_validated,
        "authority_transferred": value.authority_transferred,
        "permission_created": value.permission_created,
        "effect_authorized": value.effect_authorized,
        "trace_refs": list(value.trace_refs),
        "real_world_effects_count": value.real_world_effects_count,
    }


def _plain_outcome(
    value: multiroot.TransactionOutcomeEnvelopeV01,
) -> dict[str, object]:
    return {
        "outcome_id": value.outcome_id,
        "transaction_id": value.transaction_id,
        "expected_root_ids": list(value.expected_root_ids),
        "root_decisions": [_plain_root(item) for item in value.root_decisions],
        "cross_root_evidence_refs": [
            _plain_cross(item) for item in value.cross_root_evidence_refs
        ],
        "observed_root_ids": list(value.observed_root_ids),
        "accepted_root_ids": list(value.accepted_root_ids),
        "non_accepted_root_ids": list(value.non_accepted_root_ids),
        "outcome_status": value.outcome_status,
        "mixed_outcomes_visible": value.mixed_outcomes_visible,
        "super_root_created": value.super_root_created,
        "authority_transfer_count": value.authority_transfer_count,
        "permission_creation_count": value.permission_creation_count,
        "real_world_effects_count": value.real_world_effects_count,
    }


def _plain_validation(
    value: multiroot.MultiRootValidationResultV01,
) -> dict[str, object]:
    return {
        "validation_id": value.validation_id,
        "transaction_id": value.transaction_id,
        "expected_root_ids": list(value.expected_root_ids),
        "observed_root_ids": list(value.observed_root_ids),
        "root_decision_count": value.root_decision_count,
        "cross_root_evidence_count": value.cross_root_evidence_count,
        "accepted_root_count": value.accepted_root_count,
        "non_accepted_root_count": value.non_accepted_root_count,
        "unknown_root_ids": list(value.unknown_root_ids),
        "duplicate_root_ids": list(value.duplicate_root_ids),
        "missing_root_ids": list(value.missing_root_ids),
        "mixed_outcomes_visible": value.mixed_outcomes_visible,
        "authority_transfer_count": value.authority_transfer_count,
        "permission_creation_count": value.permission_creation_count,
        "super_root_created": value.super_root_created,
        "final_status": value.final_status,
        "errors": list(value.errors),
        "real_world_effects_count": value.real_world_effects_count,
    }


def _rehash_root(
    value: multiroot.RootDecisionEnvelopeV01,
    **changes: object,
) -> multiroot.RootDecisionEnvelopeV01:
    provisional = replace(value, envelope_id="0" * 64, **changes)
    material = _plain_root(provisional)
    material.pop("envelope_id")
    return replace(
        provisional,
        envelope_id=domain_separated_sha256_hex_v01(
            domain="hedgehog.kernel.multiroot.root_decision_envelope.v01",
            payload=canonical_json_bytes_v01(material),
        ),
    )


def _rehash_cross(
    value: multiroot.CrossRootEvidenceRefV01,
    **changes: object,
) -> multiroot.CrossRootEvidenceRefV01:
    provisional = replace(value, ref_id="0" * 64, **changes)
    material = _plain_cross(provisional)
    material.pop("ref_id")
    return replace(
        provisional,
        ref_id=domain_separated_sha256_hex_v01(
            domain="hedgehog.kernel.multiroot.cross_root_evidence_ref.v01",
            payload=canonical_json_bytes_v01(material),
        ),
    )


def _rehash_outcome(
    value: multiroot.TransactionOutcomeEnvelopeV01,
    **changes: object,
) -> multiroot.TransactionOutcomeEnvelopeV01:
    provisional = replace(value, outcome_id="0" * 64, **changes)
    material = _plain_outcome(provisional)
    material.pop("outcome_id")
    return replace(
        provisional,
        outcome_id=domain_separated_sha256_hex_v01(
            domain="hedgehog.kernel.multiroot.transaction_outcome_envelope.v01",
            payload=canonical_json_bytes_v01(material),
        ),
    )


def _rehash_validation(
    value: multiroot.MultiRootValidationResultV01,
    **changes: object,
) -> multiroot.MultiRootValidationResultV01:
    provisional = replace(value, validation_id="0" * 64, **changes)
    material = _plain_validation(provisional)
    material.pop("validation_id")
    return replace(
        provisional,
        validation_id=domain_separated_sha256_hex_v01(
            domain="hedgehog.kernel.multiroot.validation_result.v01",
            payload=canonical_json_bytes_v01(material),
        ),
    )


def _contains_forbidden_projection_value(value: object) -> bool:
    if isinstance(value, (tuple, bytes, bytearray, memoryview)) or is_dataclass(value):
        return True
    if isinstance(value, dict):
        return any(_contains_forbidden_projection_value(item) for item in value.values())
    if isinstance(value, list):
        return any(_contains_forbidden_projection_value(item) for item in value)
    return False


@pytest.fixture
def pass_three() -> multiroot.TransactionOutcomeEnvelopeV01:
    return _outcome()


@pytest.fixture
def pass_four() -> multiroot.TransactionOutcomeEnvelopeV01:
    return _outcome(ROOTS_FOUR)


@pytest.fixture
def mixed() -> multiroot.TransactionOutcomeEnvelopeV01:
    return _outcome(ROOTS_THREE, ("ACCEPTED", "BLOCKED", "HELD"))


@pytest.fixture
def incomplete() -> multiroot.TransactionOutcomeEnvelopeV01:
    return _outcome(ROOTS_THREE, observed_count=2)


@pytest.mark.parametrize(
    "cls,expected",
    (
        (multiroot.RootDecisionEnvelopeV01, ROOT_FIELDS),
        (multiroot.CrossRootEvidenceRefV01, CROSS_FIELDS),
        (multiroot.TransactionOutcomeEnvelopeV01, OUTCOME_FIELDS),
        (multiroot.MultiRootValidationResultV01, VALIDATION_FIELDS),
    ),
)
def test_exact_dataclass_field_order(cls: type[object], expected: tuple[str, ...]) -> None:
    assert tuple(field.name for field in fields(cls)) == expected


@pytest.mark.parametrize(
    "cls",
    (
        multiroot.RootDecisionEnvelopeV01,
        multiroot.CrossRootEvidenceRefV01,
        multiroot.TransactionOutcomeEnvelopeV01,
        multiroot.MultiRootValidationResultV01,
    ),
)
def test_public_dataclasses_are_frozen_and_slotted(cls: type[object]) -> None:
    assert is_dataclass(cls)
    assert cls.__dataclass_params__.frozen is True
    assert tuple(cls.__slots__) == tuple(field.name for field in fields(cls))


@pytest.mark.parametrize(
    "value",
    (
        lambda: _root(ROOTS_THREE[0]),
        lambda: _cross(),
        lambda: _outcome(),
        lambda: multiroot.validate_multiroot_v01(_outcome()),
    ),
)
def test_public_dataclass_instances_reject_mutation(value) -> None:
    instance = value()
    with pytest.raises(FrozenInstanceError):
        setattr(instance, fields(instance)[0].name, "changed")


def test_exact_public_function_surface() -> None:
    observed = tuple(
        name
        for name, value in vars(multiroot).items()
        if inspect.isfunction(value) and not name.startswith("_")
    )
    assert observed == PUBLIC_FUNCTIONS


@pytest.mark.parametrize(
    "name",
    (
        "RootDecisionEnvelopeV01",
        "CrossRootEvidenceRefV01",
        "TransactionOutcomeEnvelopeV01",
        "MultiRootValidationResultV01",
        *PUBLIC_FUNCTIONS,
    ),
)
def test_package_direct_attributes(name: str) -> None:
    assert getattr(kernel_package, name) is getattr(multiroot, name)


def test_package_all_is_unchanged() -> None:
    assert kernel_package.__all__ == EXPECTED_ALL
    assert not set(PUBLIC_FUNCTIONS).intersection(kernel_package.__all__)


def test_accidental_annotations_name_absent() -> None:
    assert "annotations" not in vars(multiroot)


def test_exact_public_dataclass_set() -> None:
    observed = {
        name
        for name, value in vars(multiroot).items()
        if inspect.isclass(value) and not name.startswith("_")
    }
    assert observed == {
        "RootDecisionEnvelopeV01",
        "CrossRootEvidenceRefV01",
        "TransactionOutcomeEnvelopeV01",
        "MultiRootValidationResultV01",
    }


@pytest.mark.parametrize(
    "name,expected",
    (
        ("MODULE_ID", "kernel_multiroot_v01"),
        ("SLICE_ID", "domain_neutral_reference_kernel_gate1_g1d2"),
        ("MULTIROOT_VERSION", "v0.1"),
        ("STATUS_PASS", "PASS"),
        ("STATUS_MIXED", "MIXED"),
        ("STATUS_INCOMPLETE", "INCOMPLETE"),
        ("STATUS_FAIL_CLOSED", "FAIL_CLOSED"),
        ("ROOT_AUTHORITY_CLASS", "ROOT_OWNED"),
    ),
)
def test_exact_identity_constants(name: str, expected: str) -> None:
    assert getattr(multiroot, name) == expected


def test_exact_immutable_vocabulary_tuples() -> None:
    assert multiroot.MULTIROOT_STATUSES == ("PASS", "MIXED", "INCOMPLETE", "FAIL_CLOSED")
    assert multiroot.ROOT_OUTCOME_CLASSES == (
        "ACCEPTED", "REJECTED", "BLOCKED", "HELD", "DEFERRED",
        "NEEDS_USER", "NEEDS_MORE_EVIDENCE", "NO_UPDATE",
    )
    assert multiroot.CROSS_ROOT_EVIDENCE_CLASSES == (
        "VALIDATED_EVIDENCE", "EVIDENCE_RECEIPT", "CROSS_ROOT_ADVISORY",
    )
    assert all(
        type(value) is tuple
        for value in (
            multiroot.MULTIROOT_STATUSES,
            multiroot.ROOT_OUTCOME_CLASSES,
            multiroot.CROSS_ROOT_EVIDENCE_CLASSES,
        )
    )


@pytest.mark.parametrize("outcome_class", multiroot.ROOT_OUTCOME_CLASSES)
def test_every_root_outcome_class_builds_and_validates(outcome_class: str) -> None:
    value = _root(ROOTS_THREE[0], outcome_class)
    assert multiroot.validate_root_decision_envelope_v01(value) == ()
    assert value.selected_subject_id is not None if outcome_class == "ACCEPTED" else value.selected_subject_id is None


@pytest.mark.parametrize("outcome_class", multiroot.ROOT_OUTCOME_CLASSES)
def test_every_root_outcome_identity_is_deterministic(outcome_class: str) -> None:
    assert _root(ROOTS_THREE[0], outcome_class) == _root(ROOTS_THREE[0], outcome_class)


@pytest.mark.parametrize("outcome_class", multiroot.ROOT_OUTCOME_CLASSES[1:])
def test_nonaccepted_outcomes_reject_selected_subject(outcome_class: str) -> None:
    with pytest.raises(ValueError, match="^multiroot_root_decision_invalid$"):
        multiroot.build_root_decision_envelope_v01(
            transaction_id=TRANSACTION_ID,
            root_id=ROOTS_THREE[0],
            root_decision_id="decision:invalid:selected",
            source_decision_ref="source:invalid:selected",
            outcome_class=outcome_class,
            reason_code="reason:invalid:selected",
            selected_subject_id="subject:forbidden",
            evidence_refs=(),
            cross_root_input_refs=(),
        )


def test_accepted_outcome_requires_selected_subject() -> None:
    with pytest.raises(ValueError, match="^multiroot_root_decision_invalid$"):
        multiroot.build_root_decision_envelope_v01(
            transaction_id=TRANSACTION_ID,
            root_id=ROOTS_THREE[0],
            root_decision_id="decision:invalid:missing",
            source_decision_ref="source:invalid:missing",
            outcome_class="ACCEPTED",
            reason_code="reason:invalid:missing",
            selected_subject_id=None,
            evidence_refs=(),
            cross_root_input_refs=(),
        )


@pytest.mark.parametrize(
    "field,value,reason",
    (
        ("envelope_id", "0" * 64, "multiroot_identity_mismatch"),
        ("transaction_id", "", "multiroot_root_decision_invalid"),
        ("root_id", "root:superroot", "multiroot_super_root_forbidden"),
        ("root_decision_id", "", "multiroot_root_decision_invalid"),
        ("source_decision_ref", "", "multiroot_root_decision_invalid"),
        ("outcome_class", "UNKNOWN", "multiroot_root_decision_invalid"),
        ("reason_code", "", "multiroot_root_decision_invalid"),
        ("selected_subject_id", None, "multiroot_root_decision_invalid"),
        ("root_commit_created", False, "multiroot_root_decision_invalid"),
        ("authority_class", "ADVISORY", "multiroot_authority_transfer_forbidden"),
        ("evidence_refs", [], "multiroot_root_decision_invalid"),
        ("cross_root_input_refs", [], "multiroot_root_decision_invalid"),
        ("real_world_effects_count", 1, "multiroot_real_effect_forbidden"),
    ),
)
def test_every_root_envelope_field_mutation_rejected(field: str, value: object, reason: str) -> None:
    errors = multiroot.validate_root_decision_envelope_v01(
        replace(_root(ROOTS_THREE[0]), **{field: value})
    )
    assert reason in errors


@pytest.mark.parametrize(
    "field",
    ("transaction_id", "root_id", "root_decision_id", "source_decision_ref", "reason_code"),
)
@pytest.mark.parametrize("value", (None, "", True, "\ud800"))
def test_root_text_field_rejection_matrix(field: str, value: object) -> None:
    errors = multiroot.validate_root_decision_envelope_v01(
        replace(_root(ROOTS_THREE[0]), **{field: value})
    )
    assert "multiroot_root_decision_invalid" in errors


@pytest.mark.parametrize("field", ("evidence_refs", "cross_root_input_refs"))
@pytest.mark.parametrize(
    "value",
    ([], ("",), ("ref:a", "ref:a"), ("\ud800",)),
)
def test_root_reference_tuple_rejection_matrix(field: str, value: object) -> None:
    assert multiroot.validate_root_decision_envelope_v01(
        replace(_root(ROOTS_THREE[0]), **{field: value})
    )


def test_self_rehashed_root_authority_escalation_is_rejected() -> None:
    forged = _rehash_root(_root(ROOTS_THREE[0]), authority_class="ADVISORY")
    errors = multiroot.validate_root_decision_envelope_v01(forged)
    assert "multiroot_authority_transfer_forbidden" in errors
    assert "multiroot_identity_mismatch" not in errors


@pytest.mark.parametrize("evidence_class", multiroot.CROSS_ROOT_EVIDENCE_CLASSES)
def test_every_cross_root_evidence_class_builds(evidence_class: str) -> None:
    value = _cross(evidence_class=evidence_class)
    assert multiroot.validate_cross_root_evidence_ref_v01(value) == ()
    assert value.receipt_validated is (evidence_class == "EVIDENCE_RECEIPT")


@pytest.mark.parametrize("evidence_class", multiroot.CROSS_ROOT_EVIDENCE_CLASSES)
def test_cross_root_ref_identity_is_deterministic(evidence_class: str) -> None:
    assert _cross(evidence_class=evidence_class) == _cross(evidence_class=evidence_class)


@pytest.mark.parametrize(
    "evidence_class,receipt_validated,reason",
    (
        ("EVIDENCE_RECEIPT", False, "multiroot_receipt_validation_required"),
        ("EVIDENCE_RECEIPT", True, None),
        ("VALIDATED_EVIDENCE", True, "multiroot_cross_root_evidence_invalid"),
        ("CROSS_ROOT_ADVISORY", True, "multiroot_cross_root_evidence_invalid"),
    ),
)
def test_receipt_validation_coherence(evidence_class: str, receipt_validated: bool, reason: str | None) -> None:
    base = _cross(evidence_class=evidence_class)
    value = _rehash_cross(base, receipt_validated=receipt_validated)
    errors = multiroot.validate_cross_root_evidence_ref_v01(value)
    if reason is None:
        assert errors == ()
    else:
        assert reason in errors


@pytest.mark.parametrize(
    "value",
    ("", "0" * 63, "0" * 65, "G" * 64, True, None),
)
def test_cross_root_hash_must_be_exact_lowercase_sha256(value: object) -> None:
    errors = multiroot.validate_cross_root_evidence_ref_v01(
        replace(_cross(), evidence_artifact_hash=value)
    )
    assert "multiroot_cross_root_evidence_invalid" in errors


@pytest.mark.parametrize(
    "field",
    ("transaction_id", "source_root_id", "target_root_id", "evidence_artifact_id"),
)
@pytest.mark.parametrize("value", (None, "", True, "\ud800"))
def test_cross_root_text_field_rejection_matrix(field: str, value: object) -> None:
    assert multiroot.validate_cross_root_evidence_ref_v01(
        replace(_cross(), **{field: value})
    )


@pytest.mark.parametrize(
    "field,value,reason",
    (
        ("ref_id", "0" * 64, "multiroot_identity_mismatch"),
        ("evidence_class", "UNKNOWN", "multiroot_cross_root_evidence_invalid"),
        ("receipt_validated", 1, "multiroot_cross_root_evidence_invalid"),
        ("authority_transferred", True, "multiroot_authority_transfer_forbidden"),
        ("permission_created", True, "multiroot_permission_transfer_forbidden"),
        ("effect_authorized", True, "multiroot_effect_authorization_forbidden"),
        ("trace_refs", (), "multiroot_cross_root_evidence_invalid"),
        ("trace_refs", [], "multiroot_cross_root_evidence_invalid"),
        ("real_world_effects_count", 1, "multiroot_real_effect_forbidden"),
    ),
)
def test_cross_root_field_attack_matrix(field: str, value: object, reason: str) -> None:
    errors = multiroot.validate_cross_root_evidence_ref_v01(
        replace(_cross(), **{field: value})
    )
    assert reason in errors


@pytest.mark.parametrize(
    "field,reason",
    (
        ("authority_transferred", "multiroot_authority_transfer_forbidden"),
        ("permission_created", "multiroot_permission_transfer_forbidden"),
        ("effect_authorized", "multiroot_effect_authorization_forbidden"),
    ),
)
def test_self_rehashed_cross_root_escalations_rejected(field: str, reason: str) -> None:
    forged = _rehash_cross(_cross(), **{field: True})
    errors = multiroot.validate_cross_root_evidence_ref_v01(forged)
    assert reason in errors
    assert "multiroot_identity_mismatch" not in errors


def test_cross_root_self_reference_rejected() -> None:
    forged = _rehash_cross(_cross(), target_root_id=ROOTS_THREE[0])
    assert multiroot.validate_cross_root_evidence_ref_v01(forged) == (
        "multiroot_cross_root_self_reference",
    )


def test_three_root_all_accepted_pass(pass_three) -> None:
    result = multiroot.validate_multiroot_v01(pass_three)
    assert multiroot.validate_transaction_outcome_envelope_v01(pass_three) == ()
    assert pass_three.outcome_status == "PASS"
    assert result.final_status == "PASS"
    assert result.root_decision_count == 3
    assert result.accepted_root_count == 3
    assert result.non_accepted_root_count == 0
    assert result.errors == ()


def test_four_root_all_accepted_pass_without_three_root_hardcoding(pass_four) -> None:
    result = multiroot.validate_multiroot_v01(pass_four)
    assert pass_four.outcome_status == "PASS"
    assert result.final_status == "PASS"
    assert result.expected_root_ids == ROOTS_FOUR
    assert result.root_decision_count == 4
    assert result.accepted_root_count == 4


def test_mixed_outcomes_remain_visible_and_never_pass(mixed) -> None:
    result = multiroot.validate_multiroot_v01(mixed)
    assert mixed.outcome_status == "MIXED"
    assert mixed.mixed_outcomes_visible is True
    assert mixed.non_accepted_root_ids == ROOTS_THREE[1:]
    assert result.final_status == "MIXED"
    assert result.non_accepted_root_count == 2
    assert result.errors == ()


def test_incomplete_geometry_remains_visible_and_never_pass(incomplete) -> None:
    result = multiroot.validate_multiroot_v01(incomplete)
    assert incomplete.outcome_status == "INCOMPLETE"
    assert incomplete.observed_root_ids == ROOTS_THREE[:2]
    assert result.final_status == "INCOMPLETE"
    assert result.missing_root_ids == (ROOTS_THREE[2],)
    assert result.errors == ()


@pytest.mark.parametrize(
    "outcome_classes,expected_status",
    (
        (("ACCEPTED", "ACCEPTED", "ACCEPTED"), "PASS"),
        (("REJECTED", "REJECTED", "REJECTED"), "MIXED"),
        (("ACCEPTED", "NEEDS_USER", "ACCEPTED"), "MIXED"),
        (("NO_UPDATE", "ACCEPTED", "DEFERRED"), "MIXED"),
    ),
)
def test_outcome_status_matrix(outcome_classes: tuple[str, ...], expected_status: str) -> None:
    value = _outcome(ROOTS_THREE, outcome_classes)
    assert value.outcome_status == expected_status
    assert multiroot.validate_multiroot_v01(value).final_status == expected_status


@pytest.mark.parametrize("missing_count", (1, 2, 3))
def test_every_incomplete_root_count_is_visible(missing_count: int) -> None:
    observed_count = len(ROOTS_THREE) - missing_count
    value = _outcome(ROOTS_THREE, observed_count=observed_count)
    result = multiroot.validate_multiroot_v01(value)
    assert result.final_status == "INCOMPLETE"
    assert result.missing_root_ids == ROOTS_THREE[observed_count:]


def test_root_decision_order_must_follow_expected_order() -> None:
    decisions = tuple(_root(root_id, suffix=f"{index:03d}") for index, root_id in enumerate(ROOTS_THREE))
    with pytest.raises(ValueError, match="^multiroot_outcome_invalid$"):
        multiroot.build_transaction_outcome_envelope_v01(
            transaction_id=TRANSACTION_ID,
            expected_root_ids=ROOTS_THREE,
            root_decisions=(decisions[1], decisions[0], decisions[2]),
            cross_root_evidence_refs=(),
        )


@pytest.mark.parametrize("expected", ((), [], (ROOTS_THREE[0], ROOTS_THREE[0]), ("",)))
def test_expected_root_geometry_rejections(expected: object) -> None:
    with pytest.raises(ValueError, match="^multiroot_expected_roots_invalid$"):
        multiroot.build_transaction_outcome_envelope_v01(
            transaction_id=TRANSACTION_ID,
            expected_root_ids=expected,
            root_decisions=(),
            cross_root_evidence_refs=(),
        )


@pytest.mark.parametrize(
    "root_id",
    ("superroot", "root:superroot", "root:SUPERROOT", "root:super_root", "prefix:super_root:suffix", "SUPER_ROOT"),
)
def test_super_root_identity_rejected(root_id: str) -> None:
    with pytest.raises(ValueError, match="^multiroot_super_root_forbidden$"):
        multiroot.build_transaction_outcome_envelope_v01(
            transaction_id=TRANSACTION_ID,
            expected_root_ids=(ROOTS_THREE[0], root_id),
            root_decisions=(_root(ROOTS_THREE[0]),),
            cross_root_evidence_refs=(),
        )


def test_unknown_root_fails_closed_with_visible_identity(pass_three) -> None:
    unknown = _root("root:unknown", suffix="999")
    forged = _rehash_outcome(
        pass_three,
        root_decisions=(*pass_three.root_decisions, unknown),
        observed_root_ids=(*pass_three.observed_root_ids, unknown.root_id),
    )
    result = multiroot.validate_multiroot_v01(forged)
    assert result.final_status == "FAIL_CLOSED"
    assert result.unknown_root_ids == ("root:unknown",)
    assert "multiroot_unknown_root" in result.errors


def test_duplicate_root_fails_closed_with_visible_identity(pass_three) -> None:
    duplicate = _root(ROOTS_THREE[0], suffix="999")
    forged = _rehash_outcome(
        pass_three,
        root_decisions=(pass_three.root_decisions[0], duplicate, *pass_three.root_decisions[1:]),
        observed_root_ids=(ROOTS_THREE[0], ROOTS_THREE[0], *ROOTS_THREE[1:]),
    )
    result = multiroot.validate_multiroot_v01(forged)
    assert result.final_status == "FAIL_CLOSED"
    assert result.duplicate_root_ids == (ROOTS_THREE[0],)
    assert "multiroot_duplicate_root" in result.errors


def test_duplicate_decision_identity_fails_closed(pass_three) -> None:
    first = pass_three.root_decisions[0]
    second = _rehash_root(
        pass_three.root_decisions[1], root_decision_id=first.root_decision_id
    )
    forged = _rehash_outcome(
        pass_three,
        root_decisions=(first, second, pass_three.root_decisions[2]),
    )
    result = multiroot.validate_multiroot_v01(forged)
    assert result.final_status == "FAIL_CLOSED"
    assert "multiroot_duplicate_decision" in result.errors


def test_self_rehashed_silent_global_pass_over_mixed_is_rejected(mixed) -> None:
    forged = _rehash_outcome(
        mixed,
        outcome_status="PASS",
        mixed_outcomes_visible=False,
    )
    errors = multiroot.validate_transaction_outcome_envelope_v01(forged)
    assert "multiroot_silent_global_pass_forbidden" in errors
    assert "multiroot_status_mismatch" in errors
    assert multiroot.validate_multiroot_v01(forged).final_status == "FAIL_CLOSED"


def test_self_rehashed_pass_over_incomplete_is_rejected(incomplete) -> None:
    forged = _rehash_outcome(incomplete, outcome_status="PASS")
    errors = multiroot.validate_transaction_outcome_envelope_v01(forged)
    assert "multiroot_missing_root" in errors
    assert "multiroot_silent_global_pass_forbidden" in errors


def test_canonical_cross_root_evidence_order_and_binding() -> None:
    refs = (
        _cross(ROOTS_THREE[0], ROOTS_THREE[1], artifact_suffix="001"),
        _cross(ROOTS_THREE[1], ROOTS_THREE[2], artifact_suffix="002"),
    )
    value = _outcome(refs=refs)
    assert value.cross_root_evidence_refs == refs
    assert multiroot.validate_transaction_outcome_envelope_v01(value) == ()


def test_standalone_root_input_refs_remain_context_free() -> None:
    decision = _rehash_root(
        _root(ROOTS_THREE[0]),
        cross_root_input_refs=("ref:not-present-in-an-outcome",),
    )
    assert multiroot.validate_root_decision_envelope_v01(decision) == ()


def test_orphan_cross_root_input_ref_fails_outcome_closed() -> None:
    base = _outcome()
    decision = _rehash_root(
        base.root_decisions[0],
        cross_root_input_refs=("ref:not-present-in-an-outcome",),
    )
    forged = _rehash_outcome(
        base,
        root_decisions=(decision, *base.root_decisions[1:]),
    )
    errors = multiroot.validate_transaction_outcome_envelope_v01(forged)
    assert "multiroot_cross_root_evidence_invalid" in errors
    assert multiroot.validate_multiroot_v01(forged).final_status == "FAIL_CLOSED"


def test_malformed_cross_root_input_ref_has_contextual_evidence_error() -> None:
    base = _outcome()
    decision = _rehash_root(
        base.root_decisions[0],
        cross_root_input_refs=("",),
    )
    forged = _rehash_outcome(
        base,
        root_decisions=(decision, *base.root_decisions[1:]),
    )
    errors = multiroot.validate_transaction_outcome_envelope_v01(forged)
    assert "multiroot_root_decision_invalid" in errors
    assert "multiroot_cross_root_evidence_invalid" in errors


def test_wrong_target_cross_root_input_ref_fails_outcome_closed() -> None:
    ref = _cross(ROOTS_THREE[0], ROOTS_THREE[1])
    base = _outcome(refs=(ref,))
    wrong_consumer = _rehash_root(
        base.root_decisions[2],
        cross_root_input_refs=(ref.ref_id,),
    )
    forged = _rehash_outcome(
        base,
        root_decisions=(*base.root_decisions[:2], wrong_consumer),
    )
    errors = multiroot.validate_transaction_outcome_envelope_v01(forged)
    assert "multiroot_cross_root_evidence_invalid" in errors
    assert multiroot.validate_multiroot_v01(forged).final_status == "FAIL_CLOSED"


def test_correct_target_cross_root_input_ref_is_accepted() -> None:
    ref = _cross(ROOTS_THREE[0], ROOTS_THREE[1])
    base = _outcome(refs=(ref,))
    consumer = _rehash_root(
        base.root_decisions[1],
        cross_root_input_refs=(ref.ref_id,),
    )
    value = _rehash_outcome(
        base,
        root_decisions=(base.root_decisions[0], consumer, base.root_decisions[2]),
    )
    assert multiroot.validate_transaction_outcome_envelope_v01(value) == ()
    assert multiroot.validate_multiroot_v01(value).final_status == "PASS"


def test_one_root_cannot_consume_another_roots_target_ref() -> None:
    ref_for_beta = _cross(ROOTS_THREE[0], ROOTS_THREE[1])
    base = _outcome(refs=(ref_for_beta,))
    alpha = _rehash_root(
        base.root_decisions[0],
        cross_root_input_refs=(ref_for_beta.ref_id,),
    )
    forged = _rehash_outcome(
        base,
        root_decisions=(alpha, *base.root_decisions[1:]),
    )
    assert "multiroot_cross_root_evidence_invalid" in (
        multiroot.validate_transaction_outcome_envelope_v01(forged)
    )


def test_two_targeted_input_refs_in_canonical_order_are_accepted() -> None:
    refs = (
        _cross(ROOTS_THREE[0], ROOTS_THREE[1], artifact_suffix="001"),
        _cross(ROOTS_THREE[2], ROOTS_THREE[1], artifact_suffix="002"),
    )
    base = _outcome(refs=refs)
    consumer = _rehash_root(
        base.root_decisions[1],
        cross_root_input_refs=tuple(ref.ref_id for ref in refs),
    )
    value = _rehash_outcome(
        base,
        root_decisions=(base.root_decisions[0], consumer, base.root_decisions[2]),
    )
    assert multiroot.validate_transaction_outcome_envelope_v01(value) == ()


def test_reversed_input_ref_order_fails_after_outcome_rehash() -> None:
    refs = (
        _cross(ROOTS_THREE[0], ROOTS_THREE[1], artifact_suffix="001"),
        _cross(ROOTS_THREE[2], ROOTS_THREE[1], artifact_suffix="002"),
    )
    base = _outcome(refs=refs)
    consumer = _rehash_root(
        base.root_decisions[1],
        cross_root_input_refs=tuple(ref.ref_id for ref in reversed(refs)),
    )
    forged = _rehash_outcome(
        base,
        root_decisions=(base.root_decisions[0], consumer, base.root_decisions[2]),
    )
    assert "multiroot_outcome_invalid" in (
        multiroot.validate_transaction_outcome_envelope_v01(forged)
    )


def test_valid_unconsumed_cross_root_ref_remains_available() -> None:
    value = _outcome(refs=(_cross(),))
    assert all(not decision.cross_root_input_refs for decision in value.root_decisions)
    assert multiroot.validate_transaction_outcome_envelope_v01(value) == ()


def test_validated_receipt_input_for_correct_target_is_accepted() -> None:
    ref = _cross(evidence_class="EVIDENCE_RECEIPT")
    base = _outcome(refs=(ref,))
    consumer = _rehash_root(
        base.root_decisions[1],
        cross_root_input_refs=(ref.ref_id,),
    )
    value = _rehash_outcome(
        base,
        root_decisions=(base.root_decisions[0], consumer, base.root_decisions[2]),
    )
    assert multiroot.validate_transaction_outcome_envelope_v01(value) == ()


def test_unvalidated_receipt_cannot_enter_root_inputs() -> None:
    valid = _cross(evidence_class="EVIDENCE_RECEIPT")
    invalid = _rehash_cross(valid, receipt_validated=False)
    base = _outcome()
    consumer = _rehash_root(
        base.root_decisions[1],
        cross_root_input_refs=(invalid.ref_id,),
    )
    forged = _rehash_outcome(
        base,
        root_decisions=(base.root_decisions[0], consumer, base.root_decisions[2]),
        cross_root_evidence_refs=(invalid,),
    )
    errors = multiroot.validate_transaction_outcome_envelope_v01(forged)
    assert "multiroot_receipt_validation_required" in errors
    assert "multiroot_cross_root_evidence_invalid" in errors


def test_reordered_cross_root_evidence_is_rejected_even_self_rehashed() -> None:
    refs = (
        _cross(ROOTS_THREE[0], ROOTS_THREE[1], artifact_suffix="001"),
        _cross(ROOTS_THREE[1], ROOTS_THREE[2], artifact_suffix="002"),
    )
    value = _outcome(refs=refs)
    forged = _rehash_outcome(value, cross_root_evidence_refs=tuple(reversed(refs)))
    assert "multiroot_outcome_invalid" in multiroot.validate_transaction_outcome_envelope_v01(forged)
    with pytest.raises(ValueError, match="^multiroot_outcome_invalid$"):
        multiroot.transaction_outcome_envelope_to_plain_dict_v01(forged)


@pytest.mark.parametrize(
    "which,reason",
    (
        ("source", "multiroot_cross_root_unknown_source"),
        ("target", "multiroot_cross_root_unknown_target"),
    ),
)
def test_cross_root_unknown_endpoint_rejected(which: str, reason: str) -> None:
    changes = {"source_root_id": "root:unknown"} if which == "source" else {"target_root_id": "root:unknown"}
    ref = _rehash_cross(_cross(), **changes)
    base = _outcome()
    forged = _rehash_outcome(base, cross_root_evidence_refs=(ref,))
    assert reason in multiroot.validate_transaction_outcome_envelope_v01(forged)


def test_cross_root_transaction_mismatch_rejected() -> None:
    ref = _cross(transaction_id="txn:other")
    base = _outcome()
    forged = _rehash_outcome(base, cross_root_evidence_refs=(ref,))
    assert "multiroot_transaction_mismatch" in multiroot.validate_transaction_outcome_envelope_v01(forged)


def test_duplicate_cross_root_ref_id_rejected() -> None:
    ref = _cross()
    base = _outcome()
    forged = _rehash_outcome(base, cross_root_evidence_refs=(ref, ref))
    assert "multiroot_cross_root_evidence_invalid" in multiroot.validate_transaction_outcome_envelope_v01(forged)


def test_duplicate_cross_root_evidence_relation_rejected() -> None:
    first = _cross(artifact_suffix="same")
    second = _rehash_cross(first, trace_refs=("trace:different",))
    base = _outcome()
    forged = _rehash_outcome(base, cross_root_evidence_refs=(first, second))
    assert "multiroot_cross_root_evidence_invalid" in multiroot.validate_transaction_outcome_envelope_v01(forged)


@pytest.mark.parametrize(
    "field,reason",
    (
        ("authority_transferred", "multiroot_authority_transfer_forbidden"),
        ("permission_created", "multiroot_permission_transfer_forbidden"),
        ("effect_authorized", "multiroot_effect_authorization_forbidden"),
    ),
)
def test_cross_root_escalation_attacks_fail_outcome_closed(field: str, reason: str) -> None:
    ref = _rehash_cross(_cross(), **{field: True})
    base = _outcome()
    forged = _rehash_outcome(base, cross_root_evidence_refs=(ref,))
    result = multiroot.validate_multiroot_v01(forged)
    assert result.final_status == "FAIL_CLOSED"
    assert reason in result.errors


def test_unvalidated_receipt_fails_outcome_closed() -> None:
    ref = _rehash_cross(
        _cross(evidence_class="EVIDENCE_RECEIPT"), receipt_validated=False
    )
    base = _outcome()
    forged = _rehash_outcome(base, cross_root_evidence_refs=(ref,))
    result = multiroot.validate_multiroot_v01(forged)
    assert "multiroot_receipt_validation_required" in result.errors
    assert result.final_status == "FAIL_CLOSED"


@pytest.mark.parametrize(
    "field,value,reason",
    (
        ("outcome_id", "0" * 64, "multiroot_identity_mismatch"),
        ("transaction_id", "txn:other", "multiroot_transaction_mismatch"),
        ("expected_root_ids", [], "multiroot_expected_roots_invalid"),
        ("root_decisions", [], "multiroot_outcome_invalid"),
        ("cross_root_evidence_refs", [], "multiroot_outcome_invalid"),
        ("observed_root_ids", (), "multiroot_outcome_invalid"),
        ("accepted_root_ids", (), "multiroot_outcome_invalid"),
        ("non_accepted_root_ids", (ROOTS_THREE[0],), "multiroot_outcome_invalid"),
        ("outcome_status", "FAIL_CLOSED", "multiroot_status_mismatch"),
        ("mixed_outcomes_visible", True, "multiroot_status_mismatch"),
        ("super_root_created", True, "multiroot_super_root_forbidden"),
        ("authority_transfer_count", 1, "multiroot_authority_transfer_forbidden"),
        ("permission_creation_count", 1, "multiroot_permission_transfer_forbidden"),
        ("real_world_effects_count", 1, "multiroot_real_effect_forbidden"),
    ),
)
def test_every_outcome_field_mutation_rejected(field: str, value: object, reason: str, pass_three) -> None:
    errors = multiroot.validate_transaction_outcome_envelope_v01(
        replace(pass_three, **{field: value})
    )
    assert reason in errors


@pytest.mark.parametrize("value", (True, -1, 1, 999))
def test_nonzero_or_bool_outcome_effect_count_rejected(value: object, pass_three) -> None:
    forged = _rehash_outcome(pass_three, real_world_effects_count=value)
    assert "multiroot_real_effect_forbidden" in multiroot.validate_transaction_outcome_envelope_v01(forged)


@pytest.mark.parametrize(
    "fixture_name",
    ("pass_three", "pass_four", "mixed", "incomplete"),
)
def test_builders_results_and_ids_are_deterministic(fixture_name: str) -> None:
    builders = {
        "pass_three": lambda: _outcome(),
        "pass_four": lambda: _outcome(ROOTS_FOUR),
        "mixed": lambda: _outcome(ROOTS_THREE, ("ACCEPTED", "BLOCKED", "HELD")),
        "incomplete": lambda: _outcome(ROOTS_THREE, observed_count=2),
    }
    first = builders[fixture_name]()
    second = builders[fixture_name]()
    assert first == second
    assert first.outcome_id == second.outcome_id
    assert multiroot.transaction_outcome_envelope_to_plain_dict_v01(first) == multiroot.transaction_outcome_envelope_to_plain_dict_v01(second)
    assert multiroot.validate_multiroot_v01(first) == multiroot.validate_multiroot_v01(second)


@pytest.mark.parametrize(
    "fixture_name",
    ("pass_three", "pass_four", "mixed", "incomplete"),
)
def test_validation_result_projection_is_deterministic(fixture_name: str) -> None:
    outcomes = {
        "pass_three": _outcome(),
        "pass_four": _outcome(ROOTS_FOUR),
        "mixed": _outcome(ROOTS_THREE, ("ACCEPTED", "BLOCKED", "HELD")),
        "incomplete": _outcome(ROOTS_THREE, observed_count=2),
    }
    first = multiroot.validate_multiroot_v01(outcomes[fixture_name])
    second = multiroot.validate_multiroot_v01(outcomes[fixture_name])
    assert first.validation_id == second.validation_id
    assert multiroot.multiroot_validation_result_to_plain_dict_v01(first) == multiroot.multiroot_validation_result_to_plain_dict_v01(second)


def test_duplicate_root_fail_closed_result_publicly_projects(pass_three) -> None:
    duplicate = _root(ROOTS_THREE[0], suffix="999")
    forged = _rehash_outcome(
        pass_three,
        root_decisions=(
            pass_three.root_decisions[0],
            duplicate,
            *pass_three.root_decisions[1:],
        ),
        observed_root_ids=(ROOTS_THREE[0], ROOTS_THREE[0], *ROOTS_THREE[1:]),
    )
    result = multiroot.validate_multiroot_v01(forged)
    assert result.final_status == "FAIL_CLOSED"
    assert result.duplicate_root_ids == (ROOTS_THREE[0],)
    projected = multiroot.multiroot_validation_result_to_plain_dict_v01(result)
    assert projected["duplicate_root_ids"] == [ROOTS_THREE[0]]


def test_malformed_nested_decision_fail_closed_result_publicly_projects(
    pass_three,
) -> None:
    malformed = replace(
        pass_three,
        root_decisions=(object(), *pass_three.root_decisions[1:]),
    )
    result = multiroot.validate_multiroot_v01(malformed)
    assert result.final_status == "FAIL_CLOSED"
    assert result.root_decision_count == 3
    assert result.observed_root_ids == ROOTS_THREE[1:]
    assert result.missing_root_ids == (ROOTS_THREE[0],)
    classified = result.accepted_root_count + result.non_accepted_root_count
    assert len(result.observed_root_ids) <= classified <= result.root_decision_count
    projected = multiroot.multiroot_validation_result_to_plain_dict_v01(result)
    assert projected["final_status"] == "FAIL_CLOSED"


def test_malformed_nested_evidence_fail_closed_result_publicly_projects(
    pass_three,
) -> None:
    malformed = replace(pass_three, cross_root_evidence_refs=(object(),))
    result = multiroot.validate_multiroot_v01(malformed)
    assert result.final_status == "FAIL_CLOSED"
    assert result.cross_root_evidence_count == 1
    assert multiroot.multiroot_validation_result_to_plain_dict_v01(result)[
        "cross_root_evidence_count"
    ] == 1


def test_duplicate_expected_roots_remain_visible_in_fail_closed_geometry(
    pass_three,
) -> None:
    expected = (ROOTS_THREE[0], ROOTS_THREE[0], *ROOTS_THREE[1:])
    forged = _rehash_outcome(pass_three, expected_root_ids=expected)
    result = multiroot.validate_multiroot_v01(forged)
    assert result.final_status == "FAIL_CLOSED"
    assert result.expected_root_ids == expected
    assert result.duplicate_root_ids == (ROOTS_THREE[0],)
    assert "multiroot_duplicate_root" in result.errors
    multiroot.multiroot_validation_result_to_plain_dict_v01(result)


@pytest.mark.parametrize(
    "geometry_field",
    ("unknown_root_ids", "duplicate_root_ids", "missing_root_ids"),
)
def test_fail_closed_root_geometry_cannot_be_removed_and_rehashed(
    geometry_field: str,
    pass_three,
) -> None:
    if geometry_field == "unknown_root_ids":
        extra = _root("root:unknown", suffix="999")
        outcome = _rehash_outcome(
            pass_three,
            root_decisions=(*pass_three.root_decisions, extra),
            observed_root_ids=(*pass_three.observed_root_ids, extra.root_id),
        )
    elif geometry_field == "duplicate_root_ids":
        extra = _root(ROOTS_THREE[0], suffix="999")
        outcome = _rehash_outcome(
            pass_three,
            root_decisions=(
                pass_three.root_decisions[0],
                extra,
                *pass_three.root_decisions[1:],
            ),
            observed_root_ids=(ROOTS_THREE[0], ROOTS_THREE[0], *ROOTS_THREE[1:]),
        )
    else:
        outcome = replace(
            pass_three,
            root_decisions=(object(), *pass_three.root_decisions[1:]),
        )
    actual = multiroot.validate_multiroot_v01(outcome)
    assert getattr(actual, geometry_field)
    forged = _rehash_validation(actual, **{geometry_field: ()})
    with pytest.raises(ValueError, match="^multiroot_outcome_invalid$"):
        multiroot.multiroot_validation_result_to_plain_dict_v01(forged)


@pytest.mark.parametrize(
    "changes",
    (
        {"authority_transfer_count": 1},
        {"permission_creation_count": 1},
        {"super_root_created": True},
        {
            "observed_root_ids": (*ROOTS_THREE, "root:unknown"),
            "root_decision_count": 4,
            "accepted_root_count": 4,
        },
        {
            "observed_root_ids": ROOTS_THREE[:2],
            "root_decision_count": 2,
            "accepted_root_count": 2,
        },
        {"root_decision_count": 2},
    ),
)
def test_self_rehashed_impossible_pass_is_rejected(changes: dict[str, object]) -> None:
    forged = _rehash_validation(
        multiroot.validate_multiroot_v01(_outcome()),
        **changes,
    )
    with pytest.raises(ValueError, match="^multiroot_outcome_invalid$"):
        multiroot.multiroot_validation_result_to_plain_dict_v01(forged)


@pytest.mark.parametrize(
    "root_id",
    (
        "root:superroot",
        "root:super_root",
        "root:SUPERROOT",
        "root:SuPeR_RoOt",
    ),
)
def test_self_rehashed_pass_with_reserved_root_identity_is_rejected(
    root_id: str,
) -> None:
    actual = multiroot.validate_multiroot_v01(_outcome())
    forged = _rehash_validation(
        actual,
        expected_root_ids=(root_id,),
        observed_root_ids=(root_id,),
        root_decision_count=1,
        accepted_root_count=1,
    )
    assert "multiroot_super_root_forbidden" in (
        multiroot._validation_result_errors(forged)
    )
    with pytest.raises(ValueError, match="^multiroot_outcome_invalid$"):
        multiroot.multiroot_validation_result_to_plain_dict_v01(forged)


def _reserved_root_fail_closed_result(
    root_id: str = "root:superroot",
) -> multiroot.MultiRootValidationResultV01:
    base = _outcome()
    reserved_decision = _rehash_root(
        base.root_decisions[0],
        root_id=root_id,
        selected_subject_id=f"subject:{root_id}:001",
    )
    invalid = _rehash_outcome(
        base,
        expected_root_ids=(root_id,),
        root_decisions=(reserved_decision,),
        observed_root_ids=(root_id,),
        accepted_root_ids=(root_id,),
    )
    return multiroot.validate_multiroot_v01(invalid)


def test_genuine_reserved_root_fail_closed_result_publicly_projects() -> None:
    result = _reserved_root_fail_closed_result()
    assert result.final_status == "FAIL_CLOSED"
    assert result.super_root_created is True
    assert "multiroot_super_root_forbidden" in result.errors
    projected = multiroot.multiroot_validation_result_to_plain_dict_v01(result)
    assert projected["super_root_created"] is True


def test_reserved_root_cannot_be_hidden_by_clearing_super_root_flag() -> None:
    result = _reserved_root_fail_closed_result()
    forged = _rehash_validation(result, super_root_created=False)
    assert "multiroot_super_root_forbidden" in (
        multiroot._validation_result_errors(forged)
    )
    with pytest.raises(ValueError, match="^multiroot_outcome_invalid$"):
        multiroot.multiroot_validation_result_to_plain_dict_v01(forged)


def test_ordinary_domain_neutral_root_ids_remain_accepted() -> None:
    result = multiroot.validate_multiroot_v01(_outcome())
    assert result.final_status == "PASS"
    multiroot.multiroot_validation_result_to_plain_dict_v01(result)


@pytest.mark.parametrize(
    "count_field,reason",
    (
        ("authority_transfer_count", "multiroot_authority_transfer_forbidden"),
        ("permission_creation_count", "multiroot_permission_transfer_forbidden"),
    ),
)
def test_transfer_count_cannot_exceed_cross_root_evidence_count(
    count_field: str,
    reason: str,
) -> None:
    actual = multiroot.validate_multiroot_v01(_outcome())
    forged = _rehash_validation(
        actual,
        final_status="FAIL_CLOSED",
        errors=(reason,),
        **{count_field: 1},
    )
    assert forged.cross_root_evidence_count == 0
    assert "multiroot_outcome_invalid" in (
        multiroot._validation_result_errors(forged)
    )
    with pytest.raises(ValueError, match="^multiroot_outcome_invalid$"):
        multiroot.multiroot_validation_result_to_plain_dict_v01(forged)


def test_observed_root_count_cannot_exceed_classified_decision_count() -> None:
    actual = multiroot.validate_multiroot_v01(_outcome())
    forged = _rehash_validation(
        actual,
        accepted_root_count=2,
        final_status="FAIL_CLOSED",
        errors=("multiroot_outcome_invalid",),
    )
    assert len(forged.observed_root_ids) == 3
    assert forged.accepted_root_count + forged.non_accepted_root_count == 2
    assert forged.root_decision_count == 3
    assert "multiroot_outcome_invalid" in (
        multiroot._validation_result_errors(forged)
    )
    with pytest.raises(ValueError, match="^multiroot_outcome_invalid$"):
        multiroot.multiroot_validation_result_to_plain_dict_v01(forged)


def test_self_rehashed_mixed_result_must_expose_mixed_outcomes() -> None:
    actual = multiroot.validate_multiroot_v01(
        _outcome(ROOTS_THREE, ("ACCEPTED", "BLOCKED", "HELD"))
    )
    forged = _rehash_validation(actual, mixed_outcomes_visible=False)
    with pytest.raises(ValueError, match="^multiroot_outcome_invalid$"):
        multiroot.multiroot_validation_result_to_plain_dict_v01(forged)


def test_self_rehashed_incomplete_result_must_report_exact_missing_roots() -> None:
    actual = multiroot.validate_multiroot_v01(
        _outcome(ROOTS_THREE, observed_count=2)
    )
    forged = _rehash_validation(actual, missing_root_ids=(ROOTS_THREE[0],))
    with pytest.raises(ValueError, match="^multiroot_outcome_invalid$"):
        multiroot.multiroot_validation_result_to_plain_dict_v01(forged)


def test_self_rehashed_fail_closed_result_requires_errors(pass_three) -> None:
    malformed = replace(pass_three, root_decisions=(object(),))
    actual = multiroot.validate_multiroot_v01(malformed)
    forged = _rehash_validation(actual, errors=())
    with pytest.raises(ValueError, match="^multiroot_outcome_invalid$"):
        multiroot.multiroot_validation_result_to_plain_dict_v01(forged)


def test_sanitized_unexpected_exception_result_publicly_projects(
    monkeypatch,
) -> None:
    def fail(*args: object, **kwargs: object) -> tuple[str, ...]:
        raise RuntimeError("CALLER_SECRET")

    outcome = _outcome()
    monkeypatch.setattr(multiroot, "_outcome_errors", fail)
    result = multiroot.validate_multiroot_v01(outcome)
    assert result.errors == ("multiroot_unexpected_exception",)
    assert multiroot.multiroot_validation_result_to_plain_dict_v01(result)[
        "errors"
    ] == ["multiroot_unexpected_exception"]


@pytest.mark.parametrize(
    "field,value",
    (
        ("validation_id", "0" * 64),
        ("expected_root_ids", ROOTS_FOUR),
        ("observed_root_ids", (*ROOTS_THREE, "root:unknown")),
        ("root_decision_count", 2),
        ("accepted_root_count", 2),
        ("non_accepted_root_count", 1),
        ("unknown_root_ids", (ROOTS_THREE[0],)),
        ("duplicate_root_ids", (ROOTS_THREE[0],)),
        ("missing_root_ids", (ROOTS_THREE[2],)),
        ("mixed_outcomes_visible", True),
        ("authority_transfer_count", 1),
        ("permission_creation_count", 1),
        ("super_root_created", True),
        ("final_status", "MIXED"),
        ("errors", ("multiroot_outcome_invalid",)),
        ("real_world_effects_count", 1),
    ),
)
def test_validation_result_incoherent_field_mutation_is_rejected(
    field: str,
    value: object,
) -> None:
    actual = multiroot.validate_multiroot_v01(_outcome())
    forged = (
        replace(actual, validation_id=value)
        if field == "validation_id"
        else _rehash_validation(actual, **{field: value})
    )
    with pytest.raises(ValueError, match="^multiroot_outcome_invalid$"):
        multiroot.multiroot_validation_result_to_plain_dict_v01(forged)


@pytest.mark.parametrize(
    "field,value",
    (
        ("transaction_id", "txn:neutral:multiroot:alternate"),
        ("cross_root_evidence_count", 1),
    ),
)
def test_validation_result_coherent_field_mutation_changes_identity(
    field: str,
    value: object,
) -> None:
    actual = multiroot.validate_multiroot_v01(_outcome())
    changed = _rehash_validation(actual, **{field: value})
    assert changed.validation_id != actual.validation_id
    projected = multiroot.multiroot_validation_result_to_plain_dict_v01(changed)
    assert projected[field] == value


@pytest.mark.parametrize(
    "fixture",
    (
        lambda: _outcome(),
        lambda: _outcome(ROOTS_THREE, ("ACCEPTED", "BLOCKED", "HELD")),
        lambda: _outcome(ROOTS_THREE, observed_count=2),
    ),
)
def test_canonical_status_validation_results_still_project(fixture) -> None:
    result = multiroot.validate_multiroot_v01(fixture())
    assert multiroot.multiroot_validation_result_to_plain_dict_v01(result)[
        "final_status"
    ] == result.final_status


@pytest.mark.parametrize("kind", ("root", "cross", "outcome", "validation"))
def test_public_projections_are_json_safe_independent_and_owned(kind: str) -> None:
    values = {
        "root": (_root(ROOTS_THREE[0]), multiroot.root_decision_envelope_to_plain_dict_v01),
        "cross": (_cross(), multiroot.cross_root_evidence_ref_to_plain_dict_v01),
        "outcome": (_outcome(), multiroot.transaction_outcome_envelope_to_plain_dict_v01),
        "validation": (multiroot.validate_multiroot_v01(_outcome()), multiroot.multiroot_validation_result_to_plain_dict_v01),
    }
    source, project = values[kind]
    first = project(source)
    second = project(source)
    assert first == second and first is not second
    assert not _contains_forbidden_projection_value(first)
    canonical_json_bytes_v01(first)
    json.dumps(first, sort_keys=True, allow_nan=False)
    first.clear()
    assert project(source) == second


@pytest.mark.parametrize("kind", ("root", "cross", "outcome", "validation"))
def test_projection_rejects_malformed_exact_dataclass(kind: str) -> None:
    if kind == "root":
        value = replace(_root(ROOTS_THREE[0]), root_commit_created=False)
        project = multiroot.root_decision_envelope_to_plain_dict_v01
        reason = "multiroot_root_decision_invalid"
    elif kind == "cross":
        value = replace(_cross(), permission_created=True)
        project = multiroot.cross_root_evidence_ref_to_plain_dict_v01
        reason = "multiroot_cross_root_evidence_invalid"
    elif kind == "outcome":
        value = replace(_outcome(), outcome_status="MIXED")
        project = multiroot.transaction_outcome_envelope_to_plain_dict_v01
        reason = "multiroot_outcome_invalid"
    else:
        value = replace(multiroot.validate_multiroot_v01(_outcome()), validation_id="0" * 64)
        project = multiroot.multiroot_validation_result_to_plain_dict_v01
        reason = "multiroot_outcome_invalid"
    with pytest.raises(ValueError, match=f"^{reason}$") as caught:
        project(value)
    assert caught.value.__cause__ is None


class _HostileIdentity:
    def __eq__(self, other: object) -> bool:
        raise OSError("CALLER_SECRET")

    def __hash__(self) -> int:
        raise OSError("CALLER_SECRET")


@pytest.mark.parametrize("field", ("root_id", "outcome_class", "evidence_refs"))
def test_hostile_root_fields_are_sanitized(field: str) -> None:
    value: object = (_HostileIdentity(),) if field == "evidence_refs" else _HostileIdentity()
    errors = multiroot.validate_root_decision_envelope_v01(
        replace(_root(ROOTS_THREE[0]), **{field: value})
    )
    assert errors
    assert "CALLER_SECRET" not in repr(errors)


@pytest.mark.parametrize("field", ("source_root_id", "evidence_class", "trace_refs"))
def test_hostile_cross_fields_are_sanitized(field: str) -> None:
    value: object = (_HostileIdentity(),) if field == "trace_refs" else _HostileIdentity()
    errors = multiroot.validate_cross_root_evidence_ref_v01(
        replace(_cross(), **{field: value})
    )
    assert errors
    assert "CALLER_SECRET" not in repr(errors)


@pytest.mark.parametrize("exception_type", (ValueError, RuntimeError, OSError))
def test_builder_sanitizes_ordinary_internal_exceptions(monkeypatch, exception_type) -> None:
    def fail(*args: object, **kwargs: object) -> tuple[str, ...]:
        raise exception_type("CALLER_SECRET")

    monkeypatch.setattr(multiroot, "_root_decision_errors", fail)
    with pytest.raises(ValueError, match="^multiroot_root_decision_invalid$") as caught:
        _root(ROOTS_THREE[0])
    assert caught.value.__cause__ is None
    assert "CALLER_SECRET" not in str(caught.value)


@pytest.mark.parametrize("exception_type", (RuntimeError, OSError))
def test_validator_sanitizes_ordinary_internal_exceptions(monkeypatch, exception_type) -> None:
    outcome = _outcome()

    def fail(*args: object, **kwargs: object) -> tuple[str, ...]:
        raise exception_type("CALLER_SECRET")

    monkeypatch.setattr(multiroot, "_outcome_errors", fail)
    assert multiroot.validate_transaction_outcome_envelope_v01(outcome) == (
        "multiroot_unexpected_exception",
    )


def test_base_exception_not_swallowed(monkeypatch) -> None:
    def interrupt(*args: object, **kwargs: object) -> tuple[str, ...]:
        raise KeyboardInterrupt

    monkeypatch.setattr(multiroot, "_outcome_errors", interrupt)
    with pytest.raises(KeyboardInterrupt):
        multiroot.validate_transaction_outcome_envelope_v01(_outcome())


@pytest.mark.parametrize(
    "token",
    (
        "hedgehog.domains",
        "import demo",
        "import tests",
        "requests",
        "socket",
        "urllib",
        "pathlib",
        "subprocess",
        "cryptography",
        "RootSignerCapabilityV01",
        "RootOrchestrator",
        "ActionCommitPacket",
        "EffectFirewallV01",
        "register_root",
        "register_domain",
        "register_provider",
        "callback",
        "execute_effect",
        "random.",
        "datetime.now",
        "open(",
        ".tmp",
    ),
)
def test_static_forbidden_tokens_absent(token: str) -> None:
    assert token not in MODULE_PATH.read_text(encoding="utf-8")


def test_static_import_boundary() -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    imports = {
        node.module or ""
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    }
    assert imports <= {
        "__future__",
        "dataclasses",
        "hedgehog.kernel.integrity_replay_v01",
    }


def test_no_module_global_mutable_registry() -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            assert not isinstance(node.value, (ast.List, ast.Dict, ast.Set))


@pytest.mark.parametrize(
    "name",
    (
        "register_root_v01",
        "register_domain_v01",
        "register_provider_v01",
        "add_root_v01",
        "remove_root_v01",
        "create_super_root_v01",
        "sign_for_other_root_v01",
        "execute_effect_v01",
    ),
)
def test_forbidden_public_apis_absent(name: str) -> None:
    assert name not in vars(multiroot)
