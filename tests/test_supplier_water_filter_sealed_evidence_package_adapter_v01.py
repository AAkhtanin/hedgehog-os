import ast
import copy
from dataclasses import FrozenInstanceError, fields, is_dataclass, replace
import inspect
import json
from pathlib import Path

import pytest

from demo.run_full_wow_v1_2_product_trace import collect_full_wow_v1_2_product_trace
from hedgehog import action_commit_packet_v02 as action_packet
from hedgehog.domains.supplier_water_filter import kernel_adapter_v01 as kernel_adapter
from hedgehog.domains.supplier_water_filter import live_evidence_adapter_v01 as live_adapter
from hedgehog.domains.supplier_water_filter import sealed_evidence_package_adapter_v01 as adapter
from hedgehog.evidence import sealed_evidence_profile_v01 as profile
from hedgehog.evidence import sealed_package_v01 as sealed_package


EXPECTED_FIELDS = (
    "adapter_result_id",
    "adapter_version",
    "safe_execution_id",
    "scenario_index_id",
    "scenario_ids",
    "scenario_names",
    "scenario_classifications",
    "scenario_row_hashes",
    "scenario_technical_statuses",
    "scenario_business_outcomes",
    "source_run_id",
    "source_report_id",
    "source_trace_type",
    "transaction_id",
    "kernel_adapter_id",
    "kernel_manifest_hash",
    "multiroot_outcome_id",
    "multiroot_outcome",
    "supplier_a_status",
    "supplier_a_mock_payment_status",
    "supplier_b_status",
    "shipment_status",
    "receipt_status",
    "technical_conformance_status",
    "business_outcome",
    "real_payment_executed",
    "real_shipment_released",
    "domain_projection",
    "scenario_count",
    "source_record_count",
    "artifact_record_count",
    "kernel_artifact_ref_count",
    "causal_ref_count",
    "business_module_count",
    "fractal_branch_count",
    "result_proposal_count",
    "root_decision_count",
    "cross_root_evidence_count",
    "adapter_provider_call_count",
    "adapter_network_call_count",
    "adapter_gemini_call_count",
    "created_authority_count",
    "created_permission_count",
    "action_created_count",
    "receipt_created_count",
    "final_output_created_count",
    "real_world_effects_count",
    "validation_errors",
    "status",
)
EXPECTED_FUNCTIONS = (
    "build_supplier_water_filter_sealed_evidence_package_adapter_result_v01",
    "validate_supplier_water_filter_sealed_evidence_package_adapter_result_v01",
    "supplier_water_filter_sealed_evidence_package_adapter_result_to_plain_dict_v01",
)
SCENARIO_SPECS = (
    ("S-N1", "initial_business_blockers_root_not_ready", "deterministic_initial_business_evidence", "PASS", "NOT_READY", "NOT_READY", "BLOCKED_PENDING_CORRECTION", "ABSENT", "NOT_ENTERED", "ABSENT"),
    ("S-N2", "unsafe_live_evidence_fail_closed", "live_bound_negative_safe_projection", "FAIL_CLOSED", "NOT_READY", "NO_ACCEPTED_NEW_ROOT_FINAL", "BLOCKED_PENDING_CORRECTION", "ABSENT", "NOT_ENTERED", "ABSENT"),
    ("S-C1", "corrected_evidence_validation_rerun", "deterministic_corrected_evidence", "PASS", "MIXED", "SUPPLIER_A_SCOPED_REVIEW_READY", "SUPPLIER_A_SCOPED_REVIEW_READY", "ABSENT", "NOT_ENTERED", "ABSENT"),
    ("S-P1", "supplier_a_scoped_human_approval", "deterministic_owner_approval", "PASS", "MIXED", "SUPPLIER_A_SCOPED_REVIEW_READY", "APPROVED_SCOPE_ONLY", "ROOT_CREATED_SCOPED", "NOT_ENTERED", "ABSENT"),
    ("S-P2", "supplier_a_mock_bank_happy_path", "live_bound_deterministic_corridor", "PASS", "MIXED", "SUPPLIER_A_SCOPED_REVIEW_READY", "PASS", "VALID_SCOPED", "PASS", "EVIDENCE_ONLY"),
    ("S-F1", "no_human_approval_blocks_action", "deterministic_policy_probe", "FAIL_CLOSED", "NOT_READY", "NO_ACTION_APPROVAL", "NOT_EXECUTED", "REJECTED", "NOT_ENTERED", "ABSENT"),
    ("S-F2", "packet_and_corridor_mutation_matrix", "deterministic_packet_corridor_mutation", "FAIL_CLOSED", "MIXED", "NO_WIDENED_ROOT_DECISION", "UNCHANGED", "REJECTED", "REJECTED", "ABSENT"),
    ("S-F3", "receipt_attack_matrix", "deterministic_receipt_attack", "FAIL_CLOSED", "MIXED", "NO_NEW_PERMISSION", "UNCHANGED", "UNCHANGED", "NO_NEW_EXECUTION", "ATTACK_REJECTED"),
    ("S-M1", "integrated_mixed_business_outcome", "deterministic_integrated_outcome", "PASS", "MIXED", "HELD", "PASS", "VALID_SCOPED", "PASS", "EVIDENCE_ONLY"),
)
EXPECTED_ARTIFACT_PROVENANCE = (
    ("supplier_water_filter_artifact:01:dirty_request_received", "dirty_request_received", "NEGATIVE_CONFORMANCE", "supplier_negative_conformance_matrix"),
    ("supplier_water_filter_artifact:02:warehouse_inventory_query", "warehouse_inventory_query", "EXECUTED_DETERMINISTIC_RUNTIME", "supplier_nine_scenario_index"),
    ("supplier_water_filter_artifact:03:supplier_a_availability_query", "supplier_a_availability_query", "EXECUTED_DETERMINISTIC_RUNTIME", "supplier_nine_scenario_index"),
    ("supplier_water_filter_artifact:04:supplier_b_blocker_query", "supplier_b_blocker_query", "NEGATIVE_CONFORMANCE", "supplier_negative_conformance_matrix"),
    ("supplier_water_filter_artifact:05:legal_insurance_contract_check", "legal_insurance_contract_check", "EXECUTED_DETERMINISTIC_RUNTIME", "supplier_nine_scenario_index"),
    ("supplier_water_filter_artifact:06:accounting_invoice_po_reconciliation", "accounting_invoice_po_reconciliation", "EXECUTED_DETERMINISTIC_RUNTIME", "supplier_nine_scenario_index"),
    ("supplier_water_filter_artifact:07:bank_a_payment_slot_prepared", "bank_a_payment_slot_prepared", "EXECUTED_DETERMINISTIC_RUNTIME", "supplier_nine_scenario_index"),
    ("supplier_water_filter_artifact:08:bank_b_native_contract_preview", "bank_b_native_contract_preview", "EXECUTED_DETERMINISTIC_RUNTIME", "supplier_nine_scenario_index"),
    ("supplier_water_filter_artifact:09:top_level_semantic_route_observed_from_v1_1", "top_level_semantic_route_observed_from_v1_1", "EXECUTED_DETERMINISTIC_RUNTIME", "supplier_nine_scenario_index"),
    ("supplier_water_filter_artifact:10:bsep_membrane_observed_from_v1_1", "bsep_membrane_observed_from_v1_1", "EXECUTED_DETERMINISTIC_RUNTIME", "supplier_nine_scenario_index"),
    ("supplier_water_filter_artifact:11:top_level_live_semantic_architect_observed_from_v1_1", "top_level_live_semantic_architect_observed_from_v1_1", "EXECUTED_DETERMINISTIC_RUNTIME", "supplier_nine_scenario_index"),
    ("supplier_water_filter_artifact:12:runtime_plangraph_compiled", "runtime_plangraph_compiled", "EXECUTED_DETERMINISTIC_RUNTIME", "supplier_nine_scenario_index"),
    ("supplier_water_filter_artifact:13:fractal_branch_cells_dispatched", "fractal_branch_cells_dispatched", "EXECUTED_DETERMINISTIC_RUNTIME", "supplier_nine_scenario_index"),
    ("supplier_water_filter_artifact:14:branch_result_proposals_collected", "branch_result_proposals_collected", "EXECUTED_DETERMINISTIC_RUNTIME", "supplier_nine_scenario_index"),
    ("supplier_water_filter_artifact:15:post_vv_validated", "post_vv_validated", "EXECUTED_DETERMINISTIC_RUNTIME", "supplier_nine_scenario_index"),
    ("supplier_water_filter_artifact:16:gt_lgt_advisory_review", "gt_lgt_advisory_review", "EXECUTED_DETERMINISTIC_RUNTIME", "supplier_nine_scenario_index"),
    ("supplier_water_filter_artifact:17:root_first_not_ready", "root_first_not_ready", "ROOT_DECISION_EVIDENCE", "supplier_root_multiroot_evidence"),
    ("supplier_water_filter_artifact:18:corrected_evidence_received", "corrected_evidence_received", "EXECUTED_DETERMINISTIC_RUNTIME", "supplier_nine_scenario_index"),
    ("supplier_water_filter_artifact:19:root_second_supplier_a_scoped_review", "root_second_supplier_a_scoped_review", "ROOT_DECISION_EVIDENCE", "supplier_root_multiroot_evidence"),
    ("supplier_water_filter_artifact:20:human_approval_supplier_a_only", "human_approval_supplier_a_only", "CORRIDOR_EVIDENCE", "supplier_packet_corridor_receipt_evidence"),
    ("supplier_water_filter_artifact:21:root_created_mock_action_commit_packet_observed", "root_created_mock_action_commit_packet_observed", "CORRIDOR_EVIDENCE", "supplier_packet_corridor_receipt_evidence"),
    ("supplier_water_filter_artifact:22:mock_bank_sandbox_receipt_observed", "mock_bank_sandbox_receipt_observed", "CORRIDOR_EVIDENCE", "supplier_packet_corridor_receipt_evidence"),
    ("supplier_water_filter_artifact:23:final_state_summary", "final_state_summary", "ROOT_DECISION_EVIDENCE", "supplier_root_multiroot_evidence"),
)


def _safe_report() -> dict[str, object]:
    return {
        "execution_head": "e64b4c1",
        "run_id": "supplier-water-filter-live-fixture-001",
        "report_id": "supplier-water-filter-live-fixture-001",
        "source_task_id": "supplier-water-filter-live-evidence-task-v01",
        "transaction_id": kernel_adapter.TRANSACTION_ID,
        "provider_mode": "real_provider",
        "model_id": "gemini-2.5-flash",
        "source_final_status": "PASS",
        "actors": [
            {
                "actor_id": actor_id,
                "safe_projection": {
                    "actor_id": actor_id,
                    "accepted_summary": f"safe accepted semantics for {actor_id}",
                    "evidence_refs": [f"evidence:{index:02d}"],
                },
                "validation_status": "PASS",
            }
            for index, actor_id in enumerate(live_adapter.ACTOR_IDS)
        ],
        "bsep": {
            "bsep_id": "bsep:supplier-water-filter:001",
            "safe_projection": {
                "bounded_business_context": [
                    "Supplier A scope only",
                    "Supplier B blocked",
                    "shipment held",
                ],
                "bounded_drs_context": {"direct_reuse_allowed_count": 0},
                "bounded_avf_context": {"hard_masks_preserved": True},
                "material_exclusions": ["user", "provider", "bank"],
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


def _scenario_rows() -> tuple[dict[str, object], ...]:
    return tuple(
        {
            "scenario_id": spec[0],
            "scenario_name": spec[1],
            "classification": spec[2],
            "technical_status": spec[3],
            "business_outcome": spec[4],
            "root_status": spec[5],
            "supplier_a_status": spec[6],
            "supplier_b_status": "BLOCKED",
            "shipment_status": "HELD",
            "packet_status": spec[7],
            "corridor_status": spec[8],
            "receipt_status": spec[9],
            "additional_provider_call_count": 0,
            "additional_network_call_count": 0,
            "additional_gemini_call_count": 0,
            "real_payment_executed": False,
            "real_shipment_released": False,
            "real_world_effects_count": 0,
            "evidence_refs": (f"evidence:supplier:{spec[0].casefold()}",),
        }
        for spec in SCENARIO_SPECS
    )


@pytest.fixture(scope="module")
def safe_execution():
    return live_adapter.build_supplier_water_filter_safe_execution_projection_v01(_safe_report())


@pytest.fixture(scope="module")
def source_report():
    report = collect_full_wow_v1_2_product_trace()
    assert report["final_status"] == "PASS"
    assert report["validation_errors"] == ()
    return report


@pytest.fixture(scope="module")
def kernel_result(source_report):
    result = kernel_adapter.build_supplier_water_filter_kernel_adapter_result_v01(source_report=source_report)
    assert kernel_adapter.validate_supplier_water_filter_kernel_adapter_result_v01(source_report=source_report, result=result) == ()
    return result


@pytest.fixture(scope="module")
def context(safe_execution, source_report, kernel_result):
    return {
        "safe_execution": safe_execution,
        "scenario_rows": _scenario_rows(),
        "source_report": source_report,
        "kernel_adapter_result": kernel_result,
    }


@pytest.fixture(scope="module")
def result(context):
    return adapter.build_supplier_water_filter_sealed_evidence_package_adapter_result_v01(**context)


def _build(context):
    return adapter.build_supplier_water_filter_sealed_evidence_package_adapter_result_v01(**context)


def _validate(result, context):
    return adapter.validate_supplier_water_filter_sealed_evidence_package_adapter_result_v01(result, **context)


def _contains_forbidden(value: object) -> bool:
    if isinstance(value, bytes) or isinstance(value, tuple) or is_dataclass(value):
        return True
    if isinstance(value, dict):
        return any(_contains_forbidden(key) or _contains_forbidden(item) for key, item in value.items())
    if isinstance(value, list):
        return any(_contains_forbidden(item) for item in value)
    return False


def _package_members(projection):
    contents = tuple(
        json.dumps({"source_record_id": source.source_record_id}, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n"
        for source in projection.source_records
    )
    files = tuple(
        sealed_package.build_safe_file_record_v01(
            logical_path=f"evidence/{index:02d}-{source.source_type}.json",
            media_type="application/json",
            content_bytes=content,
            evidence_class=source.evidence_class,
            source_record_ids=(source.source_record_id,),
            terminal_newline_required=True,
            secret_scan_passed=True,
        )
        for index, (source, content) in enumerate(zip(projection.source_records, contents, strict=True))
    )
    return files, contents


def _rehash_source(source):
    return replace(
        source,
        source_record_id=profile._identity_hash(
            profile._SAFE_SOURCE_RECORD_DOMAIN,
            profile._safe_source_record_plain(source, include_id=False),
        ),
    )


def _projection_with_source(projection, index, source):
    sources = list(projection.source_records)
    sources[index] = source
    changed = replace(projection, source_records=tuple(sources), projection_id="0" * 64)
    return replace(changed, projection_id=profile._projection_identity(changed))


@pytest.mark.parametrize(
    ("name", "expected"),
    (
        ("MODULE_ID", "supplier_water_filter_sealed_evidence_package_adapter_v01"),
        ("ADAPTER_VERSION", "v0.1"),
        ("ADAPTER_STATUSES", ("PASS", "FAIL_CLOSED")),
        ("SCENARIO_COUNT", 9),
        ("SOURCE_RECORD_COUNT", 7),
        ("ARTIFACT_RECORD_COUNT", 23),
        ("KERNEL_ARTIFACT_REF_COUNT", 23),
        ("CAUSAL_REF_COUNT", 22),
        ("MULTIROOT_OUTCOME", "MIXED"),
        ("BUSINESS_OUTCOME", "MIXED"),
    ),
)
def test_constants_are_exact(name, expected):
    assert getattr(adapter, name) == expected


@pytest.mark.parametrize(("index", "name"), tuple(enumerate(EXPECTED_FIELDS)))
def test_dataclass_field_order(index, name):
    assert fields(adapter.SupplierWaterFilterSealedEvidencePackageAdapterResultV01)[index].name == name


def test_dataclass_field_geometry_is_exact():
    observed = tuple(
        field.name
        for field in fields(
            adapter.SupplierWaterFilterSealedEvidencePackageAdapterResultV01
        )
    )
    assert observed == EXPECTED_FIELDS
    assert len(observed) == len(EXPECTED_FIELDS) == 49


def test_dataclass_is_frozen_and_slotted(result):
    cls = adapter.SupplierWaterFilterSealedEvidencePackageAdapterResultV01
    assert cls.__dataclass_params__.frozen
    assert "__slots__" in vars(cls)
    with pytest.raises(FrozenInstanceError):
        result.business_outcome = "PASS"


def test_public_surface_is_exact():
    classes = tuple(name for name, value in vars(adapter).items() if not name.startswith("_") and inspect.isclass(value))
    functions = tuple(name for name, value in vars(adapter).items() if not name.startswith("_") and inspect.isfunction(value))
    assert classes == ("SupplierWaterFilterSealedEvidencePackageAdapterResultV01",)
    assert functions == EXPECTED_FUNCTIONS
    assert "annotations" not in vars(adapter)


def test_frozen_gate1_chain_plus_disposable_r1_projection_fixture_passes(
    context,
    result,
):
    """Gate-1 inputs are committed; live/scenario inputs are disposable fixtures."""
    assert kernel_adapter.validate_supplier_water_filter_kernel_adapter_result_v01(
        source_report=context["source_report"], result=context["kernel_adapter_result"]
    ) == ()
    assert context["safe_execution"].run_id == "supplier-water-filter-live-fixture-001"
    assert tuple(row["scenario_id"] for row in context["scenario_rows"]) == adapter.SCENARIO_IDS
    assert "limitation:no_new_live_collection_during_r1" in result.domain_projection.limitation_refs
    assert result.status == "PASS"
    assert _validate(result, context) == ()


def test_exact_nine_scenario_identity_name_order_and_classification(result):
    assert result.scenario_ids == adapter.SCENARIO_IDS
    assert result.scenario_names == adapter.SCENARIO_NAMES
    assert result.scenario_classifications == tuple(spec[2] for spec in SCENARIO_SPECS)
    assert result.scenario_technical_statuses == tuple(spec[3] for spec in SCENARIO_SPECS)
    assert result.scenario_business_outcomes == tuple(spec[4] for spec in SCENARIO_SPECS)
    assert len(set(result.scenario_row_hashes)) == 9


@pytest.mark.parametrize("index", range(9))
def test_every_scenario_has_zero_additional_call_geometry(index):
    row = _scenario_rows()[index]
    assert (
        row["additional_provider_call_count"],
        row["additional_network_call_count"],
        row["additional_gemini_call_count"],
    ) == (0, 0, 0)


@pytest.mark.parametrize("mutation", ("missing", "duplicate", "reordered", "renamed", "unknown"))
def test_scenario_geometry_attacks_are_rejected(context, mutation):
    changed = dict(context)
    rows = list(copy.deepcopy(context["scenario_rows"]))
    if mutation == "missing":
        rows = rows[:-1]
    elif mutation == "duplicate":
        rows[1] = copy.deepcopy(rows[0])
    elif mutation == "reordered":
        rows[0], rows[1] = rows[1], rows[0]
    elif mutation == "renamed":
        rows[0]["scenario_name"] += "_changed"
    else:
        rows[0]["scenario_id"] = "S-X1"
    changed["scenario_rows"] = tuple(rows)
    with pytest.raises(ValueError, match="scenario_invalid"):
        _build(changed)


@pytest.mark.parametrize(
    ("index", "field", "value"),
    (
        (0, "technical_status", "FAIL_CLOSED"),
        (1, "technical_status", "PASS"),
        (4, "supplier_b_status", "APPROVED"),
        (4, "shipment_status", "RELEASED"),
        (4, "receipt_status", "SETTLED"),
        (4, "business_outcome", "PASS"),
        (3, "packet_status", "WIDENED_SCOPE"),
        (4, "real_payment_executed", True),
        (4, "real_shipment_released", True),
        (4, "real_world_effects_count", 1),
        (4, "additional_provider_call_count", 6),
        (4, "additional_network_call_count", 6),
        (4, "additional_gemini_call_count", 6),
    ),
)
def test_scenario_status_authority_and_effect_attacks_are_rejected(context, index, field, value):
    changed = dict(context)
    rows = list(copy.deepcopy(context["scenario_rows"]))
    rows[index][field] = value
    changed["scenario_rows"] = tuple(rows)
    with pytest.raises(ValueError, match="scenario_invalid"):
        _build(changed)


def test_business_outcome_facts_remain_distinct(result):
    assert result.supplier_a_status == "SUPPLIER_A_SCOPED_REVIEW_READY"
    assert result.supplier_a_mock_payment_status == "PASS"
    assert result.supplier_b_status == "BLOCKED"
    assert result.shipment_status == "HELD"
    assert result.receipt_status == "EVIDENCE_ONLY"
    assert result.technical_conformance_status == "PASS"
    assert result.business_outcome == "MIXED"
    assert result.real_payment_executed is False
    assert result.real_shipment_released is False


def test_exact_kernel_causal_and_multiroot_geometry(result, kernel_result):
    projection = result.domain_projection
    assert (
        result.business_module_count,
        result.artifact_record_count,
        result.kernel_artifact_ref_count,
        result.causal_ref_count,
        result.fractal_branch_count,
        result.result_proposal_count,
        result.root_decision_count,
        result.cross_root_evidence_count,
    ) == (7, 23, 23, 22, 8, 8, 1, 0)
    assert projection.kernel_artifact_refs == kernel_result.kernel_manifest.artifacts
    assert projection.causal_consumption_refs == kernel_result.causal_consumption_refs
    assert result.multiroot_outcome == "MIXED"


def test_shared_projection_pass_and_exact_call_separation(result):
    projection = result.domain_projection
    assert profile.validate_domain_evidence_projection_v01(projection) == ()
    assert projection.status == "PASS"
    assert (projection.source_provider_call_count, projection.source_network_call_count, projection.source_gemini_call_count) == (6, 6, 6)
    assert (projection.projection_provider_call_count, projection.projection_network_call_count, projection.projection_gemini_call_count) == (0, 0, 0)
    nonzero = [
        item
        for item in projection.source_records
        if any((item.observed_provider_call_count, item.observed_network_call_count, item.observed_gemini_call_count))
    ]
    assert len(nonzero) == 1
    assert nonzero[0].evidence_class == "EXECUTED_LIVE_RUNTIME"
    assert (nonzero[0].observed_provider_call_count, nonzero[0].observed_network_call_count, nonzero[0].observed_gemini_call_count) == (6, 6, 6)


def test_kernel_manifest_hash_is_grounded_by_integrity_source(result):
    sources = result.domain_projection.source_records
    grounded = [item for item in sources if item.evidence_class == "CRYPTOGRAPHIC_INTEGRITY"]
    assert len(grounded) == 1
    assert result.kernel_manifest_hash in grounded[0].trace_refs


def test_all_artifact_source_references_resolve(result):
    source_ids = {item.source_record_id for item in result.domain_projection.source_records}
    assert len(result.domain_projection.artifact_records) == 23
    assert all(set(item.source_record_ids) <= source_ids for item in result.domain_projection.artifact_records)


def test_exact_23_row_artifact_provenance_is_frozen(result, kernel_result):
    source_by_id = {
        source.source_record_id: source
        for source in result.domain_projection.source_records
    }
    observed = []
    for artifact_record, kernel_artifact in zip(
        result.domain_projection.artifact_records,
        kernel_result.kernel_artifacts,
        strict=True,
    ):
        source_record_id, = artifact_record.source_record_ids
        source = source_by_id[source_record_id]
        source_step_id = kernel_artifact.source_component.split(":", 1)[1]
        observed.append(
            (
                artifact_record.artifact_id,
                source_step_id,
                artifact_record.evidence_class,
                source_record_id,
                source.source_type,
            )
        )
    source_id_by_type = {
        source.source_type: source.source_record_id
        for source in result.domain_projection.source_records
    }
    expected = tuple(
        (
            artifact_id,
            step_id,
            evidence_class,
            source_id_by_type[source_type],
            source_type,
        )
        for artifact_id, step_id, evidence_class, source_type in (
            EXPECTED_ARTIFACT_PROVENANCE
        )
    )
    assert tuple(observed) == expected
    packet_row = observed[20]
    assert packet_row[1:] == (
        "root_created_mock_action_commit_packet_observed",
        "CORRIDOR_EVIDENCE",
        source_id_by_type["supplier_packet_corridor_receipt_evidence"],
        "supplier_packet_corridor_receipt_evidence",
    )


def test_unknown_kernel_step_id_is_rejected():
    with pytest.raises(
        ValueError,
        match="^supplier_water_filter_sealed_evidence_adapter_geometry_invalid$",
    ):
        adapter._artifact_evidence_class("unknown_step")


def test_s_n2_and_s_p2_sources_bind_the_single_live_collection(result):
    projection = result.domain_projection
    source_by_type = {source.source_type: source for source in projection.source_records}
    for source_type in (
        "supplier_negative_conformance_matrix",
        "supplier_packet_corridor_receipt_evidence",
    ):
        assert result.safe_execution_id in source_by_type[source_type].trace_refs
    live_runtime = [
        source
        for source in projection.source_records
        if source.source_type == "supplier_live_execution_runtime"
    ]
    assert len(live_runtime) == 1
    assert (
        projection.source_provider_call_count,
        projection.source_network_call_count,
        projection.source_gemini_call_count,
    ) == (6, 6, 6)
    assert all(
        (
            source.observed_provider_call_count,
            source.observed_network_call_count,
            source.observed_gemini_call_count,
        ) == (0, 0, 0)
        for source in projection.source_records
        if source.source_type != "supplier_live_execution_runtime"
    )


def test_s_f1_public_packet_validator_rejects_missing_human_approval():
    packet = action_packet.build_supplier_a_mock_action_commit_packet_fixture_v02()
    changed = replace(packet, human_approval_ref="")
    valid, reasons = action_packet.validate_action_commit_packet_v02(changed)
    assert valid is False
    assert reasons == (action_packet.REASON_MISSING_HUMAN_APPROVAL_REF,)


def test_s_f2_public_corridor_validator_rejects_supplier_b_scope_widening():
    packet = action_packet.build_supplier_a_mock_action_commit_packet_fixture_v02()
    step = action_packet.build_supplier_a_corridor_step_fixture_v01(packet)
    changed = replace(
        step,
        allowed_subjects=(*step.allowed_subjects, action_packet.SUBJECT_SUPPLIER_B),
    )
    report = action_packet.validate_corridor_step_against_packet_v01(packet, changed)
    assert report.validation_status == action_packet.STATUS_FAIL_CLOSED
    assert report.reason_codes == (
        action_packet.REASON_CHILD_ALLOWED_NOT_SUBSET_OF_PARENT,
        action_packet.REASON_CHILD_SCOPE_NOT_SUBSET_OF_PARENT,
    )


def test_s_f3_public_receipt_validator_rejects_permission_creation():
    packet = action_packet.build_supplier_a_mock_action_commit_packet_fixture_v02()
    receipt = action_packet.build_supplier_a_mock_receipt_evidence_fixture_v01(packet)
    changed = replace(receipt, creates_action_permission=True)
    valid, reasons = action_packet.validate_mock_receipt_evidence_v01(packet, changed)
    assert valid is False
    assert reasons == (
        action_packet.REASON_RECEIPT_CANNOT_CREATE_FUTURE_PERMISSION,
    )


@pytest.mark.parametrize("field", ("kernel_artifacts", "causal_consumption_refs"))
def test_kernel_artifact_and_causal_reorder_is_rejected(context, kernel_result, field):
    changed = dict(context)
    value = getattr(kernel_result, field)
    changed["kernel_adapter_result"] = replace(kernel_result, **{field: tuple(reversed(value))})
    with pytest.raises(ValueError, match="kernel_invalid"):
        _build(changed)


def test_changed_kernel_manifest_hash_is_rejected_by_real_validator(context, kernel_result):
    changed = dict(context)
    manifest = replace(kernel_result.kernel_manifest, manifest_hash="f" * 64)
    changed["kernel_adapter_result"] = replace(kernel_result, kernel_manifest=manifest)
    with pytest.raises(ValueError, match="kernel_invalid"):
        _build(changed)


def test_multiroot_outcome_mutation_is_rejected(context, kernel_result):
    changed = dict(context)
    outcome = replace(kernel_result.multiroot_outcome, outcome_status="PASS")
    changed["kernel_adapter_result"] = replace(kernel_result, multiroot_outcome=outcome)
    with pytest.raises(ValueError, match="kernel_invalid"):
        _build(changed)


def _changed_result_value(result, field_name):
    value = getattr(result, field_name)
    if field_name == "adapter_result_id":
        return "0" * 64
    if field_name == "domain_projection":
        return replace(value, status="FAIL_CLOSED")
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
def test_every_result_field_participates_in_contextual_validation(result, context, field_name):
    forged = replace(result, **{field_name: _changed_result_value(result, field_name)})
    assert _validate(forged, context)


def test_self_rehashed_mixed_to_pass_forgery_is_rejected(result, context):
    changed = replace(result, business_outcome="PASS")
    forged = adapter._replace_result_id(changed, adapter._result_identity(changed))
    assert "supplier_water_filter_sealed_evidence_adapter_business_outcome_mismatch" in _validate(forged, context)


@pytest.mark.parametrize(
    "field",
    (
        "adapter_provider_call_count",
        "adapter_network_call_count",
        "adapter_gemini_call_count",
        "created_authority_count",
        "created_permission_count",
        "action_created_count",
        "receipt_created_count",
        "final_output_created_count",
        "real_world_effects_count",
    ),
)
@pytest.mark.parametrize("value", (1, True, False, 1.0, 0.0))
def test_exact_zero_adapter_counter_attacks_are_rejected(result, context, field, value):
    changed = replace(result, **{field: value})
    forged = adapter._replace_result_id(changed, adapter._result_identity(changed))
    assert _validate(forged, context)


def test_disposable_shared_sealed_package_seam_passes(result):
    projection = result.domain_projection
    files, contents = _package_members(projection)
    first = sealed_package.build_sealed_package_manifest_v01(
        domain_projection=projection,
        safe_file_records=files,
        safe_file_contents=contents,
        kernel_manifest_hash=result.kernel_manifest_hash,
    )
    second = sealed_package.build_sealed_package_manifest_v01(
        domain_projection=projection,
        safe_file_records=files,
        safe_file_contents=contents,
        kernel_manifest_hash=result.kernel_manifest_hash,
    )
    assert first.package_status == sealed_package.STATUS_SELF_CONSISTENT_UNANCHORED
    assert sealed_package.validate_sealed_package_manifest_v01(first, domain_projection=projection, safe_file_contents=contents) == ()
    assert first.file_count == 7
    assert first.artifact_count == 23
    assert first.package_content_hash == second.package_content_hash
    assert first.manifest_id == second.manifest_id


def test_package_seam_rejects_changed_kernel_manifest_hash(result):
    files, contents = _package_members(result.domain_projection)
    with pytest.raises(ValueError, match="^sealed_package_reference_unresolved$"):
        sealed_package.build_sealed_package_manifest_v01(
            domain_projection=result.domain_projection,
            safe_file_records=files,
            safe_file_contents=contents,
            kernel_manifest_hash="f" * 64,
        )


def test_package_seam_rejects_removed_integrity_trace(result):
    source = result.domain_projection.source_records[-1]
    changed_source = _rehash_source(replace(source, trace_refs=(result.kernel_adapter_id,)))
    projection = _projection_with_source(result.domain_projection, len(result.domain_projection.source_records) - 1, changed_source)
    assert profile.validate_domain_evidence_projection_v01(projection) == ()
    files, contents = _package_members(projection)
    with pytest.raises(ValueError, match="^sealed_package_reference_unresolved$"):
        sealed_package.build_sealed_package_manifest_v01(
            domain_projection=projection,
            safe_file_records=files,
            safe_file_contents=contents,
            kernel_manifest_hash=result.kernel_manifest_hash,
        )


def test_package_seam_rejects_incomplete_source_coverage(result):
    files, contents = _package_members(result.domain_projection)
    with pytest.raises(ValueError, match="^sealed_package_reference_unresolved$"):
        sealed_package.build_sealed_package_manifest_v01(
            domain_projection=result.domain_projection,
            safe_file_records=files[:-1],
            safe_file_contents=contents[:-1],
            kernel_manifest_hash=result.kernel_manifest_hash,
        )


def test_package_seam_rejects_changed_canonical_bytes(result):
    files, contents = _package_members(result.domain_projection)
    manifest = sealed_package.build_sealed_package_manifest_v01(
        domain_projection=result.domain_projection,
        safe_file_records=files,
        safe_file_contents=contents,
        kernel_manifest_hash=result.kernel_manifest_hash,
    )
    changed = (b'{"changed":true}\n', *contents[1:])
    assert "sealed_package_hash_mismatch" in sealed_package.validate_sealed_package_manifest_v01(
        manifest,
        domain_projection=result.domain_projection,
        safe_file_contents=changed,
    )


def test_public_projection_is_json_safe_and_copy_isolated(result, context):
    first = adapter.supplier_water_filter_sealed_evidence_package_adapter_result_to_plain_dict_v01(result, **context)
    second = adapter.supplier_water_filter_sealed_evidence_package_adapter_result_to_plain_dict_v01(result, **context)
    json.dumps(first, sort_keys=True)
    assert not _contains_forbidden(first)
    first["scenario_ids"][0] = "changed"
    first["domain_projection"]["evidence_refs"].append("changed")
    assert second["scenario_ids"][0] == "S-N1"
    assert "changed" not in result.domain_projection.evidence_refs


def test_builder_is_deterministic_and_inputs_are_unchanged(context):
    rows_before = copy.deepcopy(context["scenario_rows"])
    source_before = copy.deepcopy(context["source_report"])
    first = _build(context)
    second = _build(context)
    assert first == second
    assert context["scenario_rows"] == rows_before
    assert context["source_report"] == source_before


def test_static_forbidden_boundaries_and_no_demo_import():
    path = Path("hedgehog/domains/supplier_water_filter/sealed_evidence_package_adapter_v01.py")
    tree = ast.parse(path.read_text(encoding="utf-8"))
    import_modules = {
        node.module.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    } | {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    assert not import_modules.intersection(
        {"os", "pathlib", "tempfile", "subprocess", "socket", "requests", "urllib", "http", "google", "demo", "tests", "time", "random", "secrets", "uuid"}
    )
    imported_full = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    assert "hedgehog.evidence.sealed_package_v01" not in imported_full
    assert "hedgehog.evidence.external_anchor_v01" not in imported_full
    assert "hedgehog.evidence.sealed_replay_evidence_v01" not in imported_full
    calls = {
        node.func.id if isinstance(node.func, ast.Name) else node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, (ast.Name, ast.Attribute))
    }
    assert not calls.intersection(
        {"open", "read_text", "read_bytes", "write_text", "write_bytes", "mkdir", "glob", "rglob", "iterdir"}
    )
