"""Bounded signed inherited-pipe bridge. No PURE executor performs transport I/O."""
import json
import hashlib
import os
import secrets
import select
import struct
import time
from pathlib import Path
from hedgehog.drs import LocalDRS
from hedgehog import local_drs_resolver as resolver
from . import gate5_contracts_v01 as c, gate5_native_v01 as n


def clock(): return int(time.time())


def immutable(path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    body=c.canonical(value)
    if path.exists(): c.require(path.read_bytes()==body,'immutable_replacement')
    else:
        with path.open('xb') as stream: stream.write(body)


def state_write(path, value):
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix('.pending')
    with tmp.open('wb') as stream:
        stream.write(c.canonical(value));stream.flush();os.fsync(stream.fileno())
    os.replace(tmp,path)


def phase(folder, name, event, **extra):
    with (folder/'phases.jsonl').open('a') as stream:
        stream.write(json.dumps(dict(phase=name,event=event,utc=clock(),monotonic=time.monotonic(),**extra))+'\n')


class Budget:
    def __init__(self,path,task):
        self.path,self.task=path,task
        if not path.exists(): state_write(path,dict(task=task,metadata=0,payload=0,opened=0,body_bytes=0,reservations=[]))

    def read(self):
        value=c.decode(self.path.read_bytes());c.require(value['task']==self.task,'budget_task');return value

    def reserve(self,request):
        value=self.read();key='payload' if request['op']=='FETCH' else 'metadata'
        c.require(request['request_id'] not in value['reservations'],'request_already_reserved')
        c.require(value[key] < (2 if key=='payload' else 8),'attempt_budget')
        value[key]+=1;value['reservations'].append(request['request_id']);state_write(self.path,value)

    def received_body(self,size):
        c.require(0 < c.integer(size) <= c.BODY_MAX,'received_body_size')
        value=self.read();c.require(value['opened']<2 and value['body_bytes']+size<=131072,'received_budget')
        value['opened']+=1;value['body_bytes']+=size;state_write(self.path,value)


class PublisherBudget:
    """Owner-established contexts, durable reservations before source disclosure.

    Finite single-writer IPC profile; concurrent multi-writer service is not claimed.
    Requester-controlled task labels never establish or reset a context.
    """
    def __init__(self,path,contexts):
        self.path,self.contexts=Path(path),contexts
        if not self.path.exists():
            state_write(self.path,dict(contexts=contexts,tasks={},events=[]))
        c.require(self.read()['contexts']==contexts,'publisher_context_changed')

    def read(self): return json.loads(self.path.read_text())

    def reserve(self,req):
        state=self.read();context=self.contexts.get(req['task_ref'])
        c.require(context is not None,'publisher_unknown_task_context')
        c.require(req['requester']==context['requester'] and req['object_id']==context['object_id'],'publisher_context_binding')
        if 'uses' in context:c.require(req['use_class'] in context['uses'],'publisher_context_use')
        row=state['tasks'].setdefault(req['task_ref'],dict(metadata=0,payload=0,attempts=0,denied=0,
            bodies=0,body_bytes=0,request_ids=[],disclosures=[],refused_responses=0,released_responses=0))
        row['attempts']+=1;key='payload' if req['op']=='FETCH' else 'metadata'
        allowed=req['request_id'] not in row['request_ids'] and row[key] < (2 if key=='payload' else 8)
        if allowed:row[key]+=1;row['request_ids'].append(req['request_id'])
        else:row['denied']+=1
        state['events'].append(dict(request=req['request_id'],task=req['task_ref'],operation='RESERVE_ATTEMPT',allowed=allowed))
        state_write(self.path,state)
        return allowed

    def response(self,req,released):
        state=self.read();row=state['tasks'][req['task_ref']]
        row['released_responses' if released else 'refused_responses']+=1
        state_write(self.path,state)

    def matches_source(self,req,revision):
        context=self.contexts[req['task_ref']]
        return 'source_revision' not in context or context['source_revision']==revision

    def disclosure(self,req,size):
        c.require(0 < c.integer(size) <= min(c.BODY_MAX,req['allowed_size']),'publisher_body_size')
        state=self.read();row=state['tasks'][req['task_ref']]
        c.require(req['request_id'] in row['request_ids'] and req['request_id'] not in row['disclosures'],'publisher_unreserved_disclosure')
        c.require(row['bodies']<2 and row['body_bytes']+size<=131072,'publisher_disclosure_budget')
        row['bodies']+=1;row['body_bytes']+=size;row['disclosures'].append(req['request_id'])
        state['events'].append(dict(request=req['request_id'],task=req['task_ref'],operation='RESERVE_DISCLOSURE',bytes=size))
        state_write(self.path,state)


class PipeChannel:
    def __init__(self,read_fd,write_fd,folder):
        self.read_fd,self.write_fd,self.folder=read_fd,write_fd,folder
        self.sent=self.received=self.sent_bytes=self.received_bytes=0

    def exact(self,size,allow_eof=False):
        data=b''
        while len(data)<size:
            c.require(bool(select.select([self.read_fd],[],[],60)[0]),'SOURCE_UNAVAILABLE_IPC_STALLED')
            chunk=os.read(self.read_fd,size-len(data))
            if not chunk and not data and allow_eof:return None
            c.require(bool(chunk),'SOURCE_UNAVAILABLE_PEER_CLOSED');data+=chunk
        return data

    def receive(self,allow_eof=False):
        header=self.exact(4,allow_eof)
        if header is None:return None
        size=struct.unpack('!I',header)[0]
        c.require(size<=c.WIRE_MAX,'frame_size_before_payload_read')
        body=self.exact(size);self.received+=1;self.received_bytes+=len(body)+4
        (self.folder/('wire_received_%02d.json'%self.received)).write_bytes(body)
        value=c.decode(body);c.shape(value,('kind','value'));c.require(value['kind'] in ('REQUEST','POINTER','STATUS','BUNDLE','UNAVAILABLE','CLOSED'),'wire_kind')
        return value

    def send(self,kind,value):
        body=c.canonical(dict(kind=kind,value=value));c.decode(body)
        packet=struct.pack('!I',len(body))+body
        while packet:packet=packet[os.write(self.write_fd,packet):]
        self.sent+=1;self.sent_bytes+=len(body)+4
        (self.folder/('wire_sent_%02d.json'%self.sent)).write_bytes(body)

    def counters(self):return dict(sent=self.sent,received=self.received,sent_bytes=self.sent_bytes,received_bytes=self.received_bytes)


def source_time(now):
    return c.drs.drs_time_envelope_to_plain_data_v01(c.drs.build_drs_time_envelope_v01(pt_created_at=now,kt_as_of=now,et_observed_at=now,
        ct_context_anchor=now,ttl_seconds=300,valid_from=now,valid_to=now+300,source_observed_at=now,source_reported_at=now,
        system_ingested_at=now,system_verified_at=now,freshness_policy_id='freshness:gate5:source'))


def build_source(inputs,cap,keys,policy,folder):
    phase(folder,'native_source','START')
    revision=inputs.get('revision',1);c.require(c.integer(revision)>0,'source_revision')
    work=n.native_work('source',c.ROOT_A,'task:gate5:source:'+str(revision),dict(readings=c.canonical(inputs['observations']).decode(),reference=inputs['reference']))
    n.save(folder/'source_work.json',work)
    now=clock();result=work['outputs']
    projection=dict(source_record_ref=policy['source_record_ref'],source_revision=revision,unit_id=inputs['unit_id'],quantity_id=inputs['quantity_id'],
        reference=inputs['reference'],observations=inputs['observations'],n=result['n'],total=result['total'],
        correction=dict(num=result['correction_num'],den=result['correction_den']),source_work_ref=work['artifact']['artifact_id'])
    review=n.root_review(c.ROOT_A,'transaction:gate5:source',work['artifact']['artifact_id'],policy['source_record_ref'],
        dict(actual_native_work=work['attempts']==1,local_units=inputs['unit_id']==policy['unit_id'] and inputs['quantity_id']==policy['quantity_id']),projection,now)
    n.save(folder/'source_review.json',n.root_plain(review))
    c.require(review[2].decision=='ACCEPT','source_review_refused')
    body=dict(version='g51.body.v01',**projection,source_review_ref=review[2].decision_id,time_envelope=source_time(now),
        ttl_base='pt_created_at',source_lineage_refs=inputs.get('predecessor_work_refs',[])+[work['artifact']['artifact_id']])
    c.contract('body',body)
    manifest=c.with_id('manifest',dict(version='g51.manifest.v01',publisher=c.ROOT_A,source_revision=revision,
        source_refs=[body['source_record_ref'],body['source_work_ref'],body['source_review_ref']],declared_schema=c.BODY_SCHEMA,
        files=[dict(path='body.json',bytes=len(c.canonical(body)),sha256=c.sha(body))]));c.contract('manifest',manifest)
    pointer=c.with_id('pointer',dict(version='g51.pointer.v01',publisher_root_id=c.ROOT_A,publisher_key_id=cap.key_id,
        semantic_address=dict(namespace='gate5',domain='CALIBRATION',subject_class='bounded_calibration',intent_class='context_lookup',schema_id=c.BODY_SCHEMA,schema_version='v01'),
        source_record_ref=body['source_record_ref'],source_revision=revision,source_review_ref=body['source_review_ref'],body_sha256=c.sha(body),body_bytes=len(c.canonical(body)),
        media_type='application/json',artifact_manifest_ref=manifest['manifest_id'],safe_summary=c.canonical(dict(kind='calibration',unit_id=inputs['unit_id'],quantity_id=inputs['quantity_id'])).decode(),
        published_scope=dict(domain='CALIBRATION',unit_id=inputs['unit_id'],quantity_id=inputs['quantity_id']),allowed_use_classes=['AUDIT','LOCAL_CONTEXT'],
        forbidden_use_classes=['ACTION'],recipient_scope=[c.ROOT_B],time_envelope=body['time_envelope'],source_lineage_refs=body['source_lineage_refs'],
        access_policy_ref=policy['source_policy_ref'],revocation_stream_id='stream:gate5:calibration:'+str(revision),transport_object_id='object:gate5:calibration:one',
        creates_authority=False,creates_permission=False));c.contract('pointer',pointer)
    publish=n.root_review(c.ROOT_A,'transaction:gate5:publish',pointer['pointer_id'],body['source_record_ref'],
        dict(owner_publish_policy=policy['publish_enabled'],bounded_projection=len(c.canonical(pointer))<=c.POINTER_MAX),pointer,clock(),
        window=(now,now+300))
    c.require(publish[2].decision=='ACCEPT','publish_refused');n.save(folder/'publish_review.json',n.root_plain(publish))
    descriptor=c.sign(cap,keys,'POINTER',pointer,manifest['manifest_id'].split(':')[1])
    entry=dict(version='g51.entry.v01',pointer_id=pointer['pointer_id'],publisher_root_id=c.ROOT_A,stream_id=pointer['revocation_stream_id'],
        revision=1,state='ACTIVE',effective_at=now,reason_ref='reason:gate5:published')
    entry['entry_hash']=c.sha(entry);c.contract('entry',entry)
    for name,value in [('body',body),('manifest',manifest),('pointer',descriptor),('status_entry',entry)]:immutable(folder/(name+'.json'),value)
    resolver.write_semantic_record(LocalDRS(folder/'source_drs'),resolver.SemanticDRSRecordInput(record_id=body['source_record_ref'],domain='CALIBRATION',
        content=dict(source=body),semantic_keys=('calibration','source')))
    phase(folder,'native_source','COMPLETE',work_seconds=work['seconds'])
    return body,manifest,descriptor,entry


def request(policy,op,pointer=None,use='LOCAL_CONTEXT',subject=None,nonce=None):
    now=clock()
    value=c.with_id('request',dict(version='g51.request.v01',op=op,requester=c.ROOT_B,publisher=c.ROOT_A,task_ref='task:gate5:exchange',
        request_revision=1,pointer_ref=None if pointer is None else pointer['pointer_id'],trust_profile_hash=c.sha(policy),use_class=use,
        object_id=policy['object_id'],allowed_size=c.BODY_MAX,nonce=nonce or secrets.token_hex(32),issued_at=now,deadline=now+60,
        subject_request_ref=subject,owner_transport_scope='owner:gate5:inherited-pipes'))
    return c.contract('request',value).plain()


def send_request(channel,budget,req,policy,cap,keys,folder):
    now=clock()
    checks=dict(owner_endpoint=policy['endpoint']=='endpoint:gate5:A' and req['owner_transport_scope']==policy['transport_scope'],
        policy_identity=req['trust_profile_hash']==c.sha(policy),local_use=req['use_class'] in policy['uses'])
    review=n.root_review(c.ROOT_B,'transaction:gate5:retrieval',req['request_id'],req['object_id'],checks,req,now,window=(req['issued_at'],req['deadline']))
    c.require(review[2].decision=='ACCEPT','retrieval_refused')
    n.save(folder/('retrieval_'+req['request_id']+'.json'),n.root_plain(review))
    budget.reserve(req)
    channel.send('REQUEST',c.sign(cap,keys,'REQUEST',req,req['trust_profile_hash']))
    return channel.receive()


def publisher(channel,cap,keys,bootstrap,folder):
    policy=bootstrap['own_policy'];request_policy=bootstrap['requester_policy']
    private=folder/'private';private.mkdir();canary=secrets.token_hex(32);(private/'canary.txt').write_text(canary)
    inputs=json.loads((folder/'scenario.json').read_text())
    body,manifest,descriptor,entry=build_source(inputs,cap,keys,policy,folder)
    pointer=descriptor['value'];seen=set();counts=dict(metadata=0,payload=0,released=0,body_bytes=0)
    contexts={'task:gate5:exchange':dict(requester=c.ROOT_B,object_id='object:gate5:calibration:one')}
    for i in range(32):
        message=channel.receive(allow_eof=True)
        if message is None:break
        c.require(message['kind']=='REQUEST','expected_request')
        req=c.verify(message['value'],bootstrap['peer_keys'],'REQUEST',c.sha(request_policy));c.validate('request',req)
        c.require(req['request_id'] not in seen and req['issued_at']<=clock()<req['deadline'],'request_replay_or_expiry');seen.add(req['request_id'])
        c.require(req['requester']==c.ROOT_B and req['publisher']==c.ROOT_A and req['object_id']=='object:gate5:calibration:one','request_identity')
        c.require(req['trust_profile_hash']==c.sha(request_policy) and req['owner_transport_scope']==request_policy['transport_scope'],'request_policy')
        budget=PublisherBudget(folder/'publisher_budget.json',contexts)
        reserved=budget.reserve(req)
        if req['op']!='FETCH':c.require(reserved,'publisher_attempt_budget')
        if req['op']=='DESCRIBE':
            counts['metadata']+=1;channel.send('POINTER',descriptor)
        elif req['op']=='STATUS':
            counts['metadata']+=1;c.require(req['pointer_ref']==pointer['pointer_id'],'status_pointer')
            now=clock();status=dict(version='g51.status.v01',entry=entry,requested_pointer_hash=c.sha(pointer),requester=req['requester'],
                subject_request_ref=req['subject_request_ref'],request_revision=req['request_revision'],nonce=req['nonce'],checked_at=now,valid_until=now+60)
            c.contract('status',status);channel.send('STATUS',c.sign(cap,keys,'STATUS',status,manifest['manifest_id'].split(':')[1]))
        else:
            counts['payload']+=1;c.require(req['pointer_ref']==pointer['pointer_id'],'fetch_pointer')
            checks=dict(authenticated_requester=req['requester']==bootstrap['peer_keys']['root_ids'][0],
                source_attempt_reserved=reserved,
                audience=req['requester'] in policy['recipients'],allowed_use=req['use_class'] in policy['release_uses'],
                object_matches=req['object_id']==pointer['transport_object_id'],size_fits=pointer['body_bytes']<=req['allowed_size'])
            review=n.root_review(c.ROOT_A,'transaction:gate5:release',req['request_id'],pointer['pointer_id'],checks,
                dict(request=req,pointer_ref=pointer['pointer_id'],body_hash=c.sha(body)),clock(),
                window=(body['time_envelope']['valid_from'],min(c.temporal(body['time_envelope'],clock(),policy),req['deadline'])))
            n.save(folder/('release_review_%d.json'%counts['payload']),n.root_plain(review))
            allowed=review[2].decision=='ACCEPT'
            if allowed:budget.disclosure(req,len(c.canonical(body)))
            release=dict(version='g51.release.v01',state='RELEASED' if allowed else 'REFUSED',request_ref=req['request_id'],request_revision=req['request_revision'],
                pointer_ref=pointer['pointer_id'],manifest_ref=manifest['manifest_id'],body_hash=c.sha(body),recipient=req['requester'],use_class=req['use_class'],
                nonce=req['nonce'],deadline=req['deadline'],release_review_ref=review[2].decision_id)
            c.contract('release',release)
            response=dict(release=c.sign(cap,keys,'RELEASE',release,manifest['manifest_id'].split(':')[1]),manifest=manifest if allowed else None,body=body if allowed else None)
            c.require(canary.encode() not in c.canonical(response),'private_projection_leak')
            if allowed:counts['released']+=1;counts['body_bytes']+=len(c.canonical(body))
            budget.response(req,allowed)
            channel.send('BUNDLE',response)
    else:raise ValueError('publisher_finite_session_limit')
    public_files=[p for p in folder.rglob('*') if p.is_file() and private not in p.parents]
    c.require(all(canary.encode() not in p.read_bytes() for p in public_files),'observed_public_canary_leak')
    n.save(folder/'result.json',dict(status='SOURCE_AND_RELEASE_COMPLETE',counts=counts,wire=channel.counters(),
        canary_scan=dict(files=len(public_files),matches=0,private_body_excluded=True),source_result=body['correction']))


def requester(channel,cap,keys,bootstrap,folder):
    policy=bootstrap['own_policy'];scenario=json.loads((folder/'scenario.json').read_text());readings=scenario['readings']
    budget=Budget(folder/'budget.json','task:gate5:exchange')
    before=n.native_work('mean',c.ROOT_B,'task:gate5:uncalibrated',dict(readings=c.canonical(readings).decode()))
    refusal=n.root_review(c.ROOT_B,'transaction:gate5:uncalibrated','candidate:gate5:missing','source:gate5:calibration:one',
        dict(eligible_calibration=False),dict(status='INSUFFICIENT_EVIDENCE',mean=before['outputs']),clock())
    n.save(folder/'uncalibrated.json',dict(status='INSUFFICIENT_EVIDENCE',work=before,root=n.root_plain(refusal)))
    phase(folder,'exchange','START')
    response=send_request(channel,budget,request(policy,'DESCRIBE'),policy,cap,keys,folder)
    c.require(response['kind']=='POINTER','descriptor_response')
    descriptor=response['value'];c.check_pointer(descriptor,policy,clock())
    descriptor=n.persist_and_resolve_pointer(descriptor,folder,policy);pointer=c.check_pointer(descriptor,policy,clock())
    immutable(folder/'descriptor.json',descriptor)
    # A separate declared negative local policy cannot inherit A's publish approval.
    observed=channel.counters();negative=dict(policy,accept_calibration=False)
    denied=n.root_review(c.ROOT_B,'transaction:gate5:local-negative','candidate:gate5:local-negative',pointer['pointer_id'],
        dict(local_policy=negative['accept_calibration']),dict(policy_hash=c.sha(negative),pointer=pointer['pointer_id']),clock())
    c.require(denied[2].decision!='ACCEPT','foreign_accept_bypassed_local_root')
    n.save(folder/'local_refusal.json',dict(scope='BEFORE_BODY_FETCH_AFTER_AUTHORIZED_DESCRIPTOR',root=n.root_plain(denied),before=observed,after=channel.counters(),body_attempts=budget.read()['payload']))
    history={};conflicts={};accepted=None
    for use in scenario['use_sequence']:
        fetch=request(policy,'FETCH',pointer,use)
        status_request=request(policy,'STATUS',pointer,use,subject=fetch['request_id'],nonce=fetch['nonce'])
        status_response=send_request(channel,budget,status_request,policy,cap,keys,folder);c.require(status_response['kind']=='STATUS','status_response')
        status=status_response['value'];key,entry=c.check_status(status,pointer,fetch,policy,clock(),history)
        history[key]=entry;state_write(folder/'status_highwater.json',history)
        response=send_request(channel,budget,fetch,policy,cap,keys,folder);c.require(response['kind']=='BUNDLE','bundle_response')
        bundle=response['value'];c.shape(bundle,('release','manifest','body'))
        release=c.verify(bundle['release'],policy['peer_keys'],'RELEASE',pointer['artifact_manifest_ref'].split(':')[1]);c.validate('release',release)
        immutable(folder/('request_'+use+'.json'),fetch);immutable(folder/('status_'+use+'.json'),status);immutable(folder/('response_'+use+'.json'),bundle)
        if release['state']=='REFUSED':
            c.require(bundle['body'] is None and bundle['manifest'] is None,'refusal_disclosed_body')
            continue
        size=len(c.canonical(bundle['body']));budget.received_body(size)
        receive=dict(request_ref=fetch['request_id'],wire_message=channel.received,body_bytes=size,received_at=clock())
        immutable(folder/'quarantine/body.json',bundle['body']);immutable(folder/'quarantine/manifest.json',bundle['manifest'])
        immutable(folder/'receive.json',receive)
        checked=c.check_bundle(bundle,descriptor,fetch,status,policy,clock(),history,conflicts)
        conflicts[checked['conflict_key']]=c.sha(bundle['body']);state_write(folder/'source_conflicts.json',conflicts)
        dependency=c.sha(dict(readings=readings,limit=scenario['limit'],policy=c.sha(policy),source=c.sha(bundle['body'])))
        candidate=c.with_id('import',dict(version='g51.import.v01',local_request_ref=fetch['request_id'],pointer_ref=pointer['pointer_id'],foreign_publisher=pointer['publisher_root_id'],
            foreign_source_ref=pointer['source_record_ref'],foreign_revision=pointer['source_revision'],received_manifest_hash=c.sha(bundle['manifest']),body_hash=c.sha(bundle['body']),
            receive_event_ref='g5receive:'+c.sha(receive),validation_results={k:True for k in ('shape','signature','integrity','arithmetic','provenance','temporal','scope','status','conflict','local_policy')},
            status_entry_hash=checked['status_entry']['entry_hash'],dependency_fingerprint=dependency,policy_hash=c.sha(policy),creates_permission=False));c.contract('import',candidate)
        disposition=c.with_id('disposition',dict(version='g51.disposition.v01',candidate_ref=candidate['import_id'],parent_ref=None,state='CANDIDATE',local_review_ref=None))
        immutable(folder/'import_candidate.json',candidate);immutable(folder/'disposition_candidate.json',disposition)
        local=n.root_review(c.ROOT_B,'transaction:gate5:import',candidate['import_id'],pointer['source_record_ref'],
            dict(local_policy=policy['accept_calibration'],verified_components=all(candidate['validation_results'].values())),candidate,clock(),
            window=(pointer['time_envelope']['valid_from'],min(checked['source_end'],fetch['deadline'],status['value']['valid_until'])))
        c.require(local[2].decision=='ACCEPT','local_import_refused');n.save(folder/'import_review.json',n.root_plain(local))
        accepted_disposition=c.with_id('disposition',dict(version='g51.disposition.v01',candidate_ref=candidate['import_id'],parent_ref=disposition['disposition_id'],state='ACCEPTED_CONTEXT',local_review_ref=local[2].decision_id))
        c.contract('disposition',accepted_disposition);immutable(folder/'disposition_accepted.json',accepted_disposition)
        # Recheck source, policy, status and exact immutable import at the actual use boundary.
        used_at=clock();checked=c.check_bundle(bundle,descriptor,fetch,status,policy,used_at,history,conflicts)
        adaptation=c.with_id('adaptation',dict(version='g51.adaptation.v01',import_ref=candidate['import_id'],foreign_source_ref=pointer['source_record_ref'],source_field='correction',
            value=checked['body']['correction'],input_names=['offset_den','offset_num'],work_request_ref='task:gate5:corrected',local_acceptance_ref=local[2].decision_id))
        c.contract('adaptation',adaptation);immutable(folder/'adaptation.json',adaptation)
        values=dict(readings=c.canonical(readings).decode(),offset_den=adaptation['value']['den'],offset_num=adaptation['value']['num'])
        work=n.native_work('corrected',c.ROOT_B,adaptation['work_request_ref'],values);n.save(folder/'corrected_work.json',work)
        out=work['outputs'];within=out['corrected_num']<=c.mul(scenario['limit'],out['corrected_den'])
        assessment='WITHIN_REFERENCE_LIMIT' if within else 'REVIEW_REQUIRED'
        final=n.root_review(c.ROOT_B,'transaction:gate5:result',work['artifact']['artifact_id'],candidate['import_id'],
            dict(actual_native=work['attempts']==1,local_policy_unchanged=candidate['policy_hash']==c.sha(policy)),
            dict(assessment=assessment,work_result_ref=work['artifact']['artifact_id'],adaptation_ref=adaptation['local_view_id'],outputs=out,limit=scenario['limit']),clock(),
            window=(pointer['time_envelope']['valid_from'],min(checked['source_end'],fetch['deadline'],status['value']['valid_until'])))
        c.require(final[2].decision=='ACCEPT','final_root_refused');n.save(folder/'final_review.json',n.root_plain(final))
        resolver.write_semantic_record(LocalDRS(folder/'result_drs'),resolver.SemanticDRSRecordInput(record_id='g5result:'+c.sha(out),domain='CALIBRATION_USE',
            content=dict(assessment=assessment,outputs=out,source_ref=pointer['source_record_ref'],adaptation_ref=adaptation['local_view_id']),semantic_keys=('calibrated','historical_result')))
        accepted=dict(assessment=assessment,outputs=out,use_time=used_at,source_end=checked['source_end'],request_ref=fetch['request_id'],native_work_seconds=work['seconds'])
    c.require(accepted is not None,'INSUFFICIENT_EVIDENCE')
    phase(folder,'exchange','COMPLETE',assessment=accepted['assessment'])
    n.save(folder/'result.json',dict(status='CALIBRATION_CONSUMED',accepted=accepted,budget=budget.read(),wire=channel.counters(),
        source_body_reads='ONLY_RECEIVED_IPC_BODY; NO_A_STATE_FILES',before=before['outputs']))


def peer(role,read_fd,write_fd,folder):
    folder=Path(folder);cap=c.crypto.generate_root_signer_capability_v01(root_id=c.ROOT_A if role=='A' else c.ROOT_B)
    keys=c.crypto.build_trusted_root_key_set_v01(capabilities=(cap,))
    print(json.dumps(dict(pid=os.getpid(),public_keys=c.crypto.trusted_root_key_set_to_plain_dict_v01(keys))),flush=True)
    bootstrap=json.loads(input());c.keyset(bootstrap['peer_keys'])
    expected={'contracts':c.__file__,'native':n.__file__,'exchange':__file__}
    c.require(set(bootstrap['source_pins'])==set(expected),'source_pin_inventory')
    for key,path in expected.items():c.require(hashlib.sha256(Path(path).read_bytes()).hexdigest()==bootstrap['source_pins'][key],'source_pin_mismatch')
    n.save(folder/'bootstrap.json',bootstrap)
    channel=PipeChannel(read_fd,write_fd,folder)
    try:
        (publisher if role=='A' else requester)(channel,cap,keys,bootstrap,folder)
    finally:
        n.save(folder/'final_wire_counters.json',channel.counters());os.close(read_fd);os.close(write_fd)
