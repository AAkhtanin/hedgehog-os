"""Workspace application-owned BSEP and output review assembly through public APIs."""
import hashlib
from hedgehog import outcome_feedback_consumer_v01 as consumer
from hedgehog.kernel import semantic_work_v01 as sw, trust_model_v01 as trust, root_decision_v01 as roots
from hedgehog.incident_atlas_v01 import canonical_v01, digest_v01, require_v01

def current_source_v01(invocation,clock,material):
    """Application-owned source/BSEP via public builders, without a domain disguise."""
    from hedgehog import context_packets as packets, structured_rationale as rationale
    from hedgehog.kernel import execution_mode_router_v01 as router
    ref=digest_v01(material);route_id='route:workspace:review';vectors=('vector:'+ref,);guards=('guard:workspace:current_root',)
    # BSEP carries finite semantic fields; exact complete material remains bound
    # by its digest and is consumed by the reviewed Work input, without truncation.
    bounded=canonical_v01(dict(material_ref=ref, operation='WORKSPACE_CURRENT_SAVE_CHECK')).decode()
    business=packets.build_business_request_context_packet(packet_id='business:'+invocation,created_by='workspace:local_intake',domain='EPHEMERAL_WORKSPACE',
        request_id=invocation,business_subject='bounded_workspace_review',requested_action='review_confirmed_scope',user_visible_summary='Review the actual current workspace proposal.')
    source_ref=dict(source='G2C_BUSINESS_REQUEST_CONTEXT_PACKET_V01',packet_id=business['packet_id'],request_id=invocation,domain_id='EPHEMERAL_WORKSPACE')
    route=packets.build_orchestrator_route_context_packet(packet_id='route_context:'+ref,created_by='workspace:local_canonicalization',source_refs=(source_ref,),
        domain='EPHEMERAL_WORKSPACE',allowed_routes=(route_id,),required_guards=guards,selected_vector_ids=vectors,
        route_validation_expectations=dict(root_review_required=True,selected_only_allowed_vectors=True),orchestrator_is_root=False,creates_action_commit_packet=False,calls_connectors=False)
    proposal=dict(proposal_id='proposal:'+ref,suggested_route=route_id,selected_vector_ids=vectors,required_guards=guards,
        reason='Review independently confirmed workspace scope.',confidence=0.75,needs_review=True,uncertainty_notes=('Advice is not consent.',),root_review_required=True,
        truth_claimed=False,authority_claimed=False,action_permission_claimed=False,final_output_claimed=False,connector_command_claimed=False,drs_write_claimed=False,plan_graph_claimed=False,bypass_root_claimed=False,
        semantic_observations=(bounded,),route_reasoning=('Finite pure review.',),rejected_route_reasoning=('No real payment or shipment.',),
        guard_reasoning=('Current Root required.',),vector_reasoning=('Exact proposal and policy.',),authority_boundary_reasoning=('Local Root alone decides.',))
    structured=rationale.build_orchestrator_structured_rationale(observed_semantics=proposal['semantic_observations'],route_selection_reason=proposal['route_reasoning'],
        rejected_routes=proposal['rejected_route_reasoning'],required_guards_reasoning=proposal['guard_reasoning'],selected_vector_reasoning=proposal['vector_reasoning'],
        uncertainty_notes=proposal['uncertainty_notes'],authority_boundary=proposal['authority_boundary_reasoning'],root_review_required=True)
    def ev(text,kind):return packets.semantic_evidence_item(text,source='runtime_canonicalization',evidence_kind=kind,confidence_label='medium')
    bsep=packets.build_bounded_semantic_evidence_packet(packet_id='bsep:'+ref,source_refs=(source_ref,),domain='EPHEMERAL_WORKSPACE',source_role='orchestrator',target_role='architect',
        source_route_id=route_id,source_proposal_id=proposal['proposal_id'],source_context_packet_id=route['packet_id'],source_structured_rationale_ref='structured_rationale_v01:'+hashlib.sha256(canonical_v01(structured)).hexdigest(),
        observed_semantic_facts=(ev(bounded,'observed_fact'),),missing_evidence=(ev('Independent current review required.','missing_evidence'),),
        uncertainty_notes=(ev('Proposal only.','uncertainty'),),risk_boundary_notes=(ev('Mock effects require separate packets.','risk_boundary'),),
        rejected_action_routes=(ev('No real effects.','rejected_route'),),required_approvals_or_conditions=(ev('Local current Root review.','approval_condition'),),
        authority_boundary_notes=(ev('No authority transfer.','authority_boundary'),),selected_vector_ids=vectors,required_guards=guards)
    return router.build_execution_mode_source_context_v01(business_request_context_packet=business,bsep_packet=bsep,bsep_route_context_packet=route,
        bsep_orchestrator_proposal=proposal,bsep_structured_rationale=structured,sealed_replay_evidence=None,replay_source_manifest=None,replay_source_domain_projection=None,
        replay_source_safe_file_contents=(),replay_anchor_publication=None,replay_anchored_verification=None,replay_supplied_anchor_publication_id=None,replay_reconstructed_manifest=None,
        replay_reconstructed_domain_projection=None,replay_reconstructed_safe_file_contents=(),g2a_inspection=None,g2a_registry=None,g2a_packet_id=None,g2a_corridor=None,g2a_corridor_step=None,
        g2a_current_dependency_observations=(),g2a_logical_time_bridge=None,g2a_evaluation_time=clock.evaluation_time,g2a_evaluation_time_source=clock.evaluation_time_source,
        g2a_evaluation_context_id=clock.evaluation_context_id,g2a_transition_registry_profile=None,g2b_resolution_report=None,g2b_compatibility_projections=(),g2b_use_time=None,
        g2b_root_kernel=None,g2b_root_decision_input=None,g2b_root_decision_result=None,g2b_writeback_evidence=None)

def output_review_v01(*, root, transaction, candidates, selected, scores, evidence_ref,
                        now, predicate, topology_ref, required=(), provided=(), subjects=None):
    """Build the same public multi-candidate packet consumed by ordinary Root."""
    require_v01(type(now) is int and candidates and selected in candidates,'g34_review_input')
    subjects = subjects or {key:key for key in candidates}
    request=sw.build_semantic_work_request_v01(request_id='g34:request:'+consumer.identity('request',dict(
        root=root,transaction=transaction,candidates=candidates,predicate=predicate,now=now)),
        transaction_id=transaction,target_root_id=root,runtime_topology_ref=topology_ref,
        bounded_context_refs=(evidence_ref,),permitted_actor_ids=('g34:local_validator',),
        permitted_contribution_modes=('DETERMINISTIC',),requested_subjects=tuple(sorted(set(subjects.values()))),
        required_evidence_classes=('DEPENDENCY_EVIDENCE',),forbidden_claims=('authority_creation',))
    binding=sw.build_evidence_binding_v01(evidence_id='binding:'+evidence_ref,evidence_ref=evidence_ref,
        evidence_class='DEPENDENCY_EVIDENCE',source_component_id='g34:local_validator',
        provenance_ref='g34:independent_sources',evidence_state='PRESENT')
    claims=tuple(sw.build_normalized_claim_v01(claim_id=key,subject=subjects[key],predicate=predicate,
        object_or_value=value,time_envelope_ref='g34:time:'+str(now),provenance_refs=(evidence_ref,),
        evidence_refs=(binding.evidence_id,),confidence_micros=1000000,
        source_role='deterministic_runtime',source_mode='DETERMINISTIC') for key,value in sorted(candidates.items()))
    contribution=sw.build_actor_contribution_v01(contribution_id='g34:contribution:'+request.request_id,
        request_id=request.request_id,actor_id='g34:local_validator',actor_role='deterministic_runtime',
        contribution_mode='DETERMINISTIC',bsep_projection_ref='g34:bounded_review:bsep',scope='g34:current_review',
        bounded_context_refs=(evidence_ref,),claims=claims,evidence_bindings=(binding,),constraint_bindings=(),
        uncertainty_bindings=(),requested_validators=('g34:source_binding',),forbidden_claims_observed=())
    packet=sw.build_root_review_packet_from_contributions_v01(request=request,contributions=(contribution,),
        trust_profiles=trust.build_default_component_trust_profiles_v01())
    kernel=roots.build_root_decision_kernel_v01()
    decision_input=roots.build_root_decision_input_v01(transaction_id=transaction,target_root_id=root,root_review_packet=packet,
        post_vv_bundle=dict(bundle_id=consumer.identity('postvv',dict(candidates=candidates,required=required,provided=provided)),
            post_vv_passed=True,validated_candidate_ids=sorted(candidates),rejected_candidate_ids=[],
            required_evidence_refs=[evidence_ref,*required],provided_evidence_refs=[evidence_ref,*provided],hard_failure_reasons=[]),
        gt_advisory=dict(advisory_id='g34:gt:'+consumer.identity('ranking',dict(selected=selected,scores=scores)),
            candidate_ids=sorted(candidates),selected_candidate_id=selected,score_micros_by_candidate=scores,
            source_artifact_type='GTAdvisoryReport',source_lifecycle_state='VALIDATED',actor_role='gt',
            attempted_effect='CREATE_ROOT_DECISION',target_artifact_type='RootDecision',advisory_only=True,
            creates_final_output=False,requests_effect=False),
        policy_state=dict(policy_id='g34:bounded_current_review',identity_passed=True,scope_passed=True,hard_policy_passed=True,
            allow_accept=True,conflict_policy='DEFER',no_candidate_policy='NO_UPDATE'),
        permission_state=dict(permission_required=False,user_permission_present=False,permission_scope_valid=True,permission_ref=None),
        temporal_state=dict(temporal_valid=True,expired=False,not_before_satisfied=True,time_envelope_ref='g34:time:'+str(now)),
        conflict_state=dict(material_unresolved_conflict=bool(packet.conflict_set_ids),conflict_set_ids=list(packet.conflict_set_ids)),
        prior_root_state=dict(prior_decision_id=None,prior_decision=None,prior_selected_candidate_id=None))
    result=roots.decide_root_v01(kernel=kernel,decision_input=decision_input)
    require_v01(not roots.validate_root_decision_result_v01(kernel=kernel,decision_input=decision_input,result=result),'g34_root_result')
    return kernel,decision_input,result
