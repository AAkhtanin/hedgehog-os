"""Frozen saved-input checks. No per-control native recollection or live Host."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import shutil
import os
import subprocess
import sys
import pytest
from tests.test_gate4_reference_native_v01 import native_story
from hedgehog import gate4_reference_evidence_v01 as e
from hedgehog.gate4_reference_contracts_v01 import digest,G4_REFERENCE_NUMERIC_V01
from hedgehog.gate4_pressure_budget_v01 import evaluate_reference_pressure_v01,allocate_reference_work_budget_v01


@pytest.fixture(scope='session')
def saved_package(request):
    supplied=os.environ.get('G44_SAVED_PACKAGE')
    if supplied:
        package=Path(supplied)
        trust=e.read_json_v01(package.parent/'TEST_SUPPLIED_PIN.json')
        output=Path(os.environ['G44_COMMAND_DIR'])/'proof_controls';output.mkdir()
        return dict(package=package,trust=trust,root=package/'story',result=None,evidence=output)
    native_story=request.getfixturevalue('native_story')
    root=native_story['journal'].directory;candidate=Path(e.__file__).resolve().parents[1]
    paths=sorted(set(p.relative_to(candidate).as_posix() for p in candidate.rglob('*gate4*') if p.is_file() and p.suffix in ('.py','.json','.md')))
    # Explicit common source bodies support the original native/proof provenance.
    paths+=['hedgehog/kernel/work_composition_v01.py','hedgehog/work_execution_host_v01.py','hedgehog/kernel/root_decision_v01.py',
        'hedgehog/kernel/effect_firewall_v01.py','hedgehog/kernel/abi_v01.py','hedgehog/kernel/semantic_work_v01.py',
        'hedgehog/outcome_feedback_v01.py','hedgehog/outcome_feedback_history_v01.py','hedgehog/outcome_calibration_v01.py',
        'hedgehog/domains/airline/semantic_to_contract_binding_v01.py','hedgehog/domains/airline/incident_atlas_work_v01.py']
    ledger={name:e._body(candidate/name) for name in paths}
    ledger_path=root.parent/'portable_sources.json';e._write(ledger_path,ledger)
    package=root.parent/'portable_package'
    result=e.export_package_v01(saved_inputs=root,source_root=candidate,source_ledger=ledger_path,output=package)
    trust=dict(profile='G43_EXTERNAL_PIN_V01',status='TEST_SUPPLIED_PIN',publication_sha256=result['publication_sha256'])
    e._write(root.parent/'test_trust.json',trust)
    return dict(package=package,trust=trust,root=root,result=result)


def test_g43_saved_positive_and_test_pin(saved_package):
    p=saved_package
    result=e.verify_package_v01(package=p['package'],trust=p['trust'])
    assert result['status']=='TEST_PIN_SUPPORTED_PASS'
    assert result['result']['native_replay']=='UNSUPPORTED_NATIVE_SCHEMA'
    assert not result['result']['permission_restored']
    e._write(p.get('evidence',p['root'].parent)/'supported_result.json',result)


def test_g43_external_pin_and_source_controls(saved_package,tmp_path):
    p=saved_package
    for trust in (None,dict(p['trust'],publication_sha256='0'*64)):
        with pytest.raises(ValueError):e.verify_package_v01(package=p['package'],trust=trust)
    copy=tmp_path/'package';shutil.copytree(p['package'],copy)
    source=copy/'sources/hedgehog/gate4_reference_runtime_v01.py';body=source.read_bytes()
    source.write_bytes(body+b'\n')
    with pytest.raises(ValueError):e.verify_package_v01(package=copy,trust=p['trust'])
    source.unlink()
    with pytest.raises(ValueError):e.verify_package_v01(package=copy,trust=p['trust'])
    source.write_bytes(body)
    assert e.verify_package_v01(package=copy,trust=p['trust'])['status']=='TEST_PIN_SUPPORTED_PASS'


@pytest.mark.parametrize('case',['quota','prior','root','offer','result','expired_event','history_head','native_copy','claim_copy'])
def test_g43_semantic_controls_with_resealed_test_pin(saved_package,tmp_path,case):
    """Fresh outer hashes must not legalize an invalid source relationship."""
    p=saved_package;copy=tmp_path/'package';shutil.copytree(p['package'],copy)
    relative='story/cold/allocation_before_install.json' if case in ('quota','prior') else (
        'story/observed_g3.json' if case in ('native_copy','claim_copy') else
        'story/history_recorded.json' if case=='history_head' else 'story/cold/domain_consumption.json')
    path=copy/relative;value=e.read_json_v01(path)
    if case in ('quota','prior'):
        b=value['budget'];pressure=b['pressure_inputs']
        if case=='quota':
            from hedgehog.gate4_reference_runtime_v01 import local_id_v01
            for row in pressure['branches']:row['lower']=row['upper']=6 if row['id']==local_id_v01('branch','offer_0') else 1
        else:pressure['branches'][0]['prior'].update(value=500000000,disposition='USABLE')
        pressure['context']['source_snapshot_hash']=digest(pressure['branches']);pressure['context']['candidate_set_hash']=digest([r['id'] for r in pressure['branches']]);b['context']=deepcopy(pressure['context'])
        value['allocation']=allocate_reference_work_budget_v01(evaluate_reference_pressure_v01(pressure,profile=G4_REFERENCE_NUMERIC_V01),current_budget_context=b).plain()
    elif case=='root':value['current_reviews']['reviews'][e.a.ROOT]=value['current_reviews']['reviews'][e.a.binding.BANK_ROOT_ID]
    elif case=='offer':value['hold']['offer_id']='g40:offer:1'
    elif case=='result':value['current_reviews']['local'][e.a.ROOT]['producer']['artifact_id']='foreign_result'
    elif case=='expired_event':value['current_use']['evaluation_time']=value['current_use']['valid_to']
    elif case=='native_copy':value['native']['native']['plan_artifact_ref']='another_nonempty_plan'
    elif case=='claim_copy':value['claim']['artifact_id']='another_claim'
    else:value['head']['record_id']='different_record'
    e._write(path,value)
    manifest=e.read_json_v01(copy/'MANIFEST.json')
    for row in manifest['entries']:
        if row['path']==relative:row.update(e._body(path))
    e._write(copy/'MANIFEST.json',manifest)
    publication=e.read_json_v01(copy/'PUBLICATION.json');publication['manifest_sha256']=e._body(copy/'MANIFEST.json')['sha256'];e._write(copy/'PUBLICATION.json',publication)
    trust=dict(p['trust'],publication_sha256=e._body(copy/'PUBLICATION.json')['sha256'])
    with pytest.raises(ValueError) as error:e.verify_package_v01(package=copy,trust=trust)
    assert not any(word in str(error.value) for word in ('member_identity','wrong_independent_pin','publication_binding'))
    e._write(p.get('evidence',p['root'].parent)/('negative_'+case+'.json'),dict(case=case,trust=trust,reason=str(error.value),mutation=value,
        scope='CONTROL_ONLY_NOT_GENUINE_EXECUTION',outer_integrity='RESEALED_TEST_PIN'))


def test_g44_history_same_root_other_genuine_subject_refuses(saved_package):
    root=saved_package['root'];record=e.read_json_v01(root/'history_recorded.json')
    stored=e.read_json_v01(root/'history/epochs'/(record['head']['snapshot_id']+'.json'))
    other=e.read_json_v01(root/'observed_g3.json')['root_records']
    _,result=e.a.feedback.g35_validate_root_v01(other)
    assert result.decision=='ACCEPT' and result.target_root_id==e.a.ROOT
    with pytest.raises(ValueError,match='history_exact_subject'):
        e.validate_history_subject_v44(record['snapshot'],other,stored['meaning'])
    e.validate_history_subject_v44(record['snapshot'],record['root_records'],stored['meaning'])


def test_g44_missing_checker_dependency_refuses(saved_package,tmp_path):
    p=saved_package;copy=tmp_path/'package';shutil.copytree(p['package'],copy)
    m=e.read_json_v01(copy/'MANIFEST.json');del m['checker_source_ledger']['hedgehog/outcome_calibration_v01.py']
    e._write(copy/'MANIFEST.json',m)
    publication=e.read_json_v01(copy/'PUBLICATION.json');publication['manifest_sha256']=e._body(copy/'MANIFEST.json')['sha256'];e._write(copy/'PUBLICATION.json',publication)
    with pytest.raises(ValueError,match='checker_dependency_inventory'):
        e.verify_package_v01(package=copy,trust=dict(p['trust'],publication_sha256=e._body(copy/'PUBLICATION.json')['sha256']))


def test_g44_preloaded_alternative_origin_core_mismatch_refuses(saved_package,tmp_path):
    import hedgehog.outcome_calibration_v01 as calibration
    foreign=tmp_path/'outcome_calibration_v01.py';foreign.write_bytes(Path(calibration.__file__).read_bytes()+b'\n# Isolated changed installed core.\n')
    script="""import importlib.util,json,sys
from pathlib import Path
from hedgehog import gate4_reference_evidence_v01 as e
name='hedgehog.outcome_calibration_v01'
spec=importlib.util.spec_from_file_location(name,sys.argv[1]);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m)
try:e.verify_package_v01(package=sys.argv[2],trust=json.loads(sys.argv[3]))
except ValueError as exc:
 print(str(exc));assert 'checker_source_binding:hedgehog/outcome_calibration_v01.py' in str(exc)
else:raise AssertionError('altered installed module accepted')
"""
    r=subprocess.run([sys.executable,'-B','-c',script,str(foreign),str(saved_package['package']),json.dumps(saved_package['trust'])],capture_output=True,text=True)
    assert r.returncode==0,r.stdout+r.stderr
    assert e.verify_package_v01(package=saved_package['package'],trust=saved_package['trust'])['status']=='TEST_PIN_SUPPORTED_PASS'
