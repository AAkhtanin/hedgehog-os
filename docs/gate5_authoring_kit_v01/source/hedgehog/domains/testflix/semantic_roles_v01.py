"""Four distinct semantic duties; local input binding, never Root authority."""
from dataclasses import asdict
import json
from hedgehog.domains.testflix import contracts_v01 as c

ROLES = ('intent_interpreter', 'provider_terms_analyst', 'client_plan_selector', 'contract_reviewer')
MODES = ('LIVE_CAPTURED', 'CAPTURED_REEXECUTION', 'CONTROLLED_ROLE_DUTIES')


def projection_v01(request, role, records):
    c.validate_request_v01(request)
    index = ROLES.index(role)
    c.require_v01(tuple(r['role'] for r in records) == ROLES[:index], 'semantic_upstream_order')
    base = dict(request_id=request.request_id, preference=request.preference,
        hard_ceiling_minor=request.hard_ceiling_minor, currency=request.currency)
    base['task_contract'] = dict(subject='Testflix subscription selection from a supplied finite catalog',
        price_unit='minor currency units',
        required_inputs=['preference', 'hard_ceiling_minor', 'currency'] +
            (['catalog', 'upstream'] if index else []),
        intent_scope='Interpret the explicit preference enum; content genre and viewing habits are not required inputs.')
    if request.preference == 'QUALITY':
        base['task_contract']['preference_definition'] = dict(
            enum='QUALITY', eligible='price_minor <= hard_ceiling_minor',
            priority_order=['resolution descending', 'ads false before true', 'price_minor ascending', 'plan_id ascending'],
            scope='Use catalog fields only. Advertising is a tie-breaker, not a veto on higher resolution. '
                'Premium content and simultaneous streams are not supplied requirements.')
    if index:
        base['catalog'] = [asdict(p) for p in request.catalog]
        base['upstream'] = [dict(role=r['role'], output=r['output'],
            capture_ref=r['capture']['capture_id']) for r in records]
    return base


def _strings(value):
    return type(value) is list and len(value) <= 16 and all(
        type(v) is str and 0 < len(v) <= 512 for v in value)


def validate_output_v01(output, role, projection, request):
    c.require_v01(type(output) is dict, 'role_output_shape')
    shapes = {
        ROLES[0]: {'preference', 'priorities', 'missing_evidence', 'summary'},
        ROLES[1]: {'terms', 'missing_evidence', 'summary'},
        ROLES[2]: {'selected_plan_id', 'decision_factors', 'missing_evidence'},
        ROLES[3]: {'supports_selection', 'blocking_conflicts', 'missing_evidence', 'reason'},
    }
    c.require_v01(set(output) == shapes[role], 'role_output_shape')
    c.require_v01(_strings(output['missing_evidence']), 'role_missing_evidence_shape')
    c.require_v01(not output['missing_evidence'], 'role_required_evidence_missing')
    if role == ROLES[0]:
        c.require_v01(output['preference'] == request.preference and
            _strings(output['priorities']) and bool(output['priorities']), 'intent_source_binding')
    elif role == ROLES[1]:
        terms = output['terms']
        c.require_v01(type(terms) is list and len(terms) == len(request.catalog), 'terms_inventory')
        for term, plan in zip(terms, request.catalog, strict=True):
            expected = dict(asdict(plan), eligible=plan.price_minor <= request.hard_ceiling_minor)
            c.require_v01(type(term) is dict and set(term) == set(expected) and all(
                type(term[k]) is type(v) and term[k] == v for k, v in expected.items()), 'terms_source_binding')
    elif role == ROLES[2]:
        c.require_v01(_strings(output['decision_factors']) and bool(output['decision_factors']), 'selection_reasons')
        c.plan_by_id_v01(request, output['selected_plan_id'])
    else:
        c.require_v01(type(output['supports_selection']) is bool and _strings(output['blocking_conflicts']),
            'review_output_shape')
        c.require_v01(output['supports_selection'] and not output['blocking_conflicts'], 'semantic_review_disagreement')
        selection = projection['upstream'][2]['output']['selected_plan_id']
        c.plan_by_id_v01(request, selection)
    for key in ('summary', 'reason'):
        if key in output:
            c.require_v01(type(output[key]) is str and 0 < len(output[key]) <= 512, 'role_explanation')
    return True


def request_ref_v01(request):
    # Attached locally, not sent to the model; commits the exact request.
    return c.identity_v01('semantic_request', asdict(request))


def capture_v01(request, role, projection, output, transport):
    return _capture_material_v01(request_ref_v01(request), role, projection, output, transport)


def _capture_material_v01(request_ref, role, projection, output, transport):
    c.require_v01(type(transport) is dict and set(transport) == {
        'origin_mode', 'provider', 'model', 'attempt', 'started_utc', 'elapsed_seconds', 'raw_response'},
        'semantic_transport_shape')
    c.require_v01(transport['origin_mode'] in ('LIVE', 'CONTROLLED') and
        type(transport['raw_response']) is str and len(transport['raw_response'].encode()) <= 32768,
        'semantic_transport_mode')
    c.require_v01(all(type(transport[k]) is str and 0 < len(transport[k]) <= 256
        for k in ('provider', 'model', 'started_utc')) and type(transport['attempt']) is int and
        1 <= transport['attempt'] <= 20 and type(transport['elapsed_seconds']) in (int, float) and
        0 <= transport['elapsed_seconds'] < float('inf'), 'semantic_transport_values')
    c.require_v01(c.canonical_v01(json.loads(transport['raw_response'], object_pairs_hook=unique_pairs_v01)) ==
        c.canonical_v01(output),
        'semantic_raw_binding')
    material = dict(role=role, request_ref=request_ref,
        projection_ref=c.identity_v01('role_projection', projection),
        response_ref=c.identity_v01('role_response', output), transport=transport)
    return dict(material, capture_id=c.identity_v01('semantic_capture', material))


def unique_pairs_v01(pairs):
    result = {}
    for key, value in pairs:
        c.require_v01(key not in result, 'semantic_duplicate_key')
        result[key] = value
    return result


def validate_records_v01(request, records, *, mode):
    c.require_v01(mode in MODES and type(records) in (tuple, list) and
        tuple(r['role'] for r in records) == ROLES, 'role_inventory')
    previous = []
    for role, record in zip(ROLES, records, strict=True):
        c.require_v01(type(record) is dict and set(record) == {'role', 'projection', 'output', 'capture'},
            'semantic_record_shape')
        c.require_v01(type(record['capture']) is dict and set(record['capture']) == {
            'role', 'request_ref', 'projection_ref', 'response_ref', 'transport', 'capture_id'},
            'semantic_capture_shape')
        projection = projection_v01(request, role, previous)
        c.require_v01(c.canonical_v01(record['projection']) == c.canonical_v01(projection), 'semantic_projection_binding')
        validate_output_v01(record['output'], role, projection, request)
        actual = capture_v01(request, role, projection, record['output'], record['capture']['transport'])
        c.require_v01(actual == record['capture'], 'semantic_capture_binding')
        expected_origin = 'CONTROLLED' if mode == 'CONTROLLED_ROLE_DUTIES' else 'LIVE'
        c.require_v01(actual['transport']['origin_mode'] == expected_origin, 'semantic_origin_mode')
        previous.append(record)
    return c.plan_by_id_v01(request, records[2]['output']['selected_plan_id'])


def collect_roles_v01(request, provider, ledger):
    if provider.mode == 'CAPTURED_REEXECUTION':
        provider.validate_remaining_v01(request)
    records = []
    for role in ROLES:
        projection = projection_v01(request, role, records)
        ledger.append((role, c.identity_v01('role_projection', projection)))
        output, transport = provider.respond_v01(role, projection, request_ref_v01(request))
        validate_output_v01(output, role, projection, request)
        capture = capture_v01(request, role, projection, output, transport)
        records.append(dict(role=role, projection=projection, output=output, capture=capture))
    plan = validate_records_v01(request, records, mode=provider.mode)
    return dict(mode=provider.mode, contributions=tuple(records), selected_plan=plan,
        semantic_ref=c.identity_v01('semantic', records), provider_call_ledger=tuple(ledger[-4:]))


class ControlledRolesV01:
    """Separate deterministic duties for offline controls, never a live capture."""
    mode = 'CONTROLLED_ROLE_DUTIES'

    def __init__(self):
        self.calls = 0

    def respond_v01(self, role, projection, request_ref):
        self.calls += 1
        if role == ROLES[0]:
            value = dict(preference=projection['preference'], priorities=[projection['preference']],
                missing_evidence=[], summary='Interpret the supplied preference within the stated ceiling.')
        elif role == ROLES[1]:
            value = dict(terms=[dict(p, eligible=p['price_minor'] <= projection['hard_ceiling_minor'])
                for p in projection['catalog']], missing_evidence=[], summary='Check supplied terms for each plan.')
        elif role == ROLES[2]:
            terms = projection['upstream'][1]['output']['terms']
            intent = projection['upstream'][0]['output']['preference']
            eligible = [p for p in terms if p['eligible']]
            c.require_v01(bool(eligible), 'no_eligible_plan')
            key = (lambda p: (p['ads'], -p['resolution'], p['price_minor'], p['plan_id'])) if intent == 'AD_FREE' else (
                lambda p: (-p['resolution'], p['ads'], p['price_minor'], p['plan_id']))
            value = dict(selected_plan_id=min(eligible, key=key)['plan_id'],
                decision_factors=[intent, 'affordable supplied terms'], missing_evidence=[])
        else:
            selected = projection['upstream'][2]['output']['selected_plan_id']
            terms = projection['upstream'][1]['output']['terms']
            eligible = [p for p in terms if p['eligible']]
            chosen = next((p for p in eligible if p['plan_id'] == selected), None)
            conflicts = []
            if chosen is None:
                conflicts.append('The selection is not eligible.')
            elif projection['preference'] == 'AD_FREE' and chosen['ads'] and any(not p['ads'] for p in eligible):
                conflicts.append('An eligible ad-free plan implements the stated preference.')
            elif projection['preference'] == 'QUALITY' and chosen['resolution'] < max(p['resolution'] for p in eligible):
                conflicts.append('A higher-resolution eligible plan implements the stated preference.')
            value = dict(supports_selection=not conflicts, blocking_conflicts=conflicts,
                missing_evidence=[], reason='Check selection against preference and supplied terms; Root decides independently.')
        transport = dict(origin_mode='CONTROLLED', provider='local', model='none', attempt=self.calls,
            started_utc='CONTROLLED_NO_WALL_CLOCK', elapsed_seconds=0.0,
            raw_response=json.dumps(value, sort_keys=True, separators=(',', ':')))
        return value, transport
