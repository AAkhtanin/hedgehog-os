from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, is_dataclass, replace
import ast
import inspect
import json
from pathlib import Path

import pytest

import hedgehog.kernel as kernel
from hedgehog.kernel import trust_model_v01 as trust


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "hedgehog/kernel/trust_model_v01.py"

EXPECTED_FIELDS = (
    "component_id",
    "component_class",
    "authority_class",
    "trusted_inputs",
    "untrusted_inputs",
    "produced_artifact_classes",
    "may_create_root_decision",
    "may_create_permission",
    "may_request_effect",
    "may_hold_effect_handle",
    "compromise_assumptions",
    "fail_closed_expectation",
)
EXPECTED_IDS = (
    "root",
    "provider_llm",
    "orchestrator",
    "semantic_architect",
    "deterministic_runtime",
    "drs",
    "avf",
    "executor_fractal_child",
    "post_vv",
    "gt",
    "domain_adapter",
    "effect_firewall",
    "corridor_adapter",
    "receipt",
    "ledger",
    "crypto",
    "replay",
    "renderer_showcase",
)
EXPECTED_CLASSES = (
    "ROOT",
    "PROVIDER_LLM",
    "ORCHESTRATOR",
    "SEMANTIC_ARCHITECT",
    "DETERMINISTIC_RUNTIME",
    "DRS",
    "AVF",
    "EXECUTOR_FRACTAL_CHILD",
    "POST_VV",
    "GT",
    "DOMAIN_ADAPTER",
    "EFFECT_FIREWALL",
    "CORRIDOR_ADAPTER",
    "RECEIPT",
    "LEDGER",
    "CRYPTO",
    "REPLAY",
    "RENDERER_SHOWCASE",
)
EXPECTED_AUTHORITY = (
    "ROOT_FINAL_AUTHORITY",
    "NON_ROOT_ADVISORY",
    "NON_ROOT_ADVISORY",
    "NON_ROOT_ADVISORY",
    "NON_ROOT_DETERMINISTIC",
    "NON_ROOT_INFORMATIONAL",
    "NON_ROOT_ADVISORY",
    "NON_ROOT_BOUNDED_EXECUTOR",
    "NON_ROOT_VALIDATION",
    "NON_ROOT_ADVISORY",
    "NON_ROOT_ADAPTER",
    "NON_ROOT_EFFECT_ENFORCEMENT",
    "NON_ROOT_BOUNDED_CORRIDOR",
    "NON_ROOT_EVIDENCE",
    "NON_ROOT_TRACE",
    "NON_ROOT_INTEGRITY",
    "NON_ROOT_RECONSTRUCTION",
    "NON_ROOT_PRESENTATION",
)
COMMITTED_ALL = (
    "CanonicalArtifactRefV01",
    "ArtifactDependencyEdgeV01",
    "RootOwnershipBindingV01",
    "EvidenceClassBindingV01",
    "AuthorityClassBindingV01",
    "SealProfileV01",
    "ArtifactManifestV01",
    "SealVerificationResultV01",
    "ReplayVerificationResultV01",
    "build_default_seal_profile_v01",
    "canonical_json_bytes_v01",
    "domain_separated_sha256_hex_v01",
    "build_canonical_artifact_ref_v01",
    "build_artifact_manifest_v01",
    "verify_artifact_manifest_v01",
    "verify_artifact_replay_v01",
    "artifact_manifest_to_plain_dict_v01",
    "seal_verification_result_to_plain_dict_v01",
    "replay_verification_result_to_plain_dict_v01",
)


@pytest.fixture
def profiles() -> tuple[trust.ComponentTrustProfileV01, ...]:
    return trust.build_default_component_trust_profiles_v01()


def test_public_dataclass_surface_is_exact() -> None:
    public_dataclasses = {
        name
        for name, value in vars(trust).items()
        if not name.startswith("_")
        and inspect.isclass(value)
        and is_dataclass(value)
        and value.__module__ == trust.__name__
    }
    assert public_dataclasses == {"ComponentTrustProfileV01"}
    assert tuple(field.name for field in fields(trust.ComponentTrustProfileV01)) == (
        EXPECTED_FIELDS
    )


def test_public_dataclass_is_frozen(profiles: tuple[trust.ComponentTrustProfileV01, ...]) -> None:
    with pytest.raises(FrozenInstanceError):
        profiles[0].component_id = "changed"  # type: ignore[misc]


def test_public_function_surface_is_exact() -> None:
    functions = {
        name
        for name, value in vars(trust).items()
        if not name.startswith("_")
        and inspect.isfunction(value)
        and value.__module__ == trust.__name__
    }
    assert functions == {
        "build_default_component_trust_profiles_v01",
        "validate_component_trust_profiles_v01",
        "component_trust_profile_to_plain_dict_v01",
        "component_trust_profiles_to_plain_list_v01",
    }


@pytest.mark.parametrize(
    "attribute",
    (
        "ComponentTrustProfileV01",
        "build_default_component_trust_profiles_v01",
        "validate_component_trust_profiles_v01",
        "component_trust_profile_to_plain_dict_v01",
        "component_trust_profiles_to_plain_list_v01",
    ),
)
def test_package_has_direct_trust_attributes(attribute: str) -> None:
    assert getattr(kernel, attribute) is getattr(trust, attribute)


def test_package_all_is_unchanged() -> None:
    assert kernel.__all__ == COMMITTED_ALL
    assert type(kernel.__all__) is tuple


@pytest.mark.parametrize("index", range(18))
def test_default_profile_identity_geometry_is_exact(
    profiles: tuple[trust.ComponentTrustProfileV01, ...], index: int
) -> None:
    profile = profiles[index]
    assert profile.component_id == EXPECTED_IDS[index]
    assert profile.component_class == EXPECTED_CLASSES[index]
    assert profile.authority_class == EXPECTED_AUTHORITY[index]


@pytest.mark.parametrize("index", range(18))
def test_every_default_profile_has_complete_descriptive_surfaces(
    profiles: tuple[trust.ComponentTrustProfileV01, ...], index: int
) -> None:
    profile = profiles[index]
    assert type(profile.trusted_inputs) is tuple and profile.trusted_inputs
    assert type(profile.untrusted_inputs) is tuple and profile.untrusted_inputs
    assert type(profile.produced_artifact_classes) is tuple
    assert profile.produced_artifact_classes
    assert type(profile.compromise_assumptions) is tuple
    assert profile.compromise_assumptions
    assert isinstance(profile.fail_closed_expectation, str)
    assert profile.fail_closed_expectation


def test_default_profile_tuple_validates_cleanly(
    profiles: tuple[trust.ComponentTrustProfileV01, ...]
) -> None:
    assert len(profiles) == 18
    assert tuple(item.component_id for item in profiles) == EXPECTED_IDS
    assert trust.validate_component_trust_profiles_v01(profiles=profiles) == ()


@pytest.mark.parametrize(
    ("flag", "expected_ids"),
    (
        ("may_create_root_decision", ("root",)),
        ("may_create_permission", ("root",)),
        ("may_request_effect", ("root",)),
        ("may_hold_effect_handle", ("effect_firewall", "corridor_adapter")),
    ),
)
def test_authority_capability_law_is_exact(
    profiles: tuple[trust.ComponentTrustProfileV01, ...],
    flag: str,
    expected_ids: tuple[str, ...],
) -> None:
    assert tuple(item.component_id for item in profiles if getattr(item, flag)) == (
        expected_ids
    )


@pytest.mark.parametrize(
    "component_id",
    (
        "provider_llm",
        "drs",
        "avf",
        "gt",
        "domain_adapter",
        "receipt",
        "ledger",
        "crypto",
        "replay",
        "renderer_showcase",
    ),
)
def test_compromised_non_root_profiles_remain_non_authoritative(
    profiles: tuple[trust.ComponentTrustProfileV01, ...], component_id: str
) -> None:
    profile = next(item for item in profiles if item.component_id == component_id)
    assert profile.may_create_root_decision is False
    assert profile.may_create_permission is False
    assert profile.may_request_effect is False
    assert profile.may_hold_effect_handle is False


@pytest.mark.parametrize("index", range(18))
def test_each_profile_projection_is_json_safe_and_independent(
    profiles: tuple[trust.ComponentTrustProfileV01, ...], index: int
) -> None:
    first = trust.component_trust_profile_to_plain_dict_v01(profiles[index])
    second = trust.component_trust_profile_to_plain_dict_v01(profiles[index])
    assert first == second
    assert json.loads(json.dumps(first, allow_nan=False)) == first
    first["trusted_inputs"].append("changed")  # type: ignore[union-attr]
    assert first != second
    assert "changed" not in profiles[index].trusted_inputs


def test_full_projection_is_json_safe_and_has_no_tuples(
    profiles: tuple[trust.ComponentTrustProfileV01, ...]
) -> None:
    projected = trust.component_trust_profiles_to_plain_list_v01(profiles)
    assert len(projected) == 18
    assert json.loads(json.dumps(projected, allow_nan=False)) == projected
    assert all(type(row["trusted_inputs"]) is list for row in projected)
    projected[0]["trusted_inputs"].append("changed")  # type: ignore[union-attr]
    assert "changed" not in profiles[0].trusted_inputs


@pytest.mark.parametrize(
    ("field_name", "bad_value"),
    (
        ("component_id", "unknown"),
        ("component_class", "WRONG"),
        ("authority_class", "WRONG"),
        ("trusted_inputs", ()),
        ("untrusted_inputs", []),
        ("produced_artifact_classes", ()),
        ("may_create_root_decision", "false"),
        ("may_create_permission", 0),
        ("may_request_effect", None),
        ("may_hold_effect_handle", 1),
        ("compromise_assumptions", ()),
        ("fail_closed_expectation", ""),
    ),
)
def test_every_profile_field_mutation_fails_validation_and_projection(
    profiles: tuple[trust.ComponentTrustProfileV01, ...],
    field_name: str,
    bad_value: object,
) -> None:
    malformed = replace(profiles[0], **{field_name: bad_value})
    mutated = (malformed, *profiles[1:])
    assert trust.validate_component_trust_profiles_v01(profiles=mutated)
    with pytest.raises(ValueError, match="^trust_profile_contract_invalid$") as exc:
        trust.component_trust_profile_to_plain_dict_v01(malformed)
    assert exc.value.__cause__ is None


@pytest.mark.parametrize(
    ("mutation", "reason"),
    (
        (lambda values: list(values), "trust_profile_tuple_invalid"),
        (lambda values: (), "trust_profile_tuple_invalid"),
        (lambda values: values[:-1], "trust_profile_set_mismatch"),
        (lambda values: (*values, values[-1]), "trust_profile_id_duplicate"),
        (lambda values: (values[1], values[0], *values[2:]), "trust_profile_order_mismatch"),
        (
            lambda values: (values[0], replace(values[1], component_id="root"), *values[2:]),
            "trust_profile_id_duplicate",
        ),
        (
            lambda values: (*values, replace(values[-1], component_id="extra")),
            "trust_profile_set_mismatch",
        ),
    ),
)
def test_profile_set_shape_mutations_fail_closed(
    profiles: tuple[trust.ComponentTrustProfileV01, ...],
    mutation: object,
    reason: str,
) -> None:
    malformed = mutation(profiles)  # type: ignore[operator]
    assert reason in trust.validate_component_trust_profiles_v01(profiles=malformed)


@pytest.mark.parametrize(
    ("index", "field_name", "reason"),
    (
        (1, "may_create_root_decision", "root_decision_authority_invalid"),
        (5, "may_create_permission", "permission_authority_invalid"),
        (6, "may_request_effect", "effect_request_authority_invalid"),
        (9, "may_hold_effect_handle", "effect_handle_boundary_invalid"),
        (11, "may_hold_effect_handle", "effect_handle_boundary_invalid"),
        (12, "may_hold_effect_handle", "effect_handle_boundary_invalid"),
        (0, "may_hold_effect_handle", "effect_handle_boundary_invalid"),
    ),
)
def test_capability_boundary_mutations_fail_closed(
    profiles: tuple[trust.ComponentTrustProfileV01, ...],
    index: int,
    field_name: str,
    reason: str,
) -> None:
    changed = list(profiles)
    current = getattr(changed[index], field_name)
    changed[index] = replace(changed[index], **{field_name: not current})
    assert reason in trust.validate_component_trust_profiles_v01(
        profiles=tuple(changed)
    )


@pytest.mark.parametrize("malformed", (object(), "profiles", 1, True, {"x": 1}))
def test_validator_never_leaks_for_malformed_top_level(malformed: object) -> None:
    errors = trust.validate_component_trust_profiles_v01(profiles=malformed)
    assert errors == ("trust_profile_tuple_invalid",)


def test_projection_rejects_malformed_profile_tuple_without_exception_repr() -> None:
    with pytest.raises(ValueError, match="^trust_profile_tuple_invalid$") as exc:
        trust.component_trust_profiles_to_plain_list_v01((object(),))  # type: ignore[arg-type]
    assert exc.value.__cause__ is None
    assert "object at" not in str(exc.value)


def test_module_has_no_forbidden_imports_or_runtime_boundaries() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported = {
        node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
    }
    imported.update(
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    )
    assert not any(name.startswith(("hedgehog.domains", "demo", "tests")) for name in imported)
    assert not any(
        name.startswith(("requests", "socket", "urllib", "os", "pathlib", "tempfile", "shutil", "subprocess"))
        for name in imported
    )


@pytest.mark.parametrize(
    "forbidden_token",
    (
        "open(",
        ".read_text(",
        ".write_text(",
        "getenv(",
        "RootDecisionV01",
        "EffectCapabilityV01",
        "TransitionRegistryV01",
        "callback=",
        "effect_hook",
        ".tmp",
    ),
)
def test_module_source_contains_no_implemented_runtime_boundary(
    forbidden_token: str,
) -> None:
    assert forbidden_token not in MODULE_PATH.read_text(encoding="utf-8")
