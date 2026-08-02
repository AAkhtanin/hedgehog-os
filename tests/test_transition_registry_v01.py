from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, fields, replace
import hashlib
import inspect
import json
from pathlib import Path
import re

import pytest

import hedgehog.kernel as kernel_package
from hedgehog.kernel.abi_v01 import ARTIFACT_TYPES, LIFECYCLE_STATES
from hedgehog.kernel.integrity_replay_v01 import (
    canonical_json_bytes_v01,
    domain_separated_sha256_hex_v01,
)
import hedgehog.kernel.transition_registry_v01 as transition


MODULE_PATH = Path(transition.__file__)
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
    "build_default_transition_registry_v01", "validate_transition_rule_v01",
    "validate_transition_registry_v01", "lookup_transition_v01",
    "validate_transition_decision_v01", "transition_rule_to_plain_dict_v01",
    "transition_decision_to_plain_dict_v01", "transition_registry_to_plain_dict_v01",
)
ACTION_PACKET_PUBLIC_FUNCTIONS = (
    "action_packet_transition_rule_material_v01",
    "validate_action_packet_transition_rule_v01",
    "action_packet_transition_rule_to_plain_dict_v01",
    "build_action_packet_transition_registry_profile_v01",
    "validate_action_packet_transition_registry_profile_v01",
    "action_packet_transition_registry_material_v01",
    "action_packet_transition_registry_to_plain_dict_v01",
    "lookup_action_packet_transition_rule_v01",
)
RULE_FIELDS = (
    "rule_id", "abi_major_version", "source_artifact_type",
    "source_lifecycle_state", "actor_role", "attempted_effect",
    "target_artifact_type", "required_guards", "decision", "reason_code",
    "root_commit_required",
)
DECISION_FIELDS = (
    "decision_id", "registry_id", "rule_id", "abi_major_version",
    "source_artifact_type", "source_lifecycle_state", "actor_role",
    "attempted_effect", "target_artifact_type", "required_guards",
    "satisfied_guards", "missing_guards", "decision", "reason_code",
    "root_commit_required", "root_commit_present", "matched",
)
REGISTRY_FIELDS = ("registry_id", "registry_version", "abi_major_version", "rules")
ACTION_PACKET_RULE_FIELDS = (
    "transition_rule_id",
    "source_state",
    "target_state",
    "transition_class_code",
    "permitted_component_code",
    "root_decision_requirement_code",
    "required_evidence_codes",
    "effect_consumption_class",
    "adapter_invocation_relation_code",
    "terminal_target",
    "reason_code",
    "fail_closed_reason_codes",
)
ACTION_PACKET_REGISTRY_FIELDS = (
    "transition_registry_id",
    "registry_profile_version",
    "lifecycle_profile_id",
    "ordered_transition_rules",
)
LEGACY_REGISTRY_ID = (
    "336c082d1520d49cf9b23d1c6d983637b7835d8fa863a83dbbae82a11bfa26be"
)
LEGACY_RULE_IDS = (
    "route_proposal_to_root_accepted_route",
    "root_accepted_route_to_runtime_topology",
    "actor_contribution_to_validated_evidence",
    "result_proposal_to_post_vv_report",
    "post_vv_report_to_gt_advisory",
    "gt_advisory_to_root_decision",
    "root_decision_to_root_owned_intent",
    "root_decision_to_execution_request",
    "evidence_receipt_to_root_review",
    "root_decision_to_root_final",
    "root_final_to_transaction_outcome",
    "cross_root_evidence_to_root_review",
    "provider_contribution_to_root_decision_forbidden",
    "drs_evidence_to_permission_forbidden",
    "gt_advisory_to_root_final_forbidden",
    "receipt_to_permission_forbidden",
    "causal_evidence_to_root_decision_forbidden",
    "domain_adapter_effect_request_forbidden",
)
ACTION_PACKET_REGISTRY_ID = (
    "acptr_v01:3a0fb8ffbabca39ff96c0624f8da89eb82222c277c54d932112ebaa0eef97eab"
)
ACTION_PACKET_EXPECTED_ROWS = (
    (
        "g2a_t01_activate_root_authorization", "CREATED", "ROOT_AUTHORIZED",
        "LIFECYCLE_ACTIVATION", "lifecycle_runtime",
        "EXISTING_SOURCE_AUTHORIZATION",
        ("packet_genesis_valid", "source_root_authorization_valid",
         "idempotency_acquisition_valid"),
        "NOT_CONSUMED", "NO_ADAPTER_INVOCATION", False,
        "root_authorization_activated",
        ("packet_genesis_invalid", "source_root_authorization_invalid",
         "wrong_owning_root", "idempotency_acquisition_invalid"),
    ),
    (
        "g2a_t02_queue", "ROOT_AUTHORIZED", "QUEUED", "DETERMINISTIC",
        "lifecycle_runtime", "NONE",
        ("transition_history_valid", "temporal_authority_valid",
         "mandatory_dependencies_current", "idempotency_reservation_owned"),
        "NOT_CONSUMED", "NO_ADAPTER_INVOCATION", False, "packet_queued",
        ("packet_non_executable", "transition_history_invalid",
         "temporal_authority_invalid", "mandatory_dependency_invalid",
         "idempotency_reservation_invalid"),
    ),
    (
        "g2a_t03_pending", "QUEUED", "PENDING_FULFILLMENT",
        "DETERMINISTIC", "exclusive_corridor", "NONE",
        ("immediate_prefulfillment_validation_pass",
         "transition_history_valid", "idempotency_reservation_owned"),
        "NOT_CONSUMED", "NO_ADAPTER_INVOCATION", False,
        "pending_fulfillment",
        ("current_eligibility_invalid", "transition_history_invalid",
         "idempotency_reservation_invalid"),
    ),
    (
        "g2a_t04_fulfill_mock", "PENDING_FULFILLMENT", "FULFILLED_MOCK",
        "DETERMINISTIC_CONSUMING", "exclusive_corridor", "NONE",
        ("mock_adapter_result_valid", "effect_consumption_evidence_valid",
         "idempotency_reservation_owned"),
        "CONSUMED", "CORRIDOR_INVOCATION_CONSUMED", False,
        "fulfilled_mock",
        ("adapter_call_failed", "effect_consumption_evidence_missing",
         "current_eligibility_changed", "idempotency_reservation_invalid"),
    ),
    (
        "g2a_t05_receipt", "FULFILLED_MOCK", "RECEIPT_RECEIVED",
        "DETERMINISTIC_CONSUMING", "receipt_observer", "NONE",
        ("terminal_receipt_valid", "fulfillment_consumption_evidence_valid"),
        "CONSUMED", "POST_INVOCATION_RECEIPT_OBSERVATION", True,
        "receipt_received",
        ("receipt_invalid", "packet_binding_mismatch",
         "idempotency_binding_mismatch", "receipt_authority_claimed",
         "consumption_evidence_missing"),
    ),
    (
        "g2a_t06_created_block", "CREATED", "BLOCKED", "DETERMINISTIC",
        "lifecycle_runtime", "NONE",
        ("packet_genesis_valid", "blocking_evidence_valid"),
        "NOT_CONSUMED", "NO_ADAPTER_INVOCATION", True, "packet_blocked",
        ("packet_genesis_invalid", "blocking_evidence_missing",
         "authority_expansion_detected"),
    ),
    (
        "g2a_t07_authorized_block", "ROOT_AUTHORIZED", "BLOCKED",
        "DETERMINISTIC", "lifecycle_runtime", "NONE",
        ("blocking_evidence_valid", "authority_policy_valid",
         "idempotency_reservation_owned"),
        "NOT_CONSUMED", "NO_ADAPTER_INVOCATION", True, "packet_blocked",
        ("blocking_evidence_missing", "authority_expansion_detected",
         "authority_policy_invalid", "idempotency_reservation_invalid"),
    ),
    (
        "g2a_t08_queued_block", "QUEUED", "BLOCKED", "DETERMINISTIC",
        "lifecycle_runtime", "NONE",
        ("blocking_evidence_valid", "authority_policy_valid",
         "idempotency_reservation_owned"),
        "NOT_CONSUMED", "NO_ADAPTER_INVOCATION", True, "packet_blocked",
        ("blocking_evidence_missing", "authority_expansion_detected",
         "authority_policy_invalid", "idempotency_reservation_invalid"),
    ),
    (
        "g2a_t09_pending_block", "PENDING_FULFILLMENT", "BLOCKED",
        "DETERMINISTIC", "exclusive_corridor", "NONE",
        ("immediate_eligibility_failure_valid", "adapter_not_called",
         "idempotency_reservation_owned"),
        "NOT_CONSUMED", "NO_ADAPTER_INVOCATION", True, "packet_blocked",
        ("adapter_already_called", "blocking_evidence_missing",
         "idempotency_reservation_invalid"),
    ),
    (
        "g2a_t10_failed_block", "FAILED", "BLOCKED", "DETERMINISTIC",
        "lifecycle_runtime", "NONE",
        ("failed_non_consuming_provenance_valid",
         "retry_ineligibility_evidence_valid",
         "idempotency_reservation_owned"),
        "NOT_CONSUMED", "NO_ADAPTER_INVOCATION", True, "packet_blocked",
        ("failed_provenance_invalid", "retry_ineligibility_evidence_missing",
         "authority_expansion_detected", "idempotency_reservation_invalid"),
    ),
    (
        "g2a_t11_created_expire", "CREATED", "EXPIRED", "DETERMINISTIC",
        "temporal_validator", "NONE",
        ("packet_genesis_valid", "temporal_authority_valid",
         "evaluation_time_valid"),
        "NOT_CONSUMED", "NO_ADAPTER_INVOCATION", True, "packet_expired",
        ("packet_genesis_invalid", "temporal_authority_invalid",
         "evaluation_time_invalid", "prior_terminal_state"),
    ),
    (
        "g2a_t12_authorized_expire", "ROOT_AUTHORIZED", "EXPIRED",
        "DETERMINISTIC", "temporal_validator", "NONE",
        ("temporal_authority_valid", "evaluation_time_valid",
         "idempotency_reservation_owned"),
        "NOT_CONSUMED", "NO_ADAPTER_INVOCATION", True, "packet_expired",
        ("temporal_authority_invalid", "evaluation_time_invalid",
         "prior_terminal_state", "idempotency_reservation_invalid"),
    ),
    (
        "g2a_t13_queued_expire", "QUEUED", "EXPIRED", "DETERMINISTIC",
        "temporal_validator", "NONE",
        ("temporal_authority_valid", "evaluation_time_valid",
         "idempotency_reservation_owned"),
        "NOT_CONSUMED", "NO_ADAPTER_INVOCATION", True, "packet_expired",
        ("temporal_authority_invalid", "evaluation_time_invalid",
         "prior_terminal_state", "idempotency_reservation_invalid"),
    ),
    (
        "g2a_t14_pending_expire", "PENDING_FULFILLMENT", "EXPIRED",
        "DETERMINISTIC", "exclusive_corridor", "NONE",
        ("immediate_temporal_validation_pass", "evaluation_time_valid",
         "idempotency_reservation_owned"),
        "NOT_CONSUMED", "NO_ADAPTER_INVOCATION", True, "packet_expired",
        ("adapter_already_called", "temporal_authority_invalid",
         "evaluation_time_invalid", "idempotency_reservation_invalid"),
    ),
    (
        "g2a_t15_failed_expire", "FAILED", "EXPIRED", "DETERMINISTIC",
        "temporal_validator", "NONE",
        ("failed_non_consuming_provenance_valid", "temporal_authority_valid",
         "evaluation_time_valid", "idempotency_reservation_owned"),
        "NOT_CONSUMED", "NO_ADAPTER_INVOCATION", True, "packet_expired",
        ("failed_provenance_invalid", "temporal_authority_invalid",
         "evaluation_time_invalid", "prior_terminal_state",
         "idempotency_reservation_invalid"),
    ),
    (
        "g2a_t16_authorized_revoke", "ROOT_AUTHORIZED", "REVOKED",
        "AUTHORITY_CHANGE", "owning_local_root",
        "NEW_ROOT_REVOCATION_DECISION",
        ("accepted_revocation_binding_valid",
         "source_authorization_binding_valid",
         "idempotency_reservation_owned"),
        "NOT_CONSUMED", "NO_ADAPTER_INVOCATION", True, "packet_revoked",
        ("foreign_root", "accepted_revocation_binding_invalid",
         "source_authorization_mismatch", "idempotency_reservation_invalid"),
    ),
    (
        "g2a_t17_queued_revoke", "QUEUED", "REVOKED",
        "AUTHORITY_CHANGE", "owning_local_root",
        "NEW_ROOT_REVOCATION_DECISION",
        ("accepted_revocation_binding_valid",
         "source_authorization_binding_valid",
         "idempotency_reservation_owned"),
        "NOT_CONSUMED", "NO_ADAPTER_INVOCATION", True, "packet_revoked",
        ("foreign_root", "accepted_revocation_binding_invalid",
         "source_authorization_mismatch", "idempotency_reservation_invalid"),
    ),
    (
        "g2a_t18_pending_revoke", "PENDING_FULFILLMENT", "REVOKED",
        "AUTHORITY_CHANGE", "owning_local_root",
        "NEW_ROOT_REVOCATION_DECISION",
        ("accepted_revocation_binding_valid",
         "source_authorization_binding_valid", "adapter_not_called",
         "idempotency_reservation_owned"),
        "NOT_CONSUMED", "NO_ADAPTER_INVOCATION", True, "packet_revoked",
        ("adapter_already_called", "foreign_root",
         "accepted_revocation_binding_invalid",
         "source_authorization_mismatch", "idempotency_reservation_invalid"),
    ),
    (
        "g2a_t19_failed_revoke", "FAILED", "REVOKED",
        "AUTHORITY_CHANGE", "owning_local_root",
        "NEW_ROOT_REVOCATION_DECISION",
        ("failed_non_consuming_provenance_valid",
         "accepted_revocation_binding_valid",
         "source_authorization_binding_valid",
         "idempotency_reservation_owned"),
        "NOT_CONSUMED", "NO_ADAPTER_INVOCATION", True, "packet_revoked",
        ("failed_provenance_invalid", "foreign_root",
         "accepted_revocation_binding_invalid",
         "source_authorization_mismatch", "idempotency_reservation_invalid"),
    ),
    (
        "g2a_t20_authorized_supersede", "ROOT_AUTHORIZED", "SUPERSEDED",
        "AUTHORITY_CHANGE", "owning_local_root",
        "NEW_ROOT_SUPERSESSION_DECISION",
        ("successor_packet_valid", "accepted_supersession_binding_valid",
         "predecessor_binding_valid", "idempotency_transfer_valid"),
        "NOT_CONSUMED", "NO_ADAPTER_INVOCATION", True,
        "packet_superseded",
        ("successor_packet_missing", "accepted_supersession_binding_invalid",
         "predecessor_binding_mismatch", "foreign_root",
         "idempotency_transfer_invalid"),
    ),
    (
        "g2a_t21_queued_supersede", "QUEUED", "SUPERSEDED",
        "AUTHORITY_CHANGE", "owning_local_root",
        "NEW_ROOT_SUPERSESSION_DECISION",
        ("successor_packet_valid", "accepted_supersession_binding_valid",
         "predecessor_binding_valid", "idempotency_transfer_valid"),
        "NOT_CONSUMED", "NO_ADAPTER_INVOCATION", True,
        "packet_superseded",
        ("successor_packet_missing", "accepted_supersession_binding_invalid",
         "predecessor_binding_mismatch", "foreign_root",
         "idempotency_transfer_invalid"),
    ),
    (
        "g2a_t22_pending_supersede", "PENDING_FULFILLMENT", "SUPERSEDED",
        "AUTHORITY_CHANGE", "owning_local_root",
        "NEW_ROOT_SUPERSESSION_DECISION",
        ("successor_packet_valid", "accepted_supersession_binding_valid",
         "predecessor_binding_valid", "adapter_not_called",
         "idempotency_transfer_valid"),
        "NOT_CONSUMED", "NO_ADAPTER_INVOCATION", True,
        "packet_superseded",
        ("adapter_already_called", "successor_packet_missing",
         "accepted_supersession_binding_invalid",
         "predecessor_binding_mismatch", "foreign_root",
         "idempotency_transfer_invalid"),
    ),
    (
        "g2a_t23_failed_supersede", "FAILED", "SUPERSEDED",
        "AUTHORITY_CHANGE", "owning_local_root",
        "NEW_ROOT_SUPERSESSION_DECISION",
        ("failed_non_consuming_provenance_valid", "successor_packet_valid",
         "accepted_supersession_binding_valid", "predecessor_binding_valid",
         "idempotency_transfer_valid"),
        "NOT_CONSUMED", "NO_ADAPTER_INVOCATION", True,
        "packet_superseded",
        ("failed_provenance_invalid", "successor_packet_missing",
         "accepted_supersession_binding_invalid",
         "predecessor_binding_mismatch", "foreign_root",
         "idempotency_transfer_invalid"),
    ),
    (
        "g2a_t24_nonconsuming_failure", "PENDING_FULFILLMENT", "FAILED",
        "DETERMINISTIC", "exclusive_corridor", "NONE",
        ("adapter_invocation_evidence_valid",
         "effect_nonconsumption_evidence_valid",
         "idempotency_reservation_owned",
         "latest_disposition_event_binding_valid"),
        "NOT_CONSUMED", "CORRIDOR_INVOCATION_NONCONSUMING", False,
        "fulfillment_failed_nonconsuming",
        ("adapter_not_called", "effect_consumed", "effect_outcome_uncertain",
         "failure_evidence_missing", "idempotency_reservation_invalid",
         "latest_disposition_event_binding_invalid",
         "disposition_history_changed"),
    ),
    (
        "g2a_t25_retry", "FAILED", "QUEUED", "DETERMINISTIC",
        "lifecycle_runtime", "NONE",
        ("failed_non_consuming_provenance_valid", "retry_policy_valid",
         "current_eligibility_valid", "idempotency_reservation_owned"),
        "NOT_CONSUMED", "NO_ADAPTER_INVOCATION", False,
        "nonconsuming_retry_queued",
        ("failed_provenance_invalid", "packet_binding_mismatch",
         "idempotency_binding_mismatch", "terminal_evidence_present",
         "mandatory_dependency_invalid", "retry_policy_invalid",
         "idempotency_reservation_invalid"),
    ),
    (
        "g2a_t26_uncertain_adapter_outcome", "PENDING_FULFILLMENT",
        "FAILED", "DETERMINISTIC_UNCERTAIN", "exclusive_corridor", "NONE",
        ("adapter_invocation_evidence_valid", "effect_outcome_unresolved",
         "idempotency_reservation_owned"),
        "UNCERTAIN", "CORRIDOR_INVOCATION_UNCERTAIN", True,
        "fulfillment_failed_consumption_uncertain",
        ("adapter_not_called", "effect_consumed",
         "effect_non_consumption_proven",
         "execution_attempt_evidence_missing", "idempotency_binding_missing",
         "transition_event_identity_invalid"),
    ),
)


@pytest.fixture
def registry() -> transition.TransitionRegistryV01:
    return transition.build_default_transition_registry_v01()


def _lookup(registry, rule, *, guards=None, commit=True):
    return transition.lookup_transition_v01(
        registry=registry,
        abi_major_version=rule.abi_major_version,
        source_artifact_type=rule.source_artifact_type,
        source_lifecycle_state=rule.source_lifecycle_state,
        actor_role=rule.actor_role,
        attempted_effect=rule.attempted_effect,
        target_artifact_type=rule.target_artifact_type,
        satisfied_guards=rule.required_guards if guards is None else guards,
        root_commit_present=commit,
    )


@pytest.mark.parametrize("cls,expected", (
    (transition.TransitionRuleV01, RULE_FIELDS),
    (transition.TransitionDecisionV01, DECISION_FIELDS),
    (transition.TransitionRegistryV01, REGISTRY_FIELDS),
))
def test_public_dataclass_field_order(cls, expected):
    assert tuple(field.name for field in fields(cls)) == expected


@pytest.mark.parametrize("cls", (
    transition.TransitionRuleV01,
    transition.TransitionDecisionV01,
    transition.TransitionRegistryV01,
))
def test_public_dataclasses_are_frozen(cls, registry):
    value = registry if cls is transition.TransitionRegistryV01 else (
        registry.rules[0] if cls is transition.TransitionRuleV01 else _lookup(registry, registry.rules[0])
    )
    with pytest.raises(FrozenInstanceError):
        setattr(value, fields(cls)[0].name, "changed")


def test_exact_public_function_surface():
    observed = tuple(name for name, value in vars(transition).items() if inspect.isfunction(value) and not name.startswith("_"))
    assert observed == (
        *PUBLIC_FUNCTIONS,
        *ACTION_PACKET_PUBLIC_FUNCTIONS,
        *G2C_TRANSITION_FUNCTIONS,
    )


@pytest.mark.parametrize("name", (
    "TransitionRuleV01", "TransitionDecisionV01", "TransitionRegistryV01",
    *PUBLIC_FUNCTIONS,
))
def test_direct_package_attributes(name):
    assert getattr(kernel_package, name) is getattr(transition, name)


def test_package_all_remains_committed_surface():
    assert kernel_package.__all__ == EXPECTED_ALL


@pytest.mark.parametrize("name,expected", (
    ("MODULE_ID", "kernel_transition_registry_v01"),
    ("SLICE_ID", "domain_neutral_reference_kernel_gate1_g1c1"),
    ("TRANSITION_REGISTRY_VERSION", "v0.1"),
))
def test_module_identity(name, expected):
    assert getattr(transition, name) == expected


def test_exact_constant_tuples():
    assert transition.SUPPORTED_ABI_MAJOR_VERSIONS == (1,)
    assert transition.TRANSITION_DECISIONS == ("ALLOW", "BLOCKED_FAIL_CLOSED", "RETURN_TO_ROOT", "NEEDS_USER", "NEEDS_MORE_EVIDENCE")
    assert transition.TRANSITION_ATTEMPTED_EFFECTS == ("CREATE_TARGET_ARTIFACT", "CREATE_ROOT_DECISION", "CREATE_PERMISSION", "CREATE_FINAL_OUTPUT", "REQUEST_EFFECT", "RECORD_EVIDENCE", "RETURN_TO_ROOT")
    assert len(transition.TRANSITION_GUARD_IDS) == 13


def test_registry_geometry(registry):
    assert len(registry.rules) == 18
    assert sum(rule.decision == transition.DECISION_ALLOW for rule in registry.rules) == 8
    assert sum(rule.decision == transition.DECISION_RETURN_TO_ROOT for rule in registry.rules) == 4
    assert sum(rule.decision == transition.DECISION_BLOCKED_FAIL_CLOSED for rule in registry.rules) == 6
    assert transition.validate_transition_registry_v01(registry) == ()


@pytest.mark.parametrize("index", range(18))
def test_every_rule_valid(index, registry):
    assert transition.validate_transition_rule_v01(registry.rules[index]) == ()


@pytest.mark.parametrize("index", range(18))
def test_every_rule_uses_abi_vocabulary(index, registry):
    rule = registry.rules[index]
    assert rule.source_artifact_type in ARTIFACT_TYPES
    assert rule.target_artifact_type in ARTIFACT_TYPES
    assert rule.source_lifecycle_state in LIFECYCLE_STATES
    assert rule.attempted_effect in transition.TRANSITION_ATTEMPTED_EFFECTS
    assert set(rule.required_guards) <= set(transition.TRANSITION_GUARD_IDS)


@pytest.mark.parametrize("index", range(18))
def test_every_canonical_lookup_matches_rule(index, registry):
    rule = registry.rules[index]
    decision = _lookup(registry, rule)
    assert decision.matched is True
    assert decision.rule_id == rule.rule_id
    assert decision.decision == rule.decision
    assert decision.reason_code == rule.reason_code
    assert decision.required_guards == rule.required_guards
    assert decision.missing_guards == ()
    assert transition.validate_transition_decision_v01(registry=registry, decision=decision) == ()


@pytest.mark.parametrize("index", range(18))
def test_every_lookup_identity_is_deterministic(index, registry):
    first = _lookup(registry, registry.rules[index])
    second = _lookup(registry, registry.rules[index])
    assert first == second
    assert first.decision_id == second.decision_id


@pytest.mark.parametrize("index", range(18))
def test_missing_each_rule_rejected(index, registry):
    mutated = replace(registry, rules=registry.rules[:index] + registry.rules[index + 1:])
    assert "transition_rule_set_mismatch" in transition.validate_transition_registry_v01(mutated)


@pytest.mark.parametrize("index", range(17))
def test_each_adjacent_reorder_rejected(index, registry):
    rules = list(registry.rules)
    rules[index], rules[index + 1] = rules[index + 1], rules[index]
    mutated = replace(registry, rules=tuple(rules))
    assert "transition_rule_order_mismatch" in transition.validate_transition_registry_v01(mutated)


@pytest.mark.parametrize("field,value", (
    ("rule_id", "changed"), ("abi_major_version", 2),
    ("source_artifact_type", "unknown"), ("source_lifecycle_state", "unknown"),
    ("actor_role", "unknown"), ("attempted_effect", "unknown"),
    ("target_artifact_type", "unknown"), ("required_guards", ("artifact_valid", "unknown")),
    ("decision", "unknown"), ("reason_code", "unknown"),
    ("root_commit_required", 1),
))
def test_every_rule_field_mutation_rejected(field, value, registry):
    rule = replace(registry.rules[0], **{field: value})
    assert transition.validate_transition_rule_v01(rule)


@pytest.mark.parametrize("field,value", (
    ("registry_id", "0" * 64), ("registry_version", "v9"),
    ("abi_major_version", 2), ("rules", list()),
))
def test_registry_top_level_mutations_rejected(field, value, registry):
    assert transition.validate_transition_registry_v01(replace(registry, **{field: value}))


def test_duplicate_rule_id_and_lookup_key_rejected(registry):
    duplicate_id = replace(registry.rules[1], rule_id=registry.rules[0].rule_id)
    errors = transition.validate_transition_registry_v01(replace(registry, rules=(registry.rules[0], duplicate_id) + registry.rules[2:]))
    assert "transition_rule_id_duplicate" in errors
    duplicate_key = replace(registry.rules[1], rule_id="different", source_artifact_type=registry.rules[0].source_artifact_type, source_lifecycle_state=registry.rules[0].source_lifecycle_state, actor_role=registry.rules[0].actor_role, attempted_effect=registry.rules[0].attempted_effect, target_artifact_type=registry.rules[0].target_artifact_type)
    errors = transition.validate_transition_registry_v01(replace(registry, rules=(registry.rules[0], duplicate_key) + registry.rules[2:]))
    assert "transition_lookup_key_duplicate" in errors


@pytest.mark.parametrize("rule_id,special_guard,expected,reason", (
    ("root_decision_to_execution_request", "user_permission_present", "NEEDS_USER", "explicit_user_permission_required"),
    ("actor_contribution_to_validated_evidence", "required_evidence_present", "NEEDS_MORE_EVIDENCE", "required_evidence_missing"),
    ("result_proposal_to_post_vv_report", "hard_predicates_evaluated", "BLOCKED_FAIL_CLOSED", "required_guard_missing"),
))
def test_missing_guard_precedence(rule_id, special_guard, expected, reason, registry):
    rule = next(item for item in registry.rules if item.rule_id == rule_id)
    decision = _lookup(registry, rule, guards=tuple(item for item in rule.required_guards if item != special_guard))
    assert (decision.decision, decision.reason_code) == (expected, reason)


def test_generic_missing_precedes_special_missing(registry):
    rule = next(item for item in registry.rules if item.rule_id == "root_decision_to_execution_request")
    decision = _lookup(registry, rule, guards=("artifact_valid", "decision_accept"))
    assert (decision.decision, decision.reason_code) == ("BLOCKED_FAIL_CLOSED", "required_guard_missing")


def test_missing_root_commit_returns_to_root(registry):
    rule = next(item for item in registry.rules if item.rule_id == "root_accepted_route_to_runtime_topology")
    decision = _lookup(registry, rule, commit=False)
    assert (decision.decision, decision.reason_code) == ("RETURN_TO_ROOT", "root_commit_required")


@pytest.mark.parametrize("field,value", (
    ("source_artifact_type", "UnknownArtifact"),
    ("source_lifecycle_state", "UNKNOWN_STATE"),
    ("actor_role", "unknown_actor"), ("attempted_effect", "UNKNOWN_EFFECT"),
    ("target_artifact_type", "UnknownTarget"),
))
def test_unknown_exact_lookup_blocks(field, value, registry):
    rule = registry.rules[0]
    kwargs = dict(abi_major_version=1, source_artifact_type=rule.source_artifact_type, source_lifecycle_state=rule.source_lifecycle_state, actor_role=rule.actor_role, attempted_effect=rule.attempted_effect, target_artifact_type=rule.target_artifact_type, satisfied_guards=(), root_commit_present=False)
    kwargs[field] = value
    decision = transition.lookup_transition_v01(registry=registry, **kwargs)
    assert (decision.matched, decision.decision, decision.reason_code) == (False, "BLOCKED_FAIL_CLOSED", "unknown_transition")


def test_unknown_major_blocks(registry):
    rule = registry.rules[0]
    decision = transition.lookup_transition_v01(registry=registry, abi_major_version=2, source_artifact_type=rule.source_artifact_type, source_lifecycle_state=rule.source_lifecycle_state, actor_role=rule.actor_role, attempted_effect=rule.attempted_effect, target_artifact_type=rule.target_artifact_type, satisfied_guards=(), root_commit_present=False)
    assert (decision.matched, decision.reason_code) == (False, "unknown_abi_major")


@pytest.mark.parametrize("field,value", (
    ("abi_major_version", True), ("source_artifact_type", ""),
    ("source_lifecycle_state", 1), ("actor_role", ""),
    ("attempted_effect", object()), ("target_artifact_type", ""),
    ("satisfied_guards", []), ("satisfied_guards", ("artifact_valid", "artifact_valid")),
    ("satisfied_guards", ("unknown",)), ("root_commit_present", 1),
))
def test_malformed_lookup_raises_stable(field, value, registry):
    rule = registry.rules[0]
    kwargs = dict(abi_major_version=1, source_artifact_type=rule.source_artifact_type, source_lifecycle_state=rule.source_lifecycle_state, actor_role=rule.actor_role, attempted_effect=rule.attempted_effect, target_artifact_type=rule.target_artifact_type, satisfied_guards=(), root_commit_present=False)
    kwargs[field] = value
    with pytest.raises(ValueError, match="^transition_lookup_invalid$") as caught:
        transition.lookup_transition_v01(registry=registry, **kwargs)
    assert caught.value.__cause__ is None


@pytest.mark.parametrize("rule_id", (
    "provider_contribution_to_root_decision_forbidden",
    "drs_evidence_to_permission_forbidden",
    "gt_advisory_to_root_final_forbidden",
    "receipt_to_permission_forbidden",
    "causal_evidence_to_root_decision_forbidden",
    "domain_adapter_effect_request_forbidden",
))
def test_authority_attack_rules_fail_closed(rule_id, registry):
    rule = next(item for item in registry.rules if item.rule_id == rule_id)
    result = _lookup(registry, rule)
    assert result.decision == transition.DECISION_BLOCKED_FAIL_CLOSED
    assert result.matched is True


def test_registry_and_projection_determinism(registry):
    other = transition.build_default_transition_registry_v01()
    assert registry is not other
    assert registry.rules is not other.rules
    assert registry.registry_id == other.registry_id
    assert transition.transition_registry_to_plain_dict_v01(registry) == transition.transition_registry_to_plain_dict_v01(other)


@pytest.mark.parametrize("kind", ("rule", "decision", "registry"))
def test_projections_are_json_safe_and_independent(kind, registry):
    if kind == "rule":
        source, project = registry.rules[0], transition.transition_rule_to_plain_dict_v01
    elif kind == "decision":
        source, project = _lookup(registry, registry.rules[0]), transition.transition_decision_to_plain_dict_v01
    else:
        source, project = registry, transition.transition_registry_to_plain_dict_v01
    first, second = project(source), project(source)
    json.dumps(first, allow_nan=False)
    assert first == second
    first[next(iter(first))] = "changed"
    assert project(source) == second


def test_no_tuple_remains_in_registry_projection(registry):
    def walk(value):
        assert type(value) is not tuple
        if isinstance(value, dict):
            for item in value.values(): walk(item)
        elif isinstance(value, list):
            for item in value: walk(item)
    walk(transition.transition_registry_to_plain_dict_v01(registry))


@pytest.mark.parametrize("kind", ("rule", "decision", "registry"))
def test_malformed_exact_projection_rejected(kind, registry):
    if kind == "rule":
        value = replace(registry.rules[0], decision="REJECT")
        fn, reason = transition.transition_rule_to_plain_dict_v01, "transition_rule_invalid"
    elif kind == "decision":
        value = replace(_lookup(registry, registry.rules[0]), reason_code="unknown_transition")
        fn, reason = transition.transition_decision_to_plain_dict_v01, "transition_decision_invalid"
    else:
        value = replace(registry, registry_id="0" * 64)
        fn, reason = transition.transition_registry_to_plain_dict_v01, "transition_registry_invalid"
    with pytest.raises(ValueError, match=f"^{reason}$"):
        fn(value)


class _ExplosiveStr(str):
    def __eq__(self, other):
        raise OSError("CALLER_SECRET")
    def __hash__(self):
        raise OSError("CALLER_SECRET")


@pytest.mark.parametrize("value", (object(), _ExplosiveStr("root")))
def test_hostile_lookup_is_sanitized(value, registry):
    rule = registry.rules[0]
    with pytest.raises(ValueError) as caught:
        transition.lookup_transition_v01(registry=registry, abi_major_version=1, source_artifact_type=rule.source_artifact_type, source_lifecycle_state=rule.source_lifecycle_state, actor_role=value, attempted_effect=rule.attempted_effect, target_artifact_type=rule.target_artifact_type, satisfied_guards=(), root_commit_present=False)
    assert str(caught.value) == "transition_lookup_invalid"
    assert "CALLER_SECRET" not in str(caught.value)


def test_base_exception_not_swallowed(monkeypatch, registry):
    monkeypatch.setattr(transition, "_registry_errors", lambda value: (_ for _ in ()).throw(KeyboardInterrupt()))
    with pytest.raises(KeyboardInterrupt):
        transition.lookup_transition_v01(registry=registry, abi_major_version=1, source_artifact_type="x", source_lifecycle_state="x", actor_role="x", attempted_effect="x", target_artifact_type="x", satisfied_guards=(), root_commit_present=False)


@pytest.mark.parametrize("token", (
    "hedgehog.domains", "import demo", "import tests", "requests", "socket",
    "urllib", "pathlib", "subprocess", "open(", "getenv", "register_rule",
    "add_rule", "remove_rule", "update_rule", "callback", "effect_hook",
))
def test_static_forbidden_tokens_absent(token):
    assert token not in MODULE_PATH.read_text(encoding="utf-8")


def test_static_import_boundary():
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    imports = {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    assert imports <= {"__future__", "dataclasses", "hedgehog.kernel.abi_v01", "hedgehog.kernel.integrity_replay_v01"}


def test_legacy_transition_registry_vector_is_byte_stable() -> None:
    legacy = transition.build_default_transition_registry_v01()
    assert legacy.registry_id == LEGACY_REGISTRY_ID
    assert legacy.registry_version == "v0.1"
    assert legacy.abi_major_version == 1
    assert len(legacy.rules) == 18
    assert tuple(rule.rule_id for rule in legacy.rules) == LEGACY_RULE_IDS
    assert tuple(field.name for field in fields(transition.TransitionRuleV01)) == (
        "rule_id", "abi_major_version", "source_artifact_type",
        "source_lifecycle_state", "actor_role", "attempted_effect",
        "target_artifact_type", "required_guards", "decision",
        "reason_code", "root_commit_required",
    )
    assert tuple(
        field.name for field in fields(transition.TransitionDecisionV01)
    ) == DECISION_FIELDS
    assert tuple(
        field.name for field in fields(transition.TransitionRegistryV01)
    ) == REGISTRY_FIELDS
    plain_bytes = canonical_json_bytes_v01(
        transition.transition_registry_to_plain_dict_v01(legacy)
    )
    assert len(plain_bytes) == 7613
    assert hashlib.sha256(plain_bytes).hexdigest() == (
        "baa8a3d1e1bac9b16b316d57bfbdbb0d79333a30dd662cc3e03d1558afd08c3c"
    )


def test_action_packet_registry_exact_26_rule_profile() -> None:
    profile = transition.build_action_packet_transition_registry_profile_v01()
    assert tuple(
        field.name
        for field in fields(transition.ActionPacketTransitionRuleV01)
    ) == ACTION_PACKET_RULE_FIELDS
    assert tuple(
        field.name
        for field in fields(
            transition.ActionPacketTransitionRegistryProfileV01
        )
    ) == ACTION_PACKET_REGISTRY_FIELDS
    assert profile.transition_registry_id == ACTION_PACKET_REGISTRY_ID
    assert profile.registry_profile_version == "v0.1"
    assert (
        profile.lifecycle_profile_id
        == "action_packet_lifecycle_profile_v01"
    )
    assert len(profile.ordered_transition_rules) == 26
    assert transition.validate_action_packet_transition_registry_profile_v01(
        profile
    ) == ()
    observed = tuple(
        tuple(getattr(rule, name) for name in ACTION_PACKET_RULE_FIELDS)
        for rule in profile.ordered_transition_rules
    )
    assert observed == ACTION_PACKET_EXPECTED_ROWS
    assert tuple(
        name
        for name, _ in transition.action_packet_transition_rule_material_v01(
            profile.ordered_transition_rules[0]
        )
    ) == ACTION_PACKET_RULE_FIELDS
    material = transition.action_packet_transition_registry_material_v01(
        profile
    )
    assert tuple(name for name, _ in material) == (
        "registry_profile_version",
        "lifecycle_profile_id",
        "ordered_transition_rules",
    )
    expected_digest = domain_separated_sha256_hex_v01(
        domain="HEDGEHOG_ACTION_PACKET_TRANSITION_REGISTRY_V01",
        payload=canonical_json_bytes_v01(material),
    )
    assert profile.transition_registry_id == "acptr_v01:" + expected_digest


def test_action_packet_registry_exact_closed_vocabularies() -> None:
    assert transition.ACTION_PACKET_TRANSITION_CLASS_CODES_V01 == (
        "LIFECYCLE_ACTIVATION",
        "DETERMINISTIC",
        "DETERMINISTIC_CONSUMING",
        "AUTHORITY_CHANGE",
        "DETERMINISTIC_UNCERTAIN",
    )
    assert transition.ACTION_PACKET_ADAPTER_INVOCATION_RELATION_CODES_V01 == (
        "NO_ADAPTER_INVOCATION",
        "CORRIDOR_INVOCATION_CONSUMED",
        "CORRIDOR_INVOCATION_NONCONSUMING",
        "CORRIDOR_INVOCATION_UNCERTAIN",
        "POST_INVOCATION_RECEIPT_OBSERVATION",
    )
    profile = transition.build_action_packet_transition_registry_profile_v01()
    relations = {
        rule.transition_rule_id: rule.adapter_invocation_relation_code
        for rule in profile.ordered_transition_rules
    }
    assert relations["g2a_t04_fulfill_mock"] == (
        "CORRIDOR_INVOCATION_CONSUMED"
    )
    assert relations["g2a_t24_nonconsuming_failure"] == (
        "CORRIDOR_INVOCATION_NONCONSUMING"
    )
    assert relations["g2a_t26_uncertain_adapter_outcome"] == (
        "CORRIDOR_INVOCATION_UNCERTAIN"
    )
    assert relations["g2a_t05_receipt"] == (
        "POST_INVOCATION_RECEIPT_OBSERVATION"
    )
    assert all(
        relation == "NO_ADAPTER_INVOCATION"
        for rule_id, relation in relations.items()
        if rule_id not in {
            "g2a_t04_fulfill_mock",
            "g2a_t24_nonconsuming_failure",
            "g2a_t26_uncertain_adapter_outcome",
            "g2a_t05_receipt",
        }
    )
    assert "adapter_call_allowed" not in ACTION_PACKET_RULE_FIELDS


@pytest.mark.parametrize(
    ("field_name", "value"),
    (
        ("transition_rule_id", "unknown_rule"),
        (
            "transition_rule_id",
            _ExplosiveStr("g2a_t01_activate_root_authorization"),
        ),
        ("source_state", "PROPOSED"),
        ("target_state", "UNKNOWN"),
        ("transition_class_code", "UNKNOWN"),
        ("permitted_component_code", "unknown_component"),
        ("root_decision_requirement_code", "UNKNOWN"),
        ("required_evidence_codes", ["packet_genesis_valid"]),
        (
            "required_evidence_codes",
            ("packet_genesis_valid", "packet_genesis_valid"),
        ),
        ("required_evidence_codes", ("unknown_evidence",)),
        ("effect_consumption_class", "UNKNOWN"),
        ("adapter_invocation_relation_code", "UNKNOWN"),
        ("terminal_target", 1),
        ("reason_code", "unknown_reason"),
        ("reason_code", "free prose."),
        ("fail_closed_reason_codes", ["packet_genesis_invalid"]),
        (
            "fail_closed_reason_codes",
            ("packet_genesis_invalid", "packet_genesis_invalid"),
        ),
        ("fail_closed_reason_codes", ("unknown_fail",)),
    ),
)
def test_action_packet_rule_mutations_fail_closed(
    field_name: str,
    value: object,
) -> None:
    profile = transition.build_action_packet_transition_registry_profile_v01()
    rule = replace(
        profile.ordered_transition_rules[0],
        **{field_name: value},
    )
    assert transition.validate_action_packet_transition_rule_v01(rule)


def test_action_packet_registry_rule_table_mutations_fail_closed() -> None:
    profile = transition.build_action_packet_transition_registry_profile_v01()
    rules = profile.ordered_transition_rules
    mutations = (
        replace(profile, ordered_transition_rules=rules[:-1]),
        replace(profile, ordered_transition_rules=(*rules, rules[0])),
        replace(
            profile,
            ordered_transition_rules=(rules[0], rules[0], *rules[2:]),
        ),
        replace(
            profile,
            ordered_transition_rules=(rules[1], rules[0], *rules[2:]),
        ),
        replace(
            profile,
            transition_registry_id="acptr_v01:" + "0" * 64,
        ),
        replace(profile, lifecycle_profile_id="changed"),
        replace(profile, ordered_transition_rules=list(rules)),
    )
    for mutation in mutations:
        assert (
            transition.validate_action_packet_transition_registry_profile_v01(
                mutation
            )
        )


def test_action_packet_registry_mutation_changes_independent_identity() -> None:
    profile = transition.build_action_packet_transition_registry_profile_v01()
    material = transition.action_packet_transition_registry_material_v01(
        profile
    )
    rules = list(material[2][1])
    first = list(rules[0])
    evidence = list(first[6][1])
    evidence[0] = "blocking_evidence_valid"
    first[6] = ("required_evidence_codes", tuple(evidence))
    rules[0] = tuple(first)
    evidence_changed = (
        material[0],
        material[1],
        ("ordered_transition_rules", tuple(rules)),
    )

    fail_rules = list(material[2][1])
    fail_first = list(fail_rules[0])
    fail_codes = list(fail_first[11][1])
    fail_codes[0] = "packet_non_executable"
    fail_first[11] = ("fail_closed_reason_codes", tuple(fail_codes))
    fail_rules[0] = tuple(fail_first)
    fail_changed = (
        material[0],
        material[1],
        ("ordered_transition_rules", tuple(fail_rules)),
    )

    reordered_rules = list(material[2][1])
    reordered_rules[0], reordered_rules[1] = (
        reordered_rules[1],
        reordered_rules[0],
    )
    order_changed = (
        material[0],
        material[1],
        ("ordered_transition_rules", tuple(reordered_rules)),
    )
    for changed_material in (
        evidence_changed,
        fail_changed,
        order_changed,
    ):
        changed_id = "acptr_v01:" + domain_separated_sha256_hex_v01(
            domain="HEDGEHOG_ACTION_PACKET_TRANSITION_REGISTRY_V01",
            payload=canonical_json_bytes_v01(changed_material),
        )
        assert changed_id != profile.transition_registry_id


def test_action_packet_registry_lookup_is_exact_and_fail_closed() -> None:
    profile = transition.build_action_packet_transition_registry_profile_v01()
    for expected in profile.ordered_transition_rules:
        assert transition.lookup_action_packet_transition_rule_v01(
            registry=profile,
            transition_rule_id=expected.transition_rule_id,
        ) is expected
    for value in ("unknown", None, _ExplosiveStr("g2a_t02_queue")):
        with pytest.raises(ValueError, match="^unknown_transition$"):
            transition.lookup_action_packet_transition_rule_v01(
                registry=profile,
                transition_rule_id=value,
            )


def test_external_explanation_prose_does_not_change_registry_identity() -> None:
    profile = transition.build_action_packet_transition_registry_profile_v01()
    explanations = {
        "g2a_t01_activate_root_authorization": "Activate: reviewed, only.",
    }
    explanations["g2a_t01_activate_root_authorization"] = (
        "Different punctuation and prose!"
    )
    assert (
        transition.build_action_packet_transition_registry_profile_v01()
        .transition_registry_id
        == profile.transition_registry_id
    )


def test_action_packet_registry_validators_are_total() -> None:
    profile = transition.build_action_packet_transition_registry_profile_v01()
    values = (
        None,
        object(),
        replace(
            profile,
            transition_registry_id=_ExplosiveStr(
                profile.transition_registry_id
            ),
        ),
    )
    for value in values:
        assert (
            transition.validate_action_packet_transition_registry_profile_v01(
                value
            )
        )
    for value in (None, object(), _ExplosiveStr("g2a_t01_activate_root_authorization")):
        assert transition.validate_action_packet_transition_rule_v01(value)


G2C_TRANSITION_FUNCTIONS = (
    "build_execution_mode_transition_registry_profile_v01",
    "validate_execution_mode_transition_registry_profile_v01",
    "execution_mode_transition_registry_profile_to_plain_dict_v01",
    "validate_execution_mode_transition_decision_v01",
    "execution_mode_transition_decision_to_plain_dict_v01",
    "rebuild_execution_mode_transition_decision_identity_v01",
)
G2C_TRANSITION_SIGNATURES = {
    "build_execution_mode_transition_registry_profile_v01": (
        "() -> 'TransitionRegistryV01'"
    ),
    "validate_execution_mode_transition_registry_profile_v01": (
        "(registry: 'object') -> 'tuple[str, ...]'"
    ),
    "execution_mode_transition_registry_profile_to_plain_dict_v01": (
        "(registry: 'TransitionRegistryV01') -> 'dict[str, object]'"
    ),
    "validate_execution_mode_transition_decision_v01": (
        "(*, registry: 'TransitionRegistryV01', decision: 'object') -> "
        "'tuple[str, ...]'"
    ),
    "execution_mode_transition_decision_to_plain_dict_v01": (
        "(*, registry: 'TransitionRegistryV01', decision: "
        "'TransitionDecisionV01') -> 'dict[str, object]'"
    ),
    "rebuild_execution_mode_transition_decision_identity_v01": (
        "(decision: 'TransitionDecisionV01') -> 'str'"
    ),
}
G2C_TRANSITION_ROWS = (
    (
        "g2c_transition:proposal_to_root_review:v01",
        "ExecutionModeProposal",
        "VALIDATED",
        "execution_mode_router",
        "ENTER_ROOT_REVIEW",
        "RootExecutionModeDecision",
        ("proposal_sources_valid", "proposal_artifact_valid", "target_root_bound"),
        "RETURN_TO_ROOT",
        "g2c_transition_root_review_required",
        False,
    ),
    (
        "g2c_transition:root_accept_to_route:v01",
        "RootExecutionModeDecision",
        "ROOT_ACCEPTED",
        "root",
        "ACCEPT_ROUTE",
        "ExecutionModeRouteEligibility",
        (
            "root_result_valid",
            "accepted_mode_valid",
            "accepted_scope_valid",
            "consumption_class_valid",
        ),
        "ALLOW",
        "g2c_transition_route_accept_allowed",
        True,
    ),
    (
        "g2c_transition:root_narrow_to_route:v01",
        "RootExecutionModeDecision",
        "ROOT_ACCEPTED",
        "root",
        "NARROW_SCOPE",
        "ExecutionModeRouteEligibility",
        (
            "root_result_valid",
            "accepted_mode_valid",
            "narrowing_proof_valid",
            "consumption_class_valid",
        ),
        "ALLOW",
        "g2c_transition_scope_narrow_allowed",
        True,
    ),
    (
        "g2c_transition:root_reject_record:v01",
        "RootExecutionModeDecision",
        "ROOT_REJECTED",
        "root",
        "REJECT_ROUTE",
        "RootExecutionModeDecision",
        ("root_result_valid", "terminal_consumption_forbidden"),
        "RETURN_TO_ROOT",
        "g2c_transition_reject_recorded",
        True,
    ),
    (
        "g2c_transition:root_block_record:v01",
        "RootExecutionModeDecision",
        "BLOCKED_FAIL_CLOSED",
        "root",
        "BLOCK_ROUTE",
        "RootExecutionModeDecision",
        ("root_result_valid", "terminal_consumption_forbidden"),
        "BLOCKED_FAIL_CLOSED",
        "g2c_transition_blocked_recorded",
        True,
    ),
    (
        "g2c_transition:root_needs_user_record:v01",
        "RootExecutionModeDecision",
        "ROOT_REVIEWED",
        "root",
        "REQUEST_USER_INPUT",
        "RootExecutionModeDecision",
        ("root_result_valid", "terminal_consumption_forbidden"),
        "NEEDS_USER",
        "g2c_transition_needs_user_recorded",
        True,
    ),
)


def _g2c_decision(
    rule: transition.TransitionRuleV01,
    registry: transition.TransitionRegistryV01,
) -> transition.TransitionDecisionV01:
    provisional = transition.TransitionDecisionV01(
        decision_id="0" * 64,
        registry_id=registry.registry_id,
        rule_id=rule.rule_id,
        abi_major_version=rule.abi_major_version,
        source_artifact_type=rule.source_artifact_type,
        source_lifecycle_state=rule.source_lifecycle_state,
        actor_role=rule.actor_role,
        attempted_effect=rule.attempted_effect,
        target_artifact_type=rule.target_artifact_type,
        required_guards=rule.required_guards,
        satisfied_guards=rule.required_guards,
        missing_guards=(),
        decision=rule.decision,
        reason_code=rule.reason_code,
        root_commit_required=rule.root_commit_required,
        root_commit_present=rule.root_commit_required,
        matched=True,
    )
    return replace(
        provisional,
        decision_id=transition.rebuild_execution_mode_transition_decision_identity_v01(
            provisional
        ),
    )


def test_g2c4_transition_public_surface_and_exact_six_rule_profile() -> None:
    for name in G2C_TRANSITION_FUNCTIONS:
        assert inspect.isfunction(getattr(transition, name))
        assert str(inspect.signature(getattr(transition, name))) == (
            G2C_TRANSITION_SIGNATURES[name]
        )
        assert getattr(kernel_package, name) is getattr(transition, name)
        assert name not in kernel_package.__all__

    registry = transition.build_execution_mode_transition_registry_profile_v01()
    assert registry.registry_version == "v0.1"
    assert registry.abi_major_version == 1
    assert len(registry.rules) == 6
    assert tuple(
        (
            rule.rule_id,
            rule.source_artifact_type,
            rule.source_lifecycle_state,
            rule.actor_role,
            rule.attempted_effect,
            rule.target_artifact_type,
            rule.required_guards,
            rule.decision,
            rule.reason_code,
            rule.root_commit_required,
        )
        for rule in registry.rules
    ) == G2C_TRANSITION_ROWS
    assert transition.validate_execution_mode_transition_registry_profile_v01(
        registry
    ) == ()
    plain = transition.execution_mode_transition_registry_profile_to_plain_dict_v01(
        registry
    )
    assert list(plain) == [
        "registry_id",
        "registry_version",
        "abi_major_version",
        "rules",
    ]
    assert canonical_json_bytes_v01(plain) == canonical_json_bytes_v01(
        transition.execution_mode_transition_registry_profile_to_plain_dict_v01(
            transition.build_execution_mode_transition_registry_profile_v01()
        )
    )
    assert registry.registry_id == (
        "a44c497efb934d85d08b1ca097bdae8c4fa07806906e95176d232b1341572376"
    )


def test_g2c4_default_registry_is_byte_identical_after_profile_build() -> None:
    before = transition.build_default_transition_registry_v01()
    before_plain = transition.transition_registry_to_plain_dict_v01(before)
    transition.build_execution_mode_transition_registry_profile_v01()
    after = transition.build_default_transition_registry_v01()
    assert after.registry_id == LEGACY_REGISTRY_ID
    assert tuple(rule.rule_id for rule in after.rules) == LEGACY_RULE_IDS
    assert canonical_json_bytes_v01(before_plain) == canonical_json_bytes_v01(
        transition.transition_registry_to_plain_dict_v01(after)
    )


@pytest.mark.parametrize("rule_index", range(6))
def test_g2c4_profile_decision_identity_and_exact_rule_law(rule_index: int) -> None:
    registry = transition.build_execution_mode_transition_registry_profile_v01()
    decision = _g2c_decision(registry.rules[rule_index], registry)
    assert re.fullmatch(r"[0-9a-f]{64}", decision.decision_id)
    assert transition.validate_execution_mode_transition_decision_v01(
        registry=registry, decision=decision
    ) == ()
    assert transition.rebuild_execution_mode_transition_decision_identity_v01(
        decision
    ) == decision.decision_id
    plain = transition.execution_mode_transition_decision_to_plain_dict_v01(
        registry=registry, decision=decision
    )
    assert tuple(plain) == DECISION_FIELDS
    assert plain["required_guards"] == list(decision.required_guards)
    assert plain["satisfied_guards"] == list(decision.required_guards)
    assert plain["missing_guards"] == []


def test_g2c4_profile_and_decision_mutations_fail_closed() -> None:
    registry = transition.build_execution_mode_transition_registry_profile_v01()
    profile_mutations = (
        None,
        replace(registry, registry_id="0" * 64),
        replace(registry, rules=registry.rules[::-1]),
        replace(registry, rules=registry.rules[:-1]),
        replace(registry, registry_version="v9.9"),
    )
    for mutation in profile_mutations:
        assert transition.validate_execution_mode_transition_registry_profile_v01(
            mutation
        )

    decision = _g2c_decision(registry.rules[1], registry)
    mutations = (
        replace(decision, registry_id="0" * 64),
        replace(decision, rule_id=registry.rules[2].rule_id),
        replace(decision, satisfied_guards=decision.satisfied_guards[::-1]),
        replace(decision, missing_guards=(decision.required_guards[0],)),
        replace(decision, decision="RETURN_TO_ROOT"),
        replace(decision, reason_code="g2c_transition_reject_recorded"),
        replace(decision, root_commit_present=False),
        replace(decision, decision_id="0" * 64),
    )
    for mutation in mutations:
        assert transition.validate_execution_mode_transition_decision_v01(
            registry=registry, decision=mutation
        )
