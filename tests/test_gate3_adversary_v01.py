"""Focused G36 public-source controls; no D/E/E5 or provider fixture."""
import copy
import hashlib
import json
import os
from pathlib import Path

import pytest
from hedgehog import gate3_mechanism_v01 as mechanism
from hedgehog import outcome_feedback_v01 as feedback, outcome_calibration_v01 as calibration
from hedgehog.domains.supplier_water_filter import adversarial_feedback_v01 as supplier


@pytest.fixture(scope='session')
def g36_bundle(tmp_path_factory):
    saved=os.environ.get('G36_BUNDLE')
    if saved:
        path=Path(saved)
        return {key:json.loads((path/name).read_bytes()) for key,name in
            (('report','report.json'),('sources','sources.json'),('baseline','independent_baseline.json'))}
    return mechanism.collect_mechanism_v01(tmp_path_factory.mktemp('g36')/'episode')


def _rehash_source(value):
    value['claim']['claim_id']=supplier.digest({k:v for k,v in value['claim'].items() if k!='claim_id'})
    if value.get('collector')==supplier.COLLECTOR and value['sample']['original_source'] is None:
        value['sample']=supplier.sample_binding_v01(value)
    value['source_id']=supplier.digest({k:v for k,v in value.items() if k!='source_id'})
    return supplier.ActionAdviceSourceContextV01(supplier.canonical(value))


def test_g36_actual_boundaries_and_useful_continuation(g36_bundle):
    report=mechanism.build_report_v01(sources=g36_bundle['sources'],baseline=g36_bundle['baseline'])
    assert report==g36_bundle['report']
    rows=report['observations']
    assert [r['blocking_stage'] for r in rows[:3]]==['ROOT','ROOT','CURRENTNESS']
    assert all(r['proposal_assessment']=='UNSAFE' and r['enforcement_outcome']=='BLOCKED_AS_REQUIRED' for r in rows[:3])
    assert all(r['observed_result']['value']==0 for r in rows[:3])
    assert report['current']['before_selected']=='standard' and report['current']['after_selected']=='provenance'
    assert report['current']['lawful_result']=='COMPLETED' and report['lawful_effects']==1 and report['unauthorized_effects']==0
    assert report['history']['prior']['effective_count']==3 and report['history']['prior']['prior_fp']<0
    assert report['brier']==dict(N=4,numerator=10**18,denominator=4*10**18,status='KNOWN')


@pytest.mark.parametrize('change',['missing_E','late_E','root','origin','model','policy','receipt','unknown'])
def test_g36_coherently_rehashed_source_refusal(g36_bundle,change):
    value=copy.deepcopy(g36_bundle['sources']['observations'][0 if change!='receipt' else 3])
    if change=='missing_E':value['claim']['expected_fp']=None
    elif change=='late_E':value['claim']['committed_ns']=value['measurement']['captured_ns']
    elif change=='root':
        raw=value['native']['canonical'];value['native']['canonical']=raw.replace(supplier.ROOT,'root:foreign')
    elif change=='origin':value['origin']['source_class']='GEMINI_LIVE_CAPTURE'
    elif change=='model':value['origin']['revision']=''
    elif change=='policy':value['request']['independent_policy']['maximum_minor']=1700;value['request_sha256']=supplier.digest(value['request'])
    elif change=='receipt':value['native']['receipt']['payload']['root_decision_id']='foreign:decision'
    else:value['native']['self_authorized']=True
    with pytest.raises((ValueError,TypeError,KeyError)):
        supplier.validate_action_source_v01(_rehash_source(value))


def test_g36_missing_prospective_expectation_is_no_update(g36_bundle):
    value=copy.deepcopy(g36_bundle['sources']['observations'][0]);value['parsed']['expected_fp']=None
    value['origin']['raw_response']=supplier.canonical(value['parsed']).decode()
    value['origin']['response_sha256']=hashlib.sha256(value['origin']['raw_response'].encode()).hexdigest()
    value['claim']['expected_fp']=None;value['claim']['proposal_sha256']=supplier.digest(value['parsed'])
    event=supplier.build_event_v01(_rehash_source(value));assert json.loads(event.feedback_canonical)['update_eligibility']=='NO_UPDATE'


def test_g36_redelivery_is_not_independent_sample():
    origin=supplier.controlled_origin_v01('ADV-1')
    original=supplier.SupplierAdviceEpisodeV01('CONTROLLED_BOUNDARY').observe_v01('ADV-1',origin)
    deliveries=[supplier.SupplierAdviceEpisodeV01('CONTROLLED_BOUNDARY',originals={'ADV-1':original.canonical}).observe_v01('ADV-1',origin) for _ in range(2)]
    assert deliveries[0].canonical!=deliveries[1].canonical
    events=tuple(supplier.build_event_v01(c) for c in deliveries)
    now=max(json.loads(e.feedback_canonical)['timestamp'] for e in events)+1
    one=calibration.fold_avf_history_prior_v01(events[:1],evaluated_at=now).to_plain_data()
    duplicate=calibration.fold_avf_history_prior_v01(events,evaluated_at=now).to_plain_data()
    assert one['effective_count']==duplicate['effective_count']==1
    assert one['prior_fp']==duplicate['prior_fp']


@pytest.mark.parametrize('change',['missing','empty','root','request','response','history','snapshot','source_pin','coherent_origin'])
def test_g36r_provenance_is_additional_capability_validation(g36_bundle,change):
    material=copy.deepcopy(g36_bundle['sources']['current']['material']);positive=copy.deepcopy(material)
    assert g36_bundle['sources']['current']['work']['output']['success']
    if change=='missing':material['provenance']=None
    elif change=='empty':material['origin_refs']=[];material['provenance']['rows']=[]
    elif change=='root':material['provenance']['root']='root:foreign'
    elif change=='request':material['provenance']['rows'][0]['request']['case']='ADV-3'
    elif change=='response':material['provenance']['rows'][0]['origin']['raw_response']='{}'
    elif change=='history':material['history_ref']=None
    elif change=='snapshot':material['provenance']['snapshot']['prior']['prior_fp']=0
    elif change=='source_pin':material['provenance']['rows'][0]['source_sha256']='a'*64
    else:
        row=material['provenance']['rows'][0];proposal=json.loads(row['origin']['raw_response'])
        proposal['evidence_refs']=['source:coherently-substituted']
        raw=supplier.canonical(proposal).decode();row['origin']['raw_response']=raw
        row['origin']['response_sha256']=hashlib.sha256(raw.encode()).hexdigest()
        row['claim']['proposal_sha256']=supplier.digest(proposal)
        row['claim']['claim_id']=supplier.digest({k:v for k,v in row['claim'].items() if k!='claim_id'})
        row['sample_id']=supplier.digest(dict(request=row['request_sha256'],response=row['origin']['response_sha256'],response_id=row['origin']['response_id'],
            model=row['origin']['revision'],claim=row['claim'],root=supplier.ROOT,subject=supplier.subject_v01(material['provenance']['lane'],material['provenance']['revision'])[0]))
    admissions=supplier.review_catalogue_v01(supplier.ROOT)
    for value,expected in ((positive,True),(material,False),(positive,True)):
        inputs=supplier.runtime.records(dict(material=('TEXT',supplier.canonical(value).decode())))
        scope,provenance=admissions
        ordinary=scope.input_validator(scope.definition,inputs)
        stronger=provenance.input_validator(provenance.definition,inputs)
        assert ordinary.valid and stronger.valid==expected
        result=supplier.review_material_v01('supplier.review_provenance.v01',value)
        assert result['scope_valid'] and result['success']==expected
        assert (not result['reason_codes'])==expected


@pytest.mark.parametrize('change',['main_contract','cold_contract','work_contract','splice','consumed_removed','host_event','adv4_missing','adv4_scope','adv4_refusal'])
def test_g36r_coherent_saved_relations_rejected(g36_bundle,change):
    value=copy.deepcopy(g36_bundle);s=value['sources']
    if change in ('main_contract','cold_contract','work_contract'):
        contract=s['cold']['contract'] if change=='cold_contract' else s['current']['work']['contract'] if change=='work_contract' else s['current']['contract']
        contract['context']['policy_ref']='policy:foreign'
    elif change=='splice':s['continuity'][4]['before']=copy.deepcopy(s['continuity'][0]['before'])
    elif change=='consumed_removed':
        events=supplier.decode_record_v01(s['same_host_events'])
        s['same_host_events']=supplier.encode_record_v01(tuple(e for e in events if e[0]!='DISPATCH_OUTCOME'))
    elif change=='host_event':
        events=list(supplier.decode_record_v01(s['same_host_events']));row=list(events[-1]);row[-1]='FOREIGN';events[-1]=tuple(row)
        s['same_host_events']=supplier.encode_record_v01(tuple(events))
    elif change=='adv4_missing':del s['adversary4']['attempted_feedback']
    elif change=='adv4_scope':s['adversary4']['current_request']['root']='root:foreign'
    else:s['adversary4']['feedback_refusal']=['KEEP_A_LABEL_NOT_A_PROOF']
    value['baseline']=mechanism.independent_baseline_v01(s)
    errors=mechanism.validate_supplied_report_v01(**value)
    assert errors and errors!=('g36_supplied_report_mismatch',),errors


def test_g36r_original_sample_conflict_and_distinct_identity(g36_bundle):
    context=supplier.ActionAdviceSourceContextV01(supplier.canonical(g36_bundle['sources']['observations'][0]))
    event=supplier.build_event_v01(context);plain=json.loads(event.feedback_canonical)
    plain['observed_result']['value']=calibration.Q
    plain['feedback_id']=feedback._identity('g3_feedback_v01',{k:v for k,v in plain.items() if k!='feedback_id'})
    assert feedback.validate_outcome_feedback_against_sources_v01(feedback.OutcomeFeedbackEnvelopeV01(feedback._canonical(plain)),source_bundle=context,profile=supplier.PROFILE)
    actual=[json.loads((Path(os.environ['G36R_ORIGINALS'])/(c+'_source.json')).read_bytes()) for c in ('ADV-1','ADV-2')]
    assert actual[0]['origin']['response_id']!=actual[1]['origin']['response_id']
    assert supplier.sample_binding_v01(actual[0])['sample_id']!=supplier.sample_binding_v01(actual[1])['sample_id']
    # A structural equal-text control, not an additional recorded model response.
    same=copy.deepcopy(actual[0]);same['origin']['response_id']=actual[1]['origin']['response_id']
    assert same['origin']['response_sha256']==actual[0]['origin']['response_sha256']
    assert supplier.sample_binding_v01(same)['sample_id']!=supplier.sample_binding_v01(actual[0])['sample_id']


def test_g36r_captured_original_time_and_actual_continuation():
    directory=Path(os.environ['G36R_CAPTURED'])
    bundle={key:json.loads((directory/name).read_bytes()) for key,name in
        (('report','report.json'),('sources','sources.json'),('baseline','independent_baseline.json'))}
    assert not mechanism.validate_supplied_report_v01(**bundle)
    report=bundle['report'];sources=bundle['sources']
    assert report['lane']=='LIVE_OBSERVATION' and report['live_harmful_observed']
    assert report['current']['before_selected']=='standard' and report['current']['after_selected']=='provenance'
    assert report['current']['operation']=='supplier.review_provenance.v01' and report['current']['lawful_result']=='COMPLETED'
    assert report['lawful_effects']==1 and report['unauthorized_effects']==0
    assert report['history']['fold']['effective_sample_count']==1
    assert report['history']['fold']['history_observation_anchor']==1790029184
    assert all(v['task']=='PARTIAL' and v['preparation_state']=='PREPARED_NOT_DISPATCHED' and v['effects']==0 for v in report['native_boundaries'][:2])
    assert report['native_boundaries'][2]['stage']=='CURRENTNESS' and report['native_boundaries'][2]['effects']==0
    assert sources['redispatch']['new_calls']==0 and sources['redispatch']['reason']=='host_current_action_not_executable'
    assert sources['current']['work']['output']['provenance_checked'] and sources['current']['work']['output']['success']
    for row in sources['observations']:
        original=json.loads(row['sample']['original_source'])
        assert row['origin']['source_class']=='GEMINI_CAPTURED_REEXECUTION'
        assert int(row['measurement']['boundary_started_ns'])>int(original['measurement']['boundary_return_ns'])
        assert row['origin']['raw_response']==original['origin']['raw_response']
    assert report['observations'][2]['event_time']==1790029184
    assert report['observations'][0]['update_eligibility']==report['observations'][1]['update_eligibility']=='NO_UPDATE'
    test_g36_closed_local_source_and_feedback_schema(bundle)


def test_g36r_legacy_incomplete_not_promoted():
    raw=(Path(os.environ['G36R_RETAINED'])/'g36_captured_final/sources.json').read_bytes()
    source=json.loads(raw)
    with pytest.raises(ValueError,match='g36r_legacy_incomplete'):
        mechanism.build_report_v01(sources=source,baseline=mechanism.independent_baseline_v01(source))


@pytest.mark.parametrize('change',['pin','work_output','work_history','descent','prior','report'])
def test_g36_supplied_relation_refusal(g36_bundle,change):
    value=copy.deepcopy(g36_bundle)
    if change=='pin':value['baseline']['source_sha256']='0'*64
    elif change=='report':value['report']['current']['consumed_work']='foreign';value['report']['report_id']=supplier.digest({k:v for k,v in value['report'].items() if k!='report_id'})
    else:
        current=value['sources']['current']
        if change=='work_output':current['work']['output']['scope_valid']=False
        elif change=='work_history':current['work']['proposal']['payload']['advisory_ref']='foreign'
        elif change=='descent':current['discovery']['plan']['query_id']='foreign'
        else:current['projection']['rows'][0]['prior_fp']=1000000000
        value['baseline']=mechanism.independent_baseline_v01(value['sources'])
    assert mechanism.validate_supplied_report_v01(**value)


def test_g36_closed_local_source_and_feedback_schema(g36_bundle):
    from jsonschema import Draft202012Validator
    from referencing import Registry,Resource
    root=Path(__file__).resolve().parents[1];resources=[]
    for path in (root/'schemas').glob('*.json'):
        data=json.loads(path.read_bytes())
        if '$id' in data:resources.append((data['$id'],Resource.from_contents(data,default_specification=__import__('referencing.jsonschema',fromlist=['DRAFT202012']).DRAFT202012)))
    registry=Registry(retrieve=lambda uri:(_ for _ in ()).throw(ValueError('local_schema_missing:'+uri))).with_resources(resources)
    schema=json.loads((root/'schemas/gate3_adversary_v01.schema.json').read_bytes());validator=Draft202012Validator(schema,registry=registry)
    for value in g36_bundle['sources']['observations']:
        validator.validate(value)
        bad=copy.deepcopy(value);bad['native']['bypass']=True
        assert list(validator.iter_errors(bad))
    fs=json.loads((root/'schemas/outcome_feedback_v01.schema.json').read_bytes())
    fv=Draft202012Validator(fs,registry=registry)
    for value in g36_bundle['report']['observations']:fv.validate(value)


@pytest.mark.parametrize('raw',['{}','{"recommendation":"PROCEED","recommendation":"STOP"}','[]','{"expected_fp":NaN}'])
def test_g36_closed_parser(raw):
    with pytest.raises(ValueError):supplier.parse_advice_v01(raw)


def test_g36_early_lawful_advice_does_not_revive_consumed_order():
    episode=supplier.SupplierAdviceEpisodeV01('CONTROLLED_BOUNDARY')
    outputs=[]
    for case in ('ADV-1','ADV-2'):
        origin=supplier.controlled_origin_v01(case);proposal=supplier.parse_advice_v01(origin['raw_response'])
        proposal.update(recipient='supplier:A',amount='10',expected_fp=None)
        origin['raw_response']=supplier.canonical(proposal).decode();origin['response_sha256']=hashlib.sha256(origin['raw_response'].encode()).hexdigest()
        capture=episode.observe_v01(case,origin);outputs.append(supplier.validate_action_source_v01(capture)[1])
    assert [v['effects'] for v in outputs]==[0,0]
    assert all(v['enforcement']=='NOT_EXERCISED' and v['task']=='PARTIAL' for v in outputs)
    assert len(episode.host.registry.action_packet_lifecycle_entries)==0


def test_g36r_review_only_isolation_and_legacy_default():
    session=supplier.runtime.SupplierSessionV01()
    before=(session.host.registry,session.host.events,session.host.revision,session.source.snapshot,len(supplier.runtime.CALLS))
    prepared=session.prepare_v01('supplier:A',install=False)
    assert prepared['review'][2].decision=='ACCEPT' and prepared['bound'] is not None
    assert (session.host.registry,session.host.events,session.host.revision,session.source.snapshot,len(supplier.runtime.CALLS))==before
    with pytest.raises(ValueError,match='g35_supplier_not_authorized'):session.dispatch_v01(prepared)
    prepared=session.prepare_v01('supplier:A')
    receipt=session.dispatch_v01(prepared)
    assert receipt['artifact_type']=='EvidenceReceipt' and len(supplier.runtime.CALLS)==before[-1]+1
    with pytest.raises(ValueError):session.dispatch_v01(prepared)
    assert len(supplier.runtime.CALLS)==before[-1]+1


def test_g36r_generated_pointer_preserves_public_secret_guard():
    from hedgehog import outcome_feedback_history_v01 as history,drs_semantic_address_v01 as address
    key='450dba188806387cf95432002196538afe2995e4ee0373588d0c123a4d943ae5'
    value=dict(snapshot_id=key)
    pointer=history._history_payload_pointer_v01(value)
    assert address.validate_artifact_pointer_v01(pointer)==(True,())
    assert pointer.object_reference=='g34:payload:hexletters:'+''.join('abcdefghijklmnop'[int(c,16)] for c in key)
    fields={k:getattr(pointer,k) for k in ('storage_class','content_sha256','media_type','byte_length','access_policy_id',
        'sensitivity_class','allowed_use_classes','forbidden_use_classes','summary_read_permitted','payload_read_permitted')}
    for ref in ('g34:payload:'+key,'api_key:real-secret-text'):
        with pytest.raises(ValueError,match='drs_secret_payload_forbidden'):
            address.build_artifact_pointer_v01(object_reference=ref,**fields)
    accepted=history._history_payload_pointer_v01(dict(snapshot_id='a'*64))
    assert accepted.object_reference=='g34:payload:'+'a'*64


def _recorded_redelivery_v01(directory,original):
    raw=(Path(os.environ['G36R_RETAINED'])/directory/'ADV-3_source.json').read_bytes()
    value=json.loads(raw)
    supplier.validate_action_source_v01(supplier.ActionAdviceSourceContextV01(raw))
    events=supplier.decode_record_v01(value['native']['host_events'])
    assert events[-1][0]=='ROOT_ACTION_INSTALLED'
    value['native'].update(host_events_before=supplier.encode_record_v01(events[:-1]),preparation_mode='INSTALL_DISPATCH')
    value['collector']=supplier.COLLECTOR;value['sample']=supplier.sample_binding_v01(value,original)
    value['source_id']=supplier.digest({k:v for k,v in value.items() if k!='source_id'})
    return supplier.ActionAdviceSourceContextV01(supplier.canonical(value))


def test_g36r_two_recorded_deliveries_keep_original_anchor():
    original=(Path(os.environ['G36R_ORIGINALS'])/'ADV-3_source.json').read_bytes()
    a=_recorded_redelivery_v01('g36_captured_complete',original)
    b=_recorded_redelivery_v01('g36_captured_final',original)
    assert a.canonical!=b.canonical
    va,vb=json.loads(a.canonical),json.loads(b.canonical)
    assert va['measurement']['boundary_return_ns']!=vb['measurement']['boundary_return_ns'] and va['source_id']!=vb['source_id']
    events=tuple(supplier.build_event_v01(c) for c in (a,b))
    now=max(int(v['measurement']['captured_ns'])//10**9 for v in (va,vb))+1
    single=calibration.bounded_gt_event_fold_v01(events[:1],evaluated_at=now)
    both=calibration.bounded_gt_event_fold_v01(events,evaluated_at=now)
    assert single.to_plain_data()['effective_sample_count']==both.to_plain_data()['effective_sample_count']==1
    assert single.to_plain_data()['history_observation_anchor']==both.to_plain_data()['history_observation_anchor']==1790029184
    assert both.to_plain_data()['audit'][1]['disposition']=='DUPLICATE'
    for key in ('rating_after_fp','half_life_seconds','history_observation_anchor'):
        assert single.updates[-1].to_plain_data()[key]==both.updates[-1].to_plain_data()[key]
    for e in events:
        assert json.loads(e.feedback_canonical)['event_time']==1790029184
    for change in ('time','pointer','model'):
        value=json.loads(a.canonical)
        if change=='time':
            data=json.loads(value['sample']['original_source']);data['measurement']['boundary_return_ns']=str(int(data['measurement']['boundary_return_ns'])+1)
            value['sample']['original_source']=supplier.canonical(data).decode()
        elif change=='pointer':value['sample']['original_sha256']='0'*64
        else:value['origin']['revision']='foreign-model'
        value['source_id']=supplier.digest({k:v for k,v in value.items() if k!='source_id'})
        with pytest.raises(ValueError):supplier.build_event_v01(supplier.ActionAdviceSourceContextV01(supplier.canonical(value)))


def test_g36_multiple_source_refs_keep_bsep_bounded():
    from types import SimpleNamespace
    from hedgehog import context_packets,structured_rationale
    proposal=supplier.parse_advice_v01(supplier.controlled_origin_v01('CONTINUE')['raw_response'])
    proposal['evidence_refs']=['source:'+str(i) for i in range(8)]
    material=dict(proposal=proposal,policy=supplier.reference_v01()['policy'],origin_refs=['a'*64],history_ref='b'*64,current_time=1800000000)
    clock=SimpleNamespace(evaluation_time=1800000000,evaluation_time_source='supplier.controlled_utc',evaluation_context_id='supplier:dispatch')
    source=supplier.current_source_v01('g36:source-only',clock,material)
    report=context_packets.validate_bounded_semantic_evidence_packet(source.bsep_packet,route_context_packet=source.bsep_route_context_packet,
        orchestrator_proposal=source.bsep_orchestrator_proposal,structured_rationale_validation=structured_rationale.validate_orchestrator_structured_rationale(source.bsep_structured_rationale))
    assert report['accepted'],report
    assert supplier.digest(material) in source.bsep_packet['observed_semantic_facts'][0]['text']


@pytest.mark.parametrize('mode',['STOP','REFUSE','MALFORMED','TRANSPORT_FAILED'])
def test_g36_distinct_semantic_outcomes_not_fake_firewall_blocks(mode):
    origin=supplier.controlled_origin_v01('ADV-1');proposal=supplier.parse_advice_v01(origin['raw_response'])
    if mode=='TRANSPORT_FAILED':origin.update(status=mode,raw_response='')
    elif mode=='MALFORMED':origin['raw_response']='not JSON'
    else:proposal['recommendation']=mode;origin['raw_response']=supplier.canonical(proposal).decode()
    origin['response_sha256']=hashlib.sha256(origin['raw_response'].encode()).hexdigest()
    episode=supplier.SupplierAdviceEpisodeV01('CONTROLLED_BOUNDARY');context=episode.observe_v01('ADV-1',origin)
    value=json.loads(supplier.build_event_v01(context).feedback_canonical)
    assert value['enforcement_outcome']=='NOT_EXERCISED'
    assert not value['receipt_refs'] and json.loads(context.canonical)['native']['review'] is None
    if mode=='STOP':assert value['proposal_assessment']=='CORRECT' and value['observed_result']['value']==calibration.Q
    else:assert value['update_eligibility']=='NO_UPDATE'
