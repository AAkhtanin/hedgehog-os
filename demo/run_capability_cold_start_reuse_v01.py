"""Controlled finite PURE-code proposal through the ordinary Work handler."""
from dataclasses import replace, asdict, dataclass, fields, is_dataclass
from pathlib import Path
import base64
import json
import tempfile
from types import MappingProxyType
from hedgehog import capability_admission_v01 as pure
from hedgehog import capability_memory_binding_v01 as memory
from hedgehog import work_execution_host_v01 as hosts
from hedgehog import action_commit_packet_v02 as action
from hedgehog.drs import LocalDRS
from hedgehog.kernel import work_composition_v01 as work
from hedgehog.kernel import effect_firewall_v01 as firewall
from hedgehog.kernel import abi_v01 as abi
from demo import work_composition_mock_capabilities_v01 as mocks
from demo import run_action_packet_portability_v01 as runner


def format_integer_content_v01(invocation):
    values = {v.parameter_name:v.value for v in invocation.inputs}
    return (action.build_action_effect_parameter_record_v01(parameter_name='content_ref',value_type='REFERENCE',
        value='content:pure-value:' + str(values['value'])),)


def validate_integer_content_output_v01(definition, invocation, output):
    errors = firewall.validate_capability_values_v01(definition.output_fields,output)
    expected = 'content:pure-value:' + str(next(v.value for v in invocation.inputs if v.parameter_name=='value'))
    reasons = errors or (() if len(output)==1 and output[0].value==expected else ('pure_content_actual_input',))
    return firewall.build_capability_validation_evidence_v01(definition=definition,values=output,
        invocation_id=invocation.invocation_id,valid=not reasons,reason_codes=reasons)


def build_pure_task_v01(*, task_id, multiplier, offset, value, memory_scope, max_drs_bytes=131072):
    root,device='root:u3:local','device:u3:local'
    formatter=mocks.admit_pure_operation_v01(operation_id='u3.integer_content',input_fields=(('value','INTEGER'),),
        output_fields=(('content_ref','REFERENCE'),),executor=format_integer_content_v01,
        output_validator=validate_integer_content_output_v01,host_instance_ref='host:'+root)
    effect=mocks.admit_playback_v01(device,'host:'+root)
    catalogue=(formatter,effect)
    source=mocks.build_work_source_context_v01(task_id)
    semantic=abi.build_kernel_artifact_v01(abi_version='v1.0',artifact_id='semantic:'+task_id,
        artifact_type='SemanticArchitectProposal',schema_version='v1',transaction_id='transaction:'+task_id,
        owner_root_id=root,source_component='semantic_architect',authority_class='ADVISORY',lifecycle_state='PROPOSED',
        payload={'pure_need':dict(contract_version=pure.CONTRACT_VERSION,work_id='need',multiplier=multiplier,offset=offset),
            'provenance':'CONTROLLED_DETERMINISTIC'},trace_refs=('intent:'+task_id,),parent_refs=(source.bsep_packet['packet_id'],),
        time_envelope={'pt_created_at':'2026-01-01T00:00:00+00:00','kt_asof':'2026-01-01T00:00:00+00:00',
            'et_observed_at':None,'ct_session_anchor':'session:'+task_id,'ttl_seconds':3600,'freshness_class':'static',
            'valid_from':'2026-01-01T00:00:00+00:00','valid_to':'2026-01-01T01:00:00+00:00'})
    items=(work.WorkItemV01('baseline_effect',effect.definition.definition_id,root,
        (runner.work_literal_v01('content_ref','REFERENCE','content:u3:baseline'),
         runner.work_literal_v01('device_ref','REFERENCE',device)),(device,),(),None,None),
        work.WorkItemV01('need',pure.MISSING_DEFINITION,root,
            (runner.work_literal_v01('value','INTEGER',value),),(),(),None,None),
        work.WorkItemV01('render',formatter.definition.definition_id,root,
            (work.WorkInputBindingV01('value',work.WorkOutputBindingV01('need','value','INTEGER')),),(),('need',),None,None),
        work.WorkItemV01('effect',effect.definition.definition_id,root,
            (work.WorkInputBindingV01('content_ref',work.WorkOutputBindingV01('render','content_ref','REFERENCE')),
             runner.work_literal_v01('device_ref','REFERENCE',device)),(device,),('render',),None,None))
    common=dict(catalogue=catalogue,source_context=source,semantic_proposal=semantic)
    candidate=work.build_work_program_candidate_v01(task_id=task_id,previous_revision_id=None,intent_ref='intent:'+task_id,
        bsep_ref=source.bsep_packet['packet_id'],semantic_proposal_ref=semantic.artifact_id,catalogue_revision=0,
        budget=work.WorkBudgetV01(8,0,0,8,2),items=items,trigger_evidence_refs=(),**common)
    program=work.materialize_work_program_v01(candidate,**common)
    policy=work.build_work_task_policy_v01(candidate,**common,host_instance_ref='host:'+root,
        definition_ids=tuple(sorted([pure.MISSING_DEFINITION,*[a.definition.definition_id for a in catalogue]])),resource_refs=(device,))
    permission=work.build_pure_need_permission_v01(program,**common,work_id='need',memory_scope=memory_scope,max_drs_bytes=max_drs_bytes)
    observations=(runner.build_work_dependency_v01(device,root)[2],)
    bridge=action.build_logical_time_bridge_v01(origin_utc_epoch_seconds=1000,seconds_per_tick=1,
        bridge_policy_version='u1.controlled_ticks.v01')
    trusted=mocks.TrustedMockWorkSourceV01(observations,bridge,1014,'u1.controlled_utc','context:u1:dispatch')
    host=hosts.build_root_work_execution_host_v01(owning_root_id=root,
        registry=action.build_empty_action_commit_packet_registry_v02(),catalogue=catalogue,packet_bindings=(),
        current_dependency_observations=observations,logical_time_bridge=bridge,trusted_source=trusted,
        task_policies=(policy,),pure_need_permissions=(permission,))
    context=work.enroll_work_program_v01(host,program,**common,expected_revision=host.state_revision)
    outcome=work.advance_work_program_v01(program,**common,host_map={root:host},continuation_context=context,
        action_authorizers={root:runner.authorize_resolved_work_v01})
    if outcome.status!='NEEDS_CAPABILITY':raise ValueError('cold_missing_outcome')
    context=work.work_continuation_context_v01(host,task_id=task_id,expected_revision=host.state_revision)
    need=work.observe_missing_pure_need_v01(context)
    return dict(host=host,common=common,initial=outcome,need=need,permission=permission)


def continue_pure_task_v01(task, package):
    host,need=task['host'],task['need']
    resolution=hosts.install_admitted_pure_capability_v01(host,package=package,need=need,expected_revision=host.state_revision)
    context=work.work_continuation_context_v01(host,task_id=need.permission.task_id,expected_revision=host.state_revision)
    trigger=work.build_pure_missing_trigger_v01(context,need=need,resolution=resolution)
    old=task['initial'].program.candidate
    original=next(i for i in old.items if i.work_id=='need')
    new=replace(original,definition_id=resolution.definition_id,inputs=tuple(sorted((*original.inputs,
        runner.work_literal_v01('package_ref','REFERENCE',resolution.package_id)),key=lambda b:b.input_field)))
    items=tuple(new if i.work_id=='need' else i for i in old.items if i.work_id!='baseline_effect')
    common={**task['common'],'catalogue':host.admitted_catalogue}
    revised=work.revise_work_program_v01(context,previous_revision_id=old.revision_id,trigger=trigger,items=items,
        budget=work.WorkBudgetV01(8,0,0,7,1),**common)
    context=work.work_continuation_context_v01(host,task_id=need.permission.task_id,expected_revision=host.state_revision)
    final=work.advance_work_program_v01(revised.program,**common,host_map={host.owning_root_id:host},results=revised.results,
        continuation_context=context,action_authorizers={host.owning_root_id:runner.authorize_resolved_work_v01})
    context=work.work_continuation_context_v01(host,task_id=need.permission.task_id,expected_revision=host.state_revision)
    valid=work.validate_work_continuation_outcome_v01(final,context=context,**common)
    if valid!=(True,()) or final.status!='COMPLETED':raise ValueError('pure_continuation_failed:'+repr((valid,final)))
    return dict(task=task,resolution=resolution,trigger=trigger,package=package,common=common,final=final)


def run_cold_pure_task_v01(*, store, task_id, multiplier=3, offset=7, value=31):
    task=build_pure_task_v01(task_id=task_id,multiplier=multiplier,offset=offset,value=value,memory_scope='memory:u3:local')
    search=memory.search_pure_need_v01(store,host=task['host'],need=task['need'])
    if search.result.candidate_count!=0:raise ValueError('cold_store_not_empty_for_need')
    host=task['host']
    proposal=pure.generate_controlled_pure_candidate_v01(host,need=task['need'],expected_revision=host.state_revision)
    attempt,package=pure.admit_pure_candidate_v01(host,need=task['need'],source=proposal.wat,source_format='wat',
        contract_version=task['need'].permission.contract_version,expected_revision=host.state_revision)
    if package is None:raise ValueError('cold_admission_refused:'+str(attempt.reason))
    continued=continue_pure_task_v01(task,package)
    record=memory.write_pure_memory_v01(store,host=host,package=package,proposal=proposal)
    context=work.work_continuation_context_v01(host,task_id=task_id,expected_revision=host.state_revision)
    continued['final']=work.inspect_work_continuation_outcome_v01(context)
    return dict(search=search,proposal=proposal,attempt=attempt,record=record,continued=continued)


@dataclass(frozen=True)
class PureColdWarmReportV01:
    cold: dict
    retrieval: memory.PureMemoryRetrievalV01
    warm: dict
    cold_resources: pure.PureResourceUsageV01
    warm_resources: pure.PureResourceUsageV01


def collect_capability_cold_start_reuse_v01(*, store_path=None, multiplier=3, offset=7, value=31):
    directory=tempfile.mkdtemp(prefix='pure-cold-warm-') if store_path is None else store_path
    store=LocalDRS(directory)
    cold=run_cold_pure_task_v01(store=store,task_id='task:u3:cold',multiplier=multiplier,offset=offset,value=value)
    task=build_pure_task_v01(task_id='task:u3:warm',multiplier=multiplier,offset=offset,value=value,memory_scope='memory:u3:local')
    retrieval=memory.retrieve_pure_memory_v01(store,host=task['host'],need=task['need'])
    warm=continue_pure_task_v01(task,retrieval.package)
    report=PureColdWarmReportV01(cold,retrieval,warm,
        hosts.inspect_pure_need_resources_v01(cold['continued']['task']['host'],task_id='task:u3:cold'),
        hosts.inspect_pure_need_resources_v01(task['host'],task_id='task:u3:warm'))
    if not validate_capability_cold_start_reuse_report_v01(report):raise ValueError('pure_report_invalid')
    return report


def _check(ok,reason):
    if not ok:raise ValueError(reason)


def _validate_continued(continued):
    _check(type(continued) is dict and set(continued)=={'task','resolution','trigger','package','common','final'},'report_continued_shape')
    task=continued['task']
    _check(type(task) is dict and set(task)=={'host','common','initial','need','permission'},'report_task_shape')
    host=task['host'];need=task['need'];final=continued['final'];initial=task['initial']
    _check(type(task['common']) is dict and set(task['common'])=={'catalogue','source_context','semantic_proposal'}
        and type(continued['common']) is dict and set(continued['common'])==set(task['common']), 'report_context_shape')
    _check(initial.program==work.materialize_work_program_v01(initial.program.candidate,**task['common']), 'report_initial_context')
    pure.validate_pure_need_v01(need)
    _check(type(host) is hosts.RootWorkExecutionHostV01 and task['permission']==need.permission,'report_host_permission')
    context=work.work_continuation_context_v01(host,task_id=need.permission.task_id,expected_revision=host.state_revision)
    _check(work.validate_work_continuation_outcome_v01(final,context=context,**continued['common'])==(True,()),'report_actual_work_result')
    history=work.inspect_work_task_history_v01(context)
    _check(len(history)==2 and history[0][0]==initial.program and history[0][1]==initial.results,'report_original_history')
    _check(initial.status=='NEEDS_CAPABILITY' and final.status=='COMPLETED' and
        initial.snapshot.policy==final.snapshot.policy and final.program.candidate.task_id==initial.program.candidate.task_id,
        'report_same_task')
    initial_rows={v.work_id:v for v in initial.results}
    _check(initial_rows['need'].status=='NEEDS_CAPABILITY' and initial_rows['need'].result is None
        and initial_rows['render'].status=='BLOCKED_REQUIRED_OUTPUT' and initial_rows['effect'].status=='BLOCKED_REQUIRED_OUTPUT',
        'report_real_missing_need')
    package=continued['package']
    pure.validate_admitted_pure_package_v01(package,host=host,need=need)
    _check(continued['resolution'] in host.pure_need_resolutions and continued['resolution'].need==need
        and continued['trigger'].resolution is continued['resolution'] and continued['trigger'].need==need,'report_resolution')
    _check(final.program.candidate.previous_revision_id==initial.program.candidate.revision_id
        and final.program.candidate.trigger_evidence_refs==(continued['trigger'].trigger_id,), 'report_trigger_chain')
    memberships=host.catalogue_membership_history
    _check(len(memberships)==2 and len(memberships[1])==len(memberships[0])+1 and
        all(a is b for a,b in zip(memberships[0],memberships[1])) and
        memberships[1][-1] is package.native_admission and all(a.catalogue_revision==0 for a in memberships[0])
        and package.native_admission.catalogue_revision==1,'report_membership_history')
    rows={v.work_id:v for v in final.results}
    guest=rows['need'];rendered=rows['render'];effect=rows['effect']
    _check(guest.result.output[0].value==pure.pure_need_oracle_v01(need)[need.input_value]
        and next(v.value for v in guest.invocation.inputs if v.parameter_name=='value')==need.input_value
        and rendered.invocation.inputs[0].value==guest.result.output[0].value
        and rendered.consumed_fields[0].source_artifact_id==guest.result.result_id
        and effect.consumed_fields[0].source_artifact_id==rendered.result.result_id
        and next(v.value for v in effect.invocation.inputs if v.parameter_name=='content_ref')==rendered.result.output[0].value,
        'report_guest_downstream_binding')
    _check(len(host.pure_guest_evidence)==1,'report_guest_count')
    pure.validate_pure_guest_evidence_v01(host.pure_guest_evidence[0],host=host)
    _check(host.pure_guest_evidence[0].invocation is guest.invocation,'report_guest_native_identity')
    _check(len(host.registry.action_packet_lifecycle_entries)==2 and
        sum((i,r)==(initial_rows['baseline_effect'].invocation,initial_rows['baseline_effect'].result)
            for i,r in host.completed_work)==1 and
        sum(a.work_instance_id==initial_rows['baseline_effect'].invocation.work_instance_id
            for a in host.work_attempts)==1,
        'report_old_effect_not_replayed')
    for value in (initial_rows['baseline_effect'],effect):
        entry=next(e for e in host.registry.action_packet_lifecycle_entries if e.root_bound_genesis.packet_identity.packet_id==value.invocation.packet_id)
        root_result=entry.root_bound_genesis.root_decision_projection.root_decision_result
        _check(root_result.decision=='ACCEPT' and root_result.target_root_id==host.owning_root_id
            and value.invocation.candidate_id==entry.root_bound_genesis.canonical_projection.authorization_candidate.root_packet_authorization_candidate_id,
            'report_fresh_root_effect')
    _check(final.snapshot.usage==hosts.WorkTaskUsageV01(4,0,0,1,0) and len(host.work_attempts)==4,'report_work_resources')
    return host


def validate_capability_cold_start_reuse_report_v01(report):
    """Validate only supplied typed values and retained host observations."""
    try:
        _check(type(report) is PureColdWarmReportV01,'report_type')
        cold=report.cold
        _check(type(cold) is dict and set(cold)=={'search','proposal','attempt','record','continued'},'report_cold_shape')
        cold_host=_validate_continued(cold['continued'])
        warm_host=_validate_continued(report.warm)
        _check(cold_host is not warm_host and cold['continued']['task']['need'].permission.task_id !=
            report.warm['task']['need'].permission.task_id,'report_fresh_warm_task')
        search=cold['search'];proposal=cold['proposal'];package=cold['continued']['package']
        memory.validate_pure_search_v01(search,host=cold_host)
        _check(type(search) is memory.PureNeedSearchV01 and search.need==package.need and search.result.candidate_count==0
            and search.result.candidates==() and search.query.query_id==search.result.query_id,'report_cold_search')
        _check(proposal is cold_host.pure_generation_proposals[0] and len(cold_host.pure_generation_proposals)==1
            and proposal.need==package.need and proposal.oracle==pure.pure_need_oracle_v01(package.need)
            and proposal.source_freeze==pure.pure_source_freeze_v01() and proposal.wat==cold['attempt'].source
            and cold['attempt'] is package.attempt,'report_generation_admission')
        _check(warm_host.pure_generation_proposals==(),'report_warm_generator_zero')
        memory.validate_pure_memory_record_v01(cold['record'],package=package,host=cold_host)
        memory.validate_pure_memory_retrieval_v01(report.retrieval,host=warm_host,need=report.warm['task']['need'])
        _check(report.retrieval.package is report.warm['package'] and report.retrieval.payload==cold['record'].payload
            and report.retrieval.record==cold['record'].record and report.retrieval.package.wasm==package.wasm,'report_warm_source')
        for host,resources in ((cold_host,report.cold_resources),(warm_host,report.warm_resources)):
            pure.validate_pure_resource_usage_v01(resources)
            task_id=next(p.need.permission.task_id for p in host.pure_admission_attempts)
            _check(resources==hosts.inspect_pure_need_resources_v01(host,task_id=task_id)
                and resources.admission_attempts==1 and resources.reserved_trials==256
                and resources.guest_calls==1 and resources.measured_fuel>0 and resources.measured_guest_fuel>0,'report_resource_accounting')
        _check(report.cold_resources.generation_attempts==1 and report.warm_resources.generation_attempts==0,'report_generator_resources')
        return True
    except (ValueError,TypeError,KeyError,AttributeError,IndexError):
        return False


def _plain(value):
    if value is None or type(value) in (str,int,float,bool):return value
    if type(value) is bytes:return {'base64':base64.b64encode(value).decode()}
    if type(value) in (tuple,list):return [_plain(v) for v in value]
    if type(value) in (dict,MappingProxyType):return {k:_plain(v) for k,v in value.items()}
    if type(value) is abi.KernelArtifactV01:return abi.kernel_artifact_to_plain_dict_v01(value)
    if type(value) is firewall.AdmittedCapabilityV01:return _plain(firewall.snapshot_admitted_capability_v01(value))
    if type(value) is hosts.RootWorkExecutionHostV01:
        return dict(root=value.owning_root_id,state_revision=value.state_revision,events=_plain(value.events),
            work_attempts=_plain(value.work_attempts),guest_evidence=_plain(value.pure_guest_evidence),
            registry=_plain(value.registry))
    if is_dataclass(value):return {f.name:_plain(getattr(value,f.name)) for f in fields(value) if f.name!='_origin'}
    raise ValueError('pure_projection_type:'+str(type(value)))


def capability_cold_start_reuse_report_to_plain_data_v01(report):
    if not validate_capability_cold_start_reuse_report_v01(report):raise ValueError('pure_report_invalid')
    return _plain(report)


def render_capability_cold_start_reuse_v01(report):
    return json.dumps(capability_cold_start_reuse_report_to_plain_data_v01(report),sort_keys=True,separators=(',',':'))+'\n'
