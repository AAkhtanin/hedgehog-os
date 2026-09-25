"""Pure in-memory deterministic domain-neutral MultiRoot protocol geometry.

Every Root remains independently sovereign: there is no SuperRoot, authority
transfer, permission transfer, or Root signing. The module calls no provider,
LLM, Gemini service, network, filesystem, clock, or random source; performs no
dynamic Root registration; creates no Root, FinalOutput, or effect; and makes
no production-certification claim. Cross-Root references carry validated
evidence only, and transaction outcomes preserve mixed and incomplete Root
geometry without synthesizing one global Root decision.
"""

from __future__ import annotations

from dataclasses import dataclass as _dataclass

from hedgehog.kernel.integrity_replay_v01 import (
    canonical_json_bytes_v01 as _canonical_json_bytes_v01,
    domain_separated_sha256_hex_v01 as _domain_separated_sha256_hex_v01,
)

del annotations


MODULE_ID = "kernel_multiroot_v01"
SLICE_ID = "domain_neutral_reference_kernel_gate1_g1d2"
MULTIROOT_VERSION = "v0.1"

STATUS_PASS = "PASS"
STATUS_MIXED = "MIXED"
STATUS_INCOMPLETE = "INCOMPLETE"
STATUS_FAIL_CLOSED = "FAIL_CLOSED"
MULTIROOT_STATUSES = (
    STATUS_PASS,
    STATUS_MIXED,
    STATUS_INCOMPLETE,
    STATUS_FAIL_CLOSED,
)

ROOT_AUTHORITY_CLASS = "ROOT_OWNED"
ROOT_OUTCOME_CLASSES = (
    "ACCEPTED",
    "REJECTED",
    "BLOCKED",
    "HELD",
    "DEFERRED",
    "NEEDS_USER",
    "NEEDS_MORE_EVIDENCE",
    "NO_UPDATE",
)
CROSS_ROOT_EVIDENCE_CLASSES = (
    "VALIDATED_EVIDENCE",
    "EVIDENCE_RECEIPT",
    "CROSS_ROOT_ADVISORY",
)

_ROOT_ENVELOPE_DOMAIN = "hedgehog.kernel.multiroot.root_decision_envelope.v01"
_CROSS_ROOT_REF_DOMAIN = "hedgehog.kernel.multiroot.cross_root_evidence_ref.v01"
_OUTCOME_DOMAIN = "hedgehog.kernel.multiroot.transaction_outcome_envelope.v01"
_VALIDATION_DOMAIN = "hedgehog.kernel.multiroot.validation_result.v01"
_ERROR_REASONS = (
    "multiroot_root_decision_invalid",
    "multiroot_cross_root_evidence_invalid",
    "multiroot_outcome_invalid",
    "multiroot_identity_mismatch",
    "multiroot_transaction_mismatch",
    "multiroot_expected_roots_invalid",
    "multiroot_unknown_root",
    "multiroot_duplicate_root",
    "multiroot_duplicate_decision",
    "multiroot_missing_root",
    "multiroot_super_root_forbidden",
    "multiroot_cross_root_self_reference",
    "multiroot_cross_root_unknown_source",
    "multiroot_cross_root_unknown_target",
    "multiroot_authority_transfer_forbidden",
    "multiroot_permission_transfer_forbidden",
    "multiroot_effect_authorization_forbidden",
    "multiroot_receipt_validation_required",
    "multiroot_silent_global_pass_forbidden",
    "multiroot_status_mismatch",
    "multiroot_real_effect_forbidden",
    "multiroot_unexpected_exception",
)


@_dataclass(frozen=True, slots=True)
class RootDecisionEnvelopeV01:
    envelope_id: str
    transaction_id: str
    root_id: str
    root_decision_id: str
    source_decision_ref: str
    outcome_class: str
    reason_code: str
    selected_subject_id: str | None
    root_commit_created: bool
    authority_class: str
    evidence_refs: tuple[str, ...]
    cross_root_input_refs: tuple[str, ...]
    real_world_effects_count: int


@_dataclass(frozen=True, slots=True)
class CrossRootEvidenceRefV01:
    ref_id: str
    transaction_id: str
    source_root_id: str
    target_root_id: str
    evidence_artifact_id: str
    evidence_artifact_hash: str
    evidence_class: str
    receipt_validated: bool
    authority_transferred: bool
    permission_created: bool
    effect_authorized: bool
    trace_refs: tuple[str, ...]
    real_world_effects_count: int


@_dataclass(frozen=True, slots=True)
class TransactionOutcomeEnvelopeV01:
    outcome_id: str
    transaction_id: str
    expected_root_ids: tuple[str, ...]
    root_decisions: tuple[RootDecisionEnvelopeV01, ...]
    cross_root_evidence_refs: tuple[CrossRootEvidenceRefV01, ...]
    observed_root_ids: tuple[str, ...]
    accepted_root_ids: tuple[str, ...]
    non_accepted_root_ids: tuple[str, ...]
    outcome_status: str
    mixed_outcomes_visible: bool
    super_root_created: bool
    authority_transfer_count: int
    permission_creation_count: int
    real_world_effects_count: int


@_dataclass(frozen=True, slots=True)
class MultiRootValidationResultV01:
    validation_id: str
    transaction_id: str
    expected_root_ids: tuple[str, ...]
    observed_root_ids: tuple[str, ...]
    root_decision_count: int
    cross_root_evidence_count: int
    accepted_root_count: int
    non_accepted_root_count: int
    unknown_root_ids: tuple[str, ...]
    duplicate_root_ids: tuple[str, ...]
    missing_root_ids: tuple[str, ...]
    mixed_outcomes_visible: bool
    authority_transfer_count: int
    permission_creation_count: int
    super_root_created: bool
    final_status: str
    errors: tuple[str, ...]
    real_world_effects_count: int


def build_root_decision_envelope_v01(
    *,
    transaction_id: str,
    root_id: str,
    root_decision_id: str,
    source_decision_ref: str,
    outcome_class: str,
    reason_code: str,
    selected_subject_id: str | None,
    evidence_refs: tuple[str, ...],
    cross_root_input_refs: tuple[str, ...],
) -> RootDecisionEnvelopeV01:
    try:
        provisional = RootDecisionEnvelopeV01(
            envelope_id="0" * 64,
            transaction_id=transaction_id,
            root_id=root_id,
            root_decision_id=root_decision_id,
            source_decision_ref=source_decision_ref,
            outcome_class=outcome_class,
            reason_code=reason_code,
            selected_subject_id=selected_subject_id,
            root_commit_created=True,
            authority_class=ROOT_AUTHORITY_CLASS,
            evidence_refs=evidence_refs,
            cross_root_input_refs=cross_root_input_refs,
            real_world_effects_count=0,
        )
        errors = _root_decision_errors(provisional, check_id=False)
        if errors:
            raise ValueError(errors[0])
        material = _root_decision_plain(provisional)
        material.pop("envelope_id")
        return RootDecisionEnvelopeV01(
            envelope_id=_hash(_ROOT_ENVELOPE_DOMAIN, material),
            transaction_id=transaction_id,
            root_id=root_id,
            root_decision_id=root_decision_id,
            source_decision_ref=source_decision_ref,
            outcome_class=outcome_class,
            reason_code=reason_code,
            selected_subject_id=selected_subject_id,
            root_commit_created=True,
            authority_class=ROOT_AUTHORITY_CLASS,
            evidence_refs=evidence_refs,
            cross_root_input_refs=cross_root_input_refs,
            real_world_effects_count=0,
        )
    except ValueError as exc:
        raise ValueError(
            _stable_reason(exc, _ERROR_REASONS)
            or "multiroot_root_decision_invalid"
        ) from None
    except Exception:
        raise ValueError("multiroot_root_decision_invalid") from None


def validate_root_decision_envelope_v01(
    envelope: object,
) -> tuple[str, ...]:
    try:
        return _root_decision_errors(envelope, check_id=True)
    except Exception:
        return ("multiroot_unexpected_exception",)


def build_cross_root_evidence_ref_v01(
    *,
    transaction_id: str,
    source_root_id: str,
    target_root_id: str,
    evidence_artifact_id: str,
    evidence_artifact_hash: str,
    evidence_class: str,
    receipt_validated: bool,
    trace_refs: tuple[str, ...],
) -> CrossRootEvidenceRefV01:
    try:
        provisional = CrossRootEvidenceRefV01(
            ref_id="0" * 64,
            transaction_id=transaction_id,
            source_root_id=source_root_id,
            target_root_id=target_root_id,
            evidence_artifact_id=evidence_artifact_id,
            evidence_artifact_hash=evidence_artifact_hash,
            evidence_class=evidence_class,
            receipt_validated=receipt_validated,
            authority_transferred=False,
            permission_created=False,
            effect_authorized=False,
            trace_refs=trace_refs,
            real_world_effects_count=0,
        )
        errors = _cross_root_errors(provisional, check_id=False)
        if errors:
            raise ValueError(errors[0])
        material = _cross_root_plain(provisional)
        material.pop("ref_id")
        return CrossRootEvidenceRefV01(
            ref_id=_hash(_CROSS_ROOT_REF_DOMAIN, material),
            transaction_id=transaction_id,
            source_root_id=source_root_id,
            target_root_id=target_root_id,
            evidence_artifact_id=evidence_artifact_id,
            evidence_artifact_hash=evidence_artifact_hash,
            evidence_class=evidence_class,
            receipt_validated=receipt_validated,
            authority_transferred=False,
            permission_created=False,
            effect_authorized=False,
            trace_refs=trace_refs,
            real_world_effects_count=0,
        )
    except ValueError as exc:
        raise ValueError(
            _stable_reason(exc, _ERROR_REASONS)
            or "multiroot_cross_root_evidence_invalid"
        ) from None
    except Exception:
        raise ValueError("multiroot_cross_root_evidence_invalid") from None


def validate_cross_root_evidence_ref_v01(
    ref: object,
) -> tuple[str, ...]:
    try:
        return _cross_root_errors(ref, check_id=True)
    except Exception:
        return ("multiroot_unexpected_exception",)


def build_transaction_outcome_envelope_v01(
    *,
    transaction_id: str,
    expected_root_ids: tuple[str, ...],
    root_decisions: tuple[RootDecisionEnvelopeV01, ...],
    cross_root_evidence_refs: tuple[CrossRootEvidenceRefV01, ...],
) -> TransactionOutcomeEnvelopeV01:
    try:
        derived = _derive_outcome_fields(
            expected_root_ids=expected_root_ids,
            root_decisions=root_decisions,
        )
        provisional = TransactionOutcomeEnvelopeV01(
            outcome_id="0" * 64,
            transaction_id=transaction_id,
            expected_root_ids=expected_root_ids,
            root_decisions=root_decisions,
            cross_root_evidence_refs=cross_root_evidence_refs,
            observed_root_ids=derived[0],
            accepted_root_ids=derived[1],
            non_accepted_root_ids=derived[2],
            outcome_status=derived[3],
            mixed_outcomes_visible=derived[4],
            super_root_created=False,
            authority_transfer_count=0,
            permission_creation_count=0,
            real_world_effects_count=0,
        )
        errors = _outcome_errors(provisional, check_id=False)
        if errors:
            raise ValueError(errors[0])
        material = _outcome_plain(provisional)
        material.pop("outcome_id")
        return TransactionOutcomeEnvelopeV01(
            outcome_id=_hash(_OUTCOME_DOMAIN, material),
            transaction_id=transaction_id,
            expected_root_ids=expected_root_ids,
            root_decisions=root_decisions,
            cross_root_evidence_refs=cross_root_evidence_refs,
            observed_root_ids=derived[0],
            accepted_root_ids=derived[1],
            non_accepted_root_ids=derived[2],
            outcome_status=derived[3],
            mixed_outcomes_visible=derived[4],
            super_root_created=False,
            authority_transfer_count=0,
            permission_creation_count=0,
            real_world_effects_count=0,
        )
    except ValueError as exc:
        raise ValueError(
            _stable_reason(exc, _ERROR_REASONS) or "multiroot_outcome_invalid"
        ) from None
    except Exception:
        raise ValueError("multiroot_outcome_invalid") from None


def validate_transaction_outcome_envelope_v01(
    outcome: object,
) -> tuple[str, ...]:
    try:
        return _outcome_errors(outcome, check_id=True)
    except Exception:
        return ("multiroot_unexpected_exception",)


def validate_multiroot_v01(
    outcome: object,
) -> MultiRootValidationResultV01:
    try:
        errors = _outcome_errors(outcome, check_id=True)
        geometry = _validation_geometry(outcome)
        final_status = (
            outcome.outcome_status
            if not errors
            and type(outcome) is TransactionOutcomeEnvelopeV01
            and outcome.outcome_status
            in {STATUS_PASS, STATUS_MIXED, STATUS_INCOMPLETE}
            else STATUS_FAIL_CLOSED
        )
        fields = {
            "transaction_id": geometry[0],
            "expected_root_ids": list(geometry[1]),
            "observed_root_ids": list(geometry[2]),
            "root_decision_count": geometry[3],
            "cross_root_evidence_count": geometry[4],
            "accepted_root_count": geometry[5],
            "non_accepted_root_count": geometry[6],
            "unknown_root_ids": list(geometry[7]),
            "duplicate_root_ids": list(geometry[8]),
            "missing_root_ids": list(geometry[9]),
            "mixed_outcomes_visible": geometry[10],
            "authority_transfer_count": geometry[11],
            "permission_creation_count": geometry[12],
            "super_root_created": geometry[13],
            "final_status": final_status,
            "errors": list(errors),
            "real_world_effects_count": 0,
        }
        return MultiRootValidationResultV01(
            validation_id=_hash(_VALIDATION_DOMAIN, fields),
            transaction_id=geometry[0],
            expected_root_ids=geometry[1],
            observed_root_ids=geometry[2],
            root_decision_count=geometry[3],
            cross_root_evidence_count=geometry[4],
            accepted_root_count=geometry[5],
            non_accepted_root_count=geometry[6],
            unknown_root_ids=geometry[7],
            duplicate_root_ids=geometry[8],
            missing_root_ids=geometry[9],
            mixed_outcomes_visible=geometry[10],
            authority_transfer_count=geometry[11],
            permission_creation_count=geometry[12],
            super_root_created=geometry[13],
            final_status=final_status,
            errors=errors,
            real_world_effects_count=0,
        )
    except Exception:
        fields = {
            "transaction_id": "",
            "expected_root_ids": [],
            "observed_root_ids": [],
            "root_decision_count": 0,
            "cross_root_evidence_count": 0,
            "accepted_root_count": 0,
            "non_accepted_root_count": 0,
            "unknown_root_ids": [],
            "duplicate_root_ids": [],
            "missing_root_ids": [],
            "mixed_outcomes_visible": False,
            "authority_transfer_count": 0,
            "permission_creation_count": 0,
            "super_root_created": False,
            "final_status": STATUS_FAIL_CLOSED,
            "errors": ["multiroot_unexpected_exception"],
            "real_world_effects_count": 0,
        }
        return MultiRootValidationResultV01(
            validation_id=_hash(_VALIDATION_DOMAIN, fields),
            transaction_id="",
            expected_root_ids=(),
            observed_root_ids=(),
            root_decision_count=0,
            cross_root_evidence_count=0,
            accepted_root_count=0,
            non_accepted_root_count=0,
            unknown_root_ids=(),
            duplicate_root_ids=(),
            missing_root_ids=(),
            mixed_outcomes_visible=False,
            authority_transfer_count=0,
            permission_creation_count=0,
            super_root_created=False,
            final_status=STATUS_FAIL_CLOSED,
            errors=("multiroot_unexpected_exception",),
            real_world_effects_count=0,
        )


def root_decision_envelope_to_plain_dict_v01(
    envelope: RootDecisionEnvelopeV01,
) -> dict[str, object]:
    try:
        if _root_decision_errors(envelope, check_id=True):
            raise ValueError("multiroot_root_decision_invalid")
        result = _root_decision_plain(envelope)
        _canonical_json_bytes_v01(result)
        return result
    except Exception:
        raise ValueError("multiroot_root_decision_invalid") from None


def cross_root_evidence_ref_to_plain_dict_v01(
    ref: CrossRootEvidenceRefV01,
) -> dict[str, object]:
    try:
        if _cross_root_errors(ref, check_id=True):
            raise ValueError("multiroot_cross_root_evidence_invalid")
        result = _cross_root_plain(ref)
        _canonical_json_bytes_v01(result)
        return result
    except Exception:
        raise ValueError("multiroot_cross_root_evidence_invalid") from None


def transaction_outcome_envelope_to_plain_dict_v01(
    outcome: TransactionOutcomeEnvelopeV01,
) -> dict[str, object]:
    try:
        if _outcome_errors(outcome, check_id=True):
            raise ValueError("multiroot_outcome_invalid")
        result = _outcome_plain(outcome)
        _canonical_json_bytes_v01(result)
        return result
    except Exception:
        raise ValueError("multiroot_outcome_invalid") from None


def multiroot_validation_result_to_plain_dict_v01(
    result: MultiRootValidationResultV01,
) -> dict[str, object]:
    try:
        if _validation_result_errors(result):
            raise ValueError("multiroot_outcome_invalid")
        projected = _validation_result_plain(result)
        _canonical_json_bytes_v01(projected)
        return projected
    except Exception:
        raise ValueError("multiroot_outcome_invalid") from None


def _root_decision_errors(
    envelope: object,
    *,
    check_id: bool,
) -> tuple[str, ...]:
    if type(envelope) is not RootDecisionEnvelopeV01:
        return ("multiroot_root_decision_invalid",)
    errors: list[str] = []
    for value in (
        envelope.transaction_id,
        envelope.root_id,
        envelope.root_decision_id,
        envelope.source_decision_ref,
        envelope.reason_code,
    ):
        if not _valid_text(value):
            errors.append("multiroot_root_decision_invalid")
            break
    if _valid_text(envelope.root_id) and _super_root_id(envelope.root_id):
        errors.append("multiroot_super_root_forbidden")
    if (
        type(envelope.outcome_class) is not str
        or envelope.outcome_class not in ROOT_OUTCOME_CLASSES
    ):
        errors.append("multiroot_root_decision_invalid")
    if envelope.selected_subject_id is not None and not _valid_text(
        envelope.selected_subject_id
    ):
        errors.append("multiroot_root_decision_invalid")
    if envelope.outcome_class == "ACCEPTED":
        if envelope.selected_subject_id is None:
            errors.append("multiroot_root_decision_invalid")
    elif envelope.selected_subject_id is not None:
        errors.append("multiroot_root_decision_invalid")
    if envelope.root_commit_created is not True:
        errors.append("multiroot_root_decision_invalid")
    if envelope.authority_class != ROOT_AUTHORITY_CLASS:
        errors.append("multiroot_authority_transfer_forbidden")
    if not _valid_text_tuple(envelope.evidence_refs, allow_empty=True):
        errors.append("multiroot_root_decision_invalid")
    if not _valid_text_tuple(envelope.cross_root_input_refs, allow_empty=True):
        errors.append("multiroot_root_decision_invalid")
    if type(envelope.real_world_effects_count) is not int:
        errors.append("multiroot_real_effect_forbidden")
    elif envelope.real_world_effects_count != 0:
        errors.append("multiroot_real_effect_forbidden")
    if check_id:
        if not _valid_sha256(envelope.envelope_id):
            errors.append("multiroot_identity_mismatch")
        elif not errors:
            material = _root_decision_plain(envelope)
            material.pop("envelope_id")
            if envelope.envelope_id != _hash(_ROOT_ENVELOPE_DOMAIN, material):
                errors.append("multiroot_identity_mismatch")
    return _dedupe(errors)


def _cross_root_errors(
    ref: object,
    *,
    check_id: bool,
) -> tuple[str, ...]:
    if type(ref) is not CrossRootEvidenceRefV01:
        return ("multiroot_cross_root_evidence_invalid",)
    errors: list[str] = []
    for value in (
        ref.transaction_id,
        ref.source_root_id,
        ref.target_root_id,
        ref.evidence_artifact_id,
    ):
        if not _valid_text(value):
            errors.append("multiroot_cross_root_evidence_invalid")
            break
    for root_id in (ref.source_root_id, ref.target_root_id):
        if _valid_text(root_id) and _super_root_id(root_id):
            errors.append("multiroot_super_root_forbidden")
    if (
        _valid_text(ref.source_root_id)
        and _valid_text(ref.target_root_id)
        and ref.source_root_id == ref.target_root_id
    ):
        errors.append("multiroot_cross_root_self_reference")
    if not _valid_sha256(ref.evidence_artifact_hash):
        errors.append("multiroot_cross_root_evidence_invalid")
    if (
        type(ref.evidence_class) is not str
        or ref.evidence_class not in CROSS_ROOT_EVIDENCE_CLASSES
    ):
        errors.append("multiroot_cross_root_evidence_invalid")
    if type(ref.receipt_validated) is not bool:
        errors.append("multiroot_cross_root_evidence_invalid")
    elif ref.evidence_class == "EVIDENCE_RECEIPT":
        if ref.receipt_validated is not True:
            errors.append("multiroot_receipt_validation_required")
    elif ref.receipt_validated is not False:
        errors.append("multiroot_cross_root_evidence_invalid")
    if ref.authority_transferred is not False:
        errors.append("multiroot_authority_transfer_forbidden")
    if ref.permission_created is not False:
        errors.append("multiroot_permission_transfer_forbidden")
    if ref.effect_authorized is not False:
        errors.append("multiroot_effect_authorization_forbidden")
    if not _valid_text_tuple(ref.trace_refs, allow_empty=False):
        errors.append("multiroot_cross_root_evidence_invalid")
    if type(ref.real_world_effects_count) is not int:
        errors.append("multiroot_real_effect_forbidden")
    elif ref.real_world_effects_count != 0:
        errors.append("multiroot_real_effect_forbidden")
    if check_id:
        if not _valid_sha256(ref.ref_id):
            errors.append("multiroot_identity_mismatch")
        elif not errors:
            material = _cross_root_plain(ref)
            material.pop("ref_id")
            if ref.ref_id != _hash(_CROSS_ROOT_REF_DOMAIN, material):
                errors.append("multiroot_identity_mismatch")
    return _dedupe(errors)


def _outcome_errors(
    outcome: object,
    *,
    check_id: bool,
) -> tuple[str, ...]:
    if type(outcome) is not TransactionOutcomeEnvelopeV01:
        return ("multiroot_outcome_invalid",)
    errors: list[str] = []
    if not _valid_text(outcome.transaction_id):
        errors.append("multiroot_outcome_invalid")
    expected_valid = _valid_text_tuple(outcome.expected_root_ids, allow_empty=False)
    if not expected_valid:
        errors.append("multiroot_expected_roots_invalid")
    elif any(_super_root_id(root_id) for root_id in outcome.expected_root_ids):
        errors.append("multiroot_super_root_forbidden")
    if (
        _valid_text_members_tuple(outcome.expected_root_ids, allow_empty=False)
        and _duplicates(outcome.expected_root_ids)
    ):
        errors.append("multiroot_duplicate_root")

    decisions_valid_shape = bool(
        type(outcome.root_decisions) is tuple
        and all(type(item) is RootDecisionEnvelopeV01 for item in outcome.root_decisions)
    )
    if not decisions_valid_shape:
        errors.append("multiroot_outcome_invalid")
        decisions: tuple[RootDecisionEnvelopeV01, ...] = ()
    else:
        decisions = outcome.root_decisions
        for decision in decisions:
            errors.extend(_root_decision_errors(decision, check_id=True))

    root_ids = tuple(
        item.root_id for item in decisions if _valid_text(item.root_id)
    )
    decision_ids = tuple(
        item.root_decision_id
        for item in decisions
        if _valid_text(item.root_decision_id)
    )
    if _duplicates(root_ids):
        errors.append("multiroot_duplicate_root")
    if _duplicates(decision_ids):
        errors.append("multiroot_duplicate_decision")
    if expected_valid and any(root_id not in outcome.expected_root_ids for root_id in root_ids):
        errors.append("multiroot_unknown_root")
    if any(
        _valid_text(item.transaction_id)
        and item.transaction_id != outcome.transaction_id
        for item in decisions
    ):
        errors.append("multiroot_transaction_mismatch")

    if expected_valid and not _duplicates(root_ids) and all(
        root_id in outcome.expected_root_ids for root_id in root_ids
    ):
        expected_observed = tuple(
            root_id for root_id in outcome.expected_root_ids if root_id in root_ids
        )
        if root_ids != expected_observed:
            errors.append("multiroot_outcome_invalid")

    refs_valid_shape = bool(
        type(outcome.cross_root_evidence_refs) is tuple
        and all(
            type(item) is CrossRootEvidenceRefV01
            for item in outcome.cross_root_evidence_refs
        )
    )
    if not refs_valid_shape:
        errors.append("multiroot_outcome_invalid")
        refs: tuple[CrossRootEvidenceRefV01, ...] = ()
    else:
        refs = outcome.cross_root_evidence_refs
        for ref in refs:
            errors.extend(_cross_root_errors(ref, check_id=True))
        ref_ids = tuple(ref.ref_id for ref in refs if _valid_text(ref.ref_id))
        if _duplicates(ref_ids):
            errors.append("multiroot_cross_root_evidence_invalid")
        relations = tuple(
            (ref.source_root_id, ref.target_root_id, ref.evidence_artifact_id)
            for ref in refs
            if _valid_text(ref.source_root_id)
            and _valid_text(ref.target_root_id)
            and _valid_text(ref.evidence_artifact_id)
        )
        if _duplicates(relations):
            errors.append("multiroot_cross_root_evidence_invalid")
        if any(
            _valid_text(ref.transaction_id)
            and ref.transaction_id != outcome.transaction_id
            for ref in refs
        ):
            errors.append("multiroot_transaction_mismatch")
        if expected_valid:
            if any(ref.source_root_id not in outcome.expected_root_ids for ref in refs):
                errors.append("multiroot_cross_root_unknown_source")
            if any(ref.target_root_id not in outcome.expected_root_ids for ref in refs):
                errors.append("multiroot_cross_root_unknown_target")
            if all(
                ref.source_root_id in outcome.expected_root_ids
                and ref.target_root_id in outcome.expected_root_ids
                and _valid_text(ref.evidence_artifact_id)
                and _valid_text(ref.ref_id)
                for ref in refs
            ):
                position = {
                    root_id: index
                    for index, root_id in enumerate(outcome.expected_root_ids)
                }
                ordered = tuple(
                    sorted(
                        refs,
                        key=lambda ref: (
                            position[ref.source_root_id],
                            position[ref.target_root_id],
                            ref.evidence_artifact_id,
                            ref.ref_id,
                        ),
                    )
                )
                if refs != ordered:
                    errors.append("multiroot_outcome_invalid")

        refs_by_id = {
            ref.ref_id: ref for ref in refs if _valid_text(ref.ref_id)
        }
        ref_positions = {
            ref.ref_id: index
            for index, ref in enumerate(refs)
            if _valid_text(ref.ref_id)
        }
        for decision in decisions:
            if not _valid_text_members_tuple(
                decision.cross_root_input_refs,
                allow_empty=True,
            ):
                if decision.cross_root_input_refs:
                    errors.append("multiroot_cross_root_evidence_invalid")
                continue
            consumed_positions: list[int] = []
            for ref_id in decision.cross_root_input_refs:
                matched = refs_by_id.get(ref_id)
                if matched is None:
                    errors.append("multiroot_cross_root_evidence_invalid")
                    continue
                consumed_positions.append(ref_positions[ref_id])
                if (
                    matched.target_root_id != decision.root_id
                    or matched.transaction_id != outcome.transaction_id
                    or matched.transaction_id != decision.transaction_id
                    or _cross_root_errors(matched, check_id=True)
                ):
                    errors.append("multiroot_cross_root_evidence_invalid")
            if consumed_positions != sorted(consumed_positions):
                errors.append("multiroot_outcome_invalid")

    derived_available = bool(
        expected_valid
        and decisions_valid_shape
        and not _duplicates(root_ids)
        and all(root_id in outcome.expected_root_ids for root_id in root_ids)
        and not any(
            _super_root_id(root_id)
            for root_id in (*outcome.expected_root_ids, *root_ids)
        )
    )
    if derived_available:
        derived = _derive_outcome_fields(
            expected_root_ids=outcome.expected_root_ids,
            root_decisions=decisions,
        )
        if outcome.observed_root_ids != derived[0]:
            errors.append("multiroot_outcome_invalid")
        if outcome.accepted_root_ids != derived[1]:
            errors.append("multiroot_outcome_invalid")
        if outcome.non_accepted_root_ids != derived[2]:
            errors.append("multiroot_outcome_invalid")
        if derived[3] == STATUS_INCOMPLETE and outcome.outcome_status != STATUS_INCOMPLETE:
            errors.append("multiroot_missing_root")
        if outcome.outcome_status == STATUS_PASS and derived[3] != STATUS_PASS:
            errors.append("multiroot_silent_global_pass_forbidden")
        if outcome.outcome_status != derived[3]:
            errors.append("multiroot_status_mismatch")
        if outcome.mixed_outcomes_visible is not derived[4]:
            errors.append("multiroot_status_mismatch")
    else:
        if not _valid_text_tuple(outcome.observed_root_ids, allow_empty=True):
            errors.append("multiroot_outcome_invalid")
        if not _valid_text_tuple(outcome.accepted_root_ids, allow_empty=True):
            errors.append("multiroot_outcome_invalid")
        if not _valid_text_tuple(outcome.non_accepted_root_ids, allow_empty=True):
            errors.append("multiroot_outcome_invalid")
        if type(outcome.mixed_outcomes_visible) is not bool:
            errors.append("multiroot_status_mismatch")

    if outcome.outcome_status not in {STATUS_PASS, STATUS_MIXED, STATUS_INCOMPLETE}:
        errors.append("multiroot_status_mismatch")
    if outcome.super_root_created is not False:
        errors.append("multiroot_super_root_forbidden")
    if type(outcome.authority_transfer_count) is not int or outcome.authority_transfer_count != 0:
        errors.append("multiroot_authority_transfer_forbidden")
    if type(outcome.permission_creation_count) is not int or outcome.permission_creation_count != 0:
        errors.append("multiroot_permission_transfer_forbidden")
    if type(outcome.real_world_effects_count) is not int or outcome.real_world_effects_count != 0:
        errors.append("multiroot_real_effect_forbidden")

    if check_id:
        if not _valid_sha256(outcome.outcome_id):
            errors.append("multiroot_identity_mismatch")
        else:
            try:
                material = _outcome_plain(outcome)
                material.pop("outcome_id")
                if outcome.outcome_id != _hash(_OUTCOME_DOMAIN, material):
                    errors.append("multiroot_identity_mismatch")
            except Exception:
                errors.append("multiroot_identity_mismatch")
    return _dedupe(errors)


def _derive_outcome_fields(
    *,
    expected_root_ids: object,
    root_decisions: object,
) -> tuple[
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
    str,
    bool,
]:
    if not _valid_text_tuple(expected_root_ids, allow_empty=False):
        raise ValueError("multiroot_expected_roots_invalid")
    if any(_super_root_id(root_id) for root_id in expected_root_ids):
        raise ValueError("multiroot_super_root_forbidden")
    if type(root_decisions) is not tuple or any(
        type(item) is not RootDecisionEnvelopeV01 for item in root_decisions
    ):
        raise ValueError("multiroot_outcome_invalid")
    root_ids = tuple(item.root_id for item in root_decisions)
    if _duplicates(root_ids):
        raise ValueError("multiroot_duplicate_root")
    if any(root_id not in expected_root_ids for root_id in root_ids):
        raise ValueError("multiroot_unknown_root")
    expected_observed = tuple(
        root_id for root_id in expected_root_ids if root_id in root_ids
    )
    if root_ids != expected_observed:
        raise ValueError("multiroot_outcome_invalid")
    accepted = tuple(
        item.root_id for item in root_decisions if item.outcome_class == "ACCEPTED"
    )
    non_accepted = tuple(
        item.root_id for item in root_decisions if item.outcome_class != "ACCEPTED"
    )
    missing = tuple(root_id for root_id in expected_root_ids if root_id not in root_ids)
    status = (
        STATUS_INCOMPLETE
        if missing
        else STATUS_PASS
        if not non_accepted
        else STATUS_MIXED
    )
    return root_ids, accepted, non_accepted, status, bool(non_accepted)


def _validation_geometry(
    outcome: object,
) -> tuple[
    str,
    tuple[str, ...],
    tuple[str, ...],
    int,
    int,
    int,
    int,
    tuple[str, ...],
    tuple[str, ...],
    tuple[str, ...],
    bool,
    int,
    int,
    bool,
]:
    if type(outcome) is not TransactionOutcomeEnvelopeV01:
        return "", (), (), 0, 0, 0, 0, (), (), (), False, 0, 0, False
    transaction_id = outcome.transaction_id if type(outcome.transaction_id) is str else ""
    expected = (
        outcome.expected_root_ids
        if _valid_text_members_tuple(outcome.expected_root_ids, allow_empty=True)
        else ()
    )
    decisions = (
        outcome.root_decisions
        if type(outcome.root_decisions) is tuple
        else ()
    )
    exact_decisions = tuple(
        item for item in decisions if type(item) is RootDecisionEnvelopeV01
    )
    observed = tuple(
        item.root_id for item in exact_decisions if _valid_text(item.root_id)
    )
    accepted_count = sum(
        item.outcome_class == "ACCEPTED" for item in exact_decisions
    )
    non_accepted_count = len(exact_decisions) - accepted_count
    unknown = _unique_in_order(
        root_id for root_id in observed if root_id not in expected
    )
    duplicate = _unique_in_order(
        (*_duplicate_values(expected), *_duplicate_values(observed))
    )
    observed_set = set(observed)
    missing = tuple(
        root_id
        for root_id in _unique_in_order(expected)
        if root_id not in observed_set
    )
    refs = (
        outcome.cross_root_evidence_refs
        if type(outcome.cross_root_evidence_refs) is tuple
        else ()
    )
    exact_refs = tuple(item for item in refs if type(item) is CrossRootEvidenceRefV01)
    authority_count = sum(item.authority_transferred is True for item in exact_refs)
    permission_count = sum(item.permission_created is True for item in exact_refs)
    super_root = bool(
        outcome.super_root_created is True
        or any(_super_root_id(root_id) for root_id in expected + observed)
    )
    return (
        transaction_id,
        expected,
        observed,
        len(decisions),
        len(refs),
        accepted_count,
        non_accepted_count,
        unknown,
        duplicate,
        missing,
        bool(non_accepted_count),
        authority_count,
        permission_count,
        super_root,
    )


def _validation_result_errors(
    result: object,
) -> tuple[str, ...]:
    if type(result) is not MultiRootValidationResultV01:
        return ("multiroot_outcome_invalid",)
    errors: list[str] = []
    if type(result.transaction_id) is not str or _contains_surrogate(result.transaction_id):
        errors.append("multiroot_outcome_invalid")
    expected_valid = _valid_text_members_tuple(
        result.expected_root_ids,
        allow_empty=True,
    )
    observed_valid = _valid_text_members_tuple(
        result.observed_root_ids,
        allow_empty=True,
    )
    if not expected_valid or not observed_valid:
        errors.append("multiroot_outcome_invalid")
    for value in (
        result.unknown_root_ids,
        result.duplicate_root_ids,
        result.missing_root_ids,
    ):
        if not _valid_text_tuple(value, allow_empty=True):
            errors.append("multiroot_outcome_invalid")
    for value in (
        result.root_decision_count,
        result.cross_root_evidence_count,
        result.accepted_root_count,
        result.non_accepted_root_count,
        result.authority_transfer_count,
        result.permission_creation_count,
        result.real_world_effects_count,
    ):
        if type(value) is not int or value < 0:
            errors.append("multiroot_outcome_invalid")
            break
    if result.real_world_effects_count != 0:
        errors.append("multiroot_real_effect_forbidden")
    if type(result.mixed_outcomes_visible) is not bool or type(result.super_root_created) is not bool:
        errors.append("multiroot_outcome_invalid")
    errors_valid = bool(
        type(result.errors) is tuple
        and len(result.errors) == len(set(result.errors))
        and all(
            type(item) is str and item in _ERROR_REASONS
            for item in result.errors
        )
    )
    if not errors_valid:
        errors.append("multiroot_outcome_invalid")

    expected_unique: tuple[str, ...] = ()
    computed_unknown: tuple[str, ...] = ()
    computed_duplicate: tuple[str, ...] = ()
    computed_missing: tuple[str, ...] = ()
    geometry_valid = bool(
        expected_valid
        and observed_valid
        and _valid_text_tuple(result.unknown_root_ids, allow_empty=True)
        and _valid_text_tuple(result.duplicate_root_ids, allow_empty=True)
        and _valid_text_tuple(result.missing_root_ids, allow_empty=True)
    )
    if geometry_valid:
        expected_unique = _unique_in_order(result.expected_root_ids)
        expected_set = set(expected_unique)
        observed_set = set(result.observed_root_ids)
        computed_unknown = _unique_in_order(
            root_id
            for root_id in result.observed_root_ids
            if root_id not in expected_set
        )
        computed_duplicate = _unique_in_order(
            (
                *_duplicate_values(result.expected_root_ids),
                *_duplicate_values(result.observed_root_ids),
            )
        )
        computed_missing = tuple(
            root_id for root_id in expected_unique if root_id not in observed_set
        )
        if result.unknown_root_ids != computed_unknown:
            errors.append("multiroot_outcome_invalid")
        if result.duplicate_root_ids != computed_duplicate:
            errors.append("multiroot_outcome_invalid")
        if result.missing_root_ids != computed_missing:
            errors.append("multiroot_outcome_invalid")

    reserved_root_identity_visible = bool(
        expected_valid
        and observed_valid
        and any(
            _super_root_id(root_id)
            for root_id in (
                *result.expected_root_ids,
                *result.observed_root_ids,
            )
        )
    )

    counts_valid = all(
        type(value) is int and value >= 0
        for value in (
            result.root_decision_count,
            result.cross_root_evidence_count,
            result.accepted_root_count,
            result.non_accepted_root_count,
            result.authority_transfer_count,
            result.permission_creation_count,
            result.real_world_effects_count,
        )
    )
    booleans_valid = bool(
        type(result.mixed_outcomes_visible) is bool
        and type(result.super_root_created) is bool
    )
    if counts_valid and (
        result.authority_transfer_count > result.cross_root_evidence_count
        or result.permission_creation_count > result.cross_root_evidence_count
    ):
        errors.append("multiroot_outcome_invalid")
    if (
        reserved_root_identity_visible
        and result.final_status != STATUS_FAIL_CLOSED
    ):
        errors.append("multiroot_super_root_forbidden")

    if result.final_status not in MULTIROOT_STATUSES:
        errors.append("multiroot_status_mismatch")
    elif result.final_status == STATUS_FAIL_CLOSED:
        if not errors_valid or not result.errors:
            errors.append("multiroot_status_mismatch")
    elif not errors_valid or result.errors:
        errors.append("multiroot_status_mismatch")

    if geometry_valid and counts_valid and booleans_valid:
        expected_is_unique = result.expected_root_ids == expected_unique
        observed_is_unique = not _duplicates(result.observed_root_ids)
        complete_geometry = bool(
            expected_is_unique
            and observed_is_unique
            and result.expected_root_ids
            and result.observed_root_ids == result.expected_root_ids
            and not computed_unknown
            and not computed_duplicate
            and not computed_missing
        )
        classified_count = (
            result.accepted_root_count + result.non_accepted_root_count
        )
        zero_boundaries = bool(
            result.authority_transfer_count == 0
            and result.permission_creation_count == 0
            and result.super_root_created is False
            and result.real_world_effects_count == 0
            and not reserved_root_identity_visible
        )
        if result.mixed_outcomes_visible is not bool(
            result.non_accepted_root_count
        ):
            errors.append("multiroot_status_mismatch")

        if result.final_status == STATUS_PASS:
            if not (
                _valid_text(result.transaction_id)
                and complete_geometry
                and result.root_decision_count == len(result.observed_root_ids)
                and result.accepted_root_count == result.root_decision_count
                and result.non_accepted_root_count == 0
                and result.mixed_outcomes_visible is False
                and zero_boundaries
            ):
                errors.append("multiroot_silent_global_pass_forbidden")
        elif result.final_status == STATUS_MIXED:
            if not (
                _valid_text(result.transaction_id)
                and complete_geometry
                and result.root_decision_count == len(result.observed_root_ids)
                and result.root_decision_count == classified_count
                and result.non_accepted_root_count > 0
                and result.mixed_outcomes_visible is True
                and zero_boundaries
            ):
                errors.append("multiroot_status_mismatch")
        elif result.final_status == STATUS_INCOMPLETE:
            expected_observed = tuple(
                root_id
                for root_id in result.expected_root_ids
                if root_id in set(result.observed_root_ids)
            )
            if not (
                _valid_text(result.transaction_id)
                and expected_is_unique
                and observed_is_unique
                and result.expected_root_ids
                and result.observed_root_ids == expected_observed
                and not computed_unknown
                and not computed_duplicate
                and bool(computed_missing)
                and result.root_decision_count == len(result.observed_root_ids)
                and result.root_decision_count == classified_count
                and zero_boundaries
            ):
                errors.append("multiroot_status_mismatch")
        elif result.final_status == STATUS_FAIL_CLOSED:
            if (
                len(result.observed_root_ids) > classified_count
                or classified_count > result.root_decision_count
            ):
                errors.append("multiroot_outcome_invalid")
            if reserved_root_identity_visible and not (
                result.super_root_created is True
                and "multiroot_super_root_forbidden" in result.errors
            ):
                errors.append("multiroot_super_root_forbidden")
            if result.authority_transfer_count and (
                "multiroot_authority_transfer_forbidden" not in result.errors
            ):
                errors.append("multiroot_outcome_invalid")
            if result.permission_creation_count and (
                "multiroot_permission_transfer_forbidden" not in result.errors
            ):
                errors.append("multiroot_outcome_invalid")
            if result.super_root_created and (
                "multiroot_super_root_forbidden" not in result.errors
            ):
                errors.append("multiroot_outcome_invalid")
            if result.errors == ("multiroot_unexpected_exception",) and any(
                (
                    result.transaction_id,
                    result.expected_root_ids,
                    result.observed_root_ids,
                    result.root_decision_count,
                    result.cross_root_evidence_count,
                    result.accepted_root_count,
                    result.non_accepted_root_count,
                    result.unknown_root_ids,
                    result.duplicate_root_ids,
                    result.missing_root_ids,
                    result.mixed_outcomes_visible,
                    result.authority_transfer_count,
                    result.permission_creation_count,
                    result.super_root_created,
                    result.real_world_effects_count,
                )
            ):
                errors.append("multiroot_outcome_invalid")
    elif result.final_status in {
        STATUS_PASS,
        STATUS_MIXED,
        STATUS_INCOMPLETE,
    }:
        errors.append("multiroot_status_mismatch")

    if not _valid_sha256(result.validation_id):
        errors.append("multiroot_identity_mismatch")
    elif not errors:
        material = _validation_result_plain(result)
        material.pop("validation_id")
        if result.validation_id != _hash(_VALIDATION_DOMAIN, material):
            errors.append("multiroot_identity_mismatch")
    return _dedupe(errors)


def _root_decision_plain(envelope: RootDecisionEnvelopeV01) -> dict[str, object]:
    return {
        "envelope_id": envelope.envelope_id,
        "transaction_id": envelope.transaction_id,
        "root_id": envelope.root_id,
        "root_decision_id": envelope.root_decision_id,
        "source_decision_ref": envelope.source_decision_ref,
        "outcome_class": envelope.outcome_class,
        "reason_code": envelope.reason_code,
        "selected_subject_id": envelope.selected_subject_id,
        "root_commit_created": envelope.root_commit_created,
        "authority_class": envelope.authority_class,
        "evidence_refs": list(envelope.evidence_refs),
        "cross_root_input_refs": list(envelope.cross_root_input_refs),
        "real_world_effects_count": envelope.real_world_effects_count,
    }


def _cross_root_plain(ref: CrossRootEvidenceRefV01) -> dict[str, object]:
    return {
        "ref_id": ref.ref_id,
        "transaction_id": ref.transaction_id,
        "source_root_id": ref.source_root_id,
        "target_root_id": ref.target_root_id,
        "evidence_artifact_id": ref.evidence_artifact_id,
        "evidence_artifact_hash": ref.evidence_artifact_hash,
        "evidence_class": ref.evidence_class,
        "receipt_validated": ref.receipt_validated,
        "authority_transferred": ref.authority_transferred,
        "permission_created": ref.permission_created,
        "effect_authorized": ref.effect_authorized,
        "trace_refs": list(ref.trace_refs),
        "real_world_effects_count": ref.real_world_effects_count,
    }


def _outcome_plain(outcome: TransactionOutcomeEnvelopeV01) -> dict[str, object]:
    return {
        "outcome_id": outcome.outcome_id,
        "transaction_id": outcome.transaction_id,
        "expected_root_ids": list(outcome.expected_root_ids),
        "root_decisions": [
            _root_decision_plain(item) for item in outcome.root_decisions
        ],
        "cross_root_evidence_refs": [
            _cross_root_plain(item) for item in outcome.cross_root_evidence_refs
        ],
        "observed_root_ids": list(outcome.observed_root_ids),
        "accepted_root_ids": list(outcome.accepted_root_ids),
        "non_accepted_root_ids": list(outcome.non_accepted_root_ids),
        "outcome_status": outcome.outcome_status,
        "mixed_outcomes_visible": outcome.mixed_outcomes_visible,
        "super_root_created": outcome.super_root_created,
        "authority_transfer_count": outcome.authority_transfer_count,
        "permission_creation_count": outcome.permission_creation_count,
        "real_world_effects_count": outcome.real_world_effects_count,
    }


def _validation_result_plain(
    result: MultiRootValidationResultV01,
) -> dict[str, object]:
    return {
        "validation_id": result.validation_id,
        "transaction_id": result.transaction_id,
        "expected_root_ids": list(result.expected_root_ids),
        "observed_root_ids": list(result.observed_root_ids),
        "root_decision_count": result.root_decision_count,
        "cross_root_evidence_count": result.cross_root_evidence_count,
        "accepted_root_count": result.accepted_root_count,
        "non_accepted_root_count": result.non_accepted_root_count,
        "unknown_root_ids": list(result.unknown_root_ids),
        "duplicate_root_ids": list(result.duplicate_root_ids),
        "missing_root_ids": list(result.missing_root_ids),
        "mixed_outcomes_visible": result.mixed_outcomes_visible,
        "authority_transfer_count": result.authority_transfer_count,
        "permission_creation_count": result.permission_creation_count,
        "super_root_created": result.super_root_created,
        "final_status": result.final_status,
        "errors": list(result.errors),
        "real_world_effects_count": result.real_world_effects_count,
    }


def _hash(domain: str, value: object) -> str:
    return _domain_separated_sha256_hex_v01(
        domain=domain,
        payload=_canonical_json_bytes_v01(value),
    )


def _contains_surrogate(value: str) -> bool:
    return any(0xD800 <= ord(character) <= 0xDFFF for character in value)


def _valid_text(value: object) -> bool:
    return type(value) is str and bool(value) and not _contains_surrogate(value)


def _valid_text_tuple(value: object, *, allow_empty: bool) -> bool:
    return bool(
        type(value) is tuple
        and (allow_empty or value)
        and all(_valid_text(item) for item in value)
        and len(value) == len(set(value))
    )


def _valid_text_members_tuple(value: object, *, allow_empty: bool) -> bool:
    return bool(
        type(value) is tuple
        and (allow_empty or value)
        and all(_valid_text(item) for item in value)
    )


def _valid_sha256(value: object) -> bool:
    return bool(
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _super_root_id(value: str) -> bool:
    normalized = value.lower()
    return "superroot" in normalized or "super_root" in normalized


def _duplicates(values: tuple[object, ...]) -> bool:
    return len(values) != len(set(values))


def _duplicate_values(values: tuple[str, ...]) -> tuple[str, ...]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for value in values:
        if value in seen and value not in duplicates:
            duplicates.append(value)
        seen.add(value)
    return tuple(duplicates)


def _unique_in_order(values: object) -> tuple[str, ...]:
    output: list[str] = []
    for value in values:
        if value not in output:
            output.append(value)
    return tuple(output)


def _stable_reason(error: ValueError, allowed: tuple[str, ...]) -> str | None:
    if (
        type(error) is ValueError
        and len(error.args) == 1
        and type(error.args[0]) is str
        and error.args[0] in allowed
    ):
        return error.args[0]
    return None


def _dedupe(values: object) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))
