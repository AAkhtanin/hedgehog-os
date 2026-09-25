"""Pure in-memory deterministic domain-neutral Root decision kernel for G1-C1.

This Root-only boundary consumes validated advisory inputs and creates one
RootDecisionResultV01 only. It calls no LLM, provider, network, filesystem,
clock, or random source; creates no permission, FinalOutput, or receipt; writes
no DRS; requests and executes no effect; and trusts no score over a hard
predicate. This is not production policy certification.
"""

from __future__ import annotations

from collections.abc import Mapping as _Mapping
from dataclasses import dataclass as _dataclass

from hedgehog.kernel.integrity_replay_v01 import (
    canonical_json_bytes_v01 as _canonical_json_bytes_v01,
    domain_separated_sha256_hex_v01 as _domain_separated_sha256_hex_v01,
)
from hedgehog.kernel.semantic_work_v01 import (
    ROOT_REVIEW_STATE as _ROOT_REVIEW_STATE,
    SYNTHESIS_AUTHORITY_ADVISORY as _SYNTHESIS_AUTHORITY_ADVISORY,
    RootReviewPacketV01 as _RootReviewPacketV01,
    semantic_work_to_plain_dict_v01 as _semantic_work_to_plain_dict_v01,
)
from hedgehog.kernel.transition_registry_v01 import (
    DECISION_RETURN_TO_ROOT as _TRANSITION_RETURN_TO_ROOT,
    TransitionDecisionV01 as _TransitionDecisionV01,
    TransitionRegistryV01 as _TransitionRegistryV01,
    build_default_transition_registry_v01 as _build_default_transition_registry_v01,
    lookup_transition_v01 as _lookup_transition_v01,
    transition_decision_to_plain_dict_v01 as _transition_decision_to_plain_dict_v01,
    transition_registry_to_plain_dict_v01 as _transition_registry_to_plain_dict_v01,
    validate_transition_decision_v01 as _validate_transition_decision_v01,
    validate_transition_registry_v01 as _validate_transition_registry_v01,
)


MODULE_ID = "kernel_root_decision_v01"
SLICE_ID = "domain_neutral_reference_kernel_gate1_g1c1"
ROOT_DECISION_VERSION = "v0.1"

STATUS_PASS = "PASS"
STATUS_BLOCKED_FAIL_CLOSED = "BLOCKED_FAIL_CLOSED"

ROOT_DECISION_ACCEPT = "ACCEPT"
ROOT_DECISION_REJECT = "REJECT"
ROOT_DECISION_DEFER = "DEFER"
ROOT_DECISION_NEEDS_USER = "NEEDS_USER"
ROOT_DECISION_NEEDS_MORE_EVIDENCE = "NEEDS_MORE_EVIDENCE"
ROOT_DECISION_NO_UPDATE = "NO_UPDATE"
ROOT_DECISION_BLOCKED_FAIL_CLOSED = "BLOCKED_FAIL_CLOSED"
ROOT_DECISIONS = (
    ROOT_DECISION_BLOCKED_FAIL_CLOSED,
    ROOT_DECISION_NEEDS_USER,
    ROOT_DECISION_NEEDS_MORE_EVIDENCE,
    ROOT_DECISION_DEFER,
    ROOT_DECISION_REJECT,
    ROOT_DECISION_NO_UPDATE,
    ROOT_DECISION_ACCEPT,
)

POST_VV_HARD_FAILURE_CODES = (
    "identity_validation_failed",
    "scope_validation_failed",
    "policy_validation_failed",
    "permission_scope_validation_failed",
    "temporal_validation_failed",
    "candidate_validation_failed",
)

_PRECEDENCE_ORDER = (
    "HARD_FAILURE",
    "NEEDS_USER",
    "NEEDS_MORE_EVIDENCE",
    "MATERIAL_CONFLICT",
    "NO_VALID_CANDIDATE",
    "POLICY_REJECT",
    "ACCEPT",
)
_HARD_FAILURE_ORDER = (
    "hard_identity_violation",
    "hard_scope_violation",
    "hard_policy_violation",
    "hard_permission_scope_violation",
    "hard_temporal_violation",
    "post_vv_hard_failure",
    "gt_authority_escalation",
    "transition_blocked",
)
_RESULT_REASON_GRAMMAR = (
    (ROOT_DECISION_BLOCKED_FAIL_CLOSED, _HARD_FAILURE_ORDER),
    (ROOT_DECISION_NEEDS_USER, ("user_permission_missing",)),
    (ROOT_DECISION_NEEDS_MORE_EVIDENCE, ("required_evidence_missing",)),
    (ROOT_DECISION_DEFER, ("material_conflict_deferred",)),
    (
        ROOT_DECISION_REJECT,
        (
            "material_conflict_rejected",
            "no_valid_candidate_rejected",
            "policy_rejected_candidate",
        ),
    ),
    (ROOT_DECISION_NO_UPDATE, ("no_valid_candidate",)),
    (ROOT_DECISION_ACCEPT, ("validated_candidate_accepted",)),
)
_CONFLICT_POLICIES = ("DEFER", "REJECT")
_NO_CANDIDATE_POLICIES = ("NO_UPDATE", "REJECT")
_INPUT_DOMAIN = "hedgehog.kernel.root_decision_input.v01"
_KERNEL_DOMAIN = "hedgehog.kernel.root_decision_kernel.v01"
_RESULT_DOMAIN = "hedgehog.kernel.root_decision_result.v01"


@_dataclass(frozen=True)
class _FrozenJSONObject:
    items: tuple[tuple[str, object], ...]


@_dataclass(frozen=True)
class RootDecisionInputV01:
    decision_input_id: str
    transaction_id: str
    target_root_id: str
    root_review_packet: _RootReviewPacketV01
    post_vv_bundle: object
    gt_advisory: object
    policy_state: object
    permission_state: object
    temporal_state: object
    conflict_state: object
    prior_root_state: object


@_dataclass(frozen=True)
class RootDecisionResultV01:
    decision_id: str
    decision_input_id: str
    transaction_id: str
    target_root_id: str
    decision: str
    reason_code: str
    selected_candidate_id: str | None
    transition_decision: _TransitionDecisionV01
    hard_failure_reasons: tuple[str, ...]
    missing_evidence_refs: tuple[str, ...]
    conflict_set_ids: tuple[str, ...]
    prior_decision_id: str | None
    root_commit_created: bool
    permission_created: bool
    final_output_created: bool
    effect_requested: bool


@_dataclass(frozen=True)
class RootDecisionKernelV01:
    kernel_id: str
    kernel_version: str
    transition_registry: _TransitionRegistryV01
    precedence_order: tuple[str, ...]
    llm_dependency_allowed: bool
    effect_access: str


def build_root_decision_kernel_v01() -> RootDecisionKernelV01:
    registry = _build_default_transition_registry_v01()
    if _validate_transition_registry_v01(registry):
        raise ValueError("root_decision_kernel_invalid") from None
    material = {
        "kernel_version": ROOT_DECISION_VERSION,
        "registry_id": registry.registry_id,
        "precedence_order": list(_PRECEDENCE_ORDER),
        "llm_dependency_allowed": False,
        "effect_access": "NONE",
    }
    return RootDecisionKernelV01(
        kernel_id=_hash(_KERNEL_DOMAIN, material),
        kernel_version=ROOT_DECISION_VERSION,
        transition_registry=registry,
        precedence_order=_PRECEDENCE_ORDER,
        llm_dependency_allowed=False,
        effect_access="NONE",
    )


def validate_root_decision_kernel_v01(kernel: object) -> tuple[str, ...]:
    try:
        return _kernel_errors(kernel)
    except Exception:
        return ("root_decision_unexpected_exception",)


def build_root_decision_input_v01(
    *,
    transaction_id: str,
    target_root_id: str,
    root_review_packet: _RootReviewPacketV01,
    post_vv_bundle: object,
    gt_advisory: object,
    policy_state: object,
    permission_state: object,
    temporal_state: object,
    conflict_state: object,
    prior_root_state: object,
) -> RootDecisionInputV01:
    try:
        frozen_states = tuple(
            _freeze_json_object(value)
            for value in (
                post_vv_bundle,
                gt_advisory,
                policy_state,
                permission_state,
                temporal_state,
                conflict_state,
                prior_root_state,
            )
        )
        provisional = RootDecisionInputV01(
            decision_input_id="0" * 64,
            transaction_id=transaction_id,
            target_root_id=target_root_id,
            root_review_packet=root_review_packet,
            post_vv_bundle=frozen_states[0],
            gt_advisory=frozen_states[1],
            policy_state=frozen_states[2],
            permission_state=frozen_states[3],
            temporal_state=frozen_states[4],
            conflict_state=frozen_states[5],
            prior_root_state=frozen_states[6],
        )
        errors = _input_errors(provisional, check_id=False)
        if errors:
            raise ValueError(errors[0])
        material = _input_plain(provisional)
        material.pop("decision_input_id")
        return RootDecisionInputV01(
            decision_input_id=_hash(_INPUT_DOMAIN, material),
            transaction_id=transaction_id,
            target_root_id=target_root_id,
            root_review_packet=root_review_packet,
            post_vv_bundle=frozen_states[0],
            gt_advisory=frozen_states[1],
            policy_state=frozen_states[2],
            permission_state=frozen_states[3],
            temporal_state=frozen_states[4],
            conflict_state=frozen_states[5],
            prior_root_state=frozen_states[6],
        )
    except ValueError as exc:
        reason = _allowed_reason(exc, _INPUT_REASONS)
        raise ValueError(reason or "root_decision_input_invalid") from None
    except Exception:
        raise ValueError("root_decision_input_invalid") from None


def validate_root_decision_input_v01(
    *,
    kernel: object,
    decision_input: object,
) -> tuple[str, ...]:
    try:
        errors = list(_kernel_errors(kernel))
        errors.extend(_input_errors(decision_input, check_id=True))
        return _dedupe(errors)
    except Exception:
        return ("root_decision_unexpected_exception",)


def decide_root_v01(
    *,
    kernel: object,
    decision_input: object,
) -> RootDecisionResultV01:
    try:
        errors = validate_root_decision_input_v01(
            kernel=kernel,
            decision_input=decision_input,
        )
        if errors:
            raise ValueError(errors[0])
        assert type(kernel) is RootDecisionKernelV01
        assert type(decision_input) is RootDecisionInputV01
        return _decide_validated(kernel, decision_input)
    except ValueError as exc:
        reason = _allowed_reason(exc, _DECIDE_REASONS)
        raise ValueError(reason or "root_decision_unexpected_exception") from None
    except Exception:
        raise ValueError("root_decision_unexpected_exception") from None


def validate_root_decision_result_v01(
    *,
    kernel: object,
    decision_input: object,
    result: object,
) -> tuple[str, ...]:
    try:
        errors: list[str] = list(
            validate_root_decision_input_v01(
                kernel=kernel,
                decision_input=decision_input,
            )
        )
        if errors:
            return _dedupe(errors)
        if type(result) is not RootDecisionResultV01:
            return ("root_decision_result_invalid",)
        if result.permission_created:
            errors.append("root_decision_permission_creation_forbidden")
        if result.final_output_created:
            errors.append("root_decision_final_output_creation_forbidden")
        if result.effect_requested:
            errors.append("root_decision_effect_request_forbidden")
        expected = _decide_validated(kernel, decision_input)
        if expected.hard_failure_reasons and result.decision != ROOT_DECISION_BLOCKED_FAIL_CLOSED:
            errors.append("hard_predicate_override_forbidden")
        structure_valid = _result_structure_valid(result)
        if not structure_valid:
            errors.append("root_decision_result_invalid")
        try:
            if result.decision_id != _result_id(result):
                errors.append("root_decision_id_mismatch")
        except Exception:
            errors.append("root_decision_result_invalid")
        if (
            result.decision != expected.decision
            or result.reason_code != expected.reason_code
            or result.hard_failure_reasons != expected.hard_failure_reasons
        ):
            errors.append("root_decision_precedence_mismatch")
        try:
            projections_match = _canonical_bytes(
                _result_plain(result)
            ) == _canonical_bytes(_result_plain(expected))
        except Exception:
            projections_match = False
        if not projections_match:
            errors.append("root_decision_result_invalid")
        return _dedupe(errors)
    except Exception:
        return ("root_decision_unexpected_exception",)


def root_decision_kernel_to_plain_dict_v01(
    kernel: RootDecisionKernelV01,
) -> dict[str, object]:
    try:
        if _kernel_errors(kernel):
            raise ValueError("root_decision_kernel_invalid")
        result = _kernel_plain(kernel)
        _canonical_json_bytes_v01(result)
        return result
    except Exception:
        raise ValueError("root_decision_kernel_invalid") from None


def root_decision_input_to_plain_dict_v01(
    decision_input: RootDecisionInputV01,
) -> dict[str, object]:
    try:
        if _input_errors(decision_input, check_id=True):
            raise ValueError("root_decision_input_invalid")
        result = _input_plain(decision_input)
        _canonical_json_bytes_v01(result)
        return result
    except Exception:
        raise ValueError("root_decision_input_invalid") from None


def root_decision_result_to_plain_dict_v01(
    result: RootDecisionResultV01,
) -> dict[str, object]:
    try:
        if type(result) is not RootDecisionResultV01 or not _result_structure_valid(result):
            raise ValueError("root_decision_result_invalid")
        registry = _build_default_transition_registry_v01()
        if _validate_transition_decision_v01(
            registry=registry,
            decision=result.transition_decision,
        ):
            raise ValueError("root_decision_result_invalid")
        if result.decision_id != _result_id(result):
            raise ValueError("root_decision_result_invalid")
        projected = _result_plain(result)
        _canonical_json_bytes_v01(projected)
        return projected
    except Exception:
        raise ValueError("root_decision_result_invalid") from None


_INPUT_REASONS = (
    "root_decision_input_invalid",
    "root_review_packet_invalid",
    "root_decision_identity_mismatch",
    "root_decision_post_vv_invalid",
    "root_decision_gt_advisory_invalid",
    "root_decision_policy_state_invalid",
    "root_decision_permission_state_invalid",
    "root_decision_temporal_state_invalid",
    "root_decision_conflict_state_invalid",
    "root_decision_prior_state_invalid",
    "root_decision_candidate_binding_invalid",
    "root_decision_transition_blocked",
)
_DECIDE_REASONS = (
    "root_decision_kernel_invalid",
    *_INPUT_REASONS,
)


def _kernel_errors(kernel: object) -> tuple[str, ...]:
    if type(kernel) is not RootDecisionKernelV01:
        return ("root_decision_kernel_invalid",)
    errors: list[str] = []
    if _validate_transition_registry_v01(kernel.transition_registry):
        errors.append("root_decision_kernel_invalid")
    if (
        not _valid_sha256(kernel.kernel_id)
        or type(kernel.kernel_version) is not str
        or kernel.kernel_version != ROOT_DECISION_VERSION
        or type(kernel.precedence_order) is not tuple
        or kernel.precedence_order != _PRECEDENCE_ORDER
        or kernel.llm_dependency_allowed is not False
        or type(kernel.effect_access) is not str
        or kernel.effect_access != "NONE"
    ):
        errors.append("root_decision_kernel_invalid")
        return _dedupe(errors)
    material = {
        "kernel_version": kernel.kernel_version,
        "registry_id": kernel.transition_registry.registry_id,
        "precedence_order": list(kernel.precedence_order),
        "llm_dependency_allowed": kernel.llm_dependency_allowed,
        "effect_access": kernel.effect_access,
    }
    if kernel.kernel_id != _hash(_KERNEL_DOMAIN, material):
        errors.append("root_decision_kernel_invalid")
    return _dedupe(errors)


def _input_errors(decision_input: object, *, check_id: bool) -> tuple[str, ...]:
    if type(decision_input) is not RootDecisionInputV01:
        return ("root_decision_input_invalid",)
    errors: list[str] = []
    if not _valid_text(decision_input.transaction_id) or not _valid_text(
        decision_input.target_root_id
    ):
        errors.append("root_decision_input_invalid")
    try:
        packet = _semantic_work_to_plain_dict_v01(decision_input.root_review_packet)
    except Exception:
        errors.append("root_review_packet_invalid")
        return _dedupe(errors)
    if (
        packet.get("transaction_id") != decision_input.transaction_id
        or packet.get("target_root_id") != decision_input.target_root_id
    ):
        errors.append("root_decision_identity_mismatch")
    if (
        packet.get("review_state") != _ROOT_REVIEW_STATE
        or packet.get("authority_class") != _SYNTHESIS_AUTHORITY_ADVISORY
        or packet.get("root_decision_created") is not False
        or packet.get("permission_created") is not False
        or packet.get("final_output_created") is not False
        or not _valid_text(packet.get("runtime_topology_ref"))
    ):
        errors.append("root_review_packet_invalid")

    state_checks = (
        (decision_input.post_vv_bundle, _post_vv_valid, "root_decision_post_vv_invalid"),
        (decision_input.policy_state, _policy_valid, "root_decision_policy_state_invalid"),
        (decision_input.permission_state, _permission_valid, "root_decision_permission_state_invalid"),
        (decision_input.temporal_state, _temporal_valid, "root_decision_temporal_state_invalid"),
        (decision_input.conflict_state, lambda value: _conflict_valid(value, decision_input.root_review_packet), "root_decision_conflict_state_invalid"),
        (decision_input.prior_root_state, _prior_valid, "root_decision_prior_state_invalid"),
    )
    for value, validator, reason in state_checks:
        if not _frozen_json_valid(value) or not validator(value):
            errors.append(reason)
    if not _frozen_json_valid(decision_input.gt_advisory):
        errors.append("root_decision_gt_advisory_invalid")
    else:
        gt_error = _gt_error(
            decision_input.gt_advisory,
            decision_input.root_review_packet,
        )
        if gt_error is not None:
            errors.append(gt_error)
    if "root_decision_post_vv_invalid" not in errors:
        post = _thaw_json_value(decision_input.post_vv_bundle)
        required = tuple(post["required_evidence_refs"])
        if any(ref not in required for ref in decision_input.root_review_packet.missing_evidence_refs):
            errors.append("root_decision_post_vv_invalid")
    if check_id:
        if not _valid_sha256(decision_input.decision_input_id):
            errors.append("root_decision_input_invalid")
        elif not errors:
            material = _input_plain(decision_input)
            material.pop("decision_input_id")
            if decision_input.decision_input_id != _hash(_INPUT_DOMAIN, material):
                errors.append("root_decision_identity_mismatch")
    return _dedupe(errors)


def _post_vv_valid(value: object) -> bool:
    plain = _exact_object(value, (
        "bundle_id", "hard_failure_reasons", "post_vv_passed",
        "provided_evidence_refs", "rejected_candidate_ids",
        "required_evidence_refs", "validated_candidate_ids",
    ))
    if plain is None or not _valid_text(plain["bundle_id"]) or type(plain["post_vv_passed"]) is not bool:
        return False
    for key in (
        "validated_candidate_ids", "rejected_candidate_ids",
        "required_evidence_refs", "provided_evidence_refs", "hard_failure_reasons",
    ):
        if not _valid_text_list(plain[key], allow_empty=True):
            return False
    if set(plain["validated_candidate_ids"]) & set(plain["rejected_candidate_ids"]):
        return False
    if any(code not in POST_VV_HARD_FAILURE_CODES for code in plain["hard_failure_reasons"]):
        return False
    return (plain["post_vv_passed"] and not plain["hard_failure_reasons"]) or (
        not plain["post_vv_passed"] and bool(plain["hard_failure_reasons"])
    )


def _gt_error(value: object, packet: _RootReviewPacketV01) -> str | None:
    plain = _exact_object(value, (
        "actor_role", "advisory_id", "advisory_only", "attempted_effect",
        "candidate_ids", "creates_final_output", "requests_effect",
        "score_micros_by_candidate", "selected_candidate_id",
        "source_artifact_type", "source_lifecycle_state", "target_artifact_type",
    ))
    if plain is None or not _valid_text(plain["advisory_id"]):
        return "root_decision_gt_advisory_invalid"
    if not _valid_text_list(plain["candidate_ids"], allow_empty=False):
        return "root_decision_gt_advisory_invalid"
    selected = plain["selected_candidate_id"]
    if selected is not None and not _valid_text(selected):
        return "root_decision_gt_advisory_invalid"
    scores = plain["score_micros_by_candidate"]
    if type(scores) is not dict or any(
        type(score) is not int or not 0 <= score <= 1_000_000
        for score in scores.values()
    ):
        return "root_decision_gt_advisory_invalid"
    transition_fields = (
        plain["source_artifact_type"],
        plain["source_lifecycle_state"],
        plain["actor_role"],
        plain["attempted_effect"],
        plain["target_artifact_type"],
    )
    if not all(_valid_text(item) for item in transition_fields):
        return "root_decision_gt_advisory_invalid"
    if not all(
        type(plain[key]) is bool
        for key in ("advisory_only", "creates_final_output", "requests_effect")
    ):
        return "root_decision_gt_advisory_invalid"
    if (
        plain["advisory_only"] is not True
        or plain["creates_final_output"] is not False
        or plain["requests_effect"] is not False
    ):
        return "root_decision_gt_advisory_invalid"
    claim_ids = tuple(
        claim.claim_id for claim in packet.synthesis_proposal.normalized_claims
    )
    if any(item not in claim_ids for item in plain["candidate_ids"]):
        return "root_decision_candidate_binding_invalid"
    if selected is not None and selected not in plain["candidate_ids"]:
        return "root_decision_candidate_binding_invalid"
    if set(scores) != set(plain["candidate_ids"]):
        return "root_decision_candidate_binding_invalid"
    if transition_fields != (
        "GTAdvisoryReport",
        "VALIDATED",
        "gt",
        "CREATE_ROOT_DECISION",
        "RootDecision",
    ):
        return "root_decision_transition_blocked"
    return None


def _policy_valid(value: object) -> bool:
    plain = _exact_object(value, (
        "allow_accept", "conflict_policy", "hard_policy_passed",
        "identity_passed", "no_candidate_policy", "policy_id", "scope_passed",
    ))
    return bool(
        plain is not None
        and _valid_text(plain["policy_id"])
        and all(type(plain[key]) is bool for key in ("identity_passed", "scope_passed", "hard_policy_passed", "allow_accept"))
        and type(plain["conflict_policy"]) is str
        and plain["conflict_policy"] in _CONFLICT_POLICIES
        and type(plain["no_candidate_policy"]) is str
        and plain["no_candidate_policy"] in _NO_CANDIDATE_POLICIES
    )


def _permission_valid(value: object) -> bool:
    plain = _exact_object(value, (
        "permission_ref", "permission_required", "permission_scope_valid",
        "user_permission_present",
    ))
    if plain is None or not all(type(plain[key]) is bool for key in ("permission_required", "user_permission_present", "permission_scope_valid")):
        return False
    ref = plain["permission_ref"]
    if ref is not None and not _valid_text(ref):
        return False
    return not plain["user_permission_present"] or ref is not None


def _temporal_valid(value: object) -> bool:
    plain = _exact_object(value, (
        "expired", "not_before_satisfied", "temporal_valid", "time_envelope_ref",
    ))
    return bool(
        plain is not None
        and all(type(plain[key]) is bool for key in ("temporal_valid", "expired", "not_before_satisfied"))
        and _valid_text(plain["time_envelope_ref"])
    )


def _conflict_valid(value: object, packet: _RootReviewPacketV01) -> bool:
    plain = _exact_object(value, ("conflict_set_ids", "material_unresolved_conflict"))
    return bool(
        plain is not None
        and type(plain["material_unresolved_conflict"]) is bool
        and _valid_text_list(plain["conflict_set_ids"], allow_empty=True)
        and tuple(plain["conflict_set_ids"]) == packet.conflict_set_ids
    )


def _prior_valid(value: object) -> bool:
    plain = _exact_object(value, (
        "prior_decision", "prior_decision_id", "prior_selected_candidate_id",
    ))
    if plain is None:
        return False
    for key in plain:
        if plain[key] is not None and not _valid_text(plain[key]):
            return False
    return plain["prior_decision"] is None or plain["prior_decision"] in ROOT_DECISIONS


def _decide_validated(
    kernel: RootDecisionKernelV01,
    decision_input: RootDecisionInputV01,
) -> RootDecisionResultV01:
    post = _thaw_json_value(decision_input.post_vv_bundle)
    gt = _thaw_json_value(decision_input.gt_advisory)
    policy = _thaw_json_value(decision_input.policy_state)
    permission = _thaw_json_value(decision_input.permission_state)
    temporal = _thaw_json_value(decision_input.temporal_state)
    conflict = _thaw_json_value(decision_input.conflict_state)
    prior = _thaw_json_value(decision_input.prior_root_state)

    guards = ["artifact_valid"]
    if post["post_vv_passed"]:
        guards.append("post_vv_passed")
    if gt["advisory_only"]:
        guards.append("advisory_only")
    transition = _lookup_transition_v01(
        registry=kernel.transition_registry,
        abi_major_version=1,
        source_artifact_type=gt["source_artifact_type"],
        source_lifecycle_state=gt["source_lifecycle_state"],
        actor_role=gt["actor_role"],
        attempted_effect=gt["attempted_effect"],
        target_artifact_type=gt["target_artifact_type"],
        satisfied_guards=tuple(guards),
        root_commit_present=False,
    )

    hard: list[str] = []
    if not policy["identity_passed"]:
        hard.append("hard_identity_violation")
    if not policy["scope_passed"]:
        hard.append("hard_scope_violation")
    if not policy["hard_policy_passed"]:
        hard.append("hard_policy_violation")
    if not permission["permission_scope_valid"]:
        hard.append("hard_permission_scope_violation")
    if not temporal["temporal_valid"] or temporal["expired"] or not temporal["not_before_satisfied"]:
        hard.append("hard_temporal_violation")
    if not post["post_vv_passed"] or post["hard_failure_reasons"]:
        hard.append("post_vv_hard_failure")
    if not gt["advisory_only"] or gt["creates_final_output"] or gt["requests_effect"]:
        hard.append("gt_authority_escalation")
    if transition.decision != _TRANSITION_RETURN_TO_ROOT or transition.reason_code != "gt_advisory_returns_to_root":
        hard.append("transition_blocked")
    hard_tuple = tuple(reason for reason in _HARD_FAILURE_ORDER if reason in hard)

    missing = tuple(
        ref
        for ref in post["required_evidence_refs"]
        if ref not in post["provided_evidence_refs"]
    )
    selected = gt["selected_candidate_id"]
    valid_candidate = bool(
        selected is not None
        and selected in gt["candidate_ids"]
        and selected in post["validated_candidate_ids"]
        and selected not in post["rejected_candidate_ids"]
        and selected
        in tuple(
            claim.claim_id
            for claim in decision_input.root_review_packet.synthesis_proposal.normalized_claims
        )
    )

    if hard_tuple:
        decision, reason = ROOT_DECISION_BLOCKED_FAIL_CLOSED, hard_tuple[0]
    elif permission["permission_required"] and not permission["user_permission_present"]:
        decision, reason = ROOT_DECISION_NEEDS_USER, "user_permission_missing"
    elif missing:
        decision, reason = ROOT_DECISION_NEEDS_MORE_EVIDENCE, "required_evidence_missing"
    elif conflict["material_unresolved_conflict"]:
        if policy["conflict_policy"] == "DEFER":
            decision, reason = ROOT_DECISION_DEFER, "material_conflict_deferred"
        else:
            decision, reason = ROOT_DECISION_REJECT, "material_conflict_rejected"
    elif not valid_candidate:
        if policy["no_candidate_policy"] == "NO_UPDATE":
            decision, reason = ROOT_DECISION_NO_UPDATE, "no_valid_candidate"
        else:
            decision, reason = ROOT_DECISION_REJECT, "no_valid_candidate_rejected"
    elif not policy["allow_accept"]:
        decision, reason = ROOT_DECISION_REJECT, "policy_rejected_candidate"
    else:
        decision, reason = ROOT_DECISION_ACCEPT, "validated_candidate_accepted"

    fields = {
        "decision_input_id": decision_input.decision_input_id,
        "transaction_id": decision_input.transaction_id,
        "target_root_id": decision_input.target_root_id,
        "decision": decision,
        "reason_code": reason,
        "selected_candidate_id": selected if decision == ROOT_DECISION_ACCEPT else None,
        "transition_decision": _transition_decision_to_plain_dict_v01(transition),
        "hard_failure_reasons": list(hard_tuple),
        "missing_evidence_refs": list(missing),
        "conflict_set_ids": list(decision_input.root_review_packet.conflict_set_ids),
        "prior_decision_id": prior["prior_decision_id"],
        "root_commit_created": True,
        "permission_created": False,
        "final_output_created": False,
        "effect_requested": False,
    }
    return RootDecisionResultV01(
        decision_id=_hash(_RESULT_DOMAIN, fields),
        decision_input_id=decision_input.decision_input_id,
        transaction_id=decision_input.transaction_id,
        target_root_id=decision_input.target_root_id,
        decision=decision,
        reason_code=reason,
        selected_candidate_id=fields["selected_candidate_id"],
        transition_decision=transition,
        hard_failure_reasons=hard_tuple,
        missing_evidence_refs=missing,
        conflict_set_ids=decision_input.root_review_packet.conflict_set_ids,
        prior_decision_id=prior["prior_decision_id"],
        root_commit_created=True,
        permission_created=False,
        final_output_created=False,
        effect_requested=False,
    )


def _result_structure_valid(result: RootDecisionResultV01) -> bool:
    if type(result) is not RootDecisionResultV01:
        return False
    if not all(_valid_text(value) for value in (result.decision_id, result.decision_input_id, result.transaction_id, result.target_root_id, result.reason_code)):
        return False
    if type(result.decision) is not str or result.decision not in ROOT_DECISIONS:
        return False
    legal_reasons = next(
        (
            reasons
            for decision, reasons in _RESULT_REASON_GRAMMAR
            if decision == result.decision
        ),
        (),
    )
    if result.reason_code not in legal_reasons:
        return False
    if result.selected_candidate_id is not None and not _valid_text(result.selected_candidate_id):
        return False
    if result.prior_decision_id is not None and not _valid_text(result.prior_decision_id):
        return False
    if not all(_valid_text_tuple(value, allow_empty=True) for value in (result.hard_failure_reasons, result.missing_evidence_refs, result.conflict_set_ids)):
        return False
    if any(reason not in _HARD_FAILURE_ORDER for reason in result.hard_failure_reasons):
        return False
    if tuple(reason for reason in _HARD_FAILURE_ORDER if reason in result.hard_failure_reasons) != result.hard_failure_reasons:
        return False
    if not all(type(value) is bool for value in (result.root_commit_created, result.permission_created, result.final_output_created, result.effect_requested)):
        return False
    if result.root_commit_created is not True or result.permission_created or result.final_output_created or result.effect_requested:
        return False
    if result.decision == ROOT_DECISION_BLOCKED_FAIL_CLOSED:
        if not result.hard_failure_reasons:
            return False
        if result.reason_code != result.hard_failure_reasons[0]:
            return False
    elif result.hard_failure_reasons:
        return False
    if (result.decision == ROOT_DECISION_ACCEPT) != (result.selected_candidate_id is not None):
        return False
    if (
        result.decision == ROOT_DECISION_NEEDS_MORE_EVIDENCE
        and not result.missing_evidence_refs
    ):
        return False
    registry = _build_default_transition_registry_v01()
    if _validate_transition_decision_v01(
        registry=registry,
        decision=result.transition_decision,
    ):
        return False
    review_ready, post_vv_blocked = _canonical_root_review_transitions_v01(
        registry
    )
    supplied_transition = _canonical_bytes(
        _transition_decision_to_plain_dict_v01(result.transition_decision)
    )
    review_ready_projection = _canonical_bytes(
        _transition_decision_to_plain_dict_v01(review_ready)
    )
    post_vv_blocked_projection = _canonical_bytes(
        _transition_decision_to_plain_dict_v01(post_vv_blocked)
    )
    if supplied_transition == review_ready_projection:
        if (
            "post_vv_hard_failure" in result.hard_failure_reasons
            or "transition_blocked" in result.hard_failure_reasons
        ):
            return False
    elif supplied_transition == post_vv_blocked_projection:
        if (
            result.decision != ROOT_DECISION_BLOCKED_FAIL_CLOSED
            or "post_vv_hard_failure" not in result.hard_failure_reasons
            or "transition_blocked" not in result.hard_failure_reasons
        ):
            return False
    else:
        return False
    return _valid_sha256(result.decision_id) and _valid_sha256(result.decision_input_id)


def _canonical_root_review_transitions_v01(
    registry: _TransitionRegistryV01,
) -> tuple[_TransitionDecisionV01, _TransitionDecisionV01]:
    review_ready = _lookup_transition_v01(
        registry=registry,
        abi_major_version=1,
        source_artifact_type="GTAdvisoryReport",
        source_lifecycle_state="VALIDATED",
        actor_role="gt",
        attempted_effect="CREATE_ROOT_DECISION",
        target_artifact_type="RootDecision",
        satisfied_guards=("artifact_valid", "post_vv_passed", "advisory_only"),
        root_commit_present=False,
    )
    post_vv_blocked = _lookup_transition_v01(
        registry=registry,
        abi_major_version=1,
        source_artifact_type="GTAdvisoryReport",
        source_lifecycle_state="VALIDATED",
        actor_role="gt",
        attempted_effect="CREATE_ROOT_DECISION",
        target_artifact_type="RootDecision",
        satisfied_guards=("artifact_valid", "advisory_only"),
        root_commit_present=False,
    )
    expected = (
        (
            review_ready,
            _TRANSITION_RETURN_TO_ROOT,
            "gt_advisory_returns_to_root",
            ("artifact_valid", "post_vv_passed", "advisory_only"),
            (),
        ),
        (
            post_vv_blocked,
            ROOT_DECISION_BLOCKED_FAIL_CLOSED,
            "required_guard_missing",
            ("artifact_valid", "advisory_only"),
            ("post_vv_passed",),
        ),
    )
    for transition, decision, reason, satisfied, missing in expected:
        if (
            transition.rule_id != "gt_advisory_to_root_decision"
            or transition.decision != decision
            or transition.reason_code != reason
            or transition.required_guards
            != ("artifact_valid", "post_vv_passed", "advisory_only")
            or transition.satisfied_guards != satisfied
            or transition.missing_guards != missing
            or transition.matched is not True
            or transition.root_commit_required is not True
            or transition.root_commit_present is not False
        ):
            raise ValueError("root_decision_result_invalid")
    return review_ready, post_vv_blocked


def _result_id(result: RootDecisionResultV01) -> str:
    material = _result_plain(result)
    material.pop("decision_id")
    return _hash(_RESULT_DOMAIN, material)


def _freeze_json_object(value: object) -> _FrozenJSONObject:
    frozen = _freeze_json_snapshot(value, set())
    if type(frozen) is not _FrozenJSONObject or not _frozen_json_valid(frozen):
        raise ValueError("root_decision_input_invalid")
    return frozen


def _freeze_json_snapshot(value: object, active: set[int]) -> object:
    if value is None or type(value) in {bool, int, str}:
        _canonical_json_bytes_v01(value)
        return value
    if type(value) is float:
        _canonical_json_bytes_v01(value)
        return value
    if type(value) in {list, tuple}:
        identity = id(value)
        if identity in active:
            raise ValueError("root_decision_input_invalid")
        active.add(identity)
        try:
            return tuple(_freeze_json_snapshot(item, active) for item in value)
        finally:
            active.remove(identity)
    if isinstance(value, _Mapping):
        identity = id(value)
        if identity in active:
            raise ValueError("root_decision_input_invalid")
        active.add(identity)
        try:
            rows: list[tuple[str, object]] = []
            seen: set[str] = set()
            iterator = iter(value.items())
            while True:
                try:
                    row = next(iterator)
                except StopIteration:
                    break
                if type(row) not in {tuple, list} or len(row) != 2:
                    raise ValueError("root_decision_input_invalid")
                key, item = row
                if type(key) is not str or key in seen:
                    raise ValueError("root_decision_input_invalid")
                seen.add(key)
                rows.append((key, _freeze_json_snapshot(item, active)))
            rows.sort(key=lambda item: item[0])
            return _FrozenJSONObject(tuple(rows))
        finally:
            active.remove(identity)
    raise ValueError("root_decision_input_invalid")


def _frozen_json_valid(value: object) -> bool:
    try:
        if not _frozen_json_structure_valid(value, set()):
            return False
        _canonical_json_bytes_v01(_thaw_json_validated(value))
        return True
    except Exception:
        return False


def _frozen_json_structure_valid(value: object, active: set[int]) -> bool:
    if value is None or type(value) in {bool, int, float, str}:
        try:
            _canonical_json_bytes_v01(value)
            return True
        except Exception:
            return False
    if type(value) not in {tuple, _FrozenJSONObject}:
        return False
    identity = id(value)
    if identity in active:
        return False
    active.add(identity)
    try:
        if type(value) is tuple:
            return all(_frozen_json_structure_valid(item, active) for item in value)
        if type(value.items) is not tuple:
            return False
        previous: str | None = None
        for row in value.items:
            if type(row) is not tuple or len(row) != 2 or type(row[0]) is not str:
                return False
            if previous is not None and row[0] <= previous:
                return False
            previous = row[0]
            if not _frozen_json_structure_valid(row[1], active):
                return False
        return True
    finally:
        active.remove(identity)


def _thaw_json_validated(value: object) -> object:
    if type(value) is _FrozenJSONObject:
        return {key: _thaw_json_validated(item) for key, item in value.items}
    if type(value) is tuple:
        return [_thaw_json_validated(item) for item in value]
    return value


def _thaw_json_value(value: object) -> object:
    if not _frozen_json_valid(value):
        raise ValueError("root_decision_input_invalid")
    return _thaw_json_validated(value)


def _exact_object(value: object, keys: tuple[str, ...]) -> dict[str, object] | None:
    try:
        if type(value) is not _FrozenJSONObject:
            return None
        plain = _thaw_json_value(value)
        if type(plain) is not dict or tuple(sorted(plain)) != tuple(sorted(keys)):
            return None
        return plain
    except Exception:
        return None


def _valid_text(value: object) -> bool:
    return bool(type(value) is str and value and not any(0xD800 <= ord(char) <= 0xDFFF for char in value))


def _valid_sha256(value: object) -> bool:
    return bool(type(value) is str and len(value) == 64 and all(char in "0123456789abcdef" for char in value))


def _valid_text_list(value: object, *, allow_empty: bool) -> bool:
    return bool(type(value) is list and (allow_empty or value) and all(_valid_text(item) for item in value) and len(set(value)) == len(value))


def _valid_text_tuple(value: object, *, allow_empty: bool) -> bool:
    return bool(type(value) is tuple and (allow_empty or value) and all(_valid_text(item) for item in value) and len(set(value)) == len(value))


def _input_plain(value: RootDecisionInputV01) -> dict[str, object]:
    return {
        "decision_input_id": value.decision_input_id,
        "transaction_id": value.transaction_id,
        "target_root_id": value.target_root_id,
        "root_review_packet": _semantic_work_to_plain_dict_v01(value.root_review_packet),
        "post_vv_bundle": _thaw_json_value(value.post_vv_bundle),
        "gt_advisory": _thaw_json_value(value.gt_advisory),
        "policy_state": _thaw_json_value(value.policy_state),
        "permission_state": _thaw_json_value(value.permission_state),
        "temporal_state": _thaw_json_value(value.temporal_state),
        "conflict_state": _thaw_json_value(value.conflict_state),
        "prior_root_state": _thaw_json_value(value.prior_root_state),
    }


def _kernel_plain(value: RootDecisionKernelV01) -> dict[str, object]:
    return {
        "kernel_id": value.kernel_id,
        "kernel_version": value.kernel_version,
        "transition_registry": _transition_registry_to_plain_dict_v01(value.transition_registry),
        "precedence_order": list(value.precedence_order),
        "llm_dependency_allowed": value.llm_dependency_allowed,
        "effect_access": value.effect_access,
    }


def _result_plain(value: RootDecisionResultV01) -> dict[str, object]:
    return {
        "decision_id": value.decision_id,
        "decision_input_id": value.decision_input_id,
        "transaction_id": value.transaction_id,
        "target_root_id": value.target_root_id,
        "decision": value.decision,
        "reason_code": value.reason_code,
        "selected_candidate_id": value.selected_candidate_id,
        "transition_decision": _transition_decision_to_plain_dict_v01(value.transition_decision),
        "hard_failure_reasons": list(value.hard_failure_reasons),
        "missing_evidence_refs": list(value.missing_evidence_refs),
        "conflict_set_ids": list(value.conflict_set_ids),
        "prior_decision_id": value.prior_decision_id,
        "root_commit_created": value.root_commit_created,
        "permission_created": value.permission_created,
        "final_output_created": value.final_output_created,
        "effect_requested": value.effect_requested,
    }


def _hash(domain: str, value: object) -> str:
    return _domain_separated_sha256_hex_v01(domain=domain, payload=_canonical_json_bytes_v01(value))


def _canonical_bytes(value: object) -> bytes:
    return _canonical_json_bytes_v01(value)


def _allowed_reason(error: ValueError, allowed: tuple[str, ...]) -> str | None:
    if len(error.args) == 1 and type(error.args[0]) is str and error.args[0] in allowed:
        return error.args[0]
    return None


def _dedupe(values: list[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))
