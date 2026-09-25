"""Pure domain-neutral trust and compromise metadata for G1-B1.

The model is deterministic, in-memory descriptive metadata consumed by
conformance validation. It is not a transition registry, permission system,
Root Decision Kernel, or Effect Firewall. It performs no provider, network,
file, domain, authority-creation, or effect operation. Its authority labels
describe G1-B1 trust boundaries; they are not the future G1-B2 Kernel ABI
authority enum.
"""

from __future__ import annotations

from dataclasses import dataclass as _dataclass
from types import MappingProxyType as _MappingProxyType

from hedgehog.kernel.integrity_replay_v01 import (
    canonical_json_bytes_v01 as _canonical_json_bytes_v01,
)


MODULE_ID = "kernel_trust_model_v01"
SLICE_ID = "domain_neutral_reference_kernel_gate1_g1b1"
TRUST_MODEL_VERSION = "v0.1"
STATUS_PASS = "PASS"
STATUS_BLOCKED_FAIL_CLOSED = "BLOCKED_FAIL_CLOSED"


@_dataclass(frozen=True)
class ComponentTrustProfileV01:
    component_id: str
    component_class: str
    authority_class: str
    trusted_inputs: tuple[str, ...]
    untrusted_inputs: tuple[str, ...]
    produced_artifact_classes: tuple[str, ...]
    may_create_root_decision: bool
    may_create_permission: bool
    may_request_effect: bool
    may_hold_effect_handle: bool
    compromise_assumptions: tuple[str, ...]
    fail_closed_expectation: str


_PROFILE_ROWS = (
    (
        "root",
        "ROOT",
        "ROOT_FINAL_AUTHORITY",
        ("validated_review_state", "policy_state", "permission_state"),
        ("provider_advice", "drs_information", "gt_advice"),
        ("RootDecision", "RootOwnedIntent", "ExecutionRequest"),
        True,
        True,
        True,
        False,
        ("review_input_may_be_invalid_or_incomplete",),
        "invalid_or_incomplete_review_input_blocks_root_transition",
    ),
    (
        "provider_llm",
        "PROVIDER_LLM",
        "NON_ROOT_ADVISORY",
        ("bounded_context",),
        ("provider_generated_text", "provider_generated_json"),
        ("ActorContribution",),
        False,
        False,
        False,
        False,
        ("provider_may_hallucinate_or_be_malicious",),
        "authority_permission_topology_or_effect_claim_fails_closed",
    ),
    (
        "orchestrator",
        "ORCHESTRATOR",
        "NON_ROOT_ADVISORY",
        ("root_shaped_task", "bounded_context"),
        ("self_proposed_route",),
        ("BoundedRouteProposal",),
        False,
        False,
        False,
        False,
        ("route_scope_may_be_invalid_or_expanded",),
        "invalid_scope_returns_to_root_or_fails_closed",
    ),
    (
        "semantic_architect",
        "SEMANTIC_ARCHITECT",
        "NON_ROOT_ADVISORY",
        ("root_accepted_route", "bounded_context"),
        ("provider_owned_topology",),
        ("SemanticArchitectureProposal",),
        False,
        False,
        False,
        False,
        ("semantic_architecture_may_claim_runtime_topology",),
        "authoritative_provider_topology_is_rejected",
    ),
    (
        "deterministic_runtime",
        "DETERMINISTIC_RUNTIME",
        "NON_ROOT_DETERMINISTIC",
        ("validated_contracts", "runtime_owned_topology"),
        ("unvalidated_actor_contributions",),
        ("ValidatedEvidence", "RuntimeExecutionTopology"),
        False,
        False,
        False,
        False,
        ("contract_shape_may_be_unknown_or_malformed",),
        "unknown_contract_shape_fails_closed",
    ),
    (
        "drs",
        "DRS",
        "NON_ROOT_INFORMATIONAL",
        ("validated_memory_records",),
        ("stale_poisoned_incomplete_or_conflicting_memory",),
        ("InformationalReuse", "EvidenceReference"),
        False,
        False,
        False,
        False,
        ("memory_may_be_stale_poisoned_incomplete_or_conflicting",),
        "memory_never_creates_permission_or_root_decision",
    ),
    (
        "avf",
        "AVF",
        "NON_ROOT_ADVISORY",
        ("validated_candidates", "hard_predicates"),
        ("manipulated_scores",),
        ("AdvisoryRanking", "PressureSignal"),
        False,
        False,
        False,
        False,
        ("scores_may_be_manipulated_or_miscalibrated",),
        "scores_cannot_override_hard_predicates",
    ),
    (
        "executor_fractal_child",
        "EXECUTOR_FRACTAL_CHILD",
        "NON_ROOT_BOUNDED_EXECUTOR",
        ("bounded_parent_scope", "runtime_owned_topology"),
        ("child_generated_output",),
        ("ActorContribution", "ResultProposal"),
        False,
        False,
        False,
        False,
        ("child_may_expand_scope_or_emit_malformed_output",),
        "scope_expansion_or_malformed_output_fails_closed",
    ),
    (
        "post_vv",
        "POST_VV",
        "NON_ROOT_VALIDATION",
        ("result_proposals", "validation_contracts"),
        ("unvalidated_result_payload",),
        ("PostVVReport",),
        False,
        False,
        False,
        False,
        ("validation_may_fail_or_be_unknown",),
        "failed_or_unknown_validation_blocks_root_acceptance",
    ),
    (
        "gt",
        "GT",
        "NON_ROOT_ADVISORY",
        ("validated_candidate_reports",),
        ("terminal_advisory_ranking",),
        ("GTAdvisoryReport",),
        False,
        False,
        False,
        False,
        ("terminal_ranking_may_be_wrong_or_compromised",),
        "terminal_advice_never_commits_root_decision",
    ),
    (
        "domain_adapter",
        "DOMAIN_ADAPTER",
        "NON_ROOT_ADAPTER",
        ("kernel_contracts", "validated_domain_payload"),
        ("domain_payload",),
        ("DomainPayloadProjection",),
        False,
        False,
        False,
        False,
        ("adapter_may_attempt_authority_or_effect_bypass",),
        "authority_transition_registration_or_direct_effect_access_fails_closed",
    ),
    (
        "effect_firewall",
        "EFFECT_FIREWALL",
        "NON_ROOT_EFFECT_ENFORCEMENT",
        ("root_created_execution_request", "bounded_effect_policy"),
        ("unknown_or_expanded_effect_request",),
        ("EffectFirewallDecision",),
        False,
        False,
        False,
        True,
        ("effect_request_may_be_forged_expired_or_expanded",),
        "unknown_or_expanded_effect_request_fails_closed",
    ),
    (
        "corridor_adapter",
        "CORRIDOR_ADAPTER",
        "NON_ROOT_BOUNDED_CORRIDOR",
        ("firewall_approved_scope", "bounded_adapter_binding"),
        ("adapter_output",),
        ("BoundedCorridorEvidence",),
        False,
        False,
        False,
        True,
        ("adapter_may_mismatch_expire_duplicate_or_expand_scope",),
        "adapter_mismatch_expiry_duplication_or_scope_expansion_fails_closed",
    ),
    (
        "receipt",
        "RECEIPT",
        "NON_ROOT_EVIDENCE",
        ("validated_effect_observation",),
        ("forged_or_replayed_receipt",),
        ("EvidenceReceipt",),
        False,
        False,
        False,
        False,
        ("receipt_may_be_forged_replayed_or_misrepresented",),
        "receipt_cannot_become_permission",
    ),
    (
        "ledger",
        "LEDGER",
        "NON_ROOT_TRACE",
        ("validated_artifact_refs", "dependency_edges"),
        ("malformed_or_discontinuous_trace",),
        ("CausalTrace",),
        False,
        False,
        False,
        False,
        ("trace_may_be_discontinuous_or_malformed",),
        "trace_discontinuity_or_malformed_trace_fails_closed",
    ),
    (
        "crypto",
        "CRYPTO",
        "NON_ROOT_INTEGRITY",
        ("declared_artifact_bytes", "known_seal_profile"),
        ("semantic_truth_claim", "unknown_profile"),
        ("IntegrityVerification",),
        False,
        False,
        False,
        False,
        ("integrity_input_or_profile_may_be_malformed",),
        "unknown_profile_or_malformed_integrity_input_fails_closed",
    ),
    (
        "replay",
        "REPLAY",
        "NON_ROOT_RECONSTRUCTION",
        ("verified_manifest", "accepted_evidence"),
        ("rerun_or_authority_creation_attempt",),
        ("ReplayVerification",),
        False,
        False,
        False,
        False,
        ("replay_may_attempt_rerun_or_authority_creation",),
        "rerun_or_authority_creation_attempt_fails_closed",
    ),
    (
        "renderer_showcase",
        "RENDERER_SHOWCASE",
        "NON_ROOT_PRESENTATION",
        ("validated_public_projections",),
        ("presentation_claims",),
        ("EvidencePresentation",),
        False,
        False,
        False,
        False,
        ("renderer_may_mutate_state_or_upgrade_evidence_claims",),
        "kernel_mutation_or_evidence_claim_upgrade_fails_closed",
    ),
)

_EXPECTED_IDS = tuple(row[0] for row in _PROFILE_ROWS)
_EXPECTED_BY_ID = _MappingProxyType({row[0]: row for row in _PROFILE_ROWS})


def build_default_component_trust_profiles_v01(
) -> tuple[ComponentTrustProfileV01, ...]:
    return tuple(ComponentTrustProfileV01(*row) for row in _PROFILE_ROWS)


def validate_component_trust_profiles_v01(
    *,
    profiles: object,
) -> tuple[str, ...]:
    try:
        return _validate_profiles(profiles)
    except Exception:
        return ("trust_profile_contract_invalid",)


def component_trust_profile_to_plain_dict_v01(
    profile: ComponentTrustProfileV01,
) -> dict[str, object]:
    try:
        if _profile_errors(profile):
            raise ValueError("trust_profile_contract_invalid")
        expected = _EXPECTED_BY_ID.get(profile.component_id)
        if expected is None or profile != ComponentTrustProfileV01(*expected):
            raise ValueError("trust_profile_contract_invalid")
        projected = _profile_plain(profile)
        _canonical_json_bytes_v01(projected)
        return projected
    except Exception:
        raise ValueError("trust_profile_contract_invalid") from None


def component_trust_profiles_to_plain_list_v01(
    profiles: tuple[ComponentTrustProfileV01, ...],
) -> list[dict[str, object]]:
    try:
        if validate_component_trust_profiles_v01(profiles=profiles):
            raise ValueError("trust_profile_tuple_invalid")
        projected = [_profile_plain(profile) for profile in profiles]
        _canonical_json_bytes_v01(projected)
        return projected
    except Exception:
        raise ValueError("trust_profile_tuple_invalid") from None


def _valid_text(value: object) -> bool:
    return bool(
        type(value) is str
        and value
        and not any(0xD800 <= ord(character) <= 0xDFFF for character in value)
    )


def _valid_text_tuple(value: object) -> bool:
    return bool(
        type(value) is tuple
        and value
        and all(_valid_text(item) for item in value)
        and len(value) == len(set(value))
    )


def _profile_errors(profile: object) -> tuple[str, ...]:
    if type(profile) is not ComponentTrustProfileV01:
        return ("trust_profile_contract_invalid",)
    errors: list[str] = []
    if not all(
        _valid_text(value)
        for value in (
            profile.component_id,
            profile.component_class,
            profile.authority_class,
        )
    ):
        errors.append("trust_profile_contract_invalid")
    if not _valid_text_tuple(profile.trusted_inputs) or not _valid_text_tuple(
        profile.untrusted_inputs
    ):
        errors.append("trust_profile_input_surface_invalid")
    if not _valid_text_tuple(profile.produced_artifact_classes):
        errors.append("trust_profile_output_surface_invalid")
    if not _valid_text_tuple(profile.compromise_assumptions):
        errors.append("trust_profile_compromise_assumption_missing")
    if not _valid_text(profile.fail_closed_expectation):
        errors.append("trust_profile_fail_closed_expectation_missing")
    flags = (
        profile.may_create_root_decision,
        profile.may_create_permission,
        profile.may_request_effect,
        profile.may_hold_effect_handle,
    )
    if any(type(flag) is not bool for flag in flags):
        errors.append("trust_profile_contract_invalid")
    return tuple(dict.fromkeys(errors))


def _validate_profiles(profiles: object) -> tuple[str, ...]:
    if type(profiles) is not tuple or not profiles:
        return ("trust_profile_tuple_invalid",)
    errors: list[str] = []
    for profile in profiles:
        errors.extend(_profile_errors(profile))
    if any(type(profile) is not ComponentTrustProfileV01 for profile in profiles):
        return tuple(dict.fromkeys(errors))
    ids = tuple(profile.component_id for profile in profiles)
    if len(ids) != len(set(ids)):
        errors.append("trust_profile_id_duplicate")
    if set(ids) != set(_EXPECTED_IDS):
        errors.append("trust_profile_set_mismatch")
    elif ids != _EXPECTED_IDS:
        errors.append("trust_profile_order_mismatch")
    for profile in profiles:
        expected = _EXPECTED_BY_ID.get(profile.component_id)
        if expected is None:
            continue
        if profile.component_class != expected[1]:
            errors.append("trust_profile_component_class_invalid")
        if profile.authority_class != expected[2]:
            errors.append("trust_profile_authority_class_invalid")
    if not errors:
        root_decision_ids = tuple(
            profile.component_id
            for profile in profiles
            if profile.may_create_root_decision
        )
        permission_ids = tuple(
            profile.component_id for profile in profiles if profile.may_create_permission
        )
        effect_request_ids = tuple(
            profile.component_id for profile in profiles if profile.may_request_effect
        )
        handle_ids = tuple(
            profile.component_id for profile in profiles if profile.may_hold_effect_handle
        )
        if root_decision_ids != ("root",):
            errors.append("root_decision_authority_invalid")
        if permission_ids != ("root",):
            errors.append("permission_authority_invalid")
        if effect_request_ids != ("root",):
            errors.append("effect_request_authority_invalid")
        if handle_ids != ("effect_firewall", "corridor_adapter"):
            errors.append("effect_handle_boundary_invalid")
    if not errors:
        expected_profiles = build_default_component_trust_profiles_v01()
        for profile, expected in zip(profiles, expected_profiles):
            if profile != expected:
                errors.append("trust_profile_contract_invalid")
                break
    return tuple(dict.fromkeys(errors))


def _profile_plain(profile: ComponentTrustProfileV01) -> dict[str, object]:
    return {
        "component_id": profile.component_id,
        "component_class": profile.component_class,
        "authority_class": profile.authority_class,
        "trusted_inputs": list(profile.trusted_inputs),
        "untrusted_inputs": list(profile.untrusted_inputs),
        "produced_artifact_classes": list(profile.produced_artifact_classes),
        "may_create_root_decision": profile.may_create_root_decision,
        "may_create_permission": profile.may_create_permission,
        "may_request_effect": profile.may_request_effect,
        "may_hold_effect_handle": profile.may_hold_effect_handle,
        "compromise_assumptions": list(profile.compromise_assumptions),
        "fail_closed_expectation": profile.fail_closed_expectation,
    }
