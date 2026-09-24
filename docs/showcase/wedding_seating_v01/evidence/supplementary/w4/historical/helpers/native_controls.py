"""Real native prepare and Root, controlled transport fault injection only."""
from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
import sys
import tempfile
import time
from types import SimpleNamespace
WORK=Path(__file__).resolve().parent;sys.path.insert(0,str(WORK))
from manage import save
import episode
from hedgehog.domains.wedding_seating import native_contracts_v01 as c,qpu_bridge_v01 as b,qpu_contracts_v01 as q

class Events:
    def register(self,event,callback):self.callback=callback
    def unregister(self,event,callback):self.callback=None

class ControlledClient:
    def __init__(self,*,mutate=None,lost=False):self.meta=SimpleNamespace(events=Events());self.mutate=mutate;self.lost=lost;self.sends=0
    def create_quantum_task(self,**body):
        wire=deepcopy(body)
        if self.mutate:self.mutate(wire)
        request=SimpleNamespace(method='POST',url=b.ENDPOINT+'/quantum-task',body=c.canonical(wire))
        self.meta.events.callback(request=request)
        self.sends+=1
        if self.lost:raise TimeoutError('CONTROLLED_LOST_ACK')
        return dict(quantumTaskArn='arn:aws:braket:us-west-1:'+b.ACCOUNT+':quantum-task/CONTROLLED',ResponseMetadata=dict(RequestId='CONTROLLED'))

rows=[]
def control(name,fn,refused=False):
    started=time.monotonic()
    try:fn()
    except (ValueError,TimeoutError) as error:
        if not refused:raise
        rows.append(dict(name=name,outcome='EXPECTED_REFUSAL',reason=str(error),seconds=time.monotonic()-started))
    else:
        assert not refused,name;rows.append(dict(name=name,outcome='PASS',seconds=time.monotonic()-started))
    save(WORK/'controls/native_current_controls.json',rows)

if __name__=='__main__':
    run=episode.preparation(q.PROFILES[0]);program=episode.local_circuit(run);scope=episode.scope()
    body=b.request_v01(scope,program,'CONTROLLED-W4-CURRENT-ROOT');permit=b.permit_v01(run,scope,body,int(time.time()))
    save(WORK/'controls/current_root.json',permit.evidence())
    control('genuine_current_permit',lambda:permit.check(scope,body,int(time.time())))
    control('expired_permit',lambda:permit.check(scope,body,permit.expires),True)
    control('revoked_disclosure',lambda:permit.check(dict(scope,revoked=True),body,int(time.time())),True)
    original=run.output;run.output=dict(original,profile='MIX_CIRCLES_V01')
    control('substituted_native_output',lambda:run.validate_current(run.owner),True);run.output=original
    control('lawful_native_after_refusal',lambda:run.validate_current(run.owner))
    for case,mutate,lost in (('positive',None,False),('changed_actual_shots',lambda v:v.update(shots=999),False),
        ('private_actual_metadata',lambda v:v.update(tags={'private':'CANARY'}),False),('lost_ack',None,True)):
        with tempfile.TemporaryDirectory() as directory:
            store=b.LedgerV01(directory);client=ControlledClient(mutate=mutate,lost=lost)
            with store.locked() as ledger:
                row=store.reserve(ledger,run.owner.profile,body,permit.evidence())
                control(case,lambda:b.send_v01(store,ledger,row,permit,lambda:scope,client),case!='positive')
                assert client.sends==(1 if case in ('positive','lost_ack') else 0)
                if lost:
                    assert row['state']=='SUBMISSION_OUTCOME_UNKNOWN' and row['reserved_microusd']==725000
                    control('no_blind_resubmit_unknown',lambda:b.send_v01(store,ledger,row,permit,lambda:scope,client),True)
                assert client.meta.events.callback is None
                save(WORK/'controls'/f'{case}_ledger.json',ledger)
    print(json.dumps(dict(controls=len(rows),all_expected=True,aws_calls=0,controlled_transport_only=True)))
