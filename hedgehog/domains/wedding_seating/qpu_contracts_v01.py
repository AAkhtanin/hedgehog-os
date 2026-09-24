"""Pure Wedding QPU numeric preparation and raw-sample consumption.

No credential discovery, network, solver search or authority restoration.
"""
import json
import math as scalar
from . import native_contracts_v01 as c, math_v01 as maths
from . import encoding_v02 as encoding, circuit_v02 as circuits

PROFILES=('KEEP_FAMILIAR_V01','MIX_CIRCLES_V01')
ANGLES={'KEEP_FAMILIAR_V01':(9,22),'MIX_CIRCLES_V01':(16,22)}
GRID_SHA256={'KEEP_FAMILIAR_V01':'1668e5846d919b040f935f620753da93e6bec94373fac381dc11c07749df2c9d',
    'MIX_CIRCLES_V01':'39726a1a1f79324ad53c95d638a2ae937b00e5f66ec5bc2db856d48d9a628b0c'}
ORIGINAL_REF='16704ff36b942ba84ca41618bf59da407478c1e1a3ef7fa3779990fdea432c17'

def numeric_v01(material):
    p=c.problem_from_material(material);profile=material['profile']
    c.require(p.content_id==ORIGINAL_REF,'w4_original_fixture_only')
    c.require(profile in PROFILES,'qpu_profile')
    encs=tuple(encoding.compile_encoding_v02(p,x) for x in PROFILES)
    scale=encoding.common_scale_v02(encs)
    c.require(scale==4096,'exact_common_scale')
    enc=encs[PROFILES.index(profile)];j,k=ANGLES[profile]
    return dict(problem_ref=p.content_id,profile=profile,optimization=maths.compile_optimization_v01(p,profile).to_plain_v01(),
        encoding=enc.to_plain_v01(),descriptor=circuits.circuit_descriptor_v02(enc,scale,j,k).to_plain_v01(),
        selected_grid=material['selected_grid'],backend='LIVE_QPU_EXPLICIT_PROVIDER_BRIDGE',
        semantic_parent_ref=material['semantic_parent_ref'],request_ref=material['request_ref'])

def check_numeric_v01(material,value):
    c.require(value==numeric_v01(material),'exact_numeric_source_binding')
    grid=value['selected_grid'];j,k=ANGLES[material['profile']]
    c.require(grid['selected']['gamma_index']==j and grid['selected']['beta_index']==k and grid['scale']==4096,'recorded_grid_selection')
    enc=encoding.compile_encoding_v02(c.problem_from_material(material),material['profile'])
    c.require(grid['encoding_ref']==enc.content_id and grid['source_sha256']==GRID_SHA256[material['profile']],'recorded_grid_source')
    return enc

def check_program_v01(material,numeric,raw):
    enc=check_numeric_v01(material,numeric);j,k=ANGLES[material['profile']]
    ops,measurement=circuits.parse_openqasm_program_v02(raw)
    expected=circuits.gate_operations_v02(enc,4096,scalar.pi*j/2,scalar.pi*k/24)
    c.require(ops==expected and measurement==tuple((q,q) for q in range(10)),'compiled_gate_or_measurement_substitution')
    return enc

def samples_v01(material,numeric,raw,*,task_arn,shots=1000,allow_suboptimal=True):
    enc=check_numeric_v01(material,numeric);p=c.problem_from_material(material)
    c.require(type(raw) is bytes and len(raw)<=8*1024*1024,'result_size')
    def pairs(items):
        result={}
        for key,value in items:
            c.require(key not in result,'duplicate_result_key');result[key]=value
        return result
    data=json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda value:(_ for _ in ()).throw(ValueError('nonfinite_result')))
    c.require(data['braketSchemaHeader']['name']=='braket.task_result.gate_model_task_result','result_schema')
    meta=data['taskMetadata']
    c.require(meta['id']==task_arn and type(meta['shots']) is int and meta['shots']==shots,'result_task_shots')
    rows=data['measurements'];qubits=data['measuredQubits']
    c.require(type(rows) is list and 0<len(rows)<=shots,'measurement_rows')
    successful=meta.get('numSuccessfulShots',data.get('numSuccessfulShots',shots))
    c.require(type(successful) is int and successful==len(rows) and (successful==shots or successful<shots),'successful_shots')
    # Every row is decoded from its real logical-qubit column mapping, never from a feasible-plan index.
    lineage=[];valid=[];counts={}
    for i,row in enumerate(rows):
        index=encoding.measurement_index_v02(row,qubits)
        assignment,_=encoding.decode_basis_v02(enc,index)
        if -1 in assignment:status='INVALID_CODE_3';report=None
        else:
            report=maths.validate_assignment_v01(p,assignment,material['profile']).to_plain_v01();status=report['status']
        item=dict(shot_index=i,basis_index=index,assignment=list(assignment),status=status,validation=report)
        lineage.append(item);counts[str(index)]=counts.get(str(index),0)+1
        if status=='VALID':valid.append(item)
    selected=min(valid,key=lambda r:(r['validation']['components']['objective'],r['assignment'],r['shot_index'])) if valid else None
    if selected and not allow_suboptimal:c.require(selected['validation']['components']['objective']==0,'suboptimal_not_permitted')
    return dict(status='VALIDATED_RAW_SAMPLE' if selected else 'NO_VALID_PROVIDER_SAMPLE',raw_sha256=c.digest(raw),task_arn=task_arn,
        requested_shots=shots,successful_shots=len(rows),measured_qubits=qubits,valid_samples=len(valid),
        distinct_valid_plans=len({tuple(row['assignment']) for row in valid}),
        invalid_samples=len(rows)-len(valid),basis_counts=counts,lineage=lineage,selected=selected,
        local_reference_objective=0,objective_gap=selected['validation']['components']['objective'] if selected else None,
        postselection='CLASSICAL_OBJECTIVE_THEN_ASSIGNMENT_THEN_SHOT',local_repair=False)

def consumed_v01(material):
    parent=material['prepare_material']
    c.require(parent['problem']==material['problem'] and parent['profile']==material['profile'],'current_original_profile')
    c.require(material['prepare_result_ref'] and material['prepare_output_sha256']==c.digest(material['numeric_parent']),'required_prepare_result')
    report=samples_v01(parent,material['numeric_parent'],material['raw_result'].encode(),task_arn=material['task_arn'],
        shots=material['requested_shots'],allow_suboptimal=material['allow_suboptimal'])
    c.require(report['selected'] is not None,'NO_VALID_PROVIDER_SAMPLE')
    return dict(assignment=report['selected']['assignment'],profile=material['profile'],problem_ref=c.problem_from_material(material).content_id,
        request_ref=material['request_ref'],task_arn=material['task_arn'],raw_sha256=report['raw_sha256'],
        shot_index=report['selected']['shot_index'],basis_index=report['selected']['basis_index'],
        objective_gap=report['objective_gap'],origin='LIVE_QPU_RAW_DECODED_POSTSELECTED',local_repair=False),report

def clarification_v01(unresolved):
    return dict(unresolved_ids=list(unresolved),rendering_origin='LOCAL_RENDERING',questions=[
        'Should I keep familiar circles together or mix the circles across tables?' if x=='objective' else x for x in unresolved])
