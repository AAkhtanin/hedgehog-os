"""Finite Workspace cards and a source-bound summary-to-current-save consumer."""
from dataclasses import asdict, replace
import json
from pathlib import Path
import time
from hedgehog import action_commit_packet_v02 as actions, work_execution_host_v01 as hosts
from hedgehog import outcome_feedback_v01 as feedback
from hedgehog.kernel import abi_v01 as abi, effect_firewall_v01 as fw
from . import contracts_v01 as c, capability_registry_v01 as caps, kernel_adapter_v01 as kernel
from .session_runtime_v01 import Workspace
from .semantic_roles_v01 import ControlledProvider
from .memory_adapter_v01 import SemanticMemory, MemoryProvider
from . import incident_atlas_task_v01 as required, incident_atlas_summary_v01 as summary
from . import incident_atlas_work_v01 as native


def save_v01(path, value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(c.canonical(value))


def semantic_record_v01(session):
    return dict(session=session.id,root=session.root,roles=session.semantic_responses,captures=session.captures,
        contract=session.contract,source_hashes=session.source_hashes,root_review=feedback.g35_record_to_plain_v01(session.route_review),
        results=feedback.g35_record_to_plain_v01(session.work_results),program=feedback.g35_record_to_plain_v01(session.program),
        artifact=abi.kernel_artifact_to_plain_dict_v01(session.work_artifact),
        admissions=feedback.g35_record_to_plain_v01(tuple(fw.snapshot_admitted_capability_v01(a) for a in session.catalogue[:2])))


def state_v01(session):
    return dict(session=session.id,version=session.version,status=session.status,root=session.root,
        contract=session.contract,source_hashes=dict(session.source_hashes),allowed=list(session.allowed),
        executed=len(session.executed),host_revision=session.host.revision,services=len(session.services),
        approvals=json.loads(c.canonical(session.approvals)),pending=session.pending,saved=session.saved)


def command_v01(session, op, value=None):
    before=state_v01(session);start=time.monotonic()
    try:
        session.command(op,value)
    except BaseException:
        save_v01(session.directory/'atlas_command_failure.json',dict(command=dict(op=op,value=value),
            before=before,after=state_v01(session),registry=feedback.g35_record_to_plain_v01(session.host.registry)))
        raise
    entry=session.host.registry.action_packet_lifecycle_entries[-1]
    context=session.host.registry.action_packet_fulfillment_attempt_contexts[-1]
    receipt=abi.kernel_artifact_to_plain_dict_v01(context.receipt)
    execution=fw.native_execution_evidence_from_plain_data_v01(receipt['payload']['execution_evidence'])
    return dict(command=dict(op=op,value=value),before=before,after=state_v01(session),seconds=time.monotonic()-start,
        bound=feedback.g35_record_to_plain_v01(entry.root_bound_genesis),registry=feedback.g35_record_to_plain_v01(session.host.registry),
        context=feedback.g35_record_to_plain_v01(context),receipt=receipt,execution=feedback.g35_record_to_plain_v01(execution),
        fact=session.last_prepared_fact,inputs=feedback.g35_record_to_plain_v01(execution.invocation.inputs),
        output=caps.values(execution.result.output))


def refused_v01(session, op, value):
    before=state_v01(session)
    try:session.command(op,value)
    except ValueError as error:reason=str(error)
    else:raise AssertionError('atlas_workspace_forbidden_command_executed')
    after=state_v01(session)
    c.require(before==after,'atlas_workspace_refusal_mutated_state')
    return dict(command=dict(op=op,value=value),before=before,after=after,reason=reason,
        host='NOT_REACHED',executor_delta=0,external_publication_calls=0,
        boundary='CURRENT_COMMAND_INGRESS',scope='Finite accepted command path; not an arbitrary Python process sandbox.')


def native_input_control_v01(session):
    value=dict(op='RATE',value=3)
    valid=dict(command=c.canonical(value).decode(),session=session.id,version=session.version)
    session.validate_effect(valid)
    auth,inputs,observation,review=kernel.prepare_command(session,value,dict(
        current_session=valid['session']==session.id,current_version=valid['version']==session.version,
        typed_command=c.command(value,session.allowed)==value,no_source_write=not session.contract['source_write']))
    wrong=caps.records(dict(command=('TEXT',valid['command']),session=('REFERENCE',session.id),version=('INTEGER',session.version+1)))
    clock=session.source.sample(observation);before=len(session.executed)
    token=caps.EXECUTION.set(session)
    try:
        public_validation=caps.validate_inputs_v01(session.catalogue[2].definition,wrong)
        try:
            hosts.install_current_action_v01(session.host,**auth,inputs=wrong,admission_id=session.catalogue[2].admission_id,
                expected_revision=session.host.revision,evaluation_time=clock.evaluation_time,
                evaluation_time_source=clock.evaluation_time_source,evaluation_context_id=clock.evaluation_context_id)
        except ValueError as error:reason=str(error)
        else:raise AssertionError('atlas_wrong_input_installed')
    finally:caps.EXECUTION.reset(token)
    c.require(len(session.executed)==before and not public_validation.valid,'atlas_native_input_negative')
    return dict(authorization=feedback.g35_record_to_plain_v01(auth),inputs=feedback.g35_record_to_plain_v01(inputs),
        wrong_inputs=feedback.g35_record_to_plain_v01(wrong),review=feedback.g35_record_to_plain_v01(review),
        validation=feedback.g35_record_to_plain_v01(public_validation),observation=feedback.g35_record_to_plain_v01(observation),
        session=state_v01(session),reason=reason,executor_delta=0,boundary='PUBLIC_HOST_INSTALL_AND_REAL_EXECUTION_CONTEXT_VALIDATOR')


def summary_context_v01(session, task):
    current=required.snapshot_v01(task)
    return dict(session=state_v01(session),required=current,
        independently_current=dict(session=session.id,version=session.version,source_sha256=session.source_hashes,
            required_revision=task['program'].candidate.revision_id),old_permission_valid=False)


def check_summary_v01(value, context, supplied_result=None):
    """Validate semantic assertions against independently captured native state."""
    summary.validate_v01(value)
    c.require(not value['reuse_prior_permission'],'atlas_summary_closed_permission')
    current=context['required']; independent=context['independently_current']
    c.require(value['source_version']=='CURRENT','atlas_summary_wrong_source_version')
    if supplied_result is not None:
        feedback.g35_validate_artifact_v01(supplied_result)
        c.require(current['artifact'] is not None and supplied_result==current['artifact'], 'atlas_summary_result_context')
    if value['work_status']=='COMPLETED' or value['result_ref'] is not None:
        c.require(current['snapshot']['outcome']=='COMPLETED' and current['artifact'] is not None,'atlas_summary_required_work_missing')
        c.require(value['result_ref']==current['artifact']['artifact_id'],'atlas_summary_result_context')
    c.require(current['session']==independent['session']==context['session']['session']
        and current['version']==independent['version']==context['session']['version']
        and current['snapshot']['current_revision_id']==independent['required_revision'],'atlas_summary_current_basis')
    return dict(goal=value['goal'],selection=value['selection'],source_version=independent,
        required_work=current['snapshot']['current_revision_id'],requires_current_owner_save=True)


def accept_summary_v01(session, task, value, supplied_result=None):
    context=summary_context_v01(session,task)
    projection=check_summary_v01(value,context,supplied_result)
    ref=c.identity('summary_proposal',dict(summary=value,projection=projection))
    review=kernel.root_review(session.root,'transaction:'+session.id,ref,session.id,
        dict(current_session=session.state()['current'],source_unchanged=all(c.digest(p.read_bytes())==session.source_hashes[n] for n,p in session.assets.items()),
            no_inherited_permission=not value['reuse_prior_permission']),ref,session.program.candidate.bsep_ref,
        session.program.topology_artifact.artifact_id,session.source.sample().evaluation_time,claim_value=projection)
    return dict(projection=projection,review=feedback.g35_record_to_plain_v01(review),context=context,summary=value,summary_ref=ref)


def setup_v01(directory):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=False)
    from PIL import Image
    asset=directory/'synthetic_photo.png'
    Image.new('RGB',(32,24),(70,110,180)).save(asset,format='PNG')
    cold=Workspace(directory/'previous',[asset],c.REQUEST_A,ControlledProvider(),media=None,personal_root=native.ROOT)
    return dict(directory=directory,asset=asset,cold=cold,warm=None,store=SemanticMemory(directory/'semantic_memory'),
        result=dict(profile='AT4_WORKSPACE_V01',original_sha256=c.digest(asset.read_bytes()),previous=semantic_record_v01(cold),
            W1=[],W2=[],commands=[]))


def prior_v01(run):
    cold=run['cold'];result=run['result']
    result['commands'].append(command_v01(cold,'OPEN'))
    for op,value in [('PUBLISH',dict(recipient='public',object='local_selection')),
                     ('SEND',dict(recipient='colleague@example.invalid',channel='external',object='local_selection'))]:
        result['W1'].append(refused_v01(cold,op,value))
    for op,value in [('SHELL','echo synthetic_refused'),('EXEC','synthetic_no_execution'),
                     ('WRITE',dict(path=str(run['directory']/'not_authorized.json'),value='synthetic'))]:
        result['W2'].append(refused_v01(cold,op,value))
    result['native_input']=native_input_control_v01(cold)
    result['commands'].append(command_v01(cold,'SELECT',True))
    result['commands'].append(command_v01(cold,'REQUEST_SAVE'))
    run['old_approval']=cold.approve(cold.pending)
    result['previous_approval']=dict(ref=run['old_approval'],candidate=json.loads(c.canonical(cold.pending)))
    result['recipe_id']=run['store'].remember(cold)
    result['previous_close']=cold.close('AT4_CLOSED_BEFORE_MEMORY_REUSE')
    result['old_session_refusal']=refused_v01(cold,'SAVE',run['old_approval'])
    result['previous_report']=cold.report()
    save_v01(run['directory']/'prior.json',result)


def current_v01(run):
    old=run['cold'];provider=MemoryProvider(run['store'])
    current=Workspace(run['directory']/'current',[run['asset']],c.REQUEST_A,provider,media=None,personal_root=old.root)
    run['warm']=current;result=run['result']
    c.require(old.cleanup_report['status']=='CLOSED_SUCCESS' and old.host is not current.host and old.id!=current.id
        and not current.approvals and not current.services,'atlas_workspace_fresh_lifetime')
    result['current_initial']=semantic_record_v01(current)
    result['memory_events']=run['store'].events
    result['memory_origin']=current.memory_origin
    run['task']=required.prepare_v01(current)
    result['missing_required']=required.snapshot_v01(run['task'])
    c.require(result['missing_required']['snapshot']['outcome']=='ACTIVE' and
        not result['missing_required']['snapshot']['terminal_history_refs'] and result['missing_required']['artifact'] is None,'atlas_required_not_missing')
    result['summary_input']=dict(prior_session=old.id,closed=old.cleanup_report['status'],request=current.request,
        useful_recipe=old.semantic_responses,previous_selection=old.edits,
        limits=dict(source_write=False,publication=False,old_approval_valid=False,separate_current_save_confirmation=True),
        current_session=current.id,current_source_sha256=current.source_hashes,
        outstanding=dict(task=result['missing_required']['snapshot']['policy']['task_id'],
            revision=result['missing_required']['snapshot']['current_revision_id'],status='ACTIVE',terminal_results=0,result=None),
        native_missing_snapshot_sha256=c.digest(result['missing_required']))
    save_v01(run['directory']/'summary_input.json',result['summary_input'])
    save_v01(run['directory']/'current_missing.json',result['missing_required'])


def summary_v01(run, config_path):
    result=run['result'];capture=summary.capture_v01(run['directory']/'summary_capture',result['summary_input'],config_path=config_path)
    result['summary_capture']=capture
    result['summary_accepted']=accept_summary_v01(run['warm'],run['task'],capture['output'])
    result['D1_controls']=[]
    old_result=result['previous']['artifact']
    for label,edits,substitute in (
        ('closed_permission',dict(reuse_prior_permission=True),None),
        ('false_completed',dict(work_status='COMPLETED'),None),
        ('invented_evidence',dict(result_ref='atlas:missing:result'),None),
        ('wrong_version',dict(source_version='PREVIOUS'),old_result),
        ('valid_old_result_as_current',dict(work_status='COMPLETED',result_ref=old_result['artifact_id']),old_result)):
        derivative=summary.derivative_v01(capture,edits);before=required.snapshot_v01(run['task'])
        try:accept_summary_v01(run['warm'],run['task'],derivative['output'],substitute)
        except ValueError as error:reason=str(error)
        else:raise AssertionError('atlas_summary_poison_accepted')
        c.require(required.snapshot_v01(run['task'])==before,'atlas_summary_changed_required_state')
        result['D1_controls'].append(dict(label=label,derivative=derivative,reason=reason,
            context=summary_context_v01(run['warm'],run['task']),supplied_result=substitute,
            effective_success_samples_added=0,executor_delta=0))
    result['required_completed']=required.complete_v01(run['task'],run['warm'],result['summary_accepted']['summary_ref'])
    save_v01(run['directory']/'summary_and_required.json',dict(capture=capture,accepted=result['summary_accepted'],
        controls=result['D1_controls'],completed=result['required_completed']))


def experience_v01(run):
    current=run['warm'];result=run['result'];state=state_v01(current)
    material=dict(checks=[dict(semantic_ref=result['summary_capture']['capture_id'],session_id=current.id,
        observations=[dict(observation_id='atlas:workspace:required:'+c.digest(result['required_completed']))])],
        policy=dict(predicate='Current contract, original sources and completed required Work support this selected-only save plan.',
            owning_root=current.root,operation='ews.command.v01',exact_save_confirmation_required=True),
        session=state,summary=result['summary_capture']['output'],required_work=result['required_completed'],originals=current.source_hashes)
    material=json.loads(c.canonical(material))
    result['experience'],run['experience_live']=native.experience_v01(run['directory']/'experience',material,material)
    save_v01(run['directory']/'experience.json',result['experience'])


def consume_v01(run, chosen):
    current=run['warm'];actual=run['experience_live'];expected=run['result']['experience']['after']
    c.require(chosen['artifact']==abi.kernel_artifact_to_plain_dict_v01(actual['artifact'])
        and chosen['material']==expected['material'] and chosen['output']==expected['output'],'atlas_workspace_consumed_work')
    c.require(chosen['output']['checks'][0]['healthy'] and state_v01(current)==chosen['material']['session'], 'atlas_workspace_consumption_current')
    material=dict(work_artifact_ref=chosen['artifact']['artifact_id'],output_sha256=c.digest(chosen['output']),
        current_session=current.id,current_version=current.version,selection=chosen['material']['summary']['selection'],
        summary_ref=run['result']['summary_capture']['capture_id'],source_sha256=current.source_hashes)
    ref=c.identity('consumed_workspace_work',material)
    review=kernel.root_review(current.root,'transaction:'+current.id,ref,current.id,
        dict(exact_work=chosen['artifact']['artifact_id']==actual['artifact'].artifact_id,current_session=current.state()['current'],
            source_unchanged=all(c.digest(p.read_bytes())==current.source_hashes[n] for n,p in current.assets.items())),
        ref,current.program.candidate.bsep_ref,current.program.topology_artifact.artifact_id,current.source.sample().evaluation_time,
        claim_value=material)
    return dict(material=material,review=feedback.g35_record_to_plain_v01(review))


def continuation_v01(run):
    current=run['warm'];result=run['result']
    before=len(current.executed)
    try:consume_v01(run,result['experience']['observation'])
    except ValueError as error:wrong=str(error)
    else:raise AssertionError('atlas_wrong_work_consumed')
    c.require(len(current.executed)==before,'atlas_wrong_work_effect')
    result['consumption']=consume_v01(run,result['experience']['after'])
    result['consumption']['wrong_work_refusal']=wrong
    plan=result['consumption']['material']['selection']
    rows=[command_v01(current,'OPEN')]
    for op,key in (('SELECT','selected'),('RATE','rating'),('EXPOSURE','exposure'),('CROP','crop')):
        rows.append(command_v01(current,op,plan[key]))
    rows.append(command_v01(current,'REQUEST_SAVE'))
    result['stale_approval']=refused_v01(current,'SAVE',run['old_approval'])
    approval=current.approve(current.pending)
    result['exact_approval']=dict(ref=approval,candidate=json.loads(c.canonical(current.pending)))
    rows.append(command_v01(current,'SAVE',approval))
    result['consumption']['commands']=rows
    body=(current.directory/'output/selection.json').read_bytes()
    result['sidecar']=dict(content=json.loads(body),raw=body.decode(),bytes=len(body),sha256=c.digest(body))
    result['saved_memory_id']=run['store'].remember_saved(current)
    result['current_close']=current.close('AT4_SAVED_AND_CLOSED')
    result['current_report']=current.report()
    result['memory_events']=run['store'].events
    c.require(c.digest(run['asset'].read_bytes())==result['original_sha256'] and result['current_close']['status']=='CLOSED_SUCCESS','atlas_workspace_cleanup')
    result['counts']=dict(domain_consumers=1,predictive_events=1,effective_samples=1,current_saved_sidecars=1,
        previous_saved_sidecars=0,summary_calls=1,controlled_poison_derivatives=len(result['D1_controls']),
        captured_reexecutions=0,browser_runs=0,new_D_E=0,external_business_effects=0)
    save_v01(run['directory']/'workspace.json',result)
    return result


def collect_workspace_v01(directory, *, config_path):
    run=setup_v01(directory)
    try:
        prior_v01(run);current_v01(run)
        run['result']['W3']=required.code_control_v01(run['directory']/'code_fixture',native.ROOT)
        summary_v01(run,config_path);experience_v01(run);return continuation_v01(run)
    finally:
        for key in ('warm','cold'):
            if run[key] is not None:run[key].close('AT4_FINALIZER')
