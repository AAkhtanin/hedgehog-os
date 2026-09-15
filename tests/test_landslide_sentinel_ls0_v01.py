"""Focused LS0 controls without historical test fixtures or hidden full runners."""
import json
import os
from pathlib import Path
import pytest
from hedgehog.domains.landslide_sentinel import contracts_v01 as c
from hedgehog.domains.landslide_sentinel import semantic_adapter_v01 as semantics
from hedgehog.domains.landslide_sentinel.monitoring_runtime_v01 import Sentinel


def fixture_input():
    return json.loads((Path(__file__).resolve().parents[1]/'fixtures/landslide_sentinel/ls0_inputs_v01.json').read_text())


def evidence_dir(name):
    path=Path(os.environ['LS0_EVIDENCE'])/'runs'/os.environ['LS0_RUN_ID']/name
    path.parent.mkdir(parents=True,exist_ok=True)
    return path


def test_closed_measurements_and_semantics():
    data=fixture_input();frame=data['frames'][0]
    assert c.cadence(frame)==60 and c.cadence(data['changed_rainfall'])==15
    for bad in (dict(frame,value=None),dict(frame,value=True),dict(frame,unit='mm'),dict(frame,calibration='foreign')):
        with pytest.raises(ValueError):c.measurement(bad)
    ctx=semantics.context(data['frames'],data['reference_note'])
    valid=dict(diagnostic='INDEPENDENT_RESERVE_SERIES',source_refs=list(ctx['sources'])[:1],reason='Inspect independent measurement.')
    assert semantics.validate_response(valid,ctx)==valid
    for bad in (dict(valid,permission=True),dict(valid,source_refs=['foreign']),dict(valid,diagnostic='SIGNAL_ON')):
        with pytest.raises(ValueError):semantics.validate_response(bad,ctx)
    fake=object.__new__(semantics.GeminiHarness);fake.available=False;fake.calls=0
    with pytest.raises(ValueError,match='harness_emulator_unavailable'):fake.respond(ctx)
    assert fake.calls==0


def test_unchanged_native_configuration_and_pending_critical():
    session=Sentinel(evidence_dir('local_control'),fixture_input())
    session.prepare_config()
    assert not session.executed and not session.signal
    session.dispatch_pending()
    assert len(session.executed)==1 and session.cadence_seconds==60 and not session.signal
    assert session.intake(59) is None
    assert session.intake(60)['cadence_seconds']==60
    session.critical_while_pending()
    assert session.signal and len(session.executed)==2


def test_local_drs_reopen_and_current_descent():
    from hedgehog.domains.landslide_sentinel.monitoring_runtime_v01 import SentinelMemory,memory_dependencies,MEMORY_POLICY
    from hedgehog.domains.landslide_sentinel import capability_registry_v01 as caps
    from hedgehog.domains.landslide_sentinel.evidence_v01 import save
    fixture=fixture_input();fixture['frames'][1]['value']=450
    session=Sentinel(evidence_dir('local_drs'),fixture)
    store=SentinelMemory(session.directory/'drs')
    args=dict(root=session.root,request=session.request,dependency=memory_dependencies(session),now=session.source.sample().evaluation_time)
    assert store.select(**args) is None
    record=store.remember(session)
    reopened=SentinelMemory(session.directory/'drs')
    warm=reopened.select(**dict(args,now=session.source.sample().evaluation_time))
    assert warm is not None and warm[1]['record_id']==record
    consumed=session.pure_consumer('sentinel.information.v01',dict(summary=c.canonical(warm[0]).decode(),record_id=record))
    output=json.loads(caps.values(consumed[1][0].result.output)['material'])
    assert output['summary']==c.canonical(warm[0]).decode() and output['informational_only']
    assert reopened.select(**dict(args,policy=MEMORY_POLICY+'.changed')) is None
    assert reopened.select(**dict(args,dependency=dict(args['dependency'],calibration='changed'))) is None
    assert reopened.drs.read_record('work',record)['content']['record']['meaning_record_id']==record
    save(session.directory/'drs_proof.json',dict(cold_events=store.events,warm_events=reopened.events,record_id=record,
        actual_typed_result=consumed[1],provider_calls=0,remote_drs_calls=0,captured_reexecution_calls=0,package_replay_calls=0))


def test_diagnostic_selection_changes_actual_admitted_work():
    from hedgehog.domains.landslide_sentinel import capability_registry_v01 as caps
    from hedgehog.domains.landslide_sentinel.evidence_v01 import save
    session=Sentinel(evidence_dir('diagnostic_contrast'),fixture_input())
    frames=json.loads(c.canonical(session.frames));frames[0]['healthy']=False
    outputs=[]
    for choice in c.DIAGNOSTICS:
        material=dict(selection=choice,frames=frames,contract=session.contract)
        result=session.pure_consumer('sentinel.diagnostic.v01',material)
        outputs.append(json.loads(caps.values(result[1][0].result.output)['material']))
    assert outputs[0]['checked_sensors']==['rainfall','displacement','reserve'] and not outputs[0]['healthy']
    assert outputs[1]['checked_sensors']==['displacement','reserve'] and outputs[1]['healthy']
    assert not session.executed
    save(session.directory/'contrast.json',dict(results=outputs,provider_calls=0,scope='CONTROLLED_ADMITTED_OPERATION_CONTRAST'))
