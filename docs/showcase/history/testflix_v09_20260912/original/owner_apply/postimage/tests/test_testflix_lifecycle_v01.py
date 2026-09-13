"""One continuing real history, scoped refusals and immutable replay controls."""
from dataclasses import asdict, fields, replace
import copy
import json
import os
import time
from pathlib import Path
import pytest
from hedgehog import action_commit_packet_v02 as action, work_execution_host_v01 as hosts
from hedgehog.kernel import effect_firewall_v01 as firewall, semantic_work_v01 as semantic_work
from hedgehog.domains.testflix import contracts_v01 as c, evidence_v01 as e
from hedgehog.domains.testflix import kernel_adapter_v01 as k, lifecycle_v01 as life
from hedgehog.domains.testflix import mock_world_v01 as world, semantic_adapter_v01 as semantic


def executors():
    return tuple(v for v in world.CALLS if v[0]=='EXECUTOR')


def persist(name, value):
    target = os.environ.get('TESTFLIX_EVIDENCE_DIRECTORY')
    if target:
        directory = Path(target).parent/'actual_history'
        directory.mkdir(exist_ok=True)
        with (directory/name).open('x') as stream:
            stream.write(json.dumps(value,sort_keys=True,separators=(',',':'))+'\n')


@pytest.fixture(scope='module')
def history():
    started = time.monotonic(); timings = {}
    request = c.request_from_plain_v01(json.loads((Path(__file__).resolve().parents[1]/'demo/testflix_fixtures_v01.json').read_text()))
    handler = e.TestflixHandlerV01()
    purchase = handler.handle_v01(request)
    timings['P01_seconds'] = time.monotonic()-started
    print('HISTORY_P01_SECONDS='+str(timings['P01_seconds']),flush=True)
    initial_hosts = {root:host for root,(host,_) in handler.hosts.items()}
    original_package = e.seal_report_v01(purchase)
    start_calls = len(semantic.PROVIDER_CALLS)
    handler.advance_clock_v01(request.now+10)
    phase_start = time.monotonic()
    info = handler.handle_event_v01(c.InformationRequestV01(request.request_id+':information',request.user_id,
        purchase['entitlement'].entitlement_id,handler.now))
    timings['P02_seconds'] = time.monotonic()-phase_start
    print('HISTORY_P02_SECONDS='+str(timings['P02_seconds']),flush=True)
    controls = []
    def refused(event, reason):
        before = executors()
        view = handler.current_view_v01()
        with pytest.raises(ValueError,match='^'+reason+'$') as error:
            handler.prepare_playback_v01(event)
        assert executors()==before and handler.current_view_v01()==view and handler.pending is None
        controls.append(dict(event=asdict(event),reason=str(error.value),before=e.plain_value_v01(view),executor_delta=len(executors())-len(before)))
    concurrent = c.PlaybackRequestV01('request:concurrent',request.user_id,purchase['entitlement'].entitlement_id,
        request.device_id,request.content_id,handler.now,3600,720)
    refused(concurrent,'max_concurrent_streams')
    handler.advance_clock_v01(request.now+20)
    phase_start = time.monotonic()
    closed = handler.handle_event_v01(c.StopPlaybackV01(request.request_id+':stop',request.user_id,purchase['session'].session_id,handler.now))
    handler.advance_clock_v01(request.now+30)
    event = replace(concurrent,request_id=request.request_id+':fresh',now=handler.now)
    permitted_view = handler.current_view_v01()
    assert c.validate_playback_request_v01(event,purchase['entitlement'],handler.devices,handler.active,handler.now)==handler.devices[0]
    refused(replace(event,ttl_seconds=7201),'session_ttl_widening')
    refused(replace(event,quality=2160),'session_quality_widening')
    refused(replace(event,device_id='device:foreign'),'current_device_scope')
    refused(replace(event,content_id='content:foreign'),'current_device_content')
    refused(replace(event,user_id='subject:foreign'),'playback_entitlement_scope')
    devices = handler.devices
    handler.set_device_state_v01(tuple(replace(d,max_quality=360) for d in devices))
    refused(event,'session_quality_widening')
    handler.set_device_state_v01(tuple(replace(d,valid_to=handler.now+30) for d in devices))
    refused(event,'session_ttl_widening')
    handler.set_device_state_v01(devices)
    fresh = handler.handle_event_v01(event)
    timings['P03_with_controls_seconds'] = time.monotonic()-phase_start
    print('HISTORY_P03_WITH_CONTROLS_SECONDS='+str(timings['P03_with_controls_seconds']),flush=True)
    report = dict(purchase=purchase,writeback=handler.writeback,events=tuple(handler.events))
    assert e.validate_history_v01(report)
    package = e.seal_history_v01(report)
    replay = e.replay_history_v01(package,expected_manifest_hash=package['manifest_hash'])
    assert {root:host for root,(host,_) in handler.hosts.items()}==initial_hosts
    assert len(semantic.PROVIDER_CALLS)==start_calls
    assert e.seal_report_v01(purchase)==original_package
    persist('history_package.json',package)
    persist('history_replay.json',replay)
    persist('initial_negative_controls.json',controls)
    persist('history_stage_timings.json',timings)
    return dict(handler=handler,report=report,package=package,info=info,closed=closed,fresh=fresh,
        controls=controls,permitted_view=permitted_view,hosts=initial_hosts)


def test_P02_actual_stored_B_C_reuse_and_fresh_temporal_query(history):
    info = history['info'];original = history['report']['purchase'];writeback = history['report']['writeback']
    assert info['information']['report'].source_records==(writeback['meaning'],)
    assert info['information']['answer']==k.summary_facts_v01(original)
    assert info['route']['proposal'].selected_mode=='direct_informational_reuse'
    assert info['route']['decision'].outcome=='ACCEPT'
    assert info['information']['report'].query.evaluation_time>writeback['meaning'].time_envelope.pt_created_at
    assert not info['calls'] and not info['provider_calls']
    original_bytes=writeback['stored_bytes']
    event=replace(info['event'],request_id='request:second_information',now=info['event'].now+1)
    fresh=k.resolve_summary_v01(drs=history['handler'].drs,writeback=writeback,event=event,quote=original['quote'])
    route=k.route_summary_v01(original,fresh)
    assert fresh['report'].query.query_id!=info['information']['report'].query.query_id
    assert route['router_input'].transaction_id==fresh['report'].query.query_id
    assert fresh['answer']==info['information']['answer'] and original_bytes==writeback['stored_bytes']


def test_P02_public_consumer_scope_policy_missing_and_expired_refusals(history):
    b=history['info']['information']['report'];query=b.query;meaning=b.source_records[0]
    arguments={f.name:getattr(query,f.name) for f in fields(query) if f.name not in ('temporal_query_version','query_id')}
    same=k.memory.build_drs_temporal_query_v01(**arguments)
    assert same is not query and same==query
    assert k.memory.evaluate_drs_candidate_v01(semantic_address=b.semantic_address,query=same,meaning_record=meaning).eligible_for_ranking
    negatives=(dict(scope_fingerprint='b'*64),dict(policy_version='testflix.foreign.v01'),
        dict(evaluation_time=meaning.time_envelope.valid_to+1,as_of=meaning.time_envelope.valid_to+1,time_range_end=meaning.time_envelope.valid_to+2),
        dict(owning_local_root_id='root:testflix:provider'))
    outcomes=[];before=tuple(world.CALLS)
    for changes in negatives:
        changed=k.memory.build_drs_temporal_query_v01(**dict(arguments,**changes))
        result=k.memory.evaluate_drs_candidate_v01(semantic_address=b.semantic_address,query=changed,meaning_record=meaning)
        assert not result.eligible_for_ranking and result.reason_codes
        outcomes.append(dict(changes=changes,result=e.plain_value_v01(result)))
    names=('semantic_address','predecessor_record_id','supersession_reason','safe_summary','semantic_tags','resonance_reason',
        'memory_pointers','artifact_pointers','source_reference_ids','lineage_edges','time_envelope','authority_envelope',
        'persistent_lifecycle_state','risk_hints','conflict_hints','reuse_policy_class','policy_version','schema_versions',
        'content_fingerprint','recording_component')
    intact=k.address_api.build_meaning_record_v01(**{name:getattr(meaning,name) for name in names})
    assert intact is not meaning and intact==meaning
    missing=k.address_api.build_meaning_record_v01(**dict({name:getattr(meaning,name) for name in names},source_reference_ids=()))
    assert k.address_api.validate_meaning_record_v01(missing)==(True,())
    result=k.memory.evaluate_drs_candidate_v01(semantic_address=b.semantic_address,query=query,meaning_record=missing)
    assert not result.eligible_for_ranking and 'drs_required_evidence_missing' in result.reason_codes
    outcomes.append(dict(changes=dict(source_reference_ids=[]),result=e.plain_value_v01(result)))
    assert tuple(world.CALLS)==before
    persist('B_public_negative_results.json',outcomes)


def test_P03_same_hosts_explicit_close_and_fresh_authority_without_purchase(history):
    original=history['report']['purchase'];closed=history['closed'];fresh=history['fresh']
    assert [r['output']['state'] for r in closed['actions']]==['STOPPED','CLOSED']
    assert closed['after']['active']==()
    assert fresh['session'].candidate.entitlement_id==original['entitlement'].entitlement_id
    assert fresh['session'].session_id!=original['session'].session_id
    assert fresh['actions'][0]['bound'].root_decision_projection.root_decision_result.decision_id!=original['session'].provider_decision_id
    assert fresh['actions'][1]['bound'].packet_identity.packet_id!=original['playback']['bound'].packet_identity.packet_id
    assert fresh['after']['entitlements']==(original['entitlement'],)
    assert fresh['after']['consumed_periods']==fresh['before']['consumed_periods']
    assert {root:host for root,(host,_) in history['handler'].hosts.items()}==history['hosts']
    assert not fresh['provider_calls']
    assert [r['execution'].admission.definition.operation_id for r in fresh['actions']]==['testflix.session.v01','testflix.playback.v01']


def test_N08_consumed_real_payment_period_cannot_issue_second_entitlement(history):
    original=history['report']['purchase'];handler=history['handler'];before=executors()
    assert handler.consumed_periods[0][0]==original['payment']['output']['payment_ref']
    with pytest.raises(ValueError,match='^payment_period_already_consumed$'):
        handler.request_entitlement_from_payment_v01(original['payment'],original['entitlement'].candidate,
            replace(original['request'],request_id='request:independent-entitlement'))
    assert executors()==before and handler.entitlements==(original['entitlement'],)


def test_N11_concurrent_refusal_then_same_history_success(history):
    negative=history['controls'][0]
    assert negative['reason']=='max_concurrent_streams' and negative['executor_delta']==0
    assert negative['before']['active']==[history['report']['purchase']['session'].session_id]
    assert history['fresh']['before']['active']==() and history['fresh']['after']['active']==(history['fresh']['session'].session_id,)
    assert history['fresh']['actions'][1]['output']['playback_state']=='PLAYING'


def test_N12_session_and_current_device_limits_with_equivalent_positive(history):
    negatives=history['controls'][1:]
    assert [v['reason'] for v in negatives]==['session_ttl_widening','session_quality_widening','current_device_scope',
        'current_device_content','playback_entitlement_scope','session_quality_widening','session_ttl_widening']
    assert all(v['executor_delta']==0 for v in negatives)
    view=history['permitted_view'];event=history['fresh']['event'];ent=history['report']['purchase']['entitlement']
    assert c.validate_playback_request_v01(replace(event),ent,view['devices'],view['active'],view['now'])==view['devices'][0]
    assert history['fresh']['session'].candidate.valid_to<=min(ent.candidate.valid_to,view['devices'][0].valid_to)
    assert history['fresh']['session'].candidate.quality<=min(ent.candidate.plan.resolution,view['devices'][0].max_quality)
    two=view['devices']+(replace(view['devices'][0],device_id='device:second'),)
    assert c.validate_playback_request_v01(event,ent,two,(),event.now)==two[0]
    with pytest.raises(ValueError,match='^max_devices$'):
        c.validate_playback_request_v01(event,ent,two+(replace(two[0],device_id='device:third'),),(),event.now)


def test_N06_actual_consumed_semantic_and_root_inputs_do_not_export_canaries(history):
    report=history['report']['purchase'];request=report['request']
    values=[report['semantics'],report['quote']['common']['semantic_proposal'],report['quote']['common']['source_context'],
        report['user_selection']['source'],report['user_selection']['contribution'],report['user_selection']['review'],report['user_selection']['inputs']]
    for key in ('payment','entitlement_issuance','session_issuance','playback'):
        row=report[key]
        values += [row['root_review'],row['bound'].root_decision_projection.root_decision_input]
        assert row['root_review']['review']==row['bound'].root_decision_projection.root_decision_input.root_review_packet
    body=json.dumps(e.plain_value_v01(values),sort_keys=True)
    assert request.bank_private not in body and request.user_private not in body
    actual_claim=semantic_work.semantic_work_to_plain_dict_v01(report['user_selection']['contribution'].claims[0])['object_or_value']
    assert actual_claim==report['user_selection']['candidate']


def test_N13_original_packet_and_request_after_fresh_session_no_effect(history):
    handler=history['handler'];original=history['report']['purchase'];before=executors()
    assert handler.handle_v01(original['request']) is original
    assert handler.handle_event_v01(history['fresh']['event']) is history['fresh']
    row=original['playback'];host,source=handler.hosts['device'];clock=source.read_current_v01()
    assert clock.evaluation_time<row['bound'].canonical_projection.temporal_authority.expires_at_utc
    try:
        hosts.dispatch_current_action_v01(host,packet_id=row['bound'].packet_identity.packet_id,task_id=original['request'].request_id,
            expected_revision=host.revision,evaluation_time=clock.evaluation_time,evaluation_time_source=clock.evaluation_time_source,
            evaluation_context_id=clock.evaluation_context_id)
    except ValueError as error:
        print('N13_ACTUAL_COMMON_REFUSAL='+str(error),flush=True)
    assert executors()==before


def test_N20_supplied_history_actual_B_C_and_new_session_bindings(history):
    original=history['report'];info=history['info']
    fresh_info=k.resolve_summary_v01(drs=history['handler'].drs,writeback=original['writeback'],event=replace(info['event']),quote=original['purchase']['quote'])
    equivalent=dict(info,information=fresh_info,route=k.route_summary_v01(original['purchase'],fresh_info))
    changed=dict(original,events=(equivalent,)+original['events'][1:])
    assert fresh_info['report'] is not info['information']['report']
    assert e.validate_history_v01(changed) and e.history_to_plain_v01(changed)==e.history_to_plain_v01(original)
    missing=dict(equivalent,route=None)
    with pytest.raises(ValueError,match='^history_C_shape$'):
        e.validate_history_v01(dict(original,events=(missing,)+original['events'][1:]))
    foreign=dict(equivalent,information=dict(fresh_info,review=original['purchase']['user_selection']))
    with pytest.raises(ValueError):
        e.validate_history_v01(dict(original,events=(foreign,)+original['events'][1:]))
    fresh=history['fresh']
    wrong=replace(fresh['session'],provider_decision_id=original['purchase']['session'].provider_decision_id)
    with pytest.raises(ValueError,match='^fresh_provider_session$'):
        e.validate_history_v01(dict(original,events=original['events'][:-1]+(dict(fresh,session=wrong),)))
    with pytest.raises(ValueError):
        e.validate_history_v01(dict(original,events=(info,history['fresh'])))


def test_N20_pinned_history_replay_no_live_calls_and_tamper_refusal(history):
    package=history['package'];before=(tuple(world.CALLS),tuple(semantic.PROVIDER_CALLS))
    assert e.replay_history_v01(json.loads(json.dumps(package)),expected_manifest_hash=package['manifest_hash'])['replay_status']=='PASS'
    bad=copy.deepcopy(package);bad['payload']['events'][-1]['session']['provider_decision_id']='decision:foreign'
    with pytest.raises(ValueError,match='^history_replay_seal$'):
        e.replay_history_v01(bad,expected_manifest_hash=package['manifest_hash'])
    assert before==(tuple(world.CALLS),tuple(semantic.PROVIDER_CALLS))


def test_N16_persistent_handler_prestart_root_revoke_with_same_time_branch(history):
    handler=history['handler'];original=history['report']['purchase'];request=original['request']
    handler.advance_clock_v01(request.now+40)
    handler.handle_event_v01(c.StopPlaybackV01('request:second-stop',request.user_id,history['fresh']['session'].session_id,handler.now))
    handler.advance_clock_v01(request.now+50)
    event=replace(history['fresh']['event'],request_id='request:revocable',now=handler.now)
    prepared=handler.prepare_playback_v01(event);negative=prepared['device']
    packet=negative['bound'].packet_identity.packet_id
    assert negative['host'] is history['hosts']['device']
    source=world.LocalSourceV01(request.now,negative['source'].snapshot.observations);source.advance_clock_v01(event.now)
    admission=e.playback_admission_v01(request)
    assert firewall.snapshot_admitted_capability_v01(admission)==firewall.snapshot_admitted_capability_v01(negative['admitted'])
    positive_host=hosts.build_root_work_execution_host_v01(owning_root_id='root:testflix:device',registry=negative['pending_registry'],
        catalogue=(admission,),packet_bindings=((packet,negative['material']['corridor'],negative['material']['corridor_step'],admission.admission_id,negative['inputs']),),
        current_dependency_observations=source.snapshot.observations,logical_time_bridge=source.snapshot.logical_time_bridge,trusted_source=source)
    positive=dict(negative,host=positive_host,source=source,admitted=admission)
    assert positive_host.registry is negative['host'].registry and source.snapshot.evaluation_time==negative['source'].snapshot.evaluation_time
    accepted=life.dispatch_v01(positive,event.request_id)
    assert accepted['output']['playback_state']=='PLAYING'
    before=executors()
    life.revoke_current_v01(negative,bsep_ref=original['quote']['program'].candidate.bsep_ref,topology_ref=original['quote']['program'].topology_artifact.artifact_id)
    host=negative['host'];clock=negative['source'].read_current_v01()
    assert clock.evaluation_time<negative['bound'].canonical_projection.temporal_authority.expires_at_utc
    inspected=hosts.inspect_current_action_v01(host,packet_id=packet,expected_revision=host.revision,evaluation_time=clock.evaluation_time,
        evaluation_time_source=clock.evaluation_time_source,evaluation_context_id=clock.evaluation_context_id)
    assert not inspected.present_executable
    reason=None
    try:
        hosts.dispatch_current_action_v01(host,packet_id=packet,task_id=event.request_id,expected_revision=host.revision,
            evaluation_time=clock.evaluation_time,evaluation_time_source=clock.evaluation_time_source,evaluation_context_id=clock.evaluation_context_id)
    except ValueError as error:
        reason=str(error)
    assert executors()==before
    replay=action.replay_action_packet_lifecycle_history_v01(host.registry,packet_id=packet)
    assert replay.rebuilt_packet_id==packet
    assert e.validate_history_v01(history['report'])
    persist('N16_actual_common_revoke.json',dict(inspection=e.plain_value_v01(inspected),dispatch_reason=reason,
        registry=e.plain_value_v01(host.registry),positive_execution=e.plain_value_v01(accepted['execution']),
        executor_delta=len(executors())-len(before),clock=clock.evaluation_time,expires=negative['bound'].canonical_projection.temporal_authority.expires_at_utc,
        history_replay=e.plain_value_v01(replay)))
