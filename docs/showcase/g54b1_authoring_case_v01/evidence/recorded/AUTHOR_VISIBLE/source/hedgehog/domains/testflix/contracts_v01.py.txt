"""Small immutable domain records and independent business boundary checks."""
from dataclasses import asdict, dataclass
import hashlib
import json


def canonical_v01(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()


def identity_v01(kind, value):
    return 'testflix:' + kind + ':' + hashlib.sha256(kind.encode() + b'\0' + canonical_v01(value)).hexdigest()


def require_v01(condition, reason):
    if not condition:
        raise ValueError(reason)


@dataclass(frozen=True)
class PlanV01:
    plan_id: str
    price_minor: int
    resolution: int
    ads: bool
    period_seconds: int


@dataclass(frozen=True)
class RequestV01:
    request_id: str
    user_id: str
    merchant_id: str
    order_id: str
    device_id: str
    content_id: str
    currency: str
    now: int
    hard_ceiling_minor: int
    preference: str
    catalog: tuple[PlanV01, ...]
    registered_devices: tuple[str, ...]
    bank_private: str
    user_private: str
    purchase_consent: bool
    approved_prices_minor: tuple[int, ...]
    approved_device_id: str
    approved_order_id: str


def request_from_plain_v01(value):
    require_v01(type(value) is dict and set(value) == set(RequestV01.__dataclass_fields__), 'request_shape')
    plans = tuple(PlanV01(**p) for p in value['catalog'])
    result = RequestV01(**dict(value, catalog=plans, registered_devices=tuple(value['registered_devices']),
        approved_prices_minor=tuple(value['approved_prices_minor'])))
    validate_request_v01(result)
    return result


def validate_request_v01(request):
    require_v01(type(request) is RequestV01, 'request_type')
    for name in ('request_id','user_id','merchant_id','order_id','device_id','content_id','bank_private','user_private','approved_device_id','approved_order_id'):
        value = getattr(request, name)
        require_v01(type(value) is str and 0 < len(value) <= 512, 'request_field:' + name)
    require_v01(request.currency == 'EUR' and request.preference in ('AD_FREE','QUALITY'), 'request_policy')
    require_v01(type(request.now) is int and request.now >= 0 and type(request.hard_ceiling_minor) is int and request.hard_ceiling_minor > 0, 'request_numeric')
    require_v01(type(request.catalog) is tuple and 1 <= len(request.catalog) <= 16, 'catalog_bound')
    require_v01(len({p.plan_id for p in request.catalog}) == len(request.catalog), 'catalog_unique')
    for plan in request.catalog:
        require_v01(type(plan) is PlanV01 and type(plan.plan_id) is str and bool(plan.plan_id), 'plan_shape')
        require_v01(type(plan.price_minor) is int and plan.price_minor > 0 and type(plan.resolution) is int and plan.resolution > 0 and type(plan.ads) is bool and plan.period_seconds == 2592000, 'plan_values')
    require_v01(type(request.registered_devices) is tuple and 0 < len(request.registered_devices) <= 2 and len(set(request.registered_devices)) == len(request.registered_devices), 'device_policy')
    require_v01(request.device_id in request.registered_devices, 'device_not_registered')
    require_v01(type(request.purchase_consent) is bool and type(request.approved_prices_minor) is tuple and
        0 < len(request.approved_prices_minor) <= 16 and
        all(type(v) is int and v > 0 for v in request.approved_prices_minor) and
        len(set(request.approved_prices_minor)) == len(request.approved_prices_minor), 'purchase_consent_shape')
    return True


def plan_by_id_v01(request, plan_id):
    matches = tuple(p for p in request.catalog if p.plan_id == plan_id)
    require_v01(len(matches) == 1, 'unknown_plan')
    require_v01(matches[0].price_minor <= request.hard_ceiling_minor, 'over_budget')
    return matches[0]


@dataclass(frozen=True)
class EntitlementCandidateV01:
    user_id: str
    plan: PlanV01
    merchant_id: str
    order_id: str
    payment_receipt_ref: str
    valid_from: int
    valid_to: int
    renewal: str

    @property
    def candidate_id(self):
        return identity_v01('entitlement_candidate', asdict(self))


@dataclass(frozen=True)
class EntitlementV01:
    candidate: EntitlementCandidateV01
    decision_id: str
    issuance_receipt_ref: str

    @property
    def entitlement_id(self):
        return identity_v01('entitlement', asdict(self))


@dataclass(frozen=True)
class SessionCandidateV01:
    entitlement_id: str
    user_id: str
    device_id: str
    content_id: str
    valid_from: int
    valid_to: int
    concurrency_limit: int
    quality: int = 720

    @property
    def candidate_id(self):
        return identity_v01('session_candidate', asdict(self))


@dataclass(frozen=True)
class SessionV01:
    candidate: SessionCandidateV01
    provider_decision_id: str
    issuance_receipt_ref: str

    @property
    def session_id(self):
        return identity_v01('session', asdict(self))


def validate_payment_relationship_v01(request, plan, output):
    expected = dict(amount_minor=plan.price_minor, currency=request.currency,
        merchant_id=request.merchant_id, order_id=request.order_id)
    require_v01(all(output.get(k) == v for k, v in expected.items()), 'provider_payment_binding')
    require_v01(type(output.get('payment_ref')) is str and bool(output['payment_ref']), 'provider_payment_receipt')
    return True


def validate_entitlement_v01(entitlement, request, plan, payment, authorization):
    require_v01(type(entitlement) is EntitlementV01, 'entitlement_type')
    validate_payment_relationship_v01(request, plan, payment)
    expected = EntitlementCandidateV01(request.user_id, plan, request.merchant_id, request.order_id,
        payment['payment_ref'], request.now, request.now + plan.period_seconds, 'EXPLICIT_ONLY')
    require_v01(entitlement.candidate == expected, 'entitlement_candidate_binding')
    canonical = authorization.canonical_projection
    require_v01(canonical.business_object_identity.business_object_ref == expected.candidate_id and
        canonical.owning_local_root_id == 'root:testflix:provider' and
        authorization.root_decision_projection.root_decision_result.decision_id == entitlement.decision_id,
        'provider_entitlement_decision_binding')
    return True


def validate_session_v01(session, entitlement, request, authorization):
    require_v01(type(session) is SessionV01, 'session_type')
    expected = SessionCandidateV01(entitlement.entitlement_id, request.user_id, request.device_id,
        request.content_id, request.now, min(request.now + 7200, entitlement.candidate.valid_to), 1, entitlement.candidate.plan.resolution)
    require_v01(session.candidate == expected, 'session_candidate_binding')
    canonical = authorization.canonical_projection
    require_v01(canonical.owning_local_root_id == 'root:testflix:provider' and
        canonical.business_object_identity.business_object_ref == expected.candidate_id and
        authorization.root_decision_projection.root_decision_result.decision_id == session.provider_decision_id,
        'provider_session_decision_binding')
    return True


@dataclass(frozen=True)
class InformationRequestV01:
    request_id: str
    user_id: str
    entitlement_id: str
    now: int


@dataclass(frozen=True)
class StopPlaybackV01:
    request_id: str
    user_id: str
    session_id: str
    now: int


@dataclass(frozen=True)
class PlaybackRequestV01:
    request_id: str
    user_id: str
    entitlement_id: str
    device_id: str
    content_id: str
    now: int
    ttl_seconds: int
    quality: int


@dataclass(frozen=True)
class DeviceStateV01:
    device_id: str
    user_id: str
    valid_to: int
    max_quality: int
    permitted_content_ids: tuple[str, ...]


@dataclass(frozen=True)
class PlaybackBasisV01:
    session: SessionV01
    entitlement_id: str
    user_id: str
    valid_from: int
    valid_to: int
    max_quality: int
    device: DeviceStateV01


@dataclass(frozen=True)
class ProviderQuoteV01:
    plan: PlanV01
    merchant_id: str
    currency: str
    observed_at: int
    valid_to: int
    predecessor_id: str | None

    @property
    def quote_id(self):
        return identity_v01('provider_quote',asdict(self))


@dataclass(frozen=True)
class RenewalIntentV01:
    request_id: str
    user_id: str
    entitlement_id: str
    quote_id: str
    order_id: str
    now: int
    consent_limit_minor: int
    explicit_consent: bool


@dataclass(frozen=True)
class DeviceGrantRequestV01:
    request_id: str
    user_id: str
    device_id: str
    content_id: str
    now: int
    valid_to: int
    quality: int


def validate_provider_quote_v01(quote):
    require_v01(type(quote) is ProviderQuoteV01 and type(quote.plan) is PlanV01, 'provider_quote_type')
    require_v01(type(quote.observed_at) is int and type(quote.valid_to) is int and quote.observed_at<quote.valid_to and
        type(quote.plan.price_minor) is int and quote.plan.price_minor>0 and quote.plan.period_seconds==2592000 and
        quote.currency=='EUR' and type(quote.merchant_id) is str and bool(quote.merchant_id) and
        (quote.predecessor_id is None or type(quote.predecessor_id) is str), 'provider_quote_bounds')
    return True


def validate_renewal_intent_v01(event, entitlement, quote, now):
    require_v01(type(event) is RenewalIntentV01 and type(entitlement) is EntitlementV01, 'renewal_intent_type')
    validate_provider_quote_v01(quote)
    require_v01(type(event.explicit_consent) is bool and event.explicit_consent and
        type(event.consent_limit_minor) is int and event.consent_limit_minor>0, 'renewal_explicit_consent_required')
    require_v01(event.now==now and quote.observed_at<=now+4<quote.valid_to, 'renewal_quote_not_current')
    require_v01(event.user_id==entitlement.candidate.user_id and event.entitlement_id==entitlement.entitlement_id and
        event.quote_id==quote.quote_id and quote.merchant_id==entitlement.candidate.merchant_id and
        quote.plan.plan_id==entitlement.candidate.plan.plan_id and type(event.order_id) is str and
        event.order_id!=entitlement.candidate.order_id and type(event.request_id) is str and bool(event.request_id), 'renewal_scope')
    require_v01(quote.plan.price_minor<=event.consent_limit_minor, 'renewal_price_exceeds_consent')
    return True


def playback_basis_v01(session, entitlement, devices):
    require_v01(type(session) is SessionV01 and type(entitlement) is EntitlementV01, 'playback_basis_type')
    matches = tuple(d for d in devices if type(d) is DeviceStateV01 and d.device_id==session.candidate.device_id)
    require_v01(len(matches)==1, 'playback_basis_device_missing')
    ec = entitlement.candidate
    return PlaybackBasisV01(session,entitlement.entitlement_id,ec.user_id,ec.valid_from,ec.valid_to,ec.plan.resolution,matches[0])


def validate_playback_basis_v01(basis, evaluation_time):
    require_v01(type(basis) is PlaybackBasisV01 and type(basis.session) is SessionV01 and
        type(basis.device) is DeviceStateV01 and type(evaluation_time) is int, 'playback_basis_type')
    sc = basis.session.candidate; device = basis.device
    require_v01(sc.entitlement_id==basis.entitlement_id and sc.user_id==basis.user_id==device.user_id and
        sc.device_id==device.device_id and sc.content_id in device.permitted_content_ids, 'playback_basis_scope')
    require_v01(basis.valid_from<=sc.valid_from<=evaluation_time<sc.valid_to<=min(basis.valid_to,device.valid_to),
        'playback_basis_expired_or_widened')
    require_v01(0<sc.quality<=min(basis.max_quality,device.max_quality) and sc.concurrency_limit==1, 'playback_basis_quality')
    return True


def validate_event_v01(event):
    require_v01(type(event) in (InformationRequestV01,StopPlaybackV01,PlaybackRequestV01,RenewalIntentV01,DeviceGrantRequestV01),'event_type')
    for name,value in asdict(event).items():
        if name=='explicit_consent':
            require_v01(type(value) is bool,'event_consent_type')
        elif name in ('now','ttl_seconds','quality','valid_to','consent_limit_minor'):
            require_v01(type(value) is int and value>=0,'event_number:'+name)
        else:
            require_v01(type(value) is str and 0<len(value)<=512,'event_reference:'+name)
    if type(event) is PlaybackRequestV01:
        require_v01(event.ttl_seconds>0 and event.quality>0,'playback_request_bounds')
    return True


def validate_playback_request_v01(event, entitlement, devices, active_sessions, now):
    validate_event_v01(event)
    require_v01(type(event) is PlaybackRequestV01 and type(entitlement) is EntitlementV01,'playback_type')
    require_v01(event.now==now and entitlement.candidate.valid_from<=now+4<entitlement.candidate.valid_to,'current_entitlement')
    require_v01(event.entitlement_id==entitlement.entitlement_id and event.user_id==entitlement.candidate.user_id,'playback_entitlement_scope')
    require_v01(type(devices) is tuple and 0<len(devices)<=2 and len({d.device_id for d in devices})==len(devices),'max_devices')
    matches = tuple(d for d in devices if type(d) is DeviceStateV01 and d.device_id==event.device_id and d.user_id==event.user_id)
    require_v01(len(matches)==1,'current_device_scope')
    device = matches[0]
    require_v01(type(device.valid_to) is int and type(device.max_quality) is int and
        type(device.permitted_content_ids) is tuple and event.content_id in device.permitted_content_ids,'current_device_content')
    require_v01(now+4<device.valid_to and now+event.ttl_seconds<=min(entitlement.candidate.valid_to,device.valid_to) and
        event.ttl_seconds<=7200 and event.ttl_seconds>4,'session_ttl_widening')
    require_v01(event.quality<=min(entitlement.candidate.plan.resolution,device.max_quality),'session_quality_widening')
    require_v01(type(active_sessions) is tuple and not active_sessions,'max_concurrent_streams')
    return device
