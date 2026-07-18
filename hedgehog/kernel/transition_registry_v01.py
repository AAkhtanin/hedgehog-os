"""Pure in-memory deterministic domain-neutral transition lookup for G1-C1.

The registry is immutable after construction and performs lookup only. It does
not mutate artifacts, execute transitions, call a provider or LLM, use a
network, filesystem, clock, random source, or domain import, dynamically
register policy, create permission, create a Root decision or FinalOutput, or
execute an effect. Unknown transitions fail closed.
"""

from __future__ import annotations

from dataclasses import dataclass as _dataclass

from hedgehog.kernel.abi_v01 import (
    ARTIFACT_TYPES as _ARTIFACT_TYPES,
    LIFECYCLE_STATES as _LIFECYCLE_STATES,
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
