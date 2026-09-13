"""Small role/projection controls; no D/E runner or external transport."""
from copy import deepcopy
from dataclasses import replace
import pytest
from tests.test_testflix_contracts_v01 import request_v01
from hedgehog.domains.testflix import semantic_roles_v01 as roles
from hedgehog.domains.testflix import semantic_adapter_v01 as adapter
from hedgehog.domains.testflix import contracts_v01 as c
from hedgehog.domains.testflix import mock_world_v01 as world


def _synthetic_live_records_v10():
    request = request_v01()
    records = []
    producer = roles.ControlledRolesV01()
    for role in roles.ROLES:
        projection = roles.projection_v01(request, role, records)
        output, transport = producer.respond_v01(role, projection, roles.request_ref_v01(request))
        transport = dict(transport, origin_mode='LIVE', provider='OFFLINE_TRANSPORT_DOUBLE')
        records.append(dict(role=role, projection=projection, output=output,
            capture=roles.capture_v01(request, role, projection, output, transport)))
    return request, records


@pytest.mark.parametrize('case', ('valid', 'equivalent', 'capture_id', 'response_ref', 'request_ref',
    'projection_ref', 'raw_output', 'capture_extra', 'record_extra', 'malformed_capture', 'order', 'unused'))
def test_captured_public_entry_validates_saved_identities_v10(case):
    import json
    from hedgehog.domains.testflix.live_semantic_adapter_v01 import CapturedSemanticProviderV01, ACTUAL_CALLS
    request, original = _synthetic_live_records_v10()
    records = deepcopy(original)
    if case in ('capture_id', 'response_ref', 'request_ref', 'projection_ref'):
        records[0]['capture'][case] = 'changed-saved-identity'
    elif case == 'raw_output':
        records[0]['capture']['transport']['raw_response'] = json.dumps(dict(records[0]['output'], summary='Different raw value'))
    elif case == 'capture_extra': records[0]['capture']['unknown'] = True
    elif case == 'record_extra': records[0]['unknown'] = True
    elif case == 'malformed_capture': records[0]['capture'] = None
    elif case == 'order': records[0], records[1] = records[1], records[0]
    elif case == 'unused': records.append(deepcopy(records[0]))
    calls = (tuple(ACTUAL_CALLS), tuple(world.CALLS))
    provider = CapturedSemanticProviderV01(records)
    if case in ('valid', 'equivalent'):
        result = adapter.collect_semantics_v01(request, provider)
        assert list(result['contributions']) == original
        provider.assert_exhausted_v01()
        assert provider.position == 4
    else:
        with pytest.raises(ValueError):
            adapter.collect_semantics_v01(request, provider)
        assert provider.position == 0
        if case != 'unused':
            direct = CapturedSemanticProviderV01(records)
            with pytest.raises(ValueError):
                direct.respond_v01(roles.ROLES[0], original[0]['projection'], roles.request_ref_v01(request))
            assert direct.position == 0
    assert calls == (tuple(ACTUAL_CALLS), tuple(world.CALLS))
    positive = CapturedSemanticProviderV01(deepcopy(original))
    assert adapter.collect_semantics_v01(request, positive)['selected_plan'].plan_id == original[2]['output']['selected_plan_id']


def test_captured_unused_complete_group_rejected_before_story_effects_v10(tmp_path):
    from hedgehog.domains.testflix.live_semantic_adapter_v01 import CapturedSemanticProviderV01
    from hedgehog.domains.testflix.demo_story_v01 import run_story_v01
    request, records = _synthetic_live_records_v10()
    provider = CapturedSemanticProviderV01(records + deepcopy(records))
    before = tuple(world.CALLS)
    with pytest.raises(ValueError, match='^captured_unused_records$'):
        run_story_v01(request, provider, directory=tmp_path/'not-created', renewal=False)
    assert provider.position == 0 and tuple(world.CALLS) == before and not (tmp_path/'not-created').exists()


@pytest.mark.parametrize('fail_selector', (False, True))
def test_live_suffix_budget_restart_and_failure_v10(tmp_path, monkeypatch, fail_selector):
    import json
    from types import SimpleNamespace
    from google import genai
    from hedgehog.domains.testflix.live_semantic_adapter_v01 import LiveSemanticProviderV01, ACTUAL_CALLS
    directory = tmp_path/'captures'; directory.mkdir()
    for index in range(1,19):
        (directory/('attempt_%02d.json'%index)).write_text(json.dumps(dict(attempt=index,
            category='main' if index <= 9 else 'AB')))
    config = tmp_path/'config.py'
    config.write_text("GOOGLE_API_KEY='OFFLINE_TEST_NOT_TRANSMITTED'\nGEMINI_MODEL='OFFLINE_DOUBLE'\n")
    request, records = _synthetic_live_records_v10()
    calls = []
    class Client:
        def __init__(self, **kwargs):
            assert kwargs['http_options']['retry_options'] == {'attempts': 1}
            self.models = self
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def generate_content(self, *, contents, **kwargs):
            data = json.loads(contents); calls.append(data['duty'])
            if fail_selector and len(calls) == 1: raise RuntimeError('OFFLINE_TRANSPORT_FAILURE')
            output = records[roles.ROLES.index(data['duty'])]['output']
            return SimpleNamespace(text=json.dumps(output), usage_metadata=None, model_version='OFFLINE_DOUBLE')
    monkeypatch.setattr(genai, 'Client', Client)
    before = tuple(world.CALLS)
    count = len(ACTUAL_CALLS)
    def provider(): return LiveSemanticProviderV01(directory=directory, category='AB', config_path=config)
    try:
        for index in (2,3):
            record = records[index]
            fresh = provider()
            if index == 2 and fail_selector:
                with pytest.raises(RuntimeError, match='OFFLINE_TRANSPORT_FAILURE'):
                    fresh.respond_v01(record['role'], record['projection'], roles.request_ref_v01(request))
            else:
                output, transport = fresh.respond_v01(record['role'], record['projection'], roles.request_ref_v01(request))
                assert transport['attempt'] == index+17 and output == record['output']
        with pytest.raises(ValueError, match='^live_call_budget_exhausted$'):
            provider().respond_v01(records[3]['role'], records[3]['projection'], roles.request_ref_v01(request))
        assert len(calls) == 2 and len(list(directory.glob('attempt_*.json'))) == 20
        assert (directory/'failure_19.json').exists() == fail_selector
        assert (directory/'response_20.json').exists() and not (directory/'attempt_21.json').exists()
        assert tuple(world.CALLS) == before
    finally:
        del ACTUAL_CALLS[count:]


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


@pytest.mark.parametrize('case', ('ceiling_int_to_float', 'catalog_bool_to_int'))
def test_saved_projection_json_types_are_bound_v11(case):
    from hedgehog.domains.testflix.live_semantic_adapter_v01 import CapturedSemanticProviderV01, ACTUAL_CALLS
    request, original = _synthetic_live_records_v10()
    changed = deepcopy(original)
    index = 0 if case == 'ceiling_int_to_float' else 1
    if case == 'ceiling_int_to_float':
        changed[index]['projection']['hard_ceiling_minor'] = float(changed[index]['projection']['hard_ceiling_minor'])
    else:
        changed[index]['projection']['catalog'][0]['ads'] = int(changed[index]['projection']['catalog'][0]['ads'])
    before = (tuple(ACTUAL_CALLS), tuple(world.CALLS))
    provider = CapturedSemanticProviderV01(changed)
    with pytest.raises(ValueError, match='^semantic_projection_binding$'):
        adapter.collect_semantics_v01(request, provider)
    assert provider.position == 0
    direct = CapturedSemanticProviderV01(changed)
    for prior in range(index):
        direct.respond_v01(roles.ROLES[prior], original[prior]['projection'], roles.request_ref_v01(request))
    with pytest.raises(ValueError, match='^captured_input_binding$'):
        direct.respond_v01(roles.ROLES[index], original[index]['projection'], roles.request_ref_v01(request))
    assert direct.position == index
    good = CapturedSemanticProviderV01(deepcopy(original))
    actual = adapter.collect_semantics_v01(request, good)
    assert c.canonical_v01(list(actual['contributions'])) == c.canonical_v01(original)
    good.assert_exhausted_v01()
    assert before == (tuple(ACTUAL_CALLS), tuple(world.CALLS))
