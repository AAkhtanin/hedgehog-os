"""Pure in-memory deterministic domain-neutral transition lookup for G1-C1.

The registry is immutable after construction and performs lookup only. It does
not mutate artifacts, execute transitions, call a provider or LLM, use a
network, filesystem, clock, random source, or domain import, dynamically
register policy, create permission, create a Root decision or FinalOutput, or
execute an effect. Unknown transitions fail closed.
"""

from __future__ import annotations

from dataclasses import dataclass as _dataclass
import re as _re
import unicodedata as _unicodedata

from hedgehog.kernel.abi_v01 import (
    ACTION_PACKET_LIFECYCLE_PROFILE_ID_V01,
    ACTION_PACKET_LIFECYCLE_STATES_V01,
    ARTIFACT_TYPES as _ARTIFACT_TYPES,
    KernelArtifactV01,
    LIFECYCLE_STATES as _LIFECYCLE_STATES,
    build_action_packet_lifecycle_profile_v01 as _build_action_packet_lifecycle_profile_v01,
    kernel_artifact_to_plain_dict_v01 as _kernel_artifact_to_plain_dict_v01,
    validate_kernel_artifact_v01 as _validate_kernel_artifact_v01,
    validate_action_packet_lifecycle_profile_v01 as _validate_action_packet_lifecycle_profile_v01,
)
from hedgehog.kernel.integrity_replay_v01 import (
    canonical_json_bytes_v01 as _canonical_json_bytes_v01,
    domain_separated_sha256_hex_v01 as _domain_separated_sha256_hex_v01,
)


MODULE_ID = "kernel_transition_registry_v01"
SLICE_ID = "domain_neutral_reference_kernel_gate1_g1c1"
TRANSITION_REGISTRY_VERSION = "v0.1"
SUPPORTED_ABI_MAJOR_VERSIONS = (1,)

STATUS_PASS = "PASS"
STATUS_BLOCKED_FAIL_CLOSED = "BLOCKED_FAIL_CLOSED"

DECISION_ALLOW = "ALLOW"
DECISION_BLOCKED_FAIL_CLOSED = "BLOCKED_FAIL_CLOSED"
DECISION_RETURN_TO_ROOT = "RETURN_TO_ROOT"
DECISION_NEEDS_USER = "NEEDS_USER"
DECISION_NEEDS_MORE_EVIDENCE = "NEEDS_MORE_EVIDENCE"
TRANSITION_DECISIONS = (
    DECISION_ALLOW,
    DECISION_BLOCKED_FAIL_CLOSED,
    DECISION_RETURN_TO_ROOT,
    DECISION_NEEDS_USER,
    DECISION_NEEDS_MORE_EVIDENCE,
)

TRANSITION_ATTEMPTED_EFFECTS = (
    "CREATE_TARGET_ARTIFACT",
    "CREATE_ROOT_DECISION",
    "CREATE_PERMISSION",
    "CREATE_FINAL_OUTPUT",
    "REQUEST_EFFECT",
    "RECORD_EVIDENCE",
    "RETURN_TO_ROOT",
)

TRANSITION_GUARD_IDS = (
    "artifact_valid",
    "target_root_bound",
    "required_evidence_present",
    "hard_predicates_evaluated",
    "post_vv_passed",
    "advisory_only",
    "decision_accept",
    "user_permission_present",
    "effect_firewall_required",
    "receipt_evidence_only",
    "outcome_complete",
    "source_root_isolated",
    "finalization_policy_passed",
)

ACTION_PACKET_TRANSITION_REGISTRY_PROFILE_ID_V01 = (
    "action_packet_lifecycle_registry_profile_v01"
)
ACTION_PACKET_TRANSITION_REGISTRY_PROFILE_VERSION_V01 = "v0.1"
ACTION_PACKET_TRANSITION_REGISTRY_DOMAIN_V01 = (
    "HEDGEHOG_ACTION_PACKET_TRANSITION_REGISTRY_V01"
)
ACTION_PACKET_TRANSITION_REGISTRY_PREFIX_V01 = "acptr_v01:"

ACTION_PACKET_TRANSITION_CLASS_CODES_V01 = (
    "LIFECYCLE_ACTIVATION",
    "DETERMINISTIC",
    "DETERMINISTIC_CONSUMING",
    "AUTHORITY_CHANGE",
    "DETERMINISTIC_UNCERTAIN",
)
ACTION_PACKET_PERMITTED_COMPONENT_CODES_V01 = (
    "lifecycle_runtime",
    "exclusive_corridor",
    "receipt_observer",
    "temporal_validator",
    "owning_local_root",
)
ACTION_PACKET_ROOT_DECISION_REQUIREMENT_CODES_V01 = (
    "NONE",
    "EXISTING_SOURCE_AUTHORIZATION",
    "NEW_ROOT_REVOCATION_DECISION",
    "NEW_ROOT_SUPERSESSION_DECISION",
)
ACTION_PACKET_EFFECT_CONSUMPTION_CLASSES_V01 = (
    "NOT_CONSUMED",
    "CONSUMED",
    "UNCERTAIN",
)
ACTION_PACKET_ADAPTER_INVOCATION_RELATION_CODES_V01 = (
    "NO_ADAPTER_INVOCATION",
    "CORRIDOR_INVOCATION_CONSUMED",
    "CORRIDOR_INVOCATION_NONCONSUMING",
    "CORRIDOR_INVOCATION_UNCERTAIN",
    "POST_INVOCATION_RECEIPT_OBSERVATION",
)
ACTION_PACKET_TRANSITION_RULE_IDS_V01 = (
    "g2a_t01_activate_root_authorization",
    "g2a_t02_queue",
    "g2a_t03_pending",
    "g2a_t04_fulfill_mock",
    "g2a_t05_receipt",
    "g2a_t06_created_block",
    "g2a_t07_authorized_block",
    "g2a_t08_queued_block",
    "g2a_t09_pending_block",
    "g2a_t10_failed_block",
    "g2a_t11_created_expire",
    "g2a_t12_authorized_expire",
    "g2a_t13_queued_expire",
    "g2a_t14_pending_expire",
    "g2a_t15_failed_expire",
    "g2a_t16_authorized_revoke",
    "g2a_t17_queued_revoke",
    "g2a_t18_pending_revoke",
    "g2a_t19_failed_revoke",
    "g2a_t20_authorized_supersede",
    "g2a_t21_queued_supersede",
    "g2a_t22_pending_supersede",
    "g2a_t23_failed_supersede",
    "g2a_t24_nonconsuming_failure",
    "g2a_t25_retry",
    "g2a_t26_uncertain_adapter_outcome",
)
ACTION_PACKET_REQUIRED_EVIDENCE_CODES_V01 = (
    "packet_genesis_valid",
    "source_root_authorization_valid",
    "idempotency_acquisition_valid",
    "transition_history_valid",
    "temporal_authority_valid",
    "mandatory_dependencies_current",
    "idempotency_reservation_owned",
    "immediate_prefulfillment_validation_pass",
    "mock_adapter_result_valid",
    "effect_consumption_evidence_valid",
    "terminal_receipt_valid",
    "fulfillment_consumption_evidence_valid",
    "blocking_evidence_valid",
    "authority_policy_valid",
    "immediate_eligibility_failure_valid",
    "adapter_not_called",
    "failed_non_consuming_provenance_valid",
    "retry_ineligibility_evidence_valid",
    "evaluation_time_valid",
    "immediate_temporal_validation_pass",
    "accepted_revocation_binding_valid",
    "source_authorization_binding_valid",
    "successor_packet_valid",
    "accepted_supersession_binding_valid",
    "predecessor_binding_valid",
    "idempotency_transfer_valid",
    "adapter_invocation_evidence_valid",
    "effect_nonconsumption_evidence_valid",
    "latest_disposition_event_binding_valid",
    "retry_policy_valid",
    "current_eligibility_valid",
    "effect_outcome_unresolved",
)
ACTION_PACKET_TRANSITION_REASON_CODES_V01 = (
    "root_authorization_activated",
    "packet_queued",
    "pending_fulfillment",
    "fulfilled_mock",
    "receipt_received",
    "packet_blocked",
    "packet_expired",
    "packet_revoked",
    "packet_superseded",
    "fulfillment_failed_nonconsuming",
    "nonconsuming_retry_queued",
    "fulfillment_failed_consumption_uncertain",
)
ACTION_PACKET_FAIL_CLOSED_REASON_CODES_V01 = (
    "packet_genesis_invalid",
    "source_root_authorization_invalid",
    "wrong_owning_root",
    "idempotency_acquisition_invalid",
    "packet_non_executable",
    "transition_history_invalid",
    "temporal_authority_invalid",
    "mandatory_dependency_invalid",
    "idempotency_reservation_invalid",
    "current_eligibility_invalid",
    "adapter_call_failed",
    "effect_consumption_evidence_missing",
    "current_eligibility_changed",
    "receipt_invalid",
    "packet_binding_mismatch",
    "idempotency_binding_mismatch",
    "receipt_authority_claimed",
    "consumption_evidence_missing",
    "blocking_evidence_missing",
    "authority_expansion_detected",
    "authority_policy_invalid",
    "adapter_already_called",
    "failed_provenance_invalid",
    "retry_ineligibility_evidence_missing",
    "evaluation_time_invalid",
    "prior_terminal_state",
    "foreign_root",
    "accepted_revocation_binding_invalid",
    "source_authorization_mismatch",
    "successor_packet_missing",
    "accepted_supersession_binding_invalid",
    "predecessor_binding_mismatch",
    "idempotency_transfer_invalid",
    "adapter_not_called",
    "effect_consumed",
    "effect_outcome_uncertain",
    "failure_evidence_missing",
    "latest_disposition_event_binding_invalid",
    "disposition_history_changed",
    "terminal_evidence_present",
    "retry_policy_invalid",
    "effect_non_consumption_proven",
    "execution_attempt_evidence_missing",
    "idempotency_binding_missing",
    "transition_event_identity_invalid",
)

_REGISTRY_DOMAIN = "hedgehog.kernel.transition_registry.v01"
_DECISION_DOMAIN = "hedgehog.kernel.transition_decision.v01"
_ACTOR_ROLES = (
    "root",
    "provider_llm",
    "orchestrator",
    "semantic_architect",
    "deterministic_runtime",
    "drs",
    "avf",
    "executor_fractal_child",
    "post_vv",
    "gt",
    "domain_adapter",
    "effect_firewall",
    "corridor_adapter",
    "receipt",
    "ledger",
    "crypto",
    "replay",
    "renderer_showcase",
)
_CANONICAL_REASONS = (
    "route_acceptance_requires_root",
    "root_accepted_route_allows_topology",
    "actor_contribution_requires_validated_evidence",
    "result_proposal_allows_post_vv",
    "post_vv_allows_gt_advisory",
    "gt_advisory_returns_to_root",
    "root_decision_allows_root_owned_intent",
    "root_decision_allows_execution_request",
    "receipt_returns_to_root",
    "root_decision_allows_root_final",
    "root_final_allows_transaction_outcome",
    "cross_root_evidence_returns_to_target_root",
    "provider_cannot_create_root_decision",
    "evidence_cannot_create_permission",
    "gt_cannot_create_final_output",
    "receipt_cannot_create_permission",
    "causal_evidence_cannot_create_root_decision",
    "domain_adapter_cannot_request_effect",
)
_LOOKUP_REASONS = (
    "unknown_abi_major",
    "unknown_transition",
    "required_guard_missing",
    "explicit_user_permission_required",
    "required_evidence_missing",
    "root_commit_required",
) + _CANONICAL_REASONS


@_dataclass(frozen=True)
class TransitionRuleV01:
    rule_id: str
    abi_major_version: int
    source_artifact_type: str
    source_lifecycle_state: str
    actor_role: str
    attempted_effect: str
    target_artifact_type: str
    required_guards: tuple[str, ...]
    decision: str
    reason_code: str
    root_commit_required: bool


@_dataclass(frozen=True)
class TransitionDecisionV01:
    decision_id: str
    registry_id: str
    rule_id: str
    abi_major_version: int
    source_artifact_type: str
    source_lifecycle_state: str
    actor_role: str
    attempted_effect: str
    target_artifact_type: str
    required_guards: tuple[str, ...]
    satisfied_guards: tuple[str, ...]
    missing_guards: tuple[str, ...]
    decision: str
    reason_code: str
    root_commit_required: bool
    root_commit_present: bool
    matched: bool


@_dataclass(frozen=True)
class TransitionRegistryV01:
    registry_id: str
    registry_version: str
    abi_major_version: int
    rules: tuple[TransitionRuleV01, ...]


@_dataclass(frozen=True)
class ActionPacketTransitionRuleV01:
    transition_rule_id: str
    source_state: str
    target_state: str
    transition_class_code: str
    permitted_component_code: str
    root_decision_requirement_code: str
    required_evidence_codes: tuple[str, ...]
    effect_consumption_class: str
    adapter_invocation_relation_code: str
    terminal_target: bool
    reason_code: str
    fail_closed_reason_codes: tuple[str, ...]


@_dataclass(frozen=True)
class ActionPacketTransitionRegistryProfileV01:
    transition_registry_id: str
    registry_profile_version: str
    lifecycle_profile_id: str
    ordered_transition_rules: tuple[ActionPacketTransitionRuleV01, ...]


def build_default_transition_registry_v01() -> TransitionRegistryV01:
    rules = _canonical_rules()
    material = {
        "registry_version": TRANSITION_REGISTRY_VERSION,
        "abi_major_version": 1,
        "rules": [_rule_plain(rule) for rule in rules],
    }
    registry_id = _hash(_REGISTRY_DOMAIN, material)
    return TransitionRegistryV01(
        registry_id=registry_id,
        registry_version=TRANSITION_REGISTRY_VERSION,
        abi_major_version=1,
        rules=rules,
    )


def validate_transition_rule_v01(rule: object) -> tuple[str, ...]:
    try:
        return _rule_errors(rule)
    except Exception:
        return ("transition_unexpected_exception",)


def validate_transition_registry_v01(registry: object) -> tuple[str, ...]:
    try:
        return _registry_errors(registry)
    except Exception:
        return ("transition_unexpected_exception",)


def lookup_transition_v01(
    *,
    registry: object,
    abi_major_version: object,
    source_artifact_type: object,
    source_lifecycle_state: object,
    actor_role: object,
    attempted_effect: object,
    target_artifact_type: object,
    satisfied_guards: object,
    root_commit_present: object,
) -> TransitionDecisionV01:
    try:
        if _registry_errors(registry) or not _lookup_input_valid(
            abi_major_version=abi_major_version,
            source_artifact_type=source_artifact_type,
            source_lifecycle_state=source_lifecycle_state,
            actor_role=actor_role,
            attempted_effect=attempted_effect,
            target_artifact_type=target_artifact_type,
            satisfied_guards=satisfied_guards,
            root_commit_present=root_commit_present,
        ):
            raise ValueError("transition_lookup_invalid")
        assert type(registry) is TransitionRegistryV01
        assert type(abi_major_version) is int
        assert type(source_artifact_type) is str
        assert type(source_lifecycle_state) is str
        assert type(actor_role) is str
        assert type(attempted_effect) is str
        assert type(target_artifact_type) is str
        assert type(satisfied_guards) is tuple
        assert type(root_commit_present) is bool

        rule = None
        if abi_major_version in SUPPORTED_ABI_MAJOR_VERSIONS:
            key = (
                abi_major_version,
                source_artifact_type,
                source_lifecycle_state,
                actor_role,
                attempted_effect,
                target_artifact_type,
            )
            for item in registry.rules:
                if _rule_key(item) == key:
                    rule = item
                    break

        if abi_major_version not in SUPPORTED_ABI_MAJOR_VERSIONS:
            return _build_decision(
                registry=registry,
                rule=None,
                abi_major_version=abi_major_version,
                source_artifact_type=source_artifact_type,
                source_lifecycle_state=source_lifecycle_state,
                actor_role=actor_role,
                attempted_effect=attempted_effect,
                target_artifact_type=target_artifact_type,
                satisfied_guards=satisfied_guards,
                root_commit_present=root_commit_present,
                decision=DECISION_BLOCKED_FAIL_CLOSED,
                reason_code="unknown_abi_major",
            )
        if rule is None:
            return _build_decision(
                registry=registry,
                rule=None,
                abi_major_version=abi_major_version,
                source_artifact_type=source_artifact_type,
                source_lifecycle_state=source_lifecycle_state,
                actor_role=actor_role,
                attempted_effect=attempted_effect,
                target_artifact_type=target_artifact_type,
                satisfied_guards=satisfied_guards,
                root_commit_present=root_commit_present,
                decision=DECISION_BLOCKED_FAIL_CLOSED,
                reason_code="unknown_transition",
            )

        missing = tuple(
            guard for guard in rule.required_guards if guard not in satisfied_guards
        )
        decision = rule.decision
        reason = rule.reason_code
        if rule.decision == DECISION_BLOCKED_FAIL_CLOSED:
            pass
        else:
            generic_missing = tuple(
                guard
                for guard in missing
                if guard
                not in {"user_permission_present", "required_evidence_present"}
            )
            if generic_missing:
                decision = DECISION_BLOCKED_FAIL_CLOSED
                reason = "required_guard_missing"
            elif "user_permission_present" in missing:
                decision = DECISION_NEEDS_USER
                reason = "explicit_user_permission_required"
            elif "required_evidence_present" in missing:
                decision = DECISION_NEEDS_MORE_EVIDENCE
                reason = "required_evidence_missing"
            elif rule.decision == DECISION_RETURN_TO_ROOT:
                pass
            elif rule.root_commit_required and not root_commit_present:
                decision = DECISION_RETURN_TO_ROOT
                reason = "root_commit_required"

        return _build_decision(
            registry=registry,
            rule=rule,
            abi_major_version=abi_major_version,
            source_artifact_type=source_artifact_type,
            source_lifecycle_state=source_lifecycle_state,
            actor_role=actor_role,
            attempted_effect=attempted_effect,
            target_artifact_type=target_artifact_type,
            satisfied_guards=satisfied_guards,
            root_commit_present=root_commit_present,
            decision=decision,
            reason_code=reason,
        )
    except ValueError as exc:
        if _stable_value_error(exc, ("transition_lookup_invalid",)):
            raise ValueError("transition_lookup_invalid") from None
        raise ValueError("transition_lookup_invalid") from None
    except Exception:
        raise ValueError("transition_lookup_invalid") from None


def validate_transition_decision_v01(
    *,
    registry: object,
    decision: object,
) -> tuple[str, ...]:
    try:
        if _registry_errors(registry):
            return ("transition_registry_invalid",)
        if type(decision) is not TransitionDecisionV01:
            return ("transition_decision_invalid",)
        if not _decision_structure_valid(decision):
            return ("transition_decision_invalid",)
        expected = lookup_transition_v01(
            registry=registry,
            abi_major_version=decision.abi_major_version,
            source_artifact_type=decision.source_artifact_type,
            source_lifecycle_state=decision.source_lifecycle_state,
            actor_role=decision.actor_role,
            attempted_effect=decision.attempted_effect,
            target_artifact_type=decision.target_artifact_type,
            satisfied_guards=decision.satisfied_guards,
            root_commit_present=decision.root_commit_present,
        )
        if decision.decision_id != _decision_id(decision):
            return ("transition_decision_id_mismatch",)
        if _canonical_bytes(_decision_plain(decision)) != _canonical_bytes(
            _decision_plain(expected)
        ):
            return ("transition_decision_invalid",)
        return ()
    except Exception:
        return ("transition_unexpected_exception",)


def transition_rule_to_plain_dict_v01(
    rule: TransitionRuleV01,
) -> dict[str, object]:
    try:
        if _rule_errors(rule):
            raise ValueError("transition_rule_invalid")
        result = _rule_plain(rule)
        _canonical_json_bytes_v01(result)
        return result
    except Exception:
        raise ValueError("transition_rule_invalid") from None


def transition_decision_to_plain_dict_v01(
    decision: TransitionDecisionV01,
) -> dict[str, object]:
    try:
        if type(decision) is not TransitionDecisionV01 or not _decision_structure_valid(
            decision
        ):
            raise ValueError("transition_decision_invalid")
        registry = build_default_transition_registry_v01()
        if validate_transition_decision_v01(
            registry=registry,
            decision=decision,
        ):
            raise ValueError("transition_decision_invalid")
        result = _decision_plain(decision)
        _canonical_json_bytes_v01(result)
        return result
    except Exception:
        raise ValueError("transition_decision_invalid") from None


def transition_registry_to_plain_dict_v01(
    registry: TransitionRegistryV01,
) -> dict[str, object]:
    try:
        if _registry_errors(registry):
            raise ValueError("transition_registry_invalid")
        result = _registry_plain(registry)
        _canonical_json_bytes_v01(result)
        return result
    except Exception:
        raise ValueError("transition_registry_invalid") from None


def _canonical_rules() -> tuple[TransitionRuleV01, ...]:
    rows = (
        ("route_proposal_to_root_accepted_route", "OrchestratorRouteProposal", "PROPOSED", "orchestrator", "CREATE_TARGET_ARTIFACT", "RootAcceptedRoute", ("artifact_valid", "target_root_bound"), DECISION_RETURN_TO_ROOT, "route_acceptance_requires_root", True),
        ("root_accepted_route_to_runtime_topology", "RootAcceptedRoute", "ROOT_ACCEPTED", "deterministic_runtime", "CREATE_TARGET_ARTIFACT", "RuntimeExecutionTopology", ("artifact_valid", "target_root_bound"), DECISION_ALLOW, "root_accepted_route_allows_topology", True),
        ("actor_contribution_to_validated_evidence", "ActorContribution", "VALIDATED", "post_vv", "CREATE_TARGET_ARTIFACT", "ValidatedEvidence", ("artifact_valid", "required_evidence_present"), DECISION_ALLOW, "actor_contribution_requires_validated_evidence", False),
        ("result_proposal_to_post_vv_report", "ResultProposal", "VALIDATED", "post_vv", "CREATE_TARGET_ARTIFACT", "PostVVReport", ("artifact_valid", "hard_predicates_evaluated"), DECISION_ALLOW, "result_proposal_allows_post_vv", False),
        ("post_vv_report_to_gt_advisory", "PostVVReport", "VALIDATED", "gt", "CREATE_TARGET_ARTIFACT", "GTAdvisoryReport", ("artifact_valid", "post_vv_passed", "advisory_only"), DECISION_ALLOW, "post_vv_allows_gt_advisory", False),
        ("gt_advisory_to_root_decision", "GTAdvisoryReport", "VALIDATED", "gt", "CREATE_ROOT_DECISION", "RootDecision", ("artifact_valid", "post_vv_passed", "advisory_only"), DECISION_RETURN_TO_ROOT, "gt_advisory_returns_to_root", True),
        ("root_decision_to_root_owned_intent", "RootDecision", "ROOT_ACCEPTED", "root", "CREATE_TARGET_ARTIFACT", "RootOwnedIntent", ("artifact_valid", "decision_accept"), DECISION_ALLOW, "root_decision_allows_root_owned_intent", True),
        ("root_decision_to_execution_request", "RootDecision", "ROOT_ACCEPTED", "root", "CREATE_TARGET_ARTIFACT", "ExecutionRequest", ("artifact_valid", "decision_accept", "user_permission_present", "effect_firewall_required"), DECISION_ALLOW, "root_decision_allows_execution_request", True),
        ("evidence_receipt_to_root_review", "EvidenceReceipt", "RECEIPT_RECORDED", "receipt", "RETURN_TO_ROOT", "RootDecision", ("artifact_valid", "receipt_evidence_only"), DECISION_RETURN_TO_ROOT, "receipt_returns_to_root", True),
        ("root_decision_to_root_final", "RootDecision", "ROOT_ACCEPTED", "root", "CREATE_FINAL_OUTPUT", "RootFinal", ("artifact_valid", "decision_accept", "finalization_policy_passed"), DECISION_ALLOW, "root_decision_allows_root_final", True),
        ("root_final_to_transaction_outcome", "RootFinal", "FINALIZED", "root", "RECORD_EVIDENCE", "TransactionOutcomeEnvelope", ("artifact_valid", "outcome_complete"), DECISION_ALLOW, "root_final_allows_transaction_outcome", True),
        ("cross_root_evidence_to_root_review", "CrossRootEvidenceRef", "VALIDATED", "root", "RETURN_TO_ROOT", "RootDecision", ("artifact_valid", "source_root_isolated", "target_root_bound"), DECISION_RETURN_TO_ROOT, "cross_root_evidence_returns_to_target_root", True),
        ("provider_contribution_to_root_decision_forbidden", "ActorContribution", "VALIDATED", "provider_llm", "CREATE_ROOT_DECISION", "RootDecision", (), DECISION_BLOCKED_FAIL_CLOSED, "provider_cannot_create_root_decision", False),
        ("drs_evidence_to_permission_forbidden", "SemanticEvidence", "VALIDATED", "drs", "CREATE_PERMISSION", "ExecutionRequest", (), DECISION_BLOCKED_FAIL_CLOSED, "evidence_cannot_create_permission", False),
        ("gt_advisory_to_root_final_forbidden", "GTAdvisoryReport", "VALIDATED", "gt", "CREATE_FINAL_OUTPUT", "RootFinal", (), DECISION_BLOCKED_FAIL_CLOSED, "gt_cannot_create_final_output", False),
        ("receipt_to_permission_forbidden", "EvidenceReceipt", "RECEIPT_RECORDED", "receipt", "CREATE_PERMISSION", "ExecutionRequest", (), DECISION_BLOCKED_FAIL_CLOSED, "receipt_cannot_create_permission", False),
        ("causal_evidence_to_root_decision_forbidden", "CausalConsumptionRef", "VALIDATED", "replay", "CREATE_ROOT_DECISION", "RootDecision", (), DECISION_BLOCKED_FAIL_CLOSED, "causal_evidence_cannot_create_root_decision", False),
        ("domain_adapter_effect_request_forbidden", "RootDecision", "ROOT_ACCEPTED", "domain_adapter", "REQUEST_EFFECT", "ExecutionRequest", (), DECISION_BLOCKED_FAIL_CLOSED, "domain_adapter_cannot_request_effect", False),
    )
    return tuple(
        TransitionRuleV01(
            rule_id=row[0],
            abi_major_version=1,
            source_artifact_type=row[1],
            source_lifecycle_state=row[2],
            actor_role=row[3],
            attempted_effect=row[4],
            target_artifact_type=row[5],
            required_guards=row[6],
            decision=row[7],
            reason_code=row[8],
            root_commit_required=row[9],
        )
        for row in rows
    )


def _valid_text(value: object) -> bool:
    if type(value) is not str or not value:
        return False
    try:
        value.encode("utf-8", errors="strict")
    except UnicodeError:
        return False
    return not any(0xD800 <= ord(char) <= 0xDFFF for char in value)


def _valid_text_tuple(value: object, *, allow_empty: bool) -> bool:
    return (
        type(value) is tuple
        and (allow_empty or bool(value))
        and all(_valid_text(item) for item in value)
        and len(set(value)) == len(value)
    )


def _rule_errors(rule: object) -> tuple[str, ...]:
    if type(rule) is not TransitionRuleV01:
        return ("transition_rule_invalid",)
    errors: list[str] = []
    if not _valid_text(rule.rule_id):
        errors.append("transition_rule_invalid")
    if type(rule.abi_major_version) is not int:
        errors.append("transition_rule_invalid")
    elif rule.abi_major_version not in SUPPORTED_ABI_MAJOR_VERSIONS:
        errors.append("transition_abi_major_unknown")
    if type(rule.source_artifact_type) is not str or rule.source_artifact_type not in _ARTIFACT_TYPES:
        errors.append("transition_artifact_type_unknown")
    if type(rule.target_artifact_type) is not str or rule.target_artifact_type not in _ARTIFACT_TYPES:
        errors.append("transition_artifact_type_unknown")
    if type(rule.source_lifecycle_state) is not str or rule.source_lifecycle_state not in _LIFECYCLE_STATES:
        errors.append("transition_lifecycle_state_unknown")
    if type(rule.actor_role) is not str or rule.actor_role not in _ACTOR_ROLES:
        errors.append("transition_actor_role_unknown")
    if type(rule.attempted_effect) is not str or rule.attempted_effect not in TRANSITION_ATTEMPTED_EFFECTS:
        errors.append("transition_attempted_effect_unknown")
    if not _valid_text_tuple(rule.required_guards, allow_empty=True):
        errors.append("transition_rule_invalid")
    elif any(guard not in TRANSITION_GUARD_IDS for guard in rule.required_guards):
        errors.append("transition_guard_unknown")
    if type(rule.decision) is not str or rule.decision not in TRANSITION_DECISIONS:
        errors.append("transition_decision_unknown")
    if type(rule.reason_code) is not str or rule.reason_code not in _CANONICAL_REASONS:
        errors.append("transition_reason_unknown")
    if type(rule.root_commit_required) is not bool:
        errors.append("transition_rule_invalid")
    if not errors:
        canonical = tuple(_rule_plain(item) for item in _canonical_rules())
        if _rule_plain(rule) not in canonical:
            errors.append("transition_rule_invalid")
    return _dedupe(errors)


def _registry_errors(registry: object) -> tuple[str, ...]:
    if type(registry) is not TransitionRegistryV01:
        return ("transition_registry_invalid",)
    errors: list[str] = []
    if not _valid_text(registry.registry_id):
        errors.append("transition_registry_invalid")
    if type(registry.registry_version) is not str or registry.registry_version != TRANSITION_REGISTRY_VERSION:
        errors.append("transition_registry_invalid")
    if type(registry.abi_major_version) is not int:
        errors.append("transition_registry_invalid")
    elif registry.abi_major_version not in SUPPORTED_ABI_MAJOR_VERSIONS:
        errors.append("transition_abi_major_unknown")
    if type(registry.rules) is not tuple:
        errors.append("transition_registry_invalid")
        return _dedupe(errors)
    for rule in registry.rules:
        errors.extend(_rule_errors(rule))
    ids = tuple(rule.rule_id for rule in registry.rules if type(rule) is TransitionRuleV01 and type(rule.rule_id) is str)
    if len(set(ids)) != len(ids):
        errors.append("transition_rule_id_duplicate")
    keys = tuple(_rule_key(rule) for rule in registry.rules if type(rule) is TransitionRuleV01)
    if len(set(keys)) != len(keys):
        errors.append("transition_lookup_key_duplicate")
    expected = _canonical_rules()
    expected_ids = tuple(rule.rule_id for rule in expected)
    if set(ids) != set(expected_ids):
        errors.append("transition_rule_set_mismatch")
    elif ids != expected_ids:
        errors.append("transition_rule_order_mismatch")
    if len(registry.rules) == len(expected):
        try:
            if _canonical_bytes([_rule_plain(rule) for rule in registry.rules]) != _canonical_bytes([_rule_plain(rule) for rule in expected]):
                errors.append("transition_rule_set_mismatch")
        except Exception:
            errors.append("transition_registry_invalid")
    expected_material = {
        "registry_version": TRANSITION_REGISTRY_VERSION,
        "abi_major_version": 1,
        "rules": [_rule_plain(rule) for rule in expected],
    }
    if registry.registry_id != _hash(_REGISTRY_DOMAIN, expected_material):
        errors.append("transition_registry_id_mismatch")
    return _dedupe(errors)


def _lookup_input_valid(**values: object) -> bool:
    try:
        if type(values["abi_major_version"]) is not int:
            return False
        for name in (
            "source_artifact_type",
            "source_lifecycle_state",
            "actor_role",
            "attempted_effect",
            "target_artifact_type",
        ):
            if not _valid_text(values[name]):
                return False
        guards = values["satisfied_guards"]
        if not _valid_text_tuple(guards, allow_empty=True):
            return False
        if any(guard not in TRANSITION_GUARD_IDS for guard in guards):
            return False
        return type(values["root_commit_present"]) is bool
    except Exception:
        return False


def _build_decision(
    *,
    registry: TransitionRegistryV01,
    rule: TransitionRuleV01 | None,
    abi_major_version: int,
    source_artifact_type: str,
    source_lifecycle_state: str,
    actor_role: str,
    attempted_effect: str,
    target_artifact_type: str,
    satisfied_guards: tuple[str, ...],
    root_commit_present: bool,
    decision: str,
    reason_code: str,
) -> TransitionDecisionV01:
    required = () if rule is None else rule.required_guards
    missing = tuple(guard for guard in required if guard not in satisfied_guards)
    fields = {
        "registry_id": registry.registry_id,
        "rule_id": "UNMATCHED" if rule is None else rule.rule_id,
        "abi_major_version": abi_major_version,
        "source_artifact_type": source_artifact_type,
        "source_lifecycle_state": source_lifecycle_state,
        "actor_role": actor_role,
        "attempted_effect": attempted_effect,
        "target_artifact_type": target_artifact_type,
        "required_guards": list(required),
        "satisfied_guards": list(satisfied_guards),
        "missing_guards": list(missing),
        "decision": decision,
        "reason_code": reason_code,
        "root_commit_required": False if rule is None else rule.root_commit_required,
        "root_commit_present": root_commit_present,
        "matched": rule is not None,
    }
    decision_id = _hash(_DECISION_DOMAIN, fields)
    return TransitionDecisionV01(
        decision_id=decision_id,
        registry_id=registry.registry_id,
        rule_id=fields["rule_id"],
        abi_major_version=abi_major_version,
        source_artifact_type=source_artifact_type,
        source_lifecycle_state=source_lifecycle_state,
        actor_role=actor_role,
        attempted_effect=attempted_effect,
        target_artifact_type=target_artifact_type,
        required_guards=required,
        satisfied_guards=satisfied_guards,
        missing_guards=missing,
        decision=decision,
        reason_code=reason_code,
        root_commit_required=fields["root_commit_required"],
        root_commit_present=root_commit_present,
        matched=rule is not None,
    )


def _decision_structure_valid(decision: TransitionDecisionV01) -> bool:
    if not all(
        _valid_text(value)
        for value in (
            decision.decision_id,
            decision.registry_id,
            decision.rule_id,
            decision.source_artifact_type,
            decision.source_lifecycle_state,
            decision.actor_role,
            decision.attempted_effect,
            decision.target_artifact_type,
            decision.reason_code,
        )
    ):
        return False
    if type(decision.abi_major_version) is not int:
        return False
    if not all(
        _valid_text_tuple(value, allow_empty=True)
        for value in (
            decision.required_guards,
            decision.satisfied_guards,
            decision.missing_guards,
        )
    ):
        return False
    if any(guard not in TRANSITION_GUARD_IDS for guard in decision.required_guards + decision.satisfied_guards + decision.missing_guards):
        return False
    if type(decision.decision) is not str or decision.decision not in TRANSITION_DECISIONS:
        return False
    if decision.reason_code not in _LOOKUP_REASONS:
        return False
    return all(
        type(value) is bool
        for value in (
            decision.root_commit_required,
            decision.root_commit_present,
            decision.matched,
        )
    )


def _decision_id(decision: TransitionDecisionV01) -> str:
    material = _decision_plain(decision)
    material.pop("decision_id")
    return _hash(_DECISION_DOMAIN, material)


def _rule_key(rule: TransitionRuleV01) -> tuple[object, ...]:
    return (
        rule.abi_major_version,
        rule.source_artifact_type,
        rule.source_lifecycle_state,
        rule.actor_role,
        rule.attempted_effect,
        rule.target_artifact_type,
    )


def _rule_plain(rule: TransitionRuleV01) -> dict[str, object]:
    return {
        "rule_id": rule.rule_id,
        "abi_major_version": rule.abi_major_version,
        "source_artifact_type": rule.source_artifact_type,
        "source_lifecycle_state": rule.source_lifecycle_state,
        "actor_role": rule.actor_role,
        "attempted_effect": rule.attempted_effect,
        "target_artifact_type": rule.target_artifact_type,
        "required_guards": list(rule.required_guards),
        "decision": rule.decision,
        "reason_code": rule.reason_code,
        "root_commit_required": rule.root_commit_required,
    }


def _decision_plain(decision: TransitionDecisionV01) -> dict[str, object]:
    return {
        "decision_id": decision.decision_id,
        "registry_id": decision.registry_id,
        "rule_id": decision.rule_id,
        "abi_major_version": decision.abi_major_version,
        "source_artifact_type": decision.source_artifact_type,
        "source_lifecycle_state": decision.source_lifecycle_state,
        "actor_role": decision.actor_role,
        "attempted_effect": decision.attempted_effect,
        "target_artifact_type": decision.target_artifact_type,
        "required_guards": list(decision.required_guards),
        "satisfied_guards": list(decision.satisfied_guards),
        "missing_guards": list(decision.missing_guards),
        "decision": decision.decision,
        "reason_code": decision.reason_code,
        "root_commit_required": decision.root_commit_required,
        "root_commit_present": decision.root_commit_present,
        "matched": decision.matched,
    }


def _registry_plain(registry: TransitionRegistryV01) -> dict[str, object]:
    return {
        "registry_id": registry.registry_id,
        "registry_version": registry.registry_version,
        "abi_major_version": registry.abi_major_version,
        "rules": [_rule_plain(rule) for rule in registry.rules],
    }


def _hash(domain: str, value: object) -> str:
    return _domain_separated_sha256_hex_v01(
        domain=domain,
        payload=_canonical_json_bytes_v01(value),
    )


def _canonical_bytes(value: object) -> bytes:
    return _canonical_json_bytes_v01(value)


def _stable_value_error(error: ValueError, allowed: tuple[str, ...]) -> bool:
    return len(error.args) == 1 and type(error.args[0]) is str and error.args[0] in allowed


def _dedupe(values: list[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))


_ACTION_PACKET_TRANSITION_RULE_ROWS_V01 = (
    (
        "g2a_t01_activate_root_authorization",
        "CREATED",
        "ROOT_AUTHORIZED",
        "LIFECYCLE_ACTIVATION",
        "lifecycle_runtime",
        "EXISTING_SOURCE_AUTHORIZATION",
        (
            "packet_genesis_valid",
            "source_root_authorization_valid",
            "idempotency_acquisition_valid",
        ),
        "NOT_CONSUMED",
        "NO_ADAPTER_INVOCATION",
        False,
        "root_authorization_activated",
        (
            "packet_genesis_invalid",
            "source_root_authorization_invalid",
            "wrong_owning_root",
            "idempotency_acquisition_invalid",
        ),
    ),
    (
        "g2a_t02_queue",
        "ROOT_AUTHORIZED",
        "QUEUED",
        "DETERMINISTIC",
        "lifecycle_runtime",
        "NONE",
        (
            "transition_history_valid",
            "temporal_authority_valid",
            "mandatory_dependencies_current",
            "idempotency_reservation_owned",
        ),
        "NOT_CONSUMED",
        "NO_ADAPTER_INVOCATION",
        False,
        "packet_queued",
        (
            "packet_non_executable",
            "transition_history_invalid",
            "temporal_authority_invalid",
            "mandatory_dependency_invalid",
            "idempotency_reservation_invalid",
        ),
    ),
    (
        "g2a_t03_pending",
        "QUEUED",
        "PENDING_FULFILLMENT",
        "DETERMINISTIC",
        "exclusive_corridor",
        "NONE",
        (
            "immediate_prefulfillment_validation_pass",
            "transition_history_valid",
            "idempotency_reservation_owned",
        ),
        "NOT_CONSUMED",
        "NO_ADAPTER_INVOCATION",
        False,
        "pending_fulfillment",
        (
            "current_eligibility_invalid",
            "transition_history_invalid",
            "idempotency_reservation_invalid",
        ),
    ),
    (
        "g2a_t04_fulfill_mock",
        "PENDING_FULFILLMENT",
        "FULFILLED_MOCK",
        "DETERMINISTIC_CONSUMING",
        "exclusive_corridor",
        "NONE",
        (
            "mock_adapter_result_valid",
            "effect_consumption_evidence_valid",
            "idempotency_reservation_owned",
        ),
        "CONSUMED",
        "CORRIDOR_INVOCATION_CONSUMED",
        False,
        "fulfilled_mock",
        (
            "adapter_call_failed",
            "effect_consumption_evidence_missing",
            "current_eligibility_changed",
            "idempotency_reservation_invalid",
        ),
    ),
    (
        "g2a_t05_receipt",
        "FULFILLED_MOCK",
        "RECEIPT_RECEIVED",
        "DETERMINISTIC_CONSUMING",
        "receipt_observer",
        "NONE",
        (
            "terminal_receipt_valid",
            "fulfillment_consumption_evidence_valid",
        ),
        "CONSUMED",
        "POST_INVOCATION_RECEIPT_OBSERVATION",
        True,
        "receipt_received",
        (
            "receipt_invalid",
            "packet_binding_mismatch",
            "idempotency_binding_mismatch",
            "receipt_authority_claimed",
            "consumption_evidence_missing",
        ),
    ),
    (
        "g2a_t06_created_block",
        "CREATED",
        "BLOCKED",
        "DETERMINISTIC",
        "lifecycle_runtime",
        "NONE",
        ("packet_genesis_valid", "blocking_evidence_valid"),
        "NOT_CONSUMED",
        "NO_ADAPTER_INVOCATION",
        True,
        "packet_blocked",
        (
            "packet_genesis_invalid",
            "blocking_evidence_missing",
            "authority_expansion_detected",
        ),
    ),
    (
        "g2a_t07_authorized_block",
        "ROOT_AUTHORIZED",
        "BLOCKED",
        "DETERMINISTIC",
        "lifecycle_runtime",
        "NONE",
        (
            "blocking_evidence_valid",
            "authority_policy_valid",
            "idempotency_reservation_owned",
        ),
        "NOT_CONSUMED",
        "NO_ADAPTER_INVOCATION",
        True,
        "packet_blocked",
        (
            "blocking_evidence_missing",
            "authority_expansion_detected",
            "authority_policy_invalid",
            "idempotency_reservation_invalid",
        ),
    ),
    (
        "g2a_t08_queued_block",
        "QUEUED",
        "BLOCKED",
        "DETERMINISTIC",
        "lifecycle_runtime",
        "NONE",
        (
            "blocking_evidence_valid",
            "authority_policy_valid",
            "idempotency_reservation_owned",
        ),
        "NOT_CONSUMED",
        "NO_ADAPTER_INVOCATION",
        True,
        "packet_blocked",
        (
            "blocking_evidence_missing",
            "authority_expansion_detected",
            "authority_policy_invalid",
            "idempotency_reservation_invalid",
        ),
    ),
    (
        "g2a_t09_pending_block",
        "PENDING_FULFILLMENT",
        "BLOCKED",
        "DETERMINISTIC",
        "exclusive_corridor",
        "NONE",
        (
            "immediate_eligibility_failure_valid",
            "adapter_not_called",
            "idempotency_reservation_owned",
        ),
        "NOT_CONSUMED",
        "NO_ADAPTER_INVOCATION",
        True,
        "packet_blocked",
        (
            "adapter_already_called",
            "blocking_evidence_missing",
            "idempotency_reservation_invalid",
        ),
    ),
    (
        "g2a_t10_failed_block",
        "FAILED",
        "BLOCKED",
        "DETERMINISTIC",
        "lifecycle_runtime",
        "NONE",
        (
            "failed_non_consuming_provenance_valid",
            "retry_ineligibility_evidence_valid",
            "idempotency_reservation_owned",
        ),
        "NOT_CONSUMED",
        "NO_ADAPTER_INVOCATION",
        True,
        "packet_blocked",
        (
            "failed_provenance_invalid",
            "retry_ineligibility_evidence_missing",
            "authority_expansion_detected",
            "idempotency_reservation_invalid",
        ),
    ),
    (
        "g2a_t11_created_expire",
        "CREATED",
        "EXPIRED",
        "DETERMINISTIC",
        "temporal_validator",
        "NONE",
        (
            "packet_genesis_valid",
            "temporal_authority_valid",
            "evaluation_time_valid",
        ),
        "NOT_CONSUMED",
        "NO_ADAPTER_INVOCATION",
        True,
        "packet_expired",
        (
            "packet_genesis_invalid",
            "temporal_authority_invalid",
            "evaluation_time_invalid",
            "prior_terminal_state",
        ),
    ),
    (
        "g2a_t12_authorized_expire",
        "ROOT_AUTHORIZED",
        "EXPIRED",
        "DETERMINISTIC",
        "temporal_validator",
        "NONE",
        (
            "temporal_authority_valid",
            "evaluation_time_valid",
            "idempotency_reservation_owned",
        ),
        "NOT_CONSUMED",
        "NO_ADAPTER_INVOCATION",
        True,
        "packet_expired",
        (
            "temporal_authority_invalid",
            "evaluation_time_invalid",
            "prior_terminal_state",
            "idempotency_reservation_invalid",
        ),
    ),
    (
        "g2a_t13_queued_expire",
        "QUEUED",
        "EXPIRED",
        "DETERMINISTIC",
        "temporal_validator",
        "NONE",
        (
            "temporal_authority_valid",
            "evaluation_time_valid",
            "idempotency_reservation_owned",
        ),
        "NOT_CONSUMED",
        "NO_ADAPTER_INVOCATION",
        True,
        "packet_expired",
        (
            "temporal_authority_invalid",
            "evaluation_time_invalid",
            "prior_terminal_state",
            "idempotency_reservation_invalid",
        ),
    ),
    (
        "g2a_t14_pending_expire",
        "PENDING_FULFILLMENT",
        "EXPIRED",
        "DETERMINISTIC",
        "exclusive_corridor",
        "NONE",
        (
            "immediate_temporal_validation_pass",
            "evaluation_time_valid",
            "idempotency_reservation_owned",
        ),
        "NOT_CONSUMED",
        "NO_ADAPTER_INVOCATION",
        True,
        "packet_expired",
        (
            "adapter_already_called",
            "temporal_authority_invalid",
            "evaluation_time_invalid",
            "idempotency_reservation_invalid",
        ),
    ),
    (
        "g2a_t15_failed_expire",
        "FAILED",
        "EXPIRED",
        "DETERMINISTIC",
        "temporal_validator",
        "NONE",
        (
            "failed_non_consuming_provenance_valid",
            "temporal_authority_valid",
            "evaluation_time_valid",
            "idempotency_reservation_owned",
        ),
        "NOT_CONSUMED",
        "NO_ADAPTER_INVOCATION",
        True,
        "packet_expired",
        (
            "failed_provenance_invalid",
            "temporal_authority_invalid",
            "evaluation_time_invalid",
            "prior_terminal_state",
            "idempotency_reservation_invalid",
        ),
    ),
    (
        "g2a_t16_authorized_revoke",
        "ROOT_AUTHORIZED",
        "REVOKED",
        "AUTHORITY_CHANGE",
        "owning_local_root",
        "NEW_ROOT_REVOCATION_DECISION",
        (
            "accepted_revocation_binding_valid",
            "source_authorization_binding_valid",
            "idempotency_reservation_owned",
        ),
        "NOT_CONSUMED",
        "NO_ADAPTER_INVOCATION",
        True,
        "packet_revoked",
        (
            "foreign_root",
            "accepted_revocation_binding_invalid",
            "source_authorization_mismatch",
            "idempotency_reservation_invalid",
        ),
    ),
    (
        "g2a_t17_queued_revoke",
        "QUEUED",
        "REVOKED",
        "AUTHORITY_CHANGE",
        "owning_local_root",
        "NEW_ROOT_REVOCATION_DECISION",
        (
            "accepted_revocation_binding_valid",
            "source_authorization_binding_valid",
            "idempotency_reservation_owned",
        ),
        "NOT_CONSUMED",
        "NO_ADAPTER_INVOCATION",
        True,
        "packet_revoked",
        (
            "foreign_root",
            "accepted_revocation_binding_invalid",
            "source_authorization_mismatch",
            "idempotency_reservation_invalid",
        ),
    ),
    (
        "g2a_t18_pending_revoke",
        "PENDING_FULFILLMENT",
        "REVOKED",
        "AUTHORITY_CHANGE",
        "owning_local_root",
        "NEW_ROOT_REVOCATION_DECISION",
        (
            "accepted_revocation_binding_valid",
            "source_authorization_binding_valid",
            "adapter_not_called",
            "idempotency_reservation_owned",
        ),
        "NOT_CONSUMED",
        "NO_ADAPTER_INVOCATION",
        True,
        "packet_revoked",
        (
            "adapter_already_called",
            "foreign_root",
            "accepted_revocation_binding_invalid",
            "source_authorization_mismatch",
            "idempotency_reservation_invalid",
        ),
    ),
    (
        "g2a_t19_failed_revoke",
        "FAILED",
        "REVOKED",
        "AUTHORITY_CHANGE",
        "owning_local_root",
        "NEW_ROOT_REVOCATION_DECISION",
        (
            "failed_non_consuming_provenance_valid",
            "accepted_revocation_binding_valid",
            "source_authorization_binding_valid",
            "idempotency_reservation_owned",
        ),
        "NOT_CONSUMED",
        "NO_ADAPTER_INVOCATION",
        True,
        "packet_revoked",
        (
            "failed_provenance_invalid",
            "foreign_root",
            "accepted_revocation_binding_invalid",
            "source_authorization_mismatch",
            "idempotency_reservation_invalid",
        ),
    ),
    (
        "g2a_t20_authorized_supersede",
        "ROOT_AUTHORIZED",
        "SUPERSEDED",
        "AUTHORITY_CHANGE",
        "owning_local_root",
        "NEW_ROOT_SUPERSESSION_DECISION",
        (
            "successor_packet_valid",
            "accepted_supersession_binding_valid",
            "predecessor_binding_valid",
            "idempotency_transfer_valid",
        ),
        "NOT_CONSUMED",
        "NO_ADAPTER_INVOCATION",
        True,
        "packet_superseded",
        (
            "successor_packet_missing",
            "accepted_supersession_binding_invalid",
            "predecessor_binding_mismatch",
            "foreign_root",
            "idempotency_transfer_invalid",
        ),
    ),
    (
        "g2a_t21_queued_supersede",
        "QUEUED",
        "SUPERSEDED",
        "AUTHORITY_CHANGE",
        "owning_local_root",
        "NEW_ROOT_SUPERSESSION_DECISION",
        (
            "successor_packet_valid",
            "accepted_supersession_binding_valid",
            "predecessor_binding_valid",
            "idempotency_transfer_valid",
        ),
        "NOT_CONSUMED",
        "NO_ADAPTER_INVOCATION",
        True,
        "packet_superseded",
        (
            "successor_packet_missing",
            "accepted_supersession_binding_invalid",
            "predecessor_binding_mismatch",
            "foreign_root",
            "idempotency_transfer_invalid",
        ),
    ),
    (
        "g2a_t22_pending_supersede",
        "PENDING_FULFILLMENT",
        "SUPERSEDED",
        "AUTHORITY_CHANGE",
        "owning_local_root",
        "NEW_ROOT_SUPERSESSION_DECISION",
        (
            "successor_packet_valid",
            "accepted_supersession_binding_valid",
            "predecessor_binding_valid",
            "adapter_not_called",
            "idempotency_transfer_valid",
        ),
        "NOT_CONSUMED",
        "NO_ADAPTER_INVOCATION",
        True,
        "packet_superseded",
        (
            "adapter_already_called",
            "successor_packet_missing",
            "accepted_supersession_binding_invalid",
            "predecessor_binding_mismatch",
            "foreign_root",
            "idempotency_transfer_invalid",
        ),
    ),
    (
        "g2a_t23_failed_supersede",
        "FAILED",
        "SUPERSEDED",
        "AUTHORITY_CHANGE",
        "owning_local_root",
        "NEW_ROOT_SUPERSESSION_DECISION",
        (
            "failed_non_consuming_provenance_valid",
            "successor_packet_valid",
            "accepted_supersession_binding_valid",
            "predecessor_binding_valid",
            "idempotency_transfer_valid",
        ),
        "NOT_CONSUMED",
        "NO_ADAPTER_INVOCATION",
        True,
        "packet_superseded",
        (
            "failed_provenance_invalid",
            "successor_packet_missing",
            "accepted_supersession_binding_invalid",
            "predecessor_binding_mismatch",
            "foreign_root",
            "idempotency_transfer_invalid",
        ),
    ),
    (
        "g2a_t24_nonconsuming_failure",
        "PENDING_FULFILLMENT",
        "FAILED",
        "DETERMINISTIC",
        "exclusive_corridor",
        "NONE",
        (
            "adapter_invocation_evidence_valid",
            "effect_nonconsumption_evidence_valid",
            "idempotency_reservation_owned",
            "latest_disposition_event_binding_valid",
        ),
        "NOT_CONSUMED",
        "CORRIDOR_INVOCATION_NONCONSUMING",
        False,
        "fulfillment_failed_nonconsuming",
        (
            "adapter_not_called",
            "effect_consumed",
            "effect_outcome_uncertain",
            "failure_evidence_missing",
            "idempotency_reservation_invalid",
            "latest_disposition_event_binding_invalid",
            "disposition_history_changed",
        ),
    ),
    (
        "g2a_t25_retry",
        "FAILED",
        "QUEUED",
        "DETERMINISTIC",
        "lifecycle_runtime",
        "NONE",
        (
            "failed_non_consuming_provenance_valid",
            "retry_policy_valid",
            "current_eligibility_valid",
            "idempotency_reservation_owned",
        ),
        "NOT_CONSUMED",
        "NO_ADAPTER_INVOCATION",
        False,
        "nonconsuming_retry_queued",
        (
            "failed_provenance_invalid",
            "packet_binding_mismatch",
            "idempotency_binding_mismatch",
            "terminal_evidence_present",
            "mandatory_dependency_invalid",
            "retry_policy_invalid",
            "idempotency_reservation_invalid",
        ),
    ),
    (
        "g2a_t26_uncertain_adapter_outcome",
        "PENDING_FULFILLMENT",
        "FAILED",
        "DETERMINISTIC_UNCERTAIN",
        "exclusive_corridor",
        "NONE",
        (
            "adapter_invocation_evidence_valid",
            "effect_outcome_unresolved",
            "idempotency_reservation_owned",
        ),
        "UNCERTAIN",
        "CORRIDOR_INVOCATION_UNCERTAIN",
        True,
        "fulfillment_failed_consumption_uncertain",
        (
            "adapter_not_called",
            "effect_consumed",
            "effect_non_consumption_proven",
            "execution_attempt_evidence_missing",
            "idempotency_binding_missing",
            "transition_event_identity_invalid",
        ),
    ),
)


def action_packet_transition_rule_material_v01(
    rule: ActionPacketTransitionRuleV01,
) -> tuple[tuple[str, object], ...]:
    errors = validate_action_packet_transition_rule_v01(rule)
    if errors:
        raise ValueError(errors[0])
    return _action_packet_transition_rule_material_unchecked_v01(rule)


def validate_action_packet_transition_rule_v01(
    rule: object,
) -> tuple[str, ...]:
    try:
        if type(rule) is not ActionPacketTransitionRuleV01:
            return ("action_packet_transition_rule_invalid",)
        errors: list[str] = []
        lower_codes = (
            rule.transition_rule_id,
            rule.permitted_component_code,
            rule.reason_code,
        )
        if any(not _action_packet_machine_code_valid_v01(code) for code in lower_codes):
            errors.append("action_packet_transition_machine_code_invalid")
        if (
            type(rule.required_evidence_codes) is not tuple
            or not rule.required_evidence_codes
            or any(
                not _action_packet_machine_code_valid_v01(code)
                for code in rule.required_evidence_codes
            )
        ):
            errors.append("action_packet_transition_evidence_codes_invalid")
        elif len(rule.required_evidence_codes) != len(
            set(rule.required_evidence_codes)
        ):
            errors.append("action_packet_transition_evidence_code_duplicate")
        elif any(
            code not in ACTION_PACKET_REQUIRED_EVIDENCE_CODES_V01
            for code in rule.required_evidence_codes
        ):
            errors.append("action_packet_transition_evidence_code_unknown")
        if (
            type(rule.fail_closed_reason_codes) is not tuple
            or not rule.fail_closed_reason_codes
            or any(
                not _action_packet_machine_code_valid_v01(code)
                for code in rule.fail_closed_reason_codes
            )
        ):
            errors.append("action_packet_transition_fail_codes_invalid")
        elif len(rule.fail_closed_reason_codes) != len(
            set(rule.fail_closed_reason_codes)
        ):
            errors.append("action_packet_transition_fail_code_duplicate")
        elif any(
            code not in ACTION_PACKET_FAIL_CLOSED_REASON_CODES_V01
            for code in rule.fail_closed_reason_codes
        ):
            errors.append("action_packet_transition_fail_code_unknown")
        exact_memberships = (
            (
                rule.transition_rule_id,
                ACTION_PACKET_TRANSITION_RULE_IDS_V01,
                "action_packet_transition_rule_id_unknown",
            ),
            (
                rule.source_state,
                ACTION_PACKET_LIFECYCLE_STATES_V01,
                "action_packet_transition_state_unknown",
            ),
            (
                rule.target_state,
                ACTION_PACKET_LIFECYCLE_STATES_V01,
                "action_packet_transition_state_unknown",
            ),
            (
                rule.transition_class_code,
                ACTION_PACKET_TRANSITION_CLASS_CODES_V01,
                "action_packet_transition_class_unknown",
            ),
            (
                rule.permitted_component_code,
                ACTION_PACKET_PERMITTED_COMPONENT_CODES_V01,
                "action_packet_transition_component_unknown",
            ),
            (
                rule.root_decision_requirement_code,
                ACTION_PACKET_ROOT_DECISION_REQUIREMENT_CODES_V01,
                "action_packet_transition_root_requirement_unknown",
            ),
            (
                rule.effect_consumption_class,
                ACTION_PACKET_EFFECT_CONSUMPTION_CLASSES_V01,
                "action_packet_transition_consumption_unknown",
            ),
            (
                rule.adapter_invocation_relation_code,
                ACTION_PACKET_ADAPTER_INVOCATION_RELATION_CODES_V01,
                "action_packet_transition_invocation_relation_unknown",
            ),
            (
                rule.reason_code,
                ACTION_PACKET_TRANSITION_REASON_CODES_V01,
                "action_packet_transition_reason_unknown",
            ),
        )
        for value, vocabulary, reason in exact_memberships:
            if type(value) is not str or value not in vocabulary:
                errors.append(reason)
        if type(rule.terminal_target) is not bool:
            errors.append("action_packet_transition_terminal_type_invalid")
        if not errors:
            expected = _canonical_action_packet_transition_rules_v01()
            index = ACTION_PACKET_TRANSITION_RULE_IDS_V01.index(
                rule.transition_rule_id
            )
            if (
                _action_packet_transition_rule_material_unchecked_v01(rule)
                != _action_packet_transition_rule_material_unchecked_v01(
                    expected[index]
                )
            ):
                errors.append("action_packet_transition_rule_mismatch")
        return _dedupe(errors)
    except Exception:
        return ("action_packet_transition_rule_invalid",)


def action_packet_transition_rule_to_plain_dict_v01(
    rule: ActionPacketTransitionRuleV01,
) -> dict[str, object]:
    try:
        material = action_packet_transition_rule_material_v01(rule)
        result = {
            name: list(value) if type(value) is tuple else value
            for name, value in material
        }
        _canonical_json_bytes_v01(result)
        return result
    except Exception:
        raise ValueError("action_packet_transition_rule_invalid") from None


def build_action_packet_transition_registry_profile_v01(
) -> ActionPacketTransitionRegistryProfileV01:
    lifecycle_profile = _build_action_packet_lifecycle_profile_v01()
    if _validate_action_packet_lifecycle_profile_v01(lifecycle_profile):
        raise ValueError("action_packet_lifecycle_profile_invalid")
    rules = _canonical_action_packet_transition_rules_v01()
    material = _action_packet_transition_registry_material_unchecked_v01(
        registry_profile_version=(
            ACTION_PACKET_TRANSITION_REGISTRY_PROFILE_VERSION_V01
        ),
        lifecycle_profile_id=lifecycle_profile.profile_id,
        rules=rules,
    )
    digest = _domain_separated_sha256_hex_v01(
        domain=ACTION_PACKET_TRANSITION_REGISTRY_DOMAIN_V01,
        payload=_canonical_json_bytes_v01(material),
    )
    return ActionPacketTransitionRegistryProfileV01(
        transition_registry_id=(
            ACTION_PACKET_TRANSITION_REGISTRY_PREFIX_V01 + digest
        ),
        registry_profile_version=(
            ACTION_PACKET_TRANSITION_REGISTRY_PROFILE_VERSION_V01
        ),
        lifecycle_profile_id=lifecycle_profile.profile_id,
        ordered_transition_rules=rules,
    )


def validate_action_packet_transition_registry_profile_v01(
    registry: object,
) -> tuple[str, ...]:
    try:
        if type(registry) is not ActionPacketTransitionRegistryProfileV01:
            return ("action_packet_transition_registry_invalid",)
        errors: list[str] = []
        if (
            type(registry.transition_registry_id) is not str
            or not registry.transition_registry_id.startswith(
                ACTION_PACKET_TRANSITION_REGISTRY_PREFIX_V01
            )
            or not _lowercase_sha256_valid_v01(
                registry.transition_registry_id[
                    len(ACTION_PACKET_TRANSITION_REGISTRY_PREFIX_V01) :
                ]
            )
        ):
            errors.append("action_packet_transition_registry_id_invalid")
        if (
            type(registry.registry_profile_version) is not str
            or registry.registry_profile_version
            != ACTION_PACKET_TRANSITION_REGISTRY_PROFILE_VERSION_V01
        ):
            errors.append("action_packet_transition_registry_version_mismatch")
        lifecycle_profile = _build_action_packet_lifecycle_profile_v01()
        if (
            _validate_action_packet_lifecycle_profile_v01(lifecycle_profile)
            or type(registry.lifecycle_profile_id) is not str
            or registry.lifecycle_profile_id
            != ACTION_PACKET_LIFECYCLE_PROFILE_ID_V01
        ):
            errors.append("action_packet_transition_lifecycle_profile_mismatch")
        if type(registry.ordered_transition_rules) is not tuple:
            errors.append("action_packet_transition_rules_type_invalid")
            return _dedupe(errors)
        if len(registry.ordered_transition_rules) != 26:
            errors.append("action_packet_transition_rule_count_mismatch")
        for rule in registry.ordered_transition_rules:
            errors.extend(validate_action_packet_transition_rule_v01(rule))
        ids = tuple(
            rule.transition_rule_id
            for rule in registry.ordered_transition_rules
            if type(rule) is ActionPacketTransitionRuleV01
            and type(rule.transition_rule_id) is str
        )
        if len(ids) != len(set(ids)):
            errors.append("action_packet_transition_rule_id_duplicate")
        if ids != ACTION_PACKET_TRANSITION_RULE_IDS_V01:
            errors.append("action_packet_transition_rule_order_mismatch")
        if errors:
            return _dedupe(errors)
        expected = build_action_packet_transition_registry_profile_v01()
        supplied_material = (
            _action_packet_transition_registry_material_unchecked_v01(
                registry_profile_version=registry.registry_profile_version,
                lifecycle_profile_id=registry.lifecycle_profile_id,
                rules=registry.ordered_transition_rules,
            )
        )
        expected_material = (
            _action_packet_transition_registry_material_unchecked_v01(
                registry_profile_version=expected.registry_profile_version,
                lifecycle_profile_id=expected.lifecycle_profile_id,
                rules=expected.ordered_transition_rules,
            )
        )
        if _canonical_json_bytes_v01(supplied_material) != (
            _canonical_json_bytes_v01(expected_material)
        ):
            errors.append("action_packet_transition_registry_material_mismatch")
        if (
            type(registry.transition_registry_id) is not str
            or registry.transition_registry_id
            != expected.transition_registry_id
        ):
            errors.append("action_packet_transition_registry_id_mismatch")
        return _dedupe(errors)
    except Exception:
        return ("action_packet_transition_registry_invalid",)


def action_packet_transition_registry_material_v01(
    registry: ActionPacketTransitionRegistryProfileV01,
) -> tuple[tuple[str, object], ...]:
    errors = validate_action_packet_transition_registry_profile_v01(registry)
    if errors:
        raise ValueError(errors[0])
    return _action_packet_transition_registry_material_unchecked_v01(
        registry_profile_version=registry.registry_profile_version,
        lifecycle_profile_id=registry.lifecycle_profile_id,
        rules=registry.ordered_transition_rules,
    )


def action_packet_transition_registry_to_plain_dict_v01(
    registry: ActionPacketTransitionRegistryProfileV01,
) -> dict[str, object]:
    try:
        if validate_action_packet_transition_registry_profile_v01(registry):
            raise ValueError("action_packet_transition_registry_invalid")
        result = {
            "transition_registry_id": registry.transition_registry_id,
            "registry_profile_version": registry.registry_profile_version,
            "lifecycle_profile_id": registry.lifecycle_profile_id,
            "ordered_transition_rules": [
                action_packet_transition_rule_to_plain_dict_v01(rule)
                for rule in registry.ordered_transition_rules
            ],
        }
        _canonical_json_bytes_v01(result)
        return result
    except Exception:
        raise ValueError("action_packet_transition_registry_invalid") from None


def lookup_action_packet_transition_rule_v01(
    *,
    registry: object,
    transition_rule_id: object,
) -> ActionPacketTransitionRuleV01:
    try:
        if validate_action_packet_transition_registry_profile_v01(registry):
            raise ValueError("unknown_transition")
        if (
            type(transition_rule_id) is not str
            or transition_rule_id not in ACTION_PACKET_TRANSITION_RULE_IDS_V01
        ):
            raise ValueError("unknown_transition")
        for rule in registry.ordered_transition_rules:
            if rule.transition_rule_id == transition_rule_id:
                return rule
        raise ValueError("unknown_transition")
    except Exception:
        raise ValueError("unknown_transition") from None


def _canonical_action_packet_transition_rules_v01(
) -> tuple[ActionPacketTransitionRuleV01, ...]:
    return tuple(
        ActionPacketTransitionRuleV01(
            transition_rule_id=row[0],
            source_state=row[1],
            target_state=row[2],
            transition_class_code=row[3],
            permitted_component_code=row[4],
            root_decision_requirement_code=row[5],
            required_evidence_codes=row[6],
            effect_consumption_class=row[7],
            adapter_invocation_relation_code=row[8],
            terminal_target=row[9],
            reason_code=row[10],
            fail_closed_reason_codes=row[11],
        )
        for row in _ACTION_PACKET_TRANSITION_RULE_ROWS_V01
    )


def _action_packet_transition_rule_material_unchecked_v01(
    rule: ActionPacketTransitionRuleV01,
) -> tuple[tuple[str, object], ...]:
    return (
        ("transition_rule_id", rule.transition_rule_id),
        ("source_state", rule.source_state),
        ("target_state", rule.target_state),
        ("transition_class_code", rule.transition_class_code),
        ("permitted_component_code", rule.permitted_component_code),
        (
            "root_decision_requirement_code",
            rule.root_decision_requirement_code,
        ),
        ("required_evidence_codes", rule.required_evidence_codes),
        ("effect_consumption_class", rule.effect_consumption_class),
        (
            "adapter_invocation_relation_code",
            rule.adapter_invocation_relation_code,
        ),
        ("terminal_target", rule.terminal_target),
        ("reason_code", rule.reason_code),
        ("fail_closed_reason_codes", rule.fail_closed_reason_codes),
    )


def _action_packet_transition_registry_material_unchecked_v01(
    *,
    registry_profile_version: str,
    lifecycle_profile_id: str,
    rules: tuple[ActionPacketTransitionRuleV01, ...],
) -> tuple[tuple[str, object], ...]:
    return (
        ("registry_profile_version", registry_profile_version),
        ("lifecycle_profile_id", lifecycle_profile_id),
        (
            "ordered_transition_rules",
            tuple(
                _action_packet_transition_rule_material_unchecked_v01(rule)
                for rule in rules
            ),
        ),
    )


def _action_packet_machine_code_valid_v01(value: object) -> bool:
    if type(value) is not str or not value or "\x00" in value:
        return False
    try:
        value.encode("utf-8", errors="strict")
        return (
            _unicodedata.normalize("NFC", value) == value
            and _re.fullmatch(r"[a-z][a-z0-9_]*", value) is not None
        )
    except Exception:
        return False


def _lowercase_sha256_valid_v01(value: object) -> bool:
    return bool(
        type(value) is str
        and _re.fullmatch(r"[0-9a-f]{64}", value) is not None
    )


EXECUTION_MODE_TRANSITION_REGISTRY_PROFILE_ID_V01 = (
    "execution_mode_router_g2c_transition_profile_v01"
)
EXECUTION_MODE_TRANSITION_REGISTRY_PROFILE_VERSION_V01 = "v0.1"
EXECUTION_MODE_TRANSITION_REGISTRY_RULE_COUNT_V01 = 6

_EXECUTION_MODE_TRANSITION_RULE_ROWS_V01 = (
    (
        "g2c_transition:proposal_to_root_review:v01",
        "ExecutionModeProposal", "VALIDATED", "execution_mode_router",
        "ENTER_ROOT_REVIEW", "RootExecutionModeDecision",
        ("proposal_sources_valid", "proposal_artifact_valid", "target_root_bound"),
        DECISION_RETURN_TO_ROOT, "g2c_transition_root_review_required", False,
    ),
    (
        "g2c_transition:root_accept_to_route:v01",
        "RootExecutionModeDecision", "ROOT_ACCEPTED", "root", "ACCEPT_ROUTE",
        "ExecutionModeRouteEligibility",
        ("root_result_valid", "accepted_mode_valid", "accepted_scope_valid", "consumption_class_valid"),
        DECISION_ALLOW, "g2c_transition_route_accept_allowed", True,
    ),
    (
        "g2c_transition:root_narrow_to_route:v01",
        "RootExecutionModeDecision", "ROOT_ACCEPTED", "root", "NARROW_SCOPE",
        "ExecutionModeRouteEligibility",
        ("root_result_valid", "accepted_mode_valid", "narrowing_proof_valid", "consumption_class_valid"),
        DECISION_ALLOW, "g2c_transition_scope_narrow_allowed", True,
    ),
    (
        "g2c_transition:root_reject_record:v01",
        "RootExecutionModeDecision", "ROOT_REJECTED", "root", "REJECT_ROUTE",
        "RootExecutionModeDecision",
        ("root_result_valid", "terminal_consumption_forbidden"),
        DECISION_RETURN_TO_ROOT, "g2c_transition_reject_recorded", True,
    ),
    (
        "g2c_transition:root_block_record:v01",
        "RootExecutionModeDecision", "BLOCKED_FAIL_CLOSED", "root", "BLOCK_ROUTE",
        "RootExecutionModeDecision",
        ("root_result_valid", "terminal_consumption_forbidden"),
        DECISION_BLOCKED_FAIL_CLOSED, "g2c_transition_blocked_recorded", True,
    ),
    (
        "g2c_transition:root_needs_user_record:v01",
        "RootExecutionModeDecision", "ROOT_REVIEWED", "root", "REQUEST_USER_INPUT",
        "RootExecutionModeDecision",
        ("root_result_valid", "terminal_consumption_forbidden"),
        DECISION_NEEDS_USER, "g2c_transition_needs_user_recorded", True,
    ),
)


def _execution_mode_transition_rules_v01() -> tuple[TransitionRuleV01, ...]:
    return tuple(
        TransitionRuleV01(
            rule_id=row[0], abi_major_version=1,
            source_artifact_type=row[1], source_lifecycle_state=row[2],
            actor_role=row[3], attempted_effect=row[4],
            target_artifact_type=row[5], required_guards=row[6],
            decision=row[7], reason_code=row[8], root_commit_required=row[9],
        )
        for row in _EXECUTION_MODE_TRANSITION_RULE_ROWS_V01
    )


def _execution_mode_transition_registry_material_v01(
    rules: tuple[TransitionRuleV01, ...],
) -> dict[str, object]:
    return {
        "registry_version": EXECUTION_MODE_TRANSITION_REGISTRY_PROFILE_VERSION_V01,
        "abi_major_version": 1,
        "rules": [_rule_plain(rule) for rule in rules],
    }


def build_execution_mode_transition_registry_profile_v01(
) -> TransitionRegistryV01:
    rules = _execution_mode_transition_rules_v01()
    return TransitionRegistryV01(
        registry_id=_hash(
            _REGISTRY_DOMAIN,
            _execution_mode_transition_registry_material_v01(rules),
        ),
        registry_version=EXECUTION_MODE_TRANSITION_REGISTRY_PROFILE_VERSION_V01,
        abi_major_version=1,
        rules=rules,
    )


def validate_execution_mode_transition_registry_profile_v01(
    registry: object,
) -> tuple[str, ...]:
    try:
        if type(registry) is not TransitionRegistryV01:
            return ("g2c_transition_profile_invalid",)
        expected_rules = _execution_mode_transition_rules_v01()
        if (
            registry.registry_version
            != EXECUTION_MODE_TRANSITION_REGISTRY_PROFILE_VERSION_V01
            or type(registry.abi_major_version) is not int
            or registry.abi_major_version != 1
            or type(registry.rules) is not tuple
            or len(registry.rules) != EXECUTION_MODE_TRANSITION_REGISTRY_RULE_COUNT_V01
            or any(type(rule) is not TransitionRuleV01 for rule in registry.rules)
            or _canonical_bytes([_rule_plain(rule) for rule in registry.rules])
            != _canonical_bytes([_rule_plain(rule) for rule in expected_rules])
        ):
            return ("g2c_transition_profile_invalid",)
        expected_id = _hash(
            _REGISTRY_DOMAIN,
            _execution_mode_transition_registry_material_v01(expected_rules),
        )
        if registry.registry_id != expected_id:
            return ("g2c_transition_registry_identity_mismatch",)
        return ()
    except Exception:
        return ("g2c_transition_profile_invalid",)


def execution_mode_transition_registry_profile_to_plain_dict_v01(
    registry: TransitionRegistryV01,
) -> dict[str, object]:
    try:
        errors = validate_execution_mode_transition_registry_profile_v01(registry)
        if errors:
            raise ValueError(errors[0])
        result = _registry_plain(registry)
        _canonical_json_bytes_v01(result)
        return result
    except ValueError as exc:
        reason = exc.args[0] if len(exc.args) == 1 else None
        if reason not in {
            "g2c_transition_profile_invalid",
            "g2c_transition_registry_identity_mismatch",
        }:
            reason = "g2c_transition_profile_invalid"
        raise ValueError(reason) from None
    except Exception:
        raise ValueError("g2c_transition_profile_invalid") from None


def _execution_mode_transition_decision_structure_v01(
    decision: object,
) -> bool:
    if type(decision) is not TransitionDecisionV01:
        return False
    if not all(
        _valid_text(value)
        for value in (
            decision.decision_id, decision.registry_id, decision.rule_id,
            decision.source_artifact_type, decision.source_lifecycle_state,
            decision.actor_role, decision.attempted_effect,
            decision.target_artifact_type, decision.reason_code,
        )
    ):
        return False
    if type(decision.abi_major_version) is not int:
        return False
    if not all(
        _valid_text_tuple(value, allow_empty=True)
        for value in (
            decision.required_guards,
            decision.satisfied_guards,
            decision.missing_guards,
        )
    ):
        return False
    return (
        type(decision.decision) is str
        and decision.decision in TRANSITION_DECISIONS
        and type(decision.root_commit_required) is bool
        and type(decision.root_commit_present) is bool
        and type(decision.matched) is bool
    )


def validate_execution_mode_transition_decision_v01(
    *, registry: TransitionRegistryV01, decision: object,
) -> tuple[str, ...]:
    try:
        registry_errors = validate_execution_mode_transition_registry_profile_v01(
            registry
        )
        if registry_errors:
            return registry_errors
        if not _execution_mode_transition_decision_structure_v01(decision):
            return ("g2c_transition_decision_invalid",)
        assert type(decision) is TransitionDecisionV01
        rule = {item.rule_id: item for item in registry.rules}.get(decision.rule_id)
        if rule is None:
            return ("g2c_transition_decision_invalid",)
        if (
            decision.required_guards != rule.required_guards
            or decision.satisfied_guards != rule.required_guards
            or decision.missing_guards != ()
        ):
            return ("g2c_transition_guard_invalid",)
        if (
            decision.root_commit_required is not rule.root_commit_required
            or decision.root_commit_present is not rule.root_commit_required
        ):
            return ("g2c_transition_root_commit_required",)
        if (
            decision.registry_id != registry.registry_id
            or decision.abi_major_version != rule.abi_major_version
            or decision.source_artifact_type != rule.source_artifact_type
            or decision.source_lifecycle_state != rule.source_lifecycle_state
            or decision.actor_role != rule.actor_role
            or decision.attempted_effect != rule.attempted_effect
            or decision.target_artifact_type != rule.target_artifact_type
            or decision.decision != rule.decision
            or decision.reason_code != rule.reason_code
            or decision.matched is not True
        ):
            return ("g2c_transition_decision_invalid",)
        if decision.decision_id != rebuild_execution_mode_transition_decision_identity_v01(
            decision
        ):
            return ("g2c_transition_decision_identity_mismatch",)
        return ()
    except Exception:
        return ("g2c_transition_decision_invalid",)


def execution_mode_transition_decision_to_plain_dict_v01(
    *, registry: TransitionRegistryV01, decision: TransitionDecisionV01,
) -> dict[str, object]:
    try:
        errors = validate_execution_mode_transition_decision_v01(
            registry=registry, decision=decision
        )
        if errors:
            raise ValueError(errors[0])
        result = _decision_plain(decision)
        _canonical_json_bytes_v01(result)
        return result
    except ValueError as exc:
        reason = exc.args[0] if len(exc.args) == 1 else None
        if reason not in {
            "g2c_transition_profile_invalid",
            "g2c_transition_registry_identity_mismatch",
            "g2c_transition_decision_invalid",
            "g2c_transition_decision_identity_mismatch",
            "g2c_transition_guard_invalid",
            "g2c_transition_root_commit_required",
        }:
            reason = "g2c_transition_decision_invalid"
        raise ValueError(reason) from None
    except Exception:
        raise ValueError("g2c_transition_decision_invalid") from None


def rebuild_execution_mode_transition_decision_identity_v01(
    decision: TransitionDecisionV01,
) -> str:
    try:
        if not _execution_mode_transition_decision_structure_v01(decision):
            raise ValueError("g2c_transition_decision_invalid")
        material = _decision_plain(decision)
        material.pop("decision_id")
        return _hash(_DECISION_DOMAIN, material)
    except Exception:
        raise ValueError("g2c_transition_decision_invalid") from None


_FRACTAL_RUNTIME_TRANSITION_PROFILE_ID_V02 = (
    "fractal_runtime_g2d_transition_profile_v02"
)
_FRACTAL_RUNTIME_TRANSITION_PROFILE_VERSION_V02 = "v0.1"
_FRACTAL_RUNTIME_TRANSITION_RULE_COUNT_V02 = 17

_FRACTAL_RUNTIME_ARTIFACT_CONTEXT_PROFILES_V02 = (
    (
        "ExecutionModeRouteEligibility",
        "HEDGEHOG_EXECUTION_MODE_ROUTE_ELIGIBILITY_KERNEL_ARTIFACT_V01",
        "emabi_route_v01:",
        "v0.1",
        "root_decision_v01",
        "ROOT_AUTHORIZED",
    ),
    (
        "RuntimeExecutionTopology",
        "HEDGEHOG_FRACTAL_RUNTIME_TOPOLOGY_KERNEL_ARTIFACT_V02",
        "frabi_topology_v02:",
        "v0.2",
        "fractal_runtime_v02",
        "ADVISORY",
    ),
    (
        "FractalCellQueueEntry",
        "HEDGEHOG_FRACTAL_CELL_QUEUE_ENTRY_KERNEL_ARTIFACT_V02",
        "frabi_queue_v02:",
        "v0.2",
        "fractal_scheduler_v02",
        "ADVISORY",
    ),
    (
        "FractalCellResult",
        "HEDGEHOG_FRACTAL_CELL_RESULT_KERNEL_ARTIFACT_V02",
        "frabi_result_v02:",
        "v0.2",
        "fractal_runtime_v02",
        "ADVISORY",
    ),
    (
        "FractalRuntimeReport",
        "HEDGEHOG_FRACTAL_RUNTIME_REPORT_KERNEL_ARTIFACT_V02",
        "frabi_report_v02:",
        "v0.2",
        "fractal_runtime_v02",
        "ADVISORY",
    ),
)

_FRACTAL_RUNTIME_TARGET_LIFECYCLE_BY_RULE_V02 = (
    ("g2d_t01_route_eligibility_to_topology", "VALIDATED"),
    ("g2d_t02_topology_to_pending", "VALIDATED"),
    ("g2d_t03_pending_backpressure_defer", "VALIDATED"),
    ("g2d_t04_pending_to_ready", "VALIDATED"),
    ("g2d_t05_ready_to_running", "VALIDATED"),
    ("g2d_t06_running_to_validating", "VALIDATED"),
    ("g2d_t07_validating_to_revise", "VALIDATED"),
    ("g2d_t08_validating_to_completed", "VALIDATED"),
    ("g2d_t09_validating_to_degraded", "VALIDATED"),
    ("g2d_t10_validating_to_blocked", "VALIDATED"),
    ("g2d_t11_validating_to_needs_user", "VALIDATED"),
    ("g2d_t12_validating_to_deadend", "VALIDATED"),
    ("g2d_t13_completed_to_parent_return", "VALIDATED"),
    ("g2d_t14_degraded_to_parent_return", "VALIDATED"),
    ("g2d_t15_blocked_to_parent_return", "BLOCKED_FAIL_CLOSED"),
    ("g2d_t16_needs_user_to_parent_return", "VALIDATED"),
    ("g2d_t17_deadend_to_parent_return", "VALIDATED"),
)

_FRACTAL_RUNTIME_SOURCE_PARENT_PROFILE_BY_RULE_V02 = (
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

_FRACTAL_RUNTIME_PARENT_RELATION_BY_RULE_V02 = (
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

_FRACTAL_RUNTIME_TRANSITION_RULE_ROWS_V02 = (
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


def _fractal_runtime_transition_rules_v02() -> tuple[TransitionRuleV01, ...]:
    return tuple(
        TransitionRuleV01(
            rule_id=row[0],
            abi_major_version=row[1],
            source_artifact_type=row[2],
            source_lifecycle_state=row[3],
            actor_role=row[4],
            attempted_effect=row[5],
            target_artifact_type=row[6],
            required_guards=row[7],
            decision=row[8],
            reason_code=row[9],
            root_commit_required=row[10],
        )
        for row in _FRACTAL_RUNTIME_TRANSITION_RULE_ROWS_V02
    )


def _fractal_runtime_transition_registry_material_v02(
    rules: tuple[TransitionRuleV01, ...],
) -> dict[str, object]:
    return {
        "registry_version": _FRACTAL_RUNTIME_TRANSITION_PROFILE_VERSION_V02,
        "abi_major_version": 1,
        "rules": [_rule_plain(rule) for rule in rules],
    }


def build_fractal_runtime_transition_registry_profile_v02(
) -> TransitionRegistryV01:
    rules = _fractal_runtime_transition_rules_v02()
    return TransitionRegistryV01(
        registry_id=_hash(
            _REGISTRY_DOMAIN,
            _fractal_runtime_transition_registry_material_v02(rules),
        ),
        registry_version=_FRACTAL_RUNTIME_TRANSITION_PROFILE_VERSION_V02,
        abi_major_version=1,
        rules=rules,
    )


def validate_fractal_runtime_transition_registry_profile_v02(
    value: object,
) -> tuple[str, ...]:
    try:
        if type(value) is not TransitionRegistryV01:
            return ("g2d_transition_profile_invalid",)
        expected_rules = _fractal_runtime_transition_rules_v02()
        if (
            value.registry_version
            != _FRACTAL_RUNTIME_TRANSITION_PROFILE_VERSION_V02
            or type(value.abi_major_version) is not int
            or value.abi_major_version != 1
            or type(value.rules) is not tuple
            or len(value.rules) != _FRACTAL_RUNTIME_TRANSITION_RULE_COUNT_V02
            or any(type(rule) is not TransitionRuleV01 for rule in value.rules)
            or _canonical_bytes([_rule_plain(rule) for rule in value.rules])
            != _canonical_bytes([_rule_plain(rule) for rule in expected_rules])
        ):
            return ("g2d_transition_profile_invalid",)
        expected_id = _hash(
            _REGISTRY_DOMAIN,
            _fractal_runtime_transition_registry_material_v02(expected_rules),
        )
        if value.registry_id != expected_id:
            return ("g2d_transition_profile_invalid",)
        return ()
    except Exception:
        return ("g2d_transition_profile_invalid",)


def fractal_runtime_transition_registry_profile_to_plain_dict_v02(
    value: TransitionRegistryV01,
) -> dict[str, object]:
    try:
        errors = validate_fractal_runtime_transition_registry_profile_v02(value)
        if errors:
            raise ValueError(errors[0])
        result = _registry_plain(value)
        _canonical_json_bytes_v01(result)
        return result
    except Exception:
        raise ValueError("g2d_transition_profile_invalid") from None


def _fractal_runtime_transition_decision_structure_v02(value: object) -> bool:
    return _execution_mode_transition_decision_structure_v01(value)


def _fractal_runtime_artifact_context_valid_v02(
    artifact: KernelArtifactV01,
    *,
    expected_lifecycle: str,
) -> bool:
    profiles = {
        row[0]: row[1:]
        for row in _FRACTAL_RUNTIME_ARTIFACT_CONTEXT_PROFILES_V02
    }
    profile = profiles.get(artifact.artifact_type)
    if profile is None:
        return False
    domain, prefix, schema_version, source_component, authority_class = profile
    if (
        artifact.abi_version != "v1.0"
        or artifact.schema_version != schema_version
        or artifact.source_component != source_component
        or artifact.authority_class != authority_class
        or artifact.lifecycle_state != expected_lifecycle
    ):
        return False
    material = _kernel_artifact_to_plain_dict_v01(artifact)
    material.pop("artifact_id")
    return artifact.artifact_id == prefix + _hash(domain, material)


def _fractal_runtime_payload_v02(
    artifact: KernelArtifactV01,
) -> dict[str, object] | None:
    plain = _kernel_artifact_to_plain_dict_v01(artifact)
    payload = plain.get("payload")
    return payload if type(payload) is dict else None


def _fractal_runtime_queue_topology_context_v02(
    artifact: KernelArtifactV01,
) -> str | None:
    if artifact.artifact_type != "FractalCellQueueEntry":
        return None
    trace_refs = artifact.trace_refs
    payload = _fractal_runtime_payload_v02(artifact)
    if (
        type(trace_refs) is not tuple
        or len(trace_refs) < 2
        or any(type(ref) is not str or not ref for ref in trace_refs)
        or _re.fullmatch(r"[0-9a-f]{64}", trace_refs[0]) is None
        or not _fractal_runtime_prefixed_digest_v02(
            trace_refs[1], "frtopology_v02:"
        )
        or payload is None
        or "topology_id" in payload
        or "predecessor_queue_entry_id" in payload
    ):
        return None
    return trace_refs[1]


def _fractal_runtime_prefixed_digest_v02(value: object, prefix: str) -> bool:
    return type(value) is str and _re.fullmatch(
        _re.escape(prefix) + r"[0-9a-f]{64}", value
    ) is not None


def _fractal_runtime_source_parent_envelope_valid_v02(
    *,
    rule: TransitionRuleV01,
    source_artifact: KernelArtifactV01,
) -> bool:
    profile = dict(_FRACTAL_RUNTIME_SOURCE_PARENT_PROFILE_BY_RULE_V02).get(
        rule.rule_id
    )
    parents = source_artifact.parent_refs
    if (
        profile is None
        or type(parents) is not tuple
        or not parents
        or any(type(parent) is not str or not parent for parent in parents)
        or len(parents) != len(set(parents))
        or source_artifact.artifact_id in parents
    ):
        return False

    topology = lambda value: _fractal_runtime_prefixed_digest_v02(
        value, "frabi_topology_v02:"
    )
    queue = lambda value: _fractal_runtime_prefixed_digest_v02(
        value, "frabi_queue_v02:"
    )
    result = lambda value: _fractal_runtime_prefixed_digest_v02(
        value, "frabi_result_v02:"
    )

    if profile == "ROUTE_ELIGIBILITY_SOURCE":
        return len(parents) == 1 and _fractal_runtime_prefixed_digest_v02(
            parents[0], "emabi_decision_v01:"
        )
    if profile == "TOPOLOGY_SOURCE":
        return len(parents) == 1 and _fractal_runtime_prefixed_digest_v02(
            parents[0], "emabi_route_v01:"
        )
    if profile == "PENDING_QUEUE_SOURCE":
        return (
            len(parents) == 1 and topology(parents[0])
        ) or (
            len(parents) == 2
            and topology(parents[0])
            and queue(parents[1])
        )
    if profile == "TWO_PARENT_QUEUE_SOURCE":
        return (
            len(parents) == 2
            and topology(parents[0])
            and queue(parents[1])
        )
    if profile == "TERMINAL_QUEUE_SOURCE":
        return (
            len(parents) in {2, 3}
            and topology(parents[0])
            and queue(parents[1])
            and (len(parents) == 2 or result(parents[2]))
        )
    if profile == "CELL_RESULT_SOURCE":
        if len(parents) < 2 or not topology(parents[0]):
            return False
        queue_count = 0
        result_seen = False
        for parent in parents[1:]:
            if queue(parent) and not result_seen:
                queue_count += 1
            elif result(parent):
                result_seen = True
            else:
                return False
        return queue_count > 0
    return False


def _fractal_runtime_artifact_pair_valid_v02(
    *,
    rule: TransitionRuleV01,
    decision: TransitionDecisionV01,
    source_artifact: KernelArtifactV01,
    target_artifact: KernelArtifactV01,
) -> bool:
    target_lifecycles = dict(_FRACTAL_RUNTIME_TARGET_LIFECYCLE_BY_RULE_V02)
    target_lifecycle = target_lifecycles.get(rule.rule_id)
    if target_lifecycle is None:
        return False
    if not _fractal_runtime_artifact_context_valid_v02(
        source_artifact,
        expected_lifecycle=rule.source_lifecycle_state,
    ) or not _fractal_runtime_artifact_context_valid_v02(
        target_artifact,
        expected_lifecycle=target_lifecycle,
    ) or not _fractal_runtime_source_parent_envelope_valid_v02(
        rule=rule,
        source_artifact=source_artifact,
    ):
        return False
    source_plain = _kernel_artifact_to_plain_dict_v01(source_artifact)
    target_plain = _kernel_artifact_to_plain_dict_v01(target_artifact)
    if (
        source_artifact.artifact_id == target_artifact.artifact_id
        or source_artifact.transaction_id != target_artifact.transaction_id
        or source_artifact.owner_root_id != target_artifact.owner_root_id
        or _canonical_bytes(source_plain["time_envelope"])
        != _canonical_bytes(target_plain["time_envelope"])
        or len(target_artifact.parent_refs)
        != len(set(target_artifact.parent_refs))
        or target_artifact.artifact_id in target_artifact.parent_refs
        or target_artifact.parent_refs.count(source_artifact.artifact_id) != 1
    ):
        return False

    parent_relation = dict(_FRACTAL_RUNTIME_PARENT_RELATION_BY_RULE_V02).get(
        rule.rule_id
    )
    if parent_relation is None:
        return False
    rule_index = int(rule.rule_id[5:7])
    source_parents = source_artifact.parent_refs
    parents = target_artifact.parent_refs
    if parent_relation == "ROUTE_TO_TOPOLOGY":
        if parents != (source_artifact.artifact_id,):
            return False
    elif parent_relation == "TOPOLOGY_TO_INITIAL_QUEUE":
        if not (
            parents == (source_artifact.artifact_id,)
            or (
                len(parents) == 2
                and parents[0] == source_artifact.artifact_id
                and _fractal_runtime_prefixed_digest_v02(
                    parents[1], "frabi_queue_v02:"
                )
            )
        ):
            return False
    elif parent_relation == "QUEUE_SUCCESSOR_NO_RESULT":
        if parents != (source_parents[0], source_artifact.artifact_id):
            return False
    elif parent_relation == "QUEUE_SUCCESSOR_RESULT_INTRODUCTION":
        if (
            len(parents) not in {2, 3}
            or parents[0] != source_parents[0]
            or parents[1] != source_artifact.artifact_id
            or (
                len(parents) == 3
                and not _fractal_runtime_prefixed_digest_v02(
                    parents[2], "frabi_result_v02:"
                )
            )
        ):
            return False
    elif parent_relation == "QUEUE_SUCCESSOR_RESULT_PRESERVATION":
        expected_parents = (
            (source_parents[0], source_artifact.artifact_id)
            if len(source_parents) == 2
            else (
                source_parents[0],
                source_artifact.artifact_id,
                source_parents[2],
            )
        )
        if parents != expected_parents:
            return False
    elif parent_relation == "ROOT_RESULT_TO_REPORT":
        if (
            len(parents) < 2
            or parents[0] != source_parents[0]
            or parents[-1] != source_artifact.artifact_id
            or any(
                not _fractal_runtime_prefixed_digest_v02(
                    parent, "frabi_result_v02:"
                )
                for parent in parents[1:-1]
            )
        ):
            return False
    else:
        return False

    source_payload = _fractal_runtime_payload_v02(source_artifact)
    target_payload = _fractal_runtime_payload_v02(target_artifact)
    if source_payload is None or target_payload is None:
        return False
    if rule_index == 1:
        if not {
            "accepted_mode",
            "accepted_scope_ref",
        }.issubset(source_payload) or not {
            "accepted_mode",
            "accepted_scope_ref",
            "source_root_decision_artifact_id",
        }.issubset(target_payload):
            return False
        if (
            source_payload.get("accepted_mode")
            != target_payload.get("accepted_mode")
            or source_payload.get("accepted_scope_ref")
            != target_payload.get("accepted_scope_ref")
            or len(source_artifact.parent_refs) != 1
            or target_payload.get("source_root_decision_artifact_id")
            != source_artifact.parent_refs[0]
        ):
            return False
    elif rule_index == 2:
        target_topology_id = _fractal_runtime_queue_topology_context_v02(
            target_artifact
        )
        if (
            "topology_id" not in source_payload
            or not _fractal_runtime_prefixed_digest_v02(
                source_payload["topology_id"], "frtopology_v02:"
            )
            or target_topology_id is None
            or source_payload["topology_id"] != target_topology_id
            or "topology_seed_id" not in source_payload
            or "topology_seed_id" not in target_payload
            or source_payload["topology_seed_id"]
            != target_payload["topology_seed_id"]
            or target_artifact.trace_refs[0] != decision.decision_id
        ):
            return False
    elif 3 <= rule_index <= 12:
        source_topology_id = _fractal_runtime_queue_topology_context_v02(
            source_artifact
        )
        target_topology_id = _fractal_runtime_queue_topology_context_v02(
            target_artifact
        )
        if (
            source_topology_id is None
            or target_topology_id is None
            or source_topology_id != target_topology_id
            or target_artifact.trace_refs[0] != decision.decision_id
        ):
            return False
        for field_name in (
            "topology_seed_id",
            "cell_id",
            "parent_cell_id",
            "node_id",
        ):
            if (
                field_name not in source_payload
                or field_name not in target_payload
                or source_payload[field_name] != target_payload[field_name]
            ):
                return False
    else:
        if (
            "topology_id" in source_payload
            or "topology_id" in target_payload
            or "topology_seed_id" not in source_payload
            or "topology_seed_id" not in target_payload
            or source_payload["topology_seed_id"]
            != target_payload["topology_seed_id"]
            or type(target_artifact.trace_refs) is not tuple
            or len(target_artifact.trace_refs) < 2
            or any(
                type(ref) is not str or not ref
                for ref in target_artifact.trace_refs
            )
            or target_artifact.trace_refs[1] != decision.decision_id
        ):
            return False
    return True


def validate_fractal_runtime_transition_decision_v02(
    value: object,
    *,
    registry: TransitionRegistryV01,
    source_artifact: KernelArtifactV01,
    target_artifact: KernelArtifactV01,
) -> tuple[str, ...]:
    try:
        if validate_fractal_runtime_transition_registry_profile_v02(registry):
            return ("g2d_transition_profile_invalid",)
        if (
            not _fractal_runtime_transition_decision_structure_v02(value)
            or type(source_artifact) is not KernelArtifactV01
            or type(target_artifact) is not KernelArtifactV01
            or _validate_kernel_artifact_v01(source_artifact)
            or _validate_kernel_artifact_v01(target_artifact)
        ):
            return ("g2d_transition_decision_substituted",)
        assert type(value) is TransitionDecisionV01
        rule = {item.rule_id: item for item in registry.rules}.get(value.rule_id)
        if rule is None:
            return ("g2d_transition_decision_substituted",)
        if (
            value.registry_id != registry.registry_id
            or value.abi_major_version != rule.abi_major_version
            or value.source_artifact_type != rule.source_artifact_type
            or value.source_lifecycle_state != rule.source_lifecycle_state
            or value.actor_role != rule.actor_role
            or value.attempted_effect != rule.attempted_effect
            or value.target_artifact_type != rule.target_artifact_type
            or value.required_guards != rule.required_guards
            or value.satisfied_guards != rule.required_guards
            or value.missing_guards != ()
            or value.decision != rule.decision
            or value.reason_code != rule.reason_code
            or value.root_commit_required is not rule.root_commit_required
            or value.root_commit_present is not True
            or value.matched is not True
            or source_artifact.artifact_type != rule.source_artifact_type
            or source_artifact.lifecycle_state != rule.source_lifecycle_state
            or target_artifact.artifact_type != rule.target_artifact_type
            or not _fractal_runtime_artifact_pair_valid_v02(
                rule=rule,
                decision=value,
                source_artifact=source_artifact,
                target_artifact=target_artifact,
            )
        ):
            return ("g2d_transition_decision_substituted",)
        if value.decision_id != rebuild_fractal_runtime_transition_decision_identity_v02(value):
            return ("g2d_transition_decision_substituted",)
        return ()
    except Exception:
        return ("g2d_transition_decision_substituted",)


def fractal_runtime_transition_decision_to_plain_dict_v02(
    value: TransitionDecisionV01,
) -> dict[str, object]:
    try:
        if not _fractal_runtime_transition_decision_structure_v02(value):
            raise ValueError("g2d_transition_decision_substituted")
        if value.decision_id != rebuild_fractal_runtime_transition_decision_identity_v02(value):
            raise ValueError("g2d_transition_decision_substituted")
        result = _decision_plain(value)
        _canonical_json_bytes_v01(result)
        return result
    except Exception:
        raise ValueError("g2d_transition_decision_substituted") from None


def rebuild_fractal_runtime_transition_decision_identity_v02(
    value: TransitionDecisionV01,
) -> str:
    try:
        if not _fractal_runtime_transition_decision_structure_v02(value):
            raise ValueError("g2d_transition_decision_substituted")
        material = _decision_plain(value)
        material.pop("decision_id")
        return _hash(_DECISION_DOMAIN, material)
    except Exception:
        raise ValueError("g2d_transition_decision_substituted") from None
