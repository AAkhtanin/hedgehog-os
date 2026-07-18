from __future__ import annotations

import ast
import json
from dataclasses import FrozenInstanceError, dataclass, fields, replace
from pathlib import Path

import pytest

from hedgehog.domains.airline import crypto_artifact_seal_collector_v01 as collector
from hedgehog.domains.airline import crypto_artifact_seal_v01 as crypto
from hedgehog.domains.airline import kernel_adapter_v01 as adapter
from hedgehog.domains.airline import sealed_trace_replay_v01 as replay
from hedgehog.domains.airline import transaction_artifact_ledger_v01 as ledger
from hedgehog.kernel import abi_v01 as abi
from hedgehog.kernel import integrity_replay_v01 as integrity


MODULE_PATH = Path("hedgehog/domains/airline/kernel_adapter_v01.py")
PACKAGE_REF = "airline_kernel_adapter_fixture_v01"


@dataclass(frozen=True)
class _SourceFixture:
    replay_input: replay.AirlineSealedTraceReplayInputV01
    replay_report: replay.AirlineSealedTraceReplayReportV01


def _accepted_audit(
    item: ledger.AirlineTransactionArtifactLedgerV01,
    offer_id: str,
) -> collector.AirlineCryptoArtifactSealAcceptedLedgerAuditV01:
    values: dict[str, object] = {
        "audit_id": collector.EXPECTED_LEDGER_AUDIT_ID,
        "audit_version": collector.EXPECTED_LEDGER_AUDIT_VERSION,
        "final_status": collector.STATUS_PASS,
        "required_source_files": crypto.REQUIRED_SOURCE_FILE_REFS,
        "files_read_count": replay.SOURCE_FILE_COUNT,
        "ledger_id": item.ledger_id,
        "transaction_id": item.transaction_id,
        "selected_offer_id": offer_id,
        "source_run_ref": item.source_run_ref,
        "source_causal_report_ref": item.source_causal_report_ref,
        "source_corridor_report_ref": item.source_corridor_report_ref,
        "actual_entry_count": replay.LEDGER_ENTRY_COUNT,
        "actual_dependency_edge_count": replay.DEPENDENCY_EDGE_COUNT,
        "actual_root_final_count": replay.ROOT_FINAL_COUNT,
        "client_root_final_count": 1,
        "airline_root_final_count": 1,
        "bank_root_final_count": 1,
        **{
            field_name: True
            for field_name in collector.ACCEPTED_AUDIT_BOOLEAN_FIELDS
        },
        "stored_validation_status": collector.STATUS_PASS,
        "stored_validation_errors": (),
        **{
            field_name: 0
            for field_name in collector.ACCEPTED_AUDIT_ZERO_COUNTER_FIELDS
        },
        "validation_errors": (),
    }
    return collector.AirlineCryptoArtifactSealAcceptedLedgerAuditV01(
        **values,  # type: ignore[arg-type]
    )


def _forge_replay_report(
    report: replay.AirlineSealedTraceReplayReportV01,
    **changes: object,
) -> replay.AirlineSealedTraceReplayReportV01:
    if type(report) is not replay.AirlineSealedTraceReplayReportV01:
        raise TypeError("test_replay_report_type_invalid")
    field_names = {field.name for field in fields(report)}
    if set(changes) - field_names:
        raise TypeError("test_replay_report_field_unknown")
    forged = object.__new__(type(report))
    for field in fields(report):
        object.__setattr__(
            forged,
            field.name,
            changes.get(field.name, getattr(report, field.name)),
        )
    object.__setattr__(
        forged,
        "_constructed_by_replay_verifier_v01",
        getattr(report, "_constructed_by_replay_verifier_v01", False),
    )
    return forged


def _source_fixture(
    offer_id: str = adapter.SELECTED_OFFER_ID,
) -> _SourceFixture:
    item = ledger.build_airline_transaction_artifact_ledger_fixture_v01(
        offer_id=offer_id
    )
    identity = (
        ledger.build_airline_transaction_artifact_ledger_fixture_expected_identity_v01(
            offer_id=offer_id
        )
    )
    rows = tuple(
        (
            ref,
            f"airline-kernel-adapter:{offer_id}:{index}:{ref}".encode("utf-8"),
        )
        for index, ref in enumerate(crypto.REQUIRED_SOURCE_FILE_REFS)
    )
    core = crypto.build_airline_crypto_artifact_seal_manifest_core_v01(
        item,
        ordered_source_files=rows,
        source_package_ref=PACKAGE_REF,
        source_audit_status=crypto.STATUS_PASS,
        secret_scan_passed=True,
        expected_identity=identity,
    )
    envelope = crypto.build_airline_crypto_artifact_seal_envelope_v01(core)
    stored = crypto.verify_airline_crypto_artifact_seal_v01(
        envelope,
        ledger_item=item,
        ordered_source_files_before=rows,
        ordered_source_files_after=rows,
        expected_source_package_ref=PACKAGE_REF,
        source_audit_status=crypto.STATUS_PASS,
        secret_scan_passed=True,
        expected_manifest_core_hash=None,
        expected_identity=identity,
    )
    fresh = crypto.verify_airline_crypto_artifact_seal_v01(
        envelope,
        ledger_item=item,
        ordered_source_files_before=rows,
        ordered_source_files_after=rows,
        expected_source_package_ref=PACKAGE_REF,
        source_audit_status=crypto.STATUS_PASS,
        secret_scan_passed=True,
        expected_manifest_core_hash=envelope.manifest_core_hash,
        expected_identity=identity,
    )
    replay_input = replay.build_airline_sealed_trace_replay_input_v01(
        source_package_ref=PACKAGE_REF,
        accepted_ledger_audit=_accepted_audit(item, offer_id),
        ledger_item=item,
        envelope=envelope,
        stored_verification_report=stored,
        fresh_anchored_verification_report=fresh,
        expected_manifest_core_hash=envelope.manifest_core_hash,
        ordered_source_files=rows,
    )
    report = replay.verify_airline_sealed_trace_replay_v01(
        replay_input,
        critical_package_bytes_unchanged=True,
        post_replay_snapshot_provider_call_count=1,
    )
    return _SourceFixture(replay_input, report)


@pytest.fixture(scope="module")
def source_fixture() -> _SourceFixture:
    return _source_fixture()


@pytest.fixture(scope="module")
def result(
    source_fixture: _SourceFixture,
) -> adapter.AirlineKernelAdapterResultV01:
    return adapter.build_airline_kernel_adapter_result_v01(
        replay_input=source_fixture.replay_input,
        replay_report=source_fixture.replay_report,
    )


EXPECTED_FIELDS = (
    "adapter_id",
    "adapter_version",
    "transaction_id",
    "selected_offer_id",
    "source_package_ref",
    "source_replay_id",
    "source_manifest_core_hash",
    "source_stored_verification_status",
    "source_fresh_verification_status",
    "source_signature_verified",
    "root_ids",
    "kernel_artifacts",
    "kernel_manifest",
    "kernel_unanchored_verification",
    "kernel_anchored_verification",
    "kernel_replay",
    "causal_consumption_refs",
    "ledger_entry_count",
    "dependency_edge_count",
    "root_final_count",
    "source_file_count",
    "critical_file_count",
    "timeline_row_count",
    "provider_call_count",
    "network_call_count",
    "gemini_call_count",
    "real_world_effects_count",
)
EXPECTED_PUBLIC = {
    "MODULE_ID",
    "SLICE_ID",
    "ADAPTER_VERSION",
    "STATUS_PASS",
    "STATUS_BLOCKED_FAIL_CLOSED",
    "TRANSACTION_ID",
    "SELECTED_OFFER_ID",
    "ROOT_IDS",
    "LEDGER_ENTRY_COUNT",
    "DEPENDENCY_EDGE_COUNT",
    "ROOT_FINAL_COUNT",
    "SOURCE_FILE_COUNT",
    "CRITICAL_FILE_COUNT",
    "TIMELINE_ROW_COUNT",
    "AirlineKernelAdapterResultV01",
    "build_airline_kernel_adapter_result_v01",
    "validate_airline_kernel_adapter_result_v01",
    "airline_kernel_adapter_result_to_plain_dict_v01",
}
EXPECTED_MAPPING = (
    ("AirlineTransactionScopeV01", "SemanticEvidence", "NON_AUTHORITY", "VALIDATED"),
    ("ClientBSEPProjectionV01", "BSEPProjection", "ADVISORY", "VALIDATED"),
    ("AirlineBSEPProjectionV01", "BSEPProjection", "ADVISORY", "VALIDATED"),
    ("BankBSEPProjectionV01", "BSEPProjection", "ADVISORY", "VALIDATED"),
    ("CrossRootAdvisoryBSEPProjectionV01", "BSEPProjection", "ADVISORY", "VALIDATED"),
    ("ValidatedAirlineSemanticSelectionEvidenceV01", "ValidatedEvidence", "EVIDENCE_ONLY", "VALIDATED"),
    ("ClientRootOfferSelectionDecisionV01", "RootDecision", "ROOT_OWNED", "ROOT_ACCEPTED"),
    ("AirlineRootSelectedOfferResolutionV01", "RootDecision", "ROOT_OWNED", "ROOT_ACCEPTED"),
    ("AirlineOfferPacketV01", "ResultProposal", "ROOT_OWNED", "ROOT_ACCEPTED"),
    ("AirlineHoldCommitPacketV01", "RootOwnedIntent", "ROOT_OWNED", "ROOT_ACCEPTED"),
    ("AirlineOfferHoldReceiptV01", "EvidenceReceipt", "EVIDENCE_ONLY", "RECEIPT_RECORDED"),
    ("ClientPurchaseIntentV01", "RootOwnedIntent", "ROOT_OWNED", "ROOT_ACCEPTED"),
    ("BankPaymentAuthorizationRefV01", "CrossRootEvidenceRef", "EVIDENCE_ONLY", "VALIDATED"),
    ("AirlineTicketIssueIntentV01", "ExecutionRequest", "ROOT_AUTHORIZED", "ROOT_ACCEPTED"),
    ("MockTicketReceiptV01", "EvidenceReceipt", "EVIDENCE_ONLY", "RECEIPT_RECORDED"),
    ("MockPurchaseReceiptV01", "EvidenceReceipt", "EVIDENCE_ONLY", "RECEIPT_RECORDED"),
    ("ClientRootFinalV01", "RootFinal", "ROOT_OWNED", "FINALIZED"),
    ("AirlineRootFinalV01", "RootFinal", "ROOT_OWNED", "FINALIZED"),
    ("BankRootFinalV01", "RootFinal", "ROOT_OWNED", "FINALIZED"),
)


def test_public_surface_is_exact() -> None:
    assert {name for name in vars(adapter) if not name.startswith("_")} == EXPECTED_PUBLIC


def test_future_annotations_name_is_not_public() -> None:
    assert "annotations" not in vars(adapter)


def test_public_dataclass_is_frozen_and_slotted(
    result: adapter.AirlineKernelAdapterResultV01,
) -> None:
    assert hasattr(adapter.AirlineKernelAdapterResultV01, "__slots__")
    assert not hasattr(result, "__dict__")
    with pytest.raises(FrozenInstanceError):
        result.adapter_id = "changed"  # type: ignore[misc]


@pytest.mark.parametrize("index,name", tuple(enumerate(EXPECTED_FIELDS)))
def test_public_dataclass_field_order(index: int, name: str) -> None:
    assert fields(adapter.AirlineKernelAdapterResultV01)[index].name == name


@pytest.mark.parametrize(
    "name,value",
    (
        ("MODULE_ID", "airline_kernel_adapter_v01"),
        ("SLICE_ID", "domain_neutral_reference_kernel_gate1_g1d1"),
        ("ADAPTER_VERSION", "v0.1"),
        ("STATUS_PASS", "PASS"),
        ("STATUS_BLOCKED_FAIL_CLOSED", "BLOCKED_FAIL_CLOSED"),
        ("TRANSACTION_ID", "tri_airline_purchase:PAR-LIM:2026-08-12:client_001"),
        ("SELECTED_OFFER_ID", "offer:mock_airline_al:PAR-LIM:001"),
        ("ROOT_IDS", ("root:client_os_001", "root:mock_airline_al", "root:mock_bank_a")),
        ("LEDGER_ENTRY_COUNT", 19),
        ("DEPENDENCY_EDGE_COUNT", 29),
        ("ROOT_FINAL_COUNT", 3),
        ("SOURCE_FILE_COUNT", 9),
        ("CRITICAL_FILE_COUNT", 11),
        ("TIMELINE_ROW_COUNT", 19),
    ),
)
def test_constants_are_exact(name: str, value: object) -> None:
    assert getattr(adapter, name) == value


def test_valid_source_builds_and_validates(
    source_fixture: _SourceFixture,
    result: adapter.AirlineKernelAdapterResultV01,
) -> None:
    assert replay.validate_airline_sealed_trace_replay_input_v01(
        source_fixture.replay_input
    ).validation_status == replay.STATUS_PASS
    assert replay.validate_airline_sealed_trace_replay_report_v01(
        source_fixture.replay_report
    ).validation_status == replay.STATUS_PASS
    assert adapter.validate_airline_kernel_adapter_result_v01(
        replay_input=source_fixture.replay_input,
        replay_report=source_fixture.replay_report,
        result=result,
    ) == ()


def test_replay_report_forge_preserves_verifier_origin_and_valid_state(
    source_fixture: _SourceFixture,
) -> None:
    forged = _forge_replay_report(source_fixture.replay_report)
    assert forged is not source_fixture.replay_report
    assert getattr(forged, "_constructed_by_replay_verifier_v01") is True
    assert replay.validate_airline_sealed_trace_replay_report_v01(
        forged
    ).validation_status == replay.STATUS_PASS


def test_init_false_replay_report_mutations_use_only_forge_helper() -> None:
    source = Path(__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    forbidden_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "replace"
        and node.args
        and isinstance(node.args[0], ast.Attribute)
        and node.args[0].attr == "replay_report"
        and isinstance(node.args[0].value, ast.Name)
        and node.args[0].value.id == "source_fixture"
    ]
    forge_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "_forge_replay_report"
    ]
    assert forbidden_calls == []
    assert len(forge_calls) >= 4


@pytest.mark.parametrize("index,mapping", tuple(enumerate(EXPECTED_MAPPING)))
def test_exact_nineteen_type_mapping(
    index: int,
    mapping: tuple[str, str, str, str],
    result: adapter.AirlineKernelAdapterResultV01,
) -> None:
    artifact = result.kernel_artifacts[index]
    payload = abi.kernel_artifact_to_plain_dict_v01(artifact)["payload"]
    assert payload["airline_artifact_type"] == mapping[0]
    assert artifact.artifact_type == mapping[1]
    assert artifact.authority_class == mapping[2]
    assert artifact.lifecycle_state == mapping[3]


@pytest.mark.parametrize("index", tuple(range(19)))
def test_kernel_artifact_preserves_source_identity_and_order(
    index: int,
    source_fixture: _SourceFixture,
    result: adapter.AirlineKernelAdapterResultV01,
) -> None:
    row = source_fixture.replay_report.reconstructed_timeline[index]
    artifact = result.kernel_artifacts[index]
    assert artifact.artifact_id == row.artifact_id
    assert artifact.owner_root_id == row.root_owner
    assert artifact.parent_refs == row.depends_on
    assert artifact.trace_refs == (
        source_fixture.replay_input.source_package_ref,
        source_fixture.replay_report.replay_id,
        source_fixture.replay_input.ledger_item.ledger_id,
    )
    assert abi.validate_kernel_artifact_v01(artifact) == ()


PAYLOAD_KEYS = (
    "airline_ledger_index",
    "airline_event_time",
    "airline_event_type",
    "airline_artifact_type",
    "airline_artifact_hash",
    "airline_created_by",
    "airline_authority_class",
    "airline_evidence_class",
    "airline_is_root_final",
    "airline_selected_offer_id",
    "airline_canonical_hash_input",
)


@pytest.mark.parametrize("key", PAYLOAD_KEYS)
def test_payload_has_exact_required_key(
    key: str,
    result: adapter.AirlineKernelAdapterResultV01,
) -> None:
    payload = abi.kernel_artifact_to_plain_dict_v01(result.kernel_artifacts[0])[
        "payload"
    ]
    assert set(payload) == set(PAYLOAD_KEYS)
    assert key in payload


def test_generic_manifest_geometry_is_exact(
    result: adapter.AirlineKernelAdapterResultV01,
) -> None:
    manifest = result.kernel_manifest
    assert (
        manifest.artifact_count,
        manifest.dependency_edge_count,
        manifest.root_ownership_binding_count,
        manifest.evidence_class_binding_count,
        manifest.authority_class_binding_count,
    ) == (19, 29, 19, 19, 19)
    assert result.kernel_unanchored_verification.verification_status == (
        integrity.STATUS_SELF_CONSISTENT_UNANCHORED
    )
    assert result.kernel_anchored_verification.verification_status == "PASS"
    assert result.kernel_replay.replay_status == "PASS"


@pytest.mark.parametrize("index", tuple(range(19)))
def test_generic_replay_preserves_order_owner_and_dependency_count(
    index: int,
    result: adapter.AirlineKernelAdapterResultV01,
) -> None:
    artifact = result.kernel_artifacts[index]
    assert result.kernel_replay.reconstructed_artifact_ids[index] == artifact.artifact_id
    assert result.kernel_replay.reconstructed_artifact_types[index] == artifact.artifact_type
    assert result.kernel_replay.reconstructed_owner_root_ids[index] == artifact.owner_root_id
    assert result.kernel_replay.reconstructed_dependency_counts[index] == len(
        artifact.parent_refs
    )


def test_source_and_generic_manifest_hashes_are_distinct_identity_domains(
    result: adapter.AirlineKernelAdapterResultV01,
) -> None:
    assert len(result.source_manifest_core_hash) == 64
    assert len(result.kernel_manifest.manifest_hash) == 64
    assert result.source_manifest_core_hash != result.kernel_manifest.manifest_hash


@pytest.mark.parametrize("index", tuple(range(29)))
def test_every_dependency_has_one_exact_causal_ref(
    index: int,
    result: adapter.AirlineKernelAdapterResultV01,
) -> None:
    ref = result.causal_consumption_refs[index]
    artifact_by_id = {
        artifact.artifact_id: artifact for artifact in result.kernel_artifacts
    }
    assert ref.source_artifact_id in artifact_by_id
    assert ref.downstream_artifact_id in artifact_by_id
    assert ref.source_artifact_id in artifact_by_id[
        ref.downstream_artifact_id
    ].parent_refs
    assert ref.output_field == "/airline_artifact_hash"
    assert ref.decision_effect == "dependency_integrity_binding"
    assert ref.disposition == "USED"
    assert ref.reason_code == "used:airline_ledger_dependency_hash"
    assert abi.validate_causal_consumption_ref_v01(ref) == ()


def test_full_causal_bundle_validates(
    result: adapter.AirlineKernelAdapterResultV01,
) -> None:
    assert abi.validate_causal_consumption_bundle_v01(
        artifacts=result.kernel_artifacts,
        causal_refs=result.causal_consumption_refs,
    ) == ()


def test_causal_order_matches_ledger_and_each_depends_on_order(
    source_fixture: _SourceFixture,
    result: adapter.AirlineKernelAdapterResultV01,
) -> None:
    expected = tuple(
        (parent_id, row.artifact_id)
        for row in source_fixture.replay_report.reconstructed_timeline
        for parent_id in row.depends_on
    )
    actual = tuple(
        (ref.source_artifact_id, ref.downstream_artifact_id)
        for ref in result.causal_consumption_refs
    )
    assert actual == expected


@pytest.mark.parametrize(
    "field,value",
    (
        ("transaction_id", "wrong:transaction"),
        ("source_package_ref", "wrong:package"),
        ("manifest_core_hash", "0" * 64),
        ("expected_manifest_core_hash", "1" * 64),
        ("stored_verification_status", "PASS"),
        ("fresh_anchored_verification_status", "SELF_CONSISTENT_UNANCHORED"),
        ("external_anchor_supplied", False),
        ("external_anchor_verified", False),
        ("signature_verified", True),
        ("source_bytes_unchanged", False),
        ("critical_package_bytes_unchanged", False),
        ("transaction_rerun_count", 1),
        ("semantic_rerun_count", 1),
        ("corridor_rerun_count", 1),
        ("ledger_recollection_count", 1),
        ("crypto_collection_count", 1),
        ("provider_call_count", 1),
        ("network_call_count", 1),
        ("gemini_call_count", 1),
        ("replay_created_authority_count", 1),
        ("replay_created_permission_count", 1),
        ("replay_created_action_count", 1),
        ("replay_created_packet_count", 1),
        ("replay_created_receipt_count", 1),
        ("replay_created_final_output_count", 1),
        ("real_world_effects_count", 1),
    ),
)
def test_changed_source_report_is_rejected(
    field: str,
    value: object,
    source_fixture: _SourceFixture,
) -> None:
    changed = _forge_replay_report(
        source_fixture.replay_report,
        **{field: value},
    )
    errors = adapter.validate_airline_kernel_adapter_result_v01(
        replay_input=source_fixture.replay_input,
        replay_report=changed,
        result=object(),
    )
    expected_reason = (
        "airline_kernel_adapter_source_binding_mismatch"
        if field == "source_package_ref"
        else "airline_kernel_adapter_source_replay_invalid"
    )
    assert expected_reason in errors
    assert "airline_kernel_adapter_unexpected_exception" not in errors


def test_offer_b_is_rejected() -> None:
    fixture = _source_fixture(ledger.OFFER_B_ID)
    assert replay.validate_airline_sealed_trace_replay_input_v01(
        fixture.replay_input
    ).validation_status == replay.STATUS_PASS
    assert replay.validate_airline_sealed_trace_replay_report_v01(
        fixture.replay_report
    ).validation_status == replay.STATUS_PASS
    with pytest.raises(
        ValueError,
        match="^airline_kernel_adapter_source_binding_mismatch$",
    ):
        adapter.build_airline_kernel_adapter_result_v01(
            replay_input=fixture.replay_input,
            replay_report=fixture.replay_report,
        )


@pytest.mark.parametrize(
    "field,value",
    (
        ("ledger_entry_count", 18),
        ("ledger_entry_count", 20),
        ("dependency_edge_count", 28),
        ("dependency_edge_count", 30),
        ("root_final_count", 2),
        ("root_final_count", 4),
        ("source_file_count", 8),
        ("source_file_count", 10),
        ("critical_package_file_count", 10),
        ("critical_package_file_count", 12),
        ("timeline_row_count", 18),
        ("timeline_row_count", 20),
    ),
)
def test_source_geometry_mutation_is_rejected(
    field: str,
    value: int,
    source_fixture: _SourceFixture,
) -> None:
    changed = _forge_replay_report(
        source_fixture.replay_report,
        **{field: value},
    )
    errors = adapter.validate_airline_kernel_adapter_result_v01(
        replay_input=source_fixture.replay_input,
        replay_report=changed,
        result=object(),
    )
    assert "airline_kernel_adapter_source_replay_invalid" in errors
    assert "airline_kernel_adapter_unexpected_exception" not in errors


@pytest.mark.parametrize("row_count", (18, 20))
def test_source_timeline_row_geometry_is_rejected(
    row_count: int,
    source_fixture: _SourceFixture,
) -> None:
    timeline = source_fixture.replay_report.reconstructed_timeline
    changed_rows = timeline[:18] if row_count == 18 else (*timeline, timeline[-1])
    changed = _forge_replay_report(
        source_fixture.replay_report,
        timeline_row_count=row_count,
        reconstructed_timeline=changed_rows,
    )
    errors = adapter.validate_airline_kernel_adapter_result_v01(
        replay_input=source_fixture.replay_input,
        replay_report=changed,
        result=object(),
    )
    assert "airline_kernel_adapter_source_replay_invalid" in errors
    assert "airline_kernel_adapter_unexpected_exception" not in errors


RESULT_MUTATIONS = (
    ("adapter_id", "0" * 64),
    ("adapter_version", "v9"),
    ("transaction_id", "wrong:transaction"),
    ("selected_offer_id", "offer:wrong"),
    ("source_package_ref", "wrong:package"),
    ("source_replay_id", "wrong:replay"),
    ("source_manifest_core_hash", "0" * 64),
    ("source_stored_verification_status", "PASS"),
    ("source_fresh_verification_status", "BLOCKED_FAIL_CLOSED"),
    ("source_signature_verified", True),
    ("root_ids", tuple(reversed(adapter.ROOT_IDS))),
    ("kernel_artifacts", None),
    ("kernel_manifest", None),
    ("kernel_unanchored_verification", None),
    ("kernel_anchored_verification", None),
    ("kernel_replay", None),
    ("causal_consumption_refs", None),
    ("ledger_entry_count", 18),
    ("dependency_edge_count", 28),
    ("root_final_count", 2),
    ("source_file_count", 8),
    ("critical_file_count", 10),
    ("timeline_row_count", 18),
    ("provider_call_count", 1),
    ("network_call_count", 1),
    ("gemini_call_count", 1),
    ("real_world_effects_count", 1),
)


@pytest.mark.parametrize("field,value", RESULT_MUTATIONS)
def test_every_public_result_field_mutation_fails_contextual_validation(
    field: str,
    value: object,
    source_fixture: _SourceFixture,
    result: adapter.AirlineKernelAdapterResultV01,
) -> None:
    if field == "kernel_artifacts":
        value = result.kernel_artifacts[:-1]
    elif field == "kernel_manifest":
        value = replace(result.kernel_manifest, artifact_count=18)
    elif field == "kernel_unanchored_verification":
        value = replace(
            result.kernel_unanchored_verification,
            verification_status="PASS",
        )
    elif field == "kernel_anchored_verification":
        value = replace(
            result.kernel_anchored_verification,
            verification_status="BLOCKED_FAIL_CLOSED",
        )
    elif field == "kernel_replay":
        value = replace(result.kernel_replay, artifact_count=18)
    elif field == "causal_consumption_refs":
        value = result.causal_consumption_refs[:-1]
    changed = replace(result, **{field: value})
    errors = adapter.validate_airline_kernel_adapter_result_v01(
        replay_input=source_fixture.replay_input,
        replay_report=source_fixture.replay_report,
        result=changed,
    )
    assert errors
    assert any(error != "airline_kernel_adapter_id_mismatch" for error in errors)


@pytest.mark.parametrize(
    "field,value,reason",
    (
        ("provider_call_count", 1, "airline_kernel_adapter_authority_creation_forbidden"),
        ("network_call_count", 1, "airline_kernel_adapter_authority_creation_forbidden"),
        ("gemini_call_count", 1, "airline_kernel_adapter_authority_creation_forbidden"),
        ("real_world_effects_count", 1, "airline_kernel_adapter_effect_creation_forbidden"),
    ),
)
def test_self_rehashed_forbidden_counter_mutation_has_semantic_reason(
    field: str,
    value: int,
    reason: str,
    source_fixture: _SourceFixture,
    result: adapter.AirlineKernelAdapterResultV01,
) -> None:
    changed = replace(result, **{field: value})
    changed = replace(changed, adapter_id=adapter._adapter_id(changed))
    assert reason in adapter.validate_airline_kernel_adapter_result_v01(
        replay_input=source_fixture.replay_input,
        replay_report=source_fixture.replay_report,
        result=changed,
    )


@pytest.mark.parametrize(
    "mutation",
    ("pointer", "consumer", "reverse"),
)
def test_self_rehashed_causal_mutation_is_rejected(
    mutation: str,
    source_fixture: _SourceFixture,
    result: adapter.AirlineKernelAdapterResultV01,
) -> None:
    refs = list(result.causal_consumption_refs)
    if mutation == "pointer":
        refs[0] = replace(refs[0], output_field="/missing_hash")
    elif mutation == "consumer":
        refs[0] = replace(refs[0], consumer_component="wrong_consumer")
    else:
        refs[0] = replace(
            refs[0],
            source_artifact_id=refs[0].downstream_artifact_id,
            downstream_artifact_id=refs[0].source_artifact_id,
        )
    changed = replace(result, causal_consumption_refs=tuple(refs))
    changed = replace(changed, adapter_id=adapter._adapter_id(changed))
    errors = adapter.validate_airline_kernel_adapter_result_v01(
        replay_input=source_fixture.replay_input,
        replay_report=source_fixture.replay_report,
        result=changed,
    )
    assert "airline_kernel_adapter_causal_projection_invalid" in errors


def test_duplicate_causal_bundle_reaches_semantic_validator_without_rehash(
    source_fixture: _SourceFixture,
    result: adapter.AirlineKernelAdapterResultV01,
) -> None:
    refs = list(result.causal_consumption_refs)
    refs[1] = refs[0]
    changed = replace(result, causal_consumption_refs=tuple(refs))
    errors = adapter.validate_airline_kernel_adapter_result_v01(
        replay_input=source_fixture.replay_input,
        replay_report=source_fixture.replay_report,
        result=changed,
    )
    assert "airline_kernel_adapter_causal_projection_invalid" in errors
    assert any(error != "airline_kernel_adapter_id_mismatch" for error in errors)


def test_reordered_self_rehashed_causal_rows_fail_every_public_boundary(
    source_fixture: _SourceFixture,
    result: adapter.AirlineKernelAdapterResultV01,
) -> None:
    changed = replace(
        result,
        causal_consumption_refs=tuple(reversed(result.causal_consumption_refs)),
    )
    changed = replace(changed, adapter_id=adapter._adapter_id(changed))
    assert "airline_kernel_adapter_causal_projection_invalid" in (
        adapter._result_structure_errors(changed)
    )
    assert "airline_kernel_adapter_causal_projection_invalid" in (
        adapter.validate_airline_kernel_adapter_result_v01(
            replay_input=source_fixture.replay_input,
            replay_report=source_fixture.replay_report,
            result=changed,
        )
    )
    with pytest.raises(ValueError, match="^airline_kernel_adapter_invalid$"):
        adapter.airline_kernel_adapter_result_to_plain_dict_v01(changed)


def test_determinism_and_projection_isolation(
    source_fixture: _SourceFixture,
    result: adapter.AirlineKernelAdapterResultV01,
) -> None:
    source_rows_before = source_fixture.replay_input.ordered_source_files
    source_report_before = replay.airline_sealed_trace_replay_report_to_plain_dict_v01(
        source_fixture.replay_report
    )
    repeated = adapter.build_airline_kernel_adapter_result_v01(
        replay_input=source_fixture.replay_input,
        replay_report=source_fixture.replay_report,
    )
    first = adapter.airline_kernel_adapter_result_to_plain_dict_v01(result)
    second = adapter.airline_kernel_adapter_result_to_plain_dict_v01(repeated)
    assert result == repeated
    assert result.adapter_id == repeated.adapter_id
    assert first == second
    first["root_ids"].append("changed")  # type: ignore[union-attr]
    assert adapter.airline_kernel_adapter_result_to_plain_dict_v01(result) == second
    assert integrity.canonical_json_bytes_v01(second)
    assert json.loads(json.dumps(second)) == second
    assert source_fixture.replay_input.ordered_source_files == source_rows_before
    assert replay.airline_sealed_trace_replay_report_to_plain_dict_v01(
        source_fixture.replay_report
    ) == source_report_before


@pytest.mark.parametrize("malformed", (None, {}, object(), "result"))
def test_projection_rejects_malformed_input_with_stable_reason(
    malformed: object,
) -> None:
    with pytest.raises(ValueError, match="^airline_kernel_adapter_invalid$"):
        adapter.airline_kernel_adapter_result_to_plain_dict_v01(malformed)  # type: ignore[arg-type]


def test_projection_contains_no_tuple_bytes_or_dataclass(
    result: adapter.AirlineKernelAdapterResultV01,
) -> None:
    projection = adapter.airline_kernel_adapter_result_to_plain_dict_v01(result)

    def walk(value: object) -> None:
        assert not isinstance(value, (tuple, bytes))
        assert not hasattr(value, "__dataclass_fields__")
        if isinstance(value, dict):
            for child in value.values():
                walk(child)
        elif isinstance(value, list):
            for child in value:
                walk(child)

    walk(projection)


@pytest.mark.parametrize(
    "forbidden_root",
    (
        "demo",
        "tests",
        "providers",
        "config",
        "os",
        "pathlib",
        "tempfile",
        "shutil",
        "subprocess",
        "socket",
        "requests",
        "urllib",
    ),
)
def test_static_import_boundary(forbidden_root: str) -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    roots = {
        alias.name.split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    roots.update(
        (node.module or "").split(".")[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
    )
    assert forbidden_root not in roots


@pytest.mark.parametrize(
    "forbidden_call",
    (
        "open",
        "read",
        "write",
        "exec",
        "eval",
        "compile",
        "__import__",
        "register_provider",
        "register_adapter",
        "execute_effect",
        "execute_real_effect",
        "create_permission",
        "create_authority",
    ),
)
def test_static_call_boundary(forbidden_call: str) -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    called = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert forbidden_call not in called


def test_static_dependencies_are_exact() -> None:
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    }
    assert modules == {
        "__future__",
        "dataclasses",
        "hedgehog.domains.airline",
        "hedgehog.kernel",
    }


def test_no_filesystem_or_effect_public_function() -> None:
    public_functions = {
        name
        for name, value in vars(adapter).items()
        if not name.startswith("_") and callable(value) and name[0].islower()
    }
    assert public_functions == {
        "build_airline_kernel_adapter_result_v01",
        "validate_airline_kernel_adapter_result_v01",
        "airline_kernel_adapter_result_to_plain_dict_v01",
    }
