"""Exact generated-ID classification at the real producer/projection boundary."""
import copy
from pathlib import Path
import pytest
from demo import run_gate6_retained_obligations_v01 as x

ROOT=Path(__file__).resolve().parents[1]
ID='drsmeaning_v01:a3b6b4727137283a9057070714634f5ff6ae158c7df7b4f999c12ddcd121eb33'

@pytest.fixture(scope='module')
def generated():
    g=x.decode(x.read(ROOT/'docs/gate6_reference_v01/evidence/retained_obligations/exact_writeback_inputs.json'))
    proposal,rh,edge=x.resolver._g2b_validate_root_reviewed_writeback_geometry_v01(**g)
    wrapper=x.resolver._g2b_storage_record_v01(meaning_record=g['successor_record'],writeback_metadata=dict(
        writeback_proposal_id=proposal,root_result_binding_hash=rh,supersession_evidence_id=edge.lineage_edge_id,
        root_decision_id=g['root_decision_result'].decision_id))
    return g,wrapper

def project(g,w):
    result=x.compat.project_legacy_drs_source_v01(source_family='LOCAL_DRS_DICT',source=w,
        target_semantic_address=g['successor_record'].semantic_address,target_meaning_record=None)
    assert x.compat.validate_legacy_drs_projection_v01(result)==(True,())
    return result

def test_exact_generated_wrapper_all_locations(generated):
    g,w=generated
    assert w['provenance']['request_id']=='request:'+ID
    refs=[w['provenance']['trace_refs'][0],w['trace_refs'][0],w['source_refs'][0]['trace_ref']]
    assert all(r['trace_id']=='trace:'+ID for r in refs)
    assert x.address._secret_reason(ID) is None
    assert x.address._secret_reason('request:'+ID)=='drs_secret_payload_forbidden'
    assert x.compat._nonempty_text('request:'+ID) is False
    assert project(g,w).projection_status=='CANONICAL_CONTEXT_ONLY'
    assert w==generated[1]

HEX=ID.split(':')[1]
NEAR=[f'request:drsmeaning_v01:{v}' for v in (HEX[:-1],HEX+'a',HEX.upper(),HEX[:-1]+'g')]+[
    'request:other_v01:'+HEX,'request:request:'+ID,'leading request:'+ID,'request:'+ID+' tail',
    'request:'+ID+'\n','trace:'+ID+'\n','request:9057070714634','trace:9057070714634',
    'request:'+ID+' password=synthetic','trace:'+ID+' Bearer synthetic',
    'request:'+ID+' GB82 WEST 1234 5698 7654 32','trace:'+ID+' 4111-1111-1111-1111']
@pytest.mark.parametrize('text',NEAR+['1'*n for n in range(13,20)]+['4111 1111 1111 1111','4111-1111-1111-1111','password=synthetic','Bearer synthetic'])
def test_secret_near_misses_through_public_projection(generated,text):
    g,base=generated;w=copy.deepcopy(base)
    assert x.compat._GENERATED_MEANING_WRAPPER_ID.fullmatch(text) is None
    assert x.address._secret_reason(text)=='drs_secret_payload_forbidden'
    w['content']['nested']={'innocent_name':[{'text':text}]}
    with pytest.raises(ValueError,match='^drs_secret_payload_forbidden$'):project(g,w)

@pytest.mark.parametrize('path',[
    ('provenance','request_id'),('provenance','trace_refs',0,'trace_id'),('trace_refs',0,'trace_id'),('source_refs',0,'trace_ref','trace_id')])
def test_each_identity_screen_rejects_secret_sibling(generated,path):
    g,base=generated;w=copy.deepcopy(base);part=w
    for k in path[:-1]:part=part[k]
    part[path[-1]]='trace:9057070714634'
    with pytest.raises(ValueError):project(g,w)
    assert project(g,base).projection_status=='CANONICAL_CONTEXT_ONLY'
