from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal
from pathlib import Path

import pytest

import hedgehog.action_commit_packet_v02 as acp
from hedgehog.kernel.integrity_replay_v01 import (
    canonical_json_bytes_v01,
    domain_separated_sha256_hex_v01,
)
import hedgehog.kernel.root_decision_v01 as root_decision
import hedgehog.kernel.semantic_work_v01 as semantic_work
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
        retry_policy="NON_CONSUMING_RETRY",
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
    transaction_id: str | None = None,
    target_root_id: str | None = None,
    state_updates: dict[str, dict[str, object]] | None = None,
) -> tuple[
    semantic_work.SemanticWorkRequestV01,
    semantic_work.RootReviewPacketV01,
    root_decision.RootDecisionKernelV01,
    root_decision.RootDecisionInputV01,
    root_decision.RootDecisionResultV01,
]:
    selected_candidate = candidate_id or (
        canonical.authorization_candidate.root_packet_authorization_candidate_id
    )
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
        predicate="root_packet_authorization_candidate",
        object_or_value={
            "candidate_id": selected_candidate,
            "candidate_kind": "PACKET_AUTHORIZATION",
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
            "permission_required": True,
            "user_permission_present": True,
            "permission_scope_valid": True,
            "permission_ref": canonical.canonical_permission_ref,
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
        "execute_mock_effect_v01",
    ):
        assert forbidden not in source


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
