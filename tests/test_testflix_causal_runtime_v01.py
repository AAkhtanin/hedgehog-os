"""Actual P01 controls; one genuine baseline shared only in this test process."""
from dataclasses import asdict, replace
import copy
import json
import os
from pathlib import Path
import pytest
from hedgehog import action_commit_packet_v02 as action
from hedgehog import work_execution_host_v01 as hosts
from hedgehog.kernel import effect_firewall_v01 as firewall
from hedgehog.kernel import work_composition_v01 as work
from hedgehog.domains.testflix import contracts_v01 as c, semantic_adapter_v01 as s
from hedgehog.domains.testflix import kernel_adapter_v01 as k, lifecycle_v01 as life, mock_world_v01 as world, evidence_v01 as e


def request_v01():
    return c.request_from_plain_v01(json.loads((Path(__file__).resolve().parents[1]/'demo/testflix_fixtures_v01.json').read_text()))


@pytest.fixture(scope='module')
def actual():
    handler=e.TestflixHandlerV01()
    report=handler.handle_v01(request_v01())
    package=e.seal_report_v01(report)
    replay=e.replay_v01(package,expected_manifest_hash=package['manifest_hash'])
    output=os.environ.get('TESTFLIX_EVIDENCE_DIRECTORY')
    if output:
        directory=Path(output).resolve()
        assert Path(__file__).resolve().parents[1] not in directory.parents
        directory.mkdir(parents=True,exist_ok=True)
        for name,value in (('P01_package.json',package),('P01_replay.json',replay)):
            with (directory/name).open('x') as stream:
                stream.write(json.dumps(value,sort_keys=True,separators=(',',':'))+'\n')
    return handler,report,package


def test_P01_actual_four_root_and_business_execution(actual):
    handler,report,package=actual
    assert e.validate_report_v01(report) is True
    assert {host.owning_root_id for host,_ in handler.hosts.values()}=={
        'root:testflix:user','root:testflix:bank','root:testflix:provider','root:testflix:device'}
    assert len({id(host) for host,_ in handler.hosts.values()})==4
    assert report['payment']['output']['amount_minor']==report['entitlement'].candidate.plan.price_minor==500
    selection=report['user_selection']
    assert selection['result'].decision=='ACCEPT' and selection['result'].target_root_id=='root:testflix:user'
    assert selection['candidate']['quote_ref']==report['payment']['evidence']['quote_ref']
    assert report['payment']['evidence']['user_selection']==selection['result'].decision_id
    assert report['session'].candidate.entitlement_id==report['entitlement'].entitlement_id
    assert report['playback']['output']['session_ref']==report['session'].session_id
    for key in ('payment','entitlement_issuance','session_issuance','playback'):
        row=report[key]
        assert row['execution'].invocation.inputs==row['inputs']
        assert row['execution'].result.output_validation.valid
        assert row['context'].attempt_evidence.adapter_call_count==1
    assert len([v for v in report['calls'] if v[0]=='EXECUTOR'])==6
    assert report['entitlement'].candidate.renewal=='EXPLICIT_ONLY'
    assert report['session'].candidate.valid_to-report['session'].candidate.valid_from==7200


def test_C01_changed_soft_preference_changes_real_issued_entitlement(actual):
    _,a,_=actual
    request=replace(a['request'],preference='QUALITY')
    b=e.TestflixHandlerV01().handle_v01(request)
    assert request.hard_ceiling_minor==a['request'].hard_ceiling_minor and request.catalog==a['request'].catalog
    assert b['entitlement'].candidate.plan.resolution==1080 and b['entitlement'].candidate.plan.ads
    assert b['entitlement'].candidate.plan != a['entitlement'].candidate.plan
    assert b['payment']['output']['amount_minor']==600
    assert b['entitlement_issuance']['output']['plan_id']==b['entitlement'].candidate.plan.plan_id
    assert b['quote']['results'][0].result is not a['quote']['results'][0].result


def test_C02_coherent_opaque_renaming_and_reordering(actual):
    _,a,_=actual
    old=a['request']
    names={p.plan_id:'opaque:'+str(index+47) for index,p in enumerate(old.catalog)}
    request=replace(old,request_id='request:renamed',order_id='order:renamed',user_id='subject:renamed',
        merchant_id='merchant:renamed',device_id='device:renamed',registered_devices=('device:renamed',),content_id='content:renamed',
        approved_device_id='device:renamed',approved_order_id='order:renamed',
        catalog=tuple(replace(p,plan_id=names[p.plan_id]) for p in reversed(old.catalog)))
    b=e.TestflixHandlerV01().handle_v01(request)
    chosen=b['entitlement'].candidate.plan
    old_chosen=a['entitlement'].candidate.plan
    assert chosen.plan_id==names[old_chosen.plan_id]
    assert (chosen.price_minor,chosen.resolution,chosen.ads,chosen.period_seconds)==(
        old_chosen.price_minor,old_chosen.resolution,old_chosen.ads,old_chosen.period_seconds)
    assert b['playback']['output']['device_id']=='device:renamed'


def test_N03_explicit_purchase_consent_after_actual_work(actual):
    _,report,_=actual
    request=report['request'];semantics=report['semantics'];quote=report['quote']
    before=tuple(world.CALLS)
    fresh=e.review_user_selection_v01(request,semantics,quote)
    assert fresh is not report['user_selection'] and fresh['result']==report['user_selection']['result']
    assert e.validate_user_selection_v01(fresh,request,semantics,quote)
    for changes in (dict(purchase_consent=False),dict(approved_device_id='device:other'),
                    dict(approved_order_id='order:other'),dict(approved_prices_minor=(1,))):
        changed=replace(request,**changes)
        negative=e.review_user_selection_v01(changed,semantics,quote)
        assert negative['result'].decision!='ACCEPT'
        if changes==dict(purchase_consent=False):
            assert negative['result'].decision=='NEEDS_USER'
            assert negative['result'].reason_code=='user_permission_missing'
        else:
            assert 'hard_permission_scope_violation' in negative['result'].hard_failure_reasons
        with pytest.raises(ValueError,match='^user_selection_not_accepted$'):
            e.validate_user_selection_v01(negative,changed,semantics,quote)
        print('N03 actual UserRoot consent boundary:',changes,negative['result'].decision,negative['result'].reason_code)
    assert tuple(world.CALLS)==before


def test_N05_fresh_equivalent_and_wrong_public_bsep_context(actual):
    _,report,_=actual
    q=report['quote'];common=q['common'];candidate=q['program'].candidate
    fresh=k.bsep_source_v01(report['request'],report['semantics'])
    fresh=replace(fresh,g2a_evaluation_time=common['source_context'].g2a_evaluation_time,
        g2a_evaluation_time_source=common['source_context'].g2a_evaluation_time_source,
        g2a_evaluation_context_id=common['source_context'].g2a_evaluation_context_id)
    assert fresh==common['source_context'] and fresh is not common['source_context']
    assert work.validate_work_program_candidate_v01(candidate,**dict(common,source_context=fresh))[0]
    other=replace(report['request'],request_id='request:foreign')
    foreign=k.bsep_source_v01(other,s.collect_semantics_v01(other))
    ok,reasons=work.validate_work_program_candidate_v01(candidate,**dict(common,source_context=foreign))
    assert not ok and reasons
    print('N05 actual public contextual refusal:',reasons)


@pytest.mark.parametrize('field,value',(('amount_minor',600),('merchant_id','merchant:other'),('order_id','order:other')))
def test_N07_coherent_payment_receipt_wrong_provider_relationship(actual,field,value):
    _,report,_=actual
    request=report['request'];plan=report['entitlement'].candidate.plan
    original=report['payment']
    fresh=dict(original['output'])
    assert c.validate_payment_relationship_v01(request,plan,fresh)
    inputs=world.values_v01(original['inputs'])
    if field=='amount_minor':
        inputs['amount']=action.normalize_legacy_decimal_v01(str(value/100))
    else:
        inputs[field]=value
    typed=world.records_v01({record.parameter_name:(record.value_type,inputs[record.parameter_name]) for record in original['inputs']})
    changed_request=replace(request,merchant_id=inputs['merchant_id'],order_id=inputs['order_id'])
    admitted=e.payment_admission_v01(changed_request)
    host,source=life.new_host_v01('root:testflix:bank',(admitted,),request.now)
    prepared=life.install_v01(host,source,changed_request,admitted,typed,changed_request.order_id,changed_request.merchant_id,
        dict(order=changed_request.order_id,merchant=changed_request.merchant_id,amount=inputs['amount']),report['quote'],
        dict(local_payment_request=inputs['order_id']==changed_request.order_id))
    changed=life.dispatch_v01(prepared,request.request_id)
    assert not firewall.validate_native_execution_evidence_v01(changed['execution'])
    assert changed['output'][field]==value
    before=tuple(world.CALLS)
    with pytest.raises(ValueError,match='^provider_payment_binding$'):
        c.validate_payment_relationship_v01(request,plan,changed['output'])
    assert tuple(world.CALLS)==before
    print('N07: authentic native payment receipt; Provider entitlement boundary refuses',field)


@pytest.mark.parametrize('key',('entitlement_issuance','session_issuance'))
def test_N09_wrong_provider_candidate_public_root_binding(actual,key):
    _,report,_=actual
    row=report[key];canonical=row['bound'].canonical_projection
    equivalent=action.build_native_root_bound_action_commit_packet_v01(canonical_projection=canonical,
        root_decision_projection=row['bound'].root_decision_projection)
    assert equivalent==row['bound'] and equivalent is not row['bound']
    inputs=tuple(action.build_action_effect_parameter_record_v01(parameter_name=r.parameter_name,value_type=r.value_type,
        value='candidate:other' if r.parameter_name=='candidate_ref' else r.value) for r in row['inputs'])
    changed,_=life.canonical_action_v01(report['request'],'root:testflix:provider',row['admitted'],inputs,
        'candidate:other',canonical.normalized_target_scope.included_target_refs[0],dict(candidate='other'))
    assert action.validate_native_action_commit_packet_v01(changed)[0]
    with pytest.raises(ValueError) as failure:
        action.build_native_root_bound_action_commit_packet_v01(canonical_projection=changed,
            root_decision_projection=row['bound'].root_decision_projection)
    assert 'candidate' in str(failure.value) or 'context' in str(failure.value)
    print('N09 actual public reason:',str(failure.value))


def test_N10_device_root_missing_or_foreign(actual):
    _,report,_=actual
    row=report['playback']
    assert action.validate_native_root_bound_action_commit_packet_v01(row['bound'])[0]
    with pytest.raises(ValueError):
        action.build_native_root_bound_action_commit_packet_v01(canonical_projection=row['bound'].canonical_projection,root_decision_projection=None)
    changed=dict(report,playback=report['payment'])
    assert action.validate_native_root_bound_action_commit_packet_v01(changed['playback']['bound'])[0]
    with pytest.raises(ValueError,match='^action_root_operation:playback$'):
        e.validate_report_v01(changed)


def test_N13_repeated_request_and_common_consumption(actual):
    handler,report,_=actual
    before=tuple(world.CALLS)
    assert handler.handle_v01(report['request']) is report
    assert tuple(world.CALLS)==before
    row=report['playback'];host=row['host'];clock=row['source'].read_current_v01()
    try:
        hosts.dispatch_current_action_v01(host,packet_id=row['bound'].packet_identity.packet_id,task_id=report['request'].request_id,
            expected_revision=host.revision,evaluation_time=clock.evaluation_time,evaluation_time_source=clock.evaluation_time_source,
            evaluation_context_id=clock.evaluation_context_id)
    except ValueError as failure:
        print('N13 common current refusal:',str(failure))
    assert sum(v[0]=='EXECUTOR' for v in world.CALLS)==sum(v[0]=='EXECUTOR' for v in before)


def fresh_pending_host_v01(row, request):
    now=request.now
    source=world.LocalSourceV01(now,(row['observation'],))
    packet=row['bound'].packet_identity.packet_id
    admitted=e.playback_admission_v01(request)
    assert firewall.snapshot_admitted_capability_v01(admitted)==firewall.snapshot_admitted_capability_v01(row['admitted'])
    assert admitted is not row['admitted']
    host=hosts.build_root_work_execution_host_v01(owning_root_id=row['bound'].canonical_projection.owning_local_root_id,
        registry=row['pending_registry'],catalogue=(admitted,),
        packet_bindings=((packet,row['material']['corridor'],row['material']['corridor_step'],admitted.admission_id,row['inputs']),),
        current_dependency_observations=source.snapshot.observations,logical_time_bridge=source.snapshot.logical_time_bridge,trusted_source=source)
    return dict(row,host=host,source=source,admitted=admitted)


def test_N16_common_prestart_revoke_and_same_clock_positive(actual):
    _,report,_=actual
    row=report['playback'];now=report['request'].now
    positive=fresh_pending_host_v01(row,report['request']);negative=fresh_pending_host_v01(row,report['request'])
    assert positive['host'] is not negative['host'] and positive['host'].registry is negative['host'].registry
    assert now+4<row['bound'].canonical_projection.temporal_authority.expires_at_utc
    result=life.dispatch_v01(positive,report['request'].request_id)
    assert result['output']['playback_state']=='PLAYING'
    before=tuple(world.CALLS)
    life.revoke_current_v01(negative,bsep_ref=report['quote']['program'].candidate.bsep_ref,
        topology_ref=report['quote']['program'].topology_artifact.artifact_id)
    host=negative['host'];clock=negative['source'].read_current_v01();packet=row['bound'].packet_identity.packet_id
    inspection=hosts.inspect_current_action_v01(host,packet_id=packet,expected_revision=host.revision,
        evaluation_time=clock.evaluation_time,evaluation_time_source=clock.evaluation_time_source,evaluation_context_id=clock.evaluation_context_id)
    assert not inspection.present_executable
    print('N16 actual revoked common inspection:',inspection)
    try:
        hosts.dispatch_current_action_v01(host,packet_id=packet,task_id=report['request'].request_id,expected_revision=host.revision,
            evaluation_time=clock.evaluation_time,evaluation_time_source=clock.evaluation_time_source,evaluation_context_id=clock.evaluation_context_id)
    except ValueError as failure:
        print('N16 common revoked refusal:',str(failure))
    assert sum(v[0]=='EXECUTOR' for v in world.CALLS)==sum(v[0]=='EXECUTOR' for v in before)
    assert action.replay_action_packet_lifecycle_history_v01(host.registry,packet_id=packet).rebuilt_packet_id==packet


def test_N20_supplied_report_missing_work_and_future_entitlement(actual):
    _,report,_=actual
    before=tuple(world.CALLS)
    with pytest.raises(ValueError):
        e.validate_report_v01(dict(report,quote=dict(report['quote'],d_bundle=None)))
    bad=replace(report['entitlement'],candidate=replace(report['entitlement'].candidate,payment_receipt_ref=report['session'].session_id))
    with pytest.raises(ValueError,match='^entitlement_candidate_binding$'):
        e.validate_report_v01(dict(report,entitlement=bad))
    assert tuple(world.CALLS)==before


def test_N20_offline_replay_pin_tamper_cycle_and_zero_calls(actual):
    _,report,package=actual
    before=tuple(world.CALLS)
    equivalent=json.loads(json.dumps(package))
    assert equivalent is not package
    assert e.replay_v01(equivalent,expected_manifest_hash=package['manifest_hash'])['replay_status']=='PASS'
    changed=copy.deepcopy(package);changed['payload']['actions']['playback']['output']['playback_state']='STOPPED'
    with pytest.raises(ValueError,match='^replay_seal_refusal$'):
        e.replay_v01(changed,expected_manifest_hash=package['manifest_hash'])
    with pytest.raises(ValueError,match='^replay_external_pin$'):
        e.replay_v01(package,expected_manifest_hash='0'*64)
    cycle=copy.deepcopy(package);cycle['payload']['cycle']=cycle['payload']
    with pytest.raises(ValueError,match='^replay_seal_refusal$'):
        e.replay_v01(cycle,expected_manifest_hash=package['manifest_hash'])
    assert tuple(world.CALLS)==before
