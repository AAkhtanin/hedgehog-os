"""Wedding semantic-only Gemini ingress, local provenance and bounded revisions.

Provider text proposes meaning. Independent intake owns hard law, disclosure and
permitted operations. Scripted acknowledgements are scoped synthetic owner input,
not a browser click; every accepted revision still receives actual Root review.
"""
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timezone
import ast
import json
import os
import re
import time
from . import contracts_v01 as b, native_contracts_v01 as c

VERSION='WeddingLiveSemanticV02'
ROLES=('WEDDING_INTENT_ORCHESTRATOR','WEDDING_REQUIREMENT_ARCHITECT')
WORK={
    'GENERATE':(['REQUIREMENT_REVIEW','EXACT_SEARCH','ORIGINAL_VALIDATION'],['COMPILE_QUBO','SOLVE_EXACT','VALIDATE_ORIGINAL']),
    'REVISE':(['REQUIREMENT_REVIEW','EXACT_SEARCH','ORIGINAL_VALIDATION'],['COMPILE_QUBO','SOLVE_EXACT','VALIDATE_ORIGINAL']),
    'VALIDATE_EXISTING':(['ORIGINAL_VALIDATION'],['VALIDATE_ORIGINAL']),
    'CLARIFY':(['LOCAL_CLARIFICATION'],[]),
}
OUTPUTS={'GENERATE':['SEATING_CANDIDATES','VALIDATION_REPORT'],'REVISE':['SEATING_CANDIDATES','VALIDATION_REPORT'],
    'VALIDATE_EXISTING':['VALIDATION_REPORT'],'CLARIFY':['CLARIFICATION']}
INSTRUCTION=(
    'Interpret the supplied safe synthetic human request, not an expected answer. '
    'Return semantic fields only, with no code, authority, endpoint or assignment. '
    'Use every mandatory output, need and capability listed for the selected task. '
    'GENERATE/REVISE require review, exact search and original validation. '
    'VALIDATE_EXISTING means original validation only; never search for that request. '
    'CLARIFY means local clarification, null objective and a real unresolved question. '
    'The architect must agree with the router task or request clarification. '
    'Preserve every protected hard condition independently of your proposal. '
    'Propose ADD ALLOWED_TABLES for an explicit new guest placement; REPLACE must name '
    'the actual prior added condition IDs. Replace all equivalent prior conditions '
    'for an amended requirement, never accumulate old and new placements. '
    'Use one condition per guest, or one condition propagated through a protected '
    'TOGETHER pair. No change is needed for checking an existing plan. '
    'Do not choose an objective for an ambiguous request that does not identify one. '
    'Profile definitions are options, not answers. Return one JSON object matching the schema.'
)

def _enum(values):return dict(type='string',enum=list(values))
def _array(items):return dict(type='array',items=items)
def _object(props):return dict(type='object',properties=props,required=list(props),additionalProperties=False)
def schema_v01(role):
    common=dict(task_kind=_enum(WORK),unresolved=_array(dict(type='string')),reason=dict(type='string'))
    if role==ROLES[0]:
        common.update(needs=_array(_enum(b.NEEDS)),requested_outputs=_array(_enum(b.OUTPUTS)))
    else:
        common.update(objective_profile=dict(anyOf=[_enum(b.PROFILES),dict(type='null')]),
            needed_capabilities=_array(_enum(('COMPILE_QUBO','SOLVE_EXACT','VALIDATE_ORIGINAL'))),
            amendments=_array(_object(dict(operation=_enum(('ADD','REPLACE')),predicate=_enum(('ALLOWED_TABLES',)),
                subjects=_array(dict(type='string')),tables=_array(dict(type='string')),
                source_ref=dict(type='string'),replaces=_array(dict(type='string'))))))
    return _object(common)

def _problem(raw):
    p=b.parse_json_v01(raw)
    return b.parse_problem_v01(raw,expected_source_bundle_hash=p['source_bundle_hash'],expected_source_refs=c.source_refs(p))

@dataclass(frozen=True)
class LiveIntakeV01:
    base_bytes: bytes
    current_bytes: bytes
    request_ref: str
    safe_intent: str
    permitted_tasks: tuple=tuple(WORK)
    permitted_profiles: tuple=b.PROFILES
    structural_disclosure: bool=True
    amendment_guests: tuple=()
    private_tokens: tuple=()
    prior_output_bytes: bytes | None=None
    prior_result_ref: str | None=None

    def check(self):
        base=_problem(self.base_bytes).to_plain_v01();current=_problem(self.current_bytes).to_plain_v01()
        b.opaque(self.request_ref)
        c.require(type(self.safe_intent) is str and 0<len(self.safe_intent)<=512,'safe_intent_bound')
        c.require(not any(t and t in self.safe_intent for t in self.private_tokens),'private_intent')
        c.require(set(self.permitted_tasks)<=set(WORK) and set(self.permitted_profiles)<=set(b.PROFILES),'permitted_scope')
        c.require(set(self.amendment_guests)<=set(base['guest_ids']),'amendment_scope')
        for key in base:
            if key not in ('problem_revision','parent_problem_ref','source_bundle_hash','hard_conditions'):
                c.require(current[key]==base[key],'protected_problem_field')
        original={v['condition_id']:v for v in base['hard_conditions']}
        current_map={v['condition_id']:v for v in current['hard_conditions']}
        c.require(all(current_map.get(k)==v for k,v in original.items()),'protected_hard_law')
        return base,current

def projection_v01(intake,role,router=None):
    c.require(type(intake) is LiveIntakeV01 and role in ROLES,'live_intake_role')
    base,current=intake.check()
    c.require(intake.structural_disclosure is True,'structural_disclosure_denied')
    result=dict(version=VERSION,role=role,synthetic=True,request_ref=intake.request_ref,safe_intent=intake.safe_intent,
        permitted_tasks=list(intake.permitted_tasks),task_work={k:dict(needs=v[0],capabilities=v[1],outputs=OUTPUTS[k]) for k,v in WORK.items() if k in intake.permitted_tasks},
        objective_definitions={p:('Minimize familiar pairs separated across tables.' if p==b.PROFILES[0] else 'Minimize familiar pairs seated together.') for p in intake.permitted_profiles},
        existing_plan_available=intake.prior_output_bytes is not None)
    if role==ROLES[1]:
        c.require(router is not None,'router_required')
        result.update(router_proposal=router,guest_ids=current['guest_ids'],tables=current['table_records'],
            protected_conditions=base['hard_conditions'],familiarity_pairs=base['familiarity_pairs'],
            added_conditions=[x for x in current['hard_conditions'] if x['condition_id'] not in {v['condition_id'] for v in base['hard_conditions']}],
            permitted_amendment_guests=list(intake.amendment_guests),
            current_problem_ref=_problem(intake.current_bytes).content_id,
            actual_prior_plan=None if intake.prior_output_bytes is None else b.parse_json_v01(intake.prior_output_bytes),
            actual_prior_result_ref=intake.prior_result_ref)
    return result

def request_body_v01(intake,role,router=None):
    text=c.canonical(dict(instruction=INSTRUCTION,context=projection_v01(intake,role,router))).decode()
    return dict(contents=[dict(parts=[dict(text=text)],role='user')],
        generationConfig=dict(temperature=0,candidateCount=1,maxOutputTokens=8192,
            responseMimeType='application/json',responseJsonSchema=schema_v01(role)))

def check_egress_v01(raw,metadata,*,intake,role,model,router=None):
    expected=request_body_v01(intake,role,router)
    c.require(type(raw) is bytes and len(raw)<65536,'egress_size')
    actual=json.loads(raw)
    c.require(actual==expected,'egress_projection')
    c.require(metadata==dict(method='POST',scheme='https',host='generativelanguage.googleapis.com',
        path='/v1beta/models/'+model+':generateContent',query=''),'egress_destination')
    text=c.canonical(actual).decode()+c.canonical(metadata).decode()
    c.require(not any(t and t in text for t in intake.private_tokens),'egress_private_material')
    return True

def parse_payload_v01(raw,role,*,intake):
    value=b.parse_json_v01(raw,limit=b.SEMANTIC_BYTES)
    b.keys(value,' '.join(schema_v01(role)['required']))
    c.require(value['task_kind'] in intake.permitted_tasks,'task_scope')
    b.array(value['unresolved'],8)
    c.require(all(type(q) is str and 0<len(q)<=512 for q in value['unresolved']),'question')
    c.require(type(value['reason']) is str and 0<len(value['reason'])<=1024,'reason')
    c.require(not any(t and t in c.canonical(value).decode() for t in intake.private_tokens),'private_response')
    task=value['task_kind']
    c.require(bool(value['unresolved'])==(task=='CLARIFY'),'unresolved_task')
    if role==ROLES[0]:
        c.require(b.ids(value['needs'])==sorted(WORK[task][0]),'needs')
        expected=OUTPUTS[task]
        c.require(b.ids(value['requested_outputs'])==sorted(expected),'requested_outputs')
    else:
        inherited_profile=None
        if task=='VALIDATE_EXISTING' and intake.prior_output_bytes is not None:
            inherited_profile=b.parse_json_v01(intake.prior_output_bytes)['profile']
            c.require(inherited_profile in intake.permitted_profiles,'prior_objective_scope')
        c.require(value['objective_profile'] is None if task=='CLARIFY' else
            (value['objective_profile'] in (None,inherited_profile) if inherited_profile else value['objective_profile'] in intake.permitted_profiles),'objective_scope')
        c.require(b.ids(value['needed_capabilities'])==sorted(WORK[task][1]),'capabilities')
        b.array(value['amendments'],12)
        c.require(not value['amendments'] or task in ('GENERATE','REVISE'),'amendment_task')
        base,current=intake.check();added={x['condition_id']:x for x in current['hard_conditions'] if x not in base['hard_conditions']}
        seen=set()
        for v in value['amendments']:
            b.keys(v,'operation predicate subjects tables source_ref replaces')
            c.require(v['operation'] in ('ADD','REPLACE') and v['predicate']=='ALLOWED_TABLES','amendment_kind')
            c.require(bool(b.ids(v['subjects'],12,1)) and set(v['subjects'])<=set(intake.amendment_guests),'amendment_subject')
            c.require(set(b.ids(v['tables'],3,1))<={x['table_id'] for x in current['table_records']},'amendment_tables')
            c.require(v['source_ref']==intake.request_ref,'amendment_source')
            refs=b.ids(v['replaces'],12)
            c.require((not refs) if v['operation']=='ADD' else bool(refs) and set(refs)<=set(added),'replacement_target')
            c.require(not seen.intersection(refs),'duplicate_replacement');seen.update(refs)
            c.require(all(set(added[r]['subjects'])<=set(v['subjects']) for r in refs),'replacement_subject')
            if refs:c.require({g for r in refs for g in added[r]['subjects']}==set(v['subjects']),'replacement_subject_coverage')
        for ref in seen:
            group={r for r,v in added.items() if v['source_ref']==added[ref]['source_ref']}
            c.require(group<=seen,'incomplete_added_requirement_replacement')
    return value

def validate_capture_v01(record,*,intake,role,router=None):
    b.keys(record,'version origin request_ref role model model_version capture_ref source_snapshot schema_sha256 request_body raw_response response_sha256 egress started ended seconds')
    c.require(record['version']==VERSION and record['origin']=='LIVE_ROLE_ORIGIN','live_origin')
    c.require(record['request_ref']==intake.request_ref and record['role']==role,'capture_request_role')
    c.require(type(record['model']) is str and re.fullmatch(r'[A-Za-z0-9_.-]+',record['model']) is not None,'model')
    c.require(type(record['model_version']) is str and bool(record['model_version']),'model_version')
    c.require(record['source_snapshot']==c.digest(intake.current_bytes),'capture_source')
    c.require(record['schema_sha256']==c.digest(schema_v01(role)),'capture_schema')
    c.require(record['response_sha256']==c.digest(record['raw_response'].encode()),'capture_response')
    check_egress_v01(record['request_body'].encode(),record['egress'],intake=intake,role=role,model=record['model'],router=router)
    expected=c.identity('capture',dict(request=c.digest(record['request_body'].encode()),response=record['response_sha256'],
        request_ref=intake.request_ref,role=role,model=record['model'],started=record['started']))
    c.require(record['capture_ref']==expected,'capture_identity')
    c.require(datetime.fromisoformat(record['ended'])>=datetime.fromisoformat(record['started']),'capture_chronology')
    return parse_payload_v01(record['raw_response'],role,intake=intake)

def accepted_material_v01(intake,records,*,origin='LIVE_ROLE_ORIGIN'):
    c.require(origin in ('LIVE_ROLE_ORIGIN','CAPTURED_PROVIDER_RESPONSE_REEXECUTION'),'consumption_origin')
    c.require(len(records)==2,'two_roles')
    o=validate_capture_v01(records[0],intake=intake,role=ROLES[0])
    a=validate_capture_v01(records[1],intake=intake,role=ROLES[1],router=o)
    c.require(o['task_kind']==a['task_kind'],'cross_role_task')
    base,current=intake.check();problem=_problem(intake.current_bytes)
    amendments=a['amendments'];ack=None
    if amendments:
        replaced={r for v in amendments for r in v['replaces']}
        conditions=[v for v in current['hard_conditions'] if v['condition_id'] not in replaced]
        for index,v in enumerate(amendments):
            for guest in v['subjects']:
                conditions.append(dict(condition_id='added:'+c.digest(dict(request=intake.request_ref,index=index,guest=guest))[:32],
                    predicate=v['predicate'],subjects=[guest],tables=v['tables'],source_ref=intake.request_ref,hard=True))
        changed=dict(current,hard_conditions=conditions,problem_revision=current['problem_revision']+1,parent_problem_ref=problem.content_id,
            source_bundle_hash=c.digest(dict(parent=current['source_bundle_hash'],request=intake.request_ref,proposal=amendments,captures=[r['capture_ref'] for r in records])))
        problem=_problem(c.canonical(changed));p=problem.to_plain_v01()
        c.require(all(v in p['hard_conditions'] for v in base['hard_conditions']),'protected_revision')
        ack=dict(mode='SCRIPTED_CONTROLLED_OWNER_INPUT',request_ref=intake.request_ref,prior_problem_ref=_problem(intake.current_bytes).content_id,
            proposed_problem_ref=problem.content_id,amendments=amendments,scope_guests=list(intake.amendment_guests),browser_click_claimed=False)
    semantics=[dict(payload,role=role,capture_ref=r['capture_ref'],model=r['model_version'],origin=origin,
        source_snapshot=r['source_snapshot'],request_ref=intake.request_ref) for payload,role,r in zip((o,a),ROLES,records)]
    profile=a['objective_profile']
    if o['task_kind']=='VALIDATE_EXISTING' and profile is None:
        c.require(intake.prior_output_bytes is not None and intake.prior_result_ref is not None,'prior_objective_required')
        profile=b.parse_json_v01(intake.prior_output_bytes)['profile']
    owner=c.OwnerContextV01(problem.canonical,intake.request_ref,o['task_kind'],profile,intake.safe_intent,intake.prior_result_ref,intake.private_tokens)
    material=dict(problem=problem.to_plain_v01(),profile=owner.profile,task_kind=owner.task_kind,request_ref=owner.request_ref,parent_ref=owner.parent_ref,
        approved_intent=owner.approved_intent,semantics=semantics,projection_status='ACTUAL_SERIALIZED_EGRESS_CHECKED',origin=origin,
        revision_acknowledgement=ack,original_base_ref=_problem(intake.base_bytes).content_id)
    if o['task_kind']=='VALIDATE_EXISTING':
        material['objective_information_source']=dict(kind='ACTUAL_PRIOR_RESULT',result_ref=intake.prior_result_ref,model_selected=a['objective_profile'])
    return owner,material

def execute_live_v01(intake,records,*,now,existing=None,origin='LIVE_ROLE_ORIGIN',journal=lambda *a,**k:None):
    from . import runtime_v01 as r,native_adapter_v01 as n
    owner,material=accepted_material_v01(intake,records,origin=origin)
    if owner.task_kind=='VALIDATE_EXISTING':
        c.require(type(existing) is r.NativeRunV01 and intake.prior_result_ref==existing.evidence['artifact']['artifact_id'],'live_existing_source')
        c.require(intake.prior_output_bytes==c.canonical(existing.output),'live_existing_output')
    ack=material['revision_acknowledgement']
    if ack:
        review=n.root_review(material['problem']['owner_root_id'],'transaction:'+owner.request_ref,c.identity('revision',ack),owner.request_ref,
            dict(protected_law=all(v in material['problem']['hard_conditions'] for v in _problem(intake.base_bytes).to_plain_v01()['hard_conditions']),
                scoped_ack=ack['proposed_problem_ref']==owner.problem().content_id),c.identity('ack',ack),'wedding:revision:input','wedding:revision:review',now,
            predicate='wedding_scripted_revision_acceptance',claim_value=ack)
        material['revision_root']=r.plain(review[2])
    return r._execute_material_v01(owner,material,now=now,existing=existing,journal=journal)

class GeminiProviderV01:
    """Existing configured Gemini SDK, one attempt per explicit call, checked wire."""
    def __init__(self,directory,config_path):
        self.directory=Path(directory);self.directory.mkdir(parents=True,exist_ok=True)
        settings={}
        for node in ast.parse(Path(config_path).read_text()).body:
            if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name) and node.targets[0].id in ('GOOGLE_API_KEY','GEMINI_MODEL'):
                settings[node.targets[0].id]=ast.literal_eval(node.value)
        self.key=next((os.environ[k] for k in ('HEDGEHOG_GEMINI_API_KEY','GOOGLE_API_KEY','GEMINI_API_KEY','GOOGLE_GEMINI_API_KEY') if os.environ.get(k)),settings.get('GOOGLE_API_KEY'))
        self.model=os.environ.get('HEDGEHOG_LIVE_PROVIDER_MODEL') or settings.get('GEMINI_MODEL')
        c.require(bool(self.key) and bool(self.model),'configured_gemini_missing')
        c.require(re.fullmatch(r'[A-Za-z0-9_.-]+',self.model) is not None,'configured_model_shape')

    def capture(self,intake,role,router=None):
        from google import genai
        index=len(list(self.directory.glob('attempt_*')))+1
        c.require(index<=100,'owner_attempt_budget')
        dest=self.directory/f'attempt_{index:03d}';dest.mkdir()
        started=datetime.now(timezone.utc).isoformat();start=time.monotonic()
        receipt=dict(status='STARTED',started=started,model=self.model,role=role,request_ref=intake.request_ref,sdk_retry_attempts=1,wire_sends=0)
        def save_receipt():(dest/'receipt.json').write_bytes(c.canonical(receipt))
        save_receipt();body=request_body_v01(intake,role,router);observed={}
        def before_send(request):
            metadata=dict(method=request.method,scheme=request.url.scheme,host=request.url.host,path=request.url.path,query=request.url.query.decode())
            check_egress_v01(request.content,metadata,intake=intake,role=role,model=self.model,router=router)
            observed.update(raw=request.content,metadata=metadata)
            (dest/'request_body.json').write_bytes(request.content)
            (dest/'destination.json').write_bytes(c.canonical(metadata))
            receipt['wire_sends']+=1;save_receipt()
        try:
            with genai.Client(api_key=self.key,http_options={'timeout':180000,'retry_options':{'attempts':1},
                    'client_args':{'event_hooks':{'request':[before_send]},'follow_redirects':False}}) as client:
                response=client.models.generate_content(model=self.model,contents=body['contents'][0]['parts'][0]['text'],config=dict(
                    temperature=0,candidate_count=1,max_output_tokens=8192,response_mime_type='application/json',response_json_schema=schema_v01(role)))
            raw=response.text or ''
            (dest/'response.txt').write_text(raw)
            # The complete provider object is safe synthetic output, without request authentication.
            (dest/'provider_response.json').write_text(response.model_dump_json())
            ended=datetime.now(timezone.utc).isoformat()
            record=dict(version=VERSION,origin='LIVE_ROLE_ORIGIN',request_ref=intake.request_ref,role=role,model=self.model,
                model_version=response.model_version,capture_ref=c.identity('capture',dict(request=c.digest(observed['raw']),response=c.digest(raw.encode()),
                    request_ref=intake.request_ref,role=role,model=self.model,started=started)),source_snapshot=c.digest(intake.current_bytes),
                schema_sha256=c.digest(schema_v01(role)),request_body=observed['raw'].decode(),raw_response=raw,response_sha256=c.digest(raw.encode()),
                egress=observed['metadata'],started=started,ended=ended,seconds=time.monotonic()-start)
            (dest/'capture.json').write_bytes(c.canonical(record))
            validate_capture_v01(record,intake=intake,role=role,router=router)
            receipt.update(status='VALIDATED',capture_ref=record['capture_ref'],model_version=response.model_version)
            return record
        except Exception as error:
            receipt.update(status='FAILED',error_type=type(error).__name__)
            if isinstance(error,b.WeddingContractError):receipt['reason']=str(error)
            raise
        finally:
            receipt.update(ended=datetime.now(timezone.utc).isoformat(),seconds=time.monotonic()-start);save_receipt()
