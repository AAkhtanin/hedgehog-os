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
    LIFECYCLE_STATES as _LIFECYCLE_STATES,
    build_action_packet_lifecycle_profile_v01 as _build_action_packet_lifecycle_profile_v01,
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
