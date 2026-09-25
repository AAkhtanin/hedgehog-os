"""Finite G5-1 focused controls; never collects the exchange on import."""
import copy
import json
import os
import struct
import sys
import time
from pathlib import Path
from hedgehog.external_drs import gate5_contracts_v01 as c, gate5_native_v01 as n, gate5_exchange_v01 as e


def hostile_fixture(body, pointer, request, status, policy, cap, keys, bad=False):
    """Declared hostile source claims, not an honest native computation or live authority."""
    body=copy.deepcopy(body)
    body.update(source_record_ref='source:gate5:hostile-test',source_work_ref='work:hostile:asserted',source_review_ref='review:hostile:asserted',source_lineage_refs=['work:hostile:asserted'])
    if bad:body['correction']=dict(num=-9,den=1)
    manifest=c.with_id('manifest',dict(version='g51.manifest.v01',publisher=cap.root_id,source_revision=body['source_revision'],
        source_refs=[body['source_record_ref'],body['source_work_ref'],body['source_review_ref']],declared_schema=c.BODY_SCHEMA,
        files=[dict(path='body.json',bytes=len(c.canonical(body)),sha256=c.sha(body))]))
    pointer=c.with_id('pointer',dict(pointer,publisher_root_id=cap.root_id,publisher_key_id=cap.key_id,source_record_ref=body['source_record_ref'],
        source_review_ref=body['source_review_ref'],source_lineage_refs=body['source_lineage_refs'],artifact_manifest_ref=manifest['manifest_id'],body_sha256=c.sha(body),body_bytes=len(c.canonical(body))))
    policy=dict(policy,peer_root=cap.root_id,peer_keys=c.crypto.trusted_root_key_set_to_plain_dict_v01(keys),source_record_ref=body['source_record_ref'])
    request=c.with_id('request',dict(request,publisher=cap.root_id,pointer_ref=pointer['pointer_id'],trust_profile_hash=c.sha(policy)))
    value=copy.deepcopy(status['value']);entry=dict(value['entry'],pointer_id=pointer['pointer_id'],publisher_root_id=cap.root_id)
    entry['entry_hash']=c.sha({k:v for k,v in entry.items() if k!='entry_hash'})
    value.update(entry=entry,requested_pointer_hash=c.sha(pointer),subject_request_ref=request['request_id'])
    manifest_hash=manifest['manifest_id'].split(':')[1]
    status=c.sign(cap,keys,'STATUS',value,manifest_hash)
    release=dict(version='g51.release.v01',state='RELEASED',request_ref=request['request_id'],request_revision=request['request_revision'],
        pointer_ref=pointer['pointer_id'],manifest_ref=manifest['manifest_id'],body_hash=c.sha(body),recipient=request['requester'],use_class=request['use_class'],
        nonce=request['nonce'],deadline=request['deadline'],release_review_ref='review:hostile:release-claim')
    bundle=dict(body=body,manifest=manifest,release=c.sign(cap,keys,'RELEASE',release,manifest_hash))
    return bundle,c.sign(cap,keys,'POINTER',pointer,manifest_hash),request,status,policy


def run_controls(capture,folder):
    capture,folder=Path(capture),Path(folder);folder.mkdir(parents=True,exist_ok=False)
    started=time.monotonic();rows=[]
    read=lambda name:json.loads((capture/name).read_text())
    bundle=read('B/response_LOCAL_CONTEXT.json');descriptor=read('B/descriptor.json');request=read('B/request_LOCAL_CONTEXT.json')
    status=read('B/status_LOCAL_CONTEXT.json');policy=read('operator_trust.json')['B'];now=read('B/result.json')['accepted']['use_time']
    pointer=descriptor['value'];body=bundle['body']
    def denied(name,fn,reason):
        try:fn()
        except (ValueError,TypeError) as exc:
            c.require(reason in str(exc),'unexpected_control_reason:'+name+':'+str(exc));rows.append(dict(name=name,outcome='REFUSED',reason=str(exc)))
        else:raise AssertionError('control_accepted:'+name)
    c.check_bundle(bundle,descriptor,request,status,policy,now,{},{});rows.append(dict(name='recorded_positive_components',outcome='PASS'))
    c.require(read('A/source_work.json')['outputs']==dict(correction_den=1,correction_num=-10,n=3,total=330),'source_oracle')
    c.require(read('B/corrected_work.json')['outputs']==dict(corrected_den=1,corrected_num=96,mean_den=1,mean_num=106),'result_oracle')
    rows.append(dict(name='independent_calibration_oracle',outcome='PASS'))
    # Exact public digest pair from exchange_04's text-summary refusal.
    metadata=dict(publisher=c.ROOT_A,source_record=pointer['source_record_ref'],revision=1,
        pointer_id='g5pointer:1919a1c745c2b873570d02ae5d4fec6860734385592fff6ecb5c70c7d95c904a',
        body_sha256='8c1502938369a0d5641608ebc925abc69c2f520770ed938d538b2013baba66c4',
        schema=c.BODY_SCHEMA,endpoint_ref=policy['endpoint'])
    descent=n.pointer_descent_v01(metadata,folder/'metadata_summary_control',int(time.time())+60)
    c.require(descent['pointer']==metadata,'summary_exact_source_binding')
    rows.append(dict(name='opaque_digest_separate_from_semantic_summary',outcome='PASS_NATIVE_LOCAL_DESCENT'))
    malformed=copy.deepcopy(bundle);malformed['body']['reference']+=1
    denied('altered_body_bytes',lambda:c.check_bundle(malformed,descriptor,request,status,policy,now,{},{}),'body_integrity')
    malformed=copy.deepcopy(descriptor);sig=malformed['signature']['signature_hex'];malformed['signature']['signature_hex']=('0' if sig[0]!='0' else '1')+sig[1:]
    denied('altered_signature',lambda:c.check_pointer(malformed,policy,now),'signature_invalid')
    denied('wrong_purpose',lambda:c.verify(descriptor,policy['peer_keys'],'RELEASE',pointer['artifact_manifest_ref'].split(':')[1]),'signature_purpose')
    for field,value in [('publisher','root:other'),('pointer_ref','pointer:other'),('object_id','object:other'),('owner_transport_scope','scope:other')]:
        other=c.with_id('request',dict(request,**{field:value}))
        denied('request_target_'+field,lambda other=other:c.check_bundle(bundle,descriptor,other,status,policy,now,{},{}),'request_target_binding')
    smaller=c.with_id('request',dict(request,allowed_size=1))
    denied('request_size_limit',lambda:c.check_bundle(bundle,descriptor,smaller,status,policy,now,{},{}),'requested_size_limit')
    cap=c.crypto.generate_root_signer_capability_v01(root_id='root:gate5:declared-hostile-test')
    keys=c.crypto.build_trusted_root_key_set_v01(capabilities=(cap,))
    fixture=hostile_fixture(body,pointer,request,status,policy,cap,keys)
    c.check_bundle(*fixture,now,{},{});rows.append(dict(name='hostile_key_coherent_arithmetic_neighbor',outcome='PASS_PURE_COMPONENTS_NOT_LOCAL_AUTHORITY'))
    bad=hostile_fixture(body,pointer,request,status,policy,cap,keys,bad=True)
    # The authentic signature/closed shape are independently proved before the expected arithmetic refusal.
    c.validate('body',bad[0]['body']);c.verify(bad[1],bad[4]['peer_keys'],'POINTER',bad[1]['value']['artifact_manifest_ref'].split(':')[1])
    denied('genuinely_signed_bad_arithmetic',lambda:c.check_bundle(*bad,now,{},{}),'calibration_arithmetic')
    n.save(folder/'declared_hostile_signed_fixture.json',dict(role='DECLARED_HOSTILE_TEST_SIGNER_NO_NATIVE_SOURCE_ACCEPTANCE',
        public_keys=c.crypto.trusted_root_key_set_to_plain_dict_v01(keys),valid_neighbor=fixture,incorrect_arithmetic=bad))
    for field,value in [('request_ref','request:other'),('recipient','root:other'),('use_class','AUDIT'),('nonce','0'*64)]:
        changed=copy.deepcopy(fixture[0]);release=dict(changed['release']['value'],**{field:value})
        changed['release']=c.sign(cap,keys,'RELEASE',release,fixture[1]['value']['artifact_manifest_ref'].split(':')[1])
        denied('signed_other_'+field,lambda changed=changed:c.check_bundle(changed,*fixture[1:],now,{},{}),'release_request_binding')
    different=copy.deepcopy(fixture[3]);different['value']['nonce']='1'*64
    different=c.sign(cap,keys,'STATUS',different['value'],fixture[1]['value']['artifact_manifest_ref'].split(':')[1])
    denied('signed_status_wrong_nonce',lambda:c.check_bundle(fixture[0],fixture[1],fixture[2],different,fixture[4],now,{},{}),'status_request_binding')
    t=body['time_envelope'];end=min(t['valid_to'],t['pt_created_at']+t['ttl_seconds'],t['source_observed_at']+policy['max_source_age'])
    c.temporal(t,end-1,policy);denied('exact_source_expiry',lambda:c.temporal(t,end,policy),'source_not_current')
    for field in ('valid_to','ttl_seconds'):
        changed=dict(t,**{field:t['pt_created_at']+10 if field=='valid_to' else 10})
        rebuilt=n.rebuilt(c.drs.build_drs_time_envelope_v01,changed);changed=c.drs.drs_time_envelope_to_plain_data_v01(rebuilt)
        c.temporal(changed,t['pt_created_at']+9,policy)
        denied('exact_'+field,lambda changed=changed:c.temporal(changed,t['pt_created_at']+10,policy),'source_not_current')
    age_policy=dict(policy,max_source_age=10);c.temporal(t,t['source_observed_at']+9,age_policy)
    denied('exact_source_age',lambda:c.temporal(t,t['source_observed_at']+10,age_policy),'source_not_current')
    ingested=dict(t,system_ingested_at=t['system_ingested_at']+1,system_verified_at=t['system_verified_at']+1)
    ingested=c.drs.drs_time_envelope_to_plain_data_v01(n.rebuilt(c.drs.build_drs_time_envelope_v01,ingested))
    denied('ingestion_cannot_renew',lambda:c.temporal(ingested,end,policy),'source_not_current')
    fresh_until=status['value']['valid_until']
    c.check_status(status,pointer,request,policy,fresh_until-1,{})
    denied('exact_status_expiry',lambda:c.check_status(status,pointer,request,policy,fresh_until,{}),'status_not_current')
    denied('duplicate_json_keys',lambda:c.decode(b'{"a":1,"a":2}'),'duplicate_json_key')
    denied('noncanonical_json',lambda:c.decode(b'{"a": 1}'),'noncanonical_json')
    denied('float',lambda:c.decode(b'{"a":1.1}'),'float_forbidden')
    denied('nonfinite',lambda:c.decode(b'{"a":NaN}'),'nonfinite_forbidden')
    denied('unknown_body_field',lambda:c.contract('body',dict(body,permission=True)),'closed_fields')
    denied('bool_as_int',lambda:c.contract('body',dict(body,n=True)),'integer_range_or_type')
    denied('bad_identifier',lambda:c.contract('body',dict(body,source_record_ref='../outside')),'reference')
    denied('unknown_schema',lambda:c.contract('body',dict(body,version='other')),'schema_version')
    denied('missing_source_field',lambda:c.contract('body',{k:v for k,v in body.items() if k!='observations'}),'closed_fields')
    denied('oversized_body',lambda:c.decode(b'x'*(c.BODY_MAX+1),c.BODY_MAX),'message_size')
    value=0
    for _ in range(14):value=[value]
    denied('depth_bound',lambda:c.decode(c.canonical(value)),'json_depth')
    denied('arithmetic_overflow',lambda:c.calibration(c.LIMIT,[c.LIMIT,c.LIMIT,c.LIMIT]),'integer_range_or_type')
    fraction=c.calibration(100,[100,101,101]);c.require(fraction['correction']==dict(num=-2,den=3),'fraction_oracle')
    rows.append(dict(name='reduced_fraction_minus_two_thirds',outcome='PASS',value=fraction))
    obj=c.contract('body',body);projection=obj.plain();projection['observations'][0]=0
    c.require(obj.plain()==body,'immutable_projection');rows.append(dict(name='immutable_contract_projection',outcome='PASS'))
    read_fd,write_fd=os.pipe();os.write(write_fd,struct.pack('!I',c.WIRE_MAX+1));os.close(write_fd)
    channel=e.PipeChannel(read_fd,-1,folder)
    try:denied('oversized_frame_before_body_read',channel.receive,'frame_size_before_payload_read')
    finally:os.close(read_fd)
    # A reopened budget cannot reset the two attempted body fetches.
    budget_path=folder/'exhausted_budget.json';budget_path.write_bytes(c.canonical(read('B/budget.json')))
    budget=e.Budget(budget_path,'task:gate5:exchange');next_request=c.with_id('request',dict(request,nonce='e'*64))
    denied('budget_helper_reentry',lambda:budget.reserve(next_request),'attempt_budget')
    counter=n.native_work('corrected',c.ROOT_B,'task:gate5:counterfactual-input-control',
        dict(readings='[103,106,109]',offset_den=body['correction']['den'],offset_num=body['correction']['num']+1))
    c.require(counter['outputs']['corrected_num']==97 and counter['outputs']['corrected_den']==1,'actual_changed_input_oracle')
    n.save(folder/'actual_consumed_input_contrast.json',dict(classification='ISOLATED_TYPED_WORK_CONTRAST_NOT_ACCEPTED_FOREIGN_IMPORT',work=counter))
    rows.append(dict(name='actual_consumed_input_contrast',outcome='PASS',result=counter['outputs']))
    denied('missing_native_input_no_fallback',lambda:n.native_work('corrected',c.ROOT_B,'task:missing',dict(readings='[103,106,109]',offset_den=1)),'native_required_inputs')
    c.check_bundle(bundle,descriptor,request,status,policy,now,{},{});rows.append(dict(name='unchanged_positive_after_mutations',outcome='PASS'))
    n.save(folder/'result.json',dict(status='PASS_FOCUSED_G51',seconds=time.monotonic()-started,controls=rows,
        evidence_mode='FRESH_PURE_VALIDATION_AT_RECORDED_USE_TIME_PLUS_ONE_NEW_CONTROLLED_NATIVE_WORK',next_stage_tests_not_run=True))
    print(json.dumps(dict(status='PASS',controls=len(rows),seconds=time.monotonic()-started)))


if __name__=='__main__':run_controls(sys.argv[1],sys.argv[2])
