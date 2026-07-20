from __future__ import annotations

import ast
from dataclasses import FrozenInstanceError, fields, is_dataclass, replace
import hashlib
import inspect
import json
from pathlib import Path

import pytest

import hedgehog.evidence as evidence
from hedgehog.evidence import sealed_evidence_profile_v01 as profile
from hedgehog.evidence import sealed_package_v01 as sealed_package
from hedgehog.evidence import external_anchor_v01 as external_anchor
from hedgehog.evidence import sealed_replay_evidence_v01 as sealed_replay
from hedgehog.kernel.abi_v01 import (
    CausalConsumptionRefV01,
    build_causal_consumption_ref_v01,
)
from hedgehog.kernel.integrity_replay_v01 import (
    CanonicalArtifactRefV01,
    canonical_json_bytes_v01,
)


PROGRAMME_ID = "two_domain_all_real_sealed_evidence_program_v01"
PROGRAMME_VERSION = "v0.1"
DOMAIN_ID = "airline"
EXECUTION_HEAD = "b1096c2"
SOURCE_TASK_ID = "source_task:airline:attempt_01"
RUN_ID = "run:airline:attempt_01"
REPORT_ID = "report:airline:attempt_01"

DATACLASS_NAMES = (
    "ProgrammeEvidenceIdentityV01",
    "DomainExecutionIdentityV01",
    "LiveAttemptIdentityV01",
    "SafeSourceRecordV01",
    "EvidenceArtifactRecordV01",
    "DomainEvidenceProjectionV01",
)
BUILDER_NAMES = (
    "build_programme_evidence_identity_v01",
    "build_domain_execution_identity_v01",
    "build_live_attempt_identity_v01",
    "build_safe_source_record_v01",
    "build_evidence_artifact_record_v01",
    "build_domain_evidence_projection_v01",
)
VALIDATOR_NAMES = (
    "validate_programme_evidence_identity_v01",
    "validate_domain_execution_identity_v01",
    "validate_live_attempt_identity_v01",
    "validate_safe_source_record_v01",
    "validate_evidence_artifact_record_v01",
    "validate_domain_evidence_projection_v01",
)
PROJECTION_NAMES = (
    "programme_evidence_identity_to_plain_dict_v01",
    "domain_execution_identity_to_plain_dict_v01",
    "live_attempt_identity_to_plain_dict_v01",
    "safe_source_record_to_plain_dict_v01",
    "evidence_artifact_record_to_plain_dict_v01",
    "domain_evidence_projection_to_plain_dict_v01",
)
PUBLIC_FUNCTION_NAMES = BUILDER_NAMES + VALIDATOR_NAMES + PROJECTION_NAMES
MODULE_FUNCTION_NAMES = tuple(
    name
    for group in zip(BUILDER_NAMES, VALIDATOR_NAMES, PROJECTION_NAMES, strict=True)
    for name in group
)
PACKAGE_DATACLASS_NAMES = (
    "SafeFileRecordV01",
    "SealedPackageManifestV01",
)
PACKAGE_BUILDER_NAMES = (
    "build_safe_file_record_v01",
    "build_sealed_package_manifest_v01",
)
PACKAGE_VALIDATOR_NAMES = (
    "validate_safe_file_record_v01",
    "validate_sealed_package_manifest_v01",
)
PACKAGE_PROJECTION_NAMES = (
    "safe_file_record_to_plain_dict_v01",
    "sealed_package_manifest_to_plain_dict_v01",
)
SEALED_PACKAGE_PUBLIC_FUNCTION_NAMES = (
    PACKAGE_BUILDER_NAMES + PACKAGE_VALIDATOR_NAMES + PACKAGE_PROJECTION_NAMES
)
ANCHOR_DATACLASS_NAMES = (
    "ExternalAnchorPublicationV01",
    "AnchoredPackageVerificationV01",
)
ANCHOR_BUILDER_NAMES = (
    "build_external_anchor_publication_v01",
    "build_anchored_package_verification_v01",
)
ANCHOR_VALIDATOR_NAMES = (
    "validate_external_anchor_publication_v01",
    "validate_anchored_package_verification_v01",
)
ANCHOR_PROJECTION_NAMES = (
    "external_anchor_publication_to_plain_dict_v01",
    "anchored_package_verification_to_plain_dict_v01",
)
ANCHOR_PUBLIC_FUNCTION_NAMES = (
    ANCHOR_BUILDER_NAMES + ANCHOR_VALIDATOR_NAMES + ANCHOR_PROJECTION_NAMES
)
REPLAY_DATACLASS_NAMES = ("SealedReplayEvidenceV01",)
REPLAY_BUILDER_NAMES = ("build_sealed_replay_evidence_v01",)
REPLAY_VALIDATOR_NAMES = ("validate_sealed_replay_evidence_v01",)
REPLAY_PROJECTION_NAMES = ("sealed_replay_evidence_to_plain_dict_v01",)
REPLAY_PUBLIC_FUNCTION_NAMES = (
    REPLAY_BUILDER_NAMES + REPLAY_VALIDATOR_NAMES + REPLAY_PROJECTION_NAMES
)
PACKAGE_ALL = (
    DATACLASS_NAMES
    + PACKAGE_DATACLASS_NAMES
    + ANCHOR_DATACLASS_NAMES
    + REPLAY_DATACLASS_NAMES
    + BUILDER_NAMES
    + PACKAGE_BUILDER_NAMES
    + ANCHOR_BUILDER_NAMES
    + REPLAY_BUILDER_NAMES
    + VALIDATOR_NAMES
    + PACKAGE_VALIDATOR_NAMES
    + ANCHOR_VALIDATOR_NAMES
    + REPLAY_VALIDATOR_NAMES
    + PROJECTION_NAMES
    + PACKAGE_PROJECTION_NAMES
    + ANCHOR_PROJECTION_NAMES
    + REPLAY_PROJECTION_NAMES
)

PACKAGE_FIELD_NAMES = {
    "SafeFileRecordV01": (
        "file_record_id",
        "logical_path",
        "media_type",
        "byte_count",
        "content_sha256",
        "evidence_class",
        "source_record_ids",
        "terminal_newline_required",
        "secret_scan_passed",
    ),
    "SealedPackageManifestV01": (
        "manifest_id",
        "manifest_version",
        "domain_projection_id",
        "programme_identity_id",
        "domain_execution_identity_id",
        "attempt_identity_id",
        "domain_id",
        "package_id",
        "logical_package_ref",
        "safe_file_records",
        "artifact_record_ids",
        "kernel_manifest_hash",
        "file_count",
        "artifact_count",
        "package_content_hash",
        "packaging_provider_call_count",
        "packaging_network_call_count",
        "packaging_gemini_call_count",
        "created_authority_count",
        "created_permission_count",
        "real_world_effects_count",
        "package_status",
    ),
}

ANCHOR_FIELD_NAMES = {
    "ExternalAnchorPublicationV01": (
        "anchor_publication_id",
        "anchor_version",
        "manifest_id",
        "domain_projection_id",
        "programme_identity_id",
        "domain_execution_identity_id",
        "attempt_identity_id",
        "domain_id",
        "package_id",
        "logical_package_ref",
        "package_content_hash",
        "kernel_manifest_hash",
        "publication_base_head",
        "external_anchor_supplied_at_publication",
        "external_anchor_verified_at_publication",
        "anchored_pass_claimed",
        "publication_provider_call_count",
        "publication_network_call_count",
        "publication_gemini_call_count",
        "created_authority_count",
        "created_permission_count",
        "real_world_effects_count",
        "anchor_status",
    ),
    "AnchoredPackageVerificationV01": (
        "anchored_verification_id",
        "verification_version",
        "anchor_publication_id",
        "manifest_id",
        "domain_projection_id",
        "programme_identity_id",
        "domain_execution_identity_id",
        "attempt_identity_id",
        "domain_id",
        "package_id",
        "logical_package_ref",
        "package_content_hash",
        "kernel_manifest_hash",
        "publication_base_head",
        "supplied_anchor_publication_id",
        "external_anchor_supplied",
        "external_anchor_verified",
        "manifest_binding_verified",
        "package_binding_verified",
        "signature_verified",
        "signer_identity_verified",
        "root_attestation_verified",
        "verification_provider_call_count",
        "verification_network_call_count",
        "verification_gemini_call_count",
        "created_authority_count",
        "created_permission_count",
        "real_world_effects_count",
        "verification_status",
    ),
}

REPLAY_FIELD_NAMES = (
    "replay_id",
    "replay_version",
    "source_manifest_id",
    "reconstructed_manifest_id",
    "anchor_publication_id",
    "anchored_verification_id",
    "source_domain_projection_id",
    "reconstructed_domain_projection_id",
    "domain_id",
    "package_id",
    "logical_package_ref",
    "source_package_content_hash",
    "reconstructed_package_content_hash",
    "source_file_count",
    "reconstructed_file_count",
    "source_artifact_count",
    "reconstructed_artifact_count",
    "source_file_order_hash",
    "reconstructed_file_order_hash",
    "source_artifact_order_hash",
    "reconstructed_artifact_order_hash",
    "integrity_verified",
    "continuity_verified",
    "anchor_verified",
    "semantic_rerun_count",
    "root_decision_rerun_count",
    "corridor_rerun_count",
    "provider_call_count",
    "network_call_count",
    "gemini_call_count",
    "created_authority_count",
    "created_permission_count",
    "action_created_count",
    "receipt_created_count",
    "final_output_created_count",
    "real_world_effects_count",
    "evidence_refs",
    "replay_status",
)

FIELD_NAMES = {
    "ProgrammeEvidenceIdentityV01": (
        "programme_identity_id",
        "programme_id",
        "programme_version",
        "profile_version",
    ),
    "DomainExecutionIdentityV01": (
        "domain_execution_identity_id",
        "programme_identity_id",
        "domain_id",
        "execution_head",
        "source_task_id",
        "run_id",
        "report_id",
    ),
    "LiveAttemptIdentityV01": (
        "attempt_identity_id",
        "programme_id",
        "domain_id",
        "execution_head",
        "attempt_number",
        "run_id",
        "report_id",
        "source_task_id",
        "package_id",
        "logical_package_ref",
        "output_directory_ref",
        "provider_mode",
        "model_id",
        "expected_actor_count",
        "provider_call_budget",
    ),
    "SafeSourceRecordV01": (
        "source_record_id",
        "source_id",
        "source_type",
        "evidence_class",
        "canonical_sha256",
        "byte_count",
        "media_type",
        "trace_refs",
        "contains_raw_prompt",
        "contains_raw_provider_response",
        "secret_scan_passed",
        "observed_provider_call_count",
        "observed_network_call_count",
        "observed_gemini_call_count",
        "real_world_effects_count",
    ),
    "EvidenceArtifactRecordV01": (
        "artifact_record_id",
        "artifact_id",
        "artifact_type",
        "evidence_class",
        "source_record_ids",
        "canonical_sha256",
        "authority_class",
        "owner_root_id",
        "trace_refs",
        "created_authority_count",
        "created_permission_count",
        "real_world_effects_count",
    ),
    "DomainEvidenceProjectionV01": (
        "projection_id",
        "programme_identity",
        "domain_execution_identity",
        "attempt_identity",
        "source_records",
        "artifact_records",
        "kernel_artifact_refs",
        "causal_consumption_refs",
        "evidence_refs",
        "limitation_refs",
        "source_provider_call_count",
        "source_network_call_count",
        "source_gemini_call_count",
        "projection_provider_call_count",
        "projection_network_call_count",
        "projection_gemini_call_count",
        "created_authority_count",
        "created_permission_count",
        "real_world_effects_count",
        "status",
    ),
}


def _programme(
    *,
    programme_id: str = PROGRAMME_ID,
    programme_version: str = PROGRAMME_VERSION,
) -> profile.ProgrammeEvidenceIdentityV01:
    return profile.build_programme_evidence_identity_v01(
        programme_id=programme_id,
        programme_version=programme_version,
    )


def _domain(
    programme_identity: profile.ProgrammeEvidenceIdentityV01 | None = None,
    *,
    domain_id: str = DOMAIN_ID,
    execution_head: str = EXECUTION_HEAD,
    source_task_id: str = SOURCE_TASK_ID,
    run_id: str = RUN_ID,
    report_id: str = REPORT_ID,
) -> profile.DomainExecutionIdentityV01:
    return profile.build_domain_execution_identity_v01(
        programme_identity=programme_identity or _programme(),
        domain_id=domain_id,
        execution_head=execution_head,
        source_task_id=source_task_id,
        run_id=run_id,
        report_id=report_id,
    )


def _attempt(
    programme_identity: profile.ProgrammeEvidenceIdentityV01 | None = None,
    domain_execution_identity: profile.DomainExecutionIdentityV01 | None = None,
    *,
    provider_mode: str = "deterministic_fixture",
    expected_actor_count: int = 1,
    provider_call_budget: int = 0,
    package_id: str = "package:airline:attempt_01",
    logical_package_ref: str = "airline/attempt_01/package",
    output_directory_ref: str = "airline/attempt_01/output",
    attempt_number: int = 1,
) -> profile.LiveAttemptIdentityV01:
    programme_item = programme_identity or _programme()
    domain_item = domain_execution_identity or _domain(programme_item)
    return profile.build_live_attempt_identity_v01(
        programme_identity=programme_item,
        domain_execution_identity=domain_item,
        attempt_number=attempt_number,
        package_id=package_id,
        logical_package_ref=logical_package_ref,
        output_directory_ref=output_directory_ref,
        provider_mode=provider_mode,
        model_id="fixture-model" if provider_mode == "deterministic_fixture" else "gemini-2.5-flash",
        expected_actor_count=expected_actor_count,
        provider_call_budget=provider_call_budget,
    )


def _source(
    *,
    source_id: str = "source:airline:execution",
    evidence_class: str = "EXECUTED_DETERMINISTIC_RUNTIME",
    canonical_projection: object | None = None,
    trace_refs: tuple[str, ...] = ("trace:source",),
    contains_raw_prompt: bool = False,
    contains_raw_provider_response: bool = False,
    secret_scan_passed: bool = True,
    calls: int = 0,
    provider_calls: int | None = None,
    network_calls: int | None = None,
    gemini_calls: int | None = None,
    effects: int = 0,
) -> profile.SafeSourceRecordV01:
    return profile.build_safe_source_record_v01(
        source_id=source_id,
        source_type="safe_execution_projection",
        evidence_class=evidence_class,
        canonical_projection=(
            {"source": source_id, "status": "observed"}
            if canonical_projection is None
            else canonical_projection
        ),
        media_type="application/json",
        trace_refs=trace_refs,
        contains_raw_prompt=contains_raw_prompt,
        contains_raw_provider_response=contains_raw_provider_response,
        secret_scan_passed=secret_scan_passed,
        observed_provider_call_count=calls if provider_calls is None else provider_calls,
        observed_network_call_count=calls if network_calls is None else network_calls,
        observed_gemini_call_count=calls if gemini_calls is None else gemini_calls,
        real_world_effects_count=effects,
    )


def _artifact(
    source: profile.SafeSourceRecordV01,
    *,
    artifact_id: str = "artifact:airline:execution",
    evidence_class: str = "EXECUTED_DETERMINISTIC_RUNTIME",
    source_record_ids: tuple[str, ...] | None = None,
    canonical_projection: object | None = None,
    owner_root_id: str | None = "root:airline",
    authority: int = 0,
    permission: int = 0,
    effects: int = 0,
) -> profile.EvidenceArtifactRecordV01:
    return profile.build_evidence_artifact_record_v01(
        artifact_id=artifact_id,
        artifact_type="safe_execution_evidence",
        evidence_class=evidence_class,
        source_record_ids=(source.source_record_id,)
        if source_record_ids is None
        else source_record_ids,
        canonical_projection=(
            {"artifact": artifact_id, "source": source.source_record_id}
            if canonical_projection is None
            else canonical_projection
        ),
        authority_class="NON_AUTHORITY",
        owner_root_id=owner_root_id,
        trace_refs=("trace:artifact",),
        created_authority_count=authority,
        created_permission_count=permission,
        real_world_effects_count=effects,
    )


def _kernel_ref(artifact_id: str = "kernel:artifact:01") -> CanonicalArtifactRefV01:
    return CanonicalArtifactRefV01(
        artifact_id=artifact_id,
        artifact_type="SemanticEvidence",
        schema_version="v1",
        transaction_id="transaction:fixture",
        owner_root_id="root:fixture",
        authority_class="EVIDENCE_ONLY",
        lifecycle_state="VALIDATED",
        payload_hash="a" * 64,
    )


def _causal_ref(
    source_artifact_id: str = "kernel:artifact:01",
    downstream_artifact_id: str = "kernel:artifact:02",
) -> CausalConsumptionRefV01:
    return build_causal_consumption_ref_v01(
        producer_actor_id="actor:producer",
        source_artifact_id=source_artifact_id,
        output_field="/safe_hash",
        consumer_component="component:consumer",
        downstream_artifact_id=downstream_artifact_id,
        decision_effect="evidence_continuity",
        disposition="USED",
        reason_code="used:evidence_continuity",
        trace_refs=("trace:causal",),
    )


def _projection(
    *,
    programme_identity: profile.ProgrammeEvidenceIdentityV01 | None = None,
    domain_execution_identity: profile.DomainExecutionIdentityV01 | None = None,
    attempt_identity: profile.LiveAttemptIdentityV01 | None = None,
    source_records: tuple[profile.SafeSourceRecordV01, ...] | None = None,
    artifact_records: tuple[profile.EvidenceArtifactRecordV01, ...] | None = None,
    kernel_artifact_refs: tuple[CanonicalArtifactRefV01, ...] = (),
    causal_consumption_refs: tuple[CausalConsumptionRefV01, ...] = (),
    evidence_refs: tuple[str, ...] = ("evidence:fixture",),
    limitation_refs: tuple[str, ...] = ("limitation:fixture_only",),
) -> profile.DomainEvidenceProjectionV01:
    programme_item = programme_identity or _programme()
    domain_item = domain_execution_identity or _domain(programme_item)
    attempt_item = attempt_identity or _attempt(programme_item, domain_item)
    sources = source_records or (_source(),)
    artifacts = artifact_records or (_artifact(sources[0]),)
    return profile.build_domain_evidence_projection_v01(
        programme_identity=programme_item,
        domain_execution_identity=domain_item,
        attempt_identity=attempt_item,
        source_records=sources,
        artifact_records=artifacts,
        kernel_artifact_refs=kernel_artifact_refs,
        causal_consumption_refs=causal_consumption_refs,
        evidence_refs=evidence_refs,
        limitation_refs=limitation_refs,
    )


def _real_projection(call_count: int, domain_id: str) -> profile.DomainEvidenceProjectionV01:
    programme_item = _programme()
    domain_item = _domain(
        programme_item,
        domain_id=domain_id,
        source_task_id=f"source_task:{domain_id}:attempt_01",
        run_id=f"run:{domain_id}:attempt_01",
        report_id=f"report:{domain_id}:attempt_01",
    )
    attempt_item = _attempt(
        programme_item,
        domain_item,
        provider_mode="real_provider",
        expected_actor_count=call_count,
        provider_call_budget=call_count,
        package_id=f"package:{domain_id}:attempt_01",
        logical_package_ref=f"{domain_id}/attempt_01/package",
        output_directory_ref=f"{domain_id}/attempt_01/output",
    )
    source = _source(
        source_id=f"source:{domain_id}:live_execution",
        evidence_class="EXECUTED_LIVE_RUNTIME",
        calls=call_count,
    )
    artifact = _artifact(source, artifact_id=f"artifact:{domain_id}:execution")
    return _projection(
        programme_identity=programme_item,
        domain_execution_identity=domain_item,
        attempt_identity=attempt_item,
        source_records=(source,),
        artifact_records=(artifact,),
    )


def _contains_forbidden_projection_value(value: object) -> bool:
    if isinstance(value, (bytes, bytearray, tuple)) or is_dataclass(value):
        return True
    if isinstance(value, dict):
        return any(
            _contains_forbidden_projection_value(key)
            or _contains_forbidden_projection_value(item)
            for key, item in value.items()
        )
    if isinstance(value, list):
        return any(_contains_forbidden_projection_value(item) for item in value)
    return False


def _package_projection(
    *,
    call_count: int = 0,
    domain_id: str = "airline",
    fail_closed: bool = False,
    extra_source: bool = False,
) -> tuple[profile.DomainEvidenceProjectionV01, str]:
    kernel_hash = "e" * 64
    if call_count:
        base = _real_projection(call_count, domain_id)
        programme_item = base.programme_identity
        domain_item = base.domain_execution_identity
        attempt_item = base.attempt_identity
        primary_source = base.source_records[0]
        primary_artifact = base.artifact_records[0]
    else:
        programme_item = _programme()
        domain_item = _domain(programme_item, domain_id=domain_id)
        attempt_item = _attempt(programme_item, domain_item)
        primary_source = _source(
            evidence_class=(
                "EXECUTED_DETERMINISTIC_RUNTIME"
                if fail_closed
                else "CRYPTOGRAPHIC_INTEGRITY"
            ),
            canonical_projection={"kernel_manifest": "grounded"},
            trace_refs=("trace:kernel_manifest", kernel_hash),
            contains_raw_prompt=fail_closed,
        )
        primary_artifact = _artifact(primary_source)
    sources = (primary_source,)
    artifacts = (primary_artifact,)
    if extra_source:
        secondary_source = _source(source_id="source:secondary")
        sources += (secondary_source,)
        artifacts += (
            _artifact(secondary_source, artifact_id="artifact:secondary"),
        )
    crypto_source = (
        _source(
            source_id="source:kernel_manifest",
            evidence_class="CRYPTOGRAPHIC_INTEGRITY",
            canonical_projection={"kernel_manifest": "grounded"},
            trace_refs=("trace:kernel_manifest", kernel_hash),
        )
        if call_count or fail_closed
        else primary_source
    )
    if call_count or fail_closed:
        sources += (crypto_source,)
    artifacts += (
        _artifact(
            crypto_source,
            artifact_id="artifact:kernel_manifest",
            evidence_class="CRYPTOGRAPHIC_INTEGRITY",
            canonical_projection={"kernel_manifest": "grounded"},
        ),
    )
    projection_item = _projection(
        programme_identity=programme_item,
        domain_execution_identity=domain_item,
        attempt_identity=attempt_item,
        source_records=sources,
        artifact_records=artifacts,
    )
    return projection_item, kernel_hash


def _safe_file(
    source_record_ids: tuple[str, ...],
    *,
    logical_path: str = "evidence/runtime.json",
    media_type: str = "application/json",
    content: bytes = b'{"status":"safe"}\n',
    evidence_class: str = "EXECUTED_DETERMINISTIC_RUNTIME",
    terminal_newline_required: bool = True,
    secret_scan_passed: bool = True,
) -> sealed_package.SafeFileRecordV01:
    return sealed_package.build_safe_file_record_v01(
        logical_path=logical_path,
        media_type=media_type,
        content_bytes=content,
        evidence_class=evidence_class,
        source_record_ids=source_record_ids,
        terminal_newline_required=terminal_newline_required,
        secret_scan_passed=secret_scan_passed,
    )


def _manifest_fixture(
    *,
    call_count: int = 0,
    domain_id: str = "airline",
    fail_closed: bool = False,
    extra_source: bool = False,
) -> tuple[
    profile.DomainEvidenceProjectionV01,
    tuple[sealed_package.SafeFileRecordV01, ...],
    tuple[bytes, ...],
    sealed_package.SealedPackageManifestV01,
]:
    projection_item, kernel_hash = _package_projection(
        call_count=call_count,
        domain_id=domain_id,
        fail_closed=fail_closed,
        extra_source=extra_source,
    )
    source_ids = tuple(item.source_record_id for item in projection_item.source_records)
    contents = (b'{"status":"safe"}\n',)
    files = (_safe_file(source_ids, content=contents[0]),)
    manifest = sealed_package.build_sealed_package_manifest_v01(
        domain_projection=projection_item,
        safe_file_records=files,
        safe_file_contents=contents,
        kernel_manifest_hash=kernel_hash,
    )
    return projection_item, files, contents, manifest


def _two_file_manifest_fixture() -> tuple[
    profile.DomainEvidenceProjectionV01,
    tuple[sealed_package.SafeFileRecordV01, ...],
    tuple[bytes, ...],
    sealed_package.SealedPackageManifestV01,
]:
    projection_item, kernel_hash = _package_projection()
    source_ids = (projection_item.source_records[0].source_record_id,)
    contents = (b"alpha\n", b"beta\n")
    files = (
        _safe_file(
            source_ids,
            logical_path="evidence/alpha.txt",
            media_type="text/plain",
            content=contents[0],
        ),
        _safe_file(
            source_ids,
            logical_path="evidence/beta.txt",
            media_type="text/plain",
            content=contents[1],
        ),
    )
    manifest = sealed_package.build_sealed_package_manifest_v01(
        domain_projection=projection_item,
        safe_file_records=files,
        safe_file_contents=contents,
        kernel_manifest_hash=kernel_hash,
    )
    return projection_item, files, contents, manifest


def _rehash_file(
    result: sealed_package.SafeFileRecordV01,
) -> sealed_package.SafeFileRecordV01:
    return replace(
        result,
        file_record_id=sealed_package._safe_file_identity(result),
    )


def _rehash_source(
    result: profile.SafeSourceRecordV01,
) -> profile.SafeSourceRecordV01:
    return replace(
        result,
        source_record_id=profile._identity_hash(
            profile._SAFE_SOURCE_RECORD_DOMAIN,
            profile._safe_source_record_plain(result, include_id=False),
        ),
    )


def _rehash_manifest(
    result: sealed_package.SealedPackageManifestV01,
) -> sealed_package.SealedPackageManifestV01:
    return replace(
        result,
        manifest_id=sealed_package._manifest_identity(result),
    )


def _anchor_fixture(
    *,
    call_count: int = 0,
    domain_id: str = "airline",
    fail_closed: bool = False,
) -> tuple[
    profile.DomainEvidenceProjectionV01,
    tuple[bytes, ...],
    sealed_package.SealedPackageManifestV01,
    external_anchor.ExternalAnchorPublicationV01,
]:
    projection_item, _, contents, manifest = _manifest_fixture(
        call_count=call_count,
        domain_id=domain_id,
        fail_closed=fail_closed,
    )
    publication = external_anchor.build_external_anchor_publication_v01(
        manifest=manifest,
        domain_projection=projection_item,
        safe_file_contents=contents,
        publication_base_head=projection_item.domain_execution_identity.execution_head,
    )
    return projection_item, contents, manifest, publication


def _verification_fixture(
    *,
    call_count: int = 0,
    domain_id: str = "airline",
    fail_closed: bool = False,
    supplied_anchor_publication_id: str | None = None,
) -> tuple[
    profile.DomainEvidenceProjectionV01,
    tuple[bytes, ...],
    sealed_package.SealedPackageManifestV01,
    external_anchor.ExternalAnchorPublicationV01,
    external_anchor.AnchoredPackageVerificationV01,
]:
    projection_item, contents, manifest, publication = _anchor_fixture(
        call_count=call_count,
        domain_id=domain_id,
        fail_closed=fail_closed,
    )
    supplied = (
        publication.anchor_publication_id
        if supplied_anchor_publication_id is None
        else supplied_anchor_publication_id
    )
    verification = external_anchor.build_anchored_package_verification_v01(
        anchor_publication=publication,
        manifest=manifest,
        domain_projection=projection_item,
        safe_file_contents=contents,
        supplied_anchor_publication_id=supplied,
    )
    return projection_item, contents, manifest, publication, verification


def _rehash_publication(
    result: external_anchor.ExternalAnchorPublicationV01,
) -> external_anchor.ExternalAnchorPublicationV01:
    return replace(
        result,
        anchor_publication_id=external_anchor._publication_identity(result),
    )


def _rehash_verification(
    result: external_anchor.AnchoredPackageVerificationV01,
) -> external_anchor.AnchoredPackageVerificationV01:
    return replace(
        result,
        anchored_verification_id=external_anchor._verification_identity(result),
    )


def _replay_fixture(
    *,
    call_count: int = 0,
    domain_id: str = "airline",
    fail_closed: bool = False,
    publication_base_head: str | None = None,
    supplied_anchor_publication_id: str | None = None,
    reconstructed_context: tuple[
        profile.DomainEvidenceProjectionV01,
        tuple[bytes, ...],
        sealed_package.SealedPackageManifestV01,
    ]
    | None = None,
    evidence_refs: tuple[str, ...] = ("evidence/replay/source",),
) -> tuple[dict[str, object], sealed_replay.SealedReplayEvidenceV01]:
    source_projection, _, source_contents, source_manifest = _manifest_fixture(
        call_count=call_count,
        domain_id=domain_id,
        fail_closed=fail_closed,
    )
    base_head = (
        source_projection.domain_execution_identity.execution_head
        if publication_base_head is None
        else publication_base_head
    )
    publication = external_anchor.build_external_anchor_publication_v01(
        manifest=source_manifest,
        domain_projection=source_projection,
        safe_file_contents=source_contents,
        publication_base_head=base_head,
    )
    supplied = (
        publication.anchor_publication_id
        if supplied_anchor_publication_id is None
        else supplied_anchor_publication_id
    )
    verification = external_anchor.build_anchored_package_verification_v01(
        anchor_publication=publication,
        manifest=source_manifest,
        domain_projection=source_projection,
        safe_file_contents=source_contents,
        supplied_anchor_publication_id=supplied,
    )
    if reconstructed_context is None:
        reconstructed_projection = source_projection
        reconstructed_contents = source_contents
        reconstructed_manifest = source_manifest
    else:
        (
            reconstructed_projection,
            reconstructed_contents,
            reconstructed_manifest,
        ) = reconstructed_context
    context: dict[str, object] = {
        "source_manifest": source_manifest,
        "source_domain_projection": source_projection,
        "source_safe_file_contents": source_contents,
        "anchor_publication": publication,
        "anchored_verification": verification,
        "supplied_anchor_publication_id": supplied,
        "reconstructed_manifest": reconstructed_manifest,
        "reconstructed_domain_projection": reconstructed_projection,
        "reconstructed_safe_file_contents": reconstructed_contents,
    }
    result = sealed_replay.build_sealed_replay_evidence_v01(
        **context,  # type: ignore[arg-type]
        evidence_refs=evidence_refs,
    )
    return context, result


def _changed_byte_reconstruction(
    source_projection: profile.DomainEvidenceProjectionV01,
    source_manifest: sealed_package.SealedPackageManifestV01,
) -> tuple[
    profile.DomainEvidenceProjectionV01,
    tuple[bytes, ...],
    sealed_package.SealedPackageManifestV01,
]:
    contents = (b'{"status":"changed"}\n',)
    source_ids = tuple(
        item.source_record_id for item in source_projection.source_records
    )
    files = (_safe_file(source_ids, content=contents[0]),)
    manifest = sealed_package.build_sealed_package_manifest_v01(
        domain_projection=source_projection,
        safe_file_records=files,
        safe_file_contents=contents,
        kernel_manifest_hash=source_manifest.kernel_manifest_hash,
    )
    return source_projection, contents, manifest


def _rehash_replay(
    result: sealed_replay.SealedReplayEvidenceV01,
) -> sealed_replay.SealedReplayEvidenceV01:
    return replace(result, replay_id=sealed_replay._replay_identity(result))


@pytest.mark.parametrize("name", DATACLASS_NAMES)
def test_public_dataclass_field_order_is_exact(name: str) -> None:
    contract = getattr(profile, name)
    assert is_dataclass(contract)
    assert tuple(field.name for field in fields(contract)) == FIELD_NAMES[name]
    assert hasattr(contract, "__slots__")


@pytest.mark.parametrize("name", DATACLASS_NAMES)
def test_public_dataclasses_are_frozen(name: str) -> None:
    instances = {
        "ProgrammeEvidenceIdentityV01": _programme(),
        "DomainExecutionIdentityV01": _domain(),
        "LiveAttemptIdentityV01": _attempt(),
        "SafeSourceRecordV01": _source(),
        "EvidenceArtifactRecordV01": _artifact(_source()),
        "DomainEvidenceProjectionV01": _projection(),
    }
    instance = instances[name]
    with pytest.raises(FrozenInstanceError):
        setattr(instance, fields(instance)[0].name, "changed")


def test_exact_public_function_surface() -> None:
    public_functions = tuple(
        name
        for name, value in vars(profile).items()
        if not name.startswith("_") and inspect.isfunction(value)
    )
    assert public_functions == MODULE_FUNCTION_NAMES


def test_temporary_package_all_is_exact() -> None:
    assert evidence.__all__ == PACKAGE_ALL
    assert len(evidence.__all__) == 44


@pytest.mark.parametrize("name", PACKAGE_ALL)
def test_temporary_package_attributes_are_direct(name: str) -> None:
    package_names = (
        PACKAGE_DATACLASS_NAMES
        + PACKAGE_BUILDER_NAMES
        + PACKAGE_VALIDATOR_NAMES
        + PACKAGE_PROJECTION_NAMES
    )
    anchor_names = (
        ANCHOR_DATACLASS_NAMES
        + ANCHOR_BUILDER_NAMES
        + ANCHOR_VALIDATOR_NAMES
        + ANCHOR_PROJECTION_NAMES
    )
    replay_names = (
        REPLAY_DATACLASS_NAMES
        + REPLAY_BUILDER_NAMES
        + REPLAY_VALIDATOR_NAMES
        + REPLAY_PROJECTION_NAMES
    )
    if name in package_names:
        source_module = sealed_package
    elif name in anchor_names:
        source_module = external_anchor
    elif name in replay_names:
        source_module = sealed_replay
    else:
        source_module = profile
    assert getattr(evidence, name) is getattr(source_module, name)


def test_annotations_name_is_absent() -> None:
    assert "annotations" not in vars(profile)
    assert "annotations" not in vars(sealed_replay)
    assert "annotations" not in vars(evidence)


def test_no_accidental_public_class_or_function() -> None:
    public_classes = tuple(
        name
        for name, value in vars(profile).items()
        if not name.startswith("_") and inspect.isclass(value)
    )
    assert public_classes == DATACLASS_NAMES


def test_constants_are_exact() -> None:
    assert profile.MODULE_ID == "sealed_evidence_profile_v01"
    assert profile.PROFILE_VERSION == "v0.1"
    assert profile.PROFILE_STATUSES == ("PASS", "FAIL_CLOSED")
    assert profile.PROVIDER_MODES == ("deterministic_fixture", "real_provider")


@pytest.mark.parametrize(
    ("index", "evidence_class"),
    tuple(enumerate((
        "LIVE_PROVIDER_RAW_PRIVATE",
        "LIVE_PROVIDER_SAFE_PROJECTION",
        "EXECUTED_LIVE_RUNTIME",
        "EXECUTED_DETERMINISTIC_RUNTIME",
        "ROOT_DECISION_EVIDENCE",
        "CORRIDOR_EVIDENCE",
        "NEGATIVE_CONFORMANCE",
        "CRYPTOGRAPHIC_INTEGRITY",
        "EXTERNAL_ANCHOR",
        "REPLAY_EVIDENCE",
        "INDEPENDENT_AUDIT",
        "HISTORICAL_REFERENCE",
        "PUBLIC_SHOWCASE",
    ))),
)
def test_evidence_class_order_is_exact(index: int, evidence_class: str) -> None:
    assert profile.EVIDENCE_CLASSES[index] == evidence_class


def test_raw_private_is_not_repository_allowed() -> None:
    assert "LIVE_PROVIDER_RAW_PRIVATE" not in profile.REPOSITORY_ALLOWED_EVIDENCE_CLASSES
    assert profile.REPOSITORY_ALLOWED_EVIDENCE_CLASSES == profile.EVIDENCE_CLASSES[1:]
    assert type(profile.EVIDENCE_CLASSES) is tuple
    assert type(profile.REPOSITORY_ALLOWED_EVIDENCE_CLASSES) is tuple


def test_programme_identity_is_deterministic() -> None:
    assert _programme() == _programme()
    assert _programme().programme_identity_id == _programme().programme_identity_id


@pytest.mark.parametrize("field", ("programme_id", "programme_version"))
def test_programme_semantic_change_changes_identity(field: str) -> None:
    baseline = _programme()
    kwargs = {"programme_id": PROGRAMME_ID, "programme_version": PROGRAMME_VERSION}
    kwargs[field] += ":changed"
    changed = _programme(**kwargs)
    assert changed.programme_identity_id != baseline.programme_identity_id


@pytest.mark.parametrize(
    "invalid",
    ("", " leading", "trailing ", "line\nbreak", "nul\x00value", "\ud800"),
)
@pytest.mark.parametrize("field", ("programme_id", "programme_version"))
def test_programme_invalid_text_fails_closed(field: str, invalid: str) -> None:
    kwargs = {"programme_id": PROGRAMME_ID, "programme_version": PROGRAMME_VERSION}
    kwargs[field] = invalid
    with pytest.raises(ValueError, match="^programme_evidence_identity_invalid$"):
        _programme(**kwargs)


@pytest.mark.parametrize("code_point", (0x202E, 0x200B, 0xFEFF, 0x2028, 0x2029))
@pytest.mark.parametrize(
    ("boundary", "expected_reason"),
    (
        ("programme_id", "programme_evidence_identity_invalid"),
        ("source_id", "safe_source_record_invalid"),
        ("artifact_id", "evidence_artifact_record_invalid"),
        ("logical_package_ref", "live_attempt_identity_invalid"),
        ("output_directory_ref", "live_attempt_identity_invalid"),
        ("evidence_refs", "evidence_duplicate_identity"),
    ),
)
def test_unicode_control_and_format_characters_are_rejected(
    code_point: int,
    boundary: str,
    expected_reason: str,
) -> None:
    invalid = f"safe{chr(code_point)}value"
    with pytest.raises(ValueError) as captured:
        if boundary == "programme_id":
            _programme(programme_id=invalid)
        elif boundary == "source_id":
            _source(source_id=invalid)
        elif boundary == "artifact_id":
            _artifact(_source(), artifact_id=invalid)
        elif boundary == "logical_package_ref":
            _attempt(logical_package_ref=f"airline/{invalid}/package")
        elif boundary == "output_directory_ref":
            _attempt(output_directory_ref=f"airline/{invalid}/output")
        else:
            _projection(evidence_refs=(invalid,))
    assert str(captured.value) == expected_reason


@pytest.mark.parametrize(
    "ordinary_text",
    (
        "\u0414\u043e\u043a\u0430\u0437\u0430\u0442\u0435\u043b\u044c\u0441\u0442\u0432\u043e",
        "caf\u00e9",
        "\u8a3c\u62e0",
    ),
)
def test_ordinary_unicode_text_remains_accepted(ordinary_text: str) -> None:
    programme_item = _programme(programme_id=f"programme:{ordinary_text}")
    domain_item = _domain(programme_item)
    attempt_item = _attempt(
        programme_item,
        domain_item,
        logical_package_ref=f"airline/{ordinary_text}/package",
        output_directory_ref=f"airline/{ordinary_text}/output",
    )
    source = _source(source_id=f"source:{ordinary_text}")
    artifact = _artifact(source, artifact_id=f"artifact:{ordinary_text}")
    result = _projection(
        programme_identity=programme_item,
        domain_execution_identity=domain_item,
        attempt_identity=attempt_item,
        source_records=(source,),
        artifact_records=(artifact,),
        evidence_refs=(f"evidence:{ordinary_text}",),
        limitation_refs=(f"limitation:{ordinary_text}",),
    )
    assert result.status == "PASS"


def test_programme_stale_identity_is_rejected() -> None:
    changed = replace(_programme(), programme_identity_id="0" * 64)
    assert "evidence_identity_mismatch" in profile.validate_programme_evidence_identity_v01(changed)
    with pytest.raises(ValueError, match="^programme_evidence_identity_invalid$"):
        profile.programme_evidence_identity_to_plain_dict_v01(changed)


def test_programme_projection_is_isolated() -> None:
    item = _programme()
    plain = profile.programme_evidence_identity_to_plain_dict_v01(item)
    plain["programme_id"] = "changed"
    assert item.programme_id == PROGRAMME_ID


@pytest.mark.parametrize("head", ("", "ABCDEF1", "123456", "g123456", "a" * 41, " abcdef1", "abcdef1 "))
def test_domain_execution_head_is_strict(head: str) -> None:
    with pytest.raises(ValueError, match="^domain_execution_identity_invalid$"):
        _domain(execution_head=head)


@pytest.mark.parametrize("head", ("abcdef1", "0" * 40, "1234567890abcdef"))
def test_domain_execution_head_valid_lengths(head: str) -> None:
    assert _domain(execution_head=head).execution_head == head


def test_domain_identity_is_deterministic_and_bound_to_programme() -> None:
    programme_item = _programme()
    first = _domain(programme_item)
    second = _domain(programme_item)
    assert first == second
    assert first.programme_identity_id == programme_item.programme_identity_id


def test_domain_stale_identity_is_rejected() -> None:
    changed = replace(_domain(), domain_execution_identity_id="0" * 64)
    assert "evidence_identity_mismatch" in profile.validate_domain_execution_identity_v01(changed)


def test_domain_projection_is_isolated() -> None:
    item = _domain()
    plain = profile.domain_execution_identity_to_plain_dict_v01(item)
    plain["domain_id"] = "changed"
    assert item.domain_id == DOMAIN_ID


@pytest.mark.parametrize("attempt_number", (0, -1, True, 1.0, "1"))
def test_attempt_number_must_be_positive_exact_int(attempt_number: object) -> None:
    with pytest.raises(ValueError, match="^live_attempt_identity_invalid$"):
        _attempt(attempt_number=attempt_number)  # type: ignore[arg-type]


@pytest.mark.parametrize("count", (-1, True, 1.0, "1"))
@pytest.mark.parametrize("field", ("expected_actor_count", "provider_call_budget"))
def test_attempt_counts_are_exact_int(field: str, count: object) -> None:
    kwargs: dict[str, object] = {"expected_actor_count": 1, "provider_call_budget": 0}
    kwargs[field] = count
    with pytest.raises(ValueError, match="^live_attempt_identity_invalid$"):
        _attempt(**kwargs)  # type: ignore[arg-type]


def test_expected_actor_count_must_be_positive() -> None:
    with pytest.raises(ValueError, match="^live_attempt_identity_invalid$"):
        _attempt(expected_actor_count=0)


@pytest.mark.parametrize(
    "path",
    (
        "",
        "/absolute",
        "C:/absolute",
        "C:\\absolute",
        "../parent",
        "child/../parent",
        "./child",
        "child/./item",
        "child//item",
        "child/",
        " leading/path",
        "trailing/path ",
        "nul\x00path",
        "surrogate/\ud800",
        "cafe\u0301/path",
    ),
)
@pytest.mark.parametrize("field", ("logical_package_ref", "output_directory_ref"))
def test_attempt_logical_path_attacks_are_rejected(field: str, path: str) -> None:
    kwargs = {
        "logical_package_ref": "airline/attempt_01/package",
        "output_directory_ref": "airline/attempt_01/output",
    }
    kwargs[field] = path
    with pytest.raises(ValueError, match="^live_attempt_identity_invalid$"):
        _attempt(**kwargs)


@pytest.mark.parametrize("mode", profile.PROVIDER_MODES)
def test_attempt_provider_modes_are_supported(mode: str) -> None:
    budget = 0 if mode == "deterministic_fixture" else 12
    assert _attempt(
        provider_mode=mode,
        expected_actor_count=1 if budget == 0 else budget,
        provider_call_budget=budget,
    ).provider_mode == mode


def test_unknown_provider_mode_is_rejected() -> None:
    with pytest.raises(ValueError, match="^live_attempt_identity_invalid$"):
        _attempt(provider_mode="unknown")


def test_attempt_stale_identity_is_rejected() -> None:
    changed = replace(_attempt(), attempt_identity_id="0" * 64)
    assert "evidence_identity_mismatch" in profile.validate_live_attempt_identity_v01(changed)


def test_changed_package_ref_changes_attempt_identity() -> None:
    assert _attempt().attempt_identity_id != _attempt(
        logical_package_ref="airline/attempt_01/other_package"
    ).attempt_identity_id


def test_safe_source_hash_and_byte_count_are_derived() -> None:
    projection = {"value": [1, "two"], "status": "safe"}
    item = _source(canonical_projection=projection)
    canonical = canonical_json_bytes_v01(projection)
    assert item.canonical_sha256 == hashlib.sha256(canonical).hexdigest()
    assert item.byte_count == len(canonical)


def test_safe_source_does_not_retain_caller_mapping() -> None:
    caller = {"items": ["original"]}
    item = _source(canonical_projection=caller)
    before = item.canonical_sha256
    caller["items"].append("changed")
    assert item.canonical_sha256 == before


def test_safe_source_copies_trace_tuple() -> None:
    trace_refs = ("trace:one", "trace:two")
    item = _source(trace_refs=trace_refs)
    assert item.trace_refs == trace_refs
    assert item.trace_refs is not trace_refs


@pytest.mark.parametrize("flag", ("contains_raw_prompt", "contains_raw_provider_response", "secret_scan_passed"))
def test_safe_source_boolean_flags_require_exact_bool(flag: str) -> None:
    kwargs = {
        "contains_raw_prompt": False,
        "contains_raw_provider_response": False,
        "secret_scan_passed": True,
    }
    kwargs[flag] = 1
    with pytest.raises(ValueError, match="^safe_source_record_invalid$"):
        _source(**kwargs)  # type: ignore[arg-type]


@pytest.mark.parametrize("count", (-1, True, 1.0, "1"))
@pytest.mark.parametrize("field", ("provider_calls", "network_calls", "gemini_calls", "effects"))
def test_safe_source_counts_are_nonnegative_exact_int(field: str, count: object) -> None:
    with pytest.raises(ValueError, match="^safe_source_record_invalid$"):
        _source(**{field: count})  # type: ignore[arg-type]


def test_safe_source_identity_is_deterministic() -> None:
    assert _source() == _source()


def test_safe_source_stale_identity_is_rejected() -> None:
    changed = replace(_source(), source_record_id="0" * 64)
    assert "evidence_identity_mismatch" in profile.validate_safe_source_record_v01(changed)


def test_canonical_numeric_distinctions_change_source_hash() -> None:
    integer = _source(canonical_projection={"value": 1})
    floating = _source(canonical_projection={"value": 1.0})
    assert integer.canonical_sha256 != floating.canonical_sha256
    assert integer.source_record_id != floating.source_record_id


def test_source_projection_rejects_surrogate_projection() -> None:
    with pytest.raises(ValueError, match="^safe_source_record_invalid$"):
        _source(canonical_projection={"value": "\ud800"})


def test_artifact_hash_is_derived_and_owner_is_optional() -> None:
    source = _source()
    projection = {"artifact": "safe", "sequence": [1, 2]}
    item = _artifact(source, canonical_projection=projection, owner_root_id=None)
    assert item.canonical_sha256 == hashlib.sha256(
        canonical_json_bytes_v01(projection)
    ).hexdigest()
    assert item.owner_root_id is None


def test_artifact_source_and_trace_tuples_are_copied() -> None:
    source = _source()
    source_refs = (source.source_record_id,)
    item = _artifact(source, source_record_ids=source_refs)
    assert item.source_record_ids == source_refs
    assert item.source_record_ids is not source_refs


@pytest.mark.parametrize("count", (-1, True, 1.0, "1"))
@pytest.mark.parametrize("field", ("authority", "permission", "effects"))
def test_artifact_counts_are_nonnegative_exact_int(field: str, count: object) -> None:
    with pytest.raises(ValueError, match="^evidence_artifact_record_invalid$"):
        _artifact(_source(), **{field: count})  # type: ignore[arg-type]


def test_artifact_duplicate_source_refs_are_rejected() -> None:
    source = _source()
    with pytest.raises(ValueError, match="^evidence_artifact_record_invalid$"):
        _artifact(
            source,
            source_record_ids=(source.source_record_id, source.source_record_id),
        )


def test_artifact_stale_identity_is_rejected() -> None:
    changed = replace(_artifact(_source()), artifact_record_id="0" * 64)
    assert "evidence_identity_mismatch" in profile.validate_evidence_artifact_record_v01(changed)


def test_artifact_projection_is_isolated() -> None:
    item = _artifact(_source())
    plain = profile.evidence_artifact_record_to_plain_dict_v01(item)
    plain["source_record_ids"].append("changed")
    assert item.source_record_ids == (_source().source_record_id,)


def test_deterministic_fixture_projection_passes() -> None:
    result = _projection()
    assert result.status == "PASS"
    assert profile.validate_domain_evidence_projection_v01(result) == ()


@pytest.mark.parametrize(("calls", "domain_id"), ((12, "airline"), (6, "supplier_water_filter")))
def test_real_provider_shaped_projection_passes(calls: int, domain_id: str) -> None:
    result = _real_projection(calls, domain_id)
    assert result.status == "PASS"
    assert (
        result.source_provider_call_count,
        result.source_network_call_count,
        result.source_gemini_call_count,
    ) == (calls, calls, calls)
    assert (
        result.projection_provider_call_count,
        result.projection_network_call_count,
        result.projection_gemini_call_count,
    ) == (0, 0, 0)


def test_projection_copies_every_tuple() -> None:
    source = _source()
    artifact = _artifact(source)
    sources = (source,)
    artifacts = (artifact,)
    evidence_refs = ("evidence:one",)
    limitation_refs = ("limitation:one",)
    result = _projection(
        source_records=sources,
        artifact_records=artifacts,
        evidence_refs=evidence_refs,
        limitation_refs=limitation_refs,
    )
    assert result.source_records is not sources
    assert result.artifact_records is not artifacts
    assert result.evidence_refs is not evidence_refs
    assert result.limitation_refs is not limitation_refs


def test_projection_accepts_valid_kernel_and_causal_refs() -> None:
    result = _projection(
        kernel_artifact_refs=(_kernel_ref(),),
        causal_consumption_refs=(_causal_ref(),),
    )
    assert result.status == "PASS"


def test_two_live_count_sources_fail_closed() -> None:
    programme_item = _programme()
    domain_item = _domain(programme_item)
    attempt_item = _attempt(
        programme_item,
        domain_item,
        provider_mode="real_provider",
        expected_actor_count=12,
        provider_call_budget=12,
    )
    first = _source(
        source_id="source:live:one",
        evidence_class="EXECUTED_LIVE_RUNTIME",
        calls=6,
    )
    second = _source(
        source_id="source:live:two",
        evidence_class="EXECUTED_LIVE_RUNTIME",
        calls=6,
    )
    result = _projection(
        programme_identity=programme_item,
        domain_execution_identity=domain_item,
        attempt_identity=attempt_item,
        source_records=(first, second),
        artifact_records=(_artifact(first), _artifact(second, artifact_id="artifact:two")),
    )
    assert result.status == "FAIL_CLOSED"
    assert profile.validate_domain_evidence_projection_v01(result) == ()


def test_derivative_source_with_calls_fails_closed() -> None:
    programme_item = _programme()
    domain_item = _domain(programme_item)
    attempt_item = _attempt(
        programme_item,
        domain_item,
        provider_mode="real_provider",
        expected_actor_count=6,
        provider_call_budget=6,
    )
    source = _source(evidence_class="LIVE_PROVIDER_SAFE_PROJECTION", calls=6)
    result = _projection(
        programme_identity=programme_item,
        domain_execution_identity=domain_item,
        attempt_identity=attempt_item,
        source_records=(source,),
        artifact_records=(_artifact(source),),
    )
    assert result.status == "FAIL_CLOSED"
    assert profile.validate_domain_evidence_projection_v01(result) == ()


@pytest.mark.parametrize(
    "source",
    (
        _source(evidence_class="LIVE_PROVIDER_RAW_PRIVATE"),
        _source(contains_raw_prompt=True),
        _source(contains_raw_provider_response=True),
        _source(secret_scan_passed=False),
        _source(effects=1),
    ),
)
def test_source_safety_failures_produce_coherent_fail_closed(
    source: profile.SafeSourceRecordV01,
) -> None:
    result = _projection(
        source_records=(source,),
        artifact_records=(_artifact(source),),
    )
    assert result.status == "FAIL_CLOSED"
    assert profile.validate_domain_evidence_projection_v01(result) == ()
    assert profile.domain_evidence_projection_to_plain_dict_v01(result)["status"] == "FAIL_CLOSED"


@pytest.mark.parametrize(("authority", "permission", "effects"), ((1, 0, 0), (0, 1, 0), (0, 0, 1)))
def test_artifact_safety_failures_produce_coherent_fail_closed(
    authority: int,
    permission: int,
    effects: int,
) -> None:
    source = _source()
    artifact = _artifact(
        source,
        authority=authority,
        permission=permission,
        effects=effects,
    )
    result = _projection(source_records=(source,), artifact_records=(artifact,))
    assert result.status == "FAIL_CLOSED"
    assert profile.validate_domain_evidence_projection_v01(result) == ()


def test_real_provider_counter_mismatch_fails_closed() -> None:
    programme_item = _programme()
    domain_item = _domain(programme_item)
    attempt_item = _attempt(
        programme_item,
        domain_item,
        provider_mode="real_provider",
        expected_actor_count=6,
        provider_call_budget=6,
    )
    source = _source(
        evidence_class="EXECUTED_LIVE_RUNTIME",
        provider_calls=6,
        network_calls=5,
        gemini_calls=6,
    )
    result = _projection(
        programme_identity=programme_item,
        domain_execution_identity=domain_item,
        attempt_identity=attempt_item,
        source_records=(source,),
        artifact_records=(_artifact(source),),
    )
    assert result.status == "FAIL_CLOSED"


def test_deterministic_fixture_nonzero_budget_fails_closed() -> None:
    programme_item = _programme()
    domain_item = _domain(programme_item)
    attempt_item = _attempt(
        programme_item,
        domain_item,
        provider_call_budget=1,
    )
    result = _projection(
        programme_identity=programme_item,
        domain_execution_identity=domain_item,
        attempt_identity=attempt_item,
    )
    assert result.status == "FAIL_CLOSED"


def test_nested_identity_mismatch_is_rejected() -> None:
    programme_item = _programme()
    domain_item = _domain(programme_item)
    changed_domain = _domain(
        programme_item,
        run_id="run:airline:attempt_02",
        report_id="report:airline:attempt_02",
    )
    changed_attempt = _attempt(programme_item, changed_domain)
    with pytest.raises(ValueError, match="^evidence_nested_identity_mismatch$"):
        _projection(
            programme_identity=programme_item,
            domain_execution_identity=domain_item,
            attempt_identity=changed_attempt,
        )


def test_unresolved_artifact_source_is_rejected() -> None:
    source = _source()
    artifact = _artifact(source, source_record_ids=("source_record:missing",))
    with pytest.raises(ValueError, match="^evidence_reference_unresolved$"):
        _projection(source_records=(source,), artifact_records=(artifact,))


def test_duplicate_source_record_identity_is_rejected() -> None:
    source = _source()
    with pytest.raises(ValueError, match="^evidence_duplicate_identity$"):
        _projection(source_records=(source, source), artifact_records=(_artifact(source),))


def test_duplicate_source_id_is_rejected() -> None:
    first = _source()
    second = _source(canonical_projection={"different": True})
    with pytest.raises(ValueError, match="^evidence_duplicate_identity$"):
        _projection(
            source_records=(first, second),
            artifact_records=(_artifact(first),),
        )


def test_duplicate_artifact_identity_is_rejected() -> None:
    source = _source()
    artifact = _artifact(source)
    with pytest.raises(ValueError, match="^evidence_duplicate_identity$"):
        _projection(source_records=(source,), artifact_records=(artifact, artifact))


@pytest.mark.parametrize("field", ("evidence_refs", "limitation_refs"))
def test_duplicate_projection_refs_are_rejected(field: str) -> None:
    kwargs = {field: ("duplicate:ref", "duplicate:ref")}
    with pytest.raises(ValueError, match="^evidence_duplicate_identity$"):
        _projection(**kwargs)


def test_duplicate_kernel_artifact_identity_is_rejected() -> None:
    kernel = _kernel_ref()
    with pytest.raises(ValueError, match="^evidence_duplicate_identity$"):
        _projection(kernel_artifact_refs=(kernel, kernel))


def test_duplicate_causal_identity_is_rejected() -> None:
    causal = _causal_ref()
    with pytest.raises(ValueError, match="^evidence_duplicate_identity$"):
        _projection(causal_consumption_refs=(causal, causal))


def test_malformed_causal_ref_is_rejected() -> None:
    malformed = CausalConsumptionRefV01(
        producer_actor_id="actor:producer",
        source_artifact_id="kernel:artifact:01",
        output_field="not-a-pointer",
        consumer_component="component:consumer",
        downstream_artifact_id="kernel:artifact:02",
        decision_effect="continuity",
        disposition="USED",
        reason_code="used:continuity",
        trace_refs=("trace:causal",),
    )
    with pytest.raises(ValueError, match="^domain_evidence_projection_invalid$"):
        _projection(causal_consumption_refs=(malformed,))


def test_stored_pass_forgery_is_rejected_after_rehash() -> None:
    source = _source(contains_raw_prompt=True)
    valid_fail = _projection(
        source_records=(source,),
        artifact_records=(_artifact(source),),
    )
    forged = replace(valid_fail, status="PASS")
    forged = replace(forged, projection_id=profile._projection_identity(forged))
    assert "evidence_status_mismatch" in profile.validate_domain_evidence_projection_v01(forged)


def test_self_rehashed_nested_contradiction_is_rejected() -> None:
    valid = _projection()
    programme_item = valid.programme_identity
    changed_domain = _domain(
        programme_item,
        run_id="run:airline:attempt_02",
        report_id="report:airline:attempt_02",
    )
    forged = replace(
        valid,
        domain_execution_identity=changed_domain,
        status="FAIL_CLOSED",
    )
    forged = replace(forged, projection_id=profile._projection_identity(forged))
    errors = profile.validate_domain_evidence_projection_v01(forged)
    assert "evidence_nested_identity_mismatch" in errors
    with pytest.raises(ValueError, match="^domain_evidence_projection_invalid$"):
        profile.domain_evidence_projection_to_plain_dict_v01(forged)


@pytest.mark.parametrize(
    ("field", "reason"),
    (
        ("projection_provider_call_count", "evidence_external_call_forbidden"),
        ("projection_network_call_count", "evidence_external_call_forbidden"),
        ("projection_gemini_call_count", "evidence_external_call_forbidden"),
        ("source_provider_call_count", "evidence_external_call_forbidden"),
        ("created_authority_count", "evidence_authority_creation_forbidden"),
        ("created_permission_count", "evidence_permission_creation_forbidden"),
        ("real_world_effects_count", "evidence_effect_forbidden"),
    ),
)
def test_stored_counter_forgery_is_rejected(field: str, reason: str) -> None:
    forged = replace(_projection(), **{field: 1}, status="FAIL_CLOSED")
    forged = replace(forged, projection_id=profile._projection_identity(forged))
    assert reason in profile.validate_domain_evidence_projection_v01(forged)


@pytest.mark.parametrize(
    "field",
    (
        "source_provider_call_count",
        "source_network_call_count",
        "source_gemini_call_count",
    ),
)
@pytest.mark.parametrize("forged_value", (True, 1.0))
def test_real_source_counters_require_exact_int(
    field: str,
    forged_value: object,
) -> None:
    valid = _real_projection(1, "airline")
    assert getattr(valid, field) == forged_value
    assert type(forged_value) is not int
    forged = replace(valid, **{field: forged_value}, status="PASS")
    forged = replace(forged, projection_id=profile._projection_identity(forged))
    errors = profile.validate_domain_evidence_projection_v01(forged)
    assert "evidence_external_call_forbidden" in errors
    with pytest.raises(ValueError, match="^domain_evidence_projection_invalid$"):
        profile.domain_evidence_projection_to_plain_dict_v01(forged)


@pytest.mark.parametrize(
    "field",
    (
        "source_provider_call_count",
        "source_network_call_count",
        "source_gemini_call_count",
    ),
)
@pytest.mark.parametrize("forged_value", (False, 0.0))
def test_deterministic_source_counters_require_exact_int(
    field: str,
    forged_value: object,
) -> None:
    valid = _projection()
    assert getattr(valid, field) == forged_value
    assert type(forged_value) is not int
    forged = replace(valid, **{field: forged_value}, status="PASS")
    forged = replace(forged, projection_id=profile._projection_identity(forged))
    errors = profile.validate_domain_evidence_projection_v01(forged)
    assert "evidence_external_call_forbidden" in errors
    with pytest.raises(ValueError, match="^domain_evidence_projection_invalid$"):
        profile.domain_evidence_projection_to_plain_dict_v01(forged)


def test_projection_identity_is_order_sensitive() -> None:
    first = _source(source_id="source:first")
    second = _source(source_id="source:second")
    first_artifact = _artifact(first, artifact_id="artifact:first")
    second_artifact = _artifact(second, artifact_id="artifact:second")
    baseline = _projection(
        source_records=(first, second),
        artifact_records=(first_artifact, second_artifact),
    )
    reordered = _projection(
        source_records=(second, first),
        artifact_records=(second_artifact, first_artifact),
    )
    assert baseline.projection_id != reordered.projection_id


def test_projection_determinism_and_compact_json() -> None:
    first = _projection(kernel_artifact_refs=(_kernel_ref(),))
    second = _projection(kernel_artifact_refs=(_kernel_ref(),))
    assert first == second
    first_plain = profile.domain_evidence_projection_to_plain_dict_v01(first)
    second_plain = profile.domain_evidence_projection_to_plain_dict_v01(second)
    assert first_plain == second_plain
    assert json.dumps(first_plain, sort_keys=True, separators=(",", ":")) == json.dumps(
        second_plain,
        sort_keys=True,
        separators=(",", ":"),
    )


@pytest.mark.parametrize(
    "builder",
    (
        profile.build_programme_evidence_identity_v01,
        profile.build_domain_execution_identity_v01,
        profile.build_live_attempt_identity_v01,
        profile.build_safe_source_record_v01,
        profile.build_evidence_artifact_record_v01,
        profile.build_domain_evidence_projection_v01,
    ),
)
def test_builders_do_not_accept_status_or_identity_fields(builder: object) -> None:
    signature = inspect.signature(builder)
    forbidden = {
        "programme_identity_id",
        "domain_execution_identity_id",
        "attempt_identity_id",
        "source_record_id",
        "artifact_record_id",
        "projection_id",
        "status",
    }
    assert forbidden.isdisjoint(signature.parameters)


@pytest.mark.parametrize(
    ("value", "validator", "projector", "reason"),
    (
        (object(), profile.validate_programme_evidence_identity_v01, profile.programme_evidence_identity_to_plain_dict_v01, "programme_evidence_identity_invalid"),
        (object(), profile.validate_domain_execution_identity_v01, profile.domain_execution_identity_to_plain_dict_v01, "domain_execution_identity_invalid"),
        (object(), profile.validate_live_attempt_identity_v01, profile.live_attempt_identity_to_plain_dict_v01, "live_attempt_identity_invalid"),
        (object(), profile.validate_safe_source_record_v01, profile.safe_source_record_to_plain_dict_v01, "safe_source_record_invalid"),
        (object(), profile.validate_evidence_artifact_record_v01, profile.evidence_artifact_record_to_plain_dict_v01, "evidence_artifact_record_invalid"),
        (object(), profile.validate_domain_evidence_projection_v01, profile.domain_evidence_projection_to_plain_dict_v01, "domain_evidence_projection_invalid"),
    ),
)
def test_malformed_contracts_fail_stably(
    value: object,
    validator: object,
    projector: object,
    reason: str,
) -> None:
    assert validator(value)  # type: ignore[operator]
    with pytest.raises(ValueError, match=f"^{reason}$"):
        projector(value)  # type: ignore[operator]


def test_public_projection_has_no_tuple_or_dataclass() -> None:
    plain = profile.domain_evidence_projection_to_plain_dict_v01(
        _projection(
            kernel_artifact_refs=(_kernel_ref(),),
            causal_consumption_refs=(_causal_ref(),),
        )
    )
    assert not _contains_forbidden_projection_value(plain)
    canonical_json_bytes_v01(plain)


def test_projection_mutation_is_isolated() -> None:
    result = _projection()
    plain = profile.domain_evidence_projection_to_plain_dict_v01(result)
    plain["source_records"][0]["trace_refs"].append("changed")
    plain["evidence_refs"].append("changed")
    assert result.source_records[0].trace_refs == ("trace:source",)
    assert result.evidence_refs == ("evidence:fixture",)


def test_projection_leaves_source_contracts_unchanged() -> None:
    result = _projection()
    before = result
    profile.domain_evidence_projection_to_plain_dict_v01(result)
    assert result == before


def test_static_import_boundary_is_exact() -> None:
    source_path = Path(profile.__file__)
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
    assert set(imports) == {
        "dataclasses",
        "hashlib",
        "re",
        "unicodedata",
        "hedgehog.kernel.abi_v01",
        "hedgehog.kernel.integrity_replay_v01",
    }


@pytest.mark.parametrize(
    "forbidden",
    (
        "hedgehog.domains",
        "demo",
        "tests",
        "pathlib",
        "os",
        "stat",
        "tempfile",
        "subprocess",
        "datetime",
        "time",
        "random",
        "secrets",
        "uuid",
        "cryptography",
        "provider",
        "gemini",
        "config",
        "requests",
        "socket",
    ),
)
def test_static_forbidden_import_is_absent(forbidden: str) -> None:
    tree = ast.parse(Path(profile.__file__).read_text(encoding="utf-8"))
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
    assert all(name != forbidden and not name.startswith(f"{forbidden}.") for name in imported)


def test_static_no_package_anchor_or_replay_contract_exists() -> None:
    names = set(vars(profile))
    assert "SafeFileRecordV01" not in names
    assert "SealedPackageManifestV01" not in names
    assert "ExternalAnchorPublicationV01" not in names
    assert "AnchoredPackageVerificationV01" not in names
    assert "SealedReplayEvidenceV01" not in names


def test_static_no_effect_or_authority_operation_call() -> None:
    tree = ast.parse(Path(profile.__file__).read_text(encoding="utf-8"))
    called_names = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    forbidden_calls = {
        "open",
        "exec",
        "eval",
        "authorize_effect_request_v01",
        "execute_mock_effect_v01",
        "generate_root_signer_capability_v01",
        "build_root_decision_envelope_v01",
    }
    assert called_names.isdisjoint(forbidden_calls)


@pytest.mark.parametrize("name", PACKAGE_DATACLASS_NAMES)
def test_package_dataclass_field_order_is_exact(name: str) -> None:
    contract = getattr(sealed_package, name)
    assert is_dataclass(contract)
    assert tuple(field.name for field in fields(contract)) == PACKAGE_FIELD_NAMES[name]
    assert hasattr(contract, "__slots__")


@pytest.mark.parametrize("name", PACKAGE_DATACLASS_NAMES)
def test_package_dataclasses_are_frozen(name: str) -> None:
    _, files, _, manifest = _manifest_fixture()
    instances = {
        "SafeFileRecordV01": files[0],
        "SealedPackageManifestV01": manifest,
    }
    field_names = {
        "SafeFileRecordV01": "logical_path",
        "SealedPackageManifestV01": "package_status",
    }
    with pytest.raises(FrozenInstanceError):
        setattr(instances[name], field_names[name], "changed")


def test_package_module_public_functions_are_exact() -> None:
    expected = (
        "build_safe_file_record_v01",
        "validate_safe_file_record_v01",
        "safe_file_record_to_plain_dict_v01",
        "build_sealed_package_manifest_v01",
        "validate_sealed_package_manifest_v01",
        "sealed_package_manifest_to_plain_dict_v01",
    )
    actual = tuple(
        name
        for name, value in vars(sealed_package).items()
        if not name.startswith("_") and inspect.isfunction(value)
    )
    assert actual == expected
    assert set(actual) == set(SEALED_PACKAGE_PUBLIC_FUNCTION_NAMES)


def test_package_module_public_classes_are_exact() -> None:
    actual = tuple(
        name
        for name, value in vars(sealed_package).items()
        if not name.startswith("_") and inspect.isclass(value)
    )
    assert actual == PACKAGE_DATACLASS_NAMES


@pytest.mark.parametrize(
    ("name", "expected"),
    (
        ("MODULE_ID", "sealed_package_v01"),
        ("PACKAGE_VERSION", "v0.1"),
        ("MANIFEST_FILENAME", "sealed_package_manifest_v01.json"),
        ("STATUS_SELF_CONSISTENT_UNANCHORED", "SELF_CONSISTENT_UNANCHORED"),
        ("STATUS_FAIL_CLOSED", "FAIL_CLOSED"),
    ),
)
def test_package_constants_are_exact(name: str, expected: str) -> None:
    assert getattr(sealed_package, name) == expected


def test_package_status_vocabulary_is_exact_and_unanchored() -> None:
    assert sealed_package.PACKAGE_STATUSES == (
        "SELF_CONSISTENT_UNANCHORED",
        "FAIL_CLOSED",
    )
    assert type(sealed_package.PACKAGE_STATUSES) is tuple
    assert "PASS" not in sealed_package.PACKAGE_STATUSES
    assert "ANCHORED_PASS" not in sealed_package.PACKAGE_STATUSES


def test_package_namespace_annotations_are_absent() -> None:
    assert "annotations" not in vars(sealed_package)
    assert "annotations" not in vars(evidence)


@pytest.mark.parametrize(
    ("logical_path", "media_type", "content"),
    (
        ("evidence/runtime.json", "application/json", b'{"safe":true}\n'),
        ("evidence/story.md", "text/markdown", b"# Safe evidence\n"),
    ),
)
def test_safe_text_file_valid_cases(
    logical_path: str,
    media_type: str,
    content: bytes,
) -> None:
    source = _source()
    result = _safe_file(
        (source.source_record_id,),
        logical_path=logical_path,
        media_type=media_type,
        content=content,
    )
    assert not sealed_package.validate_safe_file_record_v01(
        result,
        content_bytes=content,
    )


@pytest.mark.parametrize("content", (b"\x00\xff\x01", b"\xff\xfe"))
def test_safe_binary_file_does_not_require_utf8(content: bytes) -> None:
    source = _source()
    result = _safe_file(
        (source.source_record_id,),
        logical_path="evidence/blob.bin",
        media_type="application/octet-stream",
        content=content,
        terminal_newline_required=False,
    )
    assert not sealed_package.validate_safe_file_record_v01(
        result,
        content_bytes=content,
    )


def test_safe_file_binds_multiple_source_records() -> None:
    first = _source()
    second = _source(source_id="source:second")
    source_ids = (first.source_record_id, second.source_record_id)
    result = _safe_file(source_ids)
    assert result.source_record_ids == source_ids
    assert result.source_record_ids is not source_ids


def test_safe_file_identity_and_content_derivations_are_deterministic() -> None:
    source = _source()
    content = b'{"safe":true}\n'
    first = _safe_file((source.source_record_id,), content=content)
    second = _safe_file((source.source_record_id,), content=content)
    assert first == second
    assert first.byte_count == len(content)
    assert first.content_sha256 == hashlib.sha256(content).hexdigest()
    assert first.file_record_id == second.file_record_id


def test_safe_file_retains_no_content_bytes() -> None:
    source = _source()
    result = _safe_file((source.source_record_id,), content=b"binary\x00payload", terminal_newline_required=False)
    assert all(type(getattr(result, slot)) is not bytes for slot in result.__slots__)


@pytest.mark.parametrize(
    "component",
    (
        "\u0414\u043e\u043a\u0430\u0437\u0430\u0442\u0435\u043b\u044c\u0441\u0442\u0432\u043e",
        "caf\u00e9",
        "\u8a3c\u62e0",
    ),
)
def test_safe_file_accepts_ordinary_unicode_path_components(component: str) -> None:
    source = _source()
    result = _safe_file(
        (source.source_record_id,),
        logical_path=f"evidence/{component}.json",
    )
    assert result.logical_path == f"evidence/{component}.json"


def test_safe_file_one_byte_context_mutation_is_rejected() -> None:
    source = _source()
    content = b'{"safe":true}\n'
    result = _safe_file((source.source_record_id,), content=content)
    changed = b'{"safe":false}\n'
    assert "sealed_package_hash_mismatch" in sealed_package.validate_safe_file_record_v01(
        result,
        content_bytes=changed,
    )
    with pytest.raises(ValueError, match="^safe_file_record_invalid$"):
        sealed_package.safe_file_record_to_plain_dict_v01(
            result,
            content_bytes=changed,
        )


def test_one_byte_rebuild_changes_file_and_package_identities() -> None:
    projection_item, kernel_hash = _package_projection()
    source_ids = (projection_item.source_records[0].source_record_id,)
    first_content = b'{"value":1}\n'
    second_content = b'{"value":2}\n'
    first_file = _safe_file(source_ids, content=first_content)
    second_file = _safe_file(source_ids, content=second_content)
    first_manifest = sealed_package.build_sealed_package_manifest_v01(
        domain_projection=projection_item,
        safe_file_records=(first_file,),
        safe_file_contents=(first_content,),
        kernel_manifest_hash=kernel_hash,
    )
    second_manifest = sealed_package.build_sealed_package_manifest_v01(
        domain_projection=projection_item,
        safe_file_records=(second_file,),
        safe_file_contents=(second_content,),
        kernel_manifest_hash=kernel_hash,
    )
    assert first_file.content_sha256 != second_file.content_sha256
    assert first_file.file_record_id != second_file.file_record_id
    assert first_manifest.package_content_hash != second_manifest.package_content_hash
    assert first_manifest.manifest_id != second_manifest.manifest_id


@pytest.mark.parametrize(
    ("field", "value", "reason"),
    (
        ("byte_count", 999, "sealed_package_hash_mismatch"),
        ("content_sha256", "0" * 64, "sealed_package_hash_mismatch"),
        ("file_record_id", "0" * 64, "sealed_package_identity_mismatch"),
    ),
)
def test_safe_file_stale_fields_are_rejected(
    field: str,
    value: object,
    reason: str,
) -> None:
    source = _source()
    content = b'{"safe":true}\n'
    forged = replace(_safe_file((source.source_record_id,), content=content), **{field: value})
    assert reason in sealed_package.validate_safe_file_record_v01(
        forged,
        content_bytes=content,
    )


@pytest.mark.parametrize(
    ("field", "value"),
    (("byte_count", 999), ("content_sha256", "0" * 64)),
)
def test_self_rehashed_stale_safe_file_fields_are_rejected(
    field: str,
    value: object,
) -> None:
    source = _source()
    content = b'{"safe":true}\n'
    forged = replace(_safe_file((source.source_record_id,), content=content), **{field: value})
    forged = _rehash_file(forged)
    assert "sealed_package_hash_mismatch" in sealed_package.validate_safe_file_record_v01(
        forged,
        content_bytes=content,
    )


@pytest.mark.parametrize("value", (True, False, 1.0, 0.0))
def test_safe_file_byte_count_requires_exact_int(value: object) -> None:
    source = _source()
    content = b"x"
    valid = _safe_file(
        (source.source_record_id,),
        content=content,
        terminal_newline_required=False,
    )
    forged = _rehash_file(replace(valid, byte_count=value))  # type: ignore[arg-type]
    assert sealed_package.validate_safe_file_record_v01(
        forged,
        content_bytes=content,
    )


@pytest.mark.parametrize("content", (bytearray(b"x"), memoryview(b"x"), [120], b""))
def test_safe_file_requires_exact_nonempty_bytes(content: object) -> None:
    source = _source()
    with pytest.raises(ValueError, match="^safe_file_record_invalid$"):
        _safe_file((source.source_record_id,), content=content)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "media_type",
    (
        "",
        "Application/json",
        "application/JSON",
        "application/json; charset=utf-8",
        "application",
        "/json",
        "application/",
        "application /json",
        " application/json",
        "application/json ",
    ),
)
def test_safe_file_invalid_media_types_are_rejected(media_type: str) -> None:
    with pytest.raises(ValueError):
        _safe_file((_source().source_record_id,), media_type=media_type)


def test_safe_file_raw_private_evidence_is_rejected() -> None:
    with pytest.raises(ValueError, match="^sealed_package_raw_material_forbidden$"):
        _safe_file(
            (_source().source_record_id,),
            evidence_class="LIVE_PROVIDER_RAW_PRIVATE",
        )


def test_safe_file_failed_secret_scan_is_rejected() -> None:
    with pytest.raises(ValueError, match="^sealed_package_secret_scan_required$"):
        _safe_file((_source().source_record_id,), secret_scan_passed=False)


def test_safe_file_duplicate_source_ids_are_rejected() -> None:
    source_id = _source().source_record_id
    with pytest.raises(ValueError, match="^sealed_package_duplicate_identity$"):
        _safe_file((source_id, source_id))


@pytest.mark.parametrize("source_id", ("", "a" * 63, "A" * 64, "g" * 64))
def test_safe_file_malformed_source_ids_are_rejected(source_id: str) -> None:
    with pytest.raises(ValueError, match="^safe_file_record_invalid$"):
        _safe_file((source_id,))


def test_safe_file_source_ids_require_exact_tuple() -> None:
    with pytest.raises(ValueError, match="^safe_file_record_invalid$"):
        _safe_file([_source().source_record_id])  # type: ignore[arg-type]


@pytest.mark.parametrize("field", ("terminal_newline_required", "secret_scan_passed"))
def test_safe_file_flags_require_exact_bool(field: str) -> None:
    kwargs = {"terminal_newline_required": True, "secret_scan_passed": True}
    kwargs[field] = 1
    with pytest.raises(ValueError):
        _safe_file((_source().source_record_id,), **kwargs)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "logical_path",
    (
        "/absolute/file.json",
        "C:/absolute/file.json",
        "C:\\absolute\\file.json",
        "../parent/file.json",
        "evidence/../file.json",
        "./evidence/file.json",
        "evidence/./file.json",
        "evidence//file.json",
        "evidence/",
        " evidence/file.json",
        "evidence/file.json ",
        "evidence/nul\x00file.json",
        "evidence/surrogate\ud800.json",
        "evidence/cafe\u0301.json",
    ),
)
def test_safe_file_logical_path_attacks_are_rejected(logical_path: str) -> None:
    with pytest.raises(ValueError, match="^safe_file_record_invalid$"):
        _safe_file((_source().source_record_id,), logical_path=logical_path)


@pytest.mark.parametrize("code_point", (0x202E, 0x200B, 0xFEFF, 0x2028, 0x2029))
def test_safe_file_unicode_format_path_attacks_are_rejected(code_point: int) -> None:
    logical_path = f"evidence/safe{chr(code_point)}file.json"
    with pytest.raises(ValueError, match="^safe_file_record_invalid$"):
        _safe_file((_source().source_record_id,), logical_path=logical_path)


def test_terminal_newline_exact_one_lf_is_accepted() -> None:
    content = b"safe\n"
    result = _safe_file((_source().source_record_id,), content=content)
    assert not sealed_package.validate_safe_file_record_v01(result, content_bytes=content)


@pytest.mark.parametrize(
    "content",
    (b"safe", b"safe\n\n", b"safe\r\n", b"\xff\n", b"safe\x00\n"),
)
def test_terminal_newline_invalid_content_is_rejected(content: bytes) -> None:
    with pytest.raises(ValueError, match="^safe_file_record_invalid$"):
        _safe_file((_source().source_record_id,), content=content)


@pytest.mark.parametrize("content", (b"safe", b"safe\n\n", b"safe\r\n", b"\xff\x00"))
def test_binary_members_ignore_text_newline_law(content: bytes) -> None:
    result = _safe_file(
        (_source().source_record_id,),
        content=content,
        terminal_newline_required=False,
    )
    assert not sealed_package.validate_safe_file_record_v01(result, content_bytes=content)


@pytest.mark.parametrize(
    ("call_count", "domain_id", "expected_source_count"),
    ((0, "airline", 0), (12, "airline", 12), (6, "supplier_water_filter", 6)),
)
def test_valid_manifest_geometries(
    call_count: int,
    domain_id: str,
    expected_source_count: int,
) -> None:
    projection_item, files, contents, manifest = _manifest_fixture(
        call_count=call_count,
        domain_id=domain_id,
    )
    assert not sealed_package.validate_sealed_package_manifest_v01(
        manifest,
        domain_projection=projection_item,
        safe_file_contents=contents,
    )
    assert manifest.package_status == "SELF_CONSISTENT_UNANCHORED"
    assert (
        projection_item.source_provider_call_count,
        projection_item.source_network_call_count,
        projection_item.source_gemini_call_count,
    ) == (expected_source_count,) * 3
    assert (
        manifest.packaging_provider_call_count,
        manifest.packaging_network_call_count,
        manifest.packaging_gemini_call_count,
    ) == (0, 0, 0)
    assert manifest.file_count == len(files)


def test_manifest_identity_bindings_and_counts_are_exact() -> None:
    projection_item, files, _, manifest = _manifest_fixture()
    assert manifest.manifest_version == "v0.1"
    assert manifest.domain_projection_id == projection_item.projection_id
    assert manifest.programme_identity_id == projection_item.programme_identity.programme_identity_id
    assert manifest.domain_execution_identity_id == projection_item.domain_execution_identity.domain_execution_identity_id
    assert manifest.attempt_identity_id == projection_item.attempt_identity.attempt_identity_id
    assert manifest.domain_id == projection_item.domain_execution_identity.domain_id
    assert manifest.package_id == projection_item.attempt_identity.package_id
    assert manifest.logical_package_ref == projection_item.attempt_identity.logical_package_ref
    assert manifest.artifact_record_ids == tuple(
        item.artifact_record_id for item in projection_item.artifact_records
    )
    assert manifest.file_count == len(files)
    assert manifest.artifact_count == len(projection_item.artifact_records)


def test_manifest_hashes_and_identity_are_deterministic() -> None:
    first = _manifest_fixture()[3]
    second = _manifest_fixture()[3]
    assert first.package_content_hash == second.package_content_hash
    assert first.manifest_id == second.manifest_id
    assert first == second


def test_manifest_kernel_hash_is_grounded() -> None:
    projection_item, _, _, manifest = _manifest_fixture()
    assert any(
        item.evidence_class == "CRYPTOGRAPHIC_INTEGRITY"
        and manifest.kernel_manifest_hash in item.trace_refs
        for item in projection_item.source_records
    )


def test_coherent_fail_closed_manifest_is_valid_and_projectable() -> None:
    projection_item, _, contents, manifest = _manifest_fixture(fail_closed=True)
    assert projection_item.status == "FAIL_CLOSED"
    assert manifest.package_status == "FAIL_CLOSED"
    assert not sealed_package.validate_sealed_package_manifest_v01(
        manifest,
        domain_projection=projection_item,
        safe_file_contents=contents,
    )
    plain = sealed_package.sealed_package_manifest_to_plain_dict_v01(
        manifest,
        domain_projection=projection_item,
        safe_file_contents=contents,
    )
    assert plain["package_status"] == "FAIL_CLOSED"


def test_complete_multi_source_coverage_is_accepted() -> None:
    projection_item, _, contents, manifest = _manifest_fixture(extra_source=True)
    assert len(projection_item.source_records) == 2
    assert not sealed_package.validate_sealed_package_manifest_v01(
        manifest,
        domain_projection=projection_item,
        safe_file_contents=contents,
    )


def test_canonical_utf8_file_order_is_accepted() -> None:
    projection_item, files, contents, manifest = _two_file_manifest_fixture()
    assert tuple(item.logical_path for item in files) == tuple(
        sorted(item.logical_path for item in files)
    )
    assert not sealed_package.validate_sealed_package_manifest_v01(
        manifest,
        domain_projection=projection_item,
        safe_file_contents=contents,
    )


def test_reversed_file_order_is_rejected_by_builder() -> None:
    projection_item, files, contents, manifest = _two_file_manifest_fixture()
    with pytest.raises(ValueError, match="^sealed_package_order_invalid$"):
        sealed_package.build_sealed_package_manifest_v01(
            domain_projection=projection_item,
            safe_file_records=tuple(reversed(files)),
            safe_file_contents=tuple(reversed(contents)),
            kernel_manifest_hash=manifest.kernel_manifest_hash,
        )


def test_reordered_self_rehashed_manifest_is_rejected() -> None:
    projection_item, files, contents, manifest = _two_file_manifest_fixture()
    reordered_files = tuple(reversed(files))
    forged = replace(
        manifest,
        safe_file_records=reordered_files,
        package_content_hash=sealed_package._package_content_hash(reordered_files),
    )
    forged = _rehash_manifest(forged)
    errors = sealed_package.validate_sealed_package_manifest_v01(
        forged,
        domain_projection=projection_item,
        safe_file_contents=tuple(reversed(contents)),
    )
    assert "sealed_package_order_invalid" in errors


def test_duplicate_file_identity_is_rejected() -> None:
    projection_item, files, contents, manifest = _two_file_manifest_fixture()
    duplicate = replace(files[1], file_record_id=files[0].file_record_id)
    forged_files = (files[0], duplicate)
    forged = replace(manifest, safe_file_records=forged_files)
    forged = _rehash_manifest(forged)
    assert "sealed_package_duplicate_identity" in sealed_package.validate_sealed_package_manifest_v01(
        forged,
        domain_projection=projection_item,
        safe_file_contents=contents,
    )


def test_duplicate_exact_path_is_rejected() -> None:
    projection_item, files, contents, manifest = _two_file_manifest_fixture()
    duplicate_path = _rehash_file(replace(files[1], logical_path=files[0].logical_path))
    forged_files = (files[0], duplicate_path)
    forged = replace(
        manifest,
        safe_file_records=forged_files,
        package_content_hash=sealed_package._package_content_hash(forged_files),
    )
    forged = _rehash_manifest(forged)
    assert "sealed_package_duplicate_identity" in sealed_package.validate_sealed_package_manifest_v01(
        forged,
        domain_projection=projection_item,
        safe_file_contents=contents,
    )


def test_casefold_path_collision_is_rejected() -> None:
    projection_item, files, contents, manifest = _two_file_manifest_fixture()
    first = _rehash_file(replace(files[0], logical_path="evidence/Case.txt"))
    second = _rehash_file(replace(files[1], logical_path="evidence/case.txt"))
    forged_files = (first, second)
    forged = replace(
        manifest,
        safe_file_records=forged_files,
        package_content_hash=sealed_package._package_content_hash(forged_files),
    )
    forged = _rehash_manifest(forged)
    assert "sealed_package_duplicate_identity" in sealed_package.validate_sealed_package_manifest_v01(
        forged,
        domain_projection=projection_item,
        safe_file_contents=contents,
    )


def test_unicode_normalized_path_collision_is_rejected() -> None:
    projection_item, files, contents, manifest = _two_file_manifest_fixture()
    first = _rehash_file(replace(files[0], logical_path="evidence/caf\u00e9.txt"))
    second = _rehash_file(replace(files[1], logical_path="evidence/cafe\u0301.txt"))
    forged_files = (first, second)
    forged = replace(
        manifest,
        safe_file_records=forged_files,
        package_content_hash=sealed_package._package_content_hash(forged_files),
    )
    forged = _rehash_manifest(forged)
    assert "sealed_package_duplicate_identity" in sealed_package.validate_sealed_package_manifest_v01(
        forged,
        domain_projection=projection_item,
        safe_file_contents=contents,
    )


@pytest.mark.parametrize(
    "reserved_path",
    ("sealed_package_manifest_v01.json", "Sealed_Package_Manifest_V01.JSON"),
)
def test_safe_file_builder_rejects_manifest_self_reference(
    reserved_path: str,
) -> None:
    with pytest.raises(
        ValueError,
        match="^sealed_package_manifest_self_reference_forbidden$",
    ):
        _safe_file((_source().source_record_id,), logical_path=reserved_path)


@pytest.mark.parametrize(
    "reserved_path",
    ("sealed_package_manifest_v01.json", "Sealed_Package_Manifest_V01.JSON"),
)
def test_safe_file_validator_rejects_rehashed_manifest_self_reference(
    reserved_path: str,
) -> None:
    content = b"{}\n"
    valid = _safe_file((_source().source_record_id,), content=content)
    forged = _rehash_file(replace(valid, logical_path=reserved_path))
    errors = sealed_package.validate_safe_file_record_v01(
        forged,
        content_bytes=content,
    )
    assert "sealed_package_manifest_self_reference_forbidden" in errors
    with pytest.raises(ValueError, match="^safe_file_record_invalid$"):
        sealed_package.safe_file_record_to_plain_dict_v01(
            forged,
            content_bytes=content,
        )


def test_safe_file_allows_unrelated_manifest_named_path() -> None:
    result = _safe_file(
        (_source().source_record_id,),
        logical_path="evidence/sealed_package_manifest_notes.json",
    )
    assert result.logical_path == "evidence/sealed_package_manifest_notes.json"


@pytest.mark.parametrize(
    "reserved_path",
    ("sealed_package_manifest_v01.json", "Sealed_Package_Manifest_V01.JSON"),
)
def test_manifest_self_reference_is_rejected(reserved_path: str) -> None:
    projection_item, kernel_hash = _package_projection()
    content = b"{}\n"
    valid_file = _safe_file(
        (projection_item.source_records[0].source_record_id,),
        logical_path="evidence/runtime.json",
        content=content,
    )
    file_record = _rehash_file(replace(valid_file, logical_path=reserved_path))
    with pytest.raises(
        ValueError,
        match="^sealed_package_manifest_self_reference_forbidden$",
    ):
        sealed_package.build_sealed_package_manifest_v01(
            domain_projection=projection_item,
            safe_file_records=(file_record,),
            safe_file_contents=(content,),
            kernel_manifest_hash=kernel_hash,
        )


def test_unresolved_file_source_reference_is_rejected() -> None:
    projection_item, kernel_hash = _package_projection()
    content = b"{}\n"
    file_record = _safe_file(("f" * 64,), content=content)
    with pytest.raises(ValueError, match="^sealed_package_reference_unresolved$"):
        sealed_package.build_sealed_package_manifest_v01(
            domain_projection=projection_item,
            safe_file_records=(file_record,),
            safe_file_contents=(content,),
            kernel_manifest_hash=kernel_hash,
        )


def test_partial_source_coverage_is_rejected() -> None:
    projection_item, kernel_hash = _package_projection(extra_source=True)
    content = b"{}\n"
    file_record = _safe_file(
        (projection_item.source_records[0].source_record_id,),
        content=content,
    )
    with pytest.raises(ValueError, match="^sealed_package_reference_unresolved$"):
        sealed_package.build_sealed_package_manifest_v01(
            domain_projection=projection_item,
            safe_file_records=(file_record,),
            safe_file_contents=(content,),
            kernel_manifest_hash=kernel_hash,
        )


@pytest.mark.parametrize("mode", ("removed", "reordered", "added"))
def test_manifest_artifact_binding_attacks_are_rejected(mode: str) -> None:
    projection_item, _, contents, manifest = _manifest_fixture()
    if mode == "removed":
        artifact_ids = manifest.artifact_record_ids[:-1]
    elif mode == "reordered":
        artifact_ids = tuple(reversed(manifest.artifact_record_ids))
    else:
        artifact_ids = manifest.artifact_record_ids + ("f" * 64,)
    forged = _rehash_manifest(replace(manifest, artifact_record_ids=artifact_ids))
    assert sealed_package.validate_sealed_package_manifest_v01(
        forged,
        domain_projection=projection_item,
        safe_file_contents=contents,
    )


def test_ungrounded_kernel_manifest_hash_is_rejected() -> None:
    projection_item, files, contents, _ = _manifest_fixture()
    with pytest.raises(ValueError, match="^sealed_package_reference_unresolved$"):
        sealed_package.build_sealed_package_manifest_v01(
            domain_projection=projection_item,
            safe_file_records=files,
            safe_file_contents=contents,
            kernel_manifest_hash="f" * 64,
        )


def test_matching_noncryptographic_artifact_hash_is_rejected() -> None:
    source = _source(trace_refs=("trace:source", "f" * 64))
    artifact = _artifact(source, canonical_projection={"manifest": "not_crypto"})
    projection_item = _projection(
        source_records=(source,),
        artifact_records=(artifact,),
    )
    content = b"{}\n"
    file_record = _safe_file((source.source_record_id,), content=content)
    with pytest.raises(ValueError, match="^sealed_package_reference_unresolved$"):
        sealed_package.build_sealed_package_manifest_v01(
            domain_projection=projection_item,
            safe_file_records=(file_record,),
            safe_file_contents=(content,),
            kernel_manifest_hash="f" * 64,
        )


def test_matching_cryptographic_artifact_hash_is_accepted() -> None:
    projection_item, _, contents, manifest = _manifest_fixture()
    assert not sealed_package.validate_sealed_package_manifest_v01(
        manifest,
        domain_projection=projection_item,
        safe_file_contents=contents,
    )


def test_kernel_manifest_grounding_requires_present_source_trace() -> None:
    source = _source(evidence_class="CRYPTOGRAPHIC_INTEGRITY")
    assert not sealed_package._kernel_manifest_hash_grounded((source,), "e" * 64)


def test_kernel_manifest_grounding_rejects_wrong_source_trace_hash() -> None:
    source = _source(
        evidence_class="CRYPTOGRAPHIC_INTEGRITY",
        trace_refs=("trace:kernel_manifest", "d" * 64),
    )
    assert not sealed_package._kernel_manifest_hash_grounded((source,), "e" * 64)


def test_kernel_manifest_grounding_rejects_noncryptographic_source() -> None:
    source = _source(trace_refs=("trace:kernel_manifest", "e" * 64))
    assert not sealed_package._kernel_manifest_hash_grounded((source,), "e" * 64)


def test_kernel_manifest_grounding_rejects_stale_source_identity() -> None:
    source = _source(
        evidence_class="CRYPTOGRAPHIC_INTEGRITY",
        trace_refs=("trace:kernel_manifest", "e" * 64),
    )
    stale = replace(source, source_id="source:changed")
    assert not sealed_package._kernel_manifest_hash_grounded((stale,), "e" * 64)


def test_kernel_manifest_grounding_rejects_raw_private_source() -> None:
    source = _source(
        evidence_class="LIVE_PROVIDER_RAW_PRIVATE",
        trace_refs=("trace:kernel_manifest", "e" * 64),
    )
    assert not sealed_package._kernel_manifest_hash_grounded((source,), "e" * 64)


def test_kernel_manifest_grounding_rejects_failed_secret_scan() -> None:
    source = _source(
        evidence_class="CRYPTOGRAPHIC_INTEGRITY",
        trace_refs=("trace:kernel_manifest", "e" * 64),
        secret_scan_passed=False,
    )
    assert not sealed_package._kernel_manifest_hash_grounded((source,), "e" * 64)


def test_kernel_manifest_grounding_rejects_self_rehashed_false_claim() -> None:
    source = _source(
        evidence_class="CRYPTOGRAPHIC_INTEGRITY",
        trace_refs=("trace:kernel_manifest", "e" * 64),
    )
    false_claim = _rehash_source(
        replace(source, evidence_class="EXECUTED_DETERMINISTIC_RUNTIME")
    )
    assert not profile.validate_safe_source_record_v01(false_claim)
    assert not sealed_package._kernel_manifest_hash_grounded(
        (false_claim,),
        "e" * 64,
    )


def test_changed_file_content_rejects_stored_manifest() -> None:
    projection_item, _, _, manifest = _manifest_fixture()
    errors = sealed_package.validate_sealed_package_manifest_v01(
        manifest,
        domain_projection=projection_item,
        safe_file_contents=(b'{"status":"changed"}\n',),
    )
    assert "sealed_package_hash_mismatch" in errors


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("package_content_hash", "0" * 64),
        ("package_id", "package:changed"),
        ("logical_package_ref", "changed/package"),
        ("domain_id", "changed_domain"),
        ("domain_projection_id", "0" * 64),
        ("attempt_identity_id", "0" * 64),
    ),
)
def test_manifest_semantic_binding_attacks_are_rejected(
    field: str,
    value: object,
) -> None:
    projection_item, _, contents, manifest = _manifest_fixture()
    forged = _rehash_manifest(replace(manifest, **{field: value}))
    assert sealed_package.validate_sealed_package_manifest_v01(
        forged,
        domain_projection=projection_item,
        safe_file_contents=contents,
    )


def test_self_consistent_status_forgery_is_rejected() -> None:
    projection_item, _, contents, manifest = _manifest_fixture(fail_closed=True)
    forged = _rehash_manifest(
        replace(manifest, package_status="SELF_CONSISTENT_UNANCHORED")
    )
    assert "sealed_package_status_mismatch" in sealed_package.validate_sealed_package_manifest_v01(
        forged,
        domain_projection=projection_item,
        safe_file_contents=contents,
    )


def test_fail_closed_status_forgery_is_rejected() -> None:
    projection_item, _, contents, manifest = _manifest_fixture()
    forged = _rehash_manifest(replace(manifest, package_status="FAIL_CLOSED"))
    assert "sealed_package_status_mismatch" in sealed_package.validate_sealed_package_manifest_v01(
        forged,
        domain_projection=projection_item,
        safe_file_contents=contents,
    )


def test_self_rehashed_contradictory_manifest_count_is_rejected() -> None:
    projection_item, _, contents, manifest = _manifest_fixture()
    forged = _rehash_manifest(replace(manifest, file_count=manifest.file_count + 1))
    assert "sealed_package_manifest_invalid" in sealed_package.validate_sealed_package_manifest_v01(
        forged,
        domain_projection=projection_item,
        safe_file_contents=contents,
    )


@pytest.mark.parametrize(
    "field",
    (
        "file_count",
        "artifact_count",
        "packaging_provider_call_count",
        "packaging_network_call_count",
        "packaging_gemini_call_count",
        "created_authority_count",
        "created_permission_count",
        "real_world_effects_count",
    ),
)
@pytest.mark.parametrize("value", (True, False, 1.0, 0.0))
def test_manifest_counters_require_exact_int(field: str, value: object) -> None:
    projection_item, _, contents, manifest = _manifest_fixture()
    forged = _rehash_manifest(replace(manifest, **{field: value}))
    errors = sealed_package.validate_sealed_package_manifest_v01(
        forged,
        domain_projection=projection_item,
        safe_file_contents=contents,
    )
    assert errors
    with pytest.raises(ValueError, match="^sealed_package_manifest_invalid$"):
        sealed_package.sealed_package_manifest_to_plain_dict_v01(
            forged,
            domain_projection=projection_item,
            safe_file_contents=contents,
        )


@pytest.mark.parametrize(
    ("field", "reason"),
    (
        ("packaging_provider_call_count", "sealed_package_external_call_forbidden"),
        ("packaging_network_call_count", "sealed_package_external_call_forbidden"),
        ("packaging_gemini_call_count", "sealed_package_external_call_forbidden"),
        ("created_authority_count", "sealed_package_authority_creation_forbidden"),
        ("created_permission_count", "sealed_package_permission_creation_forbidden"),
        ("real_world_effects_count", "sealed_package_effect_forbidden"),
    ),
)
def test_manifest_zero_operation_counters_cannot_be_forged(
    field: str,
    reason: str,
) -> None:
    projection_item, _, contents, manifest = _manifest_fixture()
    forged = _rehash_manifest(replace(manifest, **{field: 1}))
    assert reason in sealed_package.validate_sealed_package_manifest_v01(
        forged,
        domain_projection=projection_item,
        safe_file_contents=contents,
    )


def test_safe_file_public_projection_is_json_safe_and_isolated() -> None:
    source = _source()
    content = b'{"safe":true}\n'
    result = _safe_file((source.source_record_id,), content=content)
    plain = sealed_package.safe_file_record_to_plain_dict_v01(
        result,
        content_bytes=content,
    )
    assert not _contains_forbidden_projection_value(plain)
    canonical_json_bytes_v01(plain)
    plain["source_record_ids"].append("changed")
    assert result.source_record_ids == (source.source_record_id,)
    assert "content_bytes" not in plain


def test_manifest_public_projection_is_json_safe_and_isolated() -> None:
    projection_item, _, contents, manifest = _manifest_fixture()
    before = manifest
    plain = sealed_package.sealed_package_manifest_to_plain_dict_v01(
        manifest,
        domain_projection=projection_item,
        safe_file_contents=contents,
    )
    assert not _contains_forbidden_projection_value(plain)
    canonical_json_bytes_v01(plain)
    plain["safe_file_records"][0]["source_record_ids"].append("changed")
    plain["artifact_record_ids"].append("changed")
    assert manifest == before
    assert "content_bytes" not in json.dumps(plain)


@pytest.mark.parametrize(
    ("validator", "projector", "kwargs", "reason"),
    (
        (
            sealed_package.validate_safe_file_record_v01,
            sealed_package.safe_file_record_to_plain_dict_v01,
            {"content_bytes": b"x"},
            "safe_file_record_invalid",
        ),
        (
            sealed_package.validate_sealed_package_manifest_v01,
            sealed_package.sealed_package_manifest_to_plain_dict_v01,
            {"domain_projection": object(), "safe_file_contents": ()},
            "sealed_package_manifest_invalid",
        ),
    ),
)
def test_malformed_package_contracts_fail_stably(
    validator: object,
    projector: object,
    kwargs: dict[str, object],
    reason: str,
) -> None:
    assert validator(object(), **kwargs)  # type: ignore[operator]
    with pytest.raises(ValueError, match=f"^{reason}$"):
        projector(object(), **kwargs)  # type: ignore[operator]


def test_package_builders_do_not_accept_derived_fields() -> None:
    file_signature = inspect.signature(sealed_package.build_safe_file_record_v01)
    assert {"file_record_id", "byte_count", "content_sha256"}.isdisjoint(
        file_signature.parameters
    )
    manifest_signature = inspect.signature(
        sealed_package.build_sealed_package_manifest_v01
    )
    forbidden = {
        "manifest_id",
        "manifest_version",
        "package_status",
        "package_content_hash",
        "file_count",
        "artifact_count",
        "packaging_provider_call_count",
        "created_authority_count",
        "created_permission_count",
        "real_world_effects_count",
    }
    assert forbidden.isdisjoint(manifest_signature.parameters)


def test_package_static_import_boundary_is_exact() -> None:
    tree = ast.parse(Path(sealed_package.__file__).read_text(encoding="utf-8"))
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
    assert set(imports) == {
        "dataclasses",
        "hashlib",
        "re",
        "unicodedata",
        "hedgehog.evidence.sealed_evidence_profile_v01",
        "hedgehog.kernel.integrity_replay_v01",
    }


@pytest.mark.parametrize(
    "forbidden",
    (
        "hedgehog.domains",
        "demo",
        "tests",
        "pathlib",
        "os",
        "stat",
        "tempfile",
        "zipfile",
        "tarfile",
        "shutil",
        "subprocess",
        "datetime",
        "time",
        "random",
        "secrets",
        "uuid",
        "cryptography",
        "provider",
        "gemini",
        "config",
        "requests",
        "socket",
    ),
)
def test_package_static_forbidden_import_is_absent(forbidden: str) -> None:
    tree = ast.parse(Path(sealed_package.__file__).read_text(encoding="utf-8"))
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
    assert all(
        name != forbidden and not name.startswith(f"{forbidden}.")
        for name in imported
    )


def test_package_static_has_no_filesystem_or_effect_calls() -> None:
    tree = ast.parse(Path(sealed_package.__file__).read_text(encoding="utf-8"))
    called_names = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    forbidden_calls = {
        "open",
        "mkdir",
        "makedirs",
        "read_bytes",
        "read_text",
        "write_bytes",
        "write_text",
        "glob",
        "rglob",
        "authorize_effect_request_v01",
        "execute_mock_effect_v01",
        "generate_root_signer_capability_v01",
    }
    assert called_names.isdisjoint(forbidden_calls)


def test_package_static_has_no_anchor_or_replay_contract() -> None:
    names = set(vars(sealed_package))
    assert "ExternalAnchorPublicationV01" not in names
    assert "AnchoredPackageVerificationV01" not in names
    assert "SealedReplayEvidenceV01" not in names


@pytest.mark.parametrize("name", ANCHOR_DATACLASS_NAMES)
def test_anchor_dataclass_field_order_is_exact(name: str) -> None:
    contract = getattr(external_anchor, name)
    assert is_dataclass(contract)
    assert tuple(field.name for field in fields(contract)) == ANCHOR_FIELD_NAMES[name]
    assert hasattr(contract, "__slots__")


@pytest.mark.parametrize("name", ANCHOR_DATACLASS_NAMES)
def test_anchor_dataclasses_are_frozen(name: str) -> None:
    _, _, _, publication, verification = _verification_fixture()
    instances = {
        "ExternalAnchorPublicationV01": publication,
        "AnchoredPackageVerificationV01": verification,
    }
    field_names = {
        "ExternalAnchorPublicationV01": "anchor_status",
        "AnchoredPackageVerificationV01": "verification_status",
    }
    with pytest.raises(FrozenInstanceError):
        setattr(instances[name], field_names[name], "changed")


def test_anchor_module_public_functions_are_exact() -> None:
    expected = (
        "build_external_anchor_publication_v01",
        "validate_external_anchor_publication_v01",
        "external_anchor_publication_to_plain_dict_v01",
        "build_anchored_package_verification_v01",
        "validate_anchored_package_verification_v01",
        "anchored_package_verification_to_plain_dict_v01",
    )
    actual = tuple(
        name
        for name, value in vars(external_anchor).items()
        if not name.startswith("_") and inspect.isfunction(value)
    )
    assert actual == expected
    assert set(actual) == set(ANCHOR_PUBLIC_FUNCTION_NAMES)


def test_anchor_module_public_classes_are_exact() -> None:
    actual = tuple(
        name
        for name, value in vars(external_anchor).items()
        if not name.startswith("_") and inspect.isclass(value)
    )
    assert actual == ANCHOR_DATACLASS_NAMES


@pytest.mark.parametrize(
    ("name", "expected"),
    (
        ("MODULE_ID", "external_anchor_v01"),
        ("ANCHOR_VERSION", "v0.1"),
        ("VERIFICATION_VERSION", "v0.1"),
        ("STATUS_EVIDENCE_ONLY", "EVIDENCE_ONLY"),
        ("STATUS_ANCHORED_PASS", "ANCHORED_PASS"),
        ("STATUS_FAIL_CLOSED", "FAIL_CLOSED"),
    ),
)
def test_anchor_constants_are_exact(name: str, expected: str) -> None:
    assert getattr(external_anchor, name) == expected


def test_anchor_status_vocabularies_are_exact() -> None:
    assert external_anchor.ANCHOR_PUBLICATION_STATUSES == (
        "EVIDENCE_ONLY",
        "FAIL_CLOSED",
    )
    assert external_anchor.ANCHORED_VERIFICATION_STATUSES == (
        "ANCHORED_PASS",
        "FAIL_CLOSED",
    )
    assert type(external_anchor.ANCHOR_PUBLICATION_STATUSES) is tuple
    assert type(external_anchor.ANCHORED_VERIFICATION_STATUSES) is tuple
    assert "ANCHORED_PASS" not in external_anchor.ANCHOR_PUBLICATION_STATUSES
    assert "PASS" not in external_anchor.ANCHORED_VERIFICATION_STATUSES
    assert all("SIGNATURE" not in item for item in external_anchor.ANCHORED_VERIFICATION_STATUSES)


def test_anchor_namespace_annotations_are_absent() -> None:
    assert "annotations" not in vars(external_anchor)
    assert "annotations" not in vars(evidence)


@pytest.mark.parametrize(
    ("call_count", "domain_id", "expected_source_count"),
    ((0, "airline", 0), (12, "airline", 12), (6, "supplier_water_filter", 6)),
)
def test_valid_anchor_publication_geometries(
    call_count: int,
    domain_id: str,
    expected_source_count: int,
) -> None:
    projection_item, contents, manifest, publication = _anchor_fixture(
        call_count=call_count,
        domain_id=domain_id,
    )
    assert not external_anchor.validate_external_anchor_publication_v01(
        publication,
        manifest=manifest,
        domain_projection=projection_item,
        safe_file_contents=contents,
    )
    assert publication.anchor_status == "EVIDENCE_ONLY"
    assert (
        publication.publication_provider_call_count,
        publication.publication_network_call_count,
        publication.publication_gemini_call_count,
    ) == (0, 0, 0)
    assert projection_item.source_provider_call_count == expected_source_count


def test_anchor_publication_bindings_are_exact() -> None:
    projection_item, _, manifest, publication = _anchor_fixture()
    assert publication.anchor_version == "v0.1"
    assert publication.manifest_id == manifest.manifest_id
    assert publication.domain_projection_id == manifest.domain_projection_id
    assert publication.programme_identity_id == manifest.programme_identity_id
    assert publication.domain_execution_identity_id == manifest.domain_execution_identity_id
    assert publication.attempt_identity_id == manifest.attempt_identity_id
    assert publication.domain_id == manifest.domain_id
    assert publication.package_id == manifest.package_id
    assert publication.logical_package_ref == manifest.logical_package_ref
    assert publication.package_content_hash == manifest.package_content_hash
    assert publication.kernel_manifest_hash == manifest.kernel_manifest_hash
    assert publication.publication_base_head == projection_item.domain_execution_identity.execution_head


def test_anchor_publication_nonclaim_booleans_are_false() -> None:
    publication = _anchor_fixture()[3]
    assert publication.external_anchor_supplied_at_publication is False
    assert publication.external_anchor_verified_at_publication is False
    assert publication.anchored_pass_claimed is False
    assert publication.anchor_status != "ANCHORED_PASS"


def test_anchor_publication_identity_is_deterministic() -> None:
    first = _anchor_fixture()[3]
    second = _anchor_fixture()[3]
    assert first == second
    assert first.anchor_publication_id == second.anchor_publication_id


def test_coherent_fail_closed_anchor_publication_is_projectable() -> None:
    projection_item, contents, manifest, publication = _anchor_fixture(
        fail_closed=True
    )
    assert manifest.package_status == "FAIL_CLOSED"
    assert publication.anchor_status == "FAIL_CLOSED"
    assert not external_anchor.validate_external_anchor_publication_v01(
        publication,
        manifest=manifest,
        domain_projection=projection_item,
        safe_file_contents=contents,
    )
    plain = external_anchor.external_anchor_publication_to_plain_dict_v01(
        publication,
        manifest=manifest,
        domain_projection=projection_item,
        safe_file_contents=contents,
    )
    assert plain["anchor_status"] == "FAIL_CLOSED"


@pytest.mark.parametrize(
    "publication_base_head",
    ("B1096C2", "abcdef", "a" * 41, "g1096c2", " b1096c2", "b1096c2 ", True, b"b1096c2"),
)
def test_publication_base_head_attacks_are_rejected(
    publication_base_head: object,
) -> None:
    projection_item, _, contents, manifest = _manifest_fixture()
    with pytest.raises(ValueError, match="^external_anchor_publication_invalid$"):
        external_anchor.build_external_anchor_publication_v01(
            manifest=manifest,
            domain_projection=projection_item,
            safe_file_contents=contents,
            publication_base_head=publication_base_head,  # type: ignore[arg-type]
        )


def test_distinct_valid_publication_bases_are_accepted() -> None:
    projection_item, contents, manifest, first = _anchor_fixture()
    changed = "abcdef1" if first.publication_base_head != "abcdef1" else "1234567"
    second = external_anchor.build_external_anchor_publication_v01(
        manifest=manifest,
        domain_projection=projection_item,
        safe_file_contents=contents,
        publication_base_head=changed,
    )
    for publication in (first, second):
        assert not external_anchor.validate_external_anchor_publication_v01(
            publication,
            manifest=manifest,
            domain_projection=projection_item,
            safe_file_contents=contents,
        )
        assert publication.anchor_status == "EVIDENCE_ONLY"
    assert first.publication_base_head == (
        projection_item.domain_execution_identity.execution_head
    )
    assert second.publication_base_head == changed
    assert first.anchor_publication_id != second.anchor_publication_id


def test_changed_publication_base_requires_its_exact_anchor_identity() -> None:
    projection_item, contents, manifest, first = _anchor_fixture()
    changed = "abcdef1" if first.publication_base_head != "abcdef1" else "1234567"
    second = external_anchor.build_external_anchor_publication_v01(
        manifest=manifest,
        domain_projection=projection_item,
        safe_file_contents=contents,
        publication_base_head=changed,
    )
    stale = external_anchor.build_anchored_package_verification_v01(
        anchor_publication=second,
        manifest=manifest,
        domain_projection=projection_item,
        safe_file_contents=contents,
        supplied_anchor_publication_id=first.anchor_publication_id,
    )
    assert stale.external_anchor_supplied is True
    assert stale.external_anchor_verified is False
    assert stale.verification_status == "FAIL_CLOSED"
    assert not external_anchor.validate_anchored_package_verification_v01(
        stale,
        anchor_publication=second,
        manifest=manifest,
        domain_projection=projection_item,
        safe_file_contents=contents,
        supplied_anchor_publication_id=first.anchor_publication_id,
    )

    current = external_anchor.build_anchored_package_verification_v01(
        anchor_publication=second,
        manifest=manifest,
        domain_projection=projection_item,
        safe_file_contents=contents,
        supplied_anchor_publication_id=second.anchor_publication_id,
    )
    assert current.external_anchor_verified is True
    assert current.manifest_binding_verified is True
    assert current.package_binding_verified is True
    assert current.verification_status == "ANCHORED_PASS"
    assert not external_anchor.validate_anchored_package_verification_v01(
        current,
        anchor_publication=second,
        manifest=manifest,
        domain_projection=projection_item,
        safe_file_contents=contents,
        supplied_anchor_publication_id=second.anchor_publication_id,
    )

    first_current = external_anchor.build_anchored_package_verification_v01(
        anchor_publication=first,
        manifest=manifest,
        domain_projection=projection_item,
        safe_file_contents=contents,
        supplied_anchor_publication_id=first.anchor_publication_id,
    )
    assert first_current.anchored_verification_id != current.anchored_verification_id


def test_anchor_publication_has_no_future_commit_field() -> None:
    assert "publication_commit" not in {
        field.name for field in fields(external_anchor.ExternalAnchorPublicationV01)
    }


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("manifest_id", "0" * 64),
        ("domain_projection_id", "0" * 64),
        ("programme_identity_id", "0" * 64),
        ("domain_execution_identity_id", "0" * 64),
        ("attempt_identity_id", "0" * 64),
        ("domain_id", "changed_domain"),
        ("package_id", "package:changed"),
        ("logical_package_ref", "changed/package"),
        ("package_content_hash", "0" * 64),
        ("kernel_manifest_hash", "0" * 64),
    ),
)
def test_anchor_publication_binding_attacks_are_rejected(
    field: str,
    value: object,
) -> None:
    projection_item, contents, manifest, publication = _anchor_fixture()
    forged = _rehash_publication(replace(publication, **{field: value}))
    assert "external_anchor_binding_mismatch" in external_anchor.validate_external_anchor_publication_v01(
        forged,
        manifest=manifest,
        domain_projection=projection_item,
        safe_file_contents=contents,
    )


@pytest.mark.parametrize(
    "field",
    (
        "external_anchor_supplied_at_publication",
        "external_anchor_verified_at_publication",
        "anchored_pass_claimed",
    ),
)
def test_anchor_publication_nonclaim_attacks_are_rejected(field: str) -> None:
    projection_item, contents, manifest, publication = _anchor_fixture()
    forged = _rehash_publication(replace(publication, **{field: True}))
    assert "external_anchor_binding_mismatch" in external_anchor.validate_external_anchor_publication_v01(
        forged,
        manifest=manifest,
        domain_projection=projection_item,
        safe_file_contents=contents,
    )


@pytest.mark.parametrize(
    ("field", "reason"),
    (
        ("publication_provider_call_count", "external_anchor_external_call_forbidden"),
        ("publication_network_call_count", "external_anchor_external_call_forbidden"),
        ("publication_gemini_call_count", "external_anchor_external_call_forbidden"),
        ("created_authority_count", "external_anchor_authority_creation_forbidden"),
        ("created_permission_count", "external_anchor_permission_creation_forbidden"),
        ("real_world_effects_count", "external_anchor_effect_forbidden"),
    ),
)
def test_anchor_publication_zero_operation_attacks_are_rejected(
    field: str,
    reason: str,
) -> None:
    projection_item, contents, manifest, publication = _anchor_fixture()
    forged = _rehash_publication(replace(publication, **{field: 1}))
    assert reason in external_anchor.validate_external_anchor_publication_v01(
        forged,
        manifest=manifest,
        domain_projection=projection_item,
        safe_file_contents=contents,
    )


@pytest.mark.parametrize("status", ("ANCHORED_PASS", "FAIL_CLOSED"))
def test_anchor_publication_status_forgery_is_rejected(status: str) -> None:
    projection_item, contents, manifest, publication = _anchor_fixture()
    forged = _rehash_publication(replace(publication, anchor_status=status))
    assert external_anchor.validate_external_anchor_publication_v01(
        forged,
        manifest=manifest,
        domain_projection=projection_item,
        safe_file_contents=contents,
    )


@pytest.mark.parametrize(
    ("call_count", "domain_id", "expected_source_count"),
    ((0, "airline", 0), (12, "airline", 12), (6, "supplier_water_filter", 6)),
)
def test_valid_anchored_verification_geometries(
    call_count: int,
    domain_id: str,
    expected_source_count: int,
) -> None:
    projection_item, contents, manifest, publication, verification = _verification_fixture(
        call_count=call_count,
        domain_id=domain_id,
    )
    assert not external_anchor.validate_anchored_package_verification_v01(
        verification,
        anchor_publication=publication,
        manifest=manifest,
        domain_projection=projection_item,
        safe_file_contents=contents,
        supplied_anchor_publication_id=publication.anchor_publication_id,
    )
    assert verification.verification_status == "ANCHORED_PASS"
    assert projection_item.source_provider_call_count == expected_source_count
    assert (
        verification.verification_provider_call_count,
        verification.verification_network_call_count,
        verification.verification_gemini_call_count,
    ) == (0, 0, 0)


def test_valid_anchored_verification_booleans_are_exact() -> None:
    verification = _verification_fixture()[4]
    assert verification.external_anchor_supplied is True
    assert verification.external_anchor_verified is True
    assert verification.manifest_binding_verified is True
    assert verification.package_binding_verified is True
    assert verification.signature_verified is False
    assert verification.signer_identity_verified is False
    assert verification.root_attestation_verified is False


def test_anchored_verification_identity_is_deterministic() -> None:
    first = _verification_fixture()[4]
    second = _verification_fixture()[4]
    assert first == second
    assert first.anchored_verification_id == second.anchored_verification_id


def _different_anchor_id(anchor_id: str) -> str:
    replacement = "0" if anchor_id[0] != "0" else "1"
    return replacement + anchor_id[1:]


@pytest.mark.parametrize("mode", ("one_hex", "all_zero"))
def test_well_formed_anchor_mismatch_creates_coherent_fail_closed(
    mode: str,
) -> None:
    projection_item, contents, manifest, publication = _anchor_fixture()
    supplied = (
        _different_anchor_id(publication.anchor_publication_id)
        if mode == "one_hex"
        else "0" * 64
    )
    verification = external_anchor.build_anchored_package_verification_v01(
        anchor_publication=publication,
        manifest=manifest,
        domain_projection=projection_item,
        safe_file_contents=contents,
        supplied_anchor_publication_id=supplied,
    )
    assert verification.supplied_anchor_publication_id == supplied
    assert verification.external_anchor_verified is False
    assert verification.verification_status == "FAIL_CLOSED"
    assert not external_anchor.validate_anchored_package_verification_v01(
        verification,
        anchor_publication=publication,
        manifest=manifest,
        domain_projection=projection_item,
        safe_file_contents=contents,
        supplied_anchor_publication_id=supplied,
    )


@pytest.mark.parametrize(
    "supplied",
    ("A" * 64, "a" * 63, "a" * 65, "g" * 64, " a" + "0" * 62, "0" * 63 + " ", True, b"0" * 64),
)
def test_malformed_supplied_anchor_is_rejected(supplied: object) -> None:
    projection_item, contents, manifest, publication = _anchor_fixture()
    with pytest.raises(ValueError, match="^anchored_package_verification_invalid$"):
        external_anchor.build_anchored_package_verification_v01(
            anchor_publication=publication,
            manifest=manifest,
            domain_projection=projection_item,
            safe_file_contents=contents,
            supplied_anchor_publication_id=supplied,  # type: ignore[arg-type]
        )


def test_changed_supplied_anchor_changes_verification_identity() -> None:
    projection_item, contents, manifest, publication = _anchor_fixture()
    matching = _verification_fixture()[4]
    supplied = _different_anchor_id(publication.anchor_publication_id)
    mismatch = external_anchor.build_anchored_package_verification_v01(
        anchor_publication=publication,
        manifest=manifest,
        domain_projection=projection_item,
        safe_file_contents=contents,
        supplied_anchor_publication_id=supplied,
    )
    assert matching.anchored_verification_id != mismatch.anchored_verification_id


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("anchor_publication_id", "0" * 64),
        ("manifest_id", "0" * 64),
        ("domain_projection_id", "0" * 64),
        ("programme_identity_id", "0" * 64),
        ("domain_execution_identity_id", "0" * 64),
        ("attempt_identity_id", "0" * 64),
        ("domain_id", "changed_domain"),
        ("package_id", "package:changed"),
        ("logical_package_ref", "changed/package"),
        ("package_content_hash", "0" * 64),
        ("kernel_manifest_hash", "0" * 64),
        ("publication_base_head", "abcdef1"),
    ),
)
def test_anchored_verification_binding_attacks_are_rejected(
    field: str,
    value: object,
) -> None:
    projection_item, contents, manifest, publication, verification = _verification_fixture()
    forged = _rehash_verification(replace(verification, **{field: value}))
    assert external_anchor.validate_anchored_package_verification_v01(
        forged,
        anchor_publication=publication,
        manifest=manifest,
        domain_projection=projection_item,
        safe_file_contents=contents,
        supplied_anchor_publication_id=publication.anchor_publication_id,
    )


@pytest.mark.parametrize(
    "field",
    (
        "external_anchor_supplied",
        "external_anchor_verified",
        "manifest_binding_verified",
        "package_binding_verified",
        "signature_verified",
        "signer_identity_verified",
        "root_attestation_verified",
    ),
)
@pytest.mark.parametrize("mode", ("int_zero", "int_one", "wrong_bool"))
def test_verification_bool_fields_are_exact_and_derived(
    field: str,
    mode: str,
) -> None:
    projection_item, contents, manifest, publication, verification = _verification_fixture()
    current = getattr(verification, field)
    value = 0 if mode == "int_zero" else 1 if mode == "int_one" else not current
    forged = _rehash_verification(replace(verification, **{field: value}))
    assert external_anchor.validate_anchored_package_verification_v01(
        forged,
        anchor_publication=publication,
        manifest=manifest,
        domain_projection=projection_item,
        safe_file_contents=contents,
        supplied_anchor_publication_id=publication.anchor_publication_id,
    )


@pytest.mark.parametrize(
    ("field", "reason"),
    (
        ("signature_verified", "external_anchor_signature_claim_forbidden"),
        ("signer_identity_verified", "external_anchor_signer_identity_claim_forbidden"),
        ("root_attestation_verified", "external_anchor_root_attestation_claim_forbidden"),
    ),
)
def test_signature_identity_and_attestation_claims_are_forbidden(
    field: str,
    reason: str,
) -> None:
    projection_item, contents, manifest, publication, verification = _verification_fixture()
    forged = _rehash_verification(replace(verification, **{field: True}))
    assert reason in external_anchor.validate_anchored_package_verification_v01(
        forged,
        anchor_publication=publication,
        manifest=manifest,
        domain_projection=projection_item,
        safe_file_contents=contents,
        supplied_anchor_publication_id=publication.anchor_publication_id,
    )


PUBLICATION_COUNT_FIELDS = (
    "publication_provider_call_count",
    "publication_network_call_count",
    "publication_gemini_call_count",
    "created_authority_count",
    "created_permission_count",
    "real_world_effects_count",
)
VERIFICATION_COUNT_FIELDS = (
    "verification_provider_call_count",
    "verification_network_call_count",
    "verification_gemini_call_count",
    "created_authority_count",
    "created_permission_count",
    "real_world_effects_count",
)


@pytest.mark.parametrize("field", PUBLICATION_COUNT_FIELDS)
@pytest.mark.parametrize("value", (True, False, 1.0, 0.0, 1))
def test_publication_counts_require_exact_zero_int(field: str, value: object) -> None:
    projection_item, contents, manifest, publication = _anchor_fixture()
    forged = _rehash_publication(replace(publication, **{field: value}))
    assert external_anchor.validate_external_anchor_publication_v01(
        forged,
        manifest=manifest,
        domain_projection=projection_item,
        safe_file_contents=contents,
    )


@pytest.mark.parametrize("field", VERIFICATION_COUNT_FIELDS)
@pytest.mark.parametrize("value", (True, False, 1.0, 0.0, 1))
def test_verification_counts_require_exact_zero_int(field: str, value: object) -> None:
    projection_item, contents, manifest, publication, verification = _verification_fixture()
    forged = _rehash_verification(replace(verification, **{field: value}))
    assert external_anchor.validate_anchored_package_verification_v01(
        forged,
        anchor_publication=publication,
        manifest=manifest,
        domain_projection=projection_item,
        safe_file_contents=contents,
        supplied_anchor_publication_id=publication.anchor_publication_id,
    )


def test_anchor_builders_do_not_accept_status_or_verification_booleans() -> None:
    publication_parameters = inspect.signature(
        external_anchor.build_external_anchor_publication_v01
    ).parameters
    verification_parameters = inspect.signature(
        external_anchor.build_anchored_package_verification_v01
    ).parameters
    assert "anchor_status" not in publication_parameters
    assert "anchored_pass_claimed" not in publication_parameters
    assert "verification_status" not in verification_parameters
    assert "external_anchor_verified" not in verification_parameters
    assert "signature_verified" not in verification_parameters


def test_all_true_booleans_cannot_synthesize_anchored_pass() -> None:
    projection_item, contents, manifest, publication, verification = _verification_fixture()
    forged = replace(
        verification,
        external_anchor_supplied=True,
        external_anchor_verified=True,
        manifest_binding_verified=True,
        package_binding_verified=True,
        signature_verified=True,
        signer_identity_verified=True,
        root_attestation_verified=True,
        verification_status="ANCHORED_PASS",
    )
    forged = _rehash_verification(forged)
    errors = external_anchor.validate_anchored_package_verification_v01(
        forged,
        anchor_publication=publication,
        manifest=manifest,
        domain_projection=projection_item,
        safe_file_contents=contents,
        supplied_anchor_publication_id=publication.anchor_publication_id,
    )
    assert "external_anchor_signature_claim_forbidden" in errors
    assert "external_anchor_signer_identity_claim_forbidden" in errors
    assert "external_anchor_root_attestation_claim_forbidden" in errors


def test_coherent_fail_closed_verification_is_projectable() -> None:
    projection_item, contents, manifest, publication, verification = _verification_fixture(
        supplied_anchor_publication_id="0" * 64
    )
    assert verification.verification_status == "FAIL_CLOSED"
    plain = external_anchor.anchored_package_verification_to_plain_dict_v01(
        verification,
        anchor_publication=publication,
        manifest=manifest,
        domain_projection=projection_item,
        safe_file_contents=contents,
        supplied_anchor_publication_id="0" * 64,
    )
    assert plain["verification_status"] == "FAIL_CLOSED"


def test_anchor_public_projections_are_json_safe_and_isolated() -> None:
    projection_item, contents, manifest, publication, verification = _verification_fixture()
    publication_before = publication
    verification_before = verification
    publication_plain = external_anchor.external_anchor_publication_to_plain_dict_v01(
        publication,
        manifest=manifest,
        domain_projection=projection_item,
        safe_file_contents=contents,
    )
    verification_plain = external_anchor.anchored_package_verification_to_plain_dict_v01(
        verification,
        anchor_publication=publication,
        manifest=manifest,
        domain_projection=projection_item,
        safe_file_contents=contents,
        supplied_anchor_publication_id=publication.anchor_publication_id,
    )
    assert not _contains_forbidden_projection_value(publication_plain)
    assert not _contains_forbidden_projection_value(verification_plain)
    canonical_json_bytes_v01(publication_plain)
    canonical_json_bytes_v01(verification_plain)
    publication_plain["anchor_status"] = "changed"
    verification_plain["verification_status"] = "changed"
    assert publication == publication_before
    assert verification == verification_before
    assert all("private_key" not in key and "public_key" not in key for key in verification_plain)


def test_malformed_anchor_contracts_fail_stably() -> None:
    projection_item, contents, manifest, publication = _anchor_fixture()
    assert external_anchor.validate_external_anchor_publication_v01(
        object(),
        manifest=manifest,
        domain_projection=projection_item,
        safe_file_contents=contents,
    )
    with pytest.raises(ValueError, match="^external_anchor_publication_invalid$"):
        external_anchor.external_anchor_publication_to_plain_dict_v01(
            object(),  # type: ignore[arg-type]
            manifest=manifest,
            domain_projection=projection_item,
            safe_file_contents=contents,
        )
    assert external_anchor.validate_anchored_package_verification_v01(
        object(),
        anchor_publication=publication,
        manifest=manifest,
        domain_projection=projection_item,
        safe_file_contents=contents,
        supplied_anchor_publication_id=publication.anchor_publication_id,
    )
    with pytest.raises(ValueError, match="^anchored_package_verification_invalid$"):
        external_anchor.anchored_package_verification_to_plain_dict_v01(
            object(),  # type: ignore[arg-type]
            anchor_publication=publication,
            manifest=manifest,
            domain_projection=projection_item,
            safe_file_contents=contents,
            supplied_anchor_publication_id=publication.anchor_publication_id,
        )


def test_anchor_static_import_boundary_is_exact() -> None:
    tree = ast.parse(Path(external_anchor.__file__).read_text(encoding="utf-8"))
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
    assert set(imports) == {
        "dataclasses",
        "re",
        "unicodedata",
        "hedgehog.evidence.sealed_evidence_profile_v01",
        "hedgehog.evidence.sealed_package_v01",
        "hedgehog.kernel.integrity_replay_v01",
    }


@pytest.mark.parametrize(
    "forbidden",
    (
        "hedgehog.domains",
        "demo",
        "tests",
        "pathlib",
        "os",
        "stat",
        "tempfile",
        "zipfile",
        "tarfile",
        "shutil",
        "subprocess",
        "datetime",
        "time",
        "random",
        "secrets",
        "uuid",
        "cryptography",
        "provider",
        "gemini",
        "config",
        "requests",
        "socket",
        "git",
    ),
)
def test_anchor_static_forbidden_import_is_absent(forbidden: str) -> None:
    tree = ast.parse(Path(external_anchor.__file__).read_text(encoding="utf-8"))
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
    assert all(
        name != forbidden and not name.startswith(f"{forbidden}.")
        for name in imported
    )


def test_anchor_static_has_no_filesystem_git_or_effect_calls() -> None:
    tree = ast.parse(Path(external_anchor.__file__).read_text(encoding="utf-8"))
    called_names = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    forbidden_calls = {
        "open",
        "mkdir",
        "makedirs",
        "read_bytes",
        "read_text",
        "write_bytes",
        "write_text",
        "glob",
        "rglob",
        "run",
        "check_output",
        "sign",
        "verify",
        "authorize_effect_request_v01",
        "execute_mock_effect_v01",
    }
    assert called_names.isdisjoint(forbidden_calls)


def test_anchor_static_has_no_replay_or_future_commit_surface() -> None:
    names = set(vars(external_anchor))
    assert "SealedReplayEvidenceV01" not in names
    assert "publication_commit" not in names
    assert all(
        "publication_commit" not in {field.name for field in fields(contract)}
        for contract in (
            external_anchor.ExternalAnchorPublicationV01,
            external_anchor.AnchoredPackageVerificationV01,
        )
    )


def test_replay_dataclass_field_order_is_exact() -> None:
    assert is_dataclass(sealed_replay.SealedReplayEvidenceV01)
    assert tuple(
        field.name for field in fields(sealed_replay.SealedReplayEvidenceV01)
    ) == REPLAY_FIELD_NAMES
    assert len(REPLAY_FIELD_NAMES) == 38
    assert hasattr(sealed_replay.SealedReplayEvidenceV01, "__slots__")


def test_replay_dataclass_is_frozen() -> None:
    result = _replay_fixture()[1]
    with pytest.raises(FrozenInstanceError):
        result.replay_status = "FAIL_CLOSED"  # type: ignore[misc]


def test_replay_public_function_surface_is_exact() -> None:
    public_functions = tuple(
        name
        for name, value in vars(sealed_replay).items()
        if not name.startswith("_") and inspect.isfunction(value)
    )
    assert public_functions == REPLAY_PUBLIC_FUNCTION_NAMES


def test_replay_public_class_surface_is_exact() -> None:
    public_classes = tuple(
        name
        for name, value in vars(sealed_replay).items()
        if not name.startswith("_") and inspect.isclass(value)
    )
    assert public_classes == REPLAY_DATACLASS_NAMES


def test_final_package_surface_is_exact() -> None:
    assert evidence.__all__ == PACKAGE_ALL
    assert len(evidence.__all__) == 44
    for name in REPLAY_DATACLASS_NAMES + REPLAY_PUBLIC_FUNCTION_NAMES:
        assert getattr(evidence, name) is getattr(sealed_replay, name)


def test_replay_constants_are_exact() -> None:
    assert sealed_replay.MODULE_ID == "sealed_replay_evidence_v01"
    assert sealed_replay.REPLAY_VERSION == "v0.1"
    assert sealed_replay.STATUS_PASS == "PASS"
    assert sealed_replay.STATUS_FAIL_CLOSED == "FAIL_CLOSED"
    assert sealed_replay.REPLAY_STATUSES == ("PASS", "FAIL_CLOSED")
    assert type(sealed_replay.REPLAY_STATUSES) is tuple
    assert "EVIDENCE_ONLY" not in sealed_replay.REPLAY_STATUSES
    assert "ANCHORED_PASS" not in sealed_replay.REPLAY_STATUSES


@pytest.mark.parametrize(
    ("call_count", "domain_id"),
    ((0, "airline"), (12, "airline"), (6, "supplier_water_filter")),
)
def test_valid_replay_geometries_pass(call_count: int, domain_id: str) -> None:
    context, result = _replay_fixture(
        call_count=call_count,
        domain_id=domain_id,
    )
    assert not sealed_replay.validate_sealed_replay_evidence_v01(
        result,
        **context,  # type: ignore[arg-type]
    )
    assert result.integrity_verified is True
    assert result.continuity_verified is True
    assert result.anchor_verified is True
    assert result.replay_status == "PASS"
    assert result.source_manifest_id == result.reconstructed_manifest_id
    assert (
        result.source_domain_projection_id
        == result.reconstructed_domain_projection_id
    )
    assert (
        result.source_package_content_hash
        == result.reconstructed_package_content_hash
    )


def test_valid_replay_identity_and_geometry_are_exact() -> None:
    context, result = _replay_fixture()
    source_manifest = context["source_manifest"]
    source_projection = context["source_domain_projection"]
    publication = context["anchor_publication"]
    verification = context["anchored_verification"]
    assert result.source_manifest_id == source_manifest.manifest_id
    assert result.reconstructed_manifest_id == source_manifest.manifest_id
    assert result.anchor_publication_id == publication.anchor_publication_id
    assert result.anchored_verification_id == verification.anchored_verification_id
    assert result.source_domain_projection_id == source_projection.projection_id
    assert result.source_file_count == source_manifest.file_count
    assert result.source_artifact_count == source_manifest.artifact_count
    for value in (
        result.source_file_order_hash,
        result.reconstructed_file_order_hash,
        result.source_artifact_order_hash,
        result.reconstructed_artifact_order_hash,
        result.replay_id,
    ):
        assert len(value) == 64
        assert value == value.lower()


def test_replay_is_deterministic() -> None:
    first = _replay_fixture()[1]
    second = _replay_fixture()[1]
    assert first == second
    assert first.replay_id == second.replay_id


def test_replay_counters_are_zero_and_do_not_copy_live_source_counts() -> None:
    context, result = _replay_fixture(call_count=12)
    source_projection = context["source_domain_projection"]
    assert source_projection.source_provider_call_count == 12
    assert (
        result.semantic_rerun_count,
        result.root_decision_rerun_count,
        result.corridor_rerun_count,
        result.provider_call_count,
        result.network_call_count,
        result.gemini_call_count,
        result.created_authority_count,
        result.created_permission_count,
        result.action_created_count,
        result.receipt_created_count,
        result.final_output_created_count,
        result.real_world_effects_count,
    ) == (0,) * 12


@pytest.mark.parametrize("side", ("source", "reconstructed"))
def test_replay_exact_file_bytes_are_contextually_required(side: str) -> None:
    context, _ = _replay_fixture()
    changed = dict(context)
    changed[f"{side}_safe_file_contents"] = (b'{"status":"different"}\n',)
    with pytest.raises(ValueError, match="^sealed_replay_manifest_binding_mismatch$"):
        sealed_replay.build_sealed_replay_evidence_v01(
            **changed,  # type: ignore[arg-type]
            evidence_refs=("evidence/replay/source",),
        )


def test_replay_accepts_publication_base_distinct_from_execution_head() -> None:
    context, result = _replay_fixture(publication_base_head="abcdef1")
    publication = context["anchor_publication"]
    source_projection = context["source_domain_projection"]
    assert publication.publication_base_head == "abcdef1"
    assert (
        publication.publication_base_head
        != source_projection.domain_execution_identity.execution_head
    )
    assert result.anchor_verified is True
    assert result.replay_status == "PASS"


def test_old_anchor_for_changed_publication_yields_fail_closed_replay() -> None:
    first_context, _ = _replay_fixture()
    old_anchor_id = first_context["anchor_publication"].anchor_publication_id
    context, result = _replay_fixture(
        publication_base_head="abcdef1",
        supplied_anchor_publication_id=old_anchor_id,
    )
    verification = context["anchored_verification"]
    assert verification.verification_status == "FAIL_CLOSED"
    assert verification.external_anchor_verified is False
    assert result.integrity_verified is True
    assert result.continuity_verified is True
    assert result.anchor_verified is False
    assert result.replay_status == "FAIL_CLOSED"
    assert not sealed_replay.validate_sealed_replay_evidence_v01(
        result,
        **context,  # type: ignore[arg-type]
    )


def test_changed_byte_reconstruction_is_coherent_fail_closed() -> None:
    source_projection, _, _, source_manifest = _manifest_fixture()
    reconstruction = _changed_byte_reconstruction(
        source_projection,
        source_manifest,
    )
    context, result = _replay_fixture(reconstructed_context=reconstruction)
    assert result.integrity_verified is True
    assert result.continuity_verified is False
    assert result.anchor_verified is True
    assert result.replay_status == "FAIL_CLOSED"
    assert (
        result.source_package_content_hash
        != result.reconstructed_package_content_hash
    )
    assert result.source_file_count == result.reconstructed_file_count
    assert result.source_file_order_hash != result.reconstructed_file_order_hash
    assert not sealed_replay.validate_sealed_replay_evidence_v01(
        result,
        **context,  # type: ignore[arg-type]
    )


def test_changed_byte_fail_closed_replay_is_projectable() -> None:
    source_projection, _, _, source_manifest = _manifest_fixture()
    reconstruction = _changed_byte_reconstruction(
        source_projection,
        source_manifest,
    )
    context, result = _replay_fixture(reconstructed_context=reconstruction)
    plain = sealed_replay.sealed_replay_evidence_to_plain_dict_v01(
        result,
        **context,  # type: ignore[arg-type]
    )
    assert plain["replay_status"] == "FAIL_CLOSED"
    assert plain["continuity_verified"] is False


def test_distinct_valid_projection_is_coherent_fail_closed() -> None:
    reconstructed_projection, _, reconstructed_contents, reconstructed_manifest = (
        _manifest_fixture(domain_id="supplier_water_filter")
    )
    context, result = _replay_fixture(
        reconstructed_context=(
            reconstructed_projection,
            reconstructed_contents,
            reconstructed_manifest,
        )
    )
    assert result.integrity_verified is True
    assert result.continuity_verified is False
    assert result.anchor_verified is True
    assert result.replay_status == "FAIL_CLOSED"
    assert (
        result.source_domain_projection_id
        != result.reconstructed_domain_projection_id
    )
    assert not sealed_replay.validate_sealed_replay_evidence_v01(
        result,
        **context,  # type: ignore[arg-type]
    )


def test_changed_file_count_is_visible_and_fails_continuity() -> None:
    reconstructed_projection, _, reconstructed_contents, reconstructed_manifest = (
        _two_file_manifest_fixture()
    )
    context, result = _replay_fixture(
        reconstructed_context=(
            reconstructed_projection,
            reconstructed_contents,
            reconstructed_manifest,
        )
    )
    assert result.source_file_count == 1
    assert result.reconstructed_file_count == 2
    assert result.source_file_order_hash != result.reconstructed_file_order_hash
    assert result.continuity_verified is False
    assert result.replay_status == "FAIL_CLOSED"
    assert not sealed_replay.validate_sealed_replay_evidence_v01(
        result,
        **context,  # type: ignore[arg-type]
    )


def test_changed_artifact_geometry_is_visible_and_fails_continuity() -> None:
    reconstructed_projection, _, reconstructed_contents, reconstructed_manifest = (
        _manifest_fixture(extra_source=True)
    )
    context, result = _replay_fixture(
        reconstructed_context=(
            reconstructed_projection,
            reconstructed_contents,
            reconstructed_manifest,
        )
    )
    assert result.source_artifact_count != result.reconstructed_artifact_count
    assert (
        result.source_artifact_order_hash
        != result.reconstructed_artifact_order_hash
    )
    assert result.continuity_verified is False
    assert result.replay_status == "FAIL_CLOSED"
    assert not sealed_replay.validate_sealed_replay_evidence_v01(
        result,
        **context,  # type: ignore[arg-type]
    )


def test_invalid_anchor_publication_is_rejected_by_replay_builder() -> None:
    context, _ = _replay_fixture()
    publication = context["anchor_publication"]
    forged = _rehash_publication(replace(publication, manifest_id="0" * 64))
    changed = dict(context)
    changed["anchor_publication"] = forged
    with pytest.raises(ValueError, match="^sealed_replay_anchor_invalid$"):
        sealed_replay.build_sealed_replay_evidence_v01(
            **changed,  # type: ignore[arg-type]
            evidence_refs=("evidence/replay/source",),
        )


@pytest.mark.parametrize(
    "field",
    ("manifest_binding_verified", "package_binding_verified"),
)
def test_invalid_nested_anchor_binding_is_rejected(field: str) -> None:
    context, _ = _replay_fixture()
    verification = context["anchored_verification"]
    forged = _rehash_verification(
        replace(
            verification,
            **{field: False, "verification_status": "FAIL_CLOSED"},
        )
    )
    changed = dict(context)
    changed["anchored_verification"] = forged
    with pytest.raises(ValueError, match="^sealed_replay_anchor_invalid$"):
        sealed_replay.build_sealed_replay_evidence_v01(
            **changed,  # type: ignore[arg-type]
            evidence_refs=("evidence/replay/source",),
        )


def test_package_equality_cannot_synthesize_anchor_verification() -> None:
    context, result = _replay_fixture(
        supplied_anchor_publication_id="0" * 64,
    )
    assert result.source_manifest_id == result.reconstructed_manifest_id
    assert result.continuity_verified is True
    assert result.anchor_verified is False
    assert result.replay_status == "FAIL_CLOSED"
    forged = _rehash_replay(
        replace(result, anchor_verified=True, replay_status="PASS")
    )
    errors = sealed_replay.validate_sealed_replay_evidence_v01(
        forged,
        **context,  # type: ignore[arg-type]
    )
    assert "sealed_replay_anchor_invalid" in errors
    assert "sealed_replay_status_mismatch" in errors


@pytest.mark.parametrize(
    ("field", "value"),
    tuple(
        (field, value)
        for field in (
            "integrity_verified",
            "continuity_verified",
            "anchor_verified",
        )
        for value in (0, 1, False)
    ),
)
def test_replay_bool_attacks_are_rejected(field: str, value: object) -> None:
    context, result = _replay_fixture()
    forged = _rehash_replay(replace(result, **{field: value}))
    errors = sealed_replay.validate_sealed_replay_evidence_v01(
        forged,
        **context,  # type: ignore[arg-type]
    )
    assert errors
    with pytest.raises(ValueError, match="^sealed_replay_evidence_invalid$"):
        sealed_replay.sealed_replay_evidence_to_plain_dict_v01(
            forged,
            **context,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    ("field", "value"),
    tuple(
        (field, value)
        for field in (
            "semantic_rerun_count",
            "root_decision_rerun_count",
            "corridor_rerun_count",
        )
        for value in (1, True, False, 1.0, 0.0, "0")
    ),
)
def test_replay_rerun_attacks_are_rejected(field: str, value: object) -> None:
    context, result = _replay_fixture()
    forged = _rehash_replay(replace(result, **{field: value}))
    errors = sealed_replay.validate_sealed_replay_evidence_v01(
        forged,
        **context,  # type: ignore[arg-type]
    )
    assert "sealed_replay_rerun_forbidden" in errors


REPLAY_ZERO_COUNTER_REASONS = {
    "provider_call_count": "sealed_replay_external_call_forbidden",
    "network_call_count": "sealed_replay_external_call_forbidden",
    "gemini_call_count": "sealed_replay_external_call_forbidden",
    "created_authority_count": "sealed_replay_authority_creation_forbidden",
    "created_permission_count": "sealed_replay_permission_creation_forbidden",
    "action_created_count": "sealed_replay_action_creation_forbidden",
    "receipt_created_count": "sealed_replay_receipt_creation_forbidden",
    "final_output_created_count": (
        "sealed_replay_final_output_creation_forbidden"
    ),
    "real_world_effects_count": "sealed_replay_effect_forbidden",
}


@pytest.mark.parametrize(
    ("field", "expected_reason", "value"),
    tuple(
        (field, reason, value)
        for field, reason in REPLAY_ZERO_COUNTER_REASONS.items()
        for value in (1, True, False, 1.0, 0.0)
    ),
)
def test_replay_external_and_creation_counter_attacks_are_rejected(
    field: str,
    expected_reason: str,
    value: object,
) -> None:
    context, result = _replay_fixture()
    forged = _rehash_replay(replace(result, **{field: value}))
    errors = sealed_replay.validate_sealed_replay_evidence_v01(
        forged,
        **context,  # type: ignore[arg-type]
    )
    assert expected_reason in errors


@pytest.mark.parametrize(
    "evidence_refs",
    (
        (),
        [],
        ("evidence/replay/source", "evidence/replay/source"),
        ("",),
        ("/owner/private",),
        ("evidence/../private",),
        ("evidence/./source",),
        ("evidence\\source",),
        ("evidence//source",),
        ("C:/private/source",),
        ("evidence/source\x00",),
        ("evidence/\ud800",),
        (f"evidence/{chr(0x202E)}source",),
        (f"evidence/{chr(0x200B)}source",),
        (f"evidence/{chr(0xFEFF)}source",),
        (f"evidence/{chr(0x2028)}source",),
        (f"evidence/{chr(0x2029)}source",),
        (" evidence/source",),
        ("evidence/source ",),
        ("evidence/cafe\u0301",),
    ),
)
def test_replay_evidence_reference_attacks_are_rejected(
    evidence_refs: object,
) -> None:
    context, _ = _replay_fixture()
    with pytest.raises(ValueError, match="^sealed_replay_reference_invalid$"):
        sealed_replay.build_sealed_replay_evidence_v01(
            **context,  # type: ignore[arg-type]
            evidence_refs=evidence_refs,  # type: ignore[arg-type]
        )


@pytest.mark.parametrize(
    "evidence_ref",
    (
        "evidence/Latin/source",
        "evidence/\u0414\u043e\u043a\u0430\u0437\u0430\u0442\u0435\u043b\u044c\u0441\u0442\u0432\u043e/source",
        "evidence/\u8a3c\u62e0/source",
    ),
)
def test_replay_ordinary_unicode_references_are_accepted(
    evidence_ref: str,
) -> None:
    context, result = _replay_fixture(evidence_refs=(evidence_ref,))
    assert result.evidence_refs == (evidence_ref,)
    assert result.replay_status == "PASS"
    assert not sealed_replay.validate_sealed_replay_evidence_v01(
        result,
        **context,  # type: ignore[arg-type]
    )


def test_replay_evidence_reference_order_changes_identity() -> None:
    first = _replay_fixture(
        evidence_refs=("evidence/replay/a", "evidence/replay/b")
    )[1]
    second = _replay_fixture(
        evidence_refs=("evidence/replay/b", "evidence/replay/a")
    )[1]
    assert first.evidence_refs != second.evidence_refs
    assert first.replay_id != second.replay_id


def test_replay_evidence_references_are_copied() -> None:
    refs = ("evidence/replay/a", "evidence/replay/b")
    result = _replay_fixture(evidence_refs=refs)[1]
    assert result.evidence_refs == refs
    assert type(result.evidence_refs) is tuple


@pytest.mark.parametrize(
    ("field", "value", "expected_reason"),
    (
        ("source_manifest_id", "0" * 64, "sealed_replay_manifest_binding_mismatch"),
        ("reconstructed_manifest_id", "0" * 64, "sealed_replay_manifest_binding_mismatch"),
        ("anchor_publication_id", "0" * 64, "sealed_replay_anchor_invalid"),
        ("anchored_verification_id", "0" * 64, "sealed_replay_anchor_invalid"),
        ("source_domain_projection_id", "0" * 64, "sealed_replay_projection_mismatch"),
        ("reconstructed_domain_projection_id", "0" * 64, "sealed_replay_projection_mismatch"),
        ("domain_id", "changed_domain", "sealed_replay_manifest_binding_mismatch"),
        ("package_id", "package:changed", "sealed_replay_manifest_binding_mismatch"),
        ("logical_package_ref", "changed/package", "sealed_replay_manifest_binding_mismatch"),
        ("source_package_content_hash", "0" * 64, "sealed_replay_hash_mismatch"),
        ("reconstructed_package_content_hash", "0" * 64, "sealed_replay_hash_mismatch"),
        ("source_file_order_hash", "0" * 64, "sealed_replay_hash_mismatch"),
        ("reconstructed_file_order_hash", "0" * 64, "sealed_replay_hash_mismatch"),
        ("source_artifact_order_hash", "0" * 64, "sealed_replay_hash_mismatch"),
        ("reconstructed_artifact_order_hash", "0" * 64, "sealed_replay_hash_mismatch"),
    ),
)
def test_replay_stored_identity_and_hash_attacks_are_rejected(
    field: str,
    value: object,
    expected_reason: str,
) -> None:
    context, result = _replay_fixture()
    forged = _rehash_replay(replace(result, **{field: value}))
    errors = sealed_replay.validate_sealed_replay_evidence_v01(
        forged,
        **context,  # type: ignore[arg-type]
    )
    assert expected_reason in errors


def test_stale_replay_identity_is_rejected() -> None:
    context, result = _replay_fixture()
    forged = replace(result, replay_id="0" * 64)
    assert "sealed_replay_identity_mismatch" in (
        sealed_replay.validate_sealed_replay_evidence_v01(
            forged,
            **context,  # type: ignore[arg-type]
        )
    )


@pytest.mark.parametrize(
    ("field", "value", "expected_reason"),
    tuple(
        (field, value, reason)
        for field, reason in (
            ("source_file_count", "sealed_replay_file_geometry_invalid"),
            ("reconstructed_file_count", "sealed_replay_file_geometry_invalid"),
            ("source_artifact_count", "sealed_replay_artifact_geometry_invalid"),
            (
                "reconstructed_artifact_count",
                "sealed_replay_artifact_geometry_invalid",
            ),
        )
        for value in (True, 1.0, 99)
    ),
)
def test_replay_geometry_count_attacks_are_rejected(
    field: str,
    value: object,
    expected_reason: str,
) -> None:
    context, result = _replay_fixture()
    forged = _rehash_replay(replace(result, **{field: value}))
    errors = sealed_replay.validate_sealed_replay_evidence_v01(
        forged,
        **context,  # type: ignore[arg-type]
    )
    assert expected_reason in errors


def test_stored_fail_closed_over_exact_context_is_rejected() -> None:
    context, result = _replay_fixture()
    forged = _rehash_replay(replace(result, replay_status="FAIL_CLOSED"))
    assert "sealed_replay_status_mismatch" in (
        sealed_replay.validate_sealed_replay_evidence_v01(
            forged,
            **context,  # type: ignore[arg-type]
        )
    )


def test_stored_pass_over_mismatch_is_rejected() -> None:
    source_projection, _, _, source_manifest = _manifest_fixture()
    reconstruction = _changed_byte_reconstruction(
        source_projection,
        source_manifest,
    )
    context, result = _replay_fixture(reconstructed_context=reconstruction)
    forged = _rehash_replay(replace(result, replay_status="PASS"))
    assert "sealed_replay_status_mismatch" in (
        sealed_replay.validate_sealed_replay_evidence_v01(
            forged,
            **context,  # type: ignore[arg-type]
        )
    )


def test_all_true_booleans_cannot_synthesize_replay_pass() -> None:
    source_projection, _, _, source_manifest = _manifest_fixture()
    reconstruction = _changed_byte_reconstruction(
        source_projection,
        source_manifest,
    )
    context, result = _replay_fixture(reconstructed_context=reconstruction)
    forged = _rehash_replay(
        replace(
            result,
            integrity_verified=True,
            continuity_verified=True,
            anchor_verified=True,
            replay_status="PASS",
        )
    )
    errors = sealed_replay.validate_sealed_replay_evidence_v01(
        forged,
        **context,  # type: ignore[arg-type]
    )
    assert "sealed_replay_status_mismatch" in errors


def test_coherent_nested_fail_closed_replay_is_projectable() -> None:
    context, result = _replay_fixture(fail_closed=True)
    assert result.integrity_verified is False
    assert result.anchor_verified is False
    assert result.replay_status == "FAIL_CLOSED"
    assert not sealed_replay.validate_sealed_replay_evidence_v01(
        result,
        **context,  # type: ignore[arg-type]
    )
    plain = sealed_replay.sealed_replay_evidence_to_plain_dict_v01(
        result,
        **context,  # type: ignore[arg-type]
    )
    assert plain["replay_status"] == "FAIL_CLOSED"


def _same_count_artifact_reconstruction(
    *,
    reverse_order: bool,
) -> tuple[
    profile.DomainEvidenceProjectionV01,
    tuple[bytes, ...],
    sealed_package.SealedPackageManifestV01,
]:
    source_projection, kernel_manifest_hash = _package_projection()
    source = source_projection.source_records[0]
    changed_artifact = _artifact(source, artifact_id="artifact:changed")
    crypto_artifact = _artifact(
        source,
        artifact_id="artifact:kernel_manifest",
        evidence_class="CRYPTOGRAPHIC_INTEGRITY",
        canonical_projection={"kernel_manifest": "grounded"},
    )
    artifacts = (changed_artifact, crypto_artifact)
    if reverse_order:
        artifacts = tuple(reversed(artifacts))
    reconstructed_projection = _projection(
        programme_identity=source_projection.programme_identity,
        domain_execution_identity=source_projection.domain_execution_identity,
        attempt_identity=source_projection.attempt_identity,
        source_records=source_projection.source_records,
        artifact_records=artifacts,
    )
    contents = (b'{"status":"safe"}\n',)
    files = (
        _safe_file(
            (source.source_record_id,),
            content=contents[0],
        ),
    )
    manifest = sealed_package.build_sealed_package_manifest_v01(
        domain_projection=reconstructed_projection,
        safe_file_records=files,
        safe_file_contents=contents,
        kernel_manifest_hash=kernel_manifest_hash,
    )
    return reconstructed_projection, contents, manifest


@pytest.mark.parametrize("reverse_order", (False, True))
def test_same_count_artifact_change_cannot_pass_on_counts_only(
    reverse_order: bool,
) -> None:
    reconstruction = _same_count_artifact_reconstruction(
        reverse_order=reverse_order
    )
    context, result = _replay_fixture(reconstructed_context=reconstruction)
    assert result.source_artifact_count == result.reconstructed_artifact_count
    assert (
        result.source_artifact_order_hash
        != result.reconstructed_artifact_order_hash
    )
    assert result.continuity_verified is False
    assert result.replay_status == "FAIL_CLOSED"
    assert not sealed_replay.validate_sealed_replay_evidence_v01(
        result,
        **context,  # type: ignore[arg-type]
    )


def test_same_count_logical_path_change_changes_file_order_hash() -> None:
    source_projection, _, _, source_manifest = _manifest_fixture()
    contents = (b'{"status":"safe"}\n',)
    source_ids = tuple(
        item.source_record_id for item in source_projection.source_records
    )
    files = (
        _safe_file(
            source_ids,
            logical_path="evidence/renamed.json",
            content=contents[0],
        ),
    )
    reconstructed_manifest = sealed_package.build_sealed_package_manifest_v01(
        domain_projection=source_projection,
        safe_file_records=files,
        safe_file_contents=contents,
        kernel_manifest_hash=source_manifest.kernel_manifest_hash,
    )
    context, result = _replay_fixture(
        reconstructed_context=(
            source_projection,
            contents,
            reconstructed_manifest,
        )
    )
    assert result.source_file_count == result.reconstructed_file_count
    assert result.source_file_order_hash != result.reconstructed_file_order_hash
    assert result.continuity_verified is False
    assert result.replay_status == "FAIL_CLOSED"


@pytest.mark.parametrize(
    ("field", "expected_reason"),
    (
        ("source_domain_projection", "sealed_replay_projection_mismatch"),
        ("reconstructed_domain_projection", "sealed_replay_projection_mismatch"),
        ("source_manifest", "sealed_replay_manifest_binding_mismatch"),
        ("reconstructed_manifest", "sealed_replay_manifest_binding_mismatch"),
    ),
)
def test_malformed_replay_context_is_rejected(
    field: str,
    expected_reason: str,
) -> None:
    context, _ = _replay_fixture()
    changed = dict(context)
    changed[field] = object()
    with pytest.raises(ValueError, match=f"^{expected_reason}$"):
        sealed_replay.build_sealed_replay_evidence_v01(
            **changed,  # type: ignore[arg-type]
            evidence_refs=("evidence/replay/source",),
        )


def test_replay_builder_does_not_accept_caller_status() -> None:
    context, _ = _replay_fixture()
    with pytest.raises(TypeError):
        sealed_replay.build_sealed_replay_evidence_v01(
            **context,  # type: ignore[arg-type]
            evidence_refs=("evidence/replay/source",),
            replay_status="PASS",  # type: ignore[call-arg]
        )


@pytest.mark.parametrize(
    ("function_name", "required_names"),
    (
        (
            "build_sealed_replay_evidence_v01",
            (
                "source_manifest",
                "source_domain_projection",
                "source_safe_file_contents",
                "anchor_publication",
                "anchored_verification",
                "supplied_anchor_publication_id",
                "reconstructed_manifest",
                "reconstructed_domain_projection",
                "reconstructed_safe_file_contents",
                "evidence_refs",
            ),
        ),
        (
            "validate_sealed_replay_evidence_v01",
            (
                "result",
                "source_manifest",
                "source_domain_projection",
                "source_safe_file_contents",
                "anchor_publication",
                "anchored_verification",
                "supplied_anchor_publication_id",
                "reconstructed_manifest",
                "reconstructed_domain_projection",
                "reconstructed_safe_file_contents",
            ),
        ),
        (
            "sealed_replay_evidence_to_plain_dict_v01",
            (
                "result",
                "source_manifest",
                "source_domain_projection",
                "source_safe_file_contents",
                "anchor_publication",
                "anchored_verification",
                "supplied_anchor_publication_id",
                "reconstructed_manifest",
                "reconstructed_domain_projection",
                "reconstructed_safe_file_contents",
            ),
        ),
    ),
)
def test_replay_public_signatures_are_exact(
    function_name: str,
    required_names: tuple[str, ...],
) -> None:
    signature = inspect.signature(getattr(sealed_replay, function_name))
    assert tuple(signature.parameters) == required_names


def test_replay_public_projection_is_json_safe_and_isolated() -> None:
    context, result = _replay_fixture(
        evidence_refs=("evidence/replay/a", "evidence/replay/b")
    )
    before = result
    plain = sealed_replay.sealed_replay_evidence_to_plain_dict_v01(
        result,
        **context,  # type: ignore[arg-type]
    )
    assert not _contains_forbidden_projection_value(plain)
    assert json.loads(canonical_json_bytes_v01(plain)) == plain
    plain["evidence_refs"].append("evidence/replay/mutated")
    plain["replay_status"] = "MUTATED"
    assert result == before
    assert result.evidence_refs == ("evidence/replay/a", "evidence/replay/b")
    assert result.replay_status == "PASS"


def test_replay_projection_contains_every_public_field() -> None:
    context, result = _replay_fixture()
    plain = sealed_replay.sealed_replay_evidence_to_plain_dict_v01(
        result,
        **context,  # type: ignore[arg-type]
    )
    assert tuple(plain) == REPLAY_FIELD_NAMES
    assert type(plain["evidence_refs"]) is list


def test_malformed_replay_contract_fails_stably() -> None:
    context, _ = _replay_fixture()
    assert sealed_replay.validate_sealed_replay_evidence_v01(
        object(),
        **context,  # type: ignore[arg-type]
    ) == ("sealed_replay_evidence_invalid",)
    with pytest.raises(ValueError, match="^sealed_replay_evidence_invalid$"):
        sealed_replay.sealed_replay_evidence_to_plain_dict_v01(
            object(),  # type: ignore[arg-type]
            **context,  # type: ignore[arg-type]
        )


def test_replay_static_import_boundary_is_exact() -> None:
    tree = ast.parse(Path(sealed_replay.__file__).read_text(encoding="utf-8"))
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
    assert set(imports) == {
        "dataclasses",
        "re",
        "unicodedata",
        "hedgehog.evidence.sealed_evidence_profile_v01",
        "hedgehog.evidence.sealed_package_v01",
        "hedgehog.evidence.external_anchor_v01",
        "hedgehog.kernel.integrity_replay_v01",
    }


@pytest.mark.parametrize(
    "forbidden",
    (
        "hedgehog.domains",
        "demo",
        "tests",
        "pathlib",
        "os",
        "stat",
        "tempfile",
        "zipfile",
        "tarfile",
        "shutil",
        "subprocess",
        "datetime",
        "time",
        "random",
        "secrets",
        "uuid",
        "cryptography",
        "provider",
        "gemini",
        "config",
        "release",
        "requests",
        "socket",
        "git",
    ),
)
def test_replay_static_forbidden_import_is_absent(forbidden: str) -> None:
    tree = ast.parse(Path(sealed_replay.__file__).read_text(encoding="utf-8"))
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
    assert all(
        name != forbidden and not name.startswith(f"{forbidden}.")
        for name in imported
    )


def test_replay_static_has_no_filesystem_runner_or_effect_calls() -> None:
    tree = ast.parse(Path(sealed_replay.__file__).read_text(encoding="utf-8"))
    called_names = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    forbidden_calls = {
        "open",
        "mkdir",
        "makedirs",
        "read_bytes",
        "read_text",
        "write_bytes",
        "write_text",
        "glob",
        "rglob",
        "run",
        "check_output",
        "sign",
        "verify",
        "execute_semantics",
        "execute_root_decision",
        "execute_corridor",
        "create_action",
        "create_receipt",
        "create_final_output",
        "authorize_effect_request_v01",
        "execute_mock_effect_v01",
    }
    assert called_names.isdisjoint(forbidden_calls)


def test_replay_module_has_no_accidental_public_surface() -> None:
    assert "annotations" not in vars(sealed_replay)
    public_classes = {
        name
        for name, value in vars(sealed_replay).items()
        if not name.startswith("_") and inspect.isclass(value)
    }
    public_functions = {
        name
        for name, value in vars(sealed_replay).items()
        if not name.startswith("_") and inspect.isfunction(value)
    }
    assert public_classes == set(REPLAY_DATACLASS_NAMES)
    assert public_functions == set(REPLAY_PUBLIC_FUNCTION_NAMES)
