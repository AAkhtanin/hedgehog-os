"""Wedding-specific captured semantics -> native preparation -> native QPU use."""
from dataclasses import replace
import json
import time
from . import native_contracts_v01 as c, semantic_adapter_v01 as s
from . import runtime_v01 as runtime, qpu_contracts_v01 as q

def preparation_material_v01(intake,records,grid_bytes,*,request_ref,original_bytes):
    c.require(json.loads(original_bytes)==intake['base']==intake['current'],'independent_original_bytes')
    i=s.LiveIntakeV01(original_bytes,original_bytes,intake['request_ref'],intake['safe_intent'],
        permitted_tasks=tuple(intake['permitted_tasks']),permitted_profiles=tuple(intake['permitted_profiles']),
        structural_disclosure=intake['structural_disclosure'],amendment_guests=tuple(intake['amendment_guests']))
    owner,m=s.accepted_material_v01(i,records,origin='CAPTURED_PROVIDER_RESPONSE_REEXECUTION')
    c.require(owner.problem().content_id==q.ORIGINAL_REF and owner.task_kind=='GENERATE','w4_original_generation_only')
    c.require(c.digest(grid_bytes)==q.GRID_SHA256[owner.profile],'pinned_w1_grid')
    grid=json.loads(grid_bytes);selected=grid['selected']
    c.require(selected==min(grid['rows'],key=lambda r:(r['loss_key'],r['gamma_index'],r['beta_index'])),'recorded_grid_argmin')
    m.update(request_ref=request_ref,task_kind='QPU_PREPARE',semantic_parent_ref=c.identity('w3_captured_roles',records),
        historical_semantic_request_ref=owner.request_ref,
        backend_selection=dict(origin='CURRENT_W4_OWNER_INTAKE',backend='LIVE_QPU_EXPLICIT_PROVIDER_BRIDGE',
            prior_work_needs='HISTORICAL_LOCAL_EXACT_NOT_MODEL_QPU_PERMISSION'),
        selected_grid=dict(selected=selected,scale=grid['scale'],encoding_ref=grid['encoding_ref'],source_sha256=c.digest(grid_bytes)),
        origin='CAPTURED_MEANING_CURRENT_W4_NATIVE_NUMERIC')
    return replace(owner,request_ref=request_ref,task_kind='QPU_PREPARE'),m

def prepare_v01(owner,material,*,journal=lambda *a,**k:None):
    return runtime._execute_material_v01(owner,material,now=int(time.time()),journal=journal)

def consume_v01(prepared,raw,task_arn,*,allow_suboptimal,submission=None,journal=lambda *a,**k:None):
    c.require(type(prepared) is runtime.NativeRunV01 and prepared.owner.task_kind=='QPU_PREPARE','actual_preparation_producer')
    prepared.validate_current(prepared.owner)
    c.require(prepared.output==q.numeric_v01(prepared.material),'prepared_output_substituted')
    c.require(type(submission) is dict and submission['task_arn']==task_arn and submission['raw_sha256']==c.digest(raw),'bound_provider_submission')
    c.require(submission['state']=='COMPLETED_RAW' and submission['metadata']['status']=='COMPLETED','completed_provider_return')
    q.check_program_v01(prepared.material,prepared.output,submission['request']['action'].encode())
    request_ref=prepared.owner.request_ref+':raw-consumption'
    m=dict(prepared.material,request_ref=request_ref,task_kind='QPU_CONSUME',numeric_parent=prepared.output,
        prepare_material=prepared.material,prepare_result_ref=prepared.evidence['artifact']['artifact_id'],
        prepare_output_sha256=c.digest(prepared.output),raw_result=raw.decode(),task_arn=task_arn,
        submission_request_sha256=submission['request_sha256'],submission_metadata=submission['metadata'],
        submission_prepare_result_ref=submission['approval']['native_prepare_result_ref'],
        requested_shots=1000,allow_suboptimal=allow_suboptimal,origin='QPU_RAW_DECODED_CURRENT_NATIVE_CONSUMPTION')
    _,report=q.consumed_v01(m)
    owner=replace(prepared.owner,request_ref=request_ref,task_kind='QPU_CONSUME',parent_ref=prepared.evidence['artifact']['artifact_id'])
    return runtime._execute_material_v01(owner,m,now=int(time.time()),journal=journal),report
