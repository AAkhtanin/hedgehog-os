"""Pure supplied domain proof; no Root, Host, solver, transport or DRS writes."""
import json
from . import native_contracts_v01 as c,math_v01 as math

def validate_saved_run_v01(evidence,*,owner):
    try:
        return _validate_saved_run_v01(evidence,owner=owner)
    except (KeyError,TypeError,IndexError,AttributeError,json.JSONDecodeError) as error:
        raise ValueError('supplied_shape') from error

def _validate_saved_run_v01(evidence,*,owner):
    problem=owner.problem();p=problem.to_plain_v01()
    c.require(evidence['owner']==dict(problem=p,request_ref=owner.request_ref,task_kind=owner.task_kind,profile=owner.profile,parent_ref=owner.parent_ref),'supplied_owner')
    material=evidence['material']
    c.require(material['problem']==p and material['profile']==owner.profile and material['request_ref']==owner.request_ref,'supplied_original')
    results=evidence['results'];items=evidence['program']['candidate']['items']
    names=['review','compile','solve','validate','consume'] if owner.task_kind in ('GENERATE','REVISE') else ['validate','consume']
    c.require([i['work_id'] for i in items]==names and [r['work_id'] for r in results]==names,'supplied_work_set')
    previous=None
    for i,(item,result) in enumerate(zip(items,results)):
        c.require(result['status']=='COMPLETED','supplied_completed')
        incoming=json.loads(result['invocation']['inputs'][0]['value'])
        output=json.loads(result['result']['output'][0]['value'])
        c.require(incoming==(material if i==0 else previous),'supplied_actual_parent_value')
        c.require(output['problem']==p and output['profile']==owner.profile and output['request_ref']==owner.request_ref,'supplied_output_context')
        if i:
            c.require(item['inputs'][0]['source']==dict(predecessor_work_id=names[i-1],output_field='material',expected_type='TEXT'),'supplied_output_binding')
            c.require(bool(result['consumed_fields']),'supplied_causal_consumption')
        if item['work_id']=='review':c.require(output['requirements_checked']==problem.content_id and not output['contradiction'],'supplied_requirement')
        if item['work_id']=='compile':
            c.require(output['optimization']==math.compile_optimization_v01(problem,owner.profile).to_plain_v01(),'supplied_compilation')
        if item['work_id'] in ('solve','validate','consume'):
            report=math.validate_assignment_v01(problem,output['assignment'],owner.profile).to_plain_v01()
            c.require(report['status']=='VALID','supplied_original_conditions')
            if item['work_id']!='solve':c.require(output['validation']==report,'supplied_validation_report')
        if item['work_id']=='consume':
            expected=dict(assignment=output['assignment'],profile=owner.profile,problem_ref=problem.content_id,request_ref=owner.request_ref)
            c.require(output['safe_output']==expected,'supplied_displayed_plan')
        previous=output
    c.require(evidence['output']==previous['safe_output'],'supplied_final_consumer')
    c.require(evidence['root_result']['decision']=='ACCEPT' and evidence['root_result']['selected_candidate_id']==c.identity('wedding_result',evidence['output']),'supplied_root_binding')
    return dict(status='PASS',classification='PURE_SUPPLIED_DOMAIN_PROOF_NOT_NATIVE_GRAPH_REPLAY',new_solver_calls=0,new_root_calls=0,new_host_calls=0)
