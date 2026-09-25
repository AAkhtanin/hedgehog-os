"""Actual numeric source and consumer PURE Work; no peers, effects or authority cache."""
from hedgehog.external_drs import gate5_contracts_v01 as c, gate5_native_v01 as n
from hedgehog.kernel import work_composition_v01 as work, effect_firewall_v01 as firewall, abi_v01 as abi
from hedgehog import action_commit_packet_v02 as action
from demo import run_action_packet_portability_v01 as donor, work_composition_mock_capabilities_v01 as mocks
from run_numeric import execute as execute_source, validate_output as validate_source
from numeric_context import consume

def execute_consumer(invocation):
    context=c.decode(invocation.inputs[0].value.encode())
    value=consume(context)
    return (action.build_action_effect_parameter_record_v01(parameter_name='total',value_type='INTEGER',value=value),)

def validate_consumer(definition,invocation,output):
    errors=firewall.validate_capability_values_v01(definition.output_fields,output)
    if not errors:
        b=c.decode(invocation.inputs[0].value.encode())
        expected=b['body']['computed']+b['body']['sample']+b['source_projection']['request_revision']
        if output[0].value!=expected: errors=('numeric_consumer_result',)
    return firewall.build_capability_validation_evidence_v01(definition=definition,values=output,
        invocation_id=invocation.invocation_id,valid=not errors,reason_codes=errors)

def perform(mode, value, root, task):
    c.require(mode in ('source','consumer'),'numeric_mode')
    if mode=='source':
        c.integer(value); inputs=dict(sample=value); fields=(('sample','INTEGER'),); output='computed'
        executor,validator=execute_source,validate_source
    else:
        consume(value)
        inputs=dict(context_json=c.canonical(value).decode());fields=(('context_json','TEXT'),);output='total'
        executor,validator=execute_consumer,validate_consumer
    admission=mocks.admit_pure_operation_v01(operation_id='example.g54c.'+mode,input_fields=fields,
        output_fields=((output,'INTEGER'),),executor=executor,output_validator=validator,host_instance_ref='host:g54c:'+mode)
    item=work.WorkItemV01(mode,admission.definition.definition_id,root,
        tuple(donor.work_literal_v01(k,t,inputs[k]) for k,t in fields),(),(),None,None)
    program,common,host=donor.prepare_work_program_v01(task_id=task,root_id=root,admitted=(admission,),items=(item,),device_refs=())
    results=work.advance_work_program_v01(program,**common,host_map={root:host})
    valid,reasons=work.validate_work_program_result_v01(program,results,**common,host_map={root:host})
    c.require(valid and not reasons and len(results)==1 and results[0].status=='COMPLETED','numeric_native_result')
    artifact=work.work_program_result_to_artifact_v01(program,results,**common,host_map={root:host})
    snapshot=firewall.snapshot_admitted_capability_v01(admission)
    c.require(not firewall.validate_capability_execution_result_v01(results[0].result,results[0].invocation,snapshot),'numeric_typed_result')
    return dict(native_evidence=dict(admission=n.plain(snapshot),invocation=n.plain(results[0].invocation),result=n.plain(results[0].result)),
        inputs=inputs,outputs={v.parameter_name:v.value for v in results[0].result.output},attempts=len(host.work_attempts),
        results=n.plain(results),artifact=abi.kernel_artifact_to_plain_dict_v01(artifact),
        clock_profile='CONTROLLED_LOGICAL_1014_SEPARATE_FROM_SOURCE_UTC')
