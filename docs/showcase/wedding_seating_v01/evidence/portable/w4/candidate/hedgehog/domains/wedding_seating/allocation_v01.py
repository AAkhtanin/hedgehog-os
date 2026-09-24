"""Wedding-owned native inventory for the public pure G4 allocator."""
from hedgehog.gate4_reference_contracts_v01 import G4_REFERENCE_NUMERIC_V01,Q,NUMERIC_HASH,UTILITY_HASH
from hedgehog.gate4_pressure_budget_v01 import evaluate_reference_pressure_v01,allocate_reference_work_budget_v01,validate_reference_allocation_v01
from . import runtime_v01 as r,native_contracts_v01 as c,native_capabilities_v01 as caps,native_adapter_v01 as n

FAMILIES=('COHESION_EXPLANATION','MIXING_EXPLANATION')
def ref(kind,value):return 'g4_reference:wedding:'+kind+':'+c.digest(value)

def derive_budget_v01(host,task,common,material):
    snap=n.w.inspect_work_task_v01(host,task_id=task)
    c.require(snap.policy.max_compute_units==6 and snap.usage.compute_units==1,'original_optional_budget')
    c.require(n.abi.kernel_artifact_to_plain_dict_v01(common['semantic_proposal'])['payload']['parent_plan_ref']==material['parent_plan_ref'],'original_diagnostic_source')
    basis=dict(snapshot=r.plain(snap),source=r.plain(common['source_context']),proposal=r.plain(common['semantic_proposal']),material=material)
    root=ref('root',host.owning_root_id);taskref=ref('task',task);policyref=ref('policy',r.plain(snap.policy));tx=ref('transaction',common['semantic_proposal'].transaction_id)
    catalogue=ref('catalogue',[x.definition.definition_id for x in common['catalogue']])
    branches=[]
    for family in FAMILIES:
        bid='g4_reference:wedding:'+family
        def feature(value,label):return dict(value=value,source_ref=ref('feature',[material['parent_plan_ref'],family,label]),normalization='FIXED_Q_0_1',interpretation=label)
        preferred=(material['profile']=='KEEP_FAMILIAR_V01')==(family=='COHESION_EXPLANATION')
        branches.append(dict(id=bid,material_ref=ref('material',[family,material]),catalogue_revision=catalogue,
            hard=[dict(id=ref('hard',family),state='TRUE',evidence_ref=ref('validation',material['validation']))],eligible='TRUE',available='TRUE',lower=1,upper=3,
            relevance=feature(Q if preferred else Q//2,'Owner-approved profile relevance'),lineage=feature(Q,'Actual accepted parent plan'),
            uncertainty=feature(0,'Deterministic table pair counts'),cost=feature(Q//3,'One native dispatch per table'),
            prior=dict(value=0,source_ref=ref('prior',family),disposition='ABSENT',normalization='FIXED_Q_SIGNED',interpretation='No learned prior')))
    policyhash=c.digest(dict(total=snap.policy.max_compute_units,policy_ref=policyref,owner_root_id=root,task_id=taskref))
    ctx=dict(profile=G4_REFERENCE_NUMERIC_V01,scope='G4_REFERENCE_SCOPE_V01',schema='g4_reference:v01',evaluation_id=ref('evaluation',basis),
        domain_id='g4_reference:wedding',owner_root_id=root,task_id=taskref,transaction_id=tx,intent_ref=ref('intent',snap.policy.intent_ref),bsep_ref=ref('bsep',common['source_context'].bsep_packet),
        participants=sorted([root,'g4_reference:wedding:diagnostic_actor']),evaluation_time=common['source_context'].g2a_evaluation_time,
        time_envelope_ref=ref('time',r.plain(common['semantic_proposal'])['time_envelope']),source_snapshot_ref=ref('branches',branches),source_snapshot_hash=c.digest(branches),
        candidate_set_ref=ref('families',FAMILIES),candidate_set_hash=c.digest([b['id'] for b in branches]),policy_ref=policyref,policy_hash=policyhash,
        utility_profile_ref='g4_reference:utility:v01',utility_profile_hash=UTILITY_HASH,numeric_profile_ref='g4_reference:numeric:v01',numeric_profile_hash=NUMERIC_HASH,
        dependencies=[ref('parent',material['parent_plan_ref'])],catalogue_revision=catalogue,origin='NATIVE_SOURCE_BOUND_G42_V01',
        dispositions=[dict(id=ref('disposition',material['parent_plan_ref']),state='KNOWN',source_ref=ref('parent',material['parent_plan_ref']))],
        native_binding=dict(profile='G42_ORIGINAL_AND_PROJECTION_BINDING_V01',basis_sha256=c.digest(basis),original_snapshot_sha256=c.digest(r.plain(host.current_sources)),
            original_policy_sha256=c.digest(r.plain(snap.policy)),original_usage_sha256=c.digest(r.plain(snap)),original_envelope_sha256=c.digest(r.plain(common['semantic_proposal'])['time_envelope']),
            id_mapping_sha256=c.digest(dict(root=host.owning_root_id,task=task,policy=r.plain(snap.policy)))))
    pressure=dict(context=ctx,branches=branches)
    finaldef=next(x.definition.definition_id for x in common['catalogue'] if x.definition.operation_id=='wedding.consume')
    return dict(context=ctx,id=ref('budget',basis),original_policy_ref=policyref,original_policy_hash=policyhash,total=snap.policy.max_compute_units,spent=snap.usage.compute_units,
        spending_snapshot_ref=ref('usage',r.plain(snap)),spending_snapshot_hash=c.digest(dict(spent=snap.usage.compute_units,host_revision=snap.host_revision,owner_root_id=root,task_id=taskref,transaction_id=tx)),
        host_revision=snap.host_revision,mandatory=[dict(id=ref('mandatory','final'),count=1,kind='FINAL_CONSUMER',definition_ref=ref('definition',finaldef),
            material_ref=ref('material',material),material_sha256=c.digest(material),source_ref=ref('parent',material['parent_plan_ref']),catalogue_revision=catalogue)],pressure_inputs=pressure)

def run_diagnostics_v01(run):
    run.validate_current(run.owner)
    material=caps.material(run.outcome.results[-1].result.output)
    material['parent_plan_ref']=run.evidence['artifact']['artifact_id']
    task=run.owner.request_ref+':diagnostics';root=run.host.owning_root_id;now=run.evidence['now'];hostref='host:'+task
    catalogue=caps.catalogue_v01(hostref)
    source,_=n.semantic_source('Explain selected tables without changing the accepted seating plan.',task,root,now,dict(needs=['ORIGINAL_VALIDATION'],unresolved=[]))
    proposal=n.abi.build_kernel_artifact_v01(abi_version='v1.0',artifact_id=c.identity('diagnostics',material),artifact_type='SemanticArchitectProposal',schema_version='v1',transaction_id='transaction:'+task,
        owner_root_id=root,source_component='semantic_architect',authority_class='ADVISORY',lifecycle_state='PROPOSED',payload=material,
        trace_refs=('intent:'+task,material['parent_plan_ref']),parent_refs=(source.bsep_packet['packet_id'],),
        time_envelope=dict(r.plain(run.common['semantic_proposal'])['time_envelope'],ct_session_anchor=task))
    common=dict(catalogue=catalogue,source_context=source,semantic_proposal=proposal)
    defs={x.definition.operation_id:x.definition.definition_id for x in catalogue}
    seed=n.w.WorkItemV01('accepted_plan',defs['wedding.consume'],root,(n.w.WorkInputBindingV01('material',n.w.WorkLiteralV01(caps.record(material)[0])),),(),(),None,None)
    candidate=n.w.build_work_program_candidate_v01(task_id=task,previous_revision_id=None,intent_ref='intent:'+task,bsep_ref=source.bsep_packet['packet_id'],semantic_proposal_ref=proposal.artifact_id,
        catalogue_revision=0,budget=n.w.WorkBudgetV01(5,0,0,6,1),items=(seed,),trigger_evidence_refs=(),**common)
    program=n.w.materialize_work_program_v01(candidate,**common)
    policy=n.w.build_work_task_policy_v01(candidate,**common,host_instance_ref=hostref,definition_ids=tuple(sorted(defs.values())),resource_refs=())
    trusted=r.ControlledSourceV01(now)
    host=n.hosts.build_root_work_execution_host_v01(owning_root_id=root,registry=n.a.build_empty_action_commit_packet_registry_v02(),catalogue=catalogue,packet_bindings=(),current_dependency_observations=(),logical_time_bridge=trusted.snapshot.logical_time_bridge,trusted_source=trusted,task_policies=(policy,))
    context=n.w.enroll_work_program_v01(host,program,**common,expected_revision=host.state_revision)
    seed_result=n.w.advance_work_program_v01(program,**common,host_map={root:host},continuation_context=context)
    c.require(seed_result.status=='COMPLETED','diagnostic_seed')
    budget=derive_budget_v01(host,task,common,material)
    pressure=evaluate_reference_pressure_v01(budget['pressure_inputs'],profile=G4_REFERENCE_NUMERIC_V01)
    allocation=allocate_reference_work_budget_v01(pressure,current_budget_context=budget)
    fresh=derive_budget_v01(host,task,common,material)
    validate_reference_allocation_v01(allocation,inputs=fresh['pressure_inputs'],current_budget_context=fresh)
    c.require(allocation.plain()['target']==4,'four_optional_units')
    context=n.w.work_continuation_context_v01(host,task_id=task,expected_revision=host.state_revision)
    trigger=n.w.build_work_revision_trigger_v01(context,work_id='accepted_plan',output_field='material')
    selected=[]
    for row in allocation.plain()['rows']:
        stem='cohesion_' if row['id'].endswith('COHESION_EXPLANATION') else 'mixing_'
        selected.extend(stem+str(i) for i in range(row['allocation']))
    items=[]
    for i,name in enumerate(selected+['consume']):
        previous=trigger.output if i==0 else n.w.WorkOutputBindingV01(items[-1].work_id,'material','TEXT')
        items.append(n.w.WorkItemV01('diagnostic_'+name,defs['wedding.'+name],root,(n.w.WorkInputBindingV01('material',previous),),(),() if i==0 else (items[-1].work_id,),None,None))
    revised=n.w.revise_work_program_v01(context,previous_revision_id=program.candidate.revision_id,trigger=trigger,items=tuple(items),budget=n.w.WorkBudgetV01(5,0,0,5,0),**common)
    current=n.w.work_continuation_context_v01(host,task_id=task,expected_revision=host.state_revision)
    result=n.w.advance_work_program_v01(revised.program,**common,host_map={root:host},continuation_context=current)
    c.require(result.status=='COMPLETED','diagnostic_dispatch')
    actual=caps.material(result.results[-1].result.output)
    expected=[caps.table_diagnostic(material,'COHESION_EXPLANATION' if x.startswith('cohesion') else 'MIXING_EXPLANATION',int(x[-1])) for x in selected]
    c.require(actual['diagnostics']==expected and actual['safe_output']==run.output,'actual_diagnostic_consumption')
    current=n.w.work_continuation_context_v01(host,task_id=task,expected_revision=host.state_revision)
    c.require(n.w.validate_work_program_result_v01(revised.program,result.results,**common,host_map={root:host},continuation_context=current)[0],'diagnostic_supplied')
    decision=n.root_review(root,'transaction:'+task,c.identity('diagnostic_result',actual['diagnostics']),task,
        dict(actual_diagnostics=actual['diagnostics']==expected,original_cap=n.w.inspect_work_task_v01(host,task_id=task).usage.compute_units==policy.max_compute_units),
        result.results[-1].result.result_id,revised.program.candidate.bsep_ref,revised.program.topology_artifact.artifact_id,now,
        predicate='wedding_bounded_diagnostic_output',claim_value=dict(parent=material['parent_plan_ref'],diagnostics=actual['diagnostics']))
    proof=dict(budget=budget,pressure=pressure.plain(),allocation=allocation.plain(),seed=r.plain(seed_result),program=r.plain(revised.program),results=r.plain(result.results),snapshot=r.plain(n.w.inspect_work_task_v01(host,task_id=task)),
        diagnostics=actual['diagnostics'],root_input=r.plain(decision[1]),root_result=r.plain(decision[2]),
        table_coverage='PARTIAL_PER_FAMILY',strong_gt='NOT_USED_IN_SINGLE_OWNER_PROFILE',counter_native_dispatches=6)
    validate_supplied_diagnostics_v01(proof,expected_material=material)
    return proof

def validate_supplied_diagnostics_v01(proof,*,expected_material):
    budget=proof['budget']
    report=validate_reference_allocation_v01(proof['allocation'],inputs=budget['pressure_inputs'],current_budget_context=budget).plain()
    c.require(budget['mandatory'][0]['material_sha256']==c.digest(expected_material),'diagnostic_original_material')
    selected=[]
    for row in report['rows']:
        family='COHESION_EXPLANATION' if row['id'].endswith('COHESION_EXPLANATION') else 'MIXING_EXPLANATION'
        selected.extend(caps.table_diagnostic(expected_material,family,i) for i in range(row['allocation']))
    c.require(len(proof['results'])==report['target']+1,'missing_diagnostic_result')
    previous=None
    for index,result in enumerate(proof['results']):
        c.require(result['status']=='COMPLETED','diagnostic_result_status')
        incoming=__import__('json').loads(result['invocation']['inputs'][0]['value'])
        output=__import__('json').loads(result['result']['output'][0]['value'])
        if previous is not None:c.require(incoming==previous,'diagnostic_actual_parent')
        c.require(output['diagnostics']==selected[:min(index+1,len(selected))],'diagnostic_performed_value')
        previous=output
    c.require(proof['diagnostics']==selected and proof['root_result']['selected_candidate_id']==c.identity('diagnostic_result',selected),'diagnostic_current_review')
    return True
