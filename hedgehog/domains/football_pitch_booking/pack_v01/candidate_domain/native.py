"""Thin native PURE/Root adapter using public donor composition."""
from hedgehog.external_drs import gate5_contracts_v01 as c, gate5_native_v01 as n
from hedgehog.kernel import work_composition_v01 as work, effect_firewall_v01 as firewall, abi_v01 as abi
from hedgehog import action_commit_packet_v02 as action
from demo import run_action_packet_portability_v01 as donor, work_composition_mock_capabilities_v01 as mocks
from candidate_domain.domain import produce, verify_producer, consume

def values(invocation):
    return {v.parameter_name:v.value for v in invocation.inputs}

def parsed(invocation):
    return {k:c.decode(v.encode()) for k,v in values(invocation).items()}

def execute_venue(invocation):
    v=parsed(invocation)
    return (action.build_action_effect_parameter_record_v01(parameter_name='offer_json',value_type='TEXT',
            value=c.canonical(produce(v['request_json'],v['inventory_json'])).decode()),)

def execute_requester(invocation):
    v=parsed(invocation)
    return (action.build_action_effect_parameter_record_v01(parameter_name='result_json',value_type='TEXT',
            value=c.canonical(consume(v['request_json'],v['offer_json'])).decode()),)

def validate_venue(definition,invocation,output):
    errors=firewall.validate_capability_values_v01(definition.output_fields,output)
    if not errors:
        try:
            v=parsed(invocation)
            verify_producer(v['request_json'],v['inventory_json'],c.decode(output[0].value.encode()))
        except ValueError as exc:
            errors=('football_producer:'+str(exc),)
    return firewall.build_capability_validation_evidence_v01(definition=definition,values=output,
        invocation_id=invocation.invocation_id,valid=not errors,reason_codes=errors)

def validate_requester(definition,invocation,output):
    errors=firewall.validate_capability_values_v01(definition.output_fields,output)
    if not errors:
        try:
            v=parsed(invocation); result=c.decode(output[0].value.encode())
            c.require(result==consume(v['request_json'],v['offer_json']),'consumer_result_binding')
        except ValueError as exc:
            errors=('football_consumer:'+str(exc),)
    return firewall.build_capability_validation_evidence_v01(definition=definition,values=output,
        invocation_id=invocation.invocation_id,valid=not errors,reason_codes=errors)

def perform(mode,r,value,root,task,evidence_folder=None):
    c.require(mode in ('venue','requester'),'native_mode')
    if mode=='venue':
        second,out='inventory_json','offer_json'; executor,validator=execute_venue,validate_venue
    else:
        second,out='offer_json','result_json'; executor,validator=execute_requester,validate_requester
    inputs={'request_json':c.canonical(r).decode(),second:c.canonical(value).decode()}
    fields=(('request_json','TEXT'),(second,'TEXT'))
    admitted=mocks.admit_pure_operation_v01(operation_id='football.'+mode+'.v01',input_fields=fields,
        output_fields=((out,'TEXT'),),executor=executor,output_validator=validator,host_instance_ref='host:football:'+mode)
    item=work.WorkItemV01(mode,admitted.definition.definition_id,root,
        tuple(donor.work_literal_v01(k,t,inputs[k]) for k,t in fields),(),(),None,None)
    program,common,host=donor.prepare_work_program_v01(task_id=task,root_id=root,admitted=(admitted,),
                                                     items=(item,),device_refs=())
    results=work.advance_work_program_v01(program,**common,host_map={root:host})
    valid,reasons=work.validate_work_program_result_v01(program,results,**common,host_map={root:host})
    if evidence_folder is not None:
        n.save(evidence_folder/('native_attempt_'+mode+'.json'),dict(attempts=n.plain(host.work_attempts),
            results=n.plain(results),valid=valid,reasons=reasons))
    c.require(valid and not reasons and len(results)==1 and results[0].status=='COMPLETED','football_native_result')
    artifact=work.work_program_result_to_artifact_v01(program,results,**common,host_map={root:host})
    snapshot=firewall.snapshot_admitted_capability_v01(admitted)
    c.require(not firewall.validate_capability_execution_result_v01(results[0].result,results[0].invocation,snapshot),
              'football_typed_result')
    return dict(native_evidence=dict(admission=n.plain(snapshot),invocation=n.plain(results[0].invocation),
                                    result=n.plain(results[0].result)),
                inputs=inputs,outputs={v.parameter_name:v.value for v in results[0].result.output},
                attempts=len(host.work_attempts),results=n.plain(results),
                artifact=abi.kernel_artifact_to_plain_dict_v01(artifact))

def review(root,transaction,candidate,subject,checks,claim,now,folder,name,window=None,
           *,predicate='g51_bounded_context_review'):
    with (folder/'review_calls.jsonl').open('ab') as stream:
        stream.write(c.canonical(dict(stage='CALLED',root=root,candidate=candidate,subject=subject,utc=now))+b'\n')
    live=n.root_review(root,transaction,candidate,subject,checks,claim,now,predicate=predicate,window=window)
    value=n.root_plain(live)
    n.save(folder/(name+'.json'),value)
    return live
