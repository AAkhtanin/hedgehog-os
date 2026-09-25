"""Locally selected closed profile. No wire-selected callbacks or import-time admission."""
from hedgehog.external_drs import gate5_contracts_v01 as c
from hedgehog.external_drs.gate5_body_profile_v01 import ReviewedBodyProfileV01, COMMON_BODY_FIELDS
from candidate_domain.domain import validate_e, need

SCHEMA='FootballVenueOfferV01'
SUMMARY='Bounded synthetic football venue offer metadata.'

def validate_body(body):
    e=body['offer']; validate_e(e)
    c.ref(body['publisher']); c.ref(body['recipient']); c.hash_value(body['request_sha256'])
    need(body['request_sha256']==c.sha(e['request']) and body['source_revision']==e['offer_revision'],
         'body_semantic_binding')
    b=body['booking']
    if b is not None:
        c.shape(b,('state','receipt_ref','payload_sha256','snapshot_sha256','packet_ref','slots','request_sha256'))
        need(b['state']=='COMMITTED' and e['status']=='OFFER_READY' and b['slots']==e['slots'],'booking_projection')
        for k in ('receipt_ref','packet_ref'): c.ref(b[k])
        for k in ('payload_sha256','snapshot_sha256','request_sha256'): c.hash_value(b[k])

def validate_pointer(pointer):
    need(pointer['safe_summary']==SUMMARY,'metadata_only_summary')

def validate_binding(body,policy,pointer):
    need(pointer['published_scope']=={'domain':'FOOTBALL'} and policy['domain']=='FOOTBALL','football_scope')
    need(body['publisher']==policy['peer_root'] and body['recipient']==policy['local_root'],'football_audience')
    need(body['request_sha256']==policy['original_request_sha256'],'football_original_request')
    e=body['offer']
    need(e['request']['team_ref']==policy['team_ref'] and e['request']['venue_ref']==policy['venue_ref']
         and e['currency']==policy['currency'] and e['request']['revision']==policy['request_revision'],
         'football_request_policy')
    need(e['total_minor']<=policy['budget_minor'],'football_budget')

def profile():
    return ReviewedBodyProfileV01(SCHEMA,COMMON_BODY_FIELDS+
        ('publisher','recipient','request_sha256','offer','booking'),('domain',),
        'accept_football',validate_body,validate_pointer,validate_binding)

def context_from_checked(checked,status):
    b=checked['body']; t=b['time_envelope']; v=status['value']; entry=checked['status_entry']
    return dict(body=b,source_projection=dict(publisher=b['publisher'],recipient=b['recipient'],
        request_revision=b['offer']['request']['revision'],schedule_revision=b['offer']['schedule_revision'],
        offer_revision=b['source_revision'],observed_at=t['source_observed_at'],valid_from=t['valid_from'],
        valid_to=t['valid_to'],ttl=t['ttl_seconds'],pt=t['pt_created_at'],status=entry['state'],
        status_checked=v['checked_at'],status_until=v['valid_until']))
