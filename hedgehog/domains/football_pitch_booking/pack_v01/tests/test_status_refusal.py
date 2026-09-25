"""Reviewer-only signed STATUS/Root regressions; no author execution or P7 claim."""
import copy
import tempfile
import unittest
from pathlib import Path
from hedgehog.external_drs import gate5_contracts_v01 as c, gate5_exchange_v01 as x
from hedgehog.external_drs.gate5_lifecycle_v01 import ImportStore
from candidate_domain.domain import request_times
from candidate_domain.policy import consumer_policy
from candidate_domain.publication import build
from candidate_domain.profile import profile
from candidate_domain.run import requester_event, refuse_inactive_status, request
from candidate_domain.storage import read


def fixture():
    r=dict(request_id='request:own:status',revision=1,operation='FIND_OFFER',
        team_ref='team:own:status',venue_ref='venue:own:status',timezone='Europe/Tirane',
        currency='ALL',budget_minor=200,owner_approval_ref=None,sessions=[
            dict(session_id='session:'+name,start='2027-01-%02dT09:00'%(21+j),
                 end='2027-01-%02dT10:30'%(21+j),allow_shift_minutes=0)
            for j,name in enumerate(('east','west','north'))])
    intervals=[[a,b] for a,b,_ in request_times(r).values()]
    i=dict(revision=3,venue_ref=r['venue_ref'],currency=r['currency'],fields=[
        dict(field_id='field:own:status',surface='natural_grass',full_size=True,
             price_minor=19,available_utc=intervals,occupied_utc=[])])
    p=dict(local_root='root:own:status_reader',peer_root='root:own:status_source',
        publish_enabled=True,release_enabled=True,accept_football=True,
        recipients=['root:own:status_source'],status='ACTIVE',ttl_seconds=300,
        max_source_age=300,shift_approvals=[],book_approvals=[])
    return r,i,p


def signer(root):
    cap=c.crypto.generate_root_signer_capability_v01(root_id=root)
    keys=c.crypto.build_trusted_root_key_set_v01(capabilities=(cap,))
    return cap,keys,c.crypto.trusted_root_key_set_to_plain_dict_v01(keys)


def signed_status(cap,keys,pointer,fetch,state,now,revision=1):
    entry=dict(version='g51.entry.v01',pointer_id=pointer['pointer_id'],
        publisher_root_id=pointer['publisher_root_id'],stream_id=pointer['revocation_stream_id'],
        revision=revision,state=state,effective_at=now,reason_ref='reason:own:component_status')
    entry['entry_hash']=c.sha(entry); c.validate('entry',entry)
    value=dict(version='g51.status.v01',entry=entry,requested_pointer_hash=c.sha(pointer),
        requester=fetch['requester'],subject_request_ref=fetch['request_id'],
        request_revision=fetch['request_revision'],nonce=fetch['nonce'],
        checked_at=now,valid_until=now+60)
    c.validate('status',value)
    return c.sign(cap,keys,'STATUS',value,pointer['artifact_manifest_ref'].split(':')[1])


class StatusMessages:
    """In-memory component driver, not PipeChannel or independent peer telemetry.

    No framing/transport implementation or authority mock. Signed source metadata
    comes from actual native publication. This driver supplies only test STATUS
    and CLOSE replies with public signature primitives; it cannot supply a body.
    Production run_peer_v01 continues to require the operator's real PipeChannel.
    """
    def __init__(self,made,source_signer,requester_public,event_id,state,fault=None):
        self.made=made
        self.cap,self.keys,_=source_signer
        self.requester_public=requester_public
        self.event_id,self.state,self.fault=event_id,state,fault
        self.ops=[]; self.pending=None; self.received=0; self.last_status=None

    def send(self,kind,value):
        if kind!='REQUEST' or self.pending is not None:
            raise AssertionError('component_request_order')
        req=c.verify(value,self.requester_public,'REQUEST',value['value']['trust_profile_hash'])
        c.validate('request',req)
        self.ops.append(req['op']); self.pending=req

    def receive(self,allow_eof=False):
        req=self.pending; self.pending=None; self.received+=1
        if req['op']=='DESCRIBE':
            return dict(kind='POINTER',value=self.made['descriptor'])
        if req['op']=='STATUS':
            if self.fault=='unexpected':
                raise ValueError('own_component_unexpected_error')
            fetch=dict(req,request_id=req['subject_request_ref'])
            now=x.clock()-(60 if self.fault=='stale' else 0)
            value=signed_status(self.cap,self.keys,self.made['descriptor']['value'],
                                fetch,self.state,now)
            if self.fault=='tamper':
                value=copy.deepcopy(value)
                value['value']['entry']['reason_ref']='reason:own:changed_after_signing'
            self.last_status=value
            return dict(kind='STATUS',value=value)
        if req['op']=='CLOSE':
            value=dict(request_ref=req['request_id'],session=self.event_id)
            return dict(kind='CLOSED',value=c.sign(self.cap,self.keys,'CLOSE',value,req['trust_profile_hash']))
        raise AssertionError('terminal_status_must_stop_before_'+req['op'])

    def counters(self):
        # Component message counts only; no OS pipes or wire bytes are claimed.
        return dict(component_sent=len(self.ops),component_received=self.received)


class StatusRefusalTests(unittest.TestCase):
    def setup_case(self,base,terminal='REVOKED',feasible=True,fault=None):
        r,i,p=fixture()
        if not feasible:
            r['budget_minor']=0
        source=signer(p['peer_root']); local=signer(p['local_root'])
        source_policy=dict(p,local_root=p['peer_root'],peer_root=p['local_root'],
                           recipients=[p['local_root']],status=terminal)
        source_folder=base/'source_event'; source_folder.mkdir()
        made=build(r,i,source_policy,base/'source_state',source_folder,*source)
        folder=base/'requester_event'; folder.mkdir()
        event=dict(event_id='own_status',request=r)
        channel=StatusMessages(made,source,local[2],event['event_id'],terminal,fault)
        return r,p,event,made,folder,channel,source,local

    def test_actual_requester_refusal_links_terminal_evidence_and_local_root(self):
        for terminal,feasible in (('REVOKED',True),('SUPERSEDED',False)):
            with self.subTest(terminal=terminal), tempfile.TemporaryDirectory() as directory:
                base=Path(directory)
                r,p,event,made,folder,channel,source,local=self.setup_case(base,terminal,feasible)
                original=copy.deepcopy(made)
                result=requester_event(event,p,base/'requester_state',folder,channel,
                                       local[0],local[1],source[2])
                self.assertEqual(result['status'],'REFUSED')
                self.assertEqual(result['slots'],[])
                self.assertEqual(result['total_minor'],0)
                self.assertIsNone(result['receipt_ref'])
                self.assertEqual(result['counts'],dict(search=1,dispatch=0,mutations=0,observed=0))
                self.assertEqual(channel.ops,['DESCRIBE','STATUS','CLOSE'])
                refusal=read(folder/'refusal.json')
                live_record=read(folder/'refusal_review.json')
                evidence=read(folder/'status_refusal_evidence.json')
                self.assertEqual(live_record['result']['decision'],'BLOCKED_FAIL_CLOSED')
                self.assertEqual(live_record['result']['target_root_id'],p['local_root'])
                self.assertFalse(live_record['result']['permission_created'])
                self.assertFalse(live_record['result']['effect_requested'])
                self.assertEqual(refusal['review_ref'],live_record['result']['decision_id'])
                self.assertEqual(refusal['reason'],'status_not_active')
                self.assertEqual(refusal['evidence_sha256'],c.sha(evidence))
                claim=live_record['inputs']['root_review_packet']['synthesis_proposal']['normalized_claims'][0]
                self.assertEqual(claim['predicate'],'football_current_source_status_v01')
                self.assertEqual(claim['subject'],r['request_id'])
                self.assertEqual(claim['object_or_value']['request'],r)
                self.assertEqual(claim['object_or_value']['request_sha256'],c.sha(r))
                self.assertEqual(claim['object_or_value']['reason'],refusal['reason'])
                self.assertEqual(claim['object_or_value']['evidence_sha256'],c.sha(evidence))
                self.assertEqual(claim['object_or_value']['status_entry'],channel.last_status['value']['entry'])
                self.assertEqual(evidence['descriptor'],made['descriptor'])
                self.assertEqual(evidence['status'],channel.last_status)
                self.assertEqual(read(folder/'status.json'),channel.last_status)
                self.assertEqual(result['native_refs']['refusal_review'],'refusal_review.json')
                self.assertEqual(result['native_refs']['status_refusal_evidence'],'status_refusal_evidence.json')
                self.assertEqual(read(folder/'descent_review.json')['result']['decision'],'ACCEPT')
                self.assertNotEqual(live_record['result']['decision_id'],
                                    read(folder/'descent_review.json')['result']['decision_id'])
                for name in ('requester_work.json','native_attempt_requester.json','offer_body.json',
                             'import_candidate.json','action_packet.json','receipt.json','host_outcome.json'):
                    self.assertFalse((folder/name).exists(),name)
                self.assertEqual(made,original)
                self.check_restart_and_continuation(base,r,p,evidence,source)

    def check_restart_and_continuation(self,base,r,p,evidence,source):
        store=ImportStore(base/'requester_state'/'imports')
        highwater=read(store.path)['highwater']
        pointer=evidence['descriptor']['value']; fetch=evidence['fetch_request']
        policy=evidence['policy']; t=evidence['observed_at']
        key,entry=c.authenticate_status(evidence['status'],pointer,fetch,policy,t,highwater)
        self.assertEqual(highwater[key],entry)
        with self.assertRaisesRegex(ValueError,'^status_not_active$'):
            c.check_status(evidence['status'],pointer,fetch,policy,t,highwater)
        revival=signed_status(source[0],source[1],pointer,fetch,'ACTIVE',x.clock(),entry['revision']+1)
        with self.assertRaisesRegex(ValueError,'^status_terminal_revival$'):
            store.observe(revival,pointer,fetch,policy,x.clock())
        self.assertEqual(read(store.path)['highwater'][key],entry)

        # An independently identified pointer's authentic ACTIVE observation is lawful;
        # it neither resets the old stream nor grants body/action permission.
        other=c.with_id('pointer',dict(pointer,revocation_stream_id='stream:own:independent_status'))
        descriptor=c.sign(source[0],source[1],'POINTER',other,other['artifact_manifest_ref'].split(':')[1])
        c.check_pointer(descriptor,policy,x.clock(),profile=profile())
        new_fetch=request(p,r,'FETCH',policy,other)
        active=signed_status(source[0],source[1],other,new_fetch,'ACTIVE',x.clock())
        store.observe(active,other,new_fetch,policy,x.clock())
        new_key,new_entry=c.check_status(active,other,new_fetch,policy,x.clock(),read(store.path)['highwater'])
        self.assertNotEqual(new_key,key)
        self.assertEqual(new_entry['state'],'ACTIVE')
        self.assertEqual(read(store.path)['highwater'][key],entry)

    def test_invalid_signature_and_unknown_error_stay_visible(self):
        for fault,reason in (('tamper','signed_content_binding'),('unexpected','own_component_unexpected_error')):
            with self.subTest(fault=fault), tempfile.TemporaryDirectory() as directory:
                base=Path(directory)
                r,p,event,made,folder,channel,source,local=self.setup_case(base,fault=fault)
                with self.assertRaisesRegex(ValueError,'^'+reason+'$'):
                    requester_event(event,p,base/'requester_state',folder,channel,local[0],local[1],source[2])
                for name in ('report.json','refusal_review.json','status_refusal_evidence.json'):
                    self.assertFalse((folder/name).exists(),name)

    def test_stale_status_is_unknown_not_authenticated_terminal_refusal(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory)
            r,p,event,made,folder,channel,source,local=self.setup_case(base,fault='stale')
            result=requester_event(event,p,base/'requester_state',folder,channel,local[0],local[1],source[2])
            self.assertEqual(result['status'],'CURRENT_STATUS_UNKNOWN')
            self.assertEqual(read(folder/'refusal.json')['reason'],'status_not_current')
            self.assertFalse((folder/'status_refusal_evidence.json').exists())
            self.assertFalse((folder/'refusal_review.json').exists())
            self.assertNotIn('FETCH',channel.ops)

    def test_confirmation_refusal_does_not_certify_source_zero_effects(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory)
            r,p,event,made,folder,channel,source,local=self.setup_case(base)
            # Isolate reporting of an authenticated refusal during a confirmation.
            # No source effect is run or claimed by this component.
            confirm=dict(r,operation='CONFIRM_MOCK_BOOKING',owner_approval_ref='approval:own:component')
            policy=consumer_policy(p,source[2],r,r)
            pointer=made['descriptor']['value']; fetch=request(p,confirm,'FETCH',policy,pointer)
            status_req=request(p,confirm,'STATUS',policy,pointer,fetch['request_id'],fetch['nonce'])
            now=x.clock(); status=signed_status(source[0],source[1],pointer,fetch,'REVOKED',now)
            store=ImportStore(base/'requester_state'/'imports')
            store.observe(status,pointer,fetch,policy,now)
            material=dict(descriptor=made['descriptor'],fetch_request=fetch,status_request=status_req,
                          status=status,highwater=read(store.path)['highwater'],pointer_checked_at=now,
                          authenticated_at=now,observed_at=now)
            result=refuse_inactive_status(confirm,policy,material,folder)
            self.assertEqual(result['status'],'CURRENT_STATUS_UNKNOWN')
            self.assertEqual(read(folder/'refusal_review.json')['result']['decision'],'BLOCKED_FAIL_CLOSED')
            self.assertEqual(read(folder/'refusal.json')['status'],'CURRENT_STATUS_UNKNOWN')
            self.assertIsNone(result['receipt_ref'])
