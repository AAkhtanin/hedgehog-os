"""Airline A2 accepted-source binding and deterministic package projections.

This module contains no provider, network, collector, or publication client.
Pure builders are separated from descriptor-bound source loaders. Local
packageability evidence is permanently nonpublication.
"""

from __future__ import annotations

import base64
from collections.abc import Mapping
from dataclasses import asdict, dataclass, fields, is_dataclass, replace
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat
import subprocess
from types import UnionType
from typing import Any, get_args, get_origin, get_type_hints

from hedgehog.domains.airline import sealed_evidence_package_adapter_v01 as adapter
from hedgehog.domains.airline import crypto_artifact_seal_v01 as crypto
from hedgehog.domains.airline import crypto_artifact_seal_collector_v01 as crypto_collector
from hedgehog.domains.airline import kernel_adapter_v01 as kernel_adapter
from hedgehog.domains.airline import sealed_trace_replay_v01 as replay
from hedgehog.domains.airline import semantic_to_contract_causal_runtime_v01 as causal_runtime
from hedgehog.domains.airline import ticket_purchase_corridor_v01 as corridor_contracts
from hedgehog.domains.airline import ticket_purchase_corridor_runtime_v01 as corridor_runtime
from hedgehog.domains.airline import transaction_artifact_ledger_v01 as ledger
from hedgehog.domains.airline import transaction_artifact_ledger_collector_v01 as ledger_collector
from hedgehog.evidence import sealed_evidence_profile_v01 as profile
from hedgehog.evidence import sealed_package_v01 as sealed_package


VERSION = "v0.1"
SOURCE_LOCAL = "LOCAL_NONPUBLICATION_SOURCE"
SOURCE_OFFICIAL = "OFFICIAL_ACCEPTED_SOURCE"
INVOCATION_LOCAL_PRECOMMIT = "LOCAL_PRECOMMIT_PACKAGE_INVOCATION"
INVOCATION_LOCAL_COMMITTED = "LOCAL_COMMITTED_PACKAGE_INVOCATION"
INVOCATION_OFFICIAL = "OFFICIAL_PACKAGE_INVOCATION"
GATE_PHASE_PRECOMMIT = "precommit"
GATE_PHASE_COMMITTED = "committed-head"
STATUS_PASS = "PASS"
STATUS_SELF_CONSISTENT_UNANCHORED = "SELF_CONSISTENT_UNANCHORED"
MODEL_ID = "gemini-2.5-flash"
APPLICATION_CALL_MODE = "json_mime_no_response_schema_single_application_call"
CORRIDOR_ARCHIVE_LOGICAL_NAME = (
    "raw_attempt/airline_ticket_purchase_corridor_run_report_v01.json"
)
LOCAL_SAFE_REPORT_LOGICAL_NAME = "safe-report-v01.json"
OFFICIAL_PACKAGE_ROOT = (
    "docs/evidence/two_domain_all_real_sealed_evidence_program_v01/airline/"
    "airline_sealed_package_v01"
)
OFFICIAL_PACKAGE_INDEX = (
    "docs/evidence/two_domain_all_real_sealed_evidence_program_v01/airline/"
    "airline_safe_package_index_v01.json"
)
ACTOR_IDS = adapter._EXPECTED_ACTOR_IDS
LOWER_SHA256 = re.compile(r"^[0-9a-f]{64}$")
LOWER_HEAD = re.compile(r"^[0-9a-f]{40}$")
SOURCE_DOMAIN_LOCAL = (
    "hedgehog-os:airline-a2-source-identity:v0.1:LOCAL_NONPUBLICATION_SOURCE"
)
SOURCE_DOMAIN_OFFICIAL = (
    "hedgehog-os:airline-a2-source-identity:v0.1:OFFICIAL_ACCEPTED_SOURCE"
)
PROCESS_A_DOMAIN = "hedgehog-os:airline-a2-local-process-a-result:v0.1"
INDEX_DOMAIN = "hedgehog-os:airline-a2-safe-package-index:v0.1"


def canonical_json_bytes_v01(value: object) -> bytes:
    return json.dumps(
        _plain(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8", errors="strict")


def canonical_json_line_v01(value: object) -> bytes:
    return canonical_json_bytes_v01(value) + b"\n"


def _plain(value: object) -> object:
    if is_dataclass(value):
        return {field.name: _plain(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    if type(value) in (tuple, list):
        return [_plain(item) for item in value]
    return value


def _identity(domain: str, plain: Mapping[str, object], slot: str) -> str:
    zeroed = dict(plain)
    zeroed[slot] = "0" * 64
    return hashlib.sha256(
        domain.encode("ascii") + b"\0" + canonical_json_bytes_v01(zeroed)
    ).hexdigest()


def _valid_sha(value: object) -> bool:
    return type(value) is str and LOWER_SHA256.fullmatch(value) is not None


def _valid_head(value: object) -> bool:
    return type(value) is str and LOWER_HEAD.fullmatch(value) is not None


def _inside_path(root: Path, candidate: Path) -> bool:
    try:
        return os.path.commonpath((str(root), str(candidate))) == str(root)
    except ValueError:
        return False


def _text(value: object) -> bool:
    return type(value) is str and value == value.strip() and bool(value)


def _exact_int(value: object, expected: int | None = None) -> bool:
    return type(value) is int and value >= 0 and (expected is None or value == expected)


def _hydrate_value(expected_type: object, value: object) -> object:
    origin = get_origin(expected_type)
    args = get_args(expected_type)
    if origin in (tuple, list):
        if type(value) is not list:
            raise ValueError("airline_a2_hydration_invalid")
        item_type = args[0] if args else object
        hydrated = tuple(_hydrate_value(item_type, item) for item in value)
        return list(hydrated) if origin is list else hydrated
    if origin in (dict, Mapping):
        if type(value) is not dict:
            raise ValueError("airline_a2_hydration_invalid")
        key_type, item_type = args if len(args) == 2 else (object, object)
        return {
            _hydrate_value(key_type, key): _hydrate_value(item_type, item)
            for key, item in value.items()
        }
    if origin in (UnionType,) or str(origin).endswith("typing.Union"):
        for item_type in args:
            try:
                return _hydrate_value(item_type, value)
            except (TypeError, ValueError):
                continue
        raise ValueError("airline_a2_hydration_invalid")
    if isinstance(expected_type, type) and is_dataclass(expected_type):
        return _hydrate_dataclass(expected_type, value)
    if expected_type is Any or expected_type is object:
        return value
    if expected_type is type(None):
        if value is not None:
            raise ValueError("airline_a2_hydration_invalid")
        return None
    if expected_type in (str, int, float, bool, bytes):
        if type(value) is not expected_type:
            raise ValueError("airline_a2_hydration_invalid")
    return value


def _hydrate_dataclass(contract_type: type[Any], value: object) -> Any:
    if type(value) is not dict:
        raise ValueError("airline_a2_hydration_invalid")
    expected_names = tuple(field.name for field in fields(contract_type))
    if frozenset(value) != frozenset(expected_names):
        raise ValueError("airline_a2_hydration_invalid")
    hints = get_type_hints(contract_type)
    return contract_type(
        **{
            name: _hydrate_value(hints.get(name, object), value[name])
            for name in expected_names
        }
    )


@dataclass(frozen=True, slots=True)
class AirlineA2LocalNonpublicationSourceV01:
    source_variant: str
    source_identity_id: str
    attempt_number: int
    attempt_id: str
    execution_head: str
    implementation_content_sha256: str
    attempt_identity_sha256: str
    private_inventory_sha256: str
    private_inventory_digest: str
    generation_gate_sha256: str
    corridor_archive_logical_name: str
    corridor_archive_sha256: str
    corridor_archive_byte_count: int
    safe_report_logical_name: str
    safe_report_sha256: str
    safe_report_byte_count: int
    safe_execution_id: str
    execution_mode: str
    safe_execution_compatibility_provider_mode: str
    model_id: str
    provider_application_call_mode: str
    actor_ids: tuple[str, ...]
    wrapper_callback_observed_count: int
    provider_callback_started_count: int
    provider_callback_completed_count: int
    collector_invocation_count: int
    deterministic_airline_collection_count: int
    ticket_purchase_corridor_execution_count: int
    airline_transaction_artifact_ledger_collection_count: int
    airline_crypto_artifact_seal_collection_count: int
    outbound_provider_sdk_call_count: int
    outbound_network_call_count: int
    outbound_gemini_call_count: int
    real_world_effects_count: int
    official_evidence_eligible: bool
    validation_errors: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class AirlineA2OfficialAcceptedSourceV01:
    source_variant: str
    source_identity_id: str
    attempt_number: int
    attempt_id: str
    execution_head: str
    attempt_identity_sha256: str
    private_inventory_sha256: str
    private_inventory_digest: str
    generation_gate_sha256: str
    corridor_archive_logical_name: str
    corridor_archive_sha256: str
    corridor_archive_byte_count: int
    public_safe_report_path: str
    public_safe_report_sha256: str
    public_safe_report_byte_count: int
    safe_execution_id: str
    generation_audit_path: str
    generation_audit_sha256: str
    accepted_audit_status: str
    accepted_audit_disposition: str
    provider_mode: str
    model_id: str
    provider_application_call_mode: str
    actor_ids: tuple[str, ...]
    wrapper_callback_observed_count: int
    provider_callback_started_count: int
    provider_callback_completed_count: int
    provider_call_count: int
    network_call_count: int
    gemini_call_count: int
    collector_invocation_count: int
    deterministic_airline_collection_count: int
    ticket_purchase_corridor_execution_count: int
    airline_transaction_artifact_ledger_collection_count: int
    airline_crypto_artifact_seal_collection_count: int
    duplicate_actor_call_count: int
    retry_count: int
    fallback_call_count: int
    package_created_count: int
    anchor_created_count: int
    replay_created_count: int
    real_world_effects_count: int
    official_evidence_eligible: bool
    validation_errors: tuple[str, ...]


def build_airline_a2_local_nonpublication_source_v01(
    *,
    attempt_id: str,
    execution_head: str,
    implementation_content_sha256: str,
    attempt_identity_sha256: str,
    private_inventory_sha256: str,
    private_inventory_digest: str,
    generation_gate_sha256: str,
    corridor_archive_sha256: str,
    corridor_archive_byte_count: int,
    safe_report_sha256: str,
    safe_report_byte_count: int,
    safe_execution_id: str,
    wrapper_callback_observed_count: int,
    provider_callback_started_count: int,
    provider_callback_completed_count: int,
    collector_invocation_count: int,
    deterministic_airline_collection_count: int,
    ticket_purchase_corridor_execution_count: int,
    airline_transaction_artifact_ledger_collection_count: int,
    airline_crypto_artifact_seal_collection_count: int,
    outbound_provider_sdk_call_count: int,
    outbound_network_call_count: int,
    outbound_gemini_call_count: int,
    real_world_effects_count: int,
) -> AirlineA2LocalNonpublicationSourceV01:
    provisional = AirlineA2LocalNonpublicationSourceV01(
        source_variant=SOURCE_LOCAL,
        source_identity_id="0" * 64,
        attempt_number=4,
        attempt_id=attempt_id,
        execution_head=execution_head,
        implementation_content_sha256=implementation_content_sha256,
        attempt_identity_sha256=attempt_identity_sha256,
        private_inventory_sha256=private_inventory_sha256,
        private_inventory_digest=private_inventory_digest,
        generation_gate_sha256=generation_gate_sha256,
        corridor_archive_logical_name=CORRIDOR_ARCHIVE_LOGICAL_NAME,
        corridor_archive_sha256=corridor_archive_sha256,
        corridor_archive_byte_count=corridor_archive_byte_count,
        safe_report_logical_name=LOCAL_SAFE_REPORT_LOGICAL_NAME,
        safe_report_sha256=safe_report_sha256,
        safe_report_byte_count=safe_report_byte_count,
        safe_execution_id=safe_execution_id,
        execution_mode="simulated_real",
        safe_execution_compatibility_provider_mode="real_provider",
        model_id=MODEL_ID,
        provider_application_call_mode=APPLICATION_CALL_MODE,
        actor_ids=ACTOR_IDS,
        wrapper_callback_observed_count=wrapper_callback_observed_count,
        provider_callback_started_count=provider_callback_started_count,
        provider_callback_completed_count=provider_callback_completed_count,
        collector_invocation_count=collector_invocation_count,
        deterministic_airline_collection_count=deterministic_airline_collection_count,
        ticket_purchase_corridor_execution_count=ticket_purchase_corridor_execution_count,
        airline_transaction_artifact_ledger_collection_count=(
            airline_transaction_artifact_ledger_collection_count
        ),
        airline_crypto_artifact_seal_collection_count=(
            airline_crypto_artifact_seal_collection_count
        ),
        outbound_provider_sdk_call_count=outbound_provider_sdk_call_count,
        outbound_network_call_count=outbound_network_call_count,
        outbound_gemini_call_count=outbound_gemini_call_count,
        real_world_effects_count=real_world_effects_count,
        official_evidence_eligible=False,
        validation_errors=(),
    )
    result = replace(
        provisional,
        source_identity_id=_identity(
            SOURCE_DOMAIN_LOCAL,
            _plain(provisional),
            "source_identity_id",
        ),
    )
    if validate_airline_a2_local_nonpublication_source_v01(result):
        raise ValueError("airline_a2_local_source_invalid")
    return result


def validate_airline_a2_local_nonpublication_source_v01(source: object) -> tuple[str, ...]:
    if type(source) is not AirlineA2LocalNonpublicationSourceV01:
        return ("airline_a2_local_source_invalid",)
    hashes = (
        source.source_identity_id,
        source.implementation_content_sha256,
        source.attempt_identity_sha256,
        source.private_inventory_sha256,
        source.private_inventory_digest,
        source.generation_gate_sha256,
        source.corridor_archive_sha256,
        source.safe_report_sha256,
        source.safe_execution_id,
    )
    geometry = (
        source.wrapper_callback_observed_count,
        source.provider_callback_started_count,
        source.provider_callback_completed_count,
        source.collector_invocation_count,
        source.deterministic_airline_collection_count,
        source.ticket_purchase_corridor_execution_count,
        source.airline_transaction_artifact_ledger_collection_count,
        source.airline_crypto_artifact_seal_collection_count,
        source.outbound_provider_sdk_call_count,
        source.outbound_network_call_count,
        source.outbound_gemini_call_count,
        source.real_world_effects_count,
    )
    valid = (
        source.source_variant == SOURCE_LOCAL
        and source.attempt_number == 4
        and type(source.attempt_number) is int
        and _text(source.attempt_id)
        and _valid_head(source.execution_head)
        and all(_valid_sha(value) for value in hashes)
        and source.corridor_archive_logical_name == CORRIDOR_ARCHIVE_LOGICAL_NAME
        and _exact_int(source.corridor_archive_byte_count)
        and source.corridor_archive_byte_count > 0
        and source.safe_report_logical_name == LOCAL_SAFE_REPORT_LOGICAL_NAME
        and _exact_int(source.safe_report_byte_count)
        and source.safe_report_byte_count > 0
        and source.execution_mode == "simulated_real"
        and source.safe_execution_compatibility_provider_mode == "real_provider"
        and source.model_id == MODEL_ID
        and source.provider_application_call_mode == APPLICATION_CALL_MODE
        and source.actor_ids == ACTOR_IDS
        and geometry == (12, 12, 12, 1, 1, 1, 1, 1, 0, 0, 0, 0)
        and source.official_evidence_eligible is False
        and source.validation_errors == ()
        and source.source_identity_id
        == _identity(SOURCE_DOMAIN_LOCAL, _plain(source), "source_identity_id")
    )
    return () if valid else ("airline_a2_local_source_invalid",)


def airline_a2_local_nonpublication_source_to_plain_dict_v01(
    source: AirlineA2LocalNonpublicationSourceV01,
) -> dict[str, object]:
    if validate_airline_a2_local_nonpublication_source_v01(source):
        raise ValueError("airline_a2_local_source_invalid")
    return _plain(source)  # type: ignore[return-value]


def build_airline_a2_official_accepted_source_v01(**values: object) -> AirlineA2OfficialAcceptedSourceV01:
    fixed = {
        "source_variant": SOURCE_OFFICIAL,
        "source_identity_id": "0" * 64,
        "attempt_number": 4,
        "corridor_archive_logical_name": CORRIDOR_ARCHIVE_LOGICAL_NAME,
        "accepted_audit_status": "CLOSED_PASS",
        "accepted_audit_disposition": (
            "ACCEPT_FOR_A2_AIRLINE_SEAL_WITH_BOUNDED_NON_EFFECT_SCOPE"
        ),
        "provider_mode": "real_provider",
        "model_id": MODEL_ID,
        "provider_application_call_mode": APPLICATION_CALL_MODE,
        "actor_ids": ACTOR_IDS,
        "official_evidence_eligible": True,
        "validation_errors": (),
    }
    unexpected = set(values).intersection(fixed)
    if unexpected:
        raise ValueError("airline_a2_official_source_invalid")
    try:
        provisional = AirlineA2OfficialAcceptedSourceV01(**fixed, **values)
    except (TypeError, ValueError):
        raise ValueError("airline_a2_official_source_invalid") from None
    result = replace(
        provisional,
        source_identity_id=_identity(
            SOURCE_DOMAIN_OFFICIAL,
            _plain(provisional),
            "source_identity_id",
        ),
    )
    if validate_airline_a2_official_accepted_source_v01(result):
        raise ValueError("airline_a2_official_source_invalid")
    return result


def validate_airline_a2_official_accepted_source_v01(source: object) -> tuple[str, ...]:
    if type(source) is not AirlineA2OfficialAcceptedSourceV01:
        return ("airline_a2_official_source_invalid",)
    hashes = tuple(
        getattr(source, name)
        for name in (
            "source_identity_id",
            "attempt_identity_sha256",
            "private_inventory_sha256",
            "private_inventory_digest",
            "generation_gate_sha256",
            "corridor_archive_sha256",
            "public_safe_report_sha256",
            "safe_execution_id",
            "generation_audit_sha256",
        )
    )
    one_counts = (
        source.collector_invocation_count,
        source.deterministic_airline_collection_count,
        source.ticket_purchase_corridor_execution_count,
        source.airline_transaction_artifact_ledger_collection_count,
        source.airline_crypto_artifact_seal_collection_count,
    )
    zero_counts = (
        source.duplicate_actor_call_count,
        source.retry_count,
        source.fallback_call_count,
        source.package_created_count,
        source.anchor_created_count,
        source.replay_created_count,
        source.real_world_effects_count,
    )
    valid = (
        source.source_variant == SOURCE_OFFICIAL
        and source.attempt_number == 4
        and type(source.attempt_number) is int
        and _text(source.attempt_id)
        and _valid_head(source.execution_head)
        and all(_valid_sha(value) for value in hashes)
        and source.corridor_archive_logical_name == CORRIDOR_ARCHIVE_LOGICAL_NAME
        and _exact_int(source.corridor_archive_byte_count)
        and source.corridor_archive_byte_count > 0
        and _text(source.public_safe_report_path)
        and _exact_int(source.public_safe_report_byte_count)
        and source.public_safe_report_byte_count > 0
        and _text(source.generation_audit_path)
        and source.accepted_audit_status == "CLOSED_PASS"
        and source.accepted_audit_disposition
        == "ACCEPT_FOR_A2_AIRLINE_SEAL_WITH_BOUNDED_NON_EFFECT_SCOPE"
        and source.provider_mode == "real_provider"
        and source.model_id == MODEL_ID
        and source.provider_application_call_mode == APPLICATION_CALL_MODE
        and source.actor_ids == ACTOR_IDS
        and (
            source.wrapper_callback_observed_count,
            source.provider_callback_started_count,
            source.provider_callback_completed_count,
            source.provider_call_count,
            source.network_call_count,
            source.gemini_call_count,
        )
        == (12, 12, 12, 12, 12, 12)
        and one_counts == (1, 1, 1, 1, 1)
        and zero_counts == (0, 0, 0, 0, 0, 0, 0)
        and source.official_evidence_eligible is True
        and source.validation_errors == ()
        and source.source_identity_id
        == _identity(SOURCE_DOMAIN_OFFICIAL, _plain(source), "source_identity_id")
    )
    return () if valid else ("airline_a2_official_source_invalid",)


def airline_a2_official_accepted_source_to_plain_dict_v01(
    source: AirlineA2OfficialAcceptedSourceV01,
) -> dict[str, object]:
    if validate_airline_a2_official_accepted_source_v01(source):
        raise ValueError("airline_a2_official_source_invalid")
    return _plain(source)  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class AirlineA2LocalPrecommitPackageInvocationV01:
    invocation_variant: str
    package_invocation_id: str
    base_head: str
    implementation_content_sha256: str
    local_source_identity_id: str
    package_id: str
    logical_package_ref: str
    package_output_ref: str
    package_index_output_ref: str


@dataclass(frozen=True, slots=True)
class AirlineA2LocalCommittedPackageInvocationV01:
    invocation_variant: str
    package_invocation_id: str
    committed_head: str
    origin_main_head: str
    implementation_content_sha256: str
    local_source_identity_id: str
    package_id: str
    logical_package_ref: str
    package_output_ref: str
    package_index_output_ref: str
    official_publication_claimed: bool


@dataclass(frozen=True, slots=True)
class AirlineA2OfficialPackageInvocationV01:
    invocation_variant: str
    package_invocation_id: str
    official_source_identity_id: str
    implementation_head: str
    publication_base_head: str
    package_id: str
    logical_package_ref: str
    package_output_ref: str
    package_index_output_ref: str


def _invocation_domain(variant: str) -> str:
    return f"hedgehog-os:airline-a2-package-invocation:v0.1:{variant}"


def build_airline_a2_local_precommit_package_invocation_v01(
    *,
    base_head: str,
    implementation_content_sha256: str,
    local_source_identity_id: str,
) -> AirlineA2LocalPrecommitPackageInvocationV01:
    logical = (
        f"airline/a2/local/precommit/{local_source_identity_id}/"
        f"{implementation_content_sha256}"
    )
    provisional = AirlineA2LocalPrecommitPackageInvocationV01(
        invocation_variant=INVOCATION_LOCAL_PRECOMMIT,
        package_invocation_id="0" * 64,
        base_head=base_head,
        implementation_content_sha256=implementation_content_sha256,
        local_source_identity_id=local_source_identity_id,
        package_id=(
            f"airline_a2_local_precommit_package:{local_source_identity_id}:"
            f"{implementation_content_sha256}"
        ),
        logical_package_ref=logical,
        package_output_ref=f"{logical}/package",
        package_index_output_ref=f"{logical}/package-index",
    )
    result = replace(
        provisional,
        package_invocation_id=_identity(
            _invocation_domain(INVOCATION_LOCAL_PRECOMMIT),
            _plain(provisional),
            "package_invocation_id",
        ),
    )
    if validate_airline_a2_local_precommit_package_invocation_v01(result):
        raise ValueError("airline_a2_package_invocation_invalid")
    return result


def validate_airline_a2_local_precommit_package_invocation_v01(
    invocation: object,
) -> tuple[str, ...]:
    if type(invocation) is not AirlineA2LocalPrecommitPackageInvocationV01:
        return ("airline_a2_package_invocation_invalid",)
    valid = (
        invocation.invocation_variant == INVOCATION_LOCAL_PRECOMMIT
        and _valid_head(invocation.base_head)
        and _valid_sha(invocation.implementation_content_sha256)
        and _valid_sha(invocation.local_source_identity_id)
        and _text(invocation.package_id)
        and _text(invocation.logical_package_ref)
        and invocation.package_output_ref == f"{invocation.logical_package_ref}/package"
        and invocation.package_index_output_ref
        == f"{invocation.logical_package_ref}/package-index"
        and invocation.package_id
        == (
            "airline_a2_local_precommit_package:"
            f"{invocation.local_source_identity_id}:"
            f"{invocation.implementation_content_sha256}"
        )
        and invocation.logical_package_ref
        == (
            f"airline/a2/local/precommit/{invocation.local_source_identity_id}/"
            f"{invocation.implementation_content_sha256}"
        )
        and invocation.package_invocation_id
        == _identity(
            _invocation_domain(INVOCATION_LOCAL_PRECOMMIT),
            _plain(invocation),
            "package_invocation_id",
        )
    )
    return () if valid else ("airline_a2_package_invocation_invalid",)


def airline_a2_local_precommit_package_invocation_to_plain_dict_v01(
    invocation: AirlineA2LocalPrecommitPackageInvocationV01,
) -> dict[str, object]:
    if validate_airline_a2_local_precommit_package_invocation_v01(invocation):
        raise ValueError("airline_a2_package_invocation_invalid")
    return _plain(invocation)  # type: ignore[return-value]


def build_airline_a2_local_committed_package_invocation_v01(
    *,
    committed_head: str,
    origin_main_head: str,
    implementation_content_sha256: str,
    local_source_identity_id: str,
) -> AirlineA2LocalCommittedPackageInvocationV01:
    logical = (
        f"airline/a2/local/committed/{local_source_identity_id}/"
        f"{committed_head}/{implementation_content_sha256}"
    )
    provisional = AirlineA2LocalCommittedPackageInvocationV01(
        invocation_variant=INVOCATION_LOCAL_COMMITTED,
        package_invocation_id="0" * 64,
        committed_head=committed_head,
        origin_main_head=origin_main_head,
        implementation_content_sha256=implementation_content_sha256,
        local_source_identity_id=local_source_identity_id,
        package_id=(
            f"airline_a2_local_committed_package:{local_source_identity_id}:"
            f"{committed_head}:{implementation_content_sha256}"
        ),
        logical_package_ref=logical,
        package_output_ref=f"{logical}/package",
        package_index_output_ref=f"{logical}/package-index",
        official_publication_claimed=False,
    )
    result = replace(
        provisional,
        package_invocation_id=_identity(
            _invocation_domain(INVOCATION_LOCAL_COMMITTED),
            _plain(provisional),
            "package_invocation_id",
        ),
    )
    if validate_airline_a2_local_committed_package_invocation_v01(result):
        raise ValueError("airline_a2_package_invocation_invalid")
    return result


def validate_airline_a2_local_committed_package_invocation_v01(
    invocation: object,
) -> tuple[str, ...]:
    if type(invocation) is not AirlineA2LocalCommittedPackageInvocationV01:
        return ("airline_a2_package_invocation_invalid",)
    valid = (
        invocation.invocation_variant == INVOCATION_LOCAL_COMMITTED
        and _valid_head(invocation.committed_head)
        and invocation.origin_main_head == invocation.committed_head
        and _valid_sha(invocation.implementation_content_sha256)
        and _valid_sha(invocation.local_source_identity_id)
        and invocation.official_publication_claimed is False
        and invocation.package_id
        == (
            "airline_a2_local_committed_package:"
            f"{invocation.local_source_identity_id}:{invocation.committed_head}:"
            f"{invocation.implementation_content_sha256}"
        )
        and invocation.logical_package_ref
        == (
            f"airline/a2/local/committed/{invocation.local_source_identity_id}/"
            f"{invocation.committed_head}/{invocation.implementation_content_sha256}"
        )
        and invocation.package_output_ref == f"{invocation.logical_package_ref}/package"
        and invocation.package_index_output_ref
        == f"{invocation.logical_package_ref}/package-index"
        and invocation.package_invocation_id
        == _identity(
            _invocation_domain(INVOCATION_LOCAL_COMMITTED),
            _plain(invocation),
            "package_invocation_id",
        )
    )
    return () if valid else ("airline_a2_package_invocation_invalid",)


def airline_a2_local_committed_package_invocation_to_plain_dict_v01(
    invocation: AirlineA2LocalCommittedPackageInvocationV01,
) -> dict[str, object]:
    if validate_airline_a2_local_committed_package_invocation_v01(invocation):
        raise ValueError("airline_a2_package_invocation_invalid")
    return _plain(invocation)  # type: ignore[return-value]


def build_airline_a2_official_package_invocation_v01(
    *,
    official_source_identity_id: str,
    implementation_head: str,
    publication_base_head: str,
) -> AirlineA2OfficialPackageInvocationV01:
    logical = (
        f"airline/a2/official/attempt-04/{official_source_identity_id}/"
        f"{publication_base_head}"
    )
    provisional = AirlineA2OfficialPackageInvocationV01(
        invocation_variant=INVOCATION_OFFICIAL,
        package_invocation_id="0" * 64,
        official_source_identity_id=official_source_identity_id,
        implementation_head=implementation_head,
        publication_base_head=publication_base_head,
        package_id=(
            f"airline_a2_official_package:{official_source_identity_id}:"
            f"{publication_base_head}"
        ),
        logical_package_ref=logical,
        package_output_ref=OFFICIAL_PACKAGE_ROOT,
        package_index_output_ref=OFFICIAL_PACKAGE_INDEX,
    )
    result = replace(
        provisional,
        package_invocation_id=_identity(
            _invocation_domain(INVOCATION_OFFICIAL),
            _plain(provisional),
            "package_invocation_id",
        ),
    )
    if validate_airline_a2_official_package_invocation_v01(result):
        raise ValueError("airline_a2_package_invocation_invalid")
    return result


def validate_airline_a2_official_package_invocation_v01(
    invocation: object,
) -> tuple[str, ...]:
    if type(invocation) is not AirlineA2OfficialPackageInvocationV01:
        return ("airline_a2_package_invocation_invalid",)
    valid = (
        invocation.invocation_variant == INVOCATION_OFFICIAL
        and _valid_sha(invocation.official_source_identity_id)
        and _valid_head(invocation.implementation_head)
        and _valid_head(invocation.publication_base_head)
        and invocation.package_id
        == (
            f"airline_a2_official_package:{invocation.official_source_identity_id}:"
            f"{invocation.publication_base_head}"
        )
        and invocation.logical_package_ref
        == (
            f"airline/a2/official/attempt-04/{invocation.official_source_identity_id}/"
            f"{invocation.publication_base_head}"
        )
        and invocation.package_output_ref == OFFICIAL_PACKAGE_ROOT
        and invocation.package_index_output_ref == OFFICIAL_PACKAGE_INDEX
        and invocation.package_invocation_id
        == _identity(
            _invocation_domain(INVOCATION_OFFICIAL),
            _plain(invocation),
            "package_invocation_id",
        )
    )
    return () if valid else ("airline_a2_package_invocation_invalid",)


def airline_a2_official_package_invocation_to_plain_dict_v01(
    invocation: AirlineA2OfficialPackageInvocationV01,
) -> dict[str, object]:
    if validate_airline_a2_official_package_invocation_v01(invocation):
        raise ValueError("airline_a2_package_invocation_invalid")
    return _plain(invocation)  # type: ignore[return-value]


@dataclass(frozen=True, slots=True)
class AirlineA2LocalProcessAResultV01:
    result_id: str
    result_version: str
    gate_phase: str
    verified_head_token: str
    implementation_content_sha256: str
    attempt_id: str
    execution_head: str
    attempt_identity_sha256: str
    private_inventory_sha256: str
    private_inventory_digest: str
    generation_gate_sha256: str
    corridor_archive_logical_name: str
    corridor_archive_sha256: str
    corridor_archive_byte_count: int
    safe_report_logical_name: str
    safe_report_sha256: str
    safe_report_byte_count: int
    safe_execution_id: str
    wrapper_callback_observed_count: int
    provider_callback_started_count: int
    provider_callback_completed_count: int
    semantic_actor_call_count: int
    causal_actor_call_count: int
    generic_actor_call_count: int
    duplicate_actor_call_count: int
    collector_invocation_count: int
    deterministic_airline_collection_count: int
    ticket_purchase_corridor_execution_count: int
    airline_transaction_artifact_ledger_collection_count: int
    airline_crypto_artifact_seal_collection_count: int
    outbound_provider_sdk_call_count: int
    outbound_network_call_count: int
    outbound_gemini_call_count: int
    real_world_effects_count: int
    final_status: str
    validation_errors: tuple[str, ...]


def build_airline_a2_local_process_a_result_v01(
    *,
    gate_phase: str,
    verified_head_token: str,
    implementation_content_sha256: str,
    attempt_id: str,
    execution_head: str,
    attempt_identity_sha256: str,
    private_inventory_sha256: str,
    private_inventory_digest: str,
    generation_gate_sha256: str,
    corridor_archive_sha256: str,
    corridor_archive_byte_count: int,
    safe_report_sha256: str,
    safe_report_byte_count: int,
    safe_execution_id: str,
    wrapper_callback_observed_count: int,
    provider_callback_started_count: int,
    provider_callback_completed_count: int,
    semantic_actor_call_count: int,
    causal_actor_call_count: int,
    generic_actor_call_count: int,
    duplicate_actor_call_count: int,
    collector_invocation_count: int,
    deterministic_airline_collection_count: int,
    ticket_purchase_corridor_execution_count: int,
    airline_transaction_artifact_ledger_collection_count: int,
    airline_crypto_artifact_seal_collection_count: int,
    outbound_provider_sdk_call_count: int,
    outbound_network_call_count: int,
    outbound_gemini_call_count: int,
    real_world_effects_count: int,
) -> AirlineA2LocalProcessAResultV01:
    provisional = AirlineA2LocalProcessAResultV01(
        result_id="0" * 64,
        result_version=VERSION,
        gate_phase=gate_phase,
        verified_head_token=verified_head_token,
        implementation_content_sha256=implementation_content_sha256,
        attempt_id=attempt_id,
        execution_head=execution_head,
        attempt_identity_sha256=attempt_identity_sha256,
        private_inventory_sha256=private_inventory_sha256,
        private_inventory_digest=private_inventory_digest,
        generation_gate_sha256=generation_gate_sha256,
        corridor_archive_logical_name=CORRIDOR_ARCHIVE_LOGICAL_NAME,
        corridor_archive_sha256=corridor_archive_sha256,
        corridor_archive_byte_count=corridor_archive_byte_count,
        safe_report_logical_name=LOCAL_SAFE_REPORT_LOGICAL_NAME,
        safe_report_sha256=safe_report_sha256,
        safe_report_byte_count=safe_report_byte_count,
        safe_execution_id=safe_execution_id,
        wrapper_callback_observed_count=wrapper_callback_observed_count,
        provider_callback_started_count=provider_callback_started_count,
        provider_callback_completed_count=provider_callback_completed_count,
        semantic_actor_call_count=semantic_actor_call_count,
        causal_actor_call_count=causal_actor_call_count,
        generic_actor_call_count=generic_actor_call_count,
        duplicate_actor_call_count=duplicate_actor_call_count,
        collector_invocation_count=collector_invocation_count,
        deterministic_airline_collection_count=deterministic_airline_collection_count,
        ticket_purchase_corridor_execution_count=ticket_purchase_corridor_execution_count,
        airline_transaction_artifact_ledger_collection_count=(
            airline_transaction_artifact_ledger_collection_count
        ),
        airline_crypto_artifact_seal_collection_count=(
            airline_crypto_artifact_seal_collection_count
        ),
        outbound_provider_sdk_call_count=outbound_provider_sdk_call_count,
        outbound_network_call_count=outbound_network_call_count,
        outbound_gemini_call_count=outbound_gemini_call_count,
        real_world_effects_count=real_world_effects_count,
        final_status=STATUS_PASS,
        validation_errors=(),
    )
    result = replace(
        provisional,
        result_id=_identity(PROCESS_A_DOMAIN, _plain(provisional), "result_id"),
    )
    if validate_airline_a2_local_process_a_result_v01(result):
        raise ValueError("airline_a2_process_a_result_invalid")
    return result


def validate_airline_a2_local_process_a_result_v01(result: object) -> tuple[str, ...]:
    if type(result) is not AirlineA2LocalProcessAResultV01:
        return ("airline_a2_process_a_result_invalid",)
    hashes = (
        result.result_id,
        result.implementation_content_sha256,
        result.attempt_identity_sha256,
        result.private_inventory_sha256,
        result.private_inventory_digest,
        result.generation_gate_sha256,
        result.corridor_archive_sha256,
        result.safe_report_sha256,
        result.safe_execution_id,
    )
    valid = (
        result.result_version == VERSION
        and result.gate_phase in (GATE_PHASE_PRECOMMIT, GATE_PHASE_COMMITTED)
        and _valid_head(result.verified_head_token)
        and _text(result.attempt_id)
        and _valid_head(result.execution_head)
        and all(_valid_sha(value) for value in hashes)
        and result.corridor_archive_logical_name == CORRIDOR_ARCHIVE_LOGICAL_NAME
        and _exact_int(result.corridor_archive_byte_count)
        and result.corridor_archive_byte_count > 0
        and result.safe_report_logical_name == LOCAL_SAFE_REPORT_LOGICAL_NAME
        and _exact_int(result.safe_report_byte_count)
        and result.safe_report_byte_count > 0
        and (
            result.wrapper_callback_observed_count,
            result.provider_callback_started_count,
            result.provider_callback_completed_count,
            result.semantic_actor_call_count,
            result.causal_actor_call_count,
            result.generic_actor_call_count,
            result.duplicate_actor_call_count,
            result.collector_invocation_count,
            result.deterministic_airline_collection_count,
            result.ticket_purchase_corridor_execution_count,
            result.airline_transaction_artifact_ledger_collection_count,
            result.airline_crypto_artifact_seal_collection_count,
            result.outbound_provider_sdk_call_count,
            result.outbound_network_call_count,
            result.outbound_gemini_call_count,
            result.real_world_effects_count,
        )
        == (12, 12, 12, 12, 5, 7, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0)
        and result.final_status == STATUS_PASS
        and result.validation_errors == ()
        and result.result_id == _identity(PROCESS_A_DOMAIN, _plain(result), "result_id")
    )
    return () if valid else ("airline_a2_process_a_result_invalid",)


def airline_a2_local_process_a_result_to_plain_dict_v01(
    result: AirlineA2LocalProcessAResultV01,
) -> dict[str, object]:
    if validate_airline_a2_local_process_a_result_v01(result):
        raise ValueError("airline_a2_process_a_result_invalid")
    return _plain(result)  # type: ignore[return-value]


def airline_a2_local_process_a_result_from_plain_dict_v01(
    plain: Mapping[str, object],
) -> AirlineA2LocalProcessAResultV01:
    if type(plain) is not dict or set(plain) != {
        field.name for field in fields(AirlineA2LocalProcessAResultV01)
    }:
        raise ValueError("airline_a2_process_a_result_invalid")
    values = dict(plain)
    if type(values.get("validation_errors")) is not list:
        raise ValueError("airline_a2_process_a_result_invalid")
    values["validation_errors"] = tuple(values["validation_errors"])
    try:
        result = AirlineA2LocalProcessAResultV01(**values)
    except (TypeError, ValueError):
        raise ValueError("airline_a2_process_a_result_invalid") from None
    if validate_airline_a2_local_process_a_result_v01(result):
        raise ValueError("airline_a2_process_a_result_invalid")
    return result


def _ordered_file_rows(
    ordered_source_files: tuple[tuple[str, bytes], ...],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    if type(ordered_source_files) is not tuple:
        raise ValueError("airline_a2_ordered_source_files_invalid")
    for logical_name, content in ordered_source_files:
        if not _text(logical_name) or type(content) is not bytes:
            raise ValueError("airline_a2_ordered_source_files_invalid")
        encoded = base64.b64encode(content).decode("ascii")
        if base64.b64decode(encoded, validate=True) != content:
            raise ValueError("airline_a2_ordered_source_files_invalid")
        rows.append(
            {
                "base64": encoded,
                "byte_count": len(content),
                "logical_name": logical_name,
                "sha256": hashlib.sha256(content).hexdigest(),
            }
        )
    return rows


def hydrate_airline_a2_ordered_source_files_v01(
    rows: object,
) -> tuple[tuple[str, bytes], ...]:
    if type(rows) is not list:
        raise ValueError("airline_a2_ordered_source_files_invalid")
    hydrated: list[tuple[str, bytes]] = []
    for row in rows:
        if type(row) is not dict or set(row) != {
            "base64",
            "byte_count",
            "logical_name",
            "sha256",
        }:
            raise ValueError("airline_a2_ordered_source_files_invalid")
        if (
            not _text(row["logical_name"])
            or type(row["base64"]) is not str
            or any(character.isspace() for character in row["base64"])
            or not _exact_int(row["byte_count"])
            or not _valid_sha(row["sha256"])
        ):
            raise ValueError("airline_a2_ordered_source_files_invalid")
        try:
            content = base64.b64decode(row["base64"], validate=True)
        except (ValueError, TypeError):
            raise ValueError("airline_a2_ordered_source_files_invalid") from None
        if (
            base64.b64encode(content).decode("ascii") != row["base64"]
            or len(content) != row["byte_count"]
            or hashlib.sha256(content).hexdigest() != row["sha256"]
        ):
            raise ValueError("airline_a2_ordered_source_files_invalid")
        hydrated.append((row["logical_name"], content))
    return tuple(hydrated)


def _source_and_invocation_identity(
    source: AirlineA2LocalNonpublicationSourceV01 | AirlineA2OfficialAcceptedSourceV01,
    invocation: AirlineA2LocalPrecommitPackageInvocationV01
    | AirlineA2LocalCommittedPackageInvocationV01
    | AirlineA2OfficialPackageInvocationV01,
) -> tuple[str, str, str]:
    if type(source) is AirlineA2LocalNonpublicationSourceV01:
        if validate_airline_a2_local_nonpublication_source_v01(source):
            raise ValueError("airline_a2_source_invalid")
        if type(invocation) is AirlineA2LocalPrecommitPackageInvocationV01:
            errors = validate_airline_a2_local_precommit_package_invocation_v01(invocation)
            source_id = invocation.local_source_identity_id
        elif type(invocation) is AirlineA2LocalCommittedPackageInvocationV01:
            errors = validate_airline_a2_local_committed_package_invocation_v01(invocation)
            source_id = invocation.local_source_identity_id
        else:
            raise ValueError("airline_a2_source_invocation_mismatch")
        if errors or source_id != source.source_identity_id:
            raise ValueError("airline_a2_source_invocation_mismatch")
        return SOURCE_LOCAL, source.source_identity_id, invocation.package_invocation_id
    if type(source) is AirlineA2OfficialAcceptedSourceV01:
        if validate_airline_a2_official_accepted_source_v01(source):
            raise ValueError("airline_a2_source_invalid")
        if (
            type(invocation) is not AirlineA2OfficialPackageInvocationV01
            or validate_airline_a2_official_package_invocation_v01(invocation)
            or invocation.official_source_identity_id != source.source_identity_id
            or invocation.implementation_head != source.execution_head
        ):
            raise ValueError("airline_a2_source_invocation_mismatch")
        return SOURCE_OFFICIAL, source.source_identity_id, invocation.package_invocation_id
    raise ValueError("airline_a2_source_invalid")


def build_airline_a2_member_02_lineage_v01(
    *,
    source: AirlineA2LocalNonpublicationSourceV01 | AirlineA2OfficialAcceptedSourceV01,
    package_invocation: AirlineA2LocalPrecommitPackageInvocationV01
    | AirlineA2LocalCommittedPackageInvocationV01
    | AirlineA2OfficialPackageInvocationV01,
    source_record_ids: tuple[str, str, str],
) -> dict[str, object]:
    variant, source_id, invocation_id = _source_and_invocation_identity(
        source,
        package_invocation,
    )
    if (
        type(source_record_ids) is not tuple
        or len(source_record_ids) != 3
        or any(not _valid_sha(item) for item in source_record_ids)
    ):
        raise ValueError("airline_a2_lineage_invalid")
    if variant == SOURCE_LOCAL:
        plain: dict[str, object] = {
            "limitations": list(adapter._LOCAL_LIMITATIONS),
            "lineage_id": "0" * 64,
            "lineage_version": VERSION,
            "package_invocation_identity": _plain(package_invocation),
            "safe_report_binding": {
                "byte_count": source.safe_report_byte_count,
                "logical_name": source.safe_report_logical_name,
                "safe_execution_id": source.safe_execution_id,
                "sha256": source.safe_report_sha256,
            },
            "source_identity": _plain(source),
            "source_record_ids": list(source_record_ids),
            "source_variant": variant,
        }
    else:
        plain = {
            "generation_audit_binding": {
                "accepted_audit_disposition": source.accepted_audit_disposition,
                "accepted_audit_status": source.accepted_audit_status,
                "repository_relative_path": source.generation_audit_path,
                "sha256": source.generation_audit_sha256,
            },
            "limitations": list(adapter._LIMITATIONS),
            "lineage_id": "0" * 64,
            "lineage_version": VERSION,
            "safe_report_binding": {
                "byte_count": source.public_safe_report_byte_count,
                "official_evidence_eligible": True,
                "repository_relative_path": source.public_safe_report_path,
                "safe_execution_id": source.safe_execution_id,
                "sha256": source.public_safe_report_sha256,
            },
            "source_identity": _plain(source),
            "source_record_ids": list(source_record_ids),
            "source_variant": variant,
        }
    domain = f"hedgehog-os:airline-a2-member-02-lineage:v0.1:{variant}"
    plain["lineage_id"] = _identity(domain, plain, "lineage_id")
    return plain


def build_airline_a2_typed_context_v01(
    *,
    source: AirlineA2LocalNonpublicationSourceV01 | AirlineA2OfficialAcceptedSourceV01,
    package_invocation: AirlineA2LocalPrecommitPackageInvocationV01
    | AirlineA2LocalCommittedPackageInvocationV01
    | AirlineA2OfficialPackageInvocationV01,
    safe_execution: adapter.AirlineSafeExecutionProjectionV01,
    ledger_source_bundle: object,
    ledger_item: object,
    crypto_collection_result: object,
    replay_input: object,
    replay_report: object,
    kernel_adapter_result: object,
    ordered_source_files: tuple[tuple[str, bytes], ...],
) -> dict[str, object]:
    variant, source_id, invocation_id = _source_and_invocation_identity(
        source,
        package_invocation,
    )
    expected_identity = (
        ledger_collector.build_airline_transaction_artifact_ledger_expected_identity_from_source_v01(
            source_bundle=ledger_source_bundle
        )
    )
    safe_plain = adapter.airline_safe_execution_projection_to_plain_dict_v01(
        safe_execution
    )
    ledger_plain = crypto_collector.airline_crypto_artifact_seal_ledger_document_to_plain_dict_v01(
        ledger_item,
        expected_identity=expected_identity,
    )
    crypto_plain = crypto_collector.airline_crypto_artifact_seal_collection_result_to_plain_dict_v01(
        crypto_collection_result
    )
    replay_report_plain = replay.airline_sealed_trace_replay_report_to_plain_dict_v01(
        replay_report
    )
    kernel_plain = kernel_adapter.airline_kernel_adapter_result_to_plain_dict_v01(
        kernel_adapter_result
    )
    source_rows = _ordered_file_rows(ordered_source_files)
    replay_input_plain = _plain(replay_input)
    replay_input_plain["ordered_source_files"] = source_rows
    plain: dict[str, object] = {
        "crypto_source_projection": {
            "collection_result": crypto_plain,
            "ordered_source_files": source_rows,
        },
        "external_operation_counts": {
            "a2_effect_call_count": 0,
            "a2_gemini_call_count": 0,
            "a2_network_call_count": 0,
            "a2_provider_sdk_call_count": 0,
        },
        "historical_replay_input_projection": replay_input_plain,
        "historical_replay_report_projection": replay_report_plain,
        "kernel_adapter_projection": kernel_plain,
        "ledger_source_projection": {
            "ledger_item": ledger_plain,
            "source_bundle": _plain(ledger_source_bundle),
        },
        "package_invocation_id": invocation_id,
        "reconstruction_geometry": {
            "actor_count": 12,
            "corridor_delegation_count": 8,
            "corridor_phase_count": 5,
            "corridor_transition_count": 4,
            "critical_file_count": 11,
            "crypto_source_file_count": 9,
            "dependency_edge_count": 29,
            "ledger_entry_count": 19,
            "replay_timeline_row_count": 19,
            "root_final_count": 3,
            "source_record_count": 6,
        },
        "safe_execution_projection": safe_plain,
        "source_identity_id": source_id,
        "source_variant": variant,
        "typed_context_id": "0" * 64,
        "typed_context_version": VERSION,
        "validation_errors": [],
    }
    domain = f"hedgehog-os:airline-a2-member-03-typed-context:v0.1:{variant}"
    plain["typed_context_id"] = _identity(domain, plain, "typed_context_id")
    validate_airline_a2_typed_context_v01(plain)
    return plain


def validate_airline_a2_typed_context_v01(plain: object) -> tuple[str, ...]:
    keys = {
        "crypto_source_projection",
        "external_operation_counts",
        "historical_replay_input_projection",
        "historical_replay_report_projection",
        "kernel_adapter_projection",
        "ledger_source_projection",
        "package_invocation_id",
        "reconstruction_geometry",
        "safe_execution_projection",
        "source_identity_id",
        "source_variant",
        "typed_context_id",
        "typed_context_version",
        "validation_errors",
    }
    try:
        if type(plain) is not dict or set(plain) != keys:
            raise ValueError
        variant = plain["source_variant"]
        if variant not in (SOURCE_LOCAL, SOURCE_OFFICIAL):
            raise ValueError
        if (
            not _valid_sha(plain["typed_context_id"])
            or not _valid_sha(plain["source_identity_id"])
            or not _valid_sha(plain["package_invocation_id"])
            or plain["typed_context_version"] != VERSION
            or plain["validation_errors"] != []
        ):
            raise ValueError
        rows = plain["crypto_source_projection"]["ordered_source_files"]
        if len(hydrate_airline_a2_ordered_source_files_v01(rows)) != 9:
            raise ValueError
        replay_rows = plain["historical_replay_input_projection"][
            "ordered_source_files"
        ]
        if replay_rows != rows:
            raise ValueError
        domain = f"hedgehog-os:airline-a2-member-03-typed-context:v0.1:{variant}"
        if plain["typed_context_id"] != _identity(domain, plain, "typed_context_id"):
            raise ValueError
        canonical_json_bytes_v01(plain)
        return ()
    except (KeyError, TypeError, ValueError, UnicodeError, RecursionError):
        return ("airline_a2_typed_context_invalid",)


def build_airline_a2_adapter_projection_v01(
    *,
    source_variant: str,
    source_identity_id: str,
    package_invocation_id: str,
    adapter_result: adapter.AirlineSealedEvidencePackageAdapterResultV01,
) -> dict[str, object]:
    if source_variant not in (SOURCE_LOCAL, SOURCE_OFFICIAL):
        raise ValueError("airline_a2_adapter_projection_invalid")
    if not _valid_sha(source_identity_id) or not _valid_sha(package_invocation_id):
        raise ValueError("airline_a2_adapter_projection_invalid")
    domain_plain = profile.domain_evidence_projection_to_plain_dict_v01(
        adapter_result.domain_projection
    )
    adapter_plain = adapter._adapter_result_plain(adapter_result)
    plain: dict[str, object] = {
        "adapter_projection_id": "0" * 64,
        "adapter_projection_version": VERSION,
        "adapter_result": adapter_plain,
        "domain_evidence_projection": domain_plain,
        "package_invocation_id": package_invocation_id,
        "source_identity_id": source_identity_id,
        "source_record_ids": [
            item.source_record_id
            for item in adapter_result.domain_projection.source_records
        ],
        "source_variant": source_variant,
        "validation_result": {
            "adapter_status": adapter_result.status,
            "adapter_validation_errors": list(adapter_result.validation_errors),
            "domain_projection_status": adapter_result.domain_projection.status,
            "domain_projection_validation_errors": list(
                profile.validate_domain_evidence_projection_v01(
                    adapter_result.domain_projection
                )
            ),
        },
        "zero_effect_geometry": {
            "action_created_count": adapter_result.action_created_count,
            "created_authority_count": adapter_result.created_authority_count,
            "created_permission_count": adapter_result.created_permission_count,
            "final_output_created_count": adapter_result.final_output_created_count,
            "projection_created_authority_count": (
                adapter_result.domain_projection.created_authority_count
            ),
            "projection_created_permission_count": (
                adapter_result.domain_projection.created_permission_count
            ),
            "projection_real_world_effects_count": (
                adapter_result.domain_projection.real_world_effects_count
            ),
            "real_world_effects_count": adapter_result.real_world_effects_count,
            "receipt_created_count": adapter_result.receipt_created_count,
        },
    }
    domain = (
        "hedgehog-os:airline-a2-member-04-adapter-projection:"
        f"v0.1:{source_variant}"
    )
    plain["adapter_projection_id"] = _identity(
        domain,
        plain,
        "adapter_projection_id",
    )
    return plain


def build_airline_a2_adapter_result_v01(
    *,
    source: AirlineA2LocalNonpublicationSourceV01 | AirlineA2OfficialAcceptedSourceV01,
    package_invocation: AirlineA2LocalPrecommitPackageInvocationV01
    | AirlineA2LocalCommittedPackageInvocationV01
    | AirlineA2OfficialPackageInvocationV01,
    safe_execution: adapter.AirlineSafeExecutionProjectionV01,
    ledger_source_bundle: object,
    crypto_collection_result: object,
    replay_input: object,
    replay_report: object,
    kernel_adapter_result: object,
) -> adapter.AirlineSealedEvidencePackageAdapterResultV01:
    variant, _, _ = _source_and_invocation_identity(source, package_invocation)
    adapter_invocation = (
        adapter.build_airline_sealed_evidence_package_adapter_invocation_v01(
            invocation_mode=(
                adapter.INVOCATION_MODE_LOCAL_NONPUBLICATION
                if variant == SOURCE_LOCAL
                else adapter.INVOCATION_MODE_OFFICIAL_ACCEPTED
            ),
            package_id=package_invocation.package_id,
            logical_package_ref=package_invocation.logical_package_ref,
            output_directory_ref=package_invocation.package_output_ref,
        )
    )
    result = adapter.build_airline_sealed_evidence_package_adapter_result_for_invocation_v01(
        invocation=adapter_invocation,
        safe_execution=safe_execution,
        ledger_source_bundle=ledger_source_bundle,
        crypto_collection_result=crypto_collection_result,
        replay_input=replay_input,
        replay_report=replay_report,
        kernel_adapter_result=kernel_adapter_result,
    )
    errors = adapter.validate_airline_sealed_evidence_package_adapter_result_for_invocation_v01(
        result,
        invocation=adapter_invocation,
        safe_execution=safe_execution,
        ledger_source_bundle=ledger_source_bundle,
        crypto_collection_result=crypto_collection_result,
        replay_input=replay_input,
        replay_report=replay_report,
        kernel_adapter_result=kernel_adapter_result,
    )
    if errors or result.status != STATUS_PASS:
        raise ValueError("airline_a2_adapter_result_invalid")
    return result


@dataclass(frozen=True, slots=True)
class AirlineA2PackageMaterialV01:
    source_variant: str
    source_identity_id: str
    package_invocation_id: str
    member_contents: tuple[bytes, bytes, bytes, bytes]
    safe_file_records: tuple[sealed_package.SafeFileRecordV01, ...]
    adapter_result: adapter.AirlineSealedEvidencePackageAdapterResultV01
    domain_projection: profile.DomainEvidenceProjectionV01
    manifest: sealed_package.SealedPackageManifestV01
    typed_context_id: str
    adapter_projection_id: str
    adapter_result_id: str
    domain_projection_id: str


_MEMBER_PATHS = (
    "evidence/01-airline-safe-execution-report-v01.json",
    "evidence/02-airline-source-lineage-v01.json",
    "evidence/03-airline-a2-typed-context-v01.json",
    "evidence/04-airline-sealed-evidence-adapter-result-v01.json",
)


def build_airline_a2_package_material_v01(
    *,
    source: AirlineA2LocalNonpublicationSourceV01 | AirlineA2OfficialAcceptedSourceV01,
    package_invocation: AirlineA2LocalPrecommitPackageInvocationV01
    | AirlineA2LocalCommittedPackageInvocationV01
    | AirlineA2OfficialPackageInvocationV01,
    safe_report_bytes: bytes,
    safe_execution: adapter.AirlineSafeExecutionProjectionV01,
    ledger_source_bundle: object,
    ledger_item: object,
    crypto_collection_result: object,
    replay_input: object,
    replay_report: object,
    kernel_adapter_result: object,
    ordered_source_files: tuple[tuple[str, bytes], ...],
) -> AirlineA2PackageMaterialV01:
    variant, source_id, invocation_id = _source_and_invocation_identity(
        source,
        package_invocation,
    )
    if type(safe_report_bytes) is not bytes or not safe_report_bytes.endswith(b"\n"):
        raise ValueError("airline_a2_safe_report_invalid")
    expected_hash = (
        source.safe_report_sha256
        if type(source) is AirlineA2LocalNonpublicationSourceV01
        else source.public_safe_report_sha256
    )
    expected_count = (
        source.safe_report_byte_count
        if type(source) is AirlineA2LocalNonpublicationSourceV01
        else source.public_safe_report_byte_count
    )
    if hashlib.sha256(safe_report_bytes).hexdigest() != expected_hash or len(
        safe_report_bytes
    ) != expected_count:
        raise ValueError("airline_a2_safe_report_invalid")
    adapter_result = build_airline_a2_adapter_result_v01(
        source=source,
        package_invocation=package_invocation,
        safe_execution=safe_execution,
        ledger_source_bundle=ledger_source_bundle,
        crypto_collection_result=crypto_collection_result,
        replay_input=replay_input,
        replay_report=replay_report,
        kernel_adapter_result=kernel_adapter_result,
    )
    source_ids = tuple(
        item.source_record_id for item in adapter_result.domain_projection.source_records
    )
    if len(source_ids) != 6:
        raise ValueError("airline_a2_source_record_geometry_invalid")
    lineage = build_airline_a2_member_02_lineage_v01(
        source=source,
        package_invocation=package_invocation,
        source_record_ids=(source_ids[0], source_ids[4], source_ids[5]),
    )
    typed_context = build_airline_a2_typed_context_v01(
        source=source,
        package_invocation=package_invocation,
        safe_execution=safe_execution,
        ledger_source_bundle=ledger_source_bundle,
        ledger_item=ledger_item,
        crypto_collection_result=crypto_collection_result,
        replay_input=replay_input,
        replay_report=replay_report,
        kernel_adapter_result=kernel_adapter_result,
        ordered_source_files=ordered_source_files,
    )
    adapter_projection = build_airline_a2_adapter_projection_v01(
        source_variant=variant,
        source_identity_id=source_id,
        package_invocation_id=invocation_id,
        adapter_result=adapter_result,
    )
    contents = (
        safe_report_bytes,
        canonical_json_line_v01(lineage),
        canonical_json_line_v01(typed_context),
        canonical_json_line_v01(adapter_projection),
    )
    if variant == SOURCE_LOCAL:
        classes = ("EXECUTED_DETERMINISTIC_RUNTIME",) * 4
    else:
        classes = (
            "EXECUTED_LIVE_RUNTIME",
            "HISTORICAL_REFERENCE",
            "EXECUTED_DETERMINISTIC_RUNTIME",
            "EXECUTED_DETERMINISTIC_RUNTIME",
        )
    selections = (
        (source_ids[0],),
        (source_ids[0], source_ids[4], source_ids[5]),
        source_ids,
        source_ids,
    )
    records = tuple(
        sealed_package.build_safe_file_record_v01(
            logical_path=path,
            media_type="application/json",
            content_bytes=content,
            evidence_class=evidence_class,
            source_record_ids=selection,
            terminal_newline_required=True,
            secret_scan_passed=True,
        )
        for path, content, evidence_class, selection in zip(
            _MEMBER_PATHS,
            contents,
            classes,
            selections,
            strict=True,
        )
    )
    manifest = sealed_package.build_sealed_package_manifest_v01(
        domain_projection=adapter_result.domain_projection,
        safe_file_records=records,
        safe_file_contents=contents,
        kernel_manifest_hash=adapter_result.kernel_manifest_hash,
    )
    return AirlineA2PackageMaterialV01(
        source_variant=variant,
        source_identity_id=source_id,
        package_invocation_id=invocation_id,
        member_contents=contents,
        safe_file_records=records,
        adapter_result=adapter_result,
        domain_projection=adapter_result.domain_projection,
        manifest=manifest,
        typed_context_id=typed_context["typed_context_id"],
        adapter_projection_id=adapter_projection["adapter_projection_id"],
        adapter_result_id=adapter_result.adapter_result_id,
        domain_projection_id=adapter_result.domain_projection.projection_id,
    )


@dataclass(frozen=True, slots=True)
class AirlineA2SafePackageIndexV01:
    adapter_result_id: str
    domain_projection_id: str
    index_id: str
    index_version: str
    logical_package_ref: str
    manifest_byte_count: int
    manifest_id: str
    manifest_sha256: str
    member_03_typed_context_id: str
    member_04_adapter_projection_id: str
    package_content_hash: str
    package_id: str
    package_invocation_identity: AirlineA2OfficialPackageInvocationV01
    package_root: str
    package_status: str
    safe_file_records: tuple[sealed_package.SafeFileRecordV01, ...]
    source_identity: AirlineA2OfficialAcceptedSourceV01
    source_variant: str
    validation_errors: tuple[str, ...]


def build_airline_a2_safe_package_index_v01(
    *,
    source: AirlineA2OfficialAcceptedSourceV01,
    package_invocation: AirlineA2OfficialPackageInvocationV01,
    member_03_typed_context_id: str,
    member_04_adapter_projection_id: str,
    adapter_result: adapter.AirlineSealedEvidencePackageAdapterResultV01,
    domain_projection: profile.DomainEvidenceProjectionV01,
    safe_file_records: tuple[sealed_package.SafeFileRecordV01, ...],
    manifest: sealed_package.SealedPackageManifestV01,
    manifest_sha256: str,
    manifest_byte_count: int,
) -> AirlineA2SafePackageIndexV01:
    _source_and_invocation_identity(source, package_invocation)
    provisional = AirlineA2SafePackageIndexV01(
        adapter_result_id=adapter_result.adapter_result_id,
        domain_projection_id=domain_projection.projection_id,
        index_id="0" * 64,
        index_version=VERSION,
        logical_package_ref=package_invocation.logical_package_ref,
        manifest_byte_count=manifest_byte_count,
        manifest_id=manifest.manifest_id,
        manifest_sha256=manifest_sha256,
        member_03_typed_context_id=member_03_typed_context_id,
        member_04_adapter_projection_id=member_04_adapter_projection_id,
        package_content_hash=manifest.package_content_hash,
        package_id=package_invocation.package_id,
        package_invocation_identity=package_invocation,
        package_root=OFFICIAL_PACKAGE_ROOT,
        package_status=STATUS_SELF_CONSISTENT_UNANCHORED,
        safe_file_records=safe_file_records,
        source_identity=source,
        source_variant=SOURCE_OFFICIAL,
        validation_errors=(),
    )
    result = replace(
        provisional,
        index_id=_identity(INDEX_DOMAIN, _plain(provisional), "index_id"),
    )
    errors = validate_airline_a2_safe_package_index_v01(
        result,
        source=source,
        package_invocation=package_invocation,
        adapter_result=adapter_result,
        domain_projection=domain_projection,
        safe_file_records=safe_file_records,
        manifest=manifest,
        manifest_sha256=manifest_sha256,
        manifest_byte_count=manifest_byte_count,
    )
    if errors:
        raise ValueError(errors[0])
    return result


def validate_airline_a2_safe_package_index_v01(
    index: object,
    *,
    source: AirlineA2OfficialAcceptedSourceV01,
    package_invocation: AirlineA2OfficialPackageInvocationV01,
    adapter_result: adapter.AirlineSealedEvidencePackageAdapterResultV01,
    domain_projection: profile.DomainEvidenceProjectionV01,
    safe_file_records: tuple[sealed_package.SafeFileRecordV01, ...],
    manifest: sealed_package.SealedPackageManifestV01,
    manifest_sha256: str,
    manifest_byte_count: int,
) -> tuple[str, ...]:
    if type(index) is not AirlineA2SafePackageIndexV01:
        return ("airline_a2_package_index_invalid",)
    try:
        _source_and_invocation_identity(source, package_invocation)
        valid = (
            index.source_identity == source
            and index.package_invocation_identity == package_invocation
            and index.adapter_result_id == adapter_result.adapter_result_id
            and index.domain_projection_id == domain_projection.projection_id
            and index.safe_file_records == safe_file_records
            and len(index.safe_file_records) == 4
            and index.manifest_id == manifest.manifest_id
            and index.manifest_sha256 == manifest_sha256
            and index.manifest_byte_count == manifest_byte_count
            and index.package_content_hash == manifest.package_content_hash
            and index.package_id == package_invocation.package_id
            and index.logical_package_ref == package_invocation.logical_package_ref
            and index.package_root == OFFICIAL_PACKAGE_ROOT
            and index.package_status == STATUS_SELF_CONSISTENT_UNANCHORED
            and index.source_variant == SOURCE_OFFICIAL
            and index.index_version == VERSION
            and index.validation_errors == ()
            and _valid_sha(index.member_03_typed_context_id)
            and _valid_sha(index.member_04_adapter_projection_id)
            and _valid_sha(index.manifest_sha256)
            and _exact_int(index.manifest_byte_count)
            and index.index_id == _identity(INDEX_DOMAIN, _plain(index), "index_id")
        )
        return () if valid else ("airline_a2_package_index_invalid",)
    except (TypeError, ValueError, AttributeError):
        return ("airline_a2_package_index_invalid",)


def airline_a2_safe_package_index_to_plain_dict_v01(
    index: AirlineA2SafePackageIndexV01,
) -> dict[str, object]:
    if type(index) is not AirlineA2SafePackageIndexV01:
        raise ValueError("airline_a2_package_index_invalid")
    return _plain(index)  # type: ignore[return-value]


_A2_SELECTED_RAW_FILES = (
    "semantic_to_contract_causal_run.json",
    "semantic_to_contract_bridge.json",
    "integrated_deterministic_airline_summary.json",
    "tri_party_airline_bsep_packet.json",
    "tri_party_airline_bsep_validation.json",
    "tri_party_airline_bsep_side_projections.json",
    "airline_transaction_artifact_ledger.json",
    "airline_crypto_artifact_seal_manifest_v01.json",
    "airline_crypto_artifact_seal_verification_v01.json",
    "summary.json",
    "secret_scan.json",
    "airline_ticket_purchase_corridor_run_report_v01.json",
)


def _strict_json_bytes(content: bytes) -> dict[str, object]:
    if not content or b"\0" in content or b"\r" in content or content.startswith(b"\xef\xbb\xbf"):
        raise ValueError("airline_a2_source_invalid")

    def pairs(items: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in items:
            if key in result:
                raise ValueError("airline_a2_source_invalid")
            result[key] = value
        return result

    value = json.loads(
        content.decode("utf-8", errors="strict"),
        object_pairs_hook=pairs,
        parse_constant=lambda _value: (_ for _ in ()).throw(
            ValueError("airline_a2_source_invalid")
        ),
    )
    if type(value) is not dict:
        raise ValueError("airline_a2_source_invalid")
    return value


def _open_absolute_directory(path: Path) -> tuple[int, tuple[int, int]]:
    if not isinstance(path, Path) or not path.is_absolute() or str(path) != os.path.normpath(str(path)):
        raise ValueError("airline_a2_source_path_invalid")
    current = os.open("/", os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        for component in path.parts[1:]:
            before = os.stat(component, dir_fd=current, follow_symlinks=False)
            if not stat.S_ISDIR(before.st_mode):
                raise ValueError("airline_a2_source_path_invalid")
            next_fd = os.open(
                component,
                os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
                dir_fd=current,
            )
            opened = os.fstat(next_fd)
            if (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
                os.close(next_fd)
                raise ValueError("airline_a2_source_path_invalid")
            os.close(current)
            current = next_fd
        opened = os.fstat(current)
        return current, (opened.st_dev, opened.st_ino)
    except Exception:
        os.close(current)
        raise


def _read_leaf(directory_fd: int, leaf: str, maximum: int = 8_000_000) -> bytes:
    if not leaf or "/" in leaf or "\\" in leaf:
        raise ValueError("airline_a2_source_invalid")
    before = os.stat(leaf, dir_fd=directory_fd, follow_symlinks=False)
    if not stat.S_ISREG(before.st_mode) or before.st_size > maximum:
        raise ValueError("airline_a2_source_invalid")
    fd = os.open(leaf, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0), dir_fd=directory_fd)
    try:
        opened = os.fstat(fd)
        identity = (opened.st_dev, opened.st_ino)
        if identity != (before.st_dev, before.st_ino):
            raise ValueError("airline_a2_source_invalid")
        chunks: list[bytes] = []
        remaining = opened.st_size
        while remaining:
            chunk = os.read(fd, min(65536, remaining))
            if not chunk:
                raise ValueError("airline_a2_source_invalid")
            chunks.append(chunk)
            remaining -= len(chunk)
        content = b"".join(chunks)
        after = os.stat(leaf, dir_fd=directory_fd, follow_symlinks=False)
        if identity != (after.st_dev, after.st_ino) or len(content) != opened.st_size:
            raise ValueError("airline_a2_source_invalid")
        return content
    finally:
        os.close(fd)


def _read_attempt_sources(
    attempt_directory: Path,
) -> tuple[dict[str, dict[str, object]], dict[str, bytes]]:
    root_fd, _ = _open_absolute_directory(attempt_directory)
    raw_fd = -1
    try:
        if stat.S_IMODE(os.fstat(root_fd).st_mode) != 0o700:
            raise ValueError("airline_a2_source_invalid")
        root_names = tuple(sorted(os.listdir(root_fd)))
        if root_names != (
            "attempt_identity_v01.json",
            "generation_gate_v01.json",
            "private_inventory_v01.json",
            "raw_attempt",
        ):
            raise ValueError("airline_a2_source_invalid")
        metadata_bytes = {
            name: _read_leaf(root_fd, name)
            for name in (
                "attempt_identity_v01.json",
                "private_inventory_v01.json",
                "generation_gate_v01.json",
            )
        }
        for name in metadata_bytes:
            entry = os.stat(name, dir_fd=root_fd, follow_symlinks=False)
            if stat.S_IMODE(entry.st_mode) != 0o600:
                raise ValueError("airline_a2_source_invalid")
        documents = {
            name: _strict_json_bytes(content)
            for name, content in metadata_bytes.items()
        }
        raw_before = os.stat("raw_attempt", dir_fd=root_fd, follow_symlinks=False)
        raw_fd = os.open(
            "raw_attempt",
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=root_fd,
        )
        raw_opened = os.fstat(raw_fd)
        if (
            (raw_opened.st_dev, raw_opened.st_ino)
            != (raw_before.st_dev, raw_before.st_ino)
        ):
            raise ValueError("airline_a2_source_invalid")
        inventory = documents["private_inventory_v01.json"]
        rows = inventory.get("ordered_files")
        if type(rows) is not list or len(rows) != 73:
            raise ValueError("airline_a2_inventory_invalid")
        validated_rows: list[dict[str, object]] = []
        logical_names: list[str] = []
        for row in rows:
            if type(row) is not dict or set(row) != {
                "logical_ref",
                "sha256",
                "byte_count",
            }:
                raise ValueError("airline_a2_inventory_invalid")
            logical_name = row["logical_ref"]
            if (
                type(logical_name) is not str
                or not logical_name
                or "/" in logical_name
                or "\\" in logical_name
                or not _valid_sha(row["sha256"])
                or not _exact_int(row["byte_count"])
            ):
                raise ValueError("airline_a2_inventory_invalid")
            logical_names.append(logical_name)
            validated_rows.append(dict(row))
        if (
            logical_names != sorted(logical_names)
            or len(set(logical_names)) != 73
            or tuple(sorted(os.listdir(raw_fd))) != tuple(logical_names)
            or inventory.get("inventory_version") != VERSION
            or inventory.get("validation_status") != STATUS_PASS
            or inventory.get("raw_attempt_file_count") != 73
            or inventory.get("attempt_number") != 4
            or inventory.get("raw_bodies_copied_to_public_evidence") is not False
            or inventory.get("aggregate_inventory_digest")
            != hashlib.sha256(canonical_json_bytes_v01(validated_rows)).hexdigest()
        ):
            raise ValueError("airline_a2_inventory_invalid")
        selected = frozenset(_A2_SELECTED_RAW_FILES)
        if not selected <= frozenset(logical_names):
            raise ValueError("airline_a2_inventory_invalid")
        raw_bytes: dict[str, bytes] = {}
        for row in validated_rows:
            name = str(row["logical_ref"])
            entry = os.stat(name, dir_fd=raw_fd, follow_symlinks=False)
            if (
                not stat.S_ISREG(entry.st_mode)
                or entry.st_size != row["byte_count"]
                or (
                    name == "airline_ticket_purchase_corridor_run_report_v01.json"
                    and stat.S_IMODE(entry.st_mode) != 0o600
                )
            ):
                raise ValueError("airline_a2_inventory_invalid")
            if name in selected:
                content = _read_leaf(raw_fd, name)
                if hashlib.sha256(content).hexdigest() != row["sha256"]:
                    raise ValueError("airline_a2_inventory_invalid")
                raw_bytes[name] = content
        for name, content in raw_bytes.items():
            documents[f"raw_attempt/{name}"] = _strict_json_bytes(content)
        raw_after = os.stat("raw_attempt", dir_fd=root_fd, follow_symlinks=False)
        if (
            (raw_after.st_dev, raw_after.st_ino)
            != (raw_opened.st_dev, raw_opened.st_ino)
        ):
            raise ValueError("airline_a2_inventory_invalid")
        return documents, raw_bytes
    finally:
        if raw_fd >= 0:
            os.close(raw_fd)
        os.close(root_fd)


def _source_snapshot_by_type(ledger_plain: Mapping[str, object]) -> dict[str, dict[str, object]]:
    entries = ledger_plain.get("entries")
    if type(entries) is not list:
        raise ValueError("airline_a2_source_invalid")
    result: dict[str, dict[str, object]] = {}
    for entry in entries:
        if type(entry) is not dict or type(entry.get("artifact_type")) is not str:
            raise ValueError("airline_a2_source_invalid")
        canonical = entry.get("canonical_hash_input")
        snapshot = canonical.get("source_snapshot") if type(canonical) is dict else None
        if type(snapshot) is not dict:
            raise ValueError("airline_a2_source_invalid")
        result[str(entry["artifact_type"])] = snapshot
    return result


def _hydrate_six_inputs(
    *,
    safe_report_plain: dict[str, object],
    documents: dict[str, dict[str, object]],
    raw_bytes: dict[str, bytes],
) -> tuple[object, object, object, object, object, object]:
    if type(safe_report_plain.get("validation_errors")) is not list:
        raise ValueError("airline_a2_safe_execution_invalid")
    safe_report_plain = dict(safe_report_plain)
    safe_report_plain["validation_errors"] = tuple(
        safe_report_plain["validation_errors"]
    )
    safe_execution = adapter.build_airline_safe_execution_projection_v01(safe_report_plain)
    if adapter.validate_airline_safe_execution_projection_v01(safe_execution):
        raise ValueError("airline_a2_safe_execution_invalid")
    causal_report = _hydrate_dataclass(
        causal_runtime.AirlineSemanticCausalRunReportV01,
        documents["raw_attempt/semantic_to_contract_causal_run.json"],
    )
    corridor_report = _hydrate_dataclass(
        corridor_runtime.AirlineTicketPurchaseCorridorRunReportV01,
        documents["raw_attempt/airline_ticket_purchase_corridor_run_report_v01.json"],
    )
    corridor_accepted, corridor_errors = corridor_runtime.validate_airline_ticket_purchase_corridor_run_v01(corridor_report)
    if not corridor_accepted or corridor_errors:
        raise ValueError("airline_a2_corridor_invalid")
    ledger_plain = documents["raw_attempt/airline_transaction_artifact_ledger.json"]
    ledger_item = _hydrate_dataclass(ledger.AirlineTransactionArtifactLedgerV01, ledger_plain)
    snapshots = _source_snapshot_by_type(ledger_plain)
    bsep_types = (
        ledger.ARTIFACT_CLIENT_BSEP_PROJECTION,
        ledger.ARTIFACT_AIRLINE_BSEP_PROJECTION,
        ledger.ARTIFACT_BANK_BSEP_PROJECTION,
        ledger.ARTIFACT_CROSS_ROOT_BSEP_PROJECTION,
    )
    bsep_sources = tuple(
        ledger_collector.AirlineTransactionArtifactLedgerBSEPProjectionSourceV01(
            **snapshot,
            raw_secrets_included=False,
            raw_provider_text_included=False,
        )
        for snapshot in (snapshots[name] for name in bsep_types)
    )
    purchase_snapshot = snapshots[ledger.ARTIFACT_CLIENT_PURCHASE_INTENT]
    artifact_types: tuple[tuple[str, type[object]], ...] = (
        (ledger.ARTIFACT_AIRLINE_OFFER_PACKET, corridor_contracts.AirlineOfferPacketV01),
        (ledger.ARTIFACT_AIRLINE_HOLD_PACKET, corridor_contracts.AirlineHoldCommitPacketV01),
        (ledger.ARTIFACT_AIRLINE_OFFER_HOLD_RECEIPT, corridor_contracts.AirlineOfferHoldReceiptV01),
        (ledger.ARTIFACT_BANK_PAYMENT_AUTHORIZATION, corridor_contracts.BankPaymentAuthorizationRefV01),
        (ledger.ARTIFACT_AIRLINE_TICKET_ISSUE_INTENT, corridor_contracts.AirlineTicketIssueIntentV01),
        (ledger.ARTIFACT_MOCK_TICKET_RECEIPT, corridor_contracts.MockTicketReceiptV01),
        (ledger.ARTIFACT_MOCK_PURCHASE_RECEIPT, corridor_contracts.MockPurchaseReceiptV01),
    )
    hydrated_artifacts = {
        name: _hydrate_dataclass(contract_type, snapshots[name])
        for name, contract_type in artifact_types
    }
    root_types = (
        ledger.ARTIFACT_CLIENT_ROOT_FINAL,
        ledger.ARTIFACT_AIRLINE_ROOT_FINAL,
        ledger.ARTIFACT_BANK_ROOT_FINAL,
    )
    roots = tuple(
        _hydrate_dataclass(
            ledger_collector.AirlineTransactionArtifactLedgerRootFinalSourceV01,
            snapshots[name],
        )
        for name in root_types
    )
    expected_refs = ledger.AirlineTransactionArtifactLedgerExpectedSourceRefsV01(
        source_run_ref=ledger_item.source_run_ref,
        source_causal_report_ref=ledger_item.source_causal_report_ref,
        source_corridor_report_ref=ledger_item.source_corridor_report_ref,
    )
    source_bundle = ledger_collector.AirlineTransactionArtifactLedgerSourceBundleV01(
        source_bundle_id=ledger_item.source_run_ref.removeprefix("source_run:"),
        transaction_id=ledger_item.transaction_id,
        expected_source_refs=expected_refs,
        client_bsep_projection=bsep_sources[0],
        airline_bsep_projection=bsep_sources[1],
        bank_bsep_projection=bsep_sources[2],
        cross_root_bsep_projection=bsep_sources[3],
        causal_report=causal_report,
        offer_packet=hydrated_artifacts[ledger.ARTIFACT_AIRLINE_OFFER_PACKET],
        hold_packet=hydrated_artifacts[ledger.ARTIFACT_AIRLINE_HOLD_PACKET],
        hold_receipt=hydrated_artifacts[ledger.ARTIFACT_AIRLINE_OFFER_HOLD_RECEIPT],
        purchase_approval_evidence=_hydrate_dataclass(
            corridor_contracts.AirlinePurchaseApprovalEvidenceRefV01,
            purchase_snapshot["purchase_approval_evidence"],
        ),
        purchase_intent=_hydrate_dataclass(
            corridor_contracts.ClientPurchaseIntentV01,
            purchase_snapshot["purchase_intent"],
        ),
        payment_authorization_ref=hydrated_artifacts[ledger.ARTIFACT_BANK_PAYMENT_AUTHORIZATION],
        ticket_issue_intent=hydrated_artifacts[ledger.ARTIFACT_AIRLINE_TICKET_ISSUE_INTENT],
        mock_ticket_receipt=hydrated_artifacts[ledger.ARTIFACT_MOCK_TICKET_RECEIPT],
        mock_purchase_receipt=hydrated_artifacts[ledger.ARTIFACT_MOCK_PURCHASE_RECEIPT],
        corridor_report=corridor_report,
        client_root_final=roots[0],
        airline_root_final=roots[1],
        bank_root_final=roots[2],
        source_validation_refs=(expected_refs.source_run_ref, expected_refs.source_causal_report_ref, expected_refs.source_corridor_report_ref),
        auxiliary_observation_refs=ledger_collector.EXPECTED_AUXILIARY_OBSERVATION_REFS,
    )
    source_validation = ledger_collector.validate_airline_transaction_artifact_ledger_source_bundle_v01(source_bundle)
    if source_validation.validation_status != STATUS_PASS:
        raise ValueError("airline_a2_ledger_source_invalid")
    expected_identity = ledger_collector.build_airline_transaction_artifact_ledger_expected_identity_from_source_v01(source_bundle=source_bundle)
    if ledger.validate_airline_transaction_artifact_ledger_v01(ledger_item, expected_identity=expected_identity).validation_status != STATUS_PASS:
        raise ValueError("airline_a2_ledger_invalid")
    accepted_audit = crypto_collector.AirlineCryptoArtifactSealAcceptedLedgerAuditV01(
        audit_id=crypto_collector.EXPECTED_LEDGER_AUDIT_ID,
        audit_version=crypto_collector.EXPECTED_LEDGER_AUDIT_VERSION,
        final_status=STATUS_PASS,
        required_source_files=crypto_collector.REQUIRED_SOURCE_FILE_REFS,
        files_read_count=9,
        ledger_id=ledger_item.ledger_id,
        transaction_id=ledger_item.transaction_id,
        selected_offer_id=causal_report.semantic_recommendation_id,
        source_run_ref=ledger_item.source_run_ref,
        source_causal_report_ref=ledger_item.source_causal_report_ref,
        source_corridor_report_ref=ledger_item.source_corridor_report_ref,
        actual_entry_count=19,
        actual_dependency_edge_count=29,
        actual_root_final_count=3,
        client_root_final_count=1,
        airline_root_final_count=1,
        bank_root_final_count=1,
        **{name: True for name in crypto_collector.ACCEPTED_AUDIT_BOOLEAN_FIELDS},
        stored_validation_status=STATUS_PASS,
        stored_validation_errors=(),
        **{name: 0 for name in crypto_collector.ACCEPTED_AUDIT_ZERO_COUNTER_FIELDS},
        validation_errors=(),
    )
    source_rows = tuple((name, raw_bytes[name]) for name in crypto_collector.REQUIRED_SOURCE_FILE_REFS)
    manifest_plain = documents["raw_attempt/airline_crypto_artifact_seal_manifest_v01.json"]
    envelope = _hydrate_dataclass(crypto.AirlineCryptoArtifactSealEnvelopeV01, manifest_plain)
    stored_verification = _hydrate_dataclass(
        crypto.AirlineCryptoArtifactSealVerificationReportV01,
        documents["raw_attempt/airline_crypto_artifact_seal_verification_v01.json"],
    )
    crypto_source_bundle = crypto_collector.build_airline_crypto_artifact_seal_source_bundle_v01(
        source_bundle_id=f"airline_crypto_source_bundle:{safe_execution.run_id}",
        source_package_ref=envelope.manifest_core.source_package_ref,
        accepted_audit=accepted_audit,
        ledger_item=ledger_item,
        expected_identity=expected_identity,
        ordered_source_files_before_audit=source_rows,
        ordered_source_files_after_audit=source_rows,
    )
    crypto_source_report = crypto_collector.validate_airline_crypto_artifact_seal_source_bundle_v01(crypto_source_bundle)
    if crypto_source_report.validation_status != STATUS_PASS:
        raise ValueError("airline_a2_crypto_source_invalid")
    fresh_verification = crypto.verify_airline_crypto_artifact_seal_v01(
        envelope,
        ledger_item=ledger_item,
        ordered_source_files_before=source_rows,
        ordered_source_files_after=source_rows,
        expected_source_package_ref=envelope.manifest_core.source_package_ref,
        source_audit_status=STATUS_PASS,
        secret_scan_passed=True,
        expected_manifest_core_hash=envelope.manifest_core_hash,
        expected_identity=expected_identity,
    )
    crypto_result = crypto_collector.AirlineCryptoArtifactSealCollectionResultV01(
        collection_status=STATUS_PASS,
        source_bundle_id=crypto_source_bundle.source_bundle_id,
        source_package_ref=envelope.manifest_core.source_package_ref,
        transaction_id=ledger_item.transaction_id,
        ledger_id=ledger_item.ledger_id,
        manifest_core_hash=envelope.manifest_core_hash,
        expected_manifest_core_hash=envelope.manifest_core_hash,
        source_bundle_validation_report=crypto_source_report,
        manifest_core=envelope.manifest_core,
        envelope=envelope,
        verification_report=fresh_verification,
        source_bytes_unchanged_after_audit=True,
        source_bytes_unchanged_after_collection=True,
        **{name: 1 for name in crypto_collector.COLLECTION_STAGE_COUNT_FIELDS},
        **{name: 0 for name in crypto_collector.COLLECTION_ZERO_COUNTER_FIELDS},
        collection_errors=(),
    )
    if crypto_collector.validate_airline_crypto_artifact_seal_collection_result_v01(crypto_result).validation_status != STATUS_PASS:
        raise ValueError("airline_a2_crypto_invalid")
    replay_input = replay.build_airline_sealed_trace_replay_input_v01(
        source_package_ref=envelope.manifest_core.source_package_ref,
        accepted_ledger_audit=accepted_audit,
        ledger_item=ledger_item,
        envelope=envelope,
        stored_verification_report=stored_verification,
        fresh_anchored_verification_report=fresh_verification,
        expected_manifest_core_hash=envelope.manifest_core_hash,
        ordered_source_files=source_rows,
    )
    replay_report = replay.verify_airline_sealed_trace_replay_v01(
        replay_input,
        critical_package_bytes_unchanged=True,
        post_replay_snapshot_provider_call_count=1,
    )
    kernel_result = kernel_adapter.build_airline_kernel_adapter_result_v01(
        replay_input=replay_input,
        replay_report=replay_report,
    )
    if (
        replay.validate_airline_sealed_trace_replay_input_v01(replay_input).validation_status != STATUS_PASS
        or replay.validate_airline_sealed_trace_replay_report_v01(replay_report).validation_status != STATUS_PASS
        or kernel_adapter.validate_airline_kernel_adapter_result_v01(
            replay_input=replay_input,
            replay_report=replay_report,
            result=kernel_result,
        )
    ):
        raise ValueError("airline_a2_replay_kernel_invalid")
    return safe_execution, source_bundle, crypto_result, replay_input, replay_report, kernel_result


def load_airline_a2_local_nonpublication_source_v01(
    *,
    repository_root: Path,
    attempt_directory: Path,
    safe_report_path: Path,
    expected_attempt_id: str,
    expected_execution_head: str,
    expected_attempt_identity_sha256: str,
    expected_private_inventory_sha256: str,
    expected_private_inventory_digest: str,
    expected_generation_gate_sha256: str,
    expected_corridor_archive_sha256: str,
    expected_corridor_archive_byte_count: int,
    expected_safe_report_sha256: str,
    expected_safe_report_byte_count: int,
    expected_safe_execution_id: str,
    implementation_content_sha256: str,
) -> tuple[object, object, object, object, object, object, object]:
    if (
        not isinstance(repository_root, Path)
        or not repository_root.is_absolute()
        or not attempt_directory.is_absolute()
        or not safe_report_path.is_absolute()
        or attempt_directory.parent != safe_report_path.parent
        or _inside_path(repository_root, attempt_directory)
        or _inside_path(repository_root, safe_report_path)
        or safe_report_path.name != LOCAL_SAFE_REPORT_LOGICAL_NAME
        or not _text(expected_attempt_id)
        or not _valid_head(expected_execution_head)
        or not all(
            _valid_sha(value)
            for value in (
                expected_attempt_identity_sha256,
                expected_private_inventory_sha256,
                expected_private_inventory_digest,
                expected_generation_gate_sha256,
                expected_corridor_archive_sha256,
                expected_safe_report_sha256,
                expected_safe_execution_id,
                implementation_content_sha256,
            )
        )
        or not _exact_int(expected_corridor_archive_byte_count)
        or not _exact_int(expected_safe_report_byte_count)
    ):
        raise ValueError("airline_a2_source_invalid")
    documents, raw_bytes = _read_attempt_sources(attempt_directory)
    parent_fd, _ = _open_absolute_directory(safe_report_path.parent)
    try:
        safe_bytes = _read_leaf(parent_fd, safe_report_path.name)
    finally:
        os.close(parent_fd)
    safe_plain = _strict_json_bytes(safe_bytes)
    attempt_bytes = canonical_json_line_v01(documents["attempt_identity_v01.json"])
    inventory_bytes = canonical_json_line_v01(documents["private_inventory_v01.json"])
    gate_bytes = canonical_json_line_v01(documents["generation_gate_v01.json"])
    corridor_bytes = raw_bytes["airline_ticket_purchase_corridor_run_report_v01.json"]
    if (
        hashlib.sha256(attempt_bytes).hexdigest() != expected_attempt_identity_sha256
        or hashlib.sha256(inventory_bytes).hexdigest() != expected_private_inventory_sha256
        or hashlib.sha256(gate_bytes).hexdigest() != expected_generation_gate_sha256
        or hashlib.sha256(corridor_bytes).hexdigest() != expected_corridor_archive_sha256
        or len(corridor_bytes) != expected_corridor_archive_byte_count
        or hashlib.sha256(safe_bytes).hexdigest() != expected_safe_report_sha256
        or len(safe_bytes) != expected_safe_report_byte_count
    ):
        raise ValueError("airline_a2_source_hash_mismatch")
    inventory = documents["private_inventory_v01.json"]
    rows = inventory.get("ordered_files")
    if type(rows) is not list or len(rows) != 73:
        raise ValueError("airline_a2_inventory_invalid")
    row_by_name = {row.get("logical_ref"): row for row in rows if type(row) is dict}
    for name, content in raw_bytes.items():
        row = row_by_name.get(name)
        if type(row) is not dict or row.get("sha256") != hashlib.sha256(content).hexdigest() or row.get("byte_count") != len(content):
            raise ValueError("airline_a2_inventory_invalid")
    if (
        inventory.get("aggregate_inventory_digest")
        != expected_private_inventory_digest
        or documents["attempt_identity_v01.json"].get("attempt_id")
        != expected_attempt_id
        or documents["attempt_identity_v01.json"].get("execution_head")
        != expected_execution_head
        or documents["attempt_identity_v01.json"].get("attempt_number") != 4
    ):
        raise ValueError("airline_a2_inventory_invalid")
    _validate_attempt_04_document_bindings(
        documents=documents,
        expected_attempt_id=expected_attempt_id,
        expected_execution_head=expected_execution_head,
        expected_attempt_identity_sha256=expected_attempt_identity_sha256,
        expected_private_inventory_sha256=expected_private_inventory_sha256,
        expected_private_inventory_digest=expected_private_inventory_digest,
        expected_safe_execution_id=expected_safe_execution_id,
        expected_safe_report_sha256=expected_safe_report_sha256,
        official=False,
    )
    six = _hydrate_six_inputs(safe_report_plain=safe_plain, documents=documents, raw_bytes=raw_bytes)
    safe_execution = six[0]
    if getattr(safe_execution, "safe_execution_id", None) != expected_safe_execution_id:
        raise ValueError("airline_a2_safe_execution_invalid")
    source = build_airline_a2_local_nonpublication_source_v01(
        attempt_id=expected_attempt_id,
        execution_head=expected_execution_head,
        implementation_content_sha256=implementation_content_sha256,
        attempt_identity_sha256=expected_attempt_identity_sha256,
        private_inventory_sha256=expected_private_inventory_sha256,
        private_inventory_digest=expected_private_inventory_digest,
        generation_gate_sha256=expected_generation_gate_sha256,
        corridor_archive_sha256=expected_corridor_archive_sha256,
        corridor_archive_byte_count=expected_corridor_archive_byte_count,
        safe_report_sha256=expected_safe_report_sha256,
        safe_report_byte_count=expected_safe_report_byte_count,
        safe_execution_id=expected_safe_execution_id,
        wrapper_callback_observed_count=12,
        provider_callback_started_count=12,
        provider_callback_completed_count=12,
        collector_invocation_count=1,
        deterministic_airline_collection_count=1,
        ticket_purchase_corridor_execution_count=1,
        airline_transaction_artifact_ledger_collection_count=1,
        airline_crypto_artifact_seal_collection_count=1,
        outbound_provider_sdk_call_count=0,
        outbound_network_call_count=0,
        outbound_gemini_call_count=0,
        real_world_effects_count=0,
    )
    return (source, *six)


def _repository_relative_file(
    repository_root: Path,
    path: Path,
    expected_relative: str,
) -> bytes:
    if (
        not repository_root.is_absolute()
        or not path.is_absolute()
        or path != repository_root / expected_relative
    ):
        raise ValueError("airline_a2_source_path_invalid")
    parent_fd, _ = _open_absolute_directory(path.parent)
    try:
        return _read_leaf(parent_fd, path.name)
    finally:
        os.close(parent_fd)


def _validate_attempt_04_document_bindings(
    *,
    documents: Mapping[str, Mapping[str, object]],
    expected_attempt_id: str,
    expected_execution_head: str,
    expected_attempt_identity_sha256: str,
    expected_private_inventory_sha256: str,
    expected_private_inventory_digest: str,
    expected_safe_execution_id: str,
    expected_safe_report_sha256: str,
    official: bool,
) -> None:
    identity = documents["attempt_identity_v01.json"]
    inventory = documents["private_inventory_v01.json"]
    gate = documents["generation_gate_v01.json"]
    expected_actual_calls = 12 if official else 0
    if (
        identity.get("attempt_number") != 4
        or identity.get("attempt_id") != expected_attempt_id
        or identity.get("execution_head") != expected_execution_head
        or identity.get("complete_corridor_archive_logical_ref")
        != CORRIDOR_ARCHIVE_LOGICAL_NAME
        or identity.get("new_provider_call_ceiling") != 12
        or identity.get("cumulative_airline_call_ceiling") != 30
        or identity.get("supplier_accepted_budget") != 6
        or identity.get("cumulative_programme_call_ceiling") != 36
        or identity.get("owner_reviewed_attempt_04") is not True
        or inventory.get("attempt_number") != 4
        or inventory.get("attempt_id") != expected_attempt_id
        or inventory.get("validation_status") != STATUS_PASS
        or inventory.get("aggregate_inventory_digest")
        != expected_private_inventory_digest
        or gate.get("attempt_number") != 4
        or gate.get("attempt_id") != expected_attempt_id
        or gate.get("execution_head") != expected_execution_head
        or gate.get("attempt_identity_sha256")
        != expected_attempt_identity_sha256
        or gate.get("private_inventory_document_sha256")
        != expected_private_inventory_sha256
        or gate.get("private_inventory_digest")
        != expected_private_inventory_digest
        or gate.get("final_source_status") != STATUS_PASS
        or gate.get("failed_stage") != ""
        or gate.get("reason_code") != ""
        or gate.get("safe_execution_id") != expected_safe_execution_id
        or gate.get("safe_report_sha256") != expected_safe_report_sha256
        or gate.get("public_safe_report_state") != "PRESENT"
        or gate.get("wrapper_callback_observed_count") != 12
        or gate.get("provider_callback_started_count") != 12
        or gate.get("provider_callback_completed_count") != 12
        or gate.get("actual_provider_call_count") != expected_actual_calls
        or gate.get("actual_network_call_count") != expected_actual_calls
        or gate.get("actual_gemini_call_count") != expected_actual_calls
        or gate.get("actual_real_world_effects_count") != 0
        or gate.get("retry_count") != 0
        or gate.get("package_created_count") != 0
        or gate.get("anchor_created_count") != 0
        or gate.get("replay_created_count") != 0
        or gate.get("official_evidence_eligible") is not official
        or gate.get("complete_corridor_archive_logical_ref")
        != CORRIDOR_ARCHIVE_LOGICAL_NAME
    ):
        raise ValueError("airline_a2_attempt_binding_invalid")


def _git_committed_file_bytes(
    repository_root: Path,
    head: str,
    relative_path: str,
) -> bytes:
    if not _valid_head(head):
        raise ValueError("airline_a2_git_identity_invalid")
    completed = subprocess.run(
        ("git", "-C", str(repository_root), "show", f"{head}:{relative_path}"),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if completed.returncode != 0:
        raise ValueError("airline_a2_git_identity_invalid")
    return bytes(completed.stdout)


def load_airline_a2_official_accepted_source_v01(
    *,
    repository_root: Path,
    accepted_attempt_directory: Path,
    safe_report_path: Path,
    generation_audit_path: Path,
    expected_attempt_id: str,
    expected_execution_head: str,
    expected_publication_base_head: str,
    expected_attempt_identity_sha256: str,
    expected_private_inventory_sha256: str,
    expected_private_inventory_digest: str,
    expected_generation_gate_sha256: str,
    expected_corridor_archive_sha256: str,
    expected_corridor_archive_byte_count: int,
    expected_safe_report_sha256: str,
    expected_safe_report_byte_count: int,
    expected_safe_execution_id: str,
    expected_generation_audit_sha256: str,
) -> tuple[object, object, object, object, object, object, object]:
    report_relative = (
        "docs/evidence/two_domain_all_real_sealed_evidence_program_v01/airline/"
        "airline_safe_execution_report_attempt_04_v01.json"
    )
    audit_relative = (
        "docs/audit_reports/"
        "auditor_two_domain_airline_all_real_generation_attempt_04_v01.log"
    )
    if (
        not isinstance(repository_root, Path)
        or not repository_root.is_absolute()
        or not accepted_attempt_directory.is_absolute()
        or _inside_path(repository_root, accepted_attempt_directory)
        or not _valid_head(expected_execution_head)
        or not _valid_head(expected_publication_base_head)
        or not _text(expected_attempt_id)
        or not all(
            _valid_sha(value)
            for value in (
                expected_attempt_identity_sha256,
                expected_private_inventory_sha256,
                expected_private_inventory_digest,
                expected_generation_gate_sha256,
                expected_corridor_archive_sha256,
                expected_safe_report_sha256,
                expected_safe_execution_id,
                expected_generation_audit_sha256,
            )
        )
        or not _exact_int(expected_corridor_archive_byte_count)
        or not _exact_int(expected_safe_report_byte_count)
    ):
        raise ValueError("airline_a2_official_source_invalid")
    safe_bytes = _repository_relative_file(
        repository_root, safe_report_path, report_relative
    )
    audit_bytes = _repository_relative_file(
        repository_root, generation_audit_path, audit_relative
    )
    if (
        _git_committed_file_bytes(
            repository_root, expected_publication_base_head, report_relative
        )
        != safe_bytes
        or _git_committed_file_bytes(
            repository_root, expected_publication_base_head, audit_relative
        )
        != audit_bytes
        or hashlib.sha256(safe_bytes).hexdigest() != expected_safe_report_sha256
        or len(safe_bytes) != expected_safe_report_byte_count
        or hashlib.sha256(audit_bytes).hexdigest()
        != expected_generation_audit_sha256
    ):
        raise ValueError("airline_a2_official_source_invalid")
    audit_text = audit_bytes.decode("utf-8", errors="strict")
    if (
        "CLOSED_PASS" not in audit_text
        or "ACCEPT_FOR_A2_AIRLINE_SEAL_WITH_BOUNDED_NON_EFFECT_SCOPE"
        not in audit_text
        or "\x00" in audit_text
        or "\r" in audit_text
    ):
        raise ValueError("airline_a2_official_source_invalid")
    documents, raw_bytes = _read_attempt_sources(accepted_attempt_directory)
    attempt_bytes = canonical_json_line_v01(documents["attempt_identity_v01.json"])
    inventory_bytes = canonical_json_line_v01(documents["private_inventory_v01.json"])
    gate_bytes = canonical_json_line_v01(documents["generation_gate_v01.json"])
    corridor_bytes = raw_bytes["airline_ticket_purchase_corridor_run_report_v01.json"]
    inventory = documents["private_inventory_v01.json"]
    rows = inventory.get("ordered_files")
    if (
        hashlib.sha256(attempt_bytes).hexdigest()
        != expected_attempt_identity_sha256
        or hashlib.sha256(inventory_bytes).hexdigest()
        != expected_private_inventory_sha256
        or hashlib.sha256(gate_bytes).hexdigest()
        != expected_generation_gate_sha256
        or hashlib.sha256(corridor_bytes).hexdigest()
        != expected_corridor_archive_sha256
        or len(corridor_bytes) != expected_corridor_archive_byte_count
        or type(rows) is not list
        or len(rows) != 73
        or inventory.get("aggregate_inventory_digest")
        != expected_private_inventory_digest
        or documents["attempt_identity_v01.json"].get("attempt_number") != 4
        or documents["attempt_identity_v01.json"].get("attempt_id")
        != expected_attempt_id
        or documents["attempt_identity_v01.json"].get("execution_head")
        != expected_execution_head
    ):
        raise ValueError("airline_a2_official_source_invalid")
    row_by_name = {row.get("logical_ref"): row for row in rows if type(row) is dict}
    for name, content in raw_bytes.items():
        row = row_by_name.get(name)
        if (
            type(row) is not dict
            or row.get("sha256") != hashlib.sha256(content).hexdigest()
            or row.get("byte_count") != len(content)
        ):
            raise ValueError("airline_a2_official_source_invalid")
    _validate_attempt_04_document_bindings(
        documents=documents,
        expected_attempt_id=expected_attempt_id,
        expected_execution_head=expected_execution_head,
        expected_attempt_identity_sha256=expected_attempt_identity_sha256,
        expected_private_inventory_sha256=expected_private_inventory_sha256,
        expected_private_inventory_digest=expected_private_inventory_digest,
        expected_safe_execution_id=expected_safe_execution_id,
        expected_safe_report_sha256=expected_safe_report_sha256,
        official=True,
    )
    safe_plain = _strict_json_bytes(safe_bytes)
    six = _hydrate_six_inputs(
        safe_report_plain=safe_plain,
        documents=documents,
        raw_bytes=raw_bytes,
    )
    if getattr(six[0], "safe_execution_id", None) != expected_safe_execution_id:
        raise ValueError("airline_a2_official_source_invalid")
    source = build_airline_a2_official_accepted_source_v01(
        attempt_id=expected_attempt_id,
        execution_head=expected_execution_head,
        attempt_identity_sha256=expected_attempt_identity_sha256,
        private_inventory_sha256=expected_private_inventory_sha256,
        private_inventory_digest=expected_private_inventory_digest,
        generation_gate_sha256=expected_generation_gate_sha256,
        corridor_archive_sha256=expected_corridor_archive_sha256,
        corridor_archive_byte_count=expected_corridor_archive_byte_count,
        public_safe_report_path=report_relative,
        public_safe_report_sha256=expected_safe_report_sha256,
        public_safe_report_byte_count=expected_safe_report_byte_count,
        safe_execution_id=expected_safe_execution_id,
        generation_audit_path=audit_relative,
        generation_audit_sha256=expected_generation_audit_sha256,
        wrapper_callback_observed_count=12,
        provider_callback_started_count=12,
        provider_callback_completed_count=12,
        provider_call_count=12,
        network_call_count=12,
        gemini_call_count=12,
        collector_invocation_count=1,
        deterministic_airline_collection_count=1,
        ticket_purchase_corridor_execution_count=1,
        airline_transaction_artifact_ledger_collection_count=1,
        airline_crypto_artifact_seal_collection_count=1,
        duplicate_actor_call_count=0,
        retry_count=0,
        fallback_call_count=0,
        package_created_count=0,
        anchor_created_count=0,
        replay_created_count=0,
        real_world_effects_count=0,
    )
    return (source, *six)


def load_airline_a2_official_package_v01(
    *,
    package_root: Path,
    package_index_path: Path,
) -> tuple[
    AirlineA2SafePackageIndexV01,
    adapter.AirlineSealedEvidencePackageAdapterResultV01,
    profile.DomainEvidenceProjectionV01,
    sealed_package.SealedPackageManifestV01,
    tuple[bytes, ...],
]:
    index_parent, _ = _open_absolute_directory(package_index_path.parent)
    try:
        index_bytes = _read_leaf(index_parent, package_index_path.name)
        index_plain = _strict_json_bytes(index_bytes)
        if index_bytes != canonical_json_line_v01(index_plain):
            raise ValueError("airline_a2_official_package_invalid")
    finally:
        os.close(index_parent)
    index = _hydrate_dataclass(AirlineA2SafePackageIndexV01, index_plain)
    source = index.source_identity
    invocation = index.package_invocation_identity
    records = index.safe_file_records
    root_fd, _ = _open_absolute_directory(package_root)
    evidence_fd = -1
    try:
        if tuple(sorted(os.listdir(root_fd))) != (
            "evidence",
            sealed_package.MANIFEST_FILENAME,
        ):
            raise ValueError("airline_a2_official_package_invalid")
        manifest_bytes = _read_leaf(root_fd, sealed_package.MANIFEST_FILENAME)
        manifest_plain = _strict_json_bytes(manifest_bytes)
        if manifest_bytes != canonical_json_line_v01(manifest_plain):
            raise ValueError("airline_a2_official_package_invalid")
        manifest = _hydrate_dataclass(
            sealed_package.SealedPackageManifestV01, manifest_plain
        )
        evidence_fd, _ = _open_absolute_directory(package_root / "evidence")
        expected_evidence_names = tuple(
            record.logical_path.removeprefix("evidence/")
            for record in manifest.safe_file_records
        )
        if tuple(sorted(os.listdir(evidence_fd))) != tuple(
            sorted(expected_evidence_names)
        ):
            raise ValueError("airline_a2_official_package_invalid")
        contents = tuple(
            _read_leaf(evidence_fd, record.logical_path.rsplit("/", 1)[1])
            for record in manifest.safe_file_records
        )
    finally:
        if evidence_fd >= 0:
            os.close(evidence_fd)
        os.close(root_fd)
    member_04 = _strict_json_bytes(contents[3])
    adapter_result = _hydrate_dataclass(
        adapter.AirlineSealedEvidencePackageAdapterResultV01,
        member_04["adapter_result"],
    )
    domain_projection = adapter_result.domain_projection
    if (
        tuple(record.logical_path for record in manifest.safe_file_records)
        != _MEMBER_PATHS
        or tuple(record.logical_path for record in records) != _MEMBER_PATHS
        or manifest.safe_file_records != records
        or any(
            content != canonical_json_line_v01(_strict_json_bytes(content))
            for content in contents
        )
        or
        sealed_package.validate_sealed_package_manifest_v01(
            manifest,
            domain_projection=domain_projection,
            safe_file_contents=contents,
        )
        or validate_airline_a2_safe_package_index_v01(
            index,
            source=source,
            package_invocation=invocation,
            adapter_result=adapter_result,
            domain_projection=domain_projection,
            safe_file_records=records,
            manifest=manifest,
            manifest_sha256=hashlib.sha256(manifest_bytes).hexdigest(),
            manifest_byte_count=len(manifest_bytes),
        )
    ):
        raise ValueError("airline_a2_official_package_invalid")
    return index, adapter_result, domain_projection, manifest, contents
