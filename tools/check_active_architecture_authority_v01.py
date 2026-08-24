#!/usr/bin/env python3
"""Validate the active Hedgehog OS document/onboarding authority boundary."""

from __future__ import annotations

import argparse
import fnmatch
import json
from pathlib import Path, PurePosixPath
import subprocess
from typing import Iterable, Sequence


BASE_HEAD = "931645dc724c54d635f32dabfca4b62fbc9a39a2"
LOCK_PATH = "specs/current_architecture_lock_v01.md"
INDEX_PATH = "specs/document_authority_index_v01.json"
MANIFEST_PATH = "release/successor_context_manifest_v01.json"

ALLOWED_CHANGED_PATHS = frozenset(
    {
        "AGENTS.md",
        "README.md",
        LOCK_PATH,
        INDEX_PATH,
        MANIFEST_PATH,
        "tools/check_active_architecture_authority_v01.py",
        "tests/test_active_architecture_authority_v01.py",
    }
)

AUTHORITY_INDEX_KEYS = (
    "schema_version",
    "generated_for_head",
    "current_normative_documents",
    "current_operational_documents",
    "current_technical_annexes",
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
    }
)
REQUIRED_DEFERRED_E5_PATHS = frozenset(
    {
        "hedgehog/kernel/continuous_delta_runtime_v01.py",
        "tests/test_continuous_delta_runtime_g2_e_v01.py",
        "demo/run_continuous_delta_runtime_g2_e_v01.py",
    }
)

REQUIRED_MANIFEST_STATUS = "S1_PREPARED_PENDING_S2_S3"
REQUIRED_BLOCKING_REPAIRS = (
    "S2_STRUCTURED_RATIONALE_VOCABULARY_REPAIR",
    "S2_SUPPLIER_ADAPTER_EVENT_VOCABULARY_REPAIR",
    "S3_ACTIVE_SCHEMA_AND_LEGACY_ISOLATION",
)
REQUIRED_MANIFEST_PURPOSE = (
    "Bounded successor-context candidate prepared by S1 and blocked from permanent "
    "successor onboarding until the listed S2/S3 repairs close. Existing E1-E4 "
    "runtime/test targets are included only as accepted pre-E5 bytes; no frozen E5 "
    "candidate byte is present or authorized by this manifest."
)

GLOBAL_ARCHITECTURE_SCOPE = "current_global_architecture_law"
OPERATIONAL_SCOPE = "operational_instructions_subordinate_to_architecture_lock"
PUBLIC_VIEW_SCOPE = "public_engineering_view_only"
SUCCESSOR_CONTEXT_SCOPE = "successor_context_selection_only"
NAMED_GATE_SCOPE = "named_gate_contract_only"
STATUS_EVIDENCE_SCOPE = "status_or_evidence_only"
AUDIT_EVIDENCE_SCOPE = "audit_evidence_only"
KNOWN_AUTHORITY_SCOPES = frozenset(
    {
        GLOBAL_ARCHITECTURE_SCOPE,
        OPERATIONAL_SCOPE,
        PUBLIC_VIEW_SCOPE,
        SUCCESSOR_CONTEXT_SCOPE,
        NAMED_GATE_SCOPE,
        STATUS_EVIDENCE_SCOPE,
        AUDIT_EVIDENCE_SCOPE,
    }
)
BOUNDED_AUTHORITATIVE_SCOPES = frozenset({OPERATIONAL_SCOPE, NAMED_GATE_SCOPE})

REQUIRED_AGENTS_ONBOARDING_WARNINGS = (
    ("manifest_status", "S1_PREPARED_PENDING_S2_S3"),
    ("onboarding_ready", "its `onboarding_ready` value is `false`"),
    (
        "authorized_sanitation_only",
        "It may be used only for S1 review and authorized S2/S3 sanitation.",
    ),
    (
        "permanent_successor_blocked",
        "A permanent successor assistant must not be onboarded until a later "
        "authorized closure updates the manifest to a ready state.",
    ),
    (
        "frozen_e5_prohibited",
        "The frozen E5 transplant remains prohibited at this point.",
    ),
)
REQUIRED_GATE_SCOPE_NOTE = (
    "Named Gate authority cannot redefine global topology, Root sovereignty, "
    "BSEP, runtime ownership, or another Gate's contract."
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
            "s1_prepared_successor_context_candidate_pending_s2_s3",
            False,
            True,
            SUCCESSOR_CONTEXT_SCOPE,
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
            "frozen_gate1_evidence",
            False,
            True,
            STATUS_EVIDENCE_SCOPE,
            False,
        ),
        "release/integration_seam_index.json": (
            "frozen_gate1_evidence",
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
    }
)
REQUIRED_EXCLUDE_GLOBS = frozenset(
    {
        "docs/audit_reports/**",
        "docs/evidence/**",
        "docs/showcase/**",
        "specs/future/**",
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


class DuplicateJSONKeyError(ValueError):
    """Raised when a JSON object contains a duplicate key."""


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateJSONKeyError(f"duplicate key: {key}")
        result[key] = value
    return result


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
    if value.get("onboarding_ready") is not False:
        failures.append("successor_manifest.onboarding_ready")
    blocking_repairs = _validate_unique_string_list(
        value.get("blocking_repairs"),
        "successor_manifest.blocking_repairs",
        failures,
        require_paths=False,
    )
    if blocking_repairs != REQUIRED_BLOCKING_REPAIRS:
        failures.append("successor_manifest.blocking_repairs.exact")
    for key in ("purpose", "historical_access_method", "validation_command"):
        if not isinstance(value.get(key), str) or not value.get(key):
            failures.append(f"successor_manifest.{key}")
    if value.get("purpose") != REQUIRED_MANIFEST_PURPOSE:
        failures.append("successor_manifest.purpose.pending_scope")
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
    historical_entries = _validate_authority_index(authority_index, failures)
    historical_paths = {
        entry.get("path")
        for entry in historical_entries
        if isinstance(entry.get("path"), str)
    }
    _validate_manifest(successor_manifest, failures, historical_paths)
    _validate_current_documents(root, failures)
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
