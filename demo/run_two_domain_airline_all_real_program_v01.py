"""Prepare one bounded A1 Airline attempt over the committed canonical lane.

The injected mode is deterministic validation only. It performs no live
collection and cannot create official evidence. The real-provider mode is an
owner-terminal-only, single-attempt orchestration seam. This module does not
reimplement Airline semantics, Root law, Corridor, Ledger, or Crypto logic.
It creates no Package, Anchor, Replay, authority, permission, action, receipt,
FinalOutput, ticket, booking, payment, or real-world effect.
"""

from argparse import ArgumentParser as _ArgumentParser
from collections.abc import Callable as _Callable, Mapping as _Mapping
from dataclasses import dataclass as _dataclass
import errno as _errno
import hashlib as _hashlib
import importlib as _importlib
import json as _json
import math as _math
import os as _os
from pathlib import Path as _Path
import re as _re
import stat as _stat
import subprocess as _subprocess
import sys as _sys
import unicodedata as _unicodedata

from demo import run_tri_party_airline_live_semantic_lane_v01 as _lane
from hedgehog.domains.airline import semantic_to_contract_binding_v01 as _binding
from hedgehog.domains.airline import crypto_artifact_seal_collector_v01 as _crypto_collector
from hedgehog.domains.airline import crypto_artifact_seal_v01 as _crypto_contracts
from hedgehog.domains.airline import semantic_to_contract_causal_runtime_v01 as _causal
from hedgehog.domains.airline import transaction_artifact_ledger_collector_v01 as _ledger_collector
from hedgehog.domains.airline import transaction_artifact_ledger_v01 as _ledger
from hedgehog.domains.airline.sealed_evidence_package_adapter_v01 import (
    AirlineSafeExecutionProjectionV01,
    airline_safe_execution_projection_to_plain_dict_v01,
    build_airline_safe_execution_projection_v01,
    validate_airline_safe_execution_projection_v01,
)
from hedgehog.kernel.integrity_replay_v01 import canonical_json_bytes_v01 as _canonical_json_bytes_v01


MODULE_ID = "two_domain_airline_all_real_program_v01"
PROGRAMME_ID = "two_domain_all_real_sealed_evidence_program_v01"
PROGRAMME_VERSION = "v0.1"
GATE_ID = (
    "two_domain_all_real_sealed_evidence_program_v01_"
    "a1_attempt_02_semantic_runtime_recovery"
)
ATTEMPT_03_GATE_ID = (
    "two_domain_all_real_sealed_evidence_program_v01_"
    "a1_attempt_03_root_review_acknowledgement_recovery"
)
DOMAIN_ID = "airline"
MODEL_ID = "gemini-2.5-flash"

MODE_INJECTED = "injected_deterministic"
MODE_REAL = "real_provider"
STATUS_PASS = "PASS"
STATUS_FAIL_CLOSED = "FAIL_CLOSED"

REASON_INVALID = "a1_airline_program_invalid"
REASON_MODE_INVALID = "a1_airline_mode_invalid"
REASON_ATTEMPT_INVALID = "a1_airline_attempt_number_invalid"
REASON_PRIVATE_PATH_INVALID = "a1_airline_private_output_invalid"
REASON_PRIVATE_PATH_EXISTS = "a1_airline_private_output_exists"
REASON_REPOSITORY_NOT_READY = "a1_airline_repository_not_ready"
REASON_LOCAL_PRECONDITION_FAILED = "a1_airline_local_precondition_failed"
REASON_CANONICAL_REPORT_EXISTS = "a1_airline_canonical_safe_report_exists"
REASON_COLLECTOR_FAILED = "a1_airline_collector_failed"
REASON_SOURCE_GEOMETRY_INVALID = "a1_airline_source_geometry_invalid"
REASON_SAFE_NORMALIZATION_INVALID = "a1_airline_safe_normalization_invalid"
REASON_SECRET_SCAN_FAILED = "a1_airline_secret_scan_failed"
REASON_INVENTORY_INVALID = "a1_airline_private_inventory_invalid"
REASON_PUBLIC_WRITE_FAILED = "a1_airline_public_safe_report_write_failed"
REASON_PUBLIC_CLEANUP_FAILED = "a1_airline_public_safe_report_cleanup_failed"
REASON_PRIVATE_METADATA_FAILED = "a1_airline_private_metadata_write_failed"
REASON_PRIVATE_PRESERVATION_UNPROVED = "a1_airline_private_preservation_unproved"
REASON_UNEXPECTED = "a1_airline_unexpected_exception"
REASON_RECOVERY_INPUT_INVALID = "a1_airline_attempt_02_recovery_input_invalid"
REASON_ATTEMPT_03_RECOVERY_INPUT_INVALID = (
    "a1_airline_attempt_03_recovery_input_invalid"
)
REASON_PRIOR_ATTEMPT_INVALID = "a1_airline_prior_failed_attempt_invalid"
REASON_PRIOR_ATTEMPT_CHANGED = "a1_airline_prior_failed_attempt_changed"
REASON_ATTEMPT_02_INVALID = "a1_airline_attempt_02_predecessor_invalid"
REASON_ATTEMPT_02_CHANGED = "a1_airline_attempt_02_predecessor_changed"

ACTOR_IDS = tuple(item["actor_id"] for item in _lane.ACTOR_SPECS)
CAUSAL_ACTOR_IDS = tuple(_lane.CAUSAL_ACTOR_IDS)
BSEP_PROJECTION_NAMES = (
    "client_bsep_projection",
    "airline_bsep_projection",
    "bank_bsep_projection",
    "cross_root_bsep_projection",
)
SHARED_BSEP_PROJECTION_REFS = (
    "bsep_projection:client:001",
    "bsep_projection:airline_offer_selection:001",
    "bsep_projection:bank:001",
    "bsep_projection:cross_root:001",
)
ROOT_FINAL_GEOMETRY = (
    ("ClientRoot", _ledger.ARTIFACT_CLIENT_ROOT_FINAL),
    ("AirlineRoot", _ledger.ARTIFACT_AIRLINE_ROOT_FINAL),
    ("BankRoot", _ledger.ARTIFACT_BANK_ROOT_FINAL),
)
RECEIPT_ARTIFACT_TYPES = (
    _ledger.ARTIFACT_AIRLINE_OFFER_HOLD_RECEIPT,
    _ledger.ARTIFACT_MOCK_TICKET_RECEIPT,
    _ledger.ARTIFACT_MOCK_PURCHASE_RECEIPT,
)

ATTEMPT_IDENTITY_FILE = "attempt_identity_v01.json"
RAW_ATTEMPT_DIRECTORY = "raw_attempt"
PRIVATE_INVENTORY_FILE = "private_inventory_v01.json"
GENERATION_GATE_FILE = "generation_gate_v01.json"
_RAW_LEDGER_FILE = "airline_transaction_artifact_ledger.json"

CANONICAL_SAFE_REPORT_REF = (
    "docs/evidence/two_domain_all_real_sealed_evidence_program_v01/"
    "airline/airline_safe_execution_report_v01.json"
)
_REPOSITORY_ROOT = _Path(__file__).resolve().parents[1]
_REPOSITORY_VENV_PREFIX = _REPOSITORY_ROOT / ".venv"
_CANONICAL_SAFE_REPORT_PATH = _REPOSITORY_ROOT / CANONICAL_SAFE_REPORT_REF
_SOURCE_TASK_ID = "airline_preference_a_par_lim_live_attempt_v01"
_PACKAGE_ID = f"airline_sealed_evidence:{_lane.TRANSACTION_ID}"
_LOGICAL_PACKAGE_REF = "raw_attempt"
_LOGICAL_OUTPUT_DIRECTORY_REF = f"airline/{_lane.RUN_ID}/sealed_evidence"
_PROVIDER_APPLICATION_CALL_MODE = "json_mime_no_response_schema_single_application_call"
_PRIOR_ATTEMPT_ID = "fcce2c0224517487b59c40e79a75ea00078df393a2552f5b553780f8b7adc64a"
_PRIOR_EXECUTION_HEAD = "829496261a90249b500e7583bb407839e94cd874"
_PRIOR_ATTEMPT_IDENTITY_SHA256 = "c3af7707023402b287222615e4e1877e248e1f23ad6b238254f96d7ce19f5bd2"
_PRIOR_PRIVATE_INVENTORY_SHA256 = "33818a0230a245392b78194aad2c35966e59f91992170bef7461d5539e56693a"
_PRIOR_PRIVATE_INVENTORY_DIGEST = "567b567ba4b37a04665cdcc085f1feb1be0fd2facad3921f5fbd5b276c5a2163"
_PRIOR_GENERATION_GATE_SHA256 = "8fcdf7ef795d09178c3352999bdd3087c5e8e1b78184b6d055e29d0311991653"
_PRIOR_CALLBACK_PREFIX = (
    "tri_party_airline_orchestrator_llm",
    "tri_party_airline_semantic_architect_llm",
    "client_purchase_intent_reviewer_llm",
)
_PRIOR_ROOT_ENTRY_COUNT = 4
_PRIOR_RAW_FILE_COUNT = 23
_PRIOR_METADATA_MODE = 0o600
_ATTEMPT_02_ID = "0191a1820c22ccd2031e2f4f8816feebf42682eac8ba17a2b25644b27f34bf3e"
_ATTEMPT_02_EXECUTION_HEAD = "b0349bb4b90beb492a585aa998a6f167cb439279"
_ATTEMPT_02_IDENTITY_SHA256 = "46cd8175bd4e3ce898c426cc85b760f096857ed68bd33359ffb754d93f2dc80b"
_ATTEMPT_02_INVENTORY_SHA256 = "917d034f3440605ef9a4a4f2e32a5b4a3c28ec1a715084803b9b05674e8b1029"
_ATTEMPT_02_INVENTORY_DIGEST = "3313317b028843d9307e350b7ded9b8ae084048b998a8eaf0819605629ceb34b"
_ATTEMPT_02_GATE_SHA256 = "d49636630011553c4f9e5fc044699c2c493a6712c34aafeef22f2776d3ab186c"
_ATTEMPT_02_SUMMARY_SHA256 = "f7f1d78708ba5a9bcc71edbb548eb5edd9815fc604f654a236493b38279d90b8"
_ATTEMPT_02_VALIDATION_SHA256 = "90ca3e2bd1d51ff74cfbc5136e55ad601f323c5a46dfbb730bea03c8d9696e01"
_ATTEMPT_02_ROOT_ENTRY_COUNT = 4
_ATTEMPT_02_RAW_FILE_COUNT = 23
_ATTEMPT_02_METADATA_MODE = 0o600
_ATTEMPT_02_CALLBACK_PREFIX = ACTOR_IDS[:3]
_ATTEMPT_02_SEMANTIC_REASON = "airline_semantic_provider_value_invalid"
_PUBLICATION_ABSENT = "ABSENT"
_PUBLICATION_PRESENT = "PRESENT"
_PUBLICATION_ABSENCE_UNPROVEN = "ABSENCE_UNPROVEN"
_PRESERVATION_PRESERVED = "PRESERVED"
_PRESERVATION_RETAINED_UNPROVED = "RETAINED_UNPROVED"
_PRESERVATION_NOT_CREATED = "NOT_CREATED"
_EXTERNAL_NOT_PERFORMED = "NOT_PERFORMED"
_EXTERNAL_VERIFIED = "VERIFIED"
_EXTERNAL_UNVERIFIED_PARTIAL = "UNVERIFIED_PARTIAL"
_GIT_TIMEOUT_SECONDS = 5

_ACTOR_ARTIFACT_SUFFIXES = (
    "prompt.txt",
    "raw_response.txt",
    "extracted_json_candidate.json",
    "validation.json",
    "canonical_summary.json",
)
_RAW_FIXED_FILES = (
    "tri_party_airline_bsep_packet.json",
    "tri_party_airline_bsep_validation.json",
    "tri_party_airline_bsep_side_projections.json",
    "semantic_to_contract_causal_run.json",
    "semantic_to_contract_bridge.json",
    "integrated_deterministic_airline_summary.json",
    "airline_transaction_artifact_ledger.json",
    "secret_scan.json",
    "summary.json",
    "summary.log",
    _lane.CRYPTO_MANIFEST_FILE,
    _lane.CRYPTO_VERIFICATION_FILE,
)
EXPECTED_RAW_ATTEMPT_FILENAMES = tuple(
    sorted(
        tuple(
            f"{actor_id}_{suffix}"
            for actor_id in ACTOR_IDS
            for suffix in _ACTOR_ARTIFACT_SUFFIXES
        )
        + _RAW_FIXED_FILES
    )
)

_AIRLINE_CONTROL_ENV_KEYS = (
    _lane.ENV_LANE,
    _lane.ENV_ARTIFACT_DIR,
    _lane.ENV_MODEL,
    _lane.ENV_FAKE_PROVIDER,
    _lane.ENV_REAL_PROVIDER,
    _lane.ENV_CALL_DELAY_SECONDS,
    _lane.ENV_ALLOW_RAW,
    _lane.ENV_CAUSAL_BINDING,
    _lane.ENV_CRYPTO_ARTIFACT_SEAL,
)
_CREDENTIAL_ENV_KEYS = (
    _lane.provider_adapter.ENV_GEMINI_API_KEY,
    _lane.provider_adapter.ENV_GOOGLE_API_KEY,
    _lane.provider_adapter.ENV_GEMINI_API_KEY_FALLBACK,
    _lane.provider_adapter.ENV_GOOGLE_GEMINI_API_KEY,
)
_PROVIDER_TIMEOUT_ENV_KEY = _lane.provider_adapter.ENV_TIMEOUT_SECONDS
_FORBIDDEN_GIT_ENV_KEYS = frozenset(
    (
        "GIT_DIR",
        "GIT_WORK_TREE",
        "GIT_INDEX_FILE",
        "GIT_COMMON_DIR",
        "GIT_OBJECT_DIRECTORY",
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
        "GIT_NAMESPACE",
    )
)
_EXPECTED_ROOT_BOUNDARIES = (
    {
        "boundary": "ClientRoot remains client-side only",
        "boundary_preserved": True,
        "violation_count": 0,
    },
    {
        "boundary": "AirlineRoot remains airline-side only",
        "boundary_preserved": True,
        "violation_count": 0,
    },
    {
        "boundary": "BankRoot remains bank-side only",
        "boundary_preserved": True,
        "violation_count": 0,
    },
    {
        "boundary": "cross-root reviewer is advisory and not a fourth Root",
        "boundary_preserved": True,
        "violation_count": 0,
    },
)

_SAFE_REPORT_KEYS = frozenset(
    (
        "execution_head",
        "run_id",
        "report_id",
        "source_task_id",
        "transaction_id",
        "selected_offer_id",
        "provider_mode",
        "model_id",
        "source_final_status",
        "actors",
        "bsep",
        "root_finals",
        "corridor",
        "receipts",
        "counters",
        "raw_prompt_included",
        "raw_provider_response_included",
        "secret_scan_passed",
        "real_world_effects_count",
        "validation_errors",
    )
)
_SAFE_NEGATIVE_KEYS = {
    "raw_prompt_included": False,
    "raw_provider_response_included": False,
    "secret_scan_passed": True,
}
_FORBIDDEN_CANONICAL_KEY_TOKENS = (
    "rawprompt",
    "prompttext",
    "rawresponse",
    "providerresponse",
    "apikey",
    "privatekey",
    "secretvalue",
    "credential",
    "password",
    "passphrase",
    "accesstoken",
    "refreshtoken",
    "bearertoken",
    "authtoken",
    "clientsecret",
)
_SENSITIVE_ASSIGNMENT = _re.compile(
    r"(?i)(?:^|[^A-Za-z0-9_])(?:[A-Za-z0-9_]*(?:API_KEY|PRIVATE_KEY|"
    r"PASSWORD|PASSPHRASE|SECRET|TOKEN|CREDENTIAL)[A-Za-z0-9_]*)\s*[:=]"
)
_WINDOWS_ABSOLUTE = _re.compile(r"(?i)(?:^|[\s:=;,('\\\"])[A-Z]:[\\/]")
_POSIX_ABSOLUTE = _re.compile(r"(?:^|[\s:=;,('\\\"])/(?!/)[^\s]*")
_MEMORY_ADDRESS = _re.compile(r"(?i)(?:^|[^A-Za-z0-9])0x[0-9a-f]{6,}")
_OBJECT_REPR = _re.compile(r"<[^>\n]*\bobject at 0x[0-9a-fA-F]+>")
_LOWER_HEAD = _re.compile(r"^[0-9a-f]{7,40}$")

_OPEN = _os.open
_WRITE = _os.write
_FSYNC = _os.fsync
_CLOSE = _os.close
_RAW_CLOSE = _os.close
_FSTAT = _os.fstat
_RAW_FSTAT = _os.fstat
_UNLINK = _os.unlink
_COLLECTOR = _lane.collect_tri_party_airline_live_semantic_lane_v01
_REAL_PROVIDER_BUILDER = _lane.build_real_airline_semantic_provider_v01
_PRIVATE_DOCUMENT_POST_CLOSE_HOOK: _Callable[[int, str], None] | None = None
_POST_ATTEMPT_IDENTITY_WRITE_HOOK: _Callable[[_Path], None] | None = None
_POST_COLLECTOR_HOOK: _Callable[[_Path, object, object], None] | None = None
_POST_PUBLIC_WRITE_HOOK: _Callable[[_Path], None] | None = None
_PRE_GENERATION_GATE_HOOK: _Callable[[_Path], None] | None = None
_POST_PASS_GATE_WRITE_HOOK: _Callable[[_Path, _Path], None] | None = None
_FAILURE_PRESERVATION_HOOK: _Callable[[_Path], None] | None = None


class _CliError(Exception):
    pass


class _RunnerFailure(Exception):
    def __init__(self, reason: str, stage: str) -> None:
        super().__init__(reason)
        self.reason = reason
        self.stage = stage


class _PublicCleanupFailure(Exception):
    pass


@_dataclass(frozen=True, slots=True)
class AirlineA1ProgramResultV01:
    programme_id: str
    programme_version: str
    gate_id: str
    domain_id: str
    execution_mode: str
    execution_head: str
    attempt_number: int
    attempt_id: str
    final_status: str
    reason_code: str
    failed_stage: str
    live_collection_performed: bool
    official_evidence_eligible: bool
    private_attempt_preserved: bool
    private_attempt_preservation_state: str
    public_safe_report_state: str
    actual_external_operation_status: str
    provider_application_call_mode: str
    collector_invocation_count: int
    injected_callback_count: int
    wrapper_callback_observed_count: int
    provider_callback_started_count: int
    provider_callback_completed_count: int
    semantic_actor_call_count: int
    causal_actor_call_count: int
    generic_actor_call_count: int
    duplicate_actor_call_count: int
    safe_execution_id: str
    safe_report_sha256: str
    private_inventory_digest: str
    safe_report_written: bool
    source_provider_call_count: int
    source_network_call_count: int
    source_gemini_call_count: int
    source_real_world_effects_count: int
    actual_provider_call_count: int
    actual_network_call_count: int
    actual_gemini_call_count: int
    actual_real_world_effects_count: int
    retry_count: int
    package_created_count: int
    anchor_created_count: int
    replay_created_count: int


@_dataclass(frozen=True, slots=True)
class _InventoryRow:
    logical_ref: str
    sha256: str
    byte_count: int
    device: int
    inode: int


@_dataclass(frozen=True, slots=True)
class _InventorySnapshot:
    rows: tuple[_InventoryRow, ...]
    digest: str
    raw_directory_identity: tuple[int, int]
    raw_directory_mode: int


@_dataclass(frozen=True, slots=True)
class _OwnedOutput:
    parent_path: _Path
    parent_fd: int
    parent_identity: tuple[int, int]
    leaf: str
    identity: tuple[int, int]
    expected_bytes: bytes


@_dataclass(frozen=True, slots=True)
class _ReleasedOutput:
    parent_path: _Path
    parent_identity: tuple[int, int]
    leaf: str
    identity: tuple[int, int]
    expected_bytes: bytes


@_dataclass(frozen=True, slots=True)
class _PrivateDocumentProof:
    leaf: str
    identity: tuple[int, int]
    expected_bytes: bytes
    sha256: str
    byte_count: int


@_dataclass(frozen=True, slots=True)
class _PriorAttemptAnchors:
    attempt_id: str = _PRIOR_ATTEMPT_ID
    execution_head: str = _PRIOR_EXECUTION_HEAD
    attempt_identity_sha256: str = _PRIOR_ATTEMPT_IDENTITY_SHA256
    private_inventory_sha256: str = _PRIOR_PRIVATE_INVENTORY_SHA256
    private_inventory_digest: str = _PRIOR_PRIVATE_INVENTORY_DIGEST
    generation_gate_sha256: str = _PRIOR_GENERATION_GATE_SHA256
    root_entry_count: int = _PRIOR_ROOT_ENTRY_COUNT
    raw_file_count: int = _PRIOR_RAW_FILE_COUNT
    metadata_mode: int = _PRIOR_METADATA_MODE
    callback_prefix: tuple[str, ...] = _PRIOR_CALLBACK_PREFIX


@_dataclass(frozen=True, slots=True)
class _PriorAttemptProof:
    root_identity: tuple[int, int]
    root_mode: int
    raw_directory_identity: tuple[int, int]
    raw_directory_mode: int
    attempt_identity: _PrivateDocumentProof
    private_inventory: _PrivateDocumentProof
    generation_gate: _PrivateDocumentProof
    raw_rows: tuple[_InventoryRow, ...]
    raw_modes: tuple[tuple[str, int], ...]
    inventory_digest: str
    summary_sha256: str
    validation_sha256: str


_PRIOR_ANCHORS = _PriorAttemptAnchors()


@_dataclass(frozen=True, slots=True)
class _Attempt02Anchors:
    attempt_id: str = _ATTEMPT_02_ID
    execution_head: str = _ATTEMPT_02_EXECUTION_HEAD
    attempt_identity_sha256: str = _ATTEMPT_02_IDENTITY_SHA256
    private_inventory_sha256: str = _ATTEMPT_02_INVENTORY_SHA256
    private_inventory_digest: str = _ATTEMPT_02_INVENTORY_DIGEST
    generation_gate_sha256: str = _ATTEMPT_02_GATE_SHA256
    summary_sha256: str = _ATTEMPT_02_SUMMARY_SHA256
    validation_sha256: str = _ATTEMPT_02_VALIDATION_SHA256
    root_entry_count: int = _ATTEMPT_02_ROOT_ENTRY_COUNT
    raw_file_count: int = _ATTEMPT_02_RAW_FILE_COUNT
    metadata_mode: int = _ATTEMPT_02_METADATA_MODE
    callback_prefix: tuple[str, ...] = _ATTEMPT_02_CALLBACK_PREFIX


@_dataclass(frozen=True, slots=True)
class _Attempt02Proof:
    root_identity: tuple[int, int]
    root_mode: int
    raw_directory_identity: tuple[int, int]
    raw_directory_mode: int
    attempt_identity: _PrivateDocumentProof
    private_inventory: _PrivateDocumentProof
    generation_gate: _PrivateDocumentProof
    raw_rows: tuple[_InventoryRow, ...]
    raw_modes: tuple[tuple[str, int], ...]
    inventory_digest: str
    summary_sha256: str
    validation_sha256: str
    embedded_attempt_01_projection: tuple[object, ...]


_ATTEMPT_02_ANCHORS = _Attempt02Anchors()


@_dataclass(frozen=True, slots=True)
class _RealPreconditionResult:
    timeout_seconds: int
    credential_source_count: int


@_dataclass(frozen=True, slots=True)
class _CanonicalCollectionCapture:
    report: object
    deterministic_result: object
    ledger_source_bundle: object
    ledger_source_validation: object
    ledger_item: object
    crypto_source_bundle: object
    crypto_collection_result: object


def run_two_domain_airline_all_real_program_v01(
    *,
    execution_mode: str,
    attempt_number: int,
    private_output_directory: str | _Path,
    injected_provider: _lane.Provider | None = None,
    injected_safe_report_output: str | _Path | None = None,
    progress_sink: _Callable[[dict[str, object]], None] | None = None,
    prior_failed_attempt_directory: str | _Path | None = None,
    prior_attempt_id: str | None = None,
    owner_reviewed_attempt_02: bool = False,
    transitive_failed_attempt_directory: str | _Path | None = None,
    transitive_attempt_id: str | None = None,
    owner_reviewed_attempt_03: bool = False,
) -> AirlineA1ProgramResultV01:
    """Run one A1 attempt in injected validation or owner-terminal real mode."""
    root: _Path | None = None
    root_identity: tuple[int, int] | None = None
    attempt_plain: dict[str, object] | None = None
    attempt_proof: _PrivateDocumentProof | None = None
    callback_observed: list[str] = []
    base_calls_started: list[str] = []
    base_calls_completed: list[str] = []
    collector_count = 0
    output_owner: _OwnedOutput | None = None
    released_output: _ReleasedOutput | None = None
    success_gate_plain: dict[str, object] | None = None
    success_gate_proof: _PrivateDocumentProof | None = None
    safe_execution_id = ""
    safe_hash = ""
    inventory_digest = ""
    execution_head = ""
    preservation_state = _PRESERVATION_NOT_CREATED
    publication_state = _PUBLICATION_ABSENT
    prior_path: _Path | None = None
    prior_proof: _PriorAttemptProof | None = None
    attempt_02_path: _Path | None = None
    attempt_02_proof: _Attempt02Proof | None = None
    attempt_03 = attempt_number == 3
    try:
        _require_mode(execution_mode, injected_provider, injected_safe_report_output)
        if type(attempt_number) is not int or attempt_number not in (1, 2, 3):
            raise _RunnerFailure(REASON_ATTEMPT_INVALID, "input_validation")
        if execution_mode == MODE_INJECTED:
            if attempt_number != 1:
                raise _RunnerFailure(REASON_ATTEMPT_INVALID, "input_validation")
            if (
                prior_failed_attempt_directory is not None
                or prior_attempt_id is not None
                or owner_reviewed_attempt_02 is not False
                or transitive_failed_attempt_directory is not None
                or transitive_attempt_id is not None
                or owner_reviewed_attempt_03 is not False
            ):
                raise _RunnerFailure(REASON_RECOVERY_INPUT_INVALID, "input_validation")
        elif attempt_number == 2:
            if (
                prior_failed_attempt_directory is None
                or prior_attempt_id != _PRIOR_ANCHORS.attempt_id
                or owner_reviewed_attempt_02 is not True
                or transitive_failed_attempt_directory is not None
                or transitive_attempt_id is not None
                or owner_reviewed_attempt_03 is not False
            ):
                raise _RunnerFailure(REASON_RECOVERY_INPUT_INVALID, "input_validation")
        elif attempt_number == 3:
            if (
                prior_failed_attempt_directory is None
                or prior_attempt_id != _ATTEMPT_02_ANCHORS.attempt_id
                or owner_reviewed_attempt_02 is not False
                or transitive_failed_attempt_directory is None
                or transitive_attempt_id != _PRIOR_ANCHORS.attempt_id
                or owner_reviewed_attempt_03 is not True
            ):
                raise _RunnerFailure(
                    REASON_ATTEMPT_03_RECOVERY_INPUT_INVALID,
                    "input_validation",
                )
        else:
            raise _RunnerFailure(REASON_RECOVERY_INPUT_INVALID, "input_validation")
        if execution_mode == MODE_REAL:
            _require_real_local_preconditions(_os.environ)
            execution_head = _require_real_repository_ready()
        else:
            execution_head = _git_text("rev-parse", "HEAD")
            if _LOWER_HEAD.fullmatch(execution_head) is None or len(execution_head) != 40:
                raise _RunnerFailure(REASON_REPOSITORY_NOT_READY, "repository_guard")
        root = _validate_private_root(private_output_directory)
        if execution_mode == MODE_REAL and attempt_number == 2:
            prior_path = _validate_prior_failed_root(
                prior_failed_attempt_directory,
                root,
            )
            prior_proof = _verify_prior_attempt_v01(
                prior_path,
                str(prior_attempt_id),
                current_execution_head=execution_head,
            )
        elif execution_mode == MODE_REAL and attempt_number == 3:
            attempt_02_path, prior_path = _validate_attempt_03_predecessor_paths(
                prior_failed_attempt_directory,
                transitive_failed_attempt_directory,
                root,
            )
            prior_proof = _verify_prior_attempt_v01(
                prior_path,
                str(transitive_attempt_id),
                current_execution_head=execution_head,
            )
            attempt_02_proof = _verify_attempt_02_v01(
                attempt_02_path,
                str(prior_attempt_id),
                prior_proof=prior_proof,
                current_execution_head=execution_head,
            )
        output_path = _select_safe_report_path(
            execution_mode,
            injected_safe_report_output,
            private_root=root,
        )
        root_identity = _create_private_root(root)
        preservation_state = _PRESERVATION_RETAINED_UNPROVED
        attempt_plain = _build_attempt_identity(
            execution_mode=execution_mode,
            execution_head=execution_head,
            attempt_number=attempt_number,
            private_output_directory=root,
            prior_proof=prior_proof,
            attempt_02_proof=attempt_02_proof,
        )
        attempt_proof = _write_private_document(
            root,
            root_identity,
            ATTEMPT_IDENTITY_FILE,
            attempt_plain,
        )
        if _POST_ATTEMPT_IDENTITY_WRITE_HOOK is not None:
            _POST_ATTEMPT_IDENTITY_WRITE_HOOK(root / ATTEMPT_IDENTITY_FILE)
        _assert_private_root_entries(
            root,
            root_identity,
            (ATTEMPT_IDENTITY_FILE,),
        )
        _revalidate_private_document(root, root_identity, attempt_proof, attempt_plain)

        before_first_callback: _Callable[[], None] | None = None
        if attempt_03:
            before_first_callback = lambda: _require_dual_predecessors_unchanged(
                prior_proof,
                prior_path,
                str(transitive_attempt_id),
                attempt_02_proof,
                attempt_02_path,
                str(prior_attempt_id),
                current_execution_head=execution_head,
            )
        provider = _provider_for_mode(
            execution_mode,
            injected_provider,
            callback_observed,
            base_calls_started,
            base_calls_completed,
            progress_sink,
            before_first_callback=before_first_callback,
        )
        env = _collector_environment(execution_mode, root / RAW_ATTEMPT_DIRECTORY)
        constraints = _binding.build_client_constraints_preference_a_v01()
        snapshot = _binding.build_airline_candidate_snapshot_v01()
        _revalidate_private_document(root, root_identity, attempt_proof, attempt_plain)
        if execution_mode == MODE_REAL:
            _require_real_repository_ready(expected_head=execution_head)
            if attempt_number == 2:
                _require_prior_attempt_unchanged(
                    prior_proof,
                    prior_path,
                    str(prior_attempt_id),
                    current_execution_head=execution_head,
                )
        collector_count += 1
        try:
            capture = _collect_canonical_with_capture(
                env=env,
                provider=provider,
                causal_constraints=constraints,
                causal_snapshot=snapshot,
            )
        except Exception:
            if execution_mode == MODE_REAL:
                if attempt_number == 2:
                    _require_prior_attempt_unchanged(
                        prior_proof,
                        prior_path,
                        str(prior_attempt_id),
                        current_execution_head=execution_head,
                    )
                else:
                    _require_dual_predecessors_unchanged(
                        prior_proof,
                        prior_path,
                        str(transitive_attempt_id),
                        attempt_02_proof,
                        attempt_02_path,
                        str(prior_attempt_id),
                        current_execution_head=execution_head,
                    )
            raise
        report = capture.report
        if execution_mode == MODE_REAL:
            if attempt_number == 2:
                _require_prior_attempt_unchanged(
                    prior_proof,
                    prior_path,
                    str(prior_attempt_id),
                    current_execution_head=execution_head,
                )
            else:
                _require_dual_predecessors_unchanged(
                    prior_proof,
                    prior_path,
                    str(transitive_attempt_id),
                    attempt_02_proof,
                    attempt_02_path,
                    str(prior_attempt_id),
                    current_execution_head=execution_head,
                )
        if _POST_COLLECTOR_HOOK is not None:
            _POST_COLLECTOR_HOOK(root, report, capture)
        if not isinstance(report, _Mapping) or report.get("final_status") != STATUS_PASS:
            raise _RunnerFailure(REASON_COLLECTOR_FAILED, "collector_result")
        if (
            tuple(callback_observed) != ACTOR_IDS
            or tuple(base_calls_started) != ACTOR_IDS
            or tuple(base_calls_completed) != ACTOR_IDS
        ):
            raise _RunnerFailure(REASON_SOURCE_GEOMETRY_INVALID, "provider_call_geometry")
        _validate_collector_report_v01(
            report,
            execution_mode=execution_mode,
            deterministic_result=capture.deterministic_result,
            ledger_source_bundle=capture.ledger_source_bundle,
            ledger_source_validation=capture.ledger_source_validation,
            crypto_collection_result=capture.crypto_collection_result,
        )
        _validate_raw_evidence_v01(
            root=root,
            root_identity=root_identity,
            report=report,
            capture=capture,
        )
        _emit_validation_progress(progress_sink)
        _revalidate_private_document(root, root_identity, attempt_proof, attempt_plain)
        first_inventory = _scan_success_inventory(
            root,
            root_identity,
            expected_root_entries=(ATTEMPT_IDENTITY_FILE, RAW_ATTEMPT_DIRECTORY),
        )
        inventory_digest = first_inventory.digest
        normalization = build_airline_safe_normalization_v01(
            report,
            execution_head=execution_head,
            execution_mode=execution_mode,
            deterministic_result=capture.deterministic_result,
            ledger_source_bundle=capture.ledger_source_bundle,
            ledger_source_validation=capture.ledger_source_validation,
            crypto_collection_result=capture.crypto_collection_result,
            attempt_identity=attempt_plain,
        )
        safe_execution = build_airline_safe_execution_projection_v01(normalization)
        expected_safe_status = (
            STATUS_PASS if execution_mode == MODE_REAL else STATUS_FAIL_CLOSED
        )
        if validate_airline_safe_execution_projection_v01(safe_execution) != () or (
            safe_execution.status != expected_safe_status
        ):
            raise _RunnerFailure(
                REASON_SAFE_NORMALIZATION_INVALID,
                "safe_projection_validation",
            )
        safe_plain = airline_safe_execution_projection_to_plain_dict_v01(
            safe_execution
        )
        safe_execution_id = safe_execution.safe_execution_id
        if _canonical_json_bytes_v01(safe_plain) != _canonical_json_bytes_v01(
            airline_safe_execution_projection_to_plain_dict_v01(safe_execution)
        ):
            raise _RunnerFailure(
                REASON_SAFE_NORMALIZATION_INVALID,
                "safe_projection_round_trip",
            )
        safe_bytes = _canonical_json_line(normalization)
        _validate_public_safe_document(normalization)
        safe_hash = _sha256(safe_bytes)
        if execution_mode == MODE_REAL:
            _ensure_canonical_public_parent()
        output_owner = _write_public_safe_report(output_path, normalization)
        publication_state = _PUBLICATION_PRESENT
        if _POST_PUBLIC_WRITE_HOOK is not None:
            _POST_PUBLIC_WRITE_HOOK(output_path)
        final_inventory = _scan_success_inventory(
            root,
            root_identity,
            expected_root_entries=(ATTEMPT_IDENTITY_FILE, RAW_ATTEMPT_DIRECTORY),
            expected_raw_identity=first_inventory.raw_directory_identity,
        )
        if final_inventory.rows != first_inventory.rows or final_inventory.digest != inventory_digest:
            raise _RunnerFailure(REASON_INVENTORY_INVALID, "post_write_inventory")
        _revalidate_private_document(root, root_identity, attempt_proof, attempt_plain)
        _revalidate_owned_output(output_owner, normalization)
        inventory_plain = _inventory_plain(
            first_inventory,
            STATUS_PASS,
            attempt_number=attempt_number,
            attempt_id=str(attempt_plain["attempt_id"]),
        )
        inventory_proof = _write_private_document(
            root,
            root_identity,
            PRIVATE_INVENTORY_FILE,
            inventory_plain,
        )
        _revalidate_private_document(
            root,
            root_identity,
            inventory_proof,
            inventory_plain,
        )
        repeated_inventory = _scan_success_inventory(
            root,
            root_identity,
            expected_root_entries=(
                ATTEMPT_IDENTITY_FILE,
                RAW_ATTEMPT_DIRECTORY,
                PRIVATE_INVENTORY_FILE,
            ),
            expected_raw_identity=first_inventory.raw_directory_identity,
        )
        if repeated_inventory != first_inventory:
            raise _RunnerFailure(REASON_INVENTORY_INVALID, "final_private_inventory")
        _revalidate_private_document(root, root_identity, attempt_proof, attempt_plain)
        if _PRE_GENERATION_GATE_HOOK is not None:
            _PRE_GENERATION_GATE_HOOK(output_path)
        final_raw_identity = _validate_raw_evidence_v01(
            root=root,
            root_identity=root_identity,
            report=report,
            capture=capture,
        )
        final_inventory = _scan_success_inventory(
            root,
            root_identity,
            expected_root_entries=(
                ATTEMPT_IDENTITY_FILE,
                RAW_ATTEMPT_DIRECTORY,
                PRIVATE_INVENTORY_FILE,
            ),
            expected_raw_identity=first_inventory.raw_directory_identity,
        )
        if (
            final_raw_identity != first_inventory.raw_directory_identity
            or final_inventory != first_inventory
        ):
            raise _RunnerFailure(REASON_INVENTORY_INVALID, "final_freeze")
        _revalidate_private_document(
            root,
            root_identity,
            attempt_proof,
            attempt_plain,
        )
        final_inventory_plain, final_inventory_proof = (
            _prove_existing_private_document(
                root,
                root_identity,
                PRIVATE_INVENTORY_FILE,
            )
        )
        if (
            final_inventory_plain != inventory_plain
            or final_inventory_proof.identity != inventory_proof.identity
            or final_inventory_proof.expected_bytes
            != inventory_proof.expected_bytes
            or final_inventory_proof.byte_count != inventory_proof.byte_count
        ):
            raise _RunnerFailure(REASON_INVENTORY_INVALID, "final_freeze")
        _revalidate_owned_output(output_owner, normalization)
        if execution_mode == MODE_REAL:
            if attempt_number == 2:
                _require_prior_attempt_unchanged(
                    prior_proof,
                    prior_path,
                    str(prior_attempt_id),
                    current_execution_head=execution_head,
                    owned_public_report=output_owner,
                )
            else:
                _require_dual_predecessors_unchanged(
                    prior_proof,
                    prior_path,
                    str(transitive_attempt_id),
                    attempt_02_proof,
                    attempt_02_path,
                    str(prior_attempt_id),
                    current_execution_head=execution_head,
                    owned_public_report=output_owner,
                )
        gate_plain = _generation_gate_plain(
            attempt_plain=attempt_plain,
            attempt_identity_sha256=attempt_proof.sha256,
            final_status=STATUS_PASS,
            reason_code="",
            failed_stage="",
            safe_execution_id=safe_execution_id,
            safe_report_sha256=safe_hash,
            inventory_digest=inventory_digest,
            private_inventory_sha256=final_inventory_proof.sha256,
            execution_mode=execution_mode,
            attempt_number=attempt_number,
            callback_observed=tuple(callback_observed),
            base_calls_started=tuple(base_calls_started),
            base_calls_completed=tuple(base_calls_completed),
            publication_state=_PUBLICATION_PRESENT,
        )
        success_result = _result(
            execution_mode=execution_mode,
            execution_head=execution_head,
            attempt_number=attempt_number,
            attempt_id=str(attempt_plain["attempt_id"]),
            final_status=STATUS_PASS,
            reason_code="",
            failed_stage="",
            preservation_state=_PRESERVATION_PRESERVED,
            publication_state=_PUBLICATION_PRESENT,
            collector_count=collector_count,
            callback_observed=tuple(callback_observed),
            base_calls_started=tuple(base_calls_started),
            base_calls_completed=tuple(base_calls_completed),
            safe_execution_id=safe_execution_id,
            safe_hash=safe_hash,
            inventory_digest=inventory_digest,
        )
        success_gate_plain = gate_plain
        success_gate_proof = _write_private_document(
            root,
            root_identity,
            GENERATION_GATE_FILE,
            gate_plain,
            expected_root_entries=(
                ATTEMPT_IDENTITY_FILE,
                RAW_ATTEMPT_DIRECTORY,
                PRIVATE_INVENTORY_FILE,
                GENERATION_GATE_FILE,
            ),
        )
        if _POST_PASS_GATE_WRITE_HOOK is not None:
            _POST_PASS_GATE_WRITE_HOOK(
                output_path,
                root / GENERATION_GATE_FILE,
            )
        _revalidate_private_document(
            root,
            root_identity,
            success_gate_proof,
            success_gate_plain,
        )
        _revalidate_owned_output(output_owner, normalization)
        released_output = _release_owned_output(output_owner)
        output_owner = None
        return success_result
    except _PublicCleanupFailure:
        reason = REASON_PUBLIC_CLEANUP_FAILED
        stage = "public_safe_report_cleanup"
        publication_state = _PUBLICATION_ABSENCE_UNPROVEN
    except _RunnerFailure as error:
        reason = error.reason
        stage = error.stage
    except Exception:
        reason = REASON_UNEXPECTED
        stage = "unexpected_exception"

    if (
        success_gate_proof is not None
        and success_gate_plain is not None
        and root is not None
        and root_identity is not None
    ):
        try:
            _cleanup_owned_private_document(
                root,
                root_identity,
                success_gate_proof,
                success_gate_plain,
            )
            success_gate_proof = None
        except Exception:
            reason = REASON_PRIVATE_METADATA_FAILED
            stage = "generation_gate_cleanup"
    if output_owner is not None:
        try:
            _cleanup_owned_output(output_owner)
            publication_state = _PUBLICATION_ABSENT
        except _PublicCleanupFailure:
            reason = REASON_PUBLIC_CLEANUP_FAILED
            stage = "public_safe_report_cleanup"
            publication_state = _PUBLICATION_ABSENCE_UNPROVEN
    elif released_output is not None:
        try:
            _cleanup_released_output(released_output)
            publication_state = _PUBLICATION_ABSENT
        except _PublicCleanupFailure:
            reason = REASON_PUBLIC_CLEANUP_FAILED
            stage = "public_safe_report_cleanup"
            publication_state = _PUBLICATION_ABSENCE_UNPROVEN
    if (
        root is not None
        and root_identity is not None
        and attempt_plain is not None
        and attempt_proof is not None
    ):
        failure_checkpoint_override: list[tuple[str, str]] = []
        before_failure_gate: _Callable[[], tuple[str, str] | None] | None = None
        if attempt_03 and prior_proof is not None and attempt_02_proof is not None:
            def before_failure_gate() -> tuple[str, str] | None:
                try:
                    _require_dual_predecessors_unchanged(
                        prior_proof,
                        prior_path,
                        str(transitive_attempt_id),
                        attempt_02_proof,
                        attempt_02_path,
                        str(prior_attempt_id),
                        current_execution_head=execution_head,
                    )
                    return None
                except _RunnerFailure as error:
                    override = (error.reason, error.stage)
                    failure_checkpoint_override.append(override)
                    return override

        inventory_digest, preservation_state = _preserve_failed_private_attempt(
            root=root,
            root_identity=root_identity,
            attempt_plain=attempt_plain,
            attempt_proof=attempt_proof,
            reason_code=reason,
            failed_stage=stage,
            execution_mode=execution_mode,
            callback_observed=tuple(callback_observed),
            base_calls_started=tuple(base_calls_started),
            base_calls_completed=tuple(base_calls_completed),
            safe_execution_id=safe_execution_id,
            safe_report_sha256=safe_hash,
            publication_state=publication_state,
            before_generation_gate=before_failure_gate,
        )
        if failure_checkpoint_override:
            reason, stage = failure_checkpoint_override[-1]
    return _result(
        execution_mode=(
            execution_mode if execution_mode in (MODE_INJECTED, MODE_REAL) else ""
        ),
        execution_head=execution_head,
        attempt_number=(attempt_number if type(attempt_number) is int else 0),
        attempt_id=(str(attempt_plain["attempt_id"]) if attempt_plain else ""),
        final_status=STATUS_FAIL_CLOSED,
        reason_code=reason,
        failed_stage=stage,
        preservation_state=preservation_state,
        publication_state=publication_state,
        collector_count=collector_count,
        callback_observed=tuple(callback_observed),
        base_calls_started=tuple(base_calls_started),
        base_calls_completed=tuple(base_calls_completed),
        safe_execution_id=safe_execution_id,
        safe_hash=safe_hash,
        inventory_digest=inventory_digest,
    )


def build_airline_safe_normalization_v01(
    source_report: _Mapping[str, object],
    *,
    execution_head: str,
    execution_mode: str | None = None,
    deterministic_result: object = None,
    ledger_source_bundle: object = None,
    ledger_source_validation: object = None,
    crypto_collection_result: object = None,
    attempt_identity: _Mapping[str, object] | None = None,
) -> dict[str, object]:
    """Whitelist-normalize one already validated canonical collector result."""
    try:
        _validate_collector_report_v01(
            source_report,
            execution_mode=execution_mode,
            deterministic_result=deterministic_result,
            ledger_source_bundle=ledger_source_bundle,
            ledger_source_validation=ledger_source_validation,
            crypto_collection_result=crypto_collection_result,
        )
        ledger_item = source_report["airline_transaction_artifact_ledger_v0_1"]
        entries_by_type = {
            entry.artifact_type: entry for entry in ledger_item.entries
        }
        actors = []
        for item in source_report["semantic_actor_reports"]:
            actors.append(
                {
                    "actor_id": item["actor_id"],
                    "safe_projection": {
                        "actor_id": item["actor_id"],
                        "actor_index": item["actor_index"],
                        "side": item["side"],
                        "canonical_summary": item["output_semantic_summary"],
                        "accepted": item["accepted"],
                        "authority_created": item["authority_created"],
                        "action_permission_created": item[
                            "action_permission_created"
                        ],
                        "packet_created": item["packet_created"],
                        "receipt_created": item["receipt_created"],
                        "payment_created": item["payment_created"],
                        "ticket_created": item["ticket_created"],
                        "booking_created": item["booking_created"],
                        "final_output_created": item["final_output_created"],
                        "real_world_effects_count": item[
                            "real_world_effects_count"
                        ],
                    },
                    "validation_status": item["validation_status"],
                }
            )
        bsep_packet = source_report["bsep_membrane"]
        projections = source_report["bsep_side_projections"]
        safe_bsep_rows = []
        for name, shared_ref in zip(
            BSEP_PROJECTION_NAMES,
            SHARED_BSEP_PROJECTION_REFS,
            strict=True,
        ):
            projection = projections[name]
            safe_bsep_rows.append(
                {
                    "projection_ref": shared_ref,
                    "safe_projection": {
                        "projection_id": projection["projection_id"],
                        "projection_ref": shared_ref,
                        "source_projection_ref": projection["projection_ref"],
                        "source_bsep_packet_id": projection[
                            "source_bsep_packet_id"
                        ],
                        "transaction_id": projection["transaction_id"],
                        "side": projection["side"],
                        "bounded_context_summary": projection[
                            "bounded_context_summary"
                        ],
                        "validation_status": projection["validation_status"],
                        "authority_created": projection["authority_created"],
                        "permission_created": projection["permission_created"],
                        "real_world_effects_count": projection[
                            "real_world_effects_count"
                        ],
                    },
                }
            )
        roots = []
        for role, artifact_type in ROOT_FINAL_GEOMETRY:
            entry = entries_by_type[artifact_type]
            roots.append(
                {
                    "root_role": role,
                    "final_id": entry.artifact_id,
                    "safe_projection": _safe_ledger_projection(entry),
                }
            )
        receipts = []
        for artifact_type in RECEIPT_ARTIFACT_TYPES:
            entry = entries_by_type[artifact_type]
            receipts.append(
                {
                    "receipt_id": entry.artifact_id,
                    "safe_projection": _safe_ledger_projection(entry),
                }
            )
        bridge = source_report["semantic_to_contract_deterministic_bridge"]
        deterministic = source_report["integrated_deterministic_airline_transaction"]
        run_id = source_report["run_id"]
        report_id = source_report["report_id"]
        source_task_id = _SOURCE_TASK_ID
        if (
            attempt_identity is not None
            and attempt_identity.get("attempt_number") in (2, 3)
        ):
            run_id = attempt_identity["run_id"]
            report_id = attempt_identity["report_id"]
            source_task_id = attempt_identity["source_task_id"]
        normalization: dict[str, object] = {
            "execution_head": _required_head(execution_head),
            "run_id": run_id,
            "report_id": report_id,
            "source_task_id": source_task_id,
            "transaction_id": source_report["transaction_id"],
            "selected_offer_id": bridge["semantic_recommendation_id"],
            "provider_mode": source_report["provider_mode"],
            "model_id": source_report["model"],
            "source_final_status": source_report["final_status"],
            "actors": actors,
            "bsep": {
                "packet_id": bsep_packet["bsep_packet_id"],
                "safe_projection": {
                    "packet_id": bsep_packet["bsep_packet_id"],
                    "transaction_id": bsep_packet["transaction_id"],
                    "source_orchestrator_actor_id": bsep_packet[
                        "source_orchestrator_actor_id"
                    ],
                    "bounded_context_summary": bsep_packet[
                        "bounded_context_summary"
                    ],
                    "validation_status": bsep_packet["validation_status"],
                    "authority_created": bsep_packet["authority_created"],
                    "action_permission_created": bsep_packet[
                        "action_permission_created"
                    ],
                },
                "projections": safe_bsep_rows,
            },
            "root_finals": roots,
            "corridor": {
                "report_id": ledger_item.source_corridor_report_ref,
                "safe_projection": {
                    "report_id": ledger_item.source_corridor_report_ref,
                    "transaction_id": deterministic["transaction_id"],
                    "selected_offer_id": deterministic["selected_offer_id"],
                    "corridor_final_status": deterministic[
                        "corridor_final_status"
                    ],
                    "corridor_execution_count": deterministic[
                        "corridor_execution_count"
                    ],
                    "mock_only": True,
                    "real_world_effects_count": deterministic[
                        "real_world_effects_count"
                    ],
                },
            },
            "receipts": receipts,
            "counters": {
                "provider_call_count": 12,
                "network_call_count": 12,
                "gemini_call_count": 12,
            },
            "raw_prompt_included": False,
            "raw_provider_response_included": False,
            "secret_scan_passed": True,
            "real_world_effects_count": 0,
            "validation_errors": (),
        }
        if frozenset(normalization) != _SAFE_REPORT_KEYS:
            raise ValueError
        _validate_public_safe_document(normalization)
        return normalization
    except _RunnerFailure:
        raise ValueError(REASON_SAFE_NORMALIZATION_INVALID) from None
    except Exception:
        raise ValueError(REASON_SAFE_NORMALIZATION_INVALID) from None


def validate_airline_safe_normalization_v01(
    source_report: object,
) -> tuple[str, ...]:
    try:
        if not isinstance(source_report, _Mapping):
            return (REASON_SAFE_NORMALIZATION_INVALID,)
        if frozenset(source_report) != _SAFE_REPORT_KEYS:
            return (REASON_SAFE_NORMALIZATION_INVALID,)
        _validate_public_safe_document(source_report)
        result = build_airline_safe_execution_projection_v01(source_report)
        if validate_airline_safe_execution_projection_v01(result):
            return (REASON_SAFE_NORMALIZATION_INVALID,)
        return ()
    except Exception:
        return (REASON_SAFE_NORMALIZATION_INVALID,)


def airline_a1_program_result_to_plain_dict_v01(
    result: AirlineA1ProgramResultV01,
) -> dict[str, object]:
    if type(result) is not AirlineA1ProgramResultV01:
        raise ValueError(REASON_INVALID)
    return {name: getattr(result, name) for name in result.__slots__}


def _collect_canonical_with_capture(
    *,
    env: _Mapping[str, str],
    provider: _lane.Provider,
    causal_constraints: object,
    causal_snapshot: object,
) -> _CanonicalCollectionCapture:
    deterministic_module = _lane.deterministic_airline
    deterministic_name = "collect_tri_party_airline_ticket_purchase_mock_e2e_v01"
    original_deterministic = getattr(deterministic_module, deterministic_name)
    original_crypto = (
        _crypto_collector.collect_airline_crypto_artifact_seal_from_source_bundle_v01
    )
    deterministic_results: list[object] = []
    crypto_source_bundles: list[object] = []
    crypto_results: list[object] = []

    def capture_deterministic(*args: object, **kwargs: object) -> object:
        result = original_deterministic(*args, **kwargs)
        deterministic_results.append(result)
        return result

    def capture_crypto(*args: object, **kwargs: object) -> object:
        crypto_source_bundles.append(kwargs.get("source_bundle"))
        result = original_crypto(*args, **kwargs)
        crypto_results.append(result)
        return result

    setattr(deterministic_module, deterministic_name, capture_deterministic)
    setattr(
        _crypto_collector,
        "collect_airline_crypto_artifact_seal_from_source_bundle_v01",
        capture_crypto,
    )
    try:
        report = _COLLECTOR(
            env=env,
            provider=provider,
            causal_constraints=causal_constraints,
            causal_snapshot=causal_snapshot,
        )
    finally:
        setattr(deterministic_module, deterministic_name, original_deterministic)
        setattr(
            _crypto_collector,
            "collect_airline_crypto_artifact_seal_from_source_bundle_v01",
            original_crypto,
        )

    deterministic_result = (
        deterministic_results[0] if len(deterministic_results) == 1 else None
    )
    if deterministic_result is None:
        deterministic_result = getattr(report, "_a1_deterministic_result", None)
    ledger_source_bundle = getattr(
        deterministic_result,
        "_airline_transaction_artifact_ledger_source_bundle_v0_1",
        None,
    )
    ledger_source_validation = getattr(
        deterministic_result,
        "_airline_transaction_artifact_ledger_source_validation_v0_1",
        None,
    )
    ledger_item = getattr(
        deterministic_result,
        "_airline_transaction_artifact_ledger_v0_1",
        None,
    )
    if ledger_source_bundle is None:
        ledger_source_bundle = getattr(report, "_a1_ledger_source_bundle", None)
        ledger_source_validation = getattr(
            report,
            "_a1_ledger_source_validation",
            None,
        )
        ledger_item = getattr(report, "_a1_ledger_item", None)
    crypto_source_bundle = (
        crypto_source_bundles[0] if len(crypto_source_bundles) == 1 else None
    )
    crypto_result = crypto_results[0] if len(crypto_results) == 1 else None
    if crypto_source_bundle is None:
        crypto_source_bundle = getattr(report, "_a1_crypto_source_bundle", None)
        crypto_result = getattr(report, "_a1_crypto_collection_result", None)
    return _CanonicalCollectionCapture(
        report=report,
        deterministic_result=deterministic_result,
        ledger_source_bundle=ledger_source_bundle,
        ledger_source_validation=ledger_source_validation,
        ledger_item=ledger_item,
        crypto_source_bundle=crypto_source_bundle,
        crypto_collection_result=crypto_result,
    )


def _provider_for_mode(
    execution_mode: str,
    injected_provider: _lane.Provider | None,
    callback_observed: list[str],
    base_calls_started: list[str],
    base_calls_completed: list[str],
    progress_sink: _Callable[[dict[str, object]], None] | None,
    *,
    before_first_callback: _Callable[[], None] | None = None,
) -> _lane.Provider:
    if execution_mode == MODE_INJECTED:
        base = injected_provider or _build_injected_provider_v01()
    else:
        base = _REAL_PROVIDER_BUILDER(MODEL_ID)
    first_callback_checkpoint_attempted = False

    def observed(actor_id: str, prompt: str, metadata: _Mapping[str, object]) -> str:
        nonlocal first_callback_checkpoint_attempted
        index = len(callback_observed) + 1
        if (
            type(actor_id) is not str
            or index > len(ACTOR_IDS)
            or actor_id != ACTOR_IDS[index - 1]
            or actor_id in callback_observed
        ):
            raise ValueError("provider_call_geometry_invalid")
        if index == 1 and before_first_callback is not None:
            if first_callback_checkpoint_attempted:
                raise ValueError("provider_call_geometry_invalid")
            first_callback_checkpoint_attempted = True
            before_first_callback()
        callback_observed.append(actor_id)
        _emit_progress(progress_sink, index, actor_id, "call_started", "")
        try:
            supplied_metadata = dict(metadata)
            base_calls_started.append(actor_id)
            response = base(actor_id, prompt, supplied_metadata)
        except Exception:
            _emit_progress(progress_sink, index, actor_id, "call_failed", "")
            raise
        base_calls_completed.append(actor_id)
        _emit_progress(progress_sink, index, actor_id, "call_completed", "")
        return response

    return observed


def _build_injected_provider_v01() -> _lane.Provider:
    generic = _lane.build_fake_airline_semantic_provider_v01()

    def provider(actor_id: str, prompt: str, metadata: _Mapping[str, object]) -> str:
        request = metadata.get("semantic_to_contract_request")
        if not isinstance(request, _Mapping):
            return generic(actor_id, prompt, metadata)
        if actor_id == _binding.ACTOR_CLIENT_PURCHASE_INTENT_REVIEWER:
            payload = {
                "recommended_offer_id": _binding.OFFER_A_ID,
                "ranked_offer_ids": [_binding.OFFER_A_ID],
                "decision_factors": ["preference_a_exact_fit"],
                "preference_matches": ["lower_price", "window_seat"],
                "uncertainty_notes": ["requires_client_root_review"],
                "requires_root_review": True,
                "semantic_summary": (
                    "Preference A recommends bounded Offer A for Root review."
                ),
            }
        else:
            payload = {
                "supports_proposed_offer": True,
                "semantic_factors": ["supports_preference_a"],
                "blocking_conflicts": [],
            }
        return _json.dumps(payload, ensure_ascii=False, sort_keys=True)

    return provider


def _collector_environment(execution_mode: str, raw_directory: _Path) -> dict[str, str]:
    env: dict[str, str] = {}
    if execution_mode == MODE_REAL:
        for key in (*_CREDENTIAL_ENV_KEYS, _PROVIDER_TIMEOUT_ENV_KEY):
            value = _os.environ.get(key)
            if type(value) is str:
                env[key] = value
    for key in _AIRLINE_CONTROL_ENV_KEYS:
        env.pop(key, None)
    env.update(
        {
            _lane.ENV_LANE: "1",
            _lane.ENV_CAUSAL_BINDING: "1",
            _lane.ENV_CRYPTO_ARTIFACT_SEAL: "1",
            _lane.ENV_ARTIFACT_DIR: str(raw_directory),
            _lane.ENV_MODEL: MODEL_ID,
            _lane.ENV_ALLOW_RAW: "0",
            _lane.ENV_CALL_DELAY_SECONDS: (
                "2" if execution_mode == MODE_REAL else "0"
            ),
        }
    )
    if execution_mode == MODE_REAL:
        env.pop(_lane.ENV_FAKE_PROVIDER, None)
        env[_lane.ENV_REAL_PROVIDER] = "1"
    else:
        env.pop(_lane.ENV_REAL_PROVIDER, None)
        env[_lane.ENV_FAKE_PROVIDER] = "1"
    return env


def _actor_geometry_valid(
    actors: object,
    *,
    provider_mode: str,
) -> bool:
    if type(actors) is not tuple or len(actors) != len(_lane.ACTOR_SPECS):
        return False
    for index, (row, spec) in enumerate(zip(actors, _lane.ACTOR_SPECS, strict=True), start=1):
        if not isinstance(row, _Mapping):
            return False
        if (
            row.get("actor_id") != spec["actor_id"]
            or row.get("actor_index") != index
            or row.get("side") != spec["side"]
            or row.get("group") != spec["group"]
            or row.get("provider_mode") != provider_mode
            or row.get("model") != MODEL_ID
            or row.get("validation_status") != STATUS_PASS
            or row.get("accepted") is not True
        ):
            return False
        vertical = spec.get("vertical_fractal_cell") is True
        if vertical:
            if (
                row.get("vertical_fractal_cell") is not True
                or row.get("parent_actor_id") != spec.get("parent_actor_id")
                or row.get("parent_validation_status") != STATUS_PASS
            ):
                return False
        elif any(
            key in row
            for key in (
                "vertical_fractal_cell",
                "parent_actor_id",
                "parent_validation_status",
            )
        ):
            return False
    return True


def _expected_vertical_geometry() -> tuple[dict[str, object], ...]:
    false_fields = {
        "child_received_parent_raw_response": False,
        "child_received_sibling_raw_output": False,
        "child_received_unbounded_context": False,
        "child_creates_authority": False,
        "child_creates_packet": False,
        "child_creates_receipt": False,
        "child_creates_payment": False,
        "child_creates_ticket": False,
        "child_creates_booking": False,
    }
    return tuple(
        {
            "child_actor_id": spec["actor_id"],
            "parent_actor_id": spec["parent_actor_id"],
            "parent_validation_status": STATUS_PASS,
            "child_started_after_parent_validation": True,
            "child_received_parent_canonical_summary": True,
            **false_fields,
            "child_result_returns_to_parent_or_root_review": True,
            "real_world_effects_count": 0,
        }
        for spec in _lane.ACTOR_SPECS
        if spec.get("vertical_fractal_cell") is True
    )


def _expected_selection_input(report: _Mapping[str, object]) -> object:
    projection = report["bsep_side_projections"]["airline_bsep_projection"]
    typed_projection = _binding.AirlineBSEPProjectionRefV01(
        projection_ref=projection["projection_ref"],
        transaction_id=projection["transaction_id"],
        projection_side="airline_offer_selection",
        validation_status=projection["validation_status"],
        raw_secret_included=projection["raw_secrets_included"],
        authority_created=projection["authority_created"],
        real_world_effects_count=projection["real_world_effects_count"],
    )
    return _binding.build_selection_input_v01(
        typed_projection,
        _binding.build_client_constraints_preference_a_v01(),
        _binding.build_airline_candidate_snapshot_v01(),
    )


def _fresh_ledger_validation(
    ledger_item: object,
    *,
    ledger_source_bundle: object,
    ledger_source_validation: object,
) -> tuple[object, object, object]:
    if (
        type(ledger_item) is not _ledger.AirlineTransactionArtifactLedgerV01
        or type(ledger_source_bundle)
        is not _ledger_collector.AirlineTransactionArtifactLedgerSourceBundleV01
        or type(ledger_source_validation)
        is not _ledger_collector.AirlineTransactionArtifactLedgerSourceValidationReportV01
    ):
        raise ValueError
    fresh_source_validation = (
        _ledger_collector.validate_airline_transaction_artifact_ledger_source_bundle_v01(
            ledger_source_bundle,
        )
    )
    if (
        fresh_source_validation != ledger_source_validation
        or fresh_source_validation.validation_status != STATUS_PASS
        or fresh_source_validation.validation_errors != ()
    ):
        raise ValueError
    expected_identity = (
        _ledger_collector.build_airline_transaction_artifact_ledger_expected_identity_from_source_v01(
            source_bundle=ledger_source_bundle,
        )
    )
    expected_refs = ledger_source_bundle.expected_source_refs
    validation = _ledger.validate_airline_transaction_artifact_ledger_v01(
        ledger_item,
        expected_source_refs=expected_refs,
        expected_identity=expected_identity,
    )
    return expected_identity, validation, fresh_source_validation


def _ledger_validation_passed(validation: object) -> bool:
    required_true = (
        "indexes_valid",
        "artifact_ids_unique",
        "event_types_valid",
        "transaction_identity_valid",
        "dependencies_present",
        "dependencies_ordered",
        "dependency_graph_acyclic",
        "root_ownership_valid",
        "authority_classes_valid",
        "evidence_classes_valid",
        "canonical_hash_inputs_safe",
        "raw_secret_boundary_valid",
        "raw_provider_boundary_valid",
        "ledger_non_authority_valid",
        "real_effects_zero",
    )
    return bool(
        validation.validation_status == STATUS_PASS
        and validation.validation_errors == ()
        and all(getattr(validation, field) is True for field in required_true)
    )


def _validate_collector_report_v01(
    report: object,
    *,
    execution_mode: str | None,
    deterministic_result: object,
    ledger_source_bundle: object,
    ledger_source_validation: object,
    crypto_collection_result: object,
) -> None:
    try:
        if not isinstance(report, _Mapping):
            raise ValueError
        expected_provider_mode = (
            _lane.PROVIDER_MODE_REAL
            if execution_mode == MODE_REAL
            else _lane.PROVIDER_MODE_FAKE
            if execution_mode == MODE_INJECTED
            else None
        )
        actors = report["semantic_actor_reports"]
        counters = report["counter_table"]
        bridge = report["semantic_to_contract_deterministic_bridge"]
        deterministic = report["integrated_deterministic_airline_transaction"]
        ledger_summary = report["airline_transaction_artifact_ledger_integration"]
        ledger_item = report["airline_transaction_artifact_ledger_v0_1"]
        crypto = report["airline_crypto_artifact_seal_integration"]
        deterministic_source = report["deterministic_source"]
        if type(crypto_collection_result) is not _crypto_collector.AirlineCryptoArtifactSealCollectionResultV01:
            raise ValueError
        crypto_collection_plain = (
            _crypto_collector.airline_crypto_artifact_seal_collection_result_to_plain_dict_v01(
                crypto_collection_result
            )
        )
        if (
            report["final_status"] != STATUS_PASS
            or report["run_id"] != _lane.RUN_ID
            or report["report_id"] != _lane.REPORT_ID
            or report["lane_id"] != _lane.LANE_ID
            or report["model"] != MODEL_ID
            or report["transaction_id"] != _binding.TRANSACTION_ID
            or (expected_provider_mode is not None and report["provider_mode"] != expected_provider_mode)
            or not _actor_geometry_valid(
                actors,
                provider_mode=report["provider_mode"],
            )
            or tuple(report["semantic_actor_call_order"]) != ACTOR_IDS
            or report["validation_errors"] != ()
            or report["raw_response_terminal_output_allowed"] is not False
            or deterministic_source
            != {
                "run_id": "tri_party_airline_semantic_source_context_v01",
                "report_id": "tri_party_airline_semantic_source_context_v01",
                "final_status": STATUS_PASS,
            }
        ):
            raise ValueError
        actor_false_fields = (
            "authority_created",
            "action_permission_created",
            "packet_created",
            "receipt_created",
            "payment_created",
            "ticket_created",
            "booking_created",
            "final_output_created",
            "real_payment_executed",
            "real_ticket_issued",
            "real_booking_created",
        )
        if any(
            any(item.get(field_name) is not False for field_name in actor_false_fields)
            or item.get("real_world_effects_count") != 0
            for item in actors
        ):
            raise ValueError
        expected_counts = {
            "semantic_actor_call_count": 12,
            "causal_semantic_actor_call_count": 5,
            "generic_semantic_actor_call_count": 7,
            "duplicate_semantic_actor_call_count": 0,
            "deterministic_airline_collection_count": 1,
            "ticket_purchase_corridor_execution_count": 1,
            "airline_transaction_artifact_ledger_source_bundle_collection_count": 1,
            "airline_transaction_artifact_ledger_collection_count": 1,
            "airline_transaction_artifact_ledger_validation_count": 1,
            "airline_transaction_artifact_ledger_entry_count": 19,
            "airline_transaction_artifact_ledger_dependency_edge_count": 29,
            "airline_transaction_artifact_ledger_root_final_count": 3,
            "airline_transaction_artifact_ledger_duplicate_collection_count": 0,
            "airline_transaction_artifact_ledger_duplicate_corridor_execution_count": 0,
            "airline_transaction_artifact_ledger_duplicate_transaction_count": 0,
            "airline_transaction_artifact_ledger_source_reconstruction_count": 0,
            "direct_offer_override_count": 0,
            "default_offer_count": 0,
            "silent_fallback_count": 0,
            "provider_output_used_as_truth_count": 0,
            "provider_output_used_as_authority_count": 0,
            "provider_created_authority_count": 0,
            "provider_created_contract_count": 0,
            "provider_output_created_packet_count": 0,
            "provider_output_created_receipt_count": 0,
            "provider_output_created_payment_count": 0,
            "provider_output_created_ticket_count": 0,
            "provider_output_created_booking_count": 0,
            "real_airline_api_called_count": 0,
            "real_bank_api_called_count": 0,
            "real_gds_api_called_count": 0,
            "real_payment_executed_count": 0,
            "real_ticket_issued_count": 0,
            "real_booking_created_count": 0,
            "real_world_effects_count": 0,
        }
        if any(type(counters.get(key)) is not int or counters.get(key) != value for key, value in expected_counts.items()):
            raise ValueError
        source_mode = report["provider_mode"]
        if source_mode == _lane.PROVIDER_MODE_FAKE:
            source_external_geometry = (
                counters.get("real_provider_call_count"),
                counters.get("fake_provider_call_count"),
                counters.get("network_used_count"),
                counters.get("gemini_called_count"),
                counters.get("real_provider_call_delay_applied_count"),
            )
            if source_external_geometry != (0, 12, 0, 0, 0):
                raise ValueError
        elif source_mode == _lane.PROVIDER_MODE_REAL:
            source_external_geometry = (
                counters.get("real_provider_call_count"),
                counters.get("fake_provider_call_count"),
                counters.get("network_used_count"),
                counters.get("gemini_called_count"),
                counters.get("real_provider_call_delay_applied_count"),
            )
            if source_external_geometry != (12, 0, 12, 12, 12):
                raise ValueError
        else:
            raise ValueError
        bsep_packet = report["bsep_membrane"]
        bsep_false_fields = (
            "raw_passport_included",
            "raw_card_included",
            "raw_iban_included",
            "raw_payment_token_included",
            "raw_private_profile_included",
            "raw_provider_text_included",
            "raw_response_dump_included",
            "authority_created",
            "action_permission_created",
            "payment_created",
            "ticket_created",
            "booking_created",
            "final_output_created",
        )
        bsep_validation = report["bsep_validation"]
        expected_bsep_packet = _lane._build_bsep_packet(actors[0])
        expected_bsep_validation = _lane._validate_bsep_packet(expected_bsep_packet)
        expected_bsep_projections = _lane._build_bsep_side_projections(
            expected_bsep_packet
        )
        if (
            bsep_packet != expected_bsep_packet
            or bsep_validation != expected_bsep_validation
            or report["bsep_side_projections"] != expected_bsep_projections
            or
            bsep_packet.get("validation_status") != STATUS_PASS
            or any(bsep_packet.get(field_name) is not False for field_name in bsep_false_fields)
            or bsep_validation.get("accepted") is not True
            or bsep_validation.get("validation_status") != STATUS_PASS
            or any(
                bsep_validation.get(field_name) is not False
                for field_name in (
                    "bsep_is_truth",
                    "bsep_is_authority",
                    "bsep_is_permission",
                    "bsep_creates_packet",
                    "bsep_creates_receipt",
                    "bsep_creates_payment",
                    "bsep_creates_ticket",
                    "bsep_creates_booking",
                )
            )
            or len(report["bsep_side_projections"]) != 4
            or tuple(report["bsep_side_projections"]) != BSEP_PROJECTION_NAMES
            or any(
                report["bsep_side_projections"][name].get("validation_status")
                != STATUS_PASS
                for name in BSEP_PROJECTION_NAMES
            )
            or any(
                report["bsep_side_projections"][name].get(field_name)
                is not False
                for name in BSEP_PROJECTION_NAMES
                for field_name in (
                    "raw_secrets_included",
                    "raw_provider_text_included",
                    "authority_created",
                    "permission_created",
                )
            )
            or any(
                report["bsep_side_projections"][name].get(
                    "real_world_effects_count"
                )
                != 0
                for name in BSEP_PROJECTION_NAMES
            )
        ):
            raise ValueError
        vertical = report["vertical_fractal_dependencies"]
        if tuple(vertical) != _expected_vertical_geometry() or any(
            row["parent_validation_status"] != STATUS_PASS
            or row["child_started_after_parent_validation"] is not True
            or row["child_received_parent_canonical_summary"] is not True
            or row["child_received_parent_raw_response"] is not False
            or row["child_received_sibling_raw_output"] is not False
            or row["child_received_unbounded_context"] is not False
            or row["child_result_returns_to_parent_or_root_review"] is not True
            or row["child_creates_authority"] is not False
            or row["child_creates_packet"] is not False
            or row["child_creates_receipt"] is not False
            or row["child_creates_payment"] is not False
            or row["child_creates_ticket"] is not False
            or row["child_creates_booking"] is not False
            or row["real_world_effects_count"] != 0
            for row in vertical
        ):
            raise ValueError
        roots = report["root_boundaries"]
        if tuple(roots) != _EXPECTED_ROOT_BOUNDARIES or any(
            row["boundary_preserved"] is not True or row["violation_count"] != 0
            for row in roots
        ) or roots[-1]["boundary"] != "cross-root reviewer is advisory and not a fourth Root":
            raise ValueError
        causal = report["semantic_to_contract_causal_binding_v0_1"]
        selection_input = _expected_selection_input(report)
        if (
            not isinstance(deterministic_result, _Mapping)
            or type(ledger_source_bundle)
            is not _ledger_collector.AirlineTransactionArtifactLedgerSourceBundleV01
            or ledger_source_bundle.causal_report.transaction_id
            != _binding.TRANSACTION_ID
        ):
            raise ValueError
        expected_causal = _lane._causal_binding_section(
            ledger_source_bundle.causal_report,
            bsep_packet=bsep_packet,
            airline_bsep_projection=report["bsep_side_projections"][
                "airline_bsep_projection"
            ],
            causal_selection_input=selection_input,
        )
        expected_bridge = _lane._semantic_to_contract_bridge_section(
            causal_report=ledger_source_bundle.causal_report,
            deterministic_report=deterministic_result,
            semantic_actor_reports=tuple(actors),
            deterministic_collection_count=1,
            corridor_execution_count=1,
            causal_section=expected_causal,
        )
        expected_deterministic = _lane._integrated_deterministic_summary(
            deterministic_result
        )
        if (
            causal != expected_causal
            or bridge != expected_bridge
            or deterministic != expected_deterministic
            or causal.get("binding_status")
            != _causal.STATUS_LOCAL_MODEL_PASS
            or causal.get("transaction_id") != _binding.TRANSACTION_ID
            or causal.get("source_candidate_set_ref")
            != selection_input.source_candidate_set_ref
            or causal.get("source_candidate_set_snapshot_id")
            != selection_input.source_candidate_set_snapshot_id
            or causal.get("source_candidate_set_digest")
            != selection_input.source_candidate_set_digest
            or tuple(causal.get("visible_candidate_ids", ()))
            != selection_input.visible_candidate_ids
            or tuple(causal.get("airline_valid_candidate_ids", ()))
            != selection_input.airline_valid_candidate_ids
            or tuple(causal.get("client_hard_compatible_candidate_ids", ()))
            != selection_input.client_hard_compatible_candidate_ids
            or causal.get("actual_bsep_packet_id")
            != expected_bsep_packet["bsep_packet_id"]
            or causal.get("actual_airline_bsep_projection_ref")
            != selection_input.source_bsep_projection_ref
            or causal.get("causal_selection_bsep_projection_ref")
            != selection_input.source_bsep_projection_ref
            or causal.get("semantic_recommendation_id") != _binding.OFFER_A_ID
            or causal.get("client_root_selected_offer_id") != _binding.OFFER_A_ID
            or causal.get("airline_root_resolved_offer_id") != _binding.OFFER_A_ID
            or causal.get("hold_contract_offer_id") != _binding.OFFER_A_ID
            or causal.get("precollected_causal_run_count") != 1
            or causal.get("externally_observed_provider_call_count") != 5
            or causal.get("provider_calls_performed_inside_precollected_entrypoint")
            != 0
            or causal.get("duplicate_provider_call_count") != 0
            or causal.get("default_offer_used") is not False
            or causal.get("silent_fallback_used") is not False
            or causal.get("provider_created_authority_count") != 0
            or causal.get("real_world_effects_count") != 0
            or tuple(causal.get("validation_errors", ())) != ()
            or bridge.get("bridge_status") != STATUS_PASS
            or bridge.get("transaction_id") != _binding.TRANSACTION_ID
            or bridge.get("causal_report_validation_accepted") is not True
            or bridge.get("semantic_recommendation_id") != _binding.OFFER_A_ID
            or bridge.get("client_root_selected_offer_id") != _binding.OFFER_A_ID
            or bridge.get("airline_root_resolved_offer_id") != _binding.OFFER_A_ID
            or bridge.get("hold_contract_offer_id") != _binding.OFFER_A_ID
            or bridge.get("deterministic_transaction_offer_id")
            != _binding.OFFER_A_ID
            or bridge.get("deterministic_corridor_offer_id")
            != _binding.OFFER_A_ID
            or bridge.get("all_offer_ids_match") is not True
            or bridge.get("actual_bsep_packet_id")
            != expected_bsep_packet["bsep_packet_id"]
            or bridge.get("actual_airline_bsep_projection_ref")
            != selection_input.source_bsep_projection_ref
            or bridge.get("causal_selection_bsep_projection_ref")
            != selection_input.source_bsep_projection_ref
            or bridge.get("bsep_refs_match") is not True
            or bridge.get("direct_offer_override_used") is not False
            or bridge.get("default_offer_used") is not False
            or bridge.get("silent_fallback_used") is not False
            or bridge.get("provider_created_authority_count") != 0
            or bridge.get("real_world_effects_count") != 0
            or deterministic.get("collection_status") != STATUS_PASS
            or deterministic.get("transaction_id") != _binding.TRANSACTION_ID
            or deterministic.get("selected_offer_id") != _binding.OFFER_A_ID
            or deterministic.get("corridor_final_status") != STATUS_PASS
            or deterministic.get("corridor_execution_count") != 1
            or deterministic.get("real_world_effects_count") != 0
        ):
            raise ValueError
        expected_identity, fresh_ledger_validation, fresh_source_validation = (
            _fresh_ledger_validation(
                ledger_item,
                ledger_source_bundle=ledger_source_bundle,
                ledger_source_validation=ledger_source_validation,
            )
        )
        expected_refs = ledger_source_bundle.expected_source_refs
        deterministic_ledger = getattr(
            deterministic_result,
            "_airline_transaction_artifact_ledger_v0_1",
            None,
        )
        deterministic_summary = deterministic_result.get(
            "airline_transaction_artifact_ledger_integration"
        )
        expected_outer_ledger_summary = dict(deterministic_summary)
        expected_outer_ledger_summary["artifact_written_count"] = 1
        if (
            type(ledger_item) is not _ledger.AirlineTransactionArtifactLedgerV01
            or deterministic_ledger != ledger_item
            or expected_outer_ledger_summary != ledger_summary
            or fresh_source_validation != ledger_source_validation
            or not _ledger_validation_passed(fresh_ledger_validation)
            or ledger_item.validation_status != STATUS_PASS
            or ledger_item.validation_errors != ()
            or tuple(item.artifact_type for item in ledger_item.entries)
            != _ledger.EXPECTED_ARTIFACT_TYPE_SEQUENCE
            or len(ledger_item.entries) != 19
            or ledger_item.entry_count != 19
            or sum(len(item.depends_on) for item in ledger_item.entries) != 29
            or ledger_item.dependency_edge_count != 29
            or ledger_item.root_final_count != 3
            or ledger_item.provider_called_count != 0
            or ledger_item.network_used_count != 0
            or ledger_item.gemini_called_count != 0
            or ledger_item.ledger_created_authority_count != 0
            or ledger_item.ledger_created_permission_count != 0
            or ledger_item.ledger_created_action_count != 0
            or ledger_item.real_world_effects_count != 0
            or ledger_summary.get("integration_status") != STATUS_PASS
            or ledger_summary.get("source_bundle_validation_status") != STATUS_PASS
            or ledger_summary.get("ledger_validation_status") != STATUS_PASS
            or ledger_summary.get("entry_count") != 19
            or ledger_summary.get("dependency_edge_count") != 29
            or ledger_summary.get("root_final_count") != 3
            or ledger_summary.get("transaction_id") != _binding.TRANSACTION_ID
            or ledger_summary.get("ledger_id") != ledger_item.ledger_id
            or ledger_summary.get("selected_offer_id") != _binding.OFFER_A_ID
            or ledger_summary.get("source_run_ref")
            != expected_refs.source_run_ref
            or ledger_summary.get("source_causal_report_ref")
            != expected_refs.source_causal_report_ref
            or ledger_summary.get("source_corridor_report_ref")
            != expected_refs.source_corridor_report_ref
            or ledger_item.source_run_ref != expected_refs.source_run_ref
            or ledger_item.source_causal_report_ref
            != expected_refs.source_causal_report_ref
            or ledger_item.source_corridor_report_ref
            != expected_refs.source_corridor_report_ref
            or tuple(expected_identity.expected_artifact_ids.values())
            != tuple(item.artifact_id for item in ledger_item.entries)
            or ledger_summary.get("ledger_validation_errors") != ()
            or ledger_summary.get("source_bundle_validation_errors") != ()
        ):
            raise ValueError
        if (
            crypto.get("integration_status")
            != _lane.crypto_contracts.STATUS_SELF_CONSISTENT_UNANCHORED
            or crypto.get("source_file_count") != 9
            or crypto.get("source_file_count") + 2 != 11
            or crypto.get("ledger_entry_count") != 19
            or crypto.get("dependency_edge_count") != 29
            or crypto.get("root_final_count") != 3
            or crypto.get("manifest_core_hash")
            != crypto_collection_plain["manifest_core_hash"]
            or crypto.get("chain_tail_hash")
            != crypto_collection_plain["manifest_core"]["chain_tail_hash"]
            or crypto.get("source_package_hash")
            != crypto_collection_plain["manifest_core"]["source_package_hash"]
            or crypto.get("external_anchor_supplied") is not False
            or crypto.get("external_anchor_verified") is not False
            or crypto.get("anchored_pass_claimed") is not False
            or crypto.get("expected_manifest_core_hash") is not None
            or crypto.get("source_package_ref") != _LOGICAL_PACKAGE_REF
            or crypto.get("transaction_id") != _binding.TRANSACTION_ID
            or crypto.get("ledger_id") != ledger_item.ledger_id
            or crypto.get("source_bundle_id")
            != (
                "airline_crypto_artifact_seal_source_bundle:"
                f"{_binding.TRANSACTION_ID}:{_LOGICAL_PACKAGE_REF}"
            )
            or crypto.get("manifest_artifact_ref") != _lane.CRYPTO_MANIFEST_FILE
            or crypto.get("verification_artifact_ref")
            != _lane.CRYPTO_VERIFICATION_FILE
            or _re.fullmatch(r"[0-9a-f]{64}", str(crypto.get("manifest_core_hash")))
            is None
            or _re.fullmatch(r"[0-9a-f]{64}", str(crypto.get("chain_tail_hash")))
            is None
            or _re.fullmatch(r"[0-9a-f]{64}", str(crypto.get("source_package_hash")))
            is None
            or crypto.get("signature_mode") != "UNSIGNED_PLACEHOLDER"
            or crypto.get("signature_verified") is not False
            or crypto.get("source_bytes_unchanged_after_audit") is not True
            or crypto.get("source_bytes_unchanged_after_collection") is not True
            or crypto.get("source_bytes_unchanged_after_write") is not True
            or crypto.get("source_summary_frozen_before_crypto") is not True
            or crypto.get("source_summary_rewritten_after_crypto") is not False
            or crypto.get("validation_errors") != ()
            or any(
                crypto.get(field_name) != 1
                for field_name in (
                    "e1_audit_count",
                    "source_bundle_validation_count",
                    "manifest_core_collection_count",
                    "envelope_collection_count",
                    "post_collection_snapshot_provider_call_count",
                    "verification_count",
                    "manifest_artifact_written_count",
                    "verification_artifact_written_count",
                )
            )
            or any(
                crypto.get(field_name) != 0
                for field_name in (
                    "audit_rerun_count",
                    "ledger_recollection_count",
                    "semantic_rerun_count",
                    "corridor_rerun_count",
                    "provider_calls_added_by_crypto_count",
                    "network_calls_added_by_crypto_count",
                    "gemini_calls_added_by_crypto_count",
                    "crypto_created_authority_count",
                    "crypto_created_permission_count",
                    "crypto_created_action_count",
                    "real_world_effects_count",
                )
            )
        ):
            raise ValueError
        secret_scan = report["secret_scan"]
        if secret_scan.get("passed") is not True or tuple(secret_scan.get("matched_markers", ())) != ():
            raise _RunnerFailure(REASON_SECRET_SCAN_FAILED, "secret_scan")
    except _RunnerFailure:
        raise
    except Exception:
        raise _RunnerFailure(REASON_SOURCE_GEOMETRY_INVALID, "source_validation") from None


def _validate_raw_evidence_v01(
    *,
    root: _Path,
    root_identity: tuple[int, int],
    report: _Mapping[str, object],
    capture: _CanonicalCollectionCapture,
) -> tuple[int, int]:
    try:
        ledger_item = report["airline_transaction_artifact_ledger_v0_1"]
        if ledger_item != capture.ledger_item:
            raise ValueError
        expected_identity, ledger_validation, _ = _fresh_ledger_validation(
            ledger_item,
            ledger_source_bundle=capture.ledger_source_bundle,
            ledger_source_validation=capture.ledger_source_validation,
        )
        if not _ledger_validation_passed(ledger_validation):
            raise ValueError
        crypto_source_bundle = capture.crypto_source_bundle
        collection_result = capture.crypto_collection_result
        if (
            type(crypto_source_bundle)
            is not _crypto_collector.AirlineCryptoArtifactSealSourceBundleV01
            or type(collection_result)
            is not _crypto_collector.AirlineCryptoArtifactSealCollectionResultV01
            or crypto_source_bundle.ledger_item != ledger_item
            or crypto_source_bundle.expected_identity != expected_identity
        ):
            raise ValueError
        source_validation = (
            _crypto_collector.validate_airline_crypto_artifact_seal_source_bundle_v01(
                crypto_source_bundle
            )
        )
        collection_validation = (
            _crypto_collector.validate_airline_crypto_artifact_seal_collection_result_v01(
                collection_result
            )
        )
        if (
            source_validation.validation_status != STATUS_PASS
            or source_validation.validation_errors != ()
            or collection_validation.validation_status != STATUS_PASS
            or collection_validation.validation_errors != ()
            or collection_result.collection_status
            != _crypto_contracts.STATUS_SELF_CONSISTENT_UNANCHORED
            or collection_result.expected_manifest_core_hash is not None
            or collection_result.manifest_core is None
            or collection_result.envelope is None
            or collection_result.verification_report is None
        ):
            raise ValueError
        collection_plain = (
            _crypto_collector.airline_crypto_artifact_seal_collection_result_to_plain_dict_v01(
                collection_result
            )
        )
        ledger_plain = (
            _crypto_collector.airline_crypto_artifact_seal_ledger_document_to_plain_dict_v01(
                ledger_item,
                expected_identity=expected_identity,
            )
        )
        expected_ledger_bytes = _json.dumps(
            ledger_plain,
            indent=2,
            sort_keys=True,
        ).encode("utf-8")
        expected_manifest_bytes = (
            _json.dumps(
                collection_plain["envelope"],
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            ).encode("utf-8")
            + b"\n"
        )
        expected_verification_bytes = (
            _json.dumps(
                collection_plain["verification_report"],
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            ).encode("utf-8")
            + b"\n"
        )
        source_before = crypto_source_bundle.ordered_source_files_before_audit
        source_after = crypto_source_bundle.ordered_source_files_after_audit
        if (
            source_before != source_after
            or len(source_before) != 9
            or tuple(name for name, _ in source_before)
            != _crypto_contracts.REQUIRED_SOURCE_FILE_REFS
            or dict(source_before).get(_RAW_LEDGER_FILE) != expected_ledger_bytes
        ):
            raise ValueError
        expected_files = {
            **dict(source_before),
            _lane.CRYPTO_MANIFEST_FILE: expected_manifest_bytes,
            _lane.CRYPTO_VERIFICATION_FILE: expected_verification_bytes,
        }
        current_files, raw_identity = _read_exact_raw_files(
            root,
            root_identity,
            expected_files,
        )
        raw_ledger = _crypto_contracts.parse_airline_crypto_json_object_bytes_v01(
            current_files[_RAW_LEDGER_FILE]
        )
        raw_manifest = _crypto_contracts.parse_airline_crypto_json_object_bytes_v01(
            current_files[_lane.CRYPTO_MANIFEST_FILE]
        )
        raw_verification = (
            _crypto_contracts.parse_airline_crypto_json_object_bytes_v01(
                current_files[_lane.CRYPTO_VERIFICATION_FILE]
            )
        )
        if (
            raw_ledger != ledger_plain
            or raw_manifest != collection_plain["envelope"]
            or raw_verification != collection_plain["verification_report"]
        ):
            raise ValueError
        current_source_files = tuple(
            (name, current_files[name]) for name, _ in source_before
        )
        rebuilt_core = _crypto_contracts.build_airline_crypto_artifact_seal_manifest_core_v01(
            ledger_item,
            ordered_source_files=current_source_files,
            source_package_ref=crypto_source_bundle.source_package_ref,
            source_audit_status=STATUS_PASS,
            secret_scan_passed=True,
            expected_identity=expected_identity,
        )
        rebuilt_hash = (
            _crypto_contracts.hash_airline_crypto_artifact_seal_manifest_core_v01(
                rebuilt_core
            )
        )
        envelope_validation = (
            _crypto_contracts.validate_airline_crypto_artifact_seal_envelope_contract_v01(
                collection_result.envelope
            )
        )
        fresh_verification = _crypto_contracts.verify_airline_crypto_artifact_seal_v01(
            collection_result.envelope,
            ledger_item=ledger_item,
            ordered_source_files_before=current_source_files,
            ordered_source_files_after=current_source_files,
            expected_source_package_ref=crypto_source_bundle.source_package_ref,
            source_audit_status=STATUS_PASS,
            secret_scan_passed=True,
            expected_manifest_core_hash=None,
            expected_identity=expected_identity,
        )
        verification_validation = (
            _crypto_contracts.validate_airline_crypto_artifact_seal_verification_report_v01(
                fresh_verification
            )
        )
        crypto_summary = report["airline_crypto_artifact_seal_integration"]
        if (
            rebuilt_core != collection_result.manifest_core
            or rebuilt_hash != collection_result.manifest_core_hash
            or collection_result.envelope.manifest_core != rebuilt_core
            or collection_result.envelope.manifest_core_hash != rebuilt_hash
            or fresh_verification != collection_result.verification_report
            or envelope_validation.validation_status != STATUS_PASS
            or verification_validation.validation_status != STATUS_PASS
            or fresh_verification.verification_status
            != _crypto_contracts.STATUS_SELF_CONSISTENT_UNANCHORED
            or fresh_verification.external_anchor_supplied is not False
            or fresh_verification.external_anchor_verified is not False
            or fresh_verification.signature_verified is not False
            or crypto_summary.get("manifest_core_hash") != rebuilt_hash
            or crypto_summary.get("chain_tail_hash") != rebuilt_core.chain_tail_hash
            or crypto_summary.get("source_package_hash")
            != rebuilt_core.source_package_hash
            or crypto_summary.get("source_file_count") != len(current_source_files)
            or crypto_summary.get("ledger_entry_count") != 19
            or crypto_summary.get("dependency_edge_count") != 29
            or crypto_summary.get("root_final_count") != 3
        ):
            raise ValueError
        return raw_identity
    except Exception:
        raise _RunnerFailure(
            REASON_SOURCE_GEOMETRY_INVALID,
            "raw_evidence_validation",
        ) from None


def _read_exact_raw_files(
    root: _Path,
    root_identity: tuple[int, int],
    expected_files: _Mapping[str, bytes],
) -> tuple[dict[str, bytes], tuple[int, int]]:
    root_fd = _open_verified_directory(root, root_identity)
    raw_fd = -1
    try:
        raw_entry = _os.stat(
            RAW_ATTEMPT_DIRECTORY,
            dir_fd=root_fd,
            follow_symlinks=False,
        )
        flags = (
            _os.O_RDONLY
            | getattr(_os, "O_DIRECTORY", 0)
            | getattr(_os, "O_NOFOLLOW", 0)
        )
        raw_fd = _OPEN(RAW_ATTEMPT_DIRECTORY, flags, dir_fd=root_fd)
        raw_stat = _FSTAT(raw_fd)
        raw_identity = (raw_stat.st_dev, raw_stat.st_ino)
        if (
            not _stat.S_ISDIR(raw_stat.st_mode)
            or raw_identity != (raw_entry.st_dev, raw_entry.st_ino)
        ):
            raise ValueError
        result: dict[str, bytes] = {}
        for name, expected in expected_files.items():
            before = _os.stat(name, dir_fd=raw_fd, follow_symlinks=False)
            if not _stat.S_ISREG(before.st_mode) or before.st_size != len(expected):
                raise ValueError
            fd = _OPEN(
                name,
                _os.O_RDONLY | getattr(_os, "O_NOFOLLOW", 0),
                dir_fd=raw_fd,
            )
            try:
                opened = _FSTAT(fd)
                identity = (opened.st_dev, opened.st_ino)
                if (
                    not _stat.S_ISREG(opened.st_mode)
                    or identity != (before.st_dev, before.st_ino)
                    or opened.st_size != len(expected)
                ):
                    raise ValueError
                content = _read_bounded(fd, len(expected))
                after = _os.stat(name, dir_fd=raw_fd, follow_symlinks=False)
                if (
                    identity != (after.st_dev, after.st_ino)
                    or after.st_size != len(expected)
                    or content != expected
                ):
                    raise ValueError
                result[name] = content
            finally:
                _close_proven(fd)
        return result, raw_identity
    finally:
        if raw_fd >= 0:
            _close_proven(raw_fd)
        _close_proven(root_fd)


def _safe_ledger_projection(entry: object) -> dict[str, object]:
    return {
        "artifact_id": entry.artifact_id,
        "artifact_type": entry.artifact_type,
        "transaction_id": entry.transaction_id,
        "root_owner": entry.root_owner,
        "authority_class": entry.authority_class,
        "evidence_class": entry.evidence_class,
        "depends_on": list(entry.depends_on),
        "validation_status": STATUS_PASS,
        "real_world_effects_count": entry.real_world_effects_count,
    }


def _validate_public_safe_document(value: object) -> None:
    seen: set[int] = set()

    def visit(item: object, key_name: str | None = None) -> None:
        if item is None or type(item) in (bool, int):
            return
        if type(item) is float:
            if not _math.isfinite(item):
                raise ValueError
            return
        if type(item) is str:
            _validate_public_text(item)
            return
        if type(item) not in (dict, list, tuple):
            raise ValueError
        identity = id(item)
        if identity in seen:
            raise ValueError
        seen.add(identity)
        try:
            if type(item) is dict:
                for key, nested in item.items():
                    if type(key) is not str:
                        raise ValueError
                    _validate_schema_key(key)
                    if key in _SAFE_NEGATIVE_KEYS:
                        if type(nested) is not bool or nested is not _SAFE_NEGATIVE_KEYS[key]:
                            raise ValueError
                    elif any(
                        token in _canonical_key(key)
                        for token in _FORBIDDEN_CANONICAL_KEY_TOKENS
                    ):
                        raise ValueError
                    visit(nested, key)
            else:
                for nested in item:
                    visit(nested, key_name)
        finally:
            seen.remove(identity)

    try:
        visit(value)
        _canonical_json_line(value)
    except Exception:
        raise _RunnerFailure(
            REASON_SAFE_NORMALIZATION_INVALID,
            "safe_projection_privacy",
        ) from None


def _validate_schema_key(value: str) -> None:
    if (
        not value
        or value != _unicodedata.normalize("NFC", value)
        or any(ord(character) < 0x20 or ord(character) > 0x7E for character in value)
    ):
        raise ValueError


def _validate_public_text(value: str) -> None:
    if value != _unicodedata.normalize("NFC", value):
        raise ValueError
    value.encode("utf-8", errors="strict")
    if any(
        character == "\x00"
        or _unicodedata.category(character) in ("Cc", "Cf", "Cs", "Zl", "Zp")
        for character in value
    ):
        raise ValueError
    folded = _unicodedata.normalize("NFKC", value).casefold()
    if (
        "file://" in folded
        or "traceback" in folded
        or "-----begin private key-----" in folded
        or _SENSITIVE_ASSIGNMENT.search(value)
        or _WINDOWS_ABSOLUTE.search(value)
        or _POSIX_ABSOLUTE.search(value)
        or "\\\\" in value
        or value.startswith("//")
        or _MEMORY_ADDRESS.search(value)
        or _OBJECT_REPR.search(value)
    ):
        raise ValueError


def _canonical_key(value: str) -> str:
    return "".join(
        character
        for character in _unicodedata.normalize("NFKC", value).casefold()
        if character.isalnum()
    )


def _scan_success_inventory(
    root: _Path,
    root_identity: tuple[int, int],
    *,
    expected_root_entries: tuple[str, ...],
    expected_raw_identity: tuple[int, int] | None = None,
) -> _InventorySnapshot:
    root_fd = _open_verified_directory(root, root_identity)
    raw_fd = -1
    try:
        names = tuple(sorted(_os.listdir(root_fd)))
        if names != tuple(sorted(expected_root_entries)):
            raise _RunnerFailure(REASON_INVENTORY_INVALID, "private_inventory")
        flags = _os.O_RDONLY | getattr(_os, "O_DIRECTORY", 0) | getattr(_os, "O_NOFOLLOW", 0)
        raw_fd = _OPEN(RAW_ATTEMPT_DIRECTORY, flags, dir_fd=root_fd)
        raw_stat = _FSTAT(raw_fd)
        if not _stat.S_ISDIR(raw_stat.st_mode):
            raise _RunnerFailure(REASON_INVENTORY_INVALID, "private_inventory")
        raw_identity = (raw_stat.st_dev, raw_stat.st_ino)
        raw_entry = _os.stat(
            RAW_ATTEMPT_DIRECTORY,
            dir_fd=root_fd,
            follow_symlinks=False,
        )
        raw_mode = _stat.S_IMODE(raw_stat.st_mode)
        if (
            raw_identity != (raw_entry.st_dev, raw_entry.st_ino)
            or _stat.S_IMODE(raw_entry.st_mode) != raw_mode
        ):
            raise _RunnerFailure(REASON_INVENTORY_INVALID, "private_inventory")
        if expected_raw_identity is not None and raw_identity != expected_raw_identity:
            raise _RunnerFailure(REASON_INVENTORY_INVALID, "private_inventory")
        raw_names = tuple(sorted(_os.listdir(raw_fd)))
        if raw_names != EXPECTED_RAW_ATTEMPT_FILENAMES:
            raise _RunnerFailure(REASON_INVENTORY_INVALID, "private_inventory")
        rows = tuple(_inventory_file(raw_fd, name) for name in raw_names)
        raw_after = _os.stat(
            RAW_ATTEMPT_DIRECTORY,
            dir_fd=root_fd,
            follow_symlinks=False,
        )
        if (
            raw_identity != (raw_after.st_dev, raw_after.st_ino)
            or _stat.S_IMODE(raw_after.st_mode) != raw_mode
        ):
            raise _RunnerFailure(REASON_INVENTORY_INVALID, "private_inventory")
        digest = _inventory_digest(rows)
        return _InventorySnapshot(
            rows,
            digest,
            raw_identity,
            raw_mode,
        )
    except _RunnerFailure:
        raise
    except Exception:
        raise _RunnerFailure(REASON_INVENTORY_INVALID, "private_inventory") from None
    finally:
        if raw_fd >= 0:
            _close_or_runner_failure(raw_fd, REASON_INVENTORY_INVALID, "private_inventory")
        _close_or_runner_failure(root_fd, REASON_INVENTORY_INVALID, "private_inventory")


def _failure_inventory_snapshot(
    root: _Path,
    root_identity: tuple[int, int],
    *,
    allow_generation_gate: bool,
) -> _InventorySnapshot:
    root_fd = _open_verified_directory(root, root_identity)
    raw_fd = -1
    try:
        names = frozenset(_os.listdir(root_fd))
        allowed = {
            ATTEMPT_IDENTITY_FILE,
            RAW_ATTEMPT_DIRECTORY,
            PRIVATE_INVENTORY_FILE,
        }
        if allow_generation_gate:
            allowed.add(GENERATION_GATE_FILE)
        if ATTEMPT_IDENTITY_FILE not in names or not names <= allowed:
            raise ValueError
        if RAW_ATTEMPT_DIRECTORY not in names:
            return _InventorySnapshot((), _inventory_digest(()), (0, 0), 0)
        before = _os.stat(
            RAW_ATTEMPT_DIRECTORY,
            dir_fd=root_fd,
            follow_symlinks=False,
        )
        if not _stat.S_ISDIR(before.st_mode):
            raise ValueError
        flags = (
            _os.O_RDONLY
            | getattr(_os, "O_DIRECTORY", 0)
            | getattr(_os, "O_NOFOLLOW", 0)
        )
        raw_fd = _OPEN(RAW_ATTEMPT_DIRECTORY, flags, dir_fd=root_fd)
        opened = _FSTAT(raw_fd)
        identity = (opened.st_dev, opened.st_ino)
        raw_mode = _stat.S_IMODE(opened.st_mode)
        if (
            not _stat.S_ISDIR(opened.st_mode)
            or identity != (before.st_dev, before.st_ino)
            or _stat.S_IMODE(before.st_mode) != raw_mode
        ):
            raise ValueError
        rows = tuple(
            _inventory_file(raw_fd, name)
            for name in sorted(_os.listdir(raw_fd))
        )
        after = _os.stat(
            RAW_ATTEMPT_DIRECTORY,
            dir_fd=root_fd,
            follow_symlinks=False,
        )
        if (
            identity != (after.st_dev, after.st_ino)
            or _stat.S_IMODE(after.st_mode) != raw_mode
        ):
            raise ValueError
        return _InventorySnapshot(
            rows,
            _inventory_digest(rows),
            identity,
            raw_mode,
        )
    finally:
        if raw_fd >= 0:
            _close_proven(raw_fd)
        _close_proven(root_fd)


def _inventory_file(directory_fd: int, name: str) -> _InventoryRow:
    if "/" in name or "\\" in name or name in ("", ".", ".."):
        raise ValueError
    before = _os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
    if not _stat.S_ISREG(before.st_mode):
        raise ValueError
    flags = _os.O_RDONLY | getattr(_os, "O_NOFOLLOW", 0)
    fd = _OPEN(name, flags, dir_fd=directory_fd)
    try:
        opened = _FSTAT(fd)
        identity = (opened.st_dev, opened.st_ino)
        if not _stat.S_ISREG(opened.st_mode) or identity != (before.st_dev, before.st_ino):
            raise ValueError
        content = _read_all(fd)
        after = _os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
        if identity != (after.st_dev, after.st_ino) or len(content) != opened.st_size:
            raise ValueError
        return _InventoryRow(name, _sha256(content), len(content), *identity)
    finally:
        _close_proven(fd)


def _inventory_digest(rows: tuple[_InventoryRow, ...]) -> str:
    plain = [
        {
            "logical_ref": row.logical_ref,
            "sha256": row.sha256,
            "byte_count": row.byte_count,
        }
        for row in rows
    ]
    return _sha256(_canonical_json_bytes_v01(plain))


def _inventory_plain(
    snapshot: _InventorySnapshot,
    status: str,
    *,
    attempt_number: int = 1,
    attempt_id: str = "",
) -> dict[str, object]:
    plain: dict[str, object] = {
        "inventory_version": "v0.1",
        "validation_status": status,
        "raw_attempt_file_count": len(snapshot.rows),
        "ordered_files": [
            {
                "logical_ref": row.logical_ref,
                "sha256": row.sha256,
                "byte_count": row.byte_count,
            }
            for row in snapshot.rows
        ],
        "aggregate_inventory_digest": snapshot.digest,
        "raw_bodies_copied_to_public_evidence": False,
    }
    if attempt_number in (2, 3):
        plain["attempt_number"] = attempt_number
        plain["attempt_id"] = attempt_id
    return plain


def _gate_id_for_attempt(attempt_number: int) -> str:
    return ATTEMPT_03_GATE_ID if attempt_number == 3 else GATE_ID


def _predecessor_proof_sha256(
    proof: _PriorAttemptProof | _Attempt02Proof,
) -> str:
    def document(item: _PrivateDocumentProof) -> dict[str, object]:
        return {
            "leaf": item.leaf,
            "identity": list(item.identity),
            "sha256": item.sha256,
            "byte_count": item.byte_count,
        }

    plain: dict[str, object] = {
        "root_identity": list(proof.root_identity),
        "root_mode": proof.root_mode,
        "raw_directory_identity": list(proof.raw_directory_identity),
        "raw_directory_mode": proof.raw_directory_mode,
        "attempt_identity": document(proof.attempt_identity),
        "private_inventory": document(proof.private_inventory),
        "generation_gate": document(proof.generation_gate),
        "raw_rows": [
            {
                "logical_ref": row.logical_ref,
                "sha256": row.sha256,
                "byte_count": row.byte_count,
                "device": row.device,
                "inode": row.inode,
            }
            for row in proof.raw_rows
        ],
        "raw_modes": [list(item) for item in proof.raw_modes],
        "inventory_digest": proof.inventory_digest,
        "summary_sha256": proof.summary_sha256,
        "validation_sha256": proof.validation_sha256,
    }
    if isinstance(proof, _Attempt02Proof):
        plain["embedded_attempt_01_projection"] = list(
            proof.embedded_attempt_01_projection
        )
    return _sha256(_canonical_json_bytes_v01(plain))


def _build_attempt_identity(
    *,
    execution_mode: str,
    execution_head: str,
    attempt_number: int,
    private_output_directory: _Path,
    prior_proof: _PriorAttemptProof | None = None,
    attempt_02_proof: _Attempt02Proof | None = None,
) -> dict[str, object]:
    output_directory_text = str(private_output_directory)
    attempt_02 = attempt_number == 2
    attempt_03 = attempt_number == 3
    suffix = ":attempt_03" if attempt_03 else ":attempt_02" if attempt_02 else ""
    run_id = f"{_lane.RUN_ID}{suffix}"
    report_id = f"{_lane.REPORT_ID}{suffix}"
    source_task_id = (
        f"{_SOURCE_TASK_ID}{suffix}" if suffix else _SOURCE_TASK_ID
    )
    package_id = f"{_PACKAGE_ID}{suffix}" if suffix else _PACKAGE_ID
    logical_package_ref = (
        f"{_LOGICAL_PACKAGE_REF}{suffix}" if suffix else _LOGICAL_PACKAGE_REF
    )
    output_directory_ref = (
        f"airline/{_lane.RUN_ID}/attempt_{attempt_number:02d}/sealed_evidence"
        if suffix
        else _LOGICAL_OUTPUT_DIRECTORY_REF
    )
    plain: dict[str, object] = {
        "attempt_version": "v0.1",
        "programme_id": PROGRAMME_ID,
        "programme_version": PROGRAMME_VERSION,
        "gate_id": _gate_id_for_attempt(attempt_number),
        "domain_id": DOMAIN_ID,
        "execution_head": execution_head,
        "attempt_number": attempt_number,
        "run_id": run_id,
        "report_id": report_id,
        "source_task_id": source_task_id,
        "package_id": package_id,
        "logical_package_ref": logical_package_ref,
        "output_directory": output_directory_text,
        "output_directory_sha256": _sha256(output_directory_text.encode("utf-8")),
        "output_directory_ref": output_directory_ref,
        "provider_mode": execution_mode,
        "model_id": MODEL_ID,
        "expected_actor_count": 12,
        "provider_call_budget": 12 if execution_mode == MODE_REAL else 0,
        "private_logical_refs": [
            ATTEMPT_IDENTITY_FILE,
            RAW_ATTEMPT_DIRECTORY,
            PRIVATE_INVENTORY_FILE,
            GENERATION_GATE_FILE,
        ],
        "output_identity": (
            CANONICAL_SAFE_REPORT_REF
            if execution_mode == MODE_REAL
            else "injected_safe_execution_report_v01.json"
        ),
        "live_collection_performed": False,
        "official_evidence_eligible": False,
        "retry_count": 0,
        "provider_application_call_mode": _PROVIDER_APPLICATION_CALL_MODE,
    }
    if attempt_02:
        if prior_proof is None:
            raise ValueError
        plain.update(
            {
                "prior_attempt_id": _PRIOR_ANCHORS.attempt_id,
                "prior_execution_head": _PRIOR_ANCHORS.execution_head,
                "prior_attempt_identity_sha256": prior_proof.attempt_identity.sha256,
                "prior_private_inventory_sha256": prior_proof.private_inventory.sha256,
                "prior_private_inventory_digest": prior_proof.inventory_digest,
                "prior_generation_gate_sha256": prior_proof.generation_gate.sha256,
                "prior_failure_reason": REASON_COLLECTOR_FAILED,
                "prior_failed_stage": "collector_result",
                "prior_actual_external_operation_status": _EXTERNAL_UNVERIFIED_PARTIAL,
                "prior_conservative_callback_consumption": 3,
                "new_provider_call_ceiling": 12,
                "cumulative_airline_call_ceiling": 15,
                "owner_reviewed_attempt_02": True,
                "frozen_source_run_id": _lane.RUN_ID,
                "frozen_source_report_id": _lane.REPORT_ID,
            }
        )
    elif attempt_03:
        if prior_proof is None or attempt_02_proof is None:
            raise ValueError
        plain.update(
            {
                "prior_attempt_id": _ATTEMPT_02_ANCHORS.attempt_id,
                "prior_execution_head": _ATTEMPT_02_ANCHORS.execution_head,
                "prior_attempt_identity_sha256": attempt_02_proof.attempt_identity.sha256,
                "prior_private_inventory_sha256": attempt_02_proof.private_inventory.sha256,
                "prior_private_inventory_digest": attempt_02_proof.inventory_digest,
                "prior_generation_gate_sha256": attempt_02_proof.generation_gate.sha256,
                "prior_summary_sha256": attempt_02_proof.summary_sha256,
                "prior_validation_sha256": attempt_02_proof.validation_sha256,
                "prior_complete_proof_sha256": _predecessor_proof_sha256(
                    attempt_02_proof
                ),
                "prior_failure_reason": REASON_COLLECTOR_FAILED,
                "prior_failed_stage": "collector_result",
                "prior_semantic_reason": _ATTEMPT_02_SEMANTIC_REASON,
                "prior_conservative_callback_consumption": 3,
                "transitive_attempt_id": _PRIOR_ANCHORS.attempt_id,
                "transitive_execution_head": _PRIOR_ANCHORS.execution_head,
                "transitive_attempt_identity_sha256": prior_proof.attempt_identity.sha256,
                "transitive_private_inventory_sha256": prior_proof.private_inventory.sha256,
                "transitive_private_inventory_digest": prior_proof.inventory_digest,
                "transitive_generation_gate_sha256": prior_proof.generation_gate.sha256,
                "transitive_complete_proof_sha256": _predecessor_proof_sha256(
                    prior_proof
                ),
                "transitive_failure_reason": REASON_COLLECTOR_FAILED,
                "transitive_failed_stage": "collector_result",
                "transitive_conservative_callback_consumption": 3,
                "transitive_equality_verified": True,
                "prior_embedded_transitive_projection_sha256": _sha256(
                    _canonical_json_bytes_v01(
                        list(attempt_02_proof.embedded_attempt_01_projection)
                    )
                ),
                "new_provider_call_ceiling": 12,
                "cumulative_airline_call_ceiling": 18,
                "supplier_accepted_budget": 6,
                "cumulative_programme_call_ceiling": 24,
                "owner_reviewed_attempt_03": True,
                "frozen_source_run_id": _lane.RUN_ID,
                "frozen_source_report_id": _lane.REPORT_ID,
            }
        )
    plain["attempt_id"] = _sha256(
        (
            b"hedgehog.a1.airline.attempt.v03\0"
            if attempt_03
            else b"hedgehog.a1.airline.attempt.v02\0"
            if attempt_02
            else b"hedgehog.a1.airline.attempt.v01\0"
        )
        + _canonical_json_bytes_v01(plain)
    )
    return plain


def _generation_gate_plain(
    *,
    attempt_plain: dict[str, object],
    attempt_identity_sha256: str,
    final_status: str,
    reason_code: str,
    failed_stage: str,
    safe_execution_id: str,
    safe_report_sha256: str,
    inventory_digest: str,
    private_inventory_sha256: str,
    execution_mode: str,
    attempt_number: int,
    callback_observed: tuple[str, ...],
    base_calls_started: tuple[str, ...],
    base_calls_completed: tuple[str, ...],
    publication_state: str,
) -> dict[str, object]:
    accepted = final_status == STATUS_PASS
    real = execution_mode == MODE_REAL
    plain = {
        "generation_gate_version": "v0.1",
        "attempt_id": attempt_plain["attempt_id"],
        "attempt_identity_sha256": attempt_identity_sha256,
        "attempt_number": attempt_plain["attempt_number"],
        "execution_head": attempt_plain["execution_head"],
        "run_id": attempt_plain["run_id"],
        "report_id": attempt_plain["report_id"],
        "source_task_id": attempt_plain["source_task_id"],
        "private_output_directory_sha256": attempt_plain[
            "output_directory_sha256"
        ],
        "package_id": attempt_plain["package_id"],
        "logical_package_ref": attempt_plain["logical_package_ref"],
        "output_directory_ref": attempt_plain["output_directory_ref"],
        "final_source_status": final_status,
        "failed_stage": failed_stage,
        "reason_code": reason_code,
        "safe_execution_id": safe_execution_id,
        "safe_report_sha256": safe_report_sha256,
        "private_inventory_digest": inventory_digest,
        "private_inventory_document_sha256": private_inventory_sha256,
        "exact_actor_geometry_verified": accepted,
        "preference_a_verified": accepted,
        "corridor_ledger_crypto_verified": accepted,
        "secret_scan_passed": accepted,
        "live_collection_performed": real and bool(base_calls_started),
        "official_evidence_eligible": accepted and real,
        "public_safe_report_state": publication_state,
        "provider_mode": (
            _lane.PROVIDER_MODE_REAL if real else _lane.PROVIDER_MODE_FAKE
        ),
        "provider_application_call_mode": _PROVIDER_APPLICATION_CALL_MODE,
        "wrapper_callback_observed_count": len(callback_observed),
        "provider_callback_started_count": len(base_calls_started),
        "provider_callback_completed_count": len(base_calls_completed),
        "observed_actor_prefix": list(callback_observed),
        "wrapper_callback_observed_prefix": list(callback_observed),
        "base_provider_started_prefix": list(base_calls_started),
        "base_provider_completed_prefix": list(base_calls_completed),
        "injected_callback_count": len(base_calls_started) if not real else 0,
        "actual_provider_call_count": len(base_calls_started) if real else 0,
        "actual_network_call_count": (
            len(base_calls_started) if accepted and real else 0
        ),
        "actual_gemini_call_count": (
            len(base_calls_started) if accepted and real else 0
        ),
        "actual_external_operation_status": (
            _EXTERNAL_VERIFIED
            if accepted and real
            else _EXTERNAL_UNVERIFIED_PARTIAL
            if real and base_calls_started
            else _EXTERNAL_NOT_PERFORMED
        ),
        "actual_real_world_effects_count": 0,
        "retry_count": 0,
        "package_created_count": 0,
        "anchor_created_count": 0,
        "replay_created_count": 0,
    }
    if attempt_number == 3:
        plain["gate_id"] = attempt_plain["gate_id"]
    if attempt_number in (2, 3):
        keys = (
            "prior_attempt_id",
            "prior_execution_head",
            "prior_attempt_identity_sha256",
            "prior_private_inventory_sha256",
            "prior_private_inventory_digest",
            "prior_generation_gate_sha256",
            "prior_failure_reason",
            "prior_failed_stage",
            "prior_conservative_callback_consumption",
            "new_provider_call_ceiling",
            "cumulative_airline_call_ceiling",
        )
        if attempt_number == 2:
            keys += (
                "prior_actual_external_operation_status",
                "owner_reviewed_attempt_02",
            )
        else:
            keys += (
                "prior_summary_sha256",
                "prior_validation_sha256",
                "prior_complete_proof_sha256",
                "prior_semantic_reason",
                "transitive_attempt_id",
                "transitive_execution_head",
                "transitive_attempt_identity_sha256",
                "transitive_private_inventory_sha256",
                "transitive_private_inventory_digest",
                "transitive_generation_gate_sha256",
                "transitive_complete_proof_sha256",
                "transitive_failure_reason",
                "transitive_failed_stage",
                "transitive_conservative_callback_consumption",
                "transitive_equality_verified",
                "prior_embedded_transitive_projection_sha256",
                "supplier_accepted_budget",
                "cumulative_programme_call_ceiling",
                "owner_reviewed_attempt_03",
            )
        for key in keys:
            plain[key] = attempt_plain[key]
    return plain


def _preserve_failed_private_attempt(
    *,
    root: _Path,
    root_identity: tuple[int, int],
    attempt_plain: dict[str, object],
    attempt_proof: _PrivateDocumentProof,
    reason_code: str,
    failed_stage: str,
    execution_mode: str,
    callback_observed: tuple[str, ...],
    base_calls_started: tuple[str, ...],
    base_calls_completed: tuple[str, ...],
    safe_execution_id: str,
    safe_report_sha256: str,
    publication_state: str,
    before_generation_gate: _Callable[[], tuple[str, str] | None] | None = None,
) -> tuple[str, str]:
    try:
        _revalidate_private_document(
            root,
            root_identity,
            attempt_proof,
            attempt_plain,
        )
        snapshot = _failure_inventory_snapshot(
            root,
            root_identity,
            allow_generation_gate=False,
        )
        if _FAILURE_PRESERVATION_HOOK is not None:
            _FAILURE_PRESERVATION_HOOK(root)
        repeated = _failure_inventory_snapshot(
            root,
            root_identity,
            allow_generation_gate=False,
        )
        if repeated != snapshot:
            raise ValueError
        digest = snapshot.digest
        failed_inventory_plain = _inventory_plain(
            snapshot,
            STATUS_FAIL_CLOSED,
            attempt_number=int(attempt_plain["attempt_number"]),
            attempt_id=str(attempt_plain["attempt_id"]),
        )
        passed_inventory_plain = _inventory_plain(
            snapshot,
            STATUS_PASS,
            attempt_number=int(attempt_plain["attempt_number"]),
            attempt_id=str(attempt_plain["attempt_id"]),
        )
        if _private_leaf_exists(root, root_identity, PRIVATE_INVENTORY_FILE):
            existing_inventory, inventory_proof = _prove_existing_private_document(
                root,
                root_identity,
                PRIVATE_INVENTORY_FILE,
            )
            if existing_inventory not in (
                failed_inventory_plain,
                passed_inventory_plain,
            ):
                raise ValueError
            inventory_plain = existing_inventory
        else:
            inventory_plain = failed_inventory_plain
            inventory_proof = _write_private_document(
                root,
                root_identity,
                PRIVATE_INVENTORY_FILE,
                inventory_plain,
            )
        after_inventory = _failure_inventory_snapshot(
            root,
            root_identity,
            allow_generation_gate=False,
        )
        if after_inventory != snapshot:
            raise ValueError
        _revalidate_private_document(
            root,
            root_identity,
            attempt_proof,
            attempt_plain,
        )
        _revalidate_private_document(
            root,
            root_identity,
            inventory_proof,
            inventory_plain,
        )
        if before_generation_gate is not None:
            override = before_generation_gate()
            if override is not None:
                reason_code, failed_stage = override
        gate_plain = _generation_gate_plain(
            attempt_plain=attempt_plain,
            attempt_identity_sha256=attempt_proof.sha256,
            final_status=STATUS_FAIL_CLOSED,
            reason_code=reason_code,
            failed_stage=failed_stage,
            safe_execution_id=safe_execution_id,
            safe_report_sha256=safe_report_sha256,
            inventory_digest=digest,
            private_inventory_sha256=inventory_proof.sha256,
            execution_mode=execution_mode,
            attempt_number=int(attempt_plain["attempt_number"]),
            callback_observed=callback_observed,
            base_calls_started=base_calls_started,
            base_calls_completed=base_calls_completed,
            publication_state=publication_state,
        )
        if _private_leaf_exists(root, root_identity, GENERATION_GATE_FILE):
            raise ValueError
        gate_proof = _write_private_document(
            root,
            root_identity,
            GENERATION_GATE_FILE,
            gate_plain,
            expected_root_entries=(
                ATTEMPT_IDENTITY_FILE,
                *((RAW_ATTEMPT_DIRECTORY,) if snapshot.raw_directory_identity != (0, 0) else ()),
                PRIVATE_INVENTORY_FILE,
                GENERATION_GATE_FILE,
            ),
        )
        final_snapshot = _failure_inventory_snapshot(
            root,
            root_identity,
            allow_generation_gate=True,
        )
        if final_snapshot != snapshot:
            raise ValueError
        _revalidate_private_document(
            root,
            root_identity,
            attempt_proof,
            attempt_plain,
        )
        _revalidate_private_document(
            root,
            root_identity,
            inventory_proof,
            inventory_plain,
        )
        _revalidate_private_document(
            root,
            root_identity,
            gate_proof,
            gate_plain,
        )
        return digest, _PRESERVATION_PRESERVED
    except Exception:
        return "", _PRESERVATION_RETAINED_UNPROVED


def _verify_prior_attempt_v01(
    prior_path: _Path,
    supplied_attempt_id: str,
    *,
    current_execution_head: str,
    owned_public_report: _OwnedOutput | None = None,
) -> _PriorAttemptProof:
    """Prove the fixed failed Attempt 01 without reading raw private bodies."""
    root_fd = -1
    raw_fd = -1
    try:
        anchors = _PRIOR_ANCHORS
        if supplied_attempt_id != anchors.attempt_id:
            raise ValueError
        root_fd, root_identity = _open_absolute_directory_nofollow(prior_path)
        root_entries = _scandir_names(root_fd)
        if (
            len(root_entries) != anchors.root_entry_count
            or root_entries
            != tuple(
                sorted(
                    (
                        ATTEMPT_IDENTITY_FILE,
                        RAW_ATTEMPT_DIRECTORY,
                        PRIVATE_INVENTORY_FILE,
                        GENERATION_GATE_FILE,
                    )
                )
            )
        ):
            raise ValueError

        attempt_plain, attempt_proof = _read_prior_json(
            root_fd,
            ATTEMPT_IDENTITY_FILE,
            anchors.metadata_mode,
        )
        inventory_plain, inventory_proof = _read_prior_json(
            root_fd,
            PRIVATE_INVENTORY_FILE,
            anchors.metadata_mode,
        )
        gate_plain, gate_proof = _read_prior_json(
            root_fd,
            GENERATION_GATE_FILE,
            anchors.metadata_mode,
        )
        if (
            attempt_proof.sha256 != anchors.attempt_identity_sha256
            or inventory_proof.sha256 != anchors.private_inventory_sha256
            or gate_proof.sha256 != anchors.generation_gate_sha256
        ):
            raise ValueError
        _validate_prior_attempt_identity(attempt_plain, prior_path, anchors)

        raw_before = _os.stat(
            RAW_ATTEMPT_DIRECTORY,
            dir_fd=root_fd,
            follow_symlinks=False,
        )
        if not _stat.S_ISDIR(raw_before.st_mode):
            raise ValueError
        flags = (
            _os.O_RDONLY
            | getattr(_os, "O_DIRECTORY", 0)
            | getattr(_os, "O_NOFOLLOW", 0)
        )
        raw_fd = _OPEN(RAW_ATTEMPT_DIRECTORY, flags, dir_fd=root_fd)
        raw_identity = _descriptor_identity(raw_fd, directory=True)
        raw_opened = _FSTAT(raw_fd)
        if raw_identity != (raw_before.st_dev, raw_before.st_ino):
            raise ValueError
        raw_names = _scandir_names(raw_fd)
        if len(raw_names) != anchors.raw_file_count:
            raise ValueError
        raw_rows: list[_InventoryRow] = []
        raw_modes: list[tuple[str, int]] = []
        selected: dict[str, bytes] = {}
        selected_names = {
            "summary.json",
            "client_purchase_intent_reviewer_llm_validation.json",
        }
        for name in raw_names:
            row, content, mode = _read_prior_raw_file(raw_fd, name)
            raw_rows.append(row)
            raw_modes.append((name, mode))
            if name in selected_names:
                selected[name] = content
        if set(selected) != selected_names:
            raise ValueError
        raw_after = _os.stat(
            RAW_ATTEMPT_DIRECTORY,
            dir_fd=root_fd,
            follow_symlinks=False,
        )
        if (
            raw_identity != (raw_after.st_dev, raw_after.st_ino)
            or _stat.S_IMODE(raw_after.st_mode) != _stat.S_IMODE(raw_opened.st_mode)
        ):
            raise ValueError
        rows = tuple(raw_rows)
        digest = _inventory_digest(rows)
        if digest != anchors.private_inventory_digest:
            raise ValueError
        _validate_prior_inventory(inventory_plain, rows, anchors)
        _validate_prior_gate(gate_plain, anchors)
        _validate_prior_summary(
            _parse_prior_legacy_source_json(selected["summary.json"]),
            anchors,
        )
        _validate_prior_actor_validation(
            _parse_prior_legacy_source_json(
                selected["client_purchase_intent_reviewer_llm_validation.json"]
            )
        )
        _verify_prior_head_ancestry(anchors.execution_head, current_execution_head)
        if owned_public_report is None:
            if (
                _CANONICAL_SAFE_REPORT_PATH.exists()
                or _CANONICAL_SAFE_REPORT_PATH.is_symlink()
            ):
                raise ValueError
        else:
            if (
                owned_public_report.parent_path / owned_public_report.leaf
                != _CANONICAL_SAFE_REPORT_PATH
            ):
                raise ValueError
            _revalidate_owned_output(
                owned_public_report,
                _strict_json(owned_public_report.expected_bytes),
            )

        root_after = _FSTAT(root_fd)
        if (root_after.st_dev, root_after.st_ino) != root_identity:
            raise ValueError
        return _PriorAttemptProof(
            root_identity=root_identity,
            root_mode=_stat.S_IMODE(root_after.st_mode),
            raw_directory_identity=raw_identity,
            raw_directory_mode=_stat.S_IMODE(raw_opened.st_mode),
            attempt_identity=attempt_proof,
            private_inventory=inventory_proof,
            generation_gate=gate_proof,
            raw_rows=rows,
            raw_modes=tuple(raw_modes),
            inventory_digest=digest,
            summary_sha256=_sha256(selected["summary.json"]),
            validation_sha256=_sha256(
                selected["client_purchase_intent_reviewer_llm_validation.json"]
            ),
        )
    except Exception:
        raise _RunnerFailure(
            REASON_PRIOR_ATTEMPT_INVALID,
            "prior_attempt_verification",
        ) from None
    finally:
        close_failed = False
        if raw_fd >= 0:
            try:
                _close_proven(raw_fd)
            except Exception:
                close_failed = True
        if root_fd >= 0:
            try:
                _close_proven(root_fd)
            except Exception:
                close_failed = True
        if close_failed:
            raise _RunnerFailure(
                REASON_PRIOR_ATTEMPT_INVALID,
                "prior_attempt_verification",
            ) from None


def _require_prior_attempt_unchanged(
    expected: _PriorAttemptProof,
    prior_path: _Path,
    supplied_attempt_id: str,
    *,
    current_execution_head: str,
    owned_public_report: _OwnedOutput | None = None,
) -> None:
    observed = _verify_prior_attempt_v01(
        prior_path,
        supplied_attempt_id,
        current_execution_head=current_execution_head,
        owned_public_report=owned_public_report,
    )
    if observed != expected:
        raise _RunnerFailure(
            REASON_PRIOR_ATTEMPT_CHANGED,
            "prior_attempt_revalidation",
        )


def _verify_attempt_02_v01(
    attempt_02_path: _Path,
    supplied_attempt_id: str,
    *,
    prior_proof: _PriorAttemptProof,
    current_execution_head: str,
    owned_public_report: _OwnedOutput | None = None,
) -> _Attempt02Proof:
    """Prove fixed failed Attempt 02 and its exact Attempt 01 binding."""
    root_fd = -1
    raw_fd = -1
    try:
        anchors = _ATTEMPT_02_ANCHORS
        if supplied_attempt_id != anchors.attempt_id:
            raise ValueError
        root_fd, root_identity = _open_absolute_directory_nofollow(attempt_02_path)
        root_entries = _scandir_names(root_fd)
        expected_root_entries = tuple(
            sorted(
                (
                    ATTEMPT_IDENTITY_FILE,
                    RAW_ATTEMPT_DIRECTORY,
                    PRIVATE_INVENTORY_FILE,
                    GENERATION_GATE_FILE,
                )
            )
        )
        if (
            len(root_entries) != anchors.root_entry_count
            or root_entries != expected_root_entries
        ):
            raise ValueError

        attempt_plain, attempt_proof = _read_prior_json(
            root_fd,
            ATTEMPT_IDENTITY_FILE,
            anchors.metadata_mode,
        )
        inventory_plain, inventory_proof = _read_prior_json(
            root_fd,
            PRIVATE_INVENTORY_FILE,
            anchors.metadata_mode,
        )
        gate_plain, gate_proof = _read_prior_json(
            root_fd,
            GENERATION_GATE_FILE,
            anchors.metadata_mode,
        )
        if (
            attempt_proof.sha256 != anchors.attempt_identity_sha256
            or inventory_proof.sha256 != anchors.private_inventory_sha256
            or gate_proof.sha256 != anchors.generation_gate_sha256
        ):
            raise ValueError
        _validate_attempt_02_identity(
            attempt_plain,
            attempt_02_path,
            anchors,
            prior_proof,
        )

        raw_before = _os.stat(
            RAW_ATTEMPT_DIRECTORY,
            dir_fd=root_fd,
            follow_symlinks=False,
        )
        if not _stat.S_ISDIR(raw_before.st_mode):
            raise ValueError
        flags = (
            _os.O_RDONLY
            | getattr(_os, "O_DIRECTORY", 0)
            | getattr(_os, "O_NOFOLLOW", 0)
        )
        raw_fd = _OPEN(RAW_ATTEMPT_DIRECTORY, flags, dir_fd=root_fd)
        raw_identity = _descriptor_identity(raw_fd, directory=True)
        raw_opened = _FSTAT(raw_fd)
        if raw_identity != (raw_before.st_dev, raw_before.st_ino):
            raise ValueError
        raw_names = _scandir_names(raw_fd)
        if len(raw_names) != anchors.raw_file_count:
            raise ValueError
        raw_rows: list[_InventoryRow] = []
        raw_modes: list[tuple[str, int]] = []
        selected: dict[str, bytes] = {}
        selected_names = {
            "summary.json",
            "client_purchase_intent_reviewer_llm_validation.json",
        }
        for name in raw_names:
            row, content, mode = _read_prior_raw_file(raw_fd, name)
            raw_rows.append(row)
            raw_modes.append((name, mode))
            if name in selected_names:
                selected[name] = content
        if set(selected) != selected_names:
            raise ValueError
        raw_after = _os.stat(
            RAW_ATTEMPT_DIRECTORY,
            dir_fd=root_fd,
            follow_symlinks=False,
        )
        if (
            raw_identity != (raw_after.st_dev, raw_after.st_ino)
            or _stat.S_IMODE(raw_after.st_mode) != _stat.S_IMODE(raw_opened.st_mode)
        ):
            raise ValueError
        rows = tuple(raw_rows)
        digest = _inventory_digest(rows)
        if (
            digest != anchors.private_inventory_digest
            or _sha256(selected["summary.json"]) != anchors.summary_sha256
            or _sha256(
                selected["client_purchase_intent_reviewer_llm_validation.json"]
            )
            != anchors.validation_sha256
        ):
            raise ValueError
        _validate_attempt_02_inventory(inventory_plain, rows, anchors)
        _validate_attempt_02_gate(gate_plain, anchors, prior_proof)
        _validate_attempt_02_summary(
            _parse_prior_legacy_source_json(selected["summary.json"]),
            anchors,
        )
        _validate_attempt_02_actor_validation(
            _parse_prior_legacy_source_json(
                selected["client_purchase_intent_reviewer_llm_validation.json"]
            )
        )
        _verify_prior_head_ancestry(anchors.execution_head, current_execution_head)
        _verify_predecessor_public_state(owned_public_report)
        root_after = _FSTAT(root_fd)
        if (root_after.st_dev, root_after.st_ino) != root_identity:
            raise ValueError
        return _Attempt02Proof(
            root_identity=root_identity,
            root_mode=_stat.S_IMODE(root_after.st_mode),
            raw_directory_identity=raw_identity,
            raw_directory_mode=_stat.S_IMODE(raw_opened.st_mode),
            attempt_identity=attempt_proof,
            private_inventory=inventory_proof,
            generation_gate=gate_proof,
            raw_rows=rows,
            raw_modes=tuple(raw_modes),
            inventory_digest=digest,
            summary_sha256=_sha256(selected["summary.json"]),
            validation_sha256=_sha256(
                selected["client_purchase_intent_reviewer_llm_validation.json"]
            ),
            embedded_attempt_01_projection=_attempt_01_proof_projection(prior_proof),
        )
    except Exception:
        raise _RunnerFailure(
            REASON_ATTEMPT_02_INVALID,
            "attempt_02_predecessor_verification",
        ) from None
    finally:
        close_failed = False
        if raw_fd >= 0:
            try:
                _close_proven(raw_fd)
            except Exception:
                close_failed = True
        if root_fd >= 0:
            try:
                _close_proven(root_fd)
            except Exception:
                close_failed = True
        if close_failed:
            raise _RunnerFailure(
                REASON_ATTEMPT_02_INVALID,
                "attempt_02_predecessor_verification",
            ) from None


def _require_dual_predecessors_unchanged(
    expected_attempt_01: _PriorAttemptProof | None,
    attempt_01_path: _Path | None,
    attempt_01_id: str,
    expected_attempt_02: _Attempt02Proof | None,
    attempt_02_path: _Path | None,
    attempt_02_id: str,
    *,
    current_execution_head: str,
    owned_public_report: _OwnedOutput | None = None,
) -> None:
    if (
        expected_attempt_01 is None
        or attempt_01_path is None
        or expected_attempt_02 is None
        or attempt_02_path is None
    ):
        raise _RunnerFailure(REASON_ATTEMPT_02_CHANGED, "dual_predecessor_revalidation")
    try:
        observed_attempt_01 = _verify_prior_attempt_v01(
            attempt_01_path,
            attempt_01_id,
            current_execution_head=current_execution_head,
            owned_public_report=owned_public_report,
        )
    except _RunnerFailure:
        raise _RunnerFailure(
            REASON_PRIOR_ATTEMPT_CHANGED,
            "prior_attempt_revalidation",
        ) from None
    if observed_attempt_01 != expected_attempt_01:
        raise _RunnerFailure(
            REASON_PRIOR_ATTEMPT_CHANGED,
            "prior_attempt_revalidation",
        )
    try:
        observed_attempt_02 = _verify_attempt_02_v01(
            attempt_02_path,
            attempt_02_id,
            prior_proof=observed_attempt_01,
            current_execution_head=current_execution_head,
            owned_public_report=owned_public_report,
        )
    except _RunnerFailure:
        raise _RunnerFailure(
            REASON_ATTEMPT_02_CHANGED,
            "attempt_02_predecessor_revalidation",
        ) from None
    if observed_attempt_02 != expected_attempt_02:
        raise _RunnerFailure(
            REASON_ATTEMPT_02_CHANGED,
            "attempt_02_predecessor_revalidation",
        )


def _verify_predecessor_public_state(
    owned_public_report: _OwnedOutput | None,
) -> None:
    if owned_public_report is None:
        if (
            _CANONICAL_SAFE_REPORT_PATH.exists()
            or _CANONICAL_SAFE_REPORT_PATH.is_symlink()
        ):
            raise ValueError
        return
    if (
        owned_public_report.parent_path / owned_public_report.leaf
        != _CANONICAL_SAFE_REPORT_PATH
    ):
        raise ValueError
    _revalidate_owned_output(
        owned_public_report,
        _strict_json(owned_public_report.expected_bytes),
    )


def _open_absolute_directory_nofollow(path: _Path) -> tuple[int, tuple[int, int]]:
    _validate_raw_absolute_path_text(str(path))
    current_fd = _OPEN(
        "/",
        _os.O_RDONLY | getattr(_os, "O_DIRECTORY", 0),
    )
    try:
        for component in path.parts[1:]:
            flags = (
                _os.O_RDONLY
                | getattr(_os, "O_DIRECTORY", 0)
                | getattr(_os, "O_NOFOLLOW", 0)
            )
            next_fd = _OPEN(component, flags, dir_fd=current_fd)
            try:
                opened = _FSTAT(next_fd)
                entry = _os.stat(
                    component,
                    dir_fd=current_fd,
                    follow_symlinks=False,
                )
                if (
                    not _stat.S_ISDIR(opened.st_mode)
                    or (opened.st_dev, opened.st_ino)
                    != (entry.st_dev, entry.st_ino)
                ):
                    raise ValueError
            except Exception:
                _close_proven(next_fd)
                raise
            _close_proven(current_fd)
            current_fd = next_fd
        return current_fd, _descriptor_identity(current_fd, directory=True)
    except Exception:
        if current_fd >= 0:
            _close_proven(current_fd)
        raise


def _scandir_names(directory_fd: int) -> tuple[str, ...]:
    names: list[str] = []
    with _os.scandir(directory_fd) as entries:
        for entry in entries:
            if entry.name in ("", ".", "..") or "/" in entry.name or "\\" in entry.name:
                raise ValueError
            names.append(entry.name)
    return tuple(sorted(names))


def _read_prior_json(
    directory_fd: int,
    leaf: str,
    expected_mode: int,
) -> tuple[dict[str, object], _PrivateDocumentProof]:
    content, identity, mode = _read_prior_file(directory_fd, leaf, 2_000_000)
    if mode != expected_mode:
        raise ValueError
    parsed = _strict_json(content)
    if type(parsed) is not dict or _canonical_json_line(parsed) != content:
        raise ValueError
    return parsed, _PrivateDocumentProof(
        leaf=leaf,
        identity=identity,
        expected_bytes=content,
        sha256=_sha256(content),
        byte_count=len(content),
    )


def _read_prior_raw_file(
    directory_fd: int,
    leaf: str,
) -> tuple[_InventoryRow, bytes, int]:
    content, identity, mode = _read_prior_file(directory_fd, leaf, 16_000_000)
    return (
        _InventoryRow(leaf, _sha256(content), len(content), *identity),
        content,
        mode,
    )


def _read_prior_file(
    directory_fd: int,
    leaf: str,
    maximum_bytes: int,
) -> tuple[bytes, tuple[int, int], int]:
    if (
        type(leaf) is not str
        or leaf in ("", ".", "..")
        or "/" in leaf
        or "\\" in leaf
    ):
        raise ValueError
    before = _os.stat(leaf, dir_fd=directory_fd, follow_symlinks=False)
    if not _stat.S_ISREG(before.st_mode) or not 0 <= before.st_size <= maximum_bytes:
        raise ValueError
    flags = _os.O_RDONLY | getattr(_os, "O_NOFOLLOW", 0)
    fd = _OPEN(leaf, flags, dir_fd=directory_fd)
    try:
        opened = _FSTAT(fd)
        identity = _descriptor_identity(fd, directory=False)
        if (
            identity != (before.st_dev, before.st_ino)
            or opened.st_size != before.st_size
        ):
            raise ValueError
        content = _read_bounded(fd, opened.st_size)
        after = _os.stat(leaf, dir_fd=directory_fd, follow_symlinks=False)
        if (
            identity != (after.st_dev, after.st_ino)
            or after.st_size != len(content)
            or _stat.S_IMODE(after.st_mode) != _stat.S_IMODE(opened.st_mode)
        ):
            raise ValueError
        return content, identity, _stat.S_IMODE(opened.st_mode)
    finally:
        _close_proven(fd)


def _validate_prior_attempt_identity(
    plain: dict[str, object],
    prior_path: _Path,
    anchors: _PriorAttemptAnchors,
) -> None:
    expected = {
        "programme_id": PROGRAMME_ID,
        "domain_id": DOMAIN_ID,
        "execution_head": anchors.execution_head,
        "attempt_number": 1,
        "attempt_id": anchors.attempt_id,
        "run_id": _lane.RUN_ID,
        "report_id": _lane.REPORT_ID,
        "source_task_id": _SOURCE_TASK_ID,
        "package_id": _PACKAGE_ID,
        "logical_package_ref": _LOGICAL_PACKAGE_REF,
        "output_directory": str(prior_path),
        "provider_mode": MODE_REAL,
        "model_id": MODEL_ID,
        "expected_actor_count": 12,
        "provider_call_budget": 12,
        "retry_count": 0,
    }
    if any(plain.get(key) != value for key, value in expected.items()):
        raise ValueError
    identity_payload = dict(plain)
    identity_payload.pop("attempt_id", None)
    computed = _sha256(
        b"hedgehog.a1.airline.attempt.v01\0"
        + _canonical_json_bytes_v01(identity_payload)
    )
    if computed != anchors.attempt_id:
        raise ValueError


def _validate_prior_inventory(
    plain: dict[str, object],
    rows: tuple[_InventoryRow, ...],
    anchors: _PriorAttemptAnchors,
) -> None:
    expected_rows = [
        {
            "logical_ref": row.logical_ref,
            "sha256": row.sha256,
            "byte_count": row.byte_count,
        }
        for row in rows
    ]
    if (
        plain.get("validation_status") != STATUS_FAIL_CLOSED
        or plain.get("raw_attempt_file_count") != anchors.raw_file_count
        or plain.get("aggregate_inventory_digest") != anchors.private_inventory_digest
        or plain.get("ordered_files") != expected_rows
        or plain.get("raw_bodies_copied_to_public_evidence") is not False
    ):
        raise ValueError


def _validate_prior_gate(
    plain: dict[str, object],
    anchors: _PriorAttemptAnchors,
) -> None:
    expected = {
        "attempt_id": anchors.attempt_id,
        "attempt_identity_sha256": anchors.attempt_identity_sha256,
        "attempt_number": 1,
        "execution_head": anchors.execution_head,
        "final_source_status": STATUS_FAIL_CLOSED,
        "failed_stage": "collector_result",
        "reason_code": REASON_COLLECTOR_FAILED,
        "private_inventory_digest": anchors.private_inventory_digest,
        "private_inventory_document_sha256": anchors.private_inventory_sha256,
        "live_collection_performed": True,
        "official_evidence_eligible": False,
        "public_safe_report_state": _PUBLICATION_ABSENT,
        "provider_mode": _lane.PROVIDER_MODE_REAL,
        "wrapper_callback_observed_count": 3,
        "provider_callback_started_count": 3,
        "provider_callback_completed_count": 3,
        "actual_provider_call_count": 3,
        "actual_network_call_count": 0,
        "actual_gemini_call_count": 0,
        "actual_external_operation_status": _EXTERNAL_UNVERIFIED_PARTIAL,
        "actual_real_world_effects_count": 0,
        "retry_count": 0,
        "package_created_count": 0,
        "anchor_created_count": 0,
        "replay_created_count": 0,
    }
    if any(plain.get(key) != value for key, value in expected.items()):
        raise ValueError
    for key in (
        "observed_actor_prefix",
        "wrapper_callback_observed_prefix",
        "base_provider_started_prefix",
        "base_provider_completed_prefix",
    ):
        if tuple(plain.get(key, ())) != anchors.callback_prefix:
            raise ValueError


def _validate_prior_summary(
    plain: object,
    anchors: _PriorAttemptAnchors,
) -> None:
    if type(plain) is not dict:
        raise ValueError
    permitted = {
        "final_status",
        "failed_actor_id",
        "failed_stage",
        "validation_errors",
        "semantic_actor_call_order",
        "counter_table",
    }
    selected = {key: plain.get(key) for key in permitted}
    counters = selected["counter_table"]
    if type(counters) is not dict:
        raise ValueError
    delay = counters.get("real_provider_call_delay_seconds")
    if type(delay) is not float or not _math.isfinite(delay) or delay < 0.0:
        raise ValueError
    if any(
        key != "real_provider_call_delay_seconds" and type(value) is not int
        for key, value in counters.items()
    ):
        raise ValueError
    reasons = tuple(selected["validation_errors"] or ())
    if (
        selected["final_status"] != STATUS_FAIL_CLOSED
        or selected["failed_actor_id"] != "client_purchase_intent_reviewer_llm"
        or selected["failed_stage"] != "actor_validation"
        or tuple(selected["semantic_actor_call_order"] or ()) != anchors.callback_prefix
        or "selection_input_snapshot_mismatch" not in reasons
        or "semantic_to_contract_bridge_guard_failed" not in reasons
    ):
        raise ValueError


def _validate_prior_actor_validation(plain: object) -> None:
    if type(plain) is not dict:
        raise ValueError
    if (
        plain.get("accepted") is not False
        or plain.get("validation_status") != STATUS_FAIL_CLOSED
        or "selection_input_snapshot_mismatch" not in tuple(plain.get("errors") or ())
    ):
        raise ValueError


def _attempt_01_proof_projection(
    proof: _PriorAttemptProof,
) -> tuple[object, ...]:
    return (
        _PRIOR_ANCHORS.attempt_id,
        _PRIOR_ANCHORS.execution_head,
        proof.attempt_identity.sha256,
        proof.private_inventory.sha256,
        proof.inventory_digest,
        proof.generation_gate.sha256,
        REASON_COLLECTOR_FAILED,
        "collector_result",
        len(_PRIOR_ANCHORS.callback_prefix),
    )


def _validate_attempt_02_identity(
    plain: dict[str, object],
    attempt_02_path: _Path,
    anchors: _Attempt02Anchors,
    prior_proof: _PriorAttemptProof,
) -> None:
    expected = _build_attempt_identity(
        execution_mode=MODE_REAL,
        execution_head=anchors.execution_head,
        attempt_number=2,
        private_output_directory=attempt_02_path,
        prior_proof=prior_proof,
    )
    if plain != expected or plain.get("attempt_id") != anchors.attempt_id:
        raise ValueError
    embedded = (
        plain.get("prior_attempt_id"),
        plain.get("prior_execution_head"),
        plain.get("prior_attempt_identity_sha256"),
        plain.get("prior_private_inventory_sha256"),
        plain.get("prior_private_inventory_digest"),
        plain.get("prior_generation_gate_sha256"),
        plain.get("prior_failure_reason"),
        plain.get("prior_failed_stage"),
        plain.get("prior_conservative_callback_consumption"),
    )
    if embedded != _attempt_01_proof_projection(prior_proof):
        raise ValueError


def _validate_attempt_02_inventory(
    plain: dict[str, object],
    rows: tuple[_InventoryRow, ...],
    anchors: _Attempt02Anchors,
) -> None:
    expected_rows = [
        {
            "logical_ref": row.logical_ref,
            "sha256": row.sha256,
            "byte_count": row.byte_count,
        }
        for row in rows
    ]
    if (
        plain.get("validation_status") != STATUS_FAIL_CLOSED
        or plain.get("attempt_number") != 2
        or plain.get("attempt_id") != anchors.attempt_id
        or plain.get("raw_attempt_file_count") != anchors.raw_file_count
        or plain.get("aggregate_inventory_digest") != anchors.private_inventory_digest
        or plain.get("ordered_files") != expected_rows
        or plain.get("raw_bodies_copied_to_public_evidence") is not False
    ):
        raise ValueError


def _validate_attempt_02_gate(
    plain: dict[str, object],
    anchors: _Attempt02Anchors,
    prior_proof: _PriorAttemptProof,
) -> None:
    expected = {
        "attempt_id": anchors.attempt_id,
        "attempt_identity_sha256": anchors.attempt_identity_sha256,
        "attempt_number": 2,
        "execution_head": anchors.execution_head,
        "final_source_status": STATUS_FAIL_CLOSED,
        "failed_stage": "collector_result",
        "reason_code": REASON_COLLECTOR_FAILED,
        "private_inventory_digest": anchors.private_inventory_digest,
        "private_inventory_document_sha256": anchors.private_inventory_sha256,
        "live_collection_performed": True,
        "official_evidence_eligible": False,
        "public_safe_report_state": _PUBLICATION_ABSENT,
        "provider_mode": _lane.PROVIDER_MODE_REAL,
        "wrapper_callback_observed_count": 3,
        "provider_callback_started_count": 3,
        "provider_callback_completed_count": 3,
        "actual_provider_call_count": 3,
        "actual_network_call_count": 0,
        "actual_gemini_call_count": 0,
        "actual_external_operation_status": _EXTERNAL_UNVERIFIED_PARTIAL,
        "actual_real_world_effects_count": 0,
        "retry_count": 0,
        "package_created_count": 0,
        "anchor_created_count": 0,
        "replay_created_count": 0,
        "prior_attempt_id": _PRIOR_ANCHORS.attempt_id,
        "prior_execution_head": _PRIOR_ANCHORS.execution_head,
        "prior_attempt_identity_sha256": prior_proof.attempt_identity.sha256,
        "prior_private_inventory_sha256": prior_proof.private_inventory.sha256,
        "prior_private_inventory_digest": prior_proof.inventory_digest,
        "prior_generation_gate_sha256": prior_proof.generation_gate.sha256,
        "prior_failure_reason": REASON_COLLECTOR_FAILED,
        "prior_failed_stage": "collector_result",
        "prior_conservative_callback_consumption": 3,
        "new_provider_call_ceiling": 12,
        "cumulative_airline_call_ceiling": 15,
        "owner_reviewed_attempt_02": True,
    }
    if any(plain.get(key) != value for key, value in expected.items()):
        raise ValueError
    for key in (
        "observed_actor_prefix",
        "wrapper_callback_observed_prefix",
        "base_provider_started_prefix",
        "base_provider_completed_prefix",
    ):
        if tuple(plain.get(key, ())) != anchors.callback_prefix:
            raise ValueError


def _validate_attempt_02_summary(
    plain: object,
    anchors: _Attempt02Anchors,
) -> None:
    if type(plain) is not dict:
        raise ValueError
    counters = plain.get("counter_table")
    if type(counters) is not dict:
        raise ValueError
    delay = counters.get("real_provider_call_delay_seconds")
    if type(delay) is not float or not _math.isfinite(delay) or delay < 0.0:
        raise ValueError
    if any(
        key != "real_provider_call_delay_seconds" and type(value) is not int
        for key, value in counters.items()
    ):
        raise ValueError
    errors = tuple(plain.get("validation_errors") or ())
    if (
        plain.get("final_status") != STATUS_FAIL_CLOSED
        or plain.get("failed_actor_id") != "client_purchase_intent_reviewer_llm"
        or plain.get("failed_stage") != "actor_validation"
        or tuple(plain.get("semantic_actor_call_order") or ())
        != anchors.callback_prefix
        or _ATTEMPT_02_SEMANTIC_REASON not in errors
    ):
        raise ValueError


def _validate_attempt_02_actor_validation(plain: object) -> None:
    if type(plain) is not dict:
        raise ValueError
    if (
        plain.get("accepted") is not False
        or plain.get("validation_status") != STATUS_FAIL_CLOSED
        or _ATTEMPT_02_SEMANTIC_REASON not in tuple(plain.get("errors") or ())
    ):
        raise ValueError


def _verify_prior_head_ancestry(prior_head: str, current_head: str) -> None:
    if (
        type(prior_head) is not str
        or type(current_head) is not str
        or len(prior_head) != 40
        or len(current_head) != 40
        or _LOWER_HEAD.fullmatch(prior_head) is None
        or _LOWER_HEAD.fullmatch(current_head) is None
    ):
        raise ValueError
    _git_text("merge-base", "--is-ancestor", prior_head, current_head)


def _validate_prior_failed_root(
    value: str | _Path | None,
    new_root: _Path,
) -> _Path:
    try:
        raw = _os.fspath(value)
        _validate_raw_absolute_path_text(raw)
        prior = _Path(raw)
        _validate_raw_absolute_path_text(str(new_root))
        if prior == new_root or _is_within(new_root, prior):
            raise ValueError
        if _is_within(prior, _REPOSITORY_ROOT):
            raise ValueError
        fd, _ = _open_absolute_directory_nofollow(prior)
        _close_proven(fd)
        return prior
    except Exception:
        raise _RunnerFailure(
            REASON_RECOVERY_INPUT_INVALID,
            "prior_attempt_path_validation",
        ) from None


def _validate_attempt_03_predecessor_paths(
    attempt_02_value: str | _Path | None,
    attempt_01_value: str | _Path | None,
    new_root: _Path,
) -> tuple[_Path, _Path]:
    try:
        values = (_os.fspath(attempt_02_value), _os.fspath(attempt_01_value))
        for value in values:
            _validate_raw_absolute_path_text(value)
        _validate_raw_absolute_path_text(str(new_root))
        attempt_02_path, attempt_01_path = map(_Path, values)
        paths = (attempt_02_path, attempt_01_path, new_root)
        if len(set(paths)) != len(paths):
            raise ValueError
        if (
            _is_within(attempt_02_path, attempt_01_path)
            or _is_within(attempt_01_path, attempt_02_path)
            or _is_within(new_root, attempt_02_path)
            or _is_within(new_root, attempt_01_path)
        ):
            raise ValueError
        for predecessor in (attempt_02_path, attempt_01_path):
            if _is_within(predecessor, _REPOSITORY_ROOT):
                raise ValueError
            fd, _ = _open_absolute_directory_nofollow(predecessor)
            _close_proven(fd)
        return attempt_02_path, attempt_01_path
    except Exception:
        raise _RunnerFailure(
            REASON_ATTEMPT_03_RECOVERY_INPUT_INVALID,
            "predecessor_path_validation",
        ) from None


def _validate_private_root(value: str | _Path) -> _Path:
    try:
        raw = _os.fspath(value)
        _validate_raw_absolute_path_text(raw)
        candidate = _Path(raw)
        if candidate.exists() or candidate.is_symlink():
            raise _RunnerFailure(REASON_PRIVATE_PATH_EXISTS, "private_path_validation")
        parent = candidate.parent
        if not parent.is_dir() or parent.is_symlink():
            raise ValueError
        _require_no_symlink_components(parent)
        resolved_parent = parent.resolve(strict=True)
        resolved_repo = _REPOSITORY_ROOT.resolve(strict=True)
        if _is_within(resolved_parent / candidate.name, resolved_repo):
            raise ValueError
        return candidate
    except _RunnerFailure:
        raise
    except Exception:
        raise _RunnerFailure(REASON_PRIVATE_PATH_INVALID, "private_path_validation") from None


def _select_safe_report_path(
    execution_mode: str,
    value: str | _Path | None,
    *,
    private_root: _Path,
) -> _Path:
    if execution_mode == MODE_REAL:
        if value is not None:
            raise _RunnerFailure(REASON_MODE_INVALID, "input_validation")
        if _CANONICAL_SAFE_REPORT_PATH.exists() or _CANONICAL_SAFE_REPORT_PATH.is_symlink():
            raise _RunnerFailure(REASON_CANONICAL_REPORT_EXISTS, "repository_guard")
        return _CANONICAL_SAFE_REPORT_PATH
    if value is None:
        raise _RunnerFailure(REASON_MODE_INVALID, "input_validation")
    try:
        raw = _os.fspath(value)
        _validate_raw_absolute_path_text(raw)
        output = _Path(raw)
        if output == _CANONICAL_SAFE_REPORT_PATH or output.exists() or output.is_symlink():
            raise ValueError
        if not output.parent.is_dir() or output.parent.is_symlink():
            raise ValueError
        _require_no_symlink_components(output.parent)
        if _is_within(output, _REPOSITORY_ROOT.resolve(strict=True)) or _is_within(output, private_root):
            raise ValueError
        return output
    except Exception:
        raise _RunnerFailure(REASON_PRIVATE_PATH_INVALID, "safe_report_path_validation") from None


def _validate_raw_absolute_path_text(raw: object) -> None:
    if type(raw) is not str or not raw or _unicodedata.normalize("NFC", raw) != raw:
        raise ValueError
    raw.encode("utf-8", errors="strict")
    if not raw.startswith("/") or raw.startswith("//"):
        raise ValueError
    components = raw.split("/")
    if components[0] != "" or any(
        component in ("", ".", "..") for component in components[1:]
    ):
        raise ValueError
    if any(_unicodedata.category(char).startswith("C") for char in raw):
        raise ValueError


def _require_mode(
    mode: object,
    injected_provider: object,
    injected_output: object,
) -> None:
    if mode not in (MODE_INJECTED, MODE_REAL):
        raise _RunnerFailure(REASON_MODE_INVALID, "input_validation")
    if mode == MODE_REAL and (injected_provider is not None or injected_output is not None):
        raise _RunnerFailure(REASON_MODE_INVALID, "input_validation")


def _require_real_local_preconditions(
    ambient_environment: _Mapping[str, str],
) -> _RealPreconditionResult:
    try:
        if (
            _Path(_sys.prefix) != _REPOSITORY_VENV_PREFIX
            or _sys.prefix == _sys.base_prefix
            or MODEL_ID != _lane.DEFAULT_REAL_PROVIDER_MODEL
        ):
            raise ValueError
        credential_count = sum(
            type(ambient_environment.get(key)) is str
            and bool(ambient_environment.get(key, "").strip())
            for key in _CREDENTIAL_ENV_KEYS
        )
        if credential_count != 1:
            raise ValueError
        raw_timeout = ambient_environment.get(_PROVIDER_TIMEOUT_ENV_KEY)
        if raw_timeout is None:
            timeout_seconds = 20
        elif (
            type(raw_timeout) is not str
            or not raw_timeout
            or not raw_timeout.isascii()
            or not raw_timeout.isdecimal()
            or (len(raw_timeout) > 1 and raw_timeout.startswith("0"))
        ):
            raise ValueError
        else:
            timeout_seconds = int(raw_timeout)
        if not 1 <= timeout_seconds <= 120:
            raise ValueError
        if (
            _lane.provider_adapter._timeout_seconds(ambient_environment)
            != timeout_seconds
        ):
            raise ValueError
        types_module = _importlib.import_module("google.genai.types")
        http_options = getattr(types_module, "HttpOptions", None)
        if http_options is None:
            raise ValueError
        http_options(timeout=timeout_seconds * 1000)
        return _RealPreconditionResult(timeout_seconds, credential_count)
    except Exception:
        raise _RunnerFailure(
            REASON_LOCAL_PRECONDITION_FAILED,
            "local_precondition",
        ) from None


def _require_real_repository_ready(expected_head: str | None = None) -> str:
    try:
        if any(
            key in _FORBIDDEN_GIT_ENV_KEYS or key.startswith("GIT_CONFIG_")
            for key in _os.environ
        ):
            raise ValueError
        root = _git_text("rev-parse", "--show-toplevel")
        if _Path(root).resolve(strict=True) != _REPOSITORY_ROOT.resolve(strict=True):
            raise ValueError
        if _git_text("branch", "--show-current") != "main":
            raise ValueError
        head = _git_text("rev-parse", "HEAD")
        origin_head = _git_text("rev-parse", "origin/main")
        if (
            _re.fullmatch(r"[0-9a-f]{40}", head) is None
            or head != origin_head
            or (expected_head is not None and head != expected_head)
        ):
            raise ValueError
        if _git_text("status", "--porcelain", "--untracked-files=all"):
            raise ValueError
        if _git_text("diff", "--cached", "--name-only"):
            raise ValueError
        tracked = tuple(
            _git_text(
                "ls-files",
                "--error-unmatch",
                "demo/run_two_domain_airline_all_real_program_v01.py",
                "tests/test_two_domain_airline_all_real_program_v01_runner.py",
            ).splitlines()
        )
        if tracked != (
            "demo/run_two_domain_airline_all_real_program_v01.py",
            "tests/test_two_domain_airline_all_real_program_v01_runner.py",
        ):
            raise ValueError
        return head
    except Exception:
        raise _RunnerFailure(REASON_REPOSITORY_NOT_READY, "repository_guard") from None


def _git_text(*args: str) -> str:
    environment = {
        key: value
        for key, value in _os.environ.items()
        if not key.startswith("GIT_")
    }
    environment.update(
        {
            "GIT_PAGER": "cat",
            "GIT_OPTIONAL_LOCKS": "0",
            "PAGER": "cat",
            "LC_ALL": "C",
        }
    )
    completed = _subprocess.run(
        ("git", "-C", str(_REPOSITORY_ROOT), *args),
        check=True,
        stdout=_subprocess.PIPE,
        stderr=_subprocess.DEVNULL,
        text=True,
        timeout=_GIT_TIMEOUT_SECONDS,
        env=environment,
    )
    return completed.stdout.strip()


def _create_private_root(root: _Path) -> tuple[int, int]:
    parent_fd = _open_parent_directory(root.parent)
    child_fd = -1
    try:
        _os.mkdir(root.name, mode=0o700, dir_fd=parent_fd)
        flags = _os.O_RDONLY | getattr(_os, "O_DIRECTORY", 0) | getattr(_os, "O_NOFOLLOW", 0)
        child_fd = _OPEN(root.name, flags, dir_fd=parent_fd)
        identity = _descriptor_identity(child_fd, directory=True)
        entry = _os.stat(root.name, dir_fd=parent_fd, follow_symlinks=False)
        if identity != (entry.st_dev, entry.st_ino):
            raise _RunnerFailure(REASON_PRIVATE_PATH_INVALID, "private_root_creation")
        return identity
    except FileExistsError:
        raise _RunnerFailure(REASON_PRIVATE_PATH_EXISTS, "private_root_creation") from None
    except _RunnerFailure:
        raise
    except Exception:
        raise _RunnerFailure(REASON_PRIVATE_PATH_INVALID, "private_root_creation") from None
    finally:
        if child_fd >= 0:
            _close_or_runner_failure(child_fd, REASON_PRIVATE_PATH_INVALID, "private_root_creation")
        _close_or_runner_failure(parent_fd, REASON_PRIVATE_PATH_INVALID, "private_root_creation")


def _write_private_document(
    root: _Path,
    root_identity: tuple[int, int],
    leaf: str,
    plain: object,
    *,
    expected_root_entries: tuple[str, ...] | None = None,
) -> _PrivateDocumentProof:
    data = _canonical_json_line(plain)
    root_fd = _open_verified_directory(root, root_identity)
    fd = -1
    identity: tuple[int, int] | None = None
    try:
        flags = _os.O_WRONLY | _os.O_CREAT | _os.O_EXCL | getattr(_os, "O_NOFOLLOW", 0)
        fd = _OPEN(leaf, flags, 0o600, dir_fd=root_fd)
        identity = _descriptor_identity(fd, directory=False)
        entry = _os.stat(leaf, dir_fd=root_fd, follow_symlinks=False)
        if identity != (entry.st_dev, entry.st_ino):
            raise ValueError
        _write_all(fd, data)
        _os.fchmod(fd, 0o600)
        _FSYNC(fd)
        _close_proven(fd)
        fd = -1
        if _PRIVATE_DOCUMENT_POST_CLOSE_HOOK is not None:
            _PRIVATE_DOCUMENT_POST_CLOSE_HOOK(root_fd, leaf)
        proof = _PrivateDocumentProof(
            leaf=leaf,
            identity=identity,
            expected_bytes=data,
            sha256=_sha256(data),
            byte_count=len(data),
        )
        _revalidate_private_document_fd(root_fd, proof, plain)
        if expected_root_entries is not None and tuple(sorted(_os.listdir(root_fd))) != tuple(
            sorted(expected_root_entries)
        ):
            raise ValueError
        _close_proven(root_fd)
        root_fd = -1
        return proof
    except Exception:
        close_failed = False
        if fd >= 0:
            try:
                _close_proven(fd)
            except Exception:
                close_failed = True
        if identity is not None:
            try:
                entry = _os.stat(leaf, dir_fd=root_fd, follow_symlinks=False)
                if (entry.st_dev, entry.st_ino) == identity:
                    _UNLINK(leaf, dir_fd=root_fd)
                    try:
                        _os.stat(leaf, dir_fd=root_fd, follow_symlinks=False)
                    except FileNotFoundError:
                        pass
                    else:
                        close_failed = True
            except FileNotFoundError:
                pass
            except Exception:
                close_failed = True
        try:
            _close_proven(root_fd)
            root_fd = -1
        except Exception:
            close_failed = True
        stage = "private_metadata_cleanup" if close_failed else "private_metadata"
        raise _RunnerFailure(REASON_PRIVATE_METADATA_FAILED, stage) from None


def _revalidate_private_document(
    root: _Path,
    root_identity: tuple[int, int],
    proof: _PrivateDocumentProof,
    plain: object,
) -> None:
    root_fd = _open_verified_directory(root, root_identity)
    try:
        _revalidate_private_document_fd(root_fd, proof, plain)
    except _RunnerFailure:
        raise
    except Exception:
        raise _RunnerFailure(REASON_PRIVATE_METADATA_FAILED, "private_metadata_proof") from None
    finally:
        _close_or_runner_failure(
            root_fd,
            REASON_PRIVATE_METADATA_FAILED,
            "private_metadata_proof",
        )


def _revalidate_private_document_fd(
    root_fd: int,
    proof: _PrivateDocumentProof,
    plain: object,
) -> None:
    before = _os.stat(proof.leaf, dir_fd=root_fd, follow_symlinks=False)
    if (
        (before.st_dev, before.st_ino) != proof.identity
        or not _stat.S_ISREG(before.st_mode)
        or _stat.S_IMODE(before.st_mode) != 0o600
        or before.st_size != proof.byte_count
    ):
        raise ValueError
    flags = _os.O_RDONLY | getattr(_os, "O_NOFOLLOW", 0)
    fd = _OPEN(proof.leaf, flags, dir_fd=root_fd)
    try:
        opened_identity = _descriptor_identity(fd, directory=False)
        opened = _FSTAT(fd)
        if (
            opened_identity != proof.identity
            or _stat.S_IMODE(opened.st_mode) != 0o600
            or opened.st_size != proof.byte_count
        ):
            raise ValueError
        content = _read_all(fd)
        after = _os.stat(proof.leaf, dir_fd=root_fd, follow_symlinks=False)
        if (
            (after.st_dev, after.st_ino) != proof.identity
            or _stat.S_IMODE(after.st_mode) != 0o600
            or after.st_size != proof.byte_count
            or content != proof.expected_bytes
            or len(content) != proof.byte_count
            or _sha256(content) != proof.sha256
        ):
            raise ValueError
        parsed = _strict_json(content)
        if parsed != _jsonable(plain) or _canonical_json_line(parsed) != content:
            raise ValueError
    finally:
        _close_proven(fd)


def _cleanup_owned_private_document(
    root: _Path,
    root_identity: tuple[int, int],
    proof: _PrivateDocumentProof,
    plain: object,
) -> None:
    root_fd = -1
    try:
        root_fd = _open_verified_directory(root, root_identity)
        _revalidate_private_document_fd(root_fd, proof, plain)
        entry = _os.stat(proof.leaf, dir_fd=root_fd, follow_symlinks=False)
        if (
            (entry.st_dev, entry.st_ino) != proof.identity
            or not _stat.S_ISREG(entry.st_mode)
            or _stat.S_IMODE(entry.st_mode) != 0o600
            or entry.st_size != proof.byte_count
        ):
            raise ValueError
        _UNLINK(proof.leaf, dir_fd=root_fd)
        try:
            _os.stat(proof.leaf, dir_fd=root_fd, follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            raise ValueError
        _close_proven(root_fd)
        root_fd = -1
    except Exception:
        if root_fd >= 0:
            try:
                _close_proven(root_fd)
            except Exception:
                pass
        raise _RunnerFailure(
            REASON_PRIVATE_METADATA_FAILED,
            "generation_gate_cleanup",
        ) from None


def _private_leaf_exists(
    root: _Path,
    root_identity: tuple[int, int],
    leaf: str,
) -> bool:
    root_fd = _open_verified_directory(root, root_identity)
    try:
        try:
            _os.stat(leaf, dir_fd=root_fd, follow_symlinks=False)
        except FileNotFoundError:
            return False
        return True
    finally:
        _close_proven(root_fd)


def _prove_existing_private_document(
    root: _Path,
    root_identity: tuple[int, int],
    leaf: str,
) -> tuple[object, _PrivateDocumentProof]:
    root_fd = _open_verified_directory(root, root_identity)
    try:
        before = _os.stat(leaf, dir_fd=root_fd, follow_symlinks=False)
        if (
            not _stat.S_ISREG(before.st_mode)
            or _stat.S_IMODE(before.st_mode) != 0o600
        ):
            raise ValueError
        flags = _os.O_RDONLY | getattr(_os, "O_NOFOLLOW", 0)
        fd = _OPEN(leaf, flags, dir_fd=root_fd)
        try:
            identity = _descriptor_identity(fd, directory=False)
            opened = _FSTAT(fd)
            if (
                identity != (before.st_dev, before.st_ino)
                or _stat.S_IMODE(opened.st_mode) != 0o600
                or opened.st_size != before.st_size
            ):
                raise ValueError
            content = _read_all(fd)
            after = _os.stat(leaf, dir_fd=root_fd, follow_symlinks=False)
            if (
                identity != (after.st_dev, after.st_ino)
                or _stat.S_IMODE(after.st_mode) != 0o600
                or after.st_size != len(content)
            ):
                raise ValueError
        finally:
            _close_proven(fd)
        parsed = _strict_json(content)
        if _canonical_json_line(parsed) != content:
            raise ValueError
        proof = _PrivateDocumentProof(
            leaf,
            identity,
            content,
            _sha256(content),
            len(content),
        )
        return parsed, proof
    finally:
        _close_proven(root_fd)


def _assert_private_root_entries(
    root: _Path,
    root_identity: tuple[int, int],
    expected: tuple[str, ...],
) -> None:
    fd = _open_verified_directory(root, root_identity)
    try:
        if tuple(sorted(_os.listdir(fd))) != tuple(sorted(expected)):
            raise _RunnerFailure(REASON_INVENTORY_INVALID, "private_root_inventory")
    finally:
        _close_or_runner_failure(fd, REASON_INVENTORY_INVALID, "private_root_inventory")


def _write_public_safe_report(path: _Path, plain: object) -> _OwnedOutput:
    expected = _canonical_json_line(plain)
    try:
        parent_fd = _open_parent_directory(path.parent)
    except Exception:
        raise _PublicCleanupFailure from None
    parent_identity = _descriptor_identity(parent_fd, directory=True)
    fd = -1
    identity: tuple[int, int] | None = None
    owner: _OwnedOutput | None = None
    try:
        flags = _os.O_WRONLY | _os.O_CREAT | _os.O_EXCL | getattr(_os, "O_NOFOLLOW", 0)
        fd = _OPEN(path.name, flags, 0o600, dir_fd=parent_fd)
        identity = _descriptor_identity(fd, directory=False)
        entry = _os.stat(path.name, dir_fd=parent_fd, follow_symlinks=False)
        if identity != (entry.st_dev, entry.st_ino):
            raise _PublicCleanupFailure
        owner = _OwnedOutput(
            path.parent,
            parent_fd,
            parent_identity,
            path.name,
            identity,
            expected,
        )
        _write_all(fd, expected)
        _FSYNC(fd)
        _os.fchmod(fd, 0o400)
        _close_proven(fd)
        fd = -1
        _revalidate_owned_output(owner, plain)
        return owner
    except FileExistsError:
        _close_proven(parent_fd)
        raise _RunnerFailure(REASON_PUBLIC_WRITE_FAILED, "public_safe_report_write") from None
    except _PublicCleanupFailure:
        if fd >= 0:
            try:
                _close_proven(fd)
            except Exception:
                pass
        if owner is not None:
            _cleanup_owned_output(owner)
        else:
            _close_proven(parent_fd)
        raise
    except Exception:
        if fd >= 0:
            try:
                _close_proven(fd)
            except Exception:
                pass
        if owner is not None:
            try:
                _cleanup_owned_output(owner)
            except _PublicCleanupFailure:
                raise
        else:
            _close_proven(parent_fd)
        raise _RunnerFailure(REASON_PUBLIC_WRITE_FAILED, "public_safe_report_write") from None


def _revalidate_owned_output(owner: _OwnedOutput, plain: object) -> None:
    _verify_directory_path_identity(owner.parent_path, owner.parent_identity)
    flags = _os.O_RDONLY | getattr(_os, "O_NOFOLLOW", 0)
    fd = _OPEN(owner.leaf, flags, dir_fd=owner.parent_fd)
    try:
        opened = _FSTAT(fd)
        entry = _os.stat(
            owner.leaf,
            dir_fd=owner.parent_fd,
            follow_symlinks=False,
        )
        if (
            _descriptor_identity(fd, directory=False) != owner.identity
            or (entry.st_dev, entry.st_ino) != owner.identity
            or not _stat.S_ISREG(entry.st_mode)
            or opened.st_size != len(owner.expected_bytes)
            or entry.st_size != len(owner.expected_bytes)
            or _stat.S_IMODE(opened.st_mode) != 0o400
            or _stat.S_IMODE(entry.st_mode) != 0o400
        ):
            raise _PublicCleanupFailure
        content = _read_all(fd)
        if content != owner.expected_bytes:
            raise _RunnerFailure(REASON_PUBLIC_WRITE_FAILED, "public_safe_report_reread")
        parsed = _strict_json(content)
        if parsed != _jsonable(plain) or _canonical_json_line(parsed) != content:
            raise _RunnerFailure(REASON_PUBLIC_WRITE_FAILED, "public_safe_report_reread")
        _verify_directory_path_identity(owner.parent_path, owner.parent_identity)
    finally:
        _close_proven(fd)


def _release_owned_output(owner: _OwnedOutput) -> _ReleasedOutput:
    try:
        _revalidate_owned_output(owner, _strict_json(owner.expected_bytes))
        _verify_directory_path_identity(owner.parent_path, owner.parent_identity)
        entry = _os.stat(owner.leaf, dir_fd=owner.parent_fd, follow_symlinks=False)
        if (
            (entry.st_dev, entry.st_ino) != owner.identity
            or entry.st_size != len(owner.expected_bytes)
            or _stat.S_IMODE(entry.st_mode) != 0o400
        ):
            raise _PublicCleanupFailure
        released = _ReleasedOutput(
            owner.parent_path,
            owner.parent_identity,
            owner.leaf,
            owner.identity,
            owner.expected_bytes,
        )
        _close_proven(owner.parent_fd)
        return released
    except Exception:
        raise _PublicCleanupFailure from None


def _cleanup_owned_output(owner: _OwnedOutput) -> None:
    path_identity_proven = True
    try:
        try:
            _verify_directory_path_identity(owner.parent_path, owner.parent_identity)
        except Exception:
            path_identity_proven = False
        entry = _os.stat(owner.leaf, dir_fd=owner.parent_fd, follow_symlinks=False)
        if (entry.st_dev, entry.st_ino) != owner.identity:
            raise _PublicCleanupFailure
        _UNLINK(owner.leaf, dir_fd=owner.parent_fd)
        try:
            _os.stat(owner.leaf, dir_fd=owner.parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            raise _PublicCleanupFailure
        _close_proven(owner.parent_fd)
        if not path_identity_proven:
            raise _PublicCleanupFailure
    except Exception:
        try:
            _close_proven(owner.parent_fd)
        except Exception:
            pass
        raise _PublicCleanupFailure from None


def _cleanup_released_output(owner: _ReleasedOutput) -> None:
    parent_fd = -1
    try:
        parent_fd = _open_verified_directory(
            owner.parent_path,
            owner.parent_identity,
        )
        entry = _os.stat(owner.leaf, dir_fd=parent_fd, follow_symlinks=False)
        if (entry.st_dev, entry.st_ino) != owner.identity:
            raise _PublicCleanupFailure
        flags = _os.O_RDONLY | getattr(_os, "O_NOFOLLOW", 0)
        fd = _OPEN(owner.leaf, flags, dir_fd=parent_fd)
        try:
            if _descriptor_identity(fd, directory=False) != owner.identity:
                raise _PublicCleanupFailure
            if _read_all(fd) != owner.expected_bytes:
                raise _PublicCleanupFailure
        finally:
            _close_proven(fd)
        _UNLINK(owner.leaf, dir_fd=parent_fd)
        try:
            _os.stat(owner.leaf, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            raise _PublicCleanupFailure
        _close_proven(parent_fd)
        parent_fd = -1
    except Exception:
        if parent_fd >= 0:
            try:
                _close_proven(parent_fd)
            except Exception:
                pass
        raise _PublicCleanupFailure from None


def _open_parent_directory(path: _Path) -> int:
    fd, _ = _open_absolute_directory_nofollow(path)
    return fd


def _open_verified_directory(path: _Path, identity: tuple[int, int]) -> int:
    fd = -1
    try:
        fd, observed = _open_absolute_directory_nofollow(path)
        if observed != identity:
            raise ValueError
        return fd
    except Exception:
        if fd >= 0:
            _close_proven(fd)
        raise _RunnerFailure(REASON_INVENTORY_INVALID, "private_root_identity") from None


def _verify_directory_path_identity(
    path: _Path,
    identity: tuple[int, int],
) -> None:
    fd = -1
    try:
        fd, observed = _open_absolute_directory_nofollow(path)
        if observed != identity:
            raise ValueError
        _close_proven(fd)
        fd = -1
    except Exception:
        if fd >= 0:
            try:
                _close_proven(fd)
            except Exception:
                pass
        raise _PublicCleanupFailure from None


def _descriptor_identity(fd: int, *, directory: bool) -> tuple[int, int]:
    try:
        item = _FSTAT(fd)
    except OSError:
        item = _RAW_FSTAT(fd)
    if directory and not _stat.S_ISDIR(item.st_mode):
        raise ValueError
    if not directory and not _stat.S_ISREG(item.st_mode):
        raise ValueError
    return item.st_dev, item.st_ino


def _close_proven(fd: int) -> None:
    try:
        _CLOSE(fd)
    except OSError:
        pass
    try:
        _os.fstat(fd)
    except OSError as error:
        if error.errno == _errno.EBADF:
            return
        raise
    _RAW_CLOSE(fd)
    try:
        _os.fstat(fd)
    except OSError as error:
        if error.errno == _errno.EBADF:
            return
    raise OSError("descriptor_close_unproved")


def _close_or_runner_failure(fd: int, reason: str, stage: str) -> None:
    try:
        _close_proven(fd)
    except Exception:
        raise _RunnerFailure(reason, stage) from None


def _write_all(fd: int, data: bytes) -> None:
    offset = 0
    while offset < len(data):
        count = _WRITE(fd, data[offset:])
        if type(count) is not int or count <= 0:
            raise OSError("short_write")
        offset += count


def _read_all(fd: int) -> bytes:
    parts: list[bytes] = []
    while True:
        chunk = _os.read(fd, 65536)
        if not chunk:
            return b"".join(parts)
        parts.append(chunk)


def _read_bounded(fd: int, exact_size: int) -> bytes:
    if type(exact_size) is not int or exact_size < 0:
        raise ValueError
    parts: list[bytes] = []
    remaining = exact_size + 1
    while remaining:
        chunk = _os.read(fd, min(65536, remaining))
        if not chunk:
            break
        parts.append(chunk)
        remaining -= len(chunk)
    content = b"".join(parts)
    if len(content) != exact_size:
        raise ValueError
    return content


def _strict_json(content: bytes) -> object:
    if not content.endswith(b"\n") or content.endswith(b"\n\n") or b"\r" in content:
        raise ValueError
    text = content[:-1].decode("utf-8", errors="strict")

    def pairs(rows: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in rows:
            if key in result:
                raise ValueError
            result[key] = value
        return result

    return _json.loads(
        text,
        object_pairs_hook=pairs,
        parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)),
    )


def _parse_prior_legacy_source_json(content: bytes) -> dict[str, object]:
    if (
        type(content) is not bytes
        or not 0 < len(content) <= 16_000_000
        or content.endswith(b"\n")
        or b"\r" in content
        or b"\x00" in content
        or content.startswith(b"\xef\xbb\xbf")
    ):
        raise ValueError
    text = content.decode("utf-8", errors="strict")

    def pairs(rows: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in rows:
            if key in result:
                raise ValueError
            result[key] = value
        return result

    parsed = _json.loads(
        text,
        object_pairs_hook=pairs,
        parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)),
    )
    if type(parsed) is not dict:
        raise ValueError
    canonical = _json.dumps(
        parsed,
        indent=2,
        sort_keys=True,
        allow_nan=False,
    ).encode("utf-8")
    if canonical != content:
        raise ValueError
    return parsed


def _canonical_json_line(value: object) -> bytes:
    return (
        _json.dumps(
            _jsonable(value),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
        + b"\n"
    )


def _jsonable(value: object) -> object:
    if value is None or type(value) in (str, int, float, bool):
        return value
    if type(value) is dict:
        return {key: _jsonable(item) for key, item in value.items()}
    if type(value) in (tuple, list):
        return [_jsonable(item) for item in value]
    raise TypeError


def _ensure_canonical_public_parent() -> None:
    current = _REPOSITORY_ROOT
    for part in _Path(CANONICAL_SAFE_REPORT_REF).parent.parts:
        current = current / part
        if current.exists():
            if not current.is_dir() or current.is_symlink():
                raise _RunnerFailure(REASON_PUBLIC_WRITE_FAILED, "public_parent")
        else:
            current.mkdir(mode=0o700)


def _require_no_symlink_components(path: _Path) -> None:
    current = _Path(path.anchor)
    for part in path.parts[1:]:
        current = current / part
        item = current.lstat()
        if _stat.S_ISLNK(item.st_mode) or not _stat.S_ISDIR(item.st_mode):
            raise ValueError


def _is_within(path: _Path, parent: _Path) -> bool:
    try:
        path.relative_to(parent)
        return True
    except ValueError:
        return False


def _required_head(value: object) -> str:
    if type(value) is not str or _LOWER_HEAD.fullmatch(value) is None:
        raise ValueError
    return value


def _sha256(value: bytes) -> str:
    return _hashlib.sha256(value).hexdigest()


def _emit_progress(
    sink: _Callable[[dict[str, object]], None] | None,
    index: int,
    actor_id: str,
    event: str,
    validation_status: str,
) -> None:
    if sink is not None:
        sink(
            {
                "actor_index": index,
                "actor_count": 12,
                "actor_id": actor_id,
                "event": event,
                "validation_status": validation_status,
            }
        )


def _emit_validation_progress(
    sink: _Callable[[dict[str, object]], None] | None,
) -> None:
    if sink is None:
        return
    for index, actor_id in enumerate(ACTOR_IDS, start=1):
        _emit_progress(
            sink,
            index,
            actor_id,
            "local_validation_completed",
            STATUS_PASS,
        )


def _result(
    *,
    execution_mode: str,
    execution_head: str,
    attempt_number: int,
    attempt_id: str,
    final_status: str,
    reason_code: str,
    failed_stage: str,
    preservation_state: str,
    publication_state: str,
    collector_count: int,
    callback_observed: tuple[str, ...],
    base_calls_started: tuple[str, ...],
    base_calls_completed: tuple[str, ...],
    safe_execution_id: str,
    safe_hash: str,
    inventory_digest: str,
) -> AirlineA1ProgramResultV01:
    accepted = final_status == STATUS_PASS
    real = execution_mode == MODE_REAL
    callback_count = len(callback_observed)
    base_started_count = len(base_calls_started)
    causal_count = sum(actor_id in CAUSAL_ACTOR_IDS for actor_id in callback_observed)
    duplicate_count = callback_count - len(set(callback_observed))
    external_status = (
        _EXTERNAL_VERIFIED
        if accepted and real
        else _EXTERNAL_UNVERIFIED_PARTIAL
        if real and base_started_count
        else _EXTERNAL_NOT_PERFORMED
    )
    return AirlineA1ProgramResultV01(
        programme_id=PROGRAMME_ID,
        programme_version=PROGRAMME_VERSION,
        gate_id=_gate_id_for_attempt(attempt_number),
        domain_id=DOMAIN_ID,
        execution_mode=execution_mode,
        execution_head=execution_head,
        attempt_number=attempt_number,
        attempt_id=attempt_id,
        final_status=final_status,
        reason_code=reason_code,
        failed_stage=failed_stage,
        live_collection_performed=real and base_started_count > 0,
        official_evidence_eligible=(
            accepted and real and publication_state == _PUBLICATION_PRESENT
        ),
        private_attempt_preserved=preservation_state == _PRESERVATION_PRESERVED,
        private_attempt_preservation_state=preservation_state,
        public_safe_report_state=publication_state,
        actual_external_operation_status=external_status,
        provider_application_call_mode=_PROVIDER_APPLICATION_CALL_MODE,
        collector_invocation_count=collector_count,
        injected_callback_count=base_started_count if not real else 0,
        wrapper_callback_observed_count=callback_count,
        provider_callback_started_count=base_started_count,
        provider_callback_completed_count=len(base_calls_completed),
        semantic_actor_call_count=12 if accepted else callback_count,
        causal_actor_call_count=5 if accepted else causal_count,
        generic_actor_call_count=7 if accepted else callback_count - causal_count,
        duplicate_actor_call_count=duplicate_count,
        safe_execution_id=safe_execution_id,
        safe_report_sha256=safe_hash,
        private_inventory_digest=inventory_digest,
        safe_report_written=publication_state == _PUBLICATION_PRESENT,
        source_provider_call_count=12 if accepted else 0,
        source_network_call_count=12 if accepted else 0,
        source_gemini_call_count=12 if accepted else 0,
        source_real_world_effects_count=0,
        actual_provider_call_count=base_started_count if real else 0,
        actual_network_call_count=base_started_count if accepted and real else 0,
        actual_gemini_call_count=base_started_count if accepted and real else 0,
        actual_real_world_effects_count=0,
        retry_count=0,
        package_created_count=0,
        anchor_created_count=0,
        replay_created_count=0,
    )


class _SanitizedArgumentParser(_ArgumentParser):
    def error(self, message: str) -> None:
        raise _CliError from None


def _parser() -> _SanitizedArgumentParser:
    parser = _SanitizedArgumentParser(add_help=False, allow_abbrev=False)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--injected-deterministic", action="store_true")
    modes.add_argument("--real-provider", action="store_true")
    parser.add_argument("--attempt-number", required=True)
    parser.add_argument("--private-output-directory", required=True)
    parser.add_argument("--safe-report-output")
    parser.add_argument("--prior-failed-attempt-directory")
    parser.add_argument("--prior-attempt-id")
    parser.add_argument("--owner-reviewed-attempt-02", action="store_true")
    parser.add_argument("--transitive-failed-attempt-directory")
    parser.add_argument("--transitive-attempt-id")
    parser.add_argument("--owner-reviewed-attempt-03", action="store_true")
    return parser


def _reject_duplicate_cli_options(argv: tuple[str, ...]) -> None:
    seen: set[str] = set()
    for token in argv:
        if type(token) is not str or not token.startswith("--"):
            continue
        option = token.split("=", 1)[0]
        if option in seen:
            raise _CliError
        seen.add(option)


def main(argv: list[str] | None = None) -> int:
    try:
        raw_argv = tuple(_sys.argv[1:] if argv is None else argv)
        _reject_duplicate_cli_options(raw_argv)
        args = _parser().parse_args(raw_argv)
        if args.attempt_number not in ("1", "2", "3"):
            raise _CliError
        mode = MODE_REAL if args.real_provider else MODE_INJECTED
        progress = lambda item: print(
            _canonical_json_line(item).decode("utf-8").rstrip("\n")
        )
        result = run_two_domain_airline_all_real_program_v01(
            execution_mode=mode,
            attempt_number=int(args.attempt_number),
            private_output_directory=args.private_output_directory,
            injected_safe_report_output=args.safe_report_output,
            progress_sink=progress,
            prior_failed_attempt_directory=args.prior_failed_attempt_directory,
            prior_attempt_id=args.prior_attempt_id,
            owner_reviewed_attempt_02=args.owner_reviewed_attempt_02,
            transitive_failed_attempt_directory=(
                args.transitive_failed_attempt_directory
            ),
            transitive_attempt_id=args.transitive_attempt_id,
            owner_reviewed_attempt_03=args.owner_reviewed_attempt_03,
        )
        print(
            _canonical_json_line(
                airline_a1_program_result_to_plain_dict_v01(result)
            ).decode("utf-8").rstrip("\n")
        )
        return 0 if result.final_status == STATUS_PASS else 2
    except _CliError:
        failure = {
            "final_status": STATUS_FAIL_CLOSED,
            "reason_code": REASON_INVALID,
            "live_collection_performed": False,
            "official_evidence_eligible": False,
            "actual_provider_call_count": 0,
            "actual_network_call_count": 0,
            "actual_gemini_call_count": 0,
            "actual_real_world_effects_count": 0,
        }
        print(_canonical_json_line(failure).decode("utf-8").rstrip("\n"))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
