from __future__ import annotations

from collections.abc import Mapping
from dataclasses import (
    dataclass,
    fields as _dataclass_fields,
    is_dataclass as _is_dataclass,
    replace as _dataclass_replace,
)
from datetime import date
from decimal import Decimal, InvalidOperation
import re
from types import MappingProxyType
import unicodedata

from hedgehog.kernel.integrity_replay_v01 import (
    canonical_json_bytes_v01,
    domain_separated_sha256_hex_v01,
)
from hedgehog.kernel.effect_firewall_v01 import (
    EFFECT_ACCESS_OWNER as _EFFECT_ACCESS_OWNER,
    EFFECT_DECISION_ALLOW_MOCK_EFFECT as _EFFECT_DECISION_ALLOW_MOCK_EFFECT,
    EFFECT_DECISION_BLOCKED_FAIL_CLOSED as _EFFECT_DECISION_BLOCKED_FAIL_CLOSED,
    EFFECT_FIREWALL_VERSION as _EFFECT_FIREWALL_VERSION,
    RECEIPT_SOURCE_COMPONENT as _RECEIPT_SOURCE_COMPONENT,
    EffectFirewallDecisionV01 as _EffectFirewallDecisionV01,
    EffectFirewallHistoricalAuthorizationProjectionV01 as _EffectFirewallHistoricalAuthorizationProjectionV01,
    EffectFirewallV01 as _EffectFirewallV01,
    EffectRequestV01 as _EffectRequestV01,
    authorize_effect_request_v01 as _authorize_effect_request_v01,
    build_effect_firewall_v01 as _build_effect_firewall_v01,
    build_effect_request_v01 as _build_effect_request_v01,
    effect_firewall_decision_to_plain_dict_v01 as _effect_firewall_decision_to_plain_dict_v01,
    effect_firewall_to_plain_dict_v01 as _effect_firewall_to_plain_dict_v01,
    effect_request_to_plain_dict_v01 as _effect_request_to_plain_dict_v01,
    execute_mock_effect_v01 as _execute_mock_effect_v01,
    project_effect_firewall_historical_authorization_v01 as _project_effect_firewall_historical_authorization_v01,
    validate_effect_receipt_v01 as _validate_effect_receipt_v01,
    validate_effect_firewall_decision_v01 as _validate_effect_firewall_decision_v01,
    validate_effect_firewall_v01 as _validate_effect_firewall_v01,
    validate_effect_request_v01 as _validate_effect_request_v01,
)
from hedgehog.kernel.abi_v01 import (
    KernelArtifactV01 as _KernelArtifactV01,
    build_kernel_artifact_v01 as _build_kernel_artifact_v01,
    kernel_artifact_to_plain_dict_v01 as _kernel_artifact_to_plain_dict_v01,
    validate_kernel_artifact_v01 as _validate_kernel_artifact_v01,
)
from hedgehog.kernel.root_decision_v01 import (
    RootDecisionInputV01,
    RootDecisionKernelV01,
    RootDecisionResultV01,
    root_decision_input_to_plain_dict_v01,
    root_decision_result_to_plain_dict_v01,
    validate_root_decision_input_v01,
    validate_root_decision_kernel_v01,
    validate_root_decision_result_v01,
)
from hedgehog.kernel.transition_registry_v01 import (
    ACTION_PACKET_TRANSITION_REGISTRY_PROFILE_VERSION_V01,
    ActionPacketTransitionRegistryProfileV01,
    ActionPacketTransitionRuleV01,
    build_action_packet_transition_registry_profile_v01,
    lookup_action_packet_transition_rule_v01,
    validate_action_packet_transition_registry_profile_v01,
)


SUBJECT_SUPPLIER_A = "supplier_a_adriatic_filters"
SUBJECT_SUPPLIER_B = "supplier_b_balkan_pumps"
SUBJECT_SHIPMENT_SH_2042 = "shipment_sh_2042"

ACTION_MOCK_SUPPLIER_A_PAYMENT_INTENT = "mock_supplier_a_payment_intent"
ACTION_MOCK_SUPPLIER_A_PAYMENT_ORDER = "mock_supplier_a_payment_order"
ACTION_SUPPLIER_B_PAYMENT = "supplier_b_payment"
ACTION_SHIPMENT_RELEASE = "shipment_release"
ACTION_REAL_PAYMENT = "real_payment"
ACTION_REAL_BANK_TRANSFER = "real_bank_transfer"

ADAPTER_MOCK_BANK_SANDBOX = "mock_bank_sandbox"
ADAPTER_BANK_A_MOCK = "bank_a_mock"
ADAPTER_REAL_BANK = "real_bank"
ADAPTER_REAL_SUPPLIER_API = "real_supplier_api"
ADAPTER_REAL_WAREHOUSE_API = "real_warehouse_api"

STATUS_PASS = "PASS"
STATUS_FAIL_CLOSED = "FAIL_CLOSED"
STATUS_RETURN_TO_ROOT = "RETURN_TO_ROOT"

REASON_MISSING_PACKET_ID = "missing_packet_id"
REASON_MISSING_ROOT_CREATION = "missing_root_creation"
REASON_MISSING_SOURCE_ROOT_DECISION_REF = "missing_source_root_decision_ref"
REASON_MISSING_HUMAN_APPROVAL_REF = "missing_human_approval_ref"
REASON_MISSING_SCOPE = "missing_scope"
REASON_MISSING_TTL = "missing_ttl"
REASON_MISSING_IDEMPOTENCY_KEY = "missing_idempotency_key"
REASON_ROOT_ONLY_PACKET_CREATION_REQUIRED = "root_only_packet_creation_required"
REASON_HUMAN_APPROVAL_IS_EVIDENCE_ONLY = "human_approval_is_evidence_only"
REASON_LLM_CANNOT_CREATE_ACTION_COMMIT_PACKET = (
    "llm_cannot_create_action_commit_packet"
)
REASON_AVF_CANNOT_CREATE_ACTION_COMMIT_PACKET = (
    "avf_cannot_create_action_commit_packet"
)
REASON_DRS_CANNOT_CREATE_ACTION_COMMIT_PACKET = (
    "drs_cannot_create_action_commit_packet"
)
REASON_GT_LGT_CANNOT_CREATE_ACTION_COMMIT_PACKET = (
    "gt_lgt_cannot_create_action_commit_packet"
)
REASON_SUPPLIER_B_SCOPE_FORBIDDEN = "supplier_b_scope_forbidden"
REASON_SHIPMENT_RELEASE_FORBIDDEN = "shipment_release_forbidden"
REASON_REAL_BANK_ADAPTER_FORBIDDEN = "real_bank_adapter_forbidden"
REASON_REAL_SUPPLIER_API_FORBIDDEN = "real_supplier_api_forbidden"
REASON_REAL_WAREHOUSE_API_FORBIDDEN = "real_warehouse_api_forbidden"
REASON_REAL_WORLD_EFFECTS_FORBIDDEN = "real_world_effects_forbidden"
REASON_INVALID_TTL = "invalid_ttl"
REASON_EXPIRED_PACKET = "expired_packet"
REASON_CHILD_ALLOWED_NOT_SUBSET_OF_PARENT = "child_allowed_not_subset_of_parent"
REASON_CHILD_SCOPE_NOT_SUBSET_OF_PARENT = "child_scope_not_subset_of_parent"
REASON_CHILD_PARENT_PACKET_ID_MISMATCH = "child_parent_packet_id_mismatch"
REASON_CHILD_FORBIDDEN_DOES_NOT_INCLUDE_PARENT_FORBIDDEN = (
    "child_forbidden_does_not_include_parent_forbidden"
)
REASON_CHILD_TTL_EXCEEDS_PARENT_TTL = "child_ttl_exceeds_parent_ttl"
REASON_CHILD_ADAPTER_NOT_ALLOWED_BY_PACKET = "child_adapter_not_allowed_by_packet"
REASON_ADAPTER_BINDING_NOT_ALLOWED_BY_PACKET = (
    "adapter_binding_not_allowed_by_packet"
)
REASON_CHILD_AMOUNT_MISMATCH = "child_amount_mismatch"
REASON_CHILD_CREDITOR_MISMATCH = "child_creditor_mismatch"
REASON_CHILD_PAYMENT_SLOT_MISMATCH = "child_payment_slot_mismatch"
REASON_CHILD_IDEMPOTENCY_MISMATCH = "child_idempotency_mismatch"
REASON_RECEIPT_IS_EVIDENCE_ONLY = "receipt_is_evidence_only"
REASON_RECEIPT_CANNOT_CREATE_FUTURE_PERMISSION = (
    "receipt_cannot_create_future_permission"
)
REASON_RECEIPT_CANNOT_RELEASE_SHIPMENT = "receipt_cannot_release_shipment"
REASON_RECEIPT_CANNOT_AUTHORIZE_SUPPLIER_B = "receipt_cannot_authorize_supplier_b"
REASON_RECEIPT_WRONG_PACKET_ID = "receipt_wrong_packet_id"
REASON_RECEIPT_WRONG_ADAPTER = "receipt_wrong_adapter"
REASON_RECEIPT_SCOPE_LEAKAGE = "receipt_scope_leakage"
REASON_DUPLICATE_PACKET_ID = "duplicate_packet_id"
REASON_DUPLICATE_IDEMPOTENCY_KEY = "duplicate_idempotency_key"
REASON_REASONING_DOES_NOT_RESTART_AFTER_ROOT = (
    "reasoning_does_not_restart_after_root"
)
REASON_NO_POST_ROOT_LLM_REASONING = "no_post_root_llm_reasoning"
REASON_NO_EXPANSION_AFTER_ROOT = "no_expansion_after_root"
REASON_PRODUCTION_CLAIM_NOT_ALLOWED = "production_claim_not_allowed"
REASON_PUBLIC_AUDITOR_CLAIM_NOT_ALLOWED = "public_auditor_claim_not_allowed"
REASON_REGISTRY_IS_NOT_AUTHORITY = "registry_is_not_authority"
REASON_REGISTRY_IS_NOT_PERMISSION = "registry_is_not_permission"
REASON_REGISTRY_IS_NOT_DRS = "registry_is_not_drs"
REASON_REGISTRY_IS_LOCAL_PROOF_ONLY = "registry_is_local_proof_only"
REASON_REGISTRY_CANNOT_REPAIR_INVALID_PACKET = (
    "registry_cannot_repair_invalid_packet"
)
REASON_REGISTRY_CANNOT_CREATE_RECEIPT = "registry_cannot_create_receipt"
REASON_REGISTRY_CANNOT_EXECUTE_PAYMENT = "registry_cannot_execute_payment"
REASON_REGISTRY_CANNOT_RELEASE_SHIPMENT = "registry_cannot_release_shipment"
REASON_PACKET_REGISTRY_DUPLICATE_PACKET_ID = (
    "packet_registry_duplicate_packet_id"
)
REASON_PACKET_REGISTRY_DUPLICATE_IDEMPOTENCY_KEY = (
    "packet_registry_duplicate_idempotency_key"
)
REASON_PACKET_REGISTRY_TERMINAL_RECEIPT_EXISTS = (
    "packet_registry_terminal_receipt_exists"
)
REASON_PACKET_REGISTRY_EXPIRED_PACKET = "packet_registry_expired_packet"
REASON_RETRY_BEFORE_TERMINAL_RECEIPT_ALLOWED = (
    "retry_before_terminal_receipt_allowed"
)
REASON_RETRY_AFTER_TERMINAL_RECEIPT_REJECTED = (
    "retry_after_terminal_receipt_rejected"
)
REASON_REGISTRY_PRODUCTION_PERSISTENCE_FORBIDDEN = (
    "registry_production_persistence_forbidden"
)
REASON_REGISTRY_GLOBAL_DRS_WRITE_FORBIDDEN = "registry_global_drs_write_forbidden"
REASON_REGISTRY_EXTERNAL_DRS_WRITE_FORBIDDEN = (
    "registry_external_drs_write_forbidden"
)
REASON_REGISTRY_REAL_WORLD_EFFECTS_FORBIDDEN = (
    "registry_real_world_effects_forbidden"
)

CONTAINMENT_LAWS_V02 = (
    "Allowed(child) <= Allowed(parent)",
    "Scope(child) <= Scope(parent)",
    "Forbidden(child) >= Forbidden(parent)",
    "TTL(child) <= TTL(parent)",
    "Adapter(child) in AllowedAdapters(parent)",
    "NoExpansionAfterRoot = true",
)


@dataclass(frozen=True)
class PermissionScopeV02:
    allowed_subjects: tuple[str, ...]
    forbidden_subjects: tuple[str, ...]
    allowed_actions: tuple[str, ...]
    forbidden_actions: tuple[str, ...]
    allowed_adapters: tuple[str, ...]
    forbidden_adapters: tuple[str, ...]
    payment_slot_ref: str
    creditor_ref: str
    amount: str
    currency: str


@dataclass(frozen=True)
class PacketTTL:
    created_at: str
    expires_at: str
    ttl_seconds: int
    ttl_valid: bool = True
    expired: bool = False


@dataclass(frozen=True)
class IdempotencyKeyV02:
    key: str
    duplicate_packet_id: bool = False
    duplicate_idempotency_key: bool = False
    terminal_receipt_already_exists: bool = False


@dataclass(frozen=True)
class AdapterBindingV02:
    adapter_id: str
    adapter_kind: str = "mock_bank"
    real_adapter: bool = False
    adapter_version: str | None = None


@dataclass(frozen=True)
class PacketEvidenceRefV02:
    evidence_id: str
    evidence_kind: str
    source_ref: str


@dataclass(frozen=True)
class ActionCommitPacketV02:
    packet_id: str
    source_root_decision_ref: str
    human_approval_ref: str
    scope: PermissionScopeV02
    ttl: PacketTTL
    idempotency: IdempotencyKeyV02
    adapter_binding: AdapterBindingV02
    packet_type: str = "supplier_a_mock_payment_action_commit_packet_v02"
    created_by: str = "root"
    root_created: bool = True
    evidence_refs: tuple[PacketEvidenceRefV02, ...] = ()
    drs_refs: tuple[str, ...] = ()
    avf_refs: tuple[str, ...] = ()
    bsep_ref: str = ""
    root_boundary_ref: str = ""
    receipt_evidence_only: bool = True
    real_world_effects_allowed: bool = False
    production_ready_claimed: bool = False
    public_auditor_ready_claimed: bool = False


@dataclass(frozen=True)
class ContractFulfillmentCorridorV01:
    corridor_id: str
    packet_id: str
    corridor_kind: str = "supplier_a_mock_payment_corridor"
    deterministic_only: bool = True
    post_root_llm_reasoning_allowed: bool = False
    reasoning_restarted_after_root: bool = False
    allowed_steps: tuple[str, ...] = ()
    root_review_required_on_mismatch: bool = True


@dataclass(frozen=True)
class CorridorStepV01:
    step_id: str
    parent_packet_id: str
    allowed_subjects: tuple[str, ...]
    forbidden_subjects: tuple[str, ...]
    allowed_actions: tuple[str, ...]
    forbidden_actions: tuple[str, ...]
    adapter_id: str
    ttl_seconds: int
    amount: str
    creditor_ref: str
    payment_slot_ref: str
    idempotency_key: str
    creates_permission: bool = False
    creates_final_output: bool = False
    releases_shipment: bool = False
    executes_real_payment: bool = False
    calls_real_api: bool = False


@dataclass(frozen=True)
class CorridorValidationReportV01:
    validation_status: str
    return_to_root_required: bool
    reason_codes: tuple[str, ...]
    packet_id: str
    step_id: str | None = None
    authority_expanded: bool = False
    scope_expanded: bool = False
    real_world_effects_count: int = 0


@dataclass(frozen=True)
class MockReceiptEvidenceV01:
    receipt_id: str
    packet_id: str
    subject: str
    adapter_id: str
    amount: str
    currency: str
    idempotency_key: str
    evidence_only: bool = True
    creates_future_permission: bool = False
    creates_action_permission: bool = False
    creates_final_output: bool = False
    releases_shipment: bool = False
    authorizes_supplier_b: bool = False
    mutates_packet_scope: bool = False
    creates_production_drs_record: bool = False
    real_world_effects_count: int = 0


@dataclass(frozen=True)
class ActionCommitPacketRegistryV02:
    registry_id: str
    seen_packet_ids: tuple[str, ...] = ()
    used_idempotency_keys: tuple[str, ...] = ()
    terminal_receipt_packet_ids: tuple[str, ...] = ()
    terminal_receipt_idempotency_keys: tuple[str, ...] = ()
    expired_packet_ids: tuple[str, ...] = ()
    failed_packet_ids: tuple[str, ...] = ()
    local_proof_only: bool = True
    production_persistence: bool = False
    global_drs_write: bool = False
    external_drs_write: bool = False
    creates_permission: bool = False
    creates_receipt: bool = False
    executes_payment: bool = False
    releases_shipment: bool = False
    real_world_effects_count: int = 0
    action_packet_lifecycle_entries: tuple[ActionPacketLifecycleEntryV01, ...] = ()
    idempotency_disposition_events: tuple[IdempotencyDispositionEventV01, ...] = ()
    action_packet_invalidation_contexts: tuple[
        _ActionPacketInvalidationContextV01,
        ...,
    ] = ()
    action_packet_fulfillment_attempt_contexts: tuple[
        _ActionPacketFulfillmentAttemptContextV01,
        ...,
    ] = ()


@dataclass(frozen=True)
class PacketRegistryValidationReportV02:
    validation_status: str
    return_to_root_required: bool
    reason_codes: tuple[str, ...]
    packet_id: str
    registry_id: str
    retry_allowed: bool = False
    packet_accepted_for_corridor_validation: bool = False
    registry_is_authority: bool = False
    registry_grants_permission: bool = False
    registry_creates_receipt: bool = False
    registry_executes_payment: bool = False
    registry_releases_shipment: bool = False
    real_world_effects_count: int = 0


@dataclass(frozen=True)
class PacketCorridorValidationReportV02:
    validation_status: str
    return_to_root_required: bool
    reason_codes: tuple[str, ...]
    packet_id: str
    registry_id: str
    packet_valid: bool
    registry_valid: bool
    corridor_valid: bool
    receipt_policy_valid: bool
    accepted_for_mock_corridor: bool = False
    creates_action_commit_packet: bool = False
    creates_receipt: bool = False
    executes_payment: bool = False
    releases_shipment: bool = False
    creates_final_output: bool = False
    real_world_effects_count: int = 0


def _append_reason(reasons: list[str], reason: str) -> None:
    if reason not in reasons:
        reasons.append(reason)


def _non_empty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _all_non_empty(values: tuple[str, ...]) -> bool:
    return bool(values) and all(_non_empty(value) for value in values)


def _is_subset(child: tuple[str, ...], parent: tuple[str, ...]) -> bool:
    return set(child).issubset(set(parent))


def _includes(parent_forbidden: tuple[str, ...], child_forbidden: tuple[str, ...]) -> bool:
    return set(parent_forbidden).issubset(set(child_forbidden))


def _tuple_add_unique(values: tuple[str, ...], value: str) -> tuple[str, ...]:
    if value in values:
        return values
    return (*values, value)


def _source_creator_reason(created_by: str) -> str | None:
    creator = created_by.lower()
    if "human" in creator:
        return REASON_HUMAN_APPROVAL_IS_EVIDENCE_ONLY
    if "llm" in creator or "gemini" in creator or "model" in creator:
        return REASON_LLM_CANNOT_CREATE_ACTION_COMMIT_PACKET
    if "avf" in creator:
        return REASON_AVF_CANNOT_CREATE_ACTION_COMMIT_PACKET
    if "drs" in creator:
        return REASON_DRS_CANNOT_CREATE_ACTION_COMMIT_PACKET
    if "gt" in creator or "lgt" in creator:
        return REASON_GT_LGT_CANNOT_CREATE_ACTION_COMMIT_PACKET
    return None


def build_supplier_a_mock_action_commit_packet_fixture_v02() -> ActionCommitPacketV02:
    scope = PermissionScopeV02(
        allowed_subjects=(SUBJECT_SUPPLIER_A,),
        forbidden_subjects=(SUBJECT_SUPPLIER_B, SUBJECT_SHIPMENT_SH_2042),
        allowed_actions=(
            ACTION_MOCK_SUPPLIER_A_PAYMENT_INTENT,
            ACTION_MOCK_SUPPLIER_A_PAYMENT_ORDER,
        ),
        forbidden_actions=(
            ACTION_SUPPLIER_B_PAYMENT,
            ACTION_SHIPMENT_RELEASE,
            ACTION_REAL_PAYMENT,
            ACTION_REAL_BANK_TRANSFER,
        ),
        allowed_adapters=(ADAPTER_MOCK_BANK_SANDBOX, ADAPTER_BANK_A_MOCK),
        forbidden_adapters=(
            ADAPTER_REAL_BANK,
            ADAPTER_REAL_SUPPLIER_API,
            ADAPTER_REAL_WAREHOUSE_API,
        ),
        payment_slot_ref="payment_slot:bank_a_mock:inv_2042",
        creditor_ref=SUBJECT_SUPPLIER_A,
        amount="1250.00",
        currency="EUR",
    )
    return ActionCommitPacketV02(
        packet_id="acp_v02:supplier_a_mock_payment:inv_2042",
        source_root_decision_ref="root_review:supplier_a_mock_payment_ready",
        human_approval_ref="human_approval:supplier_a_scope_only",
        scope=scope,
        ttl=PacketTTL(
            created_at="2026-07-08T00:00:00Z",
            expires_at="2026-07-08T01:00:00Z",
            ttl_seconds=3600,
        ),
        idempotency=IdempotencyKeyV02(
            key="idem:acp_v02:supplier_a_mock_payment:inv_2042",
        ),
        adapter_binding=AdapterBindingV02(adapter_id=ADAPTER_MOCK_BANK_SANDBOX),
        evidence_refs=(
            PacketEvidenceRefV02(
                evidence_id="evidence:root_review_supplier_a_ready",
                evidence_kind="root_review",
                source_ref="root_boundary:supplier_payment_review",
            ),
        ),
        drs_refs=("local_drs_v0_2_resolve_report",),
        avf_refs=("avf_v0_2_evaluation_report",),
        bsep_ref="bsep:supplier_payment_review",
        root_boundary_ref="root_boundary:supplier_a_mock_payment",
    )


def validate_action_commit_packet_v02(
    packet: ActionCommitPacketV02,
) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []

    if not _non_empty(packet.packet_id):
        _append_reason(reasons, REASON_MISSING_PACKET_ID)

    if not packet.root_created:
        _append_reason(reasons, REASON_MISSING_ROOT_CREATION)
    if packet.created_by != "root" or not packet.root_created:
        _append_reason(reasons, REASON_ROOT_ONLY_PACKET_CREATION_REQUIRED)
        creator_reason = _source_creator_reason(packet.created_by)
        if creator_reason is not None:
            _append_reason(reasons, creator_reason)

    if not _non_empty(packet.source_root_decision_ref):
        _append_reason(reasons, REASON_MISSING_SOURCE_ROOT_DECISION_REF)
    if not _non_empty(packet.human_approval_ref):
        _append_reason(reasons, REASON_MISSING_HUMAN_APPROVAL_REF)

    scope = packet.scope
    if not isinstance(scope, PermissionScopeV02):
        _append_reason(reasons, REASON_MISSING_SCOPE)
    else:
        if (
            not _all_non_empty(scope.allowed_subjects)
            or not _all_non_empty(scope.forbidden_subjects)
            or not _all_non_empty(scope.allowed_actions)
            or not _all_non_empty(scope.forbidden_actions)
            or not _all_non_empty(scope.allowed_adapters)
            or not _all_non_empty(scope.forbidden_adapters)
            or not _non_empty(scope.payment_slot_ref)
            or not _non_empty(scope.creditor_ref)
            or not _non_empty(scope.amount)
            or not _non_empty(scope.currency)
        ):
            _append_reason(reasons, REASON_MISSING_SCOPE)
        if (
            SUBJECT_SUPPLIER_B in scope.allowed_subjects
            or ACTION_SUPPLIER_B_PAYMENT in scope.allowed_actions
        ):
            _append_reason(reasons, REASON_SUPPLIER_B_SCOPE_FORBIDDEN)
        if (
            SUBJECT_SHIPMENT_SH_2042 in scope.allowed_subjects
            or ACTION_SHIPMENT_RELEASE in scope.allowed_actions
        ):
            _append_reason(reasons, REASON_SHIPMENT_RELEASE_FORBIDDEN)
        if (
            ACTION_REAL_PAYMENT in scope.allowed_actions
            or ACTION_REAL_BANK_TRANSFER in scope.allowed_actions
        ):
            _append_reason(reasons, REASON_REAL_WORLD_EFFECTS_FORBIDDEN)
        if ADAPTER_REAL_BANK in scope.allowed_adapters:
            _append_reason(reasons, REASON_REAL_BANK_ADAPTER_FORBIDDEN)
        if ADAPTER_REAL_SUPPLIER_API in scope.allowed_adapters:
            _append_reason(reasons, REASON_REAL_SUPPLIER_API_FORBIDDEN)
        if ADAPTER_REAL_WAREHOUSE_API in scope.allowed_adapters:
            _append_reason(reasons, REASON_REAL_WAREHOUSE_API_FORBIDDEN)

    ttl = packet.ttl
    if not isinstance(ttl, PacketTTL):
        _append_reason(reasons, REASON_MISSING_TTL)
    else:
        if ttl.ttl_seconds <= 0 or not ttl.ttl_valid:
            _append_reason(reasons, REASON_INVALID_TTL)
        if ttl.expired:
            _append_reason(reasons, REASON_EXPIRED_PACKET)

    idempotency = packet.idempotency
    if not isinstance(idempotency, IdempotencyKeyV02) or not _non_empty(
        getattr(idempotency, "key", ""),
    ):
        _append_reason(reasons, REASON_MISSING_IDEMPOTENCY_KEY)
    else:
        if idempotency.duplicate_packet_id:
            _append_reason(reasons, REASON_DUPLICATE_PACKET_ID)
        if (
            idempotency.duplicate_idempotency_key
            and idempotency.terminal_receipt_already_exists
        ):
            _append_reason(reasons, REASON_DUPLICATE_IDEMPOTENCY_KEY)

    adapter_binding = packet.adapter_binding
    if (
        adapter_binding.real_adapter
        or adapter_binding.adapter_id == ADAPTER_REAL_BANK
    ):
        _append_reason(reasons, REASON_REAL_BANK_ADAPTER_FORBIDDEN)
    if adapter_binding.adapter_id == ADAPTER_REAL_SUPPLIER_API:
        _append_reason(reasons, REASON_REAL_SUPPLIER_API_FORBIDDEN)
    if adapter_binding.adapter_id == ADAPTER_REAL_WAREHOUSE_API:
        _append_reason(reasons, REASON_REAL_WAREHOUSE_API_FORBIDDEN)
    if (
        isinstance(scope, PermissionScopeV02)
        and adapter_binding.adapter_id not in scope.allowed_adapters
    ):
        _append_reason(reasons, REASON_ADAPTER_BINDING_NOT_ALLOWED_BY_PACKET)

    if not packet.receipt_evidence_only:
        _append_reason(reasons, REASON_RECEIPT_IS_EVIDENCE_ONLY)
    if packet.real_world_effects_allowed:
        _append_reason(reasons, REASON_REAL_WORLD_EFFECTS_FORBIDDEN)
    if packet.production_ready_claimed:
        _append_reason(reasons, REASON_PRODUCTION_CLAIM_NOT_ALLOWED)
    if packet.public_auditor_ready_claimed:
        _append_reason(reasons, REASON_PUBLIC_AUDITOR_CLAIM_NOT_ALLOWED)

    return not reasons, tuple(reasons)


def validate_corridor_no_post_root_reasoning_v01(
    corridor: ContractFulfillmentCorridorV01,
) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if not corridor.deterministic_only:
        _append_reason(reasons, REASON_NO_EXPANSION_AFTER_ROOT)
    if corridor.post_root_llm_reasoning_allowed:
        _append_reason(reasons, REASON_NO_POST_ROOT_LLM_REASONING)
    if corridor.reasoning_restarted_after_root:
        _append_reason(reasons, REASON_REASONING_DOES_NOT_RESTART_AFTER_ROOT)
    return not reasons, tuple(reasons)


def validate_corridor_step_against_packet_v01(
    packet: ActionCommitPacketV02,
    step: CorridorStepV01,
) -> CorridorValidationReportV01:
    reasons: list[str] = []
    packet_valid, packet_reasons = validate_action_commit_packet_v02(packet)
    if not packet_valid:
        reasons.extend(packet_reasons)

    scope = packet.scope
    scope_expanded = False
    authority_expanded = False

    if step.parent_packet_id != packet.packet_id:
        _append_reason(reasons, REASON_CHILD_PARENT_PACKET_ID_MISMATCH)
    if not _is_subset(step.allowed_subjects, scope.allowed_subjects):
        _append_reason(reasons, REASON_CHILD_ALLOWED_NOT_SUBSET_OF_PARENT)
        _append_reason(reasons, REASON_CHILD_SCOPE_NOT_SUBSET_OF_PARENT)
        scope_expanded = True
    if not _is_subset(step.allowed_actions, scope.allowed_actions):
        _append_reason(reasons, REASON_CHILD_ALLOWED_NOT_SUBSET_OF_PARENT)
        _append_reason(reasons, REASON_CHILD_SCOPE_NOT_SUBSET_OF_PARENT)
        scope_expanded = True
    if not _includes(scope.forbidden_subjects, step.forbidden_subjects):
        _append_reason(
            reasons,
            REASON_CHILD_FORBIDDEN_DOES_NOT_INCLUDE_PARENT_FORBIDDEN,
        )
    if not _includes(scope.forbidden_actions, step.forbidden_actions):
        _append_reason(
            reasons,
            REASON_CHILD_FORBIDDEN_DOES_NOT_INCLUDE_PARENT_FORBIDDEN,
        )
    if step.ttl_seconds > packet.ttl.ttl_seconds:
        _append_reason(reasons, REASON_CHILD_TTL_EXCEEDS_PARENT_TTL)
    if step.adapter_id not in scope.allowed_adapters:
        _append_reason(reasons, REASON_CHILD_ADAPTER_NOT_ALLOWED_BY_PACKET)
    if step.amount != scope.amount:
        _append_reason(reasons, REASON_CHILD_AMOUNT_MISMATCH)
    if step.creditor_ref != scope.creditor_ref:
        _append_reason(reasons, REASON_CHILD_CREDITOR_MISMATCH)
    if step.payment_slot_ref != scope.payment_slot_ref:
        _append_reason(reasons, REASON_CHILD_PAYMENT_SLOT_MISMATCH)
    if step.idempotency_key != packet.idempotency.key:
        _append_reason(reasons, REASON_CHILD_IDEMPOTENCY_MISMATCH)

    if step.creates_permission or step.creates_final_output:
        _append_reason(reasons, REASON_NO_EXPANSION_AFTER_ROOT)
        authority_expanded = True
    if step.releases_shipment:
        _append_reason(reasons, REASON_SHIPMENT_RELEASE_FORBIDDEN)
        authority_expanded = True
    if step.executes_real_payment or step.calls_real_api:
        _append_reason(reasons, REASON_REAL_WORLD_EFFECTS_FORBIDDEN)
        authority_expanded = True

    status = STATUS_PASS if not reasons else STATUS_FAIL_CLOSED
    return CorridorValidationReportV01(
        validation_status=status,
        return_to_root_required=bool(reasons),
        reason_codes=tuple(reasons),
        packet_id=packet.packet_id,
        step_id=step.step_id,
        authority_expanded=authority_expanded,
        scope_expanded=scope_expanded,
    )


def validate_mock_receipt_evidence_v01(
    packet: ActionCommitPacketV02,
    receipt: MockReceiptEvidenceV01,
) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    packet_valid, packet_reasons = validate_action_commit_packet_v02(packet)
    if not packet_valid:
        reasons.extend(packet_reasons)

    scope = packet.scope

    if receipt.packet_id != packet.packet_id:
        _append_reason(reasons, REASON_RECEIPT_WRONG_PACKET_ID)
    if receipt.subject not in scope.allowed_subjects:
        _append_reason(reasons, REASON_RECEIPT_SCOPE_LEAKAGE)
    if receipt.subject == SUBJECT_SUPPLIER_B or receipt.authorizes_supplier_b:
        _append_reason(reasons, REASON_RECEIPT_CANNOT_AUTHORIZE_SUPPLIER_B)
    if receipt.adapter_id not in scope.allowed_adapters:
        _append_reason(reasons, REASON_RECEIPT_WRONG_ADAPTER)
    if receipt.amount != scope.amount:
        _append_reason(reasons, REASON_CHILD_AMOUNT_MISMATCH)
    if receipt.currency != scope.currency:
        _append_reason(reasons, REASON_CHILD_AMOUNT_MISMATCH)
    if receipt.idempotency_key != packet.idempotency.key:
        _append_reason(reasons, REASON_CHILD_IDEMPOTENCY_MISMATCH)
    if not receipt.evidence_only:
        _append_reason(reasons, REASON_RECEIPT_IS_EVIDENCE_ONLY)
    if receipt.creates_future_permission or receipt.creates_action_permission:
        _append_reason(reasons, REASON_RECEIPT_CANNOT_CREATE_FUTURE_PERMISSION)
    if receipt.creates_final_output:
        _append_reason(reasons, REASON_NO_EXPANSION_AFTER_ROOT)
    if receipt.releases_shipment:
        _append_reason(reasons, REASON_RECEIPT_CANNOT_RELEASE_SHIPMENT)
    if receipt.mutates_packet_scope or receipt.creates_production_drs_record:
        _append_reason(reasons, REASON_NO_EXPANSION_AFTER_ROOT)
    if receipt.real_world_effects_count != 0:
        _append_reason(reasons, REASON_REAL_WORLD_EFFECTS_FORBIDDEN)

    return not reasons, tuple(reasons)


def build_supplier_a_corridor_step_fixture_v01(
    packet: ActionCommitPacketV02,
) -> CorridorStepV01:
    return CorridorStepV01(
        step_id="corridor_step:mock_payment_order",
        parent_packet_id=packet.packet_id,
        allowed_subjects=(SUBJECT_SUPPLIER_A,),
        forbidden_subjects=packet.scope.forbidden_subjects,
        allowed_actions=(ACTION_MOCK_SUPPLIER_A_PAYMENT_ORDER,),
        forbidden_actions=packet.scope.forbidden_actions,
        adapter_id=ADAPTER_MOCK_BANK_SANDBOX,
        ttl_seconds=packet.ttl.ttl_seconds,
        amount=packet.scope.amount,
        creditor_ref=packet.scope.creditor_ref,
        payment_slot_ref=packet.scope.payment_slot_ref,
        idempotency_key=packet.idempotency.key,
    )


def build_supplier_a_mock_receipt_evidence_fixture_v01(
    packet: ActionCommitPacketV02,
) -> MockReceiptEvidenceV01:
    return MockReceiptEvidenceV01(
        receipt_id="mock_receipt:supplier_a:inv_2042",
        packet_id=packet.packet_id,
        subject=SUBJECT_SUPPLIER_A,
        adapter_id=ADAPTER_MOCK_BANK_SANDBOX,
        amount=packet.scope.amount,
        currency=packet.scope.currency,
        idempotency_key=packet.idempotency.key,
    )


def build_empty_action_commit_packet_registry_v02() -> ActionCommitPacketRegistryV02:
    return ActionCommitPacketRegistryV02(registry_id="acp_v02:local_registry")


def build_registry_with_seen_packet_v02(
    packet: ActionCommitPacketV02,
) -> ActionCommitPacketRegistryV02:
    return ActionCommitPacketRegistryV02(
        registry_id="acp_v02:local_registry:seen_packet",
        seen_packet_ids=(packet.packet_id,),
        used_idempotency_keys=(packet.idempotency.key,),
    )


def build_registry_with_terminal_receipt_v02(
    packet: ActionCommitPacketV02,
) -> ActionCommitPacketRegistryV02:
    return ActionCommitPacketRegistryV02(
        registry_id="acp_v02:local_registry:terminal_receipt",
        seen_packet_ids=(packet.packet_id,),
        used_idempotency_keys=(packet.idempotency.key,),
        terminal_receipt_packet_ids=(packet.packet_id,),
        terminal_receipt_idempotency_keys=(packet.idempotency.key,),
    )


class _ActionPacketRegistryValidationPassV01:
    __slots__ = (
        "registry",
        "entries_by_packet_id",
        "entries_by_idempotency_key",
        "dispositions_by_to_owner_packet_id",
        "context_by_object_id",
        "root_bound_genesis_by_object_id",
        "_root_bound_validation_cache",
        "_invalidation_context_validation_cache",
        "_supersession_bundle_cache",
    )

    def __init__(
        self,
        registry: ActionCommitPacketRegistryV02,
    ) -> None:
        entries_by_packet: dict[
            str,
            list[ActionPacketLifecycleEntryV01],
        ] = {}
        entries_by_key: dict[
            str,
            list[ActionPacketLifecycleEntryV01],
        ] = {}
        root_bound_by_object_id: dict[
            int,
            SupplierRootBoundActionCommitPacketV02ProjectionV01,
        ] = {}
        for entry in registry.action_packet_lifecycle_entries:
            if type(entry) is not ActionPacketLifecycleEntryV01:
                continue
            root_bound = entry.root_bound_genesis
            if (
                type(root_bound)
                is not SupplierRootBoundActionCommitPacketV02ProjectionV01
            ):
                continue
            root_bound_by_object_id[id(root_bound)] = root_bound
            packet_identity = root_bound.packet_identity
            if (
                type(packet_identity) is ActionCommitPacketIdentityResultV01
                and type(packet_identity.packet_id) is str
            ):
                entries_by_packet.setdefault(
                    packet_identity.packet_id,
                    [],
                ).append(entry)
            canonical = root_bound.canonical_projection
            if (
                type(canonical)
                is SupplierActionCommitPacketCanonicalProjectionV01
                and type(canonical.idempotency_identity)
                is ActionIdempotencyIdentityV01
                and type(
                    canonical.idempotency_identity.idempotency_key
                )
                is str
            ):
                entries_by_key.setdefault(
                    canonical.idempotency_identity.idempotency_key,
                    [],
                ).append(entry)

        dispositions_by_owner: dict[
            str,
            list[IdempotencyDispositionEventV01],
        ] = {}
        for event in registry.idempotency_disposition_events:
            if (
                type(event) is IdempotencyDispositionEventV01
                and type(event.to_owner_packet_id) is str
            ):
                dispositions_by_owner.setdefault(
                    event.to_owner_packet_id,
                    [],
                ).append(event)

        context_by_object_id: dict[
            int,
            _ActionPacketInvalidationContextV01,
        ] = {}
        for context in registry.action_packet_invalidation_contexts:
            if type(context) is not _ActionPacketInvalidationContextV01:
                continue
            context_by_object_id[id(context)] = context

        self.registry = registry
        self.entries_by_packet_id = MappingProxyType(
            {
                key: tuple(value)
                for key, value in entries_by_packet.items()
            }
        )
        self.entries_by_idempotency_key = MappingProxyType(
            {
                key: tuple(value)
                for key, value in entries_by_key.items()
            }
        )
        self.dispositions_by_to_owner_packet_id = MappingProxyType(
            {
                key: tuple(value)
                for key, value in dispositions_by_owner.items()
            }
        )
        self.context_by_object_id = MappingProxyType(context_by_object_id)
        self.root_bound_genesis_by_object_id = MappingProxyType(
            root_bound_by_object_id
        )
        self._root_bound_validation_cache: dict[
            int,
            tuple[
                SupplierRootBoundActionCommitPacketV02ProjectionV01,
                tuple[bool, tuple[str, ...]],
            ],
        ] = {}
        self._invalidation_context_validation_cache: dict[
            tuple[int, int, int | None],
            tuple[
                _ActionPacketInvalidationContextV01,
                SupplierRootBoundActionCommitPacketV02ProjectionV01,
                SupplierRootBoundActionCommitPacketV02ProjectionV01 | None,
                tuple[bool, tuple[str, ...]],
            ],
        ] = {}
        self._supersession_bundle_cache: dict[
            int,
            tuple[
                _ActionPacketInvalidationContextV01,
                tuple[
                    bool,
                    tuple[str, ...],
                    IdempotencyDispositionEventV01 | None,
                ],
            ],
        ] = {}


@dataclass(frozen=True)
class _ActionPacketRegistryValidationResultV02:
    valid: bool
    reasons: tuple[str, ...]
    validation_pass: _ActionPacketRegistryValidationPassV01 | None


def _unique_lifecycle_entry_from_validation_pass_v01(
    validation_pass: _ActionPacketRegistryValidationPassV01,
    packet_id: object,
) -> ActionPacketLifecycleEntryV01:
    if not validate_prefixed_sha256_identity_v01(
        packet_id,
        prefix=ACTION_COMMIT_PACKET_ID_PREFIX_V01,
    )[0]:
        raise ValueError("action_packet_lifecycle_packet_id_invalid")
    matching = validation_pass.entries_by_packet_id.get(packet_id, ())
    if len(matching) != 1:
        raise ValueError("action_packet_lifecycle_entry_not_found")
    return matching[0]


def _cached_root_bound_validation_v01(
    validation_pass: _ActionPacketRegistryValidationPassV01,
    root_bound_genesis: object,
) -> tuple[bool, tuple[str, ...]]:
    if (
        type(validation_pass) is not _ActionPacketRegistryValidationPassV01
        or validation_pass.root_bound_genesis_by_object_id.get(
            id(root_bound_genesis)
        )
        is not root_bound_genesis
    ):
        return validate_supplier_root_bound_action_commit_packet_v02_projection_v01(
            root_bound_genesis
        )
    cached = validation_pass._root_bound_validation_cache.get(
        id(root_bound_genesis)
    )
    if cached is not None and cached[0] is root_bound_genesis:
        return cached[1]
    result = (
        validate_supplier_root_bound_action_commit_packet_v02_projection_v01(
            root_bound_genesis
        )
    )
    validation_pass._root_bound_validation_cache[id(root_bound_genesis)] = (
        root_bound_genesis,
        result,
    )
    return result


def _cached_invalidation_context_validation_v01(
    validation_pass: _ActionPacketRegistryValidationPassV01,
    context: object,
    predecessor: object,
    *,
    supersession_successor: object = None,
) -> tuple[bool, tuple[str, ...]]:
    successor_id = (
        id(supersession_successor)
        if supersession_successor is not None
        else None
    )
    cache_key = (id(context), id(predecessor), successor_id)
    cacheable = (
        type(context) is _ActionPacketInvalidationContextV01
        and validation_pass.context_by_object_id.get(id(context)) is context
        and validation_pass.root_bound_genesis_by_object_id.get(
            id(predecessor)
        )
        is predecessor
        and (
            supersession_successor is None
            or validation_pass.root_bound_genesis_by_object_id.get(
                id(supersession_successor)
            )
            is supersession_successor
        )
    )
    if cacheable:
        cached = validation_pass._invalidation_context_validation_cache.get(
            cache_key
        )
        if (
            cached is not None
            and cached[0] is context
            and cached[1] is predecessor
            and cached[2] is supersession_successor
        ):
            return cached[3]
    result = _validate_action_packet_invalidation_context_core_v01(
        context,
        predecessor,
        supersession_successor=supersession_successor,
        validation_pass=validation_pass,
    )
    if cacheable:
        validation_pass._invalidation_context_validation_cache[cache_key] = (
            context,
            predecessor,
            supersession_successor,
            result,
        )
    return result


def _validate_action_commit_packet_registry_core_v02(
    registry: object,
) -> _ActionPacketRegistryValidationResultV02:
    if type(registry) is not ActionCommitPacketRegistryV02:
        return _ActionPacketRegistryValidationResultV02(
            valid=False,
            reasons=("action_packet_registry_type_invalid",),
            validation_pass=None,
        )
    reasons: list[str] = []
    validation_pass = None

    if type(registry.local_proof_only) is not bool or not registry.local_proof_only:
        _append_reason(reasons, REASON_REGISTRY_IS_LOCAL_PROOF_ONLY)
        _append_reason(reasons, REASON_REGISTRY_IS_NOT_DRS)
    if (
        type(registry.production_persistence) is not bool
        or registry.production_persistence
    ):
        _append_reason(reasons, REASON_REGISTRY_PRODUCTION_PERSISTENCE_FORBIDDEN)
        _append_reason(reasons, REASON_REGISTRY_IS_NOT_DRS)
    if type(registry.global_drs_write) is not bool or registry.global_drs_write:
        _append_reason(reasons, REASON_REGISTRY_GLOBAL_DRS_WRITE_FORBIDDEN)
        _append_reason(reasons, REASON_REGISTRY_IS_NOT_DRS)
    if (
        type(registry.external_drs_write) is not bool
        or registry.external_drs_write
    ):
        _append_reason(reasons, REASON_REGISTRY_EXTERNAL_DRS_WRITE_FORBIDDEN)
        _append_reason(reasons, REASON_REGISTRY_IS_NOT_DRS)
    if type(registry.creates_permission) is not bool or registry.creates_permission:
        _append_reason(reasons, REASON_REGISTRY_IS_NOT_PERMISSION)
        _append_reason(reasons, REASON_REGISTRY_IS_NOT_AUTHORITY)
    if type(registry.creates_receipt) is not bool or registry.creates_receipt:
        _append_reason(reasons, REASON_REGISTRY_CANNOT_CREATE_RECEIPT)
    if type(registry.executes_payment) is not bool or registry.executes_payment:
        _append_reason(reasons, REASON_REGISTRY_CANNOT_EXECUTE_PAYMENT)
    if type(registry.releases_shipment) is not bool or registry.releases_shipment:
        _append_reason(reasons, REASON_REGISTRY_CANNOT_RELEASE_SHIPMENT)
    if (
        type(registry.real_world_effects_count) is not int
        or registry.real_world_effects_count != 0
    ):
        _append_reason(reasons, REASON_REGISTRY_REAL_WORLD_EFFECTS_FORBIDDEN)

    try:
        lifecycle_valid, lifecycle_reasons, validation_pass = (
            _validate_registry_lifecycle_histories_v01(registry)
        )
        if not lifecycle_valid:
            reasons.extend(lifecycle_reasons)
    except Exception:
        _append_reason(reasons, "action_packet_registry_lifecycle_invalid")

    return _ActionPacketRegistryValidationResultV02(
        valid=not reasons,
        reasons=tuple(reasons),
        validation_pass=validation_pass,
    )


def validate_action_commit_packet_registry_v02(
    registry: object,
) -> tuple[bool, tuple[str, ...]]:
    result = _validate_action_commit_packet_registry_core_v02(registry)
    return result.valid, result.reasons


def _validate_packet_against_registry_prevalidated_v02(
    packet: ActionCommitPacketV02,
    registry: ActionCommitPacketRegistryV02,
    *,
    allow_retry_before_terminal_receipt: bool,
    registry_validation_result: tuple[bool, tuple[str, ...]],
) -> PacketRegistryValidationReportV02:
    reasons: list[str] = []
    retry_allowed = False
    packet_accepted = False

    registry_valid, registry_reasons = registry_validation_result
    if not registry_valid:
        reasons.extend(registry_reasons)

    packet_valid, packet_reasons = validate_action_commit_packet_v02(packet)
    if not packet_valid:
        _append_reason(reasons, REASON_REGISTRY_CANNOT_REPAIR_INVALID_PACKET)
        reasons.extend(packet_reasons)

    if registry_valid and packet_valid:
        terminal_packet_seen = packet.packet_id in registry.terminal_receipt_packet_ids
        terminal_key_seen = (
            packet.idempotency.key in registry.terminal_receipt_idempotency_keys
        )
        packet_seen = packet.packet_id in registry.seen_packet_ids
        key_seen = packet.idempotency.key in registry.used_idempotency_keys

        if packet.packet_id in registry.expired_packet_ids:
            _append_reason(reasons, REASON_PACKET_REGISTRY_EXPIRED_PACKET)
        if terminal_packet_seen:
            _append_reason(reasons, REASON_PACKET_REGISTRY_TERMINAL_RECEIPT_EXISTS)
            _append_reason(reasons, REASON_RETRY_AFTER_TERMINAL_RECEIPT_REJECTED)
        if terminal_key_seen:
            _append_reason(reasons, REASON_PACKET_REGISTRY_TERMINAL_RECEIPT_EXISTS)
            _append_reason(reasons, REASON_RETRY_AFTER_TERMINAL_RECEIPT_REJECTED)

        duplicate_reasons_before_retry = len(reasons)
        if packet_seen and not terminal_packet_seen:
            if allow_retry_before_terminal_receipt:
                retry_allowed = True
                _append_reason(reasons, REASON_RETRY_BEFORE_TERMINAL_RECEIPT_ALLOWED)
            else:
                _append_reason(reasons, REASON_PACKET_REGISTRY_DUPLICATE_PACKET_ID)
        if key_seen and not terminal_key_seen:
            if allow_retry_before_terminal_receipt:
                retry_allowed = True
                _append_reason(reasons, REASON_RETRY_BEFORE_TERMINAL_RECEIPT_ALLOWED)
            else:
                _append_reason(
                    reasons,
                    REASON_PACKET_REGISTRY_DUPLICATE_IDEMPOTENCY_KEY,
                )

        retry_only = (
            retry_allowed
            and duplicate_reasons_before_retry == 0
            and len(reasons) == 1
            and reasons[-1] == REASON_RETRY_BEFORE_TERMINAL_RECEIPT_ALLOWED
        )
        packet_accepted = not reasons or retry_only

    status = STATUS_PASS if packet_accepted else STATUS_FAIL_CLOSED
    return PacketRegistryValidationReportV02(
        validation_status=status,
        return_to_root_required=not packet_accepted,
        reason_codes=tuple(reasons),
        packet_id=packet.packet_id,
        registry_id=registry.registry_id,
        retry_allowed=retry_allowed and packet_accepted,
        packet_accepted_for_corridor_validation=packet_accepted,
    )


def validate_packet_against_registry_v02(
    packet: ActionCommitPacketV02,
    registry: ActionCommitPacketRegistryV02,
    *,
    allow_retry_before_terminal_receipt: bool = False,
) -> PacketRegistryValidationReportV02:
    registry_validation_result = validate_action_commit_packet_registry_v02(
        registry,
    )
    return _validate_packet_against_registry_prevalidated_v02(
        packet,
        registry,
        allow_retry_before_terminal_receipt=(
            allow_retry_before_terminal_receipt
        ),
        registry_validation_result=registry_validation_result,
    )


def validate_packet_corridor_entry_v02(
    packet: ActionCommitPacketV02,
    corridor: ContractFulfillmentCorridorV01,
    step: CorridorStepV01,
    registry: ActionCommitPacketRegistryV02,
    *,
    allow_retry_before_terminal_receipt: bool = False,
) -> PacketCorridorValidationReportV02:
    reasons: list[str] = []

    packet_valid, packet_reasons = validate_action_commit_packet_v02(packet)
    if not packet_valid:
        reasons.extend(packet_reasons)

    registry_valid, registry_reasons = validate_action_commit_packet_registry_v02(
        registry,
    )
    if not registry_valid:
        reasons.extend(registry_reasons)

    registry_report = _validate_packet_against_registry_prevalidated_v02(
        packet,
        registry,
        allow_retry_before_terminal_receipt=allow_retry_before_terminal_receipt,
        registry_validation_result=(registry_valid, registry_reasons),
    )
    if registry_report.validation_status != STATUS_PASS:
        reasons.extend(registry_report.reason_codes)

    corridor_valid, corridor_reasons = validate_corridor_no_post_root_reasoning_v01(
        corridor,
    )
    if not corridor_valid:
        reasons.extend(corridor_reasons)

    step_report = validate_corridor_step_against_packet_v01(packet, step)
    if step_report.validation_status != STATUS_PASS:
        reasons.extend(step_report.reason_codes)

    receipt_policy_valid = bool(packet.receipt_evidence_only)
    if not receipt_policy_valid:
        _append_reason(reasons, REASON_RECEIPT_IS_EVIDENCE_ONLY)

    deduped_reasons: list[str] = []
    for reason in reasons:
        _append_reason(deduped_reasons, reason)

    accepted = not deduped_reasons
    return PacketCorridorValidationReportV02(
        validation_status=STATUS_PASS if accepted else STATUS_FAIL_CLOSED,
        return_to_root_required=not accepted,
        reason_codes=tuple(deduped_reasons),
        packet_id=packet.packet_id,
        registry_id=registry.registry_id,
        packet_valid=packet_valid,
        registry_valid=registry_valid,
        corridor_valid=corridor_valid and step_report.validation_status == STATUS_PASS,
        receipt_policy_valid=receipt_policy_valid,
        accepted_for_mock_corridor=accepted,
    )


def record_packet_seen_v02(
    registry: ActionCommitPacketRegistryV02,
    packet: ActionCommitPacketV02,
) -> ActionCommitPacketRegistryV02:
    return ActionCommitPacketRegistryV02(
        registry_id=registry.registry_id,
        seen_packet_ids=_tuple_add_unique(registry.seen_packet_ids, packet.packet_id),
        used_idempotency_keys=_tuple_add_unique(
            registry.used_idempotency_keys,
            packet.idempotency.key,
        ),
        terminal_receipt_packet_ids=registry.terminal_receipt_packet_ids,
        terminal_receipt_idempotency_keys=registry.terminal_receipt_idempotency_keys,
        expired_packet_ids=registry.expired_packet_ids,
        failed_packet_ids=registry.failed_packet_ids,
        local_proof_only=registry.local_proof_only,
        production_persistence=registry.production_persistence,
        global_drs_write=registry.global_drs_write,
        external_drs_write=registry.external_drs_write,
        creates_permission=registry.creates_permission,
        creates_receipt=registry.creates_receipt,
        executes_payment=registry.executes_payment,
        releases_shipment=registry.releases_shipment,
        real_world_effects_count=registry.real_world_effects_count,
        action_packet_lifecycle_entries=registry.action_packet_lifecycle_entries,
        idempotency_disposition_events=registry.idempotency_disposition_events,
        action_packet_invalidation_contexts=(
            registry.action_packet_invalidation_contexts
        ),
        action_packet_fulfillment_attempt_contexts=(
            registry.action_packet_fulfillment_attempt_contexts
        ),
    )


def record_terminal_receipt_observation_v02(
    registry: ActionCommitPacketRegistryV02,
    packet: ActionCommitPacketV02,
    receipt: MockReceiptEvidenceV01,
) -> tuple[ActionCommitPacketRegistryV02, tuple[str, ...]]:
    receipt_valid, receipt_reasons = validate_mock_receipt_evidence_v01(packet, receipt)
    if not receipt_valid:
        return registry, receipt_reasons

    seen_registry = record_packet_seen_v02(registry, packet)
    terminal_registry = ActionCommitPacketRegistryV02(
        registry_id=seen_registry.registry_id,
        seen_packet_ids=seen_registry.seen_packet_ids,
        used_idempotency_keys=seen_registry.used_idempotency_keys,
        terminal_receipt_packet_ids=_tuple_add_unique(
            seen_registry.terminal_receipt_packet_ids,
            packet.packet_id,
        ),
        terminal_receipt_idempotency_keys=_tuple_add_unique(
            seen_registry.terminal_receipt_idempotency_keys,
            packet.idempotency.key,
        ),
        expired_packet_ids=seen_registry.expired_packet_ids,
        failed_packet_ids=seen_registry.failed_packet_ids,
        local_proof_only=seen_registry.local_proof_only,
        production_persistence=seen_registry.production_persistence,
        global_drs_write=seen_registry.global_drs_write,
        external_drs_write=seen_registry.external_drs_write,
        creates_permission=seen_registry.creates_permission,
        creates_receipt=seen_registry.creates_receipt,
        executes_payment=seen_registry.executes_payment,
        releases_shipment=seen_registry.releases_shipment,
        real_world_effects_count=seen_registry.real_world_effects_count,
        action_packet_lifecycle_entries=(
            seen_registry.action_packet_lifecycle_entries
        ),
        idempotency_disposition_events=(
            seen_registry.idempotency_disposition_events
        ),
        action_packet_invalidation_contexts=(
            seen_registry.action_packet_invalidation_contexts
        ),
        action_packet_fulfillment_attempt_contexts=(
            seen_registry.action_packet_fulfillment_attempt_contexts
        ),
    )
    return terminal_registry, ()


def build_supplier_a_packet_corridor_validation_fixture_v02() -> tuple[
    ActionCommitPacketV02,
    ContractFulfillmentCorridorV01,
    CorridorStepV01,
    ActionCommitPacketRegistryV02,
]:
    packet = build_supplier_a_mock_action_commit_packet_fixture_v02()
    corridor = ContractFulfillmentCorridorV01(
        corridor_id="corridor:supplier_a_mock_payment:v02",
        packet_id=packet.packet_id,
    )
    step = build_supplier_a_corridor_step_fixture_v01(packet)
    registry = build_empty_action_commit_packet_registry_v02()
    return packet, corridor, step, registry


# G2-A1A pure canonical-profile foundations. These contracts are additive and
# do not change the legacy V02 packet, validators, or proof-only Registry.

CanonicalMaterialV01 = tuple[tuple[str, object], ...]

INT64_MIN_V01 = -(2**63)
INT64_MAX_V01 = 2**63 - 1
CANONICAL_DECIMAL_REGEX_V01 = (
    r"(?:0|-?(?:0\.[0-9]*[1-9]|[1-9][0-9]*(?:\.[0-9]*[1-9])?))"
)
LEGACY_PLAIN_DECIMAL_INPUT_REGEX_V01 = (
    r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?"
)
UTC_TIMESTAMP_COMPATIBILITY_REGEX_V01 = (
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T"
    r"[0-9]{2}:[0-9]{2}:[0-9]{2}(?:Z|\+00:00)"
)
LOWERCASE_SHA256_REGEX_V01 = r"[0-9a-f]{64}"
CANONICAL_TOKEN_REGEX_V01 = r"[a-z][a-z0-9_]*"

ABSENT_V01 = MappingProxyType({"$hedgehog_absent": "ABSENT_V01"})

ACTION_SUBJECT_SCOPE_PROFILE_ID_V01 = "action_subject_scope_profile_v01"
ACTION_TARGET_SCOPE_PROFILE_ID_V01 = "action_target_scope_profile_v01"
ACTION_PERMISSION_SCOPE_PROFILE_ID_V01 = "action_permission_scope_profile_v01"
ACTION_EFFECT_PARAMETERS_PROFILE_ID_V01 = "action_effect_parameters_profile_v01"
ACTION_ADAPTER_BINDING_PROFILE_ID_V01 = "action_adapter_binding_profile_v01"
ACTION_DEPENDENCY_SET_CANDIDATE_PROFILE_ID_V01 = (
    "action_dependency_set_candidate_v01"
)
ACTION_DEPENDENCY_TIME_ENVELOPE_COMMITMENT_PROFILE_ID_V01 = (
    "action_dependency_time_envelope_commitment_v01"
)
ACTION_DEPENDENCY_CURRENT_OBSERVATION_PROFILE_ID_V01 = (
    "action_dependency_current_observation_v01"
)
ACTION_PACKET_EFFECT_FIREWALL_PROJECTION_PROFILE_ID_V01 = (
    "action_packet_effect_firewall_projection_v01"
)
ACTION_PACKET_FULFILLMENT_ATTEMPT_EVIDENCE_PROFILE_ID_V01 = (
    "action_packet_fulfillment_attempt_evidence_v01"
)
ACTION_PACKET_LIFECYCLE_REPLAY_PROFILE_ID_V01 = (
    "action_packet_lifecycle_replay_v01"
)
ACTION_PACKET_PRESENT_ELIGIBILITY_INSPECTION_PROFILE_ID_V01 = (
    "action_packet_present_eligibility_inspection_v01"
)
ACTION_PACKET_PRESENT_ELIGIBILITY_STATUSES_V01 = (
    "ELIGIBLE_FOR_BOUNDED_MOCK_ATTEMPT",
    "NON_EXECUTABLE",
)
ACTION_TEMPORAL_AUTHORITY_PROFILE_ID_V01 = (
    "action_temporal_authority_profile_v01"
)
ACTION_AUTHORITY_POLICY_PROFILE_ID_V01 = "action_authority_policy_profile_v01"
ACTION_BUSINESS_OBJECT_IDENTITY_PROFILE_ID_V01 = (
    "action_business_object_identity_profile_v01"
)
ACTION_CONSEQUENTIAL_EFFECT_PARAMETERS_PROFILE_ID_V01 = (
    "action_consequential_effect_parameters_profile_v01"
)

ACTION_EFFECT_PARAMETERS_DOMAIN_V01 = "HEDGEHOG_ACTION_EFFECT_PARAMETERS_V01"
ACTION_DEPENDENCY_SET_CANDIDATE_DOMAIN_V01 = (
    "HEDGEHOG_ACTION_DEPENDENCY_SET_CANDIDATE_V01"
)
ACTION_DEPENDENCY_TIME_ENVELOPE_COMMITMENT_DOMAIN_V01 = (
    "HEDGEHOG_ACTION_DEPENDENCY_TIME_ENVELOPE_COMMITMENT_V01"
)
ACTION_DEPENDENCY_CURRENT_OBSERVATION_DOMAIN_V01 = (
    "HEDGEHOG_ACTION_DEPENDENCY_CURRENT_OBSERVATION_V01"
)
ACTION_PACKET_FULFILLMENT_ATTEMPT_EVIDENCE_DOMAIN_V01 = (
    "HEDGEHOG_ACTION_PACKET_FULFILLMENT_ATTEMPT_EVIDENCE_V01"
)
PACKET_DEPENDENCY_ACCEPTANCE_BINDING_DOMAIN_V01 = (
    "HEDGEHOG_PACKET_DEPENDENCY_ACCEPTANCE_BINDING_V01"
)
ACTION_TEMPORAL_AUTHORITY_DOMAIN_V01 = (
    "HEDGEHOG_ACTION_TEMPORAL_AUTHORITY_V01"
)
ACTION_AUTHORITY_POLICY_DOMAIN_V01 = "HEDGEHOG_ACTION_AUTHORITY_POLICY_V01"
ROOT_LOGICAL_EFFECT_INTENT_DOMAIN_V01 = (
    "HEDGEHOG_ROOT_OWNED_LOGICAL_EFFECT_INTENT_V01"
)
ACTION_IDEMPOTENCY_DOMAIN_V01 = "HEDGEHOG_ACTION_IDEMPOTENCY_KEY_V01"
ROOT_PACKET_AUTHORIZATION_CANDIDATE_DOMAIN_V01 = (
    "HEDGEHOG_ROOT_BOUND_PACKET_AUTHORIZATION_CANDIDATE_V01"
)
ACTION_COMMIT_PACKET_ID_DOMAIN_V01 = "HEDGEHOG_ACTION_COMMIT_PACKET_ID_V01"
ACTION_SOURCE_ROOT_DECISION_DOMAIN_V01 = (
    "HEDGEHOG_ACTION_SOURCE_ROOT_DECISION_V01"
)
ACTION_LOGICAL_TIME_BRIDGE_DOMAIN_V01 = (
    "HEDGEHOG_ACTION_LOGICAL_TIME_BRIDGE_V01"
)

ROOT_LOGICAL_INTENT_PREFIX_V01 = "root_logical_intent_v01:"
ACTION_IDEMPOTENCY_PREFIX_V01 = "idem:action_v01:"
ROOT_PACKET_AUTHORIZATION_PREFIX_V01 = "root_packet_authorization_v01:"
ACTION_COMMIT_PACKET_ID_PREFIX_V01 = "acp_v02:"
PACKET_DEPENDENCY_ACCEPTANCE_PREFIX_V01 = (
    "packet_dependency_acceptance_v01:"
)
ACTION_DEPENDENCY_TIME_ENVELOPE_COMMITMENT_PREFIX_V01 = (
    "dependency_time_envelope_v01:"
)
ACTION_DEPENDENCY_CURRENT_OBSERVATION_PREFIX_V01 = (
    "dependency_observation_v01:"
)
ACTION_PACKET_FULFILLMENT_ATTEMPT_EVIDENCE_PREFIX_V01 = (
    "fulfillment_attempt_evidence_v01:"
)
_ACTION_PACKET_EFFECT_PROJECTION_HASH_DOMAIN_V01 = (
    "HEDGEHOG_ACTION_PACKET_EFFECT_PROJECTION_HASH_V01"
)
_ACTION_PACKET_FIREWALL_STATE_HASH_DOMAIN_V01 = (
    "HEDGEHOG_ACTION_PACKET_FIREWALL_STATE_HASH_V01"
)
_ACTION_PACKET_DISPOSITION_HISTORY_HASH_DOMAIN_V01 = (
    "HEDGEHOG_ACTION_PACKET_DISPOSITION_HISTORY_HASH_V01"
)
_ACTION_PACKET_EFFECT_RECEIPT_HASH_DOMAIN_V01 = (
    "HEDGEHOG_ACTION_PACKET_EFFECT_RECEIPT_HASH_V01"
)
_ACTION_PACKET_EFFECT_RECEIPT_REF_DOMAIN_V01 = (
    "HEDGEHOG_ACTION_PACKET_EFFECT_RECEIPT_REF_V01"
)
_ACTION_PACKET_EFFECT_RECEIPT_REF_PREFIX_V01 = "effect_receipt_v01:"
_ACTION_PACKET_REPLAY_TRANSITION_HISTORY_HASH_DOMAIN_V01 = (
    "HEDGEHOG_ACTION_PACKET_REPLAY_TRANSITION_HISTORY_HASH_V01"
)
_ACTION_PACKET_REPLAY_DISPOSITION_HISTORY_HASH_DOMAIN_V01 = (
    "HEDGEHOG_ACTION_PACKET_REPLAY_DISPOSITION_HISTORY_HASH_V01"
)
_ACTION_PACKET_REPLAY_INVALIDATION_HISTORY_HASH_DOMAIN_V01 = (
    "HEDGEHOG_ACTION_PACKET_REPLAY_INVALIDATION_HISTORY_HASH_V01"
)
_ACTION_PACKET_REPLAY_FULFILLMENT_HISTORY_HASH_DOMAIN_V01 = (
    "HEDGEHOG_ACTION_PACKET_REPLAY_FULFILLMENT_HISTORY_HASH_V01"
)
_ACTION_PACKET_FULFILLMENT_OUTCOME_CLASSES_V01 = (
    "PRE_FULFILLMENT_BLOCKED",
    "FIREWALL_BLOCKED",
    "CONSUMED",
    "NOT_CONSUMED",
    "UNCERTAIN",
)
_ACTION_PACKET_FULFILLMENT_INVOCATION_RELATIONS_V01 = (
    "NO_ADAPTER_INVOCATION",
    "CORRIDOR_INVOCATION_CONSUMED",
    "CORRIDOR_INVOCATION_NONCONSUMING",
    "CORRIDOR_INVOCATION_UNCERTAIN",
)
_ACTION_PACKET_NONCONSUMING_EXECUTION_REASONS_V01 = (
    "effect_request_expired",
)
_ACTION_PACKET_UNCERTAIN_EXECUTION_REASONS_V01 = (
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
    "effect_execution_unexpected_exception",
    "effect_outcome_unresolved",
)
TRANSITION_EVIDENCE_BINDING_PROFILE_ID_V01 = (
    "action_transition_evidence_binding_v01"
)
TRANSITION_EVIDENCE_BINDING_DOMAIN_V01 = (
    "HEDGEHOG_ACTION_TRANSITION_EVIDENCE_BINDING_V01"
)
TRANSITION_EVIDENCE_BINDING_PREFIX_V01 = "acpte_v01:"
EXECUTION_ATTEMPT_IDENTITY_PROFILE_ID_V01 = (
    "action_execution_attempt_identity_v01"
)
EXECUTION_ATTEMPT_IDENTITY_DOMAIN_V01 = (
    "HEDGEHOG_ACTION_EXECUTION_ATTEMPT_ID_V01"
)
EXECUTION_ATTEMPT_IDENTITY_PREFIX_V01 = "execution_attempt_v01:"
ACTION_PACKET_TRANSITION_EVENT_PROFILE_ID_V01 = (
    "action_packet_transition_identity_profile_v01"
)
ACTION_PACKET_TRANSITION_EVENT_DOMAIN_V01 = (
    "HEDGEHOG_ACTION_PACKET_TRANSITION_V01"
)
ACTION_PACKET_TRANSITION_EVENT_PREFIX_V01 = "acpt_v01:"
IDEMPOTENCY_DISPOSITION_EVENT_PROFILE_ID_V01 = (
    "action_idempotency_disposition_event_v01"
)
IDEMPOTENCY_DISPOSITION_EVENT_DOMAIN_V01 = (
    "HEDGEHOG_ACTION_IDEMPOTENCY_DISPOSITION_EVENT_V01"
)
IDEMPOTENCY_DISPOSITION_EVENT_PREFIX_V01 = "idem_event_v01:"
IDEMPOTENCY_DISPOSITIONS_V01 = (
    "UNCLAIMED",
    "RESERVED",
    "CONSUMED",
    "UNCERTAIN_CLOSED",
)
IDEMPOTENCY_DISPOSITION_EVENT_CLASSES_V01 = (
    "RESERVE",
    "TRANSFER_RENEWAL",
    "TRANSFER_SUPERSESSION",
    "CONSUME",
    "UNCERTAIN_CLOSE",
    "RECEIPT_CONFIRM",
)
PRE_G2A_ADAPTER_VERSION_V01 = "pre_g2a_adapter_contract_v01"
EFFECT_FIREWALL_VOCABULARY_PROJECTION_PROFILE_ID_V01 = (
    "effect_firewall_vocabulary_projection_v01"
)
ROOT_DECISION_CANDIDATE_KIND_PACKET_AUTHORIZATION_V01 = (
    "PACKET_AUTHORIZATION"
)
ROOT_DECISION_CANDIDATE_KIND_REVOCATION_V01 = "REVOCATION"
ROOT_DECISION_CANDIDATE_KIND_SUPERSESSION_V01 = "SUPERSESSION"
ROOT_DECISION_CANDIDATE_KINDS_V01 = (
    ROOT_DECISION_CANDIDATE_KIND_PACKET_AUTHORIZATION_V01,
    ROOT_DECISION_CANDIDATE_KIND_REVOCATION_V01,
    ROOT_DECISION_CANDIDATE_KIND_SUPERSESSION_V01,
)
ROOT_DECISION_CLAIM_PREDICATE_REVOCATION_V01 = (
    "action_revocation_candidate_v01"
)
ROOT_DECISION_CLAIM_PREDICATE_SUPERSESSION_V01 = (
    "action_supersession_candidate_v01"
)
REVOCATION_CANDIDATE_PROFILE_ID_V01 = "action_revocation_candidate_v01"
REVOCATION_CANDIDATE_DOMAIN_V01 = (
    "HEDGEHOG_ACTION_REVOCATION_CANDIDATE_V01"
)
REVOCATION_CANDIDATE_PREFIX_V01 = "revocation_candidate_v01:"
SUPERSESSION_CANDIDATE_PROFILE_ID_V01 = (
    "action_supersession_candidate_v01"
)
SUPERSESSION_CANDIDATE_DOMAIN_V01 = (
    "HEDGEHOG_ACTION_SUPERSESSION_CANDIDATE_V01"
)
SUPERSESSION_CANDIDATE_PREFIX_V01 = "supersession_candidate_v01:"
ACCEPTED_REVOCATION_BINDING_DOMAIN_V01 = (
    "HEDGEHOG_ACCEPTED_REVOCATION_BINDING_V01"
)
ACCEPTED_REVOCATION_BINDING_PREFIX_V01 = "accepted_revocation_v01:"
ACCEPTED_SUPERSESSION_BINDING_DOMAIN_V01 = (
    "HEDGEHOG_ACCEPTED_SUPERSESSION_BINDING_V01"
)
ACCEPTED_SUPERSESSION_BINDING_PREFIX_V01 = "accepted_supersession_v01:"
ACTION_INVALIDATION_EVIDENCE_PROFILE_ID_V01 = (
    "action_invalidation_evidence_profile_v01"
)
ACTION_INVALIDATION_EVIDENCE_DOMAIN_V01 = (
    "HEDGEHOG_ACTION_INVALIDATION_EVIDENCE_V01"
)
ACTION_INVALIDATION_VALIDATION_STATUS_V01 = "LOCAL_VALIDATION_PASS"
ACTION_INVALIDATION_CLASSES_V01 = (
    "DEPENDENCY_CHANGED",
    "DEPENDENCY_STALE",
    "ROOT_BOUND_KILL_SWITCH",
    "MANUAL_CANCEL_EVIDENCE",
    "ROOT_REVOCATION",
    "ROOT_SUPERSESSION",
)
ACTION_INVALIDATION_AUTHORITY_EFFECTS_V01 = (
    "DETERMINISTIC_BLOCK",
    "ROOT_REVOCATION",
    "ROOT_SUPERSESSION",
)
_ACTION_COMMIT_PACKET_IDENTITY_PROFILE_ID_V01 = (
    "action_commit_packet_identity_profile_v01"
)
_ACCEPTED_REVOCATION_BINDING_VALIDATOR_PROFILE_ID_V01 = (
    "accepted_revocation_binding_v01"
)
_ACCEPTED_SUPERSESSION_BINDING_VALIDATOR_PROFILE_ID_V01 = (
    "accepted_supersession_binding_v01"
)
_ROOT_DECISION_RESULT_VALIDATOR_PROFILE_ID_V01 = "root_decision_result_v01"

TEMPORAL_OUTCOME_NOT_YET_VALID_V01 = "NOT_YET_VALID"
TEMPORAL_OUTCOME_VALID_V01 = "TEMPORALLY_VALID"
TEMPORAL_OUTCOME_EXPIRED_V01 = "EXPIRED"

EFFECT_PARAMETER_VALUE_TYPES_V01 = (
    "TEXT",
    "DECIMAL",
    "INTEGER",
    "BOOLEAN",
    "REFERENCE",
)
DEPENDENCY_REQUIREMENT_CLASSES_V01 = ("MANDATORY", "OPTIONAL")
AUTHORITY_RETRY_POLICIES_V01 = ("NO_RETRY", "NON_CONSUMING_RETRY")
AUTHORITY_SUPERSESSION_POLICIES_V01 = ("ROOT_DECISION_ONLY",)
RESERVED_CONSEQUENTIAL_PARAMETER_NAMES_V01 = (
    "amount_decimal",
    "currency_code",
    "quantity_decimal",
)

_LEGACY_FIREWALL_VOCABULARY_V01 = MappingProxyType(
    {
        ("adapter", ADAPTER_MOCK_BANK_SANDBOX): (
            "mock_adapter:mock_bank_sandbox"
        ),
        ("adapter", ADAPTER_BANK_A_MOCK): "mock_adapter:bank_a_mock",
        ("action", ACTION_MOCK_SUPPLIER_A_PAYMENT_INTENT): (
            "mock_action:mock_supplier_a_payment_intent"
        ),
        ("action", ACTION_MOCK_SUPPLIER_A_PAYMENT_ORDER): (
            "mock_action:mock_supplier_a_payment_order"
        ),
    }
)
_NEVER_MAP_LEGACY_IDENTIFIERS_V01 = (
    ADAPTER_REAL_BANK,
    ADAPTER_REAL_SUPPLIER_API,
    ADAPTER_REAL_WAREHOUSE_API,
    ACTION_REAL_PAYMENT,
    ACTION_REAL_BANK_TRANSFER,
    ACTION_SHIPMENT_RELEASE,
    ACTION_SUPPLIER_B_PAYMENT,
)


@dataclass(frozen=True)
class CanonicalExecutionTimeV01:
    value: int


@dataclass(frozen=True)
class ActionSubjectScopeProfileV01:
    included_subject_refs: tuple[str, ...]
    excluded_subject_refs: tuple[str, ...]


@dataclass(frozen=True)
class ActionTargetScopeProfileV01:
    included_target_refs: tuple[str, ...]
    excluded_target_refs: tuple[str, ...]


@dataclass(frozen=True)
class ActionPermissionScopeProfileV01:
    allowed_action_classes: tuple[str, ...]
    forbidden_action_classes: tuple[str, ...]
    allowed_adapter_ids: tuple[str, ...]
    forbidden_adapter_ids: tuple[str, ...]
    required_approval_refs: tuple[str, ...]
    prohibited_effect_classes: tuple[str, ...]


@dataclass(frozen=True)
class ActionEffectParameterRecordV01:
    parameter_name: str
    value_type: str
    value: str | int | bool


@dataclass(frozen=True)
class ActionEffectParametersProfileV01:
    effect_class: str
    parameter_records: tuple[ActionEffectParameterRecordV01, ...]


@dataclass(frozen=True)
class ActionAdapterBindingProfileV01:
    corridor_class: str
    adapter_id: str
    adapter_kind: str
    adapter_version: str
    mock_only: bool = True


@dataclass(frozen=True)
class DependencySetCandidateRecordV01:
    dependency_id: str
    dependency_class: str
    evidence_ref: str
    content_sha256: str
    requirement_class: str
    time_envelope_id: str | None
    freshness_policy_id: str | None
    source_provenance_refs: tuple[str, ...]
    expected_accepting_local_root_id: str


@dataclass(frozen=True)
class DependencySetCandidateV01:
    dependency_records: tuple[DependencySetCandidateRecordV01, ...]


@dataclass(frozen=True)
class ActionDependencyCurrentObservationV01:
    observation_profile_id: str
    dependency_id: str
    evidence_ref: str
    observed_content_sha256: str
    time_envelope_id: str
    freshness_policy_id: str
    source_provenance_refs: tuple[str, ...]
    valid_from_utc: int
    valid_to_utc: int
    observed_at_utc: int
    observation_context_id: str
    observation_id: str


@dataclass(frozen=True)
class PacketDependencyAcceptanceBindingV01:
    dependency_set_candidate_fingerprint: str
    root_packet_authorization_candidate_id: str
    source_root_decision_id: str
    source_root_decision_hash: str
    owning_local_root_id: str
    packet_id: str
    accepted_status: str
    packet_dependency_acceptance_binding_id: str


@dataclass(frozen=True)
class ActionTemporalAuthorityProfileV01:
    issued_at_utc: int
    expires_at_utc: int
    ttl_seconds: int
    temporal_policy_version: str


@dataclass(frozen=True)
class TemporalEvaluationV01:
    outcome: str
    executable: bool


@dataclass(frozen=True)
class PacketTTLCompatibilityProjectionV01:
    temporal_authority: ActionTemporalAuthorityProfileV01
    evaluation: TemporalEvaluationV01


@dataclass(frozen=True)
class LogicalTimeBridgeV01:
    bridge_id: str
    origin_utc_epoch_seconds: int
    seconds_per_tick: int
    bridge_policy_version: str


@dataclass(frozen=True)
class ActionAuthorityPolicyProfileV01:
    policy_version: str
    owning_local_root_id: str
    authority_rule_refs: tuple[str, ...]
    kill_switch_condition_refs: tuple[str, ...]
    retry_policy: str
    supersession_policy: str
    logical_effect_namespace: str
    allowed_logical_effect_classes: tuple[str, ...]
    allowed_business_object_namespaces: tuple[str, ...]
    allowed_corridor_classes: tuple[str, ...]


@dataclass(frozen=True)
class ActionBusinessObjectIdentityProfileV01:
    business_object_class: str
    business_object_namespace: str
    business_object_ref: str
    owning_effect_root_id: str


@dataclass(frozen=True)
class ActionConsequentialEffectParametersProfileV01:
    amount_decimal: str | None
    currency_code: str | None
    quantity_decimal: str | None
    parameter_records: tuple[ActionEffectParameterRecordV01, ...]


@dataclass(frozen=True)
class RootOwnedLogicalEffectIntentV01:
    owning_effect_root_id: str
    transaction_id: str | None
    logical_effect_class: str
    normalized_subject_scope: ActionSubjectScopeProfileV01
    normalized_target_scope: ActionTargetScopeProfileV01
    normalized_business_object_identity: ActionBusinessObjectIdentityProfileV01
    normalized_consequential_effect_parameters: (
        ActionConsequentialEffectParametersProfileV01
    )
    logical_effect_namespace: str
    root_owned_intent_id: str


@dataclass(frozen=True)
class ActionIdempotencyIdentityV01:
    owning_effect_root_id: str
    transaction_id: str | None
    root_owned_intent_id: str | None
    logical_effect_class: str
    normalized_subject_scope: ActionSubjectScopeProfileV01
    normalized_target_scope: ActionTargetScopeProfileV01
    normalized_business_object_identity: ActionBusinessObjectIdentityProfileV01
    normalized_consequential_effect_parameters: (
        ActionConsequentialEffectParametersProfileV01
    )
    logical_effect_namespace: str
    idempotency_key: str


@dataclass(frozen=True)
class RootBoundPacketAuthorizationCandidateV01:
    owning_local_root_id: str
    transaction_id: str | None
    root_owned_intent_id: str
    effect_class: str
    normalized_subject_scope: ActionSubjectScopeProfileV01
    normalized_target_scope: ActionTargetScopeProfileV01
    normalized_permission_scope: ActionPermissionScopeProfileV01
    normalized_effect_parameters_fingerprint: str
    corridor_class: str
    adapter_binding: ActionAdapterBindingProfileV01
    dependency_set_candidate_fingerprint: str
    temporal_authority_fingerprint: str
    policy_version: str | None
    authority_policy_fingerprint: str
    predecessor_packet_id: str | None
    supersession_reason_class: str | None
    root_packet_authorization_candidate_id: str


@dataclass(frozen=True)
class ActionCommitPacketIdentityResultV01:
    packet_id: str
    material: CanonicalMaterialV01


@dataclass(frozen=True)
class TransitionEvidenceBindingV01:
    transition_evidence_binding_id: str
    evidence_code: str
    evidence_ref: str
    evidence_sha256: str
    validator_profile_id: str
    validation_status: str


@dataclass(frozen=True)
class ActionExecutionAttemptIdentityV01:
    execution_attempt_id: str
    packet_id: str
    idempotency_key: str
    attempt_ordinal: int
    evaluation_context_id: str
    material: CanonicalMaterialV01


@dataclass(frozen=True)
class ActionPacketTransitionEventV01:
    transition_event_id: str
    transition_profile_version: str
    transition_registry_id: str
    transition_rule_id: str
    packet_id: str
    idempotency_key: str
    previous_transition_event_id: str | None
    source_state: str
    target_state: str
    transition_class_code: str
    performed_by_component: str
    owning_local_root_id: str
    root_decision_ref: str | None
    transition_evidence_bindings: tuple[TransitionEvidenceBindingV01, ...]
    reason_code: str
    dependency_set_candidate_fingerprint: str
    temporal_authority_fingerprint: str
    evaluation_time: int
    evaluation_time_source: str
    evaluation_context_id: str
    execution_attempt_id: str | None
    effect_consumption_class: str
    receipt_ref: str | None


@dataclass(frozen=True)
class EffectFirewallVocabularyProjectionV01:
    identifier_kind: str
    raw_identifier: str
    canonical_identifier: str
    compatibility_mode: bool


@dataclass(frozen=True)
class SupplierActionCommitPacketCanonicalProjectionV01:
    transaction_id: str
    owning_local_root_id: str
    canonical_permission_ref: str
    selected_legacy_action: str
    selected_canonical_action: str
    source_packet: ActionCommitPacketV02
    normalized_subject_scope: ActionSubjectScopeProfileV01
    normalized_target_scope: ActionTargetScopeProfileV01
    normalized_permission_scope: ActionPermissionScopeProfileV01
    normalized_effect_parameters: ActionEffectParametersProfileV01
    normalized_effect_parameters_fingerprint: str
    adapter_binding: ActionAdapterBindingProfileV01
    dependency_candidate: DependencySetCandidateV01
    dependency_set_candidate_fingerprint: str
    temporal_authority: ActionTemporalAuthorityProfileV01
    temporal_authority_fingerprint: str
    evaluation_time: int
    evaluation_time_source: str
    evaluation_context_id: str
    temporal_evaluation: TemporalEvaluationV01
    authority_policy: ActionAuthorityPolicyProfileV01
    authority_policy_fingerprint: str
    business_object_identity: ActionBusinessObjectIdentityProfileV01
    consequential_effect_parameters: (
        ActionConsequentialEffectParametersProfileV01
    )
    logical_intent: RootOwnedLogicalEffectIntentV01
    idempotency_identity: ActionIdempotencyIdentityV01
    authorization_candidate: RootBoundPacketAuthorizationCandidateV01
    raw_allowed_actions: tuple[str, ...]
    raw_forbidden_actions: tuple[str, ...]
    raw_allowed_adapters: tuple[str, ...]
    raw_forbidden_adapters: tuple[str, ...]
    human_approval_evidence_ref: str
    advisory_drs_refs: tuple[str, ...]
    advisory_avf_refs: tuple[str, ...]
    advisory_bsep_ref: str


@dataclass(frozen=True)
class RevocationCandidateV01:
    candidate_profile_id: str
    owning_local_root_id: str
    packet_id: str
    source_authorization_decision_id: str
    idempotency_key: str
    revocation_reason_class: str
    evidence_refs: tuple[str, ...]
    evidence_hashes: tuple[str, ...]
    evaluation_time: int
    policy_fingerprint: str
    revocation_candidate_id: str


@dataclass(frozen=True)
class SupersessionCandidateV01:
    owning_local_root_id: str
    predecessor_packet_id: str
    successor_packet_authorization_candidate_id: str
    stable_logical_intent_id: str
    idempotency_key: str
    supersession_reason_class: str
    policy_fingerprint: str
    supersession_candidate_id: str


@dataclass(frozen=True)
class RootDecisionCandidateProjectionV01:
    candidate_kind: str
    projected_candidate_id: str
    root_decision_kernel: RootDecisionKernelV01
    root_decision_input: RootDecisionInputV01
    root_decision_result: RootDecisionResultV01
    source_root_decision_hash: str


@dataclass(frozen=True)
class AcceptedRevocationBindingV01:
    revocation_candidate_id: str
    revocation_root_decision_id: str
    revocation_root_decision_hash: str
    owning_local_root_id: str
    packet_id: str
    prior_authorization_decision_id: str
    accepted_revocation_binding_id: str


@dataclass(frozen=True)
class AcceptedSupersessionBindingV01:
    supersession_candidate_id: str
    supersession_root_decision_id: str
    supersession_root_decision_hash: str
    owning_local_root_id: str
    predecessor_packet_id: str
    prior_authorization_decision_id: str
    accepted_supersession_binding_id: str


@dataclass(frozen=True)
class ActionInvalidationEvidenceV01:
    profile_id: str
    source_invalidation_event_ref: str
    packet_id: str
    dependency_id: str
    invalidation_class: str
    evidence_ref: str
    evidence_sha256: str
    observed_status: str
    time_envelope_id: str
    freshness_policy_id: str
    owning_local_root_id: str
    accepted_by_local_root_id: str
    acceptance_root_decision_id: str | None
    acceptance_root_decision_hash: str | None
    validation_status: str
    authority_effect: str
    root_decision_ref: str | None
    evaluation_time: int
    evaluation_time_source: str
    evaluation_context_id: str
    invalidation_evidence_id: str


@dataclass(frozen=True)
class _ActionPacketInvalidationContextV01:
    invalidation_evidence: ActionInvalidationEvidenceV01
    revocation_candidate: RevocationCandidateV01 | None
    revocation_root_projection: RootDecisionCandidateProjectionV01 | None
    accepted_revocation_binding: AcceptedRevocationBindingV01 | None
    supersession_candidate: SupersessionCandidateV01 | None
    supersession_root_projection: RootDecisionCandidateProjectionV01 | None
    supersession_successor_packet_id: str | None
    accepted_supersession_binding: AcceptedSupersessionBindingV01 | None


@dataclass(frozen=True)
class SupplierRootBoundActionCommitPacketV02ProjectionV01:
    canonical_projection: SupplierActionCommitPacketCanonicalProjectionV01
    root_decision_projection: RootDecisionCandidateProjectionV01
    packet_identity: ActionCommitPacketIdentityResultV01
    dependency_acceptance_binding: PacketDependencyAcceptanceBindingV01
    packet: ActionCommitPacketV02


@dataclass(frozen=True)
class ActionPacketEffectFirewallProjectionV01:
    projection_profile_id: str
    packet_id: str
    registry_id: str
    pending_transition_event_id: str
    execution_attempt_id: str
    corridor_id: str
    corridor_step_id: str
    corridor_class: str
    transaction_id: str
    target_root_id: str
    root_decision_id: str
    selected_candidate_id: str
    permission_ref: str
    allowed_adapter_ids: tuple[str, ...]
    allowed_action_kinds: tuple[str, ...]
    root_scope_refs: tuple[str, ...]
    maximum_expires_at_tick: int
    request_kind: str
    adapter_id: str
    action_kind: str
    scope_refs: tuple[str, ...]
    issued_at_tick: int
    expires_at_tick: int
    current_tick: int
    idempotency_key: str
    mock_only: bool
    effect_access_owner: str
    logical_time_bridge_id: str
    attempt_evaluation_time: int
    attempt_evaluation_time_source: str
    attempt_evaluation_context_id: str
    eligibility_evaluation_time: int
    eligibility_evaluation_time_source: str
    eligibility_evaluation_context_id: str
    latest_disposition_event_id: str
    dependency_acceptance_binding_id: str
    dependency_observation_ids: tuple[str, ...]
    authority_policy_fingerprint: str
    temporal_authority_fingerprint: str


@dataclass(frozen=True)
class ActionPacketFulfillmentAttemptEvidenceV01:
    evidence_profile_id: str
    packet_id: str
    registry_id_before: str
    pending_transition_event_id: str
    execution_attempt_id: str
    attempt_observation_ordinal: int
    corridor_id: str
    corridor_step_id: str
    logical_time_bridge_id: str
    dependency_observation_ids: tuple[str, ...]
    projection_sha256: str | None
    firewall_id: str | None
    request_id: str | None
    decision_id: str | None
    capability_id: str | None
    adapter_id: str | None
    action_kind: str | None
    invocation_relation_code: str
    outcome_class: str
    reason_code: str
    adapter_invoked: bool
    adapter_call_count: int
    firewall_state_sha256_before: str | None
    firewall_state_sha256_after: str | None
    receipt_ref: str | None
    receipt_sha256: str | None
    disposition_before: str
    reservation_owner_packet_id_before: str
    latest_disposition_event_id_before: str | None
    disposition_history_sha256_before: str
    attempt_evaluation_time: int
    attempt_evaluation_time_source: str
    attempt_evaluation_context_id: str
    eligibility_evaluation_time: int
    eligibility_evaluation_time_source: str
    eligibility_evaluation_context_id: str
    real_world_effects_count: int
    attempt_evidence_id: str


@dataclass(frozen=True)
class _ActionPacketEffectAttemptPreparationV01:
    projection: ActionPacketEffectFirewallProjectionV01
    firewall: _EffectFirewallV01
    request: _EffectRequestV01
    decision: _EffectFirewallDecisionV01


@dataclass(frozen=True)
class _ActionPacketHistoricalEffectAuthorizationV01:
    projection: ActionPacketEffectFirewallProjectionV01
    firewall_id: str
    request: _EffectRequestV01
    decision: _EffectFirewallDecisionV01
    expected_capability_id: str | None
    firewall_state_sha256_before: str
    firewall_state_sha256_consumed: str | None


@dataclass(frozen=True)
class _ActionPacketFulfillmentAttemptContextV01:
    attempt_evidence: ActionPacketFulfillmentAttemptEvidenceV01
    projection: ActionPacketEffectFirewallProjectionV01 | None
    corridor: ContractFulfillmentCorridorV01
    corridor_step: CorridorStepV01
    current_dependency_observations: tuple[
        ActionDependencyCurrentObservationV01,
        ...,
    ]
    logical_time_bridge: LogicalTimeBridgeV01
    request: _EffectRequestV01 | None
    decision: _EffectFirewallDecisionV01 | None
    receipt: _KernelArtifactV01 | None


@dataclass(frozen=True)
class ActionPacketLifecycleEntryV01:
    root_bound_genesis: SupplierRootBoundActionCommitPacketV02ProjectionV01
    transition_registry_id: str
    transition_events: tuple[ActionPacketTransitionEventV01, ...]


@dataclass(frozen=True)
class IdempotencyDispositionEventV01:
    idempotency_disposition_event_id: str
    event_profile_version: str
    idempotency_key: str
    event_class: str
    from_disposition: str
    to_disposition: str
    from_owner_packet_id: str | None
    to_owner_packet_id: str | None
    previous_disposition_event_id: str | None
    cause_transition_event_ids: tuple[str, ...]
    root_decision_ref: str | None
    predecessor_packet_id: str | None
    successor_packet_id: str | None
    evidence_refs: tuple[str, ...]
    evaluation_time: int
    evaluation_time_source: str
    evaluation_context_id: str


@dataclass(frozen=True)
class IdempotencyDispositionStateV01:
    idempotency_key: str
    disposition: str
    reservation_owner_packet_id: str | None
    latest_disposition_event_id: str | None
    event_count: int


@dataclass(frozen=True)
class ActionPacketLifecycleStateV01:
    packet_id: str
    idempotency_key: str
    lifecycle_state: str
    failed_provenance: str | None
    transition_event_count: int
    latest_transition_event_id: str | None
    execution_attempt_count: int
    idempotency_disposition: str
    reservation_owner_packet_id: str | None
    latest_disposition_event_id: str | None
    terminal_receipt_ref: str | None
    lifecycle_terminal: bool
    eligible_for_corridor_revalidation: bool
    executable: bool
    registry_is_authority: bool
    registry_grants_permission: bool
    real_world_effects_count: int
    reason_codes: tuple[str, ...]


@dataclass(frozen=True)
class ActionPacketRecordedTransitionReplayV01:
    transition_event_id: str
    transition_rule_id: str
    source_state: str
    target_state: str
    evaluation_time: int
    evaluation_time_source: str
    evaluation_context_id: str
    execution_attempt_id: str | None
    effect_consumption_class: str
    receipt_ref: str | None


@dataclass(frozen=True)
class ActionPacketLifecycleReplayReportV01:
    replay_profile_id: str
    registry_id: str
    packet_id: str
    transition_registry_id: str
    source_root_decision_id: str
    source_root_decision_hash: str
    rebuilt_packet_id: str
    rebuilt_idempotency_key: str
    recorded_transitions: tuple[ActionPacketRecordedTransitionReplayV01, ...]
    disposition_event_ids: tuple[str, ...]
    invalidation_evidence_ids: tuple[str, ...]
    fulfillment_attempt_evidence_ids: tuple[str, ...]
    reconstructed_state: ActionPacketLifecycleStateV01
    transition_history_sha256: str
    disposition_history_sha256: str
    invalidation_history_sha256: str
    fulfillment_history_sha256: str
    historical_temporal_replay_pass: bool
    t24_reserved_history_replay_pass: bool
    distinct_firewall_attempt_replay_pass: bool
    registry_unchanged: bool
    creates_authority: bool
    creates_permission: bool
    creates_packet: bool
    creates_receipt: bool
    adapter_calls: int
    real_world_effects_count: int


@dataclass(frozen=True)
class ActionPacketPresentEligibilityInspectionV01:
    inspection_profile_id: str
    registry_id: str
    packet_id: str
    evaluation_time: int
    evaluation_time_source: str
    evaluation_context_id: str
    historical_state: ActionPacketLifecycleStateV01
    present_eligibility_status: str
    present_executable: bool
    retry_eligible: bool
    reason_codes: tuple[str, ...]
    transition_history_sha256: str
    disposition_history_sha256: str
    historical_result_unchanged: bool
    creates_authority: bool
    creates_permission: bool
    creates_packet: bool
    creates_receipt: bool
    adapter_calls: int
    real_world_effects_count: int


def _canonical_absent_v01() -> Mapping[str, str]:
    return ABSENT_V01


def is_absent_v01(value: object) -> bool:
    return value is ABSENT_V01


def _result_v01(reasons: list[str]) -> tuple[bool, tuple[str, ...]]:
    return not reasons, tuple(dict.fromkeys(reasons))


def _reason_v01(reasons: list[str], reason: str) -> None:
    if reason not in reasons:
        reasons.append(reason)


def _stable_exception_reason_v01(
    exc: ValueError,
    *,
    fallback: str,
) -> str:
    if (
        len(exc.args) == 1
        and type(exc.args[0]) is str
        and re.fullmatch(r"[a-z][a-z0-9_]*", exc.args[0]) is not None
    ):
        return exc.args[0]
    return fallback


def validate_identity_text_v01(
    value: object,
    *,
    allow_empty: bool = False,
) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if type(allow_empty) is not bool:
        return False, ("identity_text_allow_empty_type_invalid",)
    if type(value) is not str:
        return False, ("identity_text_type_invalid",)
    try:
        value.encode("utf-8", errors="strict")
    except UnicodeError:
        return False, ("identity_text_surrogate_invalid",)
    if "\x00" in value:
        _reason_v01(reasons, "identity_text_nul_invalid")
    if not allow_empty and not value:
        _reason_v01(reasons, "identity_text_empty")
    try:
        if unicodedata.normalize("NFC", value) != value:
            _reason_v01(reasons, "identity_text_not_nfc")
    except Exception:
        _reason_v01(reasons, "identity_text_normalization_invalid")
    return _result_v01(reasons)


def normalize_identity_text_v01(
    value: object,
    *,
    allow_empty: bool = False,
) -> str:
    if type(allow_empty) is not bool:
        raise ValueError("identity_text_allow_empty_type_invalid")
    if type(value) is not str:
        raise ValueError("identity_text_type_invalid")
    try:
        normalized = unicodedata.normalize("NFC", value)
        normalized.encode("utf-8", errors="strict")
    except Exception:
        raise ValueError("identity_text_normalization_invalid") from None
    valid, reasons = validate_identity_text_v01(
        normalized,
        allow_empty=allow_empty,
    )
    if not valid:
        raise ValueError(reasons[0])
    return normalized


def validate_lowercase_sha256_hex_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    if type(value) is not str:
        return False, ("sha256_type_invalid",)
    try:
        valid = re.fullmatch(LOWERCASE_SHA256_REGEX_V01, value) is not None
    except Exception:
        valid = False
    return (True, ()) if valid else (False, ("sha256_format_invalid",))


def validate_signed_int64_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    if type(value) is not int:
        return False, ("int64_type_invalid",)
    if value < INT64_MIN_V01 or value > INT64_MAX_V01:
        return False, ("int64_range_invalid",)
    return True, ()


def validate_positive_int_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    valid, reasons = validate_signed_int64_v01(value)
    if not valid:
        return valid, reasons
    if value <= 0:
        return False, ("positive_int_invalid",)
    return True, ()


def canonicalize_set_like_string_tuple_v01(value: object) -> tuple[str, ...]:
    if type(value) is not tuple:
        raise ValueError("set_like_tuple_type_invalid")
    normalized: list[str] = []
    for item in value:
        normalized.append(normalize_identity_text_v01(item))
    if len(normalized) != len(set(normalized)):
        raise ValueError("set_like_tuple_duplicate")
    return tuple(sorted(normalized, key=lambda item: item.encode("utf-8")))


def validate_set_like_string_tuple_v01(
    value: object,
    *,
    require_non_empty: bool = False,
) -> tuple[bool, tuple[str, ...]]:
    if type(require_non_empty) is not bool:
        return False, ("set_like_tuple_require_non_empty_type_invalid",)
    try:
        canonical = canonicalize_set_like_string_tuple_v01(value)
    except ValueError as exc:
        return False, (
            _stable_exception_reason_v01(
                exc,
                fallback="set_like_tuple_invalid",
            ),
        )
    except Exception:
        return False, ("set_like_tuple_invalid",)
    if require_non_empty and not canonical:
        return False, ("set_like_tuple_empty",)
    if canonical != value:
        return False, ("set_like_tuple_not_canonical",)
    return True, ()


def preserve_ordered_string_tuple_v01(value: object) -> tuple[str, ...]:
    if type(value) is not tuple:
        raise ValueError("ordered_tuple_type_invalid")
    return tuple(normalize_identity_text_v01(item) for item in value)


def _validate_ordered_string_tuple_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    try:
        canonical = preserve_ordered_string_tuple_v01(value)
    except ValueError as exc:
        return False, (
            _stable_exception_reason_v01(
                exc,
                fallback="ordered_tuple_invalid",
            ),
        )
    except Exception:
        return False, ("ordered_tuple_invalid",)
    if canonical != value:
        return False, ("ordered_tuple_not_canonical",)
    return True, ()


def _validate_canonical_material_structure_v01(
    material: object,
) -> tuple[bool, tuple[str, ...], tuple[str, ...]]:
    reasons: list[str] = []
    if type(material) is not tuple:
        return False, ("canonical_material_type_invalid",), ()
    if not material:
        return False, ("canonical_material_empty",), ()
    fields: list[str] = []
    for pair in material:
        if type(pair) is not tuple or len(pair) != 2:
            _reason_v01(reasons, "canonical_material_pair_invalid")
            continue
        name = pair[0]
        valid_name, _ = validate_identity_text_v01(name)
        if not valid_name:
            _reason_v01(reasons, "canonical_material_field_name_invalid")
            continue
        fields.append(name)
        if not _canonical_identity_value_is_valid_v01(pair[1]):
            _reason_v01(reasons, "canonical_material_value_invalid")
    if len(fields) != len(set(fields)):
        _reason_v01(reasons, "canonical_material_field_duplicate")
    valid, reason_tuple = _result_v01(reasons)
    return valid, reason_tuple, tuple(fields)


def validate_canonical_profile_material_v01(
    material: object,
    *,
    expected_field_names: object = None,
) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    if type(expected_field_names) is not tuple:
        return False, ("canonical_material_expected_fields_type_invalid",)
    if not expected_field_names:
        return False, ("canonical_material_expected_fields_empty",)
    expected_names: list[str] = []
    for name in expected_field_names:
        valid_name, _ = validate_identity_text_v01(name)
        if not valid_name:
            return False, ("canonical_material_expected_field_name_invalid",)
        expected_names.append(name)
    if len(expected_names) != len(set(expected_names)):
        return False, ("canonical_material_expected_field_duplicate",)
    structure_valid, structure_reasons, fields = (
        _validate_canonical_material_structure_v01(material)
    )
    if not structure_valid:
        reasons.extend(structure_reasons)
    if tuple(fields) != tuple(expected_names):
        if len(fields) < len(expected_names):
            _reason_v01(reasons, "canonical_material_field_missing")
        if len(fields) > len(expected_names):
            _reason_v01(reasons, "canonical_material_field_unknown")
        _reason_v01(reasons, "canonical_material_field_order_invalid")
    return _result_v01(reasons)


def _canonical_identity_value_is_valid_v01(value: object) -> bool:
    if value is ABSENT_V01:
        return True
    if type(value) is str:
        return validate_identity_text_v01(value, allow_empty=True)[0]
    if type(value) is bool:
        return True
    if type(value) is int:
        return validate_signed_int64_v01(value)[0]
    if type(value) is tuple:
        return all(_canonical_identity_value_is_valid_v01(item) for item in value)
    return False


def canonical_material_bytes_v01(material: object) -> bytes:
    structurally_valid, structural_reasons, field_names = (
        _validate_canonical_material_structure_v01(material)
    )
    if not structurally_valid:
        raise ValueError(structural_reasons[0])
    valid, reasons = validate_canonical_profile_material_v01(
        material,
        expected_field_names=field_names,
    )
    if not valid:
        raise ValueError(reasons[0])
    try:
        return canonical_json_bytes_v01(material)
    except Exception:
        raise ValueError("canonical_material_encoding_invalid") from None


def build_domain_separated_identity_v01(
    *,
    domain: str,
    prefix: str,
    material: CanonicalMaterialV01,
) -> str:
    valid_domain, domain_reasons = validate_identity_text_v01(domain)
    valid_prefix, prefix_reasons = validate_identity_text_v01(prefix)
    if not valid_domain:
        raise ValueError(domain_reasons[0])
    if not valid_prefix:
        raise ValueError(prefix_reasons[0])
    payload = canonical_material_bytes_v01(material)
    digest = domain_separated_sha256_hex_v01(
        domain=domain,
        payload=payload,
    )
    return prefix + digest


def validate_prefixed_sha256_identity_v01(
    value: object,
    *,
    prefix: object = None,
) -> tuple[bool, tuple[str, ...]]:
    valid_prefix, _ = validate_identity_text_v01(prefix)
    if not valid_prefix:
        return False, ("prefixed_identity_prefix_type_invalid",)
    if type(value) is not str:
        return False, ("prefixed_identity_type_invalid",)
    if not value.startswith(prefix):
        return False, ("prefixed_identity_prefix_invalid",)
    valid, _ = validate_lowercase_sha256_hex_v01(value[len(prefix) :])
    return (True, ()) if valid else (False, ("prefixed_identity_digest_invalid",))


def validate_canonical_decimal_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    if type(value) is not str:
        return False, ("canonical_decimal_type_invalid",)
    try:
        valid = re.fullmatch(CANONICAL_DECIMAL_REGEX_V01, value) is not None
    except Exception:
        valid = False
    if not valid:
        return False, ("canonical_decimal_format_invalid",)
    return True, ()


def normalize_legacy_decimal_v01(value: object) -> str:
    if type(value) is not str:
        raise ValueError("legacy_decimal_type_invalid")
    try:
        if re.fullmatch(LEGACY_PLAIN_DECIMAL_INPUT_REGEX_V01, value) is None:
            raise ValueError("legacy_decimal_format_invalid")
        decimal_value = Decimal(value)
    except ValueError:
        raise
    except (InvalidOperation, ArithmeticError):
        raise ValueError("legacy_decimal_format_invalid") from None
    if not decimal_value.is_finite():
        raise ValueError("legacy_decimal_non_finite")
    if decimal_value.is_zero() and value.startswith("-"):
        raise ValueError("legacy_decimal_negative_zero")
    if "." in value:
        normalized = value.rstrip("0").rstrip(".")
    else:
        normalized = value
    valid, reasons = validate_canonical_decimal_v01(normalized)
    if not valid:
        raise ValueError(reasons[0])
    return normalized


def validate_legacy_decimal_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    try:
        normalize_legacy_decimal_v01(value)
    except ValueError as exc:
        return False, (
            _stable_exception_reason_v01(
                exc,
                fallback="legacy_decimal_invalid",
            ),
        )
    except Exception:
        return False, ("legacy_decimal_invalid",)
    return True, ()


def validate_canonical_execution_time_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    if type(value) is CanonicalExecutionTimeV01:
        return validate_signed_int64_v01(value.value)
    return validate_signed_int64_v01(value)


def build_canonical_execution_time_v01(
    value: object,
) -> CanonicalExecutionTimeV01:
    valid, reasons = validate_signed_int64_v01(value)
    if not valid:
        raise ValueError(reasons[0])
    return CanonicalExecutionTimeV01(value=value)


def parse_utc_timestamp_v01(value: object) -> int:
    if type(value) is not str:
        raise ValueError("timestamp_type_invalid")
    try:
        if re.fullmatch(UTC_TIMESTAMP_COMPATIBILITY_REGEX_V01, value) is None:
            raise ValueError("timestamp_format_invalid")
        year = int(value[0:4])
        month = int(value[5:7])
        day_value = int(value[8:10])
        hour = int(value[11:13])
        minute = int(value[14:16])
        second = int(value[17:19])
        if year < 1 or hour > 23 or minute > 59 or second > 59:
            raise ValueError("timestamp_component_invalid")
        parsed_date = date(year, month, day_value)
        epoch_date = date(1970, 1, 1)
        epoch_seconds = (
            (parsed_date - epoch_date).days * 86400
            + hour * 3600
            + minute * 60
            + second
        )
    except ValueError as exc:
        reason = _stable_exception_reason_v01(
            exc,
            fallback="timestamp_calendar_invalid",
        )
        if reason in ("timestamp_format_invalid", "timestamp_component_invalid"):
            raise
        raise ValueError("timestamp_calendar_invalid") from None
    except Exception:
        raise ValueError("timestamp_invalid") from None
    valid, reasons = validate_signed_int64_v01(epoch_seconds)
    if not valid:
        raise ValueError(reasons[0])
    return epoch_seconds


def validate_utc_timestamp_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    try:
        parse_utc_timestamp_v01(value)
    except ValueError as exc:
        return False, (
            _stable_exception_reason_v01(
                exc,
                fallback="timestamp_invalid",
            ),
        )
    except Exception:
        return False, ("timestamp_invalid",)
    return True, ()


def format_utc_timestamp_v01(epoch_seconds: object) -> str:
    valid, reasons = validate_signed_int64_v01(epoch_seconds)
    if not valid:
        raise ValueError(reasons[0])
    try:
        day_offset, second_of_day = divmod(epoch_seconds, 86400)
        epoch_date = date(1970, 1, 1)
        calendar_date = date.fromordinal(epoch_date.toordinal() + day_offset)
        hour, remainder = divmod(second_of_day, 3600)
        minute, second = divmod(remainder, 60)
        formatted = (
            f"{calendar_date.year:04d}-{calendar_date.month:02d}-"
            f"{calendar_date.day:02d}T{hour:02d}:{minute:02d}:{second:02d}Z"
        )
    except Exception:
        raise ValueError("timestamp_output_range_invalid") from None
    try:
        if parse_utc_timestamp_v01(formatted) != epoch_seconds:
            raise ValueError("timestamp_round_trip_invalid")
    except ValueError as exc:
        raise ValueError(
            _stable_exception_reason_v01(
                exc,
                fallback="timestamp_round_trip_invalid",
            )
        ) from None
    return formatted


def build_action_temporal_authority_profile_v01(
    *,
    issued_at_utc: object,
    expires_at_utc: object,
    ttl_seconds: object,
    temporal_policy_version: object,
) -> ActionTemporalAuthorityProfileV01:
    valid_issued, issued_reasons = validate_signed_int64_v01(issued_at_utc)
    valid_expires, expires_reasons = validate_signed_int64_v01(expires_at_utc)
    valid_ttl, ttl_reasons = validate_positive_int_v01(ttl_seconds)
    try:
        policy = normalize_identity_text_v01(temporal_policy_version)
    except ValueError as exc:
        raise ValueError(
            _stable_exception_reason_v01(
                exc,
                fallback="temporal_policy_version_invalid",
            )
        ) from None
    if not valid_issued:
        raise ValueError(issued_reasons[0])
    if not valid_expires:
        raise ValueError(expires_reasons[0])
    if not valid_ttl:
        raise ValueError(ttl_reasons[0])
    try:
        expected_expires = issued_at_utc + ttl_seconds
    except Exception:
        raise ValueError("temporal_authority_arithmetic_invalid") from None
    valid_sum, _ = validate_signed_int64_v01(expected_expires)
    if not valid_sum:
        raise ValueError("temporal_authority_overflow")
    if expires_at_utc != expected_expires:
        raise ValueError("temporal_authority_inconsistent")
    return ActionTemporalAuthorityProfileV01(
        issued_at_utc=issued_at_utc,
        expires_at_utc=expires_at_utc,
        ttl_seconds=ttl_seconds,
        temporal_policy_version=policy,
    )


def validate_action_temporal_authority_profile_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    if type(value) is not ActionTemporalAuthorityProfileV01:
        return False, ("temporal_authority_type_invalid",)
    try:
        rebuilt = build_action_temporal_authority_profile_v01(
            issued_at_utc=value.issued_at_utc,
            expires_at_utc=value.expires_at_utc,
            ttl_seconds=value.ttl_seconds,
            temporal_policy_version=value.temporal_policy_version,
        )
    except ValueError as exc:
        return False, (
            _stable_exception_reason_v01(
                exc,
                fallback="temporal_authority_invalid",
            ),
        )
    except Exception:
        return False, ("temporal_authority_invalid",)
    return (True, ()) if rebuilt == value else (
        False,
        ("temporal_authority_not_canonical",),
    )


def action_temporal_authority_material_v01(
    value: ActionTemporalAuthorityProfileV01,
) -> CanonicalMaterialV01:
    valid, reasons = validate_action_temporal_authority_profile_v01(value)
    if not valid:
        raise ValueError(reasons[0])
    return (
        ("issued_at_utc", value.issued_at_utc),
        ("expires_at_utc", value.expires_at_utc),
        ("ttl_seconds", value.ttl_seconds),
        ("temporal_policy_version", value.temporal_policy_version),
    )


def build_temporal_authority_fingerprint_v01(
    value: ActionTemporalAuthorityProfileV01,
) -> str:
    material = action_temporal_authority_material_v01(value)
    return domain_separated_sha256_hex_v01(
        domain=ACTION_TEMPORAL_AUTHORITY_DOMAIN_V01,
        payload=canonical_json_bytes_v01(material),
    )


def evaluate_temporal_authority_v01(
    value: object,
    *,
    evaluation_time: object,
) -> TemporalEvaluationV01:
    valid, reasons = validate_action_temporal_authority_profile_v01(value)
    if not valid:
        raise ValueError(reasons[0])
    valid_time, time_reasons = validate_signed_int64_v01(evaluation_time)
    if not valid_time:
        raise ValueError(time_reasons[0])
    if evaluation_time < value.issued_at_utc:
        return TemporalEvaluationV01(
            outcome=TEMPORAL_OUTCOME_NOT_YET_VALID_V01,
            executable=False,
        )
    if evaluation_time >= value.expires_at_utc:
        return TemporalEvaluationV01(
            outcome=TEMPORAL_OUTCOME_EXPIRED_V01,
            executable=False,
        )
    return TemporalEvaluationV01(
        outcome=TEMPORAL_OUTCOME_VALID_V01,
        executable=True,
    )


def project_packet_ttl_compatibility_v01(
    ttl: object,
    *,
    evaluation_time: object,
    temporal_policy_version: object,
) -> PacketTTLCompatibilityProjectionV01:
    if type(ttl) is not PacketTTL:
        raise ValueError("packet_ttl_type_invalid")
    if type(ttl.ttl_valid) is not bool or type(ttl.expired) is not bool:
        raise ValueError("packet_ttl_assertion_type_invalid")
    issued = parse_utc_timestamp_v01(ttl.created_at)
    expires = parse_utc_timestamp_v01(ttl.expires_at)
    temporal = build_action_temporal_authority_profile_v01(
        issued_at_utc=issued,
        expires_at_utc=expires,
        ttl_seconds=ttl.ttl_seconds,
        temporal_policy_version=temporal_policy_version,
    )
    evaluation = evaluate_temporal_authority_v01(
        temporal,
        evaluation_time=evaluation_time,
    )
    if ttl.ttl_valid is not True:
        raise ValueError("packet_ttl_valid_assertion_mismatch")
    derived_expired = evaluation_time >= expires
    if ttl.expired != derived_expired:
        raise ValueError("packet_ttl_expired_assertion_mismatch")
    return PacketTTLCompatibilityProjectionV01(
        temporal_authority=temporal,
        evaluation=evaluation,
    )


def logical_time_bridge_material_v01(
    value: LogicalTimeBridgeV01,
) -> CanonicalMaterialV01:
    return (
        ("bridge_policy_version", value.bridge_policy_version),
        ("origin_utc_epoch_seconds", value.origin_utc_epoch_seconds),
        ("seconds_per_tick", value.seconds_per_tick),
    )


def build_logical_time_bridge_v01(
    *,
    origin_utc_epoch_seconds: object,
    seconds_per_tick: object,
    bridge_policy_version: object,
) -> LogicalTimeBridgeV01:
    valid_origin, origin_reasons = validate_signed_int64_v01(
        origin_utc_epoch_seconds
    )
    valid_scale, scale_reasons = validate_positive_int_v01(seconds_per_tick)
    if not valid_origin:
        raise ValueError(origin_reasons[0])
    if not valid_scale:
        raise ValueError(scale_reasons[0])
    policy = normalize_identity_text_v01(bridge_policy_version)
    provisional = LogicalTimeBridgeV01(
        bridge_id="",
        origin_utc_epoch_seconds=origin_utc_epoch_seconds,
        seconds_per_tick=seconds_per_tick,
        bridge_policy_version=policy,
    )
    digest = domain_separated_sha256_hex_v01(
        domain=ACTION_LOGICAL_TIME_BRIDGE_DOMAIN_V01,
        payload=canonical_json_bytes_v01(
            logical_time_bridge_material_v01(provisional)
        ),
    )
    return LogicalTimeBridgeV01(
        bridge_id=digest,
        origin_utc_epoch_seconds=origin_utc_epoch_seconds,
        seconds_per_tick=seconds_per_tick,
        bridge_policy_version=policy,
    )


def validate_logical_time_bridge_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    if type(value) is not LogicalTimeBridgeV01:
        return False, ("logical_time_bridge_type_invalid",)
    try:
        rebuilt = build_logical_time_bridge_v01(
            origin_utc_epoch_seconds=value.origin_utc_epoch_seconds,
            seconds_per_tick=value.seconds_per_tick,
            bridge_policy_version=value.bridge_policy_version,
        )
    except ValueError as exc:
        return False, (
            _stable_exception_reason_v01(
                exc,
                fallback="logical_time_bridge_invalid",
            ),
        )
    except Exception:
        return False, ("logical_time_bridge_invalid",)
    if rebuilt != value:
        return False, ("logical_time_bridge_identity_mismatch",)
    return True, ()


def logical_tick_to_epoch_seconds_v01(
    bridge: object,
    logical_tick: object,
) -> int:
    valid, reasons = validate_logical_time_bridge_v01(bridge)
    if not valid:
        raise ValueError(reasons[0])
    valid_tick, tick_reasons = validate_signed_int64_v01(logical_tick)
    if not valid_tick or logical_tick < 0:
        raise ValueError(
            tick_reasons[0] if not valid_tick else "logical_tick_negative"
        )
    result = (
        bridge.origin_utc_epoch_seconds + logical_tick * bridge.seconds_per_tick
    )
    valid_result, _ = validate_signed_int64_v01(result)
    if not valid_result:
        raise ValueError("logical_time_bridge_overflow")
    return result


def epoch_seconds_to_logical_tick_v01(
    bridge: object,
    epoch_seconds: object,
) -> int:
    valid, reasons = validate_logical_time_bridge_v01(bridge)
    if not valid:
        raise ValueError(reasons[0])
    valid_epoch, epoch_reasons = validate_signed_int64_v01(epoch_seconds)
    if not valid_epoch:
        raise ValueError(epoch_reasons[0])
    delta = epoch_seconds - bridge.origin_utc_epoch_seconds
    if delta < 0 or delta % bridge.seconds_per_tick != 0:
        raise ValueError("logical_time_bridge_unrepresentable")
    tick = delta // bridge.seconds_per_tick
    valid_tick, _ = validate_signed_int64_v01(tick)
    if not valid_tick:
        raise ValueError("logical_time_bridge_overflow")
    if logical_tick_to_epoch_seconds_v01(bridge, tick) != epoch_seconds:
        raise ValueError("logical_time_bridge_round_trip_mismatch")
    return tick


def build_action_subject_scope_profile_v01(
    *,
    included_subject_refs: object,
    excluded_subject_refs: object,
) -> ActionSubjectScopeProfileV01:
    included = canonicalize_set_like_string_tuple_v01(included_subject_refs)
    excluded = canonicalize_set_like_string_tuple_v01(excluded_subject_refs)
    if not included:
        raise ValueError("subject_scope_included_empty")
    if set(included).intersection(excluded):
        raise ValueError("subject_scope_overlap")
    return ActionSubjectScopeProfileV01(included, excluded)


def validate_action_subject_scope_profile_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    if type(value) is not ActionSubjectScopeProfileV01:
        return False, ("subject_scope_type_invalid",)
    try:
        rebuilt = build_action_subject_scope_profile_v01(
            included_subject_refs=value.included_subject_refs,
            excluded_subject_refs=value.excluded_subject_refs,
        )
    except ValueError as exc:
        return False, (
            _stable_exception_reason_v01(
                exc,
                fallback="subject_scope_invalid",
            ),
        )
    except Exception:
        return False, ("subject_scope_invalid",)
    return (True, ()) if rebuilt == value else (
        False,
        ("subject_scope_not_canonical",),
    )


def action_subject_scope_material_v01(
    value: ActionSubjectScopeProfileV01,
) -> CanonicalMaterialV01:
    valid, reasons = validate_action_subject_scope_profile_v01(value)
    if not valid:
        raise ValueError(reasons[0])
    return (
        ("profile_id", ACTION_SUBJECT_SCOPE_PROFILE_ID_V01),
        ("included_subject_refs", value.included_subject_refs),
        ("excluded_subject_refs", value.excluded_subject_refs),
    )


def build_action_target_scope_profile_v01(
    *,
    included_target_refs: object,
    excluded_target_refs: object,
) -> ActionTargetScopeProfileV01:
    included = canonicalize_set_like_string_tuple_v01(included_target_refs)
    excluded = canonicalize_set_like_string_tuple_v01(excluded_target_refs)
    if not included:
        raise ValueError("target_scope_included_empty")
    if set(included).intersection(excluded):
        raise ValueError("target_scope_overlap")
    return ActionTargetScopeProfileV01(included, excluded)


def validate_action_target_scope_profile_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    if type(value) is not ActionTargetScopeProfileV01:
        return False, ("target_scope_type_invalid",)
    try:
        rebuilt = build_action_target_scope_profile_v01(
            included_target_refs=value.included_target_refs,
            excluded_target_refs=value.excluded_target_refs,
        )
    except ValueError as exc:
        return False, (
            _stable_exception_reason_v01(
                exc,
                fallback="target_scope_invalid",
            ),
        )
    except Exception:
        return False, ("target_scope_invalid",)
    return (True, ()) if rebuilt == value else (
        False,
        ("target_scope_not_canonical",),
    )


def action_target_scope_material_v01(
    value: ActionTargetScopeProfileV01,
) -> CanonicalMaterialV01:
    valid, reasons = validate_action_target_scope_profile_v01(value)
    if not valid:
        raise ValueError(reasons[0])
    return (
        ("profile_id", ACTION_TARGET_SCOPE_PROFILE_ID_V01),
        ("included_target_refs", value.included_target_refs),
        ("excluded_target_refs", value.excluded_target_refs),
    )


def build_action_permission_scope_profile_v01(
    *,
    allowed_action_classes: object,
    forbidden_action_classes: object,
    allowed_adapter_ids: object,
    forbidden_adapter_ids: object,
    required_approval_refs: object,
    prohibited_effect_classes: object,
) -> ActionPermissionScopeProfileV01:
    allowed_actions = canonicalize_set_like_string_tuple_v01(
        allowed_action_classes
    )
    forbidden_actions = canonicalize_set_like_string_tuple_v01(
        forbidden_action_classes
    )
    allowed_adapters = canonicalize_set_like_string_tuple_v01(
        allowed_adapter_ids
    )
    forbidden_adapters = canonicalize_set_like_string_tuple_v01(
        forbidden_adapter_ids
    )
    approvals = canonicalize_set_like_string_tuple_v01(required_approval_refs)
    prohibited_effects = canonicalize_set_like_string_tuple_v01(
        prohibited_effect_classes
    )
    if not allowed_actions:
        raise ValueError("permission_allowed_actions_empty")
    if not allowed_adapters:
        raise ValueError("permission_allowed_adapters_empty")
    if not approvals:
        raise ValueError("permission_required_approvals_empty")
    if set(allowed_actions).intersection(forbidden_actions):
        raise ValueError("permission_action_overlap")
    if set(allowed_adapters).intersection(forbidden_adapters):
        raise ValueError("permission_adapter_overlap")
    for action in (*allowed_actions, *forbidden_actions):
        valid_action, action_reasons = (
            validate_native_effect_firewall_identifier_v01(
                action,
                identifier_kind="action",
            )
        )
        if not valid_action:
            raise ValueError(action_reasons[0])
    for adapter in (*allowed_adapters, *forbidden_adapters):
        valid_adapter, adapter_reasons = (
            validate_native_effect_firewall_identifier_v01(
                adapter,
                identifier_kind="adapter",
            )
        )
        if not valid_adapter:
            raise ValueError(adapter_reasons[0])
    return ActionPermissionScopeProfileV01(
        allowed_action_classes=allowed_actions,
        forbidden_action_classes=forbidden_actions,
        allowed_adapter_ids=allowed_adapters,
        forbidden_adapter_ids=forbidden_adapters,
        required_approval_refs=approvals,
        prohibited_effect_classes=prohibited_effects,
    )


def validate_action_permission_scope_profile_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    if type(value) is not ActionPermissionScopeProfileV01:
        return False, ("permission_scope_type_invalid",)
    try:
        rebuilt = build_action_permission_scope_profile_v01(
            allowed_action_classes=value.allowed_action_classes,
            forbidden_action_classes=value.forbidden_action_classes,
            allowed_adapter_ids=value.allowed_adapter_ids,
            forbidden_adapter_ids=value.forbidden_adapter_ids,
            required_approval_refs=value.required_approval_refs,
            prohibited_effect_classes=value.prohibited_effect_classes,
        )
    except ValueError as exc:
        return False, (
            _stable_exception_reason_v01(
                exc,
                fallback="permission_scope_invalid",
            ),
        )
    except Exception:
        return False, ("permission_scope_invalid",)
    return (True, ()) if rebuilt == value else (
        False,
        ("permission_scope_not_canonical",),
    )


def action_permission_scope_material_v01(
    value: ActionPermissionScopeProfileV01,
) -> CanonicalMaterialV01:
    valid, reasons = validate_action_permission_scope_profile_v01(value)
    if not valid:
        raise ValueError(reasons[0])
    return (
        ("profile_id", ACTION_PERMISSION_SCOPE_PROFILE_ID_V01),
        ("allowed_action_classes", value.allowed_action_classes),
        ("forbidden_action_classes", value.forbidden_action_classes),
        ("allowed_adapter_ids", value.allowed_adapter_ids),
        ("forbidden_adapter_ids", value.forbidden_adapter_ids),
        ("required_approval_refs", value.required_approval_refs),
        ("prohibited_effect_classes", value.prohibited_effect_classes),
    )


def build_action_effect_parameter_record_v01(
    *,
    parameter_name: object,
    value_type: object,
    value: object,
) -> ActionEffectParameterRecordV01:
    name = normalize_identity_text_v01(parameter_name)
    declared_type = normalize_identity_text_v01(value_type)
    if declared_type not in EFFECT_PARAMETER_VALUE_TYPES_V01:
        raise ValueError("effect_parameter_value_type_unknown")
    canonical_value: str | int | bool
    if declared_type in ("TEXT", "REFERENCE"):
        canonical_value = normalize_identity_text_v01(value)
    elif declared_type == "DECIMAL":
        valid, reasons = validate_canonical_decimal_v01(value)
        if not valid:
            raise ValueError(reasons[0])
        canonical_value = value
    elif declared_type == "INTEGER":
        valid, reasons = validate_signed_int64_v01(value)
        if not valid:
            raise ValueError(reasons[0])
        canonical_value = value
    else:
        if type(value) is not bool:
            raise ValueError("effect_parameter_boolean_type_invalid")
        canonical_value = value
    return ActionEffectParameterRecordV01(
        parameter_name=name,
        value_type=declared_type,
        value=canonical_value,
    )


def validate_action_effect_parameter_record_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    if type(value) is not ActionEffectParameterRecordV01:
        return False, ("effect_parameter_record_type_invalid",)
    try:
        rebuilt = build_action_effect_parameter_record_v01(
            parameter_name=value.parameter_name,
            value_type=value.value_type,
            value=value.value,
        )
    except ValueError as exc:
        return False, (
            _stable_exception_reason_v01(
                exc,
                fallback="effect_parameter_record_invalid",
            ),
        )
    except Exception:
        return False, ("effect_parameter_record_invalid",)
    return (True, ()) if rebuilt == value else (
        False,
        ("effect_parameter_record_not_canonical",),
    )


def action_effect_parameter_record_material_v01(
    value: ActionEffectParameterRecordV01,
) -> CanonicalMaterialV01:
    valid, reasons = validate_action_effect_parameter_record_v01(value)
    if not valid:
        raise ValueError(reasons[0])
    return (
        ("parameter_name", value.parameter_name),
        ("value_type", value.value_type),
        ("value", value.value),
    )


def _canonical_effect_parameter_records_v01(
    records: object,
) -> tuple[ActionEffectParameterRecordV01, ...]:
    if type(records) is not tuple:
        raise ValueError("effect_parameter_records_type_invalid")
    built: list[ActionEffectParameterRecordV01] = []
    for record in records:
        if type(record) is not ActionEffectParameterRecordV01:
            raise ValueError("effect_parameter_record_type_invalid")
        built.append(
            build_action_effect_parameter_record_v01(
                parameter_name=record.parameter_name,
                value_type=record.value_type,
                value=record.value,
            )
        )
    names = tuple(record.parameter_name for record in built)
    if len(names) != len(set(names)):
        raise ValueError("effect_parameter_name_duplicate")
    return tuple(
        sorted(built, key=lambda record: record.parameter_name.encode("utf-8"))
    )


def build_action_effect_parameters_profile_v01(
    *,
    effect_class: object,
    parameter_records: object,
) -> ActionEffectParametersProfileV01:
    return ActionEffectParametersProfileV01(
        effect_class=normalize_identity_text_v01(effect_class),
        parameter_records=_canonical_effect_parameter_records_v01(
            parameter_records
        ),
    )


def validate_action_effect_parameters_profile_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    if type(value) is not ActionEffectParametersProfileV01:
        return False, ("effect_parameters_profile_type_invalid",)
    try:
        rebuilt = build_action_effect_parameters_profile_v01(
            effect_class=value.effect_class,
            parameter_records=value.parameter_records,
        )
    except ValueError as exc:
        return False, (
            _stable_exception_reason_v01(
                exc,
                fallback="effect_parameters_profile_invalid",
            ),
        )
    except Exception:
        return False, ("effect_parameters_profile_invalid",)
    return (True, ()) if rebuilt == value else (
        False,
        ("effect_parameters_profile_not_canonical",),
    )


def action_effect_parameters_material_v01(
    value: ActionEffectParametersProfileV01,
) -> CanonicalMaterialV01:
    valid, reasons = validate_action_effect_parameters_profile_v01(value)
    if not valid:
        raise ValueError(reasons[0])
    return (
        ("profile_id", ACTION_EFFECT_PARAMETERS_PROFILE_ID_V01),
        ("effect_class", value.effect_class),
        (
            "parameter_records",
            tuple(
                action_effect_parameter_record_material_v01(record)
                for record in value.parameter_records
            ),
        ),
    )


def build_action_effect_parameters_fingerprint_v01(
    value: ActionEffectParametersProfileV01,
) -> str:
    return domain_separated_sha256_hex_v01(
        domain=ACTION_EFFECT_PARAMETERS_DOMAIN_V01,
        payload=canonical_json_bytes_v01(
            action_effect_parameters_material_v01(value)
        ),
    )


def build_action_adapter_binding_profile_v01(
    *,
    corridor_class: object,
    adapter_id: object,
    adapter_kind: object,
    adapter_version: object,
    mock_only: object = True,
) -> ActionAdapterBindingProfileV01:
    if type(mock_only) is not bool or mock_only is not True:
        raise ValueError("adapter_binding_mock_only_required")
    valid_adapter, adapter_reasons = (
        validate_native_effect_firewall_identifier_v01(
            adapter_id,
            identifier_kind="adapter",
        )
    )
    if not valid_adapter:
        raise ValueError(adapter_reasons[0])
    return ActionAdapterBindingProfileV01(
        corridor_class=normalize_identity_text_v01(corridor_class),
        adapter_id=normalize_identity_text_v01(adapter_id),
        adapter_kind=normalize_identity_text_v01(adapter_kind),
        adapter_version=normalize_identity_text_v01(adapter_version),
        mock_only=True,
    )


def validate_action_adapter_binding_profile_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    if type(value) is not ActionAdapterBindingProfileV01:
        return False, ("adapter_binding_type_invalid",)
    try:
        rebuilt = build_action_adapter_binding_profile_v01(
            corridor_class=value.corridor_class,
            adapter_id=value.adapter_id,
            adapter_kind=value.adapter_kind,
            adapter_version=value.adapter_version,
            mock_only=value.mock_only,
        )
    except ValueError as exc:
        return False, (
            _stable_exception_reason_v01(
                exc,
                fallback="adapter_binding_invalid",
            ),
        )
    except Exception:
        return False, ("adapter_binding_invalid",)
    return (True, ()) if rebuilt == value else (
        False,
        ("adapter_binding_not_canonical",),
    )


def action_adapter_binding_material_v01(
    value: ActionAdapterBindingProfileV01,
) -> CanonicalMaterialV01:
    valid, reasons = validate_action_adapter_binding_profile_v01(value)
    if not valid:
        raise ValueError(reasons[0])
    return (
        ("profile_id", ACTION_ADAPTER_BINDING_PROFILE_ID_V01),
        ("corridor_class", value.corridor_class),
        ("adapter_id", value.adapter_id),
        ("adapter_kind", value.adapter_kind),
        ("adapter_version", value.adapter_version),
        ("mock_only", True),
    )


def build_dependency_set_candidate_record_v01(
    *,
    dependency_id: object,
    dependency_class: object,
    evidence_ref: object,
    content_sha256: object,
    requirement_class: object,
    time_envelope_id: object,
    freshness_policy_id: object,
    source_provenance_refs: object,
    expected_accepting_local_root_id: object,
) -> DependencySetCandidateRecordV01:
    identifier = normalize_identity_text_v01(dependency_id)
    dependency_kind = normalize_identity_text_v01(dependency_class)
    evidence = normalize_identity_text_v01(evidence_ref)
    valid_hash, hash_reasons = validate_lowercase_sha256_hex_v01(content_sha256)
    if not valid_hash:
        raise ValueError(hash_reasons[0])
    requirement = normalize_identity_text_v01(requirement_class)
    if requirement not in DEPENDENCY_REQUIREMENT_CLASSES_V01:
        raise ValueError("dependency_requirement_class_unknown")
    if time_envelope_id is None:
        time_envelope = None
    else:
        time_envelope = normalize_identity_text_v01(time_envelope_id)
    if freshness_policy_id is None:
        freshness_policy = None
    else:
        freshness_policy = normalize_identity_text_v01(freshness_policy_id)
    if (time_envelope is None) != (freshness_policy is None):
        raise ValueError("dependency_temporal_pair_partial")
    if requirement == "MANDATORY" and time_envelope is None:
        raise ValueError("dependency_mandatory_temporal_binding_missing")
    provenance = canonicalize_set_like_string_tuple_v01(source_provenance_refs)
    if not provenance:
        raise ValueError("dependency_source_provenance_empty")
    expected_root = normalize_identity_text_v01(
        expected_accepting_local_root_id
    )
    forbidden_values = (
        "ROOT_ACCEPTED_FOR_PACKET",
        "source_root_decision_id",
        "source_root_decision_hash",
        "packet_id",
    )
    all_text = (
        identifier,
        dependency_kind,
        evidence,
        expected_root,
        *provenance,
    )
    if any(item in forbidden_values for item in all_text):
        raise ValueError("dependency_candidate_post_root_data_forbidden")
    return DependencySetCandidateRecordV01(
        dependency_id=identifier,
        dependency_class=dependency_kind,
        evidence_ref=evidence,
        content_sha256=content_sha256,
        requirement_class=requirement,
        time_envelope_id=time_envelope,
        freshness_policy_id=freshness_policy,
        source_provenance_refs=provenance,
        expected_accepting_local_root_id=expected_root,
    )


def validate_dependency_set_candidate_record_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    if type(value) is not DependencySetCandidateRecordV01:
        return False, ("dependency_record_type_invalid",)
    try:
        rebuilt = build_dependency_set_candidate_record_v01(
            dependency_id=value.dependency_id,
            dependency_class=value.dependency_class,
            evidence_ref=value.evidence_ref,
            content_sha256=value.content_sha256,
            requirement_class=value.requirement_class,
            time_envelope_id=value.time_envelope_id,
            freshness_policy_id=value.freshness_policy_id,
            source_provenance_refs=value.source_provenance_refs,
            expected_accepting_local_root_id=(
                value.expected_accepting_local_root_id
            ),
        )
    except ValueError as exc:
        return False, (
            _stable_exception_reason_v01(
                exc,
                fallback="dependency_record_invalid",
            ),
        )
    except Exception:
        return False, ("dependency_record_invalid",)
    return (True, ()) if rebuilt == value else (
        False,
        ("dependency_record_not_canonical",),
    )


def dependency_set_candidate_record_material_v01(
    value: DependencySetCandidateRecordV01,
) -> CanonicalMaterialV01:
    valid, reasons = validate_dependency_set_candidate_record_v01(value)
    if not valid:
        raise ValueError(reasons[0])
    return (
        ("dependency_id", value.dependency_id),
        ("dependency_class", value.dependency_class),
        ("evidence_ref", value.evidence_ref),
        ("content_sha256", value.content_sha256),
        ("requirement_class", value.requirement_class),
        (
            "time_envelope_id",
            value.time_envelope_id
            if value.time_envelope_id is not None
            else _canonical_absent_v01(),
        ),
        (
            "freshness_policy_id",
            value.freshness_policy_id
            if value.freshness_policy_id is not None
            else _canonical_absent_v01(),
        ),
        ("source_provenance_refs", value.source_provenance_refs),
        (
            "expected_accepting_local_root_id",
            value.expected_accepting_local_root_id,
        ),
    )


def build_dependency_set_candidate_v01(
    *,
    dependency_records: object,
) -> DependencySetCandidateV01:
    if type(dependency_records) is not tuple:
        raise ValueError("dependency_records_type_invalid")
    records: list[DependencySetCandidateRecordV01] = []
    for record in dependency_records:
        if type(record) is not DependencySetCandidateRecordV01:
            raise ValueError("dependency_record_type_invalid")
        valid, reasons = validate_dependency_set_candidate_record_v01(record)
        if not valid:
            raise ValueError(reasons[0])
        records.append(record)
    dependency_ids = tuple(record.dependency_id for record in records)
    if len(dependency_ids) != len(set(dependency_ids)):
        raise ValueError("dependency_id_duplicate")
    records.sort(key=lambda record: record.dependency_id.encode("utf-8"))
    return DependencySetCandidateV01(tuple(records))


def validate_dependency_set_candidate_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    if type(value) is not DependencySetCandidateV01:
        return False, ("dependency_candidate_type_invalid",)
    try:
        rebuilt = build_dependency_set_candidate_v01(
            dependency_records=value.dependency_records
        )
    except ValueError as exc:
        return False, (
            _stable_exception_reason_v01(
                exc,
                fallback="dependency_candidate_invalid",
            ),
        )
    except Exception:
        return False, ("dependency_candidate_invalid",)
    return (True, ()) if rebuilt == value else (
        False,
        ("dependency_candidate_not_canonical",),
    )


def action_dependency_time_envelope_commitment_material_v01(
    *,
    dependency_id: object,
    evidence_ref: object,
    content_sha256: object,
    freshness_policy_id: object,
    source_provenance_refs: object,
    valid_from_utc: object,
    valid_to_utc: object,
) -> CanonicalMaterialV01:
    try:
        dependency = normalize_identity_text_v01(dependency_id)
        evidence = normalize_identity_text_v01(evidence_ref)
        freshness = normalize_identity_text_v01(freshness_policy_id)
        if (
            dependency != dependency_id
            or evidence != evidence_ref
            or freshness != freshness_policy_id
        ):
            raise ValueError(
                "dependency_time_envelope_commitment_invalid"
            )
        valid_hash, _ = validate_lowercase_sha256_hex_v01(content_sha256)
        if not valid_hash:
            raise ValueError(
                "dependency_time_envelope_commitment_invalid"
            )
        provenance = canonicalize_set_like_string_tuple_v01(
            source_provenance_refs
        )
        if (
            not provenance
            or provenance != source_provenance_refs
        ):
            raise ValueError(
                "dependency_time_envelope_commitment_invalid"
            )
        for value in (valid_from_utc, valid_to_utc):
            if not validate_signed_int64_v01(value)[0]:
                raise ValueError(
                    "dependency_time_envelope_commitment_invalid"
                )
        if valid_from_utc >= valid_to_utc:
            raise ValueError(
                "dependency_time_envelope_commitment_invalid"
            )
        return (
            (
                "profile_id",
                ACTION_DEPENDENCY_TIME_ENVELOPE_COMMITMENT_PROFILE_ID_V01,
            ),
            ("dependency_id", dependency),
            ("evidence_ref", evidence),
            ("content_sha256", content_sha256),
            ("freshness_policy_id", freshness),
            ("source_provenance_refs", provenance),
            ("valid_from_utc", valid_from_utc),
            ("valid_to_utc", valid_to_utc),
        )
    except ValueError as exc:
        raise ValueError(
            _stable_exception_reason_v01(
                exc,
                fallback="dependency_time_envelope_commitment_invalid",
            )
        ) from None
    except Exception:
        raise ValueError(
            "dependency_time_envelope_commitment_invalid"
        ) from None


def build_action_dependency_time_envelope_id_v01(
    *,
    dependency_id: object,
    evidence_ref: object,
    content_sha256: object,
    freshness_policy_id: object,
    source_provenance_refs: object,
    valid_from_utc: object,
    valid_to_utc: object,
) -> str:
    try:
        material = (
            action_dependency_time_envelope_commitment_material_v01(
                dependency_id=dependency_id,
                evidence_ref=evidence_ref,
                content_sha256=content_sha256,
                freshness_policy_id=freshness_policy_id,
                source_provenance_refs=source_provenance_refs,
                valid_from_utc=valid_from_utc,
                valid_to_utc=valid_to_utc,
            )
        )
        return build_domain_separated_identity_v01(
            domain=(
                ACTION_DEPENDENCY_TIME_ENVELOPE_COMMITMENT_DOMAIN_V01
            ),
            prefix=(
                ACTION_DEPENDENCY_TIME_ENVELOPE_COMMITMENT_PREFIX_V01
            ),
            material=material,
        )
    except ValueError as exc:
        raise ValueError(
            _stable_exception_reason_v01(
                exc,
                fallback="dependency_time_envelope_commitment_invalid",
            )
        ) from None
    except Exception:
        raise ValueError(
            "dependency_time_envelope_commitment_invalid"
        ) from None


def validate_action_dependency_time_envelope_binding_v01(
    time_envelope_id: object,
    *,
    dependency_id: object,
    evidence_ref: object,
    content_sha256: object,
    freshness_policy_id: object,
    source_provenance_refs: object,
    valid_from_utc: object,
    valid_to_utc: object,
) -> tuple[bool, tuple[str, ...]]:
    try:
        identity_valid, _ = validate_prefixed_sha256_identity_v01(
            time_envelope_id,
            prefix=(
                ACTION_DEPENDENCY_TIME_ENVELOPE_COMMITMENT_PREFIX_V01
            ),
        )
        if not identity_valid:
            return False, (
                "dependency_time_envelope_commitment_invalid",
            )
        expected = build_action_dependency_time_envelope_id_v01(
            dependency_id=dependency_id,
            evidence_ref=evidence_ref,
            content_sha256=content_sha256,
            freshness_policy_id=freshness_policy_id,
            source_provenance_refs=source_provenance_refs,
            valid_from_utc=valid_from_utc,
            valid_to_utc=valid_to_utc,
        )
        if time_envelope_id != expected:
            return False, (
                "dependency_time_envelope_identity_mismatch",
            )
        return True, ()
    except ValueError as exc:
        return False, (
            _stable_exception_reason_v01(
                exc,
                fallback="dependency_time_envelope_commitment_invalid",
            ),
        )
    except Exception:
        return False, (
            "dependency_time_envelope_commitment_invalid",
        )


def action_dependency_current_observation_material_v01(
    value: ActionDependencyCurrentObservationV01,
) -> CanonicalMaterialV01:
    if type(value) is not ActionDependencyCurrentObservationV01:
        raise ValueError("dependency_observation_type_invalid")
    return (
        ("observation_profile_id", value.observation_profile_id),
        ("dependency_id", value.dependency_id),
        ("evidence_ref", value.evidence_ref),
        ("observed_content_sha256", value.observed_content_sha256),
        ("time_envelope_id", value.time_envelope_id),
        ("freshness_policy_id", value.freshness_policy_id),
        ("source_provenance_refs", value.source_provenance_refs),
        ("valid_from_utc", value.valid_from_utc),
        ("valid_to_utc", value.valid_to_utc),
        ("observed_at_utc", value.observed_at_utc),
        ("observation_context_id", value.observation_context_id),
    )


def build_action_dependency_current_observation_v01(
    *,
    dependency_id: object,
    evidence_ref: object,
    observed_content_sha256: object,
    time_envelope_id: object,
    freshness_policy_id: object,
    source_provenance_refs: object,
    valid_from_utc: object,
    valid_to_utc: object,
    observed_at_utc: object,
    observation_context_id: object,
) -> ActionDependencyCurrentObservationV01:
    try:
        dependency = normalize_identity_text_v01(dependency_id)
        evidence = normalize_identity_text_v01(evidence_ref)
        envelope = normalize_identity_text_v01(time_envelope_id)
        freshness = normalize_identity_text_v01(freshness_policy_id)
        context = normalize_identity_text_v01(observation_context_id)
        valid_hash, hash_reasons = validate_lowercase_sha256_hex_v01(
            observed_content_sha256
        )
        if not valid_hash:
            raise ValueError(hash_reasons[0])
        provenance = canonicalize_set_like_string_tuple_v01(
            source_provenance_refs
        )
        if not provenance:
            raise ValueError("dependency_observation_provenance_empty")
        for value in (
            valid_from_utc,
            valid_to_utc,
            observed_at_utc,
        ):
            valid_time, time_reasons = validate_signed_int64_v01(value)
            if not valid_time:
                raise ValueError(time_reasons[0])
        if valid_from_utc >= valid_to_utc:
            raise ValueError("dependency_observation_interval_invalid")
        if not valid_from_utc <= observed_at_utc < valid_to_utc:
            raise ValueError("dependency_observation_time_invalid")
        time_envelope_valid, _ = (
            validate_action_dependency_time_envelope_binding_v01(
                envelope,
                dependency_id=dependency,
                evidence_ref=evidence,
                content_sha256=observed_content_sha256,
                freshness_policy_id=freshness,
                source_provenance_refs=provenance,
                valid_from_utc=valid_from_utc,
                valid_to_utc=valid_to_utc,
            )
        )
        if not time_envelope_valid:
            raise ValueError(
                "dependency_observation_time_envelope_identity_mismatch"
            )
        provisional = ActionDependencyCurrentObservationV01(
            observation_profile_id=(
                ACTION_DEPENDENCY_CURRENT_OBSERVATION_PROFILE_ID_V01
            ),
            dependency_id=dependency,
            evidence_ref=evidence,
            observed_content_sha256=observed_content_sha256,
            time_envelope_id=envelope,
            freshness_policy_id=freshness,
            source_provenance_refs=provenance,
            valid_from_utc=valid_from_utc,
            valid_to_utc=valid_to_utc,
            observed_at_utc=observed_at_utc,
            observation_context_id=context,
            observation_id="",
        )
        observation_id = build_domain_separated_identity_v01(
            domain=ACTION_DEPENDENCY_CURRENT_OBSERVATION_DOMAIN_V01,
            prefix=ACTION_DEPENDENCY_CURRENT_OBSERVATION_PREFIX_V01,
            material=action_dependency_current_observation_material_v01(
                provisional
            ),
        )
        return _replace_action_dependency_current_observation_id_v01(
            provisional,
            observation_id,
        )
    except ValueError as exc:
        raise ValueError(
            _stable_exception_reason_v01(
                exc,
                fallback="dependency_observation_invalid",
            )
        ) from None
    except Exception:
        raise ValueError("dependency_observation_invalid") from None


def _replace_action_dependency_current_observation_id_v01(
    value: ActionDependencyCurrentObservationV01,
    observation_id: str,
) -> ActionDependencyCurrentObservationV01:
    return ActionDependencyCurrentObservationV01(
        observation_profile_id=value.observation_profile_id,
        dependency_id=value.dependency_id,
        evidence_ref=value.evidence_ref,
        observed_content_sha256=value.observed_content_sha256,
        time_envelope_id=value.time_envelope_id,
        freshness_policy_id=value.freshness_policy_id,
        source_provenance_refs=value.source_provenance_refs,
        valid_from_utc=value.valid_from_utc,
        valid_to_utc=value.valid_to_utc,
        observed_at_utc=value.observed_at_utc,
        observation_context_id=value.observation_context_id,
        observation_id=observation_id,
    )


def validate_action_dependency_current_observation_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    if type(value) is not ActionDependencyCurrentObservationV01:
        return False, ("dependency_observation_type_invalid",)
    try:
        if (
            type(value.observation_profile_id) is not str
            or value.observation_profile_id
            != ACTION_DEPENDENCY_CURRENT_OBSERVATION_PROFILE_ID_V01
        ):
            return False, ("dependency_observation_profile_invalid",)
        rebuilt = build_action_dependency_current_observation_v01(
            dependency_id=value.dependency_id,
            evidence_ref=value.evidence_ref,
            observed_content_sha256=value.observed_content_sha256,
            time_envelope_id=value.time_envelope_id,
            freshness_policy_id=value.freshness_policy_id,
            source_provenance_refs=value.source_provenance_refs,
            valid_from_utc=value.valid_from_utc,
            valid_to_utc=value.valid_to_utc,
            observed_at_utc=value.observed_at_utc,
            observation_context_id=value.observation_context_id,
        )
        if (
            type(value.observation_id) is not str
            or value.observation_id != rebuilt.observation_id
            or value != rebuilt
        ):
            return False, ("dependency_observation_identity_mismatch",)
        return True, ()
    except ValueError as exc:
        return False, (
            _stable_exception_reason_v01(
                exc,
                fallback="dependency_observation_invalid",
            ),
        )
    except Exception:
        return False, ("dependency_observation_invalid",)


def action_packet_fulfillment_attempt_evidence_material_v01(
    value: ActionPacketFulfillmentAttemptEvidenceV01,
) -> CanonicalMaterialV01:
    if type(value) is not ActionPacketFulfillmentAttemptEvidenceV01:
        raise ValueError("fulfillment_attempt_evidence_type_invalid")
    return (
        ("evidence_profile_id", value.evidence_profile_id),
        ("packet_id", value.packet_id),
        ("registry_id_before", value.registry_id_before),
        ("pending_transition_event_id", value.pending_transition_event_id),
        ("execution_attempt_id", value.execution_attempt_id),
        ("attempt_observation_ordinal", value.attempt_observation_ordinal),
        ("corridor_id", value.corridor_id),
        ("corridor_step_id", value.corridor_step_id),
        ("logical_time_bridge_id", value.logical_time_bridge_id),
        ("dependency_observation_ids", value.dependency_observation_ids),
        (
            "projection_sha256",
            _optional_identity_material_v01(value.projection_sha256),
        ),
        ("firewall_id", _optional_identity_material_v01(value.firewall_id)),
        ("request_id", _optional_identity_material_v01(value.request_id)),
        ("decision_id", _optional_identity_material_v01(value.decision_id)),
        (
            "capability_id",
            _optional_identity_material_v01(value.capability_id),
        ),
        ("adapter_id", _optional_identity_material_v01(value.adapter_id)),
        ("action_kind", _optional_identity_material_v01(value.action_kind)),
        ("invocation_relation_code", value.invocation_relation_code),
        ("outcome_class", value.outcome_class),
        ("reason_code", value.reason_code),
        ("adapter_invoked", value.adapter_invoked),
        ("adapter_call_count", value.adapter_call_count),
        (
            "firewall_state_sha256_before",
            _optional_identity_material_v01(
                value.firewall_state_sha256_before
            ),
        ),
        (
            "firewall_state_sha256_after",
            _optional_identity_material_v01(
                value.firewall_state_sha256_after
            ),
        ),
        ("receipt_ref", _optional_identity_material_v01(value.receipt_ref)),
        (
            "receipt_sha256",
            _optional_identity_material_v01(value.receipt_sha256),
        ),
        ("disposition_before", value.disposition_before),
        (
            "reservation_owner_packet_id_before",
            value.reservation_owner_packet_id_before,
        ),
        (
            "latest_disposition_event_id_before",
            _optional_identity_material_v01(
                value.latest_disposition_event_id_before
            ),
        ),
        (
            "disposition_history_sha256_before",
            value.disposition_history_sha256_before,
        ),
        ("attempt_evaluation_time", value.attempt_evaluation_time),
        (
            "attempt_evaluation_time_source",
            value.attempt_evaluation_time_source,
        ),
        (
            "attempt_evaluation_context_id",
            value.attempt_evaluation_context_id,
        ),
        ("eligibility_evaluation_time", value.eligibility_evaluation_time),
        (
            "eligibility_evaluation_time_source",
            value.eligibility_evaluation_time_source,
        ),
        (
            "eligibility_evaluation_context_id",
            value.eligibility_evaluation_context_id,
        ),
        ("real_world_effects_count", value.real_world_effects_count),
    )


def _fulfillment_attempt_evidence_errors_v01(
    value: object,
    *,
    check_identity: bool,
) -> tuple[str, ...]:
    if type(value) is not ActionPacketFulfillmentAttemptEvidenceV01:
        return ("fulfillment_attempt_evidence_type_invalid",)
    reasons: list[str] = []
    if (
        type(value.evidence_profile_id) is not str
        or value.evidence_profile_id
        != ACTION_PACKET_FULFILLMENT_ATTEMPT_EVIDENCE_PROFILE_ID_V01
    ):
        _reason_v01(reasons, "fulfillment_attempt_evidence_profile_invalid")
    for field_value, prefix, reason in (
        (
            value.packet_id,
            ACTION_COMMIT_PACKET_ID_PREFIX_V01,
            "fulfillment_attempt_packet_id_invalid",
        ),
        (
            value.pending_transition_event_id,
            ACTION_PACKET_TRANSITION_EVENT_PREFIX_V01,
            "fulfillment_attempt_pending_transition_invalid",
        ),
        (
            value.execution_attempt_id,
            EXECUTION_ATTEMPT_IDENTITY_PREFIX_V01,
            "fulfillment_attempt_execution_attempt_invalid",
        ),
    ):
        if not validate_prefixed_sha256_identity_v01(
            field_value,
            prefix=prefix,
        )[0]:
            _reason_v01(reasons, reason)
    for field_value, reason in (
        (value.registry_id_before, "fulfillment_attempt_registry_id_invalid"),
        (value.corridor_id, "fulfillment_attempt_corridor_id_invalid"),
        (value.corridor_step_id, "fulfillment_attempt_step_id_invalid"),
        (
            value.logical_time_bridge_id,
            "fulfillment_attempt_logical_time_bridge_id_invalid",
        ),
        (value.reason_code, "fulfillment_attempt_reason_invalid"),
        (
            value.attempt_evaluation_time_source,
            "fulfillment_attempt_evaluation_source_invalid",
        ),
        (
            value.attempt_evaluation_context_id,
            "fulfillment_attempt_evaluation_context_invalid",
        ),
        (
            value.eligibility_evaluation_time_source,
            "fulfillment_attempt_eligibility_source_invalid",
        ),
        (
            value.eligibility_evaluation_context_id,
            "fulfillment_attempt_eligibility_context_invalid",
        ),
    ):
        if (
            not validate_identity_text_v01(field_value)[0]
            or not field_value.strip()
        ):
            _reason_v01(reasons, reason)
    if not validate_positive_int_v01(
        value.attempt_observation_ordinal
    )[0]:
        _reason_v01(reasons, "fulfillment_attempt_ordinal_invalid")
    if (
        type(value.dependency_observation_ids) is not tuple
        or len(value.dependency_observation_ids)
        != len(set(value.dependency_observation_ids))
        or any(
            not validate_prefixed_sha256_identity_v01(
                item,
                prefix=ACTION_DEPENDENCY_CURRENT_OBSERVATION_PREFIX_V01,
            )[0]
            for item in value.dependency_observation_ids
        )
    ):
        _reason_v01(
            reasons,
            "fulfillment_attempt_dependency_observations_invalid",
        )
    for field_value, reason in (
        (value.projection_sha256, "fulfillment_attempt_projection_hash_invalid"),
        (
            value.firewall_state_sha256_before,
            "fulfillment_attempt_firewall_state_hash_invalid",
        ),
        (
            value.firewall_state_sha256_after,
            "fulfillment_attempt_firewall_state_hash_invalid",
        ),
        (value.receipt_sha256, "fulfillment_attempt_receipt_hash_invalid"),
    ):
        if field_value is not None and not validate_lowercase_sha256_hex_v01(
            field_value
        )[0]:
            _reason_v01(reasons, reason)
    for field_value, reason in (
        (value.firewall_id, "fulfillment_attempt_firewall_id_invalid"),
        (value.request_id, "fulfillment_attempt_request_id_invalid"),
        (value.decision_id, "fulfillment_attempt_decision_id_invalid"),
        (value.capability_id, "fulfillment_attempt_capability_id_invalid"),
    ):
        if field_value is not None and not validate_lowercase_sha256_hex_v01(
            field_value
        )[0]:
            _reason_v01(reasons, reason)
    for field_value, reason in (
        (value.adapter_id, "fulfillment_attempt_adapter_id_invalid"),
        (value.action_kind, "fulfillment_attempt_action_kind_invalid"),
        (value.receipt_ref, "fulfillment_attempt_receipt_ref_invalid"),
    ):
        if field_value is not None and not validate_identity_text_v01(
            field_value
        )[0]:
            _reason_v01(reasons, reason)
    if (
        type(value.invocation_relation_code) is not str
        or value.invocation_relation_code
        not in _ACTION_PACKET_FULFILLMENT_INVOCATION_RELATIONS_V01
    ):
        _reason_v01(reasons, "fulfillment_attempt_invocation_relation_invalid")
    if (
        type(value.outcome_class) is not str
        or value.outcome_class
        not in _ACTION_PACKET_FULFILLMENT_OUTCOME_CLASSES_V01
    ):
        _reason_v01(reasons, "fulfillment_attempt_outcome_class_invalid")
    if type(value.adapter_invoked) is not bool:
        _reason_v01(reasons, "fulfillment_attempt_adapter_invoked_invalid")
    if (
        type(value.adapter_call_count) is not int
        or value.adapter_call_count not in {0, 1}
    ):
        _reason_v01(reasons, "fulfillment_attempt_adapter_call_count_invalid")
    if (
        type(value.disposition_before) is not str
        or value.disposition_before not in IDEMPOTENCY_DISPOSITIONS_V01
    ):
        _reason_v01(reasons, "fulfillment_attempt_disposition_invalid")
    if not validate_prefixed_sha256_identity_v01(
        value.reservation_owner_packet_id_before,
        prefix=ACTION_COMMIT_PACKET_ID_PREFIX_V01,
    )[0]:
        _reason_v01(reasons, "fulfillment_attempt_owner_invalid")
    if (
        value.latest_disposition_event_id_before is not None
        and not validate_prefixed_sha256_identity_v01(
            value.latest_disposition_event_id_before,
            prefix=IDEMPOTENCY_DISPOSITION_EVENT_PREFIX_V01,
        )[0]
    ):
        _reason_v01(reasons, "fulfillment_attempt_latest_disposition_invalid")
    if not validate_lowercase_sha256_hex_v01(
        value.disposition_history_sha256_before
    )[0]:
        _reason_v01(
            reasons,
            "fulfillment_attempt_disposition_history_hash_invalid",
        )
    for field_value in (
        value.attempt_evaluation_time,
        value.eligibility_evaluation_time,
    ):
        if not validate_signed_int64_v01(field_value)[0]:
            _reason_v01(reasons, "fulfillment_attempt_time_invalid")
    if (
        type(value.real_world_effects_count) is not int
        or value.real_world_effects_count != 0
    ):
        _reason_v01(reasons, "fulfillment_attempt_real_effect_invalid")
    no_invocation = (
        value.adapter_invoked is False
        and value.adapter_call_count == 0
        and value.invocation_relation_code == "NO_ADAPTER_INVOCATION"
        and value.capability_id is None
        and value.receipt_ref is None
        and value.receipt_sha256 is None
    )
    component_ids_present = all(
        item is not None
        for item in (
            value.projection_sha256,
            value.firewall_id,
            value.request_id,
            value.decision_id,
            value.adapter_id,
            value.action_kind,
        )
    )
    if value.outcome_class == "PRE_FULFILLMENT_BLOCKED":
        if not (
            no_invocation
            and value.projection_sha256 is None
            and value.firewall_id is None
            and value.request_id is None
            and value.decision_id is None
            and value.adapter_id is None
            and value.action_kind is None
            and value.firewall_state_sha256_before is None
            and value.firewall_state_sha256_after is None
        ):
            _reason_v01(reasons, "fulfillment_attempt_branch_invariant_invalid")
    elif value.outcome_class == "FIREWALL_BLOCKED":
        if not (
            no_invocation
            and component_ids_present
            and value.firewall_state_sha256_before is None
            and value.firewall_state_sha256_after is None
        ):
            _reason_v01(reasons, "fulfillment_attempt_branch_invariant_invalid")
    elif value.outcome_class == "CONSUMED":
        if not (
            component_ids_present
            and value.capability_id is not None
            and value.adapter_invoked is True
            and value.adapter_call_count == 1
            and value.invocation_relation_code
            == "CORRIDOR_INVOCATION_CONSUMED"
            and value.firewall_state_sha256_before is not None
            and value.firewall_state_sha256_after is not None
            and value.receipt_ref is not None
            and value.receipt_sha256 is not None
        ):
            _reason_v01(reasons, "fulfillment_attempt_branch_invariant_invalid")
    elif value.outcome_class == "NOT_CONSUMED":
        if not (
            component_ids_present
            and value.capability_id is not None
            and value.adapter_invoked is True
            and value.adapter_call_count == 1
            and value.invocation_relation_code
            == "CORRIDOR_INVOCATION_NONCONSUMING"
            and value.firewall_state_sha256_before is not None
            and value.firewall_state_sha256_before
            == value.firewall_state_sha256_after
            and value.receipt_ref is None
            and value.receipt_sha256 is None
        ):
            _reason_v01(reasons, "fulfillment_attempt_branch_invariant_invalid")
    elif value.outcome_class == "UNCERTAIN":
        if not (
            component_ids_present
            and value.capability_id is not None
            and value.adapter_invoked is True
            and value.adapter_call_count == 1
            and value.invocation_relation_code
            == "CORRIDOR_INVOCATION_UNCERTAIN"
            and value.firewall_state_sha256_before is not None
            and value.firewall_state_sha256_after is not None
            and value.receipt_ref is None
            and value.receipt_sha256 is None
        ):
            _reason_v01(reasons, "fulfillment_attempt_branch_invariant_invalid")
    if reasons or not check_identity:
        return tuple(dict.fromkeys(reasons))
    if not validate_prefixed_sha256_identity_v01(
        value.attempt_evidence_id,
        prefix=ACTION_PACKET_FULFILLMENT_ATTEMPT_EVIDENCE_PREFIX_V01,
    )[0]:
        return ("fulfillment_attempt_evidence_id_invalid",)
    expected_id = build_domain_separated_identity_v01(
        domain=ACTION_PACKET_FULFILLMENT_ATTEMPT_EVIDENCE_DOMAIN_V01,
        prefix=ACTION_PACKET_FULFILLMENT_ATTEMPT_EVIDENCE_PREFIX_V01,
        material=action_packet_fulfillment_attempt_evidence_material_v01(
            value
        ),
    )
    if value.attempt_evidence_id != expected_id:
        return ("fulfillment_attempt_evidence_identity_mismatch",)
    return ()


def build_action_packet_fulfillment_attempt_evidence_v01(
    *,
    packet_id: object,
    registry_id_before: object,
    pending_transition_event_id: object,
    execution_attempt_id: object,
    attempt_observation_ordinal: object,
    corridor_id: object,
    corridor_step_id: object,
    logical_time_bridge_id: object,
    dependency_observation_ids: object,
    projection_sha256: object,
    firewall_id: object,
    request_id: object,
    decision_id: object,
    capability_id: object,
    adapter_id: object,
    action_kind: object,
    invocation_relation_code: object,
    outcome_class: object,
    reason_code: object,
    adapter_invoked: object,
    adapter_call_count: object,
    firewall_state_sha256_before: object,
    firewall_state_sha256_after: object,
    receipt_ref: object,
    receipt_sha256: object,
    disposition_before: object,
    reservation_owner_packet_id_before: object,
    latest_disposition_event_id_before: object,
    disposition_history_sha256_before: object,
    attempt_evaluation_time: object,
    attempt_evaluation_time_source: object,
    attempt_evaluation_context_id: object,
    eligibility_evaluation_time: object,
    eligibility_evaluation_time_source: object,
    eligibility_evaluation_context_id: object,
    real_world_effects_count: object,
) -> ActionPacketFulfillmentAttemptEvidenceV01:
    try:
        provisional = ActionPacketFulfillmentAttemptEvidenceV01(
            evidence_profile_id=(
                ACTION_PACKET_FULFILLMENT_ATTEMPT_EVIDENCE_PROFILE_ID_V01
            ),
            packet_id=packet_id,
            registry_id_before=registry_id_before,
            pending_transition_event_id=pending_transition_event_id,
            execution_attempt_id=execution_attempt_id,
            attempt_observation_ordinal=attempt_observation_ordinal,
            corridor_id=corridor_id,
            corridor_step_id=corridor_step_id,
            logical_time_bridge_id=logical_time_bridge_id,
            dependency_observation_ids=dependency_observation_ids,
            projection_sha256=projection_sha256,
            firewall_id=firewall_id,
            request_id=request_id,
            decision_id=decision_id,
            capability_id=capability_id,
            adapter_id=adapter_id,
            action_kind=action_kind,
            invocation_relation_code=invocation_relation_code,
            outcome_class=outcome_class,
            reason_code=reason_code,
            adapter_invoked=adapter_invoked,
            adapter_call_count=adapter_call_count,
            firewall_state_sha256_before=firewall_state_sha256_before,
            firewall_state_sha256_after=firewall_state_sha256_after,
            receipt_ref=receipt_ref,
            receipt_sha256=receipt_sha256,
            disposition_before=disposition_before,
            reservation_owner_packet_id_before=(
                reservation_owner_packet_id_before
            ),
            latest_disposition_event_id_before=(
                latest_disposition_event_id_before
            ),
            disposition_history_sha256_before=(
                disposition_history_sha256_before
            ),
            attempt_evaluation_time=attempt_evaluation_time,
            attempt_evaluation_time_source=attempt_evaluation_time_source,
            attempt_evaluation_context_id=attempt_evaluation_context_id,
            eligibility_evaluation_time=eligibility_evaluation_time,
            eligibility_evaluation_time_source=(
                eligibility_evaluation_time_source
            ),
            eligibility_evaluation_context_id=(
                eligibility_evaluation_context_id
            ),
            real_world_effects_count=real_world_effects_count,
            attempt_evidence_id="",
        )
        errors = _fulfillment_attempt_evidence_errors_v01(
            provisional,
            check_identity=False,
        )
        if errors:
            raise ValueError(errors[0])
        value = _dataclass_replace(
            provisional,
            attempt_evidence_id=build_domain_separated_identity_v01(
                domain=(
                    ACTION_PACKET_FULFILLMENT_ATTEMPT_EVIDENCE_DOMAIN_V01
                ),
                prefix=(
                    ACTION_PACKET_FULFILLMENT_ATTEMPT_EVIDENCE_PREFIX_V01
                ),
                material=(
                    action_packet_fulfillment_attempt_evidence_material_v01(
                        provisional
                    )
                ),
            ),
        )
        errors = _fulfillment_attempt_evidence_errors_v01(
            value,
            check_identity=True,
        )
        if errors:
            raise ValueError(errors[0])
        return value
    except ValueError as exc:
        raise ValueError(
            _stable_exception_reason_v01(
                exc,
                fallback="fulfillment_attempt_evidence_invalid",
            )
        ) from None
    except Exception:
        raise ValueError("fulfillment_attempt_evidence_invalid") from None


def validate_action_packet_fulfillment_attempt_evidence_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    try:
        errors = _fulfillment_attempt_evidence_errors_v01(
            value,
            check_identity=True,
        )
        return not errors, errors
    except Exception:
        return False, ("fulfillment_attempt_evidence_invalid",)


def dependency_set_candidate_material_v01(
    value: DependencySetCandidateV01,
) -> CanonicalMaterialV01:
    valid, reasons = validate_dependency_set_candidate_v01(value)
    if not valid:
        raise ValueError(reasons[0])
    return (
        ("profile_id", ACTION_DEPENDENCY_SET_CANDIDATE_PROFILE_ID_V01),
        (
            "dependency_records",
            tuple(
                dependency_set_candidate_record_material_v01(record)
                for record in value.dependency_records
            ),
        ),
    )


def build_dependency_set_candidate_fingerprint_v01(
    value: DependencySetCandidateV01,
) -> str:
    return domain_separated_sha256_hex_v01(
        domain=ACTION_DEPENDENCY_SET_CANDIDATE_DOMAIN_V01,
        payload=canonical_json_bytes_v01(
            dependency_set_candidate_material_v01(value)
        ),
    )


def packet_dependency_acceptance_binding_material_v01(
    value: PacketDependencyAcceptanceBindingV01,
) -> CanonicalMaterialV01:
    return (
        (
            "dependency_set_candidate_fingerprint",
            value.dependency_set_candidate_fingerprint,
        ),
        (
            "root_packet_authorization_candidate_id",
            value.root_packet_authorization_candidate_id,
        ),
        ("source_root_decision_id", value.source_root_decision_id),
        ("source_root_decision_hash", value.source_root_decision_hash),
        ("owning_local_root_id", value.owning_local_root_id),
        ("packet_id", value.packet_id),
        ("accepted_status", value.accepted_status),
    )


def build_packet_dependency_acceptance_binding_v01(
    *,
    dependency_set_candidate_fingerprint: object,
    root_packet_authorization_candidate_id: object,
    source_root_decision_id: object,
    source_root_decision_hash: object,
    owning_local_root_id: object,
    packet_id: object,
    accepted_status: object = "ROOT_ACCEPTED_FOR_PACKET",
) -> PacketDependencyAcceptanceBindingV01:
    for digest in (
        dependency_set_candidate_fingerprint,
        source_root_decision_id,
        source_root_decision_hash,
    ):
        valid, reasons = validate_lowercase_sha256_hex_v01(digest)
        if not valid:
            raise ValueError(reasons[0])
    valid_candidate, candidate_reasons = validate_prefixed_sha256_identity_v01(
        root_packet_authorization_candidate_id,
        prefix=ROOT_PACKET_AUTHORIZATION_PREFIX_V01,
    )
    if not valid_candidate:
        raise ValueError(candidate_reasons[0])
    valid_packet, packet_reasons = validate_prefixed_sha256_identity_v01(
        packet_id,
        prefix=ACTION_COMMIT_PACKET_ID_PREFIX_V01,
    )
    if not valid_packet:
        raise ValueError(packet_reasons[0])
    root_id = normalize_identity_text_v01(owning_local_root_id)
    if accepted_status != "ROOT_ACCEPTED_FOR_PACKET":
        raise ValueError("dependency_acceptance_status_invalid")
    provisional = PacketDependencyAcceptanceBindingV01(
        dependency_set_candidate_fingerprint=(
            dependency_set_candidate_fingerprint
        ),
        root_packet_authorization_candidate_id=(
            root_packet_authorization_candidate_id
        ),
        source_root_decision_id=source_root_decision_id,
        source_root_decision_hash=source_root_decision_hash,
        owning_local_root_id=root_id,
        packet_id=packet_id,
        accepted_status=accepted_status,
        packet_dependency_acceptance_binding_id="",
    )
    identity = build_domain_separated_identity_v01(
        domain=PACKET_DEPENDENCY_ACCEPTANCE_BINDING_DOMAIN_V01,
        prefix=PACKET_DEPENDENCY_ACCEPTANCE_PREFIX_V01,
        material=packet_dependency_acceptance_binding_material_v01(
            provisional
        ),
    )
    return PacketDependencyAcceptanceBindingV01(
        dependency_set_candidate_fingerprint=(
            dependency_set_candidate_fingerprint
        ),
        root_packet_authorization_candidate_id=(
            root_packet_authorization_candidate_id
        ),
        source_root_decision_id=source_root_decision_id,
        source_root_decision_hash=source_root_decision_hash,
        owning_local_root_id=root_id,
        packet_id=packet_id,
        accepted_status=accepted_status,
        packet_dependency_acceptance_binding_id=identity,
    )


def validate_packet_dependency_acceptance_binding_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    if type(value) is not PacketDependencyAcceptanceBindingV01:
        return False, ("dependency_acceptance_binding_type_invalid",)
    identity_valid, _ = validate_prefixed_sha256_identity_v01(
        value.packet_dependency_acceptance_binding_id,
        prefix=PACKET_DEPENDENCY_ACCEPTANCE_PREFIX_V01,
    )
    if not identity_valid:
        return False, ("dependency_acceptance_binding_identity_invalid",)
    if type(value.accepted_status) is not str:
        return False, ("dependency_acceptance_status_type_invalid",)
    try:
        rebuilt = build_packet_dependency_acceptance_binding_v01(
            dependency_set_candidate_fingerprint=(
                value.dependency_set_candidate_fingerprint
            ),
            root_packet_authorization_candidate_id=(
                value.root_packet_authorization_candidate_id
            ),
            source_root_decision_id=value.source_root_decision_id,
            source_root_decision_hash=value.source_root_decision_hash,
            owning_local_root_id=value.owning_local_root_id,
            packet_id=value.packet_id,
            accepted_status=value.accepted_status,
        )
    except ValueError as exc:
        return False, (
            _stable_exception_reason_v01(
                exc,
                fallback="dependency_acceptance_binding_invalid",
            ),
        )
    except Exception:
        return False, ("dependency_acceptance_binding_invalid",)
    if rebuilt != value:
        return False, ("dependency_acceptance_binding_identity_mismatch",)
    return True, ()


def build_action_authority_policy_profile_v01(
    *,
    policy_version: object,
    owning_local_root_id: object,
    authority_rule_refs: object,
    kill_switch_condition_refs: object,
    retry_policy: object,
    supersession_policy: object,
    logical_effect_namespace: object,
    allowed_logical_effect_classes: object,
    allowed_business_object_namespaces: object,
    allowed_corridor_classes: object,
) -> ActionAuthorityPolicyProfileV01:
    rules = canonicalize_set_like_string_tuple_v01(authority_rule_refs)
    switches = canonicalize_set_like_string_tuple_v01(
        kill_switch_condition_refs
    )
    effects = canonicalize_set_like_string_tuple_v01(
        allowed_logical_effect_classes
    )
    namespaces = canonicalize_set_like_string_tuple_v01(
        allowed_business_object_namespaces
    )
    corridors = canonicalize_set_like_string_tuple_v01(
        allowed_corridor_classes
    )
    retry = normalize_identity_text_v01(retry_policy)
    supersession = normalize_identity_text_v01(supersession_policy)
    if retry not in AUTHORITY_RETRY_POLICIES_V01:
        raise ValueError("authority_retry_policy_unknown")
    if supersession not in AUTHORITY_SUPERSESSION_POLICIES_V01:
        raise ValueError("authority_supersession_policy_unknown")
    if not rules:
        raise ValueError("authority_rule_refs_empty")
    if not effects:
        raise ValueError("authority_allowed_effect_classes_empty")
    if not namespaces:
        raise ValueError("authority_allowed_business_namespaces_empty")
    if not corridors:
        raise ValueError("authority_allowed_corridors_empty")
    return ActionAuthorityPolicyProfileV01(
        policy_version=normalize_identity_text_v01(policy_version),
        owning_local_root_id=normalize_identity_text_v01(
            owning_local_root_id
        ),
        authority_rule_refs=rules,
        kill_switch_condition_refs=switches,
        retry_policy=retry,
        supersession_policy=supersession,
        logical_effect_namespace=normalize_identity_text_v01(
            logical_effect_namespace
        ),
        allowed_logical_effect_classes=effects,
        allowed_business_object_namespaces=namespaces,
        allowed_corridor_classes=corridors,
    )


def validate_action_authority_policy_profile_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    if type(value) is not ActionAuthorityPolicyProfileV01:
        return False, ("authority_policy_type_invalid",)
    try:
        rebuilt = build_action_authority_policy_profile_v01(
            policy_version=value.policy_version,
            owning_local_root_id=value.owning_local_root_id,
            authority_rule_refs=value.authority_rule_refs,
            kill_switch_condition_refs=value.kill_switch_condition_refs,
            retry_policy=value.retry_policy,
            supersession_policy=value.supersession_policy,
            logical_effect_namespace=value.logical_effect_namespace,
            allowed_logical_effect_classes=(
                value.allowed_logical_effect_classes
            ),
            allowed_business_object_namespaces=(
                value.allowed_business_object_namespaces
            ),
            allowed_corridor_classes=value.allowed_corridor_classes,
        )
    except ValueError as exc:
        return False, (
            _stable_exception_reason_v01(
                exc,
                fallback="authority_policy_invalid",
            ),
        )
    except Exception:
        return False, ("authority_policy_invalid",)
    return (True, ()) if rebuilt == value else (
        False,
        ("authority_policy_not_canonical",),
    )


def action_authority_policy_material_v01(
    value: ActionAuthorityPolicyProfileV01,
) -> CanonicalMaterialV01:
    valid, reasons = validate_action_authority_policy_profile_v01(value)
    if not valid:
        raise ValueError(reasons[0])
    return (
        ("profile_id", ACTION_AUTHORITY_POLICY_PROFILE_ID_V01),
        ("policy_version", value.policy_version),
        ("owning_local_root_id", value.owning_local_root_id),
        ("authority_rule_refs", value.authority_rule_refs),
        ("kill_switch_condition_refs", value.kill_switch_condition_refs),
        ("retry_policy", value.retry_policy),
        ("supersession_policy", value.supersession_policy),
        ("logical_effect_namespace", value.logical_effect_namespace),
        (
            "allowed_logical_effect_classes",
            value.allowed_logical_effect_classes,
        ),
        (
            "allowed_business_object_namespaces",
            value.allowed_business_object_namespaces,
        ),
        ("allowed_corridor_classes", value.allowed_corridor_classes),
    )


def build_action_authority_policy_fingerprint_v01(
    value: ActionAuthorityPolicyProfileV01,
) -> str:
    return domain_separated_sha256_hex_v01(
        domain=ACTION_AUTHORITY_POLICY_DOMAIN_V01,
        payload=canonical_json_bytes_v01(
            action_authority_policy_material_v01(value)
        ),
    )


def build_action_business_object_identity_profile_v01(
    *,
    business_object_class: object,
    business_object_namespace: object,
    business_object_ref: object,
    owning_effect_root_id: object,
) -> ActionBusinessObjectIdentityProfileV01:
    return ActionBusinessObjectIdentityProfileV01(
        business_object_class=normalize_identity_text_v01(
            business_object_class
        ),
        business_object_namespace=normalize_identity_text_v01(
            business_object_namespace
        ),
        business_object_ref=normalize_identity_text_v01(business_object_ref),
        owning_effect_root_id=normalize_identity_text_v01(
            owning_effect_root_id
        ),
    )


def validate_action_business_object_identity_profile_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    if type(value) is not ActionBusinessObjectIdentityProfileV01:
        return False, ("business_object_identity_type_invalid",)
    try:
        rebuilt = build_action_business_object_identity_profile_v01(
            business_object_class=value.business_object_class,
            business_object_namespace=value.business_object_namespace,
            business_object_ref=value.business_object_ref,
            owning_effect_root_id=value.owning_effect_root_id,
        )
    except ValueError as exc:
        return False, (
            _stable_exception_reason_v01(
                exc,
                fallback="business_object_identity_invalid",
            ),
        )
    except Exception:
        return False, ("business_object_identity_invalid",)
    return (True, ()) if rebuilt == value else (
        False,
        ("business_object_identity_not_canonical",),
    )


def action_business_object_identity_material_v01(
    value: ActionBusinessObjectIdentityProfileV01,
) -> CanonicalMaterialV01:
    valid, reasons = validate_action_business_object_identity_profile_v01(
        value
    )
    if not valid:
        raise ValueError(reasons[0])
    return (
        ("profile_id", ACTION_BUSINESS_OBJECT_IDENTITY_PROFILE_ID_V01),
        ("business_object_class", value.business_object_class),
        ("business_object_namespace", value.business_object_namespace),
        ("business_object_ref", value.business_object_ref),
        ("owning_effect_root_id", value.owning_effect_root_id),
    )


def build_action_consequential_effect_parameters_profile_v01(
    *,
    amount_decimal: object,
    currency_code: object,
    quantity_decimal: object,
    parameter_records: object,
) -> ActionConsequentialEffectParametersProfileV01:
    amount: str | None
    currency: str | None
    quantity: str | None
    if amount_decimal is None:
        amount = None
    else:
        valid_amount, amount_reasons = validate_canonical_decimal_v01(
            amount_decimal
        )
        if not valid_amount:
            raise ValueError(amount_reasons[0])
        amount = amount_decimal
    if currency_code is None:
        currency = None
    else:
        currency = normalize_identity_text_v01(currency_code)
        if re.fullmatch(r"[A-Z]{3}", currency) is None:
            raise ValueError("currency_code_format_invalid")
    if quantity_decimal is None:
        quantity = None
    else:
        valid_quantity, quantity_reasons = validate_canonical_decimal_v01(
            quantity_decimal
        )
        if not valid_quantity:
            raise ValueError(quantity_reasons[0])
        quantity = quantity_decimal
    if amount is not None and currency is None:
        raise ValueError("currency_required_for_amount")
    if currency is not None and amount is None:
        raise ValueError("currency_without_amount")
    records = _canonical_effect_parameter_records_v01(parameter_records)
    if any(
        record.parameter_name in RESERVED_CONSEQUENTIAL_PARAMETER_NAMES_V01
        for record in records
    ):
        raise ValueError("consequential_parameter_name_reserved")
    return ActionConsequentialEffectParametersProfileV01(
        amount_decimal=amount,
        currency_code=currency,
        quantity_decimal=quantity,
        parameter_records=records,
    )


def validate_action_consequential_effect_parameters_profile_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    if type(value) is not ActionConsequentialEffectParametersProfileV01:
        return False, ("consequential_parameters_type_invalid",)
    try:
        rebuilt = build_action_consequential_effect_parameters_profile_v01(
            amount_decimal=value.amount_decimal,
            currency_code=value.currency_code,
            quantity_decimal=value.quantity_decimal,
            parameter_records=value.parameter_records,
        )
    except ValueError as exc:
        return False, (
            _stable_exception_reason_v01(
                exc,
                fallback="consequential_parameters_invalid",
            ),
        )
    except Exception:
        return False, ("consequential_parameters_invalid",)
    return (True, ()) if rebuilt == value else (
        False,
        ("consequential_parameters_not_canonical",),
    )


def action_consequential_effect_parameters_material_v01(
    value: ActionConsequentialEffectParametersProfileV01,
) -> CanonicalMaterialV01:
    valid, reasons = (
        validate_action_consequential_effect_parameters_profile_v01(value)
    )
    if not valid:
        raise ValueError(reasons[0])
    return (
        ("profile_id", ACTION_CONSEQUENTIAL_EFFECT_PARAMETERS_PROFILE_ID_V01),
        (
            "amount_decimal",
            value.amount_decimal
            if value.amount_decimal is not None
            else _canonical_absent_v01(),
        ),
        (
            "currency_code",
            value.currency_code
            if value.currency_code is not None
            else _canonical_absent_v01(),
        ),
        (
            "quantity_decimal",
            value.quantity_decimal
            if value.quantity_decimal is not None
            else _canonical_absent_v01(),
        ),
        (
            "parameter_records",
            tuple(
                action_effect_parameter_record_material_v01(record)
                for record in value.parameter_records
            ),
        ),
    )


def project_consequential_effect_parameters_v01(
    *,
    effect_class: object,
    consequential_parameters: object,
) -> ActionEffectParametersProfileV01:
    valid, reasons = (
        validate_action_consequential_effect_parameters_profile_v01(
            consequential_parameters
        )
    )
    if not valid:
        raise ValueError(reasons[0])
    records = list(consequential_parameters.parameter_records)
    if consequential_parameters.amount_decimal is not None:
        records.append(
            build_action_effect_parameter_record_v01(
                parameter_name="amount_decimal",
                value_type="DECIMAL",
                value=consequential_parameters.amount_decimal,
            )
        )
    if consequential_parameters.currency_code is not None:
        records.append(
            build_action_effect_parameter_record_v01(
                parameter_name="currency_code",
                value_type="TEXT",
                value=consequential_parameters.currency_code,
            )
        )
    if consequential_parameters.quantity_decimal is not None:
        records.append(
            build_action_effect_parameter_record_v01(
                parameter_name="quantity_decimal",
                value_type="DECIMAL",
                value=consequential_parameters.quantity_decimal,
            )
        )
    return build_action_effect_parameters_profile_v01(
        effect_class=effect_class,
        parameter_records=tuple(records),
    )


def validate_canonical_permission_ref_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    valid, reasons = validate_identity_text_v01(value)
    if not valid:
        return valid, reasons
    if not value.startswith("permission:"):
        return False, ("canonical_permission_ref_prefix_invalid",)
    return True, ()


def validate_executable_transaction_id_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    if value is None or is_absent_v01(value):
        return False, ("executable_transaction_absent",)
    valid, reasons = validate_identity_text_v01(value)
    if not valid:
        return False, reasons
    return True, ()


def _optional_identity_material_v01(value: str | None) -> object:
    return value if value is not None else _canonical_absent_v01()


def root_owned_logical_effect_intent_material_v01(
    value: RootOwnedLogicalEffectIntentV01,
) -> CanonicalMaterialV01:
    return (
        ("logical_intent_profile_version", "v0.1"),
        ("owning_effect_root_id", value.owning_effect_root_id),
        ("transaction_id", _optional_identity_material_v01(value.transaction_id)),
        ("logical_effect_class", value.logical_effect_class),
        (
            "normalized_subject_scope",
            action_subject_scope_material_v01(value.normalized_subject_scope),
        ),
        (
            "normalized_target_scope",
            action_target_scope_material_v01(value.normalized_target_scope),
        ),
        (
            "normalized_business_object_identity",
            action_business_object_identity_material_v01(
                value.normalized_business_object_identity
            ),
        ),
        (
            "normalized_consequential_effect_parameters",
            action_consequential_effect_parameters_material_v01(
                value.normalized_consequential_effect_parameters
            ),
        ),
        ("logical_effect_namespace", value.logical_effect_namespace),
    )


def build_root_owned_logical_effect_intent_v01(
    *,
    owning_effect_root_id: object,
    transaction_id: object,
    logical_effect_class: object,
    normalized_subject_scope: object,
    normalized_target_scope: object,
    normalized_business_object_identity: object,
    normalized_consequential_effect_parameters: object,
    logical_effect_namespace: object,
) -> RootOwnedLogicalEffectIntentV01:
    root_id = normalize_identity_text_v01(owning_effect_root_id)
    transaction: str | None
    if transaction_id is None or is_absent_v01(transaction_id):
        transaction = None
    else:
        transaction = normalize_identity_text_v01(transaction_id)
    for profile, validator in (
        (normalized_subject_scope, validate_action_subject_scope_profile_v01),
        (normalized_target_scope, validate_action_target_scope_profile_v01),
        (
            normalized_business_object_identity,
            validate_action_business_object_identity_profile_v01,
        ),
        (
            normalized_consequential_effect_parameters,
            validate_action_consequential_effect_parameters_profile_v01,
        ),
    ):
        valid, reasons = validator(profile)
        if not valid:
            raise ValueError(reasons[0])
    effect_class = normalize_identity_text_v01(logical_effect_class)
    namespace = normalize_identity_text_v01(logical_effect_namespace)
    provisional = RootOwnedLogicalEffectIntentV01(
        owning_effect_root_id=root_id,
        transaction_id=transaction,
        logical_effect_class=effect_class,
        normalized_subject_scope=normalized_subject_scope,
        normalized_target_scope=normalized_target_scope,
        normalized_business_object_identity=normalized_business_object_identity,
        normalized_consequential_effect_parameters=(
            normalized_consequential_effect_parameters
        ),
        logical_effect_namespace=namespace,
        root_owned_intent_id="",
    )
    identity = build_domain_separated_identity_v01(
        domain=ROOT_LOGICAL_EFFECT_INTENT_DOMAIN_V01,
        prefix=ROOT_LOGICAL_INTENT_PREFIX_V01,
        material=root_owned_logical_effect_intent_material_v01(provisional),
    )
    return RootOwnedLogicalEffectIntentV01(
        owning_effect_root_id=root_id,
        transaction_id=transaction,
        logical_effect_class=effect_class,
        normalized_subject_scope=normalized_subject_scope,
        normalized_target_scope=normalized_target_scope,
        normalized_business_object_identity=normalized_business_object_identity,
        normalized_consequential_effect_parameters=(
            normalized_consequential_effect_parameters
        ),
        logical_effect_namespace=namespace,
        root_owned_intent_id=identity,
    )


def validate_root_owned_logical_effect_intent_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    if type(value) is not RootOwnedLogicalEffectIntentV01:
        return False, ("logical_intent_type_invalid",)
    try:
        rebuilt = build_root_owned_logical_effect_intent_v01(
            owning_effect_root_id=value.owning_effect_root_id,
            transaction_id=value.transaction_id,
            logical_effect_class=value.logical_effect_class,
            normalized_subject_scope=value.normalized_subject_scope,
            normalized_target_scope=value.normalized_target_scope,
            normalized_business_object_identity=(
                value.normalized_business_object_identity
            ),
            normalized_consequential_effect_parameters=(
                value.normalized_consequential_effect_parameters
            ),
            logical_effect_namespace=value.logical_effect_namespace,
        )
    except ValueError as exc:
        return False, (
            _stable_exception_reason_v01(
                exc,
                fallback="logical_intent_invalid",
            ),
        )
    except Exception:
        return False, ("logical_intent_invalid",)
    if rebuilt != value:
        return False, ("logical_intent_identity_mismatch",)
    return True, ()


def action_idempotency_identity_material_v01(
    value: ActionIdempotencyIdentityV01,
) -> CanonicalMaterialV01:
    return (
        ("idempotency_contract_version", "v0.1"),
        ("owning_effect_root_id", value.owning_effect_root_id),
        ("transaction_id", _optional_identity_material_v01(value.transaction_id)),
        (
            "root_owned_intent_id",
            _optional_identity_material_v01(value.root_owned_intent_id),
        ),
        ("logical_effect_class", value.logical_effect_class),
        (
            "normalized_subject_scope",
            action_subject_scope_material_v01(value.normalized_subject_scope),
        ),
        (
            "normalized_target_scope",
            action_target_scope_material_v01(value.normalized_target_scope),
        ),
        (
            "normalized_business_object_identity",
            action_business_object_identity_material_v01(
                value.normalized_business_object_identity
            ),
        ),
        (
            "normalized_consequential_effect_parameters",
            action_consequential_effect_parameters_material_v01(
                value.normalized_consequential_effect_parameters
            ),
        ),
        ("logical_effect_namespace", value.logical_effect_namespace),
    )


def build_action_idempotency_identity_v01(
    *,
    owning_effect_root_id: object,
    transaction_id: object,
    root_owned_intent_id: object,
    logical_effect_class: object,
    normalized_subject_scope: object,
    normalized_target_scope: object,
    normalized_business_object_identity: object,
    normalized_consequential_effect_parameters: object,
    logical_effect_namespace: object,
) -> ActionIdempotencyIdentityV01:
    root_id = normalize_identity_text_v01(owning_effect_root_id)
    transaction = (
        None
        if transaction_id is None or is_absent_v01(transaction_id)
        else normalize_identity_text_v01(transaction_id)
    )
    intent_id = (
        None
        if root_owned_intent_id is None or is_absent_v01(root_owned_intent_id)
        else normalize_identity_text_v01(root_owned_intent_id)
    )
    if transaction is None and intent_id is None:
        raise ValueError("idempotency_identifiers_both_absent")
    if intent_id is not None:
        valid_intent, intent_reasons = validate_prefixed_sha256_identity_v01(
            intent_id,
            prefix=ROOT_LOGICAL_INTENT_PREFIX_V01,
        )
        if not valid_intent:
            raise ValueError(intent_reasons[0])
    for profile, validator in (
        (normalized_subject_scope, validate_action_subject_scope_profile_v01),
        (normalized_target_scope, validate_action_target_scope_profile_v01),
        (
            normalized_business_object_identity,
            validate_action_business_object_identity_profile_v01,
        ),
        (
            normalized_consequential_effect_parameters,
            validate_action_consequential_effect_parameters_profile_v01,
        ),
    ):
        valid, reasons = validator(profile)
        if not valid:
            raise ValueError(reasons[0])
    provisional = ActionIdempotencyIdentityV01(
        owning_effect_root_id=root_id,
        transaction_id=transaction,
        root_owned_intent_id=intent_id,
        logical_effect_class=normalize_identity_text_v01(logical_effect_class),
        normalized_subject_scope=normalized_subject_scope,
        normalized_target_scope=normalized_target_scope,
        normalized_business_object_identity=normalized_business_object_identity,
        normalized_consequential_effect_parameters=(
            normalized_consequential_effect_parameters
        ),
        logical_effect_namespace=normalize_identity_text_v01(
            logical_effect_namespace
        ),
        idempotency_key="",
    )
    key = build_domain_separated_identity_v01(
        domain=ACTION_IDEMPOTENCY_DOMAIN_V01,
        prefix=ACTION_IDEMPOTENCY_PREFIX_V01,
        material=action_idempotency_identity_material_v01(provisional),
    )
    return ActionIdempotencyIdentityV01(
        owning_effect_root_id=provisional.owning_effect_root_id,
        transaction_id=provisional.transaction_id,
        root_owned_intent_id=provisional.root_owned_intent_id,
        logical_effect_class=provisional.logical_effect_class,
        normalized_subject_scope=provisional.normalized_subject_scope,
        normalized_target_scope=provisional.normalized_target_scope,
        normalized_business_object_identity=(
            provisional.normalized_business_object_identity
        ),
        normalized_consequential_effect_parameters=(
            provisional.normalized_consequential_effect_parameters
        ),
        logical_effect_namespace=provisional.logical_effect_namespace,
        idempotency_key=key,
    )


def validate_action_idempotency_identity_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    if type(value) is not ActionIdempotencyIdentityV01:
        return False, ("idempotency_identity_type_invalid",)
    try:
        rebuilt = build_action_idempotency_identity_v01(
            owning_effect_root_id=value.owning_effect_root_id,
            transaction_id=value.transaction_id,
            root_owned_intent_id=value.root_owned_intent_id,
            logical_effect_class=value.logical_effect_class,
            normalized_subject_scope=value.normalized_subject_scope,
            normalized_target_scope=value.normalized_target_scope,
            normalized_business_object_identity=(
                value.normalized_business_object_identity
            ),
            normalized_consequential_effect_parameters=(
                value.normalized_consequential_effect_parameters
            ),
            logical_effect_namespace=value.logical_effect_namespace,
        )
    except ValueError as exc:
        return False, (
            _stable_exception_reason_v01(
                exc,
                fallback="idempotency_identity_invalid",
            ),
        )
    except Exception:
        return False, ("idempotency_identity_invalid",)
    if rebuilt != value:
        return False, ("idempotency_identity_mismatch",)
    return True, ()


def root_bound_packet_authorization_candidate_material_v01(
    value: RootBoundPacketAuthorizationCandidateV01,
) -> CanonicalMaterialV01:
    return (
        ("packet_contract_family", "ActionCommitPacketV02"),
        ("packet_contract_version", "v0.2"),
        ("owning_local_root_id", value.owning_local_root_id),
        ("transaction_id", _optional_identity_material_v01(value.transaction_id)),
        ("root_owned_intent_id", value.root_owned_intent_id),
        ("effect_class", value.effect_class),
        (
            "normalized_subject_scope",
            action_subject_scope_material_v01(value.normalized_subject_scope),
        ),
        (
            "normalized_target_scope",
            action_target_scope_material_v01(value.normalized_target_scope),
        ),
        (
            "normalized_permission_scope",
            action_permission_scope_material_v01(
                value.normalized_permission_scope
            ),
        ),
        (
            "normalized_effect_parameters_fingerprint",
            value.normalized_effect_parameters_fingerprint,
        ),
        ("corridor_class", value.corridor_class),
        (
            "adapter_binding",
            action_adapter_binding_material_v01(value.adapter_binding),
        ),
        (
            "dependency_set_candidate_fingerprint",
            value.dependency_set_candidate_fingerprint,
        ),
        (
            "temporal_authority_fingerprint",
            value.temporal_authority_fingerprint,
        ),
        ("policy_version", _optional_identity_material_v01(value.policy_version)),
        (
            "authority_policy_fingerprint",
            value.authority_policy_fingerprint,
        ),
        (
            "predecessor_packet_id",
            _optional_identity_material_v01(value.predecessor_packet_id),
        ),
        (
            "supersession_reason_class",
            _optional_identity_material_v01(value.supersession_reason_class),
        ),
    )


def build_root_bound_packet_authorization_candidate_v01(
    *,
    owning_local_root_id: object,
    transaction_id: object,
    root_owned_intent_id: object,
    effect_class: object,
    normalized_subject_scope: object,
    normalized_target_scope: object,
    normalized_permission_scope: object,
    normalized_effect_parameters_fingerprint: object,
    corridor_class: object,
    adapter_binding: object,
    dependency_set_candidate_fingerprint: object,
    temporal_authority_fingerprint: object,
    policy_version: object,
    authority_policy_fingerprint: object,
    predecessor_packet_id: object = None,
    supersession_reason_class: object = None,
) -> RootBoundPacketAuthorizationCandidateV01:
    root_id = normalize_identity_text_v01(owning_local_root_id)
    transaction = (
        None
        if transaction_id is None or is_absent_v01(transaction_id)
        else normalize_identity_text_v01(transaction_id)
    )
    intent_id = normalize_identity_text_v01(root_owned_intent_id)
    valid_intent, intent_reasons = validate_prefixed_sha256_identity_v01(
        intent_id,
        prefix=ROOT_LOGICAL_INTENT_PREFIX_V01,
    )
    if not valid_intent:
        raise ValueError(intent_reasons[0])
    for profile, validator in (
        (normalized_subject_scope, validate_action_subject_scope_profile_v01),
        (normalized_target_scope, validate_action_target_scope_profile_v01),
        (
            normalized_permission_scope,
            validate_action_permission_scope_profile_v01,
        ),
        (adapter_binding, validate_action_adapter_binding_profile_v01),
    ):
        valid, reasons = validator(profile)
        if not valid:
            raise ValueError(reasons[0])
    for fingerprint in (
        normalized_effect_parameters_fingerprint,
        dependency_set_candidate_fingerprint,
        temporal_authority_fingerprint,
        authority_policy_fingerprint,
    ):
        valid, reasons = validate_lowercase_sha256_hex_v01(fingerprint)
        if not valid:
            raise ValueError(reasons[0])
    policy = (
        None
        if policy_version is None or is_absent_v01(policy_version)
        else normalize_identity_text_v01(policy_version)
    )
    predecessor = (
        None
        if predecessor_packet_id is None or is_absent_v01(predecessor_packet_id)
        else normalize_identity_text_v01(predecessor_packet_id)
    )
    reason_class = (
        None
        if supersession_reason_class is None
        or is_absent_v01(supersession_reason_class)
        else normalize_identity_text_v01(supersession_reason_class)
    )
    if predecessor is None and reason_class is not None:
        raise ValueError("supersession_reason_without_predecessor")
    if predecessor is not None and reason_class is None:
        raise ValueError("predecessor_without_supersession_reason")
    if predecessor is not None:
        valid_predecessor, predecessor_reasons = (
            validate_prefixed_sha256_identity_v01(
                predecessor,
                prefix=ACTION_COMMIT_PACKET_ID_PREFIX_V01,
            )
        )
        if not valid_predecessor:
            raise ValueError(predecessor_reasons[0])
    provisional = RootBoundPacketAuthorizationCandidateV01(
        owning_local_root_id=root_id,
        transaction_id=transaction,
        root_owned_intent_id=intent_id,
        effect_class=normalize_identity_text_v01(effect_class),
        normalized_subject_scope=normalized_subject_scope,
        normalized_target_scope=normalized_target_scope,
        normalized_permission_scope=normalized_permission_scope,
        normalized_effect_parameters_fingerprint=(
            normalized_effect_parameters_fingerprint
        ),
        corridor_class=normalize_identity_text_v01(corridor_class),
        adapter_binding=adapter_binding,
        dependency_set_candidate_fingerprint=(
            dependency_set_candidate_fingerprint
        ),
        temporal_authority_fingerprint=temporal_authority_fingerprint,
        policy_version=policy,
        authority_policy_fingerprint=authority_policy_fingerprint,
        predecessor_packet_id=predecessor,
        supersession_reason_class=reason_class,
        root_packet_authorization_candidate_id="",
    )
    identity = build_domain_separated_identity_v01(
        domain=ROOT_PACKET_AUTHORIZATION_CANDIDATE_DOMAIN_V01,
        prefix=ROOT_PACKET_AUTHORIZATION_PREFIX_V01,
        material=root_bound_packet_authorization_candidate_material_v01(
            provisional
        ),
    )
    return RootBoundPacketAuthorizationCandidateV01(
        owning_local_root_id=provisional.owning_local_root_id,
        transaction_id=provisional.transaction_id,
        root_owned_intent_id=provisional.root_owned_intent_id,
        effect_class=provisional.effect_class,
        normalized_subject_scope=provisional.normalized_subject_scope,
        normalized_target_scope=provisional.normalized_target_scope,
        normalized_permission_scope=provisional.normalized_permission_scope,
        normalized_effect_parameters_fingerprint=(
            provisional.normalized_effect_parameters_fingerprint
        ),
        corridor_class=provisional.corridor_class,
        adapter_binding=provisional.adapter_binding,
        dependency_set_candidate_fingerprint=(
            provisional.dependency_set_candidate_fingerprint
        ),
        temporal_authority_fingerprint=(
            provisional.temporal_authority_fingerprint
        ),
        policy_version=provisional.policy_version,
        authority_policy_fingerprint=(
            provisional.authority_policy_fingerprint
        ),
        predecessor_packet_id=provisional.predecessor_packet_id,
        supersession_reason_class=provisional.supersession_reason_class,
        root_packet_authorization_candidate_id=identity,
    )


def validate_root_bound_packet_authorization_candidate_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    if type(value) is not RootBoundPacketAuthorizationCandidateV01:
        return False, ("packet_authorization_candidate_type_invalid",)
    try:
        rebuilt = build_root_bound_packet_authorization_candidate_v01(
            owning_local_root_id=value.owning_local_root_id,
            transaction_id=value.transaction_id,
            root_owned_intent_id=value.root_owned_intent_id,
            effect_class=value.effect_class,
            normalized_subject_scope=value.normalized_subject_scope,
            normalized_target_scope=value.normalized_target_scope,
            normalized_permission_scope=value.normalized_permission_scope,
            normalized_effect_parameters_fingerprint=(
                value.normalized_effect_parameters_fingerprint
            ),
            corridor_class=value.corridor_class,
            adapter_binding=value.adapter_binding,
            dependency_set_candidate_fingerprint=(
                value.dependency_set_candidate_fingerprint
            ),
            temporal_authority_fingerprint=(
                value.temporal_authority_fingerprint
            ),
            policy_version=value.policy_version,
            authority_policy_fingerprint=value.authority_policy_fingerprint,
            predecessor_packet_id=value.predecessor_packet_id,
            supersession_reason_class=value.supersession_reason_class,
        )
    except ValueError as exc:
        return False, (
            _stable_exception_reason_v01(
                exc,
                fallback="packet_authorization_candidate_invalid",
            ),
        )
    except Exception:
        return False, ("packet_authorization_candidate_invalid",)
    if rebuilt != value:
        return False, ("packet_authorization_candidate_identity_mismatch",)
    return True, ()


def action_commit_packet_identity_material_v01(
    *,
    candidate: RootBoundPacketAuthorizationCandidateV01,
    source_root_decision_id: str,
    source_root_decision_hash: str,
) -> CanonicalMaterialV01:
    valid, reasons = validate_root_bound_packet_authorization_candidate_v01(
        candidate
    )
    if not valid:
        raise ValueError(reasons[0])
    for value in (source_root_decision_id, source_root_decision_hash):
        valid_digest, digest_reasons = validate_lowercase_sha256_hex_v01(value)
        if not valid_digest:
            raise ValueError(digest_reasons[0])
    return (
        ("packet_contract_family", "ActionCommitPacketV02"),
        ("packet_contract_version", "v0.2"),
        ("owning_local_root_id", candidate.owning_local_root_id),
        ("source_root_decision_id", source_root_decision_id),
        ("source_root_decision_hash", source_root_decision_hash),
        (
            "transaction_id",
            _optional_identity_material_v01(candidate.transaction_id),
        ),
        ("root_owned_intent_id", candidate.root_owned_intent_id),
        ("effect_class", candidate.effect_class),
        (
            "normalized_subject_scope",
            action_subject_scope_material_v01(
                candidate.normalized_subject_scope
            ),
        ),
        (
            "normalized_target_scope",
            action_target_scope_material_v01(candidate.normalized_target_scope),
        ),
        (
            "normalized_permission_scope",
            action_permission_scope_material_v01(
                candidate.normalized_permission_scope
            ),
        ),
        (
            "normalized_effect_parameters_fingerprint",
            candidate.normalized_effect_parameters_fingerprint,
        ),
        ("corridor_class", candidate.corridor_class),
        (
            "adapter_binding",
            action_adapter_binding_material_v01(candidate.adapter_binding),
        ),
        (
            "dependency_set_candidate_fingerprint",
            candidate.dependency_set_candidate_fingerprint,
        ),
        (
            "temporal_authority_fingerprint",
            candidate.temporal_authority_fingerprint,
        ),
        (
            "policy_version",
            _optional_identity_material_v01(candidate.policy_version),
        ),
        (
            "authority_policy_fingerprint",
            candidate.authority_policy_fingerprint,
        ),
        (
            "predecessor_packet_id",
            _optional_identity_material_v01(candidate.predecessor_packet_id),
        ),
        (
            "supersession_reason_class",
            _optional_identity_material_v01(
                candidate.supersession_reason_class
            ),
        ),
    )


def build_action_commit_packet_identity_v01(
    *,
    candidate: RootBoundPacketAuthorizationCandidateV01,
    source_root_decision_id: object,
    source_root_decision_hash: object,
) -> ActionCommitPacketIdentityResultV01:
    material = action_commit_packet_identity_material_v01(
        candidate=candidate,
        source_root_decision_id=source_root_decision_id,
        source_root_decision_hash=source_root_decision_hash,
    )
    packet_id = build_domain_separated_identity_v01(
        domain=ACTION_COMMIT_PACKET_ID_DOMAIN_V01,
        prefix=ACTION_COMMIT_PACKET_ID_PREFIX_V01,
        material=material,
    )
    return ActionCommitPacketIdentityResultV01(
        packet_id=packet_id,
        material=material,
    )


def validate_action_commit_packet_identity_v01(
    value: object,
    *,
    candidate: object = None,
    source_root_decision_id: object = None,
    source_root_decision_hash: object = None,
) -> tuple[bool, tuple[str, ...]]:
    if type(value) is not ActionCommitPacketIdentityResultV01:
        return False, ("packet_identity_result_type_invalid",)
    if type(candidate) is not RootBoundPacketAuthorizationCandidateV01:
        return False, ("packet_authorization_candidate_type_invalid",)
    packet_id_valid, _ = validate_prefixed_sha256_identity_v01(
        value.packet_id,
        prefix=ACTION_COMMIT_PACKET_ID_PREFIX_V01,
    )
    if not packet_id_valid:
        return False, ("packet_identity_id_invalid",)
    try:
        rebuilt = build_action_commit_packet_identity_v01(
            candidate=candidate,
            source_root_decision_id=source_root_decision_id,
            source_root_decision_hash=source_root_decision_hash,
        )
    except ValueError as exc:
        return False, (
            _stable_exception_reason_v01(
                exc,
                fallback="packet_identity_invalid",
            ),
        )
    except Exception:
        return False, ("packet_identity_invalid",)
    expected_field_names = tuple(name for name, _ in rebuilt.material)
    supplied_material_valid, _ = validate_canonical_profile_material_v01(
        value.material,
        expected_field_names=expected_field_names,
    )
    if not supplied_material_valid:
        return False, ("packet_identity_material_invalid",)
    try:
        supplied_bytes = canonical_material_bytes_v01(value.material)
        rebuilt_bytes = canonical_material_bytes_v01(rebuilt.material)
    except ValueError:
        return False, ("packet_identity_material_invalid",)
    if supplied_bytes != rebuilt_bytes or value.packet_id != rebuilt.packet_id:
        return False, ("packet_identity_mismatch",)
    return True, ()


def validate_native_effect_firewall_identifier_v01(
    value: object,
    *,
    identifier_kind: object = None,
) -> tuple[bool, tuple[str, ...]]:
    if type(identifier_kind) is not str or identifier_kind not in (
        "adapter",
        "action",
    ):
        return False, ("firewall_identifier_kind_invalid",)
    valid, reasons = validate_identity_text_v01(value)
    if not valid:
        return valid, reasons
    prefix = "mock_adapter:" if identifier_kind == "adapter" else "mock_action:"
    if not value.startswith(prefix):
        return False, ("firewall_identifier_prefix_invalid",)
    token = value[len(prefix) :]
    try:
        matched = re.fullmatch(CANONICAL_TOKEN_REGEX_V01, token) is not None
    except Exception:
        matched = False
    if not matched:
        return False, ("firewall_identifier_token_invalid",)
    return True, ()


def build_native_effect_firewall_vocabulary_projection_v01(
    *,
    canonical_identifier: object,
    identifier_kind: object,
) -> EffectFirewallVocabularyProjectionV01:
    valid, reasons = validate_native_effect_firewall_identifier_v01(
        canonical_identifier,
        identifier_kind=identifier_kind,
    )
    if not valid:
        raise ValueError(reasons[0])
    return EffectFirewallVocabularyProjectionV01(
        identifier_kind=identifier_kind,
        raw_identifier=canonical_identifier,
        canonical_identifier=canonical_identifier,
        compatibility_mode=False,
    )


def build_legacy_effect_firewall_vocabulary_projection_v01(
    *,
    raw_identifier: object,
    identifier_kind: object,
    raw_allowed_identifiers: object,
    raw_forbidden_identifiers: object,
) -> EffectFirewallVocabularyProjectionV01:
    if type(identifier_kind) is not str or identifier_kind not in (
        "adapter",
        "action",
    ):
        raise ValueError("firewall_identifier_kind_invalid")
    raw = normalize_identity_text_v01(raw_identifier)
    allowed = preserve_ordered_string_tuple_v01(raw_allowed_identifiers)
    forbidden = preserve_ordered_string_tuple_v01(raw_forbidden_identifiers)
    if raw.startswith("mock_adapter:") or raw.startswith("mock_action:"):
        raise ValueError("legacy_firewall_identifier_prefixed")
    if raw in _NEVER_MAP_LEGACY_IDENTIFIERS_V01:
        raise ValueError("legacy_firewall_real_identifier_forbidden")
    if raw not in allowed:
        raise ValueError("legacy_firewall_identifier_not_allowed")
    if raw in forbidden:
        raise ValueError("legacy_firewall_identifier_forbidden")
    canonical = _LEGACY_FIREWALL_VOCABULARY_V01.get(
        (identifier_kind, raw)
    )
    if canonical is None:
        raise ValueError("legacy_firewall_mapping_unknown")
    return EffectFirewallVocabularyProjectionV01(
        identifier_kind=identifier_kind,
        raw_identifier=raw,
        canonical_identifier=canonical,
        compatibility_mode=True,
    )


def validate_effect_firewall_vocabulary_projection_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    if type(value) is not EffectFirewallVocabularyProjectionV01:
        return False, ("firewall_vocabulary_projection_type_invalid",)
    if type(value.compatibility_mode) is not bool:
        return False, ("firewall_vocabulary_compatibility_mode_type_invalid",)
    if type(value.identifier_kind) is not str or value.identifier_kind not in (
        "adapter",
        "action",
    ):
        return False, ("firewall_identifier_kind_invalid",)
    for identifier in (value.raw_identifier, value.canonical_identifier):
        valid_identifier_text, _ = validate_identity_text_v01(identifier)
        if not valid_identifier_text:
            return False, ("firewall_vocabulary_identifier_invalid",)
    try:
        if value.compatibility_mode is True:
            expected = _LEGACY_FIREWALL_VOCABULARY_V01.get(
                (value.identifier_kind, value.raw_identifier)
            )
            if expected is None:
                raise ValueError("legacy_firewall_mapping_unknown")
            rebuilt = EffectFirewallVocabularyProjectionV01(
                identifier_kind=value.identifier_kind,
                raw_identifier=value.raw_identifier,
                canonical_identifier=expected,
                compatibility_mode=True,
            )
        else:
            rebuilt = build_native_effect_firewall_vocabulary_projection_v01(
                canonical_identifier=value.canonical_identifier,
                identifier_kind=value.identifier_kind,
            )
    except ValueError as exc:
        return False, (
            _stable_exception_reason_v01(
                exc,
                fallback="firewall_vocabulary_projection_invalid",
            ),
        )
    except Exception:
        return False, ("firewall_vocabulary_projection_invalid",)
    if rebuilt != value:
        return False, ("firewall_vocabulary_projection_mismatch",)
    return True, ()


def _map_all_legacy_allowed_vocabulary_v01(
    *,
    raw_values: tuple[str, ...],
    raw_forbidden_values: tuple[str, ...],
    identifier_kind: str,
) -> tuple[str, ...]:
    mapped = tuple(
        build_legacy_effect_firewall_vocabulary_projection_v01(
            raw_identifier=raw,
            identifier_kind=identifier_kind,
            raw_allowed_identifiers=raw_values,
            raw_forbidden_identifiers=raw_forbidden_values,
        ).canonical_identifier
        for raw in raw_values
    )
    return canonicalize_set_like_string_tuple_v01(mapped)


def _validate_action_commit_packet_exact_types_v01(
    packet: object,
) -> tuple[bool, tuple[str, ...]]:
    if type(packet) is not ActionCommitPacketV02:
        return False, ("action_commit_packet_exact_type_invalid",)
    reasons: list[str] = []
    for value in (
        packet.packet_id,
        packet.source_root_decision_ref,
        packet.human_approval_ref,
        packet.packet_type,
        packet.created_by,
        packet.bsep_ref,
        packet.root_boundary_ref,
    ):
        if type(value) is not str:
            _reason_v01(reasons, "action_commit_packet_string_type_invalid")
    for value in (
        packet.root_created,
        packet.receipt_evidence_only,
        packet.real_world_effects_allowed,
        packet.production_ready_claimed,
        packet.public_auditor_ready_claimed,
    ):
        if type(value) is not bool:
            _reason_v01(reasons, "action_commit_packet_bool_type_invalid")

    scope = packet.scope
    if type(scope) is not PermissionScopeV02:
        _reason_v01(reasons, "action_commit_packet_scope_type_invalid")
    else:
        for value in (
            scope.allowed_subjects,
            scope.forbidden_subjects,
            scope.allowed_actions,
            scope.forbidden_actions,
            scope.allowed_adapters,
            scope.forbidden_adapters,
        ):
            if (
                type(value) is not tuple
                or any(type(item) is not str for item in value)
            ):
                _reason_v01(reasons, "action_commit_packet_tuple_type_invalid")
        for value in (
            scope.payment_slot_ref,
            scope.creditor_ref,
            scope.amount,
            scope.currency,
        ):
            if type(value) is not str:
                _reason_v01(reasons, "action_commit_packet_string_type_invalid")

    ttl = packet.ttl
    if type(ttl) is not PacketTTL:
        _reason_v01(reasons, "action_commit_packet_ttl_type_invalid")
    else:
        if type(ttl.created_at) is not str or type(ttl.expires_at) is not str:
            _reason_v01(reasons, "action_commit_packet_string_type_invalid")
        if type(ttl.ttl_seconds) is not int:
            _reason_v01(reasons, "action_commit_packet_integer_type_invalid")
        if type(ttl.ttl_valid) is not bool or type(ttl.expired) is not bool:
            _reason_v01(reasons, "action_commit_packet_bool_type_invalid")

    idempotency = packet.idempotency
    if type(idempotency) is not IdempotencyKeyV02:
        _reason_v01(reasons, "action_commit_packet_idempotency_type_invalid")
    else:
        if type(idempotency.key) is not str:
            _reason_v01(reasons, "action_commit_packet_string_type_invalid")
        for value in (
            idempotency.duplicate_packet_id,
            idempotency.duplicate_idempotency_key,
            idempotency.terminal_receipt_already_exists,
        ):
            if type(value) is not bool:
                _reason_v01(reasons, "action_commit_packet_bool_type_invalid")

    adapter = packet.adapter_binding
    if type(adapter) is not AdapterBindingV02:
        _reason_v01(reasons, "action_commit_packet_adapter_type_invalid")
    else:
        if (
            type(adapter.adapter_id) is not str
            or type(adapter.adapter_kind) is not str
            or (
                adapter.adapter_version is not None
                and type(adapter.adapter_version) is not str
            )
        ):
            _reason_v01(reasons, "action_commit_packet_string_type_invalid")
        if type(adapter.real_adapter) is not bool:
            _reason_v01(reasons, "action_commit_packet_bool_type_invalid")

    if (
        type(packet.evidence_refs) is not tuple
        or any(type(item) is not PacketEvidenceRefV02 for item in packet.evidence_refs)
    ):
        _reason_v01(reasons, "action_commit_packet_evidence_tuple_type_invalid")
    else:
        for evidence in packet.evidence_refs:
            if any(
                type(value) is not str
                for value in (
                    evidence.evidence_id,
                    evidence.evidence_kind,
                    evidence.source_ref,
                )
            ):
                _reason_v01(reasons, "action_commit_packet_string_type_invalid")
    for value in (packet.drs_refs, packet.avf_refs):
        if (
            type(value) is not tuple
            or any(type(item) is not str for item in value)
        ):
            _reason_v01(reasons, "action_commit_packet_tuple_type_invalid")
    return _result_v01(reasons)


def _build_supplier_action_commit_packet_canonical_projection_unchecked_v01(
    packet: object,
    *,
    transaction_id: object,
    owning_local_root_id: object,
    canonical_permission_ref: object,
    selected_legacy_action: object,
    logical_effect_namespace: object,
    business_object_namespace: object,
    corridor_class: object,
    adapter_version: object,
    temporal_policy_version: object,
    authority_policy: object,
    dependency_candidate: object,
    evaluation_time: object,
    evaluation_time_source: object,
    evaluation_context_id: object,
    predecessor_packet_id: object = None,
    supersession_reason_class: object = None,
) -> SupplierActionCommitPacketCanonicalProjectionV01:
    if (
        type(packet) is ActionCommitPacketV02
        and type(packet.adapter_binding) is AdapterBindingV02
        and packet.adapter_binding.adapter_version is not None
    ):
        raise ValueError(
            "supplier_projection_source_adapter_version_must_be_absent"
        )
    exact_packet_valid, _ = _validate_action_commit_packet_exact_types_v01(
        packet
    )
    if not exact_packet_valid:
        raise ValueError("supplier_projection_packet_type_invalid")
    try:
        historical_valid, _ = validate_action_commit_packet_v02(packet)
    except Exception:
        raise ValueError("supplier_projection_historical_packet_invalid") from None
    if not historical_valid:
        raise ValueError("supplier_projection_historical_packet_invalid")
    valid_transaction, transaction_reasons = (
        validate_executable_transaction_id_v01(transaction_id)
    )
    if not valid_transaction:
        raise ValueError(transaction_reasons[0])
    valid_permission, permission_reasons = (
        validate_canonical_permission_ref_v01(canonical_permission_ref)
    )
    if not valid_permission:
        raise ValueError(permission_reasons[0])
    root_id = normalize_identity_text_v01(owning_local_root_id)
    corridor = normalize_identity_text_v01(corridor_class)
    namespace = normalize_identity_text_v01(logical_effect_namespace)
    business_namespace = normalize_identity_text_v01(
        business_object_namespace
    )
    version = normalize_identity_text_v01(adapter_version)
    valid_evaluation_time, evaluation_time_reasons = (
        validate_signed_int64_v01(evaluation_time)
    )
    if not valid_evaluation_time:
        raise ValueError(evaluation_time_reasons[0])
    evaluation_source = normalize_identity_text_v01(evaluation_time_source)
    evaluation_context = normalize_identity_text_v01(evaluation_context_id)
    if version != PRE_G2A_ADAPTER_VERSION_V01:
        raise ValueError("supplier_projection_adapter_version_invalid")
    valid_policy, policy_reasons = validate_action_authority_policy_profile_v01(
        authority_policy
    )
    if not valid_policy:
        raise ValueError(policy_reasons[0])
    valid_dependency, dependency_reasons = validate_dependency_set_candidate_v01(
        dependency_candidate
    )
    if not valid_dependency:
        raise ValueError(dependency_reasons[0])
    if packet.adapter_binding.real_adapter:
        raise ValueError("supplier_projection_real_adapter_forbidden")
    adapter_projection = (
        build_legacy_effect_firewall_vocabulary_projection_v01(
            raw_identifier=packet.adapter_binding.adapter_id,
            identifier_kind="adapter",
            raw_allowed_identifiers=packet.scope.allowed_adapters,
            raw_forbidden_identifiers=packet.scope.forbidden_adapters,
        )
    )
    action_projection = (
        build_legacy_effect_firewall_vocabulary_projection_v01(
            raw_identifier=selected_legacy_action,
            identifier_kind="action",
            raw_allowed_identifiers=packet.scope.allowed_actions,
            raw_forbidden_identifiers=packet.scope.forbidden_actions,
        )
    )
    if packet.adapter_binding.adapter_id != ADAPTER_MOCK_BANK_SANDBOX:
        raise ValueError("supplier_projection_selected_adapter_mismatch")
    if selected_legacy_action != ACTION_MOCK_SUPPLIER_A_PAYMENT_ORDER:
        raise ValueError("supplier_projection_selected_action_mismatch")
    allowed_actions = _map_all_legacy_allowed_vocabulary_v01(
        raw_values=packet.scope.allowed_actions,
        raw_forbidden_values=packet.scope.forbidden_actions,
        identifier_kind="action",
    )
    allowed_adapters = _map_all_legacy_allowed_vocabulary_v01(
        raw_values=packet.scope.allowed_adapters,
        raw_forbidden_values=packet.scope.forbidden_adapters,
        identifier_kind="adapter",
    )
    subject_scope = build_action_subject_scope_profile_v01(
        included_subject_refs=packet.scope.allowed_subjects,
        excluded_subject_refs=packet.scope.forbidden_subjects,
    )
    target_scope = build_action_target_scope_profile_v01(
        included_target_refs=(
            packet.scope.creditor_ref,
            packet.scope.payment_slot_ref,
        ),
        excluded_target_refs=(),
    )
    permission_scope = build_action_permission_scope_profile_v01(
        allowed_action_classes=allowed_actions,
        forbidden_action_classes=(),
        allowed_adapter_ids=allowed_adapters,
        forbidden_adapter_ids=(),
        required_approval_refs=(canonical_permission_ref,),
        prohibited_effect_classes=(),
    )
    adapter_binding = build_action_adapter_binding_profile_v01(
        corridor_class=corridor,
        adapter_id=adapter_projection.canonical_identifier,
        adapter_kind=packet.adapter_binding.adapter_kind,
        adapter_version=version,
        mock_only=True,
    )
    ttl_projection = project_packet_ttl_compatibility_v01(
        packet.ttl,
        evaluation_time=evaluation_time,
        temporal_policy_version=temporal_policy_version,
    )
    temporal_authority = ttl_projection.temporal_authority
    temporal_evaluation = ttl_projection.evaluation
    business_object = build_action_business_object_identity_profile_v01(
        business_object_class="PAYMENT_SLOT",
        business_object_namespace=business_namespace,
        business_object_ref=packet.scope.payment_slot_ref,
        owning_effect_root_id=root_id,
    )
    consequential = (
        build_action_consequential_effect_parameters_profile_v01(
            amount_decimal=normalize_legacy_decimal_v01(packet.scope.amount),
            currency_code=packet.scope.currency,
            quantity_decimal=None,
            parameter_records=(),
        )
    )
    effect_parameters = project_consequential_effect_parameters_v01(
        effect_class="PAYMENT",
        consequential_parameters=consequential,
    )
    effect_fingerprint = build_action_effect_parameters_fingerprint_v01(
        effect_parameters
    )
    dependency_fingerprint = (
        build_dependency_set_candidate_fingerprint_v01(dependency_candidate)
    )
    temporal_fingerprint = build_temporal_authority_fingerprint_v01(
        temporal_authority
    )
    policy_fingerprint = build_action_authority_policy_fingerprint_v01(
        authority_policy
    )
    logical_intent = build_root_owned_logical_effect_intent_v01(
        owning_effect_root_id=root_id,
        transaction_id=transaction_id,
        logical_effect_class="PAYMENT",
        normalized_subject_scope=subject_scope,
        normalized_target_scope=target_scope,
        normalized_business_object_identity=business_object,
        normalized_consequential_effect_parameters=consequential,
        logical_effect_namespace=namespace,
    )
    idempotency = build_action_idempotency_identity_v01(
        owning_effect_root_id=root_id,
        transaction_id=transaction_id,
        root_owned_intent_id=logical_intent.root_owned_intent_id,
        logical_effect_class="PAYMENT",
        normalized_subject_scope=subject_scope,
        normalized_target_scope=target_scope,
        normalized_business_object_identity=business_object,
        normalized_consequential_effect_parameters=consequential,
        logical_effect_namespace=namespace,
    )
    authorization_candidate = (
        build_root_bound_packet_authorization_candidate_v01(
            owning_local_root_id=root_id,
            transaction_id=transaction_id,
            root_owned_intent_id=logical_intent.root_owned_intent_id,
            effect_class="PAYMENT",
            normalized_subject_scope=subject_scope,
            normalized_target_scope=target_scope,
            normalized_permission_scope=permission_scope,
            normalized_effect_parameters_fingerprint=effect_fingerprint,
            corridor_class=corridor,
            adapter_binding=adapter_binding,
            dependency_set_candidate_fingerprint=dependency_fingerprint,
            temporal_authority_fingerprint=temporal_fingerprint,
            policy_version=authority_policy.policy_version,
            authority_policy_fingerprint=policy_fingerprint,
            predecessor_packet_id=predecessor_packet_id,
            supersession_reason_class=supersession_reason_class,
        )
    )
    projection = SupplierActionCommitPacketCanonicalProjectionV01(
        transaction_id=transaction_id,
        owning_local_root_id=root_id,
        canonical_permission_ref=canonical_permission_ref,
        selected_legacy_action=selected_legacy_action,
        selected_canonical_action=action_projection.canonical_identifier,
        source_packet=packet,
        normalized_subject_scope=subject_scope,
        normalized_target_scope=target_scope,
        normalized_permission_scope=permission_scope,
        normalized_effect_parameters=effect_parameters,
        normalized_effect_parameters_fingerprint=effect_fingerprint,
        adapter_binding=adapter_binding,
        dependency_candidate=dependency_candidate,
        dependency_set_candidate_fingerprint=dependency_fingerprint,
        temporal_authority=temporal_authority,
        temporal_authority_fingerprint=temporal_fingerprint,
        evaluation_time=evaluation_time,
        evaluation_time_source=evaluation_source,
        evaluation_context_id=evaluation_context,
        temporal_evaluation=temporal_evaluation,
        authority_policy=authority_policy,
        authority_policy_fingerprint=policy_fingerprint,
        business_object_identity=business_object,
        consequential_effect_parameters=consequential,
        logical_intent=logical_intent,
        idempotency_identity=idempotency,
        authorization_candidate=authorization_candidate,
        raw_allowed_actions=tuple(packet.scope.allowed_actions),
        raw_forbidden_actions=tuple(packet.scope.forbidden_actions),
        raw_allowed_adapters=tuple(packet.scope.allowed_adapters),
        raw_forbidden_adapters=tuple(packet.scope.forbidden_adapters),
        human_approval_evidence_ref=packet.human_approval_ref,
        advisory_drs_refs=tuple(packet.drs_refs),
        advisory_avf_refs=tuple(packet.avf_refs),
        advisory_bsep_ref=packet.bsep_ref,
    )
    return projection


def build_supplier_action_commit_packet_canonical_projection_v01(
    packet: object,
    *,
    transaction_id: object,
    owning_local_root_id: object,
    canonical_permission_ref: object,
    selected_legacy_action: object,
    logical_effect_namespace: object,
    business_object_namespace: object,
    corridor_class: object,
    adapter_version: object,
    temporal_policy_version: object,
    authority_policy: object,
    dependency_candidate: object,
    evaluation_time: object,
    evaluation_time_source: object,
    evaluation_context_id: object,
    predecessor_packet_id: object = None,
    supersession_reason_class: object = None,
) -> SupplierActionCommitPacketCanonicalProjectionV01:
    """Project one retained legacy Supplier packet without authorizing it."""

    try:
        projection = (
            _build_supplier_action_commit_packet_canonical_projection_unchecked_v01(
                packet,
                transaction_id=transaction_id,
                owning_local_root_id=owning_local_root_id,
                canonical_permission_ref=canonical_permission_ref,
                selected_legacy_action=selected_legacy_action,
                logical_effect_namespace=logical_effect_namespace,
                business_object_namespace=business_object_namespace,
                corridor_class=corridor_class,
                adapter_version=adapter_version,
                temporal_policy_version=temporal_policy_version,
                authority_policy=authority_policy,
                dependency_candidate=dependency_candidate,
                evaluation_time=evaluation_time,
                evaluation_time_source=evaluation_time_source,
                evaluation_context_id=evaluation_context_id,
                predecessor_packet_id=predecessor_packet_id,
                supersession_reason_class=supersession_reason_class,
            )
        )
        projection_valid, projection_reasons = (
            validate_supplier_action_commit_packet_canonical_projection_v01(
                projection
            )
        )
        if not projection_valid:
            raise ValueError(projection_reasons[0])
        return projection
    except ValueError as exc:
        raise ValueError(
            _stable_exception_reason_v01(
                exc,
                fallback="supplier_projection_invalid",
            )
        ) from None
    except Exception:
        raise ValueError("supplier_projection_invalid") from None


def _validate_g2a1a_cross_profile_coherence_impl_v01(
    value: object,
    *,
    selected_canonical_action: object = None,
    selected_canonical_adapter: object = None,
    packet_identity: object = None,
    source_root_decision_id: object = None,
    source_root_decision_hash: object = None,
) -> tuple[bool, tuple[str, ...]]:
    """Rebuild every G2-A1A identity and enforce cross-profile equality."""

    if type(value) is not SupplierActionCommitPacketCanonicalProjectionV01:
        return False, ("cross_profile_bundle_type_invalid",)
    reasons: list[str] = []
    try:
        action = normalize_identity_text_v01(selected_canonical_action)
        adapter = normalize_identity_text_v01(selected_canonical_adapter)
    except ValueError as exc:
        return False, (
            _stable_exception_reason_v01(
                exc,
                fallback="cross_profile_selected_identifier_invalid",
            ),
        )
    except Exception:
        return False, ("cross_profile_selected_identifier_invalid",)
    for identifier, kind in ((action, "action"), (adapter, "adapter")):
        valid_identifier, identifier_reasons = (
            validate_native_effect_firewall_identifier_v01(
                identifier,
                identifier_kind=kind,
            )
        )
        if not valid_identifier:
            return False, identifier_reasons

    validators = (
        (
            value.normalized_subject_scope,
            validate_action_subject_scope_profile_v01,
            "subject_scope_invalid",
        ),
        (
            value.normalized_target_scope,
            validate_action_target_scope_profile_v01,
            "target_scope_invalid",
        ),
        (
            value.normalized_permission_scope,
            validate_action_permission_scope_profile_v01,
            "permission_scope_invalid",
        ),
        (
            value.normalized_effect_parameters,
            validate_action_effect_parameters_profile_v01,
            "effect_parameters_invalid",
        ),
        (
            value.adapter_binding,
            validate_action_adapter_binding_profile_v01,
            "adapter_binding_invalid",
        ),
        (
            value.dependency_candidate,
            validate_dependency_set_candidate_v01,
            "dependency_candidate_invalid",
        ),
        (
            value.temporal_authority,
            validate_action_temporal_authority_profile_v01,
            "temporal_authority_invalid",
        ),
        (
            value.authority_policy,
            validate_action_authority_policy_profile_v01,
            "authority_policy_invalid",
        ),
        (
            value.business_object_identity,
            validate_action_business_object_identity_profile_v01,
            "business_object_identity_invalid",
        ),
        (
            value.consequential_effect_parameters,
            validate_action_consequential_effect_parameters_profile_v01,
            "consequential_parameters_invalid",
        ),
        (
            value.logical_intent,
            validate_root_owned_logical_effect_intent_v01,
            "logical_intent_invalid",
        ),
        (
            value.idempotency_identity,
            validate_action_idempotency_identity_v01,
            "idempotency_identity_invalid",
        ),
        (
            value.authorization_candidate,
            validate_root_bound_packet_authorization_candidate_v01,
            "authorization_candidate_invalid",
        ),
    )
    for profile, validator, reason in validators:
        valid, _ = validator(profile)
        if not valid:
            _reason_v01(reasons, reason)
    if reasons:
        return _result_v01(reasons)

    logical = value.logical_intent
    idempotency = value.idempotency_identity
    candidate = value.authorization_candidate
    policy = value.authority_policy
    permission = value.normalized_permission_scope
    business = value.business_object_identity

    if not (
        value.transaction_id
        == logical.transaction_id
        == idempotency.transaction_id
        == candidate.transaction_id
    ):
        _reason_v01(reasons, "cross_profile_transaction_mismatch")
    if not (
        logical.root_owned_intent_id
        == idempotency.root_owned_intent_id
        == candidate.root_owned_intent_id
    ):
        _reason_v01(reasons, "cross_profile_logical_intent_mismatch")
    if not (
        value.owning_local_root_id
        == logical.owning_effect_root_id
        == idempotency.owning_effect_root_id
        == candidate.owning_local_root_id
        == policy.owning_local_root_id
        == business.owning_effect_root_id
    ):
        _reason_v01(reasons, "cross_profile_root_mismatch")
    if not (
        value.normalized_subject_scope
        == logical.normalized_subject_scope
        == idempotency.normalized_subject_scope
        == candidate.normalized_subject_scope
    ):
        _reason_v01(reasons, "cross_profile_subject_scope_mismatch")
    if not (
        value.normalized_target_scope
        == logical.normalized_target_scope
        == idempotency.normalized_target_scope
        == candidate.normalized_target_scope
    ):
        _reason_v01(reasons, "cross_profile_target_scope_mismatch")
    if candidate.normalized_permission_scope != permission:
        _reason_v01(reasons, "cross_profile_permission_scope_mismatch")
    if not (
        candidate.corridor_class
        == value.adapter_binding.corridor_class
        == candidate.adapter_binding.corridor_class
    ):
        _reason_v01(reasons, "cross_profile_corridor_mismatch")
    if (
        candidate.policy_version is not None
        and candidate.policy_version != policy.policy_version
    ):
        _reason_v01(reasons, "cross_profile_policy_version_mismatch")
    if not (
        logical.logical_effect_namespace
        == idempotency.logical_effect_namespace
        == policy.logical_effect_namespace
    ):
        _reason_v01(reasons, "cross_profile_namespace_mismatch")
    if not (
        candidate.effect_class
        == logical.logical_effect_class
        == idempotency.logical_effect_class
        == value.normalized_effect_parameters.effect_class
    ):
        _reason_v01(reasons, "cross_profile_effect_class_mismatch")
    if candidate.effect_class not in policy.allowed_logical_effect_classes:
        _reason_v01(reasons, "cross_profile_effect_class_not_allowed")
    if (
        business.business_object_namespace
        not in policy.allowed_business_object_namespaces
    ):
        _reason_v01(reasons, "cross_profile_business_namespace_not_allowed")
    if candidate.corridor_class not in policy.allowed_corridor_classes:
        _reason_v01(reasons, "cross_profile_corridor_not_allowed")
    if adapter != value.adapter_binding.adapter_id:
        _reason_v01(reasons, "cross_profile_selected_adapter_mismatch")
    if adapter not in permission.allowed_adapter_ids:
        _reason_v01(reasons, "cross_profile_adapter_not_allowed")
    if adapter in permission.forbidden_adapter_ids:
        _reason_v01(reasons, "cross_profile_adapter_forbidden")
    if action not in permission.allowed_action_classes:
        _reason_v01(reasons, "cross_profile_action_not_allowed")
    if action in permission.forbidden_action_classes:
        _reason_v01(reasons, "cross_profile_action_forbidden")
    if candidate.effect_class in permission.prohibited_effect_classes:
        _reason_v01(reasons, "cross_profile_effect_prohibited")
    if value.canonical_permission_ref not in permission.required_approval_refs:
        _reason_v01(reasons, "cross_profile_permission_ref_mismatch")
    if not permission.allowed_adapter_ids:
        _reason_v01(reasons, "cross_profile_allowed_adapters_empty")
    if not permission.allowed_action_classes:
        _reason_v01(reasons, "cross_profile_allowed_actions_empty")
    if not permission.required_approval_refs:
        _reason_v01(reasons, "cross_profile_required_approvals_empty")
    if any(
        record.expected_accepting_local_root_id
        != value.owning_local_root_id
        for record in value.dependency_candidate.dependency_records
    ):
        _reason_v01(reasons, "cross_profile_dependency_root_mismatch")

    try:
        rebuilt_effect_profile = project_consequential_effect_parameters_v01(
            effect_class=candidate.effect_class,
            consequential_parameters=value.consequential_effect_parameters,
        )
        rebuilt_effect_fingerprint = (
            build_action_effect_parameters_fingerprint_v01(
                rebuilt_effect_profile
            )
        )
        rebuilt_dependency_fingerprint = (
            build_dependency_set_candidate_fingerprint_v01(
                value.dependency_candidate
            )
        )
        rebuilt_temporal_fingerprint = (
            build_temporal_authority_fingerprint_v01(value.temporal_authority)
        )
        rebuilt_policy_fingerprint = (
            build_action_authority_policy_fingerprint_v01(policy)
        )
        rebuilt_logical = build_root_owned_logical_effect_intent_v01(
            owning_effect_root_id=value.owning_local_root_id,
            transaction_id=value.transaction_id,
            logical_effect_class=candidate.effect_class,
            normalized_subject_scope=value.normalized_subject_scope,
            normalized_target_scope=value.normalized_target_scope,
            normalized_business_object_identity=business,
            normalized_consequential_effect_parameters=(
                value.consequential_effect_parameters
            ),
            logical_effect_namespace=policy.logical_effect_namespace,
        )
        rebuilt_idempotency = build_action_idempotency_identity_v01(
            owning_effect_root_id=value.owning_local_root_id,
            transaction_id=value.transaction_id,
            root_owned_intent_id=rebuilt_logical.root_owned_intent_id,
            logical_effect_class=candidate.effect_class,
            normalized_subject_scope=value.normalized_subject_scope,
            normalized_target_scope=value.normalized_target_scope,
            normalized_business_object_identity=business,
            normalized_consequential_effect_parameters=(
                value.consequential_effect_parameters
            ),
            logical_effect_namespace=policy.logical_effect_namespace,
        )
        rebuilt_candidate = (
            build_root_bound_packet_authorization_candidate_v01(
                owning_local_root_id=value.owning_local_root_id,
                transaction_id=value.transaction_id,
                root_owned_intent_id=rebuilt_logical.root_owned_intent_id,
                effect_class=candidate.effect_class,
                normalized_subject_scope=value.normalized_subject_scope,
                normalized_target_scope=value.normalized_target_scope,
                normalized_permission_scope=permission,
                normalized_effect_parameters_fingerprint=(
                    rebuilt_effect_fingerprint
                ),
                corridor_class=candidate.corridor_class,
                adapter_binding=value.adapter_binding,
                dependency_set_candidate_fingerprint=(
                    rebuilt_dependency_fingerprint
                ),
                temporal_authority_fingerprint=rebuilt_temporal_fingerprint,
                policy_version=policy.policy_version,
                authority_policy_fingerprint=rebuilt_policy_fingerprint,
                predecessor_packet_id=candidate.predecessor_packet_id,
                supersession_reason_class=(
                    candidate.supersession_reason_class
                ),
            )
        )
    except ValueError:
        _reason_v01(reasons, "cross_profile_rebuild_failed")
    else:
        if rebuilt_effect_profile != value.normalized_effect_parameters:
            _reason_v01(reasons, "cross_profile_parameter_projection_mismatch")
        if (
            rebuilt_effect_fingerprint
            != value.normalized_effect_parameters_fingerprint
            or rebuilt_effect_fingerprint
            != candidate.normalized_effect_parameters_fingerprint
        ):
            _reason_v01(reasons, "cross_profile_effect_fingerprint_mismatch")
        if (
            rebuilt_dependency_fingerprint
            != value.dependency_set_candidate_fingerprint
            or rebuilt_dependency_fingerprint
            != candidate.dependency_set_candidate_fingerprint
        ):
            _reason_v01(reasons, "cross_profile_dependency_fingerprint_mismatch")
        if (
            rebuilt_temporal_fingerprint
            != value.temporal_authority_fingerprint
            or rebuilt_temporal_fingerprint
            != candidate.temporal_authority_fingerprint
        ):
            _reason_v01(reasons, "cross_profile_temporal_fingerprint_mismatch")
        if (
            rebuilt_policy_fingerprint != value.authority_policy_fingerprint
            or rebuilt_policy_fingerprint
            != candidate.authority_policy_fingerprint
        ):
            _reason_v01(reasons, "cross_profile_policy_fingerprint_mismatch")
        if rebuilt_logical != logical:
            _reason_v01(reasons, "cross_profile_logical_intent_rebuild_mismatch")
        if rebuilt_idempotency != idempotency:
            _reason_v01(reasons, "cross_profile_idempotency_rebuild_mismatch")
        if rebuilt_candidate != candidate:
            _reason_v01(reasons, "cross_profile_candidate_rebuild_mismatch")

    supplied_packet_values = (
        packet_identity,
        source_root_decision_id,
        source_root_decision_hash,
    )
    if any(item is not None for item in supplied_packet_values):
        if any(item is None for item in supplied_packet_values):
            _reason_v01(reasons, "cross_profile_packet_identity_input_partial")
        else:
            packet_valid, _ = validate_action_commit_packet_identity_v01(
                packet_identity,
                candidate=candidate,
                source_root_decision_id=source_root_decision_id,
                source_root_decision_hash=source_root_decision_hash,
            )
            if not packet_valid:
                _reason_v01(reasons, "cross_profile_packet_identity_mismatch")
    return _result_v01(reasons)


def validate_g2a1a_cross_profile_coherence_v01(
    value: object,
    *,
    selected_canonical_action: object = None,
    selected_canonical_adapter: object = None,
    packet_identity: object = None,
    source_root_decision_id: object = None,
    source_root_decision_hash: object = None,
) -> tuple[bool, tuple[str, ...]]:
    try:
        return _validate_g2a1a_cross_profile_coherence_impl_v01(
            value,
            selected_canonical_action=selected_canonical_action,
            selected_canonical_adapter=selected_canonical_adapter,
            packet_identity=packet_identity,
            source_root_decision_id=source_root_decision_id,
            source_root_decision_hash=source_root_decision_hash,
        )
    except Exception:
        return False, ("cross_profile_validation_invalid",)


def _validate_supplier_action_commit_packet_canonical_projection_impl_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    if type(value) is not SupplierActionCommitPacketCanonicalProjectionV01:
        return False, ("supplier_projection_type_invalid",)
    reasons: list[str] = []
    exact_source_valid, exact_source_reasons = (
        _validate_action_commit_packet_exact_types_v01(value.source_packet)
    )
    if not exact_source_valid:
        return False, (
            "supplier_projection_source_packet_type_invalid",
            *exact_source_reasons,
        )
    try:
        historical_valid, _ = validate_action_commit_packet_v02(
            value.source_packet
        )
    except Exception:
        historical_valid = False
    if not historical_valid:
        return False, ("supplier_projection_historical_packet_invalid",)

    transaction_valid, _ = validate_executable_transaction_id_v01(
        value.transaction_id
    )
    if not transaction_valid:
        _reason_v01(reasons, "supplier_projection_transaction_invalid")
    root_valid, _ = validate_identity_text_v01(value.owning_local_root_id)
    if not root_valid:
        _reason_v01(reasons, "supplier_projection_root_invalid")
    permission_valid, _ = validate_canonical_permission_ref_v01(
        value.canonical_permission_ref
    )
    if not permission_valid:
        _reason_v01(reasons, "supplier_projection_permission_invalid")
    evaluation_time_valid, _ = validate_signed_int64_v01(
        value.evaluation_time
    )
    if not evaluation_time_valid:
        _reason_v01(reasons, "supplier_projection_evaluation_time_invalid")
    if not validate_identity_text_v01(value.evaluation_time_source)[0]:
        _reason_v01(reasons, "supplier_projection_evaluation_source_invalid")
    if not validate_identity_text_v01(value.evaluation_context_id)[0]:
        _reason_v01(reasons, "supplier_projection_evaluation_context_invalid")
    if type(value.temporal_evaluation) is not TemporalEvaluationV01:
        _reason_v01(reasons, "supplier_projection_temporal_evaluation_invalid")
    elif (
        type(value.temporal_evaluation.outcome) is not str
        or type(value.temporal_evaluation.executable) is not bool
    ):
        _reason_v01(reasons, "supplier_projection_temporal_evaluation_invalid")
    else:
        try:
            derived_evaluation = evaluate_temporal_authority_v01(
                value.temporal_authority,
                evaluation_time=value.evaluation_time,
            )
        except ValueError:
            _reason_v01(
                reasons,
                "supplier_projection_temporal_evaluation_invalid",
            )
        else:
            if value.temporal_evaluation != derived_evaluation:
                _reason_v01(
                    reasons,
                    "supplier_projection_temporal_evaluation_mismatch",
                )

    direct_text_fields = (
        value.selected_legacy_action,
        value.selected_canonical_action,
        value.evaluation_time_source,
        value.evaluation_context_id,
        value.human_approval_evidence_ref,
        value.advisory_bsep_ref,
    )
    if any(not validate_identity_text_v01(item)[0] for item in direct_text_fields):
        _reason_v01(reasons, "supplier_projection_text_field_invalid")
    direct_tuple_fields = (
        value.raw_allowed_actions,
        value.raw_forbidden_actions,
        value.raw_allowed_adapters,
        value.raw_forbidden_adapters,
        value.advisory_drs_refs,
        value.advisory_avf_refs,
    )
    if any(
        not _validate_ordered_string_tuple_v01(item)[0]
        for item in direct_tuple_fields
    ):
        _reason_v01(reasons, "supplier_projection_tuple_field_invalid")

    historical_packet = value.source_packet

    exact_fields = (
        (
            value.selected_legacy_action,
            ACTION_MOCK_SUPPLIER_A_PAYMENT_ORDER,
            "supplier_projection_selected_legacy_action_mismatch",
        ),
        (
            value.selected_canonical_action,
            "mock_action:mock_supplier_a_payment_order",
            "supplier_projection_selected_canonical_action_mismatch",
        ),
        (
            value.raw_allowed_actions,
            historical_packet.scope.allowed_actions,
            "supplier_projection_raw_allowed_actions_mismatch",
        ),
        (
            value.raw_forbidden_actions,
            historical_packet.scope.forbidden_actions,
            "supplier_projection_raw_forbidden_actions_mismatch",
        ),
        (
            value.raw_allowed_adapters,
            historical_packet.scope.allowed_adapters,
            "supplier_projection_raw_allowed_adapters_mismatch",
        ),
        (
            value.raw_forbidden_adapters,
            historical_packet.scope.forbidden_adapters,
            "supplier_projection_raw_forbidden_adapters_mismatch",
        ),
        (
            value.human_approval_evidence_ref,
            historical_packet.human_approval_ref,
            "supplier_projection_human_approval_evidence_mismatch",
        ),
        (
            value.advisory_drs_refs,
            historical_packet.drs_refs,
            "supplier_projection_advisory_drs_mismatch",
        ),
        (
            value.advisory_avf_refs,
            historical_packet.avf_refs,
            "supplier_projection_advisory_avf_mismatch",
        ),
        (
            value.advisory_bsep_ref,
            historical_packet.bsep_ref,
            "supplier_projection_advisory_bsep_mismatch",
        ),
    )
    for actual, expected, reason in exact_fields:
        if actual != expected:
            _reason_v01(reasons, reason)

    if type(value.adapter_binding) is not ActionAdapterBindingProfileV01:
        _reason_v01(reasons, "adapter_binding_invalid")
        selected_adapter: object = None
    else:
        selected_adapter = value.adapter_binding.adapter_id
        if selected_adapter != "mock_adapter:mock_bank_sandbox":
            _reason_v01(
                reasons,
                "supplier_projection_selected_adapter_mismatch",
            )

    permission_scope = value.normalized_permission_scope
    if type(permission_scope) is not ActionPermissionScopeProfileV01:
        _reason_v01(reasons, "permission_scope_invalid")
    elif permission_scope.required_approval_refs != (
        value.canonical_permission_ref,
    ):
        _reason_v01(
            reasons,
            "supplier_projection_permission_singleton_mismatch",
        )

    raw_allowed_actions = (
        value.raw_allowed_actions
        if type(value.raw_allowed_actions) is tuple
        else ()
    )
    raw_forbidden_actions = (
        value.raw_forbidden_actions
        if type(value.raw_forbidden_actions) is tuple
        else ()
    )
    raw_allowed_adapters = (
        value.raw_allowed_adapters
        if type(value.raw_allowed_adapters) is tuple
        else ()
    )
    raw_forbidden_adapters = (
        value.raw_forbidden_adapters
        if type(value.raw_forbidden_adapters) is tuple
        else ()
    )
    raw_selected_action = value.selected_legacy_action
    raw_selected_adapter = historical_packet.adapter_binding.adapter_id
    if raw_selected_action not in raw_allowed_actions:
        _reason_v01(reasons, "supplier_projection_raw_action_not_allowed")
    if raw_selected_action in raw_forbidden_actions:
        _reason_v01(reasons, "supplier_projection_raw_action_forbidden")
    if raw_selected_adapter not in raw_allowed_adapters:
        _reason_v01(reasons, "supplier_projection_raw_adapter_not_allowed")
    if raw_selected_adapter in raw_forbidden_adapters:
        _reason_v01(reasons, "supplier_projection_raw_adapter_forbidden")

    try:
        action_projection = (
            build_legacy_effect_firewall_vocabulary_projection_v01(
                raw_identifier=raw_selected_action,
                identifier_kind="action",
                raw_allowed_identifiers=raw_allowed_actions,
                raw_forbidden_identifiers=raw_forbidden_actions,
            )
        )
        adapter_projection = (
            build_legacy_effect_firewall_vocabulary_projection_v01(
                raw_identifier=raw_selected_adapter,
                identifier_kind="adapter",
                raw_allowed_identifiers=raw_allowed_adapters,
                raw_forbidden_identifiers=raw_forbidden_adapters,
            )
        )
    except ValueError:
        _reason_v01(reasons, "supplier_projection_closed_mapping_invalid")
    except Exception:
        _reason_v01(reasons, "supplier_projection_closed_mapping_invalid")
    else:
        if action_projection.canonical_identifier != value.selected_canonical_action:
            _reason_v01(
                reasons,
                "supplier_projection_selected_action_mapping_mismatch",
            )
        if adapter_projection.canonical_identifier != selected_adapter:
            _reason_v01(
                reasons,
                "supplier_projection_selected_adapter_mapping_mismatch",
            )

    raw_identifiers = (
        raw_allowed_actions
        + raw_forbidden_actions
        + raw_allowed_adapters
        + raw_forbidden_adapters
    )
    if value.selected_canonical_action in raw_identifiers:
        _reason_v01(reasons, "supplier_projection_raw_action_in_canonical_slot")
    if selected_adapter in raw_identifiers:
        _reason_v01(reasons, "supplier_projection_raw_adapter_in_canonical_slot")

    if type(value.adapter_binding) is ActionAdapterBindingProfileV01:
        coherence_valid, coherence_reasons = (
            validate_g2a1a_cross_profile_coherence_v01(
                value,
                selected_canonical_action=value.selected_canonical_action,
                selected_canonical_adapter=value.adapter_binding.adapter_id,
            )
        )
        if not coherence_valid:
            for reason in coherence_reasons:
                _reason_v01(reasons, reason)
    if reasons:
        return _result_v01(reasons)

    try:
        expected = (
            _build_supplier_action_commit_packet_canonical_projection_unchecked_v01(
                value.source_packet,
                transaction_id=value.transaction_id,
                owning_local_root_id=value.owning_local_root_id,
                canonical_permission_ref=value.canonical_permission_ref,
                selected_legacy_action=value.selected_legacy_action,
                logical_effect_namespace=(
                    value.logical_intent.logical_effect_namespace
                ),
                business_object_namespace=(
                    value.business_object_identity.business_object_namespace
                ),
                corridor_class=value.authorization_candidate.corridor_class,
                adapter_version=value.adapter_binding.adapter_version,
                temporal_policy_version=(
                    value.temporal_authority.temporal_policy_version
                ),
                authority_policy=value.authority_policy,
                dependency_candidate=value.dependency_candidate,
                evaluation_time=value.evaluation_time,
                evaluation_time_source=value.evaluation_time_source,
                evaluation_context_id=value.evaluation_context_id,
                predecessor_packet_id=(
                    value.authorization_candidate.predecessor_packet_id
                ),
                supersession_reason_class=(
                    value.authorization_candidate.supersession_reason_class
                ),
            )
        )
    except ValueError:
        return False, ("supplier_projection_source_rebuild_invalid",)
    except Exception:
        return False, ("supplier_projection_source_rebuild_invalid",)
    for field_name in SupplierActionCommitPacketCanonicalProjectionV01.__dataclass_fields__:
        actual = getattr(value, field_name)
        rebuilt = getattr(expected, field_name)
        if type(actual) is not type(rebuilt) or actual != rebuilt:
            _reason_v01(reasons, "supplier_projection_source_rebuild_mismatch")
    return _result_v01(reasons)


def validate_supplier_action_commit_packet_canonical_projection_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    try:
        return (
            _validate_supplier_action_commit_packet_canonical_projection_impl_v01(
                value
            )
        )
    except Exception:
        return False, ("supplier_projection_validation_invalid",)


def _canonical_revocation_evidence_v01(
    evidence_refs: object,
    evidence_hashes: object,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    if type(evidence_refs) is not tuple or type(evidence_hashes) is not tuple:
        raise ValueError("revocation_candidate_evidence_tuple_invalid")
    if not evidence_refs:
        raise ValueError("revocation_candidate_evidence_empty")
    if len(evidence_refs) != len(evidence_hashes):
        raise ValueError("revocation_candidate_evidence_cardinality_invalid")
    pairs: list[tuple[str, str]] = []
    seen: set[str] = set()
    for evidence_ref, evidence_hash in zip(
        evidence_refs,
        evidence_hashes,
        strict=True,
    ):
        if type(evidence_ref) is not str or type(evidence_hash) is not str:
            raise ValueError("revocation_candidate_evidence_type_invalid")
        normalized_ref = normalize_identity_text_v01(evidence_ref)
        hash_valid, hash_reasons = validate_lowercase_sha256_hex_v01(
            evidence_hash
        )
        if not hash_valid:
            raise ValueError(hash_reasons[0])
        if normalized_ref in seen:
            raise ValueError("revocation_candidate_evidence_duplicate")
        seen.add(normalized_ref)
        pairs.append((normalized_ref, evidence_hash))
    pairs.sort(key=lambda item: item[0].encode("utf-8"))
    return (
        tuple(item[0] for item in pairs),
        tuple(item[1] for item in pairs),
    )


def revocation_candidate_material_v01(
    value: RevocationCandidateV01,
) -> CanonicalMaterialV01:
    if type(value) is not RevocationCandidateV01:
        raise ValueError("revocation_candidate_type_invalid")
    return (
        ("candidate_profile_id", value.candidate_profile_id),
        ("owning_local_root_id", value.owning_local_root_id),
        ("packet_id", value.packet_id),
        (
            "source_authorization_decision_id",
            value.source_authorization_decision_id,
        ),
        ("idempotency_key", value.idempotency_key),
        ("revocation_reason_class", value.revocation_reason_class),
        ("evidence_refs", value.evidence_refs),
        ("evidence_hashes", value.evidence_hashes),
        ("evaluation_time", value.evaluation_time),
        ("policy_fingerprint", value.policy_fingerprint),
    )


def build_revocation_candidate_v01(
    *,
    owning_local_root_id: object,
    packet_id: object,
    source_authorization_decision_id: object,
    idempotency_key: object,
    revocation_reason_class: object,
    evidence_refs: object,
    evidence_hashes: object,
    evaluation_time: object,
    policy_fingerprint: object,
) -> RevocationCandidateV01:
    try:
        root_id = normalize_identity_text_v01(owning_local_root_id)
        reason_class = normalize_identity_text_v01(revocation_reason_class)
        valid_packet, packet_reasons = validate_prefixed_sha256_identity_v01(
            packet_id,
            prefix=ACTION_COMMIT_PACKET_ID_PREFIX_V01,
        )
        if not valid_packet:
            raise ValueError(packet_reasons[0])
        valid_decision, decision_reasons = validate_lowercase_sha256_hex_v01(
            source_authorization_decision_id
        )
        if not valid_decision:
            raise ValueError(decision_reasons[0])
        valid_key, key_reasons = validate_prefixed_sha256_identity_v01(
            idempotency_key,
            prefix=ACTION_IDEMPOTENCY_PREFIX_V01,
        )
        if not valid_key:
            raise ValueError(key_reasons[0])
        valid_time, time_reasons = validate_signed_int64_v01(evaluation_time)
        if not valid_time:
            raise ValueError(time_reasons[0])
        valid_policy, policy_reasons = validate_lowercase_sha256_hex_v01(
            policy_fingerprint
        )
        if not valid_policy:
            raise ValueError(policy_reasons[0])
        refs, hashes = _canonical_revocation_evidence_v01(
            evidence_refs,
            evidence_hashes,
        )
        provisional = RevocationCandidateV01(
            candidate_profile_id=REVOCATION_CANDIDATE_PROFILE_ID_V01,
            owning_local_root_id=root_id,
            packet_id=packet_id,
            source_authorization_decision_id=(
                source_authorization_decision_id
            ),
            idempotency_key=idempotency_key,
            revocation_reason_class=reason_class,
            evidence_refs=refs,
            evidence_hashes=hashes,
            evaluation_time=evaluation_time,
            policy_fingerprint=policy_fingerprint,
            revocation_candidate_id="",
        )
        candidate = RevocationCandidateV01(
            candidate_profile_id=provisional.candidate_profile_id,
            owning_local_root_id=provisional.owning_local_root_id,
            packet_id=provisional.packet_id,
            source_authorization_decision_id=(
                provisional.source_authorization_decision_id
            ),
            idempotency_key=provisional.idempotency_key,
            revocation_reason_class=provisional.revocation_reason_class,
            evidence_refs=provisional.evidence_refs,
            evidence_hashes=provisional.evidence_hashes,
            evaluation_time=provisional.evaluation_time,
            policy_fingerprint=provisional.policy_fingerprint,
            revocation_candidate_id=build_domain_separated_identity_v01(
                domain=REVOCATION_CANDIDATE_DOMAIN_V01,
                prefix=REVOCATION_CANDIDATE_PREFIX_V01,
                material=revocation_candidate_material_v01(provisional),
            ),
        )
        valid, reasons = validate_revocation_candidate_v01(candidate)
        if not valid:
            raise ValueError(reasons[0])
        return candidate
    except ValueError as exc:
        raise ValueError(
            _stable_exception_reason_v01(
                exc,
                fallback="revocation_candidate_invalid",
            )
        ) from None
    except Exception:
        raise ValueError("revocation_candidate_invalid") from None


def validate_revocation_candidate_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    try:
        if type(value) is not RevocationCandidateV01:
            return False, ("revocation_candidate_type_invalid",)
        if (
            type(value.candidate_profile_id) is not str
            or value.candidate_profile_id
            != REVOCATION_CANDIDATE_PROFILE_ID_V01
            or type(value.owning_local_root_id) is not str
            or normalize_identity_text_v01(value.owning_local_root_id)
            != value.owning_local_root_id
            or type(value.revocation_reason_class) is not str
            or normalize_identity_text_v01(value.revocation_reason_class)
            != value.revocation_reason_class
        ):
            return False, ("revocation_candidate_field_invalid",)
        for identifier, prefix in (
            (value.packet_id, ACTION_COMMIT_PACKET_ID_PREFIX_V01),
            (value.idempotency_key, ACTION_IDEMPOTENCY_PREFIX_V01),
        ):
            valid, reasons = validate_prefixed_sha256_identity_v01(
                identifier,
                prefix=prefix,
            )
            if not valid:
                return False, reasons
        for digest in (
            value.source_authorization_decision_id,
            value.policy_fingerprint,
        ):
            valid, reasons = validate_lowercase_sha256_hex_v01(digest)
            if not valid:
                return False, reasons
        valid_time, time_reasons = validate_signed_int64_v01(
            value.evaluation_time
        )
        if not valid_time:
            return False, time_reasons
        refs, hashes = _canonical_revocation_evidence_v01(
            value.evidence_refs,
            value.evidence_hashes,
        )
        if (
            refs != value.evidence_refs
            or hashes != value.evidence_hashes
            or type(value.revocation_candidate_id) is not str
            or value.revocation_candidate_id
            != build_domain_separated_identity_v01(
                domain=REVOCATION_CANDIDATE_DOMAIN_V01,
                prefix=REVOCATION_CANDIDATE_PREFIX_V01,
                material=revocation_candidate_material_v01(value),
            )
        ):
            return False, ("revocation_candidate_identity_mismatch",)
        return True, ()
    except ValueError as exc:
        return False, (
            _stable_exception_reason_v01(
                exc,
                fallback="revocation_candidate_invalid",
            ),
        )
    except Exception:
        return False, ("revocation_candidate_invalid",)


def supersession_candidate_material_v01(
    value: SupersessionCandidateV01,
) -> CanonicalMaterialV01:
    if type(value) is not SupersessionCandidateV01:
        raise ValueError("supersession_candidate_type_invalid")
    return (
        ("owning_local_root_id", value.owning_local_root_id),
        ("predecessor_packet_id", value.predecessor_packet_id),
        (
            "successor_packet_authorization_candidate_id",
            value.successor_packet_authorization_candidate_id,
        ),
        ("stable_logical_intent_id", value.stable_logical_intent_id),
        ("idempotency_key", value.idempotency_key),
        ("supersession_reason_class", value.supersession_reason_class),
        ("policy_fingerprint", value.policy_fingerprint),
    )


def build_supersession_candidate_v01(
    *,
    owning_local_root_id: object,
    predecessor_packet_id: object,
    successor_packet_authorization_candidate_id: object,
    stable_logical_intent_id: object,
    idempotency_key: object,
    supersession_reason_class: object,
    policy_fingerprint: object,
) -> SupersessionCandidateV01:
    try:
        root_id = normalize_identity_text_v01(owning_local_root_id)
        reason_class = normalize_identity_text_v01(
            supersession_reason_class
        )
        checks = (
            (
                predecessor_packet_id,
                ACTION_COMMIT_PACKET_ID_PREFIX_V01,
            ),
            (
                successor_packet_authorization_candidate_id,
                ROOT_PACKET_AUTHORIZATION_PREFIX_V01,
            ),
            (stable_logical_intent_id, ROOT_LOGICAL_INTENT_PREFIX_V01),
            (idempotency_key, ACTION_IDEMPOTENCY_PREFIX_V01),
        )
        for identifier, prefix in checks:
            valid, reasons = validate_prefixed_sha256_identity_v01(
                identifier,
                prefix=prefix,
            )
            if not valid:
                raise ValueError(reasons[0])
        valid_policy, policy_reasons = validate_lowercase_sha256_hex_v01(
            policy_fingerprint
        )
        if not valid_policy:
            raise ValueError(policy_reasons[0])
        provisional = SupersessionCandidateV01(
            owning_local_root_id=root_id,
            predecessor_packet_id=predecessor_packet_id,
            successor_packet_authorization_candidate_id=(
                successor_packet_authorization_candidate_id
            ),
            stable_logical_intent_id=stable_logical_intent_id,
            idempotency_key=idempotency_key,
            supersession_reason_class=reason_class,
            policy_fingerprint=policy_fingerprint,
            supersession_candidate_id="",
        )
        candidate = SupersessionCandidateV01(
            owning_local_root_id=provisional.owning_local_root_id,
            predecessor_packet_id=provisional.predecessor_packet_id,
            successor_packet_authorization_candidate_id=(
                provisional.successor_packet_authorization_candidate_id
            ),
            stable_logical_intent_id=provisional.stable_logical_intent_id,
            idempotency_key=provisional.idempotency_key,
            supersession_reason_class=(
                provisional.supersession_reason_class
            ),
            policy_fingerprint=provisional.policy_fingerprint,
            supersession_candidate_id=build_domain_separated_identity_v01(
                domain=SUPERSESSION_CANDIDATE_DOMAIN_V01,
                prefix=SUPERSESSION_CANDIDATE_PREFIX_V01,
                material=supersession_candidate_material_v01(provisional),
            ),
        )
        valid, reasons = validate_supersession_candidate_v01(candidate)
        if not valid:
            raise ValueError(reasons[0])
        return candidate
    except ValueError as exc:
        raise ValueError(
            _stable_exception_reason_v01(
                exc,
                fallback="supersession_candidate_invalid",
            )
        ) from None
    except Exception:
        raise ValueError("supersession_candidate_invalid") from None


def validate_supersession_candidate_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    try:
        if type(value) is not SupersessionCandidateV01:
            return False, ("supersession_candidate_type_invalid",)
        if (
            type(value.owning_local_root_id) is not str
            or normalize_identity_text_v01(value.owning_local_root_id)
            != value.owning_local_root_id
            or type(value.supersession_reason_class) is not str
            or normalize_identity_text_v01(value.supersession_reason_class)
            != value.supersession_reason_class
        ):
            return False, ("supersession_candidate_field_invalid",)
        for identifier, prefix in (
            (
                value.predecessor_packet_id,
                ACTION_COMMIT_PACKET_ID_PREFIX_V01,
            ),
            (
                value.successor_packet_authorization_candidate_id,
                ROOT_PACKET_AUTHORIZATION_PREFIX_V01,
            ),
            (value.stable_logical_intent_id, ROOT_LOGICAL_INTENT_PREFIX_V01),
            (value.idempotency_key, ACTION_IDEMPOTENCY_PREFIX_V01),
        ):
            valid, reasons = validate_prefixed_sha256_identity_v01(
                identifier,
                prefix=prefix,
            )
            if not valid:
                return False, reasons
        policy_valid, policy_reasons = validate_lowercase_sha256_hex_v01(
            value.policy_fingerprint
        )
        if not policy_valid:
            return False, policy_reasons
        if (
            type(value.supersession_candidate_id) is not str
            or value.supersession_candidate_id
            != build_domain_separated_identity_v01(
                domain=SUPERSESSION_CANDIDATE_DOMAIN_V01,
                prefix=SUPERSESSION_CANDIDATE_PREFIX_V01,
                material=supersession_candidate_material_v01(value),
            )
        ):
            return False, ("supersession_candidate_identity_mismatch",)
        return True, ()
    except ValueError as exc:
        return False, (
            _stable_exception_reason_v01(
                exc,
                fallback="supersession_candidate_invalid",
            ),
        )
    except Exception:
        return False, ("supersession_candidate_invalid",)


def _validate_revocation_candidate_against_packet_core_v01(
    candidate: object,
    packet: object,
    *,
    packet_validation_result: tuple[bool, tuple[str, ...]] | None = None,
) -> tuple[bool, tuple[str, ...]]:
    try:
        candidate_valid, candidate_reasons = validate_revocation_candidate_v01(
            candidate
        )
        if not candidate_valid:
            return False, candidate_reasons
        packet_valid, packet_reasons = (
            packet_validation_result
            if packet_validation_result is not None
            else validate_supplier_root_bound_action_commit_packet_v02_projection_v01(
                packet
            )
        )
        if not packet_valid:
            return False, packet_reasons
        reasons: list[str] = []
        canonical = packet.canonical_projection
        source_decision_id = (
            packet.root_decision_projection.root_decision_result.decision_id
        )
        if candidate.owning_local_root_id != canonical.owning_local_root_id:
            _reason_v01(reasons, "revocation_candidate_root_mismatch")
        if candidate.packet_id != packet.packet_identity.packet_id:
            _reason_v01(reasons, "revocation_candidate_packet_mismatch")
        if candidate.source_authorization_decision_id != source_decision_id:
            _reason_v01(
                reasons,
                "revocation_candidate_source_authorization_mismatch",
            )
        if (
            candidate.idempotency_key
            != canonical.idempotency_identity.idempotency_key
        ):
            _reason_v01(reasons, "revocation_candidate_key_mismatch")
        if candidate.policy_fingerprint != canonical.authority_policy_fingerprint:
            _reason_v01(reasons, "revocation_candidate_policy_mismatch")
        return _result_v01(reasons)
    except Exception:
        return False, ("revocation_candidate_context_invalid",)


def validate_revocation_candidate_against_packet_v01(
    candidate: object,
    packet: object,
) -> tuple[bool, tuple[str, ...]]:
    return _validate_revocation_candidate_against_packet_core_v01(
        candidate,
        packet,
    )


def _validate_supersession_candidate_against_packets_core_v01(
    candidate: object,
    predecessor: object,
    successor: object,
    *,
    predecessor_validation_result: tuple[
        bool,
        tuple[str, ...],
    ]
    | None = None,
    successor_validation_result: tuple[
        bool,
        tuple[str, ...],
    ]
    | None = None,
) -> tuple[bool, tuple[str, ...]]:
    try:
        candidate_valid, candidate_reasons = (
            validate_supersession_candidate_v01(candidate)
        )
        if not candidate_valid:
            return False, candidate_reasons
        for packet, validation_result in (
            (predecessor, predecessor_validation_result),
            (successor, successor_validation_result),
        ):
            packet_valid, packet_reasons = (
                validation_result
                if validation_result is not None
                else validate_supplier_root_bound_action_commit_packet_v02_projection_v01(
                    packet
                )
            )
            if not packet_valid:
                return False, packet_reasons
        reasons: list[str] = []
        predecessor_canonical = predecessor.canonical_projection
        successor_canonical = successor.canonical_projection
        predecessor_candidate = predecessor_canonical.authorization_candidate
        successor_candidate = successor_canonical.authorization_candidate
        predecessor_decision = (
            predecessor.root_decision_projection.root_decision_result
            .decision_id
        )
        successor_decision = (
            successor.root_decision_projection.root_decision_result.decision_id
        )
        if predecessor.packet_identity.packet_id == successor.packet_identity.packet_id:
            _reason_v01(reasons, "supersession_packet_identity_not_distinct")
        if predecessor_decision == successor_decision:
            _reason_v01(reasons, "supersession_source_decision_not_distinct")
        if (
            predecessor_candidate.root_packet_authorization_candidate_id
            == successor_candidate.root_packet_authorization_candidate_id
        ):
            _reason_v01(
                reasons,
                "supersession_authorization_candidate_not_distinct",
            )
        roots = (
            candidate.owning_local_root_id,
            predecessor_canonical.owning_local_root_id,
            successor_canonical.owning_local_root_id,
        )
        if len(set(roots)) != 1:
            _reason_v01(reasons, "supersession_candidate_root_mismatch")
        if candidate.predecessor_packet_id != predecessor.packet_identity.packet_id:
            _reason_v01(reasons, "supersession_predecessor_mismatch")
        if (
            candidate.successor_packet_authorization_candidate_id
            != successor_candidate.root_packet_authorization_candidate_id
        ):
            _reason_v01(reasons, "supersession_successor_candidate_mismatch")
        if (
            candidate.stable_logical_intent_id
            != successor_canonical.logical_intent.root_owned_intent_id
        ):
            _reason_v01(reasons, "supersession_logical_intent_mismatch")
        if (
            candidate.idempotency_key
            != successor_canonical.idempotency_identity.idempotency_key
        ):
            _reason_v01(reasons, "supersession_idempotency_key_mismatch")
        if (
            predecessor_canonical.transaction_id
            != successor_canonical.transaction_id
        ):
            _reason_v01(reasons, "supersession_transaction_mismatch")
        if (
            candidate.policy_fingerprint
            != predecessor_canonical.authority_policy_fingerprint
        ):
            _reason_v01(reasons, "supersession_policy_mismatch")
        if (
            successor_candidate.predecessor_packet_id
            != predecessor.packet_identity.packet_id
            or successor_candidate.supersession_reason_class
            != candidate.supersession_reason_class
        ):
            _reason_v01(
                reasons,
                "supersession_authorization_predecessor_mismatch",
            )
        if candidate.supersession_reason_class == "RENEWAL" and (
            predecessor_canonical.logical_intent.root_owned_intent_id
            != successor_canonical.logical_intent.root_owned_intent_id
            or predecessor_canonical.idempotency_identity.idempotency_key
            != successor_canonical.idempotency_identity.idempotency_key
        ):
            _reason_v01(reasons, "supersession_renewal_identity_mismatch")
        return _result_v01(reasons)
    except Exception:
        return False, ("supersession_candidate_context_invalid",)


def validate_supersession_candidate_against_packets_v01(
    candidate: object,
    predecessor: object,
    successor: object,
) -> tuple[bool, tuple[str, ...]]:
    return _validate_supersession_candidate_against_packets_core_v01(
        candidate,
        predecessor,
        successor,
    )


def build_action_source_root_decision_hash_v01(result: object) -> str:
    if type(result) is not RootDecisionResultV01:
        raise ValueError("source_root_decision_result_type_invalid")
    try:
        projection = root_decision_result_to_plain_dict_v01(result)
        projection_bytes = canonical_json_bytes_v01(projection)
        return domain_separated_sha256_hex_v01(
            domain=ACTION_SOURCE_ROOT_DECISION_DOMAIN_V01,
            payload=projection_bytes,
        )
    except Exception:
        raise ValueError("source_root_decision_hash_invalid") from None


def _validate_root_decision_candidate_projection_impl_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    if type(value) is not RootDecisionCandidateProjectionV01:
        return False, ("root_candidate_projection_type_invalid",)
    reasons: list[str] = []
    candidate_profiles = {
        ROOT_DECISION_CANDIDATE_KIND_PACKET_AUTHORIZATION_V01: (
            ROOT_PACKET_AUTHORIZATION_PREFIX_V01,
            "root_packet_authorization_candidate",
        ),
        ROOT_DECISION_CANDIDATE_KIND_REVOCATION_V01: (
            REVOCATION_CANDIDATE_PREFIX_V01,
            ROOT_DECISION_CLAIM_PREDICATE_REVOCATION_V01,
        ),
        ROOT_DECISION_CANDIDATE_KIND_SUPERSESSION_V01: (
            SUPERSESSION_CANDIDATE_PREFIX_V01,
            ROOT_DECISION_CLAIM_PREDICATE_SUPERSESSION_V01,
        ),
    }
    if (
        type(value.candidate_kind) is not str
        or value.candidate_kind not in ROOT_DECISION_CANDIDATE_KINDS_V01
    ):
        _reason_v01(reasons, "root_candidate_kind_invalid")
    else:
        candidate_valid, _ = validate_prefixed_sha256_identity_v01(
            value.projected_candidate_id,
            prefix=candidate_profiles[value.candidate_kind][0],
        )
        if not candidate_valid:
            _reason_v01(reasons, "root_candidate_id_invalid")
    source_hash_valid, _ = validate_lowercase_sha256_hex_v01(
        value.source_root_decision_hash
    )
    if not source_hash_valid:
        _reason_v01(reasons, "source_root_decision_hash_invalid")
    if type(value.root_decision_kernel) is not RootDecisionKernelV01:
        _reason_v01(reasons, "root_candidate_kernel_type_invalid")
    if type(value.root_decision_input) is not RootDecisionInputV01:
        _reason_v01(reasons, "root_candidate_input_type_invalid")
    if type(value.root_decision_result) is not RootDecisionResultV01:
        _reason_v01(reasons, "root_candidate_result_type_invalid")
    if reasons:
        return _result_v01(reasons)

    if validate_root_decision_kernel_v01(value.root_decision_kernel) != ():
        _reason_v01(reasons, "root_candidate_kernel_invalid")
    if (
        validate_root_decision_input_v01(
            kernel=value.root_decision_kernel,
            decision_input=value.root_decision_input,
        )
        != ()
    ):
        _reason_v01(reasons, "root_candidate_input_invalid")
    if (
        validate_root_decision_result_v01(
            kernel=value.root_decision_kernel,
            decision_input=value.root_decision_input,
            result=value.root_decision_result,
        )
        != ()
    ):
        _reason_v01(reasons, "root_candidate_result_invalid")
    if reasons:
        return _result_v01(reasons)

    decision_input = value.root_decision_input
    result = value.root_decision_result
    if result.decision_input_id != decision_input.decision_input_id:
        _reason_v01(reasons, "root_candidate_decision_input_mismatch")
    if result.transaction_id != decision_input.transaction_id:
        _reason_v01(reasons, "root_candidate_transaction_mismatch")
    if result.target_root_id != decision_input.target_root_id:
        _reason_v01(reasons, "root_candidate_target_root_mismatch")
    if result.decision != "ACCEPT":
        _reason_v01(reasons, "root_candidate_accept_required")
    if result.reason_code != "validated_candidate_accepted":
        _reason_v01(reasons, "root_candidate_accept_reason_invalid")
    if result.root_commit_created is not True:
        _reason_v01(reasons, "root_candidate_commit_missing")
    if result.permission_created is not False:
        _reason_v01(reasons, "root_candidate_permission_creation_forbidden")
    if result.final_output_created is not False:
        _reason_v01(reasons, "root_candidate_final_output_forbidden")
    if result.effect_requested is not False:
        _reason_v01(reasons, "root_candidate_effect_request_forbidden")
    if result.selected_candidate_id != value.projected_candidate_id:
        _reason_v01(reasons, "root_candidate_result_selection_mismatch")

    try:
        input_plain = root_decision_input_to_plain_dict_v01(decision_input)
    except Exception:
        return False, ("root_candidate_input_projection_invalid",)
    review = input_plain.get("root_review_packet")
    post_vv = input_plain.get("post_vv_bundle")
    gt = input_plain.get("gt_advisory")
    policy = input_plain.get("policy_state")
    permission = input_plain.get("permission_state")
    temporal = input_plain.get("temporal_state")
    conflict = input_plain.get("conflict_state")
    if not all(
        type(item) is dict
        for item in (review, post_vv, gt, policy, permission, temporal, conflict)
    ):
        return False, ("root_candidate_input_projection_invalid",)

    synthesis = review.get("synthesis_proposal")
    claims = synthesis.get("normalized_claims") if type(synthesis) is dict else None
    if type(claims) is not list:
        _reason_v01(reasons, "root_candidate_review_claims_invalid")
    else:
        matching_claims = [
            claim
            for claim in claims
            if type(claim) is dict
            and claim.get("claim_id") == value.projected_candidate_id
        ]
        if len(matching_claims) != 1:
            _reason_v01(reasons, "root_candidate_review_claim_missing")
        else:
            claim = matching_claims[0]
            expected_object = {
                "candidate_id": value.projected_candidate_id,
                "candidate_kind": value.candidate_kind,
            }
            if (
                claim.get("predicate")
                != candidate_profiles[value.candidate_kind][1]
                or claim.get("object_or_value") != expected_object
            ):
                _reason_v01(reasons, "root_candidate_review_claim_invalid")
        for claim in claims:
            if type(claim) is not dict:
                _reason_v01(reasons, "root_candidate_review_claims_invalid")
                continue
            claim_object = claim.get("object_or_value")
            if (
                claim.get("claim_id") != value.projected_candidate_id
                and type(claim_object) is dict
                and claim_object.get("candidate_id")
                == value.projected_candidate_id
            ):
                _reason_v01(reasons, "root_candidate_identity_position_duplicate")
    if (
        review.get("root_decision_created") is not False
        or review.get("permission_created") is not False
        or review.get("final_output_created") is not False
    ):
        _reason_v01(reasons, "root_candidate_review_authority_invalid")

    validated_ids = post_vv.get("validated_candidate_ids")
    rejected_ids = post_vv.get("rejected_candidate_ids")
    if (
        type(validated_ids) is not list
        or validated_ids.count(value.projected_candidate_id) != 1
    ):
        _reason_v01(reasons, "root_candidate_post_vv_validated_missing")
    if (
        type(rejected_ids) is not list
        or value.projected_candidate_id in rejected_ids
    ):
        _reason_v01(reasons, "root_candidate_post_vv_rejected")

    candidate_ids = gt.get("candidate_ids")
    scores = gt.get("score_micros_by_candidate")
    if (
        type(candidate_ids) is not list
        or candidate_ids.count(value.projected_candidate_id) != 1
    ):
        _reason_v01(reasons, "root_candidate_gt_candidate_missing")
    if gt.get("selected_candidate_id") != value.projected_candidate_id:
        _reason_v01(reasons, "root_candidate_gt_selection_mismatch")
    if type(scores) is not dict or value.projected_candidate_id not in scores:
        _reason_v01(reasons, "root_candidate_gt_score_missing")
    if "rejected_candidate_ids" in gt or "blocked_candidate_ids" in gt:
        _reason_v01(reasons, "root_candidate_gt_prohibited_set_present")

    if (
        value.candidate_kind
        == ROOT_DECISION_CANDIDATE_KIND_PACKET_AUTHORIZATION_V01
    ):
        if (
            permission.get("permission_required") is not True
            or permission.get("user_permission_present") is not True
            or permission.get("permission_scope_valid") is not True
        ):
            _reason_v01(reasons, "root_candidate_permission_state_invalid")
        if not validate_canonical_permission_ref_v01(
            permission.get("permission_ref")
        )[0]:
            _reason_v01(reasons, "root_candidate_permission_ref_invalid")
    elif (
        permission.get("permission_required") is not False
        or permission.get("user_permission_present") is not False
        or permission.get("permission_scope_valid") is not True
        or permission.get("permission_ref") is not None
    ):
        _reason_v01(reasons, "root_candidate_permission_state_invalid")
    for key in (
        "identity_passed",
        "scope_passed",
        "hard_policy_passed",
        "allow_accept",
    ):
        if policy.get(key) is not True:
            _reason_v01(reasons, "root_candidate_policy_hard_predicate_failed")
    if (
        temporal.get("temporal_valid") is not True
        or temporal.get("expired") is not False
        or temporal.get("not_before_satisfied") is not True
    ):
        _reason_v01(reasons, "root_candidate_temporal_state_invalid")
    if conflict.get("material_unresolved_conflict") is not False:
        _reason_v01(reasons, "root_candidate_material_conflict")

    try:
        rebuilt_hash = build_action_source_root_decision_hash_v01(result)
    except ValueError:
        _reason_v01(reasons, "source_root_decision_hash_invalid")
    else:
        if value.source_root_decision_hash != rebuilt_hash:
            _reason_v01(reasons, "source_root_decision_hash_mismatch")
    return _result_v01(reasons)


def validate_root_decision_candidate_projection_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    try:
        return _validate_root_decision_candidate_projection_impl_v01(value)
    except Exception:
        return False, ("root_candidate_projection_invalid",)


def build_root_decision_candidate_projection_v01(
    *,
    candidate_kind: object,
    projected_candidate_id: object,
    root_decision_kernel: object,
    root_decision_input: object,
    root_decision_result: object,
) -> RootDecisionCandidateProjectionV01:
    try:
        source_hash = build_action_source_root_decision_hash_v01(
            root_decision_result
        )
        projection = RootDecisionCandidateProjectionV01(
            candidate_kind=candidate_kind,
            projected_candidate_id=projected_candidate_id,
            root_decision_kernel=root_decision_kernel,
            root_decision_input=root_decision_input,
            root_decision_result=root_decision_result,
            source_root_decision_hash=source_hash,
        )
        valid, reasons = validate_root_decision_candidate_projection_v01(
            projection
        )
        if not valid:
            raise ValueError(reasons[0])
        return projection
    except ValueError as exc:
        raise ValueError(
            _stable_exception_reason_v01(
                exc,
                fallback="root_candidate_projection_invalid",
            )
        ) from None
    except Exception:
        raise ValueError("root_candidate_projection_invalid") from None


def _validate_revocation_root_context_coherence_core_v01(
    candidate: object,
    root_projection: object,
    packet: object,
    *,
    packet_validation_result: tuple[bool, tuple[str, ...]] | None = None,
) -> tuple[bool, tuple[str, ...]]:
    try:
        context_valid, context_reasons = (
            _validate_revocation_candidate_against_packet_core_v01(
                candidate,
                packet,
                packet_validation_result=packet_validation_result,
            )
        )
        if not context_valid:
            return False, context_reasons
        root_valid, root_reasons = (
            validate_root_decision_candidate_projection_v01(root_projection)
        )
        if not root_valid:
            return False, root_reasons
        reasons: list[str] = []
        canonical = packet.canonical_projection
        source_result = packet.root_decision_projection.root_decision_result
        decision_input = root_projection.root_decision_input
        result = root_projection.root_decision_result
        if (
            root_projection.candidate_kind
            != ROOT_DECISION_CANDIDATE_KIND_REVOCATION_V01
            or root_projection.projected_candidate_id
            != candidate.revocation_candidate_id
        ):
            _reason_v01(reasons, "revocation_root_candidate_mismatch")
        if (
            decision_input.transaction_id != canonical.transaction_id
            or result.transaction_id != canonical.transaction_id
        ):
            _reason_v01(reasons, "revocation_root_transaction_mismatch")
        if (
            decision_input.target_root_id != canonical.owning_local_root_id
            or result.target_root_id != canonical.owning_local_root_id
        ):
            _reason_v01(reasons, "revocation_root_target_mismatch")
        plain = root_decision_input_to_plain_dict_v01(decision_input)
        policy = plain.get("policy_state")
        prior = plain.get("prior_root_state")
        if type(policy) is not dict or type(prior) is not dict:
            return False, ("revocation_root_input_projection_invalid",)
        if (
            policy.get("policy_id") != candidate.policy_fingerprint
            or candidate.policy_fingerprint
            != canonical.authority_policy_fingerprint
        ):
            _reason_v01(reasons, "revocation_root_policy_mismatch")
        source_decision_id = source_result.decision_id
        source_candidate_id = (
            canonical.authorization_candidate
            .root_packet_authorization_candidate_id
        )
        if (
            result.prior_decision_id != source_decision_id
            or prior.get("prior_decision_id") != source_decision_id
            or prior.get("prior_decision") != "ACCEPT"
            or prior.get("prior_selected_candidate_id")
            != source_candidate_id
        ):
            _reason_v01(reasons, "revocation_root_prior_state_mismatch")
        if result.decision_id == source_decision_id:
            _reason_v01(reasons, "revocation_root_decision_not_distinct")
        return _result_v01(reasons)
    except Exception:
        return False, ("revocation_root_context_invalid",)


def validate_revocation_root_context_coherence_v01(
    candidate: object,
    root_projection: object,
    packet: object,
) -> tuple[bool, tuple[str, ...]]:
    return _validate_revocation_root_context_coherence_core_v01(
        candidate,
        root_projection,
        packet,
    )


def _validate_supersession_root_context_coherence_core_v01(
    candidate: object,
    root_projection: object,
    predecessor: object,
    successor: object,
    *,
    predecessor_validation_result: tuple[
        bool,
        tuple[str, ...],
    ]
    | None = None,
    successor_validation_result: tuple[
        bool,
        tuple[str, ...],
    ]
    | None = None,
) -> tuple[bool, tuple[str, ...]]:
    try:
        context_valid, context_reasons = (
            _validate_supersession_candidate_against_packets_core_v01(
                candidate,
                predecessor,
                successor,
                predecessor_validation_result=(
                    predecessor_validation_result
                ),
                successor_validation_result=successor_validation_result,
            )
        )
        if not context_valid:
            return False, context_reasons
        root_valid, root_reasons = (
            validate_root_decision_candidate_projection_v01(root_projection)
        )
        if not root_valid:
            return False, root_reasons
        reasons: list[str] = []
        predecessor_canonical = predecessor.canonical_projection
        successor_canonical = successor.canonical_projection
        predecessor_result = (
            predecessor.root_decision_projection.root_decision_result
        )
        successor_result = (
            successor.root_decision_projection.root_decision_result
        )
        decision_input = root_projection.root_decision_input
        result = root_projection.root_decision_result
        if (
            root_projection.candidate_kind
            != ROOT_DECISION_CANDIDATE_KIND_SUPERSESSION_V01
            or root_projection.projected_candidate_id
            != candidate.supersession_candidate_id
        ):
            _reason_v01(reasons, "supersession_root_candidate_mismatch")
        transactions = (
            decision_input.transaction_id,
            result.transaction_id,
            predecessor_canonical.transaction_id,
            successor_canonical.transaction_id,
        )
        if len(set(transactions)) != 1:
            _reason_v01(reasons, "supersession_root_transaction_mismatch")
        roots = (
            decision_input.target_root_id,
            result.target_root_id,
            predecessor_canonical.owning_local_root_id,
            successor_canonical.owning_local_root_id,
        )
        if len(set(roots)) != 1:
            _reason_v01(reasons, "supersession_root_target_mismatch")
        plain = root_decision_input_to_plain_dict_v01(decision_input)
        policy = plain.get("policy_state")
        prior = plain.get("prior_root_state")
        if type(policy) is not dict or type(prior) is not dict:
            return False, ("supersession_root_input_projection_invalid",)
        if (
            policy.get("policy_id") != candidate.policy_fingerprint
            or candidate.policy_fingerprint
            != predecessor_canonical.authority_policy_fingerprint
        ):
            _reason_v01(reasons, "supersession_root_policy_mismatch")
        predecessor_decision_id = predecessor_result.decision_id
        predecessor_candidate_id = (
            predecessor_canonical.authorization_candidate
            .root_packet_authorization_candidate_id
        )
        if (
            result.prior_decision_id != predecessor_decision_id
            or prior.get("prior_decision_id") != predecessor_decision_id
            or prior.get("prior_decision") != "ACCEPT"
            or prior.get("prior_selected_candidate_id")
            != predecessor_candidate_id
        ):
            _reason_v01(reasons, "supersession_root_prior_state_mismatch")
        if result.decision_id in {
            predecessor_decision_id,
            successor_result.decision_id,
        }:
            _reason_v01(reasons, "supersession_root_decision_not_distinct")
        return _result_v01(reasons)
    except Exception:
        return False, ("supersession_root_context_invalid",)


def validate_supersession_root_context_coherence_v01(
    candidate: object,
    root_projection: object,
    predecessor: object,
    successor: object,
) -> tuple[bool, tuple[str, ...]]:
    return _validate_supersession_root_context_coherence_core_v01(
        candidate,
        root_projection,
        predecessor,
        successor,
    )


def accepted_revocation_binding_material_v01(
    value: AcceptedRevocationBindingV01,
) -> CanonicalMaterialV01:
    if type(value) is not AcceptedRevocationBindingV01:
        raise ValueError("accepted_revocation_binding_type_invalid")
    return (
        ("revocation_candidate_id", value.revocation_candidate_id),
        ("revocation_root_decision_id", value.revocation_root_decision_id),
        (
            "revocation_root_decision_hash",
            value.revocation_root_decision_hash,
        ),
        ("owning_local_root_id", value.owning_local_root_id),
        ("packet_id", value.packet_id),
        (
            "prior_authorization_decision_id",
            value.prior_authorization_decision_id,
        ),
    )


def validate_accepted_revocation_binding_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    try:
        if type(value) is not AcceptedRevocationBindingV01:
            return False, ("accepted_revocation_binding_type_invalid",)
        for identifier, prefix in (
            (
                value.revocation_candidate_id,
                REVOCATION_CANDIDATE_PREFIX_V01,
            ),
            (value.packet_id, ACTION_COMMIT_PACKET_ID_PREFIX_V01),
        ):
            valid, reasons = validate_prefixed_sha256_identity_v01(
                identifier,
                prefix=prefix,
            )
            if not valid:
                return False, reasons
        for digest in (
            value.revocation_root_decision_id,
            value.revocation_root_decision_hash,
            value.prior_authorization_decision_id,
        ):
            valid, reasons = validate_lowercase_sha256_hex_v01(digest)
            if not valid:
                return False, reasons
        if (
            value.revocation_root_decision_id
            == value.prior_authorization_decision_id
        ):
            return False, ("accepted_revocation_decision_not_distinct",)
        if (
            type(value.owning_local_root_id) is not str
            or normalize_identity_text_v01(value.owning_local_root_id)
            != value.owning_local_root_id
            or type(value.accepted_revocation_binding_id) is not str
            or value.accepted_revocation_binding_id
            != build_domain_separated_identity_v01(
                domain=ACCEPTED_REVOCATION_BINDING_DOMAIN_V01,
                prefix=ACCEPTED_REVOCATION_BINDING_PREFIX_V01,
                material=accepted_revocation_binding_material_v01(value),
            )
        ):
            return False, ("accepted_revocation_binding_identity_mismatch",)
        return True, ()
    except ValueError as exc:
        return False, (
            _stable_exception_reason_v01(
                exc,
                fallback="accepted_revocation_binding_invalid",
            ),
        )
    except Exception:
        return False, ("accepted_revocation_binding_invalid",)


def _build_expected_accepted_revocation_binding_v01(
    candidate: RevocationCandidateV01,
    root_projection: RootDecisionCandidateProjectionV01,
    packet: SupplierRootBoundActionCommitPacketV02ProjectionV01,
) -> AcceptedRevocationBindingV01:
    result = root_projection.root_decision_result
    provisional = AcceptedRevocationBindingV01(
        revocation_candidate_id=candidate.revocation_candidate_id,
        revocation_root_decision_id=result.decision_id,
        revocation_root_decision_hash=(
            root_projection.source_root_decision_hash
        ),
        owning_local_root_id=(
            packet.canonical_projection.owning_local_root_id
        ),
        packet_id=packet.packet_identity.packet_id,
        prior_authorization_decision_id=(
            packet.root_decision_projection.root_decision_result.decision_id
        ),
        accepted_revocation_binding_id="",
    )
    return AcceptedRevocationBindingV01(
        revocation_candidate_id=provisional.revocation_candidate_id,
        revocation_root_decision_id=provisional.revocation_root_decision_id,
        revocation_root_decision_hash=(
            provisional.revocation_root_decision_hash
        ),
        owning_local_root_id=provisional.owning_local_root_id,
        packet_id=provisional.packet_id,
        prior_authorization_decision_id=(
            provisional.prior_authorization_decision_id
        ),
        accepted_revocation_binding_id=build_domain_separated_identity_v01(
            domain=ACCEPTED_REVOCATION_BINDING_DOMAIN_V01,
            prefix=ACCEPTED_REVOCATION_BINDING_PREFIX_V01,
            material=accepted_revocation_binding_material_v01(provisional),
        ),
    )


def _validate_accepted_revocation_binding_against_context_v01(
    value: object,
    candidate: object,
    root_projection: object,
    packet: object,
    *,
    packet_validation_result: tuple[bool, tuple[str, ...]] | None = None,
) -> tuple[bool, tuple[str, ...]]:
    try:
        if not validate_accepted_revocation_binding_v01(value)[0]:
            return False, ("accepted_revocation_binding_context_invalid",)
        if not _validate_revocation_candidate_against_packet_core_v01(
            candidate,
            packet,
            packet_validation_result=packet_validation_result,
        )[0]:
            return False, ("accepted_revocation_binding_context_invalid",)
        if not _validate_revocation_root_context_coherence_core_v01(
            candidate,
            root_projection,
            packet,
            packet_validation_result=packet_validation_result,
        )[0]:
            return False, ("accepted_revocation_binding_context_invalid",)
        expected = _build_expected_accepted_revocation_binding_v01(
            candidate,
            root_projection,
            packet,
        )
        if (
            accepted_revocation_binding_material_v01(value)
            != accepted_revocation_binding_material_v01(expected)
            or value.accepted_revocation_binding_id
            != expected.accepted_revocation_binding_id
        ):
            return False, ("accepted_revocation_binding_context_invalid",)
        return True, ()
    except Exception:
        return False, ("accepted_revocation_binding_context_invalid",)


def build_accepted_revocation_binding_v01(
    *,
    candidate: object,
    root_projection: object,
    packet: object,
) -> AcceptedRevocationBindingV01:
    try:
        context_valid, context_reasons = (
            validate_revocation_root_context_coherence_v01(
                candidate,
                root_projection,
                packet,
            )
        )
        if not context_valid:
            raise ValueError(context_reasons[0])
        binding = _build_expected_accepted_revocation_binding_v01(
            candidate,
            root_projection,
            packet,
        )
        valid, reasons = validate_accepted_revocation_binding_v01(binding)
        if not valid:
            raise ValueError(reasons[0])
        return binding
    except ValueError as exc:
        raise ValueError(
            _stable_exception_reason_v01(
                exc,
                fallback="accepted_revocation_binding_invalid",
            )
        ) from None
    except Exception:
        raise ValueError("accepted_revocation_binding_invalid") from None


def accepted_supersession_binding_material_v01(
    value: AcceptedSupersessionBindingV01,
) -> CanonicalMaterialV01:
    if type(value) is not AcceptedSupersessionBindingV01:
        raise ValueError("accepted_supersession_binding_type_invalid")
    return (
        ("supersession_candidate_id", value.supersession_candidate_id),
        (
            "supersession_root_decision_id",
            value.supersession_root_decision_id,
        ),
        (
            "supersession_root_decision_hash",
            value.supersession_root_decision_hash,
        ),
        ("owning_local_root_id", value.owning_local_root_id),
        ("predecessor_packet_id", value.predecessor_packet_id),
        (
            "prior_authorization_decision_id",
            value.prior_authorization_decision_id,
        ),
    )


def validate_accepted_supersession_binding_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    try:
        if type(value) is not AcceptedSupersessionBindingV01:
            return False, ("accepted_supersession_binding_type_invalid",)
        for identifier, prefix in (
            (
                value.supersession_candidate_id,
                SUPERSESSION_CANDIDATE_PREFIX_V01,
            ),
            (
                value.predecessor_packet_id,
                ACTION_COMMIT_PACKET_ID_PREFIX_V01,
            ),
        ):
            valid, reasons = validate_prefixed_sha256_identity_v01(
                identifier,
                prefix=prefix,
            )
            if not valid:
                return False, reasons
        for digest in (
            value.supersession_root_decision_id,
            value.supersession_root_decision_hash,
            value.prior_authorization_decision_id,
        ):
            valid, reasons = validate_lowercase_sha256_hex_v01(digest)
            if not valid:
                return False, reasons
        if (
            value.supersession_root_decision_id
            == value.prior_authorization_decision_id
        ):
            return False, ("accepted_supersession_decision_not_distinct",)
        if (
            type(value.owning_local_root_id) is not str
            or normalize_identity_text_v01(value.owning_local_root_id)
            != value.owning_local_root_id
            or type(value.accepted_supersession_binding_id) is not str
            or value.accepted_supersession_binding_id
            != build_domain_separated_identity_v01(
                domain=ACCEPTED_SUPERSESSION_BINDING_DOMAIN_V01,
                prefix=ACCEPTED_SUPERSESSION_BINDING_PREFIX_V01,
                material=accepted_supersession_binding_material_v01(value),
            )
        ):
            return False, ("accepted_supersession_binding_identity_mismatch",)
        return True, ()
    except ValueError as exc:
        return False, (
            _stable_exception_reason_v01(
                exc,
                fallback="accepted_supersession_binding_invalid",
            ),
        )
    except Exception:
        return False, ("accepted_supersession_binding_invalid",)


def _build_expected_accepted_supersession_binding_v01(
    candidate: SupersessionCandidateV01,
    root_projection: RootDecisionCandidateProjectionV01,
    predecessor: SupplierRootBoundActionCommitPacketV02ProjectionV01,
) -> AcceptedSupersessionBindingV01:
    result = root_projection.root_decision_result
    predecessor_result = (
        predecessor.root_decision_projection.root_decision_result
    )
    provisional = AcceptedSupersessionBindingV01(
        supersession_candidate_id=candidate.supersession_candidate_id,
        supersession_root_decision_id=result.decision_id,
        supersession_root_decision_hash=(
            root_projection.source_root_decision_hash
        ),
        owning_local_root_id=(
            predecessor.canonical_projection.owning_local_root_id
        ),
        predecessor_packet_id=predecessor.packet_identity.packet_id,
        prior_authorization_decision_id=predecessor_result.decision_id,
        accepted_supersession_binding_id="",
    )
    return AcceptedSupersessionBindingV01(
        supersession_candidate_id=provisional.supersession_candidate_id,
        supersession_root_decision_id=(
            provisional.supersession_root_decision_id
        ),
        supersession_root_decision_hash=(
            provisional.supersession_root_decision_hash
        ),
        owning_local_root_id=provisional.owning_local_root_id,
        predecessor_packet_id=provisional.predecessor_packet_id,
        prior_authorization_decision_id=(
            provisional.prior_authorization_decision_id
        ),
        accepted_supersession_binding_id=build_domain_separated_identity_v01(
            domain=ACCEPTED_SUPERSESSION_BINDING_DOMAIN_V01,
            prefix=ACCEPTED_SUPERSESSION_BINDING_PREFIX_V01,
            material=accepted_supersession_binding_material_v01(provisional),
        ),
    )


def _validate_accepted_supersession_binding_against_context_v01(
    value: object,
    candidate: object,
    root_projection: object,
    predecessor: object,
    successor: object,
    *,
    predecessor_validation_result: tuple[
        bool,
        tuple[str, ...],
    ]
    | None = None,
    successor_validation_result: tuple[
        bool,
        tuple[str, ...],
    ]
    | None = None,
) -> tuple[bool, tuple[str, ...]]:
    try:
        if not validate_accepted_supersession_binding_v01(value)[0]:
            return False, ("accepted_supersession_binding_context_invalid",)
        if not _validate_supersession_candidate_against_packets_core_v01(
            candidate,
            predecessor,
            successor,
            predecessor_validation_result=predecessor_validation_result,
            successor_validation_result=successor_validation_result,
        )[0]:
            return False, ("accepted_supersession_binding_context_invalid",)
        if not _validate_supersession_root_context_coherence_core_v01(
            candidate,
            root_projection,
            predecessor,
            successor,
            predecessor_validation_result=predecessor_validation_result,
            successor_validation_result=successor_validation_result,
        )[0]:
            return False, ("accepted_supersession_binding_context_invalid",)
        expected = _build_expected_accepted_supersession_binding_v01(
            candidate,
            root_projection,
            predecessor,
        )
        if (
            accepted_supersession_binding_material_v01(value)
            != accepted_supersession_binding_material_v01(expected)
            or value.accepted_supersession_binding_id
            != expected.accepted_supersession_binding_id
        ):
            return False, ("accepted_supersession_binding_context_invalid",)
        return True, ()
    except Exception:
        return False, ("accepted_supersession_binding_context_invalid",)


def build_accepted_supersession_binding_v01(
    *,
    candidate: object,
    root_projection: object,
    predecessor: object,
    successor: object,
) -> AcceptedSupersessionBindingV01:
    try:
        context_valid, context_reasons = (
            validate_supersession_root_context_coherence_v01(
                candidate,
                root_projection,
                predecessor,
                successor,
            )
        )
        if not context_valid:
            raise ValueError(context_reasons[0])
        binding = _build_expected_accepted_supersession_binding_v01(
            candidate,
            root_projection,
            predecessor,
        )
        valid, reasons = validate_accepted_supersession_binding_v01(binding)
        if not valid:
            raise ValueError(reasons[0])
        return binding
    except ValueError as exc:
        raise ValueError(
            _stable_exception_reason_v01(
                exc,
                fallback="accepted_supersession_binding_invalid",
            )
        ) from None
    except Exception:
        raise ValueError("accepted_supersession_binding_invalid") from None


def _validate_mandatory_dependency_local_root_acceptance_core_v01(
    packet: object,
    *,
    packet_validation_result: tuple[bool, tuple[str, ...]] | None = None,
) -> tuple[bool, tuple[str, ...]]:
    try:
        packet_valid, packet_reasons = (
            packet_validation_result
            if packet_validation_result is not None
            else validate_supplier_root_bound_action_commit_packet_v02_projection_v01(
                packet
            )
        )
        if not packet_valid:
            return False, packet_reasons
        reasons: list[str] = []
        canonical = packet.canonical_projection
        records = canonical.dependency_candidate.dependency_records
        mandatory = tuple(
            record
            for record in records
            if record.requirement_class == "MANDATORY"
        )
        if not mandatory:
            _reason_v01(reasons, "mandatory_dependency_missing")
        dependency_ids: set[str] = set()
        for record in mandatory:
            if record.dependency_id in dependency_ids:
                _reason_v01(reasons, "mandatory_dependency_duplicate")
            dependency_ids.add(record.dependency_id)
            if (
                record.expected_accepting_local_root_id
                != canonical.owning_local_root_id
            ):
                _reason_v01(reasons, "mandatory_dependency_root_mismatch")
            if (
                type(record.dependency_id) is not str
                or type(record.evidence_ref) is not str
                or type(record.content_sha256) is not str
                or type(record.time_envelope_id) is not str
                or type(record.freshness_policy_id) is not str
            ):
                _reason_v01(reasons, "mandatory_dependency_field_invalid")
            recursive_values = (
                record.dependency_id,
                record.evidence_ref,
                record.time_envelope_id,
                record.freshness_policy_id,
                *record.source_provenance_refs,
            )
            if any(
                type(item) is str
                and item.startswith(
                    PACKET_DEPENDENCY_ACCEPTANCE_PREFIX_V01
                )
                for item in recursive_values
            ):
                _reason_v01(
                    reasons,
                    "mandatory_dependency_recursive_acceptance_binding",
                )
        binding = packet.dependency_acceptance_binding
        binding_valid, binding_reasons = (
            validate_packet_dependency_acceptance_binding_v01(binding)
        )
        if not binding_valid:
            return False, binding_reasons
        source_result = packet.root_decision_projection.root_decision_result
        expected = (
            canonical.dependency_set_candidate_fingerprint,
            canonical.authorization_candidate
            .root_packet_authorization_candidate_id,
            source_result.decision_id,
            packet.root_decision_projection.source_root_decision_hash,
            canonical.owning_local_root_id,
            packet.packet_identity.packet_id,
            "ROOT_ACCEPTED_FOR_PACKET",
        )
        actual = (
            binding.dependency_set_candidate_fingerprint,
            binding.root_packet_authorization_candidate_id,
            binding.source_root_decision_id,
            binding.source_root_decision_hash,
            binding.owning_local_root_id,
            binding.packet_id,
            binding.accepted_status,
        )
        if actual != expected or any(
            type(item) is not str for item in actual
        ):
            _reason_v01(reasons, "mandatory_dependency_acceptance_mismatch")
        return _result_v01(reasons)
    except Exception:
        return False, ("mandatory_dependency_acceptance_invalid",)


def validate_mandatory_dependency_local_root_acceptance_v01(
    packet: object,
) -> tuple[bool, tuple[str, ...]]:
    return _validate_mandatory_dependency_local_root_acceptance_core_v01(
        packet
    )


def action_invalidation_evidence_material_v01(
    value: ActionInvalidationEvidenceV01,
) -> CanonicalMaterialV01:
    if type(value) is not ActionInvalidationEvidenceV01:
        raise ValueError("action_invalidation_evidence_type_invalid")
    return (
        ("profile_id", value.profile_id),
        (
            "source_invalidation_event_ref",
            value.source_invalidation_event_ref,
        ),
        ("packet_id", value.packet_id),
        ("dependency_id", value.dependency_id),
        ("invalidation_class", value.invalidation_class),
        ("evidence_ref", value.evidence_ref),
        ("evidence_sha256", value.evidence_sha256),
        ("observed_status", value.observed_status),
        ("time_envelope_id", value.time_envelope_id),
        ("freshness_policy_id", value.freshness_policy_id),
        ("owning_local_root_id", value.owning_local_root_id),
        ("accepted_by_local_root_id", value.accepted_by_local_root_id),
        (
            "acceptance_root_decision_id",
            _optional_identity_material_v01(
                value.acceptance_root_decision_id
            ),
        ),
        (
            "acceptance_root_decision_hash",
            _optional_identity_material_v01(
                value.acceptance_root_decision_hash
            ),
        ),
        ("validation_status", value.validation_status),
        ("authority_effect", value.authority_effect),
        (
            "root_decision_ref",
            _optional_identity_material_v01(value.root_decision_ref),
        ),
        ("evaluation_time", value.evaluation_time),
        ("evaluation_time_source", value.evaluation_time_source),
        ("evaluation_context_id", value.evaluation_context_id),
    )


def _validate_action_invalidation_root_positions_v01(
    *,
    authority_effect: str,
    acceptance_root_decision_id: object,
    acceptance_root_decision_hash: object,
    root_decision_ref: object,
) -> tuple[str | None, str | None, str | None]:
    values = (
        acceptance_root_decision_id,
        acceptance_root_decision_hash,
        root_decision_ref,
    )
    if authority_effect == "DETERMINISTIC_BLOCK":
        if any(value is not None for value in values):
            raise ValueError("action_invalidation_root_position_invalid")
        return None, None, None
    if any(type(value) is not str for value in values):
        raise ValueError("action_invalidation_root_position_invalid")
    decision_valid, decision_reasons = validate_lowercase_sha256_hex_v01(
        acceptance_root_decision_id
    )
    hash_valid, hash_reasons = validate_lowercase_sha256_hex_v01(
        acceptance_root_decision_hash
    )
    ref_valid, ref_reasons = validate_lowercase_sha256_hex_v01(
        root_decision_ref
    )
    if not decision_valid:
        raise ValueError(decision_reasons[0])
    if not hash_valid:
        raise ValueError(hash_reasons[0])
    if not ref_valid:
        raise ValueError(ref_reasons[0])
    if acceptance_root_decision_id != root_decision_ref:
        raise ValueError("action_invalidation_root_decision_mismatch")
    return (
        acceptance_root_decision_id,
        acceptance_root_decision_hash,
        root_decision_ref,
    )


def build_action_invalidation_evidence_v01(
    *,
    source_invalidation_event_ref: object,
    packet_id: object,
    dependency_id: object,
    invalidation_class: object,
    evidence_ref: object,
    evidence_sha256: object,
    observed_status: object,
    time_envelope_id: object,
    freshness_policy_id: object,
    owning_local_root_id: object,
    accepted_by_local_root_id: object,
    acceptance_root_decision_id: object = None,
    acceptance_root_decision_hash: object = None,
    authority_effect: object,
    root_decision_ref: object = None,
    evaluation_time: object,
    evaluation_time_source: object,
    evaluation_context_id: object,
) -> ActionInvalidationEvidenceV01:
    try:
        text_values = tuple(
            normalize_identity_text_v01(value)
            for value in (
                source_invalidation_event_ref,
                dependency_id,
                evidence_ref,
                observed_status,
                time_envelope_id,
                freshness_policy_id,
                owning_local_root_id,
                accepted_by_local_root_id,
                evaluation_time_source,
                evaluation_context_id,
            )
        )
        (
            source_ref,
            dependency,
            normalized_evidence_ref,
            status,
            time_envelope,
            freshness_policy,
            owning_root,
            accepting_root,
            evaluation_source,
            evaluation_context,
        ) = text_values
        if type(invalidation_class) is not str or (
            invalidation_class not in ACTION_INVALIDATION_CLASSES_V01
        ):
            raise ValueError("action_invalidation_class_invalid")
        if type(authority_effect) is not str or (
            authority_effect not in ACTION_INVALIDATION_AUTHORITY_EFFECTS_V01
        ):
            raise ValueError("action_invalidation_authority_effect_invalid")
        expected_effect = {
            "DEPENDENCY_CHANGED": "DETERMINISTIC_BLOCK",
            "DEPENDENCY_STALE": "DETERMINISTIC_BLOCK",
            "ROOT_BOUND_KILL_SWITCH": "DETERMINISTIC_BLOCK",
            "MANUAL_CANCEL_EVIDENCE": "DETERMINISTIC_BLOCK",
            "ROOT_REVOCATION": "ROOT_REVOCATION",
            "ROOT_SUPERSESSION": "ROOT_SUPERSESSION",
        }[invalidation_class]
        if authority_effect != expected_effect:
            raise ValueError("action_invalidation_class_effect_mismatch")
        packet_valid, packet_reasons = validate_prefixed_sha256_identity_v01(
            packet_id,
            prefix=ACTION_COMMIT_PACKET_ID_PREFIX_V01,
        )
        if not packet_valid:
            raise ValueError(packet_reasons[0])
        evidence_hash_valid, evidence_hash_reasons = (
            validate_lowercase_sha256_hex_v01(evidence_sha256)
        )
        if not evidence_hash_valid:
            raise ValueError(evidence_hash_reasons[0])
        time_valid, time_reasons = validate_signed_int64_v01(evaluation_time)
        if not time_valid:
            raise ValueError(time_reasons[0])
        decision_id, decision_hash, decision_ref = (
            _validate_action_invalidation_root_positions_v01(
                authority_effect=authority_effect,
                acceptance_root_decision_id=acceptance_root_decision_id,
                acceptance_root_decision_hash=(
                    acceptance_root_decision_hash
                ),
                root_decision_ref=root_decision_ref,
            )
        )
        provisional = ActionInvalidationEvidenceV01(
            profile_id=ACTION_INVALIDATION_EVIDENCE_PROFILE_ID_V01,
            source_invalidation_event_ref=source_ref,
            packet_id=packet_id,
            dependency_id=dependency,
            invalidation_class=invalidation_class,
            evidence_ref=normalized_evidence_ref,
            evidence_sha256=evidence_sha256,
            observed_status=status,
            time_envelope_id=time_envelope,
            freshness_policy_id=freshness_policy,
            owning_local_root_id=owning_root,
            accepted_by_local_root_id=accepting_root,
            acceptance_root_decision_id=decision_id,
            acceptance_root_decision_hash=decision_hash,
            validation_status=ACTION_INVALIDATION_VALIDATION_STATUS_V01,
            authority_effect=authority_effect,
            root_decision_ref=decision_ref,
            evaluation_time=evaluation_time,
            evaluation_time_source=evaluation_source,
            evaluation_context_id=evaluation_context,
            invalidation_evidence_id="",
        )
        identity = domain_separated_sha256_hex_v01(
            domain=ACTION_INVALIDATION_EVIDENCE_DOMAIN_V01,
            payload=canonical_material_bytes_v01(
                action_invalidation_evidence_material_v01(provisional)
            ),
        )
        if source_ref == identity:
            raise ValueError("action_invalidation_self_reference_forbidden")
        evidence = ActionInvalidationEvidenceV01(
            profile_id=provisional.profile_id,
            source_invalidation_event_ref=(
                provisional.source_invalidation_event_ref
            ),
            packet_id=provisional.packet_id,
            dependency_id=provisional.dependency_id,
            invalidation_class=provisional.invalidation_class,
            evidence_ref=provisional.evidence_ref,
            evidence_sha256=provisional.evidence_sha256,
            observed_status=provisional.observed_status,
            time_envelope_id=provisional.time_envelope_id,
            freshness_policy_id=provisional.freshness_policy_id,
            owning_local_root_id=provisional.owning_local_root_id,
            accepted_by_local_root_id=(
                provisional.accepted_by_local_root_id
            ),
            acceptance_root_decision_id=(
                provisional.acceptance_root_decision_id
            ),
            acceptance_root_decision_hash=(
                provisional.acceptance_root_decision_hash
            ),
            validation_status=provisional.validation_status,
            authority_effect=provisional.authority_effect,
            root_decision_ref=provisional.root_decision_ref,
            evaluation_time=provisional.evaluation_time,
            evaluation_time_source=provisional.evaluation_time_source,
            evaluation_context_id=provisional.evaluation_context_id,
            invalidation_evidence_id=identity,
        )
        valid, reasons = validate_action_invalidation_evidence_v01(evidence)
        if not valid:
            raise ValueError(reasons[0])
        return evidence
    except ValueError as exc:
        raise ValueError(
            _stable_exception_reason_v01(
                exc,
                fallback="action_invalidation_evidence_invalid",
            )
        ) from None
    except Exception:
        raise ValueError("action_invalidation_evidence_invalid") from None


def validate_action_invalidation_evidence_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    try:
        if type(value) is not ActionInvalidationEvidenceV01:
            return False, ("action_invalidation_evidence_type_invalid",)
        if (
            type(value.profile_id) is not str
            or value.profile_id
            != ACTION_INVALIDATION_EVIDENCE_PROFILE_ID_V01
            or type(value.validation_status) is not str
            or value.validation_status
            != ACTION_INVALIDATION_VALIDATION_STATUS_V01
            or type(value.invalidation_class) is not str
            or value.invalidation_class not in ACTION_INVALIDATION_CLASSES_V01
            or type(value.authority_effect) is not str
            or value.authority_effect
            not in ACTION_INVALIDATION_AUTHORITY_EFFECTS_V01
        ):
            return False, ("action_invalidation_evidence_field_invalid",)
        expected_effect = {
            "DEPENDENCY_CHANGED": "DETERMINISTIC_BLOCK",
            "DEPENDENCY_STALE": "DETERMINISTIC_BLOCK",
            "ROOT_BOUND_KILL_SWITCH": "DETERMINISTIC_BLOCK",
            "MANUAL_CANCEL_EVIDENCE": "DETERMINISTIC_BLOCK",
            "ROOT_REVOCATION": "ROOT_REVOCATION",
            "ROOT_SUPERSESSION": "ROOT_SUPERSESSION",
        }[value.invalidation_class]
        if value.authority_effect != expected_effect:
            return False, ("action_invalidation_class_effect_mismatch",)
        for text_value in (
            value.source_invalidation_event_ref,
            value.dependency_id,
            value.evidence_ref,
            value.observed_status,
            value.time_envelope_id,
            value.freshness_policy_id,
            value.owning_local_root_id,
            value.accepted_by_local_root_id,
            value.evaluation_time_source,
            value.evaluation_context_id,
        ):
            if (
                type(text_value) is not str
                or normalize_identity_text_v01(text_value) != text_value
            ):
                return False, ("action_invalidation_evidence_text_invalid",)
        packet_valid, packet_reasons = validate_prefixed_sha256_identity_v01(
            value.packet_id,
            prefix=ACTION_COMMIT_PACKET_ID_PREFIX_V01,
        )
        if not packet_valid:
            return False, packet_reasons
        hash_valid, hash_reasons = validate_lowercase_sha256_hex_v01(
            value.evidence_sha256
        )
        if not hash_valid:
            return False, hash_reasons
        time_valid, time_reasons = validate_signed_int64_v01(
            value.evaluation_time
        )
        if not time_valid:
            return False, time_reasons
        _validate_action_invalidation_root_positions_v01(
            authority_effect=value.authority_effect,
            acceptance_root_decision_id=value.acceptance_root_decision_id,
            acceptance_root_decision_hash=(
                value.acceptance_root_decision_hash
            ),
            root_decision_ref=value.root_decision_ref,
        )
        expected_id = domain_separated_sha256_hex_v01(
            domain=ACTION_INVALIDATION_EVIDENCE_DOMAIN_V01,
            payload=canonical_material_bytes_v01(
                action_invalidation_evidence_material_v01(value)
            ),
        )
        if (
            type(value.invalidation_evidence_id) is not str
            or value.invalidation_evidence_id != expected_id
            or value.source_invalidation_event_ref == expected_id
        ):
            return False, ("action_invalidation_evidence_identity_mismatch",)
        return True, ()
    except ValueError as exc:
        return False, (
            _stable_exception_reason_v01(
                exc,
                fallback="action_invalidation_evidence_invalid",
            ),
        )
    except Exception:
        return False, ("action_invalidation_evidence_invalid",)


def _validate_action_invalidation_evidence_against_packet_core_v01(
    evidence: object,
    packet: object,
    *,
    revocation_candidate: object = None,
    revocation_root_projection: object = None,
    accepted_revocation_binding: object = None,
    supersession_candidate: object = None,
    supersession_root_projection: object = None,
    supersession_successor: object = None,
    accepted_supersession_binding: object = None,
    packet_validation_result: tuple[bool, tuple[str, ...]] | None = None,
    successor_validation_result: tuple[
        bool,
        tuple[str, ...],
    ]
    | None = None,
) -> tuple[bool, tuple[str, ...]]:
    try:
        evidence_valid, evidence_reasons = (
            validate_action_invalidation_evidence_v01(evidence)
        )
        if not evidence_valid:
            return False, evidence_reasons
        dependency_valid, dependency_reasons = (
            _validate_mandatory_dependency_local_root_acceptance_core_v01(
                packet,
                packet_validation_result=packet_validation_result,
            )
        )
        if not dependency_valid:
            return False, dependency_reasons
        reasons: list[str] = []
        canonical = packet.canonical_projection
        if evidence.packet_id != packet.packet_identity.packet_id:
            _reason_v01(reasons, "action_invalidation_packet_mismatch")
        if (
            evidence.owning_local_root_id != canonical.owning_local_root_id
            or evidence.accepted_by_local_root_id
            != canonical.owning_local_root_id
        ):
            _reason_v01(reasons, "action_invalidation_root_mismatch")
        if evidence.invalidation_class in {
            "DEPENDENCY_CHANGED",
            "DEPENDENCY_STALE",
        }:
            matching = tuple(
                record
                for record in canonical.dependency_candidate.dependency_records
                if record.requirement_class == "MANDATORY"
                and record.dependency_id == evidence.dependency_id
            )
            if len(matching) != 1:
                _reason_v01(
                    reasons,
                    "action_invalidation_mandatory_dependency_mismatch",
                )
            else:
                record = matching[0]
                if (
                    evidence.evidence_ref != record.evidence_ref
                    or evidence.time_envelope_id != record.time_envelope_id
                    or evidence.freshness_policy_id
                    != record.freshness_policy_id
                ):
                    _reason_v01(
                        reasons,
                        "action_invalidation_dependency_binding_mismatch",
                    )
        elif evidence.invalidation_class in {
            "ROOT_BOUND_KILL_SWITCH",
            "MANUAL_CANCEL_EVIDENCE",
        }:
            if (
                evidence.dependency_id
                not in canonical.authority_policy.kill_switch_condition_refs
            ):
                _reason_v01(
                    reasons,
                    "action_invalidation_policy_condition_mismatch",
                )
        elif evidence.invalidation_class == "ROOT_REVOCATION":
            binding_context_valid, _ = (
                _validate_accepted_revocation_binding_against_context_v01(
                    accepted_revocation_binding,
                    revocation_candidate,
                    revocation_root_projection,
                    packet,
                    packet_validation_result=packet_validation_result,
                )
            )
            if not binding_context_valid:
                _reason_v01(
                    reasons,
                    "action_invalidation_revocation_binding_invalid",
                )
            else:
                binding = accepted_revocation_binding
                digest = binding.accepted_revocation_binding_id[
                    len(ACCEPTED_REVOCATION_BINDING_PREFIX_V01) :
                ]
                if (
                    evidence.evidence_ref
                    != binding.accepted_revocation_binding_id
                    or evidence.evidence_sha256 != digest
                    or evidence.acceptance_root_decision_id
                    != binding.revocation_root_decision_id
                    or evidence.root_decision_ref
                    != binding.revocation_root_decision_id
                    or evidence.acceptance_root_decision_hash
                    != binding.revocation_root_decision_hash
                    or binding.packet_id != packet.packet_identity.packet_id
                    or binding.owning_local_root_id
                    != canonical.owning_local_root_id
                    or binding.prior_authorization_decision_id
                    != packet.root_decision_projection.root_decision_result
                    .decision_id
                ):
                    _reason_v01(
                        reasons,
                        "action_invalidation_revocation_binding_mismatch",
                    )
        elif evidence.invalidation_class == "ROOT_SUPERSESSION":
            binding_context_valid, _ = (
                _validate_accepted_supersession_binding_against_context_v01(
                    accepted_supersession_binding,
                    supersession_candidate,
                    supersession_root_projection,
                    packet,
                    supersession_successor,
                    predecessor_validation_result=packet_validation_result,
                    successor_validation_result=successor_validation_result,
                )
            )
            if not binding_context_valid:
                _reason_v01(
                    reasons,
                    "action_invalidation_supersession_binding_invalid",
                )
            else:
                binding = accepted_supersession_binding
                digest = binding.accepted_supersession_binding_id[
                    len(ACCEPTED_SUPERSESSION_BINDING_PREFIX_V01) :
                ]
                if (
                    evidence.evidence_ref
                    != binding.accepted_supersession_binding_id
                    or evidence.evidence_sha256 != digest
                    or evidence.acceptance_root_decision_id
                    != binding.supersession_root_decision_id
                    or evidence.root_decision_ref
                    != binding.supersession_root_decision_id
                    or evidence.acceptance_root_decision_hash
                    != binding.supersession_root_decision_hash
                    or binding.predecessor_packet_id
                    != packet.packet_identity.packet_id
                    or binding.owning_local_root_id
                    != canonical.owning_local_root_id
                    or binding.prior_authorization_decision_id
                    != packet.root_decision_projection.root_decision_result
                    .decision_id
                ):
                    _reason_v01(
                        reasons,
                        "action_invalidation_supersession_binding_mismatch",
                    )
        return _result_v01(reasons)
    except Exception:
        return False, ("action_invalidation_context_invalid",)


def validate_action_invalidation_evidence_against_packet_v01(
    evidence: object,
    packet: object,
    *,
    revocation_candidate: object = None,
    revocation_root_projection: object = None,
    accepted_revocation_binding: object = None,
    supersession_candidate: object = None,
    supersession_root_projection: object = None,
    supersession_successor: object = None,
    accepted_supersession_binding: object = None,
) -> tuple[bool, tuple[str, ...]]:
    return _validate_action_invalidation_evidence_against_packet_core_v01(
        evidence,
        packet,
        revocation_candidate=revocation_candidate,
        revocation_root_projection=revocation_root_projection,
        accepted_revocation_binding=accepted_revocation_binding,
        supersession_candidate=supersession_candidate,
        supersession_root_projection=supersession_root_projection,
        supersession_successor=supersession_successor,
        accepted_supersession_binding=accepted_supersession_binding,
    )


def _validate_action_packet_invalidation_context_core_v01(
    value: object,
    packet: object,
    *,
    supersession_successor: object = None,
    validation_pass: _ActionPacketRegistryValidationPassV01 | None = None,
) -> tuple[bool, tuple[str, ...]]:
    try:
        if type(value) is not _ActionPacketInvalidationContextV01:
            return False, ("action_packet_invalidation_context_type_invalid",)
        evidence = value.invalidation_evidence
        if type(evidence) is not ActionInvalidationEvidenceV01:
            return False, ("action_packet_invalidation_evidence_invalid",)
        deterministic = evidence.invalidation_class in {
            "DEPENDENCY_CHANGED",
            "DEPENDENCY_STALE",
            "ROOT_BOUND_KILL_SWITCH",
            "MANUAL_CANCEL_EVIDENCE",
        }
        revocation = evidence.invalidation_class == "ROOT_REVOCATION"
        supersession = evidence.invalidation_class == "ROOT_SUPERSESSION"
        revocation_values = (
            value.revocation_candidate,
            value.revocation_root_projection,
            value.accepted_revocation_binding,
        )
        supersession_values = (
            value.supersession_candidate,
            value.supersession_root_projection,
            value.supersession_successor_packet_id,
            value.accepted_supersession_binding,
        )
        if deterministic:
            if (
                evidence.authority_effect != "DETERMINISTIC_BLOCK"
                or any(item is not None for item in revocation_values)
                or any(item is not None for item in supersession_values)
            ):
                return False, (
                    "action_packet_invalidation_context_shape_invalid",
                )
            packet_validation_result = (
                _cached_root_bound_validation_v01(
                    validation_pass,
                    packet,
                )
                if validation_pass is not None
                else None
            )
            return _validate_action_invalidation_evidence_against_packet_core_v01(
                evidence,
                packet,
                packet_validation_result=packet_validation_result,
            )
        if revocation:
            if (
                evidence.authority_effect != "ROOT_REVOCATION"
                or type(value.revocation_candidate)
                is not RevocationCandidateV01
                or type(value.revocation_root_projection)
                is not RootDecisionCandidateProjectionV01
                or type(value.accepted_revocation_binding)
                is not AcceptedRevocationBindingV01
                or any(item is not None for item in supersession_values)
            ):
                return False, (
                    "action_packet_invalidation_context_shape_invalid",
                )
            packet_validation_result = (
                _cached_root_bound_validation_v01(
                    validation_pass,
                    packet,
                )
                if validation_pass is not None
                else None
            )
            return _validate_action_invalidation_evidence_against_packet_core_v01(
                evidence,
                packet,
                revocation_candidate=value.revocation_candidate,
                revocation_root_projection=value.revocation_root_projection,
                accepted_revocation_binding=(
                    value.accepted_revocation_binding
                ),
                packet_validation_result=packet_validation_result,
            )
        if supersession:
            if (
                evidence.authority_effect != "ROOT_SUPERSESSION"
                or any(item is not None for item in revocation_values)
                or type(value.supersession_candidate)
                is not SupersessionCandidateV01
                or type(value.supersession_root_projection)
                is not RootDecisionCandidateProjectionV01
                or type(value.supersession_successor_packet_id) is not str
                or type(value.accepted_supersession_binding)
                is not AcceptedSupersessionBindingV01
                or type(supersession_successor)
                is not SupplierRootBoundActionCommitPacketV02ProjectionV01
                or supersession_successor.packet_identity.packet_id
                != value.supersession_successor_packet_id
            ):
                return False, (
                    "action_packet_invalidation_context_shape_invalid",
                )
            packet_validation_result = (
                _cached_root_bound_validation_v01(
                    validation_pass,
                    packet,
                )
                if validation_pass is not None
                else None
            )
            successor_validation_result = (
                _cached_root_bound_validation_v01(
                    validation_pass,
                    supersession_successor,
                )
                if validation_pass is not None
                else None
            )
            return _validate_action_invalidation_evidence_against_packet_core_v01(
                evidence,
                packet,
                supersession_candidate=value.supersession_candidate,
                supersession_root_projection=(
                    value.supersession_root_projection
                ),
                supersession_successor=supersession_successor,
                accepted_supersession_binding=(
                    value.accepted_supersession_binding
                ),
                packet_validation_result=packet_validation_result,
                successor_validation_result=successor_validation_result,
            )
        return False, ("action_packet_invalidation_context_class_invalid",)
    except Exception:
        return False, ("action_packet_invalidation_context_invalid",)


def _validate_action_packet_invalidation_context_v01(
    value: object,
    packet: object,
    *,
    supersession_successor: object = None,
) -> tuple[bool, tuple[str, ...]]:
    return _validate_action_packet_invalidation_context_core_v01(
        value,
        packet,
        supersession_successor=supersession_successor,
    )


def _transition_evidence_binding_for_code_v01(
    event: ActionPacketTransitionEventV01,
    evidence_code: str,
) -> TransitionEvidenceBindingV01 | None:
    matching = tuple(
        binding
        for binding in event.transition_evidence_bindings
        if binding.evidence_code == evidence_code
    )
    return matching[0] if len(matching) == 1 else None


def _transition_evidence_binding_matches_v01(
    event: ActionPacketTransitionEventV01,
    *,
    evidence_code: str,
    evidence_ref: str,
    evidence_sha256: str,
    validator_profile_id: str,
) -> bool:
    binding = _transition_evidence_binding_for_code_v01(
        event,
        evidence_code,
    )
    return (
        type(binding) is TransitionEvidenceBindingV01
        and type(binding.evidence_ref) is str
        and binding.evidence_ref == evidence_ref
        and type(binding.evidence_sha256) is str
        and binding.evidence_sha256 == evidence_sha256
        and type(binding.validator_profile_id) is str
        and binding.validator_profile_id == validator_profile_id
        and type(binding.validation_status) is str
        and binding.validation_status == "PASS"
    )


def _invalidation_context_matches_transition_reference_v01(
    context: _ActionPacketInvalidationContextV01,
    event: ActionPacketTransitionEventV01,
) -> bool:
    deterministic_codes = {
        "g2a_t06_created_block": "blocking_evidence_valid",
        "g2a_t07_authorized_block": "blocking_evidence_valid",
        "g2a_t08_queued_block": "blocking_evidence_valid",
        "g2a_t09_pending_block": "immediate_eligibility_failure_valid",
        "g2a_t10_failed_block": "retry_ineligibility_evidence_valid",
    }
    if event.transition_rule_id in deterministic_codes:
        binding = _transition_evidence_binding_for_code_v01(
            event,
            deterministic_codes[event.transition_rule_id],
        )
        return (
            type(binding) is TransitionEvidenceBindingV01
            and binding.evidence_ref
            == context.invalidation_evidence.invalidation_evidence_id
        )
    if event.transition_rule_id in {
        "g2a_t16_authorized_revoke",
        "g2a_t17_queued_revoke",
        "g2a_t18_pending_revoke",
        "g2a_t19_failed_revoke",
    }:
        binding = _transition_evidence_binding_for_code_v01(
            event,
            "accepted_revocation_binding_valid",
        )
        return (
            type(binding) is TransitionEvidenceBindingV01
            and type(context.accepted_revocation_binding)
            is AcceptedRevocationBindingV01
            and binding.evidence_ref
            == context.accepted_revocation_binding
            .accepted_revocation_binding_id
        )
    if event.transition_rule_id in {
        "g2a_t20_authorized_supersede",
        "g2a_t21_queued_supersede",
        "g2a_t22_pending_supersede",
        "g2a_t23_failed_supersede",
    }:
        binding = _transition_evidence_binding_for_code_v01(
            event,
            "accepted_supersession_binding_valid",
        )
        return (
            type(binding) is TransitionEvidenceBindingV01
            and type(context.accepted_supersession_binding)
            is AcceptedSupersessionBindingV01
            and binding.evidence_ref
            == context.accepted_supersession_binding
            .accepted_supersession_binding_id
        )
    return False


def validate_action_packet_renewal_relationship_v01(
    predecessor: object,
    successor: object,
    candidate: object,
    accepted_binding: object,
    *,
    root_projection: object = None,
) -> tuple[bool, tuple[str, ...]]:
    try:
        context_valid, context_reasons = (
            validate_supersession_candidate_against_packets_v01(
                candidate,
                predecessor,
                successor,
            )
        )
        if not context_valid:
            return False, context_reasons
        if root_projection is None:
            return False, ("renewal_root_projection_required",)
        binding_context_valid, binding_context_reasons = (
            _validate_accepted_supersession_binding_against_context_v01(
                accepted_binding,
                candidate,
                root_projection,
                predecessor,
                successor,
            )
        )
        if not binding_context_valid:
            return False, binding_context_reasons
        reasons: list[str] = []
        predecessor_canonical = predecessor.canonical_projection
        successor_canonical = successor.canonical_projection
        predecessor_auth = predecessor_canonical.authorization_candidate
        successor_auth = successor_canonical.authorization_candidate
        predecessor_decision = (
            predecessor.root_decision_projection.root_decision_result
            .decision_id
        )
        successor_decision = (
            successor.root_decision_projection.root_decision_result.decision_id
        )
        if candidate.supersession_reason_class != "RENEWAL":
            _reason_v01(reasons, "renewal_reason_invalid")
        if (
            predecessor_canonical.owning_local_root_id
            != successor_canonical.owning_local_root_id
            or predecessor_canonical.transaction_id
            != successor_canonical.transaction_id
            or predecessor_canonical.logical_intent.root_owned_intent_id
            != successor_canonical.logical_intent.root_owned_intent_id
            or predecessor_canonical.idempotency_identity.idempotency_key
            != successor_canonical.idempotency_identity.idempotency_key
        ):
            _reason_v01(reasons, "renewal_logical_context_mismatch")
        if (
            predecessor.packet_identity.packet_id
            == successor.packet_identity.packet_id
            or predecessor_auth.root_packet_authorization_candidate_id
            == successor_auth.root_packet_authorization_candidate_id
            or predecessor_decision == successor_decision
        ):
            _reason_v01(reasons, "renewal_identity_not_distinct")
        if (
            successor_auth.predecessor_packet_id
            != predecessor.packet_identity.packet_id
            or successor_auth.supersession_reason_class != "RENEWAL"
            or candidate.predecessor_packet_id
            != predecessor.packet_identity.packet_id
            or candidate.successor_packet_authorization_candidate_id
            != successor_auth.root_packet_authorization_candidate_id
        ):
            _reason_v01(reasons, "renewal_predecessor_binding_mismatch")
        if (
            accepted_binding.supersession_candidate_id
            != candidate.supersession_candidate_id
            or accepted_binding.predecessor_packet_id
            != predecessor.packet_identity.packet_id
            or accepted_binding.prior_authorization_decision_id
            != predecessor_decision
            or accepted_binding.owning_local_root_id
            != predecessor_canonical.owning_local_root_id
        ):
            _reason_v01(reasons, "renewal_accepted_binding_mismatch")
        return _result_v01(reasons)
    except Exception:
        return False, ("renewal_relationship_invalid",)


def _validate_supplier_root_context_coherence_impl_v01(
    canonical_projection: object,
    root_projection: object,
) -> tuple[bool, tuple[str, ...]]:
    reasons: list[str] = []
    canonical_valid, canonical_reasons = (
        validate_supplier_action_commit_packet_canonical_projection_v01(
            canonical_projection
        )
    )
    if not canonical_valid:
        return False, (
            "supplier_root_context_canonical_projection_invalid",
            *canonical_reasons,
        )
    root_valid, root_reasons = validate_root_decision_candidate_projection_v01(
        root_projection
    )
    if not root_valid:
        return False, (
            "supplier_root_context_root_projection_invalid",
            *root_reasons,
        )
    candidate = canonical_projection.authorization_candidate
    decision_input = root_projection.root_decision_input
    result = root_projection.root_decision_result
    if (
        root_projection.candidate_kind
        != ROOT_DECISION_CANDIDATE_KIND_PACKET_AUTHORIZATION_V01
    ):
        _reason_v01(reasons, "supplier_root_context_candidate_kind_mismatch")
    if (
        root_projection.projected_candidate_id
        != candidate.root_packet_authorization_candidate_id
    ):
        _reason_v01(reasons, "supplier_root_context_candidate_mismatch")
    if (
        decision_input.transaction_id != canonical_projection.transaction_id
        or result.transaction_id != canonical_projection.transaction_id
    ):
        _reason_v01(reasons, "supplier_root_context_transaction_mismatch")
    if (
        decision_input.target_root_id
        != canonical_projection.owning_local_root_id
        or result.target_root_id != canonical_projection.owning_local_root_id
    ):
        _reason_v01(reasons, "supplier_root_context_root_mismatch")
    try:
        plain = root_decision_input_to_plain_dict_v01(decision_input)
    except Exception:
        return False, ("supplier_root_context_input_projection_invalid",)
    permission = plain.get("permission_state")
    policy = plain.get("policy_state")
    temporal = plain.get("temporal_state")
    post_vv = plain.get("post_vv_bundle")
    prior = plain.get("prior_root_state")
    if not all(
        type(item) is dict
        for item in (permission, policy, temporal, post_vv, prior)
    ):
        return False, ("supplier_root_context_input_projection_invalid",)
    if (
        permission.get("permission_ref")
        != canonical_projection.canonical_permission_ref
    ):
        _reason_v01(reasons, "supplier_root_context_permission_mismatch")
    if (
        policy.get("policy_id")
        != canonical_projection.authority_policy_fingerprint
    ):
        _reason_v01(reasons, "supplier_root_context_policy_mismatch")
    if (
        temporal.get("time_envelope_ref")
        != canonical_projection.temporal_authority_fingerprint
    ):
        _reason_v01(reasons, "supplier_root_context_temporal_mismatch")
    if any(
        policy.get(key) is not True
        for key in (
            "identity_passed",
            "scope_passed",
            "hard_policy_passed",
            "allow_accept",
        )
    ):
        _reason_v01(reasons, "supplier_root_context_policy_hard_failure")
    try:
        derived_temporal_evaluation = evaluate_temporal_authority_v01(
            canonical_projection.temporal_authority,
            evaluation_time=canonical_projection.evaluation_time,
        )
    except ValueError:
        _reason_v01(reasons, "supplier_root_context_temporal_evidence_invalid")
    else:
        if (
            canonical_projection.temporal_evaluation
            != derived_temporal_evaluation
        ):
            _reason_v01(
                reasons,
                "supplier_root_context_temporal_evaluation_mismatch",
            )
        if (
            derived_temporal_evaluation.outcome
            != TEMPORAL_OUTCOME_VALID_V01
            or derived_temporal_evaluation.executable is not True
        ):
            _reason_v01(reasons, "supplier_root_context_temporal_invalid")
        expected_expired = (
            derived_temporal_evaluation.outcome
            == TEMPORAL_OUTCOME_EXPIRED_V01
        )
        expected_not_before = (
            canonical_projection.evaluation_time
            >= canonical_projection.temporal_authority.issued_at_utc
        )
        if (
            temporal.get("temporal_valid")
            is not derived_temporal_evaluation.executable
            or temporal.get("expired") is not expected_expired
            or temporal.get("not_before_satisfied")
            is not expected_not_before
        ):
            _reason_v01(reasons, "supplier_root_context_temporal_truth_mismatch")

    required_refs = post_vv.get("required_evidence_refs")
    provided_refs = post_vv.get("provided_evidence_refs")
    if type(required_refs) is not list or type(provided_refs) is not list:
        _reason_v01(reasons, "supplier_root_context_evidence_sets_invalid")
    else:
        mandatory_refs = tuple(
            record.evidence_ref
            for record in canonical_projection.dependency_candidate.dependency_records
            if record.requirement_class == "MANDATORY"
        )
        if any(ref not in required_refs for ref in mandatory_refs):
            _reason_v01(
                reasons,
                "supplier_root_context_required_dependency_missing",
            )
        if any(ref not in provided_refs for ref in mandatory_refs):
            _reason_v01(
                reasons,
                "supplier_root_context_provided_dependency_missing",
            )
    if (
        prior.get("prior_decision_id") is not None
        or prior.get("prior_decision") is not None
        or prior.get("prior_selected_candidate_id") is not None
        or result.prior_decision_id is not None
    ):
        _reason_v01(reasons, "supplier_root_context_prior_state_forbidden")
    return _result_v01(reasons)


def validate_supplier_root_context_coherence_v01(
    canonical_projection: object,
    root_projection: object,
) -> tuple[bool, tuple[str, ...]]:
    try:
        return _validate_supplier_root_context_coherence_impl_v01(
            canonical_projection,
            root_projection,
        )
    except Exception:
        return False, ("supplier_root_context_validation_invalid",)


def _build_supplier_root_bound_packet_v01(
    canonical_projection: SupplierActionCommitPacketCanonicalProjectionV01,
    root_projection: RootDecisionCandidateProjectionV01,
    packet_identity: ActionCommitPacketIdentityResultV01,
    dependency_binding: PacketDependencyAcceptanceBindingV01,
) -> ActionCommitPacketV02:
    source_packet = canonical_projection.source_packet
    consequential = canonical_projection.consequential_effect_parameters
    if consequential.amount_decimal is None or consequential.currency_code is None:
        raise ValueError("supplier_root_bound_amount_currency_required")
    temporal = canonical_projection.temporal_authority
    evaluation = evaluate_temporal_authority_v01(
        temporal,
        evaluation_time=canonical_projection.evaluation_time,
    )
    expected_targets = canonicalize_set_like_string_tuple_v01(
        (
            source_packet.scope.creditor_ref,
            source_packet.scope.payment_slot_ref,
        )
    )
    if (
        canonical_projection.normalized_target_scope.included_target_refs
        != expected_targets
        or canonical_projection.business_object_identity.business_object_ref
        != source_packet.scope.payment_slot_ref
    ):
        raise ValueError("supplier_root_bound_target_continuity_invalid")
    packet = ActionCommitPacketV02(
        packet_id=packet_identity.packet_id,
        source_root_decision_ref=(
            root_projection.root_decision_result.decision_id
        ),
        human_approval_ref=source_packet.human_approval_ref,
        scope=PermissionScopeV02(
            allowed_subjects=(
                canonical_projection.normalized_subject_scope.included_subject_refs
            ),
            forbidden_subjects=(
                canonical_projection.normalized_subject_scope.excluded_subject_refs
            ),
            allowed_actions=(
                canonical_projection.normalized_permission_scope.allowed_action_classes
            ),
            forbidden_actions=source_packet.scope.forbidden_actions,
            allowed_adapters=(
                canonical_projection.normalized_permission_scope.allowed_adapter_ids
            ),
            forbidden_adapters=source_packet.scope.forbidden_adapters,
            payment_slot_ref=(
                canonical_projection.business_object_identity.business_object_ref
            ),
            creditor_ref=source_packet.scope.creditor_ref,
            amount=consequential.amount_decimal,
            currency=consequential.currency_code,
        ),
        ttl=PacketTTL(
            created_at=format_utc_timestamp_v01(temporal.issued_at_utc),
            expires_at=format_utc_timestamp_v01(temporal.expires_at_utc),
            ttl_seconds=temporal.ttl_seconds,
            ttl_valid=(
                validate_action_temporal_authority_profile_v01(temporal)
                == (True, ())
            ),
            expired=evaluation.outcome == TEMPORAL_OUTCOME_EXPIRED_V01,
        ),
        idempotency=IdempotencyKeyV02(
            key=canonical_projection.idempotency_identity.idempotency_key,
            duplicate_packet_id=False,
            duplicate_idempotency_key=False,
            terminal_receipt_already_exists=False,
        ),
        adapter_binding=AdapterBindingV02(
            adapter_id=canonical_projection.adapter_binding.adapter_id,
            adapter_kind=canonical_projection.adapter_binding.adapter_kind,
            real_adapter=False,
            adapter_version=canonical_projection.adapter_binding.adapter_version,
        ),
        packet_type=source_packet.packet_type,
        created_by="root",
        root_created=True,
        evidence_refs=(
            *source_packet.evidence_refs,
            PacketEvidenceRefV02(
                evidence_id=root_projection.root_decision_result.decision_id,
                evidence_kind="root_decision_result_v01",
                source_ref=(
                    root_projection.root_decision_input.decision_input_id
                ),
            ),
            PacketEvidenceRefV02(
                evidence_id=(
                    dependency_binding.packet_dependency_acceptance_binding_id
                ),
                evidence_kind=(
                    "packet_dependency_acceptance_binding_v01"
                ),
                source_ref=(
                    canonical_projection.dependency_set_candidate_fingerprint
                ),
            ),
        ),
        drs_refs=source_packet.drs_refs,
        avf_refs=source_packet.avf_refs,
        bsep_ref=source_packet.bsep_ref,
        root_boundary_ref=(
            root_projection.root_decision_input.decision_input_id
        ),
        receipt_evidence_only=True,
        real_world_effects_allowed=False,
        production_ready_claimed=False,
        public_auditor_ready_claimed=False,
    )
    historical_valid, _ = validate_action_commit_packet_v02(packet)
    if not historical_valid:
        raise ValueError("supplier_root_bound_historical_validation_failed")
    return packet


def _validate_supplier_root_bound_projection_impl_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    if type(value) is not SupplierRootBoundActionCommitPacketV02ProjectionV01:
        return False, ("supplier_root_bound_projection_type_invalid",)
    reasons: list[str] = []
    context_valid, context_reasons = validate_supplier_root_context_coherence_v01(
        value.canonical_projection,
        value.root_decision_projection,
    )
    if not context_valid:
        return False, (
            "supplier_root_bound_context_invalid",
            *context_reasons,
        )
    if type(value.packet_identity) is not ActionCommitPacketIdentityResultV01:
        _reason_v01(reasons, "supplier_root_bound_packet_identity_type_invalid")
    if (
        type(value.dependency_acceptance_binding)
        is not PacketDependencyAcceptanceBindingV01
    ):
        _reason_v01(reasons, "supplier_root_bound_dependency_binding_type_invalid")
    if type(value.packet) is not ActionCommitPacketV02:
        _reason_v01(reasons, "supplier_root_bound_packet_type_invalid")
    if reasons:
        return _result_v01(reasons)

    canonical = value.canonical_projection
    root_projection = value.root_decision_projection
    source_id = root_projection.root_decision_result.decision_id
    source_hash = root_projection.source_root_decision_hash
    try:
        rebuilt_hash = build_action_source_root_decision_hash_v01(
            root_projection.root_decision_result
        )
        rebuilt_identity = build_action_commit_packet_identity_v01(
            candidate=canonical.authorization_candidate,
            source_root_decision_id=source_id,
            source_root_decision_hash=source_hash,
        )
        rebuilt_binding = build_packet_dependency_acceptance_binding_v01(
            dependency_set_candidate_fingerprint=(
                canonical.dependency_set_candidate_fingerprint
            ),
            root_packet_authorization_candidate_id=(
                canonical.authorization_candidate
                .root_packet_authorization_candidate_id
            ),
            source_root_decision_id=source_id,
            source_root_decision_hash=source_hash,
            owning_local_root_id=canonical.owning_local_root_id,
            packet_id=rebuilt_identity.packet_id,
            accepted_status="ROOT_ACCEPTED_FOR_PACKET",
        )
        expected_packet = _build_supplier_root_bound_packet_v01(
            canonical,
            root_projection,
            rebuilt_identity,
            rebuilt_binding,
        )
    except ValueError:
        return False, ("supplier_root_bound_rebuild_invalid",)
    except Exception:
        return False, ("supplier_root_bound_rebuild_invalid",)
    if rebuilt_hash != source_hash:
        _reason_v01(reasons, "supplier_root_bound_source_hash_mismatch")
    packet_identity_valid, _ = validate_action_commit_packet_identity_v01(
        value.packet_identity,
        candidate=canonical.authorization_candidate,
        source_root_decision_id=source_id,
        source_root_decision_hash=source_hash,
    )
    if not packet_identity_valid:
        _reason_v01(reasons, "supplier_root_bound_packet_identity_invalid")
    if (
        type(value.packet_identity.packet_id) is not str
        or value.packet_identity.packet_id != rebuilt_identity.packet_id
        or canonical_material_bytes_v01(value.packet_identity.material)
        != canonical_material_bytes_v01(rebuilt_identity.material)
    ):
        _reason_v01(reasons, "supplier_root_bound_packet_identity_mismatch")
    binding_valid, _ = validate_packet_dependency_acceptance_binding_v01(
        value.dependency_acceptance_binding
    )
    if not binding_valid:
        _reason_v01(reasons, "supplier_root_bound_dependency_binding_invalid")
    if value.dependency_acceptance_binding != rebuilt_binding:
        _reason_v01(reasons, "supplier_root_bound_dependency_binding_mismatch")
    packet_types_valid, _ = _validate_action_commit_packet_exact_types_v01(
        value.packet
    )
    if not packet_types_valid:
        _reason_v01(reasons, "supplier_root_bound_packet_exact_types_invalid")
    packet_identity_scalar_valid = (
        validate_prefixed_sha256_identity_v01(
            value.packet.packet_id,
            prefix=ACTION_COMMIT_PACKET_ID_PREFIX_V01,
        )[0]
        and validate_lowercase_sha256_hex_v01(
            value.packet.source_root_decision_ref
        )[0]
        and validate_lowercase_sha256_hex_v01(
            value.packet.root_boundary_ref
        )[0]
        and validate_prefixed_sha256_identity_v01(
            value.packet.idempotency.key,
            prefix=ACTION_IDEMPOTENCY_PREFIX_V01,
        )[0]
    )
    if not packet_identity_scalar_valid:
        _reason_v01(reasons, "supplier_root_bound_identity_scalar_invalid")
    if value.packet != expected_packet:
        _reason_v01(reasons, "supplier_root_bound_packet_mismatch")
    try:
        historical_valid, _ = validate_action_commit_packet_v02(value.packet)
    except Exception:
        historical_valid = False
    if not historical_valid:
        _reason_v01(reasons, "supplier_root_bound_historical_validation_failed")
    return _result_v01(reasons)


def validate_supplier_root_bound_action_commit_packet_v02_projection_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    try:
        return _validate_supplier_root_bound_projection_impl_v01(value)
    except Exception:
        return False, ("supplier_root_bound_projection_invalid",)


def build_supplier_root_bound_action_commit_packet_v02_projection_v01(
    *,
    canonical_projection: object,
    root_decision_projection: object,
) -> SupplierRootBoundActionCommitPacketV02ProjectionV01:
    try:
        context_valid, context_reasons = (
            validate_supplier_root_context_coherence_v01(
                canonical_projection,
                root_decision_projection,
            )
        )
        if not context_valid:
            raise ValueError(context_reasons[0])
        source_id = root_decision_projection.root_decision_result.decision_id
        source_hash = root_decision_projection.source_root_decision_hash
        packet_identity = build_action_commit_packet_identity_v01(
            candidate=canonical_projection.authorization_candidate,
            source_root_decision_id=source_id,
            source_root_decision_hash=source_hash,
        )
        dependency_binding = (
            build_packet_dependency_acceptance_binding_v01(
                dependency_set_candidate_fingerprint=(
                    canonical_projection.dependency_set_candidate_fingerprint
                ),
                root_packet_authorization_candidate_id=(
                    canonical_projection.authorization_candidate
                    .root_packet_authorization_candidate_id
                ),
                source_root_decision_id=source_id,
                source_root_decision_hash=source_hash,
                owning_local_root_id=canonical_projection.owning_local_root_id,
                packet_id=packet_identity.packet_id,
                accepted_status="ROOT_ACCEPTED_FOR_PACKET",
            )
        )
        packet = _build_supplier_root_bound_packet_v01(
            canonical_projection,
            root_decision_projection,
            packet_identity,
            dependency_binding,
        )
        projection = SupplierRootBoundActionCommitPacketV02ProjectionV01(
            canonical_projection=canonical_projection,
            root_decision_projection=root_decision_projection,
            packet_identity=packet_identity,
            dependency_acceptance_binding=dependency_binding,
            packet=packet,
        )
        valid, reasons = (
            validate_supplier_root_bound_action_commit_packet_v02_projection_v01(
                projection
            )
        )
        if not valid:
            raise ValueError(reasons[0])
        return projection
    except ValueError as exc:
        raise ValueError(
            _stable_exception_reason_v01(
                exc,
                fallback="supplier_root_bound_projection_invalid",
            )
        ) from None
    except Exception:
        raise ValueError("supplier_root_bound_projection_invalid") from None


def transition_evidence_binding_material_v01(
    value: TransitionEvidenceBindingV01,
) -> CanonicalMaterialV01:
    if type(value) is not TransitionEvidenceBindingV01:
        raise ValueError("transition_evidence_binding_type_invalid")
    return (
        ("evidence_code", value.evidence_code),
        ("evidence_ref", value.evidence_ref),
        ("evidence_sha256", value.evidence_sha256),
        ("validator_profile_id", value.validator_profile_id),
        ("validation_status", value.validation_status),
    )


def build_transition_evidence_binding_v01(
    *,
    action_packet_transition_registry_profile: object,
    transition_rule_id: object,
    evidence_code: object,
    evidence_ref: object,
    evidence_sha256: object,
    validator_profile_id: object,
) -> TransitionEvidenceBindingV01:
    try:
        rule = lookup_action_packet_transition_rule_v01(
            registry=action_packet_transition_registry_profile,
            transition_rule_id=transition_rule_id,
        )
        if (
            type(evidence_code) is not str
            or evidence_code not in rule.required_evidence_codes
        ):
            raise ValueError("transition_evidence_code_not_required")
        for value in (evidence_ref, validator_profile_id):
            valid_text, text_reasons = validate_identity_text_v01(value)
            if not valid_text:
                raise ValueError(text_reasons[0])
        valid_hash, hash_reasons = validate_lowercase_sha256_hex_v01(
            evidence_sha256
        )
        if not valid_hash:
            raise ValueError(hash_reasons[0])
        provisional = TransitionEvidenceBindingV01(
            transition_evidence_binding_id="",
            evidence_code=evidence_code,
            evidence_ref=evidence_ref,
            evidence_sha256=evidence_sha256,
            validator_profile_id=validator_profile_id,
            validation_status="PASS",
        )
        material = transition_evidence_binding_material_v01(provisional)
        binding = TransitionEvidenceBindingV01(
            transition_evidence_binding_id=(
                build_domain_separated_identity_v01(
                    domain=TRANSITION_EVIDENCE_BINDING_DOMAIN_V01,
                    prefix=TRANSITION_EVIDENCE_BINDING_PREFIX_V01,
                    material=material,
                )
            ),
            evidence_code=evidence_code,
            evidence_ref=evidence_ref,
            evidence_sha256=evidence_sha256,
            validator_profile_id=validator_profile_id,
            validation_status="PASS",
        )
        valid, reasons = validate_transition_evidence_binding_v01(
            binding,
            action_packet_transition_registry_profile=(
                action_packet_transition_registry_profile
            ),
            transition_rule_id=transition_rule_id,
        )
        if not valid:
            raise ValueError(reasons[0])
        return binding
    except ValueError as exc:
        raise ValueError(
            _stable_exception_reason_v01(
                exc,
                fallback="transition_evidence_binding_invalid",
            )
        ) from None
    except Exception:
        raise ValueError("transition_evidence_binding_invalid") from None


def validate_transition_evidence_binding_v01(
    value: object,
    *,
    action_packet_transition_registry_profile: object = None,
    transition_rule_id: object = None,
) -> tuple[bool, tuple[str, ...]]:
    try:
        if type(value) is not TransitionEvidenceBindingV01:
            return False, ("transition_evidence_binding_type_invalid",)
        if validate_action_packet_transition_registry_profile_v01(
            action_packet_transition_registry_profile
        ):
            return False, ("transition_evidence_registry_invalid",)
        try:
            rule = lookup_action_packet_transition_rule_v01(
                registry=action_packet_transition_registry_profile,
                transition_rule_id=transition_rule_id,
            )
        except ValueError:
            return False, ("transition_evidence_rule_unknown",)
        reasons: list[str] = []
        binding_id_valid, _ = validate_prefixed_sha256_identity_v01(
            value.transition_evidence_binding_id,
            prefix=TRANSITION_EVIDENCE_BINDING_PREFIX_V01,
        )
        if not binding_id_valid:
            _reason_v01(reasons, "transition_evidence_binding_id_invalid")
        if (
            type(value.evidence_code) is not str
            or value.evidence_code not in rule.required_evidence_codes
        ):
            _reason_v01(reasons, "transition_evidence_code_not_required")
        for field_value, reason in (
            (value.evidence_ref, "transition_evidence_ref_invalid"),
            (
                value.validator_profile_id,
                "transition_evidence_validator_profile_invalid",
            ),
        ):
            if not validate_identity_text_v01(field_value)[0]:
                _reason_v01(reasons, reason)
        if not validate_lowercase_sha256_hex_v01(value.evidence_sha256)[0]:
            _reason_v01(reasons, "transition_evidence_sha256_invalid")
        if type(value.validation_status) is not str or (
            value.validation_status != "PASS"
        ):
            _reason_v01(reasons, "transition_evidence_status_invalid")
        if reasons:
            return _result_v01(reasons)
        material = transition_evidence_binding_material_v01(value)
        expected_id = build_domain_separated_identity_v01(
            domain=TRANSITION_EVIDENCE_BINDING_DOMAIN_V01,
            prefix=TRANSITION_EVIDENCE_BINDING_PREFIX_V01,
            material=material,
        )
        if (
            type(value.transition_evidence_binding_id) is not str
            or value.transition_evidence_binding_id != expected_id
        ):
            _reason_v01(reasons, "transition_evidence_binding_id_mismatch")
        return _result_v01(reasons)
    except Exception:
        return False, ("transition_evidence_binding_invalid",)


def action_execution_attempt_identity_material_v01(
    *,
    packet_id: object,
    idempotency_key: object,
    attempt_ordinal: object,
    evaluation_context_id: object,
) -> CanonicalMaterialV01:
    if not validate_prefixed_sha256_identity_v01(
        packet_id,
        prefix=ACTION_COMMIT_PACKET_ID_PREFIX_V01,
    )[0]:
        raise ValueError("execution_attempt_packet_id_invalid")
    if not validate_prefixed_sha256_identity_v01(
        idempotency_key,
        prefix=ACTION_IDEMPOTENCY_PREFIX_V01,
    )[0]:
        raise ValueError("execution_attempt_idempotency_key_invalid")
    if not validate_positive_int_v01(attempt_ordinal)[0]:
        raise ValueError("execution_attempt_ordinal_invalid")
    if not validate_identity_text_v01(evaluation_context_id)[0]:
        raise ValueError("execution_attempt_evaluation_context_invalid")
    return (
        ("packet_id", packet_id),
        ("idempotency_key", idempotency_key),
        ("attempt_ordinal", attempt_ordinal),
        ("evaluation_context_id", evaluation_context_id),
    )


def build_action_execution_attempt_identity_v01(
    *,
    packet_id: object,
    idempotency_key: object,
    attempt_ordinal: object,
    evaluation_context_id: object,
) -> ActionExecutionAttemptIdentityV01:
    """Build an attempt ID; G2-A2B derives its ordinal from validated history."""

    try:
        material = action_execution_attempt_identity_material_v01(
            packet_id=packet_id,
            idempotency_key=idempotency_key,
            attempt_ordinal=attempt_ordinal,
            evaluation_context_id=evaluation_context_id,
        )
        value = ActionExecutionAttemptIdentityV01(
            execution_attempt_id=build_domain_separated_identity_v01(
                domain=EXECUTION_ATTEMPT_IDENTITY_DOMAIN_V01,
                prefix=EXECUTION_ATTEMPT_IDENTITY_PREFIX_V01,
                material=material,
            ),
            packet_id=packet_id,
            idempotency_key=idempotency_key,
            attempt_ordinal=attempt_ordinal,
            evaluation_context_id=evaluation_context_id,
            material=material,
        )
        valid, reasons = validate_action_execution_attempt_identity_v01(value)
        if not valid:
            raise ValueError(reasons[0])
        return value
    except ValueError as exc:
        raise ValueError(
            _stable_exception_reason_v01(
                exc,
                fallback="execution_attempt_identity_invalid",
            )
        ) from None
    except Exception:
        raise ValueError("execution_attempt_identity_invalid") from None


def validate_action_execution_attempt_identity_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    try:
        if type(value) is not ActionExecutionAttemptIdentityV01:
            return False, ("execution_attempt_identity_type_invalid",)
        if not validate_prefixed_sha256_identity_v01(
            value.execution_attempt_id,
            prefix=EXECUTION_ATTEMPT_IDENTITY_PREFIX_V01,
        )[0]:
            return False, ("execution_attempt_id_invalid",)
        try:
            rebuilt_material = action_execution_attempt_identity_material_v01(
                packet_id=value.packet_id,
                idempotency_key=value.idempotency_key,
                attempt_ordinal=value.attempt_ordinal,
                evaluation_context_id=value.evaluation_context_id,
            )
            rebuilt_id = build_domain_separated_identity_v01(
                domain=EXECUTION_ATTEMPT_IDENTITY_DOMAIN_V01,
                prefix=EXECUTION_ATTEMPT_IDENTITY_PREFIX_V01,
                material=rebuilt_material,
            )
        except ValueError as exc:
            return False, (
                _stable_exception_reason_v01(
                    exc,
                    fallback="execution_attempt_identity_invalid",
                ),
            )
        expected_fields = (
            "packet_id",
            "idempotency_key",
            "attempt_ordinal",
            "evaluation_context_id",
        )
        if not validate_canonical_profile_material_v01(
            value.material,
            expected_field_names=expected_fields,
        )[0]:
            return False, ("execution_attempt_material_invalid",)
        if (
            canonical_material_bytes_v01(value.material)
            != canonical_material_bytes_v01(rebuilt_material)
            or type(value.execution_attempt_id) is not str
            or value.execution_attempt_id != rebuilt_id
        ):
            return False, ("execution_attempt_identity_mismatch",)
        return True, ()
    except Exception:
        return False, ("execution_attempt_identity_invalid",)


def action_packet_transition_event_material_v01(
    value: ActionPacketTransitionEventV01,
) -> CanonicalMaterialV01:
    if type(value) is not ActionPacketTransitionEventV01:
        raise ValueError("transition_event_type_invalid")
    if type(value.transition_evidence_bindings) is not tuple:
        raise ValueError("transition_event_evidence_type_invalid")
    return (
        ("transition_profile_version", value.transition_profile_version),
        ("transition_registry_id", value.transition_registry_id),
        ("transition_rule_id", value.transition_rule_id),
        ("packet_id", value.packet_id),
        ("idempotency_key", value.idempotency_key),
        (
            "previous_transition_event_id",
            _optional_identity_material_v01(
                value.previous_transition_event_id
            ),
        ),
        ("source_state", value.source_state),
        ("target_state", value.target_state),
        ("transition_class_code", value.transition_class_code),
        ("performed_by_component", value.performed_by_component),
        ("owning_local_root_id", value.owning_local_root_id),
        (
            "root_decision_ref",
            _optional_identity_material_v01(value.root_decision_ref),
        ),
        (
            "transition_evidence_bindings",
            tuple(
                transition_evidence_binding_material_v01(binding)
                for binding in value.transition_evidence_bindings
            ),
        ),
        ("reason_code", value.reason_code),
        (
            "dependency_set_candidate_fingerprint",
            value.dependency_set_candidate_fingerprint,
        ),
        (
            "temporal_authority_fingerprint",
            value.temporal_authority_fingerprint,
        ),
        ("evaluation_time", value.evaluation_time),
        ("evaluation_time_source", value.evaluation_time_source),
        ("evaluation_context_id", value.evaluation_context_id),
        (
            "execution_attempt_id",
            _optional_identity_material_v01(value.execution_attempt_id),
        ),
        ("effect_consumption_class", value.effect_consumption_class),
        ("receipt_ref", _optional_identity_material_v01(value.receipt_ref)),
    )


def build_action_packet_transition_event_v01(
    *,
    action_packet_transition_registry_profile: object,
    transition_rule_id: object,
    packet_id: object,
    idempotency_key: object,
    previous_transition_event_id: object,
    owning_local_root_id: object,
    root_decision_ref: object,
    transition_evidence_bindings: object,
    dependency_set_candidate_fingerprint: object,
    temporal_authority_fingerprint: object,
    evaluation_time: object,
    evaluation_time_source: object,
    evaluation_context_id: object,
    execution_attempt_identity: object,
    receipt_ref: object,
) -> ActionPacketTransitionEventV01:
    try:
        if validate_action_packet_transition_registry_profile_v01(
            action_packet_transition_registry_profile
        ):
            raise ValueError("transition_event_registry_invalid")
        rule = lookup_action_packet_transition_rule_v01(
            registry=action_packet_transition_registry_profile,
            transition_rule_id=transition_rule_id,
        )
        execution_attempt_id = _transition_attempt_id_for_event_v01(
            execution_attempt_identity,
            packet_id=packet_id,
            idempotency_key=idempotency_key,
            evaluation_context_id=evaluation_context_id,
        )
        event = ActionPacketTransitionEventV01(
            transition_event_id="",
            transition_profile_version=(
                ACTION_PACKET_TRANSITION_REGISTRY_PROFILE_VERSION_V01
            ),
            transition_registry_id=(
                action_packet_transition_registry_profile
                .transition_registry_id
            ),
            transition_rule_id=rule.transition_rule_id,
            packet_id=packet_id,
            idempotency_key=idempotency_key,
            previous_transition_event_id=previous_transition_event_id,
            source_state=rule.source_state,
            target_state=rule.target_state,
            transition_class_code=rule.transition_class_code,
            performed_by_component=rule.permitted_component_code,
            owning_local_root_id=owning_local_root_id,
            root_decision_ref=root_decision_ref,
            transition_evidence_bindings=transition_evidence_bindings,
            reason_code=rule.reason_code,
            dependency_set_candidate_fingerprint=(
                dependency_set_candidate_fingerprint
            ),
            temporal_authority_fingerprint=temporal_authority_fingerprint,
            evaluation_time=evaluation_time,
            evaluation_time_source=evaluation_time_source,
            evaluation_context_id=evaluation_context_id,
            execution_attempt_id=execution_attempt_id,
            effect_consumption_class=rule.effect_consumption_class,
            receipt_ref=receipt_ref,
        )
        material = action_packet_transition_event_material_v01(event)
        event = ActionPacketTransitionEventV01(
            transition_event_id=build_domain_separated_identity_v01(
                domain=ACTION_PACKET_TRANSITION_EVENT_DOMAIN_V01,
                prefix=ACTION_PACKET_TRANSITION_EVENT_PREFIX_V01,
                material=material,
            ),
            transition_profile_version=event.transition_profile_version,
            transition_registry_id=event.transition_registry_id,
            transition_rule_id=event.transition_rule_id,
            packet_id=event.packet_id,
            idempotency_key=event.idempotency_key,
            previous_transition_event_id=event.previous_transition_event_id,
            source_state=event.source_state,
            target_state=event.target_state,
            transition_class_code=event.transition_class_code,
            performed_by_component=event.performed_by_component,
            owning_local_root_id=event.owning_local_root_id,
            root_decision_ref=event.root_decision_ref,
            transition_evidence_bindings=(
                event.transition_evidence_bindings
            ),
            reason_code=event.reason_code,
            dependency_set_candidate_fingerprint=(
                event.dependency_set_candidate_fingerprint
            ),
            temporal_authority_fingerprint=(
                event.temporal_authority_fingerprint
            ),
            evaluation_time=event.evaluation_time,
            evaluation_time_source=event.evaluation_time_source,
            evaluation_context_id=event.evaluation_context_id,
            execution_attempt_id=event.execution_attempt_id,
            effect_consumption_class=event.effect_consumption_class,
            receipt_ref=event.receipt_ref,
        )
        valid, reasons = validate_action_packet_transition_event_v01(
            event,
            action_packet_transition_registry_profile=(
                action_packet_transition_registry_profile
            ),
        )
        if not valid:
            raise ValueError(reasons[0])
        return event
    except ValueError as exc:
        raise ValueError(
            _stable_exception_reason_v01(
                exc,
                fallback="transition_event_invalid",
            )
        ) from None
    except Exception:
        raise ValueError("transition_event_invalid") from None


def validate_action_packet_transition_event_v01(
    value: object,
    *,
    action_packet_transition_registry_profile: object = None,
) -> tuple[bool, tuple[str, ...]]:
    try:
        if type(value) is not ActionPacketTransitionEventV01:
            return False, ("transition_event_type_invalid",)
        if validate_action_packet_transition_registry_profile_v01(
            action_packet_transition_registry_profile
        ):
            return False, ("transition_event_registry_invalid",)
        try:
            rule = lookup_action_packet_transition_rule_v01(
                registry=action_packet_transition_registry_profile,
                transition_rule_id=value.transition_rule_id,
            )
        except ValueError:
            return False, ("transition_event_rule_unknown",)
        reasons: list[str] = []
        if (
            type(value.transition_profile_version) is not str
            or value.transition_profile_version
            != ACTION_PACKET_TRANSITION_REGISTRY_PROFILE_VERSION_V01
        ):
            _reason_v01(reasons, "transition_event_profile_version_mismatch")
        if (
            type(value.transition_registry_id) is not str
            or value.transition_registry_id
            != action_packet_transition_registry_profile.transition_registry_id
        ):
            _reason_v01(reasons, "transition_event_registry_id_mismatch")
        derived_fields = (
            (value.source_state, rule.source_state, "transition_event_source_mismatch"),
            (value.target_state, rule.target_state, "transition_event_target_mismatch"),
            (
                value.transition_class_code,
                rule.transition_class_code,
                "transition_event_class_mismatch",
            ),
            (
                value.performed_by_component,
                rule.permitted_component_code,
                "transition_event_component_mismatch",
            ),
            (value.reason_code, rule.reason_code, "transition_event_reason_mismatch"),
            (
                value.effect_consumption_class,
                rule.effect_consumption_class,
                "transition_event_consumption_mismatch",
            ),
        )
        for actual, expected, reason in derived_fields:
            if type(actual) is not str or actual != expected:
                _reason_v01(reasons, reason)
        if not validate_prefixed_sha256_identity_v01(
            value.packet_id,
            prefix=ACTION_COMMIT_PACKET_ID_PREFIX_V01,
        )[0]:
            _reason_v01(reasons, "transition_event_packet_id_invalid")
        if not validate_prefixed_sha256_identity_v01(
            value.idempotency_key,
            prefix=ACTION_IDEMPOTENCY_PREFIX_V01,
        )[0]:
            _reason_v01(reasons, "transition_event_idempotency_key_invalid")
        if value.previous_transition_event_id is not None and (
            not validate_prefixed_sha256_identity_v01(
                value.previous_transition_event_id,
                prefix=ACTION_PACKET_TRANSITION_EVENT_PREFIX_V01,
            )[0]
        ):
            _reason_v01(reasons, "transition_event_previous_id_invalid")
        if (
            rule.transition_rule_id == "g2a_t01_activate_root_authorization"
            and value.previous_transition_event_id is not None
        ):
            _reason_v01(reasons, "transition_event_activation_previous_forbidden")
        if not validate_identity_text_v01(value.owning_local_root_id)[0]:
            _reason_v01(reasons, "transition_event_owning_root_invalid")
        _validate_transition_root_ref_v01(value, rule, reasons)
        if not validate_lowercase_sha256_hex_v01(
            value.dependency_set_candidate_fingerprint
        )[0]:
            _reason_v01(reasons, "transition_event_dependency_fingerprint_invalid")
        if not validate_lowercase_sha256_hex_v01(
            value.temporal_authority_fingerprint
        )[0]:
            _reason_v01(reasons, "transition_event_temporal_fingerprint_invalid")
        if not validate_signed_int64_v01(value.evaluation_time)[0]:
            _reason_v01(reasons, "transition_event_evaluation_time_invalid")
        for field_value, reason in (
            (
                value.evaluation_time_source,
                "transition_event_evaluation_source_invalid",
            ),
            (
                value.evaluation_context_id,
                "transition_event_evaluation_context_invalid",
            ),
        ):
            if not validate_identity_text_v01(field_value)[0]:
                _reason_v01(reasons, reason)
        _validate_transition_evidence_collection_v01(
            value,
            action_packet_transition_registry_profile,
            rule,
            reasons,
        )
        _validate_transition_attempt_receipt_matrix_v01(value, rule, reasons)
        if reasons:
            return _result_v01(reasons)
        material = action_packet_transition_event_material_v01(value)
        if len(material) != 22:
            _reason_v01(reasons, "transition_event_material_count_invalid")
        expected_id = build_domain_separated_identity_v01(
            domain=ACTION_PACKET_TRANSITION_EVENT_DOMAIN_V01,
            prefix=ACTION_PACKET_TRANSITION_EVENT_PREFIX_V01,
            material=material,
        )
        if (
            type(value.transition_event_id) is not str
            or value.transition_event_id != expected_id
        ):
            _reason_v01(reasons, "transition_event_id_mismatch")
        return _result_v01(reasons)
    except Exception:
        return False, ("transition_event_invalid",)


def _transition_attempt_id_for_event_v01(
    value: object,
    *,
    packet_id: object,
    idempotency_key: object,
    evaluation_context_id: object,
) -> str | None:
    if value is None:
        return None
    if type(value) is not ActionExecutionAttemptIdentityV01:
        raise ValueError("transition_event_attempt_identity_invalid")
    if not validate_action_execution_attempt_identity_v01(value)[0]:
        raise ValueError("transition_event_attempt_identity_invalid")
    if (
        type(packet_id) is not str
        or type(idempotency_key) is not str
        or type(evaluation_context_id) is not str
        or value.packet_id != packet_id
        or value.idempotency_key != idempotency_key
        or value.evaluation_context_id != evaluation_context_id
    ):
        raise ValueError("transition_event_attempt_binding_mismatch")
    return value.execution_attempt_id


def _validate_transition_root_ref_v01(
    event: ActionPacketTransitionEventV01,
    rule: ActionPacketTransitionRuleV01,
    reasons: list[str],
) -> None:
    if rule.root_decision_requirement_code == "NONE":
        if event.root_decision_ref is not None:
            _reason_v01(reasons, "transition_event_root_ref_forbidden")
        return
    if not validate_lowercase_sha256_hex_v01(event.root_decision_ref)[0]:
        _reason_v01(reasons, "transition_event_root_ref_required")


def _validate_transition_evidence_collection_v01(
    event: ActionPacketTransitionEventV01,
    registry: ActionPacketTransitionRegistryProfileV01,
    rule: ActionPacketTransitionRuleV01,
    reasons: list[str],
) -> None:
    bindings = event.transition_evidence_bindings
    if type(bindings) is not tuple or any(
        type(binding) is not TransitionEvidenceBindingV01
        for binding in bindings
    ):
        _reason_v01(reasons, "transition_event_evidence_type_invalid")
        return
    codes = tuple(binding.evidence_code for binding in bindings)
    if codes != rule.required_evidence_codes:
        _reason_v01(reasons, "transition_event_evidence_order_mismatch")
    if len(codes) != len(set(codes)):
        _reason_v01(reasons, "transition_event_evidence_duplicate")
    if set(codes) != set(rule.required_evidence_codes):
        _reason_v01(reasons, "transition_event_evidence_set_mismatch")
    for binding in bindings:
        if not validate_transition_evidence_binding_v01(
            binding,
            action_packet_transition_registry_profile=registry,
            transition_rule_id=rule.transition_rule_id,
        )[0]:
            _reason_v01(reasons, "transition_event_evidence_binding_invalid")


def _validate_transition_attempt_receipt_matrix_v01(
    event: ActionPacketTransitionEventV01,
    rule: ActionPacketTransitionRuleV01,
    reasons: list[str],
) -> None:
    attempt_rules = {
        "g2a_t03_pending",
        "g2a_t04_fulfill_mock",
        "g2a_t05_receipt",
        "g2a_t24_nonconsuming_failure",
        "g2a_t26_uncertain_adapter_outcome",
    }
    if rule.transition_rule_id in attempt_rules:
        if not validate_prefixed_sha256_identity_v01(
            event.execution_attempt_id,
            prefix=EXECUTION_ATTEMPT_IDENTITY_PREFIX_V01,
        )[0]:
            _reason_v01(reasons, "transition_event_attempt_required")
    elif event.execution_attempt_id is not None:
        _reason_v01(reasons, "transition_event_attempt_forbidden")
    if rule.transition_rule_id == "g2a_t05_receipt":
        if not validate_identity_text_v01(event.receipt_ref)[0]:
            _reason_v01(reasons, "transition_event_receipt_required")
    elif event.receipt_ref is not None:
        _reason_v01(reasons, "transition_event_receipt_forbidden")


def idempotency_disposition_event_material_v01(
    value: IdempotencyDispositionEventV01,
) -> CanonicalMaterialV01:
    if type(value) is not IdempotencyDispositionEventV01:
        raise ValueError("idempotency_disposition_event_type_invalid")
    if type(value.cause_transition_event_ids) is not tuple:
        raise ValueError("idempotency_disposition_cause_type_invalid")
    if type(value.evidence_refs) is not tuple:
        raise ValueError("idempotency_disposition_evidence_type_invalid")
    return (
        ("event_profile_version", value.event_profile_version),
        ("idempotency_key", value.idempotency_key),
        ("event_class", value.event_class),
        ("from_disposition", value.from_disposition),
        ("to_disposition", value.to_disposition),
        (
            "from_owner_packet_id",
            _optional_identity_material_v01(value.from_owner_packet_id),
        ),
        (
            "to_owner_packet_id",
            _optional_identity_material_v01(value.to_owner_packet_id),
        ),
        (
            "previous_disposition_event_id",
            _optional_identity_material_v01(
                value.previous_disposition_event_id
            ),
        ),
        ("cause_transition_event_ids", value.cause_transition_event_ids),
        (
            "root_decision_ref",
            _optional_identity_material_v01(value.root_decision_ref),
        ),
        (
            "predecessor_packet_id",
            _optional_identity_material_v01(value.predecessor_packet_id),
        ),
        (
            "successor_packet_id",
            _optional_identity_material_v01(value.successor_packet_id),
        ),
        ("evidence_refs", value.evidence_refs),
        ("evaluation_time", value.evaluation_time),
        ("evaluation_time_source", value.evaluation_time_source),
        ("evaluation_context_id", value.evaluation_context_id),
    )


def build_idempotency_disposition_event_v01(
    *,
    idempotency_key: object,
    event_class: object,
    from_disposition: object,
    to_disposition: object,
    from_owner_packet_id: object,
    to_owner_packet_id: object,
    previous_disposition_event_id: object,
    cause_transition_event_ids: object,
    root_decision_ref: object,
    predecessor_packet_id: object,
    successor_packet_id: object,
    evidence_refs: object,
    evaluation_time: object,
    evaluation_time_source: object,
    evaluation_context_id: object,
) -> IdempotencyDispositionEventV01:
    try:
        event = IdempotencyDispositionEventV01(
            idempotency_disposition_event_id="",
            event_profile_version=(
                ACTION_PACKET_TRANSITION_REGISTRY_PROFILE_VERSION_V01
            ),
            idempotency_key=idempotency_key,
            event_class=event_class,
            from_disposition=from_disposition,
            to_disposition=to_disposition,
            from_owner_packet_id=from_owner_packet_id,
            to_owner_packet_id=to_owner_packet_id,
            previous_disposition_event_id=previous_disposition_event_id,
            cause_transition_event_ids=cause_transition_event_ids,
            root_decision_ref=root_decision_ref,
            predecessor_packet_id=predecessor_packet_id,
            successor_packet_id=successor_packet_id,
            evidence_refs=evidence_refs,
            evaluation_time=evaluation_time,
            evaluation_time_source=evaluation_time_source,
            evaluation_context_id=evaluation_context_id,
        )
        material = idempotency_disposition_event_material_v01(event)
        event = IdempotencyDispositionEventV01(
            idempotency_disposition_event_id=(
                build_domain_separated_identity_v01(
                    domain=IDEMPOTENCY_DISPOSITION_EVENT_DOMAIN_V01,
                    prefix=IDEMPOTENCY_DISPOSITION_EVENT_PREFIX_V01,
                    material=material,
                )
            ),
            event_profile_version=event.event_profile_version,
            idempotency_key=event.idempotency_key,
            event_class=event.event_class,
            from_disposition=event.from_disposition,
            to_disposition=event.to_disposition,
            from_owner_packet_id=event.from_owner_packet_id,
            to_owner_packet_id=event.to_owner_packet_id,
            previous_disposition_event_id=(
                event.previous_disposition_event_id
            ),
            cause_transition_event_ids=event.cause_transition_event_ids,
            root_decision_ref=event.root_decision_ref,
            predecessor_packet_id=event.predecessor_packet_id,
            successor_packet_id=event.successor_packet_id,
            evidence_refs=event.evidence_refs,
            evaluation_time=event.evaluation_time,
            evaluation_time_source=event.evaluation_time_source,
            evaluation_context_id=event.evaluation_context_id,
        )
        valid, reasons = validate_idempotency_disposition_event_v01(event)
        if not valid:
            raise ValueError(reasons[0])
        return event
    except ValueError as exc:
        raise ValueError(
            _stable_exception_reason_v01(
                exc,
                fallback="idempotency_disposition_event_invalid",
            )
        ) from None
    except Exception:
        raise ValueError("idempotency_disposition_event_invalid") from None


def validate_idempotency_disposition_event_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    try:
        if type(value) is not IdempotencyDispositionEventV01:
            return False, ("idempotency_disposition_event_type_invalid",)
        reasons: list[str] = []
        if (
            type(value.event_profile_version) is not str
            or value.event_profile_version
            != ACTION_PACKET_TRANSITION_REGISTRY_PROFILE_VERSION_V01
        ):
            _reason_v01(
                reasons,
                "idempotency_disposition_event_profile_version_invalid",
            )
        if not validate_prefixed_sha256_identity_v01(
            value.idempotency_key,
            prefix=ACTION_IDEMPOTENCY_PREFIX_V01,
        )[0]:
            _reason_v01(reasons, "idempotency_disposition_key_invalid")
        if (
            type(value.event_class) is not str
            or value.event_class
            not in IDEMPOTENCY_DISPOSITION_EVENT_CLASSES_V01
        ):
            _reason_v01(reasons, "idempotency_disposition_class_invalid")
        for item, reason in (
            (
                value.from_disposition,
                "idempotency_disposition_from_invalid",
            ),
            (
                value.to_disposition,
                "idempotency_disposition_to_invalid",
            ),
        ):
            if (
                type(item) is not str
                or item not in IDEMPOTENCY_DISPOSITIONS_V01
            ):
                _reason_v01(reasons, reason)
        _validate_optional_packet_identity_v01(
            value.from_owner_packet_id,
            "idempotency_disposition_from_owner_invalid",
            reasons,
        )
        _validate_optional_packet_identity_v01(
            value.to_owner_packet_id,
            "idempotency_disposition_to_owner_invalid",
            reasons,
        )
        _validate_optional_prefixed_identity_v01(
            value.previous_disposition_event_id,
            IDEMPOTENCY_DISPOSITION_EVENT_PREFIX_V01,
            "idempotency_disposition_previous_event_invalid",
            reasons,
        )
        _validate_optional_packet_identity_v01(
            value.predecessor_packet_id,
            "idempotency_disposition_predecessor_invalid",
            reasons,
        )
        _validate_optional_packet_identity_v01(
            value.successor_packet_id,
            "idempotency_disposition_successor_invalid",
            reasons,
        )
        if value.root_decision_ref is not None and (
            not validate_lowercase_sha256_hex_v01(
                value.root_decision_ref
            )[0]
        ):
            _reason_v01(reasons, "idempotency_disposition_root_ref_invalid")
        causes = value.cause_transition_event_ids
        if (
            type(causes) is not tuple
            or not causes
            or any(
                not validate_prefixed_sha256_identity_v01(
                    item,
                    prefix=ACTION_PACKET_TRANSITION_EVENT_PREFIX_V01,
                )[0]
                for item in causes
            )
        ):
            _reason_v01(reasons, "idempotency_disposition_causes_invalid")
        elif len(causes) != len(set(causes)):
            _reason_v01(reasons, "idempotency_disposition_causes_duplicate")
        evidence_valid, _ = validate_set_like_string_tuple_v01(
            value.evidence_refs,
            require_non_empty=True,
        )
        if not evidence_valid:
            _reason_v01(reasons, "idempotency_disposition_evidence_invalid")
        if not validate_signed_int64_v01(value.evaluation_time)[0]:
            _reason_v01(reasons, "idempotency_disposition_time_invalid")
        if not validate_identity_text_v01(value.evaluation_time_source)[0]:
            _reason_v01(reasons, "idempotency_disposition_time_source_invalid")
        if not validate_identity_text_v01(value.evaluation_context_id)[0]:
            _reason_v01(reasons, "idempotency_disposition_context_invalid")
        _validate_idempotency_disposition_event_matrix_v01(value, reasons)
        if reasons:
            return _result_v01(reasons)
        material = idempotency_disposition_event_material_v01(value)
        if len(material) != 16:
            _reason_v01(reasons, "idempotency_disposition_material_count_invalid")
        expected_id = build_domain_separated_identity_v01(
            domain=IDEMPOTENCY_DISPOSITION_EVENT_DOMAIN_V01,
            prefix=IDEMPOTENCY_DISPOSITION_EVENT_PREFIX_V01,
            material=material,
        )
        if (
            type(value.idempotency_disposition_event_id) is not str
            or value.idempotency_disposition_event_id != expected_id
        ):
            _reason_v01(reasons, "idempotency_disposition_event_id_mismatch")
        return _result_v01(reasons)
    except Exception:
        return False, ("idempotency_disposition_event_invalid",)


def _validate_optional_packet_identity_v01(
    value: object,
    reason: str,
    reasons: list[str],
) -> None:
    if value is not None and not validate_prefixed_sha256_identity_v01(
        value,
        prefix=ACTION_COMMIT_PACKET_ID_PREFIX_V01,
    )[0]:
        _reason_v01(reasons, reason)


def _validate_optional_prefixed_identity_v01(
    value: object,
    prefix: str,
    reason: str,
    reasons: list[str],
) -> None:
    if value is not None and not validate_prefixed_sha256_identity_v01(
        value,
        prefix=prefix,
    )[0]:
        _reason_v01(reasons, reason)


def _validate_idempotency_disposition_event_matrix_v01(
    event: IdempotencyDispositionEventV01,
    reasons: list[str],
) -> None:
    if event.event_class == "RESERVE":
        valid_common = (
            event.from_disposition == "UNCLAIMED"
            and event.to_disposition == "RESERVED"
            and event.from_owner_packet_id is None
            and event.to_owner_packet_id is not None
            and event.previous_disposition_event_id is None
            and event.root_decision_ref is not None
        )
        initial = (
            event.predecessor_packet_id is None
            and event.successor_packet_id is None
            and len(event.cause_transition_event_ids) == 1
            and len(event.evidence_refs) == 3
        )
        branch_a = (
            event.predecessor_packet_id is not None
            and event.successor_packet_id is not None
            and event.predecessor_packet_id != event.successor_packet_id
            and event.to_owner_packet_id == event.successor_packet_id
            and len(event.cause_transition_event_ids) == 2
            and len(event.evidence_refs) == 3
        )
        if not valid_common or not (initial or branch_a):
            _reason_v01(reasons, "idempotency_disposition_reserve_matrix_invalid")
        return
    if event.event_class in {
        "TRANSFER_RENEWAL",
        "TRANSFER_SUPERSESSION",
    }:
        if not (
            event.from_disposition == "RESERVED"
            and event.to_disposition == "RESERVED"
            and event.from_owner_packet_id is not None
            and event.to_owner_packet_id is not None
            and event.from_owner_packet_id != event.to_owner_packet_id
            and event.previous_disposition_event_id is not None
            and event.predecessor_packet_id == event.from_owner_packet_id
            and event.successor_packet_id == event.to_owner_packet_id
            and event.root_decision_ref is not None
            and len(event.cause_transition_event_ids) == 2
            and len(event.evidence_refs) == 3
        ):
            _reason_v01(reasons, "idempotency_disposition_transfer_matrix_invalid")
        return
    common_terminal = (
        event.from_owner_packet_id is not None
        and event.from_owner_packet_id == event.to_owner_packet_id
        and event.previous_disposition_event_id is not None
        and len(event.cause_transition_event_ids) == 1
        and event.root_decision_ref is None
        and event.predecessor_packet_id is None
        and event.successor_packet_id is None
        and len(event.evidence_refs) == 2
    )
    if event.event_class == "CONSUME":
        valid = (
            common_terminal
            and event.from_disposition == "RESERVED"
            and event.to_disposition == "CONSUMED"
        )
    elif event.event_class == "UNCERTAIN_CLOSE":
        valid = (
            common_terminal
            and event.from_disposition == "RESERVED"
            and event.to_disposition == "UNCERTAIN_CLOSED"
        )
    elif event.event_class == "RECEIPT_CONFIRM":
        valid = (
            common_terminal
            and event.from_disposition == "CONSUMED"
            and event.to_disposition == "CONSUMED"
        )
    else:
        return
    if not valid:
        _reason_v01(reasons, "idempotency_disposition_outcome_matrix_invalid")


def validate_idempotency_disposition_history_v01(
    history: object,
) -> tuple[bool, tuple[str, ...]]:
    try:
        if type(history) is not tuple:
            return False, ("idempotency_disposition_history_type_invalid",)
        reasons: list[str] = []
        seen_ids: set[str] = set()
        latest_by_key: dict[str, IdempotencyDispositionEventV01] = {}
        for event in history:
            valid, _ = validate_idempotency_disposition_event_v01(event)
            if not valid:
                _reason_v01(
                    reasons,
                    "idempotency_disposition_history_event_invalid",
                )
                continue
            event_id = event.idempotency_disposition_event_id
            if event_id in seen_ids:
                _reason_v01(
                    reasons,
                    "idempotency_disposition_history_duplicate",
                )
                continue
            seen_ids.add(event_id)
            previous = latest_by_key.get(event.idempotency_key)
            if previous is None:
                if (
                    event.previous_disposition_event_id is not None
                    or event.from_disposition != "UNCLAIMED"
                    or event.from_owner_packet_id is not None
                    or event.event_class != "RESERVE"
                ):
                    _reason_v01(
                        reasons,
                        "idempotency_disposition_history_initial_invalid",
                    )
            else:
                if (
                    event.previous_disposition_event_id
                    != previous.idempotency_disposition_event_id
                ):
                    _reason_v01(
                        reasons,
                        "idempotency_disposition_history_chain_invalid",
                    )
                if event.from_disposition != previous.to_disposition:
                    _reason_v01(
                        reasons,
                        "idempotency_disposition_history_state_mismatch",
                    )
                if event.from_owner_packet_id != previous.to_owner_packet_id:
                    _reason_v01(
                        reasons,
                        "idempotency_disposition_history_owner_mismatch",
                    )
                if previous.to_disposition == "UNCERTAIN_CLOSED":
                    _reason_v01(
                        reasons,
                        "uncertain_key_permanently_closed",
                    )
                if previous.to_disposition == "CONSUMED" and (
                    event.event_class != "RECEIPT_CONFIRM"
                    or previous.event_class != "CONSUME"
                ):
                    _reason_v01(
                        reasons,
                        "consumed_key_permanently_closed",
                    )
                if (
                    previous.event_class == "RECEIPT_CONFIRM"
                    and event.idempotency_key == previous.idempotency_key
                ):
                    _reason_v01(
                        reasons,
                        "consumed_key_permanently_closed",
                    )
                if event.event_class == "RESERVE":
                    _reason_v01(
                        reasons,
                        "idempotency_disposition_reacquisition_forbidden",
                    )
            latest_by_key[event.idempotency_key] = event
        return _result_v01(reasons)
    except Exception:
        return False, ("idempotency_disposition_history_invalid",)


def derive_idempotency_disposition_v01(
    history: object,
    *,
    idempotency_key: object,
) -> IdempotencyDispositionStateV01:
    try:
        valid_key, _ = validate_prefixed_sha256_identity_v01(
            idempotency_key,
            prefix=ACTION_IDEMPOTENCY_PREFIX_V01,
        )
        if not valid_key:
            raise ValueError("idempotency_disposition_key_invalid")
        valid, reasons = validate_idempotency_disposition_history_v01(history)
        if not valid:
            raise ValueError(reasons[0])
        matching = tuple(
            event for event in history if event.idempotency_key == idempotency_key
        )
        if not matching:
            return IdempotencyDispositionStateV01(
                idempotency_key=idempotency_key,
                disposition="UNCLAIMED",
                reservation_owner_packet_id=None,
                latest_disposition_event_id=None,
                event_count=0,
            )
        latest = matching[-1]
        return IdempotencyDispositionStateV01(
            idempotency_key=idempotency_key,
            disposition=latest.to_disposition,
            reservation_owner_packet_id=latest.to_owner_packet_id,
            latest_disposition_event_id=(
                latest.idempotency_disposition_event_id
            ),
            event_count=len(matching),
        )
    except ValueError as exc:
        raise ValueError(
            _stable_exception_reason_v01(
                exc,
                fallback="idempotency_disposition_history_invalid",
            )
        ) from None
    except Exception:
        raise ValueError("idempotency_disposition_history_invalid") from None


def build_action_packet_lifecycle_entry_v01(
    *,
    root_bound_genesis: object,
    action_packet_transition_registry_profile: object,
) -> ActionPacketLifecycleEntryV01:
    try:
        if validate_action_packet_transition_registry_profile_v01(
            action_packet_transition_registry_profile
        ):
            raise ValueError("action_packet_lifecycle_registry_invalid")
        entry = ActionPacketLifecycleEntryV01(
            root_bound_genesis=root_bound_genesis,
            transition_registry_id=(
                action_packet_transition_registry_profile.transition_registry_id
            ),
            transition_events=(),
        )
        valid, reasons = validate_action_packet_lifecycle_entry_v01(
            entry,
            action_packet_transition_registry_profile=(
                action_packet_transition_registry_profile
            ),
        )
        if not valid:
            raise ValueError(reasons[0])
        return entry
    except ValueError as exc:
        raise ValueError(
            _stable_exception_reason_v01(
                exc,
                fallback="action_packet_lifecycle_entry_invalid",
            )
        ) from None
    except Exception:
        raise ValueError("action_packet_lifecycle_entry_invalid") from None


def _validate_action_packet_lifecycle_entry_core_v01(
    value: object,
    *,
    action_packet_transition_registry_profile: object = None,
    invalidation_contexts: object = None,
    idempotency_disposition_events: object = None,
    lifecycle_entries: object = None,
    validation_pass: _ActionPacketRegistryValidationPassV01 | None = None,
) -> tuple[bool, tuple[str, ...]]:
    try:
        if type(value) is not ActionPacketLifecycleEntryV01:
            return False, ("action_packet_lifecycle_entry_type_invalid",)
        registry = _exact_action_packet_transition_registry_v01(
            action_packet_transition_registry_profile
        )
        reasons: list[str] = []
        genesis_result = (
            _cached_root_bound_validation_v01(
                validation_pass,
                value.root_bound_genesis,
            )
            if validation_pass is not None
            else validate_supplier_root_bound_action_commit_packet_v02_projection_v01(
                value.root_bound_genesis
            )
        )
        genesis_valid, _ = genesis_result
        if not genesis_valid:
            _reason_v01(reasons, "action_packet_lifecycle_genesis_invalid")
        if (
            type(value.transition_registry_id) is not str
            or value.transition_registry_id != registry.transition_registry_id
        ):
            _reason_v01(reasons, "action_packet_lifecycle_registry_id_mismatch")
        history_valid, history_reasons = (
            _validate_action_packet_transition_history_core_v01(
                value.transition_events,
                root_bound_genesis=value.root_bound_genesis,
                action_packet_transition_registry_profile=registry,
                invalidation_contexts=invalidation_contexts,
                idempotency_disposition_events=(
                    idempotency_disposition_events
                ),
                lifecycle_entries=lifecycle_entries,
                root_bound_validation_result=genesis_result,
                validation_pass=validation_pass,
            )
        )
        if not history_valid:
            reasons.extend(history_reasons)
        return _result_v01(reasons)
    except Exception:
        return False, ("action_packet_lifecycle_entry_invalid",)


def validate_action_packet_lifecycle_entry_v01(
    value: object,
    *,
    action_packet_transition_registry_profile: object = None,
    invalidation_contexts: object = None,
    idempotency_disposition_events: object = None,
    lifecycle_entries: object = None,
) -> tuple[bool, tuple[str, ...]]:
    return _validate_action_packet_lifecycle_entry_core_v01(
        value,
        action_packet_transition_registry_profile=(
            action_packet_transition_registry_profile
        ),
        invalidation_contexts=invalidation_contexts,
        idempotency_disposition_events=idempotency_disposition_events,
        lifecycle_entries=lifecycle_entries,
    )


def _validate_action_packet_transition_history_core_v01(
    transition_events: object,
    *,
    root_bound_genesis: object,
    action_packet_transition_registry_profile: object,
    invalidation_contexts: object = None,
    idempotency_disposition_events: object = None,
    lifecycle_entries: object = None,
    root_bound_validation_result: tuple[
        bool,
        tuple[str, ...],
    ]
    | None = None,
    validation_pass: _ActionPacketRegistryValidationPassV01 | None = None,
) -> tuple[bool, tuple[str, ...]]:
    try:
        if type(transition_events) is not tuple:
            return False, ("action_packet_transition_history_type_invalid",)
        registry = _exact_action_packet_transition_registry_v01(
            action_packet_transition_registry_profile
        )
        genesis_result = (
            root_bound_validation_result
            if root_bound_validation_result is not None
            else _cached_root_bound_validation_v01(
                validation_pass,
                root_bound_genesis,
            )
            if validation_pass is not None
            else validate_supplier_root_bound_action_commit_packet_v02_projection_v01(
                root_bound_genesis
            )
        )
        genesis_valid, _ = genesis_result
        if not genesis_valid:
            return False, ("action_packet_transition_genesis_invalid",)
        canonical = root_bound_genesis.canonical_projection
        packet_id = root_bound_genesis.packet_identity.packet_id
        idempotency_key = canonical.idempotency_identity.idempotency_key
        owning_root = canonical.owning_local_root_id
        dependency_fingerprint = (
            canonical.dependency_set_candidate_fingerprint
        )
        temporal_fingerprint = canonical.temporal_authority_fingerprint
        source_root_decision_id = (
            root_bound_genesis.root_decision_projection.root_decision_result
            .decision_id
        )
        contexts = () if invalidation_contexts is None else invalidation_contexts
        dispositions = (
            ()
            if idempotency_disposition_events is None
            else idempotency_disposition_events
        )
        entries = () if lifecycle_entries is None else lifecycle_entries
        if (
            type(contexts) is not tuple
            or any(
                type(context) is not _ActionPacketInvalidationContextV01
                for context in contexts
            )
            or type(dispositions) is not tuple
            or any(
                type(disposition) is not IdempotencyDispositionEventV01
                for disposition in dispositions
            )
            or type(entries) is not tuple
            or any(
                type(entry) is not ActionPacketLifecycleEntryV01
                for entry in entries
            )
        ):
            return False, ("action_packet_transition_context_invalid",)
        reasons: list[str] = []
        seen_ids: set[str] = set()
        current_state = "CREATED"
        failed_provenance: str | None = None
        attempt_count = 0
        for index, event in enumerate(transition_events):
            event_valid, _ = validate_action_packet_transition_event_v01(
                event,
                action_packet_transition_registry_profile=registry,
            )
            if not event_valid:
                _reason_v01(reasons, "action_packet_transition_event_invalid")
                continue
            if event.transition_event_id in seen_ids:
                _reason_v01(reasons, "action_packet_transition_history_duplicate")
            seen_ids.add(event.transition_event_id)
            expected_previous = (
                None
                if index == 0
                else transition_events[index - 1].transition_event_id
            )
            if event.previous_transition_event_id != expected_previous:
                _reason_v01(reasons, "action_packet_transition_history_chain_invalid")
            if index == 0 and event.transition_rule_id not in {
                "g2a_t01_activate_root_authorization",
                "g2a_t06_created_block",
                "g2a_t11_created_expire",
            }:
                _reason_v01(reasons, "action_packet_transition_first_event_invalid")
            if (
                event.packet_id != packet_id
                or event.idempotency_key != idempotency_key
            ):
                _reason_v01(reasons, "action_packet_transition_packet_key_mismatch")
            if event.owning_local_root_id != owning_root:
                _reason_v01(reasons, "action_packet_transition_root_mismatch")
            if (
                event.dependency_set_candidate_fingerprint
                != dependency_fingerprint
            ):
                _reason_v01(
                    reasons,
                    "action_packet_transition_dependency_mismatch",
                )
            if event.temporal_authority_fingerprint != temporal_fingerprint:
                _reason_v01(reasons, "action_packet_transition_temporal_mismatch")
            temporal_reason = _action_packet_transition_temporal_reason_v01(
                root_bound_genesis,
                event,
            )
            if temporal_reason is not None:
                _reason_v01(reasons, temporal_reason)
            if event.source_state != current_state:
                _reason_v01(reasons, "action_packet_transition_source_mismatch")
            if (
                event.transition_rule_id
                == "g2a_t01_activate_root_authorization"
                and event.root_decision_ref != source_root_decision_id
            ):
                _reason_v01(
                    reasons,
                    "action_packet_transition_source_authorization_mismatch",
                )
            if event.transition_rule_id in {
                "g2a_t06_created_block",
                "g2a_t07_authorized_block",
                "g2a_t08_queued_block",
                "g2a_t09_pending_block",
                "g2a_t10_failed_block",
            }:
                matching_contexts = tuple(
                    context
                    for context in contexts
                    if context.invalidation_evidence.packet_id == packet_id
                    and _invalidation_context_matches_transition_reference_v01(
                        context,
                        event,
                    )
                )
                if len(matching_contexts) != 1:
                    _reason_v01(
                        reasons,
                        "invalidation_transition_requires_g2a3_binding",
                    )
                else:
                    context_valid, context_reasons = (
                        _validate_contextual_invalidation_transition_v01(
                            matching_contexts[0],
                            event,
                            root_bound_genesis=root_bound_genesis,
                            preceding_events=transition_events[:index],
                            disposition_events=dispositions,
                            validation_pass=validation_pass,
                        )
                    )
                    if not context_valid:
                        reasons.extend(context_reasons)
            if event.transition_rule_id in {
                "g2a_t16_authorized_revoke",
                "g2a_t17_queued_revoke",
                "g2a_t18_pending_revoke",
                "g2a_t19_failed_revoke",
            }:
                matching_contexts = tuple(
                    context
                    for context in contexts
                    if context.invalidation_evidence.packet_id == packet_id
                    and _invalidation_context_matches_transition_reference_v01(
                        context,
                        event,
                    )
                )
                if len(matching_contexts) != 1:
                    _reason_v01(
                        reasons,
                        "authority_transition_requires_g2a3_binding",
                    )
                else:
                    context_valid, context_reasons = (
                        _validate_contextual_invalidation_transition_v01(
                            matching_contexts[0],
                            event,
                            root_bound_genesis=root_bound_genesis,
                            preceding_events=transition_events[:index],
                            disposition_events=dispositions,
                            validation_pass=validation_pass,
                        )
                    )
                    if not context_valid:
                        reasons.extend(context_reasons)
            if event.transition_rule_id in {
                "g2a_t20_authorized_supersede",
                "g2a_t21_queued_supersede",
                "g2a_t22_pending_supersede",
                "g2a_t23_failed_supersede",
            }:
                matching_contexts = tuple(
                    context
                    for context in contexts
                    if context.invalidation_evidence.packet_id == packet_id
                    and _invalidation_context_matches_transition_reference_v01(
                        context,
                        event,
                    )
                )
                if len(matching_contexts) != 1:
                    _reason_v01(
                        reasons,
                        "authority_transition_requires_g2a3_binding",
                    )
                else:
                    context = matching_contexts[0]
                    successor_entries = tuple(
                        entry
                        for entry in entries
                        if entry.root_bound_genesis.packet_identity.packet_id
                        == context.supersession_successor_packet_id
                    )
                    if len(successor_entries) != 1:
                        _reason_v01(
                            reasons,
                            "action_packet_supersession_successor_invalid",
                        )
                    else:
                        context_valid, context_reasons = (
                            _validate_contextual_invalidation_transition_v01(
                                context,
                                event,
                                root_bound_genesis=root_bound_genesis,
                                preceding_events=transition_events[:index],
                                disposition_events=dispositions,
                                supersession_successor=(
                                    successor_entries[0].root_bound_genesis
                                ),
                                validation_pass=validation_pass,
                            )
                        )
                        if not context_valid:
                            reasons.extend(context_reasons)
            if current_state == "FAILED" and (
                failed_provenance != "FAILED_NON_CONSUMING"
                or event.transition_rule_id
                not in {
                    "g2a_t10_failed_block",
                    "g2a_t15_failed_expire",
                    "g2a_t19_failed_revoke",
                    "g2a_t23_failed_supersede",
                    "g2a_t25_retry",
                }
            ):
                _reason_v01(reasons, "failed_provenance_invalid")
            if (
                event.transition_rule_id == "g2a_t25_retry"
                and canonical.authority_policy.retry_policy
                != "NON_CONSUMING_RETRY"
            ):
                _reason_v01(reasons, "retry_policy_invalid")
            if event.transition_rule_id == "g2a_t03_pending":
                attempt_count += 1
                expected_attempt = build_action_execution_attempt_identity_v01(
                    packet_id=packet_id,
                    idempotency_key=idempotency_key,
                    attempt_ordinal=attempt_count,
                    evaluation_context_id=event.evaluation_context_id,
                )
                if event.execution_attempt_id != expected_attempt.execution_attempt_id:
                    _reason_v01(
                        reasons,
                        "action_packet_transition_attempt_ordinal_mismatch",
                    )
            if event.transition_rule_id in {
                "g2a_t04_fulfill_mock",
                "g2a_t24_nonconsuming_failure",
                "g2a_t26_uncertain_adapter_outcome",
            }:
                if (
                    index == 0
                    or transition_events[index - 1].transition_rule_id
                    != "g2a_t03_pending"
                    or event.execution_attempt_id
                    != transition_events[index - 1].execution_attempt_id
                ):
                    _reason_v01(
                        reasons,
                        "action_packet_transition_outcome_attempt_mismatch",
                    )
                if (
                    index > 0
                    and event.evaluation_context_id
                    != transition_events[index - 1].evaluation_context_id
                ):
                    _reason_v01(
                        reasons,
                        "action_packet_transition_attempt_context_mismatch",
                    )
            if event.transition_rule_id == "g2a_t05_receipt":
                if (
                    index == 0
                    or transition_events[index - 1].transition_rule_id
                    != "g2a_t04_fulfill_mock"
                    or event.execution_attempt_id
                    != transition_events[index - 1].execution_attempt_id
                ):
                    _reason_v01(
                        reasons,
                        "action_packet_transition_receipt_attempt_mismatch",
                    )
                if (
                    index > 0
                    and event.evaluation_context_id
                    != transition_events[index - 1].evaluation_context_id
                ):
                    _reason_v01(
                        reasons,
                        "action_packet_transition_attempt_context_mismatch",
                    )
            current_state = event.target_state
            if event.transition_rule_id == "g2a_t24_nonconsuming_failure":
                failed_provenance = "FAILED_NON_CONSUMING"
            elif event.transition_rule_id == "g2a_t26_uncertain_adapter_outcome":
                failed_provenance = "FAILED_UNCERTAIN_TERMINAL"
            elif current_state != "FAILED":
                failed_provenance = None
        return _result_v01(reasons)
    except Exception:
        return False, ("action_packet_transition_history_invalid",)


def validate_action_packet_transition_history_v01(
    transition_events: object,
    *,
    root_bound_genesis: object,
    action_packet_transition_registry_profile: object,
    invalidation_contexts: object = None,
    idempotency_disposition_events: object = None,
    lifecycle_entries: object = None,
) -> tuple[bool, tuple[str, ...]]:
    return _validate_action_packet_transition_history_core_v01(
        transition_events,
        root_bound_genesis=root_bound_genesis,
        action_packet_transition_registry_profile=(
            action_packet_transition_registry_profile
        ),
        invalidation_contexts=invalidation_contexts,
        idempotency_disposition_events=idempotency_disposition_events,
        lifecycle_entries=lifecycle_entries,
    )


def _packet_local_disposition_history_v01(
    root_bound_genesis: SupplierRootBoundActionCommitPacketV02ProjectionV01,
    preceding_events: tuple[ActionPacketTransitionEventV01, ...],
    disposition_events: tuple[IdempotencyDispositionEventV01, ...],
) -> tuple[IdempotencyDispositionEventV01, ...]:
    key = (
        root_bound_genesis.canonical_projection.idempotency_identity
        .idempotency_key
    )
    packet_id = root_bound_genesis.packet_identity.packet_id
    preceding_ids = {
        event.transition_event_id for event in preceding_events
    }
    activation_ids = {
        event.transition_event_id
        for event in preceding_events
        if (
            event.packet_id == packet_id
            and event.transition_rule_id
            == "g2a_t01_activate_root_authorization"
        )
    }
    return tuple(
        event
        for event in disposition_events
        if event.idempotency_key == key
        and (
            all(
                cause_id in preceding_ids
                for cause_id in event.cause_transition_event_ids
            )
            or (
                event.event_class
                in {
                    "RESERVE",
                    "TRANSFER_RENEWAL",
                    "TRANSFER_SUPERSESSION",
                }
                and event.to_owner_packet_id == packet_id
                and any(
                    cause_id in activation_ids
                    for cause_id in event.cause_transition_event_ids
                )
            )
        )
    )


def _disposition_before_transition_events_v01(
    root_bound_genesis: SupplierRootBoundActionCommitPacketV02ProjectionV01,
    preceding_events: tuple[ActionPacketTransitionEventV01, ...],
    disposition_events: tuple[IdempotencyDispositionEventV01, ...],
) -> IdempotencyDispositionStateV01:
    key = (
        root_bound_genesis.canonical_projection.idempotency_identity
        .idempotency_key
    )
    return _derive_idempotency_disposition_unchecked_v01(
        _packet_local_disposition_history_v01(
            root_bound_genesis,
            preceding_events,
            disposition_events,
        ),
        key,
    )


def _validate_contextual_invalidation_transition_v01(
    context: object,
    event: object,
    *,
    root_bound_genesis: object,
    preceding_events: object,
    disposition_events: object,
    supersession_successor: object = None,
    validation_pass: _ActionPacketRegistryValidationPassV01 | None = None,
) -> tuple[bool, tuple[str, ...]]:
    try:
        if (
            type(context) is not _ActionPacketInvalidationContextV01
            or type(event) is not ActionPacketTransitionEventV01
            or type(root_bound_genesis)
            is not SupplierRootBoundActionCommitPacketV02ProjectionV01
            or type(preceding_events) is not tuple
            or any(
                type(item) is not ActionPacketTransitionEventV01
                for item in preceding_events
            )
            or type(disposition_events) is not tuple
            or any(
                type(item) is not IdempotencyDispositionEventV01
                for item in disposition_events
            )
        ):
            return False, (
                "action_packet_invalidation_transition_context_invalid",
            )
        context_valid, _ = (
            _cached_invalidation_context_validation_v01(
                validation_pass,
                context,
                root_bound_genesis,
                supersession_successor=supersession_successor,
            )
            if validation_pass is not None
            else _validate_action_packet_invalidation_context_v01(
                context,
                root_bound_genesis,
                supersession_successor=supersession_successor,
            )
        )
        if not context_valid:
            return False, (
                "action_packet_invalidation_transition_context_invalid",
            )
        evidence = context.invalidation_evidence
        canonical = root_bound_genesis.canonical_projection
        packet_id = root_bound_genesis.packet_identity.packet_id
        reasons: list[str] = []
        if (
            event.packet_id != packet_id
            or event.evaluation_time != evidence.evaluation_time
            or event.evaluation_time_source
            != evidence.evaluation_time_source
            or event.evaluation_context_id != evidence.evaluation_context_id
        ):
            _reason_v01(
                reasons,
                "action_packet_invalidation_transition_context_mismatch",
            )
        deterministic_codes = {
            "g2a_t06_created_block": "blocking_evidence_valid",
            "g2a_t07_authorized_block": "blocking_evidence_valid",
            "g2a_t08_queued_block": "blocking_evidence_valid",
            "g2a_t09_pending_block": (
                "immediate_eligibility_failure_valid"
            ),
            "g2a_t10_failed_block": (
                "retry_ineligibility_evidence_valid"
            ),
        }
        if event.transition_rule_id in deterministic_codes:
            invalidation_id = evidence.invalidation_evidence_id
            if not _transition_evidence_binding_matches_v01(
                event,
                evidence_code=deterministic_codes[
                    event.transition_rule_id
                ],
                evidence_ref=invalidation_id,
                evidence_sha256=invalidation_id,
                validator_profile_id=(
                    ACTION_INVALIDATION_EVIDENCE_PROFILE_ID_V01
                ),
            ):
                _reason_v01(
                    reasons,
                    "action_packet_invalidation_evidence_binding_invalid",
                )
            if event.root_decision_ref is not None:
                _reason_v01(
                    reasons,
                    "action_packet_deterministic_block_root_ref_forbidden",
                )
        elif event.transition_rule_id in {
            "g2a_t16_authorized_revoke",
            "g2a_t17_queued_revoke",
            "g2a_t18_pending_revoke",
            "g2a_t19_failed_revoke",
        }:
            binding = context.accepted_revocation_binding
            if type(binding) is not AcceptedRevocationBindingV01:
                _reason_v01(
                    reasons,
                    "action_packet_revocation_binding_invalid",
                )
            else:
                binding_id = binding.accepted_revocation_binding_id
                if not _transition_evidence_binding_matches_v01(
                    event,
                    evidence_code="accepted_revocation_binding_valid",
                    evidence_ref=binding_id,
                    evidence_sha256=binding_id[
                        len(ACCEPTED_REVOCATION_BINDING_PREFIX_V01) :
                    ],
                    validator_profile_id=(
                        _ACCEPTED_REVOCATION_BINDING_VALIDATOR_PROFILE_ID_V01
                    ),
                ):
                    _reason_v01(
                        reasons,
                        "action_packet_revocation_binding_invalid",
                    )
                if event.root_decision_ref != (
                    binding.revocation_root_decision_id
                ):
                    _reason_v01(
                        reasons,
                        "action_packet_revocation_root_ref_invalid",
                    )
            source_result = (
                root_bound_genesis.root_decision_projection
                .root_decision_result
            )
            if not _transition_evidence_binding_matches_v01(
                event,
                evidence_code="source_authorization_binding_valid",
                evidence_ref=source_result.decision_id,
                evidence_sha256=(
                    root_bound_genesis.root_decision_projection
                    .source_root_decision_hash
                ),
                validator_profile_id=(
                    _ROOT_DECISION_RESULT_VALIDATOR_PROFILE_ID_V01
                ),
            ):
                _reason_v01(
                    reasons,
                    "action_packet_source_authorization_binding_invalid",
                )
        elif event.transition_rule_id in {
            "g2a_t20_authorized_supersede",
            "g2a_t21_queued_supersede",
            "g2a_t22_pending_supersede",
            "g2a_t23_failed_supersede",
        }:
            successor = supersession_successor
            binding = context.accepted_supersession_binding
            if (
                type(successor)
                is not SupplierRootBoundActionCommitPacketV02ProjectionV01
                or type(binding) is not AcceptedSupersessionBindingV01
            ):
                _reason_v01(
                    reasons,
                    "action_packet_supersession_context_invalid",
                )
            else:
                successor_packet_id = successor.packet_identity.packet_id
                binding_id = binding.accepted_supersession_binding_id
                for evidence_code, evidence_ref, evidence_hash, profile in (
                    (
                        "successor_packet_valid",
                        successor_packet_id,
                        successor_packet_id[
                            len(ACTION_COMMIT_PACKET_ID_PREFIX_V01) :
                        ],
                        _ACTION_COMMIT_PACKET_IDENTITY_PROFILE_ID_V01,
                    ),
                    (
                        "accepted_supersession_binding_valid",
                        binding_id,
                        binding_id[
                            len(
                                ACCEPTED_SUPERSESSION_BINDING_PREFIX_V01
                            ) :
                        ],
                        (
                            _ACCEPTED_SUPERSESSION_BINDING_VALIDATOR_PROFILE_ID_V01
                        ),
                    ),
                    (
                        "predecessor_binding_valid",
                        packet_id,
                        packet_id[
                            len(ACTION_COMMIT_PACKET_ID_PREFIX_V01) :
                        ],
                        _ACTION_COMMIT_PACKET_IDENTITY_PROFILE_ID_V01,
                    ),
                ):
                    if not _transition_evidence_binding_matches_v01(
                        event,
                        evidence_code=evidence_code,
                        evidence_ref=evidence_ref,
                        evidence_sha256=evidence_hash,
                        validator_profile_id=profile,
                    ):
                        _reason_v01(
                            reasons,
                            "action_packet_supersession_binding_invalid",
                        )
                if event.root_decision_ref != (
                    binding.supersession_root_decision_id
                ):
                    _reason_v01(
                        reasons,
                        "action_packet_supersession_root_ref_invalid",
                    )
        else:
            return False, (
                "action_packet_invalidation_transition_rule_invalid",
            )
        if event.transition_rule_id == "g2a_t06_created_block":
            packet_identity = root_bound_genesis.packet_identity.packet_id
            if not _transition_evidence_binding_matches_v01(
                event,
                evidence_code="packet_genesis_valid",
                evidence_ref=packet_identity,
                evidence_sha256=packet_identity[
                    len(ACTION_COMMIT_PACKET_ID_PREFIX_V01) :
                ],
                validator_profile_id=(
                    _ACTION_COMMIT_PACKET_IDENTITY_PROFILE_ID_V01
                ),
            ):
                _reason_v01(
                    reasons,
                    "action_packet_genesis_binding_invalid",
                )
        if event.transition_rule_id in {
            "g2a_t07_authorized_block",
            "g2a_t08_queued_block",
        }:
            fingerprint = canonical.authority_policy_fingerprint
            if not _transition_evidence_binding_matches_v01(
                event,
                evidence_code="authority_policy_valid",
                evidence_ref=fingerprint,
                evidence_sha256=fingerprint,
                validator_profile_id=ACTION_AUTHORITY_POLICY_PROFILE_ID_V01,
            ):
                _reason_v01(
                    reasons,
                    "action_packet_authority_policy_binding_invalid",
                )
        disposition = _disposition_before_transition_events_v01(
            root_bound_genesis,
            preceding_events,
            disposition_events,
        )
        if event.transition_rule_id in {
            "g2a_t20_authorized_supersede",
            "g2a_t21_queued_supersede",
            "g2a_t22_pending_supersede",
            "g2a_t23_failed_supersede",
        }:
            successor_packet_id = (
                supersession_successor.packet_identity.packet_id
                if type(supersession_successor)
                is SupplierRootBoundActionCommitPacketV02ProjectionV01
                else None
            )
            consuming_dispositions = tuple(
                item
                for item in disposition_events
                if event.transition_event_id
                in item.cause_transition_event_ids
                and item.from_owner_packet_id == packet_id
                and item.to_owner_packet_id == successor_packet_id
                and item.event_class
                in {
                    "TRANSFER_RENEWAL",
                    "TRANSFER_SUPERSESSION",
                }
            )
            if len(consuming_dispositions) == 1:
                disposition_index = disposition_events.index(
                    consuming_dispositions[0]
                )
                disposition = _derive_idempotency_disposition_unchecked_v01(
                    disposition_events[:disposition_index],
                    canonical.idempotency_identity.idempotency_key,
                )
        reservation_rules = {
            "g2a_t07_authorized_block",
            "g2a_t08_queued_block",
            "g2a_t09_pending_block",
            "g2a_t10_failed_block",
            "g2a_t16_authorized_revoke",
            "g2a_t17_queued_revoke",
            "g2a_t18_pending_revoke",
            "g2a_t19_failed_revoke",
        }
        if event.transition_rule_id in reservation_rules:
            latest_id = disposition.latest_disposition_event_id
            if (
                disposition.disposition != "RESERVED"
                or disposition.reservation_owner_packet_id != packet_id
                or type(latest_id) is not str
                or not _transition_evidence_binding_matches_v01(
                    event,
                    evidence_code="idempotency_reservation_owned",
                    evidence_ref=latest_id if type(latest_id) is str else "",
                    evidence_sha256=(
                        latest_id[
                            len(
                                IDEMPOTENCY_DISPOSITION_EVENT_PREFIX_V01
                            ) :
                        ]
                        if type(latest_id) is str
                        else ""
                    ),
                    validator_profile_id=(
                        IDEMPOTENCY_DISPOSITION_EVENT_PROFILE_ID_V01
                    ),
                )
            ):
                _reason_v01(
                    reasons,
                    "action_packet_invalidation_reservation_invalid",
                )
        if event.transition_rule_id in {
            "g2a_t20_authorized_supersede",
            "g2a_t21_queued_supersede",
            "g2a_t22_pending_supersede",
            "g2a_t23_failed_supersede",
        }:
            latest_id = disposition.latest_disposition_event_id
            if (
                disposition.disposition != "RESERVED"
                or disposition.reservation_owner_packet_id != packet_id
                or type(latest_id) is not str
                or not _transition_evidence_binding_matches_v01(
                    event,
                    evidence_code="idempotency_transfer_valid",
                    evidence_ref=latest_id if type(latest_id) is str else "",
                    evidence_sha256=(
                        latest_id[
                            len(
                                IDEMPOTENCY_DISPOSITION_EVENT_PREFIX_V01
                            ) :
                        ]
                        if type(latest_id) is str
                        else ""
                    ),
                    validator_profile_id=(
                        IDEMPOTENCY_DISPOSITION_EVENT_PROFILE_ID_V01
                    ),
                )
            ):
                _reason_v01(
                    reasons,
                    "action_packet_supersession_transfer_binding_invalid",
                )
        if event.transition_rule_id in {
            "g2a_t09_pending_block",
            "g2a_t18_pending_revoke",
            "g2a_t22_pending_supersede",
        }:
            latest = preceding_events[-1] if preceding_events else None
            if (
                type(latest) is not ActionPacketTransitionEventV01
                or latest.transition_rule_id != "g2a_t03_pending"
                or type(latest.execution_attempt_id) is not str
                or not _transition_evidence_binding_matches_v01(
                    event,
                    evidence_code="adapter_not_called",
                    evidence_ref=(
                        latest.execution_attempt_id
                        if type(latest) is ActionPacketTransitionEventV01
                        and type(latest.execution_attempt_id) is str
                        else ""
                    ),
                    evidence_sha256=(
                        latest.execution_attempt_id[
                            len(EXECUTION_ATTEMPT_IDENTITY_PREFIX_V01) :
                        ]
                        if type(latest) is ActionPacketTransitionEventV01
                        and type(latest.execution_attempt_id) is str
                        else ""
                    ),
                    validator_profile_id=(
                        EXECUTION_ATTEMPT_IDENTITY_PROFILE_ID_V01
                    ),
                )
            ):
                _reason_v01(
                    reasons,
                    "action_packet_invalidation_adapter_state_invalid",
                )
        if event.transition_rule_id in {
            "g2a_t10_failed_block",
            "g2a_t19_failed_revoke",
            "g2a_t23_failed_supersede",
        }:
            latest = preceding_events[-1] if preceding_events else None
            if (
                type(latest) is not ActionPacketTransitionEventV01
                or latest.transition_rule_id
                != "g2a_t24_nonconsuming_failure"
                or not _transition_evidence_binding_matches_v01(
                    event,
                    evidence_code="failed_non_consuming_provenance_valid",
                    evidence_ref=(
                        latest.transition_event_id
                        if type(latest) is ActionPacketTransitionEventV01
                        else ""
                    ),
                    evidence_sha256=(
                        latest.transition_event_id[
                            len(ACTION_PACKET_TRANSITION_EVENT_PREFIX_V01) :
                        ]
                        if type(latest) is ActionPacketTransitionEventV01
                        else ""
                    ),
                    validator_profile_id=(
                        ACTION_PACKET_TRANSITION_EVENT_PROFILE_ID_V01
                    ),
                )
            ):
                _reason_v01(
                    reasons,
                    "action_packet_failed_provenance_binding_invalid",
                )
        return _result_v01(reasons)
    except Exception:
        return False, (
            "action_packet_invalidation_transition_context_invalid",
        )


def _action_packet_transition_temporal_reason_v01(
    root_bound_genesis: object,
    event: object,
) -> str | None:
    try:
        if (
            type(root_bound_genesis)
            is not SupplierRootBoundActionCommitPacketV02ProjectionV01
            or type(event) is not ActionPacketTransitionEventV01
        ):
            return "action_packet_transition_temporal_truth_invalid"
        evaluation = evaluate_temporal_authority_v01(
            root_bound_genesis.canonical_projection.temporal_authority,
            evaluation_time=event.evaluation_time,
        )
        rule_id = event.transition_rule_id
        if rule_id == "g2a_t01_activate_root_authorization":
            if evaluation.outcome == TEMPORAL_OUTCOME_EXPIRED_V01:
                return "action_packet_activation_after_expiry_forbidden"
            return None
        if rule_id in {
            "g2a_t02_queue",
            "g2a_t03_pending",
            "g2a_t25_retry",
        }:
            if (
                evaluation.outcome != TEMPORAL_OUTCOME_VALID_V01
                or type(evaluation.executable) is not bool
                or not evaluation.executable
            ):
                return "action_packet_transition_temporal_truth_invalid"
            return None
        if rule_id in {
            "g2a_t11_created_expire",
            "g2a_t12_authorized_expire",
            "g2a_t13_queued_expire",
            "g2a_t14_pending_expire",
            "g2a_t15_failed_expire",
        }:
            if evaluation.outcome != TEMPORAL_OUTCOME_EXPIRED_V01:
                return "action_packet_expiry_not_reached"
        return None
    except Exception:
        return "action_packet_transition_temporal_truth_invalid"


def _exact_action_packet_transition_registry_v01(
    value: object,
) -> ActionPacketTransitionRegistryProfileV01:
    registry = (
        build_action_packet_transition_registry_profile_v01()
        if value is None
        else value
    )
    if validate_action_packet_transition_registry_profile_v01(registry):
        raise ValueError("action_packet_lifecycle_registry_invalid")
    expected = build_action_packet_transition_registry_profile_v01()
    if (
        type(registry) is not ActionPacketTransitionRegistryProfileV01
        or registry != expected
    ):
        raise ValueError("action_packet_lifecycle_registry_invalid")
    return registry


def derive_action_packet_lifecycle_state_v01(
    registry: object,
    *,
    packet_id: object,
    action_packet_transition_registry_profile: object = None,
) -> ActionPacketLifecycleStateV01:
    try:
        valid, reasons = validate_action_commit_packet_registry_v02(registry)
        if not valid:
            raise ValueError(reasons[0])
        transition_registry = _exact_action_packet_transition_registry_v01(
            action_packet_transition_registry_profile
        )
        entry = _find_lifecycle_entry_v01(registry, packet_id)
        if entry.transition_registry_id != transition_registry.transition_registry_id:
            raise ValueError("action_packet_lifecycle_registry_id_mismatch")
        return _derive_action_packet_lifecycle_state_unchecked_v01(
            entry,
            registry.idempotency_disposition_events,
        )
    except ValueError as exc:
        raise ValueError(
            _stable_exception_reason_v01(
                exc,
                fallback="action_packet_lifecycle_state_invalid",
            )
        ) from None
    except Exception:
        raise ValueError("action_packet_lifecycle_state_invalid") from None


def _derive_action_packet_lifecycle_state_unchecked_v01(
    entry: ActionPacketLifecycleEntryV01,
    disposition_history: tuple[IdempotencyDispositionEventV01, ...],
) -> ActionPacketLifecycleStateV01:
    genesis = entry.root_bound_genesis
    packet_id = genesis.packet_identity.packet_id
    idempotency_key = (
        genesis.canonical_projection.idempotency_identity.idempotency_key
    )
    events = entry.transition_events
    latest = events[-1] if events else None
    lifecycle_state = latest.target_state if latest is not None else "CREATED"
    failed_provenance = None
    if latest is not None:
        if latest.transition_rule_id == "g2a_t24_nonconsuming_failure":
            failed_provenance = "FAILED_NON_CONSUMING"
        elif latest.transition_rule_id == "g2a_t26_uncertain_adapter_outcome":
            failed_provenance = "FAILED_UNCERTAIN_TERMINAL"
    disposition = _derive_idempotency_disposition_unchecked_v01(
        disposition_history,
        idempotency_key,
    )
    terminal_receipt_ref = (
        latest.receipt_ref
        if latest is not None
        and latest.transition_rule_id == "g2a_t05_receipt"
        else None
    )
    lifecycle_terminal = lifecycle_state in {
        "RECEIPT_RECEIVED",
        "BLOCKED",
        "EXPIRED",
        "REVOKED",
        "SUPERSEDED",
    } or failed_provenance == "FAILED_UNCERTAIN_TERMINAL"
    eligible = (
        lifecycle_state == "PENDING_FULFILLMENT"
        and disposition.disposition == "RESERVED"
        and disposition.reservation_owner_packet_id == packet_id
        and terminal_receipt_ref is None
    )
    return ActionPacketLifecycleStateV01(
        packet_id=packet_id,
        idempotency_key=idempotency_key,
        lifecycle_state=lifecycle_state,
        failed_provenance=failed_provenance,
        transition_event_count=len(events),
        latest_transition_event_id=(
            latest.transition_event_id if latest is not None else None
        ),
        execution_attempt_count=sum(
            event.transition_rule_id == "g2a_t03_pending" for event in events
        ),
        idempotency_disposition=disposition.disposition,
        reservation_owner_packet_id=(
            disposition.reservation_owner_packet_id
        ),
        latest_disposition_event_id=(
            disposition.latest_disposition_event_id
        ),
        terminal_receipt_ref=terminal_receipt_ref,
        lifecycle_terminal=lifecycle_terminal,
        eligible_for_corridor_revalidation=eligible,
        executable=False,
        registry_is_authority=False,
        registry_grants_permission=False,
        real_world_effects_count=0,
        reason_codes=(),
    )


def _derive_idempotency_disposition_unchecked_v01(
    history: tuple[IdempotencyDispositionEventV01, ...],
    idempotency_key: str,
) -> IdempotencyDispositionStateV01:
    matching = tuple(
        event for event in history if event.idempotency_key == idempotency_key
    )
    if not matching:
        return IdempotencyDispositionStateV01(
            idempotency_key=idempotency_key,
            disposition="UNCLAIMED",
            reservation_owner_packet_id=None,
            latest_disposition_event_id=None,
            event_count=0,
        )
    latest = matching[-1]
    return IdempotencyDispositionStateV01(
        idempotency_key=idempotency_key,
        disposition=latest.to_disposition,
        reservation_owner_packet_id=latest.to_owner_packet_id,
        latest_disposition_event_id=latest.idempotency_disposition_event_id,
        event_count=len(matching),
    )


def _find_lifecycle_entry_v01(
    registry: ActionCommitPacketRegistryV02,
    packet_id: object,
) -> ActionPacketLifecycleEntryV01:
    if not validate_prefixed_sha256_identity_v01(
        packet_id,
        prefix=ACTION_COMMIT_PACKET_ID_PREFIX_V01,
    )[0]:
        raise ValueError("action_packet_lifecycle_packet_id_invalid")
    matching = tuple(
        entry
        for entry in registry.action_packet_lifecycle_entries
        if entry.root_bound_genesis.packet_identity.packet_id == packet_id
    )
    if len(matching) != 1:
        raise ValueError("action_packet_lifecycle_entry_not_found")
    return matching[0]


def _validate_registry_lifecycle_histories_v01(
    registry: ActionCommitPacketRegistryV02,
) -> tuple[
    bool,
    tuple[str, ...],
    _ActionPacketRegistryValidationPassV01 | None,
]:
    reasons: list[str] = []
    entries = registry.action_packet_lifecycle_entries
    dispositions = registry.idempotency_disposition_events
    contexts = registry.action_packet_invalidation_contexts
    fulfillment_contexts = registry.action_packet_fulfillment_attempt_contexts
    if type(entries) is not tuple or any(
        type(entry) is not ActionPacketLifecycleEntryV01 for entry in entries
    ):
        return (
            False,
            ("action_packet_registry_lifecycle_entries_invalid",),
            None,
        )
    if type(dispositions) is not tuple or any(
        type(event) is not IdempotencyDispositionEventV01
        for event in dispositions
    ):
        return (
            False,
            ("action_packet_registry_disposition_events_invalid",),
            None,
        )
    if type(contexts) is not tuple or any(
        type(context) is not _ActionPacketInvalidationContextV01
        for context in contexts
    ):
        return (
            False,
            ("action_packet_registry_invalidation_contexts_invalid",),
            None,
        )
    if type(fulfillment_contexts) is not tuple or any(
        type(context) is not _ActionPacketFulfillmentAttemptContextV01
        for context in fulfillment_contexts
    ):
        return (
            False,
            ("action_packet_registry_fulfillment_contexts_invalid",),
            None,
        )
    transition_registry = build_action_packet_transition_registry_profile_v01()
    packet_ids: list[str] = []
    transition_by_id: dict[str, ActionPacketTransitionEventV01] = {}
    entry_by_packet: dict[str, ActionPacketLifecycleEntryV01] = {}
    for entry in entries:
        packet_id = entry.root_bound_genesis.packet_identity.packet_id
        if packet_id in packet_ids:
            _reason_v01(reasons, "action_packet_registry_duplicate_genesis")
        packet_ids.append(packet_id)
        entry_by_packet[packet_id] = entry
    entries_by_key: dict[str, list[ActionPacketLifecycleEntryV01]] = {}
    for entry in entries:
        key = (
            entry.root_bound_genesis.canonical_projection
            .idempotency_identity.idempotency_key
        )
        entries_by_key.setdefault(key, []).append(entry)
    validation_pass = _ActionPacketRegistryValidationPassV01(registry)
    for same_key_entries in (
        validation_pass.entries_by_idempotency_key.values()
    ):
        if len(same_key_entries) < 2:
            continue
        root_kinds = tuple(
            (
                entry,
                _same_key_lineage_root_kind_v01(
                    registry,
                    entry,
                    entry_by_packet,
                    validation_pass=validation_pass,
                ),
            )
            for entry in same_key_entries
        )
        roots = tuple(
            entry
            for entry, kind in root_kinds
            if kind in {"ORDINARY", "MATERIAL"}
        )
        if any(kind == "INVALID_ALIAS" for _, kind in root_kinds):
            _reason_v01(
                reasons,
                "logical_effect_identity_alias_forbidden",
            )
        if (
            len(roots) != 1
            or not _same_key_entries_are_bound_successors_v01(
                registry,
                roots[0],
                entry_by_packet,
                validation_pass=validation_pass,
            )
        ):
            _reason_v01(
                reasons,
                "authority_transition_requires_g2a3_binding",
            )
    for entry in entries:
        valid, _ = _validate_action_packet_lifecycle_entry_core_v01(
            entry,
            action_packet_transition_registry_profile=transition_registry,
            invalidation_contexts=contexts,
            idempotency_disposition_events=dispositions,
            lifecycle_entries=entries,
            validation_pass=validation_pass,
        )
        if not valid:
            _reason_v01(reasons, "action_packet_registry_lifecycle_entry_invalid")
            continue
        packet_id = entry.root_bound_genesis.packet_identity.packet_id
        for event in entry.transition_events:
            if event.transition_event_id in transition_by_id:
                _reason_v01(
                    reasons,
                    "action_packet_registry_duplicate_transition_event",
                )
            transition_by_id[event.transition_event_id] = event
    invalidation_ids: set[str] = set()
    accepted_binding_ids: set[str] = set()
    context_consumption_counts: dict[str, int] = {}
    context_positions_by_packet: dict[str, list[int]] = {}
    supersession_disposition_ids_in_context_order: list[str] = []
    for context in contexts:
        evidence = context.invalidation_evidence
        if type(evidence) is not ActionInvalidationEvidenceV01:
            _reason_v01(
                reasons,
                "action_packet_registry_invalidation_context_invalid",
            )
            continue
        invalidation_id = evidence.invalidation_evidence_id
        if invalidation_id in invalidation_ids:
            _reason_v01(
                reasons,
                "action_packet_registry_invalidation_context_duplicate",
            )
        invalidation_ids.add(invalidation_id)
        packet_entry = entry_by_packet.get(evidence.packet_id)
        if packet_entry is None:
            _reason_v01(
                reasons,
                "action_packet_registry_invalidation_packet_missing",
            )
            continue
        successor_entry = (
            entry_by_packet.get(context.supersession_successor_packet_id)
            if context.supersession_successor_packet_id is not None
            else None
        )
        context_valid, _ = _cached_invalidation_context_validation_v01(
            validation_pass,
            context,
            packet_entry.root_bound_genesis,
            supersession_successor=(
                successor_entry.root_bound_genesis
                if type(successor_entry) is ActionPacketLifecycleEntryV01
                else None
            ),
        )
        if not context_valid:
            _reason_v01(
                reasons,
                "action_packet_registry_invalidation_context_invalid",
            )
        accepted_id = None
        if (
            type(context.accepted_revocation_binding)
            is AcceptedRevocationBindingV01
        ):
            accepted_id = (
                context.accepted_revocation_binding
                .accepted_revocation_binding_id
            )
        elif (
            type(context.accepted_supersession_binding)
            is AcceptedSupersessionBindingV01
        ):
            accepted_id = (
                context.accepted_supersession_binding
                .accepted_supersession_binding_id
            )
        if accepted_id is not None:
            if accepted_id in accepted_binding_ids:
                _reason_v01(
                    reasons,
                    "action_packet_registry_accepted_binding_reused",
                )
            accepted_binding_ids.add(accepted_id)
        if evidence.invalidation_class == "ROOT_SUPERSESSION":
            bundle_valid, bundle_reasons, disposition = (
                _cached_registry_supersession_bundle_v01(
                    validation_pass,
                    context,
                )
            )
            if not bundle_valid or disposition is None:
                reasons.extend(bundle_reasons)
                _reason_v01(
                    reasons,
                    "action_packet_registry_invalidation_context_orphan",
                )
            else:
                consumption_id = disposition.idempotency_disposition_event_id
                supersession_disposition_ids_in_context_order.append(
                    consumption_id
                )
                context_consumption_counts[consumption_id] = (
                    context_consumption_counts.get(consumption_id, 0) + 1
                )
                supersession_transition_positions = tuple(
                    index
                    for index, transition in enumerate(
                        packet_entry.transition_events
                    )
                    if _invalidation_context_matches_transition_reference_v01(
                        context,
                        transition,
                    )
                )
                context_positions_by_packet.setdefault(
                    evidence.packet_id,
                    [],
                ).append(
                    supersession_transition_positions[0]
                    if len(supersession_transition_positions) == 1
                    else len(packet_entry.transition_events)
                )
        else:
            matching_transitions = tuple(
                (index, transition)
                for index, transition in enumerate(
                    packet_entry.transition_events
                )
                if _invalidation_context_matches_transition_reference_v01(
                    context,
                    transition,
                )
            )
            if len(matching_transitions) != 1:
                _reason_v01(
                    reasons,
                    "action_packet_registry_invalidation_context_orphan",
                )
            else:
                transition_index, transition = matching_transitions[0]
                context_consumption_counts[transition.transition_event_id] = (
                    context_consumption_counts.get(
                        transition.transition_event_id,
                        0,
                    )
                    + 1
                )
                context_positions_by_packet.setdefault(
                    evidence.packet_id,
                    [],
                ).append(transition_index)
    if any(count != 1 for count in context_consumption_counts.values()):
        _reason_v01(
            reasons,
            "action_packet_registry_invalidation_context_reused",
        )
    if any(
        positions != sorted(positions)
        for positions in context_positions_by_packet.values()
    ):
        _reason_v01(
            reasons,
            "action_packet_registry_invalidation_context_reordered",
        )
    supersession_disposition_ids = set(
        supersession_disposition_ids_in_context_order
    )
    supersession_disposition_ids_in_history_order = tuple(
        event.idempotency_disposition_event_id
        for event in dispositions
        if event.idempotency_disposition_event_id
        in supersession_disposition_ids
    )
    if (
        tuple(supersession_disposition_ids_in_context_order)
        != supersession_disposition_ids_in_history_order
    ):
        _reason_v01(
            reasons,
            "action_packet_registry_invalidation_context_reordered",
        )
    disposition_valid, _ = validate_idempotency_disposition_history_v01(
        dispositions
    )
    if not disposition_valid:
        _reason_v01(reasons, "action_packet_registry_disposition_history_invalid")
    for disposition_event in dispositions:
        owner_ids = tuple(
            packet_id
            for packet_id in (
                disposition_event.from_owner_packet_id,
                disposition_event.to_owner_packet_id,
                disposition_event.predecessor_packet_id,
                disposition_event.successor_packet_id,
            )
            if packet_id is not None
        )
        if any(packet_id not in entry_by_packet for packet_id in owner_ids):
            _reason_v01(reasons, "action_packet_registry_owner_packet_missing")
        causes = tuple(
            transition_by_id.get(event_id)
            for event_id in disposition_event.cause_transition_event_ids
        )
        if any(cause is None for cause in causes):
            _reason_v01(reasons, "action_packet_registry_cause_transition_missing")
            continue
        typed_causes = tuple(cause for cause in causes if cause is not None)
        if any(
            cause.idempotency_key != disposition_event.idempotency_key
            for cause in typed_causes
        ):
            _reason_v01(reasons, "action_packet_registry_cause_key_mismatch")
        _validate_registry_disposition_cause_bundle_v01(
            registry,
            disposition_event,
            typed_causes,
            entry_by_packet,
            reasons,
            validation_pass=validation_pass,
        )
    _validate_registry_fulfillment_attempt_histories_v01(
        registry,
        entry_by_packet=entry_by_packet,
        transition_by_id=transition_by_id,
        validation_pass=validation_pass,
        reasons=reasons,
    )
    if reasons:
        valid, result_reasons = _result_v01(reasons)
        return valid, result_reasons, validation_pass
    for entry in entries:
        state = _derive_action_packet_lifecycle_state_unchecked_v01(
            entry,
            dispositions,
        )
        _validate_registry_state_disposition_coherence_v01(
            entry,
            state,
            dispositions,
            reasons,
        )
    valid, result_reasons = _result_v01(reasons)
    return valid, result_reasons, validation_pass


def _is_initial_authorization_lifecycle_entry_v01(value: object) -> bool:
    if type(value) is not ActionPacketLifecycleEntryV01:
        return False
    candidate = (
        value.root_bound_genesis.canonical_projection.authorization_candidate
    )
    return (
        type(candidate) is RootBoundPacketAuthorizationCandidateV01
        and candidate.predecessor_packet_id is None
        and candidate.supersession_reason_class is None
    )


def _same_key_lineage_root_kind_v01(
    registry: ActionCommitPacketRegistryV02,
    value: ActionPacketLifecycleEntryV01,
    entries: dict[str, ActionPacketLifecycleEntryV01],
    *,
    validation_pass: _ActionPacketRegistryValidationPassV01 | None = None,
) -> str | None:
    if _is_initial_authorization_lifecycle_entry_v01(value):
        return "ORDINARY"
    projection = value.root_bound_genesis.canonical_projection
    authorization = projection.authorization_candidate
    predecessor_id = authorization.predecessor_packet_id
    predecessor = entries.get(predecessor_id)
    if not (
        type(predecessor_id) is str
        and predecessor_id
        and type(authorization.supersession_reason_class) is str
        and authorization.supersession_reason_class
        and authorization.supersession_reason_class != "RENEWAL"
        and type(predecessor) is ActionPacketLifecycleEntryV01
    ):
        return None
    predecessor_projection = (
        predecessor.root_bound_genesis.canonical_projection
    )
    same_key = (
        predecessor_projection.idempotency_identity.idempotency_key
        == projection.idempotency_identity.idempotency_key
    )
    same_intent = (
        predecessor_projection.logical_intent.root_owned_intent_id
        == projection.logical_intent.root_owned_intent_id
    )
    if same_key != same_intent:
        return "INVALID_ALIAS"
    if (
        same_key
        or predecessor_projection.owning_local_root_id
        != projection.owning_local_root_id
        or predecessor_projection.transaction_id != projection.transaction_id
    ):
        return None
    if (
        value.transition_events
        and value.transition_events[0].transition_rule_id
        == "g2a_t01_activate_root_authorization"
    ):
        matching_contexts = tuple(
            context
            for context in registry.action_packet_invalidation_contexts
            if (
                context.invalidation_evidence.invalidation_class
                == "ROOT_SUPERSESSION"
                and context.invalidation_evidence.packet_id == predecessor_id
                and context.supersession_successor_packet_id
                == value.root_bound_genesis.packet_identity.packet_id
                and (
                    _cached_registry_supersession_bundle_v01(
                        validation_pass,
                        context,
                    )[0]
                    if validation_pass is not None
                    else _validate_registry_supersession_bundle_v01(
                        registry,
                        context,
                    )[0]
                )
            )
        )
        if len(matching_contexts) != 1:
            return None
    return "MATERIAL"


def _same_key_entries_are_bound_successors_v01(
    registry: ActionCommitPacketRegistryV02,
    owner_entry: ActionPacketLifecycleEntryV01,
    entries: dict[str, ActionPacketLifecycleEntryV01],
    *,
    validation_pass: _ActionPacketRegistryValidationPassV01 | None = None,
) -> bool:
    owner_key = (
        owner_entry.root_bound_genesis.canonical_projection
        .idempotency_identity.idempotency_key
    )
    same_key_entries = tuple(
        entry
        for entry in entries.values()
        if (
            entry.root_bound_genesis.canonical_projection
            .idempotency_identity.idempotency_key
            == owner_key
        )
    )
    if owner_entry not in same_key_entries:
        return False
    entry_by_id: dict[str, ActionPacketLifecycleEntryV01] = {}
    for entry in same_key_entries:
        genesis_valid, _ = (
            _cached_root_bound_validation_v01(
                validation_pass,
                entry.root_bound_genesis,
            )
            if validation_pass is not None
            else validate_supplier_root_bound_action_commit_packet_v02_projection_v01(
                entry.root_bound_genesis
            )
        )
        packet_id = entry.root_bound_genesis.packet_identity.packet_id
        if (
            not genesis_valid
            or type(packet_id) is not str
            or packet_id in entry_by_id
        ):
            return False
        entry_by_id[packet_id] = entry
    roots = tuple(
        entry
        for entry in same_key_entries
        if _same_key_lineage_root_kind_v01(
            registry,
            entry,
            entries,
            validation_pass=validation_pass,
        )
        in {"ORDINARY", "MATERIAL"}
    )
    if len(roots) != 1 or roots[0] is not owner_entry:
        return False
    root_projection = owner_entry.root_bound_genesis.canonical_projection
    root_intent_id = root_projection.logical_intent.root_owned_intent_id
    for entry in same_key_entries:
        projection = entry.root_bound_genesis.canonical_projection
        if (
            projection.idempotency_identity.idempotency_key != owner_key
            or projection.logical_intent.root_owned_intent_id != root_intent_id
        ):
            return False
        if entry is owner_entry:
            continue
        authorization = (
            projection.authorization_candidate
        )
        predecessor_id = authorization.predecessor_packet_id
        predecessor = entry_by_id.get(predecessor_id)
        if not (
            type(predecessor_id) is str
            and predecessor_id
            and predecessor_id
            != entry.root_bound_genesis.packet_identity.packet_id
            and type(predecessor) is ActionPacketLifecycleEntryV01
            and type(authorization.supersession_reason_class) is str
            and authorization.supersession_reason_class
        ):
            return False
        predecessor_projection = (
            predecessor.root_bound_genesis.canonical_projection
        )
        if not (
            predecessor_projection.idempotency_identity.idempotency_key
            == owner_key
            and predecessor_projection.logical_intent.root_owned_intent_id
            == root_intent_id
            and predecessor_projection.owning_local_root_id
            == projection.owning_local_root_id
            and predecessor_projection.transaction_id
            == projection.transaction_id
        ):
            return False
        visited = {
            entry.root_bound_genesis.packet_identity.packet_id,
        }
        current = predecessor
        while current is not owner_entry:
            current_id = current.root_bound_genesis.packet_identity.packet_id
            if current_id in visited:
                return False
            visited.add(current_id)
            current_authorization = (
                current.root_bound_genesis.canonical_projection
                .authorization_candidate
            )
            current_predecessor_id = (
                current_authorization.predecessor_packet_id
            )
            if (
                type(current_predecessor_id) is not str
                or not current_predecessor_id
                or type(entry_by_id.get(current_predecessor_id))
                is not ActionPacketLifecycleEntryV01
            ):
                return False
            current = entry_by_id[current_predecessor_id]
        if (
            entry.transition_events
            and entry.transition_events[0].transition_rule_id
            == "g2a_t01_activate_root_authorization"
        ):
            matching_contexts = tuple(
                context
                for context in registry.action_packet_invalidation_contexts
                if (
                    context.invalidation_evidence.invalidation_class
                    == "ROOT_SUPERSESSION"
                    and context.invalidation_evidence.packet_id
                    == predecessor_id
                    and context.supersession_successor_packet_id
                    == entry.root_bound_genesis.packet_identity.packet_id
                    and (
                        _cached_registry_supersession_bundle_v01(
                            validation_pass,
                            context,
                        )[0]
                        if validation_pass is not None
                        else _validate_registry_supersession_bundle_v01(
                            registry,
                            context,
                        )[0]
                    )
                )
            )
            if len(matching_contexts) != 1:
                return False
    return True


def _validate_registry_disposition_cause_bundle_v01(
    registry: ActionCommitPacketRegistryV02,
    event: IdempotencyDispositionEventV01,
    causes: tuple[ActionPacketTransitionEventV01, ...],
    entries: dict[str, ActionPacketLifecycleEntryV01],
    reasons: list[str],
    *,
    validation_pass: _ActionPacketRegistryValidationPassV01 | None = None,
) -> None:
    rule_ids = tuple(cause.transition_rule_id for cause in causes)
    if event.event_class == "RESERVE":
        supersession_bundle = (
            _disposition_has_valid_supersession_context_v01(
                registry,
                event,
                validation_pass=validation_pass,
            )
        )
        if event.predecessor_packet_id is None:
            owner_entry = entries.get(event.to_owner_packet_id)
            if (
                type(owner_entry) is ActionPacketLifecycleEntryV01
                and not _is_initial_authorization_lifecycle_entry_v01(
                    owner_entry
                )
                and not supersession_bundle
            ):
                _reason_v01(
                    reasons,
                    "authority_transition_requires_g2a3_binding",
                )
            same_key_entry_count = sum(
                (
                    entry.root_bound_genesis.canonical_projection
                    .idempotency_identity.idempotency_key
                    == event.idempotency_key
                )
                for entry in entries.values()
            )
            if (
                same_key_entry_count != 1
                and not supersession_bundle
                and not (
                    type(owner_entry) is ActionPacketLifecycleEntryV01
                    and _is_initial_authorization_lifecycle_entry_v01(
                        owner_entry
                    )
                    and _same_key_entries_are_bound_successors_v01(
                        registry,
                        owner_entry,
                        entries,
                        validation_pass=validation_pass,
                    )
                )
            ):
                _reason_v01(
                    reasons,
                    "authority_transition_requires_g2a3_binding",
                )
            if (
                rule_ids != ("g2a_t01_activate_root_authorization",)
                or causes[0].packet_id != event.to_owner_packet_id
                or causes[0].root_decision_ref != event.root_decision_ref
                or not _disposition_context_matches_transition_v01(
                    event,
                    causes[0],
                )
                or event.evidence_refs
                != _binding_ids_for_codes_v01(
                    causes[0],
                    (
                        "packet_genesis_valid",
                        "source_root_authorization_valid",
                        "idempotency_acquisition_valid",
                    ),
                )
            ):
                _reason_v01(reasons, "atomic_activation_reserve_invalid")
            return
        if (
            rule_ids
            != (
                "g2a_t11_created_expire",
                "g2a_t01_activate_root_authorization",
            )
            or causes[0].packet_id != event.predecessor_packet_id
            or causes[1].packet_id != event.successor_packet_id
            or event.to_owner_packet_id != event.successor_packet_id
            or causes[1].root_decision_ref != event.root_decision_ref
            or not _same_logical_effect_entries_v01(
                entries.get(event.predecessor_packet_id),
                entries.get(event.successor_packet_id),
            )
            or not _disposition_context_matches_transition_v01(
                event,
                causes[1],
            )
        ):
            _reason_v01(reasons, "unclaimed_predecessor_transfer_forbidden")
        if not supersession_bundle:
            _reason_v01(
                reasons,
                "authority_transition_requires_g2a3_binding",
            )
        return
    if event.event_class in {
        "TRANSFER_RENEWAL",
        "TRANSFER_SUPERSESSION",
    }:
        if not _disposition_has_valid_supersession_context_v01(
            registry,
            event,
            validation_pass=validation_pass,
        ):
            _reason_v01(
                reasons,
                "authority_transition_requires_g2a3_binding",
            )
        return
    if event.event_class == "CONSUME":
        expected_codes = (
            "effect_consumption_evidence_valid",
            "mock_adapter_result_valid",
        )
        expected_rule = "g2a_t04_fulfill_mock"
    elif event.event_class == "UNCERTAIN_CLOSE":
        expected_codes = (
            "adapter_invocation_evidence_valid",
            "effect_outcome_unresolved",
        )
        expected_rule = "g2a_t26_uncertain_adapter_outcome"
    elif event.event_class == "RECEIPT_CONFIRM":
        expected_codes = (
            "fulfillment_consumption_evidence_valid",
            "terminal_receipt_valid",
        )
        expected_rule = "g2a_t05_receipt"
    else:
        return
    if (
        rule_ids != (expected_rule,)
        or causes[0].packet_id != event.to_owner_packet_id
        or not _disposition_context_matches_transition_v01(event, causes[0])
        or event.evidence_refs
        != _binding_ids_for_codes_v01(causes[0], expected_codes)
    ):
        _reason_v01(reasons, "atomic_outcome_disposition_invalid")


def _binding_ids_for_codes_v01(
    event: ActionPacketTransitionEventV01,
    codes: tuple[str, ...],
) -> tuple[str, ...]:
    selected = tuple(
        binding.transition_evidence_binding_id
        for binding in event.transition_evidence_bindings
        if binding.evidence_code in codes
    )
    return tuple(sorted(selected, key=lambda item: item.encode("utf-8")))


def _disposition_context_matches_transition_v01(
    disposition_event: IdempotencyDispositionEventV01,
    transition_event: ActionPacketTransitionEventV01,
) -> bool:
    return (
        disposition_event.evaluation_time == transition_event.evaluation_time
        and disposition_event.evaluation_time_source
        == transition_event.evaluation_time_source
        and disposition_event.evaluation_context_id
        == transition_event.evaluation_context_id
    )


def _same_logical_effect_entries_v01(
    predecessor: ActionPacketLifecycleEntryV01 | None,
    successor: ActionPacketLifecycleEntryV01 | None,
) -> bool:
    if (
        type(predecessor) is not ActionPacketLifecycleEntryV01
        or type(successor) is not ActionPacketLifecycleEntryV01
    ):
        return False
    predecessor_projection = predecessor.root_bound_genesis.canonical_projection
    successor_projection = successor.root_bound_genesis.canonical_projection
    return (
        predecessor_projection.logical_intent.root_owned_intent_id
        == successor_projection.logical_intent.root_owned_intent_id
        and predecessor_projection.idempotency_identity.idempotency_key
        == successor_projection.idempotency_identity.idempotency_key
    )


def _logical_effect_relation_v01(
    predecessor: ActionPacketLifecycleEntryV01,
    successor: ActionPacketLifecycleEntryV01,
) -> str | None:
    predecessor_projection = predecessor.root_bound_genesis.canonical_projection
    successor_projection = successor.root_bound_genesis.canonical_projection
    intent_equal = (
        predecessor_projection.logical_intent.root_owned_intent_id
        == successor_projection.logical_intent.root_owned_intent_id
    )
    key_equal = (
        predecessor_projection.idempotency_identity.idempotency_key
        == successor_projection.idempotency_identity.idempotency_key
    )
    if intent_equal and key_equal:
        return "SAME"
    if not intent_equal and not key_equal:
        return "DIFFERENT"
    return None


def _validate_registry_supersession_bundle_v01(
    registry: ActionCommitPacketRegistryV02,
    context: _ActionPacketInvalidationContextV01,
    *,
    validation_pass: _ActionPacketRegistryValidationPassV01 | None = None,
) -> tuple[
    bool,
    tuple[str, ...],
    IdempotencyDispositionEventV01 | None,
]:
    try:
        evidence = context.invalidation_evidence
        if (
            type(evidence) is not ActionInvalidationEvidenceV01
            or evidence.invalidation_class != "ROOT_SUPERSESSION"
            or evidence.authority_effect != "ROOT_SUPERSESSION"
        ):
            return False, ("action_packet_supersession_context_invalid",), None
        if (
            type(validation_pass) is _ActionPacketRegistryValidationPassV01
            and validation_pass.registry is registry
        ):
            predecessor = _unique_lifecycle_entry_from_validation_pass_v01(
                validation_pass,
                evidence.packet_id
            )
            successor = _unique_lifecycle_entry_from_validation_pass_v01(
                validation_pass,
                context.supersession_successor_packet_id
            )
        else:
            predecessor = _find_lifecycle_entry_v01(
                registry,
                evidence.packet_id,
            )
            successor = _find_lifecycle_entry_v01(
                registry,
                context.supersession_successor_packet_id,
            )
        context_valid, _ = (
            _cached_invalidation_context_validation_v01(
                validation_pass,
                context,
                predecessor.root_bound_genesis,
                supersession_successor=successor.root_bound_genesis,
            )
            if validation_pass is not None
            else _validate_action_packet_invalidation_context_v01(
                context,
                predecessor.root_bound_genesis,
                supersession_successor=successor.root_bound_genesis,
            )
        )
        if not context_valid:
            return False, ("action_packet_supersession_context_invalid",), None
        reasons: list[str] = []
        predecessor_id = predecessor.root_bound_genesis.packet_identity.packet_id
        successor_id = successor.root_bound_genesis.packet_identity.packet_id
        predecessor_projection = (
            predecessor.root_bound_genesis.canonical_projection
        )
        successor_projection = successor.root_bound_genesis.canonical_projection
        successor_authorization = successor_projection.authorization_candidate
        candidate = context.supersession_candidate
        binding = context.accepted_supersession_binding
        if (
            predecessor_id == successor_id
            or type(candidate) is not SupersessionCandidateV01
            or type(binding) is not AcceptedSupersessionBindingV01
            or successor_authorization.predecessor_packet_id != predecessor_id
            or successor_authorization.supersession_reason_class
            != candidate.supersession_reason_class
        ):
            _reason_v01(reasons, "action_packet_supersession_relationship_invalid")
        relation = _logical_effect_relation_v01(predecessor, successor)
        if relation is None:
            _reason_v01(reasons, "logical_effect_identity_alias_forbidden")
        successor_activation = (
            successor.transition_events[0]
            if successor.transition_events
            else None
        )
        successor_source_decision = (
            successor.root_bound_genesis.root_decision_projection
            .root_decision_result.decision_id
        )
        if (
            type(successor_activation) is not ActionPacketTransitionEventV01
            or successor_activation.transition_rule_id
            != "g2a_t01_activate_root_authorization"
            or successor_activation.previous_transition_event_id is not None
            or successor_activation.packet_id != successor_id
            or successor_activation.root_decision_ref
            != successor_source_decision
            or successor_activation.evaluation_time != evidence.evaluation_time
            or successor_activation.evaluation_time_source
            != evidence.evaluation_time_source
            or successor_activation.evaluation_context_id
            != evidence.evaluation_context_id
        ):
            _reason_v01(reasons, "action_packet_successor_activation_invalid")
            return _result_v01(reasons)[0], tuple(reasons), None
        candidate_dispositions = (
            validation_pass.dispositions_by_to_owner_packet_id.get(
                successor_id,
                (),
            )
            if (
                type(validation_pass)
                is _ActionPacketRegistryValidationPassV01
                and validation_pass.registry is registry
            )
            else registry.idempotency_disposition_events
        )
        matching_dispositions = tuple(
            disposition
            for disposition in candidate_dispositions
            if disposition.to_owner_packet_id == successor_id
            and successor_activation.transition_event_id
            in disposition.cause_transition_event_ids
        )
        if len(matching_dispositions) != 1:
            _reason_v01(reasons, "action_packet_supersession_disposition_invalid")
            return _result_v01(reasons)[0], tuple(reasons), None
        disposition = matching_dispositions[0]
        disposition_index = registry.idempotency_disposition_events.index(
            disposition
        )
        preceding_dispositions = registry.idempotency_disposition_events[
            :disposition_index
        ]
        predecessor_before = _derive_idempotency_disposition_unchecked_v01(
            preceding_dispositions,
            predecessor_projection.idempotency_identity.idempotency_key,
        )
        successor_before = _derive_idempotency_disposition_unchecked_v01(
            preceding_dispositions,
            successor_projection.idempotency_identity.idempotency_key,
        )
        if not (
            disposition.root_decision_ref == successor_source_decision
            and disposition.evaluation_time == evidence.evaluation_time
            and disposition.evaluation_time_source
            == evidence.evaluation_time_source
            and disposition.evaluation_context_id
            == evidence.evaluation_context_id
        ):
            _reason_v01(
                reasons,
                "action_packet_supersession_disposition_context_invalid",
            )
        predecessor_latest = (
            predecessor.transition_events[-1]
            if predecessor.transition_events
            else None
        )
        reason_class = candidate.supersession_reason_class
        expected_transfer_class = (
            "TRANSFER_RENEWAL"
            if reason_class == "RENEWAL"
            else "TRANSFER_SUPERSESSION"
        )
        expected_causes: tuple[str, ...]
        expected_evidence_refs: tuple[str, ...]
        if relation == "SAME" and (
            type(predecessor_latest) is ActionPacketTransitionEventV01
            and predecessor_latest.transition_rule_id
            == "g2a_t11_created_expire"
        ):
            expected_causes = (
                predecessor_latest.transition_event_id,
                successor_activation.transition_event_id,
            )
            expected_evidence_refs = (
                binding.accepted_supersession_binding_id,
                predecessor_latest.transition_event_id,
                successor_source_decision,
            )
            if not (
                predecessor_latest.target_state == "EXPIRED"
                and predecessor_before.disposition == "UNCLAIMED"
                and predecessor_before.reservation_owner_packet_id is None
                and disposition.event_class == "RESERVE"
                and disposition.idempotency_key
                == successor_projection.idempotency_identity.idempotency_key
                and disposition.from_disposition == "UNCLAIMED"
                and disposition.to_disposition == "RESERVED"
                and disposition.from_owner_packet_id is None
                and disposition.to_owner_packet_id == successor_id
                and disposition.previous_disposition_event_id is None
                and disposition.predecessor_packet_id == predecessor_id
                and disposition.successor_packet_id == successor_id
            ):
                _reason_v01(
                    reasons,
                    "unclaimed_predecessor_transfer_forbidden",
                )
        elif relation == "SAME" and (
            type(predecessor_latest) is ActionPacketTransitionEventV01
            and predecessor_latest.transition_rule_id
            in {
                "g2a_t20_authorized_supersede",
                "g2a_t21_queued_supersede",
                "g2a_t22_pending_supersede",
                "g2a_t23_failed_supersede",
            }
        ):
            expected_causes = (
                predecessor_latest.transition_event_id,
                successor_activation.transition_event_id,
            )
            expected_evidence_refs = (
                binding.accepted_supersession_binding_id,
                predecessor_projection.logical_intent.root_owned_intent_id,
                successor_source_decision,
            )
            if not (
                predecessor_before.disposition == "RESERVED"
                and predecessor_before.reservation_owner_packet_id
                == predecessor_id
                and disposition.event_class == expected_transfer_class
                and disposition.idempotency_key
                == successor_projection.idempotency_identity.idempotency_key
                and disposition.from_disposition == "RESERVED"
                and disposition.to_disposition == "RESERVED"
                and disposition.from_owner_packet_id == predecessor_id
                and disposition.to_owner_packet_id == successor_id
                and disposition.previous_disposition_event_id
                == predecessor_before.latest_disposition_event_id
                and disposition.predecessor_packet_id == predecessor_id
                and disposition.successor_packet_id == successor_id
            ):
                _reason_v01(reasons, "atomic_reserved_transfer_invalid")
        elif relation == "SAME" and (
            type(predecessor_latest) is ActionPacketTransitionEventV01
            and predecessor_latest.transition_rule_id
            in {
                "g2a_t12_authorized_expire",
                "g2a_t13_queued_expire",
                "g2a_t14_pending_expire",
                "g2a_t15_failed_expire",
                "g2a_t07_authorized_block",
                "g2a_t08_queued_block",
                "g2a_t09_pending_block",
                "g2a_t10_failed_block",
                "g2a_t16_authorized_revoke",
                "g2a_t17_queued_revoke",
                "g2a_t18_pending_revoke",
                "g2a_t19_failed_revoke",
            }
        ):
            expected_causes = (
                predecessor_latest.transition_event_id,
                successor_activation.transition_event_id,
            )
            expected_evidence_refs = (
                predecessor_latest.transition_event_id,
                binding.accepted_supersession_binding_id,
                successor_source_decision,
            )
            if not (
                predecessor_before.disposition == "RESERVED"
                and predecessor_before.reservation_owner_packet_id
                == predecessor_id
                and disposition.event_class == expected_transfer_class
                and disposition.idempotency_key
                == successor_projection.idempotency_identity.idempotency_key
                and disposition.from_disposition == "RESERVED"
                and disposition.to_disposition == "RESERVED"
                and disposition.from_owner_packet_id == predecessor_id
                and disposition.to_owner_packet_id == successor_id
                and disposition.previous_disposition_event_id
                == predecessor_before.latest_disposition_event_id
                and disposition.predecessor_packet_id == predecessor_id
                and disposition.successor_packet_id == successor_id
            ):
                _reason_v01(
                    reasons,
                    "terminal_predecessor_transfer_invalid",
                )
        elif relation == "DIFFERENT":
            allowed_states = {
                "CREATED",
                "ROOT_AUTHORIZED",
                "QUEUED",
                "PENDING_FULFILLMENT",
                "EXPIRED",
                "BLOCKED",
                "REVOKED",
            }
            predecessor_state = (
                predecessor_latest.target_state
                if type(predecessor_latest) is ActionPacketTransitionEventV01
                else "CREATED"
            )
            if (
                predecessor_state == "FAILED"
                and type(predecessor_latest) is ActionPacketTransitionEventV01
                and predecessor_latest.transition_rule_id
                == "g2a_t24_nonconsuming_failure"
            ):
                predecessor_state = "FAILED_NON_CONSUMING"
            allowed_states.add("FAILED_NON_CONSUMING")
            expected_causes = (successor_activation.transition_event_id,)
            expected_evidence_refs = _binding_ids_for_codes_v01(
                successor_activation,
                (
                    "packet_genesis_valid",
                    "source_root_authorization_valid",
                    "idempotency_acquisition_valid",
                ),
            )
            if not (
                reason_class != "RENEWAL"
                and predecessor_state in allowed_states
                and successor_before.disposition == "UNCLAIMED"
                and successor_before.reservation_owner_packet_id is None
                and disposition.event_class == "RESERVE"
                and disposition.idempotency_key
                == successor_projection.idempotency_identity.idempotency_key
                and disposition.from_disposition == "UNCLAIMED"
                and disposition.to_disposition == "RESERVED"
                and disposition.from_owner_packet_id is None
                and disposition.to_owner_packet_id == successor_id
                and disposition.previous_disposition_event_id is None
                and disposition.predecessor_packet_id is None
                and disposition.successor_packet_id is None
            ):
                _reason_v01(
                    reasons,
                    "material_effect_successor_application_invalid",
                )
        else:
            _reason_v01(reasons, "action_packet_supersession_branch_invalid")
            return _result_v01(reasons)[0], tuple(reasons), disposition
        expected_evidence_refs = tuple(
            sorted(expected_evidence_refs, key=lambda item: item.encode("utf-8"))
        )
        if (
            disposition.cause_transition_event_ids != expected_causes
            or disposition.evidence_refs != expected_evidence_refs
        ):
            _reason_v01(
                reasons,
                "action_packet_supersession_disposition_evidence_invalid",
            )
        valid, result_reasons = _result_v01(reasons)
        return valid, result_reasons, disposition
    except Exception:
        return False, ("action_packet_supersession_bundle_invalid",), None


def _cached_registry_supersession_bundle_v01(
    validation_pass: _ActionPacketRegistryValidationPassV01,
    context: _ActionPacketInvalidationContextV01,
) -> tuple[
    bool,
    tuple[str, ...],
    IdempotencyDispositionEventV01 | None,
]:
    if (
        type(validation_pass) is not _ActionPacketRegistryValidationPassV01
        or validation_pass.context_by_object_id.get(id(context)) is not context
    ):
        return _validate_registry_supersession_bundle_v01(
            validation_pass.registry,
            context,
        )
    cached = validation_pass._supersession_bundle_cache.get(id(context))
    if cached is not None and cached[0] is context:
        return cached[1]
    result = _validate_registry_supersession_bundle_v01(
        validation_pass.registry,
        context,
        validation_pass=validation_pass,
    )
    validation_pass._supersession_bundle_cache[id(context)] = (
        context,
        result,
    )
    return result


def _disposition_has_valid_supersession_context_v01(
    registry: ActionCommitPacketRegistryV02,
    disposition: IdempotencyDispositionEventV01,
    *,
    validation_pass: _ActionPacketRegistryValidationPassV01 | None = None,
) -> bool:
    matching = 0
    for context in registry.action_packet_invalidation_contexts:
        if (
            type(context) is not _ActionPacketInvalidationContextV01
            or context.invalidation_evidence.invalidation_class
            != "ROOT_SUPERSESSION"
        ):
            continue
        valid, _, matched_disposition = (
            _cached_registry_supersession_bundle_v01(
                validation_pass,
                context,
            )
            if validation_pass is not None
            else _validate_registry_supersession_bundle_v01(
                registry,
                context,
            )
        )
        if (
            valid
            and type(matched_disposition) is IdempotencyDispositionEventV01
            and matched_disposition.idempotency_disposition_event_id
            == disposition.idempotency_disposition_event_id
        ):
            matching += 1
    return matching == 1


def _validate_registry_state_disposition_coherence_v01(
    entry: ActionPacketLifecycleEntryV01,
    state: ActionPacketLifecycleStateV01,
    dispositions: tuple[IdempotencyDispositionEventV01, ...],
    reasons: list[str],
) -> None:
    events = entry.transition_events
    packet_id = state.packet_id
    latest_rule = events[-1].transition_rule_id if events else None
    acquisition_events = tuple(
        event
        for event in dispositions
        if event.idempotency_key == state.idempotency_key
        and event.to_owner_packet_id == packet_id
        and event.event_class
        in {
            "RESERVE",
            "TRANSFER_RENEWAL",
            "TRANSFER_SUPERSESSION",
        }
    )
    outgoing_transfers = tuple(
        event
        for event in dispositions
        if event.idempotency_key == state.idempotency_key
        and event.from_owner_packet_id == packet_id
        and event.to_owner_packet_id != packet_id
        and event.event_class
        in {
            "TRANSFER_RENEWAL",
            "TRANSFER_SUPERSESSION",
        }
    )
    expected_reserved_rules = {
        "g2a_t01_activate_root_authorization",
        "g2a_t02_queue",
        "g2a_t03_pending",
        "g2a_t07_authorized_block",
        "g2a_t08_queued_block",
        "g2a_t09_pending_block",
        "g2a_t10_failed_block",
        "g2a_t12_authorized_expire",
        "g2a_t13_queued_expire",
        "g2a_t14_pending_expire",
        "g2a_t15_failed_expire",
        "g2a_t16_authorized_revoke",
        "g2a_t17_queued_revoke",
        "g2a_t18_pending_revoke",
        "g2a_t19_failed_revoke",
        "g2a_t24_nonconsuming_failure",
        "g2a_t25_retry",
    }
    if latest_rule in expected_reserved_rules and not (
        state.idempotency_disposition == "RESERVED"
        and (
            (
                state.reservation_owner_packet_id == packet_id
                and len(acquisition_events) == 1
            )
            or (
                state.reservation_owner_packet_id != packet_id
                and len(outgoing_transfers) == 1
            )
        )
    ):
        _reason_v01(reasons, "action_packet_registry_reservation_mismatch")
    if latest_rule in {
        "g2a_t20_authorized_supersede",
        "g2a_t21_queued_supersede",
        "g2a_t22_pending_supersede",
        "g2a_t23_failed_supersede",
    } and not (
        state.lifecycle_state == "SUPERSEDED"
        and state.idempotency_disposition == "RESERVED"
        and state.reservation_owner_packet_id != packet_id
        and len(outgoing_transfers) == 1
        and latest_rule
        in {
            transition.transition_rule_id
            for transition in events
            if transition.transition_event_id
            in outgoing_transfers[0].cause_transition_event_ids
        }
    ):
        _reason_v01(reasons, "action_packet_registry_supersession_mismatch")
    if latest_rule in {
        "g2a_t04_fulfill_mock",
        "g2a_t05_receipt",
    } and not (
        state.idempotency_disposition == "CONSUMED"
        and state.reservation_owner_packet_id == packet_id
    ):
        _reason_v01(reasons, "action_packet_registry_consumption_mismatch")
    if latest_rule == "g2a_t26_uncertain_adapter_outcome" and not (
        state.idempotency_disposition == "UNCERTAIN_CLOSED"
        and state.reservation_owner_packet_id == packet_id
    ):
        _reason_v01(reasons, "action_packet_registry_uncertain_close_mismatch")
    cause_classes = {
        "g2a_t01_activate_root_authorization": "RESERVE",
        "g2a_t04_fulfill_mock": "CONSUME",
        "g2a_t05_receipt": "RECEIPT_CONFIRM",
        "g2a_t26_uncertain_adapter_outcome": "UNCERTAIN_CLOSE",
    }
    for transition in events:
        expected_class = cause_classes.get(transition.transition_rule_id)
        matching = tuple(
            event
            for event in dispositions
            if transition.transition_event_id
            in event.cause_transition_event_ids
            and event.event_class == expected_class
        )
        if (
            transition.transition_rule_id
            == "g2a_t01_activate_root_authorization"
        ):
            matching = tuple(
                event
                for event in dispositions
                if transition.transition_event_id
                in event.cause_transition_event_ids
                and event.event_class
                in {
                    "RESERVE",
                    "TRANSFER_RENEWAL",
                    "TRANSFER_SUPERSESSION",
                }
            )
        if expected_class is not None and len(matching) != 1:
            _reason_v01(reasons, "action_packet_registry_atomic_pair_missing")
        if (
            transition.transition_rule_id
            == "g2a_t24_nonconsuming_failure"
            and any(
                transition.transition_event_id
                in event.cause_transition_event_ids
                for event in dispositions
            )
        ):
            _reason_v01(reasons, "disposition_history_changed")
    for index, transition in enumerate(events):
        if transition.transition_rule_id != "g2a_t24_nonconsuming_failure":
            continue
        disposition_before = _derive_disposition_before_transition_v01(
            entry,
            dispositions,
            transition_index=index,
        )
        if not _t24_latest_disposition_binding_is_exact_v01(
            transition,
            disposition_before,
        ):
            _reason_v01(
                reasons,
                "latest_disposition_event_binding_invalid",
            )
    if state.lifecycle_state == "RECEIPT_RECEIVED" and (
        state.terminal_receipt_ref is None
        or state.idempotency_disposition != "CONSUMED"
    ):
        _reason_v01(reasons, "action_packet_registry_receipt_state_invalid")


def _derive_disposition_before_transition_v01(
    entry: ActionPacketLifecycleEntryV01,
    dispositions: tuple[IdempotencyDispositionEventV01, ...],
    *,
    transition_index: int,
) -> IdempotencyDispositionStateV01:
    key = (
        entry.root_bound_genesis.canonical_projection.idempotency_identity
        .idempotency_key
    )
    return _derive_idempotency_disposition_unchecked_v01(
        _packet_local_disposition_history_v01(
            entry.root_bound_genesis,
            entry.transition_events[:transition_index],
            dispositions,
        ),
        key,
    )


def _t24_latest_disposition_binding_is_exact_v01(
    transition_event: object,
    disposition_state: object,
) -> bool:
    try:
        if type(disposition_state) is IdempotencyDispositionStateV01:
            disposition = disposition_state.disposition
        elif type(disposition_state) is ActionPacketLifecycleStateV01:
            disposition = disposition_state.idempotency_disposition
        else:
            return False
        if (
            type(transition_event) is not ActionPacketTransitionEventV01
            or transition_event.transition_rule_id
            != "g2a_t24_nonconsuming_failure"
            or disposition != "RESERVED"
            or disposition_state.reservation_owner_packet_id
            != transition_event.packet_id
            or type(disposition_state.latest_disposition_event_id) is not str
        ):
            return False
        latest_id = disposition_state.latest_disposition_event_id
        if not validate_prefixed_sha256_identity_v01(
            latest_id,
            prefix=IDEMPOTENCY_DISPOSITION_EVENT_PREFIX_V01,
        )[0]:
            return False
        matching = tuple(
            binding
            for binding in transition_event.transition_evidence_bindings
            if binding.evidence_code
            == "latest_disposition_event_binding_valid"
        )
        if len(matching) != 1:
            return False
        binding = matching[0]
        digest = latest_id[len(IDEMPOTENCY_DISPOSITION_EVENT_PREFIX_V01) :]
        return (
            type(binding.evidence_ref) is str
            and binding.evidence_ref == latest_id
            and type(binding.evidence_sha256) is str
            and binding.evidence_sha256 == digest
            and type(binding.validator_profile_id) is str
            and binding.validator_profile_id
            == IDEMPOTENCY_DISPOSITION_EVENT_PROFILE_ID_V01
            and type(binding.validation_status) is str
            and binding.validation_status == "PASS"
        )
    except Exception:
        return False


def record_action_packet_genesis_v01(
    registry: object,
    *,
    root_bound_genesis: object,
    action_packet_transition_registry_profile: object,
) -> ActionCommitPacketRegistryV02:
    try:
        _require_valid_action_packet_registry_v01(registry)
        transition_registry = _exact_action_packet_transition_registry_v01(
            action_packet_transition_registry_profile
        )
        genesis_valid, genesis_reasons = (
            validate_supplier_root_bound_action_commit_packet_v02_projection_v01(
                root_bound_genesis
            )
        )
        if not genesis_valid:
            raise ValueError(genesis_reasons[0])
        packet_id = root_bound_genesis.packet_identity.packet_id
        idempotency_key = (
            root_bound_genesis.canonical_projection.idempotency_identity
            .idempotency_key
        )
        if any(
            entry.root_bound_genesis.packet_identity.packet_id == packet_id
            for entry in registry.action_packet_lifecycle_entries
        ):
            raise ValueError("action_packet_registry_duplicate_genesis")
        existing_same_key = tuple(
            entry
            for entry in registry.action_packet_lifecycle_entries
            if (
                entry.root_bound_genesis.canonical_projection
                .idempotency_identity.idempotency_key
                == idempotency_key
            )
        )
        stable_intent_id = (
            root_bound_genesis.canonical_projection.logical_intent
            .root_owned_intent_id
        )
        if any(
            entry.root_bound_genesis.canonical_projection.logical_intent
            .root_owned_intent_id
            != stable_intent_id
            for entry in existing_same_key
        ):
            raise ValueError("logical_effect_identity_alias_forbidden")
        disposition = _derive_idempotency_disposition_unchecked_v01(
            registry.idempotency_disposition_events,
            idempotency_key,
        )
        if disposition.disposition == "CONSUMED":
            raise ValueError("consumed_key_permanently_closed")
        if disposition.disposition == "UNCERTAIN_CLOSED":
            raise ValueError("uncertain_key_permanently_closed")
        entry = build_action_packet_lifecycle_entry_v01(
            root_bound_genesis=root_bound_genesis,
            action_packet_transition_registry_profile=transition_registry,
        )
        proposed = _registry_with_g2a_histories_v01(
            registry,
            lifecycle_entries=registry.action_packet_lifecycle_entries + (entry,),
        )
        _require_valid_action_packet_registry_v01(proposed)
        return proposed
    except ValueError as exc:
        raise ValueError(
            _stable_exception_reason_v01(
                exc,
                fallback="action_packet_genesis_record_invalid",
            )
        ) from None
    except Exception:
        raise ValueError("action_packet_genesis_record_invalid") from None


def activate_action_packet_lifecycle_v01(
    registry: object,
    *,
    packet_id: object,
    transition_event: object,
    disposition_event: object,
    action_packet_transition_registry_profile: object,
) -> ActionCommitPacketRegistryV02:
    try:
        _require_valid_action_packet_registry_v01(registry)
        transition_registry = _exact_action_packet_transition_registry_v01(
            action_packet_transition_registry_profile
        )
        entry = _find_lifecycle_entry_v01(registry, packet_id)
        state = _derive_action_packet_lifecycle_state_unchecked_v01(
            entry,
            registry.idempotency_disposition_events,
        )
        if state.lifecycle_state != "CREATED" or entry.transition_events:
            raise ValueError("action_packet_lifecycle_activation_state_invalid")
        if (
            type(transition_event) is not ActionPacketTransitionEventV01
            or transition_event.transition_rule_id
            != "g2a_t01_activate_root_authorization"
        ):
            raise ValueError("action_packet_lifecycle_activation_event_invalid")
        if (
            type(disposition_event) is not IdempotencyDispositionEventV01
            or disposition_event.event_class != "RESERVE"
        ):
            raise ValueError("action_packet_lifecycle_activation_reserve_invalid")
        temporal_reason = _action_packet_transition_temporal_reason_v01(
            entry.root_bound_genesis,
            transition_event,
        )
        if temporal_reason is not None:
            raise ValueError(temporal_reason)
        if disposition_event.predecessor_packet_id is not None:
            raise ValueError("authority_transition_requires_g2a3_binding")
        if disposition_event.successor_packet_id is not None:
            raise ValueError("action_packet_lifecycle_activation_pair_invalid")
        if not _is_initial_authorization_lifecycle_entry_v01(entry):
            raise ValueError("authority_transition_requires_g2a3_binding")
        canonical_key = (
            entry.root_bound_genesis.canonical_projection.idempotency_identity
            .idempotency_key
        )
        same_key_entry_count = sum(
            candidate.root_bound_genesis.canonical_projection
            .idempotency_identity.idempotency_key
            == canonical_key
            for candidate in registry.action_packet_lifecycle_entries
        )
        if same_key_entry_count != 1:
            raise ValueError("authority_transition_requires_g2a3_binding")
        _validate_activation_pair_v01(
            registry,
            entry,
            transition_event,
            disposition_event,
        )
        updated_entry = ActionPacketLifecycleEntryV01(
            root_bound_genesis=entry.root_bound_genesis,
            transition_registry_id=entry.transition_registry_id,
            transition_events=(transition_event,),
        )
        proposed = _registry_replace_entry_and_dispositions_v01(
            registry,
            old_entry=entry,
            new_entry=updated_entry,
            disposition_events=(
                registry.idempotency_disposition_events
                + (disposition_event,)
            ),
        )
        _require_valid_action_packet_registry_v01(proposed)
        return proposed
    except ValueError as exc:
        raise ValueError(
            _stable_exception_reason_v01(
                exc,
                fallback="action_packet_lifecycle_activation_invalid",
            )
        ) from None
    except Exception:
        raise ValueError("action_packet_lifecycle_activation_invalid") from None


def append_action_packet_lifecycle_transition_v01(
    registry: object,
    *,
    packet_id: object,
    transition_event: object,
    action_packet_transition_registry_profile: object,
) -> ActionCommitPacketRegistryV02:
    try:
        _require_valid_action_packet_registry_v01(registry)
        _exact_action_packet_transition_registry_v01(
            action_packet_transition_registry_profile
        )
        if type(transition_event) is not ActionPacketTransitionEventV01:
            raise ValueError("action_packet_lifecycle_transition_invalid")
        blocked_rules = {
            "g2a_t01_activate_root_authorization",
            "g2a_t04_fulfill_mock",
            "g2a_t05_receipt",
            "g2a_t24_nonconsuming_failure",
            "g2a_t26_uncertain_adapter_outcome",
        }
        authority_rules = {
            "g2a_t16_authorized_revoke",
            "g2a_t17_queued_revoke",
            "g2a_t18_pending_revoke",
            "g2a_t19_failed_revoke",
            "g2a_t20_authorized_supersede",
            "g2a_t21_queued_supersede",
            "g2a_t22_pending_supersede",
            "g2a_t23_failed_supersede",
        }
        if transition_event.transition_rule_id in authority_rules:
            raise ValueError("authority_transition_requires_g2a3_binding")
        if transition_event.transition_rule_id in {
            "g2a_t06_created_block",
            "g2a_t07_authorized_block",
            "g2a_t08_queued_block",
            "g2a_t09_pending_block",
            "g2a_t10_failed_block",
        }:
            raise ValueError("invalidation_transition_requires_g2a3_binding")
        if transition_event.transition_rule_id in blocked_rules:
            raise ValueError("action_packet_transition_requires_atomic_operation")
        allowed_rules = {
            "g2a_t02_queue",
            "g2a_t03_pending",
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
            "g2a_t25_retry",
        }
        if transition_event.transition_rule_id not in allowed_rules:
            raise ValueError("action_packet_lifecycle_transition_invalid")
        entry = _find_lifecycle_entry_v01(registry, packet_id)
        temporal_reason = _action_packet_transition_temporal_reason_v01(
            entry.root_bound_genesis,
            transition_event,
        )
        if temporal_reason is not None:
            raise ValueError(temporal_reason)
        state = _derive_action_packet_lifecycle_state_unchecked_v01(
            entry,
            registry.idempotency_disposition_events,
        )
        if transition_event.transition_rule_id not in {
            "g2a_t06_created_block",
            "g2a_t11_created_expire",
        } and not (
            state.idempotency_disposition == "RESERVED"
            and state.reservation_owner_packet_id == packet_id
        ):
            raise ValueError("idempotency_reservation_invalid")
        if transition_event.transition_rule_id == "g2a_t25_retry":
            if (
                state.failed_provenance != "FAILED_NON_CONSUMING"
                or state.terminal_receipt_ref is not None
            ):
                raise ValueError("failed_provenance_invalid")
            if (
                entry.root_bound_genesis.canonical_projection.authority_policy
                .retry_policy
                != "NON_CONSUMING_RETRY"
            ):
                raise ValueError("retry_policy_invalid")
        return _append_transition_and_validate_registry_v01(
            registry,
            entry,
            transition_event,
        )
    except ValueError as exc:
        raise ValueError(
            _stable_exception_reason_v01(
                exc,
                fallback="action_packet_lifecycle_transition_invalid",
            )
        ) from None
    except Exception:
        raise ValueError("action_packet_lifecycle_transition_invalid") from None


def record_action_packet_consumed_outcome_v01(
    registry: object,
    *,
    packet_id: object,
    transition_event: object,
    disposition_event: object,
    action_packet_transition_registry_profile: object,
) -> ActionCommitPacketRegistryV02:
    return _record_atomic_outcome_v01(
        registry,
        packet_id=packet_id,
        transition_event=transition_event,
        disposition_event=disposition_event,
        action_packet_transition_registry_profile=(
            action_packet_transition_registry_profile
        ),
        required_source_state="PENDING_FULFILLMENT",
        transition_rule_id="g2a_t04_fulfill_mock",
        disposition_event_class="CONSUME",
        failure_reason="action_packet_consumed_outcome_invalid",
    )


def record_action_packet_nonconsuming_outcome_v01(
    registry: object,
    *,
    packet_id: object,
    transition_event: object,
    action_packet_transition_registry_profile: object,
) -> ActionCommitPacketRegistryV02:
    try:
        _require_valid_action_packet_registry_v01(registry)
        _exact_action_packet_transition_registry_v01(
            action_packet_transition_registry_profile
        )
        entry = _find_lifecycle_entry_v01(registry, packet_id)
        state = _derive_action_packet_lifecycle_state_unchecked_v01(
            entry,
            registry.idempotency_disposition_events,
        )
        if not (
            state.lifecycle_state == "PENDING_FULFILLMENT"
            and state.idempotency_disposition == "RESERVED"
            and state.reservation_owner_packet_id == packet_id
            and type(transition_event) is ActionPacketTransitionEventV01
            and transition_event.transition_rule_id
            == "g2a_t24_nonconsuming_failure"
        ):
            raise ValueError("action_packet_nonconsuming_outcome_invalid")
        _require_live_attempt_context_continuity_v01(entry, transition_event)
        if not _t24_latest_disposition_binding_is_exact_v01(
            transition_event,
            state,
        ):
            raise ValueError("latest_disposition_event_binding_invalid")
        before_history = registry.idempotency_disposition_events
        before_bytes = _disposition_history_bytes_v01(before_history)
        before_latest = state.latest_disposition_event_id
        proposed = _append_transition_and_validate_registry_v01(
            registry,
            entry,
            transition_event,
        )
        after_state = _derive_action_packet_lifecycle_state_unchecked_v01(
            _find_lifecycle_entry_v01(proposed, packet_id),
            proposed.idempotency_disposition_events,
        )
        if (
            proposed.idempotency_disposition_events is not before_history
            or proposed.idempotency_disposition_events != before_history
            or _disposition_history_bytes_v01(
                proposed.idempotency_disposition_events
            )
            != before_bytes
            or after_state.latest_disposition_event_id != before_latest
            or after_state.idempotency_disposition != "RESERVED"
            or after_state.reservation_owner_packet_id != packet_id
        ):
            raise ValueError("disposition_history_changed")
        return proposed
    except ValueError as exc:
        raise ValueError(
            _stable_exception_reason_v01(
                exc,
                fallback="action_packet_nonconsuming_outcome_invalid",
            )
        ) from None
    except Exception:
        raise ValueError("action_packet_nonconsuming_outcome_invalid") from None


def record_action_packet_uncertain_outcome_v01(
    registry: object,
    *,
    packet_id: object,
    transition_event: object,
    disposition_event: object,
    action_packet_transition_registry_profile: object,
) -> ActionCommitPacketRegistryV02:
    return _record_atomic_outcome_v01(
        registry,
        packet_id=packet_id,
        transition_event=transition_event,
        disposition_event=disposition_event,
        action_packet_transition_registry_profile=(
            action_packet_transition_registry_profile
        ),
        required_source_state="PENDING_FULFILLMENT",
        transition_rule_id="g2a_t26_uncertain_adapter_outcome",
        disposition_event_class="UNCERTAIN_CLOSE",
        failure_reason="action_packet_uncertain_outcome_invalid",
    )


def record_action_packet_receipt_confirmation_v01(
    registry: object,
    *,
    packet_id: object,
    transition_event: object,
    disposition_event: object,
    action_packet_transition_registry_profile: object,
) -> ActionCommitPacketRegistryV02:
    return _record_atomic_outcome_v01(
        registry,
        packet_id=packet_id,
        transition_event=transition_event,
        disposition_event=disposition_event,
        action_packet_transition_registry_profile=(
            action_packet_transition_registry_profile
        ),
        required_source_state="FULFILLED_MOCK",
        transition_rule_id="g2a_t05_receipt",
        disposition_event_class="RECEIPT_CONFIRM",
        failure_reason="action_packet_receipt_confirmation_invalid",
    )


def record_action_packet_deterministic_invalidation_v01(
    registry: object,
    *,
    packet_id: object,
    invalidation_evidence: object,
    transition_event: object,
    action_packet_transition_registry_profile: object,
) -> ActionCommitPacketRegistryV02:
    try:
        _require_valid_action_packet_registry_v01(registry)
        _exact_action_packet_transition_registry_v01(
            action_packet_transition_registry_profile
        )
        entry = _find_lifecycle_entry_v01(registry, packet_id)
        state = _derive_action_packet_lifecycle_state_unchecked_v01(
            entry,
            registry.idempotency_disposition_events,
        )
        context = _ActionPacketInvalidationContextV01(
            invalidation_evidence=invalidation_evidence,
            revocation_candidate=None,
            revocation_root_projection=None,
            accepted_revocation_binding=None,
            supersession_candidate=None,
            supersession_root_projection=None,
            supersession_successor_packet_id=None,
            accepted_supersession_binding=None,
        )
        context_valid, context_reasons = (
            _validate_action_packet_invalidation_context_v01(
                context,
                entry.root_bound_genesis,
            )
        )
        if not context_valid:
            raise ValueError(context_reasons[0])
        expected_rule = {
            "CREATED": "g2a_t06_created_block",
            "ROOT_AUTHORIZED": "g2a_t07_authorized_block",
            "QUEUED": "g2a_t08_queued_block",
            "PENDING_FULFILLMENT": "g2a_t09_pending_block",
            "FAILED": "g2a_t10_failed_block",
        }.get(state.lifecycle_state)
        if (
            expected_rule is None
            or type(transition_event) is not ActionPacketTransitionEventV01
            or transition_event.transition_rule_id != expected_rule
            or (
                expected_rule == "g2a_t10_failed_block"
                and state.failed_provenance != "FAILED_NON_CONSUMING"
            )
        ):
            raise ValueError("action_packet_deterministic_invalidation_invalid")
        if expected_rule == "g2a_t06_created_block":
            if not (
                state.idempotency_disposition == "UNCLAIMED"
                and state.reservation_owner_packet_id is None
            ):
                raise ValueError("idempotency_reservation_invalid")
        elif not (
            state.idempotency_disposition == "RESERVED"
            and state.reservation_owner_packet_id == packet_id
        ):
            raise ValueError("idempotency_reservation_invalid")
        transition_valid, transition_reasons = (
            _validate_contextual_invalidation_transition_v01(
                context,
                transition_event,
                root_bound_genesis=entry.root_bound_genesis,
                preceding_events=entry.transition_events,
                disposition_events=registry.idempotency_disposition_events,
            )
        )
        if not transition_valid:
            raise ValueError(transition_reasons[0])
        proposed = _append_invalidation_context_and_transition_v01(
            registry,
            entry=entry,
            context=context,
            transition_event=transition_event,
        )
        after_state = _derive_action_packet_lifecycle_state_unchecked_v01(
            _find_lifecycle_entry_v01(proposed, packet_id),
            proposed.idempotency_disposition_events,
        )
        if (
            after_state.lifecycle_state != "BLOCKED"
            or proposed.idempotency_disposition_events
            is not registry.idempotency_disposition_events
            or after_state.idempotency_disposition
            != state.idempotency_disposition
            or after_state.reservation_owner_packet_id
            != state.reservation_owner_packet_id
        ):
            raise ValueError("action_packet_deterministic_invalidation_invalid")
        return proposed
    except ValueError as exc:
        raise ValueError(
            _stable_exception_reason_v01(
                exc,
                fallback="action_packet_deterministic_invalidation_invalid",
            )
        ) from None
    except Exception:
        raise ValueError(
            "action_packet_deterministic_invalidation_invalid"
        ) from None


def record_action_packet_revocation_v01(
    registry: object,
    *,
    packet_id: object,
    revocation_candidate: object,
    revocation_root_projection: object,
    accepted_revocation_binding: object,
    invalidation_evidence: object,
    transition_event: object,
    action_packet_transition_registry_profile: object,
) -> ActionCommitPacketRegistryV02:
    try:
        _require_valid_action_packet_registry_v01(registry)
        _exact_action_packet_transition_registry_v01(
            action_packet_transition_registry_profile
        )
        entry = _find_lifecycle_entry_v01(registry, packet_id)
        state = _derive_action_packet_lifecycle_state_unchecked_v01(
            entry,
            registry.idempotency_disposition_events,
        )
        context = _ActionPacketInvalidationContextV01(
            invalidation_evidence=invalidation_evidence,
            revocation_candidate=revocation_candidate,
            revocation_root_projection=revocation_root_projection,
            accepted_revocation_binding=accepted_revocation_binding,
            supersession_candidate=None,
            supersession_root_projection=None,
            supersession_successor_packet_id=None,
            accepted_supersession_binding=None,
        )
        context_valid, context_reasons = (
            _validate_action_packet_invalidation_context_v01(
                context,
                entry.root_bound_genesis,
            )
        )
        if not context_valid:
            raise ValueError(context_reasons[0])
        expected_rule = {
            "ROOT_AUTHORIZED": "g2a_t16_authorized_revoke",
            "QUEUED": "g2a_t17_queued_revoke",
            "PENDING_FULFILLMENT": "g2a_t18_pending_revoke",
            "FAILED": "g2a_t19_failed_revoke",
        }.get(state.lifecycle_state)
        if (
            expected_rule is None
            or type(transition_event) is not ActionPacketTransitionEventV01
            or transition_event.transition_rule_id != expected_rule
            or (
                expected_rule == "g2a_t19_failed_revoke"
                and state.failed_provenance != "FAILED_NON_CONSUMING"
            )
        ):
            raise ValueError("action_packet_revocation_invalid")
        if not (
            state.idempotency_disposition == "RESERVED"
            and state.reservation_owner_packet_id == packet_id
            and state.terminal_receipt_ref is None
        ):
            raise ValueError("idempotency_reservation_invalid")
        transition_valid, transition_reasons = (
            _validate_contextual_invalidation_transition_v01(
                context,
                transition_event,
                root_bound_genesis=entry.root_bound_genesis,
                preceding_events=entry.transition_events,
                disposition_events=registry.idempotency_disposition_events,
            )
        )
        if not transition_valid:
            raise ValueError(transition_reasons[0])
        proposed = _append_invalidation_context_and_transition_v01(
            registry,
            entry=entry,
            context=context,
            transition_event=transition_event,
        )
        after_state = _derive_action_packet_lifecycle_state_unchecked_v01(
            _find_lifecycle_entry_v01(proposed, packet_id),
            proposed.idempotency_disposition_events,
        )
        if (
            after_state.lifecycle_state != "REVOKED"
            or proposed.idempotency_disposition_events
            is not registry.idempotency_disposition_events
            or after_state.idempotency_disposition != "RESERVED"
            or after_state.reservation_owner_packet_id != packet_id
        ):
            raise ValueError("action_packet_revocation_invalid")
        return proposed
    except ValueError as exc:
        raise ValueError(
            _stable_exception_reason_v01(
                exc,
                fallback="action_packet_revocation_invalid",
            )
        ) from None
    except Exception:
        raise ValueError("action_packet_revocation_invalid") from None


def record_action_packet_supersession_v01(
    registry: object,
    *,
    predecessor_packet_id: object,
    successor_packet_id: object,
    supersession_candidate: object,
    supersession_root_projection: object,
    accepted_supersession_binding: object,
    invalidation_evidence: object,
    successor_activation_event: object,
    disposition_event: object,
    action_packet_transition_registry_profile: object,
    predecessor_supersession_event: object = None,
) -> ActionCommitPacketRegistryV02:
    try:
        _require_valid_action_packet_registry_v01(registry)
        _exact_action_packet_transition_registry_v01(
            action_packet_transition_registry_profile
        )
        predecessor = _find_lifecycle_entry_v01(
            registry,
            predecessor_packet_id,
        )
        successor = _find_lifecycle_entry_v01(
            registry,
            successor_packet_id,
        )
        if predecessor is successor:
            raise ValueError("action_packet_supersession_identity_invalid")
        context = _ActionPacketInvalidationContextV01(
            invalidation_evidence=invalidation_evidence,
            revocation_candidate=None,
            revocation_root_projection=None,
            accepted_revocation_binding=None,
            supersession_candidate=supersession_candidate,
            supersession_root_projection=supersession_root_projection,
            supersession_successor_packet_id=successor_packet_id,
            accepted_supersession_binding=accepted_supersession_binding,
        )
        context_valid, context_reasons = (
            _validate_action_packet_invalidation_context_v01(
                context,
                predecessor.root_bound_genesis,
                supersession_successor=successor.root_bound_genesis,
            )
        )
        if not context_valid:
            raise ValueError(context_reasons[0])
        relation = _logical_effect_relation_v01(predecessor, successor)
        if relation is None:
            raise ValueError("logical_effect_identity_alias_forbidden")
        predecessor_state = _derive_action_packet_lifecycle_state_unchecked_v01(
            predecessor,
            registry.idempotency_disposition_events,
        )
        successor_state = _derive_action_packet_lifecycle_state_unchecked_v01(
            successor,
            registry.idempotency_disposition_events,
        )
        if not (
            successor_state.lifecycle_state == "CREATED"
            and successor.transition_events == ()
            and successor_state.reservation_owner_packet_id
            != successor_packet_id
            and type(successor_activation_event)
            is ActionPacketTransitionEventV01
            and successor_activation_event.transition_rule_id
            == "g2a_t01_activate_root_authorization"
            and type(disposition_event) is IdempotencyDispositionEventV01
        ):
            raise ValueError("action_packet_successor_activation_invalid")
        successor_authorization = (
            successor.root_bound_genesis.canonical_projection
            .authorization_candidate
        )
        if not (
            successor_authorization.predecessor_packet_id
            == predecessor_packet_id
            and type(supersession_candidate) is SupersessionCandidateV01
            and successor_authorization.supersession_reason_class
            == supersession_candidate.supersession_reason_class
        ):
            raise ValueError("action_packet_supersession_relationship_invalid")
        temporal_reason = _action_packet_transition_temporal_reason_v01(
            successor.root_bound_genesis,
            successor_activation_event,
        )
        if temporal_reason is not None:
            raise ValueError(temporal_reason)
        predecessor_latest = (
            predecessor.transition_events[-1]
            if predecessor.transition_events
            else None
        )
        reason_class = supersession_candidate.supersession_reason_class
        expected_transfer_class = (
            "TRANSFER_RENEWAL"
            if reason_class == "RENEWAL"
            else "TRANSFER_SUPERSESSION"
        )
        predecessor_event = predecessor_supersession_event
        if relation == "SAME":
            if predecessor_state.idempotency_disposition == "CONSUMED":
                raise ValueError("consumed_key_permanently_closed")
            if (
                predecessor_state.idempotency_disposition
                == "UNCERTAIN_CLOSED"
            ):
                raise ValueError("uncertain_key_permanently_closed")
            if (
                predecessor_state.lifecycle_state == "EXPIRED"
                and type(predecessor_latest)
                is ActionPacketTransitionEventV01
                and predecessor_latest.transition_rule_id
                == "g2a_t11_created_expire"
                and predecessor_state.reservation_owner_packet_id is None
            ):
                if (
                    predecessor_event is not None
                    or disposition_event.event_class != "RESERVE"
                ):
                    raise ValueError(
                        "unclaimed_predecessor_transfer_forbidden"
                    )
            elif predecessor_state.lifecycle_state in {
                "ROOT_AUTHORIZED",
                "QUEUED",
                "PENDING_FULFILLMENT",
                "FAILED",
            }:
                expected_rule = {
                    "ROOT_AUTHORIZED": "g2a_t20_authorized_supersede",
                    "QUEUED": "g2a_t21_queued_supersede",
                    "PENDING_FULFILLMENT": "g2a_t22_pending_supersede",
                    "FAILED": "g2a_t23_failed_supersede",
                }[predecessor_state.lifecycle_state]
                if (
                    predecessor_state.lifecycle_state == "FAILED"
                    and predecessor_state.failed_provenance
                    != "FAILED_NON_CONSUMING"
                ):
                    raise ValueError("failed_provenance_invalid")
                if not (
                    type(predecessor_event)
                    is ActionPacketTransitionEventV01
                    and predecessor_event.transition_rule_id == expected_rule
                    and disposition_event.event_class
                    == expected_transfer_class
                ):
                    raise ValueError("atomic_reserved_transfer_invalid")
            elif (
                predecessor_state.lifecycle_state
                in {"EXPIRED", "BLOCKED", "REVOKED"}
                and type(predecessor_latest)
                is ActionPacketTransitionEventV01
                and predecessor_latest.transition_rule_id
                in {
                    "g2a_t12_authorized_expire",
                    "g2a_t13_queued_expire",
                    "g2a_t14_pending_expire",
                    "g2a_t15_failed_expire",
                    "g2a_t07_authorized_block",
                    "g2a_t08_queued_block",
                    "g2a_t09_pending_block",
                    "g2a_t10_failed_block",
                    "g2a_t16_authorized_revoke",
                    "g2a_t17_queued_revoke",
                    "g2a_t18_pending_revoke",
                    "g2a_t19_failed_revoke",
                }
            ):
                if (
                    predecessor_event is not None
                    or disposition_event.event_class
                    != expected_transfer_class
                ):
                    raise ValueError("terminal_predecessor_transfer_invalid")
            else:
                raise ValueError("action_packet_supersession_branch_invalid")
            if (
                predecessor_state.lifecycle_state != "EXPIRED"
                or predecessor_latest is None
                or predecessor_latest.transition_rule_id
                != "g2a_t11_created_expire"
            ) and not (
                predecessor_state.idempotency_disposition == "RESERVED"
                and predecessor_state.reservation_owner_packet_id
                == predecessor_packet_id
                and predecessor_state.terminal_receipt_ref is None
            ):
                raise ValueError("atomic_reserved_transfer_invalid")
        else:
            allowed_material_states = {
                "CREATED",
                "ROOT_AUTHORIZED",
                "QUEUED",
                "PENDING_FULFILLMENT",
                "EXPIRED",
                "BLOCKED",
                "REVOKED",
            }
            if (
                predecessor_state.lifecycle_state == "FAILED"
                and predecessor_state.failed_provenance
                == "FAILED_NON_CONSUMING"
            ):
                allowed_material_states.add("FAILED")
            if not (
                reason_class != "RENEWAL"
                and predecessor_state.lifecycle_state
                in allowed_material_states
                and predecessor_event is None
                and disposition_event.event_class == "RESERVE"
            ):
                raise ValueError(
                    "material_effect_successor_application_invalid"
                )
        updated_predecessor = predecessor
        if predecessor_event is not None:
            updated_predecessor = ActionPacketLifecycleEntryV01(
                root_bound_genesis=predecessor.root_bound_genesis,
                transition_registry_id=predecessor.transition_registry_id,
                transition_events=(
                    predecessor.transition_events + (predecessor_event,)
                ),
            )
        updated_successor = ActionPacketLifecycleEntryV01(
            root_bound_genesis=successor.root_bound_genesis,
            transition_registry_id=successor.transition_registry_id,
            transition_events=(successor_activation_event,),
        )
        updated_entries = tuple(
            (
                updated_predecessor
                if entry is predecessor
                else updated_successor
                if entry is successor
                else entry
            )
            for entry in registry.action_packet_lifecycle_entries
        )
        proposed = _registry_with_g2a_histories_v01(
            registry,
            lifecycle_entries=updated_entries,
            disposition_events=(
                registry.idempotency_disposition_events
                + (disposition_event,)
            ),
            invalidation_contexts=(
                registry.action_packet_invalidation_contexts + (context,)
            ),
        )
        proposed_validation = _require_valid_action_packet_registry_v01(
            proposed
        )
        bundle_valid, bundle_reasons, matched_disposition = (
            _cached_registry_supersession_bundle_v01(
                proposed_validation.validation_pass,
                context,
            )
        )
        if (
            not bundle_valid
            or matched_disposition is not disposition_event
        ):
            raise ValueError(
                bundle_reasons[0]
                if bundle_reasons
                else "action_packet_supersession_bundle_invalid"
            )
        successor_after = _derive_action_packet_lifecycle_state_unchecked_v01(
            _find_lifecycle_entry_v01(proposed, successor_packet_id),
            proposed.idempotency_disposition_events,
        )
        if not (
            successor_after.lifecycle_state == "ROOT_AUTHORIZED"
            and successor_after.idempotency_disposition == "RESERVED"
            and successor_after.reservation_owner_packet_id
            == successor_packet_id
            and successor_after.executable is False
        ):
            raise ValueError("action_packet_successor_activation_invalid")
        return proposed
    except ValueError as exc:
        raise ValueError(
            _stable_exception_reason_v01(
                exc,
                fallback="action_packet_supersession_invalid",
            )
        ) from None
    except Exception:
        raise ValueError("action_packet_supersession_invalid") from None


def _append_invalidation_context_and_transition_v01(
    registry: ActionCommitPacketRegistryV02,
    *,
    entry: ActionPacketLifecycleEntryV01,
    context: _ActionPacketInvalidationContextV01,
    transition_event: ActionPacketTransitionEventV01,
) -> ActionCommitPacketRegistryV02:
    updated_entry = ActionPacketLifecycleEntryV01(
        root_bound_genesis=entry.root_bound_genesis,
        transition_registry_id=entry.transition_registry_id,
        transition_events=entry.transition_events + (transition_event,),
    )
    entries = tuple(
        updated_entry if candidate is entry else candidate
        for candidate in registry.action_packet_lifecycle_entries
    )
    if sum(
        candidate is entry
        for candidate in registry.action_packet_lifecycle_entries
    ) != 1:
        raise ValueError("action_packet_lifecycle_entry_not_found")
    proposed = _registry_with_g2a_histories_v01(
        registry,
        lifecycle_entries=entries,
        disposition_events=registry.idempotency_disposition_events,
        invalidation_contexts=(
            registry.action_packet_invalidation_contexts + (context,)
        ),
    )
    _require_valid_action_packet_registry_v01(proposed)
    return proposed


def _record_atomic_outcome_v01(
    registry: object,
    *,
    packet_id: object,
    transition_event: object,
    disposition_event: object,
    action_packet_transition_registry_profile: object,
    required_source_state: str,
    transition_rule_id: str,
    disposition_event_class: str,
    failure_reason: str,
) -> ActionCommitPacketRegistryV02:
    try:
        _require_valid_action_packet_registry_v01(registry)
        _exact_action_packet_transition_registry_v01(
            action_packet_transition_registry_profile
        )
        entry = _find_lifecycle_entry_v01(registry, packet_id)
        state = _derive_action_packet_lifecycle_state_unchecked_v01(
            entry,
            registry.idempotency_disposition_events,
        )
        required_disposition = (
            "CONSUMED"
            if transition_rule_id == "g2a_t05_receipt"
            else "RESERVED"
        )
        if not (
            state.lifecycle_state == required_source_state
            and state.idempotency_disposition == required_disposition
            and state.reservation_owner_packet_id == packet_id
            and type(transition_event) is ActionPacketTransitionEventV01
            and transition_event.transition_rule_id == transition_rule_id
            and type(disposition_event) is IdempotencyDispositionEventV01
            and disposition_event.event_class == disposition_event_class
            and disposition_event.cause_transition_event_ids
            == (transition_event.transition_event_id,)
            and disposition_event.previous_disposition_event_id
            == state.latest_disposition_event_id
        ):
            raise ValueError(failure_reason)
        _require_live_attempt_context_continuity_v01(entry, transition_event)
        updated_entry = ActionPacketLifecycleEntryV01(
            root_bound_genesis=entry.root_bound_genesis,
            transition_registry_id=entry.transition_registry_id,
            transition_events=entry.transition_events + (transition_event,),
        )
        proposed = _registry_replace_entry_and_dispositions_v01(
            registry,
            old_entry=entry,
            new_entry=updated_entry,
            disposition_events=(
                registry.idempotency_disposition_events
                + (disposition_event,)
            ),
        )
        _require_valid_action_packet_registry_v01(proposed)
        return proposed
    except ValueError as exc:
        raise ValueError(
            _stable_exception_reason_v01(exc, fallback=failure_reason)
        ) from None
    except Exception:
        raise ValueError(failure_reason) from None


def _require_live_attempt_context_continuity_v01(
    entry: ActionPacketLifecycleEntryV01,
    transition_event: ActionPacketTransitionEventV01,
) -> None:
    expected_predecessor_rule = {
        "g2a_t04_fulfill_mock": "g2a_t03_pending",
        "g2a_t24_nonconsuming_failure": "g2a_t03_pending",
        "g2a_t26_uncertain_adapter_outcome": "g2a_t03_pending",
        "g2a_t05_receipt": "g2a_t04_fulfill_mock",
    }.get(transition_event.transition_rule_id)
    if expected_predecessor_rule is None:
        return
    if not entry.transition_events:
        raise ValueError("action_packet_transition_attempt_context_mismatch")
    predecessor = entry.transition_events[-1]
    if (
        predecessor.transition_rule_id != expected_predecessor_rule
        or type(predecessor.execution_attempt_id) is not str
        or type(transition_event.execution_attempt_id) is not str
        or transition_event.execution_attempt_id
        != predecessor.execution_attempt_id
        or type(predecessor.evaluation_context_id) is not str
        or type(transition_event.evaluation_context_id) is not str
        or transition_event.evaluation_context_id
        != predecessor.evaluation_context_id
    ):
        raise ValueError("action_packet_transition_attempt_context_mismatch")


def _validate_activation_pair_v01(
    registry: ActionCommitPacketRegistryV02,
    entry: ActionPacketLifecycleEntryV01,
    transition_event: ActionPacketTransitionEventV01,
    disposition_event: IdempotencyDispositionEventV01,
) -> None:
    genesis = entry.root_bound_genesis
    packet_id = genesis.packet_identity.packet_id
    canonical = genesis.canonical_projection
    idempotency_key = canonical.idempotency_identity.idempotency_key
    source_root_id = (
        genesis.root_decision_projection.root_decision_result.decision_id
    )
    event_valid, _ = validate_action_packet_transition_event_v01(
        transition_event,
        action_packet_transition_registry_profile=(
            build_action_packet_transition_registry_profile_v01()
        ),
    )
    disposition_valid, _ = validate_idempotency_disposition_event_v01(
        disposition_event
    )
    if not event_valid or not disposition_valid:
        raise ValueError("action_packet_lifecycle_activation_pair_invalid")
    if not (
        transition_event.packet_id == packet_id
        and transition_event.idempotency_key == idempotency_key
        and transition_event.owning_local_root_id
        == canonical.owning_local_root_id
        and transition_event.dependency_set_candidate_fingerprint
        == canonical.dependency_set_candidate_fingerprint
        and transition_event.temporal_authority_fingerprint
        == canonical.temporal_authority_fingerprint
        and transition_event.previous_transition_event_id is None
        and transition_event.root_decision_ref == source_root_id
        and disposition_event.idempotency_key == idempotency_key
        and disposition_event.to_owner_packet_id == packet_id
        and disposition_event.root_decision_ref == source_root_id
        and disposition_event.cause_transition_event_ids[-1]
        == transition_event.transition_event_id
    ):
        raise ValueError("action_packet_lifecycle_activation_pair_invalid")
    current = _derive_idempotency_disposition_unchecked_v01(
        registry.idempotency_disposition_events,
        idempotency_key,
    )
    if current.disposition != "UNCLAIMED":
        raise ValueError("idempotency_acquisition_invalid")
    if disposition_event.predecessor_packet_id is None:
        if disposition_event.cause_transition_event_ids != (
            transition_event.transition_event_id,
        ):
            raise ValueError("action_packet_lifecycle_activation_pair_invalid")
        return
    predecessor = _find_lifecycle_entry_v01(
        registry,
        disposition_event.predecessor_packet_id,
    )
    predecessor_state = _derive_action_packet_lifecycle_state_unchecked_v01(
        predecessor,
        registry.idempotency_disposition_events,
    )
    if not (
        disposition_event.successor_packet_id == packet_id
        and predecessor_state.lifecycle_state == "EXPIRED"
        and predecessor.transition_events
        and predecessor.transition_events[-1].transition_rule_id
        == "g2a_t11_created_expire"
        and disposition_event.cause_transition_event_ids
        == (
            predecessor.transition_events[-1].transition_event_id,
            transition_event.transition_event_id,
        )
        and _same_logical_effect_entries_v01(predecessor, entry)
    ):
        raise ValueError("unclaimed_predecessor_transfer_forbidden")


def _append_transition_and_validate_registry_v01(
    registry: ActionCommitPacketRegistryV02,
    entry: ActionPacketLifecycleEntryV01,
    transition_event: ActionPacketTransitionEventV01,
) -> ActionCommitPacketRegistryV02:
    updated_entry = ActionPacketLifecycleEntryV01(
        root_bound_genesis=entry.root_bound_genesis,
        transition_registry_id=entry.transition_registry_id,
        transition_events=entry.transition_events + (transition_event,),
    )
    proposed = _registry_replace_entry_and_dispositions_v01(
        registry,
        old_entry=entry,
        new_entry=updated_entry,
        disposition_events=registry.idempotency_disposition_events,
    )
    _require_valid_action_packet_registry_v01(proposed)
    return proposed


def _registry_replace_entry_and_dispositions_v01(
    registry: ActionCommitPacketRegistryV02,
    *,
    old_entry: ActionPacketLifecycleEntryV01,
    new_entry: ActionPacketLifecycleEntryV01,
    disposition_events: tuple[IdempotencyDispositionEventV01, ...],
) -> ActionCommitPacketRegistryV02:
    entries = tuple(
        new_entry if entry is old_entry else entry
        for entry in registry.action_packet_lifecycle_entries
    )
    if sum(entry is old_entry for entry in registry.action_packet_lifecycle_entries) != 1:
        raise ValueError("action_packet_lifecycle_entry_not_found")
    return _registry_with_g2a_histories_v01(
        registry,
        lifecycle_entries=entries,
        disposition_events=disposition_events,
    )


def _registry_with_g2a_histories_v01(
    registry: ActionCommitPacketRegistryV02,
    *,
    lifecycle_entries: tuple[ActionPacketLifecycleEntryV01, ...] | None = None,
    disposition_events: tuple[IdempotencyDispositionEventV01, ...] | None = None,
    invalidation_contexts: tuple[
        _ActionPacketInvalidationContextV01,
        ...,
    ]
    | None = None,
    fulfillment_attempt_contexts: tuple[
        _ActionPacketFulfillmentAttemptContextV01,
        ...,
    ]
    | None = None,
    terminal_receipt_packet_ids: tuple[str, ...] | None = None,
    terminal_receipt_idempotency_keys: tuple[str, ...] | None = None,
) -> ActionCommitPacketRegistryV02:
    return ActionCommitPacketRegistryV02(
        registry_id=registry.registry_id,
        seen_packet_ids=registry.seen_packet_ids,
        used_idempotency_keys=registry.used_idempotency_keys,
        terminal_receipt_packet_ids=(
            registry.terminal_receipt_packet_ids
            if terminal_receipt_packet_ids is None
            else terminal_receipt_packet_ids
        ),
        terminal_receipt_idempotency_keys=(
            registry.terminal_receipt_idempotency_keys
            if terminal_receipt_idempotency_keys is None
            else terminal_receipt_idempotency_keys
        ),
        expired_packet_ids=registry.expired_packet_ids,
        failed_packet_ids=registry.failed_packet_ids,
        local_proof_only=registry.local_proof_only,
        production_persistence=registry.production_persistence,
        global_drs_write=registry.global_drs_write,
        external_drs_write=registry.external_drs_write,
        creates_permission=registry.creates_permission,
        creates_receipt=registry.creates_receipt,
        executes_payment=registry.executes_payment,
        releases_shipment=registry.releases_shipment,
        real_world_effects_count=registry.real_world_effects_count,
        action_packet_lifecycle_entries=(
            registry.action_packet_lifecycle_entries
            if lifecycle_entries is None
            else lifecycle_entries
        ),
        idempotency_disposition_events=(
            registry.idempotency_disposition_events
            if disposition_events is None
            else disposition_events
        ),
        action_packet_invalidation_contexts=(
            registry.action_packet_invalidation_contexts
            if invalidation_contexts is None
            else invalidation_contexts
        ),
        action_packet_fulfillment_attempt_contexts=(
            registry.action_packet_fulfillment_attempt_contexts
            if fulfillment_attempt_contexts is None
            else fulfillment_attempt_contexts
        ),
    )


def _require_valid_action_packet_registry_v01(
    registry: object,
) -> _ActionPacketRegistryValidationResultV02:
    result = _validate_action_commit_packet_registry_core_v02(registry)
    if not result.valid:
        raise ValueError(result.reasons[0])
    return result


def _g2a4a_current_dependency_observation_ids_v01(
    root_bound_genesis: SupplierRootBoundActionCommitPacketV02ProjectionV01,
    current_dependency_observations: object,
    *,
    eligibility_evaluation_time: object,
    eligibility_evaluation_context_id: object,
    validation_pass: _ActionPacketRegistryValidationPassV01,
) -> tuple[str, ...]:
    if type(current_dependency_observations) is not tuple:
        raise ValueError("current_dependency_observations_type_invalid")
    if not validate_signed_int64_v01(eligibility_evaluation_time)[0]:
        raise ValueError("current_dependency_evaluation_time_invalid")
    if not validate_identity_text_v01(
        eligibility_evaluation_context_id
    )[0]:
        raise ValueError("current_dependency_evaluation_context_invalid")
    root_bound_result = _cached_root_bound_validation_v01(
        validation_pass,
        root_bound_genesis,
    )
    accepted, _ = _validate_mandatory_dependency_local_root_acceptance_core_v01(
        root_bound_genesis,
        packet_validation_result=root_bound_result,
    )
    if not accepted:
        raise ValueError("current_dependency_acceptance_invalid")
    canonical = root_bound_genesis.canonical_projection
    candidate = canonical.dependency_candidate
    if not validate_dependency_set_candidate_v01(candidate)[0]:
        raise ValueError("current_dependency_candidate_invalid")
    records_by_id = {
        record.dependency_id: record
        for record in candidate.dependency_records
    }
    observations_by_id: dict[
        str,
        ActionDependencyCurrentObservationV01,
    ] = {}
    observation_ids: set[str] = set()
    for observation in current_dependency_observations:
        valid_observation, _ = (
            validate_action_dependency_current_observation_v01(observation)
        )
        if not valid_observation:
            raise ValueError("current_dependency_observation_invalid")
        if observation.observation_id in observation_ids:
            raise ValueError("current_dependency_observation_duplicate")
        observation_ids.add(observation.observation_id)
        if observation.dependency_id in observations_by_id:
            raise ValueError("current_dependency_observation_duplicate")
        if observation.dependency_id not in records_by_id:
            raise ValueError("current_dependency_observation_unknown")
        observations_by_id[observation.dependency_id] = observation
    ordered_ids: list[str] = []
    for record in candidate.dependency_records:
        observation = observations_by_id.get(record.dependency_id)
        if observation is None:
            if record.requirement_class == "MANDATORY":
                raise ValueError("current_mandatory_dependency_missing")
            continue
        if (
            type(record.time_envelope_id) is not str
            or type(record.freshness_policy_id) is not str
            or observation.dependency_id != record.dependency_id
            or observation.evidence_ref != record.evidence_ref
            or observation.observed_content_sha256 != record.content_sha256
            or observation.time_envelope_id != record.time_envelope_id
            or observation.freshness_policy_id
            != record.freshness_policy_id
            or observation.source_provenance_refs
            != record.source_provenance_refs
        ):
            raise ValueError("current_dependency_observation_mismatch")
        time_envelope_valid, _ = (
            validate_action_dependency_time_envelope_binding_v01(
                record.time_envelope_id,
                dependency_id=record.dependency_id,
                evidence_ref=record.evidence_ref,
                content_sha256=record.content_sha256,
                freshness_policy_id=record.freshness_policy_id,
                source_provenance_refs=record.source_provenance_refs,
                valid_from_utc=observation.valid_from_utc,
                valid_to_utc=observation.valid_to_utc,
            )
        )
        if not time_envelope_valid:
            raise ValueError(
                "current_dependency_time_envelope_invalid"
            )
        if (
            record.expected_accepting_local_root_id
            != canonical.owning_local_root_id
        ):
            raise ValueError("current_dependency_root_mismatch")
        if (
            not observation.valid_from_utc
            <= eligibility_evaluation_time
            < observation.valid_to_utc
            or observation.observed_at_utc > eligibility_evaluation_time
        ):
            raise ValueError("current_dependency_stale")
        if (
            observation.observation_context_id
            != eligibility_evaluation_context_id
        ):
            raise ValueError("current_dependency_context_mismatch")
        ordered_ids.append(observation.observation_id)
    return tuple(ordered_ids)


def _g2a4a_root_scope_refs_v01(
    canonical: SupplierActionCommitPacketCanonicalProjectionV01,
) -> tuple[str, ...]:
    subject = canonical.normalized_subject_scope
    target = canonical.normalized_target_scope
    root_scope_refs = (
        subject.included_subject_refs + target.included_target_refs
    )
    if (
        not root_scope_refs
        or len(root_scope_refs) != len(set(root_scope_refs))
        or any(
            type(item) is not str
            or not validate_identity_text_v01(item)[0]
            for item in root_scope_refs
        )
        or set(root_scope_refs).intersection(
            subject.excluded_subject_refs + target.excluded_target_refs
        )
    ):
        raise ValueError("action_packet_effect_scope_invalid")
    return root_scope_refs


def _g2a4a_validate_corridor_containment_v01(
    canonical: SupplierActionCommitPacketCanonicalProjectionV01,
    packet_id: str,
    corridor: object,
    corridor_step: object,
) -> tuple[str, ...]:
    if type(corridor) is not ContractFulfillmentCorridorV01:
        raise ValueError("action_packet_corridor_type_invalid")
    if type(corridor_step) is not CorridorStepV01:
        raise ValueError("action_packet_corridor_step_type_invalid")
    if (
        corridor.packet_id != packet_id
        or corridor.corridor_kind != canonical.adapter_binding.corridor_class
        or type(corridor.deterministic_only) is not bool
        or corridor.deterministic_only is not True
        or type(corridor.post_root_llm_reasoning_allowed) is not bool
        or corridor.post_root_llm_reasoning_allowed is not False
        or type(corridor.reasoning_restarted_after_root) is not bool
        or corridor.reasoning_restarted_after_root is not False
        or type(corridor.root_review_required_on_mismatch) is not bool
        or corridor.root_review_required_on_mismatch is not True
    ):
        raise ValueError("action_packet_corridor_binding_invalid")
    if (
        type(corridor.allowed_steps) is not tuple
        or not corridor.allowed_steps
        or len(corridor.allowed_steps) != len(set(corridor.allowed_steps))
        or any(
            type(step_id) is not str
            or not validate_identity_text_v01(step_id)[0]
            for step_id in corridor.allowed_steps
        )
        or corridor.allowed_steps.count(corridor_step.step_id) != 1
    ):
        raise ValueError("action_packet_corridor_step_not_authorized")
    legacy_valid, _ = validate_corridor_no_post_root_reasoning_v01(
        corridor
    )
    legacy_validation_packet = _dataclass_replace(
        canonical.source_packet,
        packet_id=packet_id,
    )
    step_report = validate_corridor_step_against_packet_v01(
        legacy_validation_packet,
        corridor_step,
    )
    if not legacy_valid or step_report.validation_status != STATUS_PASS:
        raise ValueError("action_packet_corridor_legacy_invalid")
    raw_action = canonical.selected_legacy_action
    raw_adapter = canonical.source_packet.adapter_binding.adapter_id
    if (
        corridor_step.parent_packet_id != packet_id
        or corridor_step.allowed_actions.count(raw_action) != 1
        or corridor_step.adapter_id != raw_adapter
        or raw_action not in canonical.raw_allowed_actions
        or raw_action in canonical.raw_forbidden_actions
        or raw_adapter not in canonical.raw_allowed_adapters
        or raw_adapter in canonical.raw_forbidden_adapters
    ):
        raise ValueError("action_packet_corridor_legacy_containment_invalid")
    permission = canonical.normalized_permission_scope
    policy = canonical.authority_policy
    effect_class = canonical.authorization_candidate.effect_class
    business_namespace = (
        canonical.business_object_identity.business_object_namespace
    )
    if (
        canonical.adapter_binding.adapter_id
        not in permission.allowed_adapter_ids
        or canonical.adapter_binding.adapter_id
        in permission.forbidden_adapter_ids
        or canonical.selected_canonical_action
        not in permission.allowed_action_classes
        or canonical.selected_canonical_action
        in permission.forbidden_action_classes
        or effect_class in permission.prohibited_effect_classes
        or effect_class not in policy.allowed_logical_effect_classes
        or canonical.adapter_binding.corridor_class
        not in policy.allowed_corridor_classes
        or business_namespace
        not in policy.allowed_business_object_namespaces
        or canonical.canonical_permission_ref
        not in permission.required_approval_refs
    ):
        raise ValueError("action_packet_corridor_canonical_containment_invalid")
    return _g2a4a_root_scope_refs_v01(canonical)


def _g2a4a_logical_ticks_v01(
    canonical: SupplierActionCommitPacketCanonicalProjectionV01,
    logical_time_bridge: object,
    eligibility_evaluation_time: object,
) -> tuple[int, int, int]:
    valid_bridge, bridge_reasons = validate_logical_time_bridge_v01(
        logical_time_bridge
    )
    if not valid_bridge:
        raise ValueError(bridge_reasons[0])
    issued_at_tick = epoch_seconds_to_logical_tick_v01(
        logical_time_bridge,
        canonical.temporal_authority.issued_at_utc,
    )
    expires_at_tick = epoch_seconds_to_logical_tick_v01(
        logical_time_bridge,
        canonical.temporal_authority.expires_at_utc,
    )
    current_tick = epoch_seconds_to_logical_tick_v01(
        logical_time_bridge,
        eligibility_evaluation_time,
    )
    for tick, epoch in (
        (issued_at_tick, canonical.temporal_authority.issued_at_utc),
        (expires_at_tick, canonical.temporal_authority.expires_at_utc),
        (current_tick, eligibility_evaluation_time),
    ):
        if logical_tick_to_epoch_seconds_v01(
            logical_time_bridge,
            tick,
        ) != epoch:
            raise ValueError("logical_time_bridge_round_trip_mismatch")
    if not issued_at_tick <= current_tick < expires_at_tick:
        raise ValueError("action_packet_effect_time_invalid")
    return issued_at_tick, expires_at_tick, current_tick


def _build_action_packet_effect_firewall_projection_core_v01(
    registry: ActionCommitPacketRegistryV02,
    *,
    packet_id: object,
    corridor: object,
    corridor_step: object,
    current_dependency_observations: object,
    logical_time_bridge: object,
    eligibility_evaluation_time: object,
    eligibility_evaluation_time_source: object,
    eligibility_evaluation_context_id: object,
    registry_validation_result: _ActionPacketRegistryValidationResultV02,
) -> ActionPacketEffectFirewallProjectionV01:
    validation_pass = registry_validation_result.validation_pass
    if (
        not registry_validation_result.valid
        or type(validation_pass)
        is not _ActionPacketRegistryValidationPassV01
        or validation_pass.registry is not registry
    ):
        raise ValueError("action_packet_effect_registry_invalid")
    if (
        not validate_identity_text_v01(registry.registry_id)[0]
        or not registry.registry_id.strip()
    ):
        raise ValueError("action_packet_effect_registry_id_invalid")
    if (
        type(corridor) is ContractFulfillmentCorridorV01
        and (
            not validate_identity_text_v01(corridor.corridor_id)[0]
            or not corridor.corridor_id.strip()
        )
    ):
        raise ValueError("action_packet_effect_corridor_id_invalid")
    if not validate_signed_int64_v01(eligibility_evaluation_time)[0]:
        raise ValueError("action_packet_effect_evaluation_time_invalid")
    if not validate_identity_text_v01(
        eligibility_evaluation_time_source
    )[0]:
        raise ValueError("action_packet_effect_evaluation_source_invalid")
    if not validate_identity_text_v01(
        eligibility_evaluation_context_id
    )[0]:
        raise ValueError("action_packet_effect_evaluation_context_invalid")
    entry = _unique_lifecycle_entry_from_validation_pass_v01(
        validation_pass,
        packet_id,
    )
    root_bound = entry.root_bound_genesis
    root_bound_valid, _ = _cached_root_bound_validation_v01(
        validation_pass,
        root_bound,
    )
    if not root_bound_valid:
        raise ValueError("action_packet_effect_genesis_invalid")
    canonical = root_bound.canonical_projection
    if not validate_supplier_action_commit_packet_canonical_projection_v01(
        canonical
    )[0]:
        raise ValueError("action_packet_effect_projection_invalid")
    root_projection = root_bound.root_decision_projection
    if not validate_root_decision_candidate_projection_v01(
        root_projection
    )[0]:
        raise ValueError("action_packet_effect_root_invalid")
    state = _derive_action_packet_lifecycle_state_unchecked_v01(
        entry,
        registry.idempotency_disposition_events,
    )
    latest = entry.transition_events[-1] if entry.transition_events else None
    transition_registry = build_action_packet_transition_registry_profile_v01()
    pending_rule = lookup_action_packet_transition_rule_v01(
        registry=transition_registry,
        transition_rule_id="g2a_t03_pending",
    )
    if (
        state.lifecycle_state != "PENDING_FULFILLMENT"
        or state.eligible_for_corridor_revalidation is not True
        or type(latest) is not ActionPacketTransitionEventV01
        or latest.transition_rule_id != "g2a_t03_pending"
        or latest.target_state != "PENDING_FULFILLMENT"
        or type(latest.execution_attempt_id) is not str
        or not validate_prefixed_sha256_identity_v01(
            latest.execution_attempt_id,
            prefix=EXECUTION_ATTEMPT_IDENTITY_PREFIX_V01,
        )[0]
        or latest.effect_consumption_class
        != pending_rule.effect_consumption_class
        or latest.receipt_ref is not None
        or any(
            event.execution_attempt_id == latest.execution_attempt_id
            and event.transition_rule_id
            in {
                "g2a_t04_fulfill_mock",
                "g2a_t24_nonconsuming_failure",
                "g2a_t26_uncertain_adapter_outcome",
            }
            for event in entry.transition_events
        )
    ):
        raise ValueError("action_packet_effect_pending_attempt_invalid")
    if (
        state.idempotency_disposition != "RESERVED"
        or state.reservation_owner_packet_id != packet_id
        or type(state.latest_disposition_event_id) is not str
        or not validate_prefixed_sha256_identity_v01(
            state.latest_disposition_event_id,
            prefix=IDEMPOTENCY_DISPOSITION_EVENT_PREFIX_V01,
        )[0]
        or state.terminal_receipt_ref is not None
        or packet_id in registry.terminal_receipt_packet_ids
        or state.idempotency_key
        in registry.terminal_receipt_idempotency_keys
    ):
        raise ValueError("action_packet_effect_reservation_invalid")
    temporal = evaluate_temporal_authority_v01(
        canonical.temporal_authority,
        evaluation_time=eligibility_evaluation_time,
    )
    if (
        temporal.outcome != TEMPORAL_OUTCOME_VALID_V01
        or type(temporal.executable) is not bool
        or temporal.executable is not True
    ):
        raise ValueError("action_packet_effect_temporal_invalid")
    dependency_observation_ids = (
        _g2a4a_current_dependency_observation_ids_v01(
            root_bound,
            current_dependency_observations,
            eligibility_evaluation_time=eligibility_evaluation_time,
            eligibility_evaluation_context_id=(
                eligibility_evaluation_context_id
            ),
            validation_pass=validation_pass,
        )
    )
    root_scope_refs = _g2a4a_validate_corridor_containment_v01(
        canonical,
        root_bound.packet_identity.packet_id,
        corridor,
        corridor_step,
    )
    issued_at_tick, expires_at_tick, current_tick = (
        _g2a4a_logical_ticks_v01(
            canonical,
            logical_time_bridge,
            eligibility_evaluation_time,
        )
    )
    root_result = root_projection.root_decision_result
    projection = ActionPacketEffectFirewallProjectionV01(
        projection_profile_id=(
            ACTION_PACKET_EFFECT_FIREWALL_PROJECTION_PROFILE_ID_V01
        ),
        packet_id=root_bound.packet_identity.packet_id,
        registry_id=registry.registry_id,
        pending_transition_event_id=latest.transition_event_id,
        execution_attempt_id=latest.execution_attempt_id,
        corridor_id=corridor.corridor_id,
        corridor_step_id=corridor_step.step_id,
        corridor_class=canonical.adapter_binding.corridor_class,
        transaction_id=canonical.transaction_id,
        target_root_id=canonical.owning_local_root_id,
        root_decision_id=root_result.decision_id,
        selected_candidate_id=(
            canonical.authorization_candidate
            .root_packet_authorization_candidate_id
        ),
        permission_ref=canonical.canonical_permission_ref,
        allowed_adapter_ids=(
            canonical.normalized_permission_scope.allowed_adapter_ids
        ),
        allowed_action_kinds=(
            canonical.normalized_permission_scope.allowed_action_classes
        ),
        root_scope_refs=root_scope_refs,
        maximum_expires_at_tick=expires_at_tick,
        request_kind="ActionCommitPacket",
        adapter_id=canonical.adapter_binding.adapter_id,
        action_kind=canonical.selected_canonical_action,
        scope_refs=root_scope_refs,
        issued_at_tick=issued_at_tick,
        expires_at_tick=expires_at_tick,
        current_tick=current_tick,
        idempotency_key=(
            canonical.idempotency_identity.idempotency_key
        ),
        mock_only=True,
        effect_access_owner=_EFFECT_ACCESS_OWNER,
        logical_time_bridge_id=logical_time_bridge.bridge_id,
        attempt_evaluation_time=latest.evaluation_time,
        attempt_evaluation_time_source=latest.evaluation_time_source,
        attempt_evaluation_context_id=latest.evaluation_context_id,
        eligibility_evaluation_time=eligibility_evaluation_time,
        eligibility_evaluation_time_source=(
            eligibility_evaluation_time_source
        ),
        eligibility_evaluation_context_id=(
            eligibility_evaluation_context_id
        ),
        latest_disposition_event_id=state.latest_disposition_event_id,
        dependency_acceptance_binding_id=(
            root_bound.dependency_acceptance_binding
            .packet_dependency_acceptance_binding_id
        ),
        dependency_observation_ids=dependency_observation_ids,
        authority_policy_fingerprint=(
            canonical.authority_policy_fingerprint
        ),
        temporal_authority_fingerprint=(
            canonical.temporal_authority_fingerprint
        ),
    )
    if not _action_packet_effect_projection_exact_types_v01(projection):
        raise ValueError("action_packet_effect_projection_shape_invalid")
    return projection


def _build_action_packet_effect_projection_from_historical_view_v01(
    *,
    registry_id: str,
    entry: ActionPacketLifecycleEntryV01,
    disposition_history: tuple[IdempotencyDispositionEventV01, ...],
    terminal_receipt_packet_ids: tuple[str, ...],
    terminal_receipt_idempotency_keys: tuple[str, ...],
    packet_id: object,
    corridor: object,
    corridor_step: object,
    current_dependency_observations: object,
    logical_time_bridge: object,
    eligibility_evaluation_time: object,
    eligibility_evaluation_time_source: object,
    eligibility_evaluation_context_id: object,
    validation_pass: _ActionPacketRegistryValidationPassV01,
) -> ActionPacketEffectFirewallProjectionV01:
    if (
        not validate_identity_text_v01(registry_id)[0]
        or not registry_id.strip()
    ):
        raise ValueError("action_packet_effect_registry_id_invalid")
    if (
        type(corridor) is ContractFulfillmentCorridorV01
        and (
            not validate_identity_text_v01(corridor.corridor_id)[0]
            or not corridor.corridor_id.strip()
        )
    ):
        raise ValueError("action_packet_effect_corridor_id_invalid")
    if (
        type(entry) is not ActionPacketLifecycleEntryV01
        or type(disposition_history) is not tuple
        or type(terminal_receipt_packet_ids) is not tuple
        or type(terminal_receipt_idempotency_keys) is not tuple
        or not validate_signed_int64_v01(
            eligibility_evaluation_time
        )[0]
        or not validate_identity_text_v01(
            eligibility_evaluation_time_source
        )[0]
        or not validate_identity_text_v01(
            eligibility_evaluation_context_id
        )[0]
    ):
        raise ValueError("action_packet_effect_historical_view_invalid")
    root_bound = entry.root_bound_genesis
    root_bound_valid, _ = _cached_root_bound_validation_v01(
        validation_pass,
        root_bound,
    )
    if not root_bound_valid:
        raise ValueError("action_packet_effect_genesis_invalid")
    if root_bound.packet_identity.packet_id != packet_id:
        raise ValueError("action_packet_effect_packet_mismatch")
    canonical = root_bound.canonical_projection
    if not validate_supplier_action_commit_packet_canonical_projection_v01(
        canonical
    )[0]:
        raise ValueError("action_packet_effect_projection_invalid")
    root_projection = root_bound.root_decision_projection
    if not validate_root_decision_candidate_projection_v01(
        root_projection
    )[0]:
        raise ValueError("action_packet_effect_root_invalid")
    state = _derive_action_packet_lifecycle_state_unchecked_v01(
        entry,
        disposition_history,
    )
    latest = entry.transition_events[-1] if entry.transition_events else None
    transition_registry = build_action_packet_transition_registry_profile_v01()
    pending_rule = lookup_action_packet_transition_rule_v01(
        registry=transition_registry,
        transition_rule_id="g2a_t03_pending",
    )
    if (
        state.lifecycle_state != "PENDING_FULFILLMENT"
        or state.eligible_for_corridor_revalidation is not True
        or type(latest) is not ActionPacketTransitionEventV01
        or latest.transition_rule_id != "g2a_t03_pending"
        or latest.target_state != "PENDING_FULFILLMENT"
        or type(latest.execution_attempt_id) is not str
        or not validate_prefixed_sha256_identity_v01(
            latest.execution_attempt_id,
            prefix=EXECUTION_ATTEMPT_IDENTITY_PREFIX_V01,
        )[0]
        or latest.effect_consumption_class
        != pending_rule.effect_consumption_class
        or latest.receipt_ref is not None
        or any(
            event.execution_attempt_id == latest.execution_attempt_id
            and event.transition_rule_id
            in {
                "g2a_t04_fulfill_mock",
                "g2a_t24_nonconsuming_failure",
                "g2a_t26_uncertain_adapter_outcome",
            }
            for event in entry.transition_events
        )
    ):
        raise ValueError("action_packet_effect_pending_attempt_invalid")
    if (
        state.idempotency_disposition != "RESERVED"
        or state.reservation_owner_packet_id != packet_id
        or type(state.latest_disposition_event_id) is not str
        or not validate_prefixed_sha256_identity_v01(
            state.latest_disposition_event_id,
            prefix=IDEMPOTENCY_DISPOSITION_EVENT_PREFIX_V01,
        )[0]
        or state.terminal_receipt_ref is not None
        or packet_id in terminal_receipt_packet_ids
        or state.idempotency_key in terminal_receipt_idempotency_keys
    ):
        raise ValueError("action_packet_effect_reservation_invalid")
    temporal = evaluate_temporal_authority_v01(
        canonical.temporal_authority,
        evaluation_time=eligibility_evaluation_time,
    )
    if (
        temporal.outcome != TEMPORAL_OUTCOME_VALID_V01
        or type(temporal.executable) is not bool
        or temporal.executable is not True
    ):
        raise ValueError("action_packet_effect_temporal_invalid")
    dependency_observation_ids = (
        _g2a4a_current_dependency_observation_ids_v01(
            root_bound,
            current_dependency_observations,
            eligibility_evaluation_time=eligibility_evaluation_time,
            eligibility_evaluation_context_id=(
                eligibility_evaluation_context_id
            ),
            validation_pass=validation_pass,
        )
    )
    root_scope_refs = _g2a4a_validate_corridor_containment_v01(
        canonical,
        root_bound.packet_identity.packet_id,
        corridor,
        corridor_step,
    )
    issued_at_tick, expires_at_tick, current_tick = (
        _g2a4a_logical_ticks_v01(
            canonical,
            logical_time_bridge,
            eligibility_evaluation_time,
        )
    )
    root_result = root_projection.root_decision_result
    projection = ActionPacketEffectFirewallProjectionV01(
        projection_profile_id=(
            ACTION_PACKET_EFFECT_FIREWALL_PROJECTION_PROFILE_ID_V01
        ),
        packet_id=root_bound.packet_identity.packet_id,
        registry_id=registry_id,
        pending_transition_event_id=latest.transition_event_id,
        execution_attempt_id=latest.execution_attempt_id,
        corridor_id=corridor.corridor_id,
        corridor_step_id=corridor_step.step_id,
        corridor_class=canonical.adapter_binding.corridor_class,
        transaction_id=canonical.transaction_id,
        target_root_id=canonical.owning_local_root_id,
        root_decision_id=root_result.decision_id,
        selected_candidate_id=(
            canonical.authorization_candidate
            .root_packet_authorization_candidate_id
        ),
        permission_ref=canonical.canonical_permission_ref,
        allowed_adapter_ids=(
            canonical.normalized_permission_scope.allowed_adapter_ids
        ),
        allowed_action_kinds=(
            canonical.normalized_permission_scope.allowed_action_classes
        ),
        root_scope_refs=root_scope_refs,
        maximum_expires_at_tick=expires_at_tick,
        request_kind="ActionCommitPacket",
        adapter_id=canonical.adapter_binding.adapter_id,
        action_kind=canonical.selected_canonical_action,
        scope_refs=root_scope_refs,
        issued_at_tick=issued_at_tick,
        expires_at_tick=expires_at_tick,
        current_tick=current_tick,
        idempotency_key=canonical.idempotency_identity.idempotency_key,
        mock_only=True,
        effect_access_owner=_EFFECT_ACCESS_OWNER,
        logical_time_bridge_id=logical_time_bridge.bridge_id,
        attempt_evaluation_time=latest.evaluation_time,
        attempt_evaluation_time_source=latest.evaluation_time_source,
        attempt_evaluation_context_id=latest.evaluation_context_id,
        eligibility_evaluation_time=eligibility_evaluation_time,
        eligibility_evaluation_time_source=(
            eligibility_evaluation_time_source
        ),
        eligibility_evaluation_context_id=(
            eligibility_evaluation_context_id
        ),
        latest_disposition_event_id=state.latest_disposition_event_id,
        dependency_acceptance_binding_id=(
            root_bound.dependency_acceptance_binding
            .packet_dependency_acceptance_binding_id
        ),
        dependency_observation_ids=dependency_observation_ids,
        authority_policy_fingerprint=(
            canonical.authority_policy_fingerprint
        ),
        temporal_authority_fingerprint=(
            canonical.temporal_authority_fingerprint
        ),
    )
    if not _action_packet_effect_projection_exact_types_v01(projection):
        raise ValueError("action_packet_effect_projection_shape_invalid")
    return projection


def build_action_packet_effect_firewall_projection_v01(
    registry: object,
    *,
    packet_id: object,
    corridor: object,
    corridor_step: object,
    current_dependency_observations: object,
    logical_time_bridge: object,
    eligibility_evaluation_time: object,
    eligibility_evaluation_time_source: object,
    eligibility_evaluation_context_id: object,
) -> ActionPacketEffectFirewallProjectionV01:
    try:
        validation_result = _require_valid_action_packet_registry_v01(
            registry
        )
        return _build_action_packet_effect_firewall_projection_core_v01(
            registry,
            packet_id=packet_id,
            corridor=corridor,
            corridor_step=corridor_step,
            current_dependency_observations=(
                current_dependency_observations
            ),
            logical_time_bridge=logical_time_bridge,
            eligibility_evaluation_time=eligibility_evaluation_time,
            eligibility_evaluation_time_source=(
                eligibility_evaluation_time_source
            ),
            eligibility_evaluation_context_id=(
                eligibility_evaluation_context_id
            ),
            registry_validation_result=validation_result,
        )
    except ValueError as exc:
        raise ValueError(
            _stable_exception_reason_v01(
                exc,
                fallback="action_packet_effect_projection_invalid",
            )
        ) from None
    except Exception:
        raise ValueError("action_packet_effect_projection_invalid") from None


def _action_packet_effect_projection_exact_types_v01(
    value: ActionPacketEffectFirewallProjectionV01,
) -> bool:
    string_fields = (
        "projection_profile_id",
        "packet_id",
        "registry_id",
        "pending_transition_event_id",
        "execution_attempt_id",
        "corridor_id",
        "corridor_step_id",
        "corridor_class",
        "transaction_id",
        "target_root_id",
        "root_decision_id",
        "selected_candidate_id",
        "permission_ref",
        "request_kind",
        "adapter_id",
        "action_kind",
        "idempotency_key",
        "effect_access_owner",
        "logical_time_bridge_id",
        "attempt_evaluation_time_source",
        "attempt_evaluation_context_id",
        "eligibility_evaluation_time_source",
        "eligibility_evaluation_context_id",
        "latest_disposition_event_id",
        "dependency_acceptance_binding_id",
        "authority_policy_fingerprint",
        "temporal_authority_fingerprint",
    )
    tuple_fields = (
        "allowed_adapter_ids",
        "allowed_action_kinds",
        "root_scope_refs",
        "scope_refs",
        "dependency_observation_ids",
    )
    int_fields = (
        "maximum_expires_at_tick",
        "issued_at_tick",
        "expires_at_tick",
        "current_tick",
        "attempt_evaluation_time",
        "eligibility_evaluation_time",
    )
    return (
        all(
            type(getattr(value, name)) is str
            and validate_identity_text_v01(getattr(value, name))[0]
            for name in string_fields
        )
        and all(
            type(getattr(value, name)) is tuple
            and all(type(item) is str for item in getattr(value, name))
            for name in tuple_fields
        )
        and all(type(getattr(value, name)) is int for name in int_fields)
        and type(value.mock_only) is bool
    )


def _validate_action_packet_effect_firewall_projection_core_v01(
    value: object,
    registry: ActionCommitPacketRegistryV02,
    *,
    packet_id: object,
    corridor: object,
    corridor_step: object,
    current_dependency_observations: object,
    logical_time_bridge: object,
    eligibility_evaluation_time: object,
    eligibility_evaluation_time_source: object,
    eligibility_evaluation_context_id: object,
    registry_validation_result: _ActionPacketRegistryValidationResultV02,
) -> tuple[bool, tuple[str, ...]]:
    if type(value) is not ActionPacketEffectFirewallProjectionV01:
        return False, ("action_packet_effect_projection_type_invalid",)
    if not _action_packet_effect_projection_exact_types_v01(value):
        return False, ("action_packet_effect_projection_field_type_invalid",)
    try:
        expected = _build_action_packet_effect_firewall_projection_core_v01(
            registry,
            packet_id=packet_id,
            corridor=corridor,
            corridor_step=corridor_step,
            current_dependency_observations=(
                current_dependency_observations
            ),
            logical_time_bridge=logical_time_bridge,
            eligibility_evaluation_time=eligibility_evaluation_time,
            eligibility_evaluation_time_source=(
                eligibility_evaluation_time_source
            ),
            eligibility_evaluation_context_id=(
                eligibility_evaluation_context_id
            ),
            registry_validation_result=registry_validation_result,
        )
    except ValueError as exc:
        return False, (
            _stable_exception_reason_v01(
                exc,
                fallback="action_packet_effect_projection_invalid",
            ),
        )
    except Exception:
        return False, ("action_packet_effect_projection_invalid",)
    if value != expected:
        return False, ("action_packet_effect_projection_mismatch",)
    return True, ()


def validate_action_packet_effect_firewall_projection_v01(
    value: object,
    registry: object,
    *,
    packet_id: object,
    corridor: object,
    corridor_step: object,
    current_dependency_observations: object,
    logical_time_bridge: object,
    eligibility_evaluation_time: object,
    eligibility_evaluation_time_source: object,
    eligibility_evaluation_context_id: object,
) -> tuple[bool, tuple[str, ...]]:
    try:
        validation_result = _require_valid_action_packet_registry_v01(
            registry
        )
        return _validate_action_packet_effect_firewall_projection_core_v01(
            value,
            registry,
            packet_id=packet_id,
            corridor=corridor,
            corridor_step=corridor_step,
            current_dependency_observations=(
                current_dependency_observations
            ),
            logical_time_bridge=logical_time_bridge,
            eligibility_evaluation_time=eligibility_evaluation_time,
            eligibility_evaluation_time_source=(
                eligibility_evaluation_time_source
            ),
            eligibility_evaluation_context_id=(
                eligibility_evaluation_context_id
            ),
            registry_validation_result=validation_result,
        )
    except ValueError as exc:
        return False, (
            _stable_exception_reason_v01(
                exc,
                fallback="action_packet_effect_projection_invalid",
            ),
        )
    except Exception:
        return False, ("action_packet_effect_projection_invalid",)


def _prepare_action_packet_effect_attempt_v01(
    registry: object,
    *,
    packet_id: object,
    corridor: object,
    corridor_step: object,
    current_dependency_observations: object,
    logical_time_bridge: object,
    eligibility_evaluation_time: object,
    eligibility_evaluation_time_source: object,
    eligibility_evaluation_context_id: object,
) -> _ActionPacketEffectAttemptPreparationV01:
    try:
        validation_result = _require_valid_action_packet_registry_v01(
            registry
        )
        projection = (
            _build_action_packet_effect_firewall_projection_core_v01(
                registry,
                packet_id=packet_id,
                corridor=corridor,
                corridor_step=corridor_step,
                current_dependency_observations=(
                    current_dependency_observations
                ),
                logical_time_bridge=logical_time_bridge,
                eligibility_evaluation_time=eligibility_evaluation_time,
                eligibility_evaluation_time_source=(
                    eligibility_evaluation_time_source
                ),
                eligibility_evaluation_context_id=(
                    eligibility_evaluation_context_id
                ),
                registry_validation_result=validation_result,
            )
        )
        projection_valid, projection_reasons = (
            _validate_action_packet_effect_firewall_projection_core_v01(
                projection,
                registry,
                packet_id=packet_id,
                corridor=corridor,
                corridor_step=corridor_step,
                current_dependency_observations=(
                    current_dependency_observations
                ),
                logical_time_bridge=logical_time_bridge,
                eligibility_evaluation_time=eligibility_evaluation_time,
                eligibility_evaluation_time_source=(
                    eligibility_evaluation_time_source
                ),
                eligibility_evaluation_context_id=(
                    eligibility_evaluation_context_id
                ),
                registry_validation_result=validation_result,
            )
        )
        if not projection_valid:
            raise ValueError(projection_reasons[0])
        validation_pass = validation_result.validation_pass
        if type(validation_pass) is not _ActionPacketRegistryValidationPassV01:
            raise ValueError("action_packet_effect_registry_invalid")
        entry = _unique_lifecycle_entry_from_validation_pass_v01(
            validation_pass,
            packet_id,
        )
        root_projection = entry.root_bound_genesis.root_decision_projection
        firewall = _build_effect_firewall_v01(
            root_decision_kernel=root_projection.root_decision_kernel,
            decision_input=root_projection.root_decision_input,
            root_decision_result=root_projection.root_decision_result,
            invocation_id=projection.execution_attempt_id,
            allowed_adapter_ids=projection.allowed_adapter_ids,
            allowed_action_kinds=projection.allowed_action_kinds,
            root_scope_refs=projection.root_scope_refs,
            maximum_expires_at_tick=projection.maximum_expires_at_tick,
        )
        if _validate_effect_firewall_v01(firewall) != ():
            raise ValueError("action_packet_effect_firewall_invalid")
        firewall_equalities = (
            firewall.invocation_id == projection.execution_attempt_id,
            firewall.transaction_id == projection.transaction_id,
            firewall.target_root_id == projection.target_root_id,
            firewall.root_decision_id == projection.root_decision_id,
            firewall.selected_candidate_id
            == projection.selected_candidate_id,
            firewall.permission_ref == projection.permission_ref,
            firewall.allowed_adapter_ids == projection.allowed_adapter_ids,
            firewall.allowed_action_kinds
            == projection.allowed_action_kinds,
            firewall.root_scope_refs == projection.root_scope_refs,
            firewall.maximum_expires_at_tick
            == projection.maximum_expires_at_tick,
            type(firewall.mock_only) is bool,
            firewall.mock_only is True,
            firewall.effect_access_owner == _EFFECT_ACCESS_OWNER,
        )
        state = firewall._state
        if not all(firewall_equalities) or not (
            len(state.seen_request_ids) == 0
            and len(state.used_idempotency_keys) == 0
            and len(state.issued_capabilities) == 0
            and len(state.consumed_capability_ids) == 0
            and len(state.terminal_receipt_ids) == 0
            and state.mock_effect_execution_count == 0
        ):
            raise ValueError("action_packet_effect_firewall_binding_invalid")
        request = _build_effect_request_v01(
            root_decision_kernel=root_projection.root_decision_kernel,
            decision_input=root_projection.root_decision_input,
            root_decision_result=root_projection.root_decision_result,
            request_kind=projection.request_kind,
            adapter_id=projection.adapter_id,
            action_kind=projection.action_kind,
            scope_refs=projection.scope_refs,
            issued_at_tick=projection.issued_at_tick,
            expires_at_tick=projection.expires_at_tick,
            idempotency_key=projection.idempotency_key,
        )
        if _validate_effect_request_v01(request) != ():
            raise ValueError("action_packet_effect_request_invalid")
        request_equalities = (
            request.request_kind == "ActionCommitPacket",
            request.transaction_id == firewall.transaction_id,
            request.target_root_id == firewall.target_root_id,
            request.root_decision_id == firewall.root_decision_id,
            request.selected_candidate_id == firewall.selected_candidate_id,
            request.permission_ref == firewall.permission_ref,
            request.adapter_id == projection.adapter_id,
            request.action_kind == projection.action_kind,
            request.scope_refs == firewall.root_scope_refs,
            request.issued_at_tick == projection.issued_at_tick,
            request.expires_at_tick == projection.expires_at_tick,
            request.idempotency_key == projection.idempotency_key,
            type(request.mock_only) is bool,
            request.mock_only is True,
        )
        if not all(request_equalities):
            raise ValueError("action_packet_effect_request_binding_invalid")
        decision = _authorize_effect_request_v01(
            firewall=firewall,
            request=request,
            current_tick=projection.current_tick,
        )
        if (
            _validate_effect_firewall_decision_v01(
                firewall=firewall,
                request=request,
                decision=decision,
            )
            != ()
            or decision.decision != _EFFECT_DECISION_ALLOW_MOCK_EFFECT
            or decision.reason_code != "mock_effect_authorized"
            or type(decision.capability_issued) is not bool
            or decision.capability_issued is not True
            or type(decision.return_to_root) is not bool
            or decision.return_to_root is not False
            or type(decision.real_world_effects_count) is not int
            or decision.real_world_effects_count != 0
            or len(state.issued_capabilities) != 1
            or len(state.consumed_capability_ids) != 0
            or len(state.terminal_receipt_ids) != 0
            or state.mock_effect_execution_count != 0
        ):
            raise ValueError("action_packet_effect_authorization_invalid")
        return _ActionPacketEffectAttemptPreparationV01(
            projection=projection,
            firewall=firewall,
            request=request,
            decision=decision,
        )
    except ValueError as exc:
        raise ValueError(
            _stable_exception_reason_v01(
                exc,
                fallback="action_packet_effect_preparation_invalid",
            )
        ) from None
    except Exception:
        raise ValueError("action_packet_effect_preparation_invalid") from None


def _disposition_history_bytes_v01(
    history: tuple[IdempotencyDispositionEventV01, ...],
) -> bytes:
    return canonical_json_bytes_v01(
        tuple(
            idempotency_disposition_event_material_v01(event)
            for event in history
        )
    )


def _action_packet_private_component_sha256_v01(
    domain: str,
    value: object,
) -> str:
    return domain_separated_sha256_hex_v01(
        domain=domain,
        payload=canonical_json_bytes_v01(value),
    )


def _action_packet_effect_projection_sha256_v01(
    projection: ActionPacketEffectFirewallProjectionV01,
) -> str:
    if (
        type(projection) is not ActionPacketEffectFirewallProjectionV01
        or not _action_packet_effect_projection_exact_types_v01(projection)
    ):
        raise ValueError("action_packet_effect_projection_invalid")
    material = tuple(
        (name, getattr(projection, name))
        for name in (
            "projection_profile_id",
            "packet_id",
            "registry_id",
            "pending_transition_event_id",
            "execution_attempt_id",
            "corridor_id",
            "corridor_step_id",
            "corridor_class",
            "transaction_id",
            "target_root_id",
            "root_decision_id",
            "selected_candidate_id",
            "permission_ref",
            "allowed_adapter_ids",
            "allowed_action_kinds",
            "root_scope_refs",
            "maximum_expires_at_tick",
            "request_kind",
            "adapter_id",
            "action_kind",
            "scope_refs",
            "issued_at_tick",
            "expires_at_tick",
            "current_tick",
            "idempotency_key",
            "mock_only",
            "effect_access_owner",
            "logical_time_bridge_id",
            "attempt_evaluation_time",
            "attempt_evaluation_time_source",
            "attempt_evaluation_context_id",
            "eligibility_evaluation_time",
            "eligibility_evaluation_time_source",
            "eligibility_evaluation_context_id",
            "latest_disposition_event_id",
            "dependency_acceptance_binding_id",
            "dependency_observation_ids",
            "authority_policy_fingerprint",
            "temporal_authority_fingerprint",
        )
    )
    return _action_packet_private_component_sha256_v01(
        _ACTION_PACKET_EFFECT_PROJECTION_HASH_DOMAIN_V01,
        material,
    )


def _action_packet_firewall_state_sha256_v01(
    firewall: _EffectFirewallV01,
) -> str:
    return _action_packet_firewall_state_observation_v01(firewall)[1]


def _historical_action_packet_firewall_plain_v01(
    projection: ActionPacketEffectFirewallProjectionV01,
    authorization: _EffectFirewallHistoricalAuthorizationProjectionV01,
    *,
    consumed: bool,
) -> dict[str, object]:
    counters = {
        "seen_request_count": 1,
        "used_idempotency_key_count": 1,
        "issued_capability_count": (
            1 if authorization.expected_capability_id is not None else 0
        ),
        "consumed_capability_count": 1 if consumed else 0,
        "terminal_receipt_count": 1 if consumed else 0,
        "mock_effect_execution_count": 1 if consumed else 0,
        "real_world_effects_count": 0,
    }
    return {
        "firewall_id": authorization.firewall_id,
        "firewall_version": _EFFECT_FIREWALL_VERSION,
        "invocation_id": projection.execution_attempt_id,
        "transaction_id": projection.transaction_id,
        "target_root_id": projection.target_root_id,
        "root_decision_id": projection.root_decision_id,
        "selected_candidate_id": projection.selected_candidate_id,
        "permission_ref": projection.permission_ref,
        "allowed_adapter_ids": list(projection.allowed_adapter_ids),
        "allowed_action_kinds": list(projection.allowed_action_kinds),
        "root_scope_refs": list(projection.root_scope_refs),
        "maximum_expires_at_tick": projection.maximum_expires_at_tick,
        "mock_only": True,
        "effect_access_owner": _EFFECT_ACCESS_OWNER,
        "state_counters": counters,
    }


def _historical_action_packet_effect_authorization_v01(
    entry: ActionPacketLifecycleEntryV01,
    projection: ActionPacketEffectFirewallProjectionV01,
) -> _ActionPacketHistoricalEffectAuthorizationV01:
    root_projection = entry.root_bound_genesis.root_decision_projection
    authorization = _project_effect_firewall_historical_authorization_v01(
        root_decision_kernel=root_projection.root_decision_kernel,
        decision_input=root_projection.root_decision_input,
        root_decision_result=root_projection.root_decision_result,
        invocation_id=projection.execution_attempt_id,
        allowed_adapter_ids=projection.allowed_adapter_ids,
        allowed_action_kinds=projection.allowed_action_kinds,
        root_scope_refs=projection.root_scope_refs,
        maximum_expires_at_tick=projection.maximum_expires_at_tick,
        request_kind=projection.request_kind,
        adapter_id=projection.adapter_id,
        action_kind=projection.action_kind,
        scope_refs=projection.scope_refs,
        issued_at_tick=projection.issued_at_tick,
        expires_at_tick=projection.expires_at_tick,
        idempotency_key=projection.idempotency_key,
        current_tick=projection.current_tick,
    )
    before = _action_packet_private_component_sha256_v01(
        _ACTION_PACKET_FIREWALL_STATE_HASH_DOMAIN_V01,
        _historical_action_packet_firewall_plain_v01(
            projection,
            authorization,
            consumed=False,
        ),
    )
    consumed = (
        _action_packet_private_component_sha256_v01(
            _ACTION_PACKET_FIREWALL_STATE_HASH_DOMAIN_V01,
            _historical_action_packet_firewall_plain_v01(
                projection,
                authorization,
                consumed=True,
            ),
        )
        if authorization.expected_capability_id is not None
        else None
    )
    return _ActionPacketHistoricalEffectAuthorizationV01(
        projection=projection,
        firewall_id=authorization.firewall_id,
        request=authorization.request,
        decision=authorization.decision,
        expected_capability_id=authorization.expected_capability_id,
        firewall_state_sha256_before=before,
        firewall_state_sha256_consumed=consumed,
    )


def _action_packet_firewall_state_observation_v01(
    firewall: object,
) -> tuple[bool, str, dict[str, object] | None]:
    try:
        plain = _effect_firewall_to_plain_dict_v01(firewall)
        return (
            True,
            _action_packet_private_component_sha256_v01(
                _ACTION_PACKET_FIREWALL_STATE_HASH_DOMAIN_V01,
                plain,
            ),
            plain,
        )
    except Exception:
        state = (
            getattr(firewall, "_state", None)
            if type(firewall) is _EffectFirewallV01
            else None
        )
        observation = {
            "observation_class": "UNVALIDATABLE_STATE",
            "firewall_type_status": (
                "EXACT" if type(firewall) is _EffectFirewallV01 else "INVALID"
            ),
            "state_presence_status": (
                "PRESENT" if state is not None else "ABSENT"
            ),
            "seen_request_ids_status": (
                "EXACT_SET"
                if type(getattr(state, "seen_request_ids", None)) is set
                else "INVALID"
            ),
            "used_idempotency_keys_status": (
                "EXACT_SET"
                if type(getattr(state, "used_idempotency_keys", None)) is set
                else "INVALID"
            ),
            "issued_capabilities_status": (
                "EXACT_DICT"
                if type(getattr(state, "issued_capabilities", None)) is dict
                else "INVALID"
            ),
            "consumed_capability_ids_status": (
                "EXACT_SET"
                if type(
                    getattr(state, "consumed_capability_ids", None)
                )
                is set
                else "INVALID"
            ),
            "terminal_receipt_ids_status": (
                "EXACT_SET"
                if type(getattr(state, "terminal_receipt_ids", None)) is set
                else "INVALID"
            ),
            "mock_effect_execution_count_status": (
                "EXACT_INT"
                if type(
                    getattr(state, "mock_effect_execution_count", None)
                )
                is int
                else "INVALID"
            ),
        }
        return (
            False,
            _action_packet_private_component_sha256_v01(
                _ACTION_PACKET_FIREWALL_STATE_HASH_DOMAIN_V01,
                observation,
            ),
            None,
        )


def _action_packet_disposition_history_sha256_v01(
    history: tuple[IdempotencyDispositionEventV01, ...],
) -> str:
    return domain_separated_sha256_hex_v01(
        domain=_ACTION_PACKET_DISPOSITION_HISTORY_HASH_DOMAIN_V01,
        payload=_disposition_history_bytes_v01(history),
    )


def _action_packet_effect_receipt_sha256_v01(
    receipt: _KernelArtifactV01,
) -> str:
    return _action_packet_private_component_sha256_v01(
        _ACTION_PACKET_EFFECT_RECEIPT_HASH_DOMAIN_V01,
        _kernel_artifact_to_plain_dict_v01(receipt),
    )


def _action_packet_effect_receipt_ref_v01(
    *,
    packet_id: str,
    execution_attempt_id: str,
    request_id: str,
    decision_id: str,
    eligibility_evaluation_context_id: str,
) -> str:
    return build_domain_separated_identity_v01(
        domain=_ACTION_PACKET_EFFECT_RECEIPT_REF_DOMAIN_V01,
        prefix=_ACTION_PACKET_EFFECT_RECEIPT_REF_PREFIX_V01,
        material=(
            ("packet_id", packet_id),
            ("execution_attempt_id", execution_attempt_id),
            ("request_id", request_id),
            ("decision_id", decision_id),
            (
                "eligibility_evaluation_context_id",
                eligibility_evaluation_context_id,
            ),
        ),
    )


def _action_packet_effect_receipt_time_envelope_v01(
    entry: ActionPacketLifecycleEntryV01,
    projection: ActionPacketEffectFirewallProjectionV01,
) -> dict[str, object]:
    temporal = entry.root_bound_genesis.canonical_projection.temporal_authority
    return {
        "ct_session_anchor": projection.eligibility_evaluation_context_id,
        "et_observed_at": format_utc_timestamp_v01(
            projection.eligibility_evaluation_time
        ),
        "freshness_class": "real_time",
        "kt_asof": format_utc_timestamp_v01(
            projection.eligibility_evaluation_time
        ),
        "pt_created_at": format_utc_timestamp_v01(temporal.issued_at_utc),
        "ttl_seconds": (
            temporal.expires_at_utc
            - projection.eligibility_evaluation_time
        ),
        "valid_from": format_utc_timestamp_v01(temporal.issued_at_utc),
        "valid_to": format_utc_timestamp_v01(temporal.expires_at_utc),
    }


def _expected_action_packet_effect_receipt_plain_v01(
    entry: ActionPacketLifecycleEntryV01,
    projection: ActionPacketEffectFirewallProjectionV01,
    request: _EffectRequestV01,
    decision: _EffectFirewallDecisionV01,
) -> dict[str, object]:
    receipt_ref = _action_packet_effect_receipt_ref_v01(
        packet_id=projection.packet_id,
        execution_attempt_id=projection.execution_attempt_id,
        request_id=request.request_id,
        decision_id=decision.decision_id,
        eligibility_evaluation_context_id=(
            projection.eligibility_evaluation_context_id
        ),
    )
    payload = {
        "receipt_ref": receipt_ref,
        "request_id": request.request_id,
        "firewall_decision_id": decision.decision_id,
        "capability_id": decision.capability_id,
        "root_decision_id": request.root_decision_id,
        "selected_candidate_id": request.selected_candidate_id,
        "permission_ref": request.permission_ref,
        "adapter_id": request.adapter_id,
        "action_kind": request.action_kind,
        "scope_refs": list(request.scope_refs),
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
    return {
        "abi_version": "v1.0",
        "artifact_id": receipt_ref,
        "artifact_type": "EvidenceReceipt",
        "schema_version": "v1",
        "transaction_id": request.transaction_id,
        "owner_root_id": request.target_root_id,
        "source_component": _RECEIPT_SOURCE_COMPONENT,
        "authority_class": "EVIDENCE_ONLY",
        "lifecycle_state": "RECEIPT_RECORDED",
        "payload": payload,
        "trace_refs": [
            request.request_id,
            request.root_decision_id,
            decision.decision_id,
        ],
        "parent_refs": [request.root_decision_id],
        "time_envelope": _action_packet_effect_receipt_time_envelope_v01(
            entry,
            projection,
        ),
    }


def _rebuild_exact_action_packet_effect_receipt_v01(
    entry: ActionPacketLifecycleEntryV01,
    projection: ActionPacketEffectFirewallProjectionV01,
    request: _EffectRequestV01,
    decision: _EffectFirewallDecisionV01,
) -> _KernelArtifactV01:
    plain = _expected_action_packet_effect_receipt_plain_v01(
        entry,
        projection,
        request,
        decision,
    )
    return _build_kernel_artifact_v01(
        abi_version=plain["abi_version"],
        artifact_id=plain["artifact_id"],
        artifact_type=plain["artifact_type"],
        schema_version=plain["schema_version"],
        transaction_id=plain["transaction_id"],
        owner_root_id=plain["owner_root_id"],
        source_component=plain["source_component"],
        authority_class=plain["authority_class"],
        lifecycle_state=plain["lifecycle_state"],
        payload=plain["payload"],
        trace_refs=tuple(plain["trace_refs"]),
        parent_refs=tuple(plain["parent_refs"]),
        time_envelope=plain["time_envelope"],
    )


def _prepare_action_packet_effect_attempt_from_projection_v01(
    entry: ActionPacketLifecycleEntryV01,
    projection: ActionPacketEffectFirewallProjectionV01,
) -> _ActionPacketEffectAttemptPreparationV01:
    root_projection = entry.root_bound_genesis.root_decision_projection
    firewall = _build_effect_firewall_v01(
        root_decision_kernel=root_projection.root_decision_kernel,
        decision_input=root_projection.root_decision_input,
        root_decision_result=root_projection.root_decision_result,
        invocation_id=projection.execution_attempt_id,
        allowed_adapter_ids=projection.allowed_adapter_ids,
        allowed_action_kinds=projection.allowed_action_kinds,
        root_scope_refs=projection.root_scope_refs,
        maximum_expires_at_tick=projection.maximum_expires_at_tick,
    )
    if _validate_effect_firewall_v01(firewall) != ():
        raise ValueError("action_packet_effect_firewall_invalid")
    request = _build_effect_request_v01(
        root_decision_kernel=root_projection.root_decision_kernel,
        decision_input=root_projection.root_decision_input,
        root_decision_result=root_projection.root_decision_result,
        request_kind=projection.request_kind,
        adapter_id=projection.adapter_id,
        action_kind=projection.action_kind,
        scope_refs=projection.scope_refs,
        issued_at_tick=projection.issued_at_tick,
        expires_at_tick=projection.expires_at_tick,
        idempotency_key=projection.idempotency_key,
    )
    if _validate_effect_request_v01(request) != ():
        raise ValueError("action_packet_effect_request_invalid")
    decision = _authorize_effect_request_v01(
        firewall=firewall,
        request=request,
        current_tick=projection.current_tick,
    )
    if (
        _validate_effect_firewall_decision_v01(
            firewall=firewall,
            request=request,
            decision=decision,
        )
        != ()
        or decision.decision
        not in {
            _EFFECT_DECISION_ALLOW_MOCK_EFFECT,
            _EFFECT_DECISION_BLOCKED_FAIL_CLOSED,
        }
        or decision.real_world_effects_count != 0
    ):
        raise ValueError("action_packet_effect_authorization_invalid")
    return _ActionPacketEffectAttemptPreparationV01(
        projection=projection,
        firewall=firewall,
        request=request,
        decision=decision,
    )


def _g2a4b_attempt_input_v01(
    registry: ActionCommitPacketRegistryV02,
    validation_result: _ActionPacketRegistryValidationResultV02,
    *,
    packet_id: object,
    corridor: object,
    corridor_step: object,
    current_dependency_observations: object,
    logical_time_bridge: object,
    eligibility_evaluation_time: object,
    eligibility_evaluation_time_source: object,
    eligibility_evaluation_context_id: object,
) -> tuple[
    ActionPacketLifecycleEntryV01,
    ActionPacketTransitionEventV01,
    ActionPacketLifecycleStateV01,
    int,
]:
    validation_pass = validation_result.validation_pass
    if type(validation_pass) is not _ActionPacketRegistryValidationPassV01:
        raise ValueError("action_packet_fulfillment_registry_invalid")
    entry = _unique_lifecycle_entry_from_validation_pass_v01(
        validation_pass,
        packet_id,
    )
    state = _derive_action_packet_lifecycle_state_unchecked_v01(
        entry,
        registry.idempotency_disposition_events,
    )
    pending = entry.transition_events[-1] if entry.transition_events else None
    if not (
        type(pending) is ActionPacketTransitionEventV01
        and pending.transition_rule_id == "g2a_t03_pending"
        and type(pending.execution_attempt_id) is str
        and state.lifecycle_state == "PENDING_FULFILLMENT"
        and state.idempotency_disposition == "RESERVED"
        and state.reservation_owner_packet_id == packet_id
        and type(state.latest_disposition_event_id) is str
    ):
        raise ValueError("action_packet_fulfillment_attempt_invalid")
    if (
        type(corridor) is not ContractFulfillmentCorridorV01
        or type(corridor_step) is not CorridorStepV01
        or type(current_dependency_observations) is not tuple
        or any(
            not validate_action_dependency_current_observation_v01(item)[0]
            for item in current_dependency_observations
        )
        or type(logical_time_bridge) is not LogicalTimeBridgeV01
        or not validate_logical_time_bridge_v01(logical_time_bridge)[0]
        or not validate_signed_int64_v01(
            eligibility_evaluation_time
        )[0]
        or not validate_identity_text_v01(
            eligibility_evaluation_time_source
        )[0]
        or not validate_identity_text_v01(
            eligibility_evaluation_context_id
        )[0]
    ):
        raise ValueError("action_packet_fulfillment_context_invalid")
    prior = tuple(
        context
        for context in registry.action_packet_fulfillment_attempt_contexts
        if (
            context.attempt_evidence.execution_attempt_id
            == pending.execution_attempt_id
        )
    )
    if any(
        context.attempt_evidence.outcome_class
        in {"CONSUMED", "NOT_CONSUMED", "UNCERTAIN"}
        for context in prior
    ):
        raise ValueError("action_packet_fulfillment_attempt_closed")
    if any(
        context.attempt_evidence.eligibility_evaluation_context_id
        == eligibility_evaluation_context_id
        for context in prior
    ):
        raise ValueError("action_packet_fulfillment_observation_duplicate")
    return entry, pending, state, len(prior) + 1


def _g2a4b_dependency_observation_ids_v01(
    observations: tuple[ActionDependencyCurrentObservationV01, ...],
) -> tuple[str, ...]:
    return tuple(
        item.observation_id
        for item in sorted(
            observations,
            key=lambda item: item.dependency_id.encode("utf-8"),
        )
    )


def _g2a4b_attempt_evidence_v01(
    registry: ActionCommitPacketRegistryV02,
    entry: ActionPacketLifecycleEntryV01,
    pending: ActionPacketTransitionEventV01,
    state: ActionPacketLifecycleStateV01,
    *,
    ordinal: int,
    corridor: ContractFulfillmentCorridorV01,
    corridor_step: CorridorStepV01,
    observations: tuple[ActionDependencyCurrentObservationV01, ...],
    logical_time_bridge: LogicalTimeBridgeV01,
    eligibility_evaluation_time: int,
    eligibility_evaluation_time_source: str,
    eligibility_evaluation_context_id: str,
    projection: ActionPacketEffectFirewallProjectionV01 | None,
    preparation: _ActionPacketEffectAttemptPreparationV01 | None,
    outcome_class: str,
    reason_code: str,
    adapter_invoked: bool,
    firewall_state_sha256_before: str | None,
    firewall_state_sha256_after: str | None,
    receipt: _KernelArtifactV01 | None,
) -> ActionPacketFulfillmentAttemptEvidenceV01:
    decision = preparation.decision if preparation is not None else None
    request = preparation.request if preparation is not None else None
    firewall = preparation.firewall if preparation is not None else None
    relation = {
        "PRE_FULFILLMENT_BLOCKED": "NO_ADAPTER_INVOCATION",
        "FIREWALL_BLOCKED": "NO_ADAPTER_INVOCATION",
        "CONSUMED": "CORRIDOR_INVOCATION_CONSUMED",
        "NOT_CONSUMED": "CORRIDOR_INVOCATION_NONCONSUMING",
        "UNCERTAIN": "CORRIDOR_INVOCATION_UNCERTAIN",
    }[outcome_class]
    receipt_ref = receipt.artifact_id if receipt is not None else None
    return build_action_packet_fulfillment_attempt_evidence_v01(
        packet_id=entry.root_bound_genesis.packet_identity.packet_id,
        registry_id_before=registry.registry_id,
        pending_transition_event_id=pending.transition_event_id,
        execution_attempt_id=pending.execution_attempt_id,
        attempt_observation_ordinal=ordinal,
        corridor_id=corridor.corridor_id,
        corridor_step_id=corridor_step.step_id,
        logical_time_bridge_id=logical_time_bridge.bridge_id,
        dependency_observation_ids=(
            _g2a4b_dependency_observation_ids_v01(observations)
        ),
        projection_sha256=(
            _action_packet_effect_projection_sha256_v01(projection)
            if projection is not None
            else None
        ),
        firewall_id=firewall.firewall_id if firewall is not None else None,
        request_id=request.request_id if request is not None else None,
        decision_id=decision.decision_id if decision is not None else None,
        capability_id=(
            decision.capability_id
            if (
                decision is not None
                and outcome_class
                not in {"PRE_FULFILLMENT_BLOCKED", "FIREWALL_BLOCKED"}
            )
            else None
        ),
        adapter_id=projection.adapter_id if projection is not None else None,
        action_kind=projection.action_kind if projection is not None else None,
        invocation_relation_code=relation,
        outcome_class=outcome_class,
        reason_code=reason_code,
        adapter_invoked=adapter_invoked,
        adapter_call_count=1 if adapter_invoked else 0,
        firewall_state_sha256_before=firewall_state_sha256_before,
        firewall_state_sha256_after=firewall_state_sha256_after,
        receipt_ref=receipt_ref,
        receipt_sha256=(
            _action_packet_effect_receipt_sha256_v01(receipt)
            if receipt is not None
            else None
        ),
        disposition_before=state.idempotency_disposition,
        reservation_owner_packet_id_before=(
            state.reservation_owner_packet_id
        ),
        latest_disposition_event_id_before=(
            state.latest_disposition_event_id
        ),
        disposition_history_sha256_before=(
            _action_packet_disposition_history_sha256_v01(
                registry.idempotency_disposition_events
            )
        ),
        attempt_evaluation_time=pending.evaluation_time,
        attempt_evaluation_time_source=pending.evaluation_time_source,
        attempt_evaluation_context_id=pending.evaluation_context_id,
        eligibility_evaluation_time=eligibility_evaluation_time,
        eligibility_evaluation_time_source=(
            eligibility_evaluation_time_source
        ),
        eligibility_evaluation_context_id=(
            eligibility_evaluation_context_id
        ),
        real_world_effects_count=0,
    )


def _g2a4b_transition_binding_v01(
    transition_registry: ActionPacketTransitionRegistryProfileV01,
    *,
    rule_id: str,
    evidence_code: str,
    evidence_ref: str,
    evidence_sha256: str,
    validator_profile_id: str,
) -> TransitionEvidenceBindingV01:
    return build_transition_evidence_binding_v01(
        action_packet_transition_registry_profile=transition_registry,
        transition_rule_id=rule_id,
        evidence_code=evidence_code,
        evidence_ref=evidence_ref,
        evidence_sha256=evidence_sha256,
        validator_profile_id=validator_profile_id,
    )


def _g2a4b_attempt_identity_v01(
    entry: ActionPacketLifecycleEntryV01,
    pending: ActionPacketTransitionEventV01,
) -> ActionExecutionAttemptIdentityV01:
    attempt = build_action_execution_attempt_identity_v01(
        packet_id=pending.packet_id,
        idempotency_key=pending.idempotency_key,
        attempt_ordinal=sum(
            event.transition_rule_id == "g2a_t03_pending"
            for event in entry.transition_events
        ),
        evaluation_context_id=pending.evaluation_context_id,
    )
    if attempt.execution_attempt_id != pending.execution_attempt_id:
        raise ValueError("action_packet_fulfillment_attempt_invalid")
    return attempt


def _g2a4b_outcome_transition_v01(
    entry: ActionPacketLifecycleEntryV01,
    pending: ActionPacketTransitionEventV01,
    state: ActionPacketLifecycleStateV01,
    evidence: ActionPacketFulfillmentAttemptEvidenceV01,
    *,
    rule_id: str,
    receipt: _KernelArtifactV01 | None,
    transition_registry: ActionPacketTransitionRegistryProfileV01,
) -> ActionPacketTransitionEventV01:
    evidence_hash = evidence.attempt_evidence_id[
        len(ACTION_PACKET_FULFILLMENT_ATTEMPT_EVIDENCE_PREFIX_V01) :
    ]
    disposition_id = state.latest_disposition_event_id
    if type(disposition_id) is not str:
        raise ValueError("action_packet_fulfillment_disposition_invalid")
    disposition_hash = disposition_id[
        len(IDEMPOTENCY_DISPOSITION_EVENT_PREFIX_V01) :
    ]
    binding_specs: dict[str, tuple[str, str, str]] = {
        "adapter_invocation_evidence_valid": (
            evidence.attempt_evidence_id,
            evidence_hash,
            ACTION_PACKET_FULFILLMENT_ATTEMPT_EVIDENCE_PROFILE_ID_V01,
        ),
        "effect_consumption_evidence_valid": (
            evidence.attempt_evidence_id,
            evidence_hash,
            ACTION_PACKET_FULFILLMENT_ATTEMPT_EVIDENCE_PROFILE_ID_V01,
        ),
        "effect_nonconsumption_evidence_valid": (
            evidence.attempt_evidence_id,
            evidence_hash,
            ACTION_PACKET_FULFILLMENT_ATTEMPT_EVIDENCE_PROFILE_ID_V01,
        ),
        "effect_outcome_unresolved": (
            evidence.attempt_evidence_id,
            evidence_hash,
            ACTION_PACKET_FULFILLMENT_ATTEMPT_EVIDENCE_PROFILE_ID_V01,
        ),
        "idempotency_reservation_owned": (
            disposition_id,
            disposition_hash,
            IDEMPOTENCY_DISPOSITION_EVENT_PROFILE_ID_V01,
        ),
        "latest_disposition_event_binding_valid": (
            disposition_id,
            disposition_hash,
            IDEMPOTENCY_DISPOSITION_EVENT_PROFILE_ID_V01,
        ),
    }
    if rule_id == "g2a_t04_fulfill_mock":
        if receipt is None or evidence.receipt_sha256 is None:
            raise ValueError("action_packet_fulfillment_receipt_invalid")
        binding_specs["mock_adapter_result_valid"] = (
            receipt.artifact_id,
            evidence.receipt_sha256,
            "effect_firewall_receipt_v01",
        )
    rule = lookup_action_packet_transition_rule_v01(
        registry=transition_registry,
        transition_rule_id=rule_id,
    )
    bindings = tuple(
        _g2a4b_transition_binding_v01(
            transition_registry,
            rule_id=rule_id,
            evidence_code=code,
            evidence_ref=binding_specs[code][0],
            evidence_sha256=binding_specs[code][1],
            validator_profile_id=binding_specs[code][2],
        )
        for code in rule.required_evidence_codes
    )
    return build_action_packet_transition_event_v01(
        action_packet_transition_registry_profile=transition_registry,
        transition_rule_id=rule_id,
        packet_id=pending.packet_id,
        idempotency_key=pending.idempotency_key,
        previous_transition_event_id=pending.transition_event_id,
        owning_local_root_id=pending.owning_local_root_id,
        root_decision_ref=None,
        transition_evidence_bindings=bindings,
        dependency_set_candidate_fingerprint=(
            pending.dependency_set_candidate_fingerprint
        ),
        temporal_authority_fingerprint=(
            pending.temporal_authority_fingerprint
        ),
        evaluation_time=pending.evaluation_time,
        evaluation_time_source=pending.evaluation_time_source,
        evaluation_context_id=pending.evaluation_context_id,
        execution_attempt_identity=_g2a4b_attempt_identity_v01(
            entry,
            pending,
        ),
        receipt_ref=None,
    )


def _g2a4b_receipt_transition_v01(
    entry: ActionPacketLifecycleEntryV01,
    consumed: ActionPacketTransitionEventV01,
    evidence: ActionPacketFulfillmentAttemptEvidenceV01,
    receipt: _KernelArtifactV01,
    *,
    receipt_evaluation_time: int,
    receipt_evaluation_time_source: str,
    transition_registry: ActionPacketTransitionRegistryProfileV01,
) -> ActionPacketTransitionEventV01:
    if evidence.receipt_sha256 is None:
        raise ValueError("action_packet_receipt_observation_invalid")
    specs = {
        "terminal_receipt_valid": (
            receipt.artifact_id,
            evidence.receipt_sha256,
            "effect_firewall_receipt_v01",
        ),
        "fulfillment_consumption_evidence_valid": (
            consumed.transition_event_id,
            consumed.transition_event_id[
                len(ACTION_PACKET_TRANSITION_EVENT_PREFIX_V01) :
            ],
            ACTION_PACKET_TRANSITION_EVENT_PROFILE_ID_V01,
        ),
    }
    rule_id = "g2a_t05_receipt"
    rule = lookup_action_packet_transition_rule_v01(
        registry=transition_registry,
        transition_rule_id=rule_id,
    )
    bindings = tuple(
        _g2a4b_transition_binding_v01(
            transition_registry,
            rule_id=rule_id,
            evidence_code=code,
            evidence_ref=specs[code][0],
            evidence_sha256=specs[code][1],
            validator_profile_id=specs[code][2],
        )
        for code in rule.required_evidence_codes
    )
    pending = next(
        event
        for event in reversed(entry.transition_events)
        if (
            event.transition_rule_id == "g2a_t03_pending"
            and event.execution_attempt_id == consumed.execution_attempt_id
        )
    )
    return build_action_packet_transition_event_v01(
        action_packet_transition_registry_profile=transition_registry,
        transition_rule_id=rule_id,
        packet_id=consumed.packet_id,
        idempotency_key=consumed.idempotency_key,
        previous_transition_event_id=consumed.transition_event_id,
        owning_local_root_id=consumed.owning_local_root_id,
        root_decision_ref=None,
        transition_evidence_bindings=bindings,
        dependency_set_candidate_fingerprint=(
            consumed.dependency_set_candidate_fingerprint
        ),
        temporal_authority_fingerprint=(
            consumed.temporal_authority_fingerprint
        ),
        evaluation_time=receipt_evaluation_time,
        evaluation_time_source=receipt_evaluation_time_source,
        evaluation_context_id=consumed.evaluation_context_id,
        execution_attempt_identity=_g2a4b_attempt_identity_v01(
            entry,
            pending,
        ),
        receipt_ref=receipt.artifact_id,
    )


def _g2a4b_outcome_disposition_v01(
    state: ActionPacketLifecycleStateV01,
    transition: ActionPacketTransitionEventV01,
    *,
    event_class: str,
) -> IdempotencyDispositionEventV01:
    from_disposition, to_disposition, evidence_codes = {
        "CONSUME": (
            "RESERVED",
            "CONSUMED",
            (
                "effect_consumption_evidence_valid",
                "mock_adapter_result_valid",
            ),
        ),
        "UNCERTAIN_CLOSE": (
            "RESERVED",
            "UNCERTAIN_CLOSED",
            (
                "adapter_invocation_evidence_valid",
                "effect_outcome_unresolved",
            ),
        ),
        "RECEIPT_CONFIRM": (
            "CONSUMED",
            "CONSUMED",
            (
                "fulfillment_consumption_evidence_valid",
                "terminal_receipt_valid",
            ),
        ),
    }[event_class]
    return build_idempotency_disposition_event_v01(
        idempotency_key=state.idempotency_key,
        event_class=event_class,
        from_disposition=from_disposition,
        to_disposition=to_disposition,
        from_owner_packet_id=state.packet_id,
        to_owner_packet_id=state.packet_id,
        previous_disposition_event_id=state.latest_disposition_event_id,
        cause_transition_event_ids=(transition.transition_event_id,),
        root_decision_ref=None,
        predecessor_packet_id=None,
        successor_packet_id=None,
        evidence_refs=_binding_ids_for_codes_v01(
            transition,
            evidence_codes,
        ),
        evaluation_time=transition.evaluation_time,
        evaluation_time_source=transition.evaluation_time_source,
        evaluation_context_id=transition.evaluation_context_id,
    )


def _g2a4b_append_context_only_v01(
    registry: ActionCommitPacketRegistryV02,
    context: _ActionPacketFulfillmentAttemptContextV01,
) -> ActionCommitPacketRegistryV02:
    proposed = _registry_with_g2a_histories_v01(
        registry,
        fulfillment_attempt_contexts=(
            registry.action_packet_fulfillment_attempt_contexts
            + (context,)
        ),
    )
    _require_valid_action_packet_registry_v01(proposed)
    return proposed


def _g2a4b_append_outcome_v01(
    registry: ActionCommitPacketRegistryV02,
    entry: ActionPacketLifecycleEntryV01,
    context: _ActionPacketFulfillmentAttemptContextV01,
    transition: ActionPacketTransitionEventV01,
    disposition: IdempotencyDispositionEventV01 | None,
) -> ActionCommitPacketRegistryV02:
    proposed = _g2a4b_build_outcome_registry_v01(
        registry,
        entry,
        context,
        transition,
        disposition,
    )
    _require_valid_action_packet_registry_v01(proposed)
    return proposed


def _g2a4b_build_outcome_registry_v01(
    registry: ActionCommitPacketRegistryV02,
    entry: ActionPacketLifecycleEntryV01,
    context: _ActionPacketFulfillmentAttemptContextV01,
    transition: ActionPacketTransitionEventV01,
    disposition: IdempotencyDispositionEventV01 | None,
) -> ActionCommitPacketRegistryV02:
    updated_entry = ActionPacketLifecycleEntryV01(
        root_bound_genesis=entry.root_bound_genesis,
        transition_registry_id=entry.transition_registry_id,
        transition_events=entry.transition_events + (transition,),
    )
    entries = tuple(
        updated_entry if candidate is entry else candidate
        for candidate in registry.action_packet_lifecycle_entries
    )
    proposed = _registry_with_g2a_histories_v01(
        registry,
        lifecycle_entries=entries,
        disposition_events=(
            registry.idempotency_disposition_events
            if disposition is None
            else registry.idempotency_disposition_events + (disposition,)
        ),
        fulfillment_attempt_contexts=(
            registry.action_packet_fulfillment_attempt_contexts
            + (context,)
        ),
    )
    return proposed


def _g2a4b_transition_binding_matches_v01(
    transition: ActionPacketTransitionEventV01,
    evidence_code: str,
    *,
    evidence_ref: str,
    evidence_sha256: str,
    validator_profile_id: str,
) -> bool:
    matching = tuple(
        binding
        for binding in transition.transition_evidence_bindings
        if binding.evidence_code == evidence_code
    )
    return (
        len(matching) == 1
        and matching[0].evidence_ref == evidence_ref
        and matching[0].evidence_sha256 == evidence_sha256
        and matching[0].validator_profile_id == validator_profile_id
        and matching[0].validation_status == "PASS"
    )


def _g2a4b_receipt_bindings_valid_v01(
    receipt: object,
    projection: ActionPacketEffectFirewallProjectionV01,
    request: _EffectRequestV01,
    decision: _EffectFirewallDecisionV01,
) -> bool:
    try:
        if (
            type(receipt) is not _KernelArtifactV01
            or _validate_kernel_artifact_v01(receipt) != ()
        ):
            return False
        plain = _kernel_artifact_to_plain_dict_v01(receipt)
        payload = plain.get("payload")
        return (
            type(payload) is dict
            and plain.get("artifact_id") == payload.get("receipt_ref")
            and plain.get("artifact_type") == "EvidenceReceipt"
            and plain.get("transaction_id") == projection.transaction_id
            and plain.get("owner_root_id") == projection.target_root_id
            and plain.get("authority_class") == "EVIDENCE_ONLY"
            and plain.get("lifecycle_state") == "RECEIPT_RECORDED"
            and payload.get("request_id") == request.request_id
            and payload.get("firewall_decision_id") == decision.decision_id
            and payload.get("capability_id") == decision.capability_id
            and payload.get("root_decision_id") == projection.root_decision_id
            and payload.get("selected_candidate_id")
            == projection.selected_candidate_id
            and payload.get("permission_ref") == projection.permission_ref
            and payload.get("adapter_id") == projection.adapter_id
            and payload.get("action_kind") == projection.action_kind
            and payload.get("scope_refs") == list(projection.scope_refs)
            and payload.get("receipt_evidence_only") is True
            and payload.get("root_confirmation_required") is True
            and payload.get("root_confirmation_created") is False
            and payload.get("future_permission_created") is False
            and payload.get("root_decision_created") is False
            and payload.get("final_output_created") is False
            and payload.get("effect_handle_exposed") is False
            and type(payload.get("real_world_effects_count")) is int
            and payload.get("real_world_effects_count") == 0
        )
    except Exception:
        return False


def _g2a4b_expected_consumed_firewall_state_sha256_v01(
    firewall: _EffectFirewallV01,
) -> str:
    plain = _effect_firewall_to_plain_dict_v01(firewall)
    counters = dict(plain["state_counters"])
    counters["consumed_capability_count"] = 1
    counters["terminal_receipt_count"] = 1
    counters["mock_effect_execution_count"] = 1
    projected = dict(plain)
    projected["state_counters"] = counters
    return _action_packet_private_component_sha256_v01(
        _ACTION_PACKET_FIREWALL_STATE_HASH_DOMAIN_V01,
        projected,
    )


def _recompute_historical_action_packet_attempt_v01(
    registry: ActionCommitPacketRegistryV02,
    context: _ActionPacketFulfillmentAttemptContextV01,
    entry: ActionPacketLifecycleEntryV01,
    pending: ActionPacketTransitionEventV01,
    *,
    validation_pass: _ActionPacketRegistryValidationPassV01,
) -> tuple[
    ActionPacketEffectFirewallProjectionV01 | None,
    _ActionPacketHistoricalEffectAuthorizationV01 | None,
    str | None,
    ActionPacketLifecycleEntryV01,
    tuple[IdempotencyDispositionEventV01, ...],
]:
    evidence = context.attempt_evidence
    pending_positions = tuple(
        index
        for index, event in enumerate(entry.transition_events)
        if event is pending
    )
    disposition_positions = tuple(
        index
        for index, event in enumerate(
            registry.idempotency_disposition_events
        )
        if (
            event.idempotency_disposition_event_id
            == evidence.latest_disposition_event_id_before
        )
    )
    if len(pending_positions) != 1 or len(disposition_positions) != 1:
        raise ValueError(
            "action_packet_registry_fulfillment_historical_view_invalid"
        )
    historical_entry = ActionPacketLifecycleEntryV01(
        root_bound_genesis=entry.root_bound_genesis,
        transition_registry_id=entry.transition_registry_id,
        transition_events=entry.transition_events[
            : pending_positions[0] + 1
        ],
    )
    disposition_prefix = registry.idempotency_disposition_events[
        : disposition_positions[0] + 1
    ]
    if evidence.disposition_history_sha256_before != (
        _action_packet_disposition_history_sha256_v01(
            disposition_prefix
        )
    ):
        raise ValueError(
            "action_packet_registry_fulfillment_historical_view_invalid"
        )
    try:
        projection = (
            _build_action_packet_effect_projection_from_historical_view_v01(
                registry_id=registry.registry_id,
                entry=historical_entry,
                disposition_history=disposition_prefix,
                terminal_receipt_packet_ids=(),
                terminal_receipt_idempotency_keys=(),
                packet_id=evidence.packet_id,
                corridor=context.corridor,
                corridor_step=context.corridor_step,
                current_dependency_observations=(
                    context.current_dependency_observations
                ),
                logical_time_bridge=context.logical_time_bridge,
                eligibility_evaluation_time=(
                    evidence.eligibility_evaluation_time
                ),
                eligibility_evaluation_time_source=(
                    evidence.eligibility_evaluation_time_source
                ),
                eligibility_evaluation_context_id=(
                    evidence.eligibility_evaluation_context_id
                ),
                validation_pass=validation_pass,
            )
        )
    except ValueError as exc:
        replay_reason = _stable_exception_reason_v01(
            exc,
            fallback="action_packet_effect_historical_replay_invalid",
        )
        if (
            context.projection is None
            and evidence.outcome_class == "PRE_FULFILLMENT_BLOCKED"
            and evidence.reason_code == replay_reason
        ):
            return (
                None,
                None,
                replay_reason,
                historical_entry,
                disposition_prefix,
            )
        raise ValueError(
            "action_packet_registry_fulfillment_historical_replay_invalid"
        ) from None
    if (
        type(context.projection)
        is not ActionPacketEffectFirewallProjectionV01
        or context.projection != projection
        or evidence.projection_sha256
        != _action_packet_effect_projection_sha256_v01(projection)
    ):
        raise ValueError(
            "action_packet_registry_fulfillment_projection_invalid"
        )
    historical_authorization = (
        _historical_action_packet_effect_authorization_v01(
            historical_entry,
            projection,
        )
    )
    return (
        projection,
        historical_authorization,
        None,
        historical_entry,
        disposition_prefix,
    )


def _validate_registry_fulfillment_attempt_histories_v01(
    registry: ActionCommitPacketRegistryV02,
    *,
    entry_by_packet: dict[str, ActionPacketLifecycleEntryV01],
    transition_by_id: dict[str, ActionPacketTransitionEventV01],
    validation_pass: _ActionPacketRegistryValidationPassV01,
    reasons: list[str],
) -> None:
    contexts = registry.action_packet_fulfillment_attempt_contexts
    seen_evidence_ids: set[str] = set()
    state_by_attempt: dict[str, dict[str, object]] = {}
    terminal_context_by_attempt: dict[
        str,
        _ActionPacketFulfillmentAttemptContextV01,
    ] = {}
    transition_context_counts: dict[str, int] = {}
    for context in contexts:
        evidence = context.attempt_evidence
        if not validate_action_packet_fulfillment_attempt_evidence_v01(
            evidence
        )[0]:
            _reason_v01(
                reasons,
                "action_packet_registry_fulfillment_evidence_invalid",
            )
            continue
        if evidence.attempt_evidence_id in seen_evidence_ids:
            _reason_v01(
                reasons,
                "action_packet_registry_fulfillment_evidence_duplicate",
            )
        seen_evidence_ids.add(evidence.attempt_evidence_id)
        attempt_state = state_by_attempt.setdefault(
            evidence.execution_attempt_id,
            {
                "count": 0,
                "contexts": set(),
                "adapter_calls": 0,
                "terminal": False,
            },
        )
        attempt_state["count"] = int(attempt_state["count"]) + 1
        if evidence.attempt_observation_ordinal != attempt_state["count"]:
            _reason_v01(
                reasons,
                "action_packet_registry_fulfillment_ordinal_invalid",
            )
        evaluation_contexts = attempt_state["contexts"]
        if (
            type(evaluation_contexts) is set
            and evidence.eligibility_evaluation_context_id
            in evaluation_contexts
        ):
            _reason_v01(
                reasons,
                "action_packet_registry_fulfillment_observation_duplicate",
            )
        if type(evaluation_contexts) is set:
            evaluation_contexts.add(
                evidence.eligibility_evaluation_context_id
            )
        if attempt_state["terminal"]:
            _reason_v01(
                reasons,
                "action_packet_registry_fulfillment_context_after_terminal",
            )
        attempt_state["adapter_calls"] = (
            int(attempt_state["adapter_calls"])
            + evidence.adapter_call_count
        )
        if int(attempt_state["adapter_calls"]) > 1:
            _reason_v01(
                reasons,
                "action_packet_registry_fulfillment_multiple_invocations",
            )
        if evidence.outcome_class in {
            "CONSUMED",
            "NOT_CONSUMED",
            "UNCERTAIN",
        }:
            attempt_state["terminal"] = True
            terminal_context_by_attempt[evidence.execution_attempt_id] = (
                context
            )
        try:
            entry = _unique_lifecycle_entry_from_validation_pass_v01(
                validation_pass,
                evidence.packet_id,
            )
        except ValueError:
            _reason_v01(
                reasons,
                "action_packet_registry_fulfillment_packet_missing",
            )
            continue
        pending = transition_by_id.get(evidence.pending_transition_event_id)
        if not (
            type(pending) is ActionPacketTransitionEventV01
            and pending in entry.transition_events
            and pending.transition_rule_id == "g2a_t03_pending"
            and pending.execution_attempt_id == evidence.execution_attempt_id
            and pending.packet_id == evidence.packet_id
            and evidence.registry_id_before == registry.registry_id
            and evidence.attempt_evaluation_time == pending.evaluation_time
            and evidence.attempt_evaluation_time_source
            == pending.evaluation_time_source
            and evidence.attempt_evaluation_context_id
            == pending.evaluation_context_id
            and evidence.disposition_before == "RESERVED"
            and evidence.reservation_owner_packet_id_before
            == evidence.packet_id
        ):
            _reason_v01(
                reasons,
                "action_packet_registry_fulfillment_attempt_binding_invalid",
            )
            continue
        matching_latest_positions = tuple(
            index
            for index, disposition in enumerate(
                registry.idempotency_disposition_events
            )
            if disposition.idempotency_disposition_event_id
            == evidence.latest_disposition_event_id_before
        )
        if (
            len(matching_latest_positions) != 1
            or evidence.disposition_history_sha256_before
            != _action_packet_disposition_history_sha256_v01(
                registry.idempotency_disposition_events[
                    : matching_latest_positions[0] + 1
                ]
            )
        ):
            _reason_v01(
                reasons,
                "action_packet_registry_fulfillment_disposition_history_invalid",
            )
        if not (
            type(context.corridor) is ContractFulfillmentCorridorV01
            and type(context.corridor_step) is CorridorStepV01
            and type(context.current_dependency_observations) is tuple
            and all(
                validate_action_dependency_current_observation_v01(item)[0]
                for item in context.current_dependency_observations
            )
            and type(context.logical_time_bridge) is LogicalTimeBridgeV01
            and validate_logical_time_bridge_v01(
                context.logical_time_bridge
            )[0]
            and evidence.corridor_id == context.corridor.corridor_id
            and evidence.corridor_step_id == context.corridor_step.step_id
            and evidence.logical_time_bridge_id
            == context.logical_time_bridge.bridge_id
            and evidence.dependency_observation_ids
            == _g2a4b_dependency_observation_ids_v01(
                context.current_dependency_observations
            )
        ):
            _reason_v01(
                reasons,
                "action_packet_registry_fulfillment_context_binding_invalid",
            )
        try:
            (
                projection,
                historical_authorization,
                _replay_reason,
                historical_entry,
                _disposition_prefix,
            ) = _recompute_historical_action_packet_attempt_v01(
                registry,
                context,
                entry,
                pending,
                validation_pass=validation_pass,
            )
        except ValueError:
            _reason_v01(
                reasons,
                "action_packet_registry_fulfillment_historical_replay_invalid",
            )
            continue
        if projection is None:
            if any(
                item is not None
                for item in (
                    context.request,
                    context.decision,
                    context.receipt,
                )
            ):
                _reason_v01(
                    reasons,
                    "action_packet_registry_fulfillment_component_invalid",
                )
            continue
        if (
            type(historical_authorization)
            is not _ActionPacketHistoricalEffectAuthorizationV01
            or type(context.request) is not _EffectRequestV01
            or type(context.decision) is not _EffectFirewallDecisionV01
        ):
            _reason_v01(
                reasons,
                "action_packet_registry_fulfillment_component_invalid",
            )
            continue
        request = historical_authorization.request
        decision = historical_authorization.decision
        expected_before_hash = (
            historical_authorization.firewall_state_sha256_before
        )
        if not (
            request == context.request
            and decision == context.decision
            and historical_authorization.firewall_id == evidence.firewall_id
            and request.request_id == evidence.request_id
            and decision.decision_id == evidence.decision_id
            and historical_authorization.expected_capability_id
            == evidence.capability_id
            and evidence.adapter_id == projection.adapter_id
            and evidence.action_kind == projection.action_kind
        ):
            _reason_v01(
                reasons,
                "action_packet_registry_fulfillment_component_invalid",
            )
            continue
        if evidence.outcome_class == "FIREWALL_BLOCKED":
            if not (
                decision.decision == _EFFECT_DECISION_BLOCKED_FAIL_CLOSED
                and decision.capability_id is None
                and evidence.reason_code == decision.reason_code
            ):
                _reason_v01(
                    reasons,
                    "action_packet_registry_fulfillment_reason_invalid",
                )
            continue
        if (
            decision.decision != _EFFECT_DECISION_ALLOW_MOCK_EFFECT
            or evidence.firewall_state_sha256_before
            != expected_before_hash
        ):
            _reason_v01(
                reasons,
                "action_packet_registry_fulfillment_component_invalid",
            )
            continue
        if evidence.outcome_class == "CONSUMED":
            if (
                evidence.reason_code != "mock_effect_consumed"
                or evidence.firewall_state_sha256_after
                != historical_authorization.firewall_state_sha256_consumed
            ):
                _reason_v01(
                    reasons,
                    "action_packet_registry_fulfillment_reason_invalid",
                )
        elif evidence.outcome_class == "NOT_CONSUMED":
            if not (
                evidence.reason_code
                in _ACTION_PACKET_NONCONSUMING_EXECUTION_REASONS_V01
                and evidence.firewall_state_sha256_after
                == expected_before_hash
            ):
                _reason_v01(
                    reasons,
                    "action_packet_registry_fulfillment_reason_invalid",
                )
        elif evidence.outcome_class == "UNCERTAIN":
            if (
                evidence.reason_code
                not in _ACTION_PACKET_UNCERTAIN_EXECUTION_REASONS_V01
                or (
                    evidence.reason_code == "effect_request_expired"
                    and evidence.firewall_state_sha256_after
                    == expected_before_hash
                )
            ):
                _reason_v01(
                    reasons,
                    "action_packet_registry_fulfillment_reason_invalid",
                )
        else:
            _reason_v01(
                reasons,
                "action_packet_registry_fulfillment_reason_invalid",
            )
        if evidence.outcome_class == "CONSUMED":
            try:
                expected_receipt_plain = (
                    _expected_action_packet_effect_receipt_plain_v01(
                        historical_entry,
                        projection,
                        request,
                        decision,
                    )
                )
                receipt_valid = (
                    type(context.receipt) is _KernelArtifactV01
                    and _validate_kernel_artifact_v01(context.receipt) == ()
                    and _kernel_artifact_to_plain_dict_v01(context.receipt)
                    == expected_receipt_plain
                    and evidence.receipt_ref
                    == expected_receipt_plain["artifact_id"]
                    and evidence.receipt_sha256
                    == _action_packet_private_component_sha256_v01(
                        _ACTION_PACKET_EFFECT_RECEIPT_HASH_DOMAIN_V01,
                        expected_receipt_plain,
                    )
                    and _g2a4b_receipt_bindings_valid_v01(
                        context.receipt,
                        projection,
                        request,
                        decision,
                    )
                )
            except Exception:
                receipt_valid = False
            if not receipt_valid:
                _reason_v01(
                    reasons,
                    "action_packet_registry_fulfillment_receipt_invalid",
                )
        elif context.receipt is not None:
            _reason_v01(
                reasons,
                "action_packet_registry_fulfillment_receipt_invalid",
            )
    a4b_transitions = tuple(
        transition
        for transition in transition_by_id.values()
        if any(
            binding.validator_profile_id
            == ACTION_PACKET_FULFILLMENT_ATTEMPT_EVIDENCE_PROFILE_ID_V01
            for binding in transition.transition_evidence_bindings
        )
    )
    for transition in a4b_transitions:
        matching = tuple(
            context
            for context in contexts
            if (
                context.attempt_evidence.execution_attempt_id
                == transition.execution_attempt_id
                and context.attempt_evidence.packet_id
                == transition.packet_id
                and context.attempt_evidence.outcome_class
                == {
                    "g2a_t04_fulfill_mock": "CONSUMED",
                    "g2a_t24_nonconsuming_failure": "NOT_CONSUMED",
                    "g2a_t26_uncertain_adapter_outcome": "UNCERTAIN",
                }.get(transition.transition_rule_id)
            )
        )
        if len(matching) != 1:
            _reason_v01(
                reasons,
                "action_packet_registry_fulfillment_bundle_missing",
            )
            continue
        context = matching[0]
        evidence = context.attempt_evidence
        evidence_hash = evidence.attempt_evidence_id[
            len(ACTION_PACKET_FULFILLMENT_ATTEMPT_EVIDENCE_PREFIX_V01) :
        ]
        latest_id = evidence.latest_disposition_event_id_before
        latest_hash = (
            latest_id[len(IDEMPOTENCY_DISPOSITION_EVENT_PREFIX_V01) :]
            if latest_id is not None
            else ""
        )
        attempt_codes = {
            "g2a_t04_fulfill_mock": (
                "effect_consumption_evidence_valid",
            ),
            "g2a_t24_nonconsuming_failure": (
                "adapter_invocation_evidence_valid",
                "effect_nonconsumption_evidence_valid",
            ),
            "g2a_t26_uncertain_adapter_outcome": (
                "adapter_invocation_evidence_valid",
                "effect_outcome_unresolved",
            ),
        }[transition.transition_rule_id]
        if any(
            not _g2a4b_transition_binding_matches_v01(
                transition,
                code,
                evidence_ref=evidence.attempt_evidence_id,
                evidence_sha256=evidence_hash,
                validator_profile_id=(
                    ACTION_PACKET_FULFILLMENT_ATTEMPT_EVIDENCE_PROFILE_ID_V01
                ),
            )
            for code in attempt_codes
        ) or not _g2a4b_transition_binding_matches_v01(
            transition,
            "idempotency_reservation_owned",
            evidence_ref=latest_id or "",
            evidence_sha256=latest_hash,
            validator_profile_id=IDEMPOTENCY_DISPOSITION_EVENT_PROFILE_ID_V01,
        ):
            _reason_v01(
                reasons,
                "action_packet_registry_fulfillment_transition_binding_invalid",
            )
        if transition.transition_rule_id == "g2a_t24_nonconsuming_failure":
            if not _g2a4b_transition_binding_matches_v01(
                transition,
                "latest_disposition_event_binding_valid",
                evidence_ref=latest_id or "",
                evidence_sha256=latest_hash,
                validator_profile_id=(
                    IDEMPOTENCY_DISPOSITION_EVENT_PROFILE_ID_V01
                ),
            ):
                _reason_v01(
                    reasons,
                    "action_packet_registry_fulfillment_transition_binding_invalid",
                )
        if transition.transition_rule_id == "g2a_t04_fulfill_mock":
            if (
                context.receipt is None
                or evidence.receipt_sha256 is None
                or not _g2a4b_transition_binding_matches_v01(
                    transition,
                    "mock_adapter_result_valid",
                    evidence_ref=context.receipt.artifact_id,
                    evidence_sha256=evidence.receipt_sha256,
                    validator_profile_id="effect_firewall_receipt_v01",
                )
            ):
                _reason_v01(
                    reasons,
                    "action_packet_registry_fulfillment_transition_binding_invalid",
                )
        transition_context_counts[transition.transition_event_id] = 1
    for attempt_id, context in terminal_context_by_attempt.items():
        evidence = context.attempt_evidence
        expected_rule = {
            "CONSUMED": "g2a_t04_fulfill_mock",
            "NOT_CONSUMED": "g2a_t24_nonconsuming_failure",
            "UNCERTAIN": "g2a_t26_uncertain_adapter_outcome",
        }[evidence.outcome_class]
        matching = tuple(
            transition
            for transition in a4b_transitions
            if (
                transition.execution_attempt_id == attempt_id
                and transition.transition_rule_id == expected_rule
            )
        )
        if len(matching) != 1:
            _reason_v01(
                reasons,
                "action_packet_registry_fulfillment_bundle_missing",
            )
            continue
        transition = matching[0]
        dispositions = tuple(
            event
            for event in registry.idempotency_disposition_events
            if transition.transition_event_id
            in event.cause_transition_event_ids
        )
        expected_class = {
            "CONSUMED": "CONSUME",
            "NOT_CONSUMED": None,
            "UNCERTAIN": "UNCERTAIN_CLOSE",
        }[evidence.outcome_class]
        if (
            expected_class is None
            and dispositions
            or expected_class is not None
            and (
                len(dispositions) != 1
                or dispositions[0].event_class != expected_class
            )
        ):
            _reason_v01(
                reasons,
                "action_packet_registry_fulfillment_disposition_invalid",
            )
        receipt_events = tuple(
            event
            for event in entry_by_packet[evidence.packet_id].transition_events
            if (
                event.transition_rule_id == "g2a_t05_receipt"
                and event.execution_attempt_id == attempt_id
                and any(
                    binding.validator_profile_id
                    == "effect_firewall_receipt_v01"
                    for binding in event.transition_evidence_bindings
                )
            )
        )
        if evidence.outcome_class != "CONSUMED" and receipt_events:
            _reason_v01(
                reasons,
                "action_packet_registry_fulfillment_receipt_invalid",
            )
        if len(receipt_events) > 1:
            _reason_v01(
                reasons,
                "action_packet_registry_fulfillment_receipt_duplicate",
            )
        if receipt_events:
            receipt_event = receipt_events[0]
            if (
                context.receipt is None
                or evidence.receipt_sha256 is None
                or receipt_event.receipt_ref != context.receipt.artifact_id
                or not _g2a4b_transition_binding_matches_v01(
                    receipt_event,
                    "terminal_receipt_valid",
                    evidence_ref=context.receipt.artifact_id,
                    evidence_sha256=evidence.receipt_sha256,
                    validator_profile_id="effect_firewall_receipt_v01",
                )
                or not _g2a4b_transition_binding_matches_v01(
                    receipt_event,
                    "fulfillment_consumption_evidence_valid",
                    evidence_ref=transition.transition_event_id,
                    evidence_sha256=transition.transition_event_id[
                        len(ACTION_PACKET_TRANSITION_EVENT_PREFIX_V01) :
                    ],
                    validator_profile_id=(
                        ACTION_PACKET_TRANSITION_EVENT_PROFILE_ID_V01
                    ),
                )
            ):
                _reason_v01(
                    reasons,
                    "action_packet_registry_fulfillment_receipt_invalid",
                )


def _g2a4b_fallback_attempt_evidence_v01(
    registry: ActionCommitPacketRegistryV02,
    entry: ActionPacketLifecycleEntryV01,
    pending: ActionPacketTransitionEventV01,
    state: ActionPacketLifecycleStateV01,
    *,
    ordinal: int,
    corridor: ContractFulfillmentCorridorV01,
    corridor_step: CorridorStepV01,
    observations: tuple[ActionDependencyCurrentObservationV01, ...],
    logical_time_bridge: LogicalTimeBridgeV01,
    eligibility_evaluation_time: int,
    eligibility_evaluation_time_source: str,
    eligibility_evaluation_context_id: str,
    projection: ActionPacketEffectFirewallProjectionV01,
    preparation: _ActionPacketEffectAttemptPreparationV01,
    outcome_class: str,
    reason_code: str,
    firewall_state_sha256_before: str,
    firewall_state_sha256_after: str,
    receipt: _KernelArtifactV01 | None,
) -> ActionPacketFulfillmentAttemptEvidenceV01:
    relation = {
        "CONSUMED": "CORRIDOR_INVOCATION_CONSUMED",
        "UNCERTAIN": "CORRIDOR_INVOCATION_UNCERTAIN",
    }[outcome_class]
    decision = preparation.decision
    request = preparation.request
    return build_action_packet_fulfillment_attempt_evidence_v01(
        packet_id=entry.root_bound_genesis.packet_identity.packet_id,
        registry_id_before=registry.registry_id,
        pending_transition_event_id=pending.transition_event_id,
        execution_attempt_id=pending.execution_attempt_id,
        attempt_observation_ordinal=ordinal,
        corridor_id=corridor.corridor_id,
        corridor_step_id=corridor_step.step_id,
        logical_time_bridge_id=logical_time_bridge.bridge_id,
        dependency_observation_ids=(
            _g2a4b_dependency_observation_ids_v01(observations)
        ),
        projection_sha256=(
            _action_packet_effect_projection_sha256_v01(projection)
        ),
        firewall_id=preparation.firewall.firewall_id,
        request_id=request.request_id,
        decision_id=decision.decision_id,
        capability_id=decision.capability_id,
        adapter_id=projection.adapter_id,
        action_kind=projection.action_kind,
        invocation_relation_code=relation,
        outcome_class=outcome_class,
        reason_code=reason_code,
        adapter_invoked=True,
        adapter_call_count=1,
        firewall_state_sha256_before=firewall_state_sha256_before,
        firewall_state_sha256_after=firewall_state_sha256_after,
        receipt_ref=receipt.artifact_id if receipt is not None else None,
        receipt_sha256=(
            _action_packet_effect_receipt_sha256_v01(receipt)
            if receipt is not None
            else None
        ),
        disposition_before=state.idempotency_disposition,
        reservation_owner_packet_id_before=(
            state.reservation_owner_packet_id
        ),
        latest_disposition_event_id_before=(
            state.latest_disposition_event_id
        ),
        disposition_history_sha256_before=(
            _action_packet_disposition_history_sha256_v01(
                registry.idempotency_disposition_events
            )
        ),
        attempt_evaluation_time=pending.evaluation_time,
        attempt_evaluation_time_source=pending.evaluation_time_source,
        attempt_evaluation_context_id=pending.evaluation_context_id,
        eligibility_evaluation_time=eligibility_evaluation_time,
        eligibility_evaluation_time_source=(
            eligibility_evaluation_time_source
        ),
        eligibility_evaluation_context_id=(
            eligibility_evaluation_context_id
        ),
        real_world_effects_count=0,
    )


def _g2a4b_prove_consumed_receipt_truth_v01(
    entry: ActionPacketLifecycleEntryV01,
    projection: ActionPacketEffectFirewallProjectionV01,
    preparation: _ActionPacketEffectAttemptPreparationV01,
    returned: object,
    execution_reason: str | None,
) -> tuple[bool, _KernelArtifactV01 | None]:
    try:
        expected = _rebuild_exact_action_packet_effect_receipt_v01(
            entry,
            projection,
            preparation.request,
            preparation.decision,
        )
        if (
            execution_reason is not None
            or type(returned) is not _KernelArtifactV01
            or returned != expected
            or _kernel_artifact_to_plain_dict_v01(returned)
            != _kernel_artifact_to_plain_dict_v01(expected)
            or _validate_kernel_artifact_v01(returned) != ()
            or _validate_effect_receipt_v01(
                firewall=preparation.firewall,
                request=preparation.request,
                decision=preparation.decision,
                receipt=returned,
            )
            != ()
            or not _g2a4b_receipt_bindings_valid_v01(
                returned,
                projection,
                preparation.request,
                preparation.decision,
            )
        ):
            return False, None
        plain = _effect_firewall_to_plain_dict_v01(preparation.firewall)
        counters = plain["state_counters"]
        if not (
            counters["consumed_capability_count"] == 1
            and counters["terminal_receipt_count"] == 1
            and counters["mock_effect_execution_count"] == 1
            and counters["real_world_effects_count"] == 0
        ):
            return False, None
        return True, returned
    except Exception:
        return False, None


def _g2a4b_classify_invoked_outcome_v01(
    *,
    consumed_truth: bool,
    receipt: _KernelArtifactV01 | None,
    returned: object,
    execution_reason: str | None,
    firewall_before_valid: bool,
    firewall_before_sha256: str,
    firewall_after_valid: bool,
    firewall_after_sha256: str,
) -> tuple[str, str, _KernelArtifactV01 | None, str, str | None]:
    if consumed_truth and receipt is not None:
        return (
            "CONSUMED",
            "mock_effect_consumed",
            receipt,
            "g2a_t04_fulfill_mock",
            "CONSUME",
        )
    if (
        execution_reason
        in _ACTION_PACKET_NONCONSUMING_EXECUTION_REASONS_V01
        and firewall_before_valid
        and firewall_after_valid
        and firewall_before_sha256 == firewall_after_sha256
        and returned is None
    ):
        return (
            "NOT_CONSUMED",
            execution_reason,
            None,
            "g2a_t24_nonconsuming_failure",
            None,
        )
    reason = (
        execution_reason
        if execution_reason in _ACTION_PACKET_UNCERTAIN_EXECUTION_REASONS_V01
        else "effect_outcome_unresolved"
    )
    return (
        "UNCERTAIN",
        reason,
        None,
        "g2a_t26_uncertain_adapter_outcome",
        "UNCERTAIN_CLOSE",
    )


def _g2a4b_assemble_invoked_outcome_bundle_v01(
    registry: ActionCommitPacketRegistryV02,
    entry: ActionPacketLifecycleEntryV01,
    pending: ActionPacketTransitionEventV01,
    state: ActionPacketLifecycleStateV01,
    *,
    ordinal: int,
    corridor: ContractFulfillmentCorridorV01,
    corridor_step: CorridorStepV01,
    observations: tuple[ActionDependencyCurrentObservationV01, ...],
    logical_time_bridge: LogicalTimeBridgeV01,
    eligibility_evaluation_time: int,
    eligibility_evaluation_time_source: str,
    eligibility_evaluation_context_id: str,
    projection: ActionPacketEffectFirewallProjectionV01,
    preparation: _ActionPacketEffectAttemptPreparationV01,
    outcome_class: str,
    reason_code: str,
    firewall_state_sha256_before: str,
    firewall_state_sha256_after: str,
    receipt: _KernelArtifactV01 | None,
    rule_id: str,
    disposition_class: str | None,
    transition_registry: ActionPacketTransitionRegistryProfileV01,
    fallback: bool,
) -> tuple[
    _ActionPacketFulfillmentAttemptContextV01,
    ActionPacketTransitionEventV01,
    IdempotencyDispositionEventV01 | None,
]:
    evidence = (
        _g2a4b_fallback_attempt_evidence_v01(
            registry,
            entry,
            pending,
            state,
            ordinal=ordinal,
            corridor=corridor,
            corridor_step=corridor_step,
            observations=observations,
            logical_time_bridge=logical_time_bridge,
            eligibility_evaluation_time=eligibility_evaluation_time,
            eligibility_evaluation_time_source=(
                eligibility_evaluation_time_source
            ),
            eligibility_evaluation_context_id=(
                eligibility_evaluation_context_id
            ),
            projection=projection,
            preparation=preparation,
            outcome_class=outcome_class,
            reason_code=reason_code,
            firewall_state_sha256_before=firewall_state_sha256_before,
            firewall_state_sha256_after=firewall_state_sha256_after,
            receipt=receipt,
        )
        if fallback
        else _g2a4b_attempt_evidence_v01(
            registry,
            entry,
            pending,
            state,
            ordinal=ordinal,
            corridor=corridor,
            corridor_step=corridor_step,
            observations=observations,
            logical_time_bridge=logical_time_bridge,
            eligibility_evaluation_time=eligibility_evaluation_time,
            eligibility_evaluation_time_source=(
                eligibility_evaluation_time_source
            ),
            eligibility_evaluation_context_id=(
                eligibility_evaluation_context_id
            ),
            projection=projection,
            preparation=preparation,
            outcome_class=outcome_class,
            reason_code=reason_code,
            adapter_invoked=True,
            firewall_state_sha256_before=firewall_state_sha256_before,
            firewall_state_sha256_after=firewall_state_sha256_after,
            receipt=receipt,
        )
    )
    transition = _g2a4b_outcome_transition_v01(
        entry,
        pending,
        state,
        evidence,
        rule_id=rule_id,
        receipt=receipt,
        transition_registry=transition_registry,
    )
    disposition = (
        _g2a4b_outcome_disposition_v01(
            state,
            transition,
            event_class=disposition_class,
        )
        if disposition_class is not None
        else None
    )
    context = _ActionPacketFulfillmentAttemptContextV01(
        attempt_evidence=evidence,
        projection=projection,
        corridor=corridor,
        corridor_step=corridor_step,
        current_dependency_observations=observations,
        logical_time_bridge=logical_time_bridge,
        request=preparation.request,
        decision=preparation.decision,
        receipt=receipt,
    )
    return context, transition, disposition


def _g2a4b_build_invoked_outcome_bundle_v01(
    registry: ActionCommitPacketRegistryV02,
    entry: ActionPacketLifecycleEntryV01,
    pending: ActionPacketTransitionEventV01,
    state: ActionPacketLifecycleStateV01,
    **kwargs: object,
) -> tuple[
    _ActionPacketFulfillmentAttemptContextV01,
    ActionPacketTransitionEventV01,
    IdempotencyDispositionEventV01 | None,
]:
    return _g2a4b_assemble_invoked_outcome_bundle_v01(
        registry,
        entry,
        pending,
        state,
        fallback=False,
        **kwargs,
    )


def _g2a4b_fallback_invoked_outcome_bundle_v01(
    registry: ActionCommitPacketRegistryV02,
    entry: ActionPacketLifecycleEntryV01,
    pending: ActionPacketTransitionEventV01,
    state: ActionPacketLifecycleStateV01,
    *,
    ordinal: int,
    corridor: ContractFulfillmentCorridorV01,
    corridor_step: CorridorStepV01,
    observations: tuple[ActionDependencyCurrentObservationV01, ...],
    logical_time_bridge: LogicalTimeBridgeV01,
    eligibility_evaluation_time: int,
    eligibility_evaluation_time_source: str,
    eligibility_evaluation_context_id: str,
    projection: ActionPacketEffectFirewallProjectionV01,
    preparation: _ActionPacketEffectAttemptPreparationV01,
    consumed_truth: bool,
    receipt: _KernelArtifactV01 | None,
    firewall_state_sha256_before: str,
    firewall_state_sha256_after: str,
    transition_registry: ActionPacketTransitionRegistryProfileV01,
) -> tuple[
    _ActionPacketFulfillmentAttemptContextV01,
    ActionPacketTransitionEventV01,
    IdempotencyDispositionEventV01 | None,
]:
    return _g2a4b_assemble_invoked_outcome_bundle_v01(
        registry,
        entry,
        pending,
        state,
        ordinal=ordinal,
        corridor=corridor,
        corridor_step=corridor_step,
        observations=observations,
        logical_time_bridge=logical_time_bridge,
        eligibility_evaluation_time=eligibility_evaluation_time,
        eligibility_evaluation_time_source=(
            eligibility_evaluation_time_source
        ),
        eligibility_evaluation_context_id=(
            eligibility_evaluation_context_id
        ),
        projection=projection,
        preparation=preparation,
        outcome_class="CONSUMED" if consumed_truth else "UNCERTAIN",
        reason_code=(
            "mock_effect_consumed"
            if consumed_truth
            else "effect_outcome_unresolved"
        ),
        firewall_state_sha256_before=firewall_state_sha256_before,
        firewall_state_sha256_after=firewall_state_sha256_after,
        receipt=receipt if consumed_truth else None,
        rule_id=(
            "g2a_t04_fulfill_mock"
            if consumed_truth
            else "g2a_t26_uncertain_adapter_outcome"
        ),
        disposition_class=(
            "CONSUME" if consumed_truth else "UNCERTAIN_CLOSE"
        ),
        transition_registry=transition_registry,
        fallback=True,
    )


def execute_action_packet_mock_fulfillment_v01(
    registry: object,
    *,
    packet_id: object,
    corridor: object,
    corridor_step: object,
    current_dependency_observations: object,
    logical_time_bridge: object,
    eligibility_evaluation_time: object,
    eligibility_evaluation_time_source: object,
    eligibility_evaluation_context_id: object,
    action_packet_transition_registry_profile: object,
) -> ActionCommitPacketRegistryV02:
    invoked = False
    try:
        validation_result = _require_valid_action_packet_registry_v01(
            registry
        )
        transition_registry = _exact_action_packet_transition_registry_v01(
            action_packet_transition_registry_profile
        )
        entry, pending, state, ordinal = _g2a4b_attempt_input_v01(
            registry,
            validation_result,
            packet_id=packet_id,
            corridor=corridor,
            corridor_step=corridor_step,
            current_dependency_observations=(
                current_dependency_observations
            ),
            logical_time_bridge=logical_time_bridge,
            eligibility_evaluation_time=eligibility_evaluation_time,
            eligibility_evaluation_time_source=(
                eligibility_evaluation_time_source
            ),
            eligibility_evaluation_context_id=(
                eligibility_evaluation_context_id
            ),
        )
        observations = current_dependency_observations
        try:
            projection = (
                _build_action_packet_effect_firewall_projection_core_v01(
                    registry,
                    packet_id=packet_id,
                    corridor=corridor,
                    corridor_step=corridor_step,
                    current_dependency_observations=observations,
                    logical_time_bridge=logical_time_bridge,
                    eligibility_evaluation_time=(
                        eligibility_evaluation_time
                    ),
                    eligibility_evaluation_time_source=(
                        eligibility_evaluation_time_source
                    ),
                    eligibility_evaluation_context_id=(
                        eligibility_evaluation_context_id
                    ),
                    registry_validation_result=validation_result,
                )
            )
        except ValueError as exc:
            reason = _stable_exception_reason_v01(
                exc,
                fallback="action_packet_pre_fulfillment_blocked",
            )
            evidence = _g2a4b_attempt_evidence_v01(
                registry,
                entry,
                pending,
                state,
                ordinal=ordinal,
                corridor=corridor,
                corridor_step=corridor_step,
                observations=observations,
                logical_time_bridge=logical_time_bridge,
                eligibility_evaluation_time=eligibility_evaluation_time,
                eligibility_evaluation_time_source=(
                    eligibility_evaluation_time_source
                ),
                eligibility_evaluation_context_id=(
                    eligibility_evaluation_context_id
                ),
                projection=None,
                preparation=None,
                outcome_class="PRE_FULFILLMENT_BLOCKED",
                reason_code=reason,
                adapter_invoked=False,
                firewall_state_sha256_before=None,
                firewall_state_sha256_after=None,
                receipt=None,
            )
            context = _ActionPacketFulfillmentAttemptContextV01(
                attempt_evidence=evidence,
                projection=None,
                corridor=corridor,
                corridor_step=corridor_step,
                current_dependency_observations=observations,
                logical_time_bridge=logical_time_bridge,
                request=None,
                decision=None,
                receipt=None,
            )
            return _g2a4b_append_context_only_v01(registry, context)
        preparation = _prepare_action_packet_effect_attempt_from_projection_v01(
            entry,
            projection,
        )
        decision = preparation.decision
        if decision.decision == _EFFECT_DECISION_BLOCKED_FAIL_CLOSED:
            evidence = _g2a4b_attempt_evidence_v01(
                registry,
                entry,
                pending,
                state,
                ordinal=ordinal,
                corridor=corridor,
                corridor_step=corridor_step,
                observations=observations,
                logical_time_bridge=logical_time_bridge,
                eligibility_evaluation_time=eligibility_evaluation_time,
                eligibility_evaluation_time_source=(
                    eligibility_evaluation_time_source
                ),
                eligibility_evaluation_context_id=(
                    eligibility_evaluation_context_id
                ),
                projection=projection,
                preparation=preparation,
                outcome_class="FIREWALL_BLOCKED",
                reason_code=decision.reason_code,
                adapter_invoked=False,
                firewall_state_sha256_before=None,
                firewall_state_sha256_after=None,
                receipt=None,
            )
            context = _ActionPacketFulfillmentAttemptContextV01(
                attempt_evidence=evidence,
                projection=projection,
                corridor=corridor,
                corridor_step=corridor_step,
                current_dependency_observations=observations,
                logical_time_bridge=logical_time_bridge,
                request=preparation.request,
                decision=decision,
                receipt=None,
            )
            return _g2a4b_append_context_only_v01(registry, context)
        if not (
            decision.decision == _EFFECT_DECISION_ALLOW_MOCK_EFFECT
            and type(decision.capability_id) is str
            and decision.capability_issued is True
        ):
            raise ValueError("action_packet_effect_authorization_invalid")
        firewall = preparation.firewall
        (
            firewall_before_valid,
            firewall_before,
            _firewall_before_plain,
        ) = _action_packet_firewall_state_observation_v01(firewall)
        if not firewall_before_valid:
            raise ValueError("action_packet_effect_firewall_state_invalid")
        receipt_ref = _action_packet_effect_receipt_ref_v01(
            packet_id=projection.packet_id,
            execution_attempt_id=projection.execution_attempt_id,
            request_id=preparation.request.request_id,
            decision_id=decision.decision_id,
            eligibility_evaluation_context_id=(
                projection.eligibility_evaluation_context_id
            ),
        )
        receipt_time_envelope = (
            _action_packet_effect_receipt_time_envelope_v01(
                entry,
                projection,
            )
        )
        returned: object = None
        execution_reason: str | None = None
        try:
            invoked = True
            returned = (_execute_mock_effect_v01)(
                firewall=firewall,
                request=preparation.request,
                decision=decision,
                current_tick=projection.current_tick,
                adapter_id=projection.adapter_id,
                action_kind=projection.action_kind,
                child_scope_refs=projection.scope_refs,
                child_expires_at_tick=projection.expires_at_tick,
                receipt_artifact_id=receipt_ref,
                time_envelope=receipt_time_envelope,
            )
        except ValueError as exc:
            execution_reason = _stable_exception_reason_v01(
                exc,
                fallback="effect_execution_unexpected_exception",
            )
            if execution_reason not in (
                _ACTION_PACKET_NONCONSUMING_EXECUTION_REASONS_V01
                + _ACTION_PACKET_UNCERTAIN_EXECUTION_REASONS_V01
            ):
                execution_reason = "effect_execution_unexpected_exception"
        except Exception:
            execution_reason = "effect_execution_unexpected_exception"
        consumed_truth, proven_receipt = (
            _g2a4b_prove_consumed_receipt_truth_v01(
                entry,
                projection,
                preparation,
                returned,
                execution_reason,
            )
        )
        try:
            (
                firewall_after_valid,
                firewall_after,
                _firewall_after_plain,
            ) = _action_packet_firewall_state_observation_v01(firewall)
        except Exception:
            firewall_after_valid = False
            firewall_after = (
                _g2a4b_expected_consumed_firewall_state_sha256_v01(
                    firewall
                )
                if consumed_truth
                else _action_packet_private_component_sha256_v01(
                    _ACTION_PACKET_FIREWALL_STATE_HASH_DOMAIN_V01,
                    {
                        "observation_class": "UNVALIDATABLE_STATE",
                        "observer_status": "FAILED",
                    },
                )
            )
        try:
            (
                outcome_class,
                reason_code,
                stored_receipt,
                rule_id,
                disposition_class,
            ) = _g2a4b_classify_invoked_outcome_v01(
                consumed_truth=consumed_truth,
                receipt=proven_receipt,
                returned=returned,
                execution_reason=execution_reason,
                firewall_before_valid=firewall_before_valid,
                firewall_before_sha256=firewall_before,
                firewall_after_valid=firewall_after_valid,
                firewall_after_sha256=firewall_after,
            )
            context, transition, disposition = (
                _g2a4b_build_invoked_outcome_bundle_v01(
                    registry,
                    entry,
                    pending,
                    state,
                    ordinal=ordinal,
                    corridor=corridor,
                    corridor_step=corridor_step,
                    observations=observations,
                    logical_time_bridge=logical_time_bridge,
                    eligibility_evaluation_time=eligibility_evaluation_time,
                    eligibility_evaluation_time_source=(
                        eligibility_evaluation_time_source
                    ),
                    eligibility_evaluation_context_id=(
                        eligibility_evaluation_context_id
                    ),
                    projection=projection,
                    preparation=preparation,
                    outcome_class=outcome_class,
                    reason_code=reason_code,
                    firewall_state_sha256_before=firewall_before,
                    firewall_state_sha256_after=firewall_after,
                    receipt=stored_receipt,
                    rule_id=rule_id,
                    disposition_class=disposition_class,
                    transition_registry=transition_registry,
                )
            )
        except Exception:
            context, transition, disposition = (
                _g2a4b_fallback_invoked_outcome_bundle_v01(
                    registry,
                    entry,
                    pending,
                    state,
                    ordinal=ordinal,
                    corridor=corridor,
                    corridor_step=corridor_step,
                    observations=observations,
                    logical_time_bridge=logical_time_bridge,
                    eligibility_evaluation_time=eligibility_evaluation_time,
                    eligibility_evaluation_time_source=(
                        eligibility_evaluation_time_source
                    ),
                    eligibility_evaluation_context_id=(
                        eligibility_evaluation_context_id
                    ),
                    projection=projection,
                    preparation=preparation,
                    consumed_truth=consumed_truth,
                    receipt=proven_receipt,
                    firewall_state_sha256_before=firewall_before,
                    firewall_state_sha256_after=firewall_after,
                    transition_registry=transition_registry,
                )
            )
        proposed = _g2a4b_build_outcome_registry_v01(
            registry,
            entry,
            context,
            transition,
            disposition,
        )
        _require_valid_action_packet_registry_v01(proposed)
        return proposed
    except ValueError as exc:
        raise ValueError(
            _stable_exception_reason_v01(
                exc,
                fallback=(
                    "action_packet_post_invocation_outcome_invalid"
                    if invoked
                    else "action_packet_mock_fulfillment_invalid"
                ),
            )
        ) from None
    except Exception:
        raise ValueError(
            "action_packet_post_invocation_outcome_invalid"
            if invoked
            else "action_packet_mock_fulfillment_invalid"
        ) from None


def observe_action_packet_effect_receipt_v01(
    registry: object,
    *,
    packet_id: object,
    attempt_evidence_id: object,
    receipt_evaluation_time: object,
    receipt_evaluation_time_source: object,
    action_packet_transition_registry_profile: object,
) -> ActionCommitPacketRegistryV02:
    try:
        validation_result = _require_valid_action_packet_registry_v01(
            registry
        )
        transition_registry = _exact_action_packet_transition_registry_v01(
            action_packet_transition_registry_profile
        )
        if (
            not validate_prefixed_sha256_identity_v01(
                attempt_evidence_id,
                prefix=(
                    ACTION_PACKET_FULFILLMENT_ATTEMPT_EVIDENCE_PREFIX_V01
                ),
            )[0]
            or not validate_signed_int64_v01(receipt_evaluation_time)[0]
            or not validate_identity_text_v01(
                receipt_evaluation_time_source
            )[0]
        ):
            raise ValueError("action_packet_receipt_observation_invalid")
        validation_pass = validation_result.validation_pass
        if type(validation_pass) is not _ActionPacketRegistryValidationPassV01:
            raise ValueError("action_packet_receipt_observation_invalid")
        entry = _unique_lifecycle_entry_from_validation_pass_v01(
            validation_pass,
            packet_id,
        )
        matching = tuple(
            context
            for context in registry.action_packet_fulfillment_attempt_contexts
            if (
                context.attempt_evidence.attempt_evidence_id
                == attempt_evidence_id
                and context.attempt_evidence.packet_id == packet_id
                and context.attempt_evidence.outcome_class == "CONSUMED"
            )
        )
        if len(matching) != 1:
            raise ValueError("action_packet_receipt_observation_invalid")
        context = matching[0]
        evidence = context.attempt_evidence
        receipt = context.receipt
        try:
            exact_receipt = _rebuild_exact_action_packet_effect_receipt_v01(
                entry,
                context.projection,
                context.request,
                context.decision,
            )
            receipt_valid = (
                type(context.projection)
                is ActionPacketEffectFirewallProjectionV01
                and type(context.request) is _EffectRequestV01
                and type(context.decision) is _EffectFirewallDecisionV01
                and type(receipt) is _KernelArtifactV01
                and receipt == exact_receipt
                and _kernel_artifact_to_plain_dict_v01(receipt)
                == _kernel_artifact_to_plain_dict_v01(exact_receipt)
                and evidence.receipt_ref == exact_receipt.artifact_id
                and evidence.receipt_sha256
                == _action_packet_effect_receipt_sha256_v01(exact_receipt)
                and _validate_kernel_artifact_v01(receipt) == ()
                and _g2a4b_receipt_bindings_valid_v01(
                    receipt,
                    context.projection,
                    context.request,
                    context.decision,
                )
            )
        except Exception:
            receipt_valid = False
        if not receipt_valid:
            raise ValueError("action_packet_receipt_observation_invalid")
        state = _derive_action_packet_lifecycle_state_unchecked_v01(
            entry,
            registry.idempotency_disposition_events,
        )
        consumed = entry.transition_events[-1] if entry.transition_events else None
        if not (
            state.lifecycle_state == "FULFILLED_MOCK"
            and state.idempotency_disposition == "CONSUMED"
            and state.reservation_owner_packet_id == packet_id
            and type(consumed) is ActionPacketTransitionEventV01
            and consumed.transition_rule_id == "g2a_t04_fulfill_mock"
            and consumed.execution_attempt_id == evidence.execution_attempt_id
            and packet_id not in registry.terminal_receipt_packet_ids
            and state.idempotency_key
            not in registry.terminal_receipt_idempotency_keys
        ):
            raise ValueError("action_packet_receipt_observation_invalid")
        receipt_transition = _g2a4b_receipt_transition_v01(
            entry,
            consumed,
            evidence,
            receipt,
            receipt_evaluation_time=receipt_evaluation_time,
            receipt_evaluation_time_source=receipt_evaluation_time_source,
            transition_registry=transition_registry,
        )
        disposition = _g2a4b_outcome_disposition_v01(
            state,
            receipt_transition,
            event_class="RECEIPT_CONFIRM",
        )
        updated_entry = ActionPacketLifecycleEntryV01(
            root_bound_genesis=entry.root_bound_genesis,
            transition_registry_id=entry.transition_registry_id,
            transition_events=entry.transition_events
            + (receipt_transition,),
        )
        entries = tuple(
            updated_entry if candidate is entry else candidate
            for candidate in registry.action_packet_lifecycle_entries
        )
        proposed = _registry_with_g2a_histories_v01(
            registry,
            lifecycle_entries=entries,
            disposition_events=registry.idempotency_disposition_events
            + (disposition,),
            terminal_receipt_packet_ids=_tuple_add_unique(
                registry.terminal_receipt_packet_ids,
                packet_id,
            ),
            terminal_receipt_idempotency_keys=_tuple_add_unique(
                registry.terminal_receipt_idempotency_keys,
                state.idempotency_key,
            ),
        )
        _require_valid_action_packet_registry_v01(proposed)
        return proposed
    except ValueError as exc:
        raise ValueError(
            _stable_exception_reason_v01(
                exc,
                fallback="action_packet_receipt_observation_invalid",
            )
        ) from None
    except Exception:
        raise ValueError("action_packet_receipt_observation_invalid") from None


def _action_packet_replay_canonical_value_v01(value: object) -> object:
    if value is None or type(value) in {bool, int, str}:
        return value
    if type(value) is tuple:
        return tuple(
            _action_packet_replay_canonical_value_v01(item)
            for item in value
        )
    if isinstance(value, Mapping):
        if any(type(key) is not str for key in value):
            raise ValueError("action_packet_replay_material_invalid")
        return tuple(
            (
                key,
                _action_packet_replay_canonical_value_v01(value[key]),
            )
            for key in sorted(value)
        )
    if _is_dataclass(value) and not isinstance(value, type):
        return tuple(
            (
                field.name,
                _action_packet_replay_canonical_value_v01(
                    getattr(value, field.name)
                ),
            )
            for field in _dataclass_fields(value)
        )
    raise ValueError("action_packet_replay_material_invalid")


def _action_packet_replay_history_sha256_v01(
    domain: str,
    material: object,
) -> str:
    return domain_separated_sha256_hex_v01(
        domain=domain,
        payload=canonical_json_bytes_v01(material),
    )


def _action_packet_replay_histories_v01(
    registry: ActionCommitPacketRegistryV02,
    entry: ActionPacketLifecycleEntryV01,
) -> tuple[
    tuple[IdempotencyDispositionEventV01, ...],
    tuple[_ActionPacketInvalidationContextV01, ...],
    tuple[_ActionPacketFulfillmentAttemptContextV01, ...],
]:
    packet_id = entry.root_bound_genesis.packet_identity.packet_id
    idempotency_key = (
        entry.root_bound_genesis.canonical_projection
        .idempotency_identity.idempotency_key
    )
    dispositions = tuple(
        event
        for event in registry.idempotency_disposition_events
        if event.idempotency_key == idempotency_key
    )
    invalidations = tuple(
        context
        for context in registry.action_packet_invalidation_contexts
        if (
            context.invalidation_evidence.packet_id == packet_id
            or context.supersession_successor_packet_id == packet_id
        )
    )
    fulfillments = tuple(
        context
        for context in registry.action_packet_fulfillment_attempt_contexts
        if context.attempt_evidence.packet_id == packet_id
    )
    return dispositions, invalidations, fulfillments


def _action_packet_replay_t24_pass_v01(
    entry: ActionPacketLifecycleEntryV01,
    disposition_history: tuple[IdempotencyDispositionEventV01, ...],
    fulfillments: tuple[_ActionPacketFulfillmentAttemptContextV01, ...],
) -> bool:
    for transition_index, transition in enumerate(entry.transition_events):
        if transition.transition_rule_id != "g2a_t24_nonconsuming_failure":
            continue
        preceding_pending = tuple(
            (index, event)
            for index, event in enumerate(
                entry.transition_events[:transition_index]
            )
            if (
                event.transition_rule_id == "g2a_t03_pending"
                and event.execution_attempt_id
                == transition.execution_attempt_id
            )
        )
        if (
            len(preceding_pending) != 1
            or preceding_pending[0][0] != transition_index - 1
            or transition.previous_transition_event_id
            != preceding_pending[0][1].transition_event_id
            or transition.receipt_ref is not None
        ):
            return False
        attempt_contexts = tuple(
            context
            for context in fulfillments
            if (
                context.attempt_evidence.execution_attempt_id
                == transition.execution_attempt_id
            )
        )
        contexts = tuple(
            context
            for context in attempt_contexts
            if (
                context.attempt_evidence.outcome_class == "NOT_CONSUMED"
            )
        )
        claims_a4b_profile = any(
            binding.validator_profile_id
            == ACTION_PACKET_FULFILLMENT_ATTEMPT_EVIDENCE_PROFILE_ID_V01
            for binding in transition.transition_evidence_bindings
        )
        if claims_a4b_profile:
            if len(contexts) != 1:
                return False
            evidence = contexts[0].attempt_evidence
            latest_disposition_event_id = (
                evidence.latest_disposition_event_id_before
            )
        else:
            if attempt_contexts:
                return False
            evidence = None
            latest_bindings = tuple(
                binding
                for binding in transition.transition_evidence_bindings
                if binding.evidence_code
                == "latest_disposition_event_binding_valid"
            )
            if len(latest_bindings) != 1:
                return False
            latest_disposition_event_id = latest_bindings[0].evidence_ref
        matching_latest = tuple(
            index
            for index, event in enumerate(disposition_history)
            if (
                event.idempotency_disposition_event_id
                == latest_disposition_event_id
            )
        )
        if len(matching_latest) != 1:
            return False
        prefix = disposition_history[: matching_latest[0] + 1]
        state = _derive_idempotency_disposition_unchecked_v01(
            prefix,
            transition.idempotency_key,
        )
        transition_state = _derive_action_packet_lifecycle_state_unchecked_v01(
            ActionPacketLifecycleEntryV01(
                root_bound_genesis=entry.root_bound_genesis,
                transition_registry_id=entry.transition_registry_id,
                transition_events=entry.transition_events[
                    : transition_index + 1
                ],
            ),
            prefix,
        )
        if not (
            _t24_latest_disposition_binding_is_exact_v01(
                transition,
                state,
            )
            and state.disposition == "RESERVED"
            and state.reservation_owner_packet_id == transition.packet_id
            and state.latest_disposition_event_id
            == latest_disposition_event_id
            and transition_state.lifecycle_state == "FAILED"
            and transition_state.failed_provenance
            == "FAILED_NON_CONSUMING"
            and transition_state.idempotency_disposition == "RESERVED"
            and transition_state.reservation_owner_packet_id
            == transition.packet_id
            and transition_state.latest_disposition_event_id
            == latest_disposition_event_id
            and not any(
                event.execution_attempt_id
                == transition.execution_attempt_id
                and event.receipt_ref is not None
                for event in entry.transition_events
            )
            and not any(
                transition.transition_event_id
                in event.cause_transition_event_ids
                for event in disposition_history
            )
        ):
            return False
        if evidence is None:
            reservation_bindings = tuple(
                binding
                for binding in transition.transition_evidence_bindings
                if binding.evidence_code == "idempotency_reservation_owned"
            )
            if len(reservation_bindings) != 1:
                return False
            reservation_binding = reservation_bindings[0]
            latest_digest = latest_disposition_event_id[
                len(IDEMPOTENCY_DISPOSITION_EVENT_PREFIX_V01) :
            ]
            if (
                reservation_binding.validator_profile_id
                == IDEMPOTENCY_DISPOSITION_EVENT_PROFILE_ID_V01
                and (
                    reservation_binding.evidence_ref
                    != latest_disposition_event_id
                    or reservation_binding.evidence_sha256 != latest_digest
                )
            ) or (
                reservation_binding.validator_profile_id
                == ACTION_PACKET_FULFILLMENT_ATTEMPT_EVIDENCE_PROFILE_ID_V01
                or reservation_binding.validation_status != "PASS"
            ):
                return False
            continue
        if not (
            evidence.reason_code
            in _ACTION_PACKET_NONCONSUMING_EXECUTION_REASONS_V01
            and evidence.adapter_call_count == 1
            and evidence.receipt_ref is None
            and evidence.disposition_history_sha256_before
            == _action_packet_disposition_history_sha256_v01(prefix)
        ):
            return False
    return True


def _action_packet_replay_core_v01(
    registry: ActionCommitPacketRegistryV02,
    *,
    packet_id: object,
    action_packet_transition_registry_profile: object,
    validation_result: _ActionPacketRegistryValidationResultV02,
) -> ActionPacketLifecycleReplayReportV01:
    validation_pass = validation_result.validation_pass
    if (
        not validation_result.valid
        or type(validation_pass)
        is not _ActionPacketRegistryValidationPassV01
        or validation_pass.registry is not registry
    ):
        raise ValueError("action_packet_replay_registry_invalid")
    transition_registry = _exact_action_packet_transition_registry_v01(
        action_packet_transition_registry_profile
    )
    entry = _unique_lifecycle_entry_from_validation_pass_v01(
        validation_pass,
        packet_id,
    )
    if entry.transition_registry_id != transition_registry.transition_registry_id:
        raise ValueError("action_packet_lifecycle_registry_id_mismatch")
    root_bound = entry.root_bound_genesis
    root_projection = root_bound.root_decision_projection
    canonical = root_bound.canonical_projection
    rebuilt_packet = build_action_commit_packet_identity_v01(
        candidate=canonical.authorization_candidate,
        source_root_decision_id=(
            root_projection.root_decision_result.decision_id
        ),
        source_root_decision_hash=(
            root_projection.source_root_decision_hash
        ),
    )
    idempotency = canonical.idempotency_identity
    rebuilt_idempotency = build_action_idempotency_identity_v01(
        owning_effect_root_id=idempotency.owning_effect_root_id,
        transaction_id=idempotency.transaction_id,
        root_owned_intent_id=idempotency.root_owned_intent_id,
        logical_effect_class=idempotency.logical_effect_class,
        normalized_subject_scope=idempotency.normalized_subject_scope,
        normalized_target_scope=idempotency.normalized_target_scope,
        normalized_business_object_identity=(
            idempotency.normalized_business_object_identity
        ),
        normalized_consequential_effect_parameters=(
            idempotency.normalized_consequential_effect_parameters
        ),
        logical_effect_namespace=idempotency.logical_effect_namespace,
    )
    if (
        rebuilt_packet != root_bound.packet_identity
        or rebuilt_idempotency != idempotency
    ):
        raise ValueError("action_packet_replay_identity_invalid")
    dispositions, invalidations, fulfillments = (
        _action_packet_replay_histories_v01(registry, entry)
    )
    state = _derive_action_packet_lifecycle_state_unchecked_v01(
        entry,
        registry.idempotency_disposition_events,
    )
    transitions = tuple(
        ActionPacketRecordedTransitionReplayV01(
            transition_event_id=event.transition_event_id,
            transition_rule_id=event.transition_rule_id,
            source_state=event.source_state,
            target_state=event.target_state,
            evaluation_time=event.evaluation_time,
            evaluation_time_source=event.evaluation_time_source,
            evaluation_context_id=event.evaluation_context_id,
            execution_attempt_id=event.execution_attempt_id,
            effect_consumption_class=event.effect_consumption_class,
            receipt_ref=event.receipt_ref,
        )
        for event in entry.transition_events
    )
    transition_material = tuple(
        action_packet_transition_event_material_v01(event)
        for event in entry.transition_events
    )
    disposition_material = tuple(
        idempotency_disposition_event_material_v01(event)
        for event in dispositions
    )
    invalidation_material = tuple(
        _action_packet_replay_canonical_value_v01(context)
        for context in invalidations
    )
    fulfillment_material = tuple(
        _action_packet_replay_canonical_value_v01(context)
        for context in fulfillments
    )
    terminal_attempts = tuple(
        context.attempt_evidence.execution_attempt_id
        for context in fulfillments
        if context.attempt_evidence.adapter_invoked
    )
    report = ActionPacketLifecycleReplayReportV01(
        replay_profile_id=ACTION_PACKET_LIFECYCLE_REPLAY_PROFILE_ID_V01,
        registry_id=registry.registry_id,
        packet_id=root_bound.packet_identity.packet_id,
        transition_registry_id=entry.transition_registry_id,
        source_root_decision_id=(
            root_projection.root_decision_result.decision_id
        ),
        source_root_decision_hash=(
            root_projection.source_root_decision_hash
        ),
        rebuilt_packet_id=rebuilt_packet.packet_id,
        rebuilt_idempotency_key=rebuilt_idempotency.idempotency_key,
        recorded_transitions=transitions,
        disposition_event_ids=tuple(
            event.idempotency_disposition_event_id
            for event in dispositions
        ),
        invalidation_evidence_ids=tuple(
            context.invalidation_evidence.invalidation_evidence_id
            for context in invalidations
        ),
        fulfillment_attempt_evidence_ids=tuple(
            context.attempt_evidence.attempt_evidence_id
            for context in fulfillments
        ),
        reconstructed_state=state,
        transition_history_sha256=(
            _action_packet_replay_history_sha256_v01(
                _ACTION_PACKET_REPLAY_TRANSITION_HISTORY_HASH_DOMAIN_V01,
                transition_material,
            )
        ),
        disposition_history_sha256=(
            _action_packet_replay_history_sha256_v01(
                _ACTION_PACKET_REPLAY_DISPOSITION_HISTORY_HASH_DOMAIN_V01,
                disposition_material,
            )
        ),
        invalidation_history_sha256=(
            _action_packet_replay_history_sha256_v01(
                _ACTION_PACKET_REPLAY_INVALIDATION_HISTORY_HASH_DOMAIN_V01,
                invalidation_material,
            )
        ),
        fulfillment_history_sha256=(
            _action_packet_replay_history_sha256_v01(
                _ACTION_PACKET_REPLAY_FULFILLMENT_HISTORY_HASH_DOMAIN_V01,
                fulfillment_material,
            )
        ),
        historical_temporal_replay_pass=all(
            _action_packet_transition_temporal_reason_v01(root_bound, event)
            is None
            for event in entry.transition_events
        ),
        t24_reserved_history_replay_pass=(
            _action_packet_replay_t24_pass_v01(
                entry,
                registry.idempotency_disposition_events,
                fulfillments,
            )
        ),
        distinct_firewall_attempt_replay_pass=(
            len(terminal_attempts) == len(set(terminal_attempts))
        ),
        registry_unchanged=True,
        creates_authority=False,
        creates_permission=False,
        creates_packet=False,
        creates_receipt=False,
        adapter_calls=0,
        real_world_effects_count=0,
    )
    if not (
        report.historical_temporal_replay_pass
        and report.t24_reserved_history_replay_pass
        and report.distinct_firewall_attempt_replay_pass
    ):
        raise ValueError("action_packet_replay_history_invalid")
    return report


def replay_action_packet_lifecycle_history_v01(
    registry: object,
    *,
    packet_id: object,
    action_packet_transition_registry_profile: object = None,
) -> ActionPacketLifecycleReplayReportV01:
    try:
        validation_result = _require_valid_action_packet_registry_v01(
            registry
        )
        return _action_packet_replay_core_v01(
            registry,
            packet_id=packet_id,
            action_packet_transition_registry_profile=(
                action_packet_transition_registry_profile
            ),
            validation_result=validation_result,
        )
    except ValueError as exc:
        raise ValueError(
            _stable_exception_reason_v01(
                exc,
                fallback="action_packet_lifecycle_replay_invalid",
            )
        ) from None
    except Exception:
        raise ValueError("action_packet_lifecycle_replay_invalid") from None


def _action_packet_lifecycle_replay_report_shape_v01(
    report: object,
) -> bool:
    if type(report) is not ActionPacketLifecycleReplayReportV01:
        return False
    try:
        return bool(
            report.replay_profile_id
            == ACTION_PACKET_LIFECYCLE_REPLAY_PROFILE_ID_V01
            and type(report.registry_id) is str
            and type(report.packet_id) is str
            and type(report.transition_registry_id) is str
            and type(report.source_root_decision_id) is str
            and type(report.source_root_decision_hash) is str
            and type(report.rebuilt_packet_id) is str
            and type(report.rebuilt_idempotency_key) is str
            and type(report.recorded_transitions) is tuple
            and all(
                type(item) is ActionPacketRecordedTransitionReplayV01
                and type(item.transition_event_id) is str
                and type(item.transition_rule_id) is str
                and type(item.source_state) is str
                and type(item.target_state) is str
                and type(item.evaluation_time) is int
                and type(item.evaluation_time_source) is str
                and type(item.evaluation_context_id) is str
                and (
                    item.execution_attempt_id is None
                    or type(item.execution_attempt_id) is str
                )
                and type(item.effect_consumption_class) is str
                and (
                    item.receipt_ref is None
                    or type(item.receipt_ref) is str
                )
                for item in report.recorded_transitions
            )
            and all(
                type(value) is tuple
                and all(type(item) is str for item in value)
                for value in (
                    report.disposition_event_ids,
                    report.invalidation_evidence_ids,
                    report.fulfillment_attempt_evidence_ids,
                )
            )
            and type(report.reconstructed_state)
            is ActionPacketLifecycleStateV01
            and all(
                type(value) is str
                and validate_lowercase_sha256_hex_v01(value)[0]
                for value in (
                    report.transition_history_sha256,
                    report.disposition_history_sha256,
                    report.invalidation_history_sha256,
                    report.fulfillment_history_sha256,
                )
            )
            and all(
                type(value) is bool
                for value in (
                    report.historical_temporal_replay_pass,
                    report.t24_reserved_history_replay_pass,
                    report.distinct_firewall_attempt_replay_pass,
                    report.registry_unchanged,
                    report.creates_authority,
                    report.creates_permission,
                    report.creates_packet,
                    report.creates_receipt,
                )
            )
            and type(report.adapter_calls) is int
            and type(report.real_world_effects_count) is int
            and report.registry_unchanged is True
            and report.creates_authority is False
            and report.creates_permission is False
            and report.creates_packet is False
            and report.creates_receipt is False
            and report.adapter_calls == 0
            and report.real_world_effects_count == 0
        )
    except Exception:
        return False


def validate_action_packet_lifecycle_replay_report_v01(
    report: object,
    registry: object,
    *,
    packet_id: object,
    action_packet_transition_registry_profile: object = None,
) -> tuple[bool, tuple[str, ...]]:
    if not _action_packet_lifecycle_replay_report_shape_v01(report):
        return False, ("action_packet_lifecycle_replay_report_invalid",)
    try:
        expected = replay_action_packet_lifecycle_history_v01(
            registry,
            packet_id=packet_id,
            action_packet_transition_registry_profile=(
                action_packet_transition_registry_profile
            ),
        )
        if (
            _action_packet_replay_canonical_value_v01(report)
            != _action_packet_replay_canonical_value_v01(expected)
        ):
            return False, ("action_packet_lifecycle_replay_report_mismatch",)
        return True, ()
    except ValueError as exc:
        return False, (
            _stable_exception_reason_v01(
                exc,
                fallback="action_packet_lifecycle_replay_report_invalid",
            ),
        )
    except Exception:
        return False, ("action_packet_lifecycle_replay_report_invalid",)


def _action_packet_retry_inspection_projection_v01(
    registry: ActionCommitPacketRegistryV02,
    entry: ActionPacketLifecycleEntryV01,
    *,
    corridor: object,
    corridor_step: object,
    current_dependency_observations: object,
    logical_time_bridge: object,
    evaluation_time: object,
    evaluation_time_source: object,
    evaluation_context_id: object,
    validation_pass: _ActionPacketRegistryValidationPassV01,
) -> ActionPacketEffectFirewallProjectionV01:
    if (
        entry.root_bound_genesis.canonical_projection.authority_policy
        .retry_policy
        != "NON_CONSUMING_RETRY"
    ):
        raise ValueError("retry_policy_invalid")
    latest = entry.transition_events[-1] if entry.transition_events else None
    if (
        type(latest) is not ActionPacketTransitionEventV01
        or latest.transition_rule_id != "g2a_t24_nonconsuming_failure"
    ):
        raise ValueError("action_packet_retry_not_eligible")
    pending_positions = tuple(
        index
        for index, event in enumerate(entry.transition_events)
        if (
            event.execution_attempt_id == latest.execution_attempt_id
            and event.transition_rule_id == "g2a_t03_pending"
        )
    )
    if len(pending_positions) != 1:
        raise ValueError("action_packet_retry_not_eligible")
    pending_entry = ActionPacketLifecycleEntryV01(
        root_bound_genesis=entry.root_bound_genesis,
        transition_registry_id=entry.transition_registry_id,
        transition_events=entry.transition_events[
            : pending_positions[0] + 1
        ],
    )
    return _build_action_packet_effect_projection_from_historical_view_v01(
        registry_id=registry.registry_id,
        entry=pending_entry,
        disposition_history=registry.idempotency_disposition_events,
        terminal_receipt_packet_ids=registry.terminal_receipt_packet_ids,
        terminal_receipt_idempotency_keys=(
            registry.terminal_receipt_idempotency_keys
        ),
        packet_id=entry.root_bound_genesis.packet_identity.packet_id,
        corridor=corridor,
        corridor_step=corridor_step,
        current_dependency_observations=current_dependency_observations,
        logical_time_bridge=logical_time_bridge,
        eligibility_evaluation_time=evaluation_time,
        eligibility_evaluation_time_source=evaluation_time_source,
        eligibility_evaluation_context_id=evaluation_context_id,
        validation_pass=validation_pass,
    )


def _action_packet_present_inspection_core_v01(
    registry: ActionCommitPacketRegistryV02,
    *,
    packet_id: object,
    corridor: object,
    corridor_step: object,
    current_dependency_observations: object,
    logical_time_bridge: object,
    evaluation_time: object,
    evaluation_time_source: object,
    evaluation_context_id: object,
    action_packet_transition_registry_profile: object,
    validation_result: _ActionPacketRegistryValidationResultV02,
) -> ActionPacketPresentEligibilityInspectionV01:
    if (
        not validate_signed_int64_v01(evaluation_time)[0]
        or not validate_identity_text_v01(evaluation_time_source)[0]
        or not validate_identity_text_v01(evaluation_context_id)[0]
    ):
        raise ValueError("action_packet_present_inspection_context_invalid")
    replay = _action_packet_replay_core_v01(
        registry,
        packet_id=packet_id,
        action_packet_transition_registry_profile=(
            action_packet_transition_registry_profile
        ),
        validation_result=validation_result,
    )
    validation_pass = validation_result.validation_pass
    if type(validation_pass) is not _ActionPacketRegistryValidationPassV01:
        raise ValueError("action_packet_present_inspection_registry_invalid")
    entry = _unique_lifecycle_entry_from_validation_pass_v01(
        validation_pass,
        packet_id,
    )
    state = replay.reconstructed_state
    present_executable = False
    retry_eligible = False
    reasons: tuple[str, ...]
    try:
        if state.lifecycle_state == "PENDING_FULFILLMENT":
            _build_action_packet_effect_firewall_projection_core_v01(
                registry,
                packet_id=packet_id,
                corridor=corridor,
                corridor_step=corridor_step,
                current_dependency_observations=(
                    current_dependency_observations
                ),
                logical_time_bridge=logical_time_bridge,
                eligibility_evaluation_time=evaluation_time,
                eligibility_evaluation_time_source=evaluation_time_source,
                eligibility_evaluation_context_id=evaluation_context_id,
                registry_validation_result=validation_result,
            )
            present_executable = True
            reasons = ()
        elif (
            state.lifecycle_state == "FAILED"
            and state.failed_provenance == "FAILED_NON_CONSUMING"
            and state.idempotency_disposition == "RESERVED"
            and state.reservation_owner_packet_id == packet_id
            and state.terminal_receipt_ref is None
        ):
            _action_packet_retry_inspection_projection_v01(
                registry,
                entry,
                corridor=corridor,
                corridor_step=corridor_step,
                current_dependency_observations=(
                    current_dependency_observations
                ),
                logical_time_bridge=logical_time_bridge,
                evaluation_time=evaluation_time,
                evaluation_time_source=evaluation_time_source,
                evaluation_context_id=evaluation_context_id,
                validation_pass=validation_pass,
            )
            retry_eligible = True
            reasons = ("action_packet_retry_transition_required",)
        else:
            reasons = ("action_packet_present_state_non_executable",)
    except ValueError as exc:
        reasons = (
            _stable_exception_reason_v01(
                exc,
                fallback="action_packet_present_non_executable",
            ),
        )
    report = ActionPacketPresentEligibilityInspectionV01(
        inspection_profile_id=(
            ACTION_PACKET_PRESENT_ELIGIBILITY_INSPECTION_PROFILE_ID_V01
        ),
        registry_id=registry.registry_id,
        packet_id=entry.root_bound_genesis.packet_identity.packet_id,
        evaluation_time=evaluation_time,
        evaluation_time_source=evaluation_time_source,
        evaluation_context_id=evaluation_context_id,
        historical_state=state,
        present_eligibility_status=(
            "ELIGIBLE_FOR_BOUNDED_MOCK_ATTEMPT"
            if present_executable
            else "NON_EXECUTABLE"
        ),
        present_executable=present_executable,
        retry_eligible=retry_eligible,
        reason_codes=reasons,
        transition_history_sha256=replay.transition_history_sha256,
        disposition_history_sha256=replay.disposition_history_sha256,
        historical_result_unchanged=True,
        creates_authority=False,
        creates_permission=False,
        creates_packet=False,
        creates_receipt=False,
        adapter_calls=0,
        real_world_effects_count=0,
    )
    return report


def inspect_action_packet_present_eligibility_v01(
    registry: object,
    *,
    packet_id: object,
    corridor: object,
    corridor_step: object,
    current_dependency_observations: object,
    logical_time_bridge: object,
    evaluation_time: object,
    evaluation_time_source: object,
    evaluation_context_id: object,
    action_packet_transition_registry_profile: object = None,
) -> ActionPacketPresentEligibilityInspectionV01:
    try:
        validation_result = _require_valid_action_packet_registry_v01(
            registry
        )
        return _action_packet_present_inspection_core_v01(
            registry,
            packet_id=packet_id,
            corridor=corridor,
            corridor_step=corridor_step,
            current_dependency_observations=(
                current_dependency_observations
            ),
            logical_time_bridge=logical_time_bridge,
            evaluation_time=evaluation_time,
            evaluation_time_source=evaluation_time_source,
            evaluation_context_id=evaluation_context_id,
            action_packet_transition_registry_profile=(
                action_packet_transition_registry_profile
            ),
            validation_result=validation_result,
        )
    except ValueError as exc:
        raise ValueError(
            _stable_exception_reason_v01(
                exc,
                fallback="action_packet_present_inspection_invalid",
            )
        ) from None
    except Exception:
        raise ValueError("action_packet_present_inspection_invalid") from None


def _action_packet_present_inspection_shape_v01(
    report: object,
) -> bool:
    if type(report) is not ActionPacketPresentEligibilityInspectionV01:
        return False
    try:
        return bool(
            report.inspection_profile_id
            == ACTION_PACKET_PRESENT_ELIGIBILITY_INSPECTION_PROFILE_ID_V01
            and type(report.registry_id) is str
            and type(report.packet_id) is str
            and type(report.evaluation_time) is int
            and type(report.evaluation_time_source) is str
            and type(report.evaluation_context_id) is str
            and type(report.historical_state)
            is ActionPacketLifecycleStateV01
            and type(report.present_eligibility_status) is str
            and report.present_eligibility_status
            in ACTION_PACKET_PRESENT_ELIGIBILITY_STATUSES_V01
            and type(report.present_executable) is bool
            and type(report.retry_eligible) is bool
            and type(report.reason_codes) is tuple
            and all(type(item) is str for item in report.reason_codes)
            and validate_lowercase_sha256_hex_v01(
                report.transition_history_sha256
            )[0]
            and validate_lowercase_sha256_hex_v01(
                report.disposition_history_sha256
            )[0]
            and type(report.historical_result_unchanged) is bool
            and report.historical_result_unchanged is True
            and type(report.creates_authority) is bool
            and report.creates_authority is False
            and type(report.creates_permission) is bool
            and report.creates_permission is False
            and type(report.creates_packet) is bool
            and report.creates_packet is False
            and type(report.creates_receipt) is bool
            and report.creates_receipt is False
            and type(report.adapter_calls) is int
            and report.adapter_calls == 0
            and type(report.real_world_effects_count) is int
            and report.real_world_effects_count == 0
            and (
                report.present_executable
                == (
                    report.present_eligibility_status
                    == "ELIGIBLE_FOR_BOUNDED_MOCK_ATTEMPT"
                )
            )
            and not (report.present_executable and report.retry_eligible)
        )
    except Exception:
        return False


def validate_action_packet_present_eligibility_inspection_v01(
    report: object,
    registry: object,
    *,
    packet_id: object,
    corridor: object,
    corridor_step: object,
    current_dependency_observations: object,
    logical_time_bridge: object,
    evaluation_time: object,
    evaluation_time_source: object,
    evaluation_context_id: object,
    action_packet_transition_registry_profile: object = None,
) -> tuple[bool, tuple[str, ...]]:
    if not _action_packet_present_inspection_shape_v01(report):
        return False, ("action_packet_present_inspection_report_invalid",)
    try:
        expected = inspect_action_packet_present_eligibility_v01(
            registry,
            packet_id=packet_id,
            corridor=corridor,
            corridor_step=corridor_step,
            current_dependency_observations=(
                current_dependency_observations
            ),
            logical_time_bridge=logical_time_bridge,
            evaluation_time=evaluation_time,
            evaluation_time_source=evaluation_time_source,
            evaluation_context_id=evaluation_context_id,
            action_packet_transition_registry_profile=(
                action_packet_transition_registry_profile
            ),
        )
        if (
            _action_packet_replay_canonical_value_v01(report)
            != _action_packet_replay_canonical_value_v01(expected)
        ):
            return False, (
                "action_packet_present_inspection_report_mismatch",
            )
        return True, ()
    except ValueError as exc:
        return False, (
            _stable_exception_reason_v01(
                exc,
                fallback="action_packet_present_inspection_report_invalid",
            ),
        )
    except Exception:
        return False, ("action_packet_present_inspection_report_invalid",)
