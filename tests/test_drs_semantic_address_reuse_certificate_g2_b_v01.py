from __future__ import annotations

from dataclasses import FrozenInstanceError, fields, is_dataclass, replace
from decimal import Decimal
import hashlib
import inspect
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
import hedgehog.kernel.root_decision_v01 as root_decision
import hedgehog.kernel.semantic_work_v01 as semantic_work
from hedgehog.kernel.trust_model_v01 import (
    build_default_component_trust_profiles_v01,
)
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


_B2_EVIDENCE_CLASSES = (
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
_B2_ALL_TIME_AXES = ("PT", "KT", "ET", "CT", "TTL", "VALIDITY")
_B2_MODE_PROFILE = (
    (
        "CURRENT_DECISION",
        "INJECTED_CURRENT_DECISION_TIME",
        _B2_ALL_TIME_AXES,
    ),
    (
        "DIRECT_REUSE_CANDIDATE",
        "INJECTED_CURRENT_DECISION_TIME",
        _B2_ALL_TIME_AXES,
    ),
    (
        "HISTORICAL_AS_OF",
        "RECORDED_HISTORICAL_AS_OF_TIME",
        ("KT", "VALIDITY"),
    ),
    (
        "AUDIT_REPLAY",
        "RECORDED_AUDIT_REPLAY_TIME",
        ("PT", "KT", "ET", "CT", "VALIDITY"),
    ),
    (
        "TREND_ANALYSIS",
        "INJECTED_ANALYSIS_TIME",
        ("KT", "ET", "VALIDITY"),
    ),
    (
        "MEMORY_CONTEXT_ONLY",
        "INJECTED_ANALYSIS_TIME",
        ("KT", "TTL", "VALIDITY"),
    ),
)
_B2_IDENTITY_VECTORS = {
    "query_evaluation_id": (
        "drsqeval_v01:"
        "febbf3354c3aecfc9b7a3a6b88c4f2f61d930f6f2faaae5f0df3801dab230ba3"
    ),
    "candidate_ids": (
        "drscandidate_v01:"
        "0c233cfa0bffa0b6c30641dbf0ebaab479e20f5ba7383d5dfc67e4dcf58e5e7a",
        "drscandidate_v01:"
        "10ad3d8778725da9f3fb7bc7203252490e81b7c3c2dab669ef26498f37b6a087",
        "drscandidate_v01:"
        "3088fd39fcee23ff38f19743f68459bcab64e0675fcdcb06637f6de1e9dd80cc",
    ),
    "ranked_candidate_ids": (
        "drscandidate_v01:"
        "0c233cfa0bffa0b6c30641dbf0ebaab479e20f5ba7383d5dfc67e4dcf58e5e7a",
        "drscandidate_v01:"
        "10ad3d8778725da9f3fb7bc7203252490e81b7c3c2dab669ef26498f37b6a087",
        "drscandidate_v01:"
        "3088fd39fcee23ff38f19743f68459bcab64e0675fcdcb06637f6de1e9dd80cc",
    ),
    "selected_candidate_id": (
        "drscandidate_v01:"
        "0c233cfa0bffa0b6c30641dbf0ebaab479e20f5ba7383d5dfc67e4dcf58e5e7a"
    ),
    "observed_evidence_fingerprint": (
        "f73b43cc76eacc59184c16065bf76276c072afaa02011a1a49fb0e48759bb38e"
    ),
    "checked_dependency_fingerprint": (
        "b0ae1bb7426fa62f8478de0465f6fc12b8484b69c74e81e16300b7761529fd06"
    ),
    "source_history_hash": (
        "7ff6d9fbef5907865f15980eb451c060bce2c186a6845e4e31fd23b8e3f7bcdc"
    ),
    "report_id": (
        "drsreport_v01:"
        "8663d05defeda985e4c2c7979858665ccebaa16ff4c278d48ab551c3dd3a551b"
    ),
}


def _b2_address(
    *,
    intent_class: str = "informational_summary",
) -> semantic.SemanticAddressV01:
    return semantic.build_semantic_address_v01(
        namespace="local_reference",
        domain="g2b2_information",
        subject_class="bounded_information",
        intent_class=intent_class,
        meaning_schema_id="drs_meaning_record",
        meaning_schema_version="v0.1",
    )


def _b2_authority(
    *,
    authority_class: str = "ROOT_ACCEPTED_CONTEXT",
    root_acceptance_state: str = "ACCEPTED_CONTEXT",
) -> semantic.DRSAuthorityEnvelopeV01:
    root_evidence = authority_class in {
        "ROOT_ACCEPTED_CONTEXT",
        "ROOT_ACCEPTED_WORK",
        "ROOT_FINAL_REFERENCE",
    }
    return semantic.build_drs_authority_envelope_v01(
        authority_class=authority_class,
        owning_local_root_id="root:local_reference" if root_evidence else None,
        source_root_decision_input_id=(
            "root-input:g2b2:accepted" if root_evidence else None
        ),
        source_root_decision_id=(
            "root-decision:g2b2:accepted" if root_evidence else None
        ),
        source_root_decision_hash=_SHA_D if root_evidence else None,
        authority_scope_fingerprint=_SHA_C,
        root_acceptance_state=root_acceptance_state,
        recording_component="g2b2_fixture",
    )


def _b2_time(
    *,
    pt_created_at: int = 100,
    kt_as_of: int = 100,
    et_observed_at: int = 100,
    ct_context_anchor: int = 100,
    ttl_seconds: int = 1000,
    valid_from: int = 50,
    valid_to: int = 1000,
) -> semantic.DRSTimeEnvelopeV01:
    return semantic.build_drs_time_envelope_v01(
        pt_created_at=pt_created_at,
        kt_as_of=kt_as_of,
        et_observed_at=et_observed_at,
        ct_context_anchor=ct_context_anchor,
        ttl_seconds=ttl_seconds,
        valid_from=valid_from,
        valid_to=valid_to,
        source_observed_at=100,
        source_reported_at=101,
        system_ingested_at=102,
        system_verified_at=103,
        freshness_policy_id="freshness:g2b2_v01",
    )


def _b2_record(
    *,
    ordinal: int = 1,
    address: semantic.SemanticAddressV01 | None = None,
    time_envelope: semantic.DRSTimeEnvelopeV01 | None = None,
    authority: semantic.DRSAuthorityEnvelopeV01 | None = None,
    persistent_lifecycle_state: str = "ACTIVE",
    risk_hints: tuple[str, ...] = (),
    conflict_hints: tuple[str, ...] = (),
    reuse_policy_class: str = "ANSWER_SHORTCUT",
    policy_version: str = "policy_v01",
    schema_versions: tuple[str, ...] = ("v0.1",),
    source_reference_ids: tuple[str, ...] | None = None,
    lineage_edges: tuple[semantic.LineageEdgeV01, ...] = (),
) -> semantic.MeaningRecordV01:
    address = address or _b2_address()
    return semantic.build_meaning_record_v01(
        semantic_address=address,
        predecessor_record_id=None,
        supersession_reason=None,
        safe_summary=f"Bounded G2-B2 informational summary {ordinal}.",
        semantic_tags=("g2b2", "informational"),
        resonance_reason="Exact local semantic address match.",
        memory_pointers=(),
        artifact_pointers=(),
        source_reference_ids=(
            source_reference_ids
            if source_reference_ids is not None
            else (f"source:g2b2:{ordinal}",)
        ),
        lineage_edges=lineage_edges,
        time_envelope=time_envelope or _b2_time(),
        authority_envelope=authority or _b2_authority(),
        persistent_lifecycle_state=persistent_lifecycle_state,
        risk_hints=risk_hints,
        conflict_hints=conflict_hints,
        reuse_policy_class=reuse_policy_class,
        policy_version=policy_version,
        schema_versions=schema_versions,
        content_fingerprint=f"{ordinal:x}"[-1] * 64,
        recording_component="g2b2_fixture",
    )


def _b2_query(
    *,
    address: semantic.SemanticAddressV01 | None = None,
    query_mode: str = "DIRECT_REUSE_CANDIDATE",
    as_of: int = 200,
    evaluation_time: int = 200,
    evaluation_time_source: str = "INJECTED_CURRENT_DECISION_TIME",
    required_time_axes: tuple[str, ...] = _B2_ALL_TIME_AXES,
    max_age_seconds: int = 1000,
    reuse_intent: str = "INFORMATIONAL_SHORTCUT_CONSIDERATION",
    requested_reuse_classes: tuple[str, ...] = ("ANSWER_SHORTCUT",),
    required_evidence_classes: tuple[str, ...] = _B2_EVIDENCE_CLASSES,
    forbidden_changes: tuple[str, ...] = ("POLICY_CHANGED",),
    policy_version: str = "policy_v01",
    schema_versions: tuple[str, ...] = ("v0.1",),
    scope_fingerprint: str = _SHA_C,
    owning_local_root_id: str = "root:local_reference",
) -> resolution.DRSTemporalQueryV01:
    address = address or _b2_address()
    return resolution.build_drs_temporal_query_v01(
        query_mode=query_mode,
        semantic_address_id=address.semantic_address_id,
        scope_fingerprint=scope_fingerprint,
        as_of=as_of,
        evaluation_time=evaluation_time,
        evaluation_time_source=evaluation_time_source,
        time_range_start=0,
        time_range_end=2000,
        required_time_axes=required_time_axes,
        freshness_policy_id="freshness:g2b2_v01",
        max_age_seconds=max_age_seconds,
        domain=address.domain,
        risk_class="LOW",
        reuse_intent=reuse_intent,
        requested_reuse_classes=requested_reuse_classes,
        required_evidence_classes=required_evidence_classes,
        forbidden_changes=forbidden_changes,
        policy_version=policy_version,
        schema_versions=schema_versions,
        owning_local_root_id=owning_local_root_id,
    )


def _b2_evaluate(
    record: semantic.MeaningRecordV01,
    query: resolution.DRSTemporalQueryV01,
    *,
    address: semantic.SemanticAddressV01 | None = None,
    action_history_binding: reuse.G2AActionHistoryBindingV01 | None = None,
) -> resolution.QueryEvaluationStateV01:
    return resolution.evaluate_drs_candidate_v01(
        semantic_address=address or record.semantic_address,
        query=query,
        meaning_record=record,
        action_history_binding=action_history_binding,
    )


def _b2_candidate(
    evaluation: resolution.QueryEvaluationStateV01,
    query: resolution.DRSTemporalQueryV01,
    record: semantic.MeaningRecordV01,
    *,
    semantic_similarity_units: int,
    gt_advisory_prior_units: int = 1000,
    conflict_penalty_units: int = 0,
    risk_penalty_units: int = 0,
    retrieval_cost_units: int = 100,
) -> resolution.ResolutionCandidateV01:
    return resolution.build_resolution_candidate_v01(
        query_id=query.query_id,
        semantic_address_id=query.semantic_address_id,
        meaning_record_id=record.meaning_record_id,
        query_evaluation_id=evaluation.query_evaluation_id,
        safe_summary=record.safe_summary,
        evidence_ref_ids=record.source_reference_ids,
        source_history_hash=evaluation.source_history_hash,
        action_history_binding_id=evaluation.action_history_binding_id,
        semantic_similarity_units=semantic_similarity_units,
        freshness_units=evaluation.current_freshness_units,
        source_authority_prior_units=9000,
        lineage_proximity_units=7000,
        historical_utility_units=6000,
        gt_advisory_prior_units=gt_advisory_prior_units,
        conflict_penalty_units=conflict_penalty_units,
        risk_penalty_units=risk_penalty_units,
        retrieval_cost_units=retrieval_cost_units,
    )


def _b2_positive_fixture() -> dict[str, object]:
    address = _b2_address()
    query = _b2_query(address=address)
    records = tuple(
        _b2_record(ordinal=ordinal, address=address)
        for ordinal in (1, 2, 3)
    )
    evaluations = tuple(_b2_evaluate(record, query) for record in records)
    candidates = (
        _b2_candidate(
            evaluations[0],
            query,
            records[0],
            semantic_similarity_units=9000,
        ),
        _b2_candidate(
            evaluations[1],
            query,
            records[1],
            semantic_similarity_units=8000,
        ),
        _b2_candidate(
            evaluations[2],
            query,
            records[2],
            semantic_similarity_units=8000,
        ),
    )
    ranked = resolution.rank_eligible_drs_candidates_v01(
        query=query,
        query_evaluations=evaluations,
        candidates=candidates,
    )
    budget = resolution.build_memory_descent_budget_v01(
        max_depth=0,
        max_records_opened=3,
        max_pointers_opened=0,
        max_artifacts_opened=0,
        max_bytes_opened=0,
        max_lineage_edges=0,
        max_conflict_records=0,
    )
    plan = resolution.build_retrieval_plan_v01(
        query_id=query.query_id,
        semantic_address_id=address.semantic_address_id,
        proposed_record_ids=tuple(
            record.meaning_record_id for record in records
        ),
        proposed_memory_pointer_ids=(),
        proposed_artifact_pointer_ids=(),
        requested_descent_class="SUMMARY_ONLY",
        proposed_budget_id=budget.memory_descent_budget_id,
        required_access_policy_ids=(),
        reason_codes=(),
    )
    report = resolution.build_drs_resolution_report_v01(
        semantic_address=address,
        query=query,
        source_projections=(),
        source_records=records,
        query_evaluations=evaluations,
        eligible_candidates=candidates,
        ranked_candidate_ids=tuple(
            candidate.resolution_candidate_id for candidate in ranked
        ),
        selected_candidate_id=ranked[0].resolution_candidate_id,
        retrieval_plan=plan,
        memory_descent_result=None,
        root_shortcut_projection=None,
        reuse_certificate=None,
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
        "address": address,
        "query": query,
        "records": records,
        "evaluations": evaluations,
        "candidates": candidates,
        "ranked": ranked,
        "plan": plan,
        "report": report,
    }


def _b2_record_with_time(
    record: semantic.MeaningRecordV01,
    **changes: object,
) -> semantic.MeaningRecordV01:
    time_envelope = _reidentify(replace(record.time_envelope, **changes))
    return _reidentify(replace(record, time_envelope=time_envelope))


def _b2_action_history(
    *,
    lifecycle_state: str = "ROOT_AUTHORIZED",
    disposition: str = "RESERVED",
    terminal_receipt_ref: str | None = None,
) -> reuse.G2AActionHistoryBindingV01:
    return reuse.build_g2a_action_history_binding_v01(
        packet_id="acp_v02:g2b2_historical",
        registry_id="acp_v02:g2b2_registry",
        transition_history_sha256=_SHA_A,
        disposition_history_sha256=_SHA_B,
        lifecycle_state=lifecycle_state,
        disposition=disposition,
        reservation_owner_packet_id="acp_v02:g2b2_historical",
        terminal_receipt_ref=terminal_receipt_ref,
        current_status_validation_id="action-history-validation:g2b2",
        current_status_evaluated_at=200,
        current_status_evaluation_time_source=(
            "INJECTED_CURRENT_DECISION_TIME"
        ),
        reason_codes=("action_history_shortcut_forbidden",),
    )


def _b2_assert_blocked(
    evaluation: resolution.QueryEvaluationStateV01,
    *,
    state: str,
    first_reason: str,
) -> None:
    assert evaluation.eligible_for_ranking is False
    assert evaluation.query_state == state
    assert evaluation.reason_codes[0] == first_reason
    assert evaluation.creates_authority is False
    assert evaluation.creates_permission is False


def _b2_reidentified_report(
    report: resolution.DRSResolutionReportV01,
    **changes: object,
) -> resolution.DRSResolutionReportV01:
    return _reidentify(replace(report, **changes))


def _b2_ineligible_evaluation(
    evaluation: resolution.QueryEvaluationStateV01,
    *,
    ordinal: int,
    **changes: object,
) -> resolution.QueryEvaluationStateV01:
    return _reidentify(
        replace(
            evaluation,
            meaning_record_id=(
                "drsmeaning_v01:" + format(ordinal, "x")[-1] * 64
            ),
            query_state="BLOCKED_BY_SCOPE",
            scope_passed=False,
            eligible_for_ranking=False,
            reason_codes=("drs_address_scope_mismatch",),
            **changes,
        )
    )


def _b2_assert_ranking_error(
    expected: str,
    *,
    query: object,
    evaluations: object,
    candidates: object,
) -> None:
    with pytest.raises(ValueError, match=rf"^{expected}$"):
        resolution.rank_eligible_drs_candidates_v01(
            query=query,
            query_evaluations=evaluations,
            candidates=candidates,
        )


def _b2_report_forgery_matrix(
    fixture: dict[str, object],
) -> tuple[tuple[str, resolution.DRSResolutionReportV01], ...]:
    report = fixture["report"]
    assert isinstance(report, resolution.DRSResolutionReportV01)
    evaluations = report.query_evaluations
    candidates = report.eligible_candidates
    records = report.source_records
    changed_evaluation = _reidentify(
        replace(
            evaluations[0],
            policy_compatible=False,
            query_state="BLOCKED_BY_POLICY",
            eligible_for_ranking=False,
            reason_codes=("drs_policy_version_mismatch",),
        )
    )
    changed_reason = _reidentify(
        replace(
            evaluations[0],
            query_state="BLOCKED_BY_POLICY",
            eligible_for_ranking=False,
            reason_codes=("drs_schema_version_mismatch",),
        )
    )
    changed_state = _reidentify(
        replace(
            evaluations[0],
            query_state="STALE_CONTEXT_ONLY",
            eligible_for_ranking=False,
            reason_codes=("drs_query_mode_invalid_for_shortcut",),
        )
    )
    changed_freshness = _reidentify(
        replace(evaluations[0], current_freshness_units=8999)
    )
    rebound_candidate = _reidentify(
        replace(
            candidates[0],
            query_evaluation_id=evaluations[1].query_evaluation_id,
        )
    )
    pointer_plan = _reidentify(
        replace(
            report.retrieval_plan,
            proposed_memory_pointer_ids=("drsmem_v01:" + "a" * 64,),
        )
    )
    open_plan = _reidentify(
        replace(
            report.retrieval_plan,
            requested_descent_class="OPEN_ONE_ARTIFACT",
        )
    )
    nonzero_counter = _b2_reidentified_report(report, provider_calls=-1)
    return (
        (
            "changed_evaluation_boolean",
            _b2_reidentified_report(
                report,
                query_evaluations=(changed_evaluation,) + evaluations[1:],
            ),
        ),
        (
            "changed_evaluation_reason",
            _b2_reidentified_report(
                report,
                query_evaluations=(changed_reason,) + evaluations[1:],
            ),
        ),
        (
            "changed_query_state",
            _b2_reidentified_report(
                report,
                query_evaluations=(changed_state,) + evaluations[1:],
            ),
        ),
        (
            "changed_freshness",
            _b2_reidentified_report(
                report,
                query_evaluations=(changed_freshness,) + evaluations[1:],
            ),
        ),
        (
            "omitted_evaluation",
            _b2_reidentified_report(
                report,
                query_evaluations=evaluations[:-1],
            ),
        ),
        (
            "extra_evaluation",
            _b2_reidentified_report(
                report,
                query_evaluations=evaluations + (evaluations[0],),
            ),
        ),
        (
            "omitted_candidate",
            _b2_reidentified_report(
                report,
                eligible_candidates=candidates[:-1],
                ranked_candidate_ids=report.ranked_candidate_ids[:-1],
            ),
        ),
        (
            "extra_candidate",
            _b2_reidentified_report(
                report,
                eligible_candidates=candidates + (candidates[0],),
            ),
        ),
        (
            "candidate_rebound",
            _b2_reidentified_report(
                report,
                eligible_candidates=(rebound_candidate,) + candidates[1:],
                ranked_candidate_ids=(
                    rebound_candidate.resolution_candidate_id,
                )
                + report.ranked_candidate_ids[1:],
                selected_candidate_id=rebound_candidate.resolution_candidate_id,
            ),
        ),
        (
            "swapped_rank_order",
            _b2_reidentified_report(
                report,
                ranked_candidate_ids=(
                    report.ranked_candidate_ids[1],
                    report.ranked_candidate_ids[0],
                )
                + report.ranked_candidate_ids[2:],
                selected_candidate_id=report.ranked_candidate_ids[1],
            ),
        ),
        (
            "wrong_selected",
            _b2_reidentified_report(
                report,
                selected_candidate_id=report.ranked_candidate_ids[1],
            ),
        ),
        (
            "duplicate_bucket",
            _b2_reidentified_report(
                report,
                context_only_record_ids=(records[0].meaning_record_id,),
                blocked_record_ids=(records[0].meaning_record_id,),
            ),
        ),
        (
            "wrong_bucket",
            _b2_reidentified_report(
                report,
                historical_only_record_ids=(records[0].meaning_record_id,),
            ),
        ),
        (
            "changed_record_order",
            _b2_reidentified_report(
                report,
                source_records=(records[1], records[0]) + records[2:],
            ),
        ),
        (
            "changed_plan_order",
            _b2_reidentified_report(
                report,
                retrieval_plan=_reidentify(
                    replace(
                        report.retrieval_plan,
                        proposed_record_ids=(
                            report.retrieval_plan.proposed_record_ids[1],
                            report.retrieval_plan.proposed_record_ids[0],
                        )
                        + report.retrieval_plan.proposed_record_ids[2:],
                    )
                ),
            ),
        ),
        (
            "non_summary_plan",
            _b2_reidentified_report(report, retrieval_plan=open_plan),
        ),
        (
            "pointer_plan",
            _b2_reidentified_report(report, retrieval_plan=pointer_plan),
        ),
        ("forged_counter", nonzero_counter),
        (
            "pass_over_mismatch",
            _b2_reidentified_report(
                report,
                query_evaluations=(changed_evaluation,) + evaluations[1:],
                final_status="PASS",
                reason_codes=(),
            ),
        ),
    )


def test_g2b_half_open_validity_boundary_rejects_exact_valid_to() -> None:
    address = _b2_address()
    query = _b2_query(address=address, as_of=200, evaluation_time=200)
    baseline = _b2_record(address=address)
    at_valid_from_query = _b2_query(
        address=address,
        as_of=50,
        evaluation_time=50,
    )
    at_valid_from_record = _b2_record_with_time(
        baseline,
        pt_created_at=50,
        kt_as_of=50,
        et_observed_at=50,
        ct_context_anchor=50,
    )
    assert _b2_evaluate(
        at_valid_from_record,
        at_valid_from_query,
    ).validity_interval_passed is True
    valid = _b2_evaluate(
        _b2_record_with_time(baseline, valid_to=201),
        query,
    )
    assert valid.eligible_for_ranking is True
    exact_boundary = _b2_evaluate(
        _b2_record_with_time(baseline, valid_to=200),
        query,
    )
    _b2_assert_blocked(
        exact_boundary,
        state="BLOCKED_BY_TIME",
        first_reason="drs_time_validity_interval_invalid",
    )


def test_g2b_half_open_ttl_boundary_rejects_exact_expiry() -> None:
    address = _b2_address()
    query = _b2_query(address=address, as_of=200, evaluation_time=200)
    baseline = _b2_record(address=address)
    assert _b2_evaluate(
        _b2_record_with_time(
            baseline,
            pt_created_at=100,
            ttl_seconds=101,
        ),
        query,
    ).eligible_for_ranking is True
    expired = _b2_evaluate(
        _b2_record_with_time(
            baseline,
            pt_created_at=100,
            ttl_seconds=100,
        ),
        query,
    )
    _b2_assert_blocked(
        expired,
        state="BLOCKED_BY_TIME",
        first_reason="drs_time_ttl_expired",
    )
    zero_age_record = _b2_record_with_time(
        baseline,
        pt_created_at=200,
        kt_as_of=200,
        et_observed_at=200,
        ct_context_anchor=200,
    )
    zero_age_query = _b2_query(
        address=address,
        max_age_seconds=0,
    )
    zero_age = _b2_evaluate(zero_age_record, zero_age_query)
    assert zero_age.current_freshness_units == 10000
    assert zero_age.eligible_for_ranking is True
    positive_age = _b2_evaluate(baseline, zero_age_query)
    assert positive_age.current_freshness_units == 0
    _b2_assert_blocked(
        positive_age,
        state="BLOCKED_BY_TIME",
        first_reason="drs_temporal_hard_gate_failed",
    )
    max_age_minus_one = _b2_evaluate(
        baseline,
        _b2_query(address=address, max_age_seconds=101),
    )
    assert max_age_minus_one.current_freshness_units == 99
    assert max_age_minus_one.eligible_for_ranking is True
    exact_max_age = _b2_evaluate(
        baseline,
        _b2_query(address=address, max_age_seconds=100),
    )
    assert exact_max_age.current_freshness_units == 0
    _b2_assert_blocked(
        exact_max_age,
        state="BLOCKED_BY_TIME",
        first_reason="drs_temporal_hard_gate_failed",
    )
    future_cases = (
        ("pt_created_at", 201),
        ("kt_as_of", 201),
        ("et_observed_at", 201),
        ("ct_context_anchor", 201),
    )
    for field_name, value in future_cases:
        future_record = _b2_record_with_time(
            baseline,
            **{field_name: value},
        )
        future_evaluation = _b2_evaluate(future_record, query)
        if field_name == "pt_created_at":
            assert future_evaluation.current_freshness_units == 0
        _b2_assert_blocked(
            future_evaluation,
            state="BLOCKED_BY_TIME",
            first_reason="drs_temporal_hard_gate_failed",
        )
    for invalid in (True, 100.0, Decimal("100"), "100"):
        invalid_time = replace(
            baseline.time_envelope,
            pt_created_at=invalid,
        )
        invalid_record = replace(baseline, time_envelope=invalid_time)
        with pytest.raises(
            ValueError,
            match=r"^drs_exact_type_or_identity_invalid$",
        ):
            _b2_evaluate(invalid_record, query)

    class _IntSubclass(int):
        pass

    subclass_time = replace(
        baseline.time_envelope,
        pt_created_at=_IntSubclass(100),
    )
    subclass_record = replace(baseline, time_envelope=subclass_time)
    with pytest.raises(
        ValueError,
        match=r"^drs_exact_type_or_identity_invalid$",
    ):
        _b2_evaluate(subclass_record, query)


def test_g2b_missing_required_time_axis_fails_closed() -> None:
    address = _b2_address()
    record = _b2_record(address=address)
    for missing in _B2_ALL_TIME_AXES:
        axes = tuple(axis for axis in _B2_ALL_TIME_AXES if axis != missing)
        query = _b2_query(address=address, required_time_axes=axes)
        evaluation = _b2_evaluate(record, query)
        _b2_assert_blocked(
            evaluation,
            state="BLOCKED_BY_TIME",
            first_reason="drs_time_axis_missing",
        )
    extended_axes = (
        ("SOURCE_OBSERVED", "source_observed_at", "as_of"),
        ("SOURCE_REPORTED", "source_reported_at", "as_of"),
        ("SYSTEM_INGESTED", "system_ingested_at", "evaluation_time"),
        ("SYSTEM_VERIFIED", "system_verified_at", "evaluation_time"),
    )
    observed = {}
    for axis, field_name, boundary_name in extended_axes:
        query = _b2_query(
            address=address,
            required_time_axes=_B2_ALL_TIME_AXES + (axis,),
            required_evidence_classes=(),
        )
        boundary = getattr(query, boundary_name)
        boundary_evaluation = _b2_evaluate(
            _b2_record_with_time(record, **{field_name: boundary}),
            query,
        )
        future_evaluation = _b2_evaluate(
            _b2_record_with_time(record, **{field_name: boundary + 1}),
            query,
        )
        unrequested_evaluation = _b2_evaluate(
            _b2_record_with_time(record, **{field_name: boundary + 1}),
            _b2_query(address=address, required_evidence_classes=()),
        )
        observed[axis] = (
            (
                boundary_evaluation.required_time_axes_passed,
                boundary_evaluation.temporal_hard_gate_passed,
                boundary_evaluation.eligible_for_ranking,
            ),
            (
                future_evaluation.required_time_axes_passed,
                future_evaluation.temporal_hard_gate_passed,
                future_evaluation.eligible_for_ranking,
                future_evaluation.query_state,
                future_evaluation.reason_codes,
            ),
            (
                unrequested_evaluation.required_time_axes_passed,
                unrequested_evaluation.temporal_hard_gate_passed,
                unrequested_evaluation.eligible_for_ranking,
            ),
        )
    assert observed == {
        axis: (
            (True, True, True),
            (
                False,
                False,
                False,
                "BLOCKED_BY_TIME",
                ("drs_temporal_hard_gate_failed",),
            ),
            (True, True, True),
        )
        for axis, _, _ in extended_axes
    }, repr(observed)


def test_g2b_query_mode_controls_temporal_validity_and_shortcut_eligibility() -> None:
    address = _b2_address()
    observed = {}
    for mode, source, axes in _B2_MODE_PROFILE:
        intents = (
            ("CONTEXT", ("CONTEXT_ONLY",)),
            (
                "INFORMATIONAL_SHORTCUT_CONSIDERATION",
                ("ANSWER_SHORTCUT",),
            ),
            ("WARNING_LOOKUP", ("CONTEXT_ONLY",)),
            ("HISTORY_INSPECTION", ("CONTEXT_ONLY",)),
        )
        for reuse_intent, reuse_classes in intents:
            record = _b2_record(
                address=address,
                reuse_policy_class=reuse_classes[0],
            )
            query = _b2_query(
                address=address,
                query_mode=mode,
                evaluation_time_source=source,
                required_time_axes=axes,
                reuse_intent=reuse_intent,
                requested_reuse_classes=reuse_classes,
                required_evidence_classes=(),
            )
            evaluation = _b2_evaluate(record, query)
            observed[(mode, reuse_intent)] = (
                evaluation.query_state,
                evaluation.eligible_for_ranking,
            )
    assert observed[
        ("DIRECT_REUSE_CANDIDATE", "INFORMATIONAL_SHORTCUT_CONSIDERATION")
    ] == ("FRESH_CANDIDATE", True)
    assert observed[("CURRENT_DECISION", "CONTEXT")] == (
        "FRESH_CANDIDATE",
        True,
    )
    assert all(
        eligible is False
        for (mode, _), (_, eligible) in observed.items()
        if mode not in {"CURRENT_DECISION", "DIRECT_REUSE_CANDIDATE"}
    )
    for mode, expected_source, axes in _B2_MODE_PROFILE:
        wrong_source = next(
            source
            for source in (
                "INJECTED_CURRENT_DECISION_TIME",
                "RECORDED_HISTORICAL_AS_OF_TIME",
                "RECORDED_AUDIT_REPLAY_TIME",
                "INJECTED_ANALYSIS_TIME",
            )
            if source != expected_source
        )
        query = _b2_query(
            address=address,
            query_mode=mode,
            evaluation_time_source=wrong_source,
            required_time_axes=axes,
            required_evidence_classes=(),
        )
        _b2_assert_blocked(
            _b2_evaluate(record, query),
            state="BLOCKED_BY_TIME",
            first_reason="drs_temporal_hard_gate_failed",
        )
    disabled_classes = tuple(
        reuse_class
        for reuse_class in resolution.DRS_REUSE_CLASSES_V01
        if reuse_class not in resolution.DRS_ENABLED_REUSE_CLASSES_V01
    )
    disabled_observed = {}
    for mode, source, axes in _B2_MODE_PROFILE:
        for disabled_class in disabled_classes:
            standalone = _b2_evaluate(
                _b2_record(
                    address=address,
                    reuse_policy_class=disabled_class,
                ),
                _b2_query(
                    address=address,
                    query_mode=mode,
                    evaluation_time_source=source,
                    required_time_axes=axes,
                    reuse_intent="CONTEXT",
                    requested_reuse_classes=(disabled_class,),
                    required_evidence_classes=(),
                ),
            )
            mixed = _b2_evaluate(
                _b2_record(address=address),
                _b2_query(
                    address=address,
                    query_mode=mode,
                    evaluation_time_source=source,
                    required_time_axes=axes,
                    requested_reuse_classes=(
                        "ANSWER_SHORTCUT",
                        disabled_class,
                    ),
                    required_evidence_classes=(),
                ),
            )
            disabled_record = _b2_evaluate(
                _b2_record(
                    address=address,
                    reuse_policy_class=disabled_class,
                ),
                _b2_query(
                    address=address,
                    query_mode=mode,
                    evaluation_time_source=source,
                    required_time_axes=axes,
                    reuse_intent="CONTEXT",
                    requested_reuse_classes=("CONTEXT_ONLY",),
                    required_evidence_classes=(),
                ),
            )
            disabled_observed[(mode, disabled_class)] = tuple(
                (
                    evaluation.query_state,
                    evaluation.eligible_for_ranking,
                    evaluation.reason_codes,
                )
                for evaluation in (
                    standalone,
                    mixed,
                    disabled_record,
                )
            )
    expected_disabled = (
        "BLOCKED_BY_POLICY",
        False,
        ("drs_reuse_class_disabled",),
    )
    assert disabled_classes == (
        "ROUTE_SHORTCUT",
        "SEALED_REPLAY_SHORTCUT",
        "PROTOCOL_PREPARATION_SHORTCUT",
        "ACTION_SHORTCUT_NOT_ENABLED_IN_REFERENCE_KERNEL",
    )
    assert disabled_observed == {
        key: (
            expected_disabled,
            expected_disabled,
            expected_disabled,
        )
        for key in disabled_observed
    }, repr(disabled_observed)


def test_g2b_hard_eligibility_precedes_ranking() -> None:
    fixture = _b2_positive_fixture()
    query = fixture["query"]
    record = fixture["records"][0]
    assert isinstance(query, resolution.DRSTemporalQueryV01)
    assert isinstance(record, semantic.MeaningRecordV01)
    bad_record = _reidentify(
        replace(
            record,
            policy_version="policy_v02",
            schema_versions=("v0.2",),
            conflict_hints=("CONFLICT_PRESENT",),
        )
    )
    evaluation = _b2_evaluate(bad_record, query)
    assert evaluation.reason_codes[:3] == (
        "drs_policy_version_mismatch",
        "drs_schema_version_mismatch",
        "drs_required_evidence_missing",
    )
    assert evaluation.reason_codes.index(
        "drs_conflict_blocked"
    ) > evaluation.reason_codes.index("drs_required_evidence_missing")
    independent_cases = (
        (
            _reidentify(
                replace(
                    record,
                    authority_envelope=_b2_authority(
                        authority_class="UNTRUSTED_SEMANTIC_DRAFT",
                        root_acceptance_state="UNREVIEWED",
                    ),
                )
            ),
            "drs_provenance_invalid",
        ),
        (
            _reidentify(
                replace(
                    record,
                    persistent_lifecycle_state="ARCHIVED",
                )
            ),
            "drs_persistent_lifecycle_blocked",
        ),
        (
            _reidentify(
                replace(
                    record,
                    source_reference_ids=("permission:g2b2:stale",),
                )
            ),
            "drs_permission_boundary_failed",
        ),
    )
    for mutated, expected_reason in independent_cases:
        restricted_query = _b2_query(
            address=record.semantic_address,
            required_evidence_classes=(),
        )
        blocked = _b2_evaluate(mutated, restricted_query)
        assert expected_reason in blocked.reason_codes
    wrong_scope_query = _b2_query(
        address=record.semantic_address,
        required_evidence_classes=(),
        scope_fingerprint=_SHA_D,
    )
    _b2_assert_blocked(
        _b2_evaluate(record, wrong_scope_query),
        state="BLOCKED_BY_SCOPE",
        first_reason="drs_address_scope_mismatch",
    )


def test_g2b_ineligible_highest_score_candidate_cannot_win() -> None:
    fixture = _b2_positive_fixture()
    query = fixture["query"]
    evaluations = fixture["evaluations"]
    candidates = fixture["candidates"]
    assert isinstance(query, resolution.DRSTemporalQueryV01)
    assert isinstance(evaluations, tuple)
    assert isinstance(candidates, tuple)
    ineligible = _reidentify(
        replace(
            evaluations[0],
            query_state="BLOCKED_BY_POLICY",
            policy_compatible=False,
            eligible_for_ranking=False,
            reason_codes=("drs_policy_version_mismatch",),
        )
    )
    with pytest.raises(
        ValueError,
        match=r"^drs_ineligible_candidate_selected$",
    ):
        resolution.rank_eligible_drs_candidates_v01(
            query=query,
            query_evaluations=(ineligible,) + evaluations[1:],
            candidates=candidates,
        )
    assert resolution.rank_eligible_drs_candidates_v01(
        query=query,
        query_evaluations=(),
        candidates=(),
    ) == ()
    assert resolution.rank_eligible_drs_candidates_v01(
        query=query,
        query_evaluations=(evaluations[0],),
        candidates=(candidates[0],),
    ) == (candidates[0],)
    _b2_assert_ranking_error(
        "drs_ranking_tie_break_invalid",
        query=query,
        evaluations=evaluations + (evaluations[0],),
        candidates=candidates,
    )
    _b2_assert_ranking_error(
        "drs_ranking_tie_break_invalid",
        query=query,
        evaluations=evaluations,
        candidates=candidates + (candidates[0],),
    )
    _b2_assert_ranking_error(
        "drs_ranking_tie_break_invalid",
        query=query,
        evaluations=evaluations,
        candidates=candidates[:-1],
    )
    unknown_candidate = _reidentify(
        replace(
            candidates[0],
            meaning_record_id="drsmeaning_v01:" + "f" * 64,
        )
    )
    _b2_assert_ranking_error(
        "drs_ineligible_candidate_selected",
        query=query,
        evaluations=evaluations,
        candidates=(unknown_candidate,) + candidates[1:],
    )
    binding_forgeries = (
        replace(candidates[0], query_id="drsquery_v01:" + "f" * 64),
        replace(
            candidates[0],
            query_evaluation_id=evaluations[1].query_evaluation_id,
        ),
        replace(candidates[0], source_history_hash=_SHA_E),
        replace(
            candidates[0],
            action_history_binding_id="drsg2ahistory_v01:" + "f" * 64,
        ),
        replace(
            candidates[0],
            freshness_units=evaluations[0].current_freshness_units - 1,
            total_score_units=candidates[0].total_score_units - 2000,
        ),
    )
    for forged in binding_forgeries:
        reidentified = _reidentify(forged)
        _b2_assert_ranking_error(
            "drs_ineligible_candidate_selected",
            query=query,
            evaluations=evaluations,
            candidates=(reidentified,) + candidates[1:],
        )
    foreign_evaluations = (
        _b2_ineligible_evaluation(
            evaluations[0],
            ordinal=10,
            query_id="drsquery_v01:" + "a" * 64,
        ),
        _b2_ineligible_evaluation(
            evaluations[0],
            ordinal=11,
            semantic_address_id="drsaddr_v01:" + "b" * 64,
        ),
        _b2_ineligible_evaluation(
            evaluations[0],
            ordinal=12,
            query_id="drsquery_v01:" + "c" * 64,
            semantic_address_id="drsaddr_v01:" + "d" * 64,
        ),
        _b2_ineligible_evaluation(
            evaluations[0],
            ordinal=13,
            evaluated_at=query.evaluation_time + 1,
        ),
        _b2_ineligible_evaluation(
            evaluations[0],
            ordinal=14,
            evaluation_time_source="INJECTED_ANALYSIS_TIME",
        ),
        _b2_ineligible_evaluation(
            evaluations[0],
            ordinal=15,
            evaluated_at=query.evaluation_time + 1,
            evaluation_time_source="INJECTED_ANALYSIS_TIME",
        ),
    )
    foreign_acceptance = []
    for foreign in foreign_evaluations:
        try:
            ranked = resolution.rank_eligible_drs_candidates_v01(
                query=query,
                query_evaluations=evaluations + (foreign,),
                candidates=candidates,
            )
        except ValueError as exc:
            foreign_acceptance.append((False, str(exc)))
        else:
            foreign_acceptance.append((ranked == fixture["ranked"], None))
    assert foreign_acceptance == [
        (False, "drs_ranking_tie_break_invalid")
        for _ in foreign_evaluations
    ], repr(foreign_acceptance)
    query_local_ineligible = _b2_ineligible_evaluation(
        evaluations[0],
        ordinal=9,
    )
    assert resolution.rank_eligible_drs_candidates_v01(
        query=query,
        query_evaluations=evaluations + (query_local_ineligible,),
        candidates=candidates,
    ) == fixture["ranked"]


def test_g2b_ranking_tie_break_ends_with_canonical_candidate_id() -> None:
    fixture = _b2_positive_fixture()
    ranked = fixture["ranked"]
    assert isinstance(ranked, tuple)
    assert ranked[1].total_score_units == ranked[2].total_score_units
    assert ranked[1].resolution_candidate_id < ranked[2].resolution_candidate_id
    assert tuple(
        candidate.resolution_candidate_id for candidate in ranked[1:]
    ) == tuple(
        sorted(
            candidate.resolution_candidate_id
            for candidate in ranked[1:]
        )
    )
    evaluation = fixture["evaluations"][0]
    query = fixture["query"]
    record = fixture["records"][0]
    minimum = resolution.build_resolution_candidate_v01(
        query_id=query.query_id,
        semantic_address_id=query.semantic_address_id,
        meaning_record_id=record.meaning_record_id,
        query_evaluation_id=evaluation.query_evaluation_id,
        safe_summary=record.safe_summary,
        evidence_ref_ids=record.source_reference_ids,
        source_history_hash=evaluation.source_history_hash,
        action_history_binding_id=None,
        semantic_similarity_units=0,
        freshness_units=evaluation.current_freshness_units,
        source_authority_prior_units=0,
        lineage_proximity_units=0,
        historical_utility_units=0,
        gt_advisory_prior_units=0,
        conflict_penalty_units=10000,
        risk_penalty_units=10000,
        retrieval_cost_units=10000,
    )
    assert minimum.total_score_units < 0
    maximum = resolution.build_resolution_candidate_v01(
        query_id=query.query_id,
        semantic_address_id=query.semantic_address_id,
        meaning_record_id=record.meaning_record_id,
        query_evaluation_id=evaluation.query_evaluation_id,
        safe_summary=record.safe_summary,
        evidence_ref_ids=record.source_reference_ids,
        source_history_hash=evaluation.source_history_hash,
        action_history_binding_id=None,
        semantic_similarity_units=10000,
        freshness_units=evaluation.current_freshness_units,
        source_authority_prior_units=10000,
        lineage_proximity_units=10000,
        historical_utility_units=10000,
        gt_advisory_prior_units=10000,
        conflict_penalty_units=0,
        risk_penalty_units=0,
        retrieval_cost_units=0,
    )
    assert maximum.total_score_units > 0


def test_g2b_gt_advisory_score_creates_no_authority() -> None:
    fixture = _b2_positive_fixture()
    candidate = _b2_candidate(
        fixture["evaluations"][0],
        fixture["query"],
        fixture["records"][0],
        semantic_similarity_units=0,
        gt_advisory_prior_units=10000,
    )
    assert candidate.creates_authority is False
    assert candidate.creates_permission is False
    assert candidate.creates_final_output is False


def test_g2b_semantic_similarity_creates_no_authority() -> None:
    fixture = _b2_positive_fixture()
    candidate = _b2_candidate(
        fixture["evaluations"][0],
        fixture["query"],
        fixture["records"][0],
        semantic_similarity_units=10000,
        gt_advisory_prior_units=0,
    )
    assert candidate.creates_authority is False
    assert candidate.creates_permission is False


def test_g2b_freshness_creates_no_authority() -> None:
    fixture = _b2_positive_fixture()
    evaluation = fixture["evaluations"][0]
    assert evaluation.current_freshness_units == 9000
    assert evaluation.creates_authority is False
    assert evaluation.creates_permission is False


def test_g2b_forbidden_change_blocks_reuse() -> None:
    address = _b2_address()
    query = _b2_query(address=address)
    record = _b2_record(
        address=address,
        risk_hints=("POLICY_CHANGED",),
    )
    _b2_assert_blocked(
        _b2_evaluate(record, query),
        state="BLOCKED_BY_FORBIDDEN_CHANGE",
        first_reason="drs_forbidden_change_detected",
    )


def test_g2b_missing_required_evidence_blocks_reuse() -> None:
    address = _b2_address()
    query = _b2_query(
        address=address,
        required_evidence_classes=_B2_EVIDENCE_CLASSES
        + ("UNAVAILABLE_EVIDENCE",),
    )
    _b2_assert_blocked(
        _b2_evaluate(_b2_record(address=address), query),
        state="BLOCKED_BY_REQUIRED_EVIDENCE",
        first_reason="drs_required_evidence_missing",
    )


def test_g2b_policy_version_mismatch_blocks_reuse() -> None:
    address = _b2_address()
    query = _b2_query(
        address=address,
        required_evidence_classes=(),
    )
    record = _b2_record(address=address, policy_version="policy_v02")
    _b2_assert_blocked(
        _b2_evaluate(record, query),
        state="BLOCKED_BY_POLICY",
        first_reason="drs_policy_version_mismatch",
    )


def test_g2b_schema_version_mismatch_blocks_reuse() -> None:
    address = _b2_address()
    query = _b2_query(
        address=address,
        required_evidence_classes=(),
    )
    record = _b2_record(address=address, schema_versions=("v0.2",))
    _b2_assert_blocked(
        _b2_evaluate(record, query),
        state="BLOCKED_BY_POLICY",
        first_reason="drs_schema_version_mismatch",
    )


def test_g2b_conflict_blocks_reuse() -> None:
    address = _b2_address()
    query = _b2_query(
        address=address,
        required_evidence_classes=(),
    )
    record = _b2_record(
        address=address,
        conflict_hints=("CONFLICT_PRESENT",),
    )
    _b2_assert_blocked(
        _b2_evaluate(record, query),
        state="BLOCKED_BY_CONFLICT",
        first_reason="drs_conflict_blocked",
    )


def test_g2b_quarantined_record_blocks_reuse() -> None:
    address = _b2_address()
    query = _b2_query(
        address=address,
        required_evidence_classes=(),
    )
    record = _b2_record(
        address=address,
        persistent_lifecycle_state="QUARANTINED",
    )
    _b2_assert_blocked(
        _b2_evaluate(record, query),
        state="BLOCKED_BY_QUARANTINE",
        first_reason="drs_quarantine_blocked",
    )


def test_g2b_deadend_record_blocks_reuse() -> None:
    address = _b2_address()
    query = _b2_query(
        address=address,
        required_evidence_classes=(),
    )
    record = _b2_record(
        address=address,
        persistent_lifecycle_state="DEADEND",
    )
    _b2_assert_blocked(
        _b2_evaluate(record, query),
        state="BLOCKED_BY_DEADEND",
        first_reason="drs_deadend_blocked",
    )


def test_g2b_action_like_request_cannot_take_answer_shortcut() -> None:
    address = _b2_address(intent_class="action_request")
    query = _b2_query(
        address=address,
        required_evidence_classes=(),
    )
    record = _b2_record(address=address)
    _b2_assert_blocked(
        _b2_evaluate(record, query),
        state="BLOCKED_BY_ACTION_INTENT",
        first_reason="drs_action_intent_shortcut_forbidden",
    )


def test_g2b_prior_root_final_cannot_authorize_shortcut() -> None:
    address = _b2_address()
    query = _b2_query(
        address=address,
        required_evidence_classes=(),
    )
    record = _b2_record(
        address=address,
        authority=_b2_authority(
            authority_class="ROOT_FINAL_REFERENCE",
            root_acceptance_state="ACCEPTED_WORK",
        ),
    )
    _b2_assert_blocked(
        _b2_evaluate(record, query),
        state="BLOCKED_BY_PROVENANCE",
        first_reason="drs_prior_root_final_shortcut_forbidden",
    )
    action_history_record = _b2_record(
        address=address,
        authority=_b2_authority(
            authority_class="ACTION_HISTORY_REFERENCE",
            root_acceptance_state="UNREVIEWED",
        ),
    )
    _b2_assert_blocked(
        _b2_evaluate(action_history_record, query),
        state="BLOCKED_BY_ACTION_HISTORY",
        first_reason="drs_action_history_shortcut_forbidden",
    )


def test_g2b_prior_receipt_cannot_authorize_shortcut() -> None:
    address = _b2_address()
    query = _b2_query(address=address)
    evaluation = _b2_evaluate(
        _b2_record(address=address),
        query,
        action_history_binding=_b2_action_history(
            terminal_receipt_ref="receipt:g2b2:historical",
        ),
    )
    _b2_assert_blocked(
        evaluation,
        state="BLOCKED_BY_ACTION_HISTORY",
        first_reason="drs_prior_receipt_shortcut_forbidden",
    )
    malformed = _reidentify(
        replace(
            _b2_action_history(),
            terminal_receipt_ref="receipt with whitespace",
        )
    )
    with pytest.raises(
        ValueError,
        match=r"^drs_exact_type_or_identity_invalid$",
    ):
        _b2_evaluate(
            _b2_record(address=address),
            query,
            action_history_binding=malformed,
        )


def test_g2b_expired_action_packet_cannot_authorize_shortcut() -> None:
    address = _b2_address()
    query = _b2_query(address=address)
    evaluation = _b2_evaluate(
        _b2_record(address=address),
        query,
        action_history_binding=_b2_action_history(
            lifecycle_state="EXPIRED",
        ),
    )
    _b2_assert_blocked(
        evaluation,
        state="BLOCKED_BY_ACTION_HISTORY",
        first_reason="drs_action_history_expired",
    )


def test_g2b_revoked_action_packet_cannot_authorize_shortcut() -> None:
    address = _b2_address()
    query = _b2_query(address=address)
    evaluation = _b2_evaluate(
        _b2_record(address=address),
        query,
        action_history_binding=_b2_action_history(
            lifecycle_state="REVOKED",
        ),
    )
    _b2_assert_blocked(
        evaluation,
        state="BLOCKED_BY_ACTION_HISTORY",
        first_reason="drs_action_history_revoked",
    )


def test_g2b_superseded_action_packet_cannot_authorize_shortcut() -> None:
    address = _b2_address()
    query = _b2_query(address=address)
    evaluation = _b2_evaluate(
        _b2_record(address=address),
        query,
        action_history_binding=_b2_action_history(
            lifecycle_state="SUPERSEDED",
        ),
    )
    _b2_assert_blocked(
        evaluation,
        state="BLOCKED_BY_ACTION_HISTORY",
        first_reason="drs_action_history_superseded",
    )


def test_g2b_blocked_action_packet_cannot_authorize_shortcut() -> None:
    address = _b2_address()
    query = _b2_query(address=address)
    for lifecycle_state in ("BLOCKED", "FAILED"):
        evaluation = _b2_evaluate(
            _b2_record(address=address),
            query,
            action_history_binding=_b2_action_history(
                lifecycle_state=lifecycle_state,
            ),
        )
        _b2_assert_blocked(
            evaluation,
            state="BLOCKED_BY_ACTION_HISTORY",
            first_reason="drs_action_history_blocked",
        )


def test_g2b_consumed_action_history_cannot_authorize_shortcut() -> None:
    address = _b2_address()
    query = _b2_query(address=address)
    evaluation = _b2_evaluate(
        _b2_record(address=address),
        query,
        action_history_binding=_b2_action_history(
            disposition="CONSUMED",
        ),
    )
    _b2_assert_blocked(
        evaluation,
        state="BLOCKED_BY_ACTION_HISTORY",
        first_reason="drs_action_history_consumed",
    )


def test_g2b_uncertain_closed_history_cannot_authorize_shortcut() -> None:
    address = _b2_address()
    query = _b2_query(address=address)
    evaluation = _b2_evaluate(
        _b2_record(address=address),
        query,
        action_history_binding=_b2_action_history(
            disposition="UNCERTAIN_CLOSED",
        ),
    )
    _b2_assert_blocked(
        evaluation,
        state="BLOCKED_BY_ACTION_HISTORY",
        first_reason="drs_action_history_uncertain_closed",
    )


def test_g2b_root_remains_final_authority() -> None:
    fixture = _b2_positive_fixture()
    report = fixture["report"]
    assert report.final_status == "PASS"
    assert report.memory_descent_result is None
    assert report.root_shortcut_projection is None
    assert report.reuse_certificate is None
    assert report.retrieval_plan.executes_read is False
    assert all(
        candidate.creates_authority is False
        and candidate.creates_permission is False
        and candidate.creates_final_output is False
        for candidate in report.eligible_candidates
    )
    first_evaluation = fixture["evaluations"][0]
    assert {
        "query_evaluation_id": first_evaluation.query_evaluation_id,
        "candidate_ids": tuple(
            candidate.resolution_candidate_id
            for candidate in fixture["candidates"]
        ),
        "ranked_candidate_ids": tuple(
            candidate.resolution_candidate_id
            for candidate in fixture["ranked"]
        ),
        "selected_candidate_id": report.selected_candidate_id,
        "observed_evidence_fingerprint": (
            first_evaluation.observed_evidence_fingerprint
        ),
        "checked_dependency_fingerprint": (
            first_evaluation.checked_dependency_fingerprint
        ),
        "source_history_hash": first_evaluation.source_history_hash,
        "report_id": report.report_id,
    } == _B2_IDENTITY_VECTORS
    report_forgeries = _b2_report_forgery_matrix(fixture)
    observed = {
        label: resolution.validate_drs_resolution_report_v01(forgery)
        for label, forgery in report_forgeries
    }
    assert all(result[0] is False for result in observed.values()), repr(
        observed
    )
    before = (
        semantic.semantic_address_to_plain_data_v01(fixture["address"]),
        resolution.drs_temporal_query_to_plain_data_v01(fixture["query"]),
        tuple(
            semantic.meaning_record_to_plain_data_v01(record)
            for record in fixture["records"]
        ),
    )
    _b2_positive_fixture()
    after = (
        semantic.semantic_address_to_plain_data_v01(fixture["address"]),
        resolution.drs_temporal_query_to_plain_data_v01(fixture["query"]),
        tuple(
            semantic.meaning_record_to_plain_data_v01(record)
            for record in fixture["records"]
        ),
    )
    assert canonical_json_bytes_v01(before) == canonical_json_bytes_v01(after)

    class _QuerySubclass(resolution.DRSTemporalQueryV01):
        pass

    class _TupleSubclass(tuple):
        pass

    query_subclass = _QuerySubclass(**fixture["query"].__dict__)
    with pytest.raises(
        ValueError,
        match=r"^drs_exact_type_or_identity_invalid$",
    ):
        resolution.evaluate_drs_candidate_v01(
            semantic_address=fixture["address"],
            query=query_subclass,
            meaning_record=fixture["records"][0],
        )
    _b2_assert_ranking_error(
        "drs_exact_type_or_identity_invalid",
        query=fixture["query"],
        evaluations=_TupleSubclass(fixture["evaluations"]),
        candidates=fixture["candidates"],
    )
    _b2_assert_ranking_error(
        "drs_exact_type_or_identity_invalid",
        query=fixture["query"],
        evaluations=fixture["evaluations"],
        candidates=_TupleSubclass(fixture["candidates"]),
    )
    pickled_query = pickle.loads(pickle.dumps(fixture["query"]))
    assert (
        resolution.validate_drs_temporal_query_v01(pickled_query)
        == (True, ())
    )
    b4_fixture = _b4_fixture()
    assert _b4_validate(b4_fixture) == (True, ())
    assert b4_fixture["projection"].creates_authority is False
    assert b4_fixture["certificate"].creates_authority is False
    assert b4_fixture["certificate"].creates_permission is False
    assert b4_fixture["certificate"].creates_final_output is False


_B3_DESCENT_CLASSES = (
    "SUMMARY_ONLY",
    "OPEN_ONE_ARTIFACT",
    "OPEN_LINEAGE_NEIGHBORHOOD",
    "OPEN_CONFLICT_SET",
    "OPEN_DEADEND_PROOF",
    "OPEN_FULL_TRACE",
)
_B3_ROOT_BINDING_DOMAIN = (
    "hedgehog:drs:memory_descent_root_result_binding:v01"
)
_B3_ROOT_PREDICATE = "approve_controlled_memory_descent_plan_v01"
_B3_CLASS_APPROVALS = (
    (
        "SUMMARY_ONLY",
        ("anchor", "neighbor"),
        ("summary",),
        (),
    ),
    (
        "OPEN_ONE_ARTIFACT",
        ("anchor",),
        (),
        ("artifact",),
    ),
    (
        "OPEN_LINEAGE_NEIGHBORHOOD",
        ("anchor", "neighbor", "conflict"),
        ("summary", "lineage"),
        (),
    ),
    (
        "OPEN_CONFLICT_SET",
        ("anchor", "conflict"),
        ("conflict",),
        (),
    ),
    (
        "OPEN_DEADEND_PROOF",
        ("anchor", "deadend"),
        ("deadend",),
        (),
    ),
    (
        "OPEN_FULL_TRACE",
        ("anchor", "neighbor", "conflict", "deadend"),
        ("summary", "lineage", "conflict", "deadend"),
        ("artifact",),
    ),
)
_B3_NARROWING = (
    ("SUMMARY_ONLY", ("SUMMARY_ONLY",)),
    ("OPEN_ONE_ARTIFACT", ("OPEN_ONE_ARTIFACT", "SUMMARY_ONLY")),
    (
        "OPEN_LINEAGE_NEIGHBORHOOD",
        ("OPEN_LINEAGE_NEIGHBORHOOD", "SUMMARY_ONLY"),
    ),
    ("OPEN_CONFLICT_SET", ("OPEN_CONFLICT_SET", "SUMMARY_ONLY")),
    ("OPEN_DEADEND_PROOF", ("OPEN_DEADEND_PROOF", "SUMMARY_ONLY")),
    ("OPEN_FULL_TRACE", _B3_DESCENT_CLASSES),
)
_B3_IDENTITY_VECTORS = {
    "proposed_budget_id": (
        "drsbudget_v01:"
        "ac854beda1471218b53f91712054ac033d634b4778e48756c260e2453ecbf7b4"
    ),
    "retrieval_plan_id": (
        "drsplan_v01:"
        "668b1900a8c3df7661119b4a5df1b71072718933b248e3c6b1f8b6413f82406a"
    ),
    "root_kernel_id": (
        "6cbe784404adaf78863830a3dd1cb67d1baaa1c3d46296c633018c715c522235"
    ),
    "root_input_id": (
        "1e8c1ba880665c10a59b1a8e479bfe0a50dac8dff1282e6b813397d772f78614"
    ),
    "root_result_id": (
        "db753fd76d44a0d7690322223fbd4ebf6f7e9f6434f208d89b1bf4f930d77e01"
    ),
    "root_result_binding_hash": (
        "8babadd4b1f7e34d9745a2941d53a5203bcddf580f099be3b539e705d94aadea"
    ),
    "summary_request_id": (
        "drsdescentreq_v01:"
        "b38fcc2dc70ff2a651bba50078c9ed0b1bcf548a5cb0d25141d51e838a186fed"
    ),
    "summary_result_id": (
        "drsdescentres_v01:"
        "f31544ab7dce1fd19d08bc3a507eba8af233407d62f75c60d2ce55bfe7632e3c"
    ),
    "open_one_artifact_request_id": (
        "drsdescentreq_v01:"
        "17a88cf1c1d36cee76e2ed9effa8980d46c229f9bc7e9bda2d4703fc265bc7b4"
    ),
    "open_one_artifact_result_id": (
        "drsdescentres_v01:"
        "3a6141d9f05da7e722624a178ed73f8b7b1356fe454bad2a2c2466fab99b182f"
    ),
    "open_full_trace_request_id": (
        "drsdescentreq_v01:"
        "94d2891144a0faea761b4a07518120ec2e29cf57cf24cb52bec196f0f9c4862d"
    ),
    "open_full_trace_result_id": (
        "drsdescentres_v01:"
        "03ae97b1316fa0a1bf9031c833e43beb3239be446f91bd37f0936e72a883b485"
    ),
    "report_id": (
        "drsreport_v01:"
        "67d2f3d84a5a5eb97c8fc8c838af40f0e494c38a82f457937707bb42c296f48a"
    ),
}


def _b3_root_states(
    plan: resolution.RetrievalPlanV01,
) -> dict[str, dict[str, object]]:
    candidate_ids = [plan.retrieval_plan_id]
    return {
        "post_vv_bundle": {
            "bundle_id": "post-vv:g2b3",
            "post_vv_passed": True,
            "validated_candidate_ids": candidate_ids,
            "rejected_candidate_ids": [],
            "required_evidence_refs": [],
            "provided_evidence_refs": [],
            "hard_failure_reasons": [],
        },
        "gt_advisory": {
            "advisory_id": "gt:g2b3",
            "candidate_ids": candidate_ids,
            "selected_candidate_id": plan.retrieval_plan_id,
            "score_micros_by_candidate": {
                plan.retrieval_plan_id: 500_000,
            },
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
            "policy_id": "policy:g2b3",
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
            "time_envelope_ref": "time-envelope:g2b3",
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


def _b3_root_triple(
    plan: resolution.RetrievalPlanV01,
) -> tuple[
    root_decision.RootDecisionKernelV01,
    root_decision.RootDecisionInputV01,
    root_decision.RootDecisionResultV01,
]:
    request = semantic_work.build_semantic_work_request_v01(
        request_id="semantic-work-request:g2b3",
        transaction_id=plan.query_id,
        target_root_id="root:local_reference",
        runtime_topology_ref="topology:g2b3",
        bounded_context_refs=("context:g2b3",),
        permitted_actor_ids=("actor:g2b3",),
        permitted_contribution_modes=("DETERMINISTIC",),
        requested_subjects=(plan.semantic_address_id,),
        required_evidence_classes=("PLAN_BINDING",),
        forbidden_claims=("create_permission",),
    )
    evidence = semantic_work.build_evidence_binding_v01(
        evidence_id="evidence-binding:g2b3:plan",
        evidence_ref="evidence:g2b3:plan",
        evidence_class="PLAN_BINDING",
        source_component_id="actor:g2b3",
        provenance_ref="provenance:g2b3",
        evidence_state=semantic_work.EVIDENCE_STATE_PRESENT,
    )
    claim = semantic_work.build_normalized_claim_v01(
        claim_id=plan.retrieval_plan_id,
        subject=plan.semantic_address_id,
        predicate=_B3_ROOT_PREDICATE,
        object_or_value=resolution.retrieval_plan_to_plain_data_v01(plan),
        time_envelope_ref="time-envelope:g2b3",
        provenance_refs=("provenance:g2b3",),
        evidence_refs=("evidence-binding:g2b3:plan",),
        confidence_micros=1_000_000,
        source_role="deterministic_runtime",
        source_mode="DETERMINISTIC",
    )
    contribution = semantic_work.build_actor_contribution_v01(
        contribution_id="contribution:g2b3",
        request_id=request.request_id,
        actor_id="actor:g2b3",
        actor_role="deterministic_runtime",
        contribution_mode="DETERMINISTIC",
        bsep_projection_ref="bsep:g2b3",
        scope=plan.semantic_address_id,
        bounded_context_refs=("context:g2b3",),
        claims=(claim,),
        evidence_bindings=(evidence,),
        constraint_bindings=(),
        uncertainty_bindings=(),
        requested_validators=(),
        forbidden_claims_observed=(),
    )
    packet = semantic_work.build_root_review_packet_from_contributions_v01(
        request=request,
        contributions=(contribution,),
        trust_profiles=build_default_component_trust_profiles_v01(),
    )
    kernel = root_decision.build_root_decision_kernel_v01()
    decision_input = root_decision.build_root_decision_input_v01(
        transaction_id=plan.query_id,
        target_root_id="root:local_reference",
        root_review_packet=packet,
        **_b3_root_states(plan),
    )
    result = root_decision.decide_root_v01(
        kernel=kernel,
        decision_input=decision_input,
    )
    assert result.decision == root_decision.ROOT_DECISION_ACCEPT
    assert result.selected_candidate_id == plan.retrieval_plan_id
    return kernel, decision_input, result


def _b3_approval(
    descent_class: str,
) -> tuple[tuple[str, ...], tuple[str, ...], tuple[str, ...]]:
    for name, record_names, memory_names, artifact_names in _B3_CLASS_APPROVALS:
        if name == descent_class:
            return record_names, memory_names, artifact_names
    raise AssertionError("unknown B3 descent class")


def _b3_fixture(
    *,
    requested_descent_class: str = "OPEN_FULL_TRACE",
    approved_descent_class: str | None = None,
    approved_budget_changes: dict[str, object] | None = None,
) -> dict[str, object]:
    approved_descent_class = (
        approved_descent_class or requested_descent_class
    )
    address = _b2_address()
    query = _b2_query(address=address)
    neighbor = _b2_record(ordinal=2, address=address)
    conflict = _b2_record(
        ordinal=3,
        address=address,
        conflict_hints=("Conflicting source evidence.",),
    )
    deadend = _b2_record(
        ordinal=4,
        address=address,
        persistent_lifecycle_state="DEADEND",
    )
    payload = b'{"bounded":"g2b3 artifact"}'
    pointer_uses = _B3_DESCENT_CLASSES
    memory_pointers = {
        "summary": semantic.build_memory_pointer_v01(
            storage_class="LOCAL_MEANING_RECORD",
            object_reference=neighbor.meaning_record_id,
            content_sha256=neighbor.content_fingerprint,
            record_class="MeaningRecordV01",
            byte_length=None,
            access_policy_id="policy:g2b3:summary",
            sensitivity_class="INTERNAL",
            allowed_use_classes=pointer_uses,
            forbidden_use_classes=(),
            summary_read_permitted=True,
            payload_read_permitted=False,
        ),
        "lineage": semantic.build_memory_pointer_v01(
            storage_class="LOCAL_LINEAGE_SET",
            object_reference=neighbor.meaning_record_id,
            content_sha256=neighbor.content_fingerprint,
            record_class="MeaningRecordV01",
            byte_length=None,
            access_policy_id="policy:g2b3:lineage",
            sensitivity_class="INTERNAL",
            allowed_use_classes=pointer_uses,
            forbidden_use_classes=(),
            summary_read_permitted=True,
            payload_read_permitted=False,
        ),
        "conflict": semantic.build_memory_pointer_v01(
            storage_class="LOCAL_CONFLICT_SET",
            object_reference=conflict.meaning_record_id,
            content_sha256=conflict.content_fingerprint,
            record_class="MeaningRecordV01",
            byte_length=None,
            access_policy_id="policy:g2b3:conflict",
            sensitivity_class="INTERNAL",
            allowed_use_classes=pointer_uses,
            forbidden_use_classes=(),
            summary_read_permitted=True,
            payload_read_permitted=False,
        ),
        "deadend": semantic.build_memory_pointer_v01(
            storage_class="LOCAL_DEADEND_PROOF",
            object_reference=deadend.meaning_record_id,
            content_sha256=deadend.content_fingerprint,
            record_class="MeaningRecordV01",
            byte_length=None,
            access_policy_id="policy:g2b3:deadend",
            sensitivity_class="INTERNAL",
            allowed_use_classes=pointer_uses,
            forbidden_use_classes=(),
            summary_read_permitted=True,
            payload_read_permitted=False,
        ),
    }
    artifact_pointer = semantic.build_artifact_pointer_v01(
        storage_class="LOCAL_DOCUMENT",
        object_reference="artifact:g2b3:bounded",
        content_sha256=hashlib.sha256(payload).hexdigest(),
        media_type="application/json",
        byte_length=len(payload),
        access_policy_id="policy:g2b3:artifact",
        sensitivity_class="INTERNAL",
        allowed_use_classes=pointer_uses,
        forbidden_use_classes=(),
        summary_read_permitted=True,
        payload_read_permitted=True,
    )
    lineage_edge = semantic.build_lineage_edge_v01(
        source_meaning_record_id=neighbor.meaning_record_id,
        target_meaning_record_id=conflict.meaning_record_id,
        relation_class="CONTRADICTS",
        claim_dimension="g2b3_conflict",
        source_history_hash=_SHA_E,
        evidence_ref_ids=("evidence:g2b3:lineage",),
        created_at=150,
        recording_component="g2b3_fixture",
    )
    anchor = semantic.build_meaning_record_v01(
        semantic_address=address,
        predecessor_record_id=None,
        supersession_reason=None,
        safe_summary="Bounded G2-B3 anchor summary.",
        semantic_tags=("g2b3", "informational"),
        resonance_reason="Root-approved controlled local memory descent.",
        memory_pointers=tuple(memory_pointers.values()),
        artifact_pointers=(artifact_pointer,),
        source_reference_ids=("source:g2b3:anchor",),
        lineage_edges=(lineage_edge,),
        time_envelope=_b2_time(),
        authority_envelope=_b2_authority(),
        persistent_lifecycle_state="ACTIVE",
        risk_hints=(),
        conflict_hints=(),
        reuse_policy_class="ANSWER_SHORTCUT",
        policy_version="policy_v01",
        schema_versions=("v0.1",),
        content_fingerprint=_SHA_A,
        recording_component="g2b3_fixture",
    )
    records_by_name = {
        "anchor": anchor,
        "neighbor": neighbor,
        "conflict": conflict,
        "deadend": deadend,
    }
    source_records = tuple(records_by_name.values())
    proposed_budget = resolution.build_memory_descent_budget_v01(
        max_depth=3,
        max_records_opened=4,
        max_pointers_opened=5,
        max_artifacts_opened=1,
        max_bytes_opened=len(payload),
        max_lineage_edges=1,
        max_conflict_records=1,
    )
    proposed_memory_pointers = tuple(memory_pointers.values())
    all_pointers = proposed_memory_pointers + (artifact_pointer,)
    plan = resolution.build_retrieval_plan_v01(
        query_id=query.query_id,
        semantic_address_id=address.semantic_address_id,
        proposed_record_ids=tuple(
            record.meaning_record_id for record in source_records
        ),
        proposed_memory_pointer_ids=tuple(
            pointer.pointer_id for pointer in proposed_memory_pointers
        ),
        proposed_artifact_pointer_ids=(artifact_pointer.pointer_id,),
        requested_descent_class=requested_descent_class,
        proposed_budget_id=proposed_budget.memory_descent_budget_id,
        required_access_policy_ids=tuple(
            pointer.access_policy_id for pointer in all_pointers
        ),
        reason_codes=(),
    )
    kernel, decision_input, root_result = _b3_root_triple(plan)
    root_hash = domain_separated_sha256_hex_v01(
        domain=_B3_ROOT_BINDING_DOMAIN,
        payload=canonical_json_bytes_v01(
            root_decision.root_decision_result_to_plain_dict_v01(root_result)
        ),
    )
    approved_budget_values: dict[str, object] = {
        "max_depth": proposed_budget.max_depth,
        "max_records_opened": proposed_budget.max_records_opened,
        "max_pointers_opened": proposed_budget.max_pointers_opened,
        "max_artifacts_opened": proposed_budget.max_artifacts_opened,
        "max_bytes_opened": proposed_budget.max_bytes_opened,
        "max_lineage_edges": proposed_budget.max_lineage_edges,
        "max_conflict_records": proposed_budget.max_conflict_records,
    }
    approved_budget_values.update(approved_budget_changes or {})
    approved_budget = resolution.build_memory_descent_budget_v01(
        **approved_budget_values,
    )
    record_names, memory_names, artifact_names = _b3_approval(
        approved_descent_class
    )
    request = resolution.build_memory_descent_request_v01(
        retrieval_plan_id=plan.retrieval_plan_id,
        query_id=plan.query_id,
        owning_local_root_id="root:local_reference",
        root_kernel_id=kernel.kernel_id,
        root_decision_input_id=decision_input.decision_input_id,
        root_decision_id=root_result.decision_id,
        root_decision_hash=root_hash,
        requested_descent_class=requested_descent_class,
        approved_descent_class=approved_descent_class,
        proposed_budget_id=proposed_budget.memory_descent_budget_id,
        approved_budget=approved_budget,
        approved_record_ids=tuple(
            records_by_name[name].meaning_record_id for name in record_names
        ),
        approved_memory_pointer_ids=tuple(
            memory_pointers[name].pointer_id for name in memory_names
        ),
        approved_artifact_pointer_ids=tuple(
            artifact_pointer.pointer_id for _ in artifact_names
        ),
    )
    artifact_payloads = (
        ((artifact_pointer.pointer_id, payload),)
        if artifact_names
        else ()
    )
    return {
        "address": address,
        "query": query,
        "records": source_records,
        "records_by_name": records_by_name,
        "memory_pointers": memory_pointers,
        "artifact_pointer": artifact_pointer,
        "lineage_edge": lineage_edge,
        "payload": payload,
        "artifact_payloads": artifact_payloads,
        "proposed_budget": proposed_budget,
        "plan": plan,
        "kernel": kernel,
        "root_input": decision_input,
        "root_result": root_result,
        "root_hash": root_hash,
        "approved_budget": approved_budget,
        "request": request,
    }


def _b3_execute(fixture: dict[str, object]) -> resolution.MemoryDescentResultV01:
    return resolution.execute_local_memory_descent_v01(
        retrieval_plan=fixture["plan"],
        proposed_budget=fixture["proposed_budget"],
        descent_request=fixture["request"],
        root_kernel=fixture["kernel"],
        root_decision_input=fixture["root_input"],
        root_decision_result=fixture["root_result"],
        source_records=fixture["records"],
        artifact_payloads=fixture["artifact_payloads"],
    )


def _b3_execution_kwargs(fixture: dict[str, object]) -> dict[str, object]:
    return {
        "retrieval_plan": fixture["plan"],
        "proposed_budget": fixture["proposed_budget"],
        "descent_request": fixture["request"],
        "root_kernel": fixture["kernel"],
        "root_decision_input": fixture["root_input"],
        "root_decision_result": fixture["root_result"],
        "source_records": fixture["records"],
        "artifact_payloads": fixture["artifact_payloads"],
    }


def _b3_assert_error(
    expected: str,
    fixture: dict[str, object],
    **changes: object,
) -> None:
    kwargs = _b3_execution_kwargs(fixture)
    kwargs.update(changes)
    with pytest.raises(ValueError, match=rf"^{expected}$"):
        resolution.execute_local_memory_descent_v01(**kwargs)


def _b3_input_snapshot(
    fixture: dict[str, object],
) -> tuple[bytes, tuple[tuple[str, bytes], ...]]:
    material = (
        resolution.retrieval_plan_to_plain_data_v01(fixture["plan"]),
        resolution.memory_descent_budget_to_plain_data_v01(
            fixture["proposed_budget"]
        ),
        resolution.memory_descent_request_to_plain_data_v01(
            fixture["request"]
        ),
        root_decision.root_decision_kernel_to_plain_dict_v01(
            fixture["kernel"]
        ),
        root_decision.root_decision_input_to_plain_dict_v01(
            fixture["root_input"]
        ),
        root_decision.root_decision_result_to_plain_dict_v01(
            fixture["root_result"]
        ),
        tuple(
            semantic.meaning_record_to_plain_data_v01(record)
            for record in fixture["records"]
        ),
    )
    return canonical_json_bytes_v01(material), tuple(
        fixture["artifact_payloads"]
    )


def _b3_report(
    fixture: dict[str, object],
    result: resolution.MemoryDescentResultV01,
) -> resolution.DRSResolutionReportV01:
    return resolution.build_drs_resolution_report_v01(
        semantic_address=fixture["address"],
        query=fixture["query"],
        source_projections=(),
        source_records=fixture["records"],
        query_evaluations=(),
        eligible_candidates=(),
        ranked_candidate_ids=(),
        selected_candidate_id=None,
        retrieval_plan=fixture["plan"],
        memory_descent_result=result,
        root_shortcut_projection=None,
        reuse_certificate=None,
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


def _b3_reidentified_report_result(
    report: resolution.DRSResolutionReportV01,
    result: resolution.MemoryDescentResultV01,
    **changes: object,
) -> resolution.DRSResolutionReportV01:
    changed_result = _reidentify(replace(result, **changes))
    return _reidentify(
        replace(report, memory_descent_result=changed_result)
    )


def _b3_proposed_unopened_memory_pointer_forgery(
    **pointer_changes: object,
) -> tuple[
    dict[str, object],
    resolution.DRSResolutionReportV01,
]:
    fixture = _b3_fixture(
        requested_descent_class="OPEN_ONE_ARTIFACT",
        approved_descent_class="OPEN_ONE_ARTIFACT",
    )
    result = _b3_execute(fixture)
    report = _b3_report(fixture, result)
    original_pointer = fixture["memory_pointers"]["summary"]
    changed_pointer = _reidentify(
        replace(original_pointer, **pointer_changes)
    )
    changed_memory_pointers = dict(fixture["memory_pointers"])
    changed_memory_pointers["summary"] = changed_pointer
    original_anchor = fixture["records_by_name"]["anchor"]
    changed_anchor = _reidentify(
        replace(
            original_anchor,
            memory_pointers=tuple(changed_memory_pointers.values()),
        )
    )
    changed_records_by_name = dict(fixture["records_by_name"])
    changed_records_by_name["anchor"] = changed_anchor
    changed_records = tuple(changed_records_by_name.values())
    changed_plan = _reidentify(
        replace(
            fixture["plan"],
            proposed_record_ids=tuple(
                record.meaning_record_id for record in changed_records
            ),
            proposed_memory_pointer_ids=tuple(
                pointer.pointer_id
                for pointer in changed_memory_pointers.values()
            ),
        )
    )
    kernel, root_input, root_result = _b3_root_triple(changed_plan)
    root_hash = domain_separated_sha256_hex_v01(
        domain=_B3_ROOT_BINDING_DOMAIN,
        payload=canonical_json_bytes_v01(
            root_decision.root_decision_result_to_plain_dict_v01(
                root_result
            )
        ),
    )
    changed_request = _reidentify(
        replace(
            fixture["request"],
            retrieval_plan_id=changed_plan.retrieval_plan_id,
            root_kernel_id=kernel.kernel_id,
            root_decision_input_id=root_input.decision_input_id,
            root_decision_id=root_result.decision_id,
            root_decision_hash=root_hash,
            approved_record_ids=(changed_anchor.meaning_record_id,),
        )
    )
    changed_result = _reidentify(
        replace(
            result,
            memory_descent_request_id=(
                changed_request.memory_descent_request_id
            ),
            retrieval_plan_id=changed_plan.retrieval_plan_id,
            opened_record_ids=(changed_anchor.meaning_record_id,),
        )
    )
    changed_report = _reidentify(
        replace(
            report,
            source_records=changed_records,
            retrieval_plan=changed_plan,
            memory_descent_result=changed_result,
        )
    )
    changed_fixture = dict(fixture)
    changed_fixture.update(
        {
            "records": changed_records,
            "records_by_name": changed_records_by_name,
            "memory_pointers": changed_memory_pointers,
            "plan": changed_plan,
            "kernel": kernel,
            "root_input": root_input,
            "root_result": root_result,
            "root_hash": root_hash,
            "request": changed_request,
        }
    )
    return changed_fixture, changed_report


def _b3_observation_report_forgeries(
    fixture: dict[str, object],
    result: resolution.MemoryDescentResultV01,
    report: resolution.DRSResolutionReportV01,
) -> tuple[tuple[str, resolution.DRSResolutionReportV01], ...]:
    ordinary_record_id = fixture[
        "records_by_name"
    ]["neighbor"].meaning_record_id
    return (
        (
            "foreign_safe_summary",
            _b3_reidentified_report_result(
                report,
                result,
                safe_summaries=(
                    "Safe but foreign transported summary.",
                )
                + result.safe_summaries[1:],
            ),
        ),
        (
            "foreign_payload_fingerprint",
            _b3_reidentified_report_result(
                report,
                result,
                opened_payload_fingerprints=(_SHA_B,),
            ),
        ),
        (
            "missing_payload_fingerprint",
            _b3_reidentified_report_result(
                report,
                result,
                opened_payload_fingerprints=(),
            ),
        ),
        (
            "extra_payload_fingerprint",
            _b3_reidentified_report_result(
                report,
                result,
                opened_payload_fingerprints=(
                    result.opened_payload_fingerprints + (_SHA_B,)
                ),
            ),
        ),
        (
            "zero_bytes",
            _b3_reidentified_report_result(
                report,
                result,
                bytes_opened=0,
            ),
        ),
        (
            "changed_bytes",
            _b3_reidentified_report_result(
                report,
                result,
                bytes_opened=result.bytes_opened + 1,
            ),
        ),
        (
            "zero_depth",
            _b3_reidentified_report_result(
                report,
                result,
                depth_reached=0,
            ),
        ),
        (
            "foreign_lineage_edge",
            _b3_reidentified_report_result(
                report,
                result,
                traversed_lineage_edge_ids=(
                    "drsedge_v01:" + "f" * 64,
                ),
            ),
        ),
        (
            "ordinary_conflict_record",
            _b3_reidentified_report_result(
                report,
                result,
                opened_conflict_record_ids=(ordinary_record_id,),
            ),
        ),
        (
            "incompatible_conflict_class",
            _b3_reidentified_report_result(
                report,
                result,
                executed_descent_class="OPEN_CONFLICT_SET",
            ),
        ),
        (
            "incompatible_deadend_class",
            _b3_reidentified_report_result(
                report,
                result,
                executed_descent_class="OPEN_DEADEND_PROOF",
            ),
        ),
        (
            "reversed_memory_pointer_order",
            _b3_reidentified_report_result(
                report,
                result,
                opened_memory_pointer_ids=tuple(
                    reversed(result.opened_memory_pointer_ids)
                ),
            ),
        ),
        (
            "reversed_record_order",
            _b3_reidentified_report_result(
                report,
                result,
                opened_record_ids=tuple(
                    reversed(result.opened_record_ids)
                ),
                safe_summaries=tuple(
                    reversed(result.safe_summaries)
                ),
            ),
        ),
    )


def _b3_observed_identity_vectors() -> dict[str, object]:
    summary = _b3_fixture(
        requested_descent_class="SUMMARY_ONLY",
        approved_descent_class="SUMMARY_ONLY",
    )
    open_one = _b3_fixture(
        requested_descent_class="OPEN_ONE_ARTIFACT",
        approved_descent_class="OPEN_ONE_ARTIFACT",
    )
    full = _b3_fixture(
        requested_descent_class="OPEN_FULL_TRACE",
        approved_descent_class="OPEN_FULL_TRACE",
    )
    summary_result = _b3_execute(summary)
    open_one_result = _b3_execute(open_one)
    full_result = _b3_execute(full)
    report = _b3_report(full, full_result)
    return {
        "proposed_budget_id": full[
            "proposed_budget"
        ].memory_descent_budget_id,
        "retrieval_plan_id": full["plan"].retrieval_plan_id,
        "root_kernel_id": full["kernel"].kernel_id,
        "root_input_id": full["root_input"].decision_input_id,
        "root_result_id": full["root_result"].decision_id,
        "root_result_binding_hash": full["root_hash"],
        "summary_request_id": summary[
            "request"
        ].memory_descent_request_id,
        "summary_result_id": summary_result.memory_descent_result_id,
        "open_one_artifact_request_id": open_one[
            "request"
        ].memory_descent_request_id,
        "open_one_artifact_result_id": (
            open_one_result.memory_descent_result_id
        ),
        "open_full_trace_request_id": full[
            "request"
        ].memory_descent_request_id,
        "open_full_trace_result_id": full_result.memory_descent_result_id,
        "report_id": report.report_id,
    }


def test_g2b_retrieval_is_filesystem_and_record_read_pure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = _b3_fixture(approved_descent_class="OPEN_FULL_TRACE")
    before = _b3_input_snapshot(fixture)

    def _forbidden_open(*args: object, **kwargs: object) -> object:
        raise AssertionError("filesystem access attempted")

    monkeypatch.setattr("builtins.open", _forbidden_open)
    first = _b3_execute(fixture)
    second = _b3_execute(fixture)
    assert first == second
    assert _b3_input_snapshot(fixture) == before
    assert first.real_world_effects_count == 0
    assert first.creates_authority is False
    assert first.creates_permission is False
    report = _b3_report(fixture, first)
    assert resolution.validate_drs_resolution_report_v01(report) == (
        True,
        (),
    )
    proposed_pointer_forgeries = (
        (
            "proposed_unopened_content_mismatch",
            _b3_proposed_unopened_memory_pointer_forgery(
                content_sha256="e" * 64,
            ),
        ),
        (
            "proposed_unopened_foreign_target",
            _b3_proposed_unopened_memory_pointer_forgery(
                object_reference="drsmeaning_v01:" + "f" * 64,
            ),
        ),
    )
    proposed_pointer_results = []
    for label, (changed_fixture, changed_report) in (
        proposed_pointer_forgeries
    ):
        assert changed_fixture[
            "request"
        ].approved_memory_pointer_ids == ()
        _b3_assert_error(
            "drs_pointer_access_policy_denied",
            changed_fixture,
        )
        proposed_pointer_results.append(
            (
                label,
                resolution.validate_drs_resolution_report_v01(
                    changed_report
                ),
            )
        )
    assert tuple(proposed_pointer_results) == tuple(
        (
            label,
            (
                False,
                ("drs_resolution_report_binding_invalid",),
            ),
        )
        for label, _ in proposed_pointer_results
    ), "; ".join(
        f"{label}={outcome!r}"
        for label, outcome in proposed_pointer_results
    )
    report_forgery_results = tuple(
        (
            label,
            resolution.validate_drs_resolution_report_v01(
                forged_report
            ),
        )
        for label, forged_report in _b3_observation_report_forgeries(
            fixture,
            first,
            report,
        )
    )
    assert report_forgery_results == tuple(
        (
            label,
            (
                False,
                ("drs_resolution_report_binding_invalid",),
            ),
        )
        for label, _ in report_forgery_results
    ), "; ".join(
        f"{label}={outcome!r}"
        for label, outcome in report_forgery_results
    )
    wrong_plan_result = _reidentify(
        replace(
            first,
            retrieval_plan_id="drsplan_v01:" + "f" * 64,
        )
    )
    wrong_plan_report = _reidentify(
        replace(report, memory_descent_result=wrong_plan_result)
    )
    assert resolution.validate_drs_resolution_report_v01(
        wrong_plan_report
    )[0] is False
    nonzero_effect_result = _reidentify(
        replace(first, real_world_effects_count=1)
    )
    nonzero_effect_report = _reidentify(
        replace(report, memory_descent_result=nonzero_effect_result)
    )
    assert resolution.validate_drs_resolution_report_v01(
        nonzero_effect_report
    )[0] is False
    source = inspect.getsource(resolution.execute_local_memory_descent_v01)
    for forbidden in (
        "open(",
        "Path(",
        "LocalDRS",
        "decide_root_v01",
        "provider",
        "network",
        "connector",
        "external_drs",
    ):
        assert forbidden not in source
    for descent_class in _B3_DESCENT_CLASSES:
        class_fixture = _b3_fixture(
            requested_descent_class=descent_class,
            approved_descent_class=descent_class,
        )
        result = _b3_execute(class_fixture)
        assert result.executed_descent_class == descent_class
        assert result.limits_respected is True
        assert result.reason_codes == ()
        assert resolution.validate_memory_descent_result_v01(
            result
        ) == (True, ())
        assert resolution.validate_drs_resolution_report_v01(
            _b3_report(class_fixture, result)
        ) == (True, ())
    b1_report = _fixture_family()[resolution.DRSResolutionReportV01]
    b2_report = _b2_positive_fixture()["report"]
    assert resolution.validate_drs_resolution_report_v01(
        b1_report
    ) == (True, ())
    assert resolution.validate_drs_resolution_report_v01(
        b2_report
    ) == (True, ())
    assert _b3_observed_identity_vectors() == _B3_IDENTITY_VECTORS


def test_g2b_memory_descent_without_root_approval_is_rejected() -> None:
    fixture = _b3_fixture(approved_descent_class="SUMMARY_ONLY")
    result = _b3_execute(fixture)
    assert result.memory_descent_request_id == fixture[
        "request"
    ].memory_descent_request_id
    request = fixture["request"]
    forged_approval = _reidentify(replace(request, root_approved=False))
    _b3_assert_error(
        "drs_exact_type_or_identity_invalid",
        fixture,
        descent_request=forged_approval,
    )
    _b3_assert_error(
        "drs_exact_type_or_identity_invalid",
        fixture,
        root_kernel=None,
    )
    wrong_owner = _reidentify(
        replace(request, owning_local_root_id="root:foreign")
    )
    _b3_assert_error(
        "drs_root_owner_mismatch",
        fixture,
        descent_request=wrong_owner,
    )
    wrong_hash = _reidentify(replace(request, root_decision_hash=_SHA_A))
    _b3_assert_error(
        "drs_root_decision_binding_invalid",
        fixture,
        descent_request=wrong_hash,
    )
    wrong_result_id = _reidentify(
        replace(request, root_decision_id="root-decision:foreign")
    )
    _b3_assert_error(
        "drs_root_decision_binding_invalid",
        fixture,
        descent_request=wrong_result_id,
    )
    wrong_plan = _reidentify(
        replace(
            fixture["plan"],
            semantic_address_id="drsaddr_v01:" + "f" * 64,
        )
    )
    _b3_assert_error(
        "drs_root_decision_binding_invalid",
        fixture,
        retrieval_plan=wrong_plan,
    )
    assert root_decision.validate_root_decision_kernel_v01(
        fixture["kernel"]
    ) == ()
    assert root_decision.validate_root_decision_input_v01(
        kernel=fixture["kernel"],
        decision_input=fixture["root_input"],
    ) == ()
    assert root_decision.validate_root_decision_result_v01(
        kernel=fixture["kernel"],
        decision_input=fixture["root_input"],
        result=fixture["root_result"],
    ) == ()


def test_g2b_root_cannot_expand_reference_descent_budget() -> None:
    for requested_class, allowed in _B3_NARROWING:
        fixture = _b3_fixture(
            requested_descent_class=requested_class,
            approved_descent_class=allowed[0],
        )
        request = fixture["request"]
        for approved_class in _B3_DESCENT_CLASSES:
            candidate = _reidentify(
                replace(request, approved_descent_class=approved_class)
            )
            valid, reasons = resolution.validate_memory_descent_request_v01(
                candidate
            )
            if approved_class in allowed:
                assert valid, (requested_class, approved_class, reasons)
            else:
                assert not valid, (requested_class, approved_class)
                assert "drs_memory_descent_budget_expansion" in reasons

    fixture = _b3_fixture(approved_descent_class="OPEN_FULL_TRACE")
    proposed = fixture["proposed_budget"]
    request = fixture["request"]
    budget_fields = (
        "max_depth",
        "max_records_opened",
        "max_pointers_opened",
        "max_artifacts_opened",
        "max_bytes_opened",
        "max_lineage_edges",
        "max_conflict_records",
    )
    for field_name in budget_fields:
        expanded_budget = _reidentify(
            replace(
                request.approved_budget,
                **{field_name: getattr(proposed, field_name) + 1},
            )
        )
        expanded_request = _reidentify(
            replace(request, approved_budget=expanded_budget)
        )
        _b3_assert_error(
            "drs_memory_descent_budget_expansion",
            fixture,
            descent_request=expanded_request,
        )
    reordered = _reidentify(
        replace(
            request,
            approved_record_ids=tuple(reversed(request.approved_record_ids)),
        )
    )
    _b3_assert_error(
        "drs_memory_descent_budget_expansion",
        fixture,
        descent_request=reordered,
    )
    unknown = _reidentify(
        replace(
            request,
            approved_record_ids=request.approved_record_ids
            + ("drsmeaning_v01:" + "f" * 64,),
        )
    )
    _b3_assert_error(
        "drs_memory_descent_budget_expansion",
        fixture,
        descent_request=unknown,
    )


def test_g2b_pointer_open_accounting_is_exact() -> None:
    expected = {
        "SUMMARY_ONLY": (2, 1, 0, 0),
        "OPEN_ONE_ARTIFACT": (1, 1, 1, 0),
        "OPEN_LINEAGE_NEIGHBORHOOD": (3, 2, 0, 1),
        "OPEN_CONFLICT_SET": (2, 1, 0, 0),
        "OPEN_DEADEND_PROOF": (2, 1, 0, 0),
        "OPEN_FULL_TRACE": (4, 5, 1, 1),
    }
    results = {}
    for descent_class, counts in expected.items():
        fixture = _b3_fixture(
            requested_descent_class=descent_class,
            approved_descent_class=descent_class,
        )
        result = _b3_execute(fixture)
        results[descent_class] = result
        assert (
            result.records_opened,
            result.pointers_opened,
            result.artifacts_opened,
            result.lineage_edges_traversed,
        ) == counts
        assert result.records_opened == len(result.opened_record_ids)
        assert result.pointers_opened == (
            len(result.opened_memory_pointer_ids)
            + len(result.opened_artifact_pointer_ids)
        )
        assert result.artifacts_opened == len(
            result.opened_artifact_pointer_ids
        )
        assert result.lineage_edges_traversed == len(
            result.traversed_lineage_edge_ids
        )
        assert result.conflict_records_opened == len(
            result.opened_conflict_record_ids
        )
    full = results["OPEN_FULL_TRACE"]
    fixture = _b3_fixture(approved_descent_class="OPEN_FULL_TRACE")
    assert full.bytes_opened == len(fixture["payload"])
    assert full.opened_payload_fingerprints == (
        hashlib.sha256(fixture["payload"]).hexdigest(),
    )
    assert fixture["payload"] not in full.__dict__.values()

    for field_name, value in (
            ("records_opened", full.records_opened - 1),
            ("pointers_opened", full.pointers_opened - 1),
            ("artifacts_opened", 0),
            ("lineage_edges_traversed", 0),
        ("conflict_records_opened", 0),
        ("limits_respected", False),
        ("real_world_effects_count", 1),
    ):
        forgery = _reidentify(replace(full, **{field_name: value}))
        assert resolution.validate_memory_descent_result_v01(forgery)[0] is False

    intrinsic_forgeries = (
        (
            "summary_count",
            _reidentify(
                replace(
                    full,
                    safe_summaries=full.safe_summaries[:-1],
                )
            ),
        ),
        (
            "fingerprint_count",
            _reidentify(
                replace(full, opened_payload_fingerprints=())
            ),
        ),
        (
            "conflict_order",
            _reidentify(
                replace(
                    full,
                    opened_conflict_record_ids=(
                        fixture[
                            "records_by_name"
                        ]["conflict"].meaning_record_id,
                        fixture[
                            "records_by_name"
                        ]["neighbor"].meaning_record_id,
                    ),
                    conflict_records_opened=2,
                )
            ),
        ),
    )
    intrinsic_results = tuple(
        (
            label,
            resolution.validate_memory_descent_result_v01(forgery),
        )
        for label, forgery in intrinsic_forgeries
    )
    assert all(
        valid is False
        and "drs_memory_descent_accounting_invalid" in reasons
        for _, (valid, reasons) in intrinsic_results
    ), "; ".join(
        f"{label}={outcome!r}"
        for label, outcome in intrinsic_results
    )


def test_g2b_summary_only_opens_no_payload() -> None:
    fixture = _b3_fixture(
        requested_descent_class="OPEN_FULL_TRACE",
        approved_descent_class="SUMMARY_ONLY",
    )
    result = _b3_execute(fixture)
    assert result.executed_descent_class == "SUMMARY_ONLY"
    assert result.opened_artifact_pointer_ids == ()
    assert result.opened_payload_fingerprints == ()
    assert result.artifacts_opened == 0
    assert result.bytes_opened == 0
    _b3_assert_error(
        "drs_summary_only_payload_forbidden",
        fixture,
        artifact_payloads=(
            (
                fixture["artifact_pointer"].pointer_id,
                fixture["payload"],
            ),
        ),
    )
    forged = _reidentify(
        replace(
            result,
            opened_artifact_pointer_ids=(
                fixture["artifact_pointer"].pointer_id,
            ),
            opened_payload_fingerprints=(
                hashlib.sha256(fixture["payload"]).hexdigest(),
            ),
            pointers_opened=result.pointers_opened + 1,
            artifacts_opened=1,
            bytes_opened=len(fixture["payload"]),
        )
    )
    valid, reasons = resolution.validate_memory_descent_result_v01(forged)
    assert valid is False
    assert "drs_summary_only_payload_forbidden" in reasons


def test_g2b_open_one_artifact_obeys_depth_and_count_one() -> None:
    fixture = _b3_fixture(approved_descent_class="OPEN_ONE_ARTIFACT")
    result = _b3_execute(fixture)
    assert result.executed_descent_class == "OPEN_ONE_ARTIFACT"
    assert result.opened_record_ids == (
        fixture["records_by_name"]["anchor"].meaning_record_id,
    )
    assert result.opened_memory_pointer_ids == ()
    assert result.opened_artifact_pointer_ids == (
        fixture["artifact_pointer"].pointer_id,
    )
    assert result.pointers_opened == 1
    assert result.artifacts_opened == 1
    assert result.depth_reached == 1
    assert result.bytes_opened == len(fixture["payload"])
    assert result.opened_payload_fingerprints == (
        hashlib.sha256(fixture["payload"]).hexdigest(),
    )

    extra_pointer = next(iter(fixture["memory_pointers"].values()))
    expanded_request = _reidentify(
        replace(
            fixture["request"],
            approved_memory_pointer_ids=(extra_pointer.pointer_id,),
        )
    )
    _b3_assert_error(
        "drs_open_one_artifact_limit_exceeded",
        fixture,
        descent_request=expanded_request,
    )
    missing_payload = dict(_b3_execution_kwargs(fixture))
    missing_payload["artifact_payloads"] = ()
    with pytest.raises(
        ValueError,
        match=r"^drs_open_one_artifact_limit_exceeded$",
    ):
        resolution.execute_local_memory_descent_v01(**missing_payload)
    forged_depth = _reidentify(replace(result, depth_reached=2))
    valid, reasons = resolution.validate_memory_descent_result_v01(
        forged_depth
    )
    assert valid is False
    assert "drs_open_one_artifact_limit_exceeded" in reasons


_B4_ROOT_RESULT_BINDING_DOMAIN = (
    "hedgehog:drs:root_shortcut_root_result_binding:v01"
)
_B4_ROOT_CLAIM_PREDICATE = (
    "authorize_non_action_informational_answer_shortcut_v01"
)
_B4_POLICY_REF = "policy:drs_answer_shortcut:v0.1"
_B4_IDENTITY_VECTORS = {
    "root_kernel_id": (
        "6cbe784404adaf78863830a3dd1cb67d1baaa1c3d46296c633018c715c522235"
    ),
    "root_input_id": (
        "430997a4dfe7bbebafb71d43630fdff3b1bcc14ca5fb5c6459f23a0d07ecde4f"
    ),
    "root_result_id": (
        "15298756dba7b09d6934c1592cd8b4f3835f2f35fd66112f70988069354b3ccf"
    ),
    "root_result_binding_hash": (
        "a7fa40eaa6feab89abcd032f579b075a5a32cfbf05de4713558b0cde17aa3cd7"
    ),
    "selected_candidate_id": (
        "drscandidate_v01:"
        "0c233cfa0bffa0b6c30641dbf0ebaab479e20f5ba7383d5dfc67e4dcf58e5e7a"
    ),
    "projection_id": (
        "drsrootshortcut_v01:"
        "f76532bf93271230b99daefa18750d6c48ccd50ba3b222f670859c81e98ce3fb"
    ),
    "certificate_id": (
        "reusecert_v01:"
        "8e5d38ed4e690409177a3791278b771d55c436c0c8c0bd54e460f95f4d73975f"
    ),
    "report_id": (
        "drsreport_v01:"
        "247a3f57bc4dcdd726b6d5bced7a6c7bba9394c8bff96fe141a7976ec2e997c8"
    ),
    "use_time": 200,
}


def _b4_claim_preimage(
    *,
    fixture: dict[str, object],
    valid_from: int = 200,
    valid_to: int = 300,
    issued_at: int = 200,
) -> dict[str, object]:
    query = fixture["query"]
    candidate = fixture["ranked"][0]
    evaluation = next(
        item
        for item in fixture["evaluations"]
        if item.query_evaluation_id == candidate.query_evaluation_id
    )
    return {
        "profile_version": "v0.1",
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
        "issued_at": issued_at,
        "evaluated_at": evaluation.evaluated_at,
        "root_shortcut_policy_ref": _B4_POLICY_REF,
    }


def _b4_root_states(candidate_id: str) -> dict[str, dict[str, object]]:
    return {
        "post_vv_bundle": {
            "bundle_id": "post-vv:g2b4",
            "post_vv_passed": True,
            "validated_candidate_ids": [candidate_id],
            "rejected_candidate_ids": [],
            "required_evidence_refs": [],
            "provided_evidence_refs": [],
            "hard_failure_reasons": [],
        },
        "gt_advisory": {
            "advisory_id": "gt:g2b4",
            "candidate_ids": [candidate_id],
            "selected_candidate_id": candidate_id,
            "score_micros_by_candidate": {candidate_id: 500_000},
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
            "policy_id": "policy:g2b4",
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
            "time_envelope_ref": "time-envelope:g2b4",
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


def _b4_fixture() -> dict[str, object]:
    fixture = _b2_positive_fixture()
    query = fixture["query"]
    address = fixture["address"]
    candidate = fixture["ranked"][0]
    evaluation = next(
        item
        for item in fixture["evaluations"]
        if item.query_evaluation_id == candidate.query_evaluation_id
    )
    record = next(
        item
        for item in fixture["records"]
        if item.meaning_record_id == candidate.meaning_record_id
    )
    claim_preimage = _b4_claim_preimage(fixture=fixture)
    request = semantic_work.build_semantic_work_request_v01(
        request_id="semantic-work-request:g2b4",
        transaction_id=query.query_id,
        target_root_id="root:local_reference",
        runtime_topology_ref="topology:g2b4",
        bounded_context_refs=("context:g2b4",),
        permitted_actor_ids=("actor:g2b4",),
        permitted_contribution_modes=("DETERMINISTIC",),
        requested_subjects=(address.semantic_address_id,),
        required_evidence_classes=("ROOT_SHORTCUT_BINDING",),
        forbidden_claims=("create_permission",),
    )
    evidence = semantic_work.build_evidence_binding_v01(
        evidence_id="evidence-binding:g2b4:shortcut",
        evidence_ref="evidence:g2b4:shortcut",
        evidence_class="ROOT_SHORTCUT_BINDING",
        source_component_id="actor:g2b4",
        provenance_ref="provenance:g2b4",
        evidence_state=semantic_work.EVIDENCE_STATE_PRESENT,
    )
    claim = semantic_work.build_normalized_claim_v01(
        claim_id=candidate.resolution_candidate_id,
        subject=address.semantic_address_id,
        predicate=_B4_ROOT_CLAIM_PREDICATE,
        object_or_value=claim_preimage,
        time_envelope_ref="time-envelope:g2b4",
        provenance_refs=("provenance:g2b4",),
        evidence_refs=("evidence-binding:g2b4:shortcut",),
        confidence_micros=1_000_000,
        source_role="deterministic_runtime",
        source_mode="DETERMINISTIC",
    )
    contribution = semantic_work.build_actor_contribution_v01(
        contribution_id="contribution:g2b4",
        request_id=request.request_id,
        actor_id="actor:g2b4",
        actor_role="deterministic_runtime",
        contribution_mode="DETERMINISTIC",
        bsep_projection_ref="bsep:g2b4",
        scope=address.semantic_address_id,
        bounded_context_refs=("context:g2b4",),
        claims=(claim,),
        evidence_bindings=(evidence,),
        constraint_bindings=(),
        uncertainty_bindings=(),
        requested_validators=(),
        forbidden_claims_observed=(),
    )
    packet = semantic_work.build_root_review_packet_from_contributions_v01(
        request=request,
        contributions=(contribution,),
        trust_profiles=build_default_component_trust_profiles_v01(),
    )
    kernel = root_decision.build_root_decision_kernel_v01()
    decision_input = root_decision.build_root_decision_input_v01(
        transaction_id=query.query_id,
        target_root_id="root:local_reference",
        root_review_packet=packet,
        **_b4_root_states(candidate.resolution_candidate_id),
    )
    decision_result = root_decision.decide_root_v01(
        kernel=kernel,
        decision_input=decision_input,
    )
    result_hash = domain_separated_sha256_hex_v01(
        domain=_B4_ROOT_RESULT_BINDING_DOMAIN,
        payload=canonical_json_bytes_v01(
            root_decision.root_decision_result_to_plain_dict_v01(
                decision_result
            )
        ),
    )
    projection = reuse.build_root_shortcut_authorization_projection_v01(
        owning_local_root_id="root:local_reference",
        root_kernel_id=kernel.kernel_id,
        root_decision_input_id=decision_input.decision_input_id,
        root_decision_id=decision_result.decision_id,
        root_decision_hash=result_hash,
        selected_candidate_id=candidate.resolution_candidate_id,
        semantic_address_id=address.semantic_address_id,
        meaning_record_id=record.meaning_record_id,
        query_id=query.query_id,
        query_evaluation_id=evaluation.query_evaluation_id,
        allowed_reuse_class="ANSWER_SHORTCUT",
        scope_fingerprint=query.scope_fingerprint,
        policy_version=query.policy_version,
        schema_versions=query.schema_versions,
        valid_from=200,
        valid_to=300,
        root_shortcut_policy_ref=_B4_POLICY_REF,
    )
    certificate = reuse.build_reuse_certificate_v01(
        semantic_address_id=address.semantic_address_id,
        meaning_record_id=record.meaning_record_id,
        query_id=query.query_id,
        query_evaluation_id=evaluation.query_evaluation_id,
        resolution_candidate_id=candidate.resolution_candidate_id,
        root_shortcut_authorization_projection=projection,
        case_type="NON_ACTION_INFORMATIONAL",
        required_evidence_classes=query.required_evidence_classes,
        observed_evidence_fingerprint=(
            evaluation.observed_evidence_fingerprint
        ),
        forbidden_changes=query.forbidden_changes,
        checked_dependency_fingerprint=(
            evaluation.checked_dependency_fingerprint
        ),
        valid_from=200,
        valid_to=300,
        reuse_class="ANSWER_SHORTCUT",
        source_history_hash=evaluation.source_history_hash,
        action_history_binding_id=None,
        issued_at=200,
        evaluated_at=evaluation.evaluated_at,
    )
    report = _reidentify(
        replace(
            fixture["report"],
            root_shortcut_projection=projection,
            reuse_certificate=certificate,
        )
    )
    assert resolution.validate_drs_resolution_report_v01(report) == (
        True,
        (),
    )
    return {
        **fixture,
        "selected_candidate": candidate,
        "selected_evaluation": evaluation,
        "selected_record": record,
        "claim_preimage": claim_preimage,
        "root_kernel": kernel,
        "root_input": decision_input,
        "root_result": decision_result,
        "root_result_binding_hash": result_hash,
        "projection": projection,
        "certificate": certificate,
        "report": report,
        "use_time": 200,
    }


class _B4ExplodingEqualityError(Exception):
    pass


class _B4ExplodingEquality:
    def __eq__(self, other: object) -> bool:
        raise _B4ExplodingEqualityError("unvalidated equality executed")


def _b4_alternate_root_triple(
    fixture: dict[str, object],
    *,
    transaction_id: str | None = None,
    target_root_id: str = "root:local_reference",
    selected_candidate_id: str | None = None,
    claim_specs: tuple[dict[str, object], ...] | None = None,
) -> tuple[
    root_decision.RootDecisionKernelV01,
    root_decision.RootDecisionInputV01,
    root_decision.RootDecisionResultV01,
]:
    query = fixture["query"]
    address = fixture["address"]
    candidate_id = (
        fixture["selected_candidate"].resolution_candidate_id
        if selected_candidate_id is None
        else selected_candidate_id
    )
    root_transaction_id = (
        query.query_id if transaction_id is None else transaction_id
    )
    if claim_specs is None:
        claim_specs = ({},)
    requested_subjects = tuple(
        dict.fromkeys(
            (
                address.semantic_address_id,
                *(
                    str(
                        spec.get(
                            "subject",
                            address.semantic_address_id,
                        )
                    )
                    for spec in claim_specs
                ),
            )
        )
    )
    request = semantic_work.build_semantic_work_request_v01(
        request_id="semantic-work-request:g2b4:alternate",
        transaction_id=root_transaction_id,
        target_root_id=target_root_id,
        runtime_topology_ref="topology:g2b4:alternate",
        bounded_context_refs=("context:g2b4:alternate",),
        permitted_actor_ids=("actor:g2b4:alternate",),
        permitted_contribution_modes=("DETERMINISTIC",),
        requested_subjects=requested_subjects,
        required_evidence_classes=("ROOT_SHORTCUT_BINDING",),
        forbidden_claims=("create_permission",),
    )
    evidence = semantic_work.build_evidence_binding_v01(
        evidence_id="evidence-binding:g2b4:alternate",
        evidence_ref="evidence:g2b4:alternate",
        evidence_class="ROOT_SHORTCUT_BINDING",
        source_component_id="actor:g2b4:alternate",
        provenance_ref="provenance:g2b4:alternate",
        evidence_state=semantic_work.EVIDENCE_STATE_PRESENT,
    )
    claims = tuple(
        semantic_work.build_normalized_claim_v01(
            claim_id=str(spec.get("claim_id", candidate_id)),
            subject=str(
                spec.get("subject", address.semantic_address_id)
            ),
            predicate=str(
                spec.get("predicate", _B4_ROOT_CLAIM_PREDICATE)
            ),
            object_or_value=spec.get(
                "object_or_value",
                fixture["claim_preimage"],
            ),
            time_envelope_ref="time-envelope:g2b4:alternate",
            provenance_refs=("provenance:g2b4:alternate",),
            evidence_refs=("evidence-binding:g2b4:alternate",),
            confidence_micros=1_000_000,
            source_role="deterministic_runtime",
            source_mode="DETERMINISTIC",
        )
        for spec in claim_specs
    )
    contribution = semantic_work.build_actor_contribution_v01(
        contribution_id="contribution:g2b4:alternate",
        request_id=request.request_id,
        actor_id="actor:g2b4:alternate",
        actor_role="deterministic_runtime",
        contribution_mode="DETERMINISTIC",
        bsep_projection_ref="bsep:g2b4:alternate",
        scope=address.semantic_address_id,
        bounded_context_refs=("context:g2b4:alternate",),
        claims=claims,
        evidence_bindings=(evidence,),
        constraint_bindings=(),
        uncertainty_bindings=(),
        requested_validators=(),
        forbidden_claims_observed=(),
    )
    packet = semantic_work.build_root_review_packet_from_contributions_v01(
        request=request,
        contributions=(contribution,),
        trust_profiles=build_default_component_trust_profiles_v01(),
    )
    states = _b4_root_states(candidate_id)
    root_candidate_ids = list(
        dict.fromkeys(
            (
                candidate_id,
                *(claim.claim_id for claim in claims),
            )
        )
    )
    states["post_vv_bundle"]["validated_candidate_ids"] = (
        root_candidate_ids
    )
    states["gt_advisory"]["candidate_ids"] = root_candidate_ids
    states["gt_advisory"]["score_micros_by_candidate"] = {
        item: 500_000 for item in root_candidate_ids
    }
    kernel = root_decision.build_root_decision_kernel_v01()
    decision_input = root_decision.build_root_decision_input_v01(
        transaction_id=root_transaction_id,
        target_root_id=target_root_id,
        root_review_packet=packet,
        **states,
    )
    result = root_decision.decide_root_v01(
        kernel=kernel,
        decision_input=decision_input,
    )
    assert root_decision.validate_root_decision_kernel_v01(kernel) == ()
    assert root_decision.validate_root_decision_input_v01(
        kernel=kernel,
        decision_input=decision_input,
    ) == ()
    assert root_decision.validate_root_decision_result_v01(
        kernel=kernel,
        decision_input=decision_input,
        result=result,
    ) == ()
    return kernel, decision_input, result


def _b4_report_for_root_triple(
    fixture: dict[str, object],
    *,
    root_kernel: root_decision.RootDecisionKernelV01,
    root_input: root_decision.RootDecisionInputV01,
    root_result: root_decision.RootDecisionResultV01,
    owning_local_root_id: str = "root:local_reference",
) -> resolution.DRSResolutionReportV01:
    query = fixture["query"]
    address = fixture["address"]
    candidate = fixture["selected_candidate"]
    evaluation = fixture["selected_evaluation"]
    record = fixture["selected_record"]
    result_hash = domain_separated_sha256_hex_v01(
        domain=_B4_ROOT_RESULT_BINDING_DOMAIN,
        payload=canonical_json_bytes_v01(
            root_decision.root_decision_result_to_plain_dict_v01(
                root_result
            )
        ),
    )
    projection = reuse.build_root_shortcut_authorization_projection_v01(
        owning_local_root_id=owning_local_root_id,
        root_kernel_id=root_kernel.kernel_id,
        root_decision_input_id=root_input.decision_input_id,
        root_decision_id=root_result.decision_id,
        root_decision_hash=result_hash,
        selected_candidate_id=candidate.resolution_candidate_id,
        semantic_address_id=address.semantic_address_id,
        meaning_record_id=record.meaning_record_id,
        query_id=query.query_id,
        query_evaluation_id=evaluation.query_evaluation_id,
        allowed_reuse_class="ANSWER_SHORTCUT",
        scope_fingerprint=query.scope_fingerprint,
        policy_version=query.policy_version,
        schema_versions=query.schema_versions,
        valid_from=fixture["projection"].valid_from,
        valid_to=fixture["projection"].valid_to,
        root_shortcut_policy_ref=_B4_POLICY_REF,
    )
    certificate = reuse.build_reuse_certificate_v01(
        semantic_address_id=address.semantic_address_id,
        meaning_record_id=record.meaning_record_id,
        query_id=query.query_id,
        query_evaluation_id=evaluation.query_evaluation_id,
        resolution_candidate_id=candidate.resolution_candidate_id,
        root_shortcut_authorization_projection=projection,
        case_type="NON_ACTION_INFORMATIONAL",
        required_evidence_classes=query.required_evidence_classes,
        observed_evidence_fingerprint=(
            evaluation.observed_evidence_fingerprint
        ),
        forbidden_changes=query.forbidden_changes,
        checked_dependency_fingerprint=(
            evaluation.checked_dependency_fingerprint
        ),
        valid_from=projection.valid_from,
        valid_to=projection.valid_to,
        reuse_class="ANSWER_SHORTCUT",
        source_history_hash=evaluation.source_history_hash,
        action_history_binding_id=None,
        issued_at=fixture["certificate"].issued_at,
        evaluated_at=evaluation.evaluated_at,
    )
    report = _reidentify(
        replace(
            fixture["report"],
            root_shortcut_projection=projection,
            reuse_certificate=certificate,
        )
    )
    assert resolution.validate_drs_resolution_report_v01(report) == (
        True,
        (),
    )
    return report


_B4_UNSET = object()


def _b4_validate(
    fixture: dict[str, object],
    *,
    report: object | None = None,
    root_kernel: object | None = None,
    root_input: object | None = None,
    root_result: object | None = None,
    use_time: object = _B4_UNSET,
) -> tuple[bool, tuple[str, ...]]:
    return reuse.validate_existing_root_shortcut_decision_v01(
        resolution_report=(
            fixture["report"] if report is None else report
        ),
        root_kernel=(
            fixture["root_kernel"] if root_kernel is None else root_kernel
        ),
        root_decision_input=(
            fixture["root_input"] if root_input is None else root_input
        ),
        root_decision_result=(
            fixture["root_result"] if root_result is None else root_result
        ),
        use_time=(
            fixture["use_time"]
            if use_time is _B4_UNSET
            else use_time
        ),
    )


def _b4_alternate_value(name: str, value: object) -> object:
    if type(value) is bool:
        return not value
    if type(value) is int:
        return value + 1
    if type(value) is tuple:
        return value + ("G2B4_MUTATION",)
    if value is None:
        return "drsg2ahistory_v01:" + "e" * 64
    if type(value) is str:
        for prefix in (
            "drsaddr_v01:",
            "drsmeaning_v01:",
            "drsquery_v01:",
            "drsqeval_v01:",
            "drscandidate_v01:",
            "drsrootshortcut_v01:",
            "reusecert_v01:",
        ):
            if value.startswith(prefix):
                return prefix + "e" * 64
        if len(value) == 64 and all(
            character in "0123456789abcdef" for character in value
        ):
            return "e" * 64
        if name.endswith("_version"):
            return "v9.9"
        return value + ":mutation"
    raise AssertionError(name)


def test_g2b_root_decision_exact_cross_binding_is_required() -> None:
    fixture = _b4_fixture()
    assert _b4_validate(fixture) == (True, ())

    class _RootKernelSubclass(root_decision.RootDecisionKernelV01):
        pass

    class _RootInputSubclass(root_decision.RootDecisionInputV01):
        pass

    class _RootResultSubclass(root_decision.RootDecisionResultV01):
        pass

    kernel_subclass = _RootKernelSubclass(
        *(
            getattr(fixture["root_kernel"], field.name)
            for field in fields(fixture["root_kernel"])
        )
    )
    input_subclass = _RootInputSubclass(
        *(
            getattr(fixture["root_input"], field.name)
            for field in fields(fixture["root_input"])
        )
    )
    result_subclass = _RootResultSubclass(
        *(
            getattr(fixture["root_result"], field.name)
            for field in fields(fixture["root_result"])
        )
    )
    kernel_cases = (
        ("kernel_wrong_outer_type", object()),
        ("kernel_subclass", kernel_subclass),
        (
            "kernel_malformed_identity_field",
            replace(
                fixture["root_kernel"],
                kernel_id=_B4ExplodingEquality(),
            ),
        ),
        (
            "kernel_wrong_id",
            replace(fixture["root_kernel"], kernel_id="e" * 64),
        ),
    )
    for label, invalid_kernel in kernel_cases:
        assert root_decision.validate_root_decision_kernel_v01(
            invalid_kernel
        )
        valid, reasons = _b4_validate(
            fixture,
            root_kernel=invalid_kernel,
        )
        assert valid is False, label
        assert reasons == ("drs_exact_type_or_identity_invalid",)

    packet = fixture["root_input"].root_review_packet
    proposal = packet.synthesis_proposal
    authority_claim = replace(
        proposal.normalized_claims[0],
        authority_class="ROOT",
    )
    authority_proposal = replace(
        proposal,
        normalized_claims=(authority_claim,),
    )
    authority_packet = replace(
        packet,
        synthesis_proposal=authority_proposal,
    )
    missing_claim_proposal = replace(
        proposal,
        normalized_claims=(),
    )
    missing_claim_packet = replace(
        packet,
        synthesis_proposal=missing_claim_proposal,
    )
    input_cases = (
        ("input_wrong_outer_type", object()),
        ("input_subclass", input_subclass),
        (
            "input_malformed_identity_field",
            replace(
                fixture["root_input"],
                decision_input_id=_B4ExplodingEquality(),
            ),
        ),
        (
            "input_wrong_id",
            replace(
                fixture["root_input"],
                decision_input_id="e" * 64,
            ),
        ),
        (
            "input_claim_authority_not_none",
            replace(
                fixture["root_input"],
                root_review_packet=authority_packet,
            ),
        ),
        (
            "input_claim_missing",
            replace(
                fixture["root_input"],
                root_review_packet=missing_claim_packet,
            ),
        ),
    )
    for label, invalid_input in input_cases:
        assert root_decision.validate_root_decision_input_v01(
            kernel=fixture["root_kernel"],
            decision_input=invalid_input,
        )
        valid, reasons = _b4_validate(
            fixture,
            root_input=invalid_input,
        )
        assert valid is False, label
        assert reasons == ("drs_exact_type_or_identity_invalid",)

    other_candidate_id = fixture["ranked"][1].resolution_candidate_id
    result_cases = (
        ("result_wrong_outer_type", object()),
        ("result_subclass", result_subclass),
        (
            "result_malformed_identity_field",
            replace(
                fixture["root_result"],
                decision_id=_B4ExplodingEquality(),
            ),
        ),
        (
            "result_wrong_id",
            replace(fixture["root_result"], decision_id="e" * 64),
        ),
        (
            "result_wrong_decision_input_binding",
            replace(
                fixture["root_result"],
                decision_input_id="e" * 64,
            ),
        ),
        (
            "result_wrong_transaction",
            replace(
                fixture["root_result"],
                transaction_id="drsquery_v01:" + "e" * 64,
            ),
        ),
        (
            "result_wrong_target_root",
            replace(
                fixture["root_result"],
                target_root_id="root:foreign",
            ),
        ),
        (
            "result_non_accept",
            replace(fixture["root_result"], decision="REJECT"),
        ),
        (
            "result_wrong_accepted_reason",
            replace(
                fixture["root_result"],
                reason_code="no_valid_candidate",
            ),
        ),
        (
            "result_wrong_selected_candidate",
            replace(
                fixture["root_result"],
                selected_candidate_id=other_candidate_id,
            ),
        ),
        (
            "result_root_commit_false",
            replace(
                fixture["root_result"],
                root_commit_created=False,
            ),
        ),
        (
            "result_permission_created",
            replace(
                fixture["root_result"],
                permission_created=True,
            ),
        ),
        (
            "result_final_output_created",
            replace(
                fixture["root_result"],
                final_output_created=True,
            ),
        ),
        (
            "result_effect_requested",
            replace(
                fixture["root_result"],
                effect_requested=True,
            ),
        ),
    )
    for label, invalid_result in result_cases:
        assert root_decision.validate_root_decision_result_v01(
            kernel=fixture["root_kernel"],
            decision_input=fixture["root_input"],
            result=invalid_result,
        )
        valid, reasons = _b4_validate(
            fixture,
            root_result=invalid_result,
        )
        assert valid is False, label
        assert reasons == ("drs_exact_type_or_identity_invalid",)

    forged_projection = _reidentify(
        replace(fixture["projection"], root_decision_hash=_SHA_E)
    )
    forged_certificate = _reidentify(
        replace(
            fixture["certificate"],
            root_shortcut_authorization_projection_id=(
                forged_projection.root_shortcut_projection_id
            ),
            root_decision_hash=_SHA_E,
        )
    )
    forged_report = _reidentify(
        replace(
            fixture["report"],
            root_shortcut_projection=forged_projection,
            reuse_certificate=forged_certificate,
        )
    )
    assert _b4_validate(fixture, report=forged_report) == (
        False,
        ("drs_root_decision_binding_invalid",),
    )

    second_claim_id = fixture["ranked"][1].resolution_candidate_id
    changed_preimage = {
        **fixture["claim_preimage"],
        "observed_evidence_fingerprint": "e" * 64,
    }
    changed_policy_preimage = {
        **fixture["claim_preimage"],
        "root_shortcut_policy_ref": "policy:foreign",
    }
    claim_cases = (
        (
            "claim_second_present",
            (
                {},
                {
                    "claim_id": second_claim_id,
                    "predicate": (
                        _B4_ROOT_CLAIM_PREDICATE + ":second"
                    ),
                },
            ),
            None,
        ),
        (
            "claim_wrong_id",
            ({"claim_id": second_claim_id},),
            second_claim_id,
        ),
        (
            "claim_wrong_subject",
            ({"subject": "drsaddr_v01:" + "e" * 64},),
            None,
        ),
        (
            "claim_wrong_predicate",
            ({"predicate": "authorize_other_shortcut_v01"},),
            None,
        ),
        (
            "claim_changed_preimage",
            ({"object_or_value": changed_preimage},),
            None,
        ),
        (
            "claim_wrong_policy_reference",
            ({"object_or_value": changed_policy_preimage},),
            None,
        ),
    )
    for label, claim_specs, selected_candidate_id in claim_cases:
        kernel, decision_input, result = _b4_alternate_root_triple(
            fixture,
            claim_specs=claim_specs,
            selected_candidate_id=selected_candidate_id,
        )
        report = _b4_report_for_root_triple(
            fixture,
            root_kernel=kernel,
            root_input=decision_input,
            root_result=result,
        )
        valid, reasons = _b4_validate(
            fixture,
            report=report,
            root_kernel=kernel,
            root_input=decision_input,
            root_result=result,
        )
        assert valid is False, label
        assert reasons == ("drs_root_decision_binding_invalid",)


def test_g2b_wrong_local_root_is_rejected() -> None:
    fixture = _b4_fixture()
    projection = _reidentify(
        replace(fixture["projection"], owning_local_root_id="root:foreign")
    )
    certificate = _reidentify(
        replace(
            fixture["certificate"],
            root_shortcut_authorization_projection_id=(
                projection.root_shortcut_projection_id
            ),
            owning_local_root_id="root:foreign",
        )
    )
    report = _reidentify(
        replace(
            fixture["report"],
            root_shortcut_projection=projection,
            reuse_certificate=certificate,
        )
    )
    assert _b4_validate(fixture, report=report) == (
        False,
        ("drs_root_owner_mismatch",),
    )
    coherent_cases = (
        (
            "coherent_foreign_root",
            {
                "target_root_id": "root:foreign",
            },
            "root:foreign",
        ),
        (
            "coherent_other_query",
            {
                "transaction_id": "drsquery_v01:" + "e" * 64,
            },
            "root:local_reference",
        ),
        (
            "coherent_other_candidate",
            {
                "selected_candidate_id": (
                    fixture["ranked"][1].resolution_candidate_id
                ),
            },
            "root:local_reference",
        ),
    )
    for label, triple_changes, projection_root_id in coherent_cases:
        kernel, decision_input, result = _b4_alternate_root_triple(
            fixture,
            **triple_changes,
        )
        alternate_report = _b4_report_for_root_triple(
            fixture,
            root_kernel=kernel,
            root_input=decision_input,
            root_result=result,
            owning_local_root_id=projection_root_id,
        )
        valid, reasons = _b4_validate(
            fixture,
            report=alternate_report,
            root_kernel=kernel,
            root_input=decision_input,
            root_result=result,
        )
        assert valid is False, label
        assert reasons


def test_g2b_forged_root_shortcut_projection_is_rejected() -> None:
    fixture = _b4_fixture()
    projection_fields = tuple(
        field.name for field in fields(reuse.RootShortcutAuthorizationProjectionV01)
    )
    assert len(projection_fields) == 26
    for name in projection_fields:
        changed = replace(
            fixture["projection"],
            **{
                name: _b4_alternate_value(
                    name,
                    getattr(fixture["projection"], name),
                )
            },
        )
        projection = (
            changed
            if name == "root_shortcut_projection_id"
            else _reidentify(changed)
        )
        report = _reidentify(
            replace(fixture["report"], root_shortcut_projection=projection)
        )
        valid, reasons = _b4_validate(fixture, report=report)
        assert valid is False, name
        assert reasons

    class _ProjectionSubclass(
        reuse.RootShortcutAuthorizationProjectionV01
    ):
        pass

    subclass = _ProjectionSubclass(
        *(
            getattr(fixture["projection"], field.name)
            for field in fields(fixture["projection"])
        )
    )
    report = replace(
        fixture["report"],
        root_shortcut_projection=subclass,
    )
    assert _b4_validate(fixture, report=report)[0] is False


def test_g2b_reuse_certificate_identity_rebuild_is_exact() -> None:
    fixture = _b4_fixture()
    assert reuse.validate_reuse_certificate_v01(
        fixture["certificate"]
    ) == (True, ())
    stale = replace(
        fixture["certificate"],
        observed_evidence_fingerprint=_SHA_E,
    )
    assert reuse.validate_reuse_certificate_v01(stale) == (
        False,
        ("reuse_certificate_identity_invalid",),
    )
    rebuilt = _reidentify(stale)
    assert reuse.validate_reuse_certificate_v01(rebuilt) == (True, ())
    report = _reidentify(
        replace(fixture["report"], reuse_certificate=rebuilt)
    )
    assert _b4_validate(fixture, report=report) == (
        False,
        ("reuse_certificate_cross_profile_mismatch",),
    )


def test_g2b_reuse_certificate_cross_profile_coherence_is_exact() -> None:
    fixture = _b4_fixture()
    certificate_fields = tuple(
        field.name for field in fields(reuse.ReuseCertificateV01)
    )
    assert len(certificate_fields) == 39
    for name in certificate_fields:
        changed = replace(
            fixture["certificate"],
            **{
                name: _b4_alternate_value(
                    name,
                    getattr(fixture["certificate"], name),
                )
            },
        )
        certificate = (
            changed if name == "certificate_id" else _reidentify(changed)
        )
        report = _reidentify(
            replace(fixture["report"], reuse_certificate=certificate)
        )
        valid, reasons = _b4_validate(fixture, report=report)
        assert valid is False, name
        assert reasons


def test_g2b_reuse_certificate_expires_at_exact_valid_to() -> None:
    fixture = _b4_fixture()
    class _B4IntSubclass(int):
        pass

    assert _b4_validate(fixture, use_time=200) == (True, ())
    assert _b4_validate(fixture, use_time=299) == (True, ())
    assert _b4_validate(fixture, use_time=300) == (
        False,
        ("reuse_certificate_expired",),
    )
    assert _b4_validate(fixture, use_time=199) == (
        False,
        ("reuse_certificate_expired",),
    )
    for invalid in (
        True,
        200.0,
        Decimal("200"),
        "200",
        _B4IntSubclass(200),
        None,
    ):
        assert _b4_validate(fixture, use_time=invalid) == (
            False,
            ("drs_exact_type_or_identity_invalid",),
        )


def _b4_request_reason(text: str) -> str | None:
    from hedgehog.root_orchestrator import RootOrchestrator

    return RootOrchestrator._classify_g2b_shortcut_request(text)


def test_g2b_payment_request_cannot_take_answer_shortcut() -> None:
    for text in (
        "pay supplier",
        "SEND PAYMENT!",
        "transfer   funds",
        "authorize payment",
        "execute payment",
        "make bank transfer",
    ):
        assert _b4_request_reason(text) == "drs_payment_shortcut_forbidden"
    assert _b4_request_reason("explain the payment policy") is None


def test_g2b_shipment_release_cannot_take_answer_shortcut() -> None:
    for text in ("release shipment", "Dispatch shipment!", "ship order"):
        assert _b4_request_reason(text) == "drs_shipment_shortcut_forbidden"
    assert _b4_request_reason("show shipment policy") is None


def test_g2b_ticket_issue_cannot_take_answer_shortcut() -> None:
    for text in (
        "buy ticket",
        "purchase ticket",
        "book ticket",
        "issue ticket",
        "reserve seat",
    ):
        assert _b4_request_reason(text) == "drs_ticket_shortcut_forbidden"
    assert _b4_request_reason("summarize ticket rules") is None


def test_g2b_action_commit_packet_creation_cannot_take_answer_shortcut() -> None:
    for text in (
        "create ActionCommitPacket",
        "issue ActionCommitPacket",
        "generate action packet",
        "authorize action packet",
    ):
        assert _b4_request_reason(text) == (
            "drs_action_packet_shortcut_forbidden"
        )


def test_g2b_receipt_creation_cannot_take_answer_shortcut() -> None:
    for text in ("create receipt", "issue receipt", "generate receipt"):
        assert _b4_request_reason(text) == (
            "drs_receipt_creation_shortcut_forbidden"
        )
    assert _b4_request_reason("explain receipt requirements") is None
    assert _b4_request_reason("execute maintenance") == (
        "drs_action_intent_shortcut_forbidden"
    )
    assert _b4_request_reason("summarize maintenance intervals") is None
    assert _b4_request_reason("explain passport requirements") is None


def test_g2b_caller_boolean_cannot_authorize_shortcut() -> None:
    from hedgehog.root_orchestrator import RootOrchestrator

    signature = inspect.signature(RootOrchestrator.process_event)
    assert tuple(signature.parameters)[-2:] == (
        "g2b_resolution_report",
        "g2b_use_time",
    )
    assert signature.parameters["allow_direct_reuse"].default is False
    assert signature.parameters["g2b_resolution_report"].default is None
    assert signature.parameters["g2b_use_time"].default is None


def test_g2b_valid_informational_shortcut_skips_only_allowed_heavy_actors() -> None:
    fixture = _b4_fixture()
    assert _b4_validate(fixture) == (True, ())
    assert {
        "root_kernel_id": fixture["root_kernel"].kernel_id,
        "root_input_id": fixture["root_input"].decision_input_id,
        "root_result_id": fixture["root_result"].decision_id,
        "root_result_binding_hash": fixture[
            "root_result_binding_hash"
        ],
        "selected_candidate_id": fixture[
            "selected_candidate"
        ].resolution_candidate_id,
        "projection_id": fixture[
            "projection"
        ].root_shortcut_projection_id,
        "certificate_id": fixture["certificate"].certificate_id,
        "report_id": fixture["report"].report_id,
        "use_time": fixture["use_time"],
    } == _B4_IDENTITY_VECTORS
    assert fixture["selected_record"].semantic_address.intent_class in (
        "informational_summary",
        "informational_lookup",
        "informational_explanation",
        "context_lookup",
        "warning_lookup",
        "historical_inspection",
        "trend_analysis",
    )
    assert _b4_request_reason("explain passport requirements") is None
    report_mutations = (
        {"root_shortcut_projection": None},
        {"reuse_certificate": None},
        {
            "ranked_candidate_ids": tuple(
                reversed(fixture["report"].ranked_candidate_ids)
            )
        },
        {"selected_candidate_id": None},
        {"source_records": fixture["report"].source_records[1:]},
        {
            "source_records": tuple(
                reversed(fixture["report"].source_records)
            )
        },
        {
            "query_evaluations": (
                fixture["report"].query_evaluations[1:]
            )
        },
        {
            "eligible_candidates": (
                fixture["report"].eligible_candidates[1:]
            )
        },
        {"final_status": "FAIL"},
        {"reason_codes": ("drs_resolution_report_binding_invalid",)},
        {"persistent_records_unchanged": False},
        {"provider_calls": 1},
        {"network_calls": 1},
        {"gemini_calls": 1},
        {"external_drs_calls": 1},
        {"connector_calls": 1},
        {"real_world_effects_count": 1},
    )
    for changes in report_mutations:
        forged_report = _reidentify(
            replace(fixture["report"], **changes)
        )
        valid, reasons = _b4_validate(
            fixture,
            report=forged_report,
        )
        assert valid is False, repr(changes)
        assert reasons


def test_g2b_drs_cannot_create_final_output() -> None:
    fixture = _b4_fixture()
    assert fixture["projection"].creates_final_output is False
    assert fixture["selected_record"].creates_authority is False
    assert fixture["selected_record"].creates_permission is False
    assert not hasattr(resolution, "build_final_output_v01")


def test_g2b_certificate_cannot_create_final_output() -> None:
    fixture = _b4_fixture()
    assert fixture["certificate"].creates_final_output is False
    assert fixture["certificate"].creates_authority is False
    assert fixture["certificate"].creates_permission is False
    assert fixture["certificate"].real_world_effects_count == 0
