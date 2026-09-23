"""Independent CLI replay with passive finite entrypoint observations."""
import json
import runpy
import sys
import time
from ops import WORK, CANDIDATE, save
sys.path.insert(0,str(CANDIDATE))
from hedgehog import incident_atlas_v01 as atlas, gate3_mechanism_v01 as mechanism
from hedgehog import work_execution_host_v01 as host, outcome_feedback_history_v01 as history
from hedgehog import outcome_feedback_consumer_v01 as consumer
from hedgehog.kernel import root_decision_v01 as root
from hedgehog.domains.supplier_water_filter import incident_atlas_backend_v01 as backend, incident_atlas_v01 as supplier
from hedgehog.domains.airline import incident_atlas_v01 as airline, semantic_to_contract_causal_runtime_v01 as causal
from hedgehog.domains.testflix import incident_atlas_v01 as testflix, evidence_v01 as evidence
from hedgehog.domains.testflix import lifecycle_v01 as lifecycle, semantic_adapter_v01 as semantics
from hedgehog.domains.ephemeral_workspace import incident_atlas_v01 as workspace, incident_atlas_summary_v01 as summary
from hedgehog.domains.ephemeral_workspace import session_runtime_v01 as session, memory_adapter_v01 as memory
from hedgehog.domains.ephemeral_workspace import incident_atlas_work_v01 as workspace_work
from hedgehog.kernel import work_composition_v01 as composition
from hedgehog.domains.landslide_sentinel import incident_atlas_v01 as sentinel, monitoring_runtime_v01 as monitoring
from hedgehog.domains.landslide_sentinel import semantic_adapter_v01 as sentinel_semantic
from hedgehog.domains.landslide_sentinel.outcome_feedback_adapter_v01 import SentinelPredictiveSourceV01, G34ControlledCurrentWorkV01

label=sys.argv[1];export=WORK/'export'
targets=dict(collect=atlas.collect_v01,donor_collect=mechanism.collect_mechanism_v01,
    supplier_collect=supplier.collect_supplier_v01,airline_collect=airline.collect_airline_v01,
    testflix_collect=testflix.collect_testflix_v01,testflix_handle=evidence.TestflixHandlerV01.handle_v01,
    testflix_provider=semantics.collect_semantics_v01,testflix_dispatch=lifecycle.dispatch_v01,
    semantic_callback=causal._call_provider,root_decide=root.decide_root_v01,
    host_init=host.RootWorkExecutionHostV01.__init__,host_dispatch=host.RootWorkExecutionHostV01.dispatch,
    backend_invoke=backend.BackendV01.invoke_v01,pure_work=consumer.execute_reviewed_pure_work_v01,
    history_prepare=history.OutcomeHistoryV01.prepare_v01,history_commit=history.OutcomeHistoryV01.commit_v01,
    history_read=history.OutcomeHistoryV01.read_v01,history_current=history.OutcomeHistoryV01.current_v01,
    workspace_collect=workspace.collect_workspace_v01,summary_capture=summary.capture_v01,
    workspace_command=session.Workspace.command,workspace_effect=session.Workspace.execute_effect,
    workspace_model=summary.LiveProvider.respond,workspace_history=workspace_work.observe_v01,
    workspace_memory_read=memory.SemanticMemory.select,workspace_memory_write=memory.SemanticMemory._write,
    work_advance=composition.advance_work_program_v01,host_pure=host.execute_admitted_pure_work_v01,
    sentinel_collect=sentinel.collect_sentinel_v01,sentinel_episode=monitoring.ControlledEpisode.__init__,
    sentinel_command=monitoring.ControlledEpisode.command,sentinel_read=monitoring.ControlledEpisode.observation_work,
    sentinel_worker=monitoring.ControlledEpisode.start_optional,sentinel_native_work=monitoring.ControlledEpisode.pure_consumer,
    sentinel_prediction=SentinelPredictiveSourceV01.observe_v01,
    sentinel_current_work=G34ControlledCurrentWorkV01.evaluate_v01,
    sentinel_current_check=G34ControlledCurrentWorkV01.evaluate_check_v01)
names={f.__code__:n for n,f in targets.items()};counts={n:0 for n in targets}
slot=next(i for i in range(6) if sys.monitoring.get_tool(i) is None)
sys.monitoring.use_tool_id(slot,'AT5 replay observation')
def observe(code,offset):counts[names[code]]+=1
sys.monitoring.register_callback(slot,sys.monitoring.events.PY_START,observe)
for code in names:sys.monitoring.set_local_events(slot,code,sys.monitoring.events.PY_START)
start=time.monotonic();status='INCOMPLETE'
try:
    sys.argv=['demo/run_incident_atlas_v01.py','replay','--package',str(export/'atlas_package.json'),
        '--expected-pin',str(export/'expected_pin.json'),'--output',str(WORK/(label+'.json'))]
    runpy.run_path(str(CANDIDATE/'demo/run_incident_atlas_v01.py'),run_name='__main__')
    report=json.loads((WORK/(label+'.json')).read_bytes())
    assert report['cards']==[p+str(i) for p in ('A','N','S','T','W') for i in range(1,5)]
    assert report['counts']['unique_experience_consumers']==5 and not any(counts.values()),counts
    status='PASS'
finally:
    for code in names:sys.monitoring.set_local_events(slot,code,0)
    sys.monitoring.register_callback(slot,sys.monitoring.events.PY_START,None);sys.monitoring.free_tool_id(slot)
    save(WORK/(label+'_observation.json'),dict(status=status,counts=counts,elapsed_seconds=time.monotonic()-start,
        scope='Selected production entrypoints, not an OS-wide network or effect audit',
        origins={n:dict(file=f.__code__.co_filename,line=f.__code__.co_firstlineno) for n,f in targets.items()}))
