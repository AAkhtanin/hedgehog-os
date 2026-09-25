"""Declared two-session G52 IPC collector; no source data is bootstrapped into B."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from hedgehog.external_drs import gate5_contracts_v01 as c, gate5_exchange_v01 as e, gate5_native_v01 as n, gate5_lifecycle_v01 as life


def observed_peer(role,r,w,folder,session):
    from hedgehog.kernel import root_decision_v01 as roots
    targets={'native_work':n.native_work,'root_decision':roots.decide_root_v01,'peer_send':e.PipeChannel.send,'peer_receive':e.PipeChannel.receive,
        'history_query':life.Requester.history,'source_work':e.build_source,'current_use':life.Requester.use}
    by_code={fn.__code__:name for name,fn in targets.items()};counts={name:0 for name in targets};intervals=[];active={}
    started=time.monotonic();tool=4;sys.monitoring.use_tool_id(tool,'g52_sparse_observation')
    def enter(code,*args):
        if code in active:
            then,before=active.pop(code)
            intervals.append(dict(function=by_code[code],returned=False,end_upper_bound_seconds=time.monotonic()-then,
                deltas={name:counts[name]-before[name] for name in counts}))
        name=by_code[code];counts[name]+=1
        if name in ('history_query','source_work','current_use'):active[code]=(time.monotonic(),dict(counts))
    def leave(code,*args):
        if code in active:
            then,before=active.pop(code);intervals.append(dict(function=by_code[code],seconds=time.monotonic()-then,
                returned=True,deltas={name:counts[name]-before[name] for name in counts}))
    sys.monitoring.register_callback(tool,sys.monitoring.events.PY_START,enter)
    sys.monitoring.register_callback(tool,sys.monitoring.events.PY_RETURN,leave)
    for code in by_code:sys.monitoring.set_local_events(tool,code,sys.monitoring.events.PY_START|sys.monitoring.events.PY_RETURN)
    try:
        if role=='A':life.publisher(r,w,folder)
        else:life.requester(r,w,folder,session)
    finally:
        for code in by_code:sys.monitoring.set_local_events(tool,code,0)
        sys.monitoring.free_tool_id(tool)
        n.save(Path(folder)/('observation_%d.json'%session),dict(counts=counts,intervals=intervals,seconds=time.monotonic()-started,
            unfinished=list(by_code[code] for code in active),profile='SELECTED_CODE_OBJECT_EVENTS_ONLY'))


def collect(folder,scenario_dir):
    folder,scenario_dir=Path(folder),Path(scenario_dir);folder.mkdir(parents=True,exist_ok=False)
    for role in ('A','B'):
        (folder/role).mkdir();shutil.copy2(scenario_dir/(role+'.json'),folder/role/'scenario.json')
    names=[Path(m.__file__) for m in (c,e,n,life)]
    n.save(folder/'preexecution.json',dict(source_pins={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in names},
        scenarios={role:hashlib.sha256((folder/role/'scenario.json').read_bytes()).hexdigest() for role in ('A','B')},
        task_contexts=life.contexts(),transport='INHERITED_PIPES',clock_profile='ACTUAL_INTEGER_UTC_SOURCE_REVIEW_STATUS_USE; DONOR_WORK_LOGICAL_1014',
        schedule='A retained; B1 exits after terminal persistence; B2 is a new process and signer explicitly repinned; no key serialization',
        source_status_schedule='Baseline STATUS #3 unavailable; #4 active; #5+ revoked. Scope task independent.',
        max_sessions=2,max_messages_per_session=32))
    ar,bw=os.pipe();br,aw=os.pipe();children=[];receipts=[];start=time.monotonic()
    def launch(role,session,r,w):
        stderr=(folder/role/('stderr_%d.txt'%session)).open('w')
        argv=[sys.executable,'-B',__file__,'peer',role,str(r),str(w),str(folder/role),str(session)]
        process=subprocess.Popen(argv,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=stderr,text=True,pass_fds=(r,w))
        children.append((process,stderr));receipts.append(dict(role=role,session=session,pid=process.pid,start=time.time(),argv=argv,rc=None,reaped=False))
        n.save(folder/'processes.json',receipts)
        line=process.stdout.readline();c.require(bool(line),'peer_key_bootstrap');return process,json.loads(line)
    try:
        a,a_keys=launch('A',0,ar,aw)
        base=dict(source_record_ref='source:gate5:calibration:one',source_policy_ref='policy:gate5:source:v01',unit_id=c.UNIT,
            quantity_id=c.QUANTITY,max_source_age=300,max_validity_horizon=600)
        a_policy=dict(base,policy_version='gate5.publisher.v01',publish_enabled=True,recipients=[c.ROOT_B],release_uses=['LOCAL_CONTEXT'])
        b_policy=dict(base,policy_version='gate5.importer.v01',peer_root=c.ROOT_A,local_root=c.ROOT_B,peer_keys=a_keys,
            endpoint='endpoint:gate5:A',object_id='object:gate5:calibration:one',transport_scope='owner:gate5:inherited-pipes',schemas=[c.BODY_SCHEMA],
            domain='CALIBRATION',uses=['AUDIT','LOCAL_CONTEXT'],accept_calibration=True,status_max_age=60,
            authority_scope_fingerprint=c.sha(dict(root=c.ROOT_B,purpose='calibration_context')))
        public_b=[]
        for session in (1,2):
            b,b_keys=launch('B',session,br,bw);public_b.append(b_keys)
            a.stdin.write(json.dumps(dict(own_policy=a_policy,requester_policy=b_policy,peer_keys=b_keys,contexts=life.contexts()))+'\n');a.stdin.flush()
            c.require(a.stdout.readline().strip()=='READY:'+str(session),'source_session_ready')
            b.stdin.write(json.dumps(dict(own_policy=b_policy,peer_keys=a_keys,contexts=life.contexts()))+'\n');b.stdin.flush();b.stdin.close()
            while b.poll() is None:
                with (folder/'heartbeat.jsonl').open('a') as out:out.write(json.dumps(dict(stage='B_SESSION_'+str(session),elapsed=time.monotonic()-start,pid=b.pid))+'\n')
                try:b.wait(2)
                except subprocess.TimeoutExpired:pass
            (folder/'B'/('stdout_%d.txt'%session)).write_text(b.stdout.read())
            c.require(b.wait()==0,'B_session_failed')
            c.require(a.stdout.readline().strip()=='DONE:'+str(session),'source_session_close')
            if session==1:
                n.save(folder/'restart_checkpoint.json',dict(b1_pid=b.pid,b1_rc=b.returncode,b1_reaped=True,
                    persisted_state=life.read(folder/'B/import_state.json'),budget=life.read(folder/'B/budgets'/(life.BASELINE+'.json')),
                    accepted_sha256=hashlib.sha256((folder/'B/r1/accepted.json').read_bytes()).hexdigest(),
                    a_pid=a.pid,a_still_running=a.poll() is None))
        a.stdin.close();a.wait();c.require(a.returncode==0,'A_failed');(folder/'A/stdout.txt').write_text(a.stdout.read())
        c.require(public_b[0]!=public_b[1],'fresh_B_signer_required')
        n.save(folder/'operator_trust.json',dict(A=a_policy,B=b_policy,A_keys=a_keys,B_sessions=public_b,
            task_contexts=life.contexts(),origin='TRUSTED_LOCAL_OPERATOR_REPIN_BEFORE_EACH_B_SESSION'))
        canary=(folder/'A/private/canary.txt').read_bytes()
        files=[p for p in folder.rglob('*') if p.is_file() and 'private' not in p.relative_to(folder).parts]
        c.require(all(canary not in p.read_bytes() for p in files),'canary_leak')
        n.save(folder/'canary_scan.json',dict(public_files=len(files),matches=0,private_body_and_hash_not_exported=True))
        one=life.read(folder/'B/r1/accepted.json');two=life.read(folder/'B/r2/accepted.json')
        n.save(folder/'summary.json',dict(status='COLLECTED_G52',seconds=time.monotonic()-start,
            historical=one['claim'],current=two['claim'],source_state=life.read(folder/'A/publisher_budget.json'),
            importer_state=life.read(folder/'B/import_state.json'),process_restart=True,transport='INHERITED_OS_PIPES_NOT_ENCRYPTION'))
        print(json.dumps(dict(status='COLLECTED_G52',seconds=time.monotonic()-start,historical=one['claim']['outputs'],current=two['claim']['outputs'])))
    finally:
        for process,stderr in children:
            if process.poll() is None:process.terminate()
            process.wait();stderr.close()
        for row,(process,_) in zip(receipts,children):row.update(rc=process.returncode,reaped=True,end=time.time())
        n.save(folder/'processes.json',receipts)
        for fd in (ar,bw,br,aw):os.close(fd)


if __name__=='__main__':
    if sys.argv[1]=='peer':observed_peer(sys.argv[2],int(sys.argv[3]),int(sys.argv[4]),Path(sys.argv[5]),int(sys.argv[6]))
    else:collect(sys.argv[1],sys.argv[2])
