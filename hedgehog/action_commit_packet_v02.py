from __future__ import annotations

from dataclasses import dataclass


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
