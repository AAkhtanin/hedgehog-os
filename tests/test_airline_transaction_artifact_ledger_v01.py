from __future__ import annotations

import ast
from copy import deepcopy
from dataclasses import replace
from pathlib import Path

import pytest

from hedgehog.domains.airline import transaction_artifact_ledger_v01 as ledger


MODULE_PATH = Path("hedgehog/domains/airline/transaction_artifact_ledger_v01.py")
EFFECT_FIELD = "real_world_effects_count"


def _valid_a() -> ledger.AirlineTransactionArtifactLedgerV01:
    return ledger.build_valid_airline_transaction_artifact_ledger_offer_a_v01()


def _valid_b() -> ledger.AirlineTransactionArtifactLedgerV01:
    return ledger.build_valid_airline_transaction_artifact_ledger_offer_b_v01()


def _report(
    item: ledger.AirlineTransactionArtifactLedgerV01,
) -> ledger.AirlineTransactionArtifactLedgerValidationReportV01:
    return ledger.validate_airline_transaction_artifact_ledger_v01(item)


def _assert_pass(item: ledger.AirlineTransactionArtifactLedgerV01) -> None:
    report = _report(item)
    assert report.validation_status == ledger.STATUS_PASS
    assert report.validation_errors == ()


def _assert_fails(
    item: ledger.AirlineTransactionArtifactLedgerV01,
    reason: str | None = None,
) -> ledger.AirlineTransactionArtifactLedgerValidationReportV01:
    report = _report(item)
    assert report.validation_status == ledger.STATUS_FAIL_CLOSED
    if reason is not None:
        assert reason in report.validation_errors
    return report


def _replace_entry(
    item: ledger.AirlineTransactionArtifactLedgerV01,
    index: int,
    **changes: object,
) -> ledger.AirlineTransactionArtifactLedgerV01:
    entries = list(item.entries)
    entries[index] = replace(entries[index], **changes)
    return replace(item, entries=tuple(entries))


def _replace_entry_effect(
    item: ledger.AirlineTransactionArtifactLedgerV01,
    index: int,
    count: int,
) -> ledger.AirlineTransactionArtifactLedgerV01:
    return _replace_entry(item, index, **{EFFECT_FIELD: count})


def _without_entry(
    item: ledger.AirlineTransactionArtifactLedgerV01,
    artifact_type: str,
) -> ledger.AirlineTransactionArtifactLedgerV01:
    entries = tuple(entry for entry in item.entries if entry.artifact_type != artifact_type)
    return replace(item, entries=entries)


def _entry_by_type(
    item: ledger.AirlineTransactionArtifactLedgerV01,
    artifact_type: str,
) -> ledger.AirlineTransactionArtifactLedgerEntryV01:
    return next(entry for entry in item.entries if entry.artifact_type == artifact_type)


def _index_by_type(item: ledger.AirlineTransactionArtifactLedgerV01) -> dict[str, int]:
    return {entry.artifact_type: entry.ledger_index for entry in item.entries}


def _mutable_json(value: object) -> object:
    if isinstance(value, dict):
        return {key: _mutable_json(item) for key, item in value.items()}
    if hasattr(value, "items"):
        return {key: _mutable_json(item) for key, item in value.items()}  # type: ignore[attr-defined]
    if isinstance(value, tuple):
        return tuple(_mutable_json(item) for item in value)
    return value


def _replace_hash_input(
    item: ledger.AirlineTransactionArtifactLedgerV01,
    index: int,
    updates: dict[str, object],
) -> ledger.AirlineTransactionArtifactLedgerV01:
    base = _mutable_json(item.entries[index].canonical_hash_input)
    assert isinstance(base, dict)
    base.update(updates)
    return _replace_entry(item, index, canonical_hash_input=base)


def _mutate_all_hash_inputs(
    item: ledger.AirlineTransactionArtifactLedgerV01,
    updates: dict[str, object],
    *,
    only_existing_keys: bool = False,
) -> ledger.AirlineTransactionArtifactLedgerV01:
    entries = []
    for entry in item.entries:
        base = _mutable_json(entry.canonical_hash_input)
        assert isinstance(base, dict)
        for key, value in updates.items():
            if not only_existing_keys or key in base:
                base[key] = value
        entries.append(replace(entry, canonical_hash_input=base))
    return replace(item, entries=tuple(entries))


def _apply_offer_profile_facts(
    item: ledger.AirlineTransactionArtifactLedgerV01,
    profile: ledger.AirlineTransactionArtifactLedgerV01,
    *,
    ledger_id_offer: str,
) -> ledger.AirlineTransactionArtifactLedgerV01:
    profile_by_type = {entry.artifact_type: entry for entry in profile.entries}
    entries = []
    for entry in item.entries:
        base = _mutable_json(entry.canonical_hash_input)
        assert isinstance(base, dict)
        source_hash = profile_by_type[entry.artifact_type].canonical_hash_input
        for key in ("selected_offer_id", "hold_id", "amount", "currency", "route_ref"):
            if key in base:
                base[key] = source_hash[key]
        entries.append(replace(entry, canonical_hash_input=base))
    return replace(
        item,
        ledger_id=f"airline_transaction_artifact_ledger:{ledger_id_offer}",
        entries=tuple(entries),
    )


def _coordinated_rename_artifact_ids(
    item: ledger.AirlineTransactionArtifactLedgerV01,
    renames: dict[str, str],
) -> ledger.AirlineTransactionArtifactLedgerV01:
    entries = []
    for entry in item.entries:
        new_artifact_id = renames.get(entry.artifact_id, entry.artifact_id)
        new_depends_on = tuple(renames.get(dep, dep) for dep in entry.depends_on)
        base = _mutable_json(entry.canonical_hash_input)
        assert isinstance(base, dict)
        base["artifact_id"] = new_artifact_id
        base["depends_on"] = new_depends_on
        entries.append(
            replace(
                entry,
                artifact_id=new_artifact_id,
                depends_on=new_depends_on,
                canonical_hash_input=base,
            )
        )
    return replace(item, entries=tuple(entries))


def test_01_valid_offer_a_ledger_passes() -> None:
    item = _valid_a()
    _assert_pass(item)
    assert item.entries[5].canonical_hash_input["selected_offer_id"] == ledger.OFFER_A_ID


def test_02_valid_offer_b_ledger_passes() -> None:
    item = _valid_b()
    _assert_pass(item)
    assert item.entries[5].canonical_hash_input["selected_offer_id"] == ledger.OFFER_B_ID


def test_03_transaction_started_is_unique_and_index_zero() -> None:
    item = _valid_a()
    entries = list(item.entries)
    entries[1] = replace(entries[1], event_type=ledger.EVENT_TRANSACTION_STARTED)
    _assert_fails(
        replace(item, entries=tuple(entries)),
        ledger.REASON_MULTIPLE_TRANSACTION_STARTED,
    )
    moved = _replace_entry(item, 0, ledger_index=1)
    _assert_fails(moved, ledger.REASON_TRANSACTION_STARTED_NOT_INDEX_ZERO)


def test_04_ledger_indexes_are_contiguous() -> None:
    _assert_fails(_replace_entry(_valid_a(), 4, ledger_index=44), ledger.REASON_NON_CONTIGUOUS_LEDGER_INDEX)


def test_05_duplicate_index_fails() -> None:
    _assert_fails(_replace_entry(_valid_a(), 2, ledger_index=1), ledger.REASON_DUPLICATE_LEDGER_INDEX)


def test_06_duplicate_artifact_id_fails() -> None:
    first_id = _valid_a().entries[1].artifact_id
    _assert_fails(_replace_entry(_valid_a(), 2, artifact_id=first_id), ledger.REASON_DUPLICATE_ARTIFACT_ID)


def test_07_mixed_transaction_id_fails() -> None:
    _assert_fails(_replace_entry(_valid_a(), 6, transaction_id="other"), ledger.REASON_MIXED_TRANSACTION_ID)


def test_08_missing_dependency_fails() -> None:
    _assert_fails(
        _replace_entry(_valid_a(), 5, depends_on=("missing:artifact",)),
        ledger.REASON_MISSING_DEPENDENCY,
    )


def test_09_later_entry_dependency_fails() -> None:
    later = _valid_a().entries[18].artifact_id
    _assert_fails(
        _replace_entry(_valid_a(), 5, depends_on=(later,)),
        ledger.REASON_DEPENDENCY_ON_LATER_ENTRY,
    )


def test_10_self_dependency_fails() -> None:
    entry = _valid_a().entries[7]
    _assert_fails(
        _replace_entry(_valid_a(), 7, depends_on=(entry.artifact_id,)),
        ledger.REASON_SELF_DEPENDENCY,
    )


def test_11_cyclic_dependency_fails() -> None:
    item = _valid_a()
    entries = list(item.entries)
    entries[6] = replace(entries[6], depends_on=(entries[7].artifact_id,))
    entries[7] = replace(entries[7], depends_on=(entries[6].artifact_id,))
    _assert_fails(replace(item, entries=tuple(entries)), ledger.REASON_CYCLIC_DEPENDENCY)


def test_12_wrong_clientroot_owner_fails() -> None:
    _assert_fails(
        _replace_entry(_valid_a(), 11, root_owner=ledger.AIRLINE_ROOT_ID),
        ledger.REASON_WRONG_ROOT_OWNER,
    )


def test_13_wrong_airlineroot_owner_fails() -> None:
    _assert_fails(
        _replace_entry(_valid_a(), 8, root_owner=ledger.CLIENT_ROOT_ID),
        ledger.REASON_WRONG_ROOT_OWNER,
    )


def test_14_wrong_bankroot_owner_fails() -> None:
    _assert_fails(
        _replace_entry(_valid_a(), 12, root_owner=ledger.CLIENT_ROOT_ID),
        ledger.REASON_WRONG_ROOT_OWNER,
    )


def test_15_cross_root_reviewer_as_fourth_root_fails() -> None:
    _assert_fails(
        _replace_entry(_valid_a(), 18, root_owner=ledger.ROOT_OWNER_BSEP_CROSS_ROOT),
        ledger.REASON_CROSS_ROOT_REVIEWER_AS_FOURTH_ROOT,
    )


@pytest.mark.parametrize(
    ("index", "reason_name"),
    [
        (8, "provider-created offer"),
        (9, "provider-created hold"),
        (11, "provider-created purchase intent"),
        (12, "provider-created payment authorization"),
        (13, "provider-created ticket intent"),
    ],
)
def test_16_to_20_provider_created_contract_artifacts_fail(index: int, reason_name: str) -> None:
    assert reason_name
    _assert_fails(
        _replace_entry(_valid_a(), index, created_by="gemini_provider_llm"),
        ledger.REASON_WRONG_CREATED_BY,
    )


def test_21_receipt_classified_as_permission_fails() -> None:
    _assert_fails(
        _replace_entry(_valid_a(), 14, authority_class="receipt_permission"),
        ledger.REASON_FORBIDDEN_CLASSIFICATION,
    )


def test_22_receipt_classified_as_authority_fails() -> None:
    _assert_fails(
        _replace_entry(_valid_a(), 10, authority_class=ledger.AUTHORITY_ROOT_OWNED_CONTRACT),
        ledger.REASON_WRONG_AUTHORITY_CLASS,
    )


def test_23_root_final_owned_by_wrong_root_fails() -> None:
    _assert_fails(
        _replace_entry(_valid_a(), 16, root_owner=ledger.BANK_ROOT_ID),
        ledger.REASON_WRONG_ROOT_OWNER,
    )


def test_24_missing_clientroot_final_fails() -> None:
    _assert_fails(
        _without_entry(_valid_a(), ledger.ARTIFACT_CLIENT_ROOT_FINAL),
        ledger.REASON_MISSING_CLIENT_ROOT_FINAL,
    )


def test_25_missing_airlineroot_final_fails() -> None:
    _assert_fails(
        _without_entry(_valid_a(), ledger.ARTIFACT_AIRLINE_ROOT_FINAL),
        ledger.REASON_MISSING_AIRLINE_ROOT_FINAL,
    )


def test_26_missing_bankroot_final_fails() -> None:
    _assert_fails(
        _without_entry(_valid_a(), ledger.ARTIFACT_BANK_ROOT_FINAL),
        ledger.REASON_MISSING_BANK_ROOT_FINAL,
    )


@pytest.mark.parametrize(
    ("payload", "reason"),
    [
        ({"raw_provider_text": "full provider text"}, ledger.REASON_UNSAFE_CANONICAL_HASH_INPUT),
        ({"raw_passport": "P123"}, ledger.REASON_UNSAFE_CANONICAL_HASH_INPUT),
        ({"card": "4111", "iban": "IBAN", "payment_token": "tok"}, ledger.REASON_UNSAFE_CANONICAL_HASH_INPUT),
    ],
)
def test_27_to_29_secret_or_raw_provider_material_in_canonical_hash_input_fails(
    payload: dict[str, str],
    reason: str,
) -> None:
    base = dict(_valid_a().entries[5].canonical_hash_input)
    base.update(payload)
    _assert_fails(_replace_entry(_valid_a(), 5, canonical_hash_input=base), reason)


def test_30_malformed_canonical_hash_input_fails() -> None:
    _assert_fails(
        _replace_entry(_valid_a(), 5, canonical_hash_input=object()),
        ledger.REASON_MALFORMED_CANONICAL_HASH_INPUT,
    )


def test_31_unknown_event_type_fails() -> None:
    _assert_fails(_replace_entry(_valid_a(), 5, event_type="unknown"), ledger.REASON_UNKNOWN_EVENT_TYPE)


def test_32_unknown_authority_class_fails() -> None:
    _assert_fails(
        _replace_entry(_valid_a(), 5, authority_class="unknown_authority"),
        ledger.REASON_UNKNOWN_AUTHORITY_CLASS,
    )


def test_33_unknown_evidence_class_fails() -> None:
    _assert_fails(
        _replace_entry(_valid_a(), 5, evidence_class="unknown_evidence"),
        ledger.REASON_UNKNOWN_EVIDENCE_CLASS,
    )


def test_34_nonzero_ledger_created_authority_fails() -> None:
    _assert_fails(
        _replace_entry(_valid_a(), 5, ledger_created_authority=True),
        ledger.REASON_LEDGER_CREATED_AUTHORITY,
    )


def test_35_nonzero_ledger_created_permission_fails() -> None:
    _assert_fails(
        _replace_entry(_valid_a(), 5, ledger_created_permission=True),
        ledger.REASON_LEDGER_CREATED_PERMISSION,
    )


def test_36_nonzero_ledger_created_action_fails() -> None:
    _assert_fails(
        _replace_entry(_valid_a(), 5, ledger_created_action=True),
        ledger.REASON_LEDGER_CREATED_ACTION,
    )


def test_37_nonzero_real_effect_fails() -> None:
    _assert_fails(
        _replace_entry_effect(_valid_a(), 5, 1),
        ledger.REASON_NONZERO_REAL_WORLD_EFFECTS,
    )


def test_38_ledger_validation_does_not_mutate_source_artifacts() -> None:
    item = _valid_a()
    before = deepcopy(item)
    _assert_pass(item)
    assert item == before


def test_39_a_b_a_isolation_passes() -> None:
    constants = (ledger.EMITTED_EVENT_TYPES, ledger.AUTHORITY_CLASSES, ledger.EVIDENCE_CLASSES)
    _assert_pass(_valid_a())
    _assert_pass(_valid_b())
    _assert_pass(_valid_a())
    assert constants == (ledger.EMITTED_EVENT_TYPES, ledger.AUTHORITY_CLASSES, ledger.EVIDENCE_CLASSES)


def test_40_b_a_b_isolation_passes() -> None:
    _assert_pass(_valid_b())
    _assert_pass(_valid_a())
    _assert_pass(_valid_b())


def test_41_raw_prompt_response_remain_auxiliary_refs_only() -> None:
    semantic = _entry_by_type(_valid_a(), ledger.ARTIFACT_VALIDATED_CANONICAL_SEMANTIC_EVIDENCE)
    assert semantic.auxiliary_artifact_refs == (
        ledger.OPAQUE_PROMPT_REF,
        ledger.OPAQUE_RESPONSE_REF,
    )
    assert all("prompt" not in ref.lower() and "response" not in ref.lower() for ref in semantic.source_validation_refs)
    _assert_fails(
        _replace_entry(_valid_a(), 5, source_validation_refs=semantic.source_validation_refs + (ledger.OPAQUE_RESPONSE_REF,)),
        ledger.REASON_RAW_PROMPT_RESPONSE_NOT_AUXILIARY_ONLY,
    )


@pytest.mark.parametrize(
    "bad_ref",
    (
        ledger.OPAQUE_PROMPT_REF,
        ledger.OPAQUE_RESPONSE_REF,
        "actor_prompt.txt",
        "actor_raw_response.txt",
        "evidence/actors/actor_prompt.txt",
        "evidence/actors/actor_raw_response.txt",
        "raw_prompt:actor:001",
        "raw_response:actor:001",
        "provider_prompt_file:actor:001",
        "provider_raw_response_file:actor:001",
    ),
)
def test_raw_prompt_response_source_refs_remain_blocked(bad_ref: str) -> None:
    item = _valid_a()
    semantic = item.entries[5]
    refs = (*semantic.source_validation_refs, bad_ref)
    item = _replace_entry(
        item,
        5,
        source_validation_refs=refs,
        canonical_hash_input={
            **dict(semantic.canonical_hash_input),
            "source_validation_refs": refs,
        },
    )
    _assert_fails(
        item,
        ledger.REASON_RAW_PROMPT_RESPONSE_NOT_AUXILIARY_ONLY,
    )


@pytest.mark.parametrize(
    "auxiliary_refs",
    (
        (ledger.OPAQUE_PROMPT_REF,),
        (ledger.OPAQUE_RESPONSE_REF,),
        (ledger.OPAQUE_RESPONSE_REF, ledger.OPAQUE_PROMPT_REF),
        (ledger.OPAQUE_PROMPT_REF, "auxiliary_artifact_ref:replacement"),
        (
            ledger.OPAQUE_PROMPT_REF,
            ledger.OPAQUE_RESPONSE_REF,
            "auxiliary_artifact_ref:third",
        ),
    ),
)
def test_canonical_semantic_auxiliary_refs_remain_exact(
    auxiliary_refs: tuple[str, ...],
) -> None:
    _assert_fails(
        _replace_entry(
            _valid_a(),
            5,
            auxiliary_artifact_refs=auxiliary_refs,
        ),
        ledger.REASON_AUXILIARY_ARTIFACT_REFS_PROFILE_MISMATCH,
    )


def test_42_canonical_semantic_entry_comes_from_validated_evidence_not_raw_response() -> None:
    semantic = _entry_by_type(_valid_a(), ledger.ARTIFACT_VALIDATED_CANONICAL_SEMANTIC_EVIDENCE)
    for required in ledger.REQUIRED_SEMANTIC_SOURCE_REFS:
        assert required in semantic.source_validation_refs
    _assert_fails(
        _replace_entry(_valid_a(), 5, source_validation_refs=(ledger.OPAQUE_RESPONSE_REF,)),
        ledger.REASON_SEMANTIC_CLAIM_MISSING_SOURCE_REFS,
    )


def test_43_human_approval_remains_evidence_and_not_ticket_payment_permission() -> None:
    purchase = _entry_by_type(_valid_a(), ledger.ARTIFACT_CLIENT_PURCHASE_INTENT)
    assert ledger.SOURCE_REF_HUMAN_APPROVAL in purchase.source_validation_refs
    assert not any(entry.artifact_type == "AirlinePurchaseApprovalEvidenceRefV01" for entry in _valid_a().entries)
    _assert_fails(
        _replace_entry(_valid_a(), 11, source_validation_refs=()),
        ledger.REASON_HUMAN_APPROVAL_NOT_SOURCE_REF,
    )


def test_44_ledger_module_imports_no_provider_network_gemini_config_demo_runner() -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    allowed_top_level_imports = {
        "__future__",
        "collections",
        "math",
        "re",
        "dataclasses",
        "types",
        "typing",
        "hedgehog",
    }
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        if isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    assert imports <= allowed_top_level_imports


def test_45_module_is_airline_domain_not_core_and_not_installed_needle() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "Airline domain projection" in source
    assert "not Hedgehog OS universal kernel/core" in source
    assert "not an installed Needle" in source
    assert "hedgehog/transaction_artifact_ledger" not in source


def test_46_lied_entry_count_fails() -> None:
    _assert_fails(replace(_valid_a(), entry_count=999), ledger.REASON_LEDGER_ENTRY_COUNT_MISMATCH)


def test_47_lied_dependency_edge_count_fails() -> None:
    _assert_fails(
        replace(_valid_a(), dependency_edge_count=999),
        ledger.REASON_LEDGER_DEPENDENCY_EDGE_COUNT_MISMATCH,
    )


def test_48_lied_event_type_counts_fails() -> None:
    _assert_fails(
        replace(_valid_a(), event_type_counts={ledger.EVENT_ROOT_FINAL_CREATED: 999}),
        ledger.REASON_LEDGER_EVENT_TYPE_COUNTS_MISMATCH,
    )


def test_49_lied_root_final_count_fails() -> None:
    _assert_fails(replace(_valid_a(), root_final_count=999), ledger.REASON_LEDGER_ROOT_FINAL_COUNT_MISMATCH)


def test_50_two_root_finals_with_stored_root_final_count_three_fails() -> None:
    item = replace(_without_entry(_valid_a(), ledger.ARTIFACT_BANK_ROOT_FINAL), root_final_count=3)
    _assert_fails(item, ledger.REASON_LEDGER_ROOT_FINAL_COUNT_MISMATCH)


def test_51_entry_created_authority_with_stored_count_zero_fails() -> None:
    item = _replace_entry(_valid_a(), 5, ledger_created_authority=True)
    item = replace(item, ledger_created_authority_count=0)
    _assert_fails(item, ledger.REASON_LEDGER_DERIVED_COUNTER_MISMATCH)


def test_52_nonzero_entry_effect_with_stored_total_zero_fails() -> None:
    item = _replace_entry_effect(_valid_a(), 5, 1)
    item = replace(item, real_world_effects_count=0)
    _assert_fails(item, ledger.REASON_LEDGER_DERIVED_COUNTER_MISMATCH)


def test_53_stored_pass_cannot_override_invalid_dependency_graph() -> None:
    item = _replace_entry(_valid_a(), 5, depends_on=("missing:artifact",))
    item = replace(item, validation_status=ledger.STATUS_PASS, validation_errors=())
    report = _assert_fails(item, ledger.REASON_MISSING_DEPENDENCY)
    assert ledger.REASON_LEDGER_STORED_VALIDATION_STATUS_MISMATCH in report.validation_errors


def test_54_ambiguous_artifact_classification_is_impossible() -> None:
    for classification in ledger.CLASSIFICATION_BY_ARTIFACT_TYPE.values():
        assert " or " not in classification
        assert classification == ledger.CLASS_CANONICAL_LEDGER_ENTRY


def test_55_every_mapped_current_artifact_has_exactly_one_classification() -> None:
    assert set(ledger.CLASSIFICATION_BY_ARTIFACT_TYPE) == set(ledger.ARTIFACT_PROFILES)
    assert len(ledger.CLASSIFICATION_BY_ARTIFACT_TYPE) == len(set(ledger.CLASSIFICATION_BY_ARTIFACT_TYPE.keys()))


def test_56_approval_evidence_is_not_assigned_a_fabricated_creator() -> None:
    item = _valid_a()
    assert all(entry.artifact_type != "AirlinePurchaseApprovalEvidenceRefV01" for entry in item.entries)
    purchase = _entry_by_type(item, ledger.ARTIFACT_CLIENT_PURCHASE_INTENT)
    assert ledger.SOURCE_REF_HUMAN_APPROVAL in purchase.source_validation_refs


def test_57_offer_hold_receipt_is_independently_present_before_purchase_intent() -> None:
    indexes = _index_by_type(_valid_a())
    assert indexes[ledger.ARTIFACT_AIRLINE_OFFER_HOLD_RECEIPT] < indexes[ledger.ARTIFACT_CLIENT_PURCHASE_INTENT]
    _assert_fails(
        _without_entry(_valid_a(), ledger.ARTIFACT_AIRLINE_OFFER_HOLD_RECEIPT),
        ledger.REASON_OFFER_HOLD_RECEIPT_NOT_BEFORE_PURCHASE_INTENT,
    )


@pytest.mark.parametrize(
    "changes",
    [
        {"event_type": ["not", "a", "string"]},
        {"depends_on": [["not-hashable"]]},
        {"source_validation_refs": (["not-string"],)},
        {"canonical_hash_input": {"bad": object()}},
        {"real_world_effects_count": True},
    ],
)
def test_malformed_nested_python_values_fail_closed_without_exception(
    changes: dict[str, object],
) -> None:
    item = _replace_entry(_valid_a(), 5, **changes)
    report = _report(item)
    assert report.validation_status == ledger.STATUS_FAIL_CLOSED


def test_reserved_human_approval_recorded_cannot_be_emitted_in_v01() -> None:
    _assert_fails(
        _replace_entry(_valid_a(), 11, event_type=ledger.EVENT_HUMAN_APPROVAL_RECORDED),
        ledger.REASON_RESERVED_EVENT_TYPE,
    )


def test_unknown_offer_fixture_input_has_no_fallback() -> None:
    with pytest.raises(ValueError, match="unknown_offer_id"):
        ledger.build_airline_transaction_artifact_ledger_fixture_v01(
            offer_id="offer:unknown",
        )


def test_canonical_hash_input_key_order_does_not_change_canonical_meaning() -> None:
    item = _valid_a()
    entry = item.entries[5]
    reordered = dict(reversed(list(entry.canonical_hash_input.items())))
    _assert_pass(_replace_entry(item, 5, canonical_hash_input=reordered))


def test_no_dynamic_or_digest_sources_exist() -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                assert (node.func.value.id, node.func.attr) not in {
                    ("datetime", "now"),
                    ("time", "time"),
                }
        if isinstance(node, ast.Import):
            imported = {alias.name.split(".")[0] for alias in node.names}
            assert imported <= {"math", "re", "dataclasses", "typing", "hedgehog"}
        if isinstance(node, ast.ImportFrom) and node.module:
            assert node.module.split(".")[0] in {
                "__future__",
                "collections",
                "math",
                "re",
                "dataclasses",
                "types",
                "typing",
                "hedgehog",
            }


def test_global_artifact_profiles_are_externally_immutable() -> None:
    assert not hasattr(ledger, "_ARTIFACT_PROFILES_DICT")
    with pytest.raises(TypeError):
        ledger.ARTIFACT_PROFILES[ledger.ARTIFACT_TRANSACTION_SCOPE] = object()  # type: ignore[index]


def test_global_classification_mapping_is_externally_immutable() -> None:
    with pytest.raises(TypeError):
        ledger.CLASSIFICATION_BY_ARTIFACT_TYPE[ledger.ARTIFACT_TRANSACTION_SCOPE] = "changed"  # type: ignore[index]


def test_ledger_event_type_counts_are_externally_immutable() -> None:
    item = _valid_a()
    with pytest.raises(TypeError):
        item.event_type_counts[ledger.EVENT_TRANSACTION_STARTED] = 99  # type: ignore[index]


def test_entry_canonical_hash_input_is_externally_immutable() -> None:
    entry = _valid_a().entries[5]
    with pytest.raises(TypeError):
        entry.canonical_hash_input["root_permission"] = "granted"  # type: ignore[index]


def test_nested_canonical_hash_input_collections_are_externally_immutable() -> None:
    entry = _valid_a().entries[5]
    depends_on = entry.canonical_hash_input["depends_on"]
    source_refs = entry.canonical_hash_input["source_validation_refs"]
    with pytest.raises(TypeError):
        depends_on[0] = "forged"  # type: ignore[index]
    with pytest.raises(TypeError):
        source_refs[0] = "forged"  # type: ignore[index]


def test_no_mutable_artifact_profile_policy_registry_source_exists() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "_ARTIFACT_PROFILES_DICT" not in source
    tree = ast.parse(source)
    for node in tree.body:
        targets: list[ast.expr] = []
        if isinstance(node, ast.Assign):
            targets = list(node.targets)
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
        for target in targets:
            if isinstance(target, ast.Name):
                assert target.id != "_ARTIFACT_PROFILES_DICT"


def test_offer_a_and_b_use_committed_root_and_sandbox_creators() -> None:
    for item in (_valid_a(), _valid_b()):
        by_type = {entry.artifact_type: entry for entry in item.entries}
        assert by_type[ledger.ARTIFACT_CLIENT_ROOT_SELECTION_DECISION].created_by == ledger.CLIENT_ROOT_ID
        assert by_type[ledger.ARTIFACT_AIRLINE_ROOT_OFFER_RESOLUTION].created_by == ledger.AIRLINE_ROOT_ID
        assert by_type[ledger.ARTIFACT_BANK_PAYMENT_AUTHORIZATION].created_by == ledger.BANK_ROOT_ID
        assert (
            by_type[ledger.ARTIFACT_AIRLINE_OFFER_HOLD_RECEIPT].created_by
            == ledger.corridor_contracts.ADAPTER_AIRLINE_HOLD_SANDBOX
        )
        assert (
            by_type[ledger.ARTIFACT_MOCK_TICKET_RECEIPT].created_by
            == ledger.corridor_contracts.ADAPTER_AIRLINE_TICKET_SANDBOX
        )
        assert (
            by_type[ledger.ARTIFACT_MOCK_PURCHASE_RECEIPT].created_by
            == ledger.CREATED_BY_CLIENT_COMPLETION_OBSERVER
        )


def test_correct_plain_dict_canonical_hash_input_is_frozen_and_passes() -> None:
    item = _valid_a()
    source_hash = dict(item.entries[5].canonical_hash_input)
    constructed = _replace_entry(item, 5, canonical_hash_input=source_hash)
    _assert_pass(constructed)
    with pytest.raises(TypeError):
        constructed.entries[5].canonical_hash_input["artifact_id"] = "forged"  # type: ignore[index]


def test_plain_dict_canonical_hash_input_nested_values_are_frozen() -> None:
    item = _valid_a()
    source_hash = dict(item.entries[5].canonical_hash_input)
    constructed = _replace_entry(item, 5, canonical_hash_input=source_hash)
    refs = constructed.entries[5].canonical_hash_input["source_validation_refs"]
    deps = constructed.entries[5].canonical_hash_input["depends_on"]
    with pytest.raises(TypeError):
        refs[0] = "forged"  # type: ignore[index]
    with pytest.raises(TypeError):
        deps[0] = "forged"  # type: ignore[index]


def test_mutating_source_canonical_dict_after_construction_does_not_change_ledger() -> None:
    item = _valid_a()
    source_hash = dict(item.entries[5].canonical_hash_input)
    constructed = _replace_entry(item, 5, canonical_hash_input=source_hash)
    source_hash["artifact_id"] = "forged"
    _assert_pass(constructed)
    assert constructed.entries[5].canonical_hash_input["artifact_id"] != "forged"


def test_correct_plain_dict_event_type_counts_is_frozen_and_passes() -> None:
    source_counts = dict(_valid_a().event_type_counts)
    constructed = replace(_valid_a(), event_type_counts=source_counts)
    _assert_pass(constructed)
    with pytest.raises(TypeError):
        constructed.event_type_counts[ledger.EVENT_TRANSACTION_STARTED] = 9  # type: ignore[index]
    report = _report(constructed)
    with pytest.raises(TypeError):
        report.event_type_counts[ledger.EVENT_TRANSACTION_STARTED] = 9  # type: ignore[index]


def test_mutating_source_event_counts_dict_after_construction_does_not_change_ledger() -> None:
    source_counts = dict(_valid_a().event_type_counts)
    constructed = replace(_valid_a(), event_type_counts=source_counts)
    source_counts[ledger.EVENT_TRANSACTION_STARTED] = 99
    _assert_pass(constructed)
    assert constructed.event_type_counts[ledger.EVENT_TRANSACTION_STARTED] == 1


@pytest.mark.parametrize(
    "updates",
    [
        {"root_permission": "granted"},
        {"provider_authority": True},
        {"arbitrary_extra_key": "extra"},
    ],
)
def test_extra_canonical_hash_input_keys_fail_for_every_entry(
    updates: dict[str, object],
) -> None:
    item = _mutate_all_hash_inputs(_valid_a(), updates)
    _assert_fails(item, ledger.REASON_CANONICAL_HASH_INPUT_KEYSET_MISMATCH)


@pytest.mark.parametrize(
    "updates",
    [
        {"selected_offer_id": ledger.OFFER_B_ID},
        {"amount": 999999},
        {"currency": "FORGED"},
        {"route_ref": "route:forged"},
    ],
)
def test_coordinated_forged_source_facts_fail(
    updates: dict[str, object],
) -> None:
    item = _mutate_all_hash_inputs(_valid_a(), updates, only_existing_keys=True)
    _assert_fails(item, ledger.REASON_CANONICAL_HASH_INPUT_SOURCE_FACT_MISMATCH)


def test_fixture_offer_a_coordinated_non_fixture_hold_id_fails_lineage() -> None:
    item = _mutate_all_hash_inputs(
        _valid_a(),
        {"hold_id": "hold:semantic_causal:001"},
        only_existing_keys=True,
    )
    _assert_fails(item, ledger.REASON_CANONICAL_SOURCE_LINEAGE_MISMATCH)


def test_selected_offer_cannot_appear_in_transaction_started() -> None:
    item = _replace_hash_input(
        _valid_a(),
        0,
        {"selected_offer_id": ledger.OFFER_A_ID},
    )
    _assert_fails(item, ledger.REASON_CANONICAL_HASH_INPUT_KEYSET_MISMATCH)


def test_hold_id_cannot_appear_before_hold_exists() -> None:
    item = _replace_hash_input(_valid_a(), 5, {"hold_id": "hold:early"})
    _assert_fails(item, ledger.REASON_CANONICAL_HASH_INPUT_KEYSET_MISMATCH)


def test_missing_required_canonical_hash_input_key_fails() -> None:
    item = _valid_a()
    base = dict(item.entries[5].canonical_hash_input)
    base.pop("artifact_id")
    item = _replace_entry(item, 5, canonical_hash_input=base)
    _assert_fails(item, ledger.REASON_CANONICAL_HASH_INPUT_KEYSET_MISMATCH)


def test_extra_source_ref_fails_even_when_hash_input_is_updated() -> None:
    item = _valid_a()
    entry = item.entries[5]
    refs = entry.source_validation_refs + ("AirlineExtraValidationRefV01:extra",)
    item = _replace_entry(
        item,
        5,
        source_validation_refs=refs,
        canonical_hash_input={
            **dict(entry.canonical_hash_input),
            "source_validation_refs": refs,
        },
    )
    _assert_fails(item, ledger.REASON_SOURCE_VALIDATION_REFS_PROFILE_MISMATCH)


@pytest.mark.parametrize(
    "bad_ref",
    [
        "source_ref:authority_permission:granted",
        "source_ref:raw_secret_payload",
    ],
)
def test_unsafe_source_ref_fails_even_when_hash_input_is_updated(
    bad_ref: str,
) -> None:
    item = _valid_a()
    entry = item.entries[5]
    refs = entry.source_validation_refs + (bad_ref,)
    item = _replace_entry(
        item,
        5,
        source_validation_refs=refs,
        canonical_hash_input={
            **dict(entry.canonical_hash_input),
            "source_validation_refs": refs,
        },
    )
    _assert_fails(item, ledger.REASON_UNSAFE_SOURCE_OR_AUXILIARY_REF)


def test_extra_auxiliary_ref_fails() -> None:
    item = _replace_entry(
        _valid_a(),
        6,
        auxiliary_artifact_refs=("auxiliary_artifact_ref:extra",),
    )
    _assert_fails(item, ledger.REASON_AUXILIARY_ARTIFACT_REFS_PROFILE_MISMATCH)


@pytest.mark.parametrize(
    ("field_name", "value", "reason"),
    [
        ("ledger_id", "", ledger.REASON_LEDGER_ID_MISMATCH),
        ("ledger_id", ["ledger"], ledger.REASON_LEDGER_ID_MISMATCH),
        ("ledger_version", "wrong", ledger.REASON_LEDGER_VERSION_MISMATCH),
        ("source_run_ref", "", ledger.REASON_LEDGER_SOURCE_REF_MISMATCH),
        ("source_causal_report_ref", "wrong", ledger.REASON_LEDGER_SOURCE_REF_MISMATCH),
        ("source_corridor_report_ref", "wrong", ledger.REASON_LEDGER_SOURCE_REF_MISMATCH),
        ("provider_called_count", False, ledger.REASON_LEDGER_MALFORMED_COUNT),
        ("validation_errors", 7, ledger.REASON_LEDGER_MALFORMED_VALIDATION_ERRORS),
    ],
)
def test_ledger_envelope_fields_are_validated(
    field_name: str,
    value: object,
    reason: str,
) -> None:
    item = replace(_valid_a(), **{field_name: value})
    _assert_fails(item, reason)


def test_expected_source_refs_are_independently_bound() -> None:
    item = _valid_a()
    expected_refs = ledger.build_airline_transaction_artifact_ledger_fixture_source_refs_v01()
    report = ledger.validate_airline_transaction_artifact_ledger_v01(
        item,
        expected_source_refs=expected_refs,
    )
    assert report.validation_status == ledger.STATUS_PASS


def test_wrong_expected_source_refs_fail_closed() -> None:
    item = _valid_a()
    expected_refs = replace(
        ledger.build_airline_transaction_artifact_ledger_fixture_source_refs_v01(),
        source_run_ref="source_run:independent_wrong_ref",
    )
    report = ledger.validate_airline_transaction_artifact_ledger_v01(
        item,
        expected_source_refs=expected_refs,
    )
    assert report.validation_status == ledger.STATUS_FAIL_CLOSED
    assert ledger.REASON_SOURCE_REF_MISMATCH in report.validation_errors
    assert ledger.REASON_LEDGER_STORED_VALIDATION_STATUS_MISMATCH in report.validation_errors


@pytest.mark.parametrize(
    "expected_refs",
    [
        object(),
        ledger.AirlineTransactionArtifactLedgerExpectedSourceRefsV01(
            source_run_ref="",
            source_causal_report_ref=ledger.SOURCE_CAUSAL_REPORT_REF_FIXTURE,
            source_corridor_report_ref=ledger.SOURCE_CORRIDOR_REPORT_REF_FIXTURE,
        ),
        ledger.AirlineTransactionArtifactLedgerExpectedSourceRefsV01(
            source_run_ref=["bad"],  # type: ignore[arg-type]
            source_causal_report_ref=ledger.SOURCE_CAUSAL_REPORT_REF_FIXTURE,
            source_corridor_report_ref=ledger.SOURCE_CORRIDOR_REPORT_REF_FIXTURE,
        ),
    ],
)
def test_malformed_expected_source_refs_fail_without_exception(
    expected_refs: object,
) -> None:
    report = ledger.validate_airline_transaction_artifact_ledger_v01(
        _valid_a(),
        expected_source_refs=expected_refs,  # type: ignore[arg-type]
    )
    assert report.validation_status == ledger.STATUS_FAIL_CLOSED
    assert ledger.REASON_SOURCE_REF_MISMATCH in report.validation_errors


@pytest.mark.parametrize(
    ("index", "changes"),
    [
        (5, {"artifact_id": ["artifact"]}),
        (5, {"artifact_type": ["artifact_type"]}),
        (5, {"transaction_id": ["transaction"]}),
        (5, {"root_owner": ["root"]}),
        (5, {"created_by": ["creator"]}),
        (5, {"depends_on": (["dependency"],)}),
        (5, {"source_validation_refs": (["source"],)}),
        (5, {"auxiliary_artifact_refs": (["aux"],)}),
    ],
)
def test_malformed_entry_fields_fail_without_exception(
    index: int,
    changes: dict[str, object],
) -> None:
    report = _report(_replace_entry(_valid_a(), index, **changes))
    assert report.validation_status == ledger.STATUS_FAIL_CLOSED


@pytest.mark.parametrize(
    "changes",
    [
        {"transaction_id": ["transaction"]},
        {"event_type_counts": [("event", 1)]},
        {"validation_errors": 7},
        {"entries": _valid_a().entries + (object(),)},
    ],
)
def test_malformed_ledger_fields_fail_without_exception(
    changes: dict[str, object],
) -> None:
    report = _report(replace(_valid_a(), **changes))
    assert report.validation_status == ledger.STATUS_FAIL_CLOSED


def test_invalid_calendar_timestamp_fails_closed() -> None:
    _assert_fails(
        _replace_entry(_valid_a(), 5, event_time="2026-99-99T99:99:99Z"),
        ledger.REASON_MALFORMED_TIMESTAMP,
    )


def test_inconsistent_deterministic_timestamp_fails_closed() -> None:
    _assert_fails(
        _replace_entry(_valid_a(), 5, recorded_at="2026-07-12T11:00:00Z"),
        ledger.REASON_MALFORMED_TIMESTAMP,
    )


def test_complete_b_facts_with_unchanged_a_artifact_ids_fail() -> None:
    item = _apply_offer_profile_facts(
        _valid_a(),
        _valid_b(),
        ledger_id_offer=ledger.OFFER_B_ID,
    )
    _assert_fails(item, ledger.REASON_ARTIFACT_ID_SOURCE_FACT_MISMATCH)


def test_complete_a_facts_with_unchanged_b_artifact_ids_fail() -> None:
    item = _apply_offer_profile_facts(
        _valid_b(),
        _valid_a(),
        ledger_id_offer=ledger.OFFER_A_ID,
    )
    _assert_fails(item, ledger.REASON_ARTIFACT_ID_SOURCE_FACT_MISMATCH)


def test_renaming_all_artifact_ids_and_dependencies_fails() -> None:
    item = _valid_a()
    renames = {
        entry.artifact_id: f"forged_artifact:{entry.ledger_index:02d}"
        for entry in item.entries
    }
    item = _coordinated_rename_artifact_ids(item, renames)
    _assert_fails(item, ledger.REASON_ARTIFACT_ID_SOURCE_FACT_MISMATCH)


def test_renaming_one_offer_specific_artifact_id_and_references_fails() -> None:
    item = _valid_a()
    hold = _entry_by_type(item, ledger.ARTIFACT_AIRLINE_HOLD_PACKET)
    item = _coordinated_rename_artifact_ids(
        item,
        {hold.artifact_id: "forged_hold_artifact:001"},
    )
    _assert_fails(item, ledger.REASON_ARTIFACT_ID_SOURCE_FACT_MISMATCH)


def test_renaming_fixed_bsep_artifact_id_and_references_fails() -> None:
    item = _valid_a()
    bsep = _entry_by_type(item, ledger.ARTIFACT_AIRLINE_BSEP_PROJECTION)
    item = _coordinated_rename_artifact_ids(
        item,
        {bsep.artifact_id: "forged_bsep_projection:airline"},
    )
    _assert_fails(item, ledger.REASON_ARTIFACT_ID_SOURCE_FACT_MISMATCH)


def test_valid_a_and_b_counts_remain_fixed() -> None:
    for item in (_valid_a(), _valid_b()):
        report = _report(item)
        assert report.validation_status == ledger.STATUS_PASS
        assert report.entry_count == 19
        assert report.dependency_edge_count == 29
        assert report.root_final_count == 3


def test_positive_source_markers_present() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    for token in (
        "AirlineTransactionArtifactLedgerEntryV01",
        "AirlineTransactionArtifactLedgerV01",
        "AirlineTransactionArtifactLedgerValidationReportV01",
        "transaction_started",
        "semantic_claim_created",
        "bsep_projection_created",
        "client_root_selection_decided",
        "airline_root_offer_resolved",
        "offer_hold_receipt_created",
        "Independent derived-field recomputation behavior",
        "ledger_entry_count_mismatch",
        "ledger_event_type_counts_mismatch",
        "Ledger records trace",
        "Ledger does not authorize",
        "not Hedgehog OS universal kernel/core",
        "not an installed Needle",
    ):
        assert token in source


def test_forbidden_source_boundaries_absent() -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        assert not isinstance(node, (ast.With, ast.AsyncWith))
        assert not (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "open"
        )
