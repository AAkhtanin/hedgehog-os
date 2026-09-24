"""One shared controlled native story and independently reached refusal neighbors."""
from copy import deepcopy
from dataclasses import replace
import json
import os
from pathlib import Path
import time
import pytest
from hedgehog.domains.wedding_seating import contracts_v01 as base,privacy_v01 as privacy,math_v01 as math
from hedgehog.domains.wedding_seating import native_contracts_v01 as c,native_capabilities_v01 as caps,native_adapter_v01 as n,runtime_v01 as runtime
from hedgehog.domains.wedding_seating import allocation_v01 as allocation,memory_v01 as memory,supplied_v01 as supplied

def inputs(request='request:w2:keep',kind='GENERATE',profile='KEEP_FAMILIAR_V01',parent=None,problem=None):
    p=problem or json.loads(Path('fixtures/wedding_seating/reference_problem_v01.json').read_text())
    intent='Check the existing plan without replacement.' if kind=='VALIDATE_EXISTING' else ('Clarify the missing approved objective.' if kind=='CLARIFY' else ('Prefer familiar circles.' if profile=='KEEP_FAMILIAR_V01' else 'Prefer mixing circles.'))
    owner=c.OwnerContextV01(c.canonical(p),request,kind,profile,intent,parent,('PRIVATE_CANARY_W2',))
    original=owner.problem()
    policy=privacy.DisclosurePolicyV01(p['disclosure_profile_ref'],True,tuple(p['guest_ids']),tuple(t['table_id'] for t in p['table_records']),tuple(x['condition_id'] for x in p['hard_conditions']),c.source_refs(p),((p['safe_intent_ref'],intent),))
    templates=json.loads(Path('fixtures/wedding_seating/semantic_proposals_v01.json').read_text())['proposals'][:2]
    for s in templates:
        s.update(request_ref=request,capture_ref=request+':capture:'+s['role'],problem_ref=original.content_id,problem_revision=p['problem_revision'],task_kind=kind,unresolved=['question:objective'] if kind=='CLARIFY' else [],source_refs=list(c.source_refs(p)))
        if s['role']=='ORCHESTRATOR':
            s['needs']=['ORIGINAL_VALIDATION'] if kind=='VALIDATE_EXISTING' else ['LOCAL_CLARIFICATION'] if kind=='CLARIFY' else ['EXACT_SEARCH','ORIGINAL_VALIDATION','REQUIREMENT_REVIEW']
            s['requested_outputs']=['VALIDATION_REPORT'] if kind=='VALIDATE_EXISTING' else ['CLARIFICATION'] if kind=='CLARIFY' else ['SEATING_CANDIDATES','VALIDATION_REPORT']
        else:
            s.update(objective_profile=profile,condition_refs=[x['condition_id'] for x in p['hard_conditions']],needed_capabilities=['VALIDATE_ORIGINAL'] if kind=='VALIDATE_EXISTING' else [] if kind=='CLARIFY' else ['COMPILE_QUBO','SOLVE_EXACT','VALIDATE_ORIGINAL'])
    projections=[privacy.semantic_projection_v01(original,role,policy=policy).to_plain_v01() for role in ('ORCHESTRATOR','REQUIREMENT_ARCHITECT')]
    return owner,templates,dict(policy=policy,serialized_projections=projections)

def invoke(owner,responses,kwargs,**extra):
    return runtime.execute_v01(owner,owner.problem_bytes,[c.canonical(v) for v in responses],**kwargs,now=1700000000,**extra)

def test_source_only_independent_intake_v01():
    owner,responses,kw=inputs()
    # Entire hand-built projection, not a second call to the projection producer.
    assert kw['serialized_projections'][0]==dict(projection='SEMANTIC_APPROVED',synthetic=True,role='ORCHESTRATOR',safe_intent='Prefer familiar circles.',guest_count=12,table_capacities=[4,4,4])
    good=c.consume_semantics_v01(owner,owner.problem_bytes,[c.canonical(v) for v in responses],**kw)
    assert good['task_kind']=='GENERATE'
    for edit in ('delete','predicate','revision','profile'):
        bad=json.loads(owner.problem_bytes)
        if edit=='delete':bad['hard_conditions'].pop(6)
        elif edit=='predicate':bad['hard_conditions'][6]['predicate']='TOGETHER'
        elif edit=='revision':bad['problem_revision']+=1;bad['parent_problem_ref']=owner.problem().content_id
        else:bad['allowed_objective_profiles']=['MIX_CIRCLES_V01']
        with pytest.raises(ValueError,match='independent_owner_problem'):owner.check(c.canonical(bad))

def test_source_only_semantic_neighbors_v01():
    owner,responses,kw=inputs()
    mutations=[(0,'request_ref','request:foreign'),(0,'role','REQUIREMENT_ARCHITECT'),(1,'capture_ref','capture:foreign'),(1,'problem_ref','0'*64),
        (1,'task_kind','REVISE'),(1,'condition_refs',responses[1]['condition_refs'][:-1]),(1,'needed_capabilities',['SOLVE_EXACT']),
        (0,'needs',['ORIGINAL_VALIDATION','UNKNOWN']), (0,'endpoint','https://not-authorized.invalid'),(1,'permission',True),(0,'reason','PRIVATE_CANARY_W2'),(1,'objective_profile','MIX_CIRCLES_V01')]
    for i,k,v in mutations:
        bad=deepcopy(responses);bad[i][k]=v
        with pytest.raises(ValueError):c.consume_semantics_v01(owner,owner.problem_bytes,[c.canonical(x) for x in bad],**kw)
    assert c.consume_semantics_v01(owner,owner.problem_bytes,[c.canonical(x) for x in responses],**kw)['profile']==owner.profile
    escaped=deepcopy(responses);escaped[0]['reason']='PRIVATE_CANARY_W2'
    raw=[c.canonical(x) for x in escaped];raw[0]=raw[0].replace(b'PRIVATE_CANARY_W2',b'PRIVATE_\\u0043ANARY_W2')
    with pytest.raises(ValueError,match='private_semantic_material'):c.consume_semantics_v01(owner,owner.problem_bytes,raw,**kw)
    projections=deepcopy(kw);projections['serialized_projections'][0]['safe_intent']='PRIVATE_CANARY_W2'
    with pytest.raises(ValueError,match='serialized_projection_mismatch'):c.consume_semantics_v01(owner,owner.problem_bytes,[c.canonical(x) for x in responses],**projections)

@pytest.fixture(scope='session')
def story(tmp_path_factory):
    directory=Path(os.environ.get('W2_COMMAND',str(tmp_path_factory.mktemp('wedding'))))/'story'
    directory.mkdir(parents=True,exist_ok=True)
    def save(name,value): (directory/(name+'.json')).write_text(json.dumps(value,sort_keys=True,indent=2)+'\n')
    def journal(phase,**v):
        with (directory/'phases.jsonl').open('a') as f:f.write(json.dumps(dict(phase=phase,wall=time.time(),**v))+'\n')
        print(phase,v,flush=True)
    a=inputs();first=invoke(*a,journal=journal);save('C1',first.evidence)
    b=inputs('request:w2:mix','REVISE','MIX_CIRCLES_V01',first.evidence['artifact']['artifact_id']);second=invoke(*b,journal=journal);save('C2',second.evidence)
    v=inputs('request:w2:validate','VALIDATE_EXISTING',parent=first.evidence['artifact']['artifact_id']);validated=invoke(*v,existing=first,journal=journal);save('C3',validated.evidence)
    clear=inputs('request:w2:clarify','CLARIFY');clarified=invoke(*clear,journal=journal);save('C4_clarify',clarified)
    bad=deepcopy(a[0].problem().to_plain_v01());bad['problem_revision']=2;bad['parent_problem_ref']=a[0].problem().content_id
    conflict=deepcopy(bad['hard_conditions'][0]);conflict.update(condition_id='condition_conflict',predicate='APART');bad['hard_conditions'].append(conflict)
    negative=inputs('request:w2:contradiction',problem=bad);contradiction=invoke(*negative,journal=journal);save('C4_conflict',contradiction)
    journal('G4_START');optional=allocation.run_diagnostics_v01(first);save('C6_allocation',optional);journal('G4_RETURN')
    journal('MEMORY_START')
    store=memory.WeddingMemoryV01(directory/'local_drs');store.remember_v01(first)
    repeat=store.select_v01(first.owner,1700000001);assert repeat==first.output
    assert store.select_v01(first.owner,1700004000) is None
    assert store.select_v01(replace(first.owner,profile='MIX_CIRCLES_V01'),1700000001) is None
    foreign=first.owner.problem().to_plain_v01();foreign['owner_root_id']='organizer:foreign'
    assert store.select_v01(replace(first.owner,problem_bytes=c.canonical(foreign)),1700000001) is None
    store.remember_negative_v01(negative[0],1700000000)
    assert store.select_v01(negative[0],1700000001,kind='negative_context') is not None
    assert store.select_v01(first.owner,1700000001,kind='negative_context') is None
    corrected=deepcopy(first.owner.problem().to_plain_v01());corrected['problem_revision']=3;corrected['parent_problem_ref']=negative[0].problem().content_id
    recovery_inputs=inputs('request:w2:recovery',kind='REVISE',parent=negative[0].problem().content_id,problem=corrected)
    assert store.select_v01(recovery_inputs[0],1700000001,kind='negative_context') is None
    recovered=invoke(*recovery_inputs,journal=journal);save('C4_recovery',recovered.evidence)
    store.remember_v01(recovered)
    save('C6_memory',store.events)
    journal('MEMORY_RETURN')
    return dict(first=first,second=second,validated=validated,recovered=recovered,clarified=clarified,contradiction=contradiction,optional=optional,store=store,directory=directory,inputs=a)

def test_native_story_profiles_v01(story):
    a,b=story['first'],story['second']
    assert a.output['assignment']!=b.output['assignment']
    assert caps.material(a.outcome.results[1].result.output)['optimization']['qubo_terms']!=caps.material(b.outcome.results[1].result.output)['optimization']['qubo_terms']
    assert a.validate_current(a.owner) and b.validate_current(b.owner)

def test_native_validate_only_v01(story):
    run=story['validated'];assert [x.work_id for x in run.outcome.results]==['validate','consume']
    assert run.output['assignment']==story['first'].output['assignment']
    assert 'optimization' not in run.material and 'search_evaluated' not in caps.material(run.outcome.results[-1].result.output)

def test_native_clarify_conflict_v01(story):
    assert story['clarified']['questions']==['question:objective']
    assert story['contradiction']['status']=='UNSAT_SUPPORTED_DIRECT_PAIR' and len(story['contradiction']['condition_witness'])==2
    assert story['first'].validate_current(story['first'].owner)
    assert story['recovered'].validate_current(story['recovered'].owner)

def test_native_supplied_neighbors_v01(story):
    run=story['first'];ctx=n.w.work_continuation_context_v01(run.host,task_id=run.owner.request_ref,expected_revision=run.host.state_revision)
    args=dict(run.common,host_map={run.host.owning_root_id:run.host},review_bindings=run.reviews,continuation_context=ctx)
    controls={}
    controls['missing_producer']=n.w.validate_work_program_result_v01(run.program,run.outcome.results[1:],**args)
    assert not controls['missing_producer'][0]
    bad=list(run.outcome.results);bad[-1]=replace(bad[-1],revision_id='foreign:revision')
    controls['foreign_result']=n.w.validate_work_program_result_v01(run.program,tuple(bad),**args)
    assert not controls['foreign_result'][0]
    bad=list(run.outcome.results)
    bad[0]=replace(bad[0],result=replace(bad[0].result,output=caps.record(dict(run.material,requirements_checked='foreign',contradiction=[]))))
    controls['altered_producer']=n.w.validate_work_program_result_v01(run.program,tuple(bad),**args)
    assert not controls['altered_producer'][0]
    item=run.program.candidate.items[1]
    wrong=replace(item,inputs=(n.w.WorkInputBindingV01('material',n.w.WorkOutputBindingV01('review','absent','TEXT')),))
    altered_candidate=replace(run.program.candidate,items=(run.program.candidate.items[0],wrong,*run.program.candidate.items[2:]))
    controls['wrong_field']=n.w.validate_work_program_candidate_v01(altered_candidate,**run.common)
    assert not controls['wrong_field'][0]
    foreign_program=replace(run.program,topology_artifact=story['second'].program.topology_artifact)
    controls['foreign_topology']=n.w.validate_work_program_result_v01(foreign_program,run.outcome.results,**args)
    assert not controls['foreign_topology'][0]
    altered=deepcopy(run.evidence);altered['results'][-1]['result']['output'][0]['value']=altered['results'][0]['result']['output'][0]['value']
    with pytest.raises(ValueError):supplied.validate_saved_run_v01(altered,owner=run.owner)
    assert run.validate_current(run.owner)
    (story['directory']/'native_refusal_reasons.json').write_text(json.dumps(controls,indent=2,sort_keys=True)+'\n')

def test_native_current_root_output_v01(story):
    run=story['first'];saved=deepcopy(run.output)
    run.output['profile']='MIX_CIRCLES_V01'
    with pytest.raises(ValueError,match='actual_consumed_output'):run.validate_current(run.owner)
    run.output.clear();run.output.update(saved)
    with pytest.raises(ValueError,match='current_owner_context'):run.validate_current(story['second'].owner)
    snapshot=run.source.snapshot
    run.source.snapshot=replace(snapshot,source_revision=snapshot.source_revision+1)
    with pytest.raises(ValueError,match='current_source_snapshot'):run.validate_current(run.owner)
    run.source.snapshot=snapshot
    assert run.validate_current(run.owner)

def test_native_allocation_controls_v01(story):
    proof=story['optional'];budget=proof['budget'];report=proof['allocation']
    assert proof['snapshot']['usage']['compute_units']==6 and len(proof['diagnostics'])==4
    for key in ('available','target'):
        bad=deepcopy(report);bad[key]+=1
        with pytest.raises(ValueError):allocation.validate_reference_allocation_v01(bad,inputs=budget['pressure_inputs'],current_budget_context=budget)
    bad=deepcopy(budget);bad['total']+=1
    with pytest.raises(ValueError):allocation.validate_reference_allocation_v01(report,inputs=budget['pressure_inputs'],current_budget_context=bad)
    allocation.validate_reference_allocation_v01(deepcopy(report),inputs=budget['pressure_inputs'],current_budget_context=budget)
    original=caps.material(story['first'].outcome.results[-1].result.output)
    original['parent_plan_ref']=story['first'].evidence['artifact']['artifact_id']
    bad=deepcopy(proof);bad['results'].pop(1)
    with pytest.raises(ValueError,match='missing_diagnostic_result'):allocation.validate_supplied_diagnostics_v01(bad,expected_material=original)
    assert allocation.validate_supplied_diagnostics_v01(deepcopy(proof),expected_material=original)

def test_native_offline_supplied_v01(story):
    for name in ('first','second','validated','recovered'):
        run=story[name];assert supplied.validate_saved_run_v01(deepcopy(run.evidence),owner=run.owner)['status']=='PASS'
