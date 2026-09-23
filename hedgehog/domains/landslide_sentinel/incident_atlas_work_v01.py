"""Existing Sentinel prediction/history/current Work, with exact downstream binding."""
import json
import time
from pathlib import Path
from hedgehog import outcome_feedback_v01 as f, outcome_calibration_v01 as cal
from hedgehog import outcome_feedback_history_v01 as h, outcome_feedback_consumer_v01 as con
from hedgehog.kernel import work_composition_v01 as w, abi_v01 as abi
from hedgehog.incident_atlas_history_v01 import storage_projection_v01
from .outcome_feedback_adapter_v01 import SentinelPredictiveSourceV01, G34ControlledCurrentWorkV01
from . import contracts_v01 as c, capability_registry_v01 as caps, kernel_adapter_v01 as k
from .incident_atlas_source_v01 import work_record_v01
from .evidence_v01 import save

SCORES=('0.70','0.69')


def experience_v01(session, semantic):
    directory=session.directory/'atlas_history';directory.mkdir()
    save(directory/'predeclared_scores.json',dict(scores=SCORES,predicted=True,expected_fp=cal.Q//2))
    store=SentinelPredictiveSourceV01(session)
    capture=store.observe_v01(semantic,predicted=True,expected_fp=cal.Q//2)
    source,observation,feedback=store.feedback_v01(capture)
    source_data=json.loads(source.canonical)
    basis=session.reviewed_role_result(source_data['result_artifact']['artifact_id'])
    native=f.NativeOutcomeSourceContextV01(c.canonical(source_data['native_source']))
    proof=h.NativeOutcomeWorkProofV01(source=native,host=session.host,program=basis.program,results=basis.results,
        common=basis.common,review_bindings=basis.review_bindings,material=basis.material,review=basis.review)
    h.validate_native_work_proof_v01(proof)
    event=cal.bind_outcome_feedback_event_v01(feedback,source_bundle=source,profile=f.PREDICTIVE_SOURCE_PROFILE_ID)
    history=h.OutcomeHistoryV01(directory/'store',trusted_events=(event,))
    now=int(time.time())
    snapshot,review=history.prepare_v01((json.loads(feedback.canonical)['feedback_id'],),expected_head=None,evaluated_at=now)
    head=history.commit_v01(snapshot,review,expected_head=None)
    key=snapshot.to_plain_data()['prior']['history_key']
    material=json.loads(basis.material)
    check=dict(records=material['checks'][0]['observations'],tick=session.tick,site=session.fixture['site'],policy=session.contract,purpose='local')
    materials=[dict(candidate_id='atlas:sentinel:diagnostic',operation='sentinel.diagnostic.v01',base_score=SCORES[0],material=material),
        dict(candidate_id='atlas:sentinel:observability',operation='sentinel.observability.v01',base_score=SCORES[1],material=check)]
    context=G34ControlledCurrentWorkV01(root=session.root,frames=session.frames,reference_note=session.fixture['reference_note'],
        materials=materials,valid_from=now,valid_to=now+3600)
    values={};lives={}
    for name,current_store in (('before',None),('after',history)):
        values[name+'_initial'],lives[name+'_initial']=context.evaluate_v01(store=current_store,history_key=key,now=now,invocation='atlas:sentinel:'+name)
        initial=lives[name+'_initial']
        c.require(values[name+'_initial']['review']['result']['decision']=='NEEDS_MORE_EVIDENCE','atlas_sentinel_required_check')
        values[name+'_check'],extra=context.evaluate_check_v01(request=initial['check_request'],now=now,invocation='atlas:sentinel:'+name+':check')
        receipt=(extra['program'],extra['results'],extra['common'],{session.root:extra['host']})
        values[name],lives[name]=context.evaluate_v01(store=current_store,history_key=key,now=now,
            invocation='atlas:sentinel:'+name+':completed',additional_receipt=receipt)
        for label,live in ((name+'_check',extra),(name,lives[name])):
            values[label]['typed_work']=work_record_v01(live['program'],live['results'],live['artifact'],live['catalogue'])
    c.require(values['before']['projection']['selected']!=values['after']['projection']['selected'],'atlas_sentinel_history_did_not_change_work')
    record=dict(source=source_data,observation=json.loads(observation.canonical),feedback=json.loads(feedback.canonical),
        native=json.loads((session.directory/'g34_native_1.json').read_bytes()),
        native_work=work_record_v01(basis.program,basis.results,basis.artifact,session.catalogue),
        native_review=[f.g35_record_to_plain_v01(v) for v in basis.review],live_native_proof='VALIDATED',
        snapshot=snapshot.to_plain_data(),head=head,recording_review=f.g35_record_to_plain_v01(review),
        storage=storage_projection_v01(directory/'store',(snapshot.to_plain_data(),)),materials=materials,values=values,
        root=session.root,source_window=[now,now+3600],feedback_samples=1,new_provider_calls=0)
    save(directory/'experience.json',record)
    return record,lives


def consume_v01(session, selected, live):
    """Consume exact selected current output; do not borrow another Work's authority."""
    c.require(selected['projection']['selected']=='atlas:sentinel:observability'
        and selected['work']['operation']=='sentinel.observability.v01','atlas_sentinel_selected_operation')
    actual=live['artifact']
    c.require(selected['work']['artifact']==abi.kernel_artifact_to_plain_dict_v01(actual),'atlas_sentinel_selected_result')
    ok,reasons=w.validate_work_program_result_v01(live['program'],live['results'],**live['common'],host_map={session.root:live['host']})
    c.require(ok,'atlas_sentinel_selected_native:'+repr(reasons))
    material=json.loads(caps.values(live['results'][0].invocation.inputs)['material'])
    expected=dict(records=sorted((v for v in session.book.latest.values() if v['channel'] in ('displacement','reserve')),
        key=lambda v:v['observation_id']),tick=session.tick,site=session.fixture['site'],policy=session.contract,purpose='local')
    c.require(material==expected and live['material']==expected and actual.owner_root_id==session.root,
        'atlas_sentinel_current_consumption_context')
    output=json.loads(caps.values(live['results'][0].result.output)['material'])
    c.require(output==selected['work']['output']==c.observability(material),'atlas_sentinel_consumed_output')
    claim=dict(selected_result_ref=actual.artifact_id,current_input_sha256=c.digest(material),
        policy_sha256=c.digest(session.contract),calibration=session.contract['calibration'],source_ids=output['source_ids'],output=output,
        continuation='RETAIN_INSUFFICIENT_SUPPORT_AND_REQUIRE_NEW_INDEPENDENT_MEASUREMENTS')
    review=k.root_review(session.root,'transaction:'+session.id,c.identity('atlas_consumed_observability',claim),session.id,
        dict(exact_result=True,current_material=output['input_sha256']==c.digest(material)),actual.artifact_id,
        live['program'].candidate.bsep_ref,live['program'].topology_artifact.artifact_id,session.source.sample().evaluation_time,
        claim_value=claim,predicate='atlas_current_observability_continuation')
    return dict(claim=claim,material=material,review=[f.g35_record_to_plain_v01(v) for v in review],
        creates_permission=False,incident_root=session.root,pure_host_distinct=live['host'] is not session.host,
        meaningful_next_step='REQUEST_NEW_INDEPENDENT_LOCAL_MEASUREMENTS')
