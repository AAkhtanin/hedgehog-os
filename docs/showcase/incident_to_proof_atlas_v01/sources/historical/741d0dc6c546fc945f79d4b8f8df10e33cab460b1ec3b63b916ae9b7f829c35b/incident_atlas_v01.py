"""One Testflix setup, isolated current boundaries, and a consumed G34 Work.

Accepted domain handlers and all Root/Host rules are unchanged. Domain clocks
are controlled logical UTC seconds; LocalSource evaluates at logical now + 4.
"""
from dataclasses import asdict, replace
import json
from pathlib import Path
import time
from hedgehog import action_commit_packet_v02 as action, work_execution_host_v01 as hosts
from hedgehog import outcome_feedback_v01 as feedback
from hedgehog.kernel import abi_v01 as abi, effect_firewall_v01 as firewall
from hedgehog.kernel import semantic_work_v01 as semantic_work, root_decision_v01 as roots, trust_model_v01 as trust
from hedgehog.kernel import work_composition_v01 as work
from hedgehog.incident_atlas_v01 import canonical_v01 as canonical, digest_v01 as digest, require_v01 as require
from . import contracts_v01 as c, evidence_v01 as e, lifecycle_v01 as life
from . import mock_world_v01 as world, semantic_adapter_v01 as semantic
from . import incident_atlas_work_v01 as native

ROOT=Path(__file__).resolve().parents[3]

def save_v01(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(canonical(value))

def calls_v01():return tuple(v for v in world.CALLS if v[0]=='EXECUTOR')

def clock_v01(source):
    clock=source.read_current_v01()
    return dict(evaluation_time=clock.evaluation_time,evaluation_source=clock.evaluation_time_source,
        evaluation_context=clock.evaluation_context_id,source_revision=clock.source_revision,
        observations=feedback.g35_record_to_plain_v01(clock.observations),
        bridge=feedback.g35_record_to_plain_v01(clock.logical_time_bridge))

def action_record_v01(record):
    result={key:feedback.g35_record_to_plain_v01(record[key]) for key in
        ('bound','inputs','material','observation','pending_registry')}
    result.update(admission=feedback.g35_record_to_plain_v01(firewall.snapshot_admitted_capability_v01(record['admitted'])),
        evidence=e.plain_value_v01(record['evidence']),checks=record['checks'],root_review=feedback.g35_record_to_plain_v01(record['root_review']),
        registry=feedback.g35_record_to_plain_v01(record.get('registry',record['host'].registry)),
        clock=clock_v01(record['source']))
    if 'receipt' in record:
        result.update(receipt=abi.kernel_artifact_to_plain_dict_v01(record['receipt']),
            execution=feedback.g35_record_to_plain_v01(record['execution']),output=record['output'],
            context=feedback.g35_record_to_plain_v01(record['context']))
    return result

def inspection_v01(prepared):
    host=prepared['host'];clock=prepared['source'].read_current_v01()
    value=hosts.inspect_current_action_v01(host,packet_id=prepared['bound'].packet_identity.packet_id,
        expected_revision=host.revision,evaluation_time=clock.evaluation_time,
        evaluation_time_source=clock.evaluation_time_source,evaluation_context_id=clock.evaluation_context_id)
    return feedback.g35_record_to_plain_v01(value)

def refuse_dispatch_v01(prepared,task):
    before=len(calls_v01());reason=None
    try:life.dispatch_v01(prepared,task)
    except ValueError as error:reason=str(error)
    require(reason is not None and len(calls_v01())==before,'atlas_testflix_forbidden_effect')
    return dict(reason=reason,executor_delta=len(calls_v01())-before,action=action_record_v01(prepared),inspection=inspection_v01(prepared))

def device_branch_v01(session):
    """New actual Host from immutable native pre-start material, never JSON authority."""
    original=session['purchase'];pending=session['handler'].pending;device=pending['device']
    request=original['request'];source=world.LocalSourceV01(request.now,device['source'].snapshot.observations)
    source.advance_clock_v01(session['handler'].now)
    admitted=e.playback_admission_v01(request)
    require(firewall.snapshot_admitted_capability_v01(admitted)==firewall.snapshot_admitted_capability_v01(device['admitted']),'atlas_testflix_branch_admission')
    packet=device['bound'].packet_identity.packet_id
    host=hosts.build_root_work_execution_host_v01(owning_root_id='root:testflix:device',registry=device['pending_registry'],
        catalogue=(admitted,),packet_bindings=((packet,device['material']['corridor'],device['material']['corridor_step'],admitted.admission_id,device['inputs']),),
        current_dependency_observations=source.snapshot.observations,logical_time_bridge=source.snapshot.logical_time_bridge,trusted_source=source)
    return dict(device,host=host,source=source,admitted=admitted)

def setup_v01(directory):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=False)
    fixture=json.loads((ROOT/'fixtures/incident_atlas_testflix_v01.json').read_bytes())
    raw=json.loads((ROOT/'demo/testflix_fixtures_v01.json').read_bytes())
    raw.update(request_id='request:'+fixture['request_suffix'],now=int(time.time()))
    request=c.request_from_plain_v01(raw);handler=e.TestflixHandlerV01()
    start=time.monotonic();purchase=handler.handle_v01(request,provider=semantic.controlled_provider_v01)
    seconds=time.monotonic()-start
    return dict(directory=directory,handler=handler,purchase=purchase,fixture=fixture,setup_seconds=seconds)

def project_setup_v01(session):
    directory=session['directory'];handler=session['handler'];purchase=session['purchase'];request=purchase['request']
    # The accepted full projector retains quote/D and native action source bodies.
    plain=e.report_to_plain_v01(purchase)
    save_v01(directory/'purchase.json',plain)
    actions={key:action_record_v01(purchase[key]) for key in ('payment','entitlement_issuance','session_issuance','playback')}
    quote=purchase['quote']
    artifact=work.work_program_result_to_artifact_v01(quote['program'],quote['results'],**quote['common'],
        host_map={'root:testflix:user':quote['host']},review_bindings=((quote['obligation'],quote['d_source'],quote['d_bundle']),))
    quote_records=dict(results=feedback.g35_record_to_plain_v01(quote['results']),
        admissions=feedback.g35_record_to_plain_v01(tuple(firewall.snapshot_admitted_capability_v01(v) for v in quote['common']['catalogue'])),
        topology=abi.kernel_artifact_to_plain_dict_v01(quote['program'].topology_artifact),artifact=abi.kernel_artifact_to_plain_dict_v01(artifact),
        selection=feedback.g35_record_to_plain_v01(tuple(purchase['user_selection'][k] for k in ('kernel','inputs','result'))))
    result=dict(fixture=session['fixture'],request=asdict(request),purchase=plain,actions=actions,quote_records=quote_records,
        setup_seconds=session['setup_seconds'],clock_law='Logical integer UTC seconds; trusted evaluation=handler.now+4; validity requires evaluation < valid_to.',
        roots={k:h.owning_root_id for k,(h,_) in handler.hosts.items()},new_provider_calls=0,captured_reexecutions=0)
    save_v01(directory/'setup.json',result)
    session['result']=result

def stale_quote_v01(session):
    purchase=session['purchase'];request=purchase['request'];quote=purchase['quote'];selection=purchase['user_selection']
    admitted=e.payment_admission_v01(request);host,source=life.new_host_v01('root:testflix:bank',(admitted,),request.now)
    original=purchase['payment'];terms=original['evidence']
    prepared=life.install_v01(host,source,request,admitted,original['inputs'],request.order_id,request.merchant_id,terms,quote,
        dict(actual_quote_completed=original['output']['amount_minor']==purchase['semantics']['selected_plan'].price_minor,
            current_explicit_selection=e.validate_user_selection_v01(selection,request,purchase['semantics'],quote)))
    before=action_record_v01(prepared);state=action.derive_action_packet_lifecycle_state_v01(host.registry,packet_id=prepared['bound'].packet_identity.packet_id)
    save_v01(session['directory']/'T1_pending.json',dict(action=before,state=feedback.g35_record_to_plain_v01(state)))
    require(state.lifecycle_state=='PENDING_FULFILLMENT' and state.idempotency_disposition!='CONSUMED','atlas_testflix_T1_not_pending')
    source.advance_clock_v01(request.now+30)
    changed=dict(terms,amount_minor=session['result']['fixture']['changed_price_minor'],quote_ref='testflix:new_quote:'+digest(dict(terms,revision=2)))
    observation=life.refresh_dependency_v01(prepared,changed,request.now+120)
    refusal=refuse_dispatch_v01(prepared,request.request_id)
    result=dict(before=before,changed_terms=changed,current_observation=feedback.g35_record_to_plain_v01(observation),
        refusal=refusal,positive_initial_payment_ref=original['receipt'].artifact_id,
        scope='Independent unconsumed Bank branch of the same original request, not the consumed main payment. Changed-price purchase NOT_EXECUTED; no fresh E.')
    session['result']['T1']=result;save_v01(session['directory']/'T1.json',result)

def receipt_retry_v01(session):
    handler=session['handler'];purchase=session['purchase'];paid=purchase['payment']
    before=dict(view=e.plain_value_v01(handler.current_view_v01()),registry=feedback.g35_record_to_plain_v01(paid['host'].registry),calls=len(calls_v01()))
    retry=refuse_dispatch_v01(paid,purchase['request'].request_id)
    host=paid['host'];receipt_reason=None
    try:host.observe_receipt(packet_id=paid['bound'].packet_identity.packet_id,
        attempt_evidence_id=paid['context'].attempt_evidence.attempt_evidence_id,expected_revision=host.revision,
        evaluation_time=paid['source'].snapshot.evaluation_time+1,evaluation_time_source=paid['source'].snapshot.evaluation_time_source)
    except ValueError as error:receipt_reason=str(error)
    replay=host.replay(packet_id=paid['bound'].packet_identity.packet_id)
    extension=None
    try:handler.request_entitlement_from_payment_v01(paid,purchase['entitlement'].candidate,purchase['request'])
    except ValueError as error:extension=str(error)
    after=dict(view=e.plain_value_v01(handler.current_view_v01()),registry=feedback.g35_record_to_plain_v01(host.registry),calls=len(calls_v01()))
    require(before==after and extension=='payment_period_already_consumed','atlas_testflix_T3_duplicate_purchase')
    result=dict(before=before,after=after,retry=retry,repeat_receipt_reason=receipt_reason,
        lifecycle_replay=feedback.g35_record_to_plain_v01(replay),extension_reason=extension,receipt=abi.kernel_artifact_to_plain_dict_v01(paid['receipt']))
    session['result']['T3']=result;save_v01(session['directory']/'T3.json',result)

def prepare_session_v01(session):
    handler=session['handler'];purchase=session['purchase'];request=purchase['request']
    handler.advance_clock_v01(request.now+10)
    stopped=handler.handle_event_v01(c.StopPlaybackV01('request:atlas:stop',request.user_id,purchase['session'].session_id,handler.now))
    handler.advance_clock_v01(request.now+20)
    event=c.PlaybackRequestV01('request:atlas:current_start',request.user_id,purchase['entitlement'].entitlement_id,
        request.device_id,request.content_id,handler.now,session['result']['fixture']['fresh_session_ttl_seconds'],720)
    pending=handler.prepare_playback_v01(event)
    session['event']=event;session['pending']=pending
    stop_plain={k:e.plain_value_v01(v) for k,v in stopped.items() if k!='actions'}
    stop_plain['actions']=[action_record_v01(v) for v in stopped['actions']]
    result=dict(event=asdict(event),stopped=stop_plain,session=asdict(pending['session']),
        issued=action_record_v01(pending['issued']),pending_device=action_record_v01(pending['device']),view=e.plain_value_v01(handler.current_view_v01()))
    session['result']['prepared_session']=result;save_v01(session['directory']/'prepared_session.json',result)

def session_boundaries_v01(session):
    handler=session['handler'];purchase=session['purchase'];event=session['event'];pending=session['pending']
    expired=device_branch_v01(session);deadline=expired['bound'].canonical_projection.temporal_authority.expires_at_utc
    expired['source'].advance_clock_v01(deadline-4)
    require(expired['source'].snapshot.evaluation_time==deadline==pending['session'].candidate.valid_to,'atlas_testflix_expiry_equality')
    expiry=refuse_dispatch_v01(expired,event.request_id)
    revoked=device_branch_v01(session)
    revocation=life.revoke_current_v01(revoked,bsep_ref=purchase['quote']['program'].candidate.bsep_ref,
        topology_ref=purchase['quote']['program'].topology_artifact.artifact_id)
    refusal=refuse_dispatch_v01(revoked,event.request_id)
    result=dict(expiry=expiry,deadline=deadline,revocation=refusal,
        owning_root='root:testflix:device',main_clock=clock_v01(pending['device']['source']),
        period_unchanged=asdict(purchase['entitlement']),branches='Two separate actual pre-start Device Hosts; main Host never advanced or revoked by these controls.')
    session['result']['T2']=result;save_v01(session['directory']/'T2.json',result)

def experience_v01(session):
    handler=session['handler'];purchase=session['purchase'];pending=session['pending']
    material=native.material_v01(pending['device'],session['event'],purchase['entitlement'],handler.devices,'atlas:testflix:current_start_prediction')
    experience,live=native.experience_v01(session['directory']/'experience',material,material)
    session['experience_live']=live;session['result']['experience']=experience
    save_v01(session['directory']/'experience.json',experience)

def memory_review_v01(session, consent):
    """The suggestion enters the actual Root candidate as advice, never permission."""
    purchase=session['purchase'];request=replace(purchase['request'],purchase_consent=consent)
    base=e.review_user_selection_v01(request,purchase['semantics'],purchase['quote'])
    exp=session['result']['experience'];advice=dict(suggestion=session['result']['fixture']['memory_suggestion'],
        authority='ADVISORY_ONLY',snapshot_ref=exp['snapshot']['snapshot_id'],prior=exp['snapshot']['prior'],
        current_projection=exp['after']['projection'],work_artifact_ref=exp['after']['artifact']['artifact_id'])
    ref='atlas:memory:'+digest(advice);source=replace(base['source'],bounded_context_refs=base['source'].bounded_context_refs+(ref,))
    old=base['contribution'];original=old.claims[0]
    claim=semantic_work.build_normalized_claim_v01(claim_id=original.claim_id,subject=original.subject,predicate=original.predicate,
        object_or_value=dict(candidate=base['candidate'],memory_advice=advice),time_envelope_ref=original.time_envelope_ref,
        provenance_refs=original.provenance_refs+(ref,),evidence_refs=original.evidence_refs,confidence_micros=original.confidence_micros,
        source_role=original.source_role,source_mode=original.source_mode)
    contribution=replace(old,claims=(claim,),bounded_context_refs=source.bounded_context_refs)
    packet=semantic_work.build_root_review_packet_from_contributions_v01(request=source,contributions=(contribution,),
        trust_profiles=trust.build_default_component_trust_profiles_v01())
    raw=roots.root_decision_input_to_plain_dict_v01(base['inputs'])
    raw.pop('decision_input_id');raw['root_review_packet']=packet
    now=session['handler'].now+4
    temporal=request.now<=now<base['candidate']['valid_to']
    raw['temporal_state']=dict(temporal_valid=temporal,expired=not temporal,not_before_satisfied=now>=request.now,
        time_envelope_ref=base['candidate']['d_report_ref'])
    decision_input=roots.build_root_decision_input_v01(**raw)
    result=roots.decide_root_v01(kernel=base['kernel'],decision_input=decision_input)
    require(not roots.validate_root_decision_result_v01(kernel=base['kernel'],decision_input=decision_input,result=result),'atlas_testflix_memory_root')
    require(result.decision==('ACCEPT' if consent else 'NEEDS_USER'),'atlas_testflix_memory_consent')
    return dict(request=asdict(request),candidate=base['candidate'],advice=advice,source=feedback.g35_record_to_plain_v01(source),
        contribution=feedback.g35_record_to_plain_v01(contribution),review=feedback.g35_record_to_plain_v01((base['kernel'],decision_input,result)),
        current_logical_time=session['handler'].now+4,quote_role='Retained still-in-period source; this review issues no action packet and executes no renewal.')

def memory_controls_v01(session):
    handler=session['handler'];before=dict(view=e.plain_value_v01(handler.current_view_v01()),calls=len(calls_v01()))
    negative=memory_review_v01(session,False);positive=memory_review_v01(session,True)
    after=dict(view=e.plain_value_v01(handler.current_view_v01()),calls=len(calls_v01()))
    require(before==after and session['result']['experience']['snapshot']['prior']['prior_fp']>0,'atlas_testflix_memory_effect')
    result=dict(before=before,after=after,no_consent=negative,explicit_consent=positive,
        attribution='Correct current-source prediction is favorable experience; absent purchase consent is not a prediction penalty.',D1='PENDING')
    session['result']['T4']=result;save_v01(session['directory']/'T4.json',result)

def consume_v01(session, selected_work):
    handler=session['handler'];purchase=session['purchase'];pending=session['pending'];live=session['experience_live']
    require(selected_work['artifact']==session['result']['experience']['after']['artifact']
        and selected_work['program']==session['result']['experience']['after']['program']
        and selected_work['results']==session['result']['experience']['after']['results'], 'atlas_testflix_wrong_consumer_work')
    actual=native.material_v01(pending['device'],session['event'],purchase['entitlement'],handler.devices,'atlas:testflix:current_start_prediction')
    artifact=work.work_program_result_to_artifact_v01(live['program'],live['results'],**live['common'],host_map={native.ROOT:live['host']})
    require(abi.kernel_artifact_to_plain_dict_v01(artifact)==selected_work['artifact'] and actual==selected_work['material']
        and selected_work['output']==native.evaluate_v01(actual,provenance=selected_work['projection']['selected']=='provenance')
        and selected_work['output']['checks'][0]['healthy'],'atlas_testflix_current_work_material')
    packet_id=pending['device']['bound'].packet_identity.packet_id
    material=dict(packet_id=packet_id,operation='testflix.playback.v01',work_artifact_ref=artifact.artifact_id,
        input_sha256=digest(actual),output_sha256=digest(selected_work['output']),session_ref=pending['session'].session_id)
    review=native.output_review_v01(root='root:testflix:device',transaction=pending['device']['bound'].canonical_projection.transaction_id,
        candidates={packet_id:material},selected=packet_id,scores={packet_id:1000000},evidence_ref=artifact.artifact_id,
        now=handler.now+4,predicate='atlas_testflix_current_start_work_consumed',topology_ref=live['program'].topology_artifact.artifact_id)
    require(review[2].decision=='ACCEPT','atlas_testflix_consumer_review')
    before=len(calls_v01());record=handler.dispatch_playback_v01(pending)
    require(len(calls_v01())==before+1 and record['actions'][-1]['output']['playback_state']=='PLAYING','atlas_testflix_continuation')
    return dict(material=material,review=feedback.g35_record_to_plain_v01(review),event=asdict(record['event']),
        session=asdict(record['session']),playback=action_record_v01(record['actions'][-1]),
        before=e.plain_value_v01(record['before']),after=e.plain_value_v01(record['after']),executor_delta=1)

def continuation_v01(session):
    before=len(calls_v01());wrong=None
    try:consume_v01(session,session['result']['experience']['observation'])
    except ValueError as error:wrong=str(error)
    require(wrong=='atlas_testflix_wrong_consumer_work' and len(calls_v01())==before,'atlas_testflix_wrong_work_control')
    result=consume_v01(session,session['result']['experience']['after'])
    result['wrong_work_control']=dict(reason=wrong,executor_delta=0)
    session['result']['consumption']=result
    session['result']['final_view']=e.plain_value_v01(session['handler'].current_view_v01())
    handler=session['handler']
    payments=handler.hosts['bank'][0].registry.action_packet_fulfillment_attempt_contexts
    session['result']['counts']=dict(main_payments=sum(v.receipt is not None for v in payments),
        new_paid_periods=len(handler.entitlements),new_current_sessions=len(handler.sessions)-1,native_prediction_events=1,
        unique_experience_consumers=1,new_provider_calls=0,captured_reexecutions=0)
    save_v01(session['directory']/'testflix.json',session['result'])
    return session['result']
