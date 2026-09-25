"""Reviewer-only component regressions; no author execution or peer-success claim."""
import copy
import tempfile
import unittest
from pathlib import Path
from hedgehog.drs import LocalDRS
from hedgehog import drs_semantic_address_v01 as address
from hedgehog.external_drs import gate5_contracts_v01 as c, gate5_native_v01 as n, gate5_exchange_v01 as x
from candidate_domain import domain as d
from candidate_domain.memory import descent
from candidate_domain.policy import consumer_policy
from candidate_domain.profile import SUMMARY, context_from_checked, profile
from candidate_domain.publication import envelope
from candidate_domain.run import complete_report
from candidate_domain.storage import read, save


def fixture(changed=False):
    r=dict(request_id='request:own:report',revision=1,operation='FIND_OFFER',
        team_ref='team:own:report',venue_ref='venue:own:report',timezone='Europe/Tirane',
        currency='ALL',budget_minor=200,owner_approval_ref=None,sessions=[
            dict(session_id='session:'+name,start='2027-01-%02dT09:00'%(18+j),
                 end='2027-01-%02dT10:30'%(18+j),allow_shift_minutes=0)
            for j,name in enumerate(('north','east','west'))])
    if changed:
        r['request_id']='request:own:renamed'
        r['team_ref']='team:own:renamed'
        for j,s in enumerate(r['sessions']):
            s['session_id']='renamed:'+('z','b','a')[j]
        r['sessions'].reverse()
    intervals=[[a,b] for a,b,_ in d.request_times(r).values()]
    fields=[dict(field_id='field:'+name,surface='natural_grass',full_size=True,
        price_minor=price,available_utc=copy.deepcopy(intervals),occupied_utc=[])
        for name,price in (('east',23),('west',29))]
    if changed:
        for j,f in enumerate(fields):
            f['field_id']='renamed_field:'+('q','p')[j]
            f['price_minor']+=j+4
        fields.reverse()
    return r,dict(revision=4,venue_ref=r['venue_ref'],currency=r['currency'],fields=fields)


def local_policy():
    # Only the independent local inputs required by consumer_policy are supplied.
    # This component fixture makes no bootstrap/keyset authentication claim.
    return dict(local_root='root:own:reader',peer_root='root:own:publisher',
                accept_football=True,max_source_age=300)


def component_body(r,i,now):
    e=d.produce(r,i)
    d.verify_producer(r,i,e)
    p=local_policy()
    b=dict(version='g51.body.v01',
        source_record_ref=consumer_policy(p,{},r,r)['source_record_ref'],
        source_revision=e['offer_revision'],source_work_ref='work:own:component',
        source_review_ref='review:own:component',time_envelope=envelope(now,300),
        ttl_base='pt_created_at',source_lineage_refs=[],publisher=p['peer_root'],
        recipient=p['local_root'],request_sha256=c.sha(r),offer=e,booking=None)
    c.validate('body',b,profile=profile())
    return b


def source_projection(b,state,now):
    # Isolates the declared projection; these test values are not signed STATUS.
    return context_from_checked(dict(body=b,status_entry=dict(state=state)),
        dict(value=dict(checked_at=now,valid_until=now+60)))['source_projection']


class CurrentPublicationReportTests(unittest.TestCase):
    def test_terminal_status_overrides_ready_and_empty_producer_results(self):
        for feasible in (True,False):
            r,i=fixture()
            if not feasible:
                r['budget_minor']=0
            now=x.clock()
            b=component_body(r,i,now)
            original=copy.deepcopy(b)
            for terminal in ('REVOKED','SUPERSEDED'):
                with self.subTest(feasible=feasible,terminal=terminal), tempfile.TemporaryDirectory() as directory:
                    folder=Path(directory)
                    source=source_projection(b,terminal,now)
                    counts=dict(source_work=1,requester_work=0,host_attempt=0,mutations=0)
                    result=complete_report(folder,r,b['offer']['status'],b,source,counts=counts)
                    self.assertEqual(result['status'],'REFUSED')
                    self.assertEqual(result['slots'],[])
                    self.assertEqual(result['total_minor'],0)
                    self.assertEqual(result['source'],source)
                    self.assertIsNone(result['receipt_ref'])
                    self.assertEqual(result['counts'],dict(search=1,dispatch=0,mutations=0,observed=1))
                    self.assertEqual(read(folder/'report.json'),result)
                    self.assertEqual(b,original)

    def test_active_continuation_and_no_status_observation(self):
        r,i=fixture(); now=x.clock(); b=component_body(r,i,now)
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for state,expected in (('ACTIVE','OFFER_READY'),('REVOKED','REFUSED'),
                                   ('SUPERSEDED','REFUSED'),('UNAVAILABLE','CURRENT_STATUS_UNKNOWN')):
                folder=root/state; folder.mkdir()
                result=complete_report(folder,r,b['offer']['status'],b,
                                       current_source_state=state)
                self.assertEqual(result['status'],expected)
                self.assertEqual(result['slots'],b['offer']['slots'] if state=='ACTIVE' else [])
                self.assertEqual(result['total_minor'],b['offer']['total_minor'] if state=='ACTIVE' else 0)
                self.assertIsNone(result['source'])
            # A retained terminal observation cannot be replaced by a current ACTIVE caption.
            folder=root/'retained_terminal'; folder.mkdir()
            result=complete_report(folder,r,'OFFER_READY',b,source_projection(b,'REVOKED',now),
                                   current_source_state='ACTIVE')
            self.assertEqual(result['status'],'REFUSED')
            self.assertEqual(result['source']['status'],'REVOKED')

    def test_uncertainty_and_explicit_receipt_history_are_not_reset(self):
        r,i=fixture(); now=x.clock(); b=component_body(r,i,now)
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); folder=root/'after_start'; folder.mkdir()
            # Synthetic stage data tests reporting only; it is not a native receipt or execution.
            save(folder/'action_failure.json',dict(stages=[dict(stage='HOST_ATTEMPT'),
                 dict(stage='EXECUTOR_STARTED')],reason='OWN_COMPONENT_FIXTURE'))
            counts=dict(source_work=0,requester_work=0,host_attempt=1,mutations=None)
            result=complete_report(folder,r,'OFFER_READY',b,source_projection(b,'REVOKED',now),
                receipt='receipt:own:component',counts=counts)
            self.assertEqual(result['status'],'CURRENT_STATUS_UNKNOWN')
            self.assertEqual(result['counts']['dispatch'],1)
            self.assertIsNone(result['counts']['mutations'])
            self.assertEqual(result['receipt_ref'],'receipt:own:component')
            for operation,status in (('VERIFY_EXISTING','VERIFIED'),('CONFIRM_MOCK_BOOKING','MOCK_BOOKED')):
                folder=root/operation; folder.mkdir()
                result=complete_report(folder,dict(r,operation=operation),status,
                    receipt='receipt:own:component',slots=b['offer']['slots'],
                    current_source_state='REVOKED')
                self.assertEqual(result['status'],status)
                self.assertEqual(result['slots'],b['offer']['slots'])
                self.assertEqual(result['counts']['dispatch'],0)
                self.assertEqual(result['counts']['mutations'],0)


class SourceReferenceTests(unittest.TestCase):
    def test_origin_reference_and_exact_native_descent_bindings(self):
        references=[]
        for changed in (False,True):
            r,i=fixture(changed); p=local_policy(); now=x.clock()
            b=component_body(r,i,now)
            ref=consumer_policy(p,{},r,r)['source_record_ref']
            publisher_view=dict(p,local_root=p['peer_root'],peer_root=p['local_root'])
            self.assertEqual(ref,consumer_policy(publisher_view,{},r,r)['source_record_ref'])
            self.assertRegex(ref,r'^[0-9a-f]{64}$')
            self.assertEqual(ref,b['source_record_ref'])
            self.assertNotEqual(ref,consumer_policy(p,{},dict(r,operation='CONFIRM_MOCK_BOOKING'),r)['source_record_ref'])
            references.append(ref)
            # Metadata component fixture only; production validates the signed descriptor first.
            pointer=dict(publisher_root_id=p['peer_root'],source_record_ref=ref,
                pointer_id='pointer:own:reference',body_sha256=c.sha(b),
                safe_summary=SUMMARY,time_envelope=b['time_envelope'])
            with tempfile.TemporaryDirectory() as directory:
                folder=Path(directory)
                decision=descent(pointer,p['local_root'],folder,now,now+300)
                proof=read(folder/'pointer_descent.json')
                record_id=proof['request']['approved_record_ids'][0]
                stored=LocalDRS(folder/'drs').read_record('work',record_id)['content']['record']
                self.assertEqual(stored['source_reference_ids'],[ref])
                self.assertEqual(stored['time_envelope'],pointer['time_envelope'])
                self.assertEqual(stored['content_fingerprint'],c.sha(pointer))
                self.assertEqual(stored['authority_envelope']['owning_local_root_id'],p['local_root'])
                self.assertEqual(proof['request']['root_decision_id'],decision)
                self.assertTrue(proof['result']['limits_respected'])
                self.assertFalse(proof['result']['creates_authority'])
                self.assertFalse(proof['result']['creates_permission'])
                self.check_public_secret_guard(stored)
        self.assertNotEqual(*references)

    def check_public_secret_guard(self,stored):
        # Rebuild metadata through the original public constructor, never a Root grant.
        values=dict(stored,
            semantic_address=n.rebuilt(address.build_semantic_address_v01,stored['semantic_address']),
            time_envelope=n.rebuilt(address.build_drs_time_envelope_v01,stored['time_envelope']),
            authority_envelope=n.rebuilt(address.build_drs_authority_envelope_v01,stored['authority_envelope']))
        # Deliberately shaped synthetic reference, not a claimed hash of a real record.
        # The public DRS contract distinguishes bare SHA256 references from general text.
        digest_shape='a'+'0'*13+'b'*50
        for bad in ('source:football:'+digest_shape,'token:own_synthetic_fixture'):
            with self.assertRaisesRegex(ValueError,'^drs_secret_payload_forbidden$'):
                n.rebuilt(address.build_meaning_record_v01,dict(values,source_reference_ids=[bad]))
        good=n.rebuilt(address.build_meaning_record_v01,dict(values,source_reference_ids=[digest_shape]))
        self.assertEqual(good.source_reference_ids,(digest_shape,))
        self.assertEqual(good.time_envelope,values['time_envelope'])
