"""Independent context and complete supplied-value refusal controls."""
from copy import deepcopy
import json
from pathlib import Path
import pytest
from jsonschema import Draft202012Validator

from hedgehog.gate4_reference_contracts_v01 import (
    ReferenceValueV01, reference_schema_v01, checked, G4_REFERENCE_NUMERIC_V01 as PROFILE,
)
from hedgehog.gate4_strategy_reference_v01 import (
    evaluate_reference_strategy_v01 as strategy, validate_reference_strategy_report_v01 as validate_strategy,
)
from hedgehog.gate4_pressure_budget_v01 import (
    evaluate_reference_pressure_v01 as pressure, allocate_reference_work_budget_v01 as allocate,
    validate_reference_allocation_v01 as validate_allocation,
)
from tests.test_gate4_reference_math_v01 import fixture, seal_strategy, seal_budget


def positive_strategy():
    d=fixture()['strategy']; r=strategy(d,independently_bound_context=d['context'])
    return d,r


def positive_allocation():
    b=fixture()['budget']; p=pressure(b['pressure_inputs'],profile=PROFILE)
    return b,allocate(p,current_budget_context=b)


@pytest.mark.parametrize('field',['recommendation','factor','witness','trace','product','deferred','sets'])
def test_coherently_rehashed_strategy_report_rejected(field):
    d,good=positive_strategy(); altered=good.plain()
    if field=='recommendation': altered['recommendation']='g4_reference:candidate:A'
    if field=='factor': altered['utilities'][0]['factor']+=1
    if field=='witness': altered['witnesses'][0]['differences'][0]['delta']+=1
    if field=='trace': altered['utilities'][0]['terms'][0]['numerator']+=1
    if field=='product': altered['scores'][0]['product']='1'
    if field=='deferred': altered['weak_ir']=not altered['weak_ir']
    if field=='sets': altered['pareto'].pop()
    bad=ReferenceValueV01('strategy_report',altered)
    assert bad.identity!=good.identity
    with pytest.raises(ValueError,match='supplied_report_mismatch'): validate_strategy(bad,inputs=d,source_basis=d['context'])
    assert validate_strategy(good,inputs=d,source_basis=deepcopy(d['context'])).canonical==good.canonical


@pytest.mark.parametrize('field',['weight','allocation','leftover','trace','budget_revision'])
def test_coherently_rehashed_allocation_rejected(field):
    b,good=positive_allocation(); altered=good.plain()
    if field=='weight': altered['rows'][1]['weight']+=1
    if field=='allocation': altered['rows'][0]['allocation']-=1
    if field=='leftover': altered['unallocated']+=1
    if field=='trace': altered['rounds'][0]['remaining']+=1
    if field=='budget_revision': altered['budget']['host_revision']+=1
    bad=ReferenceValueV01('allocation_report',altered)
    with pytest.raises(ValueError,match='supplied_report_mismatch'): validate_allocation(bad,inputs=b['pressure_inputs'],current_budget_context=b)
    assert validate_allocation(good,inputs=b['pressure_inputs'],current_budget_context=deepcopy(b)).canonical==good.canonical


@pytest.mark.parametrize('field',['owner_root_id','task_id','transaction_id','source_snapshot_hash','candidate_set_hash',
    'policy_hash','evaluation_time','catalogue_revision','numeric_profile_hash'])
def test_wrong_independent_context_does_not_inherit_report(field):
    d,good=positive_strategy(); basis=deepcopy(d['context'])
    if field=='evaluation_time': basis[field]+=1
    elif field.endswith('hash'): basis[field]='a'*64
    elif field=='owner_root_id': basis[field]=basis['participants'][1]
    else: basis[field]='g4_reference:other'
    with pytest.raises(ValueError): validate_strategy(good,inputs=d,source_basis=basis)
    assert validate_strategy(good,inputs=d,source_basis=d['context'])==good


def test_independent_budget_revision_and_pressure_inputs():
    b,good=positive_allocation(); changed=deepcopy(b); changed['host_revision']+=1; changed=seal_budget(changed)
    with pytest.raises(ValueError): validate_allocation(good,inputs=changed['pressure_inputs'],current_budget_context=changed)
    p=pressure(b['pressure_inputs'],profile=PROFILE).plain(); p['survivors'][0]['z_fp']+=1
    with pytest.raises(ValueError,match='supplied_report_mismatch'): allocate(ReferenceValueV01('pressure_report',p),current_budget_context=b)
    assert validate_allocation(good,inputs=b['pressure_inputs'],current_budget_context=b)==good


@pytest.mark.parametrize('case',['bool','float','unknown','profile','duplicate','participant','hash','range','weight_sum','term_duplicate','source'])
def test_strict_python_boundaries(case):
    d=fixture()['strategy']; u=d['candidates'][0]['utilities'][0]
    if case=='bool': u['terms'][0]['feature_fp']=True
    if case=='float': u['terms'][0]['feature_fp']=1.0
    if case=='unknown': d['extra']='unknown'
    if case=='profile': d['context']['profile']='other'
    if case=='duplicate': d['candidates'].append(deepcopy(d['candidates'][0]))
    if case=='participant': d['candidates'][0]['participants'].pop()
    if case=='hash': d['candidates'][0]['source_hash']='invalid'
    if case=='range': u['terms'][0]['feature_fp']=10**9+1
    if case=='weight_sum': u['terms'][0]['weight_fp']=1
    if case=='term_duplicate': u['terms'].append(deepcopy(u['terms'][0]))
    if case=='source': u['terms'][0]['source_ref']='g4_reference:foreign'
    with pytest.raises(ValueError):
        d=seal_strategy(d); strategy(d,independently_bound_context=d['context'])
    good=fixture()['strategy']; assert strategy(good,independently_bound_context=good['context']).plain()['status']=='RECOMMENDATION'


@pytest.mark.parametrize('raw',[b'{"a":1,"a":2}',b'{"x":NaN}',b'{"x":Infinity}',b'{"x":1.0}',
    b'{"x":1e3}',b'['*25+b'0'+b']'*25,b' '*262145,b'{"x":'+b'9'*100+b'}',b'\xff',b'{'])
def test_raw_json_refusals(raw):
    with pytest.raises(ValueError): ReferenceValueV01('strategy_input',raw)


def test_immutable_containers_cycles_and_bounded_input():
    d=fixture()['strategy']; obj=ReferenceValueV01('strategy_input',d); identity=obj.identity
    d['candidates'][0]['utilities'][0]['terms'][0]['feature_fp']=0
    copy=obj.plain(); copy['context']['participants'].clear()
    assert obj.identity==identity and len(obj.plain()['context']['participants'])==3
    with pytest.raises((AttributeError,TypeError)): obj.canonical=b'{}'
    cyclic={}; cyclic['self']=cyclic
    with pytest.raises(ValueError,match='container_limit'): ReferenceValueV01('strategy_input',cyclic)
    with pytest.raises(ValueError): ReferenceValueV01('strategy_input',{'x':['x'*256]*513})
    with pytest.raises(ValueError): ReferenceValueV01('strategy_input',{'x':lambda:None})


def test_schema_local_bundle_and_shape_agreement():
    schema=json.loads((Path(__file__).parents[1]/'schemas/gate4_reference_v01.schema.json').read_bytes())
    assert schema==reference_schema_v01(); Draft202012Validator.check_schema(schema)
    validator=Draft202012Validator(schema); d,r=positive_strategy(); b,a=positive_allocation()
    examples=[('strategy_input',d),('strategy_report',r.plain()),('pressure_input',b['pressure_inputs']),
        ('pressure_report',pressure(b['pressure_inputs'],profile=PROFILE).plain()),('budget',b),('allocation_report',a.plain())]
    for kind,value in examples:
        validator.validate(dict(kind=kind,value=value)); ReferenceValueV01(kind,value)
        altered=deepcopy(value); altered['unexpected']=1
        assert not validator.is_valid(dict(kind=kind,value=altered))
        with pytest.raises(ValueError): ReferenceValueV01(kind,altered)
    for invalid in (True,0.5,-10**10):
        bad=deepcopy(d); bad['candidates'][0]['utilities'][0]['terms'][0]['feature_fp']=invalid
        assert not validator.is_valid(dict(kind='strategy_input',value=bad))
        with pytest.raises(ValueError): ReferenceValueV01('strategy_input',bad)


@pytest.mark.parametrize('case',['negative','spent','mandatory_duplicate','mandatory_material','policy','catalogue','cold','unknown_type'])
def test_budget_and_prior_invalid_inputs(case):
    b=fixture()['budget']
    if case=='negative': b['spent']=-1
    if case=='spent': b['spent']=10
    if case=='mandatory_duplicate': b['mandatory'].append(deepcopy(b['mandatory'][0]))
    if case=='mandatory_material': b['mandatory'][0]['material_ref']='g4_reference:foreign'
    if case=='policy': b['original_policy_ref']='g4_reference:foreign'
    if case=='catalogue': b['pressure_inputs']['branches'][0]['catalogue_revision']='g4_reference:foreign'
    if case=='cold': b['pressure_inputs']['branches'][0]['prior']['value']=1
    if case=='unknown_type': b['pressure_inputs']['branches'][0]['prior']['disposition']='NEW'
    with pytest.raises(ValueError):
        b=seal_budget(b); allocate(pressure(b['pressure_inputs'],profile=PROFILE),current_budget_context=b)
    assert positive_allocation()[1].plain()['status']=='ALLOCATED'


@pytest.mark.parametrize('field',['owner_root_id','task_id','transaction_id','evaluation_time','policy_hash','source_snapshot_ref'])
def test_coherent_foreign_report_rejected_by_original_source(field):
    d,good=positive_strategy(); changed=deepcopy(d)
    if field=='evaluation_time': changed['context'][field]+=1
    elif field=='owner_root_id': changed['context'][field]=changed['context']['participants'][1]
    elif field=='policy_hash': changed['context'][field]='a'*64
    else: changed['context'][field]='g4_reference:foreign'
    changed=seal_strategy(changed)
    other=strategy(changed,independently_bound_context=deepcopy(changed['context']))
    assert other.identity!=good.identity
    with pytest.raises(ValueError,match='supplied_report_mismatch'):
        validate_strategy(other,inputs=d,source_basis=d['context'])
    assert validate_strategy(good,inputs=d,source_basis=d['context'])==good


def test_canonical_input_size_and_depth_before_math():
    # All leaves individually fit; the aggregate still exceeds the input cap.
    huge={'g4_reference:key'+str(i):['x'*256]*100 for i in range(20)}
    with pytest.raises(ValueError,match='input_size'): ReferenceValueV01('strategy_input',huge)
    nested=0
    for _ in range(25): nested=[nested]
    with pytest.raises(ValueError,match='structure_limit'): ReferenceValueV01('strategy_input',nested)
    d,r=positive_strategy()
    assert ReferenceValueV01('strategy_input',ReferenceValueV01('strategy_input',d).canonical).plain()==d
