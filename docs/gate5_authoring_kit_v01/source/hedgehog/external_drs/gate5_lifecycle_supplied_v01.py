"""Narrow G52 historical proof: structural native records and exact causal claims.

No Root decisions, Work execution, Host dispatch, remote access or DRS writes.
Expected package/source pins are supplied separately by the reviewing operator.
"""
import hashlib
import json
from pathlib import Path
from hedgehog.kernel import root_decision_v01 as roots, semantic_work_v01 as sw, transition_registry_v01 as transitions
from . import gate5_contracts_v01 as c, gate5_native_v01 as n, gate5_supplied_v01 as old


def thaw(value):
    if type(value) is dict:
        if set(value)=={'items'}:
            c.require(type(value['items']) is list and len(dict(value['items']))==len(value['items']),'frozen_object_shape')
            return {k:thaw(v) for k,v in value['items']}
        return {k:thaw(v) for k,v in value.items()}
    if type(value) is list:return [thaw(v) for v in value]
    return value


def root_record(proof,root,selected,claim_value=None,subject=None,accepted=True):
    """Public input/result structure validation, without recomputing Root decisions."""
    raw=proof['inputs'];packet=raw['root_review_packet'];synthesis=packet['synthesis_proposal']
    c.require(not synthesis['conflict_sets'],'unsupported_recorded_conflict_shape')
    claims=[]
    for value in synthesis['normalized_claims']:
        args={k:v for k,v in value.items() if k!='authority_class'}
        args.update(object_or_value=thaw(value['object_or_value']),provenance_refs=tuple(value['provenance_refs']),evidence_refs=tuple(value['evidence_refs']))
        claim=sw.build_normalized_claim_v01(**args);c.require(n.plain(claim)==value,'recorded_claim_shape');claims.append(claim)
    rebuilt_synthesis=old.record(sw.SynthesisProposalV01,synthesis,normalized_claims=tuple(claims),conflict_sets=(),
        **old.tuple_fields(synthesis,('source_contribution_ids','missing_evidence_refs','contribution_modes','requested_validators')))
    rebuilt_packet=old.record(sw.RootReviewPacketV01,packet,synthesis_proposal=rebuilt_synthesis,
        **old.tuple_fields(packet,('contribution_ids','conflict_set_ids','missing_evidence_refs','required_validator_ids')))
    args={k:thaw(v) for k,v in raw.items() if k not in ('decision_input_id','root_review_packet')}
    inputs=roots.build_root_decision_input_v01(root_review_packet=rebuilt_packet,**args)
    kernel=roots.build_root_decision_kernel_v01()
    c.require(n.plain(inputs)==raw and n.plain(kernel)==proof['kernel'],'recorded_root_input_identity')
    c.require(not roots.validate_root_decision_input_v01(kernel=kernel,decision_input=inputs),'recorded_root_input_structure')
    result=proof['result'];td=result['transition_decision']
    transition=old.record(transitions.TransitionDecisionV01,td,**old.tuple_fields(td,('required_guards','satisfied_guards','missing_guards')))
    rebuilt=old.record(roots.RootDecisionResultV01,result,transition_decision=transition,
        **old.tuple_fields(result,('hard_failure_reasons','missing_evidence_refs','conflict_set_ids')))
    c.require(roots.root_decision_result_to_plain_dict_v01(rebuilt)==result,'recorded_root_result_structure')
    old.root_links(proof,root,selected,accepted)
    c.require(raw['target_root_id']==root and len(claims)==1,'recorded_root_target')
    claim=claims[0]
    if accepted:
        c.require(claim.claim_id==selected and thaw(raw['gt_advisory'])['selected_candidate_id']==selected,'recorded_root_work_selection')
    if subject is not None:c.require(claim.subject==subject,'recorded_root_subject')
    actual=thaw(n.plain(claim)['object_or_value'])
    if claim_value is not None:c.require(actual==claim_value,'recorded_root_claim_binding')
    return actual


def accepted_record(value,policy):
    record=value['import_record'];candidate=record['candidate'];body=record['bundle']['body'];pointer=record['descriptor']['value']
    c.require(record['policy']==policy,'supplied_local_policy')
    checked=c.check_bundle(record['bundle'],record['descriptor'],record['request'],record['status'],policy,value['use_time'],{}, {})
    c.validate('import',candidate)
    scenario=record['scenario'];dependency=c.sha(dict(readings=scenario['readings'],limit=scenario['limit'],policy=c.sha(policy),source=c.sha(body)))
    expected=dict(local_request_ref=record['request']['request_id'],pointer_ref=pointer['pointer_id'],foreign_publisher=pointer['publisher_root_id'],
        foreign_source_ref=body['source_record_ref'],foreign_revision=body['source_revision'],received_manifest_hash=c.sha(record['bundle']['manifest']),
        body_hash=c.sha(body),dependency_fingerprint=dependency,policy_hash=c.sha(policy),status_entry_hash=checked['status_entry']['entry_hash'])
    c.require(all(candidate[k]==v for k,v in expected.items()),'supplied_import_relationship')
    root_record(record['review'],c.ROOT_B,candidate['import_id'],candidate,body['source_record_ref'])
    adaptation=value['adaptation'];c.validate('adaptation',adaptation)
    c.require(adaptation['value']==body['correction'] and adaptation['import_ref']==candidate['import_id'] and
        adaptation['foreign_source_ref']==body['source_record_ref'] and adaptation['local_acceptance_ref']==record['review']['result']['decision_id'],'supplied_adaptation')
    inputs=dict(readings=c.canonical(scenario['readings']).decode(),offset_num=body['correction']['num'],offset_den=body['correction']['den'])
    outputs=old.native_result(value['work'],c.ROOT_B,inputs)
    math=c.corrected(scenario['readings'],body['correction'])
    c.require(outputs==dict(corrected_num=math['corrected']['num'],corrected_den=math['corrected']['den'],mean_num=math['mean']['num'],mean_den=math['mean']['den']),'supplied_native_math')
    assessment='WITHIN_REFERENCE_LIMIT' if outputs['corrected_num']<=c.mul(scenario['limit'],outputs['corrected_den']) else 'REVIEW_REQUIRED'
    claim=dict(assessment=assessment,work_result_ref=value['work']['artifact']['artifact_id'],adaptation_ref=adaptation['local_view_id'],outputs=outputs,
        limit=scenario['limit'],source_revision=body['source_revision'],source_ref=body['source_record_ref'],body_hash=c.sha(body),
        dependency_fingerprint=dependency,policy_hash=c.sha(policy),local_request_ref=record['request']['request_id'])
    c.require(value['claim']==claim,'supplied_assessment_relationship')
    root_record(value['final_review'],c.ROOT_B,value['work']['artifact']['artifact_id'],claim,candidate['import_id'])
    return claim


def verify(folder,expected,source_root):
    folder,source_root=Path(folder),Path(source_root)
    for name,pin in expected['capture_files'].items():
        path=folder/name;c.require(path.is_file() and not path.is_symlink(),'missing_evidence:'+name)
        data=path.read_bytes();c.require(len(data)==pin['bytes'] and hashlib.sha256(data).hexdigest()==pin['sha256'],'external_capture_pin:'+name)
    for name,sha in expected['source_pins'].items():c.require(hashlib.sha256((source_root/name).read_bytes()).hexdigest()==sha,'external_source_pin:'+name)
    read=lambda name:json.loads((folder/name).read_text())
    trust=read('operator_trust.json');c.require(c.sha(trust)==expected['operator_trust_sha256'],'operator_trust_pin')
    policy=trust['B'];one=read('B/r1/accepted.json');two=read('B/r2/accepted.json')
    claims=[accepted_record(value,policy) for value in (one,two)]
    c.require(one['import_record']['scenario']==two['import_record']['scenario'],'experience_not_policy_change')
    for revision,value in [(1,one),(2,two)]:
        candidate=value['import_record']['candidate']
        root_record(read('B/r%d/current_review.json'%revision),c.ROOT_B,candidate['import_id'],
            dict(dependency=candidate['dependency_fingerprint'],policy=candidate['policy_hash'],import_ref=candidate['import_id']),
            value['claim']['source_ref'])
        body=value['import_record']['bundle']['body'];proof=read('A/r%d/source_work.json'%revision)
        output=old.native_result(proof,c.ROOT_A,dict(readings=c.canonical(body['observations']).decode(),reference=body['reference']))
        c.require(output==dict(n=body['n'],total=body['total'],correction_num=body['correction']['num'],correction_den=body['correction']['den']) and body['source_revision']==revision,'native_source_binding')
        source_claim={k:body[k] for k in ('source_record_ref','source_revision','unit_id','quantity_id','reference','observations','n','total','correction','source_work_ref')}
        review=read('A/r%d/source_review.json'%revision)
        root_record(review,c.ROOT_A,proof['artifact']['artifact_id'],source_claim,body['source_record_ref'])
        c.require(review['result']['decision_id']==body['source_review_ref'] and proof['artifact']['artifact_id']==body['source_work_ref'],'source_review_binding')
        publish=read('A/r%d/publish_review.json'%revision)
        root_record(publish,c.ROOT_A,value['import_record']['descriptor']['value']['pointer_id'],value['import_record']['descriptor']['value'],body['source_record_ref'])
    c.require(one['import_record']['bundle']['body']['source_work_ref'] in two['import_record']['bundle']['body']['source_lineage_refs'],'revision_lineage')
    checkpoint=read('restart_checkpoint.json');processes=read('processes.json')
    c.require(len(processes)==3 and all(p['rc']==0 and p['reaped'] for p in processes),'process_completion')
    c.require(processes[1]['pid']!=processes[2]['pid'] and checkpoint['b1_pid']==processes[1]['pid'] and checkpoint['b1_reaped'] and checkpoint['a_still_running'],'actual_restart')
    c.require(checkpoint['accepted_sha256']==hashlib.sha256((folder/'B/r1/accepted.json').read_bytes()).hexdigest(),'historical_bytes_changed')
    c.require(trust['B_sessions'][0]!=trust['B_sessions'][1] and trust['A_keys']==policy['peer_keys'],'explicit_key_repin')
    for label,expected_values in [('before_restart',[one]),('after_restart',[one]),('final',[one,two])]:
        history=read('B/history_'+label+'.json')
        c.require({c.sha(v) for v in history['results']}=={c.sha(v) for v in expected_values},'historical_query_relationship')
        c.require(history['wire_before']==history['wire_after'] and history['mode']=='HISTORICAL_NOT_CURRENT_PERMISSION','history_zero_fetch')
        root_record(history['review'],c.ROOT_B,history['review']['result']['selected_candidate_id'],dict(mode=history['mode'],
            record_ids=[x['record_id'] for x in history['resolver']['candidates']],result_hashes=[c.sha(v) for v in history['results']]),'history:g52')
    for session in (1,2):
        observer=read('B/observation_%d.json'%session)
        for interval in observer['intervals']:
            if interval['function']=='history_query':
                c.require(interval['deltas']['native_work']==0 and interval['deltas']['peer_send']==0 and interval['deltas']['root_decision']==1,'history_observed_calls')
    terminal=read('B/terminal_observation.json');p1=one['import_record']['descriptor']['value']
    key,entry=c.authenticate_status(terminal['status'],p1,terminal['request'],policy,terminal['status']['value']['checked_at'],{})
    c.require(entry['state']=='REVOKED' and checkpoint['persisted_state']['highwater'][key]==entry,'terminal_persisted_before_exit')
    state=read('B/import_state.json');c.require(state['highwater'][key]==entry,'restart_terminal_preserved')
    p2=two['import_record']['descriptor']['value'];key2,entry2=c.authenticate_status(two['import_record']['status'],p2,two['import_record']['request'],policy,two['use_time'],{})
    c.require(key!=key2 and state['highwater'][key2]==entry2 and entry2['state']=='ACTIVE' and entry2['revision']==1,'pointer_stream_independence')
    c.require(read('B/restart_old_active.json')['reason']=='status_rollback' and read('B/status_unavailable.json')['reason']=='CURRENT_STATUS_UNKNOWN','current_refusals')
    for name in ('changed_policy','changed_dependency'):
        changed=root_record(read('B/'+name+'/current_review.json'),c.ROOT_B,None,accepted=False)
        c.require(changed['import_ref']==two['import_record']['candidate']['import_id'] and
            changed['dependency']!=two['claim']['dependency_fingerprint'],'changed_context_refusal_binding')
    local_denial=read('B/local_policy_refusal.json');local_wire=read('B/local_denial_counters.json')
    root_record(local_denial['review'],c.ROOT_B,None,dict(policy=local_denial['policy'],pointer_ref=p1['pointer_id']),p1['pointer_id'],False)
    c.require(local_denial['policy']['accept_calibration'] is False and local_wire['before']==local_wire['after'],'local_denial_zero_fetch')
    dedup=read('B/dedup.json');c.require(len(dedup['state']['sources'])==1 and len(dedup['state']['duplicates'])==1 and dedup['history_records']==1 and dedup['state']['credit']==0,'dedup_before_restart')
    c.require(len(state['sources'])==2 and len(state['duplicates'])==1 and state['credit']==0,'dedup_after_restart')
    counts=[]
    for session in (1,2):
        a=read('A/session%d/wire_counters.json'%session);b=read('B/session%d/wire_counters.json'%session)
        c.require(a['sent']==b['received'] and a['received']==b['sent'] and a['sent_bytes']==b['received_bytes'] and a['received_bytes']==b['sent_bytes'],'wire_counters')
        for i in range(1,b['sent']+1):
            sent=(folder/('B/session%d/wire_sent_%02d.json'%(session,i))).read_bytes();received=(folder/('A/session%d/wire_received_%02d.json'%(session,i))).read_bytes()
            c.require(sent==received,'request_wire_bytes');message=c.decode(sent)
            c.verify(message['value'],trust['B_sessions'][session-1],'REQUEST',c.sha(policy))
        events=read('B/session%d/events.json'%session)
        c.require(len(events)==a['sent']==b['sent'],'finite_request_response_count')
        pointers={v['import_record']['descriptor']['value']['pointer_id']:v['import_record']['descriptor']['value'] for v in (one,two)}
        for i,event in enumerate(events,1):
            sent=(folder/('A/session%d/wire_sent_%02d.json'%(session,i))).read_bytes()
            c.require(sent==(folder/('B/session%d/wire_received_%02d.json'%(session,i))).read_bytes(),'response_wire_bytes')
            response=c.decode(sent);req=event['request']
            c.require(event['response']==response and req==c.decode((folder/('B/session%d/wire_sent_%02d.json'%(session,i))).read_bytes())['value']['value'],'event_wire_binding')
            request_review=read('B/requests/'+req['request_id']+'.json')
            root_record(request_review['review'],c.ROOT_B,req['request_id'],req,req['object_id'])
            kind=response['kind']
            if kind=='POINTER':c.check_pointer(response['value'],policy,req['issued_at'])
            elif kind=='CLOSED':
                value=c.verify(response['value'],policy['peer_keys'],'CLOSE',c.sha(policy))
                c.require(value==dict(request_ref=req['request_id'],session=session),'close_binding')
            else:
                pointer=pointers[req['pointer_ref']];manifest_hash=pointer['artifact_manifest_ref'].split(':')[1]
                if kind=='STATUS':
                    # STATUS authenticates the requested FETCH subject, not the wrapper ID.
                    subject=dict(request_id=req['subject_request_ref'],requester=req['requester'],
                        request_revision=req['request_revision'],nonce=req['nonce'])
                    c.authenticate_status(response['value'],pointer,subject,policy,response['value']['value']['checked_at'],{})
                elif kind=='UNAVAILABLE':
                    value=c.verify(response['value'],policy['peer_keys'],'STATUS_UNAVAILABLE',manifest_hash)
                    c.require(value==dict(request_ref=req['request_id'],nonce=req['nonce'],reason='CURRENT_STATUS_UNKNOWN'),'unavailable_binding')
                elif kind=='BUNDLE':
                    bundle=response['value'];release=c.verify(bundle['release'],policy['peer_keys'],'RELEASE',manifest_hash)
                    c.require(release['request_ref']==req['request_id'] and release['nonce']==req['nonce'] and release['pointer_ref']==pointer['pointer_id'],'release_wire_binding')
                    source=read('A/releases/'+req['request_id']+'.json');allowed=release['state']=='RELEASED'
                    c.require(source['request']==req and source['response']==bundle and source['review']['result']['decision_id']==release['release_review_ref'],'source_release_binding')
                    root_record(source['review'],c.ROOT_A,req['request_id'] if allowed else None,
                        dict(request=req,pointer_ref=pointer['pointer_id'],body_hash=pointer['body_sha256']),pointer['pointer_id'],allowed)
                    c.require(allowed or (bundle['body'] is None and bundle['manifest'] is None),'refusal_disclosure')
                else:raise ValueError('unsupported_response')
        counts.append(b)
    source_budget=read('A/publisher_budget.json');baseline=source_budget['tasks']['task:gate5:exchange']
    c.require(baseline['payload']==2 and baseline['bodies']==2 and baseline['denied']==2 and baseline['metadata']==8,'publisher_budget_final')
    c.require(baseline['refused_responses']==2 and baseline['released_responses']==2 and
        source_budget['tasks']['task:gate5:scope-refusal']['refused_responses']==1 and
        source_budget['tasks']['task:gate5:scope-refusal']['body_bytes']==0,'publisher_refusal_accounting')
    c.require(source_budget['contexts']==read('B/task_contexts.json')==read('A/bootstrap_1.json')['contexts']==read('A/bootstrap_2.json')['contexts'],'persisted_operator_contexts')
    for i in (1,2):
        attack=read('B/publisher_budget_control_%d.json'%i);bundle=attack['response']['value'];req=attack['request']
        release=c.verify(bundle['release'],policy['peer_keys'],'RELEASE',p1['artifact_manifest_ref'].split(':')[1])
        c.require(release['state']=='REFUSED' and release['request_ref']==req['request_id'] and bundle['body'] is None and bundle['manifest'] is None,'publisher_no_overbudget_body')
        source=read('A/releases/'+req['request_id']+'.json')
        c.require(source['reserved'] is False and source['budget_after']['tasks'][req['task_ref']]['bodies']==2,'publisher_pre_disclosure_reservation')
        root_record(source['review'],c.ROOT_A,None,accepted=False)
    c.require(read('canary_scan.json')['matches']==0,'recorded_canary_scan')
    return dict(status='PASS_NARROW_G52_SUPPLIED',claims=claims,wire=counts,source_budget=source_budget['tasks'],
        history_immutable=True,restarted=True,terminal_preserved=True,deduplicated_sources=2,credit=0,
        scope='PUBLIC_CRYPTO_PURE_WORK_AND_ROOT_INPUT_RESULT_STRUCTURES_WITH_EXACT_RECORDED_CLAIMS; NOT_FULL_NATIVE_REPLAY_OR_CURRENT_AUTHORITY',
        canary='RECORDED_PUBLIC_SCAN_NOT_FRESH_PRIVATE_SCAN',new_root_decisions=0,new_work=0,host_dispatch=0,fetch=0,drs_writes=0,effects=0)
