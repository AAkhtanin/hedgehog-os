"""Finite G52 lifecycle over the G51 public-native adapters and inherited pipes."""
import json
import os
from pathlib import Path
import secrets
import time
from hedgehog.drs import LocalDRS
from hedgehog import local_drs_resolver as resolver
from . import gate5_contracts_v01 as c, gate5_exchange_v01 as e, gate5_native_v01 as n

BASELINE='task:gate5:exchange'
SCOPE='task:gate5:scope-refusal'
REVISION_TWO='task:gate5:revision-two'


def read(path): return json.loads(Path(path).read_text())


def contexts():
    return {task:dict(requester=c.ROOT_B,object_id='object:gate5:calibration:one',
        purpose=purpose,source_revision=2 if task==REVISION_TWO else 1,uses=['AUDIT'] if task==SCOPE else ['LOCAL_CONTEXT'],
        owner_epoch='g52.declared.before.execution') for task,purpose in
        [(BASELINE,'REVISION_ONE_AND_RESTART'),(SCOPE,'ISOLATED_AUDIT_REFUSAL'),(REVISION_TWO,'REVISION_TWO')]}


class ImportStore:
    def __init__(self,folder):
        self.folder=Path(folder);self.path=self.folder/'import_state.json'
        if not self.path.exists(): e.state_write(self.path,dict(highwater={},sources={},duplicates=[],quarantine=[],credit=0))

    def observe(self,envelope,pointer,request,policy,now):
        state=read(self.path)
        try:key,entry=c.authenticate_status(envelope,pointer,request,policy,now,state['highwater'])
        except ValueError as exc:
            state['quarantine'].append(dict(kind='STATUS',reason=str(exc),envelope=envelope,request=request))
            e.state_write(self.path,state);raise
        state['highwater'][key]=entry
        e.state_write(self.path,state)
        return entry

    def conflicts(self):
        return {k:v['body_hash'] for k,v in read(self.path)['sources'].items()}

    def validate_bundle(self,bundle,descriptor,request,status,policy,now):
        try:return c.check_bundle(bundle,descriptor,request,status,policy,now,read(self.path)['highwater'],self.conflicts())
        except ValueError as exc:
            if str(exc)=='source_equivocation':self.quarantine(str(exc),dict(bundle=bundle,descriptor=descriptor,request=request,status=status))
            raise

    def import_body(self,checked,pointer):
        state=read(self.path);key=checked['conflict_key'];body=checked['body'];digest=c.sha(body)
        if key in state['sources']:
            c.require(state['sources'][key]['body_hash']==digest,'source_equivocation')
            state['duplicates'].append(dict(key=key,body_hash=digest,pointer=pointer['pointer_id']))
            e.state_write(self.path,state);return 'DUPLICATE'
        c.require(len(state['sources'])<8,'record_bound')
        state['sources'][key]=dict(body_hash=digest,source_ref=body['source_record_ref'],revision=body['source_revision'],pointer=pointer['pointer_id'])
        e.state_write(self.path,state);return 'NEW_SOURCE'

    def quarantine(self,reason,value):
        state=read(self.path);state['quarantine'].append(dict(kind='IMPORT',reason=reason,value=value));e.state_write(self.path,state)


def make_request(policy,op,task,pointer=None,use='LOCAL_CONTEXT',subject=None,nonce=None):
    return c.with_id('request',dict(e.request(policy,op,pointer,use,subject,nonce),task_ref=task))


def publisher_service(channel,cap,keys,bootstrap,sources,folder,session):
    policy=bootstrap['own_policy'];request_policy=bootstrap['requester_policy']
    status_counts=read(folder/'status_counts.json') if (folder/'status_counts.json').exists() else {}
    for _ in range(32):
        message=channel.receive(allow_eof=True)
        if message is None:return
        c.require(message['kind']=='REQUEST','expected_request')
        req=c.verify(message['value'],bootstrap['peer_keys'],'REQUEST',c.sha(request_policy));c.validate('request',req)
        c.require(req['requester']==c.ROOT_B and req['publisher']==c.ROOT_A and req['issued_at']<=e.clock()<req['deadline'],'source_request_identity_or_time')
        c.require(req['trust_profile_hash']==c.sha(request_policy) and req['owner_transport_scope']==request_policy['transport_scope'],'source_request_policy')
        budget=e.PublisherBudget(folder/'publisher_budget.json',bootstrap['contexts'])
        reserved=budget.reserve(req)
        if req['op']=='CLOSE':
            c.require(reserved,'publisher_attempt_budget')
            channel.send('CLOSED',c.sign(cap,keys,'CLOSE',dict(request_ref=req['request_id'],session=session),c.sha(request_policy)))
            return
        if req['op']=='DESCRIBE':
            c.require(reserved,'publisher_attempt_budget')
            c.require(budget.matches_source(req,sources[max(sources)]['body']['source_revision']),'publisher_descriptor_task_revision')
            channel.send('POINTER',sources[max(sources)]['descriptor']);continue
        match=[s for s in sources.values() if s['descriptor']['value']['pointer_id']==req['pointer_ref']]
        c.require(len(match)==1,'publisher_pointer_lookup');source=match[0]
        body,manifest,descriptor,entry=(source[k] for k in ('body','manifest','descriptor','entry'))
        pointer=descriptor['value'];manifest_hash=manifest['manifest_id'].split(':')[1]
        if req['op']=='STATUS':
            c.require(reserved,'publisher_attempt_budget')
            count=status_counts.get(req['task_ref'],0)+1;status_counts[req['task_ref']]=count;e.state_write(folder/'status_counts.json',status_counts)
            # Declared source-side lifecycle observations, not caller-selected status.
            if req['task_ref']==BASELINE and count==3:
                value=dict(request_ref=req['request_id'],nonce=req['nonce'],reason='CURRENT_STATUS_UNKNOWN')
                channel.send('UNAVAILABLE',c.sign(cap,keys,'STATUS_UNAVAILABLE',value,manifest_hash));continue
            if req['task_ref']==BASELINE and count>=5 and entry['state']=='ACTIVE':
                entry=dict(entry,revision=2,state='REVOKED',effective_at=e.clock(),reason_ref='reason:gate5:declared-revocation')
                entry['entry_hash']=c.sha({k:v for k,v in entry.items() if k!='entry_hash'});c.validate('entry',entry)
                source['entry']=entry;e.immutable(folder/'revoked_entry.json',entry)
            now=e.clock();value=dict(version='g51.status.v01',entry=entry,requested_pointer_hash=c.sha(pointer),requester=req['requester'],
                subject_request_ref=req['subject_request_ref'],request_revision=req['request_revision'],nonce=req['nonce'],checked_at=now,valid_until=now+60)
            c.contract('status',value);channel.send('STATUS',c.sign(cap,keys,'STATUS',value,manifest_hash));continue
        checks=dict(authenticated_request=True,source_attempt_reserved=reserved,task_source_revision=budget.matches_source(req,body['source_revision']),allowed_use=req['use_class'] in policy['release_uses'],
            audience=req['requester'] in policy['recipients'],current=entry['state']=='ACTIVE',size=pointer['body_bytes']<=req['allowed_size'])
        review=n.root_review(c.ROOT_A,'transaction:g52:release',req['request_id'],pointer['pointer_id'],checks,
            dict(request=req,pointer_ref=pointer['pointer_id'],body_hash=c.sha(body)),e.clock(),
            window=(body['time_envelope']['valid_from'],min(c.temporal(body['time_envelope'],e.clock(),policy),req['deadline'])))
        allowed=review[2].decision=='ACCEPT'
        # This durable write must precede construction/sending of a permitted body.
        if allowed:budget.disclosure(req,len(c.canonical(body)))
        before=channel.counters()
        release=dict(version='g51.release.v01',state='RELEASED' if allowed else 'REFUSED',request_ref=req['request_id'],request_revision=req['request_revision'],
            pointer_ref=pointer['pointer_id'],manifest_ref=manifest['manifest_id'],body_hash=c.sha(body),recipient=req['requester'],use_class=req['use_class'],
            nonce=req['nonce'],deadline=req['deadline'],release_review_ref=review[2].decision_id)
        value=dict(release=c.sign(cap,keys,'RELEASE',release,manifest_hash),manifest=manifest if allowed else None,body=body if allowed else None)
        budget.response(req,allowed)
        channel.send('BUNDLE',value)
        e.immutable(folder/'releases'/(req['request_id']+'.json'),dict(request=req,review=n.root_plain(review),response=value,
            reserved=reserved,budget_after=budget.read(),wire_before=before,wire_after=channel.counters(),session=session))
    raise ValueError('publisher_finite_session_limit')


def publisher(read_fd,write_fd,folder):
    folder=Path(folder);private=folder/'private';private.mkdir();(private/'canary.txt').write_text(secrets.token_hex(32))
    cap=c.crypto.generate_root_signer_capability_v01(root_id=c.ROOT_A);keys=c.crypto.build_trusted_root_key_set_v01(capabilities=(cap,))
    print(json.dumps(c.crypto.trusted_root_key_set_to_plain_dict_v01(keys)),flush=True)
    sources={};previous=[];scenario=read(folder/'scenario.json')
    try:
        for session,inputs in enumerate(scenario['revisions'],1):
            bootstrap=json.loads(input());c.require(bootstrap['contexts']==contexts(),'operator_contexts')
            n.save(folder/('bootstrap_%d.json'%session),bootstrap)
            source_folder=folder/('r%d'%session);source_folder.mkdir()
            body,manifest,descriptor,entry=e.build_source(dict(inputs,predecessor_work_refs=previous),cap,keys,bootstrap['own_policy'],source_folder)
            sources[session]=dict(body=body,manifest=manifest,descriptor=descriptor,entry=entry);previous=[body['source_work_ref']]
            transport_folder=folder/('session%d'%session);transport_folder.mkdir()
            channel=e.PipeChannel(read_fd,write_fd,transport_folder)
            print('READY:'+str(session),flush=True)
            try:publisher_service(channel,cap,keys,bootstrap,sources,folder,session)
            finally:n.save(transport_folder/'wire_counters.json',channel.counters())
            print('DONE:'+str(session),flush=True)
    finally:os.close(read_fd);os.close(write_fd)


class Requester:
    def __init__(self,folder,session,channel,cap,keys,bootstrap):
        self.folder,self.session,self.channel=Path(folder),session,channel
        self.cap,self.keys,self.policy=cap,keys,bootstrap['own_policy']
        c.require(bootstrap['contexts']==contexts(),'requester_operator_contexts')
        self.contexts=bootstrap['contexts']
        e.immutable(self.folder/'task_contexts.json',self.contexts)
        self.scenario=read(self.folder/'scenario.json');self.store=ImportStore(self.folder)
        self.events=[]

    def io(self,req,bypass_budget=False):
        policy=self.policy
        c.require(req['task_ref'] in self.contexts,'requester_unknown_task_context')
        c.require(req['use_class'] in self.contexts[req['task_ref']]['uses'],'requester_context_use')
        review=n.root_review(c.ROOT_B,'transaction:g52:request',req['request_id'],req['object_id'],
            dict(endpoint=policy['endpoint']=='endpoint:gate5:A',scope=req['use_class'] in policy['uses']),req,e.clock(),window=(req['issued_at'],req['deadline']))
        c.require(review[2].decision=='ACCEPT','retrieval_refused')
        e.immutable(self.folder/'requests'/(req['request_id']+'.json'),dict(request=req,review=n.root_plain(review),session=self.session,
            bypass='DECLARED_MALICIOUS_REQUESTER_BUDGET_CONTROL' if bypass_budget else None))
        if not bypass_budget:e.Budget(self.folder/'budgets'/(req['task_ref']+'.json'),req['task_ref']).reserve(req)
        self.channel.send('REQUEST',c.sign(self.cap,self.keys,'REQUEST',req,c.sha(policy)))
        response=self.channel.receive()
        self.events.append(dict(request=req,response=response,wire=self.channel.counters()))
        return response

    def status(self,descriptor,task):
        pointer=descriptor['value'];c.check_route(pointer,self.policy)
        fetch=make_request(self.policy,'FETCH',task,pointer)
        req=make_request(self.policy,'STATUS',task,pointer,subject=fetch['request_id'],nonce=fetch['nonce'])
        response=self.io(req)
        if response['kind']=='UNAVAILABLE':
            value=c.verify(response['value'],self.policy['peer_keys'],'STATUS_UNAVAILABLE',pointer['artifact_manifest_ref'].split(':')[1])
            c.require(value==dict(request_ref=req['request_id'],nonce=req['nonce'],reason='CURRENT_STATUS_UNKNOWN'),'unavailable_binding')
            return fetch,None
        c.require(response['kind']=='STATUS','expected_status')
        entry=self.store.observe(response['value'],pointer,fetch,self.policy,e.clock())
        return fetch,response['value']

    def descriptor(self,task):
        response=self.io(make_request(self.policy,'DESCRIBE',task));c.require(response['kind']=='POINTER','expected_pointer')
        descriptor=response['value'];pointer=c.check_pointer(descriptor,self.policy,e.clock())
        drs=LocalDRS(self.folder/'address_index')
        resolver.write_semantic_record(drs,resolver.SemanticDRSRecordInput(record_id=pointer['pointer_id'],domain='G52_POINTER',
            content=dict(kind='pointer',revision=pointer['source_revision'],descriptor=descriptor),semantic_keys=('calibration','pointer')))
        return self.resolve_pointer(pointer['source_revision'])

    def resolve_pointer(self,revision):
        drs=LocalDRS(self.folder/'address_index')
        result=resolver.resolve_semantic_candidates(drs,resolver.SemanticResolveQuery(query_id='query:g52:pointer:'+str(revision),
            domain='G52_POINTER',semantic_terms=('calibration','pointer'),content_filters=dict(revision=revision),require_root_review=True),layers=('work',))
        c.require(len(result.candidates)==1,'persisted_pointer_lookup')
        descriptor=drs.read_record('work',result.candidates[0].record_id)['content']['descriptor'];pointer=descriptor['value']
        c.check_pointer(descriptor,self.policy,e.clock())
        metadata=dict(publisher=pointer['publisher_root_id'],source_record=pointer['source_record_ref'],revision=revision,
            pointer_id=pointer['pointer_id'],body_sha256=pointer['body_sha256'],schema=c.BODY_SCHEMA,endpoint_ref=self.policy['endpoint'])
        directory=self.folder/('lookup_s%d_r%d'%(self.session,revision))
        proof=n.pointer_descent_v01(metadata,directory,c.temporal(pointer['time_envelope'],e.clock(),self.policy))
        n.save(directory/'resolution.json',dict(result=n.plain(result),descriptor_hash=c.sha(descriptor),root=proof['root'],
            process_id=os.getpid(),session=self.session))
        return descriptor

    def fetch(self,descriptor,req,status):
        c.require(status is not None,'CURRENT_STATUS_UNKNOWN')
        c.check_status(status,descriptor['value'],req,self.policy,e.clock(),read(self.store.path)['highwater'])
        response=self.io(req);c.require(response['kind']=='BUNDLE','expected_bundle')
        bundle=response['value']
        checked=self.store.validate_bundle(bundle,descriptor,req,status,self.policy,e.clock())
        e.Budget(self.folder/'budgets'/(req['task_ref']+'.json'),req['task_ref']).received_body(len(c.canonical(bundle['body'])))
        e.immutable(self.folder/'quarantine/bodies'/(c.sha(bundle['body'])+'.json'),bundle['body'])
        e.immutable(self.folder/'quarantine/receipts'/(req['request_id']+'.json'),bundle)
        disposition=self.store.import_body(checked,descriptor['value'])
        return bundle,checked,disposition

    def consume(self,descriptor,req,status,bundle,checked,target):
        target=Path(target);target.mkdir(parents=True,exist_ok=True)
        scenario,policy=self.scenario,self.policy;body=checked['body'];pointer=descriptor['value']
        dependency=c.sha(dict(readings=scenario['readings'],limit=scenario['limit'],policy=c.sha(policy),source=c.sha(body)))
        candidate=c.with_id('import',dict(version='g51.import.v01',local_request_ref=req['request_id'],pointer_ref=pointer['pointer_id'],
            foreign_publisher=pointer['publisher_root_id'],foreign_source_ref=body['source_record_ref'],foreign_revision=body['source_revision'],
            received_manifest_hash=c.sha(bundle['manifest']),body_hash=c.sha(body),receive_event_ref='receive:'+c.sha(bundle),
            validation_results={k:True for k in ('shape','signature','integrity','arithmetic','provenance','temporal','scope','status','conflict','local_policy')},
            status_entry_hash=checked['status_entry']['entry_hash'],dependency_fingerprint=dependency,policy_hash=c.sha(policy),creates_permission=False))
        c.contract('import',candidate)
        review=n.root_review(c.ROOT_B,'transaction:g52:import',candidate['import_id'],body['source_record_ref'],
            dict(components_checked=True,local_policy=policy['accept_calibration']),candidate,e.clock(),
            window=(body['time_envelope']['valid_from'],min(checked['source_end'],req['deadline'],status['value']['valid_until'])))
        c.require(review[2].decision=='ACCEPT','import_refused')
        record=dict(descriptor=descriptor,request=req,status=status,bundle=bundle,candidate=candidate,review=n.root_plain(review),scenario=scenario,policy=policy)
        e.immutable(target/'import.json',record)
        return record

    def use(self,record,target,policy=None,scenario=None):
        target=Path(target);policy=self.policy if policy is None else policy;scenario=self.scenario if scenario is None else scenario
        body=record['bundle']['body'];candidate=record['candidate'];req=record['request']
        dependency=c.sha(dict(readings=scenario['readings'],limit=scenario['limit'],policy=c.sha(policy),source=c.sha(body)))
        context_ok=dependency==candidate['dependency_fingerprint'] and c.sha(policy)==candidate['policy_hash']
        current=n.root_review(c.ROOT_B,'transaction:g52:current',candidate['import_id'],body['source_record_ref'],
            dict(current_context=context_ok),dict(dependency=dependency,policy=c.sha(policy),import_ref=candidate['import_id']),e.clock())
        n.save(target/'current_review.json',n.root_plain(current));c.require(current[2].decision=='ACCEPT','current_context_changed')
        checked=c.check_bundle(record['bundle'],record['descriptor'],req,record['status'],policy,e.clock(),read(self.store.path)['highwater'],self.store.conflicts())
        adaptation=c.with_id('adaptation',dict(version='g51.adaptation.v01',import_ref=candidate['import_id'],foreign_source_ref=body['source_record_ref'],
            source_field='correction',value=checked['body']['correction'],input_names=['offset_den','offset_num'],work_request_ref='task:g52:corrected:'+str(body['source_revision']),
            local_acceptance_ref=record['review']['result']['decision_id']))
        c.contract('adaptation',adaptation)
        values=dict(readings=c.canonical(scenario['readings']).decode(),offset_num=adaptation['value']['num'],offset_den=adaptation['value']['den'])
        work=n.native_work('corrected',c.ROOT_B,adaptation['work_request_ref'],values);out=work['outputs']
        assessment='WITHIN_REFERENCE_LIMIT' if out['corrected_num']<=c.mul(scenario['limit'],out['corrected_den']) else 'REVIEW_REQUIRED'
        claim=dict(assessment=assessment,work_result_ref=work['artifact']['artifact_id'],adaptation_ref=adaptation['local_view_id'],outputs=out,
            limit=scenario['limit'],source_revision=body['source_revision'],source_ref=body['source_record_ref'],body_hash=c.sha(body),
            dependency_fingerprint=dependency,policy_hash=c.sha(policy),local_request_ref=req['request_id'])
        final=n.root_review(c.ROOT_B,'transaction:g52:result',work['artifact']['artifact_id'],candidate['import_id'],
            dict(actual_native=work['attempts']==1,current_context=context_ok),claim,e.clock(),
            window=(body['time_envelope']['valid_from'],min(checked['source_end'],req['deadline'],record['status']['value']['valid_until'])))
        c.require(final[2].decision=='ACCEPT','final_review_refused')
        result=dict(import_record=record,adaptation=adaptation,work=work,final_review=n.root_plain(final),claim=claim,use_time=e.clock())
        e.immutable(target/'accepted.json',result)
        resolver.write_semantic_record(LocalDRS(self.folder/'history'),resolver.SemanticDRSRecordInput(record_id=work['artifact']['artifact_id'],domain='G52_HISTORY',
            content=dict(revision=body['source_revision'],result=result),semantic_keys=('calibration','result')))
        return result

    def history(self,label):
        before=self.channel.counters();drs=LocalDRS(self.folder/'history')
        found=resolver.resolve_semantic_candidates(drs,resolver.SemanticResolveQuery(query_id='query:g52:history:'+label,domain='G52_HISTORY',
            semantic_terms=('calibration','result'),require_root_review=True),layers=('work',))
        values=[drs.read_record('work',x.record_id)['content']['result'] for x in found.candidates]
        c.require(bool(values),'history_missing')
        review=n.root_review(c.ROOT_B,'transaction:g52:history','history:'+c.sha(values),'history:g52',dict(local_history=True),
            dict(mode='HISTORICAL_NOT_CURRENT_PERMISSION',record_ids=[x.record_id for x in found.candidates],result_hashes=[c.sha(x) for x in values]),e.clock())
        result=dict(mode='HISTORICAL_NOT_CURRENT_PERMISSION',resolver=n.plain(found),results=values,review=n.root_plain(review),
            wire_before=before,wire_after=self.channel.counters(),process_id=os.getpid(),session=self.session)
        e.immutable(self.folder/('history_'+label+'.json'),result);return result

    def refusal(self,name,pointer,reason):
        result=n.root_review(c.ROOT_B,'transaction:g52:refusal','refusal:'+name,pointer['pointer_id'],dict(current_evidence=False),
            dict(reason=reason,pointer=pointer['pointer_id']),e.clock())
        e.immutable(self.folder/(name+'.json'),dict(reason=reason,review=n.root_plain(result),wire=self.channel.counters()))

    def run(self):
        if self.session==1:
            mean=n.native_work('mean',c.ROOT_B,'task:g52:uncalibrated',dict(readings=c.canonical(self.scenario['readings']).decode()))
            missing=n.root_review(c.ROOT_B,'transaction:g52:missing','candidate:g52:missing','source:gate5:calibration:one',dict(eligible_calibration=False),
                dict(status='INSUFFICIENT_EVIDENCE',mean=mean['outputs']),e.clock())
            n.save(self.folder/'uncalibrated.json',dict(work=mean,status='INSUFFICIENT_EVIDENCE',root=n.root_plain(missing)))
            descriptor=self.descriptor(BASELINE);p=descriptor['value']
            before_denial=self.channel.counters();negative=dict(self.policy,accept_calibration=False)
            denial=n.root_review(c.ROOT_B,'transaction:g52:local-negative','candidate:g52:local-negative',p['pointer_id'],
                dict(local_policy=negative['accept_calibration']),dict(policy=negative,pointer_ref=p['pointer_id']),e.clock())
            c.require(denial[2].decision!='ACCEPT','local_negative_accepted')
            e.immutable(self.folder/'local_policy_refusal.json',dict(policy=negative,review=n.root_plain(denial)))
            e.immutable(self.folder/'local_denial_counters.json',dict(before=before_denial,after=self.channel.counters()))
            n.save(self.folder/'before_body.json',dict(wire=self.channel.counters(),budget=e.Budget(self.folder/'budgets'/(BASELINE+'.json'),BASELINE).read(),
                address_files=[str(x.relative_to(self.folder)) for x in (self.folder/'address_index').rglob('*.json')],
                index_records=LocalDRS(self.folder/'address_index').read_layer('work'),quarantine_files=[str(x) for x in (self.folder/'quarantine').glob('**/*.json')]))
            denied=make_request(self.policy,'FETCH',SCOPE,p,use='AUDIT');response=self.io(denied)
            value=c.verify(response['value']['release'],self.policy['peer_keys'],'RELEASE',p['artifact_manifest_ref'].split(':')[1])
            c.require(value['state']=='REFUSED' and response['value']['body'] is None,'A_scope_refusal')
            req,status=self.status(descriptor,BASELINE);bundle,checked,kind=self.fetch(descriptor,req,status)
            c.require(kind=='NEW_SOURCE','baseline_new_source')
            record=self.consume(descriptor,req,status,bundle,checked,self.folder/'r1');self.use(record,self.folder/'r1')
            self.history('before_restart')
            req2,status2=self.status(descriptor,BASELINE);again,checked2,kind=self.fetch(descriptor,req2,status2)
            c.require(kind=='DUPLICATE' and c.sha(again['body'])==c.sha(bundle['body']),'dedup')
            n.save(self.folder/'dedup.json',dict(state=read(self.store.path),history_records=len(LocalDRS(self.folder/'history').read_layer('work')),
                request=req2,status=status2,bundle=again))
            for i in (1,2):
                hostile=make_request(self.policy,'FETCH',BASELINE,p)
                before=self.channel.counters();r=self.io(hostile,bypass_budget=True)
                release=c.verify(r['value']['release'],self.policy['peer_keys'],'RELEASE',p['artifact_manifest_ref'].split(':')[1])
                c.require(release['state']=='REFUSED' and r['value']['body'] is None and r['value']['manifest'] is None,'publisher_budget_disclosure')
                n.save(self.folder/('publisher_budget_control_%d.json'%i),dict(request=hostile,response=r,wire_before=before,wire_after=self.channel.counters()))
            q,unknown=self.status(descriptor,BASELINE);c.require(unknown is None,'unavailable_expected');self.refusal('status_unavailable',p,'CURRENT_STATUS_UNKNOWN')
            q,active=self.status(descriptor,BASELINE);c.check_status(active,p,q,self.policy,e.clock(),read(self.store.path)['highwater'])
            q,terminal=self.status(descriptor,BASELINE)
            c.require(terminal['value']['entry']['state']=='REVOKED','terminal_expected')
            try:c.check_status(terminal,p,q,self.policy,e.clock(),read(self.store.path)['highwater'])
            except ValueError as exc:c.require(str(exc)=='status_not_active','terminal_reason');self.refusal('revoked_current_use',p,str(exc))
            else:raise AssertionError('terminal_accepted')
            e.immutable(self.folder/'terminal_observation.json',dict(request=q,status=terminal,state=read(self.store.path)))
            close_task=BASELINE
        else:
            old=self.resolve_pointer(1);self.history('after_restart')
            prior=read(self.folder/'r1/import.json');snapshot=read(self.store.path)
            try:self.store.observe(prior['status'],old['value'],prior['request'],self.policy,e.clock())
            except ValueError as exc:c.require(str(exc)=='status_rollback','restart_rollback_reason');self.refusal('restart_old_active',old['value'],str(exc))
            else:raise AssertionError('restart_revocation_lost')
            c.require(read(self.store.path)['highwater']==snapshot['highwater'],'terminal_state_changed')
            q,terminal=self.status(old,BASELINE);c.require(terminal['value']['entry']['state']=='REVOKED','source_terminal_lost')
            descriptor=self.descriptor(REVISION_TWO);p=descriptor['value']
            req,status=self.status(descriptor,REVISION_TWO);bundle,checked,kind=self.fetch(descriptor,req,status)
            c.require(kind=='NEW_SOURCE' and prior['bundle']['body']['source_work_ref'] in bundle['body']['source_lineage_refs'],'revision_lineage')
            record=self.consume(descriptor,req,status,bundle,checked,self.folder/'r2')
            changed=dict(self.policy,policy_version='gate5.importer.changed-control.v01')
            try:self.use(record,self.folder/'changed_policy',policy=changed)
            except ValueError as exc:c.require(str(exc)=='current_context_changed','policy_change_reason')
            else:raise AssertionError('policy_change_accepted')
            changed_scenario=dict(self.scenario,readings=[100,100,100])
            try:self.use(record,self.folder/'changed_dependency',scenario=changed_scenario)
            except ValueError as exc:c.require(str(exc)=='current_context_changed','dependency_change_reason')
            else:raise AssertionError('dependency_change_accepted')
            self.use(record,self.folder/'r2');self.history('final')
            close_task=REVISION_TWO
        req=make_request(self.policy,'CLOSE',close_task);response=self.io(req)
        c.require(response['kind']=='CLOSED','close_response')
        value=c.verify(response['value'],self.policy['peer_keys'],'CLOSE',c.sha(self.policy))
        c.require(value==dict(request_ref=req['request_id'],session=self.session),'close_binding')


def requester(read_fd,write_fd,folder,session):
    folder=Path(folder);cap=c.crypto.generate_root_signer_capability_v01(root_id=c.ROOT_B);keys=c.crypto.build_trusted_root_key_set_v01(capabilities=(cap,))
    print(json.dumps(c.crypto.trusted_root_key_set_to_plain_dict_v01(keys)),flush=True)
    bootstrap=json.loads(input());n.save(folder/('bootstrap_%d.json'%session),bootstrap)
    transport=folder/('session%d'%session);transport.mkdir();channel=e.PipeChannel(read_fd,write_fd,transport)
    runtime=Requester(folder,session,channel,cap,keys,bootstrap)
    try:runtime.run()
    finally:
        n.save(transport/'events.json',runtime.events);n.save(transport/'wire_counters.json',channel.counters())
        os.close(read_fd);os.close(write_fd)
