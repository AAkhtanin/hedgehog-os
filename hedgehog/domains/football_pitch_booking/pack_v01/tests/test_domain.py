"""Own invented fixtures; reviewer execution only. These are not examiner cases."""
import copy
import tempfile
import unittest
from pathlib import Path
from hedgehog.external_drs import gate5_contracts_v01 as c
from candidate_domain import domain as d
from candidate_domain.profile import profile, context_from_checked
from candidate_domain.publication import envelope
from candidate_domain.policy import approve_shift, approve_booking
from candidate_domain.storage import save

def fixture():
    r=dict(request_id='req:training',revision=1,operation='FIND_OFFER',team_ref='team:synthetic',
        venue_ref='venue:local',timezone='Europe/Tirane',currency='ALL',budget_minor=200,
        owner_approval_ref=None,sessions=[
            dict(session_id='s'+str(j),start='2027-01-%02dT09:00'%(6+j),end='2027-01-%02dT10:30'%(6+j),
                 allow_shift_minutes=0) for j in range(3)])
    times=d.request_times(r)
    intervals=[[a,b+1800] for a,b,_ in times.values()]
    fields=[dict(field_id=name,surface='natural_grass',full_size=True,price_minor=price,
                 available_utc=copy.deepcopy(intervals),occupied_utc=[])
            for name,price in (('field:c',29),('field:a',17))]
    return r,dict(revision=3,venue_ref=r['venue_ref'],currency=r['currency'],fields=fields)

class DomainTests(unittest.TestCase):
    def test_complete_and_changed_input(self):
        r,i=fixture(); e=d.produce(r,i); d.verify_producer(r,i,e)
        self.assertEqual(e['status'],'OFFER_READY')
        self.assertEqual(e['total_minor'],3*min(f['price_minor'] for f in i['fields']))
        changed=copy.deepcopy(i); changed['fields'][1]['price_minor']=35
        other=d.produce(r,changed); d.verify_producer(r,changed,other)
        self.assertNotEqual(e['total_minor'],other['total_minor'])
        self.assertNotEqual(e['slots'],other['slots'])

    def test_permutation_and_tie_rule(self):
        r,i=fixture()
        for f in i['fields']: f['price_minor']=19
        e=d.produce(r,i)
        i['fields'].reverse(); changed=copy.deepcopy(r); changed['sessions'].reverse()
        p=d.produce(changed,i)
        self.assertEqual(e['slots'],p['slots'])
        self.assertTrue(all(s['field_id']==min(f['field_id'] for f in i['fields']) for s in p['slots']))
        for f in i['fields']: f['field_id']='z' if f['field_id']=='field:a' else 'b'
        renamed=d.produce(r,i)
        self.assertTrue(all(s['field_id']=='b' for s in renamed['slots']))
        self.assertEqual(renamed['total_minor'],e['total_minor'])

    def test_hard_conditions_and_continuation(self):
        r,i=fixture(); bad=copy.deepcopy(i)
        bad['fields'][0]['surface']='artificial'
        bad['fields'][1]['full_size']=False
        self.assertEqual(d.produce(r,bad)['status'],'NO_COMPLETE_OFFER')
        self.assertEqual(d.produce(r,i)['status'],'OFFER_READY')
        low=copy.deepcopy(r); low['budget_minor']=1
        self.assertEqual(d.produce(low,i)['slots'],[])
        wrong=copy.deepcopy(i); wrong['currency']='EUR'
        with self.assertRaises(d.Refusal): d.produce(r,wrong)

    def test_half_open_and_long_overlap(self):
        r,i=fixture(); times=d.request_times(r)
        first=list(times.values())[0]
        for f in i['fields']: f['occupied_utc']=[[first[0]-300,first[0]]]
        self.assertEqual(d.produce(r,i)['status'],'OFFER_READY')
        for f in i['fields']: f['occupied_utc']=[[first[0],first[1]+3600]]
        self.assertEqual(d.produce(r,i)['slots'],[])
        f=dict(available_utc=[[first[0],first[0]+600],[first[0]+600,first[1]]],occupied_utc=[])
        self.assertTrue(d.available(f,first[0],first[1]))

    def test_shift_requires_bound_approval_and_remains_overlap_checked(self):
        r,i=fixture(); changed=copy.deepcopy(r); changed['revision']=2; changed['owner_approval_ref']='approval:shift'
        shifted=changed['sessions'][2]; shifted['allow_shift_minutes']=30
        a,b,_=d.request_times(r)[shifted['session_id']]
        for f in i['fields']: f['occupied_utc']=[[a,a+1800]]
        self.assertEqual(d.produce(r,i)['slots'],[])
        result=d.produce(changed,i)
        self.assertEqual(result['status'],'OFFER_READY')
        chosen=next(s for s in result['slots'] if s['session_id']==shifted['session_id'])
        self.assertEqual(chosen['start_utc'],a+1800)
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); save(root/'requests'/(c.sha(r)+'.json'),r)
            p=dict(shift_approvals=[])
            with self.assertRaises(d.Refusal): approve_shift(changed,p,root)
            p['shift_approvals']=[dict(approval_ref='approval:shift',request_sha256=c.sha(changed),
                                      previous_request_sha256=c.sha(r))]
            approve_shift(changed,p,root)
        for f in i['fields']: f['occupied_utc']=[[a,b+1800]]
        self.assertEqual(d.produce(changed,i)['slots'],[])

    def test_missing_and_duplicate_inputs(self):
        r,i=fixture()
        for key in ('budget_minor','timezone'):
            bad=copy.deepcopy(r); del bad[key]
            with self.assertRaises(d.Refusal): d.produce(bad,i)
        bad=copy.deepcopy(r); bad['budget_minor']=True
        with self.assertRaises(d.Refusal): d.produce(bad,i)
        bad=copy.deepcopy(r); bad['sessions'][1]['session_id']=bad['sessions'][0]['session_id']
        with self.assertRaises(d.Refusal): d.produce(bad,i)
        bad=copy.deepcopy(i); bad['fields'][1]['field_id']=bad['fields'][0]['field_id']
        with self.assertRaises(d.Refusal): d.produce(r,bad)

    def test_producer_validation_never_repairs(self):
        r,i=fixture(); e=d.produce(r,i)
        for mutation in ('price','slots','status'):
            bad=copy.deepcopy(e)
            if mutation=='price': bad['total_minor']+=1
            if mutation=='slots': bad['slots']=[]
            if mutation=='status': bad['status']='NO_COMPLETE_OFFER'
            with self.assertRaises(ValueError): d.verify_producer(r,i,bad)
        bad=copy.deepcopy(e); bad['unexpected']=True
        with self.assertRaises(ValueError): d.validate_e(bad)
        expensive=copy.deepcopy(e)
        expensive['slots']=[dict(s,field_id=i['fields'][0]['field_id'],price_minor=i['fields'][0]['price_minor'])
                            for s in e['slots']]
        expensive['total_minor']=sum(s['price_minor'] for s in expensive['slots'])
        with self.assertRaises(d.Refusal): d.verify_producer(r,i,expensive)

    def test_schema_does_not_accept_unknown_body_fields(self):
        r,i=fixture()
        b=dict(version='g51.body.v01',source_record_ref='source:own:test',source_revision=i['revision'],
            source_work_ref='work:own:test',source_review_ref='review:own:test',time_envelope=envelope(1900000000,40),
            ttl_base='pt_created_at',source_lineage_refs=[],publisher='root:venue',recipient='root:team',
            request_sha256=c.sha(r),offer=d.produce(r,i),booking=None)
        c.validate('body',b,profile=profile())
        bad=copy.deepcopy(b); bad['expected_answer']='forbidden'
        with self.assertRaises(ValueError): c.validate('body',bad,profile=profile())
        bad=copy.deepcopy(b); bad['offer']['total_minor']+=1
        with self.assertRaises(ValueError): c.validate('body',bad,profile=profile())
        # These syntactic test IDs are never presented as native evidence.

    def test_context_consumption_preserves_B(self):
        r,i=fixture()
        b=dict(version='g51.body.v01',source_record_ref='source:own:test',source_revision=i['revision'],
            source_work_ref='work:own:test',source_review_ref='review:own:test',time_envelope=envelope(1900000000,40),
            ttl_base='pt_created_at',source_lineage_refs=[],publisher='root:venue',recipient='root:team',
            request_sha256=c.sha(r),offer=d.produce(r,i),booking=None)
        status=dict(value=dict(checked_at=1900000001,valid_until=1900000030))
        context=context_from_checked(dict(body=b,status_entry=dict(state='ACTIVE')),status)
        result=d.consume(r,context)
        self.assertEqual(result['slots'],b['offer']['slots'])
        self.assertEqual(result['source'],context['source_projection'])
        bad=copy.deepcopy(context); bad['source_projection']['schedule_revision']+=1
        with self.assertRaises(ValueError): d.consume(r,bad)
        bad=copy.deepcopy(context); del bad['body']['offer']['slots']
        with self.assertRaises(ValueError): d.consume(r,bad)
        # This isolates pure shape mapping; no signature/retrieval claim is made.

    def test_time_and_request_mismatch(self):
        r,i=fixture(); e=d.produce(r,i)
        t=envelope(1900000000,40); p=dict(max_source_age=30,max_validity_horizon=300)
        self.assertEqual(c.temporal(t,1900000029,p),1900000030)
        for now in (1899999999,1900000030,1900000040):
            with self.assertRaises(ValueError): c.temporal(t,now,p)
        wrong=copy.deepcopy(r); wrong['team_ref']='team:another'
        with self.assertRaises(ValueError): d.verify_producer(wrong,i,e)

class NativeReviewerTests(unittest.TestCase):
    def test_real_producer_work_and_changed_inputs(self):
        from candidate_domain.native import perform
        r,i=fixture()
        producer=perform('venue',r,i,'root:own:venue','task:own:producer')
        e=c.decode(producer['outputs']['offer_json'].encode()); d.verify_producer(r,i,e)
        self.assertEqual(producer['attempts'],1)
        self.assertEqual(producer['inputs']['inventory_json'],c.canonical(i).decode())
        # Only a producer is tested here; full peer authenticity requires the independent runner.
        changed=copy.deepcopy(i); changed['fields'][1]['price_minor']+=7
        second=perform('venue',r,changed,'root:own:venue','task:own:producer_changed')
        self.assertNotEqual(second['outputs'],producer['outputs'])

    def test_native_mock_and_history_no_redispatch(self):
        from candidate_domain.publication import build
        from candidate_domain.effect import book, reconcile
        from candidate_domain.policy import validate_policy
        r,i=fixture()
        p=dict(local_root='root:own:venue',peer_root='root:own:team',publish_enabled=True,release_enabled=True,
            accept_football=True,recipients=['root:own:team'],status='ACTIVE',ttl_seconds=300,max_source_age=300,
            shift_approvals=[],book_approvals=[])
        validate_policy(p)
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); out=root/'find'; out.mkdir()
            cap=c.crypto.generate_root_signer_capability_v01(root_id=p['local_root'])
            keys=c.crypto.build_trusted_root_key_set_v01(capabilities=(cap,))
            public=c.crypto.trusted_root_key_set_to_plain_dict_v01(keys)
            body=build(r,i,p,root/'state',out,cap,keys,public)['body']
            confirm=dict(r,operation='CONFIRM_MOCK_BOOKING',owner_approval_ref='approval:book')
            p['book_approvals']=[dict(approval_ref='approval:book',request_sha256=c.sha(confirm),
                                     offer_request_sha256=c.sha(r))]
            approve_booking(confirm,body,p)
            effect_out=root/'confirm'; effect_out.mkdir()
            booking=book(confirm,i,body,p,root/'state',effect_out)
            before=(root/'state'/'registry.json').read_bytes()
            history=reconcile(root/'state',confirm)
            self.assertEqual(history['saved']['booking'],booking)
            self.assertEqual((root/'state'/'registry.json').read_bytes(),before)
            bad=dict(confirm,budget_minor=confirm['budget_minor']+1)
            with self.assertRaises(d.Refusal): reconcile(root/'state',bad)
