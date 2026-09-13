"""Bounded semantic inputs and real non-oracular sensitivity controls."""
from dataclasses import replace
import json
from pathlib import Path
import pytest
from hedgehog.domains.testflix import contracts_v01 as c
from hedgehog.domains.testflix import semantic_adapter_v01 as s
from hedgehog.domains.testflix import evidence_v01 as e
from hedgehog.domains.testflix import mock_world_v01 as world


def request_v01():
    return c.request_from_plain_v01(json.loads((Path(__file__).resolve().parents[1]/'demo/testflix_fixtures_v01.json').read_text()))


@pytest.mark.parametrize('case,change,reason',(
    ('N01',dict(selected_plan_id='plan:unknown'),'unknown_plan'),
    ('N02',dict(selected_plan_id='plan:ef62'),'over_budget'),
    ('N03_authority',dict(authority=True),'semantic_output_shape'),
    ('N03_amount',dict(amount=1),'semantic_output_shape'),
    ('N03_endpoint',dict(endpoint='https://invalid.invalid'),'semantic_output_shape'),
    ('N04',None,'semantic_output_shape'),
))
def test_bounded_semantic_refusal_before_effect(case,change,reason):
    request = request_v01()
    projection = s.role_projection_v01(request,'orchestrator')
    original = s.controlled_provider_v01('orchestrator',projection)
    equivalent = dict(original)
    assert equivalent is not original
    assert s.validate_contribution_v01(equivalent,'orchestrator',dict(projection),request)==c.plan_by_id_v01(request,original['selected_plan_id'])
    before = tuple(world.CALLS)
    def invalid_provider(role, actual_projection):
        output = s.controlled_provider_v01(role,actual_projection)
        if change is None:
            del output['selected_plan_id']
        else:
            output.update(change)
        return output
    with pytest.raises(ValueError,match='^'+reason+'$'):
        e.TestflixHandlerV01().handle_v01(request,invalid_provider)
    assert tuple(world.CALLS)==before
    print(case+': actual semantic refusal='+reason+'; zero capability calls')


def test_C01_always_same_selector_fails_sensitivity_control():
    a=request_v01();b=replace(a,preference='QUALITY')
    assert a.catalog==b.catalog and a.hard_ceiling_minor==b.hard_ceiling_minor
    real_a=s.collect_semantics_v01(a);real_b=s.collect_semantics_v01(b)
    assert real_a['selected_plan']!=real_b['selected_plan']
    def constant_selector(role,projection):
        return dict(s.controlled_provider_v01(role,projection),selected_plan_id=real_a['selected_plan'].plan_id)
    bad_a=s.collect_semantics_v01(a,constant_selector)
    bad_b=s.collect_semantics_v01(b,constant_selector)
    with pytest.raises(AssertionError):
        assert bad_a['selected_plan']!=bad_b['selected_plan']
    print('C01: sensitivity control rejects an always-same selector, despite valid output shapes')


def test_N06_actual_projection_privacy_and_device_policy():
    request=request_v01()
    projections={r:s.role_projection_v01(request,r) for r in ('orchestrator','architect','selector','reviewer','user','bank','provider','device')}
    body=json.dumps(projections)
    assert request.bank_private not in body and request.user_private not in body
    assert 'preference' not in projections['bank'] and 'content_id' not in projections['bank']
    assert 'merchant_id' not in projections['device'] and 'catalog' not in projections['device']
    with pytest.raises(ValueError,match='^device_not_registered$'):
        c.validate_request_v01(replace(request,device_id='device:guest'))


def test_request_schema_does_not_admit_scenario_oracles():
    body=json.loads((Path(__file__).resolve().parents[1]/'demo/testflix_fixtures_v01.json').read_text())
    for key in ('act_id','expected_status','desired_plan'):
        with pytest.raises(ValueError,match='^request_shape$'):
            c.request_from_plain_v01(dict(body,**{key:'not-an-input'}))
