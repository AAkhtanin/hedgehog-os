"""One native bounded episode, independent consumers, and external DRS genesis."""
from copy import deepcopy
from dataclasses import replace
import json
import os
from pathlib import Path
import time

import pytest
from jsonschema import Draft202012Validator
from hedgehog import outcome_feedback_v01 as g3
from hedgehog import outcome_feedback_history_v01 as history
from hedgehog.domains.landslide_sentinel import contracts_v01 as c, events_v01 as events
from hedgehog.domains.landslide_sentinel import semantic_adapter_v01 as sem, kernel_adapter_v01 as kernel
from hedgehog.domains.landslide_sentinel.monitoring_runtime_v01 import ControlledEpisode
from hedgehog.domains.landslide_sentinel.outcome_feedback_adapter_v01 import SentinelOutcomeSourceV01
from hedgehog.domains.landslide_sentinel.evidence_v01 import plain
from hedgehog.kernel import abi_v01 as abi, root_decision_v01 as roots

ROOT=Path(__file__).resolve().parents[1]


def save(directory,name,value):
    (directory/name).write_bytes(c.canonical(plain(value))+b'\n')


@pytest.fixture(scope='module')
def native_observation(tmp_path_factory):
    directory=Path(os.environ['G32_EVIDENCE'])/'commands'/os.environ['G32_COMMAND']/'native' if 'G32_EVIDENCE' in os.environ else tmp_path_factory.mktemp('g32_native')/'native'
    directory.mkdir(parents=True,exist_ok=False)
    fixture=json.loads((ROOT/'fixtures/landslide_sentinel/ls1_inputs_v01.json').read_bytes())
    spec=json.loads((ROOT/'fixtures/gate3_sentinel_observation_v01.json').read_bytes())
    timings={}
    def timed(name,fn):
        started=time.perf_counter()
        with (directory/'stages.jsonl').open('a') as stream:stream.write(json.dumps({'phase':name,'event':'START'})+'\n')
        value=fn();timings[name]=time.perf_counter()-started
        with (directory/'stages.jsonl').open('a') as stream:stream.write(json.dumps({'phase':name,'event':'RETURN','seconds':timings[name]})+'\n')
        return value
    session=timed('bootstrap',lambda:ControlledEpisode(directory/'episode',fixture))
    session.ingest([events.observation(v['sensor'],v['value'],120,1) for v in fixture['frames']],120)
    store=SentinelOutcomeSourceV01(session)
    def semantic(root):
        return sem.collect(session.frames,fixture['maintenance_note'],root,session.source.sample().evaluation_time,
            controlled=spec['response'],intended_role=spec['role'],capabilities=session.capabilities.snapshot(spec['role']),
            observations=tuple(session.book.latest.values()),tick=session.tick,policy=session.contract)[1]
    refused=timed('early_semantic_refusal',lambda:store.observe_role_v01(semantic('root:g32:foreign'),expected_fp=g3.Q))
    healthy=timed('healthy_native_work',lambda:store.observe_role_v01(semantic(session.root),expected_fp=g3.Q))
    unknown=timed('lawful_neighbor_missing_expectation',lambda:store.observe_role_v01(semantic(session.root),expected_fp=None))
    captures={'healthy':healthy,'refused':refused,'unknown':unknown}
    feedback={};observations={}
    for name,capture in captures.items():
        observations[name],feedback[name]=timed(name+'_normalization',lambda capture=capture:store.build_feedback_v01(capture))
        save(directory,name+'_native.json',json.loads(capture.native_canonical))
        save(directory,name+'_source.json',json.loads(capture.source_canonical))
        save(directory,name+'_observation.json',json.loads(observations[name].canonical))
        save(directory,name+'_feedback.json',g3.outcome_feedback_to_plain_data_v01(feedback[name]))
    basis=store.native_basis_v01(healthy)
    proof=history.NativeOutcomeWorkProofV01(store.validate_capture_v01(healthy),basis.host,basis.program,basis.results,
        basis.common,basis.review_bindings,basis.material,basis.review)
    review=timed('fresh_recording_root_review',lambda:history.review_outcome_recording_v01(feedback['healthy'],native_proof=proof))
    save(directory,'recording_review.json',dict(candidate=json.loads(review.candidate_canonical),
        kernel=roots.root_decision_kernel_to_plain_dict_v01(review.kernel),
        decision_input=roots.root_decision_input_to_plain_dict_v01(review.decision_input),
        decision_result=roots.root_decision_result_to_plain_dict_v01(review.decision_result)))
    db=history.OutcomeHistoryGenesisV01(directory/'history')
    value=g3.outcome_feedback_to_plain_data_v01(feedback['healthy'])
    query_args=dict(subject=value['advisory_subject_key'],history_key=value['avf_history_key'],as_of=value['timestamp'])
    cold=timed('cold_query',lambda:db.query_v01(**query_args));save(directory,'cold_query.json',cold)
    record=timed('root_reviewed_write_readback',lambda:db.record_v01(feedback['healthy'],native_proof=proof,review=review))
    found=timed('semantic_rediscovery',lambda:db.query_v01(**query_args));save(directory,'rediscovery.json',found)
    save(directory,'record.json',record);save(directory,'timings.json',timings)
    yield dict(directory=directory,session=session,store=store,captures=captures,feedback=feedback,observations=observations,
        proof=proof,review=review,db=db,cold=cold,found=found,query_args=query_args,record=record)
    assert not session.executed
    save(directory,'finalizer.json',dict(complete=True,effect_executions=len(session.executed),trusted_source_reads=session.source.reads,
        role_attempts=3,role_results=len(session.role_results),timings=timings,full_D_E='NOT_RUN',provider_calls=0))


def test_g32_native_work_feedback_schema_and_abi(native_observation):
    f=native_observation;capture=f['captures']['healthy'];value=f['feedback']['healthy'];store=f['store']
    assert not store.validate_feedback_v01(value,capture=capture)
    data=g3.outcome_feedback_to_plain_data_v01(value)
    assert data['proposal_assessment']=='CORRECT' and data['task_outcome']=='COMPLETED'
    assert data['enforcement_outcome']=='ALLOWED_AS_REQUIRED' and data['update_eligibility']=='ELIGIBLE'
    assert data['root_decision_ref']['state']=='KNOWN' and data['action_packet_ref']['state']=='NOT_APPLICABLE'
    assert data['actual_cost']['work_invocations']['value']>0
    assert data['actual_cost']['model_calls']['value']==0
    Draft202012Validator(json.loads((ROOT/'schemas/outcome_feedback_v01.schema.json').read_bytes())).validate(data)
    source=store.validate_capture_v01(capture)
    artifact=g3.project_outcome_feedback_evidence_v01(value,source_bundle=source,profile=g3.NATIVE_SOURCE_PROFILE_ID,
        current_abi_context=dict(artifact_id='g32:evidence:'+data['feedback_id'],transaction_id=data['transaction_id'],owner_root_id=data['local_root_scope_id'],parent_refs=[],time_envelope=data['time_envelope']))
    assert not abi.validate_kernel_artifact_bundle_v01(artifacts=(artifact,))
    save(f['directory'],'feedback_abi.json',abi.kernel_artifact_to_plain_dict_v01(artifact))
    native=json.loads(capture.native_canonical);basis=store.native_basis_v01(capture)
    assert f['session'].reviewed_role_result(basis.artifact.artifact_id) is basis
    assert kernel.validate_reviewed_work(f['session'],basis)==native['record']['output']
    assert int(native['claim']['wall_ns'])<=int(native['event_wall_ns'])<=int(native['capture_wall_ns'])
    assert data['time_envelope']==native['record']['work_artifact']['time_envelope']
    assert data['event_time']==int(native['event_wall_ns'])//10**9 and native['scenario_tick']==120


def test_g32_early_refusal_and_unknown_neighbor(native_observation):
    f=native_observation
    early=g3.outcome_feedback_to_plain_data_v01(f['feedback']['refused'])
    actual=json.loads(f['captures']['refused'].native_canonical)
    assert actual['reason']=='role_current_root_policy' and actual['record'] is None
    assert early['root_decision_ref']['state']==early['action_packet_ref']['state']=='NOT_REACHED'
    assert early['enforcement_outcome']=='BLOCKED_AS_REQUIRED' and early['proposal_assessment']=='NOT_SCORABLE'
    assert early['actual_cost']['work_invocations']['value']==0
    unknown=g3.outcome_feedback_to_plain_data_v01(f['feedback']['unknown'])
    assert unknown['task_outcome']=='COMPLETED' and unknown['pre_decision_expectation']['state']=='UNKNOWN'
    assert unknown['proposal_assessment']=='NOT_SCORABLE' and unknown['update_eligibility']=='NO_UPDATE'
    assert not f['store'].validate_feedback_v01(f['feedback']['unknown'],capture=f['captures']['unknown'])


def _rehash(data):
    data['feedback_id']=g3._identity('g3_feedback_v01',{k:v for k,v in data.items() if k!='feedback_id'})
    return g3.parse_outcome_feedback_json_v01(g3._canonical(data))


@pytest.mark.parametrize('field',('local_root_scope_id','transaction_id','strategy_candidate_id','context_fingerprint','source_closure_ref','advice_claim_profile_id','task_outcome','proposal_assessment'))
def test_g32_coherent_feedback_poison_refused(native_observation,field):
    f=native_observation;value=f['feedback']['healthy'];data=g3.outcome_feedback_to_plain_data_v01(value)
    data[field]='FAILED' if field=='task_outcome' else 'UNSAFE' if field=='proposal_assessment' else '0'*64 if field=='context_fingerprint' else 'coherent:foreign'
    poisoned=_rehash(data)
    assert not g3.validate_outcome_feedback_structure_v01(poisoned)
    assert f['store'].validate_feedback_v01(poisoned,capture=f['captures']['healthy'])==('g31_feedback_source_mismatch',)


@pytest.mark.parametrize('group,field',(('context','local_root_scope_id'),('context','transaction_id'),('proposal','operation'),('policy','revision'),('context','capability_contract_version'),('expectation','source_id'),('native','output_sha256')))
def test_g32_coherent_supplied_source_poison_refused(native_observation,group,field):
    f=native_observation;capture=f['captures']['healthy'];source=json.loads(capture.source_canonical)
    source[group][field]='coherent:foreign'
    assert f['store'].validate_feedback_v01(f['feedback']['healthy'],capture=capture,supplied_source=source)==('g32_supplied_source_changed',)
    save(f['directory'],'source_poison_'+group+'_'+field+'.json',dict(source=source,reason='g32_supplied_source_changed'))


def test_g32_origin_copy_and_container_isolation(native_observation):
    f=native_observation;store=f['store'];capture=f['captures']['healthy'];value=f['feedback']['healthy']
    assert not store.validate_feedback_v01(value,capture=replace(capture))
    for altered in (replace(capture,_origin=object()),replace(capture,ordinal=capture.ordinal+1),replace(capture,source_canonical=capture.source_canonical+b' ')):
        assert store.validate_feedback_v01(value,capture=altered)
    detached=g3.outcome_feedback_to_plain_data_v01(value);detached['actual_cost']['model_calls']['value']=100
    assert g3.outcome_feedback_to_plain_data_v01(value)['actual_cost']['model_calls']['value']==0
    early=f['captures']['refused'];summary=json.loads(early.source_canonical);summary['native']['root_decision_ref']='invented:result'
    assert store.validate_feedback_v01(f['feedback']['refused'],capture=early,supplied_source=summary)
    assert not store.validate_feedback_v01(value,capture=capture)


def test_g32_native_currentness_and_historical_evidence(native_observation):
    f=native_observation;store=f['store'];session=f['session'];capture=f['captures']['healthy'];basis=store.native_basis_v01(capture)
    with pytest.raises(ValueError,match='reviewed_work_host'):
        kernel.validate_reviewed_work(session,replace(basis,host=object()))
    old=deepcopy(session.contract);before=capture.native_canonical;reads=session.source.reads
    try:
        session.contract['g32_control_revision']='changed'
        with pytest.raises(ValueError,match='reviewed_work_current_dependencies'):store.validate_capture_v01(capture)
        assert store.validate_capture_v01(capture,require_current=False).canonical==capture.source_canonical
        assert session.source.reads==reads and capture.native_canonical==before
    finally:
        session.contract.clear();session.contract.update(old)
    assert not store.validate_feedback_v01(f['feedback']['healthy'],capture=capture)


def test_g32_genesis_cold_root_review_readback_and_search(native_observation):
    f=native_observation;value=f['feedback']['healthy'];proof=f['proof'];review=f['review']
    assert not f['cold'][1].candidates
    assert review.decision_result.decision=='ACCEPT' and review.decision_result.decision_id!=proof.review[2].decision_id
    candidates=f['found'][1].candidates
    assert any(row.record_id==f['record']['record_id'] for row in candidates)
    assert all(row.review_required and not row.direct_reuse_allowed and not row.action_permission_granted for row in candidates)
    assert f['db'].record_v01(value,native_proof=proof,review=review)==f['record']
    assert len(list((f['db'].directory/'drs'/'work').glob('*.json')))==1
    unrelated=history.OutcomeRecordingReviewV01(review.candidate_canonical,*proof.review)
    with pytest.raises(ValueError,match='g32_record_root_scope'):f['db'].record_v01(value,native_proof=proof,review=unrelated)
    with pytest.raises(ValueError):history.validate_recording_review_v01(value,native_proof=replace(proof,host=object()),review=review)


@pytest.mark.parametrize('target',('payload','record','root','policy','context'))
def test_g32_history_poison_and_lawful_rediscovery(native_observation,target):
    f=native_observation;db=f['db'];value=f['feedback']['healthy'];proof=f['proof'];review=f['review']
    if target in ('payload','record'):
        path=db.directory/'evidence'/'feedback.json' if target=='payload' else db.directory/'drs'/'work'/(f['record']['record_id']+'.json')
        old=path.read_bytes()
        try:
            data=json.loads(old)
            if target=='payload':
                data['task_outcome']='FAILED';path.write_bytes(_rehash(data).canonical)
            else:
                data['content']['source_sha256']='f'*64;path.write_bytes(c.canonical(data))
            with pytest.raises(ValueError,match='g32_persisted_'):db.readback_v01(value,native_proof=proof,review=review)
        finally:path.write_bytes(old)
    else:
        supplied=json.loads(proof.source.canonical)
        field={'root':'local_root_scope_id','policy':'policy_semantics_version','context':'transaction_id'}[target]
        supplied['context'][field]='coherent:foreign'
        with pytest.raises((ValueError,KeyError,AttributeError)):
            db.readback_v01(value,native_proof=replace(proof,source=g3.NativeOutcomeSourceContextV01(g3._canonical(supplied))),review=review)
    assert db.readback_v01(value,native_proof=proof,review=review)==f['record']
    assert any(row.record_id==f['record']['record_id'] for row in db.query_v01(**f['query_args'])[1].candidates)


def test_g32_fully_rebuilt_source_report_not_recording_authority(native_observation):
    f=native_observation;source=json.loads(f['proof'].source.canonical)
    source['context']['policy_semantics_version']=source['policy']['revision']='coherent:other-policy'
    source['policy']['source_id']='coherent:other-policy'
    changed=g3.NativeOutcomeSourceContextV01(g3._canonical(source))
    data=g3.outcome_feedback_to_plain_data_v01(f['feedback']['healthy'])
    observation=g3.build_outcome_observation_v01(source_bundle=changed,profile=g3.NATIVE_SOURCE_PROFILE_ID,
        explicit_times={k:data[k] for k in ('ingested_time','evaluated_at','timestamp')})
    forged=g3.build_outcome_feedback_v01(observation=observation,source_bundle=changed,profile=g3.NATIVE_SOURCE_PROFILE_ID)
    assert not g3.validate_outcome_feedback_against_sources_v01(forged,source_bundle=changed,profile=g3.NATIVE_SOURCE_PROFILE_ID)
    assert f['store'].validate_feedback_v01(forged,capture=f['captures']['healthy'],supplied_source=source)==('g32_supplied_source_changed',)
    with pytest.raises(ValueError,match='g32_genesis_feedback'):
        history.review_outcome_recording_v01(forged,native_proof=f['proof'])
    assert f['db'].readback_v01(f['feedback']['healthy'],native_proof=f['proof'],review=f['review'])==f['record']
    other=deepcopy(f['query_args']);other['subject']['local_root_scope_id']='root:other'
    assert not f['db'].query_v01(**other)[1].candidates


def test_g32_future_supplied_evidence_is_not_current(native_observation):
    f=native_observation;capture=f['captures']['healthy'];source=f['store'].validate_capture_v01(capture)
    future=int(time.time())+3600
    observation=g3.build_outcome_observation_v01(source_bundle=source,profile=g3.NATIVE_SOURCE_PROFILE_ID,
        explicit_times=dict(ingested_time=future,evaluated_at=future,timestamp=future))
    value=g3.build_outcome_feedback_v01(observation=observation,source_bundle=source,profile=g3.NATIVE_SOURCE_PROFILE_ID)
    assert f['store'].validate_feedback_v01(value,capture=capture)==('g32_future_evidence_time',)
    with pytest.raises(ValueError,match='g32_genesis_future_evidence'):
        history.review_outcome_recording_v01(value,native_proof=f['proof'])
    assert not f['store'].validate_feedback_v01(f['feedback']['healthy'],capture=capture)


def test_g32_raw_order_same_second_and_ingest_binding(native_observation):
    f=native_observation;source=json.loads(f['captures']['healthy'].source_canonical)
    # Structural source-contract controls only, not invented native authority.
    epoch=source['observation']['event_time']
    source['native'].update(claim_wall_ns=str(epoch*10**9+1),event_wall_ns=str(epoch*10**9+2),capture_wall_ns=str(epoch*10**9+3))
    source['proposal']['created_at']=source['expectation']['created_at']=epoch
    context=g3.NativeOutcomeSourceContextV01(g3._canonical(source))
    assert g3.build_outcome_observation_v01(source_bundle=context,profile=g3.NATIVE_SOURCE_PROFILE_ID,
        explicit_times=dict(ingested_time=epoch,evaluated_at=epoch,timestamp=epoch))
    source['native']['capture_wall_ns']=str((epoch+1)*10**9)
    context=g3.NativeOutcomeSourceContextV01(g3._canonical(source))
    with pytest.raises(ValueError,match='g32_ingest_before_capture'):
        g3.build_outcome_observation_v01(source_bundle=context,profile=g3.NATIVE_SOURCE_PROFILE_ID,
            explicit_times=dict(ingested_time=epoch,evaluated_at=epoch,timestamp=epoch))
