"""External phase journal and finite passive no-recollection observation."""
import sys,time
from ops import *
COUNTS={};NAMES={};SLOT=None;START=None
def pytest_sessionstart(session):
    global SLOT,START
    from hedgehog import incident_atlas_v01 as atlas, work_execution_host_v01 as host
    from hedgehog import outcome_feedback_history_v01 as history, outcome_feedback_consumer_v01 as consumer
    from hedgehog.kernel import root_decision_v01 as roots, work_composition_v01 as work
    from hedgehog.domains.supplier_water_filter import incident_atlas_v01 as supplier, incident_atlas_backend_v01 as backend
    from hedgehog.domains.airline import incident_atlas_v01 as airline, semantic_to_contract_causal_runtime_v01 as causal
    from hedgehog.domains.testflix import incident_atlas_v01 as testflix, semantic_adapter_v01 as tfsem
    from hedgehog.domains.ephemeral_workspace import incident_atlas_v01 as workspace, incident_atlas_summary_v01 as summary
    from hedgehog.domains.landslide_sentinel import incident_atlas_v01 as sentinel, monitoring_runtime_v01 as monitoring
    targets=dict(collect=atlas.collect_v01,supplier=supplier.collect_supplier_v01,airline=airline.collect_airline_v01,
        testflix=testflix.collect_testflix_v01,workspace=workspace.collect_workspace_v01,sentinel=sentinel.collect_sentinel_v01,
        root=roots.decide_root_v01,host_init=host.RootWorkExecutionHostV01.__init__,host_dispatch=host.RootWorkExecutionHostV01.dispatch,
        host_pure=host.execute_admitted_pure_work_v01,work=work.advance_work_program_v01,
        current_work=consumer.execute_reviewed_pure_work_v01,history_prepare=history.OutcomeHistoryV01.prepare_v01,
        history_commit=history.OutcomeHistoryV01.commit_v01,history_read=history.OutcomeHistoryV01.read_v01,
        history_current=history.OutcomeHistoryV01.current_v01,provider=causal._call_provider,
        testflix_provider=tfsem.collect_semantics_v01,workspace_provider=summary.LiveProvider.respond,
        summary_capture=summary.capture_v01,backend=backend.BackendV01.invoke_v01,
        sentinel_episode=monitoring.ControlledEpisode.__init__)
    for name,fn in targets.items():
        assert Path(fn.__code__.co_filename).is_relative_to(CLONE),(name,fn.__code__.co_filename)
        COUNTS[name]=0;NAMES[fn.__code__]=name
    save(WORK/'focused_import_origins.json',{name:dict(file=fn.__code__.co_filename,line=fn.__code__.co_firstlineno) for name,fn in targets.items()})
    SLOT=next(i for i in range(6) if sys.monitoring.get_tool(i) is None);START=time.monotonic()
    sys.monitoring.use_tool_id(SLOT,'AT6 saved verification')
    sys.monitoring.register_callback(SLOT,sys.monitoring.events.PY_START,observe)
    for code in NAMES:sys.monitoring.set_local_events(SLOT,code,sys.monitoring.events.PY_START)
def observe(code,offset):COUNTS[NAMES[code]]+=1
def pytest_runtest_logreport(report):
    with (WORK/'focused_phases.jsonl').open('a') as out:
        out.write(json.dumps(dict(node=report.nodeid,phase=report.when,outcome=report.outcome,seconds=report.duration,
            error=str(report.longrepr) if report.failed else None))+'\n')
def pytest_sessionfinish(session,exitstatus):
    if SLOT is not None:
        for code in NAMES:sys.monitoring.set_local_events(SLOT,code,0)
        sys.monitoring.register_callback(SLOT,sys.monitoring.events.PY_START,None);sys.monitoring.free_tool_id(SLOT)
    save(WORK/'focused_observation.json',dict(counts=COUNTS,seconds=time.monotonic()-START if START else None,
        scope='Selected domain/provider/Root/Host/Work/history entrypoints, not OS-wide monitoring.'))
    save(WORK/'focused_finalizer.json',dict(rc=int(exitstatus),nodes=session.testscollected,failed=session.testsfailed))
    if any(COUNTS.values()):session.exitstatus=1
