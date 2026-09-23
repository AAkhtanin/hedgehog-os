"""Saved release and finite registry controls; never collect legacy runtimes."""
from copy import deepcopy
from pathlib import Path
import os
import pytest
from hedgehog import gate4_reference_release_v01 as r

ROOT=Path(r.__file__).resolve().parents[1]

def test_g44_current_registry_and_historical_geometry():
    checked=r.validate_registration_v01(ROOT)
    assert checked['registration']['historical_counts']==dict(acts=12,seams=24,current_schemas=16,retired_schemas=2)
    from demo import run_living_gauntlet_v01 as l
    assert not l._validate_completion_manifest_v01(r.read(ROOT/r.REGISTRY_PATHS[0]))
    assert not l._validate_integration_seam_index_v01(r.read(ROOT/r.REGISTRY_PATHS[1]))
    assert not l._validate_completion_manifest_v01(checked['historical'][r.REGISTRY_PATHS[0]])
    assert not l._validate_integration_seam_index_v01(checked['historical'][r.REGISTRY_PATHS[1]])

@pytest.mark.parametrize('mutation',['old_record','unknown_field','missing_dependency','wrong_consumer','source_pin'])
def test_g44_closed_registry_refusals(mutation):
    path=r.REGISTRY_PATHS[0];v=deepcopy(r.read(ROOT/path))
    if mutation=='old_record':v['active_runtime_acts'][0]['status']='OTHER'
    elif mutation=='unknown_field':v[r.KEY]['unknown']=True
    elif mutation=='missing_dependency':del v[r.KEY]['sources']['hedgehog/gate4_reference_runtime_v01.py']
    elif mutation=='wrong_consumer':v[r.KEY]['symbols']['verifier']='other:validator'
    else:v[r.KEY]['sources']['hedgehog/gate4_reference_runtime_v01.py']['sha256']='0'*64
    with pytest.raises(ValueError):r.historical_projection_v01(v,path,root=ROOT)
    r.historical_projection_v01(r.read(ROOT/path),path,root=ROOT)

def test_g44_retained_parent_supplied_controls():
    p=Path(os.environ['G44_PARENT']);pin=(p.parent/'PARENT_PIN.txt').read_text().strip()
    result=r.validate_parents_v01(directory=p,expected_manifest_sha256=pin,root=ROOT)
    assert result['collectors']==0 and result['living_status']=='PASS' and result['conformance_status']=='PASS'
    with pytest.raises(ValueError,match='parent_manifest_pin'):
        r.validate_parents_v01(directory=p,expected_manifest_sha256='0'*64,root=ROOT)
