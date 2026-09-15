"""Focused source, chronology, public consumer and native-boundary assertions."""
import copy
import json
import os
from pathlib import Path
import pytest
from hedgehog.domains.landslide_sentinel import contracts_v01 as c,semantic_adapter_v01 as sem,kernel_adapter_v01 as k,evidence_v01 as ev
from hedgehog.domains.landslide_sentinel.events_v01 import observation,EventBook
from hedgehog.domains.landslide_sentinel.incident_policy_v01 import Incident
from hedgehog.domains.landslide_sentinel.monitoring_runtime_v01 import ControlledEpisode


def directory(name):
    return Path(os.environ['LS2_EVIDENCE'])/'runs'/os.environ['LS2_RUN_ID']/name


def fixture():
    value=json.loads((Path(__file__).resolve().parents[1]/'fixtures/landslide_sentinel/ls1_inputs_v01.json').read_bytes())
    value['reserve_series']=[observation('reserve',v,t,i+1,lineage='independent:reserve_series') for i,(t,v) in enumerate(((100,1600),(110,1700),(120,1750)))]
    return value


def session_at(name,tick=120):
    session=ControlledEpisode(directory(name),fixture())
    session.ingest([observation(v['sensor'],v['value'],tick,1) for v in fixture()['frames']],tick)
    return session


def role(session,choice='REFERENCE_INTEGRITY',duty='LOCAL_SLOPE_ANALYST'):
    return sem.collect(session.frames,session.fixture['maintenance_note'],session.root,session.source.sample().evaluation_time,
        controlled=dict(diagnostic=choice,reason='Bounded fixture contribution.'),intended_role=duty,
        capabilities=session.capabilities.snapshot(duty),observations=tuple(session.book.latest.values()),tick=session.tick,policy=session.contract)[1]


def test_ls2r2_accepted_local_age_native_recovery():
    with ev.BoundaryObserver() as observer:
        s=session_at('r2_age',0)
        s.ingest([observation(ch,6000,0,2) for ch in ('displacement','reserve')],0)
        assert s.evaluate_local()['new_incident'] and s.read_signal()['signal']
        s.update_policy(dict(s.contract,max_local_age_seconds=2));rows=[]
        for measured,received in ((15,20),(30,35),(45,50)):
            s.ingest([observation(ch,350,measured,measured+2,received=received) for ch in ('displacement','reserve')],received)
            value=s.evaluate_local();rows.append(value)
            assert not value['clearance'] and value['reason']=='measurement_stale_for_critical' and s.read_signal()['signal']
        stale_effects=len(s.effects)
        for measured in (60,75,90):
            s.ingest([observation(ch,350,measured,measured+2,received=measured+2) for ch in ('displacement','reserve')],measured+2)
            value=s.evaluate_local();rows.append(value)
        assert value['clearance'] and min(value['measured_spans'].values())==30
        assert len(s.effects)==stale_effects+1 and not s.read_signal()['signal']
        assert s.contract['max_local_age_seconds']==2 and observer.snapshot()['public_D']==observer.snapshot()['public_E']==0
        ev.save(s.directory/'result.json',dict(rows=rows,policy=s.contract,effects=s.effects,readback=s.read_signal(),counts=observer.snapshot()))


def test_ls2r2_age_boundary_and_looser_policy():
    from hedgehog.domains.landslide_sentinel.incident_policy_v01 import features,local_pair
    outcomes=[]
    for limit,age in ((2,2),(2,3),(10,10),(10,11),(12,11),(12,12),(12,13)):
        book=EventBook();book.ingest([observation(ch,6000,100,1,received=100+age) for ch in ('displacement','reserve')],100+age)
        policy=dict(c.POLICY,max_local_age_seconds=limit)
        frames=[dict(sensor=v['channel'],value=v['value'],unit=v['unit'],scenario_tick=v['observed_end'],healthy=True,calibration=v['calibration']) for v in book.latest.values()]
        assert c.critical(frames,book.tick,policy)==(age<=limit)
        for purpose in ('critical','recovery'):
            if age<=limit:
                assert features(book,purpose,policy)['hard_critical'];assert len(local_pair(book,purpose,policy))==2
            else:
                with pytest.raises(ValueError,match='measurement_stale_for_'+purpose):features(book,purpose,policy)
        assert c.critical(frames,book.tick)==(age<=10)
        outcomes.append(dict(limit=limit,age=age,eligible=age<=limit))
    ev.save(directory('age_boundaries.json'),outcomes)


def test_ls2r2_duty_requirements_and_interval_work():
    with ev.BoundaryObserver() as observer:
        s=session_at('duty_interval',3720);rows=[]
        def consume(choice,duty='CLOUD_ENVIRONMENTAL_ANALYST',observations=None):
            value=(role(s,choice,duty) if observations is None else sem.collect(s.frames,s.fixture['maintenance_note'],
                s.root,s.source.sample().evaluation_time,controlled=dict(diagnostic=choice,reason='Controlled bounded evidence.'),
                intended_role=duty,capabilities=s.capabilities.snapshot(duty),observations=observations,tick=s.tick,policy=s.contract)[1])
            result,_=s.consume_roles([value]);rows.append(result);return result['output']['checks'][0]
        point=consume('TEMPORAL_CONTEXT_APPLICABILITY')
        assert not point['healthy'] and 'HOURLY_INTERVAL_DURATION_MISMATCH' in point['detail']['findings'][0]['reasons']
        unknown=consume('TEMPORAL_CONTEXT_APPLICABILITY',observations=())
        assert not unknown['healthy'] and unknown['detail']['findings'][0]['status']=='MISSING'
        s.ingest([observation('rainfall',12000,3720,2,observed_start=120)],3720)
        valid=consume('TEMPORAL_CONTEXT_APPLICABILITY');assert valid['healthy']
        gaps=consume('EVIDENCE_GAPS');assert gaps['healthy']
        assert not any('PHYSICAL' in reason for finding in gaps['detail']['findings'] for reason in finding['reasons'])
        spatial=consume('SPATIAL_CONTEXT_APPLICABILITY')
        assert spatial['detail']['physical_applicability']=='UNRESOLVED_NO_VERIFIED_MAPPING'
        missing=consume('EVIDENCE_GAPS','LOCAL_SLOPE_ANALYST',observations=(s.book.latest['displacement'],))
        assert not missing['healthy'] and any('REQUIRED_CURRENT_CHANNEL_MISSING' in v['reasons'] for v in missing['detail']['findings'])
        supplied=consume('EVIDENCE_GAPS','LOCAL_SLOPE_ANALYST');assert supplied['healthy']
        assert supplied['detail']['physical_zero_check']=='NOT_ESTABLISHED'
        assert observer.snapshot()['series_read']==observer.snapshot()['mock_effect']==0
        assert all(v['plan_root']['decision']=='ACCEPT' and v['root']['decision']=='ACCEPT' for v in rows)
        ev.save(s.directory/'result.json',dict(cases=rows,counts=observer.snapshot()))


def test_ls2r2_interval_contract_edges():
    base=observation('rainfall',12000,3720,1,observed_start=120)
    cases=[]
    for name,record,tick,expected in (
        ('supported',base,3720,'SUPPORTED'),('boundary',base,3780,'SUPPORTED'),
        ('historical_fresh_transport',dict(base,received=3781),3781,'UNRESOLVED'),
        ('unknown_start',dict(base,observed_start=None),3720,'MISSING'),
        ('point_hourly',dict(base,observed_start=3720),3720,'INCOMPATIBLE'),
        ('future',dict(base,received=3721),3720,'INCOMPATIBLE'),
        ('unknown_statistic',dict(base,statistic='unconfirmed'),3720,'INCOMPATIBLE'),
        ('wrong_units',dict(base,unit='unknown'),3720,'INCOMPATIBLE')):
        actual=c.temporal_findings([record],tick)[0]
        assert actual['status']==expected
        cases.append(dict(case=name,actual=actual,scope='PURE_DOMAIN_INTERVAL_CONSUMER_NOT_NEW_SOURCE_AUTHORITY'))
    ev.save(directory('interval_edges.json'),cases)


def test_ls2r2_investigation_binding_and_substantive_controls():
    with ev.BoundaryObserver() as observer:
        s=session_at('investigation_bindings');rows=[]
        for choice in ('REFERENCE_INTEGRITY','INDEPENDENT_RESERVE_SERIES'):
            value=role(s,choice);material=s.role_material(value);before=observer.snapshot()
            bad=copy.deepcopy(material);bad['checks'][0]['investigation']['target']='FOREIGN_TARGET'
            with pytest.raises(ValueError,match='semantic_investigation_binding'):sem.validate_current(bad,s)
            bad_value=copy.deepcopy(value);bad_value['response']['source_refs']=['foreign_source']
            with pytest.raises(ValueError):s.consume_roles([bad_value])
            bad_value=copy.deepcopy(value);bad_value['response']['target']='unadmitted'
            with pytest.raises(ValueError,match='semantic_shape'):s.consume_roles([bad_value])
            assert observer.delta(before)['series_read']==observer.delta(before)['mock_effect']==0
            result,_=s.consume_roles([value]);rows.append(result)
        a,b=[v['output']['checks'][0] for v in rows]
        assert a['investigation']['target']!=b['investigation']['target']
        assert c.performed_investigation(a)!=c.performed_investigation(b)
        relabelled=copy.deepcopy(a);relabelled['selection']='EVIDENCE_GAPS'
        relabelled['investigation']=c.investigation('EVIDENCE_GAPS','LOCAL_SLOPE_ANALYST')
        assert c.performed_investigation(a)==c.performed_investigation(relabelled)
        assert 'findings' in a['detail'] and 'sample_ids' in b['detail'] and b['detail']['fitness']=='ELIGIBLE'
        assert observer.snapshot()['series_read']==1
        assert all(v['material']['checks'][0]['investigation']==v['output']['checks'][0]['investigation'] for v in rows)
        phases=[json.loads(line) for line in (s.directory/'phases.jsonl').read_text().splitlines()]
        read=next(i for i,v in enumerate(phases) if v['phase']=='ACTUAL_REVIEWED_SERIES_READ')
        assert any(v['phase']=='CURRENT_WORK_ROOT_ACCEPTED' and v['stage']=='PLAN' for v in phases[:read])
        assert any(v['phase']=='CURRENT_WORK_ROOT_ACCEPTED' and v['stage']=='RESULT' for v in phases[read+1:])
        ev.save(s.directory/'result.json',dict(alternatives=rows,counts=observer.snapshot()))


def test_ls2r_recovery_stable_dependency_changes():
    with ev.BoundaryObserver() as observer:
        for changed in ('calibration','lineage'):
            s=session_at('f1_'+changed,0);history=[]
            def pair(t,seq,calibration=None,lineage=None,high=False):
                s.ingest([observation(ch,6000 if high else 350,t,seq,calibration=calibration,
                    lineage=(lineage if ch=='reserve' else None)) for ch in ('displacement','reserve')],t)
                result=s.evaluate_local();history.append(result);return result
            pair(0,2,high=True);pair(15,3);pair(30,4)
            old=tuple(s.book.history)
            if changed=='calibration':s.update_policy(dict(s.contract,calibration='calibration:sentinel:v02'))
            kw=dict(calibration=s.contract['calibration'],lineage='independent:replacement' if changed=='lineage' else None)
            value=pair(45,5,**kw);assert not value['clearance'] and s.read_signal()['signal']
            before=len(s.executed)
            with pytest.raises(ValueError,match='root_refusal'):
                s.command(dict(op='SET_LOCAL_SIGNAL_STATE',state='OFF',basis_ref=c.identity('mixed_clearance',value)),
                    dict(current_coverage=value['clearance']))
            assert len(s.executed)==before and s.book.history[:len(old)]==list(old)
            pair(60,6,**kw);value=pair(75,7,**kw)
            assert value['clearance'] and not s.read_signal()['signal'] and len(s.incident.revoked_coverage)==1
            ev.save(s.directory/'result.json',dict(assessments=history,revoked=s.incident.revoked_coverage,
                effects=s.effects,readback=s.read_signal(),counts=observer.snapshot()))


def test_ls2r_current_policy_pending_and_next_intake():
    with ev.BoundaryObserver() as observer:
        s=session_at('f2_current',0)
        old=s.prepare_config();assert len(s.executed)==0
        s.update_policy(dict(s.contract,rain_fast_mm_x1000=10000))
        with pytest.raises(ValueError,match='host_current_action_not_executable'):s.dispatch_pending()
        assert len(s.executed)==0
        fresh=s.prepare_config();assert fresh!=old
        receipt=s.dispatch_pending();assert s.cadence_seconds==15 and s.next_intake==15
        assert s.intake(14) is None
        intake=s.intake(15);assert intake['scenario_tick']==15 and intake['cadence_seconds']==15
        policy=dict(s.contract)
        with pytest.raises(ValueError,match='unsupported_cadence_policy'):s.update_policy(dict(policy,fast_cadence_seconds=5))
        assert s.contract==policy
        ev.save(s.directory/'result.json',dict(old_packet=old,new_packet=fresh,receipt=ev.plain(receipt),
            intake=intake,policy=policy,counts=observer.snapshot()))


def test_ls2r_plan_before_read_and_exact_duplicate():
    from dataclasses import replace
    with ev.BoundaryObserver() as observer:
        s=session_at('f4_order');bootstrap=s.program;value=role(s,'INDEPENDENT_RESERVE_SERIES')
        before=observer.snapshot();material=s.role_material(value);sem.validate_current(material,s)
        assert observer.delta(before)['series_read']==0
        bad=copy.deepcopy(role(s,duty='ADVERSARIAL_SENSOR_REVIEWER'));bad['response']['source_refs']=['foreign']
        with pytest.raises(ValueError):s.consume_roles([value,bad])
        assert observer.delta(before)['mock_effect']==0
        basis,_=s.plan_roles([value]);assert observer.delta(before)['series_read']==0 and s.program is bootstrap
        refused=replace(basis,review=(*basis.review[:2],replace(basis.review[2],decision='REJECT')))
        with pytest.raises(ValueError):s.execute_role_plan(refused)
        assert observer.delta(before)['series_read']==0
        result=s.execute_role_plan(basis)
        assert result['output']['checks'][0]['detail']['fitness']=='ELIGIBLE'
        assert observer.delta(before)['series_read']==1 and s.program is bootstrap
        read=result['material']['checks'][0]['series'];assert read['plan_basis']['bsep_ref']==basis.program.candidate.bsep_ref
        assert read['plan_basis']['work_artifact_ref']==basis.artifact.artifact_id
        baseline=observer.snapshot();again,_=s.consume_roles([json.loads(c.canonical(value))])
        assert observer.delta(baseline)['series_read']==observer.delta(baseline)['mock_effect']==0
        assert again['material']['checks'][0]['series']['receipt_ref']==read['receipt_ref']
        phases=[json.loads(line) for line in (s.directory/'phases.jsonl').read_text().splitlines()]
        accepted=next(i for i,v in enumerate(phases) if v['phase']=='CURRENT_WORK_ROOT_ACCEPTED' and v['stage']=='PLAN')
        acquired=next(i for i,v in enumerate(phases) if v['phase']=='ACTUAL_REVIEWED_SERIES_READ')
        consumed=next(i for i,v in enumerate(phases) if v['phase']=='CURRENT_WORK_ROOT_ACCEPTED' and v['stage']=='RESULT')
        assert accepted<acquired<consumed
        ev.save(s.directory/'result.json',dict(first=result,duplicate=again,order=[accepted,acquired,consumed],counts=observer.snapshot()))


def test_ls2r_plan_invalidated_before_read():
    with ev.BoundaryObserver() as observer:
        records=[]
        for dimension in ('calibration','source','capability'):
            s=session_at('f4_change_'+dimension);basis,_=s.plan_roles([role(s,'INDEPENDENT_RESERVE_SERIES')]);before=observer.snapshot()
            if dimension=='calibration':s.update_policy(dict(s.contract,calibration='calibration:sentinel:v02'))
            elif dimension=='source':s.fixture['reserve_series'][0]=observation('reserve',1999,100,1,lineage='independent:reserve_series')
            else:s.connectivity(False,s.tick)
            with pytest.raises(ValueError,match='reviewed_work_current_dependencies') as error:s.execute_role_plan(basis)
            counts=observer.delta(before);assert counts['series_read']==counts['mock_effect']==0
            records.append(dict(dimension=dimension,reason=str(error.value),counts=counts))
        ev.save(directory('f4_change_results.json'),records)


def test_ls2r_series_fitness_actual_consumers():
    with ev.BoundaryObserver() as observer:
        s=session_at('f4_fitness');cases=[]
        for name,changes in (('correlated',dict(lineage='independent:displacement')),
            ('calibration',dict(calibration='calibration:sentinel:v02')),('short_window',{}),('valid',{})):
            times=(118,119,120) if name=='short_window' else (100,110,120)
            s.fixture['reserve_series']=[observation('reserve',1600+i*50,t,i+1,
                **dict(dict(lineage='independent:reserve_series'),**changes)) for i,t in enumerate(times)]
            result,_=s.consume_roles([role(s,'INDEPENDENT_RESERVE_SERIES')])
            detail=result['output']['checks'][0]['detail']
            assert (detail['fitness']=='ELIGIBLE')==(name=='valid')
            cases.append(dict(case=name,result=result))
        ev.save(s.directory/'result.json',dict(cases=cases,counts=observer.snapshot()))


def test_ls2r_environmental_choice_changes_actual_work():
    with ev.BoundaryObserver() as observer:
        s=session_at('f3_environmental');results=[]
        for choice in ('TEMPORAL_CONTEXT_APPLICABILITY','SPATIAL_CONTEXT_APPLICABILITY'):
            value=role(s,choice,'CLOUD_ENVIRONMENTAL_ANALYST')
            assert not any('note' in v for v in value['context']['sources'].values())
            result,_=s.consume_roles([value]);results.append(result)
        a,b=[v['output']['checks'][0] for v in results]
        assert a['selection']!=b['selection'] and 'measured' in a['detail'] and 'sites' in b['detail']
        assert observer.snapshot()['series_read']==0
        ev.save(s.directory/'result.json',dict(alternatives=results,counts=observer.snapshot()))


def test_r1_measured_recovery_native_refusal():
    with ev.BoundaryObserver() as observer:
        session=session_at('r1',0)
        def pair(observed,received,seq,high=False,reserve_observed=None):
            session.ingest([observation('displacement',6200 if high else 400,observed,seq,received=received),
                observation('reserve',5800 if high else 350,observed if reserve_observed is None else reserve_observed,seq,received=received)],received)
            return session.evaluate_local()
        pair(0,0,2,True)
        for t,r,s in ((15,15,3),(30,30,4),(35,45,5)):value=pair(t,r,s)
        assert not value['clearance'] and min(value['measured_spans'].values())==20 and session.signal
        count=len(session.executed)
        with pytest.raises(ValueError,match='root_refusal'):
            session.command(dict(op='SET_LOCAL_SIGNAL_STATE',state='OFF',basis_ref=c.identity('delayed',value)),
                dict(measured_clearance=value['clearance'],active=session.incident.state=='ACTIVE'))
        assert len(session.executed)==count and session.read_signal()['signal']
        for t,s in ((60,6),(75,7),(90,8)):value=pair(t,t,s)
        assert value['clearance'] and not session.read_signal()['signal']
        ev.save(session.directory/'result.json',dict(assessment=value,effects=session.effects,counts=observer.snapshot(),history=[json.loads(v) for v in session.book.history]))


def test_r2_r3_current_source_and_negative_mix():
    with ev.BoundaryObserver() as observer:
        session=session_at('r2_r3')
        value=role(session);material=session.role_material(value)
        assert value['site_cloud_available'] and value['remote_rainfall_available']
        assert 'rainfall' in value['context']['not_included_channels']
        bootstrap,_=k.semantic_source(session.request,session.id,session.root,session.source.sample().evaluation_time,session.semantic_responses[0])
        with pytest.raises(ValueError,match='stale_bootstrap_bsep'):
            session.pure_consumer('sentinel.diagnostic.v01',material,semantic_source_override=bootstrap)
        result,_=session.consume_roles([value])
        assert result['output']['semantic_refs']==[value['contribution']['contribution_id']]
        assert result['program']['bsep_ref']!=bootstrap.bsep_packet['packet_id']
        session.connectivity(False,120)
        with pytest.raises(ValueError,match='role_current_context'):session.role_material(value)
        fresh=role(session);assert not fresh['site_cloud_available']
        for key,val in (('authority',True),('command','ON')):
            bad=dict(fresh['response'],**{key:val})
            with pytest.raises(ValueError,match='semantic_shape'):sem.validate_response(bad,fresh['context'])
        for refs in ([],['foreign:ref']):
            with pytest.raises(ValueError):sem.validate_response(dict(fresh['response'],source_refs=refs),fresh['context'])
        ev.save(session.directory/'result.json',dict(current=value,consumed=result,offline=fresh,counts=observer.snapshot()))


def test_chronology_projection_and_types():
    session=session_at('projection',0)
    old=c.canonical(session.frames)
    with pytest.raises(ValueError):session.ingest([observation('reserve',500,5,2,received=4)],4)
    assert c.canonical(session.frames)==old and session.tick==0
    session.ingest([observation('reserve',None,5,2,status='MISSING')],5)
    assert not any(v['sensor']=='reserve' for v in session.frames)
    assert not session.evaluate_local()['new_incident']
    for value in (True,float('nan'),1.5):
        with pytest.raises(ValueError):observation('reserve',value,5,3)
    wrong=observation('reserve',400,5,3,site='foreign')
    with pytest.raises(ValueError):session.ingest([wrong],5)
    ev.save(session.directory/'result.json',dict(frames=session.frames,latest=session.book.latest))


def test_c02_c03_c04_current_observability():
    from hedgehog.domains.landslide_sentinel.contrasts_v01 import context_status
    with ev.BoundaryObserver() as observer:
        session=session_at('c02_c03_c04',120)
        old=observation('rainfall',2000,0,2,received=120)
        correction=observation('rainfall',3000,0,3,received=120)
        book=EventBook();book.ingest([old],120);history=book.history[0];book.ingest([correction],120)
        assert book.history[0]==history and context_status(correction,120,session.fixture['site'])['status']=='HISTORICAL_OR_INAPPLICABLE'
        session.ingest([observation('displacement',None,120,2,status='MISSING')],120)
        limited=session.observation_work();assert limited['result']['observability']=='LIMITED' and not limited['result']['hard_critical']
        session.ingest([observation('reserve',None,120,2,status='MISSING')],120)
        absent=session.observation_work();assert absent['result']['observability']=='INSUFFICIENT'
        with pytest.raises(ValueError,match='root_refusal'):
            session.command(dict(op='SET_LOCAL_SIGNAL_STATE',state='ON',basis_ref=c.identity('absent',absent)),dict(hard_floor=absent['result']['hard_critical']))
        copies=[observation(ch,6000,120,3,lineage='same:upstream') for ch in ('reserve','displacement')]
        session.ingest(copies,120);duplicate=session.observation_work()
        assert not duplicate['result']['hard_critical']
        original=c.canonical(session.book.latest)
        session.ingest(copies[::-1],120);assert c.canonical(session.book.latest)==original
        with pytest.raises(ValueError):session.ingest([observation('reserve',100,119,4)],120)
        fresh=[observation(ch,6000,120,4) for ch in ('displacement','reserve')]
        session.ingest(fresh,120);positive=session.observation_work();assert positive['result']['hard_critical']
        ev.save(session.directory/'result.json',dict(old=old,correction=correction,history=[json.loads(v) for v in book.history],
            limited=limited,absent=absent,duplicates=duplicate,independent=positive,counts=observer.snapshot()))


def test_c05_budget_actual_work():
    from hedgehog.domains.landslide_sentinel.contrasts_v01 import optional_diagnostics
    results=[]
    with ev.BoundaryObserver() as observer:
        session=session_at('c05_same_session');original=c.canonical(session.frames);spent=[]
        for units in (2,1,0):
            before=observer.snapshot()
            if units:
                result=optional_diagnostics(session,units)
                assert len(result['outputs'])==units and all(v['program']['budget']['max_compute_units']==units for v in result['outputs'])
                assert all(v['program']['task_id']==session.id for v in result['outputs'])
            else:
                with pytest.raises(ValueError) as error:optional_diagnostics(session,0)
                result=dict(refusal=str(error.value))
            spent.append(session.budgets.tasks['pure_work']['spent'])
            assert c.canonical(session.frames)==original
            results.append(dict(units=units,result=result,counts=observer.delta(before)))
        assert spent==[2,3,4]
        ev.save(directory('c05_result.json'),results)


def test_c06_pending_critical_and_c09_delivery():
    from hedgehog.domains.landslide_sentinel.monitoring_runtime_v01 import clock_args
    from hedgehog import work_execution_host_v01 as hosts
    from hedgehog.domains.landslide_sentinel.outbox_v01 import Receiver
    with ev.BoundaryObserver() as observer:
        for offline in (False,True):
            session=session_at('pending_'+str(offline),0);session.start_optional()
            try:
                if offline:session.connectivity(False,5)
                session.ingest([observation(ch,6000,15,2) for ch in ('displacement','reserve')],15)
                session.evaluate_local();assert session.signal and not session.pending_return
                before=len(session.executed);old_packet=session.on_effect['packet_id']
                with pytest.raises(ValueError):hosts.dispatch_current_action_v01(session.host,packet_id=old_packet,task_id=session.id,
                    expected_revision=session.host.revision,**clock_args(session.source.sample()))
                assert len(session.executed)==before
                raw=session.outbox.read(session.message['message_id'])
                session.connectivity(True,16);session.deliver();session.deliver()
                assert raw==session.outbox.read(session.message['message_id']) and len(list(session.receiver.directory.glob('*.json')))==1
                class MissingAck(Receiver):
                    def receive(self,ref,raw):super().receive(ref,raw);return None
                with pytest.raises(ValueError):session.outbox.deliver(session.message['message_id'],MissingAck(session.directory/'uncertain'))
                assert session.outbox.trail[-1]['state']=='UNKNOWN'
            finally:session.release_optional()
            assert session.signal and session.incident.state=='ACTIVE'
            assert session.on_completed['monotonic']<session.pending_return[0]['monotonic']
            ev.save(session.directory/'result.json',dict(effects=session.effects,signal=session.read_signal(),trail=session.outbox.trail,
                pending=session.pending_return,budgets=session.budgets.tasks,counts=observer.snapshot()))


def test_c08_additional_channels_same_root():
    with ev.BoundaryObserver() as observer:
        session=session_at('c08',0);root=session.root;host=session.host
        assert not session.evaluate_local()['hard_critical']
        session.ingest([observation('channel_level',600,0,1),observation('vibration',800,0,1)],0)
        result=session.evaluate_channel()
        assert result['work']['result']['hard_critical'] and session.signal and session.root==root and session.host is host
        ev.save(session.directory/'result.json',dict(result=result,counts=observer.snapshot()))


def test_c10_memory_revisions_and_current_consumption():
    from hedgehog.domains.landslide_sentinel.monitoring_runtime_v01 import SentinelMemory,memory_dependencies
    with ev.BoundaryObserver() as observer:
        session=session_at('memory',0);store=SentinelMemory(session.directory/'drs');ref=store.remember(session)
        results=[]
        for tick in (0,15):
            if tick:session.ingest([observation(ch,500,tick,2) for ch in ('displacement','reserve')],tick)
            fresh=SentinelMemory(session.directory/'drs');before=observer.snapshot()
            selected=fresh.select(root=session.root,request=session.request,dependency=memory_dependencies(session),now=session.source.sample().evaluation_time)
            assert selected is not None
            session.work_mode='memory_informed'
            work=session.pure_consumer('sentinel.information.v01',dict(summary=c.canonical(selected[0]).decode(),record_id=ref))
            session.work_mode='deterministic'
            delta=observer.delta(before)
            assert all(delta[k]==0 for k in ('harness_attempt','harness_transport','sensor_attempt','mock_effect'))
            results.append(dict(events=fresh.events,result=ev.plain(work[1]),counts=delta))
        old_policy=dict(session.contract)
        for field,value in (('version','sentinel.policy.v02'),('calibration','calibration:sentinel:v02')):
            session.update_policy(dict(old_policy,**{field:value}))
            fresh=SentinelMemory(session.directory/'drs')
            rejected=fresh.select(root=session.root,request=session.request,dependency=memory_dependencies(session),now=session.source.sample().evaluation_time)
            assert rejected is None
            reviewed=session.observation_work();assert reviewed['result']['policy']==session.contract
            results.append(dict(changed=field,events=fresh.events,fresh_review=reviewed,path='FRESH_EXECUTION_NOT_DELTA_PASS'))
        ev.save(session.directory/'result.json',dict(results=results,counts=observer.snapshot()))


def test_reviewer_controlled_extra_field_refused():
    session=session_at('reviewer_extra')
    with pytest.raises(ValueError,match='controlled_response_shape'):
        sem.collect(session.frames,session.fixture['maintenance_note'],session.root,session.source.sample().evaluation_time,
            controlled=dict(diagnostic='REFERENCE_INTEGRITY',reason='Shape probe.',authority_creation={'may_commit':True}),
            intended_role='LOCAL_SLOPE_ANALYST',capabilities=session.capabilities.snapshot('LOCAL_SLOPE_ANALYST'),
            observations=tuple(session.book.latest.values()),tick=session.tick)


def test_reviewer_fresh_capture_old_local_refused():
    session=session_at('reviewer_old',210)
    session.ingest([observation(ch,1500,210,2,received=271) for ch in ('displacement','reserve')],271)
    value=role(session)
    material=dict(selection=value['response']['diagnostic'],frames=session.frames,contract=session.contract,phase='PLAN',
        semantic_bindings=[value],checks=[dict(selection=value['response']['diagnostic'],semantic_ref=value['contribution']['contribution_id'],
            tick=session.tick,site=session.fixture['site'],observations=sorted((v for v in value['context']['sources'].values() if 'observation_id' in v),key=lambda v:v['observation_id']),series=None,
            investigation=c.investigation(value['response']['diagnostic'],value['context']['duty']))])
    sem.validate_bound(value);sem.validate_material(material)
    before=c.canonical(material)
    with pytest.raises(ValueError,match='semantic_stale_local_measurement'):sem.validate_current(material,session)
    with pytest.raises(ValueError,match='semantic_stale_local_measurement'):session.role_material(value)
    assert c.canonical(material)==before and not session.effects


def test_c02_historical_context_actual_consumer():
    with ev.BoundaryObserver() as observer:
        session=session_at('c02_consumer',3720)
        session.ingest([observation('rainfall',12000,3720,2,observed_start=120)],3720)
        session.fixture['maintenance_note']=dict(text='Synthetic gauge log, version1.',observed_at=3720,received_at=3720,
            site=session.fixture['site'],source='synthetic_gauge_log')
        first=role(session,'TEMPORAL_CONTEXT_APPLICABILITY','CLOUD_ENVIRONMENTAL_ANALYST')
        current,_=session.consume_roles([first]);assert current['output']['checks'][0]['healthy']
        frozen=c.canonical(current);results=[current]
        for tick,sequence,value in ((3840,3,2000),(3850,4,3000)):
            session.ingest([observation('rainfall',value,3720,sequence,received=tick,observed_start=120)],tick)
            bound=role(session,'TEMPORAL_CONTEXT_APPLICABILITY','CLOUD_ENVIRONMENTAL_ANALYST')
            result,_=session.consume_roles([bound]);assert not result['output']['checks'][0]['healthy']
            results.append(result)
        assert c.canonical(current)==frozen and not session.effects
        ev.save(session.directory/'result.json',dict(results=results,history=[json.loads(v) for v in session.book.history],counts=observer.snapshot()))


def test_ea_normalization_interval_controls():
    from hedgehog.domains.landslide_sentinel.rainfall_adapter_v01 import normalize,aggregate
    measure={'@id':'controlled:ea:measure','parameter':'rainfall','unitName':'mm','period':900,'valueType':'total'}
    rows=[normalize(measure,dict(measure=measure['@id'],dateTime=stamp,value=value,**{'@id':'controlled:'+stamp}),3600,
        interval_semantics='CONTROLLED_END_LABEL')
        for stamp,value in (('1970-01-01T00:15:00Z',0.1235),('1970-01-01T00:30:00Z',0.1255),('1970-01-01T00:45:00Z',0))]
    assert [v['value'] for v in rows]==[124,126,0] and aggregate(rows)['total_mm_x1000']==250
    unknown=normalize(measure,dict(measure=measure['@id'],dateTime='1970-01-01T00:15:00Z',value=0),3600)
    assert unknown['observed_start'] is unknown['observed_end'] is None and unknown['value']==0
    with pytest.raises(ValueError,match='ea_interval_unconfirmed'):aggregate([unknown])
    for bad in ([rows[0],rows[0]], [rows[0],rows[2]], [rows[0],dict(rows[1],observed_start=800,observed_end=1700)]):
        with pytest.raises(ValueError):aggregate(bad)
    for value in (True,'NaN',None):
        with pytest.raises(ValueError):normalize(measure,dict(measure=measure['@id'],dateTime='1970-01-01T00:15:00Z',value=value),3600)
    with pytest.raises(ValueError):normalize(dict(measure,valueType='instantaneous'),dict(measure=measure['@id'],dateTime='1970-01-01T00:15:00Z',value=1),3600)
    ev.save(directory('ea_controls.json'),dict(classification='CONTROLLED_NORMALIZER_TEST_NOT_ACTUAL_EA_READING',rows=rows,total=aggregate(rows)))


def test_expired_packet_and_receipt_not_authority():
    from hedgehog import work_execution_host_v01 as hosts
    from hedgehog.domains.landslide_sentinel.monitoring_runtime_v01 import clock_args
    session=session_at('expired',0);session.prepare_config();receipt=session.dispatch_pending()
    before=len(session.executed)
    with pytest.raises(KeyError) as receipt_error:
        hosts.dispatch_current_action_v01(session.host,packet_id=receipt.artifact_id,task_id=session.id,
            expected_revision=session.host.revision,**clock_args(session.source.sample()))
    assert receipt_error.value.args == (receipt.artifact_id,)
    session.ingest([observation('rainfall',31000,15,2)],15);session.prepare_config()
    session.source.offset+=3601
    with pytest.raises(ValueError) as expired_error:session.dispatch_pending()
    assert len(session.executed)==before
    ev.save(session.directory/'result.json',dict(receipt_as_packet=str(receipt_error.value),expired=str(expired_error.value),effect_delta=0,
        time_semantics='Explicit trusted mock clock offset; not an external clock attestation.'))


def test_semantic_source_order_survives_canonical_work_literal():
    session=session_at('source_order',810)
    session.ingest([observation(ch,value,810,2) for ch,value in (('displacement',1710),('reserve',1880),('rainfall',33300))],810)
    value=role(session,duty='ADVERSARIAL_SENSOR_REVIEWER');material=session.role_material(value)
    sem.validate_material(json.loads(c.canonical(material)))
    result,_=session.consume_roles([value])
    assert result['output']['semantic_refs']==[value['contribution']['contribution_id']]
    changed=json.loads(c.canonical(material));changed['checks'][0]['observations'][0]['value']+=1
    with pytest.raises(ValueError,match='semantic_work_source_mix'):sem.validate_material(changed)
    ev.save(session.directory/'result.json',dict(material=material,consumed=result))
