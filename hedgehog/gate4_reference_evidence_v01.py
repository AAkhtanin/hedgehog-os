"""G43 finite safe-derived saved proof. No collection or live authority recovery.

The G4-specific publication binds exact native originals separately from supported
projections. A test-supplied pin is not independent review or source admission.
"""
import hashlib
import json
import ast
import importlib
import importlib.metadata
import sys
from pathlib import Path, PurePosixPath

from hedgehog.domains.airline import gate4_reference_adapter_v01 as a
from hedgehog.gate4_reference_contracts_v01 import ReferenceValueV01
from hedgehog.gate4_strategy_reference_v01 import evaluate_reference_strategy_v01
from hedgehog.gate4_pressure_budget_v01 import validate_reference_allocation_v01

PROFILE='G43_SAVED_PROOF_V01'
LIMIT=32*1024*1024


def checker_sources_v44():
    """Conservative repository import closure, including local semantic imports.

    Read installed modules, never evidence-package code. Every discovered module
    is compared using its actual imported origin, including preloaded modules.
    The detached caller pin binds all bytes, not this function's own assertions.
    """
    root=Path(__file__).resolve().parents[1]
    pending=['hedgehog.gate4_reference_evidence_v01','hedgehog.gate4_reference_runtime_v01']
    found={}
    while pending:
        name=pending.pop()
        if name in found:continue
        module=importlib.import_module(name)
        path=Path(module.__file__).resolve()
        relative=name.replace('.','/')+('/__init__.py' if hasattr(module,'__path__') else '.py')
        found[name]=dict(path=relative,origin=str(path),**_body(path))
        package=name if hasattr(module,'__path__') else name.rpartition('.')[0]
        tree=ast.parse(path.read_bytes())
        candidates=[]
        for node in ast.walk(tree):
            if isinstance(node,ast.Import):candidates.extend(n.name for n in node.names)
            elif isinstance(node,ast.ImportFrom):
                base=importlib.util.resolve_name('.'*node.level+(node.module or ''),package) if node.level else node.module or ''
                candidates.append(base);candidates.extend(base+'.'+n.name for n in node.names if n.name!='*')
        # Import package initializers are executable dependencies too.
        candidates.extend('.'.join(name.split('.')[:i]) for i in range(1,len(name.split('.'))))
        for dependency in candidates:
            if not dependency.startswith(('hedgehog','demo.')):continue
            p=root/dependency.replace('.','/')
            if p.with_suffix('.py').is_file() or (p/'__init__.py').is_file():pending.append(dependency)
    return dict(sorted(found.items()))


def checker_environment_v44():
    return dict(implementation=sys.implementation.name,python=sys.version,
        executable=_body(Path(sys.executable).resolve()),
        distributions={name:importlib.metadata.version(name) for name in ('jsonschema','referencing')})


def validate_history_subject_v44(snapshot,records,meaning):
    """A valid same-Root ACCEPT is insufficient without its exact recorded subject."""
    from hedgehog.outcome_feedback_consumer_v01 import identity
    inp,result=a.feedback.g35_validate_root_v01(records)
    key=snapshot['snapshot_id'];root=snapshot['prior']['history_key']['local_root_scope_id']
    proposal=dict(snapshot_id=key,expected_head=snapshot['predecessor'],source_pins=snapshot['source_pins'],
        fold_id=snapshot['fold']['fold_id'],prior_id=snapshot['prior']['prior_id'],corrections=snapshot['corrections'],
        root=root,epoch=snapshot['epoch'],evaluated_at=snapshot['evaluated_at'])
    require(result.decision=='ACCEPT' and result.target_root_id==inp.target_root_id==root
        and result.selected_candidate_id==key and inp.transaction_id=='g34:history:'+key,'history_exact_subject')
    expected='g34:request:'+identity('request',dict(root=root,transaction=inp.transaction_id,
        candidates={key:proposal},predicate='g34_record_exact_history',now=snapshot['evaluated_at']))
    require(inp.root_review_packet.request_id==expected,'history_recording_payload')
    plain=a.plain_v01(inp);auth=meaning['authority_envelope']
    claim=a.semantic.build_normalized_claim_v01(claim_id=key,subject=key,predicate='g34_record_exact_history',
        object_or_value=proposal,time_envelope_ref='g34:time:'+str(snapshot['evaluated_at']),
        provenance_refs=(key,),evidence_refs=('binding:'+key,),confidence_micros=1000000,
        source_role='deterministic_runtime',source_mode='DETERMINISTIC')
    require(plain['root_review_packet']['synthesis_proposal']['normalized_claims']==[a.semantic.semantic_work_to_plain_dict_v01(claim)],'history_exact_candidate_payload')
    require(plain['temporal_state']['time_envelope_ref']=='g34:time:'+str(snapshot['evaluated_at'])
        and plain['post_vv_bundle']['required_evidence_refs']==[key]
        and plain['post_vv_bundle']['provided_evidence_refs']==[key],'history_recording_time_evidence')
    require(auth['source_root_decision_input_id']==inp.decision_input_id
        and auth['source_root_decision_id']==result.decision_id
        and auth['source_root_decision_hash']==a.digest_v01(result)
        and meaning['safe_summary']==key and meaning['content_fingerprint']==identity('snapshot_body',snapshot),
        'history_meaning_authority')


def validate_observation_copies_v44(observed,initial,saved):
    p=observed['predictive'];native=observed['native'];n=native['native']
    require(p['native_source']==native and p['claim_artifact']==observed['claim']
        and p['result_artifact']==observed['artifact'],'observation_cross_copy')
    artifact=initial['artifact'];program=a.feedback.g35_record_from_plain_v01(saved['initial_program'])
    rows=a.feedback.g35_record_from_plain_v01(saved['initial_results']);require(len(rows)==1,'observation_one_work')
    material=json.loads(rows[0].invocation.inputs[0].value);output=_outputs(rows[0])['material']
    inp,result=a.feedback.g35_validate_root_v01(observed['root_records'])
    require(observed['artifact']==artifact and n['plan_artifact_ref']==program.topology_artifact.artifact_id
        and n['result_artifact_ref']==artifact['artifact_id'] and n['material_sha256']==a.digest_v01(material)
        and n['dependencies_sha256']==a.digest_v01(material) and n['output_sha256']==a.digest_v01(output)
        and n['root_decision_ref']==result.decision_id and inp.transaction_id==artifact['transaction_id']
        and n['work_count']==1 and n['time_envelope']==artifact['time_envelope'],'observation_actual_cold_work')
    observation=a.feedback.build_outcome_observation_v01(source_bundle=a.feedback.PredictiveOutcomeSourceContextV01(a.canonical_v01(p)),
        profile=a.feedback.PREDICTIVE_SOURCE_PROFILE_ID,
        explicit_times={k:observed['observation'][k] for k in ('ingested_time','evaluated_at','timestamp')})
    require(json.loads(observation.canonical)==observed['observation'],'observation_fields_times_occurrence')


def require(value,reason):
    if not value:raise ValueError('g43_saved:'+reason)


def _pairs(items):
    out={}
    for key,value in items:
        require(key not in out,'duplicate_json_key');out[key]=value
    return out


def read_json_v01(path):
    p=Path(path);require(p.is_file() and not p.is_symlink() and p.stat().st_size<=LIMIT,'file_bound')
    return json.loads(p.read_bytes(),object_pairs_hook=_pairs,parse_constant=lambda s:require(False,'nonfinite'))


def _path(name):
    require(type(name) is str and name and str(PurePosixPath(name))==name and
        not PurePosixPath(name).is_absolute() and '..' not in PurePosixPath(name).parts and '\\' not in name,'safe_path')
    return name


def _body(path):
    path=Path(path);require(path.is_file() and not path.is_symlink() and path.stat().st_size<=LIMIT,'file_bound')
    raw=path.read_bytes()
    return dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest())


def _write(path,value):
    Path(path).write_bytes(a.canonical_v01(value))


def _outputs(row):
    return {v.parameter_name:json.loads(v.value) for v in row.result.output}


def _work_records(saved,enrolled,completed,initial):
    """Validate admitted saved executions and exact finite causal input relations.

    This intentionally does not call the Host-bearing Work validator. Observation
    authenticity depends on the independent publication pin, not these DTOs.
    """
    f=a.feedback;w=a.work;abi=a.abi
    admissions=f.g35_record_from_plain_v01(saved['admissions']);by_id={x.admission_id:x for x in admissions}
    require(len(by_id)==len(admissions)==3,'admission_inventory')
    for admitted in admissions:
        require(admitted.definition.effect_kind=='PURE' and not admitted.definition.resource_refs,'pure_catalogue')
    all_rows=[];old={};artifact_ids={}
    for phase,container in (('initial',initial['result']),('final',completed['final'])):
        program=f.g35_record_from_plain_v01(saved[phase+'_program'])
        rows=f.g35_record_from_plain_v01(saved[phase+'_results'])
        require(a.plain_v01(program)==container['program'] and a.plain_v01(rows)==container['results'],'original_work_records')
        candidate=program.candidate
        require(candidate.revision_id==w._revision(candidate) and tuple(r.work_id for r in rows)==program.ordered_work_ids==w._order(candidate.items),'work_revision_order')
        top=a.plain_v01(program.topology_artifact);artifact=initial['artifact'] if phase=='initial' else completed['artifact']
        f.g35_validate_artifact_v01(top);f.g35_validate_artifact_v01(artifact)
        payload=w._payload(dict(topology_ref=top['artifact_id'],work_results=[w._plain(r) for r in rows]),'result_payload')
        require(artifact['payload']==payload and artifact['artifact_id']==w._identity('work_results',payload)
            and artifact['parent_refs']==[top['artifact_id']] and artifact['time_envelope']==top['time_envelope'],'result_artifact_relation')
        require(top['artifact_id']==w._identity('work_topology',top['payload']) and
            top['payload']['work_program']==w._plain(candidate) and top['payload']['ordered_work_ids']==list(program.ordered_work_ids),'topology_relation')
        require(top['transaction_id']==enrolled['proposal']['transaction_id'] and top['owner_root_id']==a.ROOT
            and artifact['owner_root_id']==a.ROOT and artifact['transaction_id']==top['transaction_id'],'work_root_transaction')
        current={};items={i.work_id:i for i in candidate.items}
        for row in rows:
            item=items[row.work_id];inv=row.invocation;result=row.result
            require(row.status=='COMPLETED' and row.reasons==() and result.outcome=='SUCCEEDED','completed_row')
            require(inv.admission_id in by_id and not a.firewall.validate_capability_execution_result_v01(result,inv,by_id[inv.admission_id]),'public_saved_execution_result')
            require((row.task_id,row.revision_id)==(candidate.task_id,candidate.revision_id) and inv.task_id==candidate.task_id
                and inv.owning_root_id==item.owning_root_id==a.ROOT and inv.definition_id==item.definition_id
                and inv.work_instance_id==w._work_ref(candidate,item),'work_identity')
            require(all(k in current for k in item.depends_on) and item.guard is None,'work_dependencies')
            inputs=[];refs=[]
            for b in item.inputs:
                source=b.source
                if type(source) is w.WorkLiteralV01:value=source.value
                else:
                    historical=type(source) is w.WorkHistoricalOutputV01
                    require(historical or type(source) is w.WorkOutputBindingV01,'input_kind')
                    pool=old if historical else current
                    require(source.predecessor_work_id in pool,'causal_predecessor')
                    previous=pool[source.predecessor_work_id]
                    value=next(v for v in previous.result.output if v.parameter_name==source.output_field)
                    require(value.value_type==source.expected_type,'causal_type')
                    if historical:
                        require((source.task_id,source.revision_id,source.invocation_id,source.result_id,source.admission_id,source.result_artifact_ref,source.value)==
                            (candidate.task_id,previous.revision_id,previous.invocation.invocation_id,previous.result.result_id,
                             previous.invocation.admission_id,artifact_ids[previous.work_id],value),'historical_input')
                        traces=(candidate.task_id,candidate.revision_id,source.revision_id,source.invocation_id,source.result_artifact_ref)
                    else:
                        require(source.predecessor_work_id in item.depends_on,'current_input_dependency')
                        traces=(candidate.task_id,candidate.revision_id,previous.invocation.invocation_id,item.work_id)
                    refs.append(abi.build_causal_consumption_ref_v01(producer_actor_id=previous.work_id,source_artifact_id=previous.result.result_id,
                        output_field='/'+source.output_field.replace('~','~0').replace('/','~1'),consumer_component='work_composition',
                        downstream_artifact_id=inv.work_instance_id,decision_effect='bind_input',disposition='USED',
                        reason_code='used:actual_historical_output_field' if historical else 'used:actual_output_field',trace_refs=traces))
                inputs.append(a.actions.ActionEffectParameterRecordV01(b.input_field,value.value_type,value.value))
            require(tuple(sorted(inputs,key=lambda v:v.parameter_name))==inv.inputs and tuple(refs)==row.consumed_fields,'actual_causal_fields')
            values={v.parameter_name:json.loads(v.value) for v in inv.inputs}
            operation=by_id[inv.admission_id].definition.operation_id
            expected=(a.checks.evaluate_v01(values['material']) if operation=='atlas.airline.constraint' else
                a.quantum_result_v42(values['material']) if operation=='g42.airline.quantum' else a.strategy_work_result_v42(values))
            require(_outputs(row)=={'material':expected},'actual_domain_output')
            current[row.work_id]=row
            require(any(x['invocation']==a.plain_v01(inv) and x['result']==a.plain_v01(result) and x['disposition']=='COMPLETED'
                for x in completed['attempts']),'attempt_result_link')
        all_rows.extend(rows);old.update(current);artifact_ids.update({r.work_id:artifact['artifact_id'] for r in rows})
    require(len(completed['attempts'])==len(all_rows)==9 and len({r.invocation.work_instance_id for r in all_rows})==9,'unique_nine_units')
    return all_rows


def _roots(records,plain,basis,artifact,recommendation):
    require(set(records)==set(plain['reviews'])==set(a.ROOTS),'root_inventory')
    for root,saved in records.items():
        inputs,result=a.feedback.g35_validate_root_v01(saved)
        decoded=[a.feedback.g35_record_from_plain_v01(v) for v in saved]
        require(a.plain_v01(decoded)==plain['reviews'][root],'root_originals')
        local=plain['local'][root]
        require(inputs.root_review_packet.request_id=='g42:review:'+a.digest_v01(local) and
            plain['reviews'][root][1]['post_vv_bundle']['bundle_id']=='g42:current_use:'+a.digest_v01(local),'root_local_input_binding')
        a.validate_current_basis_v43(basis,local['now'])
        require(inputs.target_root_id==result.target_root_id==root and result.decision=='ACCEPT'
            and inputs.transaction_id==artifact['transaction_id'] and result.selected_candidate_id==recommendation,'root_current_result')
        require(local['root']==root and local['producer']==artifact and local['source']==basis['domain']['snapshot']['fields']['candidate_set_digest'],'root_source_result_link')
        consent=local['consent']
        if root in (a.ROOT,a.binding.BANK_ROOT_ID):
            require(consent is not None and consent['root_id']==root and consent['offer_id']==local['subject']
                and consent['source_digest']==local['source'] and consent['max_amount']>=local['terms']['amount']
                and consent['currency']==local['terms']['currency'] and consent['purpose']=='PREPARATION_ONLY','independent_consent')


def validate_saved_story_v01(directory):
    """Recompute finite supported relations at recorded times, never current permission."""
    root=Path(directory);read=lambda p:read_json_v01(root/p)
    domain=read('original_domain.json')['domain'];config=read('frozen_configuration.json')
    observed=read('observed_g3.json');record=read('history_recorded.json');head=read('history/HEAD.json')
    require(head==record['head'],'history_head')
    snapshot=a.history.HistorySnapshotV01(a.canonical_v01(record['snapshot'])).to_plain_data()
    payload=root/'history/epochs'/(head['snapshot_id']+'.payload.json')
    stored_path=root/'history/epochs'/(head['snapshot_id']+'.json');stored=read_json_v01(stored_path)
    descriptor_path=root/'history/epochs'/(head['snapshot_id']+'.descriptor.json');descriptor=read_json_v01(descriptor_path)
    require(_body(stored_path)['sha256']==head['body_sha256'] and read_json_v01(payload)==stored['snapshot']==snapshot,'history_record_bytes')
    require(_body(descriptor_path)['sha256']==head['descriptor_sha256'] and descriptor==dict(snapshot_id=head['snapshot_id'],
        history_key=snapshot['prior']['history_key'],meaning=stored['meaning'],root_review=stored['review'],
        body_sha256=head['body_sha256'],prior_id=snapshot['prior']['prior_id']) and stored['meaning']['meaning_record_id']==head['record_id'],'history_descriptor_head')
    recording_input,recording_result=a.feedback.g35_validate_root_v01(record['root_records'])
    validate_history_subject_v44(snapshot,record['root_records'],stored['meaning'])
    require(a.plain_v01([a.feedback.g35_record_from_plain_v01(x) for x in record['root_records']])==record['review']
        and a.plain_v01(recording_result)==stored['review']['result'] and recording_result.decision=='ACCEPT'
        and recording_result.target_root_id==a.ROOT,'history_recording_root')
    observed_input,observed_result=a.feedback.g35_validate_root_v01(observed['root_records'])
    require(observed_result.decision_id==observed['native']['native']['root_decision_ref'] and
        observed_input.transaction_id==observed['artifact']['transaction_id'],'observation_root')
    predictive=a.feedback.PredictiveOutcomeSourceContextV01(a.canonical_v01(observed['predictive']))
    ofe=a.feedback.build_outcome_feedback_v01(observation=a.feedback.build_outcome_observation_v01(source_bundle=predictive,
        profile=a.feedback.PREDICTIVE_SOURCE_PROFILE_ID,explicit_times={k:observed['observation'][k] for k in ('ingested_time','evaluated_at','timestamp')}),
        source_bundle=predictive,profile=a.feedback.PREDICTIVE_SOURCE_PROFILE_ID)
    require(json.loads(ofe.canonical)==observed['feedback'],'feedback_from_actual_observation')
    event=a.calibration.bind_outcome_feedback_event_v01(ofe,source_bundle=predictive,profile=a.feedback.PREDICTIVE_SOURCE_PROFILE_ID)
    fold=a.calibration.bounded_gt_event_fold_v01((event,),evaluated_at=snapshot['evaluated_at'])
    prior=a.calibration.fold_avf_history_prior_v01((event,),evaluated_at=snapshot['evaluated_at']).to_plain_data()
    require(snapshot['fold']==fold.to_plain_data() and snapshot['updates']==[u.to_plain_data() for u in fold.updates]
        and snapshot['prior']==prior and snapshot['event_refs']==[observed['feedback']['feedback_id']]
        and snapshot['source_pins']=={observed['feedback']['feedback_id']:hashlib.sha256(event.source_canonical).hexdigest()},'history_source_reduction')
    results={}
    for label in ('cold','contrast','warm'):
        original=read(label+'/enrolled.json');before=read(label+'/allocation_before_install.json');done=read(label+'/completed_work.json')
        initial=read(label+'/initial_completed.json');saved=read(label+'/portable_records.json');hold=read(label+'/domain_consumption.json')
        basis=before['basis'];material=before['final_material'];proposal=original['proposal']
        require(basis['domain']==domain and basis['configuration']==config and basis['policy']==original['policy']
            and basis['source']==original['source'] and basis['usage']==initial['result']['snapshot'],'native_original_basis')
        view=a.projection_view_v43(basis,proposal)
        strategy=a.derive_strategy_v42(view,basis)
        require(strategy==before['strategy_inputs'],'independent_strategy_projection')
        report=evaluate_reference_strategy_v01(strategy,independently_bound_context=strategy['context']).plain()
        expected=a.derive_budget_from_originals_v43(basis,proposal,material)
        require(expected==before['budget'],'independent_budget_projection')
        allocation=validate_reference_allocation_v01(before['allocation'],inputs=expected['pressure_inputs'],current_budget_context=expected).plain()
        rows=_work_records(saved,original,done,initial)
        if label=='cold':validate_observation_copies_v44(observed,initial,saved)
        final_values={v.parameter_name:json.loads(v.value) for v in rows[-1].invocation.inputs}
        require(final_values['allocation_proof']==dict(profile='G43_ALLOCATION_WORK_PROOF_V01',basis=basis,proposal=proposal,budget=expected,allocation=allocation),'work_accepted_allocation_proof')
        output=_outputs(rows[-1])['material']
        require(output==done['output'] and output['strategy_report']==report and output['allocation_identity']==ReferenceValueV01('allocation_report',allocation).identity,'actual_final_consumption')
        for state,spent,revisions in ((original['snapshot'],0,0),(initial['result']['snapshot'],1,0),(done['final']['snapshot'],9,1)):
            require(state['policy']==original['policy'] and state['usage']['compute_units']==spent and state['usage']['revisions']==revisions
                and state['usage']['model_calls']==0,'original_cap_progression')
        require(original['policy']['max_compute_units']==9 and done['after']['usage']['compute_units']==9,'original_cap')
        _roots(saved['roots'],read(label+'/reviews.json'),basis,done['artifact'],report['recommendation'])
        _roots(saved['current_roots'],hold['current_reviews'],basis,done['artifact'],report['recommendation'])
        require(a.validate_current_basis_v43(basis,hold['current_use']['evaluation_time'])==hold['current_use'],'current_use_event')
        offer=next(r for r in view['snapshot'].authoritative_offer_records if a.digest_v01(a.plain_v01(r))==a.digest_v01(hold['current_reviews']['local'][a.ROOT]['terms']))
        from hedgehog.gate4_reference_runtime_v01 import local_id_v01
        require(local_id_v01('offer',offer.offer_id)==report['recommendation'] and hold['hold']['offer_id']==offer.offer_id
            and hold['hold']['amount']==offer.amount and hold['hold']['currency']==offer.currency and hold['status']=='PREPARATION_ONLY_NOT_EXECUTED','selected_offer_hold_link')
        records=a.feedback.g35_record_from_plain_v01(read(label+'/domain_records.json'))
        require(a.plain_v01(records)=={k:hold[k] for k in records},'domain_original_records')
        selection=a.binding.build_selection_input_v01(a.binding.build_valid_airline_bsep_projection_ref_v01(),view['constraints'],view['snapshot'])
        rr=a.binding.validate_airline_root_selected_offer_resolution_v01(selection,view['snapshot'],records['evidence'],records['decision'],records['resolution'])
        hr=a.binding.validate_airline_semantic_hold_contract_binding_v01(records['resolution'],records['hold'],records['binding'],resolution_report=rr)
        pr=a.binding.corridor_contracts.validate_airline_hold_commit_packet_v01(records['offer_packet'],records['hold'],records['contract_context'])
        require(all(x.validation_status=='PASS' for x in (rr,hr,pr)),'public_saved_hold_validation')
        history=basis['history']
        if label=='warm':
            bridge=history['bridge'];a.feedback.g35_validate_artifact_v01(bridge);p=bridge['payload']
            require(p['head']==head and p['prior']==prior and p['history_key']==prior['history_key'] and
                p['current_transaction_ref']==proposal['transaction_id'] and bridge['owner_root_id']==a.ROOT,'history_current_bridge')
            require(history['payload_sha256']==hashlib.sha256(a.canonical_v01(snapshot)).hexdigest()
                and history['descent']['opened_record_ids']==[head['record_id']] and history['review']['result']['decision']=='ACCEPT','root_approved_opened_prior')
            require(snapshot['valid_from']<=p['evaluated_at']<snapshot['valid_to'] and
                p['evaluated_at']==basis['host_sources']['evaluation_time'],'history_event_time')
            for event_row in read(label+'/current_use.json'):
                require(snapshot['valid_from']<=event_row['evaluation_time']<snapshot['valid_to'],'history_consumption_expired')
        else:require(not history.get('bridge') and not history['opened'],'cold_no_history')
        require(observed['artifact']==read('cold/initial_completed.json')['artifact'],'observed_actual_work')
        results[label]=dict(strategy=report,allocation=allocation,actual_output=output,
            result_artifact=done['artifact'],current_use=hold['current_use'],hold=hold['hold'],
            root_decisions=hold['current_reviews']['reviews'],source_binding=strategy['context']['native_binding'],units=9)
    comparison=read('comparisons.json')
    require(results['cold']['hold']['offer_id']!=results['contrast']['hold']['offer_id'],'cp_strategy')
    counts=lambda name:{r['id']:r['allocation'] for r in results[name]['allocation']['rows']}
    require(counts('cold')!=counts('warm') and comparison['cp_budget']['actual_raw_prior']==prior['prior_fp'],'cp_budget')
    return dict(profile=PROFILE,instances=results,history=dict(head=head,snapshot=snapshot,feedback=observed['feedback']),
        comparisons=comparison,checks=['ORIGINAL_PROJECTIONS','ADMITTED_SAVED_RESULTS','ALLOCATION_CAUSAL_INPUT',
            'RECORDED_CURRENT_VALIDITY','SEPARATE_ROOTS','HISTORY_REDUCTION_AND_OPENED_PRIOR','ORIGINAL_NINE_UNITS'],
        native_replay='UNSUPPORTED_NATIVE_SCHEMA',scope='SAFE_DERIVED_SAVED_RELATIONSHIPS_AT_RECORDED_EVENT_TIMES',
        permission_restored=False,new_runtime_authority=False)


def export_package_v01(*,saved_inputs,source_root,source_ledger,output):
    """Explicit saved files only. Does not collect or execute the story."""
    saved=Path(saved_inputs);dst=Path(output);require(not dst.exists(),'output_exists')
    ledger=read_json_v01(source_ledger);require(type(ledger) is dict and bool(ledger),'source_ledger')
    validate_saved_story_v01(saved)
    bodies={}
    for p in sorted(saved.rglob('*')):
        require(not p.is_symlink(),'input_symlink')
        if p.is_file() and p.suffix in ('.json','.jsonl'):
            require(p.stat().st_size<=LIMIT,'saved_file_bound');bodies['story/'+_path(p.relative_to(saved).as_posix())]=p.read_bytes()
    for name,row in ledger.items():
        p=Path(source_root)/_path(name);require(p.is_file() and not p.is_symlink(),'source_missing')
        require(_body(p)=={k:row[k] for k in ('bytes','sha256')},'source_identity')
        bodies['sources/'+name]=p.read_bytes()
    closure=checker_sources_v44()
    checker={row['path']:{k:row[k] for k in ('bytes','sha256')} for row in closure.values()}
    for row in closure.values():bodies['checker_sources/'+row['path']]=Path(row['origin']).read_bytes()
    dst.mkdir(parents=True)
    for name,body in bodies.items():
        p=dst/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(body)
    manifest=dict(profile='G44_SAVED_PROOF_V01',producer_source_ledger=ledger,checker_source_ledger=checker,
        checker_environment=checker_environment_v44(),entries=[dict(path=k,bytes=len(v),sha256=hashlib.sha256(v).hexdigest()) for k,v in sorted(bodies.items())])
    _write(dst/'MANIFEST.json',manifest)
    publication=dict(profile='G44_PUBLICATION_V01',manifest_sha256=_body(dst/'MANIFEST.json')['sha256'],
        status='EVIDENCE_ONLY_PENDING_INDEPENDENT_REVIEW',source_admission='NOT_PERFORMED')
    _write(dst/'PUBLICATION.json',publication)
    return dict(publication_sha256=_body(dst/'PUBLICATION.json')['sha256'],status=publication['status'],files=len(bodies))


def verify_package_v01(*,package,trust):
    root=Path(package);require(type(trust) is dict and set(trust)=={'profile','status','publication_sha256'},'independent_pin_required')
    require(trust['profile']=='G43_EXTERNAL_PIN_V01' and trust['status'] in ('TEST_SUPPLIED_PIN','INDEPENDENTLY_REVIEWED_PIN'),'external_pin_profile')
    require(_body(root/'PUBLICATION.json')['sha256']==trust['publication_sha256'],'wrong_independent_pin')
    publication=read_json_v01(root/'PUBLICATION.json');manifest=read_json_v01(root/'MANIFEST.json')
    require(set(publication)=={'profile','manifest_sha256','status','source_admission'} and publication['profile']=='G44_PUBLICATION_V01'
        and publication['manifest_sha256']==_body(root/'MANIFEST.json')['sha256'],'publication_binding')
    require(set(manifest)=={'profile','producer_source_ledger','checker_source_ledger','checker_environment','entries'} and manifest['profile']=='G44_SAVED_PROOF_V01','manifest_shape')
    names=[_path(r['path']) for r in manifest['entries']];require(len(names)==len(set(names)),'unique_members')
    actual=[]
    for p in root.rglob('*'):
        require(not p.is_symlink(),'package_symlink')
        if p.is_file():actual.append(p.relative_to(root).as_posix())
    require(set(actual)==set(names)|{'MANIFEST.json','PUBLICATION.json'},'complete_package_coverage')
    for row in manifest['entries']:
        require(set(row)=={'path','bytes','sha256'} and _body(root/row['path'])=={k:row[k] for k in ('bytes','sha256')},'member_identity')
    ledger=manifest['producer_source_ledger']
    required={'hedgehog/gate4_reference_evidence_v01.py','hedgehog/gate4_reference_runtime_v01.py',
        'hedgehog/domains/airline/gate4_reference_adapter_v01.py','hedgehog/domains/airline/gate4_reference_history_v01.py',
        'hedgehog/gate4_pressure_budget_v01.py','hedgehog/gate4_strategy_reference_v01.py','hedgehog/gate4_reference_contracts_v01.py'}
    require(required<=set(ledger),'required_source_inventory')
    for name,row in ledger.items():
        require('sources/'+_path(name) in names and _body(root/'sources'/name)=={k:row[k] for k in ('bytes','sha256')},'required_source_bytes')
    # Do not import uploaded source. The installed finite checker must match its pin.
    closure=checker_sources_v44();checker=manifest['checker_source_ledger']
    require(set(checker)=={row['path'] for row in closure.values()},'checker_dependency_inventory')
    for row in closure.values():
        name=row['path'];expected=checker[name]
        require(set(expected)=={'bytes','sha256'} and 'checker_sources/'+name in names
            and _body(root/'checker_sources'/name)==expected
            and _body(Path(row['origin']))==expected,'checker_source_binding:'+name)
    require(checker_environment_v44()==manifest['checker_environment'],'checker_environment_binding')
    result=validate_saved_story_v01(root/'story')
    return dict(profile='G44_VERIFIED_SUPPORTED_REPLAY_V01',publication=publication,expected_pin=trust,
        status='TEST_PIN_SUPPORTED_PASS' if trust['status']=='TEST_SUPPLIED_PIN' else 'INDEPENDENT_PIN_SUPPORTED_PASS',
        source_admission='NOT_PERFORMED',result=result)
