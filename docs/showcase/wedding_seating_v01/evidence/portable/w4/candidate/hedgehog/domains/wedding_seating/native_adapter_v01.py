"""Wedding adapters of public native context and Root builders."""
from dataclasses import fields, replace
from datetime import datetime, timezone
from hedgehog import action_commit_packet_v02 as a, work_execution_host_v01 as hosts
from hedgehog import context_packets as packets, structured_rationale as rationale
from hedgehog.kernel import abi_v01 as abi, work_composition_v01 as w
from hedgehog.kernel import root_decision_v01 as roots, semantic_work_v01 as sw, trust_model_v01 as trust
from hedgehog.kernel import execution_mode_router_v01 as router, fractal_runtime_v02 as d, transition_registry_v01 as transitions
from . import native_contracts_v01 as c

def stamp(now):return datetime.fromtimestamp(now,timezone.utc).isoformat()

def root_review(root, transaction, candidate, subject, checks, evidence_ref, bsep, topology, now,
                *, predicate='wedding_route_candidate', kind='ROUTE', permission=None, policy='wedding:hard_policy', time_ref=None,
                claim_value=None):
    c.require(bool(checks) and all(type(v) is bool for v in checks.values()), 'root_checks_actual_boolean')
    req = sw.build_semantic_work_request_v01(request_id='review:'+candidate,transaction_id=transaction,target_root_id=root,
        runtime_topology_ref=topology,bounded_context_refs=(evidence_ref,),permitted_actor_ids=('wedding:local_validator',),
        permitted_contribution_modes=('DETERMINISTIC',),requested_subjects=(subject,),required_evidence_classes=('DEPENDENCY_EVIDENCE',),
        forbidden_claims=('authority_creation',))
    ev = sw.build_evidence_binding_v01(evidence_id='binding:'+evidence_ref,evidence_ref=evidence_ref,evidence_class='DEPENDENCY_EVIDENCE',
        source_component_id='wedding:local_validator',provenance_ref='wedding:local_source',evidence_state='PRESENT')
    claim = sw.build_normalized_claim_v01(claim_id=candidate,subject=subject,predicate=predicate,
        object_or_value=dict(candidate_id=candidate,candidate_kind=kind) if claim_value is None else claim_value,time_envelope_ref='wedding:time:'+str(now),
        provenance_refs=(evidence_ref,),evidence_refs=(ev.evidence_id,),confidence_micros=1000000,
        source_role='deterministic_runtime',source_mode='DETERMINISTIC')
    contribution = sw.build_actor_contribution_v01(contribution_id='contribution:'+candidate,request_id=req.request_id,
        actor_id='wedding:local_validator',actor_role='deterministic_runtime',contribution_mode='DETERMINISTIC',bsep_projection_ref=bsep,
        scope=subject,bounded_context_refs=(evidence_ref,),claims=(claim,),evidence_bindings=(ev,),constraint_bindings=(),
        uncertainty_bindings=(),requested_validators=tuple(sorted(checks)),forbidden_claims_observed=())
    packet = sw.build_root_review_packet_from_contributions_v01(request=req,contributions=(contribution,),
        trust_profiles=trust.build_default_component_trust_profiles_v01())
    valid = all(checks.values())
    kernel = roots.build_root_decision_kernel_v01()
    inputs = roots.build_root_decision_input_v01(transaction_id=transaction,target_root_id=root,root_review_packet=packet,
        post_vv_bundle=dict(bundle_id=c.identity('checks',checks),post_vv_passed=valid,validated_candidate_ids=[candidate] if valid else [],
            rejected_candidate_ids=[] if valid else [candidate],required_evidence_refs=[evidence_ref],provided_evidence_refs=[evidence_ref],
            hard_failure_reasons=[k for k,v in checks.items() if not v]),
        gt_advisory=dict(advisory_id='gt:'+candidate,candidate_ids=[candidate],selected_candidate_id=candidate if valid else None,
            score_micros_by_candidate={candidate:1000000 if valid else 0},source_artifact_type='GTAdvisoryReport',source_lifecycle_state='VALIDATED',
            actor_role='gt',attempted_effect='CREATE_ROOT_DECISION',target_artifact_type='RootDecision',advisory_only=True,
            creates_final_output=False,requests_effect=False),
        policy_state=dict(policy_id=policy,identity_passed=valid,scope_passed=valid,hard_policy_passed=valid,allow_accept=valid,
            conflict_policy='DEFER',no_candidate_policy='NO_UPDATE'),
        permission_state=dict(permission_required=permission is not None,user_permission_present=permission is not None and valid,
            permission_scope_valid=valid,permission_ref=permission),
        temporal_state=dict(temporal_valid=True,expired=False,not_before_satisfied=True,time_envelope_ref=time_ref or 'wedding:time:'+str(now)),
        conflict_state=dict(material_unresolved_conflict=bool(packet.conflict_set_ids),conflict_set_ids=list(packet.conflict_set_ids)),
        prior_root_state=dict(prior_decision_id=None,prior_decision=None,prior_selected_candidate_id=None))
    result = roots.decide_root_v01(kernel=kernel,decision_input=inputs)
    c.require(not roots.validate_root_decision_result_v01(kernel=kernel,decision_input=inputs,result=result), 'root_result_invalid')
    c.require(result.decision == 'ACCEPT', 'root_refusal:'+result.reason_code)
    return kernel, inputs, result

def semantic_source(request, request_id, root, now, orchestrator, *, clock_origin='wedding.controlled_clock'):
    binding_key='semantic_capture_ref' if 'capture_ref' in orchestrator else 'controlled_response_ref'
    summary=c.canonical(dict(task_kind=orchestrator.get('task_kind','BOUNDED_REVIEW'),needs=orchestrator['needs'],
        **{binding_key:orchestrator.get('capture_ref',c.identity('controlled_response',orchestrator))})).decode()
    ref = c.identity('orchestrator', dict(request=request,output=orchestrator))
    transaction = 'transaction:'+request_id
    decision = root_review(root,transaction,ref,request_id,dict(wedding_scope='ORIGINAL_VALIDATION' in orchestrator['needs'],
        no_unresolved_questions=not orchestrator['unresolved']),ref,'wedding:intake:bounded','wedding:route:proposal',now)
    business = packets.build_business_request_context_packet(packet_id='business:'+request_id,created_by='wedding:local_intake',domain='WEDDING_SEATING',
        request_id=request_id,business_subject='bounded_seating',requested_action='bounded_seating',user_visible_summary=request)
    source_ref = dict(source='G2C_BUSINESS_REQUEST_CONTEXT_PACKET_V01',packet_id=business['packet_id'],request_id=request_id,domain_id='WEDDING_SEATING')
    route_id = 'route:wedding:seating'
    vectors, guards = ('vector:'+ref,), ('guard:wedding:current_root',)
    route = packets.build_orchestrator_route_context_packet(packet_id='route_context:'+ref,created_by='wedding:local_canonicalization',source_refs=(source_ref,),
        domain='WEDDING_SEATING',allowed_routes=(route_id,),required_guards=guards,selected_vector_ids=vectors,
        route_validation_expectations=dict(root_review_required=True,selected_only_allowed_vectors=True),orchestrator_is_root=False,
        creates_action_commit_packet=False,calls_connectors=False)
    proposal = dict(proposal_id='proposal:'+ref,suggested_route=route_id,selected_vector_ids=vectors,required_guards=guards,
        reason='Pure seating work under original mandatory conditions.',confidence=0.75,needs_review=True,
        uncertainty_notes=('Semantic proposal is not action permission.',),root_review_required=True,
        truth_claimed=False,authority_claimed=False,action_permission_claimed=False,final_output_claimed=False,
        connector_command_claimed=False,drs_write_claimed=False,plan_graph_claimed=False,bypass_root_claimed=False,
        semantic_observations=(summary,),route_reasoning=('Bounded pure seating computation.',),
        rejected_route_reasoning=('No guest contact, reservation or effect.',),guard_reasoning=('Current Root required per command.',),
        vector_reasoning=('Actual validated Wedding needs.',),authority_boundary_reasoning=('OrganizerRoot alone accepts.',))
    structured = rationale.build_orchestrator_structured_rationale(observed_semantics=proposal['semantic_observations'],
        route_selection_reason=proposal['route_reasoning'],rejected_routes=proposal['rejected_route_reasoning'],
        required_guards_reasoning=proposal['guard_reasoning'],selected_vector_reasoning=proposal['vector_reasoning'],
        uncertainty_notes=proposal['uncertainty_notes'],authority_boundary=proposal['authority_boundary_reasoning'],root_review_required=True)
    def ev(text, kind):
        return packets.semantic_evidence_item(text,source='runtime_canonicalization',evidence_kind=kind,confidence_label='medium')
    bsep = packets.build_bounded_semantic_evidence_packet(packet_id='bsep:'+ref,source_refs=(source_ref,),domain='WEDDING_SEATING',
        source_role='orchestrator',target_role='architect',source_route_id=route_id,source_proposal_id=proposal['proposal_id'],
        source_context_packet_id=route['packet_id'],source_structured_rationale_ref='structured_rationale_v01:'+c.digest(structured),
        observed_semantic_facts=(ev(summary,'observed_fact'),),
        missing_evidence=(ev('Final output requires current OrganizerRoot review.','missing_evidence'),),
        uncertainty_notes=(ev('Proposal only.','uncertainty'),),risk_boundary_notes=(ev('No effects are in this pure task.','risk_boundary'),),
        rejected_action_routes=(ev('No publication.','rejected_route'),),required_approvals_or_conditions=(ev(decision[2].decision_id,'approval_condition'),),
        authority_boundary_notes=(ev('No authority transfer.','authority_boundary'),),selected_vector_ids=vectors,required_guards=guards)
    source = router.build_execution_mode_source_context_v01(business_request_context_packet=business,bsep_packet=bsep,bsep_route_context_packet=route,
        bsep_orchestrator_proposal=proposal,bsep_structured_rationale=structured,sealed_replay_evidence=None,replay_source_manifest=None,
        replay_source_domain_projection=None,replay_source_safe_file_contents=(),replay_anchor_publication=None,replay_anchored_verification=None,
        replay_supplied_anchor_publication_id=None,replay_reconstructed_manifest=None,replay_reconstructed_domain_projection=None,
        replay_reconstructed_safe_file_contents=(),g2a_inspection=None,g2a_registry=None,g2a_packet_id=None,g2a_corridor=None,g2a_corridor_step=None,
        g2a_current_dependency_observations=(),g2a_logical_time_bridge=None,g2a_evaluation_time=now,g2a_evaluation_time_source=clock_origin,
        g2a_evaluation_context_id='wedding:current',g2a_transition_registry_profile=None,g2b_resolution_report=None,g2b_compatibility_projections=(),
        g2b_use_time=None,g2b_root_kernel=None,g2b_root_decision_input=None,g2b_root_decision_result=None,g2b_writeback_evidence=None)
    return source, decision

def source_family(session, common, item, candidate, now):
    scope=w.build_work_review_scope_ref_v01(candidate=candidate,item=item,source_context=common['source_context'],semantic_proposal=common['semantic_proposal'])
    ids=dict(request_id=session.id,transaction_id='transaction:'+session.id,owning_root_id=session.root,domain_id='WEDDING_SEATING')
    profiles=tuple(router.build_execution_mode_local_mode_profile_v01(**ids,mode=mode,policy_snapshot_id='policy:wedding:wedding_review',
        capability_snapshot_id='capabilities:wedding:local',cost_model_id='cost:wedding:bounded',policy_allowed=mode=='full_semantic',
        scope_allowed=True,risk_allowed=True,privacy_allowed=True,capability_state='NOT_REQUIRED' if mode in
        ('sealed_replay','direct_informational_reuse') else 'AVAILABLE',capability_id=None if mode in
        ('sealed_replay','direct_informational_reuse') else 'capability:wedding:'+mode,cost_units=i+1)
        for i,mode in enumerate(router.EXECUTABLE_EXECUTION_MODES_V01))
    snapshot=router.build_execution_mode_local_routing_snapshot_v01(**ids,request_class='BOUNDED_REVIEW',action_class='NON_ACTION',
        action_packet_relation='NOT_APPLICABLE',scope_class='BOUNDED',scope_ref=scope,permitted_narrower_scope_refs=(),risk_class='LOW',
        policy_snapshot_id='policy:wedding:wedding_review',capability_snapshot_id='capabilities:wedding:local',cost_model_id='cost:wedding:bounded',
        required_user_input_state='COMPLETE',hard_block_state='CLEAR',evaluation_time_epoch_seconds=now,pt_created_at_utc=stamp(now),
        et_observed_at_utc=stamp(now),ct_session_anchor=session.id,ttl_seconds=3600,freshness_class='static',
        valid_from_utc=stamp(now),valid_to_utc=stamp(now+3600),mode_profiles=profiles)
    source=router.build_execution_mode_source_context_v01(**dict({f.name:getattr(common['source_context'],f.name) for f in fields(common['source_context'])},
        g2a_evaluation_time=now,g2a_evaluation_time_source=snapshot.created_by,g2a_evaluation_context_id=snapshot.local_routing_snapshot_id))
    routing=router.build_execution_mode_router_input_v01(request_id=session.id,transaction_id=ids['transaction_id'],owning_root_id=session.root,
        bsep_binding=router.build_execution_mode_bsep_binding_v01(**ids,source_context=source),local_routing_snapshot=snapshot,
        replay_binding=router.build_execution_mode_replay_not_applicable_binding_v01(**ids),
        g2a_binding=router.build_execution_mode_g2a_no_packet_binding_v01(**ids,evaluation_time=now,
            evaluation_time_source=snapshot.created_by,evaluation_context_id=snapshot.local_routing_snapshot_id),
        g2b_binding=router.build_execution_mode_g2b_not_applicable_binding_v01(**ids))
    proposal,validated=router.route_execution_mode_v01(router_input=routing,source_context=source)
    c.require(validated.validation_status=='PASS' and proposal.selected_mode=='full_semantic','wedding_C_route')
    artifact=router.project_execution_mode_proposal_kernel_artifact_v01(proposal=proposal,router_input=routing,source_context=source)
    registry=transitions.build_execution_mode_transition_registry_profile_v01()
    before=router.evaluate_execution_mode_proposal_to_root_transition_v01(registry=registry,proposal=proposal,router_input=routing,
        source_context=source,proposal_artifact=artifact)
    ri=router.build_root_execution_mode_review_input_v01(proposal=proposal,router_input=routing,source_context=source,proposal_artifact=artifact,
        proposal_transition_decision=before,review_action='ACCEPT',accepted_scope_ref=scope,narrowing_basis_refs=())
    decision,rk,rinput,result,validated=router.review_execution_mode_proposal_v01(review_input=ri,proposal=proposal,router_input=routing,
        source_context=source,proposal_artifact=artifact,proposal_transition_decision=before)
    c.require(validated.validation_status=='PASS' and decision.outcome=='ACCEPT','wedding_C_Root')
    args=dict(review_input=ri,decision=decision,proposal=proposal,router_input=routing,source_context=source,proposal_artifact=artifact,
        proposal_transition_decision=before,root_kernel=rk,root_decision_input=rinput,root_decision_result=result)
    da=router.project_root_execution_mode_decision_kernel_artifact_v01(**args)
    after=router.evaluate_execution_mode_root_route_transition_v01(registry=registry,**args,decision_artifact=da)
    eligibility=router.project_execution_mode_route_eligibility_kernel_artifact_v01(**args,decision_artifact=da,root_route_transition_decision=after)
    checked=router.validate_execution_mode_route_eligibility_against_source_v01(**args,decision_artifact=da,
        root_route_transition_decision=after,route_eligibility_artifact=eligibility)
    c.require(checked.validation_status=='PASS','wedding_C_eligibility')
    args['g2c_source_context']=args.pop('source_context')
    ds=d.build_fractal_runtime_source_context_v02(**args,transition_registry=registry,decision_artifact=da,root_route_transition_decision=after,
        route_eligibility_artifact=eligibility,runtime_policy=d.build_fractal_runtime_policy_v02(
            required_downstream_capability_ids=proposal.required_downstream_capability_ids,permitted_child_scope_refs=()))
    return ds,dict(common,source_context=source)
