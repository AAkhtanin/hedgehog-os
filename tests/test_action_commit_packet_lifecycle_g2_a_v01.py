from __future__ import annotations

import ast
import copy
from dataclasses import dataclass, fields, replace
from decimal import Decimal
from functools import wraps
import inspect
import pickle
from pathlib import Path

import pytest

import hedgehog.action_commit_packet_v02 as acp
import hedgehog.kernel.abi_v01 as kernel_abi
import hedgehog.kernel.effect_firewall_v01 as effect_firewall
from hedgehog.kernel.integrity_replay_v01 import (
    canonical_json_bytes_v01,
    domain_separated_sha256_hex_v01,
)
import hedgehog.kernel.root_decision_v01 as root_decision
import hedgehog.kernel.semantic_work_v01 as semantic_work
import hedgehog.kernel.transition_registry_v01 as transition_registry
import hedgehog.kernel.trust_model_v01 as trust_model


ROOT_ID = "root:supplier"
TRANSACTION_ID = "transaction:inv_2042"
PERMISSION_REF = "permission:supplier_a_payment"
LOGICAL_NAMESPACE = "supplier.payment.v01"
BUSINESS_NAMESPACE = "supplier.payment_slot.v01"
CORRIDOR_CLASS = "supplier_a_mock_payment_corridor"
TEMPORAL_POLICY = "packet_ttl_v01"
EVALUATION_TIME = 1783470600
EVALUATION_TIME_SOURCE = "explicit_test_evaluation_time"
EVALUATION_CONTEXT_ID = "evaluation_context:g2a1_supplier_projection"
G2A2A_PACKET_ID = "acp_v02:" + "a" * 64
G2A2A_IDEMPOTENCY_KEY = "idem:action_v01:" + "b" * 64
G2A2A_PREVIOUS_EVENT_ID = "acpt_v01:" + "c" * 64
G2A2A_EVIDENCE_SHA256 = "d" * 64
G2A2A_ROOT_DECISION_REF = "e" * 64
G2A2A_DEPENDENCY_FINGERPRINT = "f" * 64
G2A2A_TEMPORAL_FINGERPRINT = "0" * 64
G2A2A_EVALUATION_CONTEXT_ID = "evaluation_context:g2a2a"
G2A2A_ATTEMPT_RULE_IDS = {
    "g2a_t03_pending",
    "g2a_t04_fulfill_mock",
    "g2a_t05_receipt",
    "g2a_t24_nonconsuming_failure",
    "g2a_t26_uncertain_adapter_outcome",
}
G2A3A_REVOCATION_CANDIDATE_ID = (
    "revocation_candidate_v01:"
    "fb56318c926658ca635e62f247ec014eea25e7967f0cd10a94fb0f3c7e38f259"
)
G2A3A_SUPERSESSION_CANDIDATE_ID = (
    "supersession_candidate_v01:"
    "4700c804f164e0a1cdec58754a2b481e36d6fa78a9a252b7df731a3045ce8cd8"
)
G2A3A_REVOCATION_DECISION_INPUT_ID = (
    "17f52b82929629beb5feacff9497c1f91808c5400f7ff4bb21c07a03f1c98e9d"
)
G2A3A_REVOCATION_DECISION_ID = (
    "07a2b27c6f1359ebabf3ca60949af713d13633e09aaaed3701e1e8c0c8ce72d2"
)
G2A3A_REVOCATION_DECISION_HASH = (
    "34b85f5db52ec2956f931535119b09ec9095ec1ebd2c72abe324e2f01a632c52"
)
G2A3A_ACCEPTED_REVOCATION_BINDING_ID = (
    "accepted_revocation_v01:"
    "4b36644dbd15910bb594b887182c9f978e9ae1f1cfcb65c6f9787b77810dddec"
)
G2A3A_SUPERSESSION_DECISION_INPUT_ID = (
    "e0d29be44df4855bb2f056cde680a446a832dc3c59a0bea55539c278255c9014"
)
G2A3A_SUPERSESSION_DECISION_ID = (
    "a425c949e2308d538af04c4cc76838477a63e512214589f6f100b72679785269"
)
G2A3A_SUPERSESSION_DECISION_HASH = (
    "df9869ef0897246616aec0d0ad89c5a4abb9133d820906242b361b9c340d445b"
)
G2A3A_ACCEPTED_SUPERSESSION_BINDING_ID = (
    "accepted_supersession_v01:"
    "b50cf2ad2d77cbc07e38d24c616a496f11c13246a36a976d6737cabedf5afb0c"
)
G2A3A_INVALIDATION_IDS = {
    "DEPENDENCY_CHANGED": (
        "5884d3bb8028d07b05e26cecd92932a5504012d80f12616c259dadf273a32e59"
    ),
    "DEPENDENCY_STALE": (
        "9c808ce27d3e07c7fa20e046ba1322be9c2e61fc0263b181944d2689da13f103"
    ),
    "ROOT_BOUND_KILL_SWITCH": (
        "846449494c3a6d35a8963ef44dd315752e9a29586f99314acdf3f9bebdd2dc4e"
    ),
    "MANUAL_CANCEL_EVIDENCE": (
        "ca0910dfd1e92237e4738dc84b039edefa66083f94064ac1dfb85a7694de48dd"
    ),
    "ROOT_REVOCATION": (
        "b4ece25573cbd03472f1b2eb3962c208f1febd597bdd984a736599e76e3979eb"
    ),
    "ROOT_SUPERSESSION": (
        "48af8605f4b7465a136b93932eebb6311c47f3bcc0695d0be0e8ae40f392d92b"
    ),
}
G2A3A_SAME_EFFECT_NONRENEWAL_VECTOR = {
    "successor_authorization_candidate_id": (
        "root_packet_authorization_v01:"
        "0d6832f1a0cc27c8f94347c077ebdfeb8419b3193674418e68db8635202e8e8c"
    ),
    "successor_packet_id": (
        "acp_v02:"
        "330fb12be53d2cddfb9aa9485498525ce44223f0bbc5f40ab411957fced30c1e"
    ),
    "successor_source_decision_id": (
        "ff2a60d3c7190a42dc3bee46deaec39c77f51b8f5ed766132c0a8e68eaf1efd6"
    ),
    "supersession_candidate_id": (
        "supersession_candidate_v01:"
        "e91cc209a388ac2154191d8b8a87ad7914b47590c302a1b48cbf52c157674b34"
    ),
    "supersession_root_decision_id": (
        "2c5384093f2153b54911dbcf16851a9dac8868a92067b34967c0edac226ddbfe"
    ),
    "supersession_root_decision_hash": (
        "b64757ca11a26381b6507e90ce27c8719c860b1803c75e957245d6e081755885"
    ),
    "accepted_supersession_binding_id": (
        "accepted_supersession_v01:"
        "655186dc5b5be2c41f71e13c2b31fc4f466e45900b243319a4be08f2800edfa7"
    ),
}
G2A3A_MATERIAL_EFFECT_SUPERSESSION_VECTOR = {
    "successor_stable_intent_id": (
        "root_logical_intent_v01:"
        "8fa35e0fd9067fed90fb3daf9ce570228c74ca0011b285f489515f24193710ff"
    ),
    "successor_idempotency_key": (
        "idem:action_v01:"
        "3baa1b7bb7bbe73274460782876c83abc6481fd41f2fb8067f1f8618715dd8f8"
    ),
    "successor_authorization_candidate_id": (
        "root_packet_authorization_v01:"
        "a265f1516b4d659c49f8310d37d2f49df6995234fe4e0284011fc88fb1303b6f"
    ),
    "successor_packet_id": (
        "acp_v02:"
        "7e4a2e853869688eb4b8c05d390bbed1e73710fdf1895ec0f12cea81169222d6"
    ),
    "successor_source_decision_id": (
        "3502d36fa799d9261da4b2f3b39e955479a12e0eca0bc5edd7e9013fc1156b12"
    ),
    "supersession_candidate_id": (
        "supersession_candidate_v01:"
        "b44deaaac68669a9ae787d315e58a5c6328788d106f8bfbe16c65da935c235cf"
    ),
    "supersession_root_decision_id": (
        "81e096b73376e89d4cdaa7d846baf9bc19ae23a820613234890377d319671e8a"
    ),
    "supersession_root_decision_hash": (
        "3451f9bba7dc260cda150ac3c9f4f1e24c2918672834ce3db03edfe9899a88f2"
    ),
    "accepted_supersession_binding_id": (
        "accepted_supersession_v01:"
        "52b85248c7fbb17cd5ce6ff79cc0b52ab61ca258023ef05eba7051a06b7a766f"
    ),
}
G2A3B2_VECTOR = {
    "t20_transition_event_id": (
        "acpt_v01:"
        "9a7d460488262edd55d1cf0598905c60bccaa108d0fc4a2465743bdae71afd60"
    ),
    "t22_transition_event_id": (
        "acpt_v01:"
        "e8c3175ae9e156aba98947a0783d81f1722cec9486f6354d297c33edbe5d6f1b"
    ),
    "branch_a_successor_t01_id": (
        "acpt_v01:"
        "304c2e1b422fb05ab2b0dd01d5213328adf772b15f47716a4c8c58a950b683e0"
    ),
    "branch_a_reserve_id": (
        "idem_event_v01:"
        "1ee5fd74111dfdecc9ea61fbf380c6379839bb0fe52dc2d8564e74c724a498b3"
    ),
    "active_transfer_renewal_id": (
        "idem_event_v01:"
        "fc08b71782a7b3b8cbbef9e4c9bea6f7eb21c3f335f8b5fed5c4c20562a0b926"
    ),
    "active_transfer_supersession_id": (
        "idem_event_v01:"
        "8da3c2c7ed1b6c312df36456adc890280c1161f9e24111c9f13dbcc3b89cc64c"
    ),
    "terminal_transfer_renewal_id": (
        "idem_event_v01:"
        "a72e07795af98c7872973fe9d9a15c1d47f2b66137571000759e2593e00a5e18"
    ),
    "terminal_transfer_supersession_id": (
        "idem_event_v01:"
        "60ad70b478971eab5546ab59b602cb4c9c335ced7dce4891c26057238281cb22"
    ),
    "material_successor_t01_id": (
        "acpt_v01:"
        "ff9c3ba48ec578a5dd8746d7d8360c751b684c3cddd145d6db1dc15e84bd305b"
    ),
    "material_distinct_key_reserve_id": (
        "idem_event_v01:"
        "07b9673546df21f33c4771ea0fc21783df12721dc613fccd6728ae4d504fa892"
    ),
}


@dataclass(frozen=True)
class _RootBoundFixtureV01:
    canonical_projection: acp.SupplierActionCommitPacketCanonicalProjectionV01
    semantic_request: semantic_work.SemanticWorkRequestV01
    root_review_packet: semantic_work.RootReviewPacketV01
    root_decision_kernel: root_decision.RootDecisionKernelV01
    root_decision_input: root_decision.RootDecisionInputV01
    root_decision_result: root_decision.RootDecisionResultV01
    root_projection: acp.RootDecisionCandidateProjectionV01
    root_bound_projection: (
        acp.SupplierRootBoundActionCommitPacketV02ProjectionV01
    )


@dataclass(frozen=True)
class _G2A3AFixtureV01:
    predecessor: acp.SupplierRootBoundActionCommitPacketV02ProjectionV01
    successor: acp.SupplierRootBoundActionCommitPacketV02ProjectionV01
    revocation_candidate: acp.RevocationCandidateV01
    revocation_root_projection: acp.RootDecisionCandidateProjectionV01
    accepted_revocation_binding: acp.AcceptedRevocationBindingV01
    supersession_candidate: acp.SupersessionCandidateV01
    supersession_root_projection: acp.RootDecisionCandidateProjectionV01
    accepted_supersession_binding: acp.AcceptedSupersessionBindingV01


def _dependency(
    *,
    dependency_id: str = "dependency:invoice_2042",
    content_sha256: str = "a" * 64,
    requirement_class: str = "MANDATORY",
    root_id: str = ROOT_ID,
) -> acp.DependencySetCandidateV01:
    record = acp.build_dependency_set_candidate_record_v01(
        dependency_id=dependency_id,
        dependency_class="INVOICE_EVIDENCE",
        evidence_ref="evidence:invoice_2042",
        content_sha256=content_sha256,
        requirement_class=requirement_class,
        time_envelope_id="time_envelope:invoice_2042",
        freshness_policy_id="freshness_policy:invoice_v01",
        source_provenance_refs=("source:invoice_2042",),
        expected_accepting_local_root_id=root_id,
    )
    return acp.build_dependency_set_candidate_v01(
        dependency_records=(record,)
    )


def _policy(
    *,
    policy_version: str = "supplier_policy_v01",
    root_id: str = ROOT_ID,
    retry_policy: str = "NON_CONSUMING_RETRY",
    logical_namespace: str = LOGICAL_NAMESPACE,
    effect_classes: tuple[str, ...] = ("PAYMENT",),
    business_namespaces: tuple[str, ...] = (BUSINESS_NAMESPACE,),
    corridor_classes: tuple[str, ...] = (CORRIDOR_CLASS,),
) -> acp.ActionAuthorityPolicyProfileV01:
    return acp.build_action_authority_policy_profile_v01(
        policy_version=policy_version,
        owning_local_root_id=root_id,
        authority_rule_refs=("authority_rule:supplier_a_payment",),
        kill_switch_condition_refs=("kill_switch:manual_cancel",),
        retry_policy=retry_policy,
        supersession_policy="ROOT_DECISION_ONLY",
        logical_effect_namespace=logical_namespace,
        allowed_logical_effect_classes=effect_classes,
        allowed_business_object_namespaces=business_namespaces,
        allowed_corridor_classes=corridor_classes,
    )


def _projection(
    *,
    packet: acp.ActionCommitPacketV02 | None = None,
    transaction_id: str = TRANSACTION_ID,
    root_id: str = ROOT_ID,
    permission_ref: str = PERMISSION_REF,
    selected_action: str = acp.ACTION_MOCK_SUPPLIER_A_PAYMENT_ORDER,
    logical_namespace: str = LOGICAL_NAMESPACE,
    business_namespace: str = BUSINESS_NAMESPACE,
    corridor_class: str = CORRIDOR_CLASS,
    policy: acp.ActionAuthorityPolicyProfileV01 | None = None,
    dependency: acp.DependencySetCandidateV01 | None = None,
    evaluation_time: int = EVALUATION_TIME,
    evaluation_time_source: str = EVALUATION_TIME_SOURCE,
    evaluation_context_id: str = EVALUATION_CONTEXT_ID,
    predecessor_packet_id: str | None = None,
    supersession_reason_class: str | None = None,
) -> acp.SupplierActionCommitPacketCanonicalProjectionV01:
    return acp.build_supplier_action_commit_packet_canonical_projection_v01(
        packet or acp.build_supplier_a_mock_action_commit_packet_fixture_v02(),
        transaction_id=transaction_id,
        owning_local_root_id=root_id,
        canonical_permission_ref=permission_ref,
        selected_legacy_action=selected_action,
        logical_effect_namespace=logical_namespace,
        business_object_namespace=business_namespace,
        corridor_class=corridor_class,
        adapter_version=acp.PRE_G2A_ADAPTER_VERSION_V01,
        temporal_policy_version=TEMPORAL_POLICY,
        authority_policy=policy or _policy(root_id=root_id),
        dependency_candidate=dependency or _dependency(root_id=root_id),
        evaluation_time=evaluation_time,
        evaluation_time_source=evaluation_time_source,
        evaluation_context_id=evaluation_context_id,
        predecessor_packet_id=predecessor_packet_id,
        supersession_reason_class=supersession_reason_class,
    )


def _g2a2a_registry(
) -> transition_registry.ActionPacketTransitionRegistryProfileV01:
    return (
        transition_registry.build_action_packet_transition_registry_profile_v01()
    )


def _g2a2a_attempt() -> acp.ActionExecutionAttemptIdentityV01:
    return acp.build_action_execution_attempt_identity_v01(
        packet_id=G2A2A_PACKET_ID,
        idempotency_key=G2A2A_IDEMPOTENCY_KEY,
        attempt_ordinal=1,
        evaluation_context_id=G2A2A_EVALUATION_CONTEXT_ID,
    )


def _g2a2a_bindings(
    rule_id: str,
) -> tuple[acp.TransitionEvidenceBindingV01, ...]:
    registry = _g2a2a_registry()
    rule = transition_registry.lookup_action_packet_transition_rule_v01(
        registry=registry,
        transition_rule_id=rule_id,
    )
    return tuple(
        acp.build_transition_evidence_binding_v01(
            action_packet_transition_registry_profile=registry,
            transition_rule_id=rule_id,
            evidence_code=evidence_code,
            evidence_ref=f"evidence:{evidence_code}",
            evidence_sha256=G2A2A_EVIDENCE_SHA256,
            validator_profile_id="validator:g2a2a",
        )
        for evidence_code in rule.required_evidence_codes
    )


def _g2a2a_event(
    rule_id: str,
) -> acp.ActionPacketTransitionEventV01:
    registry = _g2a2a_registry()
    rule = transition_registry.lookup_action_packet_transition_rule_v01(
        registry=registry,
        transition_rule_id=rule_id,
    )
    return acp.build_action_packet_transition_event_v01(
        action_packet_transition_registry_profile=registry,
        transition_rule_id=rule_id,
        packet_id=G2A2A_PACKET_ID,
        idempotency_key=G2A2A_IDEMPOTENCY_KEY,
        previous_transition_event_id=(
            None
            if rule_id == "g2a_t01_activate_root_authorization"
            else G2A2A_PREVIOUS_EVENT_ID
        ),
        owning_local_root_id=ROOT_ID,
        root_decision_ref=(
            None
            if rule.root_decision_requirement_code == "NONE"
            else G2A2A_ROOT_DECISION_REF
        ),
        transition_evidence_bindings=_g2a2a_bindings(rule_id),
        dependency_set_candidate_fingerprint=(
            G2A2A_DEPENDENCY_FINGERPRINT
        ),
        temporal_authority_fingerprint=G2A2A_TEMPORAL_FINGERPRINT,
        evaluation_time=EVALUATION_TIME,
        evaluation_time_source=EVALUATION_TIME_SOURCE,
        evaluation_context_id=G2A2A_EVALUATION_CONTEXT_ID,
        execution_attempt_identity=(
            _g2a2a_attempt()
            if rule_id in G2A2A_ATTEMPT_RULE_IDS
            else None
        ),
        receipt_ref="receipt:g2a2a" if rule_id == "g2a_t05_receipt" else None,
    )


def _mutate_supplier_source_packet(
    packet: acp.ActionCommitPacketV02,
    mutation: str,
) -> acp.ActionCommitPacketV02:
    if mutation == "subject":
        return replace(
            packet,
            scope=replace(
                packet.scope,
                allowed_subjects=("supplier_a_alternate",),
            ),
        )
    if mutation == "creditor":
        return replace(
            packet,
            scope=replace(packet.scope, creditor_ref="creditor:alternate"),
        )
    if mutation == "payment_slot":
        return replace(
            packet,
            scope=replace(
                packet.scope,
                payment_slot_ref="payment_slot:bank_a_mock:alternate",
            ),
        )
    if mutation == "missing_action":
        return replace(
            packet,
            scope=replace(
                packet.scope,
                allowed_actions=(acp.ACTION_MOCK_SUPPLIER_A_PAYMENT_ORDER,),
            ),
        )
    if mutation == "missing_adapter":
        return replace(
            packet,
            scope=replace(
                packet.scope,
                allowed_adapters=(acp.ADAPTER_MOCK_BANK_SANDBOX,),
            ),
        )
    if mutation == "adapter_kind":
        return replace(
            packet,
            adapter_binding=replace(
                packet.adapter_binding,
                adapter_kind="mock_bank_alternate",
            ),
        )
    if mutation == "amount":
        return replace(
            packet,
            scope=replace(packet.scope, amount="1300.00"),
        )
    if mutation == "currency":
        return replace(
            packet,
            scope=replace(packet.scope, currency="GBP"),
        )
    if mutation == "ttl":
        return replace(
            packet,
            ttl=replace(
                packet.ttl,
                expires_at="2026-07-08T00:45:00Z",
                ttl_seconds=2700,
            ),
        )
    if mutation == "issued_time":
        return replace(
            packet,
            ttl=replace(
                packet.ttl,
                created_at="2026-07-08T00:15:00Z",
                ttl_seconds=2700,
            ),
        )
    if mutation == "expiry_time":
        return replace(
            packet,
            ttl=replace(
                packet.ttl,
                expires_at="2026-07-08T01:15:00Z",
                ttl_seconds=4500,
            ),
        )
    if mutation == "raw_compatibility":
        return replace(
            packet,
            scope=replace(
                packet.scope,
                forbidden_actions=(
                    *packet.scope.forbidden_actions,
                    "audit_only_action",
                ),
            ),
        )
    if mutation == "human_approval":
        return replace(
            packet,
            human_approval_ref="human_approval:alternate_scope",
        )
    if mutation == "advisory_lineage":
        return replace(
            packet,
            drs_refs=("drs:alternate",),
            avf_refs=("avf:alternate",),
            bsep_ref="bsep:alternate",
        )
    raise AssertionError(f"unknown source mutation: {mutation}")


def _rebuild_projection_with_consequential_parameters(
    projection: acp.SupplierActionCommitPacketCanonicalProjectionV01,
    consequential: acp.ActionConsequentialEffectParametersProfileV01,
) -> acp.SupplierActionCommitPacketCanonicalProjectionV01:
    effect = acp.project_consequential_effect_parameters_v01(
        effect_class="PAYMENT",
        consequential_parameters=consequential,
    )
    effect_fingerprint = acp.build_action_effect_parameters_fingerprint_v01(
        effect
    )
    logical = acp.build_root_owned_logical_effect_intent_v01(
        owning_effect_root_id=projection.owning_local_root_id,
        transaction_id=projection.transaction_id,
        logical_effect_class="PAYMENT",
        normalized_subject_scope=projection.normalized_subject_scope,
        normalized_target_scope=projection.normalized_target_scope,
        normalized_business_object_identity=projection.business_object_identity,
        normalized_consequential_effect_parameters=consequential,
        logical_effect_namespace=projection.logical_intent.logical_effect_namespace,
    )
    idempotency = acp.build_action_idempotency_identity_v01(
        owning_effect_root_id=projection.owning_local_root_id,
        transaction_id=projection.transaction_id,
        root_owned_intent_id=logical.root_owned_intent_id,
        logical_effect_class="PAYMENT",
        normalized_subject_scope=projection.normalized_subject_scope,
        normalized_target_scope=projection.normalized_target_scope,
        normalized_business_object_identity=projection.business_object_identity,
        normalized_consequential_effect_parameters=consequential,
        logical_effect_namespace=logical.logical_effect_namespace,
    )
    base = projection.authorization_candidate
    candidate = acp.build_root_bound_packet_authorization_candidate_v01(
        owning_local_root_id=base.owning_local_root_id,
        transaction_id=base.transaction_id,
        root_owned_intent_id=logical.root_owned_intent_id,
        effect_class=base.effect_class,
        normalized_subject_scope=base.normalized_subject_scope,
        normalized_target_scope=base.normalized_target_scope,
        normalized_permission_scope=base.normalized_permission_scope,
        normalized_effect_parameters_fingerprint=effect_fingerprint,
        corridor_class=base.corridor_class,
        adapter_binding=base.adapter_binding,
        dependency_set_candidate_fingerprint=(
            base.dependency_set_candidate_fingerprint
        ),
        temporal_authority_fingerprint=base.temporal_authority_fingerprint,
        policy_version=base.policy_version,
        authority_policy_fingerprint=base.authority_policy_fingerprint,
        predecessor_packet_id=base.predecessor_packet_id,
        supersession_reason_class=base.supersession_reason_class,
    )
    return replace(
        projection,
        normalized_effect_parameters=effect,
        normalized_effect_parameters_fingerprint=effect_fingerprint,
        consequential_effect_parameters=consequential,
        logical_intent=logical,
        idempotency_identity=idempotency,
        authorization_candidate=candidate,
    )


def _rebuild_logical(
    projection: acp.SupplierActionCommitPacketCanonicalProjectionV01,
    *,
    root_id: str | None = None,
    transaction_id: str | None = None,
    effect_class: str | None = None,
    subject: acp.ActionSubjectScopeProfileV01 | None = None,
    target: acp.ActionTargetScopeProfileV01 | None = None,
    business: acp.ActionBusinessObjectIdentityProfileV01 | None = None,
    consequential: (
        acp.ActionConsequentialEffectParametersProfileV01 | None
    ) = None,
    namespace: str | None = None,
) -> tuple[
    acp.RootOwnedLogicalEffectIntentV01,
    acp.ActionIdempotencyIdentityV01,
]:
    logical = acp.build_root_owned_logical_effect_intent_v01(
        owning_effect_root_id=root_id or projection.owning_local_root_id,
        transaction_id=(
            transaction_id
            if transaction_id is not None
            else projection.transaction_id
        ),
        logical_effect_class=effect_class or "PAYMENT",
        normalized_subject_scope=subject or projection.normalized_subject_scope,
        normalized_target_scope=target or projection.normalized_target_scope,
        normalized_business_object_identity=(
            business or projection.business_object_identity
        ),
        normalized_consequential_effect_parameters=(
            consequential or projection.consequential_effect_parameters
        ),
        logical_effect_namespace=namespace or LOGICAL_NAMESPACE,
    )
    idempotency = acp.build_action_idempotency_identity_v01(
        owning_effect_root_id=logical.owning_effect_root_id,
        transaction_id=logical.transaction_id,
        root_owned_intent_id=logical.root_owned_intent_id,
        logical_effect_class=logical.logical_effect_class,
        normalized_subject_scope=logical.normalized_subject_scope,
        normalized_target_scope=logical.normalized_target_scope,
        normalized_business_object_identity=(
            logical.normalized_business_object_identity
        ),
        normalized_consequential_effect_parameters=(
            logical.normalized_consequential_effect_parameters
        ),
        logical_effect_namespace=logical.logical_effect_namespace,
    )
    return logical, idempotency


def _rebuild_projection_gate_context(
    projection: acp.SupplierActionCommitPacketCanonicalProjectionV01,
    *,
    transaction_id: object,
    permission_ref: str,
    required_approval_refs: tuple[str, ...] | None = None,
) -> acp.SupplierActionCommitPacketCanonicalProjectionV01:
    permission = acp.build_action_permission_scope_profile_v01(
        allowed_action_classes=(
            projection.normalized_permission_scope.allowed_action_classes
        ),
        forbidden_action_classes=(
            projection.normalized_permission_scope.forbidden_action_classes
        ),
        allowed_adapter_ids=(
            projection.normalized_permission_scope.allowed_adapter_ids
        ),
        forbidden_adapter_ids=(
            projection.normalized_permission_scope.forbidden_adapter_ids
        ),
        required_approval_refs=required_approval_refs or (permission_ref,),
        prohibited_effect_classes=(
            projection.normalized_permission_scope.prohibited_effect_classes
        ),
    )
    logical = acp.build_root_owned_logical_effect_intent_v01(
        owning_effect_root_id=projection.owning_local_root_id,
        transaction_id=transaction_id,
        logical_effect_class=projection.logical_intent.logical_effect_class,
        normalized_subject_scope=projection.normalized_subject_scope,
        normalized_target_scope=projection.normalized_target_scope,
        normalized_business_object_identity=projection.business_object_identity,
        normalized_consequential_effect_parameters=(
            projection.consequential_effect_parameters
        ),
        logical_effect_namespace=projection.logical_intent.logical_effect_namespace,
    )
    idempotency = acp.build_action_idempotency_identity_v01(
        owning_effect_root_id=projection.owning_local_root_id,
        transaction_id=transaction_id,
        root_owned_intent_id=logical.root_owned_intent_id,
        logical_effect_class=logical.logical_effect_class,
        normalized_subject_scope=projection.normalized_subject_scope,
        normalized_target_scope=projection.normalized_target_scope,
        normalized_business_object_identity=projection.business_object_identity,
        normalized_consequential_effect_parameters=(
            projection.consequential_effect_parameters
        ),
        logical_effect_namespace=logical.logical_effect_namespace,
    )
    candidate = acp.build_root_bound_packet_authorization_candidate_v01(
        owning_local_root_id=projection.owning_local_root_id,
        transaction_id=transaction_id,
        root_owned_intent_id=logical.root_owned_intent_id,
        effect_class=projection.authorization_candidate.effect_class,
        normalized_subject_scope=projection.normalized_subject_scope,
        normalized_target_scope=projection.normalized_target_scope,
        normalized_permission_scope=permission,
        normalized_effect_parameters_fingerprint=(
            projection.normalized_effect_parameters_fingerprint
        ),
        corridor_class=projection.authorization_candidate.corridor_class,
        adapter_binding=projection.adapter_binding,
        dependency_set_candidate_fingerprint=(
            projection.dependency_set_candidate_fingerprint
        ),
        temporal_authority_fingerprint=(
            projection.temporal_authority_fingerprint
        ),
        policy_version=projection.authority_policy.policy_version,
        authority_policy_fingerprint=projection.authority_policy_fingerprint,
    )
    stored_transaction = (
        None if transaction_id is None or acp.is_absent_v01(transaction_id)
        else transaction_id
    )
    return replace(
        projection,
        transaction_id=stored_transaction,  # type: ignore[arg-type]
        canonical_permission_ref=permission_ref,
        normalized_permission_scope=permission,
        logical_intent=logical,
        idempotency_identity=idempotency,
        authorization_candidate=candidate,
    )


def _build_frozen_root_evidence(
    canonical: acp.SupplierActionCommitPacketCanonicalProjectionV01,
    *,
    candidate_id: str | None = None,
    candidate_kind: str = "PACKET_AUTHORIZATION",
    transaction_id: str | None = None,
    target_root_id: str | None = None,
    claim_predicate: str | None = None,
    claim_candidate_kind: str | None = None,
    state_updates: dict[str, dict[str, object]] | None = None,
) -> tuple[
    semantic_work.SemanticWorkRequestV01,
    semantic_work.RootReviewPacketV01,
    root_decision.RootDecisionKernelV01,
    root_decision.RootDecisionInputV01,
    root_decision.RootDecisionResultV01,
]:
    if candidate_id is None:
        if candidate_kind != "PACKET_AUTHORIZATION":
            raise ValueError("candidate_id_required")
        selected_candidate = (
            canonical.authorization_candidate
            .root_packet_authorization_candidate_id
        )
    else:
        selected_candidate = candidate_id
    predicate_by_kind = {
        "PACKET_AUTHORIZATION": "root_packet_authorization_candidate",
        "REVOCATION": "action_revocation_candidate_v01",
        "SUPERSESSION": "action_supersession_candidate_v01",
    }
    predicate = predicate_by_kind[candidate_kind]
    transaction = transaction_id or canonical.transaction_id
    target_root = target_root_id or canonical.owning_local_root_id
    subject = "action_commit_packet:supplier_a"
    context_ref = "context:g2a1b_packet_authorization"
    actor_id = "runtime:g2a1b_candidate_projection"
    request = semantic_work.build_semantic_work_request_v01(
        request_id="semantic_request:g2a1b_supplier_authorization",
        transaction_id=transaction,
        target_root_id=target_root,
        runtime_topology_ref="runtime_topology:g2a1b_frozen_root_path",
        bounded_context_refs=(context_ref,),
        permitted_actor_ids=(actor_id,),
        permitted_contribution_modes=("DETERMINISTIC",),
        requested_subjects=(subject,),
        required_evidence_classes=("DEPENDENCY_EVIDENCE",),
        forbidden_claims=("authority_creation",),
    )
    dependency_record = canonical.dependency_candidate.dependency_records[0]
    evidence = semantic_work.build_evidence_binding_v01(
        evidence_id="evidence_binding:g2a1b_dependency",
        evidence_ref=dependency_record.evidence_ref,
        evidence_class="DEPENDENCY_EVIDENCE",
        source_component_id="deterministic_runtime",
        provenance_ref=dependency_record.source_provenance_refs[0],
        evidence_state="PRESENT",
    )
    claim = semantic_work.build_normalized_claim_v01(
        claim_id=selected_candidate,
        subject=subject,
        predicate=claim_predicate or predicate,
        object_or_value={
            "candidate_id": selected_candidate,
            "candidate_kind": claim_candidate_kind or candidate_kind,
        },
        time_envelope_ref=canonical.temporal_authority_fingerprint,
        provenance_refs=("provenance:g2a1b_packet_authorization",),
        evidence_refs=(evidence.evidence_id,),
        confidence_micros=1_000_000,
        source_role="deterministic_runtime",
        source_mode="DETERMINISTIC",
    )
    contribution = semantic_work.build_actor_contribution_v01(
        contribution_id="contribution:g2a1b_packet_authorization",
        request_id=request.request_id,
        actor_id=actor_id,
        actor_role="deterministic_runtime",
        contribution_mode="DETERMINISTIC",
        bsep_projection_ref="bsep:g2a1b_packet_authorization",
        scope="scope:g2a1b_supplier_packet_authorization",
        bounded_context_refs=(context_ref,),
        claims=(claim,),
        evidence_bindings=(evidence,),
        constraint_bindings=(),
        uncertainty_bindings=(),
        requested_validators=("validator:g2a1b_packet_authorization",),
        forbidden_claims_observed=(),
    )
    profiles = trust_model.build_default_component_trust_profiles_v01()
    review_packet = (
        semantic_work.build_root_review_packet_from_contributions_v01(
            request=request,
            contributions=(contribution,),
            trust_profiles=profiles,
        )
    )
    mandatory_refs = [
        record.evidence_ref
        for record in canonical.dependency_candidate.dependency_records
        if record.requirement_class == "MANDATORY"
    ]
    states: dict[str, dict[str, object]] = {
        "post_vv_bundle": {
            "bundle_id": "post_vv:g2a1b_supplier_authorization",
            "post_vv_passed": True,
            "validated_candidate_ids": [selected_candidate],
            "rejected_candidate_ids": [],
            "required_evidence_refs": mandatory_refs,
            "provided_evidence_refs": mandatory_refs,
            "hard_failure_reasons": [],
        },
        "gt_advisory": {
            "advisory_id": "gt:g2a1b_supplier_authorization",
            "candidate_ids": [selected_candidate],
            "selected_candidate_id": selected_candidate,
            "score_micros_by_candidate": {selected_candidate: 1_000_000},
            "source_artifact_type": "GTAdvisoryReport",
            "source_lifecycle_state": "VALIDATED",
            "actor_role": "gt",
            "attempted_effect": "CREATE_ROOT_DECISION",
            "target_artifact_type": "RootDecision",
            "advisory_only": True,
            "creates_final_output": False,
            "requests_effect": False,
        },
        "policy_state": {
            "policy_id": canonical.authority_policy_fingerprint,
            "identity_passed": True,
            "scope_passed": True,
            "hard_policy_passed": True,
            "allow_accept": True,
            "conflict_policy": "DEFER",
            "no_candidate_policy": "NO_UPDATE",
        },
        "permission_state": {
            "permission_required": candidate_kind == "PACKET_AUTHORIZATION",
            "user_permission_present": candidate_kind == "PACKET_AUTHORIZATION",
            "permission_scope_valid": True,
            "permission_ref": (
                canonical.canonical_permission_ref
                if candidate_kind == "PACKET_AUTHORIZATION"
                else None
            ),
        },
        "temporal_state": {
            "temporal_valid": True,
            "expired": False,
            "not_before_satisfied": True,
            "time_envelope_ref": canonical.temporal_authority_fingerprint,
        },
        "conflict_state": {
            "material_unresolved_conflict": False,
            "conflict_set_ids": list(review_packet.conflict_set_ids),
        },
        "prior_root_state": {
            "prior_decision_id": None,
            "prior_decision": None,
            "prior_selected_candidate_id": None,
        },
    }
    for state_name, updates in (state_updates or {}).items():
        states[state_name].update(updates)
    kernel = root_decision.build_root_decision_kernel_v01()
    decision_input = root_decision.build_root_decision_input_v01(
        transaction_id=transaction,
        target_root_id=target_root,
        root_review_packet=review_packet,
        post_vv_bundle=states["post_vv_bundle"],
        gt_advisory=states["gt_advisory"],
        policy_state=states["policy_state"],
        permission_state=states["permission_state"],
        temporal_state=states["temporal_state"],
        conflict_state=states["conflict_state"],
        prior_root_state=states["prior_root_state"],
    )
    result = root_decision.decide_root_v01(
        kernel=kernel,
        decision_input=decision_input,
    )
    return request, review_packet, kernel, decision_input, result


def _rebuild_frozen_root_input(
    fixture: _RootBoundFixtureV01,
    *,
    transaction_id: str | None = None,
    target_root_id: str | None = None,
    root_review_packet: semantic_work.RootReviewPacketV01 | None = None,
    state_updates: dict[str, dict[str, object]] | None = None,
) -> tuple[
    root_decision.RootDecisionInputV01,
    root_decision.RootDecisionResultV01,
]:
    plain = root_decision.root_decision_input_to_plain_dict_v01(
        fixture.root_decision_input
    )
    states = {
        name: dict(plain[name])
        for name in (
            "post_vv_bundle",
            "gt_advisory",
            "policy_state",
            "permission_state",
            "temporal_state",
            "conflict_state",
            "prior_root_state",
        )
    }
    for state_name, updates in (state_updates or {}).items():
        states[state_name].update(updates)
    decision_input = root_decision.build_root_decision_input_v01(
        transaction_id=transaction_id or fixture.root_decision_input.transaction_id,
        target_root_id=target_root_id or fixture.root_decision_input.target_root_id,
        root_review_packet=root_review_packet or fixture.root_review_packet,
        post_vv_bundle=states["post_vv_bundle"],
        gt_advisory=states["gt_advisory"],
        policy_state=states["policy_state"],
        permission_state=states["permission_state"],
        temporal_state=states["temporal_state"],
        conflict_state=states["conflict_state"],
        prior_root_state=states["prior_root_state"],
    )
    result = root_decision.decide_root_v01(
        kernel=fixture.root_decision_kernel,
        decision_input=decision_input,
    )
    return decision_input, result


def _unchecked_root_projection(
    fixture: _RootBoundFixtureV01,
    *,
    candidate_id: str | None = None,
    kernel: object | None = None,
    decision_input: object | None = None,
    result: object | None = None,
    source_hash: str | None = None,
) -> acp.RootDecisionCandidateProjectionV01:
    selected_result = result or fixture.root_decision_result
    selected_source_hash = source_hash
    if selected_source_hash is None:
        try:
            selected_source_hash = (
                acp.build_action_source_root_decision_hash_v01(
                    selected_result
                )
            )
        except ValueError:
            selected_source_hash = (
                fixture.root_projection.source_root_decision_hash
            )
    return acp.RootDecisionCandidateProjectionV01(
        candidate_kind=(
            acp.ROOT_DECISION_CANDIDATE_KIND_PACKET_AUTHORIZATION_V01
        ),
        projected_candidate_id=(
            candidate_id
            or fixture.canonical_projection.authorization_candidate
            .root_packet_authorization_candidate_id
        ),
        root_decision_kernel=kernel or fixture.root_decision_kernel,
        root_decision_input=decision_input or fixture.root_decision_input,
        root_decision_result=selected_result,
        source_root_decision_hash=selected_source_hash,
    )


def _root_projection_from_valid_evidence(
    fixture: _RootBoundFixtureV01,
    *,
    candidate_id: str,
    decision_input: root_decision.RootDecisionInputV01,
    result: root_decision.RootDecisionResultV01,
) -> acp.RootDecisionCandidateProjectionV01:
    return acp.build_root_decision_candidate_projection_v01(
        candidate_kind=(
            acp.ROOT_DECISION_CANDIDATE_KIND_PACKET_AUTHORIZATION_V01
        ),
        projected_candidate_id=candidate_id,
        root_decision_kernel=fixture.root_decision_kernel,
        root_decision_input=decision_input,
        root_decision_result=result,
    )


@pytest.fixture(scope="module")
def root_bound_fixture() -> _RootBoundFixtureV01:
    canonical = _projection()
    request, review, kernel, decision_input, result = (
        _build_frozen_root_evidence(canonical)
    )
    root_projection = acp.build_root_decision_candidate_projection_v01(
        candidate_kind=(
            acp.ROOT_DECISION_CANDIDATE_KIND_PACKET_AUTHORIZATION_V01
        ),
        projected_candidate_id=(
            canonical.authorization_candidate
            .root_packet_authorization_candidate_id
        ),
        root_decision_kernel=kernel,
        root_decision_input=decision_input,
        root_decision_result=result,
    )
    root_bound = (
        acp.build_supplier_root_bound_action_commit_packet_v02_projection_v01(
            canonical_projection=canonical,
            root_decision_projection=root_projection,
        )
    )
    return _RootBoundFixtureV01(
        canonical_projection=canonical,
        semantic_request=request,
        root_review_packet=review,
        root_decision_kernel=kernel,
        root_decision_input=decision_input,
        root_decision_result=result,
        root_projection=root_projection,
        root_bound_projection=root_bound,
    )


def test_absent_sentinel_and_canonical_distinctions() -> None:
    assert dict(acp.ABSENT_V01) == {"$hedgehog_absent": "ABSENT_V01"}
    assert acp.is_absent_v01(acp.ABSENT_V01) is True
    assert acp.is_absent_v01(
        {"$hedgehog_absent": "ABSENT_V01"}
    ) is False
    absent = canonical_json_bytes_v01(acp.ABSENT_V01)
    assert absent != canonical_json_bytes_v01(None)
    assert absent != canonical_json_bytes_v01("")
    assert absent != canonical_json_bytes_v01(())

    with pytest.raises(TypeError):
        acp.ABSENT_V01["changed"] = "value"  # type: ignore[index]


def test_mutable_caller_input_cannot_change_built_profile() -> None:
    raw = ["subject:b", "subject:a"]
    profile = acp.build_action_subject_scope_profile_v01(
        included_subject_refs=tuple(raw),
        excluded_subject_refs=(),
    )
    raw.append("subject:c")
    assert profile.included_subject_refs == ("subject:a", "subject:b")


def test_canonical_material_field_validation() -> None:
    valid = (("first", 1), ("second", 2))
    assert acp.validate_canonical_profile_material_v01(
        valid,
        expected_field_names=("first", "second"),
    ) == (True, ())
    cases = (
        ((("first", 1),), "canonical_material_field_missing"),
        (
            (("first", 1), ("second", 2), ("third", 3)),
            "canonical_material_field_unknown",
        ),
        (
            (("second", 2), ("first", 1)),
            "canonical_material_field_order_invalid",
        ),
        (
            (("first", 1), ("first", 2)),
            "canonical_material_field_duplicate",
        ),
    )
    for material, reason in cases:
        valid_result, reasons = acp.validate_canonical_profile_material_v01(
            material,
            expected_field_names=("first", "second"),
        )
        assert valid_result is False
        assert reason in reasons


@pytest.mark.parametrize(
    "material",
    (
        {},
        [],
        "x",
        None,
        (),
        (("a", 1), ("a", 2)),
        (("a", 1), ("bad",)),
        (["a", 1],),
        (("", 1),),
        (("e\u0301", 1),),
        (("bad\x00name", 1),),
        ((1, "value"),),
        (("a", []),),
        (("a", {}),),
        (("a", {"$hedgehog_absent": "ABSENT_V01"}),),
        (("a", set()),),
    ),
)
def test_canonical_material_gate_rejects_malformed_and_mutable_input(
    material: object,
) -> None:
    valid, reasons = acp.validate_canonical_profile_material_v01(
        material,
        expected_field_names=("a",),
    )
    assert valid is False
    assert reasons
    with pytest.raises(ValueError):
        acp.canonical_material_bytes_v01(material)
    with pytest.raises(ValueError):
        acp.build_domain_separated_identity_v01(
            domain="HEDGEHOG_TEST_V01",
            prefix="test_v01:",
            material=material,  # type: ignore[arg-type]
        )


def test_canonical_material_control_types_fail_closed_without_throwing() -> None:
    material = (("a", 1),)
    for expected in (None, [], "a", 1, 1.0, True, {}, ("",)):
        valid, reasons = acp.validate_canonical_profile_material_v01(
            material,
            expected_field_names=expected,
        )
        assert valid is False
        assert reasons
    assert acp.validate_identity_text_v01("value", allow_empty=1)[0] is False
    assert acp.validate_identity_text_v01("value", allow_empty="true")[0] is False
    assert acp.validate_set_like_string_tuple_v01(
        ("value",),
        require_non_empty=1,
    )[0] is False
    assert acp.validate_set_like_string_tuple_v01(
        ("value",),
        require_non_empty="true",
    )[0] is False
    for prefix in (None, "", 1, 1.0, True, [], {}):
        valid, reasons = acp.validate_prefixed_sha256_identity_v01(
            "prefix:" + "a" * 64,
            prefix=prefix,
        )
        assert valid is False
        assert reasons
    for kind in (None, 1, 1.0, True, [], {}, "unknown"):
        valid, reasons = acp.validate_native_effect_firewall_identifier_v01(
            "mock_adapter:value",
            identifier_kind=kind,
        )
        assert valid is False
        assert reasons


def test_nfc_set_normalization_duplicate_nul_and_surrogate_laws() -> None:
    decomposed = "cafe\u0301"
    composed = "caf\u00e9"
    assert acp.canonicalize_set_like_string_tuple_v01((decomposed,)) == (
        composed,
    )
    with pytest.raises(ValueError, match="set_like_tuple_duplicate"):
        acp.canonicalize_set_like_string_tuple_v01((decomposed, composed))
    assert acp.validate_identity_text_v01("bad\x00value")[0] is False
    assert acp.validate_identity_text_v01("\ud800")[0] is False
    assert acp.validate_signed_int64_v01(True)[0] is False


@pytest.mark.parametrize(
    "value",
    ("0", "1", "-1", "1.5", "-1.5", "0.5", "0.01", "-0.5", "10.01", "-10.01"),
)
def test_canonical_decimal_accepts_exact_examples(value: str) -> None:
    assert acp.validate_canonical_decimal_v01(value) == (True, ())


@pytest.mark.parametrize(
    "value",
    (
        "+1",
        "01",
        "00.5",
        ".5",
        "1.",
        "1.0",
        "0.10",
        "-0",
        "-0.0",
        "1e3",
        "NaN",
        "Infinity",
        1.0,
        Decimal("1"),
        True,
        None,
    ),
)
def test_canonical_decimal_rejects_exact_examples(value: object) -> None:
    assert acp.validate_canonical_decimal_v01(value)[0] is False


@pytest.mark.parametrize(
    ("source", "expected"),
    (("1250.00", "1250"), ("0.50", "0.5"), ("0.0100", "0.01")),
)
def test_legacy_decimal_normalization(source: str, expected: str) -> None:
    assert acp.normalize_legacy_decimal_v01(source) == expected


@pytest.mark.parametrize("value", ("-0", "-0.0", "1e3", 1.5))
def test_legacy_decimal_rejects_negative_zero_exponent_and_float(
    value: object,
) -> None:
    assert acp.validate_legacy_decimal_v01(value)[0] is False


def test_timestamp_exact_utc_forms_and_boundaries() -> None:
    z_value = acp.parse_utc_timestamp_v01("2026-07-08T00:00:00Z")
    offset_value = acp.parse_utc_timestamp_v01(
        "2026-07-08T00:00:00+00:00"
    )
    assert z_value == offset_value == 1783468800
    assert acp.parse_utc_timestamp_v01("1970-01-01T00:00:00Z") == 0


@pytest.mark.parametrize(
    "value",
    (
        "2026-02-30T00:00:00Z",
        "2026-07-08T00:00:00",
        "2026-07-08T00:00:00.1Z",
        "2026-07-08T00:00:00+01:00",
        "2026-07-08T00:00:60Z",
        True,
    ),
)
def test_timestamp_rejects_malformed_or_noncanonical_values(
    value: object,
) -> None:
    assert acp.validate_utc_timestamp_v01(value)[0] is False


def test_temporal_consistency_and_half_open_interval() -> None:
    temporal = acp.build_action_temporal_authority_profile_v01(
        issued_at_utc=100,
        expires_at_utc=110,
        ttl_seconds=10,
        temporal_policy_version="ttl_v01",
    )
    assert acp.evaluate_temporal_authority_v01(
        temporal, evaluation_time=99
    ) == acp.TemporalEvaluationV01("NOT_YET_VALID", False)
    assert acp.evaluate_temporal_authority_v01(
        temporal, evaluation_time=100
    ) == acp.TemporalEvaluationV01("TEMPORALLY_VALID", True)
    assert acp.evaluate_temporal_authority_v01(
        temporal, evaluation_time=109
    ) == acp.TemporalEvaluationV01("TEMPORALLY_VALID", True)
    assert acp.evaluate_temporal_authority_v01(
        temporal, evaluation_time=110
    ) == acp.TemporalEvaluationV01("EXPIRED", False)
    with pytest.raises(ValueError, match="temporal_authority_inconsistent"):
        acp.build_action_temporal_authority_profile_v01(
            issued_at_utc=100,
            expires_at_utc=111,
            ttl_seconds=10,
            temporal_policy_version="ttl_v01",
        )
    with pytest.raises(ValueError, match="temporal_authority_overflow"):
        acp.build_action_temporal_authority_profile_v01(
            issued_at_utc=acp.INT64_MAX_V01,
            expires_at_utc=acp.INT64_MAX_V01,
            ttl_seconds=1,
            temporal_policy_version="ttl_v01",
        )


def test_packet_ttl_assertions_are_recomputed() -> None:
    packet = acp.build_supplier_a_mock_action_commit_packet_fixture_v02()
    result = acp.project_packet_ttl_compatibility_v01(
        packet.ttl,
        evaluation_time=EVALUATION_TIME,
        temporal_policy_version=TEMPORAL_POLICY,
    )
    assert result.evaluation.executable is True
    with pytest.raises(ValueError, match="expired_assertion_mismatch"):
        acp.project_packet_ttl_compatibility_v01(
            replace(packet.ttl, expired=True),
            evaluation_time=EVALUATION_TIME,
            temporal_policy_version=TEMPORAL_POLICY,
        )
    with pytest.raises(ValueError, match="valid_assertion_mismatch"):
        acp.project_packet_ttl_compatibility_v01(
            replace(packet.ttl, ttl_valid=False),
            evaluation_time=EVALUATION_TIME,
            temporal_policy_version=TEMPORAL_POLICY,
        )


def test_logical_time_bridge_exact_round_trip_and_rejections() -> None:
    bridge = acp.build_logical_time_bridge_v01(
        origin_utc_epoch_seconds=1000,
        seconds_per_tick=5,
        bridge_policy_version="bridge_v01",
    )
    assert acp.logical_tick_to_epoch_seconds_v01(bridge, 3) == 1015
    assert acp.epoch_seconds_to_logical_tick_v01(bridge, 1015) == 3
    with pytest.raises(ValueError, match="unrepresentable"):
        acp.epoch_seconds_to_logical_tick_v01(bridge, 1016)
    with pytest.raises(ValueError):
        acp.build_logical_time_bridge_v01(
            origin_utc_epoch_seconds=0,
            seconds_per_tick=True,
            bridge_policy_version="bridge_v01",
        )
    overflow_bridge = acp.build_logical_time_bridge_v01(
        origin_utc_epoch_seconds=acp.INT64_MAX_V01,
        seconds_per_tick=2,
        bridge_policy_version="bridge_v01",
    )
    with pytest.raises(ValueError, match="overflow"):
        acp.logical_tick_to_epoch_seconds_v01(overflow_bridge, 1)


def test_subject_target_and_permission_profile_laws() -> None:
    subject = acp.build_action_subject_scope_profile_v01(
        included_subject_refs=("subject:a",),
        excluded_subject_refs=("subject:b",),
    )
    target = acp.build_action_target_scope_profile_v01(
        included_target_refs=("target:a",),
        excluded_target_refs=(),
    )
    permission = acp.build_action_permission_scope_profile_v01(
        allowed_action_classes=("mock_action:pay",),
        forbidden_action_classes=("mock_action:block",),
        allowed_adapter_ids=("mock_adapter:bank",),
        forbidden_adapter_ids=("mock_adapter:other",),
        required_approval_refs=("permission:pay",),
        prohibited_effect_classes=(),
    )
    assert tuple(name for name, _ in acp.action_subject_scope_material_v01(subject)) == (
        "profile_id",
        "included_subject_refs",
        "excluded_subject_refs",
    )
    assert len(acp.action_target_scope_material_v01(target)) == 3
    assert len(acp.action_permission_scope_material_v01(permission)) == 7
    with pytest.raises(ValueError, match="included_empty"):
        acp.build_action_subject_scope_profile_v01(
            included_subject_refs=(),
            excluded_subject_refs=(),
        )
    with pytest.raises(ValueError, match="scope_overlap"):
        acp.build_action_target_scope_profile_v01(
            included_target_refs=("target:a",),
            excluded_target_refs=("target:a",),
        )
    with pytest.raises(ValueError, match="permission_action_overlap"):
        acp.build_action_permission_scope_profile_v01(
            allowed_action_classes=("mock_action:pay",),
            forbidden_action_classes=("mock_action:pay",),
            allowed_adapter_ids=("mock_adapter:bank",),
            forbidden_adapter_ids=(),
            required_approval_refs=("permission:pay",),
            prohibited_effect_classes=(),
        )


def test_effect_parameter_types_order_and_fingerprint() -> None:
    records = (
        acp.build_action_effect_parameter_record_v01(
            parameter_name="zeta", value_type="INTEGER", value=7
        ),
        acp.build_action_effect_parameter_record_v01(
            parameter_name="alpha", value_type="BOOLEAN", value=True
        ),
        acp.build_action_effect_parameter_record_v01(
            parameter_name="middle", value_type="DECIMAL", value="1.5"
        ),
    )
    profile = acp.build_action_effect_parameters_profile_v01(
        effect_class="PAYMENT",
        parameter_records=records,
    )
    assert tuple(record.parameter_name for record in profile.parameter_records) == (
        "alpha",
        "middle",
        "zeta",
    )
    fingerprint = acp.build_action_effect_parameters_fingerprint_v01(profile)
    assert len(fingerprint) == 64
    assert fingerprint == fingerprint.lower()
    with pytest.raises(ValueError):
        acp.build_action_effect_parameter_record_v01(
            parameter_name="bad", value_type="INTEGER", value=True
        )


def test_dependency_profiles_exact_material_and_anti_cycle() -> None:
    dependency = _dependency()
    record_material = acp.dependency_set_candidate_record_material_v01(
        dependency.dependency_records[0]
    )
    material = acp.dependency_set_candidate_material_v01(dependency)
    assert len(record_material) == 9
    assert len(material) == 2
    assert "source_root_decision_id" not in tuple(name for name, _ in record_material)
    assert "packet_id" not in tuple(name for name, _ in record_material)
    assert len(acp.build_dependency_set_candidate_fingerprint_v01(dependency)) == 64
    with pytest.raises(ValueError, match="mandatory_temporal_binding_missing"):
        acp.build_dependency_set_candidate_record_v01(
            dependency_id="dependency:bad",
            dependency_class="EVIDENCE",
            evidence_ref="evidence:bad",
            content_sha256="b" * 64,
            requirement_class="MANDATORY",
            time_envelope_id=None,
            freshness_policy_id=None,
            source_provenance_refs=("source:bad",),
            expected_accepting_local_root_id=ROOT_ID,
        )


def test_dependency_acceptance_binding_exact_identity() -> None:
    projection = _projection()
    packet_identity = acp.build_action_commit_packet_identity_v01(
        candidate=projection.authorization_candidate,
        source_root_decision_id="b" * 64,
        source_root_decision_hash="c" * 64,
    )
    binding = acp.build_packet_dependency_acceptance_binding_v01(
        dependency_set_candidate_fingerprint=(
            projection.dependency_set_candidate_fingerprint
        ),
        root_packet_authorization_candidate_id=(
            projection.authorization_candidate
            .root_packet_authorization_candidate_id
        ),
        source_root_decision_id="b" * 64,
        source_root_decision_hash="c" * 64,
        owning_local_root_id=ROOT_ID,
        packet_id=packet_identity.packet_id,
    )
    assert len(acp.packet_dependency_acceptance_binding_material_v01(binding)) == 7
    assert binding.packet_dependency_acceptance_binding_id.startswith(
        "packet_dependency_acceptance_v01:"
    )
    assert acp.validate_packet_dependency_acceptance_binding_v01(binding) == (
        True,
        (),
    )


def test_policy_business_and_consequential_contracts() -> None:
    policy = _policy()
    assert len(acp.action_authority_policy_material_v01(policy)) == 11
    business = acp.build_action_business_object_identity_profile_v01(
        business_object_class="PAYMENT_SLOT",
        business_object_namespace=BUSINESS_NAMESPACE,
        business_object_ref="slot:1",
        owning_effect_root_id=ROOT_ID,
    )
    assert len(acp.action_business_object_identity_material_v01(business)) == 5
    consequential = acp.build_action_consequential_effect_parameters_profile_v01(
        amount_decimal="10.5",
        currency_code="EUR",
        quantity_decimal=None,
        parameter_records=(),
    )
    assert len(
        acp.action_consequential_effect_parameters_material_v01(consequential)
    ) == 5
    with pytest.raises(ValueError, match="currency_required"):
        acp.build_action_consequential_effect_parameters_profile_v01(
            amount_decimal="1",
            currency_code=None,
            quantity_decimal=None,
            parameter_records=(),
        )
    with pytest.raises(ValueError, match="currency_without_amount"):
        acp.build_action_consequential_effect_parameters_profile_v01(
            amount_decimal=None,
            currency_code="EUR",
            quantity_decimal=None,
            parameter_records=(),
        )
    reserved = acp.build_action_effect_parameter_record_v01(
        parameter_name="amount_decimal",
        value_type="DECIMAL",
        value="1",
    )
    with pytest.raises(ValueError, match="name_reserved"):
        acp.build_action_consequential_effect_parameters_profile_v01(
            amount_decimal=None,
            currency_code=None,
            quantity_decimal=None,
            parameter_records=(reserved,),
        )


def test_every_nested_profile_id_is_exact() -> None:
    projection = _projection()
    assert acp.action_subject_scope_material_v01(
        projection.normalized_subject_scope
    )[0] == ("profile_id", "action_subject_scope_profile_v01")
    assert acp.action_target_scope_material_v01(
        projection.normalized_target_scope
    )[0] == ("profile_id", "action_target_scope_profile_v01")
    assert acp.action_permission_scope_material_v01(
        projection.normalized_permission_scope
    )[0] == ("profile_id", "action_permission_scope_profile_v01")
    assert acp.action_effect_parameters_material_v01(
        projection.normalized_effect_parameters
    )[0] == ("profile_id", "action_effect_parameters_profile_v01")
    assert acp.action_adapter_binding_material_v01(
        projection.adapter_binding
    )[0] == ("profile_id", "action_adapter_binding_profile_v01")
    assert acp.dependency_set_candidate_material_v01(
        projection.dependency_candidate
    )[0] == ("profile_id", "action_dependency_set_candidate_v01")
    assert acp.ACTION_TEMPORAL_AUTHORITY_PROFILE_ID_V01 == (
        "action_temporal_authority_profile_v01"
    )
    assert acp.action_authority_policy_material_v01(
        projection.authority_policy
    )[0] == ("profile_id", "action_authority_policy_profile_v01")
    assert acp.action_business_object_identity_material_v01(
        projection.business_object_identity
    )[0] == ("profile_id", "action_business_object_identity_profile_v01")
    assert acp.action_consequential_effect_parameters_material_v01(
        projection.consequential_effect_parameters
    )[0] == (
        "profile_id",
        "action_consequential_effect_parameters_profile_v01",
    )


def test_identity_material_counts_prefixes_and_forgery_rejection() -> None:
    projection = _projection()
    assert len(
        acp.root_owned_logical_effect_intent_material_v01(
            projection.logical_intent
        )
    ) == 9
    assert len(
        acp.action_idempotency_identity_material_v01(
            projection.idempotency_identity
        )
    ) == 10
    assert len(
        acp.root_bound_packet_authorization_candidate_material_v01(
            projection.authorization_candidate
        )
    ) == 18
    assert projection.logical_intent.root_owned_intent_id.startswith(
        "root_logical_intent_v01:"
    )
    assert projection.idempotency_identity.idempotency_key.startswith(
        "idem:action_v01:"
    )
    assert (
        projection.authorization_candidate
        .root_packet_authorization_candidate_id
        .startswith("root_packet_authorization_v01:")
    )
    packet = acp.build_action_commit_packet_identity_v01(
        candidate=projection.authorization_candidate,
        source_root_decision_id="d" * 64,
        source_root_decision_hash="e" * 64,
    )
    assert len(packet.material) == 20
    assert packet.packet_id.startswith("acp_v02:")
    forged = replace(packet, packet_id="acp_v02:" + "0" * 64)
    assert acp.validate_action_commit_packet_identity_v01(
        forged,
        candidate=projection.authorization_candidate,
        source_root_decision_id="d" * 64,
        source_root_decision_hash="e" * 64,
    )[0] is False
    forged_intent = replace(
        projection.logical_intent,
        root_owned_intent_id="root_logical_intent_v01:" + "0" * 64,
    )
    assert acp.validate_root_owned_logical_effect_intent_v01(forged_intent)[0] is False
    forged_key = replace(
        projection.idempotency_identity,
        idempotency_key="idem:action_v01:" + "0" * 64,
    )
    assert acp.validate_action_idempotency_identity_v01(forged_key)[0] is False
    forged_candidate = replace(
        projection.authorization_candidate,
        root_packet_authorization_candidate_id=(
            "root_packet_authorization_v01:" + "0" * 64
        ),
    )
    assert acp.validate_root_bound_packet_authorization_candidate_v01(
        forged_candidate
    )[0] is False


def test_standard_supplier_identity_vector_is_frozen() -> None:
    projection = _projection()
    packet = acp.build_action_commit_packet_identity_v01(
        candidate=projection.authorization_candidate,
        source_root_decision_id="d" * 64,
        source_root_decision_hash="e" * 64,
    )
    assert projection.logical_intent.root_owned_intent_id == (
        "root_logical_intent_v01:"
        "40bbd8a12946b96b9b8e36bf7420f2ede1ca98b8b361430a80a719d6791d882a"
    )
    assert projection.idempotency_identity.idempotency_key == (
        "idem:action_v01:"
        "3449140e3ee436b701d3e4ea69a4eb5d38c53081d77b68da47b3c93a0a2cde96"
    )
    assert (
        projection.authorization_candidate.root_packet_authorization_candidate_id
        == (
            "root_packet_authorization_v01:"
            "2b9ccac71b74d6365e139c14dc62f1419c86004b515ecc3692bc0a1b06e73061"
        )
    )
    assert projection.dependency_set_candidate_fingerprint == (
        "478490d365bac88ce1f0b31eee309fb8d852e159800be03510b9173e3b50120e"
    )
    assert projection.temporal_authority_fingerprint == (
        "76ab12e0a25063acd30a25dab55b8c92fef65231200eea337c1c5e608723e7fb"
    )
    assert projection.authority_policy_fingerprint == (
        "72f2e12f881bd7d2b1e7a5afc579aab9d85c5d1dec53d990e48ba6c545c05c5a"
    )
    assert projection.normalized_effect_parameters_fingerprint == (
        "74b5408e6155866096b6b4ff4adc75493a32f8ff3e37fdf246e97c401674c220"
    )
    assert packet.packet_id == (
        "acp_v02:"
        "f8095599a2c287a6c5341c252b680db355eddfc470349344e0ade1849fa5a835"
    )


def test_packet_only_changes_preserve_logical_intent_and_idempotency() -> None:
    projection = _projection()
    original_logical = projection.logical_intent.root_owned_intent_id
    original_key = projection.idempotency_identity.idempotency_key
    original_candidate = (
        projection.authorization_candidate.root_packet_authorization_candidate_id
    )
    temporal = acp.build_action_temporal_authority_profile_v01(
        issued_at_utc=projection.temporal_authority.issued_at_utc,
        expires_at_utc=projection.temporal_authority.expires_at_utc + 60,
        ttl_seconds=projection.temporal_authority.ttl_seconds + 60,
        temporal_policy_version=TEMPORAL_POLICY,
    )
    candidate = acp.build_root_bound_packet_authorization_candidate_v01(
        owning_local_root_id=projection.owning_local_root_id,
        transaction_id=projection.transaction_id,
        root_owned_intent_id=original_logical,
        effect_class="PAYMENT",
        normalized_subject_scope=projection.normalized_subject_scope,
        normalized_target_scope=projection.normalized_target_scope,
        normalized_permission_scope=projection.normalized_permission_scope,
        normalized_effect_parameters_fingerprint=(
            projection.normalized_effect_parameters_fingerprint
        ),
        corridor_class=CORRIDOR_CLASS,
        adapter_binding=replace(
            projection.adapter_binding, adapter_version="adapter_v02"
        ),
        dependency_set_candidate_fingerprint="f" * 64,
        temporal_authority_fingerprint=(
            acp.build_temporal_authority_fingerprint_v01(temporal)
        ),
        policy_version="supplier_policy_v02",
        authority_policy_fingerprint="1" * 64,
    )
    assert projection.logical_intent.root_owned_intent_id == original_logical
    assert projection.idempotency_identity.idempotency_key == original_key
    assert (
        candidate.root_packet_authorization_candidate_id != original_candidate
    )
    idempotency_fields = tuple(
        name
        for name, _ in acp.action_idempotency_identity_material_v01(
            projection.idempotency_identity
        )
    )
    for excluded in (
        "packet_contract_version",
        "ttl_seconds",
        "adapter_version",
        "dependency_set_candidate_fingerprint",
        "policy_version",
        "retry_counter",
        "registry_state",
    ):
        assert excluded not in idempotency_fields


@pytest.mark.parametrize(
    "change",
    ("root", "transaction", "effect", "subject", "target", "business", "amount", "namespace"),
)
def test_material_logical_effect_changes_change_intent_and_key(
    change: str,
) -> None:
    projection = _projection()
    kwargs: dict[str, object] = {}
    if change == "root":
        kwargs["root_id"] = "root:other"
        kwargs["business"] = replace(
            projection.business_object_identity,
            owning_effect_root_id="root:other",
        )
    elif change == "transaction":
        kwargs["transaction_id"] = "transaction:other"
    elif change == "effect":
        kwargs["effect_class"] = "SHIPMENT"
    elif change == "subject":
        kwargs["subject"] = acp.build_action_subject_scope_profile_v01(
            included_subject_refs=("subject:other",),
            excluded_subject_refs=(),
        )
    elif change == "target":
        kwargs["target"] = acp.build_action_target_scope_profile_v01(
            included_target_refs=("target:other",),
            excluded_target_refs=(),
        )
    elif change == "business":
        kwargs["business"] = replace(
            projection.business_object_identity,
            business_object_ref="slot:other",
        )
    elif change == "amount":
        kwargs["consequential"] = (
            acp.build_action_consequential_effect_parameters_profile_v01(
                amount_decimal="1251",
                currency_code="EUR",
                quantity_decimal=None,
                parameter_records=(),
            )
        )
    else:
        kwargs["namespace"] = "supplier.payment.other"
    logical, idempotency = _rebuild_logical(projection, **kwargs)
    assert logical.root_owned_intent_id != projection.logical_intent.root_owned_intent_id
    assert idempotency.idempotency_key != projection.idempotency_identity.idempotency_key


def test_effect_firewall_vocabulary_exact_mappings_and_native_path() -> None:
    assert acp.EFFECT_FIREWALL_VOCABULARY_PROJECTION_PROFILE_ID_V01 == (
        "effect_firewall_vocabulary_projection_v01"
    )
    cases = (
        (
            "adapter",
            "mock_bank_sandbox",
            ("mock_bank_sandbox",),
            "mock_adapter:mock_bank_sandbox",
        ),
        (
            "adapter",
            "bank_a_mock",
            ("bank_a_mock",),
            "mock_adapter:bank_a_mock",
        ),
        (
            "action",
            "mock_supplier_a_payment_intent",
            ("mock_supplier_a_payment_intent",),
            "mock_action:mock_supplier_a_payment_intent",
        ),
        (
            "action",
            "mock_supplier_a_payment_order",
            ("mock_supplier_a_payment_order",),
            "mock_action:mock_supplier_a_payment_order",
        ),
    )
    for kind, raw, allowed, expected in cases:
        projection = (
            acp.build_legacy_effect_firewall_vocabulary_projection_v01(
                raw_identifier=raw,
                identifier_kind=kind,
                raw_allowed_identifiers=allowed,
                raw_forbidden_identifiers=(),
            )
        )
        assert projection.canonical_identifier == expected
    native = acp.build_native_effect_firewall_vocabulary_projection_v01(
        canonical_identifier="mock_adapter:native_bank",
        identifier_kind="adapter",
    )
    assert native.compatibility_mode is False


@pytest.mark.parametrize("compatibility_mode", (1, 1.0, "true", None, [], {}))
def test_effect_firewall_vocabulary_requires_exact_boolean_mode(
    compatibility_mode: object,
) -> None:
    forged = acp.EffectFirewallVocabularyProjectionV01(
        identifier_kind="adapter",
        raw_identifier="mock_bank_sandbox",
        canonical_identifier="mock_adapter:mock_bank_sandbox",
        compatibility_mode=compatibility_mode,  # type: ignore[arg-type]
    )
    valid, reasons = acp.validate_effect_firewall_vocabulary_projection_v01(
        forged
    )
    assert valid is False
    assert reasons == ("firewall_vocabulary_compatibility_mode_type_invalid",)


def test_effect_firewall_vocabulary_exact_bool_paths_are_distinct() -> None:
    legacy = acp.build_legacy_effect_firewall_vocabulary_projection_v01(
        raw_identifier="mock_bank_sandbox",
        identifier_kind="adapter",
        raw_allowed_identifiers=("mock_bank_sandbox",),
        raw_forbidden_identifiers=(),
    )
    native = acp.build_native_effect_firewall_vocabulary_projection_v01(
        canonical_identifier="mock_adapter:mock_bank_sandbox",
        identifier_kind="adapter",
    )
    assert acp.validate_effect_firewall_vocabulary_projection_v01(legacy) == (
        True,
        (),
    )
    assert acp.validate_effect_firewall_vocabulary_projection_v01(native) == (
        True,
        (),
    )
    assert replace(legacy, compatibility_mode=False) != native
    assert acp.validate_effect_firewall_vocabulary_projection_v01(
        replace(legacy, compatibility_mode=False)
    )[0] is False
    assert acp.validate_effect_firewall_vocabulary_projection_v01(
        replace(native, compatibility_mode=True)
    )[0] is False


@pytest.mark.parametrize(
    ("raw", "kind", "allowed", "forbidden"),
    (
        ("unknown", "adapter", ("unknown",), ()),
        (
            "mock_adapter:mock_bank_sandbox",
            "adapter",
            ("mock_adapter:mock_bank_sandbox",),
            (),
        ),
        ("real_bank", "adapter", ("real_bank",), ()),
        ("real_payment", "action", ("real_payment",), ()),
        ("mock_bank_sandbox", "action", ("mock_bank_sandbox",), ()),
        ("mock_bank_sandbox", "adapter", (), ()),
        (
            "mock_bank_sandbox",
            "adapter",
            ("mock_bank_sandbox",),
            ("mock_bank_sandbox",),
        ),
        (
            "mock_supplier_a_payment_order",
            "action",
            ("mock_supplier_a_payment_order",),
            ("mock_supplier_a_payment_order",),
        ),
    ),
)
def test_effect_firewall_vocabulary_rejects_bypass(
    raw: str,
    kind: str,
    allowed: tuple[str, ...],
    forbidden: tuple[str, ...],
) -> None:
    with pytest.raises(ValueError):
        acp.build_legacy_effect_firewall_vocabulary_projection_v01(
            raw_identifier=raw,
            identifier_kind=kind,
            raw_allowed_identifiers=allowed,
            raw_forbidden_identifiers=forbidden,
        )


def test_permission_and_executable_transaction_helpers() -> None:
    assert acp.validate_canonical_permission_ref_v01(PERMISSION_REF) == (
        True,
        (),
    )
    assert acp.validate_canonical_permission_ref_v01(
        "human_approval:supplier_a_scope_only"
    )[0] is False
    assert acp.validate_executable_transaction_id_v01(TRANSACTION_ID) == (
        True,
        (),
    )
    assert acp.validate_executable_transaction_id_v01(acp.ABSENT_V01)[0] is False


def test_supplier_projection_is_pure_and_exact() -> None:
    packet = acp.build_supplier_a_mock_action_commit_packet_fixture_v02()
    before = packet
    projection = _projection(packet=packet)
    assert packet == before
    assert packet.adapter_binding.adapter_version is None
    assert projection.adapter_binding.adapter_version == (
        acp.PRE_G2A_ADAPTER_VERSION_V01
    )
    assert projection.adapter_binding.adapter_id == (
        "mock_adapter:mock_bank_sandbox"
    )
    assert projection.selected_canonical_action == (
        "mock_action:mock_supplier_a_payment_order"
    )
    assert projection.business_object_identity.business_object_class == (
        "PAYMENT_SLOT"
    )
    assert projection.business_object_identity.business_object_ref == (
        packet.scope.payment_slot_ref
    )
    assert projection.consequential_effect_parameters.amount_decimal == "1250"
    assert projection.consequential_effect_parameters.currency_code == "EUR"
    assert projection.normalized_permission_scope.required_approval_refs == (
        PERMISSION_REF,
    )
    assert projection.normalized_permission_scope.prohibited_effect_classes == ()
    assert projection.human_approval_evidence_ref == (
        "human_approval:supplier_a_scope_only"
    )
    assert not hasattr(projection, "root_decision")
    assert not hasattr(projection, "effect_request")
    assert acp.validate_supplier_action_commit_packet_canonical_projection_v01(
        projection
    ) == (True, ())


def test_supplier_projection_requires_explicit_context() -> None:
    with pytest.raises(ValueError):
        _projection(permission_ref="human_approval:supplier_a_scope_only")
    with pytest.raises(ValueError):
        _projection(transaction_id="")
    with pytest.raises(ValueError):
        _projection(selected_action=acp.ACTION_MOCK_SUPPLIER_A_PAYMENT_INTENT)


def test_supplier_projection_validator_covers_all_compatibility_fields() -> None:
    projection = _projection()
    mutations = (
        (
            replace(
                projection,
                selected_legacy_action=(
                    acp.ACTION_MOCK_SUPPLIER_A_PAYMENT_INTENT
                ),
            ),
            "supplier_projection_selected_legacy_action_mismatch",
        ),
        (
            replace(
                projection,
                selected_canonical_action=(
                    "mock_action:mock_supplier_a_payment_intent"
                ),
            ),
            "supplier_projection_selected_canonical_action_mismatch",
        ),
        (
            replace(projection, raw_allowed_actions=("arbitrary_action",)),
            "supplier_projection_raw_allowed_actions_mismatch",
        ),
        (
            replace(projection, raw_forbidden_actions=("real_payment",)),
            "supplier_projection_raw_forbidden_actions_mismatch",
        ),
        (
            replace(projection, raw_allowed_adapters=("arbitrary_adapter",)),
            "supplier_projection_raw_allowed_adapters_mismatch",
        ),
        (
            replace(projection, raw_forbidden_adapters=("real_bank",)),
            "supplier_projection_raw_forbidden_adapters_mismatch",
        ),
        (
            replace(
                projection,
                human_approval_evidence_ref="human_approval:altered",
            ),
            "supplier_projection_human_approval_evidence_mismatch",
        ),
        (
            replace(projection, advisory_drs_refs=("drs:altered",)),
            "supplier_projection_advisory_drs_mismatch",
        ),
        (
            replace(projection, advisory_avf_refs=("avf:altered",)),
            "supplier_projection_advisory_avf_mismatch",
        ),
        (
            replace(projection, advisory_bsep_ref="bsep:altered"),
            "supplier_projection_advisory_bsep_mismatch",
        ),
        (
            replace(
                projection,
                adapter_binding=replace(
                    projection.adapter_binding,
                    adapter_id="mock_adapter:bank_a_mock",
                ),
            ),
            "supplier_projection_selected_adapter_mismatch",
        ),
    )
    for changed, expected_reason in mutations:
        valid, reasons = (
            acp.validate_supplier_action_commit_packet_canonical_projection_v01(
                changed
            )
        )
        assert valid is False
        assert expected_reason in reasons


@pytest.mark.parametrize(
    ("field_name", "malformed"),
    (
        ("raw_allowed_actions", None),
        ("raw_forbidden_actions", []),
        ("raw_allowed_adapters", ["mock_bank_sandbox"]),
        ("raw_forbidden_adapters", {}),
        ("advisory_drs_refs", ["drs:invoice:inv_2042"]),
        ("advisory_avf_refs", None),
    ),
)
def test_supplier_projection_rejects_tuple_substitution(
    field_name: str,
    malformed: object,
) -> None:
    changed = replace(_projection(), **{field_name: malformed})
    valid, reasons = (
        acp.validate_supplier_action_commit_packet_canonical_projection_v01(
            changed
        )
    )
    assert valid is False
    assert reasons


@pytest.mark.parametrize(
    "permission_ref",
    (
        "human_approval:supplier_a_scope_only",
        "approval:supplier_a_payment",
        "arbitrary_text",
    ),
)
def test_coherent_forged_permission_context_fails_executable_gate(
    permission_ref: str,
) -> None:
    forged = _rebuild_projection_gate_context(
        _projection(),
        transaction_id=TRANSACTION_ID,
        permission_ref=permission_ref,
    )
    valid, reasons = (
        acp.validate_supplier_action_commit_packet_canonical_projection_v01(
            forged
        )
    )
    assert valid is False
    assert "supplier_projection_permission_invalid" in reasons


def test_coherent_absent_transaction_fails_executable_gate() -> None:
    forged = _rebuild_projection_gate_context(
        _projection(),
        transaction_id=None,
        permission_ref=PERMISSION_REF,
    )
    valid, reasons = (
        acp.validate_supplier_action_commit_packet_canonical_projection_v01(
            forged
        )
    )
    assert valid is False
    assert "supplier_projection_transaction_invalid" in reasons
    for transaction_id in (acp.ABSENT_V01, ""):
        changed = replace(forged, transaction_id=transaction_id)
        valid, reasons = (
            acp.validate_supplier_action_commit_packet_canonical_projection_v01(
                changed
            )
        )
        assert valid is False
        assert "supplier_projection_transaction_invalid" in reasons


def test_supplier_permission_reference_must_be_exact_singleton() -> None:
    projection = _projection()
    changed = _rebuild_projection_gate_context(
        projection,
        transaction_id=TRANSACTION_ID,
        permission_ref=PERMISSION_REF,
        required_approval_refs=(
            PERMISSION_REF,
            "permission:second",
        ),
    )
    valid, reasons = (
        acp.validate_supplier_action_commit_packet_canonical_projection_v01(
            changed
        )
    )
    assert valid is False
    assert "supplier_projection_permission_singleton_mismatch" in reasons


def test_supplier_projection_builder_rejects_invalid_complete_contexts() -> None:
    historical = acp.build_supplier_a_mock_action_commit_packet_fixture_v02()
    wrong_adapter_packet = replace(
        historical,
        adapter_binding=replace(
            historical.adapter_binding,
            adapter_id=acp.ADAPTER_BANK_A_MOCK,
        ),
    )
    invalid_builds = (
        lambda: _projection(policy=_policy(root_id="root:other")),
        lambda: _projection(dependency=_dependency(root_id="root:other")),
        lambda: _projection(
            policy=_policy(logical_namespace="supplier.other")
        ),
        lambda: _projection(logical_namespace="supplier.other"),
        lambda: _projection(
            policy=_policy(business_namespaces=("supplier.other",))
        ),
        lambda: _projection(business_namespace="supplier.other"),
        lambda: _projection(
            policy=_policy(corridor_classes=("corridor:other",))
        ),
        lambda: _projection(corridor_class="corridor:other"),
        lambda: _projection(policy=_policy(effect_classes=("SHIPMENT",))),
        lambda: _projection(permission_ref="human_approval:invalid"),
        lambda: _projection(transaction_id=None),  # type: ignore[arg-type]
        lambda: _projection(
            selected_action=acp.ACTION_MOCK_SUPPLIER_A_PAYMENT_INTENT
        ),
        lambda: _projection(packet=wrong_adapter_packet),
    )
    for build in invalid_builds:
        with pytest.raises(ValueError):
            build()
    valid = _projection()
    assert acp.validate_supplier_action_commit_packet_canonical_projection_v01(
        valid
    ) == (True, ())


@pytest.mark.parametrize(
    ("mutation", "expected_reason"),
    (
        ("transaction", "cross_profile_transaction_mismatch"),
        ("root", "cross_profile_root_mismatch"),
        ("subject", "cross_profile_subject_scope_mismatch"),
        ("target", "cross_profile_target_scope_mismatch"),
        ("corridor", "cross_profile_corridor_mismatch"),
        ("policy", "cross_profile_policy_version_mismatch"),
        ("namespace", "cross_profile_namespace_mismatch"),
        ("effect", "cross_profile_effect_class_mismatch"),
    ),
)
def test_cross_profile_coherence_mismatch_classes(
    mutation: str,
    expected_reason: str,
) -> None:
    projection = _projection()
    changed = projection
    if mutation == "transaction":
        _, idempotency = _rebuild_logical(
            projection, transaction_id="transaction:other"
        )
        changed = replace(projection, idempotency_identity=idempotency)
    elif mutation == "root":
        business = replace(
            projection.business_object_identity,
            owning_effect_root_id="root:other",
        )
        changed = replace(projection, business_object_identity=business)
    elif mutation == "subject":
        changed = replace(
            projection,
            normalized_subject_scope=(
                acp.build_action_subject_scope_profile_v01(
                    included_subject_refs=("subject:other",),
                    excluded_subject_refs=(),
                )
            ),
        )
    elif mutation == "target":
        changed = replace(
            projection,
            normalized_target_scope=acp.build_action_target_scope_profile_v01(
                included_target_refs=("target:other",),
                excluded_target_refs=(),
            ),
        )
    elif mutation == "corridor":
        changed = replace(
            projection,
            adapter_binding=replace(
                projection.adapter_binding,
                corridor_class="corridor:other",
            ),
        )
    elif mutation == "policy":
        changed = replace(
            projection,
            authority_policy=_policy(policy_version="supplier_policy_v02"),
        )
    elif mutation == "namespace":
        changed = replace(
            projection,
            authority_policy=_policy(logical_namespace="supplier.other"),
        )
    else:
        changed = replace(
            projection,
            normalized_effect_parameters=(
                acp.build_action_effect_parameters_profile_v01(
                    effect_class="SHIPMENT",
                    parameter_records=(
                        projection.normalized_effect_parameters.parameter_records
                    ),
                )
            ),
        )
    valid, reasons = acp.validate_g2a1a_cross_profile_coherence_v01(
        changed,
        selected_canonical_action=projection.selected_canonical_action,
        selected_canonical_adapter=projection.adapter_binding.adapter_id,
    )
    assert valid is False
    assert expected_reason in reasons


def test_cross_profile_permission_membership_failures() -> None:
    projection = _projection()
    cases = (
        (
            "mock_adapter:other",
            projection.selected_canonical_action,
            "cross_profile_adapter_not_allowed",
        ),
        (
            projection.adapter_binding.adapter_id,
            "mock_action:other",
            "cross_profile_action_not_allowed",
        ),
    )
    for adapter, action, reason in cases:
        valid, reasons = acp.validate_g2a1a_cross_profile_coherence_v01(
            projection,
            selected_canonical_action=action,
            selected_canonical_adapter=adapter,
        )
        assert valid is False
        assert reason in reasons

    prohibited = replace(
        projection.normalized_permission_scope,
        prohibited_effect_classes=("PAYMENT",),
    )
    changed = replace(projection, normalized_permission_scope=prohibited)
    valid, reasons = acp.validate_g2a1a_cross_profile_coherence_v01(
        changed,
        selected_canonical_action=projection.selected_canonical_action,
        selected_canonical_adapter=projection.adapter_binding.adapter_id,
    )
    assert valid is False
    assert "cross_profile_effect_prohibited" in reasons

    adapter_forbidden_permission = (
        acp.build_action_permission_scope_profile_v01(
            allowed_action_classes=(
                projection.normalized_permission_scope.allowed_action_classes
            ),
            forbidden_action_classes=(),
            allowed_adapter_ids=("mock_adapter:bank_a_mock",),
            forbidden_adapter_ids=(projection.adapter_binding.adapter_id,),
            required_approval_refs=(PERMISSION_REF,),
            prohibited_effect_classes=(),
        )
    )
    changed = replace(
        projection,
        normalized_permission_scope=adapter_forbidden_permission,
    )
    valid, reasons = acp.validate_g2a1a_cross_profile_coherence_v01(
        changed,
        selected_canonical_action=projection.selected_canonical_action,
        selected_canonical_adapter=projection.adapter_binding.adapter_id,
    )
    assert valid is False
    assert "cross_profile_adapter_forbidden" in reasons

    action_forbidden_permission = (
        acp.build_action_permission_scope_profile_v01(
            allowed_action_classes=(
                "mock_action:mock_supplier_a_payment_intent",
            ),
            forbidden_action_classes=(projection.selected_canonical_action,),
            allowed_adapter_ids=(
                projection.normalized_permission_scope.allowed_adapter_ids
            ),
            forbidden_adapter_ids=(),
            required_approval_refs=(PERMISSION_REF,),
            prohibited_effect_classes=(),
        )
    )
    changed = replace(
        projection,
        normalized_permission_scope=action_forbidden_permission,
    )
    valid, reasons = acp.validate_g2a1a_cross_profile_coherence_v01(
        changed,
        selected_canonical_action=projection.selected_canonical_action,
        selected_canonical_adapter=projection.adapter_binding.adapter_id,
    )
    assert valid is False
    assert "cross_profile_action_forbidden" in reasons


def test_cross_profile_policy_membership_and_parameter_projection_failures() -> None:
    projection = _projection()
    wrong_business_policy = _policy(
        business_namespaces=("supplier.other",)
    )
    changed_policy = replace(
        projection,
        authority_policy=wrong_business_policy,
    )
    valid, reasons = acp.validate_g2a1a_cross_profile_coherence_v01(
        changed_policy,
        selected_canonical_action=projection.selected_canonical_action,
        selected_canonical_adapter=projection.adapter_binding.adapter_id,
    )
    assert valid is False
    assert "cross_profile_business_namespace_not_allowed" in reasons

    changed_policy = replace(
        projection,
        authority_policy=_policy(effect_classes=("SHIPMENT",)),
    )
    valid, reasons = acp.validate_g2a1a_cross_profile_coherence_v01(
        changed_policy,
        selected_canonical_action=projection.selected_canonical_action,
        selected_canonical_adapter=projection.adapter_binding.adapter_id,
    )
    assert valid is False
    assert "cross_profile_effect_class_not_allowed" in reasons

    changed_policy = replace(
        projection,
        authority_policy=_policy(corridor_classes=("corridor:other",)),
    )
    valid, reasons = acp.validate_g2a1a_cross_profile_coherence_v01(
        changed_policy,
        selected_canonical_action=projection.selected_canonical_action,
        selected_canonical_adapter=projection.adapter_binding.adapter_id,
    )
    assert valid is False
    assert "cross_profile_corridor_not_allowed" in reasons

    altered_effect = replace(
        projection.normalized_effect_parameters,
        parameter_records=(
            acp.build_action_effect_parameter_record_v01(
                parameter_name="amount_decimal",
                value_type="DECIMAL",
                value="999",
            ),
            acp.build_action_effect_parameter_record_v01(
                parameter_name="currency_code",
                value_type="TEXT",
                value="EUR",
            ),
        ),
    )
    changed_effect = replace(
        projection,
        normalized_effect_parameters=altered_effect,
    )
    valid, reasons = acp.validate_g2a1a_cross_profile_coherence_v01(
        changed_effect,
        selected_canonical_action=projection.selected_canonical_action,
        selected_canonical_adapter=projection.adapter_binding.adapter_id,
    )
    assert valid is False
    assert "cross_profile_parameter_projection_mismatch" in reasons


def test_material_reorder_invalidates_profile_contract() -> None:
    material = acp.action_subject_scope_material_v01(
        _projection().normalized_subject_scope
    )
    reordered = (material[1], material[0], material[2])
    valid, reasons = acp.validate_canonical_profile_material_v01(
        reordered,
        expected_field_names=(
            "profile_id",
            "included_subject_refs",
            "excluded_subject_refs",
        ),
    )
    assert valid is False
    assert "canonical_material_field_order_invalid" in reasons
    assert canonical_json_bytes_v01(reordered) != canonical_json_bytes_v01(
        material
    )


def test_new_total_validators_do_not_throw_on_malformed_objects() -> None:
    validators = (
        acp.validate_action_subject_scope_profile_v01,
        acp.validate_action_target_scope_profile_v01,
        acp.validate_action_permission_scope_profile_v01,
        acp.validate_action_effect_parameter_record_v01,
        acp.validate_action_effect_parameters_profile_v01,
        acp.validate_action_adapter_binding_profile_v01,
        acp.validate_dependency_set_candidate_record_v01,
        acp.validate_dependency_set_candidate_v01,
        acp.validate_packet_dependency_acceptance_binding_v01,
        acp.validate_action_temporal_authority_profile_v01,
        acp.validate_logical_time_bridge_v01,
        acp.validate_action_authority_policy_profile_v01,
        acp.validate_action_business_object_identity_profile_v01,
        acp.validate_action_consequential_effect_parameters_profile_v01,
        acp.validate_root_owned_logical_effect_intent_v01,
        acp.validate_action_idempotency_identity_v01,
        acp.validate_root_bound_packet_authorization_candidate_v01,
        acp.validate_effect_firewall_vocabulary_projection_v01,
        acp.validate_supplier_action_commit_packet_canonical_projection_v01,
    )
    for malformed in (None, True, 1, 1.0, "", (), [], {}, object()):
        for validator in validators:
            valid, reasons = validator(malformed)
            assert valid is False
            assert reasons

    projection = _projection()
    malformed_projection = replace(projection, adapter_binding=object())
    assert acp.validate_supplier_action_commit_packet_canonical_projection_v01(
        malformed_projection
    )[0] is False
    malformed_vocabulary = acp.EffectFirewallVocabularyProjectionV01(
        identifier_kind="adapter",
        raw_identifier=[],  # type: ignore[arg-type]
        canonical_identifier="mock_adapter:mock_bank_sandbox",
        compatibility_mode=True,
    )
    assert acp.validate_effect_firewall_vocabulary_projection_v01(
        malformed_vocabulary
    )[0] is False


def test_public_validator_control_arguments_are_total() -> None:
    projection = _projection()
    calls = (
        lambda: acp.validate_identity_text_v01("value", allow_empty=None),
        lambda: acp.validate_set_like_string_tuple_v01(
            ("value",),
            require_non_empty=[],
        ),
        lambda: acp.validate_canonical_profile_material_v01(
            (("field", "value"),),
            expected_field_names={"field": "value"},
        ),
        lambda: acp.validate_prefixed_sha256_identity_v01(
            "prefix:" + "a" * 64,
            prefix=[],
        ),
        lambda: acp.validate_native_effect_firewall_identifier_v01(
            "mock_adapter:value",
            identifier_kind={},
        ),
        lambda: acp.validate_g2a1a_cross_profile_coherence_v01(
            projection,
            selected_canonical_action=[],
            selected_canonical_adapter={},
        ),
        lambda: acp.validate_g2a1a_cross_profile_coherence_v01(projection),
        lambda: acp.validate_action_commit_packet_identity_v01(
            object(),
            candidate=[],
            source_root_decision_id={},
            source_root_decision_hash=None,
        ),
    )
    for call in calls:
        valid, reasons = call()
        assert valid is False
        assert reasons
        assert all(
            isinstance(reason, str) and reason
            for reason in reasons
        )


def test_historical_supplier_contract_remains_byte_for_byte_observable() -> None:
    packet = acp.build_supplier_a_mock_action_commit_packet_fixture_v02()
    assert acp.validate_action_commit_packet_v02(packet) == (True, ())
    assert packet.packet_id == "acp_v02:supplier_a_mock_payment:inv_2042"
    assert packet.idempotency.key == (
        "idem:acp_v02:supplier_a_mock_payment:inv_2042"
    )
    assert packet.human_approval_ref == "human_approval:supplier_a_scope_only"
    assert packet.scope.allowed_actions == (
        "mock_supplier_a_payment_intent",
        "mock_supplier_a_payment_order",
    )
    assert packet.scope.allowed_adapters == ("mock_bank_sandbox", "bank_a_mock")
    assert packet.adapter_binding.adapter_version is None


def test_frozen_root_packet_authorization_path_is_exact(
    root_bound_fixture: _RootBoundFixtureV01,
) -> None:
    fixture = root_bound_fixture
    candidate_id = (
        fixture.canonical_projection.authorization_candidate
        .root_packet_authorization_candidate_id
    )
    assert root_decision.validate_root_decision_kernel_v01(
        fixture.root_decision_kernel
    ) == ()
    assert root_decision.validate_root_decision_input_v01(
        kernel=fixture.root_decision_kernel,
        decision_input=fixture.root_decision_input,
    ) == ()
    assert root_decision.validate_root_decision_result_v01(
        kernel=fixture.root_decision_kernel,
        decision_input=fixture.root_decision_input,
        result=fixture.root_decision_result,
    ) == ()
    assert fixture.root_decision_result.decision == "ACCEPT"
    assert (
        fixture.root_decision_result.reason_code
        == "validated_candidate_accepted"
    )
    assert fixture.root_decision_result.selected_candidate_id == candidate_id
    assert fixture.root_decision_result.root_commit_created is True
    assert fixture.root_decision_result.permission_created is False
    assert fixture.root_decision_result.final_output_created is False
    assert fixture.root_decision_result.effect_requested is False
    assert acp.validate_root_decision_candidate_projection_v01(
        fixture.root_projection
    ) == (True, ())
    plain = root_decision.root_decision_input_to_plain_dict_v01(
        fixture.root_decision_input
    )
    claims = plain["root_review_packet"]["synthesis_proposal"][
        "normalized_claims"
    ]
    assert [claim["claim_id"] for claim in claims].count(candidate_id) == 1
    assert plain["post_vv_bundle"]["validated_candidate_ids"].count(
        candidate_id
    ) == 1
    assert candidate_id not in plain["post_vv_bundle"][
        "rejected_candidate_ids"
    ]
    assert plain["gt_advisory"]["candidate_ids"].count(candidate_id) == 1
    assert plain["gt_advisory"]["selected_candidate_id"] == candidate_id


def test_source_root_decision_hash_uses_exact_frozen_projection(
    root_bound_fixture: _RootBoundFixtureV01,
) -> None:
    result = root_bound_fixture.root_decision_result
    plain = root_decision.root_decision_result_to_plain_dict_v01(result)
    expected = domain_separated_sha256_hex_v01(
        domain="HEDGEHOG_ACTION_SOURCE_ROOT_DECISION_V01",
        payload=canonical_json_bytes_v01(plain),
    )
    first = acp.build_action_source_root_decision_hash_v01(result)
    second = acp.build_action_source_root_decision_hash_v01(result)
    assert first == second == expected
    assert root_bound_fixture.root_projection.source_root_decision_hash == expected
    with pytest.raises(ValueError, match="source_root_decision_result_type_invalid"):
        acp.build_action_source_root_decision_hash_v01(object())
    forged = replace(
        root_bound_fixture.root_projection,
        source_root_decision_hash="0" * 64,
    )
    valid, reasons = acp.validate_root_decision_candidate_projection_v01(
        forged
    )
    assert valid is False
    assert "source_root_decision_hash_mismatch" in reasons


def test_utc_formatter_exact_round_trip_and_boundaries() -> None:
    examples = (
        (0, "1970-01-01T00:00:00Z"),
        (
            acp.parse_utc_timestamp_v01("0001-01-01T00:00:00Z"),
            "0001-01-01T00:00:00Z",
        ),
        (
            acp.parse_utc_timestamp_v01("9999-12-31T23:59:59Z"),
            "9999-12-31T23:59:59Z",
        ),
    )
    for epoch, expected in examples:
        formatted = acp.format_utc_timestamp_v01(epoch)
        assert formatted == expected
        assert acp.parse_utc_timestamp_v01(formatted) == epoch
    with pytest.raises(ValueError):
        acp.format_utc_timestamp_v01(True)
    for epoch in (
        acp.parse_utc_timestamp_v01("0001-01-01T00:00:00Z") - 1,
        acp.parse_utc_timestamp_v01("9999-12-31T23:59:59Z") + 1,
    ):
        with pytest.raises(ValueError, match="timestamp_output_range_invalid"):
            acp.format_utc_timestamp_v01(epoch)


def test_root_bound_supplier_operational_projection_exact(
    root_bound_fixture: _RootBoundFixtureV01,
) -> None:
    bound = root_bound_fixture.root_bound_projection
    canonical = bound.canonical_projection
    root_projection = bound.root_decision_projection
    packet = bound.packet
    historical = acp.build_supplier_a_mock_action_commit_packet_fixture_v02()
    assert acp.validate_supplier_root_bound_action_commit_packet_v02_projection_v01(
        bound
    ) == (True, ())
    assert acp.validate_action_commit_packet_v02(packet) == (True, ())
    assert packet.packet_id == bound.packet_identity.packet_id
    assert packet.source_root_decision_ref == (
        root_projection.root_decision_result.decision_id
    )
    assert packet.root_boundary_ref == (
        root_projection.root_decision_input.decision_input_id
    )
    assert packet.idempotency.key == canonical.idempotency_identity.idempotency_key
    assert packet.scope.allowed_actions == (
        canonical.normalized_permission_scope.allowed_action_classes
    )
    assert packet.scope.allowed_adapters == (
        canonical.normalized_permission_scope.allowed_adapter_ids
    )
    assert packet.scope.forbidden_actions == historical.scope.forbidden_actions
    assert packet.scope.forbidden_adapters == historical.scope.forbidden_adapters
    assert packet.scope.payment_slot_ref == (
        canonical.business_object_identity.business_object_ref
    )
    assert packet.scope.creditor_ref == historical.scope.creditor_ref
    assert packet.scope.amount == (
        canonical.consequential_effect_parameters.amount_decimal
    )
    assert packet.scope.currency == (
        canonical.consequential_effect_parameters.currency_code
    )
    assert acp.parse_utc_timestamp_v01(packet.ttl.created_at) == (
        canonical.temporal_authority.issued_at_utc
    )
    assert acp.parse_utc_timestamp_v01(packet.ttl.expires_at) == (
        canonical.temporal_authority.expires_at_utc
    )
    assert packet.adapter_binding.adapter_id == canonical.adapter_binding.adapter_id
    assert packet.adapter_binding.adapter_version == (
        acp.PRE_G2A_ADAPTER_VERSION_V01
    )
    assert packet.human_approval_ref == historical.human_approval_ref
    assert packet.human_approval_ref != canonical.canonical_permission_ref
    assert packet.evidence_refs[:-2] == historical.evidence_refs
    assert packet.evidence_refs[-2] == acp.PacketEvidenceRefV02(
        evidence_id=root_projection.root_decision_result.decision_id,
        evidence_kind="root_decision_result_v01",
        source_ref=root_projection.root_decision_input.decision_input_id,
    )
    assert packet.evidence_refs[-1] == acp.PacketEvidenceRefV02(
        evidence_id=(
            bound.dependency_acceptance_binding
            .packet_dependency_acceptance_binding_id
        ),
        evidence_kind="packet_dependency_acceptance_binding_v01",
        source_ref=canonical.dependency_set_candidate_fingerprint,
    )
    assert packet.drs_refs == canonical.advisory_drs_refs
    assert packet.avf_refs == canonical.advisory_avf_refs
    assert packet.bsep_ref == canonical.advisory_bsep_ref
    assert packet.receipt_evidence_only is True
    assert packet.real_world_effects_allowed is False
    assert packet.production_ready_claimed is False
    assert packet.public_auditor_ready_claimed is False
    assert not hasattr(bound, "effect_request")
    assert not hasattr(bound, "capability")
    assert not hasattr(bound, "lifecycle_state")
    assert not hasattr(bound, "receipt")


def test_deterministic_root_bound_vector_is_literal_and_independent(
    root_bound_fixture: _RootBoundFixtureV01,
) -> None:
    fixture = root_bound_fixture
    bound = fixture.root_bound_projection
    assert fixture.root_decision_input.decision_input_id == (
        "272ec4a39708ae67a5d2b5654f4386d4d2452001c1f90cc8c2d1bba62337e114"
    )
    assert fixture.root_decision_result.decision_id == (
        "9d6eebcabb9d3e3474d9bf733fc0db96b26bc4dcc7acc7aac3df3fc2a3b4715d"
    )
    result_plain = root_decision.root_decision_result_to_plain_dict_v01(
        fixture.root_decision_result
    )
    independent_source_hash = domain_separated_sha256_hex_v01(
        domain="HEDGEHOG_ACTION_SOURCE_ROOT_DECISION_V01",
        payload=canonical_json_bytes_v01(result_plain),
    )
    assert independent_source_hash == (
        "d1585fe0d5d98d5333cc9a7b6321c724f13ef808a924a7d605ce5312211ec472"
    )
    packet_material = acp.action_commit_packet_identity_material_v01(
        candidate=fixture.canonical_projection.authorization_candidate,
        source_root_decision_id=fixture.root_decision_result.decision_id,
        source_root_decision_hash=independent_source_hash,
    )
    independent_packet_id = "acp_v02:" + domain_separated_sha256_hex_v01(
        domain="HEDGEHOG_ACTION_COMMIT_PACKET_ID_V01",
        payload=canonical_json_bytes_v01(packet_material),
    )
    assert independent_packet_id == (
        "acp_v02:"
        "d8e807c09eb63732b2af7ecf6afbb3de59fe90e04aa36af5bd40425a210470d2"
    )
    binding_material = (
        acp.packet_dependency_acceptance_binding_material_v01(
            bound.dependency_acceptance_binding
        )
    )
    independent_binding_id = (
        "packet_dependency_acceptance_v01:"
        + domain_separated_sha256_hex_v01(
            domain="HEDGEHOG_PACKET_DEPENDENCY_ACCEPTANCE_BINDING_V01",
            payload=canonical_json_bytes_v01(binding_material),
        )
    )
    assert independent_binding_id == (
        "packet_dependency_acceptance_v01:"
        "339c8f4e31cbd5bb3e0a7a43e018b4b366a1a27fd19203b63f49ef9910186010"
    )
    assert fixture.root_projection.source_root_decision_hash == (
        independent_source_hash
    )
    assert bound.packet_identity.packet_id == independent_packet_id
    assert (
        bound.dependency_acceptance_binding
        .packet_dependency_acceptance_binding_id
        == independent_binding_id
    )


def test_root_candidate_required_surface_substitutions_fail_closed(
    root_bound_fixture: _RootBoundFixtureV01,
) -> None:
    fixture = root_bound_fixture
    candidate_id = (
        fixture.canonical_projection.authorization_candidate
        .root_packet_authorization_candidate_id
    )
    other_candidate = "root_packet_authorization_v01:" + "f" * 64

    _, other_review, _, _, _ = _build_frozen_root_evidence(
        fixture.canonical_projection,
        candidate_id=other_candidate,
    )
    review_input = replace(
        fixture.root_decision_input,
        root_review_packet=other_review,
    )
    variants = [
        _unchecked_root_projection(
            fixture,
            decision_input=review_input,
        )
    ]
    input_plain = root_decision.root_decision_input_to_plain_dict_v01(
        fixture.root_decision_input
    )
    for state_name, updates in (
        (
            "post_vv_bundle",
            {"validated_candidate_ids": [other_candidate]},
        ),
        (
            "post_vv_bundle",
            {"rejected_candidate_ids": [candidate_id]},
        ),
        (
            "gt_advisory",
            {
                "candidate_ids": [other_candidate],
                "selected_candidate_id": other_candidate,
                "score_micros_by_candidate": {other_candidate: 1_000_000},
            },
        ),
        (
            "gt_advisory",
            {
                "candidate_ids": [candidate_id, other_candidate],
                "selected_candidate_id": other_candidate,
                "score_micros_by_candidate": {
                    candidate_id: 1_000_000,
                    other_candidate: 999_999,
                },
            },
        ),
    ):
        altered_state = dict(input_plain[state_name])
        altered_state.update(updates)
        decision_input = replace(
            fixture.root_decision_input,
            **{state_name: altered_state},
        )
        variants.append(
            _unchecked_root_projection(
                fixture,
                decision_input=decision_input,
            )
        )

    for projection in variants:
        valid, reasons = acp.validate_root_decision_candidate_projection_v01(
            projection
        )
        assert valid is False
        assert reasons


def test_root_candidate_result_and_context_substitutions_fail_closed(
    root_bound_fixture: _RootBoundFixtureV01,
) -> None:
    fixture = root_bound_fixture
    candidate_id = (
        fixture.canonical_projection.authorization_candidate
        .root_packet_authorization_candidate_id
    )
    other_candidate = "root_packet_authorization_v01:" + "f" * 64
    _, _, _, other_input, other_result = _build_frozen_root_evidence(
        fixture.canonical_projection,
        candidate_id=other_candidate,
    )
    wrong_kernel = replace(
        fixture.root_decision_kernel,
        kernel_id="0" * 64,
    )
    forged_results = (
        replace(
            fixture.root_decision_result,
            selected_candidate_id=other_candidate,
        ),
        replace(
            fixture.root_decision_result,
            decision="REJECT",
            reason_code="policy_rejected_candidate",
            selected_candidate_id=None,
            root_commit_created=False,
        ),
    )
    variants = [
        _unchecked_root_projection(
            fixture,
            decision_input=other_input,
            result=fixture.root_decision_result,
        ),
        _unchecked_root_projection(
            fixture,
            decision_input=fixture.root_decision_input,
            result=other_result,
        ),
        _unchecked_root_projection(fixture, kernel=wrong_kernel),
        *(
            _unchecked_root_projection(fixture, result=result)
            for result in forged_results
        ),
    ]
    for projection in variants:
        valid, reasons = acp.validate_root_decision_candidate_projection_v01(
            projection
        )
        assert valid is False
        assert reasons
    assert candidate_id != other_candidate


@pytest.mark.parametrize(
    "state_updates",
    [
        {
            "permission_state": {
                "user_permission_present": False,
            }
        },
        {
            "permission_state": {
                "permission_scope_valid": False,
            }
        },
        {
            "permission_state": {
                "permission_ref": "human_approval:not_permission",
            }
        },
        {
            "policy_state": {
                "hard_policy_passed": False,
            }
        },
        {
            "temporal_state": {
                "temporal_valid": False,
                "expired": True,
            }
        },
    ],
)
def test_root_candidate_hard_conditions_fail_closed(
    root_bound_fixture: _RootBoundFixtureV01,
    state_updates: dict[str, dict[str, object]],
) -> None:
    decision_input, result = _rebuild_frozen_root_input(
        root_bound_fixture,
        state_updates=state_updates,
    )
    projection = _unchecked_root_projection(
        root_bound_fixture,
        decision_input=decision_input,
        result=result,
    )
    valid, reasons = acp.validate_root_decision_candidate_projection_v01(
        projection
    )
    assert valid is False
    assert reasons


def test_root_candidate_material_conflict_fails_closed(
    root_bound_fixture: _RootBoundFixtureV01,
) -> None:
    decision_input = replace(
        root_bound_fixture.root_decision_input,
        conflict_state={
            "material_unresolved_conflict": True,
            "conflict_set_ids": ["conflict:material"],
        },
    )
    projection = _unchecked_root_projection(
        root_bound_fixture,
        decision_input=decision_input,
    )
    valid, reasons = acp.validate_root_decision_candidate_projection_v01(
        projection
    )
    assert valid is False
    assert reasons


def test_root_candidate_source_hash_and_totality_fail_closed(
    root_bound_fixture: _RootBoundFixtureV01,
) -> None:
    forged = replace(
        root_bound_fixture.root_projection,
        source_root_decision_hash="0" * 64,
    )
    assert acp.validate_root_decision_candidate_projection_v01(forged)[0] is False
    for malformed in (
        None,
        {},
        [],
        "root projection",
        object(),
    ):
        valid, reasons = acp.validate_root_decision_candidate_projection_v01(
            malformed
        )
        assert valid is False
        assert reasons


def test_packet_specific_root_context_substitutions_fail_closed(
    root_bound_fixture: _RootBoundFixtureV01,
) -> None:
    fixture = root_bound_fixture
    canonical = fixture.canonical_projection
    other_candidate = "root_packet_authorization_v01:" + "f" * 64
    _, _, _, candidate_input, candidate_result = _build_frozen_root_evidence(
        canonical,
        candidate_id=other_candidate,
    )
    candidate_projection = _root_projection_from_valid_evidence(
        fixture,
        candidate_id=other_candidate,
        decision_input=candidate_input,
        result=candidate_result,
    )
    _, _, _, transaction_input, transaction_result = (
        _build_frozen_root_evidence(
            canonical,
            transaction_id="transaction:other",
        )
    )
    transaction_projection = _root_projection_from_valid_evidence(
        fixture,
        candidate_id=(
            canonical.authorization_candidate
            .root_packet_authorization_candidate_id
        ),
        decision_input=transaction_input,
        result=transaction_result,
    )
    _, _, _, root_input, root_result = _build_frozen_root_evidence(
        canonical,
        target_root_id="root:foreign",
    )
    root_projection = _root_projection_from_valid_evidence(
        fixture,
        candidate_id=(
            canonical.authorization_candidate
            .root_packet_authorization_candidate_id
        ),
        decision_input=root_input,
        result=root_result,
    )

    valid_context_variants = []
    for updates in (
        {
            "permission_state": {
                "permission_ref": "permission:other",
            }
        },
        {
            "policy_state": {
                "policy_id": "policy:other",
            }
        },
        {
            "temporal_state": {
                "time_envelope_ref": "time_envelope:other",
            }
        },
        {
            "post_vv_bundle": {
                "required_evidence_refs": [],
                "provided_evidence_refs": [],
            }
        },
        {
            "prior_root_state": {
                "prior_decision_id": "a" * 64,
                "prior_decision": "ACCEPT",
                "prior_selected_candidate_id": (
                    canonical.authorization_candidate
                    .root_packet_authorization_candidate_id
                ),
            }
        },
    ):
        decision_input, result = _rebuild_frozen_root_input(
            fixture,
            state_updates=updates,
        )
        valid_context_variants.append(
            _root_projection_from_valid_evidence(
                fixture,
                candidate_id=(
                    canonical.authorization_candidate
                    .root_packet_authorization_candidate_id
                ),
                decision_input=decision_input,
                result=result,
            )
        )

    required_only_input, required_only_result = _rebuild_frozen_root_input(
        fixture,
        state_updates={
            "post_vv_bundle": {
                "provided_evidence_refs": [],
            }
        },
    )
    required_only_projection = _unchecked_root_projection(
        fixture,
        decision_input=required_only_input,
        result=required_only_result,
    )

    variants = (
        candidate_projection,
        transaction_projection,
        root_projection,
        *valid_context_variants,
        required_only_projection,
    )
    for projection in variants:
        valid, reasons = acp.validate_supplier_root_context_coherence_v01(
            canonical,
            projection,
        )
        assert valid is False
        assert reasons


def test_initial_supplier_context_rejects_predecessor_candidate(
    root_bound_fixture: _RootBoundFixtureV01,
) -> None:
    canonical = root_bound_fixture.canonical_projection
    base = canonical.authorization_candidate
    predecessor_candidate = (
        acp.build_root_bound_packet_authorization_candidate_v01(
            owning_local_root_id=base.owning_local_root_id,
            transaction_id=base.transaction_id,
            root_owned_intent_id=base.root_owned_intent_id,
            effect_class=base.effect_class,
            normalized_subject_scope=base.normalized_subject_scope,
            normalized_target_scope=base.normalized_target_scope,
            normalized_permission_scope=base.normalized_permission_scope,
            normalized_effect_parameters_fingerprint=(
                base.normalized_effect_parameters_fingerprint
            ),
            corridor_class=base.corridor_class,
            adapter_binding=base.adapter_binding,
            dependency_set_candidate_fingerprint=(
                base.dependency_set_candidate_fingerprint
            ),
            temporal_authority_fingerprint=(
                base.temporal_authority_fingerprint
            ),
            policy_version=base.policy_version,
            authority_policy_fingerprint=base.authority_policy_fingerprint,
            predecessor_packet_id="acp_v02:" + "a" * 64,
            supersession_reason_class="RENEWAL",
        )
    )
    altered = replace(canonical, authorization_candidate=predecessor_candidate)
    valid, reasons = acp.validate_supplier_root_context_coherence_v01(
        altered,
        root_bound_fixture.root_projection,
    )
    assert valid is False
    assert reasons


@pytest.mark.parametrize(
    "packet_mutator",
    [
        lambda packet: replace(packet, packet_id="acp_v02:" + "0" * 64),
        lambda packet: replace(packet, source_root_decision_ref="0" * 64),
        lambda packet: replace(packet, root_boundary_ref="0" * 64),
        lambda packet: replace(
            packet,
            idempotency=replace(packet.idempotency, key="idem:action_v01:" + "0" * 64),
        ),
        lambda packet: replace(
            packet,
            scope=replace(packet.scope, allowed_actions=("mock_action:other",)),
        ),
        lambda packet: replace(
            packet,
            scope=replace(packet.scope, allowed_adapters=("mock_adapter:other",)),
        ),
        lambda packet: replace(
            packet,
            scope=replace(packet.scope, creditor_ref="creditor:other"),
        ),
        lambda packet: replace(
            packet,
            scope=replace(packet.scope, payment_slot_ref="payment_slot:other"),
        ),
        lambda packet: replace(
            packet,
            scope=replace(packet.scope, amount="1"),
        ),
        lambda packet: replace(
            packet,
            scope=replace(packet.scope, currency="USD"),
        ),
        lambda packet: replace(
            packet,
            ttl=replace(packet.ttl, ttl_seconds=packet.ttl.ttl_seconds + 1),
        ),
        lambda packet: replace(
            packet,
            adapter_binding=replace(
                packet.adapter_binding,
                adapter_id="mock_adapter:bank_a_mock",
            ),
        ),
        lambda packet: replace(
            packet,
            adapter_binding=replace(
                packet.adapter_binding,
                adapter_version="adapter_version:other",
            ),
        ),
        lambda packet: replace(
            packet,
            evidence_refs=tuple(reversed(packet.evidence_refs)),
        ),
        lambda packet: replace(packet, drs_refs=("drs:other",)),
        lambda packet: replace(packet, avf_refs=("avf:other",)),
        lambda packet: replace(packet, bsep_ref="bsep:other"),
        lambda packet: replace(packet, receipt_evidence_only=False),
        lambda packet: replace(packet, real_world_effects_allowed=True),
        lambda packet: replace(packet, production_ready_claimed=True),
        lambda packet: replace(packet, public_auditor_ready_claimed=True),
    ],
)
def test_root_bound_operational_packet_drift_fails_closed(
    root_bound_fixture: _RootBoundFixtureV01,
    packet_mutator: object,
) -> None:
    bound = root_bound_fixture.root_bound_projection
    mutated_packet = packet_mutator(bound.packet)  # type: ignore[operator]
    mutated = replace(bound, packet=mutated_packet)
    valid, reasons = (
        acp.validate_supplier_root_bound_action_commit_packet_v02_projection_v01(
            mutated
        )
    )
    assert valid is False
    assert reasons


def test_root_bound_dependency_binding_and_evidence_drift_fail_closed(
    root_bound_fixture: _RootBoundFixtureV01,
) -> None:
    bound = root_bound_fixture.root_bound_projection
    binding = bound.dependency_acceptance_binding
    binding_variants = (
        replace(binding, dependency_set_candidate_fingerprint="0" * 64),
        replace(
            binding,
            root_packet_authorization_candidate_id=(
                "root_packet_authorization_v01:" + "0" * 64
            ),
        ),
        replace(binding, source_root_decision_id="0" * 64),
        replace(binding, source_root_decision_hash="0" * 64),
        replace(binding, owning_local_root_id="root:foreign"),
        replace(binding, packet_id="acp_v02:" + "0" * 64),
        replace(binding, accepted_status="ROOT_ACCEPTED_FOR_OTHER"),
        replace(
            binding,
            packet_dependency_acceptance_binding_id=(
                "packet_dependency_acceptance_v01:" + "0" * 64
            ),
        ),
    )
    for altered_binding in binding_variants:
        assert acp.validate_packet_dependency_acceptance_binding_v01(
            altered_binding
        )[0] is False
        altered = replace(
            bound,
            dependency_acceptance_binding=altered_binding,
        )
        assert (
            acp.validate_supplier_root_bound_action_commit_packet_v02_projection_v01(
                altered
            )[0]
            is False
        )

    altered_evidence = replace(
        bound.packet.evidence_refs[-1],
        evidence_id="packet_dependency_acceptance_v01:" + "0" * 64,
    )
    packet = replace(
        bound.packet,
        evidence_refs=(*bound.packet.evidence_refs[:-1], altered_evidence),
    )
    assert acp.validate_supplier_root_bound_action_commit_packet_v02_projection_v01(
        replace(bound, packet=packet)
    )[0] is False


def test_root_bound_builder_validator_closure_and_totality(
    root_bound_fixture: _RootBoundFixtureV01,
) -> None:
    fixture = root_bound_fixture
    rebuilt = (
        acp.build_supplier_root_bound_action_commit_packet_v02_projection_v01(
            canonical_projection=fixture.canonical_projection,
            root_decision_projection=fixture.root_projection,
        )
    )
    assert acp.validate_supplier_root_bound_action_commit_packet_v02_projection_v01(
        rebuilt
    ) == (True, ())
    for malformed in (None, {}, [], "packet projection", object()):
        valid, reasons = (
            acp.validate_supplier_root_bound_action_commit_packet_v02_projection_v01(
                malformed
            )
        )
        assert valid is False
        assert reasons
    with pytest.raises(ValueError):
        acp.build_supplier_root_bound_action_commit_packet_v02_projection_v01(
            canonical_projection=None,
            root_decision_projection=fixture.root_projection,
        )
    with pytest.raises(ValueError):
        acp.build_root_decision_candidate_projection_v01(
            candidate_kind="PACKET_AUTHORIZATION",
            projected_candidate_id="root_packet_authorization_v01:" + "0" * 64,
            root_decision_kernel=fixture.root_decision_kernel,
            root_decision_input=fixture.root_decision_input,
            root_decision_result=fixture.root_decision_result,
        )


def test_g2a1b_source_non_authority_boundary() -> None:
    source = Path(acp.__file__).read_text(encoding="utf-8")
    assert "decide_root_v01" not in source
    for forbidden in (
        "EffectFirewallV01(",
        "EffectRequestV01(",
    ):
        assert forbidden not in source
    tree = ast.parse(source)
    executor_imports = tuple(
        imported
        for node in ast.walk(tree)
        if (
            isinstance(node, ast.ImportFrom)
            and node.module == "hedgehog.kernel.effect_firewall_v01"
        )
        for imported in node.names
        if (
            imported.name == "execute_mock_effect_v01"
            and imported.asname == "_execute_mock_effect_v01"
        )
    )
    executor_calls = tuple(
        node
        for node in ast.walk(tree)
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "_execute_mock_effect_v01"
        )
    )
    unaliased_calls = tuple(
        node
        for node in ast.walk(tree)
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "execute_mock_effect_v01"
        )
    )
    alternate_executor_calls = tuple(
        node
        for node in ast.walk(tree)
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id.endswith("execute_mock_effect_v01")
            and node.func.id
            not in {"_execute_mock_effect_v01", "execute_mock_effect_v01"}
        )
    )
    assert len(executor_imports) == 1
    assert len(executor_calls) == 1
    assert unaliased_calls == ()
    assert alternate_executor_calls == ()
    assert "mock_connector_sandbox" not in source
    assert not any(
        isinstance(node, ast.ClassDef) and node.name == "EffectCapabilityV01"
        for node in ast.walk(tree)
    )


def test_supplier_projection_retains_exact_validated_source_packet() -> None:
    source = acp.build_supplier_a_mock_action_commit_packet_fixture_v02()
    before = source
    projection = _projection(packet=source)
    assert projection.source_packet is source
    assert projection.source_packet == before
    assert acp.validate_action_commit_packet_v02(source) == (True, ())

    invalid = replace(source, root_created=False)
    assert acp.validate_action_commit_packet_v02(invalid)[0] is False
    with pytest.raises(ValueError):
        _projection(packet=invalid)

    substituted = _mutate_supplier_source_packet(source, "creditor")
    forged = replace(projection, source_packet=substituted)
    valid, reasons = (
        acp.validate_supplier_action_commit_packet_canonical_projection_v01(
            forged
        )
    )
    assert valid is False
    assert "supplier_projection_source_rebuild_mismatch" in reasons


@pytest.mark.parametrize(
    "mutation",
    (
        "subject",
        "creditor",
        "payment_slot",
        "adapter_kind",
        "amount",
        "currency",
        "ttl",
        "issued_time",
        "expiry_time",
        "raw_compatibility",
        "human_approval",
        "advisory_lineage",
    ),
)
def test_coherent_source_mapping_drift_fails_complete_validation(
    mutation: str,
) -> None:
    source = acp.build_supplier_a_mock_action_commit_packet_fixture_v02()
    altered_source = _mutate_supplier_source_packet(source, mutation)
    assert acp.validate_action_commit_packet_v02(altered_source) == (True, ())
    coherent_for_altered_source = _projection(packet=altered_source)
    assert acp.validate_supplier_action_commit_packet_canonical_projection_v01(
        coherent_for_altered_source
    ) == (True, ())

    forged = replace(coherent_for_altered_source, source_packet=source)
    valid, reasons = (
        acp.validate_supplier_action_commit_packet_canonical_projection_v01(
            forged
        )
    )
    assert valid is False
    assert reasons


def test_coherent_allowed_vocabulary_source_drift_fails_closed() -> None:
    source = acp.build_supplier_a_mock_action_commit_packet_fixture_v02()
    source_without_action = _mutate_supplier_source_packet(
        source,
        "missing_action",
    )
    source_without_adapter = _mutate_supplier_source_packet(
        source,
        "missing_adapter",
    )
    base_projection = _projection(packet=source)
    missing_action_projection = _projection(packet=source_without_action)

    canonical_has_extra_action = replace(
        base_projection,
        source_packet=source_without_action,
    )
    canonical_misses_source_action = replace(
        missing_action_projection,
        source_packet=source,
    )
    canonical_has_extra_adapter = replace(
        base_projection,
        source_packet=source_without_adapter,
    )
    for forged in (
        canonical_has_extra_action,
        canonical_misses_source_action,
        canonical_has_extra_adapter,
    ):
        valid, reasons = (
            acp.validate_supplier_action_commit_packet_canonical_projection_v01(
                forged
            )
        )
        assert valid is False
        assert reasons


def test_coherent_adapter_version_and_quantity_forgery_fail_closed() -> None:
    projection = _projection()
    adapter = replace(
        projection.adapter_binding,
        adapter_version="pre_g2a_adapter_contract_v02",
    )
    base = projection.authorization_candidate
    candidate = acp.build_root_bound_packet_authorization_candidate_v01(
        owning_local_root_id=base.owning_local_root_id,
        transaction_id=base.transaction_id,
        root_owned_intent_id=base.root_owned_intent_id,
        effect_class=base.effect_class,
        normalized_subject_scope=base.normalized_subject_scope,
        normalized_target_scope=base.normalized_target_scope,
        normalized_permission_scope=base.normalized_permission_scope,
        normalized_effect_parameters_fingerprint=(
            base.normalized_effect_parameters_fingerprint
        ),
        corridor_class=base.corridor_class,
        adapter_binding=adapter,
        dependency_set_candidate_fingerprint=(
            base.dependency_set_candidate_fingerprint
        ),
        temporal_authority_fingerprint=base.temporal_authority_fingerprint,
        policy_version=base.policy_version,
        authority_policy_fingerprint=base.authority_policy_fingerprint,
    )
    coherent_adapter_forgery = replace(
        projection,
        adapter_binding=adapter,
        authorization_candidate=candidate,
    )

    quantity = (
        acp.build_action_consequential_effect_parameters_profile_v01(
            amount_decimal=(
                projection.consequential_effect_parameters.amount_decimal
            ),
            currency_code=(
                projection.consequential_effect_parameters.currency_code
            ),
            quantity_decimal="2",
            parameter_records=(),
        )
    )
    coherent_quantity_forgery = _rebuild_projection_with_consequential_parameters(
        projection,
        quantity,
    )
    for forged in (coherent_adapter_forgery, coherent_quantity_forgery):
        valid, reasons = (
            acp.validate_supplier_action_commit_packet_canonical_projection_v01(
                forged
            )
        )
        assert valid is False
        assert reasons


def test_alternate_valid_source_maps_through_root_bound_packet() -> None:
    source = acp.build_supplier_a_mock_action_commit_packet_fixture_v02()
    alternate = replace(
        source,
        packet_id="legacy:alternate_packet",
        source_root_decision_ref="legacy:alternate_root_ref",
        human_approval_ref="human_approval:alternate_supplier_scope",
        scope=replace(
            source.scope,
            allowed_subjects=("supplier_a_alternate",),
            payment_slot_ref="payment_slot:bank_a_mock:alternate",
            creditor_ref="creditor:alternate_supplier",
            amount="1300.00",
            currency="GBP",
        ),
        ttl=replace(
            source.ttl,
            created_at="2026-07-08T00:10:00Z",
            expires_at="2026-07-08T01:10:00Z",
        ),
        idempotency=replace(
            source.idempotency,
            key="legacy:alternate_idempotency",
        ),
    )
    assert acp.validate_action_commit_packet_v02(alternate) == (True, ())
    canonical = _projection(packet=alternate)
    assert canonical.source_packet is alternate
    assert canonical.normalized_subject_scope.included_subject_refs == (
        "supplier_a_alternate",
    )
    assert canonical.business_object_identity.business_object_ref == (
        alternate.scope.payment_slot_ref
    )
    assert canonical.consequential_effect_parameters.amount_decimal == "1300"
    assert canonical.consequential_effect_parameters.currency_code == "GBP"

    _, _, kernel, decision_input, result = _build_frozen_root_evidence(
        canonical
    )
    root_projection = acp.build_root_decision_candidate_projection_v01(
        candidate_kind="PACKET_AUTHORIZATION",
        projected_candidate_id=(
            canonical.authorization_candidate
            .root_packet_authorization_candidate_id
        ),
        root_decision_kernel=kernel,
        root_decision_input=decision_input,
        root_decision_result=result,
    )
    bound = acp.build_supplier_root_bound_action_commit_packet_v02_projection_v01(
        canonical_projection=canonical,
        root_decision_projection=root_projection,
    )
    assert bound.packet.packet_id != alternate.packet_id
    assert bound.packet.source_root_decision_ref != (
        alternate.source_root_decision_ref
    )
    assert bound.packet.idempotency.key != alternate.idempotency.key
    assert bound.packet.scope.allowed_subjects == alternate.scope.allowed_subjects
    assert bound.packet.scope.creditor_ref == alternate.scope.creditor_ref
    assert bound.packet.scope.payment_slot_ref == alternate.scope.payment_slot_ref
    assert bound.packet.scope.amount == "1300"
    assert bound.packet.scope.currency == "GBP"
    assert bound.packet.ttl.created_at == alternate.ttl.created_at
    assert bound.packet.ttl.expires_at == alternate.ttl.expires_at
    assert bound.packet.adapter_binding.adapter_id == (
        "mock_adapter:mock_bank_sandbox"
    )


def test_temporal_evaluation_is_retained_and_packet_specific() -> None:
    source = acp.build_supplier_a_mock_action_commit_packet_fixture_v02()
    issued = acp.parse_utc_timestamp_v01(source.ttl.created_at)
    expires = acp.parse_utc_timestamp_v01(source.ttl.expires_at)
    cases = (
        (
            issued - 1,
            acp.TEMPORAL_OUTCOME_NOT_YET_VALID_V01,
            False,
        ),
        (issued, acp.TEMPORAL_OUTCOME_VALID_V01, True),
        (expires - 1, acp.TEMPORAL_OUTCOME_VALID_V01, True),
    )
    projections = {}
    for evaluation_time, outcome, executable in cases:
        projection = _projection(
            packet=source,
            evaluation_time=evaluation_time,
        )
        projections[outcome, evaluation_time] = projection
        assert projection.evaluation_time == evaluation_time
        assert projection.evaluation_time_source == EVALUATION_TIME_SOURCE
        assert projection.evaluation_context_id == EVALUATION_CONTEXT_ID
        assert projection.temporal_evaluation == acp.TemporalEvaluationV01(
            outcome=outcome,
            executable=executable,
        )
        assert acp.validate_supplier_action_commit_packet_canonical_projection_v01(
            projection
        ) == (True, ())

    not_yet_valid = projections[
        acp.TEMPORAL_OUTCOME_NOT_YET_VALID_V01,
        issued - 1,
    ]
    _, _, kernel, decision_input, result = _build_frozen_root_evidence(
        not_yet_valid
    )
    root_projection = acp.build_root_decision_candidate_projection_v01(
        candidate_kind="PACKET_AUTHORIZATION",
        projected_candidate_id=(
            not_yet_valid.authorization_candidate
            .root_packet_authorization_candidate_id
        ),
        root_decision_kernel=kernel,
        root_decision_input=decision_input,
        root_decision_result=result,
    )
    assert acp.validate_root_decision_candidate_projection_v01(
        root_projection
    ) == (True, ())
    assert acp.validate_supplier_root_context_coherence_v01(
        not_yet_valid,
        root_projection,
    )[0] is False
    with pytest.raises(ValueError):
        acp.build_supplier_root_bound_action_commit_packet_v02_projection_v01(
            canonical_projection=not_yet_valid,
            root_decision_projection=root_projection,
        )

    for evaluation_time in (issued, expires - 1):
        projection = projections[
            acp.TEMPORAL_OUTCOME_VALID_V01,
            evaluation_time,
        ]
        _, _, kernel, decision_input, result = _build_frozen_root_evidence(
            projection
        )
        root_projection = acp.build_root_decision_candidate_projection_v01(
            candidate_kind="PACKET_AUTHORIZATION",
            projected_candidate_id=(
                projection.authorization_candidate
                .root_packet_authorization_candidate_id
            ),
            root_decision_kernel=kernel,
            root_decision_input=decision_input,
            root_decision_result=result,
        )
        assert acp.validate_root_decision_candidate_projection_v01(
            root_projection
        ) == (True, ())
        assert acp.validate_supplier_root_context_coherence_v01(
            projection,
            root_projection,
        ) == (True, ())
        bound = (
            acp.build_supplier_root_bound_action_commit_packet_v02_projection_v01(
                canonical_projection=projection,
                root_decision_projection=root_projection,
            )
        )
        assert bound.packet.ttl.expired is False

    assert acp.evaluate_temporal_authority_v01(
        projections[
            acp.TEMPORAL_OUTCOME_VALID_V01,
            expires - 1,
        ].temporal_authority,
        evaluation_time=expires,
    ) == acp.TemporalEvaluationV01(
        outcome=acp.TEMPORAL_OUTCOME_EXPIRED_V01,
        executable=False,
    )


@pytest.mark.parametrize("evaluation_time_offset", (0, 1))
def test_supplier_projection_rejects_expired_assertion_mismatch(
    evaluation_time_offset: int,
) -> None:
    source = acp.build_supplier_a_mock_action_commit_packet_fixture_v02()
    expires = acp.parse_utc_timestamp_v01(source.ttl.expires_at)
    assert source.ttl.expired is False
    with pytest.raises(
        ValueError,
        match="^packet_ttl_expired_assertion_mismatch$",
    ):
        _projection(
            packet=source,
            evaluation_time=expires + evaluation_time_offset,
        )


def test_supplier_projection_validator_cannot_bypass_ttl_assertions() -> None:
    source = acp.build_supplier_a_mock_action_commit_packet_fixture_v02()
    expires = acp.parse_utc_timestamp_v01(source.ttl.expires_at)
    projection = _projection(
        packet=source,
        evaluation_time=expires - 1,
    )
    forged = replace(
        projection,
        evaluation_time=expires,
        temporal_evaluation=acp.TemporalEvaluationV01(
            outcome=acp.TEMPORAL_OUTCOME_EXPIRED_V01,
            executable=False,
        ),
    )
    valid, reasons = (
        acp.validate_supplier_action_commit_packet_canonical_projection_v01(
            forged
        )
    )
    assert valid is False
    assert "supplier_projection_source_rebuild_invalid" in reasons


@pytest.mark.parametrize(
    "source_adapter_version",
    (
        "",
        "source_evil_v9",
        acp.PRE_G2A_ADAPTER_VERSION_V01,
        "source_adapter_v01",
        pytest.param(object(), id="non_string_object"),
    ),
)
def test_supplier_projection_requires_absent_source_adapter_version(
    source_adapter_version: object,
) -> None:
    source = acp.build_supplier_a_mock_action_commit_packet_fixture_v02()
    mutated = replace(
        source,
        adapter_binding=replace(
            source.adapter_binding,
            adapter_version=source_adapter_version,
        ),
    )
    assert acp.validate_action_commit_packet_v02(mutated) == (True, ())
    with pytest.raises(
        ValueError,
        match=(
            "^supplier_projection_source_adapter_version_must_be_absent$"
        ),
    ):
        _projection(packet=mutated)


def test_supplier_projection_validator_rejects_source_adapter_version() -> None:
    projection = _projection()
    versioned_source = replace(
        projection.source_packet,
        adapter_binding=replace(
            projection.source_packet.adapter_binding,
            adapter_version="source_adapter_v01",
        ),
    )
    forged = replace(projection, source_packet=versioned_source)
    valid, reasons = (
        acp.validate_supplier_action_commit_packet_canonical_projection_v01(
            forged
        )
    )
    assert valid is False
    assert "supplier_projection_source_rebuild_invalid" in reasons


def test_supplier_projection_rejects_source_adapter_version_subclass() -> None:
    source = acp.build_supplier_a_mock_action_commit_packet_fixture_v02()
    versioned_source = replace(
        source,
        adapter_binding=replace(
            source.adapter_binding,
            adapter_version=_AlwaysEqualStr(
                acp.PRE_G2A_ADAPTER_VERSION_V01
            ),
        ),
    )
    with pytest.raises(
        ValueError,
        match=(
            "^supplier_projection_source_adapter_version_must_be_absent$"
        ),
    ):
        _projection(packet=versioned_source)


def test_g2a2a_public_contract_shapes_and_constants() -> None:
    assert acp.TRANSITION_EVIDENCE_BINDING_PROFILE_ID_V01 == (
        "action_transition_evidence_binding_v01"
    )
    assert acp.EXECUTION_ATTEMPT_IDENTITY_PROFILE_ID_V01 == (
        "action_execution_attempt_identity_v01"
    )
    assert acp.ACTION_PACKET_TRANSITION_EVENT_PROFILE_ID_V01 == (
        "action_packet_transition_identity_profile_v01"
    )
    assert tuple(
        field.name for field in fields(acp.TransitionEvidenceBindingV01)
    ) == (
        "transition_evidence_binding_id",
        "evidence_code",
        "evidence_ref",
        "evidence_sha256",
        "validator_profile_id",
        "validation_status",
    )
    assert tuple(
        field.name for field in fields(acp.ActionExecutionAttemptIdentityV01)
    ) == (
        "execution_attempt_id",
        "packet_id",
        "idempotency_key",
        "attempt_ordinal",
        "evaluation_context_id",
        "material",
    )
    assert tuple(
        field.name for field in fields(acp.ActionPacketTransitionEventV01)
    ) == (
        "transition_event_id",
        "transition_profile_version",
        "transition_registry_id",
        "transition_rule_id",
        "packet_id",
        "idempotency_key",
        "previous_transition_event_id",
        "source_state",
        "target_state",
        "transition_class_code",
        "performed_by_component",
        "owning_local_root_id",
        "root_decision_ref",
        "transition_evidence_bindings",
        "reason_code",
        "dependency_set_candidate_fingerprint",
        "temporal_authority_fingerprint",
        "evaluation_time",
        "evaluation_time_source",
        "evaluation_context_id",
        "execution_attempt_id",
        "effect_consumption_class",
        "receipt_ref",
    )


def test_transition_evidence_binding_exact_identity() -> None:
    registry = _g2a2a_registry()
    binding = _g2a2a_bindings(
        "g2a_t01_activate_root_authorization"
    )[0]
    material = acp.transition_evidence_binding_material_v01(binding)
    assert tuple(name for name, _ in material) == (
        "evidence_code",
        "evidence_ref",
        "evidence_sha256",
        "validator_profile_id",
        "validation_status",
    )
    assert binding.validation_status == "PASS"
    assert binding.transition_evidence_binding_id == (
        "acpte_v01:"
        "a442dab1f8cbd975b96aed1b42af2ae573d3a2d38f03f87ab589ef5ad01e5d97"
    )
    assert acp.validate_transition_evidence_binding_v01(
        binding,
        action_packet_transition_registry_profile=registry,
        transition_rule_id="g2a_t01_activate_root_authorization",
    ) == (True, ())
    assert _g2a2a_bindings(
        "g2a_t01_activate_root_authorization"
    )[0] == binding


def test_transition_evidence_binding_adversarial_rejections() -> None:
    registry = _g2a2a_registry()
    rule_id = "g2a_t01_activate_root_authorization"
    binding = _g2a2a_bindings(rule_id)[0]
    for forged in (
        replace(binding, transition_evidence_binding_id="acpte_v01:" + "0" * 64),
        replace(binding, evidence_sha256="0" * 63),
        replace(binding, validator_profile_id=""),
        replace(binding, validation_status="FAIL"),
        replace(binding, evidence_ref=""),
        replace(binding, evidence_ref=_AlwaysEqualStr(binding.evidence_ref)),
        replace(binding, evidence_code="transition_history_valid"),
        replace(
            binding,
            transition_evidence_binding_id=_AlwaysEqualStr(
                binding.transition_evidence_binding_id
            ),
        ),
    ):
        valid, reasons = acp.validate_transition_evidence_binding_v01(
            forged,
            action_packet_transition_registry_profile=registry,
            transition_rule_id=rule_id,
        )
        assert valid is False
        assert reasons
    with pytest.raises(ValueError):
        acp.build_transition_evidence_binding_v01(
            action_packet_transition_registry_profile=registry,
            transition_rule_id=rule_id,
            evidence_code="transition_history_valid",
            evidence_ref="evidence:wrong_rule",
            evidence_sha256=G2A2A_EVIDENCE_SHA256,
            validator_profile_id="validator:g2a2a",
        )
    assert acp.validate_transition_evidence_binding_v01(
        object(),
        action_packet_transition_registry_profile=registry,
        transition_rule_id=rule_id,
    )[0] is False


def test_execution_attempt_identity_exact_and_deterministic() -> None:
    attempt = _g2a2a_attempt()
    assert tuple(name for name, _ in attempt.material) == (
        "packet_id",
        "idempotency_key",
        "attempt_ordinal",
        "evaluation_context_id",
    )
    assert attempt.execution_attempt_id == (
        "execution_attempt_v01:"
        "03e9cacf21db74bd69c9d9e6184d8cdc0165351e16fccf2a7b22c93d84a6a82b"
    )
    assert acp.validate_action_execution_attempt_identity_v01(attempt) == (
        True,
        (),
    )
    assert _g2a2a_attempt() == attempt
    changed_ordinal = acp.build_action_execution_attempt_identity_v01(
        packet_id=G2A2A_PACKET_ID,
        idempotency_key=G2A2A_IDEMPOTENCY_KEY,
        attempt_ordinal=2,
        evaluation_context_id=G2A2A_EVALUATION_CONTEXT_ID,
    )
    changed_context = acp.build_action_execution_attempt_identity_v01(
        packet_id=G2A2A_PACKET_ID,
        idempotency_key=G2A2A_IDEMPOTENCY_KEY,
        attempt_ordinal=1,
        evaluation_context_id="evaluation_context:g2a2a_changed",
    )
    assert changed_ordinal.execution_attempt_id != attempt.execution_attempt_id
    assert changed_context.execution_attempt_id != attempt.execution_attempt_id


@pytest.mark.parametrize("ordinal", (0, -1, True, 1.0))
def test_execution_attempt_rejects_nonpositive_or_nonexact_ordinal(
    ordinal: object,
) -> None:
    with pytest.raises(ValueError):
        acp.build_action_execution_attempt_identity_v01(
            packet_id=G2A2A_PACKET_ID,
            idempotency_key=G2A2A_IDEMPOTENCY_KEY,
            attempt_ordinal=ordinal,
            evaluation_context_id=G2A2A_EVALUATION_CONTEXT_ID,
        )


def test_execution_attempt_identity_rejects_forgery() -> None:
    attempt = _g2a2a_attempt()
    forged_values = (
        replace(
            attempt,
            execution_attempt_id="execution_attempt_v01:" + "0" * 64,
        ),
        replace(
            attempt,
            execution_attempt_id=_AlwaysEqualStr(
                attempt.execution_attempt_id
            ),
        ),
        replace(attempt, packet_id="acp_v02:" + "0" * 63),
        replace(attempt, idempotency_key="idem:action_v01:" + "0" * 63),
        replace(attempt, material=tuple(reversed(attempt.material))),
    )
    for forged in forged_values:
        assert acp.validate_action_execution_attempt_identity_v01(
            forged
        )[0] is False
    assert acp.validate_action_execution_attempt_identity_v01(object())[0] is False


@pytest.mark.parametrize(
    "rule_id",
    transition_registry.ACTION_PACKET_TRANSITION_RULE_IDS_V01,
)
def test_every_action_packet_transition_event_builds_and_validates(
    rule_id: str,
) -> None:
    registry = _g2a2a_registry()
    rule = transition_registry.lookup_action_packet_transition_rule_v01(
        registry=registry,
        transition_rule_id=rule_id,
    )
    event = _g2a2a_event(rule_id)
    assert acp.validate_action_packet_transition_event_v01(
        event,
        action_packet_transition_registry_profile=registry,
    ) == (True, ())
    assert event.transition_registry_id == registry.transition_registry_id
    assert event.transition_rule_id == rule.transition_rule_id
    assert event.source_state == rule.source_state
    assert event.target_state == rule.target_state
    assert event.transition_class_code == rule.transition_class_code
    assert event.performed_by_component == rule.permitted_component_code
    assert event.reason_code == rule.reason_code
    assert event.effect_consumption_class == rule.effect_consumption_class
    assert tuple(
        binding.evidence_code
        for binding in event.transition_evidence_bindings
    ) == rule.required_evidence_codes
    material = acp.action_packet_transition_event_material_v01(event)
    assert len(material) == 22
    assert event.transition_event_id.startswith("acpt_v01:")
    assert len(event.transition_event_id.removeprefix("acpt_v01:")) == 64


def test_transition_event_deterministic_literal_ids() -> None:
    expected = {
        "g2a_t01_activate_root_authorization": (
            "acpt_v01:"
            "ab48ee053eadb4fd72f2e998bb807ed8b2a58cbca42461448e36cf5744f454be"
        ),
        "g2a_t02_queue": (
            "acpt_v01:"
            "34a8972108e7c2eca9b9c5587e73bb2e4382bd36006877c5c1eb9ece840e6b88"
        ),
        "g2a_t03_pending": (
            "acpt_v01:"
            "dcac921c908dbb6bb91cecf023e6fc802edcd150558557b9d1e40679d5bf0382"
        ),
        "g2a_t24_nonconsuming_failure": (
            "acpt_v01:"
            "fd2ff18b675ecc84df382311cc7c314aa1a03f36e34d43af4dc75e46fbb2a694"
        ),
        "g2a_t26_uncertain_adapter_outcome": (
            "acpt_v01:"
            "27753e6a066dc42a372aa126299243ffb095f7af01cbf1cfdeb7b6337f714d49"
        ),
    }
    for rule_id, event_id in expected.items():
        assert _g2a2a_event(rule_id).transition_event_id == event_id


@pytest.mark.parametrize(
    ("field_name", "value"),
    (
        ("transition_registry_id", "acptr_v01:" + "0" * 64),
        ("source_state", "FAILED"),
        ("target_state", "FAILED"),
        ("transition_class_code", "AUTHORITY_CHANGE"),
        ("performed_by_component", "owning_local_root"),
        ("reason_code", "packet_blocked"),
        ("effect_consumption_class", "CONSUMED"),
        ("packet_id", "acp_v02:" + "0" * 63),
        ("idempotency_key", "idem:action_v01:" + "0" * 63),
        ("previous_transition_event_id", "acpt_v01:" + "0" * 63),
        ("evaluation_time", True),
    ),
)
def test_transition_event_rule_and_identity_drift_fails_closed(
    field_name: str,
    value: object,
) -> None:
    registry = _g2a2a_registry()
    event = _g2a2a_event("g2a_t02_queue")
    forged = replace(event, **{field_name: value})
    assert acp.validate_action_packet_transition_event_v01(
        forged,
        action_packet_transition_registry_profile=registry,
    )[0] is False


def test_transition_event_evidence_set_order_and_binding_are_exact() -> None:
    registry = _g2a2a_registry()
    event = _g2a2a_event("g2a_t02_queue")
    bindings = event.transition_evidence_bindings
    wrong_hash = replace(bindings[0], evidence_sha256="0" * 64)
    wrong_validator = replace(bindings[0], validator_profile_id="validator:other")
    non_pass = replace(bindings[0], validation_status="FAIL")
    another_rule_binding = _g2a2a_bindings("g2a_t01_activate_root_authorization")[0]
    forged_collections = (
        bindings[:-1],
        (*bindings, bindings[0]),
        tuple(reversed(bindings)),
        (another_rule_binding, *bindings[1:]),
        (wrong_hash, *bindings[1:]),
        (wrong_validator, *bindings[1:]),
        (non_pass, *bindings[1:]),
        ("evidence:free_form",),
    )
    for forged_bindings in forged_collections:
        forged = replace(
            event,
            transition_evidence_bindings=forged_bindings,
        )
        assert acp.validate_action_packet_transition_event_v01(
            forged,
            action_packet_transition_registry_profile=registry,
        )[0] is False


def test_transition_event_root_reference_matrix() -> None:
    registry = _g2a2a_registry()
    none_rule = _g2a2a_event("g2a_t02_queue")
    required_rule = _g2a2a_event(
        "g2a_t01_activate_root_authorization"
    )
    for forged in (
        replace(none_rule, root_decision_ref=G2A2A_ROOT_DECISION_REF),
        replace(required_rule, root_decision_ref=None),
        replace(required_rule, root_decision_ref="not_a_digest"),
    ):
        assert acp.validate_action_packet_transition_event_v01(
            forged,
            action_packet_transition_registry_profile=registry,
        )[0] is False


def test_transition_event_unknown_rule_fails_closed() -> None:
    registry = _g2a2a_registry()
    with pytest.raises(ValueError, match="^unknown_transition$"):
        acp.build_action_packet_transition_event_v01(
            action_packet_transition_registry_profile=registry,
            transition_rule_id="g2a_unknown",
            packet_id=G2A2A_PACKET_ID,
            idempotency_key=G2A2A_IDEMPOTENCY_KEY,
            previous_transition_event_id=G2A2A_PREVIOUS_EVENT_ID,
            owning_local_root_id=ROOT_ID,
            root_decision_ref=None,
            transition_evidence_bindings=(),
            dependency_set_candidate_fingerprint=(
                G2A2A_DEPENDENCY_FINGERPRINT
            ),
            temporal_authority_fingerprint=(
                G2A2A_TEMPORAL_FINGERPRINT
            ),
            evaluation_time=EVALUATION_TIME,
            evaluation_time_source=EVALUATION_TIME_SOURCE,
            evaluation_context_id=G2A2A_EVALUATION_CONTEXT_ID,
            execution_attempt_identity=None,
            receipt_ref=None,
        )


@pytest.mark.parametrize(
    "rule_id",
    transition_registry.ACTION_PACKET_TRANSITION_RULE_IDS_V01,
)
def test_transition_event_attempt_and_receipt_presence_matrix(
    rule_id: str,
) -> None:
    event = _g2a2a_event(rule_id)
    if rule_id in G2A2A_ATTEMPT_RULE_IDS:
        assert event.execution_attempt_id == (
            _g2a2a_attempt().execution_attempt_id
        )
    else:
        assert event.execution_attempt_id is None
    if rule_id == "g2a_t05_receipt":
        assert event.receipt_ref == "receipt:g2a2a"
    else:
        assert event.receipt_ref is None


def test_transition_event_attempt_and_receipt_matrix_rejections() -> None:
    registry = _g2a2a_registry()
    mutations = (
        replace(_g2a2a_event("g2a_t03_pending"), execution_attempt_id=None),
        replace(
            _g2a2a_event("g2a_t02_queue"),
            execution_attempt_id=_g2a2a_attempt().execution_attempt_id,
        ),
        replace(_g2a2a_event("g2a_t03_pending"), receipt_ref="receipt:x"),
        replace(_g2a2a_event("g2a_t04_fulfill_mock"), receipt_ref="receipt:x"),
        replace(
            _g2a2a_event("g2a_t24_nonconsuming_failure"),
            receipt_ref="receipt:x",
        ),
        replace(
            _g2a2a_event("g2a_t26_uncertain_adapter_outcome"),
            receipt_ref="receipt:x",
        ),
        replace(_g2a2a_event("g2a_t05_receipt"), receipt_ref=None),
        replace(_g2a2a_event("g2a_t05_receipt"), receipt_ref=""),
        replace(
            _g2a2a_event("g2a_t03_pending"),
            execution_attempt_id="execution_attempt_v01:" + "0" * 63,
        ),
        replace(_g2a2a_event("g2a_t02_queue"), receipt_ref=""),
    )
    for mutation in mutations:
        assert acp.validate_action_packet_transition_event_v01(
            mutation,
            action_packet_transition_registry_profile=registry,
        )[0] is False


def test_transition_event_id_and_material_forgery_fail_closed() -> None:
    registry = _g2a2a_registry()
    event = _g2a2a_event("g2a_t02_queue")
    for forged_id in (
        "acpt_v01:" + "0" * 64,
        _AlwaysEqualStr(event.transition_event_id),
    ):
        assert acp.validate_action_packet_transition_event_v01(
            replace(event, transition_event_id=forged_id),
            action_packet_transition_registry_profile=registry,
        )[0] is False
    material = acp.action_packet_transition_event_material_v01(event)
    names = tuple(name for name, _ in material)
    assert acp.validate_canonical_profile_material_v01(
        material,
        expected_field_names=names,
    ) == (True, ())
    for forged_material in (
        tuple(reversed(material)),
        material[:-1],
        (*material, ("unknown_field", "value")),
    ):
        assert acp.validate_canonical_profile_material_v01(
            forged_material,
            expected_field_names=names,
        )[0] is False


def test_transition_event_validators_are_total_and_non_mutating() -> None:
    registry = _g2a2a_registry()
    assert acp.validate_action_packet_transition_event_v01(
        object(),
        action_packet_transition_registry_profile=registry,
    )[0] is False
    assert acp.validate_action_packet_transition_event_v01(
        _g2a2a_event("g2a_t02_queue"),
        action_packet_transition_registry_profile=object(),
    )[0] is False
    assert not hasattr(acp.ActionPacketTransitionEventV01, "append")
    assert not hasattr(acp.ActionPacketTransitionEventV01, "current_state")
    assert not hasattr(acp.ActionPacketTransitionEventV01, "disposition")


def test_temporal_evaluation_forgery_and_malformed_context_fail_closed() -> None:
    projection = _projection()
    stale_evaluation = replace(
        projection,
        evaluation_time=projection.temporal_authority.expires_at_utc,
    )
    forged_outcome = replace(
        projection,
        temporal_evaluation=acp.TemporalEvaluationV01(
            outcome=acp.TEMPORAL_OUTCOME_EXPIRED_V01,
            executable=False,
        ),
    )
    for forged in (stale_evaluation, forged_outcome):
        valid, reasons = (
            acp.validate_supplier_action_commit_packet_canonical_projection_v01(
                forged
            )
        )
        assert valid is False
        assert reasons
    for kwargs in (
        {"evaluation_time": True},
        {"evaluation_time_source": ""},
        {"evaluation_context_id": ""},
    ):
        with pytest.raises(ValueError):
            _projection(**kwargs)  # type: ignore[arg-type]


def test_operational_target_continuity_fails_closed(
    root_bound_fixture: _RootBoundFixtureV01,
) -> None:
    fixture = root_bound_fixture
    canonical = fixture.canonical_projection
    changed_source = _mutate_supplier_source_packet(
        canonical.source_packet,
        "creditor",
    )
    candidate_source_mismatch = replace(
        canonical,
        source_packet=changed_source,
    )
    assert acp.validate_supplier_root_context_coherence_v01(
        candidate_source_mismatch,
        fixture.root_projection,
    )[0] is False

    packet_creditor_drift = replace(
        fixture.root_bound_projection,
        packet=replace(
            fixture.root_bound_projection.packet,
            scope=replace(
                fixture.root_bound_projection.packet.scope,
                creditor_ref="creditor:other",
            ),
        ),
    )
    assert (
        acp.validate_supplier_root_bound_action_commit_packet_v02_projection_v01(
            packet_creditor_drift
        )[0]
        is False
    )

    changed_slot_source = _mutate_supplier_source_packet(
        canonical.source_packet,
        "payment_slot",
    )
    payment_slot_mismatch = replace(
        canonical,
        source_packet=changed_slot_source,
    )
    assert acp.validate_supplier_root_context_coherence_v01(
        payment_slot_mismatch,
        fixture.root_projection,
    )[0] is False


class _AlwaysEqualStr(str):
    def __eq__(self, other: object) -> bool:
        return True

    def __ne__(self, other: object) -> bool:
        return False

    __hash__ = str.__hash__


class _AlwaysEqualObject:
    def __eq__(self, other: object) -> bool:
        return True

    def __ne__(self, other: object) -> bool:
        return False


def test_custom_equality_cannot_bypass_identity_validation(
    root_bound_fixture: _RootBoundFixtureV01,
) -> None:
    fixture = root_bound_fixture
    bound = fixture.root_bound_projection
    forged_root = replace(
        fixture.root_projection,
        source_root_decision_hash=_AlwaysEqualStr("0" * 64),
    )
    assert acp.validate_root_decision_candidate_projection_v01(
        forged_root
    )[0] is False

    forged_identity = replace(
        bound.packet_identity,
        packet_id=_AlwaysEqualStr(bound.packet_identity.packet_id),
    )
    assert acp.validate_action_commit_packet_identity_v01(
        forged_identity,
        candidate=fixture.canonical_projection.authorization_candidate,
        source_root_decision_id=fixture.root_decision_result.decision_id,
        source_root_decision_hash=fixture.root_projection.source_root_decision_hash,
    )[0] is False

    forged_binding = replace(
        bound.dependency_acceptance_binding,
        packet_dependency_acceptance_binding_id=_AlwaysEqualStr(
            bound.dependency_acceptance_binding
            .packet_dependency_acceptance_binding_id
        ),
    )
    assert acp.validate_packet_dependency_acceptance_binding_v01(
        forged_binding
    )[0] is False

    packet_mutations = (
        replace(
            bound.packet,
            packet_id=_AlwaysEqualStr(bound.packet.packet_id),
        ),
        replace(
            bound.packet,
            source_root_decision_ref=_AlwaysEqualStr(
                bound.packet.source_root_decision_ref
            ),
        ),
        replace(
            bound.packet,
            root_boundary_ref=_AlwaysEqualStr(bound.packet.root_boundary_ref),
        ),
        replace(
            bound.packet,
            idempotency=replace(
                bound.packet.idempotency,
                key=_AlwaysEqualStr(bound.packet.idempotency.key),
            ),
        ),
        replace(
            bound.packet,
            packet_id=_AlwaysEqualObject(),  # type: ignore[arg-type]
        ),
    )
    for packet in packet_mutations:
        forged = replace(bound, packet=packet)
        assert (
            acp.validate_supplier_root_bound_action_commit_packet_v02_projection_v01(
                forged
            )[0]
            is False
        )


def _g2a2b_evidence_ids(
    event: acp.ActionPacketTransitionEventV01,
    codes: tuple[str, ...],
) -> tuple[str, ...]:
    return tuple(
        sorted(
            (
                binding.transition_evidence_binding_id
                for binding in event.transition_evidence_bindings
                if binding.evidence_code in codes
            ),
            key=lambda item: item.encode("utf-8"),
        )
    )


def _g2a2b_event(
    entry: acp.ActionPacketLifecycleEntryV01,
    rule_id: str,
    *,
    evaluation_context_id: str | None = None,
    evaluation_time: int | None = None,
    latest_disposition_event_id: str | None = None,
    receipt_ref: str | None = None,
) -> acp.ActionPacketTransitionEventV01:
    genesis = entry.root_bound_genesis
    events = entry.transition_events
    packet_id = genesis.packet_identity.packet_id
    key = genesis.canonical_projection.idempotency_identity.idempotency_key
    context_id = (
        evaluation_context_id
        or f"evaluation_context:g2a2b:{rule_id}:{len(events) + 1}"
    )
    attempt = None
    if rule_id == "g2a_t03_pending":
        ordinal = 1 + sum(
            event.transition_rule_id == "g2a_t03_pending"
            for event in events
        )
        attempt = acp.build_action_execution_attempt_identity_v01(
            packet_id=packet_id,
            idempotency_key=key,
            attempt_ordinal=ordinal,
            evaluation_context_id=context_id,
        )
    elif rule_id in {
        "g2a_t04_fulfill_mock",
        "g2a_t24_nonconsuming_failure",
        "g2a_t26_uncertain_adapter_outcome",
    }:
        pending = events[-1]
        ordinal = sum(
            event.transition_rule_id == "g2a_t03_pending"
            for event in events
        )
        context_id = pending.evaluation_context_id
        attempt = acp.build_action_execution_attempt_identity_v01(
            packet_id=packet_id,
            idempotency_key=key,
            attempt_ordinal=ordinal,
            evaluation_context_id=context_id,
        )
    elif rule_id == "g2a_t05_receipt":
        consumed = events[-1]
        ordinal = sum(
            event.transition_rule_id == "g2a_t03_pending"
            for event in events
        )
        context_id = consumed.evaluation_context_id
        attempt = acp.build_action_execution_attempt_identity_v01(
            packet_id=packet_id,
            idempotency_key=key,
            attempt_ordinal=ordinal,
            evaluation_context_id=context_id,
        )
    bindings = _g2a2a_bindings(rule_id)
    if (
        rule_id == "g2a_t24_nonconsuming_failure"
        and latest_disposition_event_id is not None
    ):
        bindings = tuple(
            acp.build_transition_evidence_binding_v01(
                action_packet_transition_registry_profile=_g2a2a_registry(),
                transition_rule_id=rule_id,
                evidence_code=binding.evidence_code,
                evidence_ref=(
                    latest_disposition_event_id
                    if binding.evidence_code
                    == "latest_disposition_event_binding_valid"
                    else binding.evidence_ref
                ),
                evidence_sha256=(
                    latest_disposition_event_id[
                        len(acp.IDEMPOTENCY_DISPOSITION_EVENT_PREFIX_V01) :
                    ]
                    if binding.evidence_code
                    == "latest_disposition_event_binding_valid"
                    else binding.evidence_sha256
                ),
                validator_profile_id=(
                    acp.IDEMPOTENCY_DISPOSITION_EVENT_PROFILE_ID_V01
                    if binding.evidence_code
                    == "latest_disposition_event_binding_valid"
                    else binding.validator_profile_id
                ),
            )
            for binding in bindings
        )
    return acp.build_action_packet_transition_event_v01(
        action_packet_transition_registry_profile=_g2a2a_registry(),
        transition_rule_id=rule_id,
        packet_id=packet_id,
        idempotency_key=key,
        previous_transition_event_id=(
            events[-1].transition_event_id if events else None
        ),
        owning_local_root_id=genesis.canonical_projection.owning_local_root_id,
        root_decision_ref=(
            genesis.root_decision_projection.root_decision_result.decision_id
            if rule_id == "g2a_t01_activate_root_authorization"
            else None
        ),
        transition_evidence_bindings=bindings,
        dependency_set_candidate_fingerprint=(
            genesis.canonical_projection.dependency_set_candidate_fingerprint
        ),
        temporal_authority_fingerprint=(
            genesis.canonical_projection.temporal_authority_fingerprint
        ),
        evaluation_time=(
            EVALUATION_TIME + len(events)
            if evaluation_time is None
            else evaluation_time
        ),
        evaluation_time_source=EVALUATION_TIME_SOURCE,
        evaluation_context_id=context_id,
        execution_attempt_identity=attempt,
        receipt_ref=receipt_ref,
    )


def _rebuild_transition_event(
    event: acp.ActionPacketTransitionEventV01,
    **changes: object,
) -> acp.ActionPacketTransitionEventV01:
    provisional = replace(event, transition_event_id="", **changes)
    return replace(
        provisional,
        transition_event_id=acp.build_domain_separated_identity_v01(
            domain=acp.ACTION_PACKET_TRANSITION_EVENT_DOMAIN_V01,
            prefix=acp.ACTION_PACKET_TRANSITION_EVENT_PREFIX_V01,
            material=acp.action_packet_transition_event_material_v01(
                provisional
            ),
        ),
    )


def _g2a2b_recorded_genesis(
    root_bound: acp.SupplierRootBoundActionCommitPacketV02ProjectionV01,
) -> acp.ActionCommitPacketRegistryV02:
    return acp.record_action_packet_genesis_v01(
        acp.build_empty_action_commit_packet_registry_v02(),
        root_bound_genesis=root_bound,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )


def _g2a2b_activate(
    registry: acp.ActionCommitPacketRegistryV02,
    packet_id: str,
    *,
    evaluation_time: int | None = None,
) -> tuple[
    acp.ActionCommitPacketRegistryV02,
    acp.ActionPacketTransitionEventV01,
    acp.IdempotencyDispositionEventV01,
]:
    event, reserve = _g2a2b_activation_pair(
        registry,
        packet_id,
        evaluation_time=evaluation_time,
    )
    activated = acp.activate_action_packet_lifecycle_v01(
        registry,
        packet_id=packet_id,
        transition_event=event,
        disposition_event=reserve,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    return activated, event, reserve


def _g2a2b_activation_pair(
    registry: acp.ActionCommitPacketRegistryV02,
    packet_id: str,
    *,
    evaluation_time: int | None = None,
) -> tuple[
    acp.ActionPacketTransitionEventV01,
    acp.IdempotencyDispositionEventV01,
]:
    entry = next(
        item
        for item in registry.action_packet_lifecycle_entries
        if item.root_bound_genesis.packet_identity.packet_id == packet_id
    )
    event = _g2a2b_event(
        entry,
        "g2a_t01_activate_root_authorization",
        evaluation_time=evaluation_time,
    )
    genesis = entry.root_bound_genesis
    reserve = acp.build_idempotency_disposition_event_v01(
        idempotency_key=(
            genesis.canonical_projection.idempotency_identity.idempotency_key
        ),
        event_class="RESERVE",
        from_disposition="UNCLAIMED",
        to_disposition="RESERVED",
        from_owner_packet_id=None,
        to_owner_packet_id=packet_id,
        previous_disposition_event_id=None,
        cause_transition_event_ids=(event.transition_event_id,),
        root_decision_ref=(
            genesis.root_decision_projection.root_decision_result.decision_id
        ),
        predecessor_packet_id=None,
        successor_packet_id=None,
        evidence_refs=_g2a2b_evidence_ids(
            event,
            (
                "packet_genesis_valid",
                "source_root_authorization_valid",
                "idempotency_acquisition_valid",
            ),
        ),
        evaluation_time=event.evaluation_time,
        evaluation_time_source=event.evaluation_time_source,
        evaluation_context_id=event.evaluation_context_id,
    )
    return event, reserve


def _g2a2b_append(
    registry: acp.ActionCommitPacketRegistryV02,
    packet_id: str,
    rule_id: str,
    *,
    evaluation_context_id: str | None = None,
) -> tuple[
    acp.ActionCommitPacketRegistryV02,
    acp.ActionPacketTransitionEventV01,
]:
    entry = next(
        item
        for item in registry.action_packet_lifecycle_entries
        if item.root_bound_genesis.packet_identity.packet_id == packet_id
    )
    event = _g2a2b_event(
        entry,
        rule_id,
        evaluation_context_id=evaluation_context_id,
    )
    updated = acp.append_action_packet_lifecycle_transition_v01(
        registry,
        packet_id=packet_id,
        transition_event=event,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    return updated, event


def _g2a2b_pending_registry(
    root_bound: acp.SupplierRootBoundActionCommitPacketV02ProjectionV01,
) -> tuple[
    acp.ActionCommitPacketRegistryV02,
    acp.ActionPacketTransitionEventV01,
]:
    packet_id = root_bound.packet_identity.packet_id
    registry = _g2a2b_recorded_genesis(root_bound)
    registry, _, _ = _g2a2b_activate(registry, packet_id)
    registry, _ = _g2a2b_append(registry, packet_id, "g2a_t02_queue")
    registry, pending = _g2a2b_append(
        registry,
        packet_id,
        "g2a_t03_pending",
        evaluation_context_id="evaluation_context:g2a2b:attempt:1",
    )
    return registry, pending


def _g2a2b_outcome_disposition(
    state: acp.ActionPacketLifecycleStateV01,
    transition: acp.ActionPacketTransitionEventV01,
    event_class: str,
) -> acp.IdempotencyDispositionEventV01:
    if event_class == "CONSUME":
        before, after = "RESERVED", "CONSUMED"
        codes = (
            "effect_consumption_evidence_valid",
            "mock_adapter_result_valid",
        )
    elif event_class == "UNCERTAIN_CLOSE":
        before, after = "RESERVED", "UNCERTAIN_CLOSED"
        codes = (
            "adapter_invocation_evidence_valid",
            "effect_outcome_unresolved",
        )
    else:
        before = after = "CONSUMED"
        codes = (
            "fulfillment_consumption_evidence_valid",
            "terminal_receipt_valid",
        )
    return acp.build_idempotency_disposition_event_v01(
        idempotency_key=state.idempotency_key,
        event_class=event_class,
        from_disposition=before,
        to_disposition=after,
        from_owner_packet_id=state.packet_id,
        to_owner_packet_id=state.packet_id,
        previous_disposition_event_id=state.latest_disposition_event_id,
        cause_transition_event_ids=(transition.transition_event_id,),
        root_decision_ref=None,
        predecessor_packet_id=None,
        successor_packet_id=None,
        evidence_refs=_g2a2b_evidence_ids(transition, codes),
        evaluation_time=transition.evaluation_time,
        evaluation_time_source=transition.evaluation_time_source,
        evaluation_context_id=transition.evaluation_context_id,
    )


def test_g2a2b_genesis_is_immutable_unclaimed_and_non_authoritative(
    root_bound_fixture: _RootBoundFixtureV01,
) -> None:
    source = acp.build_empty_action_commit_packet_registry_v02()
    source_before = repr(source)
    registry = acp.record_action_packet_genesis_v01(
        source,
        root_bound_genesis=root_bound_fixture.root_bound_projection,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    packet_id = root_bound_fixture.root_bound_projection.packet_identity.packet_id
    state = acp.derive_action_packet_lifecycle_state_v01(
        registry,
        packet_id=packet_id,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    assert repr(source) == source_before
    assert len(registry.action_packet_lifecycle_entries) == 1
    assert registry.idempotency_disposition_events == ()
    assert state.lifecycle_state == "CREATED"
    assert state.idempotency_disposition == "UNCLAIMED"
    assert state.reservation_owner_packet_id is None
    assert state.executable is False
    assert state.registry_is_authority is False
    assert state.registry_grants_permission is False
    assert state.real_world_effects_count == 0
    assert acp.validate_action_commit_packet_registry_v02(registry) == (
        True,
        (),
    )
    with pytest.raises(ValueError, match="action_packet_registry_duplicate_genesis"):
        acp.record_action_packet_genesis_v01(
            registry,
            root_bound_genesis=root_bound_fixture.root_bound_projection,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )


def test_g2a2b_activation_is_atomic_and_reserves_exact_owner(
    root_bound_fixture: _RootBoundFixtureV01,
) -> None:
    root_bound = root_bound_fixture.root_bound_projection
    registry = _g2a2b_recorded_genesis(root_bound)
    before = repr(registry)
    activated, transition, reserve = _g2a2b_activate(
        registry,
        root_bound.packet_identity.packet_id,
    )
    state = acp.derive_action_packet_lifecycle_state_v01(
        activated,
        packet_id=root_bound.packet_identity.packet_id,
    )
    assert repr(registry) == before
    assert state.lifecycle_state == "ROOT_AUTHORIZED"
    assert state.idempotency_disposition == "RESERVED"
    assert state.reservation_owner_packet_id == state.packet_id
    assert state.executable is False
    assert reserve.cause_transition_event_ids == (transition.transition_event_id,)
    assert reserve.root_decision_ref == transition.root_decision_ref
    assert len(activated.idempotency_disposition_events) == 1
    with pytest.raises(ValueError):
        acp.activate_action_packet_lifecycle_v01(
            registry,
            packet_id=state.packet_id,
            transition_event=transition,
            disposition_event=replace(
                reserve,
                cause_transition_event_ids=(G2A2A_PREVIOUS_EVENT_ID,),
            ),
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )
    assert repr(registry) == before


def test_g2a2b_attempt_history_nonconsuming_retry_and_new_ordinal(
    root_bound_fixture: _RootBoundFixtureV01,
) -> None:
    root_bound = root_bound_fixture.root_bound_projection
    packet_id = root_bound.packet_identity.packet_id
    registry, first_pending = _g2a2b_pending_registry(root_bound)
    entry = registry.action_packet_lifecycle_entries[0]
    current = acp.derive_action_packet_lifecycle_state_v01(
        registry,
        packet_id=packet_id,
    )
    failure = _g2a2b_event(
        entry,
        "g2a_t24_nonconsuming_failure",
        latest_disposition_event_id=current.latest_disposition_event_id,
    )
    before_events = registry.idempotency_disposition_events
    before_bytes = canonical_json_bytes_v01(
        tuple(
            acp.idempotency_disposition_event_material_v01(event)
            for event in before_events
        )
    )
    registry = acp.record_action_packet_nonconsuming_outcome_v01(
        registry,
        packet_id=packet_id,
        transition_event=failure,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    failed_state = acp.derive_action_packet_lifecycle_state_v01(
        registry,
        packet_id=packet_id,
    )
    assert failed_state.lifecycle_state == "FAILED"
    assert failed_state.failed_provenance == "FAILED_NON_CONSUMING"
    assert registry.idempotency_disposition_events is before_events
    assert canonical_json_bytes_v01(
        tuple(
            acp.idempotency_disposition_event_material_v01(event)
            for event in registry.idempotency_disposition_events
        )
    ) == before_bytes
    assert failed_state.idempotency_disposition == "RESERVED"
    registry, _ = _g2a2b_append(registry, packet_id, "g2a_t25_retry")
    registry, second_pending = _g2a2b_append(
        registry,
        packet_id,
        "g2a_t03_pending",
        evaluation_context_id="evaluation_context:g2a2b:attempt:2",
    )
    assert first_pending.execution_attempt_id != second_pending.execution_attempt_id
    state = acp.derive_action_packet_lifecycle_state_v01(
        registry,
        packet_id=packet_id,
    )
    assert state.execution_attempt_count == 2
    assert state.lifecycle_state == "PENDING_FULFILLMENT"
    assert state.eligible_for_corridor_revalidation is True
    assert state.executable is False


def test_g2a2b_consumption_and_receipt_are_atomic(
    root_bound_fixture: _RootBoundFixtureV01,
) -> None:
    root_bound = root_bound_fixture.root_bound_projection
    packet_id = root_bound.packet_identity.packet_id
    registry, pending = _g2a2b_pending_registry(root_bound)
    entry = registry.action_packet_lifecycle_entries[0]
    fulfilled = _g2a2b_event(entry, "g2a_t04_fulfill_mock")
    before_state = acp.derive_action_packet_lifecycle_state_v01(
        registry,
        packet_id=packet_id,
    )
    consume = _g2a2b_outcome_disposition(
        before_state,
        fulfilled,
        "CONSUME",
    )
    registry = acp.record_action_packet_consumed_outcome_v01(
        registry,
        packet_id=packet_id,
        transition_event=fulfilled,
        disposition_event=consume,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    consumed = acp.derive_action_packet_lifecycle_state_v01(
        registry,
        packet_id=packet_id,
    )
    assert fulfilled.execution_attempt_id == pending.execution_attempt_id
    assert consumed.lifecycle_state == "FULFILLED_MOCK"
    assert consumed.idempotency_disposition == "CONSUMED"
    entry = registry.action_packet_lifecycle_entries[0]
    receipt = _g2a2b_event(
        entry,
        "g2a_t05_receipt",
        receipt_ref="receipt:g2a2b:terminal",
    )
    confirmation = _g2a2b_outcome_disposition(
        consumed,
        receipt,
        "RECEIPT_CONFIRM",
    )
    registry = acp.record_action_packet_receipt_confirmation_v01(
        registry,
        packet_id=packet_id,
        transition_event=receipt,
        disposition_event=confirmation,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    state = acp.derive_action_packet_lifecycle_state_v01(
        registry,
        packet_id=packet_id,
    )
    assert receipt.execution_attempt_id == pending.execution_attempt_id
    assert state.lifecycle_state == "RECEIPT_RECEIVED"
    assert state.idempotency_disposition == "CONSUMED"
    assert state.terminal_receipt_ref == "receipt:g2a2b:terminal"
    assert state.lifecycle_terminal is True
    assert state.executable is False


def test_g2a2b_uncertain_outcome_is_permanently_closed(
    root_bound_fixture: _RootBoundFixtureV01,
) -> None:
    root_bound = root_bound_fixture.root_bound_projection
    packet_id = root_bound.packet_identity.packet_id
    registry, pending = _g2a2b_pending_registry(root_bound)
    entry = registry.action_packet_lifecycle_entries[0]
    uncertain = _g2a2b_event(entry, "g2a_t26_uncertain_adapter_outcome")
    before_state = acp.derive_action_packet_lifecycle_state_v01(
        registry,
        packet_id=packet_id,
    )
    close = _g2a2b_outcome_disposition(
        before_state,
        uncertain,
        "UNCERTAIN_CLOSE",
    )
    registry = acp.record_action_packet_uncertain_outcome_v01(
        registry,
        packet_id=packet_id,
        transition_event=uncertain,
        disposition_event=close,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    state = acp.derive_action_packet_lifecycle_state_v01(
        registry,
        packet_id=packet_id,
    )
    assert uncertain.execution_attempt_id == pending.execution_attempt_id
    assert state.lifecycle_state == "FAILED"
    assert state.failed_provenance == "FAILED_UNCERTAIN_TERMINAL"
    assert state.idempotency_disposition == "UNCERTAIN_CLOSED"
    assert state.lifecycle_terminal is True
    entry = registry.action_packet_lifecycle_entries[0]
    forged_retry = _g2a2b_event(entry, "g2a_t25_retry")
    with pytest.raises(ValueError):
        acp.append_action_packet_lifecycle_transition_v01(
            registry,
            packet_id=packet_id,
            transition_event=forged_retry,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )


def _standalone_disposition_fixtures(
) -> tuple[acp.IdempotencyDispositionEventV01, ...]:
    predecessor = "acp_v02:" + "8" * 64
    successor = "acp_v02:" + "9" * 64
    first_transition = "acpt_v01:" + "1" * 64
    second_transition = "acpt_v01:" + "2" * 64
    previous = "idem_event_v01:" + "3" * 64
    common = {
        "idempotency_key": G2A2A_IDEMPOTENCY_KEY,
        "evaluation_time": EVALUATION_TIME,
        "evaluation_time_source": EVALUATION_TIME_SOURCE,
        "evaluation_context_id": G2A2A_EVALUATION_CONTEXT_ID,
    }
    initial = acp.build_idempotency_disposition_event_v01(
        **common,
        event_class="RESERVE",
        from_disposition="UNCLAIMED",
        to_disposition="RESERVED",
        from_owner_packet_id=None,
        to_owner_packet_id=G2A2A_PACKET_ID,
        previous_disposition_event_id=None,
        cause_transition_event_ids=(first_transition,),
        root_decision_ref=G2A2A_ROOT_DECISION_REF,
        predecessor_packet_id=None,
        successor_packet_id=None,
        evidence_refs=("evidence:a", "evidence:b", "evidence:c"),
    )
    branch_a = acp.build_idempotency_disposition_event_v01(
        **common,
        event_class="RESERVE",
        from_disposition="UNCLAIMED",
        to_disposition="RESERVED",
        from_owner_packet_id=None,
        to_owner_packet_id=successor,
        previous_disposition_event_id=None,
        cause_transition_event_ids=(first_transition, second_transition),
        root_decision_ref=G2A2A_ROOT_DECISION_REF,
        predecessor_packet_id=predecessor,
        successor_packet_id=successor,
        evidence_refs=("evidence:a", "evidence:b", "evidence:c"),
    )
    transfer_kwargs = {
        **common,
        "from_disposition": "RESERVED",
        "to_disposition": "RESERVED",
        "from_owner_packet_id": predecessor,
        "to_owner_packet_id": successor,
        "previous_disposition_event_id": previous,
        "cause_transition_event_ids": (
            first_transition,
            second_transition,
        ),
        "root_decision_ref": G2A2A_ROOT_DECISION_REF,
        "predecessor_packet_id": predecessor,
        "successor_packet_id": successor,
        "evidence_refs": ("evidence:a", "evidence:b", "evidence:c"),
    }
    renewal = acp.build_idempotency_disposition_event_v01(
        **transfer_kwargs,
        event_class="TRANSFER_RENEWAL",
    )
    supersession = acp.build_idempotency_disposition_event_v01(
        **transfer_kwargs,
        event_class="TRANSFER_SUPERSESSION",
    )
    outcome_kwargs = {
        **common,
        "from_owner_packet_id": G2A2A_PACKET_ID,
        "to_owner_packet_id": G2A2A_PACKET_ID,
        "previous_disposition_event_id": previous,
        "cause_transition_event_ids": (first_transition,),
        "root_decision_ref": None,
        "predecessor_packet_id": None,
        "successor_packet_id": None,
        "evidence_refs": ("evidence:a", "evidence:b"),
    }
    consume = acp.build_idempotency_disposition_event_v01(
        **outcome_kwargs,
        event_class="CONSUME",
        from_disposition="RESERVED",
        to_disposition="CONSUMED",
    )
    uncertain = acp.build_idempotency_disposition_event_v01(
        **outcome_kwargs,
        event_class="UNCERTAIN_CLOSE",
        from_disposition="RESERVED",
        to_disposition="UNCERTAIN_CLOSED",
    )
    receipt = acp.build_idempotency_disposition_event_v01(
        **outcome_kwargs,
        event_class="RECEIPT_CONFIRM",
        from_disposition="CONSUMED",
        to_disposition="CONSUMED",
    )
    return (
        initial,
        branch_a,
        renewal,
        supersession,
        consume,
        uncertain,
        receipt,
    )


def test_g2a2b_disposition_profile_matrix_and_literal_ids() -> None:
    fixtures = _standalone_disposition_fixtures()
    assert acp.IDEMPOTENCY_DISPOSITIONS_V01 == (
        "UNCLAIMED",
        "RESERVED",
        "CONSUMED",
        "UNCERTAIN_CLOSED",
    )
    assert acp.IDEMPOTENCY_DISPOSITION_EVENT_CLASSES_V01 == (
        "RESERVE",
        "TRANSFER_RENEWAL",
        "TRANSFER_SUPERSESSION",
        "CONSUME",
        "UNCERTAIN_CLOSE",
        "RECEIPT_CONFIRM",
    )
    assert all(
        acp.validate_idempotency_disposition_event_v01(event) == (True, ())
        for event in fixtures
    )
    assert all(
        len(acp.idempotency_disposition_event_material_v01(event)) == 16
        for event in fixtures
    )
    assert tuple(
        event.idempotency_disposition_event_id for event in fixtures
    ) == (
        "idem_event_v01:80a87710931fa774be37719d506d0d91"
        "d29a5ae2c59af08d10aaf573c80cbc61",
        "idem_event_v01:5bb54bd1ee2ac8ca686faf8415402ceb"
        "a1117f7e2e40ee153d5024b5c3158586",
        "idem_event_v01:b457d9cdf3ad7ceb77d37e536b04cb1e"
        "138fbb7fbf74f174bcae025f0eccd9c8",
        "idem_event_v01:46923ae48beb7b07f4e49188958f6b1a"
        "bee360cd62734cd991c7aecec7f44a7d",
        "idem_event_v01:e71a12cc59c1687ebb336a259ffce159"
        "8dba143ca189f33fe1776d55a2dcf2f4",
        "idem_event_v01:b2e686be41a108449b3466579b5fc5be"
        "cbfd7a921652c5caf533363233692304",
        "idem_event_v01:68399ef3633d4b7be47352c64c74a8d7"
        "efd414c0ecb2433a6f48f35b4c42e072",
    )


def test_g2a2b_disposition_history_reconstructs_and_closes() -> None:
    initial, _, _, _, consume, uncertain, receipt = (
        _standalone_disposition_fixtures()
    )
    assert acp.derive_idempotency_disposition_v01(
        (),
        idempotency_key=G2A2A_IDEMPOTENCY_KEY,
    ).disposition == "UNCLAIMED"
    reserved = acp.derive_idempotency_disposition_v01(
        (initial,),
        idempotency_key=G2A2A_IDEMPOTENCY_KEY,
    )
    assert reserved.disposition == "RESERVED"
    assert reserved.reservation_owner_packet_id == G2A2A_PACKET_ID
    chained_consume = acp.build_idempotency_disposition_event_v01(
        idempotency_key=consume.idempotency_key,
        event_class=consume.event_class,
        from_disposition=consume.from_disposition,
        to_disposition=consume.to_disposition,
        from_owner_packet_id=consume.from_owner_packet_id,
        to_owner_packet_id=consume.to_owner_packet_id,
        previous_disposition_event_id=(
            initial.idempotency_disposition_event_id
        ),
        cause_transition_event_ids=consume.cause_transition_event_ids,
        root_decision_ref=None,
        predecessor_packet_id=None,
        successor_packet_id=None,
        evidence_refs=consume.evidence_refs,
        evaluation_time=consume.evaluation_time,
        evaluation_time_source=consume.evaluation_time_source,
        evaluation_context_id=consume.evaluation_context_id,
    )
    assert acp.validate_idempotency_disposition_history_v01(
        (initial, chained_consume)
    ) == (True, ())
    assert acp.validate_idempotency_disposition_history_v01(
        (initial, chained_consume, uncertain)
    )[0] is False
    chained_receipt = acp.build_idempotency_disposition_event_v01(
        idempotency_key=receipt.idempotency_key,
        event_class="RECEIPT_CONFIRM",
        from_disposition="CONSUMED",
        to_disposition="CONSUMED",
        from_owner_packet_id=receipt.from_owner_packet_id,
        to_owner_packet_id=receipt.to_owner_packet_id,
        previous_disposition_event_id=(
            chained_consume.idempotency_disposition_event_id
        ),
        cause_transition_event_ids=receipt.cause_transition_event_ids,
        root_decision_ref=None,
        predecessor_packet_id=None,
        successor_packet_id=None,
        evidence_refs=receipt.evidence_refs,
        evaluation_time=receipt.evaluation_time,
        evaluation_time_source=receipt.evaluation_time_source,
        evaluation_context_id=receipt.evaluation_context_id,
    )
    assert acp.validate_idempotency_disposition_history_v01(
        (initial, chained_consume, chained_receipt)
    ) == (True, ())
    assert acp.validate_idempotency_disposition_history_v01(
        (initial, chained_consume, chained_receipt, chained_receipt)
    )[0] is False


@pytest.mark.parametrize(
    "field,value",
    (
        ("idempotency_disposition_event_id", "idem_event_v01:" + "f" * 64),
        ("event_class", "RELEASE"),
        ("cause_transition_event_ids", ()),
        ("evidence_refs", ("evidence:b", "evidence:a")),
        ("evaluation_time", True),
    ),
)
def test_g2a2b_disposition_adversarial_mutations_fail_closed(
    field: str,
    value: object,
) -> None:
    event = _standalone_disposition_fixtures()[0]
    assert acp.validate_idempotency_disposition_event_v01(
        replace(event, **{field: value})
    )[0] is False


def test_g2a2b_authority_transitions_remain_blocked_until_g2a3(
    root_bound_fixture: _RootBoundFixtureV01,
) -> None:
    root_bound = root_bound_fixture.root_bound_projection
    packet_id = root_bound.packet_identity.packet_id
    registry = _g2a2b_recorded_genesis(root_bound)
    registry, _, _ = _g2a2b_activate(registry, packet_id)
    entry = registry.action_packet_lifecycle_entries[0]
    rule_id = "g2a_t16_authorized_revoke"
    event = acp.build_action_packet_transition_event_v01(
        action_packet_transition_registry_profile=_g2a2a_registry(),
        transition_rule_id=rule_id,
        packet_id=packet_id,
        idempotency_key=(
            root_bound.canonical_projection.idempotency_identity.idempotency_key
        ),
        previous_transition_event_id=(
            entry.transition_events[-1].transition_event_id
        ),
        owning_local_root_id=ROOT_ID,
        root_decision_ref="7" * 64,
        transition_evidence_bindings=_g2a2a_bindings(rule_id),
        dependency_set_candidate_fingerprint=(
            root_bound.canonical_projection.dependency_set_candidate_fingerprint
        ),
        temporal_authority_fingerprint=(
            root_bound.canonical_projection.temporal_authority_fingerprint
        ),
        evaluation_time=EVALUATION_TIME,
        evaluation_time_source=EVALUATION_TIME_SOURCE,
        evaluation_context_id="evaluation_context:g2a2b:g2a3_boundary",
        execution_attempt_identity=None,
        receipt_ref=None,
    )
    with pytest.raises(
        ValueError,
        match="authority_transition_requires_g2a3_binding",
    ):
        acp.append_action_packet_lifecycle_transition_v01(
            registry,
            packet_id=packet_id,
            transition_event=event,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )


def test_g2a2b_legacy_registry_helpers_preserve_new_histories(
    root_bound_fixture: _RootBoundFixtureV01,
) -> None:
    root_bound = root_bound_fixture.root_bound_projection
    registry = _g2a2b_recorded_genesis(root_bound)
    seen = acp.record_packet_seen_v02(registry, root_bound.packet)
    assert (
        seen.action_packet_lifecycle_entries
        == registry.action_packet_lifecycle_entries
    )
    assert (
        seen.idempotency_disposition_events
        == registry.idempotency_disposition_events
    )
    assert acp.validate_action_commit_packet_registry_v02(
        acp.build_empty_action_commit_packet_registry_v02()
    ) == (True, ())


@pytest.mark.parametrize("malformed", (None, [], {}, "x", object()))
def test_g2a2b_public_validators_are_total(malformed: object) -> None:
    assert acp.validate_action_packet_lifecycle_entry_v01(malformed)[0] is False
    assert acp.validate_idempotency_disposition_event_v01(malformed)[0] is False
    assert acp.validate_idempotency_disposition_history_v01(malformed)[0] is False


def test_g2a2b_empty_disposition_history_is_valid() -> None:
    assert acp.validate_idempotency_disposition_history_v01(()) == (True, ())


def _root_bound_from_canonical(
    canonical: acp.SupplierActionCommitPacketCanonicalProjectionV01,
) -> acp.SupplierRootBoundActionCommitPacketV02ProjectionV01:
    _, _, kernel, decision_input, result = _build_frozen_root_evidence(canonical)
    root_projection = acp.build_root_decision_candidate_projection_v01(
        candidate_kind="PACKET_AUTHORIZATION",
        projected_candidate_id=(
            canonical.authorization_candidate
            .root_packet_authorization_candidate_id
        ),
        root_decision_kernel=kernel,
        root_decision_input=decision_input,
        root_decision_result=result,
    )
    return acp.build_supplier_root_bound_action_commit_packet_v02_projection_v01(
        canonical_projection=canonical,
        root_decision_projection=root_projection,
    )


def test_g2a2b_branch_a_shape_is_valid_but_live_activation_requires_g2a3(
    root_bound_fixture: _RootBoundFixtureV01,
) -> None:
    predecessor = root_bound_fixture.root_bound_projection
    predecessor_id = predecessor.packet_identity.packet_id
    registry = _g2a2b_recorded_genesis(predecessor)
    predecessor_entry = registry.action_packet_lifecycle_entries[0]
    expiry = _g2a2b_event(
        predecessor_entry,
        "g2a_t11_created_expire",
        evaluation_time=(
            predecessor.canonical_projection.temporal_authority.expires_at_utc
        ),
    )
    registry = acp.append_action_packet_lifecycle_transition_v01(
        registry,
        packet_id=predecessor_id,
        transition_event=expiry,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    predecessor_state = acp.derive_action_packet_lifecycle_state_v01(
        registry,
        packet_id=predecessor_id,
    )
    assert predecessor_state.lifecycle_state == "EXPIRED"
    assert predecessor_state.idempotency_disposition == "UNCLAIMED"

    source = acp.build_supplier_a_mock_action_commit_packet_fixture_v02()
    renewed_source = replace(
        source,
        packet_id="legacy:renewed_supplier_packet",
        source_root_decision_ref="legacy:renewed_root_ref",
        ttl=replace(
            source.ttl,
            created_at="2026-07-08T00:10:00Z",
            expires_at="2026-07-08T01:10:00Z",
        ),
    )
    successor = _root_bound_from_canonical(
        _projection(
            packet=renewed_source,
            predecessor_packet_id=predecessor_id,
            supersession_reason_class="RENEWAL",
        )
    )
    successor_id = successor.packet_identity.packet_id
    assert successor_id != predecessor_id
    assert (
        successor.canonical_projection.logical_intent.root_owned_intent_id
        == predecessor.canonical_projection.logical_intent.root_owned_intent_id
    )
    assert (
        successor.canonical_projection.idempotency_identity.idempotency_key
        == predecessor.canonical_projection.idempotency_identity.idempotency_key
    )
    registry = acp.record_action_packet_genesis_v01(
        registry,
        root_bound_genesis=successor,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    successor_entry = next(
        entry
        for entry in registry.action_packet_lifecycle_entries
        if entry.root_bound_genesis.packet_identity.packet_id == successor_id
    )
    activation = _g2a2b_event(
        successor_entry,
        "g2a_t01_activate_root_authorization",
    )
    branch_reserve = acp.build_idempotency_disposition_event_v01(
        idempotency_key=(
            successor.canonical_projection.idempotency_identity.idempotency_key
        ),
        event_class="RESERVE",
        from_disposition="UNCLAIMED",
        to_disposition="RESERVED",
        from_owner_packet_id=None,
        to_owner_packet_id=successor_id,
        previous_disposition_event_id=None,
        cause_transition_event_ids=(
            expiry.transition_event_id,
            activation.transition_event_id,
        ),
        root_decision_ref=(
            successor.root_decision_projection.root_decision_result.decision_id
        ),
        predecessor_packet_id=predecessor_id,
        successor_packet_id=successor_id,
        evidence_refs=(
            "evidence:predecessor_expiry",
            "evidence:predecessor_relationship",
            "evidence:successor_authorization",
        ),
        evaluation_time=activation.evaluation_time,
        evaluation_time_source=activation.evaluation_time_source,
        evaluation_context_id=activation.evaluation_context_id,
    )
    assert acp.validate_idempotency_disposition_event_v01(
        branch_reserve
    ) == (True, ())
    forged_entry = replace(
        successor_entry,
        transition_events=(activation,),
    )
    forged_registry = replace(
        registry,
        action_packet_lifecycle_entries=tuple(
            forged_entry if entry is successor_entry else entry
            for entry in registry.action_packet_lifecycle_entries
        ),
        idempotency_disposition_events=(branch_reserve,),
    )
    valid, reasons = acp.validate_action_commit_packet_registry_v02(
        forged_registry
    )
    assert valid is False
    assert "authority_transition_requires_g2a3_binding" in reasons
    before = repr(registry).encode("utf-8")
    with pytest.raises(
        ValueError,
        match="^authority_transition_requires_g2a3_binding$",
    ):
        acp.activate_action_packet_lifecycle_v01(
            registry,
            packet_id=successor_id,
            transition_event=activation,
            disposition_event=branch_reserve,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )
    assert repr(registry).encode("utf-8") == before
    successor_state = acp.derive_action_packet_lifecycle_state_v01(
        registry,
        packet_id=successor_id,
    )
    assert successor_state.lifecycle_state == "CREATED"
    assert successor_state.idempotency_disposition == "UNCLAIMED"
    assert successor_state.reservation_owner_packet_id is None
    assert acp.validate_action_commit_packet_registry_v02(registry) == (
        True,
        (),
    )


def test_g2a2b_transition_chain_tampering_fails_closed(
    root_bound_fixture: _RootBoundFixtureV01,
) -> None:
    root_bound = root_bound_fixture.root_bound_projection
    packet_id = root_bound.packet_identity.packet_id
    registry, _ = _g2a2b_pending_registry(root_bound)
    entry = registry.action_packet_lifecycle_entries[0]
    mutations = (
        replace(
            entry,
            transition_events=(
                entry.transition_events[0],
                replace(
                    entry.transition_events[1],
                    previous_transition_event_id=None,
                ),
                entry.transition_events[2],
            ),
        ),
        replace(
            entry,
            transition_events=(
                entry.transition_events[1],
                entry.transition_events[0],
                entry.transition_events[2],
            ),
        ),
        replace(
            entry,
            transition_events=entry.transition_events
            + (entry.transition_events[-1],),
        ),
        replace(
            entry,
            transition_events=(
                entry.transition_events[0],
                replace(entry.transition_events[1], packet_id=G2A2A_PACKET_ID),
                entry.transition_events[2],
            ),
        ),
    )
    for forged in mutations:
        assert acp.validate_action_packet_lifecycle_entry_v01(
            forged,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )[0] is False
    assert acp.derive_action_packet_lifecycle_state_v01(
        registry,
        packet_id=packet_id,
    ).lifecycle_state == "PENDING_FULFILLMENT"


def test_g2a2b_custom_equality_disposition_identity_is_rejected() -> None:
    initial = _standalone_disposition_fixtures()[0]
    forged = replace(
        initial,
        idempotency_disposition_event_id=_AlwaysEqualStr(
            initial.idempotency_disposition_event_id
        ),
    )
    assert acp.validate_idempotency_disposition_event_v01(forged)[0] is False


def test_g2a2b_exact_new_dataclass_field_orders() -> None:
    assert tuple(field.name for field in fields(acp.ActionPacketLifecycleEntryV01)) == (
        "root_bound_genesis",
        "transition_registry_id",
        "transition_events",
    )
    assert tuple(
        field.name for field in fields(acp.IdempotencyDispositionEventV01)
    ) == (
        "idempotency_disposition_event_id",
        "event_profile_version",
        "idempotency_key",
        "event_class",
        "from_disposition",
        "to_disposition",
        "from_owner_packet_id",
        "to_owner_packet_id",
        "previous_disposition_event_id",
        "cause_transition_event_ids",
        "root_decision_ref",
        "predecessor_packet_id",
        "successor_packet_id",
        "evidence_refs",
        "evaluation_time",
        "evaluation_time_source",
        "evaluation_context_id",
    )
    registry_fields = tuple(
        field.name for field in fields(acp.ActionCommitPacketRegistryV02)
    )
    assert registry_fields[-4:] == (
        "action_packet_lifecycle_entries",
        "idempotency_disposition_events",
        "action_packet_invalidation_contexts",
        "action_packet_fulfillment_attempt_contexts",
    )
    fulfillment_field = fields(acp.ActionCommitPacketRegistryV02)[-1]
    assert fulfillment_field.name == (
        "action_packet_fulfillment_attempt_contexts"
    )
    assert fulfillment_field.default == ()
    assert acp.ActionCommitPacketRegistryV02.__dataclass_params__.frozen is True
    assert acp.IDEMPOTENCY_DISPOSITION_EVENT_PROFILE_ID_V01 == (
        "action_idempotency_disposition_event_v01"
    )
    assert acp.IDEMPOTENCY_DISPOSITION_EVENT_DOMAIN_V01 == (
        "HEDGEHOG_ACTION_IDEMPOTENCY_DISPOSITION_EVENT_V01"
    )
    assert acp.IDEMPOTENCY_DISPOSITION_EVENT_PREFIX_V01 == "idem_event_v01:"
    assert "RELEASE" not in acp.IDEMPOTENCY_DISPOSITION_EVENT_CLASSES_V01


def test_g2a2b_incomplete_atomic_pairs_are_rejected(
    root_bound_fixture: _RootBoundFixtureV01,
) -> None:
    root_bound = root_bound_fixture.root_bound_projection
    packet_id = root_bound.packet_identity.packet_id
    genesis_registry = _g2a2b_recorded_genesis(root_bound)
    entry = genesis_registry.action_packet_lifecycle_entries[0]
    activation = _g2a2b_event(
        entry,
        "g2a_t01_activate_root_authorization",
    )
    with pytest.raises(
        ValueError,
        match="action_packet_transition_requires_atomic_operation",
    ):
        acp.append_action_packet_lifecycle_transition_v01(
            genesis_registry,
            packet_id=packet_id,
            transition_event=activation,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )

    pending_registry, _ = _g2a2b_pending_registry(root_bound)
    pending_entry = pending_registry.action_packet_lifecycle_entries[0]
    fulfilled = _g2a2b_event(
        pending_entry,
        "g2a_t04_fulfill_mock",
    )
    with pytest.raises(
        ValueError,
        match="action_packet_transition_requires_atomic_operation",
    ):
        acp.append_action_packet_lifecycle_transition_v01(
            pending_registry,
            packet_id=packet_id,
            transition_event=fulfilled,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )
    forged_entry = replace(
        pending_entry,
        transition_events=pending_entry.transition_events + (fulfilled,),
    )
    forged_registry = replace(
        pending_registry,
        action_packet_lifecycle_entries=(forged_entry,),
    )
    assert acp.validate_action_commit_packet_registry_v02(
        forged_registry
    )[0] is False


def test_g2a2b_outcome_attempt_must_reuse_immediately_preceding_pending(
    root_bound_fixture: _RootBoundFixtureV01,
) -> None:
    root_bound = root_bound_fixture.root_bound_projection
    packet_id = root_bound.packet_identity.packet_id
    registry, pending = _g2a2b_pending_registry(root_bound)
    entry = registry.action_packet_lifecycle_entries[0]
    wrong_attempt = acp.build_action_execution_attempt_identity_v01(
        packet_id=packet_id,
        idempotency_key=(
            root_bound.canonical_projection.idempotency_identity.idempotency_key
        ),
        attempt_ordinal=2,
        evaluation_context_id=pending.evaluation_context_id,
    )
    wrong = acp.build_action_packet_transition_event_v01(
        action_packet_transition_registry_profile=_g2a2a_registry(),
        transition_rule_id="g2a_t24_nonconsuming_failure",
        packet_id=packet_id,
        idempotency_key=(
            root_bound.canonical_projection.idempotency_identity.idempotency_key
        ),
        previous_transition_event_id=pending.transition_event_id,
        owning_local_root_id=ROOT_ID,
        root_decision_ref=None,
        transition_evidence_bindings=_g2a2a_bindings(
            "g2a_t24_nonconsuming_failure"
        ),
        dependency_set_candidate_fingerprint=(
            root_bound.canonical_projection.dependency_set_candidate_fingerprint
        ),
        temporal_authority_fingerprint=(
            root_bound.canonical_projection.temporal_authority_fingerprint
        ),
        evaluation_time=EVALUATION_TIME,
        evaluation_time_source=EVALUATION_TIME_SOURCE,
        evaluation_context_id=pending.evaluation_context_id,
        execution_attempt_identity=wrong_attempt,
        receipt_ref=None,
    )
    with pytest.raises(ValueError):
        acp.record_action_packet_nonconsuming_outcome_v01(
            registry,
            packet_id=packet_id,
            transition_event=wrong,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )


def _g2a2_final_entry(
    registry: acp.ActionCommitPacketRegistryV02,
    packet_id: str,
) -> acp.ActionPacketLifecycleEntryV01:
    return next(
        entry
        for entry in registry.action_packet_lifecycle_entries
        if entry.root_bound_genesis.packet_identity.packet_id == packet_id
    )


def _g2a2_final_registry_with_event(
    registry: acp.ActionCommitPacketRegistryV02,
    packet_id: str,
    event: acp.ActionPacketTransitionEventV01,
    *,
    disposition_event: acp.IdempotencyDispositionEventV01 | None = None,
) -> acp.ActionCommitPacketRegistryV02:
    entry = _g2a2_final_entry(registry, packet_id)
    forged_entry = replace(
        entry,
        transition_events=entry.transition_events + (event,),
    )
    return replace(
        registry,
        action_packet_lifecycle_entries=tuple(
            forged_entry if candidate is entry else candidate
            for candidate in registry.action_packet_lifecycle_entries
        ),
        idempotency_disposition_events=(
            registry.idempotency_disposition_events
            if disposition_event is None
            else registry.idempotency_disposition_events
            + (disposition_event,)
        ),
    )


def _g2a2_final_live_t24(
    registry: acp.ActionCommitPacketRegistryV02,
    packet_id: str,
    *,
    evaluation_time: int | None = None,
) -> acp.ActionPacketTransitionEventV01:
    state = acp.derive_action_packet_lifecycle_state_v01(
        registry,
        packet_id=packet_id,
    )
    return _g2a2b_event(
        _g2a2_final_entry(registry, packet_id),
        "g2a_t24_nonconsuming_failure",
        evaluation_time=evaluation_time,
        latest_disposition_event_id=state.latest_disposition_event_id,
    )


def _g2a2_final_failed_nonconsuming_registry(
    root_bound: acp.SupplierRootBoundActionCommitPacketV02ProjectionV01,
) -> tuple[
    acp.ActionCommitPacketRegistryV02,
    acp.ActionPacketTransitionEventV01,
]:
    packet_id = root_bound.packet_identity.packet_id
    registry, _ = _g2a2b_pending_registry(root_bound)
    failure = _g2a2_final_live_t24(registry, packet_id)
    registry = acp.record_action_packet_nonconsuming_outcome_v01(
        registry,
        packet_id=packet_id,
        transition_event=failure,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    return registry, failure


def _g2a2_final_expiry_source(
    root_bound: acp.SupplierRootBoundActionCommitPacketV02ProjectionV01,
    rule_id: str,
) -> acp.ActionCommitPacketRegistryV02:
    packet_id = root_bound.packet_identity.packet_id
    registry = _g2a2b_recorded_genesis(root_bound)
    if rule_id == "g2a_t11_created_expire":
        return registry
    registry, _, _ = _g2a2b_activate(registry, packet_id)
    if rule_id == "g2a_t12_authorized_expire":
        return registry
    registry, _ = _g2a2b_append(registry, packet_id, "g2a_t02_queue")
    if rule_id == "g2a_t13_queued_expire":
        return registry
    registry, _ = _g2a2b_append(
        registry,
        packet_id,
        "g2a_t03_pending",
        evaluation_context_id="evaluation_context:g2a2_final:expiry",
    )
    if rule_id == "g2a_t14_pending_expire":
        return registry
    failure = _g2a2_final_live_t24(registry, packet_id)
    return acp.record_action_packet_nonconsuming_outcome_v01(
        registry,
        packet_id=packet_id,
        transition_event=failure,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )


def _g2a2_final_replace_t24_binding(
    event: acp.ActionPacketTransitionEventV01,
    *,
    evidence_ref: str | None = None,
    evidence_sha256: str | None = None,
    validator_profile_id: str | None = None,
    remove: bool = False,
    duplicate: bool = False,
) -> acp.ActionPacketTransitionEventV01:
    bindings: list[acp.TransitionEvidenceBindingV01] = []
    replacement: acp.TransitionEvidenceBindingV01 | None = None
    for binding in event.transition_evidence_bindings:
        if binding.evidence_code != "latest_disposition_event_binding_valid":
            bindings.append(binding)
            continue
        if remove:
            continue
        replacement = acp.build_transition_evidence_binding_v01(
            action_packet_transition_registry_profile=_g2a2a_registry(),
            transition_rule_id=event.transition_rule_id,
            evidence_code=binding.evidence_code,
            evidence_ref=(
                binding.evidence_ref
                if evidence_ref is None
                else evidence_ref
            ),
            evidence_sha256=(
                binding.evidence_sha256
                if evidence_sha256 is None
                else evidence_sha256
            ),
            validator_profile_id=(
                binding.validator_profile_id
                if validator_profile_id is None
                else validator_profile_id
            ),
        )
        bindings.append(replacement)
    if duplicate and replacement is not None:
        bindings.append(replacement)
    return _rebuild_transition_event(
        event,
        transition_evidence_bindings=tuple(bindings),
    )


@pytest.mark.parametrize(
    ("offset", "accepted"),
    ((-1, True), (0, True), (3599, True), (3600, False), (3601, False)),
)
def test_g2a2_final_activation_uses_canonical_temporal_truth(
    root_bound_fixture: _RootBoundFixtureV01,
    offset: int,
    accepted: bool,
) -> None:
    root_bound = root_bound_fixture.root_bound_projection
    packet_id = root_bound.packet_identity.packet_id
    issued = root_bound.canonical_projection.temporal_authority.issued_at_utc
    registry = _g2a2b_recorded_genesis(root_bound)
    event, reserve = _g2a2b_activation_pair(
        registry,
        packet_id,
        evaluation_time=issued + offset,
    )
    if accepted:
        activated = acp.activate_action_packet_lifecycle_v01(
            registry,
            packet_id=packet_id,
            transition_event=event,
            disposition_event=reserve,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )
        state = acp.derive_action_packet_lifecycle_state_v01(
            activated,
            packet_id=packet_id,
        )
        assert state.lifecycle_state == "ROOT_AUTHORIZED"
        assert state.executable is False
        assert acp.validate_action_commit_packet_registry_v02(
            activated
        ) == (True, ())
    else:
        before = repr(registry).encode("utf-8")
        with pytest.raises(
            ValueError,
            match="^action_packet_activation_after_expiry_forbidden$",
        ):
            acp.activate_action_packet_lifecycle_v01(
                registry,
                packet_id=packet_id,
                transition_event=event,
                disposition_event=reserve,
                action_packet_transition_registry_profile=_g2a2a_registry(),
            )
        assert repr(registry).encode("utf-8") == before
        forged = _g2a2_final_registry_with_event(
            registry,
            packet_id,
            event,
            disposition_event=reserve,
        )
        assert acp.validate_action_commit_packet_registry_v02(
            forged
        )[0] is False


def test_g2a2_final_queue_pending_and_retry_require_valid_interval(
    root_bound_fixture: _RootBoundFixtureV01,
) -> None:
    root_bound = root_bound_fixture.root_bound_projection
    packet_id = root_bound.packet_identity.packet_id
    temporal = root_bound.canonical_projection.temporal_authority

    registry = _g2a2b_recorded_genesis(root_bound)
    registry, _, _ = _g2a2b_activate(
        registry,
        packet_id,
        evaluation_time=temporal.issued_at_utc - 1,
    )
    entry = _g2a2_final_entry(registry, packet_id)
    early_queue = _g2a2b_event(
        entry,
        "g2a_t02_queue",
        evaluation_time=temporal.issued_at_utc - 1,
    )
    with pytest.raises(
        ValueError,
        match="^action_packet_transition_temporal_truth_invalid$",
    ):
        acp.append_action_packet_lifecycle_transition_v01(
            registry,
            packet_id=packet_id,
            transition_event=early_queue,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )
    assert acp.validate_action_commit_packet_registry_v02(
        _g2a2_final_registry_with_event(
            registry,
            packet_id,
            early_queue,
        )
    )[0] is False

    valid_queue = _g2a2b_event(
        entry,
        "g2a_t02_queue",
        evaluation_time=temporal.issued_at_utc,
    )
    registry = acp.append_action_packet_lifecycle_transition_v01(
        registry,
        packet_id=packet_id,
        transition_event=valid_queue,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    expired_pending = _g2a2b_event(
        _g2a2_final_entry(registry, packet_id),
        "g2a_t03_pending",
        evaluation_time=temporal.expires_at_utc,
        evaluation_context_id="evaluation_context:g2a2_final:expired_pending",
    )
    with pytest.raises(
        ValueError,
        match="^action_packet_transition_temporal_truth_invalid$",
    ):
        acp.append_action_packet_lifecycle_transition_v01(
            registry,
            packet_id=packet_id,
            transition_event=expired_pending,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )
    assert acp.validate_action_commit_packet_registry_v02(
        _g2a2_final_registry_with_event(
            registry,
            packet_id,
            expired_pending,
        )
    )[0] is False

    failed_registry, _ = _g2a2_final_failed_nonconsuming_registry(root_bound)
    for evaluation_time in (
        temporal.expires_at_utc,
        temporal.expires_at_utc + 1,
    ):
        expired_retry = _g2a2b_event(
            _g2a2_final_entry(failed_registry, packet_id),
            "g2a_t25_retry",
            evaluation_time=evaluation_time,
        )
        with pytest.raises(
            ValueError,
            match="^action_packet_transition_temporal_truth_invalid$",
        ):
            acp.append_action_packet_lifecycle_transition_v01(
                failed_registry,
                packet_id=packet_id,
                transition_event=expired_retry,
                action_packet_transition_registry_profile=_g2a2a_registry(),
            )
        assert acp.validate_action_commit_packet_registry_v02(
            _g2a2_final_registry_with_event(
                failed_registry,
                packet_id,
                expired_retry,
            )
        )[0] is False


@pytest.mark.parametrize(
    "rule_id",
    (
        "g2a_t11_created_expire",
        "g2a_t12_authorized_expire",
        "g2a_t13_queued_expire",
        "g2a_t14_pending_expire",
        "g2a_t15_failed_expire",
    ),
)
def test_g2a2_final_expiry_rules_use_exact_half_open_boundary(
    root_bound_fixture: _RootBoundFixtureV01,
    rule_id: str,
) -> None:
    root_bound = root_bound_fixture.root_bound_projection
    packet_id = root_bound.packet_identity.packet_id
    expires = root_bound.canonical_projection.temporal_authority.expires_at_utc
    early_registry = _g2a2_final_expiry_source(root_bound, rule_id)
    early = _g2a2b_event(
        _g2a2_final_entry(early_registry, packet_id),
        rule_id,
        evaluation_time=expires - 1,
    )
    with pytest.raises(
        ValueError,
        match="^action_packet_expiry_not_reached$",
    ):
        acp.append_action_packet_lifecycle_transition_v01(
            early_registry,
            packet_id=packet_id,
            transition_event=early,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )
    assert acp.validate_action_commit_packet_registry_v02(
        _g2a2_final_registry_with_event(
            early_registry,
            packet_id,
            early,
        )
    )[0] is False

    for evaluation_time in (expires, expires + 1):
        registry = _g2a2_final_expiry_source(root_bound, rule_id)
        event = _g2a2b_event(
            _g2a2_final_entry(registry, packet_id),
            rule_id,
            evaluation_time=evaluation_time,
        )
        updated = acp.append_action_packet_lifecycle_transition_v01(
            registry,
            packet_id=packet_id,
            transition_event=event,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )
        assert acp.derive_action_packet_lifecycle_state_v01(
            updated,
            packet_id=packet_id,
        ).lifecycle_state == "EXPIRED"


@pytest.mark.parametrize(
    "rule_id",
    (
        "g2a_t04_fulfill_mock",
        "g2a_t24_nonconsuming_failure",
        "g2a_t26_uncertain_adapter_outcome",
    ),
)
def test_g2a2_final_outcome_attempt_context_cannot_change(
    root_bound_fixture: _RootBoundFixtureV01,
    rule_id: str,
) -> None:
    root_bound = root_bound_fixture.root_bound_projection
    packet_id = root_bound.packet_identity.packet_id
    registry, _ = _g2a2b_pending_registry(root_bound)
    if rule_id == "g2a_t24_nonconsuming_failure":
        event = _g2a2_final_live_t24(registry, packet_id)
    else:
        event = _g2a2b_event(
            _g2a2_final_entry(registry, packet_id),
            rule_id,
        )
    forged = _rebuild_transition_event(
        event,
        evaluation_context_id="evaluation_context:g2a2_final:forged",
    )
    assert acp.validate_action_packet_transition_event_v01(
        forged,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    ) == (True, ())
    assert acp.validate_action_packet_transition_history_v01(
        _g2a2_final_entry(registry, packet_id).transition_events + (forged,),
        root_bound_genesis=root_bound,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )[0] is False
    before = repr(registry).encode("utf-8")
    with pytest.raises(
        ValueError,
        match="^action_packet_transition_attempt_context_mismatch$",
    ):
        if rule_id == "g2a_t24_nonconsuming_failure":
            acp.record_action_packet_nonconsuming_outcome_v01(
                registry,
                packet_id=packet_id,
                transition_event=forged,
                action_packet_transition_registry_profile=_g2a2a_registry(),
            )
        else:
            disposition_class = (
                "CONSUME"
                if rule_id == "g2a_t04_fulfill_mock"
                else "UNCERTAIN_CLOSE"
            )
            state = acp.derive_action_packet_lifecycle_state_v01(
                registry,
                packet_id=packet_id,
            )
            disposition = _g2a2b_outcome_disposition(
                state,
                forged,
                disposition_class,
            )
            operation = (
                acp.record_action_packet_consumed_outcome_v01
                if disposition_class == "CONSUME"
                else acp.record_action_packet_uncertain_outcome_v01
            )
            operation(
                registry,
                packet_id=packet_id,
                transition_event=forged,
                disposition_event=disposition,
                action_packet_transition_registry_profile=_g2a2a_registry(),
            )
    assert repr(registry).encode("utf-8") == before


def test_g2a2_final_receipt_attempt_context_cannot_change(
    root_bound_fixture: _RootBoundFixtureV01,
) -> None:
    root_bound = root_bound_fixture.root_bound_projection
    packet_id = root_bound.packet_identity.packet_id
    registry, _ = _g2a2b_pending_registry(root_bound)
    fulfilled = _g2a2b_event(
        _g2a2_final_entry(registry, packet_id),
        "g2a_t04_fulfill_mock",
    )
    state = acp.derive_action_packet_lifecycle_state_v01(
        registry,
        packet_id=packet_id,
    )
    registry = acp.record_action_packet_consumed_outcome_v01(
        registry,
        packet_id=packet_id,
        transition_event=fulfilled,
        disposition_event=_g2a2b_outcome_disposition(
            state,
            fulfilled,
            "CONSUME",
        ),
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    receipt = _g2a2b_event(
        _g2a2_final_entry(registry, packet_id),
        "g2a_t05_receipt",
        receipt_ref="receipt:g2a2_final",
    )
    forged = _rebuild_transition_event(
        receipt,
        evaluation_context_id="evaluation_context:g2a2_final:receipt_forged",
    )
    assert acp.validate_action_packet_transition_event_v01(
        forged,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    ) == (True, ())
    consumed = acp.derive_action_packet_lifecycle_state_v01(
        registry,
        packet_id=packet_id,
    )
    confirmation = _g2a2b_outcome_disposition(
        consumed,
        forged,
        "RECEIPT_CONFIRM",
    )
    with pytest.raises(
        ValueError,
        match="^action_packet_transition_attempt_context_mismatch$",
    ):
        acp.record_action_packet_receipt_confirmation_v01(
            registry,
            packet_id=packet_id,
            transition_event=forged,
            disposition_event=confirmation,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )


def test_g2a2_final_t24_binds_exact_latest_disposition_event(
    root_bound_fixture: _RootBoundFixtureV01,
) -> None:
    root_bound = root_bound_fixture.root_bound_projection
    packet_id = root_bound.packet_identity.packet_id
    registry, _ = _g2a2b_pending_registry(root_bound)
    state = acp.derive_action_packet_lifecycle_state_v01(
        registry,
        packet_id=packet_id,
    )
    event = _g2a2_final_live_t24(registry, packet_id)
    binding = next(
        item
        for item in event.transition_evidence_bindings
        if item.evidence_code == "latest_disposition_event_binding_valid"
    )
    assert binding.evidence_ref == state.latest_disposition_event_id
    assert binding.evidence_sha256 == state.latest_disposition_event_id.split(
        ":",
        1,
    )[1]
    assert (
        binding.validator_profile_id
        == acp.IDEMPOTENCY_DISPOSITION_EVENT_PROFILE_ID_V01
    )
    updated = acp.record_action_packet_nonconsuming_outcome_v01(
        registry,
        packet_id=packet_id,
        transition_event=event,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    assert (
        acp.derive_action_packet_lifecycle_state_v01(
            updated,
            packet_id=packet_id,
        ).latest_disposition_event_id
        == state.latest_disposition_event_id
    )


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("evidence_ref", "idem_event_v01:" + "1" * 64),
        ("evidence_ref", "evidence:not_latest"),
        ("evidence_sha256", "2" * 64),
        ("validator_profile_id", "validator:not_disposition_event"),
    ),
)
def test_g2a2_final_t24_rejects_inexact_latest_binding(
    root_bound_fixture: _RootBoundFixtureV01,
    field: str,
    value: str,
) -> None:
    root_bound = root_bound_fixture.root_bound_projection
    packet_id = root_bound.packet_identity.packet_id
    registry, _ = _g2a2b_pending_registry(root_bound)
    event = _g2a2_final_live_t24(registry, packet_id)
    forged = _g2a2_final_replace_t24_binding(
        event,
        **{field: value},
    )
    with pytest.raises(
        ValueError,
        match="^latest_disposition_event_binding_invalid$",
    ):
        acp.record_action_packet_nonconsuming_outcome_v01(
            registry,
            packet_id=packet_id,
            transition_event=forged,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )
    forged_registry = _g2a2_final_registry_with_event(
        registry,
        packet_id,
        forged,
    )
    assert acp.validate_action_commit_packet_registry_v02(
        forged_registry
    )[0] is False


@pytest.mark.parametrize(("remove", "duplicate"), ((True, False), (False, True)))
def test_g2a2_final_t24_rejects_missing_or_duplicate_latest_binding(
    root_bound_fixture: _RootBoundFixtureV01,
    remove: bool,
    duplicate: bool,
) -> None:
    root_bound = root_bound_fixture.root_bound_projection
    packet_id = root_bound.packet_identity.packet_id
    registry, _ = _g2a2b_pending_registry(root_bound)
    forged = _g2a2_final_replace_t24_binding(
        _g2a2_final_live_t24(registry, packet_id),
        remove=remove,
        duplicate=duplicate,
    )
    with pytest.raises(ValueError):
        acp.record_action_packet_nonconsuming_outcome_v01(
            registry,
            packet_id=packet_id,
            transition_event=forged,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )


def test_g2a2_final_historical_t24_uses_then_latest_not_later_consume(
    root_bound_fixture: _RootBoundFixtureV01,
) -> None:
    root_bound = root_bound_fixture.root_bound_projection
    packet_id = root_bound.packet_identity.packet_id
    registry, failure = _g2a2_final_failed_nonconsuming_registry(root_bound)
    reserve_id = registry.idempotency_disposition_events[0].idempotency_disposition_event_id
    registry, _ = _g2a2b_append(registry, packet_id, "g2a_t25_retry")
    registry, _ = _g2a2b_append(
        registry,
        packet_id,
        "g2a_t03_pending",
        evaluation_context_id="evaluation_context:g2a2_final:attempt_2",
    )
    fulfilled = _g2a2b_event(
        _g2a2_final_entry(registry, packet_id),
        "g2a_t04_fulfill_mock",
    )
    state = acp.derive_action_packet_lifecycle_state_v01(
        registry,
        packet_id=packet_id,
    )
    registry = acp.record_action_packet_consumed_outcome_v01(
        registry,
        packet_id=packet_id,
        transition_event=fulfilled,
        disposition_event=_g2a2b_outcome_disposition(
            state,
            fulfilled,
            "CONSUME",
        ),
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    t24_binding = next(
        binding
        for binding in failure.transition_evidence_bindings
        if binding.evidence_code == "latest_disposition_event_binding_valid"
    )
    assert t24_binding.evidence_ref == reserve_id
    assert (
        registry.idempotency_disposition_events[-1]
        .idempotency_disposition_event_id
        != reserve_id
    )
    assert acp.validate_action_commit_packet_registry_v02(registry) == (
        True,
        (),
    )


@pytest.mark.parametrize(
    "rule_id",
    (
        "g2a_t04_fulfill_mock",
        "g2a_t24_nonconsuming_failure",
        "g2a_t26_uncertain_adapter_outcome",
    ),
)
def test_g2a2_final_outcome_observation_may_follow_expiry(
    root_bound_fixture: _RootBoundFixtureV01,
    rule_id: str,
) -> None:
    root_bound = root_bound_fixture.root_bound_projection
    packet_id = root_bound.packet_identity.packet_id
    expires = root_bound.canonical_projection.temporal_authority.expires_at_utc
    registry, _ = _g2a2b_pending_registry(root_bound)
    if rule_id == "g2a_t24_nonconsuming_failure":
        event = _g2a2_final_live_t24(
            registry,
            packet_id,
            evaluation_time=expires + 1,
        )
        updated = acp.record_action_packet_nonconsuming_outcome_v01(
            registry,
            packet_id=packet_id,
            transition_event=event,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )
        assert acp.derive_action_packet_lifecycle_state_v01(
            updated,
            packet_id=packet_id,
        ).failed_provenance == "FAILED_NON_CONSUMING"
        return
    event = _g2a2b_event(
        _g2a2_final_entry(registry, packet_id),
        rule_id,
        evaluation_time=expires + 1,
    )
    state = acp.derive_action_packet_lifecycle_state_v01(
        registry,
        packet_id=packet_id,
    )
    disposition_class = (
        "CONSUME"
        if rule_id == "g2a_t04_fulfill_mock"
        else "UNCERTAIN_CLOSE"
    )
    disposition = _g2a2b_outcome_disposition(
        state,
        event,
        disposition_class,
    )
    operation = (
        acp.record_action_packet_consumed_outcome_v01
        if disposition_class == "CONSUME"
        else acp.record_action_packet_uncertain_outcome_v01
    )
    updated = operation(
        registry,
        packet_id=packet_id,
        transition_event=event,
        disposition_event=disposition,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    assert acp.validate_action_commit_packet_registry_v02(updated) == (
        True,
        (),
    )


def test_g2a2_final_receipt_observation_may_follow_expiry(
    root_bound_fixture: _RootBoundFixtureV01,
) -> None:
    root_bound = root_bound_fixture.root_bound_projection
    packet_id = root_bound.packet_identity.packet_id
    expires = root_bound.canonical_projection.temporal_authority.expires_at_utc
    registry, _ = _g2a2b_pending_registry(root_bound)
    fulfilled = _g2a2b_event(
        _g2a2_final_entry(registry, packet_id),
        "g2a_t04_fulfill_mock",
        evaluation_time=expires,
    )
    state = acp.derive_action_packet_lifecycle_state_v01(
        registry,
        packet_id=packet_id,
    )
    registry = acp.record_action_packet_consumed_outcome_v01(
        registry,
        packet_id=packet_id,
        transition_event=fulfilled,
        disposition_event=_g2a2b_outcome_disposition(
            state,
            fulfilled,
            "CONSUME",
        ),
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    receipt = _g2a2b_event(
        _g2a2_final_entry(registry, packet_id),
        "g2a_t05_receipt",
        evaluation_time=expires + 1,
        receipt_ref="receipt:g2a2_final:late",
    )
    consumed = acp.derive_action_packet_lifecycle_state_v01(
        registry,
        packet_id=packet_id,
    )
    updated = acp.record_action_packet_receipt_confirmation_v01(
        registry,
        packet_id=packet_id,
        transition_event=receipt,
        disposition_event=_g2a2b_outcome_disposition(
            consumed,
            receipt,
            "RECEIPT_CONFIRM",
        ),
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    assert acp.derive_action_packet_lifecycle_state_v01(
        updated,
        packet_id=packet_id,
    ).lifecycle_state == "RECEIPT_RECEIVED"


def test_g2a2_final_t24_custom_equality_reference_fails_closed(
    root_bound_fixture: _RootBoundFixtureV01,
) -> None:
    root_bound = root_bound_fixture.root_bound_projection
    packet_id = root_bound.packet_identity.packet_id
    registry, _ = _g2a2b_pending_registry(root_bound)
    event = _g2a2_final_live_t24(registry, packet_id)
    forged_bindings = tuple(
        replace(
            binding,
            evidence_ref=_AlwaysEqualStr(binding.evidence_ref),
        )
        if binding.evidence_code == "latest_disposition_event_binding_valid"
        else binding
        for binding in event.transition_evidence_bindings
    )
    forged = replace(
        event,
        transition_evidence_bindings=forged_bindings,
    )
    with pytest.raises(
        ValueError,
        match="^latest_disposition_event_binding_invalid$",
    ):
        acp.record_action_packet_nonconsuming_outcome_v01(
            registry,
            packet_id=packet_id,
            transition_event=forged,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )
    assert acp.validate_action_commit_packet_registry_v02(
        _g2a2_final_registry_with_event(
            registry,
            packet_id,
            forged,
        )
    )[0] is False


@pytest.mark.parametrize(
    "rule_id",
    (
        "g2a_t06_created_block",
        "g2a_t07_authorized_block",
        "g2a_t08_queued_block",
        "g2a_t09_pending_block",
        "g2a_t10_failed_block",
    ),
)
def test_g2a2_final_invalidation_mutation_requires_g2a3(
    root_bound_fixture: _RootBoundFixtureV01,
    rule_id: str,
) -> None:
    root_bound = root_bound_fixture.root_bound_projection
    packet_id = root_bound.packet_identity.packet_id
    if rule_id == "g2a_t06_created_block":
        registry = _g2a2b_recorded_genesis(root_bound)
    elif rule_id == "g2a_t07_authorized_block":
        registry = _g2a2b_recorded_genesis(root_bound)
        registry, _, _ = _g2a2b_activate(registry, packet_id)
    elif rule_id == "g2a_t08_queued_block":
        registry = _g2a2b_recorded_genesis(root_bound)
        registry, _, _ = _g2a2b_activate(registry, packet_id)
        registry, _ = _g2a2b_append(
            registry,
            packet_id,
            "g2a_t02_queue",
        )
    elif rule_id == "g2a_t09_pending_block":
        registry, _ = _g2a2b_pending_registry(root_bound)
    else:
        registry, _ = _g2a2_final_failed_nonconsuming_registry(root_bound)
    event = _g2a2b_event(
        _g2a2_final_entry(registry, packet_id),
        rule_id,
    )
    assert acp.validate_action_packet_transition_event_v01(
        event,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    ) == (True, ())
    before = repr(registry).encode("utf-8")
    with pytest.raises(
        ValueError,
        match="^invalidation_transition_requires_g2a3_binding$",
    ):
        acp.append_action_packet_lifecycle_transition_v01(
            registry,
            packet_id=packet_id,
            transition_event=event,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )
    assert repr(registry).encode("utf-8") == before
    forged = _g2a2_final_registry_with_event(
        registry,
        packet_id,
        event,
    )
    valid, reasons = acp.validate_action_commit_packet_registry_v02(forged)
    assert valid is False
    assert (
        "action_packet_registry_lifecycle_entry_invalid" in reasons
        or "invalidation_transition_requires_g2a3_binding" in reasons
    )


def _g2a2_final_same_key_successor(
    predecessor: acp.SupplierRootBoundActionCommitPacketV02ProjectionV01,
) -> acp.SupplierRootBoundActionCommitPacketV02ProjectionV01:
    source = acp.build_supplier_a_mock_action_commit_packet_fixture_v02()
    altered = replace(
        source,
        packet_id="legacy:g2a2_final_same_key_successor",
        source_root_decision_ref="legacy:g2a2_final_same_key_root",
        ttl=replace(
            source.ttl,
            created_at="2026-07-08T00:10:00Z",
            expires_at="2026-07-08T01:10:00Z",
        ),
    )
    successor = _root_bound_from_canonical(_projection(packet=altered))
    assert (
        successor.canonical_projection.logical_intent.root_owned_intent_id
        == predecessor.canonical_projection.logical_intent.root_owned_intent_id
    )
    assert (
        successor.canonical_projection.idempotency_identity.idempotency_key
        == predecessor.canonical_projection.idempotency_identity.idempotency_key
    )
    assert successor.packet_identity.packet_id != predecessor.packet_identity.packet_id
    return successor


def test_g2a2_final_unlinked_same_key_activation_is_symmetric_and_closed(
    root_bound_fixture: _RootBoundFixtureV01,
) -> None:
    first = root_bound_fixture.root_bound_projection
    second = _g2a2_final_same_key_successor(first)
    registry = _g2a2b_recorded_genesis(first)
    before = repr(registry).encode("utf-8")
    with pytest.raises(
        ValueError,
        match="^authority_transition_requires_g2a3_binding$",
    ):
        acp.record_action_packet_genesis_v01(
            registry,
            root_bound_genesis=second,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )
    assert repr(registry).encode("utf-8") == before
    assert registry.idempotency_disposition_events == ()
    forged = replace(
        registry,
        action_packet_lifecycle_entries=(
            registry.action_packet_lifecycle_entries
            + (
                acp.ActionPacketLifecycleEntryV01(
                    root_bound_genesis=second,
                    transition_registry_id=(
                        _g2a2a_registry().transition_registry_id
                    ),
                    transition_events=(),
                ),
            )
        ),
    )
    valid, reasons = acp.validate_action_commit_packet_registry_v02(forged)
    assert valid is False
    assert "authority_transition_requires_g2a3_binding" in reasons


def test_g2a2_retry_policy_no_retry_blocks_manual_history_bypass() -> None:
    policy = _policy(retry_policy="NO_RETRY")
    assert acp.validate_action_authority_policy_profile_v01(policy) == (
        True,
        (),
    )
    root_bound = _root_bound_from_canonical(_projection(policy=policy))
    assert (
        acp.validate_supplier_root_bound_action_commit_packet_v02_projection_v01(
            root_bound
        )
        == (True, ())
    )
    packet_id = root_bound.packet_identity.packet_id
    registry, _ = _g2a2_final_failed_nonconsuming_registry(root_bound)
    entry = _g2a2_final_entry(registry, packet_id)
    retry = _g2a2b_event(entry, "g2a_t25_retry")
    assert acp.validate_action_packet_transition_event_v01(
        retry,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    ) == (True, ())

    source_bytes = repr(registry).encode("utf-8")
    source_transition_count = len(entry.transition_events)
    source_disposition_count = len(registry.idempotency_disposition_events)
    with pytest.raises(ValueError, match="^retry_policy_invalid$"):
        acp.append_action_packet_lifecycle_transition_v01(
            registry,
            packet_id=packet_id,
            transition_event=retry,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )
    assert repr(registry).encode("utf-8") == source_bytes
    assert len(
        _g2a2_final_entry(registry, packet_id).transition_events
    ) == source_transition_count
    assert (
        len(registry.idempotency_disposition_events)
        == source_disposition_count
    )

    forged_history = entry.transition_events + (retry,)
    valid, reasons = acp.validate_action_packet_transition_history_v01(
        forged_history,
        root_bound_genesis=root_bound,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    assert valid is False
    assert "retry_policy_invalid" in reasons

    forged_entry = replace(entry, transition_events=forged_history)
    valid, reasons = acp.validate_action_packet_lifecycle_entry_v01(
        forged_entry,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    assert valid is False
    assert "retry_policy_invalid" in reasons

    forged_registry = replace(
        registry,
        action_packet_lifecycle_entries=(forged_entry,),
    )
    assert acp.validate_action_commit_packet_registry_v02(
        forged_registry
    )[0] is False


def test_g2a2_retry_policy_nonconsuming_positive_control(
    root_bound_fixture: _RootBoundFixtureV01,
) -> None:
    root_bound = root_bound_fixture.root_bound_projection
    assert (
        root_bound.canonical_projection.authority_policy.retry_policy
        == "NON_CONSUMING_RETRY"
    )
    packet_id = root_bound.packet_identity.packet_id
    registry, _ = _g2a2_final_failed_nonconsuming_registry(root_bound)
    entry = _g2a2_final_entry(registry, packet_id)
    retry = _g2a2b_event(entry, "g2a_t25_retry")
    assert acp.validate_action_packet_transition_history_v01(
        entry.transition_events + (retry,),
        root_bound_genesis=root_bound,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    ) == (True, ())
    updated = acp.append_action_packet_lifecycle_transition_v01(
        registry,
        packet_id=packet_id,
        transition_event=retry,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    state = acp.derive_action_packet_lifecycle_state_v01(
        updated,
        packet_id=packet_id,
    )
    assert state.lifecycle_state == "QUEUED"
    assert state.idempotency_disposition == "RESERVED"


def _g2a3a_successor(
    predecessor: acp.SupplierRootBoundActionCommitPacketV02ProjectionV01,
    *,
    variation: str = "TTL",
    supersession_reason_class: str = "RENEWAL",
) -> acp.SupplierRootBoundActionCommitPacketV02ProjectionV01:
    source = predecessor.canonical_projection.source_packet
    packet = replace(
        source,
        packet_id=f"legacy:g2a3a_successor:{variation.lower()}",
        source_root_decision_ref=(
            f"legacy:g2a3a_successor_root:{variation.lower()}"
        ),
    )
    policy = predecessor.canonical_projection.authority_policy
    dependency = predecessor.canonical_projection.dependency_candidate
    if variation == "TTL":
        packet = replace(
            packet,
            ttl=replace(
                packet.ttl,
                created_at="2026-07-08T00:10:00Z",
                expires_at="2026-07-08T01:10:00Z",
            ),
        )
    elif variation == "ADAPTER":
        packet = replace(
            packet,
            adapter_binding=replace(
                packet.adapter_binding,
                adapter_kind="mock_bank_sandbox_renewed",
            ),
        )
    elif variation == "DEPENDENCY":
        dependency = _dependency(content_sha256="9" * 64)
    elif variation == "POLICY":
        policy = _policy(policy_version="supplier_policy_v02")
    elif variation == "MATERIAL":
        packet = replace(
            packet,
            scope=replace(packet.scope, amount="1300.00"),
        )
    else:
        raise AssertionError(f"unknown renewal variation: {variation}")
    canonical = _projection(
        packet=packet,
        policy=policy,
        dependency=dependency,
        predecessor_packet_id=predecessor.packet_identity.packet_id,
        supersession_reason_class=supersession_reason_class,
    )
    return _root_bound_from_canonical(canonical)


def _g2a3a_candidate_root_projection(
    canonical: acp.SupplierActionCommitPacketCanonicalProjectionV01,
    *,
    candidate_kind: str,
    candidate_id: str,
    predecessor: acp.SupplierRootBoundActionCommitPacketV02ProjectionV01,
) -> acp.RootDecisionCandidateProjectionV01:
    predecessor_decision = (
        predecessor.root_decision_projection.root_decision_result
    )
    _, _, kernel, decision_input, result = _build_frozen_root_evidence(
        canonical,
        candidate_id=candidate_id,
        candidate_kind=candidate_kind,
        state_updates={
            "policy_state": {
                "policy_id": (
                    predecessor.canonical_projection
                    .authority_policy_fingerprint
                ),
            },
            "prior_root_state": {
                "prior_decision_id": predecessor_decision.decision_id,
                "prior_decision": "ACCEPT",
                "prior_selected_candidate_id": (
                    predecessor.canonical_projection.authorization_candidate
                    .root_packet_authorization_candidate_id
                ),
            },
        },
    )
    return acp.build_root_decision_candidate_projection_v01(
        candidate_kind=candidate_kind,
        projected_candidate_id=candidate_id,
        root_decision_kernel=kernel,
        root_decision_input=decision_input,
        root_decision_result=result,
    )


def _g2a3a_supersession_bundle(
    predecessor: acp.SupplierRootBoundActionCommitPacketV02ProjectionV01,
    successor: acp.SupplierRootBoundActionCommitPacketV02ProjectionV01,
) -> tuple[
    acp.SupersessionCandidateV01,
    acp.RootDecisionCandidateProjectionV01,
    acp.AcceptedSupersessionBindingV01,
]:
    canonical = predecessor.canonical_projection
    supersession_reason_class = (
        successor.canonical_projection.authorization_candidate
        .supersession_reason_class
    )
    assert supersession_reason_class is not None
    candidate = acp.build_supersession_candidate_v01(
        owning_local_root_id=canonical.owning_local_root_id,
        predecessor_packet_id=predecessor.packet_identity.packet_id,
        successor_packet_authorization_candidate_id=(
            successor.canonical_projection.authorization_candidate
            .root_packet_authorization_candidate_id
        ),
        stable_logical_intent_id=(
            successor.canonical_projection.logical_intent.root_owned_intent_id
        ),
        idempotency_key=(
            successor.canonical_projection.idempotency_identity.idempotency_key
        ),
        supersession_reason_class=supersession_reason_class,
        policy_fingerprint=canonical.authority_policy_fingerprint,
    )
    root_projection = _g2a3a_candidate_root_projection(
        successor.canonical_projection,
        candidate_kind="SUPERSESSION",
        candidate_id=candidate.supersession_candidate_id,
        predecessor=predecessor,
    )
    binding = acp.build_accepted_supersession_binding_v01(
        candidate=candidate,
        root_projection=root_projection,
        predecessor=predecessor,
        successor=successor,
    )
    return candidate, root_projection, binding


@pytest.fixture(scope="module")
def g2a3a_fixture(
    root_bound_fixture: _RootBoundFixtureV01,
) -> _G2A3AFixtureV01:
    predecessor = root_bound_fixture.root_bound_projection
    successor = _g2a3a_successor(predecessor)
    canonical = predecessor.canonical_projection
    source_decision = (
        predecessor.root_decision_projection.root_decision_result.decision_id
    )
    revocation_candidate = acp.build_revocation_candidate_v01(
        owning_local_root_id=canonical.owning_local_root_id,
        packet_id=predecessor.packet_identity.packet_id,
        source_authorization_decision_id=source_decision,
        idempotency_key=canonical.idempotency_identity.idempotency_key,
        revocation_reason_class="MANUAL_REVOCATION",
        evidence_refs=(
            "evidence:revocation_policy",
            "evidence:revocation_operator",
        ),
        evidence_hashes=("2" * 64, "1" * 64),
        evaluation_time=EVALUATION_TIME,
        policy_fingerprint=canonical.authority_policy_fingerprint,
    )
    revocation_root_projection = _g2a3a_candidate_root_projection(
        canonical,
        candidate_kind="REVOCATION",
        candidate_id=revocation_candidate.revocation_candidate_id,
        predecessor=predecessor,
    )
    accepted_revocation_binding = acp.build_accepted_revocation_binding_v01(
        candidate=revocation_candidate,
        root_projection=revocation_root_projection,
        packet=predecessor,
    )
    (
        supersession_candidate,
        supersession_root_projection,
        accepted_supersession_binding,
    ) = _g2a3a_supersession_bundle(predecessor, successor)
    return _G2A3AFixtureV01(
        predecessor=predecessor,
        successor=successor,
        revocation_candidate=revocation_candidate,
        revocation_root_projection=revocation_root_projection,
        accepted_revocation_binding=accepted_revocation_binding,
        supersession_candidate=supersession_candidate,
        supersession_root_projection=supersession_root_projection,
        accepted_supersession_binding=accepted_supersession_binding,
    )


def _g2a3a_invalidation(
    fixture: _G2A3AFixtureV01,
    invalidation_class: str,
) -> acp.ActionInvalidationEvidenceV01:
    predecessor = fixture.predecessor
    canonical = predecessor.canonical_projection
    record = canonical.dependency_candidate.dependency_records[0]
    dependency_id = record.dependency_id
    evidence_ref = record.evidence_ref
    evidence_sha256 = record.content_sha256
    time_envelope_id = record.time_envelope_id
    freshness_policy_id = record.freshness_policy_id
    authority_effect = "DETERMINISTIC_BLOCK"
    decision_id = None
    decision_hash = None
    if invalidation_class in {
        "ROOT_BOUND_KILL_SWITCH",
        "MANUAL_CANCEL_EVIDENCE",
    }:
        dependency_id = canonical.authority_policy.kill_switch_condition_refs[0]
        evidence_ref = f"evidence:{invalidation_class.lower()}"
        evidence_sha256 = "3" * 64
    elif invalidation_class == "ROOT_REVOCATION":
        binding = fixture.accepted_revocation_binding
        dependency_id = "dependency:root_revocation"
        evidence_ref = binding.accepted_revocation_binding_id
        evidence_sha256 = evidence_ref.split(":", 1)[1]
        authority_effect = "ROOT_REVOCATION"
        decision_id = binding.revocation_root_decision_id
        decision_hash = binding.revocation_root_decision_hash
    elif invalidation_class == "ROOT_SUPERSESSION":
        binding = fixture.accepted_supersession_binding
        dependency_id = "dependency:root_supersession"
        evidence_ref = binding.accepted_supersession_binding_id
        evidence_sha256 = evidence_ref.split(":", 1)[1]
        authority_effect = "ROOT_SUPERSESSION"
        decision_id = binding.supersession_root_decision_id
        decision_hash = binding.supersession_root_decision_hash
    return acp.build_action_invalidation_evidence_v01(
        source_invalidation_event_ref=(
            f"source_invalidation:{invalidation_class.lower()}"
        ),
        packet_id=predecessor.packet_identity.packet_id,
        dependency_id=dependency_id,
        invalidation_class=invalidation_class,
        evidence_ref=evidence_ref,
        evidence_sha256=evidence_sha256,
        observed_status=f"OBSERVED_{invalidation_class}",
        time_envelope_id=time_envelope_id,
        freshness_policy_id=freshness_policy_id,
        owning_local_root_id=canonical.owning_local_root_id,
        accepted_by_local_root_id=canonical.owning_local_root_id,
        acceptance_root_decision_id=decision_id,
        acceptance_root_decision_hash=decision_hash,
        authority_effect=authority_effect,
        root_decision_ref=decision_id,
        evaluation_time=EVALUATION_TIME,
        evaluation_time_source=EVALUATION_TIME_SOURCE,
        evaluation_context_id="evaluation_context:g2a3a_invalidation",
    )


def test_g2a3a_fixture_contracts_validate(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    fixture = g2a3a_fixture
    assert acp.validate_revocation_candidate_against_packet_v01(
        fixture.revocation_candidate,
        fixture.predecessor,
    ) == (True, ())
    assert acp.validate_supersession_candidate_against_packets_v01(
        fixture.supersession_candidate,
        fixture.predecessor,
        fixture.successor,
    ) == (True, ())
    assert acp.validate_revocation_root_context_coherence_v01(
        fixture.revocation_candidate,
        fixture.revocation_root_projection,
        fixture.predecessor,
    ) == (True, ())
    assert acp.validate_supersession_root_context_coherence_v01(
        fixture.supersession_candidate,
        fixture.supersession_root_projection,
        fixture.predecessor,
        fixture.successor,
    ) == (True, ())
    assert acp.validate_action_packet_renewal_relationship_v01(
        fixture.predecessor,
        fixture.successor,
        fixture.supersession_candidate,
        fixture.accepted_supersession_binding,
        root_projection=fixture.supersession_root_projection,
    ) == (True, ())


def _reidentify_revocation_candidate(
    value: acp.RevocationCandidateV01,
    **changes: object,
) -> acp.RevocationCandidateV01:
    provisional = replace(value, revocation_candidate_id="", **changes)
    return replace(
        provisional,
        revocation_candidate_id=acp.build_domain_separated_identity_v01(
            domain=acp.REVOCATION_CANDIDATE_DOMAIN_V01,
            prefix=acp.REVOCATION_CANDIDATE_PREFIX_V01,
            material=acp.revocation_candidate_material_v01(provisional),
        ),
    )


def _reidentify_supersession_candidate(
    value: acp.SupersessionCandidateV01,
    **changes: object,
) -> acp.SupersessionCandidateV01:
    provisional = replace(value, supersession_candidate_id="", **changes)
    return replace(
        provisional,
        supersession_candidate_id=acp.build_domain_separated_identity_v01(
            domain=acp.SUPERSESSION_CANDIDATE_DOMAIN_V01,
            prefix=acp.SUPERSESSION_CANDIDATE_PREFIX_V01,
            material=acp.supersession_candidate_material_v01(provisional),
        ),
    )


def _reidentify_invalidation(
    value: acp.ActionInvalidationEvidenceV01,
    **changes: object,
) -> acp.ActionInvalidationEvidenceV01:
    provisional = replace(value, invalidation_evidence_id="", **changes)
    return replace(
        provisional,
        invalidation_evidence_id=domain_separated_sha256_hex_v01(
            domain=acp.ACTION_INVALIDATION_EVIDENCE_DOMAIN_V01,
            payload=acp.canonical_material_bytes_v01(
                acp.action_invalidation_evidence_material_v01(provisional)
            ),
        ),
    )


def _reidentify_accepted_revocation(
    value: acp.AcceptedRevocationBindingV01,
    **changes: object,
) -> acp.AcceptedRevocationBindingV01:
    provisional = replace(
        value,
        accepted_revocation_binding_id="",
        **changes,
    )
    return replace(
        provisional,
        accepted_revocation_binding_id=(
            acp.build_domain_separated_identity_v01(
                domain=acp.ACCEPTED_REVOCATION_BINDING_DOMAIN_V01,
                prefix=acp.ACCEPTED_REVOCATION_BINDING_PREFIX_V01,
                material=acp.accepted_revocation_binding_material_v01(
                    provisional
                ),
            )
        ),
    )


def _reidentify_accepted_supersession(
    value: acp.AcceptedSupersessionBindingV01,
    **changes: object,
) -> acp.AcceptedSupersessionBindingV01:
    provisional = replace(
        value,
        accepted_supersession_binding_id="",
        **changes,
    )
    return replace(
        provisional,
        accepted_supersession_binding_id=(
            acp.build_domain_separated_identity_v01(
                domain=acp.ACCEPTED_SUPERSESSION_BINDING_DOMAIN_V01,
                prefix=acp.ACCEPTED_SUPERSESSION_BINDING_PREFIX_V01,
                material=acp.accepted_supersession_binding_material_v01(
                    provisional
                ),
            )
        ),
    )


def _g2a3a_prior_state(
    fixture: _G2A3AFixtureV01,
) -> dict[str, dict[str, object]]:
    predecessor = fixture.predecessor
    return {
        "prior_root_state": {
            "prior_decision_id": (
                predecessor.root_decision_projection.root_decision_result
                .decision_id
            ),
            "prior_decision": "ACCEPT",
            "prior_selected_candidate_id": (
                predecessor.canonical_projection.authorization_candidate
                .root_packet_authorization_candidate_id
            ),
        },
    }


def test_g2a3a_exact_shapes_materials_and_vector(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    fixture = g2a3a_fixture
    revocation = fixture.revocation_candidate
    supersession = fixture.supersession_candidate
    assert acp.ROOT_DECISION_CANDIDATE_KINDS_V01 == (
        "PACKET_AUTHORIZATION",
        "REVOCATION",
        "SUPERSESSION",
    )
    assert acp.REVOCATION_CANDIDATE_PROFILE_ID_V01 == (
        "action_revocation_candidate_v01"
    )
    assert acp.REVOCATION_CANDIDATE_DOMAIN_V01 == (
        "HEDGEHOG_ACTION_REVOCATION_CANDIDATE_V01"
    )
    assert acp.REVOCATION_CANDIDATE_PREFIX_V01 == (
        "revocation_candidate_v01:"
    )
    assert acp.SUPERSESSION_CANDIDATE_DOMAIN_V01 == (
        "HEDGEHOG_ACTION_SUPERSESSION_CANDIDATE_V01"
    )
    assert acp.SUPERSESSION_CANDIDATE_PREFIX_V01 == (
        "supersession_candidate_v01:"
    )
    assert acp.ACTION_INVALIDATION_CLASSES_V01 == (
        "DEPENDENCY_CHANGED",
        "DEPENDENCY_STALE",
        "ROOT_BOUND_KILL_SWITCH",
        "MANUAL_CANCEL_EVIDENCE",
        "ROOT_REVOCATION",
        "ROOT_SUPERSESSION",
    )
    assert acp.ACTION_INVALIDATION_AUTHORITY_EFFECTS_V01 == (
        "DETERMINISTIC_BLOCK",
        "ROOT_REVOCATION",
        "ROOT_SUPERSESSION",
    )
    assert [field.name for field in fields(acp.RevocationCandidateV01)] == [
        "candidate_profile_id",
        "owning_local_root_id",
        "packet_id",
        "source_authorization_decision_id",
        "idempotency_key",
        "revocation_reason_class",
        "evidence_refs",
        "evidence_hashes",
        "evaluation_time",
        "policy_fingerprint",
        "revocation_candidate_id",
    ]
    assert tuple(
        key for key, _ in acp.revocation_candidate_material_v01(revocation)
    ) == (
        "candidate_profile_id",
        "owning_local_root_id",
        "packet_id",
        "source_authorization_decision_id",
        "idempotency_key",
        "revocation_reason_class",
        "evidence_refs",
        "evidence_hashes",
        "evaluation_time",
        "policy_fingerprint",
    )
    assert [field.name for field in fields(acp.SupersessionCandidateV01)] == [
        "owning_local_root_id",
        "predecessor_packet_id",
        "successor_packet_authorization_candidate_id",
        "stable_logical_intent_id",
        "idempotency_key",
        "supersession_reason_class",
        "policy_fingerprint",
        "supersession_candidate_id",
    ]
    assert tuple(
        key
        for key, _ in acp.supersession_candidate_material_v01(supersession)
    ) == (
        "owning_local_root_id",
        "predecessor_packet_id",
        "successor_packet_authorization_candidate_id",
        "stable_logical_intent_id",
        "idempotency_key",
        "supersession_reason_class",
        "policy_fingerprint",
    )
    assert [field.name for field in fields(
        acp.RootDecisionCandidateProjectionV01
    )] == [
        "candidate_kind",
        "projected_candidate_id",
        "root_decision_kernel",
        "root_decision_input",
        "root_decision_result",
        "source_root_decision_hash",
    ]
    assert [field.name for field in fields(
        acp.AcceptedRevocationBindingV01
    )] == [
        "revocation_candidate_id",
        "revocation_root_decision_id",
        "revocation_root_decision_hash",
        "owning_local_root_id",
        "packet_id",
        "prior_authorization_decision_id",
        "accepted_revocation_binding_id",
    ]
    assert [field.name for field in fields(
        acp.AcceptedSupersessionBindingV01
    )] == [
        "supersession_candidate_id",
        "supersession_root_decision_id",
        "supersession_root_decision_hash",
        "owning_local_root_id",
        "predecessor_packet_id",
        "prior_authorization_decision_id",
        "accepted_supersession_binding_id",
    ]
    assert revocation.revocation_candidate_id == G2A3A_REVOCATION_CANDIDATE_ID
    assert (
        supersession.supersession_candidate_id
        == G2A3A_SUPERSESSION_CANDIDATE_ID
    )
    assert (
        fixture.revocation_root_projection.root_decision_input.decision_input_id
        == G2A3A_REVOCATION_DECISION_INPUT_ID
    )
    assert (
        fixture.revocation_root_projection.root_decision_result.decision_id
        == G2A3A_REVOCATION_DECISION_ID
    )
    assert (
        fixture.revocation_root_projection.source_root_decision_hash
        == G2A3A_REVOCATION_DECISION_HASH
    )
    assert (
        fixture.accepted_revocation_binding
        .accepted_revocation_binding_id
        == G2A3A_ACCEPTED_REVOCATION_BINDING_ID
    )
    assert (
        fixture.supersession_root_projection.root_decision_input
        .decision_input_id
        == G2A3A_SUPERSESSION_DECISION_INPUT_ID
    )
    assert (
        fixture.supersession_root_projection.root_decision_result.decision_id
        == G2A3A_SUPERSESSION_DECISION_ID
    )
    assert (
        fixture.supersession_root_projection.source_root_decision_hash
        == G2A3A_SUPERSESSION_DECISION_HASH
    )
    assert (
        fixture.accepted_supersession_binding
        .accepted_supersession_binding_id
        == G2A3A_ACCEPTED_SUPERSESSION_BINDING_ID
    )
    forbidden_material_fields = {
        "new_root_decision_id",
        "new_root_decision_hash",
        "accepted_binding_id",
        "transition_event_id",
        "invalidation_evidence_id",
    }
    assert forbidden_material_fields.isdisjoint(
        key for key, _ in acp.revocation_candidate_material_v01(revocation)
    )
    assert forbidden_material_fields.isdisjoint(
        key
        for key, _ in acp.supersession_candidate_material_v01(supersession)
    )


def test_g2a3a_revocation_candidate_sorting_identity_and_context(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    fixture = g2a3a_fixture
    candidate = fixture.revocation_candidate
    assert candidate.candidate_profile_id == acp.REVOCATION_CANDIDATE_PROFILE_ID_V01
    assert candidate.evidence_refs == (
        "evidence:revocation_operator",
        "evidence:revocation_policy",
    )
    assert candidate.evidence_hashes == ("1" * 64, "2" * 64)
    assert acp.validate_revocation_candidate_v01(candidate) == (True, ())
    rebuilt = acp.build_revocation_candidate_v01(
        owning_local_root_id=candidate.owning_local_root_id,
        packet_id=candidate.packet_id,
        source_authorization_decision_id=(
            candidate.source_authorization_decision_id
        ),
        idempotency_key=candidate.idempotency_key,
        revocation_reason_class=candidate.revocation_reason_class,
        evidence_refs=tuple(reversed(candidate.evidence_refs)),
        evidence_hashes=tuple(reversed(candidate.evidence_hashes)),
        evaluation_time=candidate.evaluation_time,
        policy_fingerprint=candidate.policy_fingerprint,
    )
    assert rebuilt == candidate
    for refs, hashes in (
        (("evidence:a",), ()),
        (("evidence:a", "evidence:a"), ("1" * 64, "2" * 64)),
        (("evidence:a",), ("not-a-hash",)),
    ):
        with pytest.raises(ValueError):
            acp.build_revocation_candidate_v01(
                owning_local_root_id=candidate.owning_local_root_id,
                packet_id=candidate.packet_id,
                source_authorization_decision_id=(
                    candidate.source_authorization_decision_id
                ),
                idempotency_key=candidate.idempotency_key,
                revocation_reason_class=candidate.revocation_reason_class,
                evidence_refs=refs,
                evidence_hashes=hashes,
                evaluation_time=candidate.evaluation_time,
                policy_fingerprint=candidate.policy_fingerprint,
            )
    for forged in (
        _reidentify_revocation_candidate(
            candidate,
            owning_local_root_id="root:foreign",
        ),
        _reidentify_revocation_candidate(
            candidate,
            packet_id="acp_v02:" + "0" * 64,
        ),
        _reidentify_revocation_candidate(
            candidate,
            source_authorization_decision_id="0" * 64,
        ),
        _reidentify_revocation_candidate(
            candidate,
            idempotency_key="idem:action_v01:" + "0" * 64,
        ),
        _reidentify_revocation_candidate(
            candidate,
            policy_fingerprint="0" * 64,
        ),
    ):
        assert acp.validate_revocation_candidate_v01(forged) == (True, ())
        assert acp.validate_revocation_candidate_against_packet_v01(
            forged,
            fixture.predecessor,
        )[0] is False
    assert acp.validate_revocation_candidate_v01(
        replace(
            candidate,
            revocation_candidate_id=_AlwaysEqualStr(
                candidate.revocation_candidate_id
            ),
        )
    )[0] is False


def test_g2a3a_supersession_candidate_context_and_foreign_root(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    fixture = g2a3a_fixture
    candidate = fixture.supersession_candidate
    assert acp.validate_supersession_candidate_v01(candidate) == (True, ())
    assert candidate.predecessor_packet_id == (
        fixture.predecessor.packet_identity.packet_id
    )
    assert candidate.successor_packet_authorization_candidate_id == (
        fixture.successor.canonical_projection.authorization_candidate
        .root_packet_authorization_candidate_id
    )
    for forged in (
        _reidentify_supersession_candidate(
            candidate,
            owning_local_root_id="root:foreign",
        ),
        _reidentify_supersession_candidate(
            candidate,
            predecessor_packet_id="acp_v02:" + "0" * 64,
        ),
        _reidentify_supersession_candidate(
            candidate,
            successor_packet_authorization_candidate_id=(
                "root_packet_authorization_v01:" + "0" * 64
            ),
        ),
        _reidentify_supersession_candidate(
            candidate,
            stable_logical_intent_id="root_logical_intent_v01:" + "0" * 64,
        ),
        _reidentify_supersession_candidate(
            candidate,
            idempotency_key="idem:action_v01:" + "0" * 64,
        ),
    ):
        assert acp.validate_supersession_candidate_v01(forged) == (True, ())
        assert acp.validate_supersession_candidate_against_packets_v01(
            forged,
            fixture.predecessor,
            fixture.successor,
        )[0] is False
    assert acp.validate_supersession_candidate_v01(
        replace(
            candidate,
            supersession_candidate_id=_AlwaysEqualStr(
                candidate.supersession_candidate_id
            ),
        )
    )[0] is False


@pytest.mark.parametrize(
    "projection_name",
    ("revocation_root_projection", "supersession_root_projection"),
)
def test_g2a3a_root_projection_surfaces_are_exact(
    g2a3a_fixture: _G2A3AFixtureV01,
    projection_name: str,
) -> None:
    fixture = g2a3a_fixture
    projection = getattr(fixture, projection_name)
    assert acp.validate_root_decision_candidate_projection_v01(
        projection
    ) == (True, ())
    plain = root_decision.root_decision_input_to_plain_dict_v01(
        projection.root_decision_input
    )
    claims = plain["root_review_packet"]["synthesis_proposal"][
        "normalized_claims"
    ]
    assert [
        claim["claim_id"]
        for claim in claims
        if claim["claim_id"] == projection.projected_candidate_id
    ] == [projection.projected_candidate_id]
    claim = next(
        item
        for item in claims
        if item["claim_id"] == projection.projected_candidate_id
    )
    assert claim["object_or_value"] == {
        "candidate_id": projection.projected_candidate_id,
        "candidate_kind": projection.candidate_kind,
    }
    assert plain["post_vv_bundle"]["validated_candidate_ids"].count(
        projection.projected_candidate_id
    ) == 1
    assert projection.projected_candidate_id not in (
        plain["post_vv_bundle"]["rejected_candidate_ids"]
    )
    assert plain["gt_advisory"]["selected_candidate_id"] == (
        projection.projected_candidate_id
    )
    assert plain["permission_state"] == {
        "permission_required": False,
        "user_permission_present": False,
        "permission_scope_valid": True,
        "permission_ref": None,
    }
    result = projection.root_decision_result
    assert (
        result.decision,
        result.reason_code,
        result.root_commit_created,
        result.permission_created,
        result.final_output_created,
        result.effect_requested,
    ) == (
        "ACCEPT",
        "validated_candidate_accepted",
        True,
        False,
        False,
        False,
    )


def test_g2a3a_root_projection_rejects_kind_predicate_and_permission_drift(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    fixture = g2a3a_fixture
    projection = fixture.revocation_root_projection
    assert acp.validate_root_decision_candidate_projection_v01(
        replace(projection, candidate_kind="SUPERSESSION")
    )[0] is False
    assert acp.validate_root_decision_candidate_projection_v01(
        replace(
            projection,
            source_root_decision_hash=_AlwaysEqualStr(
                projection.source_root_decision_hash
            ),
        )
    )[0] is False
    variants = (
        {
            "claim_predicate": "root_packet_authorization_candidate",
        },
        {
            "claim_candidate_kind": "PACKET_AUTHORIZATION",
        },
        {
            "state_updates": {
                **_g2a3a_prior_state(fixture),
                "permission_state": {
                    "permission_required": True,
                    "user_permission_present": True,
                    "permission_scope_valid": True,
                    "permission_ref": PERMISSION_REF,
                },
            },
        },
    )
    for options in variants:
        state_updates = options.get(
            "state_updates",
            _g2a3a_prior_state(fixture),
        )
        _, _, kernel, decision_input, result = _build_frozen_root_evidence(
            fixture.predecessor.canonical_projection,
            candidate_id=fixture.revocation_candidate.revocation_candidate_id,
            candidate_kind="REVOCATION",
            claim_predicate=options.get("claim_predicate"),  # type: ignore[arg-type]
            claim_candidate_kind=options.get(  # type: ignore[arg-type]
                "claim_candidate_kind"
            ),
            state_updates=state_updates,  # type: ignore[arg-type]
        )
        forged = acp.RootDecisionCandidateProjectionV01(
            candidate_kind="REVOCATION",
            projected_candidate_id=(
                fixture.revocation_candidate.revocation_candidate_id
            ),
            root_decision_kernel=kernel,
            root_decision_input=decision_input,
            root_decision_result=result,
            source_root_decision_hash=(
                acp.build_action_source_root_decision_hash_v01(result)
            ),
        )
        assert acp.validate_root_decision_candidate_projection_v01(
            forged
        )[0] is False


def test_g2a3a_accepted_bindings_are_post_root_and_exact(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    fixture = g2a3a_fixture
    revocation = fixture.accepted_revocation_binding
    supersession = fixture.accepted_supersession_binding
    assert tuple(
        key
        for key, _ in acp.accepted_revocation_binding_material_v01(
            revocation
        )
    ) == (
        "revocation_candidate_id",
        "revocation_root_decision_id",
        "revocation_root_decision_hash",
        "owning_local_root_id",
        "packet_id",
        "prior_authorization_decision_id",
    )
    assert tuple(
        key
        for key, _ in acp.accepted_supersession_binding_material_v01(
            supersession
        )
    ) == (
        "supersession_candidate_id",
        "supersession_root_decision_id",
        "supersession_root_decision_hash",
        "owning_local_root_id",
        "predecessor_packet_id",
        "prior_authorization_decision_id",
    )
    assert acp.validate_accepted_revocation_binding_v01(revocation) == (
        True,
        (),
    )
    assert acp.validate_accepted_supersession_binding_v01(supersession) == (
        True,
        (),
    )
    assert acp.validate_accepted_revocation_binding_v01(
        replace(
            revocation,
            accepted_revocation_binding_id=_AlwaysEqualStr(
                revocation.accepted_revocation_binding_id
            ),
        )
    )[0] is False
    assert acp.validate_accepted_supersession_binding_v01(
        replace(
            supersession,
            accepted_supersession_binding_id=_AlwaysEqualStr(
                supersession.accepted_supersession_binding_id
            ),
        )
    )[0] is False
    revocation_mutations = (
        ("revocation_candidate_id", "revocation_candidate_v01:" + "0" * 64),
        ("revocation_root_decision_id", "0" * 64),
        ("revocation_root_decision_hash", "0" * 64),
        ("owning_local_root_id", "root:foreign"),
        ("packet_id", "acp_v02:" + "0" * 64),
        ("prior_authorization_decision_id", "0" * 64),
    )
    for field_name, field_value in revocation_mutations:
        assert acp.validate_accepted_revocation_binding_v01(
            replace(revocation, **{field_name: field_value})
        )[0] is False
    supersession_mutations = (
        (
            "supersession_candidate_id",
            "supersession_candidate_v01:" + "0" * 64,
        ),
        ("supersession_root_decision_id", "0" * 64),
        ("supersession_root_decision_hash", "0" * 64),
        ("owning_local_root_id", "root:foreign"),
        ("predecessor_packet_id", "acp_v02:" + "0" * 64),
        ("prior_authorization_decision_id", "0" * 64),
    )
    for field_name, field_value in supersession_mutations:
        assert acp.validate_accepted_supersession_binding_v01(
            replace(supersession, **{field_name: field_value})
        )[0] is False
    assert acp.validate_accepted_revocation_binding_v01(
        fixture.revocation_candidate
    )[0] is False
    assert acp.validate_accepted_supersession_binding_v01(
        fixture.supersession_candidate
    )[0] is False
    forged_candidate = _reidentify_revocation_candidate(
        fixture.revocation_candidate,
        revocation_reason_class="OTHER_REASON",
    )
    with pytest.raises(ValueError):
        acp.build_accepted_revocation_binding_v01(
            candidate=forged_candidate,
            root_projection=fixture.revocation_root_projection,
            packet=fixture.predecessor,
        )
    assert revocation.accepted_revocation_binding_id not in tuple(
        item
        for _, item in acp.revocation_candidate_material_v01(
            fixture.revocation_candidate
        )
    )
    assert supersession.accepted_supersession_binding_id not in tuple(
        item
        for _, item in acp.supersession_candidate_material_v01(
            fixture.supersession_candidate
        )
    )


def test_g2a3a_mandatory_dependency_acceptance_is_exact(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    fixture = g2a3a_fixture
    predecessor = fixture.predecessor
    assert acp.validate_mandatory_dependency_local_root_acceptance_v01(
        predecessor
    ) == (True, ())
    binding = predecessor.dependency_acceptance_binding
    canonical = predecessor.canonical_projection
    assert (
        binding.dependency_set_candidate_fingerprint,
        binding.root_packet_authorization_candidate_id,
        binding.source_root_decision_id,
        binding.source_root_decision_hash,
        binding.owning_local_root_id,
        binding.packet_id,
        binding.accepted_status,
    ) == (
        canonical.dependency_set_candidate_fingerprint,
        canonical.authorization_candidate
        .root_packet_authorization_candidate_id,
        predecessor.root_decision_projection.root_decision_result.decision_id,
        predecessor.root_decision_projection.source_root_decision_hash,
        canonical.owning_local_root_id,
        predecessor.packet_identity.packet_id,
        "ROOT_ACCEPTED_FOR_PACKET",
    )
    optional = _root_bound_from_canonical(
        _projection(
            dependency=_dependency(requirement_class="OPTIONAL"),
        )
    )
    valid, reasons = (
        acp.validate_mandatory_dependency_local_root_acceptance_v01(optional)
    )
    assert valid is False
    assert "mandatory_dependency_missing" in reasons
    with pytest.raises(ValueError, match="cross_profile_dependency_root_mismatch"):
        _projection(dependency=_dependency(root_id="root:foreign"))
    recursive_record = acp.build_dependency_set_candidate_record_v01(
        dependency_id="dependency:recursive",
        dependency_class="INVOICE_EVIDENCE",
        evidence_ref=(
            acp.PACKET_DEPENDENCY_ACCEPTANCE_PREFIX_V01 + "0" * 64
        ),
        content_sha256="8" * 64,
        requirement_class="MANDATORY",
        time_envelope_id="time_envelope:recursive",
        freshness_policy_id="freshness_policy:recursive",
        source_provenance_refs=("source:recursive",),
        expected_accepting_local_root_id=ROOT_ID,
    )
    recursive = _root_bound_from_canonical(
        _projection(
            dependency=acp.build_dependency_set_candidate_v01(
                dependency_records=(recursive_record,),
            )
        )
    )
    valid, reasons = (
        acp.validate_mandatory_dependency_local_root_acceptance_v01(
            recursive
        )
    )
    assert valid is False
    assert "mandatory_dependency_recursive_acceptance_binding" in reasons


@pytest.mark.parametrize(
    "invalidation_class",
    acp.ACTION_INVALIDATION_CLASSES_V01,
)
def test_g2a3a_invalidation_classes_validate_exact_context(
    g2a3a_fixture: _G2A3AFixtureV01,
    invalidation_class: str,
) -> None:
    fixture = g2a3a_fixture
    evidence = _g2a3a_invalidation(fixture, invalidation_class)
    assert [field.name for field in fields(
        acp.ActionInvalidationEvidenceV01
    )][-1] == "invalidation_evidence_id"
    assert len(acp.action_invalidation_evidence_material_v01(evidence)) == 20
    assert tuple(
        key
        for key, _ in acp.action_invalidation_evidence_material_v01(
            evidence
        )
    ) == (
        "profile_id",
        "source_invalidation_event_ref",
        "packet_id",
        "dependency_id",
        "invalidation_class",
        "evidence_ref",
        "evidence_sha256",
        "observed_status",
        "time_envelope_id",
        "freshness_policy_id",
        "owning_local_root_id",
        "accepted_by_local_root_id",
        "acceptance_root_decision_id",
        "acceptance_root_decision_hash",
        "validation_status",
        "authority_effect",
        "root_decision_ref",
        "evaluation_time",
        "evaluation_time_source",
        "evaluation_context_id",
    )
    assert evidence.invalidation_evidence_id == (
        G2A3A_INVALIDATION_IDS[invalidation_class]
    )
    assert ":" not in evidence.invalidation_evidence_id
    assert acp.validate_action_invalidation_evidence_v01(evidence) == (
        True,
        (),
    )
    kwargs: dict[str, object] = {}
    if invalidation_class == "ROOT_REVOCATION":
        kwargs["revocation_candidate"] = fixture.revocation_candidate
        kwargs["revocation_root_projection"] = (
            fixture.revocation_root_projection
        )
        kwargs["accepted_revocation_binding"] = (
            fixture.accepted_revocation_binding
        )
    if invalidation_class == "ROOT_SUPERSESSION":
        kwargs["supersession_candidate"] = fixture.supersession_candidate
        kwargs["supersession_root_projection"] = (
            fixture.supersession_root_projection
        )
        kwargs["supersession_successor"] = fixture.successor
        kwargs["accepted_supersession_binding"] = (
            fixture.accepted_supersession_binding
        )
    assert acp.validate_action_invalidation_evidence_against_packet_v01(
        evidence,
        fixture.predecessor,
        **kwargs,
    ) == (True, ())


def test_g2a3a_invalidation_adversarial_bindings_fail_closed(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    fixture = g2a3a_fixture
    dependency = _g2a3a_invalidation(fixture, "DEPENDENCY_STALE")
    kill_switch = _g2a3a_invalidation(
        fixture,
        "ROOT_BOUND_KILL_SWITCH",
    )
    revocation = _g2a3a_invalidation(fixture, "ROOT_REVOCATION")
    supersession = _g2a3a_invalidation(fixture, "ROOT_SUPERSESSION")
    for forged in (
        _reidentify_invalidation(
            dependency,
            packet_id="acp_v02:" + "0" * 64,
        ),
        _reidentify_invalidation(
            dependency,
            accepted_by_local_root_id="root:foreign",
        ),
        _reidentify_invalidation(
            dependency,
            time_envelope_id="time_envelope:foreign",
        ),
        _reidentify_invalidation(
            dependency,
            freshness_policy_id="freshness_policy:foreign",
        ),
        _reidentify_invalidation(
            kill_switch,
            dependency_id="kill_switch:foreign",
        ),
    ):
        assert acp.validate_action_invalidation_evidence_v01(forged) == (
            True,
            (),
        )
        assert acp.validate_action_invalidation_evidence_against_packet_v01(
            forged,
            fixture.predecessor,
        )[0] is False
    manual = _reidentify_invalidation(
        _g2a3a_invalidation(fixture, "MANUAL_CANCEL_EVIDENCE"),
        dependency_id="manual_cancel:not_policy_bound",
    )
    assert acp.validate_action_invalidation_evidence_against_packet_v01(
        manual,
        fixture.predecessor,
    )[0] is False
    assert acp.validate_action_invalidation_evidence_against_packet_v01(
        revocation,
        fixture.predecessor,
    )[0] is False
    assert acp.validate_action_invalidation_evidence_against_packet_v01(
        supersession,
        fixture.predecessor,
    )[0] is False
    forged_digest = _reidentify_invalidation(
        revocation,
        evidence_sha256="0" * 64,
    )
    assert acp.validate_action_invalidation_evidence_against_packet_v01(
        forged_digest,
        fixture.predecessor,
        revocation_candidate=fixture.revocation_candidate,
        revocation_root_projection=fixture.revocation_root_projection,
        accepted_revocation_binding=fixture.accepted_revocation_binding,
    )[0] is False
    foreign_revocation_binding = _reidentify_accepted_revocation(
        fixture.accepted_revocation_binding,
        owning_local_root_id="root:foreign",
    )
    assert acp.validate_accepted_revocation_binding_v01(
        foreign_revocation_binding
    ) == (True, ())
    assert acp.validate_action_invalidation_evidence_against_packet_v01(
        revocation,
        fixture.predecessor,
        revocation_candidate=fixture.revocation_candidate,
        revocation_root_projection=fixture.revocation_root_projection,
        accepted_revocation_binding=foreign_revocation_binding,
    )[0] is False
    foreign_supersession_binding = _reidentify_accepted_supersession(
        fixture.accepted_supersession_binding,
        owning_local_root_id="root:foreign",
    )
    assert acp.validate_accepted_supersession_binding_v01(
        foreign_supersession_binding
    ) == (True, ())
    assert acp.validate_action_invalidation_evidence_against_packet_v01(
        supersession,
        fixture.predecessor,
        supersession_candidate=fixture.supersession_candidate,
        supersession_root_projection=fixture.supersession_root_projection,
        supersession_successor=fixture.successor,
        accepted_supersession_binding=foreign_supersession_binding,
    )[0] is False
    assert acp.validate_action_invalidation_evidence_v01(
        replace(
            dependency,
            invalidation_evidence_id=_AlwaysEqualStr(
                dependency.invalidation_evidence_id
            ),
        )
    )[0] is False
    assert acp.validate_action_invalidation_evidence_v01(
        replace(dependency, invalidation_evidence_id="0" * 64)
    )[0] is False
    assert acp.validate_action_invalidation_evidence_v01(
        replace(dependency, authority_effect="ROOT_REVOCATION")
    )[0] is False
    assert acp.validate_action_invalidation_evidence_v01(
        replace(
            dependency,
            source_invalidation_event_ref=(
                dependency.invalidation_evidence_id
            ),
        )
    )[0] is False
    with pytest.raises(ValueError):
        acp.build_action_invalidation_evidence_v01(
            source_invalidation_event_ref="source_invalidation:partial_root",
            packet_id=fixture.predecessor.packet_identity.packet_id,
            dependency_id="dependency:partial_root",
            invalidation_class="ROOT_REVOCATION",
            evidence_ref="evidence:partial_root",
            evidence_sha256="0" * 64,
            observed_status="OBSERVED_ROOT_REVOCATION",
            time_envelope_id="time_envelope:partial_root",
            freshness_policy_id="freshness_policy:partial_root",
            owning_local_root_id=ROOT_ID,
            accepted_by_local_root_id=ROOT_ID,
            acceptance_root_decision_id=G2A3A_REVOCATION_DECISION_ID,
            acceptance_root_decision_hash=None,
            authority_effect="ROOT_REVOCATION",
            root_decision_ref=G2A3A_REVOCATION_DECISION_ID,
            evaluation_time=EVALUATION_TIME,
            evaluation_time_source=EVALUATION_TIME_SOURCE,
            evaluation_context_id="evaluation_context:partial_root",
        )


@pytest.mark.parametrize(
    "variation",
    ("TTL", "ADAPTER", "DEPENDENCY", "POLICY"),
)
def test_g2a3a_pure_renewal_variants_preserve_logical_effect(
    root_bound_fixture: _RootBoundFixtureV01,
    variation: str,
) -> None:
    predecessor = root_bound_fixture.root_bound_projection
    successor = _g2a3a_successor(predecessor, variation=variation)
    candidate, root_projection, binding = _g2a3a_supersession_bundle(
        predecessor,
        successor,
    )
    assert acp.validate_action_packet_renewal_relationship_v01(
        predecessor,
        successor,
        candidate,
        binding,
        root_projection=root_projection,
    ) == (True, ())
    assert predecessor.packet_identity.packet_id != (
        successor.packet_identity.packet_id
    )
    assert (
        predecessor.canonical_projection.logical_intent.root_owned_intent_id
        == successor.canonical_projection.logical_intent.root_owned_intent_id
    )
    assert (
        predecessor.canonical_projection.idempotency_identity.idempotency_key
        == successor.canonical_projection.idempotency_identity.idempotency_key
    )


def test_g2a3a_renewal_rejects_wrong_reason_binding_and_foreign_root(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    fixture = g2a3a_fixture
    wrong_reason = _reidentify_supersession_candidate(
        fixture.supersession_candidate,
        supersession_reason_class="REPLACEMENT",
    )
    assert acp.validate_action_packet_renewal_relationship_v01(
        fixture.predecessor,
        fixture.successor,
        wrong_reason,
        fixture.accepted_supersession_binding,
    )[0] is False
    other_successor = _g2a3a_successor(
        fixture.predecessor,
        variation="DEPENDENCY",
    )
    assert acp.validate_action_packet_renewal_relationship_v01(
        fixture.predecessor,
        other_successor,
        fixture.supersession_candidate,
        fixture.accepted_supersession_binding,
    )[0] is False
    foreign_candidate = _reidentify_supersession_candidate(
        fixture.supersession_candidate,
        owning_local_root_id="root:foreign",
    )
    assert acp.validate_action_packet_renewal_relationship_v01(
        fixture.predecessor,
        fixture.successor,
        foreign_candidate,
        fixture.accepted_supersession_binding,
    )[0] is False


def test_g2a3a_root_context_rejects_prior_transaction_and_root_drift(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    fixture = g2a3a_fixture
    candidate = fixture.revocation_candidate
    variants = (
        {
            "transaction_id": "transaction:foreign",
            "target_root_id": None,
            "state_updates": _g2a3a_prior_state(fixture),
        },
        {
            "transaction_id": None,
            "target_root_id": "root:foreign",
            "state_updates": _g2a3a_prior_state(fixture),
        },
        {
            "transaction_id": None,
            "target_root_id": None,
            "state_updates": {
                "prior_root_state": {
                    "prior_decision_id": "0" * 64,
                    "prior_decision": "ACCEPT",
                    "prior_selected_candidate_id": (
                        fixture.predecessor.canonical_projection
                        .authorization_candidate
                        .root_packet_authorization_candidate_id
                    ),
                },
            },
        },
    )
    for variant in variants:
        _, _, kernel, decision_input, result = _build_frozen_root_evidence(
            fixture.predecessor.canonical_projection,
            candidate_id=candidate.revocation_candidate_id,
            candidate_kind="REVOCATION",
            transaction_id=variant["transaction_id"],  # type: ignore[arg-type]
            target_root_id=variant["target_root_id"],  # type: ignore[arg-type]
            state_updates=variant["state_updates"],  # type: ignore[arg-type]
        )
        projection = acp.build_root_decision_candidate_projection_v01(
            candidate_kind="REVOCATION",
            projected_candidate_id=candidate.revocation_candidate_id,
            root_decision_kernel=kernel,
            root_decision_input=decision_input,
            root_decision_result=result,
        )
        assert acp.validate_revocation_root_context_coherence_v01(
            candidate,
            projection,
            fixture.predecessor,
        )[0] is False


def test_g2a3a_objects_do_not_enable_live_authority_mutation(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    fixture = g2a3a_fixture
    predecessor = fixture.predecessor
    packet_id = predecessor.packet_identity.packet_id
    registry = _g2a2b_recorded_genesis(predecessor)
    registry, _, _ = _g2a2b_activate(registry, packet_id)
    entry = _g2a2_final_entry(registry, packet_id)
    rule_id = "g2a_t16_authorized_revoke"
    event = acp.build_action_packet_transition_event_v01(
        action_packet_transition_registry_profile=_g2a2a_registry(),
        transition_rule_id=rule_id,
        packet_id=packet_id,
        idempotency_key=(
            predecessor.canonical_projection.idempotency_identity
            .idempotency_key
        ),
        previous_transition_event_id=(
            entry.transition_events[-1].transition_event_id
        ),
        owning_local_root_id=ROOT_ID,
        root_decision_ref=(
            fixture.accepted_revocation_binding.revocation_root_decision_id
        ),
        transition_evidence_bindings=_g2a2a_bindings(rule_id),
        dependency_set_candidate_fingerprint=(
            predecessor.canonical_projection
            .dependency_set_candidate_fingerprint
        ),
        temporal_authority_fingerprint=(
            predecessor.canonical_projection.temporal_authority_fingerprint
        ),
        evaluation_time=EVALUATION_TIME,
        evaluation_time_source=EVALUATION_TIME_SOURCE,
        evaluation_context_id="evaluation_context:g2a3a:live_boundary",
        execution_attempt_identity=None,
        receipt_ref=None,
    )
    before = repr(registry).encode("utf-8")
    with pytest.raises(
        ValueError,
        match="^authority_transition_requires_g2a3_binding$",
    ):
        acp.append_action_packet_lifecycle_transition_v01(
            registry,
            packet_id=packet_id,
            transition_event=event,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )
    assert repr(registry).encode("utf-8") == before


def _g2a3a_invalidation_for_revocation_binding(
    fixture: _G2A3AFixtureV01,
    binding: acp.AcceptedRevocationBindingV01,
) -> acp.ActionInvalidationEvidenceV01:
    return _reidentify_invalidation(
        _g2a3a_invalidation(fixture, "ROOT_REVOCATION"),
        evidence_ref=binding.accepted_revocation_binding_id,
        evidence_sha256=(
            binding.accepted_revocation_binding_id.split(":", 1)[1]
        ),
        acceptance_root_decision_id=binding.revocation_root_decision_id,
        acceptance_root_decision_hash=binding.revocation_root_decision_hash,
        root_decision_ref=binding.revocation_root_decision_id,
    )


def _g2a3a_invalidation_for_supersession_binding(
    fixture: _G2A3AFixtureV01,
    binding: acp.AcceptedSupersessionBindingV01,
) -> acp.ActionInvalidationEvidenceV01:
    return _reidentify_invalidation(
        _g2a3a_invalidation(fixture, "ROOT_SUPERSESSION"),
        evidence_ref=binding.accepted_supersession_binding_id,
        evidence_sha256=(
            binding.accepted_supersession_binding_id.split(":", 1)[1]
        ),
        acceptance_root_decision_id=binding.supersession_root_decision_id,
        acceptance_root_decision_hash=(
            binding.supersession_root_decision_hash
        ),
        root_decision_ref=binding.supersession_root_decision_id,
    )


def test_g2a3a_same_root_reidentified_revocation_binding_is_non_authority(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    fixture = g2a3a_fixture
    source_snapshot = repr(fixture).encode("utf-8")
    forged_bindings = (
        _reidentify_accepted_revocation(
            fixture.accepted_revocation_binding,
            revocation_candidate_id=(
                acp.REVOCATION_CANDIDATE_PREFIX_V01 + "0" * 64
            ),
            revocation_root_decision_id="1" * 64,
            revocation_root_decision_hash="2" * 64,
        ),
        _reidentify_accepted_revocation(
            fixture.accepted_revocation_binding,
            revocation_root_decision_id="3" * 64,
            revocation_root_decision_hash="4" * 64,
        ),
    )
    for binding in forged_bindings:
        assert acp.validate_accepted_revocation_binding_v01(binding) == (
            True,
            (),
        )
        assert acp._validate_accepted_revocation_binding_against_context_v01(
            binding,
            fixture.revocation_candidate,
            fixture.revocation_root_projection,
            fixture.predecessor,
        ) == (False, ("accepted_revocation_binding_context_invalid",))
        evidence = _g2a3a_invalidation_for_revocation_binding(
            fixture,
            binding,
        )
        assert acp.validate_action_invalidation_evidence_v01(evidence) == (
            True,
            (),
        )
        assert acp.validate_action_invalidation_evidence_against_packet_v01(
            evidence,
            fixture.predecessor,
            revocation_candidate=fixture.revocation_candidate,
            revocation_root_projection=(
                fixture.revocation_root_projection
            ),
            accepted_revocation_binding=binding,
        )[0] is False
    assert acp._validate_accepted_revocation_binding_against_context_v01(
        fixture.accepted_revocation_binding,
        fixture.revocation_candidate,
        fixture.revocation_root_projection,
        fixture.predecessor,
    ) == (True, ())
    assert acp.validate_action_invalidation_evidence_against_packet_v01(
        _g2a3a_invalidation(fixture, "ROOT_REVOCATION"),
        fixture.predecessor,
        revocation_candidate=fixture.revocation_candidate,
        revocation_root_projection=fixture.revocation_root_projection,
        accepted_revocation_binding=fixture.accepted_revocation_binding,
    ) == (True, ())
    assert repr(fixture).encode("utf-8") == source_snapshot


def test_g2a3a_same_root_reidentified_supersession_binding_is_non_authority(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    fixture = g2a3a_fixture
    source_snapshot = repr(fixture).encode("utf-8")
    forged_bindings = (
        _reidentify_accepted_supersession(
            fixture.accepted_supersession_binding,
            supersession_candidate_id=(
                acp.SUPERSESSION_CANDIDATE_PREFIX_V01 + "0" * 64
            ),
            supersession_root_decision_id="5" * 64,
            supersession_root_decision_hash="6" * 64,
        ),
        _reidentify_accepted_supersession(
            fixture.accepted_supersession_binding,
            supersession_root_decision_id="7" * 64,
            supersession_root_decision_hash="8" * 64,
        ),
    )
    for binding in forged_bindings:
        assert acp.validate_accepted_supersession_binding_v01(binding) == (
            True,
            (),
        )
        assert (
            acp._validate_accepted_supersession_binding_against_context_v01(
                binding,
                fixture.supersession_candidate,
                fixture.supersession_root_projection,
                fixture.predecessor,
                fixture.successor,
            )
            == (
                False,
                ("accepted_supersession_binding_context_invalid",),
            )
        )
        assert acp.validate_action_packet_renewal_relationship_v01(
            fixture.predecessor,
            fixture.successor,
            fixture.supersession_candidate,
            binding,
            root_projection=fixture.supersession_root_projection,
        )[0] is False
        evidence = _g2a3a_invalidation_for_supersession_binding(
            fixture,
            binding,
        )
        assert acp.validate_action_invalidation_evidence_v01(evidence) == (
            True,
            (),
        )
        assert acp.validate_action_invalidation_evidence_against_packet_v01(
            evidence,
            fixture.predecessor,
            supersession_candidate=fixture.supersession_candidate,
            supersession_root_projection=(
                fixture.supersession_root_projection
            ),
            supersession_successor=fixture.successor,
            accepted_supersession_binding=binding,
        )[0] is False
    assert (
        acp._validate_accepted_supersession_binding_against_context_v01(
            fixture.accepted_supersession_binding,
            fixture.supersession_candidate,
            fixture.supersession_root_projection,
            fixture.predecessor,
            fixture.successor,
        )
        == (True, ())
    )
    assert repr(fixture).encode("utf-8") == source_snapshot


def test_g2a3a_root_invalidation_requires_every_provenance_component(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    fixture = g2a3a_fixture
    revocation = _g2a3a_invalidation(fixture, "ROOT_REVOCATION")
    revocation_context = {
        "revocation_candidate": fixture.revocation_candidate,
        "revocation_root_projection": fixture.revocation_root_projection,
        "accepted_revocation_binding": fixture.accepted_revocation_binding,
    }
    for missing in tuple(revocation_context):
        context = dict(revocation_context)
        context[missing] = None
        assert acp.validate_action_invalidation_evidence_against_packet_v01(
            revocation,
            fixture.predecessor,
            **context,
        )[0] is False
    assert acp.validate_action_invalidation_evidence_against_packet_v01(
        revocation,
        fixture.predecessor,
        revocation_candidate=fixture.revocation_candidate,
        revocation_root_projection=fixture.supersession_root_projection,
        accepted_revocation_binding=fixture.accepted_revocation_binding,
    )[0] is False
    candidate_from_another_packet = _reidentify_revocation_candidate(
        fixture.revocation_candidate,
        packet_id=acp.ACTION_COMMIT_PACKET_ID_PREFIX_V01 + "9" * 64,
    )
    assert acp.validate_action_invalidation_evidence_against_packet_v01(
        revocation,
        fixture.predecessor,
        revocation_candidate=candidate_from_another_packet,
        revocation_root_projection=fixture.revocation_root_projection,
        accepted_revocation_binding=fixture.accepted_revocation_binding,
    )[0] is False

    supersession = _g2a3a_invalidation(fixture, "ROOT_SUPERSESSION")
    supersession_context = {
        "supersession_candidate": fixture.supersession_candidate,
        "supersession_root_projection": (
            fixture.supersession_root_projection
        ),
        "supersession_successor": fixture.successor,
        "accepted_supersession_binding": (
            fixture.accepted_supersession_binding
        ),
    }
    for missing in tuple(supersession_context):
        context = dict(supersession_context)
        context[missing] = None
        assert acp.validate_action_invalidation_evidence_against_packet_v01(
            supersession,
            fixture.predecessor,
            **context,
        )[0] is False
    assert acp.validate_action_invalidation_evidence_against_packet_v01(
        supersession,
        fixture.predecessor,
        supersession_candidate=fixture.supersession_candidate,
        supersession_root_projection=fixture.revocation_root_projection,
        supersession_successor=fixture.successor,
        accepted_supersession_binding=fixture.accepted_supersession_binding,
    )[0] is False
    successor_from_another_candidate = _g2a3a_successor(
        fixture.predecessor,
        variation="DEPENDENCY",
    )
    assert acp.validate_action_invalidation_evidence_against_packet_v01(
        supersession,
        fixture.predecessor,
        supersession_candidate=fixture.supersession_candidate,
        supersession_root_projection=fixture.supersession_root_projection,
        supersession_successor=successor_from_another_candidate,
        accepted_supersession_binding=fixture.accepted_supersession_binding,
    )[0] is False
    assert acp.validate_action_packet_renewal_relationship_v01(
        fixture.predecessor,
        fixture.successor,
        fixture.supersession_candidate,
        fixture.accepted_supersession_binding,
    ) == (False, ("renewal_root_projection_required",))


def test_g2a3a_same_effect_nonrenewal_supersession_geometry(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    fixture = g2a3a_fixture
    predecessor = fixture.predecessor
    predecessor_snapshot = repr(predecessor).encode("utf-8")
    successor = _g2a3a_successor(
        predecessor,
        variation="TTL",
        supersession_reason_class="SAME_EFFECT_REPLACEMENT",
    )
    successor_snapshot = repr(successor).encode("utf-8")
    candidate, root_projection, binding = _g2a3a_supersession_bundle(
        predecessor,
        successor,
    )
    assert (
        acp.validate_supplier_root_bound_action_commit_packet_v02_projection_v01(
            successor
        )
        == (True, ())
    )
    assert acp.validate_supersession_candidate_against_packets_v01(
        candidate,
        predecessor,
        successor,
    ) == (True, ())
    assert acp.validate_supersession_root_context_coherence_v01(
        candidate,
        root_projection,
        predecessor,
        successor,
    ) == (True, ())
    assert (
        acp._validate_accepted_supersession_binding_against_context_v01(
            binding,
            candidate,
            root_projection,
            predecessor,
            successor,
        )
        == (True, ())
    )
    assert acp.validate_action_packet_renewal_relationship_v01(
        predecessor,
        successor,
        candidate,
        binding,
        root_projection=root_projection,
    )[0] is False
    assert (
        predecessor.canonical_projection.logical_intent.root_owned_intent_id
        == successor.canonical_projection.logical_intent.root_owned_intent_id
    )
    assert (
        predecessor.canonical_projection.idempotency_identity.idempotency_key
        == successor.canonical_projection.idempotency_identity.idempotency_key
    )
    assert {
        "successor_authorization_candidate_id": (
            successor.canonical_projection.authorization_candidate
            .root_packet_authorization_candidate_id
        ),
        "successor_packet_id": successor.packet_identity.packet_id,
        "successor_source_decision_id": (
            successor.root_decision_projection.root_decision_result.decision_id
        ),
        "supersession_candidate_id": candidate.supersession_candidate_id,
        "supersession_root_decision_id": (
            root_projection.root_decision_result.decision_id
        ),
        "supersession_root_decision_hash": (
            root_projection.source_root_decision_hash
        ),
        "accepted_supersession_binding_id": (
            binding.accepted_supersession_binding_id
        ),
    } == G2A3A_SAME_EFFECT_NONRENEWAL_VECTOR
    assert repr(predecessor).encode("utf-8") == predecessor_snapshot
    assert repr(successor).encode("utf-8") == successor_snapshot


def test_g2a3a_material_effect_supersession_geometry(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    fixture = g2a3a_fixture
    predecessor = fixture.predecessor
    predecessor_snapshot = repr(predecessor).encode("utf-8")
    successor = _g2a3a_successor(
        predecessor,
        variation="MATERIAL",
        supersession_reason_class="MATERIAL_EFFECT_REPLACEMENT",
    )
    successor_snapshot = repr(successor).encode("utf-8")
    candidate, root_projection, binding = _g2a3a_supersession_bundle(
        predecessor,
        successor,
    )
    assert acp.validate_supersession_candidate_against_packets_v01(
        candidate,
        predecessor,
        successor,
    ) == (True, ())
    assert acp.validate_supersession_root_context_coherence_v01(
        candidate,
        root_projection,
        predecessor,
        successor,
    ) == (True, ())
    assert (
        acp._validate_accepted_supersession_binding_against_context_v01(
            binding,
            candidate,
            root_projection,
            predecessor,
            successor,
        )
        == (True, ())
    )
    assert acp.validate_action_packet_renewal_relationship_v01(
        predecessor,
        successor,
        candidate,
        binding,
        root_projection=root_projection,
    )[0] is False
    assert (
        predecessor.canonical_projection.logical_intent.root_owned_intent_id
        != successor.canonical_projection.logical_intent.root_owned_intent_id
    )
    assert (
        predecessor.canonical_projection.idempotency_identity.idempotency_key
        != successor.canonical_projection.idempotency_identity.idempotency_key
    )
    assert {
        "successor_stable_intent_id": (
            successor.canonical_projection.logical_intent.root_owned_intent_id
        ),
        "successor_idempotency_key": (
            successor.canonical_projection.idempotency_identity.idempotency_key
        ),
        "successor_authorization_candidate_id": (
            successor.canonical_projection.authorization_candidate
            .root_packet_authorization_candidate_id
        ),
        "successor_packet_id": successor.packet_identity.packet_id,
        "successor_source_decision_id": (
            successor.root_decision_projection.root_decision_result.decision_id
        ),
        "supersession_candidate_id": candidate.supersession_candidate_id,
        "supersession_root_decision_id": (
            root_projection.root_decision_result.decision_id
        ),
        "supersession_root_decision_hash": (
            root_projection.source_root_decision_hash
        ),
        "accepted_supersession_binding_id": (
            binding.accepted_supersession_binding_id
        ),
    } == G2A3A_MATERIAL_EFFECT_SUPERSESSION_VECTOR
    assert repr(predecessor).encode("utf-8") == predecessor_snapshot
    assert repr(successor).encode("utf-8") == successor_snapshot


def test_g2a3a_material_successor_only_genesis_cannot_activate_initial_path(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    predecessor = g2a3a_fixture.predecessor
    successor = _g2a3a_successor(
        predecessor,
        variation="MATERIAL",
        supersession_reason_class="MATERIAL_EFFECT_REPLACEMENT",
    )
    packet_id = successor.packet_identity.packet_id
    registry = _g2a2b_recorded_genesis(successor)
    state = acp.derive_action_packet_lifecycle_state_v01(
        registry,
        packet_id=packet_id,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    assert (
        state.lifecycle_state,
        state.idempotency_disposition,
        state.reservation_owner_packet_id,
        state.executable,
    ) == ("CREATED", "UNCLAIMED", None, False)
    before = repr(registry).encode("utf-8")
    event, reserve = _g2a2b_activation_pair(registry, packet_id)
    with pytest.raises(
        ValueError,
        match="^authority_transition_requires_g2a3_binding$",
    ):
        acp.activate_action_packet_lifecycle_v01(
            registry,
            packet_id=packet_id,
            transition_event=event,
            disposition_event=reserve,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )
    assert repr(registry).encode("utf-8") == before
    assert registry.action_packet_lifecycle_entries[0].transition_events == ()
    assert registry.idempotency_disposition_events == ()
    assert registry.real_world_effects_count == 0


def test_g2a3a_material_successor_with_predecessor_cannot_activate_initial_path(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    predecessor = g2a3a_fixture.predecessor
    successor = _g2a3a_successor(
        predecessor,
        variation="MATERIAL",
        supersession_reason_class="MATERIAL_EFFECT_REPLACEMENT",
    )
    registry = acp.build_empty_action_commit_packet_registry_v02()
    for root_bound in (predecessor, successor):
        registry = acp.record_action_packet_genesis_v01(
            registry,
            root_bound_genesis=root_bound,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )
    assert (
        predecessor.canonical_projection.idempotency_identity.idempotency_key
        != successor.canonical_projection.idempotency_identity.idempotency_key
    )
    before = repr(registry).encode("utf-8")
    event, reserve = _g2a2b_activation_pair(
        registry,
        successor.packet_identity.packet_id,
    )
    with pytest.raises(
        ValueError,
        match="^authority_transition_requires_g2a3_binding$",
    ):
        acp.activate_action_packet_lifecycle_v01(
            registry,
            packet_id=successor.packet_identity.packet_id,
            transition_event=event,
            disposition_event=reserve,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )
    assert repr(registry).encode("utf-8") == before
    assert registry.idempotency_disposition_events == ()
    for root_bound in (predecessor, successor):
        state = acp.derive_action_packet_lifecycle_state_v01(
            registry,
            packet_id=root_bound.packet_identity.packet_id,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )
        assert (
            state.lifecycle_state,
            state.idempotency_disposition,
            state.reservation_owner_packet_id,
        ) == ("CREATED", "UNCLAIMED", None)
    assert registry.real_world_effects_count == 0


def test_g2a3a_same_effect_successor_only_cannot_activate_initial_path(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    predecessor = g2a3a_fixture.predecessor
    successor = _g2a3a_successor(
        predecessor,
        variation="TTL",
        supersession_reason_class="SAME_EFFECT_REPLACEMENT",
    )
    assert (
        predecessor.canonical_projection.idempotency_identity.idempotency_key
        == successor.canonical_projection.idempotency_identity.idempotency_key
    )
    registry = _g2a2b_recorded_genesis(successor)
    before = repr(registry).encode("utf-8")
    event, reserve = _g2a2b_activation_pair(
        registry,
        successor.packet_identity.packet_id,
    )
    with pytest.raises(
        ValueError,
        match="^authority_transition_requires_g2a3_binding$",
    ):
        acp.activate_action_packet_lifecycle_v01(
            registry,
            packet_id=successor.packet_identity.packet_id,
            transition_event=event,
            disposition_event=reserve,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )
    assert repr(registry).encode("utf-8") == before
    assert registry.action_packet_lifecycle_entries[0].transition_events == ()
    assert registry.idempotency_disposition_events == ()


def test_g2a3a_predecessor_bound_manual_registry_bypass_fails_closed(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    successor = _g2a3a_successor(
        g2a3a_fixture.predecessor,
        variation="MATERIAL",
        supersession_reason_class="MATERIAL_EFFECT_REPLACEMENT",
    )
    registry = _g2a2b_recorded_genesis(successor)
    event, reserve = _g2a2b_activation_pair(
        registry,
        successor.packet_identity.packet_id,
    )
    assert acp.validate_action_packet_transition_event_v01(
        event,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    ) == (True, ())
    assert acp.validate_idempotency_disposition_event_v01(reserve) == (
        True,
        (),
    )
    entry = registry.action_packet_lifecycle_entries[0]
    forged = replace(
        registry,
        action_packet_lifecycle_entries=(
            replace(entry, transition_events=(event,)),
        ),
        idempotency_disposition_events=(reserve,),
    )
    valid, reasons = acp.validate_action_commit_packet_registry_v02(forged)
    assert valid is False
    assert "authority_transition_requires_g2a3_binding" in reasons


def test_g2a3a_initial_packet_ordinary_activation_positive_control(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    initial = g2a3a_fixture.predecessor
    candidate = initial.canonical_projection.authorization_candidate
    assert candidate.predecessor_packet_id is None
    assert candidate.supersession_reason_class is None
    registry = _g2a2b_recorded_genesis(initial)
    activated, _, _ = _g2a2b_activate(
        registry,
        initial.packet_identity.packet_id,
    )
    state = acp.derive_action_packet_lifecycle_state_v01(
        activated,
        packet_id=initial.packet_identity.packet_id,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    assert (
        state.lifecycle_state,
        state.idempotency_disposition,
        state.reservation_owner_packet_id,
        state.executable,
    ) == (
        "ROOT_AUTHORIZED",
        "RESERVED",
        initial.packet_identity.packet_id,
        False,
    )


G2A3B1_DETERMINISTIC_RULES = (
    "g2a_t06_created_block",
    "g2a_t07_authorized_block",
    "g2a_t08_queued_block",
    "g2a_t09_pending_block",
    "g2a_t10_failed_block",
)
G2A3B1_REVOCATION_RULES = (
    "g2a_t16_authorized_revoke",
    "g2a_t17_queued_revoke",
    "g2a_t18_pending_revoke",
    "g2a_t19_failed_revoke",
)


def _g2a3b1_registry_for_rule(
    root_bound: acp.SupplierRootBoundActionCommitPacketV02ProjectionV01,
    rule_id: str,
) -> acp.ActionCommitPacketRegistryV02:
    packet_id = root_bound.packet_identity.packet_id
    registry = _g2a2b_recorded_genesis(root_bound)
    if rule_id == "g2a_t06_created_block":
        return registry
    registry, _, _ = _g2a2b_activate(registry, packet_id)
    if rule_id in {
        "g2a_t07_authorized_block",
        "g2a_t16_authorized_revoke",
    }:
        return registry
    registry, _ = _g2a2b_append(registry, packet_id, "g2a_t02_queue")
    if rule_id in {
        "g2a_t08_queued_block",
        "g2a_t17_queued_revoke",
    }:
        return registry
    registry, _ = _g2a2b_append(
        registry,
        packet_id,
        "g2a_t03_pending",
        evaluation_context_id="evaluation_context:g2a3b1:attempt:1",
    )
    if rule_id in {
        "g2a_t09_pending_block",
        "g2a_t18_pending_revoke",
    }:
        return registry
    entry = next(
        item
        for item in registry.action_packet_lifecycle_entries
        if item.root_bound_genesis.packet_identity.packet_id == packet_id
    )
    state = acp.derive_action_packet_lifecycle_state_v01(
        registry,
        packet_id=packet_id,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    failure = _g2a2b_event(
        entry,
        "g2a_t24_nonconsuming_failure",
        latest_disposition_event_id=state.latest_disposition_event_id,
    )
    return acp.record_action_packet_nonconsuming_outcome_v01(
        registry,
        packet_id=packet_id,
        transition_event=failure,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )


def _g2a3b1_transition_event(
    registry: acp.ActionCommitPacketRegistryV02,
    packet_id: str,
    rule_id: str,
    invalidation: acp.ActionInvalidationEvidenceV01,
    *,
    accepted_revocation_binding: (
        acp.AcceptedRevocationBindingV01 | None
    ) = None,
) -> acp.ActionPacketTransitionEventV01:
    transition_registry_profile = _g2a2a_registry()
    rule = (
        transition_registry.lookup_action_packet_transition_rule_v01(
            registry=transition_registry_profile,
            transition_rule_id=rule_id,
        )
    )
    entry = next(
        item
        for item in registry.action_packet_lifecycle_entries
        if item.root_bound_genesis.packet_identity.packet_id == packet_id
    )
    genesis = entry.root_bound_genesis
    canonical = genesis.canonical_projection
    state = acp.derive_action_packet_lifecycle_state_v01(
        registry,
        packet_id=packet_id,
        action_packet_transition_registry_profile=(
            transition_registry_profile
        ),
    )
    latest = entry.transition_events[-1] if entry.transition_events else None

    def material(evidence_code: str) -> tuple[str, str, str]:
        if evidence_code in {
            "blocking_evidence_valid",
            "immediate_eligibility_failure_valid",
            "retry_ineligibility_evidence_valid",
        }:
            return (
                invalidation.invalidation_evidence_id,
                invalidation.invalidation_evidence_id,
                acp.ACTION_INVALIDATION_EVIDENCE_PROFILE_ID_V01,
            )
        if evidence_code == "packet_genesis_valid":
            return (
                packet_id,
                packet_id[len(acp.ACTION_COMMIT_PACKET_ID_PREFIX_V01) :],
                acp._ACTION_COMMIT_PACKET_IDENTITY_PROFILE_ID_V01,
            )
        if evidence_code == "authority_policy_valid":
            fingerprint = canonical.authority_policy_fingerprint
            return (
                fingerprint,
                fingerprint,
                acp.ACTION_AUTHORITY_POLICY_PROFILE_ID_V01,
            )
        if evidence_code == "idempotency_reservation_owned":
            latest_disposition_id = state.latest_disposition_event_id
            assert latest_disposition_id is not None
            return (
                latest_disposition_id,
                latest_disposition_id[
                    len(acp.IDEMPOTENCY_DISPOSITION_EVENT_PREFIX_V01) :
                ],
                acp.IDEMPOTENCY_DISPOSITION_EVENT_PROFILE_ID_V01,
            )
        if evidence_code == "adapter_not_called":
            assert latest is not None
            assert latest.execution_attempt_id is not None
            return (
                latest.execution_attempt_id,
                latest.execution_attempt_id[
                    len(acp.EXECUTION_ATTEMPT_IDENTITY_PREFIX_V01) :
                ],
                acp.EXECUTION_ATTEMPT_IDENTITY_PROFILE_ID_V01,
            )
        if evidence_code == "failed_non_consuming_provenance_valid":
            assert latest is not None
            return (
                latest.transition_event_id,
                latest.transition_event_id[
                    len(acp.ACTION_PACKET_TRANSITION_EVENT_PREFIX_V01) :
                ],
                acp.ACTION_PACKET_TRANSITION_EVENT_PROFILE_ID_V01,
            )
        if evidence_code == "accepted_revocation_binding_valid":
            assert accepted_revocation_binding is not None
            binding_id = (
                accepted_revocation_binding.accepted_revocation_binding_id
            )
            return (
                binding_id,
                binding_id[
                    len(acp.ACCEPTED_REVOCATION_BINDING_PREFIX_V01) :
                ],
                acp._ACCEPTED_REVOCATION_BINDING_VALIDATOR_PROFILE_ID_V01,
            )
        if evidence_code == "source_authorization_binding_valid":
            source_result = (
                genesis.root_decision_projection.root_decision_result
            )
            return (
                source_result.decision_id,
                genesis.root_decision_projection.source_root_decision_hash,
                acp._ROOT_DECISION_RESULT_VALIDATOR_PROFILE_ID_V01,
            )
        raise AssertionError(f"unsupported G2-A3B1 evidence: {evidence_code}")

    bindings = tuple(
        acp.build_transition_evidence_binding_v01(
            action_packet_transition_registry_profile=(
                transition_registry_profile
            ),
            transition_rule_id=rule_id,
            evidence_code=evidence_code,
            evidence_ref=material(evidence_code)[0],
            evidence_sha256=material(evidence_code)[1],
            validator_profile_id=material(evidence_code)[2],
        )
        for evidence_code in rule.required_evidence_codes
    )
    return acp.build_action_packet_transition_event_v01(
        action_packet_transition_registry_profile=transition_registry_profile,
        transition_rule_id=rule_id,
        packet_id=packet_id,
        idempotency_key=canonical.idempotency_identity.idempotency_key,
        previous_transition_event_id=(
            latest.transition_event_id if latest is not None else None
        ),
        owning_local_root_id=canonical.owning_local_root_id,
        root_decision_ref=(
            accepted_revocation_binding.revocation_root_decision_id
            if accepted_revocation_binding is not None
            else None
        ),
        transition_evidence_bindings=bindings,
        dependency_set_candidate_fingerprint=(
            canonical.dependency_set_candidate_fingerprint
        ),
        temporal_authority_fingerprint=(
            canonical.temporal_authority_fingerprint
        ),
        evaluation_time=invalidation.evaluation_time,
        evaluation_time_source=invalidation.evaluation_time_source,
        evaluation_context_id=invalidation.evaluation_context_id,
        execution_attempt_identity=None,
        receipt_ref=None,
    )


def _g2a3b1_rebind_transition(
    event: acp.ActionPacketTransitionEventV01,
    evidence_code: str,
    *,
    evidence_ref: str | None = None,
    evidence_sha256: str | None = None,
    validator_profile_id: str | None = None,
) -> acp.ActionPacketTransitionEventV01:
    bindings = tuple(
        (
            acp.build_transition_evidence_binding_v01(
                action_packet_transition_registry_profile=_g2a2a_registry(),
                transition_rule_id=event.transition_rule_id,
                evidence_code=binding.evidence_code,
                evidence_ref=(
                    binding.evidence_ref
                    if evidence_ref is None
                    else evidence_ref
                ),
                evidence_sha256=(
                    binding.evidence_sha256
                    if evidence_sha256 is None
                    else evidence_sha256
                ),
                validator_profile_id=(
                    binding.validator_profile_id
                    if validator_profile_id is None
                    else validator_profile_id
                ),
            )
            if binding.evidence_code == evidence_code
            else binding
        )
        for binding in event.transition_evidence_bindings
    )
    return _rebuild_transition_event(
        event,
        transition_evidence_bindings=bindings,
    )


@pytest.mark.parametrize(
    "rule_id",
    G2A3B1_DETERMINISTIC_RULES,
)
def test_g2a3b1_live_deterministic_block_is_atomic(
    g2a3a_fixture: _G2A3AFixtureV01,
    rule_id: str,
) -> None:
    root_bound = g2a3a_fixture.predecessor
    packet_id = root_bound.packet_identity.packet_id
    registry = _g2a3b1_registry_for_rule(root_bound, rule_id)
    invalidation = _g2a3a_invalidation(
        g2a3a_fixture,
        "ROOT_BOUND_KILL_SWITCH",
    )
    event = _g2a3b1_transition_event(
        registry,
        packet_id,
        rule_id,
        invalidation,
    )
    before = repr(registry).encode("utf-8")
    disposition_before = registry.idempotency_disposition_events
    state_before = acp.derive_action_packet_lifecycle_state_v01(
        registry,
        packet_id=packet_id,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    updated = acp.record_action_packet_deterministic_invalidation_v01(
        registry,
        packet_id=packet_id,
        invalidation_evidence=invalidation,
        transition_event=event,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    state = acp.derive_action_packet_lifecycle_state_v01(
        updated,
        packet_id=packet_id,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    assert state.lifecycle_state == "BLOCKED"
    assert state.executable is False
    assert (
        state.idempotency_disposition,
        state.reservation_owner_packet_id,
    ) == (
        state_before.idempotency_disposition,
        state_before.reservation_owner_packet_id,
    )
    assert updated.idempotency_disposition_events is disposition_before
    assert len(updated.action_packet_invalidation_contexts) == 1
    context = updated.action_packet_invalidation_contexts[0]
    assert type(context) is acp._ActionPacketInvalidationContextV01
    assert context.invalidation_evidence is invalidation
    assert context.revocation_candidate is None
    assert context.supersession_candidate is None
    assert acp.validate_action_commit_packet_registry_v02(updated) == (
        True,
        (),
    )
    assert repr(registry).encode("utf-8") == before
    assert updated.real_world_effects_count == 0


@pytest.mark.parametrize(
    "rule_id",
    G2A3B1_REVOCATION_RULES,
)
def test_g2a3b1_live_root_revocation_is_atomic(
    g2a3a_fixture: _G2A3AFixtureV01,
    rule_id: str,
) -> None:
    fixture = g2a3a_fixture
    root_bound = fixture.predecessor
    packet_id = root_bound.packet_identity.packet_id
    registry = _g2a3b1_registry_for_rule(root_bound, rule_id)
    invalidation = _g2a3a_invalidation(fixture, "ROOT_REVOCATION")
    event = _g2a3b1_transition_event(
        registry,
        packet_id,
        rule_id,
        invalidation,
        accepted_revocation_binding=fixture.accepted_revocation_binding,
    )
    before = repr(registry).encode("utf-8")
    disposition_before = registry.idempotency_disposition_events
    source_decision_id = (
        root_bound.root_decision_projection.root_decision_result.decision_id
    )
    updated = acp.record_action_packet_revocation_v01(
        registry,
        packet_id=packet_id,
        revocation_candidate=fixture.revocation_candidate,
        revocation_root_projection=fixture.revocation_root_projection,
        accepted_revocation_binding=fixture.accepted_revocation_binding,
        invalidation_evidence=invalidation,
        transition_event=event,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    state = acp.derive_action_packet_lifecycle_state_v01(
        updated,
        packet_id=packet_id,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    assert (
        state.lifecycle_state,
        state.idempotency_disposition,
        state.reservation_owner_packet_id,
        state.executable,
    ) == ("REVOKED", "RESERVED", packet_id, False)
    assert updated.idempotency_disposition_events is disposition_before
    assert len(updated.action_packet_invalidation_contexts) == 1
    context = updated.action_packet_invalidation_contexts[0]
    assert context.revocation_candidate is fixture.revocation_candidate
    assert (
        context.revocation_root_projection
        is fixture.revocation_root_projection
    )
    assert (
        context.accepted_revocation_binding
        is fixture.accepted_revocation_binding
    )
    assert (
        updated.action_packet_lifecycle_entries[0].root_bound_genesis
        .root_decision_projection.root_decision_result.decision_id
        == source_decision_id
    )
    assert acp.validate_action_commit_packet_registry_v02(updated) == (
        True,
        (),
    )
    assert repr(registry).encode("utf-8") == before
    assert updated.creates_permission is False
    assert updated.real_world_effects_count == 0


def test_g2a3b1_context_history_rejects_orphan_duplicate_partial_and_missing(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    fixture = g2a3a_fixture
    packet_id = fixture.predecessor.packet_identity.packet_id
    registry = _g2a3b1_registry_for_rule(
        fixture.predecessor,
        "g2a_t07_authorized_block",
    )
    invalidation = _g2a3a_invalidation(
        fixture,
        "ROOT_BOUND_KILL_SWITCH",
    )
    event = _g2a3b1_transition_event(
        registry,
        packet_id,
        "g2a_t07_authorized_block",
        invalidation,
    )
    updated = acp.record_action_packet_deterministic_invalidation_v01(
        registry,
        packet_id=packet_id,
        invalidation_evidence=invalidation,
        transition_event=event,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    context = updated.action_packet_invalidation_contexts[0]
    orphan = replace(
        registry,
        action_packet_invalidation_contexts=(context,),
    )
    valid, reasons = acp.validate_action_commit_packet_registry_v02(orphan)
    assert valid is False
    assert "action_packet_registry_invalidation_context_orphan" in reasons
    missing = replace(updated, action_packet_invalidation_contexts=())
    assert acp.validate_action_commit_packet_registry_v02(missing)[0] is False
    duplicate = replace(
        updated,
        action_packet_invalidation_contexts=(context, context),
    )
    valid, reasons = acp.validate_action_commit_packet_registry_v02(duplicate)
    assert valid is False
    assert "action_packet_registry_invalidation_context_duplicate" in reasons
    partial_context = replace(
        context,
        revocation_candidate=fixture.revocation_candidate,
    )
    partial = replace(
        orphan,
        action_packet_invalidation_contexts=(partial_context,),
    )
    valid, reasons = acp.validate_action_commit_packet_registry_v02(partial)
    assert valid is False
    assert "action_packet_registry_invalidation_context_invalid" in reasons
    assert acp.validate_action_commit_packet_registry_v02(
        replace(updated, action_packet_invalidation_contexts=[context])
    )[0] is False


@pytest.mark.parametrize(
    ("evidence_code", "change"),
    (
        ("blocking_evidence_valid", "ref"),
        ("authority_policy_valid", "profile"),
        ("idempotency_reservation_owned", "hash"),
    ),
)
def test_g2a3b1_deterministic_typed_binding_drift_fails_closed(
    g2a3a_fixture: _G2A3AFixtureV01,
    evidence_code: str,
    change: str,
) -> None:
    fixture = g2a3a_fixture
    packet_id = fixture.predecessor.packet_identity.packet_id
    registry = _g2a3b1_registry_for_rule(
        fixture.predecessor,
        "g2a_t07_authorized_block",
    )
    invalidation = _g2a3a_invalidation(
        fixture,
        "ROOT_BOUND_KILL_SWITCH",
    )
    event = _g2a3b1_transition_event(
        registry,
        packet_id,
        "g2a_t07_authorized_block",
        invalidation,
    )
    changes = {
        "evidence_ref": "f" * 64 if change == "ref" else None,
        "evidence_sha256": "e" * 64 if change == "hash" else None,
        "validator_profile_id": (
            "validator:foreign" if change == "profile" else None
        ),
    }
    forged = _g2a3b1_rebind_transition(
        event,
        evidence_code,
        **changes,
    )
    before = repr(registry).encode("utf-8")
    with pytest.raises(ValueError):
        acp.record_action_packet_deterministic_invalidation_v01(
            registry,
            packet_id=packet_id,
            invalidation_evidence=invalidation,
            transition_event=forged,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )
    assert repr(registry).encode("utf-8") == before
    assert registry.action_packet_invalidation_contexts == ()


@pytest.mark.parametrize(
    "rule_id",
    ("g2a_t09_pending_block", "g2a_t10_failed_block"),
)
def test_g2a3b1_attempt_and_failed_provenance_bindings_are_exact(
    g2a3a_fixture: _G2A3AFixtureV01,
    rule_id: str,
) -> None:
    fixture = g2a3a_fixture
    packet_id = fixture.predecessor.packet_identity.packet_id
    registry = _g2a3b1_registry_for_rule(fixture.predecessor, rule_id)
    invalidation = _g2a3a_invalidation(
        fixture,
        "ROOT_BOUND_KILL_SWITCH",
    )
    event = _g2a3b1_transition_event(
        registry,
        packet_id,
        rule_id,
        invalidation,
    )
    code = (
        "adapter_not_called"
        if rule_id == "g2a_t09_pending_block"
        else "failed_non_consuming_provenance_valid"
    )
    forged = _g2a3b1_rebind_transition(
        event,
        code,
        evidence_ref="f" * 64,
    )
    with pytest.raises(ValueError):
        acp.record_action_packet_deterministic_invalidation_v01(
            registry,
            packet_id=packet_id,
            invalidation_evidence=invalidation,
            transition_event=forged,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )


def test_g2a3b1_deterministic_context_must_be_policy_bound(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    fixture = g2a3a_fixture
    packet_id = fixture.predecessor.packet_identity.packet_id
    registry = _g2a3b1_registry_for_rule(
        fixture.predecessor,
        "g2a_t07_authorized_block",
    )
    invalidation = _reidentify_invalidation(
        _g2a3a_invalidation(fixture, "ROOT_BOUND_KILL_SWITCH"),
        dependency_id="kill_switch:not_in_policy",
    )
    event = _g2a3b1_transition_event(
        registry,
        packet_id,
        "g2a_t07_authorized_block",
        invalidation,
    )
    with pytest.raises(ValueError):
        acp.record_action_packet_deterministic_invalidation_v01(
            registry,
            packet_id=packet_id,
            invalidation_evidence=invalidation,
            transition_event=event,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )


def test_g2a3b1_revocation_requires_exact_root_provenance_and_binding(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    fixture = g2a3a_fixture
    packet_id = fixture.predecessor.packet_identity.packet_id
    registry = _g2a3b1_registry_for_rule(
        fixture.predecessor,
        "g2a_t16_authorized_revoke",
    )
    forged_binding = _reidentify_accepted_revocation(
        fixture.accepted_revocation_binding,
        revocation_root_decision_id="7" * 64,
        revocation_root_decision_hash="8" * 64,
    )
    forged_invalidation = _g2a3a_invalidation_for_revocation_binding(
        fixture,
        forged_binding,
    )
    forged_event = _g2a3b1_transition_event(
        registry,
        packet_id,
        "g2a_t16_authorized_revoke",
        forged_invalidation,
        accepted_revocation_binding=forged_binding,
    )
    before = repr(registry).encode("utf-8")
    for candidate, projection, binding in (
        (None, fixture.revocation_root_projection,
         fixture.accepted_revocation_binding),
        (fixture.revocation_candidate, None,
         fixture.accepted_revocation_binding),
        (fixture.revocation_candidate, fixture.revocation_root_projection,
         None),
        (fixture.revocation_candidate, fixture.revocation_root_projection,
         forged_binding),
    ):
        with pytest.raises(ValueError):
            acp.record_action_packet_revocation_v01(
                registry,
                packet_id=packet_id,
                revocation_candidate=candidate,
                revocation_root_projection=projection,
                accepted_revocation_binding=binding,
                invalidation_evidence=(
                    forged_invalidation
                    if binding is forged_binding
                    else _g2a3a_invalidation(fixture, "ROOT_REVOCATION")
                ),
                transition_event=(
                    forged_event
                    if binding is forged_binding
                    else _g2a3b1_transition_event(
                        registry,
                        packet_id,
                        "g2a_t16_authorized_revoke",
                        _g2a3a_invalidation(
                            fixture,
                            "ROOT_REVOCATION",
                        ),
                        accepted_revocation_binding=(
                            fixture.accepted_revocation_binding
                        ),
                    )
                ),
                action_packet_transition_registry_profile=_g2a2a_registry(),
            )
    assert repr(registry).encode("utf-8") == before
    assert registry.action_packet_invalidation_contexts == ()


@pytest.mark.parametrize(
    ("rule_id", "evidence_code"),
    (
        ("g2a_t16_authorized_revoke", "accepted_revocation_binding_valid"),
        ("g2a_t16_authorized_revoke", "source_authorization_binding_valid"),
        ("g2a_t16_authorized_revoke", "idempotency_reservation_owned"),
        ("g2a_t18_pending_revoke", "adapter_not_called"),
        ("g2a_t19_failed_revoke", "failed_non_consuming_provenance_valid"),
    ),
)
def test_g2a3b1_revocation_typed_binding_drift_fails_closed(
    g2a3a_fixture: _G2A3AFixtureV01,
    rule_id: str,
    evidence_code: str,
) -> None:
    fixture = g2a3a_fixture
    packet_id = fixture.predecessor.packet_identity.packet_id
    registry = _g2a3b1_registry_for_rule(fixture.predecessor, rule_id)
    invalidation = _g2a3a_invalidation(fixture, "ROOT_REVOCATION")
    event = _g2a3b1_transition_event(
        registry,
        packet_id,
        rule_id,
        invalidation,
        accepted_revocation_binding=fixture.accepted_revocation_binding,
    )
    forged = _g2a3b1_rebind_transition(
        event,
        evidence_code,
        evidence_sha256="d" * 64,
    )
    before = repr(registry).encode("utf-8")
    with pytest.raises(ValueError):
        acp.record_action_packet_revocation_v01(
            registry,
            packet_id=packet_id,
            revocation_candidate=fixture.revocation_candidate,
            revocation_root_projection=fixture.revocation_root_projection,
            accepted_revocation_binding=fixture.accepted_revocation_binding,
            invalidation_evidence=invalidation,
            transition_event=forged,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )
    assert repr(registry).encode("utf-8") == before


def test_g2a3b1_wrong_revocation_root_ref_and_transition_rule_fail_closed(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    fixture = g2a3a_fixture
    packet_id = fixture.predecessor.packet_identity.packet_id
    registry = _g2a3b1_registry_for_rule(
        fixture.predecessor,
        "g2a_t16_authorized_revoke",
    )
    invalidation = _g2a3a_invalidation(fixture, "ROOT_REVOCATION")
    event = _g2a3b1_transition_event(
        registry,
        packet_id,
        "g2a_t16_authorized_revoke",
        invalidation,
        accepted_revocation_binding=fixture.accepted_revocation_binding,
    )
    wrong_root = _rebuild_transition_event(
        event,
        root_decision_ref="9" * 64,
    )
    wrong_rule = _g2a3b1_transition_event(
        registry,
        packet_id,
        "g2a_t17_queued_revoke",
        invalidation,
        accepted_revocation_binding=fixture.accepted_revocation_binding,
    )
    for forged in (wrong_root, wrong_rule):
        with pytest.raises(ValueError):
            acp.record_action_packet_revocation_v01(
                registry,
                packet_id=packet_id,
                revocation_candidate=fixture.revocation_candidate,
                revocation_root_projection=fixture.revocation_root_projection,
                accepted_revocation_binding=(
                    fixture.accepted_revocation_binding
                ),
                invalidation_evidence=invalidation,
                transition_event=forged,
                action_packet_transition_registry_profile=_g2a2a_registry(),
            )


def test_g2a3b1_revocation_manual_bypass_and_duplicate_fail_closed(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    fixture = g2a3a_fixture
    packet_id = fixture.predecessor.packet_identity.packet_id
    registry = _g2a3b1_registry_for_rule(
        fixture.predecessor,
        "g2a_t16_authorized_revoke",
    )
    invalidation = _g2a3a_invalidation(fixture, "ROOT_REVOCATION")
    event = _g2a3b1_transition_event(
        registry,
        packet_id,
        "g2a_t16_authorized_revoke",
        invalidation,
        accepted_revocation_binding=fixture.accepted_revocation_binding,
    )
    updated = acp.record_action_packet_revocation_v01(
        registry,
        packet_id=packet_id,
        revocation_candidate=fixture.revocation_candidate,
        revocation_root_projection=fixture.revocation_root_projection,
        accepted_revocation_binding=fixture.accepted_revocation_binding,
        invalidation_evidence=invalidation,
        transition_event=event,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    manual = replace(updated, action_packet_invalidation_contexts=())
    assert acp.validate_action_commit_packet_registry_v02(manual)[0] is False
    with pytest.raises(ValueError):
        acp.record_action_packet_revocation_v01(
            updated,
            packet_id=packet_id,
            revocation_candidate=fixture.revocation_candidate,
            revocation_root_projection=fixture.revocation_root_projection,
            accepted_revocation_binding=fixture.accepted_revocation_binding,
            invalidation_evidence=invalidation,
            transition_event=event,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )


def test_g2a3b1_supersession_context_remains_orphan_until_g2a3b2(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    fixture = g2a3a_fixture
    registry = acp.build_empty_action_commit_packet_registry_v02()
    for root_bound in (fixture.predecessor, fixture.successor):
        registry = acp.record_action_packet_genesis_v01(
            registry,
            root_bound_genesis=root_bound,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )
    context = acp._ActionPacketInvalidationContextV01(
        invalidation_evidence=_g2a3a_invalidation(
            fixture,
            "ROOT_SUPERSESSION",
        ),
        revocation_candidate=None,
        revocation_root_projection=None,
        accepted_revocation_binding=None,
        supersession_candidate=fixture.supersession_candidate,
        supersession_root_projection=fixture.supersession_root_projection,
        supersession_successor_packet_id=(
            fixture.successor.packet_identity.packet_id
        ),
        accepted_supersession_binding=(
            fixture.accepted_supersession_binding
        ),
    )
    assert acp._validate_action_packet_invalidation_context_v01(
        context,
        fixture.predecessor,
        supersession_successor=fixture.successor,
    ) == (True, ())
    forged = replace(
        registry,
        action_packet_invalidation_contexts=(context,),
    )
    valid, reasons = acp.validate_action_commit_packet_registry_v02(forged)
    assert valid is False
    assert "action_packet_registry_invalidation_context_orphan" in reasons


G2A3B2_ACTIVE_RULES = (
    ("ROOT_AUTHORIZED", "g2a_t20_authorized_supersede"),
    ("QUEUED", "g2a_t21_queued_supersede"),
    ("PENDING_FULFILLMENT", "g2a_t22_pending_supersede"),
    ("FAILED_NON_CONSUMING", "g2a_t23_failed_supersede"),
)
G2A3B2_TERMINAL_STATES = ("EXPIRED", "BLOCKED", "REVOKED")
G2A3B2_MATERIAL_STATES = (
    "CREATED",
    "ROOT_AUTHORIZED",
    "QUEUED",
    "PENDING_FULFILLMENT",
    "FAILED_NON_CONSUMING",
    "EXPIRED",
    "BLOCKED",
    "REVOKED",
)


def _g2a3b2_fixture_variant(
    fixture: _G2A3AFixtureV01,
    *,
    variation: str,
    reason: str,
) -> _G2A3AFixtureV01:
    successor = _g2a3a_successor(
        fixture.predecessor,
        variation=variation,
        supersession_reason_class=reason,
    )
    candidate, root_projection, binding = _g2a3a_supersession_bundle(
        fixture.predecessor,
        successor,
    )
    return replace(
        fixture,
        successor=successor,
        supersession_candidate=candidate,
        supersession_root_projection=root_projection,
        accepted_supersession_binding=binding,
    )


def _g2a3b2_record_genesis_pair(
    fixture: _G2A3AFixtureV01,
) -> acp.ActionCommitPacketRegistryV02:
    registry = acp.build_empty_action_commit_packet_registry_v02()
    for root_bound in (fixture.predecessor, fixture.successor):
        registry = acp.record_action_packet_genesis_v01(
            registry,
            root_bound_genesis=root_bound,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )
    return registry


def _g2a3b2_append_expiry(
    registry: acp.ActionCommitPacketRegistryV02,
    packet_id: str,
    rule_id: str,
) -> acp.ActionCommitPacketRegistryV02:
    entry = next(
        item
        for item in registry.action_packet_lifecycle_entries
        if item.root_bound_genesis.packet_identity.packet_id == packet_id
    )
    expiry = (
        entry.root_bound_genesis.canonical_projection.temporal_authority
        .expires_at_utc
    )
    event = _g2a2b_event(entry, rule_id, evaluation_time=expiry)
    return acp.append_action_packet_lifecycle_transition_v01(
        registry,
        packet_id=packet_id,
        transition_event=event,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )


def _g2a3b2_registry_for_state(
    fixture: _G2A3AFixtureV01,
    state: str,
    *,
    branch_a: bool = False,
) -> acp.ActionCommitPacketRegistryV02:
    registry = acp.record_action_packet_genesis_v01(
        acp.build_empty_action_commit_packet_registry_v02(),
        root_bound_genesis=fixture.predecessor,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    packet_id = fixture.predecessor.packet_identity.packet_id

    def with_successor(
        value: acp.ActionCommitPacketRegistryV02,
    ) -> acp.ActionCommitPacketRegistryV02:
        return acp.record_action_packet_genesis_v01(
            value,
            root_bound_genesis=fixture.successor,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )

    if state == "CREATED":
        return with_successor(registry)
    if branch_a:
        return with_successor(
            _g2a3b2_append_expiry(
                registry,
                packet_id,
                "g2a_t11_created_expire",
            )
        )
    registry, _, _ = _g2a2b_activate(registry, packet_id)
    if state == "ROOT_AUTHORIZED":
        return with_successor(registry)
    if state == "EXPIRED":
        return with_successor(
            _g2a3b2_append_expiry(
                registry,
                packet_id,
                "g2a_t12_authorized_expire",
            )
        )
    if state == "BLOCKED":
        invalidation = _g2a3a_invalidation(
            fixture,
            "ROOT_BOUND_KILL_SWITCH",
        )
        event = _g2a3b1_transition_event(
            registry,
            packet_id,
            "g2a_t07_authorized_block",
            invalidation,
        )
        return with_successor(
            acp.record_action_packet_deterministic_invalidation_v01(
                registry,
                packet_id=packet_id,
                invalidation_evidence=invalidation,
                transition_event=event,
                action_packet_transition_registry_profile=_g2a2a_registry(),
            )
        )
    if state == "REVOKED":
        invalidation = _g2a3a_invalidation(fixture, "ROOT_REVOCATION")
        event = _g2a3b1_transition_event(
            registry,
            packet_id,
            "g2a_t16_authorized_revoke",
            invalidation,
            accepted_revocation_binding=fixture.accepted_revocation_binding,
        )
        return with_successor(
            acp.record_action_packet_revocation_v01(
                registry,
                packet_id=packet_id,
                revocation_candidate=fixture.revocation_candidate,
                revocation_root_projection=fixture.revocation_root_projection,
                accepted_revocation_binding=fixture.accepted_revocation_binding,
                invalidation_evidence=invalidation,
                transition_event=event,
                action_packet_transition_registry_profile=_g2a2a_registry(),
            )
        )
    registry, _ = _g2a2b_append(
        registry,
        packet_id,
        "g2a_t02_queue",
    )
    if state == "QUEUED":
        return with_successor(registry)
    registry, _ = _g2a2b_append(
        registry,
        packet_id,
        "g2a_t03_pending",
        evaluation_context_id="evaluation_context:g2a3b2:attempt:1",
    )
    if state == "PENDING_FULFILLMENT":
        return with_successor(registry)
    if state != "FAILED_NON_CONSUMING":
        raise AssertionError(f"unknown G2-A3B2 state: {state}")
    entry = next(
        item
        for item in registry.action_packet_lifecycle_entries
        if item.root_bound_genesis.packet_identity.packet_id == packet_id
    )
    state_report = acp.derive_action_packet_lifecycle_state_v01(
        registry,
        packet_id=packet_id,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    failure = _g2a2b_event(
        entry,
        "g2a_t24_nonconsuming_failure",
        latest_disposition_event_id=(
            state_report.latest_disposition_event_id
        ),
    )
    return with_successor(
        acp.record_action_packet_nonconsuming_outcome_v01(
            registry,
            packet_id=packet_id,
            transition_event=failure,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )
    )


def _g2a3b2_invalidation(
    fixture: _G2A3AFixtureV01,
    *,
    evaluation_time: int = EVALUATION_TIME,
    evaluation_context_id: str = "evaluation_context:g2a3b2",
) -> acp.ActionInvalidationEvidenceV01:
    return _reidentify_invalidation(
        _g2a3a_invalidation(fixture, "ROOT_SUPERSESSION"),
        evaluation_time=evaluation_time,
        evaluation_context_id=evaluation_context_id,
    )


def _g2a3b2_supersession_transition(
    registry: acp.ActionCommitPacketRegistryV02,
    fixture: _G2A3AFixtureV01,
    rule_id: str,
    invalidation: acp.ActionInvalidationEvidenceV01,
) -> acp.ActionPacketTransitionEventV01:
    predecessor_id = fixture.predecessor.packet_identity.packet_id
    successor_id = fixture.successor.packet_identity.packet_id
    entry = next(
        item
        for item in registry.action_packet_lifecycle_entries
        if item.root_bound_genesis.packet_identity.packet_id == predecessor_id
    )
    state = acp.derive_action_packet_lifecycle_state_v01(
        registry,
        packet_id=predecessor_id,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    latest = entry.transition_events[-1]
    rule = transition_registry.lookup_action_packet_transition_rule_v01(
        registry=_g2a2a_registry(),
        transition_rule_id=rule_id,
    )

    def material(evidence_code: str) -> tuple[str, str, str]:
        if evidence_code == "successor_packet_valid":
            return (
                successor_id,
                successor_id[len(acp.ACTION_COMMIT_PACKET_ID_PREFIX_V01) :],
                acp._ACTION_COMMIT_PACKET_IDENTITY_PROFILE_ID_V01,
            )
        if evidence_code == "accepted_supersession_binding_valid":
            binding_id = (
                fixture.accepted_supersession_binding
                .accepted_supersession_binding_id
            )
            return (
                binding_id,
                binding_id[
                    len(acp.ACCEPTED_SUPERSESSION_BINDING_PREFIX_V01) :
                ],
                acp._ACCEPTED_SUPERSESSION_BINDING_VALIDATOR_PROFILE_ID_V01,
            )
        if evidence_code == "predecessor_binding_valid":
            return (
                predecessor_id,
                predecessor_id[
                    len(acp.ACTION_COMMIT_PACKET_ID_PREFIX_V01) :
                ],
                acp._ACTION_COMMIT_PACKET_IDENTITY_PROFILE_ID_V01,
            )
        if evidence_code == "idempotency_transfer_valid":
            disposition_id = state.latest_disposition_event_id
            assert disposition_id is not None
            return (
                disposition_id,
                disposition_id[
                    len(acp.IDEMPOTENCY_DISPOSITION_EVENT_PREFIX_V01) :
                ],
                acp.IDEMPOTENCY_DISPOSITION_EVENT_PROFILE_ID_V01,
            )
        if evidence_code == "adapter_not_called":
            assert latest.execution_attempt_id is not None
            return (
                latest.execution_attempt_id,
                latest.execution_attempt_id[
                    len(acp.EXECUTION_ATTEMPT_IDENTITY_PREFIX_V01) :
                ],
                acp.EXECUTION_ATTEMPT_IDENTITY_PROFILE_ID_V01,
            )
        if evidence_code == "failed_non_consuming_provenance_valid":
            return (
                latest.transition_event_id,
                latest.transition_event_id[
                    len(acp.ACTION_PACKET_TRANSITION_EVENT_PREFIX_V01) :
                ],
                acp.ACTION_PACKET_TRANSITION_EVENT_PROFILE_ID_V01,
            )
        raise AssertionError(f"unsupported G2-A3B2 evidence: {evidence_code}")

    bindings = tuple(
        acp.build_transition_evidence_binding_v01(
            action_packet_transition_registry_profile=_g2a2a_registry(),
            transition_rule_id=rule_id,
            evidence_code=code,
            evidence_ref=material(code)[0],
            evidence_sha256=material(code)[1],
            validator_profile_id=material(code)[2],
        )
        for code in rule.required_evidence_codes
    )
    predecessor_canonical = fixture.predecessor.canonical_projection
    return acp.build_action_packet_transition_event_v01(
        action_packet_transition_registry_profile=_g2a2a_registry(),
        transition_rule_id=rule_id,
        packet_id=predecessor_id,
        idempotency_key=(
            predecessor_canonical.idempotency_identity.idempotency_key
        ),
        previous_transition_event_id=latest.transition_event_id,
        owning_local_root_id=predecessor_canonical.owning_local_root_id,
        root_decision_ref=(
            fixture.accepted_supersession_binding
            .supersession_root_decision_id
        ),
        transition_evidence_bindings=bindings,
        dependency_set_candidate_fingerprint=(
            predecessor_canonical.dependency_set_candidate_fingerprint
        ),
        temporal_authority_fingerprint=(
            predecessor_canonical.temporal_authority_fingerprint
        ),
        evaluation_time=invalidation.evaluation_time,
        evaluation_time_source=invalidation.evaluation_time_source,
        evaluation_context_id=invalidation.evaluation_context_id,
        execution_attempt_identity=None,
        receipt_ref=None,
    )


def _g2a3b2_successor_activation(
    registry: acp.ActionCommitPacketRegistryV02,
    fixture: _G2A3AFixtureV01,
    invalidation: acp.ActionInvalidationEvidenceV01,
) -> acp.ActionPacketTransitionEventV01:
    successor_id = fixture.successor.packet_identity.packet_id
    entry = next(
        item
        for item in registry.action_packet_lifecycle_entries
        if item.root_bound_genesis.packet_identity.packet_id == successor_id
    )
    return _g2a2b_event(
        entry,
        "g2a_t01_activate_root_authorization",
        evaluation_context_id=invalidation.evaluation_context_id,
        evaluation_time=invalidation.evaluation_time,
    )


def _g2a3b2_disposition(
    registry: acp.ActionCommitPacketRegistryV02,
    fixture: _G2A3AFixtureV01,
    invalidation: acp.ActionInvalidationEvidenceV01,
    successor_activation: acp.ActionPacketTransitionEventV01,
    *,
    branch: str,
    predecessor_event: acp.ActionPacketTransitionEventV01 | None = None,
) -> acp.IdempotencyDispositionEventV01:
    predecessor_id = fixture.predecessor.packet_identity.packet_id
    successor_id = fixture.successor.packet_identity.packet_id
    predecessor_entry = next(
        item
        for item in registry.action_packet_lifecycle_entries
        if item.root_bound_genesis.packet_identity.packet_id == predecessor_id
    )
    predecessor_latest = (
        predecessor_entry.transition_events[-1]
        if predecessor_entry.transition_events
        else None
    )
    predecessor_state = acp.derive_action_packet_lifecycle_state_v01(
        registry,
        packet_id=predecessor_id,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    successor_canonical = fixture.successor.canonical_projection
    successor_root = (
        fixture.successor.root_decision_projection.root_decision_result
        .decision_id
    )
    binding_id = (
        fixture.accepted_supersession_binding
        .accepted_supersession_binding_id
    )
    if branch == "BRANCH_A":
        assert predecessor_latest is not None
        event_class = "RESERVE"
        causes = (
            predecessor_latest.transition_event_id,
            successor_activation.transition_event_id,
        )
        predecessor_ref = predecessor_id
        successor_ref = successor_id
        from_owner = None
        previous = None
        evidence_refs = (
            binding_id,
            predecessor_latest.transition_event_id,
            successor_root,
        )
    elif branch in {"ACTIVE", "TERMINAL"}:
        cause = predecessor_event or predecessor_latest
        assert cause is not None
        event_class = (
            "TRANSFER_RENEWAL"
            if fixture.supersession_candidate.supersession_reason_class
            == "RENEWAL"
            else "TRANSFER_SUPERSESSION"
        )
        causes = (
            cause.transition_event_id,
            successor_activation.transition_event_id,
        )
        predecessor_ref = predecessor_id
        successor_ref = successor_id
        from_owner = predecessor_id
        previous = predecessor_state.latest_disposition_event_id
        evidence_refs = (
            (
                predecessor_latest.transition_event_id
                if branch == "TERMINAL"
                else binding_id
            ),
            (
                binding_id
                if branch == "TERMINAL"
                else fixture.predecessor.canonical_projection.logical_intent
                .root_owned_intent_id
            ),
            successor_root,
        )
    elif branch == "MATERIAL":
        event_class = "RESERVE"
        causes = (successor_activation.transition_event_id,)
        predecessor_ref = None
        successor_ref = None
        from_owner = None
        previous = None
        evidence_refs = _g2a2b_evidence_ids(
            successor_activation,
            (
                "packet_genesis_valid",
                "source_root_authorization_valid",
                "idempotency_acquisition_valid",
            ),
        )
    else:
        raise AssertionError(f"unknown G2-A3B2 branch: {branch}")
    return acp.build_idempotency_disposition_event_v01(
        idempotency_key=(
            successor_canonical.idempotency_identity.idempotency_key
        ),
        event_class=event_class,
        from_disposition=(
            "UNCLAIMED" if event_class == "RESERVE" else "RESERVED"
        ),
        to_disposition="RESERVED",
        from_owner_packet_id=from_owner,
        to_owner_packet_id=successor_id,
        previous_disposition_event_id=previous,
        cause_transition_event_ids=causes,
        root_decision_ref=successor_root,
        predecessor_packet_id=predecessor_ref,
        successor_packet_id=successor_ref,
        evidence_refs=tuple(
            sorted(evidence_refs, key=lambda item: item.encode("utf-8"))
        ),
        evaluation_time=invalidation.evaluation_time,
        evaluation_time_source=invalidation.evaluation_time_source,
        evaluation_context_id=invalidation.evaluation_context_id,
    )


def _g2a3b2_apply(
    registry: acp.ActionCommitPacketRegistryV02,
    fixture: _G2A3AFixtureV01,
    *,
    branch: str,
    predecessor_rule: str | None = None,
    evaluation_time: int = EVALUATION_TIME,
) -> tuple[
    acp.ActionCommitPacketRegistryV02,
    acp.ActionPacketTransitionEventV01 | None,
    acp.ActionPacketTransitionEventV01,
    acp.IdempotencyDispositionEventV01,
]:
    invalidation = _g2a3b2_invalidation(
        fixture,
        evaluation_time=evaluation_time,
    )
    successor_activation = _g2a3b2_successor_activation(
        registry,
        fixture,
        invalidation,
    )
    predecessor_event = (
        _g2a3b2_supersession_transition(
            registry,
            fixture,
            predecessor_rule,
            invalidation,
        )
        if predecessor_rule is not None
        else None
    )
    disposition = _g2a3b2_disposition(
        registry,
        fixture,
        invalidation,
        successor_activation,
        branch=branch,
        predecessor_event=predecessor_event,
    )
    updated = acp.record_action_packet_supersession_v01(
        registry,
        predecessor_packet_id=fixture.predecessor.packet_identity.packet_id,
        successor_packet_id=fixture.successor.packet_identity.packet_id,
        supersession_candidate=fixture.supersession_candidate,
        supersession_root_projection=fixture.supersession_root_projection,
        accepted_supersession_binding=(
            fixture.accepted_supersession_binding
        ),
        invalidation_evidence=invalidation,
        successor_activation_event=successor_activation,
        disposition_event=disposition,
        action_packet_transition_registry_profile=_g2a2a_registry(),
        predecessor_supersession_event=predecessor_event,
    )
    return updated, predecessor_event, successor_activation, disposition


def _g2a3b2_rebuild_disposition(
    event: acp.IdempotencyDispositionEventV01,
    **changes: object,
) -> acp.IdempotencyDispositionEventV01:
    provisional = replace(
        event,
        idempotency_disposition_event_id="",
        **changes,
    )
    return replace(
        provisional,
        idempotency_disposition_event_id=(
            acp.build_domain_separated_identity_v01(
                domain=acp.IDEMPOTENCY_DISPOSITION_EVENT_DOMAIN_V01,
                prefix=acp.IDEMPOTENCY_DISPOSITION_EVENT_PREFIX_V01,
                material=acp.idempotency_disposition_event_material_v01(
                    provisional
                ),
            )
        ),
    )


def _g2a3b2_manual_registry(
    registry: acp.ActionCommitPacketRegistryV02,
    fixture: _G2A3AFixtureV01,
    invalidation: acp.ActionInvalidationEvidenceV01,
    successor_activation: acp.ActionPacketTransitionEventV01,
    disposition: acp.IdempotencyDispositionEventV01,
    predecessor_event: acp.ActionPacketTransitionEventV01 | None,
) -> acp.ActionCommitPacketRegistryV02:
    predecessor_id = fixture.predecessor.packet_identity.packet_id
    successor_id = fixture.successor.packet_identity.packet_id
    entries = []
    for entry in registry.action_packet_lifecycle_entries:
        packet_id = entry.root_bound_genesis.packet_identity.packet_id
        if packet_id == predecessor_id and predecessor_event is not None:
            entry = replace(
                entry,
                transition_events=(
                    entry.transition_events + (predecessor_event,)
                ),
            )
        elif packet_id == successor_id:
            entry = replace(
                entry,
                transition_events=(successor_activation,),
            )
        entries.append(entry)
    context = acp._ActionPacketInvalidationContextV01(
        invalidation_evidence=invalidation,
        revocation_candidate=None,
        revocation_root_projection=None,
        accepted_revocation_binding=None,
        supersession_candidate=fixture.supersession_candidate,
        supersession_root_projection=fixture.supersession_root_projection,
        supersession_successor_packet_id=successor_id,
        accepted_supersession_binding=(
            fixture.accepted_supersession_binding
        ),
    )
    return replace(
        registry,
        action_packet_lifecycle_entries=tuple(entries),
        idempotency_disposition_events=(
            registry.idempotency_disposition_events + (disposition,)
        ),
        action_packet_invalidation_contexts=(
            registry.action_packet_invalidation_contexts + (context,)
        ),
    )


@pytest.mark.parametrize(
    ("reason", "event_class"),
    (
        ("RENEWAL", "RESERVE"),
        ("POLICY_REPLACEMENT", "RESERVE"),
    ),
)
def test_g2a3b2_branch_a_successor_reserve(
    g2a3a_fixture: _G2A3AFixtureV01,
    reason: str,
    event_class: str,
) -> None:
    fixture = (
        g2a3a_fixture
        if reason == "RENEWAL"
        else _g2a3b2_fixture_variant(
            g2a3a_fixture,
            variation="TTL",
            reason=reason,
        )
    )
    registry = _g2a3b2_registry_for_state(
        fixture,
        "EXPIRED",
        branch_a=True,
    )
    expiry = (
        fixture.predecessor.canonical_projection.temporal_authority
        .expires_at_utc
    )
    before = repr(registry).encode("utf-8")
    updated, predecessor_event, _, disposition = _g2a3b2_apply(
        registry,
        fixture,
        branch="BRANCH_A",
        evaluation_time=expiry,
    )
    predecessor_state = acp.derive_action_packet_lifecycle_state_v01(
        updated,
        packet_id=fixture.predecessor.packet_identity.packet_id,
    )
    successor_state = acp.derive_action_packet_lifecycle_state_v01(
        updated,
        packet_id=fixture.successor.packet_identity.packet_id,
    )
    assert predecessor_event is None
    assert disposition.event_class == event_class
    assert predecessor_state.lifecycle_state == "EXPIRED"
    assert (
        successor_state.lifecycle_state,
        successor_state.idempotency_disposition,
        successor_state.reservation_owner_packet_id,
    ) == (
        "ROOT_AUTHORIZED",
        "RESERVED",
        fixture.successor.packet_identity.packet_id,
    )
    assert len(updated.action_packet_invalidation_contexts) == 1
    assert repr(registry).encode("utf-8") == before
    assert updated.real_world_effects_count == 0


@pytest.mark.parametrize(
    ("state", "rule_id"),
    G2A3B2_ACTIVE_RULES,
)
@pytest.mark.parametrize(
    ("reason", "event_class"),
    (
        ("RENEWAL", "TRANSFER_RENEWAL"),
        ("POLICY_REPLACEMENT", "TRANSFER_SUPERSESSION"),
    ),
)
def test_g2a3b2_active_same_effect_transfer(
    g2a3a_fixture: _G2A3AFixtureV01,
    state: str,
    rule_id: str,
    reason: str,
    event_class: str,
) -> None:
    fixture = (
        g2a3a_fixture
        if reason == "RENEWAL"
        else _g2a3b2_fixture_variant(
            g2a3a_fixture,
            variation="TTL",
            reason=reason,
        )
    )
    registry = _g2a3b2_registry_for_state(fixture, state)
    updated, predecessor_event, _, disposition = _g2a3b2_apply(
        registry,
        fixture,
        branch="ACTIVE",
        predecessor_rule=rule_id,
    )
    predecessor_state = acp.derive_action_packet_lifecycle_state_v01(
        updated,
        packet_id=fixture.predecessor.packet_identity.packet_id,
    )
    successor_state = acp.derive_action_packet_lifecycle_state_v01(
        updated,
        packet_id=fixture.successor.packet_identity.packet_id,
    )
    assert predecessor_event is not None
    assert predecessor_state.lifecycle_state == "SUPERSEDED"
    assert disposition.event_class == event_class
    assert (
        successor_state.lifecycle_state,
        successor_state.idempotency_disposition,
        successor_state.reservation_owner_packet_id,
    ) == (
        "ROOT_AUTHORIZED",
        "RESERVED",
        fixture.successor.packet_identity.packet_id,
    )
    assert updated.real_world_effects_count == 0


@pytest.mark.parametrize("state", G2A3B2_TERMINAL_STATES)
@pytest.mark.parametrize(
    ("reason", "event_class"),
    (
        ("RENEWAL", "TRANSFER_RENEWAL"),
        ("POLICY_REPLACEMENT", "TRANSFER_SUPERSESSION"),
    ),
)
def test_g2a3b2_terminal_same_effect_transfer(
    g2a3a_fixture: _G2A3AFixtureV01,
    state: str,
    reason: str,
    event_class: str,
) -> None:
    fixture = (
        g2a3a_fixture
        if reason == "RENEWAL"
        else _g2a3b2_fixture_variant(
            g2a3a_fixture,
            variation="TTL",
            reason=reason,
        )
    )
    registry = _g2a3b2_registry_for_state(fixture, state)
    updated, predecessor_event, _, disposition = _g2a3b2_apply(
        registry,
        fixture,
        branch="TERMINAL",
        evaluation_time=(
            fixture.predecessor.canonical_projection.temporal_authority
            .expires_at_utc
            if state == "EXPIRED"
            else EVALUATION_TIME
        ),
    )
    predecessor_state = acp.derive_action_packet_lifecycle_state_v01(
        updated,
        packet_id=fixture.predecessor.packet_identity.packet_id,
    )
    successor_state = acp.derive_action_packet_lifecycle_state_v01(
        updated,
        packet_id=fixture.successor.packet_identity.packet_id,
    )
    assert predecessor_event is None
    assert predecessor_state.lifecycle_state == state
    assert disposition.event_class == event_class
    assert successor_state.reservation_owner_packet_id == (
        fixture.successor.packet_identity.packet_id
    )
    assert successor_state.lifecycle_state == "ROOT_AUTHORIZED"


@pytest.mark.parametrize(
    ("terminal_rule", "terminal_state"),
    (
        ("g2a_t09_pending_block", "BLOCKED"),
        ("g2a_t18_pending_revoke", "REVOKED"),
    ),
)
def test_g2a3b2_terminal_transfer_after_late_b1_context(
    g2a3a_fixture: _G2A3AFixtureV01,
    terminal_rule: str,
    terminal_state: str,
) -> None:
    predecessor_id = g2a3a_fixture.predecessor.packet_identity.packet_id
    registry = _g2a3b1_registry_for_rule(
        g2a3a_fixture.predecessor,
        terminal_rule,
    )
    if terminal_rule == "g2a_t09_pending_block":
        invalidation = _g2a3a_invalidation(
            g2a3a_fixture,
            "ROOT_BOUND_KILL_SWITCH",
        )
        event = _g2a3b1_transition_event(
            registry,
            predecessor_id,
            terminal_rule,
            invalidation,
        )
        registry = acp.record_action_packet_deterministic_invalidation_v01(
            registry,
            packet_id=predecessor_id,
            invalidation_evidence=invalidation,
            transition_event=event,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )
    else:
        invalidation = _g2a3a_invalidation(
            g2a3a_fixture,
            "ROOT_REVOCATION",
        )
        event = _g2a3b1_transition_event(
            registry,
            predecessor_id,
            terminal_rule,
            invalidation,
            accepted_revocation_binding=(
                g2a3a_fixture.accepted_revocation_binding
            ),
        )
        registry = acp.record_action_packet_revocation_v01(
            registry,
            packet_id=predecessor_id,
            revocation_candidate=g2a3a_fixture.revocation_candidate,
            revocation_root_projection=(
                g2a3a_fixture.revocation_root_projection
            ),
            accepted_revocation_binding=(
                g2a3a_fixture.accepted_revocation_binding
            ),
            invalidation_evidence=invalidation,
            transition_event=event,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )
    registry = acp.record_action_packet_genesis_v01(
        registry,
        root_bound_genesis=g2a3a_fixture.successor,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    updated, predecessor_event, _, _ = _g2a3b2_apply(
        registry,
        g2a3a_fixture,
        branch="TERMINAL",
    )
    assert predecessor_event is None
    assert acp.derive_action_packet_lifecycle_state_v01(
        updated,
        packet_id=predecessor_id,
    ).lifecycle_state == terminal_state
    assert len(updated.action_packet_invalidation_contexts) == 2


@pytest.mark.parametrize("state", G2A3B2_MATERIAL_STATES)
def test_g2a3b2_material_effect_distinct_key_successor(
    g2a3a_fixture: _G2A3AFixtureV01,
    state: str,
) -> None:
    fixture = _g2a3b2_fixture_variant(
        g2a3a_fixture,
        variation="MATERIAL",
        reason="MATERIAL_EFFECT_REPLACEMENT",
    )
    registry = _g2a3b2_registry_for_state(fixture, state)
    predecessor_before = acp.derive_action_packet_lifecycle_state_v01(
        registry,
        packet_id=fixture.predecessor.packet_identity.packet_id,
    )
    updated, predecessor_event, _, disposition = _g2a3b2_apply(
        registry,
        fixture,
        branch="MATERIAL",
    )
    predecessor_after = acp.derive_action_packet_lifecycle_state_v01(
        updated,
        packet_id=fixture.predecessor.packet_identity.packet_id,
    )
    successor_after = acp.derive_action_packet_lifecycle_state_v01(
        updated,
        packet_id=fixture.successor.packet_identity.packet_id,
    )
    assert predecessor_event is None
    assert disposition.event_class == "RESERVE"
    assert (
        predecessor_after.lifecycle_state,
        predecessor_after.idempotency_disposition,
        predecessor_after.reservation_owner_packet_id,
    ) == (
        predecessor_before.lifecycle_state,
        predecessor_before.idempotency_disposition,
        predecessor_before.reservation_owner_packet_id,
    )
    assert (
        successor_after.lifecycle_state,
        successor_after.idempotency_disposition,
        successor_after.reservation_owner_packet_id,
    ) == (
        "ROOT_AUTHORIZED",
        "RESERVED",
        fixture.successor.packet_identity.packet_id,
    )
    assert predecessor_after.idempotency_key != successor_after.idempotency_key
    assert updated.real_world_effects_count == 0


def test_g2a3b2_deterministic_vector_is_independently_rebuilt(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    def inputs(
        fixture: _G2A3AFixtureV01,
        state: str,
        branch: str,
        *,
        rule_id: str | None = None,
        branch_a: bool = False,
        evaluation_time: int = EVALUATION_TIME,
    ) -> tuple[
        acp.ActionPacketTransitionEventV01 | None,
        acp.ActionPacketTransitionEventV01,
        acp.IdempotencyDispositionEventV01,
    ]:
        registry = _g2a3b2_registry_for_state(
            fixture,
            state,
            branch_a=branch_a,
        )
        invalidation = _g2a3b2_invalidation(
            fixture,
            evaluation_time=evaluation_time,
        )
        successor = _g2a3b2_successor_activation(
            registry,
            fixture,
            invalidation,
        )
        predecessor = (
            _g2a3b2_supersession_transition(
                registry,
                fixture,
                rule_id,
                invalidation,
            )
            if rule_id is not None
            else None
        )
        disposition = _g2a3b2_disposition(
            registry,
            fixture,
            invalidation,
            successor,
            branch=branch,
            predecessor_event=predecessor,
        )
        return predecessor, successor, disposition

    t20, _, active_renewal = inputs(
        g2a3a_fixture,
        "ROOT_AUTHORIZED",
        "ACTIVE",
        rule_id="g2a_t20_authorized_supersede",
    )
    t22, _, _ = inputs(
        g2a3a_fixture,
        "PENDING_FULFILLMENT",
        "ACTIVE",
        rule_id="g2a_t22_pending_supersede",
    )
    expiry = (
        g2a3a_fixture.predecessor.canonical_projection.temporal_authority
        .expires_at_utc
    )
    _, branch_t01, branch_reserve = inputs(
        g2a3a_fixture,
        "EXPIRED",
        "BRANCH_A",
        branch_a=True,
        evaluation_time=expiry,
    )
    nonrenewal = _g2a3b2_fixture_variant(
        g2a3a_fixture,
        variation="TTL",
        reason="POLICY_REPLACEMENT",
    )
    _, _, active_supersession = inputs(
        nonrenewal,
        "ROOT_AUTHORIZED",
        "ACTIVE",
        rule_id="g2a_t20_authorized_supersede",
    )
    _, _, terminal_renewal = inputs(
        g2a3a_fixture,
        "EXPIRED",
        "TERMINAL",
        evaluation_time=expiry,
    )
    _, _, terminal_supersession = inputs(
        nonrenewal,
        "EXPIRED",
        "TERMINAL",
        evaluation_time=expiry,
    )
    material = _g2a3b2_fixture_variant(
        g2a3a_fixture,
        variation="MATERIAL",
        reason="MATERIAL_EFFECT_REPLACEMENT",
    )
    _, material_t01, material_reserve = inputs(
        material,
        "ROOT_AUTHORIZED",
        "MATERIAL",
    )
    assert t20 is not None
    assert t22 is not None
    observed = {
        "t20_transition_event_id": t20.transition_event_id,
        "t22_transition_event_id": t22.transition_event_id,
        "branch_a_successor_t01_id": branch_t01.transition_event_id,
        "branch_a_reserve_id": (
            branch_reserve.idempotency_disposition_event_id
        ),
        "active_transfer_renewal_id": (
            active_renewal.idempotency_disposition_event_id
        ),
        "active_transfer_supersession_id": (
            active_supersession.idempotency_disposition_event_id
        ),
        "terminal_transfer_renewal_id": (
            terminal_renewal.idempotency_disposition_event_id
        ),
        "terminal_transfer_supersession_id": (
            terminal_supersession.idempotency_disposition_event_id
        ),
        "material_successor_t01_id": material_t01.transition_event_id,
        "material_distinct_key_reserve_id": (
            material_reserve.idempotency_disposition_event_id
        ),
    }
    assert observed == G2A3B2_VECTOR
    for event in (t20, t22, branch_t01, material_t01):
        assert event.transition_event_id == (
            acp.build_domain_separated_identity_v01(
                domain=acp.ACTION_PACKET_TRANSITION_EVENT_DOMAIN_V01,
                prefix=acp.ACTION_PACKET_TRANSITION_EVENT_PREFIX_V01,
                material=acp.action_packet_transition_event_material_v01(
                    event
                ),
            )
        )
    for event in (
        branch_reserve,
        active_renewal,
        active_supersession,
        terminal_renewal,
        terminal_supersession,
        material_reserve,
    ):
        assert event.idempotency_disposition_event_id == (
            acp.build_domain_separated_identity_v01(
                domain=acp.IDEMPOTENCY_DISPOSITION_EVENT_DOMAIN_V01,
                prefix=acp.IDEMPOTENCY_DISPOSITION_EVENT_PREFIX_V01,
                material=acp.idempotency_disposition_event_material_v01(
                    event
                ),
            )
        )


G2A3B2_TYPED_EVIDENCE_MUTATIONS = (
    ("g2a_t20_authorized_supersede", "successor_packet_valid", "ref"),
    ("g2a_t20_authorized_supersede", "successor_packet_valid", "hash"),
    ("g2a_t20_authorized_supersede", "successor_packet_valid", "profile"),
    (
        "g2a_t20_authorized_supersede",
        "accepted_supersession_binding_valid",
        "ref",
    ),
    (
        "g2a_t20_authorized_supersede",
        "accepted_supersession_binding_valid",
        "hash",
    ),
    (
        "g2a_t20_authorized_supersede",
        "accepted_supersession_binding_valid",
        "profile",
    ),
    ("g2a_t20_authorized_supersede", "predecessor_binding_valid", "ref"),
    ("g2a_t20_authorized_supersede", "predecessor_binding_valid", "hash"),
    (
        "g2a_t20_authorized_supersede",
        "predecessor_binding_valid",
        "profile",
    ),
    ("g2a_t20_authorized_supersede", "idempotency_transfer_valid", "ref"),
    ("g2a_t20_authorized_supersede", "idempotency_transfer_valid", "hash"),
    (
        "g2a_t20_authorized_supersede",
        "idempotency_transfer_valid",
        "profile",
    ),
    ("g2a_t22_pending_supersede", "adapter_not_called", "ref"),
    ("g2a_t22_pending_supersede", "adapter_not_called", "hash"),
    ("g2a_t22_pending_supersede", "adapter_not_called", "profile"),
    (
        "g2a_t23_failed_supersede",
        "failed_non_consuming_provenance_valid",
        "ref",
    ),
    (
        "g2a_t23_failed_supersede",
        "failed_non_consuming_provenance_valid",
        "hash",
    ),
    (
        "g2a_t23_failed_supersede",
        "failed_non_consuming_provenance_valid",
        "profile",
    ),
)


@pytest.mark.parametrize(
    ("rule_id", "evidence_code", "field"),
    G2A3B2_TYPED_EVIDENCE_MUTATIONS,
)
def test_g2a3b2_typed_supersession_evidence_is_exact(
    g2a3a_fixture: _G2A3AFixtureV01,
    rule_id: str,
    evidence_code: str,
    field: str,
) -> None:
    state = {
        "g2a_t20_authorized_supersede": "ROOT_AUTHORIZED",
        "g2a_t22_pending_supersede": "PENDING_FULFILLMENT",
        "g2a_t23_failed_supersede": "FAILED_NON_CONSUMING",
    }[rule_id]
    registry = _g2a3b2_registry_for_state(g2a3a_fixture, state)
    invalidation = _g2a3b2_invalidation(g2a3a_fixture)
    successor = _g2a3b2_successor_activation(
        registry,
        g2a3a_fixture,
        invalidation,
    )
    predecessor = _g2a3b2_supersession_transition(
        registry,
        g2a3a_fixture,
        rule_id,
        invalidation,
    )
    predecessor = _g2a3b1_rebind_transition(
        predecessor,
        evidence_code,
        evidence_ref="forged:evidence" if field == "ref" else None,
        evidence_sha256="f" * 64 if field == "hash" else None,
        validator_profile_id=(
            "forged_validator_profile_v01"
            if field == "profile"
            else None
        ),
    )
    disposition = _g2a3b2_disposition(
        registry,
        g2a3a_fixture,
        invalidation,
        successor,
        branch="ACTIVE",
        predecessor_event=predecessor,
    )
    before = repr(registry).encode("utf-8")
    with pytest.raises(ValueError):
        acp.record_action_packet_supersession_v01(
            registry,
            predecessor_packet_id=(
                g2a3a_fixture.predecessor.packet_identity.packet_id
            ),
            successor_packet_id=(
                g2a3a_fixture.successor.packet_identity.packet_id
            ),
            supersession_candidate=g2a3a_fixture.supersession_candidate,
            supersession_root_projection=(
                g2a3a_fixture.supersession_root_projection
            ),
            accepted_supersession_binding=(
                g2a3a_fixture.accepted_supersession_binding
            ),
            invalidation_evidence=invalidation,
            successor_activation_event=successor,
            disposition_event=disposition,
            action_packet_transition_registry_profile=_g2a2a_registry(),
            predecessor_supersession_event=predecessor,
        )
    forged = _g2a3b2_manual_registry(
        registry,
        g2a3a_fixture,
        invalidation,
        successor,
        disposition,
        predecessor,
    )
    assert acp.validate_action_commit_packet_registry_v02(forged)[0] is False
    assert repr(registry).encode("utf-8") == before


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("root_decision_ref", "f" * 64),
        ("evaluation_time", EVALUATION_TIME + 1),
        ("evaluation_time_source", "forged_evaluation_time_source"),
        ("evaluation_context_id", "evaluation_context:forged"),
    ),
)
def test_g2a3b2_supersession_root_and_evaluation_context_are_exact(
    g2a3a_fixture: _G2A3AFixtureV01,
    field: str,
    value: object,
) -> None:
    registry = _g2a3b2_registry_for_state(
        g2a3a_fixture,
        "ROOT_AUTHORIZED",
    )
    invalidation = _g2a3b2_invalidation(g2a3a_fixture)
    successor = _g2a3b2_successor_activation(
        registry,
        g2a3a_fixture,
        invalidation,
    )
    predecessor = _g2a3b2_supersession_transition(
        registry,
        g2a3a_fixture,
        "g2a_t20_authorized_supersede",
        invalidation,
    )
    predecessor = _rebuild_transition_event(
        predecessor,
        **{field: value},
    )
    disposition = _g2a3b2_disposition(
        registry,
        g2a3a_fixture,
        invalidation,
        successor,
        branch="ACTIVE",
        predecessor_event=predecessor,
    )
    with pytest.raises(ValueError):
        acp.record_action_packet_supersession_v01(
            registry,
            predecessor_packet_id=(
                g2a3a_fixture.predecessor.packet_identity.packet_id
            ),
            successor_packet_id=(
                g2a3a_fixture.successor.packet_identity.packet_id
            ),
            supersession_candidate=g2a3a_fixture.supersession_candidate,
            supersession_root_projection=(
                g2a3a_fixture.supersession_root_projection
            ),
            accepted_supersession_binding=(
                g2a3a_fixture.accepted_supersession_binding
            ),
            invalidation_evidence=invalidation,
            successor_activation_event=successor,
            disposition_event=disposition,
            action_packet_transition_registry_profile=_g2a2a_registry(),
            predecessor_supersession_event=predecessor,
        )
    forged = _g2a3b2_manual_registry(
        registry,
        g2a3a_fixture,
        invalidation,
        successor,
        disposition,
        predecessor,
    )
    assert acp.validate_action_commit_packet_registry_v02(forged)[0] is False


def test_g2a3b2_manual_bundle_context_and_disposition_drift_fail_closed(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    registry = _g2a3b2_registry_for_state(
        g2a3a_fixture,
        "ROOT_AUTHORIZED",
    )
    updated, predecessor, successor, disposition = _g2a3b2_apply(
        registry,
        g2a3a_fixture,
        branch="ACTIVE",
        predecessor_rule="g2a_t20_authorized_supersede",
    )
    assert predecessor is not None
    assert acp.validate_action_commit_packet_registry_v02(updated) == (
        True,
        (),
    )
    for forged in (
        replace(updated, action_packet_invalidation_contexts=()),
        replace(
            updated,
            action_packet_invalidation_contexts=(
                updated.action_packet_invalidation_contexts
                + updated.action_packet_invalidation_contexts
            ),
        ),
        replace(
            updated,
            idempotency_disposition_events=(
                updated.idempotency_disposition_events[:-1]
            ),
        ),
        replace(
            updated,
            idempotency_disposition_events=(
                updated.idempotency_disposition_events[:-1]
                + (
                    _g2a3b2_rebuild_disposition(
                        disposition,
                        cause_transition_event_ids=(
                            successor.transition_event_id,
                            predecessor.transition_event_id,
                        ),
                    ),
                )
            ),
        ),
    ):
        assert acp.validate_action_commit_packet_registry_v02(forged)[0] is False


def test_g2a3b2_transfer_class_previous_owner_and_evidence_are_exact(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    registry = _g2a3b2_registry_for_state(
        g2a3a_fixture,
        "ROOT_AUTHORIZED",
    )
    invalidation = _g2a3b2_invalidation(g2a3a_fixture)
    successor = _g2a3b2_successor_activation(
        registry,
        g2a3a_fixture,
        invalidation,
    )
    predecessor = _g2a3b2_supersession_transition(
        registry,
        g2a3a_fixture,
        "g2a_t20_authorized_supersede",
        invalidation,
    )
    valid_disposition = _g2a3b2_disposition(
        registry,
        g2a3a_fixture,
        invalidation,
        successor,
        branch="ACTIVE",
        predecessor_event=predecessor,
    )
    forged_dispositions = (
        _g2a3b2_rebuild_disposition(
            valid_disposition,
            event_class="TRANSFER_SUPERSESSION",
        ),
        _g2a3b2_rebuild_disposition(
            valid_disposition,
            previous_disposition_event_id=(
                acp.IDEMPOTENCY_DISPOSITION_EVENT_PREFIX_V01 + "f" * 64
            ),
        ),
        _g2a3b2_rebuild_disposition(
            valid_disposition,
            from_owner_packet_id=acp.ACTION_COMMIT_PACKET_ID_PREFIX_V01
            + "f" * 64,
        ),
        _g2a3b2_rebuild_disposition(
            valid_disposition,
            evidence_refs=(
                "evidence:forged",
                *valid_disposition.evidence_refs[1:],
            ),
        ),
    )
    before = repr(registry).encode("utf-8")
    for forged in forged_dispositions:
        with pytest.raises(ValueError):
            acp.record_action_packet_supersession_v01(
                registry,
                predecessor_packet_id=(
                    g2a3a_fixture.predecessor.packet_identity.packet_id
                ),
                successor_packet_id=(
                    g2a3a_fixture.successor.packet_identity.packet_id
                ),
                supersession_candidate=(
                    g2a3a_fixture.supersession_candidate
                ),
                supersession_root_projection=(
                    g2a3a_fixture.supersession_root_projection
                ),
                accepted_supersession_binding=(
                    g2a3a_fixture.accepted_supersession_binding
                ),
                invalidation_evidence=invalidation,
                successor_activation_event=successor,
                disposition_event=forged,
                action_packet_transition_registry_profile=(
                    _g2a2a_registry()
                ),
                predecessor_supersession_event=predecessor,
            )
    assert repr(registry).encode("utf-8") == before


@pytest.mark.parametrize(
    ("outcome_rule", "disposition_class", "recorder"),
    (
        (
            "g2a_t04_fulfill_mock",
            "CONSUME",
            acp.record_action_packet_consumed_outcome_v01,
        ),
        (
            "g2a_t26_uncertain_adapter_outcome",
            "UNCERTAIN_CLOSE",
            acp.record_action_packet_uncertain_outcome_v01,
        ),
    ),
)
def test_g2a3b2_consumed_and_uncertain_keys_are_permanently_closed(
    g2a3a_fixture: _G2A3AFixtureV01,
    outcome_rule: str,
    disposition_class: str,
    recorder: object,
) -> None:
    registry = _g2a3b2_registry_for_state(
        g2a3a_fixture,
        "PENDING_FULFILLMENT",
    )
    predecessor_id = g2a3a_fixture.predecessor.packet_identity.packet_id
    entry = next(
        item
        for item in registry.action_packet_lifecycle_entries
        if item.root_bound_genesis.packet_identity.packet_id == predecessor_id
    )
    state = acp.derive_action_packet_lifecycle_state_v01(
        registry,
        packet_id=predecessor_id,
    )
    outcome = _g2a2b_event(entry, outcome_rule)
    close = _g2a2b_outcome_disposition(
        state,
        outcome,
        disposition_class,
    )
    registry = recorder(
        registry,
        packet_id=predecessor_id,
        transition_event=outcome,
        disposition_event=close,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    invalidation = _g2a3b2_invalidation(g2a3a_fixture)
    successor = _g2a3b2_successor_activation(
        registry,
        g2a3a_fixture,
        invalidation,
    )
    predecessor = _g2a3b2_supersession_transition(
        registry,
        g2a3a_fixture,
        "g2a_t20_authorized_supersede",
        invalidation,
    )
    disposition = _g2a3b2_disposition(
        registry,
        g2a3a_fixture,
        invalidation,
        successor,
        branch="ACTIVE",
        predecessor_event=predecessor,
    )
    before = repr(registry).encode("utf-8")
    with pytest.raises(
        ValueError,
        match=(
            "^consumed_key_permanently_closed$"
            if disposition_class == "CONSUME"
            else "^uncertain_key_permanently_closed$"
        ),
    ):
        acp.record_action_packet_supersession_v01(
            registry,
            predecessor_packet_id=predecessor_id,
            successor_packet_id=(
                g2a3a_fixture.successor.packet_identity.packet_id
            ),
            supersession_candidate=g2a3a_fixture.supersession_candidate,
            supersession_root_projection=(
                g2a3a_fixture.supersession_root_projection
            ),
            accepted_supersession_binding=(
                g2a3a_fixture.accepted_supersession_binding
            ),
            invalidation_evidence=invalidation,
            successor_activation_event=successor,
            disposition_event=disposition,
            action_packet_transition_registry_profile=_g2a2a_registry(),
            predecessor_supersession_event=predecessor,
        )
    assert repr(registry).encode("utf-8") == before


def test_g2a3b2_pre_activation_terminal_sources_cannot_transfer(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    branch_a_registry = _g2a3b2_registry_for_state(
        g2a3a_fixture,
        "EXPIRED",
        branch_a=True,
    )
    active_registry = _g2a3b2_registry_for_state(
        g2a3a_fixture,
        "ROOT_AUTHORIZED",
    )
    active_invalidation = _g2a3b2_invalidation(g2a3a_fixture)
    active_successor = _g2a3b2_successor_activation(
        active_registry,
        g2a3a_fixture,
        active_invalidation,
    )
    active_predecessor = _g2a3b2_supersession_transition(
        active_registry,
        g2a3a_fixture,
        "g2a_t20_authorized_supersede",
        active_invalidation,
    )
    transfer = _g2a3b2_disposition(
        active_registry,
        g2a3a_fixture,
        active_invalidation,
        active_successor,
        branch="ACTIVE",
        predecessor_event=active_predecessor,
    )
    branch_invalidation = _g2a3b2_invalidation(
        g2a3a_fixture,
        evaluation_time=(
            g2a3a_fixture.predecessor.canonical_projection
            .temporal_authority.expires_at_utc
        ),
    )
    branch_successor = _g2a3b2_successor_activation(
        branch_a_registry,
        g2a3a_fixture,
        branch_invalidation,
    )
    transfer = _g2a3b2_rebuild_disposition(
        transfer,
        cause_transition_event_ids=(
            branch_a_registry.action_packet_lifecycle_entries[0]
            .transition_events[-1].transition_event_id,
            branch_successor.transition_event_id,
        ),
        evaluation_time=branch_invalidation.evaluation_time,
        evaluation_context_id=branch_invalidation.evaluation_context_id,
    )
    with pytest.raises(ValueError):
        acp.record_action_packet_supersession_v01(
            branch_a_registry,
            predecessor_packet_id=(
                g2a3a_fixture.predecessor.packet_identity.packet_id
            ),
            successor_packet_id=(
                g2a3a_fixture.successor.packet_identity.packet_id
            ),
            supersession_candidate=g2a3a_fixture.supersession_candidate,
            supersession_root_projection=(
                g2a3a_fixture.supersession_root_projection
            ),
            accepted_supersession_binding=(
                g2a3a_fixture.accepted_supersession_binding
            ),
            invalidation_evidence=branch_invalidation,
            successor_activation_event=branch_successor,
            disposition_event=transfer,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )

    registry = acp.record_action_packet_genesis_v01(
        acp.build_empty_action_commit_packet_registry_v02(),
        root_bound_genesis=g2a3a_fixture.predecessor,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    invalidation = _g2a3a_invalidation(
        g2a3a_fixture,
        "ROOT_BOUND_KILL_SWITCH",
    )
    block = _g2a3b1_transition_event(
        registry,
        g2a3a_fixture.predecessor.packet_identity.packet_id,
        "g2a_t06_created_block",
        invalidation,
    )
    registry = acp.record_action_packet_deterministic_invalidation_v01(
        registry,
        packet_id=g2a3a_fixture.predecessor.packet_identity.packet_id,
        invalidation_evidence=invalidation,
        transition_event=block,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    registry = acp.record_action_packet_genesis_v01(
        registry,
        root_bound_genesis=g2a3a_fixture.successor,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    supersession_invalidation = _g2a3b2_invalidation(g2a3a_fixture)
    successor = _g2a3b2_successor_activation(
        registry,
        g2a3a_fixture,
        supersession_invalidation,
    )
    reserve = _g2a3b2_disposition(
        registry,
        g2a3a_fixture,
        supersession_invalidation,
        successor,
        branch="BRANCH_A",
    )
    with pytest.raises(ValueError):
        acp.record_action_packet_supersession_v01(
            registry,
            predecessor_packet_id=(
                g2a3a_fixture.predecessor.packet_identity.packet_id
            ),
            successor_packet_id=(
                g2a3a_fixture.successor.packet_identity.packet_id
            ),
            supersession_candidate=g2a3a_fixture.supersession_candidate,
            supersession_root_projection=(
                g2a3a_fixture.supersession_root_projection
            ),
            accepted_supersession_binding=(
                g2a3a_fixture.accepted_supersession_binding
            ),
            invalidation_evidence=supersession_invalidation,
            successor_activation_event=successor,
            disposition_event=reserve,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )


def test_g2a3b2_second_transfer_and_reidentified_binding_fail_closed(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    registry = _g2a3b2_registry_for_state(
        g2a3a_fixture,
        "ROOT_AUTHORIZED",
    )
    updated, predecessor, successor, disposition = _g2a3b2_apply(
        registry,
        g2a3a_fixture,
        branch="ACTIVE",
        predecessor_rule="g2a_t20_authorized_supersede",
    )
    assert predecessor is not None
    with pytest.raises(ValueError):
        acp.record_action_packet_supersession_v01(
            updated,
            predecessor_packet_id=(
                g2a3a_fixture.predecessor.packet_identity.packet_id
            ),
            successor_packet_id=(
                g2a3a_fixture.successor.packet_identity.packet_id
            ),
            supersession_candidate=g2a3a_fixture.supersession_candidate,
            supersession_root_projection=(
                g2a3a_fixture.supersession_root_projection
            ),
            accepted_supersession_binding=(
                g2a3a_fixture.accepted_supersession_binding
            ),
            invalidation_evidence=_g2a3b2_invalidation(g2a3a_fixture),
            successor_activation_event=successor,
            disposition_event=disposition,
            action_packet_transition_registry_profile=_g2a2a_registry(),
            predecessor_supersession_event=predecessor,
        )
    forged_binding = _reidentify_accepted_supersession(
        g2a3a_fixture.accepted_supersession_binding,
        supersession_root_decision_id="f" * 64,
        supersession_root_decision_hash="e" * 64,
    )
    forged_invalidation = _g2a3a_invalidation_for_supersession_binding(
        g2a3a_fixture,
        forged_binding,
    )
    source = _g2a3b2_registry_for_state(
        g2a3a_fixture,
        "ROOT_AUTHORIZED",
    )
    forged_successor = _g2a3b2_successor_activation(
        source,
        g2a3a_fixture,
        forged_invalidation,
    )
    forged_predecessor = _g2a3b2_supersession_transition(
        source,
        replace(
            g2a3a_fixture,
            accepted_supersession_binding=forged_binding,
        ),
        "g2a_t20_authorized_supersede",
        forged_invalidation,
    )
    forged_disposition = _g2a3b2_disposition(
        source,
        replace(
            g2a3a_fixture,
            accepted_supersession_binding=forged_binding,
        ),
        forged_invalidation,
        forged_successor,
        branch="ACTIVE",
        predecessor_event=forged_predecessor,
    )
    with pytest.raises(ValueError):
        acp.record_action_packet_supersession_v01(
            source,
            predecessor_packet_id=(
                g2a3a_fixture.predecessor.packet_identity.packet_id
            ),
            successor_packet_id=(
                g2a3a_fixture.successor.packet_identity.packet_id
            ),
            supersession_candidate=g2a3a_fixture.supersession_candidate,
            supersession_root_projection=(
                g2a3a_fixture.supersession_root_projection
            ),
            accepted_supersession_binding=forged_binding,
            invalidation_evidence=forged_invalidation,
            successor_activation_event=forged_successor,
            disposition_event=forged_disposition,
            action_packet_transition_registry_profile=_g2a2a_registry(),
            predecessor_supersession_event=forged_predecessor,
        )


def _g2a3b2_next_same_key_generation(
    fixture: _G2A3AFixtureV01,
    *,
    supersession_reason_class: str,
    variation: str = "ADAPTER",
) -> _G2A3AFixtureV01:
    successor = _g2a3a_successor(
        fixture.successor,
        variation=variation,
        supersession_reason_class=supersession_reason_class,
    )
    candidate, root_projection, binding = _g2a3a_supersession_bundle(
        fixture.successor,
        successor,
    )
    return replace(
        fixture,
        predecessor=fixture.successor,
        successor=successor,
        supersession_candidate=candidate,
        supersession_root_projection=root_projection,
        accepted_supersession_binding=binding,
    )


def _g2a3b2_first_transfer_then_record_third_generation(
    fixture: _G2A3AFixtureV01,
    *,
    supersession_reason_class: str,
) -> tuple[
    acp.ActionCommitPacketRegistryV02,
    acp.ActionCommitPacketRegistryV02,
    _G2A3AFixtureV01,
]:
    registry = _g2a3b2_registry_for_state(fixture, "ROOT_AUTHORIZED")
    after_first, _, _, _ = _g2a3b2_apply(
        registry,
        fixture,
        branch="ACTIVE",
        predecessor_rule="g2a_t20_authorized_supersede",
    )
    third_fixture = _g2a3b2_next_same_key_generation(
        fixture,
        supersession_reason_class=supersession_reason_class,
    )
    before = repr(after_first).encode("utf-8")
    with_third = acp.record_action_packet_genesis_v01(
        after_first,
        root_bound_genesis=third_fixture.successor,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    assert repr(after_first).encode("utf-8") == before
    assert acp.validate_action_commit_packet_registry_v02(with_third) == (
        True,
        (),
    )
    return after_first, with_third, third_fixture


def _g2a3b2_assert_three_generation_chain(
    registry: acp.ActionCommitPacketRegistryV02,
    fixture: _G2A3AFixtureV01,
    third_fixture: _G2A3AFixtureV01,
    *,
    final_transfer_class: str,
) -> None:
    packets = (
        fixture.predecessor,
        fixture.successor,
        third_fixture.successor,
    )
    states = tuple(
        acp.derive_action_packet_lifecycle_state_v01(
            registry,
            packet_id=packet.packet_identity.packet_id,
        )
        for packet in packets
    )
    assert tuple(state.lifecycle_state for state in states) == (
        "SUPERSEDED",
        "SUPERSEDED",
        "ROOT_AUTHORIZED",
    )
    assert len({state.idempotency_key for state in states}) == 1
    assert len(
        {
            packet.canonical_projection.logical_intent.root_owned_intent_id
            for packet in packets
        }
    ) == 1
    key_events = tuple(
        event
        for event in registry.idempotency_disposition_events
        if event.idempotency_key == states[0].idempotency_key
    )
    assert tuple(event.event_class for event in key_events) == (
        "RESERVE",
        "TRANSFER_RENEWAL",
        final_transfer_class,
    )
    assert tuple(
        (event.from_owner_packet_id, event.to_owner_packet_id)
        for event in key_events
    ) == (
        (None, fixture.predecessor.packet_identity.packet_id),
        (
            fixture.predecessor.packet_identity.packet_id,
            fixture.successor.packet_identity.packet_id,
        ),
        (
            fixture.successor.packet_identity.packet_id,
            third_fixture.successor.packet_identity.packet_id,
        ),
    )
    assert states[-1].reservation_owner_packet_id == (
        third_fixture.successor.packet_identity.packet_id
    )
    assert len(registry.action_packet_invalidation_contexts) == 2
    binding_ids = tuple(
        context.accepted_supersession_binding
        .accepted_supersession_binding_id
        for context in registry.action_packet_invalidation_contexts
    )
    assert len(set(binding_ids)) == 2
    assert all(event.event_class != "RELEASE" for event in key_events)
    assert registry.real_world_effects_count == 0
    assert acp.validate_action_commit_packet_registry_v02(registry) == (
        True,
        (),
    )


def test_g2a3b2_three_generation_same_key_renewal_lineage(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    _, registry, third_fixture = (
        _g2a3b2_first_transfer_then_record_third_generation(
            g2a3a_fixture,
            supersession_reason_class="RENEWAL",
        )
    )
    final, predecessor_event, _, disposition = _g2a3b2_apply(
        registry,
        third_fixture,
        branch="ACTIVE",
        predecessor_rule="g2a_t20_authorized_supersede",
    )
    assert predecessor_event is not None
    assert disposition.event_class == "TRANSFER_RENEWAL"
    _g2a3b2_assert_three_generation_chain(
        final,
        g2a3a_fixture,
        third_fixture,
        final_transfer_class="TRANSFER_RENEWAL",
    )


def test_g2a3b2_three_generation_mixed_same_key_lineage(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    _, registry, third_fixture = (
        _g2a3b2_first_transfer_then_record_third_generation(
            g2a3a_fixture,
            supersession_reason_class="POLICY_REPLACEMENT",
        )
    )
    final, predecessor_event, _, disposition = _g2a3b2_apply(
        registry,
        third_fixture,
        branch="ACTIVE",
        predecessor_rule="g2a_t20_authorized_supersede",
    )
    assert predecessor_event is not None
    assert disposition.event_class == "TRANSFER_SUPERSESSION"
    _g2a3b2_assert_three_generation_chain(
        final,
        g2a3a_fixture,
        third_fixture,
        final_transfer_class="TRANSFER_SUPERSESSION",
    )


def test_g2a3b2_same_key_lineage_requires_current_owner_and_exact_provenance(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    after_first, registry, third_fixture = (
        _g2a3b2_first_transfer_then_record_third_generation(
            g2a3a_fixture,
            supersession_reason_class="RENEWAL",
        )
    )
    invalidation = _g2a3b2_invalidation(third_fixture)
    successor = _g2a3b2_successor_activation(
        registry,
        third_fixture,
        invalidation,
    )
    predecessor = _g2a3b2_supersession_transition(
        registry,
        third_fixture,
        "g2a_t20_authorized_supersede",
        invalidation,
    )
    disposition = _g2a3b2_disposition(
        registry,
        third_fixture,
        invalidation,
        successor,
        branch="ACTIVE",
        predecessor_event=predecessor,
    )
    before = repr(registry).encode("utf-8")
    for wrong_root, wrong_binding in (
        (
            g2a3a_fixture.supersession_root_projection,
            third_fixture.accepted_supersession_binding,
        ),
        (
            third_fixture.supersession_root_projection,
            g2a3a_fixture.accepted_supersession_binding,
        ),
    ):
        with pytest.raises(ValueError):
            acp.record_action_packet_supersession_v01(
                registry,
                predecessor_packet_id=(
                    third_fixture.predecessor.packet_identity.packet_id
                ),
                successor_packet_id=(
                    third_fixture.successor.packet_identity.packet_id
                ),
                supersession_candidate=third_fixture.supersession_candidate,
                supersession_root_projection=wrong_root,
                accepted_supersession_binding=wrong_binding,
                invalidation_evidence=invalidation,
                successor_activation_event=successor,
                disposition_event=disposition,
                action_packet_transition_registry_profile=_g2a2a_registry(),
                predecessor_supersession_event=predecessor,
            )
    assert repr(registry).encode("utf-8") == before

    historical_successor = _g2a3a_successor(
        g2a3a_fixture.predecessor,
        variation="ADAPTER",
        supersession_reason_class="RENEWAL",
    )
    historical_candidate, historical_root, historical_binding = (
        _g2a3a_supersession_bundle(
            g2a3a_fixture.predecessor,
            historical_successor,
        )
    )
    historical_fixture = replace(
        g2a3a_fixture,
        successor=historical_successor,
        supersession_candidate=historical_candidate,
        supersession_root_projection=historical_root,
        accepted_supersession_binding=historical_binding,
    )
    with_historical_successor = acp.record_action_packet_genesis_v01(
        after_first,
        root_bound_genesis=historical_successor,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    active_source = _g2a3b2_registry_for_state(
        historical_fixture,
        "ROOT_AUTHORIZED",
    )
    historical_invalidation = _g2a3b2_invalidation(historical_fixture)
    historical_activation = _g2a3b2_successor_activation(
        active_source,
        historical_fixture,
        historical_invalidation,
    )
    historical_predecessor = _g2a3b2_supersession_transition(
        active_source,
        historical_fixture,
        "g2a_t20_authorized_supersede",
        historical_invalidation,
    )
    historical_disposition = _g2a3b2_disposition(
        active_source,
        historical_fixture,
        historical_invalidation,
        historical_activation,
        branch="ACTIVE",
        predecessor_event=historical_predecessor,
    )
    historical_before = repr(with_historical_successor).encode("utf-8")
    with pytest.raises(ValueError):
        acp.record_action_packet_supersession_v01(
            with_historical_successor,
            predecessor_packet_id=(
                g2a3a_fixture.predecessor.packet_identity.packet_id
            ),
            successor_packet_id=historical_successor.packet_identity.packet_id,
            supersession_candidate=historical_candidate,
            supersession_root_projection=historical_root,
            accepted_supersession_binding=historical_binding,
            invalidation_evidence=historical_invalidation,
            successor_activation_event=historical_activation,
            disposition_event=historical_disposition,
            action_packet_transition_registry_profile=_g2a2a_registry(),
            predecessor_supersession_event=historical_predecessor,
        )
    assert (
        repr(with_historical_successor).encode("utf-8")
        == historical_before
    )


def test_g2a3b2_same_key_lineage_orphan_cycle_and_incomplete_bundle_fail(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    after_first, registry, third_fixture = (
        _g2a3b2_first_transfer_then_record_third_generation(
            g2a3a_fixture,
            supersession_reason_class="RENEWAL",
        )
    )
    initial_only = acp.record_action_packet_genesis_v01(
        acp.build_empty_action_commit_packet_registry_v02(),
        root_bound_genesis=g2a3a_fixture.predecessor,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    initial_only, _, _ = _g2a2b_activate(
        initial_only,
        g2a3a_fixture.predecessor.packet_identity.packet_id,
    )
    with pytest.raises(
        ValueError,
        match="^authority_transition_requires_g2a3_binding$",
    ):
        acp.record_action_packet_genesis_v01(
            initial_only,
            root_bound_genesis=third_fixture.successor,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )

    material_fixture = _g2a3b2_material_fixture_for_amount(
        g2a3a_fixture,
        amount="1500.00",
        reason="MATERIAL_EFFECT_REPLACEMENT_FOREIGN_KEY",
    )
    with_foreign_key_predecessor = acp.record_action_packet_genesis_v01(
        initial_only,
        root_bound_genesis=material_fixture.successor,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    source = g2a3a_fixture.predecessor.canonical_projection.source_packet
    foreign_key_packet = replace(
        source,
        packet_id="legacy:g2a3b2_foreign_key_predecessor",
        source_root_decision_ref=(
            "legacy:g2a3b2_foreign_key_predecessor_root"
        ),
        ttl=replace(
            source.ttl,
            created_at="2026-07-08T00:10:00Z",
            expires_at="2026-07-08T01:10:00Z",
        ),
    )
    foreign_key_canonical = _projection(
        packet=foreign_key_packet,
        policy=g2a3a_fixture.predecessor.canonical_projection.authority_policy,
        dependency=(
            g2a3a_fixture.predecessor.canonical_projection
            .dependency_candidate
        ),
        predecessor_packet_id=(
            material_fixture.successor.packet_identity.packet_id
        ),
        supersession_reason_class="RENEWAL",
    )
    foreign_key_successor = _root_bound_from_canonical(
        foreign_key_canonical
    )
    assert (
        acp.validate_supplier_root_bound_action_commit_packet_v02_projection_v01(
            foreign_key_successor
        )
        == (True, ())
    )
    with pytest.raises(
        ValueError,
        match="^authority_transition_requires_g2a3_binding$",
    ):
        acp.record_action_packet_genesis_v01(
            with_foreign_key_predecessor,
            root_bound_genesis=foreign_key_successor,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )

    original_key = (
        g2a3a_fixture.predecessor.canonical_projection.idempotency_identity
        .idempotency_key
    )
    material_root_bound = material_fixture.successor
    material_canonical = material_root_bound.canonical_projection
    changed_intent_same_key = replace(
        material_root_bound,
        canonical_projection=replace(
            material_canonical,
            idempotency_identity=replace(
                material_canonical.idempotency_identity,
                idempotency_key=original_key,
            ),
        ),
    )
    changed_intent_entry = acp.ActionPacketLifecycleEntryV01(
        root_bound_genesis=changed_intent_same_key,
        transition_registry_id=_g2a2a_registry().transition_registry_id,
        transition_events=(),
    )
    changed_intent_registry = replace(
        initial_only,
        action_packet_lifecycle_entries=(
            initial_only.action_packet_lifecycle_entries
            + (changed_intent_entry,)
        ),
    )
    assert acp.validate_action_commit_packet_registry_v02(
        changed_intent_registry
    )[0] is False

    third_id = third_fixture.successor.packet_identity.packet_id
    second_id = g2a3a_fixture.successor.packet_identity.packet_id

    def replace_predecessor(
        entry: acp.ActionPacketLifecycleEntryV01,
        predecessor_id: str,
    ) -> acp.ActionPacketLifecycleEntryV01:
        root_bound = entry.root_bound_genesis
        canonical = root_bound.canonical_projection
        authorization = replace(
            canonical.authorization_candidate,
            predecessor_packet_id=predecessor_id,
        )
        return replace(
            entry,
            root_bound_genesis=replace(
                root_bound,
                canonical_projection=replace(
                    canonical,
                    authorization_candidate=authorization,
                ),
            ),
        )

    entries = registry.action_packet_lifecycle_entries
    third_entry = next(
        entry
        for entry in entries
        if entry.root_bound_genesis.packet_identity.packet_id == third_id
    )
    self_referential = replace(
        registry,
        action_packet_lifecycle_entries=tuple(
            replace_predecessor(entry, third_id)
            if entry is third_entry
            else entry
            for entry in entries
        ),
    )
    assert acp.validate_action_commit_packet_registry_v02(
        self_referential
    )[0] is False

    cyclic = replace(
        registry,
        action_packet_lifecycle_entries=tuple(
            replace_predecessor(entry, third_id)
            if entry.root_bound_genesis.packet_identity.packet_id == second_id
            else replace_predecessor(entry, second_id)
            if entry is third_entry
            else entry
            for entry in entries
        ),
    )
    assert acp.validate_action_commit_packet_registry_v02(cyclic)[0] is False
    orphan = replace(
        registry,
        action_packet_lifecycle_entries=tuple(
            entry
            for entry in entries
            if entry.root_bound_genesis.packet_identity.packet_id != second_id
        ),
    )
    assert acp.validate_action_commit_packet_registry_v02(orphan)[0] is False

    final, _, _, _ = _g2a3b2_apply(
        registry,
        third_fixture,
        branch="ACTIVE",
        predecessor_rule="g2a_t20_authorized_supersede",
    )
    without_second_context = replace(
        final,
        action_packet_invalidation_contexts=(
            final.action_packet_invalidation_contexts[:-1]
        ),
    )
    without_second_transfer = replace(
        final,
        idempotency_disposition_events=(
            final.idempotency_disposition_events[:-1]
        ),
    )
    wrong_transfer_order = replace(
        final,
        idempotency_disposition_events=(
            final.idempotency_disposition_events[0],
            final.idempotency_disposition_events[2],
            final.idempotency_disposition_events[1],
        ),
    )
    for forged in (
        without_second_context,
        without_second_transfer,
        wrong_transfer_order,
    ):
        assert acp.validate_action_commit_packet_registry_v02(forged)[0] is False
    assert acp.validate_action_commit_packet_registry_v02(after_first) == (
        True,
        (),
    )


def _g2a3b2_material_fixture_for_amount(
    fixture: _G2A3AFixtureV01,
    *,
    amount: str,
    reason: str,
) -> _G2A3AFixtureV01:
    predecessor = fixture.predecessor
    source = predecessor.canonical_projection.source_packet
    packet = replace(
        source,
        packet_id=f"legacy:g2a3b2_material:{amount}",
        source_root_decision_ref=f"legacy:g2a3b2_material_root:{amount}",
        scope=replace(source.scope, amount=amount),
    )
    canonical = _projection(
        packet=packet,
        policy=predecessor.canonical_projection.authority_policy,
        dependency=predecessor.canonical_projection.dependency_candidate,
        predecessor_packet_id=predecessor.packet_identity.packet_id,
        supersession_reason_class=reason,
    )
    successor = _root_bound_from_canonical(canonical)
    candidate, root_projection, binding = _g2a3a_supersession_bundle(
        predecessor,
        successor,
    )
    return replace(
        fixture,
        successor=successor,
        supersession_candidate=candidate,
        supersession_root_projection=root_projection,
        accepted_supersession_binding=binding,
    )


def test_g2a3b2_supersession_context_and_disposition_append_order_cross_bound(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    first_fixture = _g2a3b2_material_fixture_for_amount(
        g2a3a_fixture,
        amount="1300.00",
        reason="MATERIAL_EFFECT_REPLACEMENT_1",
    )
    second_fixture = _g2a3b2_material_fixture_for_amount(
        g2a3a_fixture,
        amount="1400.00",
        reason="MATERIAL_EFFECT_REPLACEMENT_2",
    )
    registry = _g2a3b2_registry_for_state(
        first_fixture,
        "ROOT_AUTHORIZED",
    )
    registry, _, _, _ = _g2a3b2_apply(
        registry,
        first_fixture,
        branch="MATERIAL",
    )
    assert acp.validate_action_commit_packet_registry_v02(registry) == (
        True,
        (),
    )
    registry = acp.record_action_packet_genesis_v01(
        registry,
        root_bound_genesis=second_fixture.successor,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    registry, _, _, _ = _g2a3b2_apply(
        registry,
        second_fixture,
        branch="MATERIAL",
    )
    assert acp.validate_action_commit_packet_registry_v02(registry) == (
        True,
        (),
    )
    contexts = registry.action_packet_invalidation_contexts
    dispositions = registry.idempotency_disposition_events
    assert len(contexts) == 2
    assert len(dispositions) == 3

    reversed_contexts = replace(
        registry,
        action_packet_invalidation_contexts=(contexts[1], contexts[0]),
    )
    reversed_dispositions = replace(
        registry,
        idempotency_disposition_events=(
            dispositions[0],
            dispositions[2],
            dispositions[1],
        ),
    )
    for forged in (reversed_contexts, reversed_dispositions):
        valid, reasons = acp.validate_action_commit_packet_registry_v02(
            forged
        )
        assert valid is False
        assert (
            "action_packet_registry_invalidation_context_reordered"
            in reasons
        )

    cross_paired_context = replace(
        contexts[0],
        supersession_successor_packet_id=(
            contexts[1].supersession_successor_packet_id
        ),
    )
    mutations = (
        replace(
            registry,
            action_packet_invalidation_contexts=(
                cross_paired_context,
                contexts[1],
            ),
        ),
        replace(
            registry,
            action_packet_invalidation_contexts=(contexts[0], contexts[0]),
        ),
        replace(
            registry,
            idempotency_disposition_events=(
                dispositions + (dispositions[1],)
            ),
        ),
        replace(
            registry,
            action_packet_invalidation_contexts=(contexts[0],),
        ),
        replace(
            registry,
            idempotency_disposition_events=dispositions[:-1],
        ),
    )
    for forged in mutations:
        assert acp.validate_action_commit_packet_registry_v02(forged)[0] is False


def _g2a3b2_revocation_fixture_for_packet(
    fixture: _G2A3AFixtureV01,
    packet: acp.SupplierRootBoundActionCommitPacketV02ProjectionV01,
) -> _G2A3AFixtureV01:
    canonical = packet.canonical_projection
    source_decision_id = (
        packet.root_decision_projection.root_decision_result.decision_id
    )
    candidate = acp.build_revocation_candidate_v01(
        owning_local_root_id=canonical.owning_local_root_id,
        packet_id=packet.packet_identity.packet_id,
        source_authorization_decision_id=source_decision_id,
        idempotency_key=canonical.idempotency_identity.idempotency_key,
        revocation_reason_class="SUCCESSOR_MANUAL_REVOCATION",
        evidence_refs=(
            "evidence:successor_revocation_policy",
            "evidence:successor_revocation_operator",
        ),
        evidence_hashes=("4" * 64, "5" * 64),
        evaluation_time=EVALUATION_TIME,
        policy_fingerprint=canonical.authority_policy_fingerprint,
    )
    root_projection = _g2a3a_candidate_root_projection(
        canonical,
        candidate_kind="REVOCATION",
        candidate_id=candidate.revocation_candidate_id,
        predecessor=packet,
    )
    binding = acp.build_accepted_revocation_binding_v01(
        candidate=candidate,
        root_projection=root_projection,
        packet=packet,
    )
    return replace(
        fixture,
        predecessor=packet,
        revocation_candidate=candidate,
        revocation_root_projection=root_projection,
        accepted_revocation_binding=binding,
    )


def _g2a3b2_active_transfer_to_successor(
    fixture: _G2A3AFixtureV01,
) -> tuple[
    acp.ActionCommitPacketRegistryV02,
    acp.IdempotencyDispositionEventV01,
]:
    registry = _g2a3b2_registry_for_state(fixture, "ROOT_AUTHORIZED")
    updated, _, _, acquisition = _g2a3b2_apply(
        registry,
        fixture,
        branch="ACTIVE",
        predecessor_rule="g2a_t20_authorized_supersede",
    )
    return updated, acquisition


def test_g2a3b2_lifecycle_continuity_transfer_successor_block_and_terminal(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    transferred, acquisition = _g2a3b2_active_transfer_to_successor(
        g2a3a_fixture
    )
    successor = g2a3a_fixture.successor
    successor_id = successor.packet_identity.packet_id
    successor_fixture = replace(g2a3a_fixture, predecessor=successor)
    invalidation = _g2a3a_invalidation(
        successor_fixture,
        "ROOT_BOUND_KILL_SWITCH",
    )
    block = _g2a3b1_transition_event(
        transferred,
        successor_id,
        "g2a_t07_authorized_block",
        invalidation,
    )
    disposition_history = transferred.idempotency_disposition_events
    blocked = acp.record_action_packet_deterministic_invalidation_v01(
        transferred,
        packet_id=successor_id,
        invalidation_evidence=invalidation,
        transition_event=block,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    blocked_state = acp.derive_action_packet_lifecycle_state_v01(
        blocked,
        packet_id=successor_id,
    )
    assert (
        blocked_state.lifecycle_state,
        blocked_state.idempotency_disposition,
        blocked_state.reservation_owner_packet_id,
        blocked_state.latest_disposition_event_id,
    ) == (
        "BLOCKED",
        "RESERVED",
        successor_id,
        acquisition.idempotency_disposition_event_id,
    )
    assert blocked.idempotency_disposition_events is disposition_history

    third_fixture = _g2a3b2_next_same_key_generation(
        g2a3a_fixture,
        supersession_reason_class="RENEWAL",
    )
    with_third = acp.record_action_packet_genesis_v01(
        blocked,
        root_bound_genesis=third_fixture.successor,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    final, predecessor_event, _, _ = _g2a3b2_apply(
        with_third,
        third_fixture,
        branch="TERMINAL",
        evaluation_time=EVALUATION_TIME + 20,
    )
    assert predecessor_event is None
    assert acp.derive_action_packet_lifecycle_state_v01(
        final,
        packet_id=successor_id,
    ).lifecycle_state == "BLOCKED"
    assert acp.derive_action_packet_lifecycle_state_v01(
        final,
        packet_id=third_fixture.successor.packet_identity.packet_id,
    ).reservation_owner_packet_id == (
        third_fixture.successor.packet_identity.packet_id
    )
    assert acp.validate_action_commit_packet_registry_v02(final) == (
        True,
        (),
    )


def test_g2a3b2_lifecycle_continuity_transfer_successor_revocation(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    transferred, acquisition = _g2a3b2_active_transfer_to_successor(
        g2a3a_fixture
    )
    successor = g2a3a_fixture.successor
    successor_id = successor.packet_identity.packet_id
    fixture = _g2a3b2_revocation_fixture_for_packet(
        g2a3a_fixture,
        successor,
    )
    invalidation = _g2a3a_invalidation(fixture, "ROOT_REVOCATION")
    event = _g2a3b1_transition_event(
        transferred,
        successor_id,
        "g2a_t16_authorized_revoke",
        invalidation,
        accepted_revocation_binding=fixture.accepted_revocation_binding,
    )
    disposition_history = transferred.idempotency_disposition_events
    revoked = acp.record_action_packet_revocation_v01(
        transferred,
        packet_id=successor_id,
        revocation_candidate=fixture.revocation_candidate,
        revocation_root_projection=fixture.revocation_root_projection,
        accepted_revocation_binding=fixture.accepted_revocation_binding,
        invalidation_evidence=invalidation,
        transition_event=event,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    state = acp.derive_action_packet_lifecycle_state_v01(
        revoked,
        packet_id=successor_id,
    )
    assert (
        state.lifecycle_state,
        state.idempotency_disposition,
        state.reservation_owner_packet_id,
        state.latest_disposition_event_id,
    ) == (
        "REVOKED",
        "RESERVED",
        successor_id,
        acquisition.idempotency_disposition_event_id,
    )
    assert revoked.idempotency_disposition_events is disposition_history
    assert acp.validate_action_commit_packet_registry_v02(revoked) == (
        True,
        (),
    )


def test_g2a3b2_lifecycle_continuity_transfer_successor_t24_retry_and_t23(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    transferred, acquisition = _g2a3b2_active_transfer_to_successor(
        g2a3a_fixture
    )
    successor_id = g2a3a_fixture.successor.packet_identity.packet_id
    pending, _ = _g2a2b_append(
        transferred,
        successor_id,
        "g2a_t02_queue",
    )
    pending, _ = _g2a2b_append(
        pending,
        successor_id,
        "g2a_t03_pending",
        evaluation_context_id="evaluation_context:g2a3b2:successor:t24",
    )
    entry = next(
        item
        for item in pending.action_packet_lifecycle_entries
        if item.root_bound_genesis.packet_identity.packet_id == successor_id
    )
    failure = _g2a2b_event(
        entry,
        "g2a_t24_nonconsuming_failure",
        latest_disposition_event_id=(
            acquisition.idempotency_disposition_event_id
        ),
    )
    disposition_history = pending.idempotency_disposition_events
    failed = acp.record_action_packet_nonconsuming_outcome_v01(
        pending,
        packet_id=successor_id,
        transition_event=failure,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    state = acp.derive_action_packet_lifecycle_state_v01(
        failed,
        packet_id=successor_id,
    )
    assert (
        state.lifecycle_state,
        state.idempotency_disposition,
        state.reservation_owner_packet_id,
        state.latest_disposition_event_id,
    ) == (
        "FAILED",
        "RESERVED",
        successor_id,
        acquisition.idempotency_disposition_event_id,
    )
    assert state.failed_provenance == "FAILED_NON_CONSUMING"
    assert failed.idempotency_disposition_events is disposition_history
    retried, _ = _g2a2b_append(failed, successor_id, "g2a_t25_retry")
    assert acp.derive_action_packet_lifecycle_state_v01(
        retried,
        packet_id=successor_id,
    ).lifecycle_state == "QUEUED"

    third_fixture = _g2a3b2_next_same_key_generation(
        g2a3a_fixture,
        supersession_reason_class="RENEWAL",
    )
    with_third = acp.record_action_packet_genesis_v01(
        failed,
        root_bound_genesis=third_fixture.successor,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    superseded, predecessor_event, _, _ = _g2a3b2_apply(
        with_third,
        third_fixture,
        branch="ACTIVE",
        predecessor_rule="g2a_t23_failed_supersede",
        evaluation_time=EVALUATION_TIME + 20,
    )
    assert predecessor_event is not None
    assert acp.derive_action_packet_lifecycle_state_v01(
        superseded,
        packet_id=successor_id,
    ).lifecycle_state == "SUPERSEDED"
    assert acp.validate_action_commit_packet_registry_v02(superseded) == (
        True,
        (),
    )

    wrong_failure = _g2a2b_event(
        entry,
        "g2a_t24_nonconsuming_failure",
        latest_disposition_event_id=(
            transferred.idempotency_disposition_events[0]
            .idempotency_disposition_event_id
        ),
    )
    source_bytes = repr(pending).encode("utf-8")
    with pytest.raises(
        ValueError,
        match="^latest_disposition_event_binding_invalid$",
    ):
        acp.record_action_packet_nonconsuming_outcome_v01(
            pending,
            packet_id=successor_id,
            transition_event=wrong_failure,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )
    assert repr(pending).encode("utf-8") == source_bytes


def test_g2a3b2_lifecycle_continuity_branch_a_successor_block(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    source = _g2a3b2_registry_for_state(
        g2a3a_fixture,
        "EXPIRED",
        branch_a=True,
    )
    expiry = (
        g2a3a_fixture.predecessor.canonical_projection.temporal_authority
        .expires_at_utc
    )
    acquired, _, _, acquisition = _g2a3b2_apply(
        source,
        g2a3a_fixture,
        branch="BRANCH_A",
        evaluation_time=expiry,
    )
    successor_id = g2a3a_fixture.successor.packet_identity.packet_id
    successor_fixture = replace(
        g2a3a_fixture,
        predecessor=g2a3a_fixture.successor,
    )
    invalidation = _reidentify_invalidation(
        _g2a3a_invalidation(
            successor_fixture,
            "ROOT_BOUND_KILL_SWITCH",
        ),
        evaluation_time=expiry + 1,
        evaluation_context_id=(
            "evaluation_context:g2a3b2:branch_a_successor:block"
        ),
    )
    block = _g2a3b1_transition_event(
        acquired,
        successor_id,
        "g2a_t07_authorized_block",
        invalidation,
    )
    blocked = acp.record_action_packet_deterministic_invalidation_v01(
        acquired,
        packet_id=successor_id,
        invalidation_evidence=invalidation,
        transition_event=block,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    state = acp.derive_action_packet_lifecycle_state_v01(
        blocked,
        packet_id=successor_id,
    )
    assert (
        state.lifecycle_state,
        state.idempotency_disposition,
        state.reservation_owner_packet_id,
        state.latest_disposition_event_id,
    ) == (
        "BLOCKED",
        "RESERVED",
        successor_id,
        acquisition.idempotency_disposition_event_id,
    )
    assert blocked.idempotency_disposition_events is (
        acquired.idempotency_disposition_events
    )
    assert acp.validate_action_commit_packet_registry_v02(blocked) == (
        True,
        (),
    )


def test_g2a3b2_lifecycle_continuity_unclaimed_lineage_is_global(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    registry = acp.record_action_packet_genesis_v01(
        acp.build_empty_action_commit_packet_registry_v02(),
        root_bound_genesis=g2a3a_fixture.predecessor,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    valid_lineage = acp.record_action_packet_genesis_v01(
        registry,
        root_bound_genesis=g2a3a_fixture.successor,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    assert valid_lineage.idempotency_disposition_events == ()
    assert acp.validate_action_commit_packet_registry_v02(valid_lineage) == (
        True,
        (),
    )

    successor_only = acp.record_action_packet_genesis_v01(
        acp.build_empty_action_commit_packet_registry_v02(),
        root_bound_genesis=g2a3a_fixture.successor,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    assert acp.validate_action_commit_packet_registry_v02(successor_only) == (
        True,
        (),
    )

    preactivation_expired = _g2a3b2_append_expiry(
        valid_lineage,
        g2a3a_fixture.successor.packet_identity.packet_id,
        "g2a_t11_created_expire",
    )
    assert acp.validate_action_commit_packet_registry_v02(
        preactivation_expired
    ) == (True, ())

    orphan_fixture = _g2a3b2_next_same_key_generation(
        g2a3a_fixture,
        supersession_reason_class="RENEWAL",
    )
    with pytest.raises(
        ValueError,
        match="^authority_transition_requires_g2a3_binding$",
    ):
        acp.record_action_packet_genesis_v01(
            registry,
            root_bound_genesis=orphan_fixture.successor,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )
    orphan_entry = acp.ActionPacketLifecycleEntryV01(
        root_bound_genesis=orphan_fixture.successor,
        transition_registry_id=_g2a2a_registry().transition_registry_id,
        transition_events=(),
    )
    orphan_registry = replace(
        registry,
        action_packet_lifecycle_entries=(
            registry.action_packet_lifecycle_entries + (orphan_entry,)
        ),
    )
    valid, reasons = acp.validate_action_commit_packet_registry_v02(
        orphan_registry
    )
    assert valid is False
    assert "authority_transition_requires_g2a3_binding" in reasons

    second_root = _g2a2_final_same_key_successor(
        g2a3a_fixture.predecessor
    )
    with pytest.raises(
        ValueError,
        match="^authority_transition_requires_g2a3_binding$",
    ):
        acp.record_action_packet_genesis_v01(
            registry,
            root_bound_genesis=second_root,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )


def test_g2a3b2_lifecycle_continuity_acquisition_bundle_is_complete(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    transferred, acquisition = _g2a3b2_active_transfer_to_successor(
        g2a3a_fixture
    )
    causes = acquisition.cause_transition_event_ids
    assert len(causes) == 2
    malformed_acquisitions = (
        _g2a3b2_rebuild_disposition(
            acquisition,
            cause_transition_event_ids=(causes[0],),
        ),
        _g2a3b2_rebuild_disposition(
            acquisition,
            cause_transition_event_ids=(causes[1],),
        ),
        _g2a3b2_rebuild_disposition(
            acquisition,
            to_owner_packet_id=(
                g2a3a_fixture.predecessor.packet_identity.packet_id
            ),
        ),
    )
    for malformed in malformed_acquisitions:
        forged = replace(
            transferred,
            idempotency_disposition_events=(
                transferred.idempotency_disposition_events[:-1]
                + (malformed,)
            ),
        )
        assert acp.validate_action_commit_packet_registry_v02(forged)[0] is False
    duplicate = replace(
        transferred,
        idempotency_disposition_events=(
            transferred.idempotency_disposition_events + (acquisition,)
        ),
    )
    assert acp.validate_action_commit_packet_registry_v02(duplicate)[0] is False


def test_g2a3b2_material_lineage_root_supports_renewal_then_supersession(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    material_fixture = _g2a3b2_material_fixture_for_amount(
        g2a3a_fixture,
        amount="1700.00",
        reason="MATERIAL_EFFECT_LINEAGE_ROOT",
    )
    registry = _g2a3b2_registry_for_state(
        material_fixture,
        "ROOT_AUTHORIZED",
    )
    registry, _, _, _ = _g2a3b2_apply(
        registry,
        material_fixture,
        branch="MATERIAL",
    )
    renewal_fixture = _g2a3b2_next_same_key_generation(
        material_fixture,
        supersession_reason_class="RENEWAL",
        variation="TTL",
    )
    registry = acp.record_action_packet_genesis_v01(
        registry,
        root_bound_genesis=renewal_fixture.successor,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    registry, _, _, renewal_disposition = _g2a3b2_apply(
        registry,
        renewal_fixture,
        branch="ACTIVE",
        predecessor_rule="g2a_t20_authorized_supersede",
    )
    supersession_fixture = _g2a3b2_next_same_key_generation(
        renewal_fixture,
        supersession_reason_class="POLICY_REPLACEMENT",
        variation="ADAPTER",
    )
    registry = acp.record_action_packet_genesis_v01(
        registry,
        root_bound_genesis=supersession_fixture.successor,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    registry, _, _, supersession_disposition = _g2a3b2_apply(
        registry,
        supersession_fixture,
        branch="ACTIVE",
        predecessor_rule="g2a_t20_authorized_supersede",
    )

    packets = (
        material_fixture.predecessor,
        material_fixture.successor,
        renewal_fixture.successor,
        supersession_fixture.successor,
    )
    states = tuple(
        acp.derive_action_packet_lifecycle_state_v01(
            registry,
            packet_id=packet.packet_identity.packet_id,
        )
        for packet in packets
    )
    assert tuple(state.lifecycle_state for state in states) == (
        "ROOT_AUTHORIZED",
        "SUPERSEDED",
        "SUPERSEDED",
        "ROOT_AUTHORIZED",
    )
    first_key = (
        packets[0].canonical_projection.idempotency_identity.idempotency_key
    )
    material_key = (
        packets[1].canonical_projection.idempotency_identity.idempotency_key
    )
    first_intent = (
        packets[0].canonical_projection.logical_intent.root_owned_intent_id
    )
    material_intent = (
        packets[1].canonical_projection.logical_intent.root_owned_intent_id
    )
    assert first_key != material_key
    assert first_intent != material_intent
    assert {
        packet.canonical_projection.idempotency_identity.idempotency_key
        for packet in packets[1:]
    } == {material_key}
    assert {
        packet.canonical_projection.logical_intent.root_owned_intent_id
        for packet in packets[1:]
    } == {material_intent}
    assert states[0].reservation_owner_packet_id == (
        packets[0].packet_identity.packet_id
    )
    assert states[-1].reservation_owner_packet_id == (
        packets[-1].packet_identity.packet_id
    )
    assert renewal_disposition.event_class == "TRANSFER_RENEWAL"
    assert (
        supersession_disposition.event_class
        == "TRANSFER_SUPERSESSION"
    )
    assert len(registry.action_packet_invalidation_contexts) == 3
    assert all(
        event.event_class != "RELEASE"
        for event in registry.idempotency_disposition_events
    )
    assert registry.real_world_effects_count == 0
    assert acp.validate_action_commit_packet_registry_v02(registry) == (
        True,
        (),
    )


def test_g2a3b2_material_lineage_root_requires_exact_external_ancestry(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    material_fixture = _g2a3b2_material_fixture_for_amount(
        g2a3a_fixture,
        amount="1800.00",
        reason="MATERIAL_EFFECT_ANCESTRY",
    )
    registry = _g2a3b2_registry_for_state(
        material_fixture,
        "ROOT_AUTHORIZED",
    )
    registry, _, _, _ = _g2a3b2_apply(
        registry,
        material_fixture,
        branch="MATERIAL",
    )
    renewal_fixture = _g2a3b2_next_same_key_generation(
        material_fixture,
        supersession_reason_class="RENEWAL",
        variation="TTL",
    )
    registry = acp.record_action_packet_genesis_v01(
        registry,
        root_bound_genesis=renewal_fixture.successor,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    assert acp.validate_action_commit_packet_registry_v02(registry) == (
        True,
        (),
    )

    predecessor_id = material_fixture.predecessor.packet_identity.packet_id
    material_id = material_fixture.successor.packet_identity.packet_id
    renewal_id = renewal_fixture.successor.packet_identity.packet_id
    entry_by_id = {
        entry.root_bound_genesis.packet_identity.packet_id: entry
        for entry in registry.action_packet_lifecycle_entries
    }
    predecessor_entry = entry_by_id[predecessor_id]
    material_entry = entry_by_id[material_id]
    renewal_entry = entry_by_id[renewal_id]

    def with_entry(
        source: acp.ActionCommitPacketRegistryV02,
        packet_id: str,
        replacement: acp.ActionPacketLifecycleEntryV01,
    ) -> acp.ActionCommitPacketRegistryV02:
        return replace(
            source,
            action_packet_lifecycle_entries=tuple(
                replacement
                if (
                    entry.root_bound_genesis.packet_identity.packet_id
                    == packet_id
                )
                else entry
                for entry in source.action_packet_lifecycle_entries
            ),
        )

    missing_external = replace(
        registry,
        action_packet_lifecycle_entries=tuple(
            entry
            for entry in registry.action_packet_lifecycle_entries
            if entry.root_bound_genesis.packet_identity.packet_id
            != predecessor_id
        ),
    )
    assert acp.validate_action_commit_packet_registry_v02(
        missing_external
    )[0] is False

    material_root_bound = material_entry.root_bound_genesis
    material_canonical = material_root_bound.canonical_projection
    absent_authorization = replace(
        material_canonical.authorization_candidate,
        predecessor_packet_id=(
            acp.ACTION_COMMIT_PACKET_ID_PREFIX_V01 + "9" * 64
        ),
    )
    absent_predecessor = with_entry(
        registry,
        material_id,
        replace(
            material_entry,
            root_bound_genesis=replace(
                material_root_bound,
                canonical_projection=replace(
                    material_canonical,
                    authorization_candidate=absent_authorization,
                ),
            ),
        ),
    )
    assert acp.validate_action_commit_packet_registry_v02(
        absent_predecessor
    )[0] is False

    predecessor_root_bound = predecessor_entry.root_bound_genesis
    predecessor_canonical = predecessor_root_bound.canonical_projection
    predecessor_intent_alias = with_entry(
        registry,
        predecessor_id,
        replace(
            predecessor_entry,
            root_bound_genesis=replace(
                predecessor_root_bound,
                canonical_projection=replace(
                    predecessor_canonical,
                    logical_intent=material_canonical.logical_intent,
                ),
            ),
        ),
    )
    valid, reasons = acp.validate_action_commit_packet_registry_v02(
        predecessor_intent_alias
    )
    assert valid is False
    assert "logical_effect_identity_alias_forbidden" in reasons

    predecessor_key_alias = with_entry(
        registry,
        predecessor_id,
        replace(
            predecessor_entry,
            root_bound_genesis=replace(
                predecessor_root_bound,
                canonical_projection=replace(
                    predecessor_canonical,
                    idempotency_identity=(
                        material_canonical.idempotency_identity
                    ),
                ),
            ),
        ),
    )
    valid, reasons = acp.validate_action_commit_packet_registry_v02(
        predecessor_key_alias
    )
    assert valid is False
    assert "logical_effect_identity_alias_forbidden" in reasons

    competing_source = replace(
        material_canonical.source_packet,
        packet_id="legacy:g2a3b2_material_competing_root",
        source_root_decision_ref=(
            "legacy:g2a3b2_material_competing_root_decision"
        ),
        ttl=replace(
            material_canonical.source_packet.ttl,
            created_at="2026-07-08T00:20:00Z",
            expires_at="2026-07-08T01:20:00Z",
        ),
    )
    competing_canonical = _projection(
        packet=competing_source,
        policy=material_canonical.authority_policy,
        dependency=material_canonical.dependency_candidate,
        predecessor_packet_id=predecessor_id,
        supersession_reason_class="MATERIAL_EFFECT_COMPETING_ROOT",
    )
    competing_root = _root_bound_from_canonical(competing_canonical)
    assert (
        competing_canonical.idempotency_identity.idempotency_key
        == material_canonical.idempotency_identity.idempotency_key
    )
    assert (
        competing_canonical.logical_intent.root_owned_intent_id
        == material_canonical.logical_intent.root_owned_intent_id
    )
    source_bytes = repr(registry).encode("utf-8")
    with pytest.raises(
        ValueError,
        match="^authority_transition_requires_g2a3_binding$",
    ):
        acp.record_action_packet_genesis_v01(
            registry,
            root_bound_genesis=competing_root,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )
    assert repr(registry).encode("utf-8") == source_bytes
    competing_entry = acp.ActionPacketLifecycleEntryV01(
        root_bound_genesis=competing_root,
        transition_registry_id=_g2a2a_registry().transition_registry_id,
        transition_events=(),
    )
    competing_registry = replace(
        registry,
        action_packet_lifecycle_entries=(
            registry.action_packet_lifecycle_entries + (competing_entry,)
        ),
    )
    assert acp.validate_action_commit_packet_registry_v02(
        competing_registry
    )[0] is False

    renewal_root_bound = renewal_entry.root_bound_genesis
    renewal_canonical = renewal_root_bound.canonical_projection
    self_authorization = replace(
        renewal_canonical.authorization_candidate,
        predecessor_packet_id=renewal_id,
    )
    self_referential = with_entry(
        registry,
        renewal_id,
        replace(
            renewal_entry,
            root_bound_genesis=replace(
                renewal_root_bound,
                canonical_projection=replace(
                    renewal_canonical,
                    authorization_candidate=self_authorization,
                ),
            ),
        ),
    )
    assert acp.validate_action_commit_packet_registry_v02(
        self_referential
    )[0] is False

    without_material_context = replace(
        registry,
        action_packet_invalidation_contexts=(),
    )
    without_material_reserve = replace(
        registry,
        idempotency_disposition_events=tuple(
            event
            for event in registry.idempotency_disposition_events
            if event.to_owner_packet_id != material_id
        ),
    )
    forged_context = replace(
        registry.action_packet_invalidation_contexts[0],
        accepted_supersession_binding=(
            g2a3a_fixture.accepted_supersession_binding
        ),
    )
    wrong_material_binding = replace(
        registry,
        action_packet_invalidation_contexts=(forged_context,),
    )
    for forged in (
        without_material_context,
        without_material_reserve,
        wrong_material_binding,
    ):
        assert acp.validate_action_commit_packet_registry_v02(forged)[0] is False


def test_g2a3b2_material_lineage_root_does_not_relax_initial_activation(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    ordinary = _g2a2b_recorded_genesis(g2a3a_fixture.predecessor)
    ordinary, _, _ = _g2a2b_activate(
        ordinary,
        g2a3a_fixture.predecessor.packet_identity.packet_id,
    )
    assert acp.derive_action_packet_lifecycle_state_v01(
        ordinary,
        packet_id=g2a3a_fixture.predecessor.packet_identity.packet_id,
    ).lifecycle_state == "ROOT_AUTHORIZED"

    material_fixture = _g2a3b2_material_fixture_for_amount(
        g2a3a_fixture,
        amount="1900.00",
        reason="MATERIAL_EFFECT_ACTIVATION_BOUNDARY",
    )
    material_id = material_fixture.successor.packet_identity.packet_id
    successor_only = acp.record_action_packet_genesis_v01(
        acp.build_empty_action_commit_packet_registry_v02(),
        root_bound_genesis=material_fixture.successor,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    inert_state = acp.derive_action_packet_lifecycle_state_v01(
        successor_only,
        packet_id=material_id,
    )
    assert (
        inert_state.lifecycle_state,
        inert_state.idempotency_disposition,
        inert_state.reservation_owner_packet_id,
    ) == ("CREATED", "UNCLAIMED", None)
    activation, reserve = _g2a2b_activation_pair(
        successor_only,
        material_id,
    )
    source_bytes = repr(successor_only).encode("utf-8")
    with pytest.raises(
        ValueError,
        match="^authority_transition_requires_g2a3_binding$",
    ):
        acp.activate_action_packet_lifecycle_v01(
            successor_only,
            packet_id=material_id,
            transition_event=activation,
            disposition_event=reserve,
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )
    assert repr(successor_only).encode("utf-8") == source_bytes
    forged = _g2a2_final_registry_with_event(
        successor_only,
        material_id,
        activation,
        disposition_event=reserve,
    )
    valid, reasons = acp.validate_action_commit_packet_registry_v02(forged)
    assert valid is False
    assert "authority_transition_requires_g2a3_binding" in reasons

    material_source = _g2a3b2_registry_for_state(
        material_fixture,
        "ROOT_AUTHORIZED",
    )
    applied, _, _, _ = _g2a3b2_apply(
        material_source,
        material_fixture,
        branch="MATERIAL",
    )
    material_state = acp.derive_action_packet_lifecycle_state_v01(
        applied,
        packet_id=material_id,
    )
    assert (
        material_state.lifecycle_state,
        material_state.idempotency_disposition,
        material_state.reservation_owner_packet_id,
    ) == ("ROOT_AUTHORIZED", "RESERVED", material_id)
    assert acp.validate_action_commit_packet_registry_v02(applied) == (
        True,
        (),
    )


@pytest.mark.parametrize("malformed", (None, [], {}, "x", object()))
def test_g2a3a_public_validators_are_total(malformed: object) -> None:
    validators = (
        acp.validate_revocation_candidate_v01,
        acp.validate_supersession_candidate_v01,
        acp.validate_accepted_revocation_binding_v01,
        acp.validate_accepted_supersession_binding_v01,
        acp.validate_mandatory_dependency_local_root_acceptance_v01,
        acp.validate_action_invalidation_evidence_v01,
    )
    for validator in validators:
        assert validator(malformed)[0] is False


def test_g2a_validation_pass_preserves_malformed_transition_reason_contract(
    root_bound_fixture: _RootBoundFixtureV01,
) -> None:
    registry = _g2a2b_recorded_genesis(
        root_bound_fixture.root_bound_projection
    )
    entry = registry.action_packet_lifecycle_entries[0]
    expected = (
        False,
        ("action_packet_registry_lifecycle_entry_invalid",),
    )
    for malformed in (None, 1, {}, "x", [], (object(),)):
        malformed_entry = replace(entry, transition_events=malformed)
        malformed_registry = replace(
            registry,
            action_packet_lifecycle_entries=(malformed_entry,),
        )
        assert (
            acp.validate_action_commit_packet_registry_v02(
                malformed_registry
            )
            == expected
        )


def _g2a_validation_representative_registry(
    fixture: _G2A3AFixtureV01,
) -> acp.ActionCommitPacketRegistryV02:
    material_fixture = _g2a3b2_material_fixture_for_amount(
        fixture,
        amount="1700.00",
        reason="MATERIAL_EFFECT_LINEAGE_ROOT",
    )
    registry = _g2a3b2_registry_for_state(
        material_fixture,
        "ROOT_AUTHORIZED",
    )
    registry, _, _, _ = _g2a3b2_apply(
        registry,
        material_fixture,
        branch="MATERIAL",
    )
    renewal_fixture = _g2a3b2_next_same_key_generation(
        material_fixture,
        supersession_reason_class="RENEWAL",
        variation="TTL",
    )
    registry = acp.record_action_packet_genesis_v01(
        registry,
        root_bound_genesis=renewal_fixture.successor,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    registry, _, _, _ = _g2a3b2_apply(
        registry,
        renewal_fixture,
        branch="ACTIVE",
        predecessor_rule="g2a_t20_authorized_supersede",
    )
    return registry


def test_g2a_validation_pass_preserves_unique_packet_lookup_semantics(
    g2a3a_fixture: _G2A3AFixtureV01,
) -> None:
    registry = _g2a_validation_representative_registry(g2a3a_fixture)
    entries = registry.action_packet_lifecycle_entries
    context = registry.action_packet_invalidation_contexts[-1]
    predecessor_entry = next(
        entry
        for entry in entries
        if entry.root_bound_genesis.packet_identity.packet_id
        == context.invalidation_evidence.packet_id
    )
    successor_entry = next(
        entry
        for entry in entries
        if entry.root_bound_genesis.packet_identity.packet_id
        == context.supersession_successor_packet_id
    )
    predecessor_id = (
        predecessor_entry.root_bound_genesis.packet_identity.packet_id
    )
    successor_id = successor_entry.root_bound_genesis.packet_identity.packet_id
    validation_pass = acp._ActionPacketRegistryValidationPassV01(registry)

    assert acp._unique_lifecycle_entry_from_validation_pass_v01(
        validation_pass,
        predecessor_id,
    ) is predecessor_entry
    assert acp._find_lifecycle_entry_v01(
        registry,
        predecessor_id,
    ) is predecessor_entry
    missing_id = "acp_v02:" + "9" * 64
    for lookup in (
        lambda: acp._unique_lifecycle_entry_from_validation_pass_v01(
            validation_pass,
            missing_id,
        ),
        lambda: acp._find_lifecycle_entry_v01(registry, missing_id),
    ):
        with pytest.raises(
            ValueError,
            match="^action_packet_lifecycle_entry_not_found$",
        ):
            lookup()

    for duplicate_entry in (predecessor_entry, successor_entry):
        forged = replace(
            registry,
            action_packet_lifecycle_entries=entries + (duplicate_entry,),
        )
        forged_pass = acp._ActionPacketRegistryValidationPassV01(forged)
        duplicate_id = (
            duplicate_entry.root_bound_genesis.packet_identity.packet_id
        )
        assert len(forged_pass.entries_by_packet_id[duplicate_id]) == 2
        for lookup in (
            lambda: acp._unique_lifecycle_entry_from_validation_pass_v01(
                forged_pass,
                duplicate_id,
            ),
            lambda: acp._find_lifecycle_entry_v01(forged, duplicate_id),
        ):
            with pytest.raises(
                ValueError,
                match="^action_packet_lifecycle_entry_not_found$",
            ):
                lookup()
        bundle_valid, _, matched_disposition = (
            acp._cached_registry_supersession_bundle_v01(
                forged_pass,
                context,
            )
        )
        assert bundle_valid is False
        assert matched_disposition is None
        valid, reasons = acp.validate_action_commit_packet_registry_v02(
            forged
        )
        assert valid is False
        assert reasons[0] == "action_packet_registry_duplicate_genesis"

    assert successor_id != predecessor_id


def test_g2a_validation_pass_bounds_exact_object_revalidation(
    g2a3a_fixture: _G2A3AFixtureV01,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    registry = _g2a_validation_representative_registry(g2a3a_fixture)
    calls = {
        "registry": 0,
        "histories": 0,
        "bundle": 0,
        "root_bound": 0,
        "context": 0,
        "linear_lookup": 0,
    }

    def wrap(name: str, counter: str) -> None:
        original = getattr(acp, name)

        @wraps(original)
        def counted(*args: object, **kwargs: object) -> object:
            calls[counter] += 1
            return original(*args, **kwargs)

        monkeypatch.setattr(acp, name, counted)

    wrap("validate_action_commit_packet_registry_v02", "registry")
    wrap("_validate_registry_lifecycle_histories_v01", "histories")
    wrap("_validate_registry_supersession_bundle_v01", "bundle")
    wrap(
        "validate_supplier_root_bound_action_commit_packet_v02_projection_v01",
        "root_bound",
    )
    wrap("_validate_action_packet_invalidation_context_core_v01", "context")
    wrap("_find_lifecycle_entry_v01", "linear_lookup")

    assert acp.validate_action_commit_packet_registry_v02(registry) == (
        True,
        (),
    )
    exact_root_bound_objects = {
        id(entry.root_bound_genesis)
        for entry in registry.action_packet_lifecycle_entries
    }
    exact_context_inputs = {
        (
            id(context),
            context.invalidation_evidence.packet_id,
            context.supersession_successor_packet_id,
        )
        for context in registry.action_packet_invalidation_contexts
    }
    supersession_context_count = sum(
        context.invalidation_evidence.invalidation_class
        == "ROOT_SUPERSESSION"
        for context in registry.action_packet_invalidation_contexts
    )
    assert calls == {
        "registry": 1,
        "histories": 1,
        "bundle": supersession_context_count,
        "root_bound": len(exact_root_bound_objects),
        "context": len(exact_context_inputs),
        "linear_lookup": 0,
    }


@pytest.fixture(scope="module")
def _g2a_validation_reason_matrix_fixture() -> tuple[
    acp.ActionCommitPacketRegistryV02,
    acp.ActionCommitPacketRegistryV02,
    acp.ActionCommitPacketRegistryV02,
]:
    root_fixture = root_bound_fixture.__wrapped__()
    fixture = g2a3a_fixture.__wrapped__(root_fixture)
    base = _g2a2b_recorded_genesis(fixture.predecessor)
    activated, _, _ = _g2a2b_activate(
        base,
        fixture.predecessor.packet_identity.packet_id,
    )
    representative = _g2a_validation_representative_registry(fixture)
    return base, activated, representative


@pytest.mark.parametrize(
    ("case", "expected"),
    (
        (
            "wrong_lifecycle_tuple",
            (False, ("action_packet_registry_lifecycle_entries_invalid",)),
        ),
        (
            "wrong_disposition_tuple",
            (False, ("action_packet_registry_disposition_events_invalid",)),
        ),
        (
            "wrong_context_tuple",
            (
                False,
                ("action_packet_registry_invalidation_contexts_invalid",),
            ),
        ),
        (
            "transition_none",
            (False, ("action_packet_registry_lifecycle_entry_invalid",)),
        ),
        (
            "transition_integer",
            (False, ("action_packet_registry_lifecycle_entry_invalid",)),
        ),
        (
            "transition_list",
            (False, ("action_packet_registry_lifecycle_entry_invalid",)),
        ),
        (
            "transition_string",
            (False, ("action_packet_registry_lifecycle_entry_invalid",)),
        ),
        (
            "malformed_transition",
            (False, ("action_packet_registry_lifecycle_entry_invalid",)),
        ),
        (
            "duplicate_genesis",
            (
                False,
                (
                    "action_packet_registry_duplicate_genesis",
                    "authority_transition_requires_g2a3_binding",
                ),
            ),
        ),
        (
            "duplicate_transition_identity",
            (
                False,
                (
                    "action_packet_registry_duplicate_genesis",
                    "authority_transition_requires_g2a3_binding",
                    "action_packet_registry_duplicate_transition_event",
                ),
            ),
        ),
        (
            "duplicate_context",
            (
                False,
                (
                    "authority_transition_requires_g2a3_binding",
                    "action_packet_registry_lifecycle_entry_invalid",
                    "action_packet_registry_invalidation_context_duplicate",
                    "action_packet_registry_accepted_binding_reused",
                    "action_packet_registry_invalidation_context_reused",
                    "action_packet_registry_invalidation_context_reordered",
                    "action_packet_registry_cause_transition_missing",
                ),
            ),
        ),
        (
            "duplicate_disposition",
            (
                False,
                (
                    "authority_transition_requires_g2a3_binding",
                    "action_packet_supersession_disposition_invalid",
                    "action_packet_registry_invalidation_context_orphan",
                    "action_packet_registry_disposition_history_invalid",
                ),
            ),
        ),
        (
            "missing_context_packet",
            (
                False,
                (
                    "authority_transition_requires_g2a3_binding",
                    "action_packet_registry_lifecycle_entry_invalid",
                    "action_packet_registry_invalidation_packet_missing",
                    "action_packet_registry_cause_transition_missing",
                ),
            ),
        ),
        (
            "missing_context_successor",
            (
                False,
                (
                    "authority_transition_requires_g2a3_binding",
                    "action_packet_registry_lifecycle_entry_invalid",
                    "action_packet_registry_invalidation_context_invalid",
                    "action_packet_supersession_bundle_invalid",
                    "action_packet_registry_invalidation_context_orphan",
                    "action_packet_registry_cause_transition_missing",
                ),
            ),
        ),
    ),
)
def test_g2a_validation_pass_preserves_registry_reason_matrix(
    case: str,
    expected: tuple[bool, tuple[str, ...]],
    _g2a_validation_reason_matrix_fixture: tuple[
        acp.ActionCommitPacketRegistryV02,
        acp.ActionCommitPacketRegistryV02,
        acp.ActionCommitPacketRegistryV02,
    ],
) -> None:
    base, activated, representative = (
        _g2a_validation_reason_matrix_fixture
    )
    base_entry = base.action_packet_lifecycle_entries[0]
    last_context = representative.action_packet_invalidation_contexts[-1]
    last_disposition = representative.idempotency_disposition_events[-1]
    missing_id = "acp_v02:" + "9" * 64
    if case == "wrong_lifecycle_tuple":
        forged = replace(base, action_packet_lifecycle_entries=[])
    elif case == "wrong_disposition_tuple":
        forged = replace(base, idempotency_disposition_events=[])
    elif case == "wrong_context_tuple":
        forged = replace(base, action_packet_invalidation_contexts=[])
    elif case.startswith("transition_") or case == "malformed_transition":
        malformed_by_case = {
            "transition_none": None,
            "transition_integer": 1,
            "transition_list": [],
            "transition_string": "x",
            "malformed_transition": (object(),),
        }
        forged = replace(
            base,
            action_packet_lifecycle_entries=(
                replace(
                    base_entry,
                    transition_events=malformed_by_case[case],
                ),
            ),
        )
    elif case == "duplicate_genesis":
        forged = replace(
            base,
            action_packet_lifecycle_entries=(
                base.action_packet_lifecycle_entries
                + (base.action_packet_lifecycle_entries[0],)
            ),
        )
    elif case == "duplicate_transition_identity":
        forged = replace(
            activated,
            action_packet_lifecycle_entries=(
                activated.action_packet_lifecycle_entries
                + (activated.action_packet_lifecycle_entries[0],)
            ),
        )
    elif case == "duplicate_context":
        forged = replace(
            representative,
            action_packet_invalidation_contexts=(
                representative.action_packet_invalidation_contexts
                + (last_context,)
            ),
        )
    elif case == "duplicate_disposition":
        forged = replace(
            representative,
            idempotency_disposition_events=(
                representative.idempotency_disposition_events
                + (last_disposition,)
            ),
        )
    elif case == "missing_context_packet":
        forged = replace(
            representative,
            action_packet_invalidation_contexts=(
                representative.action_packet_invalidation_contexts[:-1]
                + (
                    replace(
                        last_context,
                        invalidation_evidence=replace(
                            last_context.invalidation_evidence,
                            packet_id=missing_id,
                        ),
                    ),
                )
            ),
        )
    else:
        assert case == "missing_context_successor"
        forged = replace(
            representative,
            action_packet_invalidation_contexts=(
                representative.action_packet_invalidation_contexts[:-1]
                + (
                    replace(
                        last_context,
                        supersession_successor_packet_id=missing_id,
                    ),
                )
            ),
        )
    assert acp.validate_action_commit_packet_registry_v02(forged) == expected


@dataclass(frozen=True)
class _G2A4AFixtureV01:
    root_bound: acp.SupplierRootBoundActionCommitPacketV02ProjectionV01
    registry: acp.ActionCommitPacketRegistryV02
    pending: acp.ActionPacketTransitionEventV01
    corridor: acp.ContractFulfillmentCorridorV01
    corridor_step: acp.CorridorStepV01
    observations: tuple[acp.ActionDependencyCurrentObservationV01, ...]
    logical_time_bridge: acp.LogicalTimeBridgeV01
    eligibility_evaluation_time: int
    eligibility_evaluation_time_source: str
    eligibility_evaluation_context_id: str


def _g2a4a_fixture_value(
    *,
    dependency: acp.DependencySetCandidateV01 | None = None,
    allowed_subjects: tuple[str, ...] = (
        "subject:procurement_requester",
    ),
) -> _G2A4AFixtureV01:
    source = acp.build_supplier_a_mock_action_commit_packet_fixture_v02()
    source = replace(
        source,
        scope=replace(
            source.scope,
            allowed_subjects=allowed_subjects,
        ),
    )
    temporal = acp.project_packet_ttl_compatibility_v01(
        source.ttl,
        evaluation_time=EVALUATION_TIME,
        temporal_policy_version=TEMPORAL_POLICY,
    ).temporal_authority
    source_dependency = dependency or _dependency(root_id=ROOT_ID)
    committed_records = tuple(
        acp.build_dependency_set_candidate_record_v01(
            dependency_id=record.dependency_id,
            dependency_class=record.dependency_class,
            evidence_ref=record.evidence_ref,
            content_sha256=record.content_sha256,
            requirement_class=record.requirement_class,
            time_envelope_id=(
                acp.build_action_dependency_time_envelope_id_v01(
                    dependency_id=record.dependency_id,
                    evidence_ref=record.evidence_ref,
                    content_sha256=record.content_sha256,
                    freshness_policy_id=record.freshness_policy_id,
                    source_provenance_refs=record.source_provenance_refs,
                    valid_from_utc=temporal.issued_at_utc,
                    valid_to_utc=temporal.expires_at_utc,
                )
            ),
            freshness_policy_id=record.freshness_policy_id,
            source_provenance_refs=record.source_provenance_refs,
            expected_accepting_local_root_id=(
                record.expected_accepting_local_root_id
            ),
        )
        for record in source_dependency.dependency_records
    )
    committed_dependency = acp.build_dependency_set_candidate_v01(
        dependency_records=committed_records
    )
    canonical = _projection(
        packet=source,
        dependency=committed_dependency,
    )
    _, _, kernel, decision_input, result = _build_frozen_root_evidence(
        canonical
    )
    root_projection = acp.build_root_decision_candidate_projection_v01(
        candidate_kind=(
            acp.ROOT_DECISION_CANDIDATE_KIND_PACKET_AUTHORIZATION_V01
        ),
        projected_candidate_id=(
            canonical.authorization_candidate
            .root_packet_authorization_candidate_id
        ),
        root_decision_kernel=kernel,
        root_decision_input=decision_input,
        root_decision_result=result,
    )
    root_bound = (
        acp.build_supplier_root_bound_action_commit_packet_v02_projection_v01(
            canonical_projection=canonical,
            root_decision_projection=root_projection,
        )
    )
    registry, pending = _g2a2b_pending_registry(root_bound)
    step = replace(
        acp.build_supplier_a_corridor_step_fixture_v01(source),
        parent_packet_id=root_bound.packet_identity.packet_id,
        allowed_subjects=source.scope.allowed_subjects,
    )
    corridor = acp.ContractFulfillmentCorridorV01(
        corridor_id="corridor:g2a4a:supplier_a_mock",
        packet_id=root_bound.packet_identity.packet_id,
        corridor_kind=canonical.adapter_binding.corridor_class,
        allowed_steps=(step.step_id,),
    )
    evaluation_context_id = "evaluation_context:g2a4a:eligibility"
    observations = tuple(
        acp.build_action_dependency_current_observation_v01(
            dependency_id=record.dependency_id,
            evidence_ref=record.evidence_ref,
            observed_content_sha256=record.content_sha256,
            time_envelope_id=record.time_envelope_id,
            freshness_policy_id=record.freshness_policy_id,
            source_provenance_refs=record.source_provenance_refs,
            valid_from_utc=canonical.temporal_authority.issued_at_utc,
            valid_to_utc=canonical.temporal_authority.expires_at_utc,
            observed_at_utc=pending.evaluation_time,
            observation_context_id=evaluation_context_id,
        )
        for record in canonical.dependency_candidate.dependency_records
    )
    bridge = acp.build_logical_time_bridge_v01(
        origin_utc_epoch_seconds=canonical.temporal_authority.issued_at_utc,
        seconds_per_tick=1,
        bridge_policy_version="g2a4a_epoch_seconds_v01",
    )
    return _G2A4AFixtureV01(
        root_bound=root_bound,
        registry=registry,
        pending=pending,
        corridor=corridor,
        corridor_step=step,
        observations=observations,
        logical_time_bridge=bridge,
        eligibility_evaluation_time=pending.evaluation_time,
        eligibility_evaluation_time_source=(
            "explicit_g2a4a_eligibility_time"
        ),
        eligibility_evaluation_context_id=evaluation_context_id,
    )


@pytest.fixture(scope="module")
def g2a4a_fixture() -> _G2A4AFixtureV01:
    return _g2a4a_fixture_value()


def _g2a4a_projection_kwargs(
    fixture: _G2A4AFixtureV01,
    **changes: object,
) -> dict[str, object]:
    values: dict[str, object] = {
        "packet_id": fixture.root_bound.packet_identity.packet_id,
        "corridor": fixture.corridor,
        "corridor_step": fixture.corridor_step,
        "current_dependency_observations": fixture.observations,
        "logical_time_bridge": fixture.logical_time_bridge,
        "eligibility_evaluation_time": (
            fixture.eligibility_evaluation_time
        ),
        "eligibility_evaluation_time_source": (
            fixture.eligibility_evaluation_time_source
        ),
        "eligibility_evaluation_context_id": (
            fixture.eligibility_evaluation_context_id
        ),
    }
    values.update(changes)
    return values


def _g2a4a_projection(
    fixture: _G2A4AFixtureV01,
    registry: acp.ActionCommitPacketRegistryV02 | None = None,
    **changes: object,
) -> acp.ActionPacketEffectFirewallProjectionV01:
    return acp.build_action_packet_effect_firewall_projection_v01(
        fixture.registry if registry is None else registry,
        **_g2a4a_projection_kwargs(fixture, **changes),
    )


def test_g2a4a_dependency_observation_identity_and_freshness_are_exact(
    g2a4a_fixture: _G2A4AFixtureV01,
) -> None:
    fixture = g2a4a_fixture
    observation = fixture.observations[0]
    material = acp.action_dependency_current_observation_material_v01(
        observation
    )
    expected_id = acp.build_domain_separated_identity_v01(
        domain=acp.ACTION_DEPENDENCY_CURRENT_OBSERVATION_DOMAIN_V01,
        prefix=acp.ACTION_DEPENDENCY_CURRENT_OBSERVATION_PREFIX_V01,
        material=material,
    )
    assert observation.observation_id == expected_id
    assert acp.validate_action_dependency_current_observation_v01(
        observation
    ) == (True, ())
    inclusive = acp.build_action_dependency_current_observation_v01(
        dependency_id=observation.dependency_id,
        evidence_ref=observation.evidence_ref,
        observed_content_sha256=observation.observed_content_sha256,
        time_envelope_id=observation.time_envelope_id,
        freshness_policy_id=observation.freshness_policy_id,
        source_provenance_refs=observation.source_provenance_refs,
        valid_from_utc=observation.valid_from_utc,
        valid_to_utc=observation.valid_to_utc,
        observed_at_utc=observation.valid_from_utc,
        observation_context_id=observation.observation_context_id,
    )
    assert acp.validate_action_dependency_current_observation_v01(
        inclusive
    ) == (True, ())
    with pytest.raises(ValueError):
        acp.build_action_dependency_current_observation_v01(
            dependency_id=observation.dependency_id,
            evidence_ref=observation.evidence_ref,
            observed_content_sha256=observation.observed_content_sha256,
            time_envelope_id=observation.time_envelope_id,
            freshness_policy_id=observation.freshness_policy_id,
            source_provenance_refs=observation.source_provenance_refs,
            valid_from_utc=observation.valid_from_utc,
            valid_to_utc=observation.valid_to_utc,
            observed_at_utc=observation.valid_to_utc,
            observation_context_id=observation.observation_context_id,
        )
    for bad_time in (True, False):
        with pytest.raises(ValueError):
            acp.build_action_dependency_current_observation_v01(
                dependency_id=observation.dependency_id,
                evidence_ref=observation.evidence_ref,
                observed_content_sha256=(
                    observation.observed_content_sha256
                ),
                time_envelope_id=observation.time_envelope_id,
                freshness_policy_id=observation.freshness_policy_id,
                source_provenance_refs=observation.source_provenance_refs,
                valid_from_utc=bad_time,
                valid_to_utc=observation.valid_to_utc,
                observed_at_utc=observation.observed_at_utc,
                observation_context_id=observation.observation_context_id,
            )
    for drift in (
        replace(observation, observed_content_sha256="b" * 64),
        replace(observation, time_envelope_id="time_envelope:other"),
        replace(observation, freshness_policy_id="freshness_policy:other"),
        replace(observation, source_provenance_refs=("source:other",)),
    ):
        valid, reasons = (
            acp.validate_action_dependency_current_observation_v01(drift)
        )
        assert valid is False
        assert reasons == (
            "dependency_observation_time_envelope_identity_mismatch",
        )
    forged_observation_id = replace(
        observation,
        observation_id=(
            acp.ACTION_DEPENDENCY_CURRENT_OBSERVATION_PREFIX_V01
            + ("c" * 64)
        ),
    )
    assert acp.validate_action_dependency_current_observation_v01(
        forged_observation_id
    ) == (
        False,
        ("dependency_observation_identity_mismatch",),
    )
    future = acp.build_action_dependency_current_observation_v01(
        dependency_id=observation.dependency_id,
        evidence_ref=observation.evidence_ref,
        observed_content_sha256=observation.observed_content_sha256,
        time_envelope_id=observation.time_envelope_id,
        freshness_policy_id=observation.freshness_policy_id,
        source_provenance_refs=observation.source_provenance_refs,
        valid_from_utc=observation.valid_from_utc,
        valid_to_utc=observation.valid_to_utc,
        observed_at_utc=fixture.eligibility_evaluation_time + 1,
        observation_context_id=observation.observation_context_id,
    )
    for observations in (
        (observation, observation),
        (replace(observation, dependency_id="dependency:unknown"),),
        (future,),
    ):
        with pytest.raises(ValueError):
            _g2a4a_projection(
                fixture,
                current_dependency_observations=observations,
            )


def test_g2a4a_pre_fulfillment_requires_pending_owned_reserved_packet(
    g2a4a_fixture: _G2A4AFixtureV01,
) -> None:
    fixture = g2a4a_fixture
    projection = _g2a4a_projection(fixture)
    assert projection.execution_attempt_id == (
        fixture.pending.execution_attempt_id
    )
    packet_id = fixture.root_bound.packet_identity.packet_id
    state = acp.derive_action_packet_lifecycle_state_v01(
        fixture.registry,
        packet_id=packet_id,
    )
    assert state.lifecycle_state == "PENDING_FULFILLMENT"
    assert state.idempotency_disposition == "RESERVED"
    assert state.reservation_owner_packet_id == packet_id

    genesis = _g2a2b_recorded_genesis(fixture.root_bound)
    authorized, _, _ = _g2a2b_activate(genesis, packet_id)
    queued, _ = _g2a2b_append(
        authorized,
        packet_id,
        "g2a_t02_queue",
    )
    for registry in (genesis, authorized, queued):
        with pytest.raises(ValueError):
            _g2a4a_projection(fixture, registry)

    current = state
    failed_event = _g2a2b_event(
        fixture.registry.action_packet_lifecycle_entries[0],
        "g2a_t24_nonconsuming_failure",
        latest_disposition_event_id=current.latest_disposition_event_id,
    )
    failed = acp.record_action_packet_nonconsuming_outcome_v01(
        fixture.registry,
        packet_id=packet_id,
        transition_event=failed_event,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    with pytest.raises(ValueError):
        _g2a4a_projection(fixture, failed)

    fulfilled_event = _g2a2b_event(
        fixture.registry.action_packet_lifecycle_entries[0],
        "g2a_t04_fulfill_mock",
    )
    consume = _g2a2b_outcome_disposition(
        state,
        fulfilled_event,
        "CONSUME",
    )
    fulfilled = acp.record_action_packet_consumed_outcome_v01(
        fixture.registry,
        packet_id=packet_id,
        transition_event=fulfilled_event,
        disposition_event=consume,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    with pytest.raises(ValueError):
        _g2a4a_projection(fixture, fulfilled)
    fulfilled_state = acp.derive_action_packet_lifecycle_state_v01(
        fulfilled,
        packet_id=packet_id,
    )
    receipt_event = _g2a2b_event(
        fulfilled.action_packet_lifecycle_entries[0],
        "g2a_t05_receipt",
        receipt_ref="receipt:g2a4a:terminal",
    )
    confirmation = _g2a2b_outcome_disposition(
        fulfilled_state,
        receipt_event,
        "RECEIPT_CONFIRM",
    )
    received = acp.record_action_packet_receipt_confirmation_v01(
        fulfilled,
        packet_id=packet_id,
        transition_event=receipt_event,
        disposition_event=confirmation,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    with pytest.raises(ValueError):
        _g2a4a_projection(fixture, received)

    uncertain_event = _g2a2b_event(
        fixture.registry.action_packet_lifecycle_entries[0],
        "g2a_t26_uncertain_adapter_outcome",
    )
    uncertain_disposition = _g2a2b_outcome_disposition(
        state,
        uncertain_event,
        "UNCERTAIN_CLOSE",
    )
    uncertain = acp.record_action_packet_uncertain_outcome_v01(
        fixture.registry,
        packet_id=packet_id,
        transition_event=uncertain_event,
        disposition_event=uncertain_disposition,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    with pytest.raises(ValueError):
        _g2a4a_projection(fixture, uncertain)

    wrong_owner = replace(
        fixture.registry,
        idempotency_disposition_events=(
            replace(
                fixture.registry.idempotency_disposition_events[0],
                to_owner_packet_id="acp_v02:" + "f" * 64,
            ),
        ),
    )
    with pytest.raises(ValueError):
        _g2a4a_projection(fixture, wrong_owner)


def test_g2a4a_pre_fulfillment_recomputes_mandatory_dependency_freshness(
    g2a4a_fixture: _G2A4AFixtureV01,
) -> None:
    fixture = g2a4a_fixture
    observation = fixture.observations[0]
    assert _g2a4a_projection(fixture).dependency_observation_ids == (
        observation.observation_id,
    )
    assert _g2a4a_projection(
        fixture,
        current_dependency_observations=(observation,),
        eligibility_evaluation_time=observation.valid_to_utc - 1,
    )
    with pytest.raises(ValueError):
        _g2a4a_projection(
            fixture,
            current_dependency_observations=(observation,),
            eligibility_evaluation_time=observation.valid_to_utc,
        )
    for observations in (
        (),
        (
            replace(
                observation,
                observed_content_sha256="c" * 64,
            ),
        ),
    ):
        with pytest.raises(ValueError):
            _g2a4a_projection(
                fixture,
                current_dependency_observations=observations,
            )

    mandatory = fixture.root_bound.canonical_projection.dependency_candidate
    optional_record = acp.build_dependency_set_candidate_record_v01(
        dependency_id="dependency:optional_quote",
        dependency_class="QUOTE_EVIDENCE",
        evidence_ref="evidence:optional_quote",
        content_sha256="d" * 64,
        requirement_class="OPTIONAL",
        time_envelope_id="time_envelope:optional_quote",
        freshness_policy_id="freshness_policy:optional_quote_v01",
        source_provenance_refs=("source:optional_quote",),
        expected_accepting_local_root_id=ROOT_ID,
    )
    with_optional = acp.build_dependency_set_candidate_v01(
        dependency_records=(
            mandatory.dependency_records[0],
            optional_record,
        ),
    )
    optional_fixture = _g2a4a_fixture_value(dependency=with_optional)
    mandatory_only = tuple(
        item
        for item in optional_fixture.observations
        if item.dependency_id != optional_record.dependency_id
    )
    assert _g2a4a_projection(
        optional_fixture,
        current_dependency_observations=mandatory_only,
    )


def test_g2a4a_retry_uses_new_attempt_and_fresh_firewall_state(
    g2a4a_fixture: _G2A4AFixtureV01,
) -> None:
    fixture = g2a4a_fixture
    first = acp._prepare_action_packet_effect_attempt_v01(
        fixture.registry,
        **_g2a4a_projection_kwargs(fixture),
    )
    packet_id = fixture.root_bound.packet_identity.packet_id
    state = acp.derive_action_packet_lifecycle_state_v01(
        fixture.registry,
        packet_id=packet_id,
    )
    failure = _g2a2b_event(
        fixture.registry.action_packet_lifecycle_entries[0],
        "g2a_t24_nonconsuming_failure",
        latest_disposition_event_id=state.latest_disposition_event_id,
    )
    retry_registry = acp.record_action_packet_nonconsuming_outcome_v01(
        fixture.registry,
        packet_id=packet_id,
        transition_event=failure,
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    retry_registry, _ = _g2a2b_append(
        retry_registry,
        packet_id,
        "g2a_t25_retry",
    )
    retry_registry, second_pending = _g2a2b_append(
        retry_registry,
        packet_id,
        "g2a_t03_pending",
        evaluation_context_id="evaluation_context:g2a4a:attempt:2",
    )
    second = acp._prepare_action_packet_effect_attempt_v01(
        retry_registry,
        **_g2a4a_projection_kwargs(
            fixture,
            eligibility_evaluation_time=second_pending.evaluation_time,
        ),
    )
    assert fixture.pending.execution_attempt_id != (
        second_pending.execution_attempt_id
    )
    assert first.firewall.invocation_id == (
        fixture.pending.execution_attempt_id
    )
    assert second.firewall.invocation_id == second_pending.execution_attempt_id
    assert first.firewall._state is not second.firewall._state
    assert first.request.idempotency_key == second.request.idempotency_key
    state_after = acp.derive_action_packet_lifecycle_state_v01(
        retry_registry,
        packet_id=packet_id,
    )
    assert state_after.idempotency_disposition == "RESERVED"
    assert state_after.reservation_owner_packet_id == packet_id
    old_decision = effect_firewall.authorize_effect_request_v01(
        firewall=first.firewall,
        request=second.request,
        current_tick=second.projection.current_tick,
    )
    assert old_decision.decision != (
        effect_firewall.EFFECT_DECISION_ALLOW_MOCK_EFFECT
    )
    assert first.firewall._state.mock_effect_execution_count == 0
    assert second.firewall._state.mock_effect_execution_count == 0


def test_g2a4a_preparation_preserves_registry_and_all_histories(
    g2a4a_fixture: _G2A4AFixtureV01,
) -> None:
    fixture = g2a4a_fixture
    registry = fixture.registry
    before_bytes = repr(registry).encode("utf-8")
    entries = registry.action_packet_lifecycle_entries
    transitions = entries[0].transition_events
    dispositions = registry.idempotency_disposition_events
    invalidations = registry.action_packet_invalidation_contexts
    genesis = entries[0].root_bound_genesis
    root_result = genesis.root_decision_projection.root_decision_result
    acceptance = genesis.dependency_acceptance_binding
    preparation = acp._prepare_action_packet_effect_attempt_v01(
        registry,
        **_g2a4a_projection_kwargs(fixture),
    )
    assert preparation.decision.real_world_effects_count == 0
    assert repr(registry).encode("utf-8") == before_bytes
    assert registry.action_packet_lifecycle_entries is entries
    assert entries[0].transition_events is transitions
    assert registry.idempotency_disposition_events is dispositions
    assert registry.action_packet_invalidation_contexts is invalidations
    assert entries[0].root_bound_genesis is genesis
    assert genesis.root_decision_projection.root_decision_result is root_result
    assert genesis.dependency_acceptance_binding is acceptance


def test_g2a4a_effect_firewall_projection_matches_every_frozen_field(
    g2a4a_fixture: _G2A4AFixtureV01,
) -> None:
    fixture = g2a4a_fixture
    projection = _g2a4a_projection(fixture)
    canonical = fixture.root_bound.canonical_projection
    root_result = (
        fixture.root_bound.root_decision_projection.root_decision_result
    )
    state = acp.derive_action_packet_lifecycle_state_v01(
        fixture.registry,
        packet_id=fixture.root_bound.packet_identity.packet_id,
    )
    expected = (
        acp.ACTION_PACKET_EFFECT_FIREWALL_PROJECTION_PROFILE_ID_V01,
        fixture.root_bound.packet_identity.packet_id,
        fixture.registry.registry_id,
        fixture.pending.transition_event_id,
        fixture.pending.execution_attempt_id,
        fixture.corridor.corridor_id,
        fixture.corridor_step.step_id,
        canonical.adapter_binding.corridor_class,
        canonical.transaction_id,
        canonical.owning_local_root_id,
        root_result.decision_id,
        canonical.authorization_candidate
        .root_packet_authorization_candidate_id,
        canonical.canonical_permission_ref,
        canonical.normalized_permission_scope.allowed_adapter_ids,
        canonical.normalized_permission_scope.allowed_action_classes,
        (
            canonical.normalized_subject_scope.included_subject_refs
            + canonical.normalized_target_scope.included_target_refs
        ),
        canonical.temporal_authority.expires_at_utc
        - fixture.logical_time_bridge.origin_utc_epoch_seconds,
        "ActionCommitPacket",
        canonical.adapter_binding.adapter_id,
        canonical.selected_canonical_action,
        (
            canonical.normalized_subject_scope.included_subject_refs
            + canonical.normalized_target_scope.included_target_refs
        ),
        canonical.temporal_authority.issued_at_utc
        - fixture.logical_time_bridge.origin_utc_epoch_seconds,
        canonical.temporal_authority.expires_at_utc
        - fixture.logical_time_bridge.origin_utc_epoch_seconds,
        fixture.eligibility_evaluation_time
        - fixture.logical_time_bridge.origin_utc_epoch_seconds,
        canonical.idempotency_identity.idempotency_key,
        True,
        effect_firewall.EFFECT_ACCESS_OWNER,
        fixture.logical_time_bridge.bridge_id,
        fixture.pending.evaluation_time,
        fixture.pending.evaluation_time_source,
        fixture.pending.evaluation_context_id,
        fixture.eligibility_evaluation_time,
        fixture.eligibility_evaluation_time_source,
        fixture.eligibility_evaluation_context_id,
        state.latest_disposition_event_id,
        fixture.root_bound.dependency_acceptance_binding
        .packet_dependency_acceptance_binding_id,
        tuple(item.observation_id for item in fixture.observations),
        canonical.authority_policy_fingerprint,
        canonical.temporal_authority_fingerprint,
    )
    assert len(fields(projection)) == 39
    assert tuple(getattr(projection, item.name) for item in fields(projection)) == (
        expected
    )
    assert acp.validate_action_packet_effect_firewall_projection_v01(
        projection,
        fixture.registry,
        **_g2a4a_projection_kwargs(fixture),
    ) == (True, ())


def test_g2a4a_projection_builds_valid_frozen_firewall_and_request(
    g2a4a_fixture: _G2A4AFixtureV01,
) -> None:
    fixture = g2a4a_fixture
    preparation = acp._prepare_action_packet_effect_attempt_v01(
        fixture.registry,
        **_g2a4a_projection_kwargs(fixture),
    )
    projection = preparation.projection
    firewall = preparation.firewall
    request = preparation.request
    assert effect_firewall.validate_effect_firewall_v01(firewall) == ()
    assert effect_firewall.validate_effect_request_v01(request) == ()
    rebuilt_firewall = effect_firewall.build_effect_firewall_v01(
        root_decision_kernel=(
            fixture.root_bound.root_decision_projection
            .root_decision_kernel
        ),
        decision_input=(
            fixture.root_bound.root_decision_projection.root_decision_input
        ),
        root_decision_result=(
            fixture.root_bound.root_decision_projection
            .root_decision_result
        ),
        invocation_id=projection.execution_attempt_id,
        allowed_adapter_ids=projection.allowed_adapter_ids,
        allowed_action_kinds=projection.allowed_action_kinds,
        root_scope_refs=projection.root_scope_refs,
        maximum_expires_at_tick=projection.maximum_expires_at_tick,
    )
    rebuilt_request = effect_firewall.build_effect_request_v01(
        root_decision_kernel=(
            fixture.root_bound.root_decision_projection
            .root_decision_kernel
        ),
        decision_input=(
            fixture.root_bound.root_decision_projection.root_decision_input
        ),
        root_decision_result=(
            fixture.root_bound.root_decision_projection
            .root_decision_result
        ),
        request_kind=projection.request_kind,
        adapter_id=projection.adapter_id,
        action_kind=projection.action_kind,
        scope_refs=projection.scope_refs,
        issued_at_tick=projection.issued_at_tick,
        expires_at_tick=projection.expires_at_tick,
        idempotency_key=projection.idempotency_key,
    )
    assert firewall.firewall_id == rebuilt_firewall.firewall_id
    assert request.request_id == rebuilt_request.request_id
    assert firewall.invocation_id == projection.execution_attempt_id
    assert (
        firewall.transaction_id,
        firewall.target_root_id,
        firewall.root_decision_id,
        firewall.selected_candidate_id,
        firewall.permission_ref,
        firewall.allowed_adapter_ids,
        firewall.allowed_action_kinds,
        firewall.root_scope_refs,
        firewall.maximum_expires_at_tick,
        firewall.mock_only,
        firewall.effect_access_owner,
    ) == (
        projection.transaction_id,
        projection.target_root_id,
        projection.root_decision_id,
        projection.selected_candidate_id,
        projection.permission_ref,
        projection.allowed_adapter_ids,
        projection.allowed_action_kinds,
        projection.root_scope_refs,
        projection.maximum_expires_at_tick,
        True,
        effect_firewall.EFFECT_ACCESS_OWNER,
    )
    assert (
        request.request_kind,
        request.adapter_id,
        request.action_kind,
        request.scope_refs,
        request.issued_at_tick,
        request.expires_at_tick,
        request.idempotency_key,
        request.mock_only,
    ) == (
        "ActionCommitPacket",
        projection.adapter_id,
        projection.action_kind,
        projection.root_scope_refs,
        projection.issued_at_tick,
        projection.expires_at_tick,
        projection.idempotency_key,
        True,
    )


def test_g2a4a_projection_rejects_every_field_drift(
    g2a4a_fixture: _G2A4AFixtureV01,
) -> None:
    fixture = g2a4a_fixture
    projection = _g2a4a_projection(fixture)
    for field in fields(projection):
        value = getattr(projection, field.name)
        if type(value) is str:
            changed: object = value + ":drift"
        elif type(value) is tuple:
            changed = value + ("scope:drift",)
        elif type(value) is int:
            changed = value + 1
        else:
            assert type(value) is bool
            changed = not value
        forged = replace(projection, **{field.name: changed})
        valid, reasons = (
            acp.validate_action_packet_effect_firewall_projection_v01(
                forged,
                fixture.registry,
                **_g2a4a_projection_kwargs(fixture),
            )
        )
        assert valid is False, field.name
        assert reasons == ("action_packet_effect_projection_mismatch",), (
            field.name,
            reasons,
        )


def test_g2a4a_corridor_legacy_and_canonical_containment_are_independent(
    g2a4a_fixture: _G2A4AFixtureV01,
) -> None:
    fixture = g2a4a_fixture
    assert _g2a4a_projection(fixture)
    step = fixture.corridor_step
    corridor = fixture.corridor
    failures = (
        {"corridor_step": replace(step, allowed_actions=())},
        {
            "corridor": replace(
                corridor,
                allowed_steps=("corridor_step:other",),
            )
        },
        {
            "corridor": replace(
                corridor,
                allowed_steps=(step.step_id, step.step_id),
            )
        },
        {"corridor": replace(corridor, corridor_kind="corridor:other")},
        {
            "corridor_step": replace(
                step,
                adapter_id=acp.ADAPTER_REAL_BANK,
            )
        },
        {
            "corridor_step": replace(
                step,
                allowed_actions=(acp.ACTION_REAL_PAYMENT,),
            )
        },
        {
            "corridor_step": replace(
                step,
                parent_packet_id="acp_v02:" + "1" * 64,
            )
        },
    )
    for changes in failures:
        with pytest.raises(ValueError):
            _g2a4a_projection(fixture, **changes)

    duplicate_scope_fixture = _g2a4a_fixture_value(
        allowed_subjects=(acp.SUBJECT_SUPPLIER_A,),
    )
    with pytest.raises(
        ValueError,
        match="action_packet_effect_scope_invalid",
    ):
        _g2a4a_projection(duplicate_scope_fixture)


def test_g2a4a_firewall_authorization_issues_private_capability_only(
    g2a4a_fixture: _G2A4AFixtureV01,
) -> None:
    preparation = acp._prepare_action_packet_effect_attempt_v01(
        g2a4a_fixture.registry,
        **_g2a4a_projection_kwargs(g2a4a_fixture),
    )
    decision = preparation.decision
    assert decision.decision == effect_firewall.EFFECT_DECISION_ALLOW_MOCK_EFFECT
    assert decision.reason_code == "mock_effect_authorized"
    assert decision.capability_issued is True
    assert decision.return_to_root is False
    assert decision.real_world_effects_count == 0
    assert not hasattr(preparation, "capability")
    assert type(decision).__name__ == "EffectFirewallDecisionV01"
    with pytest.raises(TypeError):
        copy.copy(preparation.firewall)
    with pytest.raises(TypeError):
        copy.deepcopy(preparation.firewall)
    with pytest.raises(TypeError):
        pickle.dumps(preparation.firewall)
    assert preparation.firewall._state.mock_effect_execution_count == 0
    assert preparation.firewall._state.terminal_receipt_ids == set()
    assert not hasattr(acp, "EffectCapabilityV01")


def test_g2a4a_failed_eligibility_never_reaches_firewall(
    g2a4a_fixture: _G2A4AFixtureV01,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = g2a4a_fixture
    calls = {"firewall": 0, "request": 0, "authorize": 0}
    original_firewall = acp._build_effect_firewall_v01
    original_request = acp._build_effect_request_v01
    original_authorize = acp._authorize_effect_request_v01

    @wraps(original_firewall)
    def counted_firewall(**kwargs: object) -> object:
        calls["firewall"] += 1
        return original_firewall(**kwargs)

    @wraps(original_request)
    def counted_request(**kwargs: object) -> object:
        calls["request"] += 1
        return original_request(**kwargs)

    @wraps(original_authorize)
    def counted_authorize(**kwargs: object) -> object:
        calls["authorize"] += 1
        return original_authorize(**kwargs)

    monkeypatch.setattr(acp, "_build_effect_firewall_v01", counted_firewall)
    monkeypatch.setattr(acp, "_build_effect_request_v01", counted_request)
    monkeypatch.setattr(acp, "_authorize_effect_request_v01", counted_authorize)
    bad_observation = replace(
        fixture.observations[0],
        observed_content_sha256="e" * 64,
    )
    failures = (
        {"packet_id": "acp_v02:" + "9" * 64},
        {"current_dependency_observations": ()},
        {"current_dependency_observations": (bad_observation,)},
        {
            "corridor": replace(
                fixture.corridor,
                packet_id="acp_v02:" + "8" * 64,
            )
        },
        {
            "eligibility_evaluation_time": (
                fixture.root_bound.canonical_projection
                .temporal_authority.expires_at_utc
            )
        },
    )
    for changes in failures:
        with pytest.raises(ValueError):
            acp._prepare_action_packet_effect_attempt_v01(
                fixture.registry,
                **_g2a4a_projection_kwargs(fixture, **changes),
            )
        assert calls == {"firewall": 0, "request": 0, "authorize": 0}


def test_g2a4a_projection_rejects_unrepresentable_logical_time(
    g2a4a_fixture: _G2A4AFixtureV01,
) -> None:
    fixture = g2a4a_fixture
    canonical = fixture.root_bound.canonical_projection
    issued = canonical.temporal_authority.issued_at_utc
    cases = (
        acp.build_logical_time_bridge_v01(
            origin_utc_epoch_seconds=issued + 1,
            seconds_per_tick=1,
            bridge_policy_version="g2a4a_wrong_origin_v01",
        ),
        acp.build_logical_time_bridge_v01(
            origin_utc_epoch_seconds=issued,
            seconds_per_tick=7,
            bridge_policy_version="g2a4a_nondivisible_v01",
        ),
        replace(
            fixture.logical_time_bridge,
            bridge_id="0" * 64,
        ),
    )
    for bridge in cases:
        with pytest.raises(ValueError):
            _g2a4a_projection(fixture, logical_time_bridge=bridge)
    for evaluation_time in (
        True,
        canonical.temporal_authority.expires_at_utc,
    ):
        with pytest.raises(ValueError):
            _g2a4a_projection(
                fixture,
                eligibility_evaluation_time=evaluation_time,
            )
    overflow_bridge = acp.build_logical_time_bridge_v01(
        origin_utc_epoch_seconds=-(2**63),
        seconds_per_tick=2**62,
        bridge_policy_version="g2a4a_overflow_v01",
    )
    with pytest.raises(ValueError):
        _g2a4a_projection(fixture, logical_time_bridge=overflow_bridge)


def test_g2a4a_dependency_time_envelope_commitment_binds_exact_interval(
    g2a4a_fixture: _G2A4AFixtureV01,
) -> None:
    observation = g2a4a_fixture.observations[0]
    values: dict[str, object] = {
        "dependency_id": observation.dependency_id,
        "evidence_ref": observation.evidence_ref,
        "content_sha256": observation.observed_content_sha256,
        "freshness_policy_id": observation.freshness_policy_id,
        "source_provenance_refs": observation.source_provenance_refs,
        "valid_from_utc": observation.valid_from_utc,
        "valid_to_utc": observation.valid_to_utc,
    }
    material = (
        acp.action_dependency_time_envelope_commitment_material_v01(
            **values
        )
    )
    assert tuple(name for name, _ in material) == (
        "profile_id",
        "dependency_id",
        "evidence_ref",
        "content_sha256",
        "freshness_policy_id",
        "source_provenance_refs",
        "valid_from_utc",
        "valid_to_utc",
    )
    assert len(material) == 8
    assert {
        "packet_id",
        "source_root_decision_id",
        "source_root_decision_hash",
        "observation_id",
        "observed_at_utc",
        "observation_context_id",
        "evaluation_context_id",
    }.isdisjoint(name for name, _ in material)
    expected = acp.build_domain_separated_identity_v01(
        domain=(
            acp.ACTION_DEPENDENCY_TIME_ENVELOPE_COMMITMENT_DOMAIN_V01
        ),
        prefix=(
            acp.ACTION_DEPENDENCY_TIME_ENVELOPE_COMMITMENT_PREFIX_V01
        ),
        material=material,
    )
    assert observation.time_envelope_id == expected
    assert acp.validate_action_dependency_time_envelope_binding_v01(
        expected,
        **values,
    ) == (True, ())

    for changed in (
        {"dependency_id": "dependency:other"},
        {"evidence_ref": "evidence:other"},
        {"content_sha256": "f" * 64},
        {"freshness_policy_id": "freshness_policy:other"},
        {"source_provenance_refs": ("source:other",)},
        {"valid_from_utc": observation.valid_from_utc + 1},
        {"valid_to_utc": observation.valid_to_utc - 1},
    ):
        changed_values = dict(values)
        changed_values.update(changed)
        changed_id = acp.build_action_dependency_time_envelope_id_v01(
            **changed_values
        )
        assert changed_id != expected
        assert (
            acp.validate_action_dependency_time_envelope_binding_v01(
                expected,
                **changed_values,
            )[0]
            is False
        )

    for invalid in (
        {"valid_from_utc": True},
        {"valid_to_utc": False},
        {
            "valid_from_utc": observation.valid_to_utc,
            "valid_to_utc": observation.valid_to_utc,
        },
        {
            "valid_from_utc": observation.valid_to_utc + 1,
            "valid_to_utc": observation.valid_to_utc,
        },
    ):
        invalid_values = dict(values)
        invalid_values.update(invalid)
        with pytest.raises(
            ValueError,
            match="dependency_time_envelope_commitment_invalid",
        ):
            acp.build_action_dependency_time_envelope_id_v01(
                **invalid_values
            )


def test_g2a4a_reused_time_envelope_id_cannot_extend_current_freshness(
    g2a4a_fixture: _G2A4AFixtureV01,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = g2a4a_fixture
    observation = fixture.observations[0]
    registry_bytes = repr(fixture.registry).encode("utf-8")
    calls = {"firewall": 0, "request": 0, "authorize": 0}
    original_firewall = acp._build_effect_firewall_v01
    original_request = acp._build_effect_request_v01
    original_authorize = acp._authorize_effect_request_v01

    @wraps(original_firewall)
    def counted_firewall(**kwargs: object) -> object:
        calls["firewall"] += 1
        return original_firewall(**kwargs)

    @wraps(original_request)
    def counted_request(**kwargs: object) -> object:
        calls["request"] += 1
        return original_request(**kwargs)

    @wraps(original_authorize)
    def counted_authorize(**kwargs: object) -> object:
        calls["authorize"] += 1
        return original_authorize(**kwargs)

    monkeypatch.setattr(acp, "_build_effect_firewall_v01", counted_firewall)
    monkeypatch.setattr(acp, "_build_effect_request_v01", counted_request)
    monkeypatch.setattr(acp, "_authorize_effect_request_v01", counted_authorize)

    assert _g2a4a_projection(fixture)
    assert _g2a4a_projection(
        fixture,
        eligibility_evaluation_time=observation.valid_to_utc - 1,
    )
    with pytest.raises(ValueError):
        _g2a4a_projection(
            fixture,
            eligibility_evaluation_time=observation.valid_to_utc,
        )

    forged_observations = []
    for extension in (1, 1_000_000):
        provisional = replace(
            observation,
            valid_to_utc=observation.valid_to_utc + extension,
            observation_id="",
        )
        forged_observations.append(
            replace(
                provisional,
                observation_id=acp.build_domain_separated_identity_v01(
                    domain=(
                        acp.ACTION_DEPENDENCY_CURRENT_OBSERVATION_DOMAIN_V01
                    ),
                    prefix=(
                        acp.ACTION_DEPENDENCY_CURRENT_OBSERVATION_PREFIX_V01
                    ),
                    material=(
                        acp.action_dependency_current_observation_material_v01(
                            provisional
                        )
                    ),
                ),
            )
        )
    for forged in forged_observations:
        assert acp.validate_action_dependency_current_observation_v01(
            forged
        )[0] is False
        with pytest.raises(ValueError):
            acp._prepare_action_packet_effect_attempt_v01(
                fixture.registry,
                **_g2a4a_projection_kwargs(
                    fixture,
                    current_dependency_observations=(forged,),
                ),
            )

    extended_valid_to = observation.valid_to_utc + 1_000_000
    new_envelope = acp.build_action_dependency_time_envelope_id_v01(
        dependency_id=observation.dependency_id,
        evidence_ref=observation.evidence_ref,
        content_sha256=observation.observed_content_sha256,
        freshness_policy_id=observation.freshness_policy_id,
        source_provenance_refs=observation.source_provenance_refs,
        valid_from_utc=observation.valid_from_utc,
        valid_to_utc=extended_valid_to,
    )
    assert new_envelope != observation.time_envelope_id
    self_consistent = acp.build_action_dependency_current_observation_v01(
        dependency_id=observation.dependency_id,
        evidence_ref=observation.evidence_ref,
        observed_content_sha256=observation.observed_content_sha256,
        time_envelope_id=new_envelope,
        freshness_policy_id=observation.freshness_policy_id,
        source_provenance_refs=observation.source_provenance_refs,
        valid_from_utc=observation.valid_from_utc,
        valid_to_utc=extended_valid_to,
        observed_at_utc=observation.observed_at_utc,
        observation_context_id=observation.observation_context_id,
    )
    assert acp.validate_action_dependency_current_observation_v01(
        self_consistent
    ) == (True, ())
    with pytest.raises(ValueError):
        acp._prepare_action_packet_effect_attempt_v01(
            fixture.registry,
            **_g2a4a_projection_kwargs(
                fixture,
                current_dependency_observations=(self_consistent,),
            ),
        )
    assert calls == {"firewall": 0, "request": 0, "authorize": 0}
    assert repr(fixture.registry).encode("utf-8") == registry_bytes


def test_g2a4a_projection_builder_is_closed_under_its_validator(
    g2a4a_fixture: _G2A4AFixtureV01,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = g2a4a_fixture
    projection = _g2a4a_projection(fixture)
    assert acp.validate_action_packet_effect_firewall_projection_v01(
        projection,
        fixture.registry,
        **_g2a4a_projection_kwargs(fixture),
    ) == (True, ())
    assert acp.validate_action_packet_effect_firewall_projection_v01(
        replace(projection, registry_id=""),
        fixture.registry,
        **_g2a4a_projection_kwargs(fixture),
    )[0] is False

    calls = {"registry": 0, "firewall": 0}
    original_registry = acp._validate_action_commit_packet_registry_core_v02
    original_firewall = acp._build_effect_firewall_v01

    @wraps(original_registry)
    def counted_registry(registry: object) -> object:
        calls["registry"] += 1
        return original_registry(registry)

    @wraps(original_firewall)
    def counted_firewall(**kwargs: object) -> object:
        calls["firewall"] += 1
        return original_firewall(**kwargs)

    monkeypatch.setattr(
        acp,
        "_validate_action_commit_packet_registry_core_v02",
        counted_registry,
    )
    monkeypatch.setattr(acp, "_build_effect_firewall_v01", counted_firewall)

    calls.update(registry=0, firewall=0)
    preparation = acp._prepare_action_packet_effect_attempt_v01(
        fixture.registry,
        **_g2a4a_projection_kwargs(fixture),
    )
    assert preparation.projection == projection
    assert calls == {"registry": 1, "firewall": 1}

    malformed_contexts = (
        (
            replace(fixture.registry, registry_id=""),
            fixture.corridor,
            "action_packet_effect_registry_id_invalid",
        ),
        (
            replace(fixture.registry, registry_id="   "),
            fixture.corridor,
            "action_packet_effect_registry_id_invalid",
        ),
        (
            fixture.registry,
            replace(fixture.corridor, corridor_id=""),
            "action_packet_effect_corridor_id_invalid",
        ),
        (
            fixture.registry,
            replace(fixture.corridor, corridor_id="   "),
            "action_packet_effect_corridor_id_invalid",
        ),
        (
            fixture.registry,
            replace(fixture.corridor, corridor_id="e\u0301"),
            "action_packet_effect_corridor_id_invalid",
        ),
    )
    for registry, corridor, reason in malformed_contexts:
        calls.update(registry=0, firewall=0)
        with pytest.raises(ValueError, match=reason):
            acp.build_action_packet_effect_firewall_projection_v01(
                registry,
                **_g2a4a_projection_kwargs(
                    fixture,
                    corridor=corridor,
                ),
            )
        assert calls == {"registry": 1, "firewall": 0}
        calls.update(registry=0, firewall=0)
        with pytest.raises(ValueError, match=reason):
            acp._prepare_action_packet_effect_attempt_v01(
                registry,
                **_g2a4a_projection_kwargs(
                    fixture,
                    corridor=corridor,
                ),
            )
        assert calls == {"registry": 1, "firewall": 0}


def _g2a4b_execute(
    fixture: _G2A4AFixtureV01,
    registry: acp.ActionCommitPacketRegistryV02 | None = None,
    **changes: object,
) -> acp.ActionCommitPacketRegistryV02:
    return acp.execute_action_packet_mock_fulfillment_v01(
        fixture.registry if registry is None else registry,
        action_packet_transition_registry_profile=_g2a2a_registry(),
        **_g2a4a_projection_kwargs(fixture, **changes),
    )


def _g2a4b_entry(
    registry: acp.ActionCommitPacketRegistryV02,
    packet_id: str,
) -> acp.ActionPacketLifecycleEntryV01:
    matching = tuple(
        entry
        for entry in registry.action_packet_lifecycle_entries
        if entry.root_bound_genesis.packet_identity.packet_id == packet_id
    )
    assert len(matching) == 1
    return matching[0]


def _g2a4b_observations_for_context(
    observations: tuple[acp.ActionDependencyCurrentObservationV01, ...],
    context_id: str,
) -> tuple[acp.ActionDependencyCurrentObservationV01, ...]:
    return tuple(
        acp.build_action_dependency_current_observation_v01(
            dependency_id=observation.dependency_id,
            evidence_ref=observation.evidence_ref,
            observed_content_sha256=observation.observed_content_sha256,
            time_envelope_id=observation.time_envelope_id,
            freshness_policy_id=observation.freshness_policy_id,
            source_provenance_refs=observation.source_provenance_refs,
            valid_from_utc=observation.valid_from_utc,
            valid_to_utc=observation.valid_to_utc,
            observed_at_utc=observation.observed_at_utc,
            observation_context_id=context_id,
        )
        for observation in observations
    )


def _g2a4b_evidence_kwargs(
    evidence: acp.ActionPacketFulfillmentAttemptEvidenceV01,
    **changes: object,
) -> dict[str, object]:
    values = {
        field.name: getattr(evidence, field.name)
        for field in fields(evidence)
        if field.name not in {"evidence_profile_id", "attempt_evidence_id"}
    }
    values.update(changes)
    return values


def test_g2a4b_fulfillment_attempt_evidence_identity_and_branch_invariants(
    g2a4a_fixture: _G2A4AFixtureV01,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = g2a4a_fixture
    original_execute = acp._execute_mock_effect_v01
    original_authorize = acp._authorize_effect_request_v01

    preblocked = _g2a4b_execute(
        fixture,
        current_dependency_observations=(),
    ).action_packet_fulfillment_attempt_contexts[-1].attempt_evidence

    @wraps(original_authorize)
    def blocked_authorize(**kwargs: object) -> object:
        request = kwargs["request"]
        return original_authorize(
            firewall=kwargs["firewall"],
            request=request,
            current_tick=request.expires_at_tick,
        )

    monkeypatch.setattr(
        acp,
        "_authorize_effect_request_v01",
        blocked_authorize,
    )
    firewall_blocked = _g2a4b_execute(
        fixture
    ).action_packet_fulfillment_attempt_contexts[-1].attempt_evidence
    monkeypatch.setattr(
        acp,
        "_authorize_effect_request_v01",
        original_authorize,
    )
    consumed = _g2a4b_execute(
        fixture
    ).action_packet_fulfillment_attempt_contexts[-1].attempt_evidence

    @wraps(original_execute)
    def nonconsuming_execute(**kwargs: object) -> object:
        raise ValueError("effect_request_expired")

    monkeypatch.setattr(
        acp,
        "_execute_mock_effect_v01",
        nonconsuming_execute,
    )
    nonconsuming = _g2a4b_execute(
        fixture
    ).action_packet_fulfillment_attempt_contexts[-1].attempt_evidence

    @wraps(original_execute)
    def uncertain_execute(**kwargs: object) -> object:
        raise RuntimeError("controlled_uncertain")

    monkeypatch.setattr(
        acp,
        "_execute_mock_effect_v01",
        uncertain_execute,
    )
    uncertain = _g2a4b_execute(
        fixture
    ).action_packet_fulfillment_attempt_contexts[-1].attempt_evidence

    samples = (
        preblocked,
        firewall_blocked,
        consumed,
        nonconsuming,
        uncertain,
    )
    assert len(fields(acp.ActionPacketFulfillmentAttemptEvidenceV01)) == 38
    material_names = tuple(
        name
        for name, _ in (
            acp.action_packet_fulfillment_attempt_evidence_material_v01(
                consumed
            )
        )
    )
    assert len(material_names) == 37
    assert material_names == tuple(
        field.name
        for field in fields(acp.ActionPacketFulfillmentAttemptEvidenceV01)
        if field.name != "attempt_evidence_id"
    )
    assert preblocked.projection_sha256 is None
    assert dict(
        acp.action_packet_fulfillment_attempt_evidence_material_v01(
            preblocked
        )
    )["projection_sha256"] == acp.ABSENT_V01
    assert tuple(item.outcome_class for item in samples) == (
        "PRE_FULFILLMENT_BLOCKED",
        "FIREWALL_BLOCKED",
        "CONSUMED",
        "NOT_CONSUMED",
        "UNCERTAIN",
    )
    for evidence in samples:
        assert acp.validate_action_packet_fulfillment_attempt_evidence_v01(
            evidence
        ) == (True, ())
        assert evidence.attempt_evidence_id.startswith(
            acp.ACTION_PACKET_FULFILLMENT_ATTEMPT_EVIDENCE_PREFIX_V01
        )
        rebuilt = acp.build_action_packet_fulfillment_attempt_evidence_v01(
            **_g2a4b_evidence_kwargs(evidence)
        )
        assert rebuilt == evidence
    assert consumed.attempt_observation_ordinal == 1
    for forged in (
        replace(consumed, adapter_invoked=False),
        replace(nonconsuming, receipt_ref="receipt:forged"),
        replace(preblocked, capability_id="f" * 64),
        replace(consumed, attempt_observation_ordinal=True),
    ):
        valid, reasons = (
            acp.validate_action_packet_fulfillment_attempt_evidence_v01(
                forged
            )
        )
        assert valid is False
        assert reasons

    class EqualText(str):
        def __eq__(self, other: object) -> bool:
            return True

    custom_equal = replace(consumed, reason_code=EqualText("mock_effect_consumed"))
    assert acp.validate_action_packet_fulfillment_attempt_evidence_v01(
        custom_equal
    )[0] is False


def test_g2a4b_pre_adapter_failure_appends_evidence_without_invocation(
    g2a4a_fixture: _G2A4AFixtureV01,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = g2a4a_fixture
    packet_id = fixture.root_bound.packet_identity.packet_id
    source_entry = _g2a4b_entry(fixture.registry, packet_id)
    source_dispositions = fixture.registry.idempotency_disposition_events
    calls = {"firewall": 0, "execute": 0}
    original_firewall = acp._build_effect_firewall_v01
    original_execute = acp._execute_mock_effect_v01

    @wraps(original_firewall)
    def counted_firewall(**kwargs: object) -> object:
        calls["firewall"] += 1
        return original_firewall(**kwargs)

    @wraps(original_execute)
    def counted_execute(**kwargs: object) -> object:
        calls["execute"] += 1
        return original_execute(**kwargs)

    monkeypatch.setattr(acp, "_build_effect_firewall_v01", counted_firewall)
    monkeypatch.setattr(acp, "_execute_mock_effect_v01", counted_execute)

    missing = _g2a4b_execute(
        fixture,
        current_dependency_observations=(),
    )
    missing_context = missing.action_packet_fulfillment_attempt_contexts[-1]
    assert missing_context.attempt_evidence.outcome_class == (
        "PRE_FULFILLMENT_BLOCKED"
    )
    assert missing_context.attempt_evidence.adapter_call_count == 0
    assert missing_context.projection is None
    assert missing_context.receipt is None
    assert _g2a4b_entry(missing, packet_id).transition_events == (
        source_entry.transition_events
    )
    assert missing.idempotency_disposition_events is source_dispositions

    at_expiry_context = "evaluation_context:g2a4b:expiry"
    at_expiry_observations = _g2a4b_observations_for_context(
        fixture.observations,
        at_expiry_context,
    )
    at_expiry = _g2a4b_execute(
        fixture,
        eligibility_evaluation_time=(
            fixture.root_bound.canonical_projection.temporal_authority
            .expires_at_utc
        ),
        eligibility_evaluation_context_id=at_expiry_context,
        current_dependency_observations=at_expiry_observations,
    )
    assert at_expiry.action_packet_fulfillment_attempt_contexts[
        -1
    ].attempt_evidence.outcome_class == "PRE_FULFILLMENT_BLOCKED"

    wrong_corridor = _g2a4b_execute(
        fixture,
        corridor=replace(fixture.corridor, allowed_steps=()),
    )
    assert wrong_corridor.action_packet_fulfillment_attempt_contexts[
        -1
    ].attempt_evidence.outcome_class == "PRE_FULFILLMENT_BLOCKED"
    assert calls == {"firewall": 0, "execute": 0}

    retry_context = "evaluation_context:g2a4b:fresh_after_block"
    fresh_observations = _g2a4b_observations_for_context(
        fixture.observations,
        retry_context,
    )
    completed = _g2a4b_execute(
        fixture,
        missing,
        current_dependency_observations=fresh_observations,
        eligibility_evaluation_context_id=retry_context,
    )
    assert tuple(
        context.attempt_evidence.outcome_class
        for context in completed.action_packet_fulfillment_attempt_contexts
    ) == ("PRE_FULFILLMENT_BLOCKED", "CONSUMED")
    assert calls == {"firewall": 2, "execute": 1}
    with pytest.raises(ValueError, match="observation_duplicate"):
        _g2a4b_execute(
            fixture,
            missing,
            current_dependency_observations=(),
        )


def test_g2a4b_firewall_block_appends_evidence_and_never_invokes_effect(
    g2a4a_fixture: _G2A4AFixtureV01,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = g2a4a_fixture
    packet_id = fixture.root_bound.packet_identity.packet_id
    source_entry = _g2a4b_entry(fixture.registry, packet_id)
    calls = {"authorize": 0, "execute": 0}
    original_authorize = acp._authorize_effect_request_v01
    original_execute = acp._execute_mock_effect_v01

    @wraps(original_authorize)
    def blocked_authorize(**kwargs: object) -> object:
        calls["authorize"] += 1
        request = kwargs["request"]
        return original_authorize(
            firewall=kwargs["firewall"],
            request=request,
            current_tick=request.expires_at_tick,
        )

    @wraps(original_execute)
    def counted_execute(**kwargs: object) -> object:
        calls["execute"] += 1
        return original_execute(**kwargs)

    monkeypatch.setattr(
        acp,
        "_authorize_effect_request_v01",
        blocked_authorize,
    )
    monkeypatch.setattr(acp, "_execute_mock_effect_v01", counted_execute)
    result = _g2a4b_execute(fixture)
    assert calls["execute"] == 0
    assert calls["authorize"] >= 2
    assert acp.validate_action_commit_packet_registry_v02(result) == (True, ())
    context = result.action_packet_fulfillment_attempt_contexts[-1]
    evidence = context.attempt_evidence
    assert evidence.outcome_class == "FIREWALL_BLOCKED"
    assert evidence.capability_id is None
    assert evidence.adapter_invoked is False
    assert context.projection is not None
    assert context.request is not None
    assert context.decision is not None
    assert context.decision.decision == (
        effect_firewall.EFFECT_DECISION_BLOCKED_FAIL_CLOSED
    )
    assert context.receipt is None
    assert _g2a4b_entry(result, packet_id).transition_events == (
        source_entry.transition_events
    )
    assert result.idempotency_disposition_events is (
        fixture.registry.idempotency_disposition_events
    )


def test_g2a4b_consumed_branch_invokes_once_and_atomically_records_t04_consume(
    g2a4a_fixture: _G2A4AFixtureV01,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = g2a4a_fixture
    packet_id = fixture.root_bound.packet_identity.packet_id
    calls = {"execute": 0, "source": 0, "proposed": 0}
    original_execute = acp._execute_mock_effect_v01
    original_validate = acp._validate_action_commit_packet_registry_core_v02

    @wraps(original_execute)
    def counted_execute(**kwargs: object) -> object:
        calls["execute"] += 1
        return original_execute(**kwargs)

    @wraps(original_validate)
    def counted_validate(registry: object) -> object:
        if registry is fixture.registry:
            calls["source"] += 1
        else:
            calls["proposed"] += 1
        return original_validate(registry)

    monkeypatch.setattr(acp, "_execute_mock_effect_v01", counted_execute)
    monkeypatch.setattr(
        acp,
        "_validate_action_commit_packet_registry_core_v02",
        counted_validate,
    )
    result = _g2a4b_execute(fixture)
    assert calls == {"execute": 1, "source": 1, "proposed": 1}
    assert acp.validate_action_commit_packet_registry_v02(result) == (True, ())
    assert len(result.action_packet_fulfillment_attempt_contexts) == 1
    context = result.action_packet_fulfillment_attempt_contexts[0]
    evidence = context.attempt_evidence
    assert evidence.outcome_class == "CONSUMED"
    assert evidence.adapter_call_count == 1
    assert context.receipt is not None
    assert acp.validate_action_packet_fulfillment_attempt_evidence_v01(
        evidence
    ) == (True, ())
    entry = _g2a4b_entry(result, packet_id)
    assert entry.transition_events[-1].transition_rule_id == (
        "g2a_t04_fulfill_mock"
    )
    assert (
        entry.transition_events[-1].execution_attempt_id
        == fixture.pending.execution_attempt_id
    )
    assert result.idempotency_disposition_events[-1].event_class == "CONSUME"
    state = acp.derive_action_packet_lifecycle_state_v01(
        result,
        packet_id=packet_id,
    )
    assert state.lifecycle_state == "FULFILLED_MOCK"
    assert state.idempotency_disposition == "CONSUMED"
    assert state.reservation_owner_packet_id == packet_id
    assert all(
        event.transition_rule_id != "g2a_t05_receipt"
        for event in entry.transition_events
    )
    with pytest.raises(ValueError):
        _g2a4b_execute(fixture, result)
    assert calls["execute"] == 1


def test_g2a4b_receipt_observation_atomically_records_t05_receipt_confirm(
    g2a4a_fixture: _G2A4AFixtureV01,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = g2a4a_fixture
    packet_id = fixture.root_bound.packet_identity.packet_id
    consumed = _g2a4b_execute(fixture)
    context = consumed.action_packet_fulfillment_attempt_contexts[0]
    assert context.receipt is not None
    assert effect_firewall.validate_effect_receipt_v01(
        firewall=acp._build_effect_firewall_v01(
            root_decision_kernel=(
                fixture.root_bound.root_decision_projection.root_decision_kernel
            ),
            decision_input=(
                fixture.root_bound.root_decision_projection.root_decision_input
            ),
            root_decision_result=(
                fixture.root_bound.root_decision_projection.root_decision_result
            ),
            invocation_id=context.projection.execution_attempt_id,
            allowed_adapter_ids=context.projection.allowed_adapter_ids,
            allowed_action_kinds=context.projection.allowed_action_kinds,
            root_scope_refs=context.projection.root_scope_refs,
            maximum_expires_at_tick=(
                context.projection.maximum_expires_at_tick
            ),
        ),
        request=context.request,
        decision=context.decision,
        receipt=context.receipt,
    ) != ()
    calls = {"execute": 0, "source": 0, "proposed": 0}
    original_execute = acp._execute_mock_effect_v01
    original_validate = acp._validate_action_commit_packet_registry_core_v02

    @wraps(original_execute)
    def counted_execute(**kwargs: object) -> object:
        calls["execute"] += 1
        return original_execute(**kwargs)

    @wraps(original_validate)
    def counted_validate(registry: object) -> object:
        if registry is consumed:
            calls["source"] += 1
        else:
            calls["proposed"] += 1
        return original_validate(registry)

    monkeypatch.setattr(acp, "_execute_mock_effect_v01", counted_execute)
    monkeypatch.setattr(
        acp,
        "_validate_action_commit_packet_registry_core_v02",
        counted_validate,
    )
    result = acp.observe_action_packet_effect_receipt_v01(
        consumed,
        packet_id=packet_id,
        attempt_evidence_id=context.attempt_evidence.attempt_evidence_id,
        receipt_evaluation_time=fixture.eligibility_evaluation_time + 1,
        receipt_evaluation_time_source="explicit_g2a4b_receipt_time",
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    assert calls == {"execute": 0, "source": 1, "proposed": 1}
    assert acp.validate_action_commit_packet_registry_v02(result) == (True, ())
    entry = _g2a4b_entry(result, packet_id)
    assert entry.transition_events[-1].transition_rule_id == "g2a_t05_receipt"
    assert entry.transition_events[-1].execution_attempt_id == (
        context.attempt_evidence.execution_attempt_id
    )
    assert entry.transition_events[-1].receipt_ref == context.receipt.artifact_id
    assert result.idempotency_disposition_events[-1].event_class == (
        "RECEIPT_CONFIRM"
    )
    state = acp.derive_action_packet_lifecycle_state_v01(
        result,
        packet_id=packet_id,
    )
    assert state.lifecycle_state == "RECEIPT_RECEIVED"
    assert state.idempotency_disposition == "CONSUMED"
    with pytest.raises(ValueError):
        acp.observe_action_packet_effect_receipt_v01(
            result,
            packet_id=packet_id,
            attempt_evidence_id=context.attempt_evidence.attempt_evidence_id,
            receipt_evaluation_time=fixture.eligibility_evaluation_time + 2,
            receipt_evaluation_time_source="explicit_g2a4b_receipt_time",
            action_packet_transition_registry_profile=_g2a2a_registry(),
        )
    assert calls["execute"] == 0


def test_g2a4b_nonconsuming_branch_preserves_disposition_and_allows_retry(
    g2a4a_fixture: _G2A4AFixtureV01,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = g2a4a_fixture
    packet_id = fixture.root_bound.packet_identity.packet_id
    before_dispositions = fixture.registry.idempotency_disposition_events
    before_bytes = canonical_json_bytes_v01(
        tuple(
            acp.idempotency_disposition_event_material_v01(event)
            for event in before_dispositions
        )
    )
    calls = {"execute": 0}

    @wraps(acp._execute_mock_effect_v01)
    def reject_before_mutation(**kwargs: object) -> object:
        calls["execute"] += 1
        raise ValueError("effect_request_expired")

    monkeypatch.setattr(
        acp,
        "_execute_mock_effect_v01",
        reject_before_mutation,
    )
    result = _g2a4b_execute(fixture)
    assert calls["execute"] == 1
    assert result.idempotency_disposition_events is before_dispositions
    assert canonical_json_bytes_v01(
        tuple(
            acp.idempotency_disposition_event_material_v01(event)
            for event in result.idempotency_disposition_events
        )
    ) == before_bytes
    context = result.action_packet_fulfillment_attempt_contexts[-1]
    evidence = context.attempt_evidence
    assert evidence.outcome_class == "NOT_CONSUMED"
    assert evidence.firewall_state_sha256_before == (
        evidence.firewall_state_sha256_after
    )
    assert context.receipt is None
    entry = _g2a4b_entry(result, packet_id)
    assert entry.transition_events[-1].transition_rule_id == (
        "g2a_t24_nonconsuming_failure"
    )
    state = acp.derive_action_packet_lifecycle_state_v01(
        result,
        packet_id=packet_id,
    )
    assert state.failed_provenance == "FAILED_NON_CONSUMING"
    assert state.idempotency_disposition == "RESERVED"
    assert state.reservation_owner_packet_id == packet_id
    assert state.latest_disposition_event_id == (
        acp.derive_action_packet_lifecycle_state_v01(
            fixture.registry,
            packet_id=packet_id,
        ).latest_disposition_event_id
    )
    retried, _ = _g2a2b_append(result, packet_id, "g2a_t25_retry")
    retried, second_pending = _g2a2b_append(
        retried,
        packet_id,
        "g2a_t03_pending",
        evaluation_context_id="evaluation_context:g2a4b:attempt:2",
    )
    assert second_pending.execution_attempt_id != (
        fixture.pending.execution_attempt_id
    )
    with pytest.raises(ValueError):
        _g2a4b_execute(fixture, result)
    assert calls["execute"] == 1


def test_g2a4b_uncertain_branch_closes_packet_and_key_without_receipt(
    g2a4a_fixture: _G2A4AFixtureV01,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = g2a4a_fixture
    packet_id = fixture.root_bound.packet_identity.packet_id
    calls = {"execute": 0}

    @wraps(acp._execute_mock_effect_v01)
    def unexpected(**kwargs: object) -> object:
        calls["execute"] += 1
        raise RuntimeError("controlled_post_authorization_exception")

    monkeypatch.setattr(acp, "_execute_mock_effect_v01", unexpected)
    result = _g2a4b_execute(fixture)
    assert calls["execute"] == 1
    context = result.action_packet_fulfillment_attempt_contexts[-1]
    assert context.attempt_evidence.outcome_class == "UNCERTAIN"
    assert context.receipt is None
    entry = _g2a4b_entry(result, packet_id)
    assert entry.transition_events[-1].transition_rule_id == (
        "g2a_t26_uncertain_adapter_outcome"
    )
    assert result.idempotency_disposition_events[-1].event_class == (
        "UNCERTAIN_CLOSE"
    )
    state = acp.derive_action_packet_lifecycle_state_v01(
        result,
        packet_id=packet_id,
    )
    assert state.failed_provenance == "FAILED_UNCERTAIN_TERMINAL"
    assert state.idempotency_disposition == "UNCERTAIN_CLOSED"
    assert state.lifecycle_terminal is True
    with pytest.raises(ValueError):
        _g2a4b_execute(fixture, result)
    with pytest.raises(ValueError):
        _g2a2b_append(result, packet_id, "g2a_t25_retry")
    assert calls["execute"] == 1


def test_g2a4b_one_invocation_has_exactly_one_terminal_outcome(
    g2a4a_fixture: _G2A4AFixtureV01,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = g2a4a_fixture
    forbidden_parameters = {
        "outcome_class",
        "consumed",
        "nonconsuming",
        "uncertain",
        "adapter_invoked",
        "transition_event",
        "disposition_event",
        "receipt",
        "reason_code",
    }
    assert not (
        forbidden_parameters
        & set(
            inspect.signature(
                acp.execute_action_packet_mock_fulfillment_v01
            ).parameters
        )
    )
    original_execute = acp._execute_mock_effect_v01

    def outcome_registry(mode: str) -> acp.ActionCommitPacketRegistryV02:
        if mode == "CONSUMED":
            monkeypatch.setattr(
                acp,
                "_execute_mock_effect_v01",
                original_execute,
            )
        elif mode == "NOT_CONSUMED":
            @wraps(original_execute)
            def nonconsuming(**kwargs: object) -> object:
                raise ValueError("effect_request_expired")

            monkeypatch.setattr(
                acp,
                "_execute_mock_effect_v01",
                nonconsuming,
            )
        else:
            @wraps(original_execute)
            def uncertain(**kwargs: object) -> object:
                return object()

            monkeypatch.setattr(
                acp,
                "_execute_mock_effect_v01",
                uncertain,
            )
        return _g2a4b_execute(fixture)

    expected_rules = {
        "CONSUMED": "g2a_t04_fulfill_mock",
        "NOT_CONSUMED": "g2a_t24_nonconsuming_failure",
        "UNCERTAIN": "g2a_t26_uncertain_adapter_outcome",
    }
    for mode in ("CONSUMED", "NOT_CONSUMED", "UNCERTAIN"):
        registry = outcome_registry(mode)
        context = registry.action_packet_fulfillment_attempt_contexts[-1]
        assert context.attempt_evidence.outcome_class == mode
        result_events = tuple(
            event
            for event in _g2a4b_entry(
                registry,
                fixture.root_bound.packet_identity.packet_id,
            ).transition_events
            if event.transition_rule_id in set(expected_rules.values())
        )
        assert tuple(event.transition_rule_id for event in result_events) == (
            expected_rules[mode],
        )
        disposition_classes = tuple(
            event.event_class
            for event in registry.idempotency_disposition_events
            if event.event_class in {"CONSUME", "UNCERTAIN_CLOSE"}
        )
        assert disposition_classes == {
            "CONSUMED": ("CONSUME",),
            "NOT_CONSUMED": (),
            "UNCERTAIN": ("UNCERTAIN_CLOSE",),
        }[mode]


def test_g2a4b_manual_registry_bypass_and_context_forgery_fail_closed(
    g2a4a_fixture: _G2A4AFixtureV01,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = g2a4a_fixture
    consumed = _g2a4b_execute(fixture)
    context = consumed.action_packet_fulfillment_attempt_contexts[-1]
    evidence = context.attempt_evidence
    consumed_entry = _g2a4b_entry(
        consumed,
        fixture.root_bound.packet_identity.packet_id,
    )
    source_entry = _g2a4b_entry(
        fixture.registry,
        fixture.root_bound.packet_identity.packet_id,
    )
    forged_ordinal = acp.build_action_packet_fulfillment_attempt_evidence_v01(
        **_g2a4b_evidence_kwargs(
            evidence,
            attempt_observation_ordinal=2,
        )
    )
    forged_contexts = (
        replace(
            fixture.registry,
            action_packet_fulfillment_attempt_contexts=(context,),
        ),
        replace(
            consumed,
            action_packet_fulfillment_attempt_contexts=(),
        ),
        replace(
            consumed,
            action_packet_fulfillment_attempt_contexts=(
                replace(context, attempt_evidence=forged_ordinal),
            ),
        ),
        replace(
            consumed,
            action_packet_fulfillment_attempt_contexts=(context, context),
        ),
        replace(
            consumed,
            action_packet_fulfillment_attempt_contexts=(
                replace(
                    context,
                    attempt_evidence=replace(
                        evidence,
                        projection_sha256="f" * 64,
                    ),
                ),
            ),
        ),
        replace(
            consumed,
            action_packet_fulfillment_attempt_contexts=(
                replace(
                    context,
                    attempt_evidence=replace(
                        evidence,
                        capability_id="e" * 64,
                    ),
                ),
            ),
        ),
        replace(
            consumed,
            idempotency_disposition_events=(
                fixture.registry.idempotency_disposition_events
            ),
        ),
        replace(
            consumed,
            action_packet_lifecycle_entries=(
                replace(
                    consumed_entry,
                    transition_events=source_entry.transition_events,
                ),
            ),
        ),
    )
    for forged in forged_contexts:
        assert acp.validate_action_commit_packet_registry_v02(forged)[0] is False

    original_execute = acp._execute_mock_effect_v01

    @wraps(original_execute)
    def nonconsuming(**kwargs: object) -> object:
        raise ValueError("effect_request_expired")

    monkeypatch.setattr(acp, "_execute_mock_effect_v01", nonconsuming)
    failed = _g2a4b_execute(fixture)
    assert acp.validate_action_commit_packet_registry_v02(
        replace(
            failed,
            idempotency_disposition_events=(
                failed.idempotency_disposition_events
                + (failed.idempotency_disposition_events[-1],)
            ),
        )
    )[0] is False
    monkeypatch.setattr(acp, "_execute_mock_effect_v01", original_execute)

    @wraps(original_execute)
    def uncertain(**kwargs: object) -> object:
        raise RuntimeError("controlled_uncertain")

    monkeypatch.setattr(acp, "_execute_mock_effect_v01", uncertain)
    uncertain_registry = _g2a4b_execute(fixture)
    uncertain_context = (
        uncertain_registry.action_packet_fulfillment_attempt_contexts[-1]
    )
    assert acp.validate_action_commit_packet_registry_v02(
        replace(
            uncertain_registry,
            action_packet_fulfillment_attempt_contexts=(
                replace(uncertain_context, receipt=context.receipt),
            ),
        )
    )[0] is False


def test_g2a4b_attempt_and_receipt_histories_are_ordered_and_immutable(
    g2a4a_fixture: _G2A4AFixtureV01,
) -> None:
    fixture = g2a4a_fixture
    packet_id = fixture.root_bound.packet_identity.packet_id
    blocked = _g2a4b_execute(
        fixture,
        current_dependency_observations=(),
    )
    second_context_id = "evaluation_context:g2a4b:history:2"
    consumed = _g2a4b_execute(
        fixture,
        blocked,
        current_dependency_observations=_g2a4b_observations_for_context(
            fixture.observations,
            second_context_id,
        ),
        eligibility_evaluation_context_id=second_context_id,
    )
    consumed_context = consumed.action_packet_fulfillment_attempt_contexts[-1]
    confirmed = acp.observe_action_packet_effect_receipt_v01(
        consumed,
        packet_id=packet_id,
        attempt_evidence_id=(
            consumed_context.attempt_evidence.attempt_evidence_id
        ),
        receipt_evaluation_time=fixture.eligibility_evaluation_time + 1,
        receipt_evaluation_time_source="explicit_g2a4b_receipt_time",
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    contexts = confirmed.action_packet_fulfillment_attempt_contexts
    assert tuple(
        context.attempt_evidence.outcome_class for context in contexts
    ) == ("PRE_FULFILLMENT_BLOCKED", "CONSUMED")
    assert tuple(
        context.attempt_evidence.attempt_observation_ordinal
        for context in contexts
    ) == (1, 2)
    entry = _g2a4b_entry(confirmed, packet_id)
    forged_registries = (
        replace(
            confirmed,
            action_packet_fulfillment_attempt_contexts=tuple(
                reversed(contexts)
            ),
        ),
        replace(
            confirmed,
            action_packet_fulfillment_attempt_contexts=contexts[1:],
        ),
        replace(
            confirmed,
            action_packet_fulfillment_attempt_contexts=contexts
            + (contexts[-1],),
        ),
        replace(
            confirmed,
            action_packet_fulfillment_attempt_contexts=(
                contexts[0],
                replace(
                    contexts[1],
                    attempt_evidence=replace(
                        contexts[1].attempt_evidence,
                        reason_code="rewritten",
                    ),
                ),
            ),
        ),
        replace(
            confirmed,
            action_packet_lifecycle_entries=(
                replace(
                    entry,
                    transition_events=entry.transition_events[:-1],
                ),
            ),
        ),
        replace(
            confirmed,
            idempotency_disposition_events=tuple(
                reversed(confirmed.idempotency_disposition_events)
            ),
        ),
        replace(
            confirmed,
            action_packet_fulfillment_attempt_contexts=(
                contexts[0],
                replace(
                    contexts[1],
                    receipt=replace(
                        contexts[1].receipt,
                        artifact_id="receipt:rewritten",
                    ),
                ),
            ),
        ),
    )
    for forged in forged_registries:
        assert acp.validate_action_commit_packet_registry_v02(forged)[0] is False


def test_g2a4b_retry_creates_new_attempt_and_old_attempt_cannot_execute(
    g2a4a_fixture: _G2A4AFixtureV01,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = g2a4a_fixture
    packet_id = fixture.root_bound.packet_identity.packet_id
    original_execute = acp._execute_mock_effect_v01
    calls = {"execute": 0}

    @wraps(original_execute)
    def nonconsuming(**kwargs: object) -> object:
        calls["execute"] += 1
        raise ValueError("effect_request_expired")

    monkeypatch.setattr(acp, "_execute_mock_effect_v01", nonconsuming)
    failed = _g2a4b_execute(fixture)
    failed, _ = _g2a2b_append(failed, packet_id, "g2a_t25_retry")
    failed, second_pending = _g2a2b_append(
        failed,
        packet_id,
        "g2a_t03_pending",
        evaluation_context_id="evaluation_context:g2a4b:retry:attempt:2",
    )
    second_context_id = "evaluation_context:g2a4b:retry:eligibility:2"
    monkeypatch.setattr(acp, "_execute_mock_effect_v01", original_execute)
    completed = _g2a4b_execute(
        fixture,
        failed,
        current_dependency_observations=_g2a4b_observations_for_context(
            fixture.observations,
            second_context_id,
        ),
        eligibility_evaluation_time=second_pending.evaluation_time,
        eligibility_evaluation_context_id=second_context_id,
    )
    calls["execute"] += 1
    contexts = completed.action_packet_fulfillment_attempt_contexts
    assert tuple(
        context.attempt_evidence.execution_attempt_id for context in contexts
    ) == (
        fixture.pending.execution_attempt_id,
        second_pending.execution_attempt_id,
    )
    assert tuple(
        context.attempt_evidence.outcome_class for context in contexts
    ) == ("NOT_CONSUMED", "CONSUMED")
    assert contexts[0].request.idempotency_key == (
        contexts[1].request.idempotency_key
    )
    assert contexts[0].decision.capability_id != (
        contexts[1].decision.capability_id
    )
    assert calls["execute"] == 2
    with pytest.raises(ValueError):
        _g2a4b_execute(fixture, completed)


def test_g2a4b_post_invocation_failures_never_erase_observed_truth(
    g2a4a_fixture: _G2A4AFixtureV01,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = g2a4a_fixture
    original_execute = acp._execute_mock_effect_v01
    calls = {"execute": 0}

    @wraps(original_execute)
    def malformed_return(**kwargs: object) -> object:
        calls["execute"] += 1
        return {"not": "a receipt"}

    monkeypatch.setattr(acp, "_execute_mock_effect_v01", malformed_return)
    malformed = _g2a4b_execute(fixture)
    assert malformed is not fixture.registry
    assert malformed.action_packet_fulfillment_attempt_contexts[
        -1
    ].attempt_evidence.outcome_class == "UNCERTAIN"

    @wraps(original_execute)
    def mutated_then_failed(**kwargs: object) -> object:
        calls["execute"] += 1
        firewall = kwargs["firewall"]
        firewall._state.seen_request_ids = set()
        firewall._state.used_idempotency_keys = set()
        firewall._state.issued_capabilities = {}
        firewall._state.idempotency_key_by_request_id = {}
        firewall._state.authorization_decision_id_by_capability_id = {}
        raise ValueError("effect_request_expired")

    monkeypatch.setattr(acp, "_execute_mock_effect_v01", mutated_then_failed)
    ambiguous = _g2a4b_execute(fixture)
    assert ambiguous is not fixture.registry
    assert ambiguous.action_packet_fulfillment_attempt_contexts[
        -1
    ].attempt_evidence.outcome_class == "UNCERTAIN"

    @wraps(original_execute)
    def counted_consumed(**kwargs: object) -> object:
        calls["execute"] += 1
        return original_execute(**kwargs)

    monkeypatch.setattr(acp, "_execute_mock_effect_v01", counted_consumed)
    consumed = _g2a4b_execute(fixture)
    consumed_context = consumed.action_packet_fulfillment_attempt_contexts[-1]
    assert consumed_context.attempt_evidence.outcome_class == "CONSUMED"
    assert consumed_context.receipt is not None
    assert calls["execute"] == 3
    assert all(
        len(registry.action_packet_fulfillment_attempt_contexts) == 1
        for registry in (malformed, ambiguous, consumed)
    )


def test_g2a4b_frozen_effect_firewall_execution_is_the_only_effect_path(
    g2a4a_fixture: _G2A4AFixtureV01,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_path = Path(acp.__file__)
    source = source_path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    frozen_calls = tuple(
        node
        for node in ast.walk(tree)
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "_execute_mock_effect_v01"
        )
    )
    assert len(frozen_calls) == 1
    assert "mock_connector_sandbox" not in source
    assert "EffectCapabilityV01" not in {
        node.name
        for node in tree.body
        if isinstance(node, (ast.ClassDef, ast.FunctionDef))
    }
    assert "provider" not in inspect.getsource(
        acp.execute_action_packet_mock_fulfillment_v01
    ).lower()
    calls = {"execute": 0}
    original_execute = acp._execute_mock_effect_v01

    @wraps(original_execute)
    def counted_execute(**kwargs: object) -> object:
        calls["execute"] += 1
        return original_execute(**kwargs)

    monkeypatch.setattr(acp, "_execute_mock_effect_v01", counted_execute)
    result = _g2a4b_execute(g2a4a_fixture)
    assert calls["execute"] == 1
    assert result.action_packet_fulfillment_attempt_contexts[
        -1
    ].attempt_evidence.real_world_effects_count == 0


def test_g2a4b_deterministic_attempt_transition_disposition_and_receipt_vectors(
    g2a4a_fixture: _G2A4AFixtureV01,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = g2a4a_fixture
    packet_id = fixture.root_bound.packet_identity.packet_id
    preblocked = _g2a4b_execute(
        fixture,
        current_dependency_observations=(),
    )
    consumed = _g2a4b_execute(fixture)
    consumed_context = consumed.action_packet_fulfillment_attempt_contexts[-1]
    original_execute = acp._execute_mock_effect_v01

    @wraps(original_execute)
    def nonconsuming(**kwargs: object) -> object:
        raise ValueError("effect_request_expired")

    monkeypatch.setattr(acp, "_execute_mock_effect_v01", nonconsuming)
    failed = _g2a4b_execute(fixture)

    @wraps(original_execute)
    def uncertain(**kwargs: object) -> object:
        raise RuntimeError("vector_uncertain")

    monkeypatch.setattr(acp, "_execute_mock_effect_v01", uncertain)
    uncertain_registry = _g2a4b_execute(fixture)
    confirmed = acp.observe_action_packet_effect_receipt_v01(
        consumed,
        packet_id=packet_id,
        attempt_evidence_id=(
            consumed_context.attempt_evidence.attempt_evidence_id
        ),
        receipt_evaluation_time=fixture.eligibility_evaluation_time + 1,
        receipt_evaluation_time_source="explicit_g2a4b_receipt_time",
        action_packet_transition_registry_profile=_g2a2a_registry(),
    )
    assert (
        preblocked.action_packet_fulfillment_attempt_contexts[
            -1
        ].attempt_evidence.attempt_evidence_id
        == "fulfillment_attempt_evidence_v01:"
        "5f8fa939343b558a33624642d40c16b5e3b43d685ae2655c29ab064b0b0097d6"
    )
    assert (
        consumed_context.attempt_evidence.attempt_evidence_id
        == "fulfillment_attempt_evidence_v01:"
        "b7d2e28954ed568f031f8b2cf62002a2927cb9deccb7e169644c319244ab2dda"
    )
    assert (
        failed.action_packet_fulfillment_attempt_contexts[
            -1
        ].attempt_evidence.attempt_evidence_id
        == "fulfillment_attempt_evidence_v01:"
        "30a0f8bc7ee12bb05877731f1a64536675719aa272fc06070f33e01ea39e7c23"
    )
    assert (
        uncertain_registry.action_packet_fulfillment_attempt_contexts[
            -1
        ].attempt_evidence.attempt_evidence_id
        == "fulfillment_attempt_evidence_v01:"
        "86078fbdf211ee56fb66c594db9cdb01c7459409b880070ac2da65a025d02f38"
    )
    assert _g2a4b_entry(
        consumed,
        packet_id,
    ).transition_events[-1].transition_event_id == (
        "acpt_v01:"
        "0d1fa24efb522e363f26a6270755dd294a889a01868aa01b81ec932f490efd80"
    )
    assert _g2a4b_entry(
        failed,
        packet_id,
    ).transition_events[-1].transition_event_id == (
        "acpt_v01:"
        "7159f821c0ec2962d4ef55cd4258127dd8e237f8da5d1b354886e245c9ab4b63"
    )
    assert _g2a4b_entry(
        uncertain_registry,
        packet_id,
    ).transition_events[-1].transition_event_id == (
        "acpt_v01:"
        "ca7f2c0818778ae187807a5c0f9a7e3864bff9dc0762bff14cee996c3f6f05d5"
    )
    assert _g2a4b_entry(
        confirmed,
        packet_id,
    ).transition_events[-1].transition_event_id == (
        "acpt_v01:"
        "0c448c16f4836e7030f7ee069df5e550098451218b7a3eecd196642a0bf3d256"
    )
    assert (
        consumed.idempotency_disposition_events[
            -1
        ].idempotency_disposition_event_id
        == "idem_event_v01:"
        "a0a5b50ad2da32a7bed5d912ce5acb4a83b891c43ff99edc80eded2a747f3d96"
    )
    assert (
        uncertain_registry.idempotency_disposition_events[
            -1
        ].idempotency_disposition_event_id
        == "idem_event_v01:"
        "d6226471ad9879b7c0abf6847bfdcbc4f9b123d2efbafa1d3d270e9b699d6164"
    )
    assert (
        confirmed.idempotency_disposition_events[
            -1
        ].idempotency_disposition_event_id
        == "idem_event_v01:"
        "03bc62fc14ae4c8693e72466a6c3793691ef5723277b4cbf01d8662c34a0fa15"
    )
    assert consumed_context.attempt_evidence.receipt_sha256 == (
        "c5f7e2307e71cdb6aba06cddec5b37a4e25e7268f1f0d52259a63828adfc8a68"
    )


def _g2a4_final_rebuild_terminal_bundle(
    fixture: _G2A4AFixtureV01,
    context: acp._ActionPacketFulfillmentAttemptContextV01,
    *,
    projection: acp.ActionPacketEffectFirewallProjectionV01 | None = None,
    request: object | None = None,
    decision: object | None = None,
    receipt: object | None = None,
    reason_code: str | None = None,
) -> acp.ActionCommitPacketRegistryV02:
    source = fixture.registry
    packet_id = fixture.root_bound.packet_identity.packet_id
    entry = _g2a4b_entry(source, packet_id)
    pending = entry.transition_events[-1]
    state = acp.derive_action_packet_lifecycle_state_v01(
        source,
        packet_id=packet_id,
    )
    original = context.attempt_evidence
    effective_projection = context.projection if projection is None else projection
    effective_request = context.request if request is None else request
    effective_decision = context.decision if decision is None else decision
    effective_receipt = context.receipt if receipt is None else receipt
    evidence_changes: dict[str, object] = {
        "projection_sha256": (
            acp._action_packet_effect_projection_sha256_v01(
                effective_projection
            )
            if effective_projection is not None
            else None
        ),
        "firewall_id": (
            effective_decision.firewall_id
            if effective_decision is not None
            else None
        ),
        "request_id": (
            effective_request.request_id
            if effective_request is not None
            else None
        ),
        "decision_id": (
            effective_decision.decision_id
            if effective_decision is not None
            else None
        ),
        "capability_id": (
            effective_decision.capability_id
            if effective_decision is not None
            else None
        ),
        "adapter_id": (
            effective_projection.adapter_id
            if effective_projection is not None
            else None
        ),
        "action_kind": (
            effective_projection.action_kind
            if effective_projection is not None
            else None
        ),
        "receipt_ref": (
            effective_receipt.artifact_id
            if effective_receipt is not None
            else None
        ),
        "receipt_sha256": (
            acp._action_packet_effect_receipt_sha256_v01(
                effective_receipt
            )
            if effective_receipt is not None
            else None
        ),
    }
    if reason_code is not None:
        evidence_changes["reason_code"] = reason_code
    evidence = acp.build_action_packet_fulfillment_attempt_evidence_v01(
        **_g2a4b_evidence_kwargs(original, **evidence_changes)
    )
    rule_id = {
        "CONSUMED": "g2a_t04_fulfill_mock",
        "NOT_CONSUMED": "g2a_t24_nonconsuming_failure",
        "UNCERTAIN": "g2a_t26_uncertain_adapter_outcome",
    }[evidence.outcome_class]
    transition = acp._g2a4b_outcome_transition_v01(
        entry,
        pending,
        state,
        evidence,
        rule_id=rule_id,
        receipt=(
            effective_receipt
            if evidence.outcome_class == "CONSUMED"
            else None
        ),
        transition_registry=_g2a2a_registry(),
    )
    disposition_class = {
        "CONSUMED": "CONSUME",
        "NOT_CONSUMED": None,
        "UNCERTAIN": "UNCERTAIN_CLOSE",
    }[evidence.outcome_class]
    disposition = (
        acp._g2a4b_outcome_disposition_v01(
            state,
            transition,
            event_class=disposition_class,
        )
        if disposition_class is not None
        else None
    )
    forged_context = replace(
        context,
        attempt_evidence=evidence,
        projection=effective_projection,
        request=effective_request,
        decision=effective_decision,
        receipt=effective_receipt,
    )
    forged_entry = replace(
        entry,
        transition_events=entry.transition_events + (transition,),
    )
    return replace(
        source,
        action_packet_lifecycle_entries=(forged_entry,),
        idempotency_disposition_events=(
            source.idempotency_disposition_events
            if disposition is None
            else source.idempotency_disposition_events + (disposition,)
        ),
        action_packet_fulfillment_attempt_contexts=(forged_context,),
    )


def _g2a4_final_forged_preblocked_registry(
    fixture: _G2A4AFixtureV01,
    *,
    reason_code: str,
) -> acp.ActionCommitPacketRegistryV02:
    source = fixture.registry
    packet_id = fixture.root_bound.packet_identity.packet_id
    entry = _g2a4b_entry(source, packet_id)
    pending = entry.transition_events[-1]
    state = acp.derive_action_packet_lifecycle_state_v01(
        source,
        packet_id=packet_id,
    )
    evidence = acp._g2a4b_attempt_evidence_v01(
        source,
        entry,
        pending,
        state,
        ordinal=1,
        corridor=fixture.corridor,
        corridor_step=fixture.corridor_step,
        observations=fixture.observations,
        logical_time_bridge=fixture.logical_time_bridge,
        eligibility_evaluation_time=fixture.eligibility_evaluation_time,
        eligibility_evaluation_time_source=(
            fixture.eligibility_evaluation_time_source
        ),
        eligibility_evaluation_context_id=(
            fixture.eligibility_evaluation_context_id
        ),
        projection=None,
        preparation=None,
        outcome_class="PRE_FULFILLMENT_BLOCKED",
        reason_code=reason_code,
        adapter_invoked=False,
        firewall_state_sha256_before=None,
        firewall_state_sha256_after=None,
        receipt=None,
    )
    context = acp._ActionPacketFulfillmentAttemptContextV01(
        attempt_evidence=evidence,
        projection=None,
        corridor=fixture.corridor,
        corridor_step=fixture.corridor_step,
        current_dependency_observations=fixture.observations,
        logical_time_bridge=fixture.logical_time_bridge,
        request=None,
        decision=None,
        receipt=None,
    )
    return replace(
        source,
        action_packet_fulfillment_attempt_contexts=(context,),
    )


def _g2a4_final_forged_firewall_block_registry(
    fixture: _G2A4AFixtureV01,
) -> acp.ActionCommitPacketRegistryV02:
    source = fixture.registry
    packet_id = fixture.root_bound.packet_identity.packet_id
    entry = _g2a4b_entry(source, packet_id)
    pending = entry.transition_events[-1]
    state = acp.derive_action_packet_lifecycle_state_v01(
        source,
        packet_id=packet_id,
    )
    projection = _g2a4a_projection(fixture)
    root = fixture.root_bound.root_decision_projection
    firewall = acp._build_effect_firewall_v01(
        root_decision_kernel=root.root_decision_kernel,
        decision_input=root.root_decision_input,
        root_decision_result=root.root_decision_result,
        invocation_id=projection.execution_attempt_id,
        allowed_adapter_ids=projection.allowed_adapter_ids,
        allowed_action_kinds=projection.allowed_action_kinds,
        root_scope_refs=projection.root_scope_refs,
        maximum_expires_at_tick=projection.maximum_expires_at_tick,
    )
    request = acp._build_effect_request_v01(
        root_decision_kernel=root.root_decision_kernel,
        decision_input=root.root_decision_input,
        root_decision_result=root.root_decision_result,
        request_kind=projection.request_kind,
        adapter_id=projection.adapter_id,
        action_kind=projection.action_kind,
        scope_refs=projection.scope_refs,
        issued_at_tick=projection.issued_at_tick,
        expires_at_tick=projection.expires_at_tick,
        idempotency_key=projection.idempotency_key,
    )
    decision = acp._authorize_effect_request_v01(
        firewall=firewall,
        request=request,
        current_tick=request.expires_at_tick,
    )
    preparation = acp._ActionPacketEffectAttemptPreparationV01(
        projection=projection,
        firewall=firewall,
        request=request,
        decision=decision,
    )
    evidence = acp._g2a4b_attempt_evidence_v01(
        source,
        entry,
        pending,
        state,
        ordinal=1,
        corridor=fixture.corridor,
        corridor_step=fixture.corridor_step,
        observations=fixture.observations,
        logical_time_bridge=fixture.logical_time_bridge,
        eligibility_evaluation_time=fixture.eligibility_evaluation_time,
        eligibility_evaluation_time_source=(
            fixture.eligibility_evaluation_time_source
        ),
        eligibility_evaluation_context_id=(
            fixture.eligibility_evaluation_context_id
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
    context = acp._ActionPacketFulfillmentAttemptContextV01(
        attempt_evidence=evidence,
        projection=projection,
        corridor=fixture.corridor,
        corridor_step=fixture.corridor_step,
        current_dependency_observations=fixture.observations,
        logical_time_bridge=fixture.logical_time_bridge,
        request=request,
        decision=decision,
        receipt=None,
    )
    return replace(
        source,
        action_packet_fulfillment_attempt_contexts=(context,),
    )


def _g2a4_final_forged_receipt(
    receipt: kernel_abi.KernelArtifactV01,
) -> kernel_abi.KernelArtifactV01:
    plain = kernel_abi.kernel_artifact_to_plain_dict_v01(receipt)
    artifact_id = "receipt:g2a4:coherent_forgery"
    payload = dict(plain["payload"])
    payload["receipt_ref"] = artifact_id
    time_envelope = dict(plain["time_envelope"])
    time_envelope["valid_to"] = "2099-01-01T00:00:00Z"
    time_envelope["ttl_seconds"] = int(time_envelope["ttl_seconds"]) + 1
    return kernel_abi.build_kernel_artifact_v01(
        abi_version=plain["abi_version"],
        artifact_id=artifact_id,
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
        time_envelope=time_envelope,
    )


def test_g2a4_final_preblocked_requires_replayed_failure(
    g2a4a_fixture: _G2A4AFixtureV01,
) -> None:
    replayed = _g2a4b_execute(
        g2a4a_fixture,
        current_dependency_observations=(),
    )
    assert acp.validate_action_commit_packet_registry_v02(replayed) == (
        True,
        (),
    )
    assert (
        replayed.action_packet_fulfillment_attempt_contexts[
            -1
        ].attempt_evidence.reason_code
        == "current_mandatory_dependency_missing"
    )
    forged = _g2a4_final_forged_preblocked_registry(
        g2a4a_fixture,
        reason_code="fabricated_block",
    )
    assert acp.validate_action_commit_packet_registry_v02(forged)[0] is False


def _g2a4_final_alternate_projection_field(
    field_name: str,
    value: object,
) -> object:
    if type(value) is bool:
        return not value
    if type(value) is int:
        return value + 1
    if type(value) is tuple:
        return value + (f"forged:{field_name}",)
    if field_name in {
        "authority_policy_fingerprint",
        "temporal_authority_fingerprint",
    }:
        return ("e" if value != "e" * 64 else "d") * 64
    return f"forged:{field_name}"


def test_g2a4_final_projection_rebuild_rejects_coherent_drift(
    g2a4a_fixture: _G2A4AFixtureV01,
) -> None:
    consumed = _g2a4b_execute(g2a4a_fixture)
    context = consumed.action_packet_fulfillment_attempt_contexts[-1]
    projection = context.projection
    assert projection is not None
    projection_fields = fields(
        acp.ActionPacketEffectFirewallProjectionV01
    )
    assert len(projection_fields) == 39
    rejected = 0
    for field in projection_fields:
        forged_projection = replace(
            projection,
            **{
                field.name: _g2a4_final_alternate_projection_field(
                    field.name,
                    getattr(projection, field.name),
                )
            },
        )
        forged = _g2a4_final_rebuild_terminal_bundle(
            g2a4a_fixture,
            context,
            projection=forged_projection,
        )
        assert (
            acp.validate_action_commit_packet_registry_v02(forged)[0]
            is False
        ), field.name
        rejected += 1
    assert rejected == 39


def test_g2a4_final_firewall_decision_uses_projection_tick(
    g2a4a_fixture: _G2A4AFixtureV01,
) -> None:
    forged = _g2a4_final_forged_firewall_block_registry(g2a4a_fixture)
    assert acp.validate_action_commit_packet_registry_v02(forged)[0] is False


def test_g2a4_final_branch_reason_codes_are_closed(
    g2a4a_fixture: _G2A4AFixtureV01,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_execute = acp._execute_mock_effect_v01
    consumed = _g2a4b_execute(g2a4a_fixture)
    consumed_context = (
        consumed.action_packet_fulfillment_attempt_contexts[-1]
    )
    assert acp.validate_action_commit_packet_registry_v02(consumed) == (
        True,
        (),
    )
    forged_consumed = _g2a4_final_rebuild_terminal_bundle(
        g2a4a_fixture,
        consumed_context,
        reason_code="effect_request_expired",
    )
    assert (
        acp.validate_action_commit_packet_registry_v02(forged_consumed)[0]
        is False
    )

    @wraps(original_execute)
    def nonconsuming(**kwargs: object) -> object:
        raise ValueError("effect_request_expired")

    monkeypatch.setattr(acp, "_execute_mock_effect_v01", nonconsuming)
    failed = _g2a4b_execute(g2a4a_fixture)
    context = failed.action_packet_fulfillment_attempt_contexts[-1]
    forged = _g2a4_final_rebuild_terminal_bundle(
        g2a4a_fixture,
        context,
        reason_code="effect_capability_missing",
    )
    assert acp.validate_action_commit_packet_registry_v02(forged)[0] is False
    assert acp.validate_action_commit_packet_registry_v02(failed) == (
        True,
        (),
    )

    @wraps(original_execute)
    def uncertain(**kwargs: object) -> object:
        raise RuntimeError("controlled_uncertain")

    monkeypatch.setattr(acp, "_execute_mock_effect_v01", uncertain)
    uncertain_registry = _g2a4b_execute(g2a4a_fixture)
    uncertain_context = (
        uncertain_registry.action_packet_fulfillment_attempt_contexts[-1]
    )
    assert (
        acp.validate_action_commit_packet_registry_v02(
            uncertain_registry
        )
        == (True, ())
    )
    for wrong_reason in (
        "arbitrary_uncertain_reason",
        "effect_request_expired",
        "mock_effect_consumed",
    ):
        forged_uncertain = _g2a4_final_rebuild_terminal_bundle(
            g2a4a_fixture,
            uncertain_context,
            reason_code=wrong_reason,
        )
        assert (
            acp.validate_action_commit_packet_registry_v02(
                forged_uncertain
            )[0]
            is False
        )


def test_g2a4_final_receipt_is_exactly_rebuilt(
    g2a4a_fixture: _G2A4AFixtureV01,
) -> None:
    consumed = _g2a4b_execute(g2a4a_fixture)
    context = consumed.action_packet_fulfillment_attempt_contexts[-1]
    forged_receipt = _g2a4_final_forged_receipt(context.receipt)
    forged = _g2a4_final_rebuild_terminal_bundle(
        g2a4a_fixture,
        context,
        receipt=forged_receipt,
    )
    assert kernel_abi.validate_kernel_artifact_v01(forged_receipt) == ()
    assert acp.validate_action_commit_packet_registry_v02(forged)[0] is False


def test_g2a4_final_post_invocation_fallback_preserves_truth(
    g2a4a_fixture: _G2A4AFixtureV01,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original_execute = acp._execute_mock_effect_v01
    original_evidence = acp._g2a4b_attempt_evidence_v01
    original_state = acp._action_packet_firewall_state_observation_v01
    original_classifier = acp._g2a4b_classify_invoked_outcome_v01
    original_finalizer = acp._g2a4b_build_invoked_outcome_bundle_v01

    def run_with_failure(
        target: str,
        replacement: object,
    ) -> None:
        calls = {"execute": 0}

        @wraps(original_execute)
        def counted_execute(**kwargs: object) -> object:
            calls["execute"] += 1
            return original_execute(**kwargs)

        with monkeypatch.context() as patch:
            patch.setattr(acp, "_execute_mock_effect_v01", counted_execute)
            patch.setattr(acp, target, replacement)
            result = _g2a4b_execute(g2a4a_fixture)
        assert result is not g2a4a_fixture.registry
        assert calls["execute"] == 1
        assert (
            result.action_packet_fulfillment_attempt_contexts[
                -1
            ].attempt_evidence.outcome_class
            == "CONSUMED"
        )
        assert acp.validate_action_commit_packet_registry_v02(result) == (
            True,
            (),
        )

    @wraps(original_evidence)
    def failed_primary_evidence(*args: object, **kwargs: object) -> object:
        raise ValueError("controlled_primary_evidence_failure")

    state_calls = {"count": 0}

    @wraps(original_state)
    def failed_post_state(*args: object, **kwargs: object) -> object:
        state_calls["count"] += 1
        if state_calls["count"] == 2:
            raise ValueError("controlled_post_state_failure")
        return original_state(*args, **kwargs)

    @wraps(original_classifier)
    def failed_receipt_classifier(
        *args: object,
        **kwargs: object,
    ) -> object:
        raise ValueError("controlled_receipt_classification_failure")

    @wraps(original_finalizer)
    def failed_primary_finalizer(
        *args: object,
        **kwargs: object,
    ) -> object:
        raise ValueError("controlled_primary_finalizer_failure")

    run_with_failure(
        "_g2a4b_attempt_evidence_v01",
        failed_primary_evidence,
    )
    run_with_failure(
        "_action_packet_firewall_state_observation_v01",
        failed_post_state,
    )
    run_with_failure(
        "_g2a4b_classify_invoked_outcome_v01",
        failed_receipt_classifier,
    )
    run_with_failure(
        "_g2a4b_build_invoked_outcome_bundle_v01",
        failed_primary_finalizer,
    )
