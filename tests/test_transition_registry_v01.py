from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, fields, replace
import inspect
import json
from pathlib import Path

import pytest

import hedgehog.kernel as kernel_package
from hedgehog.kernel.abi_v01 import ARTIFACT_TYPES, LIFECYCLE_STATES
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
    assert observed == PUBLIC_FUNCTIONS


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
