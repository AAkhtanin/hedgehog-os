"""Closed immutable G5-1 reference carriers and pure independent checks."""
from dataclasses import dataclass
import hashlib
import json
import math
import re
from hedgehog import drs_semantic_address_v01 as drs
from hedgehog.kernel import root_signer_isolation_v01 as crypto

LIMIT = (1 << 62) - 1
WIRE_MAX, BODY_MAX, POINTER_MAX, DEPTH_MAX = 262144, 65536, 16384, 12
BODY_SCHEMA = 'BoundedCalibrationSummaryV01'
ROOT_A, ROOT_B = 'root:gate5:calibration', 'root:gate5:site'
UNIT, QUANTITY = 'synthetic_unit_v01', 'reference_quantity_v01'


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def integer(value):
    require(type(value) is int and -LIMIT <= value <= LIMIT, 'integer_range_or_type')
    return value


def add(a, b):
    return integer(integer(a) + integer(b))


def mul(a, b):
    return integer(integer(a) * integer(b))


def rational(num, den):
    integer(num); integer(den); require(den > 0, 'rational_denominator')
    gcd = math.gcd(num, den)
    return {'num': num // gcd, 'den': den // gcd}


def ratio(value):
    shape(value, ('num', 'den'))
    require(value == rational(value['num'], value['den']), 'rational_not_reduced')
    return value


def total(values):
    require(type(values) is list and 1 <= len(values) <= 8, 'observation_count')
    result = 0
    for value in values:
        result = add(result, value)
    return result


def calibration(reference, observations):
    n, s = len(observations), total(observations)
    return dict(n=n, total=s, correction=rational(add(mul(n, reference), -s), n))


def corrected(readings, offset):
    ratio(offset)
    s, n = total(readings), len(readings)
    return dict(mean=rational(s, n), corrected=rational(add(mul(s, offset['den']), mul(n, offset['num'])), mul(n, offset['den'])))


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode()


def sha(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def walk(value, depth=0):
    require(depth <= DEPTH_MAX, 'json_depth')
    if type(value) is dict:
        require(len(value) <= 64, 'object_field_count')
        for key, item in value.items():
            require(type(key) is str and len(key) <= 128 and key.isascii(), 'json_key')
            walk(item, depth + 1)
    elif type(value) is list:
        require(len(value) <= 32, 'list_count')
        for item in value: walk(item, depth + 1)
    elif type(value) is str:
        require(len(value) <= 4096 and value.isascii(), 'json_string')
    elif type(value) is int: integer(value)
    else: require(value is None or type(value) is bool, 'json_scalar')


def decode(data, limit=WIRE_MAX):
    require(type(data) is bytes and len(data) <= limit, 'message_size')
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate_json_key')
            result[key] = value
        return result
    try:
        value = json.loads(data.decode('ascii'), object_pairs_hook=pairs,
            parse_float=lambda x: (_ for _ in ()).throw(ValueError('float_forbidden')),
            parse_constant=lambda x: (_ for _ in ()).throw(ValueError('nonfinite_forbidden')))
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ValueError('json_encoding') from exc
    walk(value)
    require(canonical(value) == data, 'noncanonical_json')
    return value


def shape(value, names):
    require(type(value) is dict and set(value) == set(names), 'closed_fields')


def ref(value):
    require(type(value) is str and 0 < len(value) <= 256 and re.fullmatch(r'[A-Za-z0-9_.:-]+', value), 'reference')


def label(value):
    ref(value); require(len(value) <= 128, 'label_size')


def hash_value(value):
    require(type(value) is str and re.fullmatch(r'[0-9a-f]{64}', value), 'sha256')


def sequence(values, maximum=16):
    require(type(values) is list and len(values) <= maximum and len(set(values)) == len(values), 'reference_sequence')
    for value in values: ref(value)


def identifier(prefix, value, field):
    return prefix + ':' + sha({k:v for k,v in value.items() if k != field})


def with_id(kind, value):
    field, prefix = IDS[kind]
    return dict(value, **{field: identifier(prefix, value, field)})


IDS = {'pointer':('pointer_id','g5pointer'), 'manifest':('manifest_id','g5manifest'),
    'request':('request_id','g5request'), 'import':('import_id','g5import'),
    'disposition':('disposition_id','g5disposition'), 'adaptation':('local_view_id','g5adaptation')}
FIELDS = {
 'body': ('version','source_record_ref','source_revision','unit_id','quantity_id','reference','observations','n','total','correction','source_work_ref','source_review_ref','time_envelope','ttl_base','source_lineage_refs'),
 'manifest': ('version','manifest_id','publisher','source_revision','source_refs','declared_schema','files'),
 'pointer': ('version','pointer_id','publisher_root_id','publisher_key_id','semantic_address','source_record_ref','source_revision','source_review_ref','body_sha256','body_bytes','media_type','artifact_manifest_ref','safe_summary','published_scope','allowed_use_classes','forbidden_use_classes','recipient_scope','time_envelope','source_lineage_refs','access_policy_ref','revocation_stream_id','transport_object_id','creates_authority','creates_permission'),
 'request': ('version','request_id','op','requester','publisher','task_ref','request_revision','pointer_ref','trust_profile_hash','use_class','object_id','allowed_size','nonce','deadline','issued_at','subject_request_ref','owner_transport_scope'),
 'entry': ('version','pointer_id','publisher_root_id','stream_id','revision','state','effective_at','reason_ref','entry_hash'),
 'status': ('version','entry','requested_pointer_hash','requester','subject_request_ref','request_revision','nonce','checked_at','valid_until'),
 'release': ('version','state','request_ref','request_revision','pointer_ref','manifest_ref','body_hash','recipient','use_class','nonce','deadline','release_review_ref'),
 'import': ('version','import_id','local_request_ref','pointer_ref','foreign_publisher','foreign_source_ref','foreign_revision','received_manifest_hash','body_hash','receive_event_ref','validation_results','status_entry_hash','dependency_fingerprint','policy_hash','creates_permission'),
 'disposition': ('version','disposition_id','candidate_ref','parent_ref','state','local_review_ref'),
 'adaptation': ('version','local_view_id','import_ref','foreign_source_ref','source_field','value','input_names','work_request_ref','local_acceptance_ref')}


def time_shape(value):
    # The public builder reconstructs exact native axes and content identity.
    import inspect
    args = {k:v for k,v in value.items() if k in inspect.signature(drs.build_drs_time_envelope_v01).parameters}
    rebuilt = drs.build_drs_time_envelope_v01(**args)
    require(drs.drs_time_envelope_to_plain_data_v01(rebuilt) == value, 'native_time_identity')
    for k in args:
        if k != 'freshness_policy_id': require(integer(args[k]) >= 0, 'negative_time')
    require(value['valid_from'] < value['valid_to'] and value['ttl_seconds'] > 0, 'time_bounds')
    add(value['pt_created_at'], value['ttl_seconds'])


def validate(kind, value, *, profile=None):
    if profile is not None:
        from .gate5_body_profile_v01 import check_local_profile_v01
        check_local_profile_v01(profile)
    schema=BODY_SCHEMA if profile is None else profile.schema_id
    require(kind in FIELDS, 'unknown_contract')
    shape(value, profile.body_fields if profile is not None and kind=='body' else FIELDS[kind]); walk(value)
    require(value['version'] == 'g51.' + kind + '.v01', 'schema_version')
    if kind in IDS:
        field, prefix = IDS[kind]
        require(value[field] == identifier(prefix, value, field), 'content_identity')
    if kind == 'body':
        if profile is not None:
            for key in ('source_record_ref','source_work_ref','source_review_ref'):ref(value[key])
            require(integer(value['source_revision'])>0,'revision');sequence(value['source_lineage_refs'])
            time_shape(value['time_envelope']);require(value['ttl_base']=='pt_created_at','ttl_base')
            require(len(canonical(value))<=BODY_MAX,'body_size')
            profile.validate_body(value)
            return
        for key in ('source_record_ref','unit_id','quantity_id','source_work_ref','source_review_ref'): ref(value[key])
        require(integer(value['source_revision']) > 0, 'revision')
        integer(value['reference']); total(value['observations']); integer(value['n']); integer(value['total']); ratio(value['correction'])
        sequence(value['source_lineage_refs']); time_shape(value['time_envelope'])
        require(value['ttl_base'] == 'pt_created_at', 'ttl_base')
        require(len(canonical(value)) <= BODY_MAX, 'body_size')
    elif kind == 'manifest':
        ref(value['publisher']); require(integer(value['source_revision']) > 0, 'revision'); sequence(value['source_refs'])
        require(value['declared_schema'] == schema, 'unknown_body_schema')
        require(type(value['files']) is list and len(value['files']) == 1, 'manifest_files')
        file = value['files'][0]; shape(file, ('path','bytes','sha256'))
        require(file['path'] == 'body.json' and 0 < integer(file['bytes']) <= BODY_MAX, 'manifest_file')
        hash_value(file['sha256'])
    elif kind == 'pointer':
        require(len(canonical(value)) <= POINTER_MAX, 'pointer_size')
        for key in ('publisher_root_id','publisher_key_id','source_record_ref','source_review_ref','artifact_manifest_ref','access_policy_ref','revocation_stream_id','transport_object_id'): ref(value[key])
        require(integer(value['source_revision']) > 0 and 0 < integer(value['body_bytes']) <= BODY_MAX, 'pointer_bounds')
        hash_value(value['body_sha256']); require(value['media_type'] == 'application/json', 'media_type')
        shape(value['semantic_address'], ('namespace','domain','subject_class','intent_class','schema_id','schema_version'))
        for v in value['semantic_address'].values(): label(v)
        require(value['semantic_address']['schema_id'] == schema, 'unknown_body_schema')
        require(value['semantic_address']['schema_version']=='v01', 'unknown_body_schema_version')
        shape(value['published_scope'], ('domain','unit_id','quantity_id') if profile is None else profile.scope_fields)
        for v in value['published_scope'].values(): label(v)
        if profile is None:
            require(value['safe_summary'] == canonical(dict(kind='calibration',unit_id=value['published_scope']['unit_id'],quantity_id=value['published_scope']['quantity_id'])).decode(), 'unsafe_summary')
        else:profile.validate_pointer(value)
        require(len(value['safe_summary']) <= 1024, 'summary_size')
        for key in ('allowed_use_classes','forbidden_use_classes','recipient_scope','source_lineage_refs'): sequence(value[key])
        require(not set(value['allowed_use_classes']) & set(value['forbidden_use_classes']), 'scope_conflict')
        require(value['creates_authority'] is False and value['creates_permission'] is False, 'authority_claim')
        time_shape(value['time_envelope'])
    elif kind == 'request':
        require(value['op'] in ('DESCRIBE','STATUS','FETCH','CLOSE'), 'operation')
        for key in ('requester','publisher','task_ref','use_class','object_id','owner_transport_scope'): ref(value[key])
        hash_value(value['trust_profile_hash']); hash_value(value['nonce'])
        require(integer(value['request_revision']) > 0 and 0 < integer(value['allowed_size']) <= BODY_MAX, 'request_bounds')
        require(0 <= integer(value['issued_at']) < integer(value['deadline']) <= add(value['issued_at'],60), 'request_deadline')
        for key in ('pointer_ref','subject_request_ref'):
            if value[key] is not None: ref(value[key])
        require((value['pointer_ref'] is None) == (value['op'] in ('DESCRIBE','CLOSE')), 'request_pointer')
        require((value['subject_request_ref'] is not None) == (value['op']=='STATUS'), 'status_subject')
    elif kind == 'entry':
        for key in ('pointer_id','publisher_root_id','stream_id','reason_ref'): ref(value[key])
        require(integer(value['revision']) > 0 and integer(value['effective_at']) >= 0, 'status_revision')
        require(value['state'] in ('ACTIVE','REVOKED','SUPERSEDED'), 'status_state')
        require(value['entry_hash'] == sha({k:v for k,v in value.items() if k!='entry_hash'}), 'status_entry_hash')
    elif kind == 'status':
        validate('entry',value['entry']); hash_value(value['requested_pointer_hash']); hash_value(value['nonce'])
        ref(value['requester']); ref(value['subject_request_ref']); require(integer(value['request_revision']) > 0,'revision')
        require(0 <= integer(value['checked_at']) < integer(value['valid_until']) <= add(value['checked_at'],60), 'status_validity')
    elif kind == 'release':
        require(value['state'] in ('RELEASED','REFUSED'), 'release_state')
        for key in ('request_ref','pointer_ref','manifest_ref','recipient','use_class','release_review_ref'): ref(value[key])
        hash_value(value['body_hash']); hash_value(value['nonce']); require(integer(value['request_revision']) > 0 and integer(value['deadline']) > 0, 'release_bounds')
    elif kind == 'import':
        for key in ('local_request_ref','pointer_ref','foreign_publisher','foreign_source_ref','receive_event_ref'): ref(value[key])
        for key in ('received_manifest_hash','body_hash','status_entry_hash','dependency_fingerprint','policy_hash'): hash_value(value[key])
        require(integer(value['foreign_revision']) > 0 and value['creates_permission'] is False, 'import_authority')
        shape(value['validation_results'], ('shape','signature','integrity','arithmetic','provenance','temporal','scope','status','conflict','local_policy'))
        require(all(v is True for v in value['validation_results'].values()), 'import_not_validated')
    elif kind == 'disposition':
        ref(value['candidate_ref'])
        require(value['state'] in ('CANDIDATE','QUARANTINED','REFUSED','ACCEPTED_CONTEXT'), 'disposition_state')
        for key in ('parent_ref','local_review_ref'):
            if value[key] is not None: ref(value[key])
        require((value['local_review_ref'] is not None) == (value['state']=='ACCEPTED_CONTEXT'), 'disposition_review')
    else:
        for key in ('import_ref','foreign_source_ref','source_field','work_request_ref','local_acceptance_ref'): ref(value[key])
        require(value['source_field'] == 'correction' and value['input_names'] == ['offset_den','offset_num'], 'adaptation_field')
        ratio(value['value'])


@dataclass(frozen=True)
class BoundedContractV01:
    """Immutable canonical bytes, closed tagged kinds; projections return fresh containers."""
    kind: str
    wire: bytes

    def __post_init__(self):
        validate(self.kind, decode(self.wire))

    def plain(self):
        return decode(self.wire)


def contract(kind, value):
    return BoundedContractV01(kind, canonical(value))


def keyset(value):
    result = crypto.TrustedRootKeySetV01(**{k:tuple(v) if type(v) is list else v for k,v in value.items()})
    require(crypto.trusted_root_key_set_to_plain_dict_v01(result) == value, 'keyset_identity')
    return result


def sign(cap, keys, purpose, value, manifest_hash):
    commitment = crypto.build_root_owned_commitment_v01(commitment_id='g5commit:'+sha(dict(purpose=purpose,value=value)),
        transaction_id='transaction:gate5:reference', owner_root_id=cap.root_id, commitment_scope='gate5:'+purpose+':v01',
        artifact_hash=sha(value), manifest_hash=manifest_hash, key_id=cap.key_id)
    signature = crypto.sign_root_owned_commitment_v01(capability=cap,trusted_key_set=keys,commitment=commitment)
    return dict(value=value,commitment=crypto.root_owned_commitment_to_plain_dict_v01(commitment),signature=crypto.root_signature_to_plain_dict_v01(signature))


def verify(envelope, pinned_keys, purpose, manifest_hash):
    shape(envelope, ('value','commitment','signature'))
    commitment = crypto.RootOwnedCommitmentV01(**envelope['commitment'])
    signature = crypto.RootSignatureV01(**envelope['signature'])
    report = crypto.verify_root_signature_v01(trusted_key_set=keyset(pinned_keys),commitment=commitment,signature=signature)
    require(report.verification_status == 'PASS', 'signature_invalid')
    require(commitment.commitment_scope == 'gate5:'+purpose+':v01' and commitment.transaction_id=='transaction:gate5:reference', 'signature_purpose')
    require(commitment.artifact_hash == sha(envelope['value']) and commitment.manifest_hash == manifest_hash, 'signed_content_binding')
    return envelope['value']


def temporal(value, now, policy):
    time_shape(value); integer(now)
    end = min(value['valid_to'],add(value['pt_created_at'],value['ttl_seconds']),add(value['source_observed_at'],policy['max_source_age']))
    require(value['valid_from'] <= now < end and value['source_observed_at'] <= now, 'source_not_current')
    require(value['valid_to']-value['valid_from'] <= policy['max_validity_horizon'], 'validity_horizon')
    return end


def authenticate_status(envelope, pointer, request, policy, now, history):
    """Authenticate observations, including terminal entries, before current-use checks."""
    value = verify(envelope, policy['peer_keys'], 'STATUS', pointer['artifact_manifest_ref'].split(':')[1])
    validate('status',value); entry=value['entry']
    require((value['requested_pointer_hash'],value['requester'],value['subject_request_ref'],value['request_revision'],value['nonce']) ==
        (sha(pointer),request['requester'],request['request_id'],request['request_revision'],request['nonce']), 'status_request_binding')
    require((entry['pointer_id'],entry['publisher_root_id'],entry['stream_id']) ==
        (pointer['pointer_id'],pointer['publisher_root_id'],pointer['revocation_stream_id']), 'status_pointer_binding')
    require(value['checked_at'] <= now < min(value['valid_until'],add(value['checked_at'],60)), 'status_not_current')
    require(entry['effective_at']<=now, 'status_not_effective')
    key=canonical([entry['publisher_root_id'],entry['pointer_id'],entry['stream_id']]).decode()
    old=history.get(key)
    if old:
        require(entry['revision']>=old['revision'], 'status_rollback')
        require(entry['revision']!=old['revision'] or entry['entry_hash']==old['entry_hash'], 'status_equivocation')
        require(old['state']=='ACTIVE' or entry['state']==old['state'], 'status_terminal_revival')
    return key,entry


def check_status(envelope, pointer, request, policy, now, history):
    key,entry=authenticate_status(envelope,pointer,request,policy,now,history)
    require(entry['state']=='ACTIVE','status_not_active')
    return key,entry


def check_route(pointer, policy, *, visited=(), depth=0, endpoint=None):
    """The bridge follows exactly one pinned object, never a payload-selected route."""
    require(type(depth) is int and depth==0 and type(visited) is tuple,'route_hop_limit')
    require(pointer['pointer_id'] not in visited and not visited,'route_cycle')
    require(endpoint in (None,policy['endpoint']) and policy['endpoint']=='endpoint:gate5:A','route_endpoint')
    require(pointer['transport_object_id']==policy['object_id'],'route_object')
    return pointer['transport_object_id']


def check_pointer(envelope, policy, now, *, profile=None):
    pointer=envelope['value']; validate('pointer',pointer,profile=profile)
    verify(envelope,policy['peer_keys'],'POINTER',pointer['artifact_manifest_ref'].split(':')[1])
    require(pointer['publisher_root_id']==policy['peer_root'] and pointer['publisher_key_id']==policy['peer_keys']['key_ids'][0], 'publisher_identity')
    require(pointer['source_record_ref']==policy['source_record_ref'] and pointer['access_policy_ref']==policy['source_policy_ref'], 'source_policy_identity')
    require(pointer['transport_object_id']==policy['object_id'], 'pinned_object_identity')
    require(pointer['semantic_address']['domain']==policy['domain'] and pointer['semantic_address']['schema_id'] in policy['schemas'], 'schema_scope')
    scope_keys=('domain','unit_id','quantity_id') if profile is None else profile.scope_fields
    require(pointer['published_scope']=={k:policy[k] for k in scope_keys}, 'source_scope')
    temporal(pointer['time_envelope'],now,policy)
    return pointer


def check_bundle(bundle, pointer_envelope, request, status, policy, now, history, conflicts, *, profile=None):
    shape(bundle, ('release','manifest','body'))
    pointer=check_pointer(pointer_envelope,policy,now,profile=profile)
    validate('request',request); require(request['issued_at']<=now<request['deadline'], 'request_expired')
    require(request['trust_profile_hash']==sha(policy) and request['requester']==policy['local_root'], 'local_request_policy')
    require((request['op'],request['publisher'],request['pointer_ref'],request['object_id'],request['owner_transport_scope']) ==
        ('FETCH',policy['peer_root'],pointer['pointer_id'],policy['object_id'],policy['transport_scope']), 'request_target_binding')
    require(pointer['body_bytes'] <= request['allowed_size'], 'requested_size_limit')
    release=verify(bundle['release'],policy['peer_keys'],'RELEASE',pointer['artifact_manifest_ref'].split(':')[1]); validate('release',release)
    require(release['state']=='RELEASED', 'release_refused')
    require((release['request_ref'],release['request_revision'],release['pointer_ref'],release['manifest_ref'],release['body_hash'],release['recipient'],release['use_class'],release['nonce'],release['deadline']) ==
        (request['request_id'],request['request_revision'],pointer['pointer_id'],pointer['artifact_manifest_ref'],pointer['body_sha256'],request['requester'],request['use_class'],request['nonce'],request['deadline']), 'release_request_binding')
    require(request['use_class'] in policy['uses'] and request['use_class'] in pointer['allowed_use_classes'] and request['use_class'] not in pointer['forbidden_use_classes'] and request['requester'] in pointer['recipient_scope'], 'local_scope')
    require(policy['accept_calibration' if profile is None else profile.policy_accept_field] is True, 'local_policy_refusal')
    body,manifest=bundle['body'],bundle['manifest']; validate('manifest',manifest,profile=profile);validate('body',body,profile=profile)
    require(manifest['manifest_id']==pointer['artifact_manifest_ref'] and manifest['publisher']==pointer['publisher_root_id'], 'manifest_identity')
    file=manifest['files'][0]
    require(file['sha256']==sha(body)==pointer['body_sha256'] and file['bytes']==len(canonical(body))==pointer['body_bytes'], 'body_integrity')
    require((body['source_record_ref'],body['source_revision'],body['source_review_ref'],body['time_envelope'],body['source_lineage_refs']) ==
        (pointer['source_record_ref'],pointer['source_revision'],pointer['source_review_ref'],pointer['time_envelope'],pointer['source_lineage_refs']), 'source_provenance')
    require(manifest['source_refs']==[body['source_record_ref'],body['source_work_ref'],body['source_review_ref']] and manifest['source_revision']==body['source_revision'], 'manifest_provenance')
    if profile is None:
        require(body['unit_id']==policy['unit_id'] and body['quantity_id']==policy['quantity_id'], 'body_units')
        expected=calibration(body['reference'],body['observations'])
        require(all(body[k]==expected[k] for k in expected), 'calibration_arithmetic')
    else:profile.validate_binding(body,policy,pointer)
    temporal(body['time_envelope'],now,policy)
    status_key,entry=check_status(status,pointer,request,policy,now,history)
    key=canonical([pointer['publisher_root_id'],body['source_record_ref'],body['source_revision']]).decode()
    require(key not in conflicts or conflicts[key]==sha(body), 'source_equivocation')
    return dict(body=body,status_key=status_key,status_entry=entry,conflict_key=key,source_end=temporal(body['time_envelope'],now,policy))
