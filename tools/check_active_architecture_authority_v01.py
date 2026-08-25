#!/usr/bin/env python3
"""Validate the active Hedgehog OS document/onboarding authority boundary."""

from __future__ import annotations

import argparse
import ast
import fnmatch
import json
from pathlib import Path, PurePosixPath
import subprocess
from typing import Iterable, Sequence


BASE_HEAD = "931645dc724c54d635f32dabfca4b62fbc9a39a2"
LOCK_PATH = "specs/current_architecture_lock_v01.md"
INDEX_PATH = "specs/document_authority_index_v01.json"
MANIFEST_PATH = "release/successor_context_manifest_v01.json"
RETIRED_INVENTORY_PATH = "release/retired_architecture_inventory_v01.json"
CURRENT_SCHEMA_SURFACE_PATH = "release/current_schema_surface_v01.json"
COMPLETION_MANIFEST_PATH = "release/completion_manifest.json"
SEAM_INDEX_PATH = "release/integration_seam_index.json"
CONFORMANCE_SOURCE_PATH = "hedgehog/kernel/conformance_v01.py"
KERNEL_CONFORMANCE_RUNNER_PATH = "demo/run_kernel_conformance_v01.py"
LIVING_GAUNTLET_PATH = "demo/run_living_gauntlet_v01.py"

ALLOWED_CHANGED_PATHS = frozenset(
    {
        "AGENTS.md",
        INDEX_PATH,
        MANIFEST_PATH,
        RETIRED_INVENTORY_PATH,
        CURRENT_SCHEMA_SURFACE_PATH,
        "demo/run_kernel_conformance_v01.py",
        "demo/run_living_gauntlet_v01.py",
        "hedgehog/kernel/conformance_v01.py",
        "release/completion_manifest.json",
        "release/current_schema_surface_v01.json",
        "release/integration_seam_index.json",
        "release/retired_architecture_inventory_v01.json",
        "tools/check_active_architecture_authority_v01.py",
        "tests/test_active_architecture_authority_v01.py",
        "tests/test_drs_semantic_address_reuse_certificate_g2_b_v01.py",
        "tests/test_kernel_conformance_v01_runner.py",
        "tests/test_living_gauntlet_v01_runner.py",
        "tests/test_repository_release_spine_v01.py",
    }
)

AUTHORITY_INDEX_KEYS = (
    "schema_version",
    "generated_for_head",
    "current_normative_documents",
    "current_operational_documents",
    "current_technical_annexes",
    "future_reference_documents",
    "historical_documents",
    "audit_only_sources",
    "excluded_from_successor_onboarding",
    "source_of_truth_order",
    "notes",
)
MANIFEST_KEYS = (
    "schema_version",
    "base_head",
    "manifest_status",
    "onboarding_ready",
    "blocking_repairs",
    "purpose",
    "always_include",
    "include_current_gate_sources",
    "include_current_gate_tests",
    "include_current_release_sources",
    "exclude_paths",
    "exclude_globs",
    "deferred_e5_transplant",
    "authority_documents",
    "historical_access_method",
    "validation_command",
)
CURRENT_DOCUMENT_ENTRY_KEYS = (
    "path",
    "status",
    "current_authority",
    "authority_scope",
    "may_override_architecture_lock",
    "onboarding_allowed",
    "role",
)
HISTORICAL_ENTRY_KEYS = (
    "path",
    "status",
    "historical_git_ref",
    "current_authority",
    "onboarding_allowed",
    "preservation",
    "current_replacement",
)
DEFERRED_ENTRY_KEYS = ("path", "status")

REQUIRED_HISTORICAL_PATHS = (
    "specs/human_passport_v0_25.md",
    "specs/math_appendix_v0_3.md",
    "specs/machine_manifest_v0_25.json",
    "specs/schema_package_v0_25_reference.md",
    "specs/invariants.md",
    "specs/demo_baseline_v0_25.md",
    "specs/demo_scenario.md",
    "specs/legacy_mapping.md",
    "docs/passport_geometry_root_needles.md",
    "docs/strategic_expansion_map.md",
)
REQUIRED_ALWAYS_INCLUDE = frozenset(
    {
        "AGENTS.md",
        "README.md",
        LOCK_PATH,
        INDEX_PATH,
        MANIFEST_PATH,
        RETIRED_INVENTORY_PATH,
        CURRENT_SCHEMA_SURFACE_PATH,
        "docs/continuous_delta_runtime_v0_1_g2_e_preflight_v01.md",
        "docs/continuous_delta_runtime_v0_1_g2_e_post_acceptance_contract_addendum_v01.md",
        "hedgehog/__init__.py",
        "hedgehog/drs.py",
        "hedgehog/local_drs_resolver.py",
        "hedgehog/local_drs_v02.py",
        "hedgehog/reuse_gate.py",
        "hedgehog/semantic_reasoning_adapter.py",
        "hedgehog/evidence/__init__.py",
        "hedgehog/evidence/external_anchor_v01.py",
        "hedgehog/evidence/sealed_evidence_profile_v01.py",
        "hedgehog/evidence/sealed_package_v01.py",
        "hedgehog/evidence/sealed_replay_evidence_v01.py",
        "hedgehog/kernel/abi_v01.py",
        "hedgehog/kernel/integrity_replay_v01.py",
        "hedgehog/kernel/root_decision_v01.py",
        "hedgehog/kernel/root_signer_isolation_v01.py",
        "hedgehog/kernel/execution_mode_router_v01.py",
        "hedgehog/kernel/fractal_runtime_v02.py",
        "hedgehog/kernel/continuous_delta_runtime_v01.py",
        "hedgehog/time_model.py",
        "hedgehog/domains/airline/kernel_adapter_v01.py",
        "hedgehog/domains/supplier_water_filter/kernel_adapter_v01.py",
        "schemas/common.schema.json",
        "schemas/time_envelope.schema.json",
        "schemas/result_proposal.schema.json",
        "schemas/vv_report.schema.json",
        "schemas/gt_report.schema.json",
        "release/current_status_overlay_v01.json",
        "release/claim_to_evidence_index.md",
        "release/current_limitations.md",
        "release/current_release_notes.md",
        "release/one_command_gauntlet.md",
        "release/completion_manifest.json",
        "release/integration_seam_index.json",
        "release/integration_seam_index.md",
    }
)
REQUIRED_GATE_SOURCES = frozenset(
    {
        "hedgehog/context_packets.py",
        "hedgehog/__init__.py",
        "hedgehog/drs.py",
        "hedgehog/local_drs_resolver.py",
        "hedgehog/local_drs_v02.py",
        "hedgehog/reuse_gate.py",
        "hedgehog/semantic_reasoning_adapter.py",
        "hedgehog/evidence/__init__.py",
        "hedgehog/evidence/external_anchor_v01.py",
        "hedgehog/evidence/sealed_evidence_profile_v01.py",
        "hedgehog/evidence/sealed_package_v01.py",
        "hedgehog/evidence/sealed_replay_evidence_v01.py",
        "hedgehog/action_commit_packet_v02.py",
        "hedgehog/drs_semantic_address_v01.py",
        "hedgehog/drs_memory_resolution_v01.py",
        "hedgehog/reuse_certificate_v01.py",
        "hedgehog/kernel/semantic_work_v01.py",
        "hedgehog/kernel/transition_registry_v01.py",
        "hedgehog/kernel/effect_firewall_v01.py",
        "hedgehog/kernel/multiroot_v01.py",
        "hedgehog/kernel/root_signer_isolation_v01.py",
        "hedgehog/kernel/execution_mode_router_v01.py",
        "hedgehog/kernel/fractal_runtime_v02.py",
        "hedgehog/kernel/continuous_delta_runtime_v01.py",
        CONFORMANCE_SOURCE_PATH,
        "hedgehog/time_model.py",
        "hedgehog/domains/airline/kernel_adapter_v01.py",
        "hedgehog/domains/supplier_water_filter/kernel_adapter_v01.py",
        "schemas/common.schema.json",
        "schemas/time_envelope.schema.json",
        "schemas/result_proposal.schema.json",
        "schemas/vv_report.schema.json",
        "schemas/gt_report.schema.json",
        "schemas/execution_mode_router_v01.schema.json",
        "schemas/fractal_runtime_v02.schema.json",
        "schemas/continuous_delta_runtime_v01.schema.json",
        "demo/run_kernel_conformance_v01.py",
        "demo/run_living_gauntlet_v01.py",
    }
)
REQUIRED_GATE_TESTS = frozenset(
    {
        "tests/test_action_commit_packet_lifecycle_g2_a_v01.py",
        "tests/test_drs_semantic_address_reuse_certificate_g2_b_v01.py",
        "tests/test_execution_mode_router_g2_c_v01.py",
        "tests/test_fractal_runtime_g2_d_v02.py",
        "tests/test_continuous_delta_runtime_g2_e_v01.py",
        "tests/test_kernel_integrity_replay_v01.py",
        "tests/test_root_signer_isolation_v01.py",
        "tests/test_airline_kernel_adapter_v01.py",
        "tests/test_supplier_water_filter_kernel_adapter_v01.py",
        "tests/test_living_gauntlet_v01_runner.py",
        "tests/test_kernel_conformance_v01_runner.py",
    }
)
REQUIRED_RELEASE_SOURCES = frozenset(
    {
        "release/current_status_overlay_v01.json",
        "release/claim_to_evidence_index.md",
        "release/current_limitations.md",
        "release/current_release_notes.md",
        "release/one_command_gauntlet.md",
        "release/completion_manifest.json",
        "release/integration_seam_index.json",
        "release/integration_seam_index.md",
        RETIRED_INVENTORY_PATH,
        CURRENT_SCHEMA_SURFACE_PATH,
    }
)
REQUIRED_DEFERRED_E5_PATHS = frozenset(
    {
        "hedgehog/kernel/continuous_delta_runtime_v01.py",
        "tests/test_continuous_delta_runtime_g2_e_v01.py",
        "demo/run_continuous_delta_runtime_g2_e_v01.py",
    }
)

REQUIRED_MANIFEST_STATUS = "SUCCESSOR_ONBOARDING_READY"
REQUIRED_BLOCKING_REPAIRS: tuple[str, ...] = ()
S3_GENERATED_FROM_HEAD = "237501110159f1adb6d8a4c5e9482d618e5a8187"
RETIRED_RECORD_KEYS = (
    "path",
    "classification",
    "current_runtime_allowed",
    "current_schema_registration_allowed",
    "current_export_allowed",
    "successor_onboarding_allowed",
    "preservation",
    "reason",
)
RETIRED_INVENTORY_KEYS = (
    "inventory_id",
    "inventory_status",
    "architecture_lock_ref",
    "generated_from_head",
    "retired_schema_paths",
    "retired_runtime_reference_paths",
    "historical_demo_test_families",
    "forbidden_current_uses",
    "preservation_law",
    "onboarding_law",
)
CURRENT_SCHEMA_SURFACE_KEYS = (
    "schema_surface_id",
    "schema_surface_status",
    "generated_from_head",
    "current_schema_paths",
    "retired_schema_paths",
    "current_loader_or_registry_refs",
    "isolation_invariants",
)
SCHEMA_LOADER_REF_KEYS = ("source_path", "schema_paths", "role")

HISTORICAL_ALL_LAYERS_RUNNER_PATH = (
    "demo/run_all_layers_applied_super_smoke.py"
)
HISTORICAL_ALL_LAYERS_TEST_PATH = (
    "tests/test_all_layers_applied_super_smoke_runner.py"
)
HISTORICAL_ALL_LAYERS_PATHS = (
    HISTORICAL_ALL_LAYERS_RUNNER_PATH,
    HISTORICAL_ALL_LAYERS_TEST_PATH,
)
_HISTORICAL_ACT_ID = "all_layers_" + "invariant_super_smoke"
_HISTORICAL_RUNNER_MODULE = "demo.run_all_layers_" + "applied_super_smoke"
_HISTORICAL_RUNNER_SYMBOL = "collect_all_layers_" + "applied_super_smoke"
CURRENT_PROFILE_ID = "kernel_conformance_v0_6_current"
HISTORICAL_PROFILE_ID = "kernel_conformance_v0_5_historical"
HISTORICAL_V05_ACTIVE_REFS = (
    "airline_deterministic_transaction_runtime",
    _HISTORICAL_ACT_ID,
    "generic_integrity_replay",
    "root_signer_isolation_conformance",
    "semantic_work_contract",
    "domain_neutral_kernel_abi",
    "causal_consumption",
    "transition_registry",
    "root_decision_kernel",
    "effect_firewall",
    "generic_multiroot",
    "supplier_water_filter_portability",
    "action_packet_lifecycle",
    "drs_semantic_address_and_reuse_certificate",
    "execution_mode_router",
    "fractal_runtime",
)
CURRENT_V06_ACTIVE_REFS = tuple(
    act_id for act_id in HISTORICAL_V05_ACTIVE_REFS if act_id != _HISTORICAL_ACT_ID
)
CURRENT_REGRESSION_CLAIM_TO_ACTS = (
    (
        "root_sole_local_final_commit_authority",
        ("root_decision_kernel", "action_packet_lifecycle", "fractal_runtime"),
    ),
    ("no_superroot_exists", ("generic_multiroot",)),
    (
        "bsep_semantic_membrane",
        ("execution_mode_router", "fractal_runtime"),
    ),
    ("runtime_execution_topology_runtime_owned", ("fractal_runtime",)),
    (
        "provider_model_advisory_only",
        ("semantic_work_contract", "fractal_runtime"),
    ),
    (
        "actor_output_cannot_create_final_output",
        ("semantic_work_contract", "fractal_runtime"),
    ),
    ("resultproposal_postvv_terminal_gt_before_root", ("fractal_runtime",)),
    (
        "drs_retrieval_reuse_no_authority",
        ("drs_semantic_address_and_reuse_certificate",),
    ),
    ("receipt_evidence_only", ("effect_firewall", "action_packet_lifecycle")),
    ("effect_capability_bounded_corridor_only", ("effect_firewall",)),
    (
        "airline_supplier_same_authority_law",
        (
            "airline_deterministic_transaction_runtime",
            "supplier_water_filter_portability",
            "action_packet_lifecycle",
        ),
    ),
    ("real_world_effects_zero", CURRENT_V06_ACTIVE_REFS),
)

RETIRED_SCHEMA_PATHS = (
    "schemas/attractor_" + "packet.schema.json",
    "schemas/plan_" + "graph.schema.json",
)
CURRENT_SCHEMA_PATHS = (
    "schemas/common.schema.json",
    "schemas/continuous_delta_runtime_v01.schema.json",
    "schemas/drs_meaning_record_v01.schema.json",
    "schemas/drs_memory_resolution_v01.schema.json",
    "schemas/drs_semantic_address_v01.schema.json",
    "schemas/execution_mode_router_v01.schema.json",
    "schemas/fractal_runtime_v02.schema.json",
    "schemas/gt_report.schema.json",
    "schemas/kernel_artifact_v01.schema.json",
    "schemas/result_proposal.schema.json",
    "schemas/reuse_certificate_v01.schema.json",
    "schemas/semantic_work_v01.schema.json",
    "schemas/time_envelope.schema.json",
    "schemas/vv_report.schema.json",
)
REQUIRED_SCHEMA_ISOLATION_INVARIANTS = (
    "RETIRED_SCHEMAS_ARE_NOT_CURRENT",
    "RETIRED_SCHEMAS_EXCLUDED_FROM_SUCCESSOR_ONBOARDING",
    "RETIRED_SCHEMAS_NOT_REGISTERED_BY_CURRENT_LOADER",
    "GIT_BYTE_PRESERVATION_ALLOWED",
    "HISTORICAL_TEST_REFERENCES_OUTSIDE_CURRENT_CONFORMANCE_ONLY",
)
RETIRED_RUNTIME_MODULE_PATHS = (
    "hedgehog/architect.py",
    "hedgehog/architect_prompt_compiler.py",
    "hedgehog/executor.py",
    "hedgehog/fractal_dag_executor.py",
    "hedgehog/llm_architect.py",
    "hedgehog/root_orchestrator.py",
    "hedgehog/trace_reporter.py",
)
RETIRED_MODULE_NAMES = frozenset(
    path[:-3].replace("/", ".") for path in RETIRED_RUNTIME_MODULE_PATHS
)
RETIRED_IMPORT_SCOPE_LABELS = {
    "current_gate1": "CURRENT_GATE1_RETIRED_IMPORTS",
    "current_gate2": "CURRENT_GATE2_RETIRED_IMPORTS",
    "living_gauntlet": "LIVING_GAUNTLET_RETIRED_IMPORTS",
    "kernel_conformance": "KERNEL_CONFORMANCE_RETIRED_IMPORTS",
    "e5": "E5_RETIRED_IMPORTS",
}

GLOBAL_ARCHITECTURE_SCOPE = "current_global_architecture_law"
OPERATIONAL_SCOPE = "operational_instructions_subordinate_to_architecture_lock"
PUBLIC_VIEW_SCOPE = "public_engineering_view_only"
SUCCESSOR_CONTEXT_SCOPE = "successor_context_selection_only"
NAMED_GATE_SCOPE = "named_gate_contract_only"
STATUS_EVIDENCE_SCOPE = "status_or_evidence_only"
AUDIT_EVIDENCE_SCOPE = "audit_evidence_only"
FUTURE_REFERENCE_SCOPE = "future_research_reference_only"
RETIRED_INVENTORY_SCOPE = "retired_architecture_inventory_only"
CURRENT_SCHEMA_SURFACE_SCOPE = "current_schema_surface_index_only"
KNOWN_AUTHORITY_SCOPES = frozenset(
    {
        GLOBAL_ARCHITECTURE_SCOPE,
        OPERATIONAL_SCOPE,
        PUBLIC_VIEW_SCOPE,
        SUCCESSOR_CONTEXT_SCOPE,
        NAMED_GATE_SCOPE,
        STATUS_EVIDENCE_SCOPE,
        AUDIT_EVIDENCE_SCOPE,
        FUTURE_REFERENCE_SCOPE,
        RETIRED_INVENTORY_SCOPE,
        CURRENT_SCHEMA_SURFACE_SCOPE,
    }
)
BOUNDED_AUTHORITATIVE_SCOPES = frozenset({OPERATIONAL_SCOPE, NAMED_GATE_SCOPE})

REQUIRED_AGENTS_ONBOARDING_WARNINGS = (
    ("manifest_status", "`SUCCESSOR_ONBOARDING_READY`"),
    ("onboarding_ready", "its `onboarding_ready` value is `true`"),
    (
        "s1_s2_s3_closed",
        "S1 document-authority succession, S2 vocabulary repair, and S3 "
        "active-schema and retired-subsystem isolation are closed.",
    ),
    (
        "architecture_clean",
        "The bounded successor context is architecture-clean and ready for guarded "
        "reintegration.",
    ),
    (
        "permanent_onboarding_guarded",
        "Permanent assistant onboarding occurs only after the sanitation changes are "
        "reintegrated into the primary worktree and the three deferred E5 paths are "
        "verified against the owner's exact frozen hashes.",
    ),
    (
        "e5_worktree_untouched",
        "The primary dirty E5 worktree remains untouched",
    ),
    (
        "no_retired_revival",
        "no compatibility, migration, alias, or revival path exists.",
    ),
)
REQUIRED_GATE_SCOPE_NOTE = (
    "Named Gate authority cannot redefine global topology, Root sovereignty, "
    "BSEP, runtime ownership, or another Gate's contract."
)

FUTURE_REFERENCE_PATH = (
    "specs/future/quantum/"
    "hedgehog_quantum_mathematical_extension_roadmap_v2_0.md"
)
FUTURE_REFERENCE_MANIFEST_EXCLUSION = "specs/future/**"
FUTURE_REFERENCE_ROLE = (
    "Future mathematical extension roadmap; not current runtime, Gate contract, "
    "implementation, completion claim, or architecture authority."
)

REQUIRED_CURRENT_CLASSIFICATIONS = {
    "current_normative_documents": {
        LOCK_PATH: (
            "current_normative_architecture_lock",
            True,
            True,
            GLOBAL_ARCHITECTURE_SCOPE,
            False,
        ),
    },
    "current_operational_documents": {
        "AGENTS.md": (
            "current_operational_view_after_s1",
            True,
            True,
            OPERATIONAL_SCOPE,
            False,
        ),
        "README.md": (
            "current_public_engineering_view_after_s1",
            False,
            True,
            PUBLIC_VIEW_SCOPE,
            False,
        ),
        MANIFEST_PATH: (
            "successor_onboarding_ready_after_s3",
            False,
            True,
            SUCCESSOR_CONTEXT_SCOPE,
            False,
        ),
        RETIRED_INVENTORY_PATH: (
            "s3_retired_architecture_inventory",
            False,
            True,
            RETIRED_INVENTORY_SCOPE,
            False,
        ),
        CURRENT_SCHEMA_SURFACE_PATH: (
            "s3_current_schema_surface_index",
            False,
            True,
            CURRENT_SCHEMA_SURFACE_SCOPE,
            False,
        ),
    },
    "current_technical_annexes": {
        "docs/domain_neutral_reference_kernel_gate1_checkpoint_v01.md": (
            "accepted_gate1_checkpoint",
            True,
            True,
            NAMED_GATE_SCOPE,
            False,
        ),
        "docs/actionpacket_lifecycle_kill_switch_g2_a_checkpoint_v01.md": (
            "accepted_gate2_g2a_checkpoint",
            True,
            True,
            NAMED_GATE_SCOPE,
            False,
        ),
        "docs/drs_semantic_address_space_reuse_certificate_g2_b_checkpoint_v01.md": (
            "accepted_gate2_g2b_checkpoint",
            True,
            True,
            NAMED_GATE_SCOPE,
            False,
        ),
        "docs/execution_mode_router_g2_c_checkpoint_v01.md": (
            "accepted_gate2_g2c_checkpoint",
            True,
            True,
            NAMED_GATE_SCOPE,
            False,
        ),
        "docs/fractal_runtime_v0_2_g2_d_post_acceptance_contract_addendum_v01.md": (
            "accepted_cumulative_gate2_g2d_contract",
            True,
            True,
            NAMED_GATE_SCOPE,
            False,
        ),
        (
            "docs/fractal_runtime_v0_2_g2_d_profile_d_t12_revise_projection_"
            "correction_checkpoint_v01.md"
        ): (
            "accepted_current_gate2_g2d_checkpoint",
            True,
            True,
            NAMED_GATE_SCOPE,
            False,
        ),
        "docs/continuous_delta_runtime_v0_1_g2_e_preflight_v01.md": (
            "accepted_repository_gate_continuation_contract",
            True,
            True,
            NAMED_GATE_SCOPE,
            False,
        ),
        "docs/continuous_delta_runtime_v0_1_g2_e_post_acceptance_contract_addendum_v01.md": (
            "accepted_cumulative_gate2_g2e_contract",
            True,
            True,
            NAMED_GATE_SCOPE,
            False,
        ),
        "release/current_status_overlay_v01.json": (
            "current_lifecycle_metadata_view",
            False,
            True,
            STATUS_EVIDENCE_SCOPE,
            False,
        ),
        "release/claim_to_evidence_index.md": (
            "current_claim_evidence_navigation",
            False,
            True,
            STATUS_EVIDENCE_SCOPE,
            False,
        ),
        "release/current_limitations.md": (
            "current_limitations_view",
            False,
            True,
            STATUS_EVIDENCE_SCOPE,
            False,
        ),
        "release/current_release_notes.md": (
            "current_engineering_notes_view",
            False,
            True,
            STATUS_EVIDENCE_SCOPE,
            False,
        ),
    },
    "future_reference_documents": {
        FUTURE_REFERENCE_PATH: (
            "future_reference_non_current",
            False,
            False,
            FUTURE_REFERENCE_SCOPE,
            False,
        ),
    },
    "audit_only_sources": {
        "docs/audit_reports/**": (
            "audit_only",
            False,
            False,
            AUDIT_EVIDENCE_SCOPE,
            False,
        ),
        "docs/evidence/**": (
            "evidence_only",
            False,
            False,
            AUDIT_EVIDENCE_SCOPE,
            False,
        ),
        "release/completion_manifest.json": (
            "current_release_completion_and_profile_index",
            False,
            True,
            STATUS_EVIDENCE_SCOPE,
            False,
        ),
        "release/integration_seam_index.json": (
            "current_release_integration_and_profile_index",
            False,
            True,
            STATUS_EVIDENCE_SCOPE,
            False,
        ),
        "release/integration_seam_index.md": (
            "historical_release_basis_overlay",
            False,
            True,
            STATUS_EVIDENCE_SCOPE,
            False,
        ),
    },
}

_RETIRED_PLAN_STEM = "plan" + "_" + "graph"
_RETIRED_PACKET_STEM = "attractor" + "_" + "packet"
REQUIRED_RETIRED_EXCLUDE_PATHS = frozenset(
    {
        "hedgehog/mode_router.py",
        "demo/run_mode_selection_matrix.py",
        "tests/test_mode_router_runtime.py",
        "tests/test_mode_selection_matrix_runner.py",
        "hedgehog/architect.py",
        "hedgehog/architect_prompt_compiler.py",
        "hedgehog/llm_architect.py",
        "hedgehog/fractal_cell_integration.py",
        "hedgehog/fractal_dag_executor.py",
        "hedgehog/fractal_fulfillment.py",
        "hedgehog/bounded_actor_contracts.py",
        "hedgehog/root_orchestrator.py",
        "hedgehog/executor.py",
        "hedgehog/trace_reporter.py",
        "hedgehog/needle_runtime.py",
        "schemas/needle.schema.json",
        f"schemas/{_RETIRED_PACKET_STEM}.schema.json",
        f"schemas/{_RETIRED_PLAN_STEM}.schema.json",
        f"demo/run_architect_from_bounded_{_RETIRED_PACKET_STEM}.py",
        "demo/run_avf_attractor_from_accepted_matrix.py",
        f"demo/run_dag_executor_from_valid_{_RETIRED_PLAN_STEM}.py",
        "demo/run_bounded_llm_semantic_executor_node_v01.py",
        "demo/run_gemini_orchestrator_architect_pair_smoke.py",
        "demo/run_fractal_cell_runtime_integration_v01.py",
        "demo/run_fractal_cell_runtime.py",
        "demo/run_fractal_dag_executor_core.py",
        "demo/run_controlled_fractal_dac_expansion_v01.py",
        "demo/run_dual_fractal_coupling_v01.py",
        "demo/run_full_semantic_e2e_v01.py",
        "demo/run_controlled_root_orchestrator_route_assembly.py",
        f"tests/test_architect_from_bounded_{_RETIRED_PACKET_STEM}_runner.py",
        "tests/test_avf_attractor_from_accepted_matrix_runner.py",
        f"tests/test_dag_executor_from_valid_{_RETIRED_PLAN_STEM}_runner.py",
        "tests/test_bounded_llm_semantic_executor_node_v01_runner.py",
        "tests/test_gemini_orchestrator_architect_pair_smoke_runner.py",
        "tests/test_architect_runtime.py",
        "tests/test_architect_prompt_compiler_runtime.py",
        "tests/test_llm_architect_runtime.py",
        "tests/test_fractal_cell_runtime_integration_v01_runner.py",
        "tests/test_fractal_cell_runtime_runner.py",
        "tests/test_fractal_dag_executor_core_runner.py",
        "tests/test_fractal_fulfillment_core.py",
        "tests/test_controlled_fractal_dac_expansion_v01_runner.py",
        "tests/test_dual_fractal_coupling_v01_runner.py",
        "tests/test_full_semantic_e2e_v01_runner.py",
        "tests/test_executor_runtime.py",
        "tests/test_executor_no_final_output.py",
        "tests/test_root_orchestrator_runtime.py",
        "tests/test_controlled_root_orchestrator_route_assembly_runner.py",
        "tests/test_post_vv_runtime.py",
        "tests/test_gt_validator_runtime.py",
        "tests/test_up_never_mutates_work.py",
        "tests/test_work_thoughts_up_separation.py",
        HISTORICAL_ALL_LAYERS_RUNNER_PATH,
        HISTORICAL_ALL_LAYERS_TEST_PATH,
    }
)
REQUIRED_EXCLUDE_GLOBS = frozenset(
    {
        "docs/audit_reports/**",
        "docs/evidence/**",
        "docs/showcase/**",
        FUTURE_REFERENCE_MANIFEST_EXCLUSION,
        "demo/run_human_*.py",
        "tests/test_human_*_runner.py",
        "demo/run_live_*.py",
        "tests/test_live_*.py",
        "demo/run_*showcase*.py",
        "tests/test_*showcase*_runner.py",
        "needles/**",
        "docs/*needle*.md",
        "demo/run_*needle*.py",
        "tests/test_*needle*.py",
        "hedgehog/marenna*.py",
        "hedgehog/up*.py",
        "schemas/marenna*.json",
        "schemas/up*.json",
        "tests/test_marenna*.py",
        "data/**",
        "_audit_exports/**",
        "**/__pycache__/**",
        "**/*.pyc",
    }
)

# Fragment construction keeps retired direct strings out of this source file.
FORBIDDEN_DIRECT_TERMS = (
    "Plan" + "Graph",
    "plan" + "_" + "graph",
    "Attractor" + "Packet",
    "attractor" + "_" + "packet",
)
REQUIRED_CURRENT_TERMS = ("BSEP", "RuntimeExecutionTopology")
SCANNED_CURRENT_DOCUMENTS = ("AGENTS.md", "README.md", LOCK_PATH)

STRUCTURED_RATIONALE_PATH = "hedgehog/structured_rationale.py"
SUPPLIER_EVENT_SOURCE_PATHS = (
    "demo/run_full_wow_v1_2_product_trace.py",
    "hedgehog/domains/supplier_water_filter/kernel_adapter_v01.py",
    (
        "hedgehog/domains/supplier_water_filter/"
        "sealed_evidence_package_adapter_v01.py"
    ),
)
_RETIRED_TITLE_PLAN = "Plan" + "Graph"
_RETIRED_SUPPLIER_EVENT = "runtime_" + "plan" + "graph_compiled"
_REQUIRED_SUPPLIER_EVENT = "runtime_execution_topology_materialized"
_RETIRED_STRUCTURED_POSITIVE_TERMS = (
    "bounded_" + _RETIRED_PLAN_STEM,
    _RETIRED_TITLE_PLAN + " remains advisory until validated",
    _RETIRED_TITLE_PLAN + " contract",
)


class DuplicateJSONKeyError(ValueError):
    """Raised when a JSON object contains a duplicate key."""


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJSONKeyError(f"duplicate key: {key}")
        result[key] = value
    return result


class StaticValueUnavailable(ValueError):
    """Raised when an assignment is not a bounded literal composition."""


def _static_value(node: ast.AST, values: dict[str, object]) -> object:
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name) and node.id in values:
        return values[node.id]
    if isinstance(node, (ast.Tuple, ast.List)):
        items: list[object] = []
        for element in node.elts:
            if isinstance(element, ast.Starred):
                expanded = _static_value(element.value, values)
                if not isinstance(expanded, (tuple, list)):
                    raise StaticValueUnavailable
                items.extend(expanded)
            else:
                items.append(_static_value(element, values))
        return tuple(items) if isinstance(node, ast.Tuple) else items
    if isinstance(node, ast.Dict):
        result: dict[object, object] = {}
        for key_node, value_node in zip(node.keys, node.values, strict=True):
            if key_node is None:
                expanded = _static_value(value_node, values)
                if not isinstance(expanded, dict):
                    raise StaticValueUnavailable
                result.update(expanded)
            else:
                result[_static_value(key_node, values)] = _static_value(
                    value_node, values
                )
        return result
    raise StaticValueUnavailable


def _static_assignments(
    source_path: Path,
    code: str,
    failures: list[str],
) -> tuple[dict[str, object], ast.Module | None, str]:
    try:
        source = source_path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        failures.append(f"{code}.read:{type(exc).__name__}")
        return {}, None, ""
    try:
        tree = ast.parse(source, filename=str(source_path))
    except SyntaxError:
        failures.append(f"{code}.syntax")
        return {}, None, source
    pending: list[tuple[str, ast.AST]] = []
    for statement in tree.body:
        if isinstance(statement, ast.Assign) and len(statement.targets) == 1:
            target = statement.targets[0]
            if isinstance(target, ast.Name):
                pending.append((target.id, statement.value))
        elif isinstance(statement, ast.AnnAssign) and isinstance(
            statement.target, ast.Name
        ) and statement.value is not None:
            pending.append((statement.target.id, statement.value))
    values: dict[str, object] = {}
    while pending:
        next_pending: list[tuple[str, ast.AST]] = []
        progressed = False
        for name, node in pending:
            try:
                values[name] = _static_value(node, values)
            except StaticValueUnavailable:
                next_pending.append((name, node))
            else:
                progressed = True
        if not progressed:
            break
        pending = next_pending
    return values, tree, source


def _load_json(path: Path, code: str, failures: list[str]) -> dict[str, object] | None:
    try:
        raw = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        failures.append(f"{code}.read:{type(exc).__name__}")
        return None
    try:
        value = json.loads(raw, object_pairs_hook=_reject_duplicate_keys)
    except (json.JSONDecodeError, DuplicateJSONKeyError) as exc:
        failures.append(f"{code}.json:{type(exc).__name__}")
        return None
    if not isinstance(value, dict):
        failures.append(f"{code}.root_type")
        return None
    return value


def _valid_relative_pattern(value: object) -> bool:
    if (
        not isinstance(value, str)
        or not value
        or "\\" in value
        or any(ord(character) < 32 or ord(character) == 127 for character in value)
    ):
        return False
    path = PurePosixPath(value)
    return (
        not path.is_absolute()
        and str(path) == value
        and all(part not in {"", ".", ".."} for part in path.parts)
    )


def _valid_relative_path(value: object) -> bool:
    return _valid_relative_pattern(value) and not any(
        character in value for character in "*?["
    )


def _valid_relative_glob(value: object) -> bool:
    return _valid_relative_pattern(value) and any(
        character in value for character in "*?["
    )


def _validate_unique_string_list(
    value: object,
    code: str,
    failures: list[str],
    *,
    require_paths: bool = True,
    allow_globs: bool = False,
) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        failures.append(f"{code}.type")
        return ()
    items = tuple(value)
    if len(set(items)) != len(items):
        failures.append(f"{code}.duplicate")
    if require_paths:
        validator = _valid_relative_pattern if allow_globs else _valid_relative_path
        if any(not validator(item) for item in items):
            failures.append(f"{code}.path")
    return items


def _validate_unique_glob_list(
    value: object,
    code: str,
    failures: list[str],
) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        failures.append(f"{code}.type")
        return ()
    items = tuple(value)
    if len(set(items)) != len(items):
        failures.append(f"{code}.duplicate")
    if any(not _valid_relative_glob(item) for item in items):
        failures.append(f"{code}.path")
    return items


def _validate_document_entries(
    value: object,
    code: str,
    failures: list[str],
    *,
    allow_globs: bool = False,
) -> tuple[dict[str, object], ...]:
    if not isinstance(value, list):
        failures.append(f"{code}.type")
        return ()
    entries: list[dict[str, object]] = []
    paths: list[str] = []
    for index, entry in enumerate(value):
        item_code = f"{code}[{index}]"
        if not isinstance(entry, dict):
            failures.append(f"{item_code}.type")
            continue
        if tuple(entry) != CURRENT_DOCUMENT_ENTRY_KEYS:
            failures.append(f"{item_code}.shape")
            continue
        path = entry.get("path")
        validator = _valid_relative_pattern if allow_globs else _valid_relative_path
        if not validator(path):
            failures.append(f"{item_code}.path")
        else:
            paths.append(path)
        if not isinstance(entry.get("status"), str) or not entry.get("status"):
            failures.append(f"{item_code}.status")
        if type(entry.get("current_authority")) is not bool:
            failures.append(f"{item_code}.current_authority")
        if not isinstance(entry.get("authority_scope"), str) or not entry.get(
            "authority_scope"
        ):
            failures.append(f"{item_code}.authority_scope")
        if type(entry.get("may_override_architecture_lock")) is not bool:
            failures.append(f"{item_code}.may_override_architecture_lock")
        if type(entry.get("onboarding_allowed")) is not bool:
            failures.append(f"{item_code}.onboarding_allowed")
        if not isinstance(entry.get("role"), str) or not entry.get("role"):
            failures.append(f"{item_code}.role")
        entries.append(entry)
    if len(set(paths)) != len(paths):
        failures.append(f"{code}.duplicate_path")
    return tuple(entries)


def _validate_historical_entries(
    value: object,
    failures: list[str],
) -> tuple[dict[str, object], ...]:
    code = "authority_index.historical_documents"
    if not isinstance(value, list):
        failures.append(f"{code}.type")
        return ()
    entries: list[dict[str, object]] = []
    paths: list[str] = []
    for index, entry in enumerate(value):
        item_code = f"{code}[{index}]"
        if not isinstance(entry, dict):
            failures.append(f"{item_code}.type")
            continue
        if tuple(entry) != HISTORICAL_ENTRY_KEYS:
            failures.append(f"{item_code}.shape")
            continue
        path = entry.get("path")
        if not _valid_relative_path(path):
            failures.append(f"{item_code}.path")
            continue
        paths.append(path)
        if entry.get("status") != "historical_reference":
            failures.append(f"historical.status:{path}")
        if entry.get("historical_git_ref") != f"{BASE_HEAD}:{path}":
            failures.append(f"historical.git_ref:{path}")
        if entry.get("current_authority") is not False:
            failures.append(f"historical.current_authority:{path}")
        if entry.get("onboarding_allowed") is not False:
            failures.append(f"historical.onboarding_allowed:{path}")
        if entry.get("preservation") != "byte history in Git":
            failures.append(f"historical.preservation:{path}")
        replacement = entry.get("current_replacement")
        if replacement is not None and not _valid_relative_path(replacement):
            failures.append(f"historical.current_replacement:{path}")
        entries.append(entry)
    if len(set(paths)) != len(paths):
        failures.append(f"{code}.duplicate_path")
    missing = sorted(set(REQUIRED_HISTORICAL_PATHS) - set(paths))
    for path in missing:
        failures.append(f"historical.missing:{path}")
    return tuple(entries)


def _validate_authority_index(
    value: dict[str, object] | None,
    failures: list[str],
) -> tuple[dict[str, object], ...]:
    if value is None:
        return ()
    if tuple(value) != AUTHORITY_INDEX_KEYS:
        failures.append("authority_index.top_level_shape")
    if not isinstance(value.get("schema_version"), str) or not value.get("schema_version"):
        failures.append("authority_index.schema_version")
    if value.get("generated_for_head") != BASE_HEAD:
        failures.append("authority_index.generated_for_head")

    category_entries: dict[str, tuple[dict[str, object], ...]] = {}
    current_entries: list[dict[str, object]] = []
    for key in (
        "current_normative_documents",
        "current_operational_documents",
        "current_technical_annexes",
        "future_reference_documents",
        "audit_only_sources",
    ):
        entries = _validate_document_entries(
            value.get(key),
            f"authority_index.{key}",
            failures,
            allow_globs=key == "audit_only_sources",
        )
        category_entries[key] = entries
        current_entries.extend(entries)
    historical_entries = _validate_historical_entries(
        value.get("historical_documents"), failures
    )
    excluded = _validate_unique_string_list(
        value.get("excluded_from_successor_onboarding"),
        "authority_index.excluded_from_successor_onboarding",
        failures,
        allow_globs=True,
    )
    source_order = _validate_unique_string_list(
        value.get("source_of_truth_order"),
        "authority_index.source_of_truth_order",
        failures,
        require_paths=False,
    )
    notes = _validate_unique_string_list(
        value.get("notes"),
        "authority_index.notes",
        failures,
        require_paths=False,
    )
    if not notes:
        failures.append("authority_index.notes.empty")
    if REQUIRED_GATE_SCOPE_NOTE not in notes:
        failures.append("authority_index.notes.missing_gate_scope_law")
    if not source_order or source_order[0] != LOCK_PATH:
        failures.append("authority_index.source_of_truth_order.first")

    for category, required_entries in REQUIRED_CURRENT_CLASSIFICATIONS.items():
        entries_by_path = {
            entry.get("path"): entry
            for entry in category_entries.get(category, ())
            if isinstance(entry.get("path"), str)
        }
        for path in sorted(set(entries_by_path) - set(required_entries)):
            failures.append(f"authority_index.{category}.unexpected:{path}")
        for path, expected in required_entries.items():
            entry = entries_by_path.get(path)
            if entry is None:
                failures.append(f"authority_index.{category}.missing:{path}")
                continue
            (
                expected_status,
                expected_authority,
                expected_onboarding,
                expected_scope,
                expected_override,
            ) = expected
            if entry.get("status") != expected_status:
                failures.append(f"authority_index.{category}.status:{path}")
            if entry.get("current_authority") is not expected_authority:
                failures.append(f"authority_index.{category}.authority:{path}")
            if entry.get("onboarding_allowed") is not expected_onboarding:
                failures.append(f"authority_index.{category}.onboarding:{path}")
            if entry.get("authority_scope") != expected_scope:
                failures.append(f"authority_index.{category}.scope:{path}")
            if entry.get("may_override_architecture_lock") is not expected_override:
                failures.append(f"authority_index.{category}.override:{path}")

    for category, entries in category_entries.items():
        for entry in entries:
            path = entry.get("path")
            authority_scope = entry.get("authority_scope")
            current_authority = entry.get("current_authority")
            may_override = entry.get("may_override_architecture_lock")
            if authority_scope not in KNOWN_AUTHORITY_SCOPES:
                failures.append(f"authority_index.unknown_authority_scope:{path}")
            if may_override is not False:
                failures.append(
                    f"authority_index.may_override_architecture_lock:{path}"
                )
            if authority_scope == GLOBAL_ARCHITECTURE_SCOPE and path != LOCK_PATH:
                failures.append(f"authority_index.global_scope_not_lock:{path}")
            if (
                current_authority is True
                and path != LOCK_PATH
                and authority_scope not in BOUNDED_AUTHORITATIVE_SCOPES
            ):
                failures.append(
                    f"authority_index.current_authority_unbounded_scope:{path}"
                )
            if category == "current_normative_documents" and (
                path != LOCK_PATH or authority_scope != GLOBAL_ARCHITECTURE_SCOPE
            ):
                failures.append(f"authority_index.normative_scope:{path}")
            if category == "current_technical_annexes":
                if current_authority is True and authority_scope != NAMED_GATE_SCOPE:
                    failures.append(f"authority_index.gate_annex.scope:{path}")
                if (
                    current_authority is False
                    and authority_scope != STATUS_EVIDENCE_SCOPE
                ):
                    failures.append(f"authority_index.status_evidence.scope:{path}")
            if category == "audit_only_sources":
                is_wildcard = isinstance(path, str) and any(
                    character in path for character in "*?["
                )
                expected_audit_scope = (
                    AUDIT_EVIDENCE_SCOPE if is_wildcard else STATUS_EVIDENCE_SCOPE
                )
                if authority_scope != expected_audit_scope:
                    failures.append(f"authority_index.audit.scope:{path}")
            if category == "future_reference_documents":
                if current_authority is not False:
                    failures.append(f"future_reference.current_authority:{path}")
                if authority_scope != FUTURE_REFERENCE_SCOPE:
                    failures.append(f"future_reference.authority_scope:{path}")
                if entry.get("onboarding_allowed") is not False:
                    failures.append(f"future_reference.onboarding_allowed:{path}")

    manifest_entries = {
        entry.get("path"): entry
        for entry in category_entries.get("current_operational_documents", ())
        if isinstance(entry.get("path"), str)
    }
    manifest_entry = manifest_entries.get(MANIFEST_PATH)
    if manifest_entry is None or manifest_entry.get("current_authority") is not False:
        failures.append("authority_index.successor_manifest_has_authority")

    for entry in category_entries.get("current_normative_documents", ()):
        path = entry.get("path")
        if entry.get("current_authority") is not True:
            failures.append(f"authority_index.normative_without_authority:{path}")
        if entry.get("onboarding_allowed") is not True:
            failures.append(f"authority_index.normative_not_onboarded:{path}")
    for category in ("current_operational_documents", "current_technical_annexes"):
        for entry in category_entries.get(category, ()):
            if entry.get("onboarding_allowed") is not True:
                failures.append(
                    f"authority_index.current_not_onboarded:{entry.get('path')}"
                )
    for entry in category_entries.get("audit_only_sources", ()):
        if entry.get("current_authority") is not False:
            failures.append(f"authority_index.audit_has_authority:{entry.get('path')}")
    for entry in category_entries.get("future_reference_documents", ()):
        path = entry.get("path")
        if entry.get("may_override_architecture_lock") is not False:
            failures.append(f"future_reference.may_override_architecture_lock:{path}")
        if path == FUTURE_REFERENCE_PATH and entry.get("role") != FUTURE_REFERENCE_ROLE:
            failures.append(f"future_reference.role:{path}")

    categories_by_path: dict[str, list[str]] = {}
    for category, entries in category_entries.items():
        for entry in entries:
            path = entry.get("path")
            if isinstance(path, str):
                categories_by_path.setdefault(path, []).append(category)
    for path, categories in sorted(categories_by_path.items()):
        if len(categories) > 1:
            failures.append(f"authority_index.cross_category_duplicate:{path}")

    current_paths = {
        entry.get("path")
        for entry in current_entries
        if isinstance(entry.get("path"), str)
    }
    historical_paths = {
        entry.get("path")
        for entry in historical_entries
        if isinstance(entry.get("path"), str)
    }
    all_historical_paths = set(REQUIRED_HISTORICAL_PATHS) | historical_paths
    for path in sorted(all_historical_paths):
        if any(path in source for source in source_order):
            failures.append(f"historical.in_source_of_truth_order:{path}")
    for path in sorted(historical_paths & current_paths):
        failures.append(f"historical.listed_as_current:{path}")
    for path in historical_paths:
        if path not in excluded:
            failures.append(f"historical.not_index_excluded:{path}")
    if FUTURE_REFERENCE_PATH not in excluded:
        failures.append("future_reference.index_exclusion_missing")
    future_paths = {
        entry.get("path")
        for entry in category_entries.get("future_reference_documents", ())
        if isinstance(entry.get("path"), str)
    }
    for path in sorted(future_paths):
        if any(path in source for source in source_order):
            failures.append(f"future_reference.in_source_of_truth_order:{path}")
        if path not in excluded:
            failures.append(f"future_reference.not_index_excluded:{path}")
    return historical_entries


def _validate_manifest(
    value: dict[str, object] | None,
    failures: list[str],
    historical_paths: Iterable[str],
) -> tuple[str, ...]:
    if value is None:
        return ()
    if tuple(value) != MANIFEST_KEYS:
        failures.append("successor_manifest.top_level_shape")
    if not isinstance(value.get("schema_version"), str) or not value.get("schema_version"):
        failures.append("successor_manifest.schema_version")
    if value.get("base_head") != BASE_HEAD:
        failures.append("successor_manifest.base_head")
    if value.get("manifest_status") != REQUIRED_MANIFEST_STATUS:
        failures.append("successor_manifest.manifest_status")
    if value.get("onboarding_ready") is not True:
        failures.append("successor_manifest.onboarding_ready")
    blocking_repairs = _validate_unique_string_list(
        value.get("blocking_repairs"),
        "successor_manifest.blocking_repairs",
        failures,
        require_paths=False,
    )
    if blocking_repairs != REQUIRED_BLOCKING_REPAIRS:
        failures.append("successor_manifest.blocking_repairs.exact")
    if value.get("onboarding_ready") is True and blocking_repairs:
        failures.append("successor_manifest.ready_with_blocking_repairs")
    if value.get("onboarding_ready") is False and not blocking_repairs:
        failures.append("successor_manifest.not_ready_without_blocking_repairs")
    for key in ("purpose", "historical_access_method", "validation_command"):
        if not isinstance(value.get(key), str) or not value.get(key):
            failures.append(f"successor_manifest.{key}")
    purpose = value.get("purpose")
    if isinstance(purpose, str):
        for required_phrase in (
            "S3 active-schema and retired-subsystem isolation",
            "guarded reintegration",
            "exact frozen-E5 hash verification",
        ):
            if required_phrase not in purpose:
                failures.append(
                    "successor_manifest.purpose.ready_scope:"
                    f"{required_phrase.replace(' ', '_')}"
                )
    if value.get("validation_command") != (
        "python3 tools/check_active_architecture_authority_v01.py"
    ):
        failures.append("successor_manifest.validation_command.exact")

    path_lists: dict[str, tuple[str, ...]] = {}
    for key in (
        "always_include",
        "include_current_gate_sources",
        "include_current_gate_tests",
        "include_current_release_sources",
        "exclude_paths",
        "authority_documents",
    ):
        path_lists[key] = _validate_unique_string_list(
            value.get(key), f"successor_manifest.{key}", failures
        )
    exclude_globs = _validate_unique_glob_list(
        value.get("exclude_globs"),
        "successor_manifest.exclude_globs",
        failures,
    )

    required_sets = (
        ("always_include", REQUIRED_ALWAYS_INCLUDE),
        ("include_current_gate_sources", REQUIRED_GATE_SOURCES),
        ("include_current_gate_tests", REQUIRED_GATE_TESTS),
        ("include_current_release_sources", REQUIRED_RELEASE_SOURCES),
    )
    for key, required in required_sets:
        missing = sorted(required - set(path_lists.get(key, ())))
        for path in missing:
            failures.append(f"successor_manifest.{key}.missing:{path}")

    authority_documents = path_lists.get("authority_documents", ())
    if not authority_documents or authority_documents[0] != LOCK_PATH:
        failures.append("successor_manifest.authority_documents.first")
    required_authority_documents = {
        LOCK_PATH,
        INDEX_PATH,
        MANIFEST_PATH,
        "AGENTS.md",
        "README.md",
    }
    for path in sorted(required_authority_documents - set(authority_documents)):
        failures.append(f"successor_manifest.authority_documents.missing:{path}")

    deferred_value = value.get("deferred_e5_transplant")
    deferred_paths: list[str] = []
    if not isinstance(deferred_value, list):
        failures.append("successor_manifest.deferred_e5_transplant.type")
    else:
        for index, entry in enumerate(deferred_value):
            code = f"successor_manifest.deferred_e5_transplant[{index}]"
            if not isinstance(entry, dict):
                failures.append(f"{code}.type")
                continue
            if tuple(entry) != DEFERRED_ENTRY_KEYS:
                failures.append(f"{code}.shape")
                continue
            path = entry.get("path")
            if not _valid_relative_path(path):
                failures.append(f"{code}.path")
                continue
            deferred_paths.append(path)
            if entry.get("status") != "DEFERRED_UNTIL_BYTE_EXACT_TRANSPLANT":
                failures.append(f"{code}.status")
        if len(set(deferred_paths)) != len(deferred_paths):
            failures.append("successor_manifest.deferred_e5_transplant.duplicate")
    if set(deferred_paths) != set(REQUIRED_DEFERRED_E5_PATHS):
        failures.append("successor_manifest.deferred_e5_transplant.paths")

    onboarding_paths: set[str] = set()
    for key in (
        "always_include",
        "include_current_gate_sources",
        "include_current_gate_tests",
        "include_current_release_sources",
        "authority_documents",
    ):
        onboarding_paths.update(path_lists.get(key, ()))

    exclude_paths = set(path_lists.get("exclude_paths", ()))
    for path in sorted(REQUIRED_RETIRED_EXCLUDE_PATHS - exclude_paths):
        failures.append(f"successor_manifest.exclude_paths.missing_retired:{path}")
    for path in (*RETIRED_SCHEMA_PATHS, *RETIRED_RUNTIME_MODULE_PATHS, *HISTORICAL_ALL_LAYERS_PATHS):
        if path not in exclude_paths:
            failures.append(f"successor_manifest.exclude_paths.missing_s3:{path}")
    for pattern in sorted(REQUIRED_EXCLUDE_GLOBS - set(exclude_globs)):
        failures.append(f"successor_manifest.exclude_globs.missing_retired:{pattern}")

    for path in sorted(onboarding_paths & exclude_paths):
        failures.append(f"successor_manifest.exclusion_conflict_path:{path}")
    for path in sorted(onboarding_paths):
        for pattern in exclude_globs:
            if fnmatch.fnmatchcase(path, pattern):
                failures.append(
                    f"successor_manifest.exclusion_conflict_glob:{path}:{pattern}"
                )

    all_historical_paths = set(REQUIRED_HISTORICAL_PATHS) | set(historical_paths)
    for path in sorted(all_historical_paths):
        if path in onboarding_paths:
            failures.append(f"historical.in_successor_context:{path}")
        if path not in exclude_paths:
            failures.append(f"historical.not_manifest_excluded:{path}")
    return tuple(sorted(onboarding_paths))


def _validate_retired_records(
    value: object,
    code: str,
    expected_paths: Iterable[str],
    expected_classification: str,
    failures: list[str],
) -> tuple[str, ...]:
    if not isinstance(value, list):
        failures.append(f"{code}.type")
        return ()
    paths: list[str] = []
    for index, record in enumerate(value):
        item_code = f"{code}[{index}]"
        if not isinstance(record, dict):
            failures.append(f"{item_code}.type")
            continue
        if tuple(record) != RETIRED_RECORD_KEYS:
            failures.append(f"{item_code}.shape")
            continue
        path = record.get("path")
        if not _valid_relative_path(path):
            failures.append(f"{item_code}.path")
            continue
        paths.append(path)
        if record.get("classification") != expected_classification:
            failures.append(f"{code}.classification:{path}")
        for field in (
            "current_runtime_allowed",
            "current_schema_registration_allowed",
            "current_export_allowed",
            "successor_onboarding_allowed",
        ):
            if record.get(field) is not False:
                failures.append(f"{code}.{field}:{path}")
        if record.get("preservation") != "BYTE_HISTORY_IN_GIT":
            failures.append(f"{code}.preservation:{path}")
        if not isinstance(record.get("reason"), str) or not record.get("reason"):
            failures.append(f"{code}.reason:{path}")
    if len(paths) != len(set(paths)):
        failures.append(f"{code}.duplicate_path")
    if set(paths) != set(expected_paths):
        failures.append(f"{code}.paths_exact")
    return tuple(paths)


def _validate_s3_inventory(
    repo_root: Path,
    value: dict[str, object] | None,
    failures: list[str],
) -> tuple[str, ...]:
    if value is None:
        return ()
    if tuple(value) != RETIRED_INVENTORY_KEYS:
        failures.append("s3.retired_inventory.top_level_shape")
    exact_scalars = {
        "inventory_id": "retired_architecture_inventory_v01",
        "inventory_status": "S3_CURRENT_ISOLATION_BASELINE",
        "architecture_lock_ref": LOCK_PATH,
        "generated_from_head": S3_GENERATED_FROM_HEAD,
    }
    for key, expected in exact_scalars.items():
        if value.get(key) != expected:
            failures.append(f"s3.retired_inventory.{key}")
    schema_paths = _validate_retired_records(
        value.get("retired_schema_paths"),
        "s3.retired_inventory.retired_schema_paths",
        RETIRED_SCHEMA_PATHS,
        "RETIRED_SCHEMA_REFERENCE",
        failures,
    )
    runtime_paths = _validate_retired_records(
        value.get("retired_runtime_reference_paths"),
        "s3.retired_inventory.retired_runtime_reference_paths",
        RETIRED_RUNTIME_MODULE_PATHS,
        "RETIRED_RUNTIME_REFERENCE",
        failures,
    )
    family_paths = _validate_retired_records(
        value.get("historical_demo_test_families"),
        "s3.retired_inventory.historical_demo_test_families",
        HISTORICAL_ALL_LAYERS_PATHS,
        "HISTORICAL_DEMO_OR_TEST",
        failures,
    )
    forbidden_uses = _validate_unique_string_list(
        value.get("forbidden_current_uses"),
        "s3.retired_inventory.forbidden_current_uses",
        failures,
        require_paths=False,
    )
    required_uses = {
        "IMPORT_FROM_CURRENT_KERNEL_GATE_OR_E5",
        "EXPORT_FROM_CURRENT_PACKAGE_FACADE",
        "REGISTER_AS_CURRENT_SCHEMA",
        "INCLUDE_IN_SUCCESSOR_ONBOARDING",
        "INVOKE_FROM_CURRENT_LIVING_GAUNTLET_OR_KERNEL_CONFORMANCE",
        "WRAP_ALIAS_MIGRATE_OR_REVIVE",
    }
    if set(forbidden_uses) != required_uses:
        failures.append("s3.retired_inventory.forbidden_current_uses.exact")
    for key in ("preservation_law", "onboarding_law"):
        if not isinstance(value.get(key), str) or not value.get(key):
            failures.append(f"s3.retired_inventory.{key}")
    all_paths = (*schema_paths, *runtime_paths, *family_paths)
    for relative_path in all_paths:
        if not (repo_root / relative_path).is_file():
            failures.append(f"s3.retired_inventory.preserved_path_missing:{relative_path}")
    return tuple(all_paths)


def _validate_current_schema_surface(
    repo_root: Path,
    value: dict[str, object] | None,
    failures: list[str],
) -> tuple[str, ...]:
    if value is None:
        return ()
    if tuple(value) != CURRENT_SCHEMA_SURFACE_KEYS:
        failures.append("s3.current_schema_surface.top_level_shape")
    exact_scalars = {
        "schema_surface_id": "current_schema_surface_v01",
        "schema_surface_status": "CURRENT_SCHEMA_SURFACE_ISOLATED",
        "generated_from_head": S3_GENERATED_FROM_HEAD,
    }
    for key, expected in exact_scalars.items():
        if value.get(key) != expected:
            failures.append(f"s3.current_schema_surface.{key}")
    current_paths = _validate_unique_string_list(
        value.get("current_schema_paths"),
        "s3.current_schema_surface.current_schema_paths",
        failures,
    )
    retired_paths = _validate_unique_string_list(
        value.get("retired_schema_paths"),
        "s3.current_schema_surface.retired_schema_paths",
        failures,
    )
    if tuple(current_paths) != CURRENT_SCHEMA_PATHS:
        failures.append("s3.current_schema_surface.current_schema_paths.exact")
    if tuple(retired_paths) != RETIRED_SCHEMA_PATHS:
        failures.append("s3.current_schema_surface.retired_schema_paths.exact")
    for retired_path in RETIRED_SCHEMA_PATHS:
        if retired_path in current_paths:
            failures.append(
                f"s3.current_schema_surface.retired_schema_current:{retired_path}"
            )
    for relative_path in (*current_paths, *retired_paths):
        if not (repo_root / relative_path).is_file():
            failures.append(f"s3.current_schema_surface.schema_missing:{relative_path}")

    loader_value = value.get("current_loader_or_registry_refs")
    loader_paths: list[str] = []
    registered_schemas: set[str] = set()
    if not isinstance(loader_value, list):
        failures.append("s3.current_schema_surface.current_loader_or_registry_refs.type")
    else:
        for index, record in enumerate(loader_value):
            code = f"s3.current_schema_surface.current_loader_or_registry_refs[{index}]"
            if not isinstance(record, dict):
                failures.append(f"{code}.type")
                continue
            if tuple(record) != SCHEMA_LOADER_REF_KEYS:
                failures.append(f"{code}.shape")
                continue
            source_path = record.get("source_path")
            if not _valid_relative_path(source_path):
                failures.append(f"{code}.source_path")
                continue
            loader_paths.append(source_path)
            schema_paths = _validate_unique_string_list(
                record.get("schema_paths"), f"{code}.schema_paths", failures
            )
            registered_schemas.update(schema_paths)
            for schema_path in schema_paths:
                if schema_path not in CURRENT_SCHEMA_PATHS:
                    failures.append(f"{code}.non_current_schema:{schema_path}")
            if not isinstance(record.get("role"), str) or not record.get("role"):
                failures.append(f"{code}.role")
    if len(loader_paths) != len(set(loader_paths)):
        failures.append("s3.current_schema_surface.loader_duplicate")
    if registered_schemas != set(CURRENT_SCHEMA_PATHS):
        failures.append("s3.current_schema_surface.loader_coverage")

    invariants = _validate_unique_string_list(
        value.get("isolation_invariants"),
        "s3.current_schema_surface.isolation_invariants",
        failures,
        require_paths=False,
    )
    if tuple(invariants) != REQUIRED_SCHEMA_ISOLATION_INVARIANTS:
        failures.append("s3.current_schema_surface.isolation_invariants.exact")

    retired_names = {
        PurePosixPath(path).name for path in RETIRED_SCHEMA_PATHS
    } | set(RETIRED_SCHEMA_PATHS)
    for source_path in loader_paths:
        try:
            source = (repo_root / source_path).read_text(encoding="utf-8")
            tree = ast.parse(source, filename=source_path)
        except (OSError, UnicodeError, SyntaxError) as exc:
            failures.append(
                f"s3.current_schema_surface.loader_read:{source_path}:"
                f"{type(exc).__name__}"
            )
            continue
        literals = {
            node.value
            for node in ast.walk(tree)
            if isinstance(node, ast.Constant) and isinstance(node.value, str)
        }
        for retired_name in sorted(retired_names & literals):
            failures.append(
                f"s3.current_schema_surface.retired_registration:"
                f"{source_path}:{retired_name}"
            )
    return tuple(loader_paths)


def _validate_release_succession(
    completion: dict[str, object] | None,
    seam_index: dict[str, object] | None,
    failures: list[str],
) -> None:
    if completion is not None:
        if completion.get("current_kernel_conformance_profile") != CURRENT_PROFILE_ID:
            failures.append("s3.release.completion.current_profile")
        profiles = completion.get("kernel_conformance_profiles")
        if not isinstance(profiles, dict) or tuple(profiles) != (
            "historical_v0_5",
            "current_v0_6",
        ):
            failures.append("s3.release.completion.profile_shape")
            profiles = {}
        historical = profiles.get("historical_v0_5")
        current = profiles.get("current_v0_6")
        expected_historical = {
            "profile_id": HISTORICAL_PROFILE_ID,
            "profile_version": "v0.5",
            "profile_status": "HISTORICAL_EVIDENCE_ONLY",
            "default_current": False,
            "active_gauntlet_refs": list(HISTORICAL_V05_ACTIVE_REFS),
            "historical_act_id": _HISTORICAL_ACT_ID,
        }
        expected_current = {
            "profile_id": CURRENT_PROFILE_ID,
            "profile_version": "v0.6",
            "profile_status": "CURRENT_ACTIVE",
            "default_current": True,
            "active_gauntlet_refs": list(CURRENT_V06_ACTIVE_REFS),
            "historical_profile_ref": HISTORICAL_PROFILE_ID,
            "historical_act_id_rebound": False,
        }
        if historical != expected_historical:
            failures.append("s3.release.completion.historical_profile_exact")
        if current != expected_current:
            failures.append("s3.release.completion.current_profile_exact")
        expected_claims = {
            claim: list(act_ids)
            for claim, act_ids in CURRENT_REGRESSION_CLAIM_TO_ACTS
        }
        if completion.get("current_regression_claim_mapping") != expected_claims:
            failures.append("s3.release.completion.claim_mapping_exact")

        active_acts = completion.get("active_runtime_acts")
        if not isinstance(active_acts, list):
            failures.append("s3.release.completion.active_runtime_acts.type")
            active_acts = []
        for record in active_acts:
            if isinstance(record, dict) and record.get("act_id") == _HISTORICAL_ACT_ID:
                failures.append("s3.release.completion.historical_act_current")
        evidence = completion.get("evidence_only_references")
        if not isinstance(evidence, list):
            failures.append("s3.release.completion.evidence_only_references.type")
            evidence = []
        historical_records = [
            record
            for record in evidence
            if isinstance(record, dict) and record.get("act_id") == _HISTORICAL_ACT_ID
        ]
        if len(historical_records) != 1:
            failures.append("s3.release.completion.historical_evidence_record")
        else:
            record = historical_records[0]
            required_values = {
                "source_module": _HISTORICAL_RUNNER_MODULE,
                "source_symbol": _HISTORICAL_RUNNER_SYMBOL,
                "historical_profile_ref": HISTORICAL_PROFILE_ID,
                "current_execution_enabled": False,
                "successor_onboarding_allowed": False,
                "status": "HISTORICAL_EVIDENCE_ONLY",
            }
            for key, expected in required_values.items():
                if record.get(key) != expected:
                    failures.append(
                        f"s3.release.completion.historical_evidence:{key}"
                    )

    if seam_index is not None:
        if seam_index.get("current_kernel_conformance_profile") != CURRENT_PROFILE_ID:
            failures.append("s3.release.seam_index.current_profile")
        if seam_index.get("historical_kernel_conformance_profile") != (
            HISTORICAL_PROFILE_ID
        ):
            failures.append("s3.release.seam_index.historical_profile")
        seams = seam_index.get("seams")
        if not isinstance(seams, list):
            failures.append("s3.release.seam_index.seams.type")
            seams = []
        historical_seams = [
            seam
            for seam in seams
            if isinstance(seam, dict)
            and seam.get("source_module") == _HISTORICAL_RUNNER_MODULE
        ]
        if len(historical_seams) != 1:
            failures.append("s3.release.seam_index.historical_seam")
        else:
            seam = historical_seams[0]
            required_values = {
                "current_mode": "HISTORICAL_PROFILE_METADATA_ONLY",
                "gate1_target": HISTORICAL_PROFILE_ID,
                "source_symbol": _HISTORICAL_RUNNER_SYMBOL,
                "status": "HISTORICAL_EVIDENCE_ONLY",
            }
            for key, expected in required_values.items():
                if seam.get(key) != expected:
                    failures.append(f"s3.release.seam_index.historical_seam:{key}")


def _class_fields(tree: ast.Module | None, class_name: str) -> tuple[str, ...]:
    if tree is None:
        return ()
    for statement in tree.body:
        if isinstance(statement, ast.ClassDef) and statement.name == class_name:
            return tuple(
                child.target.id
                for child in statement.body
                if isinstance(child, ast.AnnAssign)
                and isinstance(child.target, ast.Name)
            )
    return ()


def _assignment_is_name(
    tree: ast.Module | None,
    assignment_name: str,
    referenced_name: str,
) -> bool:
    if tree is None:
        return False
    for statement in tree.body:
        value: ast.AST | None = None
        if (
            isinstance(statement, ast.Assign)
            and len(statement.targets) == 1
            and isinstance(statement.targets[0], ast.Name)
            and statement.targets[0].id == assignment_name
        ):
            value = statement.value
        elif (
            isinstance(statement, ast.AnnAssign)
            and isinstance(statement.target, ast.Name)
            and statement.target.id == assignment_name
        ):
            value = statement.value
        if value is None:
            continue
        while isinstance(value, (ast.Tuple, ast.List)) and len(value.elts) == 1:
            value = value.elts[0]
        return isinstance(value, ast.Name) and value.id == referenced_name
    return False


def _reads_historical_pass_material(tree: ast.Module | None) -> bool:
    if tree is None:
        return False
    historical_path_markers = (
        "docs/audit_reports/",
        "docs/evidence/",
        "_audit_exports/",
        ".log",
    )
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        call_name = ""
        if isinstance(node.func, ast.Name):
            call_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            call_name = node.func.attr
        if call_name not in {"open", "read_text", "read_bytes"}:
            continue
        literals = {
            child.value
            for child in ast.walk(node)
            if isinstance(child, ast.Constant) and isinstance(child.value, str)
        }
        if any(
            marker in literal
            for literal in literals
            for marker in historical_path_markers
        ):
            return True
    return False


def _validate_conformance_profiles(repo_root: Path, failures: list[str]) -> None:
    values, tree, source = _static_assignments(
        repo_root / CONFORMANCE_SOURCE_PATH,
        "s3.kernel_conformance",
        failures,
    )
    exact_values = {
        "KERNEL_CONFORMANCE_PROFILE_V05_HISTORICAL": HISTORICAL_PROFILE_ID,
        "KERNEL_CONFORMANCE_PROFILE_V06_CURRENT": CURRENT_PROFILE_ID,
        "DEFAULT_KERNEL_CONFORMANCE_PROFILE": CURRENT_PROFILE_ID,
        "CONFORMANCE_VERSION": "v0.6",
        "_V05_HISTORICAL_ACTIVE_GAUNTLET_REFS": HISTORICAL_V05_ACTIVE_REFS,
        "_V06_CURRENT_ACTIVE_GAUNTLET_REFS": CURRENT_V06_ACTIVE_REFS,
        "_ACTIVE_GAUNTLET_REFS": CURRENT_V06_ACTIVE_REFS,
        "CURRENT_REGRESSION_CLAIM_TO_ACTS_V06": (
            CURRENT_REGRESSION_CLAIM_TO_ACTS
        ),
    }
    for name, expected in exact_values.items():
        if values.get(name) != expected:
            failures.append(f"s3.kernel_conformance.profile_exact:{name}")

    current_refs = values.get("_V06_CURRENT_ACTIVE_GAUNTLET_REFS")
    if isinstance(current_refs, tuple):
        if _HISTORICAL_ACT_ID in current_refs:
            failures.append("s3.kernel_conformance.old_act_in_current_profile")
        if len(current_refs) != len(set(current_refs)):
            failures.append("s3.kernel_conformance.current_profile_duplicate_act")
    act_sources = values.get("_ACT_SOURCES")
    if isinstance(act_sources, dict) and _HISTORICAL_ACT_ID in act_sources:
        failures.append("s3.kernel_conformance.historical_act_rebound")

    report_fields = set(_class_fields(tree, "KernelConformanceReportV01"))
    for field in (
        "profile_id",
        "historical_profile_ref",
        "claim_to_current_act",
        "current_act_count",
        "active_gauntlet_refs",
    ):
        if field not in report_fields:
            failures.append(f"s3.kernel_conformance.report_field_missing:{field}")

    if _HISTORICAL_RUNNER_MODULE in source or _HISTORICAL_RUNNER_SYMBOL in source:
        failures.append("s3.kernel_conformance.historical_runner_reference")
    if _reads_historical_pass_material(tree):
        failures.append("s3.kernel_conformance.historical_pass_consumption")

    runner_values, runner_tree, runner_source = _static_assignments(
        repo_root / KERNEL_CONFORMANCE_RUNNER_PATH,
        "s3.kernel_conformance_runner",
        failures,
    )
    if runner_values.get("RUNNER_VERSION") != "v0.6":
        failures.append("s3.kernel_conformance_runner.version")
    if not _assignment_is_name(
        runner_tree,
        "DEFAULT_KERNEL_CONFORMANCE_PROFILE",
        "KERNEL_CONFORMANCE_PROFILE_V06_CURRENT",
    ):
        failures.append("s3.kernel_conformance_runner.default_profile")
    if runner_values.get("KERNEL_CONFORMANCE_PROFILE_V05_HISTORICAL") != (
        HISTORICAL_PROFILE_ID
    ):
        failures.append("s3.kernel_conformance_runner.historical_profile")
    if runner_values.get("KERNEL_CONFORMANCE_PROFILE_V06_CURRENT") != (
        CURRENT_PROFILE_ID
    ):
        failures.append("s3.kernel_conformance_runner.current_profile")
    runner_refs = runner_values.get("_BASE_ACT_IDS")
    if runner_refs != CURRENT_V06_ACTIVE_REFS:
        failures.append("s3.kernel_conformance_runner.current_refs")
    if runner_values.get("_V05_HISTORICAL_BASE_ACT_IDS") != (
        HISTORICAL_V05_ACTIVE_REFS
    ):
        failures.append("s3.kernel_conformance_runner.historical_refs")
    runner_act_sources = runner_values.get("_ACT_SOURCES")
    if isinstance(runner_act_sources, dict) and _HISTORICAL_ACT_ID in runner_act_sources:
        failures.append("s3.kernel_conformance_runner.historical_act_rebound")
    if _reads_historical_pass_material(runner_tree):
        failures.append("s3.kernel_conformance_runner.historical_pass_consumption")

    living_values, living_tree, living_source = _static_assignments(
        repo_root / LIVING_GAUNTLET_PATH,
        "s3.living_gauntlet",
        failures,
    )
    if living_values.get("RUNNER_VERSION") != "v1.5":
        failures.append("s3.living_gauntlet.version")
    living_exact_values = {
        "KERNEL_CONFORMANCE_PROFILE_V05_HISTORICAL": HISTORICAL_PROFILE_ID,
        "KERNEL_CONFORMANCE_PROFILE_V06_CURRENT": CURRENT_PROFILE_ID,
        "DEFAULT_KERNEL_CONFORMANCE_PROFILE": CURRENT_PROFILE_ID,
        "HISTORICAL_KERNEL_CONFORMANCE_ACTIVE_REFS_V05": (
            HISTORICAL_V05_ACTIVE_REFS
        ),
        "CURRENT_KERNEL_CONFORMANCE_ACTIVE_REFS_V06": CURRENT_V06_ACTIVE_REFS,
        "CURRENT_REGRESSION_CLAIM_TO_ACTS_V06": (
            CURRENT_REGRESSION_CLAIM_TO_ACTS
        ),
    }
    for name, expected in living_exact_values.items():
        if living_values.get(name) != expected:
            failures.append(f"s3.living_gauntlet.profile_exact:{name}")
    for source_name in ("_ACTIVE_ACT_SOURCES", "_CURRENT_SEAMS"):
        source_map = living_values.get(source_name)
        if isinstance(source_map, dict) and _HISTORICAL_ACT_ID in source_map:
            failures.append(f"s3.living_gauntlet.historical_act_rebound:{source_name}")
    for executed_name in ("_EXECUTED_RUNTIME_ACT_IDS", "_EXECUTED_CONFORMANCE_ACT_IDS"):
        executed_ids = living_values.get(executed_name)
        if isinstance(executed_ids, tuple) and _HISTORICAL_ACT_ID in executed_ids:
            failures.append(
                f"s3.living_gauntlet.historical_act_executed:{executed_name}"
            )
    evidence_only_ids = living_values.get("_EVIDENCE_ONLY_ACT_IDS")
    if not isinstance(evidence_only_ids, tuple) or _HISTORICAL_ACT_ID not in (
        evidence_only_ids
    ):
        failures.append("s3.living_gauntlet.historical_evidence_identity_missing")
    if _reads_historical_pass_material(living_tree):
        failures.append("s3.living_gauntlet.historical_pass_consumption")
    living_report_fields = set(_class_fields(living_tree, "LivingGauntletReportV01"))
    # The Living report is a plain dictionary in the current runner; these keys
    # are therefore also accepted as explicit string literals in its collector.
    required_living_fields = (
        "kernel_conformance_profile",
        "historical_kernel_conformance_profile",
        "current_regression_claim_mapping",
    )
    for field in required_living_fields:
        if field not in living_report_fields and field not in living_source:
            failures.append(f"s3.living_gauntlet.report_field_missing:{field}")


def _python_module_name(relative_path: str) -> str | None:
    if not relative_path.endswith(".py"):
        return None
    parts = list(PurePosixPath(relative_path).with_suffix("").parts)
    if parts and parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts) if parts else None


def _resolve_import_from(
    source_module: str,
    source_is_package: bool,
    node: ast.ImportFrom,
) -> str:
    if node.level == 0:
        return node.module or ""
    package_parts = source_module.split(".") if source_is_package else source_module.split(".")[:-1]
    trim = node.level - 1
    if trim:
        package_parts = package_parts[:-trim] if trim <= len(package_parts) else []
    if node.module:
        package_parts.extend(node.module.split("."))
    return ".".join(package_parts)


def _imports_from_tree(
    tree: ast.Module,
    source_module: str,
    source_is_package: bool,
) -> frozenset[str]:
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            base = _resolve_import_from(source_module, source_is_package, node)
            if base:
                imported.add(base)
            for alias in node.names:
                if alias.name != "*":
                    imported.add(f"{base}.{alias.name}" if base else alias.name)
        elif isinstance(node, ast.Call):
            dynamic_loader = (
                isinstance(node.func, ast.Name) and node.func.id == "__import__"
            ) or (
                isinstance(node.func, ast.Attribute)
                and node.func.attr == "import_module"
            )
            if (
                dynamic_loader
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
            ):
                imported.add(node.args[0].value)
    return frozenset(imported)


def _build_python_import_graph(
    repo_root: Path,
    failures: list[str],
) -> tuple[dict[str, frozenset[str]], dict[str, str]]:
    graph: dict[str, frozenset[str]] = {}
    paths: dict[str, str] = {}
    for path in sorted(repo_root.rglob("*.py")):
        if ".git" in path.parts or "__pycache__" in path.parts:
            continue
        try:
            relative = path.relative_to(repo_root).as_posix()
        except ValueError:
            continue
        module = _python_module_name(relative)
        if module is None:
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative)
        except (OSError, UnicodeError, SyntaxError) as exc:
            if relative in {
                CONFORMANCE_SOURCE_PATH,
                KERNEL_CONFORMANCE_RUNNER_PATH,
                LIVING_GAUNTLET_PATH,
            }:
                failures.append(
                    f"s3.import_graph.parse:{relative}:{type(exc).__name__}"
                )
            continue
        graph[module] = _imports_from_tree(
            tree,
            module,
            path.name == "__init__.py",
        )
        paths[module] = relative
    return graph, paths


def _retired_reachable(
    seed_modules: Iterable[str],
    graph: dict[str, frozenset[str]],
) -> frozenset[str]:
    retired_modules = set(RETIRED_MODULE_NAMES) | {_HISTORICAL_RUNNER_MODULE}
    found: set[str] = set()
    pending = list(seed_modules)
    visited: set[str] = set()
    while pending:
        module = pending.pop()
        if module in visited:
            continue
        visited.add(module)
        for imported in graph.get(module, ()):
            matches = {
                retired
                for retired in retired_modules
                if imported == retired or imported.startswith(retired + ".")
            }
            found.update(matches)
            candidates = [imported]
            parts = imported.split(".")
            candidates.extend(".".join(parts[:index]) for index in range(len(parts) - 1, 0, -1))
            pending.extend(candidate for candidate in candidates if candidate in graph)
    return frozenset(found)


def _validate_current_import_graph(
    repo_root: Path,
    onboarding_paths: Iterable[str],
    failures: list[str],
) -> None:
    graph, paths_by_module = _build_python_import_graph(repo_root, failures)
    modules_by_path = {path: module for module, path in paths_by_module.items()}
    current_python = {
        path for path in onboarding_paths if path.endswith(".py")
    }
    g2_markers = (
        "g2_",
        "action_commit_packet",
        "drs_semantic_address",
        "reuse_certificate",
        "execution_mode_router",
        "fractal_runtime",
        "continuous_delta_runtime",
    )
    scope_paths = {
        "current_gate2": {
            path for path in current_python if any(marker in path for marker in g2_markers)
        },
        "living_gauntlet": {
            LIVING_GAUNTLET_PATH,
            "tests/test_living_gauntlet_v01_runner.py",
        },
        "kernel_conformance": {
            CONFORMANCE_SOURCE_PATH,
            KERNEL_CONFORMANCE_RUNNER_PATH,
            "tests/test_kernel_conformance_v01_runner.py",
        },
        "e5": set(REQUIRED_DEFERRED_E5_PATHS),
    }
    scope_paths["current_gate1"] = current_python - scope_paths["current_gate2"]
    scope_paths["current_gate1"].update(
        path
        for path in modules_by_path
        if path.startswith("hedgehog/kernel/") and path.endswith(".py")
    )
    for scope, paths in scope_paths.items():
        seeds = {
            modules_by_path[path]
            for path in paths
            if path in modules_by_path
        }
        for retired in sorted(_retired_reachable(seeds, graph)):
            failures.append(
                f"s3.import_graph.{RETIRED_IMPORT_SCOPE_LABELS[scope]}:{retired}"
            )

    facade_seeds = {
        modules_by_path[path]
        for path in ("hedgehog/__init__.py", "hedgehog/kernel/__init__.py")
        if path in modules_by_path
    }
    for retired in sorted(_retired_reachable(facade_seeds, graph)):
        failures.append(f"s3.package_facade.retired_export:{retired}")


def _validate_current_documents(repo_root: Path, failures: list[str]) -> None:
    folded_forbidden = tuple(term.casefold() for term in FORBIDDEN_DIRECT_TERMS)
    for relative_path in SCANNED_CURRENT_DOCUMENTS:
        path = repo_root / relative_path
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            failures.append(f"current_document.read:{relative_path}:{type(exc).__name__}")
            continue
        for term in REQUIRED_CURRENT_TERMS:
            if term not in text:
                failures.append(f"current_document.missing_term:{relative_path}:{term}")
        folded_text = text.casefold()
        for direct_term, folded_term in zip(FORBIDDEN_DIRECT_TERMS, folded_forbidden):
            if folded_term in folded_text:
                failures.append(
                    f"current_document.forbidden_term:{relative_path}:{direct_term}"
                )
        if relative_path == "AGENTS.md":
            section_heading = "## Bounded context and onboarding"
            if section_heading not in text:
                normalized_section = ""
            else:
                section = text.split(section_heading, 1)[1].split("\n## ", 1)[0]
                normalized_section = " ".join(section.split())
            for warning_id, required_text in REQUIRED_AGENTS_ONBOARDING_WARNINGS:
                if required_text not in normalized_section:
                    failures.append(
                        "current_document.missing_onboarding_warning:"
                        f"AGENTS.md:{warning_id}"
                    )


def _validate_s2_vocabulary(repo_root: Path, failures: list[str]) -> None:
    try:
        structured_text = (repo_root / STRUCTURED_RATIONALE_PATH).read_text(
            encoding="utf-8"
        )
    except (OSError, UnicodeError) as exc:
        failures.append(
            f"s2.structured_rationale.read:{type(exc).__name__}"
        )
    else:
        for index, retired_term in enumerate(_RETIRED_STRUCTURED_POSITIVE_TERMS):
            if retired_term in structured_text:
                failures.append(
                    f"s2.structured_rationale.retired_positive:{index}"
                )

    for relative_path in SUPPLIER_EVENT_SOURCE_PATHS:
        try:
            source_text = (repo_root / relative_path).read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            failures.append(
                f"s2.supplier_event.read:{relative_path}:{type(exc).__name__}"
            )
            continue
        if _RETIRED_SUPPLIER_EVENT in source_text:
            failures.append(f"s2.supplier_event.retired:{relative_path}")
        if _REQUIRED_SUPPLIER_EVENT not in source_text:
            failures.append(f"s2.supplier_event.current_missing:{relative_path}")


def _validate_deliverable_paths(repo_root: Path, failures: list[str]) -> None:
    for relative_path in sorted(ALLOWED_CHANGED_PATHS):
        if not (repo_root / relative_path).is_file():
            failures.append(f"deliverable.missing:{relative_path}")


def _git_changed_paths(repo_root: Path, failures: list[str]) -> set[str]:
    try:
        completed = subprocess.run(
            ("git", "status", "--porcelain=v1", "-z", "--untracked-files=all"),
            cwd=repo_root,
            check=False,
            capture_output=True,
        )
    except OSError as exc:
        failures.append(f"worktree.git_status:{type(exc).__name__}")
        return set()
    if completed.returncode != 0:
        failures.append(f"worktree.git_status:exit_{completed.returncode}")
        return set()

    fields = completed.stdout.split(b"\0")
    changed: set[str] = set()
    index = 0
    while index < len(fields):
        record = fields[index]
        index += 1
        if not record:
            continue
        if len(record) < 4 or record[2:3] != b" ":
            failures.append("worktree.git_status:malformed_record")
            continue
        status = record[:2].decode("ascii", errors="replace")
        changed.add(record[3:].decode("utf-8", errors="surrogateescape"))
        if "R" in status or "C" in status:
            if index >= len(fields) or not fields[index]:
                failures.append("worktree.git_status:missing_rename_source")
            else:
                changed.add(fields[index].decode("utf-8", errors="surrogateescape"))
                index += 1
    return changed


def _validate_changed_paths(changed_paths: Iterable[str], failures: list[str]) -> None:
    changed = set(changed_paths)
    unexpected = sorted(changed - ALLOWED_CHANGED_PATHS)
    for path in unexpected:
        failures.append(f"worktree.unexpected_changed_path:{path}")


def collect_failures(
    repo_root: Path,
) -> tuple[str, ...]:
    """Return deterministic validation failures for ``repo_root``."""

    root = repo_root.resolve()
    failures: list[str] = []
    authority_index = _load_json(root / INDEX_PATH, "authority_index", failures)
    successor_manifest = _load_json(
        root / MANIFEST_PATH, "successor_manifest", failures
    )
    retired_inventory = _load_json(
        root / RETIRED_INVENTORY_PATH, "s3.retired_inventory", failures
    )
    current_schema_surface = _load_json(
        root / CURRENT_SCHEMA_SURFACE_PATH,
        "s3.current_schema_surface",
        failures,
    )
    completion_manifest = _load_json(
        root / COMPLETION_MANIFEST_PATH, "s3.release.completion", failures
    )
    seam_index = _load_json(
        root / SEAM_INDEX_PATH, "s3.release.seam_index", failures
    )
    historical_entries = _validate_authority_index(authority_index, failures)
    historical_paths = {
        entry.get("path")
        for entry in historical_entries
        if isinstance(entry.get("path"), str)
    }
    onboarding_paths = _validate_manifest(
        successor_manifest, failures, historical_paths
    )
    _validate_s3_inventory(root, retired_inventory, failures)
    _validate_current_schema_surface(root, current_schema_surface, failures)
    _validate_release_succession(completion_manifest, seam_index, failures)
    _validate_conformance_profiles(root, failures)
    _validate_current_import_graph(root, onboarding_paths, failures)
    _validate_current_documents(root, failures)
    _validate_s2_vocabulary(root, failures)
    _validate_deliverable_paths(root, failures)
    observed_changed_paths = _git_changed_paths(root, failures)
    _validate_changed_paths(observed_changed_paths, failures)
    return tuple(sorted(set(failures)))


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check the active Hedgehog OS architecture authority boundary."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="repository root (defaults to the parent of tools/)",
    )
    return parser


def main(arguments: Sequence[str] | None = None) -> int:
    args = _build_parser().parse_args(arguments)
    failures = collect_failures(args.root)
    if not failures:
        print("ACTIVE_ARCHITECTURE_AUTHORITY_V01 PASS")
        return 0
    print("ACTIVE_ARCHITECTURE_AUTHORITY_V01 FAIL")
    for failure in failures:
        print(f"FAIL {failure}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
