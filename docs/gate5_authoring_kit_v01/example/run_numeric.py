"""Actual public native Work, a signed profile check and a current Root refusal.

No peer transport is claimed here; G52 transport evidence is separately recorded.
"""
import argparse,json,sys,time
from pathlib import Path
from hedgehog.external_drs import gate5_contracts_v01 as c,gate5_native_v01 as n,gate5_exchange_v01 as e
from hedgehog.kernel import work_composition_v01 as work,effect_firewall_v01 as firewall,abi_v01 as abi
from hedgehog import action_commit_packet_v02 as action
from demo import run_action_packet_portability_v01 as donor,work_composition_mock_capabilities_v01 as mocks
from numeric_profile import PROFILE

def execute(invocation):
    sample=invocation.inputs[0].value
    return (action.build_action_effect_parameter_record_v01(parameter_name='computed',value_type='INTEGER',value=c.add(c.mul(3,sample),2)),)

def validate_output(definition,invocation,output):
    errors=firewall.validate_capability_values_v01(definition.output_fields,output)
    if not errors and output[0].value!=3*invocation.inputs[0].value+2:errors=('numeric_result_mismatch',)
    return firewall.build_capability_validation_evidence_v01(definition=definition,values=output,invocation_id=invocation.invocation_id,valid=not errors,reason_codes=errors)

def calculate(sample):
    c.integer(sample)
    admitted=mocks.admit_pure_operation_v01(operation_id='example.integer_transform',input_fields=(('sample','INTEGER'),),
        output_fields=(('computed','INTEGER'),),executor=execute,output_validator=validate_output,host_instance_ref='host:example:integer')
    item=work.WorkItemV01('transform',admitted.definition.definition_id,'root:example:integer',(donor.work_literal_v01('sample','INTEGER',sample),),(),(),None,None)
    program,common,host=donor.prepare_work_program_v01(task_id='task:example:'+str(sample),root_id='root:example:integer',admitted=(admitted,),items=(item,),device_refs=())
    results=work.advance_work_program_v01(program,**common,host_map={host.owning_root_id:host})
    valid,reasons=work.validate_work_program_result_v01(program,results,**common,host_map={host.owning_root_id:host})
    c.require(valid and not reasons and results[0].status=='COMPLETED','numeric_work_result')
    artifact=work.work_program_result_to_artifact_v01(program,results,**common,host_map={host.owning_root_id:host})
    value=results[0].result.output[0].value
    review=n.root_review(host.owning_root_id,'transaction:example','candidate:example:'+str(sample),artifact.artifact_id,
        dict(native_valid=valid,independent_equation=value==3*sample+2),dict(input=sample,output=value,work_ref=artifact.artifact_id),int(time.time()))
    return dict(input=sample,output=value,artifact=abi.kernel_artifact_to_plain_dict_v01(artifact),root=n.root_plain(review),
        native_results=n.plain(results),attempts=len(host.work_attempts))

def signed_profile(result):
    now=int(time.time());cap=c.crypto.generate_root_signer_capability_v01(root_id='root:example:integer')
    keys=c.crypto.build_trusted_root_key_set_v01(capabilities=(cap,));public=c.crypto.trusted_root_key_set_to_plain_dict_v01(keys)
    body=dict(version='g51.body.v01',source_record_ref='source:example:integer',source_revision=1,source_work_ref=result['artifact']['artifact_id'],
        source_review_ref=result['root']['result']['decision_id'],time_envelope=e.source_time(now),ttl_base='pt_created_at',
        source_lineage_refs=[result['artifact']['artifact_id']],sample=result['input'],computed=result['output'])
    c.validate('body',body,profile=PROFILE)
    manifest=c.with_id('manifest',dict(version='g51.manifest.v01',publisher=cap.root_id,source_revision=1,
        source_refs=[body['source_record_ref'],body['source_work_ref'],body['source_review_ref']],declared_schema=PROFILE.schema_id,
        files=[dict(path='body.json',bytes=len(c.canonical(body)),sha256=c.sha(body))]));c.validate('manifest',manifest,profile=PROFILE)
    pointer=c.with_id('pointer',dict(version='g51.pointer.v01',publisher_root_id=cap.root_id,publisher_key_id=cap.key_id,
        semantic_address=dict(namespace='example',domain='INTEGER_TRANSFORM',subject_class='numeric_evidence',intent_class='context_lookup',schema_id=PROFILE.schema_id,schema_version='v01'),
        source_record_ref=body['source_record_ref'],source_revision=1,source_review_ref=body['source_review_ref'],body_sha256=c.sha(body),body_bytes=len(c.canonical(body)),
        media_type='application/json',artifact_manifest_ref=manifest['manifest_id'],safe_summary='Bounded integer transform evidence.',published_scope=dict(domain='INTEGER_TRANSFORM'),
        allowed_use_classes=['LOCAL_CONTEXT'],forbidden_use_classes=['ACTION'],recipient_scope=['root:example:consumer'],time_envelope=body['time_envelope'],
        source_lineage_refs=body['source_lineage_refs'],access_policy_ref='policy:example:source',revocation_stream_id='stream:example:one',transport_object_id='object:example:one',
        creates_authority=False,creates_permission=False))
    policy=dict(local_root='root:example:consumer',peer_root=cap.root_id,peer_keys=public,source_record_ref=body['source_record_ref'],source_policy_ref='policy:example:source',
        object_id='object:example:one',domain='INTEGER_TRANSFORM',schemas=[PROFILE.schema_id],uses=['LOCAL_CONTEXT'],accept_transform=True,
        max_source_age=300,max_validity_horizon=300,transport_scope='owner:example:local-component')
    descriptor=c.sign(cap,keys,'POINTER',pointer,manifest['manifest_id'].split(':')[1])
    request=c.with_id('request',dict(version='g51.request.v01',op='FETCH',requester=policy['local_root'],publisher=cap.root_id,task_ref='task:example:profile',request_revision=1,
        pointer_ref=pointer['pointer_id'],trust_profile_hash=c.sha(policy),use_class='LOCAL_CONTEXT',object_id=policy['object_id'],allowed_size=c.BODY_MAX,
        nonce='a'*64,deadline=now+60,issued_at=now,subject_request_ref=None,owner_transport_scope=policy['transport_scope']))
    entry=dict(version='g51.entry.v01',pointer_id=pointer['pointer_id'],publisher_root_id=cap.root_id,stream_id=pointer['revocation_stream_id'],revision=1,state='ACTIVE',effective_at=now,reason_ref='reason:example:active');entry['entry_hash']=c.sha(entry)
    status=c.sign(cap,keys,'STATUS',dict(version='g51.status.v01',entry=entry,requested_pointer_hash=c.sha(pointer),requester=request['requester'],subject_request_ref=request['request_id'],
        request_revision=1,nonce=request['nonce'],checked_at=now,valid_until=now+60),manifest['manifest_id'].split(':')[1])
    release=c.sign(cap,keys,'RELEASE',dict(version='g51.release.v01',state='RELEASED',request_ref=request['request_id'],request_revision=1,pointer_ref=pointer['pointer_id'],
        manifest_ref=manifest['manifest_id'],body_hash=c.sha(body),recipient=request['requester'],use_class=request['use_class'],nonce=request['nonce'],deadline=request['deadline'],
        release_review_ref=body['source_review_ref']),manifest['manifest_id'].split(':')[1])
    bundle=dict(body=body,manifest=manifest,release=release)
    c.check_bundle(bundle,descriptor,request,status,policy,now,{}, {},profile=PROFILE)
    # This is a component crypto/profile check, NOT an executed release or grant.
    return dict(classification='SIGNED_COMPONENT_PROFILE_CHECK_NOT_TRANSPORT_AUTHORITY',bundle=bundle,descriptor=descriptor,request=request,status=status,policy=policy,use_time=now)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('output',type=Path);args=parser.parse_args();args.output.mkdir()
    started=time.monotonic();values=[calculate(7),calculate(11)]
    assert [x['output'] for x in values]==[23,35] and all(x['attempts']==1 for x in values)
    now=int(time.time());refusal=n.root_review('root:example:integer','transaction:example:refusal','candidate:example:refused','source:example:missing',
        dict(required_input_present=False),dict(status='INSUFFICIENT_EVIDENCE'),now)
    assert refusal[2].decision!='ACCEPT'
    try:calculate(True)
    except ValueError as exc:assert str(exc)=='integer_range_or_type';bad=str(exc)
    else:raise AssertionError('bool_as_int')
    signed=signed_profile(values[0]);n.save(args.output/'signed_profile.json',signed)
    n.save(args.output/'result.json',dict(status='PASS_NATIVE_GENERIC_EXAMPLE',values=values,refusal=n.root_plain(refusal),invalid_input=bad,
        actual_work_calls=2,work_attempts=2,provider_calls=0,peer_io=0,business_effects=0,seconds=time.monotonic()-started))
    origins={name:str(Path(m.__file__).resolve()) for name,m in sys.modules.copy().items() if getattr(m,'__file__',None) and name.split('.')[0] in ('hedgehog','demo','tests')}
    n.save(args.output/'import_origins.json',origins)
    print(json.dumps(dict(status='PASS',outputs=[x['output'] for x in values],seconds=time.monotonic()-started)))
if __name__=='__main__':main()
