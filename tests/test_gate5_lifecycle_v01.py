"""Finite G52 hostile/persistence controls on immutable lifecycle captures."""
import copy
import json
from pathlib import Path
import shutil
import sys
import time
from hedgehog.external_drs import gate5_contracts_v01 as c, gate5_native_v01 as n, gate5_exchange_v01 as e, gate5_lifecycle_v01 as life
from tests.test_gate5_calibration_exchange_v01 import hostile_fixture,run_controls as g51_controls


def controls(capture,folder):
    capture,folder=Path(capture),Path(folder);folder.mkdir(parents=True,exist_ok=False);started=time.monotonic();rows=[]
    read=lambda name:json.loads((capture/name).read_text())
    accepted=read('B/r1/accepted.json');record=accepted['import_record'];now=accepted['use_time'];policy=record['policy']
    body=record['bundle']['body'];pointer=record['descriptor']['value'];request=record['request'];status=record['status']
    def good(name,detail=None):rows.append(dict(name=name,outcome='PASS',detail=detail))
    def deny(name,fn,reason):
        try:fn()
        except (ValueError,TypeError) as exc:
            c.require(reason in str(exc),'wrong_reason:'+name+':'+str(exc));rows.append(dict(name=name,outcome='REFUSED',reason=str(exc)))
        else:raise AssertionError('control_accepted:'+name)
    before=read('B/before_body.json')
    c.require(before['budget']['payload']==0 and before['quarantine_files']==[] and len(before['index_records'])==1,'pointer_only_snapshot')
    descriptor=before['index_records'][0]['content']['descriptor'];c.require(descriptor==record['descriptor'],'pointer_actual_index')
    def no_body_keys(value):
        if type(value) is dict:return not set(value)&{'observations','correction','offset','reference','body'} and all(no_body_keys(v) for v in value.values())
        if type(value) is list:return all(no_body_keys(v) for v in value)
        return True
    c.require(no_body_keys(before['index_records']),'index_contains_body');good('F01_actual_pointer_only_index')
    denial=read('B/local_denial_counters.json');c.require(denial['before']==denial['after'],'local_denial_io')
    c.require(read('B/local_policy_refusal.json')['policy']['accept_calibration'] is False,'local_denial_actual_policy');good('F02_actual_local_denial')
    events=read('B/session1/events.json');audit=next(x for x in events if x['request']['use_class']=='AUDIT')
    c.require(audit['response']['value']['body'] is None and audit['response']['value']['release']['value']['state']=='REFUSED','audience_use_refusal')
    good('F03_authenticated_A_refusal')
    cap=c.crypto.generate_root_signer_capability_v01(root_id='root:gate5:declared-hostile-test');keys=c.crypto.build_trusted_root_key_set_v01(capabilities=(cap,))
    def fixture(changed_body=None,changed_pointer=None):
        selected=copy.deepcopy(changed_pointer or pointer)
        selected['safe_summary']=c.canonical(dict(kind='calibration',unit_id=selected['published_scope']['unit_id'],quantity_id=selected['published_scope']['quantity_id'])).decode()
        return hostile_fixture(changed_body or body,selected,request,status,policy,cap,keys)
    valid=fixture();c.check_bundle(*valid,now,{},{});good('coherent_hostile_key_allowed_neighbor')
    fixtures={}
    for label,changed_body,changed_pointer,reason in [
        ('domain',body,dict(pointer,semantic_address=dict(pointer['semantic_address'],domain='OTHER'),published_scope=dict(pointer['published_scope'],domain='OTHER')),'schema_scope'),
        ('unit',dict(body,unit_id='other_unit'),dict(pointer,published_scope=dict(pointer['published_scope'],unit_id='other_unit')),'source_scope'),
        ('recipient',body,dict(pointer,recipient_scope=['root:other']),'local_scope')]:
        value=fixture(changed_body,changed_pointer)
        c.verify(value[1],value[4]['peer_keys'],'POINTER',value[1]['value']['artifact_manifest_ref'].split(':')[1]);c.validate('body',value[0]['body']);c.validate('pointer',value[1]['value'])
        deny('F05_signed_foreign_'+label,lambda value=value:c.check_bundle(*value,now,{},{}),reason);fixtures[label]=value
    changed=c.with_id('request',dict(request,request_revision=2))
    deny('F07_request_revision_binding',lambda:c.check_bundle(record['bundle'],record['descriptor'],changed,status,policy,now,{},{}),'release_request_binding')
    substitution=copy.deepcopy(valid);substitution[1]['value']['publisher_key_id']='root-key:other'
    substitution=list(substitution);substitution[1]=c.sign(cap,keys,'POINTER',c.with_id('pointer',substitution[1]['value']),substitution[1]['value']['artifact_manifest_ref'].split(':')[1])
    deny('F13_pointer_key_substitution',lambda:c.check_pointer(substitution[1],substitution[4],now),'publisher_identity')
    deny('F13_unpinned_signer',lambda:c.verify(valid[1],policy['peer_keys'],'POINTER',valid[1]['value']['artifact_manifest_ref'].split(':')[1]),'signature_invalid')
    for field in ('permission','RootFinal','capability_handle','command','import_path'):
        changed_body=dict(body,**{field:'UNTRUSTED_NON_EXECUTABLE_TEST_VALUE'})
        value=fixture(changed_body)
        c.verify(value[1],value[4]['peer_keys'],'POINTER',value[1]['value']['artifact_manifest_ref'].split(':')[1])
        deny('F14_closed_'+field,lambda value=value:c.check_bundle(*value,now,{},{}),'closed_fields')
    value=fixture(changed_pointer=dict(pointer,transport_object_id='object:other'))
    deny('F16_signed_foreign_object',lambda:c.check_pointer(value[1],value[4],now),'pinned_object_identity')
    for endpoint in ('https://other.example/object','../private','endpoint:foreign'):
        deny('F16_unsupported_route_'+endpoint,lambda endpoint=endpoint:c.check_route(pointer,policy,endpoint=endpoint),'route_endpoint')
    c.check_route(pointer,policy);good('F17_one_hop_neighbor')
    deny('F17_self_pointer',lambda:c.check_route(pointer,policy,visited=(pointer['pointer_id'],)),'route_cycle')
    deny('F17_depth_two',lambda:c.check_route(pointer,policy,depth=1),'route_hop_limit')
    # Authenticated monotonic observation stores terminal data, but invalid statements do not poison it.
    store=life.ImportStore(folder/'status_control');bundle,desc,req,env,pol=valid
    key,entry=c.authenticate_status(env,desc['value'],req,pol,now,{})
    store.observe(env,desc['value'],req,pol,now);initial=life.read(store.path)['highwater']
    same_req=c.with_id('request',dict(req,nonce='a'*64));same_value=dict(env['value'],subject_request_ref=same_req['request_id'],nonce=same_req['nonce'])
    same=c.sign(cap,keys,'STATUS',same_value,desc['value']['artifact_manifest_ref'].split(':')[1])
    store.observe(same,desc['value'],same_req,pol,now);c.require(life.read(store.path)['highwater']==initial,'same_entry_new_envelope_conflict');good('same_entry_fresh_nonce_not_conflict')
    altered=dict(entry,reason_ref='reason:test:different');altered['entry_hash']=c.sha({k:v for k,v in altered.items() if k!='entry_hash'})
    equivocal=c.sign(cap,keys,'STATUS',dict(env['value'],entry=altered),desc['value']['artifact_manifest_ref'].split(':')[1])
    deny('F11_signed_status_equivocation',lambda:store.observe(equivocal,desc['value'],req,pol,now),'status_equivocation')
    c.require(life.read(store.path)['highwater']==initial and life.read(store.path)['quarantine'][-1]['reason']=='status_equivocation','equivocation_not_quarantined')
    invalid=copy.deepcopy(env);s=invalid['signature']['signature_hex'];invalid['signature']['signature_hex']=('1' if s[0]!='1' else '2')+s[1:]
    deny('invalid_status_cannot_poison_highwater',lambda:store.observe(invalid,desc['value'],req,pol,now),'signature_invalid')
    c.require(life.read(store.path)['highwater']==initial,'invalid_poisoned_state')
    terminal=dict(entry,revision=entry['revision']+1,state='SUPERSEDED',reason_ref='reason:test:terminal')
    terminal['entry_hash']=c.sha({k:v for k,v in terminal.items() if k!='entry_hash'})
    signed=c.sign(cap,keys,'STATUS',dict(env['value'],entry=terminal),desc['value']['artifact_manifest_ref'].split(':')[1])
    store.observe(signed,desc['value'],req,pol,now)
    reopened=life.ImportStore(folder/'status_control')
    deny('F10_terminal_current_refusal',lambda:c.check_status(signed,desc['value'],req,pol,now,life.read(reopened.path)['highwater']),'status_not_active')
    deny('F10_old_active_after_reopen',lambda:reopened.observe(env,desc['value'],req,pol,now),'status_rollback')
    c.require(life.read(reopened.path)['highwater'][key]==terminal,'terminal_lost');good('terminal_stored_before_refusal')
    # Different, mathematically valid body at one source revision reaches conflict, not signature/arithmetic refusal.
    content=life.ImportStore(folder/'content_control');checked=content.validate_bundle(*valid,now);content.import_body(checked,desc['value'])
    changed_body=dict(body,observations=[109,109,109],total=327,correction=dict(num=-9,den=1))
    other=fixture(changed_body)
    c.check_bundle(*other,now,{},{});good('same_revision_changed_body_valid_components')
    deny('F11_signed_content_conflict',lambda:content.validate_bundle(*other,now),'source_equivocation')
    c.require(len(life.read(content.path)['sources'])==1 and life.read(content.path)['quarantine'][-1]['reason']=='source_equivocation','content_quarantine')
    fixtures.update(valid=valid,equivocation=equivocal,terminal=signed,changed_same_revision=other)
    n.save(folder/'signed_hostile_fixtures.json',dict(classification='DECLARED_HOSTILE_TEST_SIGNER_NOT_HONEST_NATIVE_SOURCE',public_keys=c.crypto.trusted_root_key_set_to_plain_dict_v01(keys),fixtures=fixtures))
    # Reopening cannot reset A, and a supplied task label cannot establish a context.
    budget_path=folder/'publisher_budget.json';shutil.copy2(capture/'A/publisher_budget.json',budget_path)
    source_budget=e.PublisherBudget(budget_path,life.contexts());attack=c.with_id('request',dict(request,nonce='b'*64))
    c.require(source_budget.reserve(attack) is False,'reopened_publisher_budget');good('publisher_reopened_budget_refusal')
    unknown=c.with_id('request',dict(attack,task_ref='task:caller-invented'))
    deny('caller_cannot_establish_task',lambda:source_budget.reserve(unknown),'publisher_unknown_task_context')
    c.require('task:caller-invented' not in source_budget.read()['tasks'],'unknown_context_created')
    wrong_context=c.with_id('request',dict(attack,task_ref=life.SCOPE))
    deny('approved_refusal_context_is_not_budget_reset',lambda:source_budget.reserve(wrong_context),'publisher_context_use')
    other_revision=c.with_id('request',dict(attack,task_ref=life.REVISION_TWO))
    c.require(not source_budget.matches_source(other_revision,1) and source_budget.matches_source(other_revision,2),'context_revision_binding')
    good('new_declared_task_cannot_disclose_old_revision')
    # A derived field-preserving view lets the original 43-control script consume this actual baseline.
    view=folder/'g51_component_view';(view/'A').mkdir(parents=True);(view/'B').mkdir()
    projections={'A/source_work.json':read('A/r1/source_work.json'),'B/corrected_work.json':accepted['work'],
        'B/response_LOCAL_CONTEXT.json':record['bundle'],'B/descriptor.json':record['descriptor'],'B/request_LOCAL_CONTEXT.json':request,
        'B/status_LOCAL_CONTEXT.json':status,'operator_trust.json':read('operator_trust.json'),
        'B/result.json':dict(accepted=dict(use_time=now)),'B/budget.json':read('B/budgets/'+life.BASELINE+'.json')}
    for name,value in projections.items():n.save(view/name,value)
    n.save(view/'DERIVATION.json',dict(source=str(capture),classification='DERIVED_FIELD_VIEW_NOT_A_NEW_COLLECTOR_OR_RESTORED_AUTHORITY',fields=list(projections)))
    g51_controls(view,folder/'g51_affected_controls')
    good('G51_affected_43_controls_on_G52_capture')
    for name in ('status_unavailable','revoked_current_use','restart_old_active'):
        c.require(read('B/'+name+'.json')['review']['result']['decision']!='ACCEPT','recorded_refusal');good(name)
    c.require(read('B/r2/accepted.json')['claim']['assessment']=='REVIEW_REQUIRED','lawful_continuation');good('lawful_actual_Work_after_refusals')
    n.save(folder/'result.json',dict(status='PASS_G52_FOCUSED',controls=rows,g51_controls=43,seconds=time.monotonic()-started,
        modes='FRESH_PURE_AND_DISPOSABLE_STATE_CONTROLS_ON_FINAL_SOURCE; ACTUAL_RECORDED_IPC_LIFECYCLE; ONE_NEW_G51_NATIVE_INPUT_CONTRAST'))
    print(json.dumps(dict(status='PASS_G52_FOCUSED',controls=len(rows),g51_controls=43,seconds=time.monotonic()-started)))


def supplied_controls(capture,expected_path,source_root,folder):
    """Declared test expectations reach relationships without changing accepted pins."""
    import hashlib
    from hedgehog.external_drs import gate5_lifecycle_supplied_v01 as proof
    from hedgehog.kernel import root_decision_v01 as roots
    capture,expected_path,source_root,folder=map(Path,(capture,expected_path,source_root,folder))
    folder.mkdir();expected=json.loads(expected_path.read_text());rows=[]
    targets=[roots.decide_root_v01,roots._decide_validated,n.native_work]
    counts={fn.__name__:0 for fn in targets};names={fn.__code__:fn.__name__ for fn in targets}
    def observed(code,*args):
        counts[names[code]]+=1;raise AssertionError('unexpected_execution:'+names[code])
    def deny(name,call,reason):
        try:call()
        except ValueError as exc:c.require(str(exc)==reason,'unexpected_proof_reason:'+str(exc))
        else:raise AssertionError('proof_accepted:'+name)
        rows.append(dict(name=name,outcome='REFUSED',reason=reason))
    tool=4;sys.monitoring.use_tool_id(tool,'g52_proof_controls')
    sys.monitoring.register_callback(tool,sys.monitoring.events.PY_START,observed)
    for fn in targets:sys.monitoring.set_local_events(tool,fn.__code__,sys.monitoring.events.PY_START)
    try:
        positive=proof.verify(capture,expected,source_root)
        bad=copy.deepcopy(expected);name=next(iter(bad['source_pins']));bad['source_pins'][name]='0'*64
        deny('wrong_external_source_pin',lambda:proof.verify(capture,bad,source_root),'external_source_pin:'+name)
        bad=copy.deepcopy(expected);bad['capture_files']['required_missing.json']=dict(bytes=1,sha256='0'*64,mode='0644')
        deny('missing_evidence',lambda:proof.verify(capture,bad,source_root),'missing_evidence:required_missing.json')
        clone=folder/'test_capture';shutil.copytree(capture,clone,ignore=shutil.ignore_patterns('private'))
        one=json.loads((capture/'B/r1/accepted.json').read_text());two=json.loads((capture/'B/r2/accepted.json').read_text())
        altered=copy.deepcopy(two);altered['final_review']=one['final_review']
        changed=clone/'B/r2/accepted.json';n.save(changed,altered);raw=changed.read_bytes()
        test_expected=copy.deepcopy(expected)
        test_expected['origin']='DECLARED_TEST_EXPECTATION_NOT_PRODUCTION_REANCHORING'
        test_expected['capture_files']['B/r2/accepted.json']=dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),mode='0644')
        n.save(folder/'test_expected.json',test_expected);n.save(folder/'coherent_mutation.json',altered)
        deny('genuine_wrong_root_record_with_updated_test_pin',lambda:proof.verify(clone,test_expected,source_root),'recorded_root_selection')
        deny('genuine_root_claim_not_replaced_by_summary_102',lambda:proof.root_record(one['final_review'],c.ROOT_B,
            one['work']['artifact']['artifact_id'],two['claim'],one['import_record']['candidate']['import_id']),'recorded_root_claim_binding')
        c.require(proof.verify(capture,expected,source_root)==positive,'positive_changed_after_controls')
        rows.append(dict(name='original_positive_after_refusals',outcome='PASS'))
    finally:
        for fn in targets:sys.monitoring.set_local_events(tool,fn.__code__,0)
        sys.monitoring.free_tool_id(tool)
    c.require(not any(counts.values()),'proof_controls_executed_runtime')
    n.save(folder/'result.json',dict(status='PASS_G52_SUPPLIED_CONTROLS',controls=rows,observed=counts,
        accepted_evidence_unchanged=True,classification='EXPLICIT_TEST_PINS_ONLY; NO_PRODUCTION_REANCHORING'))
    print(json.dumps(dict(status='PASS_G52_SUPPLIED_CONTROLS',controls=len(rows),observed=counts)))


if __name__=='__main__':controls(sys.argv[1],sys.argv[2])
