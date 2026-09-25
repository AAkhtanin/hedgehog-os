"""G5-1 finite two-peer collector. Source and local scenarios are supplied separately."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from hedgehog.external_drs import gate5_contracts_v01 as c, gate5_native_v01 as n, gate5_exchange_v01 as exchange


def collect(folder,scenario_dir):
    folder=Path(folder);folder.mkdir(parents=True,exist_ok=False)
    scenario_dir=Path(scenario_dir)
    for role in ('A','B'):
        (folder/role).mkdir();shutil.copy2(scenario_dir/(role+'.json'),folder/role/'scenario.json')
    pins={k:hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest() for k,m in [('contracts',c),('native',n),('exchange',exchange)]}
    n.save(folder/'preexecution_declaration.json',dict(source_pins=pins,
        scenarios={role:hashlib.sha256((folder/role/'scenario.json').read_bytes()).hexdigest() for role in ('A','B')},
        transport='INHERITED_OS_PIPES',root_ownership={'A':c.ROOT_A,'B':c.ROOT_B},
        no_expected_correction_or_answer_in_bootstrap=True,
        tasks=['positive_current_use','B_local_policy_negative','A_authenticated_AUDIT_refusal']))
    ar,bw=os.pipe();br,aw=os.pipe();children=[];receipts=[];started=time.monotonic()
    try:
        for role,r,w in [('A',ar,aw),('B',br,bw)]:
            err=(folder/role/'stderr.txt').open('w')
            argv=[sys.executable,'-B',__file__,'peer',role,str(r),str(w),str(folder/role)]
            child=subprocess.Popen(argv,pass_fds=(r,w),stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=err,text=True)
            children.append((role,child,err,argv))
            receipts.append(dict(role=role,pid=child.pid,argv=argv,start=time.time(),rc=None,reaped=False))
        for fd in (ar,aw,br,bw):os.close(fd)
        n.save(folder/'processes.json',receipts)
        public={}
        for role,child,err,argv in children:
            line=child.stdout.readline();c.require(bool(line),'peer_bootstrap_failed')
            public[role]=json.loads(line);n.save(folder/role/'public_keyset.json',public[role])
        base=dict(source_record_ref='source:gate5:calibration:one',source_policy_ref='policy:gate5:source:v01',
            unit_id=c.UNIT,quantity_id=c.QUANTITY,max_source_age=300,max_validity_horizon=600)
        a_policy=dict(base,policy_version='gate5.publisher.v01',publish_enabled=True,recipients=[c.ROOT_B],release_uses=['LOCAL_CONTEXT'])
        b_policy=dict(base,policy_version='gate5.importer.v01',peer_root=c.ROOT_A,local_root=c.ROOT_B,peer_keys=public['A']['public_keys'],
            endpoint='endpoint:gate5:A',object_id='object:gate5:calibration:one',transport_scope='owner:gate5:inherited-pipes',schemas=[c.BODY_SCHEMA],domain='CALIBRATION',
            uses=['AUDIT','LOCAL_CONTEXT'],accept_calibration=True,status_max_age=60,authority_scope_fingerprint=c.sha(dict(root=c.ROOT_B,purpose='calibration_context')))
        n.save(folder/'operator_trust.json',dict(A=a_policy,B=b_policy,public={k:v['public_keys'] for k,v in public.items()},
            source_pins=pins,origin='LOCAL_OPERATOR_BOOTSTRAP_BEFORE_RETRIEVAL_NOT_SELF_ATTESTED_PAYLOAD'))
        for role,child,err,argv in children:
            bootstrap=dict(own_policy=a_policy if role=='A' else b_policy,peer_keys=public['B' if role=='A' else 'A']['public_keys'],source_pins=pins)
            if role=='A':bootstrap['requester_policy']=b_policy
            child.stdin.write(json.dumps(bootstrap)+'\n');child.stdin.flush();child.stdin.close()
        while any(child.poll() is None for _,child,_,_ in children):
            with (folder/'heartbeat.jsonl').open('a') as stream:stream.write(json.dumps(dict(elapsed=time.monotonic()-started,pids=[p.pid for _,p,_,_ in children if p.poll() is None]))+'\n')
            time.sleep(1)
        for role,child,err,argv in children:
            (folder/role/'stdout.txt').write_text(child.stdout.read());child.wait()
        c.require(all(child.returncode==0 for _,child,_,_ in children),'peer_execution_failed')
        a=json.loads((folder/'A/result.json').read_text());b=json.loads((folder/'B/result.json').read_text())
        c.require(a['wire']['sent_bytes']==b['wire']['received_bytes'] and a['wire']['received_bytes']==b['wire']['sent_bytes'],'wire_counter_mismatch')
        c.require(a['counts']['released']==b['budget']['opened']==1,'opened_count')
        canary=(folder/'A/private/canary.txt').read_bytes()
        public_files=[p for p in folder.rglob('*') if p.is_file() and 'private' not in p.relative_to(folder).parts]
        c.require(all(canary not in p.read_bytes() for p in public_files),'public_canary_leak')
        n.save(folder/'canary_scan.json',dict(public_files=len(public_files),matches=0,private_material_excluded=True,
            scope='OBSERVED_BOOTSTRAP_WIRE_DESCRIPTORS_BODY_NATIVE_REPORTS_AND_PUBLIC_STATE; NO_CANARY_HASH_EXPORTED'))
        n.save(folder/'summary.json',dict(status='COLLECTED',seconds=time.monotonic()-started,A=a,B=b,transport='INHERITED_OS_PIPES_NOT_NETWORK_OR_ENCRYPTION'))
        print(json.dumps(dict(status='COLLECTED',seconds=time.monotonic()-started,result=b['accepted']['assessment'])),flush=True)
    finally:
        for row,(role,child,err,argv) in zip(receipts,children):
            if child.poll() is None:child.terminate()
            row.update(rc=child.wait(),end=time.time(),reaped=True);err.close()
        n.save(folder/'processes.json',receipts)


if __name__=='__main__':
    if sys.argv[1]=='peer':exchange.peer(sys.argv[2],int(sys.argv[3]),int(sys.argv[4]),sys.argv[5])
    else:collect(sys.argv[1],sys.argv[2])
