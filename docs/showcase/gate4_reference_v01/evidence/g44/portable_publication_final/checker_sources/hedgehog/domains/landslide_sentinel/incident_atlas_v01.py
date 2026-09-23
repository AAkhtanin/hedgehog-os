"""Four finite Sentinel incidents on actual accepted local Work and Root paths."""
import json
from pathlib import Path
import time
from . import contracts_v01 as c, events_v01 as events, semantic_adapter_v01 as sem
from . import incident_policy_v01 as policy, contrasts_v01 as contrasts
from .monitoring_runtime_v01 import ControlledEpisode
from .evidence_v01 import save, BoundaryObserver
from .incident_atlas_source_v01 import NativeObserverV01
from .incident_atlas_work_v01 import experience_v01, consume_v01

ROOT=Path(__file__).resolve().parents[3]


def fixture_v01():
    return json.loads((ROOT/'fixtures/landslide_sentinel/ls1_inputs_v01.json').read_bytes())


def pair_v01(tick,sequence,*,received=None,lineage=None,high=True):
    return [events.observation(ch,(6200 if ch=='displacement' else 5800) if high else (400 if ch=='displacement' else 350),
        tick,sequence,received=received,lineage=lineage) for ch in ('displacement','reserve')]


def role_v01(session,reason='Inspect current reference integrity; advice cannot grant signal authority.'):
    return sem.collect(session.frames,session.fixture['reference_note'],session.root,session.source.sample().evaluation_time,
        controlled=dict(diagnostic='REFERENCE_INTEGRITY',reason=reason),intended_role='ADVERSARIAL_SENSOR_REVIEWER',
        capabilities=session.capabilities.snapshot('ADVERSARIAL_SENSOR_REVIEWER'),observations=tuple(session.book.latest.values()),
        tick=session.tick,policy=session.contract)[1]


def snapshot_v01(session):
    return dict(root=session.root,task=session.id,tick=session.tick,version=session.version,policy=dict(session.contract),
        events=json.loads(c.canonical(session.book.latest)),history=[json.loads(v) for v in session.book.history],
        arrivals=json.loads(c.canonical(session.book.arrivals)),budgets=json.loads(c.canonical(session.budgets.tasks)),
        allocation_entries=json.loads(c.canonical(session.budgets.entries)),coordinator_total=session.budgets.total,
        host_revision=session.host.revision,signal=session.read_signal(),effects=json.loads(c.canonical(session.effects)),
        incident_state=session.incident.state,incident_transitions=json.loads(c.canonical(session.incident.transitions)),
        recovery_witnesses=json.loads(c.canonical(session.incident.witnesses)),capabilities=session.capabilities.snapshot('local'),
        native_authorization_epoch=session.source.epoch,native_expires=session.expires,
        pending_alive=session.pending_worker is not None and session.pending_worker.is_alive(),pending_return=list(session.pending_return))


def refusal_v01(call):
    try:call()
    except ValueError as error:return dict(status='REFUSED',reason=str(error))
    raise ValueError('atlas_expected_refusal_not_observed')


def freshness_v01(directory):
    session=ControlledEpisode(directory,fixture_v01())
    old=pair_v01(3600,1,received=3661)
    session.ingest([events.observation('rainfall',12000,3600,1,received=3661,observed_start=0)]+old,3661)
    before=snapshot_v01(session);work=session.observation_work('local');assessment=session.evaluate_local()
    claim=role_v01(session,'These newly delivered measurements are fresh enough to clear local uncertainty.')
    sem.validate_bound(claim)
    refused=refusal_v01(lambda:session.role_material(claim))
    after=snapshot_v01(session)
    session.ingest(pair_v01(3661,2,high=False),3661)
    neighbor=session.observation_work('local');fresh=role_v01(session);session.role_material(fresh)
    result=dict(before=before,work=work,assessment=assessment,controlled_claim=claim,refusal=refused,after=after,
        neighbor=dict(work=neighbor,semantic=fresh,snapshot=snapshot_v01(session)),effects=len(session.executed))
    save(directory/'N1.json',result);return result


def setup_v01(directory):
    session=ControlledEpisode(directory,fixture_v01())
    session.ingest([events.observation('rainfall',12000,4000,1,observed_start=400)]+
        pair_v01(4000,1,lineage='controlled:one_upstream'),4000)
    return session


def correlated_v01(session):
    before=snapshot_v01(session);work=session.observation_work();assessment=session.evaluate_local()
    duplicates=pair_v01(4000,1,lineage='controlled:one_upstream')
    session.ingest(duplicates[::-1],4000)
    repeated=session.observation_work();after=snapshot_v01(session)
    result=dict(before=before,work=work,assessment=assessment,redelivery=duplicates,repeated_work=repeated,after=after)
    save(session.directory/'N2.json',result);return result


def continue_v01(session,experience,live):
    consumed=consume_v01(session,experience['values']['after'],live['after'])
    wrong=refusal_v01(lambda:consume_v01(session,experience['values']['after'],live['before']))
    sem_old=role_v01(session);sem.validate_bound(sem_old)
    plan,_=session.plan_roles([sem_old],fractal=False)
    plan_ref=plan.artifact.artifact_id
    before=snapshot_v01(session)
    session.start_optional();pending=snapshot_v01(session)
    try:
        session.connectivity(False,4001)
        session.ingest(pair_v01(4015,2),4015)
        positive=session.observation_work();on=session.evaluate_local()
        waiting=snapshot_v01(session)
        c.require(waiting['pending_alive'] and not waiting['pending_return'] and waiting['signal']['signal'],'atlas_sentinel_pending_order')
        old_effects=c.canonical(session.effects);old_report=c.canonical(session.report)
        late=refusal_v01(lambda:session.role_material(sem_old))
        late_plan=refusal_v01(lambda:session.execute_role_plan(plan))
        assessment=session.incident.evaluate(session.book,contract=session.contract)
        checks=dict(measured_clearance=assessment['clearance'],incident_active=session.incident.state=='ACTIVE',actual_signal=session.read_signal()['signal'])
        off=refusal_v01(lambda:session.command(dict(op='SET_LOCAL_SIGNAL_STATE',state='OFF',basis_ref=c.identity('atlas_current_assessment',assessment)),checks))
        c.require(c.canonical(session.effects)==old_effects and c.canonical(session.report)==old_report,'atlas_sentinel_late_history_changed')
        denied=snapshot_v01(session)
        late_record=dict(old_semantic=sem_old,old_plan_ref=plan_ref,semantic_refusal=late,plan_refusal=late_plan,
            controlled_advice=dict(command='OFF',reason='The late optional response says the incident is over.'),
            assessment=assessment,derived_checks=checks,off_refusal=off,after=denied,immutable_effects_sha256=c.digest(old_effects),
            immutable_report_sha256=c.digest(old_report),host_reached=False)
    finally:
        session.release_optional()
    joined=snapshot_v01(session)
    budget_controls={}
    budget_controls['retry']=refusal_v01(lambda:session.budgets.consume('optional_context','RETRY_AFTER_EXHAUSTION'))
    budget_controls['reset']=refusal_v01(lambda:session.budgets.allocate('optional_context',2,'replacement_context'))
    remaining=session.budgets.total-sum(v['limit'] for v in session.budgets.tasks.values())
    session.budgets.allocate('bounded_expansion',remaining,'atlas:finite_unused_reservation')
    budget_controls['expansion']=refusal_v01(lambda:session.budgets.allocate('one_more',1,'atlas:over_total'))
    budget_controls['native_work']=refusal_v01(lambda:contrasts.optional_diagnostics(session,0))
    recovery=[]
    for sequence,tick in enumerate((4030,4045,4060),3):
        session.ingest(pair_v01(tick,sequence,high=False),tick)
        assessment=session.evaluate_local()
        recovery.append(dict(assessment=assessment,snapshot=snapshot_v01(session)))
    c.require(not session.signal and session.incident.state=='CLOSED','atlas_sentinel_lawful_recovery_missing')
    result=dict(consumption=consumed,wrong_consumed_work=wrong,before=before,pending=pending,positive=positive,
        on_assessment=on,waiting=waiting,late=late_record,joined=joined,budget_controls=budget_controls,
        budget_final=snapshot_v01(session),recovery=recovery,report=session.report,final=snapshot_v01(session),
        worker_joined=not session.pending_worker.is_alive(),same_episode=True,
        optional_profile='CONTROLLED_BARRIER_STUB',native_authorization_clock='TRUSTED_WALL_TIME_UNCHANGED')
    save(session.directory/'N3_N4.json',result);return result


def collect_sentinel_v01(directory):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=False)
    started=time.monotonic();phases={};session=None
    def step(name,fn):
        start=time.monotonic();value=fn();phases[name]=time.monotonic()-start
        save(directory/(name+'.json'),value);return value
    with BoundaryObserver() as boundaries,NativeObserverV01() as native:
        try:
            n1=step('freshness',lambda:freshness_v01(directory/'freshness_episode'))
            session=setup_v01(directory/'continuing_episode')
            n2=step('correlation',lambda:correlated_v01(session))
            at=time.monotonic();experience,live=experience_v01(session,role_v01(session))
            phases['experience']=time.monotonic()-at;save(directory/'experience.json',experience)
            continuation=step('continuation',lambda:continue_v01(session,experience,live))
            result=dict(profile='INCIDENT_ATLAS_SENTINEL_AT5_V01',n1=n1,n2=n2,experience=experience,continuation=continuation,
                native=native.plain_v01(),counts=boundaries.snapshot(),phases=phases,seconds=time.monotonic()-started,
                new_provider_calls=0,new_models=0,controlled_adversarial=True,physical_prediction_certification=False)
            save(directory/'sentinel.json',result);return result
        finally:
            if session is not None and session.pending_worker is not None and session.pending_worker.is_alive():session.release_optional()
            save(directory/'finalizer.json',dict(worker_alive=bool(session and session.pending_worker and session.pending_worker.is_alive()),
                counts=boundaries.snapshot(),seconds=time.monotonic()-started,completed_phases=phases))
            save(directory/'native_partial.json',native.plain_v01())
