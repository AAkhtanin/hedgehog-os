from __future__ import annotations

import ast
from collections.abc import Mapping
from dataclasses import FrozenInstanceError, fields, replace
import inspect
import json
import math
from pathlib import Path

import pytest

from demo.run_living_gauntlet_v01 import _build_semantic_work_fixture_v01
import hedgehog.kernel as kernel_package
import hedgehog.kernel.root_decision_v01 as root


MODULE_PATH = Path(root.__file__)
EXPECTED_ALL = (
    "CanonicalArtifactRefV01", "ArtifactDependencyEdgeV01",
    "RootOwnershipBindingV01", "EvidenceClassBindingV01",
    "AuthorityClassBindingV01", "SealProfileV01", "ArtifactManifestV01",
    "SealVerificationResultV01", "ReplayVerificationResultV01",
    "build_default_seal_profile_v01", "canonical_json_bytes_v01",
    "domain_separated_sha256_hex_v01", "build_canonical_artifact_ref_v01",
    "build_artifact_manifest_v01", "verify_artifact_manifest_v01",
    "verify_artifact_replay_v01", "artifact_manifest_to_plain_dict_v01",
    "seal_verification_result_to_plain_dict_v01",
    "replay_verification_result_to_plain_dict_v01",
)
PUBLIC_FUNCTIONS = (
    "build_root_decision_kernel_v01", "validate_root_decision_kernel_v01",
    "build_root_decision_input_v01", "validate_root_decision_input_v01",
    "decide_root_v01", "validate_root_decision_result_v01",
    "root_decision_kernel_to_plain_dict_v01",
    "root_decision_input_to_plain_dict_v01",
    "root_decision_result_to_plain_dict_v01",
)
INPUT_FIELDS = (
    "decision_input_id", "transaction_id", "target_root_id",
    "root_review_packet", "post_vv_bundle", "gt_advisory", "policy_state",
    "permission_state", "temporal_state", "conflict_state", "prior_root_state",
)
RESULT_FIELDS = (
    "decision_id", "decision_input_id", "transaction_id", "target_root_id",
    "decision", "reason_code", "selected_candidate_id", "transition_decision",
    "hard_failure_reasons", "missing_evidence_refs", "conflict_set_ids",
    "prior_decision_id", "root_commit_created", "permission_created",
    "final_output_created", "effect_requested",
)
KERNEL_FIELDS = (
    "kernel_id", "kernel_version", "transition_registry", "precedence_order",
    "llm_dependency_allowed", "effect_access",
)


@pytest.fixture(scope="module")
def packet():
    return _build_semantic_work_fixture_v01()[3]


@pytest.fixture
def kernel():
    return root.build_root_decision_kernel_v01()


def _states(packet):
    claim_ids = [claim.claim_id for claim in packet.synthesis_proposal.normalized_claims]
    missing = list(packet.missing_evidence_refs)
    return {
        "post_vv_bundle": {
            "bundle_id": "post_vv:fixture:001", "post_vv_passed": True,
            "validated_candidate_ids": claim_ids, "rejected_candidate_ids": [],
            "required_evidence_refs": missing, "provided_evidence_refs": missing,
            "hard_failure_reasons": [],
        },
        "gt_advisory": {
            "advisory_id": "gt:fixture:001", "candidate_ids": claim_ids,
            "selected_candidate_id": claim_ids[0],
            "score_micros_by_candidate": {item: 500_000 for item in claim_ids},
            "source_artifact_type": "GTAdvisoryReport",
            "source_lifecycle_state": "VALIDATED", "actor_role": "gt",
            "attempted_effect": "CREATE_ROOT_DECISION",
            "target_artifact_type": "RootDecision", "advisory_only": True,
            "creates_final_output": False, "requests_effect": False,
        },
        "policy_state": {
            "policy_id": "policy:fixture:001", "identity_passed": True,
            "scope_passed": True, "hard_policy_passed": True,
            "allow_accept": True, "conflict_policy": "DEFER",
            "no_candidate_policy": "NO_UPDATE",
        },
        "permission_state": {
            "permission_required": False, "user_permission_present": False,
            "permission_scope_valid": True, "permission_ref": None,
        },
        "temporal_state": {
            "temporal_valid": True, "expired": False,
            "not_before_satisfied": True,
            "time_envelope_ref": "time_envelope:fixture:001",
        },
        "conflict_state": {
            "material_unresolved_conflict": False,
            "conflict_set_ids": list(packet.conflict_set_ids),
        },
        "prior_root_state": {
            "prior_decision_id": None, "prior_decision": None,
            "prior_selected_candidate_id": None,
        },
    }


def _build(packet, changes=None):
    states = _states(packet)
    for state, updates in (changes or {}).items():
        states[state].update(updates)
    return root.build_root_decision_input_v01(
        transaction_id=packet.transaction_id,
        target_root_id=packet.target_root_id,
        root_review_packet=packet,
        **states,
    )


def _result(packet, kernel, changes=None):
    value = _build(packet, changes)
    return value, root.decide_root_v01(kernel=kernel, decision_input=value)


def _rehash_result(result, **changes):
    provisional = replace(result, decision_id="0" * 64, **changes)
    material = {
        "decision_input_id": provisional.decision_input_id,
        "transaction_id": provisional.transaction_id,
        "target_root_id": provisional.target_root_id,
        "decision": provisional.decision,
        "reason_code": provisional.reason_code,
        "selected_candidate_id": provisional.selected_candidate_id,
        "transition_decision": kernel_package.transition_decision_to_plain_dict_v01(
            provisional.transition_decision
        ),
        "hard_failure_reasons": list(provisional.hard_failure_reasons),
        "missing_evidence_refs": list(provisional.missing_evidence_refs),
        "conflict_set_ids": list(provisional.conflict_set_ids),
        "prior_decision_id": provisional.prior_decision_id,
        "root_commit_created": provisional.root_commit_created,
        "permission_created": provisional.permission_created,
        "final_output_created": provisional.final_output_created,
        "effect_requested": provisional.effect_requested,
    }
    decision_id = kernel_package.domain_separated_sha256_hex_v01(
        domain="hedgehog.kernel.root_decision_result.v01",
        payload=kernel_package.canonical_json_bytes_v01(material),
    )
    return replace(provisional, decision_id=decision_id)


def _lookup_transition(**changes):
    values = {
        "abi_major_version": 1,
        "source_artifact_type": "GTAdvisoryReport",
        "source_lifecycle_state": "VALIDATED",
        "actor_role": "gt",
        "attempted_effect": "CREATE_ROOT_DECISION",
        "target_artifact_type": "RootDecision",
        "satisfied_guards": ("artifact_valid", "post_vv_passed", "advisory_only"),
        "root_commit_present": False,
    }
    values.update(changes)
    return kernel_package.lookup_transition_v01(
        registry=kernel_package.build_default_transition_registry_v01(),
        **values,
    )


@pytest.mark.parametrize("cls,expected", (
    (root.RootDecisionInputV01, INPUT_FIELDS),
    (root.RootDecisionResultV01, RESULT_FIELDS),
    (root.RootDecisionKernelV01, KERNEL_FIELDS),
))
def test_dataclass_field_order(cls, expected):
    assert tuple(field.name for field in fields(cls)) == expected


@pytest.mark.parametrize("cls", (root.RootDecisionInputV01, root.RootDecisionResultV01, root.RootDecisionKernelV01))
def test_dataclasses_frozen(cls, packet, kernel):
    decision_input, result = _result(packet, kernel)
    value = {root.RootDecisionInputV01: decision_input, root.RootDecisionResultV01: result, root.RootDecisionKernelV01: kernel}[cls]
    with pytest.raises(FrozenInstanceError):
        setattr(value, fields(cls)[0].name, "changed")


def test_exact_public_function_surface():
    assert tuple(name for name, value in vars(root).items() if inspect.isfunction(value) and not name.startswith("_")) == PUBLIC_FUNCTIONS


@pytest.mark.parametrize("name", ("RootDecisionInputV01", "RootDecisionResultV01", "RootDecisionKernelV01", *PUBLIC_FUNCTIONS))
def test_direct_package_attributes(name):
    assert getattr(kernel_package, name) is getattr(root, name)


def test_package_all_unchanged():
    assert kernel_package.__all__ == EXPECTED_ALL


def test_root_decision_constants_exact():
    assert root.MODULE_ID == "kernel_root_decision_v01"
    assert root.SLICE_ID == "domain_neutral_reference_kernel_gate1_g1c1"
    assert root.ROOT_DECISION_VERSION == "v0.1"
    assert root.ROOT_DECISIONS == ("BLOCKED_FAIL_CLOSED", "NEEDS_USER", "NEEDS_MORE_EVIDENCE", "DEFER", "REJECT", "NO_UPDATE", "ACCEPT")


def test_kernel_identity_and_boundary(kernel):
    assert root.validate_root_decision_kernel_v01(kernel) == ()
    assert kernel.precedence_order == ("HARD_FAILURE", "NEEDS_USER", "NEEDS_MORE_EVIDENCE", "MATERIAL_CONFLICT", "NO_VALID_CANDIDATE", "POLICY_REJECT", "ACCEPT")
    assert kernel.llm_dependency_allowed is False
    assert kernel.effect_access == "NONE"
    assert kernel == root.build_root_decision_kernel_v01()


@pytest.mark.parametrize("field,value", (
    ("kernel_id", "0" * 64), ("kernel_version", "v9"),
    ("precedence_order", ("ACCEPT",)), ("precedence_order", list()),
    ("llm_dependency_allowed", True), ("effect_access", "EFFECT"),
))
def test_kernel_mutations_rejected(field, value, kernel):
    assert root.validate_root_decision_kernel_v01(replace(kernel, **{field: value}))


def test_valid_input_and_result(packet, kernel):
    decision_input, result = _result(packet, kernel)
    assert root.validate_root_decision_input_v01(kernel=kernel, decision_input=decision_input) == ()
    assert (result.decision, result.reason_code) == ("ACCEPT", "validated_candidate_accepted")
    assert root.validate_root_decision_result_v01(kernel=kernel, decision_input=decision_input, result=result) == ()


STATE_FIELDS = (
    ("post_vv_bundle", "bundle_id"), ("post_vv_bundle", "post_vv_passed"),
    ("post_vv_bundle", "validated_candidate_ids"), ("post_vv_bundle", "rejected_candidate_ids"),
    ("post_vv_bundle", "required_evidence_refs"), ("post_vv_bundle", "provided_evidence_refs"),
    ("post_vv_bundle", "hard_failure_reasons"),
    ("gt_advisory", "advisory_id"), ("gt_advisory", "candidate_ids"),
    ("gt_advisory", "selected_candidate_id"), ("gt_advisory", "score_micros_by_candidate"),
    ("gt_advisory", "source_artifact_type"), ("gt_advisory", "source_lifecycle_state"),
    ("gt_advisory", "actor_role"), ("gt_advisory", "attempted_effect"),
    ("gt_advisory", "target_artifact_type"), ("gt_advisory", "advisory_only"),
    ("gt_advisory", "creates_final_output"), ("gt_advisory", "requests_effect"),
    ("policy_state", "policy_id"), ("policy_state", "identity_passed"),
    ("policy_state", "scope_passed"), ("policy_state", "hard_policy_passed"),
    ("policy_state", "allow_accept"), ("policy_state", "conflict_policy"),
    ("policy_state", "no_candidate_policy"),
    ("permission_state", "permission_required"), ("permission_state", "user_permission_present"),
    ("permission_state", "permission_scope_valid"), ("permission_state", "permission_ref"),
    ("temporal_state", "temporal_valid"), ("temporal_state", "expired"),
    ("temporal_state", "not_before_satisfied"), ("temporal_state", "time_envelope_ref"),
    ("conflict_state", "material_unresolved_conflict"), ("conflict_state", "conflict_set_ids"),
    ("prior_root_state", "prior_decision_id"), ("prior_root_state", "prior_decision"),
    ("prior_root_state", "prior_selected_candidate_id"),
)


@pytest.mark.parametrize("state,field", STATE_FIELDS)
def test_missing_each_state_field_rejected(state, field, packet):
    states = _states(packet)
    del states[state][field]
    with pytest.raises(ValueError):
        root.build_root_decision_input_v01(transaction_id=packet.transaction_id, target_root_id=packet.target_root_id, root_review_packet=packet, **states)


@pytest.mark.parametrize("state", tuple(dict.fromkeys(state for state, _ in STATE_FIELDS)))
def test_extra_field_in_each_state_rejected(state, packet):
    with pytest.raises(ValueError):
        _build(packet, {state: {"unexpected": True}})


@pytest.mark.parametrize("state,field", STATE_FIELDS)
def test_arbitrary_object_in_each_state_field_rejected(state, field, packet):
    with pytest.raises(ValueError):
        _build(packet, {state: {field: object()}})


@pytest.mark.parametrize("state,field,value", (
    ("post_vv_bundle", "post_vv_passed", 1),
    ("post_vv_bundle", "hard_failure_reasons", ["unknown"]),
    ("gt_advisory", "candidate_ids", []),
    ("gt_advisory", "selected_candidate_id", "missing"),
    ("gt_advisory", "source_artifact_type", "ActorContribution"),
    ("gt_advisory", "source_lifecycle_state", "PROPOSED"),
    ("gt_advisory", "actor_role", "provider_llm"),
    ("gt_advisory", "attempted_effect", "CREATE_FINAL_OUTPUT"),
    ("gt_advisory", "target_artifact_type", "RootFinal"),
    ("gt_advisory", "advisory_only", False),
    ("gt_advisory", "creates_final_output", True),
    ("gt_advisory", "requests_effect", True),
    ("policy_state", "conflict_policy", "ACCEPT"),
    ("policy_state", "no_candidate_policy", "DEFER"),
    ("permission_state", "permission_required", 1),
    ("permission_state", "user_permission_present", True),
    ("temporal_state", "temporal_valid", 1),
    ("conflict_state", "conflict_set_ids", []),
    ("prior_root_state", "prior_decision", "UNKNOWN"),
))
def test_state_coherence_mutations_rejected(state, field, value, packet):
    with pytest.raises(ValueError):
        _build(packet, {state: {field: value}})


@pytest.mark.parametrize("changes,decision,reason", (
    ({"policy_state": {"identity_passed": False}}, "BLOCKED_FAIL_CLOSED", "hard_identity_violation"),
    ({"temporal_state": {"expired": True}}, "BLOCKED_FAIL_CLOSED", "hard_temporal_violation"),
    ({"policy_state": {"scope_passed": False}, "gt_advisory": {}}, "BLOCKED_FAIL_CLOSED", "hard_scope_violation"),
    ({"permission_state": {"permission_required": True}}, "NEEDS_USER", "user_permission_missing"),
    ({"post_vv_bundle": {"provided_evidence_refs": []}}, "NEEDS_MORE_EVIDENCE", "required_evidence_missing"),
    ({"conflict_state": {"material_unresolved_conflict": True}, "policy_state": {"conflict_policy": "DEFER"}}, "DEFER", "material_conflict_deferred"),
    ({"conflict_state": {"material_unresolved_conflict": True}, "policy_state": {"conflict_policy": "REJECT"}}, "REJECT", "material_conflict_rejected"),
    ({"gt_advisory": {"selected_candidate_id": None}, "policy_state": {"no_candidate_policy": "NO_UPDATE"}}, "NO_UPDATE", "no_valid_candidate"),
    ({"gt_advisory": {"selected_candidate_id": None}, "policy_state": {"no_candidate_policy": "REJECT"}}, "REJECT", "no_valid_candidate_rejected"),
    ({}, "ACCEPT", "validated_candidate_accepted"),
))
def test_exact_ten_precedence_outcomes(changes, decision, reason, packet, kernel):
    decision_input, result = _result(packet, kernel, changes)
    assert (result.decision, result.reason_code) == (decision, reason)
    assert root.validate_root_decision_result_v01(
        kernel=kernel,
        decision_input=decision_input,
        result=result,
    ) == ()
    assert root.root_decision_result_to_plain_dict_v01(
        result
    ) == root.root_decision_result_to_plain_dict_v01(
        root.decide_root_v01(kernel=kernel, decision_input=decision_input)
    )


@pytest.mark.parametrize("score", (0, 1, 250_000, 500_000, 999_999, 1_000_000))
def test_scores_do_not_override_scope_failure(score, packet, kernel):
    states = _states(packet)
    selected = states["gt_advisory"]["selected_candidate_id"]
    scores = dict(states["gt_advisory"]["score_micros_by_candidate"])
    scores[selected] = score
    value = _build(packet, {"policy_state": {"scope_passed": False}, "gt_advisory": {"score_micros_by_candidate": scores}})
    result = root.decide_root_v01(kernel=kernel, decision_input=value)
    assert (result.decision, result.reason_code) == ("BLOCKED_FAIL_CLOSED", "hard_scope_violation")


@pytest.mark.parametrize("value", (True, -1, 1_000_001, math.nan, math.inf, -math.inf))
def test_invalid_score_rejected(value, packet):
    states = _states(packet)
    selected = states["gt_advisory"]["selected_candidate_id"]
    scores = dict(states["gt_advisory"]["score_micros_by_candidate"])
    scores[selected] = value
    with pytest.raises(ValueError):
        _build(packet, {"gt_advisory": {"score_micros_by_candidate": scores}})


@pytest.mark.parametrize("changes,first_reason", (
    ({"policy_state": {"identity_passed": False}, "permission_state": {"permission_required": True}}, "hard_identity_violation"),
    ({"policy_state": {"scope_passed": False}, "post_vv_bundle": {"provided_evidence_refs": []}}, "hard_scope_violation"),
    ({"policy_state": {"hard_policy_passed": False}, "conflict_state": {"material_unresolved_conflict": True}}, "hard_policy_violation"),
    ({"permission_state": {"permission_required": True}, "post_vv_bundle": {"provided_evidence_refs": []}}, "user_permission_missing"),
    ({"post_vv_bundle": {"provided_evidence_refs": []}, "conflict_state": {"material_unresolved_conflict": True}}, "required_evidence_missing"),
    ({"conflict_state": {"material_unresolved_conflict": True}, "gt_advisory": {"selected_candidate_id": None}}, "material_conflict_deferred"),
    ({"gt_advisory": {"selected_candidate_id": None}}, "no_valid_candidate"),
    ({"policy_state": {"allow_accept": False}}, "policy_rejected_candidate"),
))
def test_precedence_pairs(changes, first_reason, packet, kernel):
    _, result = _result(packet, kernel, changes)
    assert result.reason_code == first_reason


def test_post_vv_failed_is_hard_and_preserves_all_normalized_reasons(packet, kernel):
    value = _build(packet, {"post_vv_bundle": {"post_vv_passed": False, "hard_failure_reasons": ["identity_validation_failed"]}})
    result = root.decide_root_v01(kernel=kernel, decision_input=value)
    assert result.hard_failure_reasons == ("post_vv_hard_failure", "transition_blocked")
    assert result.decision == "BLOCKED_FAIL_CLOSED"


def test_validated_and_rejected_candidate_overlap_is_rejected(packet):
    states = _states(packet)
    candidate = states["post_vv_bundle"]["validated_candidate_ids"][0]
    with pytest.raises(ValueError, match="^root_decision_post_vv_invalid$"):
        _build(packet, {"post_vv_bundle": {"rejected_candidate_ids": [candidate]}})


def test_selected_rejected_candidate_cannot_become_accept(packet, kernel):
    states = _states(packet)
    selected = states["gt_advisory"]["selected_candidate_id"]
    validated = [item for item in states["post_vv_bundle"]["validated_candidate_ids"] if item != selected]
    value = _build(packet, {"post_vv_bundle": {"validated_candidate_ids": validated, "rejected_candidate_ids": [selected]}})
    result = root.decide_root_v01(kernel=kernel, decision_input=value)
    assert (result.decision, result.reason_code) == ("NO_UPDATE", "no_valid_candidate")


def test_permission_scope_and_temporal_hard_failures(packet, kernel):
    value = _build(packet, {"permission_state": {"permission_scope_valid": False}, "temporal_state": {"temporal_valid": False, "expired": True, "not_before_satisfied": False}})
    result = root.decide_root_v01(kernel=kernel, decision_input=value)
    assert result.hard_failure_reasons == ("hard_permission_scope_violation", "hard_temporal_violation")


def test_caller_state_mutation_isolated(packet, kernel):
    states = _states(packet)
    value = root.build_root_decision_input_v01(transaction_id=packet.transaction_id, target_root_id=packet.target_root_id, root_review_packet=packet, **states)
    expected = root.root_decision_input_to_plain_dict_v01(value)
    states["policy_state"]["identity_passed"] = False
    states["gt_advisory"]["candidate_ids"].clear()
    assert root.root_decision_input_to_plain_dict_v01(value) == expected
    assert root.decide_root_v01(kernel=kernel, decision_input=value).decision == "ACCEPT"


class _OneShotMapping(Mapping):
    def __init__(self, rows): self.rows, self.calls = rows, 0
    def __getitem__(self, key): raise AssertionError("getitem forbidden")
    def __iter__(self): raise AssertionError("iter forbidden")
    def __len__(self): return len(self.rows)
    def items(self):
        self.calls += 1
        if self.calls > 1: raise OSError("SECOND_READ_SECRET")
        return iter(self.rows)


def test_mapping_items_consumed_once(packet):
    states = _states(packet)
    mapping = _OneShotMapping(list(states["policy_state"].items()))
    states["policy_state"] = mapping
    root.build_root_decision_input_v01(transaction_id=packet.transaction_id, target_root_id=packet.target_root_id, root_review_packet=packet, **states)
    assert mapping.calls == 1


@pytest.mark.parametrize("rows", (
    [("policy_id", "p"), ("policy_id", "q")],
    [("policy_id",)], [(1, "p")],
))
def test_hostile_or_malformed_mapping_rows_rejected(rows, packet):
    states = _states(packet)
    states["policy_state"] = _OneShotMapping(rows)
    with pytest.raises(ValueError, match="^root_decision_input_invalid$") as caught:
        root.build_root_decision_input_v01(transaction_id=packet.transaction_id, target_root_id=packet.target_root_id, root_review_packet=packet, **states)
    assert caught.value.__cause__ is None


def test_cycle_rejected(packet):
    states = _states(packet)
    cycle = []
    cycle.append(cycle)
    states["policy_state"]["extra"] = cycle
    with pytest.raises(ValueError):
        root.build_root_decision_input_v01(transaction_id=packet.transaction_id, target_root_id=packet.target_root_id, root_review_packet=packet, **states)


@pytest.mark.parametrize("projection", ("kernel", "input", "result"))
def test_projection_json_safe_independent(projection, packet, kernel):
    decision_input, result = _result(packet, kernel)
    value, fn = {
        "kernel": (kernel, root.root_decision_kernel_to_plain_dict_v01),
        "input": (decision_input, root.root_decision_input_to_plain_dict_v01),
        "result": (result, root.root_decision_result_to_plain_dict_v01),
    }[projection]
    first, second = fn(value), fn(value)
    json.dumps(first, allow_nan=False)
    assert first == second
    first[next(iter(first))] = "changed"
    assert fn(value) == second


def test_input_identity_changes_for_each_state(packet):
    baseline = _build(packet)
    changes = (
        {"post_vv_bundle": {"provided_evidence_refs": []}},
        {"gt_advisory": {"selected_candidate_id": None}},
        {"policy_state": {"allow_accept": False}},
        {"permission_state": {"permission_required": True}},
        {"temporal_state": {"expired": True}},
        {"conflict_state": {"material_unresolved_conflict": True}},
        {"prior_root_state": {"prior_decision_id": "decision:prior", "prior_decision": "ACCEPT"}},
    )
    assert all(_build(packet, change).decision_input_id != baseline.decision_input_id for change in changes)


RESULT_MUTATIONS = (
    ("decision_id", "0" * 64), ("decision_input_id", "1" * 64),
    ("transaction_id", "changed"), ("target_root_id", "changed"),
    ("decision", "REJECT"), ("reason_code", "changed"),
    ("selected_candidate_id", None), ("hard_failure_reasons", ("hard_scope_violation",)),
    ("missing_evidence_refs", ("missing",)), ("conflict_set_ids", ()),
    ("prior_decision_id", "prior"), ("root_commit_created", False),
    ("permission_created", True), ("final_output_created", True),
    ("effect_requested", True),
)


@pytest.mark.parametrize("field,value", RESULT_MUTATIONS)
def test_every_result_field_mutation_rejected(field, value, packet, kernel):
    decision_input, result = _result(packet, kernel)
    errors = root.validate_root_decision_result_v01(kernel=kernel, decision_input=decision_input, result=replace(result, **{field: value}))
    assert errors


@pytest.mark.parametrize("field,reason", (
    ("permission_created", "root_decision_permission_creation_forbidden"),
    ("final_output_created", "root_decision_final_output_creation_forbidden"),
    ("effect_requested", "root_decision_effect_request_forbidden"),
))
def test_forbidden_creation_mutations_report_exact_reason(field, reason, packet, kernel):
    decision_input, result = _result(packet, kernel)
    errors = root.validate_root_decision_result_v01(
        kernel=kernel,
        decision_input=decision_input,
        result=replace(result, **{field: True}),
    )
    assert reason in errors


def test_hard_failure_forged_accept_reports_override_reason(packet, kernel):
    decision_input, expected = _result(
        packet,
        kernel,
        {"policy_state": {"identity_passed": False}},
    )
    forged = _rehash_result(
        expected,
        decision="ACCEPT",
        reason_code="validated_candidate_accepted",
        selected_candidate_id=packet.synthesis_proposal.normalized_claims[0].claim_id,
        hard_failure_reasons=(),
    )
    errors = root.validate_root_decision_result_v01(
        kernel=kernel,
        decision_input=decision_input,
        result=forged,
    )
    assert "hard_predicate_override_forbidden" in errors


def test_candidate_outside_packet_has_exact_binding_reason(packet):
    states = _states(packet)
    candidate_ids = [*states["gt_advisory"]["candidate_ids"], "claim:outside"]
    scores = dict(states["gt_advisory"]["score_micros_by_candidate"])
    scores["claim:outside"] = 0
    with pytest.raises(
        ValueError,
        match="^root_decision_candidate_binding_invalid$",
    ):
        _build(
            packet,
            {"gt_advisory": {"candidate_ids": candidate_ids, "score_micros_by_candidate": scores}},
        )


def test_selected_candidate_outside_candidate_ids_has_exact_binding_reason(packet):
    with pytest.raises(
        ValueError,
        match="^root_decision_candidate_binding_invalid$",
    ):
        _build(packet, {"gt_advisory": {"selected_candidate_id": "claim:outside"}})


def test_score_keys_mismatch_has_exact_binding_reason(packet):
    states = _states(packet)
    scores = dict(states["gt_advisory"]["score_micros_by_candidate"])
    scores.pop(next(iter(scores)))
    with pytest.raises(
        ValueError,
        match="^root_decision_candidate_binding_invalid$",
    ):
        _build(packet, {"gt_advisory": {"score_micros_by_candidate": scores}})


@pytest.mark.parametrize("field,value", (
    ("source_artifact_type", "ActorContribution"),
    ("source_lifecycle_state", "PROPOSED"),
    ("actor_role", "provider_llm"),
    ("attempted_effect", "CREATE_FINAL_OUTPUT"),
    ("target_artifact_type", "RootFinal"),
))
def test_transition_tuple_mutation_has_exact_blocked_reason(field, value, packet):
    with pytest.raises(ValueError, match="^root_decision_transition_blocked$"):
        _build(packet, {"gt_advisory": {field: value}})


@pytest.mark.parametrize("field,value", (
    ("advisory_only", False),
    ("creates_final_output", True),
    ("requests_effect", True),
))
def test_gt_authority_flags_remain_gt_advisory_invalid(field, value, packet):
    with pytest.raises(ValueError, match="^root_decision_gt_advisory_invalid$"):
        _build(packet, {"gt_advisory": {field: value}})


def test_projection_rejects_self_hashed_unknown_reason(packet, kernel):
    _, result = _result(packet, kernel)
    forged = _rehash_result(result, reason_code="made_up_reason")
    with pytest.raises(ValueError, match="^root_decision_result_invalid$"):
        root.root_decision_result_to_plain_dict_v01(forged)


@pytest.mark.parametrize("changes", (
    {
        "decision": "BLOCKED_FAIL_CLOSED",
        "reason_code": "validated_candidate_accepted",
        "selected_candidate_id": None,
        "hard_failure_reasons": ("hard_identity_violation",),
    },
    {
        "decision": "NEEDS_USER",
        "reason_code": "required_evidence_missing",
        "selected_candidate_id": None,
    },
    {
        "decision": "NEEDS_MORE_EVIDENCE",
        "reason_code": "user_permission_missing",
        "selected_candidate_id": None,
        "missing_evidence_refs": ("evidence:missing",),
    },
    {
        "decision": "DEFER",
        "reason_code": "validated_candidate_accepted",
        "selected_candidate_id": None,
    },
    {
        "decision": "REJECT",
        "reason_code": "validated_candidate_accepted",
        "selected_candidate_id": None,
    },
    {
        "decision": "NO_UPDATE",
        "reason_code": "validated_candidate_accepted",
        "selected_candidate_id": None,
    },
    {"decision": "ACCEPT", "reason_code": "no_valid_candidate"},
))
def test_projection_rejects_every_illegal_decision_reason_pair(changes, packet, kernel):
    _, result = _result(packet, kernel)
    forged = _rehash_result(result, **changes)
    with pytest.raises(ValueError, match="^root_decision_result_invalid$"):
        root.root_decision_result_to_plain_dict_v01(forged)


def test_projection_rejects_self_hashed_blocked_without_hard_reason(packet, kernel):
    _, result = _result(packet, kernel)
    forged = _rehash_result(
        result,
        decision="BLOCKED_FAIL_CLOSED",
        reason_code="hard_identity_violation",
        selected_candidate_id=None,
        hard_failure_reasons=(),
    )
    with pytest.raises(ValueError, match="^root_decision_result_invalid$"):
        root.root_decision_result_to_plain_dict_v01(forged)


def test_projection_rejects_blocked_reason_not_first_hard_reason(packet, kernel):
    _, result = _result(packet, kernel)
    forged = _rehash_result(
        result,
        decision="BLOCKED_FAIL_CLOSED",
        reason_code="hard_scope_violation",
        selected_candidate_id=None,
        hard_failure_reasons=("hard_identity_violation", "hard_scope_violation"),
    )
    with pytest.raises(ValueError, match="^root_decision_result_invalid$"):
        root.root_decision_result_to_plain_dict_v01(forged)


def test_projection_rejects_non_blocked_result_with_hard_reasons(packet, kernel):
    _, result = _result(packet, kernel)
    forged = _rehash_result(
        result,
        hard_failure_reasons=("hard_identity_violation",),
    )
    with pytest.raises(ValueError, match="^root_decision_result_invalid$"):
        root.root_decision_result_to_plain_dict_v01(forged)


def test_projection_rejects_needs_evidence_without_missing_refs(packet, kernel):
    _, result = _result(
        packet,
        kernel,
        {"post_vv_bundle": {"provided_evidence_refs": []}},
    )
    forged = _rehash_result(result, missing_evidence_refs=())
    with pytest.raises(ValueError, match="^root_decision_result_invalid$"):
        root.root_decision_result_to_plain_dict_v01(forged)


@pytest.mark.parametrize("field", (
    "permission_created",
    "final_output_created",
    "effect_requested",
))
def test_projection_rejects_self_hashed_forbidden_creation(field, packet, kernel):
    _, result = _result(packet, kernel)
    forged = _rehash_result(result, **{field: True})
    with pytest.raises(ValueError, match="^root_decision_result_invalid$"):
        root.root_decision_result_to_plain_dict_v01(forged)


@pytest.mark.parametrize("lookup_changes", (
    {
        "source_artifact_type": "OrchestratorRouteProposal",
        "source_lifecycle_state": "PROPOSED",
        "actor_role": "orchestrator",
        "attempted_effect": "CREATE_TARGET_ARTIFACT",
        "target_artifact_type": "RootAcceptedRoute",
        "satisfied_guards": ("artifact_valid", "target_root_bound"),
    },
    {
        "source_artifact_type": "ActorContribution",
        "source_lifecycle_state": "VALIDATED",
        "actor_role": "post_vv",
        "attempted_effect": "CREATE_TARGET_ARTIFACT",
        "target_artifact_type": "ValidatedEvidence",
        "satisfied_guards": ("artifact_valid", "required_evidence_present"),
    },
    {"root_commit_present": True},
    {
        "source_artifact_type": "ActorContribution",
        "source_lifecycle_state": "VALIDATED",
        "actor_role": "post_vv",
        "attempted_effect": "CREATE_TARGET_ARTIFACT",
        "target_artifact_type": "ResultProposal",
        "satisfied_guards": (),
    },
), ids=("route_return", "alternate_allow", "root_commit_present", "unmatched"))
def test_self_hashed_alternate_registry_transition_rejected(
    lookup_changes,
    packet,
    kernel,
):
    decision_input, result = _result(packet, kernel)
    alternate = _lookup_transition(**lookup_changes)
    assert kernel_package.validate_transition_decision_v01(
        registry=kernel.transition_registry,
        decision=alternate,
    ) == ()
    forged = _rehash_result(result, transition_decision=alternate)
    with pytest.raises(ValueError, match="^root_decision_result_invalid$"):
        root.root_decision_result_to_plain_dict_v01(forged)
    assert root.validate_root_decision_result_v01(
        kernel=kernel,
        decision_input=decision_input,
        result=forged,
    )


def test_canonical_gt_root_review_transition_still_projects(packet, kernel):
    decision_input, result = _result(packet, kernel)
    transition = kernel_package.transition_decision_to_plain_dict_v01(
        result.transition_decision
    )
    assert transition["rule_id"] == "gt_advisory_to_root_decision"
    assert transition["decision"] == "RETURN_TO_ROOT"
    assert transition["reason_code"] == "gt_advisory_returns_to_root"
    assert transition["matched"] is True
    assert transition["root_commit_required"] is True
    assert transition["root_commit_present"] is False
    assert transition["missing_guards"] == []
    assert root.validate_root_decision_result_v01(
        kernel=kernel,
        decision_input=decision_input,
        result=result,
    ) == ()
    assert root.root_decision_result_to_plain_dict_v01(result)[
        "transition_decision"
    ] == transition


def test_post_vv_failure_uses_exact_blocked_transition_and_projects(packet, kernel):
    decision_input, result = _result(
        packet,
        kernel,
        {
            "post_vv_bundle": {
                "post_vv_passed": False,
                "hard_failure_reasons": ["identity_validation_failed"],
            }
        },
    )
    transition = kernel_package.transition_decision_to_plain_dict_v01(
        result.transition_decision
    )
    assert result.decision == "BLOCKED_FAIL_CLOSED"
    assert result.hard_failure_reasons == (
        "post_vv_hard_failure",
        "transition_blocked",
    )
    assert transition["rule_id"] == "gt_advisory_to_root_decision"
    assert transition["decision"] == "BLOCKED_FAIL_CLOSED"
    assert transition["reason_code"] == "required_guard_missing"
    assert transition["required_guards"] == [
        "artifact_valid",
        "post_vv_passed",
        "advisory_only",
    ]
    assert transition["satisfied_guards"] == ["artifact_valid", "advisory_only"]
    assert transition["missing_guards"] == ["post_vv_passed"]
    assert transition["matched"] is True
    assert transition["root_commit_required"] is True
    assert transition["root_commit_present"] is False
    assert root.validate_root_decision_result_v01(
        kernel=kernel,
        decision_input=decision_input,
        result=result,
    ) == ()
    assert root.root_decision_result_to_plain_dict_v01(result)[
        "transition_decision"
    ] == transition


@pytest.mark.parametrize("hard_code", root.POST_VV_HARD_FAILURE_CODES)
def test_every_post_vv_hard_code_result_validates_and_projects(
    hard_code,
    packet,
    kernel,
):
    decision_input, result = _result(
        packet,
        kernel,
        {
            "post_vv_bundle": {
                "post_vv_passed": False,
                "hard_failure_reasons": [hard_code],
            }
        },
    )
    assert root.validate_root_decision_result_v01(
        kernel=kernel,
        decision_input=decision_input,
        result=result,
    ) == ()
    projection = root.root_decision_result_to_plain_dict_v01(result)
    assert projection["transition_decision"]["decision"] == "BLOCKED_FAIL_CLOSED"
    assert projection["hard_failure_reasons"] == [
        "post_vv_hard_failure",
        "transition_blocked",
    ]


def test_post_vv_failure_with_earlier_identity_failure_validates(packet, kernel):
    decision_input, result = _result(
        packet,
        kernel,
        {
            "policy_state": {"identity_passed": False},
            "post_vv_bundle": {
                "post_vv_passed": False,
                "hard_failure_reasons": ["identity_validation_failed"],
            },
        },
    )
    assert result.reason_code == "hard_identity_violation"
    assert result.hard_failure_reasons == (
        "hard_identity_violation",
        "post_vv_hard_failure",
        "transition_blocked",
    )
    assert root.validate_root_decision_result_v01(
        kernel=kernel,
        decision_input=decision_input,
        result=result,
    ) == ()
    assert root.root_decision_result_to_plain_dict_v01(result)[
        "reason_code"
    ] == "hard_identity_violation"


@pytest.mark.parametrize("hard_failure_reasons", (
    ("transition_blocked",),
    ("post_vv_hard_failure",),
))
def test_review_ready_transition_rejects_post_vv_transition_hard_reasons(
    hard_failure_reasons,
    packet,
    kernel,
):
    _, result = _result(packet, kernel)
    forged = _rehash_result(
        result,
        decision="BLOCKED_FAIL_CLOSED",
        reason_code=hard_failure_reasons[0],
        selected_candidate_id=None,
        hard_failure_reasons=hard_failure_reasons,
    )
    with pytest.raises(ValueError, match="^root_decision_result_invalid$"):
        root.root_decision_result_to_plain_dict_v01(forged)


@pytest.mark.parametrize("changes", (
    {},
    {
        "decision": "BLOCKED_FAIL_CLOSED",
        "reason_code": "transition_blocked",
        "selected_candidate_id": None,
        "hard_failure_reasons": ("transition_blocked",),
    },
    {
        "decision": "BLOCKED_FAIL_CLOSED",
        "reason_code": "post_vv_hard_failure",
        "selected_candidate_id": None,
        "hard_failure_reasons": ("post_vv_hard_failure",),
    },
    {
        "decision": "NEEDS_USER",
        "reason_code": "user_permission_missing",
        "selected_candidate_id": None,
        "hard_failure_reasons": (),
    },
), ids=("accept", "missing_post_vv", "missing_transition", "needs_user"))
def test_blocked_transition_rejects_incoherent_outer_result(
    changes,
    packet,
    kernel,
):
    _, review_ready = _result(packet, kernel)
    blocked_transition = _lookup_transition(
        satisfied_guards=("artifact_valid", "advisory_only")
    )
    forged = _rehash_result(
        review_ready,
        transition_decision=blocked_transition,
        **changes,
    )
    with pytest.raises(ValueError, match="^root_decision_result_invalid$"):
        root.root_decision_result_to_plain_dict_v01(forged)


def test_transition_result_mutation_rejected(packet, kernel):
    decision_input, result = _result(packet, kernel)
    mutated_transition = replace(result.transition_decision, decision_id="0" * 64)
    assert root.validate_root_decision_result_v01(kernel=kernel, decision_input=decision_input, result=replace(result, transition_decision=mutated_transition))


def test_root_result_creation_boundaries(packet, kernel):
    _, result = _result(packet, kernel)
    assert result.root_commit_created is True
    assert result.permission_created is False
    assert result.final_output_created is False
    assert result.effect_requested is False


def test_two_kernels_inputs_results_and_projections_equal(packet):
    first_kernel, second_kernel = root.build_root_decision_kernel_v01(), root.build_root_decision_kernel_v01()
    first_input, second_input = _build(packet), _build(packet)
    first_result = root.decide_root_v01(kernel=first_kernel, decision_input=first_input)
    second_result = root.decide_root_v01(kernel=second_kernel, decision_input=second_input)
    assert first_kernel == second_kernel
    assert first_input == second_input
    assert first_result == second_result
    assert root.root_decision_result_to_plain_dict_v01(first_result) == root.root_decision_result_to_plain_dict_v01(second_result)


@pytest.mark.parametrize("hard_code", root.POST_VV_HARD_FAILURE_CODES)
def test_every_post_vv_hard_code_blocks(hard_code, packet, kernel):
    value = _build(packet, {"post_vv_bundle": {"post_vv_passed": False, "hard_failure_reasons": [hard_code]}})
    result = root.decide_root_v01(kernel=kernel, decision_input=value)
    assert result.decision == "BLOCKED_FAIL_CLOSED"
    assert "post_vv_hard_failure" in result.hard_failure_reasons


@pytest.mark.parametrize("prior_decision", root.ROOT_DECISIONS)
def test_every_prior_decision_is_metadata_only(prior_decision, packet, kernel):
    value = _build(packet, {"prior_root_state": {"prior_decision_id": f"prior:{prior_decision}", "prior_decision": prior_decision}})
    result = root.decide_root_v01(kernel=kernel, decision_input=value)
    assert result.decision == "ACCEPT"
    assert result.prior_decision_id == f"prior:{prior_decision}"


@pytest.mark.parametrize("claim_index", range(5))
def test_every_packet_candidate_can_be_selected_when_valid(claim_index, packet, kernel):
    states = _states(packet)
    selected = states["gt_advisory"]["candidate_ids"][claim_index]
    value = _build(packet, {"gt_advisory": {"selected_candidate_id": selected}})
    result = root.decide_root_v01(kernel=kernel, decision_input=value)
    assert result.decision == "ACCEPT"
    assert result.selected_candidate_id == selected


@pytest.mark.parametrize("claim_index,score", tuple((index, score) for index in range(5) for score in (0, 1_000_000)))
def test_score_boundaries_for_every_candidate_are_metadata(claim_index, score, packet, kernel):
    states = _states(packet)
    candidate = states["gt_advisory"]["candidate_ids"][claim_index]
    scores = dict(states["gt_advisory"]["score_micros_by_candidate"])
    scores[candidate] = score
    value = _build(packet, {"gt_advisory": {"score_micros_by_candidate": scores}})
    assert root.decide_root_v01(kernel=kernel, decision_input=value).decision == "ACCEPT"


@pytest.mark.parametrize("state,expected", (
    ("post_vv_bundle", "root_decision_post_vv_invalid"),
    ("gt_advisory", "root_decision_gt_advisory_invalid"),
    ("policy_state", "root_decision_policy_state_invalid"),
    ("permission_state", "root_decision_permission_state_invalid"),
    ("temporal_state", "root_decision_temporal_state_invalid"),
    ("conflict_state", "root_decision_conflict_state_invalid"),
    ("prior_root_state", "root_decision_prior_state_invalid"),
))
def test_each_state_builder_has_stable_rejection(state, expected, packet):
    states = _states(packet)
    states[state] = {}
    with pytest.raises(ValueError, match=f"^{expected}$"):
        root.build_root_decision_input_v01(transaction_id=packet.transaction_id, target_root_id=packet.target_root_id, root_review_packet=packet, **states)


@pytest.mark.parametrize("packet_field,value", (
    ("transaction_id", "other"), ("target_root_id", "other"),
    ("review_state", "OTHER"), ("authority_class", "ROOT"),
    ("root_decision_created", True), ("permission_created", True),
    ("final_output_created", True),
))
def test_packet_binding_mutations_rejected(packet_field, value, packet):
    states = _states(packet)
    with pytest.raises(ValueError):
        root.build_root_decision_input_v01(transaction_id=packet.transaction_id, target_root_id=packet.target_root_id, root_review_packet=replace(packet, **{packet_field: value}), **states)


class _ExplosiveMapping(Mapping):
    def __getitem__(self, key): raise OSError("CALLER_SECRET")
    def __iter__(self): raise OSError("CALLER_SECRET")
    def __len__(self): raise OSError("CALLER_SECRET")
    def items(self): raise OSError("CALLER_SECRET")


def test_hostile_mapping_sanitized(packet):
    states = _states(packet)
    states["policy_state"] = _ExplosiveMapping()
    with pytest.raises(ValueError) as caught:
        root.build_root_decision_input_v01(transaction_id=packet.transaction_id, target_root_id=packet.target_root_id, root_review_packet=packet, **states)
    assert str(caught.value) == "root_decision_input_invalid"
    assert "CALLER_SECRET" not in str(caught.value)
    assert caught.value.__cause__ is None


def test_base_exception_not_swallowed(monkeypatch):
    monkeypatch.setattr(root, "_build_default_transition_registry_v01", lambda: (_ for _ in ()).throw(KeyboardInterrupt()))
    with pytest.raises(KeyboardInterrupt):
        root.build_root_decision_kernel_v01()


@pytest.mark.parametrize("token", (
    "hedgehog.domains", "import demo", "import tests", "RootOrchestrator",
    "gt_validator", "post_vv import", "import requests", "socket", "urllib",
    "pathlib", "subprocess", "open(", "getenv", "random.", "datetime.now",
    "callback", "effect_hook", "build_action_commit", "build_execution_request",
    "writeback",
))
def test_static_forbidden_tokens_absent(token):
    assert token not in MODULE_PATH.read_text(encoding="utf-8")


def test_static_import_boundary():
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    imports = {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    assert imports <= {"__future__", "collections.abc", "dataclasses", "hedgehog.kernel.integrity_replay_v01", "hedgehog.kernel.semantic_work_v01", "hedgehog.kernel.transition_registry_v01"}
