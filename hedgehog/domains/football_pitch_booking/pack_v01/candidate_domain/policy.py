"""Operator policy and untrusted semantic-capture validation."""
from hedgehog.external_drs import gate5_contracts_v01 as c
from candidate_domain.domain import need, request_times, REQUEST
from candidate_domain.storage import read, save

POLICY=('local_root','peer_root','publish_enabled','release_enabled','accept_football','recipients',
        'status','ttl_seconds','max_source_age','shift_approvals','book_approvals')

def validate_policy(p):
    c.shape(p,POLICY)
    c.ref(p['local_root']); c.ref(p['peer_root'])
    need(p['local_root']!=p['peer_root'],'independent_roots')
    for k in ('publish_enabled','release_enabled','accept_football'):
        need(type(p[k]) is bool,'policy_boolean')
    c.sequence(p['recipients'],4)
    need(p['status'] in ('ACTIVE','REVOKED','SUPERSEDED','UNAVAILABLE'),'operator_status')
    for k in ('ttl_seconds','max_source_age'):
        need(type(p[k]) is int and 1<=p[k]<=300,'bounded_source_lifetime')
    for k in ('shift_approvals','book_approvals'):
        need(type(p[k]) is list and len(p[k])<=8,'approval_bound')
        for a in p[k]:
            c.shape(a,('approval_ref','request_sha256','previous_request_sha256') if k=='shift_approvals'
                    else ('approval_ref','request_sha256','offer_request_sha256'))
            c.ref(a['approval_ref'])
            for f in a:
                if f!='approval_ref': c.hash_value(a[f])

def validate_event(event,role,root):
    keys={'event_id','request'}|({'inventory'} if role=='publisher' else set())
    need(set(event) in (keys,keys|{'semantic_proposal','semantic_capture'}),'event_closed_shape')
    r=event['request']; request_times(r)
    if 'semantic_proposal' in event:
        proposed=event['semantic_proposal']; capture=event['semantic_capture']
        c.shape(proposed,('operation','parameters'))
        c.shape(capture,('version','origin','root_id','request','response','request_sha256','response_sha256'))
        need(capture['version']=='football.semantic_capture.v01' and capture['origin'] in
             ('CONTROLLED_EVENT','AUTHORIZED_RUNTIME_CAPTURE'),'semantic_capture_version')
        need(capture['root_id']==root and capture['request']==r and capture['response']==proposed and
             capture['request_sha256']==c.sha(r) and capture['response_sha256']==c.sha(proposed),
             'semantic_capture_binding')
        need(proposed['operation']==r['operation'] and
             proposed['parameters']=={k:r[k] for k in REQUEST if k!='operation'},'semantic_proposal_changes_event')
        # Actually consume the checked proposed mode/parameters. Consent is checked separately.
        r=dict(proposed['parameters'],operation=proposed['operation'])
    return r

def approve_shift(r,p,state):
    if not any(s['allow_shift_minutes'] for s in r['sessions']):
        return
    rows=[a for a in p['shift_approvals'] if a['approval_ref']==r['owner_approval_ref']
          and a['request_sha256']==c.sha(r)]
    need(len(rows)==1,'shift_owner_approval_missing')
    old=read(state/'requests'/(rows[0]['previous_request_sha256']+'.json'))
    need(old is not None and c.sha(old)==rows[0]['previous_request_sha256'],'shift_original_history_missing')
    need(r['revision']>old['revision'],'shift_requires_new_revision')
    need(all(r[k]==old[k] for k in REQUEST if k not in ('revision','owner_approval_ref','sessions')),
         'shift_changed_hard_request')
    before={s['session_id']:s for s in old['sessions']}
    need(set(before)=={s['session_id'] for s in r['sessions']},'shift_changed_sessions')
    changed=0
    for s in r['sessions']:
        o=before[s['session_id']]
        need(all(s[k]==o[k] for k in ('session_id','start','end')),'shift_changed_original_time')
        if s['allow_shift_minutes']!=o['allow_shift_minutes']:
            need(o['allow_shift_minutes']==0 and s['allow_shift_minutes']==30 and
                 s['start'][:10]=='2027-01-08','shift_outside_permission')
            changed+=1
    need(changed==1,'exactly_one_shift_approval')

def approve_booking(r,body,p):
    need(r['owner_approval_ref'] is not None,'booking_owner_consent_missing')
    need(any(a['approval_ref']==r['owner_approval_ref'] and a['request_sha256']==c.sha(r) and
             a['offer_request_sha256']==c.sha(body['offer']['request']) for a in p['book_approvals']),'booking_owner_consent_missing')

def remembered_request(root,r):
    save(root/'requests'/(c.sha(r)+'.json'),r)

def consumer_policy(p,public,r,original):
    booking=r['operation']=='CONFIRM_MOCK_BOOKING'
    # Mint a domain-separated content reference in the public DRS SHA256 form.
    # This is created from the original local request, never by rewriting a received reference.
    record=c.sha(dict(domain='football.source_record.v01',original=c.sha(original),booking=booking))
    return dict(local_root=p['local_root'],peer_root=p['peer_root'],peer_keys=public,
        source_record_ref=record,source_policy_ref='policy:football:source',
        object_id='object:football:'+c.sha({k:r[k] for k in ('request_id','revision','team_ref','venue_ref')}),
        domain='FOOTBALL',schemas=['FootballVenueOfferV01'],uses=['LOCAL_CONTEXT'],
        accept_football=p['accept_football'],max_source_age=p['max_source_age'],max_validity_horizon=300,
        transport_scope='owner:football:inherited-pipes',original_request_sha256=c.sha(original),
        team_ref=r['team_ref'],venue_ref=r['venue_ref'],currency=r['currency'],
        request_revision=r['revision'],budget_minor=r['budget_minor'])
