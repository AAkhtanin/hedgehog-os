"""Finite precreated peers. Entry has exactly the frozen keyword arguments."""
import pathlib
import secrets
from hedgehog.external_drs.gate5_exchange_v01 import PipeChannel
from hedgehog.external_drs import gate5_contracts_v01 as c, gate5_exchange_v01 as x, gate5_native_v01 as n
from hedgehog.external_drs.gate5_lifecycle_v01 import ImportStore
from candidate_domain.domain import Refusal, need, report, request_times, planning_equal, consume
from candidate_domain.policy import validate_policy, validate_event, approve_shift, approve_booking, remembered_request, consumer_policy
from candidate_domain.profile import profile, context_from_checked
from candidate_domain.storage import local_name, read, save, state, history_path, object_path
from candidate_domain.native import perform, review
from candidate_domain.memory import descent
from candidate_domain.publication import build, history_projection
from candidate_domain.effect import reconcile

def task_ref(r):
    return 'task:football:'+c.sha(r)

def object_ref(r):
    # Transport context derives from original local inputs, never a caller path or selected offer.
    return 'object:football:'+c.sha({k:r.get(k) for k in ('request_id','revision','team_ref','venue_ref')})

def request(p,r,op,view=None,pointer=None,subject=None,nonce=None):
    now=x.clock()
    revision=r.get('revision')
    # A transport envelope for malformed user input still permits a CLARIFY exchange.
    # Its protocol revision is independent of, and never copied into, the user report.
    revision=revision if type(revision) is int and revision>0 else 1
    fingerprint=c.sha(view if view is not None else dict(root=p['local_root'],event=c.sha(r),mode='METADATA'))
    req=c.with_id('request',dict(version='g51.request.v01',op=op,requester=p['local_root'],publisher=p['peer_root'],
        task_ref=task_ref(r),request_revision=revision,pointer_ref=None if pointer is None else pointer['pointer_id'],
        trust_profile_hash=fingerprint,use_class='LOCAL_CONTEXT',object_id=object_ref(r),allowed_size=c.BODY_MAX,
        nonce=nonce or secrets.token_hex(32),deadline=now+60,issued_at=now,subject_request_ref=subject,
        owner_transport_scope='owner:football:inherited-pipes'))
    c.validate('request',req)
    return req

def boot(role,p,bootstrap,folder):
    cap=c.crypto.generate_root_signer_capability_v01(root_id=p['local_root'])
    keys=c.crypto.build_trusted_root_key_set_v01(capabilities=(cap,))
    public=c.crypto.trusted_root_key_set_to_plain_dict_v01(keys)
    bootstrap.send('POINTER',public)
    message=bootstrap.receive()
    need(message['kind']=='POINTER','bootstrap_public_keyset_kind')
    peer=message['value']; c.keyset(peer)
    need(peer['root_ids']==[p['peer_root']] and len(peer['key_ids'])==1,'bootstrap_expected_peer_root')
    save(folder/'bootstrap_public.json',dict(local=public,peer=peer,role=role,origin='OPERATOR_BOUND_INHERITED_CHANNEL'))
    return cap,keys,public,peer

def count_event(folder,role,wire):
    source=read(folder/'venue_work.json'); requester=read(folder/'requester_work.json')
    origin=read(folder/'producer_origin.json')
    source_attempt=read(folder/'native_attempt_venue.json')
    requester_attempt=read(folder/'native_attempt_requester.json')
    action=read(folder/'host_outcome.json') or read(folder/'action_failure.json') or {}
    stages=action.get('stages',[])
    started=sum(s['stage']=='EXECUTOR_STARTED' for s in stages)
    mutations=sum(s['stage']=='MUTATION_COMMITTED' for s in stages)
    if started and not mutations:
        mutations=None
    roots=[p.name for p in folder.iterdir() if p.is_file() and
           (p.name.endswith('_review.json') or p.name.startswith('retrieval_'))]
    return dict(role=role,source_work=(0 if source_attempt is None else len(source_attempt['attempts'])),
        requester_work=0 if requester_attempt is None else len(requester_attempt['attempts']),
        host_attempt=sum(s['stage']=='HOST_ATTEMPT' for s in stages),executor_start=started,mutations=mutations,
        root_review_adapter_calls=len((folder/'review_calls.jsonl').read_text().splitlines()) if (folder/'review_calls.jsonl').exists() else 0,
        root_review_files=roots,wire=wire,receipt_reuse=int((folder/'history.json').exists()),
        pure_verification=int((folder/'history.json').exists()),
        origin='CANDIDATE_OBSERVATIONS_SEPARATE_FROM_TRUSTED_PARENT')

def complete_report(folder,r,status,body=None,source=None,receipt=None,counts=None,slots=None,
                    *,current_source_state=None):
    counts=counts or dict(source_work=0,requester_work=0,host_attempt=0,mutations=0)
    # The producer result remains original evidence; a current publication report
    # must also reflect the actual source status. Saved receipt history has no body.
    source_state=source['status'] if source is not None else current_source_state
    if body is not None and source_state is not None and source_state!='ACTIVE':
        status='CURRENT_STATUS_UNKNOWN' if source_state=='UNAVAILABLE' or effect_started(folder) else 'REFUSED'
        slots=[]
    if slots is None:
        slots=[] if body is None or status not in ('OFFER_READY','MOCK_BOOKED','VERIFIED') else body['offer']['slots']
    result=report(r,status,slots,source,receipt,search=counts['source_work'],
        dispatch=counts['host_attempt'],mutations=counts['mutations'],observed=counts['source_work']+counts['requester_work'])
    result['native_refs']={p.stem:p.name for p in folder.iterdir() if p.is_file() and p.suffix=='.json' and p.name!='report.json'}
    save(folder/'report.json',result)
    return result

def source_entry(root,pointer,p):
    path=root/'status'/(c.sha(pointer)+'.json')
    old=read(path)
    terminals=read(root/'source_terminal.json',{})
    source_key=c.sha([pointer['source_record_ref'],pointer['source_revision']])
    if old is not None and old['state']!='ACTIVE':
        return old
    status=terminals.get(source_key,p['status'])
    need(status!='UNAVAILABLE','current_status_unavailable','CURRENT_STATUS_UNKNOWN')
    if old is not None and old['state']==status:
        return old
    entry=dict(version='g51.entry.v01',pointer_id=pointer['pointer_id'],publisher_root_id=p['local_root'],
        stream_id=pointer['revocation_stream_id'],revision=1 if old is None else old['revision']+1,
        state=status,effective_at=x.clock(),reason_ref='reason:football:operator_status')
    entry['entry_hash']=c.sha(entry); c.validate('entry',entry)
    state(path,entry)
    if status!='ACTIVE':
        terminals[source_key]=status
        state(root/'source_terminal.json',terminals)
    return entry

def failure_status(exc):
    if isinstance(exc,Refusal): return exc.status
    return 'CURRENT_STATUS_UNKNOWN' if str(exc) in ('current_status_unavailable','status_not_current',
        'SOURCE_UNAVAILABLE_PEER_CLOSED','SOURCE_UNAVAILABLE_IPC_STALLED') else 'REFUSED'

def effect_started(folder):
    outcome=read(folder/'host_outcome.json') or read(folder/'action_failure.json') or {}
    return any(stage['stage']=='EXECUTOR_STARTED' for stage in outcome.get('stages',[]))

def sign_unavailable(cap,keys,req,status,reason,history=None):
    value=dict(request_ref=req['request_id'],request_sha256=c.sha(req),status=status,reason=reason,history=history)
    return c.sign(cap,keys,'UNAVAILABLE',value,req['trust_profile_hash'])

def publisher_event(event,p,root,folder,channel,cap,keys,public,peer,budget,sequence):
    raw=event['request']; problem=None; made=None; last_status=None; report_status='REFUSED'
    try:
        r=validate_event(event,'publisher',p['local_root'])
        if r['operation']=='FIND_OFFER': approve_shift(r,p,root)
        remembered_request(root,r)
    except ValueError as exc:
        r=raw; problem=exc if isinstance(exc,Refusal) else Refusal(str(exc),'CLARIFY')
        report_status=problem.status
    for step in range(4):
        message=channel.receive()
        need(message['kind']=='REQUEST','publisher_expected_request')
        wrapped=message['value']; offered=wrapped['value']
        req=c.verify(wrapped,peer,'REQUEST',offered['trust_profile_hash'])
        c.validate('request',req)
        need(req['requester']==p['peer_root'] and req['publisher']==p['local_root'] and
             req['task_ref']==task_ref(raw) and req['object_id']==object_ref(raw) and
             req['owner_transport_scope']=='owner:football:inherited-pipes' and req['use_class']=='LOCAL_CONTEXT',
             'publisher_request_context')
        need(req['issued_at']<=x.clock()<req['deadline'],'publisher_request_expired')
        sequence['requests']+=1
        need(sequence['requests']<=32,'finite_session_requests')
        reserved=budget.reserve(req)
        save(folder/('received_request_'+str(step)+'.json'),wrapped)
        if req['op']=='CLOSE':
            need(reserved,'publisher_close_budget')
            channel.send('CLOSED',c.sign(cap,keys,'CLOSE',dict(request_ref=req['request_id'],session=event['event_id']),
                                         req['trust_profile_hash']))
            break
        try:
            need(reserved,'publisher_attempt_budget')
            if problem is not None:
                raise problem
            if req['op']=='DESCRIBE':
                need(step==0,'describe_order')
                made=build(r,event['inventory'],p,root,folder,cap,keys,public)
                if 'history' in made:
                    projection=history_projection(made['history'])
                    save(folder/'history.json',dict(projection=projection,readback=made['history']['readback'],
                                                   saved_receipt=made['history']['saved']['receipt']))
                    report_status='VERIFIED' if r['operation']=='VERIFY_EXISTING' else 'MOCK_BOOKED'
                    channel.send('UNAVAILABLE',sign_unavailable(cap,keys,req,report_status,'SAVED_RECEIPT_HISTORY',projection))
                else:
                    report_status='MOCK_BOOKED' if made['body']['booking'] is not None else made['body']['offer']['status']
                    channel.send('POINTER',made['descriptor'])
            elif req['op']=='STATUS':
                need(made is not None and 'descriptor' in made,'status_requires_pointer')
                pointer=made['descriptor']['value']
                need(req['pointer_ref']==pointer['pointer_id'],'status_pointer')
                entry=source_entry(root,pointer,p); now=x.clock()
                value=dict(version='g51.status.v01',entry=entry,requested_pointer_hash=c.sha(pointer),requester=req['requester'],
                    subject_request_ref=req['subject_request_ref'],request_revision=req['request_revision'],
                    nonce=req['nonce'],checked_at=now,valid_until=now+60)
                c.validate('status',value)
                last_status=c.sign(cap,keys,'STATUS',value,pointer['artifact_manifest_ref'].split(':')[1])
                save(folder/'status.json',last_status); channel.send('STATUS',last_status)
            elif req['op']=='FETCH':
                need(made is not None and 'body' in made,'fetch_requires_publication')
                body=made['body']; pointer=made['descriptor']['value']; now=x.clock()
                need(req['pointer_ref']==pointer['pointer_id'],'fetch_pointer')
                entry=source_entry(root,pointer,p)
                time_policy=dict(max_source_age=p['max_source_age'],max_validity_horizon=300)
                end=c.temporal(body['time_envelope'],now,time_policy)
                checks=dict(authenticated_requester=req['requester']==peer['root_ids'][0],
                    source_attempt_reserved=reserved,source_revision=budget.matches_source(req,body['source_revision']),
                    audience=req['requester'] in p['recipients'],release_enabled=p['release_enabled'],
                    active=entry['state']=='ACTIVE',bounded=pointer['body_bytes']<=req['allowed_size'])
                claim=dict(request=req,pointer_ref=pointer['pointer_id'],body_hash=c.sha(body),source_review_ref=body['source_review_ref'])
                rev=review(p['local_root'],'transaction:football:release:'+c.sha(req),req['request_id'],pointer['pointer_id'],
                    checks,claim,now,folder,'release_review',window=(body['time_envelope']['valid_from'],min(end,req['deadline'])))
                allowed=rev[2].decision=='ACCEPT'
                if allowed: budget.disclosure(req,len(c.canonical(body)))
                release=dict(version='g51.release.v01',state='RELEASED' if allowed else 'REFUSED',request_ref=req['request_id'],
                    request_revision=req['request_revision'],pointer_ref=pointer['pointer_id'],manifest_ref=made['manifest']['manifest_id'],
                    body_hash=c.sha(body),recipient=req['requester'],use_class=req['use_class'],nonce=req['nonce'],
                    deadline=req['deadline'],release_review_ref=rev[2].decision_id)
                c.validate('release',release)
                # This equality joins authenticated release bytes to this actual local Root result.
                need(release['release_review_ref']==rev[2].decision_id,'release_decision_identity')
                bundle=dict(body=body if allowed else None,manifest=made['manifest'] if allowed else None,
                    release=c.sign(cap,keys,'RELEASE',release,made['manifest']['manifest_id'].split(':')[1]))
                save(folder/'bundle.json',bundle)
                budget.response(req,allowed); channel.send('BUNDLE',bundle)
                if not allowed: report_status='CURRENT_STATUS_UNKNOWN' if effect_started(folder) else 'REFUSED'
            else:
                raise Refusal('unexpected_source_operation')
        except Refusal as exc:
            if effect_started(folder) and exc.status!='CURRENT_STATUS_UNKNOWN':
                exc=Refusal(str(exc),'CURRENT_STATUS_UNKNOWN')
            problem=exc; report_status=exc.status
            save(folder/('refusal_'+str(step)+'.json'),dict(reason=str(exc),status=exc.status,stage=req['op']))
            if req['op']=='FETCH': budget.response(req,False)
            channel.send('UNAVAILABLE',sign_unavailable(cap,keys,req,exc.status,str(exc)))
        except ValueError as exc:
            # Only documented currentness/status/budget refusals are domain outcomes.
            if str(exc) not in ('source_not_current','status_not_active','publisher_disclosure_budget','received_budget'):
                raise
            report_status='CURRENT_STATUS_UNKNOWN' if effect_started(folder) else 'REFUSED'
            problem=Refusal(str(exc),report_status)
            save(folder/('refusal_'+str(step)+'.json'),dict(reason=str(exc),status=report_status,stage=req['op']))
            if req['op']=='FETCH': budget.response(req,False)
            channel.send('UNAVAILABLE',sign_unavailable(cap,keys,req,report_status,str(exc)))
    else:
        raise ValueError('event_missing_signed_close')
    counts=count_event(folder,'publisher',channel.counters())
    save(folder/'observations.json',counts)
    body=None; source=None; receipt=None; slots=None
    retained_receipt=read(folder/'receipt.json')
    if retained_receipt is not None: receipt=retained_receipt['artifact_id']
    if made is not None:
        if 'history' in made:
            booking=made['history']['saved']['booking']
            receipt=booking['receipt_ref']; slots=booking['slots']
        else:
            body=made['body']
            if last_status is not None:
                source=context_from_checked(dict(body=body,status_entry=last_status['value']['entry']),last_status)['source_projection']
            if body['booking'] is not None: receipt=body['booking']['receipt_ref']
    return complete_report(folder,r,report_status,body,source,receipt,counts,slots,
                           current_source_state=p['status'])

def send_request(channel,budget,req,p,cap,keys,folder):
    now=x.clock()
    local=review(p['local_root'],'transaction:football:retrieve:'+c.sha(req),req['request_id'],req['object_id'],
        dict(local_endpoint=req['owner_transport_scope']=='owner:football:inherited-pipes',
             local_requester=req['requester']==p['local_root'],bounded=req['allowed_size']<=c.BODY_MAX),
        req,now,folder,'retrieval_'+req['op'].lower(),window=(req['issued_at'],req['deadline']))
    need(local[2].decision=='ACCEPT','retrieval_review_refused')
    budget.reserve(req)
    channel.send('REQUEST',c.sign(cap,keys,'REQUEST',req,req['trust_profile_hash']))
    message=channel.receive()
    return message

def unavailable(message,req,peer):
    need(message['kind']=='UNAVAILABLE','unavailable_kind')
    value=c.verify(message['value'],peer,'UNAVAILABLE',req['trust_profile_hash'])
    c.shape(value,('request_ref','request_sha256','status','reason','history'))
    need(value['request_ref']==req['request_id'] and value['request_sha256']==c.sha(req),'unavailable_request_binding')
    return value

def historical_result(r,value,root,folder):
    projection=value['history']
    c.shape(projection,('booking','entry','native_key','readback_sha256','body_sha256','receipt_ref','request_sha256'))
    old=read(object_path(root,r))
    need(old is not None,'local_receipt_history_missing','CURRENT_STATUS_UNKNOWN')
    booking=projection['booking']
    need(booking==old['booking'] and projection['receipt_ref']==booking['receipt_ref'] and
         projection['body_sha256']==old['original_body_sha256'] and
         projection['entry']['payload_sha256']==booking['payload_sha256'] and
         projection['entry']['slots']==booking['slots'] and projection['entry']['packet_ref']==booking['packet_ref'] and
         projection['request_sha256']==c.sha(old['request']),'history_remote_readback_mismatch','CURRENT_STATUS_UNKNOWN')
    need(planning_equal(r,old['request']),'history_request_changed')
    if r['operation']=='CONFIRM_MOCK_BOOKING': need(r==old['request'],'same_logical_object_changed_confirmation')
    need(r['operation'] in ('VERIFY_EXISTING','CONFIRM_MOCK_BOOKING'),'history_operation')
    c.hash_value(projection['readback_sha256'])
    save(folder/'history.json',dict(projection=projection,local=old,classification='SAVED_RECEIPT_WITH_CURRENT_SIGNED_READBACK'))
    status='VERIFIED' if r['operation']=='VERIFY_EXISTING' else 'MOCK_BOOKED'
    return report(r,status,booking['slots'],old['source'],booking['receipt_ref'],observed=1)

def refuse_inactive_status(r,policy,material,folder):
    """Record a local current-use refusal, never renew the observed source/status."""
    c.require(material is not None,'status_refusal_observation_missing')
    observed_at=material['observed_at']
    pointer=c.check_pointer(material['descriptor'],policy,material['pointer_checked_at'],profile=profile())
    fetch=material['fetch_request']; status=material['status']
    key,entry=c.authenticate_status(status,pointer,fetch,policy,observed_at,material['highwater'])
    c.require(entry['state'] in ('REVOKED','SUPERSEDED'),'status_refusal_not_terminal')
    c.require(material['highwater'].get(key)==entry,'status_refusal_terminal_not_saved')
    # Observation time is retained. This new review records refusal at its own UTC;
    # its default review window does not extend any source or STATUS lifetime.
    checks=dict(source_active=entry['state']=='ACTIVE',
        original_request=fetch['task_ref']==task_ref(r) and fetch['object_id']==object_ref(r)
            and fetch['request_revision']==r['revision'],
        local_requester=fetch['requester']==policy['local_root'],
        local_policy=fetch['trust_profile_hash']==c.sha(policy),
        source_owner=entry['publisher_root_id']==policy['peer_root'],
        terminal_saved=material['highwater'][key]==entry)
    evidence=dict(material,request=r,policy=policy)
    save(folder/'status_refusal_evidence.json',evidence)
    received_body=read(folder/'offer_body.json')
    booking=None if received_body is None else received_body['booking']
    # CONFIRM may already have reached the source effect boundary before DESCRIBE
    # returned. A requester-local refusal cannot certify that source outcome.
    outcome='CURRENT_STATUS_UNKNOWN' if r['operation']=='CONFIRM_MOCK_BOOKING' or effect_started(folder) or booking is not None else 'REFUSED'
    claim=dict(request=r,request_sha256=c.sha(r),reason='status_not_active',status=outcome,
        source_record_ref=pointer['source_record_ref'],source_revision=pointer['source_revision'],
        source_review_ref=pointer['source_review_ref'],pointer_ref=pointer['pointer_id'],
        fetch_request_ref=fetch['request_id'],status_sha256=c.sha(status),
        status_entry=entry,observed_at=observed_at,evidence_sha256=c.sha(evidence))
    identity=c.sha(claim)
    live=review(policy['local_root'],'transaction:football:status_refusal:'+identity,
        'candidate:football:status_refusal:'+identity,r['request_id'],checks,claim,x.clock(),
        folder,'refusal_review',predicate='football_current_source_status_v01')
    c.require(live[2].decision=='BLOCKED_FAIL_CLOSED','status_refusal_root_outcome')
    save(folder/'refusal.json',dict(reason=claim['reason'],status=outcome,
        review_ref=live[2].decision_id,evidence_ref='status_refusal_evidence.json',
        evidence_sha256=c.sha(evidence)))
    return report(r,outcome,receipt=None if booking is None else booking['receipt_ref'])

def requester_event(event,p,root,folder,channel,cap,keys,peer):
    raw=event['request']; local_problem=None; result=None; status_observation=None
    try:
        r=validate_event(event,'requester',p['local_root'])
        need(p['accept_football'],'local_policy_refusal')
        if r['operation']=='FIND_OFFER': approve_shift(r,p,root)
        if r['operation']=='CONFIRM_MOCK_BOOKING' and read(object_path(root,r)) is None:
            preflight=read(history_path(root,r))
            need(preflight is not None,'requester_original_offer_missing','CURRENT_STATUS_UNKNOWN')
            need(planning_equal(r,preflight['body']['offer']['request']),'requester_changed_offer_request')
            approve_booking(r,preflight['body'],p)
        remembered_request(root,r)
    except ValueError as exc:
        r=raw; local_problem=exc if isinstance(exc,Refusal) else Refusal(str(exc),'CLARIFY')
    budget=x.Budget(root/'budgets'/(c.sha(raw)+'.json'),task_ref(raw))
    # Budget's parent must exist before its atomic writer creates the state.
    describe=request(p,raw,'DESCRIBE')
    msg=None
    if local_problem is None:
        msg=send_request(channel,budget,describe,p,cap,keys,folder)
        save(folder/'describe_response.json',msg)
    try:
        if local_problem is not None:
            raise local_problem
        if msg['kind']=='UNAVAILABLE':
            value=unavailable(msg,describe,peer)
            if value['history'] is not None:
                result=historical_result(r,value,root,folder)
            else:
                raise Refusal(value['reason'],value['status'])
        else:
            need(msg['kind']=='POINTER','pointer_response')
            if r['operation']=='FIND_OFFER':
                original=r; prior=None
            else:
                prior=read(history_path(root,r))
                need(prior is not None,'requester_original_offer_missing','CURRENT_STATUS_UNKNOWN')
                original=prior['body']['offer']['request']
                need(planning_equal(r,original),'requester_changed_offer_request')
                approve_booking(r,prior['body'],p)
            policy=consumer_policy(p,peer,r,original)
            pointer_time=x.clock()
            pointer=c.check_pointer(msg['value'],policy,pointer_time,profile=profile())
            save(folder/'descriptor.json',msg['value'])
            source_end=c.temporal(pointer['time_envelope'],x.clock(),policy)
            descent(pointer,p['local_root'],folder,x.clock(),source_end)
            fetch=request(p,r,'FETCH',policy,pointer)
            status_req=request(p,r,'STATUS',policy,pointer,fetch['request_id'],fetch['nonce'])
            observed=send_request(channel,budget,status_req,p,cap,keys,folder)
            save(folder/'status_request.json',status_req)
            if observed['kind']=='UNAVAILABLE':
                v=unavailable(observed,status_req,peer)
                raise Refusal(v['reason'],'CURRENT_STATUS_UNKNOWN')
            need(observed['kind']=='STATUS','status_response')
            store=ImportStore(root/'imports')
            # Authenticated terminal entries are persisted before ACTIVE/current-use refusal.
            status_time=x.clock()
            store.observe(observed['value'],pointer,fetch,policy,status_time)
            save(folder/'status.json',observed['value'])
            highwater=read(store.path)['highwater']
            status_check_time=x.clock()
            status_observation=dict(descriptor=msg['value'],fetch_request=fetch,status_request=status_req,
                status=observed['value'],highwater=highwater,pointer_checked_at=pointer_time,
                authenticated_at=status_time,observed_at=status_check_time)
            c.check_status(observed['value'],pointer,fetch,policy,status_check_time,highwater)
            received=send_request(channel,budget,fetch,p,cap,keys,folder)
            save(folder/'fetch_request.json',fetch)
            save(folder/'fetch_response.json',received)
            if received['kind']=='UNAVAILABLE':
                v=unavailable(received,fetch,peer); raise Refusal(v['reason'],v['status'])
            need(received['kind']=='BUNDLE','bundle_response')
            now=x.clock()
            material=dict(bundle=received['value'],descriptor=msg['value'],request=fetch,status=observed['value'])
            save(folder/'retrieval_material.json',material); save(folder/'local_policy.json',policy)
            save(folder/'local_use_time.json',dict(utc=now))
            try:
                checked=c.check_bundle(received['value'],msg['value'],fetch,observed['value'],policy,now,
                    read(store.path)['highwater'],store.conflicts(),profile=profile())
            except ValueError as exc:
                store.quarantine(str(exc),material)
                raise
            body=checked['body']
            budget.received_body(len(c.canonical(body)))
            kind=store.import_body(checked,pointer)
            dependency=c.sha(dict(request=r,policy=policy,source=c.sha(body),status=observed['value']['value']))
            candidate=c.with_id('import',dict(version='g51.import.v01',local_request_ref=fetch['request_id'],
                pointer_ref=pointer['pointer_id'],foreign_publisher=body['publisher'],foreign_source_ref=body['source_record_ref'],
                foreign_revision=body['source_revision'],received_manifest_hash=c.sha(received['value']['manifest']),
                body_hash=c.sha(body),receive_event_ref='receive:football:'+c.sha(material),
                validation_results={k:checked['body'] is body for k in ('shape','signature','integrity','arithmetic',
                    'provenance','temporal','scope','status','conflict','local_policy')},
                status_entry_hash=checked['status_entry']['entry_hash'],dependency_fingerprint=dependency,
                policy_hash=c.sha(policy),creates_permission=False))
            c.validate('import',candidate)
            save(folder/'import_candidate.json',candidate)
            rev=review(p['local_root'],'transaction:football:import:'+dependency,candidate['import_id'],body['source_record_ref'],
                dict(original_request=planning_equal(r,body['offer']['request']),
                audience=body['recipient']==p['local_root'],active=checked['status_entry']['state']=='ACTIVE'),
                dict(import_candidate=candidate,request_sha256=c.sha(r),body_sha256=c.sha(body)),now,folder,'import_review',
                window=(body['time_envelope']['valid_from'],min(checked['source_end'],fetch['deadline'])))
            need(rev[2].decision=='ACCEPT','import_review_refused')
            disposition=c.with_id('disposition',dict(version='g51.disposition.v01',candidate_ref=candidate['import_id'],
                parent_ref=None,state='ACCEPTED_CONTEXT',local_review_ref=rev[2].decision_id))
            c.validate('disposition',disposition); save(folder/'import_disposition.json',disposition)
            # Refresh time checks immediately before the PURE consumer, retaining original signed STATUS.
            use_time=x.clock()
            checked=c.check_bundle(received['value'],msg['value'],fetch,observed['value'],policy,use_time,
                read(store.path)['highwater'],store.conflicts(),profile=profile())
            save(folder/'consumer_use_time.json',dict(utc=use_time))
            context=context_from_checked(checked,observed['value'])
            save(folder/'consumption_context.json',context); save(folder/'offer_body.json',body)
            work=perform('requester',r,context,p['local_root'],'task:football:consume:'+dependency,evidence_folder=folder)
            save(folder/'requester_work.json',work)
            result=c.decode(work['outputs']['result_json'].encode())
            need(result==consume(r,context),'reported_consumer_binding')
            claim=dict(request_sha256=c.sha(r),offer_sha256=c.sha(body),result_sha256=c.sha(result))
            final=review(p['local_root'],'transaction:football:result:'+dependency,work['artifact']['artifact_id'],
                r['request_id'],dict(native_result=work['attempts']==1,consumed_original_request=planning_equal(r,body['offer']['request'])),
                claim,x.clock(),folder,'requester_review',
                window=(body['time_envelope']['valid_from'],min(checked['source_end'],fetch['deadline'],
                    observed['value']['value']['valid_until'],observed['value']['value']['checked_at']+60)))
            need(final[2].decision=='ACCEPT','requester_result_review_refused')
            save(root/'accepted'/(c.sha(body)+'.json'),dict(body=body,material=material,context=context,work=work,review=n.root_plain(final)))
            if r['operation']=='FIND_OFFER':
                state(history_path(root,r),dict(body=body,request=r,source=context['source_projection']))
            else:
                save(object_path(root,r),dict(request=r,booking=body['booking'],
                     original_body_sha256=c.sha(prior['body']),source=context['source_projection']))
            save(folder/'dedup.json',dict(disposition=kind,independent_source_credit=0))
    except Refusal as exc:
        received_body=read(folder/'offer_body.json')
        if received_body is not None and received_body['booking'] is not None:
            exc=Refusal(str(exc),'CURRENT_STATUS_UNKNOWN')
        save(folder/'refusal.json',dict(reason=str(exc),status=exc.status))
        rev=review(p['local_root'],'transaction:football:refusal:'+c.sha(raw),'candidate:football:refusal:'+c.sha(raw),
            object_ref(raw),dict(required_predicate=False),dict(reason=str(exc),request=raw),x.clock(),folder,'refusal_review')
        result=report(raw,exc.status)
    except ValueError as exc:
        known=('source_not_current','status_not_active','status_not_current','status_rollback','status_equivocation',
               'status_terminal_revival','source_equivocation','release_refused','local_policy_refusal','attempt_budget',
               'received_budget','football_audience','football_original_request','football_request_policy','football_budget')
        if str(exc) not in known:
            raise
        if str(exc)=='status_not_active':
            result=refuse_inactive_status(raw,policy,status_observation,folder)
        else:
            save(folder/'refusal.json',dict(reason=str(exc),status=failure_status(exc)))
            result=report(raw,failure_status(exc))
    close=request(p,raw,'CLOSE')
    message=send_request(channel,budget,close,p,cap,keys,folder)
    need(message['kind']=='CLOSED','signed_close_required')
    closed=c.verify(message['value'],peer,'CLOSE',close['trust_profile_hash'])
    c.shape(closed,('request_ref','session'))
    need(closed==dict(request_ref=close['request_id'],session=event['event_id']),'signed_close_binding')
    save(folder/'close.json',message)
    counts=count_event(folder,'requester',channel.counters()); save(folder/'observations.json',counts)
    need(result is not None,'missing_result')
    if (folder/'refusal.json').exists():
        result['counts']=dict(search=int((folder/'pointer_lookup.json').exists()),dispatch=0,mutations=0,
                              observed=counts['requester_work'])
    result['native_refs']={path.stem:path.name for path in folder.iterdir() if path.is_file() and
                           path.suffix=='.json' and path.name!='report.json'}
    save(folder/'report.json',result)
    return result

def run_peer_v01(*, role: str, input_data: dict, state_root: pathlib.Path,
                 output_root: pathlib.Path, channel: PipeChannel,
                 bootstrap: PipeChannel) -> dict | None:
    need(role in ('publisher','requester'),'peer_role')
    c.shape(input_data,('version','role','events','policy'))
    need(input_data['version']=='g54.peer_input.v01' and input_data['role']==role,'peer_input_identity')
    p=input_data['policy']; validate_policy(p)
    events=input_data['events']
    need(type(events) is list and len(events)<=8,'finite_event_bound')
    ids=[local_name(event['event_id']) for event in events]
    need(len(set(ids))==len(ids),'duplicate_event_id')
    state_root.mkdir(parents=True,exist_ok=True); output_root.mkdir(parents=True,exist_ok=True)
    save(output_root/'operator_policy.json',p)
    cap,keys,public,peer=boot(role,p,bootstrap,output_root)
    contexts={}
    if role=='publisher':
        for event in events:
            r=event['request']; revision=event['inventory'].get('revision')
            key=task_ref(r)
            context=dict(requester=p['peer_root'],object_id=object_ref(r),purpose='FOOTBALL_'+str(r.get('operation')),
                         uses=['LOCAL_CONTEXT'])
            if type(revision) is int and revision>0: context['source_revision']=revision
            # Repetition does not reset or change the operator's first task context.
            if key not in contexts: contexts[key]=context
        budget=x.PublisherBudget(state_root/'publisher_budget.json',contexts)
    sequence=dict(requests=0); results=[]
    for event in events:
        folder=output_root/event['event_id']; folder.mkdir()
        save(folder/'original_event.json',event)
        save(folder/'event_clock.json',dict(observed_at=x.clock(),native_clock='CONTROLLED_LOGICAL_1014'))
        try:
            if role=='publisher':
                value=publisher_event(event,p,state_root,folder,channel,cap,keys,public,peer,budget,sequence)
            else:
                value=requester_event(event,p,state_root,folder,channel,cap,keys,peer)
            results.append(dict(event_id=event['event_id'],status=value['status']))
        except Exception as exc:
            # Unknown setup/ABI/I/O failures remain observable and terminate this finite peer.
            save(folder/'unhandled_failure.json',dict(type=type(exc).__name__,reason=str(exc),role=role))
            if role=='publisher' and effect_started(folder) and not (folder/'report.json').exists():
                actual=count_event(folder,role,channel.counters())
                retained=read(folder/'receipt.json')
                complete_report(folder,event['request'],'CURRENT_STATUS_UNKNOWN',
                    receipt=None if retained is None else retained['artifact_id'],counts=actual)
            raise
    save(output_root/'completion.json',dict(role=role,events=results,wire=channel.counters(),executed_provider_calls=0))
    return dict(role=role,events_processed=len(results))
