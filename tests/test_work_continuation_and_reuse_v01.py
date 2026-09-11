"""Actual bounded continuation and PURE admission controls."""
from dataclasses import replace, asdict, fields
import hashlib
import base64
import json
from pathlib import Path
import sys
import tempfile
import pytest
import test_work_composition_v01 as baseline
from hedgehog import capability_admission_v01 as pure
from hedgehog import capability_memory_binding_v01 as memory
from hedgehog import work_execution_host_v01 as hosts
from hedgehog.kernel import work_composition_v01 as work
from demo import run_capability_cold_start_reuse_v01 as demo


def emit(case, **values):
    print('U3_CASE '+json.dumps(dict(case=case,**values),sort_keys=True),flush=True)


class Calls:
    """Read-only call observation; retains code objects to make id keys exact."""
    def __init__(self, functions):
        self.codes={id(f.__code__):(f.__code__,f.__module__+'.'+f.__name__) for f in functions}
        self.calls=[]
    def observe(self,frame,event,arg):
        if event=='call' and id(frame.f_code) in self.codes:
            need=frame.f_locals.get('need')
            self.calls.append((self.codes[id(frame.f_code)][1],
                need.permission.task_id if type(need) is pure.PureCapabilityNeedV01 else None))
    def __enter__(self):
        self.previous=sys.getprofile()
        sys.setprofile(self.observe)
        return self
    def __exit__(self,*args):
        sys.setprofile(self.previous)


@pytest.fixture(scope='module')
def observed_report():
    store=Path(tempfile.mkdtemp(prefix='u3-tests-cold-warm-'))
    with Calls((pure.generate_controlled_pure_candidate_v01,)) as calls:
        report=demo.collect_capability_cold_start_reuse_v01(store_path=store)
    emit('COLD_WARM_COLLECTED',store=str(store),generator_calls=calls.calls,
        cold_resources=asdict(report.cold_resources),warm_resources=asdict(report.warm_resources),
        source_freeze=report.cold['proposal'].source_freeze)
    return report,calls,store


def test_u3_cold_warm_actual_same_task_and_canonical_report(observed_report):
    report,calls,_=observed_report
    before=demo._plain(report)
    assert demo.validate_capability_cold_start_reuse_report_v01(report) is True
    assert demo._plain(report)==before
    plain=demo.capability_cold_start_reuse_report_to_plain_data_v01(report)
    rendered=demo.render_capability_cold_start_reuse_v01(report)
    assert json.loads(rendered)==plain and rendered==json.dumps(plain,sort_keys=True,separators=(',',':'))+'\n'
    assert rendered.endswith('\n') and not rendered.endswith('\n\n')
    assert calls.calls==[(pure.generate_controlled_pure_candidate_v01.__module__+'.generate_controlled_pure_candidate_v01','task:u3:cold')]
    for continued in (report.cold['continued'],report.warm):
        task=continued['task'];initial=task['initial'];final=continued['final'];host=task['host']
        assert initial.status=='NEEDS_CAPABILITY' and final.status=='COMPLETED'
        assert final.program.candidate.task_id==initial.program.candidate.task_id
        assert all(a.definition.definition_id!=pure.MISSING_DEFINITION for a in task['common']['catalogue'])
        rows={r.work_id:r for r in final.results}
        assert rows['need'].result.output[0].value==pure.pure_need_oracle_v01(task['need'])[task['need'].input_value]
        assert rows['render'].invocation.inputs[0].value==rows['need'].result.output[0].value
        assert len(host.registry.action_packet_lifecycle_entries)==2
        assert report.retrieval.root_result.decision=='ACCEPT' and not report.retrieval.root_result.permission_created
    emit('CANONICAL_SUPPLIED_REPORT',render_bytes=len(rendered.encode()),render_sha256=hashlib.sha256(rendered.encode()).hexdigest(),
        nonmutation_scope='FULL_PUBLIC_PROJECTION_EQUAL_BEFORE_AFTER',warm_generator_calls=0)


def test_u3_changed_need_after_same_common_freeze(observed_report):
    original,_,_=observed_report
    freeze=pure.pure_source_freeze_v01()
    store=demo.LocalDRS(tempfile.mkdtemp(prefix='u3-changed-need-'))
    changed=demo.run_cold_pure_task_v01(store=store,task_id='task:u3:changed',multiplier=4,offset=9,value=31)
    assert changed['proposal'].source_freeze==freeze==original.cold['proposal'].source_freeze
    assert changed['proposal'].wat!=original.cold['proposal'].wat
    a={v.work_id:v for v in original.cold['continued']['final'].results}
    b={v.work_id:v for v in changed['continued']['final'].results}
    assert b['need'].result.output[0].value!=a['need'].result.output[0].value
    assert b['render'].invocation.inputs[0].value==b['need'].result.output[0].value
    assert b['effect'].invocation.inputs!=a['effect'].invocation.inputs
    assert demo._validate_continued(changed['continued']) is changed['continued']['task']['host']
    emit('CHANGED_SUPPORTED_NEED',before=a['need'].result.output[0].value,after=b['need'].result.output[0].value,
        actual_effect_input=[asdict(v) for v in b['effect'].invocation.inputs],source_freeze=freeze)


def test_u3_history_membership_and_no_live_callback_replay(observed_report):
    report,_,_=observed_report
    continued=report.cold['continued'];host=continued['task']['host'];initial=continued['task']['initial']
    context=work.work_continuation_context_v01(host,task_id=initial.program.candidate.task_id,expected_revision=host.state_revision)
    callbacks=tuple(f for a in host.admitted_catalogue for f in (a.input_validator,a.output_validator,a.executor))
    before=(host.state_revision,host.work_attempts,host.registry,host.catalogue_membership_history)
    with Calls(callbacks) as observed:
        historical=work.build_work_historical_output_v01(context,revision_id=initial.program.candidate.revision_id,
            work_id='baseline_effect',output_field=initial.results[0].result.output[0].parameter_name)
        view=work.inspect_work_continuation_outcome_v01(context)
        assert work.validate_work_continuation_outcome_v01(view,context=context,**continued['common'])==(True,())
    assert observed.calls==[]
    assert before==(host.state_revision,host.work_attempts,host.registry,host.catalogue_membership_history)
    assert historical.result_id==initial.results[0].result.result_id
    assert all(a is b for a,b in zip(host.catalogue_membership_history[0],host.catalogue_membership_history[1]))
    bad_catalogue=tuple(reversed(host.admitted_catalogue))
    bad={**continued['common'],'catalogue':bad_catalogue}
    assert not work.validate_work_continuation_outcome_v01(view,context=context,**bad)[0]
    emit('HISTORICAL_MEMBERSHIP',callbacks=observed.calls,original_result_id=historical.result_id,
        scope='ORIGINAL_EFFECT_PUBLIC_FIELD_REPLAY_AND_SUPPLIED_CONTINUATION_VALIDATION')


def test_u3_missing_foreign_stale_resolution_and_actual_positive():
    task=demo.build_pure_task_v01(task_id='task:u3:bindings',multiplier=2,offset=5,value=8,memory_scope='memory:u3:local')
    host,need=task['host'],task['need']
    assert work.validate_current_pure_need_v01(host,need=need)
    proposal=pure.generate_controlled_pure_candidate_v01(host,need=need,expected_revision=host.state_revision)
    _,package=pure.admit_pure_candidate_v01(host,need=need,source=proposal.wat,source_format='wat',
        contract_version=pure.CONTRACT_VERSION,expected_revision=host.state_revision)
    revision=host.state_revision;before=(host.admitted_catalogue,host.work_attempts,host.registry)
    with pytest.raises(ValueError,match='pure_stale_host_revision'):
        hosts.install_admitted_pure_capability_v01(host,package=package,need=need,expected_revision=revision-1)
    wrong=replace(need,input_value=9)
    material=asdict(wrong);del material['need_id']
    wrong=replace(wrong,need_id=pure.pure_evidence_identity_v01('pure_need',material))
    assert pure.validate_pure_need_v01(wrong)
    with pytest.raises(ValueError,match='pure_need_current_binding'):
        hosts.install_admitted_pure_capability_v01(host,package=package,need=wrong,expected_revision=revision)
    with pytest.raises(ValueError,match='pure_package_type'):
        hosts.install_admitted_pure_capability_v01(host,package=None,need=need,expected_revision=revision)
    with pytest.raises(ValueError,match='pure_foreign_admission'):
        hosts.install_admitted_pure_capability_v01(host,package=replace(package),need=need,expected_revision=revision)
    assert before==(host.admitted_catalogue,host.work_attempts,host.registry) and host.state_revision==revision
    continued=demo.continue_pure_task_v01(task,package)
    assert demo._validate_continued(continued) is host
    context=work.work_continuation_context_v01(host,task_id=need.permission.task_id,expected_revision=host.state_revision)
    ok,reasons=work.validate_pure_missing_trigger_v01(continued['trigger'],context=context)
    assert not ok and reasons==('pure_need_not_observed',)
    emit('RESOLUTION_BOUNDARIES',wrong_need='RECOMPUTED_ID_ACTUAL_INPUT_MISMATCH',stale_trigger_reason=reasons,
        positive=continued['final'].status)


def test_u3_supplied_report_binding_refusals(observed_report):
    report,_,_=observed_report
    before=demo._plain(report)
    with pytest.raises(ValueError,match='pure_foreign_admission'):
        pure.validate_admitted_pure_package_v01(report.cold['continued']['package'],
            host=report.warm['task']['host'],need=report.warm['task']['need'])
    poisons=(replace(report,cold_resources=replace(report.cold_resources,generation_attempts=0)),
        replace(report,warm_resources=replace(report.warm_resources,admission_attempts=True)),
        replace(report,warm={**report.warm,'package':report.cold['continued']['package']}),
        replace(report,retrieval=replace(report.retrieval,payload=report.retrieval.payload+b' ')),
        replace(report,warm={**report.warm,'task':{**report.warm['task'],'host':report.cold['continued']['task']['host']}}))
    for changed in poisons:assert not demo.validate_capability_cold_start_reuse_report_v01(changed)
    copied_search=replace(report.cold['search'])
    with pytest.raises(ValueError,match='pure_search_not_observed'):
        memory.validate_pure_search_v01(copied_search,host=report.cold['continued']['task']['host'])
    assert demo._plain(report)==before and demo.validate_capability_cold_start_reuse_report_v01(report)
    emit('SUPPLIED_REPORT_POISONS',rejected=len(poisons),scope='RESOURCE_TYPE_AND_COUNTS_HOST_PACKAGE_PAYLOAD_BINDINGS')


def rebuild_meaning(value, **changes):
    kwargs={f.name:getattr(value,f.name) for f in fields(value) if f.name not in
        ('meaning_record_id','meaning_record_version','local_reference_kernel_scope','creates_authority','creates_permission')}
    return memory.address.build_meaning_record_v01(**(kwargs|changes))


def test_u3_temporal_and_foreign_root_public_controls(observed_report):
    report,_,_=observed_report
    value=report.retrieval;query=value.query;meaning=value.meaning
    positive=memory.resolution.evaluate_drs_candidate_v01(semantic_address=meaning.semantic_address,query=query,meaning_record=meaning)
    assert positive.eligible_for_ranking
    equivalent=rebuild_meaning(meaning)
    assert equivalent==meaning and equivalent is not meaning
    assert memory.resolution.evaluate_drs_candidate_v01(semantic_address=equivalent.semantic_address,query=query,meaning_record=equivalent)==positive
    time=meaning.time_envelope
    kwargs={f.name:getattr(time,f.name) for f in fields(time) if f.name not in ('time_envelope_id','time_envelope_version')}
    stale_time=memory.address.build_drs_time_envelope_v01(**(kwargs|{'valid_to':1010,'ttl_seconds':10}))
    stale=rebuild_meaning(meaning,time_envelope=stale_time)
    assert stale.meaning_record_id!=meaning.meaning_record_id
    refused=memory.resolution.evaluate_drs_candidate_v01(semantic_address=stale.semantic_address,query=query,meaning_record=stale)
    assert not refused.eligible_for_ranking and refused.reason_codes
    permission=replace(report.warm['task']['need'].permission,owning_root_id='root:u3:foreign')
    foreign=replace(report.warm['task']['need'],permission=permission)
    material=asdict(foreign);del material['need_id']
    foreign=replace(foreign,need_id=pure.pure_evidence_identity_v01('pure_need',material))
    kernel,decision_input,result=memory.review_pure_memory_v01(need=foreign,transaction_id=query.query_id,
        selected_id=value.plan.retrieval_plan_id,subject=query.semantic_address_id,
        predicate='approve_controlled_memory_descent_plan_v01',claim_value=memory.resolution.retrieval_plan_to_plain_data_v01(value.plan),
        validation=memory.resolution.validate_retrieval_plan_v01(value.plan)==(True,()))
    assert result.target_root_id=='root:u3:foreign' and result.decision=='ACCEPT'
    changed=replace(value,root_kernel=kernel,root_input=decision_input,root_result=result)
    with pytest.raises(ValueError,match='pure_memory_root_binding'):
        memory.validate_pure_memory_retrieval_v01(changed,host=report.warm['task']['host'],need=report.warm['task']['need'])
    assert memory.validate_pure_memory_retrieval_v01(value,host=report.warm['task']['host'],need=report.warm['task']['need'])
    emit('TEMPORAL_AND_ROOT',same_query_time=query.evaluation_time,stale_reason=refused.reason_codes,
        foreign_root='GENUINE_ACCEPT_WRONG_OWNER_REJECTED',positive_reason=positive.reason_codes)


def proposal_store(record, need, payload, label):
    """Publicly valid untrusted record; Root approves context, not code admission."""
    store=demo.LocalDRS(tempfile.mkdtemp(prefix='u3-coherent-cache-'))
    p=record.meaning.artifact_pointers[0]
    pointer=memory.address.build_artifact_pointer_v01(storage_class=p.storage_class,object_reference=p.object_reference,
        content_sha256=hashlib.sha256(payload).hexdigest(),media_type=p.media_type,byte_length=len(payload),
        access_policy_id=p.access_policy_id,sensitivity_class=p.sensitivity_class,allowed_use_classes=p.allowed_use_classes,
        forbidden_use_classes=p.forbidden_use_classes,summary_read_permitted=p.summary_read_permitted,payload_read_permitted=p.payload_read_permitted)
    kernel,decision_input,result=memory.review_pure_memory_v01(need=need,transaction_id=need.permission.task_id,
        selected_id='proposal:u3:'+label,subject=record.meaning.semantic_address.semantic_address_id,
        predicate='record_untrusted_pure_proposal_v01',claim_value={'payload_sha256':pointer.content_sha256},
        validation=memory.address.validate_artifact_pointer_v01(pointer)==(True,()))
    original=record.meaning.authority_envelope
    authority=memory.address.build_drs_authority_envelope_v01(authority_class=original.authority_class,
        owning_local_root_id=need.permission.owning_root_id,source_root_decision_input_id=decision_input.decision_input_id,
        source_root_decision_id=result.decision_id,source_root_decision_hash=memory._root_hash(result),
        authority_scope_fingerprint=original.authority_scope_fingerprint,root_acceptance_state=original.root_acceptance_state,
        recording_component=original.recording_component)
    meaning=rebuild_meaning(record.meaning,artifact_pointers=(pointer,),source_reference_ids=(pointer.pointer_id,),
        authority_envelope=authority,content_fingerprint=pointer.content_sha256)
    content={**record.record['content'],'meaning':memory.address.meaning_record_to_plain_data_v01(meaning),
        'payload_ref':pointer.object_reference,'payload_sha256':pointer.content_sha256}
    public_record=memory.resolver.write_semantic_record(store,memory.resolver.SemanticDRSRecordInput(
        record_id=meaning.meaning_record_id,domain='pure_integer',content=content,semantic_keys=('integer','affine','u8'),
        record_type='pure_source',time_envelope=record.record['time_envelope'],
        provenance={'request_id':need.permission.task_id,'created_by':'pure_test_context'},source_refs=({'ref':need.observation_id},)))
    directory=store.root_path/'pure_payloads';directory.mkdir()
    (directory/(pointer.content_sha256+'.json')).write_bytes(payload)
    assert memory.address.validate_meaning_record_v01(meaning)==(True,())
    assert public_record['record_id']==meaning.meaning_record_id and hashlib.sha256(payload).hexdigest()==pointer.content_sha256
    return store


def test_u3_coherent_cache_version_and_wrong_guest_rejected(observed_report):
    report,_,_=observed_report
    record=report.cold['record']
    identity=b'(module (func (export "transform") (param i32) (result i32) local.get 0))'
    actual=pure.worker.run_pure_wasm_worker_v01(identity,source_format='wat',inputs=(31,))
    assert actual.status=='SUCCEEDED' and actual.trials[0][1]==31
    for label,reason in (('version','pure_memory_contract_binding'),('guest','pure_memory_readmission:pure_oracle_mismatch')):
        task=demo.build_pure_task_v01(task_id='task:u3:cache:'+label,multiplier=3,offset=7,value=31,memory_scope='memory:u3:local')
        data=json.loads(record.payload)
        if label=='version':data['contract_version']='affine-u8-v00'
        else:
            data.update(wasm=base64.b64encode(actual.wasm).decode(),wasm_sha256=hashlib.sha256(actual.wasm).hexdigest(),wat=identity.decode())
        payload=json.dumps(data,sort_keys=True,separators=(',',':')).encode()
        store=proposal_store(record,task['need'],payload,label)
        host=task['host'];attempts=host.work_attempts;catalogue=host.admitted_catalogue
        with pytest.raises(ValueError,match=reason) as failure:
            memory.retrieve_pure_memory_v01(store,host=host,need=task['need'])
        assert host.work_attempts==attempts and host.admitted_catalogue==catalogue and host.pure_generation_proposals==()
        if label=='guest':
            assert host.pure_admission_attempts[-1].reason=='pure_oracle_mismatch'
            assert len(host.pure_admission_attempts[-1].worker_result.trials)==256
        emit('COHERENT_CACHE_'+label.upper(),reason=str(failure.value),query_time=host.current_sources.evaluation_time,
            actual_admission_count=len(host.pure_admission_attempts),actual_store=str(store.root_path),
            integrity='NEW_PUBLIC_POINTER_MEANING_ROOT_CONTEXT_AND_MATCHING_PAYLOAD_DIGEST')
    assert memory.validate_pure_memory_retrieval_v01(report.retrieval,host=report.warm['task']['host'],need=report.warm['task']['need'])


def test_u3_drs_second_read_is_reserved_before_io(observed_report):
    report,_,path=observed_report
    record_bytes=sum(f.stat().st_size for f in path.glob('work/*.json'))
    expected=2*record_bytes+len(report.retrieval.payload)
    assert report.warm_resources.measured_drs_bytes==expected
    assert report.warm_resources.drs_bytes>=expected
    task=demo.build_pure_task_v01(task_id='task:u3:drs-budget',multiplier=3,offset=7,value=31,
        memory_scope='memory:u3:local',max_drs_bytes=record_bytes+1)
    host=task['host'];attempts=host.work_attempts
    with Calls((demo.LocalDRS.read_layer,demo.LocalDRS.read_record)) as calls:
        with pytest.raises(ValueError,match='pure_drs_budget') as failure:
            memory.retrieve_pure_memory_v01(demo.LocalDRS(path),host=host,need=task['need'])
    assert [name.rsplit('.',1)[-1] for name,_ in calls.calls]==['read_layer']
    usage=hosts.inspect_pure_need_resources_v01(host,task_id=task['need'].permission.task_id)
    assert usage.drs_bytes==usage.measured_drs_bytes==record_bytes
    assert usage.admission_attempts==usage.generation_attempts==0 and host.work_attempts==attempts
    emit('DRS_SECOND_READ_BUDGET',reason=str(failure.value),calls=calls.calls,reserved=usage.drs_bytes,
        measured=usage.measured_drs_bytes,positive_warm_read_bytes=expected,
        scope='FILE_SIZE_ACCOUNTED_PUBLIC_IO_NOT_OS_MONITORING')


def test_u3_h1_narrowed_revision_exhaustion_and_positive():
    for remaining in (0, 1):
        case = baseline.u2_setup(task_id='task:u3:h1:' + str(remaining))
        initial = baseline.u2_advance(case)
        first, _ = baseline.u2_revise(case, initial,
            budget=baseline.work.WorkBudgetV01(8, 24, 0, 7, remaining))
        first = baseline.u2_advance(case, first)
        context = baseline.u2_context(case)
        completed = next(v for v in first.results if v.work_id.startswith('transform:'))
        trigger = baseline.work.build_work_revision_trigger_v01(context,
            work_id=completed.work_id, output_field='transformed_ref')
        before = (case['host'].work_attempts, case['host'].registry, first.snapshot)
        with pytest.raises(ValueError, match='work_task_trigger_identity'):
            baseline.u2_revise(case, first, trigger=replace(trigger, trigger_id='trigger:foreign'))
        assert baseline.u2_context(case).snapshot == before[2]
        with pytest.raises(ValueError, match='work_task_trigger_predecessor'):
            baseline.u2_revise(case, first, trigger=replace(trigger,
                output=replace(trigger.output, task_id='task:foreign')))
        assert baseline.u2_context(case).snapshot == before[2]
        next_revision, _ = baseline.u2_revise(case, first, trigger=trigger)
        if remaining == 0:
            assert next_revision.status == 'EXHAUSTED'
            assert next_revision.reason == 'work_task_revision_exhausted'
            assert next_revision.snapshot.usage == first.snapshot.usage
            assert next_revision.snapshot.accepted_revision_ids == first.snapshot.accepted_revision_ids
            assert case['host'].work_attempts == before[0] and case['host'].registry == before[1]
        else:
            assert next_revision.status == 'ACTIVE'
            assert next_revision.snapshot.usage.revisions == 2
            final = baseline.u2_advance(case, next_revision)
            assert final.status == 'COMPLETED'
            assert len(case['host'].registry.action_packet_lifecycle_entries) == 2


def h2_setup(task_id='task:u4:h2'):
    root,device='root:u4:local','device:u4:local'
    observer=demo.mocks.admit_pure_operation_v01(operation_id='u4.observe_level',input_fields=(('reading','INTEGER'),),
        output_fields=(('observed_level','INTEGER'),),executor=demo.mocks.observe_level_v01,
        output_validator=demo.mocks.validate_level_output_v01,host_instance_ref='host:'+root)
    formatter=demo.mocks.admit_pure_operation_v01(operation_id='u3.integer_content',input_fields=(('value','INTEGER'),),
        output_fields=(('content_ref','REFERENCE'),),executor=demo.format_integer_content_v01,
        output_validator=demo.validate_integer_content_output_v01,host_instance_ref='host:'+root)
    effect=demo.mocks.admit_playback_v01(device,'host:'+root)
    catalogue=(observer,formatter,effect)
    source=demo.mocks.build_work_source_context_v01(task_id)
    semantic=demo.abi.build_kernel_artifact_v01(abi_version='v1.0',artifact_id='semantic:'+task_id,
        artifact_type='SemanticArchitectProposal',schema_version='v1',transaction_id='transaction:'+task_id,
        owner_root_id=root,source_component='semantic_architect',authority_class='ADVISORY',lifecycle_state='PROPOSED',
        payload={'pure_need':dict(contract_version=demo.pure.CONTRACT_VERSION,work_id='need',multiplier=3,offset=7),
            'provenance':'CONTROLLED_DETERMINISTIC'},trace_refs=('intent:'+task_id,),parent_refs=(source.bsep_packet['packet_id'],),
        time_envelope={'pt_created_at':'2026-01-01T00:00:00+00:00','kt_asof':'2026-01-01T00:00:00+00:00',
            'et_observed_at':None,'ct_session_anchor':'session:'+task_id,'ttl_seconds':3600,'freshness_class':'static',
            'valid_from':'2026-01-01T00:00:00+00:00','valid_to':'2026-01-01T01:00:00+00:00'})
    items=(demo.work.WorkItemV01('baseline_effect',effect.definition.definition_id,root,
        (demo.runner.work_literal_v01('content_ref','REFERENCE','content:u4:baseline'),
         demo.runner.work_literal_v01('device_ref','REFERENCE',device)),(device,),(),None,None),
        demo.work.WorkItemV01('observe',observer.definition.definition_id,root,
            (demo.runner.work_literal_v01('reading','INTEGER',31),),(),(),None,None),
        demo.work.WorkItemV01('need',demo.pure.MISSING_DEFINITION,root,
            (demo.work.WorkInputBindingV01('value',demo.work.WorkOutputBindingV01('observe','observed_level','INTEGER')),),(),('observe',),None,None),
        demo.work.WorkItemV01('render',formatter.definition.definition_id,root,
            (demo.work.WorkInputBindingV01('value',demo.work.WorkOutputBindingV01('need','value','INTEGER')),),(),('need',),None,None),
        demo.work.WorkItemV01('effect',effect.definition.definition_id,root,
            (demo.work.WorkInputBindingV01('content_ref',demo.work.WorkOutputBindingV01('render','content_ref','REFERENCE')),
             demo.runner.work_literal_v01('device_ref','REFERENCE',device)),(device,),('render',),None,None))
    common=dict(catalogue=catalogue,source_context=source,semantic_proposal=semantic)
    candidate=demo.work.build_work_program_candidate_v01(task_id=task_id,previous_revision_id=None,intent_ref='intent:'+task_id,
        bsep_ref=source.bsep_packet['packet_id'],semantic_proposal_ref=semantic.artifact_id,catalogue_revision=0,
        budget=demo.work.WorkBudgetV01(8,0,0,8,2),items=items,trigger_evidence_refs=(),**common)
    program=demo.work.materialize_work_program_v01(candidate,**common)
    policy=demo.work.build_work_task_policy_v01(candidate,**common,host_instance_ref='host:'+root,
        definition_ids=tuple(sorted([demo.pure.MISSING_DEFINITION,*[a.definition.definition_id for a in catalogue]])),resource_refs=(device,))
    permission=demo.work.build_pure_need_permission_v01(program,**common,work_id='need',memory_scope='memory:u4:local')
    observations=(demo.runner.build_work_dependency_v01(device,root)[2],)
    bridge=demo.action.build_logical_time_bridge_v01(origin_utc_epoch_seconds=1000,seconds_per_tick=1,bridge_policy_version='u1.controlled_ticks.v01')
    trusted=demo.mocks.TrustedMockWorkSourceV01(observations,bridge,1014,'u1.controlled_utc','context:u1:dispatch')
    host=demo.hosts.build_root_work_execution_host_v01(owning_root_id=root,
        registry=demo.action.build_empty_action_commit_packet_registry_v02(),catalogue=catalogue,packet_bindings=(),
        current_dependency_observations=observations,logical_time_bridge=bridge,trusted_source=trusted,
        task_policies=(policy,),pure_need_permissions=(permission,))
    context=demo.work.enroll_work_program_v01(host,program,**common,expected_revision=host.state_revision)
    initial=demo.work.advance_work_program_v01(program,**common,host_map={root:host},continuation_context=context,
        action_authorizers={root:demo.runner.authorize_resolved_work_v01})
    if initial.status!='NEEDS_CAPABILITY':raise RuntimeError('H2_INITIAL_STATE')
    context=demo.work.work_continuation_context_v01(host,task_id=task_id,expected_revision=host.state_revision)
    need=demo.work.observe_missing_pure_need_v01(context)
    proposal=demo.pure.generate_controlled_pure_candidate_v01(host,need=need,expected_revision=host.state_revision)
    attempt,package=demo.pure.admit_pure_candidate_v01(host,need=need,source=proposal.wat,source_format='wat',
        contract_version=demo.pure.CONTRACT_VERSION,expected_revision=host.state_revision)
    if not attempt.admitted or package is None:raise RuntimeError('H2_ADMISSION')
    resolution=demo.hosts.install_admitted_pure_capability_v01(host,package=package,need=need,expected_revision=host.state_revision)
    context=demo.work.work_continuation_context_v01(host,task_id=task_id,expected_revision=host.state_revision)
    trigger=demo.work.build_pure_missing_trigger_v01(context,need=need,resolution=resolution)
    historical=demo.work.build_work_historical_output_v01(context,revision_id=initial.program.candidate.revision_id,
        work_id='observe',output_field='observed_level')
    if demo.work.validate_work_historical_output_v01(historical,context=context)!=(True,()):raise RuntimeError('H2_GENUINE_HISTORY')
    return dict(host=host,initial=initial,need=need,package=package,proposal=proposal,attempt=attempt,
        resolution=resolution,context=context,trigger=trigger,historical=historical,common={**common,'catalogue':host.admitted_catalogue})


def h2_items(case,mode='historical',historical=None):
    old=case['initial'].program.candidate
    original=next(i for i in old.items if i.work_id=='need')
    if mode=='historical':
        inputs=(demo.work.WorkInputBindingV01('value',case['historical'] if historical is None else historical),)
        dependencies=()
    elif mode=='literal':inputs=(demo.runner.work_literal_v01('value','INTEGER',31),);dependencies=()
    else:inputs=original.inputs;dependencies=original.depends_on
    new=replace(original,definition_id=case['resolution'].definition_id,depends_on=dependencies,
        inputs=tuple(sorted((*inputs,demo.runner.work_literal_v01('package_ref','REFERENCE',case['package'].package_id)),key=lambda b:b.input_field)))
    return tuple(new if i.work_id=='need' else i for i in old.items
        if i.work_id!='baseline_effect' and (mode=='retain' or i.work_id!='observe'))


def h2_revise(case,items):
    return demo.work.revise_work_program_v01(case['context'],previous_revision_id=case['initial'].program.candidate.revision_id,
        trigger=case['trigger'],items=items,budget=demo.work.WorkBudgetV01(8,0,0,6,1),**case['common'])


def test_u4_h2_actual_predecessor_history_and_same_task_completion():
    with Calls((demo.mocks.observe_level_v01,)) as observed:
        case = h2_setup()
        host = case['host']
        initial = case['initial']
        old_rows = {r.work_id: r for r in initial.results}
        old_bytes = demo._plain((old_rows['observe'], old_rows['baseline_effect'], initial.snapshot))
        historical = replace(case['historical'])
        assert historical is not case['historical'] and historical == case['historical']
        assert work.validate_work_historical_output_v01(historical, context=case['context']) == (True, ())
        revised = h2_revise(case, h2_items(case, historical=historical))
        context = work.work_continuation_context_v01(host, task_id=initial.program.candidate.task_id,
            expected_revision=host.state_revision)
        assert work.validate_work_program_candidate_v01(revised.program.candidate,
            continuation_context=context, **case['common']) == (True, ())
        assert work.materialize_work_program_v01(revised.program.candidate,
            continuation_context=context, **case['common']) == revised.program
        final = work.advance_work_program_v01(revised.program, **case['common'],
            host_map={host.owning_root_id: host}, continuation_context=context,
            action_authorizers={host.owning_root_id: demo.runner.authorize_resolved_work_v01})
        context = work.work_continuation_context_v01(host, task_id=initial.program.candidate.task_id,
            expected_revision=host.state_revision)
        assert work.validate_work_continuation_outcome_v01(final, context=context, **case['common']) == (True, ())
    assert len(observed.calls) == 1
    assert final.status == 'COMPLETED'
    rows = {r.work_id: r for r in final.results}
    assert set(rows) == {'need', 'render', 'effect'}
    assert rows['need'].invocation.inputs[1].value == historical.value.value == 31
    assert rows['need'].result.output[0].value == 100
    assert rows['render'].invocation.inputs[0].value == 100
    assert rows['effect'].result.outcome == 'SUCCEEDED'
    assert final.snapshot.policy == initial.snapshot.policy
    assert final.snapshot.usage.compute_units == 5 and final.snapshot.usage.revisions == 1
    assert final.program.candidate.task_id == initial.program.candidate.task_id
    assert demo._plain((old_rows['observe'], old_rows['baseline_effect'], initial.snapshot)) == old_bytes
    rebuilt = work.build_work_historical_output_v01(context, revision_id=initial.program.candidate.revision_id,
        work_id='observe', output_field='observed_level')
    assert rebuilt == historical
    assert len(host.registry.action_packet_lifecycle_entries) == 2
    emit('U4_H2_COMPLETED', calls=observed.calls, initial=demo._plain(initial), final=demo._plain(final),
        historical=asdict(historical), scope='ACTUAL_SINGLE_TASK_RETAINED_PREDECESSOR_AND_FRESH_ROOT_MOCK_EFFECT')


def test_u4_h2_coherent_history_refusals_and_public_candidate_validation():
    case = h2_setup('task:u4:h2:negative')
    host = case['host']
    before = (host.state_revision, host.work_attempts, host.registry, case['context'].snapshot)
    good = case['historical']
    wrong_value = demo.action.build_action_effect_parameter_record_v01(
        parameter_name='observed_level', value_type='INTEGER', value=32)
    foreign = h2_setup('task:u4:h2:other')['historical']
    controls = (
        ('value', replace(good, value=wrong_value), 'work_historical_actual_field'),
        ('result', replace(good, result_id='result:other'), 'work_historical_provenance'),
        ('artifact', replace(good, result_artifact_ref='artifact:other'), 'work_historical_provenance'),
        ('task', replace(good, task_id='task:other'), 'work_historical_foreign_task'),
        ('actual_other_task', foreign, 'work_historical_foreign_task'),
    )
    for label, history, reason in controls:
        assert work.validate_work_historical_output_v01(history, context=case['context']) == (False, (reason,))
        with pytest.raises(ValueError, match='^' + reason + '$') as failure:
            h2_revise(case, h2_items(case, historical=history))
        assert (host.state_revision, host.work_attempts, host.registry, case['context'].snapshot) == before
        emit('U4_H2_HISTORY_' + label, reason=str(failure.value), historical=asdict(history))
    for mode, reason in (('literal', 'pure_revision_missing_item_binding'),
                         ('retain', 'work_task_terminal_rewrite'),
                         ('omit', 'pure_revision_missing_item_binding')):
        with pytest.raises(ValueError, match='^' + reason + '$') as failure:
            h2_revise(case, h2_items(case, mode=mode))
        assert (host.state_revision, host.work_attempts, host.registry, case['context'].snapshot) == before
        emit('U4_H2_' + mode, reason=str(failure.value))
    items = h2_items(case)
    original = case['initial'].program.candidate
    context = replace(case['context'], trigger=case['trigger'])
    kwargs = dict(task_id=original.task_id, previous_revision_id=original.revision_id,
        intent_ref=original.intent_ref, bsep_ref=original.bsep_ref, semantic_proposal_ref=original.semantic_proposal_ref,
        catalogue_revision=case['resolution'].membership_epoch, budget=work.WorkBudgetV01(8,0,0,6,1),
        trigger_evidence_refs=(case['trigger'].trigger_id,), continuation_context=context, **case['common'])
    candidate = work.build_work_program_candidate_v01(items=items, **kwargs)
    assert work.validate_work_program_candidate_v01(candidate, continuation_context=context, **case['common']) == (True, ())
    with pytest.raises(ValueError, match='^pure_revision_missing_item_binding$'):
        work.build_work_program_candidate_v01(items=h2_items(case, mode='literal'), **kwargs)
    substituted = replace(candidate, items=h2_items(case, mode='literal'))
    assert work.validate_work_program_candidate_v01(substituted, continuation_context=context,
        **case['common']) == (False, ('pure_revision_missing_item_binding',))
    with pytest.raises(ValueError, match='^pure_revision_missing_item_binding$'):
        work.materialize_work_program_v01(substituted, continuation_context=context, **case['common'])
    assert (host.state_revision, host.work_attempts, host.registry, case['context'].snapshot) == before
    emit('U4_H2_PUBLIC_BOUNDARIES', builder=True, validator=True, materializer=True,
        state_unchanged=True, positive_candidate=demo._plain(candidate))
