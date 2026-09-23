"""Real enrolled missing Work and finite sacrificial-code admission controls."""
from dataclasses import asdict
import importlib.util
import json
from pathlib import Path
import sys
from hedgehog import action_commit_packet_v02 as action, work_execution_host_v01 as hosts
from hedgehog import outcome_feedback_v01 as feedback
from hedgehog.kernel import abi_v01 as abi, work_composition_v01 as work, effect_firewall_v01 as fw
from . import contracts_v01 as c, capability_registry_v01 as caps, kernel_adapter_v01 as kernel
from .incident_atlas_source_v01 import current_source_v01


def prepare_v01(session):
    task='atlas:required:'+session.id
    catalogue=(caps.admit(session.root,'ews.contract.v01',caps.execute_contract_v01),)
    clock=session.source.sample()
    material=dict(session=session.id,version=session.version,source_hashes=session.source_hashes,contract=session.contract)
    source=current_source_v01(task,clock,material)
    stamp=feedback._utc
    proposal=abi.build_kernel_artifact_v01(abi_version='v1.0',artifact_id=c.identity('required_proposal',material),
        artifact_type='SemanticArchitectProposal',schema_version='v1',transaction_id='transaction:'+task,
        owner_root_id=session.root,source_component='semantic_architect',authority_class='ADVISORY',lifecycle_state='PROPOSED',
        payload=material,trace_refs=('intent:'+task,),parent_refs=(source.bsep_packet['packet_id'],),
        time_envelope=dict(pt_created_at=stamp(clock.evaluation_time),kt_asof=stamp(clock.evaluation_time),et_observed_at=None,
            ct_session_anchor=task,ttl_seconds=1200,freshness_class='static',valid_from=stamp(clock.evaluation_time),valid_to=stamp(clock.evaluation_time+1200)))
    common=dict(catalogue=catalogue,source_context=source,semantic_proposal=proposal)
    item=work.WorkItemV01('required_current_contract',catalogue[0].definition.definition_id,session.root,
        (work.WorkInputBindingV01('material',work.WorkLiteralV01(caps.records(dict(material=('TEXT',c.canonical(session.contract).decode())))[0])),),(),(),None,None)
    candidate=work.build_work_program_candidate_v01(task_id=task,previous_revision_id=None,intent_ref='intent:'+task,
        bsep_ref=source.bsep_packet['packet_id'],semantic_proposal_ref=proposal.artifact_id,catalogue_revision=0,
        budget=work.WorkBudgetV01(1,0,0,1,0),items=(item,),trigger_evidence_refs=(),**common)
    program=work.materialize_work_program_v01(candidate,**common)
    policy=work.build_work_task_policy_v01(candidate,host_instance_ref='host:'+session.root,
        definition_ids=(catalogue[0].definition.definition_id,),resource_refs=(),**common)
    host=hosts.build_root_work_execution_host_v01(owning_root_id=session.root,registry=action.build_empty_action_commit_packet_registry_v02(),
        catalogue=catalogue,packet_bindings=(),current_dependency_observations=(),logical_time_bridge=clock.logical_time_bridge,
        trusted_source=session.source,task_policies=(policy,))
    context=work.enroll_work_program_v01(host,program,expected_revision=host.revision,**common)
    return dict(host=host,program=program,context=context,common=common,session=session.id,version=session.version,material=material)


def snapshot_v01(task):
    host=task['host'];task_id=task['program'].candidate.task_id
    snapshot=work.inspect_work_task_v01(host,task_id=task_id)
    c.require(work.validate_work_task_snapshot_v01(snapshot,host=host)[0],'atlas_required_snapshot')
    context=work.work_continuation_context_v01(host,task_id=task_id,expected_revision=host.revision)
    rows=work.inspect_work_task_history_v01(context)
    return dict(snapshot=asdict(snapshot),program=feedback.g35_record_to_plain_v01(task['program']),
        results=feedback.g35_record_to_plain_v01(rows[-1][1]),
        artifact=None if rows[-1][2] is None else abi.kernel_artifact_to_plain_dict_v01(rows[-1][2]),
        admissions=feedback.g35_record_to_plain_v01(tuple(fw.snapshot_admitted_capability_v01(a) for a in task['common']['catalogue'])),
        session=task['session'],version=task['version'],proposal=abi.kernel_artifact_to_plain_dict_v01(task['common']['semantic_proposal']),
        work_attempts=[asdict(v) for v in host.work_attempts],completed_work=feedback.g35_record_to_plain_v01(host.completed_work))


def complete_v01(task, session, summary_ref):
    c.require(session.id==task['session'] and session.version==task['version'],'atlas_required_current_version')
    reference=c.identity('required_review',dict(task=task['program'].candidate.revision_id,summary_ref=summary_ref))
    review=kernel.root_review(session.root,'transaction:'+task['program'].candidate.task_id,reference,session.id,
        dict(current=session.state()['current'],missing=not snapshot_v01(task)['snapshot']['terminal_history_refs'],
            same_source=session.source_hashes==task['material']['source_hashes']),reference,
        task['program'].candidate.bsep_ref,task['program'].topology_artifact.artifact_id,session.source.sample().evaluation_time,
        claim_value=dict(summary_ref=summary_ref,required_revision=task['program'].candidate.revision_id))
    outcome=work.advance_work_program_v01(task['program'],**task['common'],host_map={session.root:task['host']},continuation_context=task['context'])
    c.require(outcome.status=='COMPLETED','atlas_required_not_completed')
    value=snapshot_v01(task);value['current_review']=feedback.g35_record_to_plain_v01(review)
    return value


SACRIFICIAL_CODE='''"""Disposable finite code identity fixture; not an accepted module."""
from hedgehog.kernel import effect_firewall_v01 as fw
from hedgehog import action_commit_packet_v02 as action
EXECUTOR_ENTRIES=0
def input_v01(definition, inputs):
    errors=fw.validate_capability_values_v01(definition.input_fields,inputs)
    return fw.build_capability_validation_evidence_v01(definition=definition,values=inputs,invocation_id=None,valid=not errors,reason_codes=errors)
def execute_v01(invocation):
    global EXECUTOR_ENTRIES
    EXECUTOR_ENTRIES+=1
    return (action.ActionEffectParameterRecordV01('material','TEXT','original'),)
def output_v01(definition, invocation, output):
    errors=fw.validate_capability_values_v01(definition.output_fields,output)
    if tuple(v.value for v in output)!=('original',):errors+=('fixture_output',)
    return fw.build_capability_validation_evidence_v01(definition=definition,values=output,invocation_id=invocation.invocation_id,valid=not errors,reason_codes=errors)
'''


def code_control_v01(directory, root):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=False)
    path=directory/'atlas_sacrificial_v01.py';path.write_text(SACRIFICIAL_CODE)
    spec=importlib.util.spec_from_file_location('atlas_sacrificial_v01',path)
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    functions=(module.input_v01,module.output_v01,module.execute_v01)
    sources=tuple(hosts.observe_local_capability_code_v01(f) for f in functions)
    definition=fw.build_capability_definition_v01(operation_id='atlas.workspace.familiar_name',version='v01',effect_kind='PURE',business_semantics=None,
        input_fields=(fw.build_capability_field_v01(name='material',value_type='TEXT',required=True,consequential=False),),
        output_fields=(fw.build_capability_field_v01(name='material',value_type='TEXT',required=True,consequential=False),),resource_refs=(),
        input_validator_ref=sources[0].public_symbol,output_validator_ref=sources[1].public_symbol,executor_ref=sources[2].public_symbol,
        code_sha256s=tuple((v.public_symbol,v.source_sha256) for v in sources))
    admitted=hosts.admit_local_capability_v01(definition=definition,input_validator=functions[0],output_validator=functions[1],executor=functions[2],catalogue_revision=0,host_instance_ref='host:'+root)
    source=kernel.CurrentSource();clock=source.sample()
    host=hosts.build_root_work_execution_host_v01(owning_root_id=root,registry=action.build_empty_action_commit_packet_registry_v02(),catalogue=(admitted,),
        packet_bindings=(),current_dependency_observations=(),logical_time_bridge=clock.logical_time_bridge,trusted_source=source)
    def execute(name):
        return hosts.execute_admitted_pure_work_v01(host,admission_id=admitted.admission_id,task_id='atlas:code',work_instance_id=name,
            inputs=caps.records(dict(material=('TEXT','check'))),expected_revision=host.revision)
    positive=execute('original')
    before=module.EXECUTOR_ENTRIES
    changed=SACRIFICIAL_CODE.replace("'TEXT','original'","'TEXT','changed'")
    path.write_text(changed)
    (directory/'changed_source.txt').write_text(changed)
    try:
        try:execute('same_name_changed')
        except ValueError as error:reason=str(error)
        else:raise AssertionError('changed_executor_was_admitted')
        c.require(module.EXECUTOR_ENTRIES==before,'atlas_changed_executor_entered')
    finally:path.write_text(SACRIFICIAL_CODE)
    restored=execute('restored_original')
    return dict(original_source=SACRIFICIAL_CODE,changed_source=changed,original_sha256=c.digest(SACRIFICIAL_CODE.encode()),
        changed_sha256=c.digest(changed.encode()),admission=feedback.g35_record_to_plain_v01(fw.snapshot_admitted_capability_v01(admitted)),
        positive=feedback.g35_record_to_plain_v01(positive[:2]),restored=feedback.g35_record_to_plain_v01(restored[:2]),
        refused_operation=definition.operation_id,refusal=reason,changed_executor_delta=0,
        attempts=[asdict(v) for v in host.work_attempts],boundary='HOST_REFRESH_BEFORE_EXECUTOR',
        source_path=str(path),original_restored=path.read_bytes()==SACRIFICIAL_CODE.encode())
