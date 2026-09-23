"""Deterministic two-domain G2-B semantic reuse and writeback proof."""

from __future__ import annotations

from dataclasses import dataclass as _dataclass
from dataclasses import fields as _fields
from dataclasses import replace as _replace
import hashlib as _hashlib
import json as _json
from tempfile import TemporaryDirectory as _TemporaryDirectory
from pathlib import Path as _Path

from hedgehog.drs import (
    LocalDRS as _LocalDRS,
    _safe_filename as _safe_filename,
)
from hedgehog.drs_g2b_compatibility_v01 import (
    LegacyDRSProjectionV01 as _LegacyDRSProjectionV01,
    legacy_drs_projection_to_plain_data_v01 as _legacy_plain,
    project_legacy_drs_source_v01 as _project_legacy,
    validate_legacy_drs_projection_v01 as _validate_legacy,
)
from hedgehog.drs_memory_resolution_v01 import (
    DRSResolutionReportV01 as _DRSResolutionReportV01,
    DRSTemporalQueryV01 as _DRSTemporalQueryV01,
    MemoryDescentBudgetV01 as _MemoryDescentBudgetV01,
    MemoryDescentRequestV01 as _MemoryDescentRequestV01,
    MemoryDescentResultV01 as _MemoryDescentResultV01,
    QueryEvaluationStateV01 as _QueryEvaluationStateV01,
    ResolutionCandidateV01 as _ResolutionCandidateV01,
    RetrievalPlanV01 as _RetrievalPlanV01,
    build_drs_resolution_report_v01 as _build_report,
    build_drs_temporal_query_v01 as _build_query,
    build_memory_descent_budget_v01 as _build_budget,
    build_memory_descent_request_v01 as _build_descent_request,
    build_resolution_candidate_v01 as _build_candidate,
    build_retrieval_plan_v01 as _build_plan,
    drs_resolution_report_to_plain_data_v01 as _report_plain,
    drs_temporal_query_to_plain_data_v01 as _query_plain,
    evaluate_drs_candidate_v01 as _evaluate,
    execute_local_memory_descent_v01 as _execute_descent,
    memory_descent_budget_to_plain_data_v01 as _budget_plain,
    memory_descent_request_to_plain_data_v01 as _request_plain,
    memory_descent_result_to_plain_data_v01 as _result_plain,
    query_evaluation_state_to_plain_data_v01 as _evaluation_plain,
    rank_eligible_drs_candidates_v01 as _rank,
    resolution_candidate_to_plain_data_v01 as _candidate_plain,
    retrieval_plan_to_plain_data_v01 as _plan_plain,
    validate_drs_resolution_report_v01 as _validate_report,
)
from hedgehog.drs_semantic_address_v01 import (
    DRSAuthorityEnvelopeV01 as _DRSAuthorityEnvelopeV01,
    DRSTimeEnvelopeV01 as _DRSTimeEnvelopeV01,
    LineageEdgeV01 as _LineageEdgeV01,
    MeaningRecordV01 as _MeaningRecordV01,
    MemoryPointerV01 as _MemoryPointerV01,
    SemanticAddressV01 as _SemanticAddressV01,
    build_drs_authority_envelope_v01 as _build_authority,
    build_drs_time_envelope_v01 as _build_time,
    build_lineage_edge_v01 as _build_edge,
    build_meaning_record_v01 as _build_record,
    build_memory_pointer_v01 as _build_pointer,
    build_semantic_address_v01 as _build_address,
    drs_authority_envelope_to_plain_data_v01 as _authority_plain,
    drs_time_envelope_to_plain_data_v01 as _time_plain,
    lineage_edge_to_plain_data_v01 as _edge_plain,
    meaning_record_to_plain_data_v01 as _meaning_plain,
    memory_pointer_to_plain_data_v01 as _memory_pointer_plain,
    semantic_address_to_plain_data_v01 as _address_plain,
    validate_meaning_record_v01 as _validate_meaning,
)
from hedgehog.kernel.integrity_replay_v01 import (
    canonical_json_bytes_v01 as _canonical_bytes,
    domain_separated_sha256_hex_v01 as _domain_hash,
)
from hedgehog.kernel.root_decision_v01 import (
    RootDecisionInputV01 as _RootDecisionInputV01,
    RootDecisionKernelV01 as _RootDecisionKernelV01,
    RootDecisionResultV01 as _RootDecisionResultV01,
    build_root_decision_input_v01 as _build_root_input,
    build_root_decision_kernel_v01 as _build_root_kernel,
    decide_root_v01 as _decide_root,
    root_decision_input_to_plain_dict_v01 as _root_input_plain,
    root_decision_kernel_to_plain_dict_v01 as _root_kernel_plain,
    root_decision_result_to_plain_dict_v01 as _root_result_plain,
)
from hedgehog.kernel.semantic_work_v01 import (
    EVIDENCE_STATE_PRESENT as _EVIDENCE_PRESENT,
    build_actor_contribution_v01 as _build_contribution,
    build_evidence_binding_v01 as _build_evidence,
    build_normalized_claim_v01 as _build_claim,
    build_root_review_packet_from_contributions_v01 as _build_packet,
    build_semantic_work_request_v01 as _build_work_request,
)
from hedgehog.kernel.trust_model_v01 import (
    build_default_component_trust_profiles_v01 as _trust_profiles,
)
from hedgehog.local_drs_resolver import (
    _g2b_action_request_reason_v01 as _action_reason,
    _g2b_read_local_records_v01 as _pure_read,
    _g2b_storage_record_v01 as _storage_record,
    _g2b_store_snapshot_v01 as _store_snapshot,
    _g2b_validate_root_reviewed_writeback_geometry_v01
    as _validate_writeback_geometry,
    _g2b_write_root_reviewed_meaning_record_v01 as _write_successor,
    _g2b_writeback_claim_preimage_v01 as _writeback_claim_preimage,
    _g2b_writeback_root_result_hash_v01 as _writeback_root_hash,
    _g2b_wrapper_matches_v01 as _wrapper_matches,
)
from hedgehog.reuse_certificate_v01 import (
    ReuseCertificateV01 as _ReuseCertificateV01,
    RootShortcutAuthorizationProjectionV01 as _RootProjectionV01,
    build_reuse_certificate_v01 as _build_certificate,
    build_root_shortcut_authorization_projection_v01 as _build_projection,
    reuse_certificate_to_plain_data_v01 as _certificate_plain,
    root_shortcut_authorization_projection_to_plain_data_v01 as _projection_plain,
    validate_existing_root_shortcut_decision_v01 as _validate_shortcut,
)


_PROFILE_VERSION = "v0.1"
_PROFILE_ID = "g2b_two_domain_semantic_address_reuse_certificate_v01"
_REPORT_DOMAIN = "hedgehog:drs:g2b:two_domain_proof:v01"
_REPORT_PREFIX = "g2bproof_v01:"
_SHA_A = "a" * 64
_ROOT_OWNER = "root:local_reference"
_POLICY = "policy_v01"
_SCHEMAS = ("v0.1",)
_FRESHNESS = "freshness:g2b5_v01"
_EVIDENCE_CLASSES = (
    "SOURCE_IDENTITY",
    "SOURCE_INTEGRITY",
    "PROVENANCE_CHAIN",
    "TIME_FITNESS",
    "POLICY_COMPATIBILITY",
    "SCHEMA_COMPATIBILITY",
    "CONFLICT_CLEARANCE",
    "ROOT_DECISION",
    "SOURCE_HISTORY",
)
_TIME_AXES = ("PT", "KT", "ET", "CT", "TTL", "VALIDITY")
_B3_ROOT_DOMAIN = (
    "hedgehog:drs:memory_descent_root_result_binding:v01"
)
_B3_ROOT_PREDICATE = "approve_controlled_memory_descent_plan_v01"
_B4_ROOT_DOMAIN = "hedgehog:drs:root_shortcut_root_result_binding:v01"
_B4_ROOT_PREDICATE = (
    "authorize_non_action_informational_answer_shortcut_v01"
)
_B4_POLICY_REF = "policy:drs_answer_shortcut:v0.1"
_WRITEBACK_PREDICATE = (
    "authorize_g2b_immutable_meaning_record_writeback_v01"
)


@_dataclass(frozen=True)
class _G2B5DomainSpecV01:
    domain_id: str
    namespace: str
    subject_class: str
    meaning_schema_id: str
    claim_dimension: str
    positive_question: str
    safe_summary: str
    context_summary: str
    negative_requests: tuple[str, ...]
    negative_reason_codes: tuple[str, ...]
    semantic_tags: tuple[str, ...]


@_dataclass(frozen=True)
class _G2B5DomainProofV01:
    profile_version: str
    domain_id: str
    positive_question: str
    negative_requests: tuple[str, ...]
    negative_reason_codes: tuple[str, ...]
    semantic_address: object
    legacy_source_records: tuple[dict[str, object], ...]
    source_projections: tuple[object, ...]
    source_records: tuple[object, ...]
    answer_report: object
    shortcut_root_kernel: object
    shortcut_root_decision_input: object
    shortcut_root_decision_result: object
    answer_use_time: int
    context_report: object
    descent_proposed_budget: object
    descent_request: object
    descent_root_kernel: object
    descent_root_decision_input: object
    descent_root_decision_result: object
    successor_commitment_record: object
    successor_record: object
    writeback_root_kernel: object
    writeback_root_decision_input: object
    writeback_root_decision_result: object
    writeback_evidence: dict[str, object]
    pure_read_snapshot_before: tuple[tuple[object, ...], ...]
    pure_read_snapshot_after: tuple[tuple[object, ...], ...]
    final_status: str
    reason_codes: tuple[str, ...]


@_dataclass(frozen=True)
class _G2B5DeterministicReportV01:
    report_version: str
    report_id: str
    profile_id: str
    domain_order: tuple[str, ...]
    domain_results: tuple[_G2B5DomainProofV01, ...]
    operation_counters: tuple[tuple[str, int], ...]
    closed_programme_counters: tuple[tuple[str, int], ...]
    raw_user_request_to_query_cross_binding_implemented: bool
    production_generic_informational_responder_claimed: bool
    final_status: str
    reason_codes: tuple[str, ...]


_DOMAIN_SPECS_V01 = (
    _G2B5DomainSpecV01(
        domain_id="TRAVEL_POLICY_INFORMATION",
        namespace="local_reference",
        subject_class="travel_policy",
        meaning_schema_id="drs_meaning_record",
        claim_dimension="travel_policy_summary",
        positive_question=(
            "retrieve a current bounded travel-policy summary"
        ),
        safe_summary="Current bounded travel-policy summary.",
        context_summary="Bounded travel-policy context.",
        negative_requests=(
            "buy ticket",
            "reserve seat",
            "use payment reference",
            "issue ticket",
        ),
        negative_reason_codes=(
            "drs_ticket_shortcut_forbidden",
            "drs_ticket_shortcut_forbidden",
            "drs_payment_shortcut_forbidden",
            "drs_ticket_shortcut_forbidden",
        ),
        semantic_tags=(
            "travel",
            "policy",
            "informational",
            "claim_dimension:travel_policy_summary",
        ),
    ),
    _G2B5DomainSpecV01(
        domain_id="WAREHOUSE_MAINTENANCE_INFORMATION",
        namespace="local_reference",
        subject_class="warehouse_maintenance",
        meaning_schema_id="drs_meaning_record",
        claim_dimension="maintenance_interval_summary",
        positive_question=(
            "retrieve a current bounded maintenance-interval summary"
        ),
        safe_summary="Current bounded maintenance-interval summary.",
        context_summary="Bounded warehouse-maintenance context.",
        negative_requests=(
            "release shipment",
            "order replacement part",
            "authorize supplier payment",
            "execute maintenance action",
        ),
        negative_reason_codes=(
            "drs_shipment_shortcut_forbidden",
            "drs_action_intent_shortcut_forbidden",
            "drs_payment_shortcut_forbidden",
            "drs_action_intent_shortcut_forbidden",
        ),
        semantic_tags=(
            "warehouse",
            "maintenance",
            "informational",
            "claim_dimension:maintenance_interval_summary",
        ),
    ),
)


def _source_geometry_v01(
    spec: _G2B5DomainSpecV01,
) -> tuple[
    _SemanticAddressV01,
    _MeaningRecordV01,
    _MeaningRecordV01,
    _MemoryPointerV01,
    str,
]:
    if type(spec) is not _G2B5DomainSpecV01:
        raise ValueError("g2b_report_fail_closed") from None
    address = _build_address(
        namespace=spec.namespace,
        domain=spec.domain_id.lower(),
        subject_class=spec.subject_class,
        intent_class="informational_summary",
        meaning_schema_id=spec.meaning_schema_id,
        meaning_schema_version=_PROFILE_VERSION,
    )
    scope_hash = _fixture_hash(spec, "scope")
    context = _build_record(
        semantic_address=address,
        predecessor_record_id=None,
        supersession_reason=None,
        safe_summary=spec.context_summary,
        semantic_tags=spec.semantic_tags,
        resonance_reason="Exact bounded local context.",
        memory_pointers=(),
        artifact_pointers=(),
        source_reference_ids=(
            f"source:{spec.domain_id.lower()}:context",
        ),
        lineage_edges=(),
        time_envelope=_domain_time(100),
        authority_envelope=_domain_authority(
            scope_hash=scope_hash,
            authority_class="ROOT_ACCEPTED_CONTEXT",
            acceptance_state="ACCEPTED_CONTEXT",
            label=f"{spec.domain_id}:context",
        ),
        persistent_lifecycle_state="ACTIVE",
        risk_hints=(),
        conflict_hints=(),
        reuse_policy_class="CONTEXT_ONLY",
        policy_version=_POLICY,
        schema_versions=_SCHEMAS,
        content_fingerprint=_fixture_hash(spec, "context-content"),
        recording_component="g2b5_fixture",
    )
    pointer = _build_pointer(
        storage_class="LOCAL_MEANING_RECORD",
        object_reference=context.meaning_record_id,
        content_sha256=context.content_fingerprint,
        record_class="MeaningRecordV01",
        byte_length=None,
        access_policy_id="policy:g2b5:summary",
        sensitivity_class="INTERNAL",
        allowed_use_classes=("SUMMARY_ONLY",),
        forbidden_use_classes=(),
        summary_read_permitted=True,
        payload_read_permitted=False,
    )
    predecessor = _build_record(
        semantic_address=address,
        predecessor_record_id=None,
        supersession_reason=None,
        safe_summary=spec.safe_summary,
        semantic_tags=spec.semantic_tags,
        resonance_reason="Current Root-accepted bounded information.",
        memory_pointers=(pointer,),
        artifact_pointers=(),
        source_reference_ids=(
            f"source:{spec.domain_id.lower()}:work",
        ),
        lineage_edges=(),
        time_envelope=_domain_time(100),
        authority_envelope=_domain_authority(
            scope_hash=scope_hash,
            authority_class="ROOT_ACCEPTED_WORK",
            acceptance_state="ACCEPTED_WORK",
            label=f"{spec.domain_id}:work",
        ),
        persistent_lifecycle_state="ACTIVE",
        risk_hints=(),
        conflict_hints=(),
        reuse_policy_class="ANSWER_SHORTCUT",
        policy_version=_POLICY,
        schema_versions=_SCHEMAS,
        content_fingerprint=_fixture_hash(spec, "work-content"),
        recording_component="g2b5_fixture",
    )
    return address, predecessor, context, pointer, scope_hash


def _collect_domain_v01(
    spec: _G2B5DomainSpecV01,
) -> _G2B5DomainProofV01:
    (
        address,
        predecessor,
        context,
        pointer,
        scope_hash,
    ) = _source_geometry_v01(spec)
    source_records = (predecessor, context)
    with _TemporaryDirectory(prefix="g2b5_") as directory:
        drs = _LocalDRS(_Path(directory))
        for record in source_records:
            drs.write_record(
                _storage_record(
                    meaning_record=record,
                    writeback_metadata={},
                )
            )
        snapshot_before = _store_snapshot(drs.root_path)
        pure_records = _pure_read(drs=drs, layers=("work",))
        snapshot_after = _store_snapshot(drs.root_path)
        pure_by_id = {
            item["record_id"]: item for item in pure_records
        }
        legacy_records = tuple(
            pure_by_id[record.meaning_record_id]
            for record in source_records
        )
        projections = tuple(
            _project_legacy(
                source_family="LOCAL_DRS_DICT",
                source=wrapper,
                target_semantic_address=address,
                target_meaning_record=None,
            )
            for wrapper in legacy_records
        )
        answer_query = _domain_query(
            address=address,
            scope_hash=scope_hash,
            query_mode="DIRECT_REUSE_CANDIDATE",
            reuse_intent="INFORMATIONAL_SHORTCUT_CONSIDERATION",
            requested_reuse_classes=("ANSWER_SHORTCUT",),
            required_time_axes=_TIME_AXES,
            evaluation_time_source="INJECTED_CURRENT_DECISION_TIME",
        )
        answer_evaluations = tuple(
            _evaluate(
                semantic_address=address,
                query=answer_query,
                meaning_record=record,
            )
            for record in source_records
        )
        answer_candidates = tuple(
            _domain_candidate(
                query=answer_query,
                evaluation=evaluation,
                record=record,
                similarity=9000 - index * 1000,
            )
            for index, (evaluation, record) in enumerate(
                zip(answer_evaluations, source_records, strict=True)
            )
            if evaluation.eligible_for_ranking
        )
        ranked = _rank(
            query=answer_query,
            query_evaluations=answer_evaluations,
            candidates=answer_candidates,
        )
        budget = _build_budget(
            max_depth=1,
            max_records_opened=2,
            max_pointers_opened=1,
            max_artifacts_opened=0,
            max_bytes_opened=0,
            max_lineage_edges=0,
            max_conflict_records=0,
        )
        plan = _build_plan(
            query_id=answer_query.query_id,
            semantic_address_id=address.semantic_address_id,
            proposed_record_ids=tuple(
                record.meaning_record_id for record in source_records
            ),
            proposed_memory_pointer_ids=(pointer.pointer_id,),
            proposed_artifact_pointer_ids=(),
            requested_descent_class="SUMMARY_ONLY",
            proposed_budget_id=budget.memory_descent_budget_id,
            required_access_policy_ids=(pointer.access_policy_id,),
            reason_codes=(),
        )
        descent_kernel, descent_input, descent_result = _root_triple(
            transaction_id=answer_query.query_id,
            target_root_id=_ROOT_OWNER,
            selected_id=plan.retrieval_plan_id,
            subject=address.semantic_address_id,
            predicate=_B3_ROOT_PREDICATE,
            claim_value=_plan_plain(plan),
            label=f"{spec.domain_id}:descent",
        )
        descent_hash = _domain_hash(
            domain=_B3_ROOT_DOMAIN,
            payload=_canonical_bytes(_root_result_plain(descent_result)),
        )
        descent_request = _build_descent_request(
            retrieval_plan_id=plan.retrieval_plan_id,
            query_id=answer_query.query_id,
            owning_local_root_id=_ROOT_OWNER,
            root_kernel_id=descent_kernel.kernel_id,
            root_decision_input_id=descent_input.decision_input_id,
            root_decision_id=descent_result.decision_id,
            root_decision_hash=descent_hash,
            requested_descent_class="SUMMARY_ONLY",
            approved_descent_class="SUMMARY_ONLY",
            proposed_budget_id=budget.memory_descent_budget_id,
            approved_budget=budget,
            approved_record_ids=tuple(
                record.meaning_record_id for record in source_records
            ),
            approved_memory_pointer_ids=(pointer.pointer_id,),
            approved_artifact_pointer_ids=(),
        )
        memory_result = _execute_descent(
            retrieval_plan=plan,
            proposed_budget=budget,
            descent_request=descent_request,
            root_kernel=descent_kernel,
            root_decision_input=descent_input,
            root_decision_result=descent_result,
            source_records=source_records,
            artifact_payloads=(),
        )
        selected = ranked[0]
        selected_evaluation = next(
            item
            for item in answer_evaluations
            if item.query_evaluation_id
            == selected.query_evaluation_id
        )
        selected_record = next(
            item
            for item in source_records
            if item.meaning_record_id == selected.meaning_record_id
        )
        shortcut_claim = _shortcut_claim_preimage(
            query=answer_query,
            evaluation=selected_evaluation,
            candidate=selected,
            valid_from=200,
            valid_to=300,
        )
        shortcut_kernel, shortcut_input, shortcut_result = _root_triple(
            transaction_id=answer_query.query_id,
            target_root_id=_ROOT_OWNER,
            selected_id=selected.resolution_candidate_id,
            subject=address.semantic_address_id,
            predicate=_B4_ROOT_PREDICATE,
            claim_value=shortcut_claim,
            label=f"{spec.domain_id}:shortcut",
        )
        shortcut_hash = _domain_hash(
            domain=_B4_ROOT_DOMAIN,
            payload=_canonical_bytes(_root_result_plain(shortcut_result)),
        )
        projection = _build_projection(
            owning_local_root_id=_ROOT_OWNER,
            root_kernel_id=shortcut_kernel.kernel_id,
            root_decision_input_id=shortcut_input.decision_input_id,
            root_decision_id=shortcut_result.decision_id,
            root_decision_hash=shortcut_hash,
            selected_candidate_id=selected.resolution_candidate_id,
            semantic_address_id=address.semantic_address_id,
            meaning_record_id=selected_record.meaning_record_id,
            query_id=answer_query.query_id,
            query_evaluation_id=selected_evaluation.query_evaluation_id,
            allowed_reuse_class="ANSWER_SHORTCUT",
            scope_fingerprint=scope_hash,
            policy_version=_POLICY,
            schema_versions=_SCHEMAS,
            valid_from=200,
            valid_to=300,
            root_shortcut_policy_ref=_B4_POLICY_REF,
        )
        certificate = _build_certificate(
            semantic_address_id=address.semantic_address_id,
            meaning_record_id=selected_record.meaning_record_id,
            query_id=answer_query.query_id,
            query_evaluation_id=selected_evaluation.query_evaluation_id,
            resolution_candidate_id=selected.resolution_candidate_id,
            root_shortcut_authorization_projection=projection,
            case_type="NON_ACTION_INFORMATIONAL",
            required_evidence_classes=(
                answer_query.required_evidence_classes
            ),
            observed_evidence_fingerprint=(
                selected_evaluation.observed_evidence_fingerprint
            ),
            forbidden_changes=answer_query.forbidden_changes,
            checked_dependency_fingerprint=(
                selected_evaluation.checked_dependency_fingerprint
            ),
            valid_from=200,
            valid_to=300,
            reuse_class="ANSWER_SHORTCUT",
            source_history_hash=selected_evaluation.source_history_hash,
            action_history_binding_id=None,
            issued_at=200,
            evaluated_at=selected_evaluation.evaluated_at,
        )
        answer_report = _build_report(
            semantic_address=address,
            query=answer_query,
            source_projections=projections,
            source_records=source_records,
            query_evaluations=answer_evaluations,
            eligible_candidates=answer_candidates,
            ranked_candidate_ids=tuple(
                item.resolution_candidate_id for item in ranked
            ),
            selected_candidate_id=selected.resolution_candidate_id,
            retrieval_plan=plan,
            memory_descent_result=memory_result,
            root_shortcut_projection=projection,
            reuse_certificate=certificate,
            context_only_record_ids=(),
            historical_only_record_ids=(),
            warning_only_record_ids=(),
            rerun_required_record_ids=(),
            blocked_record_ids=tuple(
                item.meaning_record_id
                for item in answer_evaluations
                if item.query_state.startswith("BLOCKED_")
            ),
            provider_calls=0,
            network_calls=0,
            gemini_calls=0,
            external_drs_calls=0,
            connector_calls=0,
            real_world_effects_count=0,
            final_status="PASS",
            reason_codes=(),
        )
        if _validate_shortcut(
            resolution_report=answer_report,
            root_kernel=shortcut_kernel,
            root_decision_input=shortcut_input,
            root_decision_result=shortcut_result,
            use_time=200,
        ) != (True, ()):
            raise ValueError("g2b_report_fail_closed")
        context_report = _context_report(
            address=address,
            scope_hash=scope_hash,
            projections=projections,
            source_records=source_records,
            pointer=pointer,
        )
        observed_negative_reasons = tuple(
            _action_reason(value) for value in spec.negative_requests
        )
        if observed_negative_reasons != spec.negative_reason_codes:
            raise ValueError("g2b_report_fail_closed")
        commitment = _successor_commitment(
            spec=spec,
            address=address,
            scope_hash=scope_hash,
        )
        supersession_reason = "Root-reviewed bounded semantic replacement."
        writeback_claim = _writeback_claim_preimage(
            predecessor_record=predecessor,
            successor_commitment_record=commitment,
            claim_dimension=spec.claim_dimension,
            supersession_reason=supersession_reason,
        )
        proposal_id = writeback_claim["writeback_proposal_id"]
        writeback_kernel, writeback_input, writeback_result = _root_triple(
            transaction_id=proposal_id,
            target_root_id=_ROOT_OWNER,
            selected_id=proposal_id,
            subject=address.semantic_address_id,
            predicate=_WRITEBACK_PREDICATE,
            claim_value=writeback_claim,
            label=f"{spec.domain_id}:writeback",
        )
        successor = _final_successor(
            spec=spec,
            predecessor=predecessor,
            commitment=commitment,
            proposal_id=proposal_id,
            supersession_reason=supersession_reason,
            root_input=writeback_input,
            root_result=writeback_result,
        )
        writeback_evidence = _write_successor(
            drs=drs,
            predecessor_record=predecessor,
            successor_commitment_record=commitment,
            successor_record=successor,
            claim_dimension=spec.claim_dimension,
            root_kernel=writeback_kernel,
            root_decision_input=writeback_input,
            root_decision_result=writeback_result,
        )
        later_records = _pure_read(drs=drs, layers=("work",))
        if len(later_records) != 3:
            raise ValueError("g2b_report_fail_closed")
    return _G2B5DomainProofV01(
        profile_version=_PROFILE_VERSION,
        domain_id=spec.domain_id,
        positive_question=spec.positive_question,
        negative_requests=spec.negative_requests,
        negative_reason_codes=spec.negative_reason_codes,
        semantic_address=address,
        legacy_source_records=legacy_records,
        source_projections=projections,
        source_records=source_records,
        answer_report=answer_report,
        shortcut_root_kernel=shortcut_kernel,
        shortcut_root_decision_input=shortcut_input,
        shortcut_root_decision_result=shortcut_result,
        answer_use_time=200,
        context_report=context_report,
        descent_proposed_budget=budget,
        descent_request=descent_request,
        descent_root_kernel=descent_kernel,
        descent_root_decision_input=descent_input,
        descent_root_decision_result=descent_result,
        successor_commitment_record=commitment,
        successor_record=successor,
        writeback_root_kernel=writeback_kernel,
        writeback_root_decision_input=writeback_input,
        writeback_root_decision_result=writeback_result,
        writeback_evidence=writeback_evidence,
        pure_read_snapshot_before=snapshot_before,
        pure_read_snapshot_after=snapshot_after,
        final_status="PASS",
        reason_codes=(),
    )


def _fixture_hash(spec: _G2B5DomainSpecV01, label: str) -> str:
    return _domain_hash(
        domain="hedgehog:drs:g2b5:fixture:v01",
        payload=_canonical_bytes((spec.domain_id, label)),
    )


def _domain_time(base: int) -> _DRSTimeEnvelopeV01:
    return _build_time(
        pt_created_at=base,
        kt_as_of=base,
        et_observed_at=base,
        ct_context_anchor=base,
        ttl_seconds=1000,
        valid_from=50 if base == 100 else 150,
        valid_to=1000,
        source_observed_at=base,
        source_reported_at=base,
        system_ingested_at=base,
        system_verified_at=base,
        freshness_policy_id=_FRESHNESS,
    )


def _domain_authority(
    *,
    scope_hash: str,
    authority_class: str,
    acceptance_state: str,
    label: str,
    root_input_id: str | None = None,
    root_result_id: str | None = None,
    root_hash: str | None = None,
) -> _DRSAuthorityEnvelopeV01:
    accepted = authority_class.startswith("ROOT_ACCEPTED_")
    return _build_authority(
        authority_class=authority_class,
        owning_local_root_id=_ROOT_OWNER if accepted else None,
        source_root_decision_input_id=(
            root_input_id
            if root_input_id is not None
            else (f"root-input:{label}" if accepted else None)
        ),
        source_root_decision_id=(
            root_result_id
            if root_result_id is not None
            else (f"root-decision:{label}" if accepted else None)
        ),
        source_root_decision_hash=(
            root_hash
            if root_hash is not None
            else (_SHA_A if accepted else None)
        ),
        authority_scope_fingerprint=scope_hash,
        root_acceptance_state=acceptance_state,
        recording_component="g2b5_fixture",
    )


def _domain_query(
    *,
    address: _SemanticAddressV01,
    scope_hash: str,
    query_mode: str,
    reuse_intent: str,
    requested_reuse_classes: tuple[str, ...],
    required_time_axes: tuple[str, ...],
    evaluation_time_source: str,
) -> _DRSTemporalQueryV01:
    return _build_query(
        query_mode=query_mode,
        semantic_address_id=address.semantic_address_id,
        scope_fingerprint=scope_hash,
        as_of=200,
        evaluation_time=200,
        evaluation_time_source=evaluation_time_source,
        time_range_start=0,
        time_range_end=2000,
        required_time_axes=required_time_axes,
        freshness_policy_id=_FRESHNESS,
        max_age_seconds=1000,
        domain=address.domain,
        risk_class="LOW",
        reuse_intent=reuse_intent,
        requested_reuse_classes=requested_reuse_classes,
        required_evidence_classes=_EVIDENCE_CLASSES,
        forbidden_changes=("POLICY_CHANGED",),
        policy_version=_POLICY,
        schema_versions=_SCHEMAS,
        owning_local_root_id=_ROOT_OWNER,
    )


def _domain_candidate(
    *,
    query: _DRSTemporalQueryV01,
    evaluation: _QueryEvaluationStateV01,
    record: _MeaningRecordV01,
    similarity: int,
) -> _ResolutionCandidateV01:
    return _build_candidate(
        query_id=query.query_id,
        semantic_address_id=query.semantic_address_id,
        meaning_record_id=record.meaning_record_id,
        query_evaluation_id=evaluation.query_evaluation_id,
        safe_summary=record.safe_summary,
        evidence_ref_ids=record.source_reference_ids,
        source_history_hash=evaluation.source_history_hash,
        action_history_binding_id=None,
        semantic_similarity_units=similarity,
        freshness_units=evaluation.current_freshness_units,
        source_authority_prior_units=9000,
        lineage_proximity_units=7000,
        historical_utility_units=6000,
        gt_advisory_prior_units=1000,
        conflict_penalty_units=0,
        risk_penalty_units=0,
        retrieval_cost_units=100,
    )


def _root_states(selected_id: str, label: str) -> dict[str, object]:
    return {
        "post_vv_bundle": {
            "bundle_id": f"post-vv:{label}",
            "post_vv_passed": True,
            "validated_candidate_ids": [selected_id],
            "rejected_candidate_ids": [],
            "required_evidence_refs": [],
            "provided_evidence_refs": [],
            "hard_failure_reasons": [],
        },
        "gt_advisory": {
            "advisory_id": f"gt:{label}",
            "candidate_ids": [selected_id],
            "selected_candidate_id": selected_id,
            "score_micros_by_candidate": {selected_id: 500_000},
            "source_artifact_type": "GTAdvisoryReport",
            "source_lifecycle_state": "VALIDATED",
            "actor_role": "gt",
            "attempted_effect": "CREATE_ROOT_DECISION",
            "target_artifact_type": "RootDecision",
            "advisory_only": True,
            "creates_final_output": False,
            "requests_effect": False,
        },
        "policy_state": {
            "policy_id": f"policy:{label}",
            "identity_passed": True,
            "scope_passed": True,
            "hard_policy_passed": True,
            "allow_accept": True,
            "conflict_policy": "DEFER",
            "no_candidate_policy": "NO_UPDATE",
        },
        "permission_state": {
            "permission_required": False,
            "user_permission_present": False,
            "permission_scope_valid": True,
            "permission_ref": None,
        },
        "temporal_state": {
            "temporal_valid": True,
            "expired": False,
            "not_before_satisfied": True,
            "time_envelope_ref": f"time-envelope:{label}",
        },
        "conflict_state": {
            "material_unresolved_conflict": False,
            "conflict_set_ids": [],
        },
        "prior_root_state": {
            "prior_decision_id": None,
            "prior_decision": None,
            "prior_selected_candidate_id": None,
        },
    }


def _root_triple(
    *,
    transaction_id: str,
    target_root_id: str,
    selected_id: str,
    subject: str,
    predicate: str,
    claim_value: object,
    label: str,
) -> tuple[
    _RootDecisionKernelV01,
    _RootDecisionInputV01,
    _RootDecisionResultV01,
]:
    request = _build_work_request(
        request_id=f"semantic-work-request:{label}",
        transaction_id=transaction_id,
        target_root_id=target_root_id,
        runtime_topology_ref=f"topology:{label}",
        bounded_context_refs=(f"context:{label}",),
        permitted_actor_ids=(f"actor:{label}",),
        permitted_contribution_modes=("DETERMINISTIC",),
        requested_subjects=(subject,),
        required_evidence_classes=("ROOT_BINDING",),
        forbidden_claims=("create_permission",),
    )
    evidence = _build_evidence(
        evidence_id=f"evidence-binding:{label}",
        evidence_ref=f"evidence:{label}",
        evidence_class="ROOT_BINDING",
        source_component_id=f"actor:{label}",
        provenance_ref=f"provenance:{label}",
        evidence_state=_EVIDENCE_PRESENT,
    )
    claim = _build_claim(
        claim_id=selected_id,
        subject=subject,
        predicate=predicate,
        object_or_value=claim_value,
        time_envelope_ref=f"time-envelope:{label}",
        provenance_refs=(f"provenance:{label}",),
        evidence_refs=(f"evidence-binding:{label}",),
        confidence_micros=1_000_000,
        source_role="deterministic_runtime",
        source_mode="DETERMINISTIC",
    )
    contribution = _build_contribution(
        contribution_id=f"contribution:{label}",
        request_id=request.request_id,
        actor_id=f"actor:{label}",
        actor_role="deterministic_runtime",
        contribution_mode="DETERMINISTIC",
        bsep_projection_ref=f"bsep:{label}",
        scope=subject,
        bounded_context_refs=(f"context:{label}",),
        claims=(claim,),
        evidence_bindings=(evidence,),
        constraint_bindings=(),
        uncertainty_bindings=(),
        requested_validators=(),
        forbidden_claims_observed=(),
    )
    packet = _build_packet(
        request=request,
        contributions=(contribution,),
        trust_profiles=_trust_profiles(),
    )
    kernel = _build_root_kernel()
    decision_input = _build_root_input(
        transaction_id=transaction_id,
        target_root_id=target_root_id,
        root_review_packet=packet,
        **_root_states(selected_id, label),
    )
    result = _decide_root(kernel=kernel, decision_input=decision_input)
    return kernel, decision_input, result


def _shortcut_claim_preimage(
    *,
    query: _DRSTemporalQueryV01,
    evaluation: _QueryEvaluationStateV01,
    candidate: _ResolutionCandidateV01,
    valid_from: int,
    valid_to: int,
) -> dict[str, object]:
    return {
        "profile_version": _PROFILE_VERSION,
        "semantic_address_id": query.semantic_address_id,
        "meaning_record_id": candidate.meaning_record_id,
        "query_id": query.query_id,
        "query_evaluation_id": evaluation.query_evaluation_id,
        "resolution_candidate_id": candidate.resolution_candidate_id,
        "reuse_class": "ANSWER_SHORTCUT",
        "case_type": "NON_ACTION_INFORMATIONAL",
        "scope_fingerprint": query.scope_fingerprint,
        "policy_version": query.policy_version,
        "schema_versions": list(query.schema_versions),
        "required_evidence_classes": list(
            query.required_evidence_classes
        ),
        "observed_evidence_fingerprint": (
            evaluation.observed_evidence_fingerprint
        ),
        "forbidden_changes": list(query.forbidden_changes),
        "checked_dependency_fingerprint": (
            evaluation.checked_dependency_fingerprint
        ),
        "source_history_hash": evaluation.source_history_hash,
        "action_history_binding_id": None,
        "valid_from": valid_from,
        "valid_to": valid_to,
        "issued_at": 200,
        "evaluated_at": evaluation.evaluated_at,
        "root_shortcut_policy_ref": _B4_POLICY_REF,
    }


def _context_report(
    *,
    address: _SemanticAddressV01,
    scope_hash: str,
    projections: tuple[_LegacyDRSProjectionV01, ...],
    source_records: tuple[_MeaningRecordV01, ...],
    pointer: _MemoryPointerV01,
) -> _DRSResolutionReportV01:
    query = _domain_query(
        address=address,
        scope_hash=scope_hash,
        query_mode="MEMORY_CONTEXT_ONLY",
        reuse_intent="CONTEXT",
        requested_reuse_classes=("CONTEXT_ONLY",),
        required_time_axes=("KT", "TTL", "VALIDITY"),
        evaluation_time_source="INJECTED_ANALYSIS_TIME",
    )
    evaluations = tuple(
        _evaluate(
            semantic_address=address,
            query=query,
            meaning_record=record,
        )
        for record in source_records
    )
    budget = _build_budget(
        max_depth=1,
        max_records_opened=2,
        max_pointers_opened=1,
        max_artifacts_opened=0,
        max_bytes_opened=0,
        max_lineage_edges=0,
        max_conflict_records=0,
    )
    plan = _build_plan(
        query_id=query.query_id,
        semantic_address_id=address.semantic_address_id,
        proposed_record_ids=tuple(
            record.meaning_record_id for record in source_records
        ),
        proposed_memory_pointer_ids=(),
        proposed_artifact_pointer_ids=(),
        requested_descent_class="SUMMARY_ONLY",
        proposed_budget_id=budget.memory_descent_budget_id,
        required_access_policy_ids=(),
        reason_codes=(),
    )
    return _build_report(
        semantic_address=address,
        query=query,
        source_projections=projections,
        source_records=source_records,
        query_evaluations=evaluations,
        eligible_candidates=(),
        ranked_candidate_ids=(),
        selected_candidate_id=None,
        retrieval_plan=plan,
        memory_descent_result=None,
        root_shortcut_projection=None,
        reuse_certificate=None,
        context_only_record_ids=tuple(
            item.meaning_record_id
            for item in evaluations
            if item.query_state == "STALE_CONTEXT_ONLY"
        ),
        historical_only_record_ids=(),
        warning_only_record_ids=(),
        rerun_required_record_ids=(),
        blocked_record_ids=tuple(
            item.meaning_record_id
            for item in evaluations
            if item.query_state.startswith("BLOCKED_")
        ),
        provider_calls=0,
        network_calls=0,
        gemini_calls=0,
        external_drs_calls=0,
        connector_calls=0,
        real_world_effects_count=0,
        final_status="PASS",
        reason_codes=(),
    )


def _successor_commitment(
    *,
    spec: _G2B5DomainSpecV01,
    address: _SemanticAddressV01,
    scope_hash: str,
) -> _MeaningRecordV01:
    return _build_record(
        semantic_address=address,
        predecessor_record_id=None,
        supersession_reason=None,
        safe_summary=spec.safe_summary + " Root-reviewed successor.",
        semantic_tags=spec.semantic_tags,
        resonance_reason="Proposed immutable semantic successor.",
        memory_pointers=(),
        artifact_pointers=(),
        source_reference_ids=(
            f"source:{spec.domain_id.lower()}:successor",
        ),
        lineage_edges=(),
        time_envelope=_domain_time(210),
        authority_envelope=_domain_authority(
            scope_hash=scope_hash,
            authority_class="EVIDENCE_CANDIDATE",
            acceptance_state="UNREVIEWED",
            label=f"{spec.domain_id}:commitment",
        ),
        persistent_lifecycle_state="ACTIVE",
        risk_hints=(),
        conflict_hints=(),
        reuse_policy_class="ANSWER_SHORTCUT",
        policy_version=_POLICY,
        schema_versions=_SCHEMAS,
        content_fingerprint=_fixture_hash(spec, "successor-content"),
        recording_component="g2b5_fixture",
    )


def _final_successor(
    *,
    spec: _G2B5DomainSpecV01,
    predecessor: _MeaningRecordV01,
    commitment: _MeaningRecordV01,
    proposal_id: str,
    supersession_reason: str,
    root_input: _RootDecisionInputV01,
    root_result: _RootDecisionResultV01,
) -> _MeaningRecordV01:
    history_hash = _domain_hash(
        domain="hedgehog:drs:meaning_record_history:v01",
        payload=_canonical_bytes(_meaning_plain(predecessor)),
    )
    edge = _build_edge(
        source_meaning_record_id=predecessor.meaning_record_id,
        target_meaning_record_id=commitment.meaning_record_id,
        relation_class="REPLACES",
        claim_dimension=spec.claim_dimension,
        source_history_hash=history_hash,
        evidence_ref_ids=(proposal_id,),
        created_at=220,
        recording_component="g2b5_fixture",
    )
    root_hash = _writeback_root_hash(
        root_decision_result=root_result
    )
    return _build_record(
        semantic_address=commitment.semantic_address,
        predecessor_record_id=predecessor.meaning_record_id,
        supersession_reason=supersession_reason,
        safe_summary=commitment.safe_summary,
        semantic_tags=commitment.semantic_tags,
        resonance_reason=commitment.resonance_reason,
        memory_pointers=commitment.memory_pointers,
        artifact_pointers=commitment.artifact_pointers,
        source_reference_ids=commitment.source_reference_ids
        + (proposal_id, edge.lineage_edge_id),
        lineage_edges=(edge,),
        time_envelope=commitment.time_envelope,
        authority_envelope=_domain_authority(
            scope_hash=(
                predecessor.authority_envelope
                .authority_scope_fingerprint
            ),
            authority_class="ROOT_ACCEPTED_WORK",
            acceptance_state="ACCEPTED_WORK",
            label=f"{spec.domain_id}:successor",
            root_input_id=root_input.decision_input_id,
            root_result_id=root_result.decision_id,
            root_hash=root_hash,
        ),
        persistent_lifecycle_state=(
            commitment.persistent_lifecycle_state
        ),
        risk_hints=commitment.risk_hints,
        conflict_hints=commitment.conflict_hints,
        reuse_policy_class=commitment.reuse_policy_class,
        policy_version=commitment.policy_version,
        schema_versions=commitment.schema_versions,
        content_fingerprint=commitment.content_fingerprint,
        recording_component="g2b5_fixture",
    )


def _report_to_plain_data_v01(value: object) -> dict[str, object]:
    if type(value) is not _G2B5DeterministicReportV01:
        raise ValueError("g2b_report_fail_closed") from None
    return {
        field.name: _plain_value(getattr(value, field.name))
        for field in _fields(value)
    }


def _plain_value(value: object) -> object:
    serializers = (
        (_SemanticAddressV01, _address_plain),
        (_MemoryPointerV01, _memory_pointer_plain),
        (_LineageEdgeV01, _edge_plain),
        (_DRSAuthorityEnvelopeV01, _authority_plain),
        (_DRSTimeEnvelopeV01, _time_plain),
        (_MeaningRecordV01, _meaning_plain),
        (_LegacyDRSProjectionV01, _legacy_plain),
        (_DRSTemporalQueryV01, _query_plain),
        (_QueryEvaluationStateV01, _evaluation_plain),
        (_ResolutionCandidateV01, _candidate_plain),
        (_RetrievalPlanV01, _plan_plain),
        (_MemoryDescentBudgetV01, _budget_plain),
        (_MemoryDescentRequestV01, _request_plain),
        (_MemoryDescentResultV01, _result_plain),
        (_DRSResolutionReportV01, _report_plain),
        (_RootProjectionV01, _projection_plain),
        (_ReuseCertificateV01, _certificate_plain),
        (_RootDecisionKernelV01, _root_kernel_plain),
        (_RootDecisionInputV01, _root_input_plain),
        (_RootDecisionResultV01, _root_result_plain),
    )
    for value_type, serializer in serializers:
        if type(value) is value_type:
            return serializer(value)
    if type(value) in (_G2B5DomainProofV01, _G2B5DomainSpecV01):
        return {
            field.name: _plain_value(getattr(value, field.name))
            for field in _fields(value)
        }
    if type(value) is tuple:
        return [_plain_value(item) for item in value]
    if type(value) is list:
        return [_plain_value(item) for item in value]
    if type(value) is dict:
        if any(type(key) is not str for key in value):
            raise ValueError("g2b_report_fail_closed")
        return {key: _plain_value(item) for key, item in value.items()}
    if value is None or type(value) in (bool, int, str):
        return value
    raise ValueError("g2b_report_fail_closed")


def _reidentify_report_v01(
    value: _G2B5DeterministicReportV01,
) -> _G2B5DeterministicReportV01:
    try:
        plain = _report_to_plain_data_v01(value)
        plain.pop("report_id")
        report_id = _REPORT_PREFIX + _domain_hash(
            domain=_REPORT_DOMAIN,
            payload=_canonical_bytes(plain),
        )
    except Exception:
        report_id = _REPORT_PREFIX + "e" * 64
    return _replace(value, report_id=report_id)


def collect_drs_semantic_address_reuse_certificate_g2_b_v01(
) -> _G2B5DeterministicReportV01:
    domains = tuple(_collect_domain_v01(spec) for spec in _DOMAIN_SPECS_V01)
    counters = (
        ("domain_count", 2),
        ("positive_answer_shortcuts", 2),
        ("context_only_fallbacks", 2),
        ("action_negative_requests", 8),
        ("pure_read_passes", 4),
        ("initial_local_records_written", 4),
        ("immutable_successor_records_written", 2),
        ("root_decisions_created_in_fixture", 6),
        ("reuse_certificates_created_in_fixture", 2),
        ("provider_calls", 0),
        ("network_calls", 0),
        ("gemini_calls", 0),
        ("external_drs_calls", 0),
        ("connector_calls", 0),
        ("real_world_effects", 0),
        ("canonical_meaning_records_mutated", 0),
        ("final_outputs_created_by_drs", 0),
        ("final_outputs_created_by_certificate", 0),
        ("action_commit_packets_created", 0),
        ("receipts_created", 0),
        ("capabilities_created", 0),
        ("effect_handles_created", 0),
    )
    closed = tuple(
        (name, 0)
        for name in (
            "airline_programme_runs",
            "supplier_programme_runs",
            "package_runner_calls",
            "anchor_runner_calls",
            "replay_runner_calls",
            "living_gauntlet_calls",
            "kernel_conformance_calls",
        )
    )
    provisional = _G2B5DeterministicReportV01(
        report_version=_PROFILE_VERSION,
        report_id=_REPORT_PREFIX + "0" * 64,
        profile_id=_PROFILE_ID,
        domain_order=tuple(spec.domain_id for spec in _DOMAIN_SPECS_V01),
        domain_results=domains,
        operation_counters=counters,
        closed_programme_counters=closed,
        raw_user_request_to_query_cross_binding_implemented=False,
        production_generic_informational_responder_claimed=False,
        final_status="PASS",
        reason_codes=(),
    )
    report = _reidentify_report_v01(provisional)
    if validate_drs_semantic_address_reuse_certificate_g2_b_report_v01(
        report
    ) != (True, ()):
        raise ValueError("g2b_report_fail_closed") from None
    return report


def validate_drs_semantic_address_reuse_certificate_g2_b_report_v01(
    value: object,
) -> tuple[bool, tuple[str, ...]]:
    try:
        if type(value) is not _G2B5DeterministicReportV01:
            raise ValueError
        expected_fields = (
            "report_version",
            "report_id",
            "profile_id",
            "domain_order",
            "domain_results",
            "operation_counters",
            "closed_programme_counters",
            "raw_user_request_to_query_cross_binding_implemented",
            "production_generic_informational_responder_claimed",
            "final_status",
            "reason_codes",
        )
        if tuple(field.name for field in _fields(value)) != expected_fields:
            raise ValueError
        if (
            type(value.report_version) is not str
            or type(value.report_id) is not str
            or type(value.profile_id) is not str
            or type(value.domain_order) is not tuple
            or any(type(item) is not str for item in value.domain_order)
            or type(value.domain_results) is not tuple
            or type(value.operation_counters) is not tuple
            or type(value.closed_programme_counters) is not tuple
            or any(
                type(row) is not tuple
                or len(row) != 2
                or type(row[0]) is not str
                or type(row[1]) is not int
                for row in (
                    value.operation_counters
                    + value.closed_programme_counters
                )
            )
            or type(
                value.raw_user_request_to_query_cross_binding_implemented
            )
            is not bool
            or type(
                value.production_generic_informational_responder_claimed
            )
            is not bool
            or type(value.final_status) is not str
            or type(value.reason_codes) is not tuple
            or any(type(item) is not str for item in value.reason_codes)
            or value.report_version != _PROFILE_VERSION
            or value.profile_id != _PROFILE_ID
            or value.domain_order
            != tuple(spec.domain_id for spec in _DOMAIN_SPECS_V01)
            or len(value.domain_results) != 2
            or value.raw_user_request_to_query_cross_binding_implemented
            is not False
            or value.production_generic_informational_responder_claimed
            is not False
            or value.final_status != "PASS"
            or value.reason_codes
            or _reidentify_report_v01(value).report_id != value.report_id
        ):
            raise ValueError
        for spec, domain in zip(
            _DOMAIN_SPECS_V01, value.domain_results, strict=True
        ):
            if not _domain_proof_valid(spec, domain):
                raise ValueError
        expected_counters = (
            ("domain_count", 2),
            ("positive_answer_shortcuts", 2),
            ("context_only_fallbacks", 2),
            ("action_negative_requests", 8),
            ("pure_read_passes", 4),
            ("initial_local_records_written", 4),
            ("immutable_successor_records_written", 2),
            ("root_decisions_created_in_fixture", 6),
            ("reuse_certificates_created_in_fixture", 2),
            ("provider_calls", 0),
            ("network_calls", 0),
            ("gemini_calls", 0),
            ("external_drs_calls", 0),
            ("connector_calls", 0),
            ("real_world_effects", 0),
            ("canonical_meaning_records_mutated", 0),
            ("final_outputs_created_by_drs", 0),
            ("final_outputs_created_by_certificate", 0),
            ("action_commit_packets_created", 0),
            ("receipts_created", 0),
            ("capabilities_created", 0),
            ("effect_handles_created", 0),
        )
        if value.operation_counters != expected_counters:
            raise ValueError
        if value.closed_programme_counters != tuple(
            (name, 0)
            for name in (
                "airline_programme_runs",
                "supplier_programme_runs",
                "package_runner_calls",
                "anchor_runner_calls",
                "replay_runner_calls",
                "living_gauntlet_calls",
                "kernel_conformance_calls",
            )
        ):
            raise ValueError
        return True, ()
    except Exception:
        return False, ("g2b_report_fail_closed",)


def _domain_proof_valid(
    spec: _G2B5DomainSpecV01,
    value: object,
) -> bool:
    if type(value) is not _G2B5DomainProofV01:
        return False
    if (
        type(value.profile_version) is not str
        or type(value.domain_id) is not str
        or type(value.positive_question) is not str
        or type(value.negative_requests) is not tuple
        or any(type(item) is not str for item in value.negative_requests)
        or type(value.negative_reason_codes) is not tuple
        or any(
            type(item) is not str
            for item in value.negative_reason_codes
        )
        or type(value.answer_use_time) is not int
        or type(value.writeback_evidence) is not dict
        or type(value.pure_read_snapshot_before) is not tuple
        or type(value.pure_read_snapshot_after) is not tuple
        or type(value.final_status) is not str
        or type(value.reason_codes) is not tuple
        or any(type(item) is not str for item in value.reason_codes)
        or value.profile_version != _PROFILE_VERSION
        or value.domain_id != spec.domain_id
        or value.positive_question != spec.positive_question
        or value.negative_requests != spec.negative_requests
        or value.negative_reason_codes != spec.negative_reason_codes
        or value.final_status != "PASS"
        or value.reason_codes
        or value.pure_read_snapshot_before
        != value.pure_read_snapshot_after
        or type(value.legacy_source_records) is not tuple
        or type(value.source_projections) is not tuple
        or type(value.source_records) is not tuple
        or len(value.legacy_source_records) != 2
        or len(value.source_projections) != 2
        or len(value.source_records) != 2
        or type(value.semantic_address) is not _SemanticAddressV01
        or value.semantic_address.domain != spec.domain_id.lower()
    ):
        return False
    expected_snapshot_rows = []
    for wrapper in value.legacy_source_records:
        if type(wrapper) is not dict:
            return False
        record_id = wrapper.get("record_id")
        if type(record_id) is not str:
            return False
        payload = _json.dumps(
            wrapper,
            indent=2,
            sort_keys=True,
        ).encode("utf-8")
        expected_snapshot_rows.append(
            (
                f"work/{_safe_filename(record_id)}",
                _hashlib.sha256(payload).hexdigest(),
                len(payload),
                0o644,
            )
        )
    expected_snapshot = tuple(
        sorted(expected_snapshot_rows, key=lambda row: row[0])
    )
    if (
        value.pure_read_snapshot_before != expected_snapshot
        or value.pure_read_snapshot_after != expected_snapshot
    ):
        return False
    for wrapper, projection, record in zip(
        value.legacy_source_records,
        value.source_projections,
        value.source_records,
        strict=True,
    ):
        if (
            type(record) is not _MeaningRecordV01
            or _validate_meaning(record) != (True, ())
            or not _wrapper_matches(wrapper, record)
            or type(projection) is not _LegacyDRSProjectionV01
            or _validate_legacy(projection) != (True, ())
            or projection
            != _project_legacy(
                source_family="LOCAL_DRS_DICT",
                source=wrapper,
                target_semantic_address=value.semantic_address,
                target_meaning_record=None,
            )
            or projection.source_identity != wrapper["record_id"]
            or projection.source_family != "LOCAL_DRS_DICT"
            or projection.source_version
            != "legacy_local_drs_dict_v0"
            or projection.target_semantic_address_id
            != value.semantic_address.semantic_address_id
            or projection.target_meaning_record_id is not None
            or projection.projection_status
            != "CANONICAL_CONTEXT_ONLY"
            or projection.answer_shortcut_eligible is not False
            or projection.creates_authority is not False
            or projection.creates_permission is not False
            or projection.reason_codes
            != ("drs_legacy_context_only",)
            or "answer_shortcut_forbidden_in_g2b1"
            not in projection.downgrade_restrictions
        ):
            return False
    (
        expected_address,
        expected_predecessor,
        expected_context,
        _,
        expected_scope_hash,
    ) = _source_geometry_v01(spec)
    if (
        value.semantic_address != expected_address
        or value.source_records
        != (expected_predecessor, expected_context)
    ):
        return False
    answer = value.answer_report
    if (
        type(answer) is not _DRSResolutionReportV01
        or _validate_report(answer) != (True, ())
        or answer.semantic_address != value.semantic_address
        or answer.source_projections != value.source_projections
        or answer.source_records != value.source_records
        or answer.query.query_mode != "DIRECT_REUSE_CANDIDATE"
        or answer.query.requested_reuse_classes
        != ("ANSWER_SHORTCUT",)
        or answer.selected_candidate_id is None
        or answer.reuse_certificate is None
        or answer.root_shortcut_projection is None
        or answer.memory_descent_result is None
    ):
        return False
    rebuilt_evaluations = tuple(
        _evaluate(
            semantic_address=value.semantic_address,
            query=answer.query,
            meaning_record=record,
        )
        for record in value.source_records
    )
    if rebuilt_evaluations != answer.query_evaluations:
        return False
    rebuilt_ranked = _rank(
        query=answer.query,
        query_evaluations=answer.query_evaluations,
        candidates=answer.eligible_candidates,
    )
    if (
        tuple(item.resolution_candidate_id for item in rebuilt_ranked)
        != answer.ranked_candidate_ids
        or rebuilt_ranked[0].resolution_candidate_id
        != answer.selected_candidate_id
    ):
        return False
    if (
        type(value.descent_proposed_budget)
        is not _MemoryDescentBudgetV01
        or type(value.descent_request) is not _MemoryDescentRequestV01
        or type(value.descent_root_kernel) is not _RootDecisionKernelV01
        or type(value.descent_root_decision_input)
        is not _RootDecisionInputV01
        or type(value.descent_root_decision_result)
        is not _RootDecisionResultV01
    ):
        return False
    rebuilt_descent = _execute_descent(
        retrieval_plan=answer.retrieval_plan,
        proposed_budget=value.descent_proposed_budget,
        descent_request=value.descent_request,
        root_kernel=value.descent_root_kernel,
        root_decision_input=value.descent_root_decision_input,
        root_decision_result=value.descent_root_decision_result,
        source_records=value.source_records,
        artifact_payloads=(),
    )
    if (
        rebuilt_descent != answer.memory_descent_result
        or rebuilt_descent.executed_descent_class != "SUMMARY_ONLY"
        or rebuilt_descent.safe_summaries
        != tuple(record.safe_summary for record in value.source_records)
        or rebuilt_descent.bytes_opened != 0
    ):
        return False
    if _validate_shortcut(
        resolution_report=answer,
        root_kernel=value.shortcut_root_kernel,
        root_decision_input=value.shortcut_root_decision_input,
        root_decision_result=value.shortcut_root_decision_result,
        use_time=value.answer_use_time,
    ) != (True, ()):
        return False
    context = value.context_report
    if (
        type(context) is not _DRSResolutionReportV01
        or _validate_report(context) != (True, ())
        or context.source_records != value.source_records
        or context.source_projections != value.source_projections
        or context.query.query_mode != "MEMORY_CONTEXT_ONLY"
        or context.query.requested_reuse_classes != ("CONTEXT_ONLY",)
        or context.eligible_candidates
        or context.ranked_candidate_ids
        or context.selected_candidate_id is not None
        or context.root_shortcut_projection is not None
        or context.reuse_certificate is not None
    ):
        return False
    if tuple(_action_reason(item) for item in value.negative_requests) != (
        value.negative_reason_codes
    ):
        return False
    commitment = value.successor_commitment_record
    successor = value.successor_record
    predecessor = value.source_records[0]
    expected_commitment = _successor_commitment(
        spec=spec,
        address=expected_address,
        scope_hash=expected_scope_hash,
    )
    if (
        type(commitment) is not _MeaningRecordV01
        or type(successor) is not _MeaningRecordV01
        or _validate_meaning(commitment) != (True, ())
        or _validate_meaning(successor) != (True, ())
        or commitment != expected_commitment
    ):
        return False
    try:
        proposal_id, root_hash, edge = _validate_writeback_geometry(
            predecessor_record=predecessor,
            successor_commitment_record=commitment,
            successor_record=successor,
            claim_dimension=spec.claim_dimension,
            root_kernel=value.writeback_root_kernel,
            root_decision_input=value.writeback_root_decision_input,
            root_decision_result=value.writeback_root_decision_result,
        )
    except ValueError:
        return False
    if (
        edge != successor.lineage_edges[0]
        or proposal_id
        != value.writeback_evidence.get("writeback_proposal_id")
        or root_hash
        != value.writeback_evidence.get("root_result_binding_hash")
    ):
        return False
    expected_successor = _final_successor(
        spec=spec,
        predecessor=predecessor,
        commitment=commitment,
        proposal_id=proposal_id,
        supersession_reason=(
            "Root-reviewed bounded semantic replacement."
        ),
        root_input=value.writeback_root_decision_input,
        root_result=value.writeback_root_decision_result,
    )
    if successor != expected_successor:
        return False
    evidence = value.writeback_evidence
    predecessor_bytes = _json.dumps(
        value.legacy_source_records[0],
        indent=2,
        sort_keys=True,
    ).encode("utf-8")
    successor_wrapper = _storage_record(
        meaning_record=successor,
        writeback_metadata={
            "writeback_proposal_id": proposal_id,
            "supersession_evidence_id": edge.lineage_edge_id,
            "root_decision_id": (
                value.writeback_root_decision_result.decision_id
            ),
            "root_result_binding_hash": root_hash,
        },
    )
    successor_bytes = _json.dumps(
        successor_wrapper,
        indent=2,
        sort_keys=True,
    ).encode("utf-8")

    expected_evidence = {
        "writeback_profile_version": "v0.1",
        "writeback_proposal_id": proposal_id,
        "claim_dimension": spec.claim_dimension,
        "supersession_evidence_id": edge.lineage_edge_id,
        "predecessor_record_id": predecessor.meaning_record_id,
        "successor_commitment_record_id": commitment.meaning_record_id,
        "successor_record_id": successor.meaning_record_id,
        "root_kernel_id": value.writeback_root_kernel.kernel_id,
        "root_decision_input_id": (
            value.writeback_root_decision_input.decision_input_id
        ),
        "root_decision_id": (
            value.writeback_root_decision_result.decision_id
        ),
        "root_result_binding_hash": root_hash,
        "predecessor_storage_sha256_before": _hashlib.sha256(
            predecessor_bytes
        ).hexdigest(),
        "predecessor_storage_sha256_after": _hashlib.sha256(
            predecessor_bytes
        ).hexdigest(),
        "successor_storage_sha256": _hashlib.sha256(
            successor_bytes
        ).hexdigest(),
        "predecessor_preserved": True,
        "successor_readback_exact": True,
        "records_written": 1,
        "creates_authority": False,
        "creates_permission": False,
        "real_world_effects_count": 0,
    }
    return evidence == expected_evidence


def _main() -> int:
    report = collect_drs_semantic_address_reuse_certificate_g2_b_v01()
    valid, reasons = (
        validate_drs_semantic_address_reuse_certificate_g2_b_report_v01(
            report
        )
    )
    if not valid or reasons:
        print("G2B5_STATUS=FAIL")
        print("FINAL STATUS: FAIL")
        return 1
    counters = dict(report.operation_counters)
    print("G2B5_STATUS=PASS")
    print(f"REPORT_ID={report.report_id}")
    print(
        "DOMAIN_ORDER="
        "TRAVEL_POLICY_INFORMATION,"
        "WAREHOUSE_MAINTENANCE_INFORMATION"
    )
    for domain in report.domain_results:
        print(f"{domain.domain_id}={domain.final_status}")
    print(
        f"ANSWER_SHORTCUTS={counters['positive_answer_shortcuts']}/2"
    )
    print(
        f"CONTEXT_ONLY_FALLBACKS={counters['context_only_fallbacks']}/2"
    )
    print(
        f"ACTION_NEGATIVES={counters['action_negative_requests']}/8"
    )
    print(
        "IMMUTABLE_WRITEBACKS="
        f"{counters['immutable_successor_records_written']}/2"
    )
    preserved = sum(
        domain.writeback_evidence["predecessor_preserved"] is True
        for domain in report.domain_results
    )
    print(f"PREDECESSORS_PRESERVED={preserved}/2")
    print("PROVIDER_NETWORK_GEMINI_EFFECTS=0/0/0/0")
    print("CLOSED_PROGRAMME_RUNS=0")
    print("RAW_USER_REQUEST_TO_G2B_QUERY_CROSS_BINDING_IMPLEMENTED=false")
    print("PRODUCTION_GENERIC_INFORMATIONAL_RESPONDER_CLAIMED=false")
    print("FINAL STATUS: PASS")
    return 0


__all__ = (
    "collect_drs_semantic_address_reuse_certificate_g2_b_v01",
    "validate_drs_semantic_address_reuse_certificate_g2_b_report_v01",
)


if __name__ == "__main__":
    raise SystemExit(_main())
