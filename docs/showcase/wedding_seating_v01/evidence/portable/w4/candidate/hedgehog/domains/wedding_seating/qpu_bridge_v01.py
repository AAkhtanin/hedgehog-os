"""Explicit application bridge, not a native PURE effect capability.

Owner transport scope and fresh native Root evidence are both necessary.
Durable slots do not reset on timeout, expiry, process death or unknown POST outcome.
"""
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import time
import uuid
from . import native_contracts_v01 as c, native_adapter_v01 as native
from . import runtime_v01 as runtime, qpu_contracts_v01 as q

DEVICE='arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q'
ACCOUNT='296280725196'
PRINCIPAL='arn:aws:iam::296280725196:user/radiolaria-quantum'
BUCKET='amazon-braket-radiolaria-wedding-296280725196-us-west-1-h2xwk03'
ENDPOINT='https://braket.us-west-1.amazonaws.com'
MAX_RESULT=8*1024*1024

def stamp():return datetime.now(timezone.utc).isoformat()

def atomic_json(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    c.require(not path.is_symlink(),'ledger_symlink')
    temporary=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
    with temporary.open('x') as f:
        json.dump(value,f,sort_keys=True,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(temporary,path)
    fd=os.open(path.parent,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)

class LedgerV01:
    def __init__(self,directory):self.directory=Path(directory);self.path=self.directory/'ledger.json'
    @contextmanager
    def locked(self):
        self.directory.mkdir(parents=True,exist_ok=True)
        c.require(not self.directory.is_symlink(),'ledger_directory_symlink')
        fd=os.open(self.directory/'writer.lock',os.O_CREAT|os.O_RDWR|os.O_NOFOLLOW,0o600)
        try:
            fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
            value=json.loads(self.path.read_text()) if self.path.exists() else dict(version='WeddingQpuLedgerV01',attempts=[])
            yield value
        finally:os.close(fd)
    def save(self,value):atomic_json(self.path,value)
    def reserve(self,ledger,profile,body,approval):
        c.require(not any(r['profile']==profile for r in ledger['attempts']),'existing_profile_attempt_resume_only')
        c.require(len(ledger['attempts'])<2 and sum(r['reserved_microusd'] for r in ledger['attempts'])+725000<=1450000,'durable_task_cost_limit')
        row=dict(profile=profile,state='PREPARED',created=stamp(),request=body,request_sha256=c.digest(body),
            client_token=body['clientToken'],reserved_microusd=725000,network_attempts=0,approval=approval)
        ledger['attempts'].append(row);self.save(ledger)
        row['state']='AUTHORIZED';self.save(ledger)
        return row

def check_scope_v01(scope):
    c.require(scope['runtime_profile']=='radiolaria-quantum' and scope['runtime_arn']==PRINCIPAL and scope['account_id']==ACCOUNT,'exact_principal_scope')
    c.require(scope['device_arn']==DEVICE and scope['region']=='us-west-1' and scope['bucket']==BUCKET,'exact_cloud_scope')
    c.require(scope['prefix']=='wedding-v02/' and scope['output_prefix'].startswith('wedding-v02/w4-') and '..' not in scope['output_prefix'] and scope['output_prefix'].endswith('/'),'output_prefix')
    c.require(scope['shots']==1000 and type(scope['shots']) is int and scope['max_unique_tasks']==2 and scope['max_qpu_microusd']==1450000,'finite_allowance')
    c.require(scope['task_microusd']==300000 and scope['shot_microusd']==425,'reviewed_price')
    c.require(scope['structural_disclosure'] is True and scope['revoked'] is False,'current_disclosure_permission')
    c.require(scope['authorization']['scope']=='PRESENT_W4_NOT_RETROACTIVE_W0' and len(scope['authorization']['prompt_sha256'])==64,'owner_authorization_source')

def request_v01(scope,program,token):
    check_scope_v01(scope)
    c.require(type(token) is str and 1<=len(token)<=64,'stable_token')
    return dict(action=program.decode(),clientToken=token,deviceArn=DEVICE,outputS3Bucket=BUCKET,
        outputS3KeyPrefix=scope['output_prefix'],shots=1000)

def check_request_v01(body,*,scope,material,numeric,token):
    c.require(body==request_v01(scope,body['action'].encode(),token),'exact_request_surface')
    q.check_program_v01(material,numeric,body['action'].encode())

@dataclass
class PermitV01:
    request: dict
    scope: dict
    decision: tuple
    expires: int
    prepared: object

    def check(self,scope,body,now):
        check_scope_v01(scope)
        c.require(scope==self.scope and body==self.request and now<self.expires,'current_permit_request_or_expiry')
        c.require(type(self.prepared) is runtime.NativeRunV01,'live_native_prepare_required')
        c.require(self.prepared.owner.task_kind=='QPU_PREPARE','prepare_kind')
        self.prepared.validate_current(self.prepared.owner)
        check_request_v01(body,scope=scope,material=self.prepared.material,numeric=self.prepared.output,token=body['clientToken'])
        c.require(not native.roots.validate_root_decision_result_v01(kernel=self.decision[0],decision_input=self.decision[1],result=self.decision[2]),'independent_native_root_validation')
        c.require(self.decision[2].selected_candidate_id==c.identity('wedding_qpu_request',dict(request=body,scope=scope,expires=self.expires)),'root_exact_request')

    def evidence(self):
        return dict(request_sha256=c.digest(self.request),scope=self.scope,expires=self.expires,
            root_kernel=runtime.plain(self.decision[0]),root_input=runtime.plain(self.decision[1]),root_result=runtime.plain(self.decision[2]),
            native_prepare_result_ref=self.prepared.evidence['artifact']['artifact_id'],classification='LIVE_QPU_EXPLICIT_PROVIDER_BRIDGE')

def permit_v01(prepared,scope,body,now):
    c.require(type(prepared) is runtime.NativeRunV01,'live_native_prepare_required');prepared.validate_current(prepared.owner)
    check_request_v01(body,scope=scope,material=prepared.material,numeric=prepared.output,token=body['clientToken'])
    expires=now+600;claim=dict(request=body,scope=scope,expires=expires)
    decision=native.root_review(prepared.owner.problem().to_plain_v01()['owner_root_id'],'transaction:'+prepared.owner.request_ref,
        c.identity('wedding_qpu_request',claim),prepared.owner.request_ref,
        dict(native_numeric_consumed=True,exact_disclosed_request=True,current_owner_transport_scope=True),
        prepared.evidence['artifact']['artifact_id'],prepared.program.candidate.bsep_ref,prepared.program.topology_artifact.artifact_id,now,
        predicate='wedding_qpu_exact_submission_evidence',claim_value=claim)
    result=PermitV01(json.loads(c.canonical(body)),json.loads(c.canonical(scope)),decision,expires,prepared)
    result.check(scope,body,now);return result

def clients_v01(scope):
    check_scope_v01(scope)
    forbidden=[k for k in os.environ if k.startswith(('AWS_','AMAZON_')) or k.lower() in ('http_proxy','https_proxy','all_proxy')]
    c.require(not forbidden,'ambient_aws_or_proxy_override')
    import boto3
    from botocore.config import Config
    session=boto3.Session(profile_name=scope['runtime_profile'],region_name='us-west-1')
    config=session._session.get_scoped_config()
    c.require(not set(config)&{'aws_access_key_id','aws_secret_access_key','aws_session_token','role_arn','source_profile','credential_process','endpoint_url','services','web_identity_token_file'},'unsupported_profile_override')
    cfg=Config(signature_version='v4',retries={'mode':'standard','total_max_attempts':1},connect_timeout=10,read_timeout=30)
    sts=session.client('sts',config=cfg);identity=sts.get_caller_identity()
    c.require(identity['Account']==ACCOUNT and identity['Arn']==PRINCIPAL,'actual_principal')
    client=session.client('braket',config=cfg);s3=session.client('s3',config=cfg)
    c.require(client.meta.endpoint_url==ENDPOINT and s3.meta.endpoint_url=='https://s3.us-west-1.amazonaws.com','actual_endpoint')
    c.require(client.meta.service_model.operation_model('CreateQuantumTask').input_shape.members['clientToken'].metadata.get('idempotencyToken') is True,'documented_idempotency_token')
    return client,s3,{k:identity[k] for k in ('Arn','Account','UserId')}

def device_v01(client):
    value=client.get_device(deviceArn=DEVICE);cap=json.loads(value['deviceCapabilities'])
    c.require(value['deviceArn']==DEVICE and value['deviceType']=='QPU' and value['providerName']=='Rigetti','actual_device')
    action=cap['action']['braket.ir.openqasm.program']
    c.require({'h','cnot','rx','rz'}<=set(action['supportedOperations']),'required_operations')
    lo,hi=cap['service']['shotsRange'];c.require(lo<=1000<=hi and cap['paradigm']['qubitCount']>=10,'device_bounds')
    c.require(cap['service']['deviceCost']==dict(price=0.000425,unit='shot'),'actual_shot_cost')
    return dict(device_arn=DEVICE,status=value['deviceStatus'],device_type=value['deviceType'],provider=value['providerName'],
        shots_range=[lo,hi],qubit_count=cap['paradigm']['qubitCount'],service=cap['service'],openqasm=action,
        capability_sha256=c.digest(value['deviceCapabilities'].encode()),observed=stamp())

def send_v01(store,ledger,row,permit,scope_loader,client):
    c.require(type(permit) is PermitV01,'actual_current_permit_required')
    c.require(row['state']=='AUTHORIZED' and row['network_attempts']==0,'not_a_fresh_send')
    permit.check(scope_loader(),row['request'],int(time.time()))
    row['state']='SUBMITTING';row['submitting']=stamp();store.save(ledger)
    def before_send(request,**kwargs):
        body=request.body.encode() if isinstance(request.body,str) else request.body
        wire=json.loads(body)
        c.require(request.method=='POST' and request.url==ENDPOINT+'/quantum-task','actual_transport_destination')
        permit.check(scope_loader(),wire,int(time.time()))
        c.require(wire==row['request'] and row['request_sha256']==c.digest(wire),'actual_serialized_request')
        c.require(row['network_attempts']==0,'automatic_post_retry_forbidden')
        row['network_attempts']+=1;row['actual_wire_sha256']=c.digest(body);row['actual_wire']=body.decode();store.save(ledger)
    event='before-send.braket.CreateQuantumTask';client.meta.events.register(event,before_send)
    try:
        result=client.create_quantum_task(**row['request'])
        arn=result['quantumTaskArn']
        c.require(arn.startswith('arn:aws:braket:us-west-1:'+ACCOUNT+':quantum-task/'),'acknowledged_arn')
        row.update(state='ACKNOWLEDGED',task_arn=arn,acknowledged=stamp(),aws_request_id=result.get('ResponseMetadata',{}).get('RequestId'))
        store.save(ledger)
    except Exception as error:
        row.update(state='SUBMISSION_OUTCOME_UNKNOWN' if row['network_attempts'] else 'REFUSED_BEFORE_IO',error_type=type(error).__name__)
        if hasattr(error,'response'):row['aws_error_code']=error.response.get('Error',{}).get('Code')
        store.save(ledger);raise
    finally:client.meta.events.unregister(event,before_send)
    return row

def read_result_v01(store,ledger,row,client,s3):
    arn=row['task_arn'];meta=client.get_quantum_task(quantumTaskArn=arn)
    c.require(meta['quantumTaskArn']==arn and meta['deviceArn']==DEVICE and meta['shots']==1000,'provider_metadata_binding')
    safe={k:(v.isoformat() if isinstance(v,datetime) else v) for k,v in meta.items() if k!='ResponseMetadata'}
    row['metadata']=safe;row['last_read']=stamp();store.save(ledger)
    if meta['status'] in ('FAILED','CANCELLED'):
        row['state']='TERMINAL_PROVIDER_ERROR';store.save(ledger);return None
    if meta['status']!='COMPLETED':row['state']='PENDING';store.save(ledger);return None
    prefix=meta['outputS3Directory']
    c.require(meta['outputS3Bucket']==BUCKET and prefix.startswith(row['request']['outputS3KeyPrefix']) and '..' not in prefix.split('/'),'provider_output_location')
    c.require(meta['createdAt'].timestamp()>=datetime.fromisoformat(row['submitting']).timestamp()-5 and meta['endedAt']>=meta['createdAt'],'provider_chronology')
    key=prefix.rstrip('/')+'/results.json'
    result=s3.get_object(Bucket=BUCKET,Key=key,ExpectedBucketOwner=ACCOUNT)
    c.require(0<result['ContentLength']<=MAX_RESULT,'raw_result_size')
    try:raw=result['Body'].read(MAX_RESULT+1)
    finally:result['Body'].close()
    c.require(len(raw)==result['ContentLength'] and len(raw)<=MAX_RESULT,'raw_result_length')
    decoded=json.loads(raw);task=decoded['taskMetadata']
    c.require(task['id']==arn and task['deviceId']==DEVICE and type(task['shots']) is int and task['shots']==1000,'raw_provider_identity')
    returned_action=decoded.get('additionalMetadata',{}).get('action')
    if returned_action is not None:c.require(returned_action==json.loads(row['request']['action']),'returned_provider_action')
    path=store.directory/(row['profile']+'_results.json')
    if path.exists():c.require(path.read_bytes()==raw,'raw_result_changed')
    else:
        with path.open('xb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
    row.update(state='COMPLETED_RAW',raw_sha256=c.digest(raw),raw_path=path.name,result_key=key);store.save(ledger)
    return raw
