from __future__ import annotations

import ast
import copy
import inspect
import json
import pickle
from dataclasses import FrozenInstanceError, fields, is_dataclass, replace
from functools import wraps
from pathlib import Path

import pytest

import hedgehog.kernel as kernel_package
import hedgehog.kernel.effect_firewall_v01 as subject
from demo.run_living_gauntlet_v01 import (
    _build_semantic_work_fixture_v01,
    _root_decision_base_states_v01,
)
from hedgehog.kernel.abi_v01 import (
    KernelArtifactV01,
    build_kernel_artifact_v01,
    kernel_artifact_to_plain_dict_v01,
)
from hedgehog.kernel.integrity_replay_v01 import canonical_json_bytes_v01
from hedgehog.kernel.root_decision_v01 import (
    ROOT_DECISION_ACCEPT,
    build_root_decision_input_v01,
    build_root_decision_kernel_v01,
    decide_root_v01,
    root_decision_input_to_plain_dict_v01,
    root_decision_result_to_plain_dict_v01,
    validate_root_decision_result_v01,
)


REQUEST_FIELDS = (
    "request_id",
    "request_kind",
    "transaction_id",
    "target_root_id",
    "root_decision_id",
    "selected_candidate_id",
    "permission_ref",
    "adapter_id",
    "action_kind",
    "scope_refs",
    "issued_at_tick",
    "expires_at_tick",
    "idempotency_key",
    "mock_only",
)

# Contract section 6 adds native values and the exclusive native start, without
# changing the existing thirteen functions or the package export surface.
NATIVE_PUBLIC_FUNCTIONS = (
    'capability_value_subject_sha256_v01',
    'validate_capability_field_v01', 'build_capability_field_v01',
    'validate_capability_values_v01', 'build_capability_business_input_binding_v01',
    'build_capability_business_semantics_v01', 'validate_capability_definition_v01',
    'build_capability_definition_v01', 'validate_capability_admission_snapshot_v01',
    'validate_admitted_capability_v01', 'snapshot_admitted_capability_v01',
    'validate_capability_business_binding_v01', 'build_capability_validation_evidence_v01',
    'validate_bound_capability_invocation_v01', 'build_bound_capability_invocation_v01',
    'validate_capability_execution_result_v01', 'build_capability_execution_result_v01',
    'native_execution_evidence_to_plain_data_v01', 'native_execution_evidence_from_plain_data_v01',
    'validate_native_execution_evidence_v01', 'build_native_effect_receipt_v01',
    'validate_native_effect_receipt_v01', 'validate_retained_native_effect_receipt_v01',
    'bind_native_action_authorization_v01', 'execute_bound_effect_v01',
)

# Only nominal carriers, canonical material and pure contextual validation may
# cross this deferred edge. No Root decision or lifecycle execution is admitted.
NATIVE_DEFERRED_ACTION_ACCESS = {
    '_native_value': ('ABSENT_V01', 'ActionEffectParameterRecordV01',
        'action_effect_parameter_record_material_v01', 'validate_action_effect_parameter_record_v01'),
    '_native_identity': ('build_domain_separated_identity_v01', 'canonical_material_bytes_v01',
        'domain_separated_sha256_hex_v01'),
    'capability_value_subject_sha256_v01': ('ActionEffectParameterRecordV01', 'validate_action_effect_parameter_record_v01'),
    '_capability_scalar_valid': ('validate_canonical_decimal_v01', 'validate_identity_text_v01', 'validate_signed_int64_v01'),
    'validate_capability_values_v01': ('ActionEffectParameterRecordV01', 'validate_action_effect_parameter_record_v01'),
    'validate_capability_business_binding_v01': ('NativeActionCommitPacketV01',),
    '_native_plain': ('ActionEffectParameterRecordV01',),
    '_native_read': ('ActionEffectParameterRecordV01',),
    '_native_receipt_material_value_v01': ('ABSENT_V01',),
    'bind_native_action_authorization_v01': ('NativeRootBoundActionCommitPacketV01',
        'validate_action_packet_effect_firewall_projection_v01'),
}


def _native_deferred_action_errors(source):
    tree = ast.parse(source)
    parents = {child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
    errors = []
    for top in tree.body:
        allowed = NATIVE_DEFERRED_ACTION_ACCESS.get(top.name, ()) if isinstance(top, ast.FunctionDef) else ()
        body_nodes = set(n for stmt in top.body for n in ast.walk(stmt)) if isinstance(top, ast.FunctionDef) else set()
        for node in ast.walk(top):
            if isinstance(node, ast.ImportFrom) and any('action_commit_packet' in a.name for a in node.names):
                if not (node in body_nodes and allowed and node.module == 'hedgehog' and
                    [(a.name, a.asname) for a in node.names] == [('action_commit_packet_v02', 'action')]):
                    errors.append('action_import_location')
            if isinstance(node, ast.Import) and any('action_commit_packet' in a.name for a in node.names):
                errors.append('action_import_form')
            if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) and node.value.id == 'action':
                if node not in body_nodes or node.attr not in allowed:
                    errors.append('action_access_not_pure_allowlisted')
            if isinstance(node, ast.Name) and node.id == 'action' and isinstance(node.ctx, ast.Load):
                if not isinstance(parents.get(node), ast.Attribute) or parents[node].value is not node:
                    errors.append('action_alias_or_dynamic_access')
            if isinstance(node, ast.Call) and node not in body_nodes and isinstance(node.func, ast.Name) and (
                node.func.id in NATIVE_DEFERRED_ACTION_ACCESS or node.func.id in NATIVE_PUBLIC_FUNCTIONS or
                node.func.id == '_admit_observed_capability_v01'):
                errors.append('native_initialization_call')
    return tuple(errors)


def test_native_deferred_access_policy_rejects_initialization_and_runtime_neighbors():
    for source in (
        'from hedgehog import action_commit_packet_v02 as action\n',
        'def _native_value(value=action.NativeActionCommitPacketV01()):\n    return value\n',
        '@action.validate_native_action_commit_packet_v01\ndef _native_value(value):\n    return value\n',
        'class X:\n    value = action.NativeActionCommitPacketV01()\n',
        'value = _native_value(None)\n',
        'def _native_value(value):\n    from hedgehog import action_commit_packet_v02 as action\n    return action.execute_action_packet_mock_fulfillment_v01(value)\n',
        'def _native_value(value):\n    from hedgehog import action_commit_packet_v02 as action\n    alias = action\n    return alias\n',
        'class X:\n    value = _admit_observed_capability_v01()\n',
    ):
        assert _native_deferred_action_errors(source), source
    assert _native_deferred_action_errors('def _native_value(value):\n    from hedgehog import action_commit_packet_v02 as action\n    return action.ABSENT_V01\n') == ()


def test_native_boundary_real_fresh_import_orders():
    import subprocess
    import sys
    for modules in (('hedgehog.action_commit_packet_v02', 'hedgehog.kernel.effect_firewall_v01'),
                    ('hedgehog.kernel.effect_firewall_v01', 'hedgehog.action_commit_packet_v02')):
        code = ('import ' + modules[0] + '\nimport ' + modules[1] +
            '\nfrom hedgehog.kernel import effect_firewall_v01 as f\n'
            'v=f.build_capability_field_v01(name="value",value_type="INTEGER",required=True,consequential=False)\n'
            'if f.validate_capability_field_v01(v): raise RuntimeError("fresh_import_value_invalid")\n')
        result = subprocess.run([sys.executable, '-B', '-c', code], capture_output=True, text=True, check=False)
        assert (result.returncode, result.stdout, result.stderr) == (0, '', '')
DECISION_FIELDS = (
    "decision_id",
    "firewall_id",
    "invocation_id",
    "request_id",
    "transaction_id",
    "target_root_id",
    "root_decision_id",
    "adapter_id",
    "action_kind",
    "evaluated_at_tick",
    "decision",
    "reason_code",
    "capability_id",
    "capability_issued",
    "return_to_root",
    "real_world_effects_count",
)
FIREWALL_PUBLIC_FIELDS = (
    "firewall_id",
    "firewall_version",
    "invocation_id",
    "transaction_id",
    "target_root_id",
    "root_decision_id",
    "selected_candidate_id",
    "permission_ref",
    "allowed_adapter_ids",
    "allowed_action_kinds",
    "root_scope_refs",
    "maximum_expires_at_tick",
    "mock_only",
    "effect_access_owner",
)
HISTORICAL_AUTHORIZATION_FIELDS = (
    "profile_id",
    "firewall_id",
    "request",
    "decision",
    "expected_capability_id",
    "fresh_empty_invocation_state",
    "firewall_object_created",
    "capability_object_created",
    "real_world_effects_count",
)
CAPABILITY_PROPERTIES = (
    "capability_id",
    "firewall_id",
    "invocation_id",
    "request_id",
    "transaction_id",
    "target_root_id",
    "root_decision_id",
    "selected_candidate_id",
    "permission_ref",
    "adapter_id",
    "action_kind",
    "scope_refs",
    "expires_at_tick",
)
PACKAGE_EFFECT_FUNCTIONS = (
    "build_effect_firewall_v01",
    "validate_effect_firewall_v01",
    "build_effect_request_v01",
    "validate_effect_request_v01",
    "authorize_effect_request_v01",
    "validate_effect_firewall_decision_v01",
    "execute_mock_effect_v01",
    "validate_effect_receipt_v01",
    "effect_request_to_plain_dict_v01",
    "effect_firewall_decision_to_plain_dict_v01",
    "effect_firewall_to_plain_dict_v01",
)
HISTORICAL_PUBLIC_FUNCTIONS = (
    "project_effect_firewall_historical_authorization_v01",
    "validate_effect_firewall_historical_authorization_projection_v01",
)
PUBLIC_FUNCTIONS = PACKAGE_EFFECT_FUNCTIONS + HISTORICAL_PUBLIC_FUNCTIONS
TIME_ENVELOPE = {
    "pt_created_at": "2026-01-01T00:00:00+00:00",
    "kt_asof": "2026-01-01T00:00:00+00:00",
    "et_observed_at": None,
    "ct_session_anchor": "session:fixture:effect_firewall:001",
    "ttl_seconds": 3600,
    "freshness_class": "static",
    "valid_from": "2026-01-01T00:00:00+00:00",
    "valid_to": "2026-01-01T01:00:00+00:00",
}


def _root_context(*, permission_state: dict[str, object] | None = None):
    packet = _build_semantic_work_fixture_v01()[3]
    kernel = build_root_decision_kernel_v01()
    states = _root_decision_base_states_v01(packet)
    states["permission_state"] = permission_state or {
        "permission_required": True,
        "user_permission_present": True,
        "permission_scope_valid": True,
        "permission_ref": "permission:fixture:effect_firewall:001",
    }
    decision_input = build_root_decision_input_v01(
        transaction_id=packet.transaction_id,
        target_root_id=packet.target_root_id,
        root_review_packet=packet,
        **states,
    )
    result = decide_root_v01(kernel=kernel, decision_input=decision_input)
    return packet, kernel, decision_input, result


def _firewall(*, adapters=None, actions=None, scopes=None, maximum=200):
    _, kernel, decision_input, result = _root_context()
    firewall = subject.build_effect_firewall_v01(
        root_decision_kernel=kernel,
        decision_input=decision_input,
        root_decision_result=result,
        invocation_id="invocation:fixture:effect_firewall:001",
        allowed_adapter_ids=adapters
        or ("mock_adapter:bounded_neutral_v01",),
        allowed_action_kinds=actions
        or ("mock_action:record_neutral_receipt",),
        root_scope_refs=scopes or ("scope:neutral:alpha", "scope:neutral:beta"),
        maximum_expires_at_tick=maximum,
    )
    return kernel, decision_input, result, firewall


def _request(
    *,
    request_kind="ActionCommitPacket",
    adapter="mock_adapter:bounded_neutral_v01",
    action="mock_action:record_neutral_receipt",
    scopes=("scope:neutral:alpha",),
    issued=100,
    expires=150,
    key="idempotency:fixture:effect_firewall:001",
):
    kernel, decision_input, result, firewall = _firewall()
    request = subject.build_effect_request_v01(
        root_decision_kernel=kernel,
        decision_input=decision_input,
        root_decision_result=result,
        request_kind=request_kind,
        adapter_id=adapter,
        action_kind=action,
        scope_refs=scopes,
        issued_at_tick=issued,
        expires_at_tick=expires,
        idempotency_key=key,
    )
    return kernel, decision_input, result, firewall, request


def _authorized():
    *context, firewall, request = _request()
    decision = subject.authorize_effect_request_v01(
        firewall=firewall, request=request, current_tick=110
    )
    return (*context, firewall, request, decision)


def _executed():
    *context, firewall, request, decision = _authorized()
    receipt = subject.execute_mock_effect_v01(
        firewall=firewall,
        request=request,
        decision=decision,
        current_tick=120,
        adapter_id=request.adapter_id,
        action_kind=request.action_kind,
        child_scope_refs=("scope:neutral:alpha",),
        child_expires_at_tick=140,
        receipt_artifact_id="receipt:fixture:effect_firewall:001",
        time_envelope=TIME_ENVELOPE,
    )
    return (*context, firewall, request, decision, receipt)


def _rehash_request(request, **changes):
    changed = replace(request, **changes)
    return replace(changed, request_id=subject._request_id(changed))


def _rehash_firewall(firewall, **changes):
    changed = replace(firewall, **changes)
    return replace(
        changed,
        firewall_id=subject._hash(
            subject._FIREWALL_DOMAIN,
            subject._firewall_plain(changed, include_id=False),
        ),
    )


def _rehash_decision(decision, **changes):
    changed = replace(decision, **changes)
    return replace(changed, decision_id=subject._decision_id(changed))


def _rebuild_receipt(receipt, *, payload_changes=None, **envelope_changes):
    plain = kernel_artifact_to_plain_dict_v01(receipt)
    payload = plain["payload"]
    payload.update(payload_changes or {})
    plain.update(envelope_changes)
    return build_kernel_artifact_v01(
        abi_version=plain["abi_version"],
        artifact_id=plain["artifact_id"],
        artifact_type=plain["artifact_type"],
        schema_version=plain["schema_version"],
        transaction_id=plain["transaction_id"],
        owner_root_id=plain["owner_root_id"],
        source_component=plain["source_component"],
        authority_class=plain["authority_class"],
        lifecycle_state=plain["lifecycle_state"],
        payload=payload,
        trace_refs=tuple(plain["trace_refs"]),
        parent_refs=tuple(plain["parent_refs"]),
        time_envelope=plain["time_envelope"],
    )


def _pre_execution_receipt(request, decision, *, artifact_id="receipt:precommit:001"):
    return build_kernel_artifact_v01(
        abi_version="v1.0",
        artifact_id=artifact_id,
        artifact_type="EvidenceReceipt",
        schema_version="v1",
        transaction_id=request.transaction_id,
        owner_root_id=request.target_root_id,
        source_component=subject.RECEIPT_SOURCE_COMPONENT,
        authority_class="EVIDENCE_ONLY",
        lifecycle_state="RECEIPT_RECORDED",
        payload={
            "receipt_ref": artifact_id,
            "request_id": request.request_id,
            "firewall_decision_id": decision.decision_id,
            "capability_id": decision.capability_id,
            "root_decision_id": request.root_decision_id,
            "selected_candidate_id": request.selected_candidate_id,
            "permission_ref": request.permission_ref,
            "adapter_id": request.adapter_id,
            "action_kind": request.action_kind,
            "scope_refs": ["scope:neutral:alpha"],
            "mock_execution_status": "PASS",
            "receipt_evidence_only": True,
            "root_confirmation_required": True,
            "root_confirmation_created": False,
            "future_permission_created": False,
            "root_decision_created": False,
            "final_output_created": False,
            "effect_handle_exposed": False,
            "real_world_effects_count": 0,
        },
        trace_refs=(request.request_id, request.root_decision_id, decision.decision_id),
        parent_refs=(request.root_decision_id,),
        time_envelope=TIME_ENVELOPE,
    )


def _private_state_snapshot(firewall):
    state = firewall._state
    return (
        set(state.seen_request_ids),
        set(state.used_idempotency_keys),
        dict(state.issued_capabilities),
        dict(state.idempotency_key_by_request_id),
        dict(state.authorization_decision_id_by_capability_id),
        set(state.consumed_capability_ids),
        set(state.terminal_receipt_ids),
        dict(state.terminal_receipt_id_by_capability_id),
        state.mock_effect_execution_count,
    )


def _execute_authorized(firewall, request, decision, receipt_id):
    return subject.execute_mock_effect_v01(
        firewall=firewall,
        request=request,
        decision=decision,
        current_tick=120,
        adapter_id=request.adapter_id,
        action_kind=request.action_kind,
        child_scope_refs=("scope:neutral:alpha",),
        child_expires_at_tick=140,
        receipt_artifact_id=receipt_id,
        time_envelope=TIME_ENVELOPE,
    )


@pytest.mark.parametrize(
    ("name", "expected"),
    (
        ("MODULE_ID", "kernel_effect_firewall_v01"),
        ("SLICE_ID", "domain_neutral_reference_kernel_gate1_g1c2"),
        ("EFFECT_FIREWALL_VERSION", "v0.1"),
        ("STATUS_PASS", "PASS"),
        ("STATUS_BLOCKED_FAIL_CLOSED", "BLOCKED_FAIL_CLOSED"),
        ("EFFECT_DECISION_ALLOW_MOCK_EFFECT", "ALLOW_MOCK_EFFECT"),
        ("EFFECT_DECISION_BLOCKED_FAIL_CLOSED", "BLOCKED_FAIL_CLOSED"),
        ("EFFECT_ACCESS_OWNER", "EFFECT_FIREWALL_ONLY"),
        ("MOCK_ADAPTER_PREFIX", "mock_adapter:"),
        ("MOCK_ACTION_PREFIX", "mock_action:"),
        ("RECEIPT_SOURCE_COMPONENT", "effect_firewall"),
        (
            "EFFECT_FIREWALL_HISTORICAL_AUTHORIZATION_PROFILE_ID_V01",
            "effect_firewall_historical_authorization_projection_v01",
        ),
        ("NoExpansionAfterRoot", True),
    ),
)
def test_exact_scalar_constant(name, expected):
    assert getattr(subject, name) == expected


@pytest.mark.parametrize(
    ("name", "expected"),
    (
        ("EFFECT_FIREWALL_DECISIONS", ("ALLOW_MOCK_EFFECT", "BLOCKED_FAIL_CLOSED")),
        ("EFFECT_REQUEST_KINDS", ("ExecutionRequest", "ActionCommitPacket")),
    ),
)
def test_exact_immutable_tuple_constant(name, expected):
    value = getattr(subject, name)
    assert type(value) is tuple
    assert value == expected


@pytest.mark.parametrize(
    ("contract", "expected"),
    (
        (subject.EffectRequestV01, REQUEST_FIELDS),
        (subject.EffectFirewallDecisionV01, DECISION_FIELDS),
        (
            subject.EffectFirewallV01,
            FIREWALL_PUBLIC_FIELDS + ("_issuer_token", "_state"),
        ),
        (
            subject.EffectFirewallHistoricalAuthorizationProjectionV01,
            HISTORICAL_AUTHORIZATION_FIELDS,
        ),
    ),
)
def test_exact_dataclass_field_order(contract, expected):
    assert tuple(field.name for field in fields(contract)) == expected


@pytest.mark.parametrize(
    "contract",
    (subject.EffectRequestV01, subject.EffectFirewallDecisionV01, subject.EffectFirewallV01),
)
def test_public_dataclasses_are_frozen_and_slotted(contract):
    assert is_dataclass(contract)
    assert "__dict__" not in contract.__slots__
    instance = {subject.EffectRequestV01: _request()[-1], subject.EffectFirewallDecisionV01: _authorized()[-1], subject.EffectFirewallV01: _firewall()[-1]}[contract]
    with pytest.raises(FrozenInstanceError):
        instance.mock_only = False


@pytest.mark.parametrize("name", CAPABILITY_PROPERTIES)
def test_capability_exact_read_only_property_surface(name):
    descriptor = vars(subject.EffectCapabilityV01)[name]
    assert isinstance(descriptor, property)
    assert descriptor.fset is None


def test_capability_property_set_is_exact():
    public = {
        name
        for name, value in vars(subject.EffectCapabilityV01).items()
        if isinstance(value, property)
    }
    assert public == set(CAPABILITY_PROPERTIES)


@pytest.mark.parametrize("name", PUBLIC_FUNCTIONS)
def test_exact_public_function_exists(name):
    assert inspect.isfunction(getattr(subject, name))


def test_exact_public_function_surface():
    public_functions = {
        name
        for name, value in vars(subject).items()
        if inspect.isfunction(value) and not name.startswith("_")
    }
    assert public_functions == set(PUBLIC_FUNCTIONS + NATIVE_PUBLIC_FUNCTIONS)


@pytest.mark.parametrize(
    "name",
    (
        "EffectRequestV01",
        "EffectFirewallDecisionV01",
        "EffectFirewallV01",
        "EffectCapabilityV01",
    )
    + PACKAGE_EFFECT_FUNCTIONS,
)
def test_direct_package_attribute_exists(name):
    assert getattr(kernel_package, name) is getattr(subject, name)


def test_package_all_remains_committed_legacy_surface():
    assert kernel_package.__all__ == (
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


@pytest.mark.parametrize(
    "name",
    (
        "issue_effect_capability",
        "get_effect_capability",
        "export_effect_capability",
        "serialize_effect_capability",
        "transfer_effect_capability",
        "register_adapter",
        "register_provider",
        "register_domain",
        "register_callback",
        "execute_real_effect",
        "execute_connector",
        "execute_payment",
        "execute_shipment",
        "revoke",
        "supersede",
        "effect_capability_to_plain_dict_v01",
    ),
)
def test_forbidden_public_api_absent(name):
    assert not hasattr(subject, name)


@pytest.mark.parametrize("name", PUBLIC_FUNCTIONS)
def test_public_signature_has_no_capability_boundary(name):
    signature = inspect.signature(getattr(subject, name))
    rendered = str(signature)
    assert "EffectCapabilityV01" not in rendered


def test_capability_has_no_public_constructor():
    with pytest.raises(TypeError):
        subject.EffectCapabilityV01()


def test_valid_root_context_is_accept_and_stable():
    _, kernel, decision_input, result = _root_context()
    before_input = root_decision_input_to_plain_dict_v01(decision_input)
    before_result = root_decision_result_to_plain_dict_v01(result)
    assert result.decision == ROOT_DECISION_ACCEPT
    assert validate_root_decision_result_v01(
        kernel=kernel, decision_input=decision_input, result=result
    ) == ()
    _firewall()
    assert root_decision_input_to_plain_dict_v01(decision_input) == before_input
    assert root_decision_result_to_plain_dict_v01(result) == before_result


@pytest.mark.parametrize(
    "permission_state",
    (
        {"permission_required": False, "user_permission_present": False, "permission_scope_valid": True, "permission_ref": None},
        {"permission_required": False, "user_permission_present": True, "permission_scope_valid": True, "permission_ref": "permission:x"},
        {"permission_required": True, "user_permission_present": False, "permission_scope_valid": True, "permission_ref": None},
        {"permission_required": True, "user_permission_present": True, "permission_scope_valid": False, "permission_ref": "permission:x"},
        {"permission_required": True, "user_permission_present": True, "permission_scope_valid": True, "permission_ref": "receipt:x"},
        {"permission_required": True, "user_permission_present": True, "permission_scope_valid": True, "permission_ref": "evidence:x"},
        {"permission_required": True, "user_permission_present": True, "permission_scope_valid": True, "permission_ref": "decision:x"},
        {"permission_required": True, "user_permission_present": True, "permission_scope_valid": True, "permission_ref": "capability:x"},
    ),
)
def test_firewall_rejects_nonaccepted_permission_contexts(permission_state):
    _, kernel, decision_input, result = _root_context(permission_state=permission_state)
    with pytest.raises(ValueError, match="^effect_firewall_binding_invalid$"):
        subject.build_effect_firewall_v01(
            root_decision_kernel=kernel,
            decision_input=decision_input,
            root_decision_result=result,
            invocation_id="invocation:x",
            allowed_adapter_ids=("mock_adapter:x",),
            allowed_action_kinds=("mock_action:x",),
            root_scope_refs=("scope:x",),
            maximum_expires_at_tick=1,
        )


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("decision", "REJECT"),
        ("root_commit_created", False),
        ("selected_candidate_id", None),
        ("permission_created", True),
        ("final_output_created", True),
        ("effect_requested", True),
        ("transaction_id", "txn:other"),
        ("target_root_id", "root:other"),
        ("decision_input_id", "0" * 64),
    ),
)
def test_firewall_rejects_forged_root_result(field, value):
    _, kernel, decision_input, result = _root_context()
    forged = replace(result, **{field: value})
    with pytest.raises(ValueError, match="^effect_firewall_binding_invalid$"):
        subject.build_effect_firewall_v01(
            root_decision_kernel=kernel,
            decision_input=decision_input,
            root_decision_result=forged,
            invocation_id="invocation:x",
            allowed_adapter_ids=("mock_adapter:x",),
            allowed_action_kinds=("mock_action:x",),
            root_scope_refs=("scope:x",),
            maximum_expires_at_tick=1,
        )


@pytest.mark.parametrize(
    ("adapters", "actions", "scopes", "maximum"),
    (
        (("mock_adapter:a",), ("mock_action:a",), ("scope:a",), 1),
        (("mock_adapter:a", "mock_adapter:b"), ("mock_action:a",), ("scope:a",), 50),
        (("mock_adapter:a",), ("mock_action:a", "mock_action:b"), ("scope:a",), 50),
        (("mock_adapter:a",), ("mock_action:a",), ("scope:a", "scope:b"), 50),
        (("mock_adapter:a", "mock_adapter:b"), ("mock_action:a", "mock_action:b"), ("scope:a", "scope:b"), 999),
    ),
)
def test_firewall_valid_construction_matrix(adapters, actions, scopes, maximum):
    firewall = _firewall(adapters=adapters, actions=actions, scopes=scopes, maximum=maximum)[-1]
    assert subject.validate_effect_firewall_v01(firewall) == ()
    assert subject.effect_firewall_to_plain_dict_v01(firewall)["state_counters"]["issued_capability_count"] == 0


def test_identical_firewalls_have_equal_public_identity_distinct_issuers():
    first = _firewall()[-1]
    second = _firewall()[-1]
    assert first.firewall_id == second.firewall_id
    assert subject.effect_firewall_to_plain_dict_v01(first) == subject.effect_firewall_to_plain_dict_v01(second)
    assert first._issuer_token is not second._issuer_token
    assert first._state is not second._state


@pytest.mark.parametrize(
    ("kwargs", "reason"),
    (
        ({"invocation_id": ""}, "effect_firewall_binding_invalid"),
        ({"invocation_id": "\ud800"}, "effect_firewall_binding_invalid"),
        ({"allowed_adapter_ids": []}, "effect_firewall_adapter_policy_invalid"),
        ({"allowed_adapter_ids": ()}, "effect_firewall_adapter_policy_invalid"),
        ({"allowed_adapter_ids": ("mock_adapter:a", "mock_adapter:a")}, "effect_firewall_adapter_policy_invalid"),
        ({"allowed_adapter_ids": ("adapter:real",)}, "effect_firewall_adapter_policy_invalid"),
        ({"allowed_action_kinds": []}, "effect_firewall_action_policy_invalid"),
        ({"allowed_action_kinds": ()}, "effect_firewall_action_policy_invalid"),
        ({"allowed_action_kinds": ("mock_action:a", "mock_action:a")}, "effect_firewall_action_policy_invalid"),
        ({"allowed_action_kinds": ("action:real",)}, "effect_firewall_action_policy_invalid"),
        ({"root_scope_refs": []}, "effect_firewall_scope_invalid"),
        ({"root_scope_refs": ()}, "effect_firewall_scope_invalid"),
        ({"root_scope_refs": ("scope:a", "scope:a")}, "effect_firewall_scope_invalid"),
        ({"root_scope_refs": ("",)}, "effect_firewall_scope_invalid"),
        ({"maximum_expires_at_tick": True}, "effect_firewall_time_invalid"),
        ({"maximum_expires_at_tick": 0}, "effect_firewall_time_invalid"),
        ({"maximum_expires_at_tick": -1}, "effect_firewall_time_invalid"),
        ({"maximum_expires_at_tick": "1"}, "effect_firewall_time_invalid"),
    ),
)
def test_firewall_builder_rejects_invalid_configuration(kwargs, reason):
    _, kernel, decision_input, result = _root_context()
    values = {
        "invocation_id": "invocation:x",
        "allowed_adapter_ids": ("mock_adapter:x",),
        "allowed_action_kinds": ("mock_action:x",),
        "root_scope_refs": ("scope:x",),
        "maximum_expires_at_tick": 10,
    }
    values.update(kwargs)
    with pytest.raises(ValueError, match=f"^{reason}$"):
        subject.build_effect_firewall_v01(
            root_decision_kernel=kernel,
            decision_input=decision_input,
            root_decision_result=result,
            **values,
        )


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    (
        ("firewall_id", "0" * 64, "effect_firewall_id_mismatch"),
        ("firewall_version", "v0.2", "effect_firewall_invalid"),
        ("invocation_id", "", "effect_firewall_binding_invalid"),
        ("transaction_id", "", "effect_firewall_binding_invalid"),
        ("target_root_id", "", "effect_firewall_binding_invalid"),
        ("root_decision_id", "", "effect_firewall_binding_invalid"),
        ("selected_candidate_id", "", "effect_firewall_binding_invalid"),
        ("permission_ref", "receipt:x", "effect_firewall_binding_invalid"),
        ("allowed_adapter_ids", [], "effect_firewall_adapter_policy_invalid"),
        ("allowed_adapter_ids", ("adapter:x",), "effect_firewall_adapter_policy_invalid"),
        ("allowed_action_kinds", [], "effect_firewall_action_policy_invalid"),
        ("allowed_action_kinds", ("action:x",), "effect_firewall_action_policy_invalid"),
        ("root_scope_refs", [], "effect_firewall_scope_invalid"),
        ("root_scope_refs", ("scope:x", "scope:x"), "effect_firewall_scope_invalid"),
        ("maximum_expires_at_tick", True, "effect_firewall_time_invalid"),
        ("maximum_expires_at_tick", 0, "effect_firewall_time_invalid"),
        ("mock_only", False, "effect_firewall_mock_only_required"),
        ("effect_access_owner", "OTHER", "effect_firewall_effect_owner_invalid"),
    ),
)
def test_firewall_validator_detects_manual_mutation(field, value, reason):
    firewall = replace(_firewall()[-1], **{field: value})
    assert reason in subject.validate_effect_firewall_v01(firewall)


def test_firewall_rejects_foreign_token_and_state():
    first = _firewall()[-1]
    second = _firewall()[-1]
    assert "effect_firewall_state_invalid" in subject.validate_effect_firewall_v01(
        replace(first, _issuer_token=second._issuer_token)
    )
    assert "effect_firewall_state_invalid" in subject.validate_effect_firewall_v01(
        replace(first, _state=second._state)
    )


@pytest.mark.parametrize("request_kind", subject.EFFECT_REQUEST_KINDS)
def test_both_request_kinds_build_and_validate(request_kind):
    request = _request(request_kind=request_kind)[-1]
    assert request.request_kind == request_kind
    assert subject.validate_effect_request_v01(request) == ()


@pytest.mark.parametrize(
    ("scopes", "issued", "expires"),
    (
        (("scope:neutral:alpha",), 0, 1),
        (("scope:neutral:alpha", "scope:neutral:beta"), 0, 200),
        (("scope:neutral:beta",), 100, 101),
        (("scope:neutral:alpha",), 999, 1000),
    ),
)
def test_request_logical_time_and_scope_positive_matrix(scopes, issued, expires):
    request = _request(scopes=scopes, issued=issued, expires=expires)[-1]
    assert request.scope_refs == scopes
    assert subject.validate_effect_request_v01(request) == ()


def test_request_identity_and_projection_are_deterministic():
    first = _request()[-1]
    second = _request()[-1]
    assert first.request_id == second.request_id
    assert subject.effect_request_to_plain_dict_v01(first) == subject.effect_request_to_plain_dict_v01(second)
    assert first.permission_ref == "permission:fixture:effect_firewall:001"
    assert first.selected_candidate_id
    assert first.mock_only is True


@pytest.mark.parametrize(
    ("kwargs", "reason"),
    (
        ({"request_kind": "Unknown"}, "effect_request_kind_unknown"),
        ({"request_kind": 1}, "effect_request_kind_unknown"),
        ({"adapter_id": ""}, "effect_request_adapter_invalid"),
        ({"adapter_id": "adapter:real"}, "effect_request_adapter_invalid"),
        ({"adapter_id": "\ud800"}, "effect_request_adapter_invalid"),
        ({"action_kind": ""}, "effect_request_action_invalid"),
        ({"action_kind": "action:real"}, "effect_request_action_invalid"),
        ({"action_kind": "\ud800"}, "effect_request_action_invalid"),
        ({"scope_refs": []}, "effect_request_scope_invalid"),
        ({"scope_refs": ()}, "effect_request_scope_invalid"),
        ({"scope_refs": ("scope:a", "scope:a")}, "effect_request_scope_invalid"),
        ({"scope_refs": ("",)}, "effect_request_scope_invalid"),
        ({"issued_at_tick": True}, "effect_request_time_invalid"),
        ({"issued_at_tick": -1}, "effect_request_time_invalid"),
        ({"issued_at_tick": "0"}, "effect_request_time_invalid"),
        ({"expires_at_tick": True}, "effect_request_time_invalid"),
        ({"issued_at_tick": 10, "expires_at_tick": 10}, "effect_request_time_invalid"),
        ({"issued_at_tick": 10, "expires_at_tick": 9}, "effect_request_time_invalid"),
        ({"idempotency_key": ""}, "effect_request_idempotency_invalid"),
        ({"idempotency_key": "\ud800"}, "effect_request_idempotency_invalid"),
    ),
)
def test_request_builder_rejects_invalid_input(kwargs, reason):
    _, kernel, decision_input, result = _root_context()
    values = {
        "request_kind": "ActionCommitPacket",
        "adapter_id": "mock_adapter:x",
        "action_kind": "mock_action:x",
        "scope_refs": ("scope:x",),
        "issued_at_tick": 0,
        "expires_at_tick": 1,
        "idempotency_key": "idempotency:x",
    }
    values.update(kwargs)
    with pytest.raises(ValueError, match=f"^{reason}$"):
        subject.build_effect_request_v01(
            root_decision_kernel=kernel,
            decision_input=decision_input,
            root_decision_result=result,
            **values,
        )


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    (
        ("request_id", "0" * 64, "effect_request_id_mismatch"),
        ("request_kind", "Unknown", "effect_request_kind_unknown"),
        ("transaction_id", "", "effect_request_identity_invalid"),
        ("target_root_id", "", "effect_request_identity_invalid"),
        ("root_decision_id", "", "effect_request_identity_invalid"),
        ("selected_candidate_id", "", "effect_request_identity_invalid"),
        ("permission_ref", "receipt:x", "effect_request_permission_invalid"),
        ("adapter_id", "adapter:x", "effect_request_adapter_invalid"),
        ("action_kind", "action:x", "effect_request_action_invalid"),
        ("scope_refs", [], "effect_request_scope_invalid"),
        ("scope_refs", ("scope:x", "scope:x"), "effect_request_scope_invalid"),
        ("issued_at_tick", True, "effect_request_time_invalid"),
        ("issued_at_tick", -1, "effect_request_time_invalid"),
        ("expires_at_tick", True, "effect_request_time_invalid"),
        ("expires_at_tick", 100, "effect_request_time_invalid"),
        ("idempotency_key", "", "effect_request_idempotency_invalid"),
        ("mock_only", False, "effect_request_real_effect_forbidden"),
    ),
)
def test_request_validator_detects_manual_mutation(field, value, reason):
    malformed = replace(_request()[-1], **{field: value})
    assert reason in subject.validate_effect_request_v01(malformed)


def test_authorization_positive_path_and_state_commit():
    *_, firewall, request, decision = _authorized()
    assert decision.decision == "ALLOW_MOCK_EFFECT"
    assert decision.reason_code == "mock_effect_authorized"
    assert decision.capability_issued is True
    assert decision.return_to_root is False
    assert decision.real_world_effects_count == 0
    assert subject.validate_effect_firewall_decision_v01(
        firewall=firewall, request=request, decision=decision
    ) == ()
    counters = subject.effect_firewall_to_plain_dict_v01(firewall)["state_counters"]
    assert counters == {
        "seen_request_count": 1,
        "used_idempotency_key_count": 1,
        "issued_capability_count": 1,
        "consumed_capability_count": 0,
        "terminal_receipt_count": 0,
        "mock_effect_execution_count": 0,
        "real_world_effects_count": 0,
    }


def _authorization_case(reason):
    *_, firewall, request = _request()
    tick = 110
    if reason == "forged_request":
        request = replace(request, request_id="0" * 64)
    elif reason == "request_root_binding_mismatch":
        request = _rehash_request(request, root_decision_id="decision:other")
    elif reason == "permission_binding_mismatch":
        request = _rehash_request(request, permission_ref="permission:other")
    elif reason == "real_effect_forbidden":
        request = _rehash_request(request, mock_only=False)
    elif reason == "adapter_not_allowed":
        request = _rehash_request(request, adapter_id="mock_adapter:other")
    elif reason == "action_not_allowed":
        request = _rehash_request(request, action_kind="mock_action:other")
    elif reason == "scope_expansion_forbidden":
        request = _rehash_request(request, scope_refs=("scope:other",))
    elif reason == "ttl_expansion_forbidden":
        request = _rehash_request(request, expires_at_tick=201)
    elif reason == "request_not_yet_valid":
        tick = 99
    elif reason == "request_expired":
        tick = 150
    elif reason == "duplicate_request":
        subject.authorize_effect_request_v01(firewall=firewall, request=request, current_tick=tick)
    elif reason == "duplicate_idempotency_key":
        first = _rehash_request(request, idempotency_key="idempotency:shared")
        subject.authorize_effect_request_v01(firewall=firewall, request=first, current_tick=tick)
        request = _rehash_request(request, request_kind="ExecutionRequest", idempotency_key="idempotency:shared")
    return firewall, request, tick


@pytest.mark.parametrize("reason", subject._BLOCK_REASONS)
def test_every_authorization_reason_exact(reason):
    firewall, request, tick = _authorization_case(reason)
    before = subject.effect_firewall_to_plain_dict_v01(firewall)["state_counters"].copy()
    decision = subject.authorize_effect_request_v01(
        firewall=firewall, request=request, current_tick=tick
    )
    assert decision.decision == "BLOCKED_FAIL_CLOSED"
    assert decision.reason_code == reason
    assert decision.capability_id is None
    assert decision.capability_issued is False
    assert decision.return_to_root is True
    assert decision.real_world_effects_count == 0
    assert subject.validate_effect_firewall_decision_v01(
        firewall=firewall, request=request, decision=decision
    ) == ()
    assert subject.effect_firewall_to_plain_dict_v01(firewall)["state_counters"] == before


@pytest.mark.parametrize(
    ("changes", "tick", "expected"),
    (
        ({"root_decision_id": "other", "permission_ref": "permission:other"}, 200, "request_root_binding_mismatch"),
        ({"permission_ref": "permission:other", "mock_only": False}, 200, "permission_binding_mismatch"),
        ({"mock_only": False, "adapter_id": "mock_adapter:other"}, 200, "real_effect_forbidden"),
        ({"adapter_id": "mock_adapter:other", "action_kind": "mock_action:other"}, 200, "adapter_not_allowed"),
        ({"action_kind": "mock_action:other", "scope_refs": ("scope:other",)}, 200, "action_not_allowed"),
        ({"scope_refs": ("scope:other",), "expires_at_tick": 250}, 200, "scope_expansion_forbidden"),
        ({"expires_at_tick": 250}, 99, "ttl_expansion_forbidden"),
        ({}, 99, "request_not_yet_valid"),
        ({}, 150, "request_expired"),
    ),
)
def test_authorization_precedence(changes, tick, expected):
    *_, firewall, request = _request()
    request = _rehash_request(request, **changes) if changes else request
    decision = subject.authorize_effect_request_v01(firewall=firewall, request=request, current_tick=tick)
    assert decision.reason_code == expected


@pytest.mark.parametrize("current_tick", (None, True, -1, 1.0, "110", (), []))
def test_malformed_authorization_tick_raises_without_state(current_tick):
    *_, firewall, request = _request()
    before = subject.effect_firewall_to_plain_dict_v01(firewall)
    with pytest.raises(ValueError, match="^effect_authorization_invalid$"):
        subject.authorize_effect_request_v01(
            firewall=firewall, request=request, current_tick=current_tick
        )
    assert subject.effect_firewall_to_plain_dict_v01(firewall) == before


def test_two_fresh_firewalls_have_same_public_decision_and_distinct_capabilities():
    first = _authorized()
    second = _authorized()
    first_firewall, first_decision = first[-3], first[-1]
    second_firewall, second_decision = second[-3], second[-1]
    assert subject.effect_firewall_decision_to_plain_dict_v01(first_decision) == subject.effect_firewall_decision_to_plain_dict_v01(second_decision)
    assert first_decision.capability_id == second_decision.capability_id
    assert first_firewall._state.issued_capabilities[first_decision.capability_id] is not second_firewall._state.issued_capabilities[second_decision.capability_id]


@pytest.mark.parametrize("operation", ("copy", "deepcopy", "pickle", "json", "canonical"))
def test_capability_serialization_and_copy_are_rejected(operation):
    *_, firewall, _, decision = _authorized()
    capability = firewall._state.issued_capabilities[decision.capability_id]
    with pytest.raises((TypeError, ValueError)):
        {
            "copy": lambda: copy.copy(capability),
            "deepcopy": lambda: copy.deepcopy(capability),
            "pickle": lambda: pickle.dumps(capability),
            "json": lambda: json.dumps(capability),
            "canonical": lambda: canonical_json_bytes_v01(capability),
        }[operation]()


def test_capability_is_opaque_identity_object():
    *_, firewall, _, decision = _authorized()
    capability = firewall._state.issued_capabilities[decision.capability_id]
    assert not is_dataclass(capability)
    assert not hasattr(capability, "__dict__")
    assert repr(capability) == "EffectCapabilityV01(<opaque>)"
    assert capability == capability
    with pytest.raises(AttributeError):
        capability._adapter_id = "mock_adapter:other"


@pytest.mark.parametrize("name", CAPABILITY_PROPERTIES)
def test_issued_capability_property_matches_binding(name):
    *_, firewall, request, decision = _authorized()
    capability = firewall._state.issued_capabilities[decision.capability_id]
    expected = {
        "capability_id": decision.capability_id,
        "firewall_id": firewall.firewall_id,
        "invocation_id": firewall.invocation_id,
        "request_id": request.request_id,
        "transaction_id": request.transaction_id,
        "target_root_id": request.target_root_id,
        "root_decision_id": request.root_decision_id,
        "selected_candidate_id": request.selected_candidate_id,
        "permission_ref": request.permission_ref,
        "adapter_id": request.adapter_id,
        "action_kind": request.action_kind,
        "scope_refs": request.scope_refs,
        "expires_at_tick": request.expires_at_tick,
    }[name]
    assert getattr(capability, name) == expected


def test_capability_cross_firewall_and_forgery_rejected():
    first = _authorized()
    second = _authorized()
    firewall, request, decision = first[-3:]
    other_firewall = second[-3]
    capability = firewall._state.issued_capabilities[decision.capability_id]
    assert subject._capability_valid(capability, firewall, request)
    assert not subject._capability_valid(capability, other_firewall, request)
    forged = object.__new__(subject.EffectCapabilityV01)
    for slot in subject.EffectCapabilityV01.__slots__:
        object.__setattr__(forged, slot, getattr(capability, slot))
    object.__setattr__(forged, "_issuer_token", object())
    assert not subject._capability_valid(forged, firewall, request)


def test_firewall_and_decision_projections_expose_no_capability_object():
    *_, firewall, _, decision = _authorized()
    firewall_plain = subject.effect_firewall_to_plain_dict_v01(firewall)
    decision_plain = subject.effect_firewall_decision_to_plain_dict_v01(decision)
    assert "capability_id" not in json.dumps(firewall_plain)
    assert decision_plain["capability_id"] == decision.capability_id
    assert "EffectCapabilityV01" not in json.dumps(decision_plain)


def test_execution_positive_receipt_and_state_geometry():
    *_, firewall, request, decision, receipt = _executed()
    assert type(receipt) is KernelArtifactV01
    assert subject.validate_effect_receipt_v01(
        firewall=firewall, request=request, decision=decision, receipt=receipt
    ) == ()
    counters = subject.effect_firewall_to_plain_dict_v01(firewall)["state_counters"]
    assert counters["consumed_capability_count"] == 1
    assert counters["terminal_receipt_count"] == 1
    assert counters["mock_effect_execution_count"] == 1
    assert counters["real_world_effects_count"] == 0


@pytest.mark.parametrize(
    ("field", "expected"),
    (
        ("abi_version", "v1.0"),
        ("artifact_id", "receipt:fixture:effect_firewall:001"),
        ("artifact_type", "EvidenceReceipt"),
        ("schema_version", "v1"),
        ("source_component", "effect_firewall"),
        ("authority_class", "EVIDENCE_ONLY"),
        ("lifecycle_state", "RECEIPT_RECORDED"),
    ),
)
def test_receipt_exact_envelope_field(field, expected):
    plain = kernel_artifact_to_plain_dict_v01(_executed()[-1])
    assert plain[field] == expected


@pytest.mark.parametrize(
    ("field", "expected"),
    (
        ("mock_execution_status", "PASS"),
        ("receipt_evidence_only", True),
        ("root_confirmation_required", True),
        ("root_confirmation_created", False),
        ("future_permission_created", False),
        ("root_decision_created", False),
        ("final_output_created", False),
        ("effect_handle_exposed", False),
        ("real_world_effects_count", 0),
    ),
)
def test_receipt_exact_authority_payload_field(field, expected):
    payload = kernel_artifact_to_plain_dict_v01(_executed()[-1])["payload"]
    assert payload[field] == expected


def _execute_with(**changes):
    *_, firewall, request, decision = _authorized()
    values = {
        "firewall": firewall,
        "request": request,
        "decision": decision,
        "current_tick": 120,
        "adapter_id": request.adapter_id,
        "action_kind": request.action_kind,
        "child_scope_refs": ("scope:neutral:alpha",),
        "child_expires_at_tick": 140,
        "receipt_artifact_id": "receipt:fixture:effect_firewall:001",
        "time_envelope": TIME_ENVELOPE,
    }
    values.update(changes)
    return firewall, request, decision, values


@pytest.mark.parametrize(
    ("changes", "reason"),
    (
        ({"current_tick": True}, "effect_execution_invalid"),
        ({"current_tick": -1}, "effect_execution_invalid"),
        ({"current_tick": 99}, "effect_request_not_yet_valid"),
        ({"current_tick": 150}, "effect_request_expired"),
        ({"adapter_id": "mock_adapter:other"}, "effect_capability_adapter_mismatch"),
        ({"adapter_id": 1}, "effect_capability_adapter_mismatch"),
        ({"action_kind": "mock_action:other"}, "effect_capability_action_mismatch"),
        ({"action_kind": 1}, "effect_capability_action_mismatch"),
        ({"child_scope_refs": []}, "effect_scope_expansion_forbidden"),
        ({"child_scope_refs": ()}, "effect_scope_expansion_forbidden"),
        ({"child_scope_refs": ("scope:other",)}, "effect_scope_expansion_forbidden"),
        ({"child_scope_refs": ("scope:neutral:alpha", "scope:other")}, "effect_scope_expansion_forbidden"),
        ({"child_expires_at_tick": True}, "effect_ttl_expansion_forbidden"),
        ({"child_expires_at_tick": 120}, "effect_ttl_expansion_forbidden"),
        ({"child_expires_at_tick": 151}, "effect_ttl_expansion_forbidden"),
        ({"receipt_artifact_id": ""}, "effect_receipt_invalid"),
        ({"receipt_artifact_id": "\ud800"}, "effect_receipt_invalid"),
        ({"time_envelope": {}}, "effect_receipt_invalid"),
    ),
)
def test_execution_rejection_is_atomic(changes, reason):
    firewall, _, _, values = _execute_with(**changes)
    before = subject.effect_firewall_to_plain_dict_v01(firewall)["state_counters"].copy()
    with pytest.raises(ValueError, match=f"^{reason}$"):
        subject.execute_mock_effect_v01(**values)
    assert subject.effect_firewall_to_plain_dict_v01(firewall)["state_counters"] == before


@pytest.mark.parametrize(
    ("tick", "child_expiry", "passes"),
    (
        (100, 101, True),
        (100, 150, True),
        (149, 150, True),
        (99, 100, False),
        (150, 151, False),
        (120, 121, True),
        (120, 149, True),
        (120, 150, True),
        (120, 151, False),
    ),
)
def test_execution_logical_tick_matrix(tick, child_expiry, passes):
    firewall, _, _, values = _execute_with(current_tick=tick, child_expires_at_tick=child_expiry)
    if passes:
        assert subject.execute_mock_effect_v01(**values)
    else:
        with pytest.raises(ValueError):
            subject.execute_mock_effect_v01(**values)
        assert subject.effect_firewall_to_plain_dict_v01(firewall)["state_counters"]["mock_effect_execution_count"] == 0


def test_duplicate_authorization_execution_and_receipt_are_strict():
    *_, firewall, request, decision, _ = _executed()
    duplicate = subject.authorize_effect_request_v01(
        firewall=firewall, request=request, current_tick=110
    )
    assert duplicate.reason_code == "duplicate_request"
    with pytest.raises(ValueError, match="^effect_capability_consumed$"):
        subject.execute_mock_effect_v01(
            firewall=firewall,
            request=request,
            decision=decision,
            current_tick=120,
            adapter_id=request.adapter_id,
            action_kind=request.action_kind,
            child_scope_refs=("scope:neutral:alpha",),
            child_expires_at_tick=140,
            receipt_artifact_id="receipt:fixture:effect_firewall:001",
            time_envelope=TIME_ENVELOPE,
        )


def test_reused_idempotency_key_is_blocked():
    *_, firewall, request = _request()
    first = subject.authorize_effect_request_v01(firewall=firewall, request=request, current_tick=110)
    second_request = _rehash_request(request, request_kind="ExecutionRequest")
    second = subject.authorize_effect_request_v01(firewall=firewall, request=second_request, current_tick=110)
    assert first.decision == "ALLOW_MOCK_EFFECT"
    assert second.reason_code == "duplicate_idempotency_key"


def test_duplicate_receipt_id_with_fresh_capability_is_blocked():
    *_, firewall, request, decision, _ = _executed()
    second_request = _rehash_request(
        request,
        request_kind="ExecutionRequest",
        idempotency_key="idempotency:second",
    )
    second_decision = subject.authorize_effect_request_v01(
        firewall=firewall, request=second_request, current_tick=110
    )
    with pytest.raises(ValueError, match="^effect_receipt_duplicate$"):
        subject.execute_mock_effect_v01(
            firewall=firewall,
            request=second_request,
            decision=second_decision,
            current_tick=120,
            adapter_id=second_request.adapter_id,
            action_kind=second_request.action_kind,
            child_scope_refs=("scope:neutral:alpha",),
            child_expires_at_tick=140,
            receipt_artifact_id="receipt:fixture:effect_firewall:001",
            time_envelope=TIME_ENVELOPE,
        )
    counters = subject.effect_firewall_to_plain_dict_v01(firewall)["state_counters"]
    assert counters["consumed_capability_count"] == 1
    assert counters["mock_effect_execution_count"] == 1


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    (
        ("future_permission_created", True, "effect_receipt_permission_creation_forbidden"),
        ("root_decision_created", True, "effect_receipt_root_decision_creation_forbidden"),
        ("final_output_created", True, "effect_receipt_final_output_creation_forbidden"),
        ("effect_handle_exposed", True, "effect_receipt_effect_handle_exposure_forbidden"),
        ("real_world_effects_count", 1, "effect_receipt_real_effect_forbidden"),
        ("receipt_evidence_only", False, "effect_receipt_authority_violation"),
        ("root_confirmation_created", True, "effect_receipt_binding_mismatch"),
        ("root_confirmation_required", False, "effect_receipt_binding_mismatch"),
        ("request_id", "request:other", "effect_receipt_binding_mismatch"),
        ("firewall_decision_id", "decision:other", "effect_receipt_binding_mismatch"),
        ("capability_id", "0" * 64, "effect_receipt_binding_mismatch"),
        ("root_decision_id", "decision:other", "effect_receipt_binding_mismatch"),
        ("selected_candidate_id", "candidate:other", "effect_receipt_binding_mismatch"),
        ("permission_ref", "permission:other", "effect_receipt_binding_mismatch"),
        ("adapter_id", "mock_adapter:other", "effect_receipt_binding_mismatch"),
        ("action_kind", "mock_action:other", "effect_receipt_binding_mismatch"),
        ("mock_execution_status", "FAIL", "effect_receipt_binding_mismatch"),
        ("scope_refs", ["scope:other"], "effect_receipt_scope_expansion_forbidden"),
        ("scope_refs", ["scope:neutral:alpha", "scope:neutral:alpha"], "effect_receipt_scope_expansion_forbidden"),
    ),
)
def test_receipt_payload_authority_mutation_rejected(field, value, reason):
    *_, firewall, request, decision, receipt = _executed()
    malformed = _rebuild_receipt(receipt, payload_changes={field: value})
    assert reason in subject.validate_effect_receipt_v01(
        firewall=firewall, request=request, decision=decision, receipt=malformed
    )


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    (
        ("artifact_id", "receipt:other", "effect_receipt_binding_mismatch"),
        ("artifact_type", "SemanticEvidence", "effect_receipt_binding_mismatch"),
        ("schema_version", "v2", "effect_receipt_binding_mismatch"),
        ("transaction_id", "txn:other", "effect_receipt_binding_mismatch"),
        ("owner_root_id", "root:other", "effect_receipt_binding_mismatch"),
        ("source_component", "other", "effect_receipt_binding_mismatch"),
        ("authority_class", "NON_AUTHORITY", "effect_receipt_authority_violation"),
        ("lifecycle_state", "VALIDATED", "effect_receipt_authority_violation"),
        ("trace_refs", ("trace:other",), "effect_receipt_binding_mismatch"),
        ("parent_refs", (), "effect_receipt_binding_mismatch"),
    ),
)
def test_receipt_envelope_mutation_rejected(field, value, reason):
    *_, firewall, request, decision, receipt = _executed()
    malformed = _rebuild_receipt(receipt, **{field: value})
    assert reason in subject.validate_effect_receipt_v01(
        firewall=firewall, request=request, decision=decision, receipt=malformed
    )


def test_receipt_payload_has_exact_nineteen_keys_and_no_capability_object():
    payload = kernel_artifact_to_plain_dict_v01(_executed()[-1])["payload"]
    assert tuple(sorted(payload)) == subject._RECEIPT_PAYLOAD_KEYS
    assert len(payload) == 19
    assert "EffectCapabilityV01" not in json.dumps(payload)


@pytest.mark.parametrize("projection", ("request", "decision", "firewall"))
def test_projections_are_json_safe_and_independent(projection):
    *_, firewall, request, decision = _authorized()
    function, value = {
        "request": (subject.effect_request_to_plain_dict_v01, request),
        "decision": (subject.effect_firewall_decision_to_plain_dict_v01, decision),
        "firewall": (subject.effect_firewall_to_plain_dict_v01, firewall),
    }[projection]
    first = function(value)
    second = function(value)
    assert first == second
    assert json.loads(json.dumps(first, allow_nan=False)) == first
    first[sorted(first)[0]] = "changed"
    assert function(value) == second


@pytest.mark.parametrize("instance_name", ("firewall", "capability"))
@pytest.mark.parametrize("operation", ("copy", "deepcopy", "pickle"))
def test_firewall_and_capability_reject_transfer(instance_name, operation):
    *_, firewall, _, decision = _authorized()
    value = firewall if instance_name == "firewall" else firewall._state.issued_capabilities[decision.capability_id]
    with pytest.raises(TypeError):
        {"copy": copy.copy, "deepcopy": copy.deepcopy, "pickle": pickle.dumps}[operation](value)


@pytest.mark.parametrize(
    "value",
    (None, {}, [], (), object(), "request", 1, True),
)
def test_public_validators_fail_closed_on_wrong_top_level_type(value):
    assert subject.validate_effect_firewall_v01(value)
    assert subject.validate_effect_request_v01(value)


def test_base_exception_is_not_swallowed(monkeypatch):
    monkeypatch.setattr(subject, "_hash", lambda *args, **kwargs: (_ for _ in ()).throw(KeyboardInterrupt()))
    with pytest.raises(KeyboardInterrupt):
        subject.validate_effect_request_v01(_request()[-1])


@pytest.mark.parametrize("exception_type", (ValueError, RuntimeError, OSError))
def test_ordinary_hash_exception_is_sanitized(monkeypatch, exception_type):
    request = _request()[-1]
    monkeypatch.setattr(subject, "_hash", lambda *args, **kwargs: (_ for _ in ()).throw(exception_type("caller-secret")))
    errors = subject.validate_effect_request_v01(request)
    assert errors == ("effect_request_id_mismatch",)
    assert "caller-secret" not in repr(errors)


def test_source_import_boundary_is_exact():
    source = Path(subject.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = {
        node.module
        for node in tree.body
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    assert imported == {
        "__future__",
        "dataclasses",
        "hedgehog.kernel.abi_v01",
        "hedgehog.kernel.integrity_replay_v01",
        "hedgehog.kernel.root_decision_v01",
        "hedgehog.kernel.transition_registry_v01",
    }


@pytest.mark.parametrize(
    "forbidden",
    (
        "hedgehog.domains",
        "demo",
        "tests",
        "action_commit_packet_v02",
        "action_commit_packet",
        "action_permission",
        "mock_connector_sandbox",
        "fractal_fulfillment",
        "providers",
        "jsonschema",
        "cryptography",
        "import os",
        "pathlib",
        "tempfile",
        "shutil",
        "subprocess",
        "socket",
        "requests",
        "urllib",
        "import random",
        "import time",
        "datetime",
        "open(",
        "getenv",
        "environ",
        "__import__",
        "register_adapter",
        "register_provider",
        "register_domain",
        "execute_real",
    ),
)
def test_static_forbidden_dependency_or_hook_absent(forbidden):
    if forbidden in ('action_commit_packet_v02', 'action_commit_packet'):
        assert _native_deferred_action_errors(Path(subject.__file__).read_text(encoding='utf-8')) == ()
        return
    source = Path(subject.__file__).read_text(encoding="utf-8").lower()
    assert forbidden.lower() not in source


@pytest.mark.parametrize("domain_token", ("airline", "supplier", "water filter", "payment", "shipment", "booking", "ticket", "bank"))
def test_static_domain_token_absent(domain_token):
    source = Path(subject.__file__).read_text(encoding="utf-8").lower()
    assert domain_token not in source


def test_no_module_global_mutable_registry_or_state():
    for name, value in vars(subject).items():
        if name == "__builtins__":
            continue
        assert not (name.isupper() and type(value) in (list, dict, set))
        assert type(value) is not subject._InvocationState


def test_no_public_callback_or_capability_parameter():
    for name in PUBLIC_FUNCTIONS:
        parameters = inspect.signature(getattr(subject, name)).parameters
        assert "callback" not in parameters
        assert "capability" not in parameters


def test_public_projection_field_sets_are_exact():
    *_, firewall, request, decision = _authorized()
    assert tuple(subject.effect_request_to_plain_dict_v01(request)) == REQUEST_FIELDS
    assert tuple(subject.effect_firewall_decision_to_plain_dict_v01(decision)) == DECISION_FIELDS
    firewall_plain = subject.effect_firewall_to_plain_dict_v01(firewall)
    assert tuple(firewall_plain) == FIREWALL_PUBLIC_FIELDS + ("state_counters",)
    assert tuple(firewall_plain["state_counters"]) == (
        "seen_request_count",
        "used_idempotency_key_count",
        "issued_capability_count",
        "consumed_capability_count",
        "terminal_receipt_count",
        "mock_effect_execution_count",
        "real_world_effects_count",
    )


def test_complete_deterministic_mock_path_repeats_exactly():
    first = _executed()
    second = _executed()
    first_firewall, first_request, first_decision, first_receipt = first[-4:]
    second_firewall, second_request, second_decision, second_receipt = second[-4:]
    assert subject.effect_request_to_plain_dict_v01(first_request) == subject.effect_request_to_plain_dict_v01(second_request)
    assert subject.effect_firewall_decision_to_plain_dict_v01(first_decision) == subject.effect_firewall_decision_to_plain_dict_v01(second_decision)
    assert kernel_artifact_to_plain_dict_v01(first_receipt) == kernel_artifact_to_plain_dict_v01(second_receipt)
    assert subject.effect_firewall_to_plain_dict_v01(first_firewall) == subject.effect_firewall_to_plain_dict_v01(second_firewall)


def test_plain_object_issuer_token_has_no_builder_origin():
    firewall = _firewall()[-1]
    forged = replace(firewall, _issuer_token=object())
    assert "effect_firewall_state_invalid" in subject.validate_effect_firewall_v01(
        forged
    )


def test_direct_manual_firewall_without_builder_provenance_fails():
    source = _firewall()[-1]
    state = subject._InvocationState()
    plain_token = object()
    state.issuer_token = plain_token
    manual = subject.EffectFirewallV01(
        **{name: getattr(source, name) for name in FIREWALL_PUBLIC_FIELDS},
        _issuer_token=plain_token,
        _state=state,
    )
    assert "effect_firewall_state_invalid" in subject.validate_effect_firewall_v01(
        manual
    )


@pytest.mark.parametrize(
    ("field", "value"),
    (
        (
            "allowed_adapter_ids",
            ("mock_adapter:bounded_neutral_v01", "mock_adapter:expanded"),
        ),
        (
            "allowed_action_kinds",
            ("mock_action:record_neutral_receipt", "mock_action:expanded"),
        ),
        (
            "root_scope_refs",
            ("scope:neutral:alpha", "scope:neutral:beta", "scope:expanded"),
        ),
        ("maximum_expires_at_tick", 999),
    ),
)
def test_self_rehashed_policy_expansion_lacks_builder_origin(field, value):
    forged = _rehash_firewall(_firewall()[-1], **{field: value})
    assert "effect_firewall_state_invalid" in subject.validate_effect_firewall_v01(
        forged
    )


def test_self_rehashed_invocation_change_lacks_builder_origin():
    forged = _rehash_firewall(
        _firewall()[-1],
        invocation_id="invocation:fixture:effect_firewall:forged",
    )
    assert "effect_firewall_state_invalid" in subject.validate_effect_firewall_v01(
        forged
    )


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("transaction_id", "txn:forged"),
        ("target_root_id", "root:forged"),
        ("root_decision_id", "decision:forged"),
        ("selected_candidate_id", "candidate:forged"),
        ("permission_ref", "permission:forged"),
    ),
)
def test_self_rehashed_root_binding_change_lacks_builder_origin(field, value):
    forged = _rehash_firewall(_firewall()[-1], **{field: value})
    assert "effect_firewall_state_invalid" in subject.validate_effect_firewall_v01(
        forged
    )


def test_builder_origin_preserves_public_identity_and_private_uniqueness():
    first = _firewall()[-1]
    second = _firewall()[-1]
    assert subject.validate_effect_firewall_v01(first) == ()
    assert subject.validate_effect_firewall_v01(second) == ()
    assert first.firewall_id == second.firewall_id
    assert first._issuer_token is not second._issuer_token
    assert first.firewall_id == (
        "fcec934b116267baae8ea90b632f6dc441055e23ac05b92b25ecc2bd8e902bfb"
    )


def test_successful_authorization_records_exact_private_history():
    *_, firewall, request, decision = _authorized()
    assert firewall._state.idempotency_key_by_request_id == {
        request.request_id: request.idempotency_key
    }
    assert firewall._state.authorization_decision_id_by_capability_id == {
        decision.capability_id: decision.decision_id
    }


@pytest.mark.parametrize(
    "mutation",
    (
        "seen_without_capability",
        "idempotency_without_request",
        "receipt_without_consumption",
        "execution_count_without_consumption",
        "consumption_without_receipt",
    ),
)
def test_impossible_private_state_geometry_fails_closed(mutation):
    if mutation == "consumption_without_receipt":
        *_, firewall, _, decision = _authorized()
        firewall._state.consumed_capability_ids.add(decision.capability_id)
        firewall._state.mock_effect_execution_count = 1
    else:
        firewall = _firewall()[-1]
        if mutation == "seen_without_capability":
            firewall._state.seen_request_ids.add("0" * 64)
        elif mutation == "idempotency_without_request":
            firewall._state.used_idempotency_keys.add("idempotency:forged")
        elif mutation == "receipt_without_consumption":
            firewall._state.terminal_receipt_ids.add("receipt:forged")
        elif mutation == "execution_count_without_consumption":
            firewall._state.mock_effect_execution_count = 999
    assert subject.validate_effect_firewall_v01(firewall) == (
        "effect_firewall_state_invalid",
    )


def test_wrong_stored_authorization_decision_id_breaks_allowed_history():
    *_, firewall, request, decision = _authorized()
    firewall._state.authorization_decision_id_by_capability_id[
        decision.capability_id
    ] = "0" * 64
    assert "effect_firewall_capability_state_mismatch" in (
        subject.validate_effect_firewall_decision_v01(
            firewall=firewall,
            request=request,
            decision=decision,
        )
    )


def test_public_projection_rejects_impossible_counter_geometry():
    firewall = _firewall()[-1]
    firewall._state.mock_effect_execution_count = 999
    with pytest.raises(ValueError, match="^effect_firewall_invalid$"):
        subject.effect_firewall_to_plain_dict_v01(firewall)


@pytest.mark.parametrize("tick", (99, 150, 151, 999))
def test_rehashed_allowed_decision_tick_not_in_authorization_history_fails(tick):
    *_, firewall, request, decision = _authorized()
    forged = _rehash_decision(decision, evaluated_at_tick=tick)
    assert "effect_firewall_capability_state_mismatch" in (
        subject.validate_effect_firewall_decision_v01(
            firewall=firewall,
            request=request,
            decision=forged,
        )
    )


def test_original_allowed_decision_history_survives_execution():
    *_, firewall, request, decision = _authorized()
    assert subject.validate_effect_firewall_decision_v01(
        firewall=firewall,
        request=request,
        decision=decision,
    ) == ()
    _execute_authorized(firewall, request, decision, "receipt:history:001")
    assert subject.validate_effect_firewall_decision_v01(
        firewall=firewall,
        request=request,
        decision=decision,
    ) == ()


def test_pre_execution_receipt_requires_committed_execution_state():
    *_, firewall, request, decision = _authorized()
    receipt = _pre_execution_receipt(request, decision)
    before = _private_state_snapshot(firewall)
    assert "effect_receipt_execution_state_mismatch" in (
        subject.validate_effect_receipt_v01(
            firewall=firewall,
            request=request,
            decision=decision,
            receipt=receipt,
        )
    )
    assert _private_state_snapshot(firewall) == before


def test_executed_receipt_has_exact_committed_capability_binding():
    *_, firewall, request, decision, receipt = _executed()
    assert subject.validate_effect_receipt_v01(
        firewall=firewall,
        request=request,
        decision=decision,
        receipt=receipt,
    ) == ()
    assert firewall._state.terminal_receipt_id_by_capability_id == {
        decision.capability_id: receipt.artifact_id
    }


def test_two_capabilities_retain_distinct_terminal_receipt_bindings():
    *_, firewall, first_request = _request()
    first_decision = subject.authorize_effect_request_v01(
        firewall=firewall,
        request=first_request,
        current_tick=110,
    )
    first_receipt = _execute_authorized(
        firewall,
        first_request,
        first_decision,
        "receipt:binding:first",
    )
    second_request = _rehash_request(
        first_request,
        request_kind="ExecutionRequest",
        idempotency_key="idempotency:binding:second",
    )
    second_decision = subject.authorize_effect_request_v01(
        firewall=firewall,
        request=second_request,
        current_tick=110,
    )
    second_receipt = _execute_authorized(
        firewall,
        second_request,
        second_decision,
        "receipt:binding:second",
    )
    assert firewall._state.terminal_receipt_id_by_capability_id == {
        first_decision.capability_id: first_receipt.artifact_id,
        second_decision.capability_id: second_receipt.artifact_id,
    }
    assert subject.validate_effect_receipt_v01(
        firewall=firewall,
        request=first_request,
        decision=first_decision,
        receipt=first_receipt,
    ) == ()
    assert subject.validate_effect_receipt_v01(
        firewall=firewall,
        request=second_request,
        decision=second_decision,
        receipt=second_receipt,
    ) == ()
    assert "effect_receipt_execution_state_mismatch" in (
        subject.validate_effect_receipt_v01(
            firewall=firewall,
            request=second_request,
            decision=second_decision,
            receipt=first_receipt,
        )
    )


def test_failed_execution_preserves_every_private_state_ledger():
    *_, firewall, request, decision = _authorized()
    before = _private_state_snapshot(firewall)
    with pytest.raises(ValueError, match="^effect_scope_expansion_forbidden$"):
        subject.execute_mock_effect_v01(
            firewall=firewall,
            request=request,
            decision=decision,
            current_tick=120,
            adapter_id=request.adapter_id,
            action_kind=request.action_kind,
            child_scope_refs=("scope:expanded",),
            child_expires_at_tick=140,
            receipt_artifact_id="receipt:failed:atomicity",
            time_envelope=TIME_ENVELOPE,
        )
    assert _private_state_snapshot(firewall) == before


def test_canonical_request_decision_and_capability_ids_remain_frozen():
    *_, firewall, request, decision = _authorized()
    assert firewall.firewall_id == (
        "fcec934b116267baae8ea90b632f6dc441055e23ac05b92b25ecc2bd8e902bfb"
    )
    assert request.request_id == (
        "78f442d3adca66c7f6f9752ee7768e61ae95a9a2cf33d1badddeb082702ae1c3"
    )
    assert decision.decision_id == (
        "9ff5601e038da7f20f13de24a5c92946aae1ff14d76eb38b95f14fbc2ea1d9de"
    )
    assert decision.capability_id == (
        "77f3943c8a9a9c99852603400c0895201f156bd1f7ff65de2d6cec5a58da847a"
    )


def _historical_projection_kwargs(**changes):
    _, kernel, decision_input, result = _root_context()
    values = {
        "root_decision_kernel": kernel,
        "decision_input": decision_input,
        "root_decision_result": result,
        "invocation_id": "invocation:fixture:effect_firewall:001",
        "allowed_adapter_ids": ("mock_adapter:bounded_neutral_v01",),
        "allowed_action_kinds": ("mock_action:record_neutral_receipt",),
        "root_scope_refs": ("scope:neutral:alpha", "scope:neutral:beta"),
        "maximum_expires_at_tick": 200,
        "request_kind": "ActionCommitPacket",
        "adapter_id": "mock_adapter:bounded_neutral_v01",
        "action_kind": "mock_action:record_neutral_receipt",
        "scope_refs": ("scope:neutral:alpha",),
        "issued_at_tick": 100,
        "expires_at_tick": 150,
        "idempotency_key": "idempotency:fixture:effect_firewall:001",
        "current_tick": 110,
    }
    values.update(changes)
    return values


def _historical_static_reason_case(reason):
    kernel, decision_input, result, firewall, request = _request()
    tick = 110
    if reason == "forged_request":
        request = replace(request, request_id="0" * 64)
    elif reason == "request_root_binding_mismatch":
        request = _rehash_request(request, root_decision_id="decision:other")
    elif reason == "permission_binding_mismatch":
        request = _rehash_request(request, permission_ref="permission:other")
    elif reason == "real_effect_forbidden":
        request = _rehash_request(request, mock_only=False)
    elif reason == "adapter_not_allowed":
        request = _rehash_request(request, adapter_id="mock_adapter:other")
    elif reason == "action_not_allowed":
        request = _rehash_request(request, action_kind="mock_action:other")
    elif reason == "scope_expansion_forbidden":
        request = _rehash_request(request, scope_refs=("scope:other",))
    elif reason == "ttl_expansion_forbidden":
        request = _rehash_request(request, expires_at_tick=201)
    elif reason == "request_not_yet_valid":
        tick = 99
    elif reason == "request_expired":
        tick = 150
    projection = subject._project_effect_firewall_historical_request_v01(
        root_decision_kernel=kernel,
        decision_input=decision_input,
        root_decision_result=result,
        invocation_id=firewall.invocation_id,
        allowed_adapter_ids=firewall.allowed_adapter_ids,
        allowed_action_kinds=firewall.allowed_action_kinds,
        root_scope_refs=firewall.root_scope_refs,
        maximum_expires_at_tick=firewall.maximum_expires_at_tick,
        request=request,
        current_tick=tick,
    )
    runtime = subject.authorize_effect_request_v01(
        firewall=firewall,
        request=request,
        current_tick=tick,
    )
    return projection, runtime


def test_effect_firewall_historical_projection_matches_runtime_allow_without_state():
    values = _historical_projection_kwargs()
    historical = (
        subject.project_effect_firewall_historical_authorization_v01(
            **values
        )
    )
    runtime_firewall = subject.build_effect_firewall_v01(
        root_decision_kernel=values["root_decision_kernel"],
        decision_input=values["decision_input"],
        root_decision_result=values["root_decision_result"],
        invocation_id=values["invocation_id"],
        allowed_adapter_ids=values["allowed_adapter_ids"],
        allowed_action_kinds=values["allowed_action_kinds"],
        root_scope_refs=values["root_scope_refs"],
        maximum_expires_at_tick=values["maximum_expires_at_tick"],
    )
    runtime_request = subject.build_effect_request_v01(
        root_decision_kernel=values["root_decision_kernel"],
        decision_input=values["decision_input"],
        root_decision_result=values["root_decision_result"],
        request_kind=values["request_kind"],
        adapter_id=values["adapter_id"],
        action_kind=values["action_kind"],
        scope_refs=values["scope_refs"],
        issued_at_tick=values["issued_at_tick"],
        expires_at_tick=values["expires_at_tick"],
        idempotency_key=values["idempotency_key"],
    )
    runtime_decision = subject.authorize_effect_request_v01(
        firewall=runtime_firewall,
        request=runtime_request,
        current_tick=values["current_tick"],
    )
    assert tuple(
        field.name
        for field in fields(
            subject.EffectFirewallHistoricalAuthorizationProjectionV01
        )
    ) == HISTORICAL_AUTHORIZATION_FIELDS
    assert historical.firewall_id == runtime_firewall.firewall_id
    assert historical.request == runtime_request
    assert historical.decision == runtime_decision
    assert historical.expected_capability_id == runtime_decision.capability_id
    assert historical.fresh_empty_invocation_state is True
    assert historical.firewall_object_created is False
    assert historical.capability_object_created is False
    assert historical.real_world_effects_count == 0
    assert subject.validate_effect_firewall_historical_authorization_projection_v01(
        historical,
        **values,
    ) == ()
    with pytest.raises(FrozenInstanceError):
        historical.firewall_object_created = True


def test_effect_firewall_historical_projection_matches_static_block_reasons():
    reasons = (
        "forged_request",
        "request_root_binding_mismatch",
        "permission_binding_mismatch",
        "real_effect_forbidden",
        "adapter_not_allowed",
        "action_not_allowed",
        "scope_expansion_forbidden",
        "ttl_expansion_forbidden",
        "request_not_yet_valid",
        "request_expired",
    )
    for reason in reasons:
        historical, runtime = _historical_static_reason_case(reason)
        assert historical.decision == runtime
        assert historical.decision.reason_code == reason
        assert historical.expected_capability_id is None
        assert historical.decision.capability_issued is False
        assert historical.decision.return_to_root is True
        assert historical.real_world_effects_count == 0
    assert "duplicate_request" not in reasons
    assert "duplicate_idempotency_key" not in reasons


def test_effect_firewall_historical_projection_rejects_drift_and_is_total():
    values = _historical_projection_kwargs()
    projection = (
        subject.project_effect_firewall_historical_authorization_v01(
            **values
        )
    )
    replacements = {
        "profile_id": "wrong_profile",
        "firewall_id": "0" * 64,
        "request": replace(projection.request, request_id="0" * 64),
        "decision": replace(projection.decision, decision_id="0" * 64),
        "expected_capability_id": "0" * 64,
        "fresh_empty_invocation_state": False,
        "firewall_object_created": True,
        "capability_object_created": True,
        "real_world_effects_count": 1,
    }
    for field_name, replacement in replacements.items():
        drifted = replace(projection, **{field_name: replacement})
        assert subject.validate_effect_firewall_historical_authorization_projection_v01(
            drifted,
            **values,
        )
    for malformed in (None, True, 1, {}, [], (), object()):
        assert subject.validate_effect_firewall_historical_authorization_projection_v01(
            malformed,
            **values,
        ) == ("effect_firewall_historical_projection_invalid",)
    with pytest.raises(
        ValueError,
        match="^effect_firewall_historical_projection_invalid$",
    ):
        subject.project_effect_firewall_historical_authorization_v01(
            **_historical_projection_kwargs(current_tick=True)
        )

    class EqualProjection:
        def __eq__(self, other):
            return True

    assert subject.validate_effect_firewall_historical_authorization_projection_v01(
        EqualProjection(),
        **values,
    ) == ("effect_firewall_historical_projection_invalid",)


def test_effect_firewall_historical_projection_has_zero_runtime_state(
    monkeypatch,
):
    calls = {
        "firewall": 0,
        "authorize": 0,
        "execute": 0,
        "capability": 0,
    }


    def counter(name, original):
        @wraps(original)
        def wrapped(*args, **kwargs):
            calls[name] += 1
            return original(*args, **kwargs)

        return wrapped

    monkeypatch.setattr(
        subject,
        "build_effect_firewall_v01",
        counter("firewall", subject.build_effect_firewall_v01),
    )
    monkeypatch.setattr(
        subject,
        "authorize_effect_request_v01",
        counter("authorize", subject.authorize_effect_request_v01),
    )
    monkeypatch.setattr(
        subject,
        "execute_mock_effect_v01",
        counter("execute", subject.execute_mock_effect_v01),
    )
    monkeypatch.setattr(
        subject,
        "_issue_capability",
        counter("capability", subject._issue_capability),
    )
    values = _historical_projection_kwargs()
    projection = (
        subject.project_effect_firewall_historical_authorization_v01(
            **values
        )
    )
    assert subject.validate_effect_firewall_historical_authorization_projection_v01(
        projection,
        **values,
    ) == ()
    assert calls == {
        "firewall": 0,
        "authorize": 0,
        "execute": 0,
        "capability": 0,
    }
