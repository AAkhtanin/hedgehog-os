"""Pure saved Workspace relations; never restore a Host or decide a Root anew."""
import json
from hedgehog import action_commit_packet_v02 as action, outcome_feedback_v01 as f
from hedgehog.kernel import abi_v01 as abi, effect_firewall_v01 as fw, root_decision_v01 as roots
from . import contracts_v01 as c, capability_registry_v01 as caps, semantic_roles_v01 as roles
from . import incident_atlas_v01 as atlas, incident_atlas_summary_v01 as summary
from . import incident_atlas_work_proof_v01 as workproof


def claim_v01(review):
    inputs,result=workproof.validate_review_v01(review)
    c.require(result.decision=='ACCEPT','atlas_workspace_review_not_accept')
    raw=roots.root_decision_input_to_plain_dict_v01(inputs)
    claims=raw['root_review_packet']['synthesis_proposal']['normalized_claims']
    c.require(len(claims)==1,'atlas_workspace_review_claim')
    return claims[0]['object_or_value'],result


def records_v01(value):
    records=f.g35_validate_work_records_v01(value['results'],value['admissions'])
    program=f.g35_record_from_plain_v01(value['program'])
    f._g35_checked_work_relation_v01(abi.kernel_artifact_to_plain_dict_v01(program.topology_artifact),
        value['artifact'],records,value['admissions'])
    return program,records


def validate_semantics_v01(value):
    program,records=records_v01(value)
    c.require(len(records)==2 and roles.compile_contract(value['roles'])==value['contract'], 'atlas_workspace_contract_work')
    for row in records:
        c.require(json.loads(caps.values(row.result.output)['material'])==value['contract'],'atlas_workspace_contract_output')
    c.require([row['output'] for row in value['captures']]==value['roles'], 'atlas_workspace_semantic_capture')
    claim,result=claim_v01(value['root_review'])
    c.require(result.target_root_id==value['root']==atlas.native.ROOT and
        program.topology_artifact.owner_root_id==value['root'],'atlas_workspace_semantic_root')


def validate_action_v01(row):
    bound=f.g35_record_from_plain_v01(row['bound']); packet=bound.canonical_projection
    registry=f.g35_record_from_plain_v01(row['registry'])
    c.require(action.validate_native_root_bound_action_commit_packet_v01(bound)[0]
        and action.validate_action_commit_packet_registry_v02(registry)[0], 'atlas_workspace_native_history')
    c.require(any(e.root_bound_genesis==bound for e in registry.action_packet_lifecycle_entries),'atlas_workspace_genesis')
    execution=fw.native_execution_evidence_from_plain_data_v01(row['receipt']['payload']['execution_evidence'])
    receipt=f.g35_validate_artifact_v01(row['receipt']);context=f.g35_record_from_plain_v01(row['context'])
    c.require(not fw.validate_native_execution_evidence_v01(execution) and
        execution==f.g35_record_from_plain_v01(row['execution']) and context.receipt==receipt
        and context in registry.action_packet_fulfillment_attempt_contexts
        and execution.invocation.packet_id==bound.packet_identity.packet_id
        and execution.invocation.owning_root_id==receipt.owner_root_id==packet.owning_local_root_id==atlas.native.ROOT
        and receipt.transaction_id==packet.transaction_id,'atlas_workspace_receipt_context')
    inputs=caps.values(execution.invocation.inputs);before=row['before'];after=row['after']
    c.require(execution.invocation.inputs==f.g35_record_from_plain_v01(row['inputs'])
        and inputs==row['fact']['inputs'] and json.loads(inputs['command'])==row['command']
        and inputs['session']==before['session']==after['session'] and inputs['version']==before['version']
        and packet.dependency_candidate.dependency_records[0].content_sha256==c.digest(row['fact'])
        and row['fact']['source_sha256']==before['source_hashes']==after['source_hashes']
        and row['fact']['contract']==before['contract']==after['contract'],'atlas_workspace_action_material')
    output=caps.values(execution.result.output)
    result=json.loads(output['material'])
    c.require(row['output']==output and result['session']==after['session'] and result['version']==after['version']
        and result['op']==row['command']['op'] and after['version']==before['version']+1
        and after['executed']==before['executed']+1,'atlas_workspace_action_output')
    state=action.derive_action_packet_lifecycle_state_v01(registry,packet_id=bound.packet_identity.packet_id)
    c.require(state.lifecycle_state=='RECEIPT_RECEIVED' and state.idempotency_disposition=='CONSUMED'
        and state.terminal_receipt_ref==receipt.artifact_id and not state.executable,'atlas_workspace_terminal')
    return packet,execution


def validate_ingress_v01(row):
    c.require(row['before']==row['after'] and row['executor_delta']==0 and row['host']=='NOT_REACHED','atlas_workspace_ingress_state')
    try:c.command(row['command'],row['before']['allowed'])
    except ValueError as error:c.require(str(error)==row['reason'],'atlas_workspace_ingress_reason')
    else:raise ValueError('atlas_workspace_ingress_was_allowed')


def validate_native_input_v01(value):
    row=value['native_input'];auth=f.g35_record_from_plain_v01(row['authorization']);bound=auth['root_bound']
    c.require(action.validate_native_root_bound_action_commit_packet_v01(bound)[0],'atlas_workspace_input_packet')
    inputs=f.g35_record_from_plain_v01(row['inputs']);wrong=f.g35_record_from_plain_v01(row['wrong_inputs'])
    good=caps.values(inputs);bad=caps.values(wrong);packet=bound.canonical_projection
    c.require(good['session']==row['session']['session'] and good['version']==row['session']['version']
        and {**good,'version':good['version']+1}==bad and good['command']==c.canonical(dict(op='RATE',value=3)).decode(),
        'atlas_workspace_wrong_input_context')
    c.require(packet.consequential_effect_parameters.parameter_records==inputs and row['executor_delta']==0
        and row['reason']=='capability_business_input_binding:version','atlas_workspace_input_binding')
    c.require(not fw.validate_capability_business_binding_v01(packet.execution_source.definition,inputs,packet)
        and fw.validate_capability_business_binding_v01(packet.execution_source.definition,wrong,packet)==(row['reason'],),
        'atlas_workspace_public_input_binding')
    validation=f.g35_record_from_plain_v01(row['validation'])
    c.require(not validation.valid and validation.reason_codes==('current_session_version',),'atlas_workspace_input_validator')
    claim_v01(row['review'])


def validate_code_v01(row):
    admission=f.g35_record_from_plain_v01(row['admission'])
    c.require(not fw.validate_capability_admission_snapshot_v01(admission),'atlas_workspace_code_admission')
    c.require(c.digest(row['original_source'].encode())==row['original_sha256']
        and c.digest(row['changed_source'].encode())==row['changed_sha256'] and row['original_sha256']!=row['changed_sha256']
        and all(h==row['original_sha256'] for _,h in admission.definition.code_sha256s),'atlas_workspace_code_source')
    for key in ('positive','restored'):
        invocation,result=f.g35_record_from_plain_v01(row[key])
        c.require(not fw.validate_capability_execution_result_v01(result,invocation,admission)
            and caps.values(result.output)==dict(material='original'),'atlas_workspace_code_neighbor')
    c.require(row['refusal']=='capability_loaded_source_code_mismatch' and row['changed_executor_delta']==0
        and row['original_restored'] and row['refused_operation']==admission.definition.operation_id,
        'atlas_workspace_code_refusal')


def validate_required_v01(value):
    missing=value['missing_required'];done=value['required_completed'];s=missing['snapshot'];d=done['snapshot']
    program,records=records_v01(done)
    c.require(missing['program']==done['program'] and missing['admissions']==done['admissions']
        and s['policy']==d['policy'] and s['current_revision_id']==d['current_revision_id']==program.candidate.revision_id
        and s['policy']['task_id']==program.candidate.task_id and missing['session']==done['session']==value['current_initial']['session']
        and missing['version']==done['version']==0,'atlas_workspace_required_current_binding')
    c.require(s['outcome']=='ACTIVE' and s['terminal_history_refs']==[] and missing['artifact'] is None
        and f.g35_record_from_plain_v01(missing['results'])==() and missing['work_attempts']==[]
        and f.g35_record_from_plain_v01(missing['completed_work'])==(),'atlas_workspace_required_missing_source')
    c.require(d['outcome']=='COMPLETED' and len(d['terminal_history_refs'])==len(records)==1
        and d['host_revision']>s['host_revision'] and d['usage']['compute_units']==1
        and json.loads(caps.values(records[0].result.output)['material'])==value['current_initial']['contract'],
        'atlas_workspace_required_completed_source')
    pairs=f.g35_record_from_plain_v01(done['completed_work'])
    c.require((records[0].invocation,records[0].result) in pairs and len(done['work_attempts'])==1
        and done['work_attempts'][0]['disposition']=='COMPLETED','atlas_workspace_required_host_history')
    claim,result=claim_v01(done['current_review'])
    c.require(claim==dict(summary_ref=value['summary_accepted']['summary_ref'],required_revision=program.candidate.revision_id),
        'atlas_workspace_required_review')


def validate_summary_v01(value):
    capture=value['summary_capture'];summary.validate_v01(capture['output'])
    c.require(capture['profile']=='AT4_SUMMARY_CAPTURE_V01' and capture['mode']=='LIVE_SUMMARY'
        and json.loads(capture['raw'])==capture['output'] and capture['input']==value['summary_input']
        and capture['input_sha256']==c.digest(capture['input']) and capture['attempt']['raw_sha256']==c.digest(capture['raw'].encode())
        and capture['attempt']['request_sha256']==c.digest(capture['request'])
        and capture['capture_id']==c.identity('atlas_summary_capture',{k:v for k,v in capture.items() if k!='capture_id'}),
        'atlas_workspace_summary_capture')
    accepted=value['summary_accepted'];ctx=accepted['context']
    c.require(ctx['required']==value['missing_required'] and capture['input']['native_missing_snapshot_sha256']==c.digest(ctx['required'])
        and capture['input']['current_session']==value['current_initial']['session']
        and capture['input']['prior_session']==value['previous']['session']
        and capture['input']['closed']==value['previous_close']['status'],'atlas_workspace_summary_independent_source')
    projection=atlas.check_summary_v01(capture['output'],ctx)
    claim,_=claim_v01(accepted['review'])
    c.require(claim==projection==accepted['projection'] and accepted['summary']==capture['output'],'atlas_workspace_summary_consumed')
    for row in value['D1_controls']:
        derived=row['derivative'];edits={e['field']:e['after'] for e in derived['edits']}
        c.require(derived==summary.derivative_v01(capture,edits) and row['context']==ctx,'atlas_workspace_poison_parent_context')
        try:atlas.check_summary_v01(derived['output'],ctx,row['supplied_result'])
        except ValueError as error:c.require(str(error)==row['reason'],'atlas_workspace_poison_reason')
        else:raise ValueError('atlas_workspace_poison_accepted')
        c.require(row['effective_success_samples_added']==row['executor_delta']==0,'atlas_workspace_poison_effect')
    c.require({r['label'] for r in value['D1_controls']}=={'closed_permission','false_completed','invented_evidence','wrong_version','valid_old_result_as_current'},
        'atlas_workspace_poison_inventory')


def validate_memory_v01(value):
    old=value['previous'];new=value['current_initial'];events=value['memory_events']
    c.require(old['session']!=new['session'] and old['root']==new['root'] and old['roles']==new['roles']
        and old['source_hashes']==new['source_hashes'],'atlas_workspace_fresh_memory_session')
    write,read,saved=events;record=write['record']['content']['record'];material=write['record']['content']['material']
    c.require([e['op'] for e in events]==['WRITE','SEARCH','WRITE'] and material['value']==old['roles']
        and material['sources']==[r['response_ref'] for r in old['captures']]+[old['artifact']['artifact_id']]
        and record['meaning_record_id']==value['recipe_id']==value['memory_origin']['record_id']
        and not record['memory_pointers'] and not record['artifact_pointers'] and record['reuse_policy_class']=='CONTEXT_ONLY'
        and json.loads(record['safe_summary'])==new['roles'],'atlas_workspace_recipe_projection')
    descent=read['descent']
    c.require(descent['safe_summaries']==[record['safe_summary']] and descent['opened_record_ids']==[value['recipe_id']]
        and descent['memory_descent_result_id']==value['memory_origin']['descent_id']
        and not descent['creates_permission'] and read['root']['decision']=='ACCEPT'
        and read['root']['selected_candidate_id']==read['plan']['retrieval_plan_id']==descent['retrieval_plan_id']
        and read['query_current']['owning_local_root_id']==new['root'],'atlas_workspace_recipe_descent')
    c.require(value['old_session_refusal']['reason']=='workspace_not_current' and
        value['old_session_refusal']['before']==value['old_session_refusal']['after'],'atlas_workspace_old_session')
    c.require(saved['record']['content']['material']['value']['sidecar_sha256']==value['sidecar']['sha256'],
        'atlas_workspace_saved_memory')


def validate_consumption_v01(value):
    row=value['consumption'];chosen=value['experience']['after'];material=row['material']
    c.require(material['work_artifact_ref']==chosen['artifact']['artifact_id'] and material['output_sha256']==c.digest(chosen['output'])
        and material['selection']==chosen['material']['summary']['selection']==value['summary_capture']['output']['selection']
        and chosen['material']['required_work']==value['required_completed']
        and chosen['material']['summary']==value['summary_capture']['output'],'atlas_workspace_consumed_result')
    claim,_=claim_v01(row['review']);c.require(claim==material,'atlas_workspace_consumption_review')
    commands=row['commands'];plan=material['selection']
    c.require(commands[0]['before']==chosen['material']['session'] and [r['command'] for r in commands]==[
        dict(op='OPEN',value=None),dict(op='SELECT',value=plan['selected']),dict(op='RATE',value=plan['rating']),
        dict(op='EXPOSURE',value=plan['exposure']),dict(op='CROP',value=plan['crop']),dict(op='REQUEST_SAVE',value=None),
        dict(op='SAVE',value=value['exact_approval']['ref'])],'atlas_workspace_command_consumption')
    for command in commands:validate_action_v01(command)
    for a,b in zip(commands,commands[1:]):
        # Exact approval is an explicit local-owner input between REQUEST_SAVE and SAVE.
        keys=set(a['after'])-({'approvals'} if b['command']['op']=='SAVE' else set())
        c.require({k:a['after'][k] for k in keys}=={k:b['before'][k] for k in keys},'atlas_workspace_command_sequence')
    approve=value['exact_approval'];sidecar=value['sidecar'];before=commands[-1]['before'];after=commands[-1]['after']
    c.require(approve['candidate']==before['pending']==before['approvals'][approve['ref']]['candidate']
        and not before['approvals'][approve['ref']]['used'] and after['approvals'][approve['ref']]['used']
        and approve['ref']!=value['previous_approval']['ref'],'atlas_workspace_exact_approval')
    raw=c.canonical(approve['candidate']['content'])+b'\n'
    c.require(raw.decode()==sidecar['raw'] and json.loads(raw)==sidecar['content'] and len(raw)==sidecar['bytes']
        and c.digest(raw)==sidecar['sha256']==approve['candidate']['bytes_sha256']==after['saved']['sha256'],
        'atlas_workspace_sidecar_binding')
    c.require(value['stale_approval']['reason']=='save_approval_current' and
        value['stale_approval']['before']==value['stale_approval']['after'] and row['wrong_work_refusal']=='atlas_workspace_consumed_work',
        'atlas_workspace_stale_approval')


def validate_workspace_v01(value):
    c.require(value['profile']=='AT4_WORKSPACE_V01','atlas_workspace_profile')
    for key in ('previous','current_initial'):validate_semantics_v01(value[key])
    for row in value['W1']+value['W2']:validate_ingress_v01(row)
    c.require([r['command']['op'] for r in value['W1']+value['W2']]==['PUBLISH','SEND','SHELL','EXEC','WRITE'],'atlas_workspace_ingress_inventory')
    for row in value['commands']:validate_action_v01(row)
    validate_native_input_v01(value);validate_code_v01(value['W3']);validate_required_v01(value)
    validate_summary_v01(value);validate_memory_v01(value);workproof.validate_experience_v01(value);validate_consumption_v01(value)
    for key in ('previous_close','current_close'):
        close=value[key]
        c.require(close['status']=='CLOSED_SUCCESS' and len(close['processes'])==2
            and all(p['reaped'] and p['returncode']==0 and p['receipt']['closed'] for p in close['processes']), 'atlas_workspace_cleanup')
    c.require(value['original_sha256']==value['current_initial']['source_hashes']['asset:1']==value['sidecar']['content']['selection'][0]['source_sha256'],
        'atlas_workspace_original_preservation')
    c.require(value['counts']==dict(domain_consumers=1,predictive_events=1,effective_samples=1,current_saved_sidecars=1,
        previous_saved_sidecars=0,summary_calls=1,controlled_poison_derivatives=5,captured_reexecutions=0,browser_runs=0,
        new_D_E=0,external_business_effects=0),'atlas_workspace_counts')
    return True
