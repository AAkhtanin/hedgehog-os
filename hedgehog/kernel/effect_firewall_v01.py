"""Pure in-memory deterministic domain-neutral exclusive effect boundary.

This G1-C2 Firewall is mock-only and uses logical ticks, no clock or
randomness. It performs no filesystem, network, provider, LLM, Gemini, domain,
real-connector, or production-authorization operation. The opaque,
non-serializable capability remains internal to one Firewall invocation; no
public function returns it. Scope and TTL cannot expand after Root. The
evidence-only receipt creates no permission, Root decision, FinalOutput, or
effect handle, and real-world effects remain zero. This is not production
security certification.
"""

from __future__ import annotations

from dataclasses import dataclass as _dataclass
from dataclasses import field as _field

from hedgehog.kernel.abi_v01 import (
    KernelArtifactV01,
    build_kernel_artifact_v01 as _build_kernel_artifact_v01,
    kernel_artifact_to_plain_dict_v01 as _kernel_artifact_to_plain_dict_v01,
    validate_kernel_artifact_v01 as _validate_kernel_artifact_v01,
)
from hedgehog.kernel.integrity_replay_v01 import (
    canonical_json_bytes_v01 as _canonical_json_bytes_v01,
    domain_separated_sha256_hex_v01 as _domain_separated_sha256_hex_v01,
)
from hedgehog.kernel.root_decision_v01 import (
    ROOT_DECISION_ACCEPT as _ROOT_DECISION_ACCEPT,
    RootDecisionInputV01,
    RootDecisionKernelV01,
    RootDecisionResultV01,
    root_decision_input_to_plain_dict_v01 as _root_decision_input_to_plain_dict_v01,
    root_decision_result_to_plain_dict_v01 as _root_decision_result_to_plain_dict_v01,
    validate_root_decision_result_v01 as _validate_root_decision_result_v01,
)
from hedgehog.kernel.transition_registry_v01 import (
    DECISION_RETURN_TO_ROOT as _DECISION_RETURN_TO_ROOT,
    build_default_transition_registry_v01 as _build_default_transition_registry_v01,
    lookup_transition_v01 as _lookup_transition_v01,
)


MODULE_ID = "kernel_effect_firewall_v01"
SLICE_ID = "domain_neutral_reference_kernel_gate1_g1c2"
EFFECT_FIREWALL_VERSION = "v0.1"

STATUS_PASS = "PASS"
STATUS_BLOCKED_FAIL_CLOSED = "BLOCKED_FAIL_CLOSED"

EFFECT_DECISION_ALLOW_MOCK_EFFECT = "ALLOW_MOCK_EFFECT"
EFFECT_DECISION_BLOCKED_FAIL_CLOSED = "BLOCKED_FAIL_CLOSED"
EFFECT_FIREWALL_DECISIONS = (
    EFFECT_DECISION_ALLOW_MOCK_EFFECT,
    EFFECT_DECISION_BLOCKED_FAIL_CLOSED,
)
EFFECT_REQUEST_KINDS = ("ExecutionRequest", "ActionCommitPacket")
EFFECT_ACCESS_OWNER = "EFFECT_FIREWALL_ONLY"
MOCK_ADAPTER_PREFIX = "mock_adapter:"
MOCK_ACTION_PREFIX = "mock_action:"
RECEIPT_SOURCE_COMPONENT = "effect_firewall"
NoExpansionAfterRoot = True

_FIREWALL_DOMAIN = "hedgehog.kernel.effect_firewall.v01"
_REQUEST_DOMAIN = "hedgehog.kernel.effect_request.v01"
_CAPABILITY_DOMAIN = "hedgehog.kernel.effect_capability.v01"
_DECISION_DOMAIN = "hedgehog.kernel.effect_firewall_decision.v01"
_BLOCK_REASONS = (
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
    "duplicate_request",
    "duplicate_idempotency_key",
)
_EXECUTION_REASONS = (
    "effect_execution_invalid",
    "effect_capability_missing",
    "effect_capability_forged",
    "effect_capability_consumed",
    "effect_capability_adapter_mismatch",
    "effect_capability_action_mismatch",
    "effect_scope_expansion_forbidden",
    "effect_ttl_expansion_forbidden",
    "effect_request_not_yet_valid",
    "effect_request_expired",
    "effect_receipt_duplicate",
    "effect_receipt_invalid",
)
_RECEIPT_PAYLOAD_KEYS = (
    "action_kind",
    "adapter_id",
    "capability_id",
    "effect_handle_exposed",
    "final_output_created",
    "firewall_decision_id",
    "future_permission_created",
    "mock_execution_status",
    "permission_ref",
    "real_world_effects_count",
    "receipt_evidence_only",
    "receipt_ref",
    "request_id",
    "root_confirmation_created",
    "root_confirmation_required",
    "root_decision_created",
    "root_decision_id",
    "scope_refs",
    "selected_candidate_id",
)


_FIREWALL_ORIGIN_MARKER = object()


class _FirewallIssuerToken:
    __slots__ = ("_origin_marker", "_firewall_id", "_state")

    def __new__(cls, *args: object, **kwargs: object) -> _FirewallIssuerToken:
        raise TypeError("Firewall issuer tokens have no public constructor")

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError("Firewall issuer tokens are immutable")

    def __repr__(self) -> str:
        return "_FirewallIssuerToken(<opaque>)"


class _InvocationState:
    __slots__ = (
        "issuer_token",
        "seen_request_ids",
        "used_idempotency_keys",
        "issued_capabilities",
        "idempotency_key_by_request_id",
        "authorization_decision_id_by_capability_id",
        "consumed_capability_ids",
        "terminal_receipt_ids",
        "terminal_receipt_id_by_capability_id",
        "mock_effect_execution_count",
    )

    def __init__(self) -> None:
        self.issuer_token: _FirewallIssuerToken | None = None
        self.seen_request_ids: set[str] = set()
        self.used_idempotency_keys: set[str] = set()
        self.issued_capabilities: dict[str, EffectCapabilityV01] = {}
        self.idempotency_key_by_request_id: dict[str, str] = {}
        self.authorization_decision_id_by_capability_id: dict[str, str] = {}
        self.consumed_capability_ids: set[str] = set()
        self.terminal_receipt_ids: set[str] = set()
        self.terminal_receipt_id_by_capability_id: dict[str, str] = {}
        self.mock_effect_execution_count = 0


def _new_firewall_issuer_token(
    *,
    firewall_id: str,
    state: _InvocationState,
) -> _FirewallIssuerToken:
    token = object.__new__(_FirewallIssuerToken)
    object.__setattr__(token, "_origin_marker", _FIREWALL_ORIGIN_MARKER)
    object.__setattr__(token, "_firewall_id", firewall_id)
    object.__setattr__(token, "_state", state)
    state.issuer_token = token
    return token


class EffectCapabilityV01:
    __slots__ = (
        "_capability_id",
        "_firewall_id",
        "_invocation_id",
        "_request_id",
        "_transaction_id",
        "_target_root_id",
        "_root_decision_id",
        "_selected_candidate_id",
        "_permission_ref",
        "_adapter_id",
        "_action_kind",
        "_scope_refs",
        "_expires_at_tick",
        "_issuer_token",
        "_state",
    )

    def __new__(cls, *args: object, **kwargs: object) -> EffectCapabilityV01:
        raise TypeError("EffectCapabilityV01 has no public constructor")

    @property
    def capability_id(self) -> str:
        return self._capability_id

    @property
    def firewall_id(self) -> str:
        return self._firewall_id

    @property
    def invocation_id(self) -> str:
        return self._invocation_id

    @property
    def request_id(self) -> str:
        return self._request_id

    @property
    def transaction_id(self) -> str:
        return self._transaction_id

    @property
    def target_root_id(self) -> str:
        return self._target_root_id

    @property
    def root_decision_id(self) -> str:
        return self._root_decision_id

    @property
    def selected_candidate_id(self) -> str:
        return self._selected_candidate_id

    @property
    def permission_ref(self) -> str:
        return self._permission_ref

    @property
    def adapter_id(self) -> str:
        return self._adapter_id

    @property
    def action_kind(self) -> str:
        return self._action_kind

    @property
    def scope_refs(self) -> tuple[str, ...]:
        return self._scope_refs

    @property
    def expires_at_tick(self) -> int:
        return self._expires_at_tick

    def __setattr__(self, name: str, value: object) -> None:
        raise AttributeError("EffectCapabilityV01 is immutable")

    def __repr__(self) -> str:
        return "EffectCapabilityV01(<opaque>)"

    def __copy__(self) -> EffectCapabilityV01:
        raise TypeError("EffectCapabilityV01 cannot be copied")

    def __deepcopy__(self, memo: object) -> EffectCapabilityV01:
        raise TypeError("EffectCapabilityV01 cannot be copied")

    def __reduce__(self) -> object:
        raise TypeError("EffectCapabilityV01 cannot be serialized")

    def __reduce_ex__(self, protocol: int) -> object:
        raise TypeError("EffectCapabilityV01 cannot be serialized")


@_dataclass(frozen=True, slots=True)
class EffectRequestV01:
    request_id: str
    request_kind: str
    transaction_id: str
    target_root_id: str
    root_decision_id: str
    selected_candidate_id: str
    permission_ref: str
    adapter_id: str
    action_kind: str
    scope_refs: tuple[str, ...]
    issued_at_tick: int
    expires_at_tick: int
    idempotency_key: str
    mock_only: bool


@_dataclass(frozen=True, slots=True)
class EffectFirewallDecisionV01:
    decision_id: str
    firewall_id: str
    invocation_id: str
    request_id: str
    transaction_id: str
    target_root_id: str
    root_decision_id: str
    adapter_id: str
    action_kind: str
    evaluated_at_tick: int
    decision: str
    reason_code: str
    capability_id: str | None
    capability_issued: bool
    return_to_root: bool
    real_world_effects_count: int


@_dataclass(frozen=True, slots=True)
class EffectFirewallV01:
    firewall_id: str
    firewall_version: str
    invocation_id: str
    transaction_id: str
    target_root_id: str
    root_decision_id: str
    selected_candidate_id: str
    permission_ref: str
    allowed_adapter_ids: tuple[str, ...]
    allowed_action_kinds: tuple[str, ...]
    root_scope_refs: tuple[str, ...]
    maximum_expires_at_tick: int
    mock_only: bool
    effect_access_owner: str
    _issuer_token: object = _field(repr=False, compare=False, hash=False)
    _state: _InvocationState = _field(repr=False, compare=False, hash=False)

    def __copy__(self) -> EffectFirewallV01:
        raise TypeError("EffectFirewallV01 cannot be copied")

    def __deepcopy__(self, memo: object) -> EffectFirewallV01:
        raise TypeError("EffectFirewallV01 cannot be copied")

    def __reduce__(self) -> object:
        raise TypeError("EffectFirewallV01 cannot be serialized")

    def __reduce_ex__(self, protocol: int) -> object:
        raise TypeError("EffectFirewallV01 cannot be serialized")


def build_effect_firewall_v01(
    *,
    root_decision_kernel: RootDecisionKernelV01,
    decision_input: RootDecisionInputV01,
    root_decision_result: RootDecisionResultV01,
    invocation_id: str,
    allowed_adapter_ids: tuple[str, ...],
    allowed_action_kinds: tuple[str, ...],
    root_scope_refs: tuple[str, ...],
    maximum_expires_at_tick: int,
) -> EffectFirewallV01:
    try:
        context = _validated_root_context(
            root_decision_kernel,
            decision_input,
            root_decision_result,
        )
        if not _valid_text(invocation_id):
            raise ValueError("effect_firewall_binding_invalid")
        if not _valid_text_tuple(allowed_adapter_ids, allow_empty=False) or any(
            not item.startswith(MOCK_ADAPTER_PREFIX) for item in allowed_adapter_ids
        ):
            raise ValueError("effect_firewall_adapter_policy_invalid")
        if not _valid_text_tuple(allowed_action_kinds, allow_empty=False) or any(
            not item.startswith(MOCK_ACTION_PREFIX) for item in allowed_action_kinds
        ):
            raise ValueError("effect_firewall_action_policy_invalid")
        if not _valid_text_tuple(root_scope_refs, allow_empty=False):
            raise ValueError("effect_firewall_scope_invalid")
        if type(maximum_expires_at_tick) is not int or maximum_expires_at_tick <= 0:
            raise ValueError("effect_firewall_time_invalid")
        values = {
            "firewall_version": EFFECT_FIREWALL_VERSION,
            "invocation_id": invocation_id,
            "transaction_id": context["transaction_id"],
            "target_root_id": context["target_root_id"],
            "root_decision_id": context["root_decision_id"],
            "selected_candidate_id": context["selected_candidate_id"],
            "permission_ref": context["permission_ref"],
            "allowed_adapter_ids": list(allowed_adapter_ids),
            "allowed_action_kinds": list(allowed_action_kinds),
            "root_scope_refs": list(root_scope_refs),
            "maximum_expires_at_tick": maximum_expires_at_tick,
            "mock_only": True,
            "effect_access_owner": EFFECT_ACCESS_OWNER,
        }
        firewall_id = _hash(_FIREWALL_DOMAIN, values)
        state = _InvocationState()
        issuer_token = _new_firewall_issuer_token(
            firewall_id=firewall_id,
            state=state,
        )
        firewall = EffectFirewallV01(
            firewall_id=firewall_id,
            firewall_version=EFFECT_FIREWALL_VERSION,
            invocation_id=invocation_id,
            transaction_id=context["transaction_id"],
            target_root_id=context["target_root_id"],
            root_decision_id=context["root_decision_id"],
            selected_candidate_id=context["selected_candidate_id"],
            permission_ref=context["permission_ref"],
            allowed_adapter_ids=allowed_adapter_ids,
            allowed_action_kinds=allowed_action_kinds,
            root_scope_refs=root_scope_refs,
            maximum_expires_at_tick=maximum_expires_at_tick,
            mock_only=True,
            effect_access_owner=EFFECT_ACCESS_OWNER,
            _issuer_token=issuer_token,
            _state=state,
        )
        errors = _firewall_errors(firewall)
        if errors:
            raise ValueError(errors[0])
        return firewall
    except ValueError as exc:
        reason = _allowed_reason(exc, _FIREWALL_REASONS)
        raise ValueError(reason or "effect_firewall_invalid") from None
    except Exception:
        raise ValueError("effect_firewall_invalid") from None


def validate_effect_firewall_v01(firewall: object) -> tuple[str, ...]:
    try:
        return _firewall_errors(firewall)
    except Exception:
        return ("effect_firewall_unexpected_exception",)


def build_effect_request_v01(
    *,
    root_decision_kernel: RootDecisionKernelV01,
    decision_input: RootDecisionInputV01,
    root_decision_result: RootDecisionResultV01,
    request_kind: str,
    adapter_id: str,
    action_kind: str,
    scope_refs: tuple[str, ...],
    issued_at_tick: int,
    expires_at_tick: int,
    idempotency_key: str,
) -> EffectRequestV01:
    try:
        context = _validated_root_context(
            root_decision_kernel,
            decision_input,
            root_decision_result,
        )
        provisional = EffectRequestV01(
            request_id="0" * 64,
            request_kind=request_kind,
            transaction_id=context["transaction_id"],
            target_root_id=context["target_root_id"],
            root_decision_id=context["root_decision_id"],
            selected_candidate_id=context["selected_candidate_id"],
            permission_ref=context["permission_ref"],
            adapter_id=adapter_id,
            action_kind=action_kind,
            scope_refs=scope_refs,
            issued_at_tick=issued_at_tick,
            expires_at_tick=expires_at_tick,
            idempotency_key=idempotency_key,
            mock_only=True,
        )
        errors = _request_errors(provisional, check_id=False)
        if errors:
            raise ValueError(errors[0])
        return EffectRequestV01(
            request_id=_request_id(provisional),
            request_kind=request_kind,
            transaction_id=provisional.transaction_id,
            target_root_id=provisional.target_root_id,
            root_decision_id=provisional.root_decision_id,
            selected_candidate_id=provisional.selected_candidate_id,
            permission_ref=provisional.permission_ref,
            adapter_id=adapter_id,
            action_kind=action_kind,
            scope_refs=scope_refs,
            issued_at_tick=issued_at_tick,
            expires_at_tick=expires_at_tick,
            idempotency_key=idempotency_key,
            mock_only=True,
        )
    except ValueError as exc:
        reason = _allowed_reason(exc, _REQUEST_REASONS)
        raise ValueError(reason or "effect_request_invalid") from None
    except Exception:
        raise ValueError("effect_request_invalid") from None


def validate_effect_request_v01(request: object) -> tuple[str, ...]:
    try:
        return _request_errors(request, check_id=True)
    except Exception:
        return ("effect_request_unexpected_exception",)


def authorize_effect_request_v01(
    *,
    firewall: object,
    request: object,
    current_tick: object,
) -> EffectFirewallDecisionV01:
    try:
        if _firewall_errors(firewall) or type(request) is not EffectRequestV01:
            raise ValueError("effect_authorization_invalid")
        if type(current_tick) is not int or current_tick < 0:
            raise ValueError("effect_authorization_invalid")
        assert type(firewall) is EffectFirewallV01
        if not _request_authorization_shape_valid(request):
            raise ValueError("effect_authorization_invalid")
        try:
            forged = request.request_id != _request_id(request)
        except Exception:
            forged = True
        if forged:
            return _blocked_decision(firewall, request, current_tick, "forged_request")
        reason = _authorization_block_reason(firewall, request, current_tick)
        if reason is not None:
            return _blocked_decision(firewall, request, current_tick, reason)
        capability = _issue_capability(firewall, request)
        decision = _allowed_decision(firewall, request, current_tick, capability)
        state = firewall._state
        new_seen = set(state.seen_request_ids)
        new_seen.add(request.request_id)
        new_keys = set(state.used_idempotency_keys)
        new_keys.add(request.idempotency_key)
        new_capabilities = dict(state.issued_capabilities)
        new_capabilities[capability.capability_id] = capability
        new_request_keys = dict(state.idempotency_key_by_request_id)
        new_request_keys[request.request_id] = request.idempotency_key
        new_authorizations = dict(
            state.authorization_decision_id_by_capability_id
        )
        new_authorizations[capability.capability_id] = decision.decision_id
        state.seen_request_ids = new_seen
        state.used_idempotency_keys = new_keys
        state.issued_capabilities = new_capabilities
        state.idempotency_key_by_request_id = new_request_keys
        state.authorization_decision_id_by_capability_id = new_authorizations
        return decision
    except ValueError as exc:
        if _allowed_reason(exc, ("effect_authorization_invalid",)):
            raise ValueError("effect_authorization_invalid") from None
        raise ValueError("effect_authorization_unexpected_exception") from None
    except Exception:
        raise ValueError("effect_authorization_unexpected_exception") from None


def validate_effect_firewall_decision_v01(
    *,
    firewall: object,
    request: object,
    decision: object,
) -> tuple[str, ...]:
    try:
        errors: list[str] = []
        if _firewall_errors(firewall):
            errors.append("effect_firewall_decision_invalid")
        if type(request) is not EffectRequestV01 or not _request_authorization_shape_valid(request):
            errors.append("effect_firewall_decision_invalid")
        errors.extend(_decision_structure_errors(decision))
        if errors or type(firewall) is not EffectFirewallV01 or type(request) is not EffectRequestV01 or type(decision) is not EffectFirewallDecisionV01:
            return _dedupe(errors)
        if (
            decision.firewall_id != firewall.firewall_id
            or decision.invocation_id != firewall.invocation_id
            or decision.request_id != request.request_id
            or decision.transaction_id != request.transaction_id
            or decision.target_root_id != request.target_root_id
            or decision.root_decision_id != request.root_decision_id
            or decision.adapter_id != request.adapter_id
            or decision.action_kind != request.action_kind
        ):
            errors.append("effect_firewall_decision_binding_mismatch")
        if decision.decision == EFFECT_DECISION_ALLOW_MOCK_EFFECT:
            capability = firewall._state.issued_capabilities.get(
                decision.capability_id or ""
            )
            if (
                _request_errors(request, check_id=True)
                or _authorization_static_block_reason(
                    firewall,
                    request,
                    decision.evaluated_at_tick,
                )
                is not None
                or capability is None
                or not _capability_valid(capability, firewall, request)
                or request.request_id not in firewall._state.seen_request_ids
                or request.idempotency_key not in firewall._state.used_idempotency_keys
                or firewall._state.idempotency_key_by_request_id.get(
                    request.request_id
                )
                != request.idempotency_key
                or firewall._state.authorization_decision_id_by_capability_id.get(
                    decision.capability_id or ""
                )
                != decision.decision_id
            ):
                errors.append("effect_firewall_capability_state_mismatch")
        elif not _blocked_reason_holds(
            firewall,
            request,
            decision.evaluated_at_tick,
            decision.reason_code,
        ):
            errors.append("effect_firewall_reason_mismatch")
        return _dedupe(errors)
    except Exception:
        return ("effect_firewall_decision_unexpected_exception",)


def execute_mock_effect_v01(
    *,
    firewall: object,
    request: object,
    decision: object,
    current_tick: object,
    adapter_id: object,
    action_kind: object,
    child_scope_refs: object,
    child_expires_at_tick: object,
    receipt_artifact_id: object,
    time_envelope: object,
) -> KernelArtifactV01:
    try:
        if (
            _firewall_errors(firewall)
            or _request_errors(request, check_id=True)
            or validate_effect_firewall_decision_v01(
                firewall=firewall,
                request=request,
                decision=decision,
            )
            or type(firewall) is not EffectFirewallV01
            or type(request) is not EffectRequestV01
            or type(decision) is not EffectFirewallDecisionV01
            or decision.decision != EFFECT_DECISION_ALLOW_MOCK_EFFECT
        ):
            raise ValueError("effect_execution_invalid")
        capability = firewall._state.issued_capabilities.get(
            decision.capability_id or ""
        )
        if capability is None:
            raise ValueError("effect_capability_missing")
        if not _capability_valid(capability, firewall, request):
            raise ValueError("effect_capability_forged")
        if capability.capability_id in firewall._state.consumed_capability_ids:
            raise ValueError("effect_capability_consumed")
        if type(current_tick) is not int or current_tick < 0:
            raise ValueError("effect_execution_invalid")
        if current_tick < request.issued_at_tick:
            raise ValueError("effect_request_not_yet_valid")
        if current_tick >= request.expires_at_tick or current_tick >= capability.expires_at_tick:
            raise ValueError("effect_request_expired")
        if type(adapter_id) is not str or adapter_id != request.adapter_id or adapter_id != capability.adapter_id:
            raise ValueError("effect_capability_adapter_mismatch")
        if type(action_kind) is not str or action_kind != request.action_kind or action_kind != capability.action_kind:
            raise ValueError("effect_capability_action_mismatch")
        if not _valid_text_tuple(child_scope_refs, allow_empty=False):
            raise ValueError("effect_scope_expansion_forbidden")
        if not _is_subset(child_scope_refs, request.scope_refs) or not _is_subset(child_scope_refs, firewall.root_scope_refs):
            raise ValueError("effect_scope_expansion_forbidden")
        if (
            type(child_expires_at_tick) is not int
            or child_expires_at_tick <= current_tick
            or child_expires_at_tick > request.expires_at_tick
            or child_expires_at_tick > capability.expires_at_tick
            or child_expires_at_tick > firewall.maximum_expires_at_tick
        ):
            raise ValueError("effect_ttl_expansion_forbidden")
        if not _valid_text(receipt_artifact_id):
            raise ValueError("effect_receipt_invalid")
        if receipt_artifact_id in firewall._state.terminal_receipt_ids:
            raise ValueError("effect_receipt_duplicate")
        payload = {
            "receipt_ref": receipt_artifact_id,
            "request_id": request.request_id,
            "firewall_decision_id": decision.decision_id,
            "capability_id": capability.capability_id,
            "root_decision_id": request.root_decision_id,
            "selected_candidate_id": request.selected_candidate_id,
            "permission_ref": request.permission_ref,
            "adapter_id": adapter_id,
            "action_kind": action_kind,
            "scope_refs": list(child_scope_refs),
            "mock_execution_status": STATUS_PASS,
            "receipt_evidence_only": True,
            "root_confirmation_required": True,
            "root_confirmation_created": False,
            "future_permission_created": False,
            "root_decision_created": False,
            "final_output_created": False,
            "effect_handle_exposed": False,
            "real_world_effects_count": 0,
        }
        try:
            receipt = _build_kernel_artifact_v01(
                abi_version="v1.0",
                artifact_id=receipt_artifact_id,
                artifact_type="EvidenceReceipt",
                schema_version="v1",
                transaction_id=request.transaction_id,
                owner_root_id=request.target_root_id,
                source_component=RECEIPT_SOURCE_COMPONENT,
                authority_class="EVIDENCE_ONLY",
                lifecycle_state="RECEIPT_RECORDED",
                payload=payload,
                trace_refs=(request.request_id, request.root_decision_id, decision.decision_id),
                parent_refs=(request.root_decision_id,),
                time_envelope=time_envelope,
            )
        except Exception:
            raise ValueError("effect_receipt_invalid") from None
        if _validate_kernel_artifact_v01(receipt):
            raise ValueError("effect_receipt_invalid")
        if _effect_receipt_errors(
            firewall=firewall,
            request=request,
            decision=decision,
            receipt=receipt,
            require_execution_state=False,
        ):
            raise ValueError("effect_receipt_invalid")
        new_consumed = set(firewall._state.consumed_capability_ids)
        new_consumed.add(capability.capability_id)
        new_receipts = set(firewall._state.terminal_receipt_ids)
        new_receipts.add(receipt_artifact_id)
        new_receipt_bindings = dict(
            firewall._state.terminal_receipt_id_by_capability_id
        )
        new_receipt_bindings[capability.capability_id] = receipt_artifact_id
        new_execution_count = firewall._state.mock_effect_execution_count + 1
        firewall._state.consumed_capability_ids = new_consumed
        firewall._state.terminal_receipt_ids = new_receipts
        firewall._state.terminal_receipt_id_by_capability_id = new_receipt_bindings
        firewall._state.mock_effect_execution_count = new_execution_count
        return receipt
    except ValueError as exc:
        reason = _allowed_reason(exc, _EXECUTION_REASONS)
        raise ValueError(reason or "effect_execution_unexpected_exception") from None
    except Exception:
        raise ValueError("effect_execution_unexpected_exception") from None


def validate_effect_receipt_v01(
    *,
    firewall: object,
    request: object,
    decision: object,
    receipt: object,
) -> tuple[str, ...]:
    try:
        return _effect_receipt_errors(
            firewall=firewall,
            request=request,
            decision=decision,
            receipt=receipt,
            require_execution_state=True,
        )
    except Exception:
        return ("effect_receipt_unexpected_exception",)


def _effect_receipt_errors(
    *,
    firewall: object,
    request: object,
    decision: object,
    receipt: object,
    require_execution_state: bool,
) -> tuple[str, ...]:
    errors: list[str] = []
    if _firewall_errors(firewall) or _request_errors(request, check_id=True):
        errors.append("effect_receipt_invalid")
    if validate_effect_firewall_decision_v01(
        firewall=firewall,
        request=request,
        decision=decision,
    ):
        errors.append("effect_receipt_invalid")
    if (
        type(decision) is not EffectFirewallDecisionV01
        or decision.decision != EFFECT_DECISION_ALLOW_MOCK_EFFECT
    ):
        errors.append("effect_receipt_invalid")
    if _validate_kernel_artifact_v01(receipt):
        errors.append("effect_receipt_invalid")
    if (
        errors
        or type(firewall) is not EffectFirewallV01
        or type(request) is not EffectRequestV01
        or type(decision) is not EffectFirewallDecisionV01
        or type(receipt) is not KernelArtifactV01
    ):
        return _dedupe(errors)
    plain = _kernel_artifact_to_plain_dict_v01(receipt)
    payload = plain["payload"]
    if type(payload) is not dict or tuple(sorted(payload)) != _RECEIPT_PAYLOAD_KEYS:
        return ("effect_receipt_invalid",)
    if (
        plain["artifact_id"] != payload["receipt_ref"]
        or plain["artifact_type"] != "EvidenceReceipt"
        or plain["abi_version"] != "v1.0"
        or plain["schema_version"] != "v1"
        or plain["transaction_id"] != request.transaction_id
        or plain["owner_root_id"] != request.target_root_id
        or plain["source_component"] != RECEIPT_SOURCE_COMPONENT
        or plain["trace_refs"]
        != [request.request_id, request.root_decision_id, decision.decision_id]
        or plain["parent_refs"] != [request.root_decision_id]
    ):
        errors.append("effect_receipt_binding_mismatch")
    if (
        plain["authority_class"] != "EVIDENCE_ONLY"
        or plain["lifecycle_state"] != "RECEIPT_RECORDED"
        or payload["receipt_evidence_only"] is not True
    ):
        errors.append("effect_receipt_authority_violation")
    if (
        payload["request_id"] != request.request_id
        or payload["firewall_decision_id"] != decision.decision_id
        or payload["capability_id"] != decision.capability_id
        or payload["root_decision_id"] != request.root_decision_id
        or payload["selected_candidate_id"] != request.selected_candidate_id
        or payload["permission_ref"] != request.permission_ref
        or payload["adapter_id"] != request.adapter_id
        or payload["action_kind"] != request.action_kind
        or payload["mock_execution_status"] != STATUS_PASS
        or payload["root_confirmation_required"] is not True
        or payload["root_confirmation_created"] is not False
    ):
        errors.append("effect_receipt_binding_mismatch")
    scope = payload["scope_refs"]
    if (
        not _valid_text_list(scope, allow_empty=False)
        or not _is_subset(tuple(scope), request.scope_refs)
        or not _is_subset(tuple(scope), firewall.root_scope_refs)
    ):
        errors.append("effect_receipt_scope_expansion_forbidden")
    if payload["future_permission_created"] is not False:
        errors.append("effect_receipt_permission_creation_forbidden")
    if payload["root_decision_created"] is not False:
        errors.append("effect_receipt_root_decision_creation_forbidden")
    if payload["final_output_created"] is not False:
        errors.append("effect_receipt_final_output_creation_forbidden")
    if payload["effect_handle_exposed"] is not False:
        errors.append("effect_receipt_effect_handle_exposure_forbidden")
    if (
        type(payload["real_world_effects_count"]) is not int
        or payload["real_world_effects_count"] != 0
    ):
        errors.append("effect_receipt_real_effect_forbidden")
    if require_execution_state and (
        decision.capability_id not in firewall._state.consumed_capability_ids
        or plain["artifact_id"] not in firewall._state.terminal_receipt_ids
        or firewall._state.terminal_receipt_id_by_capability_id.get(
            decision.capability_id or ""
        )
        != plain["artifact_id"]
    ):
        errors.append("effect_receipt_execution_state_mismatch")
    transition = _lookup_transition_v01(
        registry=_build_default_transition_registry_v01(),
        abi_major_version=1,
        source_artifact_type="EvidenceReceipt",
        source_lifecycle_state="RECEIPT_RECORDED",
        actor_role="receipt",
        attempted_effect="RETURN_TO_ROOT",
        target_artifact_type="RootDecision",
        satisfied_guards=("artifact_valid", "receipt_evidence_only"),
        root_commit_present=False,
    )
    if (
        transition.rule_id != "evidence_receipt_to_root_review"
        or transition.decision != _DECISION_RETURN_TO_ROOT
        or transition.reason_code != "receipt_returns_to_root"
        or transition.required_guards
        != ("artifact_valid", "receipt_evidence_only")
        or transition.satisfied_guards
        != ("artifact_valid", "receipt_evidence_only")
        or transition.missing_guards != ()
        or transition.matched is not True
        or transition.root_commit_required is not True
        or transition.root_commit_present is not False
    ):
        errors.append("effect_receipt_return_to_root_invalid")
    return _dedupe(errors)


def effect_request_to_plain_dict_v01(request: EffectRequestV01) -> dict[str, object]:
    try:
        if _request_errors(request, check_id=True):
            raise ValueError("effect_request_invalid")
        projected = _request_plain(request)
        _canonical_json_bytes_v01(projected)
        return projected
    except Exception:
        raise ValueError("effect_request_invalid") from None


def effect_firewall_decision_to_plain_dict_v01(
    decision: EffectFirewallDecisionV01,
) -> dict[str, object]:
    try:
        if _decision_structure_errors(decision):
            raise ValueError("effect_firewall_decision_invalid")
        projected = _decision_plain(decision)
        _canonical_json_bytes_v01(projected)
        return projected
    except Exception:
        raise ValueError("effect_firewall_decision_invalid") from None


def effect_firewall_to_plain_dict_v01(
    firewall: EffectFirewallV01,
) -> dict[str, object]:
    try:
        if _firewall_errors(firewall):
            raise ValueError("effect_firewall_invalid")
        projected = _firewall_plain(firewall)
        projected["state_counters"] = {
            "seen_request_count": len(firewall._state.seen_request_ids),
            "used_idempotency_key_count": len(firewall._state.used_idempotency_keys),
            "issued_capability_count": len(firewall._state.issued_capabilities),
            "consumed_capability_count": len(firewall._state.consumed_capability_ids),
            "terminal_receipt_count": len(firewall._state.terminal_receipt_ids),
            "mock_effect_execution_count": firewall._state.mock_effect_execution_count,
            "real_world_effects_count": 0,
        }
        _canonical_json_bytes_v01(projected)
        return projected
    except Exception:
        raise ValueError("effect_firewall_invalid") from None


_FIREWALL_REASONS = (
    "effect_firewall_invalid",
    "effect_firewall_id_mismatch",
    "effect_firewall_binding_invalid",
    "effect_firewall_adapter_policy_invalid",
    "effect_firewall_action_policy_invalid",
    "effect_firewall_scope_invalid",
    "effect_firewall_time_invalid",
    "effect_firewall_mock_only_required",
    "effect_firewall_effect_owner_invalid",
    "effect_firewall_state_invalid",
)
_REQUEST_REASONS = (
    "effect_request_invalid",
    "effect_request_id_mismatch",
    "effect_request_kind_unknown",
    "effect_request_identity_invalid",
    "effect_request_permission_invalid",
    "effect_request_adapter_invalid",
    "effect_request_action_invalid",
    "effect_request_scope_invalid",
    "effect_request_time_invalid",
    "effect_request_idempotency_invalid",
    "effect_request_real_effect_forbidden",
)


def _validated_root_context(
    kernel: object,
    decision_input: object,
    result: object,
) -> dict[str, str]:
    if (
        type(kernel) is not RootDecisionKernelV01
        or type(decision_input) is not RootDecisionInputV01
        or type(result) is not RootDecisionResultV01
        or _validate_root_decision_result_v01(
            kernel=kernel,
            decision_input=decision_input,
            result=result,
        )
    ):
        raise ValueError("effect_firewall_binding_invalid")
    if (
        result.decision != _ROOT_DECISION_ACCEPT
        or result.root_commit_created is not True
        or not _valid_text(result.selected_candidate_id)
        or result.permission_created is not False
        or result.final_output_created is not False
        or result.effect_requested is not False
        or result.decision_input_id != decision_input.decision_input_id
        or result.transaction_id != decision_input.transaction_id
        or result.target_root_id != decision_input.target_root_id
    ):
        raise ValueError("effect_firewall_binding_invalid")
    input_plain = _root_decision_input_to_plain_dict_v01(decision_input)
    _root_decision_result_to_plain_dict_v01(result)
    permission = input_plain["permission_state"]
    if (
        type(permission) is not dict
        or permission.get("permission_required") is not True
        or permission.get("user_permission_present") is not True
        or permission.get("permission_scope_valid") is not True
        or not _valid_text(permission.get("permission_ref"))
        or not permission["permission_ref"].startswith("permission:")
    ):
        raise ValueError("effect_firewall_binding_invalid")
    return {
        "transaction_id": result.transaction_id,
        "target_root_id": result.target_root_id,
        "root_decision_id": result.decision_id,
        "selected_candidate_id": result.selected_candidate_id,
        "permission_ref": permission["permission_ref"],
    }


def _firewall_errors(firewall: object) -> tuple[str, ...]:
    if type(firewall) is not EffectFirewallV01:
        return ("effect_firewall_invalid",)
    errors: list[str] = []
    if not all(
        _valid_text(value)
        for value in (
            firewall.firewall_id,
            firewall.invocation_id,
            firewall.transaction_id,
            firewall.target_root_id,
            firewall.root_decision_id,
            firewall.selected_candidate_id,
            firewall.permission_ref,
        )
    ) or not firewall.permission_ref.startswith("permission:"):
        errors.append("effect_firewall_binding_invalid")
    if firewall.firewall_version != EFFECT_FIREWALL_VERSION:
        errors.append("effect_firewall_invalid")
    if not _valid_text_tuple(firewall.allowed_adapter_ids, allow_empty=False) or any(not item.startswith(MOCK_ADAPTER_PREFIX) for item in firewall.allowed_adapter_ids):
        errors.append("effect_firewall_adapter_policy_invalid")
    if not _valid_text_tuple(firewall.allowed_action_kinds, allow_empty=False) or any(not item.startswith(MOCK_ACTION_PREFIX) for item in firewall.allowed_action_kinds):
        errors.append("effect_firewall_action_policy_invalid")
    if not _valid_text_tuple(firewall.root_scope_refs, allow_empty=False):
        errors.append("effect_firewall_scope_invalid")
    if type(firewall.maximum_expires_at_tick) is not int or firewall.maximum_expires_at_tick <= 0:
        errors.append("effect_firewall_time_invalid")
    if firewall.mock_only is not True:
        errors.append("effect_firewall_mock_only_required")
    if firewall.effect_access_owner != EFFECT_ACCESS_OWNER:
        errors.append("effect_firewall_effect_owner_invalid")
    try:
        expected_id = _hash(_FIREWALL_DOMAIN, _firewall_plain(firewall, include_id=False))
    except Exception:
        expected_id = None
    if firewall.firewall_id != expected_id:
        errors.append("effect_firewall_id_mismatch")
    if not _firewall_state_valid(firewall):
        errors.append("effect_firewall_state_invalid")
    return _dedupe(errors)


def _issuer_token_valid(
    token: object,
    firewall_id: str,
    state: object,
) -> bool:
    return bool(
        type(token) is _FirewallIssuerToken
        and token._origin_marker is _FIREWALL_ORIGIN_MARKER
        and type(token._firewall_id) is str
        and token._firewall_id == firewall_id
        and token._state is state
    )


def _firewall_state_valid(firewall: EffectFirewallV01) -> bool:
    try:
        state = firewall._state
        if (
            type(state) is not _InvocationState
            or state.issuer_token is not firewall._issuer_token
            or not _issuer_token_valid(
                firewall._issuer_token,
                firewall.firewall_id,
                state,
            )
            or type(state.seen_request_ids) is not set
            or type(state.used_idempotency_keys) is not set
            or type(state.issued_capabilities) is not dict
            or type(state.idempotency_key_by_request_id) is not dict
            or type(state.authorization_decision_id_by_capability_id) is not dict
            or type(state.consumed_capability_ids) is not set
            or type(state.terminal_receipt_ids) is not set
            or type(state.terminal_receipt_id_by_capability_id) is not dict
            or type(state.mock_effect_execution_count) is not int
            or state.mock_effect_execution_count < 0
        ):
            return False
        if any(
            not _valid_sha256(value)
            for value in (
                *state.seen_request_ids,
                *state.issued_capabilities,
                *state.idempotency_key_by_request_id,
                *state.authorization_decision_id_by_capability_id,
                *state.consumed_capability_ids,
                *state.terminal_receipt_id_by_capability_id,
            )
        ):
            return False
        if (
            not all(_valid_text(item) for item in state.used_idempotency_keys)
            or not all(_valid_text(item) for item in state.terminal_receipt_ids)
            or not all(
                _valid_text(value)
                for value in state.idempotency_key_by_request_id.values()
            )
            or not all(
                _valid_sha256(value)
                for value in state.authorization_decision_id_by_capability_id.values()
            )
            or not all(
                _valid_text(value)
                for value in state.terminal_receipt_id_by_capability_id.values()
            )
        ):
            return False
        if any(
            key != capability.capability_id
            or not _capability_valid(capability, firewall)
            for key, capability in state.issued_capabilities.items()
        ):
            return False
        issued_ids = set(state.issued_capabilities)
        issued_request_ids = {
            capability.request_id
            for capability in state.issued_capabilities.values()
        }
        request_keys = state.idempotency_key_by_request_id
        request_key_values = tuple(request_keys.values())
        receipt_bindings = state.terminal_receipt_id_by_capability_id
        receipt_ids = tuple(receipt_bindings.values())
        if (
            len(issued_request_ids) != len(issued_ids)
            or state.seen_request_ids != issued_request_ids
            or set(request_keys) != state.seen_request_ids
            or len(request_key_values) != len(set(request_key_values))
            or state.used_idempotency_keys != set(request_key_values)
            or set(state.authorization_decision_id_by_capability_id) != issued_ids
            or not state.consumed_capability_ids.issubset(issued_ids)
            or set(receipt_bindings) != state.consumed_capability_ids
            or len(receipt_ids) != len(set(receipt_ids))
            or state.terminal_receipt_ids != set(receipt_ids)
            or state.mock_effect_execution_count
            != len(state.consumed_capability_ids)
            or state.mock_effect_execution_count != len(state.terminal_receipt_ids)
            or state.mock_effect_execution_count != len(receipt_bindings)
            or state.mock_effect_execution_count > len(issued_ids)
        ):
            return False
        return True
    except Exception:
        return False


def _request_errors(request: object, *, check_id: bool) -> tuple[str, ...]:
    if type(request) is not EffectRequestV01:
        return ("effect_request_invalid",)
    errors: list[str] = []
    if type(request.request_kind) is not str or request.request_kind not in EFFECT_REQUEST_KINDS:
        errors.append("effect_request_kind_unknown")
    if not all(_valid_text(value) for value in (request.transaction_id, request.target_root_id, request.root_decision_id, request.selected_candidate_id)):
        errors.append("effect_request_identity_invalid")
    if not _valid_text(request.permission_ref) or not request.permission_ref.startswith("permission:"):
        errors.append("effect_request_permission_invalid")
    if not _valid_text(request.adapter_id) or not request.adapter_id.startswith(MOCK_ADAPTER_PREFIX):
        errors.append("effect_request_adapter_invalid")
    if not _valid_text(request.action_kind) or not request.action_kind.startswith(MOCK_ACTION_PREFIX):
        errors.append("effect_request_action_invalid")
    if not _valid_text_tuple(request.scope_refs, allow_empty=False):
        errors.append("effect_request_scope_invalid")
    if (
        type(request.issued_at_tick) is not int
        or request.issued_at_tick < 0
        or type(request.expires_at_tick) is not int
        or request.expires_at_tick <= request.issued_at_tick
    ):
        errors.append("effect_request_time_invalid")
    if not _valid_text(request.idempotency_key):
        errors.append("effect_request_idempotency_invalid")
    if request.mock_only is not True:
        errors.append("effect_request_real_effect_forbidden")
    if check_id:
        try:
            if not _valid_sha256(request.request_id) or request.request_id != _request_id(request):
                errors.append("effect_request_id_mismatch")
        except Exception:
            errors.append("effect_request_id_mismatch")
    return _dedupe(errors)


def _request_authorization_shape_valid(request: EffectRequestV01) -> bool:
    return bool(
        type(request.request_kind) is str
        and request.request_kind in EFFECT_REQUEST_KINDS
        and all(
            _valid_text(value)
            for value in (
                request.request_id,
                request.transaction_id,
                request.target_root_id,
                request.root_decision_id,
                request.selected_candidate_id,
                request.permission_ref,
                request.adapter_id,
                request.action_kind,
                request.idempotency_key,
            )
        )
        and _valid_text_tuple(request.scope_refs, allow_empty=False)
        and type(request.issued_at_tick) is int
        and request.issued_at_tick >= 0
        and type(request.expires_at_tick) is int
        and request.expires_at_tick > request.issued_at_tick
        and type(request.mock_only) is bool
    )


def _authorization_block_reason(
    firewall: EffectFirewallV01,
    request: EffectRequestV01,
    current_tick: int,
) -> str | None:
    reason = _authorization_static_block_reason(firewall, request, current_tick)
    if reason is not None:
        return reason
    if request.request_id in firewall._state.seen_request_ids:
        return "duplicate_request"
    if request.idempotency_key in firewall._state.used_idempotency_keys:
        return "duplicate_idempotency_key"
    return None


def _authorization_static_block_reason(
    firewall: EffectFirewallV01,
    request: EffectRequestV01,
    current_tick: int,
) -> str | None:
    if (
        request.transaction_id != firewall.transaction_id
        or request.target_root_id != firewall.target_root_id
        or request.root_decision_id != firewall.root_decision_id
        or request.selected_candidate_id != firewall.selected_candidate_id
    ):
        return "request_root_binding_mismatch"
    if request.permission_ref != firewall.permission_ref:
        return "permission_binding_mismatch"
    if request.mock_only is not True or not request.adapter_id.startswith(MOCK_ADAPTER_PREFIX) or not request.action_kind.startswith(MOCK_ACTION_PREFIX):
        return "real_effect_forbidden"
    if request.adapter_id not in firewall.allowed_adapter_ids:
        return "adapter_not_allowed"
    if request.action_kind not in firewall.allowed_action_kinds:
        return "action_not_allowed"
    if not _is_subset(request.scope_refs, firewall.root_scope_refs):
        return "scope_expansion_forbidden"
    if request.expires_at_tick > firewall.maximum_expires_at_tick:
        return "ttl_expansion_forbidden"
    if current_tick < request.issued_at_tick:
        return "request_not_yet_valid"
    if current_tick >= request.expires_at_tick:
        return "request_expired"
    return None


def _blocked_reason_holds(
    firewall: EffectFirewallV01,
    request: EffectRequestV01,
    tick: int,
    reason: str,
) -> bool:
    if reason == "forged_request":
        return request.request_id != _request_id(request)
    if reason == "duplicate_request":
        return request.request_id in firewall._state.seen_request_ids
    if reason == "duplicate_idempotency_key":
        return request.idempotency_key in firewall._state.used_idempotency_keys
    return _authorization_block_reason(firewall, request, tick) == reason


def _issue_capability(
    firewall: EffectFirewallV01,
    request: EffectRequestV01,
) -> EffectCapabilityV01:
    material = {
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
        "scope_refs": list(request.scope_refs),
        "expires_at_tick": request.expires_at_tick,
    }
    capability = object.__new__(EffectCapabilityV01)
    for name, value in (
        ("_capability_id", _hash(_CAPABILITY_DOMAIN, material)),
        ("_firewall_id", firewall.firewall_id),
        ("_invocation_id", firewall.invocation_id),
        ("_request_id", request.request_id),
        ("_transaction_id", request.transaction_id),
        ("_target_root_id", request.target_root_id),
        ("_root_decision_id", request.root_decision_id),
        ("_selected_candidate_id", request.selected_candidate_id),
        ("_permission_ref", request.permission_ref),
        ("_adapter_id", request.adapter_id),
        ("_action_kind", request.action_kind),
        ("_scope_refs", request.scope_refs),
        ("_expires_at_tick", request.expires_at_tick),
        ("_issuer_token", firewall._issuer_token),
        ("_state", firewall._state),
    ):
        object.__setattr__(capability, name, value)
    return capability


def _capability_valid(
    capability: object,
    firewall: EffectFirewallV01,
    request: EffectRequestV01 | None = None,
) -> bool:
    if type(capability) is not EffectCapabilityV01:
        return False
    try:
        material = {
            "firewall_id": capability.firewall_id,
            "invocation_id": capability.invocation_id,
            "request_id": capability.request_id,
            "transaction_id": capability.transaction_id,
            "target_root_id": capability.target_root_id,
            "root_decision_id": capability.root_decision_id,
            "selected_candidate_id": capability.selected_candidate_id,
            "permission_ref": capability.permission_ref,
            "adapter_id": capability.adapter_id,
            "action_kind": capability.action_kind,
            "scope_refs": list(capability.scope_refs),
            "expires_at_tick": capability.expires_at_tick,
        }
        if (
            capability._issuer_token is not firewall._issuer_token
            or capability._state is not firewall._state
            or capability.capability_id != _hash(_CAPABILITY_DOMAIN, material)
            or capability.firewall_id != firewall.firewall_id
            or capability.invocation_id != firewall.invocation_id
            or capability.transaction_id != firewall.transaction_id
            or capability.target_root_id != firewall.target_root_id
            or capability.root_decision_id != firewall.root_decision_id
            or capability.selected_candidate_id != firewall.selected_candidate_id
            or capability.permission_ref != firewall.permission_ref
            or capability.adapter_id not in firewall.allowed_adapter_ids
            or capability.action_kind not in firewall.allowed_action_kinds
            or not _is_subset(capability.scope_refs, firewall.root_scope_refs)
            or capability.expires_at_tick > firewall.maximum_expires_at_tick
        ):
            return False
        if request is not None and (
            capability.request_id != request.request_id
            or capability.transaction_id != request.transaction_id
            or capability.target_root_id != request.target_root_id
            or capability.root_decision_id != request.root_decision_id
            or capability.selected_candidate_id != request.selected_candidate_id
            or capability.permission_ref != request.permission_ref
            or capability.adapter_id != request.adapter_id
            or capability.action_kind != request.action_kind
            or capability.scope_refs != request.scope_refs
            or capability.expires_at_tick != request.expires_at_tick
        ):
            return False
        return True
    except Exception:
        return False


def _allowed_decision(
    firewall: EffectFirewallV01,
    request: EffectRequestV01,
    tick: int,
    capability: EffectCapabilityV01,
) -> EffectFirewallDecisionV01:
    return _build_decision(
        firewall,
        request,
        tick,
        EFFECT_DECISION_ALLOW_MOCK_EFFECT,
        "mock_effect_authorized",
        capability.capability_id,
        True,
        False,
    )


def _blocked_decision(
    firewall: EffectFirewallV01,
    request: EffectRequestV01,
    tick: int,
    reason: str,
) -> EffectFirewallDecisionV01:
    return _build_decision(
        firewall,
        request,
        tick,
        EFFECT_DECISION_BLOCKED_FAIL_CLOSED,
        reason,
        None,
        False,
        True,
    )


def _build_decision(
    firewall: EffectFirewallV01,
    request: EffectRequestV01,
    tick: int,
    decision: str,
    reason: str,
    capability_id: str | None,
    capability_issued: bool,
    return_to_root: bool,
) -> EffectFirewallDecisionV01:
    provisional = EffectFirewallDecisionV01(
        decision_id="0" * 64,
        firewall_id=firewall.firewall_id,
        invocation_id=firewall.invocation_id,
        request_id=request.request_id,
        transaction_id=request.transaction_id,
        target_root_id=request.target_root_id,
        root_decision_id=request.root_decision_id,
        adapter_id=request.adapter_id,
        action_kind=request.action_kind,
        evaluated_at_tick=tick,
        decision=decision,
        reason_code=reason,
        capability_id=capability_id,
        capability_issued=capability_issued,
        return_to_root=return_to_root,
        real_world_effects_count=0,
    )
    return EffectFirewallDecisionV01(
        decision_id=_decision_id(provisional),
        firewall_id=provisional.firewall_id,
        invocation_id=provisional.invocation_id,
        request_id=provisional.request_id,
        transaction_id=provisional.transaction_id,
        target_root_id=provisional.target_root_id,
        root_decision_id=provisional.root_decision_id,
        adapter_id=provisional.adapter_id,
        action_kind=provisional.action_kind,
        evaluated_at_tick=tick,
        decision=decision,
        reason_code=reason,
        capability_id=capability_id,
        capability_issued=capability_issued,
        return_to_root=return_to_root,
        real_world_effects_count=0,
    )


def _decision_structure_errors(decision: object) -> tuple[str, ...]:
    if type(decision) is not EffectFirewallDecisionV01:
        return ("effect_firewall_decision_invalid",)
    errors: list[str] = []
    if not all(
        _valid_text(value)
        for value in (
            decision.decision_id,
            decision.firewall_id,
            decision.invocation_id,
            decision.request_id,
            decision.transaction_id,
            decision.target_root_id,
            decision.root_decision_id,
            decision.adapter_id,
            decision.action_kind,
            decision.reason_code,
        )
    ) or type(decision.evaluated_at_tick) is not int or decision.evaluated_at_tick < 0:
        errors.append("effect_firewall_decision_invalid")
    if type(decision.decision) is not str or decision.decision not in EFFECT_FIREWALL_DECISIONS:
        errors.append("effect_firewall_decision_invalid")
    if decision.decision == EFFECT_DECISION_ALLOW_MOCK_EFFECT:
        if (
            decision.reason_code != "mock_effect_authorized"
            or not _valid_sha256(decision.capability_id)
            or decision.capability_issued is not True
            or decision.return_to_root is not False
        ):
            errors.append("effect_firewall_reason_mismatch")
    elif (
        decision.reason_code not in _BLOCK_REASONS
        or decision.capability_id is not None
        or decision.capability_issued is not False
        or decision.return_to_root is not True
    ):
        errors.append("effect_firewall_reason_mismatch")
    if type(decision.real_world_effects_count) is not int or decision.real_world_effects_count != 0:
        errors.append("effect_firewall_decision_invalid")
    if not errors:
        try:
            if decision.decision_id != _decision_id(decision):
                errors.append("effect_firewall_decision_id_mismatch")
        except Exception:
            errors.append("effect_firewall_decision_id_mismatch")
    return _dedupe(errors)


def _firewall_plain(
    firewall: EffectFirewallV01,
    *,
    include_id: bool = True,
) -> dict[str, object]:
    projected: dict[str, object] = {
        "firewall_version": firewall.firewall_version,
        "invocation_id": firewall.invocation_id,
        "transaction_id": firewall.transaction_id,
        "target_root_id": firewall.target_root_id,
        "root_decision_id": firewall.root_decision_id,
        "selected_candidate_id": firewall.selected_candidate_id,
        "permission_ref": firewall.permission_ref,
        "allowed_adapter_ids": list(firewall.allowed_adapter_ids),
        "allowed_action_kinds": list(firewall.allowed_action_kinds),
        "root_scope_refs": list(firewall.root_scope_refs),
        "maximum_expires_at_tick": firewall.maximum_expires_at_tick,
        "mock_only": firewall.mock_only,
        "effect_access_owner": firewall.effect_access_owner,
    }
    if include_id:
        return {"firewall_id": firewall.firewall_id, **projected}
    return projected


def _request_plain(request: EffectRequestV01) -> dict[str, object]:
    return {
        "request_id": request.request_id,
        "request_kind": request.request_kind,
        "transaction_id": request.transaction_id,
        "target_root_id": request.target_root_id,
        "root_decision_id": request.root_decision_id,
        "selected_candidate_id": request.selected_candidate_id,
        "permission_ref": request.permission_ref,
        "adapter_id": request.adapter_id,
        "action_kind": request.action_kind,
        "scope_refs": list(request.scope_refs),
        "issued_at_tick": request.issued_at_tick,
        "expires_at_tick": request.expires_at_tick,
        "idempotency_key": request.idempotency_key,
        "mock_only": request.mock_only,
    }


def _decision_plain(decision: EffectFirewallDecisionV01) -> dict[str, object]:
    return {
        "decision_id": decision.decision_id,
        "firewall_id": decision.firewall_id,
        "invocation_id": decision.invocation_id,
        "request_id": decision.request_id,
        "transaction_id": decision.transaction_id,
        "target_root_id": decision.target_root_id,
        "root_decision_id": decision.root_decision_id,
        "adapter_id": decision.adapter_id,
        "action_kind": decision.action_kind,
        "evaluated_at_tick": decision.evaluated_at_tick,
        "decision": decision.decision,
        "reason_code": decision.reason_code,
        "capability_id": decision.capability_id,
        "capability_issued": decision.capability_issued,
        "return_to_root": decision.return_to_root,
        "real_world_effects_count": decision.real_world_effects_count,
    }


def _request_id(request: EffectRequestV01) -> str:
    material = _request_plain(request)
    material.pop("request_id")
    return _hash(_REQUEST_DOMAIN, material)


def _decision_id(decision: EffectFirewallDecisionV01) -> str:
    material = _decision_plain(decision)
    material.pop("decision_id")
    return _hash(_DECISION_DOMAIN, material)


def _hash(domain: str, value: object) -> str:
    return _domain_separated_sha256_hex_v01(
        domain=domain,
        payload=_canonical_json_bytes_v01(value),
    )


def _valid_text(value: object) -> bool:
    if type(value) is not str or not value:
        return False
    try:
        _canonical_json_bytes_v01(value)
        return True
    except Exception:
        return False


def _valid_sha256(value: object) -> bool:
    return bool(
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _valid_text_tuple(value: object, *, allow_empty: bool) -> bool:
    return bool(
        type(value) is tuple
        and (allow_empty or value)
        and all(_valid_text(item) for item in value)
        and len(value) == len(set(value))
    )


def _valid_text_list(value: object, *, allow_empty: bool) -> bool:
    return bool(
        type(value) is list
        and (allow_empty or value)
        and all(_valid_text(item) for item in value)
        and len(value) == len(set(value))
    )


def _is_subset(child: tuple[str, ...], parent: tuple[str, ...]) -> bool:
    return all(item in parent for item in child)


def _allowed_reason(error: ValueError, allowed: tuple[str, ...]) -> str | None:
    if len(error.args) == 1 and type(error.args[0]) is str and error.args[0] in allowed:
        return error.args[0]
    return None


def _dedupe(values: object) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))
