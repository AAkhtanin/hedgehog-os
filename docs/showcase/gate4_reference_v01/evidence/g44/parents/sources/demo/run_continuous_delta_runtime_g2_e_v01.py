"""Deterministic public two-domain G2-E portability proof."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict, dataclass, fields, is_dataclass, replace
import hashlib
import json
import math

import hedgehog.action_commit_packet_v02 as action_commit_packet
import hedgehog.context_packets as context_packets
import hedgehog.drs_g2b_compatibility_v01 as drs_compatibility
import hedgehog.drs_memory_resolution_v01 as drs_resolution
import hedgehog.drs_semantic_address_v01 as drs_semantic
import hedgehog.reuse_certificate_v01 as reuse_certificate
import hedgehog.structured_rationale as structured_rationale
import hedgehog.kernel.continuous_delta_runtime_v01 as g2e
import hedgehog.kernel.execution_mode_router_v01 as g2c
import hedgehog.kernel.fractal_runtime_v02 as g2d
import hedgehog.kernel.root_decision_v01 as root_decision
import hedgehog.kernel.semantic_work_v01 as semantic_work
import hedgehog.kernel.transition_registry_v01 as transition_registry
from hedgehog.domains.airline import semantic_to_contract_binding_v01 as travel_binding
from hedgehog.domains.airline import ticket_purchase_corridor_v01 as travel_corridor
from hedgehog.kernel.abi_v01 import (
    build_kernel_artifact_v01,
    kernel_artifact_to_canonical_ref_v01,
    kernel_artifact_to_plain_dict_v01,
    validate_kernel_artifact_v01,
)
from hedgehog.kernel.integrity_replay_v01 import (
    ArtifactDependencyEdgeV01,
    AuthorityClassBindingV01,
    EvidenceClassBindingV01,
    RootOwnershipBindingV01,
    build_artifact_manifest_v01,
    build_default_seal_profile_v01,
    canonical_json_bytes_v01,
    verify_artifact_replay_v01,
)
from hedgehog.kernel.trust_model_v01 import (
    build_default_component_trust_profiles_v01,
)


__all__ = (
    "ContinuousDeltaRuntimeG2ESubcaseResultV01",
    "ContinuousDeltaRuntimeG2ECaseResultV01",
    "ContinuousDeltaRuntimeG2EReportV01",
    "collect_continuous_delta_runtime_g2_e_v01",
    "validate_continuous_delta_runtime_g2_e_report_v01",
    "continuous_delta_runtime_g2_e_report_to_plain_data_v01",
    "render_continuous_delta_runtime_g2_e_v01",
    "main",
)


REPORT_VERSION = "v0.1"
PROFILE_ID = "continuous_delta_runtime_g2e_two_domain_proof_v01"
REPORT_ID_PREFIX = "g2eproof_v01:"
REPORT_ID_DOMAIN = "HEDGEHOG_G2E_TWO_DOMAIN_REPORT_ID_V01"
CASE_EVIDENCE_DOMAIN = "HEDGEHOG_G2E_TWO_DOMAIN_CASE_EVIDENCE_V01"
SUBCASE_EVIDENCE_DOMAIN = "HEDGEHOG_G2E_TWO_DOMAIN_SUBCASE_EVIDENCE_V01"
SEALED_EVIDENCE_DOMAIN = "HEDGEHOG_G2E_TWO_DOMAIN_SEALED_EVIDENCE_V01"
SEMANTIC_CALL_DOMAIN = "HEDGEHOG_G2E5_SEMANTIC_CALL_FINGERPRINT_V01"
SEMANTIC_RESULT_DOMAIN = "HEDGEHOG_G2E5_SEMANTIC_RESULT_V01"
MUTATED_ARGUMENT_DOMAIN = "HEDGEHOG_G2E5_MUTATED_ARGUMENT_V01"
COMPOSITIONAL_BINDING_PROFILE_V02 = "HEDGEHOG_G2E5_COMPOSITIONAL_BINDING_V02"
_COMPOSITIONAL_BINDING_DOMAIN_V02 = (
    b"HEDGEHOG_G2E5_COMPOSITIONAL_BINDING_V02\x00"
)

EVALUATION_TIME = 1785542400
EVALUATION_UTC = "2026-08-01T00:00:00+00:00"
VALID_TO_UTC = "2026-08-01T01:00:00+00:00"
VALID_TO_TIME = EVALUATION_TIME + 3600

DOMAIN_ORDER = (
    "TRAVEL_POLICY_INFORMATION",
    "WAREHOUSE_MAINTENANCE_INFORMATION",
)

CONSTRUCTIVE_CASE_ORDER = (
    "g2e_case:travel:hold_expiry:v01",
    "g2e_case:travel:price_change:v01",
    "g2e_case:travel:policy_change:v01",
    "g2e_case:travel:unrelated_preference:v01",
    "g2e_case:travel:repeat_idempotent:v01",
    "g2e_case:warehouse:water_filter_stock:v01",
    "g2e_case:warehouse:evidence_validity:v01",
    "g2e_case:warehouse:policy_change:v01",
    "g2e_case:warehouse:safe_sibling:v01",
    "g2e_case:warehouse:repeat_idempotent:v01",
)

_NEGATIVE_ROWS = (
    ("malformed_delta_identity", "delta_id", "g2e_identity_mismatch"),
    ("unvalidated_delta_source", "source_validation", "g2e_delta_source_unvalidated"),
    ("stale_baseline", "baseline_report_or_graph", "g2e_delta_baseline_stale"),
    ("future_observation", "observed_at_utc", "g2e_delta_future_observation"),
    ("invalid_time_window", "validity_window", "g2e_delta_time_invalid"),
    ("duplicate_changed_field", "ordered_changed_bindings", "g2e_delta_duplicate_binding"),
    ("conflicting_duplicate_delta", "conflicting_changed_bindings", "g2e_delta_conflicting_duplicate"),
    ("unknown_field_path", "json_pointer", "g2e_delta_field_path_invalid"),
    ("unknown_changed_artifact", "artifact_id", "g2e_delta_artifact_binding_invalid"),
    ("cross_transaction_substitution", "transaction_id", "g2e_delta_cross_transaction"),
    ("cross_domain_substitution", "domain_id", "g2e_delta_source_unvalidated"),
    ("cross_root_substitution", "owning_root_id", "g2e_delta_cross_root"),
    ("policy_version_substitution", "policy_version", "g2e_delta_policy_version_mismatch"),
    ("schema_version_substitution", "schema_versions", "g2e_delta_schema_version_mismatch"),
    ("dependency_fingerprint_forgery", "dependency_fingerprint_after", "g2e_dependency_fingerprint_forgery"),
    ("dependency_digest_role_collision", "fingerprint_typed_role", "g2e_dependency_fingerprint_role_collision"),
    ("source_history_substitution", "source_history_hash", "g2e_dependency_source_history_mismatch"),
    ("missing_dependency_edge", "ordered_edge_ids", "g2e_dependency_graph_missing_edge"),
    ("extra_unrelated_dependency_edge", "edge_source_or_dependent", "g2e_dependency_edge_unknown_source"),
    ("duplicate_dependency_edge", "edge_identity_pair", "g2e_dependency_edge_duplicate"),
    ("self_dependency_edge", "dependent_equals_dependency", "g2e_dependency_edge_self"),
    ("dependency_cycle", "ordered_graph_edges", "g2e_dependency_graph_cycle"),
    ("unknown_dependency_artifact", "dependency_artifact_id", "g2e_dependency_edge_unknown_source"),
    ("unknown_dependent_artifact", "dependent_artifact_id", "g2e_dependency_edge_unknown_dependent"),
    ("graph_version_substitution", "graph_version", "g2e_dependency_graph_version_mismatch"),
    ("graph_edge_reordering", "canonical_order", "g2e_dependency_graph_ordering_invalid"),
    ("graph_node_bound_overflow", "node_count", "g2e_dependency_graph_bounds_exceeded"),
    ("graph_edge_bound_overflow", "edge_count", "g2e_dependency_graph_bounds_exceeded"),
    ("graph_hop_bound_overflow", "maximum_path", "g2e_affected_hop_bound_exceeded"),
    ("omitted_direct_dependent", "ordered_directly_affected_ids", "g2e_affected_reachable_omitted"),
    ("omitted_transitive_dependent", "ordered_transitively_affected_ids", "g2e_affected_reachable_omitted"),
    ("injected_unrelated_affected_artifact", "affected_partition", "g2e_affected_unrelated_injected"),
    ("affected_set_reordering", "ordered_affected_ids", "g2e_affected_ordering_invalid"),
    ("affected_closure_proof_forgery", "closure_proof_sha256", "g2e_affected_proof_invalid"),
    ("invalidation_reason_substitution", "invalidation_reason_class", "g2e_invalidation_reason_invalid"),
    ("deletion_disguised_as_invalidation", "deleted", "g2e_invalidation_deletion_forbidden"),
    ("invalidation_predecessor_mismatch", "predecessor_artifact_id", "g2e_invalidation_predecessor_mismatch"),
    ("invalidation_supersession_mismatch", "superseded_by_artifact_id", "g2e_invalidation_supersession_mismatch"),
    ("preserved_payload_mutation", "preserved_payload_hash", "g2e_preserved_artifact_changed"),
    ("preserved_identity_mutation", "preserved_identity", "g2e_preserved_identity_changed"),
    ("hidden_cache_mutation", "no_cache_state", "g2e_preservation_cache_mutation"),
    ("in_place_recomputation", "prior_and_new_identity", "g2e_recomputation_in_place_forbidden"),
    ("stale_reuse_certificate_retained_current", "g2b_certificate_currentness", "g2e_invalidation_g2b_reuse_still_current"),
    ("packet_kept_executable_after_invalidation", "g2a_present_eligibility", "g2e_invalidation_g2a_root_binding_required"),
    ("packet_revoked_without_root_seam", "g2a_revocation_binding", "g2e_invalidation_g2a_root_binding_required"),
    ("route_reused_after_bound_source_change", "route_or_topology_binding", "g2e_route_revalidation_required"),
    ("child_input_topology_mismatch", "cell_input_topology", "g2e_recomputation_plan_invalid"),
    ("result_report_binding_mismatch", "g2d_result_report", "g2e_recomputation_result_invalid"),
    ("post_vv_gt_binding_mismatch", "post_vv_gt_refs", "g2e_recomputation_result_invalid"),
    ("direct_root_decision_bypass", "root_review_transition", "g2e_authority_boundary_violated"),
    ("caller_supplied_pass_reason_status", "validation_report", "g2e_status_invalid"),
    ("object_identity_presented_as_proof", "preservation_proof", "g2e_preservation_proof_invalid"),
    (
        "repeated_delta_spin",
        "repeated_work_frontier",
        (
            "g2e_recomputation_no_progress",
            "g2e_transition_selective_recomputation_blocked",
        ),
    ),
    ("hidden_mutable_global_state", "independent_call_result", "g2e_preservation_cache_mutation"),
    ("unbounded_affected_closure", "closure_limits", "g2e_dependency_graph_bounds_exceeded"),
    ("nonzero_provider_calls", "provider_calls", "g2e_zero_operation_boundary_violated"),
    ("nonzero_model_calls", "model_calls", "g2e_zero_operation_boundary_violated"),
    ("nonzero_network_calls", "network_calls", "g2e_zero_operation_boundary_violated"),
    ("nonzero_connector_calls", "connector_calls", "g2e_zero_operation_boundary_violated"),
    ("nonzero_external_drs_calls", "external_drs_calls", "g2e_zero_operation_boundary_violated"),
    ("nonzero_drs_writes", "drs_writes", "g2e_zero_operation_boundary_violated"),
    ("nonzero_action_packets", "action_commit_packets_created", "g2e_zero_operation_boundary_violated"),
    ("nonzero_permissions", "permissions_created", "g2e_zero_operation_boundary_violated"),
    ("nonzero_receipts", "receipts_created", "g2e_zero_operation_boundary_violated"),
    ("nonzero_final_outputs", "final_outputs_created", "g2e_zero_operation_boundary_violated"),
    ("nonzero_authority", "authority_created_count", "g2e_authority_boundary_violated"),
    ("nonzero_real_world_effects", "real_world_effects_count", "g2e_zero_operation_boundary_violated"),
    ("missing_changed_binding_carrier", "delta_referenced_binding", "g2e_delta_binding_set_mismatch"),
    ("unreferenced_changed_binding_injection", "unreferenced_binding", "g2e_delta_binding_set_mismatch"),
    ("source_binding_set_mismatch", "ordered_source_binding_ids", "g2e_delta_source_binding_set_mismatch"),
    ("dependency_edge_carrier_mismatch", "ordered_edge_ids", "g2e_dependency_edge_set_mismatch"),
    ("graph_basis_identity_mismatch", "graph_basis_sha256", "g2e_dependency_graph_basis_mismatch"),
    ("source_replay_edge_fingerprint_mismatch", "source_replay_edge_sha256", "g2e_dependency_replay_edge_mismatch"),
    ("source_payload_pointer_unavailable", "source_payload_pointer", "g2e_dependency_source_payload_unavailable"),
    ("baseline_observed_source_pair_substitution", "source_pair", "g2e_delta_source_binding_set_mismatch"),
    ("observed_source_payload_hash_mismatch", "observed_payload_hash", "g2e_delta_artifact_binding_invalid"),
    ("dependency_fingerprint_before_after_swap", "fingerprint_arguments", "g2e_dependency_fingerprint_mismatch"),
    ("invalidation_binding_carrier_omission", "triggering_binding", "g2e_invalidation_record_invalid"),
    ("selective_execution_carrier_omission", "execution_carrier", "g2e_recomputation_plan_invalid"),
    ("recomputed_g2d_result_report_ref_substitution", "result_report_preservation_partial", "g2e_recomputation_result_invalid"),
    ("preserved_full_artifact_bytes_mutation", "canonical_artifact_bytes", "g2e_preserved_artifact_changed"),
    ("unsupported_sequential_delta", "delta_sequence_or_prior_delta", "g2e_repeated_delta_conflict"),
    ("plan_root_review_carrier_substitution", "plan_root_carriers", "g2e_recomputation_plan_invalid"),
    ("final_root_review_carrier_substitution", "final_root_carriers", "g2e_recomputation_result_invalid"),
    ("root_acceptance_outcome_forgery", "root_acceptance_or_effect", "g2e_authority_boundary_violated"),
    ("transition_rule_eleven_field_substitution", "transition_rule_fields", "g2e_object_invalid"),
    ("transition_rule_order_or_terminal_path_forgery", "transition_order_terminal", "g2e_object_invalid"),
    ("abi_projection_profile_substitution", "abi_profile_fields", "g2e_object_invalid"),
    ("abi_parent_trace_or_root_artifact_substitution", "abi_parent_trace_root", "g2e_object_invalid"),
    ("identity_prefix_or_domain_collision", "identity_prefix_or_domain", "g2e_identity_mismatch"),
)

NEGATIVE_CASE_ORDER = tuple(
    "g2e_case:negative:" + suffix + ":v01"
    for suffix, _axis, _reason in _NEGATIVE_ROWS
)
CASE_ORDER = CONSTRUCTIVE_CASE_ORDER + NEGATIVE_CASE_ORDER


@dataclass(frozen=True)
class ContinuousDeltaRuntimeG2ESubcaseResultV01:
    subcase_id: str
    mutated_axis: str
    validation_target: str
    expected_reason_codes: tuple[str, ...]
    observed_reason_codes: tuple[str, ...]
    validation_report_id: str
    evidence_refs: tuple[str, ...]
    evidence_material_json: str
    evidence_sha256: str
    final_status: str


@dataclass(frozen=True)
class ContinuousDeltaRuntimeG2ECaseResultV01:
    case_id: str
    case_class: str
    domain_id: str
    expected_outcome: str
    observed_outcome: str
    baseline_runtime_report_id: str | None
    delta_id: str | None
    affected_set_id: str | None
    invalidation_report_id: str | None
    recomputation_plan_id: str | None
    recomputation_result_id: str | None
    continuous_delta_runtime_report_id: str | None
    ordered_changed_ids: tuple[str, ...]
    ordered_directly_affected_ids: tuple[str, ...]
    ordered_transitively_affected_ids: tuple[str, ...]
    ordered_invalidated_ids: tuple[str, ...]
    ordered_recomputed_ids: tuple[str, ...]
    ordered_preserved_ids: tuple[str, ...]
    ordered_unresolved_or_blocked_ids: tuple[str, ...]
    ordered_root_review_ids: tuple[str, ...]
    subcase_results: tuple[ContinuousDeltaRuntimeG2ESubcaseResultV01, ...]
    expected_reason_codes: tuple[str, ...]
    observed_reason_codes: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    evidence_material_json: str
    evidence_sha256: str
    provider_calls: int
    model_calls: int
    network_calls: int
    connector_calls: int
    external_drs_calls: int
    action_commit_packets_created: int
    permissions_created: int
    receipts_created: int
    final_outputs_created: int
    drs_writes: int
    authority_created_count: int
    real_world_effects_count: int
    final_status: str
    reason_codes: tuple[str, ...]


@dataclass(frozen=True)
class ContinuousDeltaRuntimeG2EReportV01:
    report_version: str
    report_id: str
    profile_id: str
    domain_order: tuple[str, ...]
    case_order: tuple[str, ...]
    case_results: tuple[ContinuousDeltaRuntimeG2ECaseResultV01, ...]
    constructive_case_count: int
    negative_case_count: int
    total_case_count: int
    accepted_baseline_bundle_count: int
    explicit_public_g2d_baseline_call_count: int
    source_collectors_replayed: bool
    source_evidence_mode: str
    sealed_evidence_sha256: str
    provider_calls: int
    model_calls: int
    network_calls: int
    connector_calls: int
    external_drs_calls: int
    action_commit_packets_created: int
    permissions_created: int
    receipts_created: int
    final_outputs_created: int
    drs_writes: int
    authority_created_count: int
    real_world_effects_count: int
    final_status: str
    reason_codes: tuple[str, ...]


def _canonical_json_text(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _sha256_domain(domain: str, value: object) -> str:
    return hashlib.sha256(
        domain.encode("ascii") + b"\x00" + _canonical_json_text(value).encode("ascii")
    ).hexdigest()


def _prefixed_identity(prefix: str, domain: str, value: object) -> str:
    return prefix + _sha256_domain(domain, value)


def _domain_slug(domain_id: str) -> str:
    return "travel" if domain_id == DOMAIN_ORDER[0] else "warehouse"


def _semantic_case_id(case_id: str) -> str:
    if case_id == "g2e_case:travel:repeat_idempotent:v01":
        return "g2e_case:travel:hold_expiry:v01"
    if case_id == "g2e_case:warehouse:repeat_idempotent:v01":
        return "g2e_case:warehouse:water_filter_stock:v01"
    return case_id


def _build_bsep_family(domain_id: str, request_id: str) -> dict[str, object]:
    slug = _domain_slug(domain_id)
    route_id = f"route:g2e5:{slug}:full-fractal"
    proposal_id = f"proposal:g2e5:{slug}:full-fractal"
    vector_ids = (f"vector:g2e5:{slug}:full-fractal",)
    guards = ("guard:g2e5:root-review",)
    business = context_packets.build_business_request_context_packet(
        packet_id=f"context_packet:g2e5:{slug}:business",
        created_by="runtime:g2e5:proof",
        domain=domain_id,
        request_id=request_id,
        business_subject="bounded_runtime_topology",
        requested_action="root_review",
        user_visible_summary="Bounded topology source review.",
    )
    business_ref = {
        "source": "G2C_BUSINESS_REQUEST_CONTEXT_PACKET_V01",
        "packet_id": business["packet_id"],
        "request_id": request_id,
        "domain_id": domain_id,
    }
    route = context_packets.build_orchestrator_route_context_packet(
        packet_id=f"context_packet:g2e5:{slug}:route",
        created_by="runtime:g2e5:proof",
        source_refs=(business_ref,),
        domain=domain_id,
        allowed_routes=(route_id,),
        required_guards=guards,
        selected_vector_ids=vector_ids,
        route_validation_expectations={
            "root_review_required": True,
            "selected_only_allowed_vectors": True,
        },
        orchestrator_is_root=False,
        creates_action_commit_packet=False,
        calls_connectors=False,
    )
    proposal = {
        "proposal_id": proposal_id,
        "suggested_route": route_id,
        "selected_vector_ids": vector_ids,
        "required_guards": guards,
        "reason": "Bounded deterministic topology review is required.",
        "confidence": 0.66,
        "needs_review": True,
        "uncertainty_notes": ("Source evidence remains advisory.",),
        "root_review_required": True,
        "truth_claimed": False,
        "authority_claimed": False,
        "action_permission_claimed": False,
        "final_output_claimed": False,
        "connector_command_claimed": False,
        "drs_write_claimed": False,
        "plan_graph_claimed": False,
        "bypass_root_claimed": False,
        "semantic_observations": ("A bounded topology route is available.",),
        "route_reasoning": ("Use deterministic mode selection.",),
        "rejected_route_reasoning": ("Unsupported action remains forbidden.",),
        "guard_reasoning": ("Root review remains mandatory.",),
        "vector_reasoning": ("The bounded vector matches the request.",),
        "authority_boundary_reasoning": ("Root remains final authority.",),
    }
    rationale = structured_rationale.build_orchestrator_structured_rationale(
        observed_semantics=proposal["semantic_observations"],
        route_selection_reason=proposal["route_reasoning"],
        rejected_routes=proposal["rejected_route_reasoning"],
        required_guards_reasoning=proposal["guard_reasoning"],
        selected_vector_reasoning=proposal["vector_reasoning"],
        uncertainty_notes=proposal["uncertainty_notes"],
        authority_boundary=proposal["authority_boundary_reasoning"],
        root_review_required=True,
    )
    rationale_sha = hashlib.sha256(canonical_json_bytes_v01(rationale)).hexdigest()

    def item(text: str, kind: str) -> dict[str, object]:
        return context_packets.semantic_evidence_item(
            text,
            source="runtime_canonicalization",
            evidence_kind=kind,
            confidence_label="medium",
        )

    packet = context_packets.build_bounded_semantic_evidence_packet(
        packet_id=f"context_packet:g2e5:{slug}:bsep",
        source_refs=(business_ref,),
        domain=domain_id,
        source_role="orchestrator",
        target_role="architect",
        source_route_id=route_id,
        source_proposal_id=proposal_id,
        source_context_packet_id=route["packet_id"],
        source_structured_rationale_ref="structured_rationale_v01:" + rationale_sha,
        observed_semantic_facts=(item("A bounded route is present.", "observed_fact"),),
        missing_evidence=(item("Root review is pending.", "missing_evidence"),),
        uncertainty_notes=(item("Source evidence remains advisory.", "uncertainty"),),
        risk_boundary_notes=(item("No action authority is present.", "risk_boundary"),),
        rejected_action_routes=(item("Unsupported action is forbidden.", "rejected_route"),),
        required_approvals_or_conditions=(item("Root review is required.", "approval_condition"),),
        authority_boundary_notes=(item("Root remains final authority.", "authority_boundary"),),
        selected_vector_ids=vector_ids,
        required_guards=guards,
    )
    return {
        "business": business,
        "route": route,
        "proposal": proposal,
        "rationale": rationale,
        "packet": packet,
    }


def _sha(label: str) -> str:
    return hashlib.sha256(label.encode("ascii")).hexdigest()


def _build_root_acceptance(
    *,
    label: str,
    transaction_id: str,
    root_id: str,
    candidate_id: str,
    subject: str,
    evidence_ref: str,
    policy_id: str,
    time_envelope_ref: str,
    permission_required: bool,
    permission_ref: str | None,
) -> tuple[
    root_decision.RootDecisionKernelV01,
    root_decision.RootDecisionInputV01,
    root_decision.RootDecisionResultV01,
]:
    actor_id = f"runtime:g2e5:{label}"
    request = semantic_work.build_semantic_work_request_v01(
        request_id=f"semantic_request:g2e5:{label}",
        transaction_id=transaction_id,
        target_root_id=root_id,
        runtime_topology_ref=f"runtime_topology:g2e5:{label}",
        bounded_context_refs=(f"context:g2e5:{label}",),
        permitted_actor_ids=(actor_id,),
        permitted_contribution_modes=("DETERMINISTIC",),
        requested_subjects=(subject,),
        required_evidence_classes=("SOURCE_EVIDENCE",),
        forbidden_claims=("authority_creation", "external_effect"),
    )
    evidence = semantic_work.build_evidence_binding_v01(
        evidence_id=f"evidence_binding:g2e5:{label}",
        evidence_ref=evidence_ref,
        evidence_class="SOURCE_EVIDENCE",
        source_component_id=actor_id,
        provenance_ref=f"provenance:g2e5:{label}",
        evidence_state=semantic_work.EVIDENCE_STATE_PRESENT,
    )
    claim = semantic_work.build_normalized_claim_v01(
        claim_id=candidate_id,
        subject=subject,
        predicate="root_packet_authorization_candidate",
        object_or_value={
            "candidate_id": candidate_id,
            "candidate_kind": "PACKET_AUTHORIZATION",
        },
        time_envelope_ref=time_envelope_ref,
        provenance_refs=(f"provenance:g2e5:{label}",),
        evidence_refs=(evidence.evidence_id,),
        confidence_micros=1_000_000,
        source_role="deterministic_runtime",
        source_mode="DETERMINISTIC",
    )
    contribution = semantic_work.build_actor_contribution_v01(
        contribution_id=f"contribution:g2e5:{label}",
        request_id=request.request_id,
        actor_id=actor_id,
        actor_role="deterministic_runtime",
        contribution_mode="DETERMINISTIC",
        bsep_projection_ref=f"bsep:g2e5:{label}",
        scope=f"scope:g2e5:{label}",
        bounded_context_refs=(f"context:g2e5:{label}",),
        claims=(claim,),
        evidence_bindings=(evidence,),
        constraint_bindings=(),
        uncertainty_bindings=(),
        requested_validators=(f"validator:g2e5:{label}",),
        forbidden_claims_observed=(),
    )
    review_packet = semantic_work.build_root_review_packet_from_contributions_v01(
        request=request,
        contributions=(contribution,),
        trust_profiles=build_default_component_trust_profiles_v01(),
    )
    kernel = root_decision.build_root_decision_kernel_v01()
    decision_input = root_decision.build_root_decision_input_v01(
        transaction_id=transaction_id,
        target_root_id=root_id,
        root_review_packet=review_packet,
        post_vv_bundle={
            "bundle_id": f"post_vv:g2e5:{label}",
            "post_vv_passed": True,
            "validated_candidate_ids": [candidate_id],
            "rejected_candidate_ids": [],
            "required_evidence_refs": [evidence_ref],
            "provided_evidence_refs": [evidence_ref],
            "hard_failure_reasons": [],
        },
        gt_advisory={
            "advisory_id": f"gt:g2e5:{label}",
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
            "policy_id": policy_id,
            "identity_passed": True,
            "scope_passed": True,
            "hard_policy_passed": True,
            "allow_accept": True,
            "conflict_policy": "DEFER",
            "no_candidate_policy": "NO_UPDATE",
        },
        permission_state={
            "permission_required": permission_required,
            "user_permission_present": permission_required,
            "permission_scope_valid": True,
            "permission_ref": permission_ref,
        },
        temporal_state={
            "temporal_valid": True,
            "expired": False,
            "not_before_satisfied": True,
            "time_envelope_ref": time_envelope_ref,
        },
        conflict_state={
            "material_unresolved_conflict": False,
            "conflict_set_ids": list(review_packet.conflict_set_ids),
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
    if result.decision != "ACCEPT":
        raise ValueError("g2e5_root_source_acceptance_failed")
    return kernel, decision_input, result


def _build_g2b_family(domain_id: str, root_id: str) -> dict[str, object]:
    slug = _domain_slug(domain_id)
    scope_ref = f"scope:g2e5:{slug}:g2b"
    scope_sha256 = _sha(scope_ref)
    address = drs_semantic.build_semantic_address_v01(
        namespace=f"g2e5_{slug}_v01",
        domain=domain_id,
        subject_class="bounded_information",
        intent_class="informational_summary",
        meaning_schema_id="drs_meaning_record",
        meaning_schema_version="v0.1",
    )
    envelope = drs_semantic.build_drs_time_envelope_v01(
        pt_created_at=EVALUATION_TIME,
        kt_as_of=EVALUATION_TIME,
        et_observed_at=EVALUATION_TIME,
        ct_context_anchor=EVALUATION_TIME,
        ttl_seconds=3600,
        valid_from=EVALUATION_TIME,
        valid_to=VALID_TO_TIME,
        source_observed_at=EVALUATION_TIME,
        source_reported_at=EVALUATION_TIME,
        system_ingested_at=EVALUATION_TIME,
        system_verified_at=EVALUATION_TIME,
        freshness_policy_id=f"freshness:g2e5:{slug}:v01",
    )
    authority = drs_semantic.build_drs_authority_envelope_v01(
        authority_class="ROOT_ACCEPTED_WORK",
        owning_local_root_id=root_id,
        source_root_decision_input_id=f"root-input:g2e5:{slug}:source",
        source_root_decision_id=f"root-decision:g2e5:{slug}:source",
        source_root_decision_hash=_sha(f"g2e5-{slug}-source-root"),
        authority_scope_fingerprint=scope_sha256,
        root_acceptance_state="ACCEPTED_WORK",
        recording_component="continuous_delta_runtime_g2e5",
    )
    record = drs_semantic.build_meaning_record_v01(
        semantic_address=address,
        predecessor_record_id=None,
        supersession_reason=None,
        safe_summary=f"Bounded deterministic {slug} source context.",
        semantic_tags=("bounded", "g2e5", slug),
        resonance_reason="Exact deterministic semantic-address match.",
        memory_pointers=(),
        artifact_pointers=(),
        source_reference_ids=(f"source:g2e5:{slug}:g2b",),
        lineage_edges=(),
        time_envelope=envelope,
        authority_envelope=authority,
        persistent_lifecycle_state="ACTIVE",
        risk_hints=(),
        conflict_hints=(),
        reuse_policy_class="ANSWER_SHORTCUT",
        policy_version=f"policy:g2e5:{slug}:v01",
        schema_versions=("v0.1",),
        content_fingerprint=_sha(f"g2e5-{slug}-meaning-record"),
        recording_component="continuous_delta_runtime_g2e5",
    )
    query = drs_resolution.build_drs_temporal_query_v01(
        query_mode="DIRECT_REUSE_CANDIDATE",
        semantic_address_id=address.semantic_address_id,
        scope_fingerprint=scope_sha256,
        as_of=EVALUATION_TIME,
        evaluation_time=EVALUATION_TIME,
        evaluation_time_source="INJECTED_CURRENT_DECISION_TIME",
        time_range_start=EVALUATION_TIME,
        time_range_end=VALID_TO_TIME,
        required_time_axes=("PT", "KT", "ET", "CT", "TTL", "VALIDITY"),
        freshness_policy_id=f"freshness:g2e5:{slug}:v01",
        max_age_seconds=3600,
        domain=domain_id,
        risk_class="LOW",
        reuse_intent="INFORMATIONAL_SHORTCUT_CONSIDERATION",
        requested_reuse_classes=("ANSWER_SHORTCUT",),
        required_evidence_classes=(
            "SOURCE_IDENTITY",
            "SOURCE_INTEGRITY",
            "PROVENANCE_CHAIN",
            "TIME_FITNESS",
            "POLICY_COMPATIBILITY",
            "SCHEMA_COMPATIBILITY",
            "CONFLICT_CLEARANCE",
            "ROOT_DECISION",
            "SOURCE_HISTORY",
        ),
        forbidden_changes=("POLICY_CHANGED",),
        policy_version=f"policy:g2e5:{slug}:v01",
        schema_versions=("v0.1",),
        owning_local_root_id=root_id,
    )
    evaluation = drs_resolution.evaluate_drs_candidate_v01(
        semantic_address=address,
        query=query,
        meaning_record=record,
        action_history_binding=None,
    )
    projection = drs_compatibility.build_legacy_drs_projection_v01(
        source_family="LOCAL_DRS_DICT",
        source={
            "record_id": f"legacy:g2e5:{slug}:g2b",
            "layer": "work",
            "type": "generic",
            "domain": domain_id,
            "content": {"summary": f"Bounded {slug} memory context."},
            "time_envelope": {
                "pt_created_at": EVALUATION_UTC,
                "kt_asof": EVALUATION_UTC,
                "et_observed_at": EVALUATION_UTC,
                "ct_session_anchor": f"case:g2e5:{slug}:g2b",
                "ttl_seconds": 3600,
                "freshness_class": "static",
                "valid_from": EVALUATION_UTC,
                "valid_to": VALID_TO_UTC,
            },
            "provenance": {
                "request_id": f"request:g2e5:{slug}:g2b",
                "created_by": "root_orchestrator",
                "trace_refs": [],
            },
            "status": "active",
        },
        target_semantic_address=address,
    )
    budget = drs_resolution.build_memory_descent_budget_v01(
        max_depth=0,
        max_records_opened=1,
        max_pointers_opened=0,
        max_artifacts_opened=0,
        max_bytes_opened=0,
        max_lineage_edges=0,
        max_conflict_records=0,
    )
    plan = drs_resolution.build_retrieval_plan_v01(
        query_id=query.query_id,
        semantic_address_id=address.semantic_address_id,
        proposed_record_ids=(record.meaning_record_id,),
        proposed_memory_pointer_ids=(),
        proposed_artifact_pointer_ids=(),
        requested_descent_class="SUMMARY_ONLY",
        proposed_budget_id=budget.memory_descent_budget_id,
        required_access_policy_ids=(),
        reason_codes=(),
    )
    candidate = drs_resolution.build_resolution_candidate_v01(
        query_id=query.query_id,
        semantic_address_id=query.semantic_address_id,
        meaning_record_id=record.meaning_record_id,
        query_evaluation_id=evaluation.query_evaluation_id,
        safe_summary=record.safe_summary,
        evidence_ref_ids=record.source_reference_ids,
        source_history_hash=evaluation.source_history_hash,
        action_history_binding_id=None,
        semantic_similarity_units=9000,
        freshness_units=evaluation.current_freshness_units,
        source_authority_prior_units=9000,
        lineage_proximity_units=7000,
        historical_utility_units=6000,
        gt_advisory_prior_units=1000,
        conflict_penalty_units=0,
        risk_penalty_units=0,
        retrieval_cost_units=100,
    )
    ranked = drs_resolution.rank_eligible_drs_candidates_v01(
        query=query,
        query_evaluations=(evaluation,),
        candidates=(candidate,),
    )
    claim_preimage = {
        "profile_version": "v0.1",
        "semantic_address_id": address.semantic_address_id,
        "meaning_record_id": record.meaning_record_id,
        "query_id": query.query_id,
        "query_evaluation_id": evaluation.query_evaluation_id,
        "resolution_candidate_id": candidate.resolution_candidate_id,
        "reuse_class": "ANSWER_SHORTCUT",
        "case_type": "NON_ACTION_INFORMATIONAL",
        "scope_fingerprint": query.scope_fingerprint,
        "policy_version": query.policy_version,
        "schema_versions": list(query.schema_versions),
        "required_evidence_classes": list(query.required_evidence_classes),
        "observed_evidence_fingerprint": evaluation.observed_evidence_fingerprint,
        "forbidden_changes": list(query.forbidden_changes),
        "checked_dependency_fingerprint": evaluation.checked_dependency_fingerprint,
        "source_history_hash": evaluation.source_history_hash,
        "action_history_binding_id": None,
        "valid_from": EVALUATION_TIME,
        "valid_to": VALID_TO_TIME,
        "issued_at": EVALUATION_TIME,
        "evaluated_at": evaluation.evaluated_at,
        "root_shortcut_policy_ref": "policy:drs_answer_shortcut:v0.1",
    }
    actor_id = f"runtime:g2e5:{slug}:g2b"
    work_request = semantic_work.build_semantic_work_request_v01(
        request_id=f"semantic_request:g2e5:{slug}:g2b",
        transaction_id=query.query_id,
        target_root_id=root_id,
        runtime_topology_ref=f"runtime_topology:g2e5:{slug}:g2b",
        bounded_context_refs=(f"context:g2e5:{slug}:g2b",),
        permitted_actor_ids=(actor_id,),
        permitted_contribution_modes=("DETERMINISTIC",),
        requested_subjects=(address.semantic_address_id,),
        required_evidence_classes=("ROOT_SHORTCUT_BINDING",),
        forbidden_claims=("create_permission",),
    )
    evidence = semantic_work.build_evidence_binding_v01(
        evidence_id=f"evidence_binding:g2e5:{slug}:g2b",
        evidence_ref=f"evidence:g2e5:{slug}:g2b",
        evidence_class="ROOT_SHORTCUT_BINDING",
        source_component_id=actor_id,
        provenance_ref=f"provenance:g2e5:{slug}:g2b",
        evidence_state=semantic_work.EVIDENCE_STATE_PRESENT,
    )
    claim = semantic_work.build_normalized_claim_v01(
        claim_id=candidate.resolution_candidate_id,
        subject=address.semantic_address_id,
        predicate="authorize_non_action_informational_answer_shortcut_v01",
        object_or_value=claim_preimage,
        time_envelope_ref=f"time-envelope:g2e5:{slug}:g2b",
        provenance_refs=(f"provenance:g2e5:{slug}:g2b",),
        evidence_refs=(evidence.evidence_id,),
        confidence_micros=1_000_000,
        source_role="deterministic_runtime",
        source_mode="DETERMINISTIC",
    )
    contribution = semantic_work.build_actor_contribution_v01(
        contribution_id=f"contribution:g2e5:{slug}:g2b",
        request_id=work_request.request_id,
        actor_id=actor_id,
        actor_role="deterministic_runtime",
        contribution_mode="DETERMINISTIC",
        bsep_projection_ref=f"bsep:g2e5:{slug}:g2b",
        scope=address.semantic_address_id,
        bounded_context_refs=(f"context:g2e5:{slug}:g2b",),
        claims=(claim,),
        evidence_bindings=(evidence,),
        constraint_bindings=(),
        uncertainty_bindings=(),
        requested_validators=(),
        forbidden_claims_observed=(),
    )
    review_packet = semantic_work.build_root_review_packet_from_contributions_v01(
        request=work_request,
        contributions=(contribution,),
        trust_profiles=build_default_component_trust_profiles_v01(),
    )
    root_kernel = root_decision.build_root_decision_kernel_v01()
    root_input = root_decision.build_root_decision_input_v01(
        transaction_id=query.query_id,
        target_root_id=root_id,
        root_review_packet=review_packet,
        post_vv_bundle={
            "bundle_id": f"post_vv:g2e5:{slug}:g2b",
            "post_vv_passed": True,
            "validated_candidate_ids": [candidate.resolution_candidate_id],
            "rejected_candidate_ids": [],
            "required_evidence_refs": [],
            "provided_evidence_refs": [],
            "hard_failure_reasons": [],
        },
        gt_advisory={
            "advisory_id": f"gt:g2e5:{slug}:g2b",
            "candidate_ids": [candidate.resolution_candidate_id],
            "selected_candidate_id": candidate.resolution_candidate_id,
            "score_micros_by_candidate": {
                candidate.resolution_candidate_id: 500_000
            },
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
            "policy_id": f"policy:g2e5:{slug}:g2b",
            "identity_passed": True,
            "scope_passed": True,
            "hard_policy_passed": True,
            "allow_accept": True,
            "conflict_policy": "DEFER",
            "no_candidate_policy": "NO_UPDATE",
        },
        permission_state={
            "permission_required": False,
            "user_permission_present": False,
            "permission_scope_valid": True,
            "permission_ref": None,
        },
        temporal_state={
            "temporal_valid": True,
            "expired": False,
            "not_before_satisfied": True,
            "time_envelope_ref": f"time-envelope:g2e5:{slug}:g2b",
        },
        conflict_state={
            "material_unresolved_conflict": False,
            "conflict_set_ids": [],
        },
        prior_root_state={
            "prior_decision_id": None,
            "prior_decision": None,
            "prior_selected_candidate_id": None,
        },
    )
    root_result = root_decision.decide_root_v01(
        kernel=root_kernel,
        decision_input=root_input,
    )
    root_hash = g2e.domain_separated_sha256_hex_v01(
        domain="hedgehog:drs:root_shortcut_root_result_binding:v01",
        payload=canonical_json_bytes_v01(
            root_decision.root_decision_result_to_plain_dict_v01(root_result)
        ),
    )
    root_projection = reuse_certificate.build_root_shortcut_authorization_projection_v01(
        owning_local_root_id=root_id,
        root_kernel_id=root_kernel.kernel_id,
        root_decision_input_id=root_input.decision_input_id,
        root_decision_id=root_result.decision_id,
        root_decision_hash=root_hash,
        selected_candidate_id=candidate.resolution_candidate_id,
        semantic_address_id=address.semantic_address_id,
        meaning_record_id=record.meaning_record_id,
        query_id=query.query_id,
        query_evaluation_id=evaluation.query_evaluation_id,
        allowed_reuse_class="ANSWER_SHORTCUT",
        scope_fingerprint=scope_sha256,
        policy_version=query.policy_version,
        schema_versions=query.schema_versions,
        valid_from=EVALUATION_TIME,
        valid_to=VALID_TO_TIME,
        root_shortcut_policy_ref="policy:drs_answer_shortcut:v0.1",
    )
    certificate = reuse_certificate.build_reuse_certificate_v01(
        semantic_address_id=address.semantic_address_id,
        meaning_record_id=record.meaning_record_id,
        query_id=query.query_id,
        query_evaluation_id=evaluation.query_evaluation_id,
        resolution_candidate_id=candidate.resolution_candidate_id,
        root_shortcut_authorization_projection=root_projection,
        case_type="NON_ACTION_INFORMATIONAL",
        required_evidence_classes=query.required_evidence_classes,
        observed_evidence_fingerprint=evaluation.observed_evidence_fingerprint,
        forbidden_changes=query.forbidden_changes,
        checked_dependency_fingerprint=evaluation.checked_dependency_fingerprint,
        valid_from=EVALUATION_TIME,
        valid_to=VALID_TO_TIME,
        reuse_class="ANSWER_SHORTCUT",
        source_history_hash=evaluation.source_history_hash,
        action_history_binding_id=None,
        issued_at=EVALUATION_TIME,
        evaluated_at=evaluation.evaluated_at,
    )
    report = drs_resolution.build_drs_resolution_report_v01(
        semantic_address=address,
        query=query,
        source_projections=(projection,),
        source_records=(record,),
        query_evaluations=(evaluation,),
        eligible_candidates=(candidate,),
        ranked_candidate_ids=tuple(item.resolution_candidate_id for item in ranked),
        selected_candidate_id=candidate.resolution_candidate_id,
        retrieval_plan=plan,
        memory_descent_result=None,
        root_shortcut_projection=root_projection,
        reuse_certificate=certificate,
        context_only_record_ids=(),
        historical_only_record_ids=(),
        warning_only_record_ids=(),
        rerun_required_record_ids=(),
        blocked_record_ids=(),
        provider_calls=0,
        network_calls=0,
        gemini_calls=0,
        external_drs_calls=0,
        connector_calls=0,
        real_world_effects_count=0,
        final_status="PASS",
        reason_codes=(),
    )
    report_validation_result = drs_resolution.validate_drs_resolution_report_v01(
        report
    )
    valid_report, report_reasons = report_validation_result
    certificate_validation_result = reuse_certificate.validate_reuse_certificate_v01(
        certificate
    )
    valid_certificate, certificate_reasons = certificate_validation_result
    if not valid_report or report_reasons or not valid_certificate or certificate_reasons:
        raise ValueError("g2e5_g2b_source_invalid")
    return {
        "transaction_id": query.query_id,
        "report": report,
        "certificate": certificate,
        "projections": (projection,),
        "root_kernel": root_kernel,
        "root_input": root_input,
        "root_result": root_result,
        "validation_returns": (
            report_validation_result,
            certificate_validation_result,
        ),
    }


def _build_g2a_family(
    *, domain_id: str, root_id: str, transaction_id: str
) -> dict[str, object]:
    slug = _domain_slug(domain_id)
    dependency_id = (
        "dependency:g2e5:travel:hold-source"
        if domain_id == DOMAIN_ORDER[0]
        else "dependency:g2a5:supplier:primary"
    )
    evidence_ref = f"evidence:g2e5:{slug}:source"
    content_sha256 = _sha(f"g2e5-{slug}-dependency-baseline")
    freshness = f"freshness:g2e5:{slug}:v01"
    provenance = (f"source:g2e5:{slug}:dependency",)
    envelope_id = action_commit_packet.build_action_dependency_time_envelope_id_v01(
        dependency_id=dependency_id,
        evidence_ref=evidence_ref,
        content_sha256=content_sha256,
        freshness_policy_id=freshness,
        source_provenance_refs=provenance,
        valid_from_utc=EVALUATION_TIME,
        valid_to_utc=VALID_TO_TIME,
    )
    record = action_commit_packet.build_dependency_set_candidate_record_v01(
        dependency_id=dependency_id,
        dependency_class=(
            "AIRLINE_HOLD_EVIDENCE"
            if domain_id == DOMAIN_ORDER[0]
            else "SUPPLIER_AVAILABILITY"
        ),
        evidence_ref=evidence_ref,
        content_sha256=content_sha256,
        requirement_class="MANDATORY",
        time_envelope_id=envelope_id,
        freshness_policy_id=freshness,
        source_provenance_refs=provenance,
        expected_accepting_local_root_id=root_id,
    )
    dependency = action_commit_packet.build_dependency_set_candidate_v01(
        dependency_records=(record,)
    )
    policy = action_commit_packet.build_action_authority_policy_profile_v01(
        policy_version=f"policy:g2e5:{slug}:g2a:v01",
        owning_local_root_id=root_id,
        authority_rule_refs=(f"authority_rule:g2e5:{slug}",),
        kill_switch_condition_refs=(f"kill_switch:g2e5:{slug}",),
        retry_policy="NON_CONSUMING_RETRY",
        supersession_policy="ROOT_DECISION_ONLY",
        logical_effect_namespace="supplier.payment.v01",
        allowed_logical_effect_classes=("PAYMENT",),
        allowed_business_object_namespaces=("supplier.payment_slot.v01",),
        allowed_corridor_classes=("supplier_a_mock_payment_corridor",),
    )
    source_packet_basis = (
        action_commit_packet.build_supplier_a_mock_action_commit_packet_fixture_v02()
    )
    source_packet = replace(
        source_packet_basis,
        scope=replace(
            source_packet_basis.scope,
            creditor_ref="creditor:supplier_a_adriatic_filters",
        ),
        ttl=action_commit_packet.PacketTTL(
            created_at="2026-08-01T00:00:00Z",
            expires_at="2026-08-01T01:00:00Z",
            ttl_seconds=3600,
        ),
    )
    canonical = action_commit_packet.build_supplier_action_commit_packet_canonical_projection_v01(
        source_packet,
        transaction_id=transaction_id,
        owning_local_root_id=root_id,
        canonical_permission_ref=f"permission:g2e5:{slug}:source",
        selected_legacy_action=action_commit_packet.ACTION_MOCK_SUPPLIER_A_PAYMENT_ORDER,
        logical_effect_namespace="supplier.payment.v01",
        business_object_namespace="supplier.payment_slot.v01",
        corridor_class="supplier_a_mock_payment_corridor",
        adapter_version=action_commit_packet.PRE_G2A_ADAPTER_VERSION_V01,
        temporal_policy_version="packet_ttl_v01",
        authority_policy=policy,
        dependency_candidate=dependency,
        evaluation_time=EVALUATION_TIME,
        evaluation_time_source="g2e5_deterministic_time",
        evaluation_context_id=f"evaluation_context:g2e5:{slug}:g2a",
        predecessor_packet_id=None,
        supersession_reason_class=None,
    )
    candidate_id = canonical.authorization_candidate.root_packet_authorization_candidate_id
    root_kernel, root_input, root_result = _build_root_acceptance(
        label=f"{slug}:g2a",
        transaction_id=transaction_id,
        root_id=root_id,
        candidate_id=candidate_id,
        subject=f"action_commit_packet:g2e5:{slug}",
        evidence_ref=evidence_ref,
        policy_id=canonical.authority_policy_fingerprint,
        time_envelope_ref=canonical.temporal_authority_fingerprint,
        permission_required=True,
        permission_ref=canonical.canonical_permission_ref,
    )
    root_projection = action_commit_packet.build_root_decision_candidate_projection_v01(
        candidate_kind=action_commit_packet.ROOT_DECISION_CANDIDATE_KIND_PACKET_AUTHORIZATION_V01,
        projected_candidate_id=candidate_id,
        root_decision_kernel=root_kernel,
        root_decision_input=root_input,
        root_decision_result=root_result,
    )
    packet = action_commit_packet.build_supplier_root_bound_action_commit_packet_v02_projection_v01(
        canonical_projection=canonical,
        root_decision_projection=root_projection,
    )
    transition_profile = (
        transition_registry.build_action_packet_transition_registry_profile_v01()
    )
    registry = action_commit_packet.record_action_packet_genesis_v01(
        action_commit_packet.build_empty_action_commit_packet_registry_v02(),
        root_bound_genesis=packet,
        action_packet_transition_registry_profile=transition_profile,
    )
    observations = tuple(
        action_commit_packet.build_action_dependency_current_observation_v01(
            dependency_id=item.dependency_id,
            evidence_ref=item.evidence_ref,
            observed_content_sha256=item.content_sha256,
            time_envelope_id=item.time_envelope_id,
            freshness_policy_id=item.freshness_policy_id,
            source_provenance_refs=item.source_provenance_refs,
            valid_from_utc=EVALUATION_TIME,
            valid_to_utc=VALID_TO_TIME,
            observed_at_utc=EVALUATION_TIME,
            observation_context_id=f"evaluation_context:g2e5:{slug}:g2a",
        )
        for item in dependency.dependency_records
    )
    invalidation = action_commit_packet.build_action_invalidation_evidence_v01(
        source_invalidation_event_ref=f"event:g2e5:{slug}:dependency-change",
        packet_id=packet.packet_identity.packet_id,
        dependency_id=record.dependency_id,
        invalidation_class="DEPENDENCY_CHANGED",
        evidence_ref=record.evidence_ref,
        evidence_sha256=_sha(f"g2e5-{slug}-dependency-observed"),
        observed_status="CHANGED",
        time_envelope_id=record.time_envelope_id,
        freshness_policy_id=record.freshness_policy_id,
        owning_local_root_id=root_id,
        accepted_by_local_root_id=root_id,
        authority_effect="DETERMINISTIC_BLOCK",
        evaluation_time=EVALUATION_TIME,
        evaluation_time_source="g2e5_deterministic_time",
        evaluation_context_id=f"evaluation_context:g2e5:{slug}:g2a",
    )
    invalidation_validation_result = (
        action_commit_packet.validate_action_invalidation_evidence_against_packet_v01(
            invalidation, packet
        )
    )
    valid, reasons = invalidation_validation_result
    if not valid or reasons:
        raise ValueError("g2e5_g2a_source_invalid")
    return {
        "registry": registry,
        "packet": packet,
        "dependency": dependency,
        "observations": observations,
        "invalidation": invalidation,
        "transition_profile": transition_profile,
        "root_result": root_result,
        "invalidation_validation_result": invalidation_validation_result,
    }


def _g2a_transition_bindings(
    profile: object,
    rule_id: str,
    *,
    label: str,
) -> tuple[action_commit_packet.TransitionEvidenceBindingV01, ...]:
    rule = transition_registry.lookup_action_packet_transition_rule_v01(
        registry=profile,
        transition_rule_id=rule_id,
    )
    return tuple(
        action_commit_packet.build_transition_evidence_binding_v01(
            action_packet_transition_registry_profile=profile,
            transition_rule_id=rule_id,
            evidence_code=code,
            evidence_ref="evidence:g2e5:" + label + ":" + code,
            evidence_sha256=_sha("g2e5-" + label + "-" + code),
            validator_profile_id="validator:g2e5_g2a_transition",
        )
        for code in rule.required_evidence_codes
    )


def _g2a_transition_event(
    entry: action_commit_packet.ActionPacketLifecycleEntryV01,
    profile: object,
    rule_id: str,
    *,
    label: str,
) -> action_commit_packet.ActionPacketTransitionEventV01:
    canonical = entry.root_bound_genesis.canonical_projection
    packet_id = entry.root_bound_genesis.packet_identity.packet_id
    evaluation_context_id = "evaluation_context:g2e5:" + label + ":" + rule_id
    attempt = None
    if rule_id == "g2a_t03_pending":
        attempt = action_commit_packet.build_action_execution_attempt_identity_v01(
            packet_id=packet_id,
            idempotency_key=canonical.idempotency_identity.idempotency_key,
            attempt_ordinal=1,
            evaluation_context_id=evaluation_context_id,
        )
    return action_commit_packet.build_action_packet_transition_event_v01(
        action_packet_transition_registry_profile=profile,
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
        transition_evidence_bindings=_g2a_transition_bindings(
            profile, rule_id, label=label
        ),
        dependency_set_candidate_fingerprint=(
            canonical.dependency_set_candidate_fingerprint
        ),
        temporal_authority_fingerprint=canonical.temporal_authority_fingerprint,
        evaluation_time=EVALUATION_TIME + len(entry.transition_events),
        evaluation_time_source="g2e5_deterministic_time",
        evaluation_context_id=evaluation_context_id,
        execution_attempt_identity=attempt,
        receipt_ref=None,
    )


def _g2a_pending_negative_setup(
    g2a_family: dict[str, object],
    *,
    label: str,
) -> dict[str, object]:
    registry = g2a_family["registry"]
    packet = g2a_family["packet"]
    profile = g2a_family["transition_profile"]
    if (
        type(registry) is not action_commit_packet.ActionCommitPacketRegistryV02
        or type(packet)
        is not action_commit_packet.SupplierRootBoundActionCommitPacketV02ProjectionV01
    ):
        raise ValueError("g2e5_g2a_negative_setup_invalid")
    packet_id = packet.packet_identity.packet_id
    entry = registry.action_packet_lifecycle_entries[0]
    activation = _g2a_transition_event(
        entry,
        profile,
        "g2a_t01_activate_root_authorization",
        label=label,
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
    canonical = packet.canonical_projection
    reserve = action_commit_packet.build_idempotency_disposition_event_v01(
        idempotency_key=canonical.idempotency_identity.idempotency_key,
        event_class="RESERVE",
        from_disposition="UNCLAIMED",
        to_disposition="RESERVED",
        from_owner_packet_id=None,
        to_owner_packet_id=packet_id,
        previous_disposition_event_id=None,
        cause_transition_event_ids=(activation.transition_event_id,),
        root_decision_ref=(
            packet.root_decision_projection.root_decision_result.decision_id
        ),
        predecessor_packet_id=None,
        successor_packet_id=None,
        evidence_refs=evidence_ids,
        evaluation_time=activation.evaluation_time,
        evaluation_time_source=activation.evaluation_time_source,
        evaluation_context_id=activation.evaluation_context_id,
    )
    pending_registry = action_commit_packet.activate_action_packet_lifecycle_v01(
        registry,
        packet_id=packet_id,
        transition_event=activation,
        disposition_event=reserve,
        action_packet_transition_registry_profile=profile,
    )
    for rule_id in ("g2a_t02_queue", "g2a_t03_pending"):
        entry = pending_registry.action_packet_lifecycle_entries[0]
        event = _g2a_transition_event(
            entry,
            profile,
            rule_id,
            label=label,
        )
        pending_registry = (
            action_commit_packet.append_action_packet_lifecycle_transition_v01(
                pending_registry,
                packet_id=packet_id,
                transition_event=event,
                action_packet_transition_registry_profile=profile,
            )
        )
    registry_validation_result = (
        action_commit_packet.validate_action_commit_packet_registry_v02(
            pending_registry
        )
    )
    registry_valid, registry_reasons = registry_validation_result
    if not registry_valid or registry_reasons:
        raise ValueError("g2e5_g2a_pending_registry_invalid")
    source_packet = canonical.source_packet
    step = action_commit_packet.build_supplier_a_corridor_step_fixture_v01(
        source_packet
    )
    step = replace(
        step,
        parent_packet_id=packet_id,
        allowed_subjects=source_packet.scope.allowed_subjects,
    )
    corridor = action_commit_packet.ContractFulfillmentCorridorV01(
        corridor_id="corridor:g2e5:" + label,
        packet_id=packet_id,
        corridor_kind=canonical.adapter_binding.corridor_class,
        allowed_steps=(step.step_id,),
    )
    evaluation_context_id = "evaluation_context:g2e5:" + label + ":present"
    observations = tuple(
        action_commit_packet.build_action_dependency_current_observation_v01(
            dependency_id=record.dependency_id,
            evidence_ref=record.evidence_ref,
            observed_content_sha256=record.content_sha256,
            time_envelope_id=record.time_envelope_id,
            freshness_policy_id=record.freshness_policy_id,
            source_provenance_refs=record.source_provenance_refs,
            valid_from_utc=EVALUATION_TIME,
            valid_to_utc=VALID_TO_TIME,
            observed_at_utc=EVALUATION_TIME,
            observation_context_id=evaluation_context_id,
        )
        for record in canonical.dependency_candidate.dependency_records
    )
    bridge = action_commit_packet.build_logical_time_bridge_v01(
        origin_utc_epoch_seconds=EVALUATION_TIME,
        seconds_per_tick=1,
        bridge_policy_version="g2e5_epoch_seconds_v01",
    )
    inspection = action_commit_packet.inspect_action_packet_present_eligibility_v01(
        pending_registry,
        packet_id=packet_id,
        corridor=corridor,
        corridor_step=step,
        current_dependency_observations=observations,
        logical_time_bridge=bridge,
        evaluation_time=EVALUATION_TIME + 4,
        evaluation_time_source="g2e5_deterministic_time",
        evaluation_context_id=evaluation_context_id,
        action_packet_transition_registry_profile=profile,
    )
    inspection_validation_result = (
        action_commit_packet.validate_action_packet_present_eligibility_inspection_v01(
            inspection,
            pending_registry,
            packet_id=packet_id,
            corridor=corridor,
            corridor_step=step,
            current_dependency_observations=observations,
            logical_time_bridge=bridge,
            evaluation_time=EVALUATION_TIME + 4,
            evaluation_time_source="g2e5_deterministic_time",
            evaluation_context_id=evaluation_context_id,
            action_packet_transition_registry_profile=profile,
        )
    )
    inspection_valid, inspection_reasons = inspection_validation_result
    if (
        not inspection_valid
        or inspection_reasons
        or inspection.present_eligibility_status
        != "ELIGIBLE_FOR_BOUNDED_MOCK_ATTEMPT"
        or inspection.present_executable is not True
    ):
        raise ValueError(
            "g2e5_g2a_present_eligibility_invalid:"
            + inspection.present_eligibility_status
            + ":"
            + ",".join(inspection.reason_codes)
        )
    return {
        "registry": pending_registry,
        "packet": packet,
        "inspection": inspection,
        "profile": profile,
        "registry_validation_result": registry_validation_result,
        "inspection_validation_result": inspection_validation_result,
    }


def _g2a_revocation_candidate(
    g2a_family: dict[str, object],
) -> dict[str, object]:
    packet = g2a_family["packet"]
    if type(packet) is not action_commit_packet.SupplierRootBoundActionCommitPacketV02ProjectionV01:
        raise ValueError("g2e5_g2a_revocation_packet_invalid")
    canonical = packet.canonical_projection
    candidate = action_commit_packet.build_revocation_candidate_v01(
        owning_local_root_id=canonical.owning_local_root_id,
        packet_id=packet.packet_identity.packet_id,
        source_authorization_decision_id=(
            packet.root_decision_projection.root_decision_result.decision_id
        ),
        idempotency_key=canonical.idempotency_identity.idempotency_key,
        revocation_reason_class="DEPENDENCY_CHANGED",
        evidence_refs=("evidence:g2e5:revocation-candidate",),
        evidence_hashes=(_sha("g2e5-revocation-candidate"),),
        evaluation_time=EVALUATION_TIME + 4,
        policy_fingerprint=canonical.authority_policy_fingerprint,
    )
    candidate_validation_result = (
        action_commit_packet.validate_revocation_candidate_v01(candidate)
    )
    valid, reasons = candidate_validation_result
    contextual_validation_result = (
        action_commit_packet.validate_revocation_candidate_against_packet_v01(
            candidate, packet
        )
    )
    contextual_valid, contextual_reasons = contextual_validation_result
    if not valid or reasons or not contextual_valid or contextual_reasons:
        raise ValueError("g2e5_g2a_revocation_candidate_invalid")
    return {
        "candidate": candidate,
        "validation_result": candidate_validation_result,
        "packet_validation_result": contextual_validation_result,
    }


def _build_g2d_source_context(
    domain_id: str,
    g2b: dict[str, object],
) -> dict[str, object]:
    slug = _domain_slug(domain_id)
    request_id = f"request:g2e5:{slug}:full-fractal:v01"
    transaction_id = str(g2b["transaction_id"])
    root_id = (
        "root:mock_airline_al"
        if domain_id == DOMAIN_ORDER[0]
        else "root:g2a5:supplier"
    )
    scope_ref = f"scope:g2e5:{slug}:full-fractal:v01"
    selected_mode = "full_fractal"
    selected_index = g2c.EXECUTABLE_EXECUTION_MODES_V01.index(selected_mode)
    profiles = tuple(
        g2c.build_execution_mode_local_mode_profile_v01(
            request_id=request_id,
            transaction_id=transaction_id,
            owning_root_id=root_id,
            domain_id=domain_id,
            mode=candidate,
            policy_snapshot_id=f"policy:g2e5:{slug}:v01",
            capability_snapshot_id=f"capabilities:g2e5:{slug}:v01",
            cost_model_id="cost:g2e5:v01",
            policy_allowed=index >= selected_index,
            scope_allowed=True,
            risk_allowed=True,
            privacy_allowed=True,
            capability_state=(
                "NOT_REQUIRED"
                if candidate in {"sealed_replay", "direct_informational_reuse"}
                else "AVAILABLE"
            ),
            capability_id=(
                None
                if candidate in {"sealed_replay", "direct_informational_reuse"}
                else f"capability:g2e5:{slug}:{candidate}:v01"
            ),
            cost_units=index + 1,
        )
        for index, candidate in enumerate(g2c.EXECUTABLE_EXECUTION_MODES_V01)
    )
    snapshot = g2c.build_execution_mode_local_routing_snapshot_v01(
        request_id=request_id,
        transaction_id=transaction_id,
        owning_root_id=root_id,
        domain_id=domain_id,
        request_class="BOUNDED_FRACTAL_REQUIRED",
        action_class="NON_ACTION",
        action_packet_relation="NOT_APPLICABLE",
        scope_class="BOUNDED",
        scope_ref=scope_ref,
        permitted_narrower_scope_refs=(),
        risk_class="LOW",
        policy_snapshot_id=f"policy:g2e5:{slug}:v01",
        capability_snapshot_id=f"capabilities:g2e5:{slug}:v01",
        cost_model_id="cost:g2e5:v01",
        required_user_input_state="COMPLETE",
        hard_block_state="CLEAR",
        evaluation_time_epoch_seconds=EVALUATION_TIME,
        pt_created_at_utc=EVALUATION_UTC,
        et_observed_at_utc=EVALUATION_UTC,
        ct_session_anchor=f"ct:g2e5:{slug}:v01",
        ttl_seconds=3600,
        freshness_class="static",
        valid_from_utc=EVALUATION_UTC,
        valid_to_utc=VALID_TO_UTC,
        mode_profiles=profiles,
    )
    bsep = _build_bsep_family(domain_id, request_id)
    source = g2c.build_execution_mode_source_context_v01(
        business_request_context_packet=bsep["business"],
        bsep_packet=bsep["packet"],
        bsep_route_context_packet=bsep["route"],
        bsep_orchestrator_proposal=bsep["proposal"],
        bsep_structured_rationale=bsep["rationale"],
        sealed_replay_evidence=None,
        replay_source_manifest=None,
        replay_source_domain_projection=None,
        replay_source_safe_file_contents=(),
        replay_anchor_publication=None,
        replay_anchored_verification=None,
        replay_supplied_anchor_publication_id=None,
        replay_reconstructed_manifest=None,
        replay_reconstructed_domain_projection=None,
        replay_reconstructed_safe_file_contents=(),
        g2a_inspection=None,
        g2a_registry=None,
        g2a_packet_id=None,
        g2a_corridor=None,
        g2a_corridor_step=None,
        g2a_current_dependency_observations=(),
        g2a_logical_time_bridge=None,
        g2a_evaluation_time=EVALUATION_TIME,
        g2a_evaluation_time_source=snapshot.created_by,
        g2a_evaluation_context_id=snapshot.local_routing_snapshot_id,
        g2a_transition_registry_profile=None,
        g2b_resolution_report=g2b["report"],
        g2b_compatibility_projections=g2b["projections"],
        g2b_use_time=EVALUATION_TIME,
        g2b_root_kernel=g2b["root_kernel"],
        g2b_root_decision_input=g2b["root_input"],
        g2b_root_decision_result=g2b["root_result"],
        g2b_writeback_evidence=None,
    )
    common = {
        "request_id": request_id,
        "transaction_id": transaction_id,
        "owning_root_id": root_id,
        "domain_id": domain_id,
    }
    router_input = g2c.build_execution_mode_router_input_v01(
        request_id=request_id,
        transaction_id=transaction_id,
        owning_root_id=root_id,
        bsep_binding=g2c.build_execution_mode_bsep_binding_v01(
            **common, source_context=source
        ),
        local_routing_snapshot=snapshot,
        replay_binding=g2c.build_execution_mode_replay_not_applicable_binding_v01(
            **common
        ),
        g2a_binding=g2c.build_execution_mode_g2a_no_packet_binding_v01(
            **common,
            evaluation_time=EVALUATION_TIME,
            evaluation_time_source=snapshot.created_by,
            evaluation_context_id=snapshot.local_routing_snapshot_id,
        ),
        g2b_binding=g2c.build_execution_mode_g2b_binding_v01(
            **common,
            source_context=source,
        ),
    )
    route_result = g2c.route_execution_mode_v01(
        router_input=router_input, source_context=source
    )
    proposal, route_report = route_result
    if route_report.validation_status != "PASS" or proposal is None:
        raise ValueError("g2e5_g2c_route_invalid")
    proposal_artifact = g2c.project_execution_mode_proposal_kernel_artifact_v01(
        proposal=proposal,
        router_input=router_input,
        source_context=source,
    )
    registry = transition_registry.build_execution_mode_transition_registry_profile_v01()
    proposal_transition = g2c.evaluate_execution_mode_proposal_to_root_transition_v01(
        registry=registry,
        proposal=proposal,
        router_input=router_input,
        source_context=source,
        proposal_artifact=proposal_artifact,
    )
    review = g2c.build_root_execution_mode_review_input_v01(
        proposal=proposal,
        router_input=router_input,
        source_context=source,
        proposal_artifact=proposal_artifact,
        proposal_transition_decision=proposal_transition,
        review_action="ACCEPT",
        accepted_scope_ref=proposal.proposed_scope_ref,
        narrowing_basis_refs=(),
    )
    review_result = (
        g2c.review_execution_mode_proposal_v01(
            review_input=review,
            proposal=proposal,
            router_input=router_input,
            source_context=source,
            proposal_artifact=proposal_artifact,
            proposal_transition_decision=proposal_transition,
        )
    )
    decision, root_kernel, root_input, root_result, review_report = review_result
    if (
        review_report.validation_status != "PASS"
        or decision is None
        or root_kernel is None
        or root_input is None
        or root_result is None
    ):
        raise ValueError("g2e5_g2c_root_review_invalid")
    decision_artifact = g2c.project_root_execution_mode_decision_kernel_artifact_v01(
        decision=decision,
        review_input=review,
        proposal=proposal,
        router_input=router_input,
        source_context=source,
        proposal_artifact=proposal_artifact,
        proposal_transition_decision=proposal_transition,
        root_kernel=root_kernel,
        root_decision_input=root_input,
        root_decision_result=root_result,
    )
    root_route_transition = g2c.evaluate_execution_mode_root_route_transition_v01(
        registry=registry,
        proposal_transition_decision=proposal_transition,
        review_input=review,
        decision=decision,
        proposal=proposal,
        router_input=router_input,
        source_context=source,
        root_kernel=root_kernel,
        root_decision_input=root_input,
        root_decision_result=root_result,
        proposal_artifact=proposal_artifact,
        decision_artifact=decision_artifact,
    )
    route_artifact = g2c.project_execution_mode_route_eligibility_kernel_artifact_v01(
        decision=decision,
        review_input=review,
        proposal=proposal,
        router_input=router_input,
        source_context=source,
        proposal_artifact=proposal_artifact,
        proposal_transition_decision=proposal_transition,
        root_kernel=root_kernel,
        root_decision_input=root_input,
        root_decision_result=root_result,
        decision_artifact=decision_artifact,
        root_route_transition_decision=root_route_transition,
    )
    if route_artifact is None:
        raise ValueError("g2e5_route_artifact_missing")
    policy = g2d.build_fractal_runtime_policy_v02(
        required_downstream_capability_ids=proposal.required_downstream_capability_ids,
        permitted_child_scope_refs=snapshot.permitted_narrower_scope_refs,
    )
    runtime_source = g2d.build_fractal_runtime_source_context_v02(
        transition_registry=registry,
        g2c_source_context=source,
        router_input=router_input,
        proposal=proposal,
        proposal_artifact=proposal_artifact,
        proposal_transition_decision=proposal_transition,
        review_input=review,
        decision=decision,
        root_kernel=root_kernel,
        root_decision_input=root_input,
        root_decision_result=root_result,
        decision_artifact=decision_artifact,
        root_route_transition_decision=root_route_transition,
        route_eligibility_artifact=route_artifact,
        runtime_policy=policy,
    )
    if g2d.validate_fractal_runtime_source_context_v02(runtime_source).status != "PASS":
        raise ValueError("g2e5_g2d_source_invalid")
    return {
        "source": runtime_source,
        "g2c_source": source,
        "route": route_artifact,
        "root_kernel": root_kernel,
        "transaction_id": transaction_id,
        "root_id": root_id,
        "domain_id": domain_id,
        "route_public_return": route_result,
        "review_public_return": review_result,
    }


def _plain_data(value: object) -> object:
    if is_dataclass(value):
        return {key: _plain_data(item) for key, item in asdict(value).items()}
    if type(value) is tuple:
        return [_plain_data(item) for item in value]
    if type(value) is list:
        return [_plain_data(item) for item in value]
    if isinstance(value, Mapping):
        return {str(key): _plain_data(item) for key, item in value.items()}
    return value


def _sha256_plain(value: object) -> str:
    return hashlib.sha256(_canonical_json_text(_plain_data(value)).encode("ascii")).hexdigest()


def _require_public_pass(report: object, failure: str) -> None:
    if getattr(report, "status", None) != "PASS":
        raise ValueError(failure)


def _kernel_artifact(
    *,
    artifact_id: str,
    transaction_id: str,
    root_id: str,
    payload: dict[str, object],
    parent_refs: tuple[str, ...] = (),
) -> g2e.KernelArtifactV01:
    return build_kernel_artifact_v01(
        abi_version="v1.0",
        artifact_id=artifact_id,
        artifact_type="SemanticEvidence",
        schema_version="v1",
        transaction_id=transaction_id,
        owner_root_id=root_id,
        source_component="continuous_delta_runtime_g2e5",
        authority_class="EVIDENCE_ONLY",
        lifecycle_state="VALIDATED",
        payload=payload,
        trace_refs=("trace:" + artifact_id,),
        parent_refs=parent_refs,
        time_envelope={
            "ct_session_anchor": "ct:g2e5:source",
            "et_observed_at": EVALUATION_UTC,
            "freshness_class": "static",
            "kt_asof": EVALUATION_UTC,
            "pt_created_at": EVALUATION_UTC,
            "ttl_seconds": 3600,
            "valid_from": EVALUATION_UTC,
            "valid_to": VALID_TO_UTC,
        },
    )


def _artifact_sha256(artifact: g2e.KernelArtifactV01) -> str:
    return hashlib.sha256(
        canonical_json_bytes_v01(kernel_artifact_to_plain_dict_v01(artifact))
    ).hexdigest()


def _payload_sha256(artifact: g2e.KernelArtifactV01) -> str:
    return hashlib.sha256(
        canonical_json_bytes_v01(
            kernel_artifact_to_plain_dict_v01(artifact)["payload"]
        )
    ).hexdigest()


def _runtime_projection(
    artifact: g2e.KernelArtifactV01,
    *,
    root_id: str,
) -> g2e.KernelArtifactV01:
    projected = kernel_artifact_to_plain_dict_v01(artifact)
    digest = hashlib.sha256(canonical_json_bytes_v01(projected)).hexdigest()
    return _kernel_artifact(
        artifact_id="artifact:g2e5:runtime-projection:" + digest,
        transaction_id=artifact.transaction_id,
        root_id=root_id,
        payload={
            "projection_profile_id": (
                "g2e_baseline_runtime_artifact_projection_v01"
            ),
            "projected_runtime_artifact": projected,
            "projected_runtime_artifact_sha256": digest,
        },
        parent_refs=(artifact.artifact_id,),
    )


def _baseline_runtime_projections(
    baseline: g2d.FractalRuntimeExecutionBundleV02,
    *,
    root_id: str,
) -> tuple[
    g2e.KernelArtifactV01,
    g2e.KernelArtifactV01,
    g2e.KernelArtifactV01,
    g2e.KernelArtifactV01,
]:
    children = tuple(
        item for item in baseline.cell_inputs if item.parent_cell_id is not None
    )
    if len(children) != 2:
        raise ValueError("g2e5_baseline_child_geometry_invalid")
    by_entry = {
        entry.queue_entry_id: artifact
        for entry, artifact in zip(
            baseline.queue_entries, baseline.queue_artifacts, strict=True
        )
    }
    selected = by_entry[children[-1].ordered_initial_queue_entry_ids[0]]
    sibling = by_entry[children[0].ordered_initial_queue_entry_ids[0]]
    return (
        _runtime_projection(selected, root_id=root_id),
        _runtime_projection(sibling, root_id=root_id),
        selected,
        sibling,
    )


def _warehouse_record(stock: int) -> dict[str, object]:
    content = {"worldstate": {"current_stock": {"water_filter": stock}}}
    content_sha256 = hashlib.sha256(canonical_json_bytes_v01(content)).hexdigest()
    dependency_id = "dependency:g2a5:supplier:primary"
    evidence_ref = "evidence:g2e5:warehouse:water-filter-stock:v01"
    freshness = "freshness:g2e5:warehouse:one-hour:v01"
    provenance = (
        "demo:run_applied_warehouse_semantic_demo.py:/worldstate/current_stock/water_filter",
    )
    envelope_id = action_commit_packet.build_action_dependency_time_envelope_id_v01(
        dependency_id=dependency_id,
        evidence_ref=evidence_ref,
        content_sha256=content_sha256,
        freshness_policy_id=freshness,
        source_provenance_refs=provenance,
        valid_from_utc=EVALUATION_TIME,
        valid_to_utc=VALID_TO_TIME,
    )
    record = action_commit_packet.build_dependency_set_candidate_record_v01(
        dependency_id=dependency_id,
        dependency_class="SUPPLIER_AVAILABILITY",
        evidence_ref=evidence_ref,
        content_sha256=content_sha256,
        requirement_class="MANDATORY",
        time_envelope_id=envelope_id,
        freshness_policy_id=freshness,
        source_provenance_refs=provenance,
        expected_accepting_local_root_id="root:g2a5:supplier",
    )
    record_validation_result = (
        action_commit_packet.validate_dependency_set_candidate_record_v01(record)
    )
    valid, reasons = record_validation_result
    candidate = action_commit_packet.build_dependency_set_candidate_v01(
        dependency_records=(record,)
    )
    candidate_validation_result = (
        action_commit_packet.validate_dependency_set_candidate_v01(candidate)
    )
    candidate_valid, candidate_reasons = candidate_validation_result
    if not valid or reasons or not candidate_valid or candidate_reasons:
        raise ValueError("g2e5_warehouse_source_invalid")
    return {
        "record": record,
        "candidate": candidate,
        "record_validation_result": record_validation_result,
        "candidate_validation_result": candidate_validation_result,
    }


def _typed_source_pair(
    *,
    case_id: str,
    baseline: g2d.FractalRuntimeExecutionBundleV02,
    g2a: dict[str, object],
    g2b: dict[str, object],
) -> dict[str, object]:
    semantic_id = _semantic_case_id(case_id)
    if semantic_id == "g2e_case:negative:repeated_delta_spin:v01":
        record = g2a["dependency"].dependency_records[0]
        invalidation = g2a["invalidation"]
        record_validation_result = (
            action_commit_packet.validate_dependency_set_candidate_record_v01(
                record
            )
        )
        invalidation_validation_result = (
            action_commit_packet.validate_action_invalidation_evidence_against_packet_v01(
                invalidation, g2a["packet"]
            )
        )
        baseline_payload = {
            "dependency_id": record.dependency_id,
            "dependency_class": record.dependency_class,
            "evidence_ref": record.evidence_ref,
            "content_sha256": record.content_sha256,
            "requirement_class": record.requirement_class,
            "time_envelope_id": record.time_envelope_id,
            "freshness_policy_id": record.freshness_policy_id,
            "source_provenance_refs": list(record.source_provenance_refs),
            "expected_accepting_local_root_id": (
                record.expected_accepting_local_root_id
            ),
        }
        observed_payload = {
            "dependency_id": record.dependency_id,
            "evidence_ref": record.evidence_ref,
            "content_sha256": invalidation.evidence_sha256,
            "observed_status": invalidation.observed_status,
            "invalidation_evidence_id": invalidation.invalidation_evidence_id,
            "packet_id": invalidation.packet_id,
        }
        return {
            "baseline_typed": record,
            "observed_typed": invalidation,
            "baseline_payload": baseline_payload,
            "observed_payload": observed_payload,
            "pointer": "/content_sha256",
            "prior_value": record.content_sha256,
            "observed_value": invalidation.evidence_sha256,
            "typed_validation": (
                record_validation_result,
                invalidation_validation_result,
            ),
            "typed_public_tuple_returns": (
                record_validation_result,
                invalidation_validation_result,
            ),
            "context_only": False,
            "policy_change": False,
            "raw_payload": True,
        }
    if semantic_id.endswith("travel:hold_expiry:v01"):
        offer = travel_corridor.build_valid_airline_offer_packet_v01()
        prior = travel_corridor.build_valid_airline_hold_commit_packet_v01()
        observed = replace(
            prior,
            packet_id=prior.packet_id + ":observed",
            expired=True,
        )
        prior_report = travel_corridor.validate_airline_hold_commit_packet_v01(
            offer, prior
        )
        observed_report = travel_corridor.validate_airline_hold_commit_packet_v01(
            offer, observed
        )
        return {
            "baseline_typed": prior,
            "observed_typed": observed,
            "baseline_payload": _plain_data(prior),
            "observed_payload": _plain_data(observed),
            "pointer": "/expired",
            "prior_value": False,
            "observed_value": True,
            "typed_validation": (prior_report, observed_report),
            "typed_public_tuple_returns": tuple(
                item for item in (prior_report, observed_report) if type(item) is tuple
            ),
            "context_only": False,
            "policy_change": False,
        }
    if semantic_id.endswith("travel:price_change:v01"):
        prior = travel_corridor.build_valid_airline_offer_packet_v01()
        observed = replace(
            prior,
            packet_id=prior.packet_id + ":observed",
            amount=783,
        )
        prior_report = travel_corridor.validate_airline_offer_packet_v01(prior)
        observed_report = travel_corridor.validate_airline_offer_packet_v01(
            observed
        )
        return {
            "baseline_typed": prior,
            "observed_typed": observed,
            "baseline_payload": _plain_data(prior),
            "observed_payload": _plain_data(observed),
            "pointer": "/amount",
            "prior_value": prior.amount,
            "observed_value": observed.amount,
            "typed_validation": (prior_report, observed_report),
            "typed_public_tuple_returns": tuple(
                item for item in (prior_report, observed_report) if type(item) is tuple
            ),
            "context_only": False,
            "policy_change": False,
        }
    if semantic_id.endswith("travel:unrelated_preference:v01"):
        prior = travel_binding.build_client_constraints_preference_a_v01()
        observed = replace(
            prior,
            soft_preference_priority=tuple(reversed(prior.soft_preference_priority)),
        )
        prior_report = (
            travel_binding.validate_client_root_travel_constraint_set_v01(prior)
        )
        observed_report = (
            travel_binding.validate_client_root_travel_constraint_set_v01(
                observed
            )
        )
        return {
            "baseline_typed": prior,
            "observed_typed": observed,
            "baseline_payload": _plain_data(prior),
            "observed_payload": _plain_data(observed),
            "pointer": "/soft_preference_priority",
            "prior_value": list(prior.soft_preference_priority),
            "observed_value": list(observed.soft_preference_priority),
            "typed_validation": (prior_report, observed_report),
            "typed_public_tuple_returns": tuple(
                item for item in (prior_report, observed_report) if type(item) is tuple
            ),
            "context_only": True,
            "policy_change": False,
        }
    if semantic_id.endswith("policy_change:v01"):
        prior = baseline.source_context.router_input.local_routing_snapshot
        observed = replace(
            prior,
            policy_snapshot_id=prior.policy_snapshot_id + ":successor",
        )
        observed = replace(
            observed,
            local_routing_snapshot_id=(
                g2c.rebuild_execution_mode_local_routing_snapshot_identity_v01(
                    observed
                )
            ),
        )
        prior_report = g2c.validate_execution_mode_local_routing_snapshot_v01(
            prior
        )
        observed_report = g2c.validate_execution_mode_local_routing_snapshot_v01(
            observed
        )
        return {
            "baseline_typed": prior,
            "observed_typed": observed,
            "baseline_payload": _plain_data(prior),
            "observed_payload": _plain_data(observed),
            "pointer": "/policy_snapshot_id",
            "prior_value": prior.policy_snapshot_id,
            "observed_value": observed.policy_snapshot_id,
            "typed_validation": (prior_report, observed_report),
            "typed_public_tuple_returns": tuple(
                item for item in (prior_report, observed_report) if type(item) is tuple
            ),
            "context_only": False,
            "policy_change": True,
        }
    if semantic_id.endswith("warehouse:evidence_validity:v01"):
        prior = g2a["observations"][0]
        observed_valid_to = prior.valid_to_utc - 60
        observed_time_envelope_id = (
            action_commit_packet.build_action_dependency_time_envelope_id_v01(
                dependency_id=prior.dependency_id,
                evidence_ref=prior.evidence_ref,
                content_sha256=prior.observed_content_sha256,
                freshness_policy_id=prior.freshness_policy_id,
                source_provenance_refs=prior.source_provenance_refs,
                valid_from_utc=prior.valid_from_utc,
                valid_to_utc=observed_valid_to,
            )
        )
        observed = action_commit_packet.build_action_dependency_current_observation_v01(
            dependency_id=prior.dependency_id,
            evidence_ref=prior.evidence_ref,
            observed_content_sha256=prior.observed_content_sha256,
            time_envelope_id=observed_time_envelope_id,
            freshness_policy_id=prior.freshness_policy_id,
            source_provenance_refs=prior.source_provenance_refs,
            valid_from_utc=prior.valid_from_utc,
            valid_to_utc=observed_valid_to,
            observed_at_utc=prior.observed_at_utc,
            observation_context_id=prior.observation_context_id,
        )
        prior_validation_result = (
            action_commit_packet.validate_action_dependency_current_observation_v01(
                prior
            )
        )
        observed_validation_result = (
            action_commit_packet.validate_action_dependency_current_observation_v01(
                observed
            )
        )
        return {
            "baseline_typed": prior,
            "observed_typed": observed,
            "baseline_payload": _plain_data(prior),
            "observed_payload": _plain_data(observed),
            "pointer": "/valid_to_utc",
            "prior_value": prior.valid_to_utc,
            "observed_value": observed.valid_to_utc,
            "typed_validation": (
                prior_validation_result,
                observed_validation_result,
            ),
            "typed_public_tuple_returns": (
                prior_validation_result,
                observed_validation_result,
            ),
            "context_only": False,
            "policy_change": False,
        }
    prior_material = _warehouse_record(6)
    observed_material = _warehouse_record(8)
    prior = prior_material["record"]
    observed = observed_material["record"]
    return {
        "baseline_typed": prior,
        "observed_typed": observed,
        "baseline_payload": {
            "typed_record": _plain_data(prior),
            "worldstate": {"current_stock": {"water_filter": 6}},
        },
        "observed_payload": {
            "typed_record": _plain_data(observed),
            "worldstate": {"current_stock": {"water_filter": 8}},
        },
        "pointer": "/worldstate/current_stock/water_filter",
        "prior_value": 6,
        "observed_value": 8,
        "typed_validation": (
            prior_material["record_validation_result"],
            observed_material["record_validation_result"],
        ),
        "typed_public_tuple_returns": (
            prior_material["record_validation_result"],
            prior_material["candidate_validation_result"],
            observed_material["record_validation_result"],
            observed_material["candidate_validation_result"],
        ),
        "typed_private_material": (prior_material, observed_material),
        "context_only": False,
        "policy_change": False,
    }


def _typed_validation_plain(value: object) -> dict[str, object]:
    if type(value) is tuple:
        return {"valid": value[0], "reason_codes": list(value[1])}
    return {
        "status": getattr(value, "validation_status", getattr(value, "status", None)),
        "reason_codes": list(getattr(value, "reason_codes", ())),
        "authority_created": getattr(value, "authority_created", False),
        "permission_created": getattr(value, "permission_created", False),
        "real_world_effects_count": getattr(value, "real_world_effects_count", 0),
    }


def _build_case_inputs(
    *,
    case_id: str,
    domain_id: str,
    baseline: g2d.FractalRuntimeExecutionBundleV02,
    source_family: dict[str, object],
    g2a: dict[str, object],
    g2b: dict[str, object],
) -> dict[str, object]:
    semantic_id = _semantic_case_id(case_id)
    slug = _domain_slug(domain_id)
    transaction_id = baseline.runtime_report.transaction_id
    root_id = baseline.runtime_report.owning_root_id
    source = _typed_source_pair(
        case_id=semantic_id,
        baseline=baseline,
        g2a=g2a,
        g2b=g2b,
    )
    if source.get("raw_payload") is True:
        prior_payload = source["baseline_payload"]
        observed_payload = source["observed_payload"]
        dependency_pointer = source["pointer"]
    else:
        prior_payload = {
            "typed_source_type": type(source["baseline_typed"]).__name__,
            "typed_source": source["baseline_payload"],
        }
        observed_payload = {
            "typed_source_type": type(source["observed_typed"]).__name__,
            "typed_source": source["observed_payload"],
        }
        dependency_pointer = "/typed_source" + source["pointer"]
    if source["policy_change"]:
        runtime_source_binding = baseline.source_binding
        route_material = {
            "route_eligibility_artifact_id": (
                runtime_source_binding.route_eligibility_artifact_id
            ),
            "route_eligibility_artifact_sha256": (
                runtime_source_binding.route_eligibility_artifact_sha256
            ),
            "source_decision_artifact_id": (
                runtime_source_binding.source_decision_artifact_id
            ),
            "source_proposal_artifact_id": (
                runtime_source_binding.source_proposal_artifact_id
            ),
            "source_policy_snapshot_id": (
                runtime_source_binding.source_policy_snapshot_id
            ),
            "source_capability_snapshot_id": (
                runtime_source_binding.source_capability_snapshot_id
            ),
            "source_parent_refs": list(runtime_source_binding.source_parent_refs),
            "source_trace_refs": list(runtime_source_binding.source_trace_refs),
        }
        prior_payload.update(route_material)
        observed_payload.update(route_material)
        observed_payload["route_eligibility_artifact_sha256"] = _sha256_plain(
            {
                "baseline_route_eligibility_artifact_sha256": (
                    runtime_source_binding.route_eligibility_artifact_sha256
                ),
                "observed_local_routing_snapshot_id": (
                    source["observed_typed"].local_routing_snapshot_id
                ),
                "observed_policy_snapshot_id": (
                    source["observed_typed"].policy_snapshot_id
                ),
            }
        )
    artifact_pointer = "/payload" + dependency_pointer
    source_digest = _sha256_plain({"case_id": semantic_id, "role": "source"})
    baseline_source = _kernel_artifact(
        artifact_id=f"artifact:g2e5:{slug}:source:{source_digest}",
        transaction_id=transaction_id,
        root_id=root_id,
        payload=prior_payload,
    )
    observed_source = _kernel_artifact(
        artifact_id=f"artifact:g2e5:{slug}:observed:{source_digest}",
        transaction_id=transaction_id,
        root_id=root_id,
        payload=observed_payload,
        parent_refs=(baseline_source.artifact_id,),
    )
    semantic_dependent = _kernel_artifact(
        artifact_id=f"artifact:g2e5:{slug}:semantic-dependent:{source_digest}",
        transaction_id=transaction_id,
        root_id=root_id,
        payload={"case_id": semantic_id, "role": "semantic-dependent"},
    )
    (
        selected_projection,
        sibling_projection,
        selected_runtime_artifact,
        sibling_runtime_artifact,
    ) = _baseline_runtime_projections(baseline, root_id=root_id)
    sibling_queue_entry_id = next(
        entry.queue_entry_id
        for entry, artifact in zip(
            baseline.queue_entries, baseline.queue_artifacts, strict=True
        )
        if artifact.artifact_id == sibling_runtime_artifact.artifact_id
    )
    baseline_artifacts = (
        baseline_source,
        semantic_dependent,
        selected_projection,
        sibling_projection,
    )
    observed_artifacts = (observed_source, *baseline_artifacts[1:])
    context_only = bool(source["context_only"])
    policy_change = bool(source["policy_change"])
    replay_edges = (
        ()
        if context_only
        else (
            ArtifactDependencyEdgeV01(
                artifact_id=semantic_dependent.artifact_id,
                depends_on_artifact_id=baseline_source.artifact_id,
            ),
            *(
                ()
                if policy_change
                else (
                    ArtifactDependencyEdgeV01(
                        artifact_id=selected_projection.artifact_id,
                        depends_on_artifact_id=semantic_dependent.artifact_id,
                    ),
                )
            ),
        )
    )
    manifest = build_artifact_manifest_v01(
        transaction_id=transaction_id,
        profile=build_default_seal_profile_v01(),
        artifacts=tuple(
            kernel_artifact_to_canonical_ref_v01(item)
            for item in baseline_artifacts
        ),
        dependency_edges=replay_edges,
        root_ownership_bindings=tuple(
            RootOwnershipBindingV01(item.artifact_id, root_id)
            for item in baseline_artifacts
        ),
        evidence_class_bindings=tuple(
            EvidenceClassBindingV01(item.artifact_id, "SOURCE_EVIDENCE")
            for item in baseline_artifacts
        ),
        authority_class_bindings=tuple(
            AuthorityClassBindingV01(item.artifact_id, item.authority_class)
            for item in baseline_artifacts
        ),
    )
    replay = verify_artifact_replay_v01(
        manifest=manifest,
        payload_rows=tuple(
            (
                item.artifact_id,
                kernel_artifact_to_plain_dict_v01(item)["payload"],
            )
            for item in baseline_artifacts
        ),
        expected_manifest_hash=manifest.manifest_hash,
    )
    policy = g2b["report"].query.policy_version
    observed_policy = policy + ":successor" if policy_change else policy
    schema_versions = g2b["report"].query.schema_versions
    history = g2b["report"].query_evaluations[0].source_history_hash
    edge_projection_bindings = tuple(
        (
            edge.artifact_id,
            edge.depends_on_artifact_id,
            (dependency_pointer,)
            if edge.depends_on_artifact_id == baseline_source.artifact_id
            else (),
            "FIELD_CAUSAL"
            if edge.depends_on_artifact_id == baseline_source.artifact_id
            else "ARTIFACT_DEPENDENCY",
        )
        for edge in replay_edges
    )
    graph_projection_result = g2e.project_integrity_replay_dependency_edges_v01(
        manifest=manifest,
        replay=replay,
        source_artifacts=baseline_artifacts,
        graph_version=g2e.CONTINUOUS_DELTA_GRAPH_VERSION_V01,
        transaction_id=transaction_id,
        owning_root_id=root_id,
        domain_id=domain_id,
        policy_version=policy,
        schema_versions=schema_versions,
        source_history_hash=history,
        edge_projection_bindings=edge_projection_bindings,
    )
    graph_basis, dependency_edges = graph_projection_result
    graph = g2e.build_dependency_graph_index_v01(
        graph_basis_sha256=graph_basis,
        graph_version=g2e.CONTINUOUS_DELTA_GRAPH_VERSION_V01,
        manifest=manifest,
        replay=replay,
        source_artifacts=baseline_artifacts,
        dependency_edges=dependency_edges,
        transaction_id=transaction_id,
        owning_root_id=root_id,
        domain_id=domain_id,
        policy_version=policy,
        schema_versions=schema_versions,
        source_history_hash=history,
        trace_refs=(f"trace:g2e5:{slug}:graph:{source_digest}",),
    )
    fingerprint_profile = g2e.build_dependency_fingerprint_profile_v01()
    before = g2e.build_dependency_fingerprint_v01(
        profile=fingerprint_profile,
        graph=graph,
        dependency_edges=dependency_edges,
        source_artifacts=baseline_artifacts,
        policy_version=policy,
        schema_versions=schema_versions,
        source_history_hash=history,
    )
    after = g2e.build_dependency_fingerprint_v01(
        profile=fingerprint_profile,
        graph=graph,
        dependency_edges=dependency_edges,
        source_artifacts=observed_artifacts,
        policy_version=observed_policy,
        schema_versions=schema_versions,
        source_history_hash=history,
    )
    source_binding = g2e.build_delta_source_binding_v01(
        request_id=baseline.runtime_report.request_id,
        transaction_id=transaction_id,
        owning_root_id=root_id,
        domain_id=domain_id,
        baseline_source_artifact_id=baseline_source.artifact_id,
        baseline_source_artifact_type=baseline_source.artifact_type,
        baseline_source_artifact_sha256=_artifact_sha256(baseline_source),
        baseline_source_payload_sha256=_payload_sha256(baseline_source),
        observed_source_artifact_id=observed_source.artifact_id,
        observed_source_artifact_type=observed_source.artifact_type,
        observed_source_artifact_sha256=_artifact_sha256(observed_source),
        observed_source_payload_sha256=_payload_sha256(observed_source),
        baseline_report_id=baseline.runtime_report.report_id,
        baseline_graph_id=graph.graph_id,
        baseline_graph_version=graph.graph_version,
        baseline_policy_version=policy,
        observed_policy_version=observed_policy,
        baseline_schema_versions=schema_versions,
        observed_schema_versions=schema_versions,
        baseline_source_history_hash=history,
        observed_source_history_hash=history,
        valid_from_utc=EVALUATION_UTC,
        valid_to_utc=VALID_TO_UTC,
        trace_refs=(f"trace:g2e5:{slug}:source-binding:{source_digest}",),
    )
    prior_value_hash = hashlib.sha256(
        canonical_json_bytes_v01(source["prior_value"])
    ).hexdigest()
    observed_value_hash = hashlib.sha256(
        canonical_json_bytes_v01(source["observed_value"])
    ).hexdigest()
    changed_field = g2e.build_changed_field_binding_v01(
        source_binding_id=source_binding.source_binding_id,
        json_pointer=artifact_pointer,
        prior_value_sha256=prior_value_hash,
        observed_value_sha256=observed_value_hash,
        change_class="FIELD_VALUE_CHANGE",
        observed_at_utc=EVALUATION_UTC,
        trace_refs=(source_binding.source_binding_id,),
    )
    changed_artifact = g2e.build_changed_artifact_binding_v01(
        source_binding_id=source_binding.source_binding_id,
        baseline_artifact_id=baseline_source.artifact_id,
        baseline_artifact_type=baseline_source.artifact_type,
        baseline_payload_sha256=_payload_sha256(baseline_source),
        observed_artifact_id=observed_source.artifact_id,
        observed_artifact_type=observed_source.artifact_type,
        observed_payload_sha256=_payload_sha256(observed_source),
        baseline_dependency_fingerprint=before,
        observed_dependency_fingerprint=after,
        change_class="ARTIFACT_SUCCESSOR",
        observed_at_utc=EVALUATION_UTC,
        trace_refs=(source_binding.source_binding_id,),
    )
    delta = g2e.build_world_state_delta_v01(
        ordered_source_binding_ids=(source_binding.source_binding_id,),
        request_id=source_binding.request_id,
        transaction_id=transaction_id,
        owning_root_id=root_id,
        domain_id=domain_id,
        baseline_report_id=baseline.runtime_report.report_id,
        baseline_graph_id=graph.graph_id,
        baseline_graph_version=graph.graph_version,
        observed_at_utc=EVALUATION_UTC,
        valid_from_utc=EVALUATION_UTC,
        valid_to_utc=VALID_TO_UTC,
        baseline_policy_version=policy,
        observed_policy_version=observed_policy,
        baseline_schema_versions=schema_versions,
        observed_schema_versions=schema_versions,
        baseline_source_history_hash=history,
        observed_source_history_hash=history,
        ordered_changed_field_binding_ids=(changed_field.changed_field_binding_id,),
        ordered_changed_artifact_binding_ids=(
            changed_artifact.changed_artifact_binding_id,
        ),
        dependency_fingerprint_before=before,
        dependency_fingerprint_after=after,
        trace_refs=(f"trace:g2e5:{slug}:delta:{source_digest}",),
    )
    request = g2e.build_affected_set_request_v01(
        delta=delta,
        graph=graph,
        trace_refs=(delta.delta_id, graph.graph_id),
    )
    affected = g2e.compute_affected_set_v01(
        request=request,
        delta=delta,
        graph=graph,
        source_bindings=(source_binding,),
        changed_field_bindings=(changed_field,),
        changed_artifact_bindings=(changed_artifact,),
        dependency_edges=dependency_edges,
        baseline_source_artifacts=baseline_artifacts,
        observed_source_artifacts=observed_artifacts,
    )
    affected_validation = g2e.validate_affected_set_against_graph_v01(
        affected,
        request=request,
        delta=delta,
        graph=graph,
        source_bindings=(source_binding,),
        changed_field_bindings=(changed_field,),
        changed_artifact_bindings=(changed_artifact,),
        dependency_edges=dependency_edges,
        baseline_source_artifacts=baseline_artifacts,
        observed_source_artifacts=observed_artifacts,
    )
    _require_public_pass(affected_validation, "g2e5_affected_set_invalid")
    context = g2e.build_continuous_delta_source_context_v01(
        integrity_manifest=manifest,
        integrity_replay=replay,
        baseline_source_artifacts=baseline_artifacts,
        observed_source_artifacts=observed_artifacts,
        g2a_registry=g2a["registry"],
        g2a_packet=g2a["packet"],
        g2a_dependency_candidate=g2a["dependency"],
        g2a_current_observations=g2a["observations"],
        g2a_root_invalidation_material=g2a["invalidation"],
        g2b_resolution_report=g2b["report"],
        g2b_reuse_certificate=g2b["certificate"],
        g2b_writeback_evidence=None,
        g2c_source_context=source_family["g2c_source"],
        baseline_g2c_route_eligibility_artifact=source_family["route"],
        baseline_g2d_execution_bundle=baseline,
        root_kernel=source_family["root_kernel"],
        post_vv_profile=None,
        gt_profile=None,
    )
    return {
        "case_id": case_id,
        "semantic_case_id": semantic_id,
        "domain_id": domain_id,
        "baseline": baseline_artifacts,
        "observed": observed_artifacts,
        "typed_source": source,
        "manifest": manifest,
        "replay": replay,
        "graph_projection_result": graph_projection_result,
        "graph_basis_sha256": graph_basis,
        "dependency_edges": dependency_edges,
        "graph": graph,
        "fingerprint_profile": fingerprint_profile,
        "source_binding": source_binding,
        "changed_field": changed_field,
        "changed_artifact": changed_artifact,
        "delta": delta,
        "request": request,
        "affected": affected,
        "affected_validation": affected_validation,
        "context": context,
        "g2a": g2a,
        "baseline_public_return": source_family["baseline_public_return"],
        "selected_projection": selected_projection,
        "sibling_projection": sibling_projection,
        "selected_runtime_artifact": selected_runtime_artifact,
        "sibling_runtime_artifact": sibling_runtime_artifact,
        "sibling_queue_entry_id": sibling_queue_entry_id,
        "context_only": context_only,
        "policy_change": policy_change,
    }


_ZERO_COUNTER_FIELDS = (
    "provider_calls",
    "model_calls",
    "network_calls",
    "connector_calls",
    "external_drs_calls",
    "action_commit_packets_created",
    "permissions_created",
    "receipts_created",
    "final_outputs_created",
    "drs_writes",
    "authority_created_count",
    "real_world_effects_count",
)


def _observed_zero_counters(*carriers: object) -> dict[str, int]:
    observed: dict[str, list[int]] = {name: [] for name in _ZERO_COUNTER_FIELDS}
    aliases = {
        "action_commit_packets_created": "action_commit_packet_created",
        "permissions_created": "permission_created",
        "receipts_created": "receipt_created",
        "final_outputs_created": "final_output_created",
        "drs_writes": "drs_write_created",
        "authority_created_count": "authority_created",
    }
    for carrier in carriers:
        if carrier is None:
            continue
        for name in _ZERO_COUNTER_FIELDS:
            source_name = name if hasattr(carrier, name) else aliases.get(name)
            if source_name is not None and hasattr(carrier, source_name):
                value = getattr(carrier, source_name)
                observed[name].append(int(value))
    if any(not values for values in observed.values()):
        missing = tuple(name for name, values in observed.items() if not values)
        raise ValueError("g2e5_counter_source_missing:" + ",".join(missing))
    result = {name: sum(values) for name, values in observed.items()}
    if any(result.values()):
        raise ValueError("g2e5_zero_operation_boundary_violated")
    return result


def _execute_case_inputs(inputs: dict[str, object]) -> dict[str, object]:
    common = {
        "source_context": inputs["context"],
        "source_bindings": (inputs["source_binding"],),
        "changed_field_bindings": (inputs["changed_field"],),
        "changed_artifact_bindings": (inputs["changed_artifact"],),
        "delta": inputs["delta"],
        "dependency_edges": inputs["dependency_edges"],
        "dependency_graph": inputs["graph"],
    }
    if inputs["context_only"]:
        if inputs["affected"].ordered_affected_ids:
            raise ValueError("g2e5_context_only_affected")
        proof = g2e.prove_unaffected_artifact_preservation_v01(
            affected_set=inputs["affected"],
            invalidation_records=(),
            source_context=inputs["context"],
            recomputed_g2d_execution_bundle=(
                inputs["context"].baseline_g2d_execution_bundle
            ),
            recomputed_bindings=(),
        )
        _require_public_pass(
            g2e.validate_preservation_proof_v01(proof),
            "g2e5_context_preservation_invalid",
        )
        counters = _observed_zero_counters(
            inputs["context"].baseline_g2d_execution_bundle.runtime_report,
            inputs["typed_source"]["typed_validation"][0],
            inputs["typed_source"]["typed_validation"][1],
        )
        return {
            "outcome": "CONTEXT_ONLY_PRESERVED",
            "invalidation_records": (),
            "invalidation_report": None,
            "invalidation_result": None,
            "bundle": None,
            "report": None,
            "preservation_proof": proof,
            "counters": counters,
            "selective_call": None,
        }
    invalidation_result = g2e.derive_invalidation_report_v01(
        affected_set=inputs["affected"],
        delta=inputs["delta"],
        source_context=inputs["context"],
        source_bindings=(inputs["source_binding"],),
        changed_field_bindings=(inputs["changed_field"],),
        changed_artifact_bindings=(inputs["changed_artifact"],),
        dependency_edges=inputs["dependency_edges"],
        dependency_graph=inputs["graph"],
    )
    records, invalidation = invalidation_result
    invalidation_validation = g2e.validate_invalidation_report_against_sources_v01(
        invalidation,
        records=records,
        affected_set=inputs["affected"],
        delta=inputs["delta"],
        source_context=inputs["context"],
        source_bindings=(inputs["source_binding"],),
        changed_field_bindings=(inputs["changed_field"],),
        changed_artifact_bindings=(inputs["changed_artifact"],),
        dependency_edges=inputs["dependency_edges"],
        dependency_graph=inputs["graph"],
    )
    _require_public_pass(
        invalidation_validation, "g2e5_invalidation_context_invalid"
    )
    if inputs["policy_change"]:
        if (
            invalidation.ordered_route_revalidation_ids
            and invalidation.reason_codes
            == ("g2e_route_revalidation_required",)
        ):
            outcome = "ROUTE_REVALIDATION_REQUIRED"
        else:
            raise ValueError("g2e5_policy_route_revalidation_missing")
        counters = _observed_zero_counters(
            inputs["context"].baseline_g2d_execution_bundle.runtime_report,
            invalidation,
            invalidation_validation,
        )
        return {
            "outcome": outcome,
            "invalidation_records": records,
            "invalidation_report": invalidation,
            "invalidation_result": invalidation_result,
            "bundle": None,
            "report": invalidation_validation,
            "preservation_proof": None,
            "counters": counters,
            "selective_call": None,
        }
    selective_result = g2e.run_continuous_delta_runtime_v01(**common)
    bundle, report = selective_result
    if bundle is None or report.status != "PASS":
        reason_material = _canonical_json_text(list(report.reason_codes))
        raise ValueError("g2e5_selective_execution_failed:" + reason_material)
    _require_public_pass(
        g2e.validate_continuous_delta_execution_bundle_v01(bundle),
        "g2e5_selective_bundle_invalid",
    )
    if (
        bundle.final_root_decision_result.decision != "ACCEPT"
        or bundle.recomputation_result.result_status != "PASS"
        or bundle.runtime_report.report_status != "PASS"
    ):
        raise ValueError("g2e5_selective_observed_outcome_invalid")
    counters = _observed_zero_counters(
        bundle.recomputation_result,
        bundle.runtime_trace,
        bundle.runtime_report,
        bundle.plan_root_decision_result,
        bundle.final_root_decision_result,
    )
    return {
        "outcome": "SELECTIVE_RECOMPUTATION_PASS",
        "invalidation_records": bundle.invalidation_records,
        "invalidation_report": bundle.invalidation_report,
        "invalidation_result": invalidation_result,
        "bundle": bundle,
        "report": report,
        "preservation_proof": bundle.preservation_proof,
        "counters": counters,
        "selective_call": {
            "kwargs": common,
            "result": selective_result,
        },
    }


def _execute_conditional_negative_inputs(
    inputs: dict[str, object],
) -> dict[str, object]:
    call_kwargs = {
        "source_context": inputs["context"],
        "source_bindings": (inputs["source_binding"],),
        "changed_field_bindings": (inputs["changed_field"],),
        "changed_artifact_bindings": (inputs["changed_artifact"],),
        "delta": inputs["delta"],
        "dependency_edges": inputs["dependency_edges"],
        "dependency_graph": inputs["graph"],
    }
    selective_result = g2e.run_continuous_delta_runtime_v01(**call_kwargs)
    bundle, report = selective_result
    if (
        bundle is not None
        or report.status != "FAIL_CLOSED"
        or report.reason_codes
        != (
            "g2e_recomputation_no_progress",
            "g2e_transition_selective_recomputation_blocked",
        )
        or report.return_to_root_required is not True
        or report.root_review_required is not False
        or report.authority_created
        or report.permission_created
        or report.action_commit_packet_created
        or report.receipt_created
        or report.final_output_created
        or report.drs_write_created
        or report.real_world_effects_count != 0
    ):
        raise ValueError("g2e5_conditional_carrier_missing")
    return {
        "inputs": inputs,
        "failure_report": report,
        "semantic_call_kwargs": call_kwargs,
        "semantic_call_result": selective_result,
    }


def _constructive_case_result(
    *,
    case_id: str,
    inputs: dict[str, object],
    execution: dict[str, object],
    repeat_execution: dict[str, object] | None = None,
    semantic_projection_memo: dict[
        int, tuple[object, dict[str, object]]
    ],
) -> ContinuousDeltaRuntimeG2ECaseResultV01:
    bundle = execution["bundle"]
    invalidation = execution["invalidation_report"]
    proof = execution["preservation_proof"]
    expected_outcome = (
        "ROUTE_REVALIDATION_REQUIRED"
        if inputs["policy_change"]
        else "CONTEXT_ONLY_PRESERVED"
        if inputs["context_only"]
        else "SELECTIVE_RECOMPUTATION_PASS"
    )
    observed_reasons = (
        tuple(invalidation.reason_codes)
        if inputs["policy_change"]
        else ()
    )
    expected_reasons = (
        ("g2e_route_revalidation_required",)
        if inputs["policy_change"]
        else ()
    )
    if observed_reasons != expected_reasons:
        raise ValueError("g2e5_constructive_reason_invalid")
    if repeat_execution is not None:
        repeated_bundle = repeat_execution["bundle"]
        first_report = execution["report"]
        repeated_report = repeat_execution["report"]
        if type(bundle) is not g2e.ContinuousDeltaExecutionBundleV01 or type(
            repeated_bundle
        ) is not g2e.ContinuousDeltaExecutionBundleV01:
            raise ValueError("g2e5_repeat_bundle_missing")
        first_bundle_bytes = _semantic_projection_bytes(
            bundle, semantic_projection_memo
        )
        second_bundle_bytes = _semantic_projection_bytes(
            repeated_bundle, semantic_projection_memo
        )
        first_report_bytes = _semantic_projection_bytes(
            first_report, semantic_projection_memo
        )
        second_report_bytes = _semantic_projection_bytes(
            repeated_report, semantic_projection_memo
        )
        first_return = execution["selective_call"]["result"]
        second_return = repeat_execution["selective_call"]["result"]
        first_return_bytes = _semantic_projection_bytes(
            first_return, semantic_projection_memo
        )
        second_return_bytes = _semantic_projection_bytes(
            second_return, semantic_projection_memo
        )
        if (
            first_bundle_bytes != second_bundle_bytes
            or first_report_bytes != second_report_bytes
            or first_return_bytes != second_return_bytes
            or bundle is repeated_bundle
            or first_report is repeated_report
        ):
            raise ValueError("g2e5_repeat_execution_not_independent")
        repeat_material = {
            "independent_execution_count": 2,
            "first_bundle_sha256": hashlib.sha256(
                first_bundle_bytes
            ).hexdigest(),
            "second_bundle_sha256": hashlib.sha256(
                second_bundle_bytes
            ).hexdigest(),
            "bundle_byte_length": len(first_bundle_bytes),
            "first_report_sha256": hashlib.sha256(
                first_report_bytes
            ).hexdigest(),
            "second_report_sha256": hashlib.sha256(
                second_report_bytes
            ).hexdigest(),
            "report_byte_length": len(first_report_bytes),
            "first_return_tuple_sha256": hashlib.sha256(
                first_return_bytes
            ).hexdigest(),
            "second_return_tuple_sha256": hashlib.sha256(
                second_return_bytes
            ).hexdigest(),
            "return_tuple_byte_length": len(first_return_bytes),
            "bundle_bytes_equal": True,
            "report_bytes_equal": True,
            "return_tuple_bytes_equal": True,
            "bundle_same_object": False,
            "report_same_object": False,
        }
    else:
        repeat_material = None
    root_ids = (
        (
            bundle.plan_root_decision_result.decision_id,
            bundle.final_root_decision_result.decision_id,
        )
        if type(bundle) is g2e.ContinuousDeltaExecutionBundleV01
        else ()
    )
    graph = inputs["graph"]
    dependency_edges = inputs["dependency_edges"]
    request = inputs["request"]
    affected = inputs["affected"]
    graph_projection_result = inputs["graph_projection_result"]
    selective_rows = tuple(
        row
        for row in (execution, repeat_execution)
        if row is not None and row["selective_call"] is not None
    )
    selective_evidence = []
    for row in selective_rows:
        call = row["selective_call"]
        call_kwargs = call["kwargs"]
        returned_bundle, validation_report = call["result"]
        if type(returned_bundle) is not g2e.ContinuousDeltaExecutionBundleV01:
            raise ValueError("g2e5_selective_call_chain_bundle_missing")
        selective_evidence.append(
            {
                "dependency_graph_id": call_kwargs["dependency_graph"].graph_id,
                "delta_id": call_kwargs["delta"].delta_id,
                "affected_request_id": (
                    returned_bundle.affected_request.affected_request_id
                ),
                "affected_set_id": returned_bundle.affected_result.affected_set_id,
                "recomputation_result_id": (
                    returned_bundle.recomputation_result.recomputation_result_id
                ),
                "runtime_report_id": returned_bundle.runtime_report.report_id,
                "validation_report_status": validation_report.status,
                "dependency_graph_binding": _semantic_return_binding(
                    call_kwargs["dependency_graph"], semantic_projection_memo
                ),
                "dependency_edges_binding": _semantic_return_binding(
                    call_kwargs["dependency_edges"], semantic_projection_memo
                ),
                "delta_binding": _semantic_return_binding(
                    call_kwargs["delta"], semantic_projection_memo
                ),
                "bundle_dependency_graph_binding": _semantic_return_binding(
                    returned_bundle.dependency_graph,
                    semantic_projection_memo,
                ),
                "bundle_dependency_edges_binding": _semantic_return_binding(
                    returned_bundle.dependency_edges,
                    semantic_projection_memo,
                ),
                "bundle_delta_binding": _semantic_return_binding(
                    returned_bundle.delta, semantic_projection_memo
                ),
                "bundle_affected_request_binding": _semantic_return_binding(
                    returned_bundle.affected_request,
                    semantic_projection_memo,
                ),
                "bundle_affected_result_binding": _semantic_return_binding(
                    returned_bundle.affected_result,
                    semantic_projection_memo,
                ),
                "bundle_binding": _semantic_return_binding(
                    returned_bundle, semantic_projection_memo
                ),
                "validation_report_binding": _semantic_return_binding(
                    validation_report, semantic_projection_memo
                ),
                "return_tuple_binding": _semantic_return_binding(
                    call["result"],
                    semantic_projection_memo,
                ),
                "external_actual_return_required": True,
            }
        )
    constructive_call_chain = {
        "proof_boundary": (
            "standalone_witness_integrity_plus_external_actual_return_oracle"
        ),
        "graph_projection": {
            "graph_basis_sha256": inputs["graph_basis_sha256"],
            "ordered_dependency_edge_ids": [
                item.edge_id for item in dependency_edges
            ],
            "return_witness": _semantic_return_witness(
                graph_projection_result, semantic_projection_memo
            ),
            "dependency_edges_binding": _semantic_return_binding(
                dependency_edges, semantic_projection_memo
            ),
        },
        "graph_construction": {
            "graph_id": graph.graph_id,
            "graph_basis_sha256": graph.graph_basis_sha256,
            "ordered_edge_ids": list(graph.ordered_edge_ids),
            "graph_witness": _semantic_return_witness(
                graph, semantic_projection_memo
            ),
        },
        "affected_set_computation": {
            "affected_request_id": request.affected_request_id,
            "request_graph_id": request.graph_id,
            "request_delta_id": request.delta_id,
            "kwargs_graph_id": graph.graph_id,
            "kwargs_delta_id": inputs["delta"].delta_id,
            "returned_affected_request_id": affected.affected_request_id,
            "returned_affected_set_id": affected.affected_set_id,
            "returned_graph_id": affected.graph_id,
            "returned_delta_id": affected.delta_id,
            "request_witness": _semantic_return_witness(
                request, semantic_projection_memo
            ),
            "kwargs_graph_binding": _semantic_return_binding(
                graph, semantic_projection_memo
            ),
            "kwargs_delta_witness": _semantic_return_witness(
                inputs["delta"], semantic_projection_memo
            ),
            "affected_result_witness": _semantic_return_witness(
                affected, semantic_projection_memo
            ),
        },
        "selective_execution": (
            None if not selective_evidence else selective_evidence
        ),
    }
    carrier_material = {
        "dependency_graph_type": type(inputs["graph"]).__name__,
        "dependency_graph_id": inputs["graph"].graph_id,
        "dependency_edge_type": "DeltaDependencyEdgeV01",
        "dependency_edge_ids": [
            item.edge_id for item in inputs["dependency_edges"]
        ],
        "affected_validation_report_id": (
            inputs["affected_validation"].validation_report_id
        ),
        "affected_set_id": inputs["affected"].affected_set_id,
        "invalidation_report_id": (
            None if invalidation is None else invalidation.invalidation_report_id
        ),
        "selective_bundle_type": None if bundle is None else type(bundle).__name__,
        "recomputation_result_id": (
            None if bundle is None else bundle.recomputation_result.recomputation_result_id
        ),
        "runtime_trace_id": None if bundle is None else bundle.runtime_trace.trace_id,
        "runtime_report_id": None if bundle is None else bundle.runtime_report.report_id,
        "root_review_ids": list(root_ids),
        "transition_ids": (
            []
            if bundle is None
            else [item.decision_id for item in bundle.g2e_transition_decisions]
        ),
        "abi_artifact_ids": (
            []
            if bundle is None
            else [
                bundle.delta_source_proposed_artifact.artifact_id,
                bundle.delta_source_artifact.artifact_id,
                bundle.dependency_graph_artifact.artifact_id,
                bundle.affected_set_artifact.artifact_id,
                bundle.invalidation_report_artifact.artifact_id,
                bundle.plan_proposed_artifact.artifact_id,
                bundle.plan_accepted_artifact.artifact_id,
                bundle.preservation_proof_artifact.artifact_id,
                bundle.runtime_report_artifact.artifact_id,
            ]
        ),
    }
    safe_sibling_material = None
    if case_id == "g2e_case:warehouse:safe_sibling:v01":
        if (
            type(bundle) is not g2e.ContinuousDeltaExecutionBundleV01
            or execution["report"].status != "PASS"
            or proof is None
        ):
            raise ValueError("g2e5_safe_sibling_bundle_missing")
        sibling_projection = inputs["sibling_projection"]
        baseline_runtime_sibling = inputs["sibling_runtime_artifact"]
        sibling_queue_entry_id = inputs["sibling_queue_entry_id"]
        recomputed_runtime_sibling = next(
            artifact
            for entry, artifact in zip(
                bundle.recomputed_g2d_execution_bundle.queue_entries,
                bundle.recomputed_g2d_execution_bundle.queue_artifacts,
                strict=True,
            )
            if entry.queue_entry_id == sibling_queue_entry_id
        )
        matching_sibling_rows = tuple(
            index
            for index, artifact_id in enumerate(
                proof.ordered_preserved_artifact_ids
            )
            if artifact_id == baseline_runtime_sibling.artifact_id
        )
        if len(matching_sibling_rows) != 1:
            raise ValueError("g2e5_safe_sibling_preservation_missing")
        sibling_index = matching_sibling_rows[0]
        projection_plain = kernel_artifact_to_plain_dict_v01(
            sibling_projection
        )
        projection_bytes = canonical_json_bytes_v01(projection_plain)
        projection_payload_bytes = canonical_json_bytes_v01(
            projection_plain["payload"]
        )
        baseline_runtime_plain = kernel_artifact_to_plain_dict_v01(
            baseline_runtime_sibling
        )
        recomputed_runtime_plain = kernel_artifact_to_plain_dict_v01(
            recomputed_runtime_sibling
        )
        baseline_runtime_bytes = canonical_json_bytes_v01(
            baseline_runtime_plain
        )
        recomputed_runtime_bytes = canonical_json_bytes_v01(
            recomputed_runtime_plain
        )
        baseline_runtime_payload_bytes = canonical_json_bytes_v01(
            baseline_runtime_plain["payload"]
        )
        recomputed_runtime_payload_bytes = canonical_json_bytes_v01(
            recomputed_runtime_plain["payload"]
        )
        baseline_runtime_sha256 = hashlib.sha256(
            baseline_runtime_bytes
        ).hexdigest()
        recomputed_runtime_sha256 = hashlib.sha256(
            recomputed_runtime_bytes
        ).hexdigest()
        baseline_runtime_payload_sha256 = hashlib.sha256(
            baseline_runtime_payload_bytes
        ).hexdigest()
        recomputed_runtime_payload_sha256 = hashlib.sha256(
            recomputed_runtime_payload_bytes
        ).hexdigest()
        invalidated_artifact_ids = tuple(
            item.artifact_id for item in execution["invalidation_records"]
        )
        protected_sibling_ids = {
            baseline_runtime_sibling.artifact_id,
            recomputed_runtime_sibling.artifact_id,
            sibling_projection.artifact_id,
        }
        sibling_touching_bindings = tuple(
            item
            for item in bundle.recomputed_bindings
            if item.prior_artifact_id in protected_sibling_ids
            or item.new_artifact_id in protected_sibling_ids
        )
        actual_recomputed_binding_ids = tuple(
            item.recomputed_binding_id for item in bundle.recomputed_bindings
        )
        recomputed_binding_rows = [
            {
                "recomputed_binding_id": item.recomputed_binding_id,
                "prior_artifact_id": item.prior_artifact_id,
                "new_artifact_id": item.new_artifact_id,
            }
            for item in bundle.recomputed_bindings
        ]
        preservation_proof_rows = [
            {
                "row_index": sibling_index,
                "preserved_artifact_id": (
                    proof.ordered_preserved_artifact_ids[sibling_index]
                ),
                "before_identity_id": (
                    proof.ordered_before_identity_ids[sibling_index]
                ),
                "after_identity_id": (
                    proof.ordered_after_identity_ids[sibling_index]
                ),
                "before_payload_sha256": (
                    proof.ordered_before_payload_sha256[sibling_index]
                ),
                "after_payload_sha256": (
                    proof.ordered_after_payload_sha256[sibling_index]
                ),
                "before_artifact_sha256": (
                    proof.ordered_before_artifact_sha256[sibling_index]
                ),
                "after_artifact_sha256": (
                    proof.ordered_after_artifact_sha256[sibling_index]
                ),
            }
        ]
        baseline_queue_artifact_row = {
            "queue_entry_id": sibling_queue_entry_id,
            "artifact_id": baseline_runtime_sibling.artifact_id,
            "artifact_sha256": baseline_runtime_sha256,
        }
        recomputed_queue_artifact_row = {
            "queue_entry_id": sibling_queue_entry_id,
            "artifact_id": recomputed_runtime_sibling.artifact_id,
            "artifact_sha256": recomputed_runtime_sha256,
        }
        projection_expected_id = (
            "artifact:g2e5:runtime-projection:" + baseline_runtime_sha256
        )
        if (
            sibling_projection.artifact_id
            == baseline_runtime_sibling.artifact_id
            or sibling_projection.artifact_id != projection_expected_id
            or baseline_runtime_sibling.artifact_id.startswith(
                "artifact:g2e5:runtime-projection:"
            )
            or sibling_projection.parent_refs
            != (baseline_runtime_sibling.artifact_id,)
            or projection_plain["payload"]["projected_runtime_artifact"]
            != baseline_runtime_plain
            or projection_plain["payload"][
                "projected_runtime_artifact_sha256"
            ]
            != baseline_runtime_sha256
            or sibling_projection.artifact_id
            in inputs["affected"].ordered_changed_node_ids
            or sibling_projection.artifact_id
            in inputs["affected"].ordered_directly_affected_ids
            or sibling_projection.artifact_id
            in inputs["affected"].ordered_transitively_affected_ids
            or sibling_projection.artifact_id
            in inputs["affected"].ordered_affected_ids
            or sibling_projection.artifact_id in invalidated_artifact_ids
            or baseline_runtime_sibling.artifact_id
            in inputs["affected"].ordered_changed_node_ids
            or baseline_runtime_sibling.artifact_id
            in inputs["affected"].ordered_directly_affected_ids
            or baseline_runtime_sibling.artifact_id
            in inputs["affected"].ordered_transitively_affected_ids
            or baseline_runtime_sibling.artifact_id
            in inputs["affected"].ordered_affected_ids
            or baseline_runtime_sibling.artifact_id in invalidated_artifact_ids
            or sibling_touching_bindings
            or baseline_runtime_sibling.artifact_id
            in bundle.recomputation_result.ordered_recomputed_artifact_ids
            or sibling_projection.artifact_id
            in bundle.recomputation_result.ordered_recomputed_artifact_ids
            or bundle.recomputation_result.ordered_recomputed_binding_ids
            != actual_recomputed_binding_ids
            or proof.ordered_before_identity_ids[sibling_index]
            != baseline_runtime_sibling.artifact_id
            or proof.ordered_after_identity_ids[sibling_index]
            != recomputed_runtime_sibling.artifact_id
            or proof.ordered_before_artifact_sha256[sibling_index]
            != baseline_runtime_sha256
            or proof.ordered_after_artifact_sha256[sibling_index]
            != recomputed_runtime_sha256
            or proof.ordered_before_payload_sha256[sibling_index]
            != baseline_runtime_payload_sha256
            or proof.ordered_after_payload_sha256[sibling_index]
            != recomputed_runtime_payload_sha256
            or baseline_runtime_sibling.artifact_id
            != recomputed_runtime_sibling.artifact_id
            or baseline_runtime_bytes != recomputed_runtime_bytes
            or baseline_runtime_payload_bytes != recomputed_runtime_payload_bytes
        ):
            raise ValueError("g2e5_safe_sibling_bytes_changed")
        safe_sibling_material = {
            "proof_boundary": (
                "standalone_canonical_integrity_plus_external_actual_runtime_oracle"
            ),
            "artifact_id": baseline_runtime_sibling.artifact_id,
            "artifact_sha256": baseline_runtime_sha256,
            "payload_sha256": baseline_runtime_payload_sha256,
            "canonical_artifact_bytes_sha256": baseline_runtime_sha256,
            "canonical_artifact_byte_length": len(baseline_runtime_bytes),
            "canonical_payload_byte_length": len(
                baseline_runtime_payload_bytes
            ),
            "queue_entry_id": sibling_queue_entry_id,
            "runtime_artifact_id": baseline_runtime_sibling.artifact_id,
            "projection_artifact_plain": projection_plain,
            "baseline_runtime_artifact_plain": baseline_runtime_plain,
            "recomputed_runtime_artifact_plain": recomputed_runtime_plain,
            "baseline_queue_artifact_row": baseline_queue_artifact_row,
            "recomputed_queue_artifact_row": recomputed_queue_artifact_row,
            "preservation_proof_rows": preservation_proof_rows,
            "recomputed_binding_rows": recomputed_binding_rows,
            "projection_artifact_id": sibling_projection.artifact_id,
            "projection_artifact_sha256": hashlib.sha256(
                projection_bytes
            ).hexdigest(),
            "projection_artifact_byte_length": len(projection_bytes),
            "projection_payload_sha256": hashlib.sha256(
                projection_payload_bytes
            ).hexdigest(),
            "projection_payload_byte_length": len(projection_payload_bytes),
            "projection_parent_runtime_artifact_id": (
                sibling_projection.parent_refs[0]
            ),
            "projection_embedded_runtime_artifact_sha256": (
                projection_plain["payload"][
                    "projected_runtime_artifact_sha256"
                ]
            ),
            "projection_embedded_runtime_artifact_byte_length": len(
                canonical_json_bytes_v01(
                    projection_plain["payload"]["projected_runtime_artifact"]
                )
            ),
            "baseline_runtime_payload_sha256": (
                baseline_runtime_payload_sha256
            ),
            "baseline_runtime_payload_byte_length": len(
                baseline_runtime_payload_bytes
            ),
            "recomputed_runtime_payload_sha256": (
                recomputed_runtime_payload_sha256
            ),
            "recomputed_runtime_payload_byte_length": len(
                recomputed_runtime_payload_bytes
            ),
            "baseline_runtime_artifact_sha256": baseline_runtime_sha256,
            "baseline_runtime_artifact_byte_length": len(
                baseline_runtime_bytes
            ),
            "recomputed_runtime_artifact_sha256": recomputed_runtime_sha256,
            "recomputed_runtime_artifact_byte_length": len(
                recomputed_runtime_bytes
            ),
            "invalidation_record_artifact_ids": list(
                invalidated_artifact_ids
            ),
            "ordered_recomputed_binding_ids": list(
                actual_recomputed_binding_ids
            ),
            "result_ordered_recomputed_binding_ids": list(
                bundle.recomputation_result.ordered_recomputed_binding_ids
            ),
            "result_ordered_recomputed_artifact_ids": list(
                bundle.recomputation_result.ordered_recomputed_artifact_ids
            ),
            "sibling_touching_recomputed_binding_ids": [
                item.recomputed_binding_id for item in sibling_touching_bindings
            ],
            "sibling_touching_prior_artifact_ids": [
                item.prior_artifact_id for item in sibling_touching_bindings
            ],
            "sibling_touching_new_artifact_ids": [
                item.new_artifact_id for item in sibling_touching_bindings
            ],
            "preservation_row_index": sibling_index,
            "preservation_before_identity_id": (
                proof.ordered_before_identity_ids[sibling_index]
            ),
            "preservation_after_identity_id": (
                proof.ordered_after_identity_ids[sibling_index]
            ),
            "preservation_before_payload_sha256": (
                proof.ordered_before_payload_sha256[sibling_index]
            ),
            "preservation_after_payload_sha256": (
                proof.ordered_after_payload_sha256[sibling_index]
            ),
            "preservation_before_artifact_sha256": (
                proof.ordered_before_artifact_sha256[sibling_index]
            ),
            "preservation_after_artifact_sha256": (
                proof.ordered_after_artifact_sha256[sibling_index]
            ),
        }
    evidence = {
        "case_id": case_id,
        "semantic_case_id": inputs["semantic_case_id"],
        "domain_id": inputs["domain_id"],
        "typed_baseline_type": type(
            inputs["typed_source"]["baseline_typed"]
        ).__name__,
        "typed_observed_type": type(
            inputs["typed_source"]["observed_typed"]
        ).__name__,
        "typed_validation": [
            _typed_validation_plain(item)
            for item in inputs["typed_source"]["typed_validation"]
        ],
        "source_pointer": inputs["typed_source"]["pointer"],
        "baseline_public_return": inputs["baseline_public_return"],
        "constructive_call_chain": constructive_call_chain,
        "artifact_source_pointer": inputs["changed_field"].json_pointer,
        "prior_value_sha256": inputs["changed_field"].prior_value_sha256,
        "observed_value_sha256": inputs["changed_field"].observed_value_sha256,
        "graph_source_manifest_id": inputs["graph"].source_manifest_id,
        "graph_source_replay_id": inputs["graph"].source_replay_id,
        "carrier_material": carrier_material,
        "partitions": {
            "changed": inputs["affected"].ordered_changed_node_ids,
            "direct": inputs["affected"].ordered_directly_affected_ids,
            "transitive": inputs["affected"].ordered_transitively_affected_ids,
            "affected": inputs["affected"].ordered_affected_ids,
            "preserved": (
                proof.ordered_preserved_artifact_ids
                if proof is not None
                else inputs["affected"].ordered_unaffected_ids
            ),
        },
        "observed_outcome": execution["outcome"],
        "observed_zero_counters": execution["counters"],
        "repeat_execution": repeat_material,
        "safe_sibling": safe_sibling_material,
        "delta_sequence": inputs["delta"].delta_sequence,
        "prior_delta_id": inputs["delta"].prior_delta_id,
        "source_collectors_replayed": False,
        "successor_baseline_created": False,
    }
    evidence_json = _canonical_json_text(_plain_data(evidence))
    evidence_sha = _sha256_domain(CASE_EVIDENCE_DOMAIN, json.loads(evidence_json))
    preserved_ids = (
        proof.ordered_preserved_artifact_ids
        if proof is not None
        else inputs["affected"].ordered_unaffected_ids
    )
    return ContinuousDeltaRuntimeG2ECaseResultV01(
        case_id=case_id,
        case_class="CONSTRUCTIVE",
        domain_id=inputs["domain_id"],
        expected_outcome=expected_outcome,
        observed_outcome=execution["outcome"],
        baseline_runtime_report_id=(
            inputs["context"].baseline_g2d_execution_bundle.runtime_report.report_id
        ),
        delta_id=inputs["delta"].delta_id,
        affected_set_id=inputs["affected"].affected_set_id,
        invalidation_report_id=(
            None if invalidation is None else invalidation.invalidation_report_id
        ),
        recomputation_plan_id=(
            None if bundle is None else bundle.recomputation_plan.recomputation_plan_id
        ),
        recomputation_result_id=(
            None if bundle is None else bundle.recomputation_result.recomputation_result_id
        ),
        continuous_delta_runtime_report_id=(
            None if bundle is None else bundle.runtime_report.report_id
        ),
        ordered_changed_ids=inputs["affected"].ordered_changed_node_ids,
        ordered_directly_affected_ids=inputs["affected"].ordered_directly_affected_ids,
        ordered_transitively_affected_ids=(
            inputs["affected"].ordered_transitively_affected_ids
        ),
        ordered_invalidated_ids=tuple(
            item.artifact_id for item in execution["invalidation_records"]
        ),
        ordered_recomputed_ids=(
            ()
            if bundle is None
            else bundle.recomputation_result.ordered_recomputed_artifact_ids
        ),
        ordered_preserved_ids=preserved_ids,
        ordered_unresolved_or_blocked_ids=(
            ()
            if invalidation is None
            else invalidation.ordered_unresolved_artifact_ids
        ),
        ordered_root_review_ids=root_ids,
        subcase_results=(),
        expected_reason_codes=expected_reasons,
        observed_reason_codes=observed_reasons,
        evidence_refs=tuple(
            item
            for item in (
                inputs["graph"].graph_id,
                inputs["affected"].affected_set_id,
                None if invalidation is None else invalidation.invalidation_report_id,
                None if bundle is None else bundle.recomputation_result.recomputation_result_id,
                *root_ids,
            )
            if item is not None
        ),
        evidence_material_json=evidence_json,
        evidence_sha256=evidence_sha,
        **execution["counters"],
        final_status="PASS",
        reason_codes=(),
    )


def _reason_tuple(reason: str | tuple[str, ...]) -> tuple[str, ...]:
    return (reason,) if type(reason) is str else reason


def _negative_subcase_specs(
    suffix: str, axis: str, reason: str | tuple[str, ...]
) -> tuple[tuple[str, str, str | tuple[str, ...]], ...]:
    if suffix == "injected_unrelated_affected_artifact":
        return (
            ("unrelated_injection", axis, "g2e_affected_unrelated_injected"),
            ("pointer_suppression", axis, "g2e_affected_reachable_omitted"),
        )
    if suffix == "route_reused_after_bound_source_change":
        return (
            ("route_source_revalidation", axis, "g2e_route_revalidation_required"),
            ("lower_topology_substitution", axis, "g2e_delta_source_unvalidated"),
        )
    if suffix == "selective_execution_carrier_omission":
        return (
            ("pre_execution_carrier", axis, "g2e_recomputation_plan_invalid"),
            ("post_execution_bundle", axis, "g2e_recomputation_result_invalid"),
            ("post_execution_partial_failure", axis, "g2e_recomputation_result_invalid"),
            ("post_execution_recomputed_binding", axis, "g2e_recomputation_result_invalid"),
            ("post_execution_g2e_evidence", axis, "g2e_recomputation_result_invalid"),
        )
    if suffix == "recomputed_g2d_result_report_ref_substitution":
        return tuple(
            (name, axis, "g2e_recomputation_result_invalid")
            for name in (
                "g2d_cell_result_ref",
                "g2d_runtime_report_ref",
                "preservation_proof_ref",
                "partial_failure_id",
            )
        )
    if suffix == "plan_root_review_carrier_substitution":
        return tuple(
            (
                name,
                axis,
                "g2e_authority_boundary_violated"
                if name in {"target_root", "transaction", "root_artifact"}
                else "g2e_recomputation_plan_invalid"
                if name == "selected_carrier"
                else "g2e_recomputation_result_invalid",
            )
            for name in (
                "root_input",
                "root_result",
                "selected_carrier",
                "prior_decision",
                "target_root",
                "transaction",
                "root_artifact",
            )
        )
    if suffix == "final_root_review_carrier_substitution":
        result_reason = (
            "g2e_recomputation_result_invalid"
        )
        return tuple(
            (name, axis, "g2e_authority_boundary_violated" if name in {"target_root", "transaction", "root_artifact"} else result_reason)
            for name in (
                "root_input",
                "root_result",
                "selected_carrier",
                "g2d_report",
                "preservation_proof",
                "prior_decision",
                "target_root",
                "transaction",
                "root_artifact",
            )
        )
    if suffix == "root_acceptance_outcome_forgery":
        return tuple(
            (name, axis, "g2e_authority_boundary_violated")
            for name in (
                "forged_accept",
                "nonzero_permission",
                "nonzero_final_output",
                "nonzero_effect",
            )
        )
    if suffix == "transition_rule_eleven_field_substitution":
        rule_fields = (
            "rule_id",
            "abi_major_version",
            "source_artifact_type",
            "source_lifecycle_state",
            "actor_role",
            "attempted_effect",
            "target_artifact_type",
            "required_guards",
            "decision",
            "reason_code",
            "root_commit_required",
        )
        return tuple(
            (f"rule_{rule_index:02d}_{field_name}", field_name, "g2e_object_invalid")
            for rule_index in range(1, 11)
            for field_name in rule_fields
        )
    if suffix == "transition_rule_order_or_terminal_path_forgery":
        return (
            ("missing_rule", axis, "g2e_object_invalid"),
            ("duplicate_rule", axis, "g2e_object_invalid"),
            ("extra_rule", axis, "g2e_object_invalid"),
            ("reordered_rules", axis, "g2e_object_invalid"),
            ("t06_nonterminal", axis, "g2e_object_invalid"),
            ("t08_nonterminal", axis, "g2e_object_invalid"),
            ("t10_trace_insertion", axis, "g2e_identity_mismatch"),
            ("non_accept_finalization", axis, "g2e_authority_boundary_violated"),
        )
    if suffix == "abi_projection_profile_substitution":
        profile_fields = (
            "artifact_type",
            "lifecycle_state",
            "authority_class",
            "source_component",
            "payload",
        )
        return tuple(
            (f"profile_{profile_index:02d}_{field_name}", field_name, "g2e_object_invalid")
            for profile_index in range(1, 8)
            for field_name in profile_fields
        )
    if suffix == "abi_parent_trace_or_root_artifact_substitution":
        artifact_instances = (
            "delta_source_proposed_artifact",
            "delta_source_artifact",
            "dependency_graph_artifact",
            "affected_set_artifact",
            "invalidation_report_artifact",
            "plan_proposed_artifact",
            "plan_accepted_artifact",
            "preservation_proof_artifact",
            "runtime_report_artifact",
        )
        lineage_subcases = tuple(
            (
                f"{family}:{index:02d}:{field_name}",
                family,
                "g2e_object_invalid",
            )
            for family in ("parent_ids", "trace_refs", "time_envelope")
            for index, field_name in enumerate(artifact_instances, start=1)
        )
        return (
            *lineage_subcases,
            ("plan_relation", "plan_relation", "g2e_object_invalid"),
            (
                "shared_root_artifact",
                "shared_root_artifact",
                "g2e_authority_boundary_violated",
            ),
        )
    if suffix == "identity_prefix_or_domain_collision":
        return (
            ("serialized_prefix", axis, "g2e_identity_mismatch"),
            ("abi_prefix_domain", axis, "g2e_identity_mismatch"),
            ("cross_role_fingerprint", axis, "g2e_dependency_fingerprint_role_collision"),
        )
    return ((suffix, axis, reason),)


def _carrier_identity(value: object) -> str:
    if is_dataclass(value):
        for field in fields(value):
            if field.name.endswith("_id"):
                candidate = getattr(value, field.name)
                if type(candidate) is str and candidate:
                    return candidate
    return _prefixed_identity(
        "g2e5_mutated_carrier_v01:",
        "HEDGEHOG_G2E5_MUTATED_CARRIER_V01",
        {"type": type(value).__name__, "plain": _plain_data(value)},
    )


def _qualified_type_name(value: object) -> str:
    value_type = type(value)
    return value_type.__module__ + "." + value_type.__qualname__


@dataclass(frozen=True)
class _CompositionalBindingNodeV02:
    sha256: str
    semantic_length: int
    recursively_immutable: bool


def _binding_uint64_v02(value: int) -> bytes:
    if type(value) is not int or value < 0 or value >= 1 << 64:
        raise ValueError("g2e5_compositional_binding_length_invalid")
    return value.to_bytes(8, "big")


def _binding_frame_v02(tag: str, parts: tuple[bytes, ...]) -> bytes:
    if type(tag) is not str or not tag or not tag.isascii():
        raise ValueError("g2e5_compositional_binding_tag_invalid")
    if type(parts) is not tuple or any(type(part) is not bytes for part in parts):
        raise ValueError("g2e5_compositional_binding_parts_invalid")
    return b"".join(
        (
            tag.encode("ascii"),
            b"\x00",
            _binding_uint64_v02(len(parts)),
            *tuple(
                _binding_uint64_v02(len(part)) + part for part in parts
            ),
        )
    )


def _binding_node_v02(
    tag: str,
    parts: tuple[bytes, ...],
    *,
    recursively_immutable: bool,
) -> _CompositionalBindingNodeV02:
    framed = _binding_frame_v02(tag, parts)
    material = _COMPOSITIONAL_BINDING_DOMAIN_V02 + framed
    return _CompositionalBindingNodeV02(
        sha256=hashlib.sha256(material).hexdigest(),
        semantic_length=len(material),
        recursively_immutable=recursively_immutable,
    )


def _binding_child_part_v02(
    role_tag: str,
    role: bytes,
    child: _CompositionalBindingNodeV02,
) -> bytes:
    return _binding_frame_v02(
        role_tag,
        (
            role,
            bytes.fromhex(child.sha256),
            _binding_uint64_v02(child.semantic_length),
        ),
    )


def _compositional_binding_node_v02(
    value: object,
    memo: dict[int, tuple[object, object]] | None = None,
    active: set[int] | None = None,
) -> _CompositionalBindingNodeV02:
    if active is None:
        active = set()
    value_id = id(value)
    params = (
        getattr(type(value), "__dataclass_params__", None)
        if is_dataclass(value) and not isinstance(value, type)
        else None
    )
    potentially_cacheable = type(value) is tuple or bool(
        params is not None and params.frozen
    )
    cache_key = -value_id
    if memo is not None and potentially_cacheable:
        cached = memo.get(cache_key)
        if (
            cached is not None
            and cached[0] is value
            and type(cached[1]) is _CompositionalBindingNodeV02
        ):
            return cached[1]
    compound = (
        type(value) in {tuple, list}
        or isinstance(value, Mapping)
        or (is_dataclass(value) and not isinstance(value, type))
    )
    if compound:
        if value_id in active:
            raise ValueError("g2e5_compositional_binding_cycle_invalid")
        active.add(value_id)
    try:
        if value is None:
            node = _binding_node_v02(
                "none", (), recursively_immutable=True
            )
        elif type(value) is bool:
            node = _binding_node_v02(
                "bool",
                (b"true" if value else b"false",),
                recursively_immutable=True,
            )
        elif type(value) is int:
            encoded = str(value).encode("ascii")
            if int(encoded.decode("ascii")) != value:
                raise ValueError("g2e5_compositional_binding_int_invalid")
            node = _binding_node_v02(
                "int", (encoded,), recursively_immutable=True
            )
        elif type(value) is float:
            if not math.isfinite(value):
                raise ValueError("g2e5_compositional_binding_float_invalid")
            node = _binding_node_v02(
                "float",
                (value.hex().encode("ascii"),),
                recursively_immutable=True,
            )
        elif type(value) is str:
            node = _binding_node_v02(
                "str", (value.encode("utf-8"),), recursively_immutable=True
            )
        elif type(value) is bytes:
            node = _binding_node_v02(
                "bytes", (value,), recursively_immutable=True
            )
        elif type(value) in {tuple, list}:
            children = tuple(
                _compositional_binding_node_v02(item, memo, active)
                for item in value
            )
            node = _binding_node_v02(
                "tuple" if type(value) is tuple else "list",
                tuple(
                    _binding_child_part_v02(
                        "position", _binding_uint64_v02(index), child
                    )
                    for index, child in enumerate(children)
                ),
                recursively_immutable=(
                    type(value) is tuple
                    and all(child.recursively_immutable for child in children)
                ),
            )
        elif isinstance(value, Mapping):
            if any(type(key) is not str for key in value):
                raise ValueError("g2e5_compositional_binding_mapping_invalid")
            rows = tuple(
                (
                    key,
                    _compositional_binding_node_v02(value[key], memo, active),
                )
                for key in sorted(value)
            )
            node = _binding_node_v02(
                "mapping",
                tuple(
                    _binding_child_part_v02(
                        "key", key.encode("utf-8"), child
                    )
                    for key, child in rows
                ),
                recursively_immutable=False,
            )
        elif is_dataclass(value) and not isinstance(value, type):
            rows = tuple(
                (
                    field.name,
                    _compositional_binding_node_v02(
                        getattr(value, field.name), memo, active
                    ),
                )
                for field in fields(value)
            )
            node = _binding_node_v02(
                "dataclass",
                (
                    _qualified_type_name(value).encode("utf-8"),
                    *tuple(
                        _binding_child_part_v02(
                            "field", name.encode("utf-8"), child
                        )
                        for name, child in rows
                    ),
                ),
                recursively_immutable=bool(
                    params is not None
                    and params.frozen
                    and all(
                        child.recursively_immutable for _name, child in rows
                    )
                ),
            )
        else:
            raise ValueError(
                "g2e5_compositional_binding_type_unsupported:"
                + _qualified_type_name(value)
            )
    finally:
        if compound:
            active.remove(value_id)
    if memo is not None and potentially_cacheable and node.recursively_immutable:
        memo[cache_key] = (value, node)
    return node


def _compositional_binding_plain_v02(
    node: _CompositionalBindingNodeV02,
) -> dict[str, object]:
    return {
        "profile_id": COMPOSITIONAL_BINDING_PROFILE_V02,
        "sha256": node.sha256,
        "semantic_length": node.semantic_length,
    }


def _compositional_value_binding_v02(
    value: object,
    memo: dict[int, tuple[object, object]] | None = None,
) -> dict[str, object]:
    return _compositional_binding_plain_v02(
        _compositional_binding_node_v02(value, memo)
    )


def _compositional_call_binding_v02(
    validator: str,
    args: tuple[object, ...],
    kwargs: Mapping[str, object],
    memo: dict[int, tuple[object, object]] | None = None,
) -> dict[str, object]:
    if type(validator) is not str or not validator:
        raise ValueError("g2e5_compositional_binding_validator_invalid")
    if type(args) is not tuple or any(type(key) is not str for key in kwargs):
        raise ValueError("g2e5_compositional_binding_call_invalid")
    active: set[int] = set()
    positional = tuple(
        _compositional_binding_node_v02(value, memo, active) for value in args
    )
    keywords = tuple(
        (
            key,
            _compositional_binding_node_v02(kwargs[key], memo, active),
        )
        for key in sorted(kwargs)
    )
    node = _binding_node_v02(
        "call",
        (
            validator.encode("utf-8"),
            _binding_uint64_v02(len(positional)),
            *tuple(
                _binding_child_part_v02(
                    "argument", _binding_uint64_v02(index), child
                )
                for index, child in enumerate(positional)
            ),
            _binding_uint64_v02(len(keywords)),
            *tuple(
                _binding_child_part_v02(
                    "keyword", key.encode("utf-8"), child
                )
                for key, child in keywords
            ),
        ),
        recursively_immutable=False,
    )
    return _compositional_binding_plain_v02(node)


def _compositional_result_binding_v02(
    operation_result: _SemanticOperationResult,
    memo: dict[int, tuple[object, object]] | None = None,
) -> dict[str, object]:
    if operation_result.kind == "value_error":
        if type(operation_result.value) is not str:
            raise ValueError("g2e5_compositional_binding_result_invalid")
        child = _compositional_binding_node_v02(operation_result.value, memo)
        tag = "result:value_error"
    elif operation_result.kind == "return":
        child = _compositional_binding_node_v02(operation_result.value, memo)
        tag = "result:return"
    else:
        raise ValueError("g2e5_compositional_binding_result_invalid")
    return _compositional_binding_plain_v02(
        _binding_node_v02(
            tag,
            (_binding_child_part_v02("value", b"value", child),),
            recursively_immutable=False,
        )
    )


def _semantic_projection_build(
    value: object,
    memo: dict[int, tuple[object, dict[str, object]]] | None,
) -> tuple[dict[str, object], bool]:
    potentially_cacheable = type(value) is tuple or (
        is_dataclass(value) and not isinstance(value, type)
    )
    if memo is not None and potentially_cacheable:
        cached = memo.get(id(value))
        if cached is not None and cached[0] is value:
            return cached[1], True
    if value is None:
        result = {"kind": "none"}
        recursively_immutable = True
    elif type(value) is bool:
        result = {"kind": "bool", "value": value}
        recursively_immutable = True
    elif type(value) is int:
        result = {"kind": "int", "value": str(value)}
        recursively_immutable = True
    elif type(value) is float:
        if not math.isfinite(value):
            raise ValueError("g2e5_semantic_projection_float_invalid")
        result = {"kind": "float", "value": value.hex()}
        recursively_immutable = True
    elif type(value) is str:
        result = {"kind": "str", "value": value}
        recursively_immutable = True
    elif type(value) is bytes:
        result = {"kind": "bytes", "hex": value.hex()}
        recursively_immutable = True
    elif type(value) is tuple:
        rows = tuple(_semantic_projection_build(item, memo) for item in value)
        result = {"kind": "tuple", "items": [row[0] for row in rows]}
        recursively_immutable = all(row[1] for row in rows)
    elif type(value) is list:
        result = {
            "kind": "list",
            "items": [_semantic_projection_build(item, memo)[0] for item in value],
        }
        recursively_immutable = False
    elif isinstance(value, Mapping):
        if any(type(key) is not str for key in value):
            raise ValueError("g2e5_semantic_projection_mapping_invalid")
        result = {
            "kind": "mapping",
            "items": [
                [key, _semantic_projection_build(value[key], memo)[0]]
                for key in sorted(value)
            ],
        }
        recursively_immutable = False
    elif is_dataclass(value) and not isinstance(value, type):
        rows = tuple(
            (
                field.name,
                *_semantic_projection_build(getattr(value, field.name), memo),
            )
            for field in fields(value)
        )
        result = {
            "kind": "dataclass",
            "type": _qualified_type_name(value),
            "fields": [[name, projection] for name, projection, _safe in rows],
        }
        params = getattr(type(value), "__dataclass_params__", None)
        recursively_immutable = bool(
            params is not None
            and params.frozen
            and all(safe for _name, _projection, safe in rows)
        )
    else:
        raise ValueError(
            "g2e5_semantic_projection_type_unsupported:"
            + _qualified_type_name(value)
        )
    if memo is not None and potentially_cacheable and recursively_immutable:
        memo[id(value)] = (value, result)
    return result, recursively_immutable


def _semantic_projection(
    value: object,
    memo: dict[int, tuple[object, dict[str, object]]] | None = None,
) -> dict[str, object]:
    return _semantic_projection_build(value, memo)[0]


_DELTA_DEPENDENCY_EDGE_FIELDS = (
    "edge_id",
    "graph_basis_sha256",
    "graph_version",
    "dependent_artifact_id",
    "dependency_artifact_id",
    "dependency_field_pointers",
    "edge_class",
    "transaction_id",
    "owning_root_id",
    "domain_id",
    "canonical_order",
    "source_replay_edge_sha256",
    "trace_refs",
)
_DEPENDENCY_GRAPH_INDEX_FIELDS = (
    "graph_id",
    "graph_version",
    "graph_basis_sha256",
    "source_manifest_id",
    "source_manifest_hash",
    "source_replay_id",
    "transaction_id",
    "owning_root_id",
    "domain_id",
    "ordered_node_ids",
    "ordered_edge_ids",
    "node_count",
    "edge_count",
    "max_nodes",
    "max_edges",
    "max_hops",
    "acyclic",
    "source_history_hash",
    "policy_version",
    "schema_versions",
    "trace_refs",
)
_AFFECTED_SET_REQUEST_FIELDS = (
    "affected_request_id",
    "delta_id",
    "graph_id",
    "graph_version",
    "baseline_report_id",
    "transaction_id",
    "owning_root_id",
    "domain_id",
    "ordered_changed_field_binding_ids",
    "ordered_changed_artifact_binding_ids",
    "max_nodes",
    "max_edges",
    "max_hops",
    "trace_refs",
)
_WORLD_STATE_DELTA_FIELDS = (
    "delta_id",
    "delta_version",
    "delta_profile_id",
    "ordered_source_binding_ids",
    "request_id",
    "transaction_id",
    "owning_root_id",
    "domain_id",
    "baseline_report_id",
    "baseline_graph_id",
    "baseline_graph_version",
    "delta_sequence",
    "prior_delta_id",
    "observed_at_utc",
    "valid_from_utc",
    "valid_to_utc",
    "baseline_policy_version",
    "observed_policy_version",
    "baseline_schema_versions",
    "observed_schema_versions",
    "baseline_source_history_hash",
    "observed_source_history_hash",
    "ordered_changed_field_binding_ids",
    "ordered_changed_artifact_binding_ids",
    "dependency_fingerprint_before",
    "dependency_fingerprint_after",
    "trace_refs",
    "authority_created",
    "permission_created",
    "action_commit_packet_created",
    "receipt_created",
    "final_output_created",
    "drs_write_created",
    "real_world_effects_count",
)
_AFFECTED_SET_RESULT_FIELDS = (
    "affected_set_id",
    "affected_request_id",
    "delta_id",
    "graph_id",
    "graph_version",
    "ordered_changed_node_ids",
    "ordered_directly_affected_ids",
    "ordered_transitively_affected_ids",
    "ordered_affected_ids",
    "ordered_unaffected_ids",
    "closure_proof_sha256",
    "visited_node_count",
    "traversed_edge_count",
    "maximum_observed_hops",
    "complete",
    "minimal",
    "trace_refs",
)
_KERNEL_ARTIFACT_PLAIN_FIELDS = (
    "abi_version",
    "artifact_id",
    "artifact_type",
    "schema_version",
    "transaction_id",
    "owner_root_id",
    "source_component",
    "authority_class",
    "lifecycle_state",
    "payload",
    "trace_refs",
    "parent_refs",
    "time_envelope",
)


def _semantic_projection_to_plain(value: object) -> object:
    if type(value) is not dict or type(value.get("kind")) is not str:
        raise ValueError("g2e5_semantic_projection_invalid")
    kind = value["kind"]
    if kind == "none" and set(value) == {"kind"}:
        result: object = None
    elif kind == "bool" and set(value) == {"kind", "value"}:
        if type(value["value"]) is not bool:
            raise ValueError("g2e5_semantic_projection_invalid")
        result = value["value"]
    elif kind == "int" and set(value) == {"kind", "value"}:
        if type(value["value"]) is not str:
            raise ValueError("g2e5_semantic_projection_invalid")
        result = int(value["value"])
    elif kind == "float" and set(value) == {"kind", "value"}:
        if type(value["value"]) is not str:
            raise ValueError("g2e5_semantic_projection_invalid")
        result = float.fromhex(value["value"])
        if not math.isfinite(result):
            raise ValueError("g2e5_semantic_projection_invalid")
    elif kind == "str" and set(value) == {"kind", "value"}:
        if type(value["value"]) is not str:
            raise ValueError("g2e5_semantic_projection_invalid")
        result = value["value"]
    elif kind == "bytes" and set(value) == {"kind", "hex"}:
        if type(value["hex"]) is not str:
            raise ValueError("g2e5_semantic_projection_invalid")
        result = bytes.fromhex(value["hex"])
    elif kind in {"tuple", "list"} and set(value) == {"kind", "items"}:
        if type(value["items"]) is not list:
            raise ValueError("g2e5_semantic_projection_invalid")
        items = tuple(
            _semantic_projection_to_plain(item) for item in value["items"]
        )
        result = items if kind == "tuple" else list(items)
    elif kind == "mapping" and set(value) == {"kind", "items"}:
        rows = value["items"]
        if (
            type(rows) is not list
            or any(
                type(row) is not list
                or len(row) != 2
                or type(row[0]) is not str
                for row in rows
            )
            or [row[0] for row in rows] != sorted(row[0] for row in rows)
            or len({row[0] for row in rows}) != len(rows)
        ):
            raise ValueError("g2e5_semantic_projection_invalid")
        result = {
            row[0]: _semantic_projection_to_plain(row[1]) for row in rows
        }
    else:
        raise ValueError("g2e5_semantic_projection_invalid")
    if _semantic_projection(result) != value:
        raise ValueError("g2e5_semantic_projection_noncanonical")
    return result


def _semantic_projection_document_canonical_v01(value: object) -> bool:
    if type(value) is not dict or type(value.get("kind")) is not str:
        return False
    kind = value["kind"]
    if kind == "dataclass":
        if (
            set(value) != {"kind", "type", "fields"}
            or type(value.get("type")) is not str
            or not value["type"]
            or type(value.get("fields")) is not list
        ):
            return False
        rows = value["fields"]
        return (
            all(
                type(row) is list
                and len(row) == 2
                and type(row[0]) is str
                and row[0]
                and _semantic_projection_document_canonical_v01(row[1])
                for row in rows
            )
            and len({row[0] for row in rows}) == len(rows)
        )
    if kind in {"tuple", "list"}:
        return (
            set(value) == {"kind", "items"}
            and type(value.get("items")) is list
            and all(
                _semantic_projection_document_canonical_v01(item)
                for item in value["items"]
            )
        )
    if kind == "mapping":
        rows = value.get("items")
        return (
            set(value) == {"kind", "items"}
            and type(rows) is list
            and all(
                type(row) is list
                and len(row) == 2
                and type(row[0]) is str
                and _semantic_projection_document_canonical_v01(row[1])
                for row in rows
            )
            and [row[0] for row in rows] == sorted(row[0] for row in rows)
            and len({row[0] for row in rows}) == len(rows)
        )
    try:
        plain = _semantic_projection_to_plain(value)
    except (TypeError, ValueError, UnicodeError):
        return False
    return _semantic_projection(plain) == value


def _projected_dataclass_plain(
    value: object,
    *,
    expected_type: str,
    expected_fields: tuple[str, ...],
) -> dict[str, object]:
    if (
        type(value) is not dict
        or set(value) != {"kind", "type", "fields"}
        or value.get("kind") != "dataclass"
        or value.get("type") != expected_type
        or type(value.get("fields")) is not list
    ):
        raise ValueError("g2e5_semantic_projection_invalid")
    rows = value["fields"]
    if (
        any(
            type(row) is not list
            or len(row) != 2
            or type(row[0]) is not str
            for row in rows
        )
        or tuple(row[0] for row in rows) != expected_fields
    ):
        raise ValueError("g2e5_semantic_projection_invalid")
    return {
        row[0]: _semantic_projection_to_plain(row[1]) for row in rows
    }


def _framed_semantic_sha256(domain: str, value: object) -> str:
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    return hashlib.sha256(domain.encode("ascii") + b"\x00" + payload).hexdigest()


def _semantic_projection_bytes(
    value: object,
    memo: dict[int, tuple[object, dict[str, object]]] | None = None,
) -> bytes:
    return json.dumps(
        _semantic_projection(value, memo),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")


def _semantic_return_binding(
    value: object,
    memo: dict[int, tuple[object, dict[str, object]]] | None = None,
) -> dict[str, object]:
    payload = _semantic_projection_bytes(value, memo)
    return {
        "sha256": hashlib.sha256(payload).hexdigest(),
        "byte_length": len(payload),
    }


def _semantic_return_witness(
    value: object,
    memo: dict[int, tuple[object, dict[str, object]]] | None = None,
) -> dict[str, object]:
    projection = _semantic_projection(value, memo)
    payload = json.dumps(
        projection,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("ascii")
    return {
        "semantic_projection": projection,
        "sha256": hashlib.sha256(payload).hexdigest(),
        "byte_length": len(payload),
    }


_CASE53_SUBCASE_ID = (
    "g2e_case:negative:repeated_delta_spin:v01:subcase:repeated_delta_spin"
)
_CASE53_GRAPH_PROJECTION_WITNESS_FIELD = (
    "case53_graph_projection_return_witness"
)


def _semantic_return_witness_valid_v01(witness: object) -> bool:
    if type(witness) is not dict or set(witness) != {
        "semantic_projection",
        "sha256",
        "byte_length",
    }:
        return False
    try:
        payload = json.dumps(
            witness["semantic_projection"],
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("ascii")
    except (TypeError, UnicodeEncodeError):
        return False
    return (
        _semantic_projection_document_canonical_v01(
            witness["semantic_projection"]
        )
        and type(witness["sha256"]) is str
        and witness["sha256"] == hashlib.sha256(payload).hexdigest()
        and type(witness["byte_length"]) is int
        and witness["byte_length"] == len(payload)
        and witness["byte_length"] > 0
    )


def _case53_graph_projection_witness_evidence_valid_v01(
    subcase_id: str,
    material: object,
) -> bool:
    if type(material) is not dict:
        return False
    witness_present = _CASE53_GRAPH_PROJECTION_WITNESS_FIELD in material
    if subcase_id == _CASE53_SUBCASE_ID:
        return witness_present and _semantic_return_witness_valid_v01(
            material[_CASE53_GRAPH_PROJECTION_WITNESS_FIELD]
        )
    return not witness_present


@dataclass(frozen=True)
class _SemanticOperationResult:
    kind: str
    value: object


@dataclass(frozen=True)
class _NegativeConstructibilityObservationV01:
    case_id: str
    subcase_name: str
    mutated_axis: str
    validation_target: str
    validator_name: str
    mutated_argument_locator: str
    mutated_carrier_type: str
    expected_reason_codes: tuple[str, ...]
    observed_reason_codes: tuple[str, ...]
    operation_result_kind: str


def _observed_negative_subcase(
    *,
    case_id: str,
    subcase_name: str,
    axis: str,
    expected_reason: str | tuple[str, ...],
    validation_target: str,
    validator_name: str,
    mutated_carrier: object,
    validation_result: object,
    resealed_outer_ids: tuple[str, ...] = (),
    semantic_args: tuple[object, ...] | None = None,
    semantic_kwargs: dict[str, object] | None = None,
    mutated_argument_locator: str = "arg:0",
    semantic_operation_result: object | None = None,
    semantic_metadata: dict[str, object] | None = None,
    semantic_projection_memo: (
        dict[int, tuple[object, dict[str, object]]] | None
    ) = None,
    constructibility_only: bool = False,
) -> (
    ContinuousDeltaRuntimeG2ESubcaseResultV01
    | _NegativeConstructibilityObservationV01
):
    call_args = (mutated_carrier,) if semantic_args is None else semantic_args
    call_kwargs = {} if semantic_kwargs is None else semantic_kwargs
    if mutated_argument_locator.startswith("arg:"):
        try:
            mutated_argument = call_args[int(mutated_argument_locator[4:])]
        except (ValueError, IndexError):
            raise ValueError("g2e5_mutated_argument_locator_invalid") from None
    elif mutated_argument_locator.startswith("kw:"):
        keyword = mutated_argument_locator[3:]
        if keyword not in call_kwargs:
            raise ValueError("g2e5_mutated_argument_locator_invalid")
        mutated_argument = call_kwargs[keyword]
    else:
        raise ValueError("g2e5_mutated_argument_locator_invalid")
    raw_operation_result = (
        validation_result
        if semantic_operation_result is None
        else semantic_operation_result
    )
    operation_result = (
        raw_operation_result
        if type(raw_operation_result) is _SemanticOperationResult
        else _SemanticOperationResult("return", raw_operation_result)
    )
    result_value = operation_result.value
    if operation_result.kind == "value_error":
        if type(result_value) is not str:
            raise ValueError("g2e5_semantic_value_error_invalid")
        semantic_result_payload = {
            "kind": "value_error",
            "reason": result_value,
        }
    elif operation_result.kind == "return":
        semantic_result_payload = None
    else:
        raise ValueError("g2e5_semantic_result_kind_invalid")
    reason_result = (
        validation_result
        if type(validation_result) is _SemanticOperationResult
        else _SemanticOperationResult("return", validation_result)
    )
    reason_value = (
        (reason_result.value,)
        if reason_result.kind == "value_error"
        else reason_result.value
    )
    if type(reason_value) is g2e.ContinuousDeltaValidationReportV01:
        observed_reasons = reason_value.reason_codes
        validation_report_id = reason_value.validation_report_id
        carrier_validation = g2e.validate_continuous_delta_validation_report_v01(
            reason_value
        )
        _require_public_pass(
            carrier_validation, "g2e5_returned_validation_report_invalid"
        )
        evidence_refs = (
            validation_report_id,
            carrier_validation.validation_report_id,
            *resealed_outer_ids,
        )
    elif type(reason_value) is tuple and all(
        type(item) is str for item in reason_value
    ):
        observed_reasons = reason_value
        validation_report_id = _prefixed_identity(
            "g2e5_validation_tuple_v01:",
            "HEDGEHOG_G2E5_VALIDATION_TUPLE_V01",
            {
                "validator": validator_name,
                "carrier_id": _carrier_identity(mutated_carrier),
                "reason_codes": list(observed_reasons),
            },
        )
        evidence_refs = (validation_report_id, *resealed_outer_ids)
    else:
        raise ValueError("g2e5_negative_validator_result_invalid")
    expected_reasons = _reason_tuple(expected_reason)
    if observed_reasons != expected_reasons:
        raise ValueError(
            "g2e5_negative_reason_mismatch:"
            + subcase_name
            + ":"
            + ",".join(observed_reasons)
        )
    if constructibility_only:
        return _NegativeConstructibilityObservationV01(
            case_id=case_id,
            subcase_name=subcase_name,
            mutated_axis=axis,
            validation_target=validation_target,
            validator_name=validator_name,
            mutated_argument_locator=mutated_argument_locator,
            mutated_carrier_type=_qualified_type_name(mutated_argument),
            expected_reason_codes=expected_reasons,
            observed_reason_codes=observed_reasons,
            operation_result_kind=operation_result.kind,
        )
    compositional_memo = semantic_projection_memo
    semantic_call_binding = _compositional_call_binding_v02(
        validator_name,
        call_args,
        call_kwargs,
        compositional_memo,
    )
    mutated_carrier_binding = _compositional_value_binding_v02(
        mutated_argument, compositional_memo
    )
    semantic_result_binding = _compositional_result_binding_v02(
        operation_result, compositional_memo
    )
    mutated_carrier_id = "NONE"
    if is_dataclass(mutated_argument) and not isinstance(mutated_argument, type):
        for field in fields(mutated_argument):
            candidate_id = getattr(mutated_argument, field.name)
            if (
                field.name.endswith("_id")
                and type(candidate_id) is str
                and candidate_id
            ):
                mutated_carrier_id = candidate_id
                break
    evidence = {
        "case_id": case_id,
        "subcase_id": subcase_name,
        "mutated_axis": axis,
        "mutated_carrier_type": _qualified_type_name(mutated_argument),
        "mutated_carrier_id": mutated_carrier_id,
        "mutated_argument_locator": mutated_argument_locator,
        "compositional_binding_profile_id": (
            COMPOSITIONAL_BINDING_PROFILE_V02
        ),
        "mutated_carrier_sha256": mutated_carrier_binding["sha256"],
        "mutated_carrier_semantic_length": mutated_carrier_binding[
            "semantic_length"
        ],
        "public_semantic_validator": validator_name,
        "semantic_call_fingerprint": semantic_call_binding["sha256"],
        "semantic_call_semantic_length": semantic_call_binding[
            "semantic_length"
        ],
        "semantic_result_sha256": semantic_result_binding["sha256"],
        "semantic_result_semantic_length": semantic_result_binding[
            "semantic_length"
        ],
        "returned_reason_codes": list(observed_reasons),
        "returned_validation_report_id": (
            reason_value.validation_report_id
            if type(reason_value) is g2e.ContinuousDeltaValidationReportV01
            else None
        ),
        "validation_result_evidence_id": validation_report_id,
        "resealed_outer_ids": list(resealed_outer_ids),
        "caller_supplied_rejection_report": False,
        **({} if semantic_metadata is None else semantic_metadata),
    }
    evidence_json = _canonical_json_text(evidence)
    return ContinuousDeltaRuntimeG2ESubcaseResultV01(
        subcase_id=f"{case_id}:subcase:{subcase_name}",
        mutated_axis=axis,
        validation_target=validation_target,
        expected_reason_codes=expected_reasons,
        observed_reason_codes=observed_reasons,
        validation_report_id=validation_report_id,
        evidence_refs=evidence_refs,
        evidence_material_json=evidence_json,
        evidence_sha256=_sha256_domain(
            SUBCASE_EVIDENCE_DOMAIN, json.loads(evidence_json)
        ),
        final_status="PASS",
    )


def _bundle_values(
    bundle: g2e.ContinuousDeltaExecutionBundleV01,
) -> dict[str, object]:
    return {field.name: getattr(bundle, field.name) for field in fields(bundle)}


def _reseal_kernel_artifact(
    artifact: g2e.KernelArtifactV01,
    *,
    label: str,
    **changes: object,
) -> g2e.KernelArtifactV01:
    plain = kernel_artifact_to_plain_dict_v01(artifact)
    material = {
        field_name: changes.get(field_name, plain[field_name])
        for field_name in (
            "abi_version",
            "artifact_type",
            "schema_version",
            "transaction_id",
            "owner_root_id",
            "source_component",
            "authority_class",
            "lifecycle_state",
            "payload",
            "trace_refs",
            "parent_refs",
            "time_envelope",
        )
    }
    prefix = artifact.artifact_id.split(":", 1)[0] + ":"
    artifact_id = prefix + g2e.domain_separated_sha256_hex_v01(
        domain="HEDGEHOG_G2E5_RESEALED_ARTIFACT_V01:" + label,
        payload=canonical_json_bytes_v01(material),
    )
    return build_kernel_artifact_v01(
        abi_version=str(material["abi_version"]),
        artifact_id=artifact_id,
        artifact_type=str(material["artifact_type"]),
        schema_version=str(material["schema_version"]),
        transaction_id=str(material["transaction_id"]),
        owner_root_id=str(material["owner_root_id"]),
        source_component=str(material["source_component"]),
        authority_class=str(material["authority_class"]),
        lifecycle_state=str(material["lifecycle_state"]),
        payload=material["payload"],
        trace_refs=tuple(material["trace_refs"]),
        parent_refs=tuple(material["parent_refs"]),
        time_envelope=material["time_envelope"],
    )


def _root_decision_artifact(
    *,
    phase: str,
    result: root_decision.RootDecisionResultV01,
    parent_refs: tuple[str, ...],
    trace_refs: tuple[str, ...],
    time_source_artifact: g2e.KernelArtifactV01,
) -> g2e.KernelArtifactV01:
    result_plain = root_decision.root_decision_result_to_plain_dict_v01(result)
    payload = {key: value for key, value in result_plain.items() if key != "transaction_id"}
    prefix = (
        "g2e_root_plan_decision_v01:"
        if phase == "PLAN"
        else "g2e_root_final_decision_v01:"
    )
    domain = (
        "HEDGEHOG_G2E_PLAN_ROOT_DECISION_ARTIFACT_V01"
        if phase == "PLAN"
        else "HEDGEHOG_G2E_FINAL_ROOT_DECISION_ARTIFACT_V01"
    )
    time_envelope = kernel_artifact_to_plain_dict_v01(time_source_artifact)[
        "time_envelope"
    ]
    material = {
        "abi_version": "v1.0",
        "artifact_type": "RootDecision",
        "schema_version": "v0.1",
        "transaction_id": result.transaction_id,
        "owner_root_id": result.target_root_id,
        "source_component": "root_decision_v01",
        "authority_class": "ROOT_OWNED",
        "lifecycle_state": "ROOT_REVIEWED",
        "payload": payload,
        "trace_refs": list(trace_refs),
        "parent_refs": list(parent_refs),
        "time_envelope": time_envelope,
    }
    return build_kernel_artifact_v01(
        abi_version="v1.0",
        artifact_id=prefix + g2e.domain_separated_sha256_hex_v01(
            domain=domain,
            payload=canonical_json_bytes_v01(material),
        ),
        artifact_type="RootDecision",
        schema_version="v0.1",
        transaction_id=result.transaction_id,
        owner_root_id=result.target_root_id,
        source_component="root_decision_v01",
        authority_class="ROOT_OWNED",
        lifecycle_state="ROOT_REVIEWED",
        payload=payload,
        trace_refs=trace_refs,
        parent_refs=parent_refs,
        time_envelope=time_envelope,
    )


def _non_accept_final_bundle(
    bundle: g2e.ContinuousDeltaExecutionBundleV01,
    *,
    non_accept_axis: str = "permission",
) -> g2e.ContinuousDeltaExecutionBundleV01:
    final_plain = root_decision.root_decision_input_to_plain_dict_v01(
        bundle.final_root_decision_input
    )
    permission_state = dict(final_plain["permission_state"])
    conflict_state = dict(final_plain["conflict_state"])
    if non_accept_axis == "permission":
        permission_state.update(
            {
                "permission_required": True,
                "user_permission_present": False,
                "permission_ref": None,
            }
        )
    elif non_accept_axis == "conflict":
        conflict_state["material_unresolved_conflict"] = True
    else:
        raise ValueError("g2e5_non_accept_final_axis_invalid")
    non_accept_input = root_decision.build_root_decision_input_v01(
        transaction_id=bundle.final_root_decision_input.transaction_id,
        target_root_id=bundle.final_root_decision_input.target_root_id,
        root_review_packet=bundle.final_root_decision_input.root_review_packet,
        post_vv_bundle=final_plain["post_vv_bundle"],
        gt_advisory=final_plain["gt_advisory"],
        policy_state=final_plain["policy_state"],
        permission_state=permission_state,
        temporal_state=final_plain["temporal_state"],
        conflict_state=conflict_state,
        prior_root_state=final_plain["prior_root_state"],
    )
    non_accept_result = root_decision.decide_root_v01(
        kernel=bundle.source_context.root_kernel,
        decision_input=non_accept_input,
    )
    if non_accept_result.decision == "ACCEPT":
        raise ValueError("g2e5_non_accept_root_probe_invalid")
    non_accept_artifact = _root_decision_artifact(
        phase="FINAL",
        result=non_accept_result,
        parent_refs=bundle.final_root_decision_artifact.parent_refs,
        trace_refs=(
            non_accept_input.decision_input_id,
            non_accept_input.root_review_packet.packet_id,
            *bundle.final_root_decision_artifact.trace_refs[2:],
        ),
        time_source_artifact=bundle.recomputed_g2d_execution_bundle.report_artifact,
    )
    return replace(
        bundle,
        final_root_decision_input=non_accept_input,
        final_root_decision_result=non_accept_result,
        final_root_decision_artifact=non_accept_artifact,
    )


def _non_accept_plan_bundle(
    bundle: g2e.ContinuousDeltaExecutionBundleV01,
) -> g2e.ContinuousDeltaExecutionBundleV01:
    plan_plain = root_decision.root_decision_input_to_plain_dict_v01(
        bundle.plan_root_decision_input
    )
    permission_state = dict(plan_plain["permission_state"])
    permission_state.update(
        {
            "permission_required": True,
            "user_permission_present": False,
            "permission_ref": None,
        }
    )
    non_accept_input = root_decision.build_root_decision_input_v01(
        transaction_id=bundle.plan_root_decision_input.transaction_id,
        target_root_id=bundle.plan_root_decision_input.target_root_id,
        root_review_packet=bundle.plan_root_decision_input.root_review_packet,
        post_vv_bundle=plan_plain["post_vv_bundle"],
        gt_advisory=plan_plain["gt_advisory"],
        policy_state=plan_plain["policy_state"],
        permission_state=permission_state,
        temporal_state=plan_plain["temporal_state"],
        conflict_state=plan_plain["conflict_state"],
        prior_root_state=plan_plain["prior_root_state"],
    )
    non_accept_result = root_decision.decide_root_v01(
        kernel=bundle.source_context.root_kernel,
        decision_input=non_accept_input,
    )
    if non_accept_result.decision == "ACCEPT":
        raise ValueError("g2e5_non_accept_plan_root_probe_invalid")
    non_accept_artifact = _root_decision_artifact(
        phase="PLAN",
        result=non_accept_result,
        parent_refs=bundle.plan_root_decision_artifact.parent_refs,
        trace_refs=(
            non_accept_input.decision_input_id,
            non_accept_input.root_review_packet.packet_id,
            *bundle.plan_root_decision_artifact.trace_refs[2:],
        ),
        time_source_artifact=bundle.plan_proposed_artifact,
    )
    return replace(
        bundle,
        plan_root_decision_input=non_accept_input,
        plan_root_decision_result=non_accept_result,
        plan_root_decision_artifact=non_accept_artifact,
    )


def _root_input_with_prior_decision_mutation(
    value: root_decision.RootDecisionInputV01,
) -> root_decision.RootDecisionInputV01:
    plain = root_decision.root_decision_input_to_plain_dict_v01(value)
    prior_root_state = dict(plain["prior_root_state"])
    prior_root_state["prior_decision_id"] = "root_decision:g2e5:foreign"
    return root_decision.build_root_decision_input_v01(
        transaction_id=value.transaction_id,
        target_root_id=value.target_root_id,
        root_review_packet=value.root_review_packet,
        post_vv_bundle=plain["post_vv_bundle"],
        gt_advisory=plain["gt_advisory"],
        policy_state=plain["policy_state"],
        permission_state=plain["permission_state"],
        temporal_state=plain["temporal_state"],
        conflict_state=plain["conflict_state"],
        prior_root_state=prior_root_state,
    )


def _coherent_bundle_artifact_mutation(
    bundle: g2e.ContinuousDeltaExecutionBundleV01,
    *,
    field_name: str,
    artifact: g2e.KernelArtifactV01,
) -> tuple[g2e.ContinuousDeltaExecutionBundleV01, tuple[str, ...]]:
    chain_fields = (
        "delta_source_proposed_artifact",
        "delta_source_artifact",
        "dependency_graph_artifact",
        "affected_set_artifact",
        "invalidation_report_artifact",
        "plan_proposed_artifact",
        "plan_root_decision_artifact",
        "plan_accepted_artifact",
        "preservation_proof_artifact",
        "final_root_decision_artifact",
        "runtime_report_artifact",
    )
    changed_index = chain_fields.index(field_name)
    replacements: dict[str, object] = {field_name: artifact}
    identity_map = {getattr(bundle, field_name).artifact_id: artifact.artifact_id}
    resealed_ids = [artifact.artifact_id]
    for downstream_field in chain_fields[changed_index + 1 :]:
        original = getattr(bundle, downstream_field)
        if downstream_field == "plan_root_decision_artifact":
            plan_artifact = replacements.get(
                "plan_proposed_artifact", bundle.plan_proposed_artifact
            )
            assert type(plan_artifact) is g2e.KernelArtifactV01
            updated = _root_decision_artifact(
                phase="PLAN",
                result=bundle.plan_root_decision_result,
                parent_refs=(
                    plan_artifact.artifact_id,
                    bundle.source_context.baseline_g2c_route_eligibility_artifact.artifact_id,
                    bundle.source_context.baseline_g2d_execution_bundle.report_artifact.artifact_id,
                ),
                trace_refs=tuple(
                    identity_map.get(ref, ref) for ref in original.trace_refs
                ),
                time_source_artifact=plan_artifact,
            )
        elif downstream_field == "final_root_decision_artifact":
            plan_root = replacements.get(
                "plan_root_decision_artifact", bundle.plan_root_decision_artifact
            )
            accepted = replacements.get(
                "plan_accepted_artifact", bundle.plan_accepted_artifact
            )
            preservation = replacements.get(
                "preservation_proof_artifact", bundle.preservation_proof_artifact
            )
            assert type(plan_root) is g2e.KernelArtifactV01
            assert type(accepted) is g2e.KernelArtifactV01
            assert type(preservation) is g2e.KernelArtifactV01
            updated = _root_decision_artifact(
                phase="FINAL",
                result=bundle.final_root_decision_result,
                parent_refs=(
                    plan_root.artifact_id,
                    accepted.artifact_id,
                    bundle.recomputed_g2d_execution_bundle.report_artifact.artifact_id,
                    preservation.artifact_id,
                ),
                trace_refs=tuple(
                    identity_map.get(ref, ref) for ref in original.trace_refs
                ),
                time_source_artifact=(
                    bundle.recomputed_g2d_execution_bundle.report_artifact
                ),
            )
        else:
            parents = tuple(
                identity_map.get(ref, ref) for ref in original.parent_refs
            )
            traces = tuple(identity_map.get(ref, ref) for ref in original.trace_refs)
            if parents == original.parent_refs and traces == original.trace_refs:
                continue
            updated = _reseal_kernel_artifact(
                original,
                label=field_name + ":outer:" + downstream_field,
                parent_refs=parents,
                trace_refs=traces,
            )
        replacements[downstream_field] = updated
        identity_map[original.artifact_id] = updated.artifact_id
        resealed_ids.append(updated.artifact_id)
    return replace(bundle, **replacements), tuple(resealed_ids)


def _reseal_public_carrier(value: object, **changes: object) -> object:
    profiles = {
        g2e.DeltaSourceBindingV01: (
            "source_binding_id",
            g2e.rebuild_delta_source_binding_identity_v01,
        ),
        g2e.ChangedFieldBindingV01: (
            "changed_field_binding_id",
            g2e.rebuild_changed_field_binding_identity_v01,
        ),
        g2e.ChangedArtifactBindingV01: (
            "changed_artifact_binding_id",
            g2e.rebuild_changed_artifact_binding_identity_v01,
        ),
        g2e.WorldStateDeltaV01: (
            "delta_id",
            g2e.rebuild_world_state_delta_identity_v01,
        ),
        g2e.DependencyFingerprintProfileV01: (
            "fingerprint_profile_id",
            g2e.rebuild_dependency_fingerprint_profile_identity_v01,
        ),
        g2e.DeltaDependencyEdgeV01: (
            "edge_id",
            g2e.rebuild_delta_dependency_edge_identity_v01,
        ),
        g2e.DependencyGraphIndexV01: (
            "graph_id",
            g2e.rebuild_dependency_graph_index_identity_v01,
        ),
        g2e.AffectedSetRequestV01: (
            "affected_request_id",
            g2e.rebuild_affected_set_request_identity_v01,
        ),
        g2e.AffectedSetResultV01: (
            "affected_set_id",
            g2e.rebuild_affected_set_result_identity_v01,
        ),
        g2e.ArtifactInvalidationRecordV01: (
            "invalidation_record_id",
            g2e.rebuild_artifact_invalidation_record_identity_v01,
        ),
        g2e.InvalidationReportV01: (
            "invalidation_report_id",
            g2e.rebuild_invalidation_report_identity_v01,
        ),
        g2e.PreservationProofV01: (
            "preservation_proof_id",
            g2e.rebuild_preservation_proof_identity_v01,
        ),
        g2e.SelectiveRecomputationPlanV01: (
            "recomputation_plan_id",
            g2e.rebuild_selective_recomputation_plan_identity_v01,
        ),
        g2e.RecomputedArtifactBindingV01: (
            "recomputed_binding_id",
            g2e.rebuild_recomputed_artifact_binding_identity_v01,
        ),
        g2e.SelectiveRecomputationResultV01: (
            "recomputation_result_id",
            g2e.rebuild_selective_recomputation_result_identity_v01,
        ),
        g2e.ContinuousDeltaRuntimeTraceV01: (
            "trace_id",
            g2e.rebuild_continuous_delta_runtime_trace_identity_v01,
        ),
        g2e.ContinuousDeltaRuntimeReportV01: (
            "report_id",
            g2e.rebuild_continuous_delta_runtime_report_identity_v01,
        ),
        g2e.ContinuousDeltaValidationReportV01: (
            "validation_report_id",
            g2e.rebuild_continuous_delta_validation_report_identity_v01,
        ),
    }
    profile = profiles.get(type(value))
    if profile is None:
        raise ValueError("g2e5_reseal_type_unsupported")
    identity_field, rebuilder = profile
    candidate = replace(value, **changes)
    return replace(candidate, **{identity_field: rebuilder(candidate)})


def _reseal_preservation_proof(
    value: g2e.PreservationProofV01,
    **changes: object,
) -> g2e.PreservationProofV01:
    candidate = replace(value, **changes)
    material = tuple(
        (field.name, _plain_data(getattr(candidate, field.name)))
        for field in fields(candidate)
        if field.name not in {"preservation_proof_id", "proof_sha256"}
    )
    proof_sha256 = hashlib.sha256(
        b"HEDGEHOG_G2E_PRESERVATION_PROOF_V01"
        + b"\x00"
        + canonical_json_bytes_v01(material)
    ).hexdigest()
    candidate = replace(candidate, proof_sha256=proof_sha256)
    return replace(
        candidate,
        preservation_proof_id=(
            g2e.rebuild_preservation_proof_identity_v01(candidate)
        ),
    )


def _public_operation_result(operation: object) -> object:
    try:
        return _SemanticOperationResult("return", operation())
    except ValueError as exc:
        if len(exc.args) == 1 and type(exc.args[0]) is str:
            return _SemanticOperationResult("value_error", exc.args[0])
        raise


def _affected_context_kwargs(
    inputs: dict[str, object], **changes: object
) -> dict[str, object]:
    values = {
        "request": inputs["request"],
        "delta": inputs["delta"],
        "graph": inputs["graph"],
        "source_bindings": (inputs["source_binding"],),
        "changed_field_bindings": (inputs["changed_field"],),
        "changed_artifact_bindings": (inputs["changed_artifact"],),
        "dependency_edges": inputs["dependency_edges"],
        "baseline_source_artifacts": inputs["baseline"],
        "observed_source_artifacts": inputs["observed"],
    }
    values.update(changes)
    return values


def _hop_bound_context_kwargs(
    inputs: dict[str, object],
) -> dict[str, object]:
    source_graph = inputs["graph"]
    transaction_id = source_graph.transaction_id
    root_id = source_graph.owning_root_id
    domain_id = source_graph.domain_id
    node_count = g2e.MAX_AFFECTED_HOPS_V01 + 2
    baseline = tuple(
        _kernel_artifact(
            artifact_id=f"artifact:g2e5:hop-bound:{index:02d}",
            transaction_id=transaction_id,
            root_id=root_id,
            payload={"index": index, "value": "baseline"},
        )
        for index in range(node_count)
    )
    observed_source = _kernel_artifact(
        artifact_id="artifact:g2e5:hop-bound:observed",
        transaction_id=transaction_id,
        root_id=root_id,
        payload={"index": 0, "value": "observed"},
        parent_refs=(baseline[0].artifact_id,),
    )
    observed = (observed_source, *baseline[1:])
    replay_edges = tuple(
        ArtifactDependencyEdgeV01(
            artifact_id=baseline[index].artifact_id,
            depends_on_artifact_id=baseline[index - 1].artifact_id,
        )
        for index in range(1, node_count)
    )
    manifest = build_artifact_manifest_v01(
        transaction_id=transaction_id,
        profile=build_default_seal_profile_v01(),
        artifacts=tuple(
            kernel_artifact_to_canonical_ref_v01(item) for item in baseline
        ),
        dependency_edges=replay_edges,
        root_ownership_bindings=tuple(
            RootOwnershipBindingV01(item.artifact_id, root_id)
            for item in baseline
        ),
        evidence_class_bindings=tuple(
            EvidenceClassBindingV01(item.artifact_id, "SOURCE_EVIDENCE")
            for item in baseline
        ),
        authority_class_bindings=tuple(
            AuthorityClassBindingV01(item.artifact_id, item.authority_class)
            for item in baseline
        ),
    )
    replay = verify_artifact_replay_v01(
        manifest=manifest,
        payload_rows=tuple(
            (
                item.artifact_id,
                kernel_artifact_to_plain_dict_v01(item)["payload"],
            )
            for item in baseline
        ),
        expected_manifest_hash=manifest.manifest_hash,
    )
    projection_result = g2e.project_integrity_replay_dependency_edges_v01(
        manifest=manifest,
        replay=replay,
        source_artifacts=baseline,
        graph_version=source_graph.graph_version,
        transaction_id=transaction_id,
        owning_root_id=root_id,
        domain_id=domain_id,
        policy_version=source_graph.policy_version,
        schema_versions=source_graph.schema_versions,
        source_history_hash=source_graph.source_history_hash,
        edge_projection_bindings=tuple(
            (
                edge.artifact_id,
                edge.depends_on_artifact_id,
                (),
                "ARTIFACT_DEPENDENCY",
            )
            for edge in replay_edges
        ),
    )
    graph_basis, dependency_edges = projection_result
    graph = g2e.build_dependency_graph_index_v01(
        graph_basis_sha256=graph_basis,
        graph_version=source_graph.graph_version,
        manifest=manifest,
        replay=replay,
        source_artifacts=baseline,
        dependency_edges=dependency_edges,
        transaction_id=transaction_id,
        owning_root_id=root_id,
        domain_id=domain_id,
        policy_version=source_graph.policy_version,
        schema_versions=source_graph.schema_versions,
        source_history_hash=source_graph.source_history_hash,
        trace_refs=(manifest.manifest_hash, replay.replay_id),
    )
    source_binding = _reseal_public_carrier(
        inputs["source_binding"],
        baseline_source_artifact_id=baseline[0].artifact_id,
        baseline_source_artifact_type=baseline[0].artifact_type,
        baseline_source_artifact_sha256=_artifact_sha256(baseline[0]),
        baseline_source_payload_sha256=_payload_sha256(baseline[0]),
        observed_source_artifact_id=observed_source.artifact_id,
        observed_source_artifact_type=observed_source.artifact_type,
        observed_source_artifact_sha256=_artifact_sha256(observed_source),
        observed_source_payload_sha256=_payload_sha256(observed_source),
        baseline_graph_id=graph.graph_id,
        baseline_graph_version=graph.graph_version,
    )
    changed_field = _reseal_public_carrier(
        inputs["changed_field"],
        source_binding_id=source_binding.source_binding_id,
        json_pointer="/payload/value",
        prior_value_sha256=_sha256_plain("baseline"),
        observed_value_sha256=_sha256_plain("observed"),
    )
    profile = g2e.build_dependency_fingerprint_profile_v01()
    before = g2e.build_dependency_fingerprint_v01(
        profile=profile,
        graph=graph,
        dependency_edges=dependency_edges,
        source_artifacts=baseline,
        policy_version=source_graph.policy_version,
        schema_versions=source_graph.schema_versions,
        source_history_hash=source_graph.source_history_hash,
    )
    after = g2e.build_dependency_fingerprint_v01(
        profile=profile,
        graph=graph,
        dependency_edges=dependency_edges,
        source_artifacts=observed,
        policy_version=source_graph.policy_version,
        schema_versions=source_graph.schema_versions,
        source_history_hash=source_graph.source_history_hash,
    )
    changed_artifact = _reseal_public_carrier(
        inputs["changed_artifact"],
        source_binding_id=source_binding.source_binding_id,
        baseline_artifact_id=baseline[0].artifact_id,
        baseline_artifact_type=baseline[0].artifact_type,
        baseline_payload_sha256=_payload_sha256(baseline[0]),
        observed_artifact_id=observed_source.artifact_id,
        observed_artifact_type=observed_source.artifact_type,
        observed_payload_sha256=_payload_sha256(observed_source),
        baseline_dependency_fingerprint=before,
        observed_dependency_fingerprint=after,
    )
    delta = _reseal_public_carrier(
        inputs["delta"],
        baseline_graph_id=graph.graph_id,
        baseline_graph_version=graph.graph_version,
        ordered_source_binding_ids=(source_binding.source_binding_id,),
        ordered_changed_field_binding_ids=(
            changed_field.changed_field_binding_id,
        ),
        ordered_changed_artifact_binding_ids=(
            changed_artifact.changed_artifact_binding_id,
        ),
        dependency_fingerprint_before=before,
        dependency_fingerprint_after=after,
    )
    request = g2e.build_affected_set_request_v01(
        delta=delta,
        graph=graph,
        trace_refs=(delta.delta_id, graph.graph_id),
    )
    return {
        "request": request,
        "delta": delta,
        "graph": graph,
        "source_bindings": (source_binding,),
        "changed_field_bindings": (changed_field,),
        "changed_artifact_bindings": (changed_artifact,),
        "dependency_edges": dependency_edges,
        "baseline_source_artifacts": baseline,
        "observed_source_artifacts": observed,
    }


def _invalidation_context_kwargs(
    inputs: dict[str, object], execution: dict[str, object], **changes: object
) -> dict[str, object]:
    values = {
        "records": execution["invalidation_records"],
        "affected_set": inputs["affected"],
        "delta": inputs["delta"],
        "source_context": inputs["context"],
        "source_bindings": (inputs["source_binding"],),
        "changed_field_bindings": (inputs["changed_field"],),
        "changed_artifact_bindings": (inputs["changed_artifact"],),
        "dependency_edges": inputs["dependency_edges"],
        "dependency_graph": inputs["graph"],
    }
    values.update(changes)
    return values


def _plan_context_kwargs(
    inputs: dict[str, object], execution: dict[str, object], **changes: object
) -> dict[str, object]:
    values = {
        "delta": inputs["delta"],
        "affected_set": inputs["affected"],
        "invalidation_records": execution["invalidation_records"],
        "invalidation_report": execution["invalidation_report"],
        "source_context": inputs["context"],
        "source_bindings": (inputs["source_binding"],),
        "changed_field_bindings": (inputs["changed_field"],),
        "changed_artifact_bindings": (inputs["changed_artifact"],),
        "dependency_edges": inputs["dependency_edges"],
        "dependency_graph": inputs["graph"],
    }
    values.update(changes)
    return values


def _result_context_kwargs(
    bundle: g2e.ContinuousDeltaExecutionBundleV01, **changes: object
) -> dict[str, object]:
    values = {
        "plan": bundle.recomputation_plan,
        "source_context": bundle.source_context,
        "delta_source_proposed_artifact": bundle.delta_source_proposed_artifact,
        "delta_source_artifact": bundle.delta_source_artifact,
        "dependency_graph_artifact": bundle.dependency_graph_artifact,
        "affected_set_artifact": bundle.affected_set_artifact,
        "invalidation_report_artifact": bundle.invalidation_report_artifact,
        "plan_proposed_artifact": bundle.plan_proposed_artifact,
        "plan_root_decision_input": bundle.plan_root_decision_input,
        "plan_root_decision_result": bundle.plan_root_decision_result,
        "plan_root_decision_artifact": bundle.plan_root_decision_artifact,
        "plan_accepted_artifact": bundle.plan_accepted_artifact,
        "recomputed_g2d_execution_bundle": bundle.recomputed_g2d_execution_bundle,
        "recomputed_bindings": bundle.recomputed_bindings,
        "preservation_proof": bundle.preservation_proof,
        "preservation_proof_artifact": bundle.preservation_proof_artifact,
        "g2e_transition_decisions": bundle.g2e_transition_decisions,
        "g2e_causal_consumption_refs": bundle.g2e_causal_consumption_refs,
    }
    values.update(changes)
    return values


def _edge_projection_rows(
    inputs: dict[str, object],
) -> tuple[tuple[str, str, tuple[str, ...], str], ...]:
    return tuple(
        (
            edge.dependent_artifact_id,
            edge.dependency_artifact_id,
            edge.dependency_field_pointers,
            edge.edge_class,
        )
        for edge in inputs["dependency_edges"]
    )


def _project_edge_mutation(
    inputs: dict[str, object],
    rows: tuple[tuple[str, str, tuple[str, ...], str], ...],
) -> tuple[object, dict[str, object]]:
    graph = inputs["graph"]
    call_kwargs = {
        "manifest": inputs["manifest"],
        "replay": inputs["replay"],
        "source_artifacts": inputs["baseline"],
        "graph_version": graph.graph_version,
        "transaction_id": graph.transaction_id,
        "owning_root_id": graph.owning_root_id,
        "domain_id": graph.domain_id,
        "policy_version": graph.policy_version,
        "schema_versions": graph.schema_versions,
        "source_history_hash": graph.source_history_hash,
        "edge_projection_bindings": rows,
    }
    return (
        _public_operation_result(
            lambda: g2e.project_integrity_replay_dependency_edges_v01(
                **call_kwargs
            )
        ),
        call_kwargs,
    )


def _alternate_transition_rule_field(
    rule: transition_registry.TransitionRuleV01,
    field_name: str,
) -> object:
    value = getattr(rule, field_name)
    if field_name == "abi_major_version":
        return 2
    if field_name == "root_commit_required":
        return not value
    if field_name == "required_guards":
        return (*value, "g2e5_mutated_guard")
    if field_name == "decision":
        return "BLOCKED_FAIL_CLOSED" if value != "BLOCKED_FAIL_CLOSED" else "ALLOW"
    if field_name == "source_lifecycle_state":
        return "PROPOSED" if value != "PROPOSED" else "VALIDATED"
    if field_name in {"source_artifact_type", "target_artifact_type"}:
        return "SemanticEvidence" if value != "SemanticEvidence" else "ValidatedEvidence"
    if field_name == "actor_role":
        return "root" if value != "root" else "continuous_delta_runtime"
    return str(value) + ":mutated"


def _matrix_negative_subcase(
    *,
    case_id: str,
    suffix: str,
    subcase_name: str,
    axis: str,
    reason: str | tuple[str, ...],
    bundle: g2e.ContinuousDeltaExecutionBundleV01,
    semantic_projection_memo: dict[
        int, tuple[object, dict[str, object]]
    ],
    constructibility_only: bool = False,
) -> (
    ContinuousDeltaRuntimeG2ESubcaseResultV01
    | _NegativeConstructibilityObservationV01
):
    if suffix == "transition_rule_eleven_field_substitution":
        parts = subcase_name.split("_", 2)
        rule_index = int(parts[1]) - 1
        field_name = parts[2]
        registry = transition_registry.build_continuous_delta_transition_registry_profile_v01()
        rules = list(registry.rules)
        governed_rule_id = rules[rule_index].rule_id
        rules[rule_index] = replace(
            rules[rule_index],
            **{
                field_name: _alternate_transition_rule_field(
                    rules[rule_index], field_name
                )
            },
        )
        candidate = replace(registry, rules=tuple(rules))
        result = transition_registry.validate_continuous_delta_transition_registry_profile_v01(
            candidate
        )
        return _observed_negative_subcase(
            case_id=case_id,
            subcase_name=subcase_name,
            axis=axis,
            expected_reason=reason,
            validation_target="continuous_delta_transition_registry_profile",
            validator_name=(
                "hedgehog.kernel.transition_registry_v01."
                "validate_continuous_delta_transition_registry_profile_v01"
            ),
            mutated_carrier=candidate,
            validation_result=result,
            semantic_metadata={
                "governed_rule_id": governed_rule_id,
                "governed_rule_field": field_name,
            },
            semantic_projection_memo=semantic_projection_memo,
            constructibility_only=constructibility_only,
        )
    if suffix == "transition_rule_order_or_terminal_path_forgery":
        registry = transition_registry.build_continuous_delta_transition_registry_profile_v01()
        rules = list(registry.rules)
        if subcase_name == "missing_rule":
            rules.pop()
            mutated = replace(registry, rules=tuple(rules))
            result = transition_registry.validate_continuous_delta_transition_registry_profile_v01(
                mutated
            )
            validator_name = (
                "hedgehog.kernel.transition_registry_v01."
                "validate_continuous_delta_transition_registry_profile_v01"
            )
        elif subcase_name == "duplicate_rule":
            rules[-1] = rules[0]
            mutated = replace(registry, rules=tuple(rules))
            result = transition_registry.validate_continuous_delta_transition_registry_profile_v01(
                mutated
            )
            validator_name = (
                "hedgehog.kernel.transition_registry_v01."
                "validate_continuous_delta_transition_registry_profile_v01"
            )
        elif subcase_name == "extra_rule":
            rules.append(replace(rules[-1], rule_id=rules[-1].rule_id + ":extra"))
            mutated = replace(registry, rules=tuple(rules))
            result = transition_registry.validate_continuous_delta_transition_registry_profile_v01(
                mutated
            )
            validator_name = (
                "hedgehog.kernel.transition_registry_v01."
                "validate_continuous_delta_transition_registry_profile_v01"
            )
        elif subcase_name == "reordered_rules":
            rules[0], rules[1] = rules[1], rules[0]
            mutated = replace(registry, rules=tuple(rules))
            result = transition_registry.validate_continuous_delta_transition_registry_profile_v01(
                mutated
            )
            validator_name = (
                "hedgehog.kernel.transition_registry_v01."
                "validate_continuous_delta_transition_registry_profile_v01"
            )
        elif subcase_name in {"t06_nonterminal", "t08_nonterminal"}:
            rule_index = 5 if subcase_name.startswith("t06") else 7
            rules[rule_index] = replace(
                rules[rule_index],
                decision="ALLOW",
                root_commit_required=False,
            )
            mutated = replace(registry, rules=tuple(rules))
            result = transition_registry.validate_continuous_delta_transition_registry_profile_v01(
                mutated
            )
            validator_name = (
                "hedgehog.kernel.transition_registry_v01."
                "validate_continuous_delta_transition_registry_profile_v01"
            )
        elif subcase_name == "t10_trace_insertion":
            t10 = bundle.g2e_transition_decisions[9]
            source_artifact = bundle.runtime_report_artifact
            identity_prefix = source_artifact.artifact_id.rsplit(":", 1)[0] + ":"
            mutated_artifact = replace(
                source_artifact,
                artifact_id=identity_prefix
                + _sha256_plain(
                    {
                        "inserted_transition_decision_id": t10.decision_id,
                        "runtime_trace_id": bundle.runtime_trace.trace_id,
                    }
                ),
            )
            mutated = replace(
                bundle,
                runtime_report_artifact=mutated_artifact,
            )
            result = g2e.validate_continuous_delta_execution_bundle_v01(mutated)
            validator_name = (
                "hedgehog.kernel.continuous_delta_runtime_v01."
                "validate_continuous_delta_execution_bundle_v01"
            )
        else:
            mutated = _non_accept_final_bundle(
                bundle, non_accept_axis="conflict"
            )
            result = g2e.validate_continuous_delta_execution_bundle_v01(mutated)
            validator_name = (
                "hedgehog.kernel.continuous_delta_runtime_v01."
                "validate_continuous_delta_execution_bundle_v01"
            )
        return _observed_negative_subcase(
            case_id=case_id,
            subcase_name=subcase_name,
            axis=axis,
            expected_reason=reason,
            validation_target=type(mutated).__name__,
            validator_name=validator_name,
            mutated_carrier=mutated,
            validation_result=result,
            semantic_projection_memo=semantic_projection_memo,
            constructibility_only=constructibility_only,
        )
    if suffix == "abi_projection_profile_substitution":
        parts = subcase_name.split("_", 2)
        profile_index = int(parts[1]) - 1
        profile_field = parts[2]
        profile_rows = (
            ("delta_source_proposed_artifact", bundle.delta_source_proposed_artifact),
            ("dependency_graph_artifact", bundle.dependency_graph_artifact),
            ("affected_set_artifact", bundle.affected_set_artifact),
            ("invalidation_report_artifact", bundle.invalidation_report_artifact),
            ("preservation_proof_artifact", bundle.preservation_proof_artifact),
            ("plan_proposed_artifact", bundle.plan_proposed_artifact),
            ("runtime_report_artifact", bundle.runtime_report_artifact),
        )
        field_name, artifact = profile_rows[profile_index]
        plain = kernel_artifact_to_plain_dict_v01(artifact)
        alternatives = {
            "artifact_type": (
                "SemanticEvidence"
                if artifact.artifact_type != "SemanticEvidence"
                else "ValidatedEvidence"
            ),
            "lifecycle_state": (
                "VALIDATED"
                if artifact.lifecycle_state != "VALIDATED"
                else "PROPOSED"
            ),
            "authority_class": (
                "NON_AUTHORITY"
                if artifact.authority_class != "NON_AUTHORITY"
                else "EVIDENCE_ONLY"
            ),
            "source_component": artifact.source_component + ".mutated",
            "payload": {**plain["payload"], "g2e5_profile_mutation": True},
        }
        mutated = _reseal_kernel_artifact(
            artifact,
            label=subcase_name,
            **{profile_field: alternatives[profile_field]},
        )
        candidate, outer_ids = _coherent_bundle_artifact_mutation(
            bundle, field_name=field_name, artifact=mutated
        )
        result = g2e.validate_continuous_delta_execution_bundle_v01(candidate)
        return _observed_negative_subcase(
            case_id=case_id,
            subcase_name=subcase_name,
            axis=profile_field,
            expected_reason=reason,
            validation_target="ContinuousDeltaExecutionBundleV01",
            validator_name=(
                "hedgehog.kernel.continuous_delta_runtime_v01."
                "validate_continuous_delta_execution_bundle_v01"
            ),
            mutated_carrier=candidate,
            validation_result=result,
            resealed_outer_ids=outer_ids,
            semantic_args=(candidate,),
            semantic_metadata={
                "governed_artifact_field": field_name,
                "governed_profile_field": profile_field,
            },
            semantic_projection_memo=semantic_projection_memo,
            constructibility_only=constructibility_only,
        )
    if suffix == "abi_parent_trace_or_root_artifact_substitution":
        artifact_rows = (
            ("delta_source_proposed_artifact", bundle.delta_source_proposed_artifact),
            ("delta_source_artifact", bundle.delta_source_artifact),
            ("dependency_graph_artifact", bundle.dependency_graph_artifact),
            ("affected_set_artifact", bundle.affected_set_artifact),
            ("invalidation_report_artifact", bundle.invalidation_report_artifact),
            ("plan_proposed_artifact", bundle.plan_proposed_artifact),
            ("plan_accepted_artifact", bundle.plan_accepted_artifact),
            ("preservation_proof_artifact", bundle.preservation_proof_artifact),
            ("runtime_report_artifact", bundle.runtime_report_artifact),
        )
        if subcase_name.startswith("parent_ids:"):
            _family, index_text, expected_field = subcase_name.split(":", 2)
            field_name, original = artifact_rows[int(index_text) - 1]
            if field_name != expected_field:
                raise ValueError("g2e5_case89_artifact_order_invalid")
            foreign_parent = next(
                artifact.artifact_id
                for _name, artifact in artifact_rows
                if artifact.artifact_id != original.artifact_id
                and artifact.artifact_id not in original.parent_refs
            )
            mutated = _reseal_kernel_artifact(
                original,
                label=subcase_name,
                parent_refs=(*original.parent_refs, foreign_parent),
            )
            candidate, outer_ids = _coherent_bundle_artifact_mutation(
                bundle, field_name=field_name, artifact=mutated
            )
        elif subcase_name.startswith("trace_refs:"):
            _family, index_text, expected_field = subcase_name.split(":", 2)
            field_name, original = artifact_rows[int(index_text) - 1]
            if field_name != expected_field:
                raise ValueError("g2e5_case89_artifact_order_invalid")
            mutated = _reseal_kernel_artifact(
                original,
                label=subcase_name,
                trace_refs=(
                    *original.trace_refs,
                    f"trace:g2e5:case89:foreign:{index_text}",
                ),
            )
            candidate, outer_ids = _coherent_bundle_artifact_mutation(
                bundle, field_name=field_name, artifact=mutated
            )
        elif subcase_name.startswith("time_envelope:"):
            _family, index_text, expected_field = subcase_name.split(":", 2)
            field_name, original = artifact_rows[int(index_text) - 1]
            if field_name != expected_field:
                raise ValueError("g2e5_case89_artifact_order_invalid")
            time_envelope = kernel_artifact_to_plain_dict_v01(original)[
                "time_envelope"
            ]
            replacement_time = "2026-08-01T00:00:01+00:00"
            if time_envelope["pt_created_at"] == replacement_time:
                replacement_time = "2026-08-01T00:00:02+00:00"
            mutated = _reseal_kernel_artifact(
                original,
                label=subcase_name,
                time_envelope={
                    **time_envelope,
                    "pt_created_at": replacement_time,
                },
            )
            candidate, outer_ids = _coherent_bundle_artifact_mutation(
                bundle, field_name=field_name, artifact=mutated
            )
        elif subcase_name == "plan_relation":
            field_name = "plan_accepted_artifact"
            original = bundle.plan_accepted_artifact
            mutated = _reseal_kernel_artifact(
                original,
                label=subcase_name,
                parent_refs=tuple(reversed(original.parent_refs)),
            )
            candidate, outer_ids = _coherent_bundle_artifact_mutation(
                bundle, field_name=field_name, artifact=mutated
            )
        else:
            mutated = bundle.final_root_decision_artifact
            candidate = replace(
                bundle, plan_root_decision_artifact=mutated
            )
            outer_ids = (mutated.artifact_id,)
        result = g2e.validate_continuous_delta_execution_bundle_v01(candidate)
        return _observed_negative_subcase(
            case_id=case_id,
            subcase_name=subcase_name,
            axis=axis,
            expected_reason=reason,
            validation_target="ContinuousDeltaExecutionBundleV01",
            validator_name=(
                "hedgehog.kernel.continuous_delta_runtime_v01."
                "validate_continuous_delta_execution_bundle_v01"
            ),
            mutated_carrier=candidate,
            validation_result=result,
            resealed_outer_ids=outer_ids,
            semantic_args=(candidate,),
            semantic_metadata={
                "governed_case89_family": axis,
                "governed_artifact_field": (
                    field_name
                    if subcase_name != "shared_root_artifact"
                    else "plan_root_decision_artifact"
                ),
            },
            semantic_projection_memo=semantic_projection_memo,
            constructibility_only=constructibility_only,
        )
    if suffix == "identity_prefix_or_domain_collision":
        if subcase_name == "serialized_prefix":
            mutated = replace(
                bundle.delta,
                delta_id="g2e_world_state_delta_v01:" + ("0" * 64),
            )
            result = g2e.validate_world_state_delta_v01(mutated)
            validator_name = (
                "hedgehog.kernel.continuous_delta_runtime_v01."
                "validate_world_state_delta_v01"
            )
        elif subcase_name == "abi_prefix_domain":
            mutated = replace(
                bundle.dependency_graph_artifact,
                artifact_id="g2eabi_graph_v01:" + ("0" * 64),
            )
            candidate = replace(bundle, dependency_graph_artifact=mutated)
            result = g2e.validate_continuous_delta_execution_bundle_v01(candidate)
            validator_name = (
                "hedgehog.kernel.continuous_delta_runtime_v01."
                "validate_continuous_delta_execution_bundle_v01"
            )
            semantic_mutated = candidate
        else:
            profile = g2e.build_dependency_fingerprint_profile_v01()
            mutated = replace(profile, typed_role="G2E_CROSS_ROLE_COLLISION")
            mutated = replace(
                mutated,
                fingerprint_profile_id=(
                    g2e.rebuild_dependency_fingerprint_profile_identity_v01(mutated)
                ),
            )
            call_kwargs = {
                "profile": mutated,
                "graph": bundle.dependency_graph,
                "dependency_edges": bundle.dependency_edges,
                "source_artifacts": bundle.source_context.baseline_source_artifacts,
                "policy_version": bundle.delta.baseline_policy_version,
                "schema_versions": bundle.delta.baseline_schema_versions,
                "source_history_hash": bundle.delta.baseline_source_history_hash,
            }
            result = g2e.validate_dependency_fingerprint_against_sources_v01(
                bundle.delta.dependency_fingerprint_before,
                **call_kwargs,
            )
            validator_name = (
                "hedgehog.kernel.continuous_delta_runtime_v01."
                "validate_dependency_fingerprint_against_sources_v01"
            )
            semantic_mutated = mutated
        if subcase_name == "serialized_prefix":
            semantic_mutated = mutated
        return _observed_negative_subcase(
            case_id=case_id,
            subcase_name=subcase_name,
            axis=axis,
            expected_reason=reason,
            validation_target=type(mutated).__name__,
            validator_name=validator_name,
            mutated_carrier=semantic_mutated,
            validation_result=result,
            semantic_args=(
                (bundle.delta.dependency_fingerprint_before,)
                if subcase_name == "cross_role_fingerprint"
                else (semantic_mutated,)
            ),
            semantic_kwargs=(
                call_kwargs
                if subcase_name == "cross_role_fingerprint"
                else None
            ),
            mutated_argument_locator=(
                "kw:profile"
                if subcase_name == "cross_role_fingerprint"
                else "arg:0"
            ),
            semantic_projection_memo=semantic_projection_memo,
            constructibility_only=constructibility_only,
        )
    raise ValueError("g2e5_matrix_negative_recipe_missing:" + suffix)


def _ordinary_negative_subcase(
    *,
    case_id: str,
    suffix: str,
    subcase_name: str,
    axis: str,
    reason: str | tuple[str, ...],
    valid_material: dict[str, object],
    foreign_material: dict[str, object],
    conditional_material: dict[str, object],
    semantic_projection_memo: dict[
        int, tuple[object, dict[str, object]]
    ],
    constructibility_only: bool = False,
) -> (
    ContinuousDeltaRuntimeG2ESubcaseResultV01
    | _NegativeConstructibilityObservationV01
):
    inputs = valid_material["inputs"]
    execution = valid_material["execution"]
    bundle = execution["bundle"]
    if type(bundle) is not g2e.ContinuousDeltaExecutionBundleV01:
        raise ValueError("g2e5_negative_bundle_basis_missing")

    def observed(
        *,
        mutated: object,
        result: object,
        validator: str,
        target: str | None = None,
        outer_ids: tuple[str, ...] = (),
        call_args: tuple[object, ...] | None = None,
        call_kwargs: dict[str, object] | None = None,
        locator: str = "arg:0",
        operation_result: object | None = None,
        metadata: dict[str, object] | None = None,
    ) -> ContinuousDeltaRuntimeG2ESubcaseResultV01:
        return _observed_negative_subcase(
            case_id=case_id,
            subcase_name=subcase_name,
            axis=axis,
            expected_reason=reason,
            validation_target=target or type(mutated).__name__,
            validator_name=validator,
            mutated_carrier=mutated,
            validation_result=result,
            resealed_outer_ids=outer_ids,
            semantic_args=call_args,
            semantic_kwargs=call_kwargs,
            mutated_argument_locator=locator,
            semantic_operation_result=operation_result,
            semantic_metadata=metadata,
            semantic_projection_memo=semantic_projection_memo,
            constructibility_only=constructibility_only,
        )

    g2e_prefix = "hedgehog.kernel.continuous_delta_runtime_v01."
    if suffix == "malformed_delta_identity":
        candidate = replace(
            inputs["delta"],
            delta_id=(
                "g2e_world_state_delta_v01:"
                + _sha("g2e5-malformed-delta-identity-stale")
            ),
        )
        return observed(
            mutated=candidate,
            result=g2e.validate_world_state_delta_v01(candidate),
            validator=g2e_prefix + "validate_world_state_delta_v01",
        )
    if suffix == "unvalidated_delta_source":
        candidate = replace(inputs["context"], g2b_writeback_evidence="forbidden")
        return observed(
            mutated=candidate,
            result=g2e.validate_continuous_delta_source_context_v01(candidate),
            validator=g2e_prefix + "validate_continuous_delta_source_context_v01",
        )
    if suffix == "stale_baseline":
        stale_report = "g2d_runtime_report_v02:" + ("0" * 64)
        source = _reseal_public_carrier(
            inputs["source_binding"], baseline_report_id=stale_report
        )
        field = _reseal_public_carrier(
            inputs["changed_field"], source_binding_id=source.source_binding_id
        )
        artifact = _reseal_public_carrier(
            inputs["changed_artifact"], source_binding_id=source.source_binding_id
        )
        delta = _reseal_public_carrier(
            inputs["delta"],
            baseline_report_id=stale_report,
            ordered_source_binding_ids=(source.source_binding_id,),
            ordered_changed_field_binding_ids=(field.changed_field_binding_id,),
            ordered_changed_artifact_binding_ids=(artifact.changed_artifact_binding_id,),
        )
        request = g2e.build_affected_set_request_v01(
            delta=delta, graph=inputs["graph"], trace_refs=inputs["request"].trace_refs
        )
        affected = g2e.compute_affected_set_v01(
            **_affected_context_kwargs(
                inputs,
                request=request,
                delta=delta,
                source_bindings=(source,),
                changed_field_bindings=(field,),
                changed_artifact_bindings=(artifact,),
            )
        )
        call_kwargs = {
            "affected_set": affected,
            "delta": delta,
            "source_context": inputs["context"],
            "source_bindings": (source,),
            "changed_field_bindings": (field,),
            "changed_artifact_bindings": (artifact,),
            "dependency_edges": inputs["dependency_edges"],
            "dependency_graph": inputs["graph"],
        }
        result = _public_operation_result(
            lambda: g2e.derive_invalidation_report_v01(**call_kwargs)
        )
        return observed(
            mutated=delta,
            result=result,
            validator=g2e_prefix + "derive_invalidation_report_v01",
            outer_ids=(source.source_binding_id, request.affected_request_id, affected.affected_set_id),
            call_args=(),
            call_kwargs=call_kwargs,
            locator="kw:delta",
        )
    if suffix == "future_observation":
        observed_source = inputs["observed"][0]
        plain = kernel_artifact_to_plain_dict_v01(observed_source)
        envelope = {**plain["time_envelope"], "et_observed_at": "2026-08-01T00:00:01+00:00"}
        candidate_source = _reseal_kernel_artifact(
            observed_source,
            label=suffix,
            time_envelope=envelope,
        )
        candidate = replace(
            inputs["context"],
            observed_source_artifacts=(candidate_source, *inputs["observed"][1:]),
        )
        return observed(
            mutated=candidate,
            result=g2e.validate_continuous_delta_source_context_v01(candidate),
            validator=g2e_prefix + "validate_continuous_delta_source_context_v01",
        )
    if suffix == "invalid_time_window":
        candidate = _reseal_public_carrier(
            inputs["delta"], valid_to_utc=inputs["delta"].valid_from_utc
        )
        call_kwargs = _affected_context_kwargs(inputs, delta=candidate)
        return observed(
            mutated=candidate,
            result=g2e.validate_affected_set_against_graph_v01(
                inputs["affected"],
                **call_kwargs,
            ),
            validator=g2e_prefix + "validate_affected_set_against_graph_v01",
            call_args=(inputs["affected"],),
            call_kwargs=call_kwargs,
            locator="kw:delta",
        )
    if suffix in {"duplicate_changed_field", "conflicting_duplicate_delta"}:
        original = inputs["changed_field"]
        changes: dict[str, object] = {
            "trace_refs": (
                *original.trace_refs,
                "trace:g2e5:" + suffix,
            )
        }
        if suffix == "conflicting_duplicate_delta":
            changes["observed_value_sha256"] = _sha(
                "g2e5-conflicting-observed-value"
            )
        duplicate = _reseal_public_carrier(original, **changes)
        semantic_key = (
            original.source_binding_id,
            original.json_pointer,
        )
        duplicate_semantic_key = (
            duplicate.source_binding_id,
            duplicate.json_pointer,
        )
        original_material = (
            original.prior_value_sha256,
            original.observed_value_sha256,
            original.change_class,
            original.observed_at_utc,
        )
        duplicate_material = (
            duplicate.prior_value_sha256,
            duplicate.observed_value_sha256,
            duplicate.change_class,
            duplicate.observed_at_utc,
        )
        if (
            duplicate.changed_field_binding_id
            == original.changed_field_binding_id
            or duplicate_semantic_key != semantic_key
            or (
                suffix == "duplicate_changed_field"
                and duplicate_material != original_material
            )
            or (
                suffix == "conflicting_duplicate_delta"
                and duplicate_material == original_material
            )
        ):
            raise ValueError("g2e5_duplicate_binding_fixture_invalid")
        changed = (original, duplicate)
        delta = _reseal_public_carrier(
            inputs["delta"],
            ordered_changed_field_binding_ids=tuple(
                item.changed_field_binding_id for item in changed
            ),
        )
        if len(set(delta.ordered_changed_field_binding_ids)) != 2:
            raise ValueError("g2e5_duplicate_binding_identity_invalid")
        delta_validation = g2e.validate_world_state_delta_v01(delta)
        if (
            type(delta_validation) is not g2e.ContinuousDeltaValidationReportV01
            or delta_validation.status != "PASS"
            or delta_validation.reason_codes != ()
            or delta_validation.source_reason_codes != ()
        ):
            raise ValueError("g2e5_duplicate_delta_invalid")
        request = g2e.build_affected_set_request_v01(
            delta=delta, graph=inputs["graph"], trace_refs=inputs["request"].trace_refs
        )
        request_validation = g2e.validate_affected_set_request_v01(request)
        if (
            type(request_validation)
            is not g2e.ContinuousDeltaValidationReportV01
            or request_validation.status != "PASS"
            or request_validation.reason_codes != ()
            or request_validation.source_reason_codes != ()
        ):
            raise ValueError("g2e5_duplicate_request_invalid")
        call_kwargs = _affected_context_kwargs(
            inputs,
            request=request,
            delta=delta,
            changed_field_bindings=changed,
        )
        result = _public_operation_result(
            lambda: g2e.compute_affected_set_v01(**call_kwargs)
        )
        return observed(
            mutated=duplicate,
            result=result,
            validator=g2e_prefix + "compute_affected_set_v01",
            outer_ids=(delta.delta_id, request.affected_request_id),
            call_args=(),
            call_kwargs=call_kwargs,
            locator="kw:changed_field_bindings",
        )
    if suffix == "unknown_field_path":
        candidate = _reseal_public_carrier(inputs["changed_field"], json_pointer="not-a-pointer")
        return observed(
            mutated=candidate,
            result=g2e.validate_changed_field_binding_v01(candidate),
            validator=g2e_prefix + "validate_changed_field_binding_v01",
        )
    if suffix in {"unknown_changed_artifact", "observed_source_payload_hash_mismatch"}:
        changes = (
            {"observed_artifact_id": "artifact:g2e5:unknown"}
            if suffix == "unknown_changed_artifact"
            else {"observed_payload_sha256": _sha("g2e5-observed-payload-mismatch")}
        )
        candidate = _reseal_public_carrier(inputs["changed_artifact"], **changes)
        delta = _reseal_public_carrier(
            inputs["delta"],
            ordered_changed_artifact_binding_ids=(
                candidate.changed_artifact_binding_id,
            ),
        )
        delta_validation = g2e.validate_world_state_delta_v01(delta)
        if (
            type(delta_validation) is not g2e.ContinuousDeltaValidationReportV01
            or delta_validation.status != "PASS"
            or delta_validation.reason_codes != ()
            or delta_validation.source_reason_codes != ()
        ):
            raise ValueError("g2e5_changed_artifact_delta_invalid")
        request = g2e.build_affected_set_request_v01(
            delta=delta,
            graph=inputs["graph"],
            trace_refs=inputs["request"].trace_refs,
        )
        call_kwargs = _affected_context_kwargs(
            inputs,
            request=request,
            delta=delta,
            changed_artifact_bindings=(candidate,),
        )
        result = _public_operation_result(
            lambda: g2e.compute_affected_set_v01(**call_kwargs)
        )
        return observed(
            mutated=candidate,
            result=result,
            validator=g2e_prefix + "compute_affected_set_v01",
            outer_ids=(delta.delta_id, request.affected_request_id),
            call_args=(),
            call_kwargs=call_kwargs,
            locator="kw:changed_artifact_bindings",
        )
    if suffix in {
        "cross_transaction_substitution",
        "cross_domain_substitution",
        "cross_root_substitution",
    }:
        foreign_inputs = foreign_material["inputs"]
        if suffix == "cross_transaction_substitution":
            candidate = replace(
                inputs["context"],
                g2a_registry=foreign_inputs["context"].g2a_registry,
                g2a_packet=foreign_inputs["context"].g2a_packet,
                g2a_dependency_candidate=foreign_inputs["context"].g2a_dependency_candidate,
                g2a_current_observations=foreign_inputs["context"].g2a_current_observations,
                g2a_root_invalidation_material=foreign_inputs["context"].g2a_root_invalidation_material,
            )
        elif suffix == "cross_domain_substitution":
            local_report = inputs["context"].g2b_resolution_report
            local_query = local_report.query
            mutated_query = replace(
                local_query,
                domain=foreign_inputs["context"].g2b_resolution_report.query.domain,
            )
            candidate = replace(
                inputs["context"],
                g2b_resolution_report=replace(local_report, query=mutated_query),
            )
        else:
            foreign_owner = (
                foreign_inputs["context"]
                .baseline_g2c_route_eligibility_artifact.owner_root_id
            )
            local_owner = (
                inputs["context"]
                .baseline_g2c_route_eligibility_artifact.owner_root_id
            )
            if foreign_owner == local_owner:
                raise ValueError("g2e5_cross_root_owner_not_foreign")
            source_artifact = _reseal_kernel_artifact(
                inputs["context"].baseline_g2c_route_eligibility_artifact,
                label="cross_root_substitution",
                owner_root_id=foreign_owner,
            )
            candidate = replace(
                inputs["context"],
                baseline_g2c_route_eligibility_artifact=source_artifact,
            )
        return observed(
            mutated=candidate,
            result=g2e.validate_continuous_delta_source_context_v01(candidate),
            validator=g2e_prefix + "validate_continuous_delta_source_context_v01",
            metadata=(
                {
                    "mutation_path": "g2b_resolution_report.query.domain",
                    "local_transaction_retained": True,
                    "local_g2d_bundle_retained": True,
                    "local_root_retained": True,
                }
                if suffix == "cross_domain_substitution"
                else {
                    "mutation_path": (
                        "baseline_g2c_route_eligibility_artifact.owner_root_id"
                    ),
                    "local_transaction_retained": True,
                    "local_domain_retained": True,
                }
                if suffix == "cross_root_substitution"
                else None
            ),
        )
    if suffix in {
        "policy_version_substitution",
        "schema_version_substitution",
        "source_history_substitution",
    }:
        values = {
            "policy_version": inputs["graph"].policy_version,
            "schema_versions": inputs["graph"].schema_versions,
            "source_history_hash": inputs["graph"].source_history_hash,
        }
        if suffix == "policy_version_substitution":
            values["policy_version"] = str(values["policy_version"]) + ":foreign"
        elif suffix == "schema_version_substitution":
            values["schema_versions"] = ("v9.9",)
        else:
            values["source_history_hash"] = _sha("g2e5-foreign-history")
        call_kwargs = {
            "profile": inputs["fingerprint_profile"],
            "graph": inputs["graph"],
            "dependency_edges": inputs["dependency_edges"],
            "source_artifacts": inputs["baseline"],
            **values,
        }
        result = g2e.validate_dependency_fingerprint_against_sources_v01(
            inputs["delta"].dependency_fingerprint_before,
            **call_kwargs,
        )
        changed_keyword = {
            "policy_version_substitution": "policy_version",
            "schema_version_substitution": "schema_versions",
            "source_history_substitution": "source_history_hash",
        }[suffix]
        return observed(
            mutated=call_kwargs[changed_keyword],
            result=result,
            validator=g2e_prefix + "validate_dependency_fingerprint_against_sources_v01",
            call_args=(inputs["delta"].dependency_fingerprint_before,),
            call_kwargs=call_kwargs,
            locator="kw:" + changed_keyword,
        )
    if suffix == "dependency_fingerprint_forgery":
        candidate = _reseal_public_carrier(
            inputs["delta"], dependency_fingerprint_after=_sha("g2e5-forged-fingerprint")
        )
        request = g2e.build_affected_set_request_v01(
            delta=candidate,
            graph=inputs["graph"],
            trace_refs=inputs["request"].trace_refs,
        )
        _require_public_pass(
            g2e.validate_affected_set_request_v01(request),
            "g2e5_negative_request_invalid",
        )
        call_kwargs = _affected_context_kwargs(
            inputs,
            request=request,
            delta=candidate,
        )
        result = _public_operation_result(
            lambda: g2e.compute_affected_set_v01(**call_kwargs)
        )
        return observed(
            mutated=candidate,
            result=result,
            validator=g2e_prefix + "compute_affected_set_v01",
            call_args=(),
            call_kwargs=call_kwargs,
            locator="kw:delta",
        )
    if suffix == "dependency_digest_role_collision":
        profile = _reseal_public_carrier(
            inputs["fingerprint_profile"], typed_role="G2E_OTHER_ROLE"
        )
        call_kwargs = {
            "profile": profile,
            "graph": inputs["graph"],
            "dependency_edges": inputs["dependency_edges"],
            "source_artifacts": inputs["baseline"],
            "policy_version": inputs["graph"].policy_version,
            "schema_versions": inputs["graph"].schema_versions,
            "source_history_hash": inputs["graph"].source_history_hash,
        }
        result = g2e.validate_dependency_fingerprint_against_sources_v01(
            inputs["delta"].dependency_fingerprint_before,
            **call_kwargs,
        )
        return observed(
            mutated=profile,
            result=result,
            validator=g2e_prefix + "validate_dependency_fingerprint_against_sources_v01",
            call_args=(inputs["delta"].dependency_fingerprint_before,),
            call_kwargs=call_kwargs,
            locator="kw:profile",
        )
    if suffix in {
        "missing_dependency_edge",
        "extra_unrelated_dependency_edge",
        "duplicate_dependency_edge",
        "self_dependency_edge",
        "dependency_cycle",
        "unknown_dependency_artifact",
        "unknown_dependent_artifact",
        "source_payload_pointer_unavailable",
    }:
        rows = _edge_projection_rows(inputs)
        nodes = inputs["graph"].ordered_node_ids
        if suffix == "missing_dependency_edge":
            mutated_rows = rows[:-1]
        elif suffix == "extra_unrelated_dependency_edge":
            mutated_rows = (*rows, (nodes[-1], nodes[0], (), "ARTIFACT_DEPENDENCY"))
        elif suffix == "duplicate_dependency_edge":
            mutated_rows = (*rows, rows[0])
        elif suffix == "self_dependency_edge":
            mutated_rows = (*rows, (nodes[0], nodes[0], (), "ARTIFACT_DEPENDENCY"))
        elif suffix == "dependency_cycle":
            mutated_rows = (*rows, (nodes[0], nodes[1], (), "ARTIFACT_DEPENDENCY"))
        elif suffix == "unknown_dependency_artifact":
            mutated_rows = (*rows, (nodes[-1], "artifact:g2e5:unknown", (), "ARTIFACT_DEPENDENCY"))
        elif suffix == "unknown_dependent_artifact":
            mutated_rows = (*rows, ("artifact:g2e5:unknown", nodes[0], (), "ARTIFACT_DEPENDENCY"))
        else:
            first = rows[0]
            mutated_rows = ((first[0], first[1], ("/missing",), first[3]), *rows[1:])
        result, call_kwargs = _project_edge_mutation(inputs, mutated_rows)
        return observed(
            mutated=mutated_rows,
            result=result,
            validator=g2e_prefix + "project_integrity_replay_dependency_edges_v01",
            target="DeltaDependencyEdgeV01",
            call_args=(),
            call_kwargs=call_kwargs,
            locator="kw:edge_projection_bindings",
        )
    if suffix in {
        "graph_version_substitution",
        "graph_node_bound_overflow",
        "graph_edge_bound_overflow",
        "unbounded_affected_closure",
        "graph_basis_identity_mismatch",
    }:
        changes = {
            "graph_version_substitution": {"graph_version": "v9.9"},
            "graph_node_bound_overflow": {"node_count": inputs["graph"].node_count + 1},
            "graph_edge_bound_overflow": {"edge_count": inputs["graph"].edge_count + 1},
            "unbounded_affected_closure": {"max_nodes": 1},
            "graph_basis_identity_mismatch": {"graph_basis_sha256": "x"},
        }[suffix]
        candidate = _reseal_public_carrier(inputs["graph"], **changes)
        return observed(
            mutated=candidate,
            result=g2e.validate_dependency_graph_index_v01(candidate),
            validator=g2e_prefix + "validate_dependency_graph_index_v01",
        )
    if suffix in {"graph_edge_reordering", "source_replay_edge_fingerprint_mismatch"}:
        edge = inputs["dependency_edges"][0]
        changes = (
            {"canonical_order": 0}
            if suffix == "graph_edge_reordering"
            else {"source_replay_edge_sha256": "x"}
        )
        candidate = _reseal_public_carrier(edge, **changes)
        return observed(
            mutated=candidate,
            result=g2e.validate_delta_dependency_edge_v01(candidate),
            validator=g2e_prefix + "validate_delta_dependency_edge_v01",
        )
    if suffix == "graph_hop_bound_overflow":
        call_kwargs = _hop_bound_context_kwargs(inputs)
        result = _public_operation_result(
            lambda: g2e.compute_affected_set_v01(**call_kwargs)
        )
        return observed(
            mutated=call_kwargs["graph"],
            result=result,
            validator=g2e_prefix + "compute_affected_set_v01",
            call_args=(),
            call_kwargs=call_kwargs,
            locator="kw:graph",
        )
    if suffix in {
        "omitted_direct_dependent",
        "omitted_transitive_dependent",
        "injected_unrelated_affected_artifact",
        "affected_set_reordering",
        "affected_closure_proof_forgery",
    }:
        affected = inputs["affected"]
        if suffix == "omitted_direct_dependent":
            omitted = affected.ordered_directly_affected_ids[0]
            candidate = _reseal_public_carrier(
                affected,
                ordered_directly_affected_ids=affected.ordered_directly_affected_ids[1:],
                ordered_affected_ids=tuple(
                    item for item in affected.ordered_affected_ids if item != omitted
                ),
                ordered_unaffected_ids=(*affected.ordered_unaffected_ids, omitted),
                visited_node_count=affected.visited_node_count - 1,
            )
        elif suffix == "omitted_transitive_dependent":
            omitted_rows = (
                affected.ordered_transitively_affected_ids
                or affected.ordered_directly_affected_ids
            )
            omitted = omitted_rows[-1]
            candidate = _reseal_public_carrier(
                affected,
                ordered_transitively_affected_ids=tuple(
                    item for item in affected.ordered_transitively_affected_ids if item != omitted
                ),
                ordered_directly_affected_ids=tuple(
                    item for item in affected.ordered_directly_affected_ids if item != omitted
                ),
                ordered_affected_ids=tuple(
                    item for item in affected.ordered_affected_ids if item != omitted
                ),
                ordered_unaffected_ids=(*affected.ordered_unaffected_ids, omitted),
                visited_node_count=affected.visited_node_count - 1,
            )
        elif subcase_name == "pointer_suppression":
            if (
                not affected.ordered_directly_affected_ids
                or not affected.ordered_transitively_affected_ids
            ):
                raise ValueError("g2e5_pointer_suppression_basis_invalid")
            suppressed = (
                affected.ordered_directly_affected_ids[0],
                affected.ordered_transitively_affected_ids[-1],
            )
            if len(set(suppressed)) != 2:
                raise ValueError("g2e5_pointer_suppression_basis_invalid")
            candidate = _reseal_public_carrier(
                affected,
                ordered_transitively_affected_ids=tuple(
                    item
                    for item in affected.ordered_transitively_affected_ids
                    if item not in suppressed
                ),
                ordered_directly_affected_ids=tuple(
                    item
                    for item in affected.ordered_directly_affected_ids
                    if item not in suppressed
                ),
                ordered_affected_ids=tuple(
                    item
                    for item in affected.ordered_affected_ids
                    if item not in suppressed
                ),
                ordered_unaffected_ids=(
                    *affected.ordered_unaffected_ids,
                    *suppressed,
                ),
                visited_node_count=affected.visited_node_count - len(suppressed),
            )
        elif suffix == "injected_unrelated_affected_artifact":
            injected = affected.ordered_unaffected_ids[0]
            candidate = _reseal_public_carrier(
                affected,
                ordered_transitively_affected_ids=(*affected.ordered_transitively_affected_ids, injected),
                ordered_affected_ids=(*affected.ordered_affected_ids, injected),
                ordered_unaffected_ids=affected.ordered_unaffected_ids[1:],
                visited_node_count=affected.visited_node_count + 1,
            )
        elif suffix == "affected_set_reordering":
            candidate = _reseal_public_carrier(
                affected, ordered_affected_ids=tuple(reversed(affected.ordered_affected_ids))
            )
        else:
            candidate = _reseal_public_carrier(
                affected, closure_proof_sha256=_sha("g2e5-forged-closure")
            )
        call_kwargs = _affected_context_kwargs(inputs)
        return observed(
            mutated=candidate,
            result=g2e.validate_affected_set_against_graph_v01(
                candidate, **call_kwargs
            ),
            validator=g2e_prefix + "validate_affected_set_against_graph_v01",
            call_args=(candidate,),
            call_kwargs=call_kwargs,
        )
    if suffix in {
        "invalidation_reason_substitution",
        "deletion_disguised_as_invalidation",
        "invalidation_predecessor_mismatch",
        "invalidation_supersession_mismatch",
        "invalidation_binding_carrier_omission",
    }:
        record = execution["invalidation_records"][0]
        changes = {
            "invalidation_reason_substitution": {"invalidation_reason_class": "UNKNOWN"},
            "deletion_disguised_as_invalidation": {"deleted": True},
            "invalidation_predecessor_mismatch": {"predecessor_artifact_id": "artifact:g2e5:foreign"},
            "invalidation_supersession_mismatch": {"superseded_by_artifact_id": "artifact:g2e5:successor"},
            "invalidation_binding_carrier_omission": {"triggering_binding_ids": ()},
        }[suffix]
        candidate = _reseal_public_carrier(record, **changes)
        return observed(
            mutated=candidate,
            result=g2e.validate_artifact_invalidation_record_v01(candidate),
            validator=g2e_prefix + "validate_artifact_invalidation_record_v01",
        )
    if suffix in {
        "preserved_payload_mutation",
        "preserved_full_artifact_bytes_mutation",
        "preserved_identity_mutation",
    }:
        proof = bundle.preservation_proof
        proof_kwargs = {
            "baseline_graph_id": proof.baseline_graph_id,
            "affected_set_id": proof.affected_set_id,
            "ordered_preserved_artifact_ids": proof.ordered_preserved_artifact_ids,
            "ordered_before_artifact_sha256": proof.ordered_before_artifact_sha256,
            "ordered_after_artifact_sha256": proof.ordered_after_artifact_sha256,
            "ordered_before_payload_sha256": proof.ordered_before_payload_sha256,
            "ordered_after_payload_sha256": proof.ordered_after_payload_sha256,
            "ordered_before_identity_ids": proof.ordered_before_identity_ids,
            "ordered_after_identity_ids": proof.ordered_after_identity_ids,
        }
        if suffix == "preserved_identity_mutation":
            changed_keyword = "ordered_after_identity_ids"
            proof_kwargs[changed_keyword] = (
                "artifact:g2e5:changed",
                *proof.ordered_after_identity_ids[1:],
            )
        elif suffix == "preserved_payload_mutation":
            changed_keyword = "ordered_after_payload_sha256"
            proof_kwargs[changed_keyword] = (
                _sha("g2e5-changed-payload"),
                *proof.ordered_after_payload_sha256[1:],
            )
        else:
            changed_keyword = "ordered_after_artifact_sha256"
            proof_kwargs[changed_keyword] = (
                _sha("g2e5-changed-artifact"),
                *proof.ordered_after_artifact_sha256[1:],
            )
        candidate = g2e.build_preservation_proof_v01(**proof_kwargs)
        return observed(
            mutated=proof_kwargs[changed_keyword],
            result=candidate.reason_codes,
            validator=g2e_prefix + "build_preservation_proof_v01",
            call_args=(),
            call_kwargs=proof_kwargs,
            locator="kw:" + changed_keyword,
            operation_result=candidate,
        )
    if suffix in {"hidden_cache_mutation", "hidden_mutable_global_state"}:
        changes = (
            {"after_cache_state_sha256": _sha("g2e5-hidden-cache-state")}
            if suffix == "hidden_cache_mutation"
            else {"mutable_global_write_count": 1}
        )
        candidate = _reseal_preservation_proof(
            bundle.preservation_proof, **changes
        )
        return observed(
            mutated=candidate,
            result=g2e.validate_preservation_proof_v01(candidate),
            validator=g2e_prefix + "validate_preservation_proof_v01",
        )
    if suffix == "in_place_recomputation":
        binding = bundle.recomputed_bindings[0]
        candidate = _reseal_public_carrier(
            binding,
            new_artifact_id=binding.prior_artifact_id,
            new_payload_sha256=binding.prior_payload_sha256,
        )
        return observed(
            mutated=candidate,
            result=g2e.validate_recomputed_artifact_binding_v01(candidate),
            validator=g2e_prefix + "validate_recomputed_artifact_binding_v01",
        )
    if suffix in {
        "stale_reuse_certificate_retained_current",
        "packet_kept_executable_after_invalidation",
        "packet_revoked_without_root_seam",
    }:
        source_record = execution["invalidation_records"][0]
        semantic_metadata: dict[str, object] = {}
        if suffix == "stale_reuse_certificate_retained_current":
            relation_changes = {
                "invalidation_reason_class": "REUSE_CERTIFICATE_STALE",
                "g2a_packet_relation": "NOT_APPLICABLE",
                "g2b_reuse_relation": "REUSE_CERTIFICATE_STALE",
                "g2c_route_relation": "ROUTE_CURRENT",
                "candidate_id": (
                    inputs["context"].g2b_reuse_certificate.certificate_id
                ),
            }
        else:
            packet_id = inputs["context"].g2a_packet.packet_identity.packet_id
            g2a_family = inputs["g2a"]
            if suffix == "packet_kept_executable_after_invalidation":
                pending = _g2a_pending_negative_setup(
                    g2a_family,
                    label=_domain_slug(inputs["domain_id"]) + ":packet-kept",
                )
                inspection = pending["inspection"]
                relation_candidate_id = packet_id
                trace_prefix = (
                    "g2a_present_eligibility:"
                    + inspection.transition_history_sha256,
                )
                triggering_ids = (
                    *source_record.triggering_binding_ids,
                    inspection.transition_history_sha256,
                )
                semantic_metadata = {
                    "g2a_semantic_type": type(inspection).__name__,
                    "g2a_semantic_id": inspection.registry_id,
                    "present_eligibility_status": (
                        inspection.present_eligibility_status
                    ),
                    "present_executable": inspection.present_executable,
                    "root_seam_present": True,
                    "source_registry_unchanged": (
                        g2a_family["registry"]
                        is inputs["context"].g2a_registry
                    ),
                }
            else:
                revocation_material = _g2a_revocation_candidate(g2a_family)
                revocation = revocation_material["candidate"]
                relation_candidate_id = packet_id
                trace_prefix = (revocation.revocation_candidate_id,)
                triggering_ids = (
                    *source_record.triggering_binding_ids,
                    revocation.revocation_candidate_id,
                )
                semantic_metadata = {
                    "g2a_semantic_type": type(revocation).__name__,
                    "g2a_semantic_id": revocation.revocation_candidate_id,
                    "revocation_validation": _plain_data(
                        revocation_material["validation_result"]
                    ),
                    "revocation_packet_validation": _plain_data(
                        revocation_material["packet_validation_result"]
                    ),
                    "root_seam_present": False,
                    "accepted_revocation_binding_created": False,
                    "revocation_transition_recorded": False,
                }
            relation_changes = {
                "invalidation_reason_class": "PACKET_ROOT_REVIEW_REQUIRED",
                "g2a_packet_relation": "PACKET_ROOT_REVIEW_REQUIRED",
                "g2b_reuse_relation": "NOT_APPLICABLE",
                "g2c_route_relation": "ROUTE_CURRENT",
                "candidate_id": relation_candidate_id,
                "trace_prefix": trace_prefix,
                "triggering_binding_ids": triggering_ids,
            }
        candidate_record = g2e.build_artifact_invalidation_record_v01(
            affected_set_id=source_record.affected_set_id,
            artifact_id=source_record.artifact_id,
            artifact_type=source_record.artifact_type,
            invalidation_reason_class=relation_changes[
                "invalidation_reason_class"
            ],
            triggering_delta_id=source_record.triggering_delta_id,
            triggering_binding_ids=relation_changes.get(
                "triggering_binding_ids", source_record.triggering_binding_ids
            ),
            predecessor_artifact_id=source_record.predecessor_artifact_id,
            g2a_packet_relation=relation_changes["g2a_packet_relation"],
            g2b_reuse_relation=relation_changes["g2b_reuse_relation"],
            g2c_route_relation=relation_changes["g2c_route_relation"],
            root_review_required=True,
            trace_refs=(
                *source_record.trace_refs,
                *relation_changes.get("trace_prefix", ()),
                relation_changes["candidate_id"],
            ),
        )
        report_kwargs = {
            "affected_set_id": source_record.affected_set_id,
            "records": (candidate_record,),
            "ordered_unresolved_artifact_ids": (),
        }
        candidate = g2e.build_invalidation_report_v01(
            **report_kwargs,
        )
        return observed(
            mutated=report_kwargs["records"],
            result=candidate.reason_codes,
            validator=g2e_prefix + "build_invalidation_report_v01",
            call_args=(),
            call_kwargs=report_kwargs,
            locator="kw:records",
            operation_result=candidate,
            metadata=semantic_metadata,
        )
    if suffix == "route_reused_after_bound_source_change":
        if subcase_name == "route_source_revalidation":
            route = _reseal_kernel_artifact(
                inputs["context"].baseline_g2c_route_eligibility_artifact,
                label=subcase_name,
                payload={"g2e5_route_substitution": True},
            )
            candidate = replace(
                inputs["context"], baseline_g2c_route_eligibility_artifact=route
            )
        else:
            foreign_binding = (
                foreign_material["inputs"]["context"]
                .baseline_g2d_execution_bundle.source_binding
            )
            local_bundle = inputs["context"].baseline_g2d_execution_bundle
            substituted_bundle = replace(
                local_bundle,
                source_binding=foreign_binding,
            )
            candidate = replace(
                inputs["context"],
                baseline_g2d_execution_bundle=substituted_bundle,
            )
        return observed(
            mutated=candidate,
            result=g2e.validate_continuous_delta_source_context_v01(candidate),
            validator=g2e_prefix + "validate_continuous_delta_source_context_v01",
            metadata={
                "mutation_path": (
                    "baseline_g2d_execution_bundle.source_binding"
                    if subcase_name == "lower_topology_substitution"
                    else "baseline_g2c_route_eligibility_artifact.payload"
                ),
                "local_route_retained": subcase_name == "lower_topology_substitution",
                "root_kernel_retained": True,
            },
        )
    if suffix == "child_input_topology_mismatch":
        candidate = _reseal_public_carrier(
            bundle.recomputation_plan, source_topology_id="runtime_topology_v02:" + ("0" * 64)
        )
        call_kwargs = _plan_context_kwargs(inputs, execution)
        return observed(
            mutated=candidate,
            result=g2e.validate_selective_recomputation_plan_against_sources_v01(
                candidate, **call_kwargs
            ),
            validator=g2e_prefix + "validate_selective_recomputation_plan_against_sources_v01",
            call_args=(candidate,),
            call_kwargs=call_kwargs,
        )
    if suffix in {"result_report_binding_mismatch", "post_vv_gt_binding_mismatch"}:
        if suffix == "result_report_binding_mismatch":
            candidate = _reseal_public_carrier(
                bundle.recomputation_result,
                recomputed_runtime_report_id=(
                    "g2d_runtime_report_v02:" + ("0" * 64)
                ),
            )
            context_kwargs = _result_context_kwargs(bundle)
            mutated = candidate
            locator = "arg:0"
        else:
            source_input = bundle.final_root_decision_input
            source_plain = root_decision.root_decision_input_to_plain_dict_v01(
                source_input
            )
            changed_post_vv = dict(source_plain["post_vv_bundle"])
            changed_post_vv["provided_evidence_refs"] = [
                "vv_report:g2e5:foreign"
            ]
            changed_gt = dict(source_plain["gt_advisory"])
            changed_gt["advisory_id"] = "gt_report:g2e5:foreign"
            changed_input = root_decision.build_root_decision_input_v01(
                transaction_id=source_input.transaction_id,
                target_root_id=source_input.target_root_id,
                root_review_packet=source_input.root_review_packet,
                post_vv_bundle=changed_post_vv,
                gt_advisory=changed_gt,
                policy_state=source_plain["policy_state"],
                permission_state=source_plain["permission_state"],
                temporal_state=source_plain["temporal_state"],
                conflict_state=source_plain["conflict_state"],
                prior_root_state=source_plain["prior_root_state"],
            )
            candidate = replace(
                bundle,
                final_root_decision_input=changed_input,
            )
            context_kwargs = {}
            mutated = candidate
            locator = "arg:0"
        result = (
            g2e.validate_selective_recomputation_result_against_plan_v01(
                candidate, **context_kwargs
            )
            if suffix == "result_report_binding_mismatch"
            else g2e.validate_continuous_delta_execution_bundle_v01(candidate)
        )
        return observed(
            mutated=mutated,
            result=result,
            validator=(
                g2e_prefix
                + "validate_selective_recomputation_result_against_plan_v01"
                if suffix == "result_report_binding_mismatch"
                else g2e_prefix
                + "validate_continuous_delta_execution_bundle_v01"
            ),
            call_args=(candidate,),
            call_kwargs=context_kwargs,
            locator=locator,
        )
    if suffix == "direct_root_decision_bypass":
        candidate = _non_accept_plan_bundle(bundle)
        return observed(
            mutated=candidate,
            result=g2e.validate_continuous_delta_execution_bundle_v01(candidate),
            validator=g2e_prefix + "validate_continuous_delta_execution_bundle_v01",
        )
    if suffix == "caller_supplied_pass_reason_status":
        source_report = inputs["affected_validation"]
        candidate = _reseal_public_carrier(source_report, status="FAIL_CLOSED")
        return observed(
            mutated=candidate,
            result=g2e.validate_continuous_delta_validation_report_v01(candidate),
            validator=g2e_prefix + "validate_continuous_delta_validation_report_v01",
        )
    if suffix == "object_identity_presented_as_proof":
        candidate = _reseal_public_carrier(
            bundle.preservation_proof, object_identity_used_as_proof=True
        )
        return observed(
            mutated=candidate,
            result=g2e.validate_preservation_proof_v01(candidate),
            validator=g2e_prefix + "validate_preservation_proof_v01",
        )
    if suffix == "repeated_delta_spin":
        candidate = conditional_material["failure_report"]
        if type(candidate) is not g2e.ContinuousDeltaValidationReportV01:
            raise ValueError("g2e5_conditional_report_missing")
        _require_public_pass(
            g2e.validate_continuous_delta_validation_report_v01(candidate),
            "g2e5_conditional_report_invalid",
        )
        if candidate.reason_codes != _reason_tuple(reason):
            raise ValueError(
                "g2e5_repeated_delta_reason_mismatch:"
                + ",".join(candidate.reason_codes)
            )
        observed_reasons = candidate.reason_codes
        case53_metadata = None
        if not constructibility_only:
            graph_projection_result = conditional_material["inputs"][
                "graph_projection_result"
            ]
            case53_metadata = {
                _CASE53_GRAPH_PROJECTION_WITNESS_FIELD: (
                    _semantic_return_witness(
                        graph_projection_result,
                        semantic_projection_memo,
                    )
                )
            }
        return observed(
            mutated=conditional_material["inputs"]["delta"],
            result=observed_reasons,
            validator=g2e_prefix + "run_continuous_delta_runtime_v01",
            outer_ids=(
                conditional_material["inputs"]["delta"].delta_id,
                conditional_material["inputs"]["affected"].affected_set_id,
                candidate.validation_report_id,
            ),
            call_args=(),
            call_kwargs=conditional_material["semantic_call_kwargs"],
            locator="kw:delta",
            operation_result=conditional_material["semantic_call_result"],
            metadata=case53_metadata,
        )
    if suffix.startswith("nonzero_"):
        field_name = axis
        if suffix == "nonzero_authority":
            candidate = _reseal_public_carrier(inputs["delta"], authority_created=True)
            result = g2e.validate_world_state_delta_v01(candidate)
            validator = g2e_prefix + "validate_world_state_delta_v01"
        else:
            candidate = _reseal_public_carrier(
                bundle.recomputation_result, **{field_name: 1}
            )
            result = g2e.validate_selective_recomputation_result_v01(candidate)
            validator = g2e_prefix + "validate_selective_recomputation_result_v01"
        return observed(mutated=candidate, result=result, validator=validator)
    if suffix in {
        "missing_changed_binding_carrier",
        "unreferenced_changed_binding_injection",
        "source_binding_set_mismatch",
        "dependency_edge_carrier_mismatch",
        "baseline_observed_source_pair_substitution",
    }:
        changes: dict[str, object]
        mutated: object
        if suffix == "missing_changed_binding_carrier":
            changes = {"changed_field_bindings": ()}
            mutated = inputs["changed_field"]
        elif suffix == "unreferenced_changed_binding_injection":
            injected = _reseal_public_carrier(
                inputs["changed_field"], json_pointer="/g2e5_unreferenced"
            )
            changes = {"changed_field_bindings": (inputs["changed_field"], injected)}
            mutated = injected
        elif suffix == "source_binding_set_mismatch":
            foreign_binding = foreign_material["inputs"]["source_binding"]
            changes = {"source_bindings": (foreign_binding,)}
            mutated = changes["source_bindings"]
        elif suffix == "dependency_edge_carrier_mismatch":
            changes = {"dependency_edges": tuple(reversed(inputs["dependency_edges"]))}
            mutated = changes["dependency_edges"]
        else:
            changes = {"observed_source_artifacts": tuple(reversed(inputs["observed"]))}
            mutated = changes["observed_source_artifacts"]
        changed_keyword = next(iter(changes))
        call_kwargs = _affected_context_kwargs(inputs, **changes)
        return observed(
            mutated=mutated,
            result=g2e.validate_affected_set_against_graph_v01(
                inputs["affected"], **call_kwargs
            ),
            validator=g2e_prefix + "validate_affected_set_against_graph_v01",
            call_args=(inputs["affected"],),
            call_kwargs=call_kwargs,
            locator="kw:" + changed_keyword,
        )
    if suffix == "dependency_fingerprint_before_after_swap":
        call_kwargs = {
            "profile": inputs["fingerprint_profile"],
            "graph": inputs["graph"],
            "dependency_edges": inputs["dependency_edges"],
            "source_artifacts": inputs["observed"],
            "policy_version": inputs["delta"].observed_policy_version,
            "schema_versions": inputs["delta"].observed_schema_versions,
            "source_history_hash": inputs["delta"].observed_source_history_hash,
        }
        result = g2e.validate_dependency_fingerprint_against_sources_v01(
            inputs["delta"].dependency_fingerprint_before,
            **call_kwargs,
        )
        return observed(
            mutated=call_kwargs["source_artifacts"],
            result=result,
            validator=g2e_prefix + "validate_dependency_fingerprint_against_sources_v01",
            call_args=(inputs["delta"].dependency_fingerprint_before,),
            call_kwargs=call_kwargs,
            locator="kw:source_artifacts",
        )
    if suffix == "selective_execution_carrier_omission":
        if subcase_name == "pre_execution_carrier":
            candidate = _reseal_public_carrier(
                bundle.recomputation_plan, delta_id="g2e_world_state_delta_v01:" + ("0" * 64)
            )
            call_kwargs = _plan_context_kwargs(inputs, execution)
            result = g2e.validate_selective_recomputation_plan_against_sources_v01(
                candidate, **call_kwargs
            )
            locator = "arg:0"
        elif subcase_name == "post_execution_bundle":
            candidate = replace(bundle, recomputed_g2d_execution_bundle=None)
            result = g2e.validate_continuous_delta_execution_bundle_v01(candidate)
            call_kwargs = {}
            locator = "arg:0"
        elif subcase_name == "post_execution_partial_failure":
            candidate = _reseal_public_carrier(
                bundle.recomputation_result,
                ordered_partial_failure_ids=(
                    "g2d_partial_failure_v02:" + ("1" * 64),
                    "g2d_partial_failure_v02:" + ("2" * 64),
                ),
            )
            call_kwargs = _result_context_kwargs(bundle)
            result = g2e.validate_selective_recomputation_result_against_plan_v01(
                candidate, **call_kwargs
            )
            locator = "arg:0"
        elif subcase_name == "post_execution_recomputed_binding":
            candidate = bundle.recomputation_result
            call_kwargs = _result_context_kwargs(
                bundle,
                recomputed_bindings=(),
            )
            result = g2e.validate_selective_recomputation_result_against_plan_v01(
                candidate,
                **call_kwargs,
            )
            locator = "kw:recomputed_bindings"
        else:
            candidate = bundle.recomputation_result
            call_kwargs = _result_context_kwargs(
                bundle,
                g2e_causal_consumption_refs=(),
            )
            result = g2e.validate_selective_recomputation_result_against_plan_v01(
                candidate,
                **call_kwargs,
            )
            locator = "kw:g2e_causal_consumption_refs"
        return observed(
            mutated=candidate,
            result=result,
            validator=(
                g2e_prefix + "validate_selective_recomputation_plan_against_sources_v01"
                if subcase_name == "pre_execution_carrier"
                else g2e_prefix + "validate_continuous_delta_execution_bundle_v01"
                if type(candidate) is g2e.ContinuousDeltaExecutionBundleV01
                else g2e_prefix + "validate_selective_recomputation_result_against_plan_v01"
            ),
            call_args=(candidate,),
            call_kwargs=call_kwargs,
            locator=locator,
        )
    if suffix == "recomputed_g2d_result_report_ref_substitution":
        if subcase_name in {"g2d_cell_result_ref", "g2d_runtime_report_ref"}:
            field_name = subcase_name
            binding = bundle.recomputed_bindings[0]
            candidate_binding = _reseal_public_carrier(
                binding, **{field_name: "g2e5:foreign:" + field_name}
            )
            candidate = bundle.recomputation_result
            call_kwargs = _result_context_kwargs(
                bundle,
                recomputed_bindings=(
                    candidate_binding,
                    *bundle.recomputed_bindings[1:],
                ),
            )
            result = g2e.validate_selective_recomputation_result_against_plan_v01(
                candidate, **call_kwargs
            )
            mutated = call_kwargs["recomputed_bindings"]
            locator = "kw:recomputed_bindings"
        else:
            changes = (
                {"preservation_proof_id": "g2e_preservation_proof_v01:" + ("0" * 64)}
                if subcase_name == "preservation_proof_ref"
                else {"ordered_partial_failure_ids": ("g2d_partial_failure_v02:foreign",)}
            )
            mutated = _reseal_public_carrier(bundle.recomputation_result, **changes)
            call_kwargs = _result_context_kwargs(bundle)
            result = g2e.validate_selective_recomputation_result_against_plan_v01(
                mutated, **call_kwargs
            )
            locator = "arg:0"
        return observed(
            mutated=mutated,
            result=result,
            validator=g2e_prefix + "validate_selective_recomputation_result_against_plan_v01",
            call_args=(candidate if subcase_name in {"g2d_cell_result_ref", "g2d_runtime_report_ref"} else mutated,),
            call_kwargs=call_kwargs,
            locator=locator,
        )
    if suffix == "unsupported_sequential_delta":
        candidate = _reseal_public_carrier(inputs["delta"], delta_sequence=2)
        return observed(
            mutated=candidate,
            result=g2e.validate_world_state_delta_v01(candidate),
            validator=g2e_prefix + "validate_world_state_delta_v01",
        )
    if suffix == "root_acceptance_outcome_forgery":
        if subcase_name == "forged_accept":
            candidate = _non_accept_final_bundle(bundle)
            mutated = candidate.final_root_decision_result
        else:
            field_name = {
                "nonzero_permission": "permission_created",
                "nonzero_final_output": "final_output_created",
                "nonzero_effect": "effect_requested",
            }[subcase_name]
            payload = kernel_artifact_to_plain_dict_v01(
                bundle.final_root_decision_artifact
            )["payload"]
            mutated = _reseal_kernel_artifact(
                bundle.final_root_decision_artifact,
                label="root_acceptance_outcome_forgery:" + subcase_name,
                payload={**payload, field_name: True},
            )
            candidate = replace(
                bundle, final_root_decision_artifact=mutated
            )
        return observed(
            mutated=candidate,
            result=g2e.validate_continuous_delta_execution_bundle_v01(candidate),
            validator=g2e_prefix + "validate_continuous_delta_execution_bundle_v01",
            call_args=(candidate,),
        )
    if suffix in {
        "plan_root_review_carrier_substitution",
        "final_root_review_carrier_substitution",
    }:
        if suffix == "plan_root_review_carrier_substitution":
            if subcase_name == "selected_carrier":
                candidate = _reseal_public_carrier(
                    bundle.recomputation_plan,
                    accepted_scope_ref="scope:g2e5:plan-selected-foreign",
                )
                call_kwargs = _plan_context_kwargs(inputs, execution)
                result = (
                    g2e.validate_selective_recomputation_plan_against_sources_v01(
                        candidate, **call_kwargs
                    )
                )
                return observed(
                    mutated=candidate,
                    result=result,
                    validator=(
                        g2e_prefix
                        + "validate_selective_recomputation_plan_against_sources_v01"
                    ),
                    call_args=(candidate,),
                    call_kwargs=call_kwargs,
                )
            if subcase_name == "root_input":
                candidate = replace(
                    bundle,
                    plan_root_decision_input=bundle.final_root_decision_input,
                )
            elif subcase_name == "root_result":
                candidate = replace(
                    bundle,
                    plan_root_decision_result=bundle.final_root_decision_result,
                )
            elif subcase_name == "prior_decision":
                candidate = replace(
                    bundle,
                    plan_root_decision_input=(
                        _root_input_with_prior_decision_mutation(
                            bundle.plan_root_decision_input
                        )
                    ),
                )
            else:
                plan_artifact = bundle.plan_root_decision_artifact
                if subcase_name == "target_root":
                    changed_artifact = _reseal_kernel_artifact(
                        plan_artifact,
                        label="plan-root:target-root",
                        owner_root_id="root:g2e5:plan-foreign",
                    )
                elif subcase_name == "transaction":
                    changed_artifact = _reseal_kernel_artifact(
                        plan_artifact,
                        label="plan-root:transaction",
                        transaction_id="transaction:g2e5:plan-foreign",
                    )
                else:
                    changed_artifact = _reseal_kernel_artifact(
                        plan_artifact,
                        label="plan-root:artifact-relation",
                        trace_refs=(
                            *plan_artifact.trace_refs,
                            "trace:g2e5:plan-root-artifact-relation",
                        ),
                    )
                candidate = replace(
                    bundle,
                    plan_root_decision_artifact=changed_artifact,
                )
        else:
            if subcase_name in {
                "selected_carrier",
                "g2d_report",
                "preservation_proof",
            }:
                result_candidate = bundle.recomputation_result
                result_kwargs = _result_context_kwargs(bundle)
                if subcase_name == "selected_carrier":
                    result_candidate = _reseal_public_carrier(
                        result_candidate,
                        recomputation_plan_id=(
                            "g2e_selective_recomputation_plan_v01:"
                            + ("0" * 64)
                        ),
                    )
                    mutated = result_candidate
                    locator = "arg:0"
                elif subcase_name == "g2d_report":
                    source_g2d = bundle.recomputed_g2d_execution_bundle
                    changed_runtime_report = replace(
                        source_g2d.runtime_report,
                        report_id="g2d_runtime_report_v02:" + ("1" * 64),
                    )
                    mutated = replace(
                        source_g2d,
                        runtime_report=changed_runtime_report,
                    )
                    result_kwargs["recomputed_g2d_execution_bundle"] = mutated
                    locator = "kw:recomputed_g2d_execution_bundle"
                else:
                    mutated = _reseal_preservation_proof(
                        bundle.preservation_proof,
                        baseline_graph_id=(
                            bundle.preservation_proof.baseline_graph_id
                            + ":final-relation"
                        ),
                    )
                    result_kwargs["preservation_proof"] = mutated
                    locator = "kw:preservation_proof"
                result = (
                    g2e.validate_selective_recomputation_result_against_plan_v01(
                        result_candidate,
                        **result_kwargs,
                    )
                )
                return observed(
                    mutated=mutated,
                    result=result,
                    validator=(
                        g2e_prefix
                        + "validate_selective_recomputation_result_against_plan_v01"
                    ),
                    call_args=(result_candidate,),
                    call_kwargs=result_kwargs,
                    locator=locator,
                )
            if subcase_name == "root_input":
                candidate = replace(
                    bundle,
                    final_root_decision_input=bundle.plan_root_decision_input,
                )
            elif subcase_name == "root_result":
                candidate = replace(
                    bundle,
                    final_root_decision_result=bundle.plan_root_decision_result,
                )
            elif subcase_name == "prior_decision":
                candidate = replace(
                    bundle,
                    final_root_decision_input=(
                        _root_input_with_prior_decision_mutation(
                            bundle.final_root_decision_input
                        )
                    ),
                )
            else:
                final_artifact = bundle.final_root_decision_artifact
                if subcase_name == "target_root":
                    changed_artifact = _reseal_kernel_artifact(
                        final_artifact,
                        label="final-root:target-root",
                        owner_root_id="root:g2e5:final-foreign",
                    )
                elif subcase_name == "transaction":
                    changed_artifact = _reseal_kernel_artifact(
                        final_artifact,
                        label="final-root:transaction",
                        transaction_id="transaction:g2e5:final-foreign",
                    )
                else:
                    changed_artifact = _reseal_kernel_artifact(
                        final_artifact,
                        label="final-root:artifact-relation",
                        trace_refs=(
                            *final_artifact.trace_refs,
                            "trace:g2e5:final-root-artifact-relation",
                        ),
                    )
                candidate = replace(
                    bundle,
                    final_root_decision_artifact=changed_artifact,
                )
        return observed(
            mutated=candidate,
            result=g2e.validate_continuous_delta_execution_bundle_v01(candidate),
            validator=g2e_prefix + "validate_continuous_delta_execution_bundle_v01",
            call_args=(candidate,),
        )
    raise ValueError("g2e5_negative_recipe_missing:" + suffix)


def _build_negative_case(
    *,
    row: tuple[str, str, str | tuple[str, ...]],
    baseline_report_id: str,
    domain_id: str,
    valid_material: dict[str, object],
    foreign_material: dict[str, object],
    conditional_material: dict[str, object],
    semantic_projection_memo: dict[
        int, tuple[object, dict[str, object]]
    ],
) -> ContinuousDeltaRuntimeG2ECaseResultV01:
    suffix, axis, reason = row
    case_id = f"g2e_case:negative:{suffix}:v01"
    bundle = valid_material["execution"]["bundle"]
    if type(bundle) is not g2e.ContinuousDeltaExecutionBundleV01:
        raise ValueError("g2e5_negative_bundle_basis_missing")
    matrix_suffixes = {
        "transition_rule_eleven_field_substitution",
        "transition_rule_order_or_terminal_path_forgery",
        "abi_projection_profile_substitution",
        "abi_parent_trace_or_root_artifact_substitution",
        "identity_prefix_or_domain_collision",
    }
    subcases = tuple(
        _matrix_negative_subcase(
            case_id=case_id,
            suffix=suffix,
            subcase_name=name,
            axis=subcase_axis,
            reason=subcase_reason,
            bundle=bundle,
            semantic_projection_memo=semantic_projection_memo,
        )
        if suffix in matrix_suffixes
        else _ordinary_negative_subcase(
            case_id=case_id,
            suffix=suffix,
            subcase_name=name,
            axis=subcase_axis,
            reason=subcase_reason,
            valid_material=valid_material,
            foreign_material=foreign_material,
            conditional_material=conditional_material,
            semantic_projection_memo=semantic_projection_memo,
        )
        for name, subcase_axis, subcase_reason in _negative_subcase_specs(
            suffix, axis, reason
        )
    )
    observed = tuple(dict.fromkeys(
        reason_code
        for subcase in subcases
        for reason_code in subcase.observed_reason_codes
    ))
    expected = tuple(dict.fromkeys(
        reason_code
        for subcase in subcases
        for reason_code in subcase.expected_reason_codes
    ))
    observed_outcome = (
        "FAIL_CLOSED"
        if subcases
        and all(
            subcase.final_status == "PASS" and subcase.observed_reason_codes
            for subcase in subcases
        )
        else "INVALID_NEGATIVE_EVIDENCE"
    )
    observed_counters = _observed_zero_counters(
        bundle.recomputation_result,
        bundle.runtime_trace,
        bundle.runtime_report,
        bundle.plan_root_decision_result,
        bundle.final_root_decision_result,
    )
    evidence = {
        "case_id": case_id,
        "domain_id": domain_id,
        "baseline_runtime_report_id": baseline_report_id,
        "subcase_ids": [subcase.subcase_id for subcase in subcases],
        "subcase_evidence_sha256": [
            subcase.evidence_sha256 for subcase in subcases
        ],
        "observed_reason_codes": observed,
        "expected_reason_codes": expected,
        "observed_outcome": observed_outcome,
        "negative_case_accepted_as_success": observed_outcome != "FAIL_CLOSED",
        "authority_created": observed_counters["authority_created_count"] != 0,
        "real_world_effects_count": observed_counters["real_world_effects_count"],
    }
    evidence_json = _canonical_json_text(evidence)
    evidence_sha = _sha256_domain(CASE_EVIDENCE_DOMAIN, evidence)
    return ContinuousDeltaRuntimeG2ECaseResultV01(
        case_id=case_id,
        case_class="NEGATIVE",
        domain_id=domain_id,
        expected_outcome="FAIL_CLOSED",
        observed_outcome=observed_outcome,
        baseline_runtime_report_id=baseline_report_id,
        delta_id=None,
        affected_set_id=None,
        invalidation_report_id=None,
        recomputation_plan_id=None,
        recomputation_result_id=None,
        continuous_delta_runtime_report_id=None,
        ordered_changed_ids=(),
        ordered_directly_affected_ids=(),
        ordered_transitively_affected_ids=(),
        ordered_invalidated_ids=(),
        ordered_recomputed_ids=(),
        ordered_preserved_ids=(),
        ordered_unresolved_or_blocked_ids=(axis,),
        ordered_root_review_ids=(
            bundle.plan_root_decision_result.decision_id,
            bundle.final_root_decision_result.decision_id,
        ),
        subcase_results=subcases,
        expected_reason_codes=expected,
        observed_reason_codes=observed,
        evidence_refs=tuple(subcase.validation_report_id for subcase in subcases),
        evidence_material_json=evidence_json,
        evidence_sha256=evidence_sha,
        **observed_counters,
        final_status="PASS",
        reason_codes=(),
    )


def _case_evidence_valid(case: ContinuousDeltaRuntimeG2ECaseResultV01) -> bool:
    try:
        material = json.loads(case.evidence_material_json)
    except (TypeError, ValueError, json.JSONDecodeError):
        return False
    if _canonical_json_text(material) != case.evidence_material_json:
        return False
    if _sha256_domain(CASE_EVIDENCE_DOMAIN, material) != case.evidence_sha256:
        return False
    for subcase in case.subcase_results:
        try:
            subcase_material = json.loads(subcase.evidence_material_json)
        except (TypeError, ValueError, json.JSONDecodeError):
            return False
        if (
            _canonical_json_text(subcase_material) != subcase.evidence_material_json
            or _sha256_domain(SUBCASE_EVIDENCE_DOMAIN, subcase_material)
            != subcase.evidence_sha256
            or subcase.expected_reason_codes != subcase.observed_reason_codes
            or subcase.final_status != "PASS"
        ):
            return False
    return True


def _zero_counter_values(value: object) -> tuple[int, ...]:
    names = (
        "provider_calls",
        "model_calls",
        "network_calls",
        "connector_calls",
        "external_drs_calls",
        "action_commit_packets_created",
        "permissions_created",
        "receipts_created",
        "final_outputs_created",
        "drs_writes",
        "authority_created_count",
        "real_world_effects_count",
    )
    return tuple(getattr(value, name) for name in names)


def _sealed_material(
    *,
    domain_order: tuple[str, ...],
    case_results: tuple[ContinuousDeltaRuntimeG2ECaseResultV01, ...],
    constructive_case_count: int,
    negative_case_count: int,
    total_case_count: int,
    accepted_baseline_bundle_count: int,
    explicit_public_g2d_baseline_call_count: int,
    source_collectors_replayed: bool,
    source_evidence_mode: str,
    final_status: str,
    reason_codes: tuple[str, ...],
) -> dict[str, object]:
    baseline_ids = tuple(
        dict.fromkeys(
            case.baseline_runtime_report_id
            for case in case_results
            if case.baseline_runtime_report_id is not None
        )
    )
    return {
        "domain_order": domain_order,
        "baseline_runtime_report_ids": baseline_ids,
        "case_order": tuple(case.case_id for case in case_results),
        "case_evidence_sha256": tuple(case.evidence_sha256 for case in case_results),
        "constructive_case_count": constructive_case_count,
        "negative_case_count": negative_case_count,
        "total_case_count": total_case_count,
        "accepted_baseline_bundle_count": accepted_baseline_bundle_count,
        "explicit_public_g2d_baseline_call_count": (
            explicit_public_g2d_baseline_call_count
        ),
        "source_collectors_replayed": source_collectors_replayed,
        "source_evidence_mode": source_evidence_mode,
        "zero_counters": tuple(
            sum(getattr(case, name) for case in case_results)
            for name in _ZERO_COUNTER_FIELDS
        ),
        "final_status": final_status,
        "reason_codes": reason_codes,
    }


def _report_identity_material(
    report: ContinuousDeltaRuntimeG2EReportV01,
) -> dict[str, object]:
    plain = continuous_delta_runtime_g2_e_report_to_plain_data_v01(
        report, validate=False
    )
    plain.pop("report_id")
    return plain


def _build_two_domain_baseline_material_v01(
    *,
    semantic_projection_memo: dict[int, tuple[object, dict[str, object]]],
    bind_public_return_evidence: bool,
) -> tuple[
    dict[str, g2d.FractalRuntimeExecutionBundleV02],
    dict[str, dict[str, object]],
]:
    baselines: dict[str, g2d.FractalRuntimeExecutionBundleV02] = {}
    families: dict[str, dict[str, object]] = {}
    for domain_id in DOMAIN_ORDER:
        root_id = (
            "root:mock_airline_al"
            if domain_id == DOMAIN_ORDER[0]
            else "root:g2a5:supplier"
        )
        g2b_family = _build_g2b_family(domain_id, root_id)
        source_family = _build_g2d_source_context(domain_id, g2b_family)
        baseline_result = g2d.run_fractal_runtime_v02(source_family["source"])
        bundle, report = baseline_result
        if bundle is None or report.status != "PASS":
            raise ValueError("g2e5_public_baseline_failed")
        _require_public_pass(
            g2d.validate_fractal_runtime_execution_bundle_v02(bundle),
            "g2e5_public_baseline_invalid",
        )
        source_family["baseline_public_return"] = (
            {
                "runtime_report_id": bundle.runtime_report.report_id,
                "bundle": _semantic_return_binding(
                    bundle, semantic_projection_memo
                ),
                "validation_report": _semantic_return_binding(
                    report, semantic_projection_memo
                ),
                "return_tuple": _semantic_return_binding(
                    baseline_result, semantic_projection_memo
                ),
            }
            if bind_public_return_evidence
            else None
        )
        source_family["baseline_public_result"] = baseline_result
        g2a_family = _build_g2a_family(
            domain_id=domain_id,
            root_id=root_id,
            transaction_id=source_family["transaction_id"],
        )
        baselines[domain_id] = bundle
        families[domain_id] = {
            "source": source_family,
            "g2a": g2a_family,
            "g2b": g2b_family,
        }
    return baselines, families


def _negative_constructibility_observations_v01(
    progress: object | None = None,
) -> tuple[
    _NegativeConstructibilityObservationV01, ...
]:
    semantic_projection_memo: dict[
        int, tuple[object, dict[str, object]]
    ] = {}
    baselines, families = _build_two_domain_baseline_material_v01(
        semantic_projection_memo=semantic_projection_memo,
        bind_public_return_evidence=False,
    )
    source_cases = (
        (CONSTRUCTIVE_CASE_ORDER[0], DOMAIN_ORDER[0]),
        (CONSTRUCTIVE_CASE_ORDER[5], DOMAIN_ORDER[1]),
    )
    materials: list[dict[str, object]] = []
    for source_index, (case_id, domain_id) in enumerate(source_cases):
        family = families[domain_id]
        inputs = _build_case_inputs(
            case_id=case_id,
            domain_id=domain_id,
            baseline=baselines[domain_id],
            source_family=family["source"],
            g2a=family["g2a"],
            g2b=family["g2b"],
        )
        material: dict[str, object] = {"inputs": inputs}
        if source_index == 0:
            material["execution"] = _execute_case_inputs(inputs)
        materials.append(material)
    valid_material, foreign_material = materials
    conditional_inputs = _build_case_inputs(
        case_id="g2e_case:negative:repeated_delta_spin:v01",
        domain_id=DOMAIN_ORDER[0],
        baseline=baselines[DOMAIN_ORDER[0]],
        source_family=families[DOMAIN_ORDER[0]]["source"],
        g2a=families[DOMAIN_ORDER[0]]["g2a"],
        g2b=families[DOMAIN_ORDER[0]]["g2b"],
    )
    conditional_material = _execute_conditional_negative_inputs(
        conditional_inputs
    )
    matrix_suffixes = {
        "transition_rule_eleven_field_substitution",
        "transition_rule_order_or_terminal_path_forgery",
        "abi_projection_profile_substitution",
        "abi_parent_trace_or_root_artifact_substitution",
        "identity_prefix_or_domain_collision",
    }
    bundle = valid_material["execution"]["bundle"]
    if type(bundle) is not g2e.ContinuousDeltaExecutionBundleV01:
        raise ValueError("g2e5_negative_bundle_basis_missing")
    observations: list[_NegativeConstructibilityObservationV01] = []
    for suffix, axis, reason in _NEGATIVE_ROWS:
        case_id = "g2e_case:negative:" + suffix + ":v01"
        for subcase_name, subcase_axis, subcase_reason in _negative_subcase_specs(
            suffix, axis, reason
        ):
            observation = (
                _matrix_negative_subcase(
                    case_id=case_id,
                    suffix=suffix,
                    subcase_name=subcase_name,
                    axis=subcase_axis,
                    reason=subcase_reason,
                    bundle=bundle,
                    semantic_projection_memo=semantic_projection_memo,
                    constructibility_only=True,
                )
                if suffix in matrix_suffixes
                else _ordinary_negative_subcase(
                    case_id=case_id,
                    suffix=suffix,
                    subcase_name=subcase_name,
                    axis=subcase_axis,
                    reason=subcase_reason,
                    valid_material=valid_material,
                    foreign_material=foreign_material,
                    conditional_material=conditional_material,
                    semantic_projection_memo=semantic_projection_memo,
                    constructibility_only=True,
                )
            )
            if type(observation) is not _NegativeConstructibilityObservationV01:
                raise ValueError("g2e5_negative_preflight_observation_invalid")
            observations.append(observation)
            if progress is not None:
                if not callable(progress):
                    raise ValueError("g2e5_negative_preflight_progress_invalid")
                progress(observation)
    return tuple(observations)


def collect_continuous_delta_runtime_g2_e_v01() -> ContinuousDeltaRuntimeG2EReportV01:
    semantic_projection_memo: dict[
        int, tuple[object, dict[str, object]]
    ] = {}
    baselines, families = _build_two_domain_baseline_material_v01(
        semantic_projection_memo=semantic_projection_memo,
        bind_public_return_evidence=True,
    )
    constructive_results: list[ContinuousDeltaRuntimeG2ECaseResultV01] = []
    constructive_material: list[dict[str, object]] = []
    for index, case_id in enumerate(CONSTRUCTIVE_CASE_ORDER):
        domain_id = DOMAIN_ORDER[0] if index < 5 else DOMAIN_ORDER[1]
        family = families[domain_id]
        inputs = _build_case_inputs(
            case_id=case_id,
            domain_id=domain_id,
            baseline=baselines[domain_id],
            source_family=family["source"],
            g2a=family["g2a"],
            g2b=family["g2b"],
        )
        execution = _execute_case_inputs(inputs)
        repeat_execution = (
            _execute_case_inputs(inputs)
            if case_id.endswith("repeat_idempotent:v01")
            else None
        )
        constructive_results.append(
            _constructive_case_result(
                case_id=case_id,
                inputs=inputs,
                execution=execution,
                repeat_execution=repeat_execution,
                semantic_projection_memo=semantic_projection_memo,
            )
        )
        constructive_material.append(
            {
                "inputs": inputs,
                "execution": execution,
                "repeat_execution": repeat_execution,
            }
        )
    constructive = tuple(constructive_results)
    valid_negative_material = constructive_material[0]
    foreign_negative_material = constructive_material[5]
    if any(
        type(material["execution"]["bundle"])
        is not g2e.ContinuousDeltaExecutionBundleV01
        for material in (valid_negative_material, foreign_negative_material)
    ):
        raise ValueError("g2e5_negative_bundle_basis_missing")
    conditional_inputs = _build_case_inputs(
        case_id="g2e_case:negative:repeated_delta_spin:v01",
        domain_id=DOMAIN_ORDER[0],
        baseline=baselines[DOMAIN_ORDER[0]],
        source_family=families[DOMAIN_ORDER[0]]["source"],
        g2a=families[DOMAIN_ORDER[0]]["g2a"],
        g2b=families[DOMAIN_ORDER[0]]["g2b"],
    )
    conditional_negative_material = _execute_conditional_negative_inputs(
        conditional_inputs
    )
    negative = tuple(
        _build_negative_case(
            row=row,
            baseline_report_id=baselines[DOMAIN_ORDER[0]].runtime_report.report_id,
            domain_id=DOMAIN_ORDER[0],
            valid_material=valid_negative_material,
            foreign_material=foreign_negative_material,
            conditional_material=conditional_negative_material,
            semantic_projection_memo=semantic_projection_memo,
        )
        for row in _NEGATIVE_ROWS
    )
    case_results = constructive + negative
    aggregate_counters = {
        name: sum(getattr(case, name) for case in case_results)
        for name in _ZERO_COUNTER_FIELDS
    }
    if any(aggregate_counters.values()):
        raise ValueError("g2e5_zero_operation_boundary_violated")
    sealed = _sealed_material(
        domain_order=DOMAIN_ORDER,
        case_results=case_results,
        constructive_case_count=len(constructive),
        negative_case_count=len(negative),
        total_case_count=len(case_results),
        accepted_baseline_bundle_count=len(baselines),
        explicit_public_g2d_baseline_call_count=len(baselines),
        source_collectors_replayed=False,
        source_evidence_mode="public_builder_constructed_baselines",
        final_status="PASS",
        reason_codes=(),
    )
    provisional = ContinuousDeltaRuntimeG2EReportV01(
        report_version=REPORT_VERSION,
        report_id=REPORT_ID_PREFIX + ("0" * 64),
        profile_id=PROFILE_ID,
        domain_order=DOMAIN_ORDER,
        case_order=CASE_ORDER,
        case_results=case_results,
        constructive_case_count=10,
        negative_case_count=90,
        total_case_count=100,
        accepted_baseline_bundle_count=2,
        explicit_public_g2d_baseline_call_count=2,
        source_collectors_replayed=False,
        source_evidence_mode="public_builder_constructed_baselines",
        sealed_evidence_sha256=_sha256_domain(SEALED_EVIDENCE_DOMAIN, sealed),
        **aggregate_counters,
        final_status="PASS",
        reason_codes=(),
    )
    report_id = REPORT_ID_PREFIX + _sha256_domain(
        REPORT_ID_DOMAIN, _report_identity_material(provisional)
    )
    result = replace(provisional, report_id=report_id)
    validate_continuous_delta_runtime_g2_e_report_v01(result)
    return result


def validate_continuous_delta_runtime_g2_e_report_v01(
    value: object,
) -> ContinuousDeltaRuntimeG2EReportV01:
    if type(value) is not ContinuousDeltaRuntimeG2EReportV01:
        raise ValueError("g2e5_report_type_invalid")
    expected_report_fields = (
        "report_version", "report_id", "profile_id", "domain_order", "case_order",
        "case_results", "constructive_case_count", "negative_case_count",
        "total_case_count", "accepted_baseline_bundle_count",
        "explicit_public_g2d_baseline_call_count", "source_collectors_replayed",
        "source_evidence_mode", "sealed_evidence_sha256", "provider_calls",
        "model_calls", "network_calls", "connector_calls", "external_drs_calls",
        "action_commit_packets_created", "permissions_created", "receipts_created",
        "final_outputs_created", "drs_writes", "authority_created_count",
        "real_world_effects_count", "final_status", "reason_codes",
    )
    if tuple(field.name for field in fields(type(value))) != expected_report_fields:
        raise ValueError("g2e5_report_geometry_invalid")
    if (
        value.report_version != REPORT_VERSION
        or value.profile_id != PROFILE_ID
        or value.domain_order != DOMAIN_ORDER
        or value.case_order != CASE_ORDER
        or tuple(case.case_id for case in value.case_results) != CASE_ORDER
        or len(set(value.case_order)) != len(value.case_order)
        or value.constructive_case_count != 10
        or value.negative_case_count != 90
        or value.total_case_count != 100
        or len(value.case_results) != 100
        or value.accepted_baseline_bundle_count != 2
        or value.explicit_public_g2d_baseline_call_count != 2
        or value.source_collectors_replayed is not False
        or value.source_evidence_mode != "public_builder_constructed_baselines"
        or value.final_status != "PASS"
        or value.reason_codes != ()
        or any(_zero_counter_values(value))
    ):
        raise ValueError("g2e5_report_contract_invalid")
    constructive = value.case_results[:10]
    negative = value.case_results[10:]
    if (
        any(type(case) is not ContinuousDeltaRuntimeG2ECaseResultV01 for case in value.case_results)
        or any(case.case_class != "CONSTRUCTIVE" for case in constructive)
        or any(case.case_class != "NEGATIVE" for case in negative)
        or tuple(case.domain_id for case in constructive[:5]) != (DOMAIN_ORDER[0],) * 5
        or tuple(case.domain_id for case in constructive[5:]) != (DOMAIN_ORDER[1],) * 5
    ):
        raise ValueError("g2e5_case_geometry_invalid")
    baseline_ids = tuple(
        dict.fromkeys(case.baseline_runtime_report_id for case in constructive)
    )
    if len(baseline_ids) != 2:
        raise ValueError("g2e5_baseline_geometry_invalid")
    constructive_material = tuple(
        json.loads(case.evidence_material_json) for case in constructive
    )
    baseline_return_by_domain: dict[str, dict[str, object]] = {}
    for case, material in zip(
        constructive, constructive_material, strict=True
    ):
        baseline_return = material.get("baseline_public_return")
        if type(baseline_return) is not dict:
            raise ValueError("g2e5_baseline_return_evidence_invalid")
        if baseline_return.get("runtime_report_id") != case.baseline_runtime_report_id:
            raise ValueError("g2e5_baseline_return_evidence_invalid")
        for key in ("bundle", "validation_report", "return_tuple"):
            binding = baseline_return.get(key)
            if (
                type(binding) is not dict
                or type(binding.get("sha256")) is not str
                or len(binding["sha256"]) != 64
                or not set(binding["sha256"]) <= set("0123456789abcdef")
                or type(binding.get("byte_length")) is not int
                or binding["byte_length"] <= 0
            ):
                raise ValueError("g2e5_baseline_return_evidence_invalid")
        prior = baseline_return_by_domain.setdefault(
            case.domain_id, baseline_return
        )
        if prior != baseline_return:
            raise ValueError("g2e5_baseline_return_domain_mismatch")
    if (
        set(baseline_return_by_domain) != set(DOMAIN_ORDER)
        or len(
            {
                row["return_tuple"]["sha256"]
                for row in baseline_return_by_domain.values()
            }
        )
        != 2
    ):
        raise ValueError("g2e5_baseline_return_geometry_invalid")

    def valid_binding(binding: object) -> bool:
        return (
            type(binding) is dict
            and set(binding) == {"sha256", "byte_length"}
            and type(binding.get("sha256")) is str
            and len(binding["sha256"]) == 64
            and set(binding["sha256"]) <= set("0123456789abcdef")
            and type(binding.get("byte_length")) is int
            and binding["byte_length"] > 0
        )

    def valid_witness(witness: object) -> bool:
        return _semantic_return_witness_valid_v01(witness)

    def projection_binding(value: object) -> dict[str, object]:
        payload = json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        ).encode("ascii")
        return {
            "sha256": hashlib.sha256(payload).hexdigest(),
            "byte_length": len(payload),
        }

    def projected_fields(value: object) -> dict[str, object] | None:
        if (
            type(value) is not dict
            or value.get("kind") != "dataclass"
            or type(value.get("fields")) is not list
        ):
            return None
        rows = value["fields"]
        if any(
            type(row) is not list
            or len(row) != 2
            or type(row[0]) is not str
            for row in rows
        ):
            return None
        result = {row[0]: row[1] for row in rows}
        return result if len(result) == len(rows) else None

    def projected_string(value: object) -> str | None:
        if (
            type(value) is dict
            and value.get("kind") == "str"
            and type(value.get("value")) is str
        ):
            return value["value"]
        return None

    projection_keys = {
        "graph_basis_sha256",
        "ordered_dependency_edge_ids",
        "return_witness",
        "dependency_edges_binding",
    }
    graph_keys = {
        "graph_id",
        "graph_basis_sha256",
        "ordered_edge_ids",
        "graph_witness",
    }
    affected_keys = {
        "affected_request_id",
        "request_graph_id",
        "request_delta_id",
        "kwargs_graph_id",
        "kwargs_delta_id",
        "returned_affected_request_id",
        "returned_affected_set_id",
        "returned_graph_id",
        "returned_delta_id",
        "request_witness",
        "kwargs_graph_binding",
        "kwargs_delta_witness",
        "affected_result_witness",
    }
    selective_keys = {
        "dependency_graph_id",
        "delta_id",
        "affected_request_id",
        "affected_set_id",
        "recomputation_result_id",
        "runtime_report_id",
        "validation_report_status",
        "dependency_graph_binding",
        "dependency_edges_binding",
        "delta_binding",
        "bundle_dependency_graph_binding",
        "bundle_dependency_edges_binding",
        "bundle_delta_binding",
        "bundle_affected_request_binding",
        "bundle_affected_result_binding",
        "bundle_binding",
        "validation_report_binding",
        "return_tuple_binding",
        "external_actual_return_required",
    }
    binding_names = {
        "dependency_edges_binding",
        "kwargs_graph_binding",
        "dependency_graph_binding",
        "delta_binding",
        "bundle_dependency_graph_binding",
        "bundle_dependency_edges_binding",
        "bundle_delta_binding",
        "bundle_affected_request_binding",
        "bundle_affected_result_binding",
        "bundle_binding",
        "validation_report_binding",
        "return_tuple_binding",
    }
    for case, material in zip(
        constructive, constructive_material, strict=True
    ):
        chain = material.get("constructive_call_chain")
        if type(chain) is not dict or set(chain) != {
            "proof_boundary",
            "graph_projection",
            "graph_construction",
            "affected_set_computation",
            "selective_execution",
        } or chain.get("proof_boundary") != (
            "standalone_witness_integrity_plus_external_actual_return_oracle"
        ):
            raise ValueError("g2e5_c2_cross_stage_relation_invalid")
        projection = chain["graph_projection"]
        graph = chain["graph_construction"]
        affected = chain["affected_set_computation"]
        if (
            type(projection) is not dict
            or set(projection) != projection_keys
            or type(graph) is not dict
            or set(graph) != graph_keys
            or type(affected) is not dict
            or set(affected) != affected_keys
        ):
            raise ValueError("g2e5_c2_cross_stage_relation_invalid")
        if any(
            not valid_witness(witness)
            for witness in (
                projection.get("return_witness"),
                graph.get("graph_witness"),
                affected.get("request_witness"),
                affected.get("kwargs_delta_witness"),
                affected.get("affected_result_witness"),
            )
        ):
            raise ValueError("g2e5_c2_projection_decode_invalid")
        if any(
            not valid_binding(row[name])
            for row in (projection, graph, affected)
            for name in row
            if name in binding_names
        ):
            raise ValueError("g2e5_c2_cross_stage_relation_invalid")
        if (
            projection["graph_basis_sha256"]
            != graph["graph_basis_sha256"]
            or projection["ordered_dependency_edge_ids"]
            != graph["ordered_edge_ids"]
            or graph["graph_id"]
            != material["carrier_material"]["dependency_graph_id"]
            or affected["returned_affected_request_id"]
            != affected["affected_request_id"]
            or affected["request_graph_id"] != graph["graph_id"]
            or affected["kwargs_graph_id"] != graph["graph_id"]
            or affected["returned_graph_id"] != graph["graph_id"]
            or affected["request_delta_id"] != case.delta_id
            or affected["kwargs_delta_id"] != case.delta_id
            or affected["returned_delta_id"] != case.delta_id
            or affected["returned_affected_set_id"] != case.affected_set_id
            or affected["kwargs_graph_binding"]
            != {
                "sha256": graph["graph_witness"]["sha256"],
                "byte_length": graph["graph_witness"]["byte_length"],
            }
        ):
            raise ValueError("g2e5_c2_cross_stage_relation_invalid")
        projection_document = projection["return_witness"][
            "semantic_projection"
        ]
        graph_document = graph["graph_witness"]["semantic_projection"]
        request_document = affected["request_witness"][
            "semantic_projection"
        ]
        delta_document = affected["kwargs_delta_witness"][
            "semantic_projection"
        ]
        affected_document = affected["affected_result_witness"][
            "semantic_projection"
        ]
        if (
            type(projection_document) is not dict
            or projection_document.get("kind") != "tuple"
            or type(projection_document.get("items")) is not list
            or len(projection_document["items"]) != 2
            or projected_string(projection_document["items"][0])
            != projection["graph_basis_sha256"]
            or type(projection_document["items"][1]) is not dict
            or projection_document["items"][1].get("kind") != "tuple"
            or type(projection_document["items"][1].get("items")) is not list
            or projection_binding(projection_document["items"][1])
            != projection["dependency_edges_binding"]
        ):
            raise ValueError("g2e5_c2_projection_decode_invalid")
        edge_documents = projection_document["items"][1]["items"]
        try:
            edge_plain = tuple(
                _projected_dataclass_plain(
                    item,
                    expected_type=(
                        "hedgehog.kernel.continuous_delta_runtime_v01."
                        "DeltaDependencyEdgeV01"
                    ),
                    expected_fields=_DELTA_DEPENDENCY_EDGE_FIELDS,
                )
                for item in edge_documents
            )
            graph_plain = _projected_dataclass_plain(
                graph_document,
                expected_type=(
                    "hedgehog.kernel.continuous_delta_runtime_v01."
                    "DependencyGraphIndexV01"
                ),
                expected_fields=_DEPENDENCY_GRAPH_INDEX_FIELDS,
            )
            request_plain = _projected_dataclass_plain(
                request_document,
                expected_type=(
                    "hedgehog.kernel.continuous_delta_runtime_v01."
                    "AffectedSetRequestV01"
                ),
                expected_fields=_AFFECTED_SET_REQUEST_FIELDS,
            )
            delta_plain = _projected_dataclass_plain(
                delta_document,
                expected_type=(
                    "hedgehog.kernel.continuous_delta_runtime_v01."
                    "WorldStateDeltaV01"
                ),
                expected_fields=_WORLD_STATE_DELTA_FIELDS,
            )
            affected_plain = _projected_dataclass_plain(
                affected_document,
                expected_type=(
                    "hedgehog.kernel.continuous_delta_runtime_v01."
                    "AffectedSetResultV01"
                ),
                expected_fields=_AFFECTED_SET_RESULT_FIELDS,
            )
        except (TypeError, ValueError, UnicodeError):
            raise ValueError("g2e5_c2_projection_decode_invalid") from None

        def reconstruct_carrier(
            carrier_type: object,
            plain: dict[str, object],
            failure_code: str,
        ) -> object:
            try:
                return carrier_type(**plain)
            except (TypeError, ValueError, UnicodeError):
                raise ValueError(failure_code) from None

        edge_carriers = tuple(
            reconstruct_carrier(
                g2e.DeltaDependencyEdgeV01,
                item,
                "g2e5_c2_edge_carrier_identity_invalid",
            )
            for item in edge_plain
        )
        graph_carrier = reconstruct_carrier(
            g2e.DependencyGraphIndexV01,
            graph_plain,
            "g2e5_c2_graph_carrier_identity_invalid",
        )
        request_carrier = reconstruct_carrier(
            g2e.AffectedSetRequestV01,
            request_plain,
            "g2e5_c2_request_carrier_identity_invalid",
        )
        delta_carrier = reconstruct_carrier(
            g2e.WorldStateDeltaV01,
            delta_plain,
            "g2e5_c2_delta_carrier_identity_invalid",
        )
        affected_carrier = reconstruct_carrier(
            g2e.AffectedSetResultV01,
            affected_plain,
            "g2e5_c2_affected_carrier_identity_invalid",
        )

        def exact_public_pass(
            report: object, validated_object_id: str
        ) -> bool:
            return (
                type(report) is g2e.ContinuousDeltaValidationReportV01
                and report.status == "PASS"
                and report.reason_codes == ()
                and report.source_reason_codes == ()
                and report.validated_object_id == validated_object_id
                and report.return_to_root_required is False
                and report.root_review_required is False
                and report.authority_created is False
                and report.permission_created is False
                and report.action_commit_packet_created is False
                and report.receipt_created is False
                and report.final_output_created is False
                and report.drs_write_created is False
                and report.real_world_effects_count == 0
            )

        def public_validation(
            operation: object, carrier: object, failure_code: str
        ) -> object:
            try:
                return operation(carrier)
            except (TypeError, ValueError, UnicodeError):
                raise ValueError(failure_code) from None

        if any(
            not exact_public_pass(
                public_validation(
                    g2e.validate_delta_dependency_edge_v01,
                    item,
                    "g2e5_c2_edge_carrier_identity_invalid",
                ),
                item.edge_id,
            )
            or item.edge_id
            != g2e.rebuild_delta_dependency_edge_identity_v01(item)
            or _semantic_projection(item) != document
            for item, document in zip(
                edge_carriers, edge_documents, strict=True
            )
        ):
            raise ValueError("g2e5_c2_edge_carrier_identity_invalid")
        if (
            not exact_public_pass(
                public_validation(
                    g2e.validate_dependency_graph_index_v01,
                    graph_carrier,
                    "g2e5_c2_graph_carrier_identity_invalid",
                ),
                graph_carrier.graph_id,
            )
            or graph_carrier.graph_id
            != g2e.rebuild_dependency_graph_index_identity_v01(graph_carrier)
            or _semantic_projection(graph_carrier) != graph_document
        ):
            raise ValueError("g2e5_c2_graph_carrier_identity_invalid")
        if (
            not exact_public_pass(
                public_validation(
                    g2e.validate_affected_set_request_v01,
                    request_carrier,
                    "g2e5_c2_request_carrier_identity_invalid",
                ),
                request_carrier.affected_request_id,
            )
            or request_carrier.affected_request_id
            != g2e.rebuild_affected_set_request_identity_v01(request_carrier)
            or _semantic_projection(request_carrier) != request_document
        ):
            raise ValueError("g2e5_c2_request_carrier_identity_invalid")
        if (
            not exact_public_pass(
                public_validation(
                    g2e.validate_world_state_delta_v01,
                    delta_carrier,
                    "g2e5_c2_delta_carrier_identity_invalid",
                ),
                delta_carrier.delta_id,
            )
            or delta_carrier.delta_id
            != g2e.rebuild_world_state_delta_identity_v01(delta_carrier)
            or _semantic_projection(delta_carrier) != delta_document
        ):
            raise ValueError("g2e5_c2_delta_carrier_identity_invalid")
        if (
            not exact_public_pass(
                public_validation(
                    g2e.validate_affected_set_result_v01,
                    affected_carrier,
                    "g2e5_c2_affected_carrier_identity_invalid",
                ),
                affected_carrier.affected_set_id,
            )
            or affected_carrier.affected_set_id
            != g2e.rebuild_affected_set_result_identity_v01(affected_carrier)
            or _semantic_projection(affected_carrier) != affected_document
        ):
            raise ValueError("g2e5_c2_affected_carrier_identity_invalid")
        edge_ids = tuple(item["edge_id"] for item in edge_plain)
        try:
            graph_nodes = set(graph_carrier.ordered_node_ids)
        except (TypeError, ValueError):
            raise ValueError("g2e5_c2_graph_carrier_identity_invalid") from None
        if (
            edge_ids != tuple(projection["ordered_dependency_edge_ids"])
            or graph_plain["graph_id"] != graph["graph_id"]
            or graph_plain["graph_basis_sha256"]
            != graph["graph_basis_sha256"]
            or graph_plain["ordered_edge_ids"] != edge_ids
            or graph_plain["node_count"]
            != len(graph_plain["ordered_node_ids"])
            or graph_plain["edge_count"] != len(edge_plain)
            or graph_plain["source_manifest_id"]
            != material["graph_source_manifest_id"]
            or graph_plain["source_replay_id"]
            != material["graph_source_replay_id"]
            or any(
                edge["graph_basis_sha256"]
                != graph_plain["graph_basis_sha256"]
                or edge["graph_version"] != graph_plain["graph_version"]
                or edge["transaction_id"] != graph_plain["transaction_id"]
                or edge["owning_root_id"] != graph_plain["owning_root_id"]
                or edge["domain_id"] != graph_plain["domain_id"]
                or edge["canonical_order"] != index + 1
                or edge["dependent_artifact_id"]
                == edge["dependency_artifact_id"]
                or edge["dependent_artifact_id"] not in graph_nodes
                or edge["dependency_artifact_id"] not in graph_nodes
                or type(edge["dependency_field_pointers"]) is not tuple
                or any(
                    type(pointer) is not str or not pointer.startswith("/")
                    for pointer in edge["dependency_field_pointers"]
                )
                or edge["edge_class"]
                not in {"FIELD_CAUSAL", "ARTIFACT_DEPENDENCY"}
                or (
                    edge["edge_class"] == "FIELD_CAUSAL"
                    and not edge["dependency_field_pointers"]
                )
                or (
                    edge["edge_class"] == "ARTIFACT_DEPENDENCY"
                    and edge["dependency_field_pointers"] != ()
                )
                for index, edge in enumerate(edge_plain)
            )
            or request_plain["affected_request_id"]
            != affected["affected_request_id"]
            or request_plain["graph_id"] != graph_plain["graph_id"]
            or request_plain["graph_version"] != graph_plain["graph_version"]
            or request_plain["delta_id"] != delta_plain["delta_id"]
            or request_plain["transaction_id"]
            != graph_plain["transaction_id"]
            or request_plain["owning_root_id"]
            != graph_plain["owning_root_id"]
            or request_plain["domain_id"] != graph_plain["domain_id"]
            or delta_plain["delta_id"] != affected["kwargs_delta_id"]
            or delta_plain["transaction_id"] != graph_plain["transaction_id"]
            or delta_plain["owning_root_id"] != graph_plain["owning_root_id"]
            or delta_plain["domain_id"] != graph_plain["domain_id"]
            or affected_plain["affected_request_id"]
            != request_plain["affected_request_id"]
            or affected_plain["affected_set_id"]
            != affected["returned_affected_set_id"]
            or affected_plain["graph_id"] != graph_plain["graph_id"]
            or affected_plain["graph_version"] != graph_plain["graph_version"]
            or affected_plain["delta_id"] != delta_plain["delta_id"]
            or affected_plain["ordered_changed_node_ids"]
            != tuple(case.ordered_changed_ids)
            or affected_plain["ordered_directly_affected_ids"]
            != tuple(case.ordered_directly_affected_ids)
            or affected_plain["ordered_transitively_affected_ids"]
            != tuple(case.ordered_transitively_affected_ids)
            or affected_plain["ordered_affected_ids"]
            != tuple(material["partitions"]["affected"])
        ):
            raise ValueError("g2e5_c2_cross_stage_relation_invalid")
        selective = chain["selective_execution"]
        expected_selective_count = (
            0
            if case.observed_outcome != "SELECTIVE_RECOMPUTATION_PASS"
            else 2
            if case.case_id.endswith("repeat_idempotent:v01")
            else 1
        )
        if expected_selective_count == 0:
            if selective is not None:
                raise ValueError("g2e5_c2_cross_stage_relation_invalid")
            continue
        if (
            type(selective) is not list
            or len(selective) != expected_selective_count
        ):
            raise ValueError("g2e5_c2_cross_stage_relation_invalid")
        for row in selective:
            if (
                type(row) is not dict
                or set(row) != selective_keys
                or any(
                    not valid_binding(row[name])
                    for name in binding_names
                    if name in row
                )
                or row["dependency_graph_id"] != graph["graph_id"]
                or row["delta_id"] != case.delta_id
                or row["affected_request_id"]
                != affected["affected_request_id"]
                or row["affected_set_id"] != case.affected_set_id
                or row["recomputation_result_id"]
                != case.recomputation_result_id
                or row["runtime_report_id"]
                != case.continuous_delta_runtime_report_id
                or row["validation_report_status"] != "PASS"
                or row["external_actual_return_required"] is not True
                or row["dependency_graph_binding"]
                != {
                    "sha256": graph["graph_witness"]["sha256"],
                    "byte_length": graph["graph_witness"]["byte_length"],
                }
                or row["dependency_edges_binding"]
                != projection["dependency_edges_binding"]
                or row["delta_binding"]
                != {
                    "sha256": affected["kwargs_delta_witness"]["sha256"],
                    "byte_length": affected["kwargs_delta_witness"][
                        "byte_length"
                    ],
                }
                or row["bundle_dependency_graph_binding"]
                != row["dependency_graph_binding"]
                or row["bundle_dependency_edges_binding"]
                != projection["dependency_edges_binding"]
                or row["bundle_delta_binding"]
                != row["delta_binding"]
                or row["bundle_affected_request_binding"]
                != {
                    "sha256": affected["request_witness"]["sha256"],
                    "byte_length": affected["request_witness"]["byte_length"],
                }
                or row["bundle_affected_result_binding"]
                != {
                    "sha256": affected["affected_result_witness"]["sha256"],
                    "byte_length": affected["affected_result_witness"][
                        "byte_length"
                    ],
                }
            ):
                raise ValueError("g2e5_c2_cross_stage_relation_invalid")
        if expected_selective_count == 2:
            repeat = material.get("repeat_execution")
            if (
                type(repeat) is not dict
                or selective[0]["bundle_binding"]["sha256"]
                != repeat.get("first_bundle_sha256")
                or selective[1]["bundle_binding"]["sha256"]
                != repeat.get("second_bundle_sha256")
                or selective[0]["validation_report_binding"]["sha256"]
                != repeat.get("first_report_sha256")
                or selective[1]["validation_report_binding"]["sha256"]
                != repeat.get("second_report_sha256")
                or selective[0]["return_tuple_binding"]["sha256"]
                != repeat.get("first_return_tuple_sha256")
                or selective[1]["return_tuple_binding"]["sha256"]
                != repeat.get("second_return_tuple_sha256")
                or selective[0]["bundle_binding"]["byte_length"]
                != repeat.get("bundle_byte_length")
                or selective[1]["bundle_binding"]["byte_length"]
                != repeat.get("bundle_byte_length")
                or selective[0]["validation_report_binding"]["byte_length"]
                != repeat.get("report_byte_length")
                or selective[1]["validation_report_binding"]["byte_length"]
                != repeat.get("report_byte_length")
                or selective[0]["return_tuple_binding"]["byte_length"]
                != repeat.get("return_tuple_byte_length")
                or selective[1]["return_tuple_binding"]["byte_length"]
                != repeat.get("return_tuple_byte_length")
            ):
                raise ValueError("g2e5_c2_cross_stage_relation_invalid")
    for case_id in (
        "g2e_case:travel:repeat_idempotent:v01",
        "g2e_case:warehouse:repeat_idempotent:v01",
    ):
        material = constructive_material[
            CONSTRUCTIVE_CASE_ORDER.index(case_id)
        ]
        repeat = material.get("repeat_execution")
        if (
            type(repeat) is not dict
            or repeat.get("independent_execution_count") != 2
            or repeat.get("bundle_bytes_equal") is not True
            or repeat.get("report_bytes_equal") is not True
            or repeat.get("return_tuple_bytes_equal") is not True
            or repeat.get("bundle_same_object") is not False
            or repeat.get("report_same_object") is not False
            or repeat.get("first_bundle_sha256")
            != repeat.get("second_bundle_sha256")
            or repeat.get("first_report_sha256")
            != repeat.get("second_report_sha256")
            or repeat.get("first_return_tuple_sha256")
            != repeat.get("second_return_tuple_sha256")
            or type(repeat.get("bundle_byte_length")) is not int
            or repeat["bundle_byte_length"] <= 0
            or type(repeat.get("report_byte_length")) is not int
            or repeat["report_byte_length"] <= 0
            or type(repeat.get("return_tuple_byte_length")) is not int
            or repeat["return_tuple_byte_length"] <= 0
        ):
            raise ValueError("g2e5_repeat_evidence_invalid")
    safe_case = constructive[8]
    safe_case_material = constructive_material[8]
    safe_material = safe_case_material.get("safe_sibling")

    safe_sibling_keys = {
        "proof_boundary",
        "artifact_id",
        "artifact_sha256",
        "payload_sha256",
        "canonical_artifact_bytes_sha256",
        "canonical_artifact_byte_length",
        "canonical_payload_byte_length",
        "queue_entry_id",
        "runtime_artifact_id",
        "projection_artifact_plain",
        "baseline_runtime_artifact_plain",
        "recomputed_runtime_artifact_plain",
        "baseline_queue_artifact_row",
        "recomputed_queue_artifact_row",
        "preservation_proof_rows",
        "recomputed_binding_rows",
        "projection_artifact_id",
        "projection_artifact_sha256",
        "projection_artifact_byte_length",
        "projection_payload_sha256",
        "projection_payload_byte_length",
        "projection_parent_runtime_artifact_id",
        "projection_embedded_runtime_artifact_sha256",
        "projection_embedded_runtime_artifact_byte_length",
        "baseline_runtime_payload_sha256",
        "baseline_runtime_payload_byte_length",
        "recomputed_runtime_payload_sha256",
        "recomputed_runtime_payload_byte_length",
        "baseline_runtime_artifact_sha256",
        "baseline_runtime_artifact_byte_length",
        "recomputed_runtime_artifact_sha256",
        "recomputed_runtime_artifact_byte_length",
        "invalidation_record_artifact_ids",
        "ordered_recomputed_binding_ids",
        "result_ordered_recomputed_binding_ids",
        "result_ordered_recomputed_artifact_ids",
        "sibling_touching_recomputed_binding_ids",
        "sibling_touching_prior_artifact_ids",
        "sibling_touching_new_artifact_ids",
        "preservation_row_index",
        "preservation_before_identity_id",
        "preservation_after_identity_id",
        "preservation_before_payload_sha256",
        "preservation_after_payload_sha256",
        "preservation_before_artifact_sha256",
        "preservation_after_artifact_sha256",
    }

    def safe_sibling_witness_valid(material: object) -> bool:
        if type(material) is not dict or set(material) != safe_sibling_keys:
            return False
        try:
            projection_plain = material["projection_artifact_plain"]
            baseline_plain = material["baseline_runtime_artifact_plain"]
            recomputed_plain = material["recomputed_runtime_artifact_plain"]
            if any(
                type(item) is not dict
                for item in (projection_plain, baseline_plain, recomputed_plain)
            ):
                return False

            def rebuild_plain_artifact(
                plain: dict[str, object],
            ) -> g2e.KernelArtifactV01 | None:
                if (
                    set(plain) != set(_KERNEL_ARTIFACT_PLAIN_FIELDS)
                    or len(plain) != len(_KERNEL_ARTIFACT_PLAIN_FIELDS)
                    or type(plain.get("trace_refs")) is not list
                    or type(plain.get("parent_refs")) is not list
                ):
                    return None
                rebuilt = build_kernel_artifact_v01(
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
                if (
                    validate_kernel_artifact_v01(rebuilt) != ()
                    or kernel_artifact_to_plain_dict_v01(rebuilt) != plain
                ):
                    return None
                return rebuilt

            projection_artifact = rebuild_plain_artifact(projection_plain)
            baseline_artifact = rebuild_plain_artifact(baseline_plain)
            recomputed_artifact = rebuild_plain_artifact(recomputed_plain)
            if any(
                item is None
                for item in (
                    projection_artifact,
                    baseline_artifact,
                    recomputed_artifact,
                )
            ):
                return False
            projection_payload = projection_plain["payload"]
            baseline_payload = baseline_plain["payload"]
            recomputed_payload = recomputed_plain["payload"]
            if any(
                type(item) is not dict
                for item in (
                    projection_payload,
                    baseline_payload,
                    recomputed_payload,
                )
            ):
                return False
            if (
                material.get("proof_boundary")
                != (
                    "standalone_canonical_integrity_plus_external_actual_runtime_oracle"
                )
                or set(projection_payload)
                != {
                    "projection_profile_id",
                    "projected_runtime_artifact",
                    "projected_runtime_artifact_sha256",
                }
                or projection_payload.get("projection_profile_id")
                != "g2e_baseline_runtime_artifact_projection_v01"
            ):
                return False

            def plain_binding(value: object) -> tuple[str, int]:
                payload = canonical_json_bytes_v01(value)
                return hashlib.sha256(payload).hexdigest(), len(payload)

            projection_hash, projection_length = plain_binding(
                projection_plain
            )
            projection_payload_hash, projection_payload_length = plain_binding(
                projection_payload
            )
            baseline_hash, baseline_length = plain_binding(baseline_plain)
            baseline_payload_hash, baseline_payload_length = plain_binding(
                baseline_payload
            )
            recomputed_hash, recomputed_length = plain_binding(
                recomputed_plain
            )
            recomputed_payload_hash, recomputed_payload_length = plain_binding(
                recomputed_payload
            )
            runtime_id = material["runtime_artifact_id"]
            projection_id = material["projection_artifact_id"]
            queue_entry_id = material["queue_entry_id"]
            proof_rows = material["preservation_proof_rows"]
            binding_rows = material["recomputed_binding_rows"]
            if (
                type(runtime_id) is not str
                or type(projection_id) is not str
                or type(queue_entry_id) is not str
                or projection_id
                != "artifact:g2e5:runtime-projection:" + baseline_hash
                or runtime_id.startswith("artifact:g2e5:runtime-projection:")
                or projection_plain.get("artifact_id") != projection_id
                or baseline_plain.get("artifact_id") != runtime_id
                or recomputed_plain.get("artifact_id") != runtime_id
                or projection_plain.get("parent_refs") != [runtime_id]
                or projection_plain.get("abi_version") != "v1.0"
                or projection_plain.get("artifact_type") != "SemanticEvidence"
                or projection_plain.get("schema_version") != "v1"
                or projection_plain.get("transaction_id")
                != baseline_plain.get("transaction_id")
                or projection_plain.get("owner_root_id")
                != baseline_plain.get("owner_root_id")
                or projection_plain.get("source_component")
                != "continuous_delta_runtime_g2e5"
                or projection_plain.get("authority_class") != "EVIDENCE_ONLY"
                or projection_plain.get("lifecycle_state") != "VALIDATED"
                or projection_plain.get("trace_refs")
                != ["trace:" + projection_id]
                or projection_plain.get("time_envelope")
                != {
                    "ct_session_anchor": "ct:g2e5:source",
                    "et_observed_at": EVALUATION_UTC,
                    "freshness_class": "static",
                    "kt_asof": EVALUATION_UTC,
                    "pt_created_at": EVALUATION_UTC,
                    "ttl_seconds": 3600,
                    "valid_from": EVALUATION_UTC,
                    "valid_to": VALID_TO_UTC,
                }
                or projection_payload.get("projected_runtime_artifact")
                != baseline_plain
                or projection_payload.get(
                    "projected_runtime_artifact_sha256"
                )
                != baseline_hash
                or projection_hash != material["projection_artifact_sha256"]
                or projection_length
                != material["projection_artifact_byte_length"]
                or projection_payload_hash
                != material["projection_payload_sha256"]
                or projection_payload_length
                != material["projection_payload_byte_length"]
                or baseline_hash != material["artifact_sha256"]
                or baseline_hash
                != material["canonical_artifact_bytes_sha256"]
                or baseline_hash
                != material["baseline_runtime_artifact_sha256"]
                or baseline_length
                != material["canonical_artifact_byte_length"]
                or baseline_length
                != material["baseline_runtime_artifact_byte_length"]
                or baseline_payload_hash != material["payload_sha256"]
                or baseline_payload_hash
                != material["baseline_runtime_payload_sha256"]
                or baseline_payload_length
                != material["canonical_payload_byte_length"]
                or baseline_payload_length
                != material["baseline_runtime_payload_byte_length"]
                or recomputed_hash
                != material["recomputed_runtime_artifact_sha256"]
                or recomputed_length
                != material["recomputed_runtime_artifact_byte_length"]
                or recomputed_payload_hash
                != material["recomputed_runtime_payload_sha256"]
                or recomputed_payload_length
                != material["recomputed_runtime_payload_byte_length"]
                or baseline_plain != recomputed_plain
                or baseline_payload != recomputed_payload
                or material["projection_parent_runtime_artifact_id"]
                != runtime_id
                or material[
                    "projection_embedded_runtime_artifact_sha256"
                ]
                != baseline_hash
                or material[
                    "projection_embedded_runtime_artifact_byte_length"
                ]
                != baseline_length
                or material["baseline_queue_artifact_row"]
                != {
                    "queue_entry_id": queue_entry_id,
                    "artifact_id": runtime_id,
                    "artifact_sha256": baseline_hash,
                }
                or material["recomputed_queue_artifact_row"]
                != {
                    "queue_entry_id": queue_entry_id,
                    "artifact_id": runtime_id,
                    "artifact_sha256": recomputed_hash,
                }
                or type(proof_rows) is not list
                or len(proof_rows) != 1
                or type(binding_rows) is not list
                or any(
                    type(row) is not dict
                    or set(row) != {
                        "recomputed_binding_id",
                        "prior_artifact_id",
                        "new_artifact_id",
                    }
                    for row in binding_rows
                )
            ):
                return False
            proof_row = proof_rows[0]
            if (
                type(proof_row) is not dict
                or set(proof_row) != {
                    "row_index",
                    "preserved_artifact_id",
                    "before_identity_id",
                    "after_identity_id",
                    "before_payload_sha256",
                    "after_payload_sha256",
                    "before_artifact_sha256",
                    "after_artifact_sha256",
                }
                or proof_row["row_index"] != material["preservation_row_index"]
                or proof_row["preserved_artifact_id"] != runtime_id
                or proof_row["before_identity_id"] != runtime_id
                or proof_row["after_identity_id"] != runtime_id
                or proof_row["before_payload_sha256"] != baseline_payload_hash
                or proof_row["after_payload_sha256"]
                != recomputed_payload_hash
                or proof_row["before_artifact_sha256"] != baseline_hash
                or proof_row["after_artifact_sha256"] != recomputed_hash
                or material["preservation_before_identity_id"] != runtime_id
                or material["preservation_after_identity_id"] != runtime_id
                or material["preservation_before_payload_sha256"]
                != proof_row["before_payload_sha256"]
                or material["preservation_after_payload_sha256"]
                != proof_row["after_payload_sha256"]
                or material["preservation_before_artifact_sha256"]
                != proof_row["before_artifact_sha256"]
                or material["preservation_after_artifact_sha256"]
                != proof_row["after_artifact_sha256"]
            ):
                return False
            binding_ids = [
                row["recomputed_binding_id"] for row in binding_rows
            ]
            protected_ids = {runtime_id, projection_id}
            touching_rows = [
                row
                for row in binding_rows
                if row["prior_artifact_id"] in protected_ids
                or row["new_artifact_id"] in protected_ids
            ]
            if (
                material["ordered_recomputed_binding_ids"] != binding_ids
                or material["result_ordered_recomputed_binding_ids"]
                != binding_ids
                or material["sibling_touching_recomputed_binding_ids"]
                != [row["recomputed_binding_id"] for row in touching_rows]
                or material["sibling_touching_prior_artifact_ids"]
                != [row["prior_artifact_id"] for row in touching_rows]
                or material["sibling_touching_new_artifact_ids"]
                != [row["new_artifact_id"] for row in touching_rows]
                or touching_rows
            ):
                return False
            invalidated_ids = material["invalidation_record_artifact_ids"]
            result_recomputed_ids = material[
                "result_ordered_recomputed_artifact_ids"
            ]
            if (
                type(invalidated_ids) is not list
                or invalidated_ids != list(safe_case.ordered_invalidated_ids)
                or type(result_recomputed_ids) is not list
                or result_recomputed_ids
                != list(safe_case.ordered_recomputed_ids)
                or any(
                    artifact_id
                    in {
                        *safe_case.ordered_changed_ids,
                        *safe_case.ordered_directly_affected_ids,
                        *safe_case.ordered_transitively_affected_ids,
                        *safe_case_material["partitions"]["affected"],
                        *invalidated_ids,
                        *result_recomputed_ids,
                    }
                    for artifact_id in (runtime_id, projection_id)
                )
            ):
                return False
        except (
            KeyError,
            TypeError,
            ValueError,
            UnicodeEncodeError,
        ):
            return False
        return True

    if type(safe_material) is dict:
        protected_ids = {
            safe_material.get("runtime_artifact_id"),
            safe_material.get("projection_artifact_id"),
        }
        binding_rows = safe_material.get("recomputed_binding_rows")
        if (
            None not in protected_ids
            and type(binding_rows) is list
            and any(
                type(row) is dict
                and (
                    row.get("prior_artifact_id") in protected_ids
                    or row.get("new_artifact_id") in protected_ids
                )
                for row in binding_rows
            )
        ):
            raise ValueError("g2e5_safe_sibling_binding_role_invalid")
    if not safe_sibling_witness_valid(safe_material):
        raise ValueError("g2e5_safe_sibling_evidence_invalid")
    if (
        type(safe_material) is not dict
        or safe_material.get("artifact_id")
        != safe_material.get("runtime_artifact_id")
        or safe_material.get("artifact_id")
        != safe_material.get("projection_parent_runtime_artifact_id")
        or safe_material.get("artifact_id")
        != safe_material.get("preservation_before_identity_id")
        or safe_material.get("projection_artifact_id")
        == safe_material.get("artifact_id")
        or safe_material.get("preservation_before_identity_id")
        != safe_material.get("preservation_after_identity_id")
        or safe_material.get("artifact_sha256")
        != safe_material.get("canonical_artifact_bytes_sha256")
        or safe_material.get("artifact_sha256")
        != safe_material.get("baseline_runtime_artifact_sha256")
        or safe_material.get("artifact_sha256")
        != safe_material.get("recomputed_runtime_artifact_sha256")
        or safe_material.get("artifact_sha256")
        != safe_material.get("projection_embedded_runtime_artifact_sha256")
        or safe_material.get("artifact_sha256")
        != safe_material.get("preservation_before_artifact_sha256")
        or safe_material.get("artifact_sha256")
        != safe_material.get("preservation_after_artifact_sha256")
        or safe_material.get("payload_sha256")
        != safe_material.get("baseline_runtime_payload_sha256")
        or safe_material.get("payload_sha256")
        != safe_material.get("recomputed_runtime_payload_sha256")
        or safe_material.get("payload_sha256")
        != safe_material.get("preservation_before_payload_sha256")
        or safe_material.get("payload_sha256")
        != safe_material.get("preservation_after_payload_sha256")
        or safe_material.get("baseline_runtime_payload_sha256")
        != safe_material.get("recomputed_runtime_payload_sha256")
        or safe_material.get("baseline_runtime_payload_byte_length")
        != safe_material.get("recomputed_runtime_payload_byte_length")
        or safe_material.get("baseline_runtime_artifact_sha256")
        != safe_material.get("recomputed_runtime_artifact_sha256")
        or safe_material.get("baseline_runtime_artifact_byte_length")
        != safe_material.get("recomputed_runtime_artifact_byte_length")
        or safe_material.get("canonical_artifact_byte_length")
        != safe_material.get("baseline_runtime_artifact_byte_length")
        or safe_material.get("canonical_payload_byte_length")
        != safe_material.get("baseline_runtime_payload_byte_length")
        or safe_material.get(
            "projection_embedded_runtime_artifact_byte_length"
        )
        != safe_material.get("baseline_runtime_artifact_byte_length")
        or type(safe_material.get("preservation_row_index")) is not int
        or safe_material["preservation_row_index"] < 0
        or any(
            protected_id
            in {
                *safe_case.ordered_changed_ids,
                *safe_case.ordered_directly_affected_ids,
                *safe_case.ordered_transitively_affected_ids,
                *safe_case_material["partitions"]["affected"],
            }
            for protected_id in (
                safe_material.get("runtime_artifact_id"),
                safe_material.get("projection_artifact_id"),
            )
        )
        or safe_material.get("invalidation_record_artifact_ids")
        != list(safe_case.ordered_invalidated_ids)
        or any(
            protected_id
            in safe_material.get("invalidation_record_artifact_ids", ())
            for protected_id in (
                safe_material.get("runtime_artifact_id"),
                safe_material.get("projection_artifact_id"),
            )
        )
        or safe_material.get("sibling_touching_recomputed_binding_ids") != []
        or safe_material.get("sibling_touching_prior_artifact_ids") != []
        or safe_material.get("sibling_touching_new_artifact_ids") != []
        or safe_material.get("ordered_recomputed_binding_ids")
        != safe_material.get("result_ordered_recomputed_binding_ids")
        or safe_material.get("result_ordered_recomputed_artifact_ids")
        != list(safe_case.ordered_recomputed_ids)
        or safe_material.get("artifact_id")
        in safe_material.get("result_ordered_recomputed_artifact_ids", ())
        or safe_material.get("projection_artifact_id")
        in safe_material.get("result_ordered_recomputed_artifact_ids", ())
        or any(
            type(safe_material.get(name)) is not int
            or safe_material[name] <= 0
            for name in (
                "canonical_artifact_byte_length",
                "canonical_payload_byte_length",
                "projection_artifact_byte_length",
                "projection_payload_byte_length",
                "projection_embedded_runtime_artifact_byte_length",
                "baseline_runtime_payload_byte_length",
                "recomputed_runtime_payload_byte_length",
                "baseline_runtime_artifact_byte_length",
                "recomputed_runtime_artifact_byte_length",
            )
        )
        or any(
            type(safe_material.get(name)) is not str
            or len(safe_material[name]) != 64
            or not set(safe_material[name]) <= set("0123456789abcdef")
            for name in (
                "artifact_sha256",
                "payload_sha256",
                "projection_artifact_sha256",
                "projection_payload_sha256",
                "projection_embedded_runtime_artifact_sha256",
            )
        )
    ):
        raise ValueError("g2e5_safe_sibling_evidence_invalid")
    required_constructive_outcomes = (
        "SELECTIVE_RECOMPUTATION_PASS",
        "SELECTIVE_RECOMPUTATION_PASS",
        "ROUTE_REVALIDATION_REQUIRED",
        "CONTEXT_ONLY_PRESERVED",
        "SELECTIVE_RECOMPUTATION_PASS",
        "SELECTIVE_RECOMPUTATION_PASS",
        "SELECTIVE_RECOMPUTATION_PASS",
        "ROUTE_REVALIDATION_REQUIRED",
        "SELECTIVE_RECOMPUTATION_PASS",
        "SELECTIVE_RECOMPUTATION_PASS",
    )
    if (
        tuple(case.expected_outcome for case in constructive)
        != required_constructive_outcomes
        or tuple(case.observed_outcome for case in constructive)
        != required_constructive_outcomes
        or any(case.expected_outcome != "FAIL_CLOSED" for case in negative)
        or any(case.observed_outcome != "FAIL_CLOSED" for case in negative)
    ):
        raise ValueError("g2e5_case_outcome_invalid")
    for case in value.case_results:
        if (
            case.expected_outcome != case.observed_outcome
            or case.expected_reason_codes != case.observed_reason_codes
            or case.final_status != "PASS"
            or case.reason_codes != ()
            or any(_zero_counter_values(case))
            or not _case_evidence_valid(case)
        ):
            raise ValueError("g2e5_case_evidence_invalid")
    if any(not case.subcase_results for case in negative):
        raise ValueError("g2e5_negative_subcase_missing")
    direct_report_case_id = (
        "g2e_case:negative:caller_supplied_pass_reason_status:v01"
    )
    semantic_call_fingerprints: list[str] = []
    formal_material_by_case: dict[str, tuple[dict[str, object], ...]] = {}
    formal_material_by_subcase_id: dict[str, dict[str, object]] = {}
    for case, row in zip(negative, _NEGATIVE_ROWS, strict=True):
        suffix, axis, reason = row
        expected_specs = _negative_subcase_specs(suffix, axis, reason)
        if tuple(
            (
                subcase.subcase_id,
                subcase.mutated_axis,
                subcase.expected_reason_codes,
                subcase.observed_reason_codes,
            )
            for subcase in case.subcase_results
        ) != tuple(
            (
                case.case_id + ":subcase:" + name,
                subcase_axis,
                _reason_tuple(subcase_reason),
                _reason_tuple(subcase_reason),
            )
            for name, subcase_axis, subcase_reason in expected_specs
        ):
            raise ValueError("g2e5_negative_matrix_geometry_invalid")
        case_material: list[dict[str, object]] = []
        for subcase in case.subcase_results:
            try:
                material = json.loads(subcase.evidence_material_json)
            except (TypeError, ValueError, json.JSONDecodeError):
                raise ValueError("g2e5_negative_evidence_invalid") from None
            validator_name = material.get("public_semantic_validator")
            semantic_call_fingerprint = material.get(
                "semantic_call_fingerprint"
            )
            mutated_carrier_sha256 = material.get("mutated_carrier_sha256")
            semantic_result_sha256 = material.get("semantic_result_sha256")
            semantic_call_length = material.get(
                "semantic_call_semantic_length"
            )
            mutated_carrier_length = material.get(
                "mutated_carrier_semantic_length"
            )
            semantic_result_length = material.get(
                "semantic_result_semantic_length"
            )
            locator = material.get("mutated_argument_locator")
            hex_digits = frozenset("0123456789abcdef")
            if (
                material.get("caller_supplied_rejection_report") is not False
                or material.get("compositional_binding_profile_id")
                != COMPOSITIONAL_BINDING_PROFILE_V02
                or type(material.get("mutated_carrier_id")) is not str
                or not material["mutated_carrier_id"]
                or type(material.get("mutated_carrier_type")) is not str
                or not material["mutated_carrier_type"]
                or type(validator_name) is not str
                or not validator_name
                or type(semantic_call_fingerprint) is not str
                or len(semantic_call_fingerprint) != 64
                or not set(semantic_call_fingerprint) <= hex_digits
                or type(mutated_carrier_sha256) is not str
                or len(mutated_carrier_sha256) != 64
                or not set(mutated_carrier_sha256) <= hex_digits
                or type(semantic_result_sha256) is not str
                or len(semantic_result_sha256) != 64
                or not set(semantic_result_sha256) <= hex_digits
                or type(semantic_call_length) is not int
                or semantic_call_length <= 0
                or type(mutated_carrier_length) is not int
                or mutated_carrier_length <= 0
                or type(semantic_result_length) is not int
                or semantic_result_length <= 0
                or type(locator) is not str
                or not (
                    locator.startswith("arg:") or locator.startswith("kw:")
                )
                or tuple(material.get("returned_reason_codes", ()))
                != subcase.observed_reason_codes
                or (
                    validator_name.endswith(
                        "validate_continuous_delta_validation_report_v01"
                    )
                    and case.case_id != direct_report_case_id
                )
                or (
                    case.case_id == direct_report_case_id
                    and not validator_name.endswith(
                        "validate_continuous_delta_validation_report_v01"
                    )
                )
            ):
                raise ValueError("g2e5_negative_evidence_invalid")
            if not _case53_graph_projection_witness_evidence_valid_v01(
                subcase.subcase_id,
                material,
            ):
                raise ValueError(
                    "g2e5_case53_graph_projection_witness_invalid"
                )
            semantic_call_fingerprints.append(semantic_call_fingerprint)
            case_material.append(material)
            formal_material_by_subcase_id[subcase.subcase_id] = material
        formal_material_by_case[case.case_id] = tuple(case_material)
    if len(semantic_call_fingerprints) != 296:
        raise ValueError("g2e5_negative_subcase_count_invalid")
    if len(set(semantic_call_fingerprints)) != len(semantic_call_fingerprints):
        raise ValueError("g2e5_negative_evidence_not_one_to_one")
    transition_case = negative[85]
    abi_case = negative[87]
    case89 = negative[88]
    if len(transition_case.subcase_results) != 110:
        raise ValueError("g2e5_transition_submatrix_invalid")
    if len(abi_case.subcase_results) != 35:
        raise ValueError("g2e5_abi_submatrix_invalid")
    if (
        len(case89.subcase_results) != 29
        or tuple(
            sum(
                1
                for subcase in case89.subcase_results
                if subcase.mutated_axis == family
            )
            for family in (
                "parent_ids",
                "trace_refs",
                "time_envelope",
                "plan_relation",
                "shared_root_artifact",
            )
        )
        != (9, 9, 9, 1, 1)
    ):
        raise ValueError("g2e5_case89_submatrix_invalid")
    for case, expected_count, reason in (
        (transition_case, 110, "g2e5_transition_submatrix_invalid"),
        (abi_case, 35, "g2e5_abi_submatrix_invalid"),
        (case89, 29, "g2e5_case89_submatrix_invalid"),
    ):
        material_rows = formal_material_by_case[case.case_id]
        digests = tuple(
            str(material["mutated_carrier_sha256"])
            for material in material_rows
        )
        fingerprints = tuple(
            str(material["semantic_call_fingerprint"])
            for material in material_rows
        )
        if (
            len(material_rows) != expected_count
            or len(set(digests)) != expected_count
            or len(set(fingerprints)) != expected_count
        ):
            raise ValueError(reason)
    duplicate_pairs = (
        (
            "preserved_payload_mutation",
            "preserved_full_artifact_bytes_mutation",
        ),
        ("hidden_cache_mutation", "hidden_mutable_global_state"),
        (
            "packet_kept_executable_after_invalidation",
            "packet_revoked_without_root_seam",
        ),
        ("result_report_binding_mismatch", "post_vv_gt_binding_mismatch"),
    )
    for left_suffix, right_suffix in duplicate_pairs:
        left = formal_material_by_case[
            "g2e_case:negative:" + left_suffix + ":v01"
        ][0]
        right = formal_material_by_case[
            "g2e_case:negative:" + right_suffix + ":v01"
        ][0]
        if (
            left["semantic_call_fingerprint"]
            == right["semantic_call_fingerprint"]
            or left["mutated_carrier_sha256"]
            == right["mutated_carrier_sha256"]
        ):
            raise ValueError("g2e5_negative_recipe_collision")
    repaired_duplicate_pairs = (
        (
            "g2e_case:negative:omitted_transitive_dependent:v01:subcase:"
            "omitted_transitive_dependent",
            "g2e_case:negative:injected_unrelated_affected_artifact:v01:"
            "subcase:pointer_suppression",
        ),
        (
            "g2e_case:negative:selective_execution_carrier_omission:v01:"
            "subcase:post_execution_partial_failure",
            "g2e_case:negative:recomputed_g2d_result_report_ref_substitution:"
            "v01:subcase:partial_failure_id",
        ),
        (
            "g2e_case:negative:result_report_binding_mismatch:v01:subcase:"
            "result_report_binding_mismatch",
            "g2e_case:negative:final_root_review_carrier_substitution:v01:"
            "subcase:selected_carrier",
        ),
        (
            "g2e_case:negative:root_acceptance_outcome_forgery:v01:subcase:"
            "forged_accept",
            "g2e_case:negative:transition_rule_order_or_terminal_path_forgery:"
            "v01:subcase:non_accept_finalization",
        ),
        (
            "g2e_case:negative:transition_rule_eleven_field_substitution:v01:"
            "subcase:rule_06_decision",
            "g2e_case:negative:transition_rule_order_or_terminal_path_forgery:"
            "v01:subcase:t06_nonterminal",
        ),
        (
            "g2e_case:negative:transition_rule_eleven_field_substitution:v01:"
            "subcase:rule_08_decision",
            "g2e_case:negative:transition_rule_order_or_terminal_path_forgery:"
            "v01:subcase:t08_nonterminal",
        ),
    )
    for left_id, right_id in repaired_duplicate_pairs:
        left = formal_material_by_subcase_id[left_id]
        right = formal_material_by_subcase_id[right_id]
        if (
            left["semantic_call_fingerprint"]
            == right["semantic_call_fingerprint"]
            or left["mutated_carrier_sha256"]
            == right["mutated_carrier_sha256"]
        ):
            raise ValueError("g2e5_negative_recipe_collision")
    for suffix, expected_count in (
        ("plan_root_review_carrier_substitution", 7),
        ("final_root_review_carrier_substitution", 9),
    ):
        rows = formal_material_by_case[
            "g2e_case:negative:" + suffix + ":v01"
        ]
        if (
            len(rows) != expected_count
            or len(
                {str(row["semantic_call_fingerprint"]) for row in rows}
            )
            != expected_count
            or len({str(row["mutated_carrier_sha256"]) for row in rows})
            != expected_count
        ):
            raise ValueError("g2e5_root_review_recipe_collision")
    sealed = _sealed_material(
        domain_order=value.domain_order,
        case_results=value.case_results,
        constructive_case_count=value.constructive_case_count,
        negative_case_count=value.negative_case_count,
        total_case_count=value.total_case_count,
        accepted_baseline_bundle_count=value.accepted_baseline_bundle_count,
        explicit_public_g2d_baseline_call_count=(
            value.explicit_public_g2d_baseline_call_count
        ),
        source_collectors_replayed=value.source_collectors_replayed,
        source_evidence_mode=value.source_evidence_mode,
        final_status=value.final_status,
        reason_codes=value.reason_codes,
    )
    if value.sealed_evidence_sha256 != _sha256_domain(
        SEALED_EVIDENCE_DOMAIN, sealed
    ):
        raise ValueError("g2e5_seal_invalid")
    expected_id = REPORT_ID_PREFIX + _sha256_domain(
        REPORT_ID_DOMAIN, _report_identity_material(value)
    )
    if value.report_id != expected_id:
        raise ValueError("g2e5_report_identity_invalid")
    return value


def continuous_delta_runtime_g2_e_report_to_plain_data_v01(
    value: ContinuousDeltaRuntimeG2EReportV01,
    *,
    validate: bool = True,
) -> dict[str, object]:
    if validate:
        validate_continuous_delta_runtime_g2_e_report_v01(value)
    return _plain_data(value)  # type: ignore[return-value]


def render_continuous_delta_runtime_g2_e_v01(
    report: ContinuousDeltaRuntimeG2EReportV01,
) -> str:
    validate_continuous_delta_runtime_g2_e_report_v01(report)
    return json.dumps(
        continuous_delta_runtime_g2_e_report_to_plain_data_v01(report),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ) + "\n"


def main() -> int:
    print(render_continuous_delta_runtime_g2_e_v01(
        collect_continuous_delta_runtime_g2_e_v01()
    ), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
