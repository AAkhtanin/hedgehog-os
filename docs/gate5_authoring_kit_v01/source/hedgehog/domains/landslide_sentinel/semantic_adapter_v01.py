"""Untrusted diagnostic meanings, locally bound to exact input evidence."""
import ast
import json
import os
from pathlib import Path
import time
from hedgehog.kernel import semantic_work_v01 as sw, trust_model_v01 as trust
from . import contracts_v01 as c

RESPONSE_SCHEMA = dict(type='object', additionalProperties=False, required=['diagnostic','source_refs','reason'],
    properties=dict(diagnostic=dict(type='string',enum=list(c.DIAGNOSTICS)),
        source_refs=dict(type='array',minItems=1,items=dict(type='string')),reason=dict(type='string',minLength=1,maxLength=512)))


def context(frames, note, *, intended_role=None, capabilities=None, observations=(), tick=None, policy=None):
    frames=[c.measurement(v) for v in frames]
    if intended_role is not None and type(note) is dict:
        from .events_v01 import SITE
        c.require(note.get('site')==SITE and type(note.get('observed_at')) is int and type(note.get('received_at')) is int
            and note['observed_at']<=note['received_at']<=tick,'semantic_note_site_time')
    channels={'LOCAL_SLOPE_ANALYST':('displacement','reserve'),'CLOUD_ENVIRONMENTAL_ANALYST':('rainfall',),
              'ADVERSARIAL_SENSOR_REVIEWER':('displacement','reserve')}
    if intended_role is not None:
        c.require(intended_role in channels,'semantic_duty')
        frames=[v for v in frames if v['sensor'] in channels[intended_role]]
    sources={c.identity('measurement',v):v for v in frames}
    if intended_role!='CLOUD_ENVIRONMENTAL_ANALYST':sources[c.identity('maintenance_note',note)]=dict(note=note)
    for row in observations:
        if intended_role is None or row['channel'] in channels[intended_role]:sources[row['observation_id']]=row
    choices=(('TEMPORAL_CONTEXT_APPLICABILITY','SPATIAL_CONTEXT_APPLICABILITY','EVIDENCE_GAPS')
        if intended_role=='CLOUD_ENVIRONMENTAL_ANALYST' else
        ('REFERENCE_INTEGRITY','INDEPENDENT_RESERVE_SERIES','EVIDENCE_GAPS') if intended_role is not None else c.DIAGNOSTICS)
    result=dict(sources=sources, allowed_diagnostics=list(choices),policy=dict(c.POLICY if policy is None else c.validate_policy(policy)),
        instruction='Choose the next bounded investigation that usefully resolves the remaining evidenced uncertainty. '
            'Compare the available questions and their evidence limits. A plan is not authority. Do not change policy or certify physical facts from unsupported notes.')
    if intended_role is not None:
        result.update(duty=intended_role,capabilities=capabilities,scenario_tick=tick,
            not_included_channels=sorted(set(('rainfall','displacement','reserve'))-set(channels[intended_role])),
            operations={key:c.DIAGNOSTIC_CATALOGUE[key] for key in choices},
            investigation_contract_version=c.INVESTIGATION_VERSION,
            investigations={key:c.investigation(key,intended_role) for key in choices},
            context_provenance='SYNTHETIC_SITE_CONTEXT_NOT_REAL_EA_OR_PHYSICAL_SENSOR')
    return result


def validate_response(value, supplied):
    c.require(type(value) is dict and set(value)=={'diagnostic','source_refs','reason'}, 'semantic_shape')
    c.require(value['diagnostic'] in c.DIAGNOSTICS and value['diagnostic'] in supplied['allowed_diagnostics'], 'semantic_diagnostic')
    refs=value['source_refs']
    c.require(type(refs) is list and bool(refs) and len(set(refs))==len(refs)
        and all(type(v) is str and v in supplied['sources'] for v in refs), 'semantic_source_binding')
    c.require(type(value['reason']) is str and 0<len(value['reason'])<=512, 'semantic_reason')
    return json.loads(c.canonical(value))


class GeminiHarness:
    """Authorized harness transport; never a site-cloud or physical local SLM."""
    def __init__(self, directory, config_path=None):
        self.directory=Path(directory);self.directory.mkdir(parents=True,exist_ok=True)
        settings={}
        if config_path:
            for node in ast.parse(Path(config_path).read_text()).body:
                if isinstance(node,ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0],ast.Name):
                    if node.targets[0].id in ('GOOGLE_API_KEY','GEMINI_MODEL'):
                        settings[node.targets[0].id]=ast.literal_eval(node.value)
        self.key=next((os.environ[k] for k in ('HEDGEHOG_GEMINI_API_KEY','GOOGLE_API_KEY','GEMINI_API_KEY','GOOGLE_GEMINI_API_KEY') if os.environ.get(k)),settings.get('GOOGLE_API_KEY'))
        self.model=os.environ.get('HEDGEHOG_LIVE_PROVIDER_MODEL') or settings.get('GEMINI_MODEL')
        self.available=True;self.calls=0;self.attempts=[]

    def respond(self, supplied):
        c.require(self.available, 'harness_emulator_unavailable')
        c.require(bool(self.key) and bool(self.model), 'configured_gemini_missing')
        from google import genai
        self.calls+=1
        attempt=dict(ordinal=self.calls,provider='Gemini',model=self.model,context_sha256=c.digest(supplied),
            classification='AUTHORIZED_ANALYST_NETWORK',intended_role=supplied.get('duty','LOCAL_SLM'),actual_mode='CLOUD_LLM',
            sdk_attempts=1,status='STARTED')
        dest=self.directory/f'attempt_{self.calls:03d}';dest.mkdir()
        response_schema=json.loads(c.canonical(RESPONSE_SCHEMA))
        response_schema['properties']['diagnostic']['enum']=supplied['allowed_diagnostics']
        response_schema['properties']['source_refs']['items']['enum']=list(supplied['sources'])
        generation=dict(response_mime_type='application/json',response_json_schema=response_schema,
            temperature=0,candidate_count=1,max_output_tokens=8192)
        (dest/'request.json').write_bytes(c.canonical(dict(context=supplied,response_schema=response_schema,attempt=attempt,generation=generation)))
        start=time.monotonic()
        try:
            client=genai.Client(api_key=self.key,http_options={'timeout':180000,'retry_options':{'attempts':1}})
            try:
                result=client.models.generate_content(model=self.model,contents=c.canonical(supplied).decode(),
                    config=generation)
            finally:
                client.close()
            raw=result.text or ''
            (dest/'response.txt').write_text(raw)
            attempt['model_version']=getattr(result,'model_version',None)
            attempt['finish_reasons']=[str(v.finish_reason) for v in result.candidates or ()]
            usage=getattr(result,'usage_metadata',None)
            attempt['usage']=None if usage is None else usage.model_dump(mode='json')
            value=validate_response(json.loads(raw),supplied)
            attempt['status']='VALIDATED'
            return value
        except Exception as error:
            attempt.update(status='FAILED',error_type=type(error).__name__)
            raise
        finally:
            attempt['seconds']=time.monotonic()-start;self.attempts.append(attempt)
            (dest/'receipt.json').write_bytes(c.canonical(attempt))


def collect(frames, note, root, now, *, harness=None, controlled=None, intended_role=None,
            capabilities=None, observations=(), tick=None,policy=None):
    supplied=context(frames,note,intended_role=intended_role,capabilities=capabilities,observations=observations,tick=tick,policy=policy)
    if controlled is not None:
        c.require(type(controlled) is dict and set(controlled)=={'diagnostic','reason'},'controlled_response_shape')
        c.require(harness is None and intended_role in ('LOCAL_SLOPE_ANALYST','CLOUD_ENVIRONMENTAL_ANALYST','ADVERSARIAL_SENSOR_REVIEWER'),'controlled_role')
        value=dict(diagnostic=controlled['diagnostic'],reason=controlled['reason'],source_refs=list(supplied['sources']))
        mode,role,profile='DETERMINISTIC','deterministic_runtime','CONTROLLED_ROLE_FIXTURE'
    elif harness is None:
        value=dict(diagnostic='REFERENCE_INTEGRITY',source_refs=list(supplied['sources']),reason='Local reference integrity check.')
        mode,role,profile='DETERMINISTIC','deterministic_runtime','LOCAL_ALGORITHMS_ONLY'
    else:
        if capabilities is not None:
            c.require(capabilities['harness_transport_available'],'semantic_harness_unavailable')
            if intended_role=='CLOUD_ENVIRONMENTAL_ANALYST':c.require(capabilities['site_cloud_available'],'environmental_context_offline')
        value=harness.respond(supplied)
        mode,role,profile='CLOUD_LLM','provider_llm','EMULATED_LOCAL_SLM'
    return bind(frames,supplied,value,root,now,mode,role,profile,intended_role)


def bind(frames,supplied,value,root,now,mode,role,profile,intended_role):
    value=validate_response(value,supplied)
    ref=c.identity('semantic_context',supplied);actor='sentinel:internal_analyst'
    request=sw.build_semantic_work_request_v01(request_id='request:'+ref,transaction_id='transaction:'+ref,
        target_root_id=root,runtime_topology_ref='sentinel:bounded_diagnostic',bounded_context_refs=(ref,),
        permitted_actor_ids=(actor,),permitted_contribution_modes=(mode,),requested_subjects=('sentinel:diagnostic',),
        required_evidence_classes=('DEPENDENCY_EVIDENCE',),forbidden_claims=('authority_creation',))
    evidence=sw.build_evidence_binding_v01(evidence_id='evidence:'+ref,evidence_ref=ref,evidence_class='DEPENDENCY_EVIDENCE',
        source_component_id=actor,provenance_ref='sentinel:local_capture:'+c.digest(value),evidence_state='PRESENT')
    claim=sw.build_normalized_claim_v01(claim_id=c.identity('claim',value),subject='sentinel:diagnostic',predicate='proposed_diagnostic',
        object_or_value=value,time_envelope_ref='sentinel:time:'+str(now),provenance_refs=(ref,),evidence_refs=(evidence.evidence_id,),
        confidence_micros=500000,source_role=role,source_mode=mode)
    contribution=sw.build_actor_contribution_v01(contribution_id=c.identity('contribution',dict(context=ref,value=value,mode=mode)),
        request_id=request.request_id,actor_id=actor,actor_role=role,contribution_mode=mode,bsep_projection_ref='bsep:'+ref,
        scope='sentinel:diagnostic',bounded_context_refs=(ref,),claims=(claim,),evidence_bindings=(evidence,),
        constraint_bindings=(),uncertainty_bindings=(),requested_validators=('diagnostic_catalogue','source_binding'),forbidden_claims_observed=())
    profiles=trust.build_default_component_trust_profiles_v01()
    errors=sw.validate_actor_contribution_v01(request=request,contribution=contribution,trust_profiles=profiles)
    c.require(not errors, 'actual_semantic_validation:'+repr(errors))
    packet=sw.build_root_review_packet_from_contributions_v01(request=request,contributions=(contribution,),trust_profiles=profiles)
    snapshot=supplied.get('capabilities') or dict(site_cloud_available=False,remote_rainfall_available=False,harness_transport_available=mode=='CLOUD_LLM')
    return dict(selection=value['diagnostic'],frames=frames,contract=dict(supplied['policy'])),dict(profile=profile,
        intended_role=intended_role or ('LOCAL_SLM' if mode=='CLOUD_LLM' else 'LOCAL_ALGORITHM'),actual_mode=mode,actor_role=role,
        evaluated_at=now,site_cloud_available=snapshot['site_cloud_available'],remote_rainfall_available=snapshot['remote_rainfall_available'],
        harness_transport_available=snapshot['harness_transport_available'],capability_snapshot=snapshot,
        request=sw.semantic_work_to_plain_dict_v01(request),contribution=sw.semantic_work_to_plain_dict_v01(contribution),
        review_packet=sw.semantic_work_to_plain_dict_v01(packet),context=supplied,response=value)


def validate_bound(value):
    """Rebuild through public semantic validators without performing a provider call."""
    _,expected=bind([],value['context'],value['response'],value['request']['target_root_id'],value['evaluated_at'],
        value['actual_mode'],value['actor_role'],value['profile'],value['context'].get('duty'))
    c.require(expected==value,'semantic_capture_content_binding')
    return value


def validate_material(material):
    semantics=material['semantic_bindings'];checks=material['checks']
    phase=material.get('phase')
    c.require(phase in ('PLAN','RESULT'),'semantic_work_phase')
    c.require(set(material)=={'selection','frames','contract','semantic_bindings','checks','phase'} |
        ({'accepted_plan'} if phase=='RESULT' else set()),'semantic_work_shape')
    c.require(bool(semantics) and len(semantics)==len(checks),'semantic_composition_inventory')
    c.require(material['selection']==checks[0]['selection'],'semantic_primary_selection')
    c.require(len({v['contribution']['contribution_id'] for v in semantics})==len(semantics),'semantic_duplicate_contribution')
    for value,row in zip(semantics,checks,strict=True):
        validate_bound(value)
        from .events_v01 import SITE
        current=value['context'].get('investigation_contract_version')
        c.require(current in (None,c.INVESTIGATION_VERSION),'investigation_contract_version')
        c.require(set(row)=={'selection','semantic_ref','tick','site','observations','series'} |
            ({'investigation'} if current else set()) and row['site']==SITE,
            'semantic_check_site_shape')
        c.require(row['semantic_ref']==value['contribution']['contribution_id'] and
            row['selection']==value['response']['diagnostic'],'semantic_selected_input')
        context=value['context']
        if current:
            expected_specs={key:c.investigation(key,context['duty']) for key in context['allowed_diagnostics']}
            c.require(context['investigations']==expected_specs,'semantic_investigation_catalogue')
            c.require(row['investigation']==expected_specs[row['selection']],'semantic_investigation_binding')
        c.require(context['policy']==material['contract'],'semantic_work_policy')
        c.require(row['tick']==context['scenario_tick'],'semantic_work_time')
        expected=sorted((v for v in context['sources'].values() if 'observation_id' in v),key=lambda v:v['observation_id'])
        c.require(row['observations']==expected,'semantic_work_source_mix')
        if material.get('phase')=='PLAN':c.require(row['series'] is None,'plan_material_must_not_acquire')
        if material.get('phase')=='RESULT':
            c.require(type(material.get('accepted_plan')) is dict and bool(material['accepted_plan']['work_artifact_ref']),
                'diagnostic_result_requires_plan')
    return material


def validate_current(material,session,*,check_plan=True):
    validate_material(material)
    c.require(material['frames']==session.frames,'semantic_current_frames')
    for value in material['semantic_bindings']:
        ctx=value['context'];duty=ctx['duty']
        c.require(value['request']['target_root_id']==session.root,'semantic_foreign_root')
        c.require(ctx['policy']==session.contract,'semantic_stale_policy')
        c.require(ctx['scenario_tick']==session.tick and ctx['capabilities']==session.capabilities.snapshot(duty),'semantic_stale_capability_or_tick')
        for row in ctx['sources'].values():
            if 'observation_id' in row:
                c.require(session.book.latest.get(row['channel'])==row,'semantic_stale_observation')
                if duty!='CLOUD_ENVIRONMENTAL_ANALYST':
                    c.require(0<=session.tick-row['observed_end']<=session.contract['max_local_age_seconds'],'semantic_stale_local_measurement')
            elif 'sensor' in row:c.require(row in session.frames,'semantic_compatibility_projection')
    if material.get('phase')=='RESULT' and check_plan:
        from . import kernel_adapter_v01 as k
        from hedgehog.kernel import abi_v01 as abi,effect_firewall_v01 as fw
        plan=material['accepted_plan'];basis=getattr(session,'accepted_plans',{}).get(plan['work_artifact_ref'])
        k.validate_reviewed_work(session,basis)
        c.require(k.reviewed_work_refs(basis)==plan,'current_accepted_plan_binding')
        planned=json.loads(basis.material)
        c.require(planned['semantic_bindings']==material['semantic_bindings'],'result_plan_semantic_binding')
        for row in material['checks']:
            if row['selection']!='INDEPENDENT_RESERVE_SERIES':continue
            series=row['series'];c.require(type(series) is dict,'series_actual_output_required')
            contexts=[v for v in session.host.registry.action_packet_fulfillment_attempt_contexts if v.receipt is not None
                and v.receipt.artifact_id==series['receipt_ref']]
            c.require(len(contexts)==1 and abi.kernel_artifact_to_plain_dict_v01(contexts[0].receipt)==series['receipt'],
                'series_host_receipt_binding')
            execution=fw.native_execution_evidence_from_plain_data_v01(series['receipt']['payload']['execution_evidence'])
            from .capability_registry_v01 import values
            actual=json.loads(values(execution.result.output)['material'])
            c.require(actual['records']==series['records'] and actual['invocation_id']==series['invocation_id'],
                'series_receipt_output_binding')
            storage_key=c.identity('series_use',dict(semantic=row['semantic_ref'],dependencies=k.work_dependencies(session).decode()))
            stored=getattr(session,'series_materials',{}).get(storage_key)
            c.require(stored is not None and stored['canonical']==c.canonical(series) and stored['dependencies']==k.work_dependencies(session),
                'series_current_source_binding')
    return material
