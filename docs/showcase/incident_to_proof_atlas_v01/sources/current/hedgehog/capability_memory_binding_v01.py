"""Need-based local semantic search; records never confer code/action authority."""
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
import base64
import hashlib
import json
from pathlib import Path
from hedgehog import capability_admission_v01 as pure
from hedgehog import local_drs_resolver as resolver
from hedgehog import drs_semantic_address_v01 as address
from hedgehog import drs_memory_resolution_v01 as resolution
from hedgehog import work_execution_host_v01 as hosts
from hedgehog.kernel import root_decision_v01 as root
from hedgehog.kernel import semantic_work_v01 as semantic
from hedgehog.kernel import trust_model_v01 as trust
from hedgehog.kernel import integrity_replay_v01 as integrity
from hedgehog.drs import LocalDRS


@dataclass(frozen=True)
class PureNeedSearchV01:
    need: pure.PureCapabilityNeedV01
    query: resolver.SemanticResolveQuery
    result: resolver.ResolvedDRSReport
    _origin: object = field(default=None,repr=False,compare=False)


class _SearchOrigin:
    def __init__(self,host,digest):
        self.host,self.digest,self.search=host,digest,None


def _utc(value):
    return datetime.fromtimestamp(value,timezone.utc).isoformat()


def _search_digest(query,result):
    return _hash(_json(dict(query=asdict(query),result=asdict(result))))


def search_pure_need_v01(store, *, host, need, as_of=None):
    pure.validate_pure_need_v01(need)
    if type(store) is not LocalDRS:
        raise ValueError('pure_local_store_type')
    p = need.permission
    current=_utc(host.current_sources.evaluation_time)
    if as_of is not None and as_of!=current:raise ValueError('pure_memory_current_time')
    as_of=current
    files=tuple(store.root_path.glob('work/*.json'))
    if any(f.is_symlink() or not f.is_file() for f in files):
        raise ValueError('pure_store_file_type')
    read_bytes=sum(f.stat().st_size for f in files)
    hosts.reserve_pure_need_work_v01(host,need=need,kind='drs',byte_count=read_bytes,
        expected_revision=host.state_revision)
    filters = dict(contract_version=p.contract_version, multiplier=p.multiplier, offset=p.offset,
        memory_scope=p.memory_scope, owning_root_id=p.owning_root_id, profile_version=p.profile_version)
    query = resolver.SemanticResolveQuery(query_id=pure.pure_evidence_identity_v01('pure_search',
        dict(task=p.task_id,filters=filters,as_of=as_of)), domain='pure_integer',
        semantic_terms=('integer','affine','u8'), content_filters=filters,
        temporal_query=dict(as_of=as_of),max_candidates=4,require_root_review=True)
    result=resolver.resolve_semantic_candidates(store,query,layers=('work',))
    hosts._record_pure_drs_bytes_v01(host,p.task_id,read_bytes)
    origin=_SearchOrigin(host,_search_digest(query,result))
    search=PureNeedSearchV01(need,query,result,origin)
    origin.search=search
    return search


def validate_pure_search_v01(value, *, host):
    _require(type(value) is PureNeedSearchV01 and type(value._origin) is _SearchOrigin
        and value._origin.host is host and value._origin.search is value,'pure_search_not_observed')
    pure.validate_pure_need_v01(value.need)
    _require(_search_digest(value.query,value.result)==value._origin.digest,'pure_search_observed_content')
    p=value.need.permission
    _require(value.query.content_filters==dict(contract_version=p.contract_version,multiplier=p.multiplier,offset=p.offset,
        memory_scope=p.memory_scope,owning_root_id=p.owning_root_id,profile_version=p.profile_version)
        and value.query.temporal_query==dict(as_of=_utc(host.current_sources.evaluation_time))
        and value.query.require_root_review and value.result.root_review_required
        and value.result.direct_reuse_allowed_count==0
        and all(not c.action_permission_granted and not c.direct_reuse_allowed for c in value.result.candidates),
        'pure_search_need_and_non_authority')
    return True


@dataclass(frozen=True)
class PureMemoryRecordV01:
    record: dict
    meaning: address.MeaningRecordV01
    payload: bytes
    root_kernel: root.RootDecisionKernelV01
    root_input: root.RootDecisionInputV01
    root_result: root.RootDecisionResultV01


@dataclass(frozen=True)
class PureMemoryRetrievalV01:
    search: PureNeedSearchV01
    record: dict
    meaning: address.MeaningRecordV01
    query: resolution.DRSTemporalQueryV01
    evaluation: resolution.QueryEvaluationStateV01
    ranked: tuple
    plan: resolution.RetrievalPlanV01
    budget: resolution.MemoryDescentBudgetV01
    request: resolution.MemoryDescentRequestV01
    root_kernel: root.RootDecisionKernelV01
    root_input: root.RootDecisionInputV01
    root_result: root.RootDecisionResultV01
    descent: resolution.MemoryDescentResultV01
    payload: bytes
    attempt: pure.PureAdmissionAttemptV01
    package: pure.AdmittedPurePackageV01


def _require(ok, reason):
    if not ok:raise ValueError(reason)


def _json(value):
    return json.dumps(value,sort_keys=True,separators=(',',':')).encode()


def _hash(value):
    return hashlib.sha256(value).hexdigest()


def _root_hash(value):
    return integrity.domain_separated_sha256_hex_v01(domain='hedgehog:drs:memory_descent_root_result_binding:v01',
        payload=integrity.canonical_json_bytes_v01(root.root_decision_result_to_plain_dict_v01(value)))


def _source_payload(payload,need):
    def unique(pairs):
        result={}
        for k,v in pairs:
            _require(k not in result,'pure_memory_duplicate_key')
            result[k]=v
        return result
    data=json.loads(payload,object_pairs_hook=unique)
    _require(type(data) is dict and set(data)=={'contract_version','multiplier','offset','profile_version','wasm','wat',
        'wasm_sha256','oracle_sha256','engine_version','configuration_sha256','generation_mode','source_freeze'},'pure_memory_payload_shape')
    p=need.permission
    _require((data['contract_version'],data['multiplier'],data['offset'],data['profile_version'],data['engine_version'])==
        (p.contract_version,p.multiplier,p.offset,p.profile_version,pure.worker.ENGINE_VERSION)
        and type(data['multiplier']) is int and type(data['offset']) is int,'pure_memory_contract_binding')
    _require(data['configuration_sha256']==pure.worker._config_digest()
        and data['oracle_sha256']==_hash(_json(pure.pure_need_oracle_v01(need)))
        and data['generation_mode']=='CONTROLLED_DETERMINISTIC'
        and type(data['wat']) is str and 0<len(data['wat'].encode())<=pure.worker.MAX_BYTES
        and data['source_freeze']==[list(v) for v in pure.pure_source_freeze_v01()],'pure_memory_source_profile')
    wasm=base64.b64decode(data['wasm'],validate=True)
    _require(0<len(wasm)<=pure.worker.MAX_BYTES and _hash(wasm)==data['wasm_sha256'],'pure_memory_guest_hash')
    return data,wasm


def review_pure_memory_v01(*, need, transaction_id, selected_id, subject, predicate, claim_value, validation):
    """Actual local Root decision after the caller's designated public check."""
    pure.validate_pure_need_v01(need)
    _require(validation is True,'pure_memory_validation_required')
    label=pure.pure_evidence_identity_v01('memory_review',dict(task=need.permission.task_id,selected=selected_id))
    request=semantic.build_semantic_work_request_v01(request_id='request:'+label,transaction_id=transaction_id,
        target_root_id=need.permission.owning_root_id,runtime_topology_ref=need.topology_id,
        bounded_context_refs=(need.need_id,),permitted_actor_ids=('actor:pure_memory',),
        permitted_contribution_modes=('DETERMINISTIC',),requested_subjects=(subject,),
        required_evidence_classes=('ROOT_BINDING',),forbidden_claims=('create_permission',))
    evidence=semantic.build_evidence_binding_v01(evidence_id='evidence:'+label,evidence_ref=selected_id,
        evidence_class='ROOT_BINDING',source_component_id='actor:pure_memory',provenance_ref=need.observation_id,
        evidence_state=semantic.EVIDENCE_STATE_PRESENT)
    claim=semantic.build_normalized_claim_v01(claim_id=selected_id,subject=subject,predicate=predicate,
        object_or_value=claim_value,time_envelope_ref='time:pure_memory',provenance_refs=(need.observation_id,),
        evidence_refs=(evidence.evidence_id,),confidence_micros=1000000,source_role='deterministic_runtime',source_mode='DETERMINISTIC')
    contribution=semantic.build_actor_contribution_v01(contribution_id='contribution:'+label,request_id=request.request_id,
        actor_id='actor:pure_memory',actor_role='deterministic_runtime',contribution_mode='DETERMINISTIC',
        bsep_projection_ref=need.permission.source_ref,scope=subject,bounded_context_refs=(need.need_id,),
        claims=(claim,),evidence_bindings=(evidence,),constraint_bindings=(),uncertainty_bindings=(),
        requested_validators=(),forbidden_claims_observed=())
    packet=semantic.build_root_review_packet_from_contributions_v01(request=request,contributions=(contribution,),
        trust_profiles=trust.build_default_component_trust_profiles_v01())
    kernel=root.build_root_decision_kernel_v01()
    decision_input=root.build_root_decision_input_v01(transaction_id=transaction_id,target_root_id=need.permission.owning_root_id,
        root_review_packet=packet,
        post_vv_bundle=dict(bundle_id='postvv:'+label,post_vv_passed=validation,validated_candidate_ids=[selected_id],
            rejected_candidate_ids=[],required_evidence_refs=[],provided_evidence_refs=[],hard_failure_reasons=[]),
        gt_advisory=dict(advisory_id='gt:'+label,candidate_ids=[selected_id],selected_candidate_id=selected_id,
            score_micros_by_candidate={selected_id:500000},source_artifact_type='GTAdvisoryReport',source_lifecycle_state='VALIDATED',
            actor_role='gt',attempted_effect='CREATE_ROOT_DECISION',target_artifact_type='RootDecision',advisory_only=True,
            creates_final_output=False,requests_effect=False),
        policy_state=dict(policy_id=need.permission.memory_scope,identity_passed=validation,scope_passed=validation,
            hard_policy_passed=validation,allow_accept=validation,conflict_policy='DEFER',no_candidate_policy='NO_UPDATE'),
        permission_state=dict(permission_required=False,user_permission_present=False,permission_scope_valid=True,permission_ref=None),
        temporal_state=dict(temporal_valid=True,expired=False,not_before_satisfied=True,time_envelope_ref='time:pure_memory'),
        conflict_state=dict(material_unresolved_conflict=False,conflict_set_ids=[]),
        prior_root_state=dict(prior_decision_id=None,prior_decision=None,prior_selected_candidate_id=None))
    result=root.decide_root_v01(kernel=kernel,decision_input=decision_input)
    _require(not root.validate_root_decision_result_v01(kernel=kernel,decision_input=decision_input,result=result)
        and result.decision=='ACCEPT','pure_memory_root_refused')
    return kernel,decision_input,result


def _address():
    return address.build_semantic_address_v01(namespace='local_pure',domain='pure_integer',subject_class='affine_u8',
        intent_class='context_lookup',meaning_schema_id='pure_source',meaning_schema_version='v01')


def _scope(permission):
    return _hash(_json(dict(root=permission.owning_root_id,memory=permission.memory_scope,
        contract=permission.contract_version,multiplier=permission.multiplier,offset=permission.offset)))


def write_pure_memory_v01(store, *, host, package, proposal):
    valid=pure.validate_admitted_pure_package_v01(package,host=host,need=package.need)
    _require(type(proposal) is pure.PureCodeProposalV01 and proposal in host.pure_generation_proposals
        and proposal.need==package.need and proposal.wat==package.attempt.source,'pure_memory_proposal_binding')
    p=package.need.permission
    payload=_json(dict(contract_version=p.contract_version,multiplier=p.multiplier,offset=p.offset,
        profile_version=p.profile_version,wasm=base64.b64encode(package.wasm).decode(),
        wat=proposal.wat.decode(),wasm_sha256=package.wasm_sha256,oracle_sha256=package.oracle_sha256,
        engine_version=package.attempt.worker_result.engine_version,
        configuration_sha256=package.attempt.worker_result.configuration_sha256,
        generation_mode='CONTROLLED_DETERMINISTIC',source_freeze=proposal.source_freeze))
    a=_address()
    kernel,decision_input,result=review_pure_memory_v01(need=package.need,transaction_id=p.task_id,
        selected_id=package.package_id,subject=a.semantic_address_id,predicate='record_validated_pure_source_v01',
        claim_value=dict(payload_sha256=_hash(payload),memory_scope=p.memory_scope),validation=valid)
    pointer=address.build_artifact_pointer_v01(storage_class='LOCAL_DOCUMENT',object_reference='artifact:pure_affine_source_v01',
        content_sha256=_hash(payload),media_type='application/json',byte_length=len(payload),access_policy_id=p.memory_scope,
        sensitivity_class='INTERNAL',allowed_use_classes=('OPEN_ONE_ARTIFACT',),forbidden_use_classes=('ACTION_EXECUTION',),
        summary_read_permitted=True,payload_read_permitted=True)
    time=address.build_drs_time_envelope_v01(pt_created_at=1000,kt_as_of=1000,et_observed_at=1000,ct_context_anchor=1000,
        ttl_seconds=1000,valid_from=1000,valid_to=2000,source_observed_at=1000,source_reported_at=1000,
        system_ingested_at=1000,system_verified_at=1000,freshness_policy_id='pure_fresh_v01')
    authority=address.build_drs_authority_envelope_v01(authority_class='ROOT_ACCEPTED_CONTEXT',owning_local_root_id=p.owning_root_id,
        source_root_decision_input_id=decision_input.decision_input_id,source_root_decision_id=result.decision_id,
        source_root_decision_hash=_root_hash(result),authority_scope_fingerprint=_scope(p),root_acceptance_state='ACCEPTED_CONTEXT',
        recording_component='pure_memory')
    meaning=address.build_meaning_record_v01(semantic_address=a,predecessor_record_id=None,supersession_reason=None,
        safe_summary='Finite integer affine source; independent readmission required.',semantic_tags=('integer','affine','u8'),
        resonance_reason='same mathematical need',memory_pointers=(),artifact_pointers=(pointer,),
        source_reference_ids=(pointer.pointer_id,),lineage_edges=(),time_envelope=time,authority_envelope=authority,
        persistent_lifecycle_state='ACTIVE',risk_hints=(),conflict_hints=(),reuse_policy_class='CONTEXT_ONLY',policy_version='pure_memory_v01',
        schema_versions=('pure_source_v01',),content_fingerprint=_hash(payload),recording_component='pure_memory')
    content=dict(contract_version=p.contract_version,multiplier=p.multiplier,offset=p.offset,memory_scope=p.memory_scope,
        owning_root_id=p.owning_root_id,profile_version=p.profile_version,meaning=address.meaning_record_to_plain_data_v01(meaning),
        payload_ref=pointer.object_reference,payload_sha256=pointer.content_sha256)
    hosts.reserve_pure_need_work_v01(host,need=package.need,kind='drs',byte_count=len(payload)+len(_json(content))+4096,
        expected_revision=host.state_revision)
    payload_dir=store.root_path/'pure_payloads'
    payload_dir.mkdir(parents=True,exist_ok=True)
    with (payload_dir/(pointer.content_sha256+'.json')).open('xb') as f:f.write(payload)
    hosts._record_pure_drs_bytes_v01(host,p.task_id,len(payload))
    record=resolver.write_semantic_record(store,resolver.SemanticDRSRecordInput(record_id=meaning.meaning_record_id,domain='pure_integer',
        content=content,semantic_keys=('integer','affine','u8'),record_type='pure_source',
        time_envelope=dict(pt_created_at=_utc(1000),kt_asof=_utc(1000),
            ttl_seconds=1000,valid_from=_utc(1000),valid_to=_utc(2000)),
        provenance=dict(request_id=p.task_id,created_by='pure_memory'),
        source_refs=({'ref':package.need.observation_id},)))
    hosts._record_pure_drs_bytes_v01(host,p.task_id,len(json.dumps(record,indent=2,sort_keys=True).encode()))
    return PureMemoryRecordV01(record,meaning,payload,kernel,decision_input,result)


def _meaning_from_record(record):
    m=record['content']['meaning']
    def kwargs(value,names):return {n:value[n] for n in names.split()}
    a=address.build_semantic_address_v01(**kwargs(m['semantic_address'],
        'namespace domain subject_class intent_class meaning_schema_id meaning_schema_version'))
    pointers=tuple(address.build_artifact_pointer_v01(**{**kwargs(p,
        'storage_class object_reference content_sha256 media_type byte_length access_policy_id sensitivity_class summary_read_permitted payload_read_permitted'),
        'allowed_use_classes':tuple(p['allowed_use_classes']),'forbidden_use_classes':tuple(p['forbidden_use_classes'])}) for p in m['artifact_pointers'])
    time=address.build_drs_time_envelope_v01(**kwargs(m['time_envelope'],
        'pt_created_at kt_as_of et_observed_at ct_context_anchor ttl_seconds valid_from valid_to source_observed_at source_reported_at system_ingested_at system_verified_at freshness_policy_id'))
    authority=address.build_drs_authority_envelope_v01(**kwargs(m['authority_envelope'],
        'authority_class owning_local_root_id source_root_decision_input_id source_root_decision_id source_root_decision_hash authority_scope_fingerprint root_acceptance_state recording_component'))
    meaning=address.build_meaning_record_v01(**kwargs(m,
        'predecessor_record_id supersession_reason safe_summary resonance_reason persistent_lifecycle_state reuse_policy_class policy_version content_fingerprint recording_component'),
        semantic_address=a,artifact_pointers=pointers,memory_pointers=(),lineage_edges=(),time_envelope=time,authority_envelope=authority,
        **{n:tuple(m[n]) for n in ('semantic_tags','source_reference_ids','risk_hints','conflict_hints','schema_versions')})
    _require(address.meaning_record_to_plain_data_v01(meaning)==m and record['record_id']==meaning.meaning_record_id,
        'pure_memory_record_shape_or_identity')
    return meaning


def retrieve_pure_memory_v01(store, *, host, need, as_of=None, evaluation_time=None):
    current=host.current_sources.evaluation_time
    _require(evaluation_time is None or type(evaluation_time) is int and evaluation_time==current,'pure_memory_current_time')
    evaluation_time=current
    search=search_pure_need_v01(store,host=host,need=need,as_of=as_of)
    candidates=[c for c in search.result.candidates if not c.blocked and not c.stale]
    _require(len(candidates)==1,'pure_memory_no_unique_candidate')
    files=tuple(store.root_path.glob('work/*.json'))
    _require(all(f.is_file() and not f.is_symlink() for f in files),'pure_store_file_type')
    hosts.reserve_pure_need_work_v01(host,need=need,kind='drs',byte_count=sum(f.stat().st_size for f in files),
        expected_revision=host.state_revision)
    record=store.read_record('work',candidates[0].record_id)
    hosts._record_pure_drs_bytes_v01(host,need.permission.task_id,len(json.dumps(record,indent=2,sort_keys=True).encode()))
    meaning=_meaning_from_record(record)
    p=need.permission
    query=resolution.build_drs_temporal_query_v01(query_mode='CURRENT_DECISION',semantic_address_id=meaning.semantic_address.semantic_address_id,
        scope_fingerprint=_scope(p),as_of=evaluation_time,evaluation_time=evaluation_time,
        evaluation_time_source='INJECTED_CURRENT_DECISION_TIME',time_range_start=1000,time_range_end=3000,
        required_time_axes=('PT','KT','ET','CT','TTL','VALIDITY'),freshness_policy_id='pure_fresh_v01',max_age_seconds=1000,
        domain='pure_integer',risk_class='LOW',reuse_intent='CONTEXT',requested_reuse_classes=('CONTEXT_ONLY',),
        required_evidence_classes=('SOURCE_IDENTITY','SOURCE_INTEGRITY','PROVENANCE_CHAIN','TIME_FITNESS','ROOT_DECISION'),
        forbidden_changes=('POLICY_CHANGED',),policy_version='pure_memory_v01',schema_versions=('pure_source_v01',),owning_local_root_id=p.owning_root_id)
    evaluation=resolution.evaluate_drs_candidate_v01(semantic_address=meaning.semantic_address,query=query,meaning_record=meaning)
    _require(evaluation.eligible_for_ranking,'pure_memory_temporal_or_scope:'+repr(evaluation.reason_codes))
    candidate=resolution.build_resolution_candidate_v01(query_id=query.query_id,semantic_address_id=query.semantic_address_id,
        meaning_record_id=meaning.meaning_record_id,query_evaluation_id=evaluation.query_evaluation_id,safe_summary=meaning.safe_summary,
        evidence_ref_ids=meaning.source_reference_ids,source_history_hash=evaluation.source_history_hash,action_history_binding_id=None,
        semantic_similarity_units=10000,freshness_units=evaluation.current_freshness_units,source_authority_prior_units=0,
        lineage_proximity_units=0,historical_utility_units=0,gt_advisory_prior_units=0,conflict_penalty_units=0,risk_penalty_units=0,retrieval_cost_units=100)
    ranked=resolution.rank_eligible_drs_candidates_v01(query=query,query_evaluations=(evaluation,),candidates=(candidate,))
    _require(len(ranked)==1 and ranked[0].meaning_record_id==meaning.meaning_record_id,'pure_memory_ranking')
    pointer=meaning.artifact_pointers[0]
    budget=resolution.build_memory_descent_budget_v01(max_depth=1,max_records_opened=1,max_pointers_opened=1,
        max_artifacts_opened=1,max_bytes_opened=pointer.byte_length,max_lineage_edges=0,max_conflict_records=0)
    plan=resolution.build_retrieval_plan_v01(query_id=query.query_id,semantic_address_id=query.semantic_address_id,
        proposed_record_ids=(meaning.meaning_record_id,),proposed_memory_pointer_ids=(),proposed_artifact_pointer_ids=(pointer.pointer_id,),
        requested_descent_class='OPEN_ONE_ARTIFACT',proposed_budget_id=budget.memory_descent_budget_id,
        required_access_policy_ids=(p.memory_scope,),reason_codes=())
    kernel,decision_input,result=review_pure_memory_v01(need=need,transaction_id=query.query_id,selected_id=plan.retrieval_plan_id,
        subject=query.semantic_address_id,predicate='approve_controlled_memory_descent_plan_v01',
        claim_value=resolution.retrieval_plan_to_plain_data_v01(plan),validation=resolution.validate_retrieval_plan_v01(plan)==(True,()))
    request=resolution.build_memory_descent_request_v01(retrieval_plan_id=plan.retrieval_plan_id,query_id=query.query_id,
        owning_local_root_id=p.owning_root_id,root_kernel_id=kernel.kernel_id,root_decision_input_id=decision_input.decision_input_id,
        root_decision_id=result.decision_id,root_decision_hash=_root_hash(result),requested_descent_class='OPEN_ONE_ARTIFACT',
        approved_descent_class='OPEN_ONE_ARTIFACT',proposed_budget_id=budget.memory_descent_budget_id,approved_budget=budget,
        approved_record_ids=(meaning.meaning_record_id,),approved_memory_pointer_ids=(),approved_artifact_pointer_ids=(pointer.pointer_id,))
    hosts.reserve_pure_need_work_v01(host,need=need,kind='drs',byte_count=pointer.byte_length,expected_revision=host.state_revision)
    path=store.root_path/'pure_payloads'/(pointer.content_sha256+'.json')
    _require(path.is_file() and not path.is_symlink() and path.stat().st_size==pointer.byte_length,'pure_memory_payload_size')
    with path.open('rb') as stream:payload=stream.read(pointer.byte_length+1)
    _require(len(payload)==pointer.byte_length,'pure_memory_payload_size')
    hosts._record_pure_drs_bytes_v01(host,need.permission.task_id,len(payload))
    descent=resolution.execute_local_memory_descent_v01(retrieval_plan=plan,proposed_budget=budget,descent_request=request,
        root_kernel=kernel,root_decision_input=decision_input,root_decision_result=result,source_records=(meaning,),
        artifact_payloads=((pointer.pointer_id,payload),))
    _require(pointer.pointer_id in descent.opened_artifact_pointer_ids and _hash(payload)==pointer.content_sha256,'pure_memory_payload_not_descended')
    data,wasm=_source_payload(payload,need)
    attempt,package=pure.admit_pure_candidate_v01(host,need=need,source=wasm,source_format='wasm',contract_version=data['contract_version'],
        expected_revision=host.state_revision)
    _require(package is not None,'pure_memory_readmission:'+str(attempt.reason))
    return PureMemoryRetrievalV01(search,record,meaning,query,evaluation,ranked,plan,budget,request,kernel,
        decision_input,result,descent,payload,attempt,package)


def _validate_root_review(kernel, decision_input, result, *, root_id, transaction_id, selected_id, subject, predicate, claim_value):
    _require(not root.validate_root_decision_kernel_v01(kernel)
        and not root.validate_root_decision_input_v01(kernel=kernel,decision_input=decision_input)
        and not root.validate_root_decision_result_v01(kernel=kernel,decision_input=decision_input,result=result), 'pure_memory_root_validation')
    _require((result.target_root_id,result.transaction_id,result.selected_candidate_id,result.decision)==
        (root_id,transaction_id,selected_id,'ACCEPT') and not result.permission_created
        and not result.final_output_created and not result.effect_requested,'pure_memory_root_binding')
    claims=root.root_decision_input_to_plain_dict_v01(decision_input)['root_review_packet']['synthesis_proposal']['normalized_claims']
    _require(len(claims)==1 and (claims[0]['claim_id'],claims[0]['subject'],claims[0]['predicate'],claims[0]['object_or_value'])==
        (selected_id,subject,predicate,claim_value),'pure_memory_root_actual_claim')


def validate_pure_memory_record_v01(value, *, package, host):
    _require(type(value) is PureMemoryRecordV01,'pure_memory_record_type')
    pure.validate_admitted_pure_package_v01(package,host=host,need=package.need)
    _require(_meaning_from_record(value.record)==value.meaning,'pure_memory_stored_meaning')
    pointer=value.meaning.artifact_pointers[0]
    _require(pointer.content_sha256==_hash(value.payload)==value.meaning.content_fingerprint
        and pointer.byte_length==len(value.payload),'pure_memory_stored_payload')
    data,wasm=_source_payload(value.payload,package.need)
    p=package.need.permission
    _require((data['contract_version'],data['multiplier'],data['offset'],data['profile_version'],data['wasm_sha256'],data['oracle_sha256'])==
        (p.contract_version,p.multiplier,p.offset,p.profile_version,package.wasm_sha256,package.oracle_sha256)
        and base64.b64decode(data['wasm'],validate=True)==package.wasm,'pure_memory_stored_contract')
    _validate_root_review(value.root_kernel,value.root_input,value.root_result,root_id=p.owning_root_id,transaction_id=p.task_id,
        selected_id=package.package_id,subject=value.meaning.semantic_address.semantic_address_id,
        predicate='record_validated_pure_source_v01',claim_value=dict(payload_sha256=_hash(value.payload),memory_scope=p.memory_scope))
    authority=value.meaning.authority_envelope
    _require((authority.source_root_decision_input_id,authority.source_root_decision_id,authority.source_root_decision_hash)==
        (value.root_input.decision_input_id,value.root_result.decision_id,_root_hash(value.root_result)), 'pure_memory_stored_root')
    return True


def validate_pure_memory_retrieval_v01(value, *, host, need):
    _require(type(value) is PureMemoryRetrievalV01 and value.search.need==need,'pure_memory_retrieval_type')
    pure.validate_admitted_pure_package_v01(value.package,host=host,need=need)
    _require(_meaning_from_record(value.record)==value.meaning,'pure_memory_retrieved_record')
    search=value.search
    validate_pure_search_v01(search,host=host)
    filters=dict(contract_version=need.permission.contract_version,multiplier=need.permission.multiplier,offset=need.permission.offset,
        memory_scope=need.permission.memory_scope,owning_root_id=need.permission.owning_root_id,profile_version=need.permission.profile_version)
    _require(search.query.content_filters==filters and search.query.semantic_terms==('integer','affine','u8')
        and search.query.query_id==search.result.query_id and search.result.candidate_count==1
        and len(search.result.candidates)==1 and search.result.candidates[0].record_id==value.record['record_id']
        and not search.result.candidates[0].blocked and not search.result.candidates[0].stale,'pure_memory_actual_search')
    evaluation=resolution.evaluate_drs_candidate_v01(semantic_address=value.meaning.semantic_address,query=value.query,meaning_record=value.meaning)
    _require(evaluation==value.evaluation and evaluation.eligible_for_ranking and value.query.scope_fingerprint==_scope(need.permission)
        and value.query.owning_local_root_id==need.permission.owning_root_id
        and value.query.evaluation_time==host.current_sources.evaluation_time,'pure_memory_current_evaluation')
    _require(len(value.ranked)==1 and resolution.rank_eligible_drs_candidates_v01(query=value.query,
        query_evaluations=(evaluation,),candidates=value.ranked)==value.ranked,'pure_memory_ranked')
    pointer=value.meaning.artifact_pointers[0]
    for valid in (resolution.validate_retrieval_plan_v01(value.plan),resolution.validate_memory_descent_budget_v01(value.budget),
        resolution.validate_memory_descent_request_v01(value.request),resolution.validate_memory_descent_result_v01(value.descent)):
        _require(valid==(True,()),'pure_memory_typed_descent')
    _require(value.plan.query_id==value.query.query_id and value.plan.semantic_address_id==value.query.semantic_address_id
        and value.plan.proposed_record_ids==(value.meaning.meaning_record_id,)
        and value.plan.proposed_artifact_pointer_ids==(pointer.pointer_id,) and value.plan.proposed_memory_pointer_ids==()
        and value.plan.required_access_policy_ids==(need.permission.memory_scope,)
        and value.plan.proposed_budget_id==value.budget.memory_descent_budget_id,'pure_memory_plan_sources')
    _validate_root_review(value.root_kernel,value.root_input,value.root_result,root_id=need.permission.owning_root_id,
        transaction_id=value.query.query_id,selected_id=value.plan.retrieval_plan_id,subject=value.query.semantic_address_id,
        predicate='approve_controlled_memory_descent_plan_v01',claim_value=resolution.retrieval_plan_to_plain_data_v01(value.plan))
    request=value.request;descent=value.descent
    _require((request.retrieval_plan_id,request.query_id,request.root_decision_input_id,request.root_decision_id,request.root_decision_hash)==
        (value.plan.retrieval_plan_id,value.query.query_id,value.root_input.decision_input_id,value.root_result.decision_id,_root_hash(value.root_result))
        and request.approved_budget==value.budget and request.approved_record_ids==value.plan.proposed_record_ids
        and request.approved_artifact_pointer_ids==(pointer.pointer_id,) and request.approved_memory_pointer_ids==(), 'pure_memory_request_binding')
    _require((descent.memory_descent_request_id,descent.retrieval_plan_id,descent.query_id,descent.applied_budget_id)==
        (request.memory_descent_request_id,value.plan.retrieval_plan_id,value.query.query_id,value.budget.memory_descent_budget_id)
        and descent.opened_record_ids==(value.meaning.meaning_record_id,) and descent.opened_artifact_pointer_ids==(pointer.pointer_id,)
        and descent.opened_payload_fingerprints==(_hash(value.payload),) and descent.bytes_opened==len(value.payload)
        and descent.artifacts_opened==descent.pointers_opened==descent.records_opened==1
        and descent.depth_reached==1 and descent.limits_respected and not descent.reason_codes
        and not descent.creates_permission and not descent.creates_authority and descent.real_world_effects_count==0,
        'pure_memory_descent_actual_payload')
    data,wasm=_source_payload(value.payload,need)
    _require(_hash(value.payload)==pointer.content_sha256 and len(value.payload)==pointer.byte_length
        and base64.b64decode(data['wasm'],validate=True)==value.package.wasm
        and value.attempt is value.package.attempt and value.attempt.source==value.package.wasm
        and value.attempt.source_format=='wasm','pure_memory_same_admission')
    return True
