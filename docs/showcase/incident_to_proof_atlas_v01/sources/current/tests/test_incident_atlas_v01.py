"""Small index and standalone supplied-proof checks; no implicit collection."""
from hedgehog import incident_atlas_v01 as atlas
import copy
import json
import os
from pathlib import Path

import pytest


def test_atlas_pending_inventory_v01():
    index = atlas.coverage_v01()
    assert len(index['cards']) == len({r['id'] for r in index['cards']}) == 20
    assert len(index['claims']) == 15
    assert all(r['status'] == 'PENDING' and not r['evidence_refs'] for r in index['cards'])
    assert index['variants']['D1']['status'] == 'PENDING'
    assert 'risk_source:W4' in {r['id'] for r in index['risk_sources']}


@pytest.fixture(scope='module')
def saved_package():
    directory=os.environ.get('AT1_SAVED_EXPORT')
    assert directory, 'AT1_SAVED_EXPORT required; tests never collect a replacement'
    return (json.loads((Path(directory)/'atlas_package.json').read_bytes()),
            json.loads((Path(directory)/'expected_pin.json').read_bytes()))


def test_atlas_supplied_replay_positive_v01(saved_package):
    package,pin=saved_package
    result=atlas.verify_v01(package,expected_pin=pin)
    expected=['A1','A2','A3','A4','S1','S2','S3','S4'] if package['airline'] is not None else ['S1','S2','S3','S4']
    if package['testflix'] is not None:expected+=['T1','T2','T3','T4']
    if package['workspace'] is not None:expected+=['W1','W2','W3','W4']
    if package['sentinel'] is not None:expected=sorted(expected+['N1','N2','N3','N4'])
    assert result['cards']==expected
    assert result['execution']=='PURE_REPLAY'
    assert result['counts']['unique_experience_consumers']==1+(package['airline'] is not None)+(package['testflix'] is not None)+(package['workspace'] is not None)+(package['sentinel'] is not None)
    assert sum(r['status']=='PENDING' for r in package['coverage']['cards'])==20-len(expected)
    assert package['coverage']['variants']['D1']['status']==('COMPLETED' if package['workspace'] is not None else 'PENDING')
    assert package['coverage']['variants']['D2']['status']=='COMPLETED'
    assert package['coverage']['variants']['D3']['status']=='COMPLETED'


def test_atlas_wrong_external_pin_v01(saved_package):
    package,pin=saved_package
    with pytest.raises(ValueError,match='atlas_external_pin_mismatch'):
        atlas.verify_v01(package,expected_pin=dict(pin,package_sha256='0'*64))


def test_atlas_rehashed_foreign_source_v01(saved_package):
    package,pin=saved_package
    altered=copy.deepcopy(package)
    altered['implementation']['hedgehog/incident_atlas_v01.py']='0'*64
    with pytest.raises(ValueError,match='atlas_implementation_source_identity'):
        atlas.verify_v01(altered,expected_pin=dict(pin,package_sha256=atlas.digest_v01(altered)))


def test_atlas_rehashed_false_relationship_v01(saved_package):
    package,pin=saved_package
    altered=copy.deepcopy(package)
    row=next(r for r in altered['supplier']['channels']['rows'] if r['label']=='foreign_task_read_B')
    row['contract_errors']=[]
    row['record_id']=atlas.digest_v01({k:v for k,v in row.items() if k not in ('record_id','label','elapsed_seconds')})
    with pytest.raises(ValueError,match='atlas_contract_reason_binding'):
        atlas.verify_v01(altered,expected_pin=dict(pin,package_sha256=atlas.digest_v01(altered)))


def test_atlas_rehashed_presentation_invention_v01(saved_package):
    package,pin=saved_package
    altered=copy.deepcopy(package)
    altered['cards']['S2']['experience']='ROOT_RECORDED'
    with pytest.raises(ValueError,match='atlas_projection_semantic_relationship'):
        atlas.verify_v01(altered,expected_pin=dict(pin,package_sha256=atlas.digest_v01(altered)))


def test_atlas_no_silent_collection_resume_v01(tmp_path):
    with pytest.raises(ValueError,match='atlas_collection_directory_already_exists'):
        atlas.collect_v01(tmp_path)
