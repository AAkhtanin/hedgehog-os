"""Closed football semantics. No storage, transport, Root or effects."""
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from itertools import product
from hedgehog.external_drs import gate5_contracts_v01 as c

REQUEST = ('request_id','revision','operation','team_ref','venue_ref','timezone',
           'currency','budget_minor','owner_approval_ref','sessions')
SESSION = ('session_id','start','end','allow_shift_minutes')
SLOT = ('session_id','venue_ref','field_id','start_utc','end_utc','price_minor')
FIELD = ('field_id','surface','full_size','price_minor')
E_FIELDS = ('request','fields','alternatives','slots','total_minor','currency',
            'status','schedule_revision','offer_revision')
SOURCE = ('publisher','recipient','request_revision','schedule_revision','offer_revision',
          'observed_at','valid_from','valid_to','ttl','pt','status','status_checked','status_until')
OPERATIONS = ('FIND_OFFER','CONFIRM_MOCK_BOOKING','VERIFY_EXISTING','CLARIFY')

class Refusal(ValueError):
    """Expected closed domain refusal, separately persisted by the peer."""
    def __init__(self, reason, status='REFUSED'):
        super().__init__(reason)
        self.status = status

def need(value, reason, status='REFUSED'):
    if not value:
        raise Refusal(reason, status)

def unique(rows, key):
    need(len({r[key] for r in rows}) == len(rows), 'duplicate_'+key)

def local_seconds(value, zone):
    need(type(value) is str and len(value) in (16,19), 'local_datetime', 'CLARIFY')
    try:
        dt = datetime.fromisoformat(value)
    except ValueError as exc:
        raise Refusal('local_datetime', 'CLARIFY') from exc
    need(dt.year==2027 and dt.month==1,'unsupported_calendar','CLARIFY')
    need(dt.tzinfo is None and dt.second == 0 and dt.microsecond == 0,
         'local_datetime_precision', 'CLARIFY')
    # Only the finite declared calendar zone is supported; no payload path lookup.
    tz = ZoneInfo('Europe/Tirane')
    a, b = dt.replace(tzinfo=tz, fold=0), dt.replace(tzinfo=tz, fold=1)
    need(a.utcoffset() == b.utcoffset() and
         a.astimezone(timezone.utc).astimezone(tz).replace(tzinfo=None) == dt,
         'ambiguous_or_missing_local_time', 'CLARIFY')
    return int(a.timestamp())

def request_times(r):
    if type(r) is not dict or set(r) != set(REQUEST):
        raise Refusal('required_request_fields', 'CLARIFY')
    c.walk(r)
    for k in ('request_id','team_ref','venue_ref'):
        c.label(r[k])
    need(type(r['revision']) is int and r['revision'] > 0, 'request_revision', 'CLARIFY')
    need(r['operation'] in OPERATIONS, 'operation', 'CLARIFY')
    need(r['timezone'] == 'Europe/Tirane', 'unsupported_timezone', 'CLARIFY')
    need(type(r['currency']) is str and len(r['currency']) == 3 and
         r['currency'].isascii() and r['currency'].isalpha() and r['currency'].isupper(),
         'currency', 'CLARIFY')
    need(type(r['budget_minor']) is int and 0 <= r['budget_minor'] <= c.LIMIT,
         'required_integer_budget', 'CLARIFY')
    if r['owner_approval_ref'] is not None:
        c.ref(r['owner_approval_ref'])
    need(type(r['sessions']) is list and len(r['sessions']) == 3, 'three_sessions', 'CLARIFY')
    result = {}
    for s in r['sessions']:
        c.shape(s, SESSION)
        c.label(s['session_id'])
        start, end = local_seconds(s['start'], r['timezone']), local_seconds(s['end'], r['timezone'])
        need(end-start == 5400, 'unsupported_duration', 'CLARIFY')
        shift = s['allow_shift_minutes']
        need(type(shift) is int and shift in (0,30), 'unsupported_shift', 'CLARIFY')
        if shift:
            need(s['start'][:10] == '2027-01-08' and r['owner_approval_ref'] is not None,
                 'shift_requires_explicit_january8_consent')
        result[s['session_id']] = (start,end,shift*60)
    unique(r['sessions'], 'session_id')
    return result

def inventory_check(i, r):
    c.shape(i, ('revision','venue_ref','currency','fields'))
    need(type(i['revision']) is int and i['revision'] > 0, 'inventory_revision')
    need(i['venue_ref'] == r['venue_ref'] and i['currency'] == r['currency'], 'inventory_scope')
    need(type(i['fields']) is list and 1 <= len(i['fields']) <= 4, 'field_bound')
    for f in i['fields']:
        c.shape(f, FIELD+('available_utc','occupied_utc'))
        c.label(f['field_id']); c.label(f['surface'])
        need(type(f['full_size']) is bool, 'full_size_type')
        need(type(f['price_minor']) is int and 0 <= f['price_minor'] <= c.LIMIT, 'integer_tariff')
        for key in ('available_utc','occupied_utc'):
            need(type(f[key]) is list and len(f[key]) <= 16, 'interval_bound')
            for pair in f[key]:
                need(type(pair) is list and len(pair) == 2, 'interval_shape')
                need(all(type(v) is int and 0 <= v <= c.LIMIT for v in pair) and pair[0] < pair[1],
                     'half_open_interval')
    unique(i['fields'], 'field_id')

def overlap(a,b):
    return a[0] < b[1] and b[0] < a[1]

def available(f, start, end):
    cursor=start
    for lo,hi in sorted(f['available_utc']):
        if lo<=cursor<hi:
            cursor=hi
        if cursor>=end:
            break
    return cursor>=end and not any(overlap((start,end), x) for x in f['occupied_utc'])

def slot_key(s):
    return tuple(s[k] for k in ('session_id','field_id','start_utc','end_utc','venue_ref'))

def combinations(r, i, times):
    options = []
    for sid in sorted(times):
        start,end,shift = times[sid]
        rows = []
        for delta in ((0,shift) if shift else (0,)):
            for f in i['fields']:
                if (f['surface'] == 'natural_grass' and f['full_size'] and
                    f['price_minor'] <= r['budget_minor'] and available(f,start+delta,end+delta)):
                    rows.append(dict(session_id=sid,venue_ref=r['venue_ref'],field_id=f['field_id'],
                                     start_utc=start+delta,end_utc=end+delta,price_minor=f['price_minor']))
        options.append(sorted(rows,key=lambda s:(s['start_utc']-start,s['price_minor'],slot_key(s))))
    return options

def compatible(rows):
    return all(a['field_id'] != b['field_id'] or
               not overlap((a['start_utc'],a['end_utc']),(b['start_utc'],b['end_utc']))
               for j,a in enumerate(rows) for b in rows[j+1:])

def rank(rows,times):
    return (sum(s['start_utc']-times[s['session_id']][0] for s in rows),
            sum(s['price_minor'] for s in rows), tuple(slot_key(s) for s in sorted(rows,key=slot_key)))

def produce(r,i):
    times=request_times(r)
    need(r['operation']=='FIND_OFFER','producer_find_only')
    inventory_check(i,r)
    options=combinations(r,i,times)
    lawful=[rows for rows in product(*options)
            if compatible(rows) and sum(s['price_minor'] for s in rows) <= r['budget_minor']]
    best=list(min(lawful,key=lambda rows:rank(rows,times))) if lawful else []
    used={s['field_id'] for rows in options for s in rows}
    fields=[{k:f[k] for k in FIELD} for f in sorted(i['fields'],key=lambda f:f['field_id']) if f['field_id'] in used]
    alternatives=[dict(session_id=sid,choices=rows[:2]) for sid,rows in zip(sorted(times),options)]
    return dict(request=r,fields=fields,alternatives=alternatives,slots=best,
                total_minor=c.integer(sum(s['price_minor'] for s in best)),currency=r['currency'],
                status='OFFER_READY' if best else 'NO_COMPLETE_OFFER',
                schedule_revision=i['revision'],offer_revision=i['revision'])

def validate_slot(s, r, times, fields):
    c.shape(s,SLOT)
    need(s['session_id'] in times and s['field_id'] in fields and s['venue_ref']==r['venue_ref'],
         'slot_scope')
    f=fields[s['field_id']]
    need(f['surface']=='natural_grass' and f['full_size'] is True,'hard_field_constraint')
    start,end,allowed=times[s['session_id']]
    need(type(s['start_utc']) is int and type(s['end_utc']) is int,'slot_integer_time')
    need((s['start_utc'],s['end_utc']) in ((start,end),(start+allowed,end+allowed)),
         'forbidden_shift_or_duration')
    need(type(s['price_minor']) is int and s['price_minor']==f['price_minor'] and
         0 <= s['price_minor'] <= r['budget_minor'],'slot_tariff')

def validate_e(e):
    c.shape(e,E_FIELDS)
    r=e['request']; times=request_times(r)
    need(r['operation']=='FIND_OFFER','original_find_request')
    need(type(e['fields']) is list and len(e['fields'])<=4,'exposed_field_bound')
    for f in e['fields']:
        c.shape(f,FIELD); c.label(f['field_id'])
        need(f['surface']=='natural_grass' and f['full_size'] is True,'exposed_hard_constraints')
        need(type(f['price_minor']) is int and 0<=f['price_minor']<=c.LIMIT,'field_price')
    unique(e['fields'],'field_id'); fields={f['field_id']:f for f in e['fields']}
    need(type(e['alternatives']) is list and len(e['alternatives'])==3,'alternative_sessions')
    unique(e['alternatives'],'session_id')
    need({a['session_id'] for a in e['alternatives']}==set(times),'alternative_session_binding')
    for a in e['alternatives']:
        c.shape(a,('session_id','choices'))
        need(type(a['choices']) is list and len(a['choices'])<=2,'alternative_bound')
        need(len({c.sha(s) for s in a['choices']})==len(a['choices']),'duplicate_alternative')
        for s in a['choices']:
            validate_slot(s,r,times,fields)
            need(s['session_id']==a['session_id'],'alternative_binding')
    need(type(e['slots']) is list,'slots_type')
    for s in e['slots']:
        validate_slot(s,r,times,fields)
    unique(e['slots'],'session_id')
    need(e['status'] in ('OFFER_READY','NO_COMPLETE_OFFER','NEEDS_CONFIRMATION'),'offer_status')
    if e['status']=='OFFER_READY':
        need(len(e['slots'])==3 and {s['session_id'] for s in e['slots']}==set(times) and
             compatible(e['slots']),'complete_offer')
    else:
        need(not e['slots'],'no_offer_empty')
    need(type(e['total_minor']) is int and e['total_minor']==sum(s['price_minor'] for s in e['slots'])
         and 0<=e['total_minor']<=r['budget_minor'] and e['currency']==r['currency'],'offer_total')
    for k in ('schedule_revision','offer_revision'):
        need(type(e[k]) is int and 0<e[k]<=c.LIMIT,'offer_revision')

def verify_producer(r,i,e):
    """Checks original inputs and all feasible combinations, never an output success flag."""
    validate_e(e); times=request_times(r); inventory_check(i,r)
    need(e['request']==r and e['schedule_revision']==i['revision'] and e['offer_revision']==i['revision'],
         'producer_original_input_binding')
    fs={f['field_id']:f for f in i['fields']}
    for f in e['fields']:
        need(f=={k:fs[f['field_id']][k] for k in FIELD},'producer_field_projection')
    for s in e['slots']+[s for a in e['alternatives'] for s in a['choices']]:
        need(available(fs[s['field_id']],s['start_utc'],s['end_utc']),'producer_availability')
    options=combinations(r,i,times)
    winner=None
    for a in options[0]:
        for b in options[1]:
            for d in options[2]:
                rows=[a,b,d]
                if compatible(rows) and sum(s['price_minor'] for s in rows)<=r['budget_minor']:
                    if winner is None or rank(rows,times)<rank(winner,times):
                        winner=rows
    need(e['slots']==(winner or []),'producer_optimal_complete_selection')
    need(e['status']==('OFFER_READY' if winner else 'NO_COMPLETE_OFFER'),'producer_no_result_truth')
    need(e['alternatives']==[dict(session_id=sid,choices=rows[:2])
                             for sid,rows in zip(sorted(times),options)],'producer_alternatives')

def planning_equal(a,b):
    return all(a[k]==b[k] for k in REQUEST if k not in ('operation','owner_approval_ref'))

def logical_object(r):
    return 'booking:'+c.sha({k:r[k] for k in ('request_id','team_ref','venue_ref')})

def report(r,status,slots=None,source=None,receipt=None,search=0,dispatch=0,mutations=0,observed=0):
    rows=[] if slots is None else slots
    return dict(version='g53.result.v01',request_ref=r.get('request_id'),
                request_revision=r.get('revision'),team_ref=r.get('team_ref'),operation=r.get('operation'),
                status=status,slots=rows,total_minor=sum(s['price_minor'] for s in rows),
                currency=r.get('currency'),source=source,receipt_ref=receipt,
                counts=dict(search=search,dispatch=dispatch,mutations=mutations,observed=observed))

def consume(r,context):
    from candidate_domain.profile import profile
    c.shape(context,('body','source_projection'))
    b=context['body']; s=context['source_projection']
    c.validate('body',b,profile=profile()); c.shape(s,SOURCE); request_times(r)
    need(planning_equal(r,b['offer']['request']),'consumer_original_request_binding')
    t=b['time_envelope']
    expected=dict(publisher=b['publisher'],recipient=b['recipient'],request_revision=b['offer']['request']['revision'],
                  schedule_revision=b['offer']['schedule_revision'],offer_revision=b['source_revision'],
                  observed_at=t['source_observed_at'],valid_from=t['valid_from'],valid_to=t['valid_to'],
                  ttl=t['ttl_seconds'],pt=t['pt_created_at'])
    need(all(s[k]==v for k,v in expected.items()),'consumer_context_projection')
    need(s['status']=='ACTIVE' and type(s['status_checked']) is int and
         type(s['status_until']) is int and 0<s['status_until']-s['status_checked']<=60,'consumer_status')
    e=b['offer']; booking=b['booking']
    if r['operation']=='FIND_OFFER':
        need(r==e['request'] and booking is None,'find_binding')
        status=e['status']; receipt=None
    else:
        need(r['operation']=='CONFIRM_MOCK_BOOKING' and booking is not None and
             booking['request_sha256']==c.sha(r) and e['status']=='OFFER_READY','confirmation_binding')
        status='MOCK_BOOKED'; receipt=booking['receipt_ref']
    return report(r,status,e['slots'],s,receipt,search=1,observed=1)
