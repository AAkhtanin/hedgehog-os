import ast
from collections import UserDict
from collections.abc import Mapping
import copy
from dataclasses import FrozenInstanceError, dataclass, fields, is_dataclass, replace
import inspect
import json
from pathlib import Path
from types import MappingProxyType

import pytest

from hedgehog.domains.supplier_water_filter import live_evidence_adapter_v01 as adapter
from hedgehog.kernel.integrity_replay_v01 import canonical_json_bytes_v01


EXPECTED_FIELDS = (
    "safe_execution_id",
    "safe_execution_version",
    "execution_head",
    "run_id",
    "report_id",
    "source_task_id",
    "transaction_id",
    "provider_mode",
    "model_id",
    "source_final_status",
    "actor_ids",
    "actor_safe_projection_hashes",
    "actor_validation_statuses",
    "bsep_id",
    "bsep_safe_projection_hash",
    "bsep_validation_status",
    "bsep_validated_before_architect",
    "provider_call_count",
    "network_call_count",
    "gemini_call_count",
    "raw_prompt_included",
    "raw_provider_response_included",
    "secret_scan_passed",
    "real_world_effects_count",
    "validation_errors",
    "status",
)
EXPECTED_FUNCTIONS = (
    "build_supplier_water_filter_safe_execution_projection_v01",
    "validate_supplier_water_filter_safe_execution_projection_v01",
    "supplier_water_filter_safe_execution_projection_to_plain_dict_v01",
)
EXPECTED_ACTOR_IDS = (
    "top_level_orchestrator_llm",
    "top_level_semantic_architect_llm",
    "legal_clause_semantic_extractor",
    "accounting_mismatch_semantic_explainer",
    "supplier_b_unstructured_note_interpreter",
    "bank_policy_semantic_reviewer",
)
UNSAFE_PUBLIC_TEXT = (
    "/Users/admin/private/raw_attempt",
    "failure at /Users/admin/private/report.json",
    "/workspace/scratch/private",
    "/mnt/private/file",
    "failure:/Users/admin/x",
    "path=/Users/admin/x",
    "C:\\Users\\admin\\private\\report.json",
    "C:/Users/admin/x",
    "failure:C:\\Users\\admin\\x",
    "\\\\server\\share\\private.json",
    "prefix=\\\\server\\share\\x",
    "//server/share/x",
    "file:///Users/admin/private/report.json",
    "address=0x1234abcd",
    "Traceback:",
    "Traceback (most recent call last):",
    "<PrivateRecord object at 0x1234abcd>",
    "OPENAI_API_KEY=private",
    "AWS_SECRET_ACCESS_KEY=private",
    "x:GEMINI_API_KEY=private",
    "GEMINI_API_KEY=private-value",
)
FORBIDDEN_KEY_VARIANTS = (
    "provider_response_backup",
    "nested_raw_prompt",
    "raw-prompt-copy",
    "providerResponseBackup",
    "privateKeyMaterial",
    "credential_snapshot",
    "secret-value-copy",
    "owner_absolute_path_copy",
    "rawUserText",
    "bankSecret",
    "actionPermission",
    "finalOutput",
)
COPIED_PUBLIC_TEXT_FIELDS = (
    "run_id",
    "report_id",
    "source_task_id",
    "transaction_id",
    "model_id",
    "bsep_id",
)
FORBIDDEN_IMPORT_ROOTS = {
    "os",
    "pathlib",
    "tempfile",
    "subprocess",
    "socket",
    "requests",
    "openai",
    "anthropic",
    "vertexai",
    "google",
    "genai",
    "httpx",
    "aiohttp",
    "urllib",
    "http",
    "demo",
    "tests",
    "time",
    "random",
    "secrets",
    "uuid",
}
FORBIDDEN_CALL_NAMES = {
    "open",
    "read_text",
    "read_bytes",
    "write_text",
    "write_bytes",
    "mkdir",
    "glob",
    "rglob",
    "iterdir",
    "generate_content",
}


@dataclass(frozen=True)
class _UnsafeDataclass:
    value: int


class _DictSubclass(dict):
    pass


class _ListSubclass(list):
    pass


class _TupleSubclass(tuple):
    pass


class _ExplosiveMapping(Mapping):
    def __init__(self):
        self.accessed = False

    def __getitem__(self, key):
        self.accessed = True
        raise AssertionError("custom mapping accessed")

    def __iter__(self):
        self.accessed = True
        raise AssertionError("custom mapping iterated")

    def __len__(self):
        self.accessed = True
        raise AssertionError("custom mapping measured")


def _safe_report() -> dict[str, object]:
    actors = [
        {
            "actor_id": actor_id,
            "safe_projection": {
                "actor_id": actor_id,
                "accepted_summary": f"safe accepted semantics for {actor_id}",
                "evidence_refs": [f"evidence:{index:02d}"],
            },
            "validation_status": "PASS",
        }
        for index, actor_id in enumerate(EXPECTED_ACTOR_IDS)
    ]
    return {
        "execution_head": "e64b4c1",
        "run_id": "supplier-water-filter-live-fixture-001",
        "report_id": "supplier-water-filter-live-fixture-001",
        "source_task_id": "supplier-water-filter-live-evidence-task-v01",
        "transaction_id": "supplier_water_filter:SH-2042:INV-2042",
        "provider_mode": "real_provider",
        "model_id": "gemini-2.5-flash",
        "source_final_status": "PASS",
        "actors": actors,
        "bsep": {
            "bsep_id": "bsep:supplier-water-filter:001",
            "safe_projection": {
                "bounded_business_context": [
                    "Supplier A scope only",
                    "Supplier B remains blocked",
                    "shipment remains held",
                ],
                "bounded_drs_context": {
                    "direct_reuse_allowed_count": 0,
                    "root_review_required": True,
                },
                "bounded_avf_context": {
                    "hard_masks_preserved": True,
                    "top_rank_is_advisory": True,
                },
                "material_exclusions": [
                    "user material",
                    "provider material",
                    "bank material",
                ],
            },
            "validation_status": "PASS",
            "validated_before_architect": True,
        },
        "counters": {
            "provider_call_count": 6,
            "network_call_count": 6,
            "gemini_call_count": 6,
        },
        "raw_prompt_included": False,
        "raw_provider_response_included": False,
        "secret_scan_passed": True,
        "real_world_effects_count": 0,
        "validation_errors": (),
    }


@pytest.fixture(scope="module")
def result():
    return adapter.build_supplier_water_filter_safe_execution_projection_v01(
        _safe_report()
    )


def _build(report=None):
    return adapter.build_supplier_water_filter_safe_execution_projection_v01(
        _safe_report() if report is None else report
    )


def _set_safe_projection(report, target, value):
    if target == "actor":
        report["actors"][0]["safe_projection"] = value
    else:
        report["bsep"]["safe_projection"] = value


def _set_copied_public_text(report, field_name, value):
    if field_name == "bsep_id":
        report["bsep"]["bsep_id"] = value
    else:
        report[field_name] = value


def _projection_rejection_reason(target):
    return "raw_material_forbidden" if target == "actor" else "bsep_invalid"


def _contains_forbidden(value: object) -> bool:
    if isinstance(value, bytes) or isinstance(value, tuple) or is_dataclass(value):
        return True
    if isinstance(value, dict):
        return any(_contains_forbidden(key) or _contains_forbidden(item) for key, item in value.items())
    if isinstance(value, list):
        return any(_contains_forbidden(item) for item in value)
    return False


@pytest.mark.parametrize(
    ("name", "expected"),
    (
        ("MODULE_ID", "supplier_water_filter_live_evidence_adapter_v01"),
        ("ADAPTER_VERSION", "v0.1"),
        ("STATUS_PASS", "PASS"),
        ("STATUS_FAIL_CLOSED", "FAIL_CLOSED"),
        ("ADAPTER_STATUSES", ("PASS", "FAIL_CLOSED")),
        ("PROVIDER_MODE_REAL", "real_provider"),
        ("ACTOR_IDS", EXPECTED_ACTOR_IDS),
    ),
)
def test_constants_are_exact(name, expected):
    assert getattr(adapter, name) == expected


@pytest.mark.parametrize(("index", "name"), tuple(enumerate(EXPECTED_FIELDS)))
def test_dataclass_field_order(index, name):
    assert fields(adapter.SupplierWaterFilterSafeExecutionProjectionV01)[index].name == name


def test_dataclass_field_geometry_is_exact():
    observed = tuple(
        field.name
        for field in fields(adapter.SupplierWaterFilterSafeExecutionProjectionV01)
    )
    assert observed == EXPECTED_FIELDS
    assert len(observed) == len(EXPECTED_FIELDS) == 26


def test_dataclass_is_frozen_and_slotted(result):
    assert adapter.SupplierWaterFilterSafeExecutionProjectionV01.__dataclass_params__.frozen
    assert "__slots__" in vars(adapter.SupplierWaterFilterSafeExecutionProjectionV01)
    with pytest.raises(FrozenInstanceError):
        result.run_id = "changed"


def test_public_surface_is_exact():
    classes = tuple(
        name
        for name, value in vars(adapter).items()
        if not name.startswith("_") and inspect.isclass(value)
    )
    functions = tuple(
        name
        for name, value in vars(adapter).items()
        if not name.startswith("_") and inspect.isfunction(value)
    )
    assert classes == ("SupplierWaterFilterSafeExecutionProjectionV01",)
    assert functions == EXPECTED_FUNCTIONS
    assert "annotations" not in vars(adapter)


def test_valid_projection_has_exact_six_actor_geometry(result):
    assert adapter.ACTOR_IDS == EXPECTED_ACTOR_IDS
    assert result.actor_ids == EXPECTED_ACTOR_IDS
    assert len(result.actor_safe_projection_hashes) == 6
    assert result.actor_validation_statuses == ("PASS",) * 6
    assert (result.provider_call_count, result.network_call_count, result.gemini_call_count) == (6, 6, 6)
    assert result.status == "PASS"
    assert adapter.validate_supplier_water_filter_safe_execution_projection_v01(result) == ()


@pytest.mark.parametrize("index", range(6))
def test_every_actor_hash_is_bound(index):
    first = _build()
    report = _safe_report()
    report["actors"][index]["safe_projection"]["accepted_summary"] += " changed"
    second = _build(report)
    changed = [a != b for a, b in zip(first.actor_safe_projection_hashes, second.actor_safe_projection_hashes)]
    assert changed == [position == index for position in range(6)]
    assert first.safe_execution_id != second.safe_execution_id


@pytest.mark.parametrize("index", range(6))
def test_every_actor_status_is_bound(index):
    report = _safe_report()
    report["actors"][index]["validation_status"] = "FAIL_CLOSED"
    result = _build(report)
    assert result.actor_validation_statuses[index] == "FAIL_CLOSED"
    assert result.status == "FAIL_CLOSED"


@pytest.mark.parametrize("mutation", ("missing", "duplicate", "reordered", "unknown"))
def test_actor_geometry_attacks_are_rejected(mutation):
    report = _safe_report()
    actors = report["actors"]
    if mutation == "missing":
        report["actors"] = actors[:-1]
    elif mutation == "duplicate":
        actors[1]["actor_id"] = actors[0]["actor_id"]
    elif mutation == "reordered":
        actors[0], actors[1] = actors[1], actors[0]
    else:
        actors[-1]["actor_id"] = "unknown_actor"
    with pytest.raises(ValueError, match="actor_geometry_invalid"):
        _build(report)


@pytest.mark.parametrize("key", tuple(_safe_report()))
def test_missing_top_level_key_is_rejected(key):
    report = _safe_report()
    report.pop(key)
    with pytest.raises(ValueError, match="source_invalid"):
        _build(report)


def test_additional_top_level_key_is_rejected():
    report = _safe_report()
    report["raw_report"] = {}
    with pytest.raises(ValueError, match="source_invalid"):
        _build(report)


@pytest.mark.parametrize(
    ("path", "value"),
    (
        (("actors",), {}),
        (("actors", 0), []),
        (("actors", 0, "extra"), True),
        (("bsep",), []),
        (("bsep", "extra"), True),
        (("counters",), []),
        (("counters", "extra"), 0),
    ),
)
def test_malformed_nested_shapes_are_rejected(path, value):
    report = _safe_report()
    if len(path) == 1:
        report[path[0]] = value
    elif len(path) == 2 and type(report[path[0]]) is list:
        report[path[0]][path[1]] = value
    elif len(path) == 2:
        report[path[0]][path[1]] = value
    else:
        report[path[0]][path[1]][path[2]] = value
    with pytest.raises(ValueError):
        _build(report)


@pytest.mark.parametrize("field", ("provider_call_count", "network_call_count", "gemini_call_count"))
@pytest.mark.parametrize("value", (True, 6.0, -1, 5, 7))
def test_exact_external_call_geometry_rejects_attacks(field, value):
    report = _safe_report()
    report["counters"][field] = value
    with pytest.raises(ValueError, match="call_geometry_invalid"):
        _build(report)


@pytest.mark.parametrize("field", ("raw_prompt_included", "raw_provider_response_included"))
def test_raw_material_flags_are_rejected(field):
    report = _safe_report()
    report[field] = True
    with pytest.raises(ValueError, match="raw_material_forbidden"):
        _build(report)


def test_failed_secret_scan_is_rejected():
    report = _safe_report()
    report["secret_scan_passed"] = False
    with pytest.raises(ValueError, match="secret_scan_required"):
        _build(report)


@pytest.mark.parametrize(
    "forbidden_key",
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
    ),
)
def test_actor_safe_projection_recursively_rejects_private_material(forbidden_key):
    report = _safe_report()
    report["actors"][0]["safe_projection"]["nested"] = {forbidden_key: "redacted"}
    with pytest.raises(ValueError, match="raw_material_forbidden"):
        _build(report)


@pytest.mark.parametrize(
    "forbidden_key",
    (
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
    ),
)
def test_bsep_recursively_rejects_forbidden_material(forbidden_key):
    report = _safe_report()
    report["bsep"]["safe_projection"]["nested"] = {forbidden_key: False}
    with pytest.raises(ValueError, match="bsep_invalid"):
        _build(report)


def test_bsep_is_bound_and_must_precede_architect():
    first = _build()
    report = _safe_report()
    report["bsep"]["safe_projection"]["bounded_business_context"].append("changed")
    second = _build(report)
    assert first.bsep_safe_projection_hash != second.bsep_safe_projection_hash
    report = _safe_report()
    report["bsep"]["validated_before_architect"] = False
    failed = _build(report)
    assert failed.status == "FAIL_CLOSED"
    assert failed.bsep_validated_before_architect is False


def test_source_failure_is_coherent_fail_closed():
    report = _safe_report()
    report["source_final_status"] = "FAIL_CLOSED"
    report["validation_errors"] = ("live_evidence_rejected",)
    result = _build(report)
    assert result.status == "FAIL_CLOSED"
    assert adapter.validate_supplier_water_filter_safe_execution_projection_v01(result) == ()


def test_build_is_deterministic_and_source_mapping_is_unchanged():
    report = _safe_report()
    before = copy.deepcopy(report)
    first = _build(report)
    second = _build(copy.deepcopy(report))
    assert first == second
    assert first.safe_execution_id == second.safe_execution_id
    assert report == before


def _changed_value(result, field_name):
    value = getattr(result, field_name)
    if field_name == "safe_execution_id":
        return "0" * 64
    if type(value) is bool:
        return not value
    if type(value) is int:
        return value + 1
    if type(value) is str:
        return value + "-changed"
    if type(value) is tuple:
        return (*value, "changed")
    raise AssertionError(field_name)


@pytest.mark.parametrize("field_name", EXPECTED_FIELDS)
def test_every_result_field_participates_in_validation(result, field_name):
    forged = replace(result, **{field_name: _changed_value(result, field_name)})
    assert adapter.validate_supplier_water_filter_safe_execution_projection_v01(forged)


def test_self_rehashed_actor_geometry_forgery_is_rejected(result):
    changed = replace(result, actor_ids=tuple(reversed(result.actor_ids)))
    forged = adapter._replace_id(changed, adapter._safe_execution_identity(changed))
    assert "supplier_water_filter_safe_execution_actor_geometry_invalid" in (
        adapter.validate_supplier_water_filter_safe_execution_projection_v01(forged)
    )


def test_self_rehashed_synthetic_pass_is_rejected():
    report = _safe_report()
    report["bsep"]["validated_before_architect"] = False
    result = _build(report)
    changed = replace(result, status="PASS")
    forged = adapter._replace_id(changed, adapter._safe_execution_identity(changed))
    assert "supplier_water_filter_safe_execution_status_mismatch" in (
        adapter.validate_supplier_water_filter_safe_execution_projection_v01(forged)
    )


def test_public_projection_is_json_safe_and_mutation_isolated(result):
    before = result
    first = adapter.supplier_water_filter_safe_execution_projection_to_plain_dict_v01(result)
    second = adapter.supplier_water_filter_safe_execution_projection_to_plain_dict_v01(result)
    canonical_json_bytes_v01(first)
    json.dumps(first, sort_keys=True)
    assert not _contains_forbidden(first)
    first["actor_ids"][0] = "changed"
    first["validation_errors"].append("changed")
    assert second["actor_ids"][0] == adapter.ACTOR_IDS[0]
    assert result == before


def test_projection_rejects_invalid_contract(result):
    forged = replace(result, provider_call_count=True)
    with pytest.raises(ValueError, match="^supplier_water_filter_safe_execution_projection_invalid$"):
        adapter.supplier_water_filter_safe_execution_projection_to_plain_dict_v01(forged)


def test_unexpected_exception_is_sanitized(monkeypatch):
    monkeypatch.setattr(adapter, "_component_hash", lambda *args: (_ for _ in ()).throw(RuntimeError("private")))
    with pytest.raises(ValueError, match="^supplier_water_filter_safe_execution_unexpected_exception$"):
        _build()


def test_ordinary_unicode_safe_text_is_accepted():
    report = _safe_report()
    report["source_task_id"] = "проверка-供应商-évidence-Ångström"
    assert _build(report).status == "PASS"


@pytest.mark.parametrize("unsafe_text", UNSAFE_PUBLIC_TEXT)
@pytest.mark.parametrize("field_name", COPIED_PUBLIC_TEXT_FIELDS)
def test_public_text_privacy_attacks_are_sanitized(field_name, unsafe_text):
    report = _safe_report()
    _set_copied_public_text(report, field_name, unsafe_text)
    with pytest.raises(ValueError) as captured:
        _build(report)
    assert str(captured.value) == "supplier_water_filter_safe_execution_source_invalid"
    assert unsafe_text not in str(captured.value)
    valid_projection = adapter.supplier_water_filter_safe_execution_projection_to_plain_dict_v01(
        _build()
    )
    assert unsafe_text not in json.dumps(valid_projection, ensure_ascii=False)


def test_non_nfc_public_text_is_rejected_without_normalization():
    report = _safe_report()
    report["source_task_id"] = "e\u0301vidence"
    with pytest.raises(
        ValueError,
        match="^supplier_water_filter_safe_execution_source_invalid$",
    ):
        _build(report)


@pytest.mark.parametrize("unsafe_text", UNSAFE_PUBLIC_TEXT)
def test_validation_errors_accept_only_bounded_reason_codes(unsafe_text):
    report = _safe_report()
    report["source_final_status"] = "FAIL_CLOSED"
    report["validation_errors"] = (unsafe_text,)
    with pytest.raises(
        ValueError,
        match="^supplier_water_filter_safe_execution_source_invalid$",
    ) as captured:
        _build(report)
    assert unsafe_text not in str(captured.value)


@pytest.mark.parametrize(
    "invalid_reason",
    ("Live Error", "live-error", "_live_error", "live_error_", "x" * 129),
)
def test_validation_error_reason_code_shape_is_closed(invalid_reason):
    report = _safe_report()
    report["source_final_status"] = "FAIL_CLOSED"
    report["validation_errors"] = (invalid_reason,)
    with pytest.raises(ValueError, match="source_invalid"):
        _build(report)


@pytest.mark.parametrize("unsafe_text", UNSAFE_PUBLIC_TEXT)
def test_forged_private_public_text_fails_validation_and_projection(result, unsafe_text):
    changed = replace(result, validation_errors=(unsafe_text,))
    forged = adapter._replace_id(changed, adapter._safe_execution_identity(changed))
    assert adapter.validate_supplier_water_filter_safe_execution_projection_v01(forged)
    with pytest.raises(
        ValueError,
        match="^supplier_water_filter_safe_execution_projection_invalid$",
    ) as captured:
        adapter.supplier_water_filter_safe_execution_projection_to_plain_dict_v01(forged)
    assert unsafe_text not in str(captured.value)


@pytest.mark.parametrize("field_name", COPIED_PUBLIC_TEXT_FIELDS)
def test_forged_public_text_fields_fail_validation_and_projection(result, field_name):
    changed = replace(result, **{field_name: "path=/Users/admin/private"})
    forged = adapter._replace_id(changed, adapter._safe_execution_identity(changed))
    assert adapter.validate_supplier_water_filter_safe_execution_projection_v01(forged)
    with pytest.raises(
        ValueError,
        match="^supplier_water_filter_safe_execution_projection_invalid$",
    ):
        adapter.supplier_water_filter_safe_execution_projection_to_plain_dict_v01(forged)


@pytest.mark.parametrize("forbidden_key", FORBIDDEN_KEY_VARIANTS)
@pytest.mark.parametrize(
    ("target", "reason"),
    (("actor", "raw_material_forbidden"), ("bsep", "bsep_invalid")),
)
def test_canonical_forbidden_key_variants_are_rejected(target, reason, forbidden_key):
    report = _safe_report()
    if target == "actor":
        report["actors"][0]["safe_projection"]["nested"] = {
            forbidden_key: "redacted"
        }
    else:
        report["bsep"]["safe_projection"]["nested"] = {
            forbidden_key: "redacted"
        }
    with pytest.raises(ValueError, match=reason):
        _build(report)


def test_non_string_and_non_nfc_nested_mapping_keys_are_rejected():
    for key in (1, "e\u0301vidence"):
        report = _safe_report()
        report["actors"][0]["safe_projection"]["nested"] = {key: "redacted"}
        with pytest.raises(ValueError, match="raw_material_forbidden"):
            _build(report)


@pytest.mark.parametrize("target", ("actor", "bsep"))
@pytest.mark.parametrize(
    "attack",
    ("mapping_proxy_root", "mapping_proxy_nested", "user_dict", "custom_mapping"),
)
def test_non_exact_mapping_attacks_are_rejected_without_custom_access(target, attack):
    explosive = None
    if attack == "mapping_proxy_root":
        value = MappingProxyType({"raw_prompt": "private"})
    elif attack == "mapping_proxy_nested":
        value = {"nested": MappingProxyType({"raw_prompt": "private"})}
    elif attack == "user_dict":
        value = UserDict({"raw_prompt": "private"})
    else:
        explosive = _ExplosiveMapping()
        value = explosive
    report = _safe_report()
    _set_safe_projection(report, target, value)
    with pytest.raises(ValueError, match=_projection_rejection_reason(target)):
        _build(report)
    if explosive is not None:
        assert explosive.accessed is False


@pytest.mark.parametrize("target", ("actor", "bsep"))
def test_nested_nfd_safe_projection_value_is_rejected(target):
    report = _safe_report()
    _set_safe_projection(report, target, {"accepted_summary": "e\u0301vidence"})
    with pytest.raises(ValueError, match=_projection_rejection_reason(target)):
        _build(report)


@pytest.mark.parametrize("target", ("actor", "bsep"))
def test_exact_safe_projection_value_domain_is_accepted(target):
    value = {
        "none_value": None,
        "bool_value": True,
        "int_value": 7,
        "float_value": 1.25,
        "text_value": "проверка 供应商 Ångström",
        "list_value": [False, 3, "safe"],
        "tuple_value": (None, 2.5, {"nested_value": "accepted"}),
    }
    report = _safe_report()
    _set_safe_projection(report, target, value)
    assert _build(report).status == "PASS"


def _unsafe_projection_values():
    return (
        b"bytes",
        bytearray(b"bytes"),
        memoryview(b"bytes"),
        {"set"},
        frozenset(("set",)),
        _UnsafeDataclass(1),
        _DictSubclass({"safe": True}),
        _ListSubclass(("safe",)),
        _TupleSubclass(("safe",)),
        float("inf"),
        float("-inf"),
        float("nan"),
        object(),
    )


@pytest.mark.parametrize("target", ("actor", "bsep"))
@pytest.mark.parametrize("unsafe_value", _unsafe_projection_values())
def test_non_closed_safe_projection_values_are_rejected(target, unsafe_value):
    report = _safe_report()
    _set_safe_projection(report, target, {"nested_value": unsafe_value})
    with pytest.raises(ValueError, match=_projection_rejection_reason(target)):
        _build(report)


@pytest.mark.parametrize("target", ("actor", "bsep"))
@pytest.mark.parametrize("container_kind", ("dict", "list"))
def test_cyclic_safe_projection_values_are_rejected(target, container_kind):
    if container_kind == "dict":
        value = {}
        value["cycle"] = value
    else:
        value = []
        value.append(value)
    report = _safe_report()
    _set_safe_projection(report, target, value)
    with pytest.raises(ValueError, match=_projection_rejection_reason(target)):
        _build(report)


def _import_roots(tree):
    roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    return roots


def _call_names(tree):
    names = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            names.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            names.add(node.func.attr)
    return names


def test_static_import_and_call_boundaries():
    path = Path("hedgehog/domains/supplier_water_filter/live_evidence_adapter_v01.py")
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports = _import_roots(tree)
    assert not imports.intersection(FORBIDDEN_IMPORT_ROOTS)
    calls = _call_names(tree)
    assert not calls.intersection(FORBIDDEN_CALL_NAMES)


def test_ast_guards_detect_from_imports_and_attribute_calls():
    tree = ast.parse(
        "from pathlib import Path\n"
        "from requests import get\n"
        "client.read_text()\n"
        "provider.generate_content()\n"
        "open('x')\n"
    )
    assert {"pathlib", "requests"} <= (
        _import_roots(tree).intersection(FORBIDDEN_IMPORT_ROOTS)
    )
    assert {"read_text", "generate_content", "open"} <= (
        _call_names(tree).intersection(FORBIDDEN_CALL_NAMES)
    )
