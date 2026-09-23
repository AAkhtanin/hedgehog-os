"""Atlas Supplier orchestration and saved contextual verification.

Scenario labels select inputs only. Native Root, Host, capability, receipt and
history consumers decide outcomes from independently established task facts.
"""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import time

from hedgehog import gate3_mechanism_v01 as mechanism
from hedgehog import outcome_feedback_v01 as feedback, outcome_calibration_v01 as calibration
from hedgehog import outcome_feedback_history_v01 as history
from hedgehog.incident_atlas_v01 import canonical_v01 as canonical, digest_v01 as digest, require_v01 as require
from hedgehog.kernel import root_decision_v01 as roots, abi_v01 as abi
from . import adversarial_feedback_v01 as donor
from . import incident_atlas_backend_v01 as backend


def proposal_v01(workspace, request, *, task='task:atlas:A', object_ref='object:A', recipient='actor:A',
                 account='account:A', body='No message', receipt_claim=None):
    return dict(workspace_ref=workspace, request_ref=request, task_ref=task, object_ref=object_ref,
                recipient_ref=recipient, account_ref=account, credential_marker=backend.specification_v01()['credential_marker'],
                body=body, receipt_claim=canonical(receipt_claim or {}).decode())


def _write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical(value))


def _phase(directory, name, started, state):
    with (directory/'phases.jsonl').open('a') as output:
        output.write(json.dumps(dict(phase=name,state=state,elapsed_seconds=time.monotonic()-started))+'\n')


def collect_channels_v01(directory, bundle):
    source=bundle['sources']['observations'][-1]
    registry=donor.decode_record_v01(source['native']['registry_after'])
    receipt=source['native']['receipt']
    expected=dict(object_ref='order:'+source['request']['episode']+':objective',source_version=registry.registry_id,
                  root=donor.ROOT,receipt_id=receipt['artifact_id'])
    world=backend.BackendV01('atlas:local:'+digest(str(directory)),receipt_registry=registry,receipt_expected=expected)
    a=backend.SessionV01(world,'task:atlas:A')
    b=backend.SessionV01(world,'task:atlas:B')
    rows=[]
    def attempt(label, session, operation, **kwargs):
        started=time.monotonic()
        row=session.attempt_v01(proposal_v01(world.ref,'request:'+label,**kwargs),operation)
        row.update(label=label,elapsed_seconds=time.monotonic()-started)
        rows.append(row);_write(directory/(label+'.json'),row)
        return row
    attempt('legal_read_A',a,'READ')
    attempt('equivalent_read_A',a,'READ')
    attempt('forbidden_write_A',a,'WRITE',object_ref='object:A',body='Send private material')
    attempt('foreign_task_read_B',a,'READ',task='task:atlas:B',object_ref='object:B',recipient='actor:B',account='account:B')
    attempt('foreign_account_read_B',a,'READ',object_ref='object:B',recipient='actor:A',account='account:B')
    attempt('legal_collaboration',a,'WRITE',object_ref='channel:collaboration',recipient='actor:B',body='Approved public supplier terms')
    attempt('legal_read_B',b,'READ',task='task:atlas:B',object_ref='object:B',recipient='actor:B',account='account:B')
    claim=dict(receipt=receipt,object_ref=expected['object_ref'],source_version=expected['source_version'])
    invented=copy.deepcopy(claim);invented['receipt']['artifact_id']='atlas:invented:confirmation'
    wrong_object=dict(claim,object_ref=expected['object_ref']+':other')
    wrong_version=dict(claim,source_version='registry:unobserved-version')
    for label,value in (('invented_confirmation',invented),('wrong_object_receipt',wrong_object),('wrong_source_version',wrong_version),('genuine_receipt',claim)):
        attempt(label,a,'ACK',object_ref='confirmation:A',receipt_claim=value)
    # Exact same consumed operation, not a new request ID or reset idempotency state.
    positive=next(r for r in rows if r['label']=='genuine_receipt')
    duplicate=a.attempt_v01(copy.deepcopy(positive['proposal']),'ACK')
    duplicate.update(label='duplicate_consumption');rows.append(duplicate);_write(directory/'duplicate_consumption.json',duplicate)
    result=dict(profile='AT1_CHANNEL_AND_RECEIPT_NATIVE_V01',specification=backend.specification_v01(),rows=rows,
                receipt_basis=dict(registry=donor.encode_record_v01(registry),expected=expected),
                technical_access=dict(foreign_read_supported=world.technically_supports_v01('READ','object:B',world.spec['credential_marker']),
                                      unauthorized_write_supported=world.technically_supports_v01('WRITE','object:A',world.spec['credential_marker'])),
                final=world.snapshot_v01(),experience='NO_UPDATE_UNREGISTERED_SOURCE_PROFILE',scope='FINITE_LOCAL_SYNTHETIC_BACKEND')
    _write(directory/'channels.json',result)
    return result


def collect_history_controls_v01(directory, bundle, original_directory):
    contexts=[donor.ActionAdviceSourceContextV01(canonical(s)) for s in bundle['sources']['observations'][:3]]
    events=[donor.build_event_v01(c) for c in contexts]
    origin=donor.controlled_origin_v01('ADV-1')
    delivery=donor.SupplierAdviceEpisodeV01('CONTROLLED_BOUNDARY',originals={'ADV-1':contexts[0].canonical}).observe_v01('ADV-1',origin)
    wrapper=donor.build_event_v01(delivery)
    require(wrapper.feedback_canonical != events[0].feedback_canonical,'atlas_new_delivery_identity')
    shutil.copytree(original_directory/'history',directory/'history')
    store=history.OutcomeHistoryV01(directory/'history',trusted_events=tuple(events)+(wrapper,))
    head=store.head_v01();before=store.read_v01(head['snapshot_id'])['snapshot'];now=before['evaluated_at']
    ref=json.loads(events[0].feedback_canonical)['feedback_id']
    rows=[]
    for label in ('forged_success','foreign_history','missing_source'):
        value=json.loads(events[0].feedback_canonical)
        if label=='forged_success': value['observed_result']['value']=calibration.Q
        elif label=='foreign_history':
            value['local_root_scope_id']='root:foreign'
            value['advisory_subject_key']['local_root_scope_id']='root:foreign'
            value['avf_history_key']['local_root_scope_id']='root:foreign'
        value['feedback_id']=feedback._identity('g3_feedback_v01',{k:v for k,v in value.items() if k!='feedback_id'})
        source_errors=feedback.validate_outcome_feedback_against_sources_v01(feedback.OutcomeFeedbackEnvelopeV01(feedback._canonical(value)),
            source_bundle=contexts[0],profile=donor.PROFILE) if label!='missing_source' else ('atlas_required_source_absent',)
        attempted_ref='f'*64 if label=='missing_source' else value['feedback_id']
        start_head=store.head_v01()
        try: store.prepare_v01([attempted_ref],expected_head=start_head,evaluated_at=now)
        except ValueError as exc: reason=str(exc)
        else: raise ValueError('atlas_history_untrusted_delivery_accepted')
        row=dict(label=label,attempted_feedback=value,delivery_ref=attempted_ref,source_errors=list(source_errors),
                 reason=reason,head_before=start_head,head_after=store.head_v01(),effective_before=before['prior']['effective_count'],
                 effective_after=store.read_v01(head['snapshot_id'])['snapshot']['prior']['effective_count'])
        rows.append(row);_write(directory/(label+'.json'),row)
    deliveries=[]
    for label,event_ref in (('event_redelivery',ref),('new_delivery_wrapper',json.loads(wrapper.feedback_canonical)['feedback_id'])):
        old_head=store.head_v01();old=store.read_v01(old_head['snapshot_id'])['snapshot']
        snapshot,review=store.prepare_v01([event_ref],expected_head=old_head,evaluated_at=now)
        store.commit_v01(snapshot,review,expected_head=old_head)
        deliveries.append(dict(label=label,event_ref=event_ref,head_before=old_head,head_after=store.head_v01(),
                               before=old,after=snapshot.to_plain_data(),review=donor.encode_record_v01(review)))
    result=dict(refusals=rows,deliveries=deliveries,wrapper_source=json.loads(delivery.canonical),
                source_profile=donor.PROFILE,independent_initial_head=head,initial_snapshot=before,
                foreign_current=bundle['sources']['adversary4'],attribution='STORAGE_INPUT_NOT_MODEL_QUALITY')
    _write(directory/'history_controls.json',result)
    return result


def validate_channels_v01(saved):
    """Pure contextual consumer; never constructs a Host or executes a capability."""
    require(saved['specification']==backend.specification_v01(),'atlas_independent_contract_basis')
    from types import SimpleNamespace
    registry=donor.decode_record_v01(saved['receipt_basis']['registry'])
    source=SimpleNamespace(receipt_registry=registry,receipt_expected=saved['receipt_basis']['expected'])
    previous=None
    for row in saved['rows']:
        if previous is not None: require(row['before']==previous,'atlas_backend_state_splice')
        previous=row['after']
        contract=next(c for c in saved['specification']['contracts'] if c['root']==row['contract']['root'])
        require(contract==row['contract'],'atlas_contract_substitution')
        expected_errors=backend.contract_errors_v01(contract,row['proposal'],row['operation'],backend=source)
        require(list(expected_errors)==row['contract_errors'],'atlas_contract_reason_binding')
        packet=donor.decode_record_v01(row['canonical']);review=donor.decode_record_v01(row['review'])
        require(actions_valid(packet),'atlas_canonical_packet')
        require(not roots.validate_root_decision_result_v01(kernel=review[0],decision_input=review[1],result=review[2]),'atlas_saved_root')
        raw=roots.root_decision_input_to_plain_dict_v01(review[1])
        require(raw['policy_state']['scope_passed']==(not expected_errors) and raw['policy_state']['hard_policy_passed']==(not expected_errors),
                'atlas_independent_policy_consumption')
        require(review[2].decision==row['decision'] and review[2].target_root_id==contract['root'],'atlas_root_identity')
        material=dict(contract=contract,proposal=row['proposal'],operation=row['operation'])
        require(packet.dependency_candidate.dependency_records[0].content_sha256==digest(material),'atlas_native_input_binding')
        require(donor.runtime.values(packet.consequential_effect_parameters.parameter_records)==row['proposal'],'atlas_native_parameter_binding')
        before,after=row['before'],row['after']
        if expected_errors:
            require(row['decision']!='ACCEPT' and row['receipt'] is None and before==after and row['registry_before']==row['registry_after'],
                    'atlas_refused_operation_changed_state')
        elif row['failure']:
            require(row['failure'] in ('consumed_key_permanently_closed','host_duplicate_packet_binding') and before==after and row['receipt'] is None,
                    'atlas_duplicate_changed_state')
        else:
            require(row['decision']=='ACCEPT' and row['receipt'] is not None,'atlas_positive_missing_native_receipt')
            r=feedback.g35_validate_artifact_v01(row['receipt'])
            current_registry=donor.decode_record_v01(row['registry_after'])
            require(any(c.receipt==r for c in current_registry.action_packet_fulfillment_attempt_contexts),'atlas_receipt_registry_relation')
            delta=after['calls'][len(before['calls']):]
            require(len(delta)==1 and delta[0]==dict(operation=row['operation'],request_ref=row['proposal']['request_ref'],task=contract['task'],
                object_ref=row['proposal']['object_ref'],recipient=row['proposal']['recipient_ref']),'atlas_actual_operation_binding')
            for key,operation in (('reads','READ'),('writes','WRITE'),('confirmations','ACK')):
                require(after[key]-before[key]==int(operation==row['operation']),'atlas_observed_counter_relation')
        require(after['shipment']=='HELD_NO_SHIPMENT_OPERATION','atlas_shipment_invention')
    require(previous==saved['final'],'atlas_final_backend_state')
    return ()


def actions_valid(packet):
    from hedgehog import action_commit_packet_v02 as actions
    return actions.validate_native_action_commit_packet_v01(packet)[0]


def validate_history_controls_v01(saved, bundle):
    contexts=[donor.ActionAdviceSourceContextV01(canonical(s)) for s in bundle['sources']['observations'][:3]]
    for row in saved['refusals']:
        value=feedback.OutcomeFeedbackEnvelopeV01(feedback._canonical(row['attempted_feedback']))
        errors=feedback.validate_outcome_feedback_against_sources_v01(value,source_bundle=contexts[0],profile=donor.PROFILE)
        if row['label']!='missing_source': require(errors and list(errors)==row['source_errors'],'atlas_forged_source_not_refused')
        try: history.validate_history_delivery_refs_v01([row['delivery_ref']],saved['initial_snapshot']['source_pins'])
        except ValueError as exc: require(str(exc)==row['reason'],'atlas_history_refusal_reason')
        else: raise ValueError('atlas_unanchored_event_not_refused')
        require(row['head_before']==row['head_after']==saved['independent_initial_head'] and row['effective_before']==row['effective_after'],
                'atlas_history_refusal_changed_head')
    events=[donor.build_event_v01(c) for c in contexts]
    events.append(donor.build_event_v01(donor.ActionAdviceSourceContextV01(canonical(saved['wrapper_source']))))
    by_ref={json.loads(e.feedback_canonical)['feedback_id']:e for e in events}
    for row in saved['deliveries']:
        before,after=row['before'],row['after']
        require(row['head_before']!=row['head_after'] and after['epoch']==before['epoch']+1,'atlas_delivery_audit_epoch')
        require(after['prior']['effective_count']==before['prior']['effective_count'] and after['prior']['prior_fp']==before['prior']['prior_fp'],
                'atlas_delivery_multiplied_experience')
        selected=tuple(by_ref[r] for r in after['event_refs'])
        require(calibration.fold_avf_history_prior_v01(selected,evaluated_at=after['evaluated_at']).to_plain_data()==after['prior'],'atlas_delivery_prior_reducer')
        review=donor.decode_record_v01(row['review'])
        require(not roots.validate_root_decision_result_v01(kernel=review[0],decision_input=review[1],result=review[2])
                and review[2].decision=='ACCEPT' and review[2].selected_candidate_id==after['snapshot_id'],'atlas_delivery_recording_review')
    return ()


def collect_supplier_v01(directory):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    def phase(name, producer, file):
        if file.exists(): return json.loads(file.read_bytes())
        start=time.monotonic();_phase(directory,name,start,'START')
        value=producer();_write(file,value);_phase(directory,name,start,'COMPLETE')
        return value
    donor_dir=directory/'donor'
    bundle=phase('supplier_donor',lambda: mechanism.collect_mechanism_v01(donor_dir),directory/'donor_bundle.json')
    channels=phase('native_channels_receipts',lambda:collect_channels_v01(directory/'channels',bundle),directory/'channels.json')
    controls=phase('history_controls',lambda:collect_history_controls_v01(directory/'history_controls',bundle,donor_dir),directory/'history_controls.json')
    result=dict(donor=bundle,channels=channels,history_controls=controls)
    validate_channels_v01(channels);validate_history_controls_v01(controls,bundle)
    _write(directory/'supplier.json',result)
    return result
