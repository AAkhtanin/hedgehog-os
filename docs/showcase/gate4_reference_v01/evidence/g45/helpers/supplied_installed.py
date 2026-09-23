"""One installed-source supplied validation. No runtime collection or effects."""
import json,os,sys,time
from pathlib import Path
from g45 import W,O,I,PINS,sha,dump,identity
from hedgehog import gate4_reference_release_v01 as r,gate4_reference_evidence_v01 as e
from demo import run_living_gauntlet_v01 as l,run_kernel_conformance_v01 as c
from hedgehog import gate3_mechanism_v01 as g3
a=e.a
OUT=W/'installed_supplied';OUT.mkdir()
assert Path(r.__file__).resolve()==O/'hedgehog/gate4_reference_release_v01.py'
assert Path(e.__file__).resolve()==O/'hedgehog/gate4_reference_evidence_v01.py'
assert identity(I/'portable_publication_final/PUBLICATION.json')['sha256']==PINS['publication']
assert identity(I/'parents/MANIFEST.json')['sha256']==PINS['parent']
trust=e.read_json_v01(I/'TEST_SUPPLIED_PIN_FINAL.json');assert trust['status']=='TEST_SUPPLIED_PIN'
functions=[a.native_story_v42,a.start_native_v42,a.run_allocated_v42,
    a.hosts.build_root_work_execution_host_v01,a.work.enroll_work_program_v01,a.work.advance_work_program_v01,
    a.work.revise_work_program_v01,a.hosts.dispatch_current_action_v01,
    a.history.OutcomeHistoryV01.__init__,a.history.OutcomeHistoryV01.prepare_v01,a.history.OutcomeHistoryV01.commit_v01,
    a.history.OutcomeHistoryV01.current_v01,a.roots.decide_root_v01,a.execute_quantum_v42,a.execute_strategy_v42,
    a.checks.execute_constraint_v01,l.collect_living_gauntlet_v01,l.collect_living_g36_v01,
    c.collect_standalone_kernel_conformance_v01,c.collect_kernel_conformance_g36_v01,g3.collect_mechanism_v01]
timed=[r.validate_registration_v01,r.validate_parents_v01,e.verify_package_v01,a.roots.validate_root_decision_result_v01]
names={f.__code__:f.__module__+'.'+f.__qualname__ for f in functions+timed};forbidden={f.__code__ for f in functions}
counts={n:0 for n in names.values()};times={n:0.0 for n in names.values()};stack={code:[] for code in names}
audit={n:0 for n in ('socket.connect','socket.getaddrinfo','urllib.Request','subprocess.Popen')}
def enter(code,offset):
    counts[names[code]]+=1;stack[code].append(time.perf_counter())
    if code in forbidden:raise RuntimeError('PROHIBITED_RUNTIME_ENTRY:'+names[code])
def leave(code,offset,value):times[names[code]]+=time.perf_counter()-stack[code].pop()
def observe_audit(name,args):
    if name in audit:
        audit[name]+=1;raise RuntimeError('PROHIBITED_EXTERNAL_ENTRY:'+name)
sys.addaudithook(observe_audit)
m=sys.monitoring;tool=4;m.use_tool_id(tool,'g45_installed_supplied')
m.register_callback(tool,m.events.PY_START,enter);m.register_callback(tool,m.events.PY_RETURN,leave)
for code in names:m.set_local_events(tool,code,m.events.PY_START|m.events.PY_RETURN)
start=time.perf_counter();rc=1
try:
    result=l.validate_living_g44_v01(parent_directory=I/'parents',parent_pin=PINS['parent'],
        package=I/'portable_publication_final',trust=trust,root=O)
    e._write(OUT/'combined.json',result)
    assert identity(OUT/'combined.json')['bytes']==1151634 and identity(OUT/'combined.json')['sha256']==PINS['combined']
    assert (OUT/'combined.json').read_bytes()==(I/'commands/0020_supplied_living_final/combined.json').read_bytes()
    origins=e.checker_sources_v44();assert all(Path(v['origin']).is_relative_to(O) for v in origins.values())
    dump(OUT/'imported_origins.json',origins);dump(OUT/'comparison.json',dict(status='BYTE_IDENTICAL_TO_REVIEWED_G44',
        result=identity(OUT/'combined.json'),trust_record=identity(I/'TEST_SUPPLIED_PIN_FINAL.json'),trust_status_unchanged='TEST_SUPPLIED_PIN',
        note='Recorded result provenance unchanged; actual G45 landing is evidenced separately'))
    rc=0;print(result['status'])
finally:
    for code in names:m.set_local_events(tool,code,0)
    m.free_tool_id(tool)
    forbidden_counts={names[code]:counts[names[code]] for code in forbidden}
    dump(OUT/'execution.json',dict(rc=rc,seconds=time.perf_counter()-start,entries=counts,forbidden_calls=forbidden_counts,
        audit=audit,inclusive_seconds_not_additive=times,interpreter=str(Path(sys.executable).resolve())))
    assert not any(forbidden_counts.values()) and not any(audit.values())
