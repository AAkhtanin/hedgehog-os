"""Finite PURE catalogue. The performed executors compute Wedding results."""
import json
from hedgehog import action_commit_packet_v02 as action, work_execution_host_v01 as host
from hedgehog.kernel import effect_firewall_v01 as firewall
from . import native_contracts_v01 as c, math_v01 as math

def record(value):
    return (action.build_action_effect_parameter_record_v01(parameter_name='material',value_type='TEXT',value=c.canonical(value).decode()),)
def values(records):return {r.parameter_name:r.value for r in records}
def material(records):return json.loads(values(records)['material'])

def validate_inputs(definition, inputs):
    errors=firewall.validate_capability_values_v01(definition.input_fields,inputs)
    if not errors:
        try:
            m=material(inputs);c.problem_from_material(m);c.require(m['profile'] in math.PROFILES if hasattr(math,'PROFILES') else m['profile'] in ('KEEP_FAMILIAR_V01','MIX_CIRCLES_V01'),'profile')
        except (ValueError,TypeError,KeyError):errors=('wedding_input',)
    return firewall.build_capability_validation_evidence_v01(definition=definition,values=inputs,invocation_id=None,valid=not errors,reason_codes=errors)

def review_requirements(invocation):
    m=material(invocation.inputs);p=c.problem_from_material(m)
    m['contradiction']=math.contradiction_witness_v01(p)
    c.require(not m['contradiction'],'contradictory_conditions')
    m['requirements_checked']=p.content_id
    return record(m)

def compile_problem(invocation):
    m=material(invocation.inputs);p=c.problem_from_material(m)
    c.require(m['requirements_checked']==p.content_id,'requirements_parent')
    m['optimization']=math.compile_optimization_v01(p,m['profile']).to_plain_v01()
    return record(m)

def solve_problem(invocation):
    m=material(invocation.inputs);p=c.problem_from_material(m)
    expected=math.compile_optimization_v01(p,m['profile']).to_plain_v01()
    c.require(m['optimization']==expected,'compiled_parent')
    result=math.ProblemMathV01(p).solve(m['profile'])
    c.require(result['status']=='FEASIBLE','no_feasible_plan')
    m['assignment']=list(result['selected']);m['search_evaluated']=result['evaluated']
    return record(m)

def validate_original(invocation):
    m=material(invocation.inputs);p=c.problem_from_material(m)
    m['validation']=math.validate_assignment_v01(p,m['assignment'],m['profile']).to_plain_v01()
    c.require(m['validation']['status']=='VALID','original_conditions_failed')
    return record(m)

def consume_plan(invocation):
    m=material(invocation.inputs);p=c.problem_from_material(m)
    expected=math.validate_assignment_v01(p,m['assignment'],m['profile']).to_plain_v01()
    c.require(m['validation']==expected and expected['status']=='VALID','validation_parent')
    m['safe_output']=dict(assignment=m['assignment'],profile=m['profile'],problem_ref=p.content_id,request_ref=m['request_ref'])
    return record(m)

def table_diagnostic(m,family,table):
    p=c.problem_from_material(m).to_plain_v01();assignment=m['assignment']
    guests=[g for g,t in zip(p['guest_ids'],assignment) if t==table]
    familiar={tuple(x) for x in p['familiarity_pairs']}
    pairs=[(a,b) for i,a in enumerate(guests) for b in guests[i+1:]]
    count=sum((a,b) in familiar for a,b in pairs)
    return dict(family=family,table=p['table_records'][table]['table_id'],guest_ids=guests,
        pair_count=len(pairs),value=count if family=='COHESION_EXPLANATION' else len(pairs)-count)

def diagnostic(invocation,family,table):
    m=material(invocation.inputs)
    row=table_diagnostic(m,family,table)
    m['diagnostics']=[*m.get('diagnostics',[]),row]
    return record(m)

def cohesion_0(invocation):return diagnostic(invocation,'COHESION_EXPLANATION',0)
def cohesion_1(invocation):return diagnostic(invocation,'COHESION_EXPLANATION',1)
def cohesion_2(invocation):return diagnostic(invocation,'COHESION_EXPLANATION',2)
def mixing_0(invocation):return diagnostic(invocation,'MIXING_EXPLANATION',0)
def mixing_1(invocation):return diagnostic(invocation,'MIXING_EXPLANATION',1)
def mixing_2(invocation):return diagnostic(invocation,'MIXING_EXPLANATION',2)

def qpu_prepare(invocation):
    from . import qpu_contracts_v01 as q
    m=material(invocation.inputs);p=c.problem_from_material(m)
    c.require(m['optimization']==math.compile_optimization_v01(p,m['profile']).to_plain_v01(),'compiled_parent')
    m['safe_output']=q.numeric_v01(m);q.check_numeric_v01(m,m['safe_output'])
    return record(m)

def qpu_validate(invocation):
    from . import qpu_contracts_v01 as q
    m=material(invocation.inputs);_,report=q.consumed_v01(m)
    m['sample_validation']=report
    return record(m)

def qpu_consume(invocation):
    from . import qpu_contracts_v01 as q
    m=material(invocation.inputs);output,report=q.consumed_v01(m)
    c.require(m['sample_validation']==report,'actual_sample_validation_parent')
    m['safe_output']=output;m['assignment']=output['assignment']
    m['validation']=report['selected']['validation']
    return record(m)

def validate_outputs(definition, invocation, output):
    errors=firewall.validate_capability_values_v01(definition.output_fields,output)
    if not errors:
        try:
            before=material(invocation.inputs);after=material(output)
            c.require(all(after.get(k)==v for k,v in before.items() if k!='diagnostics'),'producer_changed_input')
            p=c.problem_from_material(after)
            op=definition.operation_id
            if op=='wedding.review':c.require(after['requirements_checked']==p.content_id and not after['contradiction'],'requirements_output')
            elif op=='wedding.compile':c.require(after['optimization']==math.compile_optimization_v01(p,after['profile']).to_plain_v01(),'compiler_output')
            elif op in ('wedding.solve','wedding.validate','wedding.consume'):
                check=math.validate_assignment_v01(p,after['assignment'],after['profile']).to_plain_v01()
                c.require(check['status']=='VALID','original_output')
                if op!='wedding.solve':c.require(after['validation']==check,'validation_output')
                if op=='wedding.consume':c.require(after['safe_output']==dict(assignment=after['assignment'],profile=after['profile'],problem_ref=p.content_id,request_ref=after['request_ref']),'consumer_output')
            elif op=='wedding.qpu_prepare':
                from . import qpu_contracts_v01 as q
                q.check_numeric_v01(before,after['safe_output'])
            elif op in ('wedding.qpu_validate','wedding.qpu_consume'):
                from . import qpu_contracts_v01 as q
                expected,report=q.consumed_v01(before)
                c.require(after['sample_validation']==report,'sample_validation_output')
                if op.endswith('consume'):c.require(after['safe_output']==expected and after['assignment']==expected['assignment'] and after['validation']==report['selected']['validation'],'raw_consumer_output')
            elif op.startswith('wedding.cohesion_') or op.startswith('wedding.mixing_'):
                family='COHESION_EXPLANATION' if 'cohesion' in op else 'MIXING_EXPLANATION'
                c.require(after['diagnostics']==[*before.get('diagnostics',[]),table_diagnostic(before,family,int(op[-1]))],'diagnostic_output')
            else:raise ValueError('unknown_operation')
            if not ('cohesion_' in op or 'mixing_' in op):c.require(after.get('diagnostics')==before.get('diagnostics'),'diagnostics_preserved')
        except (ValueError,TypeError,KeyError):errors=('wedding_output',)
    return firewall.build_capability_validation_evidence_v01(definition=definition,values=output,invocation_id=invocation.invocation_id,valid=not errors,reason_codes=errors)

def catalogue_v01(host_ref):
    result=[]
    for name,executor in (('review',review_requirements),('compile',compile_problem),('solve',solve_problem),('validate',validate_original),('consume',consume_plan),
        ('cohesion_0',cohesion_0),('cohesion_1',cohesion_1),('cohesion_2',cohesion_2),('mixing_0',mixing_0),('mixing_1',mixing_1),('mixing_2',mixing_2),
        ('qpu_prepare',qpu_prepare),('qpu_validate',qpu_validate),('qpu_consume',qpu_consume)):
        functions=(validate_inputs,validate_outputs,executor)
        observed=tuple(host.observe_local_capability_code_v01(f) for f in functions)
        fields=(firewall.build_capability_field_v01(name='material',value_type='TEXT',required=True,consequential=False),)
        definition=firewall.build_capability_definition_v01(operation_id='wedding.'+name,version='v01',effect_kind='PURE',business_semantics=None,
            input_fields=fields,output_fields=fields,resource_refs=(),input_validator_ref=observed[0].public_symbol,
            output_validator_ref=observed[1].public_symbol,executor_ref=observed[2].public_symbol,
            code_sha256s=tuple((o.public_symbol,o.source_sha256) for o in observed))
        result.append(host.admit_local_capability_v01(definition=definition,input_validator=validate_inputs,output_validator=validate_outputs,
            executor=executor,catalogue_revision=0,host_instance_ref=host_ref))
    return tuple(result)
