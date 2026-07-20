"""Pure Supplier / Water Filter owner-normalized live-evidence projection.

The adapter accepts one explicit safe normalization produced from accepted live
evidence. It does not accept or retain a raw provider report, prompt, response,
secret, environment value, filesystem path, callback, or private object. It
performs no provider, network, Gemini, filesystem, clock, randomness,
authority, permission, action, receipt, FinalOutput, or effect operation.
PASS is derived and never supplied by the caller. Hashes bind declared safe
projections; they do not establish semantic truth or production certification.
"""

from collections.abc import Mapping as _Mapping
from dataclasses import dataclass as _dataclass
import math as _math
import re as _re
import unicodedata as _unicodedata

from hedgehog.kernel.integrity_replay_v01 import (
    canonical_json_bytes_v01 as _canonical_json_bytes_v01,
    domain_separated_sha256_hex_v01 as _domain_separated_sha256_hex_v01,
)


MODULE_ID = "supplier_water_filter_live_evidence_adapter_v01"
ADAPTER_VERSION = "v0.1"

STATUS_PASS = "PASS"
STATUS_FAIL_CLOSED = "FAIL_CLOSED"
ADAPTER_STATUSES = (STATUS_PASS, STATUS_FAIL_CLOSED)

PROVIDER_MODE_REAL = "real_provider"

ACTOR_IDS = (
    "top_level_orchestrator_llm",
    "top_level_semantic_architect_llm",
    "legal_clause_semantic_extractor",
    "accounting_mismatch_semantic_explainer",
    "supplier_b_unstructured_note_interpreter",
    "bank_policy_semantic_reviewer",
)

_IDENTITY_DOMAIN = (
    "hedgehog.domains.supplier_water_filter.safe_execution_projection.v01"
)
_SAFE_COMPONENT_DOMAIN = (
    "hedgehog.domains.supplier_water_filter.safe_execution_component.v01"
)
_LOWER_HEX_64 = _re.compile(r"^[0-9a-f]{64}$")
_EXECUTION_HEAD = _re.compile(r"^[0-9a-f]{7,40}$")
_ABSOLUTE_POSIX_PATH = _re.compile(
    r"(?:^|[\s:=,;|()\[\]{}\"'`])/(?!/)[^\s]+",
)
_ABSOLUTE_WINDOWS_PATH = _re.compile(
    r"(?:^|[\s:=,;|()\[\]{}\"'`])[a-z]:[\\/]",
    _re.IGNORECASE,
)
_UNC_PATH = _re.compile(
    r"(?:^|[\s:=,;|()\[\]{}\"'`])(?:\\\\|//)[^\\/\s]+[\\/][^\s]+",
    _re.IGNORECASE,
)
_TRACEBACK_MARKER = _re.compile(
    r"\btraceback(?:\s*\([^\r\n)]*\))?\s*:",
    _re.IGNORECASE,
)
_OBJECT_REPRESENTATION = _re.compile(
    r"<[^>\r\n]*\bobject at 0x[0-9a-f]+>",
    _re.IGNORECASE,
)
_MEMORY_ADDRESS = _re.compile(r"\b0x[0-9a-f]{6,}\b", _re.IGNORECASE)
_SENSITIVE_ENV_ASSIGNMENT = _re.compile(
    r"(?:^|[^a-z0-9_])[a-z0-9_]*(?:api_key|private_key|password|secret|token|"
    r"credential)[a-z0-9_]*\s*=",
    _re.IGNORECASE,
)
_REASON_CODE = _re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")
_SOURCE_KEYS = frozenset(
    (
        "execution_head",
        "run_id",
        "report_id",
        "source_task_id",
        "transaction_id",
        "provider_mode",
        "model_id",
        "source_final_status",
        "actors",
        "bsep",
        "counters",
        "raw_prompt_included",
        "raw_provider_response_included",
        "secret_scan_passed",
        "real_world_effects_count",
        "validation_errors",
    )
)
_ACTOR_KEYS = frozenset(("actor_id", "safe_projection", "validation_status"))
_BSEP_KEYS = frozenset(
    (
        "bsep_id",
        "safe_projection",
        "validation_status",
        "validated_before_architect",
    )
)
_COUNTER_KEYS = frozenset(
    ("provider_call_count", "network_call_count", "gemini_call_count")
)
_FORBIDDEN_SAFE_KEYS = frozenset(
    (
        "raw_prompt",
        "prompt_text",
        "raw_response",
        "provider_response",
        "api_key",
        "private_key",
        "credential",
        "secret_value",
        "artifact_dir",
        "absolute_path",
        "raw_user_text",
        "raw_provider_text",
        "raw_drs_tables",
        "raw_avf_tables",
        "raw_iban",
        "bank_secret",
        "token",
        "authority",
        "permission",
        "final_output",
    )
)
_FORBIDDEN_BSEP_KEYS = _FORBIDDEN_SAFE_KEYS


@_dataclass(frozen=True, slots=True)
class SupplierWaterFilterSafeExecutionProjectionV01:
    safe_execution_id: str
    safe_execution_version: str
    execution_head: str
    run_id: str
    report_id: str
    source_task_id: str
    transaction_id: str
    provider_mode: str
    model_id: str
    source_final_status: str
    actor_ids: tuple[str, ...]
    actor_safe_projection_hashes: tuple[str, ...]
    actor_validation_statuses: tuple[str, ...]
    bsep_id: str
    bsep_safe_projection_hash: str
    bsep_validation_status: str
    bsep_validated_before_architect: bool
    provider_call_count: int
    network_call_count: int
    gemini_call_count: int
    raw_prompt_included: bool
    raw_provider_response_included: bool
    secret_scan_passed: bool
    real_world_effects_count: int
    validation_errors: tuple[str, ...]
    status: str

    def __post_init__(self) -> None:
        if (
            type(self.actor_ids) is not tuple
            or type(self.actor_safe_projection_hashes) is not tuple
            or type(self.actor_validation_statuses) is not tuple
            or type(self.validation_errors) is not tuple
        ):
            raise ValueError("supplier_water_filter_safe_execution_invalid")


def build_supplier_water_filter_safe_execution_projection_v01(
    source_report: _Mapping[str, object],
) -> SupplierWaterFilterSafeExecutionProjectionV01:
    try:
        source = _consume_mapping(source_report, _SOURCE_KEYS)
        actors = _consume_rows(source["actors"], _ACTOR_KEYS, len(ACTOR_IDS))
        actor_ids = tuple(_required_text(item["actor_id"]) for item in actors)
        if actor_ids != ACTOR_IDS:
            raise ValueError("supplier_water_filter_safe_execution_actor_geometry_invalid")
        actor_hashes = tuple(
            _component_hash("actor", actor_id, item["safe_projection"])
            for actor_id, item in zip(actor_ids, actors, strict=True)
        )
        actor_statuses = tuple(
            _required_status(item["validation_status"]) for item in actors
        )

        bsep = _consume_mapping(source["bsep"], _BSEP_KEYS)
        bsep_id = _required_text(bsep["bsep_id"])
        bsep_projection = bsep["safe_projection"]
        if _unsafe_safe_projection(bsep_projection, _FORBIDDEN_BSEP_KEYS):
            raise ValueError("supplier_water_filter_safe_execution_bsep_invalid")
        bsep_hash = _component_hash("bsep", bsep_id, bsep_projection)
        bsep_status = _required_status(bsep["validation_status"])
        bsep_before_architect = _required_bool(
            bsep["validated_before_architect"]
        )

        counters = _consume_mapping(source["counters"], _COUNTER_KEYS)
        external_counts = tuple(
            _required_nonnegative_int(counters[name])
            for name in (
                "provider_call_count",
                "network_call_count",
                "gemini_call_count",
            )
        )
        if external_counts != (6, 6, 6):
            raise ValueError("supplier_water_filter_safe_execution_call_geometry_invalid")

        raw_prompt = _required_bool(source["raw_prompt_included"])
        raw_response = _required_bool(source["raw_provider_response_included"])
        secret_scan = _required_bool(source["secret_scan_passed"])
        if raw_prompt or raw_response:
            raise ValueError("supplier_water_filter_safe_execution_raw_material_forbidden")
        if not secret_scan:
            raise ValueError("supplier_water_filter_safe_execution_secret_scan_required")

        provider_mode = _required_text(source["provider_mode"])
        source_status = _required_status(source["source_final_status"])
        validation_errors = _required_text_tuple(
            source["validation_errors"], allow_empty=True
        )
        effects = _required_nonnegative_int(source["real_world_effects_count"])
        status = (
            STATUS_PASS
            if provider_mode == PROVIDER_MODE_REAL
            and source_status == STATUS_PASS
            and all(value == STATUS_PASS for value in actor_statuses)
            and bsep_status == STATUS_PASS
            and bsep_before_architect
            and not validation_errors
            and effects == 0
            else STATUS_FAIL_CLOSED
        )

        result = SupplierWaterFilterSafeExecutionProjectionV01(
            safe_execution_id="0" * 64,
            safe_execution_version=ADAPTER_VERSION,
            execution_head=_required_execution_head(source["execution_head"]),
            run_id=_required_text(source["run_id"]),
            report_id=_required_text(source["report_id"]),
            source_task_id=_required_text(source["source_task_id"]),
            transaction_id=_required_text(source["transaction_id"]),
            provider_mode=provider_mode,
            model_id=_required_text(source["model_id"]),
            source_final_status=source_status,
            actor_ids=actor_ids,
            actor_safe_projection_hashes=actor_hashes,
            actor_validation_statuses=actor_statuses,
            bsep_id=bsep_id,
            bsep_safe_projection_hash=bsep_hash,
            bsep_validation_status=bsep_status,
            bsep_validated_before_architect=bsep_before_architect,
            provider_call_count=external_counts[0],
            network_call_count=external_counts[1],
            gemini_call_count=external_counts[2],
            raw_prompt_included=raw_prompt,
            raw_provider_response_included=raw_response,
            secret_scan_passed=secret_scan,
            real_world_effects_count=effects,
            validation_errors=validation_errors,
            status=status,
        )
        result = _replace_id(result, _safe_execution_identity(result))
        errors = _safe_execution_errors(result)
        if errors:
            raise ValueError(errors[0])
        return result
    except ValueError as error:
        raise ValueError(_stable_reason(error)) from None
    except Exception:
        raise ValueError("supplier_water_filter_safe_execution_unexpected_exception") from None


def validate_supplier_water_filter_safe_execution_projection_v01(
    result: object,
) -> tuple[str, ...]:
    try:
        return _safe_execution_errors(result)
    except Exception:
        return ("supplier_water_filter_safe_execution_unexpected_exception",)


def supplier_water_filter_safe_execution_projection_to_plain_dict_v01(
    result: SupplierWaterFilterSafeExecutionProjectionV01,
) -> dict[str, object]:
    try:
        if _safe_execution_errors(result):
            raise ValueError
        projection = _safe_execution_plain(result)
        _canonical_json_bytes_v01(projection)
        return projection
    except Exception:
        raise ValueError("supplier_water_filter_safe_execution_projection_invalid") from None


def _safe_execution_errors(result: object) -> tuple[str, ...]:
    if type(result) is not SupplierWaterFilterSafeExecutionProjectionV01:
        return ("supplier_water_filter_safe_execution_invalid",)
    errors: list[str] = []
    text_values = (
        result.safe_execution_version,
        result.run_id,
        result.report_id,
        result.source_task_id,
        result.transaction_id,
        result.provider_mode,
        result.model_id,
        result.source_final_status,
        result.bsep_id,
        result.bsep_validation_status,
        result.status,
    )
    if any(not _valid_text(value) for value in text_values):
        errors.append("supplier_water_filter_safe_execution_invalid")
    if result.safe_execution_version != ADAPTER_VERSION or not _valid_execution_head(
        result.execution_head
    ):
        errors.append("supplier_water_filter_safe_execution_invalid")
    if (
        type(result.actor_ids) is not tuple
        or result.actor_ids != ACTOR_IDS
        or type(result.actor_safe_projection_hashes) is not tuple
        or len(result.actor_safe_projection_hashes) != len(ACTOR_IDS)
        or any(not _valid_sha256(item) for item in result.actor_safe_projection_hashes)
        or type(result.actor_validation_statuses) is not tuple
        or len(result.actor_validation_statuses) != len(ACTOR_IDS)
        or any(item not in ADAPTER_STATUSES for item in result.actor_validation_statuses)
    ):
        errors.append("supplier_water_filter_safe_execution_actor_geometry_invalid")
    if (
        not _valid_sha256(result.bsep_safe_projection_hash)
        or result.bsep_validation_status not in ADAPTER_STATUSES
        or type(result.bsep_validated_before_architect) is not bool
    ):
        errors.append("supplier_water_filter_safe_execution_bsep_invalid")
    external_counts = (
        result.provider_call_count,
        result.network_call_count,
        result.gemini_call_count,
    )
    if any(not _nonnegative_int(value) for value in external_counts) or external_counts != (
        6,
        6,
        6,
    ):
        errors.append("supplier_water_filter_safe_execution_call_geometry_invalid")
    if (
        type(result.raw_prompt_included) is not bool
        or type(result.raw_provider_response_included) is not bool
        or result.raw_prompt_included
        or result.raw_provider_response_included
    ):
        errors.append("supplier_water_filter_safe_execution_raw_material_forbidden")
    if type(result.secret_scan_passed) is not bool or not result.secret_scan_passed:
        errors.append("supplier_water_filter_safe_execution_secret_scan_required")
    if (
        not _nonnegative_int(result.real_world_effects_count)
        or result.real_world_effects_count != 0
    ):
        errors.append("supplier_water_filter_safe_execution_effect_forbidden")
    if not _valid_text_tuple(result.validation_errors, allow_empty=True):
        errors.append("supplier_water_filter_safe_execution_invalid")
    derived_status = (
        STATUS_PASS
        if result.provider_mode == PROVIDER_MODE_REAL
        and result.source_final_status == STATUS_PASS
        and type(result.actor_validation_statuses) is tuple
        and all(value == STATUS_PASS for value in result.actor_validation_statuses)
        and result.bsep_validation_status == STATUS_PASS
        and result.bsep_validated_before_architect is True
        and type(result.validation_errors) is tuple
        and not result.validation_errors
        and result.real_world_effects_count == 0
        else STATUS_FAIL_CLOSED
    )
    if result.status not in ADAPTER_STATUSES or result.status != derived_status:
        errors.append("supplier_water_filter_safe_execution_status_mismatch")
    try:
        expected_id = _safe_execution_identity(result)
    except Exception:
        expected_id = ""
    if not _valid_sha256(result.safe_execution_id) or result.safe_execution_id != expected_id:
        errors.append("supplier_water_filter_safe_execution_identity_mismatch")
    return _dedupe(errors)


def _safe_execution_identity(
    result: SupplierWaterFilterSafeExecutionProjectionV01,
) -> str:
    return _domain_separated_sha256_hex_v01(
        domain=_IDENTITY_DOMAIN,
        payload=_canonical_json_bytes_v01(
            _safe_execution_plain(result, include_id=False)
        ),
    )


def _safe_execution_plain(
    result: SupplierWaterFilterSafeExecutionProjectionV01,
    *,
    include_id: bool = True,
) -> dict[str, object]:
    projection: dict[str, object] = {}
    if include_id:
        projection["safe_execution_id"] = result.safe_execution_id
    projection.update(
        {
            "safe_execution_version": result.safe_execution_version,
            "execution_head": result.execution_head,
            "run_id": result.run_id,
            "report_id": result.report_id,
            "source_task_id": result.source_task_id,
            "transaction_id": result.transaction_id,
            "provider_mode": result.provider_mode,
            "model_id": result.model_id,
            "source_final_status": result.source_final_status,
            "actor_ids": list(result.actor_ids),
            "actor_safe_projection_hashes": list(
                result.actor_safe_projection_hashes
            ),
            "actor_validation_statuses": list(result.actor_validation_statuses),
            "bsep_id": result.bsep_id,
            "bsep_safe_projection_hash": result.bsep_safe_projection_hash,
            "bsep_validation_status": result.bsep_validation_status,
            "bsep_validated_before_architect": (
                result.bsep_validated_before_architect
            ),
            "provider_call_count": result.provider_call_count,
            "network_call_count": result.network_call_count,
            "gemini_call_count": result.gemini_call_count,
            "raw_prompt_included": result.raw_prompt_included,
            "raw_provider_response_included": (
                result.raw_provider_response_included
            ),
            "secret_scan_passed": result.secret_scan_passed,
            "real_world_effects_count": result.real_world_effects_count,
            "validation_errors": list(result.validation_errors),
            "status": result.status,
        }
    )
    return projection


def _component_hash(kind: str, identity: str, projection: object) -> str:
    if _unsafe_safe_projection(projection, _FORBIDDEN_SAFE_KEYS):
        raise ValueError("supplier_water_filter_safe_execution_raw_material_forbidden")
    return _domain_separated_sha256_hex_v01(
        domain=_SAFE_COMPONENT_DOMAIN,
        payload=_canonical_json_bytes_v01(
            {"component_kind": kind, "component_id": identity, "projection": projection}
        ),
    )


def _consume_mapping(value: object, keys: frozenset[str]) -> dict[str, object]:
    if type(value) is not dict or frozenset(value) != keys:
        raise ValueError("supplier_water_filter_safe_execution_source_invalid")
    return {key: value[key] for key in value}


def _consume_rows(
    value: object,
    keys: frozenset[str],
    expected_count: int,
) -> tuple[dict[str, object], ...]:
    if type(value) not in (tuple, list) or len(value) != expected_count:
        raise ValueError("supplier_water_filter_safe_execution_actor_geometry_invalid")
    return tuple(_consume_mapping(item, keys) for item in value)


def _unsafe_safe_projection(value: object, forbidden: frozenset[str]) -> bool:
    return not _safe_projection_value_is_valid(value, forbidden, set())


def _safe_projection_value_is_valid(
    value: object,
    forbidden: frozenset[str],
    active_container_ids: set[int],
) -> bool:
    value_type = type(value)
    if value is None or value_type in (bool, int):
        return True
    if value_type is float:
        return _math.isfinite(value)
    if value_type is str:
        return _valid_projection_text(value)
    if value_type not in (dict, list, tuple):
        return False

    container_id = id(value)
    if container_id in active_container_ids:
        return False
    active_container_ids.add(container_id)
    try:
        if value_type is dict:
            for key, item in value.items():
                if type(key) is not str or not _valid_text(key):
                    return False
                if _key_contains_forbidden_token(key, forbidden):
                    return False
                if not _safe_projection_value_is_valid(
                    item,
                    forbidden,
                    active_container_ids,
                ):
                    return False
            return True
        return all(
            _safe_projection_value_is_valid(item, forbidden, active_container_ids)
            for item in value
        )
    finally:
        active_container_ids.remove(container_id)


def _key_contains_forbidden_token(key: str, forbidden: frozenset[str]) -> bool:
    separated = _re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", key)
    separated = _re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", separated)
    tokens = tuple(
        token
        for token in _re.sub(r"[^0-9A-Za-z]+", "_", separated).casefold().split("_")
        if token
    )
    compact = "".join(tokens)
    for forbidden_key in forbidden:
        forbidden_tokens = tuple(forbidden_key.casefold().split("_"))
        width = len(forbidden_tokens)
        if any(
            tokens[index : index + width] == forbidden_tokens
            for index in range(len(tokens) - width + 1)
        ):
            return True
        if "".join(forbidden_tokens) in compact:
            return True
    return False


def _replace_id(
    result: SupplierWaterFilterSafeExecutionProjectionV01,
    safe_execution_id: str,
) -> SupplierWaterFilterSafeExecutionProjectionV01:
    values = {name: getattr(result, name) for name in result.__slots__}
    values["safe_execution_id"] = safe_execution_id
    return SupplierWaterFilterSafeExecutionProjectionV01(**values)


def _valid_text(value: object) -> bool:
    if type(value) is not str or not value or value != value.strip():
        return False
    return _valid_projection_text(value)


def _valid_projection_text(value: object) -> bool:
    if type(value) is not str:
        return False
    if _unicodedata.normalize("NFC", value) != value:
        return False
    try:
        value.encode("utf-8", errors="strict")
    except UnicodeError:
        return False
    if not all(
        not (0xD800 <= ord(character) <= 0xDFFF)
        and _unicodedata.category(character) not in {"Cc", "Cf", "Cs", "Zl", "Zp"}
        for character in value
    ):
        return False
    folded = value.casefold()
    return not (
        "file://" in folded
        or _TRACEBACK_MARKER.search(value)
        or _ABSOLUTE_POSIX_PATH.search(value)
        or _ABSOLUTE_WINDOWS_PATH.search(value)
        or _UNC_PATH.search(value)
        or _OBJECT_REPRESENTATION.search(value)
        or _MEMORY_ADDRESS.search(value)
        or _SENSITIVE_ENV_ASSIGNMENT.search(value)
    )


def _valid_execution_head(value: object) -> bool:
    return type(value) is str and _EXECUTION_HEAD.fullmatch(value) is not None


def _valid_sha256(value: object) -> bool:
    return type(value) is str and _LOWER_HEX_64.fullmatch(value) is not None


def _nonnegative_int(value: object) -> bool:
    return type(value) is int and value >= 0


def _required_text(value: object) -> str:
    if not _valid_text(value):
        raise ValueError("supplier_water_filter_safe_execution_source_invalid")
    return value


def _required_execution_head(value: object) -> str:
    if not _valid_execution_head(value):
        raise ValueError("supplier_water_filter_safe_execution_source_invalid")
    return value


def _required_status(value: object) -> str:
    if type(value) is not str or value not in ADAPTER_STATUSES:
        raise ValueError("supplier_water_filter_safe_execution_source_invalid")
    return value


def _required_bool(value: object) -> bool:
    if type(value) is not bool:
        raise ValueError("supplier_water_filter_safe_execution_source_invalid")
    return value


def _required_nonnegative_int(value: object) -> int:
    if not _nonnegative_int(value):
        raise ValueError("supplier_water_filter_safe_execution_call_geometry_invalid")
    return value


def _required_text_tuple(value: object, *, allow_empty: bool) -> tuple[str, ...]:
    if type(value) not in (tuple, list):
        raise ValueError("supplier_water_filter_safe_execution_source_invalid")
    copied = tuple(value)
    if (not allow_empty and not copied) or any(
        not _valid_reason_code(item) for item in copied
    ):
        raise ValueError("supplier_water_filter_safe_execution_source_invalid")
    if len(copied) != len(set(copied)):
        raise ValueError("supplier_water_filter_safe_execution_source_invalid")
    return copied


def _valid_text_tuple(value: object, *, allow_empty: bool) -> bool:
    return (
        type(value) is tuple
        and (allow_empty or bool(value))
        and all(_valid_reason_code(item) for item in value)
        and len(value) == len(set(value))
    )


def _valid_reason_code(value: object) -> bool:
    return (
        _valid_text(value)
        and len(value) <= 128
        and _REASON_CODE.fullmatch(value) is not None
    )


def _stable_reason(error: ValueError) -> str:
    reason = error.args[0] if len(error.args) == 1 else ""
    allowed = {
        "supplier_water_filter_safe_execution_invalid",
        "supplier_water_filter_safe_execution_source_invalid",
        "supplier_water_filter_safe_execution_actor_geometry_invalid",
        "supplier_water_filter_safe_execution_call_geometry_invalid",
        "supplier_water_filter_safe_execution_raw_material_forbidden",
        "supplier_water_filter_safe_execution_secret_scan_required",
        "supplier_water_filter_safe_execution_bsep_invalid",
        "supplier_water_filter_safe_execution_effect_forbidden",
        "supplier_water_filter_safe_execution_identity_mismatch",
        "supplier_water_filter_safe_execution_status_mismatch",
    }
    return reason if type(reason) is str and reason in allowed else (
        "supplier_water_filter_safe_execution_invalid"
    )


def _dedupe(values: list[str]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(values))
