"""Actual recording/descent controls sharing the native fixture's living objects."""
from copy import deepcopy
import pytest
from tests.test_gate4_reference_native_v01 import native_story
from hedgehog.domains.airline import gate4_reference_adapter_v01 as a
from hedgehog.domains.airline import gate4_reference_history_v01 as gh


def test_history_actual_native_proof_and_recording(native_story):
    a.history.validate_native_work_proof_v01(native_story['proof'])
    live=native_story['lives']['warm']; opened=live['opened']
    assert gh.consume_opened_v01(live,opened)==opened['prior']['prior_fp']
    assert opened['prior']['prior_fp']<0
    evidence=live['history_evidence_binding']
    assert evidence['review']['result']['decision']=='ACCEPT'
    assert evidence['descent']['opened_record_ids']==[opened['head']['record_id']]
    assert evidence['descent']['bytes_opened']>0
    stages=[r['stage'] for r in evidence['read_audit']]
    assert stages.index('ROOT_APPROVED')<stages.index('PAYLOAD_READ')<stages.index('PUBLIC_OPEN_VALIDATED')
    assert native_story['lives']['cold']['opened'] is None


def test_history_wrong_source_role_policy_time_and_head(native_story):
    live=native_story['lives']['warm']; original=live['opened']; controls={}
    for name in ('prior','head','history_key','evaluation_time','payload_sha256','store'):
        value={k:(v if k=='store' else deepcopy(v)) for k,v in original.items()}
        if name=='prior':value['prior']['prior_fp']+=1
        elif name=='head':value['head']['body_sha256']='0'*64
        elif name=='history_key':value['history_key']['capability_contract_version']='different-role-v01'
        elif name=='evaluation_time':value[name]+=1
        elif name=='payload_sha256':value[name]='0'*64
        else:value[name]=object()
        with pytest.raises(ValueError) as error:gh.consume_opened_v01(live,value)
        controls[name]=str(error.value)
        assert gh.consume_opened_v01(live,original)==original['prior']['prior_fp']
    store=live['store']
    for name,field in [('wrong_root','local_root_scope_id'),('wrong_role','task_class_id'),('wrong_policy','policy_semantics_version')]:
        key=dict(live['history_key']);key[field]='g42:foreign'
        try:
            bad,evidence=store.current_v01(history_key=key,root=a.ROOT,transaction=live['transaction'],evaluation_time=live['clock'].evaluation_time)
            gh.consume_opened_v01(live,bad)
        except ValueError as error:controls[name]=str(error)
        else:raise AssertionError(name+' accepted')
        assert gh.consume_opened_v01(live,original)==original['prior']['prior_fp']
    expired,evidence=store.current_v01(history_key=live['history_key'],root=a.ROOT,transaction=live['transaction'],evaluation_time=live['clock'].evaluation_time+1000)
    assert expired is None
    with pytest.raises(ValueError,match='g42_required_history_missing'):gh.consume_opened_v01(live,expired)
    assert gh.consume_opened_v01(live,original)==original['prior']['prior_fp']
    native_story['journal'].save('history_controls.json',dict(refusals=controls,expired=evidence,positive_prior=original['prior']['prior_fp']))


def test_g43_retained_history_current_requalification(native_story):
    live=native_story['lives']['warm']; opened=live['opened']
    original=a.canonical_v01(dict(basis=live['basis'],proposal=live['proposal'],clock=live['clock'],history=live['history_evidence_binding']))
    before=a.work.inspect_work_task_v01(live['host'],task_id=live['task_id'])
    start=opened['evaluation_time'];end=int(a.datetime.fromisoformat(a.plain_v01(opened['bridge'])['time_envelope']['valid_to']).timestamp())
    live['task_clock'].advance_v01(start+1)
    assert gh.consume_opened_v01(live,opened)==opened['prior']['prior_fp']
    assert live['current_opened']['evaluation_time']==start+1 and live['opened'] is opened
    assert live['current_history_evidence'][-1]['review']['result']['decision']=='ACCEPT'
    assert original==a.canonical_v01(dict(basis=live['basis'],proposal=live['proposal'],clock=live['clock'],history=live['history_evidence_binding']))
    live['task_clock'].advance_v01(end-1)
    assert gh.consume_opened_v01(live,opened)==opened['prior']['prior_fp']
    live['task_clock'].advance_v01(end)
    with pytest.raises(ValueError,match='g43_current_history_expired'):gh.consume_opened_v01(live,opened)
    live['task_clock'].advance_v01(end+1)
    with pytest.raises(ValueError,match='g43_current_history_expired'):gh.consume_opened_v01(live,opened)
    assert before==a.work.inspect_work_task_v01(live['host'],task_id=live['task_id'])
    native_story['journal'].save('retained_history_current_controls.json',dict(current_descent=live['current_history_evidence'],
        at_boundary='REFUSED',after='REFUSED',enrolled_original_preserved=True,usage_preserved=True))
