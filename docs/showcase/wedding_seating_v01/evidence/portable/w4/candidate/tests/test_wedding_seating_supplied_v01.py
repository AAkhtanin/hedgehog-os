"""Saved source-bound consumers and a fresh two-dispatch currentness control.

The explicit evidence path avoids recollecting the already completed D story.
These checks do not call a solver or recreate historical Host authority.
"""
from copy import deepcopy
from dataclasses import replace
import importlib.util
import json
import os
from pathlib import Path
import pytest
from hedgehog.domains.wedding_seating import native_contracts_v01 as c,native_capabilities_v01 as caps,native_adapter_v01 as n,runtime_v01 as r,supplied_v01 as supplied,allocation_v01 as allocation

def helpers():
    spec=importlib.util.spec_from_file_location('wedding_native_test_inputs',Path(__file__).with_name('test_wedding_seating_native_v01.py'))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module

@pytest.fixture(scope='module')
def saved():
    directory=Path(os.environ['W2_SAVED_STORY'])
    data={k:json.loads((directory/(k+'.json')).read_text()) for k in ('C1','C2','C3','C4_recovery','C6_allocation','C6_memory')}
    h=helpers();a=h.inputs()[0]
    b=h.inputs('request:w2:mix','REVISE','MIX_CIRCLES_V01',data['C1']['artifact']['artifact_id'])[0]
    v=h.inputs('request:w2:validate','VALIDATE_EXISTING',parent=data['C1']['artifact']['artifact_id'])[0]
    conflict=a.problem().to_plain_v01();conflict['problem_revision']=2;conflict['parent_problem_ref']=a.problem().content_id
    condition=deepcopy(conflict['hard_conditions'][0]);condition.update(condition_id='condition_conflict',predicate='APART');conflict['hard_conditions'].append(condition)
    negative=h.inputs('request:w2:contradiction',problem=conflict)[0]
    corrected=a.problem().to_plain_v01();corrected['problem_revision']=3;corrected['parent_problem_ref']=negative.problem().content_id
    recover=h.inputs('request:w2:recovery','REVISE',parent=negative.problem().content_id,problem=corrected)[0]
    return data,dict(C1=a,C2=b,C3=v,C4_recovery=recover)

def test_saved_native_original_and_edges_v01(saved):
    data,owners=saved
    reports={}
    for key,owner in owners.items():reports[key]=supplied.validate_saved_run_v01(deepcopy(data[key]),owner=owner)
    assert data['C1']['output']['assignment']!=data['C2']['output']['assignment']
    assert data['C3']['output']['assignment']==data['C1']['output']['assignment']
    assert [r['work_id'] for r in data['C3']['results']]==['validate','consume']
    Path(os.environ['W2_COMMAND'],'saved_positive.json').write_text(json.dumps(reports,indent=2)+'\n')

def test_saved_changed_producer_refusal_v01(saved):
    data,owners=saved;original=data['C1'];owner=owners['C1'];reasons={}
    for kind in ('missing','altered','wrong_field','foreign_output','source','root'):
        bad=deepcopy(original)
        if kind=='missing':bad['results'].pop(0)
        elif kind=='altered':bad['results'][-1]['result']['output'][0]['value']=bad['results'][0]['result']['output'][0]['value']
        elif kind=='wrong_field':bad['program']['candidate']['items'][1]['inputs'][0]['source']['output_field']='absent'
        elif kind=='foreign_output':bad['output']=data['C2']['output']
        elif kind=='source':bad['material']['problem']['hard_conditions'].pop(6)
        else:bad['root_result']=data['C2']['root_result']
        with pytest.raises(ValueError) as error:supplied.validate_saved_run_v01(bad,owner=owner)
        reasons[kind]=str(error.value)
    assert supplied.validate_saved_run_v01(deepcopy(original),owner=owner)['status']=='PASS'
    Path(os.environ['W2_COMMAND'],'saved_refusals.json').write_text(json.dumps(reasons,indent=2)+'\n')

def test_saved_allocation_and_memory_consumption_v01(saved):
    data,_=saved
    proof=data['C6_allocation'];budget=proof['budget'];original=json.loads(data['C1']['results'][-1]['result']['output'][0]['value'])
    original['parent_plan_ref']=data['C1']['artifact']['artifact_id']
    assert allocation.validate_supplied_diagnostics_v01(deepcopy(proof),expected_material=original)
    assert proof['snapshot']['usage']['compute_units']==6 and len(proof['diagnostics'])==4
    reasons={}
    for kind in ('excess','foreign_budget','missing_diagnostic','altered_diagnostic'):
        bad=deepcopy(proof)
        if kind=='excess':bad['allocation']['target']+=1
        elif kind=='foreign_budget':bad['budget']['total']+=1
        elif kind=='missing_diagnostic':bad['results'].pop(1)
        else:bad['diagnostics'][0]['value']+=1
        with pytest.raises(ValueError) as error:allocation.validate_supplied_diagnostics_v01(bad,expected_material=original)
        reasons[kind]=str(error.value)
    queries=[x for x in data['C6_memory'] if x['op']=='QUERY']
    assert any('descent' in x for x in queries) and any('descent' not in x for x in queries)
    assert len([x for x in data['C6_memory'] if x['op']=='WRITE'])==3
    Path(os.environ['W2_COMMAND'],'allocation_refusals.json').write_text(json.dumps(reasons,indent=2)+'\n')

def test_fresh_native_current_source_and_root_v01(saved):
    data,_=saved;h=helpers();owner,responses,kw=h.inputs('request:w2:current_control','VALIDATE_EXISTING')
    supplied.validate_saved_run_v01(data['C1'],owner=saved[1]['C1'])
    material=c.consume_semantics_v01(owner,owner.problem_bytes,[c.canonical(x) for x in responses],**kw)
    material.update(assignment=list(data['C1']['output']['assignment']),existing_result_ref=data['C1']['artifact']['artifact_id'])
    now=1700000000;task=owner.request_ref;root=owner.problem().to_plain_v01()['owner_root_id'];hostref='host:'+task
    source,_=n.semantic_source(owner.approved_intent,task,root,now,material['semantics'][0]);cat=caps.catalogue_v01(hostref)
    proposal=n.abi.build_kernel_artifact_v01(abi_version='v1.0',artifact_id=c.identity('semantic_current_control',material),artifact_type='SemanticArchitectProposal',schema_version='v1',transaction_id='transaction:'+task,owner_root_id=root,
        source_component='semantic_architect',authority_class='ADVISORY',lifecycle_state='PROPOSED',payload=material,trace_refs=('intent:'+task,),parent_refs=(source.bsep_packet['packet_id'],),
        time_envelope=dict(pt_created_at=n.stamp(now),kt_asof=n.stamp(now),et_observed_at=None,ct_session_anchor=task,ttl_seconds=3600,freshness_class='static',valid_from=n.stamp(now),valid_to=n.stamp(now+3600)))
    common=dict(catalogue=cat,source_context=source,semantic_proposal=proposal);defs={x.definition.operation_id:x.definition.definition_id for x in cat}
    items=(n.w.WorkItemV01('validate',defs['wedding.validate'],root,(n.w.WorkInputBindingV01('material',n.w.WorkLiteralV01(caps.record(material)[0])),),(),(),None,None),
        n.w.WorkItemV01('consume',defs['wedding.consume'],root,(n.w.WorkInputBindingV01('material',n.w.WorkOutputBindingV01('validate','material','TEXT')),),(),('validate',),None,None))
    candidate=n.w.build_work_program_candidate_v01(task_id=task,previous_revision_id=None,intent_ref='intent:'+task,bsep_ref=source.bsep_packet['packet_id'],semantic_proposal_ref=proposal.artifact_id,catalogue_revision=0,budget=n.w.WorkBudgetV01(2,0,0,2,0),items=items,trigger_evidence_refs=(),**common)
    program=n.w.materialize_work_program_v01(candidate,**common)
    policy=n.w.build_work_task_policy_v01(candidate,**common,host_instance_ref=hostref,definition_ids=tuple(sorted(defs.values())),resource_refs=())
    clock=r.ControlledSourceV01(now)
    host=n.hosts.build_root_work_execution_host_v01(owning_root_id=root,registry=n.a.build_empty_action_commit_packet_registry_v02(),catalogue=cat,packet_bindings=(),current_dependency_observations=(),logical_time_bridge=clock.snapshot.logical_time_bridge,trusted_source=clock,task_policies=(policy,))
    context=n.w.enroll_work_program_v01(host,program,**common,expected_revision=host.state_revision)
    outcome=n.w.advance_work_program_v01(program,**common,host_map={root:host},continuation_context=context)
    assert outcome.status=='COMPLETED'
    output=caps.material(outcome.results[-1].result.output)['safe_output']
    decision=n.root_review(root,'transaction:'+task,c.identity('wedding_result',output),task,dict(actual_validation=caps.material(outcome.results[-1].result.output)['validation']['status']=='VALID'),outcome.results[-1].result.result_id,candidate.bsep_ref,program.topology_artifact.artifact_id,now,claim_value=output)
    evidence=dict(now=now,host_revision=host.state_revision,trusted_source=r.plain(host.current_sources))
    run=r.NativeRunV01(owner,material,common,program,host,clock,outcome,(),decision,output,evidence)
    assert run.validate_current(owner);reasons={}
    saved_output=deepcopy(output);output['profile']='MIX_CIRCLES_V01'
    with pytest.raises(ValueError) as error:run.validate_current(owner)
    reasons['changed_output']=str(error.value);output.clear();output.update(saved_output)
    for key in ('source_revision','evaluation_time'):
        old=clock.snapshot;clock.snapshot=replace(old,**{key:getattr(old,key)+1})
        with pytest.raises(ValueError) as error:run.validate_current(owner)
        reasons[key]=str(error.value);clock.snapshot=old
    with pytest.raises(ValueError) as error:run.validate_current(replace(owner,request_ref='request:foreign'))
    reasons['foreign_request']=str(error.value)
    context=n.w.work_continuation_context_v01(host,task_id=task,expected_revision=host.state_revision)
    args=dict(common,host_map={root:host},continuation_context=context)
    negatives=dict(missing_producer=outcome.results[1:],altered_producer=(replace(outcome.results[0],result=replace(outcome.results[0].result,output=caps.record(dict(material,assignment=[0]*12)))),outcome.results[1]),foreign_result=(replace(outcome.results[0],revision_id='foreign:revision'),outcome.results[1]))
    for key,results in negatives.items():
        check=n.w.validate_work_program_result_v01(program,results,**args);assert not check[0];reasons[key]=check[1]
    wrong=replace(items[1],inputs=(n.w.WorkInputBindingV01('material',n.w.WorkOutputBindingV01('validate','absent','TEXT')),))
    check=n.w.validate_work_program_candidate_v01(replace(candidate,items=(items[0],wrong)),**common);assert not check[0];reasons['wrong_field']=check[1]
    foreign_fields=deepcopy(data['C2']['program']['topology_artifact'])
    foreign_fields['trace_refs']=tuple(foreign_fields['trace_refs']);foreign_fields['parent_refs']=tuple(foreign_fields['parent_refs'])
    foreign=n.abi.build_kernel_artifact_v01(**foreign_fields)
    check=n.w.validate_work_program_result_v01(replace(program,topology_artifact=foreign),outcome.results,**args);assert not check[0];reasons['foreign_topology']=check[1]
    assert run.validate_current(owner)
    Path(os.environ['W2_COMMAND'],'fresh_current_control.json').write_text(json.dumps(dict(program=r.plain(program),results=r.plain(outcome.results),policy=r.plain(policy),root=r.plain(decision[2]),reasons=reasons,native_tasks=1,native_dispatches=2,D_calls=0,solver_calls=0),indent=2,sort_keys=True)+'\n')
