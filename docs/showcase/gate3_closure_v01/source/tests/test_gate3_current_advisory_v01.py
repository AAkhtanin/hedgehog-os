"""Real predictive Work, durable history, and current advisory integration."""
import json
import os
from pathlib import Path
import time

import pytest
from hedgehog import outcome_feedback_v01 as feedback
from hedgehog import outcome_calibration_v01 as cal
from hedgehog.domains.landslide_sentinel import events_v01 as events, semantic_adapter_v01 as sem
from hedgehog.domains.landslide_sentinel.monitoring_runtime_v01 import ControlledEpisode
from hedgehog.domains.landslide_sentinel.outcome_feedback_adapter_v01 import SentinelPredictiveSourceV01

ROOT=Path(__file__).resolve().parents[1]


@pytest.fixture(scope='module')
def retained_stream(request,tmp_path_factory):
    """Immutable source reuse is not a reconstructed native Host or fresh event."""
    import hashlib
    location=os.environ.get('G34_RETAINED_SOURCE_DIR')
    if location is None:
        fresh=request.getfixturevalue('predictive_stream')
        directory=Path(os.environ['G33R_EVIDENCE'])/'commands'/os.environ['G33R_COMMAND']/'current' if 'G33R_EVIDENCE' in os.environ else tmp_path_factory.mktemp('g34r2_current')
        directory.mkdir(parents=True,exist_ok=True)
        return dict(fresh,directory=directory,native_directory=fresh['directory'])
    source=Path(location)
    pins=json.loads((source/'SOURCE_PINS.json').read_bytes())
    pin_file=os.environ.get('G34_RETAINED_PIN_FILE')
    expected=json.loads(Path(pin_file).read_bytes()) if pin_file else json.loads((ROOT/'fixtures/gate3_history_reference_v01.json').read_bytes())['retained_source_pins']
    assert pins==expected
    for rel,pin in pins.items():
        raw=(source/rel).read_bytes();assert len(raw)==pin['bytes'] and hashlib.sha256(raw).hexdigest()==pin['sha256']
    bound=tuple(cal.SourceBoundGTEventV01((source/f'{i}_feedback.json').read_bytes(),(source/f'{i}_source.json').read_bytes(),
        feedback.PREDICTIVE_SOURCE_PROFILE_ID) for i in range(1,8))
    directory=Path(os.environ['G33R_EVIDENCE'])/'commands'/os.environ['G33R_COMMAND']/'current' if 'G33R_EVIDENCE' in os.environ else tmp_path_factory.mktemp('g34r')
    directory.mkdir(parents=True,exist_ok=True)
    return dict(events=bound,directory=directory,retained_source_directory=source)


@pytest.fixture(scope='module')
def current_repair(retained_stream):
    from hedgehog import outcome_feedback_history_v01 as history
    from hedgehog.domains.landslide_sentinel.outcome_feedback_adapter_v01 import G34ControlledCurrentWorkV01
    f=retained_stream;stream=tuple(f['events']);directory=f['directory'];now=max(int(time.time()),max(json.loads(e.feedback_canonical)['timestamp'] for e in stream))
    source=json.loads(stream[-1].source_canonical);key=json.loads(stream[0].feedback_canonical)['avf_history_key'];root=key['local_root_scope_id']
    a=json.loads(source['result_artifact']['payload']['work_results'][0]['invocation']['inputs'][0]['value'])
    b=dict(records=a['checks'][0]['observations'],tick=a['checks'][0]['tick'],site=a['checks'][0]['site'],policy=a['contract'],purpose='local')
    materials=[dict(candidate_id='g34:candidate:A',operation='sentinel.diagnostic.v01',base_score='0.70',material=a),
        dict(candidate_id='g34:candidate:B',operation='sentinel.observability.v01',base_score='0.67',material=b)]
    fixture=json.loads((ROOT/'fixtures/landslide_sentinel/ls1_inputs_v01.json').read_bytes())
    def context(rows):return G34ControlledCurrentWorkV01(root=root,frames=a['frames'],reference_note=fixture['reference_note'],
        materials=rows,valid_from=now,valid_to=now+604800)
    def store(name,values):
        s=history.OutcomeHistoryV01(directory/name,trusted_events=stream)
        snapshot,review=s.prepare_v01([json.loads(e.feedback_canonical)['feedback_id'] for e in values],expected_head=None,evaluated_at=now)
        s.commit_v01(snapshot,review,expected_head=None);return s
    negative=store('negative',stream[:3]);positive=store('positive',stream[4:]);ctx=context(materials);time_ctx=context(materials[:1])
    values={};live={};receipts={}
    def save(name,pair):
        values[name],live[name]=pair
        (directory/(name+'.json')).write_text(json.dumps(values[name],sort_keys=True)+'\n')
    def check(name,context,when):
        save(name+'_check',context.evaluate_check_v01(request=live[name]['check_request'],now=when,invocation='g34r:'+name+':check'))
        v=live[name+'_check'];receipts[name]=(v['program'],v['results'],v['common'],{root:v['host']})
    for name,s in (('neutral',None),('learned',negative)):
        save(name,ctx.evaluate_v01(store=s,history_key=key,now=now,invocation='g34r:'+name))
        check(name,ctx,now)
        save(name+'_complete',ctx.evaluate_v01(store=s,history_key=key,now=now,invocation='g34r:'+name+':complete',additional_receipt=receipts[name]))
    save('fresh',time_ctx.evaluate_v01(store=positive,history_key=key,now=now,invocation='g34r:fresh'))
    save('aged',time_ctx.evaluate_v01(store=positive,history_key=key,now=now+50330,invocation='g34r:aged'))
    check('aged',time_ctx,now+50330)
    save('resumed',time_ctx.evaluate_v01(store=positive,history_key=key,now=now+50330,invocation='g34r:resumed',additional_receipt=receipts['aged']))
    return dict(stream=stream,directory=directory,now=now,key=key,root=root,negative=negative,positive=positive,
        context=ctx,time_context=time_ctx,values=values,live=live,receipts=receipts,materials=materials)


@pytest.fixture(scope='session')
def predictive_stream(request,tmp_path_factory):
    # Imported fixture definitions in the two test modules share one live stream.
    if hasattr(request.session,'_g34r2_predictive_stream'):
        yield request.session._g34r2_predictive_stream
        return
    directory=Path(os.environ['G34_NATIVE']) if 'G34_NATIVE' in os.environ else tmp_path_factory.mktemp('g34_native')
    directory.mkdir(parents=True,exist_ok=True)
    fixture=json.loads((ROOT/'fixtures/landslide_sentinel/ls1_inputs_v01.json').read_bytes())
    spec=json.loads((ROOT/'fixtures/gate3_sentinel_observation_v01.json').read_bytes())
    session=ControlledEpisode(directory/'episode',fixture)
    store=SentinelPredictiveSourceV01(session)
    captures=[];bound=[]
    # Inputs and prediction are declared before executing any outcome.
    schedule=[False,False,False,True,True,True,True]
    expected_negative=expected_positive=cal.Q//2
    for index,independent in enumerate(schedule,1):
        started=time.monotonic()
        tick=120+index
        rows=[events.observation(v['sensor'],v['value'],tick,index,
            lineage=('independent:'+v['sensor']) if independent or v['sensor']=='rainfall' else 'controlled:correlated_pair') for v in fixture['frames']]
        session.ingest(rows,tick)
        semantic=sem.collect(session.frames,fixture['maintenance_note'],session.root,session.source.sample().evaluation_time,
            controlled=spec['response'],intended_role=spec['role'],capabilities=session.capabilities.snapshot(spec['role']),
            observations=tuple(session.book.latest.values()),tick=tick,policy=session.contract)[1]
        expectation=expected_negative if index<=4 else expected_positive
        capture=store.observe_v01(semantic,expected_fp=expectation)
        source,observation,value=store.feedback_v01(capture)
        event=cal.bind_outcome_feedback_event_v01(value,source_bundle=source,profile=feedback.PREDICTIVE_SOURCE_PROFILE_ID)
        data=json.loads(value.canonical)
        assert data['proposal_assessment']==('CORRECT' if independent else 'INCORRECT')
        assert data['task_outcome']=='COMPLETED' and data['enforcement_outcome']=='ALLOWED_AS_REQUIRED'
        if index<=4: expected_negative+=cal.round_half_even_rational_v01(cal.K_FP*((cal.Q if independent else 0)-expectation),cal.Q)
        else: expected_positive+=cal.round_half_even_rational_v01(cal.K_FP*(cal.Q-expectation),cal.Q)
        captures.append(capture);bound.append(event)
        for name,body in (('source',source.canonical),('observation',observation.canonical),('feedback',value.canonical)):
            (directory/(str(index)+'_'+name+'.json')).write_bytes(body)
        _g34r2_capture_native_bundles(session,source,directory,index)
        with (directory/'phases.jsonl').open('a') as stream:
            stream.write(json.dumps(dict(phase='native_prediction',index=index,seconds=time.monotonic()-started))+'\n')
    request.session._g34r2_predictive_stream=dict(directory=directory,session=session,store=store,captures=captures,events=bound)
    yield request.session._g34r2_predictive_stream
    assert not session.executed
    (directory/'finalizer.json').write_text(json.dumps(dict(effects=len(session.executed),source_reads=session.source.reads,work_commands=session.work_request_sequence)))


def _g34r2_capture_native_bundles(session,source,directory,index):
    """Capture real accepted plan/result programs before the next dependency ingest."""
    from tests.test_work_composition_v01 import _g34r2_native_causal_artifacts,actual_evidence_plain_v03
    from hedgehog.kernel import abi_v01 as abi
    result=session.reviewed_role_result(json.loads(source.canonical)['result_artifact']['artifact_id'])
    record=session.role_results[-1]
    plan=session.accepted_plans[record['plan_basis']['work_artifact_ref']]
    bundles=[]
    for label,basis in (('plan',plan),('result',result)):
        artifacts=_g34r2_native_causal_artifacts(basis.program,basis.common,basis.artifact)
        refs=basis.program.source_bindings
        assert len(refs)==3 and not abi.validate_causal_consumption_bundle_v01(artifacts=artifacts,causal_refs=refs)
        bundles.append(dict(stage=label,artifacts=[abi.kernel_artifact_to_plain_dict_v01(a) for a in artifacts],
            native_refs=actual_evidence_plain_v03(refs),program=actual_evidence_plain_v03(basis.program),
            input_sha256=__import__('hashlib').sha256(basis.material).hexdigest(),
            root_result=actual_evidence_plain_v03(basis.review[2]),validation='PASS'))
    (directory/(str(index)+'_native_causal.json')).write_text(json.dumps(bundles,sort_keys=True)+'\n')


def test_g34_actual_predictive_source_and_prior(predictive_stream):
    f=predictive_stream
    now=int(time.time())
    negative=cal.fold_avf_history_prior_v01(tuple(f['events'][:3]),evaluated_at=now)
    assert negative.to_plain_data()['prior_fp']==-176025391
    assert cal.adjusted_avf_score_v01(700000000,-176025391)==(655993652,655994)
    recovery=cal.fold_avf_history_prior_v01(tuple(f['events'][:4]),evaluated_at=now)
    assert recovery.to_plain_data()['prior_fp']>negative.to_plain_data()['prior_fp']
    positive=cal.bounded_gt_event_fold_v01(tuple(f['events'][4:]),evaluated_at=now)
    assert positive.updates[-1].to_plain_data()['rating_after_fp']==665039062
    assert positive.updates[-1].to_plain_data()['half_life_seconds']==50330
    for capture in f['captures']:
        assert f['store'].validate_capture_v01(capture).canonical==capture.source_canonical
    for name,value in (('negative_prior',negative.to_plain_data()),('recovery_prior',recovery.to_plain_data()),('positive_update',positive.updates[-1].to_plain_data())):
        (f['directory']/(name+'.json')).write_text(json.dumps(value,sort_keys=True))


def test_g34_current_rank_and_time_work(current_repair):
    f=current_repair;v=f['values'];live=f['live']
    for name in ('neutral','learned','aged'):
        assert v[name]['review']['result']['decision']=='NEEDS_MORE_EVIDENCE'
        assert v[name]['work'] is None and live[name]['main_work_calls']==0
        assert not live[name]['host'].work_attempts and not live[name]['host'].completed_work
        assert v[name+'_check']['work']['operation']=='sentinel.observability.v01'
    assert v['neutral_complete']['work']['operation']=='sentinel.diagnostic.v01'
    assert v['learned_complete']['work']['operation']=='sentinel.observability.v01'
    assert v['neutral']['context']['inputs_sha256']==v['learned']['context']['inputs_sha256']
    assert v['neutral']['contract']['mandatory']==v['learned']['contract']['mandatory']
    assert v['learned']['projection']['trust']['trust_status']=='COLD_START_NEUTRAL'
    assert v['learned']['projection']['rows'][1]['subject_status']=='COLD_OR_NONMATCHING'
    fresh=v['fresh']['projection']['trust'];aged=v['aged']['projection']['trust']
    assert fresh['subject_key']==v['fresh']['contract']['claims']['g34:candidate:A']['subject']
    assert fresh['trust_at_time_fp']==cal.evaluate_gt_decay_value_v01(665039062,age_seconds=fresh['age_seconds'],half_life_seconds=50330)
    assert aged['age_seconds']==fresh['age_seconds']+50330
    assert aged['trust_at_time_fp']==cal.evaluate_gt_decay_value_v01(665039062,age_seconds=aged['age_seconds'],half_life_seconds=50330)
    assert v['fresh']['review']['result']['decision']==v['resumed']['review']['result']['decision']=='ACCEPT'
    assert v['fresh']['work']['operation']==v['resumed']['work']['operation']=='sentinel.diagnostic.v01'
    original=live['aged_check']['artifact']
    bridge=v['resumed']['receipt_bridge']
    assert bridge['transaction_id']!=original.transaction_id
    assert bridge['payload']['original_ref']['transaction_id']==original.transaction_id
    from hedgehog.kernel import abi_v01 as abi
    for name,current in live.items():
        if 'artifacts' in current:
            assert all(r in current['causal'] for r in current['program'].source_bindings)
            assert not abi.validate_causal_consumption_bundle_v01(artifacts=current['artifacts'],causal_refs=current['causal'])
    assert cal.evaluate_review_pressure_v01(trust_status='USABLE',trust_at_time_fp=600000000)==(400000000,False)


def test_g34_predictive_schema_sources_and_origin(predictive_stream):
    from copy import deepcopy
    from dataclasses import replace
    from jsonschema import Draft202012Validator
    f=predictive_stream;event=f['events'][0];capture=f['captures'][0]
    source=f['store'].validate_capture_v01(capture)
    value=feedback.OutcomeFeedbackEnvelopeV01(event.feedback_canonical)
    assert not feedback.validate_outcome_feedback_against_sources_v01(value,source_bundle=source,profile=feedback.PREDICTIVE_SOURCE_PROFILE_ID)
    schema=json.loads((ROOT/'schemas/outcome_feedback_g34_predictive_v01.schema.json').read_bytes())
    Draft202012Validator(schema).validate(json.loads(value.canonical))
    observation=json.loads((f['directory']/'1_observation.json').read_bytes())
    Draft202012Validator(dict(schema,**{'$ref':'#/$defs/observation'})).validate(observation)
    assert f['store'].validate_capture_v01(replace(capture)).canonical==source.canonical
    for bad in (replace(capture,_origin=object()),replace(capture,ordinal=64),replace(capture,source_canonical=capture.source_canonical+b' ')):
        with pytest.raises(ValueError): f['store'].validate_capture_v01(bad)
    for field,new in (('proposal_assessment','CORRECT'),('transaction_id','foreign:transaction'),('local_root_scope_id','foreign:root')):
        plain=json.loads(value.canonical);plain[field]=new
        plain['feedback_id']=feedback._identity('g3_feedback_v01',{k:v for k,v in plain.items() if k!='feedback_id'})
        changed=feedback.OutcomeFeedbackEnvelopeV01(feedback._canonical(plain))
        assert feedback.validate_outcome_feedback_against_sources_v01(changed,source_bundle=source,profile=feedback.PREDICTIVE_SOURCE_PROFILE_ID)
    for field,new in (('predicted','true'),('claim_wall_ns','99999999999999999999'),('dependencies_sha256','0'*64)):
        supplied=json.loads(source.canonical);supplied['claim_artifact']['payload'][field]=new
        with pytest.raises(ValueError): feedback.PredictiveOutcomeSourceContextV01(feedback.canonical_json_bytes_v01(supplied))
    assert feedback.validate_outcome_feedback_against_sources_v01(value,source_bundle=source,profile='UNKNOWN_PROFILE')
    with pytest.raises(Exception): Draft202012Validator(schema).validate(dict(json.loads(value.canonical),unknown=True))
    assert not feedback.validate_outcome_feedback_against_sources_v01(value,source_bundle=source,profile=feedback.PREDICTIVE_SOURCE_PROFILE_ID)


def test_g34_durable_cas_late_correction_and_reopen(retained_stream,monkeypatch):
    import subprocess,sys,hashlib
    from hedgehog import outcome_feedback_history_v01 as history
    from hedgehog import outcome_feedback_consumer_v01 as consumer
    f=retained_stream;events_tuple=tuple(f['events']);now=max(json.loads(e.feedback_canonical)['timestamp'] for e in events_tuple)
    store=history.OutcomeHistoryV01(f['directory']/'cas_history',trusted_events=events_tuple)
    refs=[json.loads(e.feedback_canonical)['feedback_id'] for e in events_tuple]
    late,review=store.prepare_v01([refs[2]],expected_head=None,evaluated_at=now)
    competing,competing_review=store.prepare_v01([refs[1]],expected_head=None,evaluated_at=now)
    first=store.commit_v01(late,review,expected_head=None)
    old=(store.directory/'epochs'/(first['snapshot_id']+'.json')).read_bytes()
    with pytest.raises(ValueError,match='stale_predecessor'):store.commit_v01(competing,competing_review,expected_head=None)
    assert store.head_v01()==first
    next_value,next_review=store.prepare_v01(refs[:2],expected_head=first,evaluated_at=now)
    actual_replace=os.replace
    with monkeypatch.context() as m:
        m.setattr(os,'replace',lambda *args: (_ for _ in ()).throw(OSError('CONTROLLED_ATOMIC_HEAD_FAILURE')))
        with pytest.raises(OSError,match='CONTROLLED_ATOMIC_HEAD_FAILURE'):store.commit_v01(next_value,next_review,expected_head=first)
    assert os.replace is actual_replace and store.head_v01()==first
    assert not (store.directory/'HEAD.pending').exists()
    second=store.commit_v01(next_value,next_review,expected_head=first)
    oracle=cal.bounded_gt_event_fold_v01(events_tuple[:3],evaluated_at=now)
    assert next_value.to_plain_data()['fold']==oracle.to_plain_data()
    assert (store.directory/'epochs'/(first['snapshot_id']+'.json')).read_bytes()==old
    with pytest.raises(ValueError,match='independent_correction_required'):
        store.prepare_v01([refs[3]],expected_head=second,evaluated_at=now,corrections=((refs[0],refs[3],'Unrelated positive is not a correction.'),))
    corrected,corrected_review=store.prepare_v01([refs[3]],expected_head=second,evaluated_at=now)
    with pytest.raises(ValueError,match='write_review_substitution'):store.commit_v01(corrected,next_review,expected_head=second)
    third=store.commit_v01(corrected,corrected_review,expected_head=second)
    replacement=cal.bounded_gt_event_fold_v01(events_tuple[:4],evaluated_at=now)
    assert corrected.to_plain_data()['fold']==replacement.to_plain_data()
    repeated,repeated_review=store.prepare_v01([refs[3]],expected_head=third,evaluated_at=now)
    assert repeated.to_plain_data()['prior']['effective_count']==4
    assert repeated.to_plain_data()['fold']['history_observation_anchor']==corrected.to_plain_data()['fold']['history_observation_anchor']
    final=store.commit_v01(repeated,repeated_review,expected_head=third)
    code="""import json,sys
from pathlib import Path
from hedgehog import outcome_feedback_v01 as f,outcome_calibration_v01 as c,outcome_feedback_history_v01 as h
p=Path(sys.argv[1]);source=Path(sys.argv[2]);events=tuple(c.SourceBoundGTEventV01((source/f'{i}_feedback.json').read_bytes(),(source/f'{i}_source.json').read_bytes(),f.PREDICTIVE_SOURCE_PROFILE_ID) for i in range(1,8))
s=h.OutcomeHistoryV01(p/'cas_history',trusted_events=events)
print(json.dumps(s.head_v01(),sort_keys=True))
"""
    argv=[sys.executable,'-B','-c',code,str(f['directory']),str(f.get('retained_source_directory',f.get('native_directory',f['directory'])))];began=time.perf_counter()
    completed=subprocess.run(argv,capture_output=True)
    (f['directory']/'reopen_stdout.bin').write_bytes(completed.stdout);(f['directory']/'reopen_stderr.bin').write_bytes(completed.stderr)
    (f['directory']/'reopen_receipt.json').write_text(json.dumps(dict(argv=argv,rc=completed.returncode,seconds=time.perf_counter()-began,
        stdout_sha256=hashlib.sha256(completed.stdout).hexdigest(),stderr_sha256=hashlib.sha256(completed.stderr).hexdigest(),source_kind='INDEPENDENT_SAVED_NATIVE_SOURCE_ANCHORS_NOT_RESTORED_HOST')))
    assert completed.returncode==0,completed.stderr.decode()
    assert json.loads(completed.stdout)==final


def test_g34_current_supplied_poison_hardmask_and_time(current_repair):
    from dataclasses import replace
    from hedgehog import outcome_feedback_consumer_v01 as consumer
    f=current_repair;live=f['live']['fresh'];inputs=live['trusted_inputs'];projection=live['projection'];frozen=projection.canonical
    assert not consumer.validate_current_advisory_v01(replace(projection),**inputs)
    for field in ('adjusted_fp','prior_fp','score_micros'):
        data=projection.to_plain_data();data['rows'][0][field]+=1
        data['projection_id']=consumer.identity('advisory',{k:v for k,v in data.items() if k!='projection_id'})
        assert consumer.validate_current_advisory_v01(consumer.CurrentAdvisoryProjectionV01(consumer.canonical(data)),**inputs)
    opened=inputs['opened_history']
    poisoned=dict(opened,prior=dict(opened['prior'],prior_fp=cal.Q))
    with pytest.raises(ValueError):consumer.build_current_advisory_v01(**dict(inputs,opened_history=poisoned))
    ranking=f['live']['learned']['trusted_inputs'];a,b=ranking['candidates']
    masked,_=consumer.build_current_advisory_v01(**dict(ranking,candidates=(replace(a,ttl_valid=False),b)))
    assert masked.to_plain_data()['selected']==b.candidate_id
    assert next(r for r in masked.to_plain_data()['rows'] if r['candidate_id']==a.candidate_id)['eligible'] is False
    cold=f['live']['neutral']['trusted_inputs']
    tied,_=consumer.build_current_advisory_v01(**dict(cold,candidates=tuple(replace(x,base_viability_score=.67) for x in cold['candidates'])))
    assert tied.to_plain_data()['selected']=='g34:candidate:A'
    for field in ('policy_semantics_version','advisory_source_revision','route_family_id','domain_scope_id'):
        assert f['positive'].current_v01(history_key=dict(f['key'],**{field:'foreign'}),root=f['root'],transaction='g34r:negative:'+field,evaluation_time=f['now'])[0] is None
    value=f['positive'].read_v01(f['positive'].head_v01()['snapshot_id'])['snapshot']
    for when in (value['valid_to'],value['valid_from']-1):
        assert f['positive'].current_v01(history_key=f['key'],root=f['root'],transaction='g34r:out_of_time',evaluation_time=when)[0] is None
    assert projection.canonical==frozen and not consumer.validate_current_advisory_v01(projection,**inputs)
    prior=cal.fold_avf_history_prior_v01((f['stream'][0],)*256,evaluated_at=f['now'])
    assert prior.to_plain_data()['effective_count']==1
    with pytest.raises(ValueError):cal.fold_avf_history_prior_v01((f['stream'][0],)*257,evaluated_at=f['now'])


def test_g34_native_missing_expectation_no_update(predictive_stream):
    f=predictive_stream;session=f['session']
    spec=json.loads((ROOT/'fixtures/gate3_sentinel_observation_v01.json').read_bytes())
    tick=session.tick+1
    session.ingest([events.observation(v['sensor'],v['value'],tick,8,lineage='independent:'+v['sensor'])
        for v in session.fixture['frames']],tick)
    semantic=sem.collect(session.frames,session.fixture['maintenance_note'],session.root,session.source.sample().evaluation_time,
        controlled=spec['response'],intended_role=spec['role'],capabilities=session.capabilities.snapshot(spec['role']),
        observations=tuple(session.book.latest.values()),tick=tick,policy=session.contract)[1]
    capture=f['store'].observe_v01(semantic,expected_fp=None)
    source,observation,value=f['store'].feedback_v01(capture)
    event=cal.bind_outcome_feedback_event_v01(value,source_bundle=source,profile=feedback.PREDICTIVE_SOURCE_PROFILE_ID)
    assert json.loads(value.canonical)['update_eligibility']=='NO_UPDATE'
    now=int(time.time());original=tuple(f['events'][:3])
    before=cal.fold_avf_history_prior_v01(original,evaluated_at=now).to_plain_data()
    after=cal.fold_avf_history_prior_v01(original+(event,event),evaluated_at=now).to_plain_data()
    assert after['prior_fp']==before['prior_fp'] and after['effective_count']==before['effective_count'] and after['unresolved']==1
    a=cal.bounded_gt_event_fold_v01(original,evaluated_at=now).to_plain_data()
    b=cal.bounded_gt_event_fold_v01(original+(event,event),evaluated_at=now).to_plain_data()
    assert a['history_observation_anchor']==b['history_observation_anchor']
    for name,body in (('source',source.canonical),('observation',observation.canonical),('feedback',value.canonical)):
        (f['directory']/('missing_expectation_'+name+'.json')).write_bytes(body)


@pytest.mark.parametrize('field',['route_family_id','advice_claim_profile_id','advisory_source_revision','domain_scope_id','validation_profile_id','advisory_source_class'])
def test_g34r_exact_subject_no_trust_transfer(current_repair,field):
    from copy import deepcopy
    from hedgehog import outcome_feedback_consumer_v01 as con
    live=current_repair['live']['fresh'];inputs=live['trusted_inputs'];p=inputs['contract'].to_plain_data()
    claim=p['claims']['g34:candidate:A'];claim['subject'][field]='controlled:nonmatching'
    claim['claim_id']=con.identity('current_claim',{k:v for k,v in claim.items() if k!='claim_id'})
    check=p['checks']['g34:candidate:A'];check.update(target_claim_id=claim['claim_id'],target_subject=claim['subject'])
    check['check_id']=con.identity('bounded_check',{k:v for k,v in check.items() if k!='check_id'})
    p['contract_id']=con.identity('review_contract',{k:v for k,v in p.items() if k!='contract_id'})
    changed=con.CurrentReviewContractV01(con.canonical(p))
    if field=='domain_scope_id':
        with pytest.raises(ValueError,match='claim_scope'):con.build_current_advisory_v01(**dict(inputs,contract=changed))
        return
    projection,_=con.build_current_advisory_v01(**dict(inputs,contract=changed))
    assert projection.to_plain_data()['trust']['trust_status']=='COLD_START_NEUTRAL'
    assert projection.to_plain_data()['trust']['review_recommended'] is True
    assert live['projection'].to_plain_data()['trust']['trust_status']=='USABLE'


@pytest.mark.parametrize('variant',['root','transaction','time','context','source_revision','literal','proposal','proposal_time','proposal_parent'])
def test_g34r_pre_execution_context_and_literal(current_repair,variant):
    from dataclasses import replace
    from hedgehog import outcome_feedback_consumer_v01 as con
    from hedgehog.kernel import abi_v01 as abi,work_composition_v01 as work
    live=current_repair['live']['fresh'];before=(live['host'].revision,live['host'].work_attempts,live['host'].completed_work)
    args=dict(review=live['review'],projection=live['projection'],source_context=live['source'],semantic_proposal=live['proposal'],
        catalogue=live['catalogue'],host=live['host'],item=live['item'],material=live['material'],budget=work.WorkBudgetV01(1,0,0,1,0),
        task_id=live['program'].candidate.task_id,trusted_inputs=live['trusted_inputs'])
    if variant in ('root','transaction'):
        with pytest.raises(ValueError,match='review_current_scope'):
            con.review_current_advisory_v01(projection=live['projection'],trusted_inputs=live['trusted_inputs'],
                root='foreign:root' if variant=='root' else current_repair['root'],
                transaction='foreign:transaction' if variant=='transaction' else live['review'][1].transaction_id,
                candidate_materials=live['trusted_inputs']['contract'].to_plain_data()['claims'])
    else:
        if variant in ('time','context'):
            args['source_context']=replace(live['source'],**({'g2a_evaluation_time':current_repair['now']+1} if variant=='time' else {'g2a_evaluation_context_id':'foreign:context'}))
        elif variant=='source_revision':
            bsep=dict(live['source'].bsep_packet,packet_id='foreign:bsep')
            args['source_context']=replace(live['source'],bsep_packet=bsep)
        elif variant=='literal':
            binding=live['item'].inputs[0];record=replace(binding.source.value,value='{}')
            args['item']=replace(live['item'],inputs=(replace(binding,source=work.WorkLiteralV01(record)),))
        else:
            p=abi.kernel_artifact_to_plain_dict_v01(live['proposal'])
            if variant=='proposal':p['payload']['root_decision_ref']='foreign:decision'
            elif variant=='proposal_time':p['time_envelope']['pt_created_at']=feedback._utc(current_repair['now']-1)
            else:p['parent_refs']=p['parent_refs'][:-1]
            args['semantic_proposal']=abi.build_kernel_artifact_v01(**{k:tuple(v) if k in ('trace_refs','parent_refs') else v for k,v in p.items()})
        with pytest.raises(ValueError):con.execute_reviewed_pure_work_v01(**args)
    assert (live['host'].revision,live['host'].work_attempts,live['host'].completed_work)==before
    assert not con.validate_current_advisory_v01(live['projection'],**live['trusted_inputs'])


@pytest.mark.parametrize('variant',['unrelated_receipt','epoch','root','time','observations','material','self_label'])
def test_g34r_actual_receipt_contract(current_repair,variant):
    from copy import deepcopy
    from hedgehog import outcome_feedback_consumer_v01 as con
    f=current_repair;live=f['live']['aged'];receipt=f['receipts']['aged'];check=deepcopy(live['check_request'])
    before=(live['host'].work_attempts,live['host'].completed_work)
    if variant=='unrelated_receipt':receipt=f['receipts']['neutral']
    elif variant=='epoch':check['epoch']=None
    elif variant=='root':check['root']='foreign:root'
    elif variant=='time':check['evaluated_at']+=1
    elif variant=='observations':check['observation_refs']=['foreign:observation']
    elif variant=='material':check['material']['purpose']='channel'
    else:
        program,results,common,hosts=receipt
        from hedgehog.kernel import abi_v01 as abi
        p=abi.kernel_artifact_to_plain_dict_v01(common['semantic_proposal']);p['payload']['check_request']=check
        p['payload']['satisfies_obligation']='g34:required_current_check'
        p['payload']['check_request']['target_claim_id']='foreign:claim'
        proposal=abi.build_kernel_artifact_v01(**{k:tuple(v) if k in ('trace_refs','parent_refs') else v for k,v in p.items()})
        receipt=(program,results,dict(common,semantic_proposal=proposal),hosts)
        check['target_claim_id']='foreign:claim'
        check['check_id']=con.identity('bounded_check',{k:v for k,v in check.items() if k!='check_id'})
    check['check_id']=con.identity('bounded_check',{k:v for k,v in check.items() if k!='check_id'})
    with pytest.raises(ValueError):con.current_check_receipt_bridge_v01(check=check,receipt=receipt,current_bridge=live['trusted_inputs']['bridge'])
    assert (live['host'].work_attempts,live['host'].completed_work)==before
    assert con.current_check_receipt_bridge_v01(check=live['check_request'],receipt=f['receipts']['aged'],current_bridge=live['trusted_inputs']['bridge'])


@pytest.mark.parametrize('variant',['component','pointer','parent','transaction','numeric','native_missing','native_component','native_program'])
def test_g34r_causal_complete_bundle_controls(current_repair,variant):
    from dataclasses import replace
    from hedgehog.kernel import abi_v01 as abi
    from hedgehog import outcome_feedback_consumer_v01 as con
    live=current_repair['live']['fresh'];artifacts=live['artifacts'];refs=live['causal'];program=live['program']
    if variant=='component':refs=(replace(refs[0],consumer_component='wrong:consumer'),)+refs[1:]
    elif variant=='pointer':refs=(replace(refs[0],output_field='/payload/absent'),)+refs[1:]
    elif variant=='parent':artifacts=tuple(replace(a,parent_refs=()) if a.artifact_id==refs[0].downstream_artifact_id else a for a in artifacts)
    elif variant=='transaction':artifacts=(replace(artifacts[0],transaction_id='foreign:transaction'),)+artifacts[1:]
    elif variant=='native_missing':refs=tuple(r for r in refs if r not in program.source_bindings)
    elif variant=='native_component':refs=tuple(replace(r,consumer_component='work_composition') if r in program.source_bindings else r for r in refs)
    elif variant=='native_program':program=replace(program,source_bindings=())
    else:
        p=abi.kernel_artifact_to_plain_dict_v01(live['advisory']);p['payload']['advisory']['rows'][0]['prior_fp']+=1
        changed=abi.build_kernel_artifact_v01(**{k:tuple(v) if k in ('trace_refs','parent_refs') else v for k,v in p.items()})
        artifacts=tuple(changed if a.artifact_id==changed.artifact_id else a for a in artifacts)
    assert con.validate_current_causal_proof_v01(projection=live['projection'],trusted_inputs=live['trusted_inputs'],artifacts=artifacts,causal_refs=refs,program=program,common=live['common'])
    assert not con.validate_current_causal_proof_v01(projection=live['projection'],trusted_inputs=live['trusted_inputs'],artifacts=live['artifacts'],causal_refs=live['causal'],program=live['program'],common=live['common'])


@pytest.fixture(scope='module')
def actual_descent(current_repair):
    from hedgehog import drs_memory_resolution_v01 as memory
    f=current_repair;calls=[];real=memory.execute_local_memory_descent_v01
    def observe(**kwargs):
        calls.append(kwargs)
        return real(**kwargs)
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(memory,'execute_local_memory_descent_v01',observe)
        opened,evidence=f['positive'].current_v01(history_key=f['key'],root=f['root'],transaction='g34r:observed_open',evaluation_time=f['now'])
    assert len(calls)==1 and opened is not None
    audit=evidence['read_audit'][-5:]
    assert [v['stage'] for v in audit]==['DESCRIPTOR','ROOT_APPROVED','PAYLOAD_READ','PUBLIC_OPEN_VALIDATED','NUMERIC_SOURCE_VALIDATED']
    assert evidence['descent']['bytes_opened']==len(calls[0]['artifact_payloads'][0][1])>0
    (f['directory']/'exact_payload_open.json').write_text(json.dumps(evidence,sort_keys=True)+'\n')
    return calls[0],opened,evidence


@pytest.mark.parametrize('variant',['summary_only','budget_short','payload_hash','payload_length','absent_pointer','wrong_approved_artifact','refused_root'])
def test_g34r_public_descent_neighbors(current_repair,actual_descent,variant):
    import inspect
    from dataclasses import replace
    from hedgehog import drs_memory_resolution_v01 as memory,outcome_feedback_consumer_v01 as con
    from hedgehog.kernel import root_decision_v01 as roots
    from hedgehog.kernel.integrity_replay_v01 import domain_separated_sha256_hex_v01
    args=dict(actual_descent[0]);request=args['descent_request']
    def rebuild(builder,obj,**changes):return builder(**dict({k:getattr(obj,k) for k in inspect.signature(builder).parameters},**changes))
    if variant=='summary_only':
        args['descent_request']=rebuild(memory.build_memory_descent_request_v01,request,approved_descent_class='SUMMARY_ONLY',approved_artifact_pointer_ids=())
        args['artifact_payloads']=()
    elif variant=='budget_short':
        budget=rebuild(memory.build_memory_descent_budget_v01,request.approved_budget,max_bytes_opened=request.approved_budget.max_bytes_opened-1)
        args['descent_request']=rebuild(memory.build_memory_descent_request_v01,request,approved_budget=budget)
    elif variant in ('payload_hash','payload_length'):
        key,raw=args['artifact_payloads'][0]
        args['artifact_payloads']=((key,(b'!'+raw[1:]) if variant=='payload_hash' else raw+b' '),)
    elif variant=='absent_pointer':args['artifact_payloads']=()
    elif variant=='wrong_approved_artifact':
        args['descent_request']=rebuild(memory.build_memory_descent_request_v01,request,approved_artifact_pointer_ids=())
    else:
        plan=args['retrieval_plan'];review=con.ordinary_review_v01(root=current_repair['root'],transaction=plan.query_id,
            candidates={plan.retrieval_plan_id:memory.retrieval_plan_to_plain_data_v01(plan)},selected=plan.retrieval_plan_id,
            scores={plan.retrieval_plan_id:1000000},evidence_ref='g34r:refused',now=current_repair['now'],
            predicate='approve_controlled_memory_descent_plan_v01',subjects={plan.retrieval_plan_id:plan.semantic_address_id},required=('missing:source',))
        assert review[2].decision=='NEEDS_MORE_EVIDENCE'
        args.update(root_kernel=review[0],root_decision_input=review[1],root_decision_result=review[2])
        args['descent_request']=rebuild(memory.build_memory_descent_request_v01,request,root_kernel_id=review[0].kernel_id,
            root_decision_input_id=review[1].decision_input_id,root_decision_id=review[2].decision_id,
            root_decision_hash=domain_separated_sha256_hex_v01(domain='hedgehog:drs:memory_descent_root_result_binding:v01',
                payload=con.canonical(roots.root_decision_result_to_plain_dict_v01(review[2]))))
    try:
        result=memory.execute_local_memory_descent_v01(**args)
    except ValueError as error:
        assert variant!='summary_only',str(error)
    else:
        if variant=='summary_only':assert result.bytes_opened==0 and not result.opened_artifact_pointer_ids
        else:assert result.reason_codes or not result.limits_respected
        opened=dict(actual_descent[1],descent=memory.memory_descent_result_to_plain_data_v01(result))
        with pytest.raises(ValueError):current_repair['positive'].validate_opened_v01(opened,bridge=opened['bridge'],evaluation_time=current_repair['now'])
    assert current_repair['positive'].validate_opened_v01(actual_descent[1],bridge=actual_descent[1]['bridge'],evaluation_time=current_repair['now'])==()


@pytest.mark.parametrize('variant',['foreign_policy','missing_pointer','changed_body','changed_payload','stale_head'])
def test_g34r_application_open_boundaries(current_repair,tmp_path,variant):
    import hashlib,inspect,shutil
    from hedgehog import outcome_feedback_history_v01 as history,drs_semantic_address_v01 as address,outcome_feedback_consumer_v01 as con
    f=current_repair;shutil.copytree(f['positive'].directory,tmp_path/'history')
    store=history.OutcomeHistoryV01(tmp_path/'history',trusted_events=f['stream']);head=store.head_v01()
    opened,_=store.current_v01(history_key=f['key'],root=f['root'],transaction='g34r:boundary_before',evaluation_time=f['now'])
    if variant in ('foreign_policy','missing_pointer'):
        descriptor,meaning=store._descriptor(head);pointer=meaning.artifact_pointers[0]
        if variant=='foreign_policy':
            pointer=address.build_artifact_pointer_v01(**dict({k:getattr(pointer,k) for k in inspect.signature(address.build_artifact_pointer_v01).parameters},access_policy_id='foreign:policy'))
        changed=address.build_meaning_record_v01(**dict({k:getattr(meaning,k) for k in inspect.signature(address.build_meaning_record_v01).parameters},
            artifact_pointers=(pointer,) if variant=='foreign_policy' else ()))
        descriptor['meaning']=address.meaning_record_to_plain_data_v01(changed)
        raw=con.canonical(descriptor);(store.directory/'epochs'/(head['snapshot_id']+'.descriptor.json')).write_bytes(raw)
        # Coherent descriptor/MeaningRecord identity. Fail the explicit local pointer rule,
        # rather than treating an identity mismatch as the access-policy test.
        altered_head=dict(head,record_id=changed.meaning_record_id,descriptor_sha256=hashlib.sha256(raw).hexdigest())
        actual=store._descriptor(altered_head)[1]
        assert address.validate_meaning_record_v01(actual)[0]
        if variant=='foreign_policy':assert actual.artifact_pointers[0].access_policy_id!='g34:history_context_read:v01'
        else:assert not actual.artifact_pointers
        with pytest.raises(ValueError,match='payload_pointer_scope' if variant=='foreign_policy' else 'payload_pointer_required'):
            store.current_descriptor_v01(altered_head,history_key=f['key'])
        # The current open token cannot be replaced by this other valid descriptor.
        (store.directory/'HEAD.json').write_bytes(con.canonical(altered_head))
        with pytest.raises(ValueError):store.validate_opened_v01(opened,bridge=opened['bridge'],evaluation_time=f['now'])
    elif variant=='stale_head':
        snapshot,review=store.prepare_v01([json.loads(f['stream'][3].feedback_canonical)['feedback_id']],expected_head=head,evaluated_at=f['now'])
        store.commit_v01(snapshot,review,expected_head=head)
        with pytest.raises(ValueError,match='head_changed'):store.validate_opened_v01(opened,bridge=opened['bridge'],evaluation_time=f['now'])
    else:
        path=store.directory/'epochs'/(head['snapshot_id']+('.json' if variant=='changed_body' else '.payload.json'))
        raw=path.read_bytes();path.write_bytes(raw+b' ')
        with pytest.raises(ValueError):store.current_v01(history_key=f['key'],root=f['root'],transaction='g34r:poisoned',evaluation_time=f['now'])
        path.write_bytes(raw)
        assert store.current_v01(history_key=f['key'],root=f['root'],transaction='g34r:restored',evaluation_time=f['now'])[0] is not None


def test_g34r_no_offered_check_and_no_role_flag_bypass(current_repair):
    from hedgehog import outcome_feedback_consumer_v01 as con
    live=current_repair['live']['aged'];inputs=live['trusted_inputs'];p=inputs['contract'].to_plain_data()
    p['checks']={k:None for k in p['claims']}
    p['contract_id']=con.identity('review_contract',{k:v for k,v in p.items() if k!='contract_id'})
    contract=con.CurrentReviewContractV01(con.canonical(p));changed=dict(inputs,contract=contract)
    projection,_=con.build_current_advisory_v01(**changed)
    review=con.review_current_advisory_v01(projection=projection,trusted_inputs=changed,root=p['context']['root'],transaction=p['context']['transaction'],candidate_materials=p['claims'])
    assert review[2].decision=='NEEDS_MORE_EVIDENCE'
    claim=con.review_to_plain_v01(review)['input']['root_review_packet']['synthesis_proposal']['normalized_claims'][0]['object_or_value']
    assert claim['review_requirement']==dict(recommended=True,offered=False,check_ref=None)
    p['role']='EVIDENCE_CHECK';p['contract_id']=con.identity('review_contract',{k:v for k,v in p.items() if k!='contract_id'})
    with pytest.raises(ValueError):con.CurrentReviewContractV01(con.canonical(p)).to_plain_data()


def test_g34r_expired_history_remains_review_needed(current_repair):
    f=current_repair;store=f['positive'];snapshot=store.read_v01(store.head_v01()['snapshot_id'])['snapshot']
    value,live=f['time_context'].evaluate_v01(store=store,history_key=f['key'],now=snapshot['valid_to'],invocation='g34r:expired_current')
    assert value['projection']['history_ref'] is None and value['projection']['rows'][0]['prior_fp']==0
    assert value['projection']['trust']['review_recommended'] and value['review']['result']['decision']=='NEEDS_MORE_EVIDENCE'
    assert not live['host'].work_attempts and not live['host'].completed_work and value['work'] is None


def test_g34r_low_prior_allows_lawful_extra_review(current_repair):
    f=current_repair;context=f['time_context'];now=f['now']
    waiting,live=context.evaluate_v01(store=f['negative'],history_key=f['key'],now=now,invocation='g34r:low_prior')
    assert waiting['projection']['rows'][0]['prior_fp']<0 and waiting['work'] is None and not live['host'].work_attempts
    check,done=context.evaluate_check_v01(request=live['check_request'],now=now,invocation='g34r:low_prior:check')
    accepted,actual=context.evaluate_v01(store=f['negative'],history_key=f['key'],now=now,invocation='g34r:low_prior:continue',
        additional_receipt=(done['program'],done['results'],done['common'],{f['root']:done['host']}))
    assert accepted['review']['result']['decision']=='ACCEPT' and accepted['work']['operation']=='sentinel.diagnostic.v01'
    (f['directory']/'low_prior_continuation.json').write_text(json.dumps(dict(waiting=waiting,check=check,accepted=accepted),sort_keys=True)+'\n')


def test_g34r_refused_root_reads_no_payload(current_repair,monkeypatch):
    from hedgehog import outcome_feedback_consumer_v01 as con
    f=current_repair;store=f['positive'];start=len(store.read_audit);real=con.ordinary_review_v01
    reviews=[]
    def require_missing_evidence(**kwargs):
        assert kwargs['predicate']=='approve_controlled_memory_descent_plan_v01'
        review=real(**dict(kwargs,required=('controlled:absent_approval_evidence',)))
        reviews.append(con.review_to_plain_v01(review));return review
    with monkeypatch.context() as patch:
        patch.setattr(con,'ordinary_review_v01',require_missing_evidence)
        with pytest.raises(ValueError,match='payload_root_refusal'):
            store.current_v01(history_key=f['key'],root=f['root'],transaction='g34r:root_refused',evaluation_time=f['now'])
    assert reviews[0]['result']['decision']=='NEEDS_MORE_EVIDENCE'
    assert [v['stage'] for v in store.read_audit[start:]]==['DESCRIPTOR']
    (f['directory']/'refused_root_no_payload.json').write_text(json.dumps(dict(review=reviews[0],reads=store.read_audit[start:]),sort_keys=True)+'\n')


@pytest.mark.parametrize('field,value',[('snapshot_id','../foreign'),('body_sha256',True),('descriptor_sha256','bad'),('record_id','')])
def test_g34r_descriptor_reference_shape_before_read(current_repair,field,value):
    store=current_repair['positive'];head=dict(store.head_v01(),**{field:value});audit=list(store.read_audit)
    with pytest.raises(ValueError,match='head_fields'):store.current_descriptor_v01(head,history_key=current_repair['key'])
    assert store.read_audit==audit
