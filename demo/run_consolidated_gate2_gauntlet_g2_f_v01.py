from __future__ import annotations
import dataclasses
import hashlib
import json
import hedgehog.action_commit_packet_v02 as action_packet
import hedgehog.context_packets as context_packets
import hedgehog.drs_g2b_compatibility_v01 as compatibility
import hedgehog.drs_memory_resolution_v01 as resolution
import hedgehog.drs_semantic_address_v01 as semantic
import hedgehog.kernel.abi_v01 as abi
import hedgehog.kernel.continuous_delta_runtime_v01 as continuous_delta
import hedgehog.kernel.execution_mode_router_v01 as router
import hedgehog.kernel.fractal_runtime_v02 as fractal_runtime
import hedgehog.kernel.integrity_replay_v01 as integrity_replay
import hedgehog.kernel.multiroot_v01 as multiroot
import hedgehog.kernel.root_decision_v01 as root_decision
import hedgehog.kernel.semantic_work_v01 as semantic_work
import hedgehog.kernel.transition_registry_v01 as transition_registry
import hedgehog.kernel.trust_model_v01 as trust_model
import hedgehog.reuse_certificate_v01 as reuse
import hedgehog.structured_rationale as structured_rationale
from hedgehog.kernel.integrity_replay_v01 import canonical_json_bytes_v01
from hedgehog.kernel.integrity_replay_v01 import domain_separated_sha256_hex_v01
SHARED_REQUEST_ID = 'transaction:g2f:gate2:v01'
ROOT_ROWS = (('client', 'root:g2f:client', 'domain:g2f:client'), ('supplier', 'root:g2f:supplier', 'domain:g2f:supplier'))
EVALUATION_TIME = 1788134400
VALID_TO_TIME = EVALUATION_TIME + 3600
EVALUATION_UTC = '2026-08-31T00:00:00+00:00'
VALID_TO_UTC = '2026-08-31T01:00:00+00:00'
PACKET_EVALUATION_TIME = 1783470600
PACKET_VALID_FROM_TIME = 1783468800
PACKET_VALID_TO_TIME = EVALUATION_TIME + 3600
G2B_EVIDENCE_CLASSES = ('SOURCE_IDENTITY', 'SOURCE_INTEGRITY', 'PROVENANCE_CHAIN', 'TIME_FITNESS', 'POLICY_COMPATIBILITY', 'SCHEMA_COMPATIBILITY', 'CONFLICT_CLEARANCE', 'ROOT_DECISION', 'SOURCE_HISTORY')
ROOT_BINDING_DOMAIN = 'hedgehog:drs:root_shortcut_root_result_binding:v01'
ROOT_PREDICATE = 'authorize_non_action_informational_answer_shortcut_v01'
ROOT_POLICY_REF = 'policy:drs_answer_shortcut:v0.1'
PRODUCER_BASIS_SHA256 = 'f78aedd408138603d78f249178e171c48b0338e7aa331293f0832cbb27815b0d'
CAUSAL_PARENT_ROWS_SHA256 = '27bf519714bd384e45aca540b849e93c572cb917afa0220257f21ef9068ae96a'
G2F_EXECUTION_CONTRACT_V01 = ((1, semantic.build_semantic_address_v01, ('client', 'supplier'), (semantic.validate_semantic_address_v01,), 1, 'standalone', 'ROOT_LOCAL_QUERY_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (2, semantic.build_drs_time_envelope_v01, ('client', 'supplier'), (semantic.validate_drs_time_envelope_v01,), 2, 'standalone', 'ROOT_LOCAL_QUERY_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (3, semantic.build_drs_authority_envelope_v01, ('client', 'supplier'), (semantic.validate_drs_authority_envelope_v01,), 3, 'standalone', 'ROOT_LOCAL_QUERY_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (4, semantic.build_meaning_record_v01, ('client', 'supplier'), (semantic.validate_meaning_record_v01,), 4, 'standalone', 'ROOT_LOCAL_QUERY_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (5, resolution.build_drs_temporal_query_v01, ('client', 'supplier'), (resolution.validate_drs_temporal_query_v01,), 5, 'standalone', 'ROOT_LOCAL_QUERY_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (6, resolution.evaluate_drs_candidate_v01, ('client', 'supplier'), (resolution.validate_query_evaluation_state_v01,), 6, 'standalone', 'ROOT_LOCAL_QUERY_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (7, compatibility.build_legacy_drs_projection_v01, ('client', 'supplier'), (compatibility.validate_legacy_drs_projection_v01,), 7, 'standalone', 'ROOT_LOCAL_QUERY_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (8, resolution.build_memory_descent_budget_v01, ('client', 'supplier'), (resolution.validate_memory_descent_budget_v01,), 8, 'standalone', 'ROOT_LOCAL_QUERY_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (9, resolution.build_retrieval_plan_v01, ('client', 'supplier'), (resolution.validate_retrieval_plan_v01,), 9, 'standalone', 'ROOT_LOCAL_QUERY_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (10, resolution.build_resolution_candidate_v01, ('client', 'supplier'), (resolution.validate_resolution_candidate_v01,), 10, 'standalone', 'ROOT_LOCAL_QUERY_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (11, resolution.rank_eligible_drs_candidates_v01, ('client', 'supplier'), (resolution.validate_resolution_candidate_v01,), 11, 'standalone', 'ROOT_LOCAL_QUERY_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (12, root_decision.build_root_decision_kernel_v01, ('client', 'supplier'), (root_decision.validate_root_decision_kernel_v01,), 12, 'standalone', 'ROOT_LOCAL_QUERY_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (13, semantic_work.build_semantic_work_request_v01, ('client', 'supplier'), (semantic_work.validate_semantic_work_request_v01,), 13, 'standalone', 'ROOT_LOCAL_QUERY_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (14, semantic_work.build_evidence_binding_v01, ('client', 'supplier'), (semantic_work.validate_actor_contribution_v01,), 17, 'enclosing_public_consumer', 'ROOT_LOCAL_QUERY_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (15, semantic_work.build_normalized_claim_v01, ('client', 'supplier'), (semantic_work.validate_actor_contribution_v01,), 17, 'enclosing_public_consumer', 'ROOT_LOCAL_QUERY_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (16, semantic_work.build_actor_contribution_v01, ('client', 'supplier'), (semantic_work.validate_actor_contribution_v01,), 17, 'enclosing_public_consumer', 'ROOT_LOCAL_QUERY_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (17, trust_model.build_default_component_trust_profiles_v01, ('client', 'supplier'), (trust_model.validate_component_trust_profiles_v01,), 17, 'standalone', 'ROOT_LOCAL_QUERY_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (18, semantic_work.build_root_review_packet_from_contributions_v01, ('client', 'supplier'), (semantic_work.validate_root_review_packet_v01,), 18, 'standalone', 'ROOT_LOCAL_QUERY_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (19, root_decision.build_root_decision_input_v01, ('client', 'supplier'), (root_decision.validate_root_decision_input_v01,), 19, 'standalone', 'ROOT_LOCAL_QUERY_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (20, root_decision.decide_root_v01, ('client', 'supplier'), (root_decision.validate_root_decision_result_v01,), 20, 'standalone', 'ROOT_LOCAL_QUERY_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (21, reuse.build_root_shortcut_authorization_projection_v01, ('client', 'supplier'), (reuse.validate_root_shortcut_authorization_projection_v01,), 21, 'standalone', 'ROOT_LOCAL_QUERY_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (22, reuse.build_reuse_certificate_v01, ('client', 'supplier'), (reuse.validate_reuse_certificate_v01,), 22, 'standalone', 'ROOT_LOCAL_QUERY_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (23, resolution.build_drs_resolution_report_v01, ('client', 'supplier'), (resolution.validate_drs_resolution_report_v01,), 23, 'standalone', 'ROOT_LOCAL_QUERY_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (24, reuse.validate_existing_root_shortcut_decision_v01, ('client', 'supplier'), (reuse.validate_existing_root_shortcut_decision_v01,), 24, 'producer_validation_result', 'ROOT_LOCAL_QUERY_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (25, semantic.build_semantic_address_v01, ('client',), (semantic.validate_semantic_address_v01,), 25, 'standalone', 'CLIENT_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (26, resolution.evaluate_drs_candidate_v01, ('client',), (resolution.validate_query_evaluation_state_v01,), 26, 'standalone', 'CLIENT_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (27, semantic_work.build_semantic_work_request_v01, ('client',), (semantic_work.validate_semantic_work_request_v01,), 27, 'standalone', 'CLIENT_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (28, semantic_work.build_evidence_binding_v01, ('client',), (semantic_work.validate_actor_contribution_v01,), 30, 'enclosing_public_consumer', 'CLIENT_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (29, semantic_work.build_normalized_claim_v01, ('client',), (semantic_work.validate_actor_contribution_v01,), 30, 'enclosing_public_consumer', 'CLIENT_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (30, semantic_work.build_actor_contribution_v01, ('client',), (semantic_work.validate_actor_contribution_v01,), 30, 'standalone', 'CLIENT_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (31, semantic_work.build_root_review_packet_from_contributions_v01, ('client',), (semantic_work.validate_root_review_packet_v01,), 31, 'standalone', 'CLIENT_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (32, root_decision.build_root_decision_input_v01, ('client',), (root_decision.validate_root_decision_input_v01,), 32, 'standalone', 'CLIENT_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (33, root_decision.decide_root_v01, ('client',), (root_decision.validate_root_decision_result_v01,), 33, 'standalone', 'CLIENT_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (34, resolution.build_memory_descent_request_v01, ('client',), (resolution.validate_memory_descent_request_v01,), 34, 'standalone', 'CLIENT_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (35, resolution.execute_local_memory_descent_v01, ('client',), (resolution.validate_memory_descent_result_v01,), 35, 'standalone', 'CLIENT_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (36, context_packets.build_business_request_context_packet, ('client', 'supplier'), (context_packets.validate_business_request_context_packet,), 36, 'standalone', 'ROOT_LOCAL_QUERY_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (37, context_packets.build_orchestrator_route_context_packet, ('client', 'supplier'), (context_packets.validate_orchestrator_route_context_packet,), 37, 'standalone', 'ROOT_LOCAL_QUERY_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (38, structured_rationale.build_orchestrator_structured_rationale, ('client', 'supplier'), (structured_rationale.validate_orchestrator_structured_rationale,), 38, 'standalone', 'ROOT_LOCAL_QUERY_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (39, context_packets.semantic_evidence_item, ('client', 'supplier'), (context_packets.validate_semantic_evidence_items,), 39, 'standalone', 'ROOT_LOCAL_QUERY_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (40, context_packets.build_bounded_semantic_evidence_packet, ('client', 'supplier'), (context_packets.validate_bounded_semantic_evidence_packet,), 40, 'standalone', 'ROOT_LOCAL_QUERY_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (41, router.build_execution_mode_local_mode_profile_v01, ('client', 'supplier'), (router.validate_execution_mode_local_mode_profile_v01,), 41, 'standalone', 'ROOT_LOCAL_G2C_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (42, router.build_execution_mode_local_routing_snapshot_v01, ('client', 'supplier'), (router.validate_execution_mode_local_routing_snapshot_v01,), 42, 'standalone', 'ROOT_LOCAL_G2C_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (43, router.build_execution_mode_source_context_v01, ('client', 'supplier'), (router.validate_execution_mode_source_context_v01,), 43, 'standalone', 'ROOT_LOCAL_G2C_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (44, router.build_execution_mode_bsep_binding_v01, ('client', 'supplier'), (router.validate_execution_mode_bsep_binding_v01,), 44, 'standalone', 'ROOT_LOCAL_G2C_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (45, router.build_execution_mode_replay_not_applicable_binding_v01, ('client', 'supplier'), (router.validate_execution_mode_replay_binding_v01,), 45, 'standalone', 'ROOT_LOCAL_G2C_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (46, router.build_execution_mode_g2a_no_packet_binding_v01, ('client', 'supplier'), (router.validate_execution_mode_g2a_binding_v01,), 46, 'standalone', 'ROOT_LOCAL_G2C_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (47, router.build_execution_mode_g2b_binding_v01, ('client', 'supplier'), (router.validate_execution_mode_g2b_binding_v01,), 47, 'standalone', 'ROOT_LOCAL_G2C_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (48, router.build_execution_mode_router_input_v01, ('client', 'supplier'), (router.validate_execution_mode_router_input_v01, router.validate_execution_mode_router_input_against_sources_v01), 48, 'standalone', 'ROOT_LOCAL_G2C_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (49, router.evaluate_execution_mode_feasibility_v01, ('client', 'supplier'), (router.validate_execution_mode_feasibility_row_v01,), 49, 'standalone', 'ROOT_LOCAL_G2C_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (50, router.select_execution_mode_v01, ('client', 'supplier'), (router.validate_execution_mode_feasibility_row_v01,), 50, 'standalone', 'ROOT_LOCAL_G2C_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (51, router.build_execution_mode_proposal_v01, ('client', 'supplier'), (router.validate_execution_mode_proposal_v01, router.validate_execution_mode_proposal_against_sources_v01), 51, 'standalone', 'ROOT_LOCAL_G2C_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (52, router.route_execution_mode_v01, ('client', 'supplier'), (router.validate_execution_mode_validation_report_v01, router.validate_execution_mode_proposal_against_sources_v01), 52, 'public_producer_internal', 'ROOT_LOCAL_G2C_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (53, router.project_execution_mode_proposal_kernel_artifact_v01, ('client', 'supplier'), (abi.validate_kernel_artifact_v01,), 53, 'standalone', 'ROOT_LOCAL_G2C_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (54, transition_registry.build_execution_mode_transition_registry_profile_v01, ('shared',), (transition_registry.validate_execution_mode_transition_registry_profile_v01,), 54, 'standalone', 'SHARED_IMMUTABLE_PROFILE', 'CURRENT_VALIDATOR_ENFORCED'), (55, router.evaluate_execution_mode_proposal_to_root_transition_v01, ('client', 'supplier'), (transition_registry.validate_execution_mode_transition_decision_v01,), 55, 'standalone', 'ROOT_LOCAL_G2C_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (56, router.build_root_execution_mode_review_input_v01, ('client', 'supplier'), (router.validate_root_execution_mode_review_input_v01, router.validate_root_execution_mode_review_input_against_sources_v01), 56, 'standalone', 'ROOT_LOCAL_G2C_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (57, router.review_execution_mode_proposal_v01, ('client', 'supplier'), (router.validate_root_execution_mode_decision_v01, router.validate_root_execution_mode_decision_against_source_v01, router.validate_execution_mode_validation_report_v01), 57, 'public_producer_internal', 'ROOT_LOCAL_G2C_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (58, router.project_root_execution_mode_decision_kernel_artifact_v01, ('client', 'supplier'), (abi.validate_kernel_artifact_v01,), 58, 'standalone', 'ROOT_LOCAL_G2C_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (59, router.evaluate_execution_mode_root_route_transition_v01, ('client', 'supplier'), (transition_registry.validate_execution_mode_transition_decision_v01,), 59, 'standalone', 'ROOT_LOCAL_G2C_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (60, router.project_execution_mode_route_eligibility_kernel_artifact_v01, ('client', 'supplier'), (abi.validate_kernel_artifact_v01,), 60, 'standalone', 'ROOT_LOCAL_G2C_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (61, router.validate_execution_mode_route_eligibility_against_source_v01, ('client', 'supplier'), (router.validate_execution_mode_validation_report_v01,), 61, 'public_producer_internal', 'ROOT_LOCAL_G2C_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (62, multiroot.build_cross_root_evidence_ref_v01, ('client', 'supplier'), (multiroot.validate_cross_root_evidence_ref_v01,), 62, 'standalone', 'PARENT_CORRELATION_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (63, multiroot.build_root_decision_envelope_v01, ('client', 'supplier'), (multiroot.validate_root_decision_envelope_v01,), 63, 'standalone', 'PARENT_CORRELATION_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED+FUTURE_G2F_REPORT_VALIDATOR_REQUIRED'), (64, multiroot.build_transaction_outcome_envelope_v01, ('parent',), (multiroot.validate_transaction_outcome_envelope_v01,), 64, 'standalone', 'PARENT_CORRELATION_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (65, multiroot.validate_multiroot_v01, ('parent',), (multiroot.validate_multiroot_v01,), 65, 'producer_validation_result', 'PARENT_CORRELATION_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (66, multiroot.transaction_outcome_envelope_to_plain_dict_v01, ('parent',), (multiroot.validate_transaction_outcome_envelope_v01,), 64, 'enclosing_public_consumer', 'PARENT_CORRELATION_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (67, fractal_runtime.build_fractal_runtime_policy_v02, ('client', 'supplier'), (fractal_runtime.validate_fractal_runtime_policy_v02,), 67, 'standalone', 'ROOT_LOCAL_G2D_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (68, fractal_runtime.build_fractal_runtime_source_context_v02, ('client', 'supplier'), (fractal_runtime.validate_fractal_runtime_source_context_v02,), 68, 'standalone', 'ROOT_LOCAL_G2D_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (69, fractal_runtime.run_fractal_runtime_v02, ('client', 'supplier'), (fractal_runtime.validate_fractal_runtime_execution_bundle_v02, fractal_runtime.validate_runtime_execution_topology_v02, fractal_runtime.validate_fractal_cell_result_v02, fractal_runtime.validate_fractal_cell_result_proposal_v02, fractal_runtime.validate_fractal_post_vv_report_v02, fractal_runtime.validate_fractal_gt_advisory_v02), 69, 'public_producer_internal', 'ROOT_LOCAL_G2D_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (70, action_packet.ActionCommitPacketV02, ('supplier',), (action_packet.validate_action_commit_packet_v02,), 70, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (71, action_packet.build_action_dependency_time_envelope_id_v01, ('supplier',), (action_packet.validate_action_dependency_time_envelope_binding_v01,), 71, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (72, action_packet.build_dependency_set_candidate_record_v01, ('supplier',), (action_packet.validate_dependency_set_candidate_record_v01,), 72, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (73, action_packet.build_dependency_set_candidate_v01, ('supplier',), (action_packet.validate_dependency_set_candidate_v01,), 73, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (74, action_packet.build_action_authority_policy_profile_v01, ('supplier',), (action_packet.validate_action_authority_policy_profile_v01,), 74, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (75, action_packet.build_supplier_action_commit_packet_canonical_projection_v01, ('supplier',), (action_packet.validate_supplier_action_commit_packet_canonical_projection_v01,), 75, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED+FUTURE_G2F_REPORT_VALIDATOR_REQUIRED'), (76, semantic_work.build_semantic_work_request_v01, ('supplier',), (semantic_work.validate_semantic_work_request_v01,), 76, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (77, semantic_work.build_evidence_binding_v01, ('supplier',), (semantic_work.validate_actor_contribution_v01,), 79, 'enclosing_public_consumer', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (78, semantic_work.build_normalized_claim_v01, ('supplier',), (semantic_work.validate_actor_contribution_v01,), 79, 'enclosing_public_consumer', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (79, semantic_work.build_actor_contribution_v01, ('supplier',), (semantic_work.validate_actor_contribution_v01,), 79, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (80, semantic_work.build_root_review_packet_from_contributions_v01, ('supplier',), (semantic_work.validate_root_review_packet_v01,), 80, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (81, root_decision.build_root_decision_input_v01, ('supplier',), (root_decision.validate_root_decision_input_v01,), 81, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (82, root_decision.decide_root_v01, ('supplier',), (root_decision.validate_root_decision_result_v01,), 82, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (83, action_packet.build_root_decision_candidate_projection_v01, ('supplier',), (action_packet.validate_root_decision_candidate_projection_v01, action_packet.validate_supplier_root_context_coherence_v01), 83, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (84, action_packet.build_supplier_root_bound_action_commit_packet_v02_projection_v01, ('supplier',), (action_packet.validate_supplier_root_bound_action_commit_packet_v02_projection_v01,), 84, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (85, transition_registry.build_action_packet_transition_registry_profile_v01, ('supplier',), (transition_registry.validate_action_packet_transition_registry_profile_v01,), 85, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (86, action_packet.build_empty_action_commit_packet_registry_v02, ('supplier',), (action_packet.validate_action_commit_packet_registry_v02,), 86, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (87, action_packet.record_action_packet_genesis_v01, ('supplier',), (action_packet.validate_action_commit_packet_registry_v02,), 87, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (88, action_packet.build_transition_evidence_binding_v01, ('supplier',), (action_packet.validate_transition_evidence_binding_v01,), 88, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (89, action_packet.build_action_packet_transition_event_v01, ('supplier',), (action_packet.validate_action_packet_transition_event_v01,), 89, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (90, action_packet.build_idempotency_disposition_event_v01, ('supplier',), (action_packet.validate_idempotency_disposition_history_v01,), 90, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (91, action_packet.activate_action_packet_lifecycle_v01, ('supplier',), (action_packet.validate_action_commit_packet_registry_v02,), 91, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (92, action_packet.build_transition_evidence_binding_v01, ('supplier',), (action_packet.validate_transition_evidence_binding_v01,), 92, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (93, action_packet.build_action_packet_transition_event_v01, ('supplier',), (action_packet.validate_action_packet_transition_event_v01,), 93, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (94, action_packet.append_action_packet_lifecycle_transition_v01, ('supplier',), (action_packet.validate_action_commit_packet_registry_v02, action_packet.validate_action_packet_transition_history_v01), 94, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (95, action_packet.build_action_execution_attempt_identity_v01, ('supplier',), (action_packet.validate_action_execution_attempt_identity_v01,), 95, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (96, action_packet.build_transition_evidence_binding_v01, ('supplier',), (action_packet.validate_transition_evidence_binding_v01,), 96, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (97, action_packet.build_action_packet_transition_event_v01, ('supplier',), (action_packet.validate_action_packet_transition_event_v01,), 97, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (98, action_packet.append_action_packet_lifecycle_transition_v01, ('supplier',), (action_packet.validate_action_commit_packet_registry_v02, action_packet.validate_action_packet_transition_history_v01), 98, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (99, action_packet.CorridorStepV01, ('supplier',), (action_packet.validate_action_packet_present_eligibility_inspection_v01,), 103, 'enclosing_validator', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_CONTEXTUAL_VALIDATOR_ENFORCED_AT_ROW103'), (100, action_packet.ContractFulfillmentCorridorV01, ('supplier',), (action_packet.validate_corridor_no_post_root_reasoning_v01,), 100, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (101, action_packet.build_action_dependency_current_observation_v01, ('supplier',), (action_packet.validate_action_dependency_current_observation_v01,), 101, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (102, action_packet.build_logical_time_bridge_v01, ('supplier',), (action_packet.validate_logical_time_bridge_v01,), 102, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (103, action_packet.inspect_action_packet_present_eligibility_v01, ('supplier',), (action_packet.validate_action_packet_present_eligibility_inspection_v01,), 103, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (104, action_packet.build_action_invalidation_evidence_v01, ('supplier',), (action_packet.validate_action_invalidation_evidence_v01, action_packet.validate_action_invalidation_evidence_against_packet_v01), 104, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (105, abi.build_kernel_artifact_v01, ('supplier',), (abi.validate_kernel_artifact_v01, abi.validate_kernel_artifact_bundle_v01), 105, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (106, integrity_replay.build_artifact_manifest_v01, ('supplier',), (integrity_replay.verify_artifact_manifest_v01,), 106, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (107, integrity_replay.verify_artifact_replay_v01, ('supplier',), (integrity_replay.verify_artifact_replay_v01,), 107, 'producer_validation_result', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (108, continuous_delta.project_integrity_replay_dependency_edges_v01, ('supplier',), (continuous_delta.validate_delta_dependency_edge_v01,), 108, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (109, continuous_delta.build_dependency_graph_index_v01, ('supplier',), (continuous_delta.validate_dependency_graph_index_v01,), 109, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (110, continuous_delta.build_dependency_fingerprint_profile_v01, ('supplier',), (continuous_delta.validate_dependency_fingerprint_profile_v01,), 110, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (111, continuous_delta.build_dependency_fingerprint_v01, ('supplier',), (continuous_delta.validate_delta_source_binding_v01,), 112, 'enclosing_public_consumer', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (112, continuous_delta.build_delta_source_binding_v01, ('supplier',), (continuous_delta.validate_delta_source_binding_v01,), 112, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (113, continuous_delta.build_changed_field_binding_v01, ('supplier',), (continuous_delta.validate_changed_field_binding_v01,), 113, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (114, continuous_delta.build_changed_artifact_binding_v01, ('supplier',), (continuous_delta.validate_changed_artifact_binding_v01,), 114, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (115, continuous_delta.build_world_state_delta_v01, ('supplier',), (continuous_delta.validate_world_state_delta_v01,), 115, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (116, continuous_delta.build_affected_set_request_v01, ('supplier',), (continuous_delta.validate_affected_set_request_v01,), 116, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (117, continuous_delta.compute_affected_set_v01, ('supplier',), (continuous_delta.validate_affected_set_result_v01, continuous_delta.validate_affected_set_against_graph_v01), 117, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (118, continuous_delta.build_continuous_delta_source_context_v01, ('supplier',), (continuous_delta.validate_continuous_delta_source_context_v01,), 118, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (119, continuous_delta.derive_invalidation_report_v01, ('supplier',), (continuous_delta.validate_artifact_invalidation_record_v01, continuous_delta.validate_invalidation_report_v01, continuous_delta.validate_invalidation_report_against_sources_v01), 119, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (120, continuous_delta.run_continuous_delta_runtime_v01, ('supplier',), (continuous_delta.validate_continuous_delta_execution_bundle_v01, continuous_delta.validate_preservation_proof_v01, continuous_delta.validate_selective_recomputation_result_v01, continuous_delta.validate_continuous_delta_runtime_report_v01), 120, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (121, continuous_delta.prove_unaffected_artifact_preservation_v01, ('supplier',), (continuous_delta.validate_preservation_proof_v01,), 121, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (122, semantic_work.build_semantic_work_request_v01, ('supplier',), (semantic_work.validate_semantic_work_request_v01,), 122, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_WITNESS_GUARD_AND_FUTURE_G2F_REPORT_VALIDATOR_REQUIRED'), (123, semantic_work.build_evidence_binding_v01, ('supplier',), (semantic_work.validate_actor_contribution_v01,), 125, 'enclosing_public_consumer', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_WITNESS_GUARD_AND_FUTURE_G2F_REPORT_VALIDATOR_REQUIRED'), (124, semantic_work.build_normalized_claim_v01, ('supplier',), (semantic_work.validate_actor_contribution_v01,), 125, 'enclosing_public_consumer', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_WITNESS_GUARD_AND_FUTURE_G2F_REPORT_VALIDATOR_REQUIRED'), (125, semantic_work.build_actor_contribution_v01, ('supplier',), (semantic_work.validate_actor_contribution_v01,), 125, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_WITNESS_GUARD_AND_FUTURE_G2F_REPORT_VALIDATOR_REQUIRED'), (126, semantic_work.build_root_review_packet_from_contributions_v01, ('supplier',), (semantic_work.validate_root_review_packet_v01,), 126, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_WITNESS_GUARD_AND_FUTURE_G2F_REPORT_VALIDATOR_REQUIRED'), (127, root_decision.build_root_decision_input_v01, ('supplier',), (root_decision.validate_root_decision_input_v01,), 127, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_WITNESS_GUARD_AND_FUTURE_G2F_REPORT_VALIDATOR_REQUIRED'), (128, root_decision.decide_root_v01, ('supplier',), (root_decision.validate_root_decision_result_v01,), 128, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_WITNESS_GUARD_AND_FUTURE_G2F_REPORT_VALIDATOR_REQUIRED'), (129, action_packet.build_action_invalidation_evidence_v01, ('supplier',), (action_packet.validate_action_invalidation_evidence_v01,), 129, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_WITNESS_GUARD_AND_FUTURE_G2F_REPORT_VALIDATOR_REQUIRED'), (130, action_packet.build_revocation_candidate_v01, ('supplier',), (action_packet.validate_revocation_candidate_v01, action_packet.validate_revocation_candidate_against_packet_v01), 130, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_WITNESS_GUARD_AND_FUTURE_G2F_REPORT_VALIDATOR_REQUIRED'), (131, semantic_work.build_semantic_work_request_v01, ('supplier',), (semantic_work.validate_semantic_work_request_v01,), 131, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_WITNESS_GUARD_AND_FUTURE_G2F_REPORT_VALIDATOR_REQUIRED'), (132, semantic_work.build_evidence_binding_v01, ('supplier',), (semantic_work.validate_actor_contribution_v01,), 134, 'enclosing_public_consumer', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_WITNESS_GUARD_AND_FUTURE_G2F_REPORT_VALIDATOR_REQUIRED'), (133, semantic_work.build_normalized_claim_v01, ('supplier',), (semantic_work.validate_actor_contribution_v01,), 134, 'enclosing_public_consumer', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_WITNESS_GUARD_AND_FUTURE_G2F_REPORT_VALIDATOR_REQUIRED'), (134, semantic_work.build_actor_contribution_v01, ('supplier',), (semantic_work.validate_actor_contribution_v01,), 134, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_WITNESS_GUARD_AND_FUTURE_G2F_REPORT_VALIDATOR_REQUIRED'), (135, semantic_work.build_root_review_packet_from_contributions_v01, ('supplier',), (semantic_work.validate_root_review_packet_v01,), 135, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_WITNESS_GUARD_AND_FUTURE_G2F_REPORT_VALIDATOR_REQUIRED'), (136, root_decision.build_root_decision_input_v01, ('supplier',), (root_decision.validate_root_decision_input_v01,), 136, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_WITNESS_GUARD_AND_FUTURE_G2F_REPORT_VALIDATOR_REQUIRED'), (137, root_decision.decide_root_v01, ('supplier',), (root_decision.validate_root_decision_result_v01,), 137, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_WITNESS_GUARD_AND_FUTURE_G2F_REPORT_VALIDATOR_REQUIRED'), (138, action_packet.build_root_decision_candidate_projection_v01, ('supplier',), (action_packet.validate_root_decision_candidate_projection_v01, action_packet.validate_revocation_root_context_coherence_v01), 138, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (139, action_packet.build_accepted_revocation_binding_v01, ('supplier',), (action_packet.validate_accepted_revocation_binding_v01,), 139, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (140, action_packet.build_action_invalidation_evidence_v01, ('supplier',), (action_packet.validate_action_invalidation_evidence_v01, action_packet.validate_action_invalidation_evidence_against_packet_v01), 140, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (141, action_packet.build_transition_evidence_binding_v01, ('supplier',), (action_packet.validate_transition_evidence_binding_v01,), 141, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (142, action_packet.build_action_packet_transition_event_v01, ('supplier',), (action_packet.validate_action_packet_transition_event_v01,), 142, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (143, action_packet.record_action_packet_revocation_v01, ('supplier',), (action_packet.validate_action_commit_packet_registry_v02, action_packet.validate_action_packet_transition_history_v01), 143, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (144, action_packet.inspect_action_packet_present_eligibility_v01, ('supplier',), (action_packet.validate_action_packet_present_eligibility_inspection_v01,), 144, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (145, action_packet.build_supplier_action_commit_packet_canonical_projection_v01, ('supplier',), (action_packet.validate_supplier_action_commit_packet_canonical_projection_v01,), 145, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (146, semantic_work.build_semantic_work_request_v01, ('supplier',), (semantic_work.validate_semantic_work_request_v01,), 146, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_WITNESS_GUARD_AND_FUTURE_G2F_REPORT_VALIDATOR_REQUIRED'), (147, semantic_work.build_evidence_binding_v01, ('supplier',), (semantic_work.validate_actor_contribution_v01,), 149, 'enclosing_public_consumer', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_WITNESS_GUARD_AND_FUTURE_G2F_REPORT_VALIDATOR_REQUIRED'), (148, semantic_work.build_normalized_claim_v01, ('supplier',), (semantic_work.validate_actor_contribution_v01,), 149, 'enclosing_public_consumer', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_WITNESS_GUARD_AND_FUTURE_G2F_REPORT_VALIDATOR_REQUIRED'), (149, semantic_work.build_actor_contribution_v01, ('supplier',), (semantic_work.validate_actor_contribution_v01,), 149, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_WITNESS_GUARD_AND_FUTURE_G2F_REPORT_VALIDATOR_REQUIRED'), (150, semantic_work.build_root_review_packet_from_contributions_v01, ('supplier',), (semantic_work.validate_root_review_packet_v01,), 150, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_WITNESS_GUARD_AND_FUTURE_G2F_REPORT_VALIDATOR_REQUIRED'), (151, root_decision.build_root_decision_input_v01, ('supplier',), (root_decision.validate_root_decision_input_v01,), 151, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_WITNESS_GUARD_AND_FUTURE_G2F_REPORT_VALIDATOR_REQUIRED'), (152, root_decision.decide_root_v01, ('supplier',), (root_decision.validate_root_decision_result_v01,), 152, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_WITNESS_GUARD_AND_FUTURE_G2F_REPORT_VALIDATOR_REQUIRED'), (153, action_packet.build_root_decision_candidate_projection_v01, ('supplier',), (action_packet.validate_root_decision_candidate_projection_v01, action_packet.validate_supplier_root_context_coherence_v01), 153, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (154, action_packet.build_supplier_root_bound_action_commit_packet_v02_projection_v01, ('supplier',), (action_packet.validate_supplier_root_bound_action_commit_packet_v02_projection_v01,), 154, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (155, action_packet.record_action_packet_genesis_v01, ('supplier',), (action_packet.validate_action_commit_packet_registry_v02,), 155, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (156, action_packet.build_supersession_candidate_v01, ('supplier',), (action_packet.validate_supersession_candidate_v01, action_packet.validate_supersession_candidate_against_packets_v01), 156, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (157, semantic_work.build_semantic_work_request_v01, ('supplier',), (semantic_work.validate_semantic_work_request_v01,), 157, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_WITNESS_GUARD_AND_FUTURE_G2F_REPORT_VALIDATOR_REQUIRED'), (158, semantic_work.build_evidence_binding_v01, ('supplier',), (semantic_work.validate_actor_contribution_v01,), 160, 'enclosing_public_consumer', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_WITNESS_GUARD_AND_FUTURE_G2F_REPORT_VALIDATOR_REQUIRED'), (159, semantic_work.build_normalized_claim_v01, ('supplier',), (semantic_work.validate_actor_contribution_v01,), 160, 'enclosing_public_consumer', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_WITNESS_GUARD_AND_FUTURE_G2F_REPORT_VALIDATOR_REQUIRED'), (160, semantic_work.build_actor_contribution_v01, ('supplier',), (semantic_work.validate_actor_contribution_v01,), 160, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_WITNESS_GUARD_AND_FUTURE_G2F_REPORT_VALIDATOR_REQUIRED'), (161, semantic_work.build_root_review_packet_from_contributions_v01, ('supplier',), (semantic_work.validate_root_review_packet_v01,), 161, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_WITNESS_GUARD_AND_FUTURE_G2F_REPORT_VALIDATOR_REQUIRED'), (162, root_decision.build_root_decision_input_v01, ('supplier',), (root_decision.validate_root_decision_input_v01,), 162, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_WITNESS_GUARD_AND_FUTURE_G2F_REPORT_VALIDATOR_REQUIRED'), (163, root_decision.decide_root_v01, ('supplier',), (root_decision.validate_root_decision_result_v01,), 163, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_WITNESS_GUARD_AND_FUTURE_G2F_REPORT_VALIDATOR_REQUIRED'), (164, action_packet.build_root_decision_candidate_projection_v01, ('supplier',), (action_packet.validate_root_decision_candidate_projection_v01, action_packet.validate_supersession_root_context_coherence_v01), 164, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (165, action_packet.build_accepted_supersession_binding_v01, ('supplier',), (action_packet.validate_accepted_supersession_binding_v01, action_packet.validate_action_packet_renewal_relationship_v01), 165, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (166, action_packet.build_action_invalidation_evidence_v01, ('supplier',), (action_packet.validate_action_invalidation_evidence_v01, action_packet.validate_action_invalidation_evidence_against_packet_v01), 166, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (167, action_packet.build_transition_evidence_binding_v01, ('supplier',), (action_packet.validate_transition_evidence_binding_v01,), 167, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (168, action_packet.build_action_packet_transition_event_v01, ('supplier',), (action_packet.validate_action_packet_transition_event_v01,), 168, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (169, action_packet.build_transition_evidence_binding_v01, ('supplier',), (action_packet.validate_transition_evidence_binding_v01,), 169, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (170, action_packet.build_action_packet_transition_event_v01, ('supplier',), (action_packet.validate_action_packet_transition_event_v01,), 170, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (171, action_packet.build_idempotency_disposition_event_v01, ('supplier',), (action_packet.validate_idempotency_disposition_event_v01, action_packet.validate_idempotency_disposition_history_v01), 171, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (172, action_packet.record_action_packet_supersession_v01, ('supplier',), (action_packet.validate_action_commit_packet_registry_v02,), 172, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (173, action_packet.build_transition_evidence_binding_v01, ('supplier',), (action_packet.validate_transition_evidence_binding_v01,), 173, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (174, action_packet.build_action_packet_transition_event_v01, ('supplier',), (action_packet.validate_action_packet_transition_event_v01,), 174, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (175, action_packet.append_action_packet_lifecycle_transition_v01, ('supplier',), (action_packet.validate_action_commit_packet_registry_v02,), 175, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (176, action_packet.build_action_execution_attempt_identity_v01, ('supplier',), (action_packet.validate_action_execution_attempt_identity_v01,), 176, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (177, action_packet.build_transition_evidence_binding_v01, ('supplier',), (action_packet.validate_transition_evidence_binding_v01,), 177, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (178, action_packet.build_action_packet_transition_event_v01, ('supplier',), (action_packet.validate_action_packet_transition_event_v01,), 178, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (179, action_packet.append_action_packet_lifecycle_transition_v01, ('supplier',), (action_packet.validate_action_commit_packet_registry_v02,), 179, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (180, action_packet.replay_action_packet_lifecycle_history_v01, ('supplier',), (action_packet.validate_action_packet_lifecycle_replay_report_v01,), 180, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'), (181, action_packet.inspect_action_packet_present_eligibility_v01, ('supplier',), (action_packet.validate_action_packet_present_eligibility_inspection_v01,), 181, 'standalone', 'SUPPLIER_ROOT_LOCAL_TRANSACTION', 'CURRENT_VALIDATOR_ENFORCED'))

def collect_consolidated_gate2_gauntlet_g2_f_v01():
    row_receipts = []
    component_receipts = []
    auxiliary_receipts = []
    validation_events = []

    def assert_equal(actual: object, expected: object, marker: str) -> None:
        """Assert equality only; this helper never constructs or validates a carrier."""
        if actual != expected:
            raise RuntimeError(marker + ':' + repr((actual, expected)))

    def plain_sha256(value: object) -> str:
        """Hash canonical public plain evidence; this never constructs a carrier."""
        return hashlib.sha256(canonical_json_bytes_v01(value)).hexdigest()

    def pointer_token(value: str) -> str:
        """Encode one RFC-6901 evidence pointer token."""
        return value.replace('~', '~0').replace('/', '~1')

    def plain_difference_rows(before: object, after: object, *, prefix: str='') -> tuple[dict[str, object], ...]:
        """Return exhaustive canonical evidence differences without making a carrier."""
        rows: list[dict[str, object]] = []
        if type(before) is dict and type(after) is dict:
            before_map = before
            after_map = after
            for key in sorted(set(before_map) | set(after_map)):
                pointer = prefix + '/' + pointer_token(key)
                if key not in before_map:
                    rows.append({'pointer': pointer, 'before_present': False, 'before_value': None, 'before_value_sha256': None, 'after_present': True, 'after_value': after_map[key], 'after_value_sha256': plain_sha256(after_map[key])})
                elif key not in after_map:
                    rows.append({'pointer': pointer, 'before_present': True, 'before_value': before_map[key], 'before_value_sha256': plain_sha256(before_map[key]), 'after_present': False, 'after_value': None, 'after_value_sha256': None})
                else:
                    rows.extend(plain_difference_rows(before_map[key], after_map[key], prefix=pointer))
            return tuple(rows)
        if type(before) is list and type(after) is list:
            for index in range(max(len(before), len(after))):
                pointer = prefix + '/' + str(index)
                if index >= len(before):
                    rows.append({'pointer': pointer, 'before_present': False, 'before_value': None, 'before_value_sha256': None, 'after_present': True, 'after_value': after[index], 'after_value_sha256': plain_sha256(after[index])})
                elif index >= len(after):
                    rows.append({'pointer': pointer, 'before_present': True, 'before_value': before[index], 'before_value_sha256': plain_sha256(before[index]), 'after_present': False, 'after_value': None, 'after_value_sha256': None})
                else:
                    rows.extend(plain_difference_rows(before[index], after[index], prefix=pointer))
            return tuple(rows)
        if canonical_json_bytes_v01(before) != canonical_json_bytes_v01(after):
            rows.append({'pointer': prefix, 'before_present': True, 'before_value': before, 'before_value_sha256': plain_sha256(before), 'after_present': True, 'after_value': after, 'after_value_sha256': plain_sha256(after)})
        return tuple(rows)

    def independently_derive_partitions(node_ids: tuple[str, ...], relation_rows: tuple[tuple[str, str, tuple[str, ...], str], ...], changed_ids: tuple[str, ...]) -> dict[str, tuple[str, ...]]:
        """Traverse the frozen scenario relation as independent receipt evidence."""
        positions = {node_id: index for index, node_id in enumerate(node_ids)}
        distance = {node_id: 0 for node_id in changed_ids}
        frontier = list(changed_ids)
        while frontier:
            dependency_id = frontier.pop(0)
            dependents = tuple((row[0] for row in relation_rows if row[1] == dependency_id))
            for dependent_id in dependents:
                if dependent_id not in distance:
                    distance[dependent_id] = distance[dependency_id] + 1
                    frontier.append(dependent_id)
        affected = tuple(sorted((node_id for node_id in distance if distance[node_id] > 0), key=lambda node_id: (distance[node_id], positions[node_id], node_id)))
        direct = tuple((node_id for node_id in affected if distance[node_id] == 1))
        transitive = tuple((node_id for node_id in affected if distance[node_id] > 1))
        excluded = set(changed_ids) | set(affected)
        unaffected = tuple((node_id for node_id in node_ids if node_id not in excluded))
        return {'changed': changed_ids, 'direct': direct, 'transitive': transitive, 'affected': affected, 'unaffected': unaffected}

    def evidence_plain(value: object) -> object:
        """Return deterministic plain evidence without mutating a runtime carrier."""
        if dataclasses.is_dataclass(value) and not isinstance(value, type):
            return evidence_plain(dataclasses.asdict(value))
        if type(value) is dict:
            return {
                str(key): evidence_plain(item)
                for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
            }
        if type(value) in (tuple, list):
            return [evidence_plain(item) for item in value]
        if type(value) in (set, frozenset):
            plain_items = [evidence_plain(item) for item in value]
            return sorted(
                plain_items,
                key=lambda item: json.dumps(
                    item, ensure_ascii=True, separators=(",", ":"), sort_keys=True
                ),
            )
        if type(value) is bytes:
            return {"bytes_hex": value.hex()}
        if value is None or type(value) in (bool, int, float, str):
            return value
        raise TypeError("unsupported_execution_evidence_type:" + type(value).__name__)

    def stable_value_ref(value: object) -> str:
        """Bind a receipt to the complete deterministic typed carrier representation."""
        type_name = type(value).__module__ + '.' + type(value).__qualname__
        body = (type_name + '\x00' + repr(value)).encode('utf-8')
        return "g2f_typed_repr_sha256:" + hashlib.sha256(body).hexdigest()

    def record_validation(
        row: int,
        validator: object,
        result: object,
        input_bindings: tuple[tuple[int, object], ...],
    ) -> object:
        """Retain the exact callable, result, and inputs from a live validation call."""
        validation_events.append(
            {
                "row": row,
                "validator": validator,
                "result": result,
                "input_bindings": input_bindings,
                "runtime_type": type(result),
                "stable_ref": stable_value_ref(result),
            }
        )
        return result

    def emit_receipt(
        row: int,
        ordinal: int,
        lane: str,
        producer: object,
        produced_value: object,
        *,
        input_bindings: tuple[tuple[int, str, object, object], ...],
    ) -> None:
        """Capture live producer and carrier evidence before report projection."""
        row_receipts.append(
            {
                "row": row,
                "ordinal": ordinal,
                "lane": lane,
                "producer": producer,
                "produced_value": produced_value,
                "runtime_type": type(produced_value),
                "stable_ref": stable_value_ref(produced_value),
                "stable_ref_kind": "DETERMINISTIC_TYPED_REPR_SHA256",
                "input_bindings": input_bindings,
            }
        )

    def emit_auxiliary(
        label: str,
        producer: object,
        inputs: tuple[object, ...],
        result: object,
        purpose: str,
    ) -> None:
        """Capture a non-row public call using its live inputs and result."""
        auxiliary_receipts.append(
            {
                "label": label,
                "producer": producer,
                "inputs": inputs,
                "input_ref": stable_value_ref(inputs),
                "result": result,
                "runtime_type": type(result),
                "stable_ref": stable_value_ref(result),
                "purpose": purpose,
            }
        )

    def emit_component(
        row: int,
        ordinal: int,
        lane: str,
        producer: object,
        inputs: tuple[object, ...],
        result: object,
        purpose: str,
    ) -> None:
        """Capture one live component call nested beneath a logical row."""
        component_receipts.append(
            {
                "row": row,
                "ordinal": ordinal,
                "lane": lane,
                "producer": producer,
                "inputs": inputs,
                "input_ref": stable_value_ref(inputs),
                "result": result,
                "runtime_type": type(result),
                "stable_ref": stable_value_ref(result),
                "purpose": purpose,
            }
        )
    rows: dict[int, dict[str, object]] = {index: {} for index in range(1, 182)}
    lanes: dict[str, dict[str, object]] = {label: {'label': label, 'root_id': root_id, 'domain_id': domain_id} for label, root_id, domain_id in ROOT_ROWS}
    for ordinal, (label, root_id, domain_id) in enumerate(ROOT_ROWS, start=1):
        scope_ref = f'scope:g2f:{label}:full_fractal:v01'
        lanes[label]['scope_ref'] = scope_ref
        lanes[label]['scope_sha'] = hashlib.sha256(scope_ref.encode('utf-8')).hexdigest()
        rows[1][label] = semantic.build_semantic_address_v01(namespace='g2f_v01', domain=domain_id, subject_class='bounded_information', intent_class='informational_summary', meaning_schema_id='drs_meaning_record', meaning_schema_version='v0.1')
        assert_equal(record_validation(1, semantic.validate_semantic_address_v01, semantic.validate_semantic_address_v01(rows[1][label]), ((1, rows[1][label]),)), (True, ()), f'row001_{label}')
        emit_receipt(1, ordinal, label, semantic.build_semantic_address_v01, rows[1][label], input_bindings=())
    for ordinal, (label, root_id, _domain_id) in enumerate(ROOT_ROWS, start=1):
        rows[2][label] = semantic.build_drs_time_envelope_v01(pt_created_at=EVALUATION_TIME, kt_as_of=EVALUATION_TIME, et_observed_at=EVALUATION_TIME, ct_context_anchor=EVALUATION_TIME, ttl_seconds=3600, valid_from=EVALUATION_TIME, valid_to=VALID_TO_TIME, source_observed_at=EVALUATION_TIME, source_reported_at=EVALUATION_TIME, system_ingested_at=EVALUATION_TIME, system_verified_at=EVALUATION_TIME, freshness_policy_id='freshness:g2f:v01')
        assert_equal(record_validation(2, semantic.validate_drs_time_envelope_v01, semantic.validate_drs_time_envelope_v01(rows[2][label]), ((2, rows[2][label]),)), (True, ()), f'row002_{label}')
        emit_receipt(2, ordinal, label, semantic.build_drs_time_envelope_v01, rows[2][label], input_bindings=())
    for ordinal, (label, root_id, _domain_id) in enumerate(ROOT_ROWS, start=1):
        prior_hash = hashlib.sha256(canonical_json_bytes_v01((label, 'prior_source_root'))).hexdigest()
        rows[3][label] = semantic.build_drs_authority_envelope_v01(authority_class='ROOT_ACCEPTED_WORK', owning_local_root_id=root_id, source_root_decision_input_id=f'root-input:g2f:{label}:source:v01', source_root_decision_id=f'root-decision:g2f:{label}:source:v01', source_root_decision_hash=prior_hash, authority_scope_fingerprint=lanes[label]['scope_sha'], root_acceptance_state='ACCEPTED_WORK', recording_component='g2f_v05_public_constructibility_witness')
        assert_equal(record_validation(3, semantic.validate_drs_authority_envelope_v01, semantic.validate_drs_authority_envelope_v01(rows[3][label]), ((3, rows[3][label]),)), (True, ()), f'row003_{label}')
        emit_receipt(3, ordinal, label, semantic.build_drs_authority_envelope_v01, rows[3][label], input_bindings=())
    for ordinal, (label, root_id, _domain_id) in enumerate(ROOT_ROWS, start=1):
        rows[4][label] = semantic.build_meaning_record_v01(semantic_address=rows[1][label], predecessor_record_id=None, supersession_reason=None, safe_summary='Bounded deterministic information for Root review.', semantic_tags=('bounded', 'g2f', 'informational'), resonance_reason='Exact deterministic semantic-address match.', memory_pointers=(), artifact_pointers=(), source_reference_ids=(f'source:g2f:{label}:memory:v01',), lineage_edges=(), time_envelope=rows[2][label], authority_envelope=rows[3][label], persistent_lifecycle_state='ACTIVE', risk_hints=(), conflict_hints=(), reuse_policy_class='ANSWER_SHORTCUT', policy_version=f'policy:g2f:{label}:v01', schema_versions=('v0.1',), content_fingerprint=hashlib.sha256(canonical_json_bytes_v01((label, 'meaning_record'))).hexdigest(), recording_component='g2f_v05_public_constructibility_witness')
        assert_equal(record_validation(4, semantic.validate_meaning_record_v01, semantic.validate_meaning_record_v01(rows[4][label]), ((4, rows[4][label]),)), (True, ()), f'row004_{label}')
        emit_receipt(4, ordinal, label, semantic.build_meaning_record_v01, rows[4][label], input_bindings=())
    for ordinal, (label, root_id, domain_id) in enumerate(ROOT_ROWS, start=1):
        rows[5][label] = resolution.build_drs_temporal_query_v01(query_mode='DIRECT_REUSE_CANDIDATE', semantic_address_id=rows[1][label].semantic_address_id, scope_fingerprint=lanes[label]['scope_sha'], as_of=EVALUATION_TIME, evaluation_time=EVALUATION_TIME, evaluation_time_source='INJECTED_CURRENT_DECISION_TIME', time_range_start=EVALUATION_TIME, time_range_end=VALID_TO_TIME, required_time_axes=('PT', 'KT', 'ET', 'CT', 'TTL', 'VALIDITY'), freshness_policy_id='freshness:g2f:v01', max_age_seconds=3600, domain=domain_id, risk_class='LOW', reuse_intent='INFORMATIONAL_SHORTCUT_CONSIDERATION', requested_reuse_classes=('ANSWER_SHORTCUT',), required_evidence_classes=G2B_EVIDENCE_CLASSES, forbidden_changes=('POLICY_CHANGED',), policy_version=f'policy:g2f:{label}:v01', schema_versions=('v0.1',), owning_local_root_id=root_id)
        lanes[label]['transaction_id'] = rows[5][label].query_id
        assert_equal(record_validation(5, resolution.validate_drs_temporal_query_v01, resolution.validate_drs_temporal_query_v01(rows[5][label]), ((5, rows[5][label]),)), (True, ()), f'row005_{label}')
        emit_receipt(5, ordinal, label, resolution.build_drs_temporal_query_v01, rows[5][label], input_bindings=())
    for ordinal, (label, root_id, _domain_id) in enumerate(ROOT_ROWS, start=1):
        rows[6][label] = resolution.evaluate_drs_candidate_v01(semantic_address=rows[1][label], query=rows[5][label], meaning_record=rows[4][label], action_history_binding=None)
        assert_equal(record_validation(6, resolution.validate_query_evaluation_state_v01, resolution.validate_query_evaluation_state_v01(rows[6][label]), ((6, rows[6][label]),)), (True, ()), f'row006_{label}')
        emit_receipt(6, ordinal, label, resolution.evaluate_drs_candidate_v01, rows[6][label], input_bindings=())
    for ordinal, (label, root_id, domain_id) in enumerate(ROOT_ROWS, start=1):
        legacy_source = {'record_id': f'legacy:g2f:{label}:v01', 'layer': 'work', 'type': 'generic', 'domain': domain_id, 'content': {'summary': 'Bounded deterministic G2-F memory context.'}, 'time_envelope': {'pt_created_at': EVALUATION_UTC, 'kt_asof': EVALUATION_UTC, 'et_observed_at': EVALUATION_UTC, 'ct_session_anchor': SHARED_REQUEST_ID, 'ttl_seconds': 3600, 'freshness_class': 'static', 'valid_from': EVALUATION_UTC, 'valid_to': VALID_TO_UTC}, 'provenance': {'request_id': SHARED_REQUEST_ID, 'created_by': 'root_orchestrator', 'trace_refs': []}, 'status': 'active'}
        rows[7][label] = compatibility.build_legacy_drs_projection_v01(source_family='LOCAL_DRS_DICT', source=legacy_source, target_semantic_address=rows[1][label], target_meaning_record=None)
        assert_equal(record_validation(7, compatibility.validate_legacy_drs_projection_v01, compatibility.validate_legacy_drs_projection_v01(rows[7][label]), ((7, rows[7][label]),)), (True, ()), f'row007_{label}')
        emit_receipt(7, ordinal, label, compatibility.build_legacy_drs_projection_v01, rows[7][label], input_bindings=())
    for ordinal, (label, root_id, _domain_id) in enumerate(ROOT_ROWS, start=1):
        rows[8][label] = resolution.build_memory_descent_budget_v01(max_depth=0, max_records_opened=1, max_pointers_opened=0, max_artifacts_opened=0, max_bytes_opened=0, max_lineage_edges=0, max_conflict_records=0)
        assert_equal(record_validation(8, resolution.validate_memory_descent_budget_v01, resolution.validate_memory_descent_budget_v01(rows[8][label]), ((8, rows[8][label]),)), (True, ()), f'row008_{label}')
        emit_receipt(8, ordinal, label, resolution.build_memory_descent_budget_v01, rows[8][label], input_bindings=())
    for ordinal, (label, root_id, _domain_id) in enumerate(ROOT_ROWS, start=1):
        rows[9][label] = resolution.build_retrieval_plan_v01(query_id=rows[5][label].query_id, semantic_address_id=rows[1][label].semantic_address_id, proposed_record_ids=(rows[4][label].meaning_record_id,), proposed_memory_pointer_ids=(), proposed_artifact_pointer_ids=(), requested_descent_class='SUMMARY_ONLY', proposed_budget_id=rows[8][label].memory_descent_budget_id, required_access_policy_ids=(), reason_codes=())
        assert_equal(record_validation(9, resolution.validate_retrieval_plan_v01, resolution.validate_retrieval_plan_v01(rows[9][label]), ((9, rows[9][label]),)), (True, ()), f'row009_{label}')
        emit_receipt(9, ordinal, label, resolution.build_retrieval_plan_v01, rows[9][label], input_bindings=())
    for ordinal, (label, root_id, _domain_id) in enumerate(ROOT_ROWS, start=1):
        rows[10][label] = resolution.build_resolution_candidate_v01(query_id=rows[5][label].query_id, semantic_address_id=rows[5][label].semantic_address_id, meaning_record_id=rows[4][label].meaning_record_id, query_evaluation_id=rows[6][label].query_evaluation_id, safe_summary=rows[4][label].safe_summary, evidence_ref_ids=rows[4][label].source_reference_ids, source_history_hash=rows[6][label].source_history_hash, action_history_binding_id=None, semantic_similarity_units=9000, freshness_units=rows[6][label].current_freshness_units, source_authority_prior_units=9000, lineage_proximity_units=7000, historical_utility_units=6000, gt_advisory_prior_units=1000, conflict_penalty_units=0, risk_penalty_units=0, retrieval_cost_units=100)
        assert_equal(record_validation(10, resolution.validate_resolution_candidate_v01, resolution.validate_resolution_candidate_v01(rows[10][label]), ((10, rows[10][label]),)), (True, ()), f'row010_{label}')
        emit_receipt(10, ordinal, label, resolution.build_resolution_candidate_v01, rows[10][label], input_bindings=())
    for ordinal, (label, root_id, _domain_id) in enumerate(ROOT_ROWS, start=1):
        rows[11][label] = resolution.rank_eligible_drs_candidates_v01(query=rows[5][label], query_evaluations=(rows[6][label],), candidates=(rows[10][label],))
        assert_equal(tuple((record_validation(11, resolution.validate_resolution_candidate_v01, resolution.validate_resolution_candidate_v01(item), ()) for item in rows[11][label])), ((True, ()),), f'row011_{label}')
        emit_receipt(11, ordinal, label, resolution.rank_eligible_drs_candidates_v01, rows[11][label], input_bindings=())
    for ordinal, (label, root_id, _domain_id) in enumerate(ROOT_ROWS, start=1):
        rows[12][label] = root_decision.build_root_decision_kernel_v01()
        assert_equal(record_validation(12, root_decision.validate_root_decision_kernel_v01, root_decision.validate_root_decision_kernel_v01(rows[12][label]), ((12, rows[12][label]),)), (), f'row012_{label}')
        emit_receipt(12, ordinal, label, root_decision.build_root_decision_kernel_v01, rows[12][label], input_bindings=())
    for ordinal, (label, root_id, _domain_id) in enumerate(ROOT_ROWS, start=1):
        actor_id = f'actor:g2f:{label}:shortcut:v01'
        lanes[label]['reuse_actor_id'] = actor_id
        rows[13][label] = semantic_work.build_semantic_work_request_v01(request_id=SHARED_REQUEST_ID, transaction_id=rows[5][label].query_id, target_root_id=root_id, runtime_topology_ref=rows[10][label].resolution_candidate_id, bounded_context_refs=(rows[10][label].resolution_candidate_id,), permitted_actor_ids=(actor_id,), permitted_contribution_modes=('DETERMINISTIC',), requested_subjects=(rows[1][label].semantic_address_id,), required_evidence_classes=('ROOT_SHORTCUT_BINDING',), forbidden_claims=('create_permission',))
        assert_equal(record_validation(13, semantic_work.validate_semantic_work_request_v01, semantic_work.validate_semantic_work_request_v01(rows[13][label]), ((13, rows[13][label]),)), (), f'row013_{label}')
        emit_receipt(13, ordinal, label, semantic_work.build_semantic_work_request_v01, rows[13][label], input_bindings=())
    for ordinal, (label, root_id, _domain_id) in enumerate(ROOT_ROWS, start=1):
        rows[14][label] = semantic_work.build_evidence_binding_v01(evidence_id=f'evidence-binding:g2f:{label}:shortcut:v01', evidence_ref=rows[10][label].resolution_candidate_id, evidence_class='ROOT_SHORTCUT_BINDING', source_component_id=lanes[label]['reuse_actor_id'], provenance_ref=rows[6][label].query_evaluation_id, evidence_state=semantic_work.EVIDENCE_STATE_PRESENT)
        emit_receipt(14, ordinal, label, semantic_work.build_evidence_binding_v01, rows[14][label], input_bindings=())
    for ordinal, (label, root_id, _domain_id) in enumerate(ROOT_ROWS, start=1):
        evaluation = rows[6][label]
        query = rows[5][label]
        candidate = rows[10][label]
        record = rows[4][label]
        address = rows[1][label]
        claim_preimage = {'profile_version': 'v0.1', 'semantic_address_id': address.semantic_address_id, 'meaning_record_id': record.meaning_record_id, 'query_id': query.query_id, 'query_evaluation_id': evaluation.query_evaluation_id, 'resolution_candidate_id': candidate.resolution_candidate_id, 'reuse_class': 'ANSWER_SHORTCUT', 'case_type': 'NON_ACTION_INFORMATIONAL', 'scope_fingerprint': query.scope_fingerprint, 'policy_version': query.policy_version, 'schema_versions': list(query.schema_versions), 'required_evidence_classes': list(query.required_evidence_classes), 'observed_evidence_fingerprint': evaluation.observed_evidence_fingerprint, 'forbidden_changes': list(query.forbidden_changes), 'checked_dependency_fingerprint': evaluation.checked_dependency_fingerprint, 'source_history_hash': evaluation.source_history_hash, 'action_history_binding_id': None, 'valid_from': EVALUATION_TIME, 'valid_to': VALID_TO_TIME, 'issued_at': EVALUATION_TIME, 'evaluated_at': evaluation.evaluated_at, 'root_shortcut_policy_ref': ROOT_POLICY_REF}
        rows[15][label] = semantic_work.build_normalized_claim_v01(claim_id=candidate.resolution_candidate_id, subject=address.semantic_address_id, predicate=ROOT_PREDICATE, object_or_value=claim_preimage, time_envelope_ref=f'time-envelope:g2f:{label}:shortcut:v01', provenance_refs=(evaluation.query_evaluation_id,), evidence_refs=(rows[14][label].evidence_id,), confidence_micros=1000000, source_role='deterministic_runtime', source_mode='DETERMINISTIC')
        emit_receipt(15, ordinal, label, semantic_work.build_normalized_claim_v01, rows[15][label], input_bindings=())
    for ordinal, (label, root_id, _domain_id) in enumerate(ROOT_ROWS, start=1):
        rows[16][label] = semantic_work.build_actor_contribution_v01(contribution_id=f'contribution:g2f:{label}:shortcut:v01', request_id=rows[13][label].request_id, actor_id=lanes[label]['reuse_actor_id'], actor_role='deterministic_runtime', contribution_mode='DETERMINISTIC', bsep_projection_ref=rows[7][label].projection_id, scope=rows[1][label].semantic_address_id, bounded_context_refs=rows[13][label].bounded_context_refs, claims=(rows[15][label],), evidence_bindings=(rows[14][label],), constraint_bindings=(), uncertainty_bindings=(), requested_validators=(), forbidden_claims_observed=())
        emit_receipt(16, ordinal, label, semantic_work.build_actor_contribution_v01, rows[16][label], input_bindings=())
    for ordinal, (label, root_id, _domain_id) in enumerate(ROOT_ROWS, start=1):
        rows[17][label] = trust_model.build_default_component_trust_profiles_v01()
        assert_equal(record_validation(17, trust_model.validate_component_trust_profiles_v01, trust_model.validate_component_trust_profiles_v01(profiles=rows[17][label]), ((17, rows[17][label]),)), (), f'row017_{label}')
        assert_equal(record_validation(17, semantic_work.validate_actor_contribution_v01, semantic_work.validate_actor_contribution_v01(request=rows[13][label], contribution=rows[16][label], trust_profiles=rows[17][label]), ((13, rows[13][label]), (16, rows[16][label]), (17, rows[17][label]))), (), f'row016_context_{label}')
        emit_receipt(17, ordinal, label, trust_model.build_default_component_trust_profiles_v01, rows[17][label], input_bindings=())
    for ordinal, (label, root_id, _domain_id) in enumerate(ROOT_ROWS, start=1):
        rows[18][label] = semantic_work.build_root_review_packet_from_contributions_v01(request=rows[13][label], contributions=(rows[16][label],), trust_profiles=rows[17][label])
        assert_equal(record_validation(18, semantic_work.validate_root_review_packet_v01, semantic_work.validate_root_review_packet_v01(request=rows[13][label], contributions=(rows[16][label],), packet=rows[18][label], trust_profiles=rows[17][label]), ((13, rows[13][label]), (16, rows[16][label]), (17, rows[17][label]), (18, rows[18][label]))), (), f'row018_{label}')
        emit_receipt(18, ordinal, label, semantic_work.build_root_review_packet_from_contributions_v01, rows[18][label], input_bindings=())
    for ordinal, (label, root_id, _domain_id) in enumerate(ROOT_ROWS, start=1):
        candidate_id = rows[10][label].resolution_candidate_id
        post_vv = {'bundle_id': f'post-vv:g2f:{label}:shortcut:v01', 'post_vv_passed': True, 'validated_candidate_ids': [candidate_id], 'rejected_candidate_ids': [], 'required_evidence_refs': [], 'provided_evidence_refs': [], 'hard_failure_reasons': []}
        gt = {'advisory_id': f'gt:g2f:{label}:shortcut:v01', 'candidate_ids': [candidate_id], 'selected_candidate_id': candidate_id, 'score_micros_by_candidate': {candidate_id: 500000}, 'source_artifact_type': 'GTAdvisoryReport', 'source_lifecycle_state': 'VALIDATED', 'actor_role': 'gt', 'attempted_effect': 'CREATE_ROOT_DECISION', 'target_artifact_type': 'RootDecision', 'advisory_only': True, 'creates_final_output': False, 'requests_effect': False}
        rows[19][label] = root_decision.build_root_decision_input_v01(transaction_id=rows[5][label].query_id, target_root_id=root_id, root_review_packet=rows[18][label], post_vv_bundle=post_vv, gt_advisory=gt, policy_state={'policy_id': f'policy:g2f:{label}:shortcut:v01', 'identity_passed': True, 'scope_passed': True, 'hard_policy_passed': True, 'allow_accept': True, 'conflict_policy': 'DEFER', 'no_candidate_policy': 'NO_UPDATE'}, permission_state={'permission_required': False, 'user_permission_present': False, 'permission_scope_valid': True, 'permission_ref': None}, temporal_state={'temporal_valid': True, 'expired': False, 'not_before_satisfied': True, 'time_envelope_ref': f'time-envelope:g2f:{label}:shortcut:v01'}, conflict_state={'material_unresolved_conflict': False, 'conflict_set_ids': []}, prior_root_state={'prior_decision_id': None, 'prior_decision': None, 'prior_selected_candidate_id': None})
        assert_equal(record_validation(19, root_decision.validate_root_decision_input_v01, root_decision.validate_root_decision_input_v01(kernel=rows[12][label], decision_input=rows[19][label]), ((12, rows[12][label]), (19, rows[19][label]))), (), f'row019_{label}')
        emit_receipt(19, ordinal, label, root_decision.build_root_decision_input_v01, rows[19][label], input_bindings=())
    for ordinal, (label, root_id, _domain_id) in enumerate(ROOT_ROWS, start=1):
        rows[20][label] = root_decision.decide_root_v01(kernel=rows[12][label], decision_input=rows[19][label])
        assert_equal(record_validation(20, root_decision.validate_root_decision_result_v01, root_decision.validate_root_decision_result_v01(kernel=rows[12][label], decision_input=rows[19][label], result=rows[20][label]), ((12, rows[12][label]), (19, rows[19][label]), (20, rows[20][label]))), (), f'row020_{label}')
        assert_equal((rows[20][label].decision, rows[20][label].reason_code), ('ACCEPT', 'validated_candidate_accepted'), f'row020_accept_{label}')
        emit_receipt(20, ordinal, label, root_decision.decide_root_v01, rows[20][label], input_bindings=())
    for ordinal, (label, root_id, _domain_id) in enumerate(ROOT_ROWS, start=1):
        root_hash = domain_separated_sha256_hex_v01(domain=ROOT_BINDING_DOMAIN, payload=canonical_json_bytes_v01(root_decision.root_decision_result_to_plain_dict_v01(rows[20][label])))
        lanes[label]['reuse_root_hash'] = root_hash
        rows[21][label] = reuse.build_root_shortcut_authorization_projection_v01(owning_local_root_id=root_id, root_kernel_id=rows[12][label].kernel_id, root_decision_input_id=rows[19][label].decision_input_id, root_decision_id=rows[20][label].decision_id, root_decision_hash=root_hash, selected_candidate_id=rows[10][label].resolution_candidate_id, semantic_address_id=rows[1][label].semantic_address_id, meaning_record_id=rows[4][label].meaning_record_id, query_id=rows[5][label].query_id, query_evaluation_id=rows[6][label].query_evaluation_id, allowed_reuse_class='ANSWER_SHORTCUT', scope_fingerprint=lanes[label]['scope_sha'], policy_version=rows[5][label].policy_version, schema_versions=rows[5][label].schema_versions, valid_from=EVALUATION_TIME, valid_to=VALID_TO_TIME, root_shortcut_policy_ref=ROOT_POLICY_REF)
        assert_equal(record_validation(21, reuse.validate_root_shortcut_authorization_projection_v01, reuse.validate_root_shortcut_authorization_projection_v01(rows[21][label]), ((21, rows[21][label]),)), (True, ()), f'row021_{label}')
        emit_receipt(21, ordinal, label, reuse.build_root_shortcut_authorization_projection_v01, rows[21][label], input_bindings=())
    for ordinal, (label, root_id, _domain_id) in enumerate(ROOT_ROWS, start=1):
        query, evaluation, candidate = (rows[5][label], rows[6][label], rows[10][label])
        rows[22][label] = reuse.build_reuse_certificate_v01(semantic_address_id=rows[1][label].semantic_address_id, meaning_record_id=rows[4][label].meaning_record_id, query_id=query.query_id, query_evaluation_id=evaluation.query_evaluation_id, resolution_candidate_id=candidate.resolution_candidate_id, root_shortcut_authorization_projection=rows[21][label], case_type='NON_ACTION_INFORMATIONAL', required_evidence_classes=query.required_evidence_classes, observed_evidence_fingerprint=evaluation.observed_evidence_fingerprint, forbidden_changes=query.forbidden_changes, checked_dependency_fingerprint=evaluation.checked_dependency_fingerprint, valid_from=EVALUATION_TIME, valid_to=VALID_TO_TIME, reuse_class='ANSWER_SHORTCUT', source_history_hash=evaluation.source_history_hash, action_history_binding_id=None, issued_at=EVALUATION_TIME, evaluated_at=evaluation.evaluated_at)
        assert_equal(record_validation(22, reuse.validate_reuse_certificate_v01, reuse.validate_reuse_certificate_v01(rows[22][label]), ((22, rows[22][label]),)), (True, ()), f'row022_{label}')
        emit_receipt(22, ordinal, label, reuse.build_reuse_certificate_v01, rows[22][label], input_bindings=())
    for ordinal, (label, root_id, _domain_id) in enumerate(ROOT_ROWS, start=1):
        rows[23][label] = resolution.build_drs_resolution_report_v01(semantic_address=rows[1][label], query=rows[5][label], source_projections=(rows[7][label],), source_records=(rows[4][label],), query_evaluations=(rows[6][label],), eligible_candidates=(rows[10][label],), ranked_candidate_ids=tuple((item.resolution_candidate_id for item in rows[11][label])), selected_candidate_id=rows[10][label].resolution_candidate_id, retrieval_plan=rows[9][label], memory_descent_result=None, root_shortcut_projection=rows[21][label], reuse_certificate=rows[22][label], context_only_record_ids=(), historical_only_record_ids=(), warning_only_record_ids=(), rerun_required_record_ids=(), blocked_record_ids=(), provider_calls=0, network_calls=0, gemini_calls=0, external_drs_calls=0, connector_calls=0, real_world_effects_count=0, final_status=abi.STATUS_PASS, reason_codes=())
        assert_equal(record_validation(23, resolution.validate_drs_resolution_report_v01, resolution.validate_drs_resolution_report_v01(rows[23][label]), ((23, rows[23][label]),)), (True, ()), f'row023_{label}')
        emit_receipt(23, ordinal, label, resolution.build_drs_resolution_report_v01, rows[23][label], input_bindings=())
    for ordinal, (label, root_id, _domain_id) in enumerate(ROOT_ROWS, start=1):
        rows[24][label] = record_validation(24, reuse.validate_existing_root_shortcut_decision_v01, reuse.validate_existing_root_shortcut_decision_v01(resolution_report=rows[23][label], root_kernel=rows[12][label], root_decision_input=rows[19][label], root_decision_result=rows[20][label], use_time=EVALUATION_TIME), ((12, rows[12][label]), (19, rows[19][label]), (20, rows[20][label]), (23, rows[23][label])))
        assert_equal(rows[24][label], (True, ()), f'row024_{label}')
        emit_receipt(24, ordinal, label, reuse.validate_existing_root_shortcut_decision_v01, rows[24][label], input_bindings=())
    rows[25]['client'] = semantic.build_semantic_address_v01(namespace='g2f_v01', domain='domain:g2f:client', subject_class='bounded_action', intent_class='action_execution', meaning_schema_id='drs_meaning_record', meaning_schema_version='v0.1')
    assert_equal(record_validation(25, semantic.validate_semantic_address_v01, semantic.validate_semantic_address_v01(rows[25]['client']), ((25, rows[25]['client']),)), (True, ()), 'row025_client')
    emit_receipt(25, 1, 'client', semantic.build_semantic_address_v01, rows[25]['client'], input_bindings=())
    rows[26]['client'] = resolution.evaluate_drs_candidate_v01(semantic_address=rows[25]['client'], query=rows[5]['client'], meaning_record=rows[4]['client'], action_history_binding=None)
    assert_equal(record_validation(26, resolution.validate_query_evaluation_state_v01, resolution.validate_query_evaluation_state_v01(rows[26]['client']), ((26, rows[26]['client']),)), (True, ()), 'row026_client')
    if rows[26]['client'].action_intent_passed or 'drs_action_intent_shortcut_forbidden' not in rows[26]['client'].reason_codes:
        raise RuntimeError('row026_action_like_reuse_not_blocked')
    emit_receipt(26, 1, 'client', resolution.evaluate_drs_candidate_v01, rows[26]['client'], input_bindings=())
    descent_actor_id = 'actor:g2f:client:memory-descent:v01'
    descent_evidence_id = 'evidence-binding:g2f:client:memory-descent-plan:v01'
    rows[27]['client'] = semantic_work.build_semantic_work_request_v01(request_id=SHARED_REQUEST_ID, transaction_id=rows[5]['client'].query_id, target_root_id='root:g2f:client', runtime_topology_ref=rows[9]['client'].retrieval_plan_id, bounded_context_refs=(rows[9]['client'].retrieval_plan_id,), permitted_actor_ids=(descent_actor_id,), permitted_contribution_modes=('DETERMINISTIC',), requested_subjects=(rows[1]['client'].semantic_address_id,), required_evidence_classes=('CONTROLLED_MEMORY_DESCENT_PLAN',), forbidden_claims=('create_permission', 'create_final_output', 'execute_effect'))
    assert_equal(record_validation(27, semantic_work.validate_semantic_work_request_v01, semantic_work.validate_semantic_work_request_v01(rows[27]['client']), ((27, rows[27]['client']),)), (), 'row027_client')
    emit_receipt(27, 1, 'client', semantic_work.build_semantic_work_request_v01, rows[27]['client'], input_bindings=())
    rows[28]['client'] = semantic_work.build_evidence_binding_v01(evidence_id=descent_evidence_id, evidence_ref=rows[9]['client'].retrieval_plan_id, evidence_class='CONTROLLED_MEMORY_DESCENT_PLAN', source_component_id=descent_actor_id, provenance_ref=rows[7]['client'].projection_id, evidence_state=semantic_work.EVIDENCE_STATE_PRESENT)
    emit_receipt(28, 1, 'client', semantic_work.build_evidence_binding_v01, rows[28]['client'], input_bindings=())
    descent_plan_plain = resolution.retrieval_plan_to_plain_data_v01(rows[9]['client'])
    rows[29]['client'] = semantic_work.build_normalized_claim_v01(claim_id=rows[9]['client'].retrieval_plan_id, subject=rows[9]['client'].semantic_address_id, predicate='approve_controlled_memory_descent_plan_v01', object_or_value=descent_plan_plain, time_envelope_ref=rows[2]['client'].time_envelope_id, provenance_refs=(rows[7]['client'].projection_id,), evidence_refs=(rows[28]['client'].evidence_id,), confidence_micros=1000000, source_role='deterministic_runtime', source_mode='DETERMINISTIC')
    assert_equal(rows[29]['client'].authority_class, 'NONE', 'row029_authority_class')
    emit_receipt(29, 1, 'client', semantic_work.build_normalized_claim_v01, rows[29]['client'], input_bindings=())
    rows[30]['client'] = semantic_work.build_actor_contribution_v01(contribution_id='contribution:g2f:client:memory-descent:v01', request_id=rows[27]['client'].request_id, actor_id=descent_actor_id, actor_role='deterministic_runtime', contribution_mode='DETERMINISTIC', bsep_projection_ref=rows[7]['client'].projection_id, scope=rows[9]['client'].semantic_address_id, bounded_context_refs=rows[27]['client'].bounded_context_refs, claims=(rows[29]['client'],), evidence_bindings=(rows[28]['client'],), constraint_bindings=(), uncertainty_bindings=(), requested_validators=(), forbidden_claims_observed=())
    assert_equal(record_validation(30, semantic_work.validate_actor_contribution_v01, semantic_work.validate_actor_contribution_v01(request=rows[27]['client'], contribution=rows[30]['client'], trust_profiles=rows[17]['client']), ((17, rows[17]['client']), (27, rows[27]['client']), (30, rows[30]['client']))), (), 'row030_client')
    emit_receipt(30, 1, 'client', semantic_work.build_actor_contribution_v01, rows[30]['client'], input_bindings=())
    rows[31]['client'] = semantic_work.build_root_review_packet_from_contributions_v01(request=rows[27]['client'], contributions=(rows[30]['client'],), trust_profiles=rows[17]['client'])
    assert_equal(record_validation(31, semantic_work.validate_root_review_packet_v01, semantic_work.validate_root_review_packet_v01(request=rows[27]['client'], contributions=(rows[30]['client'],), packet=rows[31]['client'], trust_profiles=rows[17]['client']), ((17, rows[17]['client']), (27, rows[27]['client']), (30, rows[30]['client']), (31, rows[31]['client']))), (), 'row031_client')
    emit_receipt(31, 1, 'client', semantic_work.build_root_review_packet_from_contributions_v01, rows[31]['client'], input_bindings=())
    descent_plan_id = rows[9]['client'].retrieval_plan_id
    rows[32]['client'] = root_decision.build_root_decision_input_v01(transaction_id=rows[5]['client'].query_id, target_root_id='root:g2f:client', root_review_packet=rows[31]['client'], post_vv_bundle={'bundle_id': 'post-vv:g2f:client:memory-descent:v01', 'hard_failure_reasons': [], 'post_vv_passed': True, 'provided_evidence_refs': [rows[28]['client'].evidence_id], 'rejected_candidate_ids': [], 'required_evidence_refs': [rows[28]['client'].evidence_id], 'validated_candidate_ids': [descent_plan_id]}, gt_advisory={'actor_role': 'gt', 'advisory_id': 'gt:g2f:client:memory-descent:v01', 'advisory_only': True, 'attempted_effect': 'CREATE_ROOT_DECISION', 'candidate_ids': [descent_plan_id], 'creates_final_output': False, 'requests_effect': False, 'score_micros_by_candidate': {descent_plan_id: 1000000}, 'selected_candidate_id': descent_plan_id, 'source_artifact_type': 'GTAdvisoryReport', 'source_lifecycle_state': 'VALIDATED', 'target_artifact_type': 'RootDecision'}, policy_state={'policy_id': 'policy:g2f:client:memory-descent:v01', 'identity_passed': True, 'scope_passed': True, 'hard_policy_passed': True, 'allow_accept': True, 'conflict_policy': 'DEFER', 'no_candidate_policy': 'NO_UPDATE'}, permission_state={'permission_required': False, 'user_permission_present': False, 'permission_scope_valid': True, 'permission_ref': None}, temporal_state={'temporal_valid': True, 'expired': False, 'not_before_satisfied': True, 'time_envelope_ref': rows[2]['client'].time_envelope_id}, conflict_state={'material_unresolved_conflict': False, 'conflict_set_ids': []}, prior_root_state={'prior_decision_id': None, 'prior_decision': None, 'prior_selected_candidate_id': None})
    assert_equal(record_validation(32, root_decision.validate_root_decision_input_v01, root_decision.validate_root_decision_input_v01(kernel=rows[12]['client'], decision_input=rows[32]['client']), ((12, rows[12]['client']), (32, rows[32]['client']))), (), 'row032_client')
    emit_receipt(32, 1, 'client', root_decision.build_root_decision_input_v01, rows[32]['client'], input_bindings=())
    rows[33]['client'] = root_decision.decide_root_v01(kernel=rows[12]['client'], decision_input=rows[32]['client'])
    assert_equal(record_validation(33, root_decision.validate_root_decision_result_v01, root_decision.validate_root_decision_result_v01(kernel=rows[12]['client'], decision_input=rows[32]['client'], result=rows[33]['client']), ((12, rows[12]['client']), (32, rows[32]['client']), (33, rows[33]['client']))), (), 'row033_client')
    assert_equal((rows[33]['client'].decision, rows[33]['client'].reason_code, rows[33]['client'].selected_candidate_id, rows[33]['client'].root_commit_created, rows[33]['client'].permission_created, rows[33]['client'].final_output_created, rows[33]['client'].effect_requested), ('ACCEPT', 'validated_candidate_accepted', descent_plan_id, True, False, False, False), 'row033_client_outcome')
    emit_receipt(33, 1, 'client', root_decision.decide_root_v01, rows[33]['client'], input_bindings=())
    descent_root_hash = domain_separated_sha256_hex_v01(domain='hedgehog:drs:memory_descent_root_result_binding:v01', payload=canonical_json_bytes_v01(root_decision.root_decision_result_to_plain_dict_v01(rows[33]['client'])))
    emit_auxiliary('client_memory_descent_root_hash', integrity_replay.domain_separated_sha256_hex_v01, (rows[33]['client'],), descent_root_hash, 'PUBLIC_DOMAIN_SEPARATED_ROOT_RESULT_HASH')
    rows[34]['client'] = resolution.build_memory_descent_request_v01(retrieval_plan_id=rows[9]['client'].retrieval_plan_id, query_id=rows[5]['client'].query_id, owning_local_root_id='root:g2f:client', root_kernel_id=rows[12]['client'].kernel_id, root_decision_input_id=rows[32]['client'].decision_input_id, root_decision_id=rows[33]['client'].decision_id, root_decision_hash=descent_root_hash, requested_descent_class=rows[9]['client'].requested_descent_class, approved_descent_class=rows[9]['client'].requested_descent_class, proposed_budget_id=rows[8]['client'].memory_descent_budget_id, approved_budget=rows[8]['client'], approved_record_ids=(rows[4]['client'].meaning_record_id,), approved_memory_pointer_ids=(), approved_artifact_pointer_ids=())
    assert_equal(record_validation(34, resolution.validate_memory_descent_request_v01, resolution.validate_memory_descent_request_v01(rows[34]['client']), ((34, rows[34]['client']),)), (True, ()), 'row034_client')
    emit_receipt(34, 1, 'client', resolution.build_memory_descent_request_v01, rows[34]['client'], input_bindings=())
    rows[35]['client'] = resolution.execute_local_memory_descent_v01(retrieval_plan=rows[9]['client'], proposed_budget=rows[8]['client'], descent_request=rows[34]['client'], root_kernel=rows[12]['client'], root_decision_input=rows[32]['client'], root_decision_result=rows[33]['client'], source_records=(rows[4]['client'],), artifact_payloads=())
    assert_equal(record_validation(35, resolution.validate_memory_descent_result_v01, resolution.validate_memory_descent_result_v01(rows[35]['client']), ((35, rows[35]['client']),)), (True, ()), 'row035_client')
    emit_receipt(35, 1, 'client', resolution.execute_local_memory_descent_v01, rows[35]['client'], input_bindings=())
    for ordinal, (label, root_id, domain_id) in enumerate(ROOT_ROWS, start=1):
        route_id = f'route:g2f:{label}:full_fractal:v01'
        proposal_id = f'semantic_proposal:g2f:{label}:full_fractal:v01'
        vectors = (f'vector:g2f:{label}:full_fractal:v01',)
        guards = ('guard:g2f:root_review:v01',)
        lanes[label]['route_id'] = route_id
        lanes[label]['proposal_id'] = proposal_id
        lanes[label]['vectors'] = vectors
        lanes[label]['guards'] = guards
        rows[36][label] = context_packets.build_business_request_context_packet(packet_id=f'context_packet:g2f:{label}:business:v01', created_by='execution_mode_router_g2c5_fixture', source_refs=(), domain=domain_id, request_id=SHARED_REQUEST_ID, business_subject='execution_mode_route', requested_action='bounded_root_review', explicit_blockers=(), user_visible_summary='Deterministic Root-local route evidence.', forbidden_authority_fields=(), forbidden_action_fields=())
        if record_validation(36, context_packets.validate_business_request_context_packet, context_packets.validate_business_request_context_packet(rows[36][label]), ((36, rows[36][label]),))['accepted'] is not True:
            raise RuntimeError(f'row036_{label}_invalid')
        emit_receipt(36, ordinal, label, context_packets.build_business_request_context_packet, rows[36][label], input_bindings=())
    for ordinal, (label, root_id, domain_id) in enumerate(ROOT_ROWS, start=1):
        business_ref = {'source': 'G2C_BUSINESS_REQUEST_CONTEXT_PACKET_V01', 'packet_id': rows[36][label]['packet_id'], 'request_id': SHARED_REQUEST_ID, 'domain_id': domain_id}
        lanes[label]['business_ref'] = business_ref
        rows[37][label] = context_packets.build_orchestrator_route_context_packet(packet_id=f'context_packet:g2f:{label}:route:v01', created_by='execution_mode_router_g2c5_fixture', source_refs=(business_ref,), domain=domain_id, allowed_routes=(lanes[label]['route_id'],), required_guards=lanes[label]['guards'], selected_vector_ids=lanes[label]['vectors'], route_validation_expectations={'root_review_required': True, 'selected_only_allowed_vectors': True}, orchestrator_is_root=False, creates_action_commit_packet=False, calls_connectors=False)
        if record_validation(37, context_packets.validate_orchestrator_route_context_packet, context_packets.validate_orchestrator_route_context_packet(rows[37][label]), ((37, rows[37][label]),))['accepted'] is not True:
            raise RuntimeError(f'row037_{label}_invalid')
        emit_receipt(37, ordinal, label, context_packets.build_orchestrator_route_context_packet, rows[37][label], input_bindings=())
    for ordinal, (label, root_id, _domain_id) in enumerate(ROOT_ROWS, start=1):
        proposal = {'proposal_id': lanes[label]['proposal_id'], 'suggested_route': lanes[label]['route_id'], 'selected_vector_ids': lanes[label]['vectors'], 'required_guards': lanes[label]['guards'], 'reason': 'Bounded full-fractal review is required.', 'confidence': 0.66, 'needs_review': True, 'uncertainty_notes': ('Source evidence remains advisory.',), 'root_review_required': True, 'truth_claimed': False, 'authority_claimed': False, 'action_permission_claimed': False, 'final_output_claimed': False, 'connector_command_claimed': False, 'drs_write_claimed': False, 'plan_graph_claimed': False, 'bypass_root_claimed': False, 'semantic_observations': ('A bounded high-depth route is required.',), 'route_reasoning': ('Use the Root-local full-fractal profile.',), 'rejected_route_reasoning': ('Shallower execution is insufficient.',), 'guard_reasoning': ('Root review remains mandatory.',), 'vector_reasoning': ('The bounded vector matches this Root lane.',), 'authority_boundary_reasoning': ('Root remains final authority.',)}
        lanes[label]['bsep_proposal'] = proposal
        rows[38][label] = structured_rationale.build_orchestrator_structured_rationale(observed_semantics=proposal['semantic_observations'], route_selection_reason=proposal['route_reasoning'], rejected_routes=proposal['rejected_route_reasoning'], required_guards_reasoning=proposal['guard_reasoning'], selected_vector_reasoning=proposal['vector_reasoning'], uncertainty_notes=proposal['uncertainty_notes'], authority_boundary=proposal['authority_boundary_reasoning'], root_review_required=True)
        rationale_validation = record_validation(38, structured_rationale.validate_orchestrator_structured_rationale, structured_rationale.validate_orchestrator_structured_rationale(rows[38][label]), ((38, rows[38][label]),))
        if rationale_validation['accepted'] is not True:
            raise RuntimeError(f'row038_{label}_invalid')
        lanes[label]['rationale_validation'] = rationale_validation
        emit_receipt(38, ordinal, label, structured_rationale.build_orchestrator_structured_rationale, rows[38][label], input_bindings=())
    for ordinal, (label, root_id, _domain_id) in enumerate(ROOT_ROWS, start=1):
        rows[39][label] = (context_packets.semantic_evidence_item('Bounded route evidence is present.', source='runtime_canonicalization', evidence_kind='observed_fact', confidence_label='medium', candidate_only=True, raw_quote=False), context_packets.semantic_evidence_item('Root review is pending.', source='runtime_canonicalization', evidence_kind='missing_evidence', confidence_label='medium', candidate_only=True, raw_quote=False), context_packets.semantic_evidence_item('Source evidence remains advisory.', source='runtime_canonicalization', evidence_kind='uncertainty', confidence_label='medium', candidate_only=True, raw_quote=False), context_packets.semantic_evidence_item('No action authority is present.', source='runtime_canonicalization', evidence_kind='risk_boundary', confidence_label='medium', candidate_only=True, raw_quote=False), context_packets.semantic_evidence_item('Unsupported action remains forbidden.', source='runtime_canonicalization', evidence_kind='rejected_route', confidence_label='medium', candidate_only=True, raw_quote=False), context_packets.semantic_evidence_item('Root review is required.', source='runtime_canonicalization', evidence_kind='approval_condition', confidence_label='medium', candidate_only=True, raw_quote=False), context_packets.semantic_evidence_item('Root remains final authority.', source='runtime_canonicalization', evidence_kind='authority_boundary', confidence_label='medium', candidate_only=True, raw_quote=False))
        fields = ('observed_semantic_facts', 'missing_evidence', 'uncertainty_notes', 'risk_boundary_notes', 'rejected_action_routes', 'required_approvals_or_conditions', 'authority_boundary_notes')
        for component_ordinal, (item, field) in enumerate(zip(rows[39][label], fields, strict=True), start=1):
            assert_equal(record_validation(39, context_packets.validate_semantic_evidence_items, context_packets.validate_semantic_evidence_items((item,), field=field), ()), (), f'row039_{label}_{field}')
            emit_component(39, component_ordinal, label, context_packets.semantic_evidence_item, (label, field), item, 'EXACT_FALSE_RAW_QUOTE_SEMANTIC_EVIDENCE_ITEM')
        emit_receipt(39, ordinal, label, context_packets.semantic_evidence_item, rows[39][label], input_bindings=())
    for ordinal, (label, root_id, domain_id) in enumerate(ROOT_ROWS, start=1):
        items = rows[39][label]
        rationale_ref = 'structured_rationale_v01:' + hashlib.sha256(canonical_json_bytes_v01(rows[38][label])).hexdigest()
        rows[40][label] = context_packets.build_bounded_semantic_evidence_packet(packet_id=f'context_packet:g2f:{label}:bsep:v01', created_by='runtime/bounded_context_packet_builder', source_refs=(lanes[label]['business_ref'],), domain=domain_id, source_role='orchestrator', target_role='architect', source_route_id=lanes[label]['route_id'], source_proposal_id=lanes[label]['proposal_id'], source_context_packet_id=rows[37][label]['packet_id'], source_structured_rationale_ref=rationale_ref, observed_semantic_facts=(items[0],), missing_evidence=(items[1],), uncertainty_notes=(items[2],), risk_boundary_notes=(items[3],), rejected_action_routes=(items[4],), required_approvals_or_conditions=(items[5],), authority_boundary_notes=(items[6],), selected_vector_ids=lanes[label]['vectors'], required_guards=lanes[label]['guards'])
        packet_validation = record_validation(40, context_packets.validate_bounded_semantic_evidence_packet, context_packets.validate_bounded_semantic_evidence_packet(rows[40][label], route_context_packet=rows[37][label], orchestrator_proposal=lanes[label]['bsep_proposal'], structured_rationale_validation=lanes[label]['rationale_validation']), ((37, rows[37][label]), (40, rows[40][label])))
        if packet_validation['accepted'] is not True:
            raise RuntimeError(f'row040_{label}_invalid:{packet_validation}')
        emit_receipt(40, ordinal, label, context_packets.build_bounded_semantic_evidence_packet, rows[40][label], input_bindings=())
    mode_states = ('UNAVAILABLE', 'NOT_REQUIRED', 'NOT_REQUIRED', 'UNAVAILABLE', 'UNAVAILABLE', 'UNAVAILABLE', 'UNAVAILABLE', 'AVAILABLE')
    mode_costs = (10, 20, 30, 40, 50, 60, 70, 80)
    for ordinal, (label, root_id, domain_id) in enumerate(ROOT_ROWS, start=1):
        built_profiles = []
        for component_ordinal, (mode, state, cost) in enumerate(zip(router.EXECUTABLE_EXECUTION_MODES_V01, mode_states, mode_costs, strict=True), start=1):
            profile = router.build_execution_mode_local_mode_profile_v01(request_id=SHARED_REQUEST_ID, transaction_id=rows[5][label].query_id, owning_root_id=root_id, domain_id=domain_id, mode=mode, policy_snapshot_id=f'policy:g2f:{label}:route:v01', capability_snapshot_id=f'capabilities:g2f:{label}:route:v01', cost_model_id='cost_model:g2f:deterministic:v01', policy_allowed=True, scope_allowed=True, risk_allowed=True, privacy_allowed=True, capability_state=state, capability_id=None if state == 'NOT_REQUIRED' else f'capability:g2f:{label}:{mode}:v01', cost_units=cost)
            report = record_validation(41, router.validate_execution_mode_local_mode_profile_v01, router.validate_execution_mode_local_mode_profile_v01(profile), ())
            (report.validation_status, report.reason_codes)
            built_profiles.append(profile)
            emit_component(41, component_ordinal, label, router.build_execution_mode_local_mode_profile_v01, (SHARED_REQUEST_ID, rows[5][label], root_id, domain_id, mode), profile, 'CANONICAL_MODE_PROFILE')
        rows[41][label] = tuple(built_profiles)
        emit_receipt(41, ordinal, label, router.build_execution_mode_local_mode_profile_v01, rows[41][label], input_bindings=())
    for ordinal, (label, root_id, domain_id) in enumerate(ROOT_ROWS, start=1):
        rows[42][label] = router.build_execution_mode_local_routing_snapshot_v01(request_id=SHARED_REQUEST_ID, transaction_id=rows[5][label].query_id, owning_root_id=root_id, domain_id=domain_id, request_class='BOUNDED_FRACTAL_REQUIRED', action_class='ACTION', action_packet_relation='NEW_ACTION_NO_PACKET', scope_class='BOUNDED', scope_ref=f'scope:g2f:{label}:full_fractal:v01', permitted_narrower_scope_refs=(), risk_class='HIGH', policy_snapshot_id=f'policy:g2f:{label}:route:v01', capability_snapshot_id=f'capabilities:g2f:{label}:route:v01', cost_model_id='cost_model:g2f:deterministic:v01', required_user_input_state='COMPLETE', hard_block_state='CLEAR', evaluation_time_epoch_seconds=EVALUATION_TIME, pt_created_at_utc=EVALUATION_UTC, et_observed_at_utc=EVALUATION_UTC, ct_session_anchor=f'ct:g2f:{label}:v01', ttl_seconds=3600, freshness_class='static', valid_from_utc=EVALUATION_UTC, valid_to_utc=VALID_TO_UTC, mode_profiles=rows[41][label])
        report = record_validation(42, router.validate_execution_mode_local_routing_snapshot_v01, router.validate_execution_mode_local_routing_snapshot_v01(rows[42][label]), ((42, rows[42][label]),))
        (report.validation_status, report.reason_codes)
        emit_receipt(42, ordinal, label, router.build_execution_mode_local_routing_snapshot_v01, rows[42][label], input_bindings=())
    for ordinal, (label, root_id, _domain_id) in enumerate(ROOT_ROWS, start=1):
        rows[43][label] = router.build_execution_mode_source_context_v01(business_request_context_packet=rows[36][label], bsep_packet=rows[40][label], bsep_route_context_packet=rows[37][label], bsep_orchestrator_proposal=lanes[label]['bsep_proposal'], bsep_structured_rationale=rows[38][label], sealed_replay_evidence=None, replay_source_manifest=None, replay_source_domain_projection=None, replay_source_safe_file_contents=(), replay_anchor_publication=None, replay_anchored_verification=None, replay_supplied_anchor_publication_id=None, replay_reconstructed_manifest=None, replay_reconstructed_domain_projection=None, replay_reconstructed_safe_file_contents=(), g2a_inspection=None, g2a_registry=None, g2a_packet_id=None, g2a_corridor=None, g2a_corridor_step=None, g2a_current_dependency_observations=(), g2a_logical_time_bridge=None, g2a_evaluation_time=EVALUATION_TIME, g2a_evaluation_time_source=rows[42][label].created_by, g2a_evaluation_context_id=rows[42][label].local_routing_snapshot_id, g2a_transition_registry_profile=None, g2b_resolution_report=rows[23][label], g2b_compatibility_projections=(rows[7][label],), g2b_use_time=EVALUATION_TIME, g2b_root_kernel=rows[12][label], g2b_root_decision_input=rows[19][label], g2b_root_decision_result=rows[20][label], g2b_writeback_evidence=None)
        report = record_validation(43, router.validate_execution_mode_source_context_v01, router.validate_execution_mode_source_context_v01(rows[43][label]), ((43, rows[43][label]),))
        (report.validation_status, report.reason_codes)
        emit_receipt(43, ordinal, label, router.build_execution_mode_source_context_v01, rows[43][label], input_bindings=())
    for ordinal, (label, root_id, domain_id) in enumerate(ROOT_ROWS, start=1):
        rows[44][label] = router.build_execution_mode_bsep_binding_v01(request_id=SHARED_REQUEST_ID, transaction_id=rows[5][label].query_id, owning_root_id=root_id, domain_id=domain_id, source_context=rows[43][label])
        report = record_validation(44, router.validate_execution_mode_bsep_binding_v01, router.validate_execution_mode_bsep_binding_v01(rows[44][label]), ((44, rows[44][label]),))
        (report.validation_status, report.reason_codes)
        emit_receipt(44, ordinal, label, router.build_execution_mode_bsep_binding_v01, rows[44][label], input_bindings=())
    for ordinal, (label, root_id, domain_id) in enumerate(ROOT_ROWS, start=1):
        rows[45][label] = router.build_execution_mode_replay_not_applicable_binding_v01(request_id=SHARED_REQUEST_ID, transaction_id=rows[5][label].query_id, owning_root_id=root_id, domain_id=domain_id)
        report = record_validation(45, router.validate_execution_mode_replay_binding_v01, router.validate_execution_mode_replay_binding_v01(rows[45][label]), ((45, rows[45][label]),))
        (report.validation_status, report.reason_codes)
        emit_receipt(45, ordinal, label, router.build_execution_mode_replay_not_applicable_binding_v01, rows[45][label], input_bindings=())
    for ordinal, (label, root_id, domain_id) in enumerate(ROOT_ROWS, start=1):
        rows[46][label] = router.build_execution_mode_g2a_no_packet_binding_v01(request_id=SHARED_REQUEST_ID, transaction_id=rows[5][label].query_id, owning_root_id=root_id, domain_id=domain_id, evaluation_time=EVALUATION_TIME, evaluation_time_source=rows[42][label].created_by, evaluation_context_id=rows[42][label].local_routing_snapshot_id)
        report = record_validation(46, router.validate_execution_mode_g2a_binding_v01, router.validate_execution_mode_g2a_binding_v01(rows[46][label]), ((46, rows[46][label]),))
        (report.validation_status, report.reason_codes)
        emit_receipt(46, ordinal, label, router.build_execution_mode_g2a_no_packet_binding_v01, rows[46][label], input_bindings=())
    for ordinal, (label, root_id, domain_id) in enumerate(ROOT_ROWS, start=1):
        rows[47][label] = router.build_execution_mode_g2b_binding_v01(request_id=SHARED_REQUEST_ID, transaction_id=rows[5][label].query_id, owning_root_id=root_id, domain_id=domain_id, source_context=rows[43][label])
        report = record_validation(47, router.validate_execution_mode_g2b_binding_v01, router.validate_execution_mode_g2b_binding_v01(rows[47][label]), ((47, rows[47][label]),))
        (report.validation_status, report.reason_codes)
        emit_receipt(47, ordinal, label, router.build_execution_mode_g2b_binding_v01, rows[47][label], input_bindings=())
    for ordinal, (label, root_id, _domain_id) in enumerate(ROOT_ROWS, start=1):
        rows[48][label] = router.build_execution_mode_router_input_v01(request_id=SHARED_REQUEST_ID, transaction_id=rows[5][label].query_id, owning_root_id=root_id, bsep_binding=rows[44][label], local_routing_snapshot=rows[42][label], replay_binding=rows[45][label], g2a_binding=rows[46][label], g2b_binding=rows[47][label])
        report = record_validation(48, router.validate_execution_mode_router_input_v01, router.validate_execution_mode_router_input_v01(rows[48][label]), ((48, rows[48][label]),))
        (report.validation_status, report.reason_codes)
        report = record_validation(48, router.validate_execution_mode_router_input_against_sources_v01, router.validate_execution_mode_router_input_against_sources_v01(router_input=rows[48][label], source_context=rows[43][label]), ((43, rows[43][label]), (48, rows[48][label])))
        (report.validation_status, report.reason_codes)
        emit_receipt(48, ordinal, label, router.build_execution_mode_router_input_v01, rows[48][label], input_bindings=())
    for ordinal, (label, root_id, _domain_id) in enumerate(ROOT_ROWS, start=1):
        rows[49][label] = router.evaluate_execution_mode_feasibility_v01(router_input=rows[48][label], source_context=rows[43][label])
        for component_ordinal, item in enumerate(rows[49][label], start=1):
            report = record_validation(49, router.validate_execution_mode_feasibility_row_v01, router.validate_execution_mode_feasibility_row_v01(item), ())
            (report.validation_status, report.reason_codes)
            emit_component(49, component_ordinal, label, router.evaluate_execution_mode_feasibility_v01, (rows[48][label], rows[43][label]), item, 'MODE_FEASIBILITY_ROW')
        emit_receipt(49, ordinal, label, router.evaluate_execution_mode_feasibility_v01, rows[49][label], input_bindings=())
    for ordinal, (label, root_id, _domain_id) in enumerate(ROOT_ROWS, start=1):
        rows[50][label] = router.select_execution_mode_v01(router_input=rows[48][label], source_context=rows[43][label], ordered_rows=rows[49][label])
        report = record_validation(50, router.validate_execution_mode_feasibility_row_v01, router.validate_execution_mode_feasibility_row_v01(rows[50][label]), ((50, rows[50][label]),))
        (report.validation_status, report.reason_codes, rows[50][label].mode, rows[50][label].feasibility_status)
        emit_receipt(50, ordinal, label, router.select_execution_mode_v01, rows[50][label], input_bindings=())
    for ordinal, (label, root_id, _domain_id) in enumerate(ROOT_ROWS, start=1):
        rows[51][label] = router.build_execution_mode_proposal_v01(router_input=rows[48][label], source_context=rows[43][label], ordered_rows=rows[49][label], selected_row=rows[50][label])
        report = record_validation(51, router.validate_execution_mode_proposal_v01, router.validate_execution_mode_proposal_v01(rows[51][label]), ((51, rows[51][label]),))
        (report.validation_status, report.reason_codes)
        report = record_validation(51, router.validate_execution_mode_proposal_against_sources_v01, router.validate_execution_mode_proposal_against_sources_v01(proposal=rows[51][label], router_input=rows[48][label], source_context=rows[43][label]), ((43, rows[43][label]), (48, rows[48][label]), (51, rows[51][label])))
        (report.validation_status, report.reason_codes)
        emit_receipt(51, ordinal, label, router.build_execution_mode_proposal_v01, rows[51][label], input_bindings=())
    for ordinal, (label, root_id, _domain_id) in enumerate(ROOT_ROWS, start=1):
        if label == 'client':
            rows[52][label] = router.route_execution_mode_v01(router_input=rows[48][label], source_context=rows[43][label])
        else:
            rows[52][label] = router.route_execution_mode_v01(router_input=rows[48][label], source_context=rows[43][label])
        routed_proposal, route_report = rows[52][label]
        (route_report.validation_status, route_report.reason_codes, routed_proposal)
        emit_receipt(52, ordinal, label, router.route_execution_mode_v01, rows[52][label], input_bindings=())
    for ordinal, (label, root_id, _domain_id) in enumerate(ROOT_ROWS, start=1):
        rows[53][label] = router.project_execution_mode_proposal_kernel_artifact_v01(proposal=rows[51][label], router_input=rows[48][label], source_context=rows[43][label])
        assert_equal(record_validation(53, abi.validate_kernel_artifact_v01, abi.validate_kernel_artifact_v01(rows[53][label]), ((53, rows[53][label]),)), (), f'row053_{label}')
        emit_receipt(53, ordinal, label, router.project_execution_mode_proposal_kernel_artifact_v01, rows[53][label], input_bindings=())
    rows[54]['shared'] = transition_registry.build_execution_mode_transition_registry_profile_v01()
    assert_equal(record_validation(54, transition_registry.validate_execution_mode_transition_registry_profile_v01, transition_registry.validate_execution_mode_transition_registry_profile_v01(rows[54]['shared']), ((54, rows[54]['shared']),)), (), 'row054_shared')
    emit_receipt(54, 1, 'shared', transition_registry.build_execution_mode_transition_registry_profile_v01, rows[54]['shared'], input_bindings=())
    for ordinal, (label, root_id, _domain_id) in enumerate(ROOT_ROWS, start=1):
        rows[55][label] = router.evaluate_execution_mode_proposal_to_root_transition_v01(registry=rows[54]['shared'], proposal=rows[51][label], router_input=rows[48][label], source_context=rows[43][label], proposal_artifact=rows[53][label])
        assert_equal(record_validation(55, transition_registry.validate_execution_mode_transition_decision_v01, transition_registry.validate_execution_mode_transition_decision_v01(registry=rows[54]['shared'], decision=rows[55][label]), ((54, rows[54]['shared']), (55, rows[55][label]))), (), f'row055_{label}')
        emit_receipt(55, ordinal, label, router.evaluate_execution_mode_proposal_to_root_transition_v01, rows[55][label], input_bindings=())
    for ordinal, (label, root_id, _domain_id) in enumerate(ROOT_ROWS, start=1):
        rows[56][label] = router.build_root_execution_mode_review_input_v01(proposal=rows[51][label], router_input=rows[48][label], source_context=rows[43][label], proposal_artifact=rows[53][label], proposal_transition_decision=rows[55][label], review_action='ACCEPT', accepted_scope_ref=rows[51][label].proposed_scope_ref, narrowing_basis_refs=())
        report = record_validation(56, router.validate_root_execution_mode_review_input_v01, router.validate_root_execution_mode_review_input_v01(rows[56][label]), ((56, rows[56][label]),))
        (report.validation_status, report.reason_codes)
        report = record_validation(56, router.validate_root_execution_mode_review_input_against_sources_v01, router.validate_root_execution_mode_review_input_against_sources_v01(review_input=rows[56][label], proposal=rows[51][label], router_input=rows[48][label], source_context=rows[43][label], proposal_artifact=rows[53][label], proposal_transition_decision=rows[55][label]), ((43, rows[43][label]), (48, rows[48][label]), (51, rows[51][label]), (53, rows[53][label]), (55, rows[55][label]), (56, rows[56][label])))
        (report.validation_status, report.reason_codes)
        emit_receipt(56, ordinal, label, router.build_root_execution_mode_review_input_v01, rows[56][label], input_bindings=())
    for ordinal, (label, root_id, _domain_id) in enumerate(ROOT_ROWS, start=1):
        if label == 'client':
            rows[57][label] = router.review_execution_mode_proposal_v01(review_input=rows[56][label], proposal=rows[51][label], router_input=rows[48][label], source_context=rows[43][label], proposal_artifact=rows[53][label], proposal_transition_decision=rows[55][label])
        else:
            rows[57][label] = router.review_execution_mode_proposal_v01(review_input=rows[56][label], proposal=rows[51][label], router_input=rows[48][label], source_context=rows[43][label], proposal_artifact=rows[53][label], proposal_transition_decision=rows[55][label])
        decision, kernel, decision_input, decision_result, review_report = rows[57][label]
        if any((item is None for item in (decision, kernel, decision_input, decision_result))):
            raise RuntimeError(f'row057_{label}_incomplete')
        (review_report.validation_status, review_report.reason_codes)
        report = record_validation(57, router.validate_root_execution_mode_decision_v01, router.validate_root_execution_mode_decision_v01(decision), ())
        (report.validation_status, report.reason_codes)
        report = record_validation(57, router.validate_root_execution_mode_decision_against_source_v01, router.validate_root_execution_mode_decision_against_source_v01(decision=decision, review_input=rows[56][label], proposal=rows[51][label], router_input=rows[48][label], source_context=rows[43][label], proposal_artifact=rows[53][label], proposal_transition_decision=rows[55][label], root_kernel=kernel, root_decision_input=decision_input, root_decision_result=decision_result), ((43, rows[43][label]), (48, rows[48][label]), (51, rows[51][label]), (53, rows[53][label]), (55, rows[55][label]), (56, rows[56][label])))
        (report.validation_status, report.reason_codes)
        emit_component(57, 1, label, router.review_execution_mode_proposal_v01, (rows[56][label], rows[51][label]), decision, 'ROOT_EXECUTION_MODE_DECISION')
        emit_component(57, 2, label, router.review_execution_mode_proposal_v01, (rows[56][label],), decision_result, 'EMBEDDED_ROOT_DECISION_RESULT')
        emit_receipt(57, ordinal, label, router.review_execution_mode_proposal_v01, rows[57][label], input_bindings=())
    for ordinal, (label, root_id, _domain_id) in enumerate(ROOT_ROWS, start=1):
        decision, kernel, decision_input, decision_result, _review_report = rows[57][label]
        rows[58][label] = router.project_root_execution_mode_decision_kernel_artifact_v01(decision=decision, review_input=rows[56][label], proposal=rows[51][label], router_input=rows[48][label], source_context=rows[43][label], proposal_artifact=rows[53][label], proposal_transition_decision=rows[55][label], root_kernel=kernel, root_decision_input=decision_input, root_decision_result=decision_result)
        assert_equal(record_validation(58, abi.validate_kernel_artifact_v01, abi.validate_kernel_artifact_v01(rows[58][label]), ((58, rows[58][label]),)), (), f'row058_{label}')
        emit_receipt(58, ordinal, label, router.project_root_execution_mode_decision_kernel_artifact_v01, rows[58][label], input_bindings=())
    for ordinal, (label, root_id, _domain_id) in enumerate(ROOT_ROWS, start=1):
        decision, kernel, decision_input, decision_result, _review_report = rows[57][label]
        rows[59][label] = router.evaluate_execution_mode_root_route_transition_v01(registry=rows[54]['shared'], proposal_transition_decision=rows[55][label], review_input=rows[56][label], decision=decision, proposal=rows[51][label], router_input=rows[48][label], source_context=rows[43][label], root_kernel=kernel, root_decision_input=decision_input, root_decision_result=decision_result, proposal_artifact=rows[53][label], decision_artifact=rows[58][label])
        assert_equal(record_validation(59, transition_registry.validate_execution_mode_transition_decision_v01, transition_registry.validate_execution_mode_transition_decision_v01(registry=rows[54]['shared'], decision=rows[59][label]), ((54, rows[54]['shared']), (59, rows[59][label]))), (), f'row059_{label}')
        emit_receipt(59, ordinal, label, router.evaluate_execution_mode_root_route_transition_v01, rows[59][label], input_bindings=())
    for ordinal, (label, root_id, _domain_id) in enumerate(ROOT_ROWS, start=1):
        decision, kernel, decision_input, decision_result, _review_report = rows[57][label]
        rows[60][label] = router.project_execution_mode_route_eligibility_kernel_artifact_v01(decision=decision, review_input=rows[56][label], proposal=rows[51][label], router_input=rows[48][label], source_context=rows[43][label], proposal_artifact=rows[53][label], proposal_transition_decision=rows[55][label], root_kernel=kernel, root_decision_input=decision_input, root_decision_result=decision_result, decision_artifact=rows[58][label], root_route_transition_decision=rows[59][label])
        if rows[60][label] is None:
            raise RuntimeError(f'row060_{label}_missing')
        assert_equal(record_validation(60, abi.validate_kernel_artifact_v01, abi.validate_kernel_artifact_v01(rows[60][label]), ((60, rows[60][label]),)), (), f'row060_{label}')
        emit_receipt(60, ordinal, label, router.project_execution_mode_route_eligibility_kernel_artifact_v01, rows[60][label], input_bindings=())
    for ordinal, (label, root_id, _domain_id) in enumerate(ROOT_ROWS, start=1):
        decision, kernel, decision_input, decision_result, _review_report = rows[57][label]
        rows[61][label] = record_validation(61, router.validate_execution_mode_route_eligibility_against_source_v01, router.validate_execution_mode_route_eligibility_against_source_v01(route_eligibility_artifact=rows[60][label], decision=decision, review_input=rows[56][label], proposal=rows[51][label], router_input=rows[48][label], source_context=rows[43][label], proposal_artifact=rows[53][label], proposal_transition_decision=rows[55][label], root_kernel=kernel, root_decision_input=decision_input, root_decision_result=decision_result, decision_artifact=rows[58][label], root_route_transition_decision=rows[59][label]), ((43, rows[43][label]), (48, rows[48][label]), (51, rows[51][label]), (53, rows[53][label]), (55, rows[55][label]), (56, rows[56][label]), (58, rows[58][label]), (59, rows[59][label]), (60, rows[60][label])))
        (rows[61][label].validation_status, rows[61][label].reason_codes)
        emit_receipt(61, ordinal, label, router.validate_execution_mode_route_eligibility_against_source_v01, rows[61][label], input_bindings=())
    cross_refs = []
    for ordinal, (label, root_id, _domain_id) in enumerate(ROOT_ROWS, start=1):
        target_root_id = ROOT_ROWS[1 if label == 'client' else 0][1]
        route_plain = abi.kernel_artifact_to_plain_dict_v01(rows[60][label])
        route_sha = hashlib.sha256(canonical_json_bytes_v01(route_plain)).hexdigest()
        ref = multiroot.build_cross_root_evidence_ref_v01(transaction_id=SHARED_REQUEST_ID, source_root_id=root_id, target_root_id=target_root_id, evidence_artifact_id=rows[60][label].artifact_id, evidence_artifact_hash=route_sha, evidence_class='VALIDATED_EVIDENCE', receipt_validated=False, trace_refs=(rows[58][label].artifact_id,))
        assert_equal(record_validation(62, multiroot.validate_cross_root_evidence_ref_v01, multiroot.validate_cross_root_evidence_ref_v01(ref), ()), (), f'row062_{label}')
        cross_refs.append(ref)
        emit_receipt(62, ordinal, label, multiroot.build_cross_root_evidence_ref_v01, ref, input_bindings=())
    rows[62]['root_set'] = tuple(cross_refs)
    root_wrappers = []
    for ordinal, (label, root_id, _domain_id) in enumerate(ROOT_ROWS, start=1):
        decision = rows[57][label][0]
        consumed_refs = tuple((ref.ref_id for ref in rows[62]['root_set'] if ref.target_root_id == root_id))
        wrapper = multiroot.build_root_decision_envelope_v01(transaction_id=SHARED_REQUEST_ID, root_id=root_id, root_decision_id=decision.decision_id, source_decision_ref=rows[58][label].artifact_id, outcome_class='ACCEPTED', reason_code='g2f_root_local_route_accepted', selected_subject_id=rows[60][label].artifact_id, evidence_refs=(rows[53][label].artifact_id, rows[58][label].artifact_id, rows[60][label].artifact_id), cross_root_input_refs=consumed_refs)
        assert_equal(record_validation(63, multiroot.validate_root_decision_envelope_v01, multiroot.validate_root_decision_envelope_v01(wrapper), ()), (), f'row063_{label}')
        root_wrappers.append(wrapper)
        emit_receipt(63, ordinal, label, multiroot.build_root_decision_envelope_v01, wrapper, input_bindings=())
    rows[63]['root_set'] = tuple(root_wrappers)
    rows[64]['parent'] = multiroot.build_transaction_outcome_envelope_v01(transaction_id=SHARED_REQUEST_ID, expected_root_ids=tuple((root_id for _label, root_id, _domain_id in ROOT_ROWS)), root_decisions=rows[63]['root_set'], cross_root_evidence_refs=rows[62]['root_set'])
    assert_equal(record_validation(64, multiroot.validate_transaction_outcome_envelope_v01, multiroot.validate_transaction_outcome_envelope_v01(rows[64]['parent']), ((64, rows[64]['parent']),)), (), 'row064_parent')
    emit_receipt(64, 1, 'parent', multiroot.build_transaction_outcome_envelope_v01, rows[64]['parent'], input_bindings=())
    rows[65]['parent'] = record_validation(65, multiroot.validate_multiroot_v01, multiroot.validate_multiroot_v01(rows[64]['parent']), ((64, rows[64]['parent']),))
    (rows[65]['parent'].final_status, rows[65]['parent'].errors, rows[64]['parent'].super_root_created, rows[64]['parent'].authority_transfer_count, rows[64]['parent'].permission_creation_count, rows[64]['parent'].real_world_effects_count)
    emit_receipt(65, 1, 'parent', multiroot.validate_multiroot_v01, rows[65]['parent'], input_bindings=())
    rows[66]['parent'] = multiroot.transaction_outcome_envelope_to_plain_dict_v01(rows[64]['parent'])
    assert_equal(rows[66]['parent']['transaction_id'], SHARED_REQUEST_ID, 'row066_parent')
    emit_receipt(66, 1, 'parent', multiroot.transaction_outcome_envelope_to_plain_dict_v01, rows[66]['parent'], input_bindings=())
    for ordinal, (label, root_id, _domain_id) in enumerate(ROOT_ROWS, start=1):
        rows[67][label] = fractal_runtime.build_fractal_runtime_policy_v02(required_downstream_capability_ids=rows[51][label].required_downstream_capability_ids, permitted_child_scope_refs=rows[42][label].permitted_narrower_scope_refs)
        report = record_validation(67, fractal_runtime.validate_fractal_runtime_policy_v02, fractal_runtime.validate_fractal_runtime_policy_v02(rows[67][label]), ((67, rows[67][label]),))
        (report.status, report.reason_codes)
        emit_receipt(67, ordinal, label, fractal_runtime.build_fractal_runtime_policy_v02, rows[67][label], input_bindings=())
    for ordinal, (label, root_id, _domain_id) in enumerate(ROOT_ROWS, start=1):
        decision, kernel, decision_input, decision_result, _review_report = rows[57][label]
        rows[68][label] = fractal_runtime.build_fractal_runtime_source_context_v02(transition_registry=rows[54]['shared'], g2c_source_context=rows[43][label], router_input=rows[48][label], proposal=rows[51][label], proposal_artifact=rows[53][label], proposal_transition_decision=rows[55][label], review_input=rows[56][label], decision=decision, root_kernel=kernel, root_decision_input=decision_input, root_decision_result=decision_result, decision_artifact=rows[58][label], root_route_transition_decision=rows[59][label], route_eligibility_artifact=rows[60][label], runtime_policy=rows[67][label])
        report = record_validation(68, fractal_runtime.validate_fractal_runtime_source_context_v02, fractal_runtime.validate_fractal_runtime_source_context_v02(rows[68][label]), ((68, rows[68][label]),))
        (report.status, report.reason_codes)
        emit_receipt(68, ordinal, label, fractal_runtime.build_fractal_runtime_source_context_v02, rows[68][label], input_bindings=())
    for ordinal, (label, root_id, _domain_id) in enumerate(ROOT_ROWS, start=1):
        if label == 'client':
            rows[69][label] = fractal_runtime.run_fractal_runtime_v02(rows[68][label])
        else:
            rows[69][label] = fractal_runtime.run_fractal_runtime_v02(rows[68][label])
        bundle, run_report = rows[69][label]
        if bundle is None:
            raise RuntimeError(f'row069_{label}_bundle_missing:{run_report}')
        (run_report.status, run_report.reason_codes)
        report = record_validation(69, fractal_runtime.validate_fractal_runtime_execution_bundle_v02, fractal_runtime.validate_fractal_runtime_execution_bundle_v02(bundle), ())
        (report.status, report.reason_codes)
        report = record_validation(69, fractal_runtime.validate_runtime_execution_topology_v02, fractal_runtime.validate_runtime_execution_topology_v02(bundle.topology), ())
        (report.status, report.reason_codes)
        for component_ordinal, result in enumerate(bundle.cell_results, start=1):
            report = record_validation(69, fractal_runtime.validate_fractal_cell_result_v02, fractal_runtime.validate_fractal_cell_result_v02(result), ())
            (report.status, report.reason_codes)
            emit_component(69, component_ordinal, label, fractal_runtime.run_fractal_runtime_v02, (rows[68][label],), result, 'FRACTAL_CELL_RESULT')
        emit_receipt(69, ordinal, label, fractal_runtime.run_fractal_runtime_v02, rows[69][label], input_bindings=())
    supplier_root_id = 'root:g2f:supplier'
    supplier_transaction_id = rows[5]['supplier'].query_id
    row070_scope = action_packet.PermissionScopeV02(allowed_subjects=('subject:procurement_requester',), forbidden_subjects=(action_packet.SUBJECT_SUPPLIER_B, action_packet.SUBJECT_SHIPMENT_SH_2042), allowed_actions=(action_packet.ACTION_MOCK_SUPPLIER_A_PAYMENT_INTENT, action_packet.ACTION_MOCK_SUPPLIER_A_PAYMENT_ORDER), forbidden_actions=(action_packet.ACTION_SUPPLIER_B_PAYMENT, action_packet.ACTION_SHIPMENT_RELEASE, action_packet.ACTION_REAL_PAYMENT, action_packet.ACTION_REAL_BANK_TRANSFER), allowed_adapters=(action_packet.ADAPTER_MOCK_BANK_SANDBOX, action_packet.ADAPTER_BANK_A_MOCK), forbidden_adapters=(action_packet.ADAPTER_REAL_BANK, action_packet.ADAPTER_REAL_SUPPLIER_API, action_packet.ADAPTER_REAL_WAREHOUSE_API), payment_slot_ref='payment_slot:bank_a_mock:inv_2042', creditor_ref=action_packet.SUBJECT_SUPPLIER_A, amount='1250.00', currency='EUR')
    row070_ttl = action_packet.PacketTTL(created_at='2026-07-08T00:00:00Z', expires_at='2026-07-08T01:00:00Z', ttl_seconds=3600, ttl_valid=True, expired=False)
    row070_idempotency = action_packet.IdempotencyKeyV02(key='idem:acp_v02:supplier_a_mock_payment:inv_2042', duplicate_packet_id=False, duplicate_idempotency_key=False, terminal_receipt_already_exists=False)
    row070_adapter = action_packet.AdapterBindingV02(adapter_id=action_packet.ADAPTER_MOCK_BANK_SANDBOX, adapter_kind='mock_bank', real_adapter=False, adapter_version=None)
    row070_evidence = action_packet.PacketEvidenceRefV02(evidence_id='evidence:root_review_supplier_a_ready', evidence_kind='root_review', source_ref='root_boundary:supplier_payment_review')
    emit_component(70, 1, 'supplier', action_packet.PermissionScopeV02, (), row070_scope, 'PUBLIC_TYPED_SCOPE')
    emit_component(70, 2, 'supplier', action_packet.PacketTTL, (), row070_ttl, 'PUBLIC_TYPED_TTL')
    emit_component(70, 3, 'supplier', action_packet.IdempotencyKeyV02, (), row070_idempotency, 'PUBLIC_TYPED_IDEMPOTENCY')
    emit_component(70, 4, 'supplier', action_packet.AdapterBindingV02, (), row070_adapter, 'PUBLIC_TYPED_ADAPTER')
    emit_component(70, 5, 'supplier', action_packet.PacketEvidenceRefV02, (), row070_evidence, 'PUBLIC_TYPED_EVIDENCE')
    rows[70]['supplier'] = action_packet.ActionCommitPacketV02(packet_id='acp_v02:supplier_a_mock_payment:inv_2042', source_root_decision_ref='root_review:supplier_a_mock_payment_ready', human_approval_ref='human_approval:supplier_a_scope_only', scope=row070_scope, ttl=row070_ttl, idempotency=row070_idempotency, adapter_binding=row070_adapter, packet_type='supplier_a_mock_payment_action_commit_packet_v02', created_by='root', root_created=True, evidence_refs=(row070_evidence,), drs_refs=('local_drs_v0_2_resolve_report',), avf_refs=('avf_v0_2_evaluation_report',), bsep_ref='bsep:supplier_payment_review', root_boundary_ref='root_boundary:supplier_a_mock_payment', receipt_evidence_only=True, real_world_effects_allowed=False, production_ready_claimed=False, public_auditor_ready_claimed=False)
    assert_equal(record_validation(70, action_packet.validate_action_commit_packet_v02, action_packet.validate_action_commit_packet_v02(rows[70]['supplier']), ((70, rows[70]['supplier']),)), (True, ()), 'row070_supplier')
    assert_equal(rows[70]['supplier'].scope.allowed_subjects, ('subject:procurement_requester',), 'row070_requester_subject')
    assert_equal(rows[70]['supplier'].scope.creditor_ref, action_packet.SUBJECT_SUPPLIER_A, 'row070_supplier_creditor')
    emit_receipt(70, 1, 'supplier', action_packet.ActionCommitPacketV02, rows[70]['supplier'], input_bindings=())
    dependency_id = 'dependency:g2f:supplier:water_filter_stock'
    dependency_evidence_ref = 'evidence:g2f:supplier:water_filter_stock'
    baseline_dependency_value = 12
    baseline_dependency_content_sha256 = hashlib.sha256(canonical_json_bytes_v01(baseline_dependency_value)).hexdigest()
    dependency_freshness_policy = 'freshness:g2f:supplier:water_filter:v01'
    dependency_provenance_refs = ('source:g2f:supplier:worldstate:v01',)
    rows[71]['supplier'] = action_packet.build_action_dependency_time_envelope_id_v01(dependency_id=dependency_id, evidence_ref=dependency_evidence_ref, content_sha256=baseline_dependency_content_sha256, freshness_policy_id=dependency_freshness_policy, source_provenance_refs=dependency_provenance_refs, valid_from_utc=PACKET_VALID_FROM_TIME, valid_to_utc=PACKET_VALID_TO_TIME)
    assert_equal(record_validation(71, action_packet.validate_action_dependency_time_envelope_binding_v01, action_packet.validate_action_dependency_time_envelope_binding_v01(rows[71]['supplier'], dependency_id=dependency_id, evidence_ref=dependency_evidence_ref, content_sha256=baseline_dependency_content_sha256, freshness_policy_id=dependency_freshness_policy, source_provenance_refs=dependency_provenance_refs, valid_from_utc=PACKET_VALID_FROM_TIME, valid_to_utc=PACKET_VALID_TO_TIME), ((71, rows[71]['supplier']),)), (True, ()), 'row071_supplier')
    emit_receipt(71, 1, 'supplier', action_packet.build_action_dependency_time_envelope_id_v01, rows[71]['supplier'], input_bindings=())
    rows[72]['supplier'] = action_packet.build_dependency_set_candidate_record_v01(dependency_id=dependency_id, dependency_class='SUPPLIER_AVAILABILITY', evidence_ref=dependency_evidence_ref, content_sha256=baseline_dependency_content_sha256, requirement_class='MANDATORY', time_envelope_id=rows[71]['supplier'], freshness_policy_id=dependency_freshness_policy, source_provenance_refs=dependency_provenance_refs, expected_accepting_local_root_id=supplier_root_id)
    assert_equal(record_validation(72, action_packet.validate_dependency_set_candidate_record_v01, action_packet.validate_dependency_set_candidate_record_v01(rows[72]['supplier']), ((72, rows[72]['supplier']),)), (True, ()), 'row072_supplier')
    emit_receipt(72, 1, 'supplier', action_packet.build_dependency_set_candidate_record_v01, rows[72]['supplier'], input_bindings=())
    rows[73]['supplier'] = action_packet.build_dependency_set_candidate_v01(dependency_records=(rows[72]['supplier'],))
    assert_equal(record_validation(73, action_packet.validate_dependency_set_candidate_v01, action_packet.validate_dependency_set_candidate_v01(rows[73]['supplier']), ((73, rows[73]['supplier']),)), (True, ()), 'row073_supplier')
    emit_receipt(73, 1, 'supplier', action_packet.build_dependency_set_candidate_v01, rows[73]['supplier'], input_bindings=())
    rows[74]['supplier'] = action_packet.build_action_authority_policy_profile_v01(policy_version='policy:g2f:supplier:action:v01', owning_local_root_id=supplier_root_id, authority_rule_refs=('authority_rule:g2f:supplier:root_packet_only',), kill_switch_condition_refs=('kill_switch:g2f:supplier:dependency_change',), retry_policy='NON_CONSUMING_RETRY', supersession_policy='ROOT_DECISION_ONLY', logical_effect_namespace='supplier.payment.v01', allowed_logical_effect_classes=('PAYMENT',), allowed_business_object_namespaces=('supplier.payment_slot.v01',), allowed_corridor_classes=('supplier_a_mock_payment_corridor',))
    assert_equal(record_validation(74, action_packet.validate_action_authority_policy_profile_v01, action_packet.validate_action_authority_policy_profile_v01(rows[74]['supplier']), ((74, rows[74]['supplier']),)), (True, ()), 'row074_supplier')
    emit_receipt(74, 1, 'supplier', action_packet.build_action_authority_policy_profile_v01, rows[74]['supplier'], input_bindings=())
    rows[75]['supplier'] = action_packet.build_supplier_action_commit_packet_canonical_projection_v01(rows[70]['supplier'], transaction_id=supplier_transaction_id, owning_local_root_id=supplier_root_id, canonical_permission_ref='permission:g2f:supplier:bounded_payment:v01', selected_legacy_action=action_packet.ACTION_MOCK_SUPPLIER_A_PAYMENT_ORDER, logical_effect_namespace='supplier.payment.v01', business_object_namespace='supplier.payment_slot.v01', corridor_class='supplier_a_mock_payment_corridor', adapter_version=action_packet.PRE_G2A_ADAPTER_VERSION_V01, temporal_policy_version='packet_ttl_v01', authority_policy=rows[74]['supplier'], dependency_candidate=rows[73]['supplier'], evaluation_time=PACKET_EVALUATION_TIME, evaluation_time_source='g2f_deterministic_logical_time', evaluation_context_id='evaluation_context:g2f:supplier:packet:v01', predecessor_packet_id=None, supersession_reason_class=None)
    assert_equal(record_validation(75, action_packet.validate_supplier_action_commit_packet_canonical_projection_v01, action_packet.validate_supplier_action_commit_packet_canonical_projection_v01(rows[75]['supplier']), ((75, rows[75]['supplier']),)), (True, ()), 'row075_supplier')
    packet_candidate_id = rows[75]['supplier'].authorization_candidate.root_packet_authorization_candidate_id
    emit_receipt(75, 1, 'supplier', action_packet.build_supplier_action_commit_packet_canonical_projection_v01, rows[75]['supplier'], input_bindings=())
    packet_actor_id = 'actor:g2f:supplier:packet-authorization:v01'
    packet_subject = 'action_commit_packet:g2f:supplier'
    rows[76]['supplier'] = semantic_work.build_semantic_work_request_v01(request_id=SHARED_REQUEST_ID, transaction_id=supplier_transaction_id, target_root_id=supplier_root_id, runtime_topology_ref=packet_candidate_id, bounded_context_refs=(packet_candidate_id,), permitted_actor_ids=(packet_actor_id,), permitted_contribution_modes=('DETERMINISTIC',), requested_subjects=(packet_subject,), required_evidence_classes=('CANDIDATE_EVIDENCE',), forbidden_claims=('aggregate_authority', 'external_effect'))
    assert_equal(record_validation(76, semantic_work.validate_semantic_work_request_v01, semantic_work.validate_semantic_work_request_v01(rows[76]['supplier']), ((76, rows[76]['supplier']),)), (), 'row076_supplier')
    emit_receipt(76, 1, 'supplier', semantic_work.build_semantic_work_request_v01, rows[76]['supplier'], input_bindings=())
    rows[77]['supplier'] = semantic_work.build_evidence_binding_v01(evidence_id='evidence-binding:g2f:supplier:packet-authorization:v01', evidence_ref=packet_candidate_id, evidence_class='CANDIDATE_EVIDENCE', source_component_id=packet_actor_id, provenance_ref=packet_candidate_id, evidence_state=semantic_work.EVIDENCE_STATE_PRESENT)
    emit_receipt(77, 1, 'supplier', semantic_work.build_evidence_binding_v01, rows[77]['supplier'], input_bindings=())
    rows[78]['supplier'] = semantic_work.build_normalized_claim_v01(claim_id=packet_candidate_id, subject=packet_subject, predicate='root_packet_authorization_candidate', object_or_value={'candidate_id': packet_candidate_id, 'candidate_kind': 'PACKET_AUTHORIZATION'}, time_envelope_ref=rows[75]['supplier'].temporal_authority_fingerprint, provenance_refs=(packet_candidate_id,), evidence_refs=(rows[77]['supplier'].evidence_id,), confidence_micros=1000000, source_role='deterministic_runtime', source_mode='DETERMINISTIC')
    emit_receipt(78, 1, 'supplier', semantic_work.build_normalized_claim_v01, rows[78]['supplier'], input_bindings=())
    rows[79]['supplier'] = semantic_work.build_actor_contribution_v01(contribution_id='contribution:g2f:supplier:packet-authorization:v01', request_id=rows[76]['supplier'].request_id, actor_id=packet_actor_id, actor_role='deterministic_runtime', contribution_mode='DETERMINISTIC', bsep_projection_ref=rows[7]['supplier'].projection_id, scope=packet_subject, bounded_context_refs=rows[76]['supplier'].bounded_context_refs, claims=(rows[78]['supplier'],), evidence_bindings=(rows[77]['supplier'],), constraint_bindings=(), uncertainty_bindings=(), requested_validators=('validator:g2f:supplier:packet-authorization:v01',), forbidden_claims_observed=())
    assert_equal(record_validation(79, semantic_work.validate_actor_contribution_v01, semantic_work.validate_actor_contribution_v01(request=rows[76]['supplier'], contribution=rows[79]['supplier'], trust_profiles=rows[17]['supplier']), ((17, rows[17]['supplier']), (76, rows[76]['supplier']), (79, rows[79]['supplier']))), (), 'row079_supplier')
    emit_receipt(79, 1, 'supplier', semantic_work.build_actor_contribution_v01, rows[79]['supplier'], input_bindings=())
    rows[80]['supplier'] = semantic_work.build_root_review_packet_from_contributions_v01(request=rows[76]['supplier'], contributions=(rows[79]['supplier'],), trust_profiles=rows[17]['supplier'])
    assert_equal(record_validation(80, semantic_work.validate_root_review_packet_v01, semantic_work.validate_root_review_packet_v01(request=rows[76]['supplier'], contributions=(rows[79]['supplier'],), packet=rows[80]['supplier'], trust_profiles=rows[17]['supplier']), ((17, rows[17]['supplier']), (76, rows[76]['supplier']), (79, rows[79]['supplier']), (80, rows[80]['supplier']))), (), 'row080_supplier')
    emit_receipt(80, 1, 'supplier', semantic_work.build_root_review_packet_from_contributions_v01, rows[80]['supplier'], input_bindings=())
    rows[81]['supplier'] = root_decision.build_root_decision_input_v01(transaction_id=supplier_transaction_id, target_root_id=supplier_root_id, root_review_packet=rows[80]['supplier'], post_vv_bundle={'bundle_id': 'post-vv:g2f:supplier:packet-authorization:v01', 'hard_failure_reasons': [], 'post_vv_passed': True, 'provided_evidence_refs': [dependency_evidence_ref], 'rejected_candidate_ids': [], 'required_evidence_refs': [dependency_evidence_ref], 'validated_candidate_ids': [packet_candidate_id]}, gt_advisory={'actor_role': 'gt', 'advisory_id': 'gt:g2f:supplier:packet-authorization:v01', 'advisory_only': True, 'attempted_effect': 'CREATE_ROOT_DECISION', 'candidate_ids': [packet_candidate_id], 'creates_final_output': False, 'requests_effect': False, 'score_micros_by_candidate': {packet_candidate_id: 1000000}, 'selected_candidate_id': packet_candidate_id, 'source_artifact_type': 'GTAdvisoryReport', 'source_lifecycle_state': 'VALIDATED', 'target_artifact_type': 'RootDecision'}, policy_state={'policy_id': rows[75]['supplier'].authority_policy_fingerprint, 'identity_passed': True, 'scope_passed': True, 'hard_policy_passed': True, 'allow_accept': True, 'conflict_policy': 'DEFER', 'no_candidate_policy': 'NO_UPDATE'}, permission_state={'permission_required': True, 'user_permission_present': True, 'permission_scope_valid': True, 'permission_ref': rows[75]['supplier'].canonical_permission_ref}, temporal_state={'temporal_valid': True, 'expired': False, 'not_before_satisfied': True, 'time_envelope_ref': rows[75]['supplier'].temporal_authority_fingerprint}, conflict_state={'material_unresolved_conflict': False, 'conflict_set_ids': []}, prior_root_state={'prior_decision_id': None, 'prior_decision': None, 'prior_selected_candidate_id': None})
    assert_equal(record_validation(81, root_decision.validate_root_decision_input_v01, root_decision.validate_root_decision_input_v01(kernel=rows[12]['supplier'], decision_input=rows[81]['supplier']), ((12, rows[12]['supplier']), (81, rows[81]['supplier']))), (), 'row081_supplier')
    emit_receipt(81, 1, 'supplier', root_decision.build_root_decision_input_v01, rows[81]['supplier'], input_bindings=())
    rows[82]['supplier'] = root_decision.decide_root_v01(kernel=rows[12]['supplier'], decision_input=rows[81]['supplier'])
    assert_equal(record_validation(82, root_decision.validate_root_decision_result_v01, root_decision.validate_root_decision_result_v01(kernel=rows[12]['supplier'], decision_input=rows[81]['supplier'], result=rows[82]['supplier']), ((12, rows[12]['supplier']), (81, rows[81]['supplier']), (82, rows[82]['supplier']))), (), 'row082_supplier')
    assert_equal((rows[82]['supplier'].decision, rows[82]['supplier'].reason_code, rows[82]['supplier'].selected_candidate_id, rows[82]['supplier'].root_commit_created, rows[82]['supplier'].permission_created, rows[82]['supplier'].final_output_created, rows[82]['supplier'].effect_requested), ('ACCEPT', 'validated_candidate_accepted', packet_candidate_id, True, False, False, False), 'row082_supplier_outcome')
    emit_receipt(82, 1, 'supplier', root_decision.decide_root_v01, rows[82]['supplier'], input_bindings=())
    rows[83]['supplier'] = action_packet.build_root_decision_candidate_projection_v01(candidate_kind=action_packet.ROOT_DECISION_CANDIDATE_KIND_PACKET_AUTHORIZATION_V01, projected_candidate_id=packet_candidate_id, root_decision_kernel=rows[12]['supplier'], root_decision_input=rows[81]['supplier'], root_decision_result=rows[82]['supplier'])
    assert_equal(record_validation(83, action_packet.validate_root_decision_candidate_projection_v01, action_packet.validate_root_decision_candidate_projection_v01(rows[83]['supplier']), ((83, rows[83]['supplier']),)), (True, ()), 'row083_supplier')
    assert_equal(record_validation(83, action_packet.validate_supplier_root_context_coherence_v01, action_packet.validate_supplier_root_context_coherence_v01(rows[75]['supplier'], rows[83]['supplier']), ((75, rows[75]['supplier']), (83, rows[83]['supplier']))), (True, ()), 'row083_supplier_context')
    emit_receipt(83, 1, 'supplier', action_packet.build_root_decision_candidate_projection_v01, rows[83]['supplier'], input_bindings=())
    rows[84]['supplier'] = action_packet.build_supplier_root_bound_action_commit_packet_v02_projection_v01(canonical_projection=rows[75]['supplier'], root_decision_projection=rows[83]['supplier'])
    assert_equal(record_validation(84, action_packet.validate_supplier_root_bound_action_commit_packet_v02_projection_v01, action_packet.validate_supplier_root_bound_action_commit_packet_v02_projection_v01(rows[84]['supplier']), ((84, rows[84]['supplier']),)), (True, ()), 'row084_supplier')
    emit_receipt(84, 1, 'supplier', action_packet.build_supplier_root_bound_action_commit_packet_v02_projection_v01, rows[84]['supplier'], input_bindings=())
    rows[85]['supplier'] = transition_registry.build_action_packet_transition_registry_profile_v01()
    assert_equal(record_validation(85, transition_registry.validate_action_packet_transition_registry_profile_v01, transition_registry.validate_action_packet_transition_registry_profile_v01(rows[85]['supplier']), ((85, rows[85]['supplier']),)), (), 'row085_supplier')
    emit_receipt(85, 1, 'supplier', transition_registry.build_action_packet_transition_registry_profile_v01, rows[85]['supplier'], input_bindings=())
    rows[86]['supplier'] = action_packet.build_empty_action_commit_packet_registry_v02()
    assert_equal(record_validation(86, action_packet.validate_action_commit_packet_registry_v02, action_packet.validate_action_commit_packet_registry_v02(rows[86]['supplier']), ((86, rows[86]['supplier']),)), (True, ()), 'row086_supplier')
    emit_receipt(86, 1, 'supplier', action_packet.build_empty_action_commit_packet_registry_v02, rows[86]['supplier'], input_bindings=())
    rows[87]['supplier'] = action_packet.record_action_packet_genesis_v01(rows[86]['supplier'], root_bound_genesis=rows[84]['supplier'], action_packet_transition_registry_profile=rows[85]['supplier'])
    assert_equal(record_validation(87, action_packet.validate_action_commit_packet_registry_v02, action_packet.validate_action_commit_packet_registry_v02(rows[87]['supplier']), ((87, rows[87]['supplier']),)), (True, ()), 'row087_supplier')
    emit_receipt(87, 1, 'supplier', action_packet.record_action_packet_genesis_v01, rows[87]['supplier'], input_bindings=())
    packet_id = rows[84]['supplier'].packet_identity.packet_id
    idempotency_key = rows[75]['supplier'].idempotency_identity.idempotency_key
    transition_ref_material = {'packet_genesis_valid': packet_id, 'source_root_authorization_valid': rows[82]['supplier'].decision_id, 'idempotency_acquisition_valid': idempotency_key}
    activation_rule = transition_registry.lookup_action_packet_transition_rule_v01(registry=rows[85]['supplier'], transition_rule_id='g2a_t01_activate_root_authorization')
    activation_bindings = []
    for component_ordinal, evidence_code in enumerate(activation_rule.required_evidence_codes, start=1):
        evidence_ref = transition_ref_material[evidence_code]
        binding = action_packet.build_transition_evidence_binding_v01(action_packet_transition_registry_profile=rows[85]['supplier'], transition_rule_id=activation_rule.transition_rule_id, evidence_code=evidence_code, evidence_ref=evidence_ref, evidence_sha256=hashlib.sha256(canonical_json_bytes_v01(evidence_ref)).hexdigest(), validator_profile_id='validator:g2f:packet-transition:v01')
        assert_equal(record_validation(88, action_packet.validate_transition_evidence_binding_v01, action_packet.validate_transition_evidence_binding_v01(binding, action_packet_transition_registry_profile=rows[85]['supplier'], transition_rule_id=activation_rule.transition_rule_id), ((85, rows[85]['supplier']),)), (True, ()), f'row088_{component_ordinal}')
        activation_bindings.append(binding)
        emit_component(88, component_ordinal, 'supplier', action_packet.build_transition_evidence_binding_v01, (evidence_ref,), binding, evidence_code)
    rows[88]['supplier'] = tuple(activation_bindings)
    assert_equal(len(rows[88]['supplier']), 3, 'row088_cardinality')
    emit_receipt(88, 1, 'supplier', action_packet.build_transition_evidence_binding_v01, rows[88]['supplier'], input_bindings=())
    rows[89]['supplier'] = action_packet.build_action_packet_transition_event_v01(action_packet_transition_registry_profile=rows[85]['supplier'], transition_rule_id=activation_rule.transition_rule_id, packet_id=packet_id, idempotency_key=idempotency_key, previous_transition_event_id=None, owning_local_root_id=supplier_root_id, root_decision_ref=rows[82]['supplier'].decision_id, transition_evidence_bindings=rows[88]['supplier'], dependency_set_candidate_fingerprint=rows[75]['supplier'].dependency_set_candidate_fingerprint, temporal_authority_fingerprint=rows[75]['supplier'].temporal_authority_fingerprint, evaluation_time=PACKET_EVALUATION_TIME, evaluation_time_source='g2f_deterministic_logical_time', evaluation_context_id='evaluation_context:g2f:supplier:activation:v01', execution_attempt_identity=None, receipt_ref=None)
    assert_equal(record_validation(89, action_packet.validate_action_packet_transition_event_v01, action_packet.validate_action_packet_transition_event_v01(rows[89]['supplier'], action_packet_transition_registry_profile=rows[85]['supplier']), ((85, rows[85]['supplier']), (89, rows[89]['supplier']))), (True, ()), 'row089_supplier')
    emit_receipt(89, 1, 'supplier', action_packet.build_action_packet_transition_event_v01, rows[89]['supplier'], input_bindings=())
    rows[90]['supplier'] = action_packet.build_idempotency_disposition_event_v01(idempotency_key=idempotency_key, event_class='RESERVE', from_disposition='UNCLAIMED', to_disposition='RESERVED', from_owner_packet_id=None, to_owner_packet_id=packet_id, previous_disposition_event_id=None, cause_transition_event_ids=(rows[89]['supplier'].transition_event_id,), root_decision_ref=rows[82]['supplier'].decision_id, predecessor_packet_id=None, successor_packet_id=None, evidence_refs=tuple(sorted((binding.transition_evidence_binding_id for binding in rows[88]['supplier']), key=lambda item: item.encode('utf-8'))), evaluation_time=rows[89]['supplier'].evaluation_time, evaluation_time_source=rows[89]['supplier'].evaluation_time_source, evaluation_context_id=rows[89]['supplier'].evaluation_context_id)
    assert_equal(record_validation(90, action_packet.validate_idempotency_disposition_history_v01, action_packet.validate_idempotency_disposition_history_v01((rows[90]['supplier'],)), ((90, rows[90]['supplier']),)), (True, ()), 'row090_supplier')
    emit_receipt(90, 1, 'supplier', action_packet.build_idempotency_disposition_event_v01, rows[90]['supplier'], input_bindings=())
    rows[91]['supplier'] = action_packet.activate_action_packet_lifecycle_v01(rows[87]['supplier'], packet_id=packet_id, transition_event=rows[89]['supplier'], disposition_event=rows[90]['supplier'], action_packet_transition_registry_profile=rows[85]['supplier'])
    assert_equal(record_validation(91, action_packet.validate_action_commit_packet_registry_v02, action_packet.validate_action_commit_packet_registry_v02(rows[91]['supplier']), ((91, rows[91]['supplier']),)), (True, ()), 'row091_supplier')
    emit_receipt(91, 1, 'supplier', action_packet.activate_action_packet_lifecycle_v01, rows[91]['supplier'], input_bindings=())
    queue_rule = transition_registry.lookup_action_packet_transition_rule_v01(registry=rows[85]['supplier'], transition_rule_id='g2a_t02_queue')
    queue_ref_material = {'transition_history_valid': rows[89]['supplier'].transition_event_id, 'temporal_authority_valid': rows[75]['supplier'].temporal_authority_fingerprint, 'mandatory_dependencies_current': rows[75]['supplier'].dependency_set_candidate_fingerprint, 'idempotency_reservation_owned': rows[90]['supplier'].idempotency_disposition_event_id}
    queue_bindings = []
    for component_ordinal, evidence_code in enumerate(queue_rule.required_evidence_codes, start=1):
        evidence_ref = queue_ref_material[evidence_code]
        binding = action_packet.build_transition_evidence_binding_v01(action_packet_transition_registry_profile=rows[85]['supplier'], transition_rule_id=queue_rule.transition_rule_id, evidence_code=evidence_code, evidence_ref=evidence_ref, evidence_sha256=hashlib.sha256(canonical_json_bytes_v01(evidence_ref)).hexdigest(), validator_profile_id='validator:g2f:packet-transition:v01')
        assert_equal(record_validation(92, action_packet.validate_transition_evidence_binding_v01, action_packet.validate_transition_evidence_binding_v01(binding, action_packet_transition_registry_profile=rows[85]['supplier'], transition_rule_id=queue_rule.transition_rule_id), ((85, rows[85]['supplier']),)), (True, ()), f'row092_{component_ordinal}')
        queue_bindings.append(binding)
        emit_component(92, component_ordinal, 'supplier', action_packet.build_transition_evidence_binding_v01, (evidence_ref,), binding, evidence_code)
    rows[92]['supplier'] = tuple(queue_bindings)
    assert_equal(len(rows[92]['supplier']), 4, 'row092_cardinality')
    emit_receipt(92, 1, 'supplier', action_packet.build_transition_evidence_binding_v01, rows[92]['supplier'], input_bindings=())
    rows[93]['supplier'] = action_packet.build_action_packet_transition_event_v01(action_packet_transition_registry_profile=rows[85]['supplier'], transition_rule_id=queue_rule.transition_rule_id, packet_id=packet_id, idempotency_key=idempotency_key, previous_transition_event_id=rows[89]['supplier'].transition_event_id, owning_local_root_id=supplier_root_id, root_decision_ref=None, transition_evidence_bindings=rows[92]['supplier'], dependency_set_candidate_fingerprint=rows[75]['supplier'].dependency_set_candidate_fingerprint, temporal_authority_fingerprint=rows[75]['supplier'].temporal_authority_fingerprint, evaluation_time=PACKET_EVALUATION_TIME + 1, evaluation_time_source='g2f_deterministic_logical_time', evaluation_context_id='evaluation_context:g2f:supplier:queue:v01', execution_attempt_identity=None, receipt_ref=None)
    assert_equal(record_validation(93, action_packet.validate_action_packet_transition_event_v01, action_packet.validate_action_packet_transition_event_v01(rows[93]['supplier'], action_packet_transition_registry_profile=rows[85]['supplier']), ((85, rows[85]['supplier']), (93, rows[93]['supplier']))), (True, ()), 'row093_supplier')
    emit_receipt(93, 1, 'supplier', action_packet.build_action_packet_transition_event_v01, rows[93]['supplier'], input_bindings=())
    rows[94]['supplier'] = action_packet.append_action_packet_lifecycle_transition_v01(rows[91]['supplier'], packet_id=packet_id, transition_event=rows[93]['supplier'], action_packet_transition_registry_profile=rows[85]['supplier'])
    assert_equal(record_validation(94, action_packet.validate_action_commit_packet_registry_v02, action_packet.validate_action_commit_packet_registry_v02(rows[94]['supplier']), ((94, rows[94]['supplier']),)), (True, ()), 'row094_registry')
    original_entry = rows[94]['supplier'].action_packet_lifecycle_entries[0]
    assert_equal(record_validation(94, action_packet.validate_action_packet_transition_history_v01, action_packet.validate_action_packet_transition_history_v01(original_entry.transition_events, root_bound_genesis=original_entry.root_bound_genesis, action_packet_transition_registry_profile=rows[85]['supplier'], invalidation_contexts=rows[94]['supplier'].action_packet_invalidation_contexts, idempotency_disposition_events=rows[94]['supplier'].idempotency_disposition_events, lifecycle_entries=rows[94]['supplier'].action_packet_lifecycle_entries), ((85, rows[85]['supplier']), (94, rows[94]['supplier'].action_packet_invalidation_contexts), (94, rows[94]['supplier'].action_packet_lifecycle_entries), (94, rows[94]['supplier'].idempotency_disposition_events))), (True, ()), 'row094_history')
    emit_receipt(94, 1, 'supplier', action_packet.append_action_packet_lifecycle_transition_v01, rows[94]['supplier'], input_bindings=())
    pending_context_id = 'evaluation_context:g2f:supplier:pending:v01'
    rows[95]['supplier'] = action_packet.build_action_execution_attempt_identity_v01(packet_id=packet_id, idempotency_key=idempotency_key, attempt_ordinal=1, evaluation_context_id=pending_context_id)
    assert_equal(record_validation(95, action_packet.validate_action_execution_attempt_identity_v01, action_packet.validate_action_execution_attempt_identity_v01(rows[95]['supplier']), ((95, rows[95]['supplier']),)), (True, ()), 'row095_supplier')
    emit_receipt(95, 1, 'supplier', action_packet.build_action_execution_attempt_identity_v01, rows[95]['supplier'], input_bindings=())
    pending_rule = transition_registry.lookup_action_packet_transition_rule_v01(registry=rows[85]['supplier'], transition_rule_id='g2a_t03_pending')
    pending_ref_material = {'immediate_prefulfillment_validation_pass': rows[95]['supplier'].execution_attempt_id, 'transition_history_valid': rows[93]['supplier'].transition_event_id, 'idempotency_reservation_owned': rows[90]['supplier'].idempotency_disposition_event_id}
    pending_bindings = []
    for component_ordinal, evidence_code in enumerate(pending_rule.required_evidence_codes, start=1):
        evidence_ref = pending_ref_material[evidence_code]
        binding = action_packet.build_transition_evidence_binding_v01(action_packet_transition_registry_profile=rows[85]['supplier'], transition_rule_id=pending_rule.transition_rule_id, evidence_code=evidence_code, evidence_ref=evidence_ref, evidence_sha256=hashlib.sha256(canonical_json_bytes_v01(evidence_ref)).hexdigest(), validator_profile_id='validator:g2f:packet-transition:v01')
        assert_equal(record_validation(96, action_packet.validate_transition_evidence_binding_v01, action_packet.validate_transition_evidence_binding_v01(binding, action_packet_transition_registry_profile=rows[85]['supplier'], transition_rule_id=pending_rule.transition_rule_id), ((85, rows[85]['supplier']),)), (True, ()), f'row096_{component_ordinal}')
        pending_bindings.append(binding)
        emit_component(96, component_ordinal, 'supplier', action_packet.build_transition_evidence_binding_v01, (evidence_ref,), binding, evidence_code)
    rows[96]['supplier'] = tuple(pending_bindings)
    assert_equal(len(rows[96]['supplier']), 3, 'row096_cardinality')
    emit_receipt(96, 1, 'supplier', action_packet.build_transition_evidence_binding_v01, rows[96]['supplier'], input_bindings=())
    rows[97]['supplier'] = action_packet.build_action_packet_transition_event_v01(action_packet_transition_registry_profile=rows[85]['supplier'], transition_rule_id=pending_rule.transition_rule_id, packet_id=packet_id, idempotency_key=idempotency_key, previous_transition_event_id=rows[93]['supplier'].transition_event_id, owning_local_root_id=supplier_root_id, root_decision_ref=None, transition_evidence_bindings=rows[96]['supplier'], dependency_set_candidate_fingerprint=rows[75]['supplier'].dependency_set_candidate_fingerprint, temporal_authority_fingerprint=rows[75]['supplier'].temporal_authority_fingerprint, evaluation_time=PACKET_EVALUATION_TIME + 2, evaluation_time_source='g2f_deterministic_logical_time', evaluation_context_id=pending_context_id, execution_attempt_identity=rows[95]['supplier'], receipt_ref=None)
    assert_equal(record_validation(97, action_packet.validate_action_packet_transition_event_v01, action_packet.validate_action_packet_transition_event_v01(rows[97]['supplier'], action_packet_transition_registry_profile=rows[85]['supplier']), ((85, rows[85]['supplier']), (97, rows[97]['supplier']))), (True, ()), 'row097_supplier')
    emit_receipt(97, 1, 'supplier', action_packet.build_action_packet_transition_event_v01, rows[97]['supplier'], input_bindings=())
    rows[98]['supplier'] = action_packet.append_action_packet_lifecycle_transition_v01(rows[94]['supplier'], packet_id=packet_id, transition_event=rows[97]['supplier'], action_packet_transition_registry_profile=rows[85]['supplier'])
    assert_equal(record_validation(98, action_packet.validate_action_commit_packet_registry_v02, action_packet.validate_action_commit_packet_registry_v02(rows[98]['supplier']), ((98, rows[98]['supplier']),)), (True, ()), 'row098_registry')
    original_entry = rows[98]['supplier'].action_packet_lifecycle_entries[0]
    assert_equal(record_validation(98, action_packet.validate_action_packet_transition_history_v01, action_packet.validate_action_packet_transition_history_v01(original_entry.transition_events, root_bound_genesis=original_entry.root_bound_genesis, action_packet_transition_registry_profile=rows[85]['supplier'], invalidation_contexts=rows[98]['supplier'].action_packet_invalidation_contexts, idempotency_disposition_events=rows[98]['supplier'].idempotency_disposition_events, lifecycle_entries=rows[98]['supplier'].action_packet_lifecycle_entries), ((85, rows[85]['supplier']), (98, rows[98]['supplier'].action_packet_invalidation_contexts), (98, rows[98]['supplier'].action_packet_lifecycle_entries), (98, rows[98]['supplier'].idempotency_disposition_events))), (True, ()), 'row098_history')
    emit_receipt(98, 1, 'supplier', action_packet.append_action_packet_lifecycle_transition_v01, rows[98]['supplier'], input_bindings=())
    rows[99]['supplier'] = action_packet.CorridorStepV01(step_id='corridor_step:mock_payment_order', parent_packet_id=rows[84]['supplier'].packet.packet_id, allowed_subjects=rows[75]['supplier'].source_packet.scope.allowed_subjects, forbidden_subjects=rows[75]['supplier'].source_packet.scope.forbidden_subjects, allowed_actions=(rows[75]['supplier'].selected_legacy_action,), forbidden_actions=rows[75]['supplier'].source_packet.scope.forbidden_actions, adapter_id=rows[75]['supplier'].source_packet.adapter_binding.adapter_id, ttl_seconds=rows[75]['supplier'].source_packet.ttl.ttl_seconds, amount=rows[75]['supplier'].source_packet.scope.amount, creditor_ref=rows[75]['supplier'].source_packet.scope.creditor_ref, payment_slot_ref=rows[75]['supplier'].source_packet.scope.payment_slot_ref, idempotency_key=rows[75]['supplier'].source_packet.idempotency.key, creates_permission=False, creates_final_output=False, releases_shipment=False, executes_real_payment=False, calls_real_api=False)
    assert_equal(type(rows[99]['supplier']), action_packet.CorridorStepV01, 'row099_exact_type')
    assert_equal((rows[99]['supplier'].step_id, rows[99]['supplier'].parent_packet_id, rows[99]['supplier'].allowed_subjects, rows[99]['supplier'].forbidden_subjects, rows[99]['supplier'].allowed_actions, rows[99]['supplier'].forbidden_actions, rows[99]['supplier'].adapter_id, rows[99]['supplier'].ttl_seconds, rows[99]['supplier'].amount, rows[99]['supplier'].creditor_ref, rows[99]['supplier'].payment_slot_ref, rows[99]['supplier'].idempotency_key, rows[99]['supplier'].creates_permission, rows[99]['supplier'].creates_final_output, rows[99]['supplier'].releases_shipment, rows[99]['supplier'].executes_real_payment, rows[99]['supplier'].calls_real_api), ('corridor_step:mock_payment_order', rows[84]['supplier'].packet.packet_id, rows[75]['supplier'].source_packet.scope.allowed_subjects, rows[75]['supplier'].source_packet.scope.forbidden_subjects, (rows[75]['supplier'].selected_legacy_action,), rows[75]['supplier'].source_packet.scope.forbidden_actions, rows[75]['supplier'].source_packet.adapter_binding.adapter_id, rows[75]['supplier'].source_packet.ttl.ttl_seconds, rows[75]['supplier'].source_packet.scope.amount, rows[75]['supplier'].source_packet.scope.creditor_ref, rows[75]['supplier'].source_packet.scope.payment_slot_ref, rows[75]['supplier'].source_packet.idempotency.key, False, False, False, False, False), 'row099_exact_public_typed_bindings')
    emit_receipt(99, 1, 'supplier', action_packet.CorridorStepV01, rows[99]['supplier'], input_bindings=())
    rows[100]['supplier'] = action_packet.ContractFulfillmentCorridorV01(corridor_id='corridor:g2f:supplier:bounded:v01', packet_id=packet_id, corridor_kind=rows[75]['supplier'].adapter_binding.corridor_class, deterministic_only=True, post_root_llm_reasoning_allowed=False, reasoning_restarted_after_root=False, allowed_steps=(rows[99]['supplier'].step_id,), root_review_required_on_mismatch=True)
    assert_equal(record_validation(100, action_packet.validate_corridor_no_post_root_reasoning_v01, action_packet.validate_corridor_no_post_root_reasoning_v01(rows[100]['supplier']), ((100, rows[100]['supplier']),)), (True, ()), 'row100_supplier')
    emit_receipt(100, 1, 'supplier', action_packet.ContractFulfillmentCorridorV01, rows[100]['supplier'], input_bindings=())
    present_context_id = 'evaluation_context:g2f:supplier:present:v01'
    rows[101]['supplier'] = action_packet.build_action_dependency_current_observation_v01(dependency_id=rows[72]['supplier'].dependency_id, evidence_ref=rows[72]['supplier'].evidence_ref, observed_content_sha256=rows[72]['supplier'].content_sha256, time_envelope_id=rows[72]['supplier'].time_envelope_id, freshness_policy_id=rows[72]['supplier'].freshness_policy_id, source_provenance_refs=rows[72]['supplier'].source_provenance_refs, valid_from_utc=PACKET_VALID_FROM_TIME, valid_to_utc=PACKET_VALID_TO_TIME, observed_at_utc=PACKET_EVALUATION_TIME + 3, observation_context_id=present_context_id)
    assert_equal(record_validation(101, action_packet.validate_action_dependency_current_observation_v01, action_packet.validate_action_dependency_current_observation_v01(rows[101]['supplier']), ((101, rows[101]['supplier']),)), (True, ()), 'row101_supplier')
    emit_receipt(101, 1, 'supplier', action_packet.build_action_dependency_current_observation_v01, rows[101]['supplier'], input_bindings=())
    rows[102]['supplier'] = action_packet.build_logical_time_bridge_v01(origin_utc_epoch_seconds=PACKET_VALID_FROM_TIME, seconds_per_tick=1, bridge_policy_version='g2f_epoch_seconds_v01')
    assert_equal(record_validation(102, action_packet.validate_logical_time_bridge_v01, action_packet.validate_logical_time_bridge_v01(rows[102]['supplier']), ((102, rows[102]['supplier']),)), (True, ()), 'row102_supplier')
    emit_receipt(102, 1, 'supplier', action_packet.build_logical_time_bridge_v01, rows[102]['supplier'], input_bindings=())
    rows[103]['supplier'] = action_packet.inspect_action_packet_present_eligibility_v01(rows[98]['supplier'], packet_id=packet_id, corridor=rows[100]['supplier'], corridor_step=rows[99]['supplier'], current_dependency_observations=(rows[101]['supplier'],), logical_time_bridge=rows[102]['supplier'], evaluation_time=PACKET_EVALUATION_TIME + 3, evaluation_time_source='g2f_deterministic_logical_time', evaluation_context_id=present_context_id, action_packet_transition_registry_profile=rows[85]['supplier'])
    assert_equal(record_validation(103, action_packet.validate_action_packet_present_eligibility_inspection_v01, action_packet.validate_action_packet_present_eligibility_inspection_v01(rows[103]['supplier'], rows[98]['supplier'], packet_id=packet_id, corridor=rows[100]['supplier'], corridor_step=rows[99]['supplier'], current_dependency_observations=(rows[101]['supplier'],), logical_time_bridge=rows[102]['supplier'], evaluation_time=PACKET_EVALUATION_TIME + 3, evaluation_time_source='g2f_deterministic_logical_time', evaluation_context_id=present_context_id, action_packet_transition_registry_profile=rows[85]['supplier']), ((85, rows[85]['supplier']), (98, rows[98]['supplier']), (99, rows[99]['supplier']), (100, rows[100]['supplier']), (101, rows[101]['supplier']), (102, rows[102]['supplier']), (103, rows[103]['supplier']))), (True, ()), 'row103_supplier')
    assert_equal((rows[103]['supplier'].present_eligibility_status, rows[103]['supplier'].present_executable, rows[103]['supplier'].adapter_calls, rows[103]['supplier'].real_world_effects_count), ('ELIGIBLE_FOR_BOUNDED_MOCK_ATTEMPT', True, 0, 0), 'row103_outcome')
    emit_receipt(103, 1, 'supplier', action_packet.inspect_action_packet_present_eligibility_v01, rows[103]['supplier'], input_bindings=())
    hostile_step = action_packet.CorridorStepV01(step_id=rows[99]['supplier'].step_id, parent_packet_id=rows[84]['supplier'].packet.packet_id, allowed_subjects=rows[75]['supplier'].source_packet.scope.allowed_subjects, forbidden_subjects=rows[75]['supplier'].source_packet.scope.forbidden_subjects, allowed_actions=(rows[75]['supplier'].selected_legacy_action,), forbidden_actions=rows[75]['supplier'].source_packet.scope.forbidden_actions, adapter_id=rows[75]['supplier'].adapter_binding.adapter_id, ttl_seconds=rows[75]['supplier'].source_packet.ttl.ttl_seconds, amount=rows[75]['supplier'].source_packet.scope.amount, creditor_ref=rows[75]['supplier'].source_packet.scope.creditor_ref, payment_slot_ref=rows[75]['supplier'].source_packet.scope.payment_slot_ref, idempotency_key=rows[75]['supplier'].source_packet.idempotency.key, creates_permission=False, creates_final_output=False, releases_shipment=False, executes_real_payment=False, calls_real_api=False)
    positive_step_plain = {'step_id': rows[99]['supplier'].step_id, 'parent_packet_id': rows[99]['supplier'].parent_packet_id, 'allowed_subjects': rows[99]['supplier'].allowed_subjects, 'forbidden_subjects': rows[99]['supplier'].forbidden_subjects, 'allowed_actions': rows[99]['supplier'].allowed_actions, 'forbidden_actions': rows[99]['supplier'].forbidden_actions, 'adapter_id': rows[99]['supplier'].adapter_id, 'ttl_seconds': rows[99]['supplier'].ttl_seconds, 'amount': rows[99]['supplier'].amount, 'creditor_ref': rows[99]['supplier'].creditor_ref, 'payment_slot_ref': rows[99]['supplier'].payment_slot_ref, 'idempotency_key': rows[99]['supplier'].idempotency_key, 'creates_permission': rows[99]['supplier'].creates_permission, 'creates_final_output': rows[99]['supplier'].creates_final_output, 'releases_shipment': rows[99]['supplier'].releases_shipment, 'executes_real_payment': rows[99]['supplier'].executes_real_payment, 'calls_real_api': rows[99]['supplier'].calls_real_api}
    hostile_step_plain = {'step_id': hostile_step.step_id, 'parent_packet_id': hostile_step.parent_packet_id, 'allowed_subjects': hostile_step.allowed_subjects, 'forbidden_subjects': hostile_step.forbidden_subjects, 'allowed_actions': hostile_step.allowed_actions, 'forbidden_actions': hostile_step.forbidden_actions, 'adapter_id': hostile_step.adapter_id, 'ttl_seconds': hostile_step.ttl_seconds, 'amount': hostile_step.amount, 'creditor_ref': hostile_step.creditor_ref, 'payment_slot_ref': hostile_step.payment_slot_ref, 'idempotency_key': hostile_step.idempotency_key, 'creates_permission': hostile_step.creates_permission, 'creates_final_output': hostile_step.creates_final_output, 'releases_shipment': hostile_step.releases_shipment, 'executes_real_payment': hostile_step.executes_real_payment, 'calls_real_api': hostile_step.calls_real_api}
    hostile_leaf_diffs = tuple((key for key in positive_step_plain if positive_step_plain[key] != hostile_step_plain[key]))
    assert_equal(hostile_leaf_diffs, ('adapter_id',), 'row103_hostile_leaf_diff')
    assert_equal(rows[99]['supplier'].adapter_id, 'mock_bank_sandbox', 'row103_positive_adapter')
    assert_equal(hostile_step.adapter_id, 'mock_adapter:mock_bank_sandbox', 'row103_hostile_adapter')
    hostile_report = action_packet.inspect_action_packet_present_eligibility_v01(rows[98]['supplier'], packet_id=packet_id, corridor=rows[100]['supplier'], corridor_step=hostile_step, current_dependency_observations=(rows[101]['supplier'],), logical_time_bridge=rows[102]['supplier'], evaluation_time=PACKET_EVALUATION_TIME + 3, evaluation_time_source='g2f_deterministic_logical_time', evaluation_context_id=present_context_id, action_packet_transition_registry_profile=rows[85]['supplier'])
    assert_equal(type(hostile_report), action_packet.ActionPacketPresentEligibilityInspectionV01, 'row103_hostile_report_type')
    assert_equal(hostile_report.present_eligibility_status, 'NON_EXECUTABLE', 'row103_hostile_status')
    assert_equal(hostile_report.present_executable, False, 'row103_hostile_executable')
    assert_equal(hostile_report.retry_eligible, False, 'row103_hostile_retry')
    assert_equal(hostile_report.reason_codes, ('action_packet_corridor_legacy_invalid',), 'row103_hostile_reasons')
    assert_equal(hostile_report.adapter_calls, 0, 'row103_hostile_adapter_calls')
    assert_equal(hostile_report.real_world_effects_count, 0, 'row103_hostile_effects')
    assert_equal(hostile_report.historical_state.lifecycle_state, 'PENDING_FULFILLMENT', 'row103_hostile_history')
    assert_equal(hostile_report.historical_result_unchanged, True, 'row103_hostile_history_unchanged')
    assert_equal(hostile_report.creates_authority, False, 'row103_hostile_authority')
    assert_equal(hostile_report.creates_permission, False, 'row103_hostile_permission')
    assert_equal(hostile_report.creates_packet, False, 'row103_hostile_packet')
    assert_equal(hostile_report.creates_receipt, False, 'row103_hostile_receipt')
    hostile_report_validator_result = record_validation(104, action_packet.validate_action_packet_present_eligibility_inspection_v01, action_packet.validate_action_packet_present_eligibility_inspection_v01(hostile_report, rows[98]['supplier'], packet_id=packet_id, corridor=rows[100]['supplier'], corridor_step=hostile_step, current_dependency_observations=(rows[101]['supplier'],), logical_time_bridge=rows[102]['supplier'], evaluation_time=PACKET_EVALUATION_TIME + 3, evaluation_time_source='g2f_deterministic_logical_time', evaluation_context_id=present_context_id, action_packet_transition_registry_profile=rows[85]['supplier']), ((85, rows[85]['supplier']), (98, rows[98]['supplier']), (100, rows[100]['supplier']), (101, rows[101]['supplier']), (102, rows[102]['supplier'])))
    assert_equal(hostile_report_validator_result, (True, ()), 'row103_hostile_report_public_validator')
    positive_report_against_hostile_result = record_validation(104, action_packet.validate_action_packet_present_eligibility_inspection_v01, action_packet.validate_action_packet_present_eligibility_inspection_v01(rows[103]['supplier'], rows[98]['supplier'], packet_id=packet_id, corridor=rows[100]['supplier'], corridor_step=hostile_step, current_dependency_observations=(rows[101]['supplier'],), logical_time_bridge=rows[102]['supplier'], evaluation_time=PACKET_EVALUATION_TIME + 3, evaluation_time_source='g2f_deterministic_logical_time', evaluation_context_id=present_context_id, action_packet_transition_registry_profile=rows[85]['supplier']), ((85, rows[85]['supplier']), (98, rows[98]['supplier']), (100, rows[100]['supplier']), (101, rows[101]['supplier']), (102, rows[102]['supplier']), (103, rows[103]['supplier'])))
    assert_equal(positive_report_against_hostile_result, (False, ('action_packet_present_inspection_report_mismatch',)), 'row103_positive_report_hostile_input_mismatch')
    observed_dependency_value = 11
    observed_dependency_content_sha256 = hashlib.sha256(canonical_json_bytes_v01(observed_dependency_value)).hexdigest()
    assert_equal(rows[72]['supplier'].content_sha256, hashlib.sha256(canonical_json_bytes_v01(12)).hexdigest(), 'row104_baseline_scenario_digest')
    rows[104]['supplier'] = action_packet.build_action_invalidation_evidence_v01(source_invalidation_event_ref='dependency-change:g2f:supplier:water-filter:v01', packet_id=packet_id, dependency_id=rows[72]['supplier'].dependency_id, invalidation_class='DEPENDENCY_CHANGED', evidence_ref=rows[72]['supplier'].evidence_ref, evidence_sha256=observed_dependency_content_sha256, observed_status='CHANGED', time_envelope_id=rows[72]['supplier'].time_envelope_id, freshness_policy_id=rows[72]['supplier'].freshness_policy_id, owning_local_root_id=supplier_root_id, accepted_by_local_root_id=supplier_root_id, acceptance_root_decision_id=None, acceptance_root_decision_hash=None, authority_effect='DETERMINISTIC_BLOCK', root_decision_ref=None, evaluation_time=rows[42]['supplier'].evaluation_time_epoch_seconds, evaluation_time_source=rows[42]['supplier'].created_by, evaluation_context_id=rows[42]['supplier'].local_routing_snapshot_id)
    assert_equal(record_validation(104, action_packet.validate_action_invalidation_evidence_v01, action_packet.validate_action_invalidation_evidence_v01(rows[104]['supplier']), ((104, rows[104]['supplier']),)), (True, ()), 'row104_structural')
    assert_equal(record_validation(104, action_packet.validate_action_invalidation_evidence_against_packet_v01, action_packet.validate_action_invalidation_evidence_against_packet_v01(rows[104]['supplier'], rows[84]['supplier']), ((84, rows[84]['supplier']), (104, rows[104]['supplier']))), (True, ()), 'row104_context')
    assert_equal((rows[104]['supplier'].acceptance_root_decision_id, rows[104]['supplier'].acceptance_root_decision_hash, rows[104]['supplier'].root_decision_ref), (None, None, None), 'row104_root_acceptance_absence')
    assert_equal(rows[104]['supplier'].evidence_sha256, observed_dependency_content_sha256, 'row104_observed_content_digest')
    emit_receipt(104, 1, 'supplier', action_packet.build_action_invalidation_evidence_v01, rows[104]['supplier'], input_bindings=())
    supplier_bundle = rows[69]['supplier'][0]
    assert_equal(supplier_bundle.observed_work_context, None, 'row105_baseline_no_observed_work')
    root_inputs = tuple((item for item in supplier_bundle.cell_inputs if item.parent_cell_id is None))
    assert_equal(len(root_inputs), 1, 'row105_unique_root_input')
    baseline_root_input = root_inputs[0]
    assert_equal(len(baseline_root_input.ordered_planned_child_cell_ids), 2, 'row105_two_planned_children')
    delta_role_bindings: dict[str, dict[str, object]] = {}
    role_rows = (('SIBLING', 'unrelated_supplier_safe_sibling', 0), ('TARGET', 'supplier_water_filter_dependency_consumer', 1))
    for role, scenario_role, canonical_child_index in role_rows:
        expected_child_id = fractal_runtime.derive_fractal_child_cell_id_v02(topology_seed_id=supplier_bundle.topology_seed.topology_seed_id, parent_cell_id=baseline_root_input.cell_id, canonical_child_index=canonical_child_index, accepted_mode=supplier_bundle.source_binding.accepted_mode, selected_local_mode_profile_id=supplier_bundle.source_binding.selected_local_mode_profile_id, source_mode_profile_set_id=supplier_bundle.source_binding.source_mode_profile_set_id, child_scope_ref=supplier_bundle.topology.accepted_scope_ref, runtime_policy_id=supplier_bundle.source_binding.runtime_policy_id, required_capability_ids=supplier_bundle.source_binding.required_downstream_capability_ids, forbidden_claims=supplier_bundle.source_context.runtime_policy.forbidden_claims, child_depth=1)
        child_cell_id = expected_child_id
        child_matches = tuple((item for item in supplier_bundle.cell_inputs if item.cell_id == child_cell_id))
        assert_equal(len(child_matches), 1, 'row105_' + role + '_child_unique')
        child_input = child_matches[0]
        assert_equal(child_input.parent_cell_id, baseline_root_input.cell_id, 'row105_' + role + '_parent')
        projection_matches = tuple((item for item in supplier_bundle.scope_projections if item.child_cell_id == child_cell_id))
        assert_equal(len(projection_matches), 1, 'row105_' + role + '_projection_unique')
        projection = projection_matches[0]
        assert_equal(projection.projection_id, child_input.scope_projection_id, 'row105_' + role + '_projection_binding')
        assert_equal((projection.child_scope_ref, child_input.scope_ref, child_input.cell_depth), (supplier_bundle.topology.accepted_scope_ref, supplier_bundle.topology.accepted_scope_ref, 1), 'row105_' + role + '_semantic_scope')
        initial_node_id = child_input.ordered_node_ids[0]
        node_matches = tuple((item for item in supplier_bundle.topology_nodes if item.node_id == initial_node_id))
        assignment_matches = tuple((item for item in supplier_bundle.runtime_assignments if item.node_id == initial_node_id))
        assert_equal(len(node_matches), 1, 'row105_' + role + '_node_unique')
        assert_equal(len(assignment_matches), 1, 'row105_' + role + '_assignment_unique')
        node = node_matches[0]
        assignment = assignment_matches[0]
        initial_entries = tuple((item for item in supplier_bundle.queue_entries if item.queue_entry_id in child_input.ordered_initial_queue_entry_ids and item.node_id == initial_node_id and (item.predecessor_queue_entry_id is None)))
        assert_equal(len(initial_entries), 1, 'row105_' + role + '_initial_queue_unique')
        initial_entry = initial_entries[0]
        initial_artifacts = tuple((item for item in supplier_bundle.queue_artifacts if abi.kernel_artifact_to_plain_dict_v01(item)['payload']['queue_entry_id'] == initial_entry.queue_entry_id))
        assert_equal(len(initial_artifacts), 1, 'row105_' + role + '_initial_queue_artifact_unique')
        initial_artifact = initial_artifacts[0]
        assert_equal(initial_artifact.parent_refs[0], supplier_bundle.topology_artifact.artifact_id, 'row105_' + role + '_topology_parent')
        assert_equal(len(initial_artifact.parent_refs), 2, 'row105_' + role + '_parent_count')
        activation_artifacts = tuple((item for item in supplier_bundle.queue_artifacts if item.artifact_id == initial_artifact.parent_refs[1]))
        assert_equal(len(activation_artifacts), 1, 'row105_' + role + '_activation_parent')
        assert_equal(expected_child_id, child_input.cell_id, 'row105_' + role + '_derived_child')
        for report, marker in ((record_validation(105, fractal_runtime.validate_runtime_topology_node_v02, fractal_runtime.validate_runtime_topology_node_v02(node), ()), 'node'), (record_validation(105, fractal_runtime.validate_runtime_assignment_v02, fractal_runtime.validate_runtime_assignment_v02(assignment), ()), 'assignment'), (record_validation(105, fractal_runtime.validate_parent_child_scope_projection_v02, fractal_runtime.validate_parent_child_scope_projection_v02(projection), ()), 'projection'), (record_validation(105, fractal_runtime.validate_fractal_cell_input_v02, fractal_runtime.validate_fractal_cell_input_v02(child_input), ()), 'cell_input'), (record_validation(105, fractal_runtime.validate_fractal_cell_queue_entry_v02, fractal_runtime.validate_fractal_cell_queue_entry_v02(initial_entry), ()), 'queue_entry')):
            (report.status, report.reason_codes)
        assert_equal(record_validation(105, abi.validate_kernel_artifact_v01, abi.validate_kernel_artifact_v01(initial_artifact), ()), (), 'row105_' + role + '_queue_artifact')
        delta_role_bindings[role] = {'scenario_role': scenario_role, 'canonical_child_index': canonical_child_index, 'root_cell_id': baseline_root_input.cell_id, 'child_cell_id': child_input.cell_id, 'child_cell_input_id': child_input.cell_input_id, 'parent_cell_id': child_input.parent_cell_id, 'scope_projection_id': projection.projection_id, 'scope_ref': child_input.scope_ref, 'topology_node_id': node.node_id, 'topology_node_kind': node.node_kind, 'assignment_id': assignment.assignment_id, 'initial_queue_entry_id': initial_entry.queue_entry_id, 'initial_queue_artifact_id': initial_artifact.artifact_id, 'initial_queue_artifact_parent_refs': tuple(initial_artifact.parent_refs), 'activation_parent_artifact_id': activation_artifacts[0].artifact_id}
        if role == 'TARGET':
            target_child_input = child_input
            target_node = node
            target_initial_entry = initial_entry
            target_initial_artifact = initial_artifact
        else:
            sibling_child_input = child_input
            sibling_node = node
            sibling_initial_entry = initial_entry
            sibling_initial_artifact = initial_artifact
    assert_equal(set(baseline_root_input.ordered_planned_child_cell_ids), {delta_role_bindings['SIBLING']['child_cell_id'], delta_role_bindings['TARGET']['child_cell_id']}, 'row105_identity_resolved_child_set')
    g2e_time_envelope = {'ct_session_anchor': 'ct:g2f:supplier:g2e:v01', 'et_observed_at': EVALUATION_UTC, 'freshness_class': 'static', 'kt_asof': EVALUATION_UTC, 'pt_created_at': EVALUATION_UTC, 'ttl_seconds': 3600, 'valid_from': EVALUATION_UTC, 'valid_to': VALID_TO_UTC}
    baseline_source_payload = {'baseline_dependency_time_envelope_id': rows[72]['supplier'].time_envelope_id, 'content_sha256': rows[72]['supplier'].content_sha256, 'dependency_class': rows[72]['supplier'].dependency_class, 'dependency_id': rows[72]['supplier'].dependency_id, 'evidence_ref': rows[72]['supplier'].evidence_ref, 'expected_accepting_local_root_id': rows[72]['supplier'].expected_accepting_local_root_id, 'freshness_policy_id': rows[72]['supplier'].freshness_policy_id, 'projection_profile_id': 'g2f_supplier_dependency_currentness_projection_v01', 'projection_profile_version': 'v0.1', 'requirement_class': rows[72]['supplier'].requirement_class, 'source_provenance_refs': list(rows[72]['supplier'].source_provenance_refs)}
    observed_source_payload = {'baseline_dependency_time_envelope_id': rows[72]['supplier'].time_envelope_id, 'content_sha256': rows[104]['supplier'].evidence_sha256, 'dependency_class': rows[72]['supplier'].dependency_class, 'dependency_id': rows[72]['supplier'].dependency_id, 'evidence_ref': rows[72]['supplier'].evidence_ref, 'expected_accepting_local_root_id': rows[72]['supplier'].expected_accepting_local_root_id, 'freshness_policy_id': rows[72]['supplier'].freshness_policy_id, 'projection_profile_id': 'g2f_supplier_dependency_currentness_projection_v01', 'projection_profile_version': 'v0.1', 'requirement_class': rows[72]['supplier'].requirement_class, 'source_provenance_refs': list(rows[72]['supplier'].source_provenance_refs)}
    expected_source_keys = ('baseline_dependency_time_envelope_id', 'content_sha256', 'dependency_class', 'dependency_id', 'evidence_ref', 'expected_accepting_local_root_id', 'freshness_policy_id', 'projection_profile_id', 'projection_profile_version', 'requirement_class', 'source_provenance_refs')
    assert_equal(tuple(sorted(baseline_source_payload)), expected_source_keys, 'row105_baseline_keys')
    assert_equal(tuple(sorted(observed_source_payload)), expected_source_keys, 'row105_observed_keys')
    authoritative_fact_leaf_diff = plain_difference_rows(baseline_source_payload, observed_source_payload)
    assert_equal(len(authoritative_fact_leaf_diff), 1, 'row105_one_authoritative_leaf')
    assert_equal(authoritative_fact_leaf_diff[0]['pointer'], '/content_sha256', 'row105_authoritative_pointer')
    common_source_trace = ('trace:g2f:g2e:supplier-dependency-currentness',)
    baseline_identity_material = {'abi_version': 'v1.0', 'artifact_type': 'SemanticEvidence', 'schema_version': 'v1', 'transaction_id': supplier_transaction_id, 'owner_root_id': supplier_root_id, 'source_component': 'continuous_delta_runtime_g2f', 'authority_class': 'EVIDENCE_ONLY', 'lifecycle_state': 'VALIDATED', 'payload': baseline_source_payload, 'trace_refs': list(common_source_trace), 'parent_refs': [], 'time_envelope': g2e_time_envelope}
    assert_equal('artifact_id' in baseline_identity_material, False, 'row105_baseline_preimage_no_id')
    baseline_source_id = 'g2fv11_dependency_source_baseline_v01:' + hashlib.sha256(('HEDGEHOG_G2F_V11_SUPPLIER_DEPENDENCY_SOURCE_BASELINE_V01' + '\x00').encode('utf-8') + canonical_json_bytes_v01(baseline_identity_material)).hexdigest()
    baseline_source = abi.build_kernel_artifact_v01(abi_version='v1.0', artifact_id=baseline_source_id, artifact_type='SemanticEvidence', schema_version='v1', transaction_id=supplier_transaction_id, owner_root_id=supplier_root_id, source_component='continuous_delta_runtime_g2f', authority_class='EVIDENCE_ONLY', lifecycle_state='VALIDATED', payload=baseline_source_payload, trace_refs=common_source_trace, parent_refs=(), time_envelope=g2e_time_envelope)
    assert_equal(record_validation(105, abi.validate_kernel_artifact_v01, abi.validate_kernel_artifact_v01(baseline_source), ()), (), 'row105_baseline_source')
    target_runtime_plain = abi.kernel_artifact_to_plain_dict_v01(target_initial_artifact)
    target_runtime_sha256 = hashlib.sha256(canonical_json_bytes_v01(target_runtime_plain)).hexdigest()
    target_runtime_projection = abi.build_kernel_artifact_v01(abi_version='v1.0', artifact_id='artifact:g2f:g2e:runtime-projection:' + target_runtime_sha256, artifact_type='SemanticEvidence', schema_version='v1', transaction_id=supplier_transaction_id, owner_root_id=supplier_root_id, source_component='continuous_delta_runtime_g2f', authority_class='EVIDENCE_ONLY', lifecycle_state='VALIDATED', payload={'projection_profile_id': 'g2e_baseline_runtime_artifact_projection_v01', 'projected_runtime_artifact': target_runtime_plain, 'projected_runtime_artifact_sha256': target_runtime_sha256}, trace_refs=('trace:g2f:g2e:selected-runtime-projection',), parent_refs=(target_initial_artifact.artifact_id,), time_envelope=g2e_time_envelope)
    assert_equal(record_validation(105, abi.validate_kernel_artifact_v01, abi.validate_kernel_artifact_v01(target_runtime_projection), ()), (), 'row105_target_runtime_projection')
    assert_equal((target_runtime_projection.schema_version, target_runtime_projection.parent_refs, target_runtime_projection.transaction_id, target_runtime_projection.owner_root_id), ('v1', (target_initial_artifact.artifact_id,), target_initial_artifact.transaction_id, target_initial_artifact.owner_root_id), 'row105_target_runtime_projection_geometry')
    assert_equal(abi.kernel_artifact_to_plain_dict_v01(target_runtime_projection)['payload'], {'projection_profile_id': 'g2e_baseline_runtime_artifact_projection_v01', 'projected_runtime_artifact': target_runtime_plain, 'projected_runtime_artifact_sha256': target_runtime_sha256}, 'row105_target_runtime_projection_payload')
    sibling_runtime_plain = abi.kernel_artifact_to_plain_dict_v01(sibling_initial_artifact)
    sibling_runtime_sha256 = hashlib.sha256(canonical_json_bytes_v01(sibling_runtime_plain)).hexdigest()
    sibling_runtime_projection = abi.build_kernel_artifact_v01(abi_version='v1.0', artifact_id='artifact:g2f:g2e:runtime-projection:' + sibling_runtime_sha256, artifact_type='SemanticEvidence', schema_version='v1', transaction_id=supplier_transaction_id, owner_root_id=supplier_root_id, source_component='continuous_delta_runtime_g2f', authority_class='EVIDENCE_ONLY', lifecycle_state='VALIDATED', payload={'projection_profile_id': 'g2e_baseline_runtime_artifact_projection_v01', 'projected_runtime_artifact': sibling_runtime_plain, 'projected_runtime_artifact_sha256': sibling_runtime_sha256}, trace_refs=('trace:g2f:g2e:sibling-runtime-projection',), parent_refs=(sibling_initial_artifact.artifact_id,), time_envelope=g2e_time_envelope)
    assert_equal(record_validation(105, abi.validate_kernel_artifact_v01, abi.validate_kernel_artifact_v01(sibling_runtime_projection), ()), (), 'row105_sibling_runtime_projection')
    assert_equal((sibling_runtime_projection.schema_version, sibling_runtime_projection.parent_refs, sibling_runtime_projection.transaction_id, sibling_runtime_projection.owner_root_id), ('v1', (sibling_initial_artifact.artifact_id,), sibling_initial_artifact.transaction_id, sibling_initial_artifact.owner_root_id), 'row105_sibling_runtime_projection_geometry')
    assert_equal(abi.kernel_artifact_to_plain_dict_v01(sibling_runtime_projection)['payload'], {'projection_profile_id': 'g2e_baseline_runtime_artifact_projection_v01', 'projected_runtime_artifact': sibling_runtime_plain, 'projected_runtime_artifact_sha256': sibling_runtime_sha256}, 'row105_sibling_runtime_projection_payload')
    target_runtime_matches = tuple((item for item in supplier_bundle.queue_artifacts if canonical_json_bytes_v01(abi.kernel_artifact_to_plain_dict_v01(item)) == canonical_json_bytes_v01(target_runtime_plain)))
    sibling_runtime_matches = tuple((item for item in supplier_bundle.queue_artifacts if canonical_json_bytes_v01(abi.kernel_artifact_to_plain_dict_v01(item)) == canonical_json_bytes_v01(sibling_runtime_plain)))
    assert_equal(target_runtime_matches, (target_initial_artifact,), 'row105_target_runtime_oracle_unique')
    assert_equal(sibling_runtime_matches, (sibling_initial_artifact,), 'row105_sibling_runtime_oracle_unique')
    assert_equal(target_runtime_projection.artifact_id != sibling_runtime_projection.artifact_id, True, 'row105_runtime_projection_ids_distinct')
    delta_role_bindings['TARGET']['runtime_projection_artifact_id'] = target_runtime_projection.artifact_id
    delta_role_bindings['TARGET']['runtime_projection_sha256'] = target_runtime_sha256
    delta_role_bindings['SIBLING']['runtime_projection_artifact_id'] = sibling_runtime_projection.artifact_id
    delta_role_bindings['SIBLING']['runtime_projection_sha256'] = sibling_runtime_sha256
    scenario_dependency_relation = ((target_runtime_projection.artifact_id, baseline_source.artifact_id, ('/content_sha256',), 'FIELD_CAUSAL'),)
    assert_equal(scenario_dependency_relation[0][0], target_runtime_projection.artifact_id, 'row105_relation_target_frozen')
    assert_equal(scenario_dependency_relation[0][1], baseline_source.artifact_id, 'row105_relation_source_frozen')
    observed_identity_material = {'abi_version': 'v1.0', 'artifact_type': 'SemanticEvidence', 'schema_version': 'v1', 'transaction_id': supplier_transaction_id, 'owner_root_id': supplier_root_id, 'source_component': 'continuous_delta_runtime_g2f', 'authority_class': 'EVIDENCE_ONLY', 'lifecycle_state': 'VALIDATED', 'payload': observed_source_payload, 'trace_refs': list(common_source_trace), 'parent_refs': [baseline_source.artifact_id], 'time_envelope': g2e_time_envelope}
    assert_equal('artifact_id' in observed_identity_material, False, 'row105_observed_preimage_no_id')
    observed_source_id = 'g2fv11_dependency_source_observed_v01:' + hashlib.sha256(('HEDGEHOG_G2F_V11_SUPPLIER_DEPENDENCY_SOURCE_OBSERVED_V01' + '\x00').encode('utf-8') + canonical_json_bytes_v01(observed_identity_material)).hexdigest()
    observed_source = abi.build_kernel_artifact_v01(abi_version='v1.0', artifact_id=observed_source_id, artifact_type='SemanticEvidence', schema_version='v1', transaction_id=supplier_transaction_id, owner_root_id=supplier_root_id, source_component='continuous_delta_runtime_g2f', authority_class='EVIDENCE_ONLY', lifecycle_state='VALIDATED', payload=observed_source_payload, trace_refs=common_source_trace, parent_refs=(baseline_source.artifact_id,), time_envelope=g2e_time_envelope)
    assert_equal(record_validation(105, abi.validate_kernel_artifact_v01, abi.validate_kernel_artifact_v01(observed_source), ()), (), 'row105_observed_source')
    assert_equal(record_validation(105, abi.validate_kernel_artifact_bundle_v01, abi.validate_kernel_artifact_bundle_v01(artifacts=(baseline_source, observed_source)), ()), (), 'row105_source_pair_parent_closed')
    rejected_v10_source_ids = {'artifact:g2f:g2e:source:baseline:90a7aa28cd4af65cf34ede84fc5d967ea8f88814705e63ac57f264969c90d6ec', 'artifact:g2f:g2e:source:observed:90a7aa28cd4af65cf34ede84fc5d967ea8f88814705e63ac57f264969c90d6ec'}
    assert_equal(len({baseline_source.artifact_id, observed_source.artifact_id}), 2, 'row105_v11_source_ids_distinct')
    assert_equal(bool({baseline_source.artifact_id, observed_source.artifact_id} & rejected_v10_source_ids), False, 'row105_v11_source_ids_disjoint_v10')
    baseline_source_plain = abi.kernel_artifact_to_plain_dict_v01(baseline_source)
    observed_source_plain = abi.kernel_artifact_to_plain_dict_v01(observed_source)
    full_artifact_raw_differences = plain_difference_rows(baseline_source_plain, observed_source_plain)
    assert_equal(tuple((row['pointer'] for row in full_artifact_raw_differences)), ('/artifact_id', '/parent_refs/0', '/payload/content_sha256'), 'row105_full_artifact_diff_inventory')
    full_artifact_changed_pointer_ledger = tuple(({**row, 'classification': 'AUTHORITATIVE_FACT' if row['pointer'] == '/payload/content_sha256' else 'DERIVED_CONSEQUENCE', 'producer': 'typed_source_projection' if row['pointer'] == '/payload/content_sha256' else 'deterministic_identity_or_predecessor_law', 'causal_parent': rows[104]['supplier'].invalidation_evidence_id if row['pointer'] == '/payload/content_sha256' else baseline_source.artifact_id} for row in full_artifact_raw_differences))
    assert_equal(tuple((row['pointer'] for row in full_artifact_changed_pointer_ledger if row['classification'] == 'AUTHORITATIVE_FACT')), ('/payload/content_sha256',), 'row105_authoritative_full_pointer')
    baseline_artifacts = (baseline_source, target_runtime_projection, sibling_runtime_projection)
    observed_artifacts = (observed_source, target_runtime_projection, sibling_runtime_projection)
    rows[105]['supplier'] = (baseline_artifacts, observed_artifacts)
    for artifact in (*baseline_artifacts, observed_source):
        assert_equal(record_validation(105, abi.validate_kernel_artifact_v01, abi.validate_kernel_artifact_v01(artifact), ()), (), 'row105_artifact_' + artifact.artifact_id)
    available_artifacts: dict[str, object] = {}
    runtime_artifacts = (supplier_bundle.source_context.proposal_artifact, supplier_bundle.source_context.decision_artifact, supplier_bundle.source_context.route_eligibility_artifact, supplier_bundle.topology_artifact, *supplier_bundle.queue_artifacts, *supplier_bundle.result_artifacts, supplier_bundle.report_artifact)
    for value in runtime_artifacts:
        prior = available_artifacts.get(value.artifact_id)
        if prior is not None:
            assert_equal(abi.kernel_artifact_to_plain_dict_v01(prior), abi.kernel_artifact_to_plain_dict_v01(value), 'row105_duplicate_baseline_artifact')
        available_artifacts[value.artifact_id] = value
    available_artifacts[baseline_source.artifact_id] = baseline_source
    available_artifacts[observed_source.artifact_id] = observed_source
    available_artifacts[target_runtime_projection.artifact_id] = target_runtime_projection
    available_artifacts[sibling_runtime_projection.artifact_id] = sibling_runtime_projection
    required_ids = {baseline_source.artifact_id, observed_source.artifact_id, target_runtime_projection.artifact_id, sibling_runtime_projection.artifact_id, target_initial_artifact.artifact_id, sibling_initial_artifact.artifact_id}
    closure_frontier = list(required_ids)
    while closure_frontier:
        child_id = closure_frontier.pop()
        child = available_artifacts.get(child_id)
        if type(child) is not abi.KernelArtifactV01:
            raise RuntimeError('row105_parent_closure_missing:' + child_id)
        for parent_id in child.parent_refs:
            if parent_id not in available_artifacts:
                raise RuntimeError('row105_parent_closure_missing:' + parent_id)
            if parent_id not in required_ids:
                required_ids.add(parent_id)
                closure_frontier.append(parent_id)
    remaining_ids = set(required_ids)
    ordered_parent_closure = []
    while remaining_ids:
        ready_ids = sorted((artifact_id for artifact_id in remaining_ids if set(available_artifacts[artifact_id].parent_refs).isdisjoint(remaining_ids)), key=lambda item: item.encode('utf-8'))
        if not ready_ids:
            raise RuntimeError('row105_parent_closure_cycle')
        for artifact_id in ready_ids:
            ordered_parent_closure.append(available_artifacts[artifact_id])
            remaining_ids.remove(artifact_id)
    abi_parent_closed_union = tuple(ordered_parent_closure)
    assert_equal(record_validation(105, abi.validate_kernel_artifact_bundle_v01, abi.validate_kernel_artifact_bundle_v01(artifacts=abi_parent_closed_union), ()), (), 'row105_parent_closed_union')
    assert_equal(all((item.transaction_id == supplier_transaction_id and item.owner_root_id == supplier_root_id for item in abi_parent_closed_union)), True, 'row105_parent_closed_supplier_local')
    emit_receipt(105, 1, 'supplier', abi.build_kernel_artifact_v01, rows[105]['supplier'], input_bindings=())
    manifest_edges = tuple((integrity_replay.ArtifactDependencyEdgeV01(artifact_id=dependent, depends_on_artifact_id=dependency) for dependent, dependency, _pointers, _edge_class in scenario_dependency_relation))
    rows[106]['supplier'] = integrity_replay.build_artifact_manifest_v01(transaction_id=supplier_transaction_id, profile=integrity_replay.build_default_seal_profile_v01(), artifacts=tuple((abi.kernel_artifact_to_canonical_ref_v01(item) for item in baseline_artifacts)), dependency_edges=manifest_edges, root_ownership_bindings=tuple((integrity_replay.RootOwnershipBindingV01(item.artifact_id, supplier_root_id) for item in baseline_artifacts)), evidence_class_bindings=tuple((integrity_replay.EvidenceClassBindingV01(item.artifact_id, 'SOURCE_EVIDENCE') for item in baseline_artifacts)), authority_class_bindings=tuple((integrity_replay.AuthorityClassBindingV01(item.artifact_id, item.authority_class) for item in baseline_artifacts)))
    payload_rows = tuple(((item.artifact_id, abi.kernel_artifact_to_plain_dict_v01(item)['payload']) for item in baseline_artifacts))
    manifest_verification = record_validation(106, integrity_replay.verify_artifact_manifest_v01, integrity_replay.verify_artifact_manifest_v01(manifest=rows[106]['supplier'], payload_rows=payload_rows, expected_manifest_hash=rows[106]['supplier'].manifest_hash), ((106, rows[106]['supplier'].manifest_hash), (106, rows[106]['supplier'])))
    (manifest_verification.verification_status, manifest_verification.verification_errors)
    assert_equal(len(rows[106]['supplier'].artifacts), 3, 'row106_artifact_count')
    assert_equal(tuple(sorted({item.schema_version for item in rows[106]['supplier'].artifacts})), ('v1',), 'row106_schema_set')
    assert_equal(len(rows[106]['supplier'].dependency_edges), 1, 'row106_edge_count')
    assert_equal(bool({target_initial_artifact.artifact_id, sibling_initial_artifact.artifact_id} & {item.artifact_id for item in rows[106]['supplier'].artifacts}), False, 'row106_no_raw_queue_nodes')
    emit_receipt(106, 1, 'supplier', integrity_replay.build_artifact_manifest_v01, rows[106]['supplier'], input_bindings=())
    rows[107]['supplier'] = record_validation(107, integrity_replay.verify_artifact_replay_v01, integrity_replay.verify_artifact_replay_v01(manifest=rows[106]['supplier'], payload_rows=payload_rows, expected_manifest_hash=rows[106]['supplier'].manifest_hash), ((106, rows[106]['supplier'].manifest_hash), (106, rows[106]['supplier'])))
    (rows[107]['supplier'].replay_status, rows[107]['supplier'].replay_errors)
    assert_equal(rows[107]['supplier'].reconstructed_dependency_edges, manifest_edges, 'row107_relation_reconstructed')
    emit_receipt(107, 1, 'supplier', integrity_replay.verify_artifact_replay_v01, rows[107]['supplier'], input_bindings=())
    query = rows[23]['supplier'].query
    policy_version = query.policy_version
    schema_versions = query.schema_versions
    source_history_hash = rows[23]['supplier'].query_evaluations[0].source_history_hash
    edge_projection_bindings = scenario_dependency_relation
    rows[108]['supplier'] = continuous_delta.project_integrity_replay_dependency_edges_v01(manifest=rows[106]['supplier'], replay=rows[107]['supplier'], source_artifacts=baseline_artifacts, graph_version=continuous_delta.CONTINUOUS_DELTA_GRAPH_VERSION_V01, transaction_id=supplier_transaction_id, owning_root_id=supplier_root_id, domain_id=rows[42]['supplier'].domain_id, policy_version=policy_version, schema_versions=schema_versions, source_history_hash=source_history_hash, edge_projection_bindings=edge_projection_bindings)
    graph_basis_sha256, dependency_edges = rows[108]['supplier']
    for edge in dependency_edges:
        report = record_validation(108, continuous_delta.validate_delta_dependency_edge_v01, continuous_delta.validate_delta_dependency_edge_v01(edge), ())
        (report.status, report.reason_codes)
    manifest_pairs = tuple(((item.artifact_id, item.depends_on_artifact_id) for item in manifest_edges))
    projected_pairs = tuple(((item.dependent_artifact_id, item.dependency_artifact_id) for item in dependency_edges))
    assert_equal(projected_pairs, manifest_pairs, 'row108_projection_pair_equivalence')
    assert_equal(len(dependency_edges), len(scenario_dependency_relation), 'row108_edge_count')
    emit_receipt(108, 1, 'supplier', continuous_delta.project_integrity_replay_dependency_edges_v01, rows[108]['supplier'], input_bindings=())
    rows[109]['supplier'] = continuous_delta.build_dependency_graph_index_v01(graph_basis_sha256=graph_basis_sha256, graph_version=continuous_delta.CONTINUOUS_DELTA_GRAPH_VERSION_V01, manifest=rows[106]['supplier'], replay=rows[107]['supplier'], source_artifacts=baseline_artifacts, dependency_edges=dependency_edges, transaction_id=supplier_transaction_id, owning_root_id=supplier_root_id, domain_id=rows[42]['supplier'].domain_id, policy_version=policy_version, schema_versions=schema_versions, source_history_hash=source_history_hash, trace_refs=('trace:g2f:g2e:dependency-graph',))
    graph_report = record_validation(109, continuous_delta.validate_dependency_graph_index_v01, continuous_delta.validate_dependency_graph_index_v01(rows[109]['supplier']), ((109, rows[109]['supplier']),))
    (graph_report.status, graph_report.reason_codes)
    assert_equal(rows[109]['supplier'].ordered_node_ids, tuple((item.artifact_id for item in baseline_artifacts)), 'row109_exact_manifest_order')
    emit_receipt(109, 1, 'supplier', continuous_delta.build_dependency_graph_index_v01, rows[109]['supplier'], input_bindings=())
    rows[110]['supplier'] = continuous_delta.build_dependency_fingerprint_profile_v01()
    fingerprint_report = record_validation(110, continuous_delta.validate_dependency_fingerprint_profile_v01, continuous_delta.validate_dependency_fingerprint_profile_v01(rows[110]['supplier']), ((110, rows[110]['supplier']),))
    (fingerprint_report.status, fingerprint_report.reason_codes)
    emit_receipt(110, 1, 'supplier', continuous_delta.build_dependency_fingerprint_profile_v01, rows[110]['supplier'], input_bindings=())
    dependency_fingerprint_before = continuous_delta.build_dependency_fingerprint_v01(profile=rows[110]['supplier'], graph=rows[109]['supplier'], dependency_edges=dependency_edges, source_artifacts=baseline_artifacts, policy_version=policy_version, schema_versions=schema_versions, source_history_hash=source_history_hash)
    dependency_fingerprint_after = continuous_delta.build_dependency_fingerprint_v01(profile=rows[110]['supplier'], graph=rows[109]['supplier'], dependency_edges=dependency_edges, source_artifacts=observed_artifacts, policy_version=policy_version, schema_versions=schema_versions, source_history_hash=source_history_hash)
    rows[111]['supplier'] = (dependency_fingerprint_before, dependency_fingerprint_after)
    if dependency_fingerprint_before == dependency_fingerprint_after:
        raise RuntimeError('row111_fingerprint_change_missing')
    emit_receipt(111, 1, 'supplier', continuous_delta.build_dependency_fingerprint_v01, rows[111]['supplier'], input_bindings=())
    baseline_artifact_sha256 = plain_sha256(baseline_source_plain)
    observed_artifact_sha256 = plain_sha256(observed_source_plain)
    baseline_payload_sha256 = plain_sha256(baseline_source_plain['payload'])
    observed_payload_sha256 = plain_sha256(observed_source_plain['payload'])
    rows[112]['supplier'] = continuous_delta.build_delta_source_binding_v01(request_id=supplier_bundle.runtime_report.request_id, transaction_id=supplier_transaction_id, owning_root_id=supplier_root_id, domain_id=rows[42]['supplier'].domain_id, baseline_source_artifact_id=baseline_source.artifact_id, baseline_source_artifact_type=baseline_source.artifact_type, baseline_source_artifact_sha256=baseline_artifact_sha256, baseline_source_payload_sha256=baseline_payload_sha256, observed_source_artifact_id=observed_source.artifact_id, observed_source_artifact_type=observed_source.artifact_type, observed_source_artifact_sha256=observed_artifact_sha256, observed_source_payload_sha256=observed_payload_sha256, baseline_report_id=supplier_bundle.runtime_report.report_id, baseline_graph_id=rows[109]['supplier'].graph_id, baseline_graph_version=rows[109]['supplier'].graph_version, baseline_policy_version=policy_version, observed_policy_version=policy_version, baseline_schema_versions=schema_versions, observed_schema_versions=schema_versions, baseline_source_history_hash=source_history_hash, observed_source_history_hash=source_history_hash, valid_from_utc=EVALUATION_UTC, valid_to_utc=VALID_TO_UTC, trace_refs=('trace:g2f:g2e:source-binding',))
    source_binding_report = record_validation(112, continuous_delta.validate_delta_source_binding_v01, continuous_delta.validate_delta_source_binding_v01(rows[112]['supplier']), ((112, rows[112]['supplier']),))
    (source_binding_report.status, source_binding_report.reason_codes)
    emit_receipt(112, 1, 'supplier', continuous_delta.build_delta_source_binding_v01, rows[112]['supplier'], input_bindings=())
    rows[113]['supplier'] = continuous_delta.build_changed_field_binding_v01(source_binding_id=rows[112]['supplier'].source_binding_id, json_pointer='/payload/content_sha256', prior_value_sha256=plain_sha256(rows[72]['supplier'].content_sha256), observed_value_sha256=plain_sha256(rows[104]['supplier'].evidence_sha256), change_class='FIELD_VALUE_CHANGE', observed_at_utc=EVALUATION_UTC, trace_refs=(rows[112]['supplier'].source_binding_id,))
    changed_field_report = record_validation(113, continuous_delta.validate_changed_field_binding_v01, continuous_delta.validate_changed_field_binding_v01(rows[113]['supplier']), ((113, rows[113]['supplier']),))
    (changed_field_report.status, changed_field_report.reason_codes)
    assert_equal(rows[113]['supplier'].json_pointer, '/payload/content_sha256', 'row113_full_artifact_pointer')
    emit_receipt(113, 1, 'supplier', continuous_delta.build_changed_field_binding_v01, rows[113]['supplier'], input_bindings=())
    rows[114]['supplier'] = continuous_delta.build_changed_artifact_binding_v01(source_binding_id=rows[112]['supplier'].source_binding_id, baseline_artifact_id=baseline_source.artifact_id, baseline_artifact_type=baseline_source.artifact_type, baseline_payload_sha256=baseline_payload_sha256, observed_artifact_id=observed_source.artifact_id, observed_artifact_type=observed_source.artifact_type, observed_payload_sha256=observed_payload_sha256, baseline_dependency_fingerprint=dependency_fingerprint_before, observed_dependency_fingerprint=dependency_fingerprint_after, change_class='ARTIFACT_SUCCESSOR', observed_at_utc=EVALUATION_UTC, trace_refs=(rows[112]['supplier'].source_binding_id,))
    changed_artifact_report = record_validation(114, continuous_delta.validate_changed_artifact_binding_v01, continuous_delta.validate_changed_artifact_binding_v01(rows[114]['supplier']), ((114, rows[114]['supplier']),))
    (changed_artifact_report.status, changed_artifact_report.reason_codes)
    emit_receipt(114, 1, 'supplier', continuous_delta.build_changed_artifact_binding_v01, rows[114]['supplier'], input_bindings=())
    rows[115]['supplier'] = continuous_delta.build_world_state_delta_v01(ordered_source_binding_ids=(rows[112]['supplier'].source_binding_id,), request_id=rows[112]['supplier'].request_id, transaction_id=supplier_transaction_id, owning_root_id=supplier_root_id, domain_id=rows[42]['supplier'].domain_id, baseline_report_id=supplier_bundle.runtime_report.report_id, baseline_graph_id=rows[109]['supplier'].graph_id, baseline_graph_version=rows[109]['supplier'].graph_version, observed_at_utc=EVALUATION_UTC, valid_from_utc=EVALUATION_UTC, valid_to_utc=VALID_TO_UTC, baseline_policy_version=policy_version, observed_policy_version=policy_version, baseline_schema_versions=schema_versions, observed_schema_versions=schema_versions, baseline_source_history_hash=source_history_hash, observed_source_history_hash=source_history_hash, ordered_changed_field_binding_ids=(rows[113]['supplier'].changed_field_binding_id,), ordered_changed_artifact_binding_ids=(rows[114]['supplier'].changed_artifact_binding_id,), dependency_fingerprint_before=dependency_fingerprint_before, dependency_fingerprint_after=dependency_fingerprint_after, trace_refs=('trace:g2f:g2e:delta',))
    delta_report = record_validation(115, continuous_delta.validate_world_state_delta_v01, continuous_delta.validate_world_state_delta_v01(rows[115]['supplier']), ((115, rows[115]['supplier']),))
    (delta_report.status, delta_report.reason_codes)
    emit_receipt(115, 1, 'supplier', continuous_delta.build_world_state_delta_v01, rows[115]['supplier'], input_bindings=())
    rows[116]['supplier'] = continuous_delta.build_affected_set_request_v01(delta=rows[115]['supplier'], graph=rows[109]['supplier'], trace_refs=(rows[115]['supplier'].delta_id, rows[109]['supplier'].graph_id))
    request_report = record_validation(116, continuous_delta.validate_affected_set_request_v01, continuous_delta.validate_affected_set_request_v01(rows[116]['supplier']), ((116, rows[116]['supplier']),))
    (request_report.status, request_report.reason_codes)
    emit_receipt(116, 1, 'supplier', continuous_delta.build_affected_set_request_v01, rows[116]['supplier'], input_bindings=())
    independent_partitions = independently_derive_partitions(tuple((item.artifact_id for item in baseline_artifacts)), scenario_dependency_relation, (baseline_source.artifact_id,))
    assert_equal(independent_partitions['direct'], (target_runtime_projection.artifact_id,), 'row117_independent_target_direct')
    assert_equal(independent_partitions['transitive'], (), 'row117_independent_no_transitive')
    assert_equal(independent_partitions['unaffected'], (sibling_runtime_projection.artifact_id,), 'row117_independent_sibling_unaffected')
    rows[117]['supplier'] = continuous_delta.compute_affected_set_v01(request=rows[116]['supplier'], delta=rows[115]['supplier'], graph=rows[109]['supplier'], source_bindings=(rows[112]['supplier'],), changed_field_bindings=(rows[113]['supplier'],), changed_artifact_bindings=(rows[114]['supplier'],), dependency_edges=dependency_edges, baseline_source_artifacts=baseline_artifacts, observed_source_artifacts=observed_artifacts)
    affected_structural = record_validation(117, continuous_delta.validate_affected_set_result_v01, continuous_delta.validate_affected_set_result_v01(rows[117]['supplier']), ((117, rows[117]['supplier']),))
    (affected_structural.status, affected_structural.reason_codes)
    affected_context = record_validation(117, continuous_delta.validate_affected_set_against_graph_v01, continuous_delta.validate_affected_set_against_graph_v01(rows[117]['supplier'], request=rows[116]['supplier'], delta=rows[115]['supplier'], graph=rows[109]['supplier'], source_bindings=(rows[112]['supplier'],), changed_field_bindings=(rows[113]['supplier'],), changed_artifact_bindings=(rows[114]['supplier'],), dependency_edges=dependency_edges, baseline_source_artifacts=baseline_artifacts, observed_source_artifacts=observed_artifacts), ((109, rows[109]['supplier']), (112, rows[112]['supplier']), (113, rows[113]['supplier']), (114, rows[114]['supplier']), (115, rows[115]['supplier']), (116, rows[116]['supplier']), (117, rows[117]['supplier'])))
    (affected_context.status, affected_context.reason_codes)
    assert_equal(rows[117]['supplier'].ordered_changed_node_ids, independent_partitions['changed'], 'row117_changed_partition')
    assert_equal(rows[117]['supplier'].ordered_directly_affected_ids, independent_partitions['direct'], 'row117_direct_partition')
    assert_equal(rows[117]['supplier'].ordered_transitively_affected_ids, independent_partitions['transitive'], 'row117_transitive_partition')
    assert_equal(rows[117]['supplier'].ordered_affected_ids, independent_partitions['affected'], 'row117_affected_partition')
    assert_equal(rows[117]['supplier'].ordered_unaffected_ids, independent_partitions['unaffected'], 'row117_unaffected_partition')
    partition_sets = tuple((set(values) for values in (independent_partitions['changed'], independent_partitions['direct'], independent_partitions['transitive'], independent_partitions['unaffected'])))
    assert_equal(all((not left & right for index, left in enumerate(partition_sets) for right in partition_sets[index + 1:])), True, 'row117_partitions_disjoint')
    assert_equal(set(independent_partitions['changed']) | set(independent_partitions['affected']) | set(independent_partitions['unaffected']), set(rows[109]['supplier'].ordered_node_ids), 'row117_partition_complete')
    assert_equal(baseline_source.artifact_id in rows[117]['supplier'].ordered_affected_ids, False, 'row117_changed_source_not_affected')
    assert_equal((rows[117]['supplier'].complete, rows[117]['supplier'].minimal), (True, True), 'row117_complete_minimal')
    emit_receipt(117, 1, 'supplier', continuous_delta.compute_affected_set_v01, rows[117]['supplier'], input_bindings=())
    rows[118]['supplier'] = continuous_delta.build_continuous_delta_source_context_v01(integrity_manifest=rows[106]['supplier'], integrity_replay=rows[107]['supplier'], baseline_source_artifacts=baseline_artifacts, observed_source_artifacts=observed_artifacts, g2a_registry=rows[98]['supplier'], g2a_packet=rows[84]['supplier'], g2a_dependency_candidate=rows[73]['supplier'], g2a_current_observations=(rows[101]['supplier'],), g2a_root_invalidation_material=rows[104]['supplier'], g2b_resolution_report=rows[23]['supplier'], g2b_reuse_certificate=rows[22]['supplier'], g2b_writeback_evidence=None, g2c_source_context=rows[43]['supplier'], baseline_g2c_route_eligibility_artifact=rows[60]['supplier'], baseline_g2d_execution_bundle=supplier_bundle, root_kernel=rows[12]['supplier'], post_vv_profile=None, gt_profile=None)
    source_context_report = record_validation(118, continuous_delta.validate_continuous_delta_source_context_v01, continuous_delta.validate_continuous_delta_source_context_v01(rows[118]['supplier']), ((118, rows[118]['supplier']),))
    (source_context_report.status, source_context_report.reason_codes)
    assert_equal((rows[118]['supplier'].g2b_writeback_evidence, rows[118]['supplier'].post_vv_profile, rows[118]['supplier'].gt_profile), (None, None, None), 'row118_absence_sentinels')
    emit_receipt(118, 1, 'supplier', continuous_delta.build_continuous_delta_source_context_v01, rows[118]['supplier'], input_bindings=())
    rows[119]['supplier'] = continuous_delta.derive_invalidation_report_v01(affected_set=rows[117]['supplier'], delta=rows[115]['supplier'], source_context=rows[118]['supplier'], source_bindings=(rows[112]['supplier'],), changed_field_bindings=(rows[113]['supplier'],), changed_artifact_bindings=(rows[114]['supplier'],), dependency_edges=dependency_edges, dependency_graph=rows[109]['supplier'])
    invalidation_records, invalidation_report = rows[119]['supplier']
    assert_equal(tuple((item.artifact_id for item in invalidation_records)), (target_runtime_projection.artifact_id,), 'row119_exact_target_invalidation')
    for record in invalidation_records:
        report = record_validation(119, continuous_delta.validate_artifact_invalidation_record_v01, continuous_delta.validate_artifact_invalidation_record_v01(record), ())
        (report.status, report.reason_codes)
    report = record_validation(119, continuous_delta.validate_invalidation_report_v01, continuous_delta.validate_invalidation_report_v01(invalidation_report), ())
    (report.status, report.reason_codes)
    report = record_validation(119, continuous_delta.validate_invalidation_report_against_sources_v01, continuous_delta.validate_invalidation_report_against_sources_v01(invalidation_report, records=invalidation_records, affected_set=rows[117]['supplier'], delta=rows[115]['supplier'], source_context=rows[118]['supplier'], source_bindings=(rows[112]['supplier'],), changed_field_bindings=(rows[113]['supplier'],), changed_artifact_bindings=(rows[114]['supplier'],), dependency_edges=dependency_edges, dependency_graph=rows[109]['supplier']), ((109, rows[109]['supplier']), (112, rows[112]['supplier']), (113, rows[113]['supplier']), (114, rows[114]['supplier']), (115, rows[115]['supplier']), (117, rows[117]['supplier']), (118, rows[118]['supplier'])))
    (report.status, report.reason_codes)
    emit_receipt(119, 1, 'supplier', continuous_delta.derive_invalidation_report_v01, rows[119]['supplier'], input_bindings=())
    rows[120]['supplier'] = continuous_delta.run_continuous_delta_runtime_v01(source_context=rows[118]['supplier'], source_bindings=(rows[112]['supplier'],), changed_field_bindings=(rows[113]['supplier'],), changed_artifact_bindings=(rows[114]['supplier'],), delta=rows[115]['supplier'], dependency_edges=dependency_edges, dependency_graph=rows[109]['supplier'])
    delta_bundle, delta_runtime_report = rows[120]['supplier']
    if delta_bundle is None:
        raise RuntimeError('row120_bundle_missing:' + repr(delta_runtime_report))
    (delta_runtime_report.status, delta_runtime_report.reason_codes)
    report = record_validation(120, continuous_delta.validate_continuous_delta_execution_bundle_v01, continuous_delta.validate_continuous_delta_execution_bundle_v01(delta_bundle), ())
    (report.status, report.reason_codes)
    report = record_validation(120, continuous_delta.validate_preservation_proof_v01, continuous_delta.validate_preservation_proof_v01(delta_bundle.preservation_proof), ())
    (report.status, report.reason_codes)
    report = record_validation(120, continuous_delta.validate_selective_recomputation_result_v01, continuous_delta.validate_selective_recomputation_result_v01(delta_bundle.recomputation_result), ())
    (report.status, report.reason_codes)
    report = record_validation(120, continuous_delta.validate_continuous_delta_runtime_report_v01, continuous_delta.validate_continuous_delta_runtime_report_v01(delta_bundle.runtime_report), ())
    (report.status, report.reason_codes)
    assert_equal(delta_bundle.affected_request, rows[116]['supplier'], 'row120_request_binding')
    assert_equal(delta_bundle.affected_result, rows[117]['supplier'], 'row120_affected_binding')
    assert_equal(delta_bundle.invalidation_records, invalidation_records, 'row120_records_binding')
    assert_equal(delta_bundle.invalidation_report, invalidation_report, 'row120_invalidation_binding')
    assert_equal(delta_bundle.recomputation_plan.ordered_affected_artifact_ids, (target_runtime_projection.artifact_id,), 'row120_plan_target_artifact')
    assert_equal(delta_bundle.recomputation_plan.ordered_affected_cell_ids, (target_child_input.cell_id,), 'row120_plan_target_cell')
    assert_equal(target_runtime_matches, (target_initial_artifact,), 'row120_target_projection_exact_runtime_resolution_oracle')
    assert_equal(sibling_runtime_projection.artifact_id in delta_bundle.recomputation_plan.ordered_affected_artifact_ids, False, 'row120_sibling_projection_not_admitted')
    for recomputed_binding in delta_bundle.recomputed_bindings:
        report = record_validation(120, continuous_delta.validate_recomputed_artifact_binding_v01, continuous_delta.validate_recomputed_artifact_binding_v01(recomputed_binding), ())
        (report.status, report.reason_codes)
    recomputed_bundle = delta_bundle.recomputed_g2d_execution_bundle
    report = record_validation(120, fractal_runtime.validate_fractal_runtime_execution_bundle_v02, fractal_runtime.validate_fractal_runtime_execution_bundle_v02(recomputed_bundle), ())
    (report.status, report.reason_codes)
    observed_work_context = recomputed_bundle.observed_work_context
    if type(observed_work_context) is not fractal_runtime.RuntimeObservedWorkContextV02:
        raise RuntimeError('row120_observed_work_context_missing')
    report = record_validation(120, fractal_runtime.validate_runtime_observed_work_context_v02, fractal_runtime.validate_runtime_observed_work_context_v02(observed_work_context), ())
    (report.status, report.reason_codes)
    report = record_validation(120, fractal_runtime.validate_runtime_observed_work_context_against_sources_v02, fractal_runtime.validate_runtime_observed_work_context_against_sources_v02(observed_work_context, baseline_execution_bundle=supplier_bundle, direct_source_artifacts=(baseline_source, observed_source), supporting_artifacts=(), binding_artifacts=observed_work_context.ordered_binding_artifacts), ())
    (report.status, report.reason_codes)
    assert_equal(observed_work_context.ordered_affected_cell_ids, (target_child_input.cell_id,), 'row120_context_target_cell')
    assert_equal(sibling_child_input.cell_id in observed_work_context.ordered_affected_cell_ids, False, 'row120_no_sibling_admission')
    assert_equal(any((item.prior_artifact_id == sibling_initial_artifact.artifact_id or item.new_artifact_id == sibling_initial_artifact.artifact_id for item in delta_bundle.recomputed_bindings)), False, 'row120_no_sibling_recomputed_binding')
    assert_equal(len(observed_work_context.ordered_binding_artifacts), 1, 'row120_one_observed_binding')
    selected_observed_binding = observed_work_context.ordered_binding_artifacts[0]
    selected_binding_payload = abi.kernel_artifact_to_plain_dict_v01(selected_observed_binding)['payload']
    source_pair = selected_binding_payload['source_pair']
    topology_binding = selected_binding_payload['topology_binding']
    change_proof = selected_binding_payload['change_proof']
    assert_equal((source_pair['baseline_identity_ref'], source_pair['observed_identity_ref']), (baseline_source.artifact_id, observed_source.artifact_id), 'row120_binding_source_pair')
    assert_equal((topology_binding['cell_ref'], topology_binding['node_ref'], topology_binding['baseline_cell_input_ref'], topology_binding['canonical_child_index']), (target_child_input.cell_id, target_node.node_id, target_child_input.cell_input_id, 1), 'row120_binding_target_geometry')
    assert_equal(tuple(change_proof['all_full_artifact_changed_pointers']), ('/payload/content_sha256',), 'row120_binding_pointer_set')
    assert_equal((change_proof['whole_artifact_expanded'], change_proof['whole_payload_expanded']), (False, False), 'row120_binding_expansion_flags')
    consumed_rows = change_proof['consumed_changed_material_rows']
    assert_equal(len(consumed_rows), 1, 'row120_one_consumed_material_row')
    assert_equal((consumed_rows[0]['full_artifact_pointer'], consumed_rows[0]['payload_pointer']), ('/payload/content_sha256', '/content_sha256'), 'row120_consumed_pointer_domains')
    matching_consumed_rows = tuple(((index, row) for index, row in enumerate(consumed_rows) if row['full_artifact_pointer'] == '/payload/content_sha256' and row['payload_pointer'] == '/content_sha256'))
    assert_equal(len(matching_consumed_rows), 1, 'row120_consumed_row_index_unique')
    canonical_consumed_index = matching_consumed_rows[0][0]
    expected_output_field = '/change_proof/consumed_changed_material_rows/' + str(canonical_consumed_index) + '/observed_value_sha256'
    observed_work_used_refs = tuple((item for item in recomputed_bundle.causal_consumption_refs if item.source_artifact_id == selected_observed_binding.artifact_id and item.decision_effect == 'OBSERVED_WORK_INPUT' and (item.disposition == 'USED') and (item.reason_code == 'used:g2d_observed_work_input') and (item.output_field == expected_output_field)))
    assert_equal(len(observed_work_used_refs), 1, 'row120_used_causal_row_unique')
    observed_work_used_ref = observed_work_used_refs[0]
    assert_equal(record_validation(120, abi.validate_causal_consumption_ref_v01, abi.validate_causal_consumption_ref_v01(observed_work_used_ref), ()), (), 'row120_used_causal_ref')
    observed_work_used_ref_plain = abi.causal_consumption_ref_to_plain_dict_v01(observed_work_used_ref)
    observed_work_used_ref_plain_sha256 = plain_sha256(observed_work_used_ref_plain)
    causal_ref_public_identity_member_present = 'causal_ref_id' in observed_work_used_ref_plain
    assert_equal(causal_ref_public_identity_member_present, False, 'row120_causal_ref_has_no_public_identity_member')
    recomputed_initial_entries = tuple((item for item in recomputed_bundle.queue_entries if item.predecessor_queue_entry_id is None and item.cell_id == target_child_input.cell_id and (item.node_id == target_node.node_id)))
    assert_equal(len(recomputed_initial_entries), 1, 'row120_recomputed_initial_entry_unique')
    recomputed_initial_entry = recomputed_initial_entries[0]
    recomputed_initial_artifacts = tuple((item for item in recomputed_bundle.queue_artifacts if abi.kernel_artifact_to_plain_dict_v01(item)['payload']['queue_entry_id'] == recomputed_initial_entry.queue_entry_id))
    assert_equal(len(recomputed_initial_artifacts), 1, 'row120_recomputed_initial_artifact_unique')
    recomputed_initial_artifact = recomputed_initial_artifacts[0]
    assert_equal(recomputed_initial_artifact.source_component, 'fractal_scheduler_v02', 'row120_recomputed_initial_source_component')
    assert_equal(tuple(observed_work_used_ref_plain.keys()), ('producer_actor_id', 'source_artifact_id', 'output_field', 'consumer_component', 'downstream_artifact_id', 'decision_effect', 'disposition', 'reason_code', 'trace_refs'), 'row120_causal_ref_public_plain_key_order')
    assert_equal(observed_work_used_ref_plain, {'producer_actor_id': 'fractal_runtime_v02', 'source_artifact_id': selected_observed_binding.artifact_id, 'output_field': expected_output_field, 'consumer_component': 'fractal_scheduler_v02', 'downstream_artifact_id': recomputed_initial_artifact.artifact_id, 'decision_effect': 'OBSERVED_WORK_INPUT', 'disposition': 'USED', 'reason_code': 'used:g2d_observed_work_input', 'trace_refs': [selected_observed_binding.artifact_id, recomputed_initial_artifact.artifact_id, recomputed_bundle.runtime_trace.trace_id]}, 'row120_causal_ref_public_plain_exact')
    assert_equal(len(observed_work_used_ref_plain_sha256) == 64 and all((character in '0123456789abcdef' for character in observed_work_used_ref_plain_sha256)), True, 'row120_causal_ref_public_plain_sha256_shape')
    assert_equal(observed_work_used_ref.downstream_artifact_id, recomputed_initial_artifact.artifact_id, 'row120_used_ref_downstream')
    assert_equal(selected_observed_binding.artifact_id in recomputed_initial_artifact.parent_refs, True, 'row120_binding_actual_queue_parent')
    assert_equal(target_initial_artifact.artifact_id == recomputed_initial_artifact.artifact_id, False, 'row120_baseline_and_recomputed_queue_roles_distinct')
    counterfactual_dependency_value = 10
    counterfactual_content_sha256 = hashlib.sha256(canonical_json_bytes_v01(counterfactual_dependency_value)).hexdigest()
    counterfactual_source_payload = {'baseline_dependency_time_envelope_id': rows[72]['supplier'].time_envelope_id, 'content_sha256': counterfactual_content_sha256, 'dependency_class': rows[72]['supplier'].dependency_class, 'dependency_id': rows[72]['supplier'].dependency_id, 'evidence_ref': rows[72]['supplier'].evidence_ref, 'expected_accepting_local_root_id': rows[72]['supplier'].expected_accepting_local_root_id, 'freshness_policy_id': rows[72]['supplier'].freshness_policy_id, 'projection_profile_id': 'g2f_supplier_dependency_currentness_projection_v01', 'projection_profile_version': 'v0.1', 'requirement_class': rows[72]['supplier'].requirement_class, 'source_provenance_refs': list(rows[72]['supplier'].source_provenance_refs)}
    counterfactual_identity_material = {'abi_version': 'v1.0', 'artifact_type': 'SemanticEvidence', 'schema_version': 'v1', 'transaction_id': supplier_transaction_id, 'owner_root_id': supplier_root_id, 'source_component': 'continuous_delta_runtime_g2f', 'authority_class': 'EVIDENCE_ONLY', 'lifecycle_state': 'VALIDATED', 'payload': counterfactual_source_payload, 'trace_refs': list(common_source_trace), 'parent_refs': [baseline_source.artifact_id], 'time_envelope': g2e_time_envelope}
    assert_equal('artifact_id' in counterfactual_identity_material, False, 'row120_counterfactual_preimage_no_id')
    counterfactual_source_id = 'g2fv11_dependency_source_counterfactual_v01:' + hashlib.sha256(('HEDGEHOG_G2F_V11_SUPPLIER_DEPENDENCY_SOURCE_COUNTERFACTUAL_V01' + '\x00').encode('utf-8') + canonical_json_bytes_v01(counterfactual_identity_material)).hexdigest()
    counterfactual_source = abi.build_kernel_artifact_v01(abi_version='v1.0', artifact_id=counterfactual_source_id, artifact_type='SemanticEvidence', schema_version='v1', transaction_id=supplier_transaction_id, owner_root_id=supplier_root_id, source_component='continuous_delta_runtime_g2f', authority_class='EVIDENCE_ONLY', lifecycle_state='VALIDATED', payload=counterfactual_source_payload, trace_refs=common_source_trace, parent_refs=(baseline_source.artifact_id,), time_envelope=g2e_time_envelope)
    assert_equal(record_validation(120, abi.validate_kernel_artifact_v01, abi.validate_kernel_artifact_v01(counterfactual_source), ()), (), 'row120_counterfactual_artifact')
    assert_equal(bool({counterfactual_source.artifact_id} & {baseline_source.artifact_id, observed_source.artifact_id, *rejected_v10_source_ids}), False, 'row120_counterfactual_id_disjoint')
    assert_equal(tuple((row['pointer'] for row in plain_difference_rows(observed_source_payload, counterfactual_source_payload))), ('/content_sha256',), 'row120_counterfactual_one_selected_leaf')
    assert_equal(counterfactual_source.artifact_id in tuple((item.artifact_id for item in baseline_artifacts + observed_artifacts)), False, 'row120_counterfactual_primary_source_exclusion')
    assert_equal(counterfactual_source.artifact_id in rows[115]['supplier'].ordered_source_binding_ids, False, 'row120_counterfactual_delta_exclusion')
    counterfactual_report = record_validation(120, fractal_runtime.validate_runtime_observed_work_counterfactual_v02, fractal_runtime.validate_runtime_observed_work_counterfactual_v02(execution_bundle=recomputed_bundle, observed_work_causal_ref=observed_work_used_ref, mutated_observed_source_artifact=counterfactual_source), ())
    (counterfactual_report.status, counterfactual_report.validation_target, counterfactual_report.failure_stage)
    assert_equal(type(counterfactual_report.validated_object_id) is str and counterfactual_report.validated_object_id.startswith('frcounterfactual_v02:'), True, 'row120_counterfactual_identity')
    emit_auxiliary('ROW_120_COUNTERFACTUAL', fractal_runtime.validate_runtime_observed_work_counterfactual_v02, (recomputed_bundle, observed_work_used_ref, counterfactual_source), counterfactual_report, 'ZERO_EFFECT_CAUSAL_COUNTERFACTUAL')
    assert_equal((delta_bundle.runtime_report.authority_created_count, delta_bundle.runtime_report.real_world_effects_count, recomputed_bundle.runtime_report.authority_created_count, recomputed_bundle.runtime_report.real_world_effects_count), (0, 0, 0, 0), 'row120_zero_authority_effects')
    emit_receipt(120, 1, 'supplier', continuous_delta.run_continuous_delta_runtime_v01, rows[120]['supplier'], input_bindings=())
    rows[121]['supplier'] = continuous_delta.prove_unaffected_artifact_preservation_v01(affected_set=rows[117]['supplier'], invalidation_records=invalidation_records, source_context=rows[118]['supplier'], recomputed_g2d_execution_bundle=recomputed_bundle, recomputed_bindings=delta_bundle.recomputed_bindings)
    report = record_validation(121, continuous_delta.validate_preservation_proof_v01, continuous_delta.validate_preservation_proof_v01(rows[121]['supplier']), ((121, rows[121]['supplier']),))
    (report.status, report.reason_codes)
    assert_equal(rows[121]['supplier'], delta_bundle.preservation_proof, 'row121_bundle_binding')
    assert_equal((rows[121]['supplier'].byte_identity_preserved, rows[121]['supplier'].object_identity_used_as_proof), (True, False), 'row121_byte_not_object_identity')
    assert_equal(sibling_runtime_projection.artifact_id in rows[121]['supplier'].ordered_preserved_artifact_ids, True, 'row121_sibling_projection_preserved_id')
    sibling_projection_bytes_preserved = canonical_json_bytes_v01(abi.kernel_artifact_to_plain_dict_v01(baseline_artifacts[2])) == canonical_json_bytes_v01(abi.kernel_artifact_to_plain_dict_v01(observed_artifacts[2]))
    assert_equal(sibling_projection_bytes_preserved, True, 'row121_sibling_projection_bytes_preserved')
    recomputed_sibling_artifacts = tuple((item for item in recomputed_bundle.queue_artifacts if item.artifact_id == sibling_initial_artifact.artifact_id))
    assert_equal(len(recomputed_sibling_artifacts), 1, 'row121_sibling_artifact_unique')
    actual_sibling_queue_bytes_preserved = canonical_json_bytes_v01(abi.kernel_artifact_to_plain_dict_v01(recomputed_sibling_artifacts[0])) == canonical_json_bytes_v01(abi.kernel_artifact_to_plain_dict_v01(sibling_initial_artifact))
    assert_equal(actual_sibling_queue_bytes_preserved, True, 'row121_sibling_bytes_preserved')
    emit_receipt(121, 1, 'supplier', continuous_delta.prove_unaffected_artifact_preservation_v01, rows[121]['supplier'], input_bindings=())
    runtime_report_artifact = delta_bundle.runtime_report_artifact
    runtime_report_artifact_plain = abi.kernel_artifact_to_plain_dict_v01(runtime_report_artifact)
    runtime_report_payload_plain = runtime_report_artifact_plain['payload']
    runtime_report_payload_sha256 = plain_sha256(runtime_report_payload_plain)
    assert_equal(len(runtime_report_payload_sha256) == 64 and runtime_report_payload_sha256 == runtime_report_payload_sha256.lower(), True, 'row122_runtime_report_payload_sha256')
    invalidation_observation_id = runtime_report_artifact.artifact_id
    invalidation_observation_actor = 'actor:g2f:supplier:invalidation-observation:v01'
    invalidation_observation_subject = 'g2e_invalidation_observation:g2f:supplier'
    rows[122]['supplier'] = semantic_work.build_semantic_work_request_v01(request_id=SHARED_REQUEST_ID, transaction_id=supplier_transaction_id, target_root_id=supplier_root_id, runtime_topology_ref=invalidation_observation_id, bounded_context_refs=(invalidation_observation_id,), permitted_actor_ids=(invalidation_observation_actor,), permitted_contribution_modes=('DETERMINISTIC',), requested_subjects=(invalidation_observation_subject,), required_evidence_classes=('G2E_RUNTIME_REPORT_EVIDENCE',), forbidden_claims=('aggregate_authority', 'external_effect'))
    assert_equal(record_validation(122, semantic_work.validate_semantic_work_request_v01, semantic_work.validate_semantic_work_request_v01(rows[122]['supplier']), ((122, rows[122]['supplier']),)), (), 'row122_supplier')
    emit_receipt(122, 1, 'supplier', semantic_work.build_semantic_work_request_v01, rows[122]['supplier'], input_bindings=((5, 'supplier', rows[5]['supplier'], rows[5]['supplier']), (120, 'supplier', rows[120]['supplier'], rows[120]['supplier'])))
    rows[123]['supplier'] = semantic_work.build_evidence_binding_v01(evidence_id='evidence-binding:g2f:supplier:g2e-observation:v01', evidence_ref=invalidation_observation_id, evidence_class='G2E_RUNTIME_REPORT_EVIDENCE', source_component_id=invalidation_observation_actor, provenance_ref=invalidation_observation_id, evidence_state=semantic_work.EVIDENCE_STATE_PRESENT)
    emit_receipt(123, 1, 'supplier', semantic_work.build_evidence_binding_v01, rows[123]['supplier'], input_bindings=((120, 'supplier', rows[120]['supplier'], rows[120]['supplier']),))
    rows[124]['supplier'] = semantic_work.build_normalized_claim_v01(claim_id=invalidation_observation_id, subject=invalidation_observation_subject, predicate='accept_g2e_invalidation_observation_v01', object_or_value={'candidate_id': invalidation_observation_id, 'candidate_kind': 'G2E_INVALIDATION_OBSERVATION'}, time_envelope_ref=rows[75]['supplier'].temporal_authority_fingerprint, provenance_refs=(invalidation_observation_id,), evidence_refs=(rows[123]['supplier'].evidence_id,), confidence_micros=1000000, source_role='deterministic_runtime', source_mode='DETERMINISTIC')
    assert_equal(rows[124]['supplier'].claim_id, invalidation_observation_id, 'row124_exact_claim')
    emit_receipt(124, 1, 'supplier', semantic_work.build_normalized_claim_v01, rows[124]['supplier'], input_bindings=((75, 'supplier', rows[75]['supplier'], rows[75]['supplier']), (120, 'supplier', rows[120]['supplier'], rows[120]['supplier']), (123, 'supplier', rows[123]['supplier'], rows[123]['supplier'])))
    rows[125]['supplier'] = semantic_work.build_actor_contribution_v01(contribution_id='contribution:g2f:supplier:g2e-observation:v01', request_id=rows[122]['supplier'].request_id, actor_id=invalidation_observation_actor, actor_role='deterministic_runtime', contribution_mode='DETERMINISTIC', bsep_projection_ref=rows[7]['supplier'].projection_id, scope=invalidation_observation_subject, bounded_context_refs=rows[122]['supplier'].bounded_context_refs, claims=(rows[124]['supplier'],), evidence_bindings=(rows[123]['supplier'],), constraint_bindings=(), uncertainty_bindings=(), requested_validators=('validator:g2f:supplier:g2e-observation:v01',), forbidden_claims_observed=())
    assert_equal(record_validation(125, semantic_work.validate_actor_contribution_v01, semantic_work.validate_actor_contribution_v01(request=rows[122]['supplier'], contribution=rows[125]['supplier'], trust_profiles=rows[17]['supplier']), ((17, rows[17]['supplier']), (122, rows[122]['supplier']), (125, rows[125]['supplier']))), (), 'row125_supplier')
    emit_receipt(125, 1, 'supplier', semantic_work.build_actor_contribution_v01, rows[125]['supplier'], input_bindings=((7, 'supplier', rows[7]['supplier'], rows[7]['supplier']), (17, 'supplier', rows[17]['supplier'], rows[17]['supplier']), (122, 'supplier', rows[122]['supplier'], rows[122]['supplier']), (123, 'supplier', rows[123]['supplier'], rows[123]['supplier']), (124, 'supplier', rows[124]['supplier'], rows[124]['supplier'])))
    rows[126]['supplier'] = semantic_work.build_root_review_packet_from_contributions_v01(request=rows[122]['supplier'], contributions=(rows[125]['supplier'],), trust_profiles=rows[17]['supplier'])
    assert_equal(record_validation(126, semantic_work.validate_root_review_packet_v01, semantic_work.validate_root_review_packet_v01(request=rows[122]['supplier'], contributions=(rows[125]['supplier'],), packet=rows[126]['supplier'], trust_profiles=rows[17]['supplier']), ((17, rows[17]['supplier']), (122, rows[122]['supplier']), (125, rows[125]['supplier']), (126, rows[126]['supplier']))), (), 'row126_supplier')
    emit_receipt(126, 1, 'supplier', semantic_work.build_root_review_packet_from_contributions_v01, rows[126]['supplier'], input_bindings=((17, 'supplier', rows[17]['supplier'], rows[17]['supplier']), (122, 'supplier', rows[122]['supplier'], rows[122]['supplier']), (125, 'supplier', rows[125]['supplier'], rows[125]['supplier'])))
    rows[127]['supplier'] = root_decision.build_root_decision_input_v01(transaction_id=supplier_transaction_id, target_root_id=supplier_root_id, root_review_packet=rows[126]['supplier'], post_vv_bundle={'bundle_id': 'post-vv:g2f:supplier:g2e-observation:v01', 'hard_failure_reasons': [], 'post_vv_passed': True, 'provided_evidence_refs': [invalidation_observation_id], 'rejected_candidate_ids': [], 'required_evidence_refs': [invalidation_observation_id], 'validated_candidate_ids': [invalidation_observation_id]}, gt_advisory={'actor_role': 'gt', 'advisory_id': 'gt:g2f:supplier:g2e-observation:v01', 'advisory_only': True, 'attempted_effect': 'CREATE_ROOT_DECISION', 'candidate_ids': [invalidation_observation_id], 'creates_final_output': False, 'requests_effect': False, 'score_micros_by_candidate': {invalidation_observation_id: 1000000}, 'selected_candidate_id': invalidation_observation_id, 'source_artifact_type': 'GTAdvisoryReport', 'source_lifecycle_state': 'VALIDATED', 'target_artifact_type': 'RootDecision'}, policy_state={'policy_id': rows[75]['supplier'].authority_policy_fingerprint, 'identity_passed': True, 'scope_passed': True, 'hard_policy_passed': True, 'allow_accept': True, 'conflict_policy': 'DEFER', 'no_candidate_policy': 'NO_UPDATE'}, permission_state={'permission_required': False, 'user_permission_present': False, 'permission_scope_valid': True, 'permission_ref': None}, temporal_state={'temporal_valid': True, 'expired': False, 'not_before_satisfied': True, 'time_envelope_ref': rows[75]['supplier'].temporal_authority_fingerprint}, conflict_state={'material_unresolved_conflict': False, 'conflict_set_ids': []}, prior_root_state={'prior_decision_id': None, 'prior_decision': None, 'prior_selected_candidate_id': None})
    assert_equal(record_validation(127, root_decision.validate_root_decision_input_v01, root_decision.validate_root_decision_input_v01(kernel=rows[12]['supplier'], decision_input=rows[127]['supplier']), ((12, rows[12]['supplier']), (127, rows[127]['supplier']))), (), 'row127_supplier')
    assert_equal((rows[127]['supplier'].transaction_id, rows[127]['supplier'].target_root_id), (supplier_transaction_id, supplier_root_id), 'row127_transaction_root')
    emit_receipt(127, 1, 'supplier', root_decision.build_root_decision_input_v01, rows[127]['supplier'], input_bindings=((5, 'supplier', rows[5]['supplier'], rows[5]['supplier']), (12, 'supplier', rows[12]['supplier'], rows[12]['supplier']), (75, 'supplier', rows[75]['supplier'], rows[75]['supplier']), (120, 'supplier', rows[120]['supplier'], rows[120]['supplier']), (126, 'supplier', rows[126]['supplier'], rows[126]['supplier'])))
    rows[128]['supplier'] = root_decision.decide_root_v01(kernel=rows[12]['supplier'], decision_input=rows[127]['supplier'])
    assert_equal(record_validation(128, root_decision.validate_root_decision_result_v01, root_decision.validate_root_decision_result_v01(kernel=rows[12]['supplier'], decision_input=rows[127]['supplier'], result=rows[128]['supplier']), ((12, rows[12]['supplier']), (127, rows[127]['supplier']), (128, rows[128]['supplier']))), (), 'row128_supplier')
    assert_equal((rows[128]['supplier'].decision, rows[128]['supplier'].reason_code, rows[128]['supplier'].selected_candidate_id, rows[128]['supplier'].root_commit_created, rows[128]['supplier'].permission_created, rows[128]['supplier'].final_output_created, rows[128]['supplier'].effect_requested), ('ACCEPT', 'validated_candidate_accepted', invalidation_observation_id, True, False, False, False), 'row128_outcome')
    emit_receipt(128, 1, 'supplier', root_decision.decide_root_v01, rows[128]['supplier'], input_bindings=((12, 'supplier', rows[12]['supplier'], rows[12]['supplier']), (120, 'supplier', rows[120]['supplier'], rows[120]['supplier']), (127, 'supplier', rows[127]['supplier'], rows[127]['supplier'])))
    rows[129]['supplier'] = action_packet.build_action_invalidation_evidence_v01(source_invalidation_event_ref=runtime_report_artifact.artifact_id, packet_id=rows[84]['supplier'].packet_identity.packet_id, dependency_id=rows[104]['supplier'].dependency_id, invalidation_class='DEPENDENCY_CHANGED', evidence_ref=runtime_report_artifact.artifact_id, evidence_sha256=runtime_report_payload_sha256, observed_status='CHANGED', time_envelope_id=rows[104]['supplier'].time_envelope_id, freshness_policy_id=rows[104]['supplier'].freshness_policy_id, owning_local_root_id=supplier_root_id, accepted_by_local_root_id=supplier_root_id, acceptance_root_decision_id=None, acceptance_root_decision_hash=None, authority_effect='DETERMINISTIC_BLOCK', root_decision_ref=None, evaluation_time=rows[104]['supplier'].evaluation_time, evaluation_time_source=rows[104]['supplier'].evaluation_time_source, evaluation_context_id=rows[104]['supplier'].evaluation_context_id)
    assert_equal(record_validation(129, action_packet.validate_action_invalidation_evidence_v01, action_packet.validate_action_invalidation_evidence_v01(rows[129]['supplier']), ((129, rows[129]['supplier']),)), (True, ()), 'row129_supplier')
    assert_equal((rows[129]['supplier'].acceptance_root_decision_id, rows[129]['supplier'].acceptance_root_decision_hash, rows[129]['supplier'].root_decision_ref), (None, None, None), 'row129_root_absence')
    row127_plain = root_decision.root_decision_input_to_plain_dict_v01(rows[127]['supplier'])
    assert_equal((rows[124]['supplier'].claim_id, tuple(row127_plain['post_vv_bundle']['validated_candidate_ids']), row127_plain['gt_advisory']['selected_candidate_id'], rows[128]['supplier'].selected_candidate_id), (runtime_report_artifact.artifact_id, (runtime_report_artifact.artifact_id,), runtime_report_artifact.artifact_id, runtime_report_artifact.artifact_id), 'row129_cross_stage_observation_acceptance')
    emit_receipt(129, 1, 'supplier', action_packet.build_action_invalidation_evidence_v01, rows[129]['supplier'], input_bindings=((84, 'supplier', rows[84]['supplier'], rows[84]['supplier']), (104, 'supplier', rows[104]['supplier'], rows[104]['supplier']), (120, 'supplier', rows[120]['supplier'], rows[120]['supplier']), (124, 'supplier', rows[124]['supplier'], rows[124]['supplier']), (127, 'supplier', rows[127]['supplier'], rows[127]['supplier']), (128, 'supplier', rows[128]['supplier'], rows[128]['supplier'])))
    rows[130]['supplier'] = action_packet.build_revocation_candidate_v01(owning_local_root_id=supplier_root_id, packet_id=rows[84]['supplier'].packet_identity.packet_id, source_authorization_decision_id=rows[82]['supplier'].decision_id, idempotency_key=rows[75]['supplier'].idempotency_identity.idempotency_key, revocation_reason_class='DEPENDENCY_CHANGED', evidence_refs=(rows[129]['supplier'].invalidation_evidence_id,), evidence_hashes=(rows[129]['supplier'].invalidation_evidence_id,), evaluation_time=rows[129]['supplier'].evaluation_time, policy_fingerprint=rows[75]['supplier'].authority_policy_fingerprint)
    assert_equal(record_validation(130, action_packet.validate_revocation_candidate_v01, action_packet.validate_revocation_candidate_v01(rows[130]['supplier']), ((130, rows[130]['supplier']),)), (True, ()), 'row130_supplier')
    assert_equal(record_validation(130, action_packet.validate_revocation_candidate_against_packet_v01, action_packet.validate_revocation_candidate_against_packet_v01(rows[130]['supplier'], rows[84]['supplier']), ((84, rows[84]['supplier']), (130, rows[130]['supplier']))), (True, ()), 'row130_supplier_context')
    assert_equal((rows[130]['supplier'].evidence_refs, rows[130]['supplier'].evidence_hashes), ((rows[129]['supplier'].invalidation_evidence_id,), (rows[129]['supplier'].invalidation_evidence_id,)), 'row130_exact_observation_binding')
    emit_receipt(130, 1, 'supplier', action_packet.build_revocation_candidate_v01, rows[130]['supplier'], input_bindings=((75, 'supplier', rows[75]['supplier'], rows[75]['supplier']), (82, 'supplier', rows[82]['supplier'], rows[82]['supplier']), (84, 'supplier', rows[84]['supplier'], rows[84]['supplier']), (129, 'supplier', rows[129]['supplier'], rows[129]['supplier'])))
    revocation_candidate_id = rows[130]['supplier'].revocation_candidate_id
    revocation_actor = 'actor:g2f:supplier:revocation:v01'
    revocation_subject = 'action_revocation:g2f:supplier'
    rows[131]['supplier'] = semantic_work.build_semantic_work_request_v01(request_id=SHARED_REQUEST_ID, transaction_id=supplier_transaction_id, target_root_id=supplier_root_id, runtime_topology_ref=revocation_candidate_id, bounded_context_refs=(revocation_candidate_id,), permitted_actor_ids=(revocation_actor,), permitted_contribution_modes=('DETERMINISTIC',), requested_subjects=(revocation_subject,), required_evidence_classes=('REVOCATION_CANDIDATE_EVIDENCE',), forbidden_claims=('aggregate_authority', 'external_effect'))
    assert_equal(record_validation(131, semantic_work.validate_semantic_work_request_v01, semantic_work.validate_semantic_work_request_v01(rows[131]['supplier']), ((131, rows[131]['supplier']),)), (), 'row131_supplier')
    emit_receipt(131, 1, 'supplier', semantic_work.build_semantic_work_request_v01, rows[131]['supplier'], input_bindings=((5, 'supplier', rows[5]['supplier'], rows[5]['supplier']), (130, 'supplier', rows[130]['supplier'], rows[130]['supplier'])))
    rows[132]['supplier'] = semantic_work.build_evidence_binding_v01(evidence_id='evidence-binding:g2f:supplier:revocation:v01', evidence_ref=revocation_candidate_id, evidence_class='REVOCATION_CANDIDATE_EVIDENCE', source_component_id=revocation_actor, provenance_ref=revocation_candidate_id, evidence_state=semantic_work.EVIDENCE_STATE_PRESENT)
    emit_receipt(132, 1, 'supplier', semantic_work.build_evidence_binding_v01, rows[132]['supplier'], input_bindings=((130, 'supplier', rows[130]['supplier'], rows[130]['supplier']),))
    rows[133]['supplier'] = semantic_work.build_normalized_claim_v01(claim_id=revocation_candidate_id, subject=revocation_subject, predicate=action_packet.ROOT_DECISION_CLAIM_PREDICATE_REVOCATION_V01, object_or_value={'candidate_id': revocation_candidate_id, 'candidate_kind': 'REVOCATION'}, time_envelope_ref=rows[75]['supplier'].temporal_authority_fingerprint, provenance_refs=(revocation_candidate_id,), evidence_refs=(rows[132]['supplier'].evidence_id,), confidence_micros=1000000, source_role='deterministic_runtime', source_mode='DETERMINISTIC')
    emit_receipt(133, 1, 'supplier', semantic_work.build_normalized_claim_v01, rows[133]['supplier'], input_bindings=((75, 'supplier', rows[75]['supplier'], rows[75]['supplier']), (130, 'supplier', rows[130]['supplier'], rows[130]['supplier']), (132, 'supplier', rows[132]['supplier'], rows[132]['supplier'])))
    rows[134]['supplier'] = semantic_work.build_actor_contribution_v01(contribution_id='contribution:g2f:supplier:revocation:v01', request_id=rows[131]['supplier'].request_id, actor_id=revocation_actor, actor_role='deterministic_runtime', contribution_mode='DETERMINISTIC', bsep_projection_ref=rows[7]['supplier'].projection_id, scope=revocation_subject, bounded_context_refs=rows[131]['supplier'].bounded_context_refs, claims=(rows[133]['supplier'],), evidence_bindings=(rows[132]['supplier'],), constraint_bindings=(), uncertainty_bindings=(), requested_validators=('validator:g2f:supplier:revocation:v01',), forbidden_claims_observed=())
    assert_equal(record_validation(134, semantic_work.validate_actor_contribution_v01, semantic_work.validate_actor_contribution_v01(request=rows[131]['supplier'], contribution=rows[134]['supplier'], trust_profiles=rows[17]['supplier']), ((17, rows[17]['supplier']), (131, rows[131]['supplier']), (134, rows[134]['supplier']))), (), 'row134_supplier')
    emit_receipt(134, 1, 'supplier', semantic_work.build_actor_contribution_v01, rows[134]['supplier'], input_bindings=((7, 'supplier', rows[7]['supplier'], rows[7]['supplier']), (17, 'supplier', rows[17]['supplier'], rows[17]['supplier']), (131, 'supplier', rows[131]['supplier'], rows[131]['supplier']), (132, 'supplier', rows[132]['supplier'], rows[132]['supplier']), (133, 'supplier', rows[133]['supplier'], rows[133]['supplier'])))
    rows[135]['supplier'] = semantic_work.build_root_review_packet_from_contributions_v01(request=rows[131]['supplier'], contributions=(rows[134]['supplier'],), trust_profiles=rows[17]['supplier'])
    assert_equal(record_validation(135, semantic_work.validate_root_review_packet_v01, semantic_work.validate_root_review_packet_v01(request=rows[131]['supplier'], contributions=(rows[134]['supplier'],), packet=rows[135]['supplier'], trust_profiles=rows[17]['supplier']), ((17, rows[17]['supplier']), (131, rows[131]['supplier']), (134, rows[134]['supplier']), (135, rows[135]['supplier']))), (), 'row135_supplier')
    emit_receipt(135, 1, 'supplier', semantic_work.build_root_review_packet_from_contributions_v01, rows[135]['supplier'], input_bindings=((17, 'supplier', rows[17]['supplier'], rows[17]['supplier']), (131, 'supplier', rows[131]['supplier'], rows[131]['supplier']), (134, 'supplier', rows[134]['supplier'], rows[134]['supplier'])))
    rows[136]['supplier'] = root_decision.build_root_decision_input_v01(transaction_id=supplier_transaction_id, target_root_id=supplier_root_id, root_review_packet=rows[135]['supplier'], post_vv_bundle={'bundle_id': 'post-vv:g2f:supplier:revocation:v01', 'hard_failure_reasons': [], 'post_vv_passed': True, 'provided_evidence_refs': [rows[129]['supplier'].invalidation_evidence_id], 'rejected_candidate_ids': [], 'required_evidence_refs': [rows[129]['supplier'].invalidation_evidence_id], 'validated_candidate_ids': [revocation_candidate_id]}, gt_advisory={'actor_role': 'gt', 'advisory_id': 'gt:g2f:supplier:revocation:v01', 'advisory_only': True, 'attempted_effect': 'CREATE_ROOT_DECISION', 'candidate_ids': [revocation_candidate_id], 'creates_final_output': False, 'requests_effect': False, 'score_micros_by_candidate': {revocation_candidate_id: 1000000}, 'selected_candidate_id': revocation_candidate_id, 'source_artifact_type': 'GTAdvisoryReport', 'source_lifecycle_state': 'VALIDATED', 'target_artifact_type': 'RootDecision'}, policy_state={'policy_id': rows[75]['supplier'].authority_policy_fingerprint, 'identity_passed': True, 'scope_passed': True, 'hard_policy_passed': True, 'allow_accept': True, 'conflict_policy': 'DEFER', 'no_candidate_policy': 'NO_UPDATE'}, permission_state={'permission_required': False, 'user_permission_present': False, 'permission_scope_valid': True, 'permission_ref': None}, temporal_state={'temporal_valid': True, 'expired': False, 'not_before_satisfied': True, 'time_envelope_ref': rows[75]['supplier'].temporal_authority_fingerprint}, conflict_state={'material_unresolved_conflict': False, 'conflict_set_ids': []}, prior_root_state={'prior_decision_id': rows[82]['supplier'].decision_id, 'prior_decision': 'ACCEPT', 'prior_selected_candidate_id': rows[75]['supplier'].authorization_candidate.root_packet_authorization_candidate_id})
    assert_equal(record_validation(136, root_decision.validate_root_decision_input_v01, root_decision.validate_root_decision_input_v01(kernel=rows[12]['supplier'], decision_input=rows[136]['supplier']), ((12, rows[12]['supplier']), (136, rows[136]['supplier']))), (), 'row136_supplier')
    emit_receipt(136, 1, 'supplier', root_decision.build_root_decision_input_v01, rows[136]['supplier'], input_bindings=((5, 'supplier', rows[5]['supplier'], rows[5]['supplier']), (12, 'supplier', rows[12]['supplier'], rows[12]['supplier']), (75, 'supplier', rows[75]['supplier'], rows[75]['supplier']), (82, 'supplier', rows[82]['supplier'], rows[82]['supplier']), (129, 'supplier', rows[129]['supplier'], rows[129]['supplier']), (130, 'supplier', rows[130]['supplier'], rows[130]['supplier']), (135, 'supplier', rows[135]['supplier'], rows[135]['supplier'])))
    rows[137]['supplier'] = root_decision.decide_root_v01(kernel=rows[12]['supplier'], decision_input=rows[136]['supplier'])
    assert_equal(record_validation(137, root_decision.validate_root_decision_result_v01, root_decision.validate_root_decision_result_v01(kernel=rows[12]['supplier'], decision_input=rows[136]['supplier'], result=rows[137]['supplier']), ((12, rows[12]['supplier']), (136, rows[136]['supplier']), (137, rows[137]['supplier']))), (), 'row137_supplier')
    assert_equal((rows[137]['supplier'].decision, rows[137]['supplier'].reason_code, rows[137]['supplier'].selected_candidate_id, rows[137]['supplier'].root_commit_created, rows[137]['supplier'].permission_created, rows[137]['supplier'].final_output_created, rows[137]['supplier'].effect_requested), ('ACCEPT', 'validated_candidate_accepted', revocation_candidate_id, True, False, False, False), 'row137_outcome')
    emit_receipt(137, 1, 'supplier', root_decision.decide_root_v01, rows[137]['supplier'], input_bindings=((12, 'supplier', rows[12]['supplier'], rows[12]['supplier']), (130, 'supplier', rows[130]['supplier'], rows[130]['supplier']), (136, 'supplier', rows[136]['supplier'], rows[136]['supplier'])))
    rows[138]['supplier'] = action_packet.build_root_decision_candidate_projection_v01(candidate_kind=action_packet.ROOT_DECISION_CANDIDATE_KIND_REVOCATION_V01, projected_candidate_id=revocation_candidate_id, root_decision_kernel=rows[12]['supplier'], root_decision_input=rows[136]['supplier'], root_decision_result=rows[137]['supplier'])
    assert_equal(record_validation(138, action_packet.validate_root_decision_candidate_projection_v01, action_packet.validate_root_decision_candidate_projection_v01(rows[138]['supplier']), ((138, rows[138]['supplier']),)), (True, ()), 'row138_supplier')
    assert_equal(record_validation(138, action_packet.validate_revocation_root_context_coherence_v01, action_packet.validate_revocation_root_context_coherence_v01(rows[130]['supplier'], rows[138]['supplier'], rows[84]['supplier']), ((84, rows[84]['supplier']), (130, rows[130]['supplier']), (138, rows[138]['supplier']))), (True, ()), 'row138_supplier_context')
    emit_receipt(138, 1, 'supplier', action_packet.build_root_decision_candidate_projection_v01, rows[138]['supplier'], input_bindings=((12, 'supplier', rows[12]['supplier'], rows[12]['supplier']), (84, 'supplier', rows[84]['supplier'], rows[84]['supplier']), (130, 'supplier', rows[130]['supplier'], rows[130]['supplier']), (136, 'supplier', rows[136]['supplier'], rows[136]['supplier']), (137, 'supplier', rows[137]['supplier'], rows[137]['supplier'])))
    rows[139]['supplier'] = action_packet.build_accepted_revocation_binding_v01(candidate=rows[130]['supplier'], root_projection=rows[138]['supplier'], packet=rows[84]['supplier'])
    assert_equal(record_validation(139, action_packet.validate_accepted_revocation_binding_v01, action_packet.validate_accepted_revocation_binding_v01(rows[139]['supplier']), ((139, rows[139]['supplier']),)), (True, ()), 'row139_supplier')
    emit_receipt(139, 1, 'supplier', action_packet.build_accepted_revocation_binding_v01, rows[139]['supplier'], input_bindings=((84, 'supplier', rows[84]['supplier'], rows[84]['supplier']), (130, 'supplier', rows[130]['supplier'], rows[130]['supplier']), (138, 'supplier', rows[138]['supplier'], rows[138]['supplier'])))
    revocation_binding_digest = rows[139]['supplier'].accepted_revocation_binding_id.split(':', 1)[1]
    rows[140]['supplier'] = action_packet.build_action_invalidation_evidence_v01(source_invalidation_event_ref=rows[129]['supplier'].invalidation_evidence_id, packet_id=rows[84]['supplier'].packet_identity.packet_id, dependency_id='dependency:root_revocation', invalidation_class='ROOT_REVOCATION', evidence_ref=rows[139]['supplier'].accepted_revocation_binding_id, evidence_sha256=revocation_binding_digest, observed_status='OBSERVED_ROOT_REVOCATION', time_envelope_id=rows[129]['supplier'].time_envelope_id, freshness_policy_id=rows[129]['supplier'].freshness_policy_id, owning_local_root_id=supplier_root_id, accepted_by_local_root_id=supplier_root_id, acceptance_root_decision_id=rows[137]['supplier'].decision_id, acceptance_root_decision_hash=rows[138]['supplier'].source_root_decision_hash, authority_effect='ROOT_REVOCATION', root_decision_ref=rows[137]['supplier'].decision_id, evaluation_time=rows[129]['supplier'].evaluation_time, evaluation_time_source=rows[129]['supplier'].evaluation_time_source, evaluation_context_id=rows[129]['supplier'].evaluation_context_id)
    assert_equal(record_validation(140, action_packet.validate_action_invalidation_evidence_v01, action_packet.validate_action_invalidation_evidence_v01(rows[140]['supplier']), ((140, rows[140]['supplier']),)), (True, ()), 'row140_supplier')
    assert_equal(record_validation(140, action_packet.validate_action_invalidation_evidence_against_packet_v01, action_packet.validate_action_invalidation_evidence_against_packet_v01(rows[140]['supplier'], rows[84]['supplier'], revocation_candidate=rows[130]['supplier'], revocation_root_projection=rows[138]['supplier'], accepted_revocation_binding=rows[139]['supplier']), ((84, rows[84]['supplier']), (130, rows[130]['supplier']), (138, rows[138]['supplier']), (139, rows[139]['supplier']), (140, rows[140]['supplier']))), (True, ()), 'row140_supplier_context')
    emit_receipt(140, 1, 'supplier', action_packet.build_action_invalidation_evidence_v01, rows[140]['supplier'], input_bindings=((84, 'supplier', rows[84]['supplier'], rows[84]['supplier']), (129, 'supplier', rows[129]['supplier'], rows[129]['supplier']), (130, 'supplier', rows[130]['supplier'], rows[130]['supplier']), (137, 'supplier', rows[137]['supplier'], rows[137]['supplier']), (138, 'supplier', rows[138]['supplier'], rows[138]['supplier']), (139, 'supplier', rows[139]['supplier'], rows[139]['supplier'])))
    revocation_rule = transition_registry.lookup_action_packet_transition_rule_v01(registry=rows[85]['supplier'], transition_rule_id='g2a_t18_pending_revoke')
    revocation_material = {'accepted_revocation_binding_valid': (rows[139]['supplier'].accepted_revocation_binding_id, revocation_binding_digest, 'accepted_revocation_binding_v01'), 'source_authorization_binding_valid': (rows[82]['supplier'].decision_id, rows[84]['supplier'].root_decision_projection.source_root_decision_hash, 'root_decision_result_v01'), 'adapter_not_called': (rows[95]['supplier'].execution_attempt_id, rows[95]['supplier'].execution_attempt_id.split(':', 1)[1], action_packet.EXECUTION_ATTEMPT_IDENTITY_PROFILE_ID_V01), 'idempotency_reservation_owned': (rows[90]['supplier'].idempotency_disposition_event_id, rows[90]['supplier'].idempotency_disposition_event_id.split(':', 1)[1], action_packet.IDEMPOTENCY_DISPOSITION_EVENT_PROFILE_ID_V01)}
    revocation_bindings = []
    for component_ordinal, evidence_code in enumerate(revocation_rule.required_evidence_codes, start=1):
        evidence_ref, evidence_hash, validator_profile = revocation_material[evidence_code]
        binding = action_packet.build_transition_evidence_binding_v01(action_packet_transition_registry_profile=rows[85]['supplier'], transition_rule_id=revocation_rule.transition_rule_id, evidence_code=evidence_code, evidence_ref=evidence_ref, evidence_sha256=evidence_hash, validator_profile_id=validator_profile)
        assert_equal(record_validation(141, action_packet.validate_transition_evidence_binding_v01, action_packet.validate_transition_evidence_binding_v01(binding, action_packet_transition_registry_profile=rows[85]['supplier'], transition_rule_id=revocation_rule.transition_rule_id), ((85, rows[85]['supplier']),)), (True, ()), f'row141_{component_ordinal}')
        revocation_bindings.append(binding)
        emit_component(141, component_ordinal, 'supplier', action_packet.build_transition_evidence_binding_v01, (evidence_ref,), binding, evidence_code)
    rows[141]['supplier'] = tuple(revocation_bindings)
    assert_equal((len(rows[141]['supplier']), tuple((item.evidence_code for item in rows[141]['supplier']))), (4, revocation_rule.required_evidence_codes), 'row141_order')
    emit_receipt(141, 1, 'supplier', action_packet.build_transition_evidence_binding_v01, rows[141]['supplier'], input_bindings=((82, 'supplier', rows[82]['supplier'], rows[82]['supplier']), (84, 'supplier', rows[84]['supplier'], rows[84]['supplier']), (85, 'supplier', rows[85]['supplier'], rows[85]['supplier']), (90, 'supplier', rows[90]['supplier'], rows[90]['supplier']), (95, 'supplier', rows[95]['supplier'], rows[95]['supplier']), (139, 'supplier', rows[139]['supplier'], rows[139]['supplier'])))
    rows[142]['supplier'] = action_packet.build_action_packet_transition_event_v01(action_packet_transition_registry_profile=rows[85]['supplier'], transition_rule_id=revocation_rule.transition_rule_id, packet_id=rows[84]['supplier'].packet_identity.packet_id, idempotency_key=rows[75]['supplier'].idempotency_identity.idempotency_key, previous_transition_event_id=rows[97]['supplier'].transition_event_id, owning_local_root_id=supplier_root_id, root_decision_ref=rows[137]['supplier'].decision_id, transition_evidence_bindings=rows[141]['supplier'], dependency_set_candidate_fingerprint=rows[75]['supplier'].dependency_set_candidate_fingerprint, temporal_authority_fingerprint=rows[75]['supplier'].temporal_authority_fingerprint, evaluation_time=rows[140]['supplier'].evaluation_time, evaluation_time_source=rows[140]['supplier'].evaluation_time_source, evaluation_context_id=rows[140]['supplier'].evaluation_context_id, execution_attempt_identity=None, receipt_ref=None)
    assert_equal(record_validation(142, action_packet.validate_action_packet_transition_event_v01, action_packet.validate_action_packet_transition_event_v01(rows[142]['supplier'], action_packet_transition_registry_profile=rows[85]['supplier']), ((85, rows[85]['supplier']), (142, rows[142]['supplier']))), (True, ()), 'row142_supplier')
    emit_receipt(142, 1, 'supplier', action_packet.build_action_packet_transition_event_v01, rows[142]['supplier'], input_bindings=((75, 'supplier', rows[75]['supplier'], rows[75]['supplier']), (84, 'supplier', rows[84]['supplier'], rows[84]['supplier']), (85, 'supplier', rows[85]['supplier'], rows[85]['supplier']), (97, 'supplier', rows[97]['supplier'], rows[97]['supplier']), (137, 'supplier', rows[137]['supplier'], rows[137]['supplier']), (140, 'supplier', rows[140]['supplier'], rows[140]['supplier']), (141, 'supplier', rows[141]['supplier'], rows[141]['supplier'])))
    row098_registry_bytes = repr(rows[98]['supplier']).encode('utf-8')
    rows[143]['supplier'] = action_packet.record_action_packet_revocation_v01(rows[98]['supplier'], packet_id=rows[84]['supplier'].packet_identity.packet_id, revocation_candidate=rows[130]['supplier'], revocation_root_projection=rows[138]['supplier'], accepted_revocation_binding=rows[139]['supplier'], invalidation_evidence=rows[140]['supplier'], transition_event=rows[142]['supplier'], action_packet_transition_registry_profile=rows[85]['supplier'])
    assert_equal(record_validation(143, action_packet.validate_action_commit_packet_registry_v02, action_packet.validate_action_commit_packet_registry_v02(rows[143]['supplier']), ((143, rows[143]['supplier']),)), (True, ()), 'row143_registry')
    revoked_entry = tuple((item for item in rows[143]['supplier'].action_packet_lifecycle_entries if item.root_bound_genesis.packet_identity.packet_id == rows[84]['supplier'].packet_identity.packet_id))[0]
    assert_equal(record_validation(143, action_packet.validate_action_packet_transition_history_v01, action_packet.validate_action_packet_transition_history_v01(revoked_entry.transition_events, root_bound_genesis=revoked_entry.root_bound_genesis, action_packet_transition_registry_profile=rows[85]['supplier'], invalidation_contexts=rows[143]['supplier'].action_packet_invalidation_contexts, idempotency_disposition_events=rows[143]['supplier'].idempotency_disposition_events, lifecycle_entries=rows[143]['supplier'].action_packet_lifecycle_entries), ((85, rows[85]['supplier']), (143, rows[143]['supplier'].action_packet_invalidation_contexts), (143, rows[143]['supplier'].action_packet_lifecycle_entries), (143, rows[143]['supplier'].idempotency_disposition_events))), (True, ()), 'row143_history')
    revoked_state = action_packet.derive_action_packet_lifecycle_state_v01(rows[143]['supplier'], packet_id=rows[84]['supplier'].packet_identity.packet_id, action_packet_transition_registry_profile=rows[85]['supplier'])
    assert_equal((revoked_state.lifecycle_state, revoked_state.idempotency_disposition, revoked_state.reservation_owner_packet_id, revoked_state.executable, rows[143]['supplier'].executes_payment, rows[143]['supplier'].releases_shipment, rows[143]['supplier'].real_world_effects_count), ('REVOKED', 'RESERVED', rows[84]['supplier'].packet_identity.packet_id, False, False, False, 0), 'row143_state')
    assert_equal(repr(rows[98]['supplier']).encode('utf-8'), row098_registry_bytes, 'row143_row098_unchanged')
    emit_receipt(143, 1, 'supplier', action_packet.record_action_packet_revocation_v01, rows[143]['supplier'], input_bindings=((84, 'supplier', rows[84]['supplier'], rows[84]['supplier']), (85, 'supplier', rows[85]['supplier'], rows[85]['supplier']), (98, 'supplier', rows[98]['supplier'], rows[98]['supplier']), (130, 'supplier', rows[130]['supplier'], rows[130]['supplier']), (138, 'supplier', rows[138]['supplier'], rows[138]['supplier']), (139, 'supplier', rows[139]['supplier'], rows[139]['supplier']), (140, 'supplier', rows[140]['supplier'], rows[140]['supplier']), (142, 'supplier', rows[142]['supplier'], rows[142]['supplier'])))
    terminal_evaluation_time = PACKET_EVALUATION_TIME + 3
    terminal_evaluation_source = 'g2f_deterministic_logical_time'
    terminal_evaluation_context = present_context_id
    rows[144]['supplier'] = action_packet.inspect_action_packet_present_eligibility_v01(rows[143]['supplier'], packet_id=rows[84]['supplier'].packet_identity.packet_id, corridor=rows[100]['supplier'], corridor_step=rows[99]['supplier'], current_dependency_observations=(rows[101]['supplier'],), logical_time_bridge=rows[102]['supplier'], evaluation_time=terminal_evaluation_time, evaluation_time_source=terminal_evaluation_source, evaluation_context_id=terminal_evaluation_context, action_packet_transition_registry_profile=rows[85]['supplier'])
    assert_equal(record_validation(144, action_packet.validate_action_packet_present_eligibility_inspection_v01, action_packet.validate_action_packet_present_eligibility_inspection_v01(rows[144]['supplier'], rows[143]['supplier'], packet_id=rows[84]['supplier'].packet_identity.packet_id, corridor=rows[100]['supplier'], corridor_step=rows[99]['supplier'], current_dependency_observations=(rows[101]['supplier'],), logical_time_bridge=rows[102]['supplier'], evaluation_time=terminal_evaluation_time, evaluation_time_source=terminal_evaluation_source, evaluation_context_id=terminal_evaluation_context, action_packet_transition_registry_profile=rows[85]['supplier']), ((84, rows[84]['supplier'].packet_identity.packet_id), (85, rows[85]['supplier']), (99, rows[99]['supplier']), (100, rows[100]['supplier']), (101, rows[101]['supplier']), (102, rows[102]['supplier']), (143, rows[143]['supplier']), (144, rows[144]['supplier']))), (True, ()), 'row144_supplier')
    assert_equal((rows[144]['supplier'].present_eligibility_status, rows[144]['supplier'].present_executable, rows[144]['supplier'].reason_codes, rows[144]['supplier'].adapter_calls, rows[144]['supplier'].real_world_effects_count), ('NON_EXECUTABLE', False, ('action_packet_present_state_non_executable',), 0, 0), 'row144_outcome')
    emit_receipt(144, 1, 'supplier', action_packet.inspect_action_packet_present_eligibility_v01, rows[144]['supplier'], input_bindings=((84, 'supplier', rows[84]['supplier'], rows[84]['supplier']), (85, 'supplier', rows[85]['supplier'], rows[85]['supplier']), (99, 'supplier', rows[99]['supplier'], rows[99]['supplier']), (100, 'supplier', rows[100]['supplier'], rows[100]['supplier']), (101, 'supplier', rows[101]['supplier'], rows[101]['supplier']), (102, 'supplier', rows[102]['supplier'], rows[102]['supplier']), (143, 'supplier', rows[143]['supplier'], rows[143]['supplier'])))
    rows[145]['supplier'] = action_packet.build_supplier_action_commit_packet_canonical_projection_v01(rows[70]['supplier'], transaction_id=supplier_transaction_id, owning_local_root_id=supplier_root_id, canonical_permission_ref=rows[75]['supplier'].canonical_permission_ref, selected_legacy_action=rows[75]['supplier'].selected_legacy_action, logical_effect_namespace=rows[75]['supplier'].logical_intent.logical_effect_namespace, business_object_namespace=rows[75]['supplier'].business_object_identity.business_object_namespace, corridor_class=rows[75]['supplier'].adapter_binding.corridor_class, adapter_version=rows[75]['supplier'].adapter_binding.adapter_version, temporal_policy_version=rows[75]['supplier'].temporal_authority.temporal_policy_version, authority_policy=rows[74]['supplier'], dependency_candidate=rows[73]['supplier'], evaluation_time=rows[75]['supplier'].evaluation_time, evaluation_time_source=rows[75]['supplier'].evaluation_time_source, evaluation_context_id=rows[75]['supplier'].evaluation_context_id, predecessor_packet_id=rows[84]['supplier'].packet_identity.packet_id, supersession_reason_class='RENEWAL')
    assert_equal(record_validation(145, action_packet.validate_supplier_action_commit_packet_canonical_projection_v01, action_packet.validate_supplier_action_commit_packet_canonical_projection_v01(rows[145]['supplier']), ((145, rows[145]['supplier']),)), (True, ()), 'row145_supplier')
    successor_candidate_id = rows[145]['supplier'].authorization_candidate.root_packet_authorization_candidate_id
    assert_equal((rows[145]['supplier'].logical_intent.root_owned_intent_id, rows[145]['supplier'].idempotency_identity.idempotency_key, rows[145]['supplier'].authorization_candidate.predecessor_packet_id, rows[145]['supplier'].authorization_candidate.supersession_reason_class), (rows[75]['supplier'].logical_intent.root_owned_intent_id, rows[75]['supplier'].idempotency_identity.idempotency_key, rows[84]['supplier'].packet_identity.packet_id, 'RENEWAL'), 'row145_same_effect_renewal')
    assert_equal(successor_candidate_id != rows[75]['supplier'].authorization_candidate.root_packet_authorization_candidate_id, True, 'row145_candidate_distinct')
    emit_receipt(145, 1, 'supplier', action_packet.build_supplier_action_commit_packet_canonical_projection_v01, rows[145]['supplier'], input_bindings=((5, 'supplier', rows[5]['supplier'], rows[5]['supplier']), (70, 'supplier', rows[70]['supplier'], rows[70]['supplier']), (73, 'supplier', rows[73]['supplier'], rows[73]['supplier']), (74, 'supplier', rows[74]['supplier'], rows[74]['supplier']), (75, 'supplier', rows[75]['supplier'], rows[75]['supplier']), (84, 'supplier', rows[84]['supplier'], rows[84]['supplier'])))
    successor_actor = 'actor:g2f:supplier:successor-authorization:v01'
    successor_subject = 'action_commit_packet:g2f:supplier:successor'
    rows[146]['supplier'] = semantic_work.build_semantic_work_request_v01(request_id=SHARED_REQUEST_ID, transaction_id=supplier_transaction_id, target_root_id=supplier_root_id, runtime_topology_ref=successor_candidate_id, bounded_context_refs=(successor_candidate_id,), permitted_actor_ids=(successor_actor,), permitted_contribution_modes=('DETERMINISTIC',), requested_subjects=(successor_subject,), required_evidence_classes=('CANDIDATE_EVIDENCE',), forbidden_claims=('aggregate_authority', 'external_effect'))
    assert_equal(record_validation(146, semantic_work.validate_semantic_work_request_v01, semantic_work.validate_semantic_work_request_v01(rows[146]['supplier']), ((146, rows[146]['supplier']),)), (), 'row146_supplier')
    emit_receipt(146, 1, 'supplier', semantic_work.build_semantic_work_request_v01, rows[146]['supplier'], input_bindings=((5, 'supplier', rows[5]['supplier'], rows[5]['supplier']), (145, 'supplier', rows[145]['supplier'], rows[145]['supplier'])))
    rows[147]['supplier'] = semantic_work.build_evidence_binding_v01(evidence_id='evidence-binding:g2f:supplier:successor-authorization:v01', evidence_ref=successor_candidate_id, evidence_class='CANDIDATE_EVIDENCE', source_component_id=successor_actor, provenance_ref=successor_candidate_id, evidence_state=semantic_work.EVIDENCE_STATE_PRESENT)
    emit_receipt(147, 1, 'supplier', semantic_work.build_evidence_binding_v01, rows[147]['supplier'], input_bindings=((145, 'supplier', rows[145]['supplier'], rows[145]['supplier']),))
    rows[148]['supplier'] = semantic_work.build_normalized_claim_v01(claim_id=successor_candidate_id, subject=successor_subject, predicate='root_packet_authorization_candidate', object_or_value={'candidate_id': successor_candidate_id, 'candidate_kind': 'PACKET_AUTHORIZATION'}, time_envelope_ref=rows[145]['supplier'].temporal_authority_fingerprint, provenance_refs=(successor_candidate_id,), evidence_refs=(rows[147]['supplier'].evidence_id,), confidence_micros=1000000, source_role='deterministic_runtime', source_mode='DETERMINISTIC')
    emit_receipt(148, 1, 'supplier', semantic_work.build_normalized_claim_v01, rows[148]['supplier'], input_bindings=((145, 'supplier', rows[145]['supplier'], rows[145]['supplier']), (147, 'supplier', rows[147]['supplier'], rows[147]['supplier'])))
    rows[149]['supplier'] = semantic_work.build_actor_contribution_v01(contribution_id='contribution:g2f:supplier:successor-authorization:v01', request_id=rows[146]['supplier'].request_id, actor_id=successor_actor, actor_role='deterministic_runtime', contribution_mode='DETERMINISTIC', bsep_projection_ref=rows[7]['supplier'].projection_id, scope=successor_subject, bounded_context_refs=rows[146]['supplier'].bounded_context_refs, claims=(rows[148]['supplier'],), evidence_bindings=(rows[147]['supplier'],), constraint_bindings=(), uncertainty_bindings=(), requested_validators=('validator:g2f:supplier:successor-authorization:v01',), forbidden_claims_observed=())
    assert_equal(record_validation(149, semantic_work.validate_actor_contribution_v01, semantic_work.validate_actor_contribution_v01(request=rows[146]['supplier'], contribution=rows[149]['supplier'], trust_profiles=rows[17]['supplier']), ((17, rows[17]['supplier']), (146, rows[146]['supplier']), (149, rows[149]['supplier']))), (), 'row149_supplier')
    emit_receipt(149, 1, 'supplier', semantic_work.build_actor_contribution_v01, rows[149]['supplier'], input_bindings=((7, 'supplier', rows[7]['supplier'], rows[7]['supplier']), (17, 'supplier', rows[17]['supplier'], rows[17]['supplier']), (146, 'supplier', rows[146]['supplier'], rows[146]['supplier']), (147, 'supplier', rows[147]['supplier'], rows[147]['supplier']), (148, 'supplier', rows[148]['supplier'], rows[148]['supplier'])))
    rows[150]['supplier'] = semantic_work.build_root_review_packet_from_contributions_v01(request=rows[146]['supplier'], contributions=(rows[149]['supplier'],), trust_profiles=rows[17]['supplier'])
    assert_equal(record_validation(150, semantic_work.validate_root_review_packet_v01, semantic_work.validate_root_review_packet_v01(request=rows[146]['supplier'], contributions=(rows[149]['supplier'],), packet=rows[150]['supplier'], trust_profiles=rows[17]['supplier']), ((17, rows[17]['supplier']), (146, rows[146]['supplier']), (149, rows[149]['supplier']), (150, rows[150]['supplier']))), (), 'row150_supplier')
    emit_receipt(150, 1, 'supplier', semantic_work.build_root_review_packet_from_contributions_v01, rows[150]['supplier'], input_bindings=((17, 'supplier', rows[17]['supplier'], rows[17]['supplier']), (146, 'supplier', rows[146]['supplier'], rows[146]['supplier']), (149, 'supplier', rows[149]['supplier'], rows[149]['supplier'])))
    successor_dependency_refs = [record.evidence_ref for record in rows[145]['supplier'].dependency_candidate.dependency_records if record.requirement_class == 'MANDATORY']
    rows[151]['supplier'] = root_decision.build_root_decision_input_v01(transaction_id=supplier_transaction_id, target_root_id=supplier_root_id, root_review_packet=rows[150]['supplier'], post_vv_bundle={'bundle_id': 'post-vv:g2f:supplier:successor-authorization:v01', 'hard_failure_reasons': [], 'post_vv_passed': True, 'provided_evidence_refs': successor_dependency_refs, 'rejected_candidate_ids': [], 'required_evidence_refs': successor_dependency_refs, 'validated_candidate_ids': [successor_candidate_id]}, gt_advisory={'actor_role': 'gt', 'advisory_id': 'gt:g2f:supplier:successor-authorization:v01', 'advisory_only': True, 'attempted_effect': 'CREATE_ROOT_DECISION', 'candidate_ids': [successor_candidate_id], 'creates_final_output': False, 'requests_effect': False, 'score_micros_by_candidate': {successor_candidate_id: 1000000}, 'selected_candidate_id': successor_candidate_id, 'source_artifact_type': 'GTAdvisoryReport', 'source_lifecycle_state': 'VALIDATED', 'target_artifact_type': 'RootDecision'}, policy_state={'policy_id': rows[145]['supplier'].authority_policy_fingerprint, 'identity_passed': True, 'scope_passed': True, 'hard_policy_passed': True, 'allow_accept': True, 'conflict_policy': 'DEFER', 'no_candidate_policy': 'NO_UPDATE'}, permission_state={'permission_required': True, 'user_permission_present': True, 'permission_scope_valid': True, 'permission_ref': rows[145]['supplier'].canonical_permission_ref}, temporal_state={'temporal_valid': True, 'expired': False, 'not_before_satisfied': True, 'time_envelope_ref': rows[145]['supplier'].temporal_authority_fingerprint}, conflict_state={'material_unresolved_conflict': False, 'conflict_set_ids': []}, prior_root_state={'prior_decision_id': None, 'prior_decision': None, 'prior_selected_candidate_id': None})
    assert_equal(record_validation(151, root_decision.validate_root_decision_input_v01, root_decision.validate_root_decision_input_v01(kernel=rows[12]['supplier'], decision_input=rows[151]['supplier']), ((12, rows[12]['supplier']), (151, rows[151]['supplier']))), (), 'row151_supplier')
    emit_receipt(151, 1, 'supplier', root_decision.build_root_decision_input_v01, rows[151]['supplier'], input_bindings=((5, 'supplier', rows[5]['supplier'], rows[5]['supplier']), (12, 'supplier', rows[12]['supplier'], rows[12]['supplier']), (145, 'supplier', rows[145]['supplier'], rows[145]['supplier']), (150, 'supplier', rows[150]['supplier'], rows[150]['supplier'])))
    rows[152]['supplier'] = root_decision.decide_root_v01(kernel=rows[12]['supplier'], decision_input=rows[151]['supplier'])
    assert_equal(record_validation(152, root_decision.validate_root_decision_result_v01, root_decision.validate_root_decision_result_v01(kernel=rows[12]['supplier'], decision_input=rows[151]['supplier'], result=rows[152]['supplier']), ((12, rows[12]['supplier']), (151, rows[151]['supplier']), (152, rows[152]['supplier']))), (), 'row152_supplier')
    assert_equal((rows[152]['supplier'].decision, rows[152]['supplier'].reason_code, rows[152]['supplier'].selected_candidate_id, rows[152]['supplier'].root_commit_created, rows[152]['supplier'].permission_created, rows[152]['supplier'].final_output_created, rows[152]['supplier'].effect_requested), ('ACCEPT', 'validated_candidate_accepted', successor_candidate_id, True, False, False, False), 'row152_outcome')
    emit_receipt(152, 1, 'supplier', root_decision.decide_root_v01, rows[152]['supplier'], input_bindings=((12, 'supplier', rows[12]['supplier'], rows[12]['supplier']), (145, 'supplier', rows[145]['supplier'], rows[145]['supplier']), (151, 'supplier', rows[151]['supplier'], rows[151]['supplier'])))
    rows[153]['supplier'] = action_packet.build_root_decision_candidate_projection_v01(candidate_kind=action_packet.ROOT_DECISION_CANDIDATE_KIND_PACKET_AUTHORIZATION_V01, projected_candidate_id=successor_candidate_id, root_decision_kernel=rows[12]['supplier'], root_decision_input=rows[151]['supplier'], root_decision_result=rows[152]['supplier'])
    assert_equal(record_validation(153, action_packet.validate_root_decision_candidate_projection_v01, action_packet.validate_root_decision_candidate_projection_v01(rows[153]['supplier']), ((153, rows[153]['supplier']),)), (True, ()), 'row153_supplier')
    assert_equal(record_validation(153, action_packet.validate_supplier_root_context_coherence_v01, action_packet.validate_supplier_root_context_coherence_v01(rows[145]['supplier'], rows[153]['supplier']), ((145, rows[145]['supplier']), (153, rows[153]['supplier']))), (True, ()), 'row153_supplier_context')
    emit_receipt(153, 1, 'supplier', action_packet.build_root_decision_candidate_projection_v01, rows[153]['supplier'], input_bindings=((12, 'supplier', rows[12]['supplier'], rows[12]['supplier']), (145, 'supplier', rows[145]['supplier'], rows[145]['supplier']), (151, 'supplier', rows[151]['supplier'], rows[151]['supplier']), (152, 'supplier', rows[152]['supplier'], rows[152]['supplier'])))
    rows[154]['supplier'] = action_packet.build_supplier_root_bound_action_commit_packet_v02_projection_v01(canonical_projection=rows[145]['supplier'], root_decision_projection=rows[153]['supplier'])
    assert_equal(record_validation(154, action_packet.validate_supplier_root_bound_action_commit_packet_v02_projection_v01, action_packet.validate_supplier_root_bound_action_commit_packet_v02_projection_v01(rows[154]['supplier']), ((154, rows[154]['supplier']),)), (True, ()), 'row154_supplier')
    successor_packet_id = rows[154]['supplier'].packet_identity.packet_id
    assert_equal((successor_packet_id != rows[84]['supplier'].packet_identity.packet_id, rows[152]['supplier'].decision_id != rows[82]['supplier'].decision_id), (True, True), 'row154_fresh_authority')
    emit_receipt(154, 1, 'supplier', action_packet.build_supplier_root_bound_action_commit_packet_v02_projection_v01, rows[154]['supplier'], input_bindings=((82, 'supplier', rows[82]['supplier'], rows[82]['supplier']), (84, 'supplier', rows[84]['supplier'], rows[84]['supplier']), (145, 'supplier', rows[145]['supplier'], rows[145]['supplier']), (152, 'supplier', rows[152]['supplier'], rows[152]['supplier']), (153, 'supplier', rows[153]['supplier'], rows[153]['supplier'])))
    rows[155]['supplier'] = action_packet.record_action_packet_genesis_v01(rows[98]['supplier'], root_bound_genesis=rows[154]['supplier'], action_packet_transition_registry_profile=rows[85]['supplier'])
    assert_equal(record_validation(155, action_packet.validate_action_commit_packet_registry_v02, action_packet.validate_action_commit_packet_registry_v02(rows[155]['supplier']), ((155, rows[155]['supplier']),)), (True, ()), 'row155_supplier')
    assert_equal(repr(rows[98]['supplier']).encode('utf-8'), row098_registry_bytes, 'row155_row098_unchanged')
    emit_receipt(155, 1, 'supplier', action_packet.record_action_packet_genesis_v01, rows[155]['supplier'], input_bindings=((85, 'supplier', rows[85]['supplier'], rows[85]['supplier']), (98, 'supplier', rows[98]['supplier'], rows[98]['supplier']), (154, 'supplier', rows[154]['supplier'], rows[154]['supplier'])))
    rows[156]['supplier'] = action_packet.build_supersession_candidate_v01(owning_local_root_id=supplier_root_id, predecessor_packet_id=rows[84]['supplier'].packet_identity.packet_id, successor_packet_authorization_candidate_id=successor_candidate_id, stable_logical_intent_id=rows[145]['supplier'].logical_intent.root_owned_intent_id, idempotency_key=rows[145]['supplier'].idempotency_identity.idempotency_key, supersession_reason_class='RENEWAL', policy_fingerprint=rows[75]['supplier'].authority_policy_fingerprint)
    assert_equal(record_validation(156, action_packet.validate_supersession_candidate_v01, action_packet.validate_supersession_candidate_v01(rows[156]['supplier']), ((156, rows[156]['supplier']),)), (True, ()), 'row156_supplier')
    assert_equal(record_validation(156, action_packet.validate_supersession_candidate_against_packets_v01, action_packet.validate_supersession_candidate_against_packets_v01(rows[156]['supplier'], rows[84]['supplier'], rows[154]['supplier']), ((84, rows[84]['supplier']), (154, rows[154]['supplier']), (156, rows[156]['supplier']))), (True, ()), 'row156_supplier_context')
    emit_receipt(156, 1, 'supplier', action_packet.build_supersession_candidate_v01, rows[156]['supplier'], input_bindings=((75, 'supplier', rows[75]['supplier'], rows[75]['supplier']), (84, 'supplier', rows[84]['supplier'], rows[84]['supplier']), (145, 'supplier', rows[145]['supplier'], rows[145]['supplier']), (154, 'supplier', rows[154]['supplier'], rows[154]['supplier'])))
    supersession_candidate_id = rows[156]['supplier'].supersession_candidate_id
    supersession_actor = 'actor:g2f:supplier:supersession:v01'
    supersession_subject = 'action_supersession:g2f:supplier'
    rows[157]['supplier'] = semantic_work.build_semantic_work_request_v01(request_id=SHARED_REQUEST_ID, transaction_id=supplier_transaction_id, target_root_id=supplier_root_id, runtime_topology_ref=supersession_candidate_id, bounded_context_refs=(supersession_candidate_id,), permitted_actor_ids=(supersession_actor,), permitted_contribution_modes=('DETERMINISTIC',), requested_subjects=(supersession_subject,), required_evidence_classes=('SUPERSESSION_CANDIDATE_EVIDENCE',), forbidden_claims=('aggregate_authority', 'external_effect'))
    assert_equal(record_validation(157, semantic_work.validate_semantic_work_request_v01, semantic_work.validate_semantic_work_request_v01(rows[157]['supplier']), ((157, rows[157]['supplier']),)), (), 'row157_supplier')
    emit_receipt(157, 1, 'supplier', semantic_work.build_semantic_work_request_v01, rows[157]['supplier'], input_bindings=((5, 'supplier', rows[5]['supplier'], rows[5]['supplier']), (156, 'supplier', rows[156]['supplier'], rows[156]['supplier'])))
    rows[158]['supplier'] = semantic_work.build_evidence_binding_v01(evidence_id='evidence-binding:g2f:supplier:supersession:v01', evidence_ref=supersession_candidate_id, evidence_class='SUPERSESSION_CANDIDATE_EVIDENCE', source_component_id=supersession_actor, provenance_ref=supersession_candidate_id, evidence_state=semantic_work.EVIDENCE_STATE_PRESENT)
    emit_receipt(158, 1, 'supplier', semantic_work.build_evidence_binding_v01, rows[158]['supplier'], input_bindings=((156, 'supplier', rows[156]['supplier'], rows[156]['supplier']),))
    rows[159]['supplier'] = semantic_work.build_normalized_claim_v01(claim_id=supersession_candidate_id, subject=supersession_subject, predicate=action_packet.ROOT_DECISION_CLAIM_PREDICATE_SUPERSESSION_V01, object_or_value={'candidate_id': supersession_candidate_id, 'candidate_kind': 'SUPERSESSION'}, time_envelope_ref=rows[145]['supplier'].temporal_authority_fingerprint, provenance_refs=(supersession_candidate_id,), evidence_refs=(rows[158]['supplier'].evidence_id,), confidence_micros=1000000, source_role='deterministic_runtime', source_mode='DETERMINISTIC')
    emit_receipt(159, 1, 'supplier', semantic_work.build_normalized_claim_v01, rows[159]['supplier'], input_bindings=((145, 'supplier', rows[145]['supplier'], rows[145]['supplier']), (156, 'supplier', rows[156]['supplier'], rows[156]['supplier']), (158, 'supplier', rows[158]['supplier'], rows[158]['supplier'])))
    rows[160]['supplier'] = semantic_work.build_actor_contribution_v01(contribution_id='contribution:g2f:supplier:supersession:v01', request_id=rows[157]['supplier'].request_id, actor_id=supersession_actor, actor_role='deterministic_runtime', contribution_mode='DETERMINISTIC', bsep_projection_ref=rows[7]['supplier'].projection_id, scope=supersession_subject, bounded_context_refs=rows[157]['supplier'].bounded_context_refs, claims=(rows[159]['supplier'],), evidence_bindings=(rows[158]['supplier'],), constraint_bindings=(), uncertainty_bindings=(), requested_validators=('validator:g2f:supplier:supersession:v01',), forbidden_claims_observed=())
    assert_equal(record_validation(160, semantic_work.validate_actor_contribution_v01, semantic_work.validate_actor_contribution_v01(request=rows[157]['supplier'], contribution=rows[160]['supplier'], trust_profiles=rows[17]['supplier']), ((17, rows[17]['supplier']), (157, rows[157]['supplier']), (160, rows[160]['supplier']))), (), 'row160_supplier')
    emit_receipt(160, 1, 'supplier', semantic_work.build_actor_contribution_v01, rows[160]['supplier'], input_bindings=((7, 'supplier', rows[7]['supplier'], rows[7]['supplier']), (17, 'supplier', rows[17]['supplier'], rows[17]['supplier']), (157, 'supplier', rows[157]['supplier'], rows[157]['supplier']), (158, 'supplier', rows[158]['supplier'], rows[158]['supplier']), (159, 'supplier', rows[159]['supplier'], rows[159]['supplier'])))
    rows[161]['supplier'] = semantic_work.build_root_review_packet_from_contributions_v01(request=rows[157]['supplier'], contributions=(rows[160]['supplier'],), trust_profiles=rows[17]['supplier'])
    assert_equal(record_validation(161, semantic_work.validate_root_review_packet_v01, semantic_work.validate_root_review_packet_v01(request=rows[157]['supplier'], contributions=(rows[160]['supplier'],), packet=rows[161]['supplier'], trust_profiles=rows[17]['supplier']), ((17, rows[17]['supplier']), (157, rows[157]['supplier']), (160, rows[160]['supplier']), (161, rows[161]['supplier']))), (), 'row161_supplier')
    emit_receipt(161, 1, 'supplier', semantic_work.build_root_review_packet_from_contributions_v01, rows[161]['supplier'], input_bindings=((17, 'supplier', rows[17]['supplier'], rows[17]['supplier']), (157, 'supplier', rows[157]['supplier'], rows[157]['supplier']), (160, 'supplier', rows[160]['supplier'], rows[160]['supplier'])))
    rows[162]['supplier'] = root_decision.build_root_decision_input_v01(transaction_id=supplier_transaction_id, target_root_id=supplier_root_id, root_review_packet=rows[161]['supplier'], post_vv_bundle={'bundle_id': 'post-vv:g2f:supplier:supersession:v01', 'hard_failure_reasons': [], 'post_vv_passed': True, 'provided_evidence_refs': [supersession_candidate_id], 'rejected_candidate_ids': [], 'required_evidence_refs': [supersession_candidate_id], 'validated_candidate_ids': [supersession_candidate_id]}, gt_advisory={'actor_role': 'gt', 'advisory_id': 'gt:g2f:supplier:supersession:v01', 'advisory_only': True, 'attempted_effect': 'CREATE_ROOT_DECISION', 'candidate_ids': [supersession_candidate_id], 'creates_final_output': False, 'requests_effect': False, 'score_micros_by_candidate': {supersession_candidate_id: 1000000}, 'selected_candidate_id': supersession_candidate_id, 'source_artifact_type': 'GTAdvisoryReport', 'source_lifecycle_state': 'VALIDATED', 'target_artifact_type': 'RootDecision'}, policy_state={'policy_id': rows[75]['supplier'].authority_policy_fingerprint, 'identity_passed': True, 'scope_passed': True, 'hard_policy_passed': True, 'allow_accept': True, 'conflict_policy': 'DEFER', 'no_candidate_policy': 'NO_UPDATE'}, permission_state={'permission_required': False, 'user_permission_present': False, 'permission_scope_valid': True, 'permission_ref': None}, temporal_state={'temporal_valid': True, 'expired': False, 'not_before_satisfied': True, 'time_envelope_ref': rows[75]['supplier'].temporal_authority_fingerprint}, conflict_state={'material_unresolved_conflict': False, 'conflict_set_ids': []}, prior_root_state={'prior_decision_id': rows[82]['supplier'].decision_id, 'prior_decision': 'ACCEPT', 'prior_selected_candidate_id': rows[75]['supplier'].authorization_candidate.root_packet_authorization_candidate_id})
    assert_equal(record_validation(162, root_decision.validate_root_decision_input_v01, root_decision.validate_root_decision_input_v01(kernel=rows[12]['supplier'], decision_input=rows[162]['supplier']), ((12, rows[12]['supplier']), (162, rows[162]['supplier']))), (), 'row162_supplier')
    emit_receipt(162, 1, 'supplier', root_decision.build_root_decision_input_v01, rows[162]['supplier'], input_bindings=((5, 'supplier', rows[5]['supplier'], rows[5]['supplier']), (12, 'supplier', rows[12]['supplier'], rows[12]['supplier']), (75, 'supplier', rows[75]['supplier'], rows[75]['supplier']), (82, 'supplier', rows[82]['supplier'], rows[82]['supplier']), (156, 'supplier', rows[156]['supplier'], rows[156]['supplier']), (161, 'supplier', rows[161]['supplier'], rows[161]['supplier'])))
    rows[163]['supplier'] = root_decision.decide_root_v01(kernel=rows[12]['supplier'], decision_input=rows[162]['supplier'])
    assert_equal(record_validation(163, root_decision.validate_root_decision_result_v01, root_decision.validate_root_decision_result_v01(kernel=rows[12]['supplier'], decision_input=rows[162]['supplier'], result=rows[163]['supplier']), ((12, rows[12]['supplier']), (162, rows[162]['supplier']), (163, rows[163]['supplier']))), (), 'row163_supplier')
    assert_equal((rows[163]['supplier'].decision, rows[163]['supplier'].reason_code, rows[163]['supplier'].selected_candidate_id, rows[163]['supplier'].root_commit_created, rows[163]['supplier'].permission_created, rows[163]['supplier'].final_output_created, rows[163]['supplier'].effect_requested), ('ACCEPT', 'validated_candidate_accepted', supersession_candidate_id, True, False, False, False), 'row163_outcome')
    emit_receipt(163, 1, 'supplier', root_decision.decide_root_v01, rows[163]['supplier'], input_bindings=((12, 'supplier', rows[12]['supplier'], rows[12]['supplier']), (156, 'supplier', rows[156]['supplier'], rows[156]['supplier']), (162, 'supplier', rows[162]['supplier'], rows[162]['supplier'])))
    rows[164]['supplier'] = action_packet.build_root_decision_candidate_projection_v01(candidate_kind=action_packet.ROOT_DECISION_CANDIDATE_KIND_SUPERSESSION_V01, projected_candidate_id=supersession_candidate_id, root_decision_kernel=rows[12]['supplier'], root_decision_input=rows[162]['supplier'], root_decision_result=rows[163]['supplier'])
    assert_equal(record_validation(164, action_packet.validate_root_decision_candidate_projection_v01, action_packet.validate_root_decision_candidate_projection_v01(rows[164]['supplier']), ((164, rows[164]['supplier']),)), (True, ()), 'row164_supplier')
    assert_equal(record_validation(164, action_packet.validate_supersession_root_context_coherence_v01, action_packet.validate_supersession_root_context_coherence_v01(rows[156]['supplier'], rows[164]['supplier'], rows[84]['supplier'], rows[154]['supplier']), ((84, rows[84]['supplier']), (154, rows[154]['supplier']), (156, rows[156]['supplier']), (164, rows[164]['supplier']))), (True, ()), 'row164_supplier_context')
    emit_receipt(164, 1, 'supplier', action_packet.build_root_decision_candidate_projection_v01, rows[164]['supplier'], input_bindings=((12, 'supplier', rows[12]['supplier'], rows[12]['supplier']), (84, 'supplier', rows[84]['supplier'], rows[84]['supplier']), (154, 'supplier', rows[154]['supplier'], rows[154]['supplier']), (156, 'supplier', rows[156]['supplier'], rows[156]['supplier']), (162, 'supplier', rows[162]['supplier'], rows[162]['supplier']), (163, 'supplier', rows[163]['supplier'], rows[163]['supplier'])))
    rows[165]['supplier'] = action_packet.build_accepted_supersession_binding_v01(candidate=rows[156]['supplier'], root_projection=rows[164]['supplier'], predecessor=rows[84]['supplier'], successor=rows[154]['supplier'])
    assert_equal(record_validation(165, action_packet.validate_accepted_supersession_binding_v01, action_packet.validate_accepted_supersession_binding_v01(rows[165]['supplier']), ((165, rows[165]['supplier']),)), (True, ()), 'row165_supplier')
    assert_equal(record_validation(165, action_packet.validate_action_packet_renewal_relationship_v01, action_packet.validate_action_packet_renewal_relationship_v01(rows[84]['supplier'], rows[154]['supplier'], rows[156]['supplier'], rows[165]['supplier'], root_projection=rows[164]['supplier']), ((84, rows[84]['supplier']), (154, rows[154]['supplier']), (156, rows[156]['supplier']), (164, rows[164]['supplier']), (165, rows[165]['supplier']))), (True, ()), 'row165_renewal')
    emit_receipt(165, 1, 'supplier', action_packet.build_accepted_supersession_binding_v01, rows[165]['supplier'], input_bindings=((84, 'supplier', rows[84]['supplier'], rows[84]['supplier']), (154, 'supplier', rows[154]['supplier'], rows[154]['supplier']), (156, 'supplier', rows[156]['supplier'], rows[156]['supplier']), (164, 'supplier', rows[164]['supplier'], rows[164]['supplier'])))
    supersession_binding_digest = rows[165]['supplier'].accepted_supersession_binding_id.split(':', 1)[1]
    atomic_supersession_time = PACKET_EVALUATION_TIME + 3
    atomic_supersession_source = 'g2f_deterministic_logical_time'
    atomic_supersession_context = 'evaluation_context:g2f:supplier:supersession:v01'
    rows[166]['supplier'] = action_packet.build_action_invalidation_evidence_v01(source_invalidation_event_ref=rows[129]['supplier'].invalidation_evidence_id, packet_id=rows[84]['supplier'].packet_identity.packet_id, dependency_id='dependency:root_supersession', invalidation_class='ROOT_SUPERSESSION', evidence_ref=rows[165]['supplier'].accepted_supersession_binding_id, evidence_sha256=supersession_binding_digest, observed_status='OBSERVED_ROOT_SUPERSESSION', time_envelope_id=rows[129]['supplier'].time_envelope_id, freshness_policy_id=rows[129]['supplier'].freshness_policy_id, owning_local_root_id=supplier_root_id, accepted_by_local_root_id=supplier_root_id, acceptance_root_decision_id=rows[163]['supplier'].decision_id, acceptance_root_decision_hash=rows[164]['supplier'].source_root_decision_hash, authority_effect='ROOT_SUPERSESSION', root_decision_ref=rows[163]['supplier'].decision_id, evaluation_time=atomic_supersession_time, evaluation_time_source=atomic_supersession_source, evaluation_context_id=atomic_supersession_context)
    assert_equal(record_validation(166, action_packet.validate_action_invalidation_evidence_v01, action_packet.validate_action_invalidation_evidence_v01(rows[166]['supplier']), ((166, rows[166]['supplier']),)), (True, ()), 'row166_supplier')
    assert_equal(record_validation(166, action_packet.validate_action_invalidation_evidence_against_packet_v01, action_packet.validate_action_invalidation_evidence_against_packet_v01(rows[166]['supplier'], rows[84]['supplier'], supersession_candidate=rows[156]['supplier'], supersession_root_projection=rows[164]['supplier'], supersession_successor=rows[154]['supplier'], accepted_supersession_binding=rows[165]['supplier']), ((84, rows[84]['supplier']), (154, rows[154]['supplier']), (156, rows[156]['supplier']), (164, rows[164]['supplier']), (165, rows[165]['supplier']), (166, rows[166]['supplier']))), (True, ()), 'row166_supplier_context')
    emit_receipt(166, 1, 'supplier', action_packet.build_action_invalidation_evidence_v01, rows[166]['supplier'], input_bindings=((84, 'supplier', rows[84]['supplier'], rows[84]['supplier']), (129, 'supplier', rows[129]['supplier'], rows[129]['supplier']), (154, 'supplier', rows[154]['supplier'], rows[154]['supplier']), (156, 'supplier', rows[156]['supplier'], rows[156]['supplier']), (163, 'supplier', rows[163]['supplier'], rows[163]['supplier']), (164, 'supplier', rows[164]['supplier'], rows[164]['supplier']), (165, 'supplier', rows[165]['supplier'], rows[165]['supplier'])))
    successor_activation_rule = transition_registry.lookup_action_packet_transition_rule_v01(registry=rows[85]['supplier'], transition_rule_id='g2a_t01_activate_root_authorization')
    successor_activation_material = {'packet_genesis_valid': successor_packet_id, 'source_root_authorization_valid': rows[152]['supplier'].decision_id, 'idempotency_acquisition_valid': rows[145]['supplier'].idempotency_identity.idempotency_key}
    successor_activation_bindings = []
    for component_ordinal, evidence_code in enumerate(successor_activation_rule.required_evidence_codes, start=1):
        evidence_ref = successor_activation_material[evidence_code]
        binding = action_packet.build_transition_evidence_binding_v01(action_packet_transition_registry_profile=rows[85]['supplier'], transition_rule_id=successor_activation_rule.transition_rule_id, evidence_code=evidence_code, evidence_ref=evidence_ref, evidence_sha256=hashlib.sha256(canonical_json_bytes_v01(evidence_ref)).hexdigest(), validator_profile_id='validator:g2f:packet-transition:v01')
        assert_equal(record_validation(167, action_packet.validate_transition_evidence_binding_v01, action_packet.validate_transition_evidence_binding_v01(binding, action_packet_transition_registry_profile=rows[85]['supplier'], transition_rule_id=successor_activation_rule.transition_rule_id), ((85, rows[85]['supplier']),)), (True, ()), f'row167_{component_ordinal}')
        successor_activation_bindings.append(binding)
        emit_component(167, component_ordinal, 'supplier', action_packet.build_transition_evidence_binding_v01, (evidence_ref,), binding, evidence_code)
    rows[167]['supplier'] = tuple(successor_activation_bindings)
    assert_equal((len(rows[167]['supplier']), tuple((item.evidence_code for item in rows[167]['supplier']))), (3, successor_activation_rule.required_evidence_codes), 'row167_order')
    emit_receipt(167, 1, 'supplier', action_packet.build_transition_evidence_binding_v01, rows[167]['supplier'], input_bindings=((85, 'supplier', rows[85]['supplier'], rows[85]['supplier']), (145, 'supplier', rows[145]['supplier'], rows[145]['supplier']), (152, 'supplier', rows[152]['supplier'], rows[152]['supplier']), (154, 'supplier', rows[154]['supplier'], rows[154]['supplier'])))
    rows[168]['supplier'] = action_packet.build_action_packet_transition_event_v01(action_packet_transition_registry_profile=rows[85]['supplier'], transition_rule_id=successor_activation_rule.transition_rule_id, packet_id=successor_packet_id, idempotency_key=rows[145]['supplier'].idempotency_identity.idempotency_key, previous_transition_event_id=None, owning_local_root_id=supplier_root_id, root_decision_ref=rows[152]['supplier'].decision_id, transition_evidence_bindings=rows[167]['supplier'], dependency_set_candidate_fingerprint=rows[145]['supplier'].dependency_set_candidate_fingerprint, temporal_authority_fingerprint=rows[145]['supplier'].temporal_authority_fingerprint, evaluation_time=rows[166]['supplier'].evaluation_time, evaluation_time_source=rows[166]['supplier'].evaluation_time_source, evaluation_context_id=rows[166]['supplier'].evaluation_context_id, execution_attempt_identity=None, receipt_ref=None)
    assert_equal(record_validation(168, action_packet.validate_action_packet_transition_event_v01, action_packet.validate_action_packet_transition_event_v01(rows[168]['supplier'], action_packet_transition_registry_profile=rows[85]['supplier']), ((85, rows[85]['supplier']), (168, rows[168]['supplier']))), (True, ()), 'row168_supplier')
    emit_receipt(168, 1, 'supplier', action_packet.build_action_packet_transition_event_v01, rows[168]['supplier'], input_bindings=((85, 'supplier', rows[85]['supplier'], rows[85]['supplier']), (145, 'supplier', rows[145]['supplier'], rows[145]['supplier']), (152, 'supplier', rows[152]['supplier'], rows[152]['supplier']), (154, 'supplier', rows[154]['supplier'], rows[154]['supplier']), (166, 'supplier', rows[166]['supplier'], rows[166]['supplier']), (167, 'supplier', rows[167]['supplier'], rows[167]['supplier'])))
    predecessor_supersession_rule = transition_registry.lookup_action_packet_transition_rule_v01(registry=rows[85]['supplier'], transition_rule_id='g2a_t22_pending_supersede')
    predecessor_supersession_material = {'successor_packet_valid': (successor_packet_id, successor_packet_id.split(':', 1)[1], 'action_commit_packet_identity_profile_v01'), 'accepted_supersession_binding_valid': (rows[165]['supplier'].accepted_supersession_binding_id, supersession_binding_digest, 'accepted_supersession_binding_v01'), 'predecessor_binding_valid': (rows[84]['supplier'].packet_identity.packet_id, rows[84]['supplier'].packet_identity.packet_id.split(':', 1)[1], 'action_commit_packet_identity_profile_v01'), 'adapter_not_called': (rows[95]['supplier'].execution_attempt_id, rows[95]['supplier'].execution_attempt_id.split(':', 1)[1], action_packet.EXECUTION_ATTEMPT_IDENTITY_PROFILE_ID_V01), 'idempotency_transfer_valid': (rows[90]['supplier'].idempotency_disposition_event_id, rows[90]['supplier'].idempotency_disposition_event_id.split(':', 1)[1], action_packet.IDEMPOTENCY_DISPOSITION_EVENT_PROFILE_ID_V01)}
    predecessor_supersession_bindings = []
    for component_ordinal, evidence_code in enumerate(predecessor_supersession_rule.required_evidence_codes, start=1):
        evidence_ref, evidence_hash, validator_profile = predecessor_supersession_material[evidence_code]
        binding = action_packet.build_transition_evidence_binding_v01(action_packet_transition_registry_profile=rows[85]['supplier'], transition_rule_id=predecessor_supersession_rule.transition_rule_id, evidence_code=evidence_code, evidence_ref=evidence_ref, evidence_sha256=evidence_hash, validator_profile_id=validator_profile)
        assert_equal(record_validation(169, action_packet.validate_transition_evidence_binding_v01, action_packet.validate_transition_evidence_binding_v01(binding, action_packet_transition_registry_profile=rows[85]['supplier'], transition_rule_id=predecessor_supersession_rule.transition_rule_id), ((85, rows[85]['supplier']),)), (True, ()), f'row169_{component_ordinal}')
        predecessor_supersession_bindings.append(binding)
        emit_component(169, component_ordinal, 'supplier', action_packet.build_transition_evidence_binding_v01, (evidence_ref,), binding, evidence_code)
    rows[169]['supplier'] = tuple(predecessor_supersession_bindings)
    assert_equal((len(rows[169]['supplier']), tuple((item.evidence_code for item in rows[169]['supplier']))), (5, predecessor_supersession_rule.required_evidence_codes), 'row169_order')
    emit_receipt(169, 1, 'supplier', action_packet.build_transition_evidence_binding_v01, rows[169]['supplier'], input_bindings=((84, 'supplier', rows[84]['supplier'], rows[84]['supplier']), (85, 'supplier', rows[85]['supplier'], rows[85]['supplier']), (90, 'supplier', rows[90]['supplier'], rows[90]['supplier']), (95, 'supplier', rows[95]['supplier'], rows[95]['supplier']), (154, 'supplier', rows[154]['supplier'], rows[154]['supplier']), (165, 'supplier', rows[165]['supplier'], rows[165]['supplier'])))
    rows[170]['supplier'] = action_packet.build_action_packet_transition_event_v01(action_packet_transition_registry_profile=rows[85]['supplier'], transition_rule_id=predecessor_supersession_rule.transition_rule_id, packet_id=rows[84]['supplier'].packet_identity.packet_id, idempotency_key=rows[75]['supplier'].idempotency_identity.idempotency_key, previous_transition_event_id=rows[97]['supplier'].transition_event_id, owning_local_root_id=supplier_root_id, root_decision_ref=rows[163]['supplier'].decision_id, transition_evidence_bindings=rows[169]['supplier'], dependency_set_candidate_fingerprint=rows[75]['supplier'].dependency_set_candidate_fingerprint, temporal_authority_fingerprint=rows[75]['supplier'].temporal_authority_fingerprint, evaluation_time=rows[166]['supplier'].evaluation_time, evaluation_time_source=rows[166]['supplier'].evaluation_time_source, evaluation_context_id=rows[166]['supplier'].evaluation_context_id, execution_attempt_identity=None, receipt_ref=None)
    assert_equal(record_validation(170, action_packet.validate_action_packet_transition_event_v01, action_packet.validate_action_packet_transition_event_v01(rows[170]['supplier'], action_packet_transition_registry_profile=rows[85]['supplier']), ((85, rows[85]['supplier']), (170, rows[170]['supplier']))), (True, ()), 'row170_supplier')
    emit_receipt(170, 1, 'supplier', action_packet.build_action_packet_transition_event_v01, rows[170]['supplier'], input_bindings=((75, 'supplier', rows[75]['supplier'], rows[75]['supplier']), (84, 'supplier', rows[84]['supplier'], rows[84]['supplier']), (85, 'supplier', rows[85]['supplier'], rows[85]['supplier']), (97, 'supplier', rows[97]['supplier'], rows[97]['supplier']), (163, 'supplier', rows[163]['supplier'], rows[163]['supplier']), (166, 'supplier', rows[166]['supplier'], rows[166]['supplier']), (169, 'supplier', rows[169]['supplier'], rows[169]['supplier'])))
    transfer_evidence_refs = tuple(sorted((rows[165]['supplier'].accepted_supersession_binding_id, rows[84]['supplier'].canonical_projection.logical_intent.root_owned_intent_id, rows[152]['supplier'].decision_id), key=lambda item: item.encode('utf-8')))
    rows[171]['supplier'] = action_packet.build_idempotency_disposition_event_v01(idempotency_key=rows[145]['supplier'].idempotency_identity.idempotency_key, event_class='TRANSFER_RENEWAL', from_disposition='RESERVED', to_disposition='RESERVED', from_owner_packet_id=rows[84]['supplier'].packet_identity.packet_id, to_owner_packet_id=successor_packet_id, previous_disposition_event_id=rows[90]['supplier'].idempotency_disposition_event_id, cause_transition_event_ids=(rows[170]['supplier'].transition_event_id, rows[168]['supplier'].transition_event_id), root_decision_ref=rows[152]['supplier'].decision_id, predecessor_packet_id=rows[84]['supplier'].packet_identity.packet_id, successor_packet_id=successor_packet_id, evidence_refs=transfer_evidence_refs, evaluation_time=rows[166]['supplier'].evaluation_time, evaluation_time_source=rows[166]['supplier'].evaluation_time_source, evaluation_context_id=rows[166]['supplier'].evaluation_context_id)
    assert_equal(record_validation(171, action_packet.validate_idempotency_disposition_event_v01, action_packet.validate_idempotency_disposition_event_v01(rows[171]['supplier']), ((171, rows[171]['supplier']),)), (True, ()), 'row171_supplier')
    assert_equal(record_validation(171, action_packet.validate_idempotency_disposition_history_v01, action_packet.validate_idempotency_disposition_history_v01(rows[98]['supplier'].idempotency_disposition_events + (rows[171]['supplier'],)), ((98, rows[98]['supplier'].idempotency_disposition_events), (171, rows[171]['supplier']))), (True, ()), 'row171_history')
    assert_equal((rows[171]['supplier'].root_decision_ref, rows[171]['supplier'].cause_transition_event_ids, rows[171]['supplier'].evidence_refs), (rows[152]['supplier'].decision_id, (rows[170]['supplier'].transition_event_id, rows[168]['supplier'].transition_event_id), transfer_evidence_refs), 'row171_exact_geometry')
    emit_receipt(171, 1, 'supplier', action_packet.build_idempotency_disposition_event_v01, rows[171]['supplier'], input_bindings=((84, 'supplier', rows[84]['supplier'], rows[84]['supplier']), (90, 'supplier', rows[90]['supplier'], rows[90]['supplier']), (98, 'supplier', rows[98]['supplier'], rows[98]['supplier']), (145, 'supplier', rows[145]['supplier'], rows[145]['supplier']), (152, 'supplier', rows[152]['supplier'], rows[152]['supplier']), (154, 'supplier', rows[154]['supplier'], rows[154]['supplier']), (165, 'supplier', rows[165]['supplier'], rows[165]['supplier']), (166, 'supplier', rows[166]['supplier'], rows[166]['supplier']), (168, 'supplier', rows[168]['supplier'], rows[168]['supplier']), (170, 'supplier', rows[170]['supplier'], rows[170]['supplier'])))
    rows[172]['supplier'] = action_packet.record_action_packet_supersession_v01(rows[155]['supplier'], predecessor_packet_id=rows[84]['supplier'].packet_identity.packet_id, successor_packet_id=successor_packet_id, supersession_candidate=rows[156]['supplier'], supersession_root_projection=rows[164]['supplier'], accepted_supersession_binding=rows[165]['supplier'], invalidation_evidence=rows[166]['supplier'], successor_activation_event=rows[168]['supplier'], disposition_event=rows[171]['supplier'], action_packet_transition_registry_profile=rows[85]['supplier'], predecessor_supersession_event=rows[170]['supplier'])
    assert_equal(record_validation(172, action_packet.validate_action_commit_packet_registry_v02, action_packet.validate_action_commit_packet_registry_v02(rows[172]['supplier']), ((172, rows[172]['supplier']),)), (True, ()), 'row172_registry')
    predecessor_superseded_state = action_packet.derive_action_packet_lifecycle_state_v01(rows[172]['supplier'], packet_id=rows[84]['supplier'].packet_identity.packet_id, action_packet_transition_registry_profile=rows[85]['supplier'])
    successor_authorized_state = action_packet.derive_action_packet_lifecycle_state_v01(rows[172]['supplier'], packet_id=successor_packet_id, action_packet_transition_registry_profile=rows[85]['supplier'])
    assert_equal((predecessor_superseded_state.lifecycle_state, successor_authorized_state.lifecycle_state, successor_authorized_state.idempotency_disposition, successor_authorized_state.reservation_owner_packet_id), ('SUPERSEDED', 'ROOT_AUTHORIZED', 'RESERVED', successor_packet_id), 'row172_atomic_state')
    assert_equal(repr(rows[98]['supplier']).encode('utf-8'), row098_registry_bytes, 'row172_row098_unchanged')
    emit_receipt(172, 1, 'supplier', action_packet.record_action_packet_supersession_v01, rows[172]['supplier'], input_bindings=((84, 'supplier', rows[84]['supplier'], rows[84]['supplier']), (85, 'supplier', rows[85]['supplier'], rows[85]['supplier']), (98, 'supplier', rows[98]['supplier'], rows[98]['supplier']), (154, 'supplier', rows[154]['supplier'], rows[154]['supplier']), (155, 'supplier', rows[155]['supplier'], rows[155]['supplier']), (156, 'supplier', rows[156]['supplier'], rows[156]['supplier']), (164, 'supplier', rows[164]['supplier'], rows[164]['supplier']), (165, 'supplier', rows[165]['supplier'], rows[165]['supplier']), (166, 'supplier', rows[166]['supplier'], rows[166]['supplier']), (168, 'supplier', rows[168]['supplier'], rows[168]['supplier']), (170, 'supplier', rows[170]['supplier'], rows[170]['supplier']), (171, 'supplier', rows[171]['supplier'], rows[171]['supplier'])))
    successor_queue_rule = transition_registry.lookup_action_packet_transition_rule_v01(registry=rows[85]['supplier'], transition_rule_id='g2a_t02_queue')
    successor_queue_material = {'transition_history_valid': rows[168]['supplier'].transition_event_id, 'temporal_authority_valid': rows[154]['supplier'].canonical_projection.temporal_authority_fingerprint, 'mandatory_dependencies_current': rows[154]['supplier'].canonical_projection.dependency_set_candidate_fingerprint, 'idempotency_reservation_owned': rows[171]['supplier'].idempotency_disposition_event_id}
    successor_queue_bindings = []
    for component_ordinal, evidence_code in enumerate(successor_queue_rule.required_evidence_codes, start=1):
        evidence_ref = successor_queue_material[evidence_code]
        binding = action_packet.build_transition_evidence_binding_v01(action_packet_transition_registry_profile=rows[85]['supplier'], transition_rule_id=successor_queue_rule.transition_rule_id, evidence_code=evidence_code, evidence_ref=evidence_ref, evidence_sha256=hashlib.sha256(canonical_json_bytes_v01(evidence_ref)).hexdigest(), validator_profile_id='validator:g2f:packet-transition:v01')
        assert_equal(record_validation(173, action_packet.validate_transition_evidence_binding_v01, action_packet.validate_transition_evidence_binding_v01(binding, action_packet_transition_registry_profile=rows[85]['supplier'], transition_rule_id=successor_queue_rule.transition_rule_id), ((85, rows[85]['supplier']),)), (True, ()), f'row173_{component_ordinal}')
        successor_queue_bindings.append(binding)
        emit_component(173, component_ordinal, 'supplier', action_packet.build_transition_evidence_binding_v01, (evidence_ref,), binding, evidence_code)
    rows[173]['supplier'] = tuple(successor_queue_bindings)
    assert_equal((len(rows[173]['supplier']), tuple((item.evidence_code for item in rows[173]['supplier']))), (4, successor_queue_rule.required_evidence_codes), 'row173_order')
    emit_receipt(173, 1, 'supplier', action_packet.build_transition_evidence_binding_v01, rows[173]['supplier'], input_bindings=((85, 'supplier', rows[85]['supplier'], rows[85]['supplier']), (154, 'supplier', rows[154]['supplier'], rows[154]['supplier']), (168, 'supplier', rows[168]['supplier'], rows[168]['supplier']), (171, 'supplier', rows[171]['supplier'], rows[171]['supplier'])))
    successor_queue_context = 'evaluation_context:g2f:supplier:successor:queue:v01'
    rows[174]['supplier'] = action_packet.build_action_packet_transition_event_v01(action_packet_transition_registry_profile=rows[85]['supplier'], transition_rule_id=successor_queue_rule.transition_rule_id, packet_id=successor_packet_id, idempotency_key=rows[145]['supplier'].idempotency_identity.idempotency_key, previous_transition_event_id=rows[168]['supplier'].transition_event_id, owning_local_root_id=supplier_root_id, root_decision_ref=None, transition_evidence_bindings=rows[173]['supplier'], dependency_set_candidate_fingerprint=rows[145]['supplier'].dependency_set_candidate_fingerprint, temporal_authority_fingerprint=rows[145]['supplier'].temporal_authority_fingerprint, evaluation_time=atomic_supersession_time + 1, evaluation_time_source=atomic_supersession_source, evaluation_context_id=successor_queue_context, execution_attempt_identity=None, receipt_ref=None)
    assert_equal(record_validation(174, action_packet.validate_action_packet_transition_event_v01, action_packet.validate_action_packet_transition_event_v01(rows[174]['supplier'], action_packet_transition_registry_profile=rows[85]['supplier']), ((85, rows[85]['supplier']), (174, rows[174]['supplier']))), (True, ()), 'row174_supplier')
    emit_receipt(174, 1, 'supplier', action_packet.build_action_packet_transition_event_v01, rows[174]['supplier'], input_bindings=((85, 'supplier', rows[85]['supplier'], rows[85]['supplier']), (145, 'supplier', rows[145]['supplier'], rows[145]['supplier']), (154, 'supplier', rows[154]['supplier'], rows[154]['supplier']), (168, 'supplier', rows[168]['supplier'], rows[168]['supplier']), (173, 'supplier', rows[173]['supplier'], rows[173]['supplier'])))
    rows[175]['supplier'] = action_packet.append_action_packet_lifecycle_transition_v01(rows[172]['supplier'], packet_id=successor_packet_id, transition_event=rows[174]['supplier'], action_packet_transition_registry_profile=rows[85]['supplier'])
    assert_equal(record_validation(175, action_packet.validate_action_commit_packet_registry_v02, action_packet.validate_action_commit_packet_registry_v02(rows[175]['supplier']), ((175, rows[175]['supplier']),)), (True, ()), 'row175_registry')
    assert_equal(action_packet.derive_action_packet_lifecycle_state_v01(rows[175]['supplier'], packet_id=successor_packet_id, action_packet_transition_registry_profile=rows[85]['supplier']).lifecycle_state, 'QUEUED', 'row175_state')
    emit_receipt(175, 1, 'supplier', action_packet.append_action_packet_lifecycle_transition_v01, rows[175]['supplier'], input_bindings=((85, 'supplier', rows[85]['supplier'], rows[85]['supplier']), (154, 'supplier', rows[154]['supplier'], rows[154]['supplier']), (172, 'supplier', rows[172]['supplier'], rows[172]['supplier']), (174, 'supplier', rows[174]['supplier'], rows[174]['supplier'])))
    successor_pending_context = 'evaluation_context:g2f:supplier:successor:pending:v01'
    rows[176]['supplier'] = action_packet.build_action_execution_attempt_identity_v01(packet_id=successor_packet_id, idempotency_key=rows[145]['supplier'].idempotency_identity.idempotency_key, attempt_ordinal=1, evaluation_context_id=successor_pending_context)
    assert_equal(record_validation(176, action_packet.validate_action_execution_attempt_identity_v01, action_packet.validate_action_execution_attempt_identity_v01(rows[176]['supplier']), ((176, rows[176]['supplier']),)), (True, ()), 'row176_supplier')
    emit_receipt(176, 1, 'supplier', action_packet.build_action_execution_attempt_identity_v01, rows[176]['supplier'], input_bindings=((145, 'supplier', rows[145]['supplier'], rows[145]['supplier']), (154, 'supplier', rows[154]['supplier'], rows[154]['supplier'])))
    successor_pending_rule = transition_registry.lookup_action_packet_transition_rule_v01(registry=rows[85]['supplier'], transition_rule_id='g2a_t03_pending')
    successor_pending_material = {'immediate_prefulfillment_validation_pass': rows[176]['supplier'].execution_attempt_id, 'transition_history_valid': rows[174]['supplier'].transition_event_id, 'idempotency_reservation_owned': rows[171]['supplier'].idempotency_disposition_event_id}
    successor_pending_bindings = []
    for component_ordinal, evidence_code in enumerate(successor_pending_rule.required_evidence_codes, start=1):
        evidence_ref = successor_pending_material[evidence_code]
        binding = action_packet.build_transition_evidence_binding_v01(action_packet_transition_registry_profile=rows[85]['supplier'], transition_rule_id=successor_pending_rule.transition_rule_id, evidence_code=evidence_code, evidence_ref=evidence_ref, evidence_sha256=hashlib.sha256(canonical_json_bytes_v01(evidence_ref)).hexdigest(), validator_profile_id='validator:g2f:packet-transition:v01')
        assert_equal(record_validation(177, action_packet.validate_transition_evidence_binding_v01, action_packet.validate_transition_evidence_binding_v01(binding, action_packet_transition_registry_profile=rows[85]['supplier'], transition_rule_id=successor_pending_rule.transition_rule_id), ((85, rows[85]['supplier']),)), (True, ()), f'row177_{component_ordinal}')
        successor_pending_bindings.append(binding)
        emit_component(177, component_ordinal, 'supplier', action_packet.build_transition_evidence_binding_v01, (evidence_ref,), binding, evidence_code)
    rows[177]['supplier'] = tuple(successor_pending_bindings)
    assert_equal((len(rows[177]['supplier']), tuple((item.evidence_code for item in rows[177]['supplier']))), (3, successor_pending_rule.required_evidence_codes), 'row177_order')
    emit_receipt(177, 1, 'supplier', action_packet.build_transition_evidence_binding_v01, rows[177]['supplier'], input_bindings=((85, 'supplier', rows[85]['supplier'], rows[85]['supplier']), (171, 'supplier', rows[171]['supplier'], rows[171]['supplier']), (174, 'supplier', rows[174]['supplier'], rows[174]['supplier']), (176, 'supplier', rows[176]['supplier'], rows[176]['supplier'])))
    rows[178]['supplier'] = action_packet.build_action_packet_transition_event_v01(action_packet_transition_registry_profile=rows[85]['supplier'], transition_rule_id=successor_pending_rule.transition_rule_id, packet_id=successor_packet_id, idempotency_key=rows[145]['supplier'].idempotency_identity.idempotency_key, previous_transition_event_id=rows[174]['supplier'].transition_event_id, owning_local_root_id=supplier_root_id, root_decision_ref=None, transition_evidence_bindings=rows[177]['supplier'], dependency_set_candidate_fingerprint=rows[145]['supplier'].dependency_set_candidate_fingerprint, temporal_authority_fingerprint=rows[145]['supplier'].temporal_authority_fingerprint, evaluation_time=atomic_supersession_time + 2, evaluation_time_source=atomic_supersession_source, evaluation_context_id=successor_pending_context, execution_attempt_identity=rows[176]['supplier'], receipt_ref=None)
    assert_equal(record_validation(178, action_packet.validate_action_packet_transition_event_v01, action_packet.validate_action_packet_transition_event_v01(rows[178]['supplier'], action_packet_transition_registry_profile=rows[85]['supplier']), ((85, rows[85]['supplier']), (178, rows[178]['supplier']))), (True, ()), 'row178_supplier')
    emit_receipt(178, 1, 'supplier', action_packet.build_action_packet_transition_event_v01, rows[178]['supplier'], input_bindings=((85, 'supplier', rows[85]['supplier'], rows[85]['supplier']), (145, 'supplier', rows[145]['supplier'], rows[145]['supplier']), (154, 'supplier', rows[154]['supplier'], rows[154]['supplier']), (174, 'supplier', rows[174]['supplier'], rows[174]['supplier']), (176, 'supplier', rows[176]['supplier'], rows[176]['supplier']), (177, 'supplier', rows[177]['supplier'], rows[177]['supplier'])))
    rows[179]['supplier'] = action_packet.append_action_packet_lifecycle_transition_v01(rows[175]['supplier'], packet_id=successor_packet_id, transition_event=rows[178]['supplier'], action_packet_transition_registry_profile=rows[85]['supplier'])
    assert_equal(record_validation(179, action_packet.validate_action_commit_packet_registry_v02, action_packet.validate_action_commit_packet_registry_v02(rows[179]['supplier']), ((179, rows[179]['supplier']),)), (True, ()), 'row179_registry')
    successor_pending_state = action_packet.derive_action_packet_lifecycle_state_v01(rows[179]['supplier'], packet_id=successor_packet_id, action_packet_transition_registry_profile=rows[85]['supplier'])
    old_superseded_state = action_packet.derive_action_packet_lifecycle_state_v01(rows[179]['supplier'], packet_id=rows[84]['supplier'].packet_identity.packet_id, action_packet_transition_registry_profile=rows[85]['supplier'])
    assert_equal((successor_pending_state.lifecycle_state, successor_pending_state.execution_attempt_count, successor_pending_state.reservation_owner_packet_id, old_superseded_state.lifecycle_state), ('PENDING_FULFILLMENT', 1, successor_packet_id, 'SUPERSEDED'), 'row179_states')
    emit_receipt(179, 1, 'supplier', action_packet.append_action_packet_lifecycle_transition_v01, rows[179]['supplier'], input_bindings=((84, 'supplier', rows[84]['supplier'], rows[84]['supplier']), (85, 'supplier', rows[85]['supplier'], rows[85]['supplier']), (154, 'supplier', rows[154]['supplier'], rows[154]['supplier']), (175, 'supplier', rows[175]['supplier'], rows[175]['supplier']), (178, 'supplier', rows[178]['supplier'], rows[178]['supplier'])))
    rows[180]['supplier'] = action_packet.replay_action_packet_lifecycle_history_v01(rows[179]['supplier'], packet_id=rows[84]['supplier'].packet_identity.packet_id, action_packet_transition_registry_profile=rows[85]['supplier'])
    assert_equal(record_validation(180, action_packet.validate_action_packet_lifecycle_replay_report_v01, action_packet.validate_action_packet_lifecycle_replay_report_v01(rows[180]['supplier'], rows[179]['supplier'], packet_id=rows[84]['supplier'].packet_identity.packet_id, action_packet_transition_registry_profile=rows[85]['supplier']), ((84, rows[84]['supplier'].packet_identity.packet_id), (85, rows[85]['supplier']), (179, rows[179]['supplier']), (180, rows[180]['supplier']))), (True, ()), 'row180_supplier')
    assert_equal((tuple((item.transition_event_id for item in rows[180]['supplier'].recorded_transitions)), rows[180]['supplier'].reconstructed_state.lifecycle_state, rows[180]['supplier'].reconstructed_state.reservation_owner_packet_id, rows[180]['supplier'].registry_unchanged, rows[180]['supplier'].creates_authority, rows[180]['supplier'].creates_permission, rows[180]['supplier'].creates_packet, rows[180]['supplier'].creates_receipt, rows[180]['supplier'].adapter_calls, rows[180]['supplier'].real_world_effects_count), ((rows[89]['supplier'].transition_event_id, rows[93]['supplier'].transition_event_id, rows[97]['supplier'].transition_event_id, rows[170]['supplier'].transition_event_id), 'SUPERSEDED', successor_packet_id, True, False, False, False, False, 0, 0), 'row180_replay')
    emit_receipt(180, 1, 'supplier', action_packet.replay_action_packet_lifecycle_history_v01, rows[180]['supplier'], input_bindings=((84, 'supplier', rows[84]['supplier'], rows[84]['supplier']), (85, 'supplier', rows[85]['supplier'], rows[85]['supplier']), (89, 'supplier', rows[89]['supplier'], rows[89]['supplier']), (93, 'supplier', rows[93]['supplier'], rows[93]['supplier']), (97, 'supplier', rows[97]['supplier'], rows[97]['supplier']), (154, 'supplier', rows[154]['supplier'], rows[154]['supplier']), (170, 'supplier', rows[170]['supplier'], rows[170]['supplier']), (179, 'supplier', rows[179]['supplier'], rows[179]['supplier'])))
    rows[181]['supplier'] = action_packet.inspect_action_packet_present_eligibility_v01(rows[179]['supplier'], packet_id=rows[84]['supplier'].packet_identity.packet_id, corridor=rows[100]['supplier'], corridor_step=rows[99]['supplier'], current_dependency_observations=(rows[101]['supplier'],), logical_time_bridge=rows[102]['supplier'], evaluation_time=terminal_evaluation_time, evaluation_time_source=terminal_evaluation_source, evaluation_context_id=terminal_evaluation_context, action_packet_transition_registry_profile=rows[85]['supplier'])
    assert_equal(record_validation(181, action_packet.validate_action_packet_present_eligibility_inspection_v01, action_packet.validate_action_packet_present_eligibility_inspection_v01(rows[181]['supplier'], rows[179]['supplier'], packet_id=rows[84]['supplier'].packet_identity.packet_id, corridor=rows[100]['supplier'], corridor_step=rows[99]['supplier'], current_dependency_observations=(rows[101]['supplier'],), logical_time_bridge=rows[102]['supplier'], evaluation_time=terminal_evaluation_time, evaluation_time_source=terminal_evaluation_source, evaluation_context_id=terminal_evaluation_context, action_packet_transition_registry_profile=rows[85]['supplier']), ((84, rows[84]['supplier'].packet_identity.packet_id), (85, rows[85]['supplier']), (99, rows[99]['supplier']), (100, rows[100]['supplier']), (101, rows[101]['supplier']), (102, rows[102]['supplier']), (179, rows[179]['supplier']), (181, rows[181]['supplier']))), (True, ()), 'row181_supplier')
    assert_equal((rows[181]['supplier'].historical_state.lifecycle_state, rows[181]['supplier'].present_eligibility_status, rows[181]['supplier'].present_executable, rows[181]['supplier'].retry_eligible, rows[181]['supplier'].reason_codes, rows[181]['supplier'].historical_result_unchanged, rows[181]['supplier'].adapter_calls, rows[181]['supplier'].real_world_effects_count), ('SUPERSEDED', 'NON_EXECUTABLE', False, False, ('action_packet_present_state_non_executable',), True, 0, 0), 'row181_outcome')
    successor_entry = tuple((item for item in rows[179]['supplier'].action_packet_lifecycle_entries if item.root_bound_genesis.packet_identity.packet_id == successor_packet_id))[0]
    assert_equal(tuple((item.transition_event_id for item in successor_entry.transition_events)), (rows[168]['supplier'].transition_event_id, rows[174]['supplier'].transition_event_id, rows[178]['supplier'].transition_event_id), 'row181_successor_history')
    emit_receipt(181, 1, 'supplier', action_packet.inspect_action_packet_present_eligibility_v01, rows[181]['supplier'], input_bindings=((84, 'supplier', rows[84]['supplier'], rows[84]['supplier']), (85, 'supplier', rows[85]['supplier'], rows[85]['supplier']), (99, 'supplier', rows[99]['supplier'], rows[99]['supplier']), (100, 'supplier', rows[100]['supplier'], rows[100]['supplier']), (101, 'supplier', rows[101]['supplier'], rows[101]['supplier']), (102, 'supplier', rows[102]['supplier'], rows[102]['supplier']), (154, 'supplier', rows[154]['supplier'], rows[154]['supplier']), (168, 'supplier', rows[168]['supplier'], rows[168]['supplier']), (174, 'supplier', rows[174]['supplier'], rows[174]['supplier']), (178, 'supplier', rows[178]['supplier'], rows[178]['supplier']), (179, 'supplier', rows[179]['supplier'], rows[179]['supplier'])))
    contract_by_row = {item[0]: item for item in G2F_EXECUTION_CONTRACT_V01}
    assert_equal(tuple(contract_by_row), tuple(range(1, 182)), 'execution_contract_keyset')
    validation_events_by_row: dict[int, tuple[dict[str, object], ...]] = {}
    for owner_row in range(1, 182):
        validation_events_by_row[owner_row] = tuple(event for event in validation_events if event['row'] == owner_row)
    reverse_bindings: dict[tuple[int, str], list[tuple[int, str, object]]] = {}
    causal_parent_rows: dict[int, tuple[int, ...]] = {}
    for raw_receipt in row_receipts:
        row = raw_receipt['row']
        lane = raw_receipt['lane']
        input_bindings = raw_receipt['input_bindings']
        if row >= 122:
            parent_rows: list[int] = []
            for parent_row, parent_lane, retained_parent, supplied_parent in input_bindings:
                assert_equal(parent_row < row, True, 'causal_parent_strictly_backward')
                assert_equal(retained_parent is rows[parent_row][parent_lane], True, 'causal_parent_retained_identity')
                assert_equal(supplied_parent is retained_parent, True, 'causal_parent_supplied_identity')
                if parent_row not in parent_rows:
                    parent_rows.append(parent_row)
                reverse_bindings.setdefault((parent_row, parent_lane), []).append((row, lane, raw_receipt['produced_value']))
            causal_parent_rows[row] = tuple(parent_rows)
    assert_equal(tuple(causal_parent_rows), tuple(range(122, 182)), 'causal_parent_row_map_complete')
    causal_parent_body = json.dumps([[row, list(parents)] for row, parents in causal_parent_rows.items()], ensure_ascii=True, separators=(',', ':')).encode('ascii') + b'\n'
    assert_equal(hashlib.sha256(causal_parent_body).hexdigest(), CAUSAL_PARENT_ROWS_SHA256, 'causal_parent_row_map_identity')
    finalized_receipts: list[dict[str, object]] = []
    for raw_receipt in row_receipts:
        row = raw_receipt['row']
        ordinal = raw_receipt['ordinal']
        lane = raw_receipt['lane']
        contract_row, producer, expected_lanes, validators, validation_owner_row, validation_mode, transaction_role, enforcement_class = contract_by_row[row]
        assert_equal(contract_row, row, 'receipt_contract_row')
        assert_equal(raw_receipt['producer'] is producer, True, 'receipt_producer_callable')
        retained_row_value = rows[row].get(lane)
        if retained_row_value is None and 'root_set' in rows[row]:
            retained_row_value = rows[row]['root_set'][ordinal - 1]
        assert_equal(raw_receipt['produced_value'] is retained_row_value, True, 'receipt_output_identity')
        assert_equal(raw_receipt['runtime_type'] is type(raw_receipt['produced_value']), True, 'receipt_runtime_type')
        assert_equal(raw_receipt['stable_ref'], stable_value_ref(raw_receipt['produced_value']), 'receipt_stable_ref')
        assert_equal(expected_lanes[ordinal - 1], lane, 'receipt_lane_ordinal')
        validator_evidence = tuple(event for event in validation_events_by_row[validation_owner_row] if event['validator'] in validators)
        assert_equal(bool(validator_evidence) or validation_mode == 'public_producer_internal', True, 'receipt_validator_evidence')
        if lane in ('client', 'supplier'):
            root_id = lanes[lane]['root_id']
            transaction_id = rows[5][lane].query_id
        elif lane == 'parent':
            root_id = tuple(root for _label, root, _domain in ROOT_ROWS)
            transaction_id = SHARED_REQUEST_ID
        else:
            root_id = None
            transaction_id = SHARED_REQUEST_ID
        finalized_receipts.append({**raw_receipt, 'root_id': root_id, 'transaction_id': transaction_id, 'transaction_role': transaction_role, 'validator_callables': validators, 'validation_owner_row': validation_owner_row, 'validation_mode': validation_mode, 'validation_evidence': validator_evidence, 'enforcement_class': enforcement_class, 'consumed_by': tuple(reverse_bindings.get((row, lane), ()))})
    row_receipts = finalized_receipts
    producers_by_row = {}
    for receipt in row_receipts:
        producers_by_row.setdefault(receipt['row'], set()).add(receipt['producer'])
    assert_equal(tuple(sorted(producers_by_row)), tuple(range(1, 182)), 'producer_rows')
    assert_equal(all((len(producers) == 1 for producers in producers_by_row.values())), True, 'producer_uniqueness')
    producer_basis_text = ''
    for row in range(1, 182):
        producer = tuple(producers_by_row[row])[0]
        module_name = producer.__module__
        symbol = producer.__name__
        producer_basis_text += f"{row:03d}\t{module_name.replace('.', '/')}.py\t{symbol}\n"
    producer_basis_bytes = producer_basis_text.encode('ascii')
    assert_equal(len(producer_basis_bytes), 14264, 'producer_basis_bytes')
    assert_equal(producer_basis_bytes.count(b'\n'), 181, 'producer_basis_lf')
    assert_equal(hashlib.sha256(producer_basis_bytes).hexdigest(), PRODUCER_BASIS_SHA256, 'producer_basis_sha256')
    direct_root_results = (rows[20]['client'], rows[20]['supplier'], rows[33]['client'], rows[82]['supplier'], rows[128]['supplier'], rows[137]['supplier'], rows[152]['supplier'], rows[163]['supplier'])
    direct_root_decision_ids = tuple((item.decision_id for item in direct_root_results))
    client_bundle = rows[69]['client'][0]
    supplier_bundle = rows[69]['supplier'][0]
    baseline_artifacts, observed_artifacts = rows[105]['supplier']
    baseline_sibling_match = tuple(item for item in baseline_artifacts if item.artifact_id == sibling_runtime_projection.artifact_id)
    observed_sibling_match = tuple(item for item in observed_artifacts if item.artifact_id == sibling_runtime_projection.artifact_id)
    assert_equal((len(baseline_sibling_match), len(observed_sibling_match)), (1, 1), 'sibling_projection_identity_lookup')
    baseline_sibling_bytes = canonical_json_bytes_v01(abi.kernel_artifact_to_plain_dict_v01(baseline_sibling_match[0]))
    observed_sibling_bytes = canonical_json_bytes_v01(abi.kernel_artifact_to_plain_dict_v01(observed_sibling_match[0]))
    recomputed_sibling = tuple((item for item in delta_bundle.recomputed_g2d_execution_bundle.queue_artifacts if item.artifact_id == sibling_initial_artifact.artifact_id))
    assert_equal(len(recomputed_sibling), 1, 'recomputed_sibling_unique')
    recomputed_sibling_bytes = canonical_json_bytes_v01(abi.kernel_artifact_to_plain_dict_v01(recomputed_sibling[0]))
    original_sibling_bytes = canonical_json_bytes_v01(abi.kernel_artifact_to_plain_dict_v01(sibling_initial_artifact))
    permission_created_count = sum((int(item.permission_created) for item in direct_root_results)) + delta_bundle.runtime_report.permissions_created + int(rows[144]['supplier'].creates_permission) + int(rows[180]['supplier'].creates_permission) + int(rows[181]['supplier'].creates_permission)
    final_output_created_count = sum((int(item.final_output_created) for item in direct_root_results)) + delta_bundle.runtime_report.final_outputs_created
    runtime_component_authority_created_count = client_bundle.runtime_report.authority_created_count + supplier_bundle.runtime_report.authority_created_count + delta_bundle.runtime_report.authority_created_count
    adapter_calls = rows[103]['supplier'].adapter_calls + hostile_report.adapter_calls + rows[144]['supplier'].adapter_calls + rows[180]['supplier'].adapter_calls + rows[181]['supplier'].adapter_calls
    real_world_effects_count = client_bundle.runtime_report.real_world_effects_count + supplier_bundle.runtime_report.real_world_effects_count + delta_bundle.runtime_report.real_world_effects_count + rows[143]['supplier'].real_world_effects_count + rows[144]['supplier'].real_world_effects_count + rows[172]['supplier'].real_world_effects_count + rows[179]['supplier'].real_world_effects_count + rows[180]['supplier'].real_world_effects_count + rows[181]['supplier'].real_world_effects_count
    operation_counts = {'provider_calls': sum((rows[23][label].provider_calls for label, _, _ in ROOT_ROWS)), 'model_calls': sum((rows[23][label].gemini_calls for label, _, _ in ROOT_ROWS)), 'network_calls': sum((rows[23][label].network_calls for label, _, _ in ROOT_ROWS)), 'connector_calls': sum((rows[23][label].connector_calls for label, _, _ in ROOT_ROWS)), 'external_drs_calls': sum((rows[23][label].external_drs_calls for label, _, _ in ROOT_ROWS)), 'adapter_calls': adapter_calls, 'real_world_effects_count': real_world_effects_count, 'non_root_authority_created_count': runtime_component_authority_created_count, 'aggregate_authority_created': rows[64]['parent'].authority_transfer_count != 0, 'superroot_created': rows[64]['parent'].super_root_created, 'permission_created_count': permission_created_count, 'final_output_created_count': final_output_created_count}
    laws = {'safe_informational_reuse_skips_heavy_work': all((rows[24][label] == (True, ()) and rows[23][label].memory_descent_result is None for label, _, _ in ROOT_ROWS)), 'action_like_reuse_remains_blocked': not rows[26]['client'].action_intent_passed and 'drs_action_intent_shortcut_forbidden' in rows[26]['client'].reason_codes, 'high_risk_multiroot_selects_deep_path': all((rows[50][label].mode == 'full_fractal' for label, _, _ in ROOT_ROWS)) and len(client_bundle.cell_results) > 0 and (len(supplier_bundle.cell_results) > 0), 'authorized_packet_revoked_before_fulfillment': revoked_state.lifecycle_state == 'REVOKED' and (not rows[144]['supplier'].present_executable), 'superseded_old_packet_replay_blocked': rows[180]['supplier'].reconstructed_state.lifecycle_state == 'SUPERSEDED' and (not rows[181]['supplier'].present_executable), 'selective_recomputation_complete_and_minimal': rows[117]['supplier'].complete and rows[117]['supplier'].minimal and (baseline_sibling_bytes == observed_sibling_bytes) and (recomputed_sibling_bytes == original_sibling_bytes), 'components_create_no_authority': not any((value if isinstance(value, bool) else value != 0 for value in operation_counts.values()))}
    causal_edges = tuple(((parent, consumer) for consumer, parents in causal_parent_rows.items() for parent in parents))
    report = {'report_version': 'v0.1', 'shared_request_id': SHARED_REQUEST_ID, 'parent_multiroot_correlation_id': rows[64]['parent'].transaction_id, 'root_ids': tuple((root_id for _, root_id, _ in ROOT_ROWS)), 'root_local_transaction_ids': tuple((rows[5][label].query_id for label, _, _ in ROOT_ROWS)), 'packet_owner_root': supplier_root_id, 'delta_affected_root_ids': (supplier_root_id,), 'delta_role_bindings': delta_role_bindings, 'rows': rows, 'row_receipts': tuple(row_receipts), 'component_receipts': tuple(component_receipts), 'auxiliary_receipts': tuple(auxiliary_receipts), 'validation_events': tuple(validation_events), 'producer_basis': producer_basis_text, 'causal_parent_rows': tuple(causal_parent_rows.items()), 'causal_edges': causal_edges, 'root_decision_logical_rows': (20, 33, 82, 128, 137, 152, 163), 'root_decisions': direct_root_results, 'revocation_source_registry': rows[98]['supplier'], 'supersession_source_registry': rows[98]['supplier'], 'baseline_sibling_bytes_sha256': hashlib.sha256(baseline_sibling_bytes).hexdigest(), 'observed_sibling_bytes_sha256': hashlib.sha256(observed_sibling_bytes).hexdigest(), 'original_sibling_queue_bytes_sha256': hashlib.sha256(original_sibling_bytes).hexdigest(), 'recomputed_sibling_queue_bytes_sha256': hashlib.sha256(recomputed_sibling_bytes).hexdigest(), 'laws': laws, 'operation_counts': operation_counts}
    if not validate_consolidated_gate2_gauntlet_g2_f_report_v01(report):
        raise ValueError('g2f_report_invalid')
    return report

def validate_consolidated_gate2_gauntlet_g2_f_report_v01(report):
    if type(report) is not dict:
        return False
    expected_keys = {
        'report_version', 'shared_request_id', 'parent_multiroot_correlation_id',
        'root_ids', 'root_local_transaction_ids', 'packet_owner_root',
        'delta_affected_root_ids', 'delta_role_bindings', 'rows', 'row_receipts',
        'component_receipts', 'auxiliary_receipts', 'validation_events',
        'producer_basis', 'causal_parent_rows', 'causal_edges',
        'root_decision_logical_rows', 'root_decisions',
        'revocation_source_registry', 'supersession_source_registry',
        'baseline_sibling_bytes_sha256', 'observed_sibling_bytes_sha256',
        'original_sibling_queue_bytes_sha256',
        'recomputed_sibling_queue_bytes_sha256', 'laws', 'operation_counts',
    }
    if set(report) != expected_keys:
        return False

    def evidence_plain(value):
        if dataclasses.is_dataclass(value) and not isinstance(value, type):
            return evidence_plain(dataclasses.asdict(value))
        if type(value) is dict:
            return {
                str(key): evidence_plain(item)
                for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
            }
        if type(value) in (tuple, list):
            return [evidence_plain(item) for item in value]
        if type(value) in (set, frozenset):
            items = [evidence_plain(item) for item in value]
            return sorted(items, key=lambda item: json.dumps(
                item, ensure_ascii=True, separators=(',', ':'), sort_keys=True
            ))
        if type(value) is bytes:
            return {'bytes_hex': value.hex()}
        if value is None or type(value) in (bool, int, float, str):
            return value
        raise TypeError('unsupported_execution_evidence_type:' + type(value).__name__)

    def stable_value_ref(value):
        type_name = type(value).__module__ + '.' + type(value).__qualname__
        body = (type_name + '\x00' + repr(value)).encode('utf-8')
        return 'g2f_typed_repr_sha256:' + hashlib.sha256(body).hexdigest()

    def contains_value(container, target):
        if container is target:
            return True
        if type(container) is dict:
            return any(contains_value(item, target) for item in container.values())
        if type(container) in (tuple, list, set, frozenset):
            return any(contains_value(item, target) for item in container)
        try:
            if container == target:
                return True
        except Exception:
            pass
        try:
            container_plain = evidence_plain(container)
            target_plain = evidence_plain(target)
        except TypeError:
            return repr(target) in repr(container)

        def contains_plain(value):
            if value == target_plain:
                return True
            if type(value) is dict:
                return any(contains_plain(item) for item in value.values())
            if type(value) is list:
                return any(contains_plain(item) for item in value)
            return False

        return contains_plain(container_plain)

    def retained_row_value(rows, row, lane, ordinal):
        if lane in rows[row]:
            return rows[row][lane]
        if lane in ('client', 'supplier') and 'root_set' in rows[row]:
            values = rows[row]['root_set']
            if type(values) is tuple and 0 < ordinal <= len(values):
                return values[ordinal - 1]
        raise KeyError('row_lane_missing')

    def validation_result_ok(result):
        if result is True or result == () or result == (True, ()):
            return True
        if type(result) is dict:
            return (
                result.get('accepted') is True
                and not result.get('errors', ())
                and not result.get('reason_codes', ())
            )
        if dataclasses.is_dataclass(result) and not isinstance(result, type):
            plain_result = evidence_plain(result)
            status_values = [
                plain_result[name]
                for name in (
                    'status', 'validation_status', 'verification_status',
                    'replay_status', 'final_status',
                )
                if name in plain_result
            ]
            if not status_values or any(value != 'PASS' for value in status_values):
                return False
            for name in ('errors', 'reason_codes', 'verification_errors', 'replay_errors'):
                if name in plain_result and plain_result[name]:
                    return False
            return True
        return False

    def internal_validation_result_ok(value):
        if validation_result_ok(value):
            return True
        if type(value) is dict:
            status_values = [
                value[name]
                for name in (
                    'status', 'validation_status', 'verification_status',
                    'replay_status', 'final_status',
                )
                if name in value
            ]
            if status_values and all(item == 'PASS' for item in status_values):
                if not any(value.get(name, ()) for name in (
                    'errors', 'reason_codes', 'verification_errors', 'replay_errors',
                )):
                    return True
            return any(internal_validation_result_ok(item) for item in value.values())
        if type(value) in (tuple, list):
            return any(internal_validation_result_ok(item) for item in value)
        if dataclasses.is_dataclass(value) and not isinstance(value, type):
            return internal_validation_result_ok(evidence_plain(value))
        return False

    try:
        rows = report['rows']
        receipts = report['row_receipts']
        components = report['component_receipts']
        auxiliaries = report['auxiliary_receipts']
        validation_events = report['validation_events']
        contract_by_row = {item[0]: item for item in G2F_EXECUTION_CONTRACT_V01}
        if tuple(contract_by_row) != tuple(range(1, 182)):
            return False
        if type(rows) is not dict or tuple(sorted(rows)) != tuple(range(1, 182)):
            return False
        if any(type(rows[row]) is not dict or not rows[row] for row in rows):
            return False
        if type(receipts) is not tuple or len(receipts) != 235:
            return False
        if type(validation_events) is not tuple:
            return False

        event_keys = {'row', 'validator', 'result', 'input_bindings', 'runtime_type', 'stable_ref'}
        failed_events = []
        for event in validation_events:
            if type(event) is not dict or set(event) != event_keys:
                return False
            if type(event['row']) is not int or not 1 <= event['row'] <= 181:
                return False
            if not callable(event['validator']):
                return False
            if event['runtime_type'] is not type(event['result']):
                return False
            if event['stable_ref'] != stable_value_ref(event['result']):
                return False
            if type(event['input_bindings']) is not tuple:
                return False
            for binding in event['input_bindings']:
                if type(binding) is not tuple or len(binding) != 2:
                    return False
                bound_row, bound_value = binding
                if type(bound_row) is not int or bound_row not in rows:
                    return False
                if not any(contains_value(value, bound_value) for value in rows[bound_row].values()):
                    return False
            if not validation_result_ok(event['result']):
                failed_events.append(event)
        if len(failed_events) != 1:
            return False
        failed_event = failed_events[0]
        if not (
            failed_event['row'] == 104
            and failed_event['validator'] is action_packet.validate_action_packet_present_eligibility_inspection_v01
            and failed_event['result'] == (
                False, ('action_packet_present_inspection_report_mismatch',)
            )
        ):
            return False

        receipt_keys = {
            'row', 'ordinal', 'lane', 'producer', 'produced_value', 'runtime_type',
            'stable_ref', 'stable_ref_kind', 'input_bindings', 'root_id',
            'transaction_id', 'transaction_role', 'validator_callables',
            'validation_owner_row', 'validation_mode', 'validation_evidence',
            'enforcement_class', 'consumed_by',
        }
        receipts_by_row = {row: [] for row in range(1, 182)}
        producers_by_row = {row: set() for row in range(1, 182)}
        attached_event_ids = set()
        derived_parent_rows = {}
        derived_reverse = {}
        for receipt in receipts:
            if type(receipt) is not dict or set(receipt) != receipt_keys:
                return False
            row = receipt['row']
            if type(row) is not int or row not in contract_by_row:
                return False
            contract_row, producer, expected_lanes, validators, owner_row, mode, transaction_role, enforcement = contract_by_row[row]
            if contract_row != row or receipt['producer'] is not producer:
                return False
            if type(receipt['ordinal']) is not int or not 1 <= receipt['ordinal'] <= len(expected_lanes):
                return False
            if receipt['lane'] != expected_lanes[receipt['ordinal'] - 1]:
                return False
            retained = retained_row_value(rows, row, receipt['lane'], receipt['ordinal'])
            if receipt['produced_value'] is not retained:
                return False
            if receipt['runtime_type'] is not type(retained):
                return False
            if receipt['stable_ref_kind'] != 'DETERMINISTIC_TYPED_REPR_SHA256':
                return False
            if receipt['stable_ref'] != stable_value_ref(retained):
                return False
            lane = receipt['lane']
            if lane in ('client', 'supplier'):
                expected_root = dict((label, root) for label, root, _domain in ROOT_ROWS)[lane]
                expected_transaction = rows[5][lane].query_id
            elif lane == 'parent':
                expected_root = tuple(root for _label, root, _domain in ROOT_ROWS)
                expected_transaction = SHARED_REQUEST_ID
            else:
                expected_root = None
                expected_transaction = SHARED_REQUEST_ID
            if receipt['root_id'] != expected_root or receipt['transaction_id'] != expected_transaction:
                return False
            if receipt['transaction_role'] != transaction_role:
                return False
            if receipt['validator_callables'] != validators:
                return False
            if receipt['validation_owner_row'] != owner_row or receipt['validation_mode'] != mode:
                return False
            if receipt['enforcement_class'] != enforcement:
                return False
            evidence = receipt['validation_evidence']
            if type(evidence) is not tuple:
                return False
            if any(not any(event is known for known in validation_events) for event in evidence):
                return False
            if any(event['row'] != owner_row or event['validator'] not in validators for event in evidence):
                return False
            if any(not validation_result_ok(event['result']) for event in evidence):
                return False
            evidence_validators = {event['validator'] for event in evidence}
            if mode == 'public_producer_internal':
                if not evidence_validators.issubset(set(validators)):
                    return False
                if not internal_validation_result_ok(retained):
                    return False
            elif evidence_validators != set(validators):
                return False
            attached_event_ids.update(id(event) for event in evidence)
            input_bindings = receipt['input_bindings']
            if type(input_bindings) is not tuple:
                return False
            if row < 122 and input_bindings:
                return False
            parents = []
            for binding in input_bindings:
                if type(binding) is not tuple or len(binding) != 4:
                    return False
                parent_row, parent_lane, retained_parent, supplied_parent = binding
                if type(parent_row) is not int or parent_row >= row or parent_row not in rows:
                    return False
                if parent_lane not in rows[parent_row]:
                    return False
                if retained_parent is not rows[parent_row][parent_lane] or supplied_parent is not retained_parent:
                    return False
                if parent_row in parents:
                    return False
                parents.append(parent_row)
                derived_reverse.setdefault((parent_row, parent_lane), []).append((row, lane, retained))
            if row >= 122:
                if row in derived_parent_rows and derived_parent_rows[row] != tuple(parents):
                    return False
                derived_parent_rows[row] = tuple(parents)
            receipts_by_row[row].append(receipt)
            producers_by_row[row].add(producer)

        for row, contract in contract_by_row.items():
            expected_lanes = contract[2]
            expected_row_keys = {'root_set'} if row in (62, 63) else set(expected_lanes)
            if set(rows[row]) != expected_row_keys:
                return False
            row_receipts = receipts_by_row[row]
            if tuple(item['lane'] for item in row_receipts) != expected_lanes:
                return False
            if tuple(item['ordinal'] for item in row_receipts) != tuple(range(1, len(expected_lanes) + 1)):
                return False
            if producers_by_row[row] != {contract[1]}:
                return False
        for receipt in receipts:
            expected_consumers = tuple(derived_reverse.get((receipt['row'], receipt['lane']), ()))
            if receipt['consumed_by'] != expected_consumers:
                return False

        derived_basis_parts = []
        for row in range(1, 182):
            producer = contract_by_row[row][1]
            module_name = producer.__module__
            derived_basis_parts.append(
                f"{row:03d}\t{module_name.replace('.', '/')}.py\t{producer.__name__}\n"
            )
        derived_basis = ''.join(derived_basis_parts)
        basis_bytes = derived_basis.encode('ascii')
        if not (
            report['producer_basis'] == derived_basis
            and len(basis_bytes) == 14264
            and basis_bytes.count(b'\n') == 181
            and hashlib.sha256(basis_bytes).hexdigest() == PRODUCER_BASIS_SHA256
        ):
            return False

        if tuple(derived_parent_rows) != tuple(range(122, 182)):
            return False
        causal_body = json.dumps(
            [[row, list(parents)] for row, parents in derived_parent_rows.items()],
            ensure_ascii=True, separators=(',', ':'),
        ).encode('ascii') + b'\n'
        if hashlib.sha256(causal_body).hexdigest() != CAUSAL_PARENT_ROWS_SHA256:
            return False
        reported_parent_rows = report['causal_parent_rows']
        if type(reported_parent_rows) is not tuple or reported_parent_rows != tuple(derived_parent_rows.items()):
            return False
        derived_edges = tuple(
            (parent, consumer)
            for consumer, parents in derived_parent_rows.items()
            for parent in parents
        )
        if report['causal_edges'] != derived_edges:
            return False
        if not (
            len(derived_parent_rows) == 60
            and len(derived_edges) == 274
            and sum(parent >= 122 for parent, _consumer in derived_edges) == 155
            and all(parent < consumer for parent, consumer in derived_edges)
            and derived_parent_rows[173] == (85, 154, 168, 171)
        ):
            return False

        component_keys = {'row', 'ordinal', 'lane', 'producer', 'inputs', 'input_ref', 'result', 'runtime_type', 'stable_ref', 'purpose'}
        single_component_producers = {
            39: context_packets.semantic_evidence_item,
            41: router.build_execution_mode_local_mode_profile_v01,
            49: router.evaluate_execution_mode_feasibility_v01,
            57: router.review_execution_mode_proposal_v01,
            69: fractal_runtime.run_fractal_runtime_v02,
            88: action_packet.build_transition_evidence_binding_v01,
            92: action_packet.build_transition_evidence_binding_v01,
            96: action_packet.build_transition_evidence_binding_v01,
            141: action_packet.build_transition_evidence_binding_v01,
            167: action_packet.build_transition_evidence_binding_v01,
            169: action_packet.build_transition_evidence_binding_v01,
            173: action_packet.build_transition_evidence_binding_v01,
            177: action_packet.build_transition_evidence_binding_v01,
        }
        row070_producers = (
            action_packet.PermissionScopeV02, action_packet.PacketTTL,
            action_packet.IdempotencyKeyV02, action_packet.AdapterBindingV02,
            action_packet.PacketEvidenceRefV02,
        )
        component_groups = {}
        if type(components) is not tuple:
            return False
        for component in components:
            if type(component) is not dict or set(component) != component_keys:
                return False
            row = component['row']
            lane = component['lane']
            ordinal = component['ordinal']
            if type(row) is not int or row not in rows or lane not in rows[row]:
                return False
            if type(ordinal) is not int or ordinal < 1:
                return False
            if row == 70:
                if ordinal > len(row070_producers) or component['producer'] is not row070_producers[ordinal - 1]:
                    return False
            elif row not in single_component_producers or component['producer'] is not single_component_producers[row]:
                return False
            if type(component['inputs']) is not tuple or not component['purpose']:
                return False
            if component['input_ref'] != stable_value_ref(component['inputs']):
                return False
            if component['runtime_type'] is not type(component['result']):
                return False
            if component['stable_ref'] != stable_value_ref(component['result']):
                return False
            if not contains_value(rows[row][lane], component['result']):
                return False
            if row == 39:
                fields = (
                    'observed_semantic_facts', 'missing_evidence',
                    'uncertainty_notes', 'risk_boundary_notes',
                    'rejected_action_routes', 'required_approvals_or_conditions',
                    'authority_boundary_notes',
                )
                if component['inputs'] != (lane, fields[ordinal - 1]) or component['result'] is not rows[39][lane][ordinal - 1]:
                    return False
            elif row == 41:
                root_by_lane = dict((item_label, item_root) for item_label, item_root, _domain in ROOT_ROWS)
                domain_by_lane = dict((item_label, item_domain) for item_label, _root, item_domain in ROOT_ROWS)
                expected_inputs = (
                    SHARED_REQUEST_ID, rows[5][lane], root_by_lane[lane],
                    domain_by_lane[lane], router.EXECUTABLE_EXECUTION_MODES_V01[ordinal - 1],
                )
                if component['inputs'] != expected_inputs or component['result'] is not rows[41][lane][ordinal - 1]:
                    return False
            elif row == 49:
                if component['inputs'] != (rows[48][lane], rows[43][lane]) or component['result'] is not rows[49][lane][ordinal - 1]:
                    return False
            elif row == 57:
                expected_inputs = (rows[56][lane], rows[51][lane]) if ordinal == 1 else (rows[56][lane],)
                expected_result = rows[57][lane][0] if ordinal == 1 else rows[57][lane][3]
                if component['inputs'] != expected_inputs or component['result'] is not expected_result:
                    return False
            elif row == 69:
                if component['inputs'] != (rows[68][lane],) or component['result'] is not rows[69][lane][0].cell_results[ordinal - 1]:
                    return False
            elif row == 70:
                packet = rows[70]['supplier']
                expected_results = (
                    packet.scope, packet.ttl, packet.idempotency,
                    packet.adapter_binding, packet.evidence_refs[0],
                )
                if component['inputs'] != () or component['result'] is not expected_results[ordinal - 1]:
                    return False
            else:
                if component['result'] is not rows[row][lane][ordinal - 1]:
                    return False
                if component['inputs'] != (component['result'].evidence_ref,):
                    return False
            key = (row, lane)
            component_groups.setdefault(key, []).append(component)
        for (row, lane), group in component_groups.items():
            if row == 57:
                expected_count = 2
            elif row == 69:
                expected_count = len(rows[row][lane][0].cell_results)
            elif row == 70:
                expected_count = 5
            else:
                expected_count = len(rows[row][lane])
            if len(group) != expected_count:
                return False
            if tuple(item['ordinal'] for item in group) != tuple(range(1, expected_count + 1)):
                return False
        required_component_groups = {
            (39, 'client'), (39, 'supplier'), (41, 'client'), (41, 'supplier'),
            (49, 'client'), (49, 'supplier'), (57, 'client'), (57, 'supplier'),
            (69, 'client'), (69, 'supplier'), (70, 'supplier'), (88, 'supplier'),
            (92, 'supplier'), (96, 'supplier'), (141, 'supplier'),
            (167, 'supplier'), (169, 'supplier'), (173, 'supplier'),
            (177, 'supplier'),
        }
        if set(component_groups) != required_component_groups:
            return False

        auxiliary_keys = {'label', 'producer', 'inputs', 'input_ref', 'result', 'runtime_type', 'stable_ref', 'purpose'}
        if type(auxiliaries) is not tuple or len(auxiliaries) != 2:
            return False
        auxiliaries_by_label = {}
        for auxiliary in auxiliaries:
            if type(auxiliary) is not dict or set(auxiliary) != auxiliary_keys:
                return False
            if auxiliary['label'] in auxiliaries_by_label or type(auxiliary['inputs']) is not tuple:
                return False
            if auxiliary['input_ref'] != stable_value_ref(auxiliary['inputs']):
                return False
            if auxiliary['runtime_type'] is not type(auxiliary['result']):
                return False
            if auxiliary['stable_ref'] != stable_value_ref(auxiliary['result']) or not auxiliary['purpose']:
                return False
            auxiliaries_by_label[auxiliary['label']] = auxiliary
        root_hash_evidence = auxiliaries_by_label['client_memory_descent_root_hash']
        if not (
            root_hash_evidence['producer'] is integrity_replay.domain_separated_sha256_hex_v01
            and root_hash_evidence['inputs'] == (rows[33]['client'],)
            and rows[34]['client'].root_decision_hash == root_hash_evidence['result']
        ):
            return False
        counterfactual_evidence = auxiliaries_by_label['ROW_120_COUNTERFACTUAL']
        delta_bundle = rows[120]['supplier'][0]
        counterfactual_inputs = counterfactual_evidence['inputs']
        if not (
            counterfactual_evidence['producer'] is fractal_runtime.validate_runtime_observed_work_counterfactual_v02
            and len(counterfactual_inputs) == 3
            and counterfactual_inputs[0] is delta_bundle.recomputed_g2d_execution_bundle
            and counterfactual_inputs[1] in counterfactual_inputs[0].causal_consumption_refs
            and counterfactual_inputs[1].source_artifact_id == counterfactual_inputs[0].observed_work_context.ordered_binding_artifacts[0].artifact_id
            and counterfactual_inputs[2].transaction_id == rows[5]['supplier'].query_id
            and counterfactual_inputs[2].owner_root_id == 'root:g2f:supplier'
            and counterfactual_inputs[2].source_component == 'continuous_delta_runtime_g2f'
            and counterfactual_inputs[2].artifact_id not in tuple(
                item.artifact_id
                for item in (
                    delta_bundle.source_context.baseline_source_artifacts
                    + delta_bundle.source_context.observed_source_artifacts
                )
            )
            and validation_result_ok(counterfactual_evidence['result'])
        ):
            return False

        root_by_lane = dict((label, root) for label, root, _domain in ROOT_ROWS)
        for label in ('client', 'supplier'):
            transaction_id = rows[5][label].query_id
            root_id = root_by_lane[label]
            if rows[5][label].query_id != transaction_id:
                return False
            if any(item.transaction_id != transaction_id or item.owning_root_id != root_id for item in rows[41][label]):
                return False
            for item in (rows[42][label], rows[48][label], rows[50][label], rows[51][label], rows[56][label]):
                if item.transaction_id != transaction_id or item.owning_root_id != root_id:
                    return False
            if any(item.transaction_id != transaction_id or item.owning_root_id != root_id for item in rows[49][label]):
                return False
            routed_proposal, routed_report = rows[52][label]
            if routed_proposal.transaction_id != transaction_id or routed_report.transaction_id != transaction_id:
                return False
            route_decision, _kernel, route_input, route_result, _review_report = rows[57][label]
            for item in (route_decision, route_input, route_result):
                if item.transaction_id != transaction_id:
                    return False
            if route_decision.owning_root_id != root_id or route_input.target_root_id != root_id or route_result.target_root_id != root_id:
                return False
            runtime_bundle = rows[69][label][0]
            if runtime_bundle.source_binding.transaction_id != transaction_id or runtime_bundle.source_binding.owning_root_id != root_id:
                return False

        if report['root_local_transaction_ids'] != (
            rows[5]['client'].query_id, rows[5]['supplier'].query_id
        ):
            return False
        if len(set(report['root_local_transaction_ids'])) != 2 or SHARED_REQUEST_ID in report['root_local_transaction_ids']:
            return False
        if rows[64]['parent'].transaction_id != SHARED_REQUEST_ID:
            return False
        if rows[64]['parent'].root_decisions != rows[63]['root_set'] or rows[64]['parent'].cross_root_evidence_refs != rows[62]['root_set']:
            return False
        for ordinal, label in enumerate(('client', 'supplier')):
            wrapper = rows[63]['root_set'][ordinal]
            cross_ref = rows[62]['root_set'][ordinal]
            route_decision = rows[57][label][0]
            if not (
                wrapper.transaction_id == SHARED_REQUEST_ID
                and wrapper.root_id == root_by_lane[label]
                and wrapper.root_decision_id == route_decision.decision_id
                and wrapper.source_decision_ref == rows[58][label].artifact_id
                and wrapper.selected_subject_id == rows[60][label].artifact_id
                and cross_ref.transaction_id == SHARED_REQUEST_ID
                and cross_ref.source_root_id == root_by_lane[label]
                and cross_ref.evidence_artifact_id == rows[60][label].artifact_id
            ):
                return False

        review_chains = (
            (20, 13, 14, 15, 16, 18, 19, 'client'),
            (20, 13, 14, 15, 16, 18, 19, 'supplier'),
            (33, 27, 28, 29, 30, 31, 32, 'client'),
            (82, 76, 77, 78, 79, 80, 81, 'supplier'),
            (128, 122, 123, 124, 125, 126, 127, 'supplier'),
            (137, 131, 132, 133, 134, 135, 136, 'supplier'),
            (152, 146, 147, 148, 149, 150, 151, 'supplier'),
            (163, 157, 158, 159, 160, 161, 162, 'supplier'),
        )
        direct_root_results = []
        for result_row, request_row, evidence_row, claim_row, contribution_row, packet_row, input_row, lane in review_chains:
            request = rows[request_row][lane]
            evidence_binding = rows[evidence_row][lane]
            claim = rows[claim_row][lane]
            contribution = rows[contribution_row][lane]
            packet = rows[packet_row][lane]
            decision_input = rows[input_row][lane]
            result = rows[result_row][lane]
            transaction_id = rows[5][lane].query_id
            root_id = root_by_lane[lane]
            input_plain = root_decision.root_decision_input_to_plain_dict_v01(decision_input)
            if not (
                request.request_id == SHARED_REQUEST_ID
                and request.transaction_id == transaction_id
                and request.target_root_id == root_id
                and contribution.request_id == request.request_id
                and any(item is claim for item in contribution.claims)
                and any(item is evidence_binding for item in contribution.evidence_bindings)
                and packet.request_id == request.request_id
                and packet.transaction_id == transaction_id
                and packet.target_root_id == root_id
                and contribution.contribution_id in packet.contribution_ids
                and decision_input.transaction_id == transaction_id
                and decision_input.target_root_id == root_id
                and decision_input.root_review_packet.packet_id == packet.packet_id
                and claim.claim_id in tuple(input_plain['post_vv_bundle']['validated_candidate_ids'])
                and input_plain['gt_advisory']['selected_candidate_id'] == claim.claim_id
                and result.decision_input_id == decision_input.decision_input_id
                and result.transaction_id == transaction_id
                and result.target_root_id == root_id
                and result.selected_candidate_id == claim.claim_id
                and result.root_commit_created
                and not result.permission_created
                and not result.final_output_created
                and not result.effect_requested
            ):
                return False
            direct_root_results.append(result)
        direct_root_results = tuple(direct_root_results)
        if report['root_decision_logical_rows'] != (20, 33, 82, 128, 137, 152, 163):
            return False
        if report['root_decisions'] != direct_root_results or len({item.decision_id for item in direct_root_results}) != 8:
            return False

        row083_receipt = receipts_by_row[83][0]
        if row083_receipt['validator_callables'] != (
            action_packet.validate_root_decision_candidate_projection_v01,
            action_packet.validate_supplier_root_context_coherence_v01,
        ):
            return False
        row099_receipt = receipts_by_row[99][0]
        if not (
            row099_receipt['validation_owner_row'] == 103
            and row099_receipt['validator_callables'] == (
                action_packet.validate_action_packet_present_eligibility_inspection_v01,
            )
            and any(
                any(bound_row == 99 and bound_value is rows[99]['supplier']
                    for bound_row, bound_value in event['input_bindings'])
                for event in row099_receipt['validation_evidence']
            )
        ):
            return False

        runtime_report_artifact = delta_bundle.runtime_report_artifact
        row127_plain = root_decision.root_decision_input_to_plain_dict_v01(rows[127]['supplier'])
        observation_id = runtime_report_artifact.artifact_id
        if not (
            rows[124]['supplier'].claim_id == observation_id
            and tuple(row127_plain['post_vv_bundle']['validated_candidate_ids']) == (observation_id,)
            and row127_plain['gt_advisory']['selected_candidate_id'] == observation_id
            and rows[128]['supplier'].selected_candidate_id == observation_id
            and rows[129]['supplier'].source_invalidation_event_ref == observation_id
            and rows[129]['supplier'].evidence_ref == observation_id
            and rows[129]['supplier'].acceptance_root_decision_id is None
            and rows[129]['supplier'].acceptance_root_decision_hash is None
            and rows[129]['supplier'].root_decision_ref is None
            and rows[130]['supplier'].evidence_refs == (rows[129]['supplier'].invalidation_evidence_id,)
            and rows[130]['supplier'].evidence_hashes == (rows[129]['supplier'].invalidation_evidence_id,)
        ):
            return False

        role_bindings = report['delta_role_bindings']
        if type(role_bindings) is not dict or set(role_bindings) != {'SIBLING', 'TARGET'}:
            return False
        supplier_bundle = rows[69]['supplier'][0]
        root_inputs = tuple(item for item in supplier_bundle.cell_inputs if item.parent_cell_id is None)
        if len(root_inputs) != 1:
            return False
        baseline_root_input = root_inputs[0]
        expected_roles = (
            ('SIBLING', 'unrelated_supplier_safe_sibling', 0),
            ('TARGET', 'supplier_water_filter_dependency_consumer', 1),
        )
        resolved_role_ids = {}
        for role, semantic_role, canonical_index in expected_roles:
            expected_child_id = fractal_runtime.derive_fractal_child_cell_id_v02(
                topology_seed_id=supplier_bundle.topology_seed.topology_seed_id,
                parent_cell_id=baseline_root_input.cell_id,
                canonical_child_index=canonical_index,
                accepted_mode=supplier_bundle.source_binding.accepted_mode,
                selected_local_mode_profile_id=supplier_bundle.source_binding.selected_local_mode_profile_id,
                source_mode_profile_set_id=supplier_bundle.source_binding.source_mode_profile_set_id,
                child_scope_ref=supplier_bundle.topology.accepted_scope_ref,
                runtime_policy_id=supplier_bundle.source_binding.runtime_policy_id,
                required_capability_ids=supplier_bundle.source_binding.required_downstream_capability_ids,
                forbidden_claims=supplier_bundle.source_context.runtime_policy.forbidden_claims,
                child_depth=1,
            )
            child_matches = tuple(item for item in supplier_bundle.cell_inputs if item.cell_id == expected_child_id)
            projection_matches = tuple(item for item in supplier_bundle.scope_projections if item.child_cell_id == expected_child_id)
            if len(child_matches) != 1 or len(projection_matches) != 1:
                return False
            child = child_matches[0]
            projection = projection_matches[0]
            node_matches = tuple(item for item in supplier_bundle.topology_nodes if item.node_id == child.ordered_node_ids[0])
            assignment_matches = tuple(item for item in supplier_bundle.runtime_assignments if item.node_id == child.ordered_node_ids[0])
            queue_matches = tuple(
                item for item in supplier_bundle.queue_entries
                if item.queue_entry_id in child.ordered_initial_queue_entry_ids
                and item.node_id == child.ordered_node_ids[0]
                and item.predecessor_queue_entry_id is None
            )
            if len(node_matches) != 1 or len(assignment_matches) != 1 or len(queue_matches) != 1:
                return False
            queue_entry = queue_matches[0]
            artifact_matches = tuple(
                item for item in supplier_bundle.queue_artifacts
                if abi.kernel_artifact_to_plain_dict_v01(item)['payload']['queue_entry_id']
                == queue_entry.queue_entry_id
            )
            if len(artifact_matches) != 1:
                return False
            artifact = artifact_matches[0]
            binding = role_bindings[role]
            if not (
                binding['scenario_role'] == semantic_role
                and binding['canonical_child_index'] == canonical_index
                and binding['root_cell_id'] == baseline_root_input.cell_id
                and binding['child_cell_id'] == expected_child_id
                and binding['child_cell_input_id'] == child.cell_input_id
                and binding['parent_cell_id'] == child.parent_cell_id
                and binding['scope_projection_id'] == projection.projection_id
                and binding['scope_ref'] == supplier_bundle.topology.accepted_scope_ref
                and binding['topology_node_id'] == node_matches[0].node_id
                and binding['topology_node_kind'] == node_matches[0].node_kind
                and binding['assignment_id'] == assignment_matches[0].assignment_id
                and binding['initial_queue_entry_id'] == queue_entry.queue_entry_id
                and binding['initial_queue_artifact_id'] == artifact.artifact_id
                and binding['initial_queue_artifact_parent_refs'] == artifact.parent_refs
                and binding['activation_parent_artifact_id'] == artifact.parent_refs[1]
                and child.scope_ref == supplier_bundle.topology.accepted_scope_ref
                and child.cell_depth == 1
            ):
                return False
            runtime_sha = hashlib.sha256(canonical_json_bytes_v01(
                abi.kernel_artifact_to_plain_dict_v01(artifact)
            )).hexdigest()
            if binding['runtime_projection_sha256'] != runtime_sha:
                return False
            resolved_role_ids[role] = expected_child_id
        if set(baseline_root_input.ordered_planned_child_cell_ids) != set(resolved_role_ids.values()):
            return False
        if resolved_role_ids['SIBLING'] == resolved_role_ids['TARGET']:
            return False

        baseline_artifacts, observed_artifacts = rows[105]['supplier']
        sibling_projection_id = role_bindings['SIBLING']['runtime_projection_artifact_id']
        baseline_sibling = tuple(item for item in baseline_artifacts if item.artifact_id == sibling_projection_id)
        observed_sibling = tuple(item for item in observed_artifacts if item.artifact_id == sibling_projection_id)
        if len(baseline_sibling) != 1 or len(observed_sibling) != 1:
            return False
        baseline_sibling_bytes = canonical_json_bytes_v01(abi.kernel_artifact_to_plain_dict_v01(baseline_sibling[0]))
        observed_sibling_bytes = canonical_json_bytes_v01(abi.kernel_artifact_to_plain_dict_v01(observed_sibling[0]))
        sibling_runtime_id = role_bindings['SIBLING']['initial_queue_artifact_id']
        original_sibling = tuple(item for item in supplier_bundle.queue_artifacts if item.artifact_id == sibling_runtime_id)
        recomputed_sibling = tuple(
            item for item in delta_bundle.recomputed_g2d_execution_bundle.queue_artifacts
            if item.artifact_id == sibling_runtime_id
        )
        if len(original_sibling) != 1 or len(recomputed_sibling) != 1:
            return False
        original_sibling_bytes = canonical_json_bytes_v01(abi.kernel_artifact_to_plain_dict_v01(original_sibling[0]))
        recomputed_sibling_bytes = canonical_json_bytes_v01(abi.kernel_artifact_to_plain_dict_v01(recomputed_sibling[0]))
        if not (
            report['baseline_sibling_bytes_sha256'] == hashlib.sha256(baseline_sibling_bytes).hexdigest()
            and report['observed_sibling_bytes_sha256'] == hashlib.sha256(observed_sibling_bytes).hexdigest()
            and report['original_sibling_queue_bytes_sha256'] == hashlib.sha256(original_sibling_bytes).hexdigest()
            and report['recomputed_sibling_queue_bytes_sha256'] == hashlib.sha256(recomputed_sibling_bytes).hexdigest()
            and baseline_sibling_bytes == observed_sibling_bytes
            and original_sibling_bytes == recomputed_sibling_bytes
        ):
            return False

        if report['revocation_source_registry'] is not rows[98]['supplier'] or report['supersession_source_registry'] is not rows[98]['supplier']:
            return False
        if any(143 in derived_parent_rows[row] for row in range(156, 182)):
            return False
        row173_evidence = tuple((item.evidence_code, item.evidence_ref) for item in rows[173]['supplier'])
        expected_row173_evidence = (
            ('transition_history_valid', rows[168]['supplier'].transition_event_id),
            ('temporal_authority_valid', rows[154]['supplier'].canonical_projection.temporal_authority_fingerprint),
            ('mandatory_dependencies_current', rows[154]['supplier'].canonical_projection.dependency_set_candidate_fingerprint),
            ('idempotency_reservation_owned', rows[171]['supplier'].idempotency_disposition_event_id),
        )
        if row173_evidence != expected_row173_evidence:
            return False

        client_bundle = rows[69]['client'][0]
        revoked_state = action_packet.derive_action_packet_lifecycle_state_v01(
            rows[143]['supplier'],
            packet_id=rows[84]['supplier'].packet_identity.packet_id,
            action_packet_transition_registry_profile=rows[85]['supplier'],
        )
        derived_operation_counts = {
            'provider_calls': sum(rows[23][label].provider_calls for label, _, _ in ROOT_ROWS),
            'model_calls': sum(rows[23][label].gemini_calls for label, _, _ in ROOT_ROWS),
            'network_calls': sum(rows[23][label].network_calls for label, _, _ in ROOT_ROWS),
            'connector_calls': sum(rows[23][label].connector_calls for label, _, _ in ROOT_ROWS),
            'external_drs_calls': sum(rows[23][label].external_drs_calls for label, _, _ in ROOT_ROWS),
            'adapter_calls': rows[103]['supplier'].adapter_calls + rows[144]['supplier'].adapter_calls + rows[180]['supplier'].adapter_calls + rows[181]['supplier'].adapter_calls,
            'real_world_effects_count': client_bundle.runtime_report.real_world_effects_count + supplier_bundle.runtime_report.real_world_effects_count + delta_bundle.runtime_report.real_world_effects_count + rows[143]['supplier'].real_world_effects_count + rows[144]['supplier'].real_world_effects_count + rows[172]['supplier'].real_world_effects_count + rows[179]['supplier'].real_world_effects_count + rows[180]['supplier'].real_world_effects_count + rows[181]['supplier'].real_world_effects_count,
            'non_root_authority_created_count': client_bundle.runtime_report.authority_created_count + supplier_bundle.runtime_report.authority_created_count + delta_bundle.runtime_report.authority_created_count,
            'aggregate_authority_created': rows[64]['parent'].authority_transfer_count != 0,
            'superroot_created': rows[64]['parent'].super_root_created,
            'permission_created_count': sum(int(item.permission_created) for item in direct_root_results) + delta_bundle.runtime_report.permissions_created + int(rows[144]['supplier'].creates_permission) + int(rows[180]['supplier'].creates_permission) + int(rows[181]['supplier'].creates_permission),
            'final_output_created_count': sum(int(item.final_output_created) for item in direct_root_results) + delta_bundle.runtime_report.final_outputs_created,
        }
        derived_laws = {
            'safe_informational_reuse_skips_heavy_work': all(rows[24][label] == (True, ()) and rows[23][label].memory_descent_result is None for label, _, _ in ROOT_ROWS),
            'action_like_reuse_remains_blocked': not rows[26]['client'].action_intent_passed and 'drs_action_intent_shortcut_forbidden' in rows[26]['client'].reason_codes,
            'high_risk_multiroot_selects_deep_path': all(rows[50][label].mode == 'full_fractal' for label, _, _ in ROOT_ROWS) and bool(client_bundle.cell_results) and bool(supplier_bundle.cell_results),
            'authorized_packet_revoked_before_fulfillment': revoked_state.lifecycle_state == 'REVOKED' and not rows[144]['supplier'].present_executable,
            'superseded_old_packet_replay_blocked': rows[180]['supplier'].reconstructed_state.lifecycle_state == 'SUPERSEDED' and not rows[181]['supplier'].present_executable,
            'selective_recomputation_complete_and_minimal': rows[117]['supplier'].complete and rows[117]['supplier'].minimal and baseline_sibling_bytes == observed_sibling_bytes and recomputed_sibling_bytes == original_sibling_bytes,
            'components_create_no_authority': not any(value if isinstance(value, bool) else value != 0 for value in derived_operation_counts.values()),
        }
        if report['operation_counts'] != derived_operation_counts:
            return False
        if any(value if isinstance(value, bool) else value != 0 for value in derived_operation_counts.values()):
            return False
        if report['laws'] != derived_laws or len(derived_laws) != 7 or not all(derived_laws.values()):
            return False
        if not (
            report['report_version'] == 'v0.1'
            and report['shared_request_id'] == SHARED_REQUEST_ID
            and report['parent_multiroot_correlation_id'] == SHARED_REQUEST_ID
            and report['root_ids'] == tuple(root for _label, root, _domain in ROOT_ROWS)
            and report['packet_owner_root'] == 'root:g2f:supplier'
            and report['delta_affected_root_ids'] == ('root:g2f:supplier',)
            and rows[129]['supplier'].acceptance_root_decision_id is None
            and rows[129]['supplier'].acceptance_root_decision_hash is None
            and rows[129]['supplier'].root_decision_ref is None
            and rows[180]['supplier'].reconstructed_state.lifecycle_state == 'SUPERSEDED'
            and not rows[181]['supplier'].present_executable
        ):
            return False
        if any(id(event) not in attached_event_ids and not validation_result_ok(event['result']) and event is not failed_event for event in validation_events):
            return False
    except (AttributeError, IndexError, KeyError, TypeError, ValueError):
        return False
    return True

def consolidated_gate2_gauntlet_g2_f_report_to_plain_data_v01(report):
    if not validate_consolidated_gate2_gauntlet_g2_f_report_v01(report):
        raise ValueError('g2f_report_invalid')
    rows = report['rows']
    receipts = report['row_receipts']

    def callable_name(value):
        return value.__module__ + '.' + value.__name__

    def json_value(value):
        if type(value) is dict:
            return {str(key): json_value(item) for key, item in sorted(value.items())}
        if type(value) in (tuple, list):
            return [json_value(item) for item in value]
        if value is None or type(value) in (bool, int, float, str):
            return value
        raise TypeError('unsupported_plain_projection_type:' + type(value).__name__)

    return {
        'auxiliary_receipts': [
            {
                'label': item['label'],
                'producer': callable_name(item['producer']),
                'purpose': item['purpose'],
                'runtime_type': item['runtime_type'].__module__ + '.' + item['runtime_type'].__qualname__,
                'stable_ref': item['stable_ref'],
            }
            for item in report['auxiliary_receipts']
        ],
        'causal_geometry': {
            'causal_edge_count': len(report['causal_edges']),
            'causal_row_count': len(report['causal_parent_rows']),
            'missing_causal_edge_count': 0,
            'new_to_new_causal_edge_count': sum(parent >= 122 for parent, _ in report['causal_edges']),
            'unexpected_causal_edge_count': 0,
        },
        'component_receipt_count': len(report['component_receipts']),
        'delta_role_bindings': {
            role: json_value(binding)
            for role, binding in sorted(report['delta_role_bindings'].items())
        },
        'g2f_status': 'NOT_CLOSED',
        'gate2_status': 'NOT_CLOSED',
        'laws': dict(report['laws']),
        'lifecycle': {
            'branch_model': 'TWO_INDEPENDENT_PROOF_BRANCHES_FROM_ROW098_PENDING_BASELINE',
            'old_packet_present_executable': rows[181]['supplier'].present_executable,
            'old_packet_replay_state': rows[180]['supplier'].reconstructed_state.lifecycle_state,
            'revocation_source_row': 98,
            'revoked_state': action_packet.derive_action_packet_lifecycle_state_v01(
                rows[143]['supplier'],
                packet_id=rows[84]['supplier'].packet_identity.packet_id,
                action_packet_transition_registry_profile=rows[85]['supplier'],
            ).lifecycle_state,
            'row_129_root_acceptance_sentinels': [
                rows[129]['supplier'].acceptance_root_decision_id,
                rows[129]['supplier'].acceptance_root_decision_hash,
                rows[129]['supplier'].root_decision_ref,
            ],
            'row_173_authorized_source_row': 154,
            'supersession_source_row': 98,
        },
        'operation_counts': dict(report['operation_counts']),
        'primary_row_receipt_count': len(receipts),
        'producer_basis_sha256': hashlib.sha256(report['producer_basis'].encode('ascii')).hexdigest(),
        'public_construction_rows_executed': len({item['row'] for item in receipts}),
        'report_version': report['report_version'],
        'root_geometry': {
            'direct_decide_root_receipt_count': len(report['root_decisions']),
            'direct_decide_root_logical_rows': list(report['root_decision_logical_rows']),
            'distinct_fresh_root_review_receipts': len({item.decision_id for item in report['root_decisions']}),
            'parent_multiroot_correlation_id': report['parent_multiroot_correlation_id'],
            'root_ids': list(report['root_ids']),
            'root_local_transaction_ids': list(report['root_local_transaction_ids']),
            'shared_request_id': report['shared_request_id'],
            'shared_request_is_local_transaction': report['shared_request_id'] in report['root_local_transaction_ids'],
        },
        'row_receipts': [
            {
                'consumed_by': [f'ROW_{consumer:03d}[{lane}]' for consumer, lane, _value in item['consumed_by']],
                'enforcement_class': item['enforcement_class'],
                'input_row_locators': [f'ROW_{parent:03d}[{lane}]' for parent, lane, _retained, _supplied in item['input_bindings']],
                'lane': item['lane'],
                'ordinal': item['ordinal'],
                'producer': callable_name(item['producer']),
                'root_id': json_value(item['root_id']),
                'row': item['row'],
                'runtime_type': item['runtime_type'].__module__ + '.' + item['runtime_type'].__qualname__,
                'stable_ref': item['stable_ref'],
                'stable_ref_kind': item['stable_ref_kind'],
                'transaction_id': item['transaction_id'],
                'transaction_role': item['transaction_role'],
                'validation_evidence_count': len(item['validation_evidence']),
                'validation_mode': item['validation_mode'],
                'validation_owner_row': item['validation_owner_row'],
                'validators': [callable_name(value) for value in item['validator_callables']],
            }
            for item in receipts
        ],
        'runtime_implementation_control_plane_status': False,
        'validation_event_count': len(report['validation_events']),
    }

def render_consolidated_gate2_gauntlet_g2_f_v01(report):
    return json.dumps(consolidated_gate2_gauntlet_g2_f_report_to_plain_data_v01(report), ensure_ascii=True, separators=(',', ':'), sort_keys=True) + '\n'

def main():
    report = collect_consolidated_gate2_gauntlet_g2_f_v01()
    print(render_consolidated_gate2_gauntlet_g2_f_v01(report), end='')
    return 0
if __name__ == '__main__':
    raise SystemExit(main())
