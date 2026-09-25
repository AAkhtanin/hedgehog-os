"""Actual common B/C/D/E evidence for a bounded media task, never effect authority."""
from dataclasses import fields, replace, asdict
from datetime import datetime, timezone
import json
import time

from hedgehog import action_commit_packet_v02 as a, work_execution_host_v01 as hosts
from hedgehog import drs_semantic_address_v01 as address, drs_memory_resolution_v01 as memory
from hedgehog import drs_g2b_compatibility_v01 as compatibility, reuse_certificate_v01 as reuse
from hedgehog.kernel import abi_v01 as abi, execution_mode_router_v01 as router
from hedgehog.kernel import fractal_runtime_v02 as d, continuous_delta_runtime_v01 as e
from hedgehog.kernel import work_composition_v01 as w, transition_registry_v01 as transitions
from hedgehog.kernel import integrity_replay_v01 as integrity
from . import contracts_v01 as c, kernel_adapter_v01 as kernel, capability_registry_v01 as caps


def stamp(now):
    return datetime.fromtimestamp(now, timezone.utc).isoformat()


def information(session, material, now):
    """Session-local historical information for E's B contract; not warm DRS reuse."""
    scope=c.digest(dict(session=session.id,material=material))
    ref=c.digest(material)
    review=kernel.root_review(session.root,'transaction:'+session.id,ref,session.id,
        dict(actual_contract=material['contract']==session.contract),ref,session.program.candidate.bsep_ref,
        session.program.topology_artifact.artifact_id,now,claim_value=material)
    addr=address.build_semantic_address_v01(namespace='ews',domain='EPHEMERAL_WORKSPACE',
        subject_class='bounded_media_contract',intent_class='informational_summary',
        meaning_schema_id='ews.media_contract',meaning_schema_version='v0.1')
    envelope=address.build_drs_time_envelope_v01(pt_created_at=now,kt_as_of=now,et_observed_at=now,ct_context_anchor=now,
        ttl_seconds=3600,valid_from=now,valid_to=now+3600,source_observed_at=now,source_reported_at=now,
        system_ingested_at=now,system_verified_at=now,freshness_policy_id='freshness:ews:media')
    authority=address.build_drs_authority_envelope_v01(authority_class='ROOT_ACCEPTED_WORK',owning_local_root_id=session.root,
        source_root_decision_input_id=review[1].decision_input_id,source_root_decision_id=review[2].decision_id,
        source_root_decision_hash=c.digest(kernel.roots.root_decision_result_to_plain_dict_v01(review[2])),
        authority_scope_fingerprint=scope,root_acceptance_state='ACCEPTED_WORK',recording_component='ews:media_information')
    record=address.build_meaning_record_v01(semantic_address=addr,predecessor_record_id=None,supersession_reason=None,
        safe_summary='Bounded frame sequence and PCM track. Preserve photo work. Audio policy: '+
            material['contract']['media']['audio_policy']+'. Sources read-only; no publication; separate selected-only save.',
        semantic_tags=('media',),resonance_reason='Exact current session media contract.',
        memory_pointers=(),artifact_pointers=(),source_reference_ids=(ref,),lineage_edges=(),time_envelope=envelope,
        authority_envelope=authority,persistent_lifecycle_state='ACTIVE',risk_hints=(),conflict_hints=(),
        reuse_policy_class='ANSWER_SHORTCUT',policy_version='ews.media.v01',schema_versions=('ews.media.v01',),
        content_fingerprint=c.digest(material),recording_component='ews:media_information')
    query=memory.build_drs_temporal_query_v01(query_mode='DIRECT_REUSE_CANDIDATE',semantic_address_id=addr.semantic_address_id,
        scope_fingerprint=scope,as_of=now,evaluation_time=now,evaluation_time_source='INJECTED_CURRENT_DECISION_TIME',
        time_range_start=now,time_range_end=now+3600,required_time_axes=('PT','KT','ET','CT','TTL','VALIDITY'),
        freshness_policy_id=envelope.freshness_policy_id,max_age_seconds=3600,domain=addr.domain,risk_class='LOW',
        reuse_intent='INFORMATIONAL_SHORTCUT_CONSIDERATION',requested_reuse_classes=('ANSWER_SHORTCUT',),
        required_evidence_classes=('SOURCE_IDENTITY','SOURCE_INTEGRITY','PROVENANCE_CHAIN','TIME_FITNESS','POLICY_COMPATIBILITY',
            'SCHEMA_COMPATIBILITY','CONFLICT_CLEARANCE','ROOT_DECISION','SOURCE_HISTORY'),forbidden_changes=('POLICY_CHANGED',),
        policy_version=record.policy_version,schema_versions=record.schema_versions,owning_local_root_id=session.root)
    ev=memory.evaluate_drs_candidate_v01(semantic_address=addr,query=query,meaning_record=record)
    c.require(ev.eligible_for_ranking,'media_information_ineligible:'+repr(ev.reason_codes))
    candidate=memory.build_resolution_candidate_v01(query_id=query.query_id,semantic_address_id=addr.semantic_address_id,
        meaning_record_id=record.meaning_record_id,query_evaluation_id=ev.query_evaluation_id,safe_summary=record.safe_summary,
        evidence_ref_ids=record.source_reference_ids,source_history_hash=ev.source_history_hash,action_history_binding_id=None,
        semantic_similarity_units=10000,freshness_units=ev.current_freshness_units,source_authority_prior_units=10000,
        lineage_proximity_units=10000,historical_utility_units=0,gt_advisory_prior_units=0,conflict_penalty_units=0,risk_penalty_units=0,retrieval_cost_units=1)
    ranked=memory.rank_eligible_drs_candidates_v01(query=query,query_evaluations=(ev,),candidates=(candidate,))
    budget=memory.build_memory_descent_budget_v01(max_depth=0,max_records_opened=1,max_pointers_opened=0,max_artifacts_opened=0,
        max_bytes_opened=0,max_lineage_edges=0,max_conflict_records=0)
    plan=memory.build_retrieval_plan_v01(query_id=query.query_id,semantic_address_id=addr.semantic_address_id,
        proposed_record_ids=(record.meaning_record_id,),proposed_memory_pointer_ids=(),proposed_artifact_pointer_ids=(),
        requested_descent_class='SUMMARY_ONLY',proposed_budget_id=budget.memory_descent_budget_id,required_access_policy_ids=(),reason_codes=())
    claim=dict(profile_version='v0.1',semantic_address_id=addr.semantic_address_id,meaning_record_id=record.meaning_record_id,
        query_id=query.query_id,query_evaluation_id=ev.query_evaluation_id,resolution_candidate_id=candidate.resolution_candidate_id,
        reuse_class='ANSWER_SHORTCUT',case_type='NON_ACTION_INFORMATIONAL',scope_fingerprint=scope,policy_version=query.policy_version,
        schema_versions=list(query.schema_versions),required_evidence_classes=list(query.required_evidence_classes),
        observed_evidence_fingerprint=ev.observed_evidence_fingerprint,forbidden_changes=list(query.forbidden_changes),
        checked_dependency_fingerprint=ev.checked_dependency_fingerprint,source_history_hash=ev.source_history_hash,
        action_history_binding_id=None,valid_from=now,valid_to=now+3600,issued_at=now,evaluated_at=now,
        root_shortcut_policy_ref='policy:drs_answer_shortcut:v0.1')
    review=kernel.root_review(session.root,query.query_id,candidate.resolution_candidate_id,addr.semantic_address_id,
        dict(eligible=ev.eligible_for_ranking,ranking=ranked==(candidate,)),ref,session.program.candidate.bsep_ref,
        session.program.topology_artifact.artifact_id,now,predicate='authorize_non_action_informational_answer_shortcut_v01',claim_value=claim)
    root_hash=a.domain_separated_sha256_hex_v01(domain='hedgehog:drs:root_shortcut_root_result_binding:v01',
        payload=c.canonical(kernel.roots.root_decision_result_to_plain_dict_v01(review[2])))
    shortcut=reuse.build_root_shortcut_authorization_projection_v01(owning_local_root_id=session.root,root_kernel_id=review[0].kernel_id,
        root_decision_input_id=review[1].decision_input_id,root_decision_id=review[2].decision_id,root_decision_hash=root_hash,
        selected_candidate_id=candidate.resolution_candidate_id,semantic_address_id=addr.semantic_address_id,meaning_record_id=record.meaning_record_id,
        query_id=query.query_id,query_evaluation_id=ev.query_evaluation_id,allowed_reuse_class='ANSWER_SHORTCUT',scope_fingerprint=scope,
        policy_version=query.policy_version,schema_versions=query.schema_versions,valid_from=now,valid_to=now+3600,
        root_shortcut_policy_ref=claim['root_shortcut_policy_ref'])
    certificate=reuse.build_reuse_certificate_v01(semantic_address_id=addr.semantic_address_id,meaning_record_id=record.meaning_record_id,
        query_id=query.query_id,query_evaluation_id=ev.query_evaluation_id,resolution_candidate_id=candidate.resolution_candidate_id,
        root_shortcut_authorization_projection=shortcut,case_type=claim['case_type'],required_evidence_classes=query.required_evidence_classes,
        observed_evidence_fingerprint=ev.observed_evidence_fingerprint,forbidden_changes=query.forbidden_changes,
        checked_dependency_fingerprint=ev.checked_dependency_fingerprint,valid_from=now,valid_to=now+3600,reuse_class='ANSWER_SHORTCUT',
        source_history_hash=ev.source_history_hash,action_history_binding_id=None,issued_at=now,evaluated_at=now)
    legacy=dict(record_id=record.meaning_record_id,layer='work',type='generic',domain=addr.domain,content=dict(summary=record.safe_summary),
        time_envelope=dict(pt_created_at=stamp(now),kt_asof=stamp(now),et_observed_at=stamp(now),ct_session_anchor=session.id,
            ttl_seconds=3600,freshness_class='static',valid_from=stamp(now),valid_to=stamp(now+3600)),
        provenance=dict(request_id=session.id,created_by='root_orchestrator',trace_refs=[dict(trace_id=ref)]),status='active')
    projection=compatibility.build_legacy_drs_projection_v01(source_family='LOCAL_DRS_DICT',source=legacy,target_semantic_address=addr)
    report=memory.build_drs_resolution_report_v01(semantic_address=addr,query=query,source_projections=(projection,),source_records=(record,),
        query_evaluations=(ev,),eligible_candidates=(candidate,),ranked_candidate_ids=(candidate.resolution_candidate_id,),
        selected_candidate_id=candidate.resolution_candidate_id,retrieval_plan=plan,memory_descent_result=None,root_shortcut_projection=shortcut,
        reuse_certificate=certificate,context_only_record_ids=(),historical_only_record_ids=(),warning_only_record_ids=(),
        rerun_required_record_ids=(),blocked_record_ids=(),provider_calls=0,network_calls=0,gemini_calls=0,external_drs_calls=0,
        connector_calls=0,real_world_effects_count=0,final_status='PASS',reason_codes=())
    c.require(reuse.validate_existing_root_shortcut_decision_v01(resolution_report=report,root_kernel=review[0],
        root_decision_input=review[1],root_decision_result=review[2],use_time=now)[0],'media_information_root_binding')
    return report,review


def source_family(session, common, item, candidate, now, information_pair):
    report,review=information_pair
    scope=w.build_work_review_scope_ref_v01(candidate=candidate,item=item,source_context=common['source_context'],semantic_proposal=common['semantic_proposal'])
    ids=dict(request_id=session.id,transaction_id=report.query.query_id,owning_root_id=session.root,domain_id=report.query.domain)
    profiles=tuple(router.build_execution_mode_local_mode_profile_v01(**ids,mode=mode,policy_snapshot_id='policy:ews:media_review',
        capability_snapshot_id='capabilities:ews:local',cost_model_id='cost:ews:bounded',policy_allowed=mode=='full_fractal',
        scope_allowed=True,risk_allowed=True,privacy_allowed=True,capability_state='NOT_REQUIRED' if mode in
        ('sealed_replay','direct_informational_reuse') else 'AVAILABLE',capability_id=None if mode in
        ('sealed_replay','direct_informational_reuse') else 'capability:ews:'+mode,cost_units=i+1)
        for i,mode in enumerate(router.EXECUTABLE_EXECUTION_MODES_V01))
    snapshot=router.build_execution_mode_local_routing_snapshot_v01(**ids,request_class='BOUNDED_REVIEW',action_class='NON_ACTION',
        action_packet_relation='NOT_APPLICABLE',scope_class='BOUNDED',scope_ref=scope,permitted_narrower_scope_refs=(),risk_class='LOW',
        policy_snapshot_id='policy:ews:media_review',capability_snapshot_id='capabilities:ews:local',cost_model_id='cost:ews:bounded',
        required_user_input_state='COMPLETE',hard_block_state='CLEAR',evaluation_time_epoch_seconds=now,pt_created_at_utc=stamp(now),
        et_observed_at_utc=stamp(now),ct_session_anchor=session.id,ttl_seconds=3600,freshness_class='static',
        valid_from_utc=stamp(now),valid_to_utc=stamp(now+3600),mode_profiles=profiles)
    source=router.build_execution_mode_source_context_v01(**dict({f.name:getattr(common['source_context'],f.name) for f in fields(common['source_context'])},
        g2a_evaluation_time=now,g2a_evaluation_time_source=snapshot.created_by,g2a_evaluation_context_id=snapshot.local_routing_snapshot_id,
        g2b_resolution_report=report,g2b_compatibility_projections=report.source_projections,g2b_use_time=now,
        g2b_root_kernel=review[0],g2b_root_decision_input=review[1],g2b_root_decision_result=review[2]))
    routing=router.build_execution_mode_router_input_v01(request_id=session.id,transaction_id=ids['transaction_id'],owning_root_id=session.root,
        bsep_binding=router.build_execution_mode_bsep_binding_v01(**ids,source_context=source),local_routing_snapshot=snapshot,
        replay_binding=router.build_execution_mode_replay_not_applicable_binding_v01(**ids),
        g2a_binding=router.build_execution_mode_g2a_no_packet_binding_v01(**ids,evaluation_time=now,
            evaluation_time_source=snapshot.created_by,evaluation_context_id=snapshot.local_routing_snapshot_id),
        g2b_binding=router.build_execution_mode_g2b_binding_v01(**ids,source_context=source))
    proposal,validated=router.route_execution_mode_v01(router_input=routing,source_context=source)
    c.require(validated.validation_status=='PASS' and proposal.selected_mode=='full_fractal','media_C_route')
    artifact=router.project_execution_mode_proposal_kernel_artifact_v01(proposal=proposal,router_input=routing,source_context=source)
    registry=transitions.build_execution_mode_transition_registry_profile_v01()
    before=router.evaluate_execution_mode_proposal_to_root_transition_v01(registry=registry,proposal=proposal,router_input=routing,
        source_context=source,proposal_artifact=artifact)
    ri=router.build_root_execution_mode_review_input_v01(proposal=proposal,router_input=routing,source_context=source,proposal_artifact=artifact,
        proposal_transition_decision=before,review_action='ACCEPT',accepted_scope_ref=scope,narrowing_basis_refs=())
    decision,rk,rinput,result,validated=router.review_execution_mode_proposal_v01(review_input=ri,proposal=proposal,router_input=routing,
        source_context=source,proposal_artifact=artifact,proposal_transition_decision=before)
    c.require(validated.validation_status=='PASS' and decision.outcome=='ACCEPT','media_C_Root')
    args=dict(review_input=ri,decision=decision,proposal=proposal,router_input=routing,source_context=source,proposal_artifact=artifact,
        proposal_transition_decision=before,root_kernel=rk,root_decision_input=rinput,root_decision_result=result)
    da=router.project_root_execution_mode_decision_kernel_artifact_v01(**args)
    after=router.evaluate_execution_mode_root_route_transition_v01(registry=registry,**args,decision_artifact=da)
    eligibility=router.project_execution_mode_route_eligibility_kernel_artifact_v01(**args,decision_artifact=da,root_route_transition_decision=after)
    args['g2c_source_context']=args.pop('source_context')
    ds=d.build_fractal_runtime_source_context_v02(**args,transition_registry=registry,decision_artifact=da,root_route_transition_decision=after,
        route_eligibility_artifact=eligibility,runtime_policy=d.build_fractal_runtime_policy_v02(
            required_downstream_capability_ids=proposal.required_downstream_capability_ids,permitted_child_scope_refs=()))
    return ds,dict(common,source_context=source)


def assemble(session, material):
    """D review gates a real pure Work item whose output is the finite media plan."""
    now=session.source.sample().evaluation_time
    info=information(session,material,now)
    session.media_transaction=info[0].query.query_id
    source,_=kernel.semantic_source(session.request,session.id,session.root,now,session.semantic_responses[0])
    proposal=abi.build_kernel_artifact_v01(abi_version='v1.0',artifact_id=c.identity('media_semantics',material),
        artifact_type='SemanticArchitectProposal',schema_version='v1',transaction_id=session.media_transaction,owner_root_id=session.root,
        source_component='semantic_architect',authority_class='ADVISORY',lifecycle_state='PROPOSED',payload=material,
        trace_refs=('intent:'+session.id,),parent_refs=(source.bsep_packet['packet_id'],),time_envelope=dict(pt_created_at=stamp(now),
            kt_asof=stamp(now),et_observed_at=None,ct_session_anchor=session.id,ttl_seconds=3600,freshness_class='static',
            valid_from=stamp(now),valid_to=stamp(now+3600)))
    admitted=next(x for x in session.catalogue if x.definition.operation_id=='ews.media_contract.v01')
    common=dict(catalogue=session.catalogue,source_context=source,semantic_proposal=proposal)
    item=w.WorkItemV01('media_contract',admitted.definition.definition_id,session.root,
        (w.WorkInputBindingV01('material',w.WorkLiteralV01(caps.records(dict(material=('TEXT',c.canonical(material).decode())))[0])),),(),(),None,None)
    params=dict(task_id=session.id,previous_revision_id=None,intent_ref='intent:'+session.id,bsep_ref=source.bsep_packet['packet_id'],
        semantic_proposal_ref=proposal.artifact_id,catalogue_revision=0,budget=w.WorkBudgetV01(4,4,0,4,0),items=(item,),trigger_evidence_refs=())
    candidate=w.build_work_program_candidate_v01(**params,**common)
    ds,common=source_family(session,common,item,candidate,now,info)
    candidate=w.build_work_program_candidate_v01(**params,**common)
    obligation=w.build_work_review_obligation_v01(candidate=candidate,item=item,source_context=ds)
    item=replace(item,review_obligation_id=obligation.obligation_id)
    candidate=w.build_work_program_candidate_v01(**dict(params,items=(item,)),**common)
    program=w.materialize_work_program_v01(candidate,**common)
    obligation=w.build_work_review_obligation_v01(candidate=candidate,item=item,source_context=ds)
    session.journal('COMMON_D_START')
    start=time.monotonic();bundle,report=d.run_fractal_runtime_v02(ds)
    session.timings.append(dict(phase='common_D',seconds=time.monotonic()-start))
    session.journal('COMMON_D_RETURN',status=report.status,reasons=list(report.reason_codes))
    c.require(bundle is not None and report.status=='PASS','media_D:'+repr(report.reason_codes))
    bindings=((obligation,ds,bundle),)
    c.require(w.validate_work_review_binding_v01(obligation,candidate=candidate,item=item,source_context=ds,
        execution_bundle=bundle,semantic_proposal=proposal)[0],'media_D_work_binding')
    results=w.advance_work_program_v01(program,**common,host_map={session.root:session.host},review_bindings=bindings)
    ok,reasons=w.validate_work_program_result_v01(program,results,**common,host_map={session.root:session.host},review_bindings=bindings)
    c.require(ok and len(results)==1 and results[0].status=='COMPLETED','media_work:'+repr(reasons))
    artifact=w.work_program_result_to_artifact_v01(program,results,**common,host_map={session.root:session.host},review_bindings=bindings)
    output=json.loads(caps.values(results[0].result.output)['material'])
    return dict(now=now,information=info,source=ds,bundle=bundle,report=report,program=program,common=common,
        obligation=obligation,results=results,artifact=artifact,output=output,material=material)


def source_artifact(payload, session, now, parents=()):
    ref=c.identity('media_source',dict(payload=payload,transaction=session.media_transaction,root=session.root,time=now,parents=parents))
    return abi.build_kernel_artifact_v01(abi_version='v1.0',artifact_id=ref,artifact_type='SemanticEvidence',schema_version='v1',
        transaction_id=session.media_transaction,owner_root_id=session.root,source_component='ews:local_media_observation',
        authority_class='EVIDENCE_ONLY',lifecycle_state='VALIDATED',payload=payload,trace_refs=('trace:'+ref,),parent_refs=parents,
        time_envelope=dict(pt_created_at=stamp(now),kt_asof=stamp(now),et_observed_at=stamp(now),ct_session_anchor=session.media_transaction,
            ttl_seconds=3600,freshness_class='static',valid_from=stamp(now),valid_to=stamp(now+3600)))


def prepare_delta_baseline(session):
    baseline=session.media_review['bundle'];pending=session.media_pending
    now=session.source.sample().evaluation_time
    prior=pending['authorization']['root_bound'].canonical_projection.dependency_candidate.dependency_records[0]
    original=source_artifact(dict(asdict(prior),source_provenance_refs=list(prior.source_provenance_refs),
        audio_source=session.media_dependency()),session,now)
    photo=source_artifact(session.media_review['material']['photo_work'],session,now)
    projections=[]
    for index in (0,1):
        topology=baseline.topology;source=baseline.source_context
        child=d.derive_fractal_child_cell_id_v02(topology_seed_id=topology.topology_seed_id,parent_cell_id=topology.root_cell_id,
            canonical_child_index=index,accepted_mode=topology.accepted_mode,
            selected_local_mode_profile_id=source.proposal.selected_local_mode_profile_id,
            source_mode_profile_set_id=source.router_input.local_routing_snapshot.mode_profile_set_id,
            child_scope_ref=topology.accepted_scope_ref,runtime_policy_id=topology.runtime_policy_id,
            required_capability_ids=source.proposal.required_downstream_capability_ids,forbidden_claims=source.runtime_policy.forbidden_claims,child_depth=1)
        entries=[q for q in baseline.queue_entries if q.cell_id==child and q.predecessor_queue_entry_id is None]
        c.require(bool(entries),'media_actual_D_child')
        q=min(entries,key=lambda v:(v.canonical_priority,v.node_instance_sequence,v.snapshot_sequence))
        artifact=next(a for v,a in zip(baseline.queue_entries,baseline.queue_artifacts,strict=True) if v.queue_entry_id==q.queue_entry_id)
        plain=abi.kernel_artifact_to_plain_dict_v01(artifact)
        projection=source_artifact(dict(projection_profile_id='g2e_baseline_runtime_artifact_projection_v01',
            projected_runtime_artifact=plain,projected_runtime_artifact_sha256=c.digest(plain)),session,now,(artifact.artifact_id,))
        projections.append((child,projection))
    artifacts=(original,projections[0][1],photo,projections[1][1])
    edges=(integrity.ArtifactDependencyEdgeV01(projections[0][1].artifact_id,original.artifact_id),
        integrity.ArtifactDependencyEdgeV01(projections[1][1].artifact_id,photo.artifact_id))
    manifest=integrity.build_artifact_manifest_v01(transaction_id=session.media_transaction,profile=integrity.build_default_seal_profile_v01(),
        artifacts=tuple(abi.kernel_artifact_to_canonical_ref_v01(v) for v in artifacts),dependency_edges=edges,
        root_ownership_bindings=tuple(integrity.RootOwnershipBindingV01(v.artifact_id,session.root) for v in artifacts),
        evidence_class_bindings=tuple(integrity.EvidenceClassBindingV01(v.artifact_id,'SOURCE_EVIDENCE') for v in artifacts),
        authority_class_bindings=tuple(integrity.AuthorityClassBindingV01(v.artifact_id,v.authority_class) for v in artifacts))
    replay=integrity.verify_artifact_replay_v01(manifest=manifest,
        payload_rows=tuple((v.artifact_id,abi.kernel_artifact_to_plain_dict_v01(v)['payload']) for v in artifacts),expected_manifest_hash=manifest.manifest_hash)
    return dict(artifacts=artifacts,edges=edges,projections=projections,manifest=manifest,replay=replay)


def delta_arguments(session, capture, invalidation, observed_time):
    base=session.media_baseline;review=session.media_review;baseline=review['bundle'];b=review['information'][0]
    prior=base['artifacts'][0];old=abi.kernel_artifact_to_plain_dict_v01(prior)
    observed=source_artifact(dict(old['payload'],content_sha256=invalidation.evidence_sha256,audio_source=session.media_dependency(),
        observed_status=invalidation.observed_status,invalidation_evidence_id=invalidation.invalidation_evidence_id,
        packet_id=invalidation.packet_id),session,observed_time,(prior.artifact_id,))
    source=e.build_continuous_delta_source_context_v01(integrity_manifest=base['manifest'],integrity_replay=base['replay'],
        baseline_source_artifacts=base['artifacts'],observed_source_artifacts=(observed,*base['artifacts'][1:]),
        g2a_registry=capture.registry,g2a_packet=capture.root_bound_packet,
        g2a_dependency_candidate=capture.root_bound_packet.canonical_projection.dependency_candidate,
        g2a_current_observations=capture.observations,g2a_root_invalidation_material=invalidation,
        g2b_resolution_report=b,g2b_reuse_certificate=b.reuse_certificate,g2b_writeback_evidence=None,
        g2c_source_context=baseline.source_context.g2c_source_context,
        baseline_g2c_route_eligibility_artifact=baseline.source_context.route_eligibility_artifact,baseline_g2d_execution_bundle=baseline,
        root_kernel=baseline.source_context.root_kernel,post_vv_profile=None,gt_profile=None,
        current_source_host=session.host,current_source_capture=capture)
    common=dict(transaction_id=b.query.query_id,owning_root_id=session.root,domain_id=b.query.domain,policy_version=b.query.policy_version,
        schema_versions=b.query.schema_versions,source_history_hash=b.query_evaluations[0].source_history_hash)
    edge_bindings=tuple((v.artifact_id,v.depends_on_artifact_id,('/content_sha256',) if v.depends_on_artifact_id==prior.artifact_id else (),
        'FIELD_CAUSAL' if v.depends_on_artifact_id==prior.artifact_id else 'ARTIFACT_DEPENDENCY') for v in base['edges'])
    basis,edges=e.project_integrity_replay_dependency_edges_v01(manifest=base['manifest'],replay=base['replay'],
        source_artifacts=base['artifacts'],graph_version=e.CONTINUOUS_DELTA_GRAPH_VERSION_V01,edge_projection_bindings=edge_bindings,**common)
    graph=e.build_dependency_graph_index_v01(graph_basis_sha256=basis,graph_version=e.CONTINUOUS_DELTA_GRAPH_VERSION_V01,
        manifest=base['manifest'],replay=base['replay'],source_artifacts=base['artifacts'],dependency_edges=edges,trace_refs=(prior.artifact_id,),**common)
    profile=e.build_dependency_fingerprint_profile_v01()
    fingerprints=tuple(e.build_dependency_fingerprint_v01(profile=profile,graph=graph,dependency_edges=edges,source_artifacts=artifacts,
        policy_version=b.query.policy_version,schema_versions=b.query.schema_versions,source_history_hash=common['source_history_hash'])
        for artifacts in (source.baseline_source_artifacts,source.observed_source_artifacts))
    new=abi.kernel_artifact_to_plain_dict_v01(observed)
    binding=e.build_delta_source_binding_v01(request_id=baseline.runtime_report.request_id,transaction_id=common['transaction_id'],
        owning_root_id=session.root,domain_id=common['domain_id'],baseline_source_artifact_id=prior.artifact_id,
        baseline_source_artifact_type=prior.artifact_type,baseline_source_artifact_sha256=c.digest(old),baseline_source_payload_sha256=c.digest(old['payload']),
        observed_source_artifact_id=observed.artifact_id,observed_source_artifact_type=observed.artifact_type,
        observed_source_artifact_sha256=c.digest(new),observed_source_payload_sha256=c.digest(new['payload']),
        baseline_report_id=baseline.runtime_report.report_id,baseline_graph_id=graph.graph_id,baseline_graph_version=graph.graph_version,
        baseline_policy_version=b.query.policy_version,observed_policy_version=b.query.policy_version,
        baseline_schema_versions=b.query.schema_versions,observed_schema_versions=b.query.schema_versions,
        baseline_source_history_hash=common['source_history_hash'],observed_source_history_hash=common['source_history_hash'],
        valid_from_utc=stamp(observed_time),valid_to_utc=stamp(observed_time+3600),trace_refs=(prior.artifact_id,observed.artifact_id))
    changed=e.build_changed_field_binding_v01(source_binding_id=binding.source_binding_id,json_pointer='/payload/content_sha256',
        prior_value_sha256=c.digest(old['payload']['content_sha256']),observed_value_sha256=c.digest(new['payload']['content_sha256']),
        change_class='FIELD_VALUE_CHANGE',observed_at_utc=stamp(observed_time),trace_refs=(binding.source_binding_id,))
    artifact=e.build_changed_artifact_binding_v01(source_binding_id=binding.source_binding_id,baseline_artifact_id=prior.artifact_id,
        baseline_artifact_type=prior.artifact_type,baseline_payload_sha256=c.digest(old['payload']),observed_artifact_id=observed.artifact_id,
        observed_artifact_type=observed.artifact_type,observed_payload_sha256=c.digest(new['payload']),baseline_dependency_fingerprint=fingerprints[0],
        observed_dependency_fingerprint=fingerprints[1],change_class='ARTIFACT_SUCCESSOR',observed_at_utc=stamp(observed_time),trace_refs=(binding.source_binding_id,))
    delta=e.build_world_state_delta_v01(ordered_source_binding_ids=(binding.source_binding_id,),request_id=binding.request_id,
        transaction_id=binding.transaction_id,owning_root_id=binding.owning_root_id,domain_id=binding.domain_id,
        baseline_report_id=baseline.runtime_report.report_id,baseline_graph_id=graph.graph_id,baseline_graph_version=graph.graph_version,
        observed_at_utc=stamp(observed_time),valid_from_utc=stamp(observed_time),valid_to_utc=stamp(observed_time+3600),
        baseline_policy_version=b.query.policy_version,observed_policy_version=b.query.policy_version,
        baseline_schema_versions=b.query.schema_versions,observed_schema_versions=b.query.schema_versions,
        baseline_source_history_hash=common['source_history_hash'],observed_source_history_hash=common['source_history_hash'],
        ordered_changed_field_binding_ids=(changed.changed_field_binding_id,),ordered_changed_artifact_binding_ids=(artifact.changed_artifact_binding_id,),
        dependency_fingerprint_before=fingerprints[0],dependency_fingerprint_after=fingerprints[1],trace_refs=(graph.graph_id,))
    return dict(source_context=source,source_bindings=(binding,),changed_field_bindings=(changed,),changed_artifact_bindings=(artifact,),
        delta=delta,dependency_edges=edges,dependency_graph=graph,retained_profile='fractal_retained_work_v01')


def consume_delta(session, bundle):
    """Follow the real changed-source -> D output chain before consuming availability."""
    source=bundle.source_context.observed_source_artifacts[0]
    payload=abi.kernel_artifact_to_plain_dict_v01(source)['payload']
    c.require(payload['audio_source']==session.loss_dependency and payload['audio_source']['audio_available'] is False,
        'media_delta_actual_source')
    c.require(bundle.final_root_decision_result.target_root_id==session.root and bundle.final_root_decision_result.decision=='ACCEPT','media_delta_Root')
    baseline=bundle.source_context.baseline_g2d_execution_bundle
    cell=session.media_baseline['projections'][0][0]
    prior=next(v.artifact_id for r,v in zip(baseline.cell_results,baseline.result_artifacts,strict=True) if r.cell_id==cell)
    bindings=tuple(v for v in bundle.recomputed_bindings if v.prior_artifact_id==prior)
    c.require(len(bindings)==1,'media_recomputed_result_binding')
    recomputed=bundle.recomputed_g2d_execution_bundle
    results=tuple(v for v in recomputed.cell_results if v.result_id==bindings[0].g2d_cell_result_ref)
    c.require(len(results)==1 and results[0].cell_id==cell and results[0].outcome=='COMPLETED' and
        results[0].accepted_output_refs and bindings[0].g2d_runtime_report_ref==recomputed.runtime_report.report_id,'media_completed_result')
    observed=recomputed.observed_work_context
    consumed=tuple(v for v in observed.ordered_binding_artifacts if
        abi.kernel_artifact_to_plain_dict_v01(v)['payload']['source_pair']['observed_identity_ref']==source.artifact_id and
        abi.kernel_artifact_to_plain_dict_v01(v)['payload']['topology_binding']['cell_ref']==cell)
    c.require(len(consumed)==1,'media_observed_source_consumption')
    rows=tuple(q for q in recomputed.queue_entries if q.cell_id==cell and q.state=='COMPLETED' and
        set(q.observed_output_refs).intersection(results[0].accepted_output_refs))
    c.require(rows and all(consumed[0].artifact_id in q.observed_evidence_refs for q in rows),'media_actual_output_evidence')
    artifacts={v.artifact_id:v for v in (*recomputed.queue_artifacts,*recomputed.result_artifacts,*observed.ordered_binding_artifacts)}
    frontier=[v.artifact_id for q,v in zip(recomputed.queue_entries,recomputed.queue_artifacts,strict=True) if q in rows];reached=set()
    while frontier:
        ref=frontier.pop()
        if ref in reached:continue
        reached.add(ref)
        if ref in artifacts:frontier.extend(artifacts[ref].parent_refs)
    c.require(consumed[0].artifact_id in reached,'media_causal_parent_chain')
    retained_photo=session.media_review['material']['photo_work']
    c.require(abi.kernel_artifact_to_plain_dict_v01(bundle.source_context.observed_source_artifacts[2])['payload']==retained_photo,
        'media_retained_photo_evidence_changed')
    c.require(session.photo_work()==session.loss_photo_work,'media_unaffected_photo_changed')
    historical_preview=retained_photo['preview']
    path=session.directory/'cache'/f"preview_{historical_preview['version']:04d}.png"
    c.require(c.digest(path.read_bytes())==historical_preview['sha256'],'media_retained_photo_bytes_changed')
    sibling=session.media_baseline['projections'][1][0]
    old=next(v for v in baseline.cell_results if v.cell_id==sibling)
    retained=tuple(v for v in recomputed.retained_consumptions if v.consumed_result==old)
    c.require(len(retained)==1,'media_unaffected_D_result_changed')
    old_artifact=next(v for r,v in zip(baseline.cell_results,baseline.result_artifacts,strict=True) if r==old)
    c.require(retained[0].consumed_result_artifact==old_artifact and
        retained[0].admission.evidence.historical_cell_result==old,'media_retained_original_evidence')
    c.require(any(old.result_id in v.ordered_child_result_ids for v in recomputed.cell_results),'media_retained_parent_consumption')
    return dict(audio_available=payload['audio_source']['audio_available'],audio_policy=session.media_review['output']['audio_policy'],
        delta_result_ref=bundle.recomputation_result.recomputation_result_id,source_artifact_ref=source.artifact_id,
        recomputed_result_ref=results[0].result_id,output_refs=list(results[0].accepted_output_refs),consumed_binding_ref=consumed[0].artifact_id,
        preserved_photo_ref=session.media_review['output']['photo_work_ref'],preserved_D_result_ref=old.result_id,
        current_photo_ref=c.identity('retained_photo',session.loss_photo_work),
        retained_consumption_ref=retained[0].consumption_id,
        final_Root_review=bundle.final_root_decision_result.decision_id)


def recompute(session, capture, invalidation, observed_time):
    args=delta_arguments(session,capture,invalidation,observed_time)
    session.delta_arguments=args
    session.journal('COMMON_E_START')
    start=time.monotonic();bundle,report=e.run_continuous_delta_runtime_v01(**args)
    session.timings.append(dict(phase='common_E',seconds=time.monotonic()-start))
    session.journal('COMMON_E_RETURN',status=report.status,reasons=list(report.reason_codes))
    c.require(bundle is not None and report.status=='PASS','media_E:'+repr(report.reason_codes))
    session.delta_return=bundle
    from .evidence_v01 import media_value
    (session.directory/'logs'/'common_E_return.json').write_bytes(c.canonical(dict(
        report=media_value(report),result=media_value(bundle.recomputation_result),plan=media_value(bundle.recomputation_plan),
        affected=media_value(bundle.affected_result),bindings=media_value(bundle.recomputed_bindings),
        final_Root=media_value(bundle.final_root_decision_result))))
    for label,validator,value in (('supplied_D',d.validate_fractal_retained_work_execution_bundle_v01,bundle.recomputed_g2d_execution_bundle),
                                  ('supplied_E',e.validate_continuous_delta_execution_bundle_v01,bundle)):
        session.journal(label+'_START');start=time.monotonic();validation=validator(value)
        session.timings.append(dict(phase=label,seconds=time.monotonic()-start))
        session.journal(label+'_RETURN',status=validation.status,reasons=list(validation.reason_codes))
        c.require(validation.status=='PASS',label+':'+repr(validation.reason_codes))
    consumed=consume_delta(session,bundle)
    review=kernel.root_review(session.root,session.media_transaction,c.identity('media_continuation',consumed),session.id,
        dict(actual_E_consumed=consumed['audio_available'] is False,preserved_work=consumed['preserved_photo_ref']==
            session.media_review['output']['photo_work_ref']),consumed['recomputed_result_ref'],session.program.candidate.bsep_ref,
        session.program.topology_artifact.artifact_id,session.source.sample().evaluation_time,claim_value=consumed)
    return dict(arguments=args,bundle=bundle,report=report,consumed=consumed,review=review)
