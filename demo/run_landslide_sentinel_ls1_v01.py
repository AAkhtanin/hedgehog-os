"""One controlled LS1 evaluator; no live model calls or physical effects."""
import argparse
import json
from pathlib import Path
import time
from hedgehog.domains.landslide_sentinel import contracts_v01 as c,evidence_v01 as ev
from hedgehog.domains.landslide_sentinel import kernel_adapter_v01 as k,capability_registry_v01 as caps
from hedgehog.domains.landslide_sentinel.events_v01 import observation,EventBook
from hedgehog.domains.landslide_sentinel.monitoring_runtime_v01 import ControlledEpisode,SentinelMemory,memory_dependencies,clock_args
from hedgehog import work_execution_host_v01 as hosts

BASE='50ab3916bff55e8034cf7e6c509d4803c5447589'


def fixture():
    return json.loads((Path(__file__).resolve().parents[1]/'fixtures/landslide_sentinel/ls1_inputs_v01.json').read_bytes())


def run_story(directory):
    data=fixture();start=time.monotonic();session=None
    with ev.BoundaryObserver() as observer:
        try:
            session=ControlledEpisode(directory,data)
            counts={};before=observer.snapshot()
            initial=[observation(v['sensor'],v['value'],0,1) for v in data['frames']]
            session.ingest(initial,0);session.intake(0);quiet=session.local_work()
            session.prepare_config();session.dispatch_pending()
            assert session.next_intake==60 and not session.signal
            consumed_initial=session.monitor_pending['packet_id']
            store=SentinelMemory(session.directory/'local_drs')
            args=dict(root=session.root,request=session.request,dependency=memory_dependencies(session),now=session.source.sample().evaluation_time)
            assert store.select(**args) is None
            record=store.remember(session)
            second=[observation(v['sensor'],v['value'],60,2) for v in data['frames']]
            session.ingest(second,60);session.intake(60);session.local_work()
            fresh=SentinelMemory(session.directory/'local_drs');warm=fresh.select(**dict(args,now=session.source.sample().evaluation_time))
            assert warm is not None
            session.work_mode='memory_informed'
            consumed=session.pure_consumer('sentinel.information.v01',dict(summary=c.canonical(warm[0]).decode(),record_id=record))
            session.work_mode='deterministic'
            ev.save(session.directory/'quiet_memory.json',dict(cold=store.events,warm=fresh.events,consumed=consumed[1],quiet=quiet))
            counts['S0']=observer.delta(before);before=observer.snapshot()
            session.prepare_config(reviewed=True)
            assert session.monitor_pending['packet_id']!=consumed_initial
            stable=c.canonical(session.stable_sources());session.rainfall_delta()
            assert session.tick==105 and session.intakes[-1]['scenario_tick']==105
            assert c.canonical(session.stable_sources())==stable and not session.signal
            counts['S1']=observer.delta(before);before=observer.snapshot()

            def ingest_local(row):
                values=[observation(ch,row[ch],row['tick'],session.book.latest[ch]['sequence']+1,
                    status='MISSING' if row[ch] is None else 'HEALTHY') for ch in ('displacement','reserve')]
                session.ingest(values,row['tick']);assert session.intake(row['tick']) is not None
                return values

            ingest_local(data['local_events'][0]);session.diagnostic_roles(data['roles'])
            assert not session.evaluate_local()['hard_critical'] and not session.signal
            counts['S2']=observer.delta(before);before=observer.snapshot()
            session.start_optional();session.connectivity(False,125)
            for lane in ('site_context','remote_rain','site_upload','harness'):
                try:session.capabilities.request(lane,'after_outage')
                except ValueError:pass
                else:raise AssertionError('Unavailable lane admitted')
            ingest_local(data['local_events'][1]);session.local_work()
            local_memory=SentinelMemory(session.directory/'local_drs').select(**dict(args,now=session.source.sample().evaluation_time))
            assert local_memory is not None
            session.work_mode='memory_informed'
            offline_memory=session.pure_consumer('sentinel.information.v01',dict(summary=c.canonical(local_memory[0]).decode(),record_id=record))
            session.work_mode='deterministic'
            counts['S3a']=observer.delta(before);before=observer.snapshot()
            ingest_local(data['local_events'][2]);critical=session.evaluate_local()
            assert critical['hard_critical'] and session.read_signal()['signal'] and not session.pending_return
            queued=session.outbox.read(session.message['message_id'])
            ingest_local(data['local_events'][3]);assert not session.evaluate_local()['new_incident']
            effects=len(session.executed)
            try:hosts.dispatch_current_action_v01(session.host,packet_id=session.on_effect['packet_id'],task_id=session.id,
                expected_revision=session.host.revision,**clock_args(session.source.sample()))
            except ValueError as error:duplicate=str(error)
            else:raise AssertionError('Duplicate ON executed')
            assert len(session.executed)==effects
            session.release_optional();assert session.on_completed['monotonic']<session.pending_return[0]['monotonic']
            counts['S3b']=observer.delta(before);before=observer.snapshot()
            session.connectivity(True,180)
            external=EventBook();external.ingest([observation('rainfall',12000,0,1,received=180,lineage='site:remote_accumulation')],180)
            try:external.current('rainfall','context')
            except ValueError as error:stale_context=str(error)
            else:raise AssertionError('Restoration renewed stale observed time')
            fresh_context=observation('rainfall',41000,180,2,lineage='site:remote_accumulation')
            session.capabilities.request('site_context',c.identity('restored_context',fresh_context))
            external.ingest([fresh_context],180);assert external.current('rainfall','context')==fresh_context
            ev.save(session.directory/'restoration_context.json',dict(history=[json.loads(v) for v in external.history],
                stale_current_refusal=stale_context,current=fresh_context,meaning='synthetic_one_hour_accumulation_at_the_same_site'))
            ingest_local(data['local_events'][4]);session.local_work()
            session.deliver();session.deliver()
            assert session.outbox.read(session.message['message_id'])==queued
            assert session.receiver.readback(session.message['message_id'])['payload_sha256']==c.digest(queued)
            assert len(list(session.receiver.directory.glob('*.json')))==1 and session.read_signal()['signal']
            counts['S4']=observer.delta(before);before=observer.snapshot()
            first=ingest_local(data['local_events'][5]);assert not session.evaluate_local()['clearance']
            session.ingest(first,195);assert not session.evaluate_local()['clearance']
            ingest_local(data['local_events'][6]);assert not session.evaluate_local()['clearance'] and session.read_signal()['signal']
            for row in data['local_events'][7:]:
                ingest_local(row);assessment=session.evaluate_local()
            assert assessment['clearance'] and not session.read_signal()['signal'] and session.incident.state=='CLOSED'
            session.remember_incident();counts['S5']=observer.delta(before)
            before=observer.snapshot();info=session.query_incident();counts['information']=observer.delta(before)
            assert info['selected'][0]['signal_off_at']==255
            for key in ('harness_attempt','harness_transport','sensor_attempt','configuration_effect','signal_effect','report_effect'):
                assert counts['information'][key]==0
            story=dict(status='CONTROLLED_S0_S5_COMPLETE',root=session.root,host_continuity='SAME_LIVE_HOST',
                modes=sorted({row['proposal']['selected_mode'] for row in session.routes}),counts=counts,total_counts=observer.snapshot(),
                timings=session.timings,seconds=time.monotonic()-start,initial_packet=consumed_initial,
                changed_pending_packet=session.monitor_pending['packet_id'],intakes=session.intakes,
                budgets=dict(tasks=session.budgets.tasks,entries=session.budgets.entries),incident=session.incident.transitions,
                final_signal=session.read_signal(),outbox=session.outbox.trail,duplicate_refusal=duplicate,
                native_replay='UNSUPPORTED_NATIVE_SCHEMA',live_calls_scope='NAMED_BOUNDARIES_ONLY')
            ev.save(session.directory/'routes.json',session.routes)
            ev.save(session.directory/'source_history.json',dict(history=[json.loads(b) for b in session.book.history],arrivals=session.book.arrivals))
            ev.save(session.directory/'effects.json',session.effects)
            ev.save(session.directory/'story.json',story)
            package=ev.export_story(session.directory,BASE);ev.save(session.directory/'package_result.json',package)
            return story
        finally:
            if session is not None:
                if session.pending_worker is not None and session.pending_worker.is_alive():session.release_optional()
                ev.save(session.directory/'final_counters.json',observer.snapshot())
                ev.save(session.directory/'cleanup.json',dict(worker_joined=session.pending_worker is None or not session.pending_worker.is_alive(),
                    signal=session.read_signal(),incident=session.incident.state,infrastructure_does_not_clear=True))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args();print(json.dumps(run_story(args.output),sort_keys=True))


if __name__=='__main__':main()
