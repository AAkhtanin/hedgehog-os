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
from hedgehog.kernel.abi_v01 import (
    ARTIFACT_TYPES,
    LIFECYCLE_STATES,
    build_kernel_artifact_v01,
    kernel_artifact_to_plain_dict_v01,
)
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
        *G2D2_TRANSITION_FUNCTIONS,
        *G2E_TRANSITION_FUNCTIONS,
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
    assert transition.TRANSITION_ATTEMPTED_EFFECTS == (
        "CREATE_TARGET_ARTIFACT",
        "CREATE_ROOT_DECISION",
        "CREATE_PERMISSION",
        "CREATE_FINAL_OUTPUT",
        "REQUEST_EFFECT",
        "RECORD_EVIDENCE",
        "RETURN_TO_ROOT",
        "VALIDATE_DELTA_SOURCE",
        "DERIVE_AFFECTED_SET",
        "DERIVE_INVALIDATION",
        "ACCEPT_RECOMPUTATION_PLAN",
        "REJECT_RECOMPUTATION_PLAN",
        "EXECUTE_SELECTIVE_RECOMPUTATION",
        "BLOCK_SELECTIVE_RECOMPUTATION",
        "FINALIZE_CONTINUOUS_DELTA_REPORT",
    )
    assert len(transition.TRANSITION_GUARD_IDS) == 59


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


G2D2_TRANSITION_FUNCTIONS = (
    "build_fractal_runtime_transition_registry_profile_v02",
    "validate_fractal_runtime_transition_registry_profile_v02",
    "fractal_runtime_transition_registry_profile_to_plain_dict_v02",
    "validate_fractal_runtime_transition_decision_v02",
    "fractal_runtime_transition_decision_to_plain_dict_v02",
    "rebuild_fractal_runtime_transition_decision_identity_v02",
)
G2E_TRANSITION_FUNCTIONS = (
    "build_continuous_delta_transition_registry_profile_v01",
    "validate_continuous_delta_transition_registry_profile_v01",
    "continuous_delta_transition_registry_profile_to_plain_dict_v01",
    "validate_continuous_delta_transition_decision_v01",
    "continuous_delta_transition_decision_to_plain_dict_v01",
    "rebuild_continuous_delta_transition_decision_identity_v01",
)
G2D2_TRANSITION_SIGNATURES = {
    "build_fractal_runtime_transition_registry_profile_v02": "() -> 'TransitionRegistryV01'",
    "validate_fractal_runtime_transition_registry_profile_v02": "(value: 'object') -> 'tuple[str, ...]'",
    "fractal_runtime_transition_registry_profile_to_plain_dict_v02": "(value: 'TransitionRegistryV01') -> 'dict[str, object]'",
    "validate_fractal_runtime_transition_decision_v02": "(value: 'object', *, registry: 'TransitionRegistryV01', source_artifact: 'KernelArtifactV01', target_artifact: 'KernelArtifactV01') -> 'tuple[str, ...]'",
    "fractal_runtime_transition_decision_to_plain_dict_v02": "(value: 'TransitionDecisionV01') -> 'dict[str, object]'",
    "rebuild_fractal_runtime_transition_decision_identity_v02": "(value: 'TransitionDecisionV01') -> 'str'",
}
G2D2_RULE_IDS = tuple(
    f"g2d_t{index:02d}_{suffix}"
    for index, suffix in enumerate(
        (
            "route_eligibility_to_topology",
            "topology_to_pending",
            "pending_backpressure_defer",
            "pending_to_ready",
            "ready_to_running",
            "running_to_validating",
            "validating_to_revise",
            "validating_to_completed",
            "validating_to_degraded",
            "validating_to_blocked",
            "validating_to_needs_user",
            "validating_to_deadend",
            "completed_to_parent_return",
            "degraded_to_parent_return",
            "blocked_to_parent_return",
            "needs_user_to_parent_return",
            "deadend_to_parent_return",
        ),
        start=1,
    )
)

G2D2_ARTIFACT_CONTEXT_PROFILES = {
    "ExecutionModeRouteEligibility": (
        "HEDGEHOG_EXECUTION_MODE_ROUTE_ELIGIBILITY_KERNEL_ARTIFACT_V01",
        "emabi_route_v01:", "v0.1", "root_decision_v01", "ROOT_AUTHORIZED",
    ),
    "RuntimeExecutionTopology": (
        "HEDGEHOG_FRACTAL_RUNTIME_TOPOLOGY_KERNEL_ARTIFACT_V02",
        "frabi_topology_v02:", "v0.2", "fractal_runtime_v02", "ADVISORY",
    ),
    "FractalCellQueueEntry": (
        "HEDGEHOG_FRACTAL_CELL_QUEUE_ENTRY_KERNEL_ARTIFACT_V02",
        "frabi_queue_v02:", "v0.2", "fractal_scheduler_v02", "ADVISORY",
    ),
    "FractalCellResult": (
        "HEDGEHOG_FRACTAL_CELL_RESULT_KERNEL_ARTIFACT_V02",
        "frabi_result_v02:", "v0.2", "fractal_runtime_v02", "ADVISORY",
    ),
    "FractalRuntimeReport": (
        "HEDGEHOG_FRACTAL_RUNTIME_REPORT_KERNEL_ARTIFACT_V02",
        "frabi_report_v02:", "v0.2", "fractal_runtime_v02", "ADVISORY",
    ),
}

G2D2_TARGET_LIFECYCLES = (
    "VALIDATED", "VALIDATED", "VALIDATED", "VALIDATED", "VALIDATED",
    "VALIDATED", "VALIDATED", "VALIDATED", "VALIDATED", "VALIDATED",
    "VALIDATED", "VALIDATED", "VALIDATED", "VALIDATED",
    "BLOCKED_FAIL_CLOSED", "VALIDATED", "VALIDATED",
)

G2D2_SOURCE_PARENT_PROFILE_ROWS = (
    ("g2d_t01_route_eligibility_to_topology", "ROUTE_ELIGIBILITY_SOURCE"),
    ("g2d_t02_topology_to_pending", "TOPOLOGY_SOURCE"),
    ("g2d_t03_pending_backpressure_defer", "PENDING_QUEUE_SOURCE"),
    ("g2d_t04_pending_to_ready", "PENDING_QUEUE_SOURCE"),
    ("g2d_t05_ready_to_running", "TWO_PARENT_QUEUE_SOURCE"),
    ("g2d_t06_running_to_validating", "TWO_PARENT_QUEUE_SOURCE"),
    ("g2d_t07_validating_to_revise", "TWO_PARENT_QUEUE_SOURCE"),
    ("g2d_t08_validating_to_completed", "TERMINAL_QUEUE_SOURCE"),
    ("g2d_t09_validating_to_degraded", "TERMINAL_QUEUE_SOURCE"),
    ("g2d_t10_validating_to_blocked", "TERMINAL_QUEUE_SOURCE"),
    ("g2d_t11_validating_to_needs_user", "TERMINAL_QUEUE_SOURCE"),
    ("g2d_t12_validating_to_deadend", "TERMINAL_QUEUE_SOURCE"),
    ("g2d_t13_completed_to_parent_return", "CELL_RESULT_SOURCE"),
    ("g2d_t14_degraded_to_parent_return", "CELL_RESULT_SOURCE"),
    ("g2d_t15_blocked_to_parent_return", "CELL_RESULT_SOURCE"),
    ("g2d_t16_needs_user_to_parent_return", "CELL_RESULT_SOURCE"),
    ("g2d_t17_deadend_to_parent_return", "CELL_RESULT_SOURCE"),
)

G2D2_PARENT_RELATION_ROWS = (
    ("g2d_t01_route_eligibility_to_topology", "ROUTE_TO_TOPOLOGY"),
    ("g2d_t02_topology_to_pending", "TOPOLOGY_TO_INITIAL_QUEUE"),
    ("g2d_t03_pending_backpressure_defer", "QUEUE_SUCCESSOR_NO_RESULT"),
    ("g2d_t04_pending_to_ready", "QUEUE_SUCCESSOR_NO_RESULT"),
    ("g2d_t05_ready_to_running", "QUEUE_SUCCESSOR_NO_RESULT"),
    (
        "g2d_t06_running_to_validating",
        "QUEUE_SUCCESSOR_RESULT_INTRODUCTION",
    ),
    ("g2d_t07_validating_to_revise", "QUEUE_SUCCESSOR_NO_RESULT"),
    (
        "g2d_t08_validating_to_completed",
        "QUEUE_SUCCESSOR_RESULT_PRESERVATION",
    ),
    (
        "g2d_t09_validating_to_degraded",
        "QUEUE_SUCCESSOR_RESULT_PRESERVATION",
    ),
    (
        "g2d_t10_validating_to_blocked",
        "QUEUE_SUCCESSOR_RESULT_PRESERVATION",
    ),
    (
        "g2d_t11_validating_to_needs_user",
        "QUEUE_SUCCESSOR_RESULT_PRESERVATION",
    ),
    (
        "g2d_t12_validating_to_deadend",
        "QUEUE_SUCCESSOR_RESULT_PRESERVATION",
    ),
    ("g2d_t13_completed_to_parent_return", "ROOT_RESULT_TO_REPORT"),
    ("g2d_t14_degraded_to_parent_return", "ROOT_RESULT_TO_REPORT"),
    ("g2d_t15_blocked_to_parent_return", "ROOT_RESULT_TO_REPORT"),
    ("g2d_t16_needs_user_to_parent_return", "ROOT_RESULT_TO_REPORT"),
    ("g2d_t17_deadend_to_parent_return", "ROOT_RESULT_TO_REPORT"),
)

G2D2_EXPECTED_RULE_ROWS = (
    (
        "g2d_t01_route_eligibility_to_topology", 1,
        "ExecutionModeRouteEligibility", "ROOT_ACCEPTED", "fractal_runtime",
        "CONSTRUCT_RUNTIME_TOPOLOGY", "RuntimeExecutionTopology",
        (
            "g2c_profile_valid", "route_eligibility_context_valid",
            "runtime_topology_class", "runtime_policy_valid",
            "root_commit_present",
        ),
        "ALLOW", "g2d_transition_topology_construction_allowed", True,
    ),
    (
        "g2d_t02_topology_to_pending", 1, "RuntimeExecutionTopology",
        "VALIDATED", "fractal_runtime", "ADMIT_TOPOLOGY_QUEUE",
        "FractalCellQueueEntry",
        (
            "topology_context_valid", "budget_valid", "queue_capacity_visible",
            "queue_predecessor_initial_none", "root_commit_present",
        ),
        "ALLOW", "g2d_transition_queue_admission_allowed", True,
    ),
    (
        "g2d_t03_pending_backpressure_defer", 1, "FractalCellQueueEntry",
        "VALIDATED", "fractal_scheduler", "DEFER_BACKPRESSURE",
        "FractalCellQueueEntry",
        (
            "queue_entry_context_valid", "queue_state_pending",
            "predecessor_queue_artifact_lineage_valid", "cell_activation_valid",
            "dependencies_satisfied", "cell_input_context_valid",
            "budget_available", "admission_slot_unavailable_after_ordering",
            "lineage_preserved", "root_commit_present",
        ),
        "ALLOW", "g2d_transition_backpressure_deferred", True,
    ),
    (
        "g2d_t04_pending_to_ready", 1, "FractalCellQueueEntry", "VALIDATED",
        "fractal_scheduler", "MARK_READY", "FractalCellQueueEntry",
        (
            "queue_entry_context_valid", "queue_state_pending",
            "predecessor_queue_artifact_lineage_valid", "cell_activation_valid",
            "dependencies_satisfied", "cell_input_context_valid",
            "budget_available", "admission_slot_selected", "root_commit_present",
        ),
        "ALLOW", "g2d_transition_pending_ready_allowed", True,
    ),
    (
        "g2d_t05_ready_to_running", 1, "FractalCellQueueEntry", "VALIDATED",
        "fractal_scheduler", "START_LOCAL_WORK", "FractalCellQueueEntry",
        (
            "queue_entry_context_valid", "queue_state_ready",
            "predecessor_queue_artifact_lineage_valid", "assignment_valid",
            "ready_parallel_reservation_valid", "budget_available",
            "root_commit_present",
        ),
        "ALLOW", "g2d_transition_ready_running_allowed", True,
    ),
    (
        "g2d_t06_running_to_validating", 1, "FractalCellQueueEntry",
        "VALIDATED", "fractal_scheduler", "ENTER_VALIDATION",
        "FractalCellQueueEntry",
        (
            "queue_entry_context_valid", "queue_state_running",
            "predecessor_queue_artifact_lineage_valid", "cell_input_context_valid",
            "local_result_or_activation_gate_outcome_available",
            "running_budget_debit_present",
            "global_parallelism_release_derivable", "root_commit_present",
        ),
        "ALLOW", "g2d_transition_running_validating_allowed", True,
    ),
    (
        "g2d_t07_validating_to_revise", 1, "FractalCellQueueEntry",
        "VALIDATED", "fractal_scheduler", "REVISE_BOUNDED",
        "FractalCellQueueEntry",
        (
            "queue_entry_context_valid", "queue_state_validating",
            "predecessor_queue_artifact_lineage_valid",
            "cell_validation_complete", "revise_eligible",
            "progress_policy_valid", "budget_available",
            "revise_admission_slot_selected", "root_commit_present",
        ),
        "ALLOW", "g2d_transition_bounded_revise_allowed", True,
    ),
    (
        "g2d_t08_validating_to_completed", 1, "FractalCellQueueEntry",
        "VALIDATED", "fractal_scheduler", "RECORD_COMPLETED",
        "FractalCellQueueEntry",
        (
            "queue_entry_context_valid", "queue_state_validating",
            "predecessor_queue_artifact_lineage_valid",
            "node_validation_complete", "node_outcome_completed",
            "budget_accounted", "root_commit_present",
        ),
        "ALLOW", "g2d_transition_completed_recorded", True,
    ),
    (
        "g2d_t09_validating_to_degraded", 1, "FractalCellQueueEntry",
        "VALIDATED", "fractal_scheduler", "RECORD_DEGRADED",
        "FractalCellQueueEntry",
        (
            "queue_entry_context_valid", "queue_state_validating",
            "predecessor_queue_artifact_lineage_valid",
            "node_validation_complete", "node_outcome_degraded",
            "node_degraded_basis_valid", "budget_accounted",
            "root_commit_present",
        ),
        "RETURN_TO_ROOT", "g2d_transition_degraded_recorded", True,
    ),
    (
        "g2d_t10_validating_to_blocked", 1, "FractalCellQueueEntry",
        "VALIDATED", "fractal_scheduler", "RECORD_BLOCKED",
        "FractalCellQueueEntry",
        (
            "queue_entry_context_valid", "queue_state_validating",
            "predecessor_queue_artifact_lineage_valid",
            "node_validation_complete", "node_outcome_blocked",
            "node_hard_failure_valid", "budget_accounted",
            "root_commit_present",
        ),
        "BLOCKED_FAIL_CLOSED", "g2d_transition_blocked_recorded", True,
    ),
    (
        "g2d_t11_validating_to_needs_user", 1, "FractalCellQueueEntry",
        "VALIDATED", "fractal_scheduler", "RECORD_NEEDS_USER",
        "FractalCellQueueEntry",
        (
            "queue_entry_context_valid", "queue_state_validating",
            "predecessor_queue_artifact_lineage_valid",
            "node_validation_complete", "node_outcome_needs_user",
            "node_resolvable_input_missing", "budget_accounted",
            "root_commit_present",
        ),
        "NEEDS_USER", "g2d_transition_needs_user_recorded", True,
    ),
    (
        "g2d_t12_validating_to_deadend", 1, "FractalCellQueueEntry",
        "VALIDATED", "fractal_scheduler", "RECORD_DEADEND",
        "FractalCellQueueEntry",
        (
            "queue_entry_context_valid", "queue_state_validating",
            "predecessor_queue_artifact_lineage_valid",
            "node_validation_complete", "node_outcome_deadend",
            "node_no_progress_or_nonresolvable", "budget_accounted",
            "root_commit_present",
        ),
        "RETURN_TO_ROOT", "g2d_transition_deadend_recorded", True,
    ),
    (
        "g2d_t13_completed_to_parent_return", 1, "FractalCellResult",
        "VALIDATED", "fractal_runtime", "RETURN_TO_PARENT",
        "FractalRuntimeReport",
        (
            "cell_result_context_valid", "cell_outcome_completed",
            "source_cell_is_root", "root_cell_result_context_valid",
            "all_required_descendant_results_accounted",
            "canonical_result_postorder_valid", "parent_lineage_valid",
            "root_review_required", "root_commit_present",
        ),
        "RETURN_TO_ROOT", "g2d_transition_completed_parent_return", True,
    ),
    (
        "g2d_t14_degraded_to_parent_return", 1, "FractalCellResult",
        "VALIDATED", "fractal_runtime", "RETURN_TO_PARENT",
        "FractalRuntimeReport",
        (
            "cell_result_context_valid", "cell_outcome_degraded",
            "source_cell_is_root", "root_cell_result_context_valid",
            "all_required_descendant_results_accounted",
            "canonical_result_postorder_valid", "parent_lineage_valid",
            "root_review_required", "root_commit_present",
        ),
        "RETURN_TO_ROOT", "g2d_transition_degraded_parent_return", True,
    ),
    (
        "g2d_t15_blocked_to_parent_return", 1, "FractalCellResult",
        "BLOCKED_FAIL_CLOSED", "fractal_runtime", "RETURN_TO_PARENT",
        "FractalRuntimeReport",
        (
            "cell_result_context_valid", "cell_outcome_blocked",
            "source_cell_is_root", "root_cell_result_context_valid",
            "all_required_descendant_results_accounted",
            "canonical_result_postorder_valid", "parent_lineage_valid",
            "root_review_required", "root_commit_present",
        ),
        "BLOCKED_FAIL_CLOSED", "g2d_transition_blocked_parent_return", True,
    ),
    (
        "g2d_t16_needs_user_to_parent_return", 1, "FractalCellResult",
        "VALIDATED", "fractal_runtime", "RETURN_TO_PARENT",
        "FractalRuntimeReport",
        (
            "cell_result_context_valid", "cell_outcome_needs_user",
            "source_cell_is_root", "root_cell_result_context_valid",
            "all_required_descendant_results_accounted",
            "canonical_result_postorder_valid", "parent_lineage_valid",
            "root_review_required", "root_commit_present",
        ),
        "NEEDS_USER", "g2d_transition_needs_user_parent_return", True,
    ),
    (
        "g2d_t17_deadend_to_parent_return", 1, "FractalCellResult",
        "VALIDATED", "fractal_runtime", "RETURN_TO_PARENT",
        "FractalRuntimeReport",
        (
            "cell_result_context_valid", "cell_outcome_deadend",
            "source_cell_is_root", "root_cell_result_context_valid",
            "all_required_descendant_results_accounted",
            "canonical_result_postorder_valid", "parent_lineage_valid",
            "root_review_required", "root_commit_present",
        ),
        "RETURN_TO_ROOT", "g2d_transition_deadend_parent_return", True,
    ),
)


def _g2d2_artifact(
    artifact_type: str,
    lifecycle_state: str,
    suffix: str,
    *,
    payload: dict[str, object],
    parent_refs: tuple[str, ...],
    transaction_id: str,
    owner_root_id: str,
    trace_refs: tuple[str, ...] | None = None,
    time_envelope: dict[str, object] | None = None,
):
    domain, prefix, schema_version, source_component, authority_class = (
        G2D2_ARTIFACT_CONTEXT_PROFILES[artifact_type]
    )
    provisional = build_kernel_artifact_v01(
        abi_version="v1.0",
        artifact_id=prefix + "0" * 64,
        artifact_type=artifact_type,
        schema_version=schema_version,
        transaction_id=transaction_id,
        owner_root_id=owner_root_id,
        source_component=source_component,
        authority_class=authority_class,
        lifecycle_state=lifecycle_state,
        payload=payload,
        trace_refs=(f"trace:g2d2:{suffix}",) if trace_refs is None else trace_refs,
        parent_refs=parent_refs,
        time_envelope=time_envelope or {
            "ct_session_anchor": "ct:g2d2",
            "et_observed_at": "2026-08-04T00:00:00+00:00",
            "freshness_class": "static",
            "kt_asof": "2026-08-04T00:00:00+00:00",
            "pt_created_at": "2026-08-04T00:00:00+00:00",
            "ttl_seconds": 3600,
            "valid_from": "2026-08-04T00:00:00+00:00",
            "valid_to": "2026-08-04T01:00:00+00:00",
        },
    )
    material = kernel_artifact_to_plain_dict_v01(provisional)
    material.pop("artifact_id")
    return replace(
        provisional,
        artifact_id=prefix + domain_separated_sha256_hex_v01(
            domain=domain,
            payload=canonical_json_bytes_v01(material),
        ),
    )


def _g2d2_rebuild_artifact(
    artifact,
    *,
    lifecycle_state: str | None = None,
    payload: dict[str, object] | None = None,
    parent_refs: tuple[str, ...] | None = None,
    transaction_id: str | None = None,
    owner_root_id: str | None = None,
    trace_refs: tuple[str, ...] | None = None,
    time_envelope: dict[str, object] | None = None,
):
    plain = kernel_artifact_to_plain_dict_v01(artifact)
    return _g2d2_artifact(
        artifact.artifact_type,
        lifecycle_state or artifact.lifecycle_state,
        "rebuilt",
        payload=plain["payload"] if payload is None else payload,
        parent_refs=artifact.parent_refs if parent_refs is None else parent_refs,
        transaction_id=transaction_id or artifact.transaction_id,
        owner_root_id=owner_root_id or artifact.owner_root_id,
        trace_refs=artifact.trace_refs if trace_refs is None else trace_refs,
        time_envelope=plain["time_envelope"] if time_envelope is None else time_envelope,
    )


def _g2d2_artifact_pair(
    rule: transition.TransitionRuleV01,
    rule_index: int,
    *,
    transaction_id: str | None = None,
    owner_root_id: str | None = None,
):
    transaction = transaction_id or f"transaction:g2d2:{rule_index}"
    root = owner_root_id or f"root:g2d2:{rule_index}"
    topology_artifact_id = "frabi_topology_v02:" + "a" * 64
    topology_id = f"frtopology_v02:{rule_index:064x}"
    topology_seed_id = f"frseed_v02:{rule_index:064x}"
    registry = transition.build_fractal_runtime_transition_registry_profile_v02()
    decision_id = _g2d2_decision(rule, registry).decision_id
    prior_decision_id = f"{rule_index + 100:064x}"
    source_trace = (f"trace:g2d2:source:{rule_index}",)
    target_trace = (f"trace:g2d2:target:{rule_index}",)
    if rule_index == 0:
        decision_parent = "emabi_decision_v01:" + "b" * 64
        source_payload = {
            "accepted_mode": "full_fractal",
            "accepted_scope_ref": "scope:g2d2:transition",
        }
        source_parents = (decision_parent,)
        target_payload = {
            "accepted_mode": "full_fractal",
            "accepted_scope_ref": "scope:g2d2:transition",
            "source_root_decision_artifact_id": decision_parent,
        }
    elif rule_index == 1:
        source_payload = {
            "topology_id": topology_id,
            "topology_seed_id": topology_seed_id,
        }
        source_parents = ("emabi_route_v01:" + "c" * 64,)
        target_payload = {
            "topology_seed_id": topology_seed_id,
            "state": "PENDING",
            "prior_state": None,
            "predecessor_relation": "INITIAL_NONE",
            "parent_cell_id": None,
        }
        target_trace = (
            decision_id,
            topology_id,
            "lineage:g2d2:t02:target",
        )
    elif 2 <= rule_index <= 11:
        source_payload = {
            "topology_seed_id": topology_seed_id,
            "cell_id": "frrootcell_v02:" + "d" * 64,
            "parent_cell_id": None,
            "node_id": "frnode_v02:" + "e" * 64,
        }
        if rule_index in {2, 3}:
            source_payload.update({
                "state": "PENDING",
                "prior_state": None,
                "predecessor_relation": "INITIAL_NONE",
            })
        source_parents = (
            (topology_artifact_id,)
            if rule_index in {2, 3}
            else (
                topology_artifact_id,
                "frabi_queue_v02:" + "1" * 64,
            )
        )
        target_payload = dict(source_payload)
        source_trace = (
            prior_decision_id,
            topology_id,
            f"lineage:g2d2:source:{rule_index}",
        )
        target_trace = (
            decision_id,
            topology_id,
            f"lineage:g2d2:target:{rule_index}",
        )
    else:
        source_payload = {
            "topology_seed_id": topology_seed_id,
        }
        source_parents = (
            topology_artifact_id,
            "frabi_queue_v02:" + "f" * 64,
        )
        target_payload = dict(source_payload)
        source_trace = (
            f"post-vv:g2d2:{rule_index}",
            f"gt:g2d2:{rule_index}",
            topology_id,
        )
        target_trace = (
            f"runtime-trace:g2d2:{rule_index}",
            decision_id,
            f"parent-return:g2d2:{rule_index}",
        )
    source = _g2d2_artifact(
        rule.source_artifact_type,
        rule.source_lifecycle_state,
        f"source-{rule_index}",
        payload=source_payload,
        parent_refs=source_parents,
        transaction_id=transaction,
        owner_root_id=root,
        trace_refs=source_trace,
    )
    if rule_index <= 1:
        target_parents = (source.artifact_id,)
    elif rule_index <= 11:
        target_parents = (source.parent_refs[0], source.artifact_id)
    else:
        target_parents = (source.parent_refs[0], source.artifact_id)
    target = _g2d2_artifact(
        rule.target_artifact_type,
        G2D2_TARGET_LIFECYCLES[rule_index],
        f"target-{rule_index}",
        payload=target_payload,
        parent_refs=target_parents,
        transaction_id=transaction,
        owner_root_id=root,
        trace_refs=target_trace,
    )
    return source, target


def _g2d2_decision(
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
        root_commit_required=True,
        root_commit_present=True,
        matched=True,
    )
    return replace(
        provisional,
        decision_id=transition.rebuild_fractal_runtime_transition_decision_identity_v02(
            provisional
        ),
    )


def _g2d2_pair_errors(
    registry: transition.TransitionRegistryV01,
    rule_index: int,
    source,
    target,
) -> tuple[str, ...]:
    rule = registry.rules[rule_index]
    return transition.validate_fractal_runtime_transition_decision_v02(
        _g2d2_decision(rule, registry),
        registry=registry,
        source_artifact=source,
        target_artifact=target,
    )


def _g2d2_target_for_source(
    target,
    source,
    parent_refs: tuple[str, ...],
):
    source_payload = kernel_artifact_to_plain_dict_v01(source)["payload"]
    target_payload = kernel_artifact_to_plain_dict_v01(target)["payload"]
    for field_name in (
        "topology_seed_id",
        "cell_id",
        "parent_cell_id",
        "node_id",
    ):
        if field_name in source_payload and field_name in target_payload:
            target_payload[field_name] = source_payload[field_name]
    return _g2d2_rebuild_artifact(
        target,
        payload=target_payload,
        parent_refs=tuple(
            source.artifact_id if parent == "SOURCE" else parent
            for parent in parent_refs
        ),
    )


def test_g2d2_transition_surface_and_exact_seventeen_rule_profile() -> None:
    for name in G2D2_TRANSITION_FUNCTIONS:
        assert inspect.isfunction(getattr(transition, name))
        assert str(inspect.signature(getattr(transition, name))) == G2D2_TRANSITION_SIGNATURES[name]
        assert getattr(kernel_package, name) is getattr(transition, name)
    registry = transition.build_fractal_runtime_transition_registry_profile_v02()
    assert registry.registry_version == "v0.1"
    assert registry.abi_major_version == 1
    assert len(registry.rules) == 17
    assert tuple(rule.rule_id for rule in registry.rules) == G2D2_RULE_IDS
    assert tuple(
        tuple(getattr(rule, field_name) for field_name in RULE_FIELDS)
        for rule in registry.rules
    ) == G2D2_EXPECTED_RULE_ROWS
    assert transition._FRACTAL_RUNTIME_ARTIFACT_CONTEXT_PROFILES_V02 == tuple(
        (artifact_type, *profile)
        for artifact_type, profile in G2D2_ARTIFACT_CONTEXT_PROFILES.items()
    )
    assert tuple(
        lifecycle
        for _rule_id, lifecycle in (
            transition._FRACTAL_RUNTIME_TARGET_LIFECYCLE_BY_RULE_V02
        )
    ) == G2D2_TARGET_LIFECYCLES
    assert (
        transition._FRACTAL_RUNTIME_SOURCE_PARENT_PROFILE_BY_RULE_V02
        == G2D2_SOURCE_PARENT_PROFILE_ROWS
    )
    assert (
        transition._FRACTAL_RUNTIME_PARENT_RELATION_BY_RULE_V02
        == G2D2_PARENT_RELATION_ROWS
    )
    assert all(rule.abi_major_version == 1 for rule in registry.rules)
    assert all(rule.root_commit_required is True for rule in registry.rules)
    t01 = registry.rules[0]
    assert (
        t01.source_artifact_type,
        t01.source_lifecycle_state,
        t01.actor_role,
        t01.attempted_effect,
        t01.target_artifact_type,
        t01.required_guards,
        t01.decision,
        t01.reason_code,
    ) == (
        "ExecutionModeRouteEligibility",
        "ROOT_ACCEPTED",
        "fractal_runtime",
        "CONSTRUCT_RUNTIME_TOPOLOGY",
        "RuntimeExecutionTopology",
        (
            "g2c_profile_valid", "route_eligibility_context_valid",
            "runtime_topology_class", "runtime_policy_valid",
            "root_commit_present",
        ),
        "ALLOW",
        "g2d_transition_topology_construction_allowed",
    )
    assert transition.validate_fractal_runtime_transition_registry_profile_v02(registry) == ()
    plain = transition.fractal_runtime_transition_registry_profile_to_plain_dict_v02(registry)
    assert tuple(plain) == REGISTRY_FIELDS
    assert canonical_json_bytes_v01(plain) == canonical_json_bytes_v01(
        transition.fractal_runtime_transition_registry_profile_to_plain_dict_v02(
            transition.build_fractal_runtime_transition_registry_profile_v02()
        )
    )


@pytest.mark.parametrize("rule_index", range(17))
def test_g2d2_transition_decision_identity_and_substitution(rule_index: int) -> None:
    registry = transition.build_fractal_runtime_transition_registry_profile_v02()
    rule = registry.rules[rule_index]
    decision = _g2d2_decision(rule, registry)
    source, target = _g2d2_artifact_pair(rule, rule_index)
    assert transition.validate_fractal_runtime_transition_decision_v02(
        decision,
        registry=registry,
        source_artifact=source,
        target_artifact=target,
    ) == ()
    assert transition.rebuild_fractal_runtime_transition_decision_identity_v02(decision) == decision.decision_id
    assert tuple(transition.fractal_runtime_transition_decision_to_plain_dict_v02(decision)) == DECISION_FIELDS
    for mutation in (
        replace(decision, registry_id="0" * 64),
        replace(decision, rule_id=registry.rules[(rule_index + 1) % 17].rule_id),
        replace(decision, satisfied_guards=decision.satisfied_guards[::-1]),
        replace(decision, decision="ALLOW" if decision.decision != "ALLOW" else "RETURN_TO_ROOT"),
        replace(decision, reason_code="g2d_transition_decision_substituted"),
        replace(decision, root_commit_required=False),
        replace(decision, root_commit_present=False),
        replace(decision, decision_id="0" * 64),
    ):
        assert transition.validate_fractal_runtime_transition_decision_v02(
            mutation,
            registry=registry,
            source_artifact=source,
            target_artifact=target,
        )
    assert transition.validate_fractal_runtime_transition_decision_v02(
        decision,
        registry=registry,
        source_artifact=source,
        target_artifact=_g2d2_rebuild_artifact(
            target,
            lifecycle_state=(
                "VALIDATED" if rule_index == 14 else "BLOCKED_FAIL_CLOSED"
            ),
        ),
    )
    foreign_source, foreign_target = _g2d2_artifact_pair(
        rule,
        rule_index,
        transaction_id=f"transaction:g2d2:foreign:{rule_index}",
        owner_root_id=f"root:g2d2:foreign:{rule_index}",
    )
    assert transition.validate_fractal_runtime_transition_decision_v02(
        decision,
        registry=registry,
        source_artifact=foreign_source,
        target_artifact=target,
    )
    assert transition.validate_fractal_runtime_transition_decision_v02(
        decision,
        registry=registry,
        source_artifact=source,
        target_artifact=foreign_target,
    )
    assert transition.validate_fractal_runtime_transition_decision_v02(
        decision,
        registry=registry,
        source_artifact=source,
        target_artifact=_g2d2_rebuild_artifact(
            target,
            parent_refs=("frabi_topology_v02:" + "9" * 64,),
        ),
    )
    target_payload = kernel_artifact_to_plain_dict_v01(target)["payload"]
    lineage_key = "accepted_mode" if rule_index == 0 else "topology_id"
    assert transition.validate_fractal_runtime_transition_decision_v02(
        decision,
        registry=registry,
        source_artifact=source,
        target_artifact=_g2d2_rebuild_artifact(
            target,
            payload={**target_payload, lineage_key: "foreign:value"},
        ),
    )
    target_time = kernel_artifact_to_plain_dict_v01(target)["time_envelope"]
    assert transition.validate_fractal_runtime_transition_decision_v02(
        decision,
        registry=registry,
        source_artifact=source,
        target_artifact=_g2d2_rebuild_artifact(
            target,
            time_envelope={
                **target_time,
                "ct_session_anchor": "ct:g2d2:foreign",
            },
        ),
    )
    assert transition.validate_fractal_runtime_transition_decision_v02(
        decision,
        registry=registry,
        source_artifact=source,
        target_artifact=replace(
            target,
            artifact_id=(
                target.artifact_id[:-1]
                + ("0" if target.artifact_id[-1] != "0" else "1")
            ),
        ),
    )
    mutated_rule = replace(rule, actor_role=rule.actor_role + "_foreign")
    mutated_registry = replace(
        registry,
        rules=registry.rules[:rule_index] + (mutated_rule,) + registry.rules[rule_index + 1:],
    )
    assert transition.validate_fractal_runtime_transition_registry_profile_v02(mutated_registry)


def test_g2d2_ctx_only_topology_partition_and_trace_binding() -> None:
    queue_forbidden_ctx_keys = ("topology_id", "predecessor_queue_entry_id")
    result_forbidden_ctx_keys = ("topology_id",)
    report_forbidden_ctx_keys = ("topology_id",)
    registry = transition.build_fractal_runtime_transition_registry_profile_v02()
    foreign_topology = "frtopology_v02:" + "9" * 64
    foreign_decision = "9" * 64

    t02_source, t02_target = _g2d2_artifact_pair(registry.rules[1], 1)
    t02_source_payload = kernel_artifact_to_plain_dict_v01(t02_source)["payload"]
    t02_target_payload = kernel_artifact_to_plain_dict_v01(t02_target)["payload"]
    assert t02_source_payload["topology_id"] == t02_target.trace_refs[1]
    assert t02_source_payload["topology_seed_id"] == t02_target_payload["topology_seed_id"]
    assert all(key not in t02_target_payload for key in queue_forbidden_ctx_keys)
    for payload in (
        {**t02_target_payload, "topology_id": t02_source_payload["topology_id"]},
        {**t02_target_payload, "predecessor_queue_entry_id": "frqueue_v02:" + "1" * 64},
        {**t02_target_payload, "topology_seed_id": "frseed_v02:" + "2" * 64},
    ):
        assert _g2d2_pair_errors(
            registry,
            1,
            t02_source,
            _g2d2_rebuild_artifact(t02_target, payload=payload),
        )
    assert _g2d2_pair_errors(
        registry, 1, t02_source, replace(t02_target, trace_refs=())
    )
    for trace_refs in (
        (t02_target.trace_refs[0],),
        (t02_target.trace_refs[0], "topology:wrong"),
        (t02_target.trace_refs[0], foreign_topology),
        (foreign_decision, t02_target.trace_refs[1]),
    ):
        assert _g2d2_pair_errors(
            registry,
            1,
            t02_source,
            _g2d2_rebuild_artifact(t02_target, trace_refs=trace_refs),
        )

    for rule_index in range(2, 12):
        source, target = _g2d2_artifact_pair(
            registry.rules[rule_index], rule_index
        )
        source_payload = kernel_artifact_to_plain_dict_v01(source)["payload"]
        target_payload = kernel_artifact_to_plain_dict_v01(target)["payload"]
        assert all(key not in source_payload for key in queue_forbidden_ctx_keys)
        assert all(key not in target_payload for key in queue_forbidden_ctx_keys)
        assert source.trace_refs[1] == target.trace_refs[1]
        for artifact, payload in (
            (source, {**source_payload, "topology_id": source.trace_refs[1]}),
            (source, {**source_payload, "predecessor_queue_entry_id": "frqueue_v02:" + "2" * 64}),
            (target, {**target_payload, "topology_id": target.trace_refs[1]}),
            (target, {**target_payload, "predecessor_queue_entry_id": source.artifact_id}),
        ):
            rebuilt = _g2d2_rebuild_artifact(artifact, payload=payload)
            assert _g2d2_pair_errors(
                registry,
                rule_index,
                rebuilt if artifact is source else source,
                rebuilt if artifact is target else target,
            )
        assert _g2d2_pair_errors(
            registry,
            rule_index,
            replace(source, trace_refs=()),
            target,
        )
        for source_trace_refs in (
            (source.trace_refs[0],),
            (source.trace_refs[0], "topology:wrong"),
        ):
            assert _g2d2_pair_errors(
                registry,
                rule_index,
                _g2d2_rebuild_artifact(
                    source, trace_refs=source_trace_refs
                ),
                target,
            )
        assert _g2d2_pair_errors(
            registry,
            rule_index,
            _g2d2_rebuild_artifact(
                source,
                trace_refs=(source.trace_refs[0], foreign_topology),
            ),
            target,
        )
        assert _g2d2_pair_errors(
            registry, rule_index, source, replace(target, trace_refs=())
        )
        for trace_refs in (
            (target.trace_refs[0],),
            (target.trace_refs[0], "topology:wrong"),
            (target.trace_refs[0], foreign_topology),
            (foreign_decision, target.trace_refs[1]),
        ):
            assert _g2d2_pair_errors(
                registry,
                rule_index,
                source,
                _g2d2_rebuild_artifact(target, trace_refs=trace_refs),
            )
        assert _g2d2_pair_errors(
            registry,
            rule_index,
            source,
            _g2d2_rebuild_artifact(
                target,
                payload={
                    **target_payload,
                    "topology_seed_id": "frseed_v02:" + "3" * 64,
                },
            ),
        )

    for rule_index in range(12, 17):
        source, target = _g2d2_artifact_pair(
            registry.rules[rule_index], rule_index
        )
        source_payload = kernel_artifact_to_plain_dict_v01(source)["payload"]
        target_payload = kernel_artifact_to_plain_dict_v01(target)["payload"]
        assert all(key not in source_payload for key in result_forbidden_ctx_keys)
        assert all(key not in target_payload for key in report_forbidden_ctx_keys)
        assert target.trace_refs[1] == _g2d2_decision(
            registry.rules[rule_index], registry
        ).decision_id
        assert _g2d2_pair_errors(
            registry,
            rule_index,
            _g2d2_rebuild_artifact(
                source,
                payload={**source_payload, "topology_id": foreign_topology},
            ),
            target,
        )
        for payload in (
            {**target_payload, "topology_id": foreign_topology},
            {**target_payload, "topology_seed_id": "frseed_v02:" + "4" * 64},
        ):
            assert _g2d2_pair_errors(
                registry,
                rule_index,
                source,
                _g2d2_rebuild_artifact(target, payload=payload),
            )
        assert _g2d2_pair_errors(
            registry, rule_index, source, replace(target, trace_refs=())
        )
        for trace_refs in (
            (target.trace_refs[0],),
            (target.trace_refs[0], foreign_decision),
        ):
            assert _g2d2_pair_errors(
                registry,
                rule_index,
                source,
                _g2d2_rebuild_artifact(target, trace_refs=trace_refs),
            )


def test_g2d2_initial_and_queue_parent_geometry() -> None:
    registry = transition.build_fractal_runtime_transition_registry_profile_v02()
    topology_id = "frabi_topology_v02:" + "2" * 64
    parent_slot_id = "frabi_queue_v02:" + "3" * 64
    result_id = "frabi_result_v02:" + "4" * 64
    binding_ids = (
        "frobservedwork_v02:" + "5" * 64,
        "frobservedwork_v02:" + "6" * 64,
    )

    t02_source, t02_target = _g2d2_artifact_pair(registry.rules[1], 1)
    assert _g2d2_pair_errors(registry, 1, t02_source, t02_target) == ()
    child_target = _g2d2_rebuild_artifact(
        t02_target,
        payload={
            **kernel_artifact_to_plain_dict_v01(t02_target)["payload"],
            "parent_cell_id": "frrootcell_v02:" + "7" * 64,
        },
        parent_refs=(t02_source.artifact_id, parent_slot_id),
    )
    assert _g2d2_pair_errors(registry, 1, t02_source, child_target) == ()
    root_context_target = _g2d2_rebuild_artifact(
        t02_target,
        parent_refs=(t02_source.artifact_id, *binding_ids),
    )
    child_context_target = _g2d2_rebuild_artifact(
        t02_target,
        payload={
            **kernel_artifact_to_plain_dict_v01(t02_target)["payload"],
            "parent_cell_id": "frrootcell_v02:" + "7" * 64,
        },
        parent_refs=(t02_source.artifact_id, parent_slot_id, *binding_ids),
    )
    assert _g2d2_pair_errors(
        registry, 1, t02_source, root_context_target
    ) == ()
    assert _g2d2_pair_errors(
        registry, 1, t02_source, child_context_target
    ) == ()
    for bad_parents in (
        (t02_source.artifact_id, result_id),
        (topology_id, parent_slot_id),
        (t02_source.artifact_id, parent_slot_id, result_id),
        (t02_source.artifact_id, parent_slot_id, "binding:foreign"),
    ):
        assert _g2d2_pair_errors(
            registry,
            1,
            t02_source,
            _g2d2_rebuild_artifact(t02_target, parent_refs=bad_parents),
        )
    assert _g2d2_pair_errors(
        registry,
        1,
        t02_source,
        replace(
            t02_target,
            parent_refs=(
                t02_source.artifact_id,
                binding_ids[0],
                binding_ids[0],
            ),
        ),
    )
    assert _g2d2_pair_errors(
        registry,
        1,
        t02_source,
        replace(
            t02_target,
            parent_refs=(t02_source.artifact_id, t02_source.artifact_id),
        ),
    )
    assert _g2d2_pair_errors(
        registry,
        1,
        t02_source,
        replace(t02_target, parent_refs=(t02_target.artifact_id,)),
    )

    for rule_index in (2, 3):
        source, target = _g2d2_artifact_pair(
            registry.rules[rule_index], rule_index
        )
        assert len(source.parent_refs) == 1
        assert _g2d2_pair_errors(registry, rule_index, source, target) == ()
        child_source = _g2d2_rebuild_artifact(
            source,
            payload={
                **kernel_artifact_to_plain_dict_v01(source)["payload"],
                "parent_cell_id": "frrootcell_v02:" + "7" * 64,
            },
            parent_refs=(source.parent_refs[0], parent_slot_id),
        )
        child_target = _g2d2_target_for_source(
            target,
            child_source,
            (child_source.parent_refs[0], "SOURCE"),
        )
        assert _g2d2_pair_errors(
            registry, rule_index, child_source, child_target
        ) == ()
        context_source = _g2d2_rebuild_artifact(
            source,
            parent_refs=(source.parent_refs[0], *binding_ids),
        )
        context_target = _g2d2_target_for_source(
            target,
            context_source,
            (context_source.parent_refs[0], "SOURCE"),
        )
        assert _g2d2_pair_errors(
            registry, rule_index, context_source, context_target
        ) == ()
        child_context_source = _g2d2_rebuild_artifact(
            source,
            payload={
                **kernel_artifact_to_plain_dict_v01(source)["payload"],
                "parent_cell_id": "frrootcell_v02:" + "7" * 64,
            },
            parent_refs=(source.parent_refs[0], parent_slot_id, *binding_ids),
        )
        child_context_target = _g2d2_target_for_source(
            target,
            child_context_source,
            (child_context_source.parent_refs[0], "SOURCE"),
        )
        assert _g2d2_pair_errors(
            registry,
            rule_index,
            child_context_source,
            child_context_target,
        ) == ()

    for rule_index in range(4, 12):
        source, target = _g2d2_artifact_pair(
            registry.rules[rule_index], rule_index
        )
        assert len(source.parent_refs) == 2
        assert _g2d2_pair_errors(registry, rule_index, source, target) == ()

    for rule_index in (2, 3, 4, 6):
        source, target = _g2d2_artifact_pair(
            registry.rules[rule_index], rule_index
        )
        forbidden_target = _g2d2_rebuild_artifact(
            target,
            parent_refs=(
                source.parent_refs[0],
                source.artifact_id,
                result_id,
            ),
        )
        assert _g2d2_pair_errors(
            registry, rule_index, source, forbidden_target
        )


def test_g2d2_child_result_parent_introduction_and_preservation() -> None:
    registry = transition.build_fractal_runtime_transition_registry_profile_v02()
    child_result_id = "frabi_result_v02:" + "5" * 64
    foreign_result_id = "frabi_result_v02:" + "6" * 64

    t06_source, t06_target = _g2d2_artifact_pair(registry.rules[5], 5)
    invoked_t06_target = _g2d2_rebuild_artifact(
        t06_target,
        parent_refs=(
            t06_source.parent_refs[0],
            t06_source.artifact_id,
            child_result_id,
        ),
    )
    assert len(t06_source.parent_refs) == 2
    assert _g2d2_pair_errors(
        registry, 5, t06_source, invoked_t06_target
    ) == ()

    for rule_index in range(7, 12):
        source, ordinary_target = _g2d2_artifact_pair(
            registry.rules[rule_index], rule_index
        )
        assert _g2d2_pair_errors(
            registry, rule_index, source, ordinary_target
        ) == ()
        invented_target = _g2d2_rebuild_artifact(
            ordinary_target,
            parent_refs=(
                source.parent_refs[0],
                source.artifact_id,
                child_result_id,
            ),
        )
        assert _g2d2_pair_errors(
            registry, rule_index, source, invented_target
        )

        invoked_source = _g2d2_rebuild_artifact(
            source,
            parent_refs=source.parent_refs + (child_result_id,),
        )
        invoked_target = _g2d2_target_for_source(
            ordinary_target,
            invoked_source,
            (invoked_source.parent_refs[0], "SOURCE", child_result_id),
        )
        assert _g2d2_pair_errors(
            registry, rule_index, invoked_source, invoked_target
        ) == ()
        removed_target = _g2d2_target_for_source(
            ordinary_target,
            invoked_source,
            (invoked_source.parent_refs[0], "SOURCE"),
        )
        changed_target = _g2d2_target_for_source(
            ordinary_target,
            invoked_source,
            (invoked_source.parent_refs[0], "SOURCE", foreign_result_id),
        )
        assert _g2d2_pair_errors(
            registry, rule_index, invoked_source, removed_target
        )
        assert _g2d2_pair_errors(
            registry, rule_index, invoked_source, changed_target
        )


def test_g2d2_topology_continuity_and_source_parent_envelopes() -> None:
    registry = transition.build_fractal_runtime_transition_registry_profile_v02()
    foreign_topology_id = "frabi_topology_v02:" + "7" * 64
    queue_id = "frabi_queue_v02:" + "8" * 64
    second_queue_id = "frabi_queue_v02:" + "9" * 64
    result_id = "frabi_result_v02:" + "a" * 64

    for rule_index in range(2, 17):
        source, target = _g2d2_artifact_pair(
            registry.rules[rule_index], rule_index
        )
        foreign_target_parents = (
            foreign_topology_id,
            *target.parent_refs[1:],
        )
        assert _g2d2_pair_errors(
            registry,
            rule_index,
            source,
            _g2d2_rebuild_artifact(
                target,
                parent_refs=foreign_target_parents,
            ),
        )

    source, target = _g2d2_artifact_pair(registry.rules[0], 0)
    malformed_source = _g2d2_rebuild_artifact(
        source,
        parent_refs=("emabi_route_v01:" + "b" * 64,),
    )
    assert _g2d2_pair_errors(
        registry,
        0,
        malformed_source,
        _g2d2_target_for_source(target, malformed_source, ("SOURCE",)),
    )

    source, target = _g2d2_artifact_pair(registry.rules[1], 1)
    malformed_source = _g2d2_rebuild_artifact(
        source,
        parent_refs=("emabi_decision_v01:" + "c" * 64,),
    )
    assert _g2d2_pair_errors(
        registry,
        1,
        malformed_source,
        _g2d2_target_for_source(target, malformed_source, ("SOURCE",)),
    )

    for rule_index in (4, 5, 6):
        source, target = _g2d2_artifact_pair(
            registry.rules[rule_index], rule_index
        )
        for bad_source_parents in (
            (source.parent_refs[0],),
            source.parent_refs + (result_id,),
        ):
            malformed_source = _g2d2_rebuild_artifact(
                source,
                parent_refs=bad_source_parents,
            )
            assert _g2d2_pair_errors(
                registry,
                rule_index,
                malformed_source,
                _g2d2_target_for_source(
                    target,
                    malformed_source,
                    (source.parent_refs[0], "SOURCE"),
                ),
            )

    for rule_index in range(12, 17):
        source, target = _g2d2_artifact_pair(
            registry.rules[rule_index], rule_index
        )
        for bad_source_parents in (
            (source.parent_refs[0], result_id),
            (source.parent_refs[0], queue_id, result_id, second_queue_id),
        ):
            malformed_source = _g2d2_rebuild_artifact(
                source,
                parent_refs=bad_source_parents,
            )
            assert _g2d2_pair_errors(
                registry,
                rule_index,
                malformed_source,
                _g2d2_target_for_source(
                    target,
                    malformed_source,
                    (source.parent_refs[0], "SOURCE"),
                ),
            )
        assert _g2d2_pair_errors(
            registry,
            rule_index,
            replace(
                source,
                parent_refs=(source.parent_refs[0], queue_id, queue_id),
            ),
            target,
        )
        assert _g2d2_pair_errors(
            registry,
            rule_index,
            replace(source, parent_refs=(source.artifact_id,)),
            target,
        )


def test_g2d2_profile_preserves_historical_registries_and_import_direction() -> None:
    default_before = transition.transition_registry_to_plain_dict_v01(
        transition.build_default_transition_registry_v01()
    )
    g2c_before = transition.execution_mode_transition_registry_profile_to_plain_dict_v01(
        transition.build_execution_mode_transition_registry_profile_v01()
    )
    transition.build_fractal_runtime_transition_registry_profile_v02()
    assert canonical_json_bytes_v01(default_before) == canonical_json_bytes_v01(
        transition.transition_registry_to_plain_dict_v01(
            transition.build_default_transition_registry_v01()
        )
    )
    assert canonical_json_bytes_v01(g2c_before) == canonical_json_bytes_v01(
        transition.execution_mode_transition_registry_profile_to_plain_dict_v01(
            transition.build_execution_mode_transition_registry_profile_v01()
        )
    )
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "hedgehog.kernel.fractal_runtime_v02" not in source


G2E_TRANSITION_EXPECTED_ROWS = (
    (
        "g2e_t01_delta_validate", 1, "ContinuousDeltaSource", "PROPOSED",
        "continuous_delta_runtime", "VALIDATE_DELTA_SOURCE",
        "ContinuousDeltaSource",
        (
            "delta_source_artifact_valid", "source_pair_valid",
            "manifest_replay_projection_valid", "zero_operation_boundary_valid",
        ),
        "ALLOW", "g2e_transition_delta_validated", False,
    ),
    (
        "g2e_t02_affected_set_derive", 1, "ContinuousDeltaSource", "VALIDATED",
        "continuous_delta_runtime", "DERIVE_AFFECTED_SET", "AffectedSetResult",
        (
            "delta_source_context_valid", "dependency_graph_artifact_valid",
            "dependency_fingerprints_valid", "changed_binding_carriers_complete",
            "dependency_edge_carriers_complete", "artifact_node_closure_complete",
            "affected_set_bounds_valid",
        ),
        "ALLOW", "g2e_transition_affected_set_derived", False,
    ),
    (
        "g2e_t03_invalidation_derive", 1, "AffectedSetResult", "VALIDATED",
        "continuous_delta_runtime", "DERIVE_INVALIDATION",
        "ArtifactInvalidationReport",
        (
            "affected_set_artifact_valid", "invalidation_carriers_complete",
            "prior_slice_currentness_valid", "immutable_history_preserved",
            "zero_operation_boundary_valid",
        ),
        "ALLOW", "g2e_transition_invalidation_derived", False,
    ),
    (
        "g2e_t04_plan_root_review", 1, "SelectiveRecomputationPlan", "PROPOSED",
        "continuous_delta_runtime", "RETURN_TO_ROOT", "RootDecision",
        (
            "plan_proposed_artifact_valid", "plan_source_bindings_valid",
            "plan_bounds_valid", "plan_root_input_valid", "root_target_bound",
            "zero_operation_boundary_valid",
        ),
        "RETURN_TO_ROOT", "g2e_transition_recomputation_plan_reviewed", False,
    ),
    (
        "g2e_t05_plan_root_accept", 1, "RootDecision", "ROOT_REVIEWED", "root",
        "ACCEPT_RECOMPUTATION_PLAN", "SelectiveRecomputationPlan",
        (
            "plan_root_input_valid", "plan_root_result_valid", "root_decision_accept",
            "selected_plan_exact", "plan_proposed_artifact_valid",
            "root_zero_effect_geometry_valid", "root_commit_present",
        ),
        "ALLOW", "g2e_transition_recomputation_plan_accepted", True,
    ),
    (
        "g2e_t06_plan_root_reject", 1, "RootDecision", "ROOT_REVIEWED", "root",
        "REJECT_RECOMPUTATION_PLAN", "SelectiveRecomputationPlan",
        (
            "plan_root_input_valid", "plan_root_result_valid",
            "root_decision_non_accept", "selected_plan_binding_valid",
            "terminal_non_execution_valid", "root_zero_effect_geometry_valid",
            "root_commit_present",
        ),
        "BLOCKED_FAIL_CLOSED", "g2e_transition_recomputation_plan_rejected", True,
    ),
    (
        "g2e_t07_selective_recompute", 1, "SelectiveRecomputationPlan",
        "ROOT_ACCEPTED", "continuous_delta_runtime",
        "EXECUTE_SELECTIVE_RECOMPUTATION", "FractalRuntimeReport",
        (
            "plan_accepted_artifact_valid", "plan_root_decision_valid",
            "route_topology_current", "affected_work_mapping_valid",
            "g2d_public_seams_valid", "execution_bounds_valid",
            "root_commit_present",
        ),
        "ALLOW", "g2e_transition_selective_recomputation_executed", True,
    ),
    (
        "g2e_t08_recompute_block", 1, "SelectiveRecomputationPlan",
        "ROOT_ACCEPTED", "continuous_delta_runtime",
        "BLOCK_SELECTIVE_RECOMPUTATION", "ContinuousDeltaRuntimeReport",
        (
            "plan_accepted_artifact_valid", "execution_failure_evidence_valid",
            "accepted_g2d_bundle_absent", "terminal_fail_closed_valid",
            "zero_operation_boundary_valid", "root_commit_present",
        ),
        "BLOCKED_FAIL_CLOSED", "g2e_transition_selective_recomputation_blocked", True,
    ),
    (
        "g2e_t09_parent_return", 1, "FractalRuntimeReport", "VALIDATED",
        "continuous_delta_runtime", "RETURN_TO_ROOT", "RootDecision",
        (
            "recomputed_g2d_bundle_valid", "recomputation_result_valid",
            "preservation_proof_valid", "partial_failures_resolved",
            "final_root_input_valid", "zero_operation_boundary_valid",
        ),
        "RETURN_TO_ROOT", "g2e_transition_delta_parent_returned", False,
    ),
    (
        "g2e_t10_report_finalize", 1, "RootDecision", "ROOT_REVIEWED", "root",
        "FINALIZE_CONTINUOUS_DELTA_REPORT", "ContinuousDeltaRuntimeReport",
        (
            "final_root_input_valid", "final_root_result_valid",
            "root_decision_accept", "selected_result_exact",
            "runtime_report_artifact_valid", "preservation_proof_valid",
            "transition_prefix_t01_t09_valid", "root_zero_effect_geometry_valid",
            "root_commit_present",
        ),
        "ALLOW", "g2e_transition_delta_report_finalized", True,
    ),
)

_G2E_ARTIFACT_PROFILES = {
    ("ContinuousDeltaSource", "PROPOSED"): (
        "NON_AUTHORITY", "g2eabi_source_proposed_v01:",
        "HEDGEHOG_G2E_CONTINUOUS_DELTA_SOURCE_PROPOSED_ARTIFACT_V01",
    ),
    ("ContinuousDeltaSource", "VALIDATED"): (
        "NON_AUTHORITY", "g2eabi_source_validated_v01:",
        "HEDGEHOG_G2E_CONTINUOUS_DELTA_SOURCE_VALIDATED_ARTIFACT_V01",
    ),
    ("DependencyGraphIndex", "VALIDATED"): (
        "NON_AUTHORITY", "g2eabi_graph_v01:",
        "HEDGEHOG_G2E_DEPENDENCY_GRAPH_INDEX_ARTIFACT_V01",
    ),
    ("AffectedSetResult", "VALIDATED"): (
        "NON_AUTHORITY", "g2eabi_affected_v01:",
        "HEDGEHOG_G2E_AFFECTED_SET_RESULT_ARTIFACT_V01",
    ),
    ("ArtifactInvalidationReport", "VALIDATED"): (
        "NON_AUTHORITY", "g2eabi_invalidation_v01:",
        "HEDGEHOG_G2E_ARTIFACT_INVALIDATION_REPORT_ARTIFACT_V01",
    ),
    ("SelectiveRecomputationPlan", "PROPOSED"): (
        "ADVISORY", "g2eabi_plan_proposed_v01:",
        "HEDGEHOG_G2E_SELECTIVE_RECOMPUTATION_PLAN_PROPOSED_ARTIFACT_V01",
    ),
    ("SelectiveRecomputationPlan", "ROOT_ACCEPTED"): (
        "ADVISORY", "g2eabi_plan_accepted_v01:",
        "HEDGEHOG_G2E_SELECTIVE_RECOMPUTATION_PLAN_ACCEPTED_ARTIFACT_V01",
    ),
    ("ContinuousDeltaRuntimeReport", "FINALIZED"): (
        "EVIDENCE_ONLY", "g2eabi_report_v01:",
        "HEDGEHOG_G2E_CONTINUOUS_DELTA_RUNTIME_REPORT_ARTIFACT_V01",
    ),
}


def _g2e_time_envelope() -> dict[str, object]:
    return {
        "ct_session_anchor": "session:g2e:transition",
        "et_observed_at": "2026-08-11T01:00:00+00:00",
        "freshness_class": "normal",
        "kt_asof": "2026-08-11T01:00:00+00:00",
        "pt_created_at": "2026-08-11T01:00:00+00:00",
        "ttl_seconds": 3600,
        "valid_from": "2026-08-11T00:00:00+00:00",
        "valid_to": "2026-08-12T00:00:00+00:00",
    }


def _g2e_artifact(
    *,
    artifact_type: str,
    lifecycle_state: str,
    label: str,
    payload: dict[str, object],
    trace_refs: tuple[str, ...],
    parent_refs: tuple[str, ...] = (),
) -> object:
    profile = _G2E_ARTIFACT_PROFILES.get((artifact_type, lifecycle_state))
    if profile is None:
        authority = (
            "ROOT_OWNED"
            if artifact_type == "RootDecision"
            else "EVIDENCE_ONLY"
            if artifact_type in {"FractalRuntimeReport", "ContinuousDeltaRuntimeReport"}
            else "ADVISORY"
        )
        source_component = (
            "root_decision_v01"
            if artifact_type == "RootDecision"
            else "fractal_runtime_v02"
            if artifact_type == "FractalRuntimeReport"
            else "continuous_delta_runtime_v01"
        )
        artifact_id = "artifact:g2e:transition:" + label
    else:
        authority, prefix, domain = profile
        source_component = "continuous_delta_runtime_v01"
        material = {
            "abi_version": "v1.0",
            "artifact_type": artifact_type,
            "schema_version": "v0.1",
            "transaction_id": "transaction:g2e:transition",
            "owner_root_id": "root:g2e:transition",
            "source_component": source_component,
            "authority_class": authority,
            "lifecycle_state": lifecycle_state,
            "payload": payload,
            "trace_refs": list(trace_refs),
            "parent_refs": list(parent_refs),
            "time_envelope": _g2e_time_envelope(),
        }
        artifact_id = prefix + domain_separated_sha256_hex_v01(
            domain=domain, payload=canonical_json_bytes_v01(material)
        )
    return build_kernel_artifact_v01(
        abi_version="v1.0",
        artifact_id=artifact_id,
        artifact_type=artifact_type,
        schema_version="v0.1",
        transaction_id="transaction:g2e:transition",
        owner_root_id="root:g2e:transition",
        source_component=source_component,
        authority_class=authority,
        lifecycle_state=lifecycle_state,
        payload=payload,
        trace_refs=trace_refs,
        parent_refs=parent_refs,
        time_envelope=_g2e_time_envelope(),
    )


def _g2e_decision(
    registry: object, rule_index: int,
) -> object:
    rule = registry.rules[rule_index]
    return transition.lookup_transition_v01(
        registry=registry,
        abi_major_version=rule.abi_major_version,
        source_artifact_type=rule.source_artifact_type,
        source_lifecycle_state=rule.source_lifecycle_state,
        actor_role=rule.actor_role,
        attempted_effect=rule.attempted_effect,
        target_artifact_type=rule.target_artifact_type,
        satisfied_guards=rule.required_guards,
        root_commit_present=rule.root_commit_required,
    )


def _g2e_artifact_pair(registry: object, rule_index: int) -> tuple[object, ...]:
    rule = registry.rules[rule_index]
    target_lifecycle = dict(
        transition._CONTINUOUS_DELTA_TARGET_LIFECYCLE_BY_RULE_V01
    )[rule.rule_id]
    delta_id = "g2e_world_state_delta_v01:" + "1" * 64
    graph_id = "g2e_dependency_graph_index_v01:" + "2" * 64
    source_payload = {"delta_id": delta_id, "profile": rule.rule_id}
    source = _g2e_artifact(
        artifact_type=rule.source_artifact_type,
        lifecycle_state=rule.source_lifecycle_state,
        label=rule.rule_id + ":source",
        payload=source_payload,
        trace_refs=("trace:" + rule.rule_id + ":source",),
    )
    decision = _g2e_decision(registry, rule_index)
    if rule_index == 0:
        target_payload = source_payload
        target_parents = (source.artifact_id, "artifact:route", "artifact:report")
        target_traces = (source.artifact_id, decision.decision_id)
    elif rule_index == 1:
        target_payload = {"delta_id": delta_id, "graph_id": graph_id}
        target_parents = (source.artifact_id, "g2eabi_graph_v01:" + "3" * 64)
        target_traces = (decision.decision_id, delta_id, graph_id)
    else:
        target_payload = {"profile": rule.rule_id, "decision": decision.decision}
        target_parents = (source.artifact_id,)
        target_traces = ("trace:" + rule.rule_id + ":target",)
    target = _g2e_artifact(
        artifact_type=rule.target_artifact_type,
        lifecycle_state=target_lifecycle,
        label=rule.rule_id + ":target",
        payload=target_payload,
        trace_refs=target_traces,
        parent_refs=target_parents,
    )
    return source, target, decision


def test_g2e_transition_profile_exact_ten_rules_eleven_fields_v01() -> None:
    registry = transition.build_continuous_delta_transition_registry_profile_v01()
    actual = tuple(tuple(getattr(rule, name) for name in RULE_FIELDS) for rule in registry.rules)
    assert actual == G2E_TRANSITION_EXPECTED_ROWS
    assert len(registry.rules) == 10
    assert all(tuple(field.name for field in fields(type(rule))) == RULE_FIELDS for rule in registry.rules)
    assert transition.validate_continuous_delta_transition_registry_profile_v01(registry) == ()


def test_g2e_transition_profile_identity_plain_data_and_default_preservation_v01() -> None:
    default_before = transition.transition_registry_to_plain_dict_v01(
        transition.build_default_transition_registry_v01()
    )
    g2c_before = transition.execution_mode_transition_registry_profile_to_plain_dict_v01(
        transition.build_execution_mode_transition_registry_profile_v01()
    )
    g2d_before = transition.fractal_runtime_transition_registry_profile_to_plain_dict_v02(
        transition.build_fractal_runtime_transition_registry_profile_v02()
    )
    registry = transition.build_continuous_delta_transition_registry_profile_v01()
    plain = transition.continuous_delta_transition_registry_profile_to_plain_dict_v01(registry)
    assert canonical_json_bytes_v01(plain) == canonical_json_bytes_v01(
        transition.continuous_delta_transition_registry_profile_to_plain_dict_v01(
            transition.build_continuous_delta_transition_registry_profile_v01()
        )
    )
    assert default_before == transition.transition_registry_to_plain_dict_v01(
        transition.build_default_transition_registry_v01()
    )
    assert g2c_before == transition.execution_mode_transition_registry_profile_to_plain_dict_v01(
        transition.build_execution_mode_transition_registry_profile_v01()
    )
    assert g2d_before == transition.fractal_runtime_transition_registry_profile_to_plain_dict_v02(
        transition.build_fractal_runtime_transition_registry_profile_v02()
    )
    wrong_id = replace(registry, registry_id="0" * 64)
    assert transition.validate_continuous_delta_transition_registry_profile_v01(
        wrong_id
    ) == ("g2e_identity_mismatch",)


def test_g2e_transition_profile_complete_field_mutation_matrix_v01() -> None:
    registry = transition.build_continuous_delta_transition_registry_profile_v01()
    replacements = {
        "rule_id": "g2e_mutated_rule",
        "abi_major_version": 2,
        "source_artifact_type": "ResultProposal",
        "source_lifecycle_state": "FINALIZED",
        "actor_role": "executor_fractal_child",
        "attempted_effect": "RECORD_EVIDENCE",
        "target_artifact_type": "ResultProposal",
        "required_guards": ("artifact_valid",),
        "decision": "NEEDS_USER",
        "reason_code": "result_proposal_allows_post_vv",
        "root_commit_required": None,
    }
    for rule_index, rule in enumerate(registry.rules):
        for field_name in RULE_FIELDS:
            replacement = replacements[field_name]
            if field_name == "root_commit_required":
                replacement = not rule.root_commit_required
            mutated_rule = replace(rule, **{field_name: replacement})
            rules = list(registry.rules)
            rules[rule_index] = mutated_rule
            mutated = replace(registry, rules=tuple(rules))
            assert transition.validate_continuous_delta_transition_registry_profile_v01(
                mutated
            ) == ("g2e_object_invalid",)
    for rules in (
        registry.rules[:-1],
        registry.rules + (registry.rules[-1],),
        tuple(reversed(registry.rules)),
    ):
        assert transition.validate_continuous_delta_transition_registry_profile_v01(
            replace(registry, rules=rules)
        ) == ("g2e_object_invalid",)


def test_g2e_transition_t01_source_validation_contextual_contract_v01() -> None:
    registry = transition.build_continuous_delta_transition_registry_profile_v01()
    source, target, decision = _g2e_artifact_pair(registry, 0)
    assert transition.validate_continuous_delta_transition_decision_v01(
        decision,
        registry=registry,
        source_artifact=source,
        target_artifact=target,
    ) == ()
    assert source.artifact_id != target.artifact_id
    assert kernel_artifact_to_plain_dict_v01(source)["payload"] == (
        kernel_artifact_to_plain_dict_v01(target)["payload"]
    )
    forged = _g2e_artifact(
        artifact_type="ContinuousDeltaSource",
        lifecycle_state="VALIDATED",
        label="t01:forged",
        payload={"delta_id": "different"},
        trace_refs=(source.artifact_id, decision.decision_id),
        parent_refs=(source.artifact_id,),
    )
    assert transition.validate_continuous_delta_transition_decision_v01(
        decision,
        registry=registry,
        source_artifact=source,
        target_artifact=forged,
    ) == ("g2e_object_invalid",)


def test_g2e_transition_t02_affected_set_contextual_contract_v01() -> None:
    registry = transition.build_continuous_delta_transition_registry_profile_v01()
    source, target, decision = _g2e_artifact_pair(registry, 1)
    assert transition.validate_continuous_delta_transition_decision_v01(
        decision,
        registry=registry,
        source_artifact=source,
        target_artifact=target,
    ) == ()
    forged = _g2e_artifact(
        artifact_type="AffectedSetResult",
        lifecycle_state="VALIDATED",
        label="t02:forged",
        payload={
            "delta_id": "g2e_world_state_delta_v01:" + "9" * 64,
            "graph_id": "g2e_dependency_graph_index_v01:" + "2" * 64,
        },
        trace_refs=target.trace_refs,
        parent_refs=target.parent_refs,
    )
    assert transition.validate_continuous_delta_transition_decision_v01(
        decision,
        registry=registry,
        source_artifact=source,
        target_artifact=forged,
    ) == ("g2e_object_invalid",)


def test_g2e_transition_future_rows_are_structural_only_v01() -> None:
    registry = transition.build_continuous_delta_transition_registry_profile_v01()
    for rule_index in range(2, 10):
        source, target, decision = _g2e_artifact_pair(registry, rule_index)
        assert transition.validate_continuous_delta_transition_decision_v01(
            decision,
            registry=registry,
            source_artifact=source,
            target_artifact=target,
        ) == ()
    source_text = MODULE_PATH.read_text(encoding="utf-8")
    assert "from hedgehog.kernel.continuous_delta_runtime_v01" not in source_text
    assert "from hedgehog.kernel.root_decision_v01" not in source_text


def test_g2e_transition_terminal_and_root_commit_geometry_v01() -> None:
    registry = transition.build_continuous_delta_transition_registry_profile_v01()
    decisions = tuple(_g2e_decision(registry, index) for index in range(10))
    assert tuple(decisions[index].decision for index in (3, 8)) == (
        "RETURN_TO_ROOT",
        "RETURN_TO_ROOT",
    )
    assert tuple(decisions[index].decision for index in (5, 7)) == (
        "BLOCKED_FAIL_CLOSED",
        "BLOCKED_FAIL_CLOSED",
    )
    assert tuple(decisions[index].decision for index in (0, 1, 2, 4, 6, 9)) == (
        "ALLOW",
    ) * 6
    assert tuple(decision.root_commit_required for decision in decisions) == tuple(
        row[-1] for row in G2E_TRANSITION_EXPECTED_ROWS
    )
    assert tuple(decision.root_commit_present for decision in decisions) == tuple(
        row[-1] for row in G2E_TRANSITION_EXPECTED_ROWS
    )


def test_g2e_transition_public_surface_import_and_zero_authority_v01() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    public_functions = tuple(
        node.name
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and not node.name.startswith("_")
    )
    expected = (
        "build_continuous_delta_transition_registry_profile_v01",
        "validate_continuous_delta_transition_registry_profile_v01",
        "continuous_delta_transition_registry_profile_to_plain_dict_v01",
        "validate_continuous_delta_transition_decision_v01",
        "continuous_delta_transition_decision_to_plain_dict_v01",
        "rebuild_continuous_delta_transition_decision_identity_v01",
    )
    assert public_functions[-6:] == expected
    assert not set(expected).intersection(kernel_package.__all__)
    for name in expected:
        assert getattr(kernel_package, name) is getattr(transition, name)
    registry = transition.build_continuous_delta_transition_registry_profile_v01()
    source_artifact, target_artifact, decision = _g2e_artifact_pair(registry, 0)
    assert source_artifact.authority_class == "NON_AUTHORITY"
    assert target_artifact.authority_class == "NON_AUTHORITY"
    assert transition.continuous_delta_transition_decision_to_plain_dict_v01(
        decision
    )["decision_id"] == decision.decision_id
    assert transition.rebuild_continuous_delta_transition_decision_identity_v01(
        decision
    ) == decision.decision_id
    assert not any("authority" in field.name for field in fields(type(decision)))
