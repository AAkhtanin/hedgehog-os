"""Small role/projection controls; no D/E runner or external transport."""
from copy import deepcopy
from dataclasses import replace
import pytest
from tests.test_testflix_contracts_v01 import request_v01
from hedgehog.domains.testflix import semantic_roles_v01 as roles
from hedgehog.domains.testflix import semantic_adapter_v01 as adapter
from hedgehog.domains.testflix import contracts_v01 as c
from hedgehog.domains.testflix import mock_world_v01 as world


def test_distinct_duties_consume_upstream_and_preference_v01():
    request = request_v01()
    before = tuple(world.CALLS)
    a = adapter.collect_semantics_v01(request, roles.ControlledRolesV01())
    b = adapter.collect_semantics_v01(replace(request, preference='QUALITY'), roles.ControlledRolesV01())
    assert a['selected_plan'] != b['selected_plan']
    assert len({tuple(sorted(r['output'])) for r in a['contributions']}) == 4
    assert tuple(r['role'] for r in a['contributions']) == roles.ROLES
    assert a['mode'] == b['mode'] == 'CONTROLLED_ROLE_DUTIES'
    assert a['contributions'][3]['projection']['upstream'][2]['output'] == a['contributions'][2]['output']
    assert roles.validate_records_v01(request, deepcopy(a['contributions']), mode=a['mode']) == a['selected_plan']
    for record in a['contributions']:
        body = c.canonical_v01(record['projection']).decode()
        assert request.bank_private not in body and request.user_private not in body
        assert 'approved_prices_minor' not in record['projection']
        assert record['projection']['task_contract']['price_unit'] == 'minor currency units'
        required = record['projection']['task_contract']['required_inputs']
        assert set(required) <= set(record['projection'])
    assert tuple(world.CALLS) == before


def test_finite_intent_scope_does_not_override_model_refusal_v09():
    request = request_v01()
    projection = roles.projection_v01(request, roles.ROLES[0], [])
    assert projection['task_contract']['required_inputs'] == ['preference', 'hard_ceiling_minor', 'currency']
    response = dict(preference='AD_FREE', priorities=['Ad-free experience'],
        missing_evidence=['Content type', 'Usage patterns', 'Specific features'],
        summary='The required-evidence refusal is retained, not silently normalized away.')
    before = tuple(world.CALLS)
    with pytest.raises(ValueError, match='^role_required_evidence_missing$'):
        roles.validate_output_v01(response, roles.ROLES[0], projection, request)
    assert tuple(world.CALLS) == before


def test_quality_definition_shared_without_overriding_review_v09():
    request = replace(request_v01(), preference='QUALITY')
    result = adapter.collect_semantics_v01(request, roles.ControlledRolesV01())
    definitions = [r['projection']['task_contract']['preference_definition'] for r in result['contributions']]
    assert all(d == definitions[0] for d in definitions)
    assert definitions[0]['priority_order'] == ['resolution descending', 'ads false before true',
        'price_minor ascending', 'plan_id ascending']
    assert result['selected_plan'].resolution == max(p.resolution for p in request.catalog
        if p.price_minor <= request.hard_ceiling_minor)
    record = result['contributions'][-1]
    refused = dict(record['output'], supports_selection=False, blocking_conflicts=['Independent disagreement'])
    with pytest.raises(ValueError, match='^semantic_review_disagreement$'):
        roles.validate_output_v01(refused, record['role'], record['projection'], request)
    first = result['contributions'][0]
    transport = dict(first['capture']['transport'], attempt=17)
    assert roles.capture_v01(request, first['role'], first['projection'], first['output'], transport)['transport']['attempt'] == 17
    with pytest.raises(ValueError, match='^semantic_transport_values$'):
        roles.capture_v01(request, first['role'], first['projection'], first['output'], dict(transport, attempt=21))
    ad_free = roles.projection_v01(request_v01(), roles.ROLES[0], [])
    assert 'preference_definition' not in ad_free['task_contract']


def test_live_prefix_does_not_relabel_controlled_or_complete_replay_v09(tmp_path):
    from hedgehog.domains.testflix.live_semantic_adapter_v01 import LiveSemanticProviderV01, ACTUAL_CALLS
    request = request_v01()
    result = adapter.collect_semantics_v01(request, roles.ControlledRolesV01())
    records = list(result['contributions'])
    calls = tuple(ACTUAL_CALLS)
    with pytest.raises(ValueError, match='^live_captured_prefix_shape$'):
        LiveSemanticProviderV01(directory=tmp_path / 'not-created', captured_prefix=records)
    with pytest.raises(ValueError, match='^live_captured_prefix_origin$'):
        LiveSemanticProviderV01(directory=tmp_path / 'not-created', captured_prefix=records[:2])
    assert not (tmp_path / 'not-created').exists() and tuple(ACTUAL_CALLS) == calls


@pytest.mark.parametrize('case', ('missing_terms', 'wrong_price', 'authority', 'disagreement',
    'missing_evidence', 'changed_input', 'changed_capture', 'changed_upstream'))
def test_role_boundaries_refuse_coherent_inputs_v01(case):
    request = request_v01()
    good = adapter.collect_semantics_v01(request, roles.ControlledRolesV01())
    records = deepcopy(list(good['contributions']))
    if case == 'missing_terms': records[1]['output']['terms'].pop()
    elif case == 'wrong_price': records[1]['output']['terms'][0]['price_minor'] += 1
    elif case == 'authority': records[3]['output']['action_permission'] = True
    elif case == 'disagreement': records[3]['output']['supports_selection'] = False
    elif case == 'missing_evidence': records[0]['output']['missing_evidence'] = ['intent']
    elif case == 'changed_input': request = replace(request, preference='QUALITY')
    elif case == 'changed_capture': records[0]['capture']['request_ref'] = 'not-this-request'
    else: records[2]['projection']['upstream'][0]['output']['preference'] = 'QUALITY'
    # Reconstruct identities for semantic mutations; rejection must not depend
    # solely on an obsolete digest or raw JSON checksum.
    if case in ('missing_terms', 'wrong_price', 'authority', 'disagreement', 'missing_evidence'):
        for record in records:
            transport = dict(record['capture']['transport'],
                raw_response=c.canonical_v01(record['output']).decode())
            record['capture'] = roles.capture_v01(request, record['role'], record['projection'], record['output'], transport)
    before = tuple(world.CALLS)
    with pytest.raises(ValueError):
        roles.validate_records_v01(request, records, mode=good['mode'])
    assert tuple(world.CALLS) == before
    original = request_v01()
    assert roles.validate_records_v01(original, good['contributions'], mode=good['mode']) == good['selected_plan']
