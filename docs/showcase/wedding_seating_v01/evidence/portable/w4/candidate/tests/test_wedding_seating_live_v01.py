"""Cheap local W3 boundary controls. Fabricated records are test-only, not live evidence."""
from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
import pytest
from hedgehog.domains.wedding_seating import semantic_adapter_v01 as s,native_contracts_v01 as c,supplied_v01 as supplied

BASE=(Path(__file__).parents[1]/'fixtures/wedding_seating/reference_problem_v01.json').read_bytes()
def intake(**kwargs):
    return s.LiveIntakeV01(BASE,BASE,'request:test:meaning','Create a complete seating plan.',amendment_guests=('guest_07','guest_08'),private_tokens=('PRIVATE_CANARY_W3',),**kwargs)
def payloads(task='GENERATE',profile='MIX_CIRCLES_V01'):
    return [dict(task_kind=task,needs=s.WORK[task][0],requested_outputs=['CLARIFICATION'] if task=='CLARIFY' else ['VALIDATION_REPORT'] if task=='VALIDATE_EXISTING' else ['SEATING_CANDIDATES','VALIDATION_REPORT'],unresolved=['Which objective do you prefer?'] if task=='CLARIFY' else [],reason='Interpret supported request.'),
        dict(task_kind=task,objective_profile=None if task=='CLARIFY' else profile,needed_capabilities=s.WORK[task][1],amendments=[],unresolved=['Which objective do you prefer?'] if task=='CLARIFY' else [],reason='Keep mandatory law.')]
def records(i,ps=None):
    ps=ps or payloads();out=[]
    for role,p in zip(s.ROLES,ps):
        raw=c.canonical(p).decode();body=c.canonical(s.request_body_v01(i,role,ps[0] if role==s.ROLES[1] else None)).decode()
        v=dict(version=s.VERSION,origin='LIVE_ROLE_ORIGIN',request_ref=i.request_ref,role=role,model='synthetic-test-only',model_version='synthetic-test-only',
            capture_ref='',source_snapshot=c.digest(i.current_bytes),schema_sha256=c.digest(s.schema_v01(role)),request_body=body,raw_response=raw,
            response_sha256=c.digest(raw.encode()),egress=dict(method='POST',scheme='https',host='generativelanguage.googleapis.com',path='/v1beta/models/synthetic-test-only:generateContent',query=''),
            started='2026-09-24T00:00:00+00:00',ended='2026-09-24T00:00:01+00:00',seconds=1)
        v['capture_ref']=c.identity('capture',dict(request=c.digest(body.encode()),response=v['response_sha256'],request_ref=i.request_ref,role=role,model=v['model'],started=v['started']))
        out.append(v)
    return out

def test_actual_egress_refusals_zero_send_v01():
    import httpx
    i=intake();body=s.request_body_v01(i,s.ROLES[0]);meta=records(i)[0]['egress'];sent=[]
    def hook(request):
        m=dict(method=request.method,scheme=request.url.scheme,host=request.url.host,path=request.url.path,query=request.url.query.decode())
        s.check_egress_v01(request.content,m,intake=i,role=s.ROLES[0],model='synthetic-test-only')
    def transport(request):sent.append(True);return httpx.Response(200,json={'synthetic':True})
    url='https://'+meta['host']+meta['path']
    with httpx.Client(transport=httpx.MockTransport(transport),event_hooks={'request':[hook]}) as client:
        for where in ('structured','free_text','metadata','foreign_projection'):
            bad=deepcopy(body);target=url
            if where=='structured':bad['private_name']='PRIVATE_CANARY_W3'
            elif where=='free_text':bad['contents'][0]['parts'][0]['text']+='PRIVATE_CANARY_W3'
            elif where=='metadata':target=url+'?label=PRIVATE_CANARY_W3'
            else:bad=s.request_body_v01(replace(i,request_ref='request:foreign'),s.ROLES[0])
            with pytest.raises(ValueError):client.post(target,content=c.canonical(bad))
        assert sent==[]
        with pytest.raises(ValueError):s.request_body_v01(replace(i,structural_disclosure=False),s.ROLES[0])
        assert sent==[]
        client.post(url,content=c.canonical(body));assert len(sent)==1

def test_live_bindings_and_field_consumption_v01():
    i=intake();rs=records(i);owner,material=s.accepted_material_v01(i,rs)
    assert owner.profile=='MIX_CIRCLES_V01' and material['semantics'][1]['capture_ref']==rs[1]['capture_ref']
    ps=payloads(profile='KEEP_FAMILIAR_V01');wrong_but_safe,_=s.accepted_material_v01(i,records(i,ps))
    assert wrong_but_safe.profile=='KEEP_FAMILIAR_V01'
    assert not hasattr(i,'expected_profile') and not hasattr(i,'case_id')
    for key,value in (('role',s.ROLES[1]),('request_ref','request:foreign'),('source_snapshot','0'*64),('capture_ref','foreign'),('schema_sha256','0'*64),('origin','CONTROLLED_FIXTURE')):
        bad=deepcopy(rs);bad[0][key]=value
        with pytest.raises(ValueError):s.accepted_material_v01(i,bad)
    for field,value in (('authority',True),('endpoint','http:foreign'),('unknown',[])):
        ps=payloads();ps[1][field]=value
        with pytest.raises(ValueError):s.accepted_material_v01(i,records(i,ps))
    ps=payloads();ps[1]['needed_capabilities']=['SHELL']
    with pytest.raises(ValueError):s.accepted_material_v01(i,records(i,ps))
    assert s.accepted_material_v01(i,deepcopy(rs))[0]==owner

def test_revision_preserves_protected_law_and_replaces_v01():
    i=intake();ps=payloads();add=dict(operation='ADD',predicate='ALLOWED_TABLES',subjects=['guest_07'],tables=['table_2'],source_ref=i.request_ref,replaces=[])
    ps[1]['amendments']=[add];owner,m=s.accepted_material_v01(i,records(i,ps))
    assert all(v in m['problem']['hard_conditions'] for v in i.check()[0]['hard_conditions'])
    added=[v for v in m['problem']['hard_conditions'] if v not in i.check()[0]['hard_conditions']][0]
    nxt=replace(i,current_bytes=owner.problem_bytes,request_ref='request:next')
    ps2=payloads('REVISE');ps2[1]['amendments']=[dict(add,operation='REPLACE',tables=['table_1'],source_ref=nxt.request_ref,replaces=[added['condition_id']])]
    new,material=s.accepted_material_v01(nxt,records(nxt,ps2))
    assert new.problem().to_plain_v01()['parent_problem_ref']==owner.problem().content_id
    assert added not in material['problem']['hard_conditions']
    assert material['revision_acknowledgement']['mode']=='SCRIPTED_CONTROLLED_OWNER_INPUT'
    for change in ('protected','source','guest','table','unknown'):
        bad=deepcopy(ps2)
        if change=='protected':bad[1]['amendments'][0]['replaces']=[i.check()[0]['hard_conditions'][0]['condition_id']]
        elif change=='source':bad[1]['amendments'][0]['source_ref']='request:foreign'
        elif change=='guest':bad[1]['amendments'][0]['subjects']=['guest_01']
        elif change=='table':bad[1]['amendments'][0]['tables']=['table_9']
        else:bad[1]['amendments'][0]['delete']=True
        with pytest.raises(ValueError):s.accepted_material_v01(nxt,records(nxt,bad))

def test_unresolved_without_invented_profile_v01():
    i=intake();rs=records(i,payloads('CLARIFY'));owner,m=s.accepted_material_v01(i,rs)
    assert owner.profile is None and m['profile'] is None
    result=s.execute_live_v01(i,rs,now=1700000000)
    assert result['status']=='NEEDS_CLARIFICATION' and result['search_calls']==0 and result['questions']

def test_verify_inherits_only_bound_prior_information_v01():
    i=replace(intake(),prior_output_bytes=c.canonical(dict(profile='KEEP_FAMILIAR_V01')),prior_result_ref='result:prior')
    ps=payloads('VALIDATE_EXISTING');ps[1]['objective_profile']=None
    owner,material=s.accepted_material_v01(i,records(i,ps))
    assert owner.profile=='KEEP_FAMILIAR_V01' and material['semantics'][1]['objective_profile'] is None
    assert material['objective_information_source']['result_ref']=='result:prior'
    ps[1]['objective_profile']='MIX_CIRCLES_V01'
    with pytest.raises(ValueError):s.accepted_material_v01(i,records(i,ps))

def test_group_amendment_and_complete_replacement_v01():
    i=intake();ps=payloads();ps[1]['amendments']=[dict(operation='ADD',predicate='ALLOWED_TABLES',subjects=['guest_07','guest_08'],tables=['table_2'],source_ref=i.request_ref,replaces=[])]
    owner,m=s.accepted_material_v01(i,records(i,ps))
    added=[v for v in m['problem']['hard_conditions'] if v['source_ref']==i.request_ref]
    assert len(added)==2 and {tuple(v['subjects']) for v in added}=={('guest_07',),('guest_08',)}
    nxt=replace(i,current_bytes=owner.problem_bytes,request_ref='request:group:next');ps=payloads('REVISE')
    ps[1]['amendments']=[dict(operation='REPLACE',predicate='ALLOWED_TABLES',subjects=v['subjects'],tables=['table_1'],source_ref=nxt.request_ref,replaces=[v['condition_id']]) for v in added]
    new,material=s.accepted_material_v01(nxt,records(nxt,ps))
    assert all(v not in material['problem']['hard_conditions'] for v in added)
    ps[1]['amendments'].pop()
    with pytest.raises(ValueError,match='incomplete_added_requirement'):s.accepted_material_v01(nxt,records(nxt,ps))

def test_saved_display_consistency_v01():
    import os
    data=json.loads(Path(os.environ['W3_SAVED_C1']).read_text());m=data['material'];o=data['owner']
    owner=c.OwnerContextV01(c.canonical(o['problem']),o['request_ref'],o['task_kind'],o['profile'],m['approved_intent'],o['parent_ref'])
    assert supplied.validate_saved_run_v01(data,owner=owner)['status']=='PASS'
    bad=deepcopy(data);last=json.loads(bad['results'][-1]['result']['output'][0]['value']);last['safe_output']['assignment']=[0]*12
    bad['results'][-1]['result']['output'][0]['value']=c.canonical(last).decode();bad['output']=last['safe_output']
    bad['root_result']['selected_candidate_id']=c.identity('wedding_result',bad['output'])
    with pytest.raises(ValueError,match='supplied_displayed_plan'):supplied.validate_saved_run_v01(bad,owner=owner)
    assert supplied.validate_saved_run_v01(deepcopy(data),owner=owner)['status']=='PASS'
