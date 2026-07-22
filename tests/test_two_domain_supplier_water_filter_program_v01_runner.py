from __future__ import annotations

import copy
from dataclasses import FrozenInstanceError, fields, replace
import inspect
import json
import os
from pathlib import Path
import stat
from typing import Any

import pytest

from demo import run_full_wow_v1_2_manual_live_multillm_fractal_trace as live
from demo import run_two_domain_supplier_water_filter_program_v01 as runner
from hedgehog.domains.supplier_water_filter import kernel_adapter_v01 as kernel
from hedgehog.domains.supplier_water_filter import live_evidence_adapter_v01 as safe


HEAD = "4024ee41fb37452456eae991cf1ade6e6af5c43b"


def _provider(role: str, prompt: str, context: dict[str, Any]) -> str:
    assert type(prompt) is str and prompt
    if role == "top_level_orchestrator_llm":
        value = copy.deepcopy(live.ORCHESTRATOR_JSON_SKELETON)
    elif role == "top_level_semantic_architect_llm":
        value = copy.deepcopy(live.ARCHITECT_JSON_SKELETON)
    else:
        value = copy.deepcopy(live.BRANCH_SEMANTIC_JSON_SKELETON)
        value["source_branch_id"] = context["source_branch_id"]
    return json.dumps(value, sort_keys=True)


def _collect():
    return runner.collect_two_domain_supplier_water_filter_program_v01(
        provider=_provider,
        execution_head=HEAD,
        owner_approved_supplier_a=True,
    )


def _source_report(provider=_provider) -> dict[str, object]:
    return live.collect_full_wow_v1_2_manual_live_multillm_fractal_trace(
        env={live.ENABLE_ENV: "1", live.CALL_DELAY_ENV: "0"},
        provider=provider,
    )


def _rehash_scenario(value, **changes):
    provisional = replace(value, scenario_result_id="0" * 64, **changes)
    return replace(
        provisional,
        scenario_result_id=runner._identity(
            runner._SCENARIO_DOMAIN,
            runner._scenario_plain(provisional, zero_id=True),
        ),
    )


def _rehash_result(value, **changes):
    provisional = replace(value, result_id="0" * 64, **changes)
    return replace(
        provisional,
        result_id=runner._identity(
            runner._RESULT_DOMAIN,
            runner._result_plain(provisional, zero_id=True),
        ),
    )


def _real_result(value):
    return _rehash_result(
        value,
        execution_mode=runner.MODE_REAL,
        provider_mode=runner.MODE_REAL,
        official_evidence_eligible=True,
        provider_call_count=6,
        network_call_count=6,
        gemini_call_count=6,
    )


def _real_source_report(provider=_provider) -> dict[str, object]:
    report = _source_report(provider)
    report["provider_mode"] = runner.MODE_REAL
    counters = report["counters"]
    counters["fake_provider_call_count"] = 0
    counters["real_provider_call_count"] = 6
    counters["network_used_count"] = 6
    counters["gemini_called_count"] = 6
    return report


def _restore_attempt_permissions(root: Path) -> None:
    if not root.exists():
        return
    raw = root / runner.RAW_ATTEMPT_DIRECTORY
    if raw.exists():
        os.chmod(raw, 0o700)
    os.chmod(root, 0o700)


@pytest.fixture(scope="module")
def result():
    value = _collect()
    assert runner.validate_supplier_s1_program_result_v01(value) == ()
    return value


@pytest.fixture(autouse=True)
def isolated_canonical_report(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    path = tmp_path / "supplier_safe_execution_report_v01.json"
    monkeypatch.setattr(runner, "CANONICAL_SAFE_REPORT_PATH", path)
    yield path
    assert not path.exists()


def test_public_constants_are_exact() -> None:
    assert runner.MODULE_ID == "two_domain_supplier_water_filter_program_v01"
    assert runner.GATE_ID == "two_domain_all_real_sealed_evidence_program_v01_s1_supplier_live"
    assert runner.MODEL_ID == "gemini-2.5-flash"
    assert runner.ACTOR_IDS == safe.ACTOR_IDS
    assert runner.SCENARIO_IDS == ("S-N1", "S-C1", "S-P1", "S-P2", "S-M1")


def test_public_callable_api_is_present() -> None:
    assert inspect.isfunction(runner.collect_two_domain_supplier_water_filter_program_v01)
    assert inspect.isfunction(runner.validate_supplier_s1_program_result_v01)
    assert inspect.isfunction(runner.supplier_s1_program_result_to_plain_dict_v01)
    assert inspect.signature(runner.collect_two_domain_supplier_water_filter_program_v01).parameters.keys() == {
        "provider",
        "execution_head",
        "owner_approved_supplier_a",
        "execution_mode",
        "artifact_directory",
    }


def test_result_and_scenario_are_immutable_and_slotted(result) -> None:
    assert runner.SupplierS1ProgramResultV01.__dataclass_params__.frozen
    assert runner.SupplierS1ScenarioResultV01.__dataclass_params__.frozen
    assert "__slots__" in vars(runner.SupplierS1ProgramResultV01)
    with pytest.raises(FrozenInstanceError):
        result.business_outcome = "PASS"


def test_result_field_order_is_stable() -> None:
    names = tuple(item.name for item in fields(runner.SupplierS1ProgramResultV01))
    assert names[0:9] == (
        "result_id",
        "result_version",
        "programme_id",
        "gate_id",
        "domain_id",
        "execution_head",
        "implementation_sha256",
        "attempt_number",
        "execution_mode",
    )
    assert names[-4:] == (
        "raw_prompt_included",
        "raw_provider_response_included",
        "secret_scan_passed",
        "validation_errors",
    )


def test_exact_actor_order_and_one_collection(result) -> None:
    assert result.actor_ids == (
        "top_level_orchestrator_llm",
        "top_level_semantic_architect_llm",
        "legal_clause_semantic_extractor",
        "accounting_mismatch_semantic_explainer",
        "supplier_b_unstructured_note_interpreter",
        "bank_policy_semantic_reviewer",
    )
    assert result.actor_validation_statuses == ("PASS",) * 6
    assert result.collector_invocation_count == 1
    assert result.callback_count == 6
    assert result.provider_start_count == 6
    assert result.provider_completion_count == 6


def test_injected_mode_has_zero_external_operations(result) -> None:
    assert result.execution_mode == runner.MODE_INJECTED
    assert result.provider_mode == "fake_injected"
    assert (
        result.provider_call_count,
        result.network_call_count,
        result.gemini_call_count,
        result.real_world_effects_count,
    ) == (0, 0, 0, 0)
    assert not result.official_evidence_eligible


def test_no_duplicate_retry_or_fallback(result) -> None:
    assert (result.duplicate_call_count, result.retry_count, result.fallback_call_count) == (0, 0, 0)


def test_only_one_collector_and_one_product_trace(monkeypatch: pytest.MonkeyPatch) -> None:
    observed = {"collector": 0, "product": 0}
    original_collector = runner._live.collect_full_wow_v1_2_manual_live_multillm_fractal_trace
    original_product = runner.collect_full_wow_v1_2_product_trace

    def collect_once(*args: Any, **kwargs: Any):
        observed["collector"] += 1
        return original_collector(*args, **kwargs)

    def product_once():
        observed["product"] += 1
        return original_product()

    monkeypatch.setattr(runner._live, "collect_full_wow_v1_2_manual_live_multillm_fractal_trace", collect_once)
    monkeypatch.setattr(runner, "collect_full_wow_v1_2_product_trace", product_once)
    assert _collect().final_status == "PASS"
    assert observed == {"collector": 1, "product": 1}


def test_s_n1_exact_not_ready_blocked_held_state(result) -> None:
    row = result.scenarios[0]
    assert row.scenario_id == "S-N1"
    assert row.root_status == "NOT_READY"
    assert row.supplier_a_status == "BLOCKED_PENDING_CORRECTION"
    assert row.supplier_b_status == "BLOCKED"
    assert row.shipment_status == "HELD"
    assert (row.packet_status, row.corridor_status, row.receipt_status) == (
        "ABSENT",
        "NOT_ENTERED",
        "ABSENT",
    )
    assert "product_trace:/secret_membrane/payment_slot_boundary" in row.evidence_refs
    assert row.validated_facts == (
        "warehouse_shortage_visible",
        "legal_or_insurance_missing_invalid_or_expired_visible",
        "supplier_b_invoice_mismatch_or_delay_visible",
        "payment_slot_is_not_permission",
    )


def test_s_c1_is_fresh_validation_without_calls(result) -> None:
    row = result.scenarios[1]
    assert row.scenario_id == "S-C1"
    assert row.root_status == "SUPPLIER_A_SCOPED_REVIEW_READY"
    assert row.supplier_a_status == "SUPPLIER_A_SCOPED_REVIEW_READY"
    assert row.supplier_b_status == "BLOCKED"
    assert row.shipment_status == "HELD"
    assert row.packet_status == "ABSENT"
    assert "product_trace:/transition_cards/corrected_evidence_received" in row.evidence_refs
    assert (
        row.additional_provider_call_count,
        row.additional_network_call_count,
        row.additional_gemini_call_count,
    ) == (0, 0, 0)


def test_s_p1_is_explicit_root_only_scoped_approval(result) -> None:
    row = result.scenarios[2]
    assert row.scenario_id == "S-P1"
    assert row.packet_status == "ROOT_CREATED_SCOPED"
    assert row.supplier_a_status == "APPROVED_SCOPE_ONLY"
    assert row.supplier_b_status == "BLOCKED"
    assert row.shipment_status == "HELD"
    assert result.root_created_action_commit_packet_count == 1
    assert row.validated_facts == (
        "amount_checked",
        "beneficiary_checked",
        "bank_policy_checked",
        "payment_slot_checked",
        "adapter_checked",
        "expiry_checked",
        "forbidden_subjects_checked",
        "forbidden_actions_checked",
    )


def test_s_p2_exact_scoped_supplier_a_mock_payment_path(result) -> None:
    row = result.scenarios[3]
    assert row.scenario_name == "supplier_a_mock_bank_happy_path"
    assert row.packet_status == "VALID_SCOPED"
    assert row.corridor_status == "PASS"
    assert row.receipt_status == "EVIDENCE_ONLY"
    assert result.corridor_execution_count == 1
    assert result.receipt_validation_count == 1
    assert not row.real_payment_executed
    assert not row.real_shipment_released


def test_s_m1_preserves_mixed_outcome(result) -> None:
    row = result.scenarios[4]
    assert row.scenario_id == "S-M1"
    assert row.validation_status == "PASS"
    assert row.business_outcome == "MIXED"
    assert row.supplier_a_status == "PASS"
    assert row.supplier_b_status == "BLOCKED"
    assert row.shipment_status == "HELD"
    assert row.receipt_status == "EVIDENCE_ONLY"
    assert result.business_outcome == "MIXED"


@pytest.mark.parametrize("row_index", range(5))
def test_every_s1_row_adds_zero_calls_and_effects(result, row_index: int) -> None:
    row = result.scenarios[row_index]
    assert (
        row.additional_provider_call_count,
        row.additional_network_call_count,
        row.additional_gemini_call_count,
        row.real_world_effects_count,
    ) == (0, 0, 0, 0)


def test_s2_rows_are_not_synthesized(result) -> None:
    assert not {"S-N2", "S-F1", "S-F2", "S-F3"}.intersection(result.actor_ids)
    assert tuple(item.scenario_id for item in result.scenarios) == runner.SCENARIO_IDS


def test_kernel_adapter_is_built_and_validated(result) -> None:
    assert len(result.kernel_adapter_id) == 64
    assert result.kernel_validation_status == "PASS"


def test_product_trace_kernel_public_api_passes() -> None:
    source = runner.collect_full_wow_v1_2_product_trace()
    built = kernel.build_supplier_water_filter_kernel_adapter_result_v01(source_report=source)
    assert kernel.validate_supplier_water_filter_kernel_adapter_result_v01(
        source_report=source,
        result=built,
    ) == ()
    assert built.multiroot_outcome.outcome_status == "MIXED"


def test_root_and_action_scope_are_validated_from_live_source() -> None:
    report = _source_report()
    source, statuses = runner._validate_live_report(report, runner.MODE_INJECTED)
    packet = source["action_commit_packet_v0_2_integration"]
    assert statuses == ("PASS",) * 6
    assert packet["created_by"] == "root"
    assert packet["allowed_subjects"] == ("supplier_a_adriatic_filters",)
    assert "supplier_b_balkan_pumps" in packet["forbidden_subjects"]
    assert "shipment_release" in packet["forbidden_actions"]
    assert "real_bank" in packet["forbidden_adapters"]


def test_mock_corridor_exact_sequence_is_observed() -> None:
    report = _source_report()
    corridor = report["mock_bank_sandbox_v0_2_corridor_execution"]
    outputs = tuple(item["step_id"] for item in corridor["corridor_sequence"])
    assert "mock_payment_intent_consent" in outputs
    assert "mock_payment_order" in outputs
    assert "mock_receipt_evidence" in outputs
    assert "terminal_receipt_observation" in outputs
    assert corridor["receipt_evidence_only"] is True
    assert corridor["real_payment_executed"] is False


def test_owner_approval_is_required_before_collector(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []
    monkeypatch.setattr(
        runner._live,
        "collect_full_wow_v1_2_manual_live_multillm_fractal_trace",
        lambda **kwargs: calls.append("collector"),
    )
    with pytest.raises(ValueError, match=runner.REASON_APPROVAL_REQUIRED):
        runner.collect_two_domain_supplier_water_filter_program_v01(
            provider=_provider,
            execution_head=HEAD,
            owner_approved_supplier_a=False,
        )
    assert calls == []


def test_mode_mismatch_fails_before_collection(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []
    monkeypatch.setattr(
        runner._live,
        "collect_full_wow_v1_2_manual_live_multillm_fractal_trace",
        lambda **kwargs: calls.append("collector"),
    )
    with pytest.raises(ValueError, match=runner.REASON_INVALID):
        runner.collect_two_domain_supplier_water_filter_program_v01(
            provider=_provider,
            execution_head=HEAD,
            owner_approved_supplier_a=True,
            execution_mode=runner.MODE_REAL,
        )
    assert calls == []


@pytest.mark.parametrize("head", ("", "abc", "G" * 40, "0" * 39, "0" * 41))
def test_execution_head_is_strict(head: str) -> None:
    with pytest.raises(ValueError, match=runner.REASON_INVALID):
        runner.collect_two_domain_supplier_water_filter_program_v01(
            provider=_provider,
            execution_head=head,
            owner_approved_supplier_a=True,
        )


def test_invalid_source_blocks_scenario_construction(monkeypatch: pytest.MonkeyPatch) -> None:
    report = _source_report()
    report["post_vv_gt_root"]["root_first_decision"] = "PASS"
    product_calls: list[str] = []
    monkeypatch.setattr(
        runner._live,
        "collect_full_wow_v1_2_manual_live_multillm_fractal_trace",
        lambda **kwargs: report,
    )
    monkeypatch.setattr(
        runner,
        "collect_full_wow_v1_2_product_trace",
        lambda: product_calls.append("called"),
    )
    with pytest.raises(ValueError, match=runner.REASON_SOURCE_INVALID):
        _collect()
    assert product_calls == []


@pytest.mark.parametrize(
    ("section", "key", "value"),
    (
        ("post_vv_gt_root", "supplier_b_final_status", "PASS"),
        ("post_vv_gt_root", "shipment_final_status", "RELEASED"),
        ("action_commit_packet_v0_2_integration", "root_created", False),
        ("action_commit_packet_v0_2_integration", "allowed_subjects", ("supplier_b_balkan_pumps",)),
        ("mock_bank_sandbox_v0_2_corridor_execution", "receipt_evidence_only", False),
        ("mock_bank_sandbox_v0_2_corridor_execution", "real_payment_executed", True),
    ),
)
def test_authority_or_effect_mutation_fails_closed(section: str, key: str, value: object) -> None:
    report = _source_report()
    report[section][key] = value
    with pytest.raises(ValueError, match=runner.REASON_SOURCE_INVALID):
        runner._validate_live_report(report, runner.MODE_INJECTED)


def test_wrong_actor_order_fails_closed() -> None:
    report = _source_report()
    rows = list(report["semantic_actor_calls"])
    rows[0], rows[1] = rows[1], rows[0]
    report["semantic_actor_calls"] = tuple(rows)
    with pytest.raises(ValueError, match=runner.REASON_SOURCE_INVALID):
        runner._validate_live_report(report, runner.MODE_INJECTED)


def test_real_mode_budget_law_without_real_call() -> None:
    report = _source_report()
    report["provider_mode"] = "real_provider"
    counters = report["counters"]
    counters["fake_provider_call_count"] = 0
    counters["real_provider_call_count"] = 6
    counters["network_used_count"] = 6
    counters["gemini_called_count"] = 6
    source, _ = runner._validate_live_report(report, runner.MODE_REAL)
    projection = safe.build_supplier_water_filter_safe_execution_projection_v01(
        runner._safe_execution_source(source, HEAD)
    )
    assert safe.validate_supplier_water_filter_safe_execution_projection_v01(projection) == ()
    assert (projection.provider_call_count, projection.network_call_count, projection.gemini_call_count) == (6, 6, 6)


def test_public_safe_serialization_is_canonical_and_bounded(result) -> None:
    plain = runner.supplier_s1_program_result_to_plain_dict_v01(result)
    encoded = runner._canonical_line(plain)
    assert encoded.endswith(b"\n") and not encoded.endswith(b"\n\n")
    assert json.loads(encoded) == plain
    text = encoded.decode("utf-8")
    for forbidden in (
        '"raw_prompt":',
        '"raw_response":',
        '"provider_response":',
        "GEMINI_API_KEY",
        "/Users/",
        "Traceback",
        "object at 0x",
    ):
        assert forbidden not in text


def test_serialized_summaries_do_not_claim_authority(result) -> None:
    plain = runner.supplier_s1_program_result_to_plain_dict_v01(result)
    decoded = tuple(json.loads(item) for item in plain["actor_safe_summaries"])
    assert decoded == runner._accepted_semantic_objects(_source_report())
    assert all(item["authority_claimed"] is False for item in decoded)
    assert plain["supplier_b_status"] == "BLOCKED"
    assert plain["shipment_status"] == "HELD"
    assert plain["business_outcome"] == "MIXED"


def test_result_identity_detects_mutation(result) -> None:
    changed = replace(result, business_outcome="PASS")
    assert runner.validate_supplier_s1_program_result_v01(changed) == (
        runner.REASON_SOURCE_INVALID,
        runner.REASON_INVALID,
    )


def test_scenario_identity_detects_mutation(result) -> None:
    changed_row = replace(result.scenarios[0], root_status="PASS")
    changed = replace(result, scenarios=(changed_row, *result.scenarios[1:]))
    assert runner.REASON_INVALID in runner.validate_supplier_s1_program_result_v01(changed)


def test_rehashed_forged_scenario_state_is_rejected(result) -> None:
    changed_row = _rehash_scenario(result.scenarios[0], supplier_b_status="PASS")
    changed = _rehash_result(result, scenarios=(changed_row, *result.scenarios[1:]))
    assert runner.REASON_SOURCE_INVALID in runner.validate_supplier_s1_program_result_v01(changed)


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("bsep_status", "FAIL_CLOSED"),
        ("first_root_status", "PASS"),
        ("kernel_validation_status", "FAIL_CLOSED"),
        ("root_created_action_commit_packet_count", 2),
        ("receipt_validation_count", 0),
    ),
)
def test_rehashed_forged_programme_claim_is_rejected(result, field: str, value: object) -> None:
    changed = _rehash_result(result, **{field: value})
    assert runner.validate_supplier_s1_program_result_v01(changed)


def test_rehashed_forged_kernel_identity_and_reference_are_rejected(result) -> None:
    forged_id = "f" * 64
    changed_row = _rehash_scenario(
        result.scenarios[4],
        evidence_refs=(
            f"kernel_adapter:{forged_id}",
            *result.scenarios[4].evidence_refs[1:],
        ),
    )
    changed = _rehash_result(
        result,
        kernel_adapter_id=forged_id,
        scenarios=(*result.scenarios[:4], changed_row),
    )
    assert runner.REASON_KERNEL_INVALID in runner.validate_supplier_s1_program_result_v01(changed)


@pytest.mark.parametrize(
    "counter",
    (
        "action_commit_packet_v0_2_root_created_model_packet_count",
        "mock_bank_sandbox_v0_2_receipt_validated_count",
    ),
)
def test_every_copied_source_counter_is_validated(counter: str) -> None:
    report = _source_report()
    report["counters"][counter] = 2
    with pytest.raises(ValueError, match=runner.REASON_SOURCE_INVALID):
        runner._validate_live_report(report, runner.MODE_INJECTED)


def test_boolean_counter_cannot_pass_as_integer(result) -> None:
    changed = _rehash_result(result, callback_count=True)
    assert runner.REASON_SOURCE_INVALID in runner.validate_supplier_s1_program_result_v01(changed)


def test_scenario_construction_is_bound_to_validated_source_evidence() -> None:
    source = _source_report()
    product = runner.collect_full_wow_v1_2_product_trace()
    kernel_result = kernel.build_supplier_water_filter_kernel_adapter_result_v01(
        source_report=product
    )
    original = runner._build_scenarios(source, product, kernel_result)
    changed = copy.deepcopy(product)
    row = next(
        item
        for item in changed["transition_cards"]
        if item["step_id"] == "corrected_evidence_received"
    )
    row["next_step"] = "final_state_summary"
    with pytest.raises(ValueError, match=runner.REASON_SOURCE_INVALID):
        runner._build_scenarios(source, changed, kernel_result)
    assert original[1].root_status == "SUPPLIER_A_SCOPED_REVIEW_READY"


def test_distinct_valid_semantics_change_only_matching_safe_material() -> None:
    def changed_provider(role: str, prompt: str, context: dict[str, Any]) -> str:
        value = json.loads(_provider(role, prompt, context))
        if role == "legal_clause_semantic_extractor":
            value["semantic_summary"] = "Legal evidence remains bounded and advisory for Root review."
        return json.dumps(value, sort_keys=True)

    first = _collect()
    second = runner.collect_two_domain_supplier_water_filter_program_v01(
        provider=changed_provider,
        execution_head=HEAD,
        owner_approved_supplier_a=True,
    )
    changed_summary_indexes = tuple(
        index
        for index, (left, right) in enumerate(
            zip(first.actor_safe_summaries, second.actor_safe_summaries, strict=True)
        )
        if left != right
    )
    first_projection = safe.build_supplier_water_filter_safe_execution_projection_v01(
        runner._safe_execution_source(_real_source_report(), HEAD)
    )
    second_projection = safe.build_supplier_water_filter_safe_execution_projection_v01(
        runner._safe_execution_source(_real_source_report(changed_provider), HEAD)
    )
    changed_projection_indexes = tuple(
        index
        for index, (left, right) in enumerate(
            zip(
                first_projection.actor_safe_projection_hashes,
                second_projection.actor_safe_projection_hashes,
                strict=True,
            )
        )
        if left != right
    )
    assert changed_summary_indexes == (2,)
    assert changed_projection_indexes == (2,)
    assert first.result_id != second.result_id
    assert first_projection.safe_execution_id != second_projection.safe_execution_id


@pytest.mark.parametrize(
    "additional_key",
    (
        "raw_prompt",
        "raw_response",
        "provider_response",
        "credential",
        "api_key",
        "private_material",
    ),
)
@pytest.mark.parametrize("surface", ("orchestrator", "architect", "branch"))
def test_additional_provider_semantic_field_fails_closed_without_publication(
    additional_key: str,
    surface: str,
    isolated_canonical_report: Path,
) -> None:
    def provider(role: str, prompt: str, context: dict[str, Any]) -> str:
        value = json.loads(_provider(role, prompt, context))
        selected = (
            surface == "orchestrator" and role == runner.ACTOR_IDS[0]
        ) or (
            surface == "architect" and role == runner.ACTOR_IDS[1]
        ) or (
            surface == "branch" and role == runner.ACTOR_IDS[2]
        )
        if selected:
            value[additional_key] = "untrusted-extra-field"
        return json.dumps(value, sort_keys=True)

    with pytest.raises(ValueError, match=runner.REASON_SOURCE_INVALID):
        runner.collect_two_domain_supplier_water_filter_program_v01(
            provider=provider,
            execution_head=HEAD,
            owner_approved_supplier_a=True,
        )
    assert not isolated_canonical_report.exists()


def test_safe_projection_receives_semantic_objects_not_serialized_json() -> None:
    source = runner._safe_execution_source(_real_source_report(), HEAD)
    actors = source["actors"]
    semantics = runner._accepted_semantic_objects(_real_source_report())
    assert len(actors) == 6
    for row, semantic in zip(actors, semantics, strict=True):
        projection = row["safe_projection"]
        assert type(projection["canonical_semantics"]) is dict
        assert "canonical_semantics_json" not in projection
        reconstructed = {
            field["field_name"]: field["field_value"]
            for field in projection["canonical_semantics"]["ordered_fields"]
        }
        assert reconstructed == semantic


def test_safe_projection_counts_are_read_from_validated_source() -> None:
    source = runner._safe_execution_source(_source_report(), HEAD)
    assert source["counters"] == {
        "provider_call_count": 0,
        "network_call_count": 0,
        "gemini_call_count": 0,
    }


def test_rehashed_summary_with_additional_semantic_key_is_rejected(result) -> None:
    semantic = json.loads(result.actor_safe_summaries[0])
    semantic["private_material"] = "untrusted-extra-field"
    summaries = (
        runner._semantic_summary(semantic),
        *result.actor_safe_summaries[1:],
    )
    changed = _rehash_result(result, actor_safe_summaries=summaries)
    assert runner.REASON_SOURCE_INVALID in runner.validate_supplier_s1_program_result_v01(changed)


def test_publication_rejects_result_and_report_from_different_valid_runs(
    isolated_canonical_report: Path,
) -> None:
    def changed_provider(role: str, prompt: str, context: dict[str, Any]) -> str:
        value = json.loads(_provider(role, prompt, context))
        if role == "legal_clause_semantic_extractor":
            value["semantic_summary"] = "Distinct valid legal semantics remain advisory."
        return json.dumps(value, sort_keys=True)

    first_result, first_report = runner._collect_with_context(
        provider=_provider,
        execution_head=HEAD,
        owner_approved_supplier_a=True,
    )
    second_result, second_report = runner._collect_with_context(
        provider=changed_provider,
        execution_head=HEAD,
        owner_approved_supplier_a=True,
    )
    assert runner.validate_supplier_s1_program_result_v01(first_result) == ()
    assert runner.validate_supplier_s1_program_result_v01(second_result) == ()
    assert first_result.actor_safe_summaries != second_result.actor_safe_summaries
    with pytest.raises(ValueError, match=runner.REASON_SOURCE_INVALID):
        runner._build_public_report(first_result, second_report)
    with pytest.raises(ValueError, match=runner.REASON_SOURCE_INVALID):
        runner._build_public_report(second_result, first_report)
    assert not isolated_canonical_report.exists()


def test_generic_advisory_templates_are_absent(result) -> None:
    forbidden = "reviewed as advisory evidence"
    assert all(forbidden not in summary.casefold() for summary in result.actor_safe_summaries)
    assert forbidden not in Path(runner.__file__).read_text(encoding="utf-8").casefold()


def test_repeated_injected_runs_are_deterministically_equal() -> None:
    assert _collect() == _collect()


def test_provider_result_type_failure_is_sanitized() -> None:
    def bad_provider(role: str, prompt: str, context: dict[str, Any]):
        return None

    with pytest.raises(ValueError, match=runner.REASON_SOURCE_INVALID):
        runner.collect_two_domain_supplier_water_filter_program_v01(
            provider=bad_provider,
            execution_head=HEAD,
            owner_approved_supplier_a=True,
        )


def test_provider_exception_causes_no_retry() -> None:
    calls: list[str] = []

    def bad_provider(role: str, prompt: str, context: dict[str, Any]) -> str:
        calls.append(role)
        raise RuntimeError("private-value")

    with pytest.raises(ValueError, match=runner.REASON_SOURCE_INVALID):
        runner.collect_two_domain_supplier_water_filter_program_v01(
            provider=bad_provider,
            execution_head=HEAD,
            owner_approved_supplier_a=True,
        )
    assert calls == [runner.ACTOR_IDS[0]]


@pytest.mark.parametrize(
    "argv",
    (
        [],
        ["--real-provider"],
        ["--attempt-number", "1"],
        ["--real-provider", "--attempt-number", "2", "--private-output-directory", "/tmp/x", runner._OWNER_APPROVAL_FLAG],
        ["--real-provider", "--attempt-number", "01", "--private-output-directory", "/tmp/x", runner._OWNER_APPROVAL_FLAG],
        ["--real-provider", "--attempt-number", "+1", "--private-output-directory", "/tmp/x", runner._OWNER_APPROVAL_FLAG],
        ["--real-provider", "--attempt-number", "١", "--private-output-directory", "/tmp/x", runner._OWNER_APPROVAL_FLAG],
        ["--real", "--attempt-number", "1", "--private-output-directory", "/tmp/x", runner._OWNER_APPROVAL_FLAG],
        ["--unknown"],
        ["positional"],
    ),
)
def test_cli_invalid_inputs_fail_closed_without_execution(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    argv: list[str],
) -> None:
    calls: list[str] = []
    monkeypatch.setattr(runner, "_execute_real_attempt", lambda path: calls.append(path))
    assert runner.main(argv) == 2
    captured = capsys.readouterr()
    assert captured.err == ""
    assert len(captured.out.splitlines()) == 1
    assert json.loads(captured.out)["final_status"] == "FAIL_CLOSED"
    assert calls == []


@pytest.mark.parametrize(
    "duplicate",
    (
        "--real-provider",
        "--attempt-number",
        "--private-output-directory",
        runner._OWNER_APPROVAL_FLAG,
    ),
)
def test_cli_rejects_every_duplicate_option(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    duplicate: str,
) -> None:
    args = [
        "--real-provider",
        "--attempt-number",
        "1",
        "--private-output-directory",
        "/tmp/supplier-attempt",
        runner._OWNER_APPROVAL_FLAG,
    ]
    args.append(duplicate if duplicate.endswith("approval") or duplicate == "--real-provider" else f"{duplicate}=x")
    monkeypatch.setattr(runner, "_execute_real_attempt", lambda path: pytest.fail("must not execute"))
    assert runner.main(args) == 2
    assert capsys.readouterr().err == ""


def test_cli_valid_geometry_delegates_once(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], result) -> None:
    calls: list[str] = []

    def execute(path: str):
        calls.append(path)
        return _real_result(result)

    monkeypatch.setattr(runner, "_execute_real_attempt", execute)
    argv = [
        "--real-provider",
        "--attempt-number",
        "1",
        "--private-output-directory",
        "/tmp/supplier-attempt",
        runner._OWNER_APPROVAL_FLAG,
    ]
    assert runner.main(argv) == 0
    captured = capsys.readouterr()
    assert captured.err == ""
    assert len(captured.out.splitlines()) == 1
    assert calls == ["/tmp/supplier-attempt"]


@pytest.mark.parametrize("path", ("relative", "./relative", "/tmp/a/../b", "/tmp//b"))
def test_private_path_rejects_noncanonical_values(path: str) -> None:
    with pytest.raises(ValueError, match=runner.REASON_PATH_INVALID):
        runner._validate_private_output(path)


def test_private_path_accepts_absent_absolute_path(tmp_path: Path) -> None:
    path = tmp_path / "attempt_01"
    assert runner._validate_private_output(str(path)) == path


def test_private_path_rejects_existing_file_and_directory(tmp_path: Path) -> None:
    file_path = tmp_path / "file"
    file_path.write_text("x", encoding="utf-8")
    with pytest.raises(ValueError, match=runner.REASON_PATH_EXISTS):
        runner._validate_private_output(str(file_path))
    directory = tmp_path / "directory"
    directory.mkdir()
    with pytest.raises(ValueError, match=runner.REASON_PATH_EXISTS):
        runner._validate_private_output(str(directory))


def test_private_path_rejects_symlink_component(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.mkdir()
    link = tmp_path / "link"
    link.symlink_to(target, target_is_directory=True)
    with pytest.raises((ValueError, OSError)):
        runner._validate_private_output(str(link / "attempt"))


def test_descriptor_write_handles_partial_writes(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    parent_fd = runner._open_absolute_directory(tmp_path)
    original = runner.os.write

    def short_write(fd: int, data: bytes) -> int:
        return original(fd, data[: max(1, len(data) // 3)])

    monkeypatch.setattr(runner.os, "write", short_write)
    try:
        runner._write_owned_file(parent_fd, "result.json", b'{"ok":true}\n', 0o600)
    finally:
        os.close(parent_fd)
    assert (tmp_path / "result.json").read_bytes() == b'{"ok":true}\n'


def test_descriptor_write_failure_removes_only_owned_inode(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    parent_fd = runner._open_absolute_directory(tmp_path)
    original = runner._write_all

    def fail_after_write(fd: int, data: bytes) -> None:
        original(fd, data)
        raise OSError("injected_write_failure")

    monkeypatch.setattr(runner, "_write_all", fail_after_write)
    try:
        with pytest.raises(OSError):
            runner._write_owned_file(parent_fd, "failed.json", b'{"ok":true}\n', 0o600)
    finally:
        os.close(parent_fd)
    assert not (tmp_path / "failed.json").exists()


def test_private_attempt_preservation_is_immutable(tmp_path: Path) -> None:
    root = tmp_path / "attempt_01"
    runner._create_attempt_root(root, HEAD)
    raw_fd = runner._open_absolute_directory(root / runner.RAW_ATTEMPT_DIRECTORY)
    try:
        runner._write_owned_file(raw_fd, "summary.json", b'{"status":"FAIL_CLOSED"}\n', 0o600)
    finally:
        os.close(raw_fd)
    runner._preserve_attempt(root=root, execution_head=HEAD, result=None, reason=runner.REASON_COLLECTION_FAILED)
    assert stat.S_IMODE(root.stat().st_mode) == 0o500
    assert stat.S_IMODE((root / runner.RAW_ATTEMPT_DIRECTORY).stat().st_mode) == 0o500
    assert stat.S_IMODE((root / runner.ATTEMPT_IDENTITY_FILE).stat().st_mode) == 0o400
    assert stat.S_IMODE((root / runner.PRIVATE_INVENTORY_FILE).stat().st_mode) == 0o400
    assert stat.S_IMODE((root / runner.GENERATION_GATE_FILE).stat().st_mode) == 0o400
    assert stat.S_IMODE((root / runner.RAW_ATTEMPT_DIRECTORY / "summary.json").stat().st_mode) == 0o400
    assert (root / runner.PRIVATE_INVENTORY_FILE).is_file()
    assert (root / runner.GENERATION_GATE_FILE).is_file()
    os.chmod(root / runner.RAW_ATTEMPT_DIRECTORY, 0o700)
    os.chmod(root, 0o700)


def test_collection_failure_preserves_private_attempt_without_public_output(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    root = tmp_path / "attempt_01"
    monkeypatch.setattr(runner, "_git_head", lambda: HEAD)
    monkeypatch.setattr(
        runner,
        "_collect_with_context",
        lambda **kwargs: (_ for _ in ()).throw(ValueError(runner.REASON_COLLECTION_FAILED)),
    )
    with pytest.raises(ValueError, match=runner.REASON_COLLECTION_FAILED):
        runner._execute_real_attempt(str(root))
    assert root.is_dir()
    assert (root / runner.GENERATION_GATE_FILE).is_file()
    assert not runner.CANONICAL_SAFE_REPORT_PATH.exists()
    os.chmod(root / runner.RAW_ATTEMPT_DIRECTORY, 0o700)
    os.chmod(root, 0o700)


def _install_simulated_real_collector(
    monkeypatch: pytest.MonkeyPatch,
    events: list[str] | None = None,
) -> None:
    report = _real_source_report()

    def collect(*, env: dict[str, str], provider: object) -> dict[str, object]:
        if events is not None:
            events.append("collect")
        assert provider is None
        artifact_root = Path(env[live.ARTIFACT_DIR_ENV])
        (artifact_root / "source_summary.json").write_bytes(b'{"final_status":"PASS"}\n')
        return copy.deepcopy(report)

    monkeypatch.setattr(
        runner._live,
        "collect_full_wow_v1_2_manual_live_multillm_fractal_trace",
        collect,
    )
    monkeypatch.setattr(runner, "_git_head", lambda: HEAD)
    monkeypatch.setattr(
        runner._live,
        "_config_value_from_env_or_config",
        lambda *args: pytest.fail("credential access forbidden"),
    )


def test_simulated_real_execution_uses_real_path_and_freezes_before_public(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    isolated_canonical_report: Path,
) -> None:
    root = tmp_path / "attempt_01"
    events: list[str] = []
    _install_simulated_real_collector(monkeypatch, events)
    original_preserve = runner._preserve_attempt
    original_write = runner._write_public_report

    def preserve(**kwargs: object) -> None:
        events.append("preserve")
        original_preserve(**kwargs)

    def write(content: bytes, parent_identity: tuple[int, int, int]):
        events.append("public")
        return original_write(content, parent_identity)

    monkeypatch.setattr(runner, "_preserve_attempt", preserve)
    monkeypatch.setattr(runner, "_write_public_report", write)
    value = runner._execute_real_attempt(str(root))
    try:
        assert runner.validate_supplier_s1_program_result_v01(value) == ()
        assert events == ["collect", "preserve", "public"]
        assert stat.S_IMODE(isolated_canonical_report.stat().st_mode) == 0o400
        assert stat.S_IMODE(root.stat().st_mode) == 0o500
        assert stat.S_IMODE((root / runner.RAW_ATTEMPT_DIRECTORY).stat().st_mode) == 0o500
        for path in (
            root / runner.ATTEMPT_IDENTITY_FILE,
            root / runner.PRIVATE_INVENTORY_FILE,
            root / runner.GENERATION_GATE_FILE,
            root / runner.RAW_ATTEMPT_DIRECTORY / "source_summary.json",
        ):
            assert stat.S_IMODE(path.stat().st_mode) == 0o400
        assert (
            value.callback_count,
            value.provider_start_count,
            value.provider_completion_count,
            value.real_world_effects_count,
        ) == (6, 6, 6, 0)
        public = json.loads(isolated_canonical_report.read_bytes())
        assert public["result_id"] == value.result_id
        assert public["safe_execution_projection"]["safe_execution_id"]
    finally:
        isolated_canonical_report.unlink(missing_ok=True)
        _restore_attempt_permissions(root)


def test_private_preservation_failure_creates_no_public_output(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    result,
) -> None:
    root = tmp_path / "attempt_01"
    public = tmp_path / "public.json"
    monkeypatch.setattr(runner, "CANONICAL_SAFE_REPORT_PATH", public)
    monkeypatch.setattr(runner, "_git_head", lambda: HEAD)
    source = _real_source_report()
    monkeypatch.setattr(runner, "_collect_with_context", lambda **kwargs: (_real_result(result), source))
    monkeypatch.setattr(runner, "_build_public_report", lambda *args: b'{}\n')
    monkeypatch.setattr(runner, "_preserve_attempt", lambda **kwargs: (_ for _ in ()).throw(OSError("failure")))
    with pytest.raises(ValueError, match=runner.REASON_WRITE_FAILED):
        runner._execute_real_attempt(str(root))
    assert not public.exists()
    _restore_attempt_permissions(root)


def test_public_write_failure_leaves_frozen_private_attempt(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    root = tmp_path / "attempt_01"
    _install_simulated_real_collector(monkeypatch)
    monkeypatch.setattr(
        runner,
        "_write_public_report",
        lambda *args: (_ for _ in ()).throw(OSError("public_write_failure")),
    )
    with pytest.raises(ValueError):
        runner._execute_real_attempt(str(root))
    try:
        assert stat.S_IMODE(root.stat().st_mode) == 0o500
        assert stat.S_IMODE((root / runner.GENERATION_GATE_FILE).stat().st_mode) == 0o400
        assert not runner.CANONICAL_SAFE_REPORT_PATH.exists()
    finally:
        _restore_attempt_permissions(root)


def test_partial_attempt_creation_is_frozen_before_collector(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    root = tmp_path / "attempt_01"
    collector_calls: list[str] = []
    original_write = runner._write_owned_file

    def fail_identity_write(
        parent_fd: int,
        name: str,
        content: bytes,
        mode: int,
    ) -> tuple[int, int]:
        if name == runner.ATTEMPT_IDENTITY_FILE:
            raise OSError("identity_write_failure")
        return original_write(parent_fd, name, content, mode)

    monkeypatch.setattr(runner, "_git_head", lambda: HEAD)
    monkeypatch.setattr(runner, "_write_owned_file", fail_identity_write)
    monkeypatch.setattr(
        runner,
        "_collect_with_context",
        lambda **kwargs: collector_calls.append("collector"),
    )
    with pytest.raises(ValueError, match=runner.REASON_WRITE_FAILED):
        runner._execute_real_attempt(str(root))
    try:
        assert collector_calls == []
        assert not runner.CANONICAL_SAFE_REPORT_PATH.exists()
        assert root.is_dir()
        assert (root / runner.RAW_ATTEMPT_DIRECTORY).is_dir()
        assert stat.S_IMODE(root.stat().st_mode) == 0o500
        assert stat.S_IMODE((root / runner.RAW_ATTEMPT_DIRECTORY).stat().st_mode) == 0o500
        assert not any(
            stat.S_IMODE(path.stat().st_mode) == 0o700
            for path in (root, root / runner.RAW_ATTEMPT_DIRECTORY)
        )
    finally:
        _restore_attempt_permissions(root)


@pytest.mark.parametrize("unsafe_kind", ("missing", "symlink"))
def test_unsafe_public_parent_fails_before_collector_and_private_root(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    unsafe_kind: str,
) -> None:
    target = tmp_path / "target"
    target.mkdir()
    if unsafe_kind == "missing":
        parent = tmp_path / "missing"
    else:
        parent = tmp_path / "link"
        parent.symlink_to(target, target_is_directory=True)
    monkeypatch.setattr(runner, "CANONICAL_SAFE_REPORT_PATH", parent / "report.json")
    root = tmp_path / "attempt_01"
    calls: list[str] = []
    monkeypatch.setattr(
        runner,
        "_collect_with_context",
        lambda **kwargs: calls.append("collector"),
    )
    with pytest.raises((ValueError, OSError)):
        runner._execute_real_attempt(str(root))
    assert calls == []
    assert not root.exists()
    assert not (target / "report.json").exists()


def test_main_rejects_stale_or_recomputed_invalid_result(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    result,
) -> None:
    invalid = replace(_real_result(result), result_id="f" * 64)
    monkeypatch.setattr(runner, "_execute_real_attempt", lambda path: invalid)
    argv = [
        "--real-provider",
        "--attempt-number",
        "1",
        "--private-output-directory",
        "/tmp/supplier-attempt",
        runner._OWNER_APPROVAL_FLAG,
    ]
    assert runner.main(argv) == 2
    captured = capsys.readouterr()
    assert captured.err == ""
    assert json.loads(captured.out)["final_status"] == runner.STATUS_FAIL_CLOSED


def test_cleanup_preserves_foreign_replacement(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    public = tmp_path / "public.json"
    public.write_bytes(b"first")
    identity = public.stat().st_dev, public.stat().st_ino
    public.unlink()
    public.write_bytes(b"foreign")
    monkeypatch.setattr(runner, "CANONICAL_SAFE_REPORT_PATH", public)
    with pytest.raises(ValueError, match=runner.REASON_WRITE_FAILED):
        runner._cleanup_owned_public(identity)
    assert public.read_bytes() == b"foreign"


def test_source_contains_no_retry_fallback_or_second_collection() -> None:
    source = Path(runner.__file__).read_text(encoding="utf-8")
    assert "retry_count=0" in source
    assert "fallback_call_count=0" in source
    assert source.count("collect_full_wow_v1_2_manual_live_multillm_fractal_trace(") == 1
    assert "requests" not in source
    assert "from google" not in source
    assert "genai.Client" not in source


def test_injected_execution_never_reads_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(runner._live, "_config_value_from_env_or_config", lambda *args: pytest.fail("credential read"))
    assert _collect().final_status == "PASS"


def test_no_canonical_publication_package_anchor_or_replay(isolated_canonical_report: Path) -> None:
    assert not isolated_canonical_report.exists()
    root = Path("docs/evidence/two_domain_all_real_sealed_evidence_program_v01/supplier_water_filter")
    assert not (root / "supplier_safe_package_index_v01.json").exists()
    assert not (root / "supplier_crypto_anchor_v01.json").exists()
    assert not (root / "supplier_replay_report_v01.json").exists()
