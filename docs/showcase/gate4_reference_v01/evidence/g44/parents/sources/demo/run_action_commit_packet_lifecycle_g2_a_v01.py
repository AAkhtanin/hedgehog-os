from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass, replace

import hedgehog.action_commit_packet_v02 as acp
from hedgehog.kernel.integrity_replay_v01 import canonical_json_bytes_v01
import hedgehog.kernel.root_decision_v01 as root_decision
import hedgehog.kernel.semantic_work_v01 as semantic_work
import hedgehog.kernel.transition_registry_v01 as transition_registry
import hedgehog.kernel.trust_model_v01 as trust_model


_EVALUATION_TIME = 1783470600
_EVALUATION_TIME_SOURCE = "explicit_g2a5_synthetic_time"
_AUTHORITY_LAW_ID = "root_only_action_commit_packet_authority_v01"
_REPORT_PROFILE_ID = "action_commit_packet_lifecycle_g2_a5_report_v01"
_SYNTHETIC_REGISTRY_ID = "acp_v02:local_registry"
_SYNTHETIC_TRANSITION_REGISTRY_ID = (
    "acptr_v01:"
    "3a0fb8ffbabca39ff96c0624f8da89eb82222c277c54d932112ebaa0eef97eab"
)
_EMPTY_FULFILLMENT_HISTORY_SHA256 = (
    "a16c1145c84e1872255db6a71b5c595c0e248aa115ffdbf5850a564d1c5a3fc2"
)

_RECORDED_TRANSITION_FIELDS_V01 = (
    "transition_event_id",
    "transition_rule_id",
    "source_state",
    "target_state",
    "evaluation_time",
    "evaluation_time_source",
    "evaluation_context_id",
    "execution_attempt_id",
    "effect_consumption_class",
    "receipt_ref",
)
_LIFECYCLE_STATE_FIELDS_V01 = (
    "packet_id",
    "idempotency_key",
    "lifecycle_state",
    "failed_provenance",
    "transition_event_count",
    "latest_transition_event_id",
    "execution_attempt_count",
    "idempotency_disposition",
    "reservation_owner_packet_id",
    "latest_disposition_event_id",
    "terminal_receipt_ref",
    "lifecycle_terminal",
    "eligible_for_corridor_revalidation",
    "executable",
    "registry_is_authority",
    "registry_grants_permission",
    "real_world_effects_count",
    "reason_codes",
)
_REPLAY_REPORT_FIELDS_V01 = (
    "replay_profile_id",
    "registry_id",
    "packet_id",
    "transition_registry_id",
    "source_root_decision_id",
    "source_root_decision_hash",
    "rebuilt_packet_id",
    "rebuilt_idempotency_key",
    "recorded_transitions",
    "disposition_event_ids",
    "invalidation_evidence_ids",
    "fulfillment_attempt_evidence_ids",
    "reconstructed_state",
    "transition_history_sha256",
    "disposition_history_sha256",
    "invalidation_history_sha256",
    "fulfillment_history_sha256",
    "historical_temporal_replay_pass",
    "t24_reserved_history_replay_pass",
    "distinct_firewall_attempt_replay_pass",
    "registry_unchanged",
    "creates_authority",
    "creates_permission",
    "creates_packet",
    "creates_receipt",
    "adapter_calls",
    "real_world_effects_count",
)
_PRESENT_INSPECTION_FIELDS_V01 = (
    "inspection_profile_id",
    "registry_id",
    "packet_id",
    "evaluation_time",
    "evaluation_time_source",
    "evaluation_context_id",
    "historical_state",
    "present_eligibility_status",
    "present_executable",
    "retry_eligible",
    "reason_codes",
    "transition_history_sha256",
    "disposition_history_sha256",
    "historical_result_unchanged",
    "creates_authority",
    "creates_permission",
    "creates_packet",
    "creates_receipt",
    "adapter_calls",
    "real_world_effects_count",
)
_DOMAIN_RESULT_FIELDS_V01 = (
    "domain_shape",
    "source_reference_status",
    "packet_id",
    "owning_local_root_id",
    "transition_registry_id",
    "invalidation_class",
    "authority_effect",
    "transition_rule_id",
    "lifecycle_before",
    "lifecycle_after",
    "idempotency_disposition_after",
    "reservation_owner_packet_id_after",
    "replay_report",
    "present_inspection",
    "generic_authority_law_id",
    "registry_creates_authority",
    "adapter_calls",
    "receipt_creations",
    "real_world_effects_count",
)
_FINAL_REPORT_FIELDS_V01 = (
    "report_profile_id",
    "airline",
    "supplier",
    "same_packet_family",
    "same_transition_registry_id",
    "same_authority_law",
    "immutable_history_proven",
    "closed_domain_artifacts_rerun",
    "provider_calls",
    "network_calls",
    "gemini_calls",
    "adapter_calls",
    "receipt_creations",
    "real_world_effects_count",
    "final_status",
)

_DOMAIN_GEOMETRY_V01 = {
    "AIRLINE": {
        "packet_id": (
            "acp_v02:"
            "485d0d73c176f430129cf05812969790655d0907238a0bff7554bd9422573472"
        ),
        "idempotency_key": (
            "idem:action_v01:"
            "0ffe82c8886f56ca0080fbad793c57341e99490fcce3b1f1781522ec46fc8bef"
        ),
        "source_root_decision_id": (
            "3ef878ebe142bc07cc450a14034bd1f6760dc5bcb137aab5637a9c1fc4ff2708"
        ),
        "source_root_decision_hash": (
            "a817eef5b59e4a1ff8aaee42b1113c013717a3d20fe792da72ba1263b5db7c8b"
        ),
        "transition_event_ids": (
            "acpt_v01:"
            "da5c2067ad81ff0259229cfc7d3259a85524b0f01992f84797a0817001efaf25",
            "acpt_v01:"
            "29147b9ab840a82667c12dfbe6e819358c47117f4c8f8a5071c4eb5d7d2857ce",
            "acpt_v01:"
            "2bd80e2a2c9d8eb99dd5203a1fa7f2dfbea5ae5551332efd5777b9392ff89176",
            "acpt_v01:"
            "f17345036a48d01ada1e89bfe552e9481db3ab056d6f13597d97cbc5b1530868",
        ),
        "execution_attempt_id": (
            "execution_attempt_v01:"
            "a78171a86ea6dc8be2968a2cce60ffd55db4e931dbc328b39833e7ff24d29317"
        ),
        "disposition_event_id": (
            "idem_event_v01:"
            "036268baf3372b79696733ce101226a609c0d420f2c83f5650c12e9ad79263ee"
        ),
        "invalidation_evidence_id": (
            "d1ad59475539611b51bf24caf3259ac6bfd6e01119488d9eae1276b91ab5f7aa"
        ),
        "transition_history_sha256": (
            "3bcb7d36c6af878cb80ae8ba0d54c1a4e8f6dbb3c689720c71206b4f0abd1a42"
        ),
        "disposition_history_sha256": (
            "65c3837500fbf26188f6ca85c34b3a5800df5d124c577bebb05d2a73d5ea783b"
        ),
        "invalidation_history_sha256": (
            "84cd1c3d0c44397dc8c9ae2267f6f7087d34784246208ec2198e3a74ebfb6ff8"
        ),
    },
    "SUPPLIER": {
        "packet_id": (
            "acp_v02:"
            "d6e3c49fd0441cc8f2618b798fe4a99fd2e40b1852cc54857a797ad8a532b8bc"
        ),
        "idempotency_key": (
            "idem:action_v01:"
            "4d309bb434b0921f6c70af6a5ee1ad187b6a9e77dee61e559792022b32b1c234"
        ),
        "source_root_decision_id": (
            "16e1c54ee96f4c952d059d3e64c5610a34d1fd69540c19630a6bdec0302d1719"
        ),
        "source_root_decision_hash": (
            "0189ef75ff88821b66606ec2c0f408e3066743a8773dd5f4d7afedf0d5868053"
        ),
        "transition_event_ids": (
            "acpt_v01:"
            "491797a77378f048ca28fcf6d96c3873123eb22065f7e97a49fe80277baef3e4",
            "acpt_v01:"
            "14ae57eeeffe79d743ef2a4fd79a0f5f40d7a4445f54b8cf2f98944e0b58aa8e",
            "acpt_v01:"
            "57f03720fa248aa5523518a3fd7236132a009031d100304c64b0d3e2edfb7224",
            "acpt_v01:"
            "32e6afc9cd98e1e4795c80680618b4c33db0b52435628f86dfd5879521b355cd",
        ),
        "execution_attempt_id": (
            "execution_attempt_v01:"
            "e9614dd85ba576af998d9003f858f0ff76e76fb814621382865abc27171f97db"
        ),
        "disposition_event_id": (
            "idem_event_v01:"
            "ef46b4f848cc19e950e69df09e3b790d83b8368a59109b3e720984649449fe3f"
        ),
        "invalidation_evidence_id": (
            "533353e63aa8c7a2bacb92735604cd444902b5854ea921d2f392f7be9cbe766c"
        ),
        "transition_history_sha256": (
            "22fd71ec4f77b2a52a2ae2246762df573b201f98306a396319dea78363603e74"
        ),
        "disposition_history_sha256": (
            "5f3c6ee419598dd7a499206326ef09ca384b91e94b97e902be1a962af9eff733"
        ),
        "invalidation_history_sha256": (
            "7b1865bb9191287832436891b58b2c11544821bb043bf612371607c494a33e7c"
        ),
    },
}


@dataclass(frozen=True)
class G2A5DomainProofResultV01:
    domain_shape: str
    source_reference_status: str
    packet_id: str
    owning_local_root_id: str
    transition_registry_id: str
    invalidation_class: str
    authority_effect: str
    transition_rule_id: str
    lifecycle_before: str
    lifecycle_after: str
    idempotency_disposition_after: str
    reservation_owner_packet_id_after: str | None
    replay_report: acp.ActionPacketLifecycleReplayReportV01
    present_inspection: acp.ActionPacketPresentEligibilityInspectionV01
    generic_authority_law_id: str
    registry_creates_authority: bool
    adapter_calls: int
    receipt_creations: int
    real_world_effects_count: int


@dataclass(frozen=True)
class ActionCommitPacketLifecycleG2A5ReportV01:
    report_profile_id: str
    airline: G2A5DomainProofResultV01
    supplier: G2A5DomainProofResultV01
    same_packet_family: bool
    same_transition_registry_id: bool
    same_authority_law: bool
    immutable_history_proven: bool
    closed_domain_artifacts_rerun: bool
    provider_calls: int
    network_calls: int
    gemini_calls: int
    adapter_calls: int
    receipt_creations: int
    real_world_effects_count: int
    final_status: str


@dataclass(frozen=True)
class _SyntheticPendingV01:
    root_bound: acp.SupplierRootBoundActionCommitPacketV02ProjectionV01
    registry: acp.ActionCommitPacketRegistryV02
    corridor: acp.ContractFulfillmentCorridorV01
    corridor_step: acp.CorridorStepV01
    observations: tuple[acp.ActionDependencyCurrentObservationV01, ...]
    bridge: acp.LogicalTimeBridgeV01


def _transition_profile(
) -> transition_registry.ActionPacketTransitionRegistryProfileV01:
    return (
        transition_registry.build_action_packet_transition_registry_profile_v01()
    )


def _authority_policy(
    root_id: str,
) -> acp.ActionAuthorityPolicyProfileV01:
    return acp.build_action_authority_policy_profile_v01(
        policy_version="g2a5_synthetic_policy_v01",
        owning_local_root_id=root_id,
        authority_rule_refs=("authority_rule:g2a5_mock_action",),
        kill_switch_condition_refs=("kill_switch:g2a5_active",),
        retry_policy="NON_CONSUMING_RETRY",
        supersession_policy="ROOT_DECISION_ONLY",
        logical_effect_namespace="g2a5.synthetic_effect.v01",
        allowed_logical_effect_classes=("PAYMENT",),
        allowed_business_object_namespaces=(
            "g2a5.synthetic_business_object.v01",
        ),
        allowed_corridor_classes=("g2a5_mock_corridor",),
    )


def _root_evidence(
    canonical: acp.SupplierActionCommitPacketCanonicalProjectionV01,
    domain_shape: str,
) -> tuple[
    root_decision.RootDecisionKernelV01,
    root_decision.RootDecisionInputV01,
    root_decision.RootDecisionResultV01,
]:
    candidate_id = (
        canonical.authorization_candidate
        .root_packet_authorization_candidate_id
    )
    context_ref = f"context:g2a5:{domain_shape.lower()}"
    actor_id = "runtime:g2a5_synthetic_authorization"
    request = semantic_work.build_semantic_work_request_v01(
        request_id=f"semantic_request:g2a5:{domain_shape.lower()}",
        transaction_id=canonical.transaction_id,
        target_root_id=canonical.owning_local_root_id,
        runtime_topology_ref="runtime_topology:g2a5_bounded_synthetic",
        bounded_context_refs=(context_ref,),
        permitted_actor_ids=(actor_id,),
        permitted_contribution_modes=("DETERMINISTIC",),
        requested_subjects=(
            f"action_commit_packet:{domain_shape.lower()}",
        ),
        required_evidence_classes=("DEPENDENCY_EVIDENCE",),
        forbidden_claims=("authority_creation",),
    )
    dependency = canonical.dependency_candidate.dependency_records[0]
    evidence = semantic_work.build_evidence_binding_v01(
        evidence_id=f"evidence_binding:g2a5:{domain_shape.lower()}",
        evidence_ref=dependency.evidence_ref,
        evidence_class="DEPENDENCY_EVIDENCE",
        source_component_id="deterministic_runtime",
        provenance_ref=dependency.source_provenance_refs[0],
        evidence_state="PRESENT",
    )
    claim = semantic_work.build_normalized_claim_v01(
        claim_id=candidate_id,
        subject=f"action_commit_packet:{domain_shape.lower()}",
        predicate="root_packet_authorization_candidate",
        object_or_value={
            "candidate_id": candidate_id,
            "candidate_kind": "PACKET_AUTHORIZATION",
        },
        time_envelope_ref=canonical.temporal_authority_fingerprint,
        provenance_refs=("provenance:g2a5_synthetic_authorization",),
        evidence_refs=(evidence.evidence_id,),
        confidence_micros=1_000_000,
        source_role="deterministic_runtime",
        source_mode="DETERMINISTIC",
    )
    contribution = semantic_work.build_actor_contribution_v01(
        contribution_id=f"contribution:g2a5:{domain_shape.lower()}",
        request_id=request.request_id,
        actor_id=actor_id,
        actor_role="deterministic_runtime",
        contribution_mode="DETERMINISTIC",
        bsep_projection_ref="bsep:g2a5_synthetic",
        scope="scope:g2a5_synthetic_authorization",
        bounded_context_refs=(context_ref,),
        claims=(claim,),
        evidence_bindings=(evidence,),
        constraint_bindings=(),
        uncertainty_bindings=(),
        requested_validators=("validator:g2a5_synthetic_authorization",),
        forbidden_claims_observed=(),
    )
    review = semantic_work.build_root_review_packet_from_contributions_v01(
        request=request,
        contributions=(contribution,),
        trust_profiles=(
            trust_model.build_default_component_trust_profiles_v01()
        ),
    )
    mandatory_refs = [
        record.evidence_ref
        for record in canonical.dependency_candidate.dependency_records
        if record.requirement_class == "MANDATORY"
    ]
    kernel = root_decision.build_root_decision_kernel_v01()
    decision_input = root_decision.build_root_decision_input_v01(
        transaction_id=canonical.transaction_id,
        target_root_id=canonical.owning_local_root_id,
        root_review_packet=review,
        post_vv_bundle={
            "bundle_id": "post_vv:g2a5_synthetic",
            "post_vv_passed": True,
            "validated_candidate_ids": [candidate_id],
            "rejected_candidate_ids": [],
            "required_evidence_refs": mandatory_refs,
            "provided_evidence_refs": mandatory_refs,
            "hard_failure_reasons": [],
        },
        gt_advisory={
            "advisory_id": "gt:g2a5_synthetic",
            "candidate_ids": [candidate_id],
            "selected_candidate_id": candidate_id,
            "score_micros_by_candidate": {candidate_id: 1_000_000},
            "source_artifact_type": "GTAdvisoryReport",
            "source_lifecycle_state": "VALIDATED",
            "actor_role": "gt",
            "attempted_effect": "CREATE_ROOT_DECISION",
            "target_artifact_type": "RootDecision",
            "advisory_only": True,
            "creates_final_output": False,
            "requests_effect": False,
        },
        policy_state={
            "policy_id": canonical.authority_policy_fingerprint,
            "identity_passed": True,
            "scope_passed": True,
            "hard_policy_passed": True,
            "allow_accept": True,
            "conflict_policy": "DEFER",
            "no_candidate_policy": "NO_UPDATE",
        },
        permission_state={
            "permission_required": True,
            "user_permission_present": True,
            "permission_scope_valid": True,
            "permission_ref": canonical.canonical_permission_ref,
        },
        temporal_state={
            "temporal_valid": True,
            "expired": False,
            "not_before_satisfied": True,
            "time_envelope_ref": canonical.temporal_authority_fingerprint,
        },
        conflict_state={
            "material_unresolved_conflict": False,
            "conflict_set_ids": list(review.conflict_set_ids),
        },
        prior_root_state={
            "prior_decision_id": None,
            "prior_decision": None,
            "prior_selected_candidate_id": None,
        },
    )
    result = root_decision.decide_root_v01(
        kernel=kernel,
        decision_input=decision_input,
    )
    return kernel, decision_input, result


def _transition_bindings(
    rule_id: str,
) -> tuple[acp.TransitionEvidenceBindingV01, ...]:
    profile = _transition_profile()
    rule = transition_registry.lookup_action_packet_transition_rule_v01(
        registry=profile,
        transition_rule_id=rule_id,
    )
    return tuple(
        acp.build_transition_evidence_binding_v01(
            action_packet_transition_registry_profile=profile,
            transition_rule_id=rule_id,
            evidence_code=code,
            evidence_ref=f"evidence:g2a5:{code}",
            evidence_sha256="d" * 64,
            validator_profile_id="validator:g2a5_transition",
        )
        for code in rule.required_evidence_codes
    )


def _transition_event(
    entry: acp.ActionPacketLifecycleEntryV01,
    rule_id: str,
    *,
    evaluation_context_id: str,
) -> acp.ActionPacketTransitionEventV01:
    canonical = entry.root_bound_genesis.canonical_projection
    packet_id = entry.root_bound_genesis.packet_identity.packet_id
    attempt = None
    if rule_id == "g2a_t03_pending":
        attempt = acp.build_action_execution_attempt_identity_v01(
            packet_id=packet_id,
            idempotency_key=canonical.idempotency_identity.idempotency_key,
            attempt_ordinal=1,
            evaluation_context_id=evaluation_context_id,
        )
    return acp.build_action_packet_transition_event_v01(
        action_packet_transition_registry_profile=_transition_profile(),
        transition_rule_id=rule_id,
        packet_id=packet_id,
        idempotency_key=canonical.idempotency_identity.idempotency_key,
        previous_transition_event_id=(
            entry.transition_events[-1].transition_event_id
            if entry.transition_events
            else None
        ),
        owning_local_root_id=canonical.owning_local_root_id,
        root_decision_ref=(
            entry.root_bound_genesis.root_decision_projection
            .root_decision_result.decision_id
            if rule_id == "g2a_t01_activate_root_authorization"
            else None
        ),
        transition_evidence_bindings=_transition_bindings(rule_id),
        dependency_set_candidate_fingerprint=(
            canonical.dependency_set_candidate_fingerprint
        ),
        temporal_authority_fingerprint=(
            canonical.temporal_authority_fingerprint
        ),
        evaluation_time=_EVALUATION_TIME + len(entry.transition_events),
        evaluation_time_source=_EVALUATION_TIME_SOURCE,
        evaluation_context_id=evaluation_context_id,
        execution_attempt_identity=attempt,
        receipt_ref=None,
    )


def _pending_fixture(domain_shape: str) -> _SyntheticPendingV01:
    root_id = f"root:g2a5:{domain_shape.lower()}"
    source = acp.build_supplier_a_mock_action_commit_packet_fixture_v02()
    temporal = acp.project_packet_ttl_compatibility_v01(
        source.ttl,
        evaluation_time=_EVALUATION_TIME,
        temporal_policy_version="packet_ttl_v01",
    ).temporal_authority
    dependency_id = f"dependency:g2a5:{domain_shape.lower()}:primary"
    evidence_ref = f"evidence:g2a5:{domain_shape.lower()}:primary"
    provenance = f"source:g2a5:{domain_shape.lower()}:primary"
    envelope = acp.build_action_dependency_time_envelope_id_v01(
        dependency_id=dependency_id,
        evidence_ref=evidence_ref,
        content_sha256="a" * 64,
        freshness_policy_id="freshness_policy:g2a5_current",
        source_provenance_refs=(provenance,),
        valid_from_utc=temporal.issued_at_utc,
        valid_to_utc=temporal.expires_at_utc,
    )
    dependency = acp.build_dependency_set_candidate_v01(
        dependency_records=(
            acp.build_dependency_set_candidate_record_v01(
                dependency_id=dependency_id,
                dependency_class="SYNTHETIC_DOMAIN_EVIDENCE",
                evidence_ref=evidence_ref,
                content_sha256="a" * 64,
                requirement_class="MANDATORY",
                time_envelope_id=envelope,
                freshness_policy_id="freshness_policy:g2a5_current",
                source_provenance_refs=(provenance,),
                expected_accepting_local_root_id=root_id,
            ),
        )
    )
    canonical = acp.build_supplier_action_commit_packet_canonical_projection_v01(
        source,
        transaction_id=f"transaction:g2a5:{domain_shape.lower()}",
        owning_local_root_id=root_id,
        canonical_permission_ref="permission:g2a5_mock_action",
        selected_legacy_action=acp.ACTION_MOCK_SUPPLIER_A_PAYMENT_ORDER,
        logical_effect_namespace="g2a5.synthetic_effect.v01",
        business_object_namespace="g2a5.synthetic_business_object.v01",
        corridor_class="g2a5_mock_corridor",
        adapter_version=acp.PRE_G2A_ADAPTER_VERSION_V01,
        temporal_policy_version="packet_ttl_v01",
        authority_policy=_authority_policy(root_id),
        dependency_candidate=dependency,
        evaluation_time=_EVALUATION_TIME,
        evaluation_time_source=_EVALUATION_TIME_SOURCE,
        evaluation_context_id=(
            f"evaluation_context:g2a5:{domain_shape.lower()}:canonical"
        ),
    )
    kernel, decision_input, result = _root_evidence(
        canonical,
        domain_shape,
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
    profile = _transition_profile()
    registry = acp.record_action_packet_genesis_v01(
        acp.build_empty_action_commit_packet_registry_v02(),
        root_bound_genesis=root_bound,
        action_packet_transition_registry_profile=profile,
    )
    packet_id = root_bound.packet_identity.packet_id
    entry = registry.action_packet_lifecycle_entries[0]
    activation = _transition_event(
        entry,
        "g2a_t01_activate_root_authorization",
        evaluation_context_id=(
            f"evaluation_context:g2a5:{domain_shape.lower()}:activate"
        ),
    )
    evidence_ids = tuple(
        sorted(
            (
                binding.transition_evidence_binding_id
                for binding in activation.transition_evidence_bindings
                if binding.evidence_code
                in {
                    "packet_genesis_valid",
                    "source_root_authorization_valid",
                    "idempotency_acquisition_valid",
                }
            ),
            key=lambda item: item.encode("utf-8"),
        )
    )
    reserve = acp.build_idempotency_disposition_event_v01(
        idempotency_key=canonical.idempotency_identity.idempotency_key,
        event_class="RESERVE",
        from_disposition="UNCLAIMED",
        to_disposition="RESERVED",
        from_owner_packet_id=None,
        to_owner_packet_id=packet_id,
        previous_disposition_event_id=None,
        cause_transition_event_ids=(activation.transition_event_id,),
        root_decision_ref=result.decision_id,
        predecessor_packet_id=None,
        successor_packet_id=None,
        evidence_refs=evidence_ids,
        evaluation_time=activation.evaluation_time,
        evaluation_time_source=activation.evaluation_time_source,
        evaluation_context_id=activation.evaluation_context_id,
    )
    registry = acp.activate_action_packet_lifecycle_v01(
        registry,
        packet_id=packet_id,
        transition_event=activation,
        disposition_event=reserve,
        action_packet_transition_registry_profile=profile,
    )
    for rule_id in ("g2a_t02_queue", "g2a_t03_pending"):
        entry = registry.action_packet_lifecycle_entries[0]
        transition = _transition_event(
            entry,
            rule_id,
            evaluation_context_id=(
                f"evaluation_context:g2a5:{domain_shape.lower()}:{rule_id}"
            ),
        )
        registry = acp.append_action_packet_lifecycle_transition_v01(
            registry,
            packet_id=packet_id,
            transition_event=transition,
            action_packet_transition_registry_profile=profile,
        )
    step = acp.build_supplier_a_corridor_step_fixture_v01(source)
    step = replace(
        step,
        parent_packet_id=packet_id,
        allowed_subjects=source.scope.allowed_subjects,
    )
    corridor = acp.ContractFulfillmentCorridorV01(
        corridor_id=f"corridor:g2a5:{domain_shape.lower()}",
        packet_id=packet_id,
        corridor_kind=canonical.adapter_binding.corridor_class,
        allowed_steps=(step.step_id,),
    )
    observation_context = (
        f"evaluation_context:g2a5:{domain_shape.lower()}:present"
    )
    observations = (
        acp.build_action_dependency_current_observation_v01(
            dependency_id=dependency_id,
            evidence_ref=evidence_ref,
            observed_content_sha256="a" * 64,
            time_envelope_id=envelope,
            freshness_policy_id="freshness_policy:g2a5_current",
            source_provenance_refs=(provenance,),
            valid_from_utc=temporal.issued_at_utc,
            valid_to_utc=temporal.expires_at_utc,
            observed_at_utc=_EVALUATION_TIME,
            observation_context_id=observation_context,
        ),
    )
    bridge = acp.build_logical_time_bridge_v01(
        origin_utc_epoch_seconds=temporal.issued_at_utc,
        seconds_per_tick=1,
        bridge_policy_version="g2a5_epoch_seconds_v01",
    )
    return _SyntheticPendingV01(
        root_bound=root_bound,
        registry=registry,
        corridor=corridor,
        corridor_step=step,
        observations=observations,
        bridge=bridge,
    )


def _invalidation(
    fixture: _SyntheticPendingV01,
    domain_shape: str,
) -> acp.ActionInvalidationEvidenceV01:
    canonical = fixture.root_bound.canonical_projection
    record = canonical.dependency_candidate.dependency_records[0]
    invalidation_class = (
        "DEPENDENCY_CHANGED"
        if domain_shape == "AIRLINE"
        else "ROOT_BOUND_KILL_SWITCH"
    )
    dependency_id = (
        record.dependency_id
        if domain_shape == "AIRLINE"
        else canonical.authority_policy.kill_switch_condition_refs[0]
    )
    evidence_ref = (
        record.evidence_ref
        if domain_shape == "AIRLINE"
        else "evidence:supplier:legal_hold_fraud_cancellation_active"
    )
    return acp.build_action_invalidation_evidence_v01(
        source_invalidation_event_ref=(
            f"source_invalidation:g2a5:{domain_shape.lower()}"
        ),
        packet_id=fixture.root_bound.packet_identity.packet_id,
        dependency_id=dependency_id,
        invalidation_class=invalidation_class,
        evidence_ref=evidence_ref,
        evidence_sha256=(
            record.content_sha256 if domain_shape == "AIRLINE" else "c" * 64
        ),
        observed_status=(
            "OBSERVED_CURRENT_DEPENDENCY_CHANGED"
            if domain_shape == "AIRLINE"
            else "OBSERVED_KILL_SWITCH_ACTIVE"
        ),
        time_envelope_id=record.time_envelope_id,
        freshness_policy_id=record.freshness_policy_id,
        owning_local_root_id=canonical.owning_local_root_id,
        accepted_by_local_root_id=canonical.owning_local_root_id,
        acceptance_root_decision_id=None,
        acceptance_root_decision_hash=None,
        authority_effect="DETERMINISTIC_BLOCK",
        root_decision_ref=None,
        evaluation_time=_EVALUATION_TIME + 3,
        evaluation_time_source=_EVALUATION_TIME_SOURCE,
        evaluation_context_id=(
            f"evaluation_context:g2a5:{domain_shape.lower()}:invalidation"
        ),
    )


def _invalidation_transition(
    fixture: _SyntheticPendingV01,
    invalidation: acp.ActionInvalidationEvidenceV01,
) -> acp.ActionPacketTransitionEventV01:
    profile = _transition_profile()
    rule_id = "g2a_t09_pending_block"
    rule = transition_registry.lookup_action_packet_transition_rule_v01(
        registry=profile,
        transition_rule_id=rule_id,
    )
    entry = fixture.registry.action_packet_lifecycle_entries[0]
    canonical = fixture.root_bound.canonical_projection
    state = acp.derive_action_packet_lifecycle_state_v01(
        fixture.registry,
        packet_id=fixture.root_bound.packet_identity.packet_id,
        action_packet_transition_registry_profile=profile,
    )
    latest = entry.transition_events[-1]

    def evidence_material(code: str) -> tuple[str, str, str]:
        if code in {
            "blocking_evidence_valid",
            "immediate_eligibility_failure_valid",
        }:
            return (
                invalidation.invalidation_evidence_id,
                invalidation.invalidation_evidence_id,
                acp.ACTION_INVALIDATION_EVIDENCE_PROFILE_ID_V01,
            )
        if code == "packet_genesis_valid":
            packet_id = fixture.root_bound.packet_identity.packet_id
            return (
                packet_id,
                packet_id[len(acp.ACTION_COMMIT_PACKET_ID_PREFIX_V01) :],
                acp._ACTION_COMMIT_PACKET_IDENTITY_PROFILE_ID_V01,
            )
        if code == "authority_policy_valid":
            value = canonical.authority_policy_fingerprint
            return (
                value,
                value,
                acp.ACTION_AUTHORITY_POLICY_PROFILE_ID_V01,
            )
        if code == "idempotency_reservation_owned":
            value = state.latest_disposition_event_id
            if value is None:
                raise ValueError("g2a5_reservation_missing")
            return (
                value,
                value[
                    len(acp.IDEMPOTENCY_DISPOSITION_EVENT_PREFIX_V01) :
                ],
                acp.IDEMPOTENCY_DISPOSITION_EVENT_PROFILE_ID_V01,
            )
        if code == "adapter_not_called":
            value = latest.execution_attempt_id
            if value is None:
                raise ValueError("g2a5_attempt_missing")
            return (
                value,
                value[len(acp.EXECUTION_ATTEMPT_IDENTITY_PREFIX_V01) :],
                acp.EXECUTION_ATTEMPT_IDENTITY_PROFILE_ID_V01,
            )
        raise ValueError("g2a5_transition_evidence_unsupported")

    bindings = tuple(
        acp.build_transition_evidence_binding_v01(
            action_packet_transition_registry_profile=profile,
            transition_rule_id=rule_id,
            evidence_code=code,
            evidence_ref=evidence_material(code)[0],
            evidence_sha256=evidence_material(code)[1],
            validator_profile_id=evidence_material(code)[2],
        )
        for code in rule.required_evidence_codes
    )
    return acp.build_action_packet_transition_event_v01(
        action_packet_transition_registry_profile=profile,
        transition_rule_id=rule_id,
        packet_id=fixture.root_bound.packet_identity.packet_id,
        idempotency_key=canonical.idempotency_identity.idempotency_key,
        previous_transition_event_id=latest.transition_event_id,
        owning_local_root_id=canonical.owning_local_root_id,
        root_decision_ref=None,
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


def _packet_family_proof_v01(
    fixture: _SyntheticPendingV01,
) -> bool:
    root_bound = fixture.root_bound
    canonical = root_bound.canonical_projection
    root_projection = root_bound.root_decision_projection
    identity = root_bound.packet_identity
    try:
        return bool(
            type(canonical.source_packet) is acp.ActionCommitPacketV02
            and acp.validate_action_commit_packet_v02(
                canonical.source_packet
            )
            == (True, ())
            and type(identity) is acp.ActionCommitPacketIdentityResultV01
            and acp.validate_action_commit_packet_identity_v01(
                identity,
                candidate=canonical.authorization_candidate,
                source_root_decision_id=(
                    root_projection.root_decision_result.decision_id
                ),
                source_root_decision_hash=(
                    root_projection.source_root_decision_hash
                ),
            )
            == (True, ())
            and acp.validate_supplier_root_bound_action_commit_packet_v02_projection_v01(
                root_bound
            )
            == (True, ())
        )
    except Exception:
        return False


def _collect_domain(
    domain_shape: str,
) -> tuple[G2A5DomainProofResultV01, bool]:
    fixture = _pending_fixture(domain_shape)
    packet_id = fixture.root_bound.packet_identity.packet_id
    packet_family_proven = _packet_family_proof_v01(fixture)
    before = acp.derive_action_packet_lifecycle_state_v01(
        fixture.registry,
        packet_id=packet_id,
        action_packet_transition_registry_profile=_transition_profile(),
    )
    invalidation = _invalidation(fixture, domain_shape)
    transition = _invalidation_transition(fixture, invalidation)
    blocked = acp.record_action_packet_deterministic_invalidation_v01(
        fixture.registry,
        packet_id=packet_id,
        invalidation_evidence=invalidation,
        transition_event=transition,
        action_packet_transition_registry_profile=_transition_profile(),
    )
    replay = acp.replay_action_packet_lifecycle_history_v01(
        blocked,
        packet_id=packet_id,
    )
    observation_context = (
        f"evaluation_context:g2a5:{domain_shape.lower()}:present"
    )
    inspection = acp.inspect_action_packet_present_eligibility_v01(
        blocked,
        packet_id=packet_id,
        corridor=fixture.corridor,
        corridor_step=fixture.corridor_step,
        current_dependency_observations=fixture.observations,
        logical_time_bridge=fixture.bridge,
        evaluation_time=_EVALUATION_TIME + 4,
        evaluation_time_source=_EVALUATION_TIME_SOURCE,
        evaluation_context_id=observation_context,
    )
    state = replay.reconstructed_state
    return (
        G2A5DomainProofResultV01(
            domain_shape=domain_shape,
            source_reference_status=(
                "INDEPENDENT_ROOT_GEOMETRY_REFERENCE_ONLY_NO_CLOSED_ARTIFACT_RERUN"
                if domain_shape == "AIRLINE"
                else "MIXED_REFERENCE_ONLY_SUPPLIER_B_BLOCKED_SHIPMENT_HELD"
            ),
            packet_id=packet_id,
            owning_local_root_id=(
                fixture.root_bound.canonical_projection.owning_local_root_id
            ),
            transition_registry_id=replay.transition_registry_id,
            invalidation_class=invalidation.invalidation_class,
            authority_effect=invalidation.authority_effect,
            transition_rule_id=transition.transition_rule_id,
            lifecycle_before=before.lifecycle_state,
            lifecycle_after=state.lifecycle_state,
            idempotency_disposition_after=state.idempotency_disposition,
            reservation_owner_packet_id_after=(
                state.reservation_owner_packet_id
            ),
            replay_report=replay,
            present_inspection=inspection,
            generic_authority_law_id=_AUTHORITY_LAW_ID,
            registry_creates_authority=False,
            adapter_calls=0,
            receipt_creations=0,
            real_world_effects_count=0,
        ),
        packet_family_proven,
    )


def _packet_identity_family_from_result_v01(
    result: object,
) -> bool:
    if type(result) is not G2A5DomainProofResultV01:
        return False
    replay = result.replay_report
    inspection = result.present_inspection
    return bool(
        type(replay) is acp.ActionPacketLifecycleReplayReportV01
        and type(inspection)
        is acp.ActionPacketPresentEligibilityInspectionV01
        and acp.validate_prefixed_sha256_identity_v01(
            result.packet_id,
            prefix=acp.ACTION_COMMIT_PACKET_ID_PREFIX_V01,
        )[0]
        and replay.packet_id == result.packet_id
        and replay.rebuilt_packet_id == result.packet_id
        and inspection.packet_id == result.packet_id
    )


def _has_exact_dataclass_fields_v01(
    value: object,
    expected_type: type[object],
    expected_fields: tuple[str, ...],
) -> bool:
    return bool(
        type(value) is expected_type
        and tuple(field.name for field in fields(expected_type))
        == expected_fields
    )


def _is_lowercase_sha256_v01(value: object) -> bool:
    return bool(
        type(value) is str
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def _is_prefixed_sha256_v01(
    value: object,
    *,
    prefix: str,
) -> bool:
    return bool(
        type(value) is str
        and value.startswith(prefix)
        and _is_lowercase_sha256_v01(value[len(prefix) :])
    )


def _recorded_transition_replay_is_exact_v01(
    recorded_transitions: object,
    *,
    domain_shape: str,
) -> bool:
    if (
        type(recorded_transitions) is not tuple
        or len(recorded_transitions) != 4
        or domain_shape not in _DOMAIN_GEOMETRY_V01
    ):
        return False
    geometry = _DOMAIN_GEOMETRY_V01[domain_shape]
    domain = domain_shape.lower()
    expected_rules = (
        "g2a_t01_activate_root_authorization",
        "g2a_t02_queue",
        "g2a_t03_pending",
        "g2a_t09_pending_block",
    )
    expected_sources = (
        "CREATED",
        "ROOT_AUTHORIZED",
        "QUEUED",
        "PENDING_FULFILLMENT",
    )
    expected_targets = (
        "ROOT_AUTHORIZED",
        "QUEUED",
        "PENDING_FULFILLMENT",
        "BLOCKED",
    )
    expected_contexts = (
        f"evaluation_context:g2a5:{domain}:activate",
        f"evaluation_context:g2a5:{domain}:g2a_t02_queue",
        f"evaluation_context:g2a5:{domain}:g2a_t03_pending",
        f"evaluation_context:g2a5:{domain}:invalidation",
    )
    expected_event_ids = geometry["transition_event_ids"]
    expected_attempt_id = geometry["execution_attempt_id"]
    if (
        type(expected_event_ids) is not tuple
        or type(expected_attempt_id) is not str
    ):
        return False
    observed_event_ids: list[str] = []
    for index, transition in enumerate(recorded_transitions):
        if not _has_exact_dataclass_fields_v01(
            transition,
            acp.ActionPacketRecordedTransitionReplayV01,
            _RECORDED_TRANSITION_FIELDS_V01,
        ):
            return False
        if not (
            _is_prefixed_sha256_v01(
                transition.transition_event_id,
                prefix="acpt_v01:",
            )
            and transition.transition_event_id == expected_event_ids[index]
            and type(transition.transition_rule_id) is str
            and transition.transition_rule_id == expected_rules[index]
            and type(transition.source_state) is str
            and transition.source_state == expected_sources[index]
            and type(transition.target_state) is str
            and transition.target_state == expected_targets[index]
            and type(transition.evaluation_time) is int
            and transition.evaluation_time == _EVALUATION_TIME + index
            and type(transition.evaluation_time_source) is str
            and transition.evaluation_time_source
            == _EVALUATION_TIME_SOURCE
            and type(transition.evaluation_context_id) is str
            and transition.evaluation_context_id == expected_contexts[index]
            and type(transition.effect_consumption_class) is str
            and transition.effect_consumption_class == "NOT_CONSUMED"
            and transition.receipt_ref is None
        ):
            return False
        if index == 2:
            if not (
                _is_prefixed_sha256_v01(
                    transition.execution_attempt_id,
                    prefix="execution_attempt_v01:",
                )
                and transition.execution_attempt_id == expected_attempt_id
            ):
                return False
        elif transition.execution_attempt_id is not None:
            return False
        observed_event_ids.append(transition.transition_event_id)
    return bool(
        len(set(observed_event_ids)) == 4
        and all(
            recorded_transitions[index].target_state
            == recorded_transitions[index + 1].source_state
            for index in range(3)
        )
        and all(
            recorded_transitions[index].evaluation_time
            < recorded_transitions[index + 1].evaluation_time
            for index in range(3)
        )
    )


def _lifecycle_state_is_exact_v01(
    state: object,
    *,
    domain_shape: str,
    recorded_transitions: tuple[
        acp.ActionPacketRecordedTransitionReplayV01, ...
    ],
    disposition_event_id: str,
) -> bool:
    if (
        not _has_exact_dataclass_fields_v01(
            state,
            acp.ActionPacketLifecycleStateV01,
            _LIFECYCLE_STATE_FIELDS_V01,
        )
        or domain_shape not in _DOMAIN_GEOMETRY_V01
        or len(recorded_transitions) != 4
    ):
        return False
    geometry = _DOMAIN_GEOMETRY_V01[domain_shape]
    return bool(
        type(state.packet_id) is str
        and state.packet_id == geometry["packet_id"]
        and type(state.idempotency_key) is str
        and state.idempotency_key == geometry["idempotency_key"]
        and type(state.lifecycle_state) is str
        and state.lifecycle_state == "BLOCKED"
        and state.failed_provenance is None
        and type(state.transition_event_count) is int
        and state.transition_event_count == len(recorded_transitions) == 4
        and type(state.latest_transition_event_id) is str
        and state.latest_transition_event_id
        == recorded_transitions[-1].transition_event_id
        and type(state.execution_attempt_count) is int
        and state.execution_attempt_count == 1
        and type(state.idempotency_disposition) is str
        and state.idempotency_disposition == "RESERVED"
        and type(state.reservation_owner_packet_id) is str
        and state.reservation_owner_packet_id == state.packet_id
        and type(state.latest_disposition_event_id) is str
        and state.latest_disposition_event_id == disposition_event_id
        and state.terminal_receipt_ref is None
        and type(state.lifecycle_terminal) is bool
        and state.lifecycle_terminal is True
        and type(state.eligible_for_corridor_revalidation) is bool
        and state.eligible_for_corridor_revalidation is False
        and type(state.executable) is bool
        and state.executable is False
        and type(state.registry_is_authority) is bool
        and state.registry_is_authority is False
        and type(state.registry_grants_permission) is bool
        and state.registry_grants_permission is False
        and type(state.real_world_effects_count) is int
        and state.real_world_effects_count == 0
        and type(state.reason_codes) is tuple
        and state.reason_codes == ()
    )


def _lifecycle_replay_report_is_exact_v01(
    replay: object,
    *,
    domain_shape: str,
) -> bool:
    if (
        not _has_exact_dataclass_fields_v01(
            replay,
            acp.ActionPacketLifecycleReplayReportV01,
            _REPLAY_REPORT_FIELDS_V01,
        )
        or domain_shape not in _DOMAIN_GEOMETRY_V01
    ):
        return False
    geometry = _DOMAIN_GEOMETRY_V01[domain_shape]
    transitions = replay.recorded_transitions
    if not _recorded_transition_replay_is_exact_v01(
        transitions,
        domain_shape=domain_shape,
    ):
        return False
    disposition_event_id = geometry["disposition_event_id"]
    invalidation_evidence_id = geometry["invalidation_evidence_id"]
    state = replay.reconstructed_state
    if (
        type(disposition_event_id) is not str
        or type(invalidation_evidence_id) is not str
        or not _lifecycle_state_is_exact_v01(
            state,
            domain_shape=domain_shape,
            recorded_transitions=transitions,
            disposition_event_id=disposition_event_id,
        )
    ):
        return False
    history_hashes = (
        replay.transition_history_sha256,
        replay.disposition_history_sha256,
        replay.invalidation_history_sha256,
        replay.fulfillment_history_sha256,
    )
    return bool(
        type(replay.replay_profile_id) is str
        and replay.replay_profile_id
        == acp.ACTION_PACKET_LIFECYCLE_REPLAY_PROFILE_ID_V01
        and type(replay.registry_id) is str
        and replay.registry_id == _SYNTHETIC_REGISTRY_ID
        and type(replay.packet_id) is str
        and _is_prefixed_sha256_v01(
            replay.packet_id,
            prefix=acp.ACTION_COMMIT_PACKET_ID_PREFIX_V01,
        )
        and replay.packet_id == geometry["packet_id"]
        and type(replay.transition_registry_id) is str
        and _is_prefixed_sha256_v01(
            replay.transition_registry_id,
            prefix="acptr_v01:",
        )
        and replay.transition_registry_id
        == _SYNTHETIC_TRANSITION_REGISTRY_ID
        and type(replay.source_root_decision_id) is str
        and _is_lowercase_sha256_v01(replay.source_root_decision_id)
        and replay.source_root_decision_id
        == geometry["source_root_decision_id"]
        and type(replay.source_root_decision_hash) is str
        and _is_lowercase_sha256_v01(replay.source_root_decision_hash)
        and replay.source_root_decision_hash
        == geometry["source_root_decision_hash"]
        and type(replay.rebuilt_packet_id) is str
        and replay.rebuilt_packet_id == replay.packet_id
        and type(replay.rebuilt_idempotency_key) is str
        and _is_prefixed_sha256_v01(
            replay.rebuilt_idempotency_key,
            prefix="idem:action_v01:",
        )
        and replay.rebuilt_idempotency_key == geometry["idempotency_key"]
        and type(replay.disposition_event_ids) is tuple
        and replay.disposition_event_ids == (disposition_event_id,)
        and _is_prefixed_sha256_v01(
            disposition_event_id,
            prefix="idem_event_v01:",
        )
        and type(replay.invalidation_evidence_ids) is tuple
        and replay.invalidation_evidence_ids
        == (invalidation_evidence_id,)
        and _is_lowercase_sha256_v01(invalidation_evidence_id)
        and type(replay.fulfillment_attempt_evidence_ids) is tuple
        and replay.fulfillment_attempt_evidence_ids == ()
        and all(_is_lowercase_sha256_v01(value) for value in history_hashes)
        and replay.transition_history_sha256
        == geometry["transition_history_sha256"]
        and replay.disposition_history_sha256
        == geometry["disposition_history_sha256"]
        and replay.invalidation_history_sha256
        == geometry["invalidation_history_sha256"]
        and replay.fulfillment_history_sha256
        == _EMPTY_FULFILLMENT_HISTORY_SHA256
        and len(set(history_hashes)) == 4
        and type(replay.historical_temporal_replay_pass) is bool
        and replay.historical_temporal_replay_pass is True
        and type(replay.t24_reserved_history_replay_pass) is bool
        and replay.t24_reserved_history_replay_pass is True
        and type(replay.distinct_firewall_attempt_replay_pass) is bool
        and replay.distinct_firewall_attempt_replay_pass is True
        and type(replay.registry_unchanged) is bool
        and replay.registry_unchanged is True
        and type(replay.creates_authority) is bool
        and replay.creates_authority is False
        and type(replay.creates_permission) is bool
        and replay.creates_permission is False
        and type(replay.creates_packet) is bool
        and replay.creates_packet is False
        and type(replay.creates_receipt) is bool
        and replay.creates_receipt is False
        and type(replay.adapter_calls) is int
        and replay.adapter_calls == 0
        and type(replay.real_world_effects_count) is int
        and replay.real_world_effects_count == 0
    )


def _present_inspection_is_exact_v01(
    inspection: object,
    *,
    replay: acp.ActionPacketLifecycleReplayReportV01,
    domain_shape: str,
) -> bool:
    if (
        not _has_exact_dataclass_fields_v01(
            inspection,
            acp.ActionPacketPresentEligibilityInspectionV01,
            _PRESENT_INSPECTION_FIELDS_V01,
        )
        or domain_shape not in _DOMAIN_GEOMETRY_V01
    ):
        return False
    geometry = _DOMAIN_GEOMETRY_V01[domain_shape]
    disposition_event_id = geometry["disposition_event_id"]
    domain = domain_shape.lower()
    state = inspection.historical_state
    if not (
        type(disposition_event_id) is str
        and _lifecycle_state_is_exact_v01(
            state,
            domain_shape=domain_shape,
            recorded_transitions=replay.recorded_transitions,
            disposition_event_id=disposition_event_id,
        )
    ):
        return False
    return bool(
        type(inspection.inspection_profile_id) is str
        and inspection.inspection_profile_id
        == acp.ACTION_PACKET_PRESENT_ELIGIBILITY_INSPECTION_PROFILE_ID_V01
        and type(inspection.registry_id) is str
        and inspection.registry_id == replay.registry_id
        and type(inspection.packet_id) is str
        and inspection.packet_id == replay.packet_id
        and type(inspection.evaluation_time) is int
        and inspection.evaluation_time == _EVALUATION_TIME + 4
        and type(inspection.evaluation_time_source) is str
        and inspection.evaluation_time_source == _EVALUATION_TIME_SOURCE
        and type(inspection.evaluation_context_id) is str
        and inspection.evaluation_context_id
        == f"evaluation_context:g2a5:{domain}:present"
        and type(state) is acp.ActionPacketLifecycleStateV01
        and state == replay.reconstructed_state
        and type(inspection.present_eligibility_status) is str
        and inspection.present_eligibility_status == "NON_EXECUTABLE"
        and type(inspection.present_executable) is bool
        and inspection.present_executable is False
        and type(inspection.retry_eligible) is bool
        and inspection.retry_eligible is False
        and type(inspection.reason_codes) is tuple
        and len(inspection.reason_codes) == 1
        and type(inspection.reason_codes[0]) is str
        and inspection.reason_codes
        == ("action_packet_present_state_non_executable",)
        and type(inspection.transition_history_sha256) is str
        and inspection.transition_history_sha256
        == replay.transition_history_sha256
        and type(inspection.disposition_history_sha256) is str
        and inspection.disposition_history_sha256
        == replay.disposition_history_sha256
        and type(inspection.historical_result_unchanged) is bool
        and inspection.historical_result_unchanged is True
        and type(inspection.creates_authority) is bool
        and inspection.creates_authority is False
        and type(inspection.creates_permission) is bool
        and inspection.creates_permission is False
        and type(inspection.creates_packet) is bool
        and inspection.creates_packet is False
        and type(inspection.creates_receipt) is bool
        and inspection.creates_receipt is False
        and type(inspection.adapter_calls) is int
        and inspection.adapter_calls == 0
        and type(inspection.real_world_effects_count) is int
        and inspection.real_world_effects_count == 0
    )


def _domain_result_cross_bound_v01(
    result: object,
    *,
    domain_shape: str,
    owning_local_root_id: str,
    invalidation_class: str,
    source_reference_status: str,
) -> bool:
    if (
        not _has_exact_dataclass_fields_v01(
            result,
            G2A5DomainProofResultV01,
            _DOMAIN_RESULT_FIELDS_V01,
        )
        or domain_shape not in _DOMAIN_GEOMETRY_V01
    ):
        return False
    replay = result.replay_report
    inspection = result.present_inspection
    if not (
        _lifecycle_replay_report_is_exact_v01(
            replay,
            domain_shape=domain_shape,
        )
        and _present_inspection_is_exact_v01(
            inspection,
            replay=replay,
            domain_shape=domain_shape,
        )
    ):
        return False
    geometry = _DOMAIN_GEOMETRY_V01[domain_shape]
    state = replay.reconstructed_state
    return bool(
        type(result.domain_shape) is str
        and result.domain_shape == domain_shape
        and type(result.source_reference_status) is str
        and result.source_reference_status == source_reference_status
        and type(result.packet_id) is str
        and result.packet_id == geometry["packet_id"]
        and _packet_identity_family_from_result_v01(result)
        and type(result.owning_local_root_id) is str
        and result.owning_local_root_id == owning_local_root_id
        and type(result.transition_registry_id) is str
        and result.transition_registry_id
        == replay.transition_registry_id
        == _SYNTHETIC_TRANSITION_REGISTRY_ID
        and type(result.invalidation_class) is str
        and result.invalidation_class == invalidation_class
        and type(result.authority_effect) is str
        and result.authority_effect == "DETERMINISTIC_BLOCK"
        and type(result.transition_rule_id) is str
        and result.transition_rule_id == "g2a_t09_pending_block"
        and type(result.lifecycle_before) is str
        and result.lifecycle_before == "PENDING_FULFILLMENT"
        and type(result.lifecycle_after) is str
        and result.lifecycle_after == state.lifecycle_state == "BLOCKED"
        and type(result.idempotency_disposition_after) is str
        and result.idempotency_disposition_after
        == state.idempotency_disposition
        == "RESERVED"
        and type(result.reservation_owner_packet_id_after) is str
        and result.reservation_owner_packet_id_after
        == state.reservation_owner_packet_id
        == result.packet_id
        and type(result.generic_authority_law_id) is str
        and result.generic_authority_law_id == _AUTHORITY_LAW_ID
        and type(result.registry_creates_authority) is bool
        and result.registry_creates_authority is False
        and type(result.adapter_calls) is int
        and result.adapter_calls == 0
        and type(result.receipt_creations) is int
        and result.receipt_creations == 0
        and type(result.real_world_effects_count) is int
        and result.real_world_effects_count == 0
    )


def collect_action_commit_packet_lifecycle_g2_a_v01(
) -> ActionCommitPacketLifecycleG2A5ReportV01:
    airline, airline_packet_family = _collect_domain("AIRLINE")
    supplier, supplier_packet_family = _collect_domain("SUPPLIER")
    same_packet_family = bool(
        airline_packet_family
        and supplier_packet_family
        and _packet_identity_family_from_result_v01(airline)
        and _packet_identity_family_from_result_v01(supplier)
    )
    same_registry = (
        airline.transition_registry_id == supplier.transition_registry_id
    )
    same_law = (
        airline.generic_authority_law_id
        == supplier.generic_authority_law_id
        == _AUTHORITY_LAW_ID
    )
    immutable = (
        airline.replay_report.registry_unchanged
        and supplier.replay_report.registry_unchanged
        and airline.present_inspection.historical_result_unchanged
        and supplier.present_inspection.historical_result_unchanged
    )
    adapter_calls = airline.adapter_calls + supplier.adapter_calls
    receipt_creations = (
        airline.receipt_creations + supplier.receipt_creations
    )
    real_world_effects_count = (
        airline.real_world_effects_count
        + supplier.real_world_effects_count
    )
    passed = (
        same_packet_family
        and same_registry
        and same_law
        and immutable
        and _domain_result_cross_bound_v01(
            airline,
            domain_shape="AIRLINE",
            owning_local_root_id="root:g2a5:airline",
            invalidation_class="DEPENDENCY_CHANGED",
            source_reference_status=(
                "INDEPENDENT_ROOT_GEOMETRY_REFERENCE_ONLY_NO_CLOSED_ARTIFACT_RERUN"
            ),
        )
        and _domain_result_cross_bound_v01(
            supplier,
            domain_shape="SUPPLIER",
            owning_local_root_id="root:g2a5:supplier",
            invalidation_class="ROOT_BOUND_KILL_SWITCH",
            source_reference_status=(
                "MIXED_REFERENCE_ONLY_SUPPLIER_B_BLOCKED_SHIPMENT_HELD"
            ),
        )
        and adapter_calls == 0
        and receipt_creations == 0
        and real_world_effects_count == 0
    )
    return ActionCommitPacketLifecycleG2A5ReportV01(
        report_profile_id=_REPORT_PROFILE_ID,
        airline=airline,
        supplier=supplier,
        same_packet_family=same_packet_family,
        same_transition_registry_id=same_registry,
        same_authority_law=same_law,
        immutable_history_proven=immutable,
        closed_domain_artifacts_rerun=False,
        provider_calls=0,
        network_calls=0,
        gemini_calls=0,
        adapter_calls=adapter_calls,
        receipt_creations=receipt_creations,
        real_world_effects_count=real_world_effects_count,
        final_status="PASS" if passed else "FAIL_CLOSED",
    )


def _two_domain_report_is_exact_v01(
    report: object,
) -> bool:
    if not _has_exact_dataclass_fields_v01(
        report,
        ActionCommitPacketLifecycleG2A5ReportV01,
        _FINAL_REPORT_FIELDS_V01,
    ):
        return False
    airline = report.airline
    supplier = report.supplier
    airline_valid = _domain_result_cross_bound_v01(
        airline,
        domain_shape="AIRLINE",
        owning_local_root_id="root:g2a5:airline",
        invalidation_class="DEPENDENCY_CHANGED",
        source_reference_status=(
            "INDEPENDENT_ROOT_GEOMETRY_REFERENCE_ONLY_NO_CLOSED_ARTIFACT_RERUN"
        ),
    )
    supplier_valid = _domain_result_cross_bound_v01(
        supplier,
        domain_shape="SUPPLIER",
        owning_local_root_id="root:g2a5:supplier",
        invalidation_class="ROOT_BOUND_KILL_SWITCH",
        source_reference_status=(
            "MIXED_REFERENCE_ONLY_SUPPLIER_B_BLOCKED_SHIPMENT_HELD"
        ),
    )
    if not (airline_valid and supplier_valid):
        return False
    airline_replay = airline.replay_report
    supplier_replay = supplier.replay_report
    airline_inspection = airline.present_inspection
    supplier_inspection = supplier.present_inspection
    airline_contexts = tuple(
        transition.evaluation_context_id
        for transition in airline_replay.recorded_transitions
    ) + (airline_inspection.evaluation_context_id,)
    supplier_contexts = tuple(
        transition.evaluation_context_id
        for transition in supplier_replay.recorded_transitions
    ) + (supplier_inspection.evaluation_context_id,)
    same_packet_family = bool(
        _packet_identity_family_from_result_v01(airline)
        and _packet_identity_family_from_result_v01(supplier)
        and airline.packet_id != supplier.packet_id
    )
    same_transition_registry = bool(
        airline.transition_registry_id
        == supplier.transition_registry_id
        == _SYNTHETIC_TRANSITION_REGISTRY_ID
    )
    same_authority_law = bool(
        airline.generic_authority_law_id
        == supplier.generic_authority_law_id
        == _AUTHORITY_LAW_ID
    )
    immutable_history = bool(
        airline_replay.registry_unchanged is True
        and supplier_replay.registry_unchanged is True
        and airline_inspection.historical_result_unchanged is True
        and supplier_inspection.historical_result_unchanged is True
    )
    adapter_calls = airline.adapter_calls + supplier.adapter_calls
    receipt_creations = (
        airline.receipt_creations + supplier.receipt_creations
    )
    real_world_effects_count = (
        airline.real_world_effects_count
        + supplier.real_world_effects_count
    )
    cross_domain_non_aliasing = bool(
        airline.packet_id != supplier.packet_id
        and airline_replay.rebuilt_idempotency_key
        != supplier_replay.rebuilt_idempotency_key
        and airline_replay.source_root_decision_id
        != supplier_replay.source_root_decision_id
        and airline_replay.source_root_decision_hash
        != supplier_replay.source_root_decision_hash
        and airline_replay.recorded_transitions
        != supplier_replay.recorded_transitions
        and airline_replay.transition_history_sha256
        != supplier_replay.transition_history_sha256
        and airline_replay.disposition_event_ids
        != supplier_replay.disposition_event_ids
        and airline_replay.disposition_history_sha256
        != supplier_replay.disposition_history_sha256
        and airline_replay.invalidation_evidence_ids
        != supplier_replay.invalidation_evidence_ids
        and airline_replay.invalidation_history_sha256
        != supplier_replay.invalidation_history_sha256
        and all(
            airline_context != supplier_context
            for airline_context in airline_contexts
            for supplier_context in supplier_contexts
        )
        and airline_replay.registry_id == supplier_replay.registry_id
        and airline_replay.fulfillment_attempt_evidence_ids
        == supplier_replay.fulfillment_attempt_evidence_ids
        == ()
        and airline_replay.fulfillment_history_sha256
        == supplier_replay.fulfillment_history_sha256
        == _EMPTY_FULFILLMENT_HISTORY_SHA256
    )
    return bool(
        type(report.report_profile_id) is str
        and report.report_profile_id == _REPORT_PROFILE_ID
        and type(report.same_packet_family) is bool
        and report.same_packet_family == same_packet_family is True
        and type(report.same_transition_registry_id) is bool
        and report.same_transition_registry_id
        == same_transition_registry
        is True
        and type(report.same_authority_law) is bool
        and report.same_authority_law == same_authority_law is True
        and type(report.immutable_history_proven) is bool
        and report.immutable_history_proven == immutable_history is True
        and cross_domain_non_aliasing
        and type(report.closed_domain_artifacts_rerun) is bool
        and report.closed_domain_artifacts_rerun is False
        and type(report.provider_calls) is int
        and report.provider_calls == 0
        and type(report.network_calls) is int
        and report.network_calls == 0
        and type(report.gemini_calls) is int
        and report.gemini_calls == 0
        and type(report.adapter_calls) is int
        and report.adapter_calls == adapter_calls == 0
        and type(report.receipt_creations) is int
        and report.receipt_creations == receipt_creations == 0
        and type(report.real_world_effects_count) is int
        and report.real_world_effects_count
        == real_world_effects_count
        == 0
        and type(report.final_status) is str
        and report.final_status == "PASS"
    )


def validate_action_commit_packet_lifecycle_g2_a_report_v01(
    report: object,
) -> tuple[bool, tuple[str, ...]]:
    try:
        if type(report) is not ActionCommitPacketLifecycleG2A5ReportV01:
            return False, ("g2a5_report_type_invalid",)
        if not _two_domain_report_is_exact_v01(report):
            return False, ("g2a5_report_fail_closed",)
        return True, ()
    except Exception:
        return False, ("g2a5_report_invalid",)


def _plain(value: object) -> object:
    if value is None or type(value) in {bool, int, str}:
        return value
    if type(value) is tuple:
        return [_plain(item) for item in value]
    if is_dataclass(value) and not isinstance(value, type):
        return {
            field.name: _plain(getattr(value, field.name))
            for field in fields(value)
        }
    raise ValueError("g2a5_report_invalid")


def render_action_commit_packet_lifecycle_g2_a_v01(
    report: ActionCommitPacketLifecycleG2A5ReportV01,
) -> str:
    valid, reasons = validate_action_commit_packet_lifecycle_g2_a_report_v01(
        report
    )
    if not valid:
        raise ValueError(reasons[0])
    return canonical_json_bytes_v01(_plain(report)).decode("utf-8")


def main() -> int:
    report = collect_action_commit_packet_lifecycle_g2_a_v01()
    valid, _ = validate_action_commit_packet_lifecycle_g2_a_report_v01(report)
    print(render_action_commit_packet_lifecycle_g2_a_v01(report))
    return 0 if valid and report.final_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
