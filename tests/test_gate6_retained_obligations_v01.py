"""Finite supplied witnesses and targeted mutations; never recollect an effect."""
import copy
import dataclasses as dc
from pathlib import Path
import pytest
from demo import run_gate6_retained_obligations_v01 as p

DATA=Path(__file__).resolve().parents[1]/'docs/gate6_reference_v01/evidence/retained_obligations'

def witness(name):
    return p.decode(p.read(DATA/name/'witness.json'))

@pytest.mark.parametrize('family',tuple(p.CHECKS))
def test_supplied_positive_no_new_runtime(family,tmp_path):
    value=witness(family)
    checked=p.observed(tmp_path,'supplied_'+family,p.pure_functions(),lambda:p.CHECKS[family](value))
    p.check_counts(checked['observation'],{})
    assert checked['value']['row'] in ('N1-05','N4-04','N4-05','N4-07')

@pytest.mark.parametrize('mutation',('candidate','root','state','counter'))
def test_avf_actual_bindings(mutation):
    value=witness('avf')
    if mutation=='candidate':value['candidate']=dc.replace(value['candidate'],candidate_id='candidate:other')
    elif mutation=='root':value['root']=value['missing_root']
    elif mutation=='state':value['after_effect']['state_counters']['mock_effect_execution_count']=2
    else:value['accepted']['observation']['counts']['effect']=0
    with pytest.raises(ValueError):p.check_avf(value)
    p.check_avf(witness('avf'))

@pytest.mark.parametrize('mutation',('business','answer','counter','warm_root'))
def test_reuse_actual_binding_and_arithmetic(mutation):
    value=witness('reuse')
    if mutation=='business':
        value['business_warm']['inputs']['reference']=11
        value['business_cold']=copy.deepcopy(value['business_warm'])
    elif mutation=='answer':value['warm']['value']['answer']['answer']['total']=28
    elif mutation=='counter':value['warm']['observation']['counts']['host_work']=1
    else:value['warm']['value']['root']=value['cold_root']
    with pytest.raises(ValueError):p.check_reuse(value)
    p.check_reuse(witness('reuse'))

@pytest.mark.parametrize('mutation',('lineage','current','old_certificate','returned_summary'))
def test_policy_independent_current_derivation(mutation):
    value=witness('policy')
    if mutation=='lineage':
        value['stored'][0]['content']['root_decision_id']='root:other'
        value['stored'][1]['content']['root_decision_id']='root:other'
    elif mutation=='current':
        value['current']['derived_current']=value['geometry']['predecessor_record'].meaning_record_id
        value['current']['claim']['current_record_id']=value['current']['derived_current']
    elif mutation=='old_certificate':value['fresh']=value['historical']
    else:value['current']['answer']=value['geometry']['predecessor_record'].safe_summary
    with pytest.raises(ValueError):p.check_policy(value)
    p.check_policy(witness('policy'))

@pytest.mark.parametrize('mutation',('private','upstream','capture','consumed'))
def test_privacy_independent_projection_oracle(mutation):
    value=witness('privacy');record=value['semantics']['contributions'][1]
    if mutation=='private':
        record['projection']['bank_private']=value['sealed']['payload']['request']['bank_private']
        value['responses'][1]['projection']=copy.deepcopy(record['projection'])
    elif mutation=='upstream':
        record['projection']['upstream'][0]['output']['summary']='Coherently changed but not the prior actual output.'
        value['responses'][1]['projection']=copy.deepcopy(record['projection'])
    elif mutation=='capture':record['capture']['transport']['attempt']=19
    else:value['sealed']['payload']['quote']['results'][0]['invocation']['inputs'][0]['value']=123
    # Keep the duplicated semantic projection coherent; the expected value is not copied from it.
    value['sealed']['payload']['semantics']=copy.deepcopy(value['semantics'])
    with pytest.raises(ValueError):p.check_privacy(value)
    p.check_privacy(witness('privacy'))
