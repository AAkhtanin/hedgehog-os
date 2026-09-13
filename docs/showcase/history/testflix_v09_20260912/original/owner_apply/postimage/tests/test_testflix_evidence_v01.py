"""Current-start and later explicit-authority controls on actual public hosts."""
import copy
from dataclasses import asdict, replace
import json
import os
from pathlib import Path
import time
import pytest
from hedgehog import action_commit_packet_v02 as action, work_execution_host_v01 as hosts
from hedgehog.kernel import effect_firewall_v01 as firewall
from hedgehog.domains.testflix import contracts_v01 as c, evidence_v01 as e
from hedgehog.domains.testflix import lifecycle_v01 as life, mock_world_v01 as world, semantic_adapter_v01 as semantic
from hedgehog.domains.testflix import kernel_adapter_v01 as kernel


def executor_calls():
    return tuple(v for v in world.CALLS if v[0]=='EXECUTOR')


def persist(name, value):
    target = os.environ.get('TESTFLIX_EVIDENCE_DIRECTORY')
    if target:
        directory = Path(target).parent/'actual_T3'
        directory.mkdir(exist_ok=True)
        with (directory/name).open('x') as stream:
            stream.write(json.dumps(value,sort_keys=True,separators=(',',':'))+'\n')


def pending_branch(handler):
    """Independent public Device host; all immutable pre-revoke evidence is shared."""
    prepared = handler.pending; device = prepared['device']
    request = next(iter(handler.reports.values()))['request']
    branch = copy.copy(handler)
    branch.hosts = dict(handler.hosts);branch.events = list(handler.events)
    source = world.LocalSourceV01(request.now,device['source'].snapshot.observations)
    source.advance_clock_v01(handler.now)
    admitted = e.playback_admission_v01(request)
    assert firewall.snapshot_admitted_capability_v01(admitted)==firewall.snapshot_admitted_capability_v01(device['admitted'])
    packet = device['bound'].packet_identity.packet_id
    host = hosts.build_root_work_execution_host_v01(owning_root_id='root:testflix:device',registry=device['pending_registry'],
        catalogue=(admitted,),packet_bindings=((packet,device['material']['corridor'],device['material']['corridor_step'],admitted.admission_id,device['inputs']),),
        current_dependency_observations=source.snapshot.observations,logical_time_bridge=source.snapshot.logical_time_bridge,trusted_source=source)
    branch.hosts = {'device':(host,source)}
    branch.pending = dict(prepared,device=dict(device,host=host,source=source,admitted=admitted))
    return branch


@pytest.fixture(scope='module')
def current_start():
    started = time.monotonic()
    request = c.request_from_plain_v01(json.loads((Path(__file__).resolve().parents[1]/'demo/testflix_fixtures_v01.json').read_text()))
    handler = e.TestflixHandlerV01();purchase = handler.handle_v01(request)
    original_hosts = {root:host for root,(host,_) in handler.hosts.items()}
    original_package = e.seal_report_v01(purchase)
    print('T3_CURRENT_START_P01_SECONDS='+str(time.monotonic()-started),flush=True)
    handler.advance_clock_v01(request.now+10)
    handler.handle_event_v01(c.StopPlaybackV01('request:t3-stop',request.user_id,purchase['session'].session_id,handler.now))
    handler.advance_clock_v01(request.now+20)
    event = c.PlaybackRequestV01('request:t3-delayed',request.user_id,purchase['entitlement'].entitlement_id,
        request.device_id,request.content_id,handler.now,60,720)
    prepared = handler.prepare_playback_v01(event)
    handler.advance_clock_v01(event.now+2)
    before = executor_calls();providers = tuple(semantic.PROVIDER_CALLS)
    actual = handler.dispatch_playback_v01(prepared)
    assert len(executor_calls())-len(before)==1 and tuple(semantic.PROVIDER_CALLS)==providers
    assert actual['before']['now']==event.now and actual['after']['now']==event.now+2
    assert actual['actions'][-1]['context'].attempt_evidence.eligibility_evaluation_time==event.now+6
    history = dict(purchase=purchase,writeback=handler.writeback,events=tuple(handler.events))
    assert e.validate_history_v01(history) and e.seal_report_v01(purchase)==original_package
    package = e.seal_history_v01(history)
    persist('delayed_valid_history.json',package)
    handler.advance_clock_v01(request.now+30)
    handler.handle_event_v01(c.StopPlaybackV01('request:t3-delayed-stop',request.user_id,actual['session'].session_id,handler.now))
    handler.advance_clock_v01(request.now+40)
    short = replace(event,request_id='request:t3-short',now=handler.now,ttl_seconds=5)
    pending = handler.prepare_playback_v01(short)
    assert pending['device']['bound'].canonical_projection.temporal_authority.expires_at_utc==short.now+5
    assert {root:host for root,(host,_) in handler.hosts.items()}==original_hosts
    persist('short_prepared.json',dict(event=asdict(short),packet=e.plain_value_v01(pending['device']['bound']),
        observation=e.plain_value_v01(pending['device']['observation']),session=asdict(pending['session'])))
    yield dict(handler=handler,prepared=pending,history=history,package=package,delayed=actual,hosts=original_hosts)
    handler.memory_directory.cleanup()


def test_current_start_delayed_valid_positive_and_historical_replay(current_start):
    actual = current_start['delayed'];package = current_start['package']
    assert actual['actions'][-1]['output']['playback_state']=='PLAYING'
    before = (tuple(world.CALLS),tuple(semantic.PROVIDER_CALLS))
    replay = e.replay_history_v01(package,expected_manifest_hash=package['manifest_hash'])
    assert replay['replay_status']=='PASS' and replay['current_permission']=='NOT_INFERRED_FROM_HISTORY'
    assert before==(tuple(world.CALLS),tuple(semantic.PROVIDER_CALLS))
    persist('delayed_history_replay.json',replay)


@pytest.mark.parametrize('change',('unchanged','session_expired','quality','content','device_expired','missing_dependency','changed_dependency'))
def test_current_start_public_eligibility_before_executor(current_start,change):
    base = current_start['handler'];branch = pending_branch(base)
    pending = branch.pending;device = pending['device'];source = device['source']
    original = source.read_current_v01()
    if change=='session_expired':
        branch.advance_clock_v01(branch.now+2)
    elif change=='quality':
        branch.set_device_state_v01(tuple(replace(d,max_quality=360) for d in branch.devices))
    elif change=='content':
        branch.set_device_state_v01(tuple(replace(d,permitted_content_ids=()) for d in branch.devices))
    elif change=='device_expired':
        branch.set_device_state_v01(tuple(replace(d,valid_to=branch.now+4) for d in branch.devices))
    elif change=='missing_dependency':
        source.withdraw_observations_v01((device['observation'].dependency_id,))
    elif change=='changed_dependency':
        # A real narrower device-grant record, not an inconsistent hash field.
        branch.set_device_state_v01(tuple(replace(d,valid_to=d.valid_to-1) for d in branch.devices))
    before = executor_calls();providers = tuple(semantic.PROVIDER_CALLS)
    clock = source.read_current_v01();host = device['host'];packet = device['bound'].packet_identity.packet_id
    inspection = hosts.inspect_current_action_v01(host,packet_id=packet,expected_revision=host.revision,
        evaluation_time=clock.evaluation_time,evaluation_time_source=clock.evaluation_time_source,evaluation_context_id=clock.evaluation_context_id)
    assert inspection.present_executable==(change=='unchanged')
    if change=='unchanged':
        result = life.dispatch_v01(device,pending['event'].request_id)
        assert result['output']['playback_state']=='PLAYING' and len(executor_calls())-len(before)==1
        reason = None
    else:
        with pytest.raises(ValueError,match='^host_current_action_not_executable$') as error:
            branch.dispatch_playback_v01(pending)
        reason = str(error.value)
        assert executor_calls()==before and branch.pending is pending and branch.active==base.active
    assert providers==tuple(semantic.PROVIDER_CALLS)
    assert e.validate_history_v01(current_start['history'])
    persist('current_start_'+change+'.json',dict(control=change,scope='INDEPENDENT_PUBLIC_DEVICE_HOST',
        before=e.plain_value_v01(original),after=e.plain_value_v01(clock),inspection=e.plain_value_v01(inspection),
        executor_delta=len(executor_calls())-len(before),reason=reason,registry=e.plain_value_v01(host.registry)))


def bank_branch(handler):
    pending=handler.pending_renewal;payment=pending['payment'];branch=copy.copy(handler)
    branch.events=list(handler.events);branch.renewal_records=[]
    source=world.LocalSourceV01(handler.now,payment['source'].snapshot.observations)
    admitted=e.payment_admission_v01(pending['request'])
    assert firewall.snapshot_admitted_capability_v01(admitted)==firewall.snapshot_admitted_capability_v01(payment['admitted'])
    host=hosts.build_root_work_execution_host_v01(owning_root_id='root:testflix:bank',registry=payment['pending_registry'],
        catalogue=(admitted,),packet_bindings=((payment['bound'].packet_identity.packet_id,payment['material']['corridor'],
            payment['material']['corridor_step'],admitted.admission_id,payment['inputs']),),
        current_dependency_observations=source.snapshot.observations,logical_time_bridge=source.snapshot.logical_time_bridge,trusted_source=source)
    branch.hosts={'bank':(host,source)}
    branch.pending_renewal=dict(pending,payment=dict(payment,host=host,source=source,admitted=admitted))
    return branch


@pytest.fixture(scope='module')
def continuing_renewal(request):
    preflight = getattr(request.config, 'testflix_bank_preflight_v08', None)
    request=c.request_from_plain_v01(json.loads((Path(__file__).resolve().parents[1]/'demo/testflix_fixtures_v01.json').read_text()))
    handler=e.TestflixHandlerV01();purchase=handler.handle_v01(request)
    original=e.seal_report_v01(purchase);original_hosts={k:id(v[0]) for k,v in handler.hosts.items()}
    handler.advance_clock_v01(request.now+10)
    info=handler.handle_event_v01(c.InformationRequestV01('request:t3-info',request.user_id,purchase['entitlement'].entitlement_id,handler.now))
    handler.advance_clock_v01(request.now+20)
    handler.handle_event_v01(c.StopPlaybackV01('request:t3-stop',request.user_id,purchase['session'].session_id,handler.now))
    handler.advance_clock_v01(request.now+30)
    fresh=handler.handle_event_v01(c.PlaybackRequestV01('request:t3-fresh',request.user_id,purchase['entitlement'].entitlement_id,
        request.device_id,request.content_id,handler.now,3600,720))
    handler.advance_clock_v01(purchase['entitlement'].candidate.valid_to-86400)
    quote=c.ProviderQuoteV01(purchase['entitlement'].candidate.plan,request.merchant_id,request.currency,handler.now,handler.now+3600,None)
    handler.observe_quote_v01(quote)
    event=c.RenewalIntentV01('request:t3-renewal-pending',request.user_id,purchase['entitlement'].entitlement_id,quote.quote_id,
        'order:t3-renewal-pending',handler.now,650,True)
    pending=handler.prepare_renewal_v01(event)
    unchanged=bank_branch(handler);within_consent=bank_branch(handler)
    unchanged.advance_clock_v01(event.now+31)
    before=executor_calls();positive=life.dispatch_v01(unchanged.pending_renewal['payment'],event.request_id)
    assert len(executor_calls())==len(before)+1 and positive['output']['amount_minor']==500
    persist('N14_unchanged_500.json',dict(scope='INDEPENDENT_BANK_BRANCH_NOT_MAIN_PAYMENT',
        receipt=e.plain_value_v01(positive['receipt']),execution=e.plain_value_v01(positive['execution']),
        payment=e._action_record_to_plain_v09(positive),executor_delta=1))
    handler.advance_clock_v01(event.now+30)
    changed=c.ProviderQuoteV01(replace(quote.plan,price_minor=700),quote.merchant_id,quote.currency,handler.now,handler.now+3600,quote.quote_id)
    handler.observe_quote_v01(changed);handler.advance_clock_v01(event.now+31)
    before=executor_calls();clock=handler.hosts['bank'][1].snapshot;host=handler.hosts['bank'][0]
    inspection=hosts.inspect_current_action_v01(host,packet_id=pending['payment']['bound'].packet_identity.packet_id,
        expected_revision=host.revision,evaluation_time=clock.evaluation_time,evaluation_time_source=clock.evaluation_time_source,
        evaluation_context_id=clock.evaluation_context_id)
    assert not inspection.present_executable
    with pytest.raises(ValueError,match='^host_current_action_not_executable$') as refused:
        life.dispatch_v01(pending['payment'],event.request_id)
    assert executor_calls()==before
    native_refusal=dict(inspection=e.plain_value_v01(inspection),reason=str(refused.value),executor_delta=len(executor_calls())-len(before),
        current_source=e.plain_value_v01(clock),packet=e.plain_value_v01(pending['payment']['bound']),
        scope='CURRENT_NATIVE_DEPENDENCY_REFUSAL_ONLY_NOT_E_ACCEPTANCE')
    persist('N14_current_quote_700.json',native_refusal)
    started=time.monotonic()
    if preflight is not None:preflight.check(handler)
    reprice=handler.reprice_pending_v01()
    assert e.validate_reprice_v01(reprice) and reprice['review']['result'].decision!='ACCEPT'
    assert executor_calls()==before
    bank_registry=handler.hosts['bank'][0].registry
    with pytest.raises(ValueError,match='^repriced_explicit_consent_limit$'):
        handler.authorize_repriced_payment_v01(reprice)
    assert handler.hosts['bank'][0].registry==bank_registry and executor_calls()==before
    persist('P04_main_700.json',e.reprice_to_plain_v01(reprice))
    print('T3_V03_MAIN_E_SECONDS='+str(time.monotonic()-started),flush=True)
    within_consent.advance_clock_v01(event.now+30)
    quote600=replace(changed,plan=replace(changed.plan,price_minor=600))
    within_consent.observe_quote_v01(quote600);within_consent.advance_clock_v01(event.now+31)
    started=time.monotonic()
    if preflight is not None:preflight.check(within_consent)
    reprice600=within_consent.reprice_pending_v01()
    assert reprice600['review']['result'].decision=='ACCEPT'
    new_payment=within_consent.authorize_repriced_payment_v01(reprice600)
    before600=executor_calls()
    paid600=life.dispatch_v01(new_payment,c.identity_v01('repriced_payment_request',
        dict(intent=event.request_id,quote=quote600.quote_id)))
    assert len(executor_calls())==len(before600)+1 and paid600['output']['amount_minor']==600
    assert new_payment['bound'].packet_identity.packet_id!=pending['payment']['bound'].packet_identity.packet_id
    persist('N14_600_review.json',e.reprice_to_plain_v01(reprice600))
    persist('N14_600_payment.json',dict(scope='INDEPENDENT_BANK_BRANCH_NOT_MAIN_PAYMENT',
        payment=e._action_record_to_plain_v09(paid600),executor_delta=len(executor_calls())-len(before600)))
    print('T3_V03_CONTROL_600_SECONDS='+str(time.monotonic()-started),flush=True)
    expiry=[]
    for label,when in (('boundary',purchase['entitlement'].candidate.valid_to-4),('after',purchase['entitlement'].candidate.valid_to-3)):
        handler.advance_clock_v01(when);before=executor_calls();providers=tuple(semantic.PROVIDER_CALLS)
        attempt=c.PlaybackRequestV01('request:expiry:'+label,request.user_id,purchase['entitlement'].entitlement_id,
            request.device_id,request.content_id,handler.now,60,720)
        with pytest.raises(ValueError,match='^current_entitlement$') as rejected:handler.prepare_playback_v01(attempt)
        assert executor_calls()==before and tuple(semantic.PROVIDER_CALLS)==providers
        row=dict(event=asdict(attempt),evaluation_time=handler.now+4,reason=str(rejected.value),executor_delta=0)
        expiry.append(row);persist('P05_'+label+'.json',row)
    handler.advance_clock_v01(purchase['entitlement'].candidate.valid_to+1)
    handler.handle_event_v01(c.StopPlaybackV01('request:expiry-stop',request.user_id,fresh['session'].session_id,handler.now))
    device_before=handler.devices
    grant=c.DeviceGrantRequestV01('request:fresh-device-grant',request.user_id,request.device_id,request.content_id,handler.now,handler.now+86400,1080)
    granted=handler.grant_device_v01(grant)
    fresh_quote=c.ProviderQuoteV01(replace(quote.plan,price_minor=700),quote.merchant_id,quote.currency,handler.now,handler.now+3600,changed.quote_id)
    handler.observe_quote_v01(fresh_quote)
    consent=c.RenewalIntentV01('request:renewal-explicit',request.user_id,purchase['entitlement'].entitlement_id,fresh_quote.quote_id,
        'order:renewal-explicit',handler.now,700,True)
    for invalid,reason in ((replace(consent,explicit_consent=False),'renewal_explicit_consent_required'),
            (replace(consent,quote_id=changed.quote_id),'renewal_scope'),(replace(consent,consent_limit_minor=650),'renewal_price_exceeds_consent')):
        before=executor_calls();providers=tuple(semantic.PROVIDER_CALLS)
        with pytest.raises(ValueError,match='^'+reason+'$') as rejected:handler.renew_v01(invalid)
        assert executor_calls()==before and tuple(semantic.PROVIDER_CALLS)==providers
        persist('renewal_rejection_'+reason+'.json',dict(event=asdict(invalid),reason=str(rejected.value),executor_delta=0,provider_delta=0))
    renewed=handler.renew_v01(consent)
    assert {k:id(v[0]) for k,v in handler.hosts.items()}==original_hosts and e.seal_report_v01(purchase)==original
    history=handler.history_v01();package=e.seal_history_v01(history)
    persist('P01_P06_history.json',package)
    replay=e.replay_history_v01(package,expected_manifest_hash=package['manifest_hash']);persist('P01_P06_replay.json',replay)
    yield dict(handler=handler,purchase=purchase,information=info,fresh=fresh,pending=pending,reprice=reprice,
        reprice600=reprice600,paid600=paid600,native_refusal=native_refusal,
        unchanged=positive,expiry=tuple(expiry),device_before=device_before,grant=granted,renewed=renewed,
        history=history,package=package,replay=replay,original=original,hosts=original_hosts)
    handler.memory_directory.cleanup()


def test_N14_current_native_quote_refusal_and_unchanged_positive(continuing_renewal):
    v=continuing_renewal;p=v['pending'];r=v['native_refusal']
    assert r['current_source']['evaluation_time']==p['event'].now+35<p['payment']['bound'].canonical_projection.temporal_authority.expires_at_utc
    assert r['executor_delta']==0 and r['reason']=='host_current_action_not_executable'
    assert v['unchanged']['output']['amount_minor']==500


def test_P04_required_actual_public_E_recomputation(continuing_renewal):
    report=continuing_renewal['reprice']
    bundle=report['delta']['bundle']
    assert bundle.delta.trace_refs==(bundle.dependency_graph.graph_id,)
    for artifact in (bundle.delta_source_proposed_artifact,bundle.delta_source_artifact):
        assert len(artifact.trace_refs)==len(set(artifact.trace_refs))
        assert set(bundle.delta.trace_refs+bundle.delta.ordered_source_binding_ids)<=set(artifact.trace_refs)
    assert e.validate_reprice_v01(report)
    assert report['delta']['bundle'].recomputation_result and report['review']['result'].decision!='ACCEPT'
    assert continuing_renewal['reprice600']['review']['result'].decision=='ACCEPT'
    assert continuing_renewal['paid600']['output']['amount_minor']==600
    for row in (report, continuing_renewal['reprice600']):
        value = e.semantic_work.semantic_work_to_plain_dict_v01(row['review']['contribution'].claims[0])['object_or_value']
        recomputed = row['delta']['bundle'].recomputed_g2d_execution_bundle
        outputs = set(value['recomputed_output_refs'])
        binding = next(b for b in row['delta']['bundle'].recomputed_bindings if b.new_artifact_id == value['recomputed_quote_ref'])
        selected_cell = next(r.cell_id for r in recomputed.cell_results if r.result_id == binding.g2d_cell_result_ref)
        consumed = tuple(q for q in recomputed.queue_entries if q.cell_id == selected_cell and q.state == 'COMPLETED'
            and outputs.intersection(q.observed_output_refs))
        assert consumed and all(value['consumed_binding_ref'] in q.observed_evidence_refs for q in consumed)
        assert value['consumed_binding_ref'] != recomputed.observed_work_context.observed_work_context_id
    row = continuing_renewal['reprice600']
    claim = e.semantic_work.semantic_work_to_plain_dict_v01(row['review']['contribution'].claims[0])['object_or_value']
    changed = dict(claim, consumed_binding_ref='binding:coherently-substituted-review:v09')
    review = e.kernel.review_information_v01(transaction=row['delta']['bundle'].delta.transaction_id,
        selected=c.identity_v01('repriced_terms', changed), subject=row['pending']['event'].order_id,
        predicate='review_repriced_renewal_against_explicit_consent', value=changed,
        quote=row['pending']['quote_work'], valid=True, root='root:testflix:bank')
    assert not e.roots.validate_root_decision_result_v01(kernel=review['kernel'], decision_input=review['inputs'], result=review['result'])
    before = executor_calls()
    with pytest.raises(ValueError, match='^reprice_decision_binding$'):
        e.validate_reprice_v01(dict(row, review=review))
    assert executor_calls() == before and e.validate_reprice_v01(row)
    persist('N15_consumed_binding_review_v09.json',dict(reason='reprice_decision_binding',
        reconstructed_root_review=e.plain_value_v01(review),executor_delta=0))


def test_N17_N19_exact_expiry_fresh_consent_and_device_basis(continuing_renewal):
    v=continuing_renewal;old=v['purchase']['entitlement'];new=v['renewed']['renewal']
    assert tuple(r['evaluation_time'] for r in v['expiry'])==(old.candidate.valid_to,old.candidate.valid_to+1)
    assert all(r['executor_delta']==0 and r['reason']=='current_entitlement' for r in v['expiry'])
    assert new['entitlement'].candidate.payment_receipt_ref==new['payment']['output']['payment_ref']
    assert new['entitlement'].candidate.plan.price_minor==700 and new['entitlement'].candidate.valid_from>old.candidate.valid_to
    assert new['entitlement'].candidate.valid_to-new['entitlement'].candidate.valid_from==30*86400
    assert max(d.valid_to for d in v['device_before'])<v['grant']['event'].now
    assert v['grant']['actions'][0]['output']['valid_to']==v['grant']['event'].valid_to
    assert new['session'].candidate.valid_to<=min(new['entitlement'].candidate.valid_to,v['grant']['event'].valid_to)
    assert new['payment']['bound'].packet_identity.packet_id!=v['purchase']['payment']['bound'].packet_identity.packet_id


def test_N15_actual_dependency_and_preserved_period_controls_v03(continuing_renewal):
    api=kernel.delta_api;record=continuing_renewal['reprice'];arguments=record['delta']['arguments']
    source=arguments['source_context'];graph=arguments['dependency_graph'];edges=arguments['dependency_edges']
    b=source.g2b_resolution_report
    bindings=tuple((v.dependent_artifact_id,v.dependency_artifact_id,v.dependency_field_pointers,v.edge_class) for v in edges)
    kwargs=dict(manifest=source.integrity_manifest,replay=source.integrity_replay,
        source_artifacts=source.baseline_source_artifacts,graph_version=graph.graph_version,
        transaction_id=graph.transaction_id,owning_root_id=graph.owning_root_id,domain_id=graph.domain_id,
        policy_version=graph.policy_version,schema_versions=graph.schema_versions,source_history_hash=graph.source_history_hash)
    fresh_basis,fresh_edges=api.project_integrity_replay_dependency_edges_v01(**kwargs,
        edge_projection_bindings=tuple(tuple(list(v)) for v in bindings))
    assert fresh_edges==edges and fresh_edges is not edges and fresh_basis==graph.graph_basis_sha256
    changed_source=arguments['source_bindings'][0].baseline_source_artifact_id
    omitted=tuple(v for v in bindings if v[1]!=changed_source)
    assert len(omitted)==len(bindings)-1 and omitted
    with pytest.raises(ValueError,match='^g2e_dependency_graph_missing_edge$') as error:
        api.project_integrity_replay_dependency_edges_v01(**kwargs,edge_projection_bindings=omitted)
    persist('N15_dependency_omission.json',dict(reason=str(error.value),fresh_equivalent=True,
        omitted_source=changed_source,remaining_edges=omitted,scope='ACTUAL_PUBLIC_MANIFEST_EDGE_RELATION'))

    def affected_for(observed):
        old=arguments['delta'];fingerprint=api.build_dependency_fingerprint_v01(
            profile=api.build_dependency_fingerprint_profile_v01(),graph=graph,dependency_edges=edges,
            source_artifacts=observed,policy_version=graph.policy_version,schema_versions=graph.schema_versions,
            source_history_hash=graph.source_history_hash)
        changed=[]
        for item in arguments['changed_artifact_bindings']:
            item=replace(item,observed_dependency_fingerprint=fingerprint)
            changed.append(replace(item,changed_artifact_binding_id=api.rebuild_changed_artifact_binding_identity_v01(item)))
        delta=replace(old,dependency_fingerprint_after=fingerprint,
            ordered_changed_artifact_binding_ids=tuple(v.changed_artifact_binding_id for v in changed))
        delta=replace(delta,delta_id=api.rebuild_world_state_delta_identity_v01(delta))
        request=api.build_affected_set_request_v01(delta=delta,graph=graph,trace_refs=(delta.delta_id,graph.graph_id))
        return api.compute_affected_set_v01(request=request,delta=delta,graph=graph,
            source_bindings=arguments['source_bindings'],changed_field_bindings=arguments['changed_field_bindings'],
            changed_artifact_bindings=tuple(changed),dependency_edges=edges,
            baseline_source_artifacts=source.baseline_source_artifacts,observed_source_artifacts=observed)

    preserved=tuple(a for a in source.observed_source_artifacts
        if 'entitlement' in kernel.abi.kernel_artifact_to_plain_dict_v01(a)['payload'])
    assert len(preserved)==1
    old=preserved[0];plain=kernel.abi.kernel_artifact_to_plain_dict_v01(old)
    equal=kernel.abi.build_kernel_artifact_v01(**dict(plain,trace_refs=tuple(plain['trace_refs']),parent_refs=tuple(plain['parent_refs'])))
    observed=tuple(equal if a is old else a for a in source.observed_source_artifacts)
    assert equal is not old and equal==old and affected_for(observed)==record['delta']['bundle'].affected_result
    payload=copy.deepcopy(plain['payload']);payload['output']['valid_to']+=1
    altered=kernel.delta_artifact_v01(payload,old.transaction_id,old.owner_root_id,
        record['observed_quote'].observed_at,parents=(old.artifact_id,))
    assert not kernel.abi.validate_kernel_artifact_v01(altered)
    with pytest.raises(ValueError,match='^g2e_delta_source_binding_set_mismatch$') as error:
        affected_for(tuple(altered if a.artifact_id==old.artifact_id else a for a in observed))
    persist('N15_preserved_period_change.json',dict(reason=str(error.value),fresh_equivalent=True,
        old=plain,altered=kernel.abi.kernel_artifact_to_plain_dict_v01(altered),
        scope='UNREPORTED_CHANGED_PRESERVED_SOURCE_WITH_FRESH_FINGERPRINT_AND_DELTA_IDENTITIES'))
    retained = record['delta']['bundle'].recomputed_g2d_execution_bundle
    binding = retained.temporal_binding
    equivalent = replace(binding)
    positive = kernel.fractal.validate_fractal_current_temporal_binding_v01(equivalent,
        source_context=retained.source_context,temporal_verification=retained.temporal_verification)
    assert equivalent is not binding and equivalent == binding and positive.status == 'PASS'
    refused = []
    for field,value in (('evaluation_time_epoch_seconds',binding.evaluation_time_epoch_seconds+1),
            ('host_revision',binding.host_revision+1)):
        altered = replace(equivalent,**{field:value})
        result = kernel.fractal.validate_fractal_current_temporal_binding_v01(altered,
            source_context=retained.source_context,temporal_verification=retained.temporal_verification)
        assert result.status == 'FAIL_CLOSED'
        refused.append(dict(field=field,value=value,result=e.plain_value_v01(result)))
    persist('N15_Bank_retained_temporal_binding.json',dict(positive=e.plain_value_v01(positive),
        binding=e.plain_value_v01(binding),refusals=refused,
        scope='ACTUAL_BANK_RETAINED_SOURCE_PAIR; NO_CONTENT_ID_FIELD; HISTORICAL_NOT_CURRENT_PERMISSION',
        attribution='PUBLIC_RESULT_OBSERVED; SOURCE_PAIR_REASON_STATIC'))


def test_N20_supplied_current_history_and_no_live_replay(continuing_renewal):
    v=continuing_renewal;history=v['history']
    assert e.validate_history_v01(history)
    before=(tuple(world.CALLS),tuple(semantic.PROVIDER_CALLS))
    replay=e.replay_history_v01(v['package'],expected_manifest_hash=v['package']['manifest_hash'])
    assert replay['replay_status']=='PASS' and before==(tuple(world.CALLS),tuple(semantic.PROVIDER_CALLS))
    assert v['handler'].handle_v01(v['purchase']['request']) is v['purchase']
    assert v['handler'].handle_event_v01(v['fresh']['event']) is v['fresh']
    assert before==(tuple(world.CALLS),tuple(semantic.PROVIDER_CALLS))
    assert e.seal_report_v01(v['purchase'])==v['original']
    renewal=v['renewed'];report=renewal['renewal'];ent=report['entitlement']
    equivalent_ent=replace(ent,candidate=replace(ent.candidate))
    assert equivalent_ent is not ent and equivalent_ent==ent
    equivalent_report=dict(report,entitlement=equivalent_ent)
    equivalent_event=dict(renewal,renewal=equivalent_report,
        after=dict(renewal['after'],entitlements=renewal['before']['entitlements']+(equivalent_ent,)))
    equivalent=dict(history,events=history['events'][:-1]+(equivalent_event,))
    assert e.validate_history_v01(equivalent) and e.history_to_plain_v01(equivalent)==e.history_to_plain_v01(history)
    foreign=dict(equivalent_report,payment=v['purchase']['payment'])
    with pytest.raises(ValueError,match='^action_root_operation:payment$'):
        e.validate_history_v01(dict(equivalent,events=equivalent['events'][:-1]+(dict(equivalent_event,renewal=foreign),)))
    bad=dict(history,quotes=history['quotes'][:-1])
    with pytest.raises(ValueError,match='history_renewal_current_quote'):e.validate_history_v01(bad)


def test_N18_historical_receipt_is_not_consent_or_foreign_root_authority(continuing_renewal):
    v=continuing_renewal;handler=v['handler'];payment=v['renewed']['renewal']['payment']
    before=(tuple(world.CALLS),tuple(semantic.PROVIDER_CALLS))
    with pytest.raises(ValueError,match='^renewal_current_quote_required$'):
        handler.renew_v01(v['purchase']['payment']['receipt'])
    host,source=handler.hosts['device'];clock=source.snapshot;registry=host.registry
    with pytest.raises(ValueError,match='^host_foreign_root$') as rejected:
        hosts.install_current_action_v01(host,root_bound=payment['bound'],admission_id=payment['admitted'].admission_id,
            inputs=payment['inputs'],**payment['material'],expected_revision=host.revision,
            evaluation_time=clock.evaluation_time,evaluation_time_source=clock.evaluation_time_source,evaluation_context_id=clock.evaluation_context_id)
    assert registry is host.registry and before==(tuple(world.CALLS),tuple(semantic.PROVIDER_CALLS))
    persist('N18_actual_foreign_root.json',dict(reason=str(rejected.value),
        source_root=payment['bound'].canonical_projection.owning_local_root_id,target_root=host.owning_root_id,
        executor_delta=len(executor_calls())-sum(v[0]=='EXECUTOR' for v in before[0])))


@pytest.fixture(scope='module')
def post_renewal(continuing_renewal):
    v=continuing_renewal;handler=v['handler'];report=v['renewed']['renewal'];started=time.monotonic()
    handler.advance_clock_v01(handler.now+10)
    stopped_event=c.StopPlaybackV01('request:v02-stop-renewed',report['request'].user_id,report['session'].session_id,handler.now)
    before=executor_calls();providers=tuple(semantic.PROVIDER_CALLS)
    stopped=handler.handle_event_v01(stopped_event)
    assert len(executor_calls())-len(before)==2 and not handler.active
    stopped_history=handler.history_v01()
    fresh_event=c.PlaybackRequestV01('request:v02-fresh-renewed',report['request'].user_id,report['entitlement'].entitlement_id,
        report['request'].device_id,report['request'].content_id,handler.now,60,720)
    for event,reason in ((replace(fresh_event,entitlement_id=v['purchase']['entitlement'].entitlement_id),'current_entitlement'),
            (replace(fresh_event,entitlement_id='entitlement:foreign'),'current_entitlement')):
        before=tuple(world.CALLS)
        with pytest.raises(ValueError,match='^'+reason+'$'):handler.prepare_playback_v01(event)
        assert tuple(world.CALLS)==before
    # Same current time and state as the refused old/foreign period requests.
    before=executor_calls();fresh=handler.handle_event_v01(fresh_event)
    assert len(executor_calls())-len(before)==2 and providers==tuple(semantic.PROVIDER_CALLS)
    history=handler.history_v01();package=e.seal_history_v01(history)
    assert history['events'][:len(v['history']['events'])]==v['history']['events']
    assert {k:id(p[0]) for k,p in handler.hosts.items()}==v['hosts']
    assert len(handler.reports)==len(handler.entitlements)==len(handler.consumed_periods)==2
    persist('post_renewal_expanded_history.json',package)
    result=dict(stopped=stopped,fresh=fresh,history=history,package=package,stopped_history=stopped_history,
        payments=tuple(r['payment']['execution'].invocation.invocation_id for r in handler.reports.values()))
    persist('post_renewal_result.json',dict(stop_executor_delta=2,fresh_executor_delta=2,provider_delta=0,
        main_payment_invocations=result['payments'],main_payment_count=len(result['payments']),
        hosts_preserved=True,elapsed_seconds=time.monotonic()-started,session_id=fresh['session'].session_id,
        entitlement_id=fresh['session'].candidate.entitlement_id,
        provider_decision_id=fresh['session'].provider_decision_id,
        device_decision_id=fresh['actions'][1]['bound'].root_decision_projection.root_decision_result.decision_id))
    return result


def test_post_renewal_stop_and_fresh_session_same_period(continuing_renewal,post_renewal):
    v=continuing_renewal;p=post_renewal;report=v['renewed']['renewal']
    assert p['stopped']['session']==report['session']
    assert p['fresh']['session'].candidate.entitlement_id==report['entitlement'].entitlement_id
    assert p['fresh']['session'].session_id!=report['session'].session_id
    assert p['fresh']['session'].provider_decision_id!=report['session'].provider_decision_id
    assert p['fresh']['actions'][1]['bound'].packet_identity.packet_id!=report['playback']['bound'].packet_identity.packet_id
    assert len(set(p['payments']))==2 and e.validate_history_v01(p['history'])


def test_post_renewal_equivalent_period_and_foreign_payment_rejected(continuing_renewal,post_renewal):
    v=continuing_renewal;p=post_renewal;history=p['history'];renewal=v['renewed'];report=renewal['renewal']
    ent=replace(report['entitlement'],candidate=replace(report['entitlement'].candidate))
    equivalent_report=dict(report,entitlement=ent)
    equivalent_renewal=dict(renewal,renewal=equivalent_report,
        after=dict(renewal['after'],entitlements=renewal['before']['entitlements']+(ent,)))
    events=tuple(equivalent_renewal if row is renewal else row for row in history['events'])
    equivalent=dict(history,events=events)
    assert ent is not report['entitlement'] and e.validate_history_v01(equivalent)
    assert e.history_to_plain_v01(equivalent)==e.history_to_plain_v01(history)
    foreign=dict(equivalent_report,payment=v['purchase']['payment'])
    poisoned=dict(equivalent,events=tuple(dict(row,renewal=foreign) if row is equivalent_renewal else row for row in events))
    with pytest.raises(ValueError,match='^action_root_operation:payment$'):e.validate_history_v01(poisoned)
    for field,value in (('entitlements',history['purchase']['entitlement']),('consumed_periods',v['history']['events'][0]['before']['consumed_periods'][0])):
        row=p['fresh'];bad_before=dict(row['before'],**{field:(value,)})
        bad_after=dict(row['after'],**{field:(value,)})
        poisoned=dict(history,events=history['events'][:-1]+(dict(row,before=bad_before,after=bad_after),))
        with pytest.raises(ValueError,match='^history_purchase_immutable$'):e.validate_history_v01(poisoned)


def test_post_renewal_live_lineage_refused_before_effect(continuing_renewal,post_renewal):
    handler=continuing_renewal['handler'];report=continuing_renewal['renewed']['renewal']
    event=c.StopPlaybackV01('request:v02-poisoned-period',report['request'].user_id,post_renewal['fresh']['session'].session_id,handler.now)
    for kind in ('period','payment'):
        branch=copy.copy(handler);branch.reports=dict(handler.reports);branch.events=list(handler.events)
        if kind=='period':branch.consumed_periods=branch.consumed_periods[:1]
        else:branch.reports[report['request'].request_id]=dict(report,payment=continuing_renewal['purchase']['payment'])
        before=(tuple(world.CALLS),tuple(semantic.PROVIDER_CALLS));active=branch.active
        with pytest.raises(ValueError,match='^period_(current_lineage|report_origin)$'):branch.handle_event_v01(event)
        assert before==(tuple(world.CALLS),tuple(semantic.PROVIDER_CALLS)) and branch.active==active


def test_post_renewal_repeated_requests_replay_and_information_limit(continuing_renewal,post_renewal):
    v=continuing_renewal;p=post_renewal;handler=v['handler'];report=v['renewed']['renewal']
    before=(tuple(world.CALLS),tuple(semantic.PROVIDER_CALLS))
    assert handler.handle_event_v01(p['stopped']['event']) is p['stopped']
    assert handler.handle_event_v01(p['fresh']['event']) is p['fresh']
    assert handler.handle_v01(v['purchase']['request']) is v['purchase']
    for entitlement,reason in ((report['entitlement'],'information_period_not_supported'),
            (v['purchase']['entitlement'],'information_period_not_current')):
        event=c.InformationRequestV01('request:v02-info:'+entitlement.entitlement_id,report['request'].user_id,entitlement.entitlement_id,handler.now)
        with pytest.raises(ValueError,match='^'+reason+'$'):handler.handle_event_v01(event)
    for package in (v['package'],p['package']):
        replay=e.replay_history_v01(package,expected_manifest_hash=package['manifest_hash'])
        assert replay['replay_status']=='PASS' and replay['current_permission']=='NOT_INFERRED_FROM_HISTORY'
    assert e.replay_v01(v['original'],expected_manifest_hash=v['original']['manifest_hash'])['replay_status']=='PASS'
    assert before==(tuple(world.CALLS),tuple(semantic.PROVIDER_CALLS))
    assert e.seal_report_v01(v['purchase'])==v['original']
