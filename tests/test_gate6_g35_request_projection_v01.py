"""Pure checks of the actual G35 producer's public request projection."""
from copy import deepcopy
from dataclasses import asdict
import json
from pathlib import Path

from jsonschema import Draft202012Validator
import pytest

from hedgehog.domains.testflix import contracts_v01 as contracts
from hedgehog.domains.testflix import outcome_feedback_adapter_v01 as adapter


ROOT = Path(__file__).resolve().parents[1]
ARRAY_FIELDS = ('catalog', 'registered_devices', 'approved_prices_minor')


@pytest.fixture
def domain_request():
    return contracts.request_from_plain_v01(
        json.loads((ROOT / 'demo/testflix_fixtures_v01.json').read_bytes()))


def request_validator():
    schema = json.loads((ROOT / 'schemas/outcome_feedback_g35_sources_v01.schema.json').read_bytes())
    branch = next(row for row in schema['$defs']['source']['allOf']
                  if row['if']['properties']['domain']['const'] == 'TESTFLIX')
    body_ref = branch['then']['properties']['body']['$ref']
    body = schema['$defs'][body_ref.rsplit('/', 1)[1]]
    return Draft202012Validator(dict(schema, **body['properties']['request']))


def test_public_request_values_privacy_and_canonical_parity(domain_request):
    request = domain_request
    before = asdict(request)
    original_arrays = {name: getattr(request, name) for name in ARRAY_FIELDS}
    public = adapter._public_request_v01(request)
    old = asdict(request)
    for name in ('bank_private', 'user_private'):
        old.pop(name)
    assert set(public) == set(before) - {'bank_private', 'user_private'}
    assert all(type(public[name]) is list for name in ARRAY_FIELDS)
    assert all(type(row) is dict for row in public['catalog'])
    assert public == json.loads(contracts.canonical_v01(old))
    assert contracts.canonical_v01(public) == contracts.canonical_v01(old)
    assert not list(request_validator().iter_errors(public))
    assert asdict(request) == before
    for name, value in original_arrays.items():
        assert type(value) is tuple and getattr(request, name) is value
    encoded = contracts.canonical_v01(public)
    for name in ('bank_private', 'user_private'):
        assert name.encode() not in encoded
        assert getattr(request, name).encode() not in encoded


@pytest.mark.parametrize('field', ARRAY_FIELDS)
def test_each_tuple_is_rejected_by_existing_request_schema(domain_request, field, record_property):
    request = domain_request
    public = adapter._public_request_v01(request)
    mutated = deepcopy(public)
    mutated[field] = tuple(mutated[field])
    errors = list(request_validator().iter_errors(mutated))
    exact = [e for e in errors if list(e.absolute_path) == [field]
             and e.validator == 'type' and e.validator_value == 'array']
    assert exact, [(list(e.absolute_path), e.message) for e in errors]
    record_property('actual_schema_failure', json.dumps([
        dict(path=list(e.absolute_path), schema_path=list(e.absolute_schema_path),
             reason=e.message) for e in exact], sort_keys=True))
    assert type(public[field]) is list
    assert not list(request_validator().iter_errors(public))


def test_projection_does_not_share_mutable_containers(domain_request):
    request = domain_request
    first = adapter._public_request_v01(request)
    second = adapter._public_request_v01(request)
    before = asdict(request)
    first['catalog'][0]['price_minor'] += 1
    first['registered_devices'].append('device:isolated-projection')
    first['approved_prices_minor'].append(777)
    assert asdict(request) == before
    assert second == adapter._public_request_v01(request)
    assert first != second
