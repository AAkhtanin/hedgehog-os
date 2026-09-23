"""Explicitly controlled proposals, privacy projections and bounded parsing."""
from dataclasses import asdict
import json
from hedgehog.domains.testflix import contracts_v01 as c

PROVIDER_CALLS = []


def role_projection_v01(request, role):
    c.validate_request_v01(request)
    if role in ('orchestrator', 'architect', 'selector', 'reviewer', 'user'):
        return dict(request_id=request.request_id, preference=request.preference,
            hard_ceiling_minor=request.hard_ceiling_minor, catalog=[asdict(p) for p in request.catalog])
    if role == 'bank':
        return dict(order_id=request.order_id, merchant_id=request.merchant_id, currency=request.currency,
            hard_ceiling_minor=request.hard_ceiling_minor)
    if role == 'provider':
        return dict(user_id=request.user_id, order_id=request.order_id, merchant_id=request.merchant_id,
            device_id=request.device_id, content_id=request.content_id)
    if role == 'device':
        return dict(user_id=request.user_id, device_id=request.device_id, content_id=request.content_id,
            registered_devices=list(request.registered_devices))
    raise ValueError('unknown_role')


def controlled_provider_v01(role, projection):
    """No expected answer, act identifier, mutable oracle or external transport."""
    eligible = [p for p in projection['catalog'] if p['price_minor'] <= projection['hard_ceiling_minor']]
    c.require_v01(bool(eligible), 'no_eligible_plan')
    if projection['preference'] == 'AD_FREE':
        key = lambda p: (p['ads'], -p['resolution'], p['price_minor'], p['plan_id'])
    else:
        key = lambda p: (-p['resolution'], p['ads'], p['price_minor'], p['plan_id'])
    selected = min(eligible, key=key)
    return dict(role=role, selected_plan_id=selected['plan_id'], reason='Bounded catalog ranking under supplied preference',
        source_ref=c.identity_v01('role_projection', projection))


def validate_contribution_v01(value, role, projection, request):
    c.require_v01(type(value) is dict and set(value) == {'role','selected_plan_id','reason','source_ref'}, 'semantic_output_shape')
    c.require_v01(value['role'] == role and value['source_ref'] == c.identity_v01('role_projection', projection), 'semantic_source_binding')
    c.require_v01(type(value['reason']) is str and 0 < len(value['reason']) <= 512, 'semantic_reason')
    return c.plan_by_id_v01(request, value['selected_plan_id'])


def collect_semantics_v01(request, provider=controlled_provider_v01):
    from hedgehog.domains.testflix import semantic_roles_v01 as roles
    from hedgehog.domains.testflix.live_semantic_adapter_v01 import LiveSemanticProviderV01, CapturedSemanticProviderV01
    if type(provider) in (roles.ControlledRolesV01, LiveSemanticProviderV01, CapturedSemanticProviderV01):
        return roles.collect_roles_v01(request, provider, PROVIDER_CALLS)
    start = len(PROVIDER_CALLS)
    records = []
    for role in ('orchestrator','architect','selector','reviewer'):
        projection = role_projection_v01(request, role)
        PROVIDER_CALLS.append((role,c.identity_v01('role_projection',projection)))
        output = provider(role, projection)
        plan = validate_contribution_v01(output, role, projection, request)
        records.append(dict(role=role, projection=projection, output=output))
    c.require_v01(len({r['output']['selected_plan_id'] for r in records}) == 1, 'semantic_review_disagreement')
    return dict(mode='CONTROLLED_DETERMINISTIC', contributions=tuple(records), selected_plan=plan,
        semantic_ref=c.identity_v01('semantic', records),provider_call_ledger=tuple(PROVIDER_CALLS[start:]))


def validate_semantics_v01(request, semantics):
    c.require_v01(type(semantics) is dict and set(semantics)=={'mode','contributions','selected_plan','semantic_ref','provider_call_ledger'},'semantics_shape')
    plan = c.plan_by_id_v01(request,semantics['selected_plan'].plan_id)
    c.require_v01(plan == semantics['selected_plan'],'selected_plan_source')
    records = semantics['contributions']
    if semantics['mode'] == 'CONTROLLED_DETERMINISTIC':
        c.require_v01(tuple(r['role'] for r in records)==('orchestrator','architect','selector','reviewer'),'semantic_roles')
        for record in records:
            projection = role_projection_v01(request,record['role'])
            c.require_v01(record['projection']==projection,'role_projection_binding')
            c.require_v01(validate_contribution_v01(record['output'],record['role'],projection,request)==plan,'semantic_plan_binding')
    else:
        from hedgehog.domains.testflix import semantic_roles_v01 as roles
        c.require_v01(roles.validate_records_v01(request, records, mode=semantics['mode']) == plan, 'semantic_plan_binding')
    c.require_v01(semantics['provider_call_ledger']==tuple(
        (r['role'],c.identity_v01('role_projection',r['projection'])) for r in records),'provider_call_binding')
    c.require_v01(semantics['semantic_ref']==c.identity_v01('semantic',records),'semantic_identity')
    return plan


def semantics_from_plain_v01(value):
    return dict(value, selected_plan=c.PlanV01(**value['selected_plan']),
        contributions=tuple(value['contributions']), provider_call_ledger=tuple(tuple(v) for v in value['provider_call_ledger']))
