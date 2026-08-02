"""Deterministic two-domain G2-C ExecutionModeRouter proof."""

from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass, replace
import hashlib
import json
from types import SimpleNamespace

import hedgehog.action_commit_packet_v02 as action_packet
import hedgehog.context_packets as context_packets
import hedgehog.drs_g2b_compatibility_v01 as compatibility
import hedgehog.drs_memory_resolution_v01 as resolution
import hedgehog.drs_semantic_address_v01 as semantic
import hedgehog.reuse_certificate_v01 as reuse
import hedgehog.structured_rationale as structured_rationale
from hedgehog.evidence import external_anchor_v01 as external_anchor
from hedgehog.evidence import sealed_evidence_profile_v01 as evidence_profile
from hedgehog.evidence import sealed_package_v01 as sealed_package
from hedgehog.evidence import sealed_replay_evidence_v01 as sealed_replay
import hedgehog.kernel.abi_v01 as abi
import hedgehog.kernel.execution_mode_router_v01 as router
from hedgehog.kernel.integrity_replay_v01 import canonical_json_bytes_v01
from hedgehog.kernel.integrity_replay_v01 import (
    domain_separated_sha256_hex_v01,
)
import hedgehog.kernel.root_decision_v01 as root_decision
import hedgehog.kernel.semantic_work_v01 as semantic_work
import hedgehog.kernel.transition_registry_v01 as transition_registry
from hedgehog.kernel.trust_model_v01 import (
    build_default_component_trust_profiles_v01,
)


EXECUTION_MODE_ROUTER_G2_C_PROOF_VERSION = "v0.1"
EXECUTION_MODE_ROUTER_G2_C_PROFILE_ID = (
    "execution_mode_router_g2c_two_domain_proof_v01"
)
CANONICAL_SCENARIO_COUNT = 10

EVALUATION_TIME = 1785542400
VALID_TO_TIME = 1785546000
EVALUATION_UTC = "2026-08-01T00:00:00+00:00"
VALID_TO_UTC = "2026-08-01T01:00:00+00:00"
DOMAIN_ORDER = (
    "TRAVEL_POLICY_INFORMATION",
    "WAREHOUSE_MAINTENANCE_INFORMATION",
)
FIXTURE_BY_DOMAIN = {
    DOMAIN_ORDER[0]: "g2c_fixture:travel_policy_information:v01",
    DOMAIN_ORDER[1]: "g2c_fixture:warehouse_maintenance_information:v01",
}
ROOT_BY_DOMAIN = {
    DOMAIN_ORDER[0]: "root:g2c:travel_policy_information:v01",
    DOMAIN_ORDER[1]: "root:g2c:warehouse_maintenance_information:v01",
}
ZERO_OPERATION_NAMES = (
    "provider_calls",
    "model_calls",
    "gemini_calls",
    "network_calls",
    "connector_calls",
    "external_drs_calls",
    "action_commit_packets_created",
    "permissions_created",
    "receipts_created",
    "topologies_created",
    "drs_writes",
    "final_outputs_created",
    "real_world_effects",
)
G2B_EVIDENCE_CLASSES = (
    "SOURCE_IDENTITY",
    "SOURCE_INTEGRITY",
    "PROVENANCE_CHAIN",
    "TIME_FITNESS",
    "POLICY_COMPATIBILITY",
    "SCHEMA_COMPATIBILITY",
    "CONFLICT_CLEARANCE",
    "ROOT_DECISION",
    "SOURCE_HISTORY",
)
G2B_DIRECT_ROOT_BINDING_DOMAIN = (
    "hedgehog:drs:root_shortcut_root_result_binding:v01"
)
G2B_DIRECT_ROOT_PREDICATE = (
    "authorize_non_action_informational_answer_shortcut_v01"
)
G2B_DIRECT_POLICY_REF = "policy:drs_answer_shortcut:v0.1"
REPORT_ID_DOMAIN = "HEDGEHOG_EXECUTION_MODE_ROUTER_G2_C5_REPORT_V01"
REPORT_ID_PREFIX = "emproof_v01:"


@dataclass(frozen=True)
class _CaseSpecV01:
    case_id: str
    suffix: str
    domain_id: str
    request_id: str
    literal_transaction_id: str | None
    selected_mode: str
    review_action: str
    root_outcome: str
    selected_reason: str
    root_source_reason: str
    projection_reason: str
    post_transition_reason: str
    downstream_consumption_class: str
    route_eligibility_present: bool
    action_class: str = "NON_ACTION"
    action_relation: str = "NOT_APPLICABLE"
    replay_bound: bool = False
    g2b_kind: str = "NOT_APPLICABLE"
    g2a_present: bool = False
    request_class: str = "BOUNDED_REVIEW"
    hard_block_state: str = "CLEAR"
    required_user_input_state: str = "COMPLETE"
    accepted_scope_ref: str | None = None
    packet_required: bool = False


CASE_SPECS = (
    _CaseSpecV01(
        "g2c_case:travel:sealed_replay:v01", "travel:sealed_replay",
        DOMAIN_ORDER[0], "request:g2c:travel:sealed_replay:v01",
        "transaction:g2c:travel:sealed_replay:v01", "sealed_replay",
        "ACCEPT", "ACCEPT", "g2c_sealed_replay_feasible",
        "validated_candidate_accepted", "g2c_root_accept_projected",
        "g2c_transition_route_accept_allowed", "SHORTCUT_RETURN_TO_ROOT",
        True, replay_bound=True,
    ),
    _CaseSpecV01(
        "g2c_case:travel:direct_informational_reuse:v01",
        "travel:direct_informational_reuse", DOMAIN_ORDER[0],
        "request:g2c:travel:direct_informational_reuse:v01", None,
        "direct_informational_reuse", "ACCEPT", "ACCEPT",
        "g2c_direct_informational_reuse_feasible",
        "validated_candidate_accepted", "g2c_root_accept_projected",
        "g2c_transition_route_accept_allowed", "SHORTCUT_RETURN_TO_ROOT",
        True, g2b_kind="DIRECT_REUSE_BOUND",
    ),
    _CaseSpecV01(
        "g2c_case:travel:memory_informed:v01", "travel:memory_informed",
        DOMAIN_ORDER[0], "request:g2c:travel:memory_informed:v01", None,
        "memory_informed", "ACCEPT", "ACCEPT",
        "g2c_memory_informed_feasible", "validated_candidate_accepted",
        "g2c_root_accept_projected", "g2c_transition_route_accept_allowed",
        "RUNTIME_TOPOLOGY_ELIGIBLE", True,
        g2b_kind="RESOLUTION_CONTEXT_BOUND",
    ),
    _CaseSpecV01(
        "g2c_case:travel:cloud_llm_narrow:v01", "travel:cloud_llm_narrow",
        DOMAIN_ORDER[0], "request:g2c:travel:cloud_llm_narrow:v01", None,
        "cloud_llm", "NARROW", "NARROW", "g2c_cloud_llm_feasible",
        "validated_candidate_accepted", "g2c_root_narrow_projected",
        "g2c_transition_scope_narrow_allowed", "RUNTIME_TOPOLOGY_ELIGIBLE",
        True, g2b_kind="RESOLUTION_CONTEXT_BOUND",
        accepted_scope_ref="scope:g2c:travel:public_summary:v01",
    ),
    _CaseSpecV01(
        "g2c_case:travel:full_semantic_reject:v01",
        "travel:full_semantic_reject", DOMAIN_ORDER[0],
        "request:g2c:travel:full_semantic_reject:v01",
        "transaction:g2c:travel:full_semantic_reject:v01", "full_semantic",
        "REJECT", "REJECT", "g2c_full_semantic_feasible",
        "policy_rejected_candidate", "g2c_root_reject_projected",
        "g2c_transition_reject_recorded", "TERMINAL_NO_CONSUMPTION", False,
    ),
    _CaseSpecV01(
        "g2c_case:warehouse:deterministic_new_action:v01",
        "warehouse:deterministic_new_action", DOMAIN_ORDER[1],
        "request:g2c:warehouse:deterministic_new_action:v01",
        "transaction:g2c:warehouse:deterministic_new_action:v01",
        "deterministic", "ACCEPT", "ACCEPT", "g2c_deterministic_feasible",
        "validated_candidate_accepted", "g2c_root_accept_projected",
        "g2c_transition_route_accept_allowed", "SHORTCUT_RETURN_TO_ROOT",
        True, action_class="ACTION", action_relation="NEW_ACTION_NO_PACKET",
        packet_required=True,
    ),
    _CaseSpecV01(
        "g2c_case:warehouse:local_slm:v01", "warehouse:local_slm",
        DOMAIN_ORDER[1], "request:g2c:warehouse:local_slm:v01",
        "transaction:g2c:warehouse:local_slm:v01", "local_slm", "ACCEPT",
        "ACCEPT", "g2c_local_slm_feasible", "validated_candidate_accepted",
        "g2c_root_accept_projected", "g2c_transition_route_accept_allowed",
        "RUNTIME_TOPOLOGY_ELIGIBLE", True,
    ),
    _CaseSpecV01(
        "g2c_case:warehouse:full_fractal_fixture_capability:v01",
        "warehouse:full_fractal_fixture_capability", DOMAIN_ORDER[1],
        "request:g2c:warehouse:full_fractal_fixture_capability:v01",
        "transaction:g2c:warehouse:full_fractal_fixture_capability:v01",
        "full_fractal", "ACCEPT", "ACCEPT", "g2c_full_fractal_feasible",
        "validated_candidate_accepted", "g2c_root_accept_projected",
        "g2c_transition_route_accept_allowed", "RUNTIME_TOPOLOGY_ELIGIBLE",
        True, request_class="BOUNDED_FRACTAL_REQUIRED",
    ),
    _CaseSpecV01(
        "g2c_case:warehouse:blocked_existing_packet:v01",
        "warehouse:blocked_existing_packet", DOMAIN_ORDER[1],
        "request:g2c:warehouse:blocked_existing_packet:v01",
        "transaction:g2c:warehouse:blocked_existing_packet:v01", "blocked",
        "TERMINAL_FROM_PROPOSAL", "BLOCKED", "g2c_hard_block_present",
        "hard_policy_violation", "g2c_root_blocked_projected",
        "g2c_transition_blocked_recorded", "TERMINAL_NO_CONSUMPTION", False,
        action_class="ACTION", action_relation="EXISTING_PACKET_ATTEMPT",
        g2a_present=True, hard_block_state="BLOCKED",
    ),
    _CaseSpecV01(
        "g2c_case:warehouse:needs_user:v01", "warehouse:needs_user",
        DOMAIN_ORDER[1], "request:g2c:warehouse:needs_user:v01",
        "transaction:g2c:warehouse:needs_user:v01", "needs_user",
        "TERMINAL_FROM_PROPOSAL", "NEEDS_USER", "g2c_user_input_required",
        "user_permission_missing", "g2c_root_needs_user_projected",
        "g2c_transition_needs_user_recorded", "TERMINAL_NO_CONSUMPTION",
        False, action_class="ACTION", action_relation="NEW_ACTION_NO_PACKET",
        required_user_input_state="MISSING_RESOLVABLE",
    ),
)


@dataclass(frozen=True)
class ExecutionModeRouterG2CCaseResultV01:
    case_id: str
    fixture_id: str
    request_id: str
    transaction_id: str
    owning_root_id: str
    domain_id: str
    semantic_address_id: str | None
    temporal_query_id: str | None
    source_family_sha256: str
    router_input_id: str
    selected_mode: str
    selected_feasibility_row_id: str
    rebuilt_selected_feasibility_row_id: str
    selected_row_reason: str
    proposal_id: str
    proposal_reason_codes: tuple[str, ...]
    review_action: str
    root_review_input_id: str
    root_support_ids: tuple[str, ...]
    source_root_input_id: str
    source_root_result_id: str
    source_root_reason: str
    root_decision_id: str
    root_outcome: str
    root_projection_reason_codes: tuple[str, ...]
    pre_root_transition_id: str
    pre_root_transition_reason: str
    post_root_transition_id: str
    post_root_transition_reason: str
    proposal_artifact_id: str
    decision_artifact_id: str
    route_eligibility_artifact_id: str | None
    downstream_consumption_class: str
    downstream_action_packet_required: bool
    root_review_conflict_set_ids: tuple[str, ...]
    root_input_conflict_set_ids: tuple[str, ...]
    root_result_conflict_set_ids: tuple[str, ...]
    trace_tuples: tuple[tuple[str, ...], ...]
    operation_steps: tuple[str, ...]
    provider_calls: int
    model_calls: int
    gemini_calls: int
    network_calls: int
    connector_calls: int
    external_drs_calls: int
    action_commit_packets_created: int
    permissions_created: int
    receipts_created: int
    topologies_created: int
    drs_writes: int
    final_outputs_created: int
    real_world_effects: int
    final_status: str
    reason_codes: tuple[str, ...]


@dataclass(frozen=True)
class ExecutionModeRouterG2CReportV01:
    report_version: str
    report_id: str
    profile_id: str
    domain_order: tuple[str, ...]
    case_order: tuple[str, ...]
    case_results: tuple[ExecutionModeRouterG2CCaseResultV01, ...]
    provider_calls: int
    model_calls: int
    gemini_calls: int
    network_calls: int
    connector_calls: int
    external_drs_calls: int
    action_commit_packets_created: int
    permissions_created: int
    receipts_created: int
    topologies_created: int
    drs_writes: int
    final_outputs_created: int
    real_world_effects: int
    final_status: str
    reason_codes: tuple[str, ...]


@dataclass(frozen=True)
class _CasePipelineV01:
    spec: _CaseSpecV01
    source_context: router.ExecutionModeSourceContextV01
    router_input: router.ExecutionModeRouterInputV01
    rows: tuple[router.ExecutionModeFeasibilityRowV01, ...]
    selected_row: router.ExecutionModeFeasibilityRowV01
    proposal: router.ExecutionModeProposalV01
    proposal_artifact: abi.KernelArtifactV01
    registry: transition_registry.TransitionRegistryV01
    pre_transition: transition_registry.TransitionDecisionV01
    review_input: router.RootExecutionModeReviewInputV01
    root_kernel: root_decision.RootDecisionKernelV01
    root_input: root_decision.RootDecisionInputV01
    root_result: root_decision.RootDecisionResultV01
    decision: router.RootExecutionModeDecisionV01
    decision_artifact: abi.KernelArtifactV01
    post_transition: transition_registry.TransitionDecisionV01
    route_eligibility: abi.KernelArtifactV01 | None
    semantic_address_id: str | None
    temporal_query_id: str | None


def _sha256_plain(value: object) -> str:
    return hashlib.sha256(canonical_json_bytes_v01(value)).hexdigest()


def _lexical(values: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(sorted(set(values), key=lambda item: item.encode("utf-8")))


def _plain(value: object) -> object:
    if is_dataclass(value) and not isinstance(value, type):
        return {item.name: _plain(getattr(value, item.name)) for item in fields(value)}
    if isinstance(value, tuple):
        return [_plain(item) for item in value]
    if isinstance(value, list):
        return [_plain(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _plain(item) for key, item in value.items()}
    return value


def _build_bsep_family(spec: _CaseSpecV01) -> dict[str, dict[str, object]]:
    label = spec.suffix.replace(":", "_")
    route_id = f"route:g2c:{spec.suffix}:v01"
    proposal_id = f"semantic_proposal:g2c:{spec.suffix}:v01"
    vectors = (f"vector:g2c:{spec.suffix}:v01",)
    guards = ("guard:g2c:root_review:v01",)
    business = context_packets.build_business_request_context_packet(
        packet_id=f"context_packet:g2c:{label}:business:v01",
        created_by="execution_mode_router_g2c5_fixture",
        domain=spec.domain_id,
        request_id=spec.request_id,
        business_subject="execution_mode_route",
        requested_action="bounded_root_review",
        user_visible_summary="Bounded deterministic route evidence.",
    )
    business_ref = {
        "source": "G2C_BUSINESS_REQUEST_CONTEXT_PACKET_V01",
        "packet_id": business["packet_id"],
        "request_id": spec.request_id,
        "domain_id": spec.domain_id,
    }
    route = context_packets.build_orchestrator_route_context_packet(
        packet_id=f"context_packet:g2c:{label}:route:v01",
        created_by="execution_mode_router_g2c5_fixture",
        source_refs=(business_ref,),
        domain=spec.domain_id,
        allowed_routes=(route_id,),
        required_guards=guards,
        selected_vector_ids=vectors,
        route_validation_expectations={
            "root_review_required": True,
            "selected_only_allowed_vectors": True,
        },
        orchestrator_is_root=False,
        creates_action_commit_packet=False,
        calls_connectors=False,
    )
    proposal: dict[str, object] = {
        "proposal_id": proposal_id,
        "suggested_route": route_id,
        "selected_vector_ids": vectors,
        "required_guards": guards,
        "reason": "Deterministic bounded route review is required.",
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
        "semantic_observations": ("A bounded route candidate is present.",),
        "route_reasoning": ("Use deterministic profile evaluation.",),
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

    def item(text: str, evidence_kind: str) -> dict[str, object]:
        return context_packets.semantic_evidence_item(
            text,
            source="runtime_canonicalization",
            evidence_kind=evidence_kind,
            confidence_label="medium",
        )

    packet = context_packets.build_bounded_semantic_evidence_packet(
        packet_id=f"context_packet:g2c:{label}:bsep:v01",
        source_refs=(business_ref,), domain=spec.domain_id,
        source_role="orchestrator", target_role="architect",
        source_route_id=route_id, source_proposal_id=proposal_id,
        source_context_packet_id=route["packet_id"],
        source_structured_rationale_ref="structured_rationale_v01:" + rationale_sha,
        observed_semantic_facts=(item("Bounded route evidence is present.", "observed_fact"),),
        missing_evidence=(item("Root review is pending.", "missing_evidence"),),
        uncertainty_notes=(item("Source evidence remains advisory.", "uncertainty"),),
        risk_boundary_notes=(item("No action authority is present.", "risk_boundary"),),
        rejected_action_routes=(item("Unsupported action remains forbidden.", "rejected_route"),),
        required_approvals_or_conditions=(item("Root review is required.", "approval_condition"),),
        authority_boundary_notes=(item("Root remains final authority.", "authority_boundary"),),
        selected_vector_ids=vectors, required_guards=guards,
    )
    return {"business": business, "route": route, "proposal": proposal,
            "rationale": rationale, "packet": packet}


def _build_replay_family(spec: _CaseSpecV01) -> dict[str, object]:
    label = spec.suffix.replace(":", "_")
    kernel_hash = _sha256_plain((spec.domain_id, spec.case_id, "sealed_replay"))
    programme = evidence_profile.build_programme_evidence_identity_v01(
        programme_id=f"g2c5_{label}_programme_v01", programme_version="v0.1"
    )
    execution = evidence_profile.build_domain_execution_identity_v01(
        programme_identity=programme, domain_id=spec.domain_id,
        execution_head="abcdef1", source_task_id=f"task:g2c:{spec.suffix}:v01",
        run_id=f"run:g2c:{spec.suffix}:v01", report_id=f"report:g2c:{spec.suffix}:v01",
    )
    attempt = evidence_profile.build_live_attempt_identity_v01(
        programme_identity=programme, domain_execution_identity=execution,
        attempt_number=1, package_id=f"package:g2c:{spec.suffix}:v01",
        logical_package_ref=f"g2c5/{label}", output_directory_ref=f"g2c5/{label}/output",
        provider_mode="deterministic_fixture", model_id="none",
        expected_actor_count=1, provider_call_budget=0,
    )
    source = evidence_profile.build_safe_source_record_v01(
        source_id=f"source:g2c:{spec.suffix}:replay:v01",
        source_type="g2c5_replay_fixture", evidence_class="CRYPTOGRAPHIC_INTEGRITY",
        canonical_projection={"domain": spec.domain_id, "hash": kernel_hash},
        media_type="application/json", trace_refs=(kernel_hash,),
        contains_raw_prompt=False, contains_raw_provider_response=False,
        secret_scan_passed=True, observed_provider_call_count=0,
        observed_network_call_count=0, observed_gemini_call_count=0,
        real_world_effects_count=0,
    )
    artifact = evidence_profile.build_evidence_artifact_record_v01(
        artifact_id=f"artifact:g2c:{spec.suffix}:replay:v01",
        artifact_type="g2c5_replay_fixture", evidence_class="CRYPTOGRAPHIC_INTEGRITY",
        source_record_ids=(source.source_record_id,),
        canonical_projection={"domain": spec.domain_id, "hash": kernel_hash},
        authority_class="evidence_only", owner_root_id=None, trace_refs=(kernel_hash,),
        created_authority_count=0, created_permission_count=0,
        real_world_effects_count=0,
    )
    projection = evidence_profile.build_domain_evidence_projection_v01(
        programme_identity=programme, domain_execution_identity=execution,
        attempt_identity=attempt, source_records=(source,), artifact_records=(artifact,),
        kernel_artifact_refs=(), causal_consumption_refs=(),
        evidence_refs=(f"evidence:g2c:{spec.suffix}:replay:v01",),
        limitation_refs=("limitation:g2c:local_only:v01",),
    )
    content = canonical_json_bytes_v01({"domain": spec.domain_id, "hash": kernel_hash}) + b"\n"
    file_record = sealed_package.build_safe_file_record_v01(
        logical_path=f"evidence/{label}.json", media_type="application/json",
        content_bytes=content, evidence_class="CRYPTOGRAPHIC_INTEGRITY",
        source_record_ids=(source.source_record_id,), terminal_newline_required=True,
        secret_scan_passed=True,
    )
    manifest = sealed_package.build_sealed_package_manifest_v01(
        domain_projection=projection, safe_file_records=(file_record,),
        safe_file_contents=(content,), kernel_manifest_hash=kernel_hash,
    )
    publication = external_anchor.build_external_anchor_publication_v01(
        manifest=manifest, domain_projection=projection,
        safe_file_contents=(content,), publication_base_head="abcdef1",
    )
    verification = external_anchor.build_anchored_package_verification_v01(
        anchor_publication=publication, manifest=manifest,
        domain_projection=projection, safe_file_contents=(content,),
        supplied_anchor_publication_id=publication.anchor_publication_id,
    )
    replay = sealed_replay.build_sealed_replay_evidence_v01(
        source_manifest=manifest, source_domain_projection=projection,
        source_safe_file_contents=(content,), anchor_publication=publication,
        anchored_verification=verification,
        supplied_anchor_publication_id=publication.anchor_publication_id,
        reconstructed_manifest=manifest, reconstructed_domain_projection=projection,
        reconstructed_safe_file_contents=(content,),
        evidence_refs=(f"evidence:g2c:{spec.suffix}:replay:v01", f"anchor:g2c:{spec.suffix}:v01"),
    )
    return {"replay": replay, "manifest": manifest, "projection": projection,
            "contents": (content,), "publication": publication,
            "verification": verification}


def _legacy_drs_source(spec: _CaseSpecV01) -> dict[str, object]:
    return {
        "record_id": f"legacy:g2c:{spec.suffix}:v01",
        "layer": "work",
        "type": "generic",
        "domain": spec.domain_id,
        "content": {"summary": "Bounded deterministic G2-C memory context."},
        "time_envelope": {
            "pt_created_at": "2026-08-01T00:00:00Z",
            "kt_asof": "2026-08-01T00:00:00Z",
            "et_observed_at": "2026-08-01T00:00:00Z",
            "ct_session_anchor": spec.case_id,
            "ttl_seconds": 3600,
            "freshness_class": "static",
            "valid_from": "2026-08-01T00:00:00Z",
            "valid_to": "2026-08-01T01:00:00Z",
        },
        "provenance": {
            "request_id": spec.request_id,
            "created_by": "root_orchestrator",
            "trace_refs": [],
        },
        "status": "active",
    }


def _g2b_address(spec: _CaseSpecV01) -> semantic.SemanticAddressV01:
    return semantic.build_semantic_address_v01(
        namespace="g2c_v01", domain=spec.domain_id,
        subject_class="bounded_information", intent_class="informational_summary",
        meaning_schema_id="drs_meaning_record", meaning_schema_version="v0.1",
    )


def _g2b_record(
    *, spec: _CaseSpecV01, address: semantic.SemanticAddressV01,
    scope_sha256: str, reuse_policy_class: str,
) -> semantic.MeaningRecordV01:
    time_envelope = semantic.build_drs_time_envelope_v01(
        pt_created_at=EVALUATION_TIME, kt_as_of=EVALUATION_TIME,
        et_observed_at=EVALUATION_TIME, ct_context_anchor=EVALUATION_TIME,
        ttl_seconds=3600, valid_from=EVALUATION_TIME, valid_to=VALID_TO_TIME,
        source_observed_at=EVALUATION_TIME, source_reported_at=EVALUATION_TIME,
        system_ingested_at=EVALUATION_TIME, system_verified_at=EVALUATION_TIME,
        freshness_policy_id="freshness:g2c:v01",
    )
    authority = semantic.build_drs_authority_envelope_v01(
        authority_class=(
            "ROOT_ACCEPTED_WORK"
            if reuse_policy_class == "ANSWER_SHORTCUT"
            else "ROOT_ACCEPTED_CONTEXT"
        ),
        owning_local_root_id=ROOT_BY_DOMAIN[spec.domain_id],
        source_root_decision_input_id=f"root-input:g2c:{spec.suffix}:source:v01",
        source_root_decision_id=f"root-decision:g2c:{spec.suffix}:source:v01",
        source_root_decision_hash=_sha256_plain((spec.case_id, "source_root")),
        authority_scope_fingerprint=scope_sha256,
        root_acceptance_state=(
            "ACCEPTED_WORK"
            if reuse_policy_class == "ANSWER_SHORTCUT"
            else "ACCEPTED_CONTEXT"
        ),
        recording_component="execution_mode_router_g2c5_fixture",
    )
    return semantic.build_meaning_record_v01(
        semantic_address=address, predecessor_record_id=None,
        supersession_reason=None,
        safe_summary="Bounded deterministic information for Root review.",
        semantic_tags=("bounded", "g2c", "informational"),
        resonance_reason="Exact deterministic semantic-address match.",
        memory_pointers=(), artifact_pointers=(),
        source_reference_ids=(f"source:g2c:{spec.suffix}:memory:v01",),
        lineage_edges=(), time_envelope=time_envelope,
        authority_envelope=authority, persistent_lifecycle_state="ACTIVE",
        risk_hints=(), conflict_hints=(),
        reuse_policy_class=reuse_policy_class,
        policy_version=f"policy:g2c:{spec.suffix}:v01",
        schema_versions=("v0.1",),
        content_fingerprint=_sha256_plain((spec.case_id, "meaning_record")),
        recording_component="execution_mode_router_g2c5_fixture",
    )


def _g2b_query(
    *, spec: _CaseSpecV01, address: semantic.SemanticAddressV01,
    scope_sha256: str,
) -> resolution.DRSTemporalQueryV01:
    direct = spec.g2b_kind == "DIRECT_REUSE_BOUND"
    return resolution.build_drs_temporal_query_v01(
        query_mode="DIRECT_REUSE_CANDIDATE" if direct else "MEMORY_CONTEXT_ONLY",
        semantic_address_id=address.semantic_address_id,
        scope_fingerprint=scope_sha256, as_of=EVALUATION_TIME,
        evaluation_time=EVALUATION_TIME,
        evaluation_time_source=(
            "INJECTED_CURRENT_DECISION_TIME" if direct else "INJECTED_ANALYSIS_TIME"
        ),
        time_range_start=EVALUATION_TIME, time_range_end=VALID_TO_TIME,
        required_time_axes=(
            ("PT", "KT", "ET", "CT", "TTL", "VALIDITY")
            if direct else ("KT", "TTL", "VALIDITY")
        ),
        freshness_policy_id="freshness:g2c:v01", max_age_seconds=3600,
        domain=spec.domain_id, risk_class="LOW",
        reuse_intent=(
            "INFORMATIONAL_SHORTCUT_CONSIDERATION" if direct else "CONTEXT"
        ),
        requested_reuse_classes=("ANSWER_SHORTCUT",) if direct else ("CONTEXT_ONLY",),
        required_evidence_classes=G2B_EVIDENCE_CLASSES,
        forbidden_changes=("POLICY_CHANGED",),
        policy_version=f"policy:g2c:{spec.suffix}:v01",
        schema_versions=("v0.1",),
        owning_local_root_id=ROOT_BY_DOMAIN[spec.domain_id],
    )


def _g2b_plan(
    *, query: resolution.DRSTemporalQueryV01,
    address: semantic.SemanticAddressV01,
    record: semantic.MeaningRecordV01,
) -> resolution.RetrievalPlanV01:
    budget = resolution.build_memory_descent_budget_v01(
        max_depth=0, max_records_opened=1, max_pointers_opened=0,
        max_artifacts_opened=0, max_bytes_opened=0, max_lineage_edges=0,
        max_conflict_records=0,
    )
    return resolution.build_retrieval_plan_v01(
        query_id=query.query_id, semantic_address_id=address.semantic_address_id,
        proposed_record_ids=(record.meaning_record_id,),
        proposed_memory_pointer_ids=(), proposed_artifact_pointer_ids=(),
        requested_descent_class="SUMMARY_ONLY",
        proposed_budget_id=budget.memory_descent_budget_id,
        required_access_policy_ids=(), reason_codes=(),
    )


def _g2b_root_states(candidate_id: str, spec: _CaseSpecV01) -> dict[str, object]:
    return {
        "post_vv_bundle": {
            "bundle_id": f"post-vv:g2c:{spec.suffix}:shortcut:v01",
            "post_vv_passed": True, "validated_candidate_ids": [candidate_id],
            "rejected_candidate_ids": [], "required_evidence_refs": [],
            "provided_evidence_refs": [], "hard_failure_reasons": [],
        },
        "gt_advisory": {
            "advisory_id": f"gt:g2c:{spec.suffix}:shortcut:v01",
            "candidate_ids": [candidate_id], "selected_candidate_id": candidate_id,
            "score_micros_by_candidate": {candidate_id: 500000},
            "source_artifact_type": "GTAdvisoryReport",
            "source_lifecycle_state": "VALIDATED", "actor_role": "gt",
            "attempted_effect": "CREATE_ROOT_DECISION",
            "target_artifact_type": "RootDecision", "advisory_only": True,
            "creates_final_output": False, "requests_effect": False,
        },
        "policy_state": {
            "policy_id": f"policy:g2c:{spec.suffix}:shortcut:v01",
            "identity_passed": True, "scope_passed": True,
            "hard_policy_passed": True, "allow_accept": True,
            "conflict_policy": "DEFER", "no_candidate_policy": "NO_UPDATE",
        },
        "permission_state": {
            "permission_required": False, "user_permission_present": False,
            "permission_scope_valid": True, "permission_ref": None,
        },
        "temporal_state": {
            "temporal_valid": True, "expired": False,
            "not_before_satisfied": True,
            "time_envelope_ref": f"time-envelope:g2c:{spec.suffix}:shortcut:v01",
        },
        "conflict_state": {
            "material_unresolved_conflict": False, "conflict_set_ids": [],
        },
        "prior_root_state": {
            "prior_decision_id": None, "prior_decision": None,
            "prior_selected_candidate_id": None,
        },
    }


def _g2b_root_triple(
    *, spec: _CaseSpecV01, query: resolution.DRSTemporalQueryV01,
    address: semantic.SemanticAddressV01,
    candidate: resolution.ResolutionCandidateV01,
    claim_preimage: dict[str, object],
) -> tuple[root_decision.RootDecisionKernelV01,
           root_decision.RootDecisionInputV01,
           root_decision.RootDecisionResultV01]:
    actor_id = f"actor:g2c:{spec.suffix}:shortcut:v01"
    request = semantic_work.build_semantic_work_request_v01(
        request_id=f"semantic-work-request:g2c:{spec.suffix}:shortcut:v01",
        transaction_id=query.query_id,
        target_root_id=ROOT_BY_DOMAIN[spec.domain_id],
        runtime_topology_ref="g2c:runtime_topology:not_created:v01",
        bounded_context_refs=(f"context:g2c:{spec.suffix}:shortcut:v01",),
        permitted_actor_ids=(actor_id,), permitted_contribution_modes=("DETERMINISTIC",),
        requested_subjects=(address.semantic_address_id,),
        required_evidence_classes=("ROOT_SHORTCUT_BINDING",),
        forbidden_claims=("create_permission",),
    )
    evidence = semantic_work.build_evidence_binding_v01(
        evidence_id=f"evidence-binding:g2c:{spec.suffix}:shortcut:v01",
        evidence_ref=f"evidence:g2c:{spec.suffix}:shortcut:v01",
        evidence_class="ROOT_SHORTCUT_BINDING", source_component_id=actor_id,
        provenance_ref=f"provenance:g2c:{spec.suffix}:shortcut:v01",
        evidence_state=semantic_work.EVIDENCE_STATE_PRESENT,
    )
    claim = semantic_work.build_normalized_claim_v01(
        claim_id=candidate.resolution_candidate_id,
        subject=address.semantic_address_id, predicate=G2B_DIRECT_ROOT_PREDICATE,
        object_or_value=claim_preimage,
        time_envelope_ref=f"time-envelope:g2c:{spec.suffix}:shortcut:v01",
        provenance_refs=(f"provenance:g2c:{spec.suffix}:shortcut:v01",),
        evidence_refs=(evidence.evidence_id,), confidence_micros=1000000,
        source_role="deterministic_runtime", source_mode="DETERMINISTIC",
    )
    contribution = semantic_work.build_actor_contribution_v01(
        contribution_id=f"contribution:g2c:{spec.suffix}:shortcut:v01",
        request_id=request.request_id, actor_id=actor_id,
        actor_role="deterministic_runtime", contribution_mode="DETERMINISTIC",
        bsep_projection_ref=f"bsep:g2c:{spec.suffix}:shortcut:v01",
        scope=address.semantic_address_id,
        bounded_context_refs=(f"context:g2c:{spec.suffix}:shortcut:v01",),
        claims=(claim,), evidence_bindings=(evidence,), constraint_bindings=(),
        uncertainty_bindings=(), requested_validators=(),
        forbidden_claims_observed=(),
    )
    packet = semantic_work.build_root_review_packet_from_contributions_v01(
        request=request, contributions=(contribution,),
        trust_profiles=build_default_component_trust_profiles_v01(),
    )
    kernel = root_decision.build_root_decision_kernel_v01()
    decision_input = root_decision.build_root_decision_input_v01(
        transaction_id=query.query_id,
        target_root_id=ROOT_BY_DOMAIN[spec.domain_id],
        root_review_packet=packet, **_g2b_root_states(candidate.resolution_candidate_id, spec),
    )
    result = root_decision.decide_root_v01(kernel=kernel, decision_input=decision_input)
    if result.decision != "ACCEPT":
        raise ValueError("g2c5_g2b_root_invalid")
    return kernel, decision_input, result


def _build_g2b_family(spec: _CaseSpecV01, scope_ref: str) -> dict[str, object]:
    address = _g2b_address(spec)
    scope_sha256 = hashlib.sha256(scope_ref.encode("utf-8")).hexdigest()
    direct = spec.g2b_kind == "DIRECT_REUSE_BOUND"
    record = _g2b_record(
        spec=spec, address=address, scope_sha256=scope_sha256,
        reuse_policy_class="ANSWER_SHORTCUT" if direct else "CONTEXT_ONLY",
    )
    query = _g2b_query(spec=spec, address=address, scope_sha256=scope_sha256)
    evaluation = resolution.evaluate_drs_candidate_v01(
        semantic_address=address, query=query, meaning_record=record,
        action_history_binding=None,
    )
    projection = compatibility.build_legacy_drs_projection_v01(
        source_family="LOCAL_DRS_DICT", source=_legacy_drs_source(spec),
        target_semantic_address=address,
    )
    plan = _g2b_plan(query=query, address=address, record=record)
    common = {
        "semantic_address": address, "query": query,
        "source_projections": (projection,), "source_records": (record,),
        "query_evaluations": (evaluation,), "retrieval_plan": plan,
        "memory_descent_result": None, "historical_only_record_ids": (),
        "warning_only_record_ids": (), "rerun_required_record_ids": (),
        "blocked_record_ids": (), "provider_calls": 0, "network_calls": 0,
        "gemini_calls": 0, "external_drs_calls": 0, "connector_calls": 0,
        "real_world_effects_count": 0, "final_status": "PASS", "reason_codes": (),
    }
    if not direct:
        if evaluation.query_state != "STALE_CONTEXT_ONLY":
            raise ValueError("g2c5_g2b_context_invalid")
        report = resolution.build_drs_resolution_report_v01(
            **common, eligible_candidates=(), ranked_candidate_ids=(),
            selected_candidate_id=None, root_shortcut_projection=None,
            reuse_certificate=None, context_only_record_ids=(record.meaning_record_id,),
        )
        return {"address": address, "query": query, "report": report,
                "projections": (projection,), "use_time": EVALUATION_TIME}

    candidate = resolution.build_resolution_candidate_v01(
        query_id=query.query_id, semantic_address_id=query.semantic_address_id,
        meaning_record_id=record.meaning_record_id,
        query_evaluation_id=evaluation.query_evaluation_id,
        safe_summary=record.safe_summary, evidence_ref_ids=record.source_reference_ids,
        source_history_hash=evaluation.source_history_hash,
        action_history_binding_id=None, semantic_similarity_units=9000,
        freshness_units=evaluation.current_freshness_units,
        source_authority_prior_units=9000, lineage_proximity_units=7000,
        historical_utility_units=6000, gt_advisory_prior_units=1000,
        conflict_penalty_units=0, risk_penalty_units=0, retrieval_cost_units=100,
    )
    ranked = resolution.rank_eligible_drs_candidates_v01(
        query=query, query_evaluations=(evaluation,), candidates=(candidate,),
    )
    claim_preimage = {
        "profile_version": "v0.1", "semantic_address_id": address.semantic_address_id,
        "meaning_record_id": record.meaning_record_id, "query_id": query.query_id,
        "query_evaluation_id": evaluation.query_evaluation_id,
        "resolution_candidate_id": candidate.resolution_candidate_id,
        "reuse_class": "ANSWER_SHORTCUT", "case_type": "NON_ACTION_INFORMATIONAL",
        "scope_fingerprint": query.scope_fingerprint,
        "policy_version": query.policy_version,
        "schema_versions": list(query.schema_versions),
        "required_evidence_classes": list(query.required_evidence_classes),
        "observed_evidence_fingerprint": evaluation.observed_evidence_fingerprint,
        "forbidden_changes": list(query.forbidden_changes),
        "checked_dependency_fingerprint": evaluation.checked_dependency_fingerprint,
        "source_history_hash": evaluation.source_history_hash,
        "action_history_binding_id": None, "valid_from": EVALUATION_TIME,
        "valid_to": VALID_TO_TIME, "issued_at": EVALUATION_TIME,
        "evaluated_at": evaluation.evaluated_at,
        "root_shortcut_policy_ref": G2B_DIRECT_POLICY_REF,
    }
    kernel, root_input, root_result = _g2b_root_triple(
        spec=spec, query=query, address=address, candidate=candidate,
        claim_preimage=claim_preimage,
    )
    root_hash = domain_separated_sha256_hex_v01(
        domain=G2B_DIRECT_ROOT_BINDING_DOMAIN,
        payload=canonical_json_bytes_v01(
            root_decision.root_decision_result_to_plain_dict_v01(root_result)
        ),
    )
    root_projection = reuse.build_root_shortcut_authorization_projection_v01(
        owning_local_root_id=ROOT_BY_DOMAIN[spec.domain_id],
        root_kernel_id=kernel.kernel_id, root_decision_input_id=root_input.decision_input_id,
        root_decision_id=root_result.decision_id, root_decision_hash=root_hash,
        selected_candidate_id=candidate.resolution_candidate_id,
        semantic_address_id=address.semantic_address_id,
        meaning_record_id=record.meaning_record_id, query_id=query.query_id,
        query_evaluation_id=evaluation.query_evaluation_id,
        allowed_reuse_class="ANSWER_SHORTCUT", scope_fingerprint=scope_sha256,
        policy_version=query.policy_version, schema_versions=query.schema_versions,
        valid_from=EVALUATION_TIME, valid_to=VALID_TO_TIME,
        root_shortcut_policy_ref=G2B_DIRECT_POLICY_REF,
    )
    certificate = reuse.build_reuse_certificate_v01(
        semantic_address_id=address.semantic_address_id,
        meaning_record_id=record.meaning_record_id, query_id=query.query_id,
        query_evaluation_id=evaluation.query_evaluation_id,
        resolution_candidate_id=candidate.resolution_candidate_id,
        root_shortcut_authorization_projection=root_projection,
        case_type="NON_ACTION_INFORMATIONAL",
        required_evidence_classes=query.required_evidence_classes,
        observed_evidence_fingerprint=evaluation.observed_evidence_fingerprint,
        forbidden_changes=query.forbidden_changes,
        checked_dependency_fingerprint=evaluation.checked_dependency_fingerprint,
        valid_from=EVALUATION_TIME, valid_to=VALID_TO_TIME,
        reuse_class="ANSWER_SHORTCUT", source_history_hash=evaluation.source_history_hash,
        action_history_binding_id=None, issued_at=EVALUATION_TIME,
        evaluated_at=evaluation.evaluated_at,
    )
    report = resolution.build_drs_resolution_report_v01(
        **common, eligible_candidates=(candidate,),
        ranked_candidate_ids=tuple(item.resolution_candidate_id for item in ranked),
        selected_candidate_id=candidate.resolution_candidate_id,
        root_shortcut_projection=root_projection, reuse_certificate=certificate,
        context_only_record_ids=(),
    )
    if reuse.validate_existing_root_shortcut_decision_v01(
        resolution_report=report, root_kernel=kernel,
        root_decision_input=root_input, root_decision_result=root_result,
        use_time=EVALUATION_TIME,
    ) != (True, ()):
        raise ValueError("g2c5_g2b_shortcut_invalid")
    return {"address": address, "query": query, "report": report,
            "projections": (projection,), "use_time": EVALUATION_TIME,
            "root_kernel": kernel, "root_input": root_input,
            "root_result": root_result}


ACTION_SOURCE_TIME = 1783470600
ACTION_TIME_SOURCE = "explicit_g2c5_action_source_time"


def _action_authority_policy(root_id: str) -> action_packet.ActionAuthorityPolicyProfileV01:
    return action_packet.build_action_authority_policy_profile_v01(
        policy_version="g2c5_action_policy_v01", owning_local_root_id=root_id,
        authority_rule_refs=("authority_rule:g2c5_mock_action",),
        kill_switch_condition_refs=("kill_switch:g2c5_active",),
        retry_policy="NON_CONSUMING_RETRY",
        supersession_policy="ROOT_DECISION_ONLY",
        logical_effect_namespace="g2c5.synthetic_effect.v01",
        allowed_logical_effect_classes=("PAYMENT",),
        allowed_business_object_namespaces=("g2c5.synthetic_business_object.v01",),
        allowed_corridor_classes=("g2c5_mock_corridor",),
    )


def _action_root_evidence(
    canonical: action_packet.SupplierActionCommitPacketCanonicalProjectionV01,
    spec: _CaseSpecV01,
) -> tuple[root_decision.RootDecisionKernelV01,
           root_decision.RootDecisionInputV01,
           root_decision.RootDecisionResultV01]:
    candidate_id = canonical.authorization_candidate.root_packet_authorization_candidate_id
    actor_id = "runtime:g2c5_action_authorization"
    context_ref = f"context:g2c:{spec.suffix}:action:v01"
    request = semantic_work.build_semantic_work_request_v01(
        request_id=f"semantic_request:g2c:{spec.suffix}:action:v01",
        transaction_id=canonical.transaction_id,
        target_root_id=canonical.owning_local_root_id,
        runtime_topology_ref="g2c:runtime_topology:not_created:v01",
        bounded_context_refs=(context_ref,), permitted_actor_ids=(actor_id,),
        permitted_contribution_modes=("DETERMINISTIC",),
        requested_subjects=(f"action_commit_packet:{spec.suffix}",),
        required_evidence_classes=("DEPENDENCY_EVIDENCE",),
        forbidden_claims=("authority_creation",),
    )
    dependency = canonical.dependency_candidate.dependency_records[0]
    evidence = semantic_work.build_evidence_binding_v01(
        evidence_id=f"evidence_binding:g2c:{spec.suffix}:action:v01",
        evidence_ref=dependency.evidence_ref,
        evidence_class="DEPENDENCY_EVIDENCE",
        source_component_id="deterministic_runtime",
        provenance_ref=dependency.source_provenance_refs[0],
        evidence_state=semantic_work.EVIDENCE_STATE_PRESENT,
    )
    claim = semantic_work.build_normalized_claim_v01(
        claim_id=candidate_id, subject=f"action_commit_packet:{spec.suffix}",
        predicate="root_packet_authorization_candidate",
        object_or_value={"candidate_id": candidate_id,
                         "candidate_kind": "PACKET_AUTHORIZATION"},
        time_envelope_ref=canonical.temporal_authority_fingerprint,
        provenance_refs=(f"provenance:g2c:{spec.suffix}:action:v01",),
        evidence_refs=(evidence.evidence_id,), confidence_micros=1000000,
        source_role="deterministic_runtime", source_mode="DETERMINISTIC",
    )
    contribution = semantic_work.build_actor_contribution_v01(
        contribution_id=f"contribution:g2c:{spec.suffix}:action:v01",
        request_id=request.request_id, actor_id=actor_id,
        actor_role="deterministic_runtime", contribution_mode="DETERMINISTIC",
        bsep_projection_ref=f"bsep:g2c:{spec.suffix}:action:v01",
        scope="scope:g2c5_action_authorization", bounded_context_refs=(context_ref,),
        claims=(claim,), evidence_bindings=(evidence,), constraint_bindings=(),
        uncertainty_bindings=(),
        requested_validators=("validator:g2c5_action_authorization",),
        forbidden_claims_observed=(),
    )
    review = semantic_work.build_root_review_packet_from_contributions_v01(
        request=request, contributions=(contribution,),
        trust_profiles=build_default_component_trust_profiles_v01(),
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
            "bundle_id": f"post_vv:g2c:{spec.suffix}:action:v01",
            "post_vv_passed": True, "validated_candidate_ids": [candidate_id],
            "rejected_candidate_ids": [], "required_evidence_refs": mandatory_refs,
            "provided_evidence_refs": mandatory_refs, "hard_failure_reasons": [],
        },
        gt_advisory={
            "advisory_id": f"gt:g2c:{spec.suffix}:action:v01",
            "candidate_ids": [candidate_id], "selected_candidate_id": candidate_id,
            "score_micros_by_candidate": {candidate_id: 1000000},
            "source_artifact_type": "GTAdvisoryReport",
            "source_lifecycle_state": "VALIDATED", "actor_role": "gt",
            "attempted_effect": "CREATE_ROOT_DECISION",
            "target_artifact_type": "RootDecision", "advisory_only": True,
            "creates_final_output": False, "requests_effect": False,
        },
        policy_state={
            "policy_id": canonical.authority_policy_fingerprint,
            "identity_passed": True, "scope_passed": True,
            "hard_policy_passed": True, "allow_accept": True,
            "conflict_policy": "DEFER", "no_candidate_policy": "NO_UPDATE",
        },
        permission_state={
            "permission_required": True, "user_permission_present": True,
            "permission_scope_valid": True,
            "permission_ref": canonical.canonical_permission_ref,
        },
        temporal_state={
            "temporal_valid": True, "expired": False,
            "not_before_satisfied": True,
            "time_envelope_ref": canonical.temporal_authority_fingerprint,
        },
        conflict_state={"material_unresolved_conflict": False,
                        "conflict_set_ids": list(review.conflict_set_ids)},
        prior_root_state={"prior_decision_id": None, "prior_decision": None,
                          "prior_selected_candidate_id": None},
    )
    result = root_decision.decide_root_v01(kernel=kernel, decision_input=decision_input)
    return kernel, decision_input, result


def _action_transition_bindings(
    rule_id: str,
) -> tuple[action_packet.TransitionEvidenceBindingV01, ...]:
    profile = transition_registry.build_action_packet_transition_registry_profile_v01()
    rule = transition_registry.lookup_action_packet_transition_rule_v01(
        registry=profile, transition_rule_id=rule_id,
    )
    return tuple(
        action_packet.build_transition_evidence_binding_v01(
            action_packet_transition_registry_profile=profile,
            transition_rule_id=rule_id, evidence_code=code,
            evidence_ref=f"evidence:g2c5:{code}", evidence_sha256="d" * 64,
            validator_profile_id="validator:g2c5_action_transition",
        )
        for code in rule.required_evidence_codes
    )


def _action_transition_event(
    entry: action_packet.ActionPacketLifecycleEntryV01,
    rule_id: str,
    *, evaluation_context_id: str,
) -> action_packet.ActionPacketTransitionEventV01:
    canonical = entry.root_bound_genesis.canonical_projection
    packet_id = entry.root_bound_genesis.packet_identity.packet_id
    attempt = None
    if rule_id == "g2a_t03_pending":
        attempt = action_packet.build_action_execution_attempt_identity_v01(
            packet_id=packet_id,
            idempotency_key=canonical.idempotency_identity.idempotency_key,
            attempt_ordinal=1, evaluation_context_id=evaluation_context_id,
        )
    return action_packet.build_action_packet_transition_event_v01(
        action_packet_transition_registry_profile=(
            transition_registry.build_action_packet_transition_registry_profile_v01()
        ),
        transition_rule_id=rule_id, packet_id=packet_id,
        idempotency_key=canonical.idempotency_identity.idempotency_key,
        previous_transition_event_id=(
            entry.transition_events[-1].transition_event_id
            if entry.transition_events else None
        ),
        owning_local_root_id=canonical.owning_local_root_id,
        root_decision_ref=(
            entry.root_bound_genesis.root_decision_projection.root_decision_result.decision_id
            if rule_id == "g2a_t01_activate_root_authorization" else None
        ),
        transition_evidence_bindings=_action_transition_bindings(rule_id),
        dependency_set_candidate_fingerprint=canonical.dependency_set_candidate_fingerprint,
        temporal_authority_fingerprint=canonical.temporal_authority_fingerprint,
        evaluation_time=ACTION_SOURCE_TIME + len(entry.transition_events),
        evaluation_time_source=ACTION_TIME_SOURCE,
        evaluation_context_id=evaluation_context_id,
        execution_attempt_identity=attempt, receipt_ref=None,
    )


def _build_g2a_pending_source(spec: _CaseSpecV01) -> SimpleNamespace:
    root_id = ROOT_BY_DOMAIN[spec.domain_id]
    source = action_packet.build_supplier_a_mock_action_commit_packet_fixture_v02()
    temporal = action_packet.project_packet_ttl_compatibility_v01(
        source.ttl, evaluation_time=ACTION_SOURCE_TIME,
        temporal_policy_version="packet_ttl_v01",
    ).temporal_authority
    dependency_id = "dependency:g2c5:warehouse:existing_packet:v01"
    evidence_ref = "evidence:g2c5:warehouse:existing_packet:v01"
    provenance = "source:g2c5:warehouse:existing_packet:v01"
    envelope = action_packet.build_action_dependency_time_envelope_id_v01(
        dependency_id=dependency_id, evidence_ref=evidence_ref,
        content_sha256="a" * 64, freshness_policy_id="freshness_policy:g2c5_current",
        source_provenance_refs=(provenance,),
        valid_from_utc=temporal.issued_at_utc, valid_to_utc=temporal.expires_at_utc,
    )
    dependency = action_packet.build_dependency_set_candidate_v01(
        dependency_records=(
            action_packet.build_dependency_set_candidate_record_v01(
                dependency_id=dependency_id,
                dependency_class="SYNTHETIC_DOMAIN_EVIDENCE",
                evidence_ref=evidence_ref, content_sha256="a" * 64,
                requirement_class="MANDATORY", time_envelope_id=envelope,
                freshness_policy_id="freshness_policy:g2c5_current",
                source_provenance_refs=(provenance,),
                expected_accepting_local_root_id=root_id,
            ),
        )
    )
    canonical = action_packet.build_supplier_action_commit_packet_canonical_projection_v01(
        source, transaction_id=spec.literal_transaction_id,
        owning_local_root_id=root_id,
        canonical_permission_ref="permission:g2c5_mock_action",
        selected_legacy_action=action_packet.ACTION_MOCK_SUPPLIER_A_PAYMENT_ORDER,
        logical_effect_namespace="g2c5.synthetic_effect.v01",
        business_object_namespace="g2c5.synthetic_business_object.v01",
        corridor_class="g2c5_mock_corridor",
        adapter_version=action_packet.PRE_G2A_ADAPTER_VERSION_V01,
        temporal_policy_version="packet_ttl_v01",
        authority_policy=_action_authority_policy(root_id),
        dependency_candidate=dependency, evaluation_time=ACTION_SOURCE_TIME,
        evaluation_time_source=ACTION_TIME_SOURCE,
        evaluation_context_id="evaluation_context:g2c5:warehouse:canonical:v01",
    )
    kernel, decision_input, result = _action_root_evidence(canonical, spec)
    root_projection = action_packet.build_root_decision_candidate_projection_v01(
        candidate_kind=action_packet.ROOT_DECISION_CANDIDATE_KIND_PACKET_AUTHORIZATION_V01,
        projected_candidate_id=canonical.authorization_candidate.root_packet_authorization_candidate_id,
        root_decision_kernel=kernel, root_decision_input=decision_input,
        root_decision_result=result,
    )
    root_bound = action_packet.build_supplier_root_bound_action_commit_packet_v02_projection_v01(
        canonical_projection=canonical, root_decision_projection=root_projection,
    )
    profile = transition_registry.build_action_packet_transition_registry_profile_v01()
    registry = action_packet.record_action_packet_genesis_v01(
        action_packet.build_empty_action_commit_packet_registry_v02(),
        root_bound_genesis=root_bound,
        action_packet_transition_registry_profile=profile,
    )
    packet_id = root_bound.packet_identity.packet_id
    entry = registry.action_packet_lifecycle_entries[0]
    activation = _action_transition_event(
        entry, "g2a_t01_activate_root_authorization",
        evaluation_context_id="evaluation_context:g2c5:warehouse:activate:v01",
    )
    evidence_ids = tuple(sorted(
        (binding.transition_evidence_binding_id
         for binding in activation.transition_evidence_bindings
         if binding.evidence_code in {
             "packet_genesis_valid", "source_root_authorization_valid",
             "idempotency_acquisition_valid",
         }), key=lambda item: item.encode("utf-8")
    ))
    reserve = action_packet.build_idempotency_disposition_event_v01(
        idempotency_key=canonical.idempotency_identity.idempotency_key,
        event_class="RESERVE", from_disposition="UNCLAIMED",
        to_disposition="RESERVED", from_owner_packet_id=None,
        to_owner_packet_id=packet_id, previous_disposition_event_id=None,
        cause_transition_event_ids=(activation.transition_event_id,),
        root_decision_ref=result.decision_id, predecessor_packet_id=None,
        successor_packet_id=None, evidence_refs=evidence_ids,
        evaluation_time=activation.evaluation_time,
        evaluation_time_source=activation.evaluation_time_source,
        evaluation_context_id=activation.evaluation_context_id,
    )
    registry = action_packet.activate_action_packet_lifecycle_v01(
        registry, packet_id=packet_id, transition_event=activation,
        disposition_event=reserve, action_packet_transition_registry_profile=profile,
    )
    for rule_id in ("g2a_t02_queue", "g2a_t03_pending"):
        event = _action_transition_event(
            registry.action_packet_lifecycle_entries[0], rule_id,
            evaluation_context_id=f"evaluation_context:g2c5:warehouse:{rule_id}:v01",
        )
        registry = action_packet.append_action_packet_lifecycle_transition_v01(
            registry, packet_id=packet_id, transition_event=event,
            action_packet_transition_registry_profile=profile,
        )
    step = replace(
        action_packet.build_supplier_a_corridor_step_fixture_v01(source),
        parent_packet_id=packet_id, allowed_subjects=source.scope.allowed_subjects,
    )
    corridor = action_packet.ContractFulfillmentCorridorV01(
        corridor_id="corridor:g2c5:warehouse:existing_packet:v01",
        packet_id=packet_id, corridor_kind=canonical.adapter_binding.corridor_class,
        allowed_steps=(step.step_id,),
    )
    observations = (
        action_packet.build_action_dependency_current_observation_v01(
            dependency_id=dependency_id, evidence_ref=evidence_ref,
            observed_content_sha256="a" * 64, time_envelope_id=envelope,
            freshness_policy_id="freshness_policy:g2c5_current",
            source_provenance_refs=(provenance,),
            valid_from_utc=temporal.issued_at_utc,
            valid_to_utc=temporal.expires_at_utc,
            observed_at_utc=ACTION_SOURCE_TIME,
            observation_context_id="evaluation_context:g2c5:warehouse:source:v01",
        ),
    )
    bridge = action_packet.build_logical_time_bridge_v01(
        origin_utc_epoch_seconds=temporal.issued_at_utc, seconds_per_tick=1,
        bridge_policy_version="g2c5_epoch_seconds_v01",
    )
    return SimpleNamespace(
        root_bound=root_bound, registry=registry, corridor=corridor,
        corridor_step=step, observations=observations,
        logical_time_bridge=bridge,
    )


def _bind_g2a_inspection(
    source: SimpleNamespace,
    snapshot: router.ExecutionModeLocalRoutingSnapshotV01,
) -> SimpleNamespace:
    observations = tuple(
        action_packet.build_action_dependency_current_observation_v01(
            dependency_id=item.dependency_id, evidence_ref=item.evidence_ref,
            observed_content_sha256=item.observed_content_sha256,
            time_envelope_id=item.time_envelope_id,
            freshness_policy_id=item.freshness_policy_id,
            source_provenance_refs=item.source_provenance_refs,
            valid_from_utc=item.valid_from_utc, valid_to_utc=item.valid_to_utc,
            observed_at_utc=item.observed_at_utc,
            observation_context_id=snapshot.local_routing_snapshot_id,
        )
        for item in source.observations
    )
    inspection = action_packet.inspect_action_packet_present_eligibility_v01(
        source.registry, packet_id=source.root_bound.packet_identity.packet_id,
        corridor=source.corridor, corridor_step=source.corridor_step,
        current_dependency_observations=observations,
        logical_time_bridge=source.logical_time_bridge,
        evaluation_time=EVALUATION_TIME,
        evaluation_time_source=snapshot.created_by,
        evaluation_context_id=snapshot.local_routing_snapshot_id,
        action_packet_transition_registry_profile=(
            transition_registry.build_action_packet_transition_registry_profile_v01()
        ),
    )
    if inspection.present_eligibility_status != "NON_EXECUTABLE":
        raise ValueError("g2c5_g2a_present_state_invalid")
    return SimpleNamespace(
        inspection=inspection, registry=source.registry, root_bound=source.root_bound,
        corridor=source.corridor, corridor_step=source.corridor_step,
        observations=observations, logical_time_bridge=source.logical_time_bridge,
    )


PROFILE_STATES = (
    ("UNAVAILABLE", "NOT_REQUIRED", "NOT_REQUIRED", "UNAVAILABLE", "UNAVAILABLE", "UNAVAILABLE", "UNAVAILABLE", "UNAVAILABLE"),
    ("UNAVAILABLE", "NOT_REQUIRED", "NOT_REQUIRED", "UNAVAILABLE", "UNAVAILABLE", "UNAVAILABLE", "UNAVAILABLE", "UNAVAILABLE"),
    ("UNAVAILABLE", "NOT_REQUIRED", "NOT_REQUIRED", "AVAILABLE", "UNAVAILABLE", "UNAVAILABLE", "UNAVAILABLE", "UNAVAILABLE"),
    ("UNAVAILABLE", "NOT_REQUIRED", "NOT_REQUIRED", "UNAVAILABLE", "UNAVAILABLE", "AVAILABLE", "UNAVAILABLE", "UNAVAILABLE"),
    ("UNAVAILABLE", "NOT_REQUIRED", "NOT_REQUIRED", "UNAVAILABLE", "UNAVAILABLE", "UNAVAILABLE", "AVAILABLE", "UNAVAILABLE"),
    ("AVAILABLE", "NOT_REQUIRED", "NOT_REQUIRED", "UNAVAILABLE", "UNAVAILABLE", "UNAVAILABLE", "UNAVAILABLE", "UNAVAILABLE"),
    ("UNAVAILABLE", "NOT_REQUIRED", "NOT_REQUIRED", "UNAVAILABLE", "AVAILABLE", "UNAVAILABLE", "UNAVAILABLE", "UNAVAILABLE"),
    ("UNAVAILABLE", "NOT_REQUIRED", "NOT_REQUIRED", "UNAVAILABLE", "UNAVAILABLE", "UNAVAILABLE", "UNAVAILABLE", "AVAILABLE"),
    ("UNAVAILABLE", "NOT_REQUIRED", "NOT_REQUIRED", "UNAVAILABLE", "UNAVAILABLE", "UNAVAILABLE", "UNAVAILABLE", "UNAVAILABLE"),
    ("UNAVAILABLE", "NOT_REQUIRED", "NOT_REQUIRED", "UNAVAILABLE", "UNAVAILABLE", "UNAVAILABLE", "UNAVAILABLE", "UNAVAILABLE"),
)
PROFILE_COSTS = (
    (10, 20, 30, 40, 50, 60, 70, 80),
    (10, 20, 30, 40, 50, 60, 70, 80),
    (10, 20, 30, 40, 50, 60, 70, 80),
    (10, 20, 30, 40, 70, 50, 80, 90),
    (10, 20, 30, 40, 50, 60, 70, 80),
    (10, 20, 30, 40, 50, 60, 70, 80),
    (10, 20, 30, 40, 50, 60, 70, 80),
    (10, 20, 30, 40, 50, 60, 70, 80),
    (10, 20, 30, 40, 50, 60, 70, 80),
    (10, 20, 30, 40, 50, 60, 70, 80),
)


def _scope_ref(spec: _CaseSpecV01) -> str:
    return f"scope:g2c:{spec.suffix}:v01"


def _build_snapshot(
    *, spec: _CaseSpecV01, transaction_id: str,
    profile_states: tuple[str, ...] | None = None,
    profile_costs: tuple[int, ...] | None = None,
) -> router.ExecutionModeLocalRoutingSnapshotV01:
    index = CASE_SPECS.index(spec)
    states = PROFILE_STATES[index] if profile_states is None else profile_states
    costs = PROFILE_COSTS[index] if profile_costs is None else profile_costs
    policy_id = f"policy:g2c:{spec.suffix}:v01"
    capability_snapshot_id = f"capabilities:g2c:{spec.suffix}:v01"
    cost_model_id = "cost_model:g2c:deterministic:v01"
    profiles = tuple(
        router.build_execution_mode_local_mode_profile_v01(
            request_id=spec.request_id, transaction_id=transaction_id,
            owning_root_id=ROOT_BY_DOMAIN[spec.domain_id], domain_id=spec.domain_id,
            mode=mode, policy_snapshot_id=policy_id,
            capability_snapshot_id=capability_snapshot_id,
            cost_model_id=cost_model_id, policy_allowed=True,
            scope_allowed=True, risk_allowed=True, privacy_allowed=True,
            capability_state=state,
            capability_id=(
                None if state == "NOT_REQUIRED" else f"capability:g2c:{mode}:v01"
            ),
            cost_units=cost,
        )
        for mode, state, cost in zip(
            router.EXECUTABLE_EXECUTION_MODES_V01, states, costs, strict=True
        )
    )
    permitted = (
        (spec.accepted_scope_ref,)
        if spec.review_action == "NARROW" and spec.accepted_scope_ref is not None
        else ()
    )
    return router.build_execution_mode_local_routing_snapshot_v01(
        request_id=spec.request_id, transaction_id=transaction_id,
        owning_root_id=ROOT_BY_DOMAIN[spec.domain_id], domain_id=spec.domain_id,
        request_class=spec.request_class, action_class=spec.action_class,
        action_packet_relation=spec.action_relation, scope_class="BOUNDED",
        scope_ref=_scope_ref(spec), permitted_narrower_scope_refs=permitted,
        risk_class="LOW", policy_snapshot_id=policy_id,
        capability_snapshot_id=capability_snapshot_id,
        cost_model_id=cost_model_id,
        required_user_input_state=spec.required_user_input_state,
        hard_block_state=spec.hard_block_state,
        evaluation_time_epoch_seconds=EVALUATION_TIME,
        pt_created_at_utc=EVALUATION_UTC, et_observed_at_utc=EVALUATION_UTC,
        ct_session_anchor=f"ct:g2c:{spec.suffix}:v01", ttl_seconds=3600,
        freshness_class="static", valid_from_utc=EVALUATION_UTC,
        valid_to_utc=VALID_TO_UTC, mode_profiles=profiles,
    )


def _build_source_context(
    *, bsep: dict[str, dict[str, object]],
    snapshot: router.ExecutionModeLocalRoutingSnapshotV01,
    replay_family: dict[str, object] | None,
    g2a_family: SimpleNamespace | None,
    g2b_family: dict[str, object] | None,
) -> router.ExecutionModeSourceContextV01:
    replay_family = replay_family or {}
    g2b_family = g2b_family or {}
    return router.build_execution_mode_source_context_v01(
        business_request_context_packet=bsep["business"],
        bsep_packet=bsep["packet"], bsep_route_context_packet=bsep["route"],
        bsep_orchestrator_proposal=bsep["proposal"],
        bsep_structured_rationale=bsep["rationale"],
        sealed_replay_evidence=replay_family.get("replay"),
        replay_source_manifest=replay_family.get("manifest"),
        replay_source_domain_projection=replay_family.get("projection"),
        replay_source_safe_file_contents=replay_family.get("contents", ()),
        replay_anchor_publication=replay_family.get("publication"),
        replay_anchored_verification=replay_family.get("verification"),
        replay_supplied_anchor_publication_id=(
            replay_family["publication"].anchor_publication_id
            if replay_family else None
        ),
        replay_reconstructed_manifest=replay_family.get("manifest"),
        replay_reconstructed_domain_projection=replay_family.get("projection"),
        replay_reconstructed_safe_file_contents=replay_family.get("contents", ()),
        g2a_inspection=getattr(g2a_family, "inspection", None),
        g2a_registry=getattr(g2a_family, "registry", None),
        g2a_packet_id=(
            g2a_family.root_bound.packet_identity.packet_id if g2a_family else None
        ),
        g2a_corridor=getattr(g2a_family, "corridor", None),
        g2a_corridor_step=getattr(g2a_family, "corridor_step", None),
        g2a_current_dependency_observations=getattr(g2a_family, "observations", ()),
        g2a_logical_time_bridge=getattr(g2a_family, "logical_time_bridge", None),
        g2a_evaluation_time=EVALUATION_TIME,
        g2a_evaluation_time_source=snapshot.created_by,
        g2a_evaluation_context_id=snapshot.local_routing_snapshot_id,
        g2a_transition_registry_profile=(
            transition_registry.build_action_packet_transition_registry_profile_v01()
            if g2a_family else None
        ),
        g2b_resolution_report=g2b_family.get("report"),
        g2b_compatibility_projections=g2b_family.get("projections", ()),
        g2b_use_time=g2b_family.get("use_time"),
        g2b_root_kernel=g2b_family.get("root_kernel"),
        g2b_root_decision_input=g2b_family.get("root_input"),
        g2b_root_decision_result=g2b_family.get("root_result"),
        g2b_writeback_evidence=None,
    )


def _build_router_input(
    spec: _CaseSpecV01,
    *,
    profile_states: tuple[str, ...] | None = None,
    profile_costs: tuple[int, ...] | None = None,
) -> tuple[router.ExecutionModeRouterInputV01,
           router.ExecutionModeSourceContextV01,
           str | None, str | None]:
    g2b_family = (
        _build_g2b_family(spec, _scope_ref(spec))
        if spec.g2b_kind != "NOT_APPLICABLE" else None
    )
    transaction_id = (
        g2b_family["query"].query_id
        if g2b_family is not None else spec.literal_transaction_id
    )
    if type(transaction_id) is not str or transaction_id == spec.request_id:
        raise ValueError("g2c5_transaction_invalid")
    action_source = _build_g2a_pending_source(spec) if spec.g2a_present else None
    if action_source is not None:
        canonical = action_source.root_bound.canonical_projection
        if (canonical.transaction_id, canonical.owning_local_root_id) != (
            transaction_id, ROOT_BY_DOMAIN[spec.domain_id]
        ):
            raise ValueError("g2c5_g2a_binding_invalid")
    snapshot = _build_snapshot(
        spec=spec, transaction_id=transaction_id,
        profile_states=profile_states, profile_costs=profile_costs,
    )
    g2a_family = (
        _bind_g2a_inspection(action_source, snapshot)
        if action_source is not None else None
    )
    bsep = _build_bsep_family(spec)
    replay_family = _build_replay_family(spec) if spec.replay_bound else None
    context = _build_source_context(
        bsep=bsep, snapshot=snapshot, replay_family=replay_family,
        g2a_family=g2a_family, g2b_family=g2b_family,
    )
    common = {
        "request_id": spec.request_id, "transaction_id": transaction_id,
        "owning_root_id": ROOT_BY_DOMAIN[spec.domain_id], "domain_id": spec.domain_id,
    }
    bsep_binding = router.build_execution_mode_bsep_binding_v01(
        **common, source_context=context
    )
    replay_binding = (
        router.build_execution_mode_replay_binding_v01(**common, source_context=context)
        if replay_family is not None
        else router.build_execution_mode_replay_not_applicable_binding_v01(**common)
    )
    g2a_binding = (
        router.build_execution_mode_g2a_binding_v01(**common, source_context=context)
        if g2a_family is not None
        else router.build_execution_mode_g2a_no_packet_binding_v01(
            **common, evaluation_time=EVALUATION_TIME,
            evaluation_time_source=snapshot.created_by,
            evaluation_context_id=snapshot.local_routing_snapshot_id,
        )
    )
    g2b_binding = (
        router.build_execution_mode_g2b_binding_v01(**common, source_context=context)
        if g2b_family is not None
        else router.build_execution_mode_g2b_not_applicable_binding_v01(**common)
    )
    value = router.build_execution_mode_router_input_v01(
        request_id=spec.request_id, transaction_id=transaction_id,
        owning_root_id=ROOT_BY_DOMAIN[spec.domain_id], bsep_binding=bsep_binding,
        local_routing_snapshot=snapshot, replay_binding=replay_binding,
        g2a_binding=g2a_binding, g2b_binding=g2b_binding,
    )
    return (
        value, context,
        g2b_family["address"].semantic_address_id if g2b_family else None,
        g2b_family["query"].query_id if g2b_family else None,
    )


def _require_pass(report: router.ExecutionModeValidationReportV01, label: str) -> None:
    if report.validation_status != "PASS":
        raise ValueError(label)


def _collect_case_pipeline_v01(
    spec: _CaseSpecV01,
    *,
    profile_states: tuple[str, ...] | None = None,
    profile_costs: tuple[int, ...] | None = None,
) -> _CasePipelineV01:
    router_input, source_context, semantic_address_id, temporal_query_id = (
        _build_router_input(
            spec, profile_states=profile_states, profile_costs=profile_costs
        )
    )
    _require_pass(
        router.validate_execution_mode_source_context_v01(source_context),
        "g2c5_source_context_invalid",
    )
    _require_pass(
        router.validate_execution_mode_router_input_against_sources_v01(
            router_input=router_input, source_context=source_context
        ),
        "g2c5_router_input_invalid",
    )
    rows = router.evaluate_execution_mode_feasibility_v01(
        router_input=router_input, source_context=source_context
    )
    selected_row = router.select_execution_mode_v01(
        router_input=router_input, source_context=source_context,
        ordered_rows=rows,
    )
    proposal = router.build_execution_mode_proposal_v01(
        router_input=router_input, source_context=source_context,
        ordered_rows=rows, selected_row=selected_row,
    )
    _require_pass(
        router.validate_execution_mode_proposal_against_sources_v01(
            proposal=proposal, router_input=router_input,
            source_context=source_context,
        ),
        "g2c5_proposal_invalid",
    )
    proposal_artifact = router.project_execution_mode_proposal_kernel_artifact_v01(
        proposal=proposal, router_input=router_input, source_context=source_context
    )
    if abi.validate_kernel_artifact_bundle_v01(artifacts=(proposal_artifact,)):
        raise ValueError("g2c5_stage_a_invalid")
    registry = transition_registry.build_execution_mode_transition_registry_profile_v01()
    pre_transition = router.evaluate_execution_mode_proposal_to_root_transition_v01(
        registry=registry, proposal=proposal, router_input=router_input,
        source_context=source_context, proposal_artifact=proposal_artifact,
    )
    if spec.review_action == "ACCEPT":
        accepted_scope_ref = proposal.proposed_scope_ref
        narrowing_basis_refs: tuple[str, ...] = ()
    elif spec.review_action == "NARROW":
        accepted_scope_ref = spec.accepted_scope_ref
        narrowing_basis_refs = _lexical((
            router_input.bsep_binding.bsep_binding_id,
            proposal_artifact.artifact_id,
            selected_row.feasibility_row_id,
        ))
    else:
        accepted_scope_ref = None
        narrowing_basis_refs = ()
    review_input = router.build_root_execution_mode_review_input_v01(
        proposal=proposal, router_input=router_input, source_context=source_context,
        proposal_artifact=proposal_artifact,
        proposal_transition_decision=pre_transition,
        review_action=spec.review_action, accepted_scope_ref=accepted_scope_ref,
        narrowing_basis_refs=narrowing_basis_refs,
    )
    _require_pass(
        router.validate_root_execution_mode_review_input_against_sources_v01(
            review_input=review_input, proposal=proposal, router_input=router_input,
            source_context=source_context, proposal_artifact=proposal_artifact,
            proposal_transition_decision=pre_transition,
        ),
        "g2c5_review_input_invalid",
    )
    decision, root_kernel, root_input, root_result, review_report = (
        router.review_execution_mode_proposal_v01(
            review_input=review_input, proposal=proposal, router_input=router_input,
            source_context=source_context, proposal_artifact=proposal_artifact,
            proposal_transition_decision=pre_transition,
        )
    )
    _require_pass(review_report, "g2c5_root_review_invalid")
    if any(item is None for item in (decision, root_kernel, root_input, root_result)):
        raise ValueError("g2c5_root_source_incomplete")
    assert decision is not None and root_kernel is not None
    assert root_input is not None and root_result is not None
    _require_pass(
        router.validate_root_execution_mode_decision_against_source_v01(
            decision=decision, review_input=review_input, proposal=proposal,
            router_input=router_input, source_context=source_context,
            proposal_artifact=proposal_artifact,
            proposal_transition_decision=pre_transition, root_kernel=root_kernel,
            root_decision_input=root_input, root_decision_result=root_result,
        ),
        "g2c5_root_decision_invalid",
    )
    decision_artifact = router.project_root_execution_mode_decision_kernel_artifact_v01(
        decision=decision, review_input=review_input, proposal=proposal,
        router_input=router_input, source_context=source_context,
        proposal_artifact=proposal_artifact,
        proposal_transition_decision=pre_transition, root_kernel=root_kernel,
        root_decision_input=root_input, root_decision_result=root_result,
    )
    if abi.validate_kernel_artifact_bundle_v01(
        artifacts=(proposal_artifact, decision_artifact)
    ):
        raise ValueError("g2c5_stage_b_invalid")
    post_transition = router.evaluate_execution_mode_root_route_transition_v01(
        registry=registry, proposal_transition_decision=pre_transition,
        review_input=review_input, decision=decision, proposal=proposal,
        router_input=router_input, source_context=source_context,
        root_kernel=root_kernel, root_decision_input=root_input,
        root_decision_result=root_result, proposal_artifact=proposal_artifact,
        decision_artifact=decision_artifact,
    )
    route_eligibility = (
        router.project_execution_mode_route_eligibility_kernel_artifact_v01(
            decision=decision, review_input=review_input, proposal=proposal,
            router_input=router_input, source_context=source_context,
            proposal_artifact=proposal_artifact,
            proposal_transition_decision=pre_transition, root_kernel=root_kernel,
            root_decision_input=root_input, root_decision_result=root_result,
            decision_artifact=decision_artifact,
            root_route_transition_decision=post_transition,
        )
    )
    bundle = (
        (proposal_artifact, decision_artifact, route_eligibility)
        if route_eligibility is not None
        else (proposal_artifact, decision_artifact)
    )
    if abi.validate_kernel_artifact_bundle_v01(artifacts=bundle):
        raise ValueError("g2c5_stage_c_invalid")
    _require_pass(
        router.validate_execution_mode_abi_profile_v01(
            proposal=proposal, router_input=router_input,
            source_context=source_context, proposal_artifact=proposal_artifact,
            proposal_transition_decision=pre_transition, review_input=review_input,
            decision=decision, root_kernel=root_kernel,
            root_decision_input=root_input, root_decision_result=root_result,
            decision_artifact=decision_artifact,
            root_route_transition_decision=post_transition,
            route_eligibility_artifact=route_eligibility,
        ),
        "g2c5_abi_profile_invalid",
    )
    return _CasePipelineV01(
        spec=spec, source_context=source_context, router_input=router_input,
        rows=rows, selected_row=selected_row, proposal=proposal,
        proposal_artifact=proposal_artifact, registry=registry,
        pre_transition=pre_transition, review_input=review_input,
        root_kernel=root_kernel, root_input=root_input, root_result=root_result,
        decision=decision, decision_artifact=decision_artifact,
        post_transition=post_transition, route_eligibility=route_eligibility,
        semantic_address_id=semantic_address_id, temporal_query_id=temporal_query_id,
    )


OPERATION_STEPS = (
    "01_SOURCE_CONTEXT_STRUCTURAL_VALIDATION",
    "02_ROUTER_INPUT_CONTEXTUAL_VALIDATION",
    "03_TEN_ROW_FEASIBILITY_EVALUATION",
    "04_EXACT_ROW_SELECTION",
    "05_PROPOSAL_BUILD_AND_CONTEXTUAL_VALIDATION",
    "06_PROPOSAL_KERNEL_ARTIFACT_PROJECTION",
    "07_STAGE_A_BUNDLE_VALIDATION",
    "08_PROPOSAL_TO_ROOT_TRANSITION",
    "09_ROOT_REVIEW_INPUT_BUILD_AND_VALIDATION",
    "10_ACTUAL_ROOT_SOURCE_FAMILY_BUILD_AND_VALIDATION",
    "11_G2C_ROOT_DECISION_PROJECTION_AND_VALIDATION",
    "12_DECISION_KERNEL_ARTIFACT_PROJECTION",
    "13_STAGE_B_BUNDLE_VALIDATION",
    "14_POST_ROOT_TRANSITION",
    "15_ROUTE_ELIGIBILITY_PROJECTION_WHEN_APPLICABLE",
    "16_STAGE_C_BUNDLE_VALIDATION",
    "17_COMPLETE_ABI_PROFILE_VALIDATION",
)


def _case_result(pipeline: _CasePipelineV01) -> ExecutionModeRouterG2CCaseResultV01:
    spec = pipeline.spec
    synthesis = pipeline.root_input.root_review_packet.synthesis_proposal
    evidence_ids = synthesis.normalized_claims[0].evidence_refs
    root_input_plain = root_decision.root_decision_input_to_plain_dict_v01(
        pipeline.root_input
    )
    post_vv_id = root_input_plain["post_vv_bundle"]["bundle_id"]
    gt_id = root_input_plain["gt_advisory"]["advisory_id"]
    root_support_ids = (
        *evidence_ids,
        pipeline.root_input.root_review_packet.contribution_ids[0],
        post_vv_id,
        gt_id,
        pipeline.review_input.root_local_context_id,
    )
    trace_tuples = (
        pipeline.router_input.trace_refs,
        pipeline.proposal_artifact.trace_refs,
        pipeline.review_input.trace_refs,
        pipeline.decision_artifact.trace_refs,
        (() if pipeline.route_eligibility is None
         else pipeline.route_eligibility.trace_refs),
    )
    zero = {name: 0 for name in ZERO_OPERATION_NAMES}
    return ExecutionModeRouterG2CCaseResultV01(
        case_id=spec.case_id, fixture_id=FIXTURE_BY_DOMAIN[spec.domain_id],
        request_id=spec.request_id, transaction_id=pipeline.router_input.transaction_id,
        owning_root_id=ROOT_BY_DOMAIN[spec.domain_id], domain_id=spec.domain_id,
        semantic_address_id=pipeline.semantic_address_id,
        temporal_query_id=pipeline.temporal_query_id,
        source_family_sha256=pipeline.router_input.bsep_binding.source_family_sha256,
        router_input_id=pipeline.router_input.router_input_id,
        selected_mode=pipeline.selected_row.mode,
        selected_feasibility_row_id=pipeline.selected_row.feasibility_row_id,
        rebuilt_selected_feasibility_row_id=(
            router.rebuild_execution_mode_feasibility_row_identity_v01(
                pipeline.selected_row
            )
        ),
        selected_row_reason=pipeline.selected_row.reason_codes[0],
        proposal_id=pipeline.proposal.proposal_id,
        proposal_reason_codes=pipeline.proposal.reason_codes,
        review_action=pipeline.review_input.review_action,
        root_review_input_id=pipeline.review_input.root_review_input_id,
        root_support_ids=root_support_ids,
        source_root_input_id=pipeline.root_input.decision_input_id,
        source_root_result_id=pipeline.root_result.decision_id,
        source_root_reason=pipeline.root_result.reason_code,
        root_decision_id=pipeline.decision.decision_id,
        root_outcome=pipeline.decision.outcome,
        root_projection_reason_codes=pipeline.decision.reason_codes,
        pre_root_transition_id=pipeline.pre_transition.decision_id,
        pre_root_transition_reason=pipeline.pre_transition.reason_code,
        post_root_transition_id=pipeline.post_transition.decision_id,
        post_root_transition_reason=pipeline.post_transition.reason_code,
        proposal_artifact_id=pipeline.proposal_artifact.artifact_id,
        decision_artifact_id=pipeline.decision_artifact.artifact_id,
        route_eligibility_artifact_id=(
            pipeline.route_eligibility.artifact_id
            if pipeline.route_eligibility is not None else None
        ),
        downstream_consumption_class=pipeline.decision.downstream_consumption_class,
        downstream_action_packet_required=(
            pipeline.decision.downstream_action_packet_required
        ),
        root_review_conflict_set_ids=(
            pipeline.root_input.root_review_packet.conflict_set_ids
        ),
        root_input_conflict_set_ids=tuple(
            root_input_plain["conflict_state"]["conflict_set_ids"]
        ),
        root_result_conflict_set_ids=pipeline.root_result.conflict_set_ids,
        trace_tuples=trace_tuples, operation_steps=OPERATION_STEPS,
        final_status="PASS", reason_codes=(), **zero,
    )


def _report_identity(value: ExecutionModeRouterG2CReportV01) -> str:
    material = execution_mode_router_g2_c_report_to_plain_data_v01(value)
    material.pop("report_id")
    return REPORT_ID_PREFIX + domain_separated_sha256_hex_v01(
        domain=REPORT_ID_DOMAIN, payload=canonical_json_bytes_v01(material)
    )


def collect_execution_mode_router_g2_c_v01() -> ExecutionModeRouterG2CReportV01:
    case_results = tuple(
        _case_result(_collect_case_pipeline_v01(spec)) for spec in CASE_SPECS
    )
    zero = {name: 0 for name in ZERO_OPERATION_NAMES}
    provisional = ExecutionModeRouterG2CReportV01(
        report_version=EXECUTION_MODE_ROUTER_G2_C_PROOF_VERSION,
        report_id=REPORT_ID_PREFIX + "0" * 64,
        profile_id=EXECUTION_MODE_ROUTER_G2_C_PROFILE_ID,
        domain_order=DOMAIN_ORDER,
        case_order=tuple(spec.case_id for spec in CASE_SPECS),
        case_results=case_results, final_status="PASS", reason_codes=(), **zero,
    )
    report = replace(provisional, report_id=_report_identity(provisional))
    if validate_execution_mode_router_g2_c_report_v01(report) != ():
        raise ValueError("g2c5_report_invalid")
    return report


def validate_execution_mode_router_g2_c_report_v01(
    report: object,
) -> tuple[str, ...]:
    try:
        if type(report) is not ExecutionModeRouterG2CReportV01:
            return ("g2c5_report_invalid",)
        reasons: list[str] = []
        if report.report_version != EXECUTION_MODE_ROUTER_G2_C_PROOF_VERSION:
            reasons.append("g2c5_report_version_invalid")
        if report.profile_id != EXECUTION_MODE_ROUTER_G2_C_PROFILE_ID:
            reasons.append("g2c5_report_profile_invalid")
        if report.domain_order != DOMAIN_ORDER:
            reasons.append("g2c5_domain_order_invalid")
        if report.case_order != tuple(spec.case_id for spec in CASE_SPECS):
            reasons.append("g2c5_case_order_invalid")
        if (
            type(report.case_results) is not tuple
            or len(report.case_results) != CANONICAL_SCENARIO_COUNT
            or any(type(item) is not ExecutionModeRouterG2CCaseResultV01
                   for item in report.case_results)
        ):
            reasons.append("g2c5_case_geometry_invalid")
        else:
            for spec, result in zip(CASE_SPECS, report.case_results, strict=True):
                expected_transaction = (
                    result.temporal_query_id
                    if spec.g2b_kind != "NOT_APPLICABLE"
                    else spec.literal_transaction_id
                )
                if (
                    result.case_id != spec.case_id
                    or result.fixture_id != FIXTURE_BY_DOMAIN[spec.domain_id]
                    or result.request_id != spec.request_id
                    or result.transaction_id != expected_transaction
                    or result.request_id == result.transaction_id
                    or result.owning_root_id != ROOT_BY_DOMAIN[spec.domain_id]
                    or result.domain_id != spec.domain_id
                    or result.selected_mode != spec.selected_mode
                    or result.selected_row_reason != spec.selected_reason
                    or result.selected_feasibility_row_id
                    != result.rebuilt_selected_feasibility_row_id
                    or result.proposal_reason_codes != ("g2c_proposal_sources_valid",)
                    or result.review_action != spec.review_action
                    or result.source_root_reason != spec.root_source_reason
                    or result.root_outcome != spec.root_outcome
                    or result.root_projection_reason_codes != (spec.projection_reason,)
                    or result.pre_root_transition_reason
                    != "g2c_transition_root_review_required"
                    or result.post_root_transition_reason != spec.post_transition_reason
                    or result.downstream_consumption_class
                    != spec.downstream_consumption_class
                    or result.downstream_action_packet_required is not spec.packet_required
                    or (result.route_eligibility_artifact_id is not None)
                    is not spec.route_eligibility_present
                    or result.root_review_conflict_set_ids != ()
                    or result.root_input_conflict_set_ids != ()
                    or result.root_result_conflict_set_ids != ()
                    or len(result.root_support_ids) != 6
                    or len(result.root_support_ids) != len(set(result.root_support_ids))
                    or result.operation_steps != OPERATION_STEPS
                    or result.final_status != "PASS"
                    or result.reason_codes != ()
                    or any(getattr(result, name) != 0 for name in ZERO_OPERATION_NAMES)
                ):
                    reasons.append("g2c5_case_result_invalid")
        if any(getattr(report, name) != 0 for name in ZERO_OPERATION_NAMES):
            reasons.append("g2c5_zero_operation_invalid")
        if report.final_status != "PASS" or report.reason_codes != ():
            reasons.append("g2c5_report_status_invalid")
        if report.report_id != _report_identity(report):
            reasons.append("g2c5_report_identity_invalid")
        return tuple(dict.fromkeys(reasons))
    except Exception:
        return ("g2c5_report_invalid",)


def execution_mode_router_g2_c_report_to_plain_data_v01(
    report: ExecutionModeRouterG2CReportV01,
) -> dict[str, object]:
    if type(report) is not ExecutionModeRouterG2CReportV01:
        raise ValueError("g2c5_report_invalid")
    return {item.name: _plain(getattr(report, item.name)) for item in fields(report)}


def render_execution_mode_router_g2_c_v01(
    report: ExecutionModeRouterG2CReportV01,
) -> str:
    if validate_execution_mode_router_g2_c_report_v01(report):
        raise ValueError("g2c5_report_invalid")
    return json.dumps(
        execution_mode_router_g2_c_report_to_plain_data_v01(report),
        ensure_ascii=True, separators=(",", ":"), allow_nan=False,
    ) + "\n"


def main() -> int:
    report = collect_execution_mode_router_g2_c_v01()
    rendered = render_execution_mode_router_g2_c_v01(report)
    print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
