"""Pure supplied Sentinel relationships; no collector, live authority or new decision."""
import json
from dataclasses import asdict
from decimal import Decimal, ROUND_HALF_EVEN
from types import SimpleNamespace
from hedgehog import action_commit_packet_v02 as actions, avf_v02 as avf
from hedgehog import outcome_feedback_v01 as f, outcome_calibration_v01 as cal, outcome_feedback_consumer_v01 as con
from hedgehog import context_packets as packets, structured_rationale as rationale
from hedgehog.kernel import abi_v01 as abi, effect_firewall_v01 as fw, root_decision_v01 as roots
from hedgehog.incident_atlas_history_v01 import (review_from_plain_v01, validate_snapshot_v01,
    validate_epoch_v01, validate_recording_review_v01)
from . import contracts_v01 as c, events_v01 as events, incident_policy_v01 as policy, semantic_adapter_v01 as sem
from . import kernel_adapter_v01 as k, capability_registry_v01 as caps


def work_v01(value):
    rows=f.g35_validate_work_records_v01(value['results'],value['admissions'])
    program=f.g35_record_from_plain_v01(value['program'])
    f._g35_checked_work_relation_v01(abi.kernel_artifact_to_plain_dict_v01(program.topology_artifact),value['artifact'],rows,value['admissions'])
    return program,rows


def claims_v01(review):
    return roots.root_decision_input_to_plain_dict_v01(review[1])['root_review_packet']['synthesis_proposal']['normalized_claims']


def book_v01(snapshot):
    book=events.EventBook()
    rows=snapshot['history']
    for row in rows:book.ingest([row],max(book.tick,row['received']))
    book.advance(snapshot['tick'])
    c.require(book.latest==snapshot['events'],'atlas_sentinel_saved_current_set')
    c.require(snapshot['policy']==c.POLICY,'atlas_sentinel_unchanged_policy')
    return book


def observation_v01(record,native):
    c.require(record['result']==c.observability(record['material']),'atlas_sentinel_observation_semantics')
    saved=next((v for v in native['work'] if v['artifact']['artifact_id'] in record['root']['evidence_refs']),None) if 'evidence_refs' in record['root'] else None
    if saved is None:
        saved=next((v for v in native['work'] if f.g35_record_from_plain_v01(v['program']).candidate.revision_id==record['program']['revision_id']),None)
    c.require(saved is not None,'atlas_sentinel_observation_native_missing')
    program,rows=work_v01(saved)
    material=json.loads(caps.values(rows[0].invocation.inputs)['material'])
    c.require(material==record['material'] and json.loads(caps.values(rows[0].result.output)['material'])==record['result'],
        'atlas_sentinel_observation_native_binding')
    review=next((v for v in native['roots'] if f.g35_record_from_plain_v01(v[2]).decision_id==record['root']['decision_id']),None)
    c.require(review is not None,'atlas_sentinel_observation_root_missing')
    ri,rr=f.g35_validate_root_v01(review)
    claims=claims_v01(tuple(f.g35_record_from_plain_v01(v) for v in review))
    c.require(rr.decision=='ACCEPT' and len(claims)==1 and claims[0]['object_or_value']==record['result']
        and saved['artifact']['artifact_id'] in claims[0]['provenance_refs']
        and ri.root_review_packet.runtime_topology_ref==program.topology_artifact.artifact_id,'atlas_sentinel_observation_root_consumption')


def saved_current_source_v01(ctx,exp,native):
    """Rebuild finite packet fields around an already validated saved intake decision."""
    from .incident_atlas_v01 import fixture_v01
    material=exp['materials'][0]['material'];now=ctx['evaluation_time'];root=exp['root']
    orchestrator,_=sem.collect(material['frames'],fixture_v01()['reference_note'],root,now)
    request='Compare bounded pure diagnostic work.';request_id=ctx['transaction'].removeprefix('transaction:')
    ref=c.identity('orchestrator',dict(request=request,output=orchestrator))
    matches=[row for row in native['roots'] if row[2]['fields']['transaction_id']==ctx['transaction']
        and row[2]['fields']['selected_candidate_id']==ref]
    c.require(bool(matches),'atlas_sentinel_saved_intake_missing')
    decisions=[]
    for row in matches:
        ri,rr=f.g35_validate_root_v01(row);plain=roots.root_decision_input_to_plain_dict_v01(ri)
        claims=plain['root_review_packet']['synthesis_proposal']['normalized_claims']
        checks=dict(finite_diagnostic=orchestrator['selection'] in c.DIAGNOSTICS,
            source_bound=orchestrator['frames']==k.session_free_frames(orchestrator['frames']))
        c.require(rr.decision=='ACCEPT' and rr.target_root_id==root and ri.target_root_id==root
            and plain['post_vv_bundle']['bundle_id']==c.identity('checks',checks)
            and plain['root_review_packet']['runtime_topology_ref']=='sentinel:route:proposal'
            and claims[0]['subject']==request_id and claims[0]['predicate']=='monitoring_route_candidate'
            and claims[0]['object_or_value']==dict(candidate_id=ref,candidate_kind='ROUTE')
            and claims[0]['provenance_refs']==[ref] and claims[0]['time_envelope_ref']=='sentinel:time:'+str(now),
            'atlas_sentinel_saved_intake_binding')
        decisions.append(rr.decision_id)
    c.require(len(set(decisions))==1,'atlas_sentinel_saved_intake_ambiguous')
    business=packets.build_business_request_context_packet(packet_id='business:'+request_id,created_by='sentinel:local_intake',
        domain='LANDSLIDE_SENTINEL',request_id=request_id,business_subject='bounded_slope_monitoring',
        requested_action='bounded_monitoring',user_visible_summary=request)
    source_ref=dict(source='G2C_BUSINESS_REQUEST_CONTEXT_PACKET_V01',packet_id=business['packet_id'],request_id=request_id,domain_id='LANDSLIDE_SENTINEL')
    vectors,guards=('vector:'+ref,),('guard:sentinel:current_root',)
    route=packets.build_orchestrator_route_context_packet(packet_id='route_context:'+ref,created_by='sentinel:local_canonicalization',
        source_refs=(source_ref,),domain='LANDSLIDE_SENTINEL',allowed_routes=('route:sentinel:monitor',),required_guards=guards,
        selected_vector_ids=vectors,route_validation_expectations=dict(root_review_required=True,selected_only_allowed_vectors=True),
        orchestrator_is_root=False,creates_action_commit_packet=False,calls_connectors=False)
    meaning=c.canonical(dict(selection=orchestrator['selection'],input_ref=c.identity('diagnostic_inputs',orchestrator))).decode()
    structured=rationale.build_orchestrator_structured_rationale(observed_semantics=(meaning,),route_selection_reason=('Bounded local sensor work.',),
        rejected_routes=('No physical equipment or public warning endpoints.',),required_guards_reasoning=('Current Root required per command.',),
        selected_vector_reasoning=('Actual finite diagnostic selection.',),uncertainty_notes=('Semantic proposal is not action permission.',),
        authority_boundary=('SentinelRoot alone accepts.',),root_review_required=True)
    def ev(text,kind):return packets.semantic_evidence_item(text,source='runtime_canonicalization',evidence_kind=kind,confidence_label='medium')
    bsep=packets.build_bounded_semantic_evidence_packet(packet_id='bsep:'+ref,source_refs=(source_ref,),domain='LANDSLIDE_SENTINEL',
        source_role='orchestrator',target_role='architect',source_route_id='route:sentinel:monitor',source_proposal_id='proposal:'+ref,
        source_context_packet_id=route['packet_id'],source_structured_rationale_ref='structured_rationale_v01:'+c.digest(structured),
        observed_semantic_facts=(ev(meaning,'observed_fact'),),
        missing_evidence=(ev('Configuration and mock signal require independent current Root review.','missing_evidence'),),
        uncertainty_notes=(ev('Proposal only.','uncertainty'),),risk_boundary_notes=(ev('Local effects require finite packets.','risk_boundary'),),
        rejected_action_routes=(ev('No publication.','rejected_route'),),required_approvals_or_conditions=(ev(decisions[0],'approval_condition'),),
        authority_boundary_notes=(ev('No authority transfer.','authority_boundary'),),selected_vector_ids=vectors,required_guards=guards)
    expected=dict(root=root,transaction=ctx['transaction'],policy_ref='policy:'+c.digest(material['contract']),domain=business['domain'],
        source_id=con.identity('current_source',dict(business=business,bsep=bsep,route=route)),evaluation_time=now,
        evaluation_source='sentinel.monotonic_sample',evaluation_context='sentinel:current',bsep_ref=bsep['packet_id'])
    c.require(ctx==expected,'atlas_sentinel_current_source_context')
    return dict(bsep=bsep,business=business,evaluation_time=now,evaluation_context='sentinel:current')


def current_work_v01(value,exp,*,native,learned=False,extra=None):
    contract=con.CurrentReviewContractV01(c.canonical(value['contract'])).to_plain_data()
    p=con.CurrentAdvisoryProjectionV01(c.canonical(value['projection'])).to_plain_data()
    review=review_from_plain_v01(value['review'])
    c.require(p['context']==contract['context'] and p['contract_id']==contract['contract_id'],'atlas_sentinel_current_contract')
    ctx=contract['context'];material0=exp['materials'][0]['material']
    source=saved_current_source_v01(ctx,exp,native)
    material_by_id={v['candidate_id']:v for v in exp['materials']}
    if contract['role']=='EVIDENCE_CHECK':
        check=contract['check_request'];material_by_id={'g34:evidence_check':dict(operation=check['operation'],material=check['material'],base_score='1.0')}
    c.require(set(material_by_id)==set(contract['claims']),'atlas_sentinel_current_candidate_set')
    candidates=tuple(avf.AVFCandidateV02(candidate_id=key,candidate_label=row['operation'],base_viability_score=float(row['base_score']),ttl_valid=True)
        for key,row in material_by_id.items())
    reports=avf.evaluate_avf_candidates_v02(avf.AVFEvaluationInputV02(evaluation_id='g34:'+p['bridge_ref'],resolver_mode='CURRENT_CONTEXT',candidates=candidates))
    c.require(c.canonical(value['reports'])==c.canonical({r.candidate_id:asdict(r) for r in reports.decision_reports}),'atlas_sentinel_current_avf')
    snapshot=exp['snapshot'] if learned else None
    for row in p['rows']:
        key=row['candidate_id'];claim=contract['claims'][key];material=material_by_id[key]['material']
        c.require(claim['operation']==material_by_id[key]['operation'] and claim['material_sha256']==c.digest(material)
            and claim['observation_refs']==exp['source']['claim_artifact']['payload']['source_observation_refs']
            and claim['subject']['local_root_scope_id']==exp['root'],'atlas_sentinel_current_material')
        prior=snapshot['prior'] if learned and claim['history_key']==snapshot['prior']['history_key'] else None
        fp=prior['prior_fp'] if prior else 0
        base=next(r for r in reports.decision_reports if r.candidate_id==key).score_explanation.final_avf_score
        base_fp=int((Decimal(str(base))*cal.Q).to_integral_value(rounding=ROUND_HALF_EVEN))
        adjusted,micros=cal.adjusted_avf_score_v01(base_fp,fp)
        matched=bool(snapshot and claim['subject']==snapshot['fold']['subject_key'])
        trust=cal.evaluate_gt_trust_at_v01(cal.GTTrustUpdateV01(c.canonical(snapshot['updates'][-1])) if matched else None,
            evaluation_time=p['evaluated_at']).to_plain_data()
        c.require(row==dict(candidate_id=key,base_fp=base_fp,prior_fp=fp,adjusted_fp=adjusted,score_micros=micros,
            eligible=True,base_field='score_explanation.final_avf_score',base_decimal=str(base),
            prior_ref=prior['prior_id'] if prior else None,trust=trust,subject_status='MATCHED' if matched else 'COLD_OR_NONMATCHING',
            claim_id=claim['claim_id']),'atlas_sentinel_history_numeric_binding')
    winner=sorted(p['rows'],key=lambda r:(-r['adjusted_fp'],r['candidate_id']))[0]
    c.require(p['selected']==winner['candidate_id'] and p['trust']==winner['trust']
        and p['history_ref']==(snapshot['snapshot_id'] if snapshot else None),'atlas_sentinel_history_selection')
    if learned:
        discovery=value['discovery'];descent=review_from_plain_v01(discovery['review'])
        audit=discovery['read_audit'];copies=1 if value['work'] is None else 2
        c.require(descent[2].decision=='ACCEPT' and descent[2].selected_candidate_id==discovery['plan']['retrieval_plan_id']
            and claims_v01(descent)[0]['object_or_value']==discovery['plan']
            and discovery['payload_sha256']==c.digest(snapshot) and discovery['opened']==[exp['head']['record_id']]
            and [v['stage'] for v in audit]==['DESCRIPTOR','ROOT_APPROVED','PAYLOAD_READ','PUBLIC_OPEN_VALIDATED','NUMERIC_SOURCE_VALIDATED']*copies
            and all(audit[i]['snapshot']==snapshot['snapshot_id'] and audit[i+1]['decision']==descent[2].decision_id
                and audit[i+2]['bytes']==audit[i+3]['bytes']==len(c.canonical(snapshot)) and audit[i+4]['snapshot']==snapshot['snapshot_id']
                for i in range(0,len(audit),5)),
            'atlas_sentinel_current_descent')
    if value['work'] is None:
        c.require(review[2].decision=='NEEDS_MORE_EVIDENCE','atlas_sentinel_required_check_refusal');return
    record=value['work'];program,rows=work_v01(value['typed_work'])
    c.require(c.canonical(record['source'])==c.canonical(source),'atlas_sentinel_work_source')
    material=json.loads(caps.values(rows[0].invocation.inputs)['material']);output=json.loads(caps.values(rows[0].result.output)['material'])
    c.require(material==material_by_id[p['selected']]['material'] and output==record['output']==
        (c.diagnostic(material) if record['operation']=='sentinel.diagnostic.v01' else c.observability(material)), 'atlas_sentinel_current_output')
    c.require(record['artifact']==value['typed_work']['artifact'] and review[2].decision=='ACCEPT'
        and review[2].target_root_id==exp['root'] and review[2].selected_candidate_id==p['selected'],'atlas_sentinel_current_review')
    final=review_from_plain_v01(record['final_review'])
    c.require(final[2].decision=='ACCEPT' and final[2].selected_candidate_id==record['artifact']['artifact_id']
        and claims_v01(final)[0]['object_or_value']==output,'atlas_sentinel_current_result_review')
    artifacts=tuple(f.g35_validate_artifact_v01(v) for v in record['causal_artifacts'])
    refs=tuple(abi.build_causal_consumption_ref_v01(**dict(v,trace_refs=tuple(v['trace_refs']))) for v in record['causal'])
    c.require(not abi.validate_causal_consumption_bundle_v01(artifacts=artifacts,causal_refs=refs)
        and all(v in refs for v in program.source_bindings),'atlas_sentinel_current_causal')
    proposal=f.g35_validate_artifact_v01(record['proposal']);payload=record['proposal']['payload']
    c.require(payload['material']==material and payload['advisory_ref']==p['projection_id']
        and payload['root_decision_ref']==review[2].decision_id and program.candidate.semantic_proposal_ref==proposal.artifact_id,
        'atlas_sentinel_current_proposal')
    if extra is not None:
        check=contract['checks'][p['selected']];bridge=value['receipt_bridge']
        f.g35_validate_artifact_v01(bridge)
        c.require(extra['contract']['check_request']==check and extra['work']['output']==check['result_facts']
            and bridge['payload']['result_facts']==extra['work']['output']
            and bridge['payload']['original_ref']['artifact_id']==extra['work']['artifact']['artifact_id']
            and payload['check_receipt_ref']==bridge['artifact_id'],'atlas_sentinel_current_additional_check')


def experience_v01(exp,native):
    source=f.PredictiveOutcomeSourceContextV01(c.canonical(exp['source']))
    ofe=f.OutcomeFeedbackEnvelopeV01(c.canonical(exp['feedback']))
    c.require(not f.validate_outcome_feedback_against_sources_v01(ofe,source_bundle=source,profile=f.PREDICTIVE_SOURCE_PROFILE_ID),
        'atlas_sentinel_feedback_source')
    c.require(exp['feedback']['proposal_assessment']=='INCORRECT' and exp['feedback']['task_outcome']=='COMPLETED'
        and exp['feedback']['enforcement_outcome']=='ALLOWED_AS_REQUIRED','atlas_sentinel_attribution')
    program,rows=work_v01(exp['native_work'])
    material=json.loads(caps.values(rows[0].invocation.inputs)['material'])
    c.require(exp['source']['result_artifact']==exp['native_work']['artifact']
        and json.loads(caps.values(rows[0].result.output)['material'])==c.diagnostic(material)
        and not c.diagnostic(material)['healthy'],'atlas_sentinel_prediction_actual_native')
    ri,rr=f.g35_validate_root_v01(exp['native_review'])
    c.require(rr.decision=='ACCEPT' and rr.target_root_id==exp['root'] and ri.root_review_packet.runtime_topology_ref==program.topology_artifact.artifact_id,
        'atlas_sentinel_prediction_root')
    event=cal.bind_outcome_feedback_event_v01(ofe,source_bundle=source,profile=f.PREDICTIVE_SOURCE_PROFILE_ID)
    validate_snapshot_v01(exp['snapshot'],{exp['feedback']['feedback_id']:event})
    review=f.g35_record_from_plain_v01(exp['recording_review'])
    validate_recording_review_v01(exp['snapshot'],review);validate_epoch_v01(exp['snapshot'],exp['head'],review,exp['storage'])
    c.require([v['base_score'] for v in exp['materials']]==['0.70','0.69'] and exp['snapshot']['prior']['effective_count']==1
        and exp['snapshot']['prior']['prior_fp']<0,'atlas_sentinel_fixed_candidates_and_sample')
    for name in ('before','after'):
        current_work_v01(exp['values'][name+'_initial'],exp,native=native,learned=name=='after')
        current_work_v01(exp['values'][name+'_check'],exp,native=native)
        current_work_v01(exp['values'][name],exp,native=native,learned=name=='after',extra=exp['values'][name+'_check'])
    c.require(exp['values']['before']['projection']['selected']=='atlas:sentinel:diagnostic'
        and exp['values']['after']['projection']['selected']=='atlas:sentinel:observability','atlas_sentinel_changed_real_work')


def freshness_v01(value,native):
    n=value['n1'];book=book_v01(n['before'])
    observation_v01(n['work'],native);observation_v01(n['neighbor']['work'],native)
    c.require(n['work']['material']['records']==list(book.latest.values()) or
        sorted(n['work']['material']['records'],key=lambda v:v['channel'])==sorted(book.latest.values(),key=lambda v:v['channel']),
        'atlas_sentinel_freshness_sources')
    c.require(n['work']['result']['observability']=='INSUFFICIENT' and n['neighbor']['work']['result']['observability']=='ADEQUATE',
        'atlas_sentinel_delivery_not_measurement')
    sem.validate_bound(n['controlled_claim'])
    context=n['controlled_claim']['context']
    c.require(context['scenario_tick']==book.tick and any(book.tick-v['observed_end']>c.POLICY['max_local_age_seconds']
        for v in context['sources'].values() if 'observation_id' in v)
        and n['refusal']['reason']=='semantic_stale_local_measurement' and n['effects']==0,'atlas_sentinel_stale_current_claim')


def correlation_v01(value,native):
    n=value['n2'];book=book_v01(n['before'])
    for name in ('work','repeated_work'):observation_v01(n[name],native)
    c.require(n['assessment']['reason']=='independent_witnesses_required' and not n['work']['result']['hard_critical'],
        'atlas_sentinel_independent_witnesses')
    before=list(book.history);book.ingest(n['redelivery'],book.tick)
    c.require(book.history==before and n['before']['history']==n['after']['history'] and n['before']['events']==n['after']['events']
        and len(n['after']['arrivals'])==len(n['before']['arrivals'])+2
        and n['work']['result']==n['repeated_work']['result'],'atlas_sentinel_duplicate_inflation')


def continuation_v01(value,native):
    v=value['continuation'];exp=value['experience'];consumed=v['consumption'];selected=exp['values']['after']['work']
    c.require(consumed['claim']['selected_result_ref']==selected['artifact']['artifact_id']
        and consumed['claim']['output']==selected['output'] and consumed['claim']['current_input_sha256']==c.digest(consumed['material'])
        and consumed['material']==exp['materials'][1]['material'] and consumed['incident_root']==exp['root'], 'atlas_sentinel_consumed_selected_work')
    ri,rr=f.g35_validate_root_v01(consumed['review'])
    claim=claims_v01(tuple(f.g35_record_from_plain_v01(x) for x in consumed['review']))[0]
    c.require(rr.decision=='ACCEPT' and rr.target_root_id==exp['root'] and claim['object_or_value']==consumed['claim']
        and selected['artifact']['artifact_id'] in claim['provenance_refs'],'atlas_sentinel_consumption_root')
    c.require(v['wrong_consumed_work']['reason']=='atlas_sentinel_selected_result','atlas_sentinel_wrong_real_work_control')
    pending,waiting,joined=v['pending'],v['waiting'],v['joined']
    c.require(pending['root']==waiting['root']==joined['root']==exp['root'] and pending['task']==waiting['task']==joined['task']
        and pending['pending_alive'] and waiting['pending_alive'] and not waiting['pending_return']
        and waiting['signal']['signal'] and not waiting['capabilities']['site_cloud_available']
        and not joined['pending_alive'] and len(joined['pending_return'])==1,'atlas_sentinel_same_pending_episode')
    c.require(pending['budgets']['optional_context']==waiting['budgets']['optional_context']
        and joined['budgets']['optional_context']['spent']==2 and joined['budgets']['pure_work']['spent']>=pending['budgets']['pure_work']['spent'],
        'atlas_sentinel_pending_budget_preserved')
    for key,reason in (('retry','task_allowance_exhausted'),('reset','allocation_refused'),('expansion','coordinator_allowance_exhausted'),('native_work','work_budget_exhausted')):
        c.require(v['budget_controls'][key]['reason']==reason,'atlas_sentinel_budget_control')
    budget=v['budget_final'];c.require(sum(r['limit'] for r in budget['budgets'].values())==budget['coordinator_total']
        and all(0<=r['spent']<=r['limit'] for r in budget['budgets'].values()),'atlas_sentinel_budget_bound')
    assessment=policy.Incident();on=assessment.evaluate(book_v01(waiting),contract=waiting['policy'])
    c.require(on==v['on_assessment'],'atlas_sentinel_on_source_assessment')
    late=v['late'];again=assessment.evaluate(book_v01(waiting),contract=waiting['policy'])
    c.require(late['assessment']==again and late['derived_checks']==dict(measured_clearance=again['clearance'],incident_active=True,actual_signal=True)
        and not again['clearance'],'atlas_sentinel_off_checks_must_come_from_sources')
    sem.validate_bound(late['old_semantic'])
    c.require(late['old_semantic']['context']['scenario_tick']<waiting['tick'] and late['semantic_refusal']['reason']=='role_current_context'
        and late['plan_refusal']['reason']=='reviewed_work_current_dependencies','atlas_sentinel_late_currentness')
    c.require(late['off_refusal']['reason'].startswith('root_refusal:') and not late['host_reached']
        and late['after']['effects']==waiting['effects'] and late['after']['host_revision']==waiting['host_revision']
        and c.digest(c.canonical(waiting['effects']))==late['immutable_effects_sha256']
        and c.digest(c.canonical(v['report']))==late['immutable_report_sha256'],'atlas_sentinel_refusal_not_effect')
    for index,row in enumerate(v['recovery']):
        result=assessment.evaluate(book_v01(row['snapshot']),contract=row['snapshot']['policy'])
        c.require(result==row['assessment'] and result['clearance']==(index==2),'atlas_sentinel_measured_recovery')
    c.require(v['final']['incident_state']=='CLOSED' and not v['final']['signal']['signal']
        and len(v['final']['effects'])==3 and v['worker_joined'],'atlas_sentinel_lawful_continuation')
    trace=value['episode_trace'];on_event=next(e for e in trace if e['phase']=='INCIDENT_ON_COMPLETED')
    c.require(on_event['monotonic']<joined['pending_return'][0]['monotonic'],'atlas_sentinel_pending_real_order')


def actions_v01(value):
    native=value['native'];v=value['continuation']
    c.require(len(native['prepared'])==len(native['actions'])==3,'atlas_sentinel_action_inventory')
    for prepared,action in zip(native['prepared'],native['actions'],strict=True):
        auth=f.g35_record_from_plain_v01(prepared['authorization']);bound=auth['root_bound'];packet=bound.canonical_projection
        registry=f.g35_record_from_plain_v01(action['registry']);effect=action['effect']
        c.require(actions.validate_native_root_bound_action_commit_packet_v01(bound)[0]
            and actions.validate_action_commit_packet_registry_v02(registry)[0],'atlas_sentinel_native_action')
        ri,rr=f.g35_validate_root_v01(prepared['review'])
        c.require(rr==bound.root_decision_projection.root_decision_result and rr.decision=='ACCEPT'
            and effect['packet_id']==bound.packet_identity.packet_id
            and packet.dependency_candidate.dependency_records[0].content_sha256==c.digest(prepared['fact']), 'atlas_sentinel_action_source')
        inputs=f.g35_record_from_plain_v01(prepared['inputs'])
        c.require(json.loads(caps.values(inputs)['command'])==prepared['command'] and prepared['fact']['command']==prepared['command'],
            'atlas_sentinel_action_command')
        receipt=f.g35_validate_artifact_v01(effect['receipt']);execution=fw.native_execution_evidence_from_plain_data_v01(effect['receipt']['payload']['execution_evidence'])
        c.require(not fw.validate_native_execution_evidence_v01(execution) and execution.invocation.inputs==inputs
            and caps.values(execution.result.output)==effect['output'] and any(ctx.receipt==receipt for ctx in registry.action_packet_fulfillment_attempt_contexts),
            'atlas_sentinel_native_receipt')
        state=actions.derive_action_packet_lifecycle_state_v01(registry,packet_id=effect['packet_id'])
        c.require(not state.executable and state.terminal_receipt_ref==receipt.artifact_id and state.idempotency_disposition=='CONSUMED',
            'atlas_sentinel_consumed_packet')
    c.require([x['effect'] for x in native['actions']]==v['final']['effects'],'atlas_sentinel_action_final_binding')
    c.require(native['prepared'][0]['checks']==dict(hard_floor=v['on_assessment']['hard_critical'],current_work=True,single_incident=True)
        and native['prepared'][2]['checks']==dict(measured_clearance=v['recovery'][-1]['assessment']['clearance'],incident_active=True,actual_signal=True),
        'atlas_sentinel_action_assessment_mapping')
    refused=[]
    for row in native['roots']:
        ri,rr=f.g35_validate_root_v01(row)
        if rr.decision!='ACCEPT' and roots.root_decision_input_to_plain_dict_v01(ri)['post_vv_bundle']['bundle_id']==c.identity('checks',v['late']['derived_checks']):refused.append(rr)
    c.require(len(refused)==1 and refused[0].target_root_id==v['final']['root'],'atlas_sentinel_actual_off_root_refusal')


def validate_sentinel_v01(value):
    c.require(value['profile']=='INCIDENT_ATLAS_SENTINEL_AT5_V01','atlas_sentinel_profile')
    native=value['native']
    for row in native['work']:work_v01(row)
    freshness_v01(value,native);correlation_v01(value,native);experience_v01(value['experience'],native)
    continuation_v01(value,native);actions_v01(value)
    c.require(value['new_provider_calls']==0 and value['counts']['public_D']==value['counts']['public_E']==0
        and value['counts']['harness_attempt']==value['counts']['harness_transport']==0,'atlas_sentinel_bounded_runtime')
    return dict(status='PASS',cards=['N1','N2','N3','N4'],consumers=1,lawful_continuations=1,new_provider_calls=0,
        scope='CONTROLLED_SAVED_RELATIONS_NOT_PHYSICAL_TRUTH_OR_LIVE_AUTHORITY')
