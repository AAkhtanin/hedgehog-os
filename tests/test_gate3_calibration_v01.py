"""G35 cheap contracts and independent consumers of one actual saved collection."""
from copy import deepcopy
import json
import os
from pathlib import Path
import pytest
from jsonschema import Draft202012Validator
from hedgehog import outcome_feedback_v01 as f, outcome_feedback_report_v01 as reports

ROOT=Path(__file__).resolve().parents[1]


def test_g35_inventory_finite_and_offline():
    value=reports.inventory_v01()
    assert len(value['cases'])==5 and len({v['public_entrypoint_binding'] for v in value['cases']})==5
    assert sum(v['cost']['D'] for v in value['cases'])==1 and not any(v['cost']['E'] or v['cost']['network'] for v in value['cases'])
    assert 'G36_LIVE_ORIGIN' in value['pending'] and 'UNSUPPORTED_NATIVE_SCHEMA' in value['pending']


def test_g35_closed_source_schema_rejects_invalid_neighbors():
    schema=json.loads((ROOT/'schemas/outcome_feedback_g35_sources_v01.schema.json').read_bytes())
    Draft202012Validator.check_schema(schema)
    validator=Draft202012Validator(schema)
    base=dict(profile=f.G35_PROFILES[0],domain='AIRLINE',case_id='G35-AIRLINE',version='v0.1',body=dict(source={},fixtures={},bank_review=[{}, {}, {}],
        receipt_provenance='CONTROLLED_FIXTURE_INPUT_NOT_NATIVE_HOST_OR_LIVE_BANKING'),measurement=dict(started_ns='1',finished_ns='2',elapsed_us=1),source_revision='a'*64)
    assert list(validator.iter_errors(base))
    for key,value in (('profile','unknown'),('version','v2'),('extra',True),('domain','TESTFLIX')):
        mutated=dict(base,**{key:value})
        assert list(validator.iter_errors(mutated))
    with pytest.raises(ValueError):f.validate_g35_source_v01(base)
    assert list(validator.iter_errors(dict(base,measurement=dict(base['measurement'],elapsed_us=-1))))


@pytest.fixture(scope='module')
def saved():
    directory=Path(os.environ['G35_SAVED_PACK'])
    return tuple(json.loads((directory/name).read_bytes()) for name in ('report.json','sources.json','independent_baseline.json'))


def test_g35_all_current_sources_same_shape(saved):
    report,sources,baseline=saved
    assert not reports.validate_supplied_report_v01(report,sources=sources,baseline=baseline)
    schema=Draft202012Validator(json.loads((ROOT/'schemas/outcome_feedback_g35_sources_v01.schema.json').read_bytes()))
    shapes=[]
    for source,row in zip(sources,report['rows'],strict=True):
        schema.validate(source)
        for record in row['observations']:
            value=record['feedback'];assert not f.validate_outcome_feedback_structure_v01(value)
            shapes.append(set(value));assert value['update_eligibility']=='NO_UPDATE'
            assert value['pre_decision_expectation']['state']=='UNKNOWN' and value['observed_regret']['state']=='UNKNOWN'
    assert all(v==shapes[0] for v in shapes)


@pytest.mark.parametrize('mutation',('outcome','link','missing','duplicate','denominator','current_consumption'))
def test_g35_supplied_rehashed_report_refused(saved,mutation):
    report,sources,baseline=saved;bad=deepcopy(report)
    if mutation=='outcome':bad['rows'][0]['observations'][0]['feedback']['task_outcome']='FAILED'
    elif mutation=='link':bad['rows'][0]['source_ref']='a'*64
    elif mutation=='missing':bad['rows'].pop()
    elif mutation=='duplicate':bad['rows'][-1]=deepcopy(bad['rows'][0])
    elif mutation=='denominator':bad['rows'][0]['observations'][0]['metrics']['brier']['denominator']=1
    else:bad['rows'][0]['observations'][0]['metrics']['consumed_drs_records']=['forged:current']
    bad['report_id']=f.g35_hash_v01({k:v for k,v in bad.items() if k!='report_id'})
    assert reports.validate_supplied_report_v01(bad,sources=sources,baseline=baseline)
    assert not reports.validate_supplied_report_v01(report,sources=sources,baseline=baseline)


@pytest.mark.parametrize('field,value',(('profile','unknown'),('domain','FOREIGN'),('version','v2'),('extra',False)))
def test_g35_source_closed_dispatch(saved,field,value):
    report,sources,baseline=saved
    for source in sources:
        bad=deepcopy(source);bad[field]=value
        with pytest.raises((ValueError,TypeError,KeyError)):f.validate_g35_source_v01(bad)


def test_g35_real_revocation_and_mixed_outcomes(saved):
    report,sources,_=saved
    supplier=f.validate_g35_source_v01(sources[1]);testflix=f.validate_g35_source_v01(sources[2])
    assert supplier[0]['quality']=='UNSAFE' and supplier[0]['enforcement']=='BLOCKED_AS_REQUIRED' and supplier[0]['effect_count']==0
    assert supplier[1]['effect_count']==1 and supplier[1]['enforcement']=='ALLOWED_AS_REQUIRED'
    assert testflix[1]['execution']=='NEEDS_USER'
    assert [v['effect_count'] for v in testflix[2:]]==[1,0,1]
    assert testflix[3]['stage']=='CURRENTNESS' and testflix[3]['execution']=='EXPIRED_OR_REVOKED'


def test_g35_actual_export_privacy_canaries(saved):
    report,sources,_=saved
    exported=f.g35_bytes_v01(dict(report=report,sources=sources))
    for secret in (b'CANARY_BANK_PRIVATE_NO_ROLE_EXPORT',b'CANARY_USER_PRIVATE_NO_BANK_OR_DEVICE_EXPORT'):
        assert secret not in exported
    assert 'bank_private' not in sources[2]['body']['request'] and 'user_private' not in sources[2]['body']['request']


def test_g35_pure_replay_exact(saved):
    report,sources,baseline=saved
    a=reports.replay_v01(report=report,sources=sources,baseline=baseline)
    b=reports.replay_v01(report=deepcopy(report),sources=deepcopy(sources),baseline=deepcopy(baseline))
    assert f.g35_bytes_v01(a)==f.g35_bytes_v01(b)
    assert a['new_samples']==a['new_history_writes']==a['new_current_decisions']==0


@pytest.mark.parametrize('mutation',('foreign_root','foreign_transaction','coherent_receipt','changed_material','unexpected_effect','nested_extra','wrong_nested_type','oversized','backfilled_expectation'))
def test_g35_coherent_saved_source_neighbors(saved,mutation):
    _,sources,_=saved
    bad=deepcopy(sources[1])
    if mutation=='foreign_root':
        # A separately valid saved review is not this Supplier operation's Root.
        f.g35_validate_root_v01(sources[3]['body']['root'])
        bad['body']['rows'][1]['review']=deepcopy(sources[3]['body']['root'])
    elif mutation=='foreign_transaction':
        bad=deepcopy(sources[2]);bad['body']['result']['transaction_id']='transaction:foreign'
        f.g35_validate_artifact_v01(bad['body']['result'])
    elif mutation=='coherent_receipt':
        bad=deepcopy(sources[2]);bad['body']['branches'][0]['receipt']=deepcopy(bad['body']['branches'][2]['receipt'])
        f.g35_validate_artifact_v01(bad['body']['branches'][0]['receipt'])
    elif mutation=='changed_material':bad['body']['rows'][1]['material']['document_claim']='substituted:source'
    elif mutation=='unexpected_effect':
        bad=deepcopy(sources[2]);bad['body']['branches'][1]['executor_delta']=1
    elif mutation=='nested_extra':bad['body']['rows'][0]['canonical']['fields']['trusted']=True
    elif mutation=='wrong_nested_type':bad['measurement']['elapsed_us']=True
    elif mutation=='oversized':bad['source_revision']='a'*257
    else:bad['body']['pre_decision_expectation']=1000000
    # Canonical rehash is possible, but not a semantic acceptance credential.
    assert f.g35_hash_v01(bad)!=f.g35_hash_v01(sources[1])
    with pytest.raises((ValueError,KeyError,TypeError,AttributeError)):f.validate_g35_source_v01(bad)


def test_g35_all_positive_sources_after_refusals(saved):
    _,sources,_=saved
    assert [len(f.validate_g35_source_v01(s)) for s in deepcopy(sources)]==[3,2,5,2,2]


def _g35r_source_attack(source,variant):
    from hedgehog.kernel import work_composition_v01 as work
    bad=deepcopy(source);body=bad['body'];artifact=body['result'];payload=artifact['payload']
    topology=body['topology'];top=topology['payload'];program=top['work_program']
    if variant=='topology_ref':payload['topology_ref']='work_topology:foreign'
    elif variant=='first_work_id':payload['work_results'][0]['work_id']='foreign_work'
    elif variant=='nested_output':payload['work_results'][0]['result']['output'][0]['parameter_name']='foreign_output'
    elif variant=='consumption':payload['work_results'][1]['consumed_fields'][0]['source_artifact_id']='result:foreign'
    elif variant=='missing':payload['work_results'].pop()
    elif variant=='duplicate':payload['work_results'][1]=deepcopy(payload['work_results'][0])
    elif variant=='reordered':payload['work_results'].reverse()
    elif variant.startswith('program_'):
        field=variant.removeprefix('program_')
        if field=='task':program['task_id']='task:foreign'
        elif field=='revision':program['intent_ref']='intent:foreign'
        elif field=='item':
            previous=program['items'][0]['work_id'];program['items'][0]['work_id']='foreign_work'
            top['ordered_work_ids']=['foreign_work' if v==previous else v for v in top['ordered_work_ids']]
            for item in program['items']:
                item['depends_on']=['foreign_work' if v==previous else v for v in item['depends_on']]
                for bound in item['inputs']:
                    if bound['source'].get('predecessor_work_id')==previous:bound['source']['predecessor_work_id']='foreign_work'
        elif field=='owner':program['items'][0]['owning_root_id']='root:foreign'
        else:program['items'][0]['definition_id']='definition:foreign'
        program['revision_id']=work._identity('work_revision',{k:v for k,v in program.items() if k!='revision_id'})
        topology['artifact_id']=work._identity('work_topology',top)
        topology['parent_refs']=[work._identity('work_proposal',{'work_program':program})]
        topology['trace_refs']=[program['task_id'],program['revision_id']]
        artifact['parent_refs']=[topology['artifact_id']];artifact['trace_refs']=list(topology['trace_refs'])
        payload['topology_ref']=topology['artifact_id']
    elif variant=='time':artifact['time_envelope']['ct_session_anchor']='session:foreign'
    elif variant=='trace':artifact['trace_refs']=['task:foreign','revision:foreign']
    elif variant=='parent':artifact['parent_refs']=['work_topology:foreign']
    else:
        field,value={'kind':('artifact_type','SemanticEvidence'),'component':('source_component','other_runtime'),
            'authority':('authority_class','ADVISORY'),'lifecycle':('lifecycle_state','VALIDATED'),
            'owner':('owner_root_id','root:foreign'),'transaction':('transaction_id','transaction:foreign')}[variant]
        artifact[field]=value
    artifact['artifact_id']=work._identity('work_results',payload)
    # These are new, coherent native content IDs, not stale-digest test failures.
    assert artifact['artifact_id']==work._identity('work_results',artifact['payload'])
    if variant in ('topology_ref','first_work_id','nested_output','consumption','missing','duplicate','reordered'):
        f.g35_validate_artifact_v01(artifact)
    return bad


@pytest.mark.parametrize('index',(2,3),ids=('testflix','workspace'))
def test_g35r_native_work_relations(saved,index):
    report,sources,baseline=saved
    records=[]
    variants=('topology_ref','first_work_id','nested_output','consumption','missing','duplicate','reordered',
        'program_task','program_revision','program_item','program_owner','program_definition',
        'time','trace','parent','kind','component','authority','lifecycle','owner','transaction')
    for variant in variants:
        bad=_g35r_source_attack(sources[index],variant)
        # Payload substitutions carry valid generic envelopes and native IDs.
        with pytest.raises(ValueError) as failure:f.validate_g35_source_v01(bad)
        envelope=variant in ('time','trace','parent','kind','component','authority','lifecycle','owner','transaction')
        if not envelope:assert str(failure.value).startswith('g35_work_'),(variant,str(failure.value))
        altered=deepcopy(sources);altered[index]=bad
        assert reports.validate_supplied_report_v01(report,sources=altered,baseline=baseline)==('g35_independent_baseline_mismatch',)
        untrusted_test_baseline=reports.build_baseline_v01(altered,explicit_times=baseline['explicit_times'])
        reasons=reports.validate_supplied_report_v01(report,sources=altered,baseline=untrusted_test_baseline)
        assert reasons,(variant,reasons)
        if not envelope:assert reasons[0].startswith('g35_work_'),(variant,reasons)
        records.append(dict(variant=variant,source_refusal=str(failure.value),supplied_refusal=list(reasons),
            real_baseline_refusal='g35_independent_baseline_mismatch',test_anchor='UNTRUSTED_TEST_MATERIAL',
            native_result_id=bad['body']['result']['artifact_id']))
    assert f.validate_g35_source_v01(deepcopy(sources[index]))
    assert not reports.validate_supplied_report_v01(report,sources=sources,baseline=baseline)
    if 'G33R_EVIDENCE' in os.environ:
        path=Path(os.environ['G33R_EVIDENCE'])/'commands'/os.environ['G33R_COMMAND']/('relations_'+sources[index]['domain']+'.json')
        path.write_text(json.dumps(records,indent=2)+'\n')


def _g35r_count_call(function):
    import sys,time
    from hedgehog.domains.airline import outcome_feedback_adapter_v01 as airline
    from hedgehog.domains.supplier_water_filter import outcome_feedback_adapter_v01 as supplier
    from hedgehog.domains.testflix import outcome_feedback_adapter_v01 as testflix
    from hedgehog.domains.ephemeral_workspace import outcome_feedback_adapter_v01 as workspace
    from hedgehog.domains.landslide_sentinel import outcome_feedback_adapter_v01 as sentinel
    entries=(f.validate_g35_source_v01,airline.validate_source_v01,supplier.validate_source_v01,testflix.validate_source_v01,
        workspace.validate_source_v01,sentinel.validate_g35_source_v01)
    targets={fn.__code__:fn.__module__+'.'+fn.__name__ for fn in entries};counts=dict.fromkeys(targets.values(),0)
    tool=4;sys.monitoring.use_tool_id(tool,'g35r_source_counts')
    def count(code,offset):counts[targets[code]]+=1
    sys.monitoring.register_callback(tool,sys.monitoring.events.PY_START,count)
    for code in targets:sys.monitoring.set_local_events(tool,code,sys.monitoring.events.PY_START)
    started=time.monotonic()
    try:value=function()
    finally:
        for code in targets:sys.monitoring.set_local_events(tool,code,0)
        sys.monitoring.free_tool_id(tool)
    assert list(counts.values())==[5,1,1,1,1,1],counts
    return value,dict(counts=counts,seconds=time.monotonic()-started)


def test_g35r_public_build_verify_replay_single_scan(saved):
    import hashlib
    report,sources,baseline=saved;metrics={}
    made,metrics['build']=_g35r_count_call(lambda:reports.build_report_v01(sources=sources,baseline=baseline,explicit_times=baseline['explicit_times']))
    reasons,metrics['verify']=_g35r_count_call(lambda:reports.validate_supplied_report_v01(report,sources=sources,baseline=baseline))
    replay,metrics['replay']=_g35r_count_call(lambda:reports.replay_v01(report=report,sources=sources,baseline=baseline))
    assert not reasons and f.g35_bytes_v01(made)==f.g35_bytes_v01(report)
    raw=f.g35_bytes_v01(replay)+b'\n'
    assert len(raw)==144756 and hashlib.sha256(raw).hexdigest()=='f9ca8e48dc61c815e1235afa0c5141aed96128823dd094ae44aef8ecd03ee75d'
    made['rows'][0]['observations'][0]['metrics']['consumed_drs_records'].append('caller:mutation')
    assert not report['rows'][0]['observations'][0]['metrics']['consumed_drs_records']
    assert not replay['report']['rows'][0]['observations'][0]['metrics']['consumed_drs_records']
    if 'G33R_EVIDENCE' in os.environ:
        path=Path(os.environ['G33R_EVIDENCE'])/'commands'/os.environ['G33R_COMMAND']/'single_scan_metrics.json'
        path.write_text(json.dumps(metrics,indent=2)+'\n')


def test_g35r_independent_calls_recheck_mutable_inputs(saved):
    report,sources,baseline=deepcopy(saved)
    assert not reports.validate_supplied_report_v01(report,sources=sources,baseline=baseline)
    sources[3]=_g35r_source_attack(sources[3],'nested_output')
    assert reports.validate_supplied_report_v01(report,sources=sources,baseline=baseline)
    test_anchor=reports.build_baseline_v01(sources,explicit_times=baseline['explicit_times'])
    assert reports.validate_supplied_report_v01(report,sources=sources,baseline=test_anchor)[0].startswith('g35_work_')
    report,sources,baseline=deepcopy(saved)
    baseline['explicit_times']['timestamp']+=1
    assert reports.validate_supplied_report_v01(report,sources=sources,baseline=baseline)==('g35_independent_time_binding',)
    with pytest.raises(ValueError):reports.replay_v01(report=report,sources=sources,baseline=baseline)
    report,sources,baseline=deepcopy(saved)
    assert not reports.validate_supplied_report_v01(report,sources=sources,baseline=baseline)
    context=f.G35OutcomeSourceContextV01(f.g35_bytes_v01(sources[3]),0)
    obs=f.build_outcome_observation_v01(source_bundle=context,profile=sources[3]['profile'],explicit_times=baseline['explicit_times'])
    value=f.build_outcome_feedback_v01(observation=obs,source_bundle=context,profile=sources[3]['profile'])
    assert not f.validate_outcome_feedback_against_sources_v01(value,source_bundle=context,profile=sources[3]['profile'])
    bad=f.G35OutcomeSourceContextV01(f.g35_bytes_v01(_g35r_source_attack(sources[3],'first_work_id')),0)
    for call in (lambda:f.build_outcome_observation_v01(source_bundle=bad,profile=sources[3]['profile'],explicit_times=baseline['explicit_times']),
        lambda:f.build_outcome_feedback_v01(observation=obs,source_bundle=bad,profile=sources[3]['profile'])):
        with pytest.raises(ValueError):call()
    assert f.validate_outcome_feedback_against_sources_v01(value,source_bundle=bad,profile=sources[3]['profile'])
    assert not f.validate_outcome_feedback_against_sources_v01(value,source_bundle=context,profile=sources[3]['profile'])
