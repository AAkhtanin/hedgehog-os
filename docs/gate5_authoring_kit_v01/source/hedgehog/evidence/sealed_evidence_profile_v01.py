"""Domain-neutral evidence identity and projection contracts only.

This module creates no package, Anchor, or Replay. It calls no provider,
network, Gemini, filesystem, clock, or randomness source; creates no authority,
permission, or effect; and makes no production-certification claim. Hashes
establish integrity, not semantic truth. PASS is derived, never caller supplied.
"""

from dataclasses import dataclass as _dataclass
import hashlib as _hashlib
import re as _re
import unicodedata as _unicodedata

from hedgehog.kernel.abi_v01 import (
    CausalConsumptionRefV01 as _CausalConsumptionRefV01,
    validate_causal_consumption_ref_v01 as _validate_causal_consumption_ref_v01,
)
from hedgehog.kernel.integrity_replay_v01 import (
    CanonicalArtifactRefV01 as _CanonicalArtifactRefV01,
    canonical_json_bytes_v01 as _canonical_json_bytes_v01,
    domain_separated_sha256_hex_v01 as _domain_separated_sha256_hex_v01,
)


MODULE_ID = "sealed_evidence_profile_v01"
PROFILE_VERSION = "v0.1"

STATUS_PASS = "PASS"
STATUS_FAIL_CLOSED = "FAIL_CLOSED"
PROFILE_STATUSES = (STATUS_PASS, STATUS_FAIL_CLOSED)

PROVIDER_MODES = (
    "deterministic_fixture",
    "real_provider",
)

EVIDENCE_CLASSES = (
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
)
REPOSITORY_ALLOWED_EVIDENCE_CLASSES = EVIDENCE_CLASSES[1:]

_PROGRAMME_IDENTITY_DOMAIN = "hedgehog.evidence.programme_identity.v01"
_DOMAIN_EXECUTION_IDENTITY_DOMAIN = (
    "hedgehog.evidence.domain_execution_identity.v01"
)
_LIVE_ATTEMPT_IDENTITY_DOMAIN = "hedgehog.evidence.live_attempt_identity.v01"
_SAFE_SOURCE_RECORD_DOMAIN = "hedgehog.evidence.safe_source_record.v01"
_EVIDENCE_ARTIFACT_RECORD_DOMAIN = (
    "hedgehog.evidence.evidence_artifact_record.v01"
)
_DOMAIN_EVIDENCE_PROJECTION_DOMAIN = (
    "hedgehog.evidence.domain_evidence_projection.v01"
)

_RAW_PRIVATE_CLASS = "LIVE_PROVIDER_RAW_PRIVATE"
_LIVE_RUNTIME_CLASS = "EXECUTED_LIVE_RUNTIME"
_LOWER_HEX_64 = _re.compile(r"^[0-9a-f]{64}$")
_EXECUTION_HEAD = _re.compile(r"^[0-9a-f]{7,40}$")
_WINDOWS_DRIVE = _re.compile(r"^[A-Za-z]:")


@_dataclass(frozen=True, slots=True)
class ProgrammeEvidenceIdentityV01:
    programme_identity_id: str
    programme_id: str
    programme_version: str
    profile_version: str


@_dataclass(frozen=True, slots=True)
class DomainExecutionIdentityV01:
    domain_execution_identity_id: str
    programme_identity_id: str
    domain_id: str
    execution_head: str
    source_task_id: str
    run_id: str
    report_id: str


@_dataclass(frozen=True, slots=True)
class LiveAttemptIdentityV01:
    attempt_identity_id: str
    programme_id: str
    domain_id: str
    execution_head: str
    attempt_number: int
    run_id: str
    report_id: str
    source_task_id: str
    package_id: str
    logical_package_ref: str
    output_directory_ref: str
    provider_mode: str
    model_id: str
    expected_actor_count: int
    provider_call_budget: int


@_dataclass(frozen=True, slots=True)
class SafeSourceRecordV01:
    source_record_id: str
    source_id: str
    source_type: str
    evidence_class: str
    canonical_sha256: str
    byte_count: int
    media_type: str
    trace_refs: tuple[str, ...]
    contains_raw_prompt: bool
    contains_raw_provider_response: bool
    secret_scan_passed: bool
    observed_provider_call_count: int
    observed_network_call_count: int
    observed_gemini_call_count: int
    real_world_effects_count: int

    def __post_init__(self) -> None:
        if type(self.trace_refs) is not tuple:
            raise ValueError("safe_source_record_invalid")


@_dataclass(frozen=True, slots=True)
class EvidenceArtifactRecordV01:
    artifact_record_id: str
    artifact_id: str
    artifact_type: str
    evidence_class: str
    source_record_ids: tuple[str, ...]
    canonical_sha256: str
    authority_class: str
    owner_root_id: str | None
    trace_refs: tuple[str, ...]
    created_authority_count: int
    created_permission_count: int
    real_world_effects_count: int

    def __post_init__(self) -> None:
        if type(self.source_record_ids) is not tuple or type(self.trace_refs) is not tuple:
            raise ValueError("evidence_artifact_record_invalid")


@_dataclass(frozen=True, slots=True)
class DomainEvidenceProjectionV01:
    projection_id: str
    programme_identity: ProgrammeEvidenceIdentityV01
    domain_execution_identity: DomainExecutionIdentityV01
    attempt_identity: LiveAttemptIdentityV01
    source_records: tuple[SafeSourceRecordV01, ...]
    artifact_records: tuple[EvidenceArtifactRecordV01, ...]
    kernel_artifact_refs: tuple[_CanonicalArtifactRefV01, ...]
    causal_consumption_refs: tuple[_CausalConsumptionRefV01, ...]
    evidence_refs: tuple[str, ...]
    limitation_refs: tuple[str, ...]
    source_provider_call_count: int
    source_network_call_count: int
    source_gemini_call_count: int
    projection_provider_call_count: int
    projection_network_call_count: int
    projection_gemini_call_count: int
    created_authority_count: int
    created_permission_count: int
    real_world_effects_count: int
    status: str

    def __post_init__(self) -> None:
        tuple_fields = (
            self.source_records,
            self.artifact_records,
            self.kernel_artifact_refs,
            self.causal_consumption_refs,
            self.evidence_refs,
            self.limitation_refs,
        )
        if any(type(value) is not tuple for value in tuple_fields):
            raise ValueError("domain_evidence_projection_invalid")


def build_programme_evidence_identity_v01(
    *,
    programme_id: str,
    programme_version: str,
) -> ProgrammeEvidenceIdentityV01:
    try:
        if not _valid_text(programme_id) or not _valid_text(programme_version):
            raise ValueError("programme_evidence_identity_invalid")
        core = {
            "programme_id": programme_id,
            "programme_version": programme_version,
            "profile_version": PROFILE_VERSION,
        }
        result = ProgrammeEvidenceIdentityV01(
            programme_identity_id=_identity_hash(_PROGRAMME_IDENTITY_DOMAIN, core),
            programme_id=programme_id,
            programme_version=programme_version,
            profile_version=PROFILE_VERSION,
        )
        if _programme_identity_errors(result):
            raise ValueError("programme_evidence_identity_invalid")
        return result
    except ValueError:
        raise ValueError("programme_evidence_identity_invalid") from None
    except Exception:
        raise ValueError("evidence_unexpected_exception") from None


def validate_programme_evidence_identity_v01(result: object) -> tuple[str, ...]:
    try:
        return _programme_identity_errors(result)
    except Exception:
        return ("evidence_unexpected_exception",)


def programme_evidence_identity_to_plain_dict_v01(
    result: ProgrammeEvidenceIdentityV01,
) -> dict[str, object]:
    try:
        if _programme_identity_errors(result):
            raise ValueError
        projected = _programme_identity_plain(result)
        _canonical_json_bytes_v01(projected)
        return projected
    except Exception:
        raise ValueError("programme_evidence_identity_invalid") from None


def build_domain_execution_identity_v01(
    *,
    programme_identity: ProgrammeEvidenceIdentityV01,
    domain_id: str,
    execution_head: str,
    source_task_id: str,
    run_id: str,
    report_id: str,
) -> DomainExecutionIdentityV01:
    try:
        if _programme_identity_errors(programme_identity):
            raise ValueError
        values = (domain_id, source_task_id, run_id, report_id)
        if any(not _valid_text(value) for value in values) or not _valid_execution_head(
            execution_head
        ):
            raise ValueError
        core = {
            "programme_identity_id": programme_identity.programme_identity_id,
            "domain_id": domain_id,
            "execution_head": execution_head,
            "source_task_id": source_task_id,
            "run_id": run_id,
            "report_id": report_id,
        }
        result = DomainExecutionIdentityV01(
            domain_execution_identity_id=_identity_hash(
                _DOMAIN_EXECUTION_IDENTITY_DOMAIN,
                core,
            ),
            programme_identity_id=programme_identity.programme_identity_id,
            domain_id=domain_id,
            execution_head=execution_head,
            source_task_id=source_task_id,
            run_id=run_id,
            report_id=report_id,
        )
        if _domain_execution_identity_errors(result):
            raise ValueError
        return result
    except ValueError:
        raise ValueError("domain_execution_identity_invalid") from None
    except Exception:
        raise ValueError("evidence_unexpected_exception") from None


def validate_domain_execution_identity_v01(result: object) -> tuple[str, ...]:
    try:
        return _domain_execution_identity_errors(result)
    except Exception:
        return ("evidence_unexpected_exception",)


def domain_execution_identity_to_plain_dict_v01(
    result: DomainExecutionIdentityV01,
) -> dict[str, object]:
    try:
        if _domain_execution_identity_errors(result):
            raise ValueError
        projected = _domain_execution_identity_plain(result)
        _canonical_json_bytes_v01(projected)
        return projected
    except Exception:
        raise ValueError("domain_execution_identity_invalid") from None


def build_live_attempt_identity_v01(
    *,
    programme_identity: ProgrammeEvidenceIdentityV01,
    domain_execution_identity: DomainExecutionIdentityV01,
    attempt_number: int,
    package_id: str,
    logical_package_ref: str,
    output_directory_ref: str,
    provider_mode: str,
    model_id: str,
    expected_actor_count: int,
    provider_call_budget: int,
) -> LiveAttemptIdentityV01:
    try:
        if _programme_identity_errors(programme_identity) or _domain_execution_identity_errors(
            domain_execution_identity
        ):
            raise ValueError
        if (
            programme_identity.programme_identity_id
            != domain_execution_identity.programme_identity_id
        ):
            raise ValueError
        if not _positive_int(attempt_number):
            raise ValueError
        if not _valid_text(package_id) or not _logical_ref_valid(
            logical_package_ref
        ) or not _logical_ref_valid(output_directory_ref):
            raise ValueError
        if provider_mode not in PROVIDER_MODES or type(provider_mode) is not str:
            raise ValueError
        if not _valid_text(model_id) or not _positive_int(expected_actor_count):
            raise ValueError
        if not _nonnegative_int(provider_call_budget):
            raise ValueError
        core = {
            "programme_id": programme_identity.programme_id,
            "domain_id": domain_execution_identity.domain_id,
            "execution_head": domain_execution_identity.execution_head,
            "attempt_number": attempt_number,
            "run_id": domain_execution_identity.run_id,
            "report_id": domain_execution_identity.report_id,
            "source_task_id": domain_execution_identity.source_task_id,
            "package_id": package_id,
            "logical_package_ref": logical_package_ref,
            "output_directory_ref": output_directory_ref,
            "provider_mode": provider_mode,
            "model_id": model_id,
            "expected_actor_count": expected_actor_count,
            "provider_call_budget": provider_call_budget,
        }
        result = LiveAttemptIdentityV01(
            attempt_identity_id=_identity_hash(_LIVE_ATTEMPT_IDENTITY_DOMAIN, core),
            **core,
        )
        if _live_attempt_identity_errors(result):
            raise ValueError
        return result
    except ValueError:
        raise ValueError("live_attempt_identity_invalid") from None
    except Exception:
        raise ValueError("evidence_unexpected_exception") from None


def validate_live_attempt_identity_v01(result: object) -> tuple[str, ...]:
    try:
        return _live_attempt_identity_errors(result)
    except Exception:
        return ("evidence_unexpected_exception",)


def live_attempt_identity_to_plain_dict_v01(
    result: LiveAttemptIdentityV01,
) -> dict[str, object]:
    try:
        if _live_attempt_identity_errors(result):
            raise ValueError
        projected = _live_attempt_identity_plain(result)
        _canonical_json_bytes_v01(projected)
        return projected
    except Exception:
        raise ValueError("live_attempt_identity_invalid") from None


def build_safe_source_record_v01(
    *,
    source_id: str,
    source_type: str,
    evidence_class: str,
    canonical_projection: object,
    media_type: str,
    trace_refs: tuple[str, ...],
    contains_raw_prompt: bool,
    contains_raw_provider_response: bool,
    secret_scan_passed: bool,
    observed_provider_call_count: int,
    observed_network_call_count: int,
    observed_gemini_call_count: int,
    real_world_effects_count: int,
) -> SafeSourceRecordV01:
    try:
        if not _valid_text(source_id) or not _valid_text(source_type):
            raise ValueError
        if type(evidence_class) is not str or evidence_class not in EVIDENCE_CLASSES:
            raise ValueError
        if not _valid_text(media_type) or not _valid_text_tuple(
            trace_refs,
            allow_empty=False,
        ):
            raise ValueError
        flags = (
            contains_raw_prompt,
            contains_raw_provider_response,
            secret_scan_passed,
        )
        if any(type(flag) is not bool for flag in flags):
            raise ValueError
        counts = (
            observed_provider_call_count,
            observed_network_call_count,
            observed_gemini_call_count,
            real_world_effects_count,
        )
        if any(not _nonnegative_int(value) for value in counts):
            raise ValueError
        canonical_bytes = _canonical_json_bytes_v01(canonical_projection)
        core = {
            "source_id": source_id,
            "source_type": source_type,
            "evidence_class": evidence_class,
            "canonical_sha256": _hashlib.sha256(canonical_bytes).hexdigest(),
            "byte_count": len(canonical_bytes),
            "media_type": media_type,
            "trace_refs": list(trace_refs),
            "contains_raw_prompt": contains_raw_prompt,
            "contains_raw_provider_response": contains_raw_provider_response,
            "secret_scan_passed": secret_scan_passed,
            "observed_provider_call_count": observed_provider_call_count,
            "observed_network_call_count": observed_network_call_count,
            "observed_gemini_call_count": observed_gemini_call_count,
            "real_world_effects_count": real_world_effects_count,
        }
        result = SafeSourceRecordV01(
            source_record_id=_identity_hash(_SAFE_SOURCE_RECORD_DOMAIN, core),
            source_id=source_id,
            source_type=source_type,
            evidence_class=evidence_class,
            canonical_sha256=core["canonical_sha256"],
            byte_count=core["byte_count"],
            media_type=media_type,
            trace_refs=tuple(item for item in trace_refs),
            contains_raw_prompt=contains_raw_prompt,
            contains_raw_provider_response=contains_raw_provider_response,
            secret_scan_passed=secret_scan_passed,
            observed_provider_call_count=observed_provider_call_count,
            observed_network_call_count=observed_network_call_count,
            observed_gemini_call_count=observed_gemini_call_count,
            real_world_effects_count=real_world_effects_count,
        )
        if _safe_source_record_errors(result):
            raise ValueError
        return result
    except ValueError:
        raise ValueError("safe_source_record_invalid") from None
    except Exception:
        raise ValueError("evidence_unexpected_exception") from None


def validate_safe_source_record_v01(result: object) -> tuple[str, ...]:
    try:
        return _safe_source_record_errors(result)
    except Exception:
        return ("evidence_unexpected_exception",)


def safe_source_record_to_plain_dict_v01(
    result: SafeSourceRecordV01,
) -> dict[str, object]:
    try:
        if _safe_source_record_errors(result):
            raise ValueError
        projected = _safe_source_record_plain(result)
        _canonical_json_bytes_v01(projected)
        return projected
    except Exception:
        raise ValueError("safe_source_record_invalid") from None


def build_evidence_artifact_record_v01(
    *,
    artifact_id: str,
    artifact_type: str,
    evidence_class: str,
    source_record_ids: tuple[str, ...],
    canonical_projection: object,
    authority_class: str,
    owner_root_id: str | None,
    trace_refs: tuple[str, ...],
    created_authority_count: int,
    created_permission_count: int,
    real_world_effects_count: int,
) -> EvidenceArtifactRecordV01:
    try:
        if not _valid_text(artifact_id) or not _valid_text(artifact_type):
            raise ValueError
        if type(evidence_class) is not str or evidence_class not in EVIDENCE_CLASSES:
            raise ValueError
        if not _valid_text_tuple(source_record_ids, allow_empty=False):
            raise ValueError
        if not _valid_text(authority_class):
            raise ValueError
        if owner_root_id is not None and not _valid_text(owner_root_id):
            raise ValueError
        if not _valid_text_tuple(trace_refs, allow_empty=False):
            raise ValueError
        counts = (
            created_authority_count,
            created_permission_count,
            real_world_effects_count,
        )
        if any(not _nonnegative_int(value) for value in counts):
            raise ValueError
        canonical_bytes = _canonical_json_bytes_v01(canonical_projection)
        core = {
            "artifact_id": artifact_id,
            "artifact_type": artifact_type,
            "evidence_class": evidence_class,
            "source_record_ids": list(source_record_ids),
            "canonical_sha256": _hashlib.sha256(canonical_bytes).hexdigest(),
            "authority_class": authority_class,
            "owner_root_id": owner_root_id,
            "trace_refs": list(trace_refs),
            "created_authority_count": created_authority_count,
            "created_permission_count": created_permission_count,
            "real_world_effects_count": real_world_effects_count,
        }
        result = EvidenceArtifactRecordV01(
            artifact_record_id=_identity_hash(
                _EVIDENCE_ARTIFACT_RECORD_DOMAIN,
                core,
            ),
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            evidence_class=evidence_class,
            source_record_ids=tuple(item for item in source_record_ids),
            canonical_sha256=core["canonical_sha256"],
            authority_class=authority_class,
            owner_root_id=owner_root_id,
            trace_refs=tuple(item for item in trace_refs),
            created_authority_count=created_authority_count,
            created_permission_count=created_permission_count,
            real_world_effects_count=real_world_effects_count,
        )
        if _evidence_artifact_record_errors(result):
            raise ValueError
        return result
    except ValueError:
        raise ValueError("evidence_artifact_record_invalid") from None
    except Exception:
        raise ValueError("evidence_unexpected_exception") from None


def validate_evidence_artifact_record_v01(result: object) -> tuple[str, ...]:
    try:
        return _evidence_artifact_record_errors(result)
    except Exception:
        return ("evidence_unexpected_exception",)


def evidence_artifact_record_to_plain_dict_v01(
    result: EvidenceArtifactRecordV01,
) -> dict[str, object]:
    try:
        if _evidence_artifact_record_errors(result):
            raise ValueError
        projected = _evidence_artifact_record_plain(result)
        _canonical_json_bytes_v01(projected)
        return projected
    except Exception:
        raise ValueError("evidence_artifact_record_invalid") from None


def build_domain_evidence_projection_v01(
    *,
    programme_identity: ProgrammeEvidenceIdentityV01,
    domain_execution_identity: DomainExecutionIdentityV01,
    attempt_identity: LiveAttemptIdentityV01,
    source_records: tuple[SafeSourceRecordV01, ...],
    artifact_records: tuple[EvidenceArtifactRecordV01, ...],
    kernel_artifact_refs: tuple[_CanonicalArtifactRefV01, ...],
    causal_consumption_refs: tuple[_CausalConsumptionRefV01, ...],
    evidence_refs: tuple[str, ...],
    limitation_refs: tuple[str, ...],
) -> DomainEvidenceProjectionV01:
    try:
        copied_sources = _copy_typed_tuple(
            source_records,
            SafeSourceRecordV01,
            allow_empty=False,
        )
        copied_artifacts = _copy_typed_tuple(
            artifact_records,
            EvidenceArtifactRecordV01,
            allow_empty=False,
        )
        copied_kernel_refs = _copy_typed_tuple(
            kernel_artifact_refs,
            _CanonicalArtifactRefV01,
            allow_empty=True,
        )
        copied_causal_refs = _copy_typed_tuple(
            causal_consumption_refs,
            _CausalConsumptionRefV01,
            allow_empty=True,
        )
        copied_evidence_refs = _copy_text_tuple(evidence_refs, allow_empty=False)
        copied_limitation_refs = _copy_text_tuple(
            limitation_refs,
            allow_empty=False,
        )
        source_counts = _source_call_counts(copied_sources)
        created_authority_count = sum(
            item.created_authority_count for item in copied_artifacts
        )
        created_permission_count = sum(
            item.created_permission_count for item in copied_artifacts
        )
        real_world_effects_count = sum(
            item.real_world_effects_count for item in copied_sources
        ) + sum(item.real_world_effects_count for item in copied_artifacts)
        provisional = DomainEvidenceProjectionV01(
            projection_id="0" * 64,
            programme_identity=programme_identity,
            domain_execution_identity=domain_execution_identity,
            attempt_identity=attempt_identity,
            source_records=copied_sources,
            artifact_records=copied_artifacts,
            kernel_artifact_refs=copied_kernel_refs,
            causal_consumption_refs=copied_causal_refs,
            evidence_refs=copied_evidence_refs,
            limitation_refs=copied_limitation_refs,
            source_provider_call_count=source_counts[0],
            source_network_call_count=source_counts[1],
            source_gemini_call_count=source_counts[2],
            projection_provider_call_count=0,
            projection_network_call_count=0,
            projection_gemini_call_count=0,
            created_authority_count=created_authority_count,
            created_permission_count=created_permission_count,
            real_world_effects_count=real_world_effects_count,
            status=STATUS_FAIL_CLOSED,
        )
        base_errors = _domain_projection_base_errors(provisional)
        if base_errors:
            raise ValueError(base_errors[0])
        status = _derived_projection_status(provisional)
        status_bound = _replace_projection_status(provisional, status)
        result = _replace_projection_id(
            status_bound,
            _projection_identity(status_bound),
        )
        if _domain_projection_errors(result):
            raise ValueError
        return result
    except ValueError as error:
        reason = _stable_projection_builder_reason(error)
        raise ValueError(reason) from None
    except Exception:
        raise ValueError("evidence_unexpected_exception") from None


def validate_domain_evidence_projection_v01(result: object) -> tuple[str, ...]:
    try:
        return _domain_projection_errors(result)
    except Exception:
        return ("evidence_unexpected_exception",)


def domain_evidence_projection_to_plain_dict_v01(
    result: DomainEvidenceProjectionV01,
) -> dict[str, object]:
    try:
        if _domain_projection_errors(result):
            raise ValueError
        projected = _domain_projection_plain(result)
        _canonical_json_bytes_v01(projected)
        return projected
    except Exception:
        raise ValueError("domain_evidence_projection_invalid") from None


def _programme_identity_errors(result: object) -> tuple[str, ...]:
    if type(result) is not ProgrammeEvidenceIdentityV01:
        return ("programme_evidence_identity_invalid",)
    errors: list[str] = []
    if (
        not _valid_sha256(result.programme_identity_id)
        or not _valid_text(result.programme_id)
        or not _valid_text(result.programme_version)
        or result.profile_version != PROFILE_VERSION
    ):
        errors.append("programme_evidence_identity_invalid")
    if not errors:
        expected = _identity_hash(
            _PROGRAMME_IDENTITY_DOMAIN,
            {
                "programme_id": result.programme_id,
                "programme_version": result.programme_version,
                "profile_version": result.profile_version,
            },
        )
        if result.programme_identity_id != expected:
            errors.append("evidence_identity_mismatch")
    return _dedupe(errors)


def _domain_execution_identity_errors(result: object) -> tuple[str, ...]:
    if type(result) is not DomainExecutionIdentityV01:
        return ("domain_execution_identity_invalid",)
    errors: list[str] = []
    values = (
        result.programme_identity_id,
        result.domain_id,
        result.source_task_id,
        result.run_id,
        result.report_id,
    )
    if (
        not _valid_sha256(result.domain_execution_identity_id)
        or any(not _valid_text(value) for value in values)
        or not _valid_sha256(result.programme_identity_id)
        or not _valid_execution_head(result.execution_head)
    ):
        errors.append("domain_execution_identity_invalid")
    if not errors:
        expected = _identity_hash(
            _DOMAIN_EXECUTION_IDENTITY_DOMAIN,
            {
                "programme_identity_id": result.programme_identity_id,
                "domain_id": result.domain_id,
                "execution_head": result.execution_head,
                "source_task_id": result.source_task_id,
                "run_id": result.run_id,
                "report_id": result.report_id,
            },
        )
        if result.domain_execution_identity_id != expected:
            errors.append("evidence_identity_mismatch")
    return _dedupe(errors)


def _live_attempt_identity_errors(result: object) -> tuple[str, ...]:
    if type(result) is not LiveAttemptIdentityV01:
        return ("live_attempt_identity_invalid",)
    errors: list[str] = []
    text_values = (
        result.programme_id,
        result.domain_id,
        result.run_id,
        result.report_id,
        result.source_task_id,
        result.package_id,
        result.model_id,
    )
    if (
        not _valid_sha256(result.attempt_identity_id)
        or any(not _valid_text(value) for value in text_values)
        or not _valid_execution_head(result.execution_head)
        or not _positive_int(result.attempt_number)
        or not _logical_ref_valid(result.logical_package_ref)
        or not _logical_ref_valid(result.output_directory_ref)
        or type(result.provider_mode) is not str
        or result.provider_mode not in PROVIDER_MODES
        or not _positive_int(result.expected_actor_count)
        or not _nonnegative_int(result.provider_call_budget)
    ):
        errors.append("live_attempt_identity_invalid")
    if not errors:
        expected = _identity_hash(
            _LIVE_ATTEMPT_IDENTITY_DOMAIN,
            _live_attempt_identity_plain(result, include_id=False),
        )
        if result.attempt_identity_id != expected:
            errors.append("evidence_identity_mismatch")
    return _dedupe(errors)


def _safe_source_record_errors(result: object) -> tuple[str, ...]:
    if type(result) is not SafeSourceRecordV01:
        return ("safe_source_record_invalid",)
    errors: list[str] = []
    text_values = (result.source_id, result.source_type, result.media_type)
    flags = (
        result.contains_raw_prompt,
        result.contains_raw_provider_response,
        result.secret_scan_passed,
    )
    counts = (
        result.byte_count,
        result.observed_provider_call_count,
        result.observed_network_call_count,
        result.observed_gemini_call_count,
        result.real_world_effects_count,
    )
    if (
        not _valid_sha256(result.source_record_id)
        or any(not _valid_text(value) for value in text_values)
        or type(result.evidence_class) is not str
        or result.evidence_class not in EVIDENCE_CLASSES
        or not _valid_sha256(result.canonical_sha256)
        or any(not _nonnegative_int(value) for value in counts)
        or any(type(flag) is not bool for flag in flags)
        or not _valid_text_tuple(result.trace_refs, allow_empty=False)
    ):
        errors.append("safe_source_record_invalid")
    if not errors:
        expected = _identity_hash(
            _SAFE_SOURCE_RECORD_DOMAIN,
            _safe_source_record_plain(result, include_id=False),
        )
        if result.source_record_id != expected:
            errors.append("evidence_identity_mismatch")
    return _dedupe(errors)


def _evidence_artifact_record_errors(result: object) -> tuple[str, ...]:
    if type(result) is not EvidenceArtifactRecordV01:
        return ("evidence_artifact_record_invalid",)
    errors: list[str] = []
    text_values = (result.artifact_id, result.artifact_type, result.authority_class)
    counts = (
        result.created_authority_count,
        result.created_permission_count,
        result.real_world_effects_count,
    )
    if (
        not _valid_sha256(result.artifact_record_id)
        or any(not _valid_text(value) for value in text_values)
        or type(result.evidence_class) is not str
        or result.evidence_class not in EVIDENCE_CLASSES
        or not _valid_text_tuple(result.source_record_ids, allow_empty=False)
        or not _valid_sha256(result.canonical_sha256)
        or (
            result.owner_root_id is not None
            and not _valid_text(result.owner_root_id)
        )
        or not _valid_text_tuple(result.trace_refs, allow_empty=False)
        or any(not _nonnegative_int(value) for value in counts)
    ):
        errors.append("evidence_artifact_record_invalid")
    if not errors:
        expected = _identity_hash(
            _EVIDENCE_ARTIFACT_RECORD_DOMAIN,
            _evidence_artifact_record_plain(result, include_id=False),
        )
        if result.artifact_record_id != expected:
            errors.append("evidence_identity_mismatch")
    return _dedupe(errors)


def _domain_projection_base_errors(result: object) -> tuple[str, ...]:
    if type(result) is not DomainEvidenceProjectionV01:
        return ("domain_evidence_projection_invalid",)
    errors: list[str] = []
    nested_errors = (
        _programme_identity_errors(result.programme_identity),
        _domain_execution_identity_errors(result.domain_execution_identity),
        _live_attempt_identity_errors(result.attempt_identity),
    )
    for nested in nested_errors:
        errors.extend(nested)
    if any(nested for nested in nested_errors):
        errors.append("evidence_nested_identity_mismatch")

    tuple_specs = (
        (result.source_records, SafeSourceRecordV01, False),
        (result.artifact_records, EvidenceArtifactRecordV01, False),
        (result.kernel_artifact_refs, _CanonicalArtifactRefV01, True),
        (result.causal_consumption_refs, _CausalConsumptionRefV01, True),
    )
    for value, item_type, allow_empty in tuple_specs:
        if (
            type(value) is not tuple
            or (not allow_empty and not value)
            or any(type(item) is not item_type for item in value)
        ):
            errors.append("domain_evidence_projection_invalid")
    if not _valid_text_tuple(result.evidence_refs, allow_empty=False) or not _valid_text_tuple(
        result.limitation_refs,
        allow_empty=False,
    ):
        errors.append("evidence_duplicate_identity")

    if type(result.source_records) is tuple and all(
        type(item) is SafeSourceRecordV01 for item in result.source_records
    ):
        for item in result.source_records:
            errors.extend(_safe_source_record_errors(item))
        source_record_ids = tuple(item.source_record_id for item in result.source_records)
        source_ids = tuple(item.source_id for item in result.source_records)
        if _has_duplicates(source_record_ids) or _has_duplicates(source_ids):
            errors.append("evidence_duplicate_identity")
    else:
        source_record_ids = ()

    if type(result.artifact_records) is tuple and all(
        type(item) is EvidenceArtifactRecordV01 for item in result.artifact_records
    ):
        for item in result.artifact_records:
            errors.extend(_evidence_artifact_record_errors(item))
        artifact_record_ids = tuple(
            item.artifact_record_id for item in result.artifact_records
        )
        artifact_ids = tuple(item.artifact_id for item in result.artifact_records)
        if _has_duplicates(artifact_record_ids) or _has_duplicates(artifact_ids):
            errors.append("evidence_duplicate_identity")
        source_set = set(source_record_ids)
        if any(
            source_id not in source_set
            for item in result.artifact_records
            for source_id in item.source_record_ids
        ):
            errors.append("evidence_reference_unresolved")

    if type(result.kernel_artifact_refs) is tuple and all(
        type(item) is _CanonicalArtifactRefV01 for item in result.kernel_artifact_refs
    ):
        kernel_identities: list[bytes] = []
        kernel_ids: list[str] = []
        for item in result.kernel_artifact_refs:
            if not _canonical_artifact_ref_valid(item):
                errors.append("domain_evidence_projection_invalid")
                continue
            kernel_ids.append(item.artifact_id)
            kernel_identities.append(_canonical_json_bytes_v01(_canonical_artifact_ref_plain(item)))
        if _has_duplicates(tuple(kernel_ids)) or _has_duplicates(tuple(kernel_identities)):
            errors.append("evidence_duplicate_identity")

    if type(result.causal_consumption_refs) is tuple and all(
        type(item) is _CausalConsumptionRefV01
        for item in result.causal_consumption_refs
    ):
        causal_identities: list[bytes] = []
        for item in result.causal_consumption_refs:
            if _validate_causal_consumption_ref_v01(item):
                errors.append("domain_evidence_projection_invalid")
                continue
            causal_identities.append(_canonical_json_bytes_v01(_causal_ref_plain(item)))
        if _has_duplicates(tuple(causal_identities)):
            errors.append("evidence_duplicate_identity")

    if not any(nested_errors):
        programme = result.programme_identity
        domain = result.domain_execution_identity
        attempt = result.attempt_identity
        if (
            programme.programme_identity_id != domain.programme_identity_id
            or programme.programme_id != attempt.programme_id
            or domain.domain_id != attempt.domain_id
            or domain.execution_head != attempt.execution_head
            or domain.source_task_id != attempt.source_task_id
            or domain.run_id != attempt.run_id
            or domain.report_id != attempt.report_id
        ):
            errors.append("evidence_nested_identity_mismatch")

    if type(result.source_records) is tuple and all(
        type(item) is SafeSourceRecordV01 for item in result.source_records
    ):
        expected_source_counts = _source_call_counts(result.source_records)
        stored_source_counts = (
            result.source_provider_call_count,
            result.source_network_call_count,
            result.source_gemini_call_count,
        )
        if (
            any(not _nonnegative_int(value) for value in stored_source_counts)
            or stored_source_counts != expected_source_counts
        ):
            errors.append("evidence_external_call_forbidden")
    phase_counts = (
        result.projection_provider_call_count,
        result.projection_network_call_count,
        result.projection_gemini_call_count,
    )
    if any(not _nonnegative_int(value) for value in phase_counts) or phase_counts != (
        0,
        0,
        0,
    ):
        errors.append("evidence_external_call_forbidden")

    if type(result.artifact_records) is tuple and all(
        type(item) is EvidenceArtifactRecordV01 for item in result.artifact_records
    ):
        authority = sum(item.created_authority_count for item in result.artifact_records)
        permission = sum(
            item.created_permission_count for item in result.artifact_records
        )
        artifact_effects = sum(
            item.real_world_effects_count for item in result.artifact_records
        )
        if result.created_authority_count != authority or not _nonnegative_int(
            result.created_authority_count
        ):
            errors.append("evidence_authority_creation_forbidden")
        if result.created_permission_count != permission or not _nonnegative_int(
            result.created_permission_count
        ):
            errors.append("evidence_permission_creation_forbidden")
    else:
        artifact_effects = 0
    if type(result.source_records) is tuple and all(
        type(item) is SafeSourceRecordV01 for item in result.source_records
    ):
        source_effects = sum(
            item.real_world_effects_count for item in result.source_records
        )
    else:
        source_effects = 0
    if result.real_world_effects_count != source_effects + artifact_effects or not _nonnegative_int(
        result.real_world_effects_count
    ):
        errors.append("evidence_effect_forbidden")
    return _dedupe(errors)


def _domain_projection_errors(result: object) -> tuple[str, ...]:
    if type(result) is not DomainEvidenceProjectionV01:
        return ("domain_evidence_projection_invalid",)
    errors = list(_domain_projection_base_errors(result))
    expected_status = (
        STATUS_FAIL_CLOSED if errors else _derived_projection_status(result)
    )
    if type(result.status) is not str or result.status not in PROFILE_STATUSES:
        errors.append("domain_evidence_projection_invalid")
    elif result.status != expected_status:
        errors.append("evidence_status_mismatch")
    try:
        expected_id = _projection_identity(result)
        if not _valid_sha256(result.projection_id) or result.projection_id != expected_id:
            errors.append("evidence_identity_mismatch")
    except Exception:
        errors.append("domain_evidence_projection_invalid")
    return _dedupe(errors)


def _derived_projection_status(result: DomainEvidenceProjectionV01) -> str:
    sources = result.source_records
    artifacts = result.artifact_records
    if any(
        item.evidence_class == _RAW_PRIVATE_CLASS
        or item.contains_raw_prompt
        or item.contains_raw_provider_response
        or not item.secret_scan_passed
        or item.real_world_effects_count != 0
        for item in sources
    ):
        return STATUS_FAIL_CLOSED
    if any(
        item.created_authority_count != 0
        or item.created_permission_count != 0
        or item.real_world_effects_count != 0
        for item in artifacts
    ):
        return STATUS_FAIL_CLOSED
    nonzero_source_rows = tuple(
        item
        for item in sources
        if (
            item.observed_provider_call_count,
            item.observed_network_call_count,
            item.observed_gemini_call_count,
        )
        != (0, 0, 0)
    )
    if len(nonzero_source_rows) > 1:
        return STATUS_FAIL_CLOSED
    if nonzero_source_rows and nonzero_source_rows[0].evidence_class != _LIVE_RUNTIME_CLASS:
        return STATUS_FAIL_CLOSED
    attempt = result.attempt_identity
    source_counts = (
        result.source_provider_call_count,
        result.source_network_call_count,
        result.source_gemini_call_count,
    )
    if attempt.provider_mode == "real_provider":
        expected = attempt.provider_call_budget
        if source_counts != (expected, expected, expected):
            return STATUS_FAIL_CLOSED
        if attempt.expected_actor_count != expected:
            return STATUS_FAIL_CLOSED
    elif attempt.provider_mode == "deterministic_fixture":
        if source_counts != (0, 0, 0) or attempt.provider_call_budget != 0:
            return STATUS_FAIL_CLOSED
    else:
        return STATUS_FAIL_CLOSED
    if (
        result.projection_provider_call_count,
        result.projection_network_call_count,
        result.projection_gemini_call_count,
        result.created_authority_count,
        result.created_permission_count,
        result.real_world_effects_count,
    ) != (0, 0, 0, 0, 0, 0):
        return STATUS_FAIL_CLOSED
    return STATUS_PASS


def _programme_identity_plain(
    result: ProgrammeEvidenceIdentityV01,
    *,
    include_id: bool = True,
) -> dict[str, object]:
    projected: dict[str, object] = {}
    if include_id:
        projected["programme_identity_id"] = result.programme_identity_id
    projected.update(
        {
            "programme_id": result.programme_id,
            "programme_version": result.programme_version,
            "profile_version": result.profile_version,
        }
    )
    return projected


def _domain_execution_identity_plain(
    result: DomainExecutionIdentityV01,
    *,
    include_id: bool = True,
) -> dict[str, object]:
    projected: dict[str, object] = {}
    if include_id:
        projected["domain_execution_identity_id"] = (
            result.domain_execution_identity_id
        )
    projected.update(
        {
            "programme_identity_id": result.programme_identity_id,
            "domain_id": result.domain_id,
            "execution_head": result.execution_head,
            "source_task_id": result.source_task_id,
            "run_id": result.run_id,
            "report_id": result.report_id,
        }
    )
    return projected


def _live_attempt_identity_plain(
    result: LiveAttemptIdentityV01,
    *,
    include_id: bool = True,
) -> dict[str, object]:
    projected: dict[str, object] = {}
    if include_id:
        projected["attempt_identity_id"] = result.attempt_identity_id
    projected.update(
        {
            "programme_id": result.programme_id,
            "domain_id": result.domain_id,
            "execution_head": result.execution_head,
            "attempt_number": result.attempt_number,
            "run_id": result.run_id,
            "report_id": result.report_id,
            "source_task_id": result.source_task_id,
            "package_id": result.package_id,
            "logical_package_ref": result.logical_package_ref,
            "output_directory_ref": result.output_directory_ref,
            "provider_mode": result.provider_mode,
            "model_id": result.model_id,
            "expected_actor_count": result.expected_actor_count,
            "provider_call_budget": result.provider_call_budget,
        }
    )
    return projected


def _safe_source_record_plain(
    result: SafeSourceRecordV01,
    *,
    include_id: bool = True,
) -> dict[str, object]:
    projected: dict[str, object] = {}
    if include_id:
        projected["source_record_id"] = result.source_record_id
    projected.update(
        {
            "source_id": result.source_id,
            "source_type": result.source_type,
            "evidence_class": result.evidence_class,
            "canonical_sha256": result.canonical_sha256,
            "byte_count": result.byte_count,
            "media_type": result.media_type,
            "trace_refs": list(result.trace_refs),
            "contains_raw_prompt": result.contains_raw_prompt,
            "contains_raw_provider_response": result.contains_raw_provider_response,
            "secret_scan_passed": result.secret_scan_passed,
            "observed_provider_call_count": result.observed_provider_call_count,
            "observed_network_call_count": result.observed_network_call_count,
            "observed_gemini_call_count": result.observed_gemini_call_count,
            "real_world_effects_count": result.real_world_effects_count,
        }
    )
    return projected


def _evidence_artifact_record_plain(
    result: EvidenceArtifactRecordV01,
    *,
    include_id: bool = True,
) -> dict[str, object]:
    projected: dict[str, object] = {}
    if include_id:
        projected["artifact_record_id"] = result.artifact_record_id
    projected.update(
        {
            "artifact_id": result.artifact_id,
            "artifact_type": result.artifact_type,
            "evidence_class": result.evidence_class,
            "source_record_ids": list(result.source_record_ids),
            "canonical_sha256": result.canonical_sha256,
            "authority_class": result.authority_class,
            "owner_root_id": result.owner_root_id,
            "trace_refs": list(result.trace_refs),
            "created_authority_count": result.created_authority_count,
            "created_permission_count": result.created_permission_count,
            "real_world_effects_count": result.real_world_effects_count,
        }
    )
    return projected


def _domain_projection_plain(
    result: DomainEvidenceProjectionV01,
    *,
    include_id: bool = True,
) -> dict[str, object]:
    projected: dict[str, object] = {}
    if include_id:
        projected["projection_id"] = result.projection_id
    projected.update(
        {
            "programme_identity": _programme_identity_plain(
                result.programme_identity
            ),
            "domain_execution_identity": _domain_execution_identity_plain(
                result.domain_execution_identity
            ),
            "attempt_identity": _live_attempt_identity_plain(
                result.attempt_identity
            ),
            "source_records": [
                _safe_source_record_plain(item) for item in result.source_records
            ],
            "artifact_records": [
                _evidence_artifact_record_plain(item)
                for item in result.artifact_records
            ],
            "kernel_artifact_refs": [
                _canonical_artifact_ref_plain(item)
                for item in result.kernel_artifact_refs
            ],
            "causal_consumption_refs": [
                _causal_ref_plain(item) for item in result.causal_consumption_refs
            ],
            "evidence_refs": list(result.evidence_refs),
            "limitation_refs": list(result.limitation_refs),
            "source_provider_call_count": result.source_provider_call_count,
            "source_network_call_count": result.source_network_call_count,
            "source_gemini_call_count": result.source_gemini_call_count,
            "projection_provider_call_count": result.projection_provider_call_count,
            "projection_network_call_count": result.projection_network_call_count,
            "projection_gemini_call_count": result.projection_gemini_call_count,
            "created_authority_count": result.created_authority_count,
            "created_permission_count": result.created_permission_count,
            "real_world_effects_count": result.real_world_effects_count,
            "status": result.status,
        }
    )
    return projected


def _canonical_artifact_ref_plain(
    result: _CanonicalArtifactRefV01,
) -> dict[str, object]:
    return {
        "artifact_id": result.artifact_id,
        "artifact_type": result.artifact_type,
        "schema_version": result.schema_version,
        "transaction_id": result.transaction_id,
        "owner_root_id": result.owner_root_id,
        "authority_class": result.authority_class,
        "lifecycle_state": result.lifecycle_state,
        "payload_hash": result.payload_hash,
    }


def _causal_ref_plain(result: _CausalConsumptionRefV01) -> dict[str, object]:
    return {
        "producer_actor_id": result.producer_actor_id,
        "source_artifact_id": result.source_artifact_id,
        "output_field": result.output_field,
        "consumer_component": result.consumer_component,
        "downstream_artifact_id": result.downstream_artifact_id,
        "decision_effect": result.decision_effect,
        "disposition": result.disposition,
        "reason_code": result.reason_code,
        "trace_refs": list(result.trace_refs),
    }


def _canonical_artifact_ref_valid(result: object) -> bool:
    if type(result) is not _CanonicalArtifactRefV01:
        return False
    text_values = (
        result.artifact_id,
        result.artifact_type,
        result.schema_version,
        result.transaction_id,
        result.owner_root_id,
        result.authority_class,
        result.lifecycle_state,
    )
    return all(_valid_text(value) for value in text_values) and _valid_sha256(
        result.payload_hash
    )


def _projection_identity(result: DomainEvidenceProjectionV01) -> str:
    return _identity_hash(
        _DOMAIN_EVIDENCE_PROJECTION_DOMAIN,
        _domain_projection_plain(result, include_id=False),
    )


def _replace_projection_status(
    result: DomainEvidenceProjectionV01,
    status: str,
) -> DomainEvidenceProjectionV01:
    plain = {field: getattr(result, field) for field in result.__slots__}
    plain["status"] = status
    return DomainEvidenceProjectionV01(**plain)


def _replace_projection_id(
    result: DomainEvidenceProjectionV01,
    projection_id: str,
) -> DomainEvidenceProjectionV01:
    plain = {field: getattr(result, field) for field in result.__slots__}
    plain["projection_id"] = projection_id
    return DomainEvidenceProjectionV01(**plain)


def _identity_hash(domain: str, semantic_fields: object) -> str:
    return _domain_separated_sha256_hex_v01(
        domain=domain,
        payload=_canonical_json_bytes_v01(semantic_fields),
    )


def _source_call_counts(
    sources: tuple[SafeSourceRecordV01, ...],
) -> tuple[int, int, int]:
    return (
        sum(item.observed_provider_call_count for item in sources),
        sum(item.observed_network_call_count for item in sources),
        sum(item.observed_gemini_call_count for item in sources),
    )


def _copy_typed_tuple(
    value: object,
    item_type: type[object],
    *,
    allow_empty: bool,
) -> tuple[object, ...]:
    if (
        type(value) is not tuple
        or (not allow_empty and not value)
        or any(type(item) is not item_type for item in value)
    ):
        raise ValueError("domain_evidence_projection_invalid")
    return tuple(item for item in value)


def _copy_text_tuple(value: object, *, allow_empty: bool) -> tuple[str, ...]:
    if not _valid_text_tuple(value, allow_empty=allow_empty):
        raise ValueError("evidence_duplicate_identity")
    return tuple(item for item in value)


def _valid_text(value: object) -> bool:
    if type(value) is not str or not value or value != value.strip():
        return False
    if any(
        0xD800 <= ord(character) <= 0xDFFF
        or _unicodedata.category(character) in ("Cc", "Cf", "Cs", "Zl", "Zp")
        for character in value
    ):
        return False
    try:
        value.encode("utf-8", errors="strict")
    except UnicodeError:
        return False
    return True


def _valid_text_tuple(value: object, *, allow_empty: bool) -> bool:
    return bool(
        type(value) is tuple
        and (allow_empty or value)
        and all(_valid_text(item) for item in value)
        and len(value) == len(set(value))
    )


def _logical_ref_valid(value: object) -> bool:
    if not _valid_text(value) or type(value) is not str:
        return False
    if (
        value.startswith("/")
        or "\\" in value
        or _WINDOWS_DRIVE.match(value) is not None
        or _unicodedata.normalize("NFC", value) != value
    ):
        return False
    parts = value.split("/")
    return all(part not in ("", ".", "..") for part in parts)


def _valid_execution_head(value: object) -> bool:
    return type(value) is str and _EXECUTION_HEAD.fullmatch(value) is not None


def _valid_sha256(value: object) -> bool:
    return type(value) is str and _LOWER_HEX_64.fullmatch(value) is not None


def _positive_int(value: object) -> bool:
    return type(value) is int and value >= 1


def _nonnegative_int(value: object) -> bool:
    return type(value) is int and value >= 0


def _has_duplicates(values: tuple[object, ...]) -> bool:
    return len(values) != len(set(values))


def _dedupe(errors: object) -> tuple[str, ...]:
    return tuple(dict.fromkeys(errors))


def _stable_projection_builder_reason(error: ValueError) -> str:
    allowed = (
        "domain_evidence_projection_invalid",
        "evidence_identity_mismatch",
        "evidence_nested_identity_mismatch",
        "evidence_duplicate_identity",
        "evidence_reference_unresolved",
        "evidence_external_call_forbidden",
        "evidence_authority_creation_forbidden",
        "evidence_permission_creation_forbidden",
        "evidence_effect_forbidden",
        "evidence_status_mismatch",
    )
    if (
        type(error) is ValueError
        and len(error.args) == 1
        and type(error.args[0]) is str
        and error.args[0] in allowed
    ):
        return error.args[0]
    return "domain_evidence_projection_invalid"
