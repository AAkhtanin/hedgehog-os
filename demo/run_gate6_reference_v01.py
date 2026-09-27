"""Explicit finite reference composition, not source admission or Gate closure.

Default preflight is static and starts no collector, container or provider.
Native execution requires named profiles and explicit external output/inputs.
"""
from __future__ import annotations

import argparse
import ast
import dataclasses
from contextlib import contextmanager
import hashlib
import importlib
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time

BASE = "b6d11f5fcb619a10e877bbaaf6770881be315f16"
DIRECT_NODE_IDS = (
    "tests/test_transition_registry_v01.py::test_unknown_exact_lookup_blocks[source_artifact_type-UnknownArtifact]",
    "tests/test_transition_registry_v01.py::test_unknown_exact_lookup_blocks[source_lifecycle_state-UNKNOWN_STATE]",
    "tests/test_transition_registry_v01.py::test_unknown_exact_lookup_blocks[actor_role-unknown_actor]",
    "tests/test_transition_registry_v01.py::test_unknown_exact_lookup_blocks[attempted_effect-UNKNOWN_EFFECT]",
    "tests/test_transition_registry_v01.py::test_unknown_exact_lookup_blocks[target_artifact_type-UnknownTarget]",
    "tests/test_transition_registry_v01.py::test_authority_attack_rules_fail_closed[provider_contribution_to_root_decision_forbidden]",
    "tests/test_transition_registry_v01.py::test_authority_attack_rules_fail_closed[drs_evidence_to_permission_forbidden]",
    "tests/test_transition_registry_v01.py::test_authority_attack_rules_fail_closed[gt_advisory_to_root_final_forbidden]",
    "tests/test_transition_registry_v01.py::test_authority_attack_rules_fail_closed[receipt_to_permission_forbidden]",
    "tests/test_transition_registry_v01.py::test_authority_attack_rules_fail_closed[causal_evidence_to_root_decision_forbidden]",
    "tests/test_transition_registry_v01.py::test_authority_attack_rules_fail_closed[domain_adapter_effect_request_forbidden]",
    "tests/test_transition_registry_v01.py::test_missing_root_commit_returns_to_root",
    "tests/test_effect_firewall_v01.py::test_every_authorization_reason_exact[forged_request]",
    "tests/test_effect_firewall_v01.py::test_every_authorization_reason_exact[request_root_binding_mismatch]",
    "tests/test_effect_firewall_v01.py::test_every_authorization_reason_exact[permission_binding_mismatch]",
    "tests/test_effect_firewall_v01.py::test_every_authorization_reason_exact[real_effect_forbidden]",
    "tests/test_effect_firewall_v01.py::test_every_authorization_reason_exact[adapter_not_allowed]",
    "tests/test_effect_firewall_v01.py::test_every_authorization_reason_exact[action_not_allowed]",
    "tests/test_effect_firewall_v01.py::test_every_authorization_reason_exact[scope_expansion_forbidden]",
    "tests/test_effect_firewall_v01.py::test_every_authorization_reason_exact[ttl_expansion_forbidden]",
    "tests/test_effect_firewall_v01.py::test_every_authorization_reason_exact[request_not_yet_valid]",
    "tests/test_effect_firewall_v01.py::test_every_authorization_reason_exact[request_expired]",
    "tests/test_effect_firewall_v01.py::test_every_authorization_reason_exact[duplicate_request]",
    "tests/test_effect_firewall_v01.py::test_every_authorization_reason_exact[duplicate_idempotency_key]",
    "tests/test_effect_firewall_v01.py::test_authorization_precedence[changes0-200-request_root_binding_mismatch]",
    "tests/test_effect_firewall_v01.py::test_authorization_precedence[changes1-200-permission_binding_mismatch]",
    "tests/test_effect_firewall_v01.py::test_authorization_precedence[changes2-200-real_effect_forbidden]",
    "tests/test_effect_firewall_v01.py::test_authorization_precedence[changes3-200-adapter_not_allowed]",
    "tests/test_effect_firewall_v01.py::test_authorization_precedence[changes4-200-action_not_allowed]",
    "tests/test_effect_firewall_v01.py::test_authorization_precedence[changes5-200-scope_expansion_forbidden]",
    "tests/test_effect_firewall_v01.py::test_authorization_precedence[changes6-99-ttl_expansion_forbidden]",
    "tests/test_effect_firewall_v01.py::test_authorization_precedence[changes7-99-request_not_yet_valid]",
    "tests/test_effect_firewall_v01.py::test_authorization_precedence[changes8-150-request_expired]",
    "tests/test_effect_firewall_v01.py::test_capability_cross_firewall_and_forgery_rejected",
    "tests/test_effect_firewall_v01.py::test_execution_rejection_is_atomic[changes0-effect_execution_invalid]",
    "tests/test_effect_firewall_v01.py::test_execution_rejection_is_atomic[changes1-effect_execution_invalid]",
    "tests/test_effect_firewall_v01.py::test_execution_rejection_is_atomic[changes2-effect_request_not_yet_valid]",
    "tests/test_effect_firewall_v01.py::test_execution_rejection_is_atomic[changes3-effect_request_expired]",
    "tests/test_effect_firewall_v01.py::test_execution_rejection_is_atomic[changes4-effect_capability_adapter_mismatch]",
    "tests/test_effect_firewall_v01.py::test_execution_rejection_is_atomic[changes5-effect_capability_adapter_mismatch]",
    "tests/test_effect_firewall_v01.py::test_execution_rejection_is_atomic[changes6-effect_capability_action_mismatch]",
    "tests/test_effect_firewall_v01.py::test_execution_rejection_is_atomic[changes7-effect_capability_action_mismatch]",
    "tests/test_effect_firewall_v01.py::test_execution_rejection_is_atomic[changes8-effect_scope_expansion_forbidden]",
    "tests/test_effect_firewall_v01.py::test_execution_rejection_is_atomic[changes9-effect_scope_expansion_forbidden]",
    "tests/test_effect_firewall_v01.py::test_execution_rejection_is_atomic[changes10-effect_scope_expansion_forbidden]",
    "tests/test_effect_firewall_v01.py::test_execution_rejection_is_atomic[changes11-effect_scope_expansion_forbidden]",
    "tests/test_effect_firewall_v01.py::test_execution_rejection_is_atomic[changes12-effect_ttl_expansion_forbidden]",
    "tests/test_effect_firewall_v01.py::test_execution_rejection_is_atomic[changes13-effect_ttl_expansion_forbidden]",
    "tests/test_effect_firewall_v01.py::test_execution_rejection_is_atomic[changes14-effect_ttl_expansion_forbidden]",
    "tests/test_effect_firewall_v01.py::test_execution_rejection_is_atomic[changes15-effect_receipt_invalid]",
    "tests/test_effect_firewall_v01.py::test_execution_rejection_is_atomic[changes16-effect_receipt_invalid]",
    "tests/test_effect_firewall_v01.py::test_execution_rejection_is_atomic[changes17-effect_receipt_invalid]",
    "tests/test_effect_firewall_v01.py::test_execution_positive_receipt_and_state_geometry",
    "tests/test_effect_firewall_v01.py::test_duplicate_authorization_execution_and_receipt_are_strict",
    "tests/test_root_decision_kernel_v01.py::test_permission_scope_and_temporal_hard_failures",
    "tests/test_root_decision_kernel_v01.py::test_caller_state_mutation_isolated",
    "tests/test_root_decision_kernel_v01.py::test_scores_do_not_override_scope_failure[0]",
    "tests/test_root_decision_kernel_v01.py::test_scores_do_not_override_scope_failure[1]",
    "tests/test_root_decision_kernel_v01.py::test_scores_do_not_override_scope_failure[250000]",
    "tests/test_root_decision_kernel_v01.py::test_scores_do_not_override_scope_failure[500000]",
    "tests/test_root_decision_kernel_v01.py::test_scores_do_not_override_scope_failure[999999]",
    "tests/test_root_decision_kernel_v01.py::test_scores_do_not_override_scope_failure[1000000]",
    "tests/test_root_decision_kernel_v01.py::test_gt_authority_flags_remain_gt_advisory_invalid[advisory_only-False]",
    "tests/test_root_decision_kernel_v01.py::test_gt_authority_flags_remain_gt_advisory_invalid[creates_final_output-True]",
    "tests/test_root_decision_kernel_v01.py::test_gt_authority_flags_remain_gt_advisory_invalid[requests_effect-True]",
    "tests/test_root_decision_kernel_v01.py::test_post_vv_failed_is_hard_and_preserves_all_normalized_reasons",
    "tests/test_root_signer_isolation_v01.py::test_complete_cross_root_signing_matrix_is_blocked[0-1]",
    "tests/test_root_signer_isolation_v01.py::test_complete_cross_root_signing_matrix_is_blocked[0-2]",
    "tests/test_root_signer_isolation_v01.py::test_complete_cross_root_signing_matrix_is_blocked[1-0]",
    "tests/test_root_signer_isolation_v01.py::test_complete_cross_root_signing_matrix_is_blocked[1-2]",
    "tests/test_root_signer_isolation_v01.py::test_complete_cross_root_signing_matrix_is_blocked[2-0]",
    "tests/test_root_signer_isolation_v01.py::test_complete_cross_root_signing_matrix_is_blocked[2-1]",
    "tests/test_root_signer_isolation_v01.py::test_each_root_signs_and_verifies_its_own_commitment[0]",
    "tests/test_root_signer_isolation_v01.py::test_each_root_signs_and_verifies_its_own_commitment[1]",
    "tests/test_root_signer_isolation_v01.py::test_each_root_signs_and_verifies_its_own_commitment[2]",
    "tests/test_airline_semantic_provider_canonicalization_v01.py::test_provider_mechanical_or_private_fields_are_rejected[<lambda>0]",
    "tests/test_airline_semantic_provider_canonicalization_v01.py::test_provider_mechanical_or_private_fields_are_rejected[<lambda>1]",
    "tests/test_airline_semantic_provider_canonicalization_v01.py::test_provider_mechanical_or_private_fields_are_rejected[<lambda>2]",
    "tests/test_airline_semantic_provider_canonicalization_v01.py::test_provider_mechanical_or_private_fields_are_rejected[<lambda>3]",
    "tests/test_airline_semantic_provider_canonicalization_v01.py::test_provider_mechanical_or_private_fields_are_rejected[<lambda>4]",
    "tests/test_airline_semantic_provider_canonicalization_v01.py::test_provider_mechanical_or_private_fields_are_rejected[<lambda>5]",
    "tests/test_airline_semantic_provider_canonicalization_v01.py::test_proposer_semantics_are_canonicalized_by_runtime_and_existing_validator",
    "tests/test_kernel_integrity_replay_v01.py::test_replay_requires_expected_hash",
    "tests/test_kernel_integrity_replay_v01.py::test_every_replay_counter_is_zero[provider_call_count]",
    "tests/test_kernel_integrity_replay_v01.py::test_every_replay_counter_is_zero[network_call_count]",
    "tests/test_kernel_integrity_replay_v01.py::test_every_replay_counter_is_zero[semantic_rerun_count]",
    "tests/test_kernel_integrity_replay_v01.py::test_every_replay_counter_is_zero[transaction_rerun_count]",
    "tests/test_kernel_integrity_replay_v01.py::test_every_replay_counter_is_zero[corridor_rerun_count]",
    "tests/test_kernel_integrity_replay_v01.py::test_every_replay_counter_is_zero[ledger_recollection_count]",
    "tests/test_kernel_integrity_replay_v01.py::test_every_replay_counter_is_zero[crypto_recollection_count]",
    "tests/test_kernel_integrity_replay_v01.py::test_every_replay_counter_is_zero[root_decision_created_count]",
    "tests/test_kernel_integrity_replay_v01.py::test_every_replay_counter_is_zero[authority_created_count]",
    "tests/test_kernel_integrity_replay_v01.py::test_every_replay_counter_is_zero[permission_created_count]",
    "tests/test_kernel_integrity_replay_v01.py::test_every_replay_counter_is_zero[action_created_count]",
    "tests/test_kernel_integrity_replay_v01.py::test_every_replay_counter_is_zero[action_commit_packet_created_count]",
    "tests/test_kernel_integrity_replay_v01.py::test_every_replay_counter_is_zero[receipt_created_count]",
    "tests/test_kernel_integrity_replay_v01.py::test_every_replay_counter_is_zero[final_output_created_count]",
    "tests/test_kernel_integrity_replay_v01.py::test_every_replay_counter_is_zero[real_world_effects_count]",
    "tests/test_kernel_integrity_replay_v01.py::test_replay_does_not_mutate_inputs",
    "tests/test_action_packet_portability_v01.py::test_s05_real_root_revocation_at_same_unexpired_time",
    "tests/test_action_packet_portability_v01.py::test_s06_stale_revision_and_old_registry_are_not_authority",
    "tests/test_gate6_reference_conformance_v01.py::test_airline_native_adapter_work_root_and_abi",
    "tests/test_gate6_reference_conformance_v01.py::test_gate5_native_math_result_is_consumed",
    "tests/test_gate6_reference_conformance_v01.py::test_anchor_signer_and_observed_pure_replay",
    "tests/test_gate6_reference_adversarial_v01.py::test_effect_handle_public_execution_is_nontransferable",
    "tests/test_gate6_reference_adversarial_v01.py::test_coherently_rehashed_scope_and_root_refusals[scope_refs-value0-scope_expansion_forbidden]",
    "tests/test_gate6_reference_adversarial_v01.py::test_coherently_rehashed_scope_and_root_refusals[expires_at_tick-250-ttl_expansion_forbidden]",
    "tests/test_gate6_reference_adversarial_v01.py::test_coherently_rehashed_scope_and_root_refusals[root_decision_id-root-decision:g6:foreign-request_root_binding_mismatch]",
    "tests/test_gate6_reference_adversarial_v01.py::test_provider_proposal_is_consumed_but_not_permission",
    "tests/test_gate6_reference_adversarial_v01.py::test_actor_authority_escalation_rejected_at_semantic_consumer[1]",
    "tests/test_gate6_reference_adversarial_v01.py::test_actor_authority_escalation_rejected_at_semantic_consumer[2]",
    "tests/test_gate6_reference_adversarial_v01.py::test_actor_authority_escalation_rejected_at_semantic_consumer[4]",
    "tests/test_gate6_reference_adversarial_v01.py::test_unflagged_authority_mutation_at_public_consumer[actor_role-semantic_actor_authority_escalation-contribution_mode_role_mismatch]",
    "tests/test_gate6_reference_adversarial_v01.py::test_unflagged_authority_mutation_at_public_consumer[claim_authority-claim_authority_forbidden-claim_contract_invalid]",
    "tests/test_gate6_reference_adversarial_v01.py::test_persisted_drs_descent_cannot_supply_permission",
    "tests/test_gate6_reference_adversarial_v01.py::test_supplier_document_or_receipt_cannot_authorize_other_supplier[dialogue]",
    "tests/test_gate6_reference_adversarial_v01.py::test_supplier_document_or_receipt_cannot_authorize_other_supplier[receipt]",
    "tests/test_gate6_reference_adversarial_v01.py::test_current_candidate_admission_does_not_self_install",
    "tests/test_gate6_reference_inventory_v01.py::test_plan_retains_independent_owners_and_model",
    "tests/test_gate6_reference_inventory_v01.py::test_dispatch_recorder_preserves_ownership_not_runtime_acceptance",
    "tests/test_gate6_reference_inventory_v01.py::test_bad_execution_selection_refuses_without_dispatch[names0]",
    "tests/test_gate6_reference_inventory_v01.py::test_bad_execution_selection_refuses_without_dispatch[names1]",
    "tests/test_gate6_reference_inventory_v01.py::test_bad_execution_selection_refuses_without_dispatch[names2]",
    "tests/test_gate6_reference_inventory_v01.py::test_bad_execution_selection_refuses_without_dispatch[names3]",
    "tests/test_gate6_reference_inventory_v01.py::test_readiness_missing_failed_stale_and_subset",
    "tests/test_gate6_reference_inventory_v01.py::test_observer_counts_and_cleans_exception",
    "tests/test_gate6_reference_inventory_v01.py::test_observer_refuses_existing_hook_without_losing_it",
    "tests/test_gate6_reference_inventory_v01.py::test_observer_python311_syntax_and_no_monitoring_dependency",
    "tests/test_gate6_reference_inventory_v01.py::test_bridge_recovery_paths_refuse[../escape]",
    "tests/test_gate6_reference_inventory_v01.py::test_bridge_recovery_paths_refuse[/absolute]",
    "tests/test_gate6_reference_inventory_v01.py::test_bridge_recovery_paths_refuse[a/../b]",
    "tests/test_gate6_reference_inventory_v01.py::test_bridge_recovery_paths_refuse[a//b]",
    "tests/test_gate6_reference_inventory_v01.py::test_bridge_recovery_paths_refuse[./a]",
    "tests/test_gate6_reference_inventory_v01.py::test_bridge_explicit_endpoint_no_remote_fallback",
    "tests/test_gate6_reference_inventory_v01.py::test_bridge_changed_prepared_source_refuses",
)
ROOT = Path(__file__).resolve().parents[1]
DIRECT_NODE_IDS += (
    "tests/test_gate6_reference_inventory_v01.py::test_direct_exact_completeness_controls[short]",
    "tests/test_gate6_reference_inventory_v01.py::test_direct_exact_completeness_controls[substitute]",
    "tests/test_gate6_reference_inventory_v01.py::test_direct_exact_completeness_controls[duplicate]",
    "tests/test_gate6_reference_inventory_v01.py::test_direct_exact_completeness_controls[skip]",
    "tests/test_gate6_reference_inventory_v01.py::test_direct_exact_completeness_controls[xfail]",
    "tests/test_gate6_reference_inventory_v01.py::test_direct_exact_completeness_controls[missing-phase]",
    "tests/test_gate6_reference_inventory_v01.py::test_direct_exact_completeness_controls[error]",
    "tests/test_gate6_reference_inventory_v01.py::test_direct_exact_completeness_controls[deselect]",
    "tests/test_gate6_reference_inventory_v01.py::test_direct_selection_parameter_id_and_safe_subset",
    "tests/test_gate6_reference_inventory_v01.py::test_readiness_rereads_artifacts_and_input[missing]",
    "tests/test_gate6_reference_inventory_v01.py::test_readiness_rereads_artifacts_and_input[changed]",
    "tests/test_gate6_reference_inventory_v01.py::test_readiness_rereads_artifacts_and_input[profile]",
    "tests/test_gate6_reference_inventory_v01.py::test_readiness_rereads_artifacts_and_input[input]",
    "tests/test_gate6_reference_inventory_v01.py::test_readiness_rereads_artifacts_and_input[escape]",
    "tests/test_gate6_reference_inventory_v01.py::test_collection_nested_owners_and_supplied_zero[available]",
    "tests/test_gate6_reference_inventory_v01.py::test_collection_nested_owners_and_supplied_zero[python311_fallback]",
    "tests/test_gate6_reference_inventory_v01.py::test_readiness_rereads_external_football_artifacts",
    "tests/test_gate6_reference_inventory_v01.py::test_collection_observer_exception_and_conflict",
    "tests/test_gate6_reference_inventory_v01.py::test_football_lifecycle_cleanup_command_doubles[none]",
    "tests/test_gate6_reference_inventory_v01.py::test_football_lifecycle_cleanup_command_doubles[ambiguous-create]",
    "tests/test_gate6_reference_inventory_v01.py::test_football_lifecycle_cleanup_command_doubles[wait]",
    "tests/test_gate6_reference_inventory_v01.py::test_football_lifecycle_cleanup_command_doubles[kill]",
    "tests/test_gate6_reference_inventory_v01.py::test_football_lifecycle_cleanup_command_doubles[remove]",
    "tests/test_gate6_reference_inventory_v01.py::test_football_lifecycle_cleanup_command_doubles[foreign]",
    "tests/test_gate6_reference_inventory_v01.py::test_football_cli_wait_failure_still_reaps_and_flushes",
    "tests/test_gate6_model_budget_v01.py::test_model_no_authorization_no_dispatch",
    "tests/test_gate6_model_budget_v01.py::test_quality_exact_input_and_independent_oracle",
    "tests/test_gate6_model_budget_v01.py::test_real_sdk_full_wire_roles_and_no_network",
    "tests/test_gate6_model_budget_v01.py::test_count_invalid_sends_no_generation[over-cap]",
    "tests/test_gate6_model_budget_v01.py::test_count_invalid_sends_no_generation[missing]",
    "tests/test_gate6_model_budget_v01.py::test_count_invalid_sends_no_generation[boolean]",
    "tests/test_gate6_model_budget_v01.py::test_failed_dispatch_no_retry_or_budget_reset[count]",
    "tests/test_gate6_model_budget_v01.py::test_failed_dispatch_no_retry_or_budget_reset[generation]",
    "tests/test_gate6_model_budget_v01.py::test_reservation_is_durable_before_uncertain_dispatch",
    "tests/test_gate6_model_budget_v01.py::test_invalid_usage_or_finish_not_complete[missing]",
    "tests/test_gate6_model_budget_v01.py::test_invalid_usage_or_finish_not_complete[output-cap]",
    "tests/test_gate6_model_budget_v01.py::test_invalid_usage_or_finish_not_complete[truncated]",
    "tests/test_gate6_model_budget_v01.py::test_interposition_exception_and_conflict_restore",
    "tests/test_gate6_model_budget_v01.py::test_redirect_and_foreign_routing_refused",
    "tests/test_gate6_model_budget_v01.py::test_preparation_is_not_model_completion",
)
PROFILES = {
    "LIVING_G36": ("demo.run_living_gauntlet_v01", "collect_living_g36_v01", "FRESH_NATIVE", {"E5": 1, "D5": 1, "G36": 1}),
    "CONFORMANCE_G36": ("demo.run_kernel_conformance_v01", "collect_kernel_conformance_g36_v01", "FRESH_NATIVE_INDEPENDENT", {"E5": 1, "D5": 1, "G36": 1}),
    "G35": ("demo.gate3_scenario_packs_v01", "collect_pack_v01", "FRESH_FIVE_DOMAIN", {"G35": 1}),
    "G4": ("hedgehog.gate4_reference_release_v01", "collect_release_v01", "FRESH_NATIVE", {"G4": 1}),
    "G51": ("demo.run_gate5_calibration_v01", "collect", "FRESH_EXCHANGE", {"G51": 1}),
    "G52": ("demo.run_gate5_lifecycle_v01", "collect", "FRESH_RESTART", {"G52": 1}),
    "FOOTBALL": ("tools.run_gate6_football_reference_v01", "execute_case", "ACCEPTED_PROGRAM_REEXECUTION", {"FOOTBALL_CASES": 16}),
    "G44_RECORDED": ("hedgehog.gate4_reference_release_v01", "validate_release_v01", "HISTORICAL_PURE", {}),
    "G5_RECORDED": ("demo.verify_gate5_reference_v01", "main", "HISTORICAL_PURE", {}),
    "DIRECT": ("tests.test_gate6_reference_conformance_v01", "test_anchor_signer_and_observed_pure_replay", "FOCUSED_PUBLIC_BOUNDARIES", {}),
    "MODEL": ("tools.run_gate6_model_contrast_v01", "execute", "MODEL_LIVE_NOT_AUTHORIZED_NOT_RUN", {}),
}


def require(ok, reason):
    if not ok:
        raise ValueError(reason)


def read(path):
    return json.loads(Path(path).read_bytes())


def identity(path):
    p = Path(path)
    require(p.is_file() and not p.is_symlink(), "source_regular_required:" + str(p))
    data = p.read_bytes()
    return dict(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())


def plain(value):
    if dataclasses.is_dataclass(value):
        return {f.name: plain(getattr(value, f.name)) for f in dataclasses.fields(value)}
    if isinstance(value, dict):
        return {str(k): plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [plain(v) for v in value]
    if value is None or type(value) in (str, bool, int, float):
        return value
    raise TypeError("unsupported_evidence_projection:" + type(value).__name__)


def save(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(plain(value), sort_keys=True, indent=2) + "\n")


def source_closure(root=ROOT):
    """Conservative local code/schema binding without Git or producer imports."""
    root = Path(root)
    paths = [root / "pyproject.toml"]
    for directory in ("hedgehog", "demo", "tools", "tests", "fixtures", "schemas", "release"):
        paths.extend(p for p in (root / directory).rglob("*")
                     if p.suffix in (".py", ".json", ".yaml", ".yml", ".toml", ".wasm")
                     and "__pycache__" not in p.parts)
    paths.append(root / "docs/gate6_reference_execution_v01.md")
    paths.extend(p for p in (root / "docs/gate5_reference_evidence_v01").rglob("*") if p.is_file())
    return {str(p.relative_to(root)): identity(p) for p in sorted(set(paths))}


def safe_file(folder, name):
    from tools.run_gate6_football_reference_v01 import safe_path
    root = Path(folder).resolve()
    p = root / safe_path(name)
    require(all(not item.is_symlink() for item in (p, *p.parents) if item != root), "symlink_evidence")
    require(p.resolve().is_relative_to(root), "evidence_escape")
    identity(p)
    return p


def input_closure(options):
    """Only named public resources. Credential locator/content is never hashed."""
    result = {}
    for key in ("scenario_dir", "work", "parent_directory", "package", "trust", "controlled", "authorization"):
        value = options.get(key)
        if value is None or not isinstance(value, str):
            continue
        p = Path(value)
        require(p.is_absolute() and not p.is_symlink() and p.exists(), "input_path:" + key)
        if p.is_dir():
            files = {}
            for f in sorted(p.rglob("*")):
                require(not f.is_symlink(), "input_symlink")
                # Football's outputs are not immutable inputs or circular hashes.
                if f.is_file() and "SUPERVISOR_EVIDENCE" not in f.relative_to(p).parts:
                    files[str(f.relative_to(p))] = identity(f)
            result[key] = dict(path=str(p), files=files)
        else:
            result[key] = dict(path=str(p), file=identity(p))
    return result


def verify_artifacts(record, profile, plan):
    require(record.get("profile") == profile and record.get("base") == BASE, "profile_base_binding")
    require(record.get("source_closure") == plan["source_closure"], "proposal_binding")
    require(record.get("input_closure") == input_closure(record.get("explicit_inputs", {})), "input_changed")
    folder = record.get("output_directory")
    require(isinstance(folder, str) and Path(folder).is_absolute(), "output_directory")
    files = record.get("output_files")
    require(isinstance(files, dict) and bool(files), "output_inventory")
    for name, pin in files.items():
        require(identity(safe_file(folder, name)) == pin, "output_changed:" + name)
    declaration = read(safe_file(folder, "PROFILE.json"))
    require(declaration == dict(profile=profile, base=BASE), "output_profile_binding")
    if profile == "DIRECT":
        require(direct_result(read(safe_file(folder, "direct_phases.json"))) == "PASS", "direct_incomplete")
    if profile == "MODEL":
        require(read(safe_file(folder, "comparison.json"))["status"] == "LIVE_CONTRAST_COMPLETE", "model_live_incomplete")
    if profile == "FOOTBALL":
        external = Path(record["explicit_inputs"]["work"]) / "SUPERVISOR_EVIDENCE"
        files = record.get("external_output_files")
        require(isinstance(files, dict) and bool(files), "football_external_inventory")
        for name, pin in files.items():
            require(identity(safe_file(external, name)) == pin, "football_external_changed:" + name)


def sentinel():
    return None


@contextmanager
def observe_calls(functions, *, output=None, phase="bounded_operation"):
    """Exact code-object, current-thread/process events; no child-process claim."""
    require(sys.getprofile() is None and threading.getprofile() is None, "observer_conflict")
    codes = {id(f.__code__): (f.__code__, label) for label, f in functions.items()}
    codes[id(sentinel.__code__)] = (sentinel.__code__, "sentinel")
    record = dict(pid=os.getpid(), thread=threading.get_ident(), phase=phase, entered=time.time(), scope="CURRENT_PROCESS_CURRENT_THREAD_ONLY",
                  children="UNOBSERVED_NOT_ZERO", events=[], counts={}, direct_owners={}, nested={}, identities={})
    for label, f in functions.items():
        record["identities"][label] = dict(file=f.__code__.co_filename, line=f.__code__.co_firstlineno,
                                            symbol=f.__qualname__, **identity(f.__code__.co_filename))
    stack = []
    def observe(code, event):
        target = codes.get(id(code))
        if target is None or target[0] is not code or threading.get_ident() != record["thread"]:
            return
        label = target[1]
        if event == "call":
            family = label.split(":")[0]
            owners = [v.split(":")[0] for v in stack]
            nested = family in owners or (family == "D5" and "E5" in owners)
            record["counts"][label] = record["counts"].get(label, 0) + 1
            bucket = record["nested"] if nested else record["direct_owners"]
            bucket[family] = bucket.get(family, 0) + 1
            record["events"].append(dict(event=event, label=label, parents=list(stack), nested=nested, time=time.monotonic()))
            stack.append(label)
        else:
            record["events"].append(dict(event=event, label=label, time=time.monotonic()))
            if stack and stack[-1] == label:
                stack.pop()
    def observer(frame, event, arg):
        if event in ("call", "return"):
            observe(frame.f_code, event)
    monitoring = getattr(sys, "monitoring", None)
    tool = 4
    enabled = []
    reserved = False
    try:
        if monitoring is None:
            record["backend"] = "SET_PROFILE_EXACT_IDENTITY_311"
            sys.setprofile(observer)
        else:
            require(all(monitoring.get_tool(i) is None for i in range(6)), "observer_monitoring_conflict")
            monitoring.use_tool_id(tool, "gate6-passive-exact-calls")
            reserved = True
            record["backend"] = "LOCAL_START_RETURN_FILTERED_GLOBAL_UNWIND"
            monitoring.register_callback(tool, monitoring.events.PY_START, lambda code, *args: observe(code, "call"))
            monitoring.register_callback(tool, monitoring.events.PY_RETURN, lambda code, *args: observe(code, "return"))
            monitoring.register_callback(tool, monitoring.events.PY_UNWIND, lambda code, *args: observe(code, "unwind"))
            # PY_UNWIND is not a local event; only exceptional exits use its filter.
            monitoring.set_events(tool, monitoring.events.PY_UNWIND)
            events = monitoring.events.PY_START | monitoring.events.PY_RETURN
            for code, _ in codes.values():
                monitoring.set_local_events(tool, code, events)
                enabled.append(code)
        sentinel()
        yield record
    finally:
        if monitoring is None:
            sys.setprofile(None)
        elif reserved:
            monitoring.set_events(tool, 0)
            for code in enabled:
                monitoring.set_local_events(tool, code, 0)
            for event in (monitoring.events.PY_START, monitoring.events.PY_RETURN, monitoring.events.PY_UNWIND):
                monitoring.register_callback(tool, event, None)
            monitoring.free_tool_id(tool)
        record["restored"] = sys.getprofile() is None and (monitoring is None or not reserved or monitoring.get_tool(tool) is None)
        record["sentinel_live"] = record["counts"].get("sentinel") == 1
        record["rationale"] = "Same-family nested wrappers are one owner; D5 inside E5 is visible nested work, not another direct D5."
        record["exited"] = time.time()
        if output is not None:
            save(output, record)


def collection_functions():
    return {
        "E5": module("demo.run_continuous_delta_runtime_g2_e_v01").collect_continuous_delta_runtime_g2_e_v01,
        "D5": module("demo.run_fractal_runtime_g2_d_v02").collect_fractal_runtime_g2_d_v02,
        "G36": module("hedgehog.gate3_mechanism_v01").collect_mechanism_v01,
        "G36:episode": module("hedgehog.domains.supplier_water_filter.adversarial_feedback_v01").collect_episode_v01,
        "D_NATIVE": module("hedgehog.kernel.fractal_runtime_v02").run_fractal_runtime_v02,
    }


def validate_direct_selection(nodes):
    require(type(nodes) is list and nodes and all(type(n) is str for n in nodes), "direct_exact_ids_required")
    require(len(nodes) == len(set(nodes)), "direct_duplicate")
    require(set(nodes) <= set(DIRECT_NODE_IDS), "direct_out_of_scope")
    return nodes


def direct_result(record):
    expected = list(DIRECT_NODE_IDS)
    collected = record.get("collected", [])
    phases = record.get("phases", [])
    if record.get("exitstatus") != 0 or record.get("deselected") or record.get("collection_errors"):
        return "INCOMPLETE"
    if len(collected) != len(set(collected)) or set(collected) != set(expected):
        return "PARTIAL_PROFILE"
    actual = [(v["nodeid"], v["when"]) for v in phases]
    required = {(n, phase) for n in expected for phase in ("setup", "call", "teardown")}
    if len(actual) != len(required) or set(actual) != required:
        return "INCOMPLETE"
    return "PASS" if all(v["outcome"] == "passed" and not v.get("wasxfail") for v in phases) else "INCOMPLETE"


class DirectPhases:
    def __init__(self, output):
        self.output = output
        self.value = dict(collected=[], phases=[], deselected=[], collection_errors=[])
    def pytest_collection_finish(self, session):
        self.value["collected"] = [item.nodeid for item in session.items]
        save(self.output, self.value)
    def pytest_deselected(self, items):
        self.value["deselected"].extend(item.nodeid for item in items)
    def pytest_collectreport(self, report):
        if report.failed:
            self.value["collection_errors"].append(report.nodeid)
    def pytest_runtest_logreport(self, report):
        self.value["phases"].append(dict(nodeid=report.nodeid, when=report.when, outcome=report.outcome,
                                        wasxfail=getattr(report, "wasxfail", None), seconds=report.duration,
                                        properties=report.user_properties if report.when == "call" else [],
                                        failure=report.longreprtext if report.failed else None))
        save(self.output, self.value)
    def pytest_sessionfinish(self, session, exitstatus):
        self.value["exitstatus"] = int(exitstatus)
        self.value["origins"] = {k: v.__file__ for k, v in sys.modules.items() if k.startswith(("hedgehog", "tests.", "demo.", "tools.")) and getattr(v, "__file__", None)}
        save(self.output, self.value)


def inspect_plan(root=ROOT):
    rows = []
    for name, (module, symbol, classification, owners) in PROFILES.items():
        path = Path(root) / (module.replace(".", "/") + ".py")
        tree = ast.parse(path.read_bytes())
        found = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == symbol]
        require(len(found) == 1, "entrypoint_missing_or_ambiguous:" + name)
        rows.append(dict(id=name, module=module, symbol=symbol, signature=ast.unparse(found[0].args),
            source=dict(path=str(path.relative_to(root)), **identity(path)), classification=classification,
            required=True, state="NOT_AUTHORIZED_NOT_RUN" if name == "MODEL" else "NOT_RUN",
            declared_top_level_owners=owners, supplied_collector_calls=0))
    from tools.run_gate6_football_reference_v01 import CASES
    return dict(profile="G6_FINITE_REFERENCE_COMPOSITION_V01", base=BASE, rows=rows, source_closure=source_closure(root),
        direct_node_ids=list(DIRECT_NODE_IDS), direct_baseline_cases=135,
        football_cases=CASES, independent_owners=["LIVING_G36", "CONFORMANCE_G36"],
        declared_total_top_level=dict(E5=2, D5=2, G36=2, G35=1, G4=1, G51=1, G52=1, FOOTBALL_CASES=16),
        runtime_observed=False, source_admission="NOT_PERFORMED", readiness="INCOMPLETE", gate6_closed=False)


def readiness(plan, receipts, root=ROOT):
    """A report is not an admission token; all retained required rows stay visible."""
    reasons = []
    current_sources = source_closure(root)
    for row in plan["rows"]:
        name = row["id"]
        record = receipts.get(name)
        if not isinstance(record, dict) or record.get("status") != "PASS":
            reasons.append(name + "_MISSING_FAILED_OR_NOT_RUN")
        elif (record.get("source") != row["source"] or
              record.get("source_closure") != plan["source_closure"] or
              current_sources != plan["source_closure"]):
            reasons.append(name + "_STALE_SOURCE")
        elif name == "FOOTBALL" and set(record.get("cases", ())) != set(plan["football_cases"]):
            reasons.append("FOOTBALL_INCOMPLETE_16")
        else:
            try:
                verify_artifacts(record, name, plan)
            except (ValueError, OSError, KeyError, TypeError) as exc:
                reasons.append(name + "_ARTIFACT_REFUSED:" + type(exc).__name__)
    return dict(status="INCOMPLETE" if reasons else "EXECUTION_COMPLETE_PENDING_REVIEW", reasons=reasons,
                source_admission="NOT_PERFORMED", gate6_closed=False)


def selection(names, *, allow_model=False):
    require(bool(names) and len(names) == len(set(names)), "nonempty_unique_selection_required")
    require(all(n in PROFILES and (n != "MODEL" or allow_model) for n in names), "unknown_or_unauthorized_profile")
    return tuple(names)


def invoke_selected(names, dispatch):
    """The injectable dispatch is for ownership harness tests, never runtime proof."""
    return {name: dispatch(name) for name in selection(names)}


def environment(root=ROOT):
    env = {k: os.environ[k] for k in ("HOME", "PATH", "LANG", "TMPDIR") if k in os.environ}
    env.update(PYTHONDONTWRITEBYTECODE="1", PYTEST_DISABLE_PLUGIN_AUTOLOAD="1", PYTHONPATH=str(root), GIT_OPTIONAL_LOCKS="0")
    return env


def module(name):
    result = importlib.import_module(name)
    require(Path(result.__file__).resolve() == ROOT / (name.replace(".", "/") + ".py"), "import_origin:" + name)
    return result


def saved_files(folder):
    return {str(p.relative_to(folder)): identity(p) for p in Path(folder).rglob("*") if p.is_file() and "private" not in p.relative_to(folder).parts}


def g5_expected(folder, root=ROOT):
    # A fresh capture hash is a local test pin, not an independent review verdict.
    from hedgehog.external_drs.gate5_contracts_v01 import sha
    names = ("gate5_contracts_v01", "gate5_native_v01", "gate5_exchange_v01", "gate5_lifecycle_v01")
    return dict(capture_files=saved_files(folder), source_pins={"hedgehog/external_drs/" + x + ".py": identity(root / ("hedgehog/external_drs/" + x + ".py"))["sha256"] for x in names},
                operator_trust_sha256=sha(read(Path(folder) / "operator_trust.json")))


def execute_profile(name, output, inputs):
    """One deliberate owner; callers must select execution, never import discovery."""
    selection([name], allow_model=True)
    output = Path(output).resolve()
    require(output != ROOT and ROOT not in output.parents and not output.exists(), "fresh_external_output_required")
    output.mkdir(parents=True)
    save(output / "PROFILE.json", dict(profile=name, base=BASE))
    data = output / "native"
    options = inputs.get(name, {})
    if name in ("LIVING_G36", "CONFORMANCE_G36"):
        owner = module(PROFILES[name][0])
        functions = collection_functions()
        with observe_calls(functions, output=output / "collection_observation.json", phase=name+":collection") as collected:
            value = getattr(owner, PROFILES[name][1])(data)
        save(output / "collection_observation.json", collected)
        require(collected["sentinel_live"] and all(collected["direct_owners"].get(k) == 1 for k in ("E5", "D5", "G36")), "actual_collection_ownership")
        check = owner.validate_living_g36_v01 if name == "LIVING_G36" else owner.validate_kernel_conformance_g36_v01
        with observe_calls(functions, output=output / "supplied_observation.json", phase=name+":supplied") as supplied:
            errors = check(value)
        save(output / "supplied_observation.json", supplied)
        require(supplied["sentinel_live"] and not any(v for k, v in supplied["counts"].items() if k != "sentinel"), "supplied_recollected")
        require(not errors, "supplied_successor:" + repr(errors))
        require(value["g3_collector_calls"] == value["e5_collector_calls"] == 1, "owner_counts")
        save(output / "full_return.json", value)
        return dict(status="PASS", classification=PROFILES[name][2], supplied_errors=errors, independent_owner=name)
    if name == "G35":
        value = module(PROFILES[name][0]).collect_pack_v01(data)
        consumer = module("hedgehog.outcome_feedback_report_v01")
        sources, baseline = read(data / "sources.json"), read(data / "independent_baseline.json")
        errors = consumer.validate_supplied_report_v01(value, sources=sources, baseline=baseline)
        require(not errors, "g35_supplied:" + repr(errors))
        replay = consumer.replay_v01(report=value, sources=sources, baseline=baseline)
        save(output / "full_return.json", value)
        save(output / "supplied_replay.json", replay)
        return dict(status="PASS", classification=PROFILES[name][2])
    if name == "G4":
        value = module(PROFILES[name][0]).collect_release_v01(data, controlled_clock=False)
        consumer = module("hedgehog.gate4_reference_evidence_v01")
        ledger = {p: identity(ROOT / p) for p in (
            "hedgehog/gate4_reference_evidence_v01.py", "hedgehog/gate4_reference_runtime_v01.py",
            "hedgehog/domains/airline/gate4_reference_adapter_v01.py", "hedgehog/domains/airline/gate4_reference_history_v01.py",
            "hedgehog/gate4_pressure_budget_v01.py", "hedgehog/gate4_strategy_reference_v01.py", "hedgehog/gate4_reference_contracts_v01.py")}
        save(output / "producer_sources.json", ledger)
        consumer.export_package_v01(saved_inputs=data, source_root=ROOT, source_ledger=output / "producer_sources.json", output=output / "package")
        trust = dict(profile="G43_EXTERNAL_PIN_V01", status="TEST_SUPPLIED_PIN", publication_sha256=identity(output / "package/PUBLICATION.json")["sha256"])
        save(output / "local_test_trust.json", trust)
        reports = []
        for ordinal in (1, 2):
            report = output / ("supplied_%d.json" % ordinal)
            argv = [sys.executable, "-B", "-m", "demo.run_gate6_reference_v01", "g4-supplied", "--inputs", str(output / "local_test_trust.json"), "--package", str(output / "package"), "--output", str(report)]
            subprocess.run(argv, cwd=ROOT, env=environment(), check=True)
            reports.append(read(report))
        save(output / "summary.json", value["summary"])
        return dict(status="PASS", classification="FRESH_G4_WITH_TWO_PURE_TEST_PIN_CONSUMERS", supplied=reports)
    if name in ("G51", "G52"):
        require("scenario_dir" in options, "declared_scenario_dir_required:" + name)
        module(PROFILES[name][0]).collect(data, Path(options["scenario_dir"]).resolve())
        expected = g5_expected(data)
        save(output / "local_test_expected.json", expected)
        consumer = module("hedgehog.external_drs." + ("gate5_supplied_v01" if name == "G51" else "gate5_lifecycle_supplied_v01"))
        verified = getattr(consumer, "verify_capture" if name == "G51" else "verify")(data, expected, ROOT)
        save(output / "supplied.json", verified)
        return dict(status="PASS", classification=PROFILES[name][2], trust="LOCAL_TEST_PINS_NOT_INDEPENDENT_ACCEPTANCE")
    if name == "FOOTBALL":
        bridge = module(PROFILES[name][0])
        require(set(options) == {"work", "docker", "endpoint", "config", "cases"}, "football_explicit_inputs")
        cases = options["cases"]
        require(cases and len(cases) == len(set(cases)) and set(cases) <= set(bridge.CASES), "football_case_selection")
        results = {}
        for case in cases:
            results[case] = bridge.execute_case(options["work"], case, docker=options["docker"], endpoint=options["endpoint"], config=options["config"])
            for ordinal in (1, 2):
                supplied = output / (case + "_supplied_%d.json" % ordinal)
                subprocess.run([sys.executable, "-B", "-m", "tools.run_gate6_football_reference_v01", "supplied", "--work", options["work"], "--case", case, "--output", str(supplied)], cwd=ROOT, env=environment(), check=True)
        save(output / "results.json", results)
        external = Path(options["work"]) / "SUPERVISOR_EVIDENCE"
        files = {str(p.relative_to(external)): identity(p) for case in cases for p in (external / case).rglob("*") if p.is_file()}
        return dict(status="PASS" if set(cases) == set(bridge.CASES) else "PARTIAL_PROFILE", cases=cases,
                    external_output_files=files, classification=PROFILES[name][2])
    if name == "G44_RECORDED":
        require(set(options) == {"parent_directory", "parent_pin", "package", "trust"}, "recorded_g44_inputs_required")
        actual = dict(options)
        if isinstance(actual["trust"], str):
            actual["trust"] = read(actual["trust"])
        result = module(PROFILES[name][0]).validate_release_v01(**actual, root=ROOT)
        save(output / "supplied.json", result)
        return dict(status="PASS", classification="HISTORICAL_PURE_NOT_FRESH_G4")
    if name == "G5_RECORDED":
        subprocess.run([sys.executable, "-B", "-m", "demo.verify_gate5_reference_v01", "--output", str(data)], cwd=ROOT, env=environment(), check=True)
        return dict(status="PASS", classification="HISTORICAL_PURE_NOT_FRESH_NATIVE")
    if name == "DIRECT":
        nodes = validate_direct_selection(options.get("nodes"))
        save(output / "selection.json", nodes)
        subprocess.run([sys.executable, "-B", "-m", "demo.run_gate6_reference_v01", "direct-child", "--inputs", str(output / "selection.json"), "--output", str(output / "direct_phases.json")], cwd=ROOT, env=environment(), check=True)
        return dict(status=direct_result(read(output / "direct_phases.json")), classification=PROFILES[name][2], nodes=nodes)
    if name == "MODEL":
        return module("tools.run_gate6_model_contrast_v01").execute(output, **options)
    raise ValueError("profile_not_implemented")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode", choices=("inspect", "preflight", "execute", "readiness", "g4-supplied", "direct-child"), nargs="?", default="preflight")
    p.add_argument("--profile", action="append", choices=tuple(PROFILES))
    p.add_argument("--inputs", type=Path)
    p.add_argument("--output", type=Path)
    p.add_argument("--package", type=Path)
    args = p.parse_args(argv)
    if args.mode == "direct-child":
        nodes = validate_direct_selection(read(args.inputs))
        import pytest
        return int(pytest.main(["-p", "no:cacheprovider", "-q", *nodes], plugins=[DirectPhases(args.output)]))
    if args.mode == "g4-supplied":
        require(all((args.inputs, args.output, args.package)), "supplied_inputs_required")
        value = module("hedgehog.gate4_reference_evidence_v01").verify_package_v01(package=args.package, trust=read(args.inputs))
        save(args.output, value)
        return 0
    plan = inspect_plan()
    if args.mode == "readiness":
        value = readiness(plan, read(args.inputs) if args.inputs else {})
    elif args.mode in ("inspect", "preflight"):
        value = plan
        value["preflight"] = "STATIC_SOURCE_SIGNATURES_ONLY_NO_RUNTIME"
    else:
        require(args.output is not None, "output_required")
        selected = selection(args.profile or [], allow_model=True)
        args.output.mkdir(parents=True, exist_ok=False)
        inputs = read(args.inputs) if args.inputs else {}
        save(args.output / "plan.json", plan)
        receipts = {}
        for name in selected:
            start = time.time()
            row = next(x for x in plan["rows"] if x["id"] == name)
            bound_inputs = input_closure(inputs.get(name, {}))
            save(args.output / (name + "_started.json"), dict(profile=name, pid=os.getpid(), started=start, source=row["source"],
                 source_closure=plan["source_closure"], explicit_inputs=inputs.get(name, {})))
            try:
                result = execute_profile(name, args.output / name, inputs)
            except BaseException as exc:
                save(args.output / (name + "_failure.json"), dict(error=repr(exc), seconds=time.time() - start))
                raise
            require(source_closure() == plan["source_closure"], "source_changed_during_profile:" + name)
            require(input_closure(inputs.get(name, {})) == bound_inputs, "input_changed_during_profile")
            receipts[name] = dict(result, profile=name, base=BASE, input_closure=bound_inputs,
                output_directory=str((args.output / name).resolve()), source=row["source"], source_closure=plan["source_closure"],
                explicit_inputs=inputs.get(name, {}), seconds=time.time() - start, output_files=saved_files(args.output / name))
            save(args.output / "receipts.json", receipts)
        value = readiness(plan, receipts)
        save(args.output / "readiness.json", value)
    if args.output and args.mode != "execute":
        save(args.output, value)
    print(json.dumps(plain(value), sort_keys=True))
    return 1 if args.mode == "readiness" and value["status"] == "INCOMPLETE" else 0


if __name__ == "__main__":
    raise SystemExit(main())
