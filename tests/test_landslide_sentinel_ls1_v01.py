"""Independent expected assertions for the bounded LS1 slice."""
import json
import os
from pathlib import Path
import pytest
from hedgehog.domains.landslide_sentinel import contracts_v01 as c,evidence_v01 as ev
from hedgehog.domains.landslide_sentinel import kernel_adapter_v01 as k,semantic_adapter_v01 as semantics
from hedgehog.domains.landslide_sentinel.events_v01 import EventBook,observation,AllocationLedger,CapabilityState
from hedgehog.domains.landslide_sentinel.incident_policy_v01 import Incident
from hedgehog.domains.landslide_sentinel.monitoring_runtime_v01 import Sentinel,ControlledEpisode
from hedgehog.domains.landslide_sentinel.outbox_v01 import Outbox,Receiver
from demo.run_landslide_sentinel_ls1_v01 import fixture,run_story


def directory(name):
    path=Path(os.environ['LS1_EVIDENCE'])/'runs'/os.environ['LS1_RUN_ID']/name
    path.parent.mkdir(parents=True,exist_ok=True);return path


def test_time_and_actual_cadence_f1():
    old=json.loads((Path(__file__).resolve().parents[1]/'fixtures/landslide_sentinel/ls0_inputs_v01.json').read_bytes())
    session=Sentinel(directory('chronology'),old)
    session.ingest_rainfall(old['changed_rainfall'])
    session.prepare_config();session.dispatch_pending()
    assert session.tick==30 and session.next_intake==45 and session.cadence_seconds==15
    assert session.intake(44) is None and session.intake(45)['scenario_tick']==45
    assert all(v['scenario_tick']<=45 for v in session.frames)
    book=EventBook()
    with pytest.raises(ValueError):book.ingest([observation('reserve',400,50,1,received=49)],49)
    book.ingest([observation('reserve',400,0,1,received=100)],100)
    with pytest.raises(ValueError,match='stale'):book.current('reserve','critical')
    for bad in (True,1.5):
        with pytest.raises(ValueError):observation('reserve',bad,0,1)
    ev.save(session.directory/'f1_result.json',dict(configured_at=30,next_intake=session.intakes[0]['scenario_tick'],packet=session.monitor_pending['packet_id']))


def test_local_routes_counters_and_profiles_f2_f4():
    from hedgehog.domains.landslide_sentinel.monitoring_runtime_v01 import SentinelMemory,memory_dependencies
    with ev.BoundaryObserver() as observer:
        session=ControlledEpisode(directory('routes'),fixture())
        session.ingest([observation(v['sensor'],v['value'],0,1) for v in fixture()['frames']],0)
        session.intake(0);result=session.local_work()
        assert result['features']['hard_critical'] is False and session.routes[-1]['proposal']['selected_mode']=='deterministic'
        store=SentinelMemory(session.directory/'memory');ref=store.remember(session)
        revisions=[]
        for online in (True,False):
            session.capabilities.change(online)
            selected=SentinelMemory(session.directory/'memory').select(root=session.root,request=session.request,
                dependency=memory_dependencies(session),now=session.source.sample().evaluation_time)
            assert selected is not None
            work=session.pure_consumer('sentinel.information.v01',dict(summary=c.canonical(selected[0]).decode(),record_id=ref))
            revisions.append(work[0].candidate.revision_id)
        assert revisions[0]!=revisions[1] and session.budgets.tasks['pure_work']['spent']==3
        assert k.mode_availability(session,'local_slm')=='UNAVAILABLE'
        session.capabilities=CapabilityState('EMULATED_LOCAL_SLM',True);session.capabilities.change(False)
        assert session.capabilities.available('harness') and not session.capabilities.available('site_context')
        assert k.mode_availability(session,'cloud_llm')=='AVAILABLE'
        session.capabilities.request('harness','controlled_representation_only')
        session.capabilities.harness=False
        with pytest.raises(ValueError):session.capabilities.request('harness','removed')
        fake=object.__new__(semantics.GeminiHarness);fake.available=False;fake.calls=0
        with pytest.raises(ValueError):fake.respond({})
        counts=observer.snapshot()
        assert counts['harness_attempt']==1 and counts['harness_rejected']==1 and counts['harness_transport']==0
        assert counts['site_request']==2 and counts['site_rejected']==1 and counts['sensor_completed']==1
        assert k.mode_availability(session,'cloud_llm')=='UNAVAILABLE'
        ev.save(session.directory/'counts.json',dict(counts=counts,routes=session.routes,work=result))


def test_finite_budget_no_identity_reset_f3():
    ledger=AllocationLedger(3);ledger.allocate('pending',2,'old_context');ledger.consume('pending','REQUEST_ENTER')
    prior=c.canonical(ledger.tasks['pending']);ledger.allocate('fresh',1,'new_context');ledger.consume('fresh','LOCAL_WORK_ENTER')
    assert c.canonical(ledger.tasks['pending'])==prior
    with pytest.raises(ValueError):ledger.consume('fresh','EXHAUSTED_WORK')
    with pytest.raises(ValueError):ledger.allocate('fresh',1,'reset')
    with pytest.raises(ValueError):ledger.allocate('new_id',1,'reset_global')
    ev.save(directory('budget')/'result.json',dict(tasks=ledger.tasks,entries=ledger.entries))


def test_measured_clearance_duplicate_missing_and_unresolved():
    book=EventBook();incident=Incident()
    def pair(tick,a,b,sequence):
        rows=[observation('displacement',a,tick,sequence),observation('reserve',b,tick,sequence,status='MISSING' if b is None else 'HEALTHY')]
        book.ingest(rows,tick);return rows,incident.evaluate(book)
    _,critical=pair(0,6200,5800,1);assert critical['new_incident'] and critical['ratios_micros'][0]>1000000
    rows,quiet=pair(15,400,350,2);assert not quiet['clearance']
    book.ingest(rows,15);assert not incident.evaluate(book)['clearance'] and len(incident.witnesses)==1
    _,missing=pair(30,400,None,3);assert not missing['clearance'] and not incident.witnesses
    for tick,seq in ((45,4),(60,5),(75,6)):_,answer=pair(tick,400,350,seq)
    assert answer['clearance'] and len(incident.witnesses)==3 and incident.state=='ACTIVE'
    # Even sufficient evidence is not an OFF receipt; cleanup cannot close it.
    with pytest.raises(ValueError):incident.close(75,None)
    assert incident.state=='ACTIVE'
    ev.save(directory('clearance')/'result.json',dict(critical=critical,measured=answer,state_without_off=incident.state))


def test_outbox_exact_receiver_and_ack_negatives():
    root=directory('outbox');box=Outbox(root/'queue');receiver=Receiver(root/'receiver')
    report=dict(classification='TEST',incident_id='incident:one',generated_at=10,historical_interval=[1,10],previous_report_ref=None)
    queued=box.queue(report);raw=box.read(queued['message_id']);ack=box.deliver(queued['message_id'],receiver)
    assert box.deliver(queued['message_id'],receiver)==ack and box.read(queued['message_id'])==raw
    assert len(list(receiver.directory.iterdir()))==1
    class MissingAck(Receiver):
        def receive(self,ref,raw):super().receive(ref,raw);return None
    class ConflictingAck(Receiver):
        def receive(self,ref,raw):return dict(super().receive(ref,raw),payload_sha256='0'*64)
    for cls in (MissingAck,ConflictingAck):
        with pytest.raises(ValueError,match='ack_not_verified'):box.deliver(queued['message_id'],cls(root/cls.__name__))
        assert box.trail[-1]['state']=='UNKNOWN'
    ev.save(root/'result.json',dict(trail=box.trail,ack=ack))


def test_controlled_s0_s5():
    story=run_story(directory('story'))
    assert story['status']=='CONTROLLED_S0_S5_COMPLETE'
    assert story['modes']==['deterministic','full_fractal','memory_informed']
    assert story['total_counts']['public_D']==1 and story['total_counts']['public_E']==1
    assert story['total_counts']['harness_transport']==0 and story['total_counts']['signal_effect']==2
    assert story['total_counts']['configuration_effect']==2 and story['total_counts']['report_effect']==2


def test_controlled_roles_and_native_report_preflight():
    from jsonschema import Draft202012Validator
    from referencing import Registry,Resource
    root=Path(__file__).resolve().parents[1]
    resources=[]
    for path in (root/'schemas').glob('*.json'):
        value=json.loads(path.read_bytes())
        if '$id' in value:resources.append((value['$id'],Resource.from_contents(value)))
    schema=json.loads((root/'schemas/semantic_work_v01.schema.json').read_bytes())
    with ev.BoundaryObserver() as observer:
        session=ControlledEpisode(directory('native_preflight'),fixture())
        session.ingest([observation(v['sensor'],v['value'],120,1) for v in fixture()['frames']],120)
        session.diagnostic_roles(fixture()['roles'])
        for row in session.role_results[-1]['role_consumptions']:
            assert row['semantic']['actual_mode']=='DETERMINISTIC'
            Draft202012Validator(dict(schema,**{'$ref':'#/$defs/actorContribution'}),registry=Registry().with_resources(resources)).validate(row['semantic']['contribution'])
        session.start_optional();session.connectivity(False,121)
        session.ingest([observation('displacement',6200,135,2),observation('reserve',5800,135,2)],135)
        try:
            session.evaluate_local();assert session.signal and not session.pending_return
            with pytest.raises(ValueError):session.deliver()
            session.connectivity(True,136);session.deliver();session.deliver()
            assert session.read_signal()['signal'] and session.incident.state=='ACTIVE'
        finally:session.release_optional()
        ev.save(session.directory/'preflight.json',dict(counts=observer.snapshot(),roles=session.role_results,trail=session.outbox.trail,
            pending_costs=session.budgets.tasks,unresolved_incident=session.incident.state,unresolved_signal=session.read_signal()))
