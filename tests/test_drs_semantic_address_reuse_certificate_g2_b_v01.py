from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, is_dataclass, replace
from decimal import Decimal
import json
from pathlib import Path
import pickle

from jsonschema import Draft202012Validator, ValidationError
from referencing import Registry, Resource
import pytest

import hedgehog.drs_g2b_compatibility_v01 as compatibility
import hedgehog.drs_memory_resolution_v01 as resolution
import hedgehog.drs_semantic_address_v01 as semantic
import hedgehog.reuse_certificate_v01 as reuse
from hedgehog.kernel.integrity_replay_v01 import canonical_json_bytes_v01
from hedgehog.kernel.integrity_replay_v01 import (
    domain_separated_sha256_hex_v01,
)
from hedgehog.local_drs_resolver import SemanticDRSRecordInput
from hedgehog.local_drs_v02 import (
    DRSFreshnessEnvelope,
    DRSRecordV02,
    TemporalQueryV02,
)


_SHA_A = "a" * 64
_SHA_B = "b" * 64
_SHA_C = "c" * 64
_SHA_D = "d" * 64
_SHA_E = "e" * 64

_EXPECTED_FIELDS = {
    semantic.SemanticAddressV01: (
        "address_profile_version",
        "namespace",
        "domain",
        "subject_class",
        "intent_class",
        "meaning_schema_id",
        "meaning_schema_version",
        "semantic_address_id",
    ),
    semantic.MemoryPointerV01: (
        "pointer_version",
        "pointer_id",
        "storage_class",
        "object_reference",
        "content_sha256",
        "record_class",
        "byte_length",
        "access_policy_id",
        "sensitivity_class",
        "allowed_use_classes",
        "forbidden_use_classes",
        "summary_read_permitted",
        "payload_read_permitted",
        "creates_authority",
        "creates_permission",
    ),
    semantic.ArtifactPointerV01: (
        "pointer_version",
        "pointer_id",
        "storage_class",
        "object_reference",
        "content_sha256",
        "media_type",
        "byte_length",
        "access_policy_id",
        "sensitivity_class",
        "allowed_use_classes",
        "forbidden_use_classes",
        "summary_read_permitted",
        "payload_read_permitted",
        "creates_authority",
        "creates_permission",
    ),
    semantic.LineageEdgeV01: (
        "lineage_edge_version",
        "lineage_edge_id",
        "source_meaning_record_id",
        "target_meaning_record_id",
        "relation_class",
        "claim_dimension",
        "source_history_hash",
        "evidence_ref_ids",
        "created_at",
        "recording_component",
        "creates_authority",
        "transfers_authority",
    ),
    semantic.DRSAuthorityEnvelopeV01: (
        "authority_envelope_version",
        "authority_envelope_id",
        "authority_class",
        "owning_local_root_id",
        "source_root_decision_input_id",
        "source_root_decision_id",
        "source_root_decision_hash",
        "authority_scope_fingerprint",
        "root_acceptance_state",
        "recording_component",
        "creates_authority",
        "creates_permission",
        "action_permission_present",
    ),
    semantic.DRSTimeEnvelopeV01: (
        "time_envelope_version",
        "time_envelope_id",
        "pt_created_at",
        "kt_as_of",
        "et_observed_at",
        "ct_context_anchor",
        "ttl_seconds",
        "valid_from",
        "valid_to",
        "source_observed_at",
        "source_reported_at",
        "system_ingested_at",
        "system_verified_at",
        "freshness_policy_id",
    ),
    semantic.MeaningRecordV01: (
        "meaning_record_version",
        "meaning_record_id",
        "semantic_address",
        "predecessor_record_id",
        "supersession_reason",
        "safe_summary",
        "semantic_tags",
        "resonance_reason",
        "memory_pointers",
        "artifact_pointers",
        "source_reference_ids",
        "lineage_edges",
        "time_envelope",
        "authority_envelope",
        "persistent_lifecycle_state",
        "risk_hints",
        "conflict_hints",
        "reuse_policy_class",
        "policy_version",
        "schema_versions",
        "content_fingerprint",
        "recording_component",
        "local_reference_kernel_scope",
        "creates_authority",
        "creates_permission",
    ),
    resolution.DRSTemporalQueryV01: (
        "temporal_query_version",
        "query_id",
        "query_mode",
        "semantic_address_id",
        "scope_fingerprint",
        "as_of",
        "evaluation_time",
        "evaluation_time_source",
        "time_range_start",
        "time_range_end",
        "required_time_axes",
        "freshness_policy_id",
        "max_age_seconds",
        "domain",
        "risk_class",
        "reuse_intent",
        "requested_reuse_classes",
        "required_evidence_classes",
        "forbidden_changes",
        "policy_version",
        "schema_versions",
        "owning_local_root_id",
    ),
    resolution.QueryEvaluationStateV01: (
        "query_evaluation_version",
        "query_evaluation_id",
        "query_id",
        "semantic_address_id",
        "meaning_record_id",
        "query_state",
        "evaluated_at",
        "evaluation_time_source",
        "temporal_hard_gate_passed",
        "validity_interval_passed",
        "ttl_freshness_passed",
        "required_time_axes_passed",
        "scope_passed",
        "lifecycle_passed",
        "policy_compatible",
        "schema_compatible",
        "provenance_passed",
        "authority_envelope_passed",
        "required_evidence_passed",
        "forbidden_changes_passed",
        "conflict_passed",
        "quarantine_passed",
        "deadend_passed",
        "action_intent_passed",
        "g2a_action_history_passed",
        "permission_boundary_passed",
        "current_freshness_units",
        "observed_evidence_fingerprint",
        "checked_dependency_fingerprint",
        "source_history_hash",
        "action_history_binding_id",
        "eligible_for_ranking",
        "reason_codes",
        "creates_authority",
        "creates_permission",
    ),
    resolution.ResolutionCandidateV01: (
        "resolution_candidate_version",
        "resolution_candidate_id",
        "query_id",
        "semantic_address_id",
        "meaning_record_id",
        "query_evaluation_id",
        "safe_summary",
        "evidence_ref_ids",
        "source_history_hash",
        "action_history_binding_id",
        "semantic_similarity_units",
        "freshness_units",
        "source_authority_prior_units",
        "lineage_proximity_units",
        "historical_utility_units",
        "gt_advisory_prior_units",
        "conflict_penalty_units",
        "risk_penalty_units",
        "retrieval_cost_units",
        "total_score_units",
        "eligible_for_ranking",
        "reason_codes",
        "creates_authority",
        "creates_permission",
        "creates_final_output",
    ),
    resolution.RetrievalPlanV01: (
        "retrieval_plan_version",
        "retrieval_plan_id",
        "query_id",
        "semantic_address_id",
        "proposed_record_ids",
        "proposed_memory_pointer_ids",
        "proposed_artifact_pointer_ids",
        "requested_descent_class",
        "proposed_budget_id",
        "required_access_policy_ids",
        "reason_codes",
        "root_approval_required",
        "creates_authority",
        "creates_permission",
        "executes_read",
    ),
    resolution.MemoryDescentBudgetV01: (
        "memory_descent_budget_version",
        "memory_descent_budget_id",
        "max_depth",
        "max_records_opened",
        "max_pointers_opened",
        "max_artifacts_opened",
        "max_bytes_opened",
        "max_lineage_edges",
        "max_conflict_records",
    ),
    resolution.MemoryDescentRequestV01: (
        "memory_descent_request_version",
        "memory_descent_request_id",
        "retrieval_plan_id",
        "query_id",
        "owning_local_root_id",
        "root_kernel_id",
        "root_decision_input_id",
        "root_decision_id",
        "root_decision_hash",
        "requested_descent_class",
        "approved_descent_class",
        "proposed_budget_id",
        "approved_budget",
        "approved_record_ids",
        "approved_memory_pointer_ids",
        "approved_artifact_pointer_ids",
        "root_approved",
        "reason_codes",
        "creates_permission",
        "creates_authority",
    ),
    resolution.MemoryDescentResultV01: (
        "memory_descent_result_version",
        "memory_descent_result_id",
        "memory_descent_request_id",
        "retrieval_plan_id",
        "query_id",
        "executed_descent_class",
        "applied_budget_id",
        "opened_record_ids",
        "opened_memory_pointer_ids",
        "opened_artifact_pointer_ids",
        "traversed_lineage_edge_ids",
        "opened_conflict_record_ids",
        "depth_reached",
        "records_opened",
        "pointers_opened",
        "artifacts_opened",
        "bytes_opened",
        "lineage_edges_traversed",
        "conflict_records_opened",
        "safe_summaries",
        "opened_payload_fingerprints",
        "limits_respected",
        "reason_codes",
        "creates_authority",
        "creates_permission",
        "real_world_effects_count",
    ),
    reuse.RootShortcutAuthorizationProjectionV01: (
        "root_shortcut_projection_version",
        "root_shortcut_projection_id",
        "owning_local_root_id",
        "root_kernel_id",
        "root_decision_input_id",
        "root_decision_id",
        "root_decision_hash",
        "selected_candidate_id",
        "semantic_address_id",
        "meaning_record_id",
        "query_id",
        "query_evaluation_id",
        "allowed_reuse_class",
        "scope_fingerprint",
        "policy_version",
        "schema_versions",
        "valid_from",
        "valid_to",
        "root_shortcut_policy_ref",
        "carries_validated_authority_evidence",
        "creates_authority",
        "creates_permission",
        "creates_action_commit_packet",
        "creates_receipt",
        "creates_effect",
        "creates_final_output",
    ),
    reuse.ReuseCertificateV01: (
        "certificate_version",
        "certificate_id",
        "semantic_address_id",
        "meaning_record_id",
        "query_id",
        "query_evaluation_id",
        "resolution_candidate_id",
        "root_shortcut_authorization_projection_id",
        "owning_local_root_id",
        "root_decision_input_id",
        "root_decision_id",
        "root_decision_hash",
        "case_type",
        "scope_fingerprint",
        "required_evidence_classes",
        "observed_evidence_fingerprint",
        "forbidden_changes",
        "checked_dependency_fingerprint",
        "valid_from",
        "valid_to",
        "reuse_class",
        "policy_version",
        "schema_versions",
        "root_shortcut_policy_ref",
        "source_history_hash",
        "action_history_binding_id",
        "issued_at",
        "evaluated_at",
        "creates_authority",
        "creates_permission",
        "creates_final_output",
        "creates_action_commit_packet",
        "creates_receipt",
        "creates_capability",
        "creates_effect_handle",
        "creates_effect",
        "real_world_effects_count",
        "proves_external_truth",
        "proves_action_occurred",
    ),
    resolution.DRSResolutionReportV01: (
        "report_version",
        "report_id",
        "semantic_address",
        "query",
        "source_projections",
        "source_records",
        "query_evaluations",
        "eligible_candidates",
        "ranked_candidate_ids",
        "selected_candidate_id",
        "retrieval_plan",
        "memory_descent_result",
        "root_shortcut_projection",
        "reuse_certificate",
        "context_only_record_ids",
        "historical_only_record_ids",
        "warning_only_record_ids",
        "rerun_required_record_ids",
        "blocked_record_ids",
        "persistent_records_unchanged",
        "provider_calls",
        "network_calls",
        "gemini_calls",
        "external_drs_calls",
        "connector_calls",
        "real_world_effects_count",
        "final_status",
        "reason_codes",
    ),
    compatibility.LegacyDRSProjectionV01: (
        "projection_version",
        "projection_id",
        "source_family",
        "source_version",
        "source_identity",
        "source_hash",
        "target_semantic_address_id",
        "target_meaning_record_id",
        "projection_profile_version",
        "fields_preserved",
        "fields_synthesized",
        "fields_unavailable",
        "downgrade_restrictions",
        "projection_status",
        "answer_shortcut_eligible",
        "reason_codes",
        "creates_authority",
        "creates_permission",
    ),
    reuse.G2AActionHistoryBindingV01: (
        "binding_version",
        "binding_id",
        "packet_id",
        "registry_id",
        "transition_history_sha256",
        "disposition_history_sha256",
        "lifecycle_state",
        "disposition",
        "reservation_owner_packet_id",
        "terminal_receipt_ref",
        "current_status_validation_id",
        "current_status_evaluated_at",
        "current_status_evaluation_time_source",
        "shortcut_eligible",
        "reason_codes",
        "creates_authority",
        "creates_permission",
    ),
}

_IDENTITY_FIELDS = {
    semantic.SemanticAddressV01: "semantic_address_id",
    semantic.MemoryPointerV01: "pointer_id",
    semantic.ArtifactPointerV01: "pointer_id",
    semantic.LineageEdgeV01: "lineage_edge_id",
    semantic.DRSAuthorityEnvelopeV01: "authority_envelope_id",
    semantic.DRSTimeEnvelopeV01: "time_envelope_id",
    semantic.MeaningRecordV01: "meaning_record_id",
    resolution.DRSTemporalQueryV01: "query_id",
    resolution.QueryEvaluationStateV01: "query_evaluation_id",
    resolution.ResolutionCandidateV01: "resolution_candidate_id",
    resolution.RetrievalPlanV01: "retrieval_plan_id",
    resolution.MemoryDescentBudgetV01: "memory_descent_budget_id",
    resolution.MemoryDescentRequestV01: "memory_descent_request_id",
    resolution.MemoryDescentResultV01: "memory_descent_result_id",
    reuse.RootShortcutAuthorizationProjectionV01: "root_shortcut_projection_id",
    reuse.ReuseCertificateV01: "certificate_id",
    resolution.DRSResolutionReportV01: "report_id",
    compatibility.LegacyDRSProjectionV01: "projection_id",
    reuse.G2AActionHistoryBindingV01: "binding_id",
}

_PREFIXES = {
    semantic.SemanticAddressV01: "drsaddr_v01:",
    semantic.MemoryPointerV01: "drsmem_v01:",
    semantic.ArtifactPointerV01: "drsart_v01:",
    semantic.LineageEdgeV01: "drsedge_v01:",
    semantic.DRSAuthorityEnvelopeV01: "drsauth_v01:",
    semantic.DRSTimeEnvelopeV01: "drstime_v01:",
    semantic.MeaningRecordV01: "drsmeaning_v01:",
    resolution.DRSTemporalQueryV01: "drsquery_v01:",
    resolution.QueryEvaluationStateV01: "drsqeval_v01:",
    resolution.ResolutionCandidateV01: "drscandidate_v01:",
    resolution.RetrievalPlanV01: "drsplan_v01:",
    resolution.MemoryDescentBudgetV01: "drsbudget_v01:",
    resolution.MemoryDescentRequestV01: "drsdescentreq_v01:",
    resolution.MemoryDescentResultV01: "drsdescentres_v01:",
    reuse.RootShortcutAuthorizationProjectionV01: "drsrootshortcut_v01:",
    reuse.ReuseCertificateV01: "reusecert_v01:",
    resolution.DRSResolutionReportV01: "drsreport_v01:",
    compatibility.LegacyDRSProjectionV01: "drslegacyproj_v01:",
    reuse.G2AActionHistoryBindingV01: "drsg2ahistory_v01:",
}

_DOMAINS = {
    semantic.SemanticAddressV01: "hedgehog:drs:semantic_address:v01",
    semantic.MemoryPointerV01: "hedgehog:drs:memory_pointer:v01",
    semantic.ArtifactPointerV01: "hedgehog:drs:artifact_pointer:v01",
    semantic.LineageEdgeV01: "hedgehog:drs:lineage_edge:v01",
    semantic.DRSAuthorityEnvelopeV01: "hedgehog:drs:authority_envelope:v01",
    semantic.DRSTimeEnvelopeV01: "hedgehog:drs:time_envelope:v01",
    semantic.MeaningRecordV01: "hedgehog:drs:meaning_record:v01",
    resolution.DRSTemporalQueryV01: "hedgehog:drs:temporal_query:v01",
    resolution.QueryEvaluationStateV01: "hedgehog:drs:query_evaluation:v01",
    resolution.ResolutionCandidateV01: "hedgehog:drs:resolution_candidate:v01",
    resolution.RetrievalPlanV01: "hedgehog:drs:retrieval_plan:v01",
    resolution.MemoryDescentBudgetV01: "hedgehog:drs:memory_descent_budget:v01",
    resolution.MemoryDescentRequestV01: "hedgehog:drs:memory_descent_request:v01",
    resolution.MemoryDescentResultV01: "hedgehog:drs:memory_descent_result:v01",
    reuse.RootShortcutAuthorizationProjectionV01: "hedgehog:drs:root_shortcut_projection:v01",
    reuse.ReuseCertificateV01: "hedgehog:drs:reuse_certificate:v01",
    resolution.DRSResolutionReportV01: "hedgehog:drs:resolution_report:v01",
    compatibility.LegacyDRSProjectionV01: "hedgehog:drs:legacy_projection:v01",
    reuse.G2AActionHistoryBindingV01: "hedgehog:drs:g2a_history_binding:v01",
}

_EXPECTED_SOURCE_PROFILE_FIELDS = {
    "LOCAL_DRS_DICT": (
        "record_id",
        "layer",
        "type",
        "domain",
        "content",
        "pointer",
        "time_envelope",
        "provenance",
        "status",
        "gt",
        "viability_feedback",
        "validation",
        "hash",
        "previous_hash",
        "trace_refs",
        "source_refs",
    ),
    "DRS_RECORD_SCHEMA_V0": (
        "record_id",
        "layer",
        "type",
        "domain",
        "content",
        "pointer",
        "time_envelope",
        "provenance",
        "status",
        "gt",
        "viability_feedback",
        "validation",
        "hash",
        "previous_hash",
        "trace_refs",
        "source_refs",
    ),
    "SEMANTIC_DRS_RECORD_INPUT": (
        "record_id",
        "domain",
        "content",
        "semantic_keys",
        "layer",
        "record_type",
        "time_envelope",
        "provenance",
        "trace_refs",
        "source_refs",
        "status",
        "gt",
        "validation",
        "root_final_ref",
        "worldstate_ref",
        "poisoning_markers",
    ),
    "DRS_RECORD_V02": (
        "record_id",
        "record_kind",
        "summary",
        "time_envelope",
        "lineage_refs",
        "source_refs",
        "provenance_refs",
        "prior_trace_ref",
        "root_final_ref",
        "artifact_refs",
        "validation_refs",
        "contains_receipt",
        "contains_action_permission",
        "accepted_evidence",
        "changed_facts",
        "conflict_pressure",
        "conflicting_provenance",
        "duplicate_poisoning_pressure",
        "wrong_domain_near_match",
        "quarantine_proximity",
        "deadend_proximity",
        "policy_ok",
        "permission_ok",
        "root_shortcut_allowed",
        "reuse_score",
        "semantic_similarity_score",
        "truth_claimed",
        "authority_claimed",
        "action_permission_claimed",
        "final_output_claimed",
    ),
    "DRS_FRESHNESS_ENVELOPE_V02": (
        "physical_time",
        "knowledge_time",
        "event_time",
        "context_time",
        "ttl_seconds",
        "validity_start",
        "validity_end",
        "source_observed_at",
        "system_ingested_at",
        "freshness_class",
    ),
    "TEMPORAL_QUERY_V02": (
        "query_id",
        "as_of",
        "context_time",
        "freshness_bias",
        "time_range_start",
        "time_range_end",
        "require_root_review",
        "allow_direct_reuse_if_all_gates_pass",
    ),
}

_VALIDATORS = {
    semantic.SemanticAddressV01: semantic.validate_semantic_address_v01,
    semantic.MemoryPointerV01: semantic.validate_memory_pointer_v01,
    semantic.ArtifactPointerV01: semantic.validate_artifact_pointer_v01,
    semantic.LineageEdgeV01: semantic.validate_lineage_edge_v01,
    semantic.DRSAuthorityEnvelopeV01: semantic.validate_drs_authority_envelope_v01,
    semantic.DRSTimeEnvelopeV01: semantic.validate_drs_time_envelope_v01,
    semantic.MeaningRecordV01: semantic.validate_meaning_record_v01,
    resolution.DRSTemporalQueryV01: resolution.validate_drs_temporal_query_v01,
    resolution.QueryEvaluationStateV01: resolution.validate_query_evaluation_state_v01,
    resolution.ResolutionCandidateV01: resolution.validate_resolution_candidate_v01,
    resolution.RetrievalPlanV01: resolution.validate_retrieval_plan_v01,
    resolution.MemoryDescentBudgetV01: resolution.validate_memory_descent_budget_v01,
    resolution.MemoryDescentRequestV01: resolution.validate_memory_descent_request_v01,
    resolution.MemoryDescentResultV01: resolution.validate_memory_descent_result_v01,
    reuse.RootShortcutAuthorizationProjectionV01: reuse.validate_root_shortcut_authorization_projection_v01,
    reuse.ReuseCertificateV01: reuse.validate_reuse_certificate_v01,
    resolution.DRSResolutionReportV01: resolution.validate_drs_resolution_report_v01,
    compatibility.LegacyDRSProjectionV01: compatibility.validate_legacy_drs_projection_v01,
    reuse.G2AActionHistoryBindingV01: reuse.validate_g2a_action_history_binding_v01,
}

_SERIALIZERS = {
    semantic.SemanticAddressV01: semantic.semantic_address_to_plain_data_v01,
    semantic.MemoryPointerV01: semantic.memory_pointer_to_plain_data_v01,
    semantic.ArtifactPointerV01: semantic.artifact_pointer_to_plain_data_v01,
    semantic.LineageEdgeV01: semantic.lineage_edge_to_plain_data_v01,
    semantic.DRSAuthorityEnvelopeV01: semantic.drs_authority_envelope_to_plain_data_v01,
    semantic.DRSTimeEnvelopeV01: semantic.drs_time_envelope_to_plain_data_v01,
    semantic.MeaningRecordV01: semantic.meaning_record_to_plain_data_v01,
    resolution.DRSTemporalQueryV01: resolution.drs_temporal_query_to_plain_data_v01,
    resolution.QueryEvaluationStateV01: resolution.query_evaluation_state_to_plain_data_v01,
    resolution.ResolutionCandidateV01: resolution.resolution_candidate_to_plain_data_v01,
    resolution.RetrievalPlanV01: resolution.retrieval_plan_to_plain_data_v01,
    resolution.MemoryDescentBudgetV01: resolution.memory_descent_budget_to_plain_data_v01,
    resolution.MemoryDescentRequestV01: resolution.memory_descent_request_to_plain_data_v01,
    resolution.MemoryDescentResultV01: resolution.memory_descent_result_to_plain_data_v01,
    reuse.RootShortcutAuthorizationProjectionV01: reuse.root_shortcut_authorization_projection_to_plain_data_v01,
    reuse.ReuseCertificateV01: reuse.reuse_certificate_to_plain_data_v01,
    resolution.DRSResolutionReportV01: resolution.drs_resolution_report_to_plain_data_v01,
    compatibility.LegacyDRSProjectionV01: compatibility.legacy_drs_projection_to_plain_data_v01,
    reuse.G2AActionHistoryBindingV01: reuse.g2a_action_history_binding_to_plain_data_v01,
}

_EXPECTED_IDENTITY_VECTORS = {
    "SemanticAddressV01": "drsaddr_v01:2cc79cf3bf056291d8559161cdbb6392e093d8ce2e57b2f8585838cfdd99c335",
    "MemoryPointerV01": "drsmem_v01:65aa601f80b313755b56faefd2599370300472759aa2ba4548f64247ecbaecf2",
    "ArtifactPointerV01": "drsart_v01:5a7da3fab6b92e4c94f968d483181fad52aab1b649c1b20c7e6b42707d5f1caa",
    "LineageEdgeV01": "drsedge_v01:09863122d73da8198c6beb139f9eb8cd0337e2f854a18328a7c1b96c1bc46ba9",
    "DRSAuthorityEnvelopeV01": "drsauth_v01:7667beb9305e86a192eb8362a05c4dda3d806500a17d8bbb01bba5f9b8224216",
    "DRSTimeEnvelopeV01": "drstime_v01:4760b0f0700540dc03c444b8578d7709314f5f059b01dcaf300ddddff2724677",
    "MeaningRecordV01": "drsmeaning_v01:f34967178228b6ebfe35100fd9e6d16ea80ddc1afb7f54c62b8d7e57b58d135c",
    "DRSTemporalQueryV01": "drsquery_v01:54858829a59839e722f446dc6ecfda9d1c080cbc3d4c18b8040d0eba6dd1c401",
    "QueryEvaluationStateV01": "drsqeval_v01:2a1bd0daa5b10f36f30627b349ec352a7b875548b9e5ae45f1b760adae7669ed",
    "ResolutionCandidateV01": "drscandidate_v01:e1d013a9259640d99627810ca1ef87908b956073c805af2cd5d7c89d061ddc6b",
    "RetrievalPlanV01": "drsplan_v01:382e54db1b446bf803c1a2107bdd97f1212360693bffc4780a8bc8ab9fdfdec1",
    "MemoryDescentBudgetV01": "drsbudget_v01:d2c9796587aca24b391ae93e051e7e6e2cd6b99a9afe35ec0782a7ecb7f3d2ce",
    "MemoryDescentRequestV01": "drsdescentreq_v01:f464d7ed56c57c570cc8858e7b21c99237cdea7dacf33148a4d3d0585354d762",
    "MemoryDescentResultV01": "drsdescentres_v01:0e262ba2c6f12ae4ab2cdd4c237c50e1bddf952fadfc39a9293e9801ee490a6c",
    "RootShortcutAuthorizationProjectionV01": "drsrootshortcut_v01:18bf04ed1ce1379889968fdda4da21683442d17bd87b7f385f4fd72440e46983",
    "ReuseCertificateV01": "reusecert_v01:759b0ca668b1bfc561ff7d691f3492667c08461a10d76a9024b20a36d22e3631",
    "DRSResolutionReportV01": "drsreport_v01:fa1716e5786626e9ebc1b3af078c94f6104922ca185a47621b117f8da4f05019",
    "LegacyDRSProjectionV01": "drslegacyproj_v01:f4ee5c96b3ccc323e1e24ca96a7cce98ff77469f2188d4d5fecba4ae028d230f",
    "G2AActionHistoryBindingV01": "drsg2ahistory_v01:f7007b1946ac505069ce61434b493891edb9187feeaee45888d63245c8d816b7",
}

_STRING_CONTRACT_GROUPS = (
    (
        "EXACT_TOKEN",
        {
            semantic.SemanticAddressV01: (
                "namespace",
                "domain",
                "subject_class",
                "intent_class",
                "meaning_schema_id",
                "meaning_schema_version",
            ),
            semantic.MemoryPointerV01: ("record_class",),
            semantic.LineageEdgeV01: (
                "claim_dimension",
                "recording_component",
            ),
            semantic.DRSAuthorityEnvelopeV01: ("recording_component",),
            semantic.MeaningRecordV01: (
                "reuse_policy_class",
                "policy_version",
                "recording_component",
            ),
            resolution.DRSTemporalQueryV01: (
                "domain",
                "risk_class",
                "policy_version",
            ),
        },
    ),
    (
        "EXACT_REFERENCE",
        {
            semantic.MemoryPointerV01: (
                "object_reference",
                "access_policy_id",
            ),
            semantic.ArtifactPointerV01: (
                "object_reference",
                "access_policy_id",
            ),
            semantic.DRSAuthorityEnvelopeV01: (
                "owning_local_root_id",
                "source_root_decision_input_id",
                "source_root_decision_id",
            ),
            semantic.DRSTimeEnvelopeV01: ("freshness_policy_id",),
            resolution.DRSTemporalQueryV01: (
                "freshness_policy_id",
                "owning_local_root_id",
            ),
            resolution.MemoryDescentRequestV01: (
                "owning_local_root_id",
                "root_kernel_id",
                "root_decision_input_id",
                "root_decision_id",
            ),
            reuse.RootShortcutAuthorizationProjectionV01: (
                "owning_local_root_id",
                "root_kernel_id",
                "root_decision_input_id",
                "root_decision_id",
                "policy_version",
                "root_shortcut_policy_ref",
            ),
            reuse.ReuseCertificateV01: (
                "owning_local_root_id",
                "root_decision_input_id",
                "root_decision_id",
                "policy_version",
                "root_shortcut_policy_ref",
            ),
            reuse.G2AActionHistoryBindingV01: (
                "packet_id",
                "registry_id",
                "reservation_owner_packet_id",
                "terminal_receipt_ref",
                "current_status_validation_id",
            ),
            compatibility.LegacyDRSProjectionV01: ("source_identity",),
        },
    ),
    (
        "EXACT_SAFE_TEXT",
        {
            semantic.MeaningRecordV01: (
                "supersession_reason",
                "safe_summary",
                "resonance_reason",
            ),
            resolution.ResolutionCandidateV01: ("safe_summary",),
        },
    ),
    (
        "EXACT_MEDIA_TYPE",
        {semantic.ArtifactPointerV01: ("media_type",)},
    ),
    (
        "EXACT_SHA256",
        {
            semantic.MemoryPointerV01: ("content_sha256",),
            semantic.ArtifactPointerV01: ("content_sha256",),
            semantic.LineageEdgeV01: ("source_history_hash",),
            semantic.DRSAuthorityEnvelopeV01: (
                "source_root_decision_hash",
                "authority_scope_fingerprint",
            ),
            semantic.MeaningRecordV01: ("content_fingerprint",),
            resolution.DRSTemporalQueryV01: ("scope_fingerprint",),
            resolution.QueryEvaluationStateV01: (
                "observed_evidence_fingerprint",
                "checked_dependency_fingerprint",
                "source_history_hash",
            ),
            resolution.ResolutionCandidateV01: ("source_history_hash",),
            resolution.MemoryDescentRequestV01: ("root_decision_hash",),
            reuse.RootShortcutAuthorizationProjectionV01: (
                "root_decision_hash",
                "scope_fingerprint",
            ),
            reuse.ReuseCertificateV01: (
                "root_decision_hash",
                "scope_fingerprint",
                "observed_evidence_fingerprint",
                "checked_dependency_fingerprint",
                "source_history_hash",
            ),
            reuse.G2AActionHistoryBindingV01: (
                "transition_history_sha256",
                "disposition_history_sha256",
            ),
            compatibility.LegacyDRSProjectionV01: ("source_hash",),
        },
    ),
    (
        "EXACT_TYPED_G2B_CANONICAL_ID",
        {
            semantic.SemanticAddressV01: ("semantic_address_id",),
            semantic.MemoryPointerV01: ("pointer_id",),
            semantic.ArtifactPointerV01: ("pointer_id",),
            semantic.LineageEdgeV01: (
                "lineage_edge_id",
                "source_meaning_record_id",
                "target_meaning_record_id",
            ),
            semantic.DRSAuthorityEnvelopeV01: ("authority_envelope_id",),
            semantic.DRSTimeEnvelopeV01: ("time_envelope_id",),
            semantic.MeaningRecordV01: (
                "meaning_record_id",
                "predecessor_record_id",
            ),
            resolution.DRSTemporalQueryV01: (
                "query_id",
                "semantic_address_id",
            ),
            resolution.QueryEvaluationStateV01: (
                "query_evaluation_id",
                "query_id",
                "semantic_address_id",
                "meaning_record_id",
                "action_history_binding_id",
            ),
            resolution.ResolutionCandidateV01: (
                "resolution_candidate_id",
                "query_id",
                "semantic_address_id",
                "meaning_record_id",
                "query_evaluation_id",
                "action_history_binding_id",
            ),
            resolution.RetrievalPlanV01: (
                "retrieval_plan_id",
                "query_id",
                "semantic_address_id",
                "proposed_budget_id",
            ),
            resolution.MemoryDescentBudgetV01: (
                "memory_descent_budget_id",
            ),
            resolution.MemoryDescentRequestV01: (
                "memory_descent_request_id",
                "retrieval_plan_id",
                "query_id",
                "proposed_budget_id",
            ),
            resolution.MemoryDescentResultV01: (
                "memory_descent_result_id",
                "memory_descent_request_id",
                "retrieval_plan_id",
                "query_id",
                "applied_budget_id",
            ),
            resolution.DRSResolutionReportV01: (
                "report_id",
                "selected_candidate_id",
            ),
            reuse.RootShortcutAuthorizationProjectionV01: (
                "root_shortcut_projection_id",
                "selected_candidate_id",
                "semantic_address_id",
                "meaning_record_id",
                "query_id",
                "query_evaluation_id",
            ),
            reuse.ReuseCertificateV01: (
                "certificate_id",
                "semantic_address_id",
                "meaning_record_id",
                "query_id",
                "query_evaluation_id",
                "resolution_candidate_id",
                "root_shortcut_authorization_projection_id",
                "action_history_binding_id",
            ),
            reuse.G2AActionHistoryBindingV01: ("binding_id",),
            compatibility.LegacyDRSProjectionV01: (
                "projection_id",
                "target_semantic_address_id",
                "target_meaning_record_id",
            ),
        },
    ),
    (
        "EXACT_ENUM",
        {
            semantic.SemanticAddressV01: ("address_profile_version",),
            semantic.MemoryPointerV01: (
                "pointer_version",
                "storage_class",
                "sensitivity_class",
            ),
            semantic.ArtifactPointerV01: (
                "pointer_version",
                "storage_class",
                "sensitivity_class",
            ),
            semantic.LineageEdgeV01: (
                "lineage_edge_version",
                "relation_class",
            ),
            semantic.DRSAuthorityEnvelopeV01: (
                "authority_envelope_version",
                "authority_class",
                "root_acceptance_state",
            ),
            semantic.DRSTimeEnvelopeV01: ("time_envelope_version",),
            semantic.MeaningRecordV01: (
                "meaning_record_version",
                "persistent_lifecycle_state",
                "local_reference_kernel_scope",
            ),
            resolution.DRSTemporalQueryV01: (
                "temporal_query_version",
                "query_mode",
                "evaluation_time_source",
                "reuse_intent",
            ),
            resolution.QueryEvaluationStateV01: (
                "query_evaluation_version",
                "query_state",
                "evaluation_time_source",
            ),
            resolution.ResolutionCandidateV01: (
                "resolution_candidate_version",
            ),
            resolution.RetrievalPlanV01: (
                "retrieval_plan_version",
                "requested_descent_class",
            ),
            resolution.MemoryDescentBudgetV01: (
                "memory_descent_budget_version",
            ),
            resolution.MemoryDescentRequestV01: (
                "memory_descent_request_version",
                "requested_descent_class",
                "approved_descent_class",
            ),
            resolution.MemoryDescentResultV01: (
                "memory_descent_result_version",
                "executed_descent_class",
            ),
            resolution.DRSResolutionReportV01: (
                "report_version",
                "final_status",
            ),
            reuse.RootShortcutAuthorizationProjectionV01: (
                "root_shortcut_projection_version",
                "allowed_reuse_class",
            ),
            reuse.ReuseCertificateV01: (
                "certificate_version",
                "case_type",
                "reuse_class",
            ),
            reuse.G2AActionHistoryBindingV01: (
                "binding_version",
                "lifecycle_state",
                "disposition",
                "current_status_evaluation_time_source",
            ),
            compatibility.LegacyDRSProjectionV01: (
                "projection_version",
                "source_family",
                "source_version",
                "projection_profile_version",
                "projection_status",
            ),
        },
    ),
    (
        "TOKEN_TUPLE",
        {
            semantic.MemoryPointerV01: (
                "allowed_use_classes",
                "forbidden_use_classes",
            ),
            semantic.ArtifactPointerV01: (
                "allowed_use_classes",
                "forbidden_use_classes",
            ),
            semantic.MeaningRecordV01: (
                "semantic_tags",
                "schema_versions",
            ),
            resolution.DRSTemporalQueryV01: (
                "required_time_axes",
                "requested_reuse_classes",
                "required_evidence_classes",
                "forbidden_changes",
                "schema_versions",
            ),
            resolution.QueryEvaluationStateV01: ("reason_codes",),
            resolution.ResolutionCandidateV01: ("reason_codes",),
            resolution.RetrievalPlanV01: ("reason_codes",),
            resolution.MemoryDescentRequestV01: ("reason_codes",),
            resolution.MemoryDescentResultV01: ("reason_codes",),
            resolution.DRSResolutionReportV01: ("reason_codes",),
            reuse.RootShortcutAuthorizationProjectionV01: (
                "schema_versions",
            ),
            reuse.ReuseCertificateV01: (
                "required_evidence_classes",
                "forbidden_changes",
                "schema_versions",
            ),
            reuse.G2AActionHistoryBindingV01: ("reason_codes",),
            compatibility.LegacyDRSProjectionV01: (
                "downgrade_restrictions",
                "reason_codes",
            ),
        },
    ),
    (
        "REFERENCE_TUPLE",
        {
            semantic.LineageEdgeV01: ("evidence_ref_ids",),
            semantic.MeaningRecordV01: ("source_reference_ids",),
            resolution.ResolutionCandidateV01: ("evidence_ref_ids",),
            resolution.RetrievalPlanV01: (
                "required_access_policy_ids",
            ),
        },
    ),
    (
        "SAFE_TEXT_TUPLE",
        {
            semantic.MeaningRecordV01: ("risk_hints", "conflict_hints"),
            resolution.MemoryDescentResultV01: ("safe_summaries",),
        },
    ),
    (
        "SHA256_TUPLE",
        {
            resolution.MemoryDescentResultV01: (
                "opened_payload_fingerprints",
            )
        },
    ),
    (
        "TYPED_ID_TUPLE",
        {
            resolution.RetrievalPlanV01: (
                "proposed_record_ids",
                "proposed_memory_pointer_ids",
                "proposed_artifact_pointer_ids",
            ),
            resolution.MemoryDescentRequestV01: (
                "approved_record_ids",
                "approved_memory_pointer_ids",
                "approved_artifact_pointer_ids",
            ),
            resolution.MemoryDescentResultV01: (
                "opened_record_ids",
                "opened_memory_pointer_ids",
                "opened_artifact_pointer_ids",
                "traversed_lineage_edge_ids",
                "opened_conflict_record_ids",
            ),
            resolution.DRSResolutionReportV01: (
                "ranked_candidate_ids",
                "context_only_record_ids",
                "historical_only_record_ids",
                "warning_only_record_ids",
                "rerun_required_record_ids",
                "blocked_record_ids",
            ),
        },
    ),
    (
        "FIELD_NAME_TUPLE",
        {
            compatibility.LegacyDRSProjectionV01: (
                "fields_preserved",
                "fields_synthesized",
                "fields_unavailable",
            )
        },
    ),
)

_TUPLE_MAXIMA = {
    (semantic.MeaningRecordV01, "semantic_tags"): 32,
    (semantic.MeaningRecordV01, "risk_hints"): 32,
    (semantic.MeaningRecordV01, "conflict_hints"): 32,
    (semantic.MeaningRecordV01, "schema_versions"): 32,
    (resolution.DRSTemporalQueryV01, "required_time_axes"): 16,
    (resolution.DRSTemporalQueryV01, "requested_reuse_classes"): 16,
    (resolution.DRSTemporalQueryV01, "required_evidence_classes"): 32,
    (resolution.DRSTemporalQueryV01, "forbidden_changes"): 32,
    (resolution.DRSTemporalQueryV01, "schema_versions"): 32,
    (resolution.QueryEvaluationStateV01, "reason_codes"): 32,
    (resolution.MemoryDescentResultV01, "safe_summaries"): 32,
    (resolution.MemoryDescentResultV01, "opened_payload_fingerprints"): 4,
    (resolution.MemoryDescentResultV01, "reason_codes"): 32,
    (reuse.RootShortcutAuthorizationProjectionV01, "schema_versions"): 32,
    (reuse.ReuseCertificateV01, "required_evidence_classes"): 32,
    (reuse.ReuseCertificateV01, "forbidden_changes"): 32,
    (reuse.ReuseCertificateV01, "schema_versions"): 32,
    (reuse.G2AActionHistoryBindingV01, "reason_codes"): 32,
    (compatibility.LegacyDRSProjectionV01, "fields_preserved"): 128,
    (compatibility.LegacyDRSProjectionV01, "fields_synthesized"): 128,
    (compatibility.LegacyDRSProjectionV01, "fields_unavailable"): 128,
    (compatibility.LegacyDRSProjectionV01, "downgrade_restrictions"): 128,
    (compatibility.LegacyDRSProjectionV01, "reason_codes"): 128,
}
_SAFE_TEXT_MAXIMA = {
    (semantic.MeaningRecordV01, "supersession_reason"): 256,
    (semantic.MeaningRecordV01, "safe_summary"): 1024,
    (semantic.MeaningRecordV01, "resonance_reason"): 512,
    (semantic.MeaningRecordV01, "risk_hints"): 256,
    (semantic.MeaningRecordV01, "conflict_hints"): 256,
    (resolution.ResolutionCandidateV01, "safe_summary"): 1024,
    (resolution.MemoryDescentResultV01, "safe_summaries"): 1024,
}
_ENUM_VALUES = {
    (semantic.MemoryPointerV01, "storage_class"): (
        "LOCAL_MEANING_RECORD",
        "LOCAL_LINEAGE_SET",
        "LOCAL_CONFLICT_SET",
        "LOCAL_DEADEND_PROOF",
    ),
    (semantic.ArtifactPointerV01, "storage_class"): (
        "LOCAL_DOCUMENT",
        "LOCAL_AUDIT_TRACE",
        "LOCAL_SEALED_EVIDENCE",
    ),
    (semantic.MemoryPointerV01, "sensitivity_class"): (
        "PUBLIC",
        "INTERNAL",
        "CONFIDENTIAL_REFERENCE_ONLY",
        "SECRET_REFERENCE_ONLY",
    ),
    (semantic.ArtifactPointerV01, "sensitivity_class"): (
        "PUBLIC",
        "INTERNAL",
        "CONFIDENTIAL_REFERENCE_ONLY",
        "SECRET_REFERENCE_ONLY",
    ),
    (semantic.LineageEdgeV01, "relation_class"): (
        "DERIVED_FROM",
        "SUPPORTS",
        "WARNS_AGAINST",
        "CONTRADICTS",
        "SUPERSEDES",
        "REPLACES",
        "SAME_TRACE",
        "REFERENCES",
        "BLOCKED_BY_POLICY",
        "DEGRADED_FROM",
    ),
    (semantic.DRSAuthorityEnvelopeV01, "authority_class"): (
        "UNTRUSTED_SEMANTIC_DRAFT",
        "CONNECTOR_OBSERVATION",
        "EVIDENCE_CANDIDATE",
        "ROOT_ACCEPTED_CONTEXT",
        "ROOT_ACCEPTED_WORK",
        "ROOT_FINAL_REFERENCE",
        "ACTION_HISTORY_REFERENCE",
    ),
    (semantic.DRSAuthorityEnvelopeV01, "root_acceptance_state"): (
        "UNREVIEWED",
        "ACCEPTED_CONTEXT",
        "ACCEPTED_WORK",
        "REJECTED",
        "QUARANTINED",
    ),
    (semantic.MeaningRecordV01, "persistent_lifecycle_state"): (
        "ACTIVE",
        "COMPLETED",
        "REJECTED",
        "QUARANTINED",
        "DEADEND",
        "ARCHIVED",
    ),
    (semantic.MeaningRecordV01, "local_reference_kernel_scope"): (
        "LOCAL_REFERENCE_KERNEL",
    ),
    (resolution.DRSTemporalQueryV01, "query_mode"): (
        "CURRENT_DECISION",
        "HISTORICAL_AS_OF",
        "AUDIT_REPLAY",
        "TREND_ANALYSIS",
        "MEMORY_CONTEXT_ONLY",
        "DIRECT_REUSE_CANDIDATE",
    ),
    (resolution.DRSTemporalQueryV01, "evaluation_time_source"): (
        "INJECTED_CURRENT_DECISION_TIME",
        "RECORDED_HISTORICAL_AS_OF_TIME",
        "RECORDED_AUDIT_REPLAY_TIME",
        "INJECTED_ANALYSIS_TIME",
    ),
    (resolution.DRSTemporalQueryV01, "reuse_intent"): (
        "CONTEXT",
        "INFORMATIONAL_SHORTCUT_CONSIDERATION",
        "WARNING_LOOKUP",
        "HISTORY_INSPECTION",
    ),
    (resolution.QueryEvaluationStateV01, "query_state"): (
        "FRESH_CANDIDATE",
        "STALE_CONTEXT_ONLY",
        "HISTORICAL_ONLY",
        "WARNING_ONLY",
        "RERUN_REQUIRED",
        "BLOCKED_BY_TIME",
        "BLOCKED_BY_SCOPE",
        "BLOCKED_BY_POLICY",
        "BLOCKED_BY_PROVENANCE",
        "BLOCKED_BY_CONFLICT",
        "BLOCKED_BY_QUARANTINE",
        "BLOCKED_BY_DEADEND",
        "BLOCKED_BY_REQUIRED_EVIDENCE",
        "BLOCKED_BY_FORBIDDEN_CHANGE",
        "BLOCKED_BY_ACTION_HISTORY",
        "BLOCKED_BY_ACTION_INTENT",
    ),
    (resolution.QueryEvaluationStateV01, "evaluation_time_source"): (
        "INJECTED_CURRENT_DECISION_TIME",
        "RECORDED_HISTORICAL_AS_OF_TIME",
        "RECORDED_AUDIT_REPLAY_TIME",
        "INJECTED_ANALYSIS_TIME",
    ),
    (resolution.RetrievalPlanV01, "requested_descent_class"): (
        "SUMMARY_ONLY",
        "OPEN_ONE_ARTIFACT",
        "OPEN_LINEAGE_NEIGHBORHOOD",
        "OPEN_CONFLICT_SET",
        "OPEN_DEADEND_PROOF",
        "OPEN_FULL_TRACE",
    ),
    (resolution.MemoryDescentRequestV01, "requested_descent_class"): (
        "SUMMARY_ONLY",
        "OPEN_ONE_ARTIFACT",
        "OPEN_LINEAGE_NEIGHBORHOOD",
        "OPEN_CONFLICT_SET",
        "OPEN_DEADEND_PROOF",
        "OPEN_FULL_TRACE",
    ),
    (resolution.MemoryDescentRequestV01, "approved_descent_class"): (
        "SUMMARY_ONLY",
        "OPEN_ONE_ARTIFACT",
        "OPEN_LINEAGE_NEIGHBORHOOD",
        "OPEN_CONFLICT_SET",
        "OPEN_DEADEND_PROOF",
        "OPEN_FULL_TRACE",
    ),
    (resolution.MemoryDescentResultV01, "executed_descent_class"): (
        "SUMMARY_ONLY",
        "OPEN_ONE_ARTIFACT",
        "OPEN_LINEAGE_NEIGHBORHOOD",
        "OPEN_CONFLICT_SET",
        "OPEN_DEADEND_PROOF",
        "OPEN_FULL_TRACE",
    ),
    (resolution.DRSResolutionReportV01, "final_status"): (
        "PASS",
        "FAIL_CLOSED",
    ),
    (reuse.RootShortcutAuthorizationProjectionV01, "allowed_reuse_class"): (
        "CONTEXT_ONLY",
        "ANSWER_SHORTCUT",
    ),
    (reuse.ReuseCertificateV01, "case_type"): (
        "NON_ACTION_INFORMATIONAL",
    ),
    (reuse.ReuseCertificateV01, "reuse_class"): (
        "CONTEXT_ONLY",
        "ANSWER_SHORTCUT",
    ),
    (reuse.G2AActionHistoryBindingV01, "lifecycle_state"): (
        "CREATED",
        "ROOT_AUTHORIZED",
        "QUEUED",
        "PENDING_FULFILLMENT",
        "FULFILLED_MOCK",
        "RECEIPT_RECEIVED",
        "FAILED",
        "BLOCKED",
        "EXPIRED",
        "REVOKED",
        "SUPERSEDED",
    ),
    (reuse.G2AActionHistoryBindingV01, "disposition"): (
        "UNCLAIMED",
        "RESERVED",
        "CONSUMED",
        "UNCERTAIN_CLOSED",
    ),
    (reuse.G2AActionHistoryBindingV01, "current_status_evaluation_time_source"): (
        "INJECTED_CURRENT_DECISION_TIME",
        "RECORDED_HISTORICAL_AS_OF_TIME",
        "RECORDED_AUDIT_REPLAY_TIME",
        "INJECTED_ANALYSIS_TIME",
    ),
    (compatibility.LegacyDRSProjectionV01, "source_family"): (
        "LOCAL_DRS_DICT",
        "DRS_RECORD_SCHEMA_V0",
        "SEMANTIC_DRS_RECORD_INPUT",
        "DRS_RECORD_V02",
        "DRS_FRESHNESS_ENVELOPE_V02",
        "TEMPORAL_QUERY_V02",
    ),
    (compatibility.LegacyDRSProjectionV01, "source_version"): (
        "legacy_local_drs_dict_v0",
        "drs_record_schema_v0",
        "semantic_drs_record_input_v0",
        "drs_record_v02",
        "drs_freshness_envelope_v02",
        "temporal_query_v02",
    ),
    (compatibility.LegacyDRSProjectionV01, "projection_status"): (
        "CANONICAL_COMPLETE",
        "CANONICAL_CONTEXT_ONLY",
        "RERUN_REQUIRED",
        "BLOCKED",
        "PROJECTION_REJECTED",
    ),
}


def _typed_prefix(contract_type: type, field_name: str) -> str:
    if field_name == _IDENTITY_FIELDS[contract_type]:
        return _PREFIXES[contract_type]
    if "semantic_address" in field_name:
        return "drsaddr_v01:"
    if "query_evaluation" in field_name:
        return "drsqeval_v01:"
    if field_name == "query_id":
        return "drsquery_v01:"
    if "candidate" in field_name:
        return "drscandidate_v01:"
    if "memory_pointer" in field_name:
        return "drsmem_v01:"
    if "artifact_pointer" in field_name:
        return "drsart_v01:"
    if "lineage_edge" in field_name:
        return "drsedge_v01:"
    if "budget" in field_name:
        return "drsbudget_v01:"
    if "descent_request" in field_name:
        return "drsdescentreq_v01:"
    if "retrieval_plan" in field_name:
        return "drsplan_v01:"
    if "root_shortcut_authorization_projection" in field_name:
        return "drsrootshortcut_v01:"
    if "action_history" in field_name:
        return "drsg2ahistory_v01:"
    if "meaning_record" in field_name or field_name == "predecessor_record_id":
        return "drsmeaning_v01:"
    raise AssertionError((contract_type.__name__, field_name))


def _contract_detail(
    contract_type: type,
    field_name: str,
    contract_class: str,
) -> object:
    if contract_class == "EXACT_TYPED_G2B_CANONICAL_ID":
        return _typed_prefix(contract_type, field_name)
    if contract_class == "EXACT_ENUM":
        if field_name.endswith("version") or "version" in field_name:
            if (
                contract_type is compatibility.LegacyDRSProjectionV01
                and field_name == "source_version"
            ):
                return _ENUM_VALUES[(contract_type, field_name)]
            return ("v0.1",)
        return _ENUM_VALUES[(contract_type, field_name)]
    if contract_class == "TYPED_ID_TUPLE":
        singular = {
            "proposed_record_ids": "meaning_record_id",
            "approved_record_ids": "meaning_record_id",
            "opened_record_ids": "meaning_record_id",
            "opened_conflict_record_ids": "meaning_record_id",
            "context_only_record_ids": "meaning_record_id",
            "historical_only_record_ids": "meaning_record_id",
            "warning_only_record_ids": "meaning_record_id",
            "rerun_required_record_ids": "meaning_record_id",
            "blocked_record_ids": "meaning_record_id",
            "proposed_memory_pointer_ids": "memory_pointer_id",
            "approved_memory_pointer_ids": "memory_pointer_id",
            "opened_memory_pointer_ids": "memory_pointer_id",
            "proposed_artifact_pointer_ids": "artifact_pointer_id",
            "approved_artifact_pointer_ids": "artifact_pointer_id",
            "opened_artifact_pointer_ids": "artifact_pointer_id",
            "traversed_lineage_edge_ids": "lineage_edge_id",
            "ranked_candidate_ids": "candidate_id",
        }[field_name]
        return _typed_prefix(contract_type, singular)
    return contract_class


def _item_maximum(
    contract_type: type,
    field_name: str,
    contract_class: str,
) -> int | None:
    if contract_class in ("EXACT_TOKEN", "TOKEN_TUPLE", "EXACT_FIELD_NAME", "FIELD_NAME_TUPLE"):
        return 128
    if contract_class in ("EXACT_REFERENCE", "REFERENCE_TUPLE"):
        return 256
    if contract_class in ("EXACT_SAFE_TEXT", "SAFE_TEXT_TUPLE"):
        return _SAFE_TEXT_MAXIMA[(contract_type, field_name)]
    if contract_class == "EXACT_MEDIA_TYPE":
        return 128
    if contract_class in ("EXACT_SHA256", "SHA256_TUPLE"):
        return 64
    if contract_class in (
        "EXACT_TYPED_G2B_CANONICAL_ID",
        "TYPED_ID_TUPLE",
    ):
        detail = _contract_detail(
            contract_type, field_name, contract_class
        )
        return len(detail) + 64
    return None


_STRING_FIELD_CONTRACT_MATRIX = tuple(
    (
        contract_type.__module__,
        contract_type,
        field_name,
        contract_class,
        _contract_detail(contract_type, field_name, contract_class),
        _item_maximum(contract_type, field_name, contract_class),
        (
            _TUPLE_MAXIMA.get((contract_type, field_name), 64)
            if contract_class.endswith("_TUPLE")
            else None
        ),
        (
            field_name != "safe_summaries"
            if contract_class.endswith("_TUPLE")
            else None
        ),
        f"{contract_type.__name__}.properties.{field_name}",
    )
    for contract_class, by_type in _STRING_CONTRACT_GROUPS
    for contract_type, field_names in by_type.items()
    for field_name in field_names
)

_EXPECTED_EVALUATION_TIME_SOURCES = (
    "INJECTED_CURRENT_DECISION_TIME",
    "RECORDED_HISTORICAL_AS_OF_TIME",
    "RECORDED_AUDIT_REPLAY_TIME",
    "INJECTED_ANALYSIS_TIME",
)
_EXPECTED_LEGACY_SOURCE_VERSIONS = {
    "LOCAL_DRS_DICT": "legacy_local_drs_dict_v0",
    "DRS_RECORD_SCHEMA_V0": "drs_record_schema_v0",
    "SEMANTIC_DRS_RECORD_INPUT": "semantic_drs_record_input_v0",
    "DRS_RECORD_V02": "drs_record_v02",
    "DRS_FRESHNESS_ENVELOPE_V02": "drs_freshness_envelope_v02",
    "TEMPORAL_QUERY_V02": "temporal_query_v02",
}
_EXPECTED_LEGACY_SYNTHESIZED = (
    "target_semantic_address_id",
    "projection_profile_version",
)
_EXPECTED_LEGACY_RESTRICTIONS = (
    "answer_shortcut_forbidden_in_g2b1",
    "root_review_required",
    "legacy_object_not_canonical",
)
_LEXICAL_SECRET_NEGATIVE_VALUES = (
    "api_key:rawsecret",
    "api_key=rawsecret",
    "api-key:rawsecret",
    "api-key=rawsecret",
    "apikey:rawsecret",
    "apikey=rawsecret",
    "x-api-key:rawsecret",
    "x-api-key=rawsecret",
    "password:rawsecret",
    "password=rawsecret",
    "passwd:rawsecret",
    "passwd=rawsecret",
    "secret:rawsecret",
    "secret=rawsecret",
    "token:rawsecret",
    "token=rawsecret",
    "client_secret:rawsecret",
    "client_secret=rawsecret",
    "client-secret:rawsecret",
    "client-secret=rawsecret",
    "access_token:rawsecret",
    "access_token=rawsecret",
    "access-token:rawsecret",
    "access-token=rawsecret",
    "refresh_token:rawsecret",
    "refresh_token=rawsecret",
    "refresh-token:rawsecret",
    "refresh-token=rawsecret",
    "authentication_secret:rawsecret",
    "authentication_secret=rawsecret",
    "authentication-secret:rawsecret",
    "authentication-secret=rawsecret",
    "bank_account:1234567890",
    "bank_account=1234567890",
    "bank-account:1234567890",
    "bank-account=1234567890",
    "iban:de89abcd1234efgh5678ijkl90",
    "iban=de89abcd1234efgh5678ijkl90",
    "cvv:123",
    "cvv=123",
    "de89abcd1234efgh5678ijkl90",
    "DE89 ABCD 1234 EFGH 5678 IJKL 90",
    "4111111111111111",
    "4111 1111 1111 1111",
    "4111-1111-1111-1111",
    "4111-1111 1111-1111",
    "passport: AB123456",
    "passport_AB123456",
    "Bearer raw-auth-material",
    "Basic dXNlcjpwYXNzd29yZA==",
    "Authorization:raw-auth-material",
)
_LEXICAL_POSITIVE_TOKEN_VALUES = (
    "passport_policy",
    "password_policy",
    "token_status",
    "authentication_mode",
    "api_key_policy",
    "bank_account_policy",
)
_LEXICAL_POSITIVE_REFERENCE_VALUES = (
    "policy:passport_requirements",
    "audit:token_policy_review",
    "policy:password_rotation",
    "scope:authentication_mode",
)
_SECRETSAFE_BOUNDARY_POSITIVE_VALUES = (
    "mytoken:public-label",
    "notpassword:rotation",
    "xapi_key:policy",
    "unbearer abc",
    "notBasic abc",
    "preAuthorization:status",
    "AB12AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA B",
    "1111111111111111111 2",
)
_SECRETSAFE_UNICODE_WHITESPACE_VALUES = (
    "Bearer \u00a0",
    "Basic \u2003",
    "Authorization:\u202f",
)
_SECRETSAFE_KEY_VALUE_MARKERS = (
    "api_key",
    "api-key",
    "apikey",
    "x-api-key",
    "password",
    "passwd",
    "secret",
    "token",
    "access_token",
    "access-token",
    "refresh_token",
    "refresh-token",
    "client_secret",
    "client-secret",
    "authentication_secret",
    "authentication-secret",
    "bank_account",
    "bank-account",
    "iban",
    "cvv",
)
_SECRETSAFE_LEFT_BOUNDARY_PREFIXES = ("", " ", ".", "_", "-")
_SECRETSAFE_EMBEDDED_PREFIXES = ("x", "A", "1")
_SECRETSAFE_AUTHENTICATION_MARKERS = (
    "Bearer",
    "Basic",
    "Authorization",
)
_SECRETSAFE_EMBEDDED_ALIAS_REJECTED_MARKERS = (
    "x-api-key",
    "access_token",
    "access-token",
    "refresh_token",
    "refresh-token",
    "client_secret",
    "client-secret",
    "authentication_secret",
    "authentication-secret",
)
_EXPECTED_SECRETSAFE_KEY_VALUE_PATTERN = (
    "(^|[^A-Za-z0-9])(?:"
    "[Aa][Pp][Ii]_[Kk][Ee][Yy]|"
    "[Aa][Pp][Ii]-[Kk][Ee][Yy]|"
    "[Aa][Pp][Ii][Kk][Ee][Yy]|"
    "[Xx]-[Aa][Pp][Ii]-[Kk][Ee][Yy]|"
    "[Pp][Aa][Ss][Ss][Ww][Oo][Rr][Dd]|"
    "[Pp][Aa][Ss][Ss][Ww][Dd]|"
    "[Ss][Ee][Cc][Rr][Ee][Tt]|"
    "[Tt][Oo][Kk][Ee][Nn]|"
    "[Aa][Cc][Cc][Ee][Ss][Ss]_[Tt][Oo][Kk][Ee][Nn]|"
    "[Aa][Cc][Cc][Ee][Ss][Ss]-[Tt][Oo][Kk][Ee][Nn]|"
    "[Rr][Ee][Ff][Rr][Ee][Ss][Hh]_[Tt][Oo][Kk][Ee][Nn]|"
    "[Rr][Ee][Ff][Rr][Ee][Ss][Hh]-[Tt][Oo][Kk][Ee][Nn]|"
    "[Cc][Ll][Ii][Ee][Nn][Tt]_[Ss][Ee][Cc][Rr][Ee][Tt]|"
    "[Cc][Ll][Ii][Ee][Nn][Tt]-[Ss][Ee][Cc][Rr][Ee][Tt]|"
    "[Aa][Uu][Tt][Hh][Ee][Nn][Tt][Ii][Cc][Aa][Tt][Ii][Oo][Nn]"
    "_[Ss][Ee][Cc][Rr][Ee][Tt]|"
    "[Aa][Uu][Tt][Hh][Ee][Nn][Tt][Ii][Cc][Aa][Tt][Ii][Oo][Nn]"
    "-[Ss][Ee][Cc][Rr][Ee][Tt]|"
    "[Bb][Aa][Nn][Kk]_[Aa][Cc][Cc][Oo][Uu][Nn][Tt]|"
    "[Bb][Aa][Nn][Kk]-[Aa][Cc][Cc][Oo][Uu][Nn][Tt]|"
    "[Ii][Bb][Aa][Nn]|"
    "[Cc][Vv][Vv]"
    ")[=:]"
)
_EXPECTED_SECRETSAFE_AUTHENTICATION_PATTERNS = (
    (
        "(^|[^A-Za-z0-9])"
        "(?:[Bb][Ee][Aa][Rr][Ee][Rr]|[Bb][Aa][Ss][Ii][Cc])"
        "[ \\t]+\\S"
    ),
    (
        "(^|[^A-Za-z0-9])"
        "[Aa][Uu][Tt][Hh][Oo][Rr][Ii][Zz][Aa][Tt][Ii][Oo][Nn]:"
        "[ \\t]*\\S"
    ),
)
_EXPECTED_SECRETSAFE_CARD_PATTERN = (
    "(?:^|[^0-9 -]|(?:^|[^0-9])[ -])"
    "[0-9](?:[ -]?[0-9]){12,18}(?![ -]?[0-9])"
)
_EXPECTED_SECRETSAFE_IBAN_PATTERN = (
    "(^|[^A-Za-z0-9])"
    "[A-Za-z][ ]?[A-Za-z][ ]?[0-9][ ]?[0-9]"
    "(?:[ ]?[A-Za-z0-9]){11,30}(?![ ]?[A-Za-z0-9])"
)
_RESERVED_REFERENCE_PROFILES = (
    (
        "sealed_secret",
        "sealed-secret-ref:",
        238,
        "vault-entry-42",
        "password=not-allowed",
    ),
    (
        "audit",
        "audit-ref:",
        246,
        "audit-entry-42",
        "Bearer secret-token",
    ),
    (
        "scope",
        "scope-ref:",
        246,
        "local-scope-42",
        "iban=raw-account",
    ),
)
_RESERVED_REFERENCE_INVALID_INITIALS = (".", "-", "_", "/", "#", ":")
_EXPECTED_RESERVED_REFERENCE_CONDITIONALS = (
    (
        "^sealed-secret-ref:",
        (
            "^sealed-secret-ref:"
            "[A-Za-z0-9][A-Za-z0-9._:/#-]{0,237}$"
        ),
        "#/$defs/noLineTerminator",
    ),
    (
        "^audit-ref:",
        "^audit-ref:[A-Za-z0-9][A-Za-z0-9._:/#-]{0,245}$",
        "#/$defs/noLineTerminator",
    ),
    (
        "^scope-ref:",
        "^scope-ref:[A-Za-z0-9][A-Za-z0-9._:/#-]{0,245}$",
        "#/$defs/noLineTerminator",
    ),
)


class _StringSubclass(str):
    pass


class _TupleSubclass(tuple):
    pass


class _EqualitySubstitute:
    def __eq__(self, other: object) -> bool:
        return True


def _legacy_sources() -> dict[str, object]:
    schema_record = {
        "record_id": "legacy:local:travel_policy",
        "layer": "work",
        "type": "generic",
        "domain": "travel_policy_information",
        "content": {"summary": "Current bounded travel policy context."},
        "time_envelope": {
            "pt_created_at": "2026-07-29T08:00:00Z",
            "kt_asof": "2026-07-29T08:00:00Z",
            "et_observed_at": "2026-07-29T08:00:00Z",
            "ct_session_anchor": "travel_policy",
            "ttl_seconds": 3600,
            "freshness_class": "normal",
            "valid_from": "2026-07-29T08:00:00Z",
            "valid_to": "2026-07-29T09:00:00Z",
        },
        "provenance": {
            "request_id": "request:legacy:travel_policy",
            "created_by": "root_orchestrator",
            "trace_refs": [],
        },
        "status": "active",
    }
    freshness = DRSFreshnessEnvelope(
        physical_time="2026-07-29T08:00:00Z",
        knowledge_time="2026-07-29T08:00:00Z",
        event_time="2026-07-29T08:00:00Z",
        context_time="travel_policy",
        ttl_seconds=3600,
        validity_start="2026-07-29T08:00:00Z",
        validity_end="2026-07-29T09:00:00Z",
        source_observed_at="2026-07-29T08:00:00Z",
        system_ingested_at="2026-07-29T08:00:01Z",
    )
    return {
        "LOCAL_DRS_DICT": json.loads(json.dumps(schema_record)),
        "DRS_RECORD_SCHEMA_V0": json.loads(json.dumps(schema_record)),
        "SEMANTIC_DRS_RECORD_INPUT": SemanticDRSRecordInput(
            record_id="legacy:semantic:travel_policy",
            domain="travel_policy_information",
            content={"summary": "Bounded semantic input context."},
            semantic_keys=("travel", "policy"),
            time_envelope={"as_of": "2026-07-29T08:00:00Z"},
            provenance={"created_by": "root_orchestrator"},
        ),
        "DRS_RECORD_V02": DRSRecordV02(
            record_id="legacy:v02:travel_policy",
            record_kind="accepted_evidence_context",
            summary="Prior bounded travel policy context.",
            time_envelope=freshness,
            source_refs=("source:travel_policy",),
            provenance_refs=("audit:travel_policy",),
        ),
        "DRS_FRESHNESS_ENVELOPE_V02": freshness,
        "TEMPORAL_QUERY_V02": TemporalQueryV02(
            query_id="legacy-query:travel_policy",
            as_of="2026-07-29T08:10:00Z",
            context_time="travel_policy",
            require_root_review=True,
            allow_direct_reuse_if_all_gates_pass=True,
        ),
    }


def _fixture_family() -> dict[type, object]:
    address = semantic.build_semantic_address_v01(
        namespace="local_reference",
        domain="travel_policy_information",
        subject_class="travel_policy",
        intent_class="informational_summary",
        meaning_schema_id="drs_meaning_record",
        meaning_schema_version="v0.1",
    )
    memory_pointer = semantic.build_memory_pointer_v01(
        storage_class="LOCAL_MEANING_RECORD",
        object_reference="meaning:travel_policy:current",
        content_sha256=_SHA_A,
        record_class="MeaningRecordV01",
        byte_length=512,
        access_policy_id="policy:summary_read",
        sensitivity_class="INTERNAL",
        allowed_use_classes=("CONTEXT_ONLY", "ANSWER_SHORTCUT"),
        forbidden_use_classes=("ACTION",),
        summary_read_permitted=True,
        payload_read_permitted=False,
    )
    artifact_pointer = semantic.build_artifact_pointer_v01(
        storage_class="LOCAL_DOCUMENT",
        object_reference="document:travel_policy:current",
        content_sha256=_SHA_B,
        media_type="application/json",
        byte_length=1024,
        access_policy_id="policy:bounded_document",
        sensitivity_class="INTERNAL",
        allowed_use_classes=("CONTEXT_ONLY",),
        forbidden_use_classes=("ACTION",),
        summary_read_permitted=True,
        payload_read_permitted=False,
    )
    lineage_edge = semantic.build_lineage_edge_v01(
        source_meaning_record_id="drsmeaning_v01:" + "1" * 64,
        target_meaning_record_id="drsmeaning_v01:" + "2" * 64,
        relation_class="DERIVED_FROM",
        claim_dimension="travel_policy_summary",
        source_history_hash=_SHA_C,
        evidence_ref_ids=("evidence:travel_policy",),
        created_at=100,
        recording_component="g2b1_fixture",
    )
    authority = semantic.build_drs_authority_envelope_v01(
        authority_class="UNTRUSTED_SEMANTIC_DRAFT",
        owning_local_root_id=None,
        source_root_decision_input_id=None,
        source_root_decision_id=None,
        source_root_decision_hash=None,
        authority_scope_fingerprint=_SHA_D,
        root_acceptance_state="UNREVIEWED",
        recording_component="g2b1_fixture",
    )
    time_envelope = semantic.build_drs_time_envelope_v01(
        pt_created_at=100,
        kt_as_of=101,
        et_observed_at=99,
        ct_context_anchor=100,
        ttl_seconds=1000,
        valid_from=50,
        valid_to=1000,
        source_observed_at=99,
        source_reported_at=100,
        system_ingested_at=101,
        system_verified_at=102,
        freshness_policy_id="freshness:reference_v01",
    )
    record = semantic.build_meaning_record_v01(
        semantic_address=address,
        predecessor_record_id=None,
        supersession_reason=None,
        safe_summary="Current bounded travel policy summary.",
        semantic_tags=("travel", "policy", "informational"),
        resonance_reason="Exact local meaning-family match.",
        memory_pointers=(memory_pointer,),
        artifact_pointers=(artifact_pointer,),
        source_reference_ids=("source:travel_policy",),
        lineage_edges=(),
        time_envelope=time_envelope,
        authority_envelope=authority,
        persistent_lifecycle_state="ACTIVE",
        risk_hints=("LOW_RISK_INFORMATIONAL",),
        conflict_hints=(),
        reuse_policy_class="CONTEXT_ONLY",
        policy_version="policy_v01",
        schema_versions=("v0.1",),
        content_fingerprint=_SHA_E,
        recording_component="g2b1_fixture",
    )
    query = resolution.build_drs_temporal_query_v01(
        query_mode="DIRECT_REUSE_CANDIDATE",
        semantic_address_id=address.semantic_address_id,
        scope_fingerprint=_SHA_D,
        as_of=200,
        evaluation_time=200,
        evaluation_time_source="INJECTED_CURRENT_DECISION_TIME",
        time_range_start=100,
        time_range_end=300,
        required_time_axes=("PT", "KT", "ET", "CT", "TTL", "VALIDITY"),
        freshness_policy_id="freshness:reference_v01",
        max_age_seconds=1000,
        domain="travel_policy_information",
        risk_class="LOW",
        reuse_intent="INFORMATIONAL_SHORTCUT_CONSIDERATION",
        requested_reuse_classes=("ANSWER_SHORTCUT",),
        required_evidence_classes=("ROOT_ACCEPTED_CONTEXT",),
        forbidden_changes=("POLICY_CHANGED",),
        policy_version="policy_v01",
        schema_versions=("v0.1",),
        owning_local_root_id="root:local_reference",
    )
    evaluation = resolution.build_query_evaluation_state_v01(
        query_id=query.query_id,
        semantic_address_id=address.semantic_address_id,
        meaning_record_id=record.meaning_record_id,
        query_state="FRESH_CANDIDATE",
        evaluated_at=200,
        evaluation_time_source="INJECTED_CURRENT_DECISION_TIME",
        temporal_hard_gate_passed=True,
        validity_interval_passed=True,
        ttl_freshness_passed=True,
        required_time_axes_passed=True,
        scope_passed=True,
        lifecycle_passed=True,
        policy_compatible=True,
        schema_compatible=True,
        provenance_passed=True,
        authority_envelope_passed=True,
        required_evidence_passed=True,
        forbidden_changes_passed=True,
        conflict_passed=True,
        quarantine_passed=True,
        deadend_passed=True,
        action_intent_passed=True,
        g2a_action_history_passed=True,
        permission_boundary_passed=True,
        current_freshness_units=9000,
        observed_evidence_fingerprint=_SHA_A,
        checked_dependency_fingerprint=_SHA_B,
        source_history_hash=_SHA_C,
        action_history_binding_id=None,
        eligible_for_ranking=True,
        reason_codes=(),
    )
    candidate = resolution.build_resolution_candidate_v01(
        query_id=query.query_id,
        semantic_address_id=address.semantic_address_id,
        meaning_record_id=record.meaning_record_id,
        query_evaluation_id=evaluation.query_evaluation_id,
        safe_summary=record.safe_summary,
        evidence_ref_ids=("evidence:travel_policy",),
        source_history_hash=_SHA_C,
        action_history_binding_id=None,
        semantic_similarity_units=9000,
        freshness_units=8000,
        source_authority_prior_units=2000,
        lineage_proximity_units=1000,
        historical_utility_units=5000,
        gt_advisory_prior_units=1000,
        conflict_penalty_units=0,
        risk_penalty_units=0,
        retrieval_cost_units=100,
    )
    budget = resolution.build_memory_descent_budget_v01(
        max_depth=1,
        max_records_opened=2,
        max_pointers_opened=2,
        max_artifacts_opened=1,
        max_bytes_opened=4096,
        max_lineage_edges=2,
        max_conflict_records=1,
    )
    plan = resolution.build_retrieval_plan_v01(
        query_id=query.query_id,
        semantic_address_id=address.semantic_address_id,
        proposed_record_ids=(record.meaning_record_id,),
        proposed_memory_pointer_ids=(memory_pointer.pointer_id,),
        proposed_artifact_pointer_ids=(artifact_pointer.pointer_id,),
        requested_descent_class="OPEN_ONE_ARTIFACT",
        proposed_budget_id=budget.memory_descent_budget_id,
        required_access_policy_ids=(
            memory_pointer.access_policy_id,
            artifact_pointer.access_policy_id,
        ),
        reason_codes=("bounded_local_read_proposal",),
    )
    descent_request = resolution.build_memory_descent_request_v01(
        retrieval_plan_id=plan.retrieval_plan_id,
        query_id=query.query_id,
        owning_local_root_id="root:local_reference",
        root_kernel_id="root_decision_kernel_v01",
        root_decision_input_id="root-input:g2b1:descent",
        root_decision_id="root-decision:g2b1:descent",
        root_decision_hash=_SHA_D,
        requested_descent_class="OPEN_ONE_ARTIFACT",
        approved_descent_class="OPEN_ONE_ARTIFACT",
        proposed_budget_id=budget.memory_descent_budget_id,
        approved_budget=budget,
        approved_record_ids=(record.meaning_record_id,),
        approved_memory_pointer_ids=(memory_pointer.pointer_id,),
        approved_artifact_pointer_ids=(artifact_pointer.pointer_id,),
    )
    descent_result = resolution.build_memory_descent_result_v01(
        memory_descent_request_id=descent_request.memory_descent_request_id,
        retrieval_plan_id=plan.retrieval_plan_id,
        query_id=query.query_id,
        executed_descent_class="OPEN_ONE_ARTIFACT",
        applied_budget_id=budget.memory_descent_budget_id,
        opened_record_ids=(record.meaning_record_id,),
        opened_memory_pointer_ids=(memory_pointer.pointer_id,),
        opened_artifact_pointer_ids=(artifact_pointer.pointer_id,),
        traversed_lineage_edge_ids=(lineage_edge.lineage_edge_id,),
        opened_conflict_record_ids=(),
        depth_reached=1,
        bytes_opened=1024,
        safe_summaries=(record.safe_summary,),
        opened_payload_fingerprints=(_SHA_B,),
    )
    root_projection = reuse.build_root_shortcut_authorization_projection_v01(
        owning_local_root_id="root:local_reference",
        root_kernel_id="root_decision_kernel_v01",
        root_decision_input_id="root-input:g2b1:shortcut",
        root_decision_id="root-decision:g2b1:shortcut",
        root_decision_hash=_SHA_D,
        selected_candidate_id=candidate.resolution_candidate_id,
        semantic_address_id=address.semantic_address_id,
        meaning_record_id=record.meaning_record_id,
        query_id=query.query_id,
        query_evaluation_id=evaluation.query_evaluation_id,
        allowed_reuse_class="ANSWER_SHORTCUT",
        scope_fingerprint=query.scope_fingerprint,
        policy_version=query.policy_version,
        schema_versions=query.schema_versions,
        valid_from=150,
        valid_to=250,
        root_shortcut_policy_ref="root-shortcut-policy:v01",
    )
    certificate = reuse.build_reuse_certificate_v01(
        semantic_address_id=address.semantic_address_id,
        meaning_record_id=record.meaning_record_id,
        query_id=query.query_id,
        query_evaluation_id=evaluation.query_evaluation_id,
        resolution_candidate_id=candidate.resolution_candidate_id,
        root_shortcut_authorization_projection=root_projection,
        case_type="NON_ACTION_INFORMATIONAL",
        required_evidence_classes=query.required_evidence_classes,
        observed_evidence_fingerprint=evaluation.observed_evidence_fingerprint,
        forbidden_changes=query.forbidden_changes,
        checked_dependency_fingerprint=evaluation.checked_dependency_fingerprint,
        valid_from=root_projection.valid_from,
        valid_to=root_projection.valid_to,
        reuse_class="ANSWER_SHORTCUT",
        source_history_hash=evaluation.source_history_hash,
        action_history_binding_id=None,
        issued_at=190,
        evaluated_at=200,
    )
    action_history = reuse.build_g2a_action_history_binding_v01(
        packet_id="acp_v02:historical_packet",
        registry_id="acp_v02:local_registry",
        transition_history_sha256=_SHA_A,
        disposition_history_sha256=_SHA_B,
        lifecycle_state="BLOCKED",
        disposition="RESERVED",
        reservation_owner_packet_id="acp_v02:historical_packet",
        terminal_receipt_ref=None,
        current_status_validation_id="action-history-validation:g2b1",
        current_status_evaluated_at=200,
        current_status_evaluation_time_source="INJECTED_CURRENT_DECISION_TIME",
        reason_codes=("action_history_shortcut_forbidden",),
    )
    projection = compatibility.project_legacy_drs_source_v01(
        source_family="DRS_RECORD_V02",
        source=_legacy_sources()["DRS_RECORD_V02"],
        target_semantic_address=address,
        target_meaning_record=record,
    )
    report = resolution.build_drs_resolution_report_v01(
        semantic_address=address,
        query=query,
        source_projections=(projection,),
        source_records=(record,),
        query_evaluations=(evaluation,),
        eligible_candidates=(candidate,),
        ranked_candidate_ids=(candidate.resolution_candidate_id,),
        selected_candidate_id=candidate.resolution_candidate_id,
        retrieval_plan=plan,
        memory_descent_result=descent_result,
        root_shortcut_projection=root_projection,
        reuse_certificate=certificate,
        context_only_record_ids=(),
        historical_only_record_ids=(),
        warning_only_record_ids=(),
        rerun_required_record_ids=(),
        blocked_record_ids=(),
        provider_calls=0,
        network_calls=0,
        gemini_calls=0,
        external_drs_calls=0,
        connector_calls=0,
        real_world_effects_count=0,
        final_status="PASS",
        reason_codes=(),
    )
    return {
        semantic.SemanticAddressV01: address,
        semantic.MemoryPointerV01: memory_pointer,
        semantic.ArtifactPointerV01: artifact_pointer,
        semantic.LineageEdgeV01: lineage_edge,
        semantic.DRSAuthorityEnvelopeV01: authority,
        semantic.DRSTimeEnvelopeV01: time_envelope,
        semantic.MeaningRecordV01: record,
        resolution.DRSTemporalQueryV01: query,
        resolution.QueryEvaluationStateV01: evaluation,
        resolution.ResolutionCandidateV01: candidate,
        resolution.RetrievalPlanV01: plan,
        resolution.MemoryDescentBudgetV01: budget,
        resolution.MemoryDescentRequestV01: descent_request,
        resolution.MemoryDescentResultV01: descent_result,
        reuse.RootShortcutAuthorizationProjectionV01: root_projection,
        reuse.ReuseCertificateV01: certificate,
        resolution.DRSResolutionReportV01: report,
        compatibility.LegacyDRSProjectionV01: projection,
        reuse.G2AActionHistoryBindingV01: action_history,
    }


def _identity_vectors(family: dict[type, object]) -> dict[str, str]:
    return {
        contract_type.__name__: getattr(
            value,
            _IDENTITY_FIELDS[contract_type],
        )
        for contract_type, value in family.items()
    }


def _schemas() -> dict[str, dict[str, object]]:
    root = Path(__file__).resolve().parents[1] / "schemas"
    return {
        path.name: json.loads(path.read_text(encoding="utf-8"))
        for path in (
            root / "drs_semantic_address_v01.schema.json",
            root / "drs_meaning_record_v01.schema.json",
            root / "drs_memory_resolution_v01.schema.json",
            root / "reuse_certificate_v01.schema.json",
        )
    }


def _schema_registry(
    schemas: dict[str, dict[str, object]],
) -> Registry:
    resources = [
        (schema["$id"], Resource.from_contents(schema))
        for schema in schemas.values()
    ]
    return Registry().with_resources(resources)


def _identity_material(contract_type: type, value: object) -> list[object]:
    identity_field = _IDENTITY_FIELDS[contract_type]
    if contract_type in {
        semantic.SemanticAddressV01,
        semantic.MemoryPointerV01,
        semantic.ArtifactPointerV01,
        semantic.LineageEdgeV01,
        semantic.DRSAuthorityEnvelopeV01,
        semantic.DRSTimeEnvelopeV01,
        semantic.MeaningRecordV01,
    }:
        projector = semantic._canonical_plain_value
    elif contract_type in {
        reuse.RootShortcutAuthorizationProjectionV01,
        reuse.ReuseCertificateV01,
        reuse.G2AActionHistoryBindingV01,
    }:
        projector = reuse._identity_value
    elif contract_type is compatibility.LegacyDRSProjectionV01:
        projector = semantic._canonical_plain_value
    else:
        projector = resolution._identity_plain
    return [
        projector(getattr(value, field_name))
        for field_name in _EXPECTED_FIELDS[contract_type]
        if field_name != identity_field
    ]


def _reidentify(value: object) -> object:
    contract_type = type(value)
    identity_field = _IDENTITY_FIELDS[contract_type]
    provisional = replace(
        value,
        **{identity_field: _PREFIXES[contract_type] + "0" * 64},
    )
    if contract_type in {
        semantic.SemanticAddressV01,
        semantic.MemoryPointerV01,
        semantic.ArtifactPointerV01,
        semantic.LineageEdgeV01,
        semantic.DRSAuthorityEnvelopeV01,
        semantic.DRSTimeEnvelopeV01,
        semantic.MeaningRecordV01,
    }:
        identity_field, domain, prefix, field_names = semantic._profile_for(
            contract_type.__name__
        )
        identity = semantic._identity(
            provisional,
            identity_field=identity_field,
            domain=domain,
            prefix=prefix,
            field_names=field_names,
        )
    elif contract_type in {
        reuse.RootShortcutAuthorizationProjectionV01,
        reuse.ReuseCertificateV01,
        reuse.G2AActionHistoryBindingV01,
    }:
        identity = reuse._identity(provisional, contract_type.__name__)
    elif contract_type is compatibility.LegacyDRSProjectionV01:
        identity = compatibility._identity(provisional)
    else:
        identity = resolution._identity(provisional, contract_type.__name__)
    return replace(provisional, **{identity_field: identity})


def _same_type_contract_mutation(
    value: object,
    *,
    field_name: str,
    contract_class: str,
) -> object:
    invalid_values = {
        "EXACT_TOKEN": "contains whitespace",
        "EXACT_REFERENCE": "reference with whitespace",
        "EXACT_SAFE_TEXT": "password=not-allowed",
        "EXACT_MEDIA_TYPE": "application json",
        "EXACT_SHA256": "A" * 64,
        "EXACT_TYPED_G2B_CANONICAL_ID": "wrong_v01:" + "a" * 64,
        "EXACT_ENUM": "NOT_A_FROZEN_VALUE",
        "TOKEN_TUPLE": ("contains whitespace",),
        "REFERENCE_TUPLE": ("reference with whitespace",),
        "SAFE_TEXT_TUPLE": ("password=not-allowed",),
        "SHA256_TUPLE": ("A" * 64,),
        "TYPED_ID_TUPLE": ("wrong_v01:" + "a" * 64,),
        "FIELD_NAME_TUPLE": ("Not_A_Field_Name",),
    }
    mutated = replace(value, **{field_name: invalid_values[contract_class]})
    if field_name == _IDENTITY_FIELDS[type(value)]:
        return mutated
    return _reidentify(mutated)


def _replace_and_reidentify(
    value: object,
    *,
    field_name: str,
    field_value: object,
) -> object:
    mutated = replace(value, **{field_name: field_value})
    if field_name == _IDENTITY_FIELDS[type(value)]:
        return mutated
    return _reidentify(mutated)


def _iter_schema_nodes(
    value: object,
    path: tuple[str, ...] = (),
) -> tuple[tuple[tuple[str, ...], dict[str, object]], ...]:
    observed: list[tuple[tuple[str, ...], dict[str, object]]] = []
    if type(value) is dict:
        observed.append((path, value))
        for key, nested in value.items():
            observed.extend(
                _iter_schema_nodes(nested, path + (str(key),))
            )
    elif type(value) is list:
        for index, nested in enumerate(value):
            observed.extend(
                _iter_schema_nodes(nested, path + (str(index),))
            )
    return tuple(observed)


def _lexical_schema_observations(
    schemas: dict[str, dict[str, object]],
) -> dict[str, bool]:
    observations: dict[str, bool] = {}
    registry = _schema_registry(schemas)
    direct = (
        (
            "token",
            "drs_meaning_record_v01.schema.json",
            "token",
            "abc\n",
        ),
        (
            "reference",
            "drs_meaning_record_v01.schema.json",
            "reference",
            "reference:value\n",
        ),
        (
            "media_type",
            "drs_meaning_record_v01.schema.json",
            "mediaType",
            "application/json\n",
        ),
        (
            "sha256",
            "drs_meaning_record_v01.schema.json",
            "sha256",
            _SHA_A + "\n",
        ),
        (
            "field_name",
            "drs_memory_resolution_v01.schema.json",
            "fieldName",
            "valid_field\n",
        ),
        (
            "safe_text_cr",
            "drs_meaning_record_v01.schema.json",
            "safeText1024",
            "safe\rtext",
        ),
        (
            "safe_text_del",
            "drs_meaning_record_v01.schema.json",
            "safeText1024",
            "safe\x7ftext",
        ),
    )
    for label, schema_name, definition_name, probe in direct:
        schema = schemas[schema_name]
        observations[label] = Draft202012Validator(
            {"$ref": f"{schema['$id']}#/$defs/{definition_name}"},
            registry=registry,
        ).is_valid(probe)
    typed_patterns = {}
    for schema_name, schema in schemas.items():
        for path, node in _iter_schema_nodes(schema):
            pattern = node.get("pattern")
            if (
                type(pattern) is str
                and "_v01:[0-9a-f]{64}$" in pattern
            ):
                typed_patterns[(schema_name, path)] = node
    assert typed_patterns
    for (schema_name, path), node in typed_patterns.items():
        prefix = node["pattern"].split("^", 1)[1].split("[", 1)[0]
        observations[
            "typed_id:" + schema_name + ":" + ".".join(path)
        ] = Draft202012Validator(node).is_valid(prefix + _SHA_A + "\n")
    return observations


def _boundary_values(
    *,
    contract_class: str,
    detail: object,
    item_maximum: int | None,
    tuple_maximum: int | None,
) -> tuple[tuple[str, object], ...]:
    prefix = detail if type(detail) is str else "drsmeaning_v01:"
    scalar = {
        "EXACT_TOKEN": (
            ("trailing_lf", "abc\n"),
            ("trailing_cr", "abc\r"),
            ("wrong_charset", "abc!"),
            ("over_bound", "a" * 129),
            ("secret_shape", "password:rawsecret"),
        ),
        "EXACT_REFERENCE": (
            ("trailing_lf", "reference:value\n"),
            ("trailing_cr", "reference:value\r"),
            ("wrong_charset", "reference value"),
            ("over_bound", "r" * 257),
            ("secret_shape", "password:rawsecret"),
        ),
        "EXACT_SAFE_TEXT": (
            ("trailing_cr", "safe\rtext"),
            ("del_control", "safe\x7ftext"),
            ("wrong_control", "safe\x00text"),
            ("over_bound", "x" * ((item_maximum or 0) + 1)),
            ("secret_shape", "password:rawsecret"),
        ),
        "EXACT_MEDIA_TYPE": (
            ("trailing_lf", "application/json\n"),
            ("trailing_cr", "application/json\r"),
            ("wrong_charset", "application json"),
            ("over_bound", "a/" + "b" * 127),
        ),
        "EXACT_SHA256": (
            ("trailing_lf", _SHA_A + "\n"),
            ("trailing_cr", _SHA_A + "\r"),
            ("wrong_charset", "A" * 64),
            ("over_bound", "a" * 65),
        ),
        "EXACT_TYPED_G2B_CANONICAL_ID": (
            ("trailing_lf", prefix + _SHA_A + "\n"),
            ("trailing_cr", prefix + _SHA_A + "\r"),
            ("wrong_prefix", "wrong_v01:" + _SHA_A),
            ("over_bound", prefix + "a" * 65),
        ),
        "EXACT_ENUM": (
            ("trailing_lf", detail[0] + "\n"),
            ("trailing_cr", detail[0] + "\r"),
            ("wrong_value", "NOT_A_FROZEN_VALUE"),
        ),
    }
    if contract_class in scalar:
        return scalar[contract_class]
    item_class = {
        "TOKEN_TUPLE": "EXACT_TOKEN",
        "REFERENCE_TUPLE": "EXACT_REFERENCE",
        "SAFE_TEXT_TUPLE": "EXACT_SAFE_TEXT",
        "SHA256_TUPLE": "EXACT_SHA256",
        "TYPED_ID_TUPLE": "EXACT_TYPED_G2B_CANONICAL_ID",
        "FIELD_NAME_TUPLE": "EXACT_FIELD_NAME",
    }[contract_class]
    if item_class == "EXACT_FIELD_NAME":
        item_probes = (
            ("trailing_lf", "valid_field\n"),
            ("trailing_cr", "valid_field\r"),
            ("wrong_charset", "Invalid_Field"),
            ("over_bound", "f" * 129),
        )
    else:
        item_probes = _boundary_values(
            contract_class=item_class,
            detail=detail,
            item_maximum=item_maximum,
            tuple_maximum=None,
        )
    probes = [(label, (value,)) for label, value in item_probes]
    maximum = tuple_maximum or 0
    if contract_class == "TOKEN_TUPLE":
        over = tuple(f"item_{index}" for index in range(maximum + 1))
    elif contract_class == "REFERENCE_TUPLE":
        over = tuple(
            f"reference:item_{index}" for index in range(maximum + 1)
        )
    elif contract_class == "SAFE_TEXT_TUPLE":
        over = tuple(f"safe item {index}" for index in range(maximum + 1))
    elif contract_class == "SHA256_TUPLE":
        over = tuple(f"{index:064x}" for index in range(maximum + 1))
    elif contract_class == "TYPED_ID_TUPLE":
        over = tuple(
            prefix + f"{index:064x}" for index in range(maximum + 1)
        )
    else:
        over = tuple(f"field_{index}" for index in range(maximum + 1))
    probes.append(("tuple_over_bound", over))
    return tuple(probes)


def _field_contract_boundary_failures(
    family: dict[type, object],
    schemas: dict[str, dict[str, object]],
    registry: Registry,
) -> tuple[int, tuple[object, ...]]:
    probe_count = 0
    failures: list[object] = []
    for (
        _,
        contract_type,
        field_name,
        contract_class,
        detail,
        item_maximum,
        tuple_maximum,
        _,
        _,
    ) in _STRING_FIELD_CONTRACT_MATRIX:
        for label, field_value in _boundary_values(
            contract_class=contract_class,
            detail=detail,
            item_maximum=item_maximum,
            tuple_maximum=tuple_maximum,
        ):
            probe_count += 1
            invalid = _replace_and_reidentify(
                family[contract_type],
                field_name=field_name,
                field_value=field_value,
            )
            runtime = _VALIDATORS[contract_type](invalid)
            schema_accepts = _schema_accepts(invalid, schemas, registry)
            if runtime[0] or schema_accepts:
                failures.append(
                    (
                        contract_type.__name__,
                        field_name,
                        contract_class,
                        label,
                        runtime,
                        schema_accepts,
                    )
                )
    return probe_count, tuple(failures)


def _schema_string_node_inventory(
    schemas: dict[str, dict[str, object]],
) -> tuple[dict[str, int], tuple[object, ...]]:
    counts = {
        "variable": 0,
        "safe_text": 0,
        "sha256": 0,
        "typed_id": 0,
        "enum_or_const": 0,
        "search_pattern": 0,
    }
    failures: list[object] = []
    safe_text_pattern = (
        "^[^\\u0000-\\u0008\\u000B-\\u001F\\u007F]*$"
    )
    for schema_name, schema in schemas.items():
        for path, node in _iter_schema_nodes(schema):
            pattern = node.get("pattern")
            is_enum_or_const = (
                type(node.get("const")) is str
                or (
                    type(node.get("enum")) is list
                    and node["enum"]
                    and all(type(item) is str for item in node["enum"])
                )
            )
            if is_enum_or_const:
                counts["enum_or_const"] += 1
                continue
            if type(pattern) is str and node.get("type") != "string":
                counts["search_pattern"] += 1
                if "(?i:" in pattern or "(?<=" in pattern or "(?<!" in pattern:
                    failures.append((schema_name, path, "python_regex"))
                continue
            if node.get("type") != "string":
                continue
            if type(pattern) is not str:
                failures.append((schema_name, path, "unclassified_string"))
                continue
            location = path[-1] if path else ""
            if "_v01:[0-9a-f]{64}$" in pattern or (
                "legacy_freshness_v02:[0-9a-f]{64}$" in pattern
            ):
                counts["typed_id"] += 1
                prefix = pattern.split("^", 1)[1].split("[", 1)[0]
                expected_length = len(prefix) + 64
                if (
                    node.get("minLength") != expected_length
                    or node.get("maxLength") != expected_length
                    or {
                        "$ref": "#/$defs/noLineTerminator"
                    } not in node.get("allOf", [])
                ):
                    failures.append(
                        (schema_name, path, "typed_id_closure")
                    )
            elif pattern == "^[0-9a-f]{64}$":
                counts["sha256"] += 1
                if (
                    node.get("minLength") != 64
                    or node.get("maxLength") != 64
                    or {
                        "$ref": "#/$defs/noLineTerminator"
                    } not in node.get("allOf", [])
                ):
                    failures.append((schema_name, path, "sha256_closure"))
            elif location.startswith("safeText"):
                counts["safe_text"] += 1
                if pattern != safe_text_pattern:
                    failures.append((schema_name, path, "safe_text_control"))
            elif location in {"token", "reference", "mediaType", "fieldName"}:
                counts["variable"] += 1
                if {
                    "$ref": "#/$defs/noLineTerminator"
                } not in node.get("allOf", []):
                    failures.append(
                        (schema_name, path, "variable_end_closure")
                    )
            else:
                failures.append((schema_name, path, "unclassified_string"))
            if "(?i:" in pattern or "(?<=" in pattern or "(?<!" in pattern:
                failures.append((schema_name, path, "python_regex"))
    return counts, tuple(failures)


def _schema_validator_for_type(
    contract_type: type,
    schemas: dict[str, dict[str, object]],
    registry: Registry,
) -> Draft202012Validator:
    return Draft202012Validator(
        _schema_reference_for_type(contract_type, schemas),
        registry=registry,
    )


def _schema_accepts(
    value: object,
    schemas: dict[str, dict[str, object]],
    registry: Registry,
) -> bool:
    try:
        _schema_validator_for_type(type(value), schemas, registry).validate(
            _SERIALIZERS[type(value)](value)
        )
    except ValidationError:
        return False
    return True


def _secret_safe_summary_observation(
    value: str,
    *,
    record: semantic.MeaningRecordV01,
    schemas: dict[str, dict[str, object]],
    registry: Registry,
) -> tuple[tuple[bool, tuple[str, ...]], bool]:
    candidate = _replace_and_reidentify(
        record,
        field_name="safe_summary",
        field_value=value,
    )
    return (
        semantic.validate_meaning_record_v01(candidate),
        _schema_accepts(candidate, schemas, registry),
    )


def _secret_safe_key_value_boundary_cases(
) -> tuple[tuple[str, str, bool], ...]:
    cases: list[tuple[str, str, bool]] = []
    for marker in _SECRETSAFE_KEY_VALUE_MARKERS:
        for delimiter in (":", "="):
            for prefix in _SECRETSAFE_LEFT_BOUNDARY_PREFIXES:
                cases.append(
                    (
                        f"boundary:{prefix!r}:{marker}:{delimiter}",
                        prefix + marker + delimiter + "public-label",
                        False,
                    )
                )
            for prefix in _SECRETSAFE_EMBEDDED_PREFIXES:
                cases.append(
                    (
                        f"embedded:{prefix}:{marker}:{delimiter}",
                        prefix + marker + delimiter + "public-label",
                        marker
                        not in _SECRETSAFE_EMBEDDED_ALIAS_REJECTED_MARKERS,
                    )
                )
    return tuple(cases)


def _secret_safe_authentication_boundary_cases(
) -> tuple[tuple[str, str, bool], ...]:
    cases: list[tuple[str, str, bool]] = []
    for marker in _SECRETSAFE_AUTHENTICATION_MARKERS:
        suffix = (
            ":public-label"
            if marker == "Authorization"
            else " public-label"
        )
        for prefix in _SECRETSAFE_LEFT_BOUNDARY_PREFIXES:
            cases.append(
                (
                    f"boundary:{prefix!r}:{marker}",
                    prefix + marker + suffix,
                    False,
                )
            )
        for prefix in _SECRETSAFE_EMBEDDED_PREFIXES:
            cases.append(
                (
                    f"embedded:{prefix}:{marker}",
                    prefix + marker + suffix,
                    True,
                )
            )
    return tuple(cases)


def _digit_run(count: int, separator: str) -> str:
    digits = "1" * count
    if separator == "":
        return digits
    if separator in {" ", "-"}:
        return separator.join(digits)
    return "".join(
        digit + (" " if index % 2 == 0 else "-")
        for index, digit in enumerate(digits[:-1])
    ) + digits[-1]


def _secret_safe_card_boundary_cases(
) -> tuple[tuple[str, str, bool], ...]:
    cases: list[tuple[str, str, bool]] = []
    contexts = (
        ("start", "", "", 0),
        ("non_digit", ".", "", 0),
        ("leading_digit_separator", "1 ", "", 1),
        ("trailing_digit_separator", "", " 2", 1),
    )
    for digit_count in range(12, 22):
        for separator in ("", " ", "-", "mixed"):
            run = _digit_run(digit_count, separator)
            for context, prefix, suffix, extra_digits in contexts:
                total_digits = digit_count + extra_digits
                cases.append(
                    (
                        f"{digit_count}:{separator or 'none'}:{context}",
                        prefix + run + suffix,
                        not 13 <= total_digits <= 19,
                    )
                )
    return tuple(cases)


def _iban_value(bban_length: int, spaced: bool) -> str:
    material = "AB12" + ("A" * bban_length)
    return " ".join(material) if spaced else material


def _secret_safe_iban_boundary_cases(
) -> tuple[tuple[str, str, bool], ...]:
    cases: list[tuple[str, str, bool]] = []
    for bban_length in range(9, 33):
        for spaced in (False, True):
            for context, prefix in (("start", ""), ("non_alnum", ".")):
                cases.append(
                    (
                        (
                            f"{bban_length}:"
                            f"{'spaced' if spaced else 'contiguous'}:"
                            f"{context}"
                        ),
                        prefix + _iban_value(bban_length, spaced),
                        not 11 <= bban_length <= 30,
                    )
                )
    return tuple(cases)


def _secret_safe_boundary_parity_audit(
    *,
    record: semantic.MeaningRecordV01,
    schemas: dict[str, dict[str, object]],
    registry: Registry,
) -> tuple[dict[str, int], tuple[object, ...]]:
    corpora = {
        "key_value_boundary": _secret_safe_key_value_boundary_cases(),
        "authentication_boundary": (
            _secret_safe_authentication_boundary_cases()
        ),
        "card_boundary": _secret_safe_card_boundary_cases(),
        "iban_boundary": _secret_safe_iban_boundary_cases(),
        "unicode_whitespace": tuple(
            (f"unicode:{index}", value, True)
            for index, value in enumerate(
                _SECRETSAFE_UNICODE_WHITESPACE_VALUES
            )
        ),
        "positive_boundary": tuple(
            (f"positive:{index}", value, True)
            for index, value in enumerate(
                _SECRETSAFE_BOUNDARY_POSITIVE_VALUES
            )
        ),
    }
    counts = {name: len(cases) for name, cases in corpora.items()}
    failures: list[object] = []
    for corpus_name, cases in corpora.items():
        for label, value, expected in cases:
            runtime, schema_accepts = _secret_safe_summary_observation(
                value,
                record=record,
                schemas=schemas,
                registry=registry,
            )
            runtime_accepts = runtime == (True, ())
            if (
                runtime_accepts != expected
                or schema_accepts != expected
                or runtime_accepts != schema_accepts
            ):
                failures.append(
                    (
                        corpus_name,
                        label,
                        value.encode("unicode_escape").decode("ascii"),
                        expected,
                        runtime,
                        schema_accepts,
                    )
                )
    return counts, tuple(failures)


def _secret_safe_patterns(
    schema: dict[str, object],
) -> tuple[str, ...]:
    patterns: list[str] = []
    for entry in schema["$defs"]["secretSafe"]["allOf"]:
        assert type(entry) is dict
        if "not" in entry:
            assert set(entry) == {"not"}
            assert type(entry["not"]) is dict
            assert set(entry["not"]) == {"pattern"}
            assert type(entry["not"]["pattern"]) is str
            patterns.append(entry["not"]["pattern"])
            continue
        assert set(entry) == {"if", "then"}
    return tuple(patterns)


def _secret_safe_conditionals(
    schema: dict[str, object],
) -> tuple[tuple[str, str, str], ...]:
    conditionals: list[tuple[str, str, str]] = []
    for entry in schema["$defs"]["secretSafe"]["allOf"]:
        assert type(entry) is dict
        if "not" in entry:
            assert set(entry) == {"not"}
            continue
        assert set(entry) == {"if", "then"}
        if_clause = entry["if"]
        then_clause = entry["then"]
        assert type(if_clause) is dict
        assert set(if_clause) == {"pattern"}
        assert type(if_clause["pattern"]) is str
        assert type(then_clause) is dict
        assert set(then_clause) == {"allOf"}
        assert type(then_clause["allOf"]) is list
        assert len(then_clause["allOf"]) == 2
        pattern_clause, reference_clause = then_clause["allOf"]
        assert type(pattern_clause) is dict
        assert set(pattern_clause) == {"pattern"}
        assert type(pattern_clause["pattern"]) is str
        assert type(reference_clause) is dict
        assert set(reference_clause) == {"$ref"}
        assert type(reference_clause["$ref"]) is str
        conditionals.append(
            (
                if_clause["pattern"],
                pattern_clause["pattern"],
                reference_clause["$ref"],
            )
        )
    return tuple(conditionals)


def _reserved_reference_cases(
) -> tuple[tuple[str, str, str, bool], ...]:
    cases: list[tuple[str, str, str, bool]] = []
    for (
        profile_name,
        prefix,
        maximum_suffix,
        ordinary_suffix,
        raw_secret_suffix,
    ) in _RESERVED_REFERENCE_PROFILES:
        cases.append((profile_name, "empty_suffix", prefix, False))
        for initial in _RESERVED_REFERENCE_INVALID_INITIALS:
            cases.append(
                (
                    profile_name,
                    f"invalid_initial:{initial}",
                    prefix + initial + "abc",
                    False,
                )
            )
        cases.extend(
            (
                (profile_name, "trailing_lf", prefix + "abc\n", False),
                (profile_name, "trailing_cr", prefix + "abc\r", False),
                (
                    profile_name,
                    "exact_maximum",
                    prefix + ("A" * maximum_suffix),
                    True,
                ),
                (
                    profile_name,
                    "one_above_maximum",
                    prefix + ("A" * (maximum_suffix + 1)),
                    False,
                ),
                (
                    profile_name,
                    "ordinary_suffix",
                    prefix + ordinary_suffix,
                    True,
                ),
                (
                    profile_name,
                    "punctuation_after_alnum",
                    prefix + "A._:/#-z",
                    True,
                ),
                (
                    profile_name,
                    "raw_secret_suffix",
                    prefix + raw_secret_suffix,
                    False,
                ),
                (
                    profile_name,
                    "embedded_prefix",
                    "x" + prefix,
                    True,
                ),
            )
        )
    return tuple(cases)


def _reserved_reference_transports(
    value: str,
    family: dict[type, object],
) -> tuple[tuple[str, object, object], ...]:
    record = family[semantic.MeaningRecordV01]
    return (
        (
            "token",
            _replace_and_reidentify(
                family[semantic.SemanticAddressV01],
                field_name="namespace",
                field_value=value,
            ),
            semantic.validate_semantic_address_v01,
        ),
        (
            "reference",
            _replace_and_reidentify(
                family[semantic.MemoryPointerV01],
                field_name="object_reference",
                field_value=value,
            ),
            semantic.validate_memory_pointer_v01,
        ),
        (
            "reference_tuple",
            _replace_and_reidentify(
                record,
                field_name="source_reference_ids",
                field_value=(value,),
            ),
            semantic.validate_meaning_record_v01,
        ),
        (
            "safe_text_256",
            _replace_and_reidentify(
                record,
                field_name="risk_hints",
                field_value=(value,),
            ),
            semantic.validate_meaning_record_v01,
        ),
        (
            "safe_text_512",
            _replace_and_reidentify(
                record,
                field_name="resonance_reason",
                field_value=value,
            ),
            semantic.validate_meaning_record_v01,
        ),
        (
            "safe_text_1024",
            _replace_and_reidentify(
                record,
                field_name="safe_summary",
                field_value=value,
            ),
            semantic.validate_meaning_record_v01,
        ),
    )


def _secret_safe_definition_accepts(
    value: str,
    *,
    schema: dict[str, object],
    registry: Registry,
) -> bool:
    return Draft202012Validator(
        {"$ref": schema["$id"] + "#/$defs/secretSafe"},
        registry=registry,
    ).is_valid(value)


def _reserved_reference_differential_audit(
    *,
    family: dict[type, object],
    schemas: dict[str, dict[str, object]],
    registry: Registry,
) -> tuple[dict[str, int], tuple[object, ...]]:
    cases = _reserved_reference_cases()
    counts = {
        "logical_cases": len(cases),
        "direct_secret_safe_cases": 0,
        "canonical_transport_cases": 0,
        "legacy_recursive_cases": 0,
        "total_cases": 0,
    }
    failures: list[object] = []
    direct_schemas = (
        (
            "semantic_address",
            schemas["drs_semantic_address_v01.schema.json"],
        ),
        (
            "meaning_record",
            schemas["drs_meaning_record_v01.schema.json"],
        ),
    )
    for profile_name, case_name, value, expected in cases:
        runtime_direct = semantic._secret_reason(value) is None
        for schema_name, schema in direct_schemas:
            schema_direct = _secret_safe_definition_accepts(
                value,
                schema=schema,
                registry=registry,
            )
            counts["direct_secret_safe_cases"] += 1
            if (
                runtime_direct != expected
                or schema_direct != expected
                or runtime_direct != schema_direct
            ):
                failures.append(
                    (
                        profile_name,
                        case_name,
                        f"direct:{schema_name}",
                        expected,
                        runtime_direct,
                        schema_direct,
                    )
                )
        for transport_name, candidate, validator in (
            _reserved_reference_transports(value, family)
        ):
            runtime = validator(candidate)
            runtime_accepts = runtime == (True, ())
            schema_accepts = _schema_accepts(
                candidate,
                schemas,
                registry,
            )
            counts["canonical_transport_cases"] += 1
            expected_transport = expected
            if transport_name == "token":
                expected_transport = (
                    expected
                    and len(value) <= 128
                    and semantic._TOKEN.fullmatch(value) is not None
                )
            if (
                runtime_accepts != expected_transport
                or schema_accepts != expected_transport
                or runtime_accepts != schema_accepts
            ):
                failures.append(
                    (
                        profile_name,
                        case_name,
                        transport_name,
                        expected_transport,
                        runtime,
                        schema_accepts,
                    )
                )
            if (
                transport_name == "reference"
                and not expected
                and runtime
                != (False, ("drs_secret_payload_forbidden",))
            ):
                failures.append(
                    (
                        profile_name,
                        case_name,
                        "reference_reason",
                        (False, ("drs_secret_payload_forbidden",)),
                        runtime,
                    )
                )
        legacy_source = _legacy_sources()["LOCAL_DRS_DICT"]
        legacy_source["content"]["summary"] = value
        try:
            compatibility.project_legacy_drs_source_v01(
                source_family="LOCAL_DRS_DICT",
                source=legacy_source,
                target_semantic_address=family[
                    semantic.SemanticAddressV01
                ],
            )
        except ValueError as error:
            legacy_accepts = False
            legacy_reason = str(error)
        else:
            legacy_accepts = True
            legacy_reason = None
        counts["legacy_recursive_cases"] += 1
        if (
            legacy_accepts != expected
            or (
                not expected
                and legacy_reason != "drs_secret_payload_forbidden"
            )
        ):
            failures.append(
                (
                    profile_name,
                    case_name,
                    "legacy_recursive",
                    expected,
                    legacy_accepts,
                    legacy_reason,
                )
            )
    counts["total_cases"] = (
        counts["direct_secret_safe_cases"]
        + counts["canonical_transport_cases"]
        + counts["legacy_recursive_cases"]
    )
    return counts, tuple(failures)


def _schema_reference_for_type(
    contract_type: type,
    schemas: dict[str, dict[str, object]],
) -> dict[str, object]:
    if contract_type is semantic.SemanticAddressV01:
        return {"$ref": schemas["drs_semantic_address_v01.schema.json"]["$id"]}
    if contract_type in {
        semantic.MemoryPointerV01,
        semantic.ArtifactPointerV01,
        semantic.LineageEdgeV01,
        semantic.DRSAuthorityEnvelopeV01,
        semantic.DRSTimeEnvelopeV01,
        semantic.MeaningRecordV01,
    }:
        schema = schemas["drs_meaning_record_v01.schema.json"]
    elif contract_type in {
        reuse.RootShortcutAuthorizationProjectionV01,
        reuse.ReuseCertificateV01,
        reuse.G2AActionHistoryBindingV01,
    }:
        schema = schemas["reuse_certificate_v01.schema.json"]
    else:
        schema = schemas["drs_memory_resolution_v01.schema.json"]
    return {"$ref": f"{schema['$id']}#/$defs/{contract_type.__name__}"}


def _schema_definition_for_type(
    contract_type: type,
    schemas: dict[str, dict[str, object]],
) -> dict[str, object]:
    if contract_type is semantic.SemanticAddressV01:
        return schemas["drs_semantic_address_v01.schema.json"]
    if contract_type in {
        semantic.MemoryPointerV01,
        semantic.ArtifactPointerV01,
        semantic.LineageEdgeV01,
        semantic.DRSAuthorityEnvelopeV01,
        semantic.DRSTimeEnvelopeV01,
        semantic.MeaningRecordV01,
    }:
        schema = schemas["drs_meaning_record_v01.schema.json"]
    elif contract_type in {
        reuse.RootShortcutAuthorizationProjectionV01,
        reuse.ReuseCertificateV01,
        reuse.G2AActionHistoryBindingV01,
    }:
        schema = schemas["reuse_certificate_v01.schema.json"]
    else:
        schema = schemas["drs_memory_resolution_v01.schema.json"]
    return schema["$defs"][contract_type.__name__]


def _wrong_json_type(value: object) -> object:
    if type(value) is str:
        return []
    if type(value) is bool:
        return 0
    if type(value) is int:
        return True
    if type(value) is list:
        return {}
    if type(value) is dict:
        return []
    if value is None:
        return []
    raise AssertionError(type(value).__name__)


def _wrong_runtime_type(value: object) -> object:
    if type(value) is str:
        return []
    if type(value) is bool:
        return 0
    if type(value) is int:
        return True
    if type(value) is tuple:
        return []
    if value is None:
        return []
    if is_dataclass(value):
        return []
    raise AssertionError(type(value).__name__)


def test_g2b_canonical_address_identity_rebuild_is_exact() -> None:
    family = _fixture_family()
    assert len(family) == 19
    assert len(_EXPECTED_FIELDS) == 19
    expected_string_fields = {
        (contract_type, field.name)
        for contract_type in _EXPECTED_FIELDS
        for field in fields(contract_type)
        if "str" in str(field.type)
    }
    observed_string_fields = {
        (contract_type, field_name)
        for _, contract_type, field_name, *_
        in _STRING_FIELD_CONTRACT_MATRIX
    }
    assert len(_STRING_FIELD_CONTRACT_MATRIX) == 231
    assert len(observed_string_fields) == 231
    assert observed_string_fields == expected_string_fields
    assert tuple(resolution._EVALUATION_TIME_SOURCES) == (
        _EXPECTED_EVALUATION_TIME_SOURCES
    )
    assert tuple(reuse._EVALUATION_TIME_SOURCES) == (
        _EXPECTED_EVALUATION_TIME_SOURCES
    )
    assert {
        profile[0]: profile[5]
        for profile in compatibility._SOURCE_PROFILES
    } == _EXPECTED_LEGACY_SOURCE_VERSIONS
    for contract_type, value in family.items():
        assert is_dataclass(contract_type)
        assert contract_type.__dataclass_params__.frozen is True
        assert tuple(field.name for field in fields(contract_type)) == (
            _EXPECTED_FIELDS[contract_type]
        )
        valid, reasons = _VALIDATORS[contract_type](value)
        assert (valid, reasons) == (True, ())
        plain = _SERIALIZERS[contract_type](value)
        assert tuple(plain) == _EXPECTED_FIELDS[contract_type]
        identity = getattr(value, _IDENTITY_FIELDS[contract_type])
        assert identity.startswith(_PREFIXES[contract_type])
        assert len(identity) == len(_PREFIXES[contract_type]) + 64
        material = _identity_material(contract_type, value)
        payload = canonical_json_bytes_v01(material)
        digest = domain_separated_sha256_hex_v01(
            domain=_DOMAINS[contract_type],
            payload=payload,
        )
        assert identity == _PREFIXES[contract_type] + digest
        assert b"\n" not in payload
        assert not payload.startswith(_DOMAINS[contract_type].encode("ascii"))
        with pytest.raises(FrozenInstanceError):
            setattr(value, _IDENTITY_FIELDS[contract_type], identity)
    observed = _identity_vectors(family)
    assert observed == _EXPECTED_IDENTITY_VECTORS, repr(observed)


def test_g2b_dynamic_context_is_excluded_from_address_identity() -> None:
    first = semantic.build_semantic_address_v01(
        namespace="local_reference",
        domain="travel_policy_information",
        subject_class="travel_policy",
        intent_class="informational_summary",
        meaning_schema_id="drs_meaning_record",
        meaning_schema_version="v0.1",
    )
    second = semantic.build_semantic_address_v01(
        namespace="local_reference",
        domain="travel_policy_information",
        subject_class="travel_policy",
        intent_class="informational_summary",
        meaning_schema_id="drs_meaning_record",
        meaning_schema_version="v0.1",
    )
    assert first == second
    assert first.semantic_address_id == second.semantic_address_id
    assert set(semantic.semantic_address_to_plain_data_v01(first)) == {
        "address_profile_version",
        "namespace",
        "domain",
        "subject_class",
        "intent_class",
        "meaning_schema_id",
        "meaning_schema_version",
        "semantic_address_id",
    }
    with pytest.raises(
        ValueError,
        match="^drs_address_dynamic_material_forbidden$",
    ):
        semantic.build_semantic_address_v01(
            namespace="user:exact-person",
            domain="travel_policy_information",
            subject_class="travel_policy",
            intent_class="informational_summary",
            meaning_schema_id="drs_meaning_record",
            meaning_schema_version="v0.1",
        )


def test_g2b_meaning_record_identity_and_nested_exactness() -> None:
    family = _fixture_family()
    record = family[semantic.MeaningRecordV01]
    schemas = _schemas()
    registry = _schema_registry(schemas)
    assert type(record) is semantic.MeaningRecordV01
    rebuilt = semantic.build_meaning_record_v01(
        semantic_address=record.semantic_address,
        predecessor_record_id=record.predecessor_record_id,
        supersession_reason=record.supersession_reason,
        safe_summary=record.safe_summary,
        semantic_tags=record.semantic_tags,
        resonance_reason=record.resonance_reason,
        memory_pointers=record.memory_pointers,
        artifact_pointers=record.artifact_pointers,
        source_reference_ids=record.source_reference_ids,
        lineage_edges=record.lineage_edges,
        time_envelope=record.time_envelope,
        authority_envelope=record.authority_envelope,
        persistent_lifecycle_state=record.persistent_lifecycle_state,
        risk_hints=record.risk_hints,
        conflict_hints=record.conflict_hints,
        reuse_policy_class=record.reuse_policy_class,
        policy_version=record.policy_version,
        schema_versions=record.schema_versions,
        content_fingerprint=record.content_fingerprint,
        recording_component=record.recording_component,
    )
    assert rebuilt == record
    changed = replace(record, safe_summary="Different bounded summary.")
    assert semantic.validate_meaning_record_v01(changed) == (
        False,
        ("drs_meaning_record_identity_invalid",),
    )
    nested_substitute = replace(record, semantic_address=_EqualitySubstitute())
    assert semantic.validate_meaning_record_v01(nested_substitute) == (
        False,
        ("drs_exact_type_required",),
    )
    for authority_class, acceptance_state in (
        ("UNTRUSTED_SEMANTIC_DRAFT", "ACCEPTED_WORK"),
        ("CONNECTOR_OBSERVATION", "ACCEPTED_CONTEXT"),
        ("EVIDENCE_CANDIDATE", "ACCEPTED_WORK"),
    ):
        with pytest.raises(ValueError, match="^drs_root_evidence_invalid$"):
            semantic.build_drs_authority_envelope_v01(
                authority_class=authority_class,
                owning_local_root_id=None,
                source_root_decision_input_id=None,
                source_root_decision_id=None,
                source_root_decision_hash=None,
                authority_scope_fingerprint=_SHA_D,
                root_acceptance_state=acceptance_state,
                recording_component="g2b1_fixture",
            )
    with pytest.raises(ValueError, match="^drs_root_evidence_invalid$"):
        semantic.build_drs_authority_envelope_v01(
            authority_class="ROOT_ACCEPTED_WORK",
            owning_local_root_id="root:local_reference",
            source_root_decision_input_id=None,
            source_root_decision_id="root-decision:g2b1",
            source_root_decision_hash=_SHA_D,
            authority_scope_fingerprint=_SHA_D,
            root_acceptance_state="ACCEPTED_WORK",
            recording_component="g2b1_fixture",
        )
    same_type_mutations = (
        (
            "meaning_safe_summary_secret",
            _reidentify(
                replace(
                    record,
                    safe_summary="Routine note password=not-allowed",
                )
            ),
            "drs_secret_payload_forbidden",
        ),
        (
            "meaning_resonance_reason_secret",
            _reidentify(
                replace(
                    record,
                    resonance_reason="Bearer raw-auth-material",
                )
            ),
            "drs_secret_payload_forbidden",
        ),
        (
            "meaning_semantic_tag_whitespace",
            _reidentify(
                replace(record, semantic_tags=("contains whitespace",))
            ),
            "drs_text_bound_invalid",
        ),
        (
            "meaning_semantic_tags_count_33",
            _reidentify(
                replace(
                    record,
                    semantic_tags=tuple(f"tag_{index}" for index in range(33)),
                )
            ),
            "drs_tuple_bound_invalid",
        ),
    )
    observed = {}
    for label, invalid, expected_reason in same_type_mutations:
        runtime = semantic.validate_meaning_record_v01(invalid)
        schema_accepts = _schema_accepts(invalid, schemas, registry)
        observed[label] = (runtime, schema_accepts)
    assert all(
        runtime[0] is False and expected_reason in runtime[1]
        for (_, invalid, expected_reason), (runtime, _)
        in zip(same_type_mutations, observed.values(), strict=True)
    ), repr(observed)
    assert {
        label: schema_accepts
        for label, (_, schema_accepts) in observed.items()
    } == {label: False for label, _, _ in same_type_mutations}


def test_g2b_pointer_identity_rebuild_is_exact() -> None:
    family = _fixture_family()
    memory_pointer = family[semantic.MemoryPointerV01]
    artifact_pointer = family[semantic.ArtifactPointerV01]
    assert semantic.validate_memory_pointer_v01(memory_pointer) == (True, ())
    assert semantic.validate_artifact_pointer_v01(artifact_pointer) == (True, ())
    assert memory_pointer.pointer_id != artifact_pointer.pointer_id
    assert semantic.memory_pointer_to_plain_data_v01(memory_pointer)[
        "allowed_use_classes"
    ] == ["CONTEXT_ONLY", "ANSWER_SHORTCUT"]
    assert semantic.artifact_pointer_to_plain_data_v01(artifact_pointer)[
        "payload_read_permitted"
    ] is False


def test_g2b_pointer_access_policy_is_enforced() -> None:
    with pytest.raises(
        ValueError,
        match="^drs_pointer_access_policy_denied$",
    ):
        semantic.build_memory_pointer_v01(
            storage_class="LOCAL_MEANING_RECORD",
            object_reference="meaning:travel_policy:current",
            content_sha256=_SHA_A,
            record_class="MeaningRecordV01",
            byte_length=512,
            access_policy_id="policy:summary_read",
            sensitivity_class="INTERNAL",
            allowed_use_classes=("ANSWER_SHORTCUT",),
            forbidden_use_classes=("ANSWER_SHORTCUT",),
            summary_read_permitted=True,
            payload_read_permitted=False,
        )
    with pytest.raises(
        ValueError,
        match="^drs_pointer_access_policy_denied$",
    ):
        semantic.build_artifact_pointer_v01(
            storage_class="LOCAL_DOCUMENT",
            object_reference="document:travel_policy:current",
            content_sha256=_SHA_B,
            media_type="application/json",
            byte_length=1024,
            access_policy_id="policy:bounded_document",
            sensitivity_class="SECRET_REFERENCE_ONLY",
            allowed_use_classes=("CONTEXT_ONLY",),
            forbidden_use_classes=("ACTION",),
            summary_read_permitted=True,
            payload_read_permitted=True,
        )
    with pytest.raises(ValueError, match="^drs_pointer_reference_invalid$"):
        semantic.build_memory_pointer_v01(
            storage_class="LOCAL_MEANING_RECORD",
            object_reference="meaning reference with spaces",
            content_sha256=_SHA_A,
            record_class="MeaningRecordV01",
            byte_length=512,
            access_policy_id="policy:summary_read",
            sensitivity_class="INTERNAL",
            allowed_use_classes=("CONTEXT_ONLY",),
            forbidden_use_classes=("ACTION",),
            summary_read_permitted=True,
            payload_read_permitted=False,
        )
    maximum_reference = "r" * 256
    pointer = semantic.build_memory_pointer_v01(
        storage_class="LOCAL_MEANING_RECORD",
        object_reference=maximum_reference,
        content_sha256=_SHA_A,
        record_class="MeaningRecordV01",
        byte_length=512,
        access_policy_id="policy:summary_read",
        sensitivity_class="INTERNAL",
        allowed_use_classes=("CONTEXT_ONLY",),
        forbidden_use_classes=("ACTION",),
        summary_read_permitted=True,
        payload_read_permitted=False,
    )
    assert pointer.object_reference == maximum_reference
    with pytest.raises(ValueError, match="^drs_pointer_reference_invalid$"):
        semantic.build_memory_pointer_v01(
            storage_class="LOCAL_MEANING_RECORD",
            object_reference="r" * 257,
            content_sha256=_SHA_A,
            record_class="MeaningRecordV01",
            byte_length=512,
            access_policy_id="policy:summary_read",
            sensitivity_class="INTERNAL",
            allowed_use_classes=("CONTEXT_ONLY",),
            forbidden_use_classes=("ACTION",),
            summary_read_permitted=True,
            payload_read_permitted=False,
        )


def test_g2b_raw_secret_payload_is_rejected_independent_of_key_name() -> None:
    family = _fixture_family()
    record = family[semantic.MeaningRecordV01]
    address = family[semantic.SemanticAddressV01]
    schemas = _schemas()
    registry = _schema_registry(schemas)
    for safe_reference in (
        "sealed-secret-ref:vault-entry-42",
        "audit-ref:audit-entry-42",
        "scope-ref:local-scope-42",
    ):
        pointer = semantic.build_memory_pointer_v01(
            storage_class="LOCAL_MEANING_RECORD",
            object_reference=safe_reference,
            content_sha256=_SHA_A,
            record_class="MeaningRecordV01",
            byte_length=512,
            access_policy_id="policy:summary_read",
            sensitivity_class="SECRET_REFERENCE_ONLY",
            allowed_use_classes=("CONTEXT_ONLY",),
            forbidden_use_classes=("ACTION",),
            summary_read_permitted=True,
            payload_read_permitted=False,
        )
        assert pointer.object_reference == safe_reference
    with pytest.raises(
        ValueError,
        match="^drs_secret_payload_forbidden$",
    ):
        semantic.build_meaning_record_v01(
            semantic_address=record.semantic_address,
            predecessor_record_id=None,
            supersession_reason=None,
            safe_summary="Routine note password=not-allowed",
            semantic_tags=record.semantic_tags,
            resonance_reason=record.resonance_reason,
            memory_pointers=record.memory_pointers,
            artifact_pointers=record.artifact_pointers,
            source_reference_ids=record.source_reference_ids,
            lineage_edges=(),
            time_envelope=record.time_envelope,
            authority_envelope=record.authority_envelope,
            persistent_lifecycle_state="ACTIVE",
            risk_hints=(),
            conflict_hints=(),
            reuse_policy_class="CONTEXT_ONLY",
            policy_version="policy_v01",
            schema_versions=("v0.1",),
            content_fingerprint=_SHA_E,
            recording_component="g2b1_fixture",
        )
    source = _legacy_sources()["LOCAL_DRS_DICT"]
    source["content"]["note"] = "Bearer raw-auth-material"
    with pytest.raises(
        ValueError,
        match="^drs_secret_payload_forbidden$",
    ):
        compatibility.project_legacy_drs_source_v01(
            source_family="LOCAL_DRS_DICT",
            source=source,
            target_semantic_address=record.semantic_address,
        )
    for hidden_secret in (
        "sealed-secret-ref:password=not-allowed",
        "audit-ref:Bearer secret-token",
        "scope-ref:iban=raw-account",
    ):
        with pytest.raises(
            ValueError,
            match="^drs_secret_payload_forbidden$",
        ):
            semantic.build_memory_pointer_v01(
                storage_class="LOCAL_MEANING_RECORD",
                object_reference=hidden_secret,
                content_sha256=_SHA_A,
                record_class="MeaningRecordV01",
                byte_length=512,
                access_policy_id="policy:summary_read",
                sensitivity_class="SECRET_REFERENCE_ONLY",
                allowed_use_classes=("CONTEXT_ONLY",),
                forbidden_use_classes=("ACTION",),
                summary_read_permitted=True,
                payload_read_permitted=False,
            )
    card_address = _reidentify(
        replace(address, namespace="4111111111111")
    )
    observed_secret_shapes = {
        "card_shaped_token": (
            semantic.validate_semantic_address_v01(card_address),
            _schema_accepts(card_address, schemas, registry),
        )
    }
    for safe_token in (
        "passport_policy",
        "token_status",
        "password_policy",
        "authentication_mode",
    ):
        safe_address = _reidentify(
            replace(address, namespace=safe_token)
        )
        observed_secret_shapes[f"safe_token:{safe_token}"] = (
            semantic.validate_semantic_address_v01(safe_address),
            _schema_accepts(safe_address, schemas, registry),
        )
    for safe_reference in (
        "policy:passport_requirements",
        "audit:token_policy_review",
    ):
        pointer = _reidentify(
            replace(
                family[semantic.MemoryPointerV01],
                object_reference=safe_reference,
            )
        )
        observed_secret_shapes[f"safe_reference:{safe_reference}"] = (
            semantic.validate_memory_pointer_v01(pointer),
            _schema_accepts(pointer, schemas, registry),
        )
    assert observed_secret_shapes == {
        "card_shaped_token": (
            (False, ("drs_secret_payload_forbidden",)),
            False,
        ),
        **{
            f"safe_token:{value}": ((True, ()), True)
            for value in (
                "passport_policy",
                "token_status",
                "password_policy",
                "authentication_mode",
            )
        },
        **{
            f"safe_reference:{value}": ((True, ()), True)
            for value in (
                "policy:passport_requirements",
                "audit:token_policy_review",
            )
        },
    }, repr(observed_secret_shapes)
    lexical_secret_failures = []
    for secret_value in _LEXICAL_SECRET_NEGATIVE_VALUES:
        safe_text_record = _replace_and_reidentify(
            record,
            field_name="safe_summary",
            field_value=secret_value,
        )
        safe_text_tuple_record = _replace_and_reidentify(
            record,
            field_name="risk_hints",
            field_value=(secret_value,),
        )
        for label, candidate in (
            ("safe_text", safe_text_record),
            ("safe_text_tuple", safe_text_tuple_record),
        ):
            runtime = semantic.validate_meaning_record_v01(candidate)
            schema_accepts = _schema_accepts(candidate, schemas, registry)
            if runtime != (
                False,
                ("drs_secret_payload_forbidden",),
            ) or schema_accepts:
                lexical_secret_failures.append(
                    (secret_value, label, runtime, schema_accepts)
                )
        if semantic._TOKEN.fullmatch(secret_value) is not None:
            token_address = _replace_and_reidentify(
                address,
                field_name="namespace",
                field_value=secret_value,
            )
            token_tuple_record = _replace_and_reidentify(
                record,
                field_name="semantic_tags",
                field_value=(secret_value,),
            )
            for label, candidate, validator in (
                (
                    "token",
                    token_address,
                    semantic.validate_semantic_address_v01,
                ),
                (
                    "token_tuple",
                    token_tuple_record,
                    semantic.validate_meaning_record_v01,
                ),
            ):
                runtime = validator(candidate)
                schema_accepts = _schema_accepts(candidate, schemas, registry)
                if runtime != (
                    False,
                    ("drs_secret_payload_forbidden",),
                ) or schema_accepts:
                    lexical_secret_failures.append(
                        (secret_value, label, runtime, schema_accepts)
                    )
        if semantic._REFERENCE.fullmatch(secret_value) is not None:
            reference_pointer = _replace_and_reidentify(
                family[semantic.MemoryPointerV01],
                field_name="object_reference",
                field_value=secret_value,
            )
            reference_tuple_record = _replace_and_reidentify(
                record,
                field_name="source_reference_ids",
                field_value=(secret_value,),
            )
            for label, candidate, validator in (
                (
                    "reference",
                    reference_pointer,
                    semantic.validate_memory_pointer_v01,
                ),
                (
                    "reference_tuple",
                    reference_tuple_record,
                    semantic.validate_meaning_record_v01,
                ),
            ):
                runtime = validator(candidate)
                schema_accepts = _schema_accepts(candidate, schemas, registry)
                if runtime != (
                    False,
                    ("drs_secret_payload_forbidden",),
                ) or schema_accepts:
                    lexical_secret_failures.append(
                        (secret_value, label, runtime, schema_accepts)
                    )
        legacy_source = _legacy_sources()["LOCAL_DRS_DICT"]
        legacy_source["content"]["summary"] = secret_value
        try:
            compatibility.project_legacy_drs_source_v01(
                source_family="LOCAL_DRS_DICT",
                source=legacy_source,
                target_semantic_address=address,
            )
        except ValueError as error:
            if str(error) != "drs_secret_payload_forbidden":
                lexical_secret_failures.append(
                    (
                        secret_value,
                        "legacy_recursive",
                        str(error),
                        None,
                    )
                )
        else:
            lexical_secret_failures.append(
                (secret_value, "legacy_recursive", "accepted", None)
            )
    assert lexical_secret_failures == [], repr(lexical_secret_failures)
    for safe_token in _LEXICAL_POSITIVE_TOKEN_VALUES:
        safe_address = _replace_and_reidentify(
            address,
            field_name="namespace",
            field_value=safe_token,
        )
        assert semantic.validate_semantic_address_v01(safe_address) == (
            True,
            (),
        )
        assert _schema_accepts(safe_address, schemas, registry)
    for safe_reference in _LEXICAL_POSITIVE_REFERENCE_VALUES:
        safe_pointer = _replace_and_reidentify(
            family[semantic.MemoryPointerV01],
            field_name="object_reference",
            field_value=safe_reference,
        )
        assert semantic.validate_memory_pointer_v01(safe_pointer) == (
            True,
            (),
        )
        assert _schema_accepts(safe_pointer, schemas, registry)
    for safe_text in ("line one\nline two", "column\tvalue"):
        safe_record = _replace_and_reidentify(
            record,
            field_name="safe_summary",
            field_value=safe_text,
        )
        assert semantic.validate_meaning_record_v01(safe_record) == (
            True,
            (),
        )
        assert _schema_accepts(safe_record, schemas, registry)
    parity_counts, parity_failures = _secret_safe_boundary_parity_audit(
        record=record,
        schemas=schemas,
        registry=registry,
    )
    assert parity_counts == {
        "key_value_boundary": 320,
        "authentication_boundary": 24,
        "card_boundary": 160,
        "iban_boundary": 96,
        "unicode_whitespace": 3,
        "positive_boundary": 8,
    }
    assert parity_failures == (), repr(parity_failures)
    reserved_counts, reserved_failures = (
        _reserved_reference_differential_audit(
            family=family,
            schemas=schemas,
            registry=registry,
        )
    )
    assert reserved_counts == {
        "logical_cases": 45,
        "direct_secret_safe_cases": 90,
        "canonical_transport_cases": 270,
        "legacy_recursive_cases": 45,
        "total_cases": 405,
    }
    assert reserved_failures == (), repr(reserved_failures)


def test_g2b_time_fields_require_exact_signed_int64() -> None:
    valid = {
        "pt_created_at": 100,
        "kt_as_of": 101,
        "et_observed_at": 99,
        "ct_context_anchor": 100,
        "ttl_seconds": 1000,
        "valid_from": 50,
        "valid_to": 1000,
        "source_observed_at": 99,
        "source_reported_at": 100,
        "system_ingested_at": 101,
        "system_verified_at": 102,
        "freshness_policy_id": "freshness:reference_v01",
    }
    for invalid in (True, 1.0, Decimal("1"), "1"):
        values = dict(valid)
        values["pt_created_at"] = invalid
        with pytest.raises(ValueError, match="^drs_time_type_invalid$"):
            semantic.build_drs_time_envelope_v01(**values)
    overflow = dict(valid)
    overflow["pt_created_at"] = 2**63 - 1
    overflow["ttl_seconds"] = 1
    with pytest.raises(ValueError, match="^drs_time_overflow_invalid$"):
        semantic.build_drs_time_envelope_v01(**overflow)


def test_g2b_persistent_lifecycle_is_distinct_from_query_state() -> None:
    family = _fixture_family()
    record = family[semantic.MeaningRecordV01]
    evaluation = family[resolution.QueryEvaluationStateV01]
    assert record.persistent_lifecycle_state == "ACTIVE"
    assert evaluation.query_state == "FRESH_CANDIDATE"
    assert not (
        set(semantic.DRS_PERSISTENT_LIFECYCLE_STATES_V01)
        & set(resolution.DRS_QUERY_STATES_V01)
    )
    assert "query_state" not in semantic.meaning_record_to_plain_data_v01(record)
    assert "persistent_lifecycle_state" not in (
        resolution.query_evaluation_state_to_plain_data_v01(evaluation)
    )


def test_g2b_legacy_projection_reports_every_preserved_synthesized_and_missing_field() -> None:
    family = _fixture_family()
    address = family[semantic.SemanticAddressV01]
    record = family[semantic.MeaningRecordV01]
    expected_statuses = {
        "LOCAL_DRS_DICT": "CANONICAL_CONTEXT_ONLY",
        "DRS_RECORD_SCHEMA_V0": "CANONICAL_CONTEXT_ONLY",
        "SEMANTIC_DRS_RECORD_INPUT": "RERUN_REQUIRED",
        "DRS_RECORD_V02": "CANONICAL_COMPLETE",
        "DRS_FRESHNESS_ENVELOPE_V02": "PROJECTION_REJECTED",
        "TEMPORAL_QUERY_V02": "BLOCKED",
    }
    assert tuple(profile[0] for profile in compatibility._SOURCE_PROFILES) == (
        tuple(_EXPECTED_SOURCE_PROFILE_FIELDS)
    )
    assert {
        profile[0]: profile[3]
        for profile in compatibility._SOURCE_PROFILES
    } == _EXPECTED_SOURCE_PROFILE_FIELDS
    for source_family, source in _legacy_sources().items():
        source_before = pickle.dumps(source)
        projection = compatibility.project_legacy_drs_source_v01(
            source_family=source_family,
            source=source,
            target_semantic_address=address,
            target_meaning_record=(
                record if source_family == "DRS_RECORD_V02" else None
            ),
        )
        assert projection.projection_status == expected_statuses[source_family]
        expected_preserved = tuple(
            field_name
            for field_name in _EXPECTED_SOURCE_PROFILE_FIELDS[source_family]
            if type(source) is not dict or field_name in source
        )
        assert projection.fields_preserved == expected_preserved
        assert projection.fields_synthesized == (
            "target_semantic_address_id",
            "projection_profile_version",
        )
        assert projection.downgrade_restrictions == (
            "answer_shortcut_forbidden_in_g2b1",
            "root_review_required",
            "legacy_object_not_canonical",
        )
        assert projection.answer_shortcut_eligible is False
        assert projection.creates_authority is False
        assert projection.creates_permission is False
        assert set(projection.fields_preserved) == set(
            tuple(source)
            if type(source) is dict
            else _EXPECTED_SOURCE_PROFILE_FIELDS[source_family]
        )
        assert not (
            set(projection.fields_preserved)
            & set(projection.fields_synthesized)
        )
        assert pickle.dumps(source) == source_before
    local = _legacy_sources()["LOCAL_DRS_DICT"]
    reordered = {
        field_name: local[field_name]
        for field_name in reversed(tuple(local))
    }
    ordered_projection = compatibility.project_legacy_drs_source_v01(
        source_family="LOCAL_DRS_DICT",
        source=local,
        target_semantic_address=address,
    )
    malformed_schema = _legacy_sources()["DRS_RECORD_SCHEMA_V0"]
    malformed_schema["unclassified_extra"] = "currently accepted"
    with pytest.raises(ValueError, match="^drs_legacy_source_invalid$"):
        compatibility.project_legacy_drs_source_v01(
            source_family="DRS_RECORD_SCHEMA_V0",
            source=malformed_schema,
            target_semantic_address=address,
        )
    malformed_local = _legacy_sources()["LOCAL_DRS_DICT"]
    malformed_local["time_envelope"]["ttl_seconds"] = True
    with pytest.raises(ValueError, match="^drs_legacy_source_invalid$"):
        compatibility.project_legacy_drs_source_v01(
            source_family="LOCAL_DRS_DICT",
            source=malformed_local,
            target_semantic_address=address,
        )
    reordered_projection = compatibility.project_legacy_drs_source_v01(
        source_family="LOCAL_DRS_DICT",
        source=reordered,
        target_semantic_address=address,
    )
    assert reordered_projection == ordered_projection
    projection_forgery = _reidentify(
        replace(
            ordered_projection,
            fields_preserved=tuple(
                f"field_{index}" for index in range(65)
            ),
        )
    )
    schemas = _schemas()
    registry = _schema_registry(schemas)
    assert compatibility.validate_legacy_drs_projection_v01(
        projection_forgery
    )[0] is False and _schema_accepts(
        projection_forgery, schemas, registry
    ) is False


def test_g2b_missing_legacy_safety_evidence_cannot_become_shortcut() -> None:
    family = _fixture_family()
    address = family[semantic.SemanticAddressV01]
    for source_family, source in _legacy_sources().items():
        projection = compatibility.project_legacy_drs_source_v01(
            source_family=source_family,
            source=source,
            target_semantic_address=address,
            target_meaning_record=None,
        )
        assert projection.answer_shortcut_eligible is False
        assert projection.projection_status in {
            "CANONICAL_CONTEXT_ONLY",
            "RERUN_REQUIRED",
            "BLOCKED",
            "PROJECTION_REJECTED",
        }
        assert "answer_shortcut_forbidden_in_g2b1" in (
            projection.downgrade_restrictions
        )
    with pytest.raises(
        ValueError,
        match="^drs_legacy_source_family_type_mismatch$",
    ):
        compatibility.project_legacy_drs_source_v01(
            source_family="DRS_RECORD_V02",
            source=_legacy_sources()["LOCAL_DRS_DICT"],
            target_semantic_address=address,
        )
    malformed_freshness = replace(
        _legacy_sources()["DRS_FRESHNESS_ENVELOPE_V02"],
        ttl_seconds=True,
    )
    with pytest.raises(ValueError, match="^drs_legacy_source_invalid$"):
        compatibility.project_legacy_drs_source_v01(
            source_family="DRS_FRESHNESS_ENVELOPE_V02",
            source=malformed_freshness,
            target_semantic_address=address,
        )
    forged_identity = replace(
        _legacy_sources()["DRS_RECORD_V02"],
        record_id="forged identity with spaces",
    )
    with pytest.raises(
        ValueError,
        match="^drs_legacy_source_identity_invalid$",
    ):
        compatibility.project_legacy_drs_source_v01(
            source_family="DRS_RECORD_V02",
            source=forged_identity,
            target_semantic_address=address,
        )
    malformed_input = replace(
        _legacy_sources()["SEMANTIC_DRS_RECORD_INPUT"],
        content=[],
    )
    with pytest.raises(ValueError, match="^drs_legacy_source_invalid$"):
        compatibility.project_legacy_drs_source_v01(
            source_family="SEMANTIC_DRS_RECORD_INPUT",
            source=malformed_input,
            target_semantic_address=address,
        )
    base = compatibility.project_legacy_drs_source_v01(
        source_family="LOCAL_DRS_DICT",
        source=_legacy_sources()["LOCAL_DRS_DICT"],
        target_semantic_address=address,
    )
    coherent_forgeries = (
        (
            "family_version_mismatch",
            _reidentify(
                replace(base, source_version="temporal_query_v02")
            ),
        ),
        (
            "arbitrary_fields_preserved",
            _reidentify(
                replace(
                    base,
                    fields_preserved=("completely_wrong_field",),
                )
            ),
        ),
        (
            "incorrect_fields_synthesized",
            _reidentify(
                replace(base, fields_synthesized=("projection_profile_version",))
            ),
        ),
        (
            "arbitrary_downgrade_restrictions",
            _reidentify(
                replace(base, downgrade_restrictions=("caller_selected",))
            ),
        ),
        (
            "impossible_status_reason",
            _reidentify(
                replace(
                    base,
                    projection_status="CANONICAL_COMPLETE",
                    reason_codes=(),
                )
            ),
        ),
    )
    schemas = _schemas()
    registry = _schema_registry(schemas)
    observed = {}
    for label, forged in coherent_forgeries:
        runtime = compatibility.validate_legacy_drs_projection_v01(forged)
        schema_accepts = _schema_accepts(forged, schemas, registry)
        observed[label] = (runtime, schema_accepts)
    assert observed == {
        label: ((False, ("drs_legacy_projection_incomplete",)), False)
        for label, _ in coherent_forgeries
    }, repr(observed)


def test_g2b_validators_reject_custom_equality_substitutes() -> None:
    family = _fixture_family()
    substitute = _EqualitySubstitute()
    for validator in _VALIDATORS.values():
        valid, reasons = validator(substitute)
        assert valid is False
        assert reasons == ("drs_exact_type_required",)
    record = family[semantic.MeaningRecordV01]
    invalid = replace(record, memory_pointers=(substitute,))
    assert semantic.validate_meaning_record_v01(invalid) == (
        False,
        ("drs_exact_type_required",),
    )


def test_g2b_validators_reject_str_subclasses() -> None:
    family = _fixture_family()
    for contract_type, value in family.items():
        version_field = _EXPECTED_FIELDS[contract_type][0]
        invalid = replace(
            value,
            **{
                version_field: _StringSubclass(
                    getattr(value, version_field)
                )
            },
        )
        assert _VALIDATORS[contract_type](invalid) == (
            False,
            ("drs_exact_type_required",),
        )
    record = family[semantic.MeaningRecordV01]
    tuple_subclass = replace(
        record,
        semantic_tags=_TupleSubclass(record.semantic_tags),
    )
    assert semantic.validate_meaning_record_v01(tuple_subclass)[0] is False


def test_g2b_validators_reject_bool_as_int() -> None:
    family = _fixture_family()
    time_envelope = family[semantic.DRSTimeEnvelopeV01]
    invalid_time = replace(time_envelope, pt_created_at=True)
    assert semantic.validate_drs_time_envelope_v01(invalid_time)[1][0] == (
        "drs_time_type_invalid"
    )
    budget = family[resolution.MemoryDescentBudgetV01]
    invalid_budget = replace(budget, max_depth=True)
    assert resolution.validate_memory_descent_budget_v01(invalid_budget)[1] == (
        "drs_exact_int_required",
    )
    candidate = family[resolution.ResolutionCandidateV01]
    invalid_candidate = replace(candidate, freshness_units=True)
    assert resolution.validate_resolution_candidate_v01(
        invalid_candidate
    )[1][0] == "drs_exact_int_required"


def test_g2b_pickle_reconstruction_cannot_bypass_validation() -> None:
    family = _fixture_family()
    for contract_type, value in family.items():
        restored = pickle.loads(pickle.dumps(value))
        assert type(restored) is contract_type
        assert _VALIDATORS[contract_type](restored) == (True, ())
    address = pickle.loads(
        pickle.dumps(family[semantic.SemanticAddressV01])
    )
    object.__setattr__(address, "namespace", "tampered")
    assert semantic.validate_semantic_address_v01(address) == (
        False,
        ("drs_identity_invalid",),
    )


def test_g2b_schema_and_version_mixing_fails_closed() -> None:
    family = _fixture_family()
    schemas = _schemas()
    registry = _schema_registry(schemas)
    for schema in schemas.values():
        Draft202012Validator.check_schema(schema)
    address_secret_patterns = _secret_safe_patterns(
        schemas["drs_semantic_address_v01.schema.json"]
    )
    meaning_secret_patterns = _secret_safe_patterns(
        schemas["drs_meaning_record_v01.schema.json"]
    )
    address_secret_conditionals = _secret_safe_conditionals(
        schemas["drs_semantic_address_v01.schema.json"]
    )
    meaning_secret_conditionals = _secret_safe_conditionals(
        schemas["drs_meaning_record_v01.schema.json"]
    )
    assert address_secret_conditionals == (
        _EXPECTED_RESERVED_REFERENCE_CONDITIONALS
    )
    assert meaning_secret_conditionals == (
        _EXPECTED_RESERVED_REFERENCE_CONDITIONALS
    )
    assert address_secret_patterns[0] == (
        _EXPECTED_SECRETSAFE_KEY_VALUE_PATTERN
    )
    assert meaning_secret_patterns[0] == (
        _EXPECTED_SECRETSAFE_KEY_VALUE_PATTERN
    )
    assert address_secret_patterns[1:3] == (
        _EXPECTED_SECRETSAFE_AUTHENTICATION_PATTERNS
    )
    assert meaning_secret_patterns[1:3] == (
        _EXPECTED_SECRETSAFE_AUTHENTICATION_PATTERNS
    )
    assert address_secret_patterns[3] == (
        _EXPECTED_SECRETSAFE_CARD_PATTERN
    )
    assert meaning_secret_patterns[4] == (
        _EXPECTED_SECRETSAFE_CARD_PATTERN
    )
    assert address_secret_patterns[4] == (
        _EXPECTED_SECRETSAFE_IBAN_PATTERN
    )
    assert meaning_secret_patterns[5] == (
        _EXPECTED_SECRETSAFE_IBAN_PATTERN
    )
    lexical_schema_observations = _lexical_schema_observations(schemas)
    assert lexical_schema_observations
    assert {
        label: accepted
        for label, accepted in lexical_schema_observations.items()
        if accepted
    } == {}, repr(lexical_schema_observations)
    assert semantic._token_reason("abc\n") == "drs_text_bound_invalid"
    assert (
        semantic._reference_reason("reference:value\n")
        == "drs_text_bound_invalid"
    )
    assert (
        semantic._media_type_reason("application/json\n")
        == "drs_text_bound_invalid"
    )
    assert semantic._is_sha256(_SHA_A + "\n") is False
    assert (
        semantic._field_name_tuple_reasons(
            ("valid_field\n",),
            maximum_items=128,
        )
        == ("drs_text_bound_invalid",)
    )
    for prefix in set(_PREFIXES.values()):
        assert (
            semantic._typed_id_reason(prefix + _SHA_A + "\n", prefix)
            == "drs_text_bound_invalid"
        )
    assert (
        semantic._bounded_text("safe\rtext", maximum=1024)
        == "drs_text_bound_invalid"
    )
    assert (
        semantic._bounded_text("safe\x7ftext", maximum=1024)
        == "drs_text_bound_invalid"
    )
    assert semantic._bounded_text("safe\ttext", maximum=1024) is None
    assert semantic._bounded_text("safe\ntext", maximum=1024) is None
    field_probe_count, field_probe_failures = (
        _field_contract_boundary_failures(family, schemas, registry)
    )
    assert field_probe_count > len(_STRING_FIELD_CONTRACT_MATRIX)
    assert field_probe_failures == (), repr(field_probe_failures)
    schema_string_counts, schema_string_failures = (
        _schema_string_node_inventory(schemas)
    )
    assert sum(schema_string_counts.values()) > 0
    assert schema_string_failures == (), repr(schema_string_failures)
    roots = {
        "drs_semantic_address_v01.schema.json": family[
            semantic.SemanticAddressV01
        ],
        "drs_meaning_record_v01.schema.json": family[
            semantic.MeaningRecordV01
        ],
        "drs_memory_resolution_v01.schema.json": family[
            resolution.DRSResolutionReportV01
        ],
        "reuse_certificate_v01.schema.json": family[
            reuse.ReuseCertificateV01
        ],
    }
    for name, value in roots.items():
        Draft202012Validator(
            schemas[name],
            registry=registry,
        ).validate(_SERIALIZERS[type(value)](value))
    for contract_type, value in family.items():
        contract_schema = _schema_reference_for_type(
            contract_type,
            schemas,
        )
        validator = Draft202012Validator(
            contract_schema,
            registry=registry,
        )
        plain = _SERIALIZERS[contract_type](value)
        validator.validate(plain)
        definition = _schema_definition_for_type(contract_type, schemas)
        assert definition["additionalProperties"] is False
        assert tuple(definition["required"]) == _EXPECTED_FIELDS[contract_type]
        assert tuple(definition["properties"]) == _EXPECTED_FIELDS[contract_type]
        for field_name in _EXPECTED_FIELDS[contract_type]:
            missing_plain = dict(plain)
            del missing_plain[field_name]
            with pytest.raises(ValidationError):
                validator.validate(missing_plain)
            invalid_plain = dict(plain)
            invalid_plain[field_name] = _wrong_json_type(plain[field_name])
            with pytest.raises(ValidationError):
                validator.validate(invalid_plain)
            invalid_runtime = replace(
                value,
                **{
                    field_name: _wrong_runtime_type(
                        getattr(value, field_name)
                    )
                },
            )
            assert _VALIDATORS[contract_type](invalid_runtime)[0] is False
    schema_types = {
        semantic.SemanticAddressV01: (
            schemas["drs_semantic_address_v01.schema.json"]["properties"]
        ),
        semantic.MemoryPointerV01: schemas[
            "drs_meaning_record_v01.schema.json"
        ]["$defs"]["MemoryPointerV01"]["properties"],
        semantic.ArtifactPointerV01: schemas[
            "drs_meaning_record_v01.schema.json"
        ]["$defs"]["ArtifactPointerV01"]["properties"],
        semantic.LineageEdgeV01: schemas[
            "drs_meaning_record_v01.schema.json"
        ]["$defs"]["LineageEdgeV01"]["properties"],
        semantic.DRSAuthorityEnvelopeV01: schemas[
            "drs_meaning_record_v01.schema.json"
        ]["$defs"]["DRSAuthorityEnvelopeV01"]["properties"],
        semantic.DRSTimeEnvelopeV01: schemas[
            "drs_meaning_record_v01.schema.json"
        ]["$defs"]["DRSTimeEnvelopeV01"]["properties"],
        semantic.MeaningRecordV01: schemas[
            "drs_meaning_record_v01.schema.json"
        ]["$defs"]["MeaningRecordV01"]["properties"],
        resolution.DRSTemporalQueryV01: schemas[
            "drs_memory_resolution_v01.schema.json"
        ]["$defs"]["DRSTemporalQueryV01"]["properties"],
        resolution.QueryEvaluationStateV01: schemas[
            "drs_memory_resolution_v01.schema.json"
        ]["$defs"]["QueryEvaluationStateV01"]["properties"],
        resolution.ResolutionCandidateV01: schemas[
            "drs_memory_resolution_v01.schema.json"
        ]["$defs"]["ResolutionCandidateV01"]["properties"],
        resolution.RetrievalPlanV01: schemas[
            "drs_memory_resolution_v01.schema.json"
        ]["$defs"]["RetrievalPlanV01"]["properties"],
        resolution.MemoryDescentBudgetV01: schemas[
            "drs_memory_resolution_v01.schema.json"
        ]["$defs"]["MemoryDescentBudgetV01"]["properties"],
        resolution.MemoryDescentRequestV01: schemas[
            "drs_memory_resolution_v01.schema.json"
        ]["$defs"]["MemoryDescentRequestV01"]["properties"],
        resolution.MemoryDescentResultV01: schemas[
            "drs_memory_resolution_v01.schema.json"
        ]["$defs"]["MemoryDescentResultV01"]["properties"],
        reuse.RootShortcutAuthorizationProjectionV01: schemas[
            "reuse_certificate_v01.schema.json"
        ]["$defs"]["RootShortcutAuthorizationProjectionV01"]["properties"],
        reuse.ReuseCertificateV01: schemas[
            "reuse_certificate_v01.schema.json"
        ]["$defs"]["ReuseCertificateV01"]["properties"],
        resolution.DRSResolutionReportV01: schemas[
            "drs_memory_resolution_v01.schema.json"
        ]["$defs"]["DRSResolutionReportV01"]["properties"],
        compatibility.LegacyDRSProjectionV01: schemas[
            "drs_memory_resolution_v01.schema.json"
        ]["$defs"]["LegacyDRSProjectionV01"]["properties"],
        reuse.G2AActionHistoryBindingV01: schemas[
            "reuse_certificate_v01.schema.json"
        ]["$defs"]["G2AActionHistoryBindingV01"]["properties"],
    }
    assert {
        contract_type: tuple(properties)
        for contract_type, properties in schema_types.items()
    } == _EXPECTED_FIELDS
    meaning_schema = schemas["drs_meaning_record_v01.schema.json"]
    assert meaning_schema["$defs"]["reference"]["maxLength"] == 256
    pointer_validator = Draft202012Validator(
        {
            "$ref": (
                meaning_schema["$id"]
                + "#/$defs/MemoryPointerV01"
            )
        },
        registry=registry,
    )
    pointer_plain = semantic.memory_pointer_to_plain_data_v01(
        family[semantic.MemoryPointerV01]
    )
    for invalid_reference in (
        "r" * 257,
        "sealed-secret-ref:password=not-allowed",
        "audit-ref:Bearer secret-token",
        "scope-ref:iban=raw-account",
    ):
        invalid_pointer = dict(pointer_plain)
        invalid_pointer["object_reference"] = invalid_reference
        with pytest.raises(ValidationError):
            pointer_validator.validate(invalid_pointer)
    authority_plain = semantic.drs_authority_envelope_to_plain_data_v01(
        family[semantic.DRSAuthorityEnvelopeV01]
    )
    authority_plain["root_acceptance_state"] = "ACCEPTED_WORK"
    authority_validator = Draft202012Validator(
        {
            "$ref": (
                meaning_schema["$id"]
                + "#/$defs/DRSAuthorityEnvelopeV01"
            )
        },
        registry=registry,
    )
    with pytest.raises(ValidationError):
        authority_validator.validate(authority_plain)
    same_type_schema_probes = (
        (
            "candidate_safe_summary_secret",
            _reidentify(
                replace(
                    family[resolution.ResolutionCandidateV01],
                    safe_summary="password=not-allowed",
                )
            ),
        ),
        (
            "descent_safe_summary_secret",
            _reidentify(
                replace(
                    family[resolution.MemoryDescentResultV01],
                    safe_summaries=("Bearer raw-auth-material",),
                )
            ),
        ),
        (
            "query_evidence_non_token",
            _reidentify(
                replace(
                    family[resolution.DRSTemporalQueryV01],
                    required_evidence_classes=("not a token",),
                )
            ),
        ),
        (
            "query_evidence_count_33",
            _reidentify(
                replace(
                    family[resolution.DRSTemporalQueryV01],
                    required_evidence_classes=tuple(
                        f"evidence_{index}" for index in range(33)
                    ),
                )
            ),
        ),
        (
            "plan_record_wrong_prefix",
            _reidentify(
                replace(
                    family[resolution.RetrievalPlanV01],
                    proposed_record_ids=("generic:record-reference",),
                )
            ),
        ),
        (
            "plan_memory_pointer_wrong_prefix",
            _reidentify(
                replace(
                    family[resolution.RetrievalPlanV01],
                    proposed_memory_pointer_ids=("generic:memory-reference",),
                )
            ),
        ),
        (
            "plan_artifact_pointer_wrong_prefix",
            _reidentify(
                replace(
                    family[resolution.RetrievalPlanV01],
                    proposed_artifact_pointer_ids=("generic:artifact-reference",),
                )
            ),
        ),
        (
            "query_unknown_evaluation_time_source",
            _reidentify(
                replace(
                    family[resolution.DRSTemporalQueryV01],
                    evaluation_time_source="CALLER_SELECTED_TIME",
                )
            ),
        ),
        (
            "evaluation_unknown_evaluation_time_source",
            _reidentify(
                replace(
                    family[resolution.QueryEvaluationStateV01],
                    evaluation_time_source="CALLER_SELECTED_TIME",
                )
            ),
        ),
        (
            "certificate_unknown_case_type",
            _reidentify(
                replace(
                    family[reuse.ReuseCertificateV01],
                    case_type="ACTION_LIKE",
                )
            ),
        ),
        (
            "artifact_media_type_whitespace",
            _reidentify(
                replace(
                    family[semantic.ArtifactPointerV01],
                    media_type="application json",
                )
            ),
        ),
        (
            "artifact_media_type_over_bound",
            _reidentify(
                replace(
                    family[semantic.ArtifactPointerV01],
                    media_type="a/" + "b" * 127,
                )
            ),
        ),
    )
    observed = {}
    for label, invalid in same_type_schema_probes:
        runtime = _VALIDATORS[type(invalid)](invalid)
        schema_accepts = _schema_accepts(invalid, schemas, registry)
        observed[label] = (runtime, schema_accepts)
    assert all(
        runtime[0] is False for runtime, _ in observed.values()
    ), repr(observed)
    assert {
        label: schema_accepts
        for label, (_, schema_accepts) in observed.items()
    } == {
        label: False for label, _ in same_type_schema_probes
    }, repr(observed)
    matrix_failures = []
    for (
        _,
        contract_type,
        field_name,
        contract_class,
        _,
        _,
        _,
        _,
        _,
    ) in _STRING_FIELD_CONTRACT_MATRIX:
        invalid = _same_type_contract_mutation(
            family[contract_type],
            field_name=field_name,
            contract_class=contract_class,
        )
        runtime = _VALIDATORS[contract_type](invalid)
        schema_accepts = _schema_accepts(invalid, schemas, registry)
        if runtime[0] or schema_accepts:
            matrix_failures.append(
                (
                    contract_type.__name__,
                    field_name,
                    contract_class,
                    runtime,
                    schema_accepts,
                )
            )
    assert matrix_failures == [], repr(matrix_failures)
    schema_text = json.dumps(schemas, sort_keys=True)
    assert "(?i:" not in schema_text
    assert "(?<=" not in schema_text
    assert "(?<!" not in schema_text
    mixed = replace(
        family[semantic.SemanticAddressV01],
        address_profile_version="v0.2",
    )
    assert semantic.validate_semantic_address_v01(mixed) == (
        False,
        ("drs_schema_version_mismatch",),
    )
    with pytest.raises(Exception):
        Draft202012Validator(
            schemas["drs_semantic_address_v01.schema.json"],
            registry=registry,
        ).validate(semantic.semantic_address_to_plain_data_v01(mixed))
