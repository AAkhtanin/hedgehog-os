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
from dataclasses import fields as _fields
from dataclasses import replace as _replace

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
EFFECT_FIREWALL_HISTORICAL_AUTHORIZATION_PROFILE_ID_V01 = (
    "effect_firewall_historical_authorization_projection_v01"
)
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
        "started_capability_ids",
        "native_evidence_by_capability_id",
        "native_authorization",
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
        self.started_capability_ids: set[str] = set()
        self.native_evidence_by_capability_id: dict[str, object] = {}
        self.native_authorization = None
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
class EffectFirewallHistoricalAuthorizationProjectionV01:
    profile_id: str
    firewall_id: str
    request: EffectRequestV01
    decision: EffectFirewallDecisionV01
    expected_capability_id: str | None
    fresh_empty_invocation_state: bool
    firewall_object_created: bool
    capability_object_created: bool
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


def project_effect_firewall_historical_authorization_v01(
    *,
    root_decision_kernel: object,
    decision_input: object,
    root_decision_result: object,
    invocation_id: object,
    allowed_adapter_ids: object,
    allowed_action_kinds: object,
    root_scope_refs: object,
    maximum_expires_at_tick: object,
    request_kind: object,
    adapter_id: object,
    action_kind: object,
    scope_refs: object,
    issued_at_tick: object,
    expires_at_tick: object,
    idempotency_key: object,
    current_tick: object,
) -> EffectFirewallHistoricalAuthorizationProjectionV01:
    try:
        request = build_effect_request_v01(
            root_decision_kernel=root_decision_kernel,
            decision_input=decision_input,
            root_decision_result=root_decision_result,
            request_kind=request_kind,
            adapter_id=adapter_id,
            action_kind=action_kind,
            scope_refs=scope_refs,
            issued_at_tick=issued_at_tick,
            expires_at_tick=expires_at_tick,
            idempotency_key=idempotency_key,
        )
        return _project_effect_firewall_historical_request_v01(
            root_decision_kernel=root_decision_kernel,
            decision_input=decision_input,
            root_decision_result=root_decision_result,
            invocation_id=invocation_id,
            allowed_adapter_ids=allowed_adapter_ids,
            allowed_action_kinds=allowed_action_kinds,
            root_scope_refs=root_scope_refs,
            maximum_expires_at_tick=maximum_expires_at_tick,
            request=request,
            current_tick=current_tick,
        )
    except ValueError as exc:
        reason = _allowed_reason(
            exc,
            (
                *_FIREWALL_REASONS,
                *_REQUEST_REASONS,
                "effect_firewall_historical_projection_invalid",
            ),
        )
        raise ValueError(
            reason or "effect_firewall_historical_projection_invalid"
        ) from None
    except Exception:
        raise ValueError(
            "effect_firewall_historical_projection_invalid"
        ) from None


def validate_effect_firewall_historical_authorization_projection_v01(
    projection: object,
    *,
    root_decision_kernel: object,
    decision_input: object,
    root_decision_result: object,
    invocation_id: object,
    allowed_adapter_ids: object,
    allowed_action_kinds: object,
    root_scope_refs: object,
    maximum_expires_at_tick: object,
    request_kind: object,
    adapter_id: object,
    action_kind: object,
    scope_refs: object,
    issued_at_tick: object,
    expires_at_tick: object,
    idempotency_key: object,
    current_tick: object,
) -> tuple[str, ...]:
    try:
        if not _historical_projection_shape_valid(projection):
            return ("effect_firewall_historical_projection_invalid",)
        expected = project_effect_firewall_historical_authorization_v01(
            root_decision_kernel=root_decision_kernel,
            decision_input=decision_input,
            root_decision_result=root_decision_result,
            invocation_id=invocation_id,
            allowed_adapter_ids=allowed_adapter_ids,
            allowed_action_kinds=allowed_action_kinds,
            root_scope_refs=root_scope_refs,
            maximum_expires_at_tick=maximum_expires_at_tick,
            request_kind=request_kind,
            adapter_id=adapter_id,
            action_kind=action_kind,
            scope_refs=scope_refs,
            issued_at_tick=issued_at_tick,
            expires_at_tick=expires_at_tick,
            idempotency_key=idempotency_key,
            current_tick=current_tick,
        )
        if projection != expected:
            return ("effect_firewall_historical_projection_mismatch",)
        return ()
    except Exception:
        return ("effect_firewall_historical_projection_invalid",)


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


def _begin_exclusive_effect_v01(*, firewall, request, decision, current_tick,
    adapter_id, action_kind, child_scope_refs, child_expires_at_tick):
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
    if capability.capability_id in firewall._state.started_capability_ids:
        raise ValueError("effect_capability_consumed")
    return capability


def _record_exclusive_consumption_v01(firewall, capability, receipt_artifact_id):
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
        capability = _begin_exclusive_effect_v01(firewall=firewall, request=request, decision=decision,
            current_tick=current_tick, adapter_id=adapter_id, action_kind=action_kind,
            child_scope_refs=child_scope_refs, child_expires_at_tick=child_expires_at_tick)
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
        _record_exclusive_consumption_v01(firewall, capability, receipt_artifact_id)
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
    errors.extend(_retained_effect_receipt_contract_errors_v01(receipt=receipt, request=request, decision=decision,
        root_scope_refs=firewall.root_scope_refs))
    plain = _kernel_artifact_to_plain_dict_v01(receipt)
    observed = firewall._state.native_evidence_by_capability_id.get(decision.capability_id)
    if observed is not None:
        if (tuple(sorted(plain['payload'])) != _NATIVE_RECEIPT_KEYS or
            plain['payload']['execution_evidence'] != native_execution_evidence_to_plain_data_v01(observed)):
            errors.append('effect_receipt_execution_evidence_mismatch')
    elif tuple(sorted(plain['payload'])) == _NATIVE_RECEIPT_KEYS:
        errors.append('effect_receipt_not_observed_native_execution')
    if require_execution_state and (
        decision.capability_id not in firewall._state.consumed_capability_ids
        or plain["artifact_id"] not in firewall._state.terminal_receipt_ids
        or firewall._state.terminal_receipt_id_by_capability_id.get(
            decision.capability_id or ""
        )
        != plain["artifact_id"]
    ):
        errors.append("effect_receipt_execution_state_mismatch")
    return _dedupe(errors)


def _retained_effect_receipt_contract_errors_v01(*, receipt, request, decision, root_scope_refs):
    errors: list[str] = []
    plain = _kernel_artifact_to_plain_dict_v01(receipt)
    payload = plain["payload"]
    if type(payload) is not dict or tuple(sorted(payload)) not in (_RECEIPT_PAYLOAD_KEYS, _NATIVE_RECEIPT_KEYS):
        return ("effect_receipt_invalid",)
    if tuple(sorted(payload)) == _NATIVE_RECEIPT_KEYS:
        errors.extend(_native_effect_receipt_binding_errors_v01(receipt, request, decision))
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
        or not _is_subset(tuple(scope), root_scope_refs)
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


def _historical_firewall_values_v01(
    *,
    root_decision_kernel: object,
    decision_input: object,
    root_decision_result: object,
    invocation_id: object,
    allowed_adapter_ids: object,
    allowed_action_kinds: object,
    root_scope_refs: object,
    maximum_expires_at_tick: object,
) -> dict[str, object]:
    context = _validated_root_context(
        root_decision_kernel,
        decision_input,
        root_decision_result,
    )
    if not _valid_text(invocation_id):
        raise ValueError("effect_firewall_binding_invalid")
    if not _valid_text_tuple(
        allowed_adapter_ids,
        allow_empty=False,
    ) or any(
        not item.startswith(MOCK_ADAPTER_PREFIX)
        for item in allowed_adapter_ids
    ):
        raise ValueError("effect_firewall_adapter_policy_invalid")
    if not _valid_text_tuple(
        allowed_action_kinds,
        allow_empty=False,
    ) or any(
        not item.startswith(MOCK_ACTION_PREFIX)
        for item in allowed_action_kinds
    ):
        raise ValueError("effect_firewall_action_policy_invalid")
    if not _valid_text_tuple(root_scope_refs, allow_empty=False):
        raise ValueError("effect_firewall_scope_invalid")
    if (
        type(maximum_expires_at_tick) is not int
        or maximum_expires_at_tick <= 0
    ):
        raise ValueError("effect_firewall_time_invalid")
    values: dict[str, object] = {
        "firewall_version": EFFECT_FIREWALL_VERSION,
        "invocation_id": invocation_id,
        "transaction_id": context["transaction_id"],
        "target_root_id": context["target_root_id"],
        "root_decision_id": context["root_decision_id"],
        "selected_candidate_id": context["selected_candidate_id"],
        "permission_ref": context["permission_ref"],
        "allowed_adapter_ids": allowed_adapter_ids,
        "allowed_action_kinds": allowed_action_kinds,
        "root_scope_refs": root_scope_refs,
        "maximum_expires_at_tick": maximum_expires_at_tick,
        "mock_only": True,
        "effect_access_owner": EFFECT_ACCESS_OWNER,
    }
    material = {
        key: list(value) if type(value) is tuple else value
        for key, value in values.items()
    }
    values["firewall_id"] = _hash(_FIREWALL_DOMAIN, material)
    return values


def _historical_static_block_reason_v01(
    firewall_values: dict[str, object],
    request: EffectRequestV01,
    current_tick: int,
) -> str | None:
    if (
        request.transaction_id != firewall_values["transaction_id"]
        or request.target_root_id != firewall_values["target_root_id"]
        or request.root_decision_id != firewall_values["root_decision_id"]
        or request.selected_candidate_id
        != firewall_values["selected_candidate_id"]
    ):
        return "request_root_binding_mismatch"
    if request.permission_ref != firewall_values["permission_ref"]:
        return "permission_binding_mismatch"
    if (
        request.mock_only is not True
        or not request.adapter_id.startswith(MOCK_ADAPTER_PREFIX)
        or not request.action_kind.startswith(MOCK_ACTION_PREFIX)
    ):
        return "real_effect_forbidden"
    if request.adapter_id not in firewall_values["allowed_adapter_ids"]:
        return "adapter_not_allowed"
    if request.action_kind not in firewall_values["allowed_action_kinds"]:
        return "action_not_allowed"
    if not _is_subset(
        request.scope_refs,
        firewall_values["root_scope_refs"],
    ):
        return "scope_expansion_forbidden"
    if (
        request.expires_at_tick
        > firewall_values["maximum_expires_at_tick"]
    ):
        return "ttl_expansion_forbidden"
    if current_tick < request.issued_at_tick:
        return "request_not_yet_valid"
    if current_tick >= request.expires_at_tick:
        return "request_expired"
    return None


def _historical_capability_id_v01(
    firewall_values: dict[str, object],
    request: EffectRequestV01,
) -> str:
    return _hash(
        _CAPABILITY_DOMAIN,
        {
            "firewall_id": firewall_values["firewall_id"],
            "invocation_id": firewall_values["invocation_id"],
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
        },
    )


def _project_effect_firewall_historical_request_v01(
    *,
    root_decision_kernel: object,
    decision_input: object,
    root_decision_result: object,
    invocation_id: object,
    allowed_adapter_ids: object,
    allowed_action_kinds: object,
    root_scope_refs: object,
    maximum_expires_at_tick: object,
    request: object,
    current_tick: object,
) -> EffectFirewallHistoricalAuthorizationProjectionV01:
    values = _historical_firewall_values_v01(
        root_decision_kernel=root_decision_kernel,
        decision_input=decision_input,
        root_decision_result=root_decision_result,
        invocation_id=invocation_id,
        allowed_adapter_ids=allowed_adapter_ids,
        allowed_action_kinds=allowed_action_kinds,
        root_scope_refs=root_scope_refs,
        maximum_expires_at_tick=maximum_expires_at_tick,
    )
    if (
        type(request) is not EffectRequestV01
        or not _request_authorization_shape_valid(request)
        or type(current_tick) is not int
        or current_tick < 0
    ):
        raise ValueError("effect_firewall_historical_projection_invalid")
    if request.request_id != _request_id(request):
        reason = "forged_request"
    else:
        reason = _historical_static_block_reason_v01(
            values,
            request,
            current_tick,
        )
    capability_id = (
        _historical_capability_id_v01(values, request)
        if reason is None
        else None
    )
    decision = _build_decision_values_v01(
        firewall_id=values["firewall_id"],
        invocation_id=values["invocation_id"],
        request=request,
        tick=current_tick,
        decision=(
            EFFECT_DECISION_ALLOW_MOCK_EFFECT
            if reason is None
            else EFFECT_DECISION_BLOCKED_FAIL_CLOSED
        ),
        reason="mock_effect_authorized" if reason is None else reason,
        capability_id=capability_id,
        capability_issued=reason is None,
        return_to_root=reason is not None,
    )
    projection = EffectFirewallHistoricalAuthorizationProjectionV01(
        profile_id=(
            EFFECT_FIREWALL_HISTORICAL_AUTHORIZATION_PROFILE_ID_V01
        ),
        firewall_id=values["firewall_id"],
        request=request,
        decision=decision,
        expected_capability_id=capability_id,
        fresh_empty_invocation_state=True,
        firewall_object_created=False,
        capability_object_created=False,
        real_world_effects_count=0,
    )
    if not _historical_projection_shape_valid(projection):
        raise ValueError("effect_firewall_historical_projection_invalid")
    return projection


def _historical_projection_shape_valid(projection: object) -> bool:
    if (
        type(projection)
        is not EffectFirewallHistoricalAuthorizationProjectionV01
    ):
        return False
    try:
        decision = projection.decision
        return bool(
            projection.profile_id
            == EFFECT_FIREWALL_HISTORICAL_AUTHORIZATION_PROFILE_ID_V01
            and _valid_sha256(projection.firewall_id)
            and type(projection.request) is EffectRequestV01
            and _request_authorization_shape_valid(projection.request)
            and type(decision) is EffectFirewallDecisionV01
            and not _decision_structure_errors(decision)
            and decision.firewall_id == projection.firewall_id
            and projection.expected_capability_id
            == decision.capability_id
            and projection.fresh_empty_invocation_state is True
            and type(projection.fresh_empty_invocation_state) is bool
            and projection.firewall_object_created is False
            and type(projection.firewall_object_created) is bool
            and projection.capability_object_created is False
            and type(projection.capability_object_created) is bool
            and type(projection.real_world_effects_count) is int
            and projection.real_world_effects_count == 0
            and (
                decision.decision == EFFECT_DECISION_ALLOW_MOCK_EFFECT
                and _valid_sha256(projection.expected_capability_id)
                or decision.decision
                == EFFECT_DECISION_BLOCKED_FAIL_CLOSED
                and projection.expected_capability_id is None
            )
        )
    except Exception:
        return False


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
            or type(state.started_capability_ids) is not set
            or type(state.native_evidence_by_capability_id) is not dict
            or type(state.terminal_receipt_ids) is not set
            or type(state.terminal_receipt_id_by_capability_id) is not dict
            or type(state.mock_effect_execution_count) is not int
            or state.mock_effect_execution_count < 0
        ):
            return False
        if (not state.started_capability_ids <= set(state.issued_capabilities)
            or not set(state.native_evidence_by_capability_id) <= state.started_capability_ids
            or any(validate_native_execution_evidence_v01(evidence)
                for evidence in state.native_evidence_by_capability_id.values())):
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
    return _build_decision_values_v01(
        firewall_id=firewall.firewall_id,
        invocation_id=firewall.invocation_id,
        request=request,
        tick=tick,
        decision=decision,
        reason=reason,
        capability_id=capability_id,
        capability_issued=capability_issued,
        return_to_root=return_to_root,
    )


def _build_decision_values_v01(
    *,
    firewall_id: str,
    invocation_id: str,
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
        firewall_id=firewall_id,
        invocation_id=invocation_id,
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


# Native capability definitions are inert during module initialization. Nominal action value
# access occurs only after both modules have completed initialization.
@_dataclass(frozen=True)
class CapabilityFieldV01:
    name: str
    value_type: str
    required: bool
    consequential: bool
    minimum: int | str | None
    maximum: int | str | None
    allowed_values: tuple[str | int | bool, ...]


@_dataclass(frozen=True)
class CapabilityBusinessInputBindingV01:
    input_name: str
    source_kind: str
    source_name: str
    value_type: str


@_dataclass(frozen=True)
class CapabilityBusinessSemanticsV01:
    operation_key: str
    selected_action_class: str
    logical_effect_class: str
    logical_effect_namespace: str
    business_object_class: str
    business_object_namespace: str
    input_bindings: tuple[CapabilityBusinessInputBindingV01, ...]


@_dataclass(frozen=True)
class CapabilityDefinitionV01:
    definition_id: str
    operation_id: str
    version: str
    effect_kind: str
    business_semantics: CapabilityBusinessSemanticsV01 | None
    input_fields: tuple[CapabilityFieldV01, ...]
    output_fields: tuple[CapabilityFieldV01, ...]
    resource_refs: tuple[str, ...]
    input_validator_ref: str
    output_validator_ref: str
    executor_ref: str
    code_sha256s: tuple[tuple[str, str], ...]
    contract_sha256: str


@_dataclass(frozen=True)
class CapabilityCodeSnapshotV01:
    public_symbol: str
    source_utf8: str
    source_sha256: str


@_dataclass(frozen=True)
class CapabilityAdmissionSnapshotV01:
    admission_id: str
    definition: CapabilityDefinitionV01
    code_sources: tuple[CapabilityCodeSnapshotV01, ...]
    input_contract_ref: str
    output_contract_ref: str
    implementation_ref: str
    catalogue_revision: int
    host_instance_ref: str


@_dataclass(frozen=True)
class AdmittedCapabilityV01:
    definition: CapabilityDefinitionV01
    input_validator: object
    output_validator: object
    executor: object
    observed_code_identities: tuple[CapabilityCodeSnapshotV01, ...]
    admission_id: str
    catalogue_revision: int
    host_instance_ref: str
    _origin: object = _field(default=None, repr=False, compare=False)


class _CapabilityAdmissionOriginV01:
    """Per-admission provenance, populated only by trusted host setup."""
    __slots__ = ('admitted', 'callables', 'codes', 'owner', 'start_observer')

    def __init__(self, callables):
        self.admitted = None
        self.callables = callables
        self.codes = tuple(c.__code__ for c in callables)
        self.owner = None
        self.start_observer = None


@_dataclass(frozen=True)
class CapabilityValidationEvidenceV01:
    definition_id: str
    validator_code_sha256: str
    subject_sha256: str
    invocation_id: str | None
    valid: bool
    reason_codes: tuple[str, ...]


@_dataclass(frozen=True)
class BoundCapabilityInvocationV01:
    invocation_id: str
    admission_id: str
    definition_id: str
    task_id: str
    work_instance_id: str
    owning_root_id: str
    candidate_id: str | None
    packet_id: str | None
    execution_attempt_id: str
    inputs: tuple[object, ...]
    resource_refs: tuple[str, ...]
    input_validation: CapabilityValidationEvidenceV01


@_dataclass(frozen=True)
class CapabilityExecutionResultV01:
    result_id: str
    invocation_id: str
    execution_attempt_id: str
    admission_id: str
    consumed_input_sha256: str
    actual_implementation_sha256: str
    output: tuple[object, ...]
    output_validation: CapabilityValidationEvidenceV01
    outcome: str


@_dataclass(frozen=True)
class NativeExecutionEvidenceV01:
    admission: CapabilityAdmissionSnapshotV01
    invocation: BoundCapabilityInvocationV01
    result: CapabilityExecutionResultV01


_NATIVE_TYPES = (CapabilityFieldV01, CapabilityBusinessInputBindingV01,
    CapabilityBusinessSemanticsV01, CapabilityDefinitionV01,
    CapabilityCodeSnapshotV01, CapabilityAdmissionSnapshotV01,
    CapabilityValidationEvidenceV01, BoundCapabilityInvocationV01,
    CapabilityExecutionResultV01, NativeExecutionEvidenceV01)
_NATIVE_CONTROL_NAMES = ('capability_definition_ref', 'capability_implementation_ref',
    'capability_input_contract_ref', 'capability_output_contract_ref')
_NATIVE_RECEIPT_PROFILE = 'common_action.execution_result.v01'
_NATIVE_RECEIPT_KEYS = tuple(sorted((*_RECEIPT_PAYLOAD_KEYS, 'receipt_profile', 'execution_evidence')))


def _native_require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError(reason)


def _native_value(value: object) -> object:
    from hedgehog import action_commit_packet_v02 as action
    if value is None:
        return action.ABSENT_V01
    if type(value) in (str, int, bool):
        return value
    if type(value) is action.ActionEffectParameterRecordV01:
        _native_require(action.validate_action_effect_parameter_record_v01(value)[0], 'capability_record_invalid')
        return action.action_effect_parameter_record_material_v01(value)
    if type(value) in _NATIVE_TYPES:
        return tuple((f.name, _native_value(getattr(value, f.name))) for f in _fields(value))
    if type(value) is tuple:
        return tuple(_native_value(v) for v in value)
    raise ValueError('capability_material_type_invalid')


def _native_material(value: object, excluded: tuple[str, ...] = ()) -> tuple:
    return tuple((f.name, _native_value(getattr(value, f.name)))
                 for f in _fields(value) if f.name not in excluded)


def _native_identity(leaf: str, material: tuple, prefix: str | None = None) -> str:
    from hedgehog import action_commit_packet_v02 as action
    if prefix == '':
        return action.domain_separated_sha256_hex_v01(domain='hedgehog.common_action.'+leaf+'.v01',
            payload=action.canonical_material_bytes_v01(material))
    return action.build_domain_separated_identity_v01(domain='hedgehog.common_action.'+leaf+'.v01',
        prefix=leaf+':' if prefix is None else prefix, material=material)


def capability_value_subject_sha256_v01(values: object) -> str:
    from hedgehog import action_commit_packet_v02 as action
    _native_require(type(values) is tuple, 'capability_values_type')
    for value in values:
        _native_require(type(value) is action.ActionEffectParameterRecordV01 and
            action.validate_action_effect_parameter_record_v01(value)[0], 'capability_record_invalid')
    return _native_identity('capability_value_subject', (('records', _native_value(values)),), '')


def _capability_scalar_valid(kind: str, value: object) -> bool:
    from hedgehog import action_commit_packet_v02 as action
    if kind in ('TEXT', 'REFERENCE'):
        return type(value) is str and action.validate_identity_text_v01(value)[0]
    if kind == 'DECIMAL':
        return type(value) is str and action.validate_canonical_decimal_v01(value)[0]
    if kind == 'INTEGER':
        return type(value) is int and action.validate_signed_int64_v01(value)[0]
    return kind == 'BOOLEAN' and type(value) is bool


def validate_capability_field_v01(value: object) -> tuple[str, ...]:
    try:
        _native_require(type(value) is CapabilityFieldV01 and _valid_text(value.name), 'capability_field_type')
        _native_require(value.name not in _NATIVE_CONTROL_NAMES, 'capability_reserved_field')
        _native_require(value.value_type in ('TEXT', 'REFERENCE', 'DECIMAL', 'INTEGER', 'BOOLEAN') and
            type(value.required) is type(value.consequential) is bool, 'capability_field_declaration')
        _native_require(type(value.allowed_values) is tuple and len({(type(v), v) for v in value.allowed_values})==len(value.allowed_values), 'capability_allowed_values')
        _native_require(all(_capability_scalar_valid(value.value_type, v) for v in value.allowed_values), 'capability_allowed_value_type')
        for bound in (value.minimum, value.maximum):
            _native_require(bound is None or value.value_type in ('DECIMAL', 'INTEGER') and _capability_scalar_valid(value.value_type, bound), 'capability_field_range_type')
        if value.minimum is not None and value.maximum is not None:
            from decimal import Decimal
            _native_require(Decimal(value.minimum)<=Decimal(value.maximum), 'capability_field_range')
        return ()
    except (ValueError, TypeError, AttributeError) as exc:
        return (str(exc) if type(exc) is ValueError else 'capability_field_invalid',)


def build_capability_field_v01(*, name: str, value_type: str, required: bool,
    consequential: bool, minimum: object = None, maximum: object = None,
    allowed_values: tuple = ()) -> CapabilityFieldV01:
    value=CapabilityFieldV01(name,value_type,required,consequential,minimum,maximum,allowed_values)
    errors=validate_capability_field_v01(value)
    if errors:raise ValueError(errors[0])
    return value


def _capability_fields_valid(values: object) -> bool:
    return (type(values) is tuple and all(not validate_capability_field_v01(v) for v in values)
        and tuple(v.name for v in values)==tuple(sorted({v.name for v in values})))


def validate_capability_values_v01(fields: object, values: object) -> tuple[str, ...]:
    from hedgehog import action_commit_packet_v02 as action
    try:
        _native_require(_capability_fields_valid(fields) and type(values) is tuple, 'capability_value_shape')
        _native_require(all(type(v) is action.ActionEffectParameterRecordV01 and action.validate_action_effect_parameter_record_v01(v)[0] for v in values), 'capability_record_invalid')
        names=tuple(v.parameter_name for v in values)
        _native_require(names==tuple(sorted(set(names))) and set(names)<=set(f.name for f in fields), 'capability_value_names')
        actual={v.parameter_name:v for v in values}
        for f in fields:
            _native_require(not f.required or f.name in actual,'capability_value_missing:'+f.name)
            if f.name not in actual:continue
            v=actual[f.name]
            _native_require(v.value_type==f.value_type and _capability_scalar_valid(f.value_type,v.value),'capability_value_type:'+f.name)
            _native_require(not f.allowed_values or (type(v.value),v.value) in {(type(x),x) for x in f.allowed_values},'capability_value_not_allowed:'+f.name)
            from decimal import Decimal
            _native_require(f.minimum is None or Decimal(v.value)>=Decimal(f.minimum),'capability_value_below_minimum:'+f.name)
            _native_require(f.maximum is None or Decimal(v.value)<=Decimal(f.maximum),'capability_value_above_maximum:'+f.name)
        return ()
    except (ValueError, TypeError, AttributeError) as exc:
        return (str(exc) if type(exc) is ValueError else 'capability_values_invalid',)


def build_capability_business_input_binding_v01(*, input_name: str, source_kind: str,
    source_name: str, value_type: str) -> CapabilityBusinessInputBindingV01:
    value=CapabilityBusinessInputBindingV01(input_name,source_kind,source_name,value_type)
    _native_require(all(_valid_text(x) for x in (input_name,source_kind,source_name,value_type)), 'capability_business_binding_text')
    _native_require(input_name not in _NATIVE_CONTROL_NAMES and source_name not in _NATIVE_CONTROL_NAMES, 'capability_reserved_field')
    scalars={'AMOUNT':('amount_decimal','DECIMAL'),'CURRENCY':('currency_code','TEXT'),
             'QUANTITY':('quantity_decimal','DECIMAL'),'BUSINESS_OBJECT_REF':('business_object_ref','REFERENCE')}
    _native_require(source_kind in (*scalars,'RECORD','SUBJECT_RECORD','TARGET_RECORD'), 'capability_business_source_kind')
    _native_require(source_kind not in scalars or (source_name,value_type)==scalars[source_kind], 'capability_business_scalar_selector')
    _native_require(source_kind not in ('SUBJECT_RECORD','TARGET_RECORD') or value_type=='REFERENCE', 'capability_business_scope_type')
    return value


def build_capability_business_semantics_v01(*, operation_key: str, selected_action_class: str,
    logical_effect_class: str, logical_effect_namespace: str, business_object_class: str,
    business_object_namespace: str, input_bindings: tuple) -> CapabilityBusinessSemanticsV01:
    _native_require(all(_valid_text(x) for x in (operation_key,selected_action_class,logical_effect_class,logical_effect_namespace,business_object_class,business_object_namespace)), 'capability_business_text')
    _native_require(operation_key==logical_effect_namespace and selected_action_class.startswith(MOCK_ACTION_PREFIX), 'capability_business_operation')
    _native_require(type(input_bindings) is tuple and all(type(v) is CapabilityBusinessInputBindingV01 for v in input_bindings), 'capability_business_bindings_type')
    for value in input_bindings:
        _native_require(build_capability_business_input_binding_v01(**{f.name:getattr(value,f.name) for f in _fields(value)})==value, 'capability_business_binding')
    bindings=tuple(sorted(input_bindings,key=lambda v:v.input_name))
    _native_require(len({v.input_name for v in bindings})==len(bindings), 'capability_business_binding_duplicate')
    return CapabilityBusinessSemanticsV01(operation_key,selected_action_class,logical_effect_class,logical_effect_namespace,business_object_class,business_object_namespace,bindings)


def _capability_contract_refs(definition: CapabilityDefinitionV01) -> tuple[str, str]:
    codes=dict(definition.code_sha256s)
    return (_native_identity('capability_input_contract',(('input_fields',_native_value(definition.input_fields)),
        ('business_semantics',_native_value(definition.business_semantics)),('input_validator_ref',definition.input_validator_ref),
        ('input_validator_code_sha256',codes[definition.input_validator_ref]))),
        _native_identity('capability_output_contract',(('output_fields',_native_value(definition.output_fields)),
        ('output_validator_ref',definition.output_validator_ref),('output_validator_code_sha256',codes[definition.output_validator_ref]))))


def validate_capability_definition_v01(value: object) -> tuple[str, ...]:
    try:
        _native_require(type(value) is CapabilityDefinitionV01, 'capability_definition_type')
        _native_require(all(_valid_text(getattr(value,n)) for n in ('definition_id','operation_id','version','input_validator_ref','output_validator_ref','executor_ref')), 'capability_definition_text')
        _native_require(value.effect_kind in ('PURE','MOCK_CONSEQUENTIAL'), 'capability_effect_kind')
        _native_require(_capability_fields_valid(value.input_fields) and _capability_fields_valid(value.output_fields), 'capability_definition_fields')
        _native_require(_valid_text_tuple(value.resource_refs,allow_empty=True) and value.resource_refs==tuple(sorted(value.resource_refs)), 'capability_resources')
        if value.effect_kind=='PURE':
            _native_require(value.business_semantics is None and not any(f.consequential for f in value.input_fields), 'capability_pure_semantics')
        else:
            semantics=value.business_semantics
            _native_require(type(semantics) is CapabilityBusinessSemanticsV01, 'capability_business_type')
            _native_require(build_capability_business_semantics_v01(**{f.name:getattr(semantics,f.name) for f in _fields(semantics)})==semantics, 'capability_business_semantics')
            _native_require(value.operation_id==semantics.operation_key and tuple(v.input_name for v in semantics.input_bindings)==tuple(f.name for f in value.input_fields)
                and all(f.required and f.consequential and f.value_type==b.value_type for f,b in zip(value.input_fields,semantics.input_bindings)), 'capability_business_exhaustive_mapping')
        _native_require(type(value.code_sha256s) is tuple and all(type(p) is tuple and len(p)==2 and _valid_text(p[0]) and _valid_sha256(p[1]) for p in value.code_sha256s), 'capability_code_hashes')
        _native_require(tuple(p[0] for p in value.code_sha256s)==tuple(sorted({value.input_validator_ref,value.output_validator_ref,value.executor_ref})) and len(value.code_sha256s)==3,'capability_code_symbols')
        i,o=_capability_contract_refs(value)
        _native_require(value.contract_sha256==_native_identity('capability_contract',(('input_contract_ref',i),('output_contract_ref',o)),''), 'capability_contract_hash')
        _native_require(value.definition_id==_native_identity('capability_definition',_native_material(value,('definition_id',))), 'capability_definition_identity')
        return ()
    except (ValueError, KeyError, TypeError, AttributeError) as exc:
        return (str(exc) if type(exc) is ValueError else 'capability_definition_invalid',)


def build_capability_definition_v01(*, operation_id: str, version: str, effect_kind: str,
    business_semantics: object, input_fields: tuple, output_fields: tuple, resource_refs: tuple,
    input_validator_ref: str, output_validator_ref: str, executor_ref: str,
    code_sha256s: tuple) -> CapabilityDefinitionV01:
    value=CapabilityDefinitionV01('',operation_id,version,effect_kind,business_semantics,
        tuple(sorted(input_fields,key=lambda v:v.name)),tuple(sorted(output_fields,key=lambda v:v.name)),
        tuple(sorted(resource_refs)),input_validator_ref,output_validator_ref,executor_ref,tuple(sorted(code_sha256s)),'')
    i,o=_capability_contract_refs(value)
    value=_replace(value,contract_sha256=_native_identity('capability_contract',(('input_contract_ref',i),('output_contract_ref',o)),''))
    value=_replace(value,definition_id=_native_identity('capability_definition',_native_material(value,('definition_id',))))
    errors=validate_capability_definition_v01(value)
    if errors:raise ValueError(errors[0])
    return value


def _admission_snapshot(value: AdmittedCapabilityV01) -> CapabilityAdmissionSnapshotV01:
    i,o=_capability_contract_refs(value.definition)
    implementation=_native_identity('capability_implementation',(('code_sources',_native_value(value.observed_code_identities)),))
    return CapabilityAdmissionSnapshotV01(value.admission_id,value.definition,value.observed_code_identities,i,o,implementation,value.catalogue_revision,value.host_instance_ref)


def validate_capability_admission_snapshot_v01(value: object) -> tuple[str, ...]:
    import hashlib
    try:
        _native_require(type(value) is CapabilityAdmissionSnapshotV01,'capability_snapshot_type')
        errors=validate_capability_definition_v01(value.definition)
        if errors:raise ValueError(errors[0])
        _native_require(type(value.catalogue_revision) is int and value.catalogue_revision>=0 and _valid_text(value.host_instance_ref),'capability_snapshot_host_revision')
        _native_require(type(value.code_sources) is tuple and all(type(v) is CapabilityCodeSnapshotV01 for v in value.code_sources),'capability_source_type')
        _native_require(tuple((s.public_symbol,s.source_sha256) for s in value.code_sources)==value.definition.code_sha256s,'capability_snapshot_sources')
        _native_require(all(type(s.source_utf8) is str and hashlib.sha256(s.source_utf8.encode()).hexdigest()==s.source_sha256 for s in value.code_sources),'capability_source_hash')
        i,o=_capability_contract_refs(value.definition)
        _native_require((value.input_contract_ref,value.output_contract_ref)==(i,o),'capability_snapshot_contracts')
        _native_require(value.implementation_ref==_native_identity('capability_implementation',(('code_sources',_native_value(value.code_sources)),)),'capability_implementation_identity')
        _native_require(value.admission_id==_native_identity('capability_admission',_native_material(value,('admission_id',))),'capability_admission_identity')
        return ()
    except (ValueError, TypeError, AttributeError) as exc:
        return (str(exc) if type(exc) is ValueError else 'capability_snapshot_invalid',)


def _admit_observed_capability_v01(*, definition: CapabilityDefinitionV01, input_validator: object,
    output_validator: object, executor: object, catalogue_revision: int, host_instance_ref: str,
    sources: tuple) -> AdmittedCapabilityV01:
    errors=validate_capability_definition_v01(definition)
    if errors:raise ValueError(errors[0])
    callables=(input_validator,output_validator,executor)
    _native_require(tuple(s.public_symbol for s in sources)==(definition.input_validator_ref,definition.output_validator_ref,definition.executor_ref),'capability_callable_roles')
    sources=tuple(sorted(sources,key=lambda v:v.public_symbol))
    origin = _CapabilityAdmissionOriginV01(callables)
    value=AdmittedCapabilityV01(definition,input_validator,output_validator,executor,sources,'',catalogue_revision,host_instance_ref,origin)
    snapshot=_admission_snapshot(value)
    value=_replace(value,admission_id=_native_identity('capability_admission',_native_material(snapshot,('admission_id',))))
    errors=validate_capability_admission_snapshot_v01(_admission_snapshot(value))
    if errors:raise ValueError(errors[0])
    origin.admitted = value
    return value


def validate_admitted_capability_v01(value: object) -> tuple[str, ...]:
    try:
        _native_require(type(value) is AdmittedCapabilityV01,'capability_admitted_type')
        origin=value._origin
        _native_require(type(origin) is _CapabilityAdmissionOriginV01 and origin.admitted is value,'capability_not_trusted_admission')
        callables=(value.input_validator,value.output_validator,value.executor)
        _native_require(all(v is original for v,original in zip(callables,origin.callables)), 'capability_callable_changed')
        _native_require(all(v.__code__ is code for v,code in zip(callables,origin.codes)),'capability_loaded_code_changed')
        return validate_capability_admission_snapshot_v01(_admission_snapshot(value))
    except (ValueError, TypeError, AttributeError) as exc:
        return (str(exc) if type(exc) is ValueError else 'capability_admitted_invalid',)


def snapshot_admitted_capability_v01(admitted_capability: object) -> CapabilityAdmissionSnapshotV01:
    errors=validate_admitted_capability_v01(admitted_capability)
    if errors:raise ValueError(errors[0])
    return _admission_snapshot(admitted_capability)


def validate_capability_business_binding_v01(definition: object, inputs: object,
    canonical_projection: object) -> tuple[str, ...]:
    from hedgehog import action_commit_packet_v02 as action
    try:
        errors=validate_capability_definition_v01(definition)
        if errors:raise ValueError(errors[0])
        errors=validate_capability_values_v01(definition.input_fields,inputs)
        if errors:raise ValueError(errors[0])
        c=canonical_projection;s=definition.business_semantics
        _native_require(type(c) is action.NativeActionCommitPacketV01 and type(s) is CapabilityBusinessSemanticsV01,'capability_business_context_type')
        _native_require((c.selected_canonical_action,c.logical_intent.logical_effect_class,c.authority_policy.logical_effect_namespace,
            c.business_object_identity.business_object_class,c.business_object_identity.business_object_namespace)==
            (s.selected_action_class,s.logical_effect_class,s.logical_effect_namespace,s.business_object_class,s.business_object_namespace),'capability_business_operation_binding')
        _native_require(definition.resource_refs==c.normalized_target_scope.included_target_refs,'capability_target_binding')
        q=c.consequential_effect_parameters;records={v.parameter_name:v for v in q.parameter_records};actual={v.parameter_name:v for v in inputs}
        _native_require(not set(records).intersection(_NATIVE_CONTROL_NAMES),'capability_reserved_business_record')
        for binding in s.input_bindings:
            if binding.source_kind in ('AMOUNT','CURRENCY','QUANTITY'):value=getattr(q,binding.source_name)
            elif binding.source_kind=='BUSINESS_OBJECT_REF':value=c.business_object_identity.business_object_ref
            else:
                _native_require(binding.source_name in records,'capability_business_record_missing')
                record=records[binding.source_name];_native_require(record.value_type==binding.value_type,'capability_business_record_type');value=record.value
                if binding.source_kind=='SUBJECT_RECORD':_native_require(value in c.normalized_subject_scope.included_subject_refs and value not in c.normalized_subject_scope.excluded_subject_refs,'capability_subject_binding')
                if binding.source_kind=='TARGET_RECORD':_native_require(value in c.normalized_target_scope.included_target_refs and value not in c.normalized_target_scope.excluded_target_refs,'capability_target_binding')
            supplied=actual[binding.input_name]
            _native_require(type(supplied.value) is type(value) and supplied.value==value and supplied.value_type==binding.value_type,'capability_business_input_binding:'+binding.input_name)
        return ()
    except (ValueError, KeyError, TypeError, AttributeError) as exc:
        return (str(exc) if type(exc) is ValueError else 'capability_business_binding_invalid',)


def build_capability_validation_evidence_v01(*, definition: CapabilityDefinitionV01,
    values: tuple, invocation_id: str | None, valid: bool,
    reason_codes: tuple[str, ...]) -> CapabilityValidationEvidenceV01:
    role=definition.input_validator_ref if invocation_id is None else definition.output_validator_ref
    _native_require(type(valid) is bool and _valid_text_tuple(reason_codes,allow_empty=True) and valid==(not reason_codes),'capability_validation_truth_shape')
    return CapabilityValidationEvidenceV01(definition.definition_id,dict(definition.code_sha256s)[role],
        capability_value_subject_sha256_v01(values),invocation_id,valid,reason_codes)


def _capability_evidence_errors(evidence: object, definition: CapabilityDefinitionV01,
    values: tuple, invocation_id: str | None) -> tuple[str, ...]:
    _native_require(type(evidence) is CapabilityValidationEvidenceV01,'capability_validation_evidence_type')
    expected=build_capability_validation_evidence_v01(definition=definition,values=values,invocation_id=invocation_id,
        valid=evidence.valid,reason_codes=evidence.reason_codes)
    _native_require(evidence==expected,'capability_validation_evidence_binding')
    return evidence.reason_codes if not evidence.valid else ()


def validate_bound_capability_invocation_v01(value: object, admission_snapshot: object,
    canonical_projection: object = None) -> tuple[str, ...]:
    try:
        _native_require(type(value) is BoundCapabilityInvocationV01,'capability_invocation_type')
        errors=validate_capability_admission_snapshot_v01(admission_snapshot)
        if errors:raise ValueError(errors[0])
        d=admission_snapshot.definition
        _native_require((value.admission_id,value.definition_id,value.resource_refs)==(admission_snapshot.admission_id,d.definition_id,d.resource_refs),'capability_invocation_admission')
        _native_require(all(_valid_text(getattr(value,n)) for n in ('invocation_id','task_id','work_instance_id','owning_root_id','execution_attempt_id')),'capability_invocation_text')
        _native_require((value.candidate_id is None and value.packet_id is None) if d.effect_kind=='PURE' else (_valid_text(value.candidate_id) and _valid_text(value.packet_id)),'capability_invocation_effect_context')
        errors=validate_capability_values_v01(d.input_fields,value.inputs)
        if errors:raise ValueError(errors[0])
        errors=_capability_evidence_errors(value.input_validation,d,value.inputs,None)
        if errors:raise ValueError('capability_input_validation_failed:'+errors[0])
        _native_require(value.invocation_id==_native_identity('capability_invocation',_native_material(value,('invocation_id',))),'capability_invocation_identity')
        if canonical_projection is not None:
            errors=validate_capability_business_binding_v01(d,value.inputs,canonical_projection)
            if errors:raise ValueError(errors[0])
            _native_require(value.candidate_id==canonical_projection.authorization_candidate.root_packet_authorization_candidate_id and
                value.owning_root_id==canonical_projection.owning_local_root_id and admission_snapshot==canonical_projection.execution_source,'capability_invocation_candidate_binding')
        return ()
    except (ValueError, TypeError, AttributeError) as exc:
        return (str(exc) if type(exc) is ValueError else 'capability_invocation_invalid',)


def build_bound_capability_invocation_v01(*, admitted_capability: object, task_id: str,
    work_instance_id: str, owning_root_id: str, candidate_id: str | None, packet_id: str | None,
    execution_attempt_id: str, inputs: tuple, resource_refs: tuple,
    canonical_projection: object = None) -> BoundCapabilityInvocationV01:
    snapshot=snapshot_admitted_capability_v01(admitted_capability);d=snapshot.definition
    errors=validate_capability_values_v01(d.input_fields,inputs)
    if errors:raise ValueError(errors[0])
    if d.effect_kind=='MOCK_CONSEQUENTIAL':
        errors=validate_capability_business_binding_v01(d,inputs,canonical_projection)
        if errors:raise ValueError(errors[0])
    evidence=admitted_capability.input_validator(d,inputs)
    errors=_capability_evidence_errors(evidence,d,inputs,None)
    if errors:raise ValueError('capability_input_validation_failed:'+errors[0])
    value=BoundCapabilityInvocationV01('',snapshot.admission_id,d.definition_id,task_id,work_instance_id,owning_root_id,candidate_id,packet_id,execution_attempt_id,inputs,resource_refs,evidence)
    value=_replace(value,invocation_id=_native_identity('capability_invocation',_native_material(value,('invocation_id',))))
    errors=validate_bound_capability_invocation_v01(value,snapshot,canonical_projection)
    if errors:raise ValueError(errors[0])
    return value


def validate_capability_execution_result_v01(value: object, invocation: object,
    admission_snapshot: object) -> tuple[str, ...]:
    try:
        errors=validate_bound_capability_invocation_v01(invocation,admission_snapshot)
        if errors:raise ValueError(errors[0])
        _native_require(type(value) is CapabilityExecutionResultV01,'capability_result_type')
        d=admission_snapshot.definition
        _native_require((value.invocation_id,value.execution_attempt_id,value.admission_id)==(invocation.invocation_id,invocation.execution_attempt_id,invocation.admission_id),'capability_result_invocation_binding')
        _native_require(value.consumed_input_sha256==capability_value_subject_sha256_v01(invocation.inputs) and
            value.actual_implementation_sha256==dict(d.code_sha256s)[d.executor_ref],'capability_result_input_code_binding')
        _native_require(value.outcome in ('SUCCEEDED','FAILED_NON_CONSUMING','UNCERTAIN_CLOSED'),'capability_result_outcome')
        errors=validate_capability_values_v01(d.output_fields,value.output)
        if errors:raise ValueError(errors[0])
        errors=_capability_evidence_errors(value.output_validation,d,value.output,invocation.invocation_id)
        _native_require(value.outcome!='SUCCEEDED' or not errors,'capability_output_validation_failed')
        _native_require(value.result_id==_native_identity('capability_result',_native_material(value,('result_id',))),'capability_result_identity')
        return ()
    except (ValueError, TypeError, AttributeError) as exc:
        return (str(exc) if type(exc) is ValueError else 'capability_result_invalid',)


def build_capability_execution_result_v01(*, invocation, admission_snapshot, output, output_validation):
    """Content-bound evidence; construction alone is not observed execution."""
    definition = admission_snapshot.definition
    result = CapabilityExecutionResultV01('', invocation.invocation_id, invocation.execution_attempt_id,
        invocation.admission_id, capability_value_subject_sha256_v01(invocation.inputs),
        dict(definition.code_sha256s)[definition.executor_ref], output, output_validation, 'SUCCEEDED')
    result = _replace(result, result_id=_native_identity('capability_result', _native_material(result, ('result_id',))))
    errors = validate_capability_execution_result_v01(result, invocation, admission_snapshot)
    if errors:
        raise ValueError(errors[0])
    return result


def native_execution_evidence_to_plain_data_v01(value: object) -> dict[str, object]:
    errors=validate_native_execution_evidence_v01(value)
    if errors:raise ValueError(errors[0])
    return _native_plain(value)


def _native_plain(value: object) -> object:
    from hedgehog import action_commit_packet_v02 as action
    if value is None or type(value) in (str,int,bool):return value
    if type(value) in (*_NATIVE_TYPES,action.ActionEffectParameterRecordV01):
        return {f.name:_native_plain(getattr(value,f.name)) for f in _fields(value)}
    if type(value) is tuple:return [_native_plain(v) for v in value]
    raise ValueError('native_plain_type')


def _native_read(cls: type, plain: object) -> object:
    from hedgehog import action_commit_packet_v02 as action
    _native_require(type(plain) is dict and set(plain)=={f.name for f in _fields(cls)},'native_plain_exact_fields:'+cls.__name__)
    nested={CapabilityBusinessSemanticsV01:{'input_bindings':(CapabilityBusinessInputBindingV01,)},
        CapabilityDefinitionV01:{'business_semantics':CapabilityBusinessSemanticsV01,'input_fields':(CapabilityFieldV01,), 'output_fields':(CapabilityFieldV01,)},
        CapabilityAdmissionSnapshotV01:{'definition':CapabilityDefinitionV01,'code_sources':(CapabilityCodeSnapshotV01,)},
        BoundCapabilityInvocationV01:{'inputs':(action.ActionEffectParameterRecordV01,), 'input_validation':CapabilityValidationEvidenceV01},
        CapabilityExecutionResultV01:{'output':(action.ActionEffectParameterRecordV01,), 'output_validation':CapabilityValidationEvidenceV01},
        NativeExecutionEvidenceV01:{'admission':CapabilityAdmissionSnapshotV01,'invocation':BoundCapabilityInvocationV01,'result':CapabilityExecutionResultV01}}
    tuple_names={'allowed_values','resource_refs','reason_codes','code_sha256s'}
    values={}
    for name,item in plain.items():
        kind=nested.get(cls,{}).get(name)
        if kind is not None:
            if type(kind) is tuple:
                _native_require(type(item) is list,'native_plain_tuple:'+name);item=tuple(_native_read(kind[0],v) for v in item)
            elif item is not None:item=_native_read(kind,item)
        elif name in tuple_names:
            _native_require(type(item) is list,'native_plain_tuple:'+name)
            if name=='code_sha256s':
                _native_require(all(type(p) is list and len(p)==2 for p in item),'native_plain_code_pairs');item=tuple(tuple(p) for p in item)
            else:item=tuple(item)
        values[name]=item
    return cls(**values)


def native_execution_evidence_from_plain_data_v01(plain: object) -> NativeExecutionEvidenceV01:
    value=_native_read(NativeExecutionEvidenceV01,plain)
    errors=validate_native_execution_evidence_v01(value)
    if errors:raise ValueError(errors[0])
    return value


def validate_native_execution_evidence_v01(value: object) -> tuple[str, ...]:
    if type(value) is not NativeExecutionEvidenceV01:return ('native_execution_evidence_type',)
    errors=validate_capability_execution_result_v01(value.result,value.invocation,value.admission)
    if errors:return errors
    if value.admission.definition.effect_kind!='MOCK_CONSEQUENTIAL' or value.result.outcome!='SUCCEEDED':return ('native_success_evidence_required',)
    return ()


def _native_receipt_material_value_v01(value):
    from hedgehog import action_commit_packet_v02 as action
    if value is None:
        return action.ABSENT_V01
    if type(value) in (str, int, bool):
        return value
    if type(value) is list:
        return tuple(_native_receipt_material_value_v01(v) for v in value)
    if type(value) is dict:
        return tuple((k, _native_receipt_material_value_v01(value[k])) for k in sorted(value))
    raise ValueError('native_receipt_material_type')


def _native_receipt_identity_v01(plain):
    payload = tuple((k, _native_receipt_material_value_v01(plain['payload'][k]))
        for k in sorted(plain['payload']) if k != 'receipt_ref')
    envelope = tuple((k, _native_receipt_material_value_v01(plain[k])) for k in (
        'abi_version', 'artifact_type', 'schema_version', 'transaction_id', 'owner_root_id',
        'source_component', 'authority_class', 'lifecycle_state', 'trace_refs', 'parent_refs', 'time_envelope'))
    return _native_identity('native_effect_receipt', (('payload', payload), ('envelope', envelope)), 'effect_receipt_v01:')


def _native_effect_receipt_binding_errors_v01(receipt, request, decision):
    try:
        plain = _kernel_artifact_to_plain_dict_v01(receipt)
        payload = plain['payload']
        _native_require(tuple(sorted(payload)) == _NATIVE_RECEIPT_KEYS and
            payload['receipt_profile'] == _NATIVE_RECEIPT_PROFILE, 'native_receipt_profile')
        evidence = native_execution_evidence_from_plain_data_v01(payload['execution_evidence'])
        invocation = evidence.invocation
        semantics = evidence.admission.definition.business_semantics
        _native_require((invocation.owning_root_id, invocation.candidate_id,
            semantics.selected_action_class) == (request.target_root_id, request.selected_candidate_id,
            request.action_kind), 'native_receipt_invocation_root_candidate_action')
        _native_require(set(invocation.resource_refs) <= set(payload['scope_refs']), 'native_receipt_resource_binding')
        _native_require(plain['artifact_id'] == payload['receipt_ref'] == _native_receipt_identity_v01(plain),
            'native_receipt_identity')
        return ()
    except (ValueError, KeyError, TypeError, AttributeError) as exc:
        return (str(exc) if type(exc) is ValueError else 'native_receipt_invalid',)


def build_native_effect_receipt_v01(*, firewall, request, decision, time_envelope, execution_evidence):
    _native_require(not _firewall_errors(firewall) and not validate_effect_firewall_decision_v01(
        firewall=firewall, request=request, decision=decision), 'native_receipt_authorization')
    capability = firewall._state.issued_capabilities.get(decision.capability_id)
    _native_require(capability is not None and capability.capability_id in firewall._state.started_capability_ids
        and firewall._state.native_evidence_by_capability_id.get(capability.capability_id) is execution_evidence,
        'native_receipt_requires_observed_completion')
    payload = dict(receipt_ref='effect_receipt_v01:pending', request_id=request.request_id,
        firewall_decision_id=decision.decision_id, capability_id=capability.capability_id,
        root_decision_id=request.root_decision_id, selected_candidate_id=request.selected_candidate_id,
        permission_ref=request.permission_ref, adapter_id=request.adapter_id, action_kind=request.action_kind,
        scope_refs=list(request.scope_refs), mock_execution_status=STATUS_PASS, receipt_evidence_only=True,
        root_confirmation_required=True, root_confirmation_created=False, future_permission_created=False,
        root_decision_created=False, final_output_created=False, effect_handle_exposed=False, real_world_effects_count=0,
        receipt_profile=_NATIVE_RECEIPT_PROFILE,
        execution_evidence=native_execution_evidence_to_plain_data_v01(execution_evidence))
    kwargs = dict(abi_version='v1.0', artifact_id=payload['receipt_ref'], artifact_type='EvidenceReceipt',
        schema_version='v1', transaction_id=request.transaction_id, owner_root_id=request.target_root_id,
        source_component=RECEIPT_SOURCE_COMPONENT, authority_class='EVIDENCE_ONLY', lifecycle_state='RECEIPT_RECORDED',
        payload=payload, trace_refs=(request.request_id, request.root_decision_id, decision.decision_id),
        parent_refs=(request.root_decision_id,), time_envelope=time_envelope)
    provisional = _build_kernel_artifact_v01(**kwargs)
    identifier = _native_receipt_identity_v01(_kernel_artifact_to_plain_dict_v01(provisional))
    payload['receipt_ref'] = identifier
    kwargs['artifact_id'] = identifier
    receipt = _build_kernel_artifact_v01(**kwargs)
    errors = _effect_receipt_errors(firewall=firewall, request=request, decision=decision,
        receipt=receipt, require_execution_state=False)
    if errors:
        raise ValueError(errors[0])
    return receipt


def validate_native_effect_receipt_v01(*, firewall, request, decision, receipt):
    errors = _native_effect_receipt_binding_errors_v01(receipt, request, decision)
    return errors or validate_effect_receipt_v01(firewall=firewall, request=request,
        decision=decision, receipt=receipt)


def validate_retained_native_effect_receipt_v01(*, receipt, request, decision):
    """Structural historical proof only; cannot authorize a new execution."""
    try:
        if _validate_kernel_artifact_v01(receipt) or _request_errors(request, check_id=True) or _decision_structure_errors(decision):
            return ('native_retained_envelope_or_context_invalid',)
        errors = _native_effect_receipt_binding_errors_v01(receipt, request, decision)
        return errors or _retained_effect_receipt_contract_errors_v01(receipt=receipt, request=request,
            decision=decision, root_scope_refs=request.scope_refs)
    except Exception:
        return ('native_retained_receipt_invalid',)


def bind_native_action_authorization_v01(*, firewall, registry, projection, corridor,
    corridor_step, current_dependency_observations, logical_time_bridge):
    """Retain a public, contextual proof in this already Root-issued boundary."""
    from hedgehog import action_commit_packet_v02 as action
    _native_require(not validate_effect_firewall_v01(firewall), 'native_firewall_invalid')
    _native_require(firewall._state.native_authorization is None and
        not firewall._state.started_capability_ids, 'native_authorization_already_bound')
    valid, reasons = action.validate_action_packet_effect_firewall_projection_v01(
        projection, registry, packet_id=projection.packet_id, corridor=corridor,
        corridor_step=corridor_step, current_dependency_observations=current_dependency_observations,
        logical_time_bridge=logical_time_bridge,
        eligibility_evaluation_time=projection.eligibility_evaluation_time,
        eligibility_evaluation_time_source=projection.eligibility_evaluation_time_source,
        eligibility_evaluation_context_id=projection.eligibility_evaluation_context_id)
    _native_require(valid, 'native_authorization_projection:' + repr(reasons))
    entry = next(e for e in registry.action_packet_lifecycle_entries
        if e.root_bound_genesis.packet_identity.packet_id == projection.packet_id)
    bound = entry.root_bound_genesis
    _native_require(type(bound) is action.NativeRootBoundActionCommitPacketV01,
        'native_authorization_encoding')
    _native_require((firewall.transaction_id, firewall.target_root_id, firewall.root_decision_id,
        firewall.selected_candidate_id, firewall.permission_ref, firewall.invocation_id,
        firewall.allowed_adapter_ids, firewall.allowed_action_kinds, firewall.root_scope_refs,
        firewall.maximum_expires_at_tick) == (projection.transaction_id, projection.target_root_id,
        projection.root_decision_id, projection.selected_candidate_id, projection.permission_ref,
        projection.execution_attempt_id, projection.allowed_adapter_ids, projection.allowed_action_kinds,
        projection.root_scope_refs, projection.maximum_expires_at_tick), 'native_authorization_root_context')
    firewall._state.native_authorization = (bound, projection, corridor_step)


def execute_bound_effect_v01(*, firewall, request, decision, current_tick, invocation,
    admitted_capability, child_scope_refs, child_expires_at_tick, time_envelope):
    snapshot = snapshot_admitted_capability_v01(admitted_capability)
    _native_require(snapshot.definition.effect_kind == 'MOCK_CONSEQUENTIAL', 'capability_pure_as_effect')
    _native_require(not validate_effect_firewall_v01(firewall), 'native_firewall_invalid')
    binding = firewall._state.native_authorization
    _native_require(type(binding) is tuple and len(binding) == 3, 'native_authorization_missing')
    bound, projection, step = binding
    errors = validate_bound_capability_invocation_v01(invocation, snapshot, bound.canonical_projection)
    if errors:
        raise ValueError(errors[0])
    _native_require((invocation.packet_id, invocation.execution_attempt_id, child_scope_refs,
        child_expires_at_tick, current_tick) == (bound.packet_identity.packet_id,
        projection.execution_attempt_id, projection.scope_refs, projection.expires_at_tick,
        projection.current_tick), 'native_authorization_attempt_corridor')
    _native_require((request.adapter_id, request.action_kind, request.scope_refs, request.idempotency_key,
        request.issued_at_tick, request.expires_at_tick) == (projection.adapter_id, projection.action_kind,
        projection.scope_refs, projection.idempotency_key, projection.issued_at_tick,
        projection.expires_at_tick), 'native_authorization_request')
    actual = {v.parameter_name: v.value for v in invocation.inputs}
    for role in snapshot.definition.business_semantics.input_bindings:
        if role.source_kind == 'SUBJECT_RECORD':
            _native_require(actual[role.input_name] in step.subject_scope.included_subject_refs and
                actual[role.input_name] not in step.subject_scope.excluded_subject_refs,
                'native_dispatch_narrowed_subject')
        if role.source_kind == 'TARGET_RECORD':
            _native_require(actual[role.input_name] in step.target_scope.included_target_refs and
                actual[role.input_name] not in step.target_scope.excluded_target_refs,
                'native_dispatch_narrowed_target')
    origin = admitted_capability._origin
    _native_require(origin.owner is None or origin.start_observer is not None,
        'capability_host_dispatch_required')
    _native_require(invocation.owning_root_id == request.target_root_id and invocation.candidate_id == request.selected_candidate_id
        and snapshot.definition.business_semantics.selected_action_class == request.action_kind,
        'native_dispatch_root_candidate_action')
    _native_require(set(invocation.resource_refs) <= set(child_scope_refs), 'native_dispatch_resource_scope')
    # Structural evidence is replayable, but live start requires the designated call.
    input_validation = admitted_capability.input_validator(snapshot.definition, invocation.inputs)
    errors = _capability_evidence_errors(input_validation, snapshot.definition, invocation.inputs, None)
    if errors:
        raise ValueError('capability_input_validation_failed:' + errors[0])
    _native_require(input_validation == invocation.input_validation, 'capability_input_validation_observation_mismatch')
    invocation = _replace(invocation, input_validation=input_validation)
    capability = _begin_exclusive_effect_v01(firewall=firewall, request=request, decision=decision,
        current_tick=current_tick, adapter_id=request.adapter_id, action_kind=request.action_kind,
        child_scope_refs=child_scope_refs, child_expires_at_tick=child_expires_at_tick)
    firewall._state.started_capability_ids.add(capability.capability_id)
    if origin.start_observer is not None:
        origin.start_observer(invocation)
    try:
        output = admitted_capability.executor(invocation)
        output_validation = admitted_capability.output_validator(snapshot.definition, invocation, output)
        result = build_capability_execution_result_v01(invocation=invocation, admission_snapshot=snapshot,
            output=output, output_validation=output_validation)
        evidence = NativeExecutionEvidenceV01(snapshot, invocation, result)
        firewall._state.native_evidence_by_capability_id[capability.capability_id] = evidence
        receipt = build_native_effect_receipt_v01(firewall=firewall, request=request, decision=decision,
            time_envelope=time_envelope, execution_evidence=evidence)
        _record_exclusive_consumption_v01(firewall, capability, receipt.artifact_id)
        return receipt
    except Exception as exc:
        raise ValueError('effect_outcome_unresolved') from exc
