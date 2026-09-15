"""Opt-in source-bound analytical work. Mock equipment; live transport only with --live."""
import argparse
import json
from pathlib import Path
import time
from dataclasses import replace
from hedgehog.domains.landslide_sentinel import contracts_v01 as c,semantic_adapter_v01 as sem,evidence_v01 as ev
from hedgehog.domains.landslide_sentinel import kernel_adapter_v01 as k
from hedgehog.domains.landslide_sentinel.events_v01 import observation,CapabilityState
from hedgehog.domains.landslide_sentinel.monitoring_runtime_v01 import ControlledEpisode,SentinelMemory,memory_dependencies

DUTIES=('LOCAL_SLOPE_ANALYST','CLOUD_ENVIRONMENTAL_ANALYST','ADVERSARIAL_SENSOR_REVIEWER')


def fixture():
    root=Path(__file__).resolve().parents[1]/'fixtures/landslide_sentinel'
    base=json.loads((root/'ls1_inputs_v01.json').read_bytes())
    data=json.loads((root/'ls2_inputs_v01.json').read_bytes())
    base.update(frames=[dict(v,scenario_tick=0) for v in data['frames']],reserve_series_raw=data['reserve_series_raw'])
    return base,data


def collect_current(session,note,duty,harness,controlled=None):
    if harness is not None:session.capabilities.request('harness',c.identity('analyst_request',dict(note=note,duty=duty)))
    _,value=sem.collect(session.frames,note,session.root,session.source.sample().evaluation_time,harness=harness,
        controlled=controlled,intended_role=duty,capabilities=session.capabilities.snapshot(duty),
        observations=tuple(session.book.latest.values()),tick=session.tick,policy=session.contract)
    return value


def run(directory,*,live=False,config=None,fractal=True,contrasts_only=False,experiment=None):
    base,data=fixture();directory=Path(directory);start=time.monotonic()
    if experiment is not None:
        c.require(type(experiment) is dict and set(experiment)=={'notes'} and type(experiment['notes']) is list
            and len(experiment['notes'])==2 and all(type(v) is str and bool(v) for v in experiment['notes']),
            'frozen_experiment_input_shape')
        source=dict(data['notes']['maintenance'])
        data['notes']=dict(maintenance=dict(source,text=experiment['notes'][0]),new_crack=dict(source,text=experiment['notes'][1]))
    with ev.BoundaryObserver() as observer:
        session=ControlledEpisode(directory,base)
        if experiment is not None:ev.save(directory/'experiment_input.json',experiment)
        session.ingest([observation(v['sensor'],v['value'],data['tick'],1,
            observed_start=data['rainfall_observed_start'] if v['sensor']=='rainfall' else None) for v in data['frames']],data['tick'])
        session.capabilities=CapabilityState('EMULATED_LOCAL_SLM',live)
        harness=sem.GeminiHarness(directory/'captures',config_path=config) if live else None
        def collect(note,duty,index):
            controlled=None if live else dict(diagnostic={'LOCAL_SLOPE_ANALYST':'REFERENCE_INTEGRITY',
                'CLOUD_ENVIRONMENTAL_ANALYST':'TEMPORAL_CONTEXT_APPLICABILITY','ADVERSARIAL_SENSOR_REVIEWER':'INDEPENDENT_RESERVE_SERIES'}[duty],
                reason='Controlled admitted diagnostic input.')
            try:value=collect_current(session,note,duty,harness,controlled)
            except ValueError as error:
                recoverable=isinstance(error,json.JSONDecodeError) or str(error) in ('semantic_source_binding','semantic_shape','semantic_reason','semantic_diagnostic')
                if not live or not recoverable:raise
                ev.phase(directory,'ONE_INVALID_REPRESENTATION_RETRY',duty=duty,previous_attempt=harness.calls,error_type=type(error).__name__)
                value=collect_current(session,note,duty,harness,controlled)
            ev.save(directory/('semantic_'+str(len(captures))+'.json'),value);captures.append(value);return value
        captures=[]
        first=collect(data['notes']['maintenance'],DUTIES[0],0)
        other=[] if contrasts_only else [collect(data['notes']['maintenance'],duty,i) for i,duty in enumerate(DUTIES[1:],1)]
        scope='AB_BASELINE' if contrasts_only else 'THREE_ROLE_COMPOSITION'
        ev.phase(directory,scope+'_START',live=live)
        composition,execution=session.consume_roles([first,*other],fractal=fractal and not contrasts_only)
        ev.phase(directory,scope+'_RETURN',result_refs=composition['output']['semantic_refs'])
        if execution is not None:
            # The actual source and return remain live for the public supplied validator.
            ds=execution['source'];bundle=execution['bundle'];t=time.monotonic()
            report=k.d.validate_fractal_runtime_execution_bundle_v02(replace(bundle))
            c.require(report.status=='PASS','composition_supplied_D')
            ev.save(directory/'supplied_D.json',dict(report=ev.plain(report),seconds=time.monotonic()-t))
            bad=replace(bundle,cell_results=(replace(bundle.cell_results[0],result_id='forged:cell_result'),*bundle.cell_results[1:]))
            refusal=k.d.validate_fractal_runtime_execution_bundle_v02(bad)
            c.require(refusal.status!='PASS' and bundle.cell_results[0].result_id!='forged:cell_result','altered_D_identity_accepted')
            ev.save(directory/'D_identity_refusal.json',dict(report=ev.plain(refusal),original_id=bundle.cell_results[0].result_id))
            ev.phase(directory,'COMPOSITION_D_PROJECTION_START')
            t=time.monotonic();projection=k.d.fractal_runtime_execution_bundle_to_plain_data_v02(bundle)
            ev.save(directory/'common_D.json',projection)
            obligation=execution['obligation']
            projection_refs={name:getattr(obligation,name) for name in ('obligation_id','task_id','revision_id','work_id',
                'owning_root_id','business_request_ref','bsep_ref','semantic_proposal_ref')}
            ev.save(directory/'D_work_review.json',dict(obligation_refs=projection_refs,
                limitation='Runtime-only source_context omitted; actual current binding was validated during execution.',
                report=ev.plain(execution['report']),projection_seconds=time.monotonic()-t))
            ev.phase(directory,'COMPOSITION_D_PROJECTION_RETURN')
        second=collect(data['notes']['new_crack'],DUTIES[0],1)
        contrast,_=session.consume_roles([second])
        ab=dict(changed_dimension='source_bound_maintenance_note_only',first=first,second=second,
            first_consumed=composition['output']['checks'][0],second_consumed=contrast['output']['checks'][0],
            first_performed=c.performed_investigation(composition['output']['checks'][0]),
            second_performed=c.performed_investigation(contrast['output']['checks'][0]))
        ab['demonstrated']=ab['first_performed']!=ab['second_performed']
        ev.save(directory/'live_AB.json',ab)
        store=SentinelMemory(session.directory/'local_drs');memory_ref=store.remember(session)
        session.connectivity(False,data['tick'])
        internal=collect(data['notes']['new_crack'],DUTIES[0],1)
        offline,_=session.consume_roles([internal])
        c.require(k.mode_availability(session,'local_slm')=='UNAVAILABLE','physical_local_slm_never_present')
        before=observer.snapshot()
        # An exact captured contribution is re-executed under the same current context.
        capture_path=directory/('semantic_'+str(len(captures)-1)+'.json')
        capture_bytes=capture_path.read_bytes()
        c.require(capture_bytes==c.canonical(internal)+b'\n','persisted_capture_binding')
        captured=json.loads(capture_bytes);sem.validate_bound(captured)
        repeated,_=session.consume_roles([captured])
        captured_counts=observer.delta(before)
        c.require(captured_counts['harness_attempt']==captured_counts['harness_transport']==captured_counts['mock_effect']==0,'captured_transport')
        ev.save(directory/'captured_reexecution.json',dict(provenance='CAPTURED_REEXECUTION' if live else 'CONTROLLED_REEXECUTION',
            semantic=captured,result=repeated,counts=captured_counts,not_local_drs=True,
            capture_file=capture_path.name,capture_sha256=c.digest(capture_bytes)))
        session.capabilities.harness=False;session.capabilities.revision+=1
        if harness is not None:harness.available=False
        try:session.role_material(internal)
        except ValueError as error:withdrawal=str(error)
        else:raise ValueError('withdrawn_context_accepted')
        session.capabilities.profile='LOCAL_ALGORITHMS_ONLY';session.capabilities.revision+=1
        before=observer.snapshot()
        session.ingest([observation(v['sensor'],v['value']+10,data['tick']+15,2) for v in data['frames'] if v['sensor']!='rainfall'],data['tick']+15)
        session.intake(data['tick']+15);fresh=session.observation_work();local_counts=observer.delta(before)
        warm=SentinelMemory(session.directory/'local_drs')
        selected=warm.select(root=session.root,request=session.request,dependency=memory_dependencies(session),
            now=session.source.sample().evaluation_time)
        c.require(selected is not None and selected[1]['record_id']==memory_ref,'local_only_eligible_drs')
        session.work_mode='memory_informed'
        memory_work=session.pure_consumer('sentinel.information.v01',dict(summary=c.canonical(selected[0]).decode(),record_id=memory_ref))
        session.work_mode='deterministic'
        ev.save(directory/'local_only_drs.json',dict(cold=store.events,warm=warm.events,selected=selected,
            program=ev.plain(memory_work[0].candidate),results=ev.plain(memory_work[1]),artifact=ev.plain(memory_work[2])))
        local_counts=observer.delta(before)
        c.require(local_counts['harness_transport']==0 and local_counts['harness_attempt']==0,'local_only_transport')
        result=dict(status='LIVE_COMPLETED' if live else 'CONTROLLED_COMPLETED',scope='CONTRASTS_AND_PROFILES_ONLY' if contrasts_only else 'THREE_ROLE_AND_CONTRASTS',root=session.root,
            seconds=time.monotonic()-start,timings=session.timings,counts=observer.snapshot(),ab_demonstrated=ab['demonstrated'],
            compositions=[composition,contrast,offline],local_only=fresh,local_counts=local_counts,withdrawal=withdrawal,
            capture_count=len(captures),attempts=[] if harness is None else harness.attempts,signal=session.read_signal(),
            actual_execution_origin='CLOUD_LLM/provider_llm' if live else 'DETERMINISTIC/deterministic_runtime')
        ev.save(directory/'result.json',result)
        ev.save(directory/'cleanup.json',dict(owned_workers=0,signal=session.read_signal(),no_incident_clearance_claim=True))
        return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path);parser.add_argument('--live',action='store_true')
    parser.add_argument('--config',type=Path);parser.add_argument('--no-fractal',action='store_true')
    parser.add_argument('--contrasts-only',action='store_true')
    parser.add_argument('--experiment',type=Path)
    args=parser.parse_args();result=run(args.output,live=args.live,config=args.config,fractal=not args.no_fractal,contrasts_only=args.contrasts_only,
        experiment=None if args.experiment is None else json.loads(args.experiment.read_bytes()))
    print(json.dumps({k:result[k] for k in ('status','seconds','counts','ab_demonstrated')}))


if __name__=='__main__':main()
