"""Four finite Gate6 Reference witnesses; recorded evidence never restores authority.

The local-current-policy composition is explicit and bounded to its supplied
validated store. It is not automatic global DRS supersession or a new service.
"""
from __future__ import annotations

import argparse
import base64
import dataclasses as dc
import hashlib
import inspect
import json
from pathlib import Path
import sys
import time
import traceback

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from hedgehog import avf_v02 as avf, drs_semantic_address_v01 as address
from hedgehog import drs_memory_resolution_v01 as memory, reuse_certificate_v01 as reuse
from hedgehog import drs_g2b_compatibility_v01 as compat, local_drs_resolver as resolver
from hedgehog import work_execution_host_v01 as host
from hedgehog.drs import LocalDRS
from hedgehog.kernel import abi_v01 as abi, root_decision_v01 as roots, semantic_work_v01 as sw
from hedgehog.kernel import integrity_replay_v01 as integrity, effect_firewall_v01 as firewall
from hedgehog.kernel import transition_registry_v01 as transitions
from hedgehog.external_drs import gate5_native_v01 as native, gate5_supplied_v01 as supplied_native
from demo import run_drs_semantic_address_reuse_certificate_g2_b_v01 as g2b
from demo import run_gate6_reference_v01 as composer

def require(value,reason):
    if not value:raise ValueError(reason)
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()
def digest(value):return hashlib.sha256(canonical(value)).hexdigest()
def save(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(canonical(value)+b'\n')
def read(path):return json.loads(Path(path).read_bytes())

# Exact immutable evidence carriers only; no Host/Firewall/capability handle codec.
_MODULES=(abi,roots,sw,avf,address,memory,reuse,compat,transitions)
_TYPES={m.__name__+'.'+name:cls for m in _MODULES for name,cls in vars(m).items()
        if isinstance(cls,type) and dc.is_dataclass(cls) and cls.__module__==m.__name__}
_TYPES.update({firewall.__name__+'.'+c.__name__:c for c in
    (firewall.EffectRequestV01,firewall.EffectFirewallDecisionV01,
     firewall.EffectFirewallHistoricalAuthorizationProjectionV01)})
def encode(value):
    if type(value) is bytes:return {'@bytes':base64.b64encode(value).decode('ascii')}
    if dc.is_dataclass(value):
        key=type(value).__module__+'.'+type(value).__name__
        require(key in _TYPES,'non_evidence_type:'+key)
        return {'@record':key,'fields':{f.name:encode(getattr(value,f.name)) for f in dc.fields(value)}}
    if type(value) is tuple:return {'@tuple':[encode(x) for x in value]}
    if type(value) is list:return [encode(x) for x in value]
    if type(value) is dict:
        require(not any(k.startswith('@') for k in value),'reserved_evidence_key')
        return {k:encode(v) for k,v in value.items()}
    require(value is None or type(value) in (str,bool,int,float),'non_plain_evidence')
    return value
def decode(value):
    if type(value) is dict:
        if '@bytes' in value:
            require(set(value)=={'@bytes'},'evidence_bytes_fields');return base64.b64decode(value['@bytes'],validate=True)
        if '@record' in value:
            require(set(value)=={'@record','fields'} and value['@record'] in _TYPES,'evidence_record_type')
            cls=_TYPES[value['@record']];require(set(value['fields'])=={f.name for f in dc.fields(cls)},'evidence_record_fields')
            return cls(**{k:decode(v) for k,v in value['fields'].items()})
        if '@tuple' in value:
            require(set(value)=={'@tuple'},'evidence_tuple_fields');return tuple(decode(x) for x in value['@tuple'])
        return {k:decode(v) for k,v in value.items()}
    if type(value) is list:return [decode(x) for x in value]
    require(value is None or type(value) in (str,bool,int,float),'evidence_scalar');return value

def root_check(review):
    kernel,inputs,result=review
    require(not roots.validate_root_decision_input_v01(kernel=kernel,decision_input=inputs),'root_input_invalid')
    require(not roots.validate_root_decision_result_v01(kernel=kernel,decision_input=inputs,result=result),'root_result_invalid')
    return roots.root_decision_input_to_plain_dict_v01(inputs)

def review(*,root,transaction,selected,subject,predicate,value,label,checks=None,permission=None):
    kernel,inputs,_=g2b._root_triple(transaction_id=transaction,target_root_id=root,selected_id=selected,
        subject=subject,predicate=predicate,claim_value=value,label=label)
    if checks is not None or permission is not None:
        fields=roots.root_decision_input_to_plain_dict_v01(inputs)
        valid=all(checks.values()) if checks is not None else True
        states={k:fields[k] for k in ('post_vv_bundle','gt_advisory','policy_state','permission_state','temporal_state','conflict_state','prior_root_state')}
        if not valid:
            states['post_vv_bundle'].update(post_vv_passed=False,validated_candidate_ids=[],rejected_candidate_ids=[selected],hard_failure_reasons=['policy_validation_failed'])
            states['policy_state'].update(hard_policy_passed=False,allow_accept=False)
        if permission is not None:states['permission_state']=permission
        inputs=roots.build_root_decision_input_v01(transaction_id=transaction,target_root_id=root,root_review_packet=inputs.root_review_packet,**states)
    result=roots.decide_root_v01(kernel=kernel,decision_input=inputs)
    triple=(kernel,inputs,result);root_check(triple);return triple

def observed(output,label,functions,operation):
    start=time.monotonic()
    with composer.observe_calls(functions,output=output/(label+'.observation.json'),phase=label) as observation:
        result=operation()
    require(observation['sentinel_live'] and observation['restored'],'observer_not_restored')
    return dict(value=result,observation=observation,seconds=time.monotonic()-start)

def refusal(function,**kwargs):
    try:function(**kwargs)
    except ValueError as exc:return dict(type=type(exc).__name__,reason=str(exc))
    raise AssertionError('expected_public_refusal:'+function.__name__)

def collect_avf(output):
    candidate=avf.AVFCandidateV02(candidate_id=avf.CANDIDATE_PREPARE_SUPPLIER_A_PAYMENT_FORM_ONLY,
        candidate_label='Prepare isolated mock request for independent Root review',
        source_drs_record_refs=('evidence:g6a5r:avf',),candidate_direction='Bounded proposal only',base_viability_score=1.0)
    evaluated=avf.evaluate_avf_candidates_v02(avf.AVFEvaluationInputV02(evaluation_id='g6a5r:avf',candidates=(candidate,)))
    report=evaluated.decision_reports[0]
    require(report.score_explanation.final_avf_score==1.0 and report.score_explanation.rank==1 and report.hard_mask.hard_mask_value==1,'eligible_high_avf')
    permission=dict(permission_required=True,user_permission_present=True,permission_scope_valid=True,permission_ref='permission:g6a5r:isolated_mock')
    def decide(label,perm):
        return review(root='root:g6a5r:isolated_mock',transaction='transaction:g6a5r:avf',selected=candidate.candidate_id,
            subject='g6a5r:mock_receipt',predicate='review_isolated_mock_request',
            value=dict(avf_report_sha256=digest(encode(report)),candidate_id=candidate.candidate_id,mock_only=True),
            label=label,permission=perm)
    good=decide('g6a5r:avf:good',permission)
    common=dict(root_decision_kernel=good[0],decision_input=good[1],root_decision_result=good[2])
    fwargs=dict(invocation_id='invocation:g6a5r:mock',allowed_adapter_ids=('mock_adapter:g6a5r',),
        allowed_action_kinds=('mock_action:g6a5r:receipt',),root_scope_refs=('scope:g6a5r:mock',),maximum_expires_at_tick=200)
    reqargs=dict(request_kind='ActionCommitPacket',adapter_id='mock_adapter:g6a5r',action_kind='mock_action:g6a5r:receipt',
        scope_refs=('scope:g6a5r:mock',),issued_at_tick=100,expires_at_tick=150,idempotency_key='idempotency:g6a5r:mock')
    gate=firewall.build_effect_firewall_v01(**common,**fwargs)
    before=firewall.effect_firewall_to_plain_dict_v01(gate)
    def rejected_avf():
        wrong=dict(common,root_decision_result=report)
        return dict(firewall=refusal(firewall.build_effect_firewall_v01,**wrong,**fwargs),
            request=refusal(firewall.build_effect_request_v01,**wrong,**reqargs))
    functions=dict(build_firewall=firewall.build_effect_firewall_v01,build_request=firewall.build_effect_request_v01,
        authorize=firewall.authorize_effect_request_v01,effect=firewall.execute_mock_effect_v01)
    rejected=observed(output,'avf_rejected',functions,rejected_avf)
    after_rejection=firewall.effect_firewall_to_plain_dict_v01(gate)
    require(before==after_rejection,'avf_mutated_gate')
    def positive():
        request=firewall.build_effect_request_v01(**common,**reqargs)
        decision=firewall.authorize_effect_request_v01(firewall=gate,request=request,current_tick=110)
        from tests.test_effect_firewall_v01 import TIME_ENVELOPE
        receipt=firewall.execute_mock_effect_v01(firewall=gate,request=request,decision=decision,current_tick=120,
            adapter_id=request.adapter_id,action_kind=request.action_kind,child_scope_refs=request.scope_refs,
            child_expires_at_tick=140,receipt_artifact_id='receipt:g6a5r:isolated_mock',time_envelope=TIME_ENVELOPE)
        require(not firewall.validate_effect_receipt_v01(receipt=receipt,firewall=gate,request=request,decision=decision),'effect_receipt')
        return dict(request=request,decision=decision,receipt=receipt)
    accepted=observed(output,'avf_positive',functions,positive)
    historical=firewall.project_effect_firewall_historical_authorization_v01(
        **common,**fwargs,**reqargs,current_tick=110)
    after_effect=firewall.effect_firewall_to_plain_dict_v01(gate)
    missing=decide('g6a5r:avf:no_permission',dict(permission,user_permission_present=False,permission_ref=None))
    missing_result=observed(output,'avf_no_permission',functions,lambda:refusal(firewall.build_effect_firewall_v01,
        root_decision_kernel=missing[0],decision_input=missing[1],root_decision_result=missing[2],**fwargs))
    require(firewall.effect_firewall_to_plain_dict_v01(gate)==after_effect,'missing_permission_effect')
    return dict(candidate=candidate,evaluation=evaluated,report=report,root=good,missing_root=missing,
        firewall_arguments=fwargs,request_arguments=reqargs,before=before,after_rejection=after_rejection,after_effect=after_effect,
        rejected=rejected,accepted=accepted,missing=missing_result,historical=historical,
        final_state=firewall.effect_firewall_to_plain_dict_v01(gate))

EVIDENCE=g2b._EVIDENCE_CLASSES
def make_record(*,root,summary,source_refs,review_value,now,domain='CALIBRATION_INFORMATION',subject='calibration_source',
                tags=('calibration','informational'),pointers=(),artifact_pointers=(),scope=None):
    schema='g6a5r.'+subject+'.v01';scope=scope or digest(dict(root=root,subject=subject))
    addr=address.build_semantic_address_v01(namespace='g6a5r',domain=domain,subject_class=subject,
        intent_class='informational_summary',meaning_schema_id=schema,meaning_schema_version='v01')
    fingerprint=hashlib.sha256(summary.encode()).hexdigest()
    root_value=dict(summary=summary,source_refs=list(source_refs),content_fingerprint=fingerprint,source=review_value)
    rr=review(root=root,transaction='transaction:g6a5r:write:'+fingerprint,selected='candidate:'+fingerprint,
        subject=addr.semantic_address_id,predicate='record_validated_information',value=root_value,label='g6a5r:write:'+fingerprint)
    env=address.build_drs_time_envelope_v01(pt_created_at=now,kt_as_of=now,et_observed_at=now,ct_context_anchor=now,
        ttl_seconds=600,valid_from=now,valid_to=now+600,source_observed_at=now,source_reported_at=now,
        system_ingested_at=now,system_verified_at=now,freshness_policy_id='freshness:g6a5r')
    auth=address.build_drs_authority_envelope_v01(authority_class='ROOT_ACCEPTED_WORK',owning_local_root_id=root,
        source_root_decision_input_id=rr[1].decision_input_id,source_root_decision_id=rr[2].decision_id,
        source_root_decision_hash=digest(roots.root_decision_result_to_plain_dict_v01(rr[2])),authority_scope_fingerprint=scope,
        root_acceptance_state='ACCEPTED_WORK',recording_component='g6a5r:reference')
    record=address.build_meaning_record_v01(semantic_address=addr,predecessor_record_id=None,supersession_reason=None,
        safe_summary=summary,semantic_tags=tags,resonance_reason='Exact reviewed informational input, not action permission.',
        memory_pointers=pointers,artifact_pointers=artifact_pointers,source_reference_ids=source_refs,lineage_edges=(),
        time_envelope=env,authority_envelope=auth,persistent_lifecycle_state='ACTIVE',risk_hints=(),conflict_hints=(),
        reuse_policy_class='ANSWER_SHORTCUT',policy_version='policy:g6a5r:informational',schema_versions=(schema,),
        content_fingerprint=fingerprint,recording_component='g6a5r:reference')
    return record,rr

def query_for(record,when):
    return memory.build_drs_temporal_query_v01(query_mode='DIRECT_REUSE_CANDIDATE',semantic_address_id=record.semantic_address.semantic_address_id,
        scope_fingerprint=record.authority_envelope.authority_scope_fingerprint,as_of=when,evaluation_time=when,
        evaluation_time_source='INJECTED_CURRENT_DECISION_TIME',time_range_start=0,time_range_end=when+1,
        required_time_axes=('PT','KT','ET','CT','TTL','VALIDITY'),freshness_policy_id=record.time_envelope.freshness_policy_id,
        max_age_seconds=600,domain=record.semantic_address.domain,risk_class='LOW',reuse_intent='INFORMATIONAL_SHORTCUT_CONSIDERATION',
        requested_reuse_classes=('ANSWER_SHORTCUT',),required_evidence_classes=EVIDENCE,forbidden_changes=('POLICY_CHANGED',),
        policy_version=record.policy_version,schema_versions=record.schema_versions,owning_local_root_id=record.authority_envelope.owning_local_root_id)

def shortcut(record,stored,when,label):
    query=query_for(record,when)
    evaluated=memory.evaluate_drs_candidate_v01(semantic_address=record.semantic_address,query=query,meaning_record=record)
    require(evaluated.eligible_for_ranking,'shortcut_ineligible:'+repr(evaluated.reason_codes))
    candidate=g2b._domain_candidate(query=query,evaluation=evaluated,record=record,similarity=10000)
    ranked=memory.rank_eligible_drs_candidates_v01(query=query,query_evaluations=(evaluated,),candidates=(candidate,))
    require(ranked==(candidate,),'shortcut_ranking')
    budget=memory.build_memory_descent_budget_v01(max_depth=0,max_records_opened=1,max_pointers_opened=0,max_artifacts_opened=0,
        max_bytes_opened=0,max_lineage_edges=0,max_conflict_records=0)
    plan=memory.build_retrieval_plan_v01(query_id=query.query_id,semantic_address_id=query.semantic_address_id,
        proposed_record_ids=(record.meaning_record_id,),proposed_memory_pointer_ids=(),proposed_artifact_pointer_ids=(),
        requested_descent_class='SUMMARY_ONLY',proposed_budget_id=budget.memory_descent_budget_id,required_access_policy_ids=(),reason_codes=())
    claim=g2b._shortcut_claim_preimage(query=query,evaluation=evaluated,candidate=candidate,valid_from=when,valid_to=record.time_envelope.valid_to)
    claim['issued_at']=when
    rr=review(root=query.owning_local_root_id,transaction=query.query_id,selected=candidate.resolution_candidate_id,
        subject=query.semantic_address_id,predicate='authorize_non_action_informational_answer_shortcut_v01',value=claim,label=label,
        checks=dict(eligible=evaluated.eligible_for_ranking,ranked=ranked==(candidate,)))
    root_hash=integrity.domain_separated_sha256_hex_v01(domain='hedgehog:drs:root_shortcut_root_result_binding:v01',
        payload=canonical(roots.root_decision_result_to_plain_dict_v01(rr[2])))
    projection=reuse.build_root_shortcut_authorization_projection_v01(owning_local_root_id=query.owning_local_root_id,
        root_kernel_id=rr[0].kernel_id,root_decision_input_id=rr[1].decision_input_id,root_decision_id=rr[2].decision_id,
        root_decision_hash=root_hash,selected_candidate_id=candidate.resolution_candidate_id,semantic_address_id=query.semantic_address_id,
        meaning_record_id=record.meaning_record_id,query_id=query.query_id,query_evaluation_id=evaluated.query_evaluation_id,
        allowed_reuse_class='ANSWER_SHORTCUT',scope_fingerprint=query.scope_fingerprint,policy_version=query.policy_version,
        schema_versions=query.schema_versions,valid_from=when,valid_to=record.time_envelope.valid_to,root_shortcut_policy_ref=claim['root_shortcut_policy_ref'])
    cert=reuse.build_reuse_certificate_v01(semantic_address_id=query.semantic_address_id,meaning_record_id=record.meaning_record_id,
        query_id=query.query_id,query_evaluation_id=evaluated.query_evaluation_id,resolution_candidate_id=candidate.resolution_candidate_id,
        root_shortcut_authorization_projection=projection,case_type='NON_ACTION_INFORMATIONAL',required_evidence_classes=query.required_evidence_classes,
        observed_evidence_fingerprint=evaluated.observed_evidence_fingerprint,forbidden_changes=query.forbidden_changes,
        checked_dependency_fingerprint=evaluated.checked_dependency_fingerprint,valid_from=when,valid_to=record.time_envelope.valid_to,
        reuse_class='ANSWER_SHORTCUT',source_history_hash=evaluated.source_history_hash,action_history_binding_id=None,issued_at=when,evaluated_at=when)
    legacy=compat.project_legacy_drs_source_v01(source_family='LOCAL_DRS_DICT',source=stored,target_semantic_address=record.semantic_address,target_meaning_record=None)
    report=memory.build_drs_resolution_report_v01(semantic_address=record.semantic_address,query=query,source_projections=(legacy,),
        source_records=(record,),query_evaluations=(evaluated,),eligible_candidates=(candidate,),ranked_candidate_ids=(candidate.resolution_candidate_id,),
        selected_candidate_id=candidate.resolution_candidate_id,retrieval_plan=plan,memory_descent_result=None,root_shortcut_projection=projection,
        reuse_certificate=cert,context_only_record_ids=(),historical_only_record_ids=(),warning_only_record_ids=(),rerun_required_record_ids=(),blocked_record_ids=(),
        provider_calls=0,network_calls=0,gemini_calls=0,external_drs_calls=0,connector_calls=0,real_world_effects_count=0,final_status='PASS',reason_codes=())
    checked=reuse.validate_existing_root_shortcut_decision_v01(resolution_report=report,root_kernel=rr[0],root_decision_input=rr[1],root_decision_result=rr[2],use_time=when)
    require(checked==(True,()),'shortcut_public:'+repr(checked))
    return dict(report=report,root=rr,use_time=when,checked=checked,budget=budget)

def business_binding(record,stored,intended):
    require(resolver._g2b_wrapper_matches_v01(stored,record),'persisted_record_binding')
    summary=json.loads(stored['content']['canonical_meaning_record']['safe_summary'])
    require(summary['business']==intended and record.authority_envelope.authority_scope_fingerprint==digest(intended),
        'warm_business_binding')
    require(record.authority_envelope.owning_local_root_id==intended['owner'] and record.policy_version==intended['policy']
        and record.schema_versions==(intended['schema'],),'warm_profile_binding')
    return summary

def warm_consume(record,stored,intended,when):
    summary=business_binding(record,stored,intended)
    result=shortcut(record,stored,when,'g6a5r:warm')
    result['answer']=summary
    return result

def collect_reuse(output):
    values=dict(readings='[8,10,9]',reference=10);root='root:gate5:calibration';now=int(time.time())
    business=dict(operation='gate5.source',inputs=values,owner=root,policy='policy:g6a5r:informational',schema='g6a5r.calibration_source.v01',source_facts=dict(readings=[8,10,9],reference=10))
    functions=dict(domain_executor=native.execute_calibration_v01,host_work=host.execute_admitted_pure_work_v01,
        root=roots.decide_root_v01,read=LocalDRS.read_record,effect=firewall.execute_mock_effect_v01)
    cold=observed(output,'cold',functions,lambda:native.native_work('source',root,'task:g6a5r:cold',values))
    value=cold['value'];require(value['outputs']==dict(total=27,n=3,correction_num=1,correction_den=1),'independent_arithmetic')
    rr=native.root_review(root,'transaction:g6a5r:cold',value['artifact']['artifact_id'],'calibration_source',
        dict(arithmetic=value['outputs']==dict(total=27,n=3,correction_num=1,correction_den=1)),
        dict(work_artifact=value['artifact']['artifact_id'],business=business,answer=value['outputs']),now)
    record,write_root=make_record(root=root,summary=canonical(dict(business=business,answer=value['outputs'])).decode(),
        source_refs=(value['artifact']['artifact_id'],rr[2].decision_id),review_value=dict(work=value['artifact'],root=roots.root_decision_result_to_plain_dict_v01(rr[2])),
        now=now,scope=digest(business))
    drs=LocalDRS(output/'drs');drs.write_record(resolver._g2b_storage_record_v01(meaning_record=record,writeback_metadata={}))
    persisted=drs.read_record('work',record.meaning_record_id);initial=canonical(persisted)
    intended=dict(operation='gate5.source',inputs=dict(readings='[8,10,9]',reference=10),owner='root:gate5:calibration',
        policy='policy:g6a5r:informational',schema='g6a5r.calibration_source.v01',source_facts=dict(readings=[8,10,9],reference=10))
    def warm_operation():
        actual=LocalDRS(output/'drs').read_record('work',record.meaning_record_id)
        require(canonical(actual)==initial and resolver._g2b_wrapper_matches_v01(wrapper=actual,record=record),'persisted_record_binding')
        return warm_consume(record,actual,intended,now+1)
    warm=observed(output,'warm',functions,warm_operation)
    changed=dict(intended,inputs=dict(readings='[8,10,8]',reference=10),source_facts=dict(readings=[8,10,8],reference=10))
    changed_refusal=observed(output,'changed_business',functions,lambda:refusal(warm_consume,
        record=record,stored=persisted,intended=changed,when=now+1))
    report=warm['value']['report'];root_values=warm['value']['root']
    expired=reuse.validate_existing_root_shortcut_decision_v01(resolution_report=report,root_kernel=root_values[0],
        root_decision_input=root_values[1],root_decision_result=root_values[2],use_time=record.time_envelope.valid_to)
    wrong=reuse.validate_existing_root_shortcut_decision_v01(resolution_report=report,root_kernel=rr[0],root_decision_input=rr[1],root_decision_result=rr[2],use_time=now+1)
    require(expired[0] is False and wrong[0] is False,'shortcut_negative')
    require(cold['observation']['counts'].get('domain_executor')==cold['observation']['counts'].get('host_work')==1,'cold_count')
    require(warm['observation']['counts'].get('read')==1 and not warm['observation']['counts'].get('domain_executor',0)
        and not warm['observation']['counts'].get('host_work',0),'warm_count')
    require(warm['value']['answer']['answer']==value['outputs'],'returned_answer')
    return dict(unit='ONE_ACTUAL_ADMITTED_DOMAIN_WORK_EXECUTION',business_cold=business,business_warm=intended,
        cold=cold,cold_root=rr,write_root=write_root,record=record,persisted=persisted,warm=warm,expired=expired,wrong_root=wrong,
        changed_business=changed,changed_refusal=changed_refusal,
        final_store_unchanged=canonical(drs.read_record('work',record.meaning_record_id))==initial)

def rebuild_record(record,**changes):
    fields={n:getattr(record,n) for n in inspect.signature(address.build_meaning_record_v01).parameters}
    return address.build_meaning_record_v01(**dict(fields,**changes))

def policy_geometry(predecessor,commitment,successor,rr):
    return dict(predecessor_record=predecessor,successor_commitment_record=commitment,successor_record=successor,
        claim_dimension='travel_policy_summary',root_kernel=rr[0],root_decision_input=rr[1],root_decision_result=rr[2])

def current_policy_id(geometry,stored):
    """Finite closed-store policy: validate real replacement before selecting its tip."""
    proposal,root_hash,edge=resolver._g2b_validate_root_reviewed_writeback_geometry_v01(**geometry)
    records=(geometry['predecessor_record'],geometry['successor_record'])
    require(len(stored)==2 and len({r['record_id'] for r in stored})==2,'current_policy_store_inventory')
    by_id={r['record_id']:r for r in stored}
    for record in records:
        require(record.meaning_record_id in by_id and resolver._g2b_wrapper_matches_v01(by_id[record.meaning_record_id],record),'current_policy_stored_binding')
    successor=records[1];content=by_id[successor.meaning_record_id]['content']
    require((content['writeback_proposal_id'],content['root_result_binding_hash'],content['supersession_evidence_id'],content['root_decision_id'])==
        (proposal,root_hash,edge.lineage_edge_id,geometry['root_decision_result'].decision_id),'current_policy_stored_writeback')
    require(records[0].policy_version==successor.policy_version and records[0].schema_versions==successor.schema_versions,'current_policy_same_profile')
    # The validated edge and actual successor predecessor field derive replacement.
    removed={r.predecessor_record_id for r in records if r.predecessor_record_id is not None}
    tips={r.meaning_record_id for r in records}-removed
    require(len(tips)==1,'current_policy_ambiguous_tip')
    return next(iter(tips))

def current_policy_consume(geometry,stored,answer,label):
    current=current_policy_id(geometry,stored)
    rr=answer['root'];report=answer['report'];when=answer['use_time']
    valid=reuse.validate_existing_root_shortcut_decision_v01(resolution_report=report,root_kernel=rr[0],root_decision_input=rr[1],root_decision_result=rr[2],use_time=when)
    require(valid==(True,()),'historical_shortcut_invalid')
    selected=selected_record(report).meaning_record_id
    checks=dict(valid_historical_shortcut=valid==(True,()),current_record_matches=selected==current)
    claim=dict(policy='g6a5r:explicit_local_current_travel_policy_v01',claim_dimension='travel_policy_summary',
        stored_identities=sorted((r['record_id'],digest(r)) for r in stored),current_record_id=current,
        requested_record_id=selected,query_id=report.query.query_id,checks=checks)
    decision=review(root=report.query.owning_local_root_id,transaction='current:'+report.query.query_id,
        selected=report.selected_candidate_id,subject=report.query.semantic_address_id,predicate='consume_local_current_policy_only',
        value=claim,label=label,checks=checks)
    accepted=decision[2].decision=='ACCEPT'
    require(accepted==checks['current_record_matches'],'current_root_must_follow_checked_policy')
    actual=next(r for r in stored if r['record_id']==selected)
    return dict(derived_current=current,checks=checks,claim=claim,root=decision,
        status='CONSUMED' if accepted else 'REFUSED_REPLACED',answer=actual['content']['canonical_meaning_record']['safe_summary'] if accepted else None)

def descent_case(record,payload,when,descent_class,label,output):
    query=query_for(record,when);pointer=record.artifact_pointers[0]
    budget=memory.build_memory_descent_budget_v01(max_depth=1,max_records_opened=1,max_pointers_opened=1,
        max_artifacts_opened=1,max_bytes_opened=len(payload),max_lineage_edges=0,max_conflict_records=0)
    proposed=(pointer.pointer_id,) if descent_class!='SUMMARY_ONLY' else ()
    plan=memory.build_retrieval_plan_v01(query_id=query.query_id,semantic_address_id=query.semantic_address_id,
        proposed_record_ids=(record.meaning_record_id,),proposed_memory_pointer_ids=(),proposed_artifact_pointer_ids=proposed,
        requested_descent_class=descent_class,proposed_budget_id=budget.memory_descent_budget_id,
        required_access_policy_ids=(pointer.access_policy_id,) if proposed else (),reason_codes=())
    rr=review(root=query.owning_local_root_id,transaction=query.query_id,selected=plan.retrieval_plan_id,
        subject=query.semantic_address_id,predicate='approve_controlled_memory_descent_plan_v01',
        value=memory.retrieval_plan_to_plain_data_v01(plan),label=label)
    root_hash=integrity.domain_separated_sha256_hex_v01(domain='hedgehog:drs:memory_descent_root_result_binding:v01',
        payload=canonical(roots.root_decision_result_to_plain_dict_v01(rr[2])))
    request=memory.build_memory_descent_request_v01(retrieval_plan_id=plan.retrieval_plan_id,query_id=query.query_id,
        owning_local_root_id=query.owning_local_root_id,root_kernel_id=rr[0].kernel_id,root_decision_input_id=rr[1].decision_input_id,
        root_decision_id=rr[2].decision_id,root_decision_hash=root_hash,requested_descent_class=descent_class,
        approved_descent_class=descent_class,proposed_budget_id=budget.memory_descent_budget_id,approved_budget=budget,
        approved_record_ids=(record.meaning_record_id,),approved_memory_pointer_ids=(),approved_artifact_pointer_ids=proposed)
    arguments=dict(retrieval_plan=plan,proposed_budget=budget,descent_request=request,root_kernel=rr[0],
        root_decision_input=rr[1],root_decision_result=rr[2],source_records=(record,),
        artifact_payloads=((pointer.pointer_id,payload),) if proposed else ())
    def execute():
        try:return dict(result=memory.execute_local_memory_descent_v01(**arguments))
        except ValueError as exc:return dict(refusal=str(exc))
    outcome=observed(output,label,dict(descent=memory.execute_local_memory_descent_v01,
        access=memory._b3_pointer_access_allowed,read=LocalDRS.read_record,effect=firewall.execute_mock_effect_v01),execute)
    return dict(arguments=arguments,outcome=outcome,payload_origin='CONTROLLED_IN_MEMORY_NOT_EXTERNAL_READ')

def collect_policy(output,now=None):
    now=int(time.time()) if now is None else now;root='root:local_reference'
    predecessor,initial_root=make_record(root=root,summary='Current bounded travel-policy summary.',
        source_refs=('source:g6a5r:travel_policy:initial',),review_value=dict(profile='TRAVEL_POLICY_INFORMATION'),now=now,
        domain='TRAVEL_POLICY_INFORMATION',subject='travel_policy',tags=('travel','policy','informational','claim_dimension:travel_policy_summary'))
    drs=LocalDRS(output/'drs');drs.write_record(resolver._g2b_storage_record_v01(meaning_record=predecessor,writeback_metadata={}))
    first=drs.read_record('work',predecessor.meaning_record_id);before=canonical(first)
    initial=shortcut(predecessor,first,now+1,'g6a5r:policy:initial')
    expired_query=query_for(predecessor,now+600)
    expired=memory.evaluate_drs_candidate_v01(semantic_address=predecessor.semantic_address,query=expired_query,meaning_record=predecessor)
    require(not expired.eligible_for_ranking,'expired_policy_ranked')
    unreviewed=address.build_drs_authority_envelope_v01(authority_class='EVIDENCE_CANDIDATE',owning_local_root_id=None,
        source_root_decision_input_id=None,source_root_decision_id=None,source_root_decision_hash=None,
        authority_scope_fingerprint=predecessor.authority_envelope.authority_scope_fingerprint,root_acceptance_state='UNREVIEWED',recording_component='g6a5r:reference')
    summary='Current bounded travel-policy summary. Root-reviewed successor.'
    times={n:getattr(predecessor.time_envelope,n) for n in inspect.signature(address.build_drs_time_envelope_v01).parameters}
    for n in ('pt_created_at','kt_as_of','et_observed_at','ct_context_anchor','valid_from','source_observed_at','source_reported_at','system_ingested_at','system_verified_at'):times[n]=now+2
    times['valid_to']=now+602
    commitment=rebuild_record(predecessor,safe_summary=summary,authority_envelope=unreviewed,
        time_envelope=address.build_drs_time_envelope_v01(**times),source_reference_ids=('source:g6a5r:travel_policy:successor',),
        content_fingerprint=hashlib.sha256(summary.encode()).hexdigest())
    reason='Root-reviewed correction of the same travel_policy_summary claim.'
    claim=resolver._g2b_writeback_claim_preimage_v01(predecessor_record=predecessor,successor_commitment_record=commitment,
        claim_dimension='travel_policy_summary',supersession_reason=reason)
    rr=review(root=root,transaction=claim['writeback_proposal_id'],selected=claim['writeback_proposal_id'],
        subject=predecessor.semantic_address.semantic_address_id,predicate=resolver._G2B_WRITEBACK_PREDICATE_V01,value=claim,label='g6a5r:policy:writeback')
    edge=address.build_lineage_edge_v01(source_meaning_record_id=predecessor.meaning_record_id,target_meaning_record_id=commitment.meaning_record_id,
        relation_class='REPLACES',claim_dimension='travel_policy_summary',source_history_hash=resolver._g2b_predecessor_history_hash_v01(predecessor),
        evidence_ref_ids=(claim['writeback_proposal_id'],),created_at=now+2,recording_component='g6a5r:reference')
    auth=address.build_drs_authority_envelope_v01(authority_class='ROOT_ACCEPTED_WORK',owning_local_root_id=root,
        source_root_decision_input_id=rr[1].decision_input_id,source_root_decision_id=rr[2].decision_id,
        source_root_decision_hash=resolver._g2b_writeback_root_result_hash_v01(root_decision_result=rr[2]),
        authority_scope_fingerprint=predecessor.authority_envelope.authority_scope_fingerprint,root_acceptance_state='ACCEPTED_WORK',recording_component='g6a5r:reference')
    successor=rebuild_record(commitment,predecessor_record_id=predecessor.meaning_record_id,supersession_reason=reason,
        authority_envelope=auth,lineage_edges=(edge,),source_reference_ids=commitment.source_reference_ids+(claim['writeback_proposal_id'],edge.lineage_edge_id))
    geometry=policy_geometry(predecessor,commitment,successor,rr)
    save(output/'writeback_inputs.json',encode(geometry))
    write_observed=observed(output,'policy_writeback',dict(writeback=resolver._g2b_write_root_reviewed_meaning_record_v01,
        write=LocalDRS.write_record),lambda:resolver._g2b_write_root_reviewed_meaning_record_v01(drs=drs,**geometry))
    writeback=write_observed['value']
    stored=resolver._g2b_read_local_records_v01(drs=drs,layers=('work',))
    require(canonical(drs.read_record('work',predecessor.meaning_record_id))==before,'predecessor_mutated')
    fresh=shortcut(successor,drs.read_record('work',successor.meaning_record_id),now+3,'g6a5r:policy:fresh')
    old=shortcut(predecessor,drs.read_record('work',predecessor.meaning_record_id),now+3,'g6a5r:policy:historical')
    current=current_policy_consume(geometry,stored,fresh,'g6a5r:policy:current')
    replaced=current_policy_consume(geometry,stored,old,'g6a5r:policy:replaced')
    require(current_policy_id(geometry,tuple(reversed(stored)))==current['derived_current'],'list_order_dependence')
    rebound=reuse.validate_existing_root_shortcut_decision_v01(resolution_report=old['report'],root_kernel=fresh['root'][0],
        root_decision_input=fresh['root'][1],root_decision_result=fresh['root'][2],use_time=now+3)
    require(not rebound[0],'historical_certificate_rebound')
    payload=b'{"internal_policy_detail":"restricted controlled example"}'
    pointer=address.build_artifact_pointer_v01(storage_class='LOCAL_DOCUMENT',object_reference='document:g6a5r:policy',
        content_sha256=hashlib.sha256(payload).hexdigest(),media_type='application/json',byte_length=len(payload),
        access_policy_id='access:g6a5r:summary_only',sensitivity_class='INTERNAL',allowed_use_classes=('SUMMARY_ONLY',),
        forbidden_use_classes=('OPEN_ONE_ARTIFACT',),summary_read_permitted=True,payload_read_permitted=False)
    restricted,restricted_root=make_record(root=root,summary='Restricted travel-policy summary available for informational use.',
        source_refs=('source:g6a5r:travel_policy:restricted',),review_value=dict(pointer=address.artifact_pointer_to_plain_data_v01(pointer)),now=now,
        domain='TRAVEL_POLICY_INFORMATION',subject='travel_policy',tags=predecessor.semantic_tags,artifact_pointers=(pointer,))
    denied=descent_case(restricted,payload,now+3,'OPEN_ONE_ARTIFACT','restricted',output)
    allowed=descent_case(restricted,payload,now+3,'SUMMARY_ONLY','summary',output)
    require(denied['outcome']['value']==dict(refusal='drs_pointer_access_policy_denied'),'restricted_actual_reason')
    require(allowed['outcome']['value']['result'].bytes_opened==0,'summary_payload_read')
    return dict(initial_root=initial_root,initial=initial,expired_query=expired_query,expired=expired,geometry=geometry,
        writeback=writeback,write_observed=write_observed,stored=stored,fresh=fresh,historical=old,current=current,replaced=replaced,rebound=rebound,
        predecessor_unchanged=canonical(drs.read_record('work',predecessor.meaning_record_id))==before,
        restricted_root=restricted_root,restricted=restricted,denied=denied,allowed=allowed)

def selected_record(report):
    require(len(report.source_records)==len(report.eligible_candidates)==1,'one_record_witness_required')
    record,candidate=report.source_records[0],report.eligible_candidates[0]
    require(report.selected_candidate_id==candidate.resolution_candidate_id
        and candidate.meaning_record_id==record.meaning_record_id,'selected_record_binding')
    return record

def claim_value(rr):
    plain=root_check(rr)
    claims=plain['root_review_packet']['synthesis_proposal']['normalized_claims']
    require(len(claims)==1,'one_claim_witness_required')
    return claims[0]['object_or_value']

def counts(observation):
    require(observation['sentinel_live'] and observation['restored'] and observation['scope']=='CURRENT_PROCESS_CURRENT_THREAD_ONLY',
        'observer_boundary')
    actual={}
    for event in observation['events']:
        if event['event']=='call':actual[event['label']]=actual.get(event['label'],0)+1
    require(actual==observation['counts'] and actual.get('sentinel')==1,'observer_event_counts')
    for pin in observation['identities'].values():
        path=Path(pin['file']);parts=path.parts
        start=next((i for i,x in enumerate(parts) if x in ('hedgehog','demo','tests')),None)
        require(start is not None,'observer_source_path')
        local=ROOT.joinpath(*parts[start:]);data=local.read_bytes()
        require(len(data)==pin['bytes'] and hashlib.sha256(data).hexdigest()==pin['sha256'],'observer_source_pin')
    return actual

def check_counts(observation,expected):
    require(counts(observation)==dict(expected,sentinel=1),'operation_counts')

def validate_shortcut(value,record):
    rr=value['root'];root_check(rr);report=value['report']
    require(selected_record(report)==record,'shortcut_record')
    require(reuse.validate_existing_root_shortcut_decision_v01(resolution_report=report,root_kernel=rr[0],
        root_decision_input=rr[1],root_decision_result=rr[2],use_time=value['use_time'])==(True,()),'shortcut_validation')

def check_avf(value):
    candidate,report=value['candidate'],value['report']
    require(avf.validate_avf_decision_report_v02(report)==(True,()),'avf_report')
    require(value['evaluation'].decision_reports==(report,) and report.candidate_id==candidate.candidate_id
        and report.score_explanation.final_avf_score==1.0 and report.score_explanation.rank==1
        and report.hard_mask.hard_mask_value==1,'avf_candidate_score')
    expected=dict(avf_report_sha256=digest(encode(report)),candidate_id=candidate.candidate_id,mock_only=True)
    for rr in (value['root'],value['missing_root']):require(claim_value(rr)==expected,'avf_root_claim')
    require(value['root'][2].decision=='ACCEPT' and value['missing_root'][2].decision!='ACCEPT','avf_permission_decisions')
    require(value['root'][2].selected_candidate_id==candidate.candidate_id,'avf_selected_candidate')
    require(value['before']==value['after_rejection'],'avf_refusal_state')
    check_counts(value['rejected']['observation'],dict(build_firewall=1,build_request=1))
    check_counts(value['accepted']['observation'],dict(build_request=1,authorize=1,effect=1))
    check_counts(value['missing']['observation'],dict(build_firewall=1))
    require({k:x['reason'] for k,x in value['rejected']['value'].items()}==dict(
        firewall='effect_firewall_binding_invalid',request='effect_request_invalid'),'avf_actual_refusals')
    require(value['missing']['value']['reason']=='effect_firewall_binding_invalid','missing_permission_refusal')
    rr=value['root'];projection=value['historical'];actual=value['accepted']['value']
    require(not firewall.validate_effect_firewall_historical_authorization_projection_v01(projection,
        root_decision_kernel=rr[0],decision_input=rr[1],root_decision_result=rr[2],
        **value['firewall_arguments'],**value['request_arguments'],current_tick=110),'historical_authorization')
    require(projection.request==actual['request'] and projection.decision==actual['decision'],'actual_historical_binding')
    receipt=actual['receipt']
    require(not abi.validate_kernel_artifact_v01(receipt),'receipt_abi')
    require(not firewall._retained_effect_receipt_contract_errors_v01(receipt=receipt,request=actual['request'],
        decision=actual['decision'],root_scope_refs=value['firewall_arguments']['root_scope_refs']),'receipt_contract')
    # Actual state and receipt bind the observed isolated effect; no live gate is rebuilt.
    before,after=value['before'],value['after_effect']
    require(before['firewall_id']==after['firewall_id']==projection.firewall_id,'gate_identity')
    require(all(v==0 for v in before['state_counters'].values()),'fresh_empty_gate')
    require(after['state_counters']=={k:(0 if k=='real_world_effects_count' else 1) for k in before['state_counters']}
        and value['final_state']==after,'exact_isolated_effect_state')
    return dict(row='N1-05',high_avf=1.0,invalid_builders=2,mock_effects=1,new_authority_restored=False)

def check_reuse(value):
    cold=value['cold']['value'];business=value['business_warm'];record=value['record']
    require(business==value['business_cold'],'same_business')
    require(business['operation']=='gate5.source' and business['inputs']==dict(readings='[8,10,9]',reference=10)
        and business['source_facts']==dict(readings=[8,10,9],reference=10),'business_input')
    numbers=json.loads(business['inputs']['readings']);reference=business['inputs']['reference']
    total=sum(numbers);n=len(numbers)
    from fractions import Fraction
    correction=Fraction(reference*n-total,n)
    expected=dict(total=total,n=n,correction_num=correction.numerator,correction_den=correction.denominator)
    require(supplied_native.native_result(cold,business['owner'],business['inputs'])==expected,'native_arithmetic')
    for key in ('cold_root','write_root'):root_check(value[key])
    require(value['cold_root'][2].selected_candidate_id==cold['artifact']['artifact_id'],'cold_root_work')
    require(claim_value(value['cold_root'])['answer']==expected and claim_value(value['cold_root'])['business']==business,'cold_review_business')
    authority=record.authority_envelope;wr=value['write_root']
    require((authority.source_root_decision_input_id,authority.source_root_decision_id,authority.source_root_decision_hash)==
        (wr[1].decision_input_id,wr[2].decision_id,digest(roots.root_decision_result_to_plain_dict_v01(wr[2]))),'write_root_binding')
    require(claim_value(wr)['summary']==record.safe_summary and cold['artifact']['artifact_id'] in record.source_reference_ids,'write_content_lineage')
    summary=business_binding(record,value['persisted'],business)
    validate_shortcut(value['warm']['value'],record)
    require(summary==value['warm']['value']['answer'] and summary['answer']==expected,'stored_returned_answer')
    check_counts(value['cold']['observation'],dict(domain_executor=1,host_work=1))
    check_counts(value['warm']['observation'],dict(read=1,root=2))
    check_counts(value['changed_refusal']['observation'],{})
    require(value['changed_business']!=business and value['changed_refusal']['value']['reason']=='warm_business_binding','changed_business_refusal')
    require(refusal(business_binding,record=record,stored=value['persisted'],intended=value['changed_business'])['reason']=='warm_business_binding','changed_business_check')
    rr=value['warm']['value']['root'];report=value['warm']['value']['report']
    expired=reuse.validate_existing_root_shortcut_decision_v01(resolution_report=report,root_kernel=rr[0],root_decision_input=rr[1],
        root_decision_result=rr[2],use_time=record.time_envelope.valid_to)
    cr=value['cold_root']
    wrong=reuse.validate_existing_root_shortcut_decision_v01(resolution_report=report,root_kernel=cr[0],root_decision_input=cr[1],
        root_decision_result=cr[2],use_time=value['warm']['value']['use_time'])
    require(expired==value['expired'] and wrong==value['wrong_root'] and not expired[0] and not wrong[0],'reuse_negatives')
    require(value['final_store_unchanged'],'warm_store_mutation')
    return dict(row='N4-04',answer=expected,domain_executions=[1,0],host_work=[1,0],warm_roots=2,action_effects=0)

def check_policy(value):
    geometry=value['geometry'];stored=value['stored'];current=current_policy_id(geometry,stored)
    require(current_policy_id(geometry,tuple(reversed(stored)))==current,'policy_order')
    require(geometry['predecessor_record'].time_envelope.pt_created_at==1790503615
        and geometry['successor_record'].time_envelope.pt_created_at==1790503617,'exact_policy_time')
    exact=decode(read(ROOT/'docs/gate6_reference_v01/evidence/retained_obligations/exact_writeback_inputs.json'))
    require(geometry==exact,'exact_failed_geometry_parity')
    check_counts(value['write_observed']['observation'],dict(writeback=1,write=1))
    require(value['write_observed']['value']==value['writeback'] and value['predecessor_unchanged'],'immutable_writeback')
    wb=value['writeback'];proposal,root_hash,edge=resolver._g2b_validate_root_reviewed_writeback_geometry_v01(**geometry)
    require(wb['records_written']==1 and wb['successor_readback_exact'] and wb['predecessor_preserved']
        and wb['successor_record_id']==current and wb['root_decision_id']==geometry['root_decision_result'].decision_id
        and wb['writeback_proposal_id']==proposal and wb['root_result_binding_hash']==root_hash
        and wb['supersession_evidence_id']==edge.lineage_edge_id,'writeback_relationships')
    by_id={r['record_id']:r for r in stored}
    storage_hash=lambda r:hashlib.sha256(json.dumps(r,indent=2,sort_keys=True).encode()).hexdigest()
    require(wb['predecessor_storage_sha256_before']==wb['predecessor_storage_sha256_after']==storage_hash(by_id[geometry['predecessor_record'].meaning_record_id])
        and wb['successor_storage_sha256']==storage_hash(by_id[current]),'writeback_exact_bytes')
    root_check(value['initial_root']);root_check(value['restricted_root'])
    validate_shortcut(value['initial'],geometry['predecessor_record'])
    for name,record,decision_name in (('fresh',geometry['successor_record'],'current'),
                                      ('historical',geometry['predecessor_record'],'replaced')):
        answer=value[name];validate_shortcut(answer,record);result=value[decision_name]
        selected=selected_record(answer['report']).meaning_record_id
        checks=dict(valid_historical_shortcut=True,current_record_matches=selected==current)
        expected=dict(policy='g6a5r:explicit_local_current_travel_policy_v01',claim_dimension='travel_policy_summary',
            stored_identities=sorted((r['record_id'],digest(r)) for r in stored),current_record_id=current,
            requested_record_id=selected,query_id=answer['report'].query.query_id,checks=checks)
        require(canonical(result['claim'])==canonical(expected) and canonical(claim_value(result['root']))==canonical(expected),
            'current_policy_root_claim')
        require(result['checks']==checks and result['derived_current']==current,'current_policy_derivation')
        accepted=selected==current
        require((result['root'][2].decision=='ACCEPT')==accepted and result['status']==('CONSUMED' if accepted else 'REFUSED_REPLACED')
            and result['answer']==(record.safe_summary if accepted else None),'current_policy_consumption')
    expired=memory.evaluate_drs_candidate_v01(semantic_address=geometry['predecessor_record'].semantic_address,
        query=value['expired_query'],meaning_record=geometry['predecessor_record'])
    require(expired==value['expired'] and not expired.eligible_for_ranking,'policy_expiry')
    rr=value['fresh']['root']
    rebound=reuse.validate_existing_root_shortcut_decision_v01(resolution_report=value['historical']['report'],root_kernel=rr[0],
        root_decision_input=rr[1],root_decision_result=rr[2],use_time=value['fresh']['use_time'])
    require(rebound==value['rebound'] and not rebound[0],'policy_rebound')
    pointer=value['restricted'].artifact_pointers[0]
    require(not pointer.payload_read_permitted and pointer.summary_read_permitted and 'OPEN_ONE_ARTIFACT' in pointer.forbidden_use_classes,'restricted_pointer')
    denied,allowed=value['denied'],value['allowed']
    for case in (denied,allowed):
        a=case['arguments'];rr=(a['root_kernel'],a['root_decision_input'],a['root_decision_result'])
        root_check(rr);plan=a['retrieval_plan'];request=a['descent_request'];budget=a['proposed_budget']
        require(memory.validate_retrieval_plan_v01(plan)==(True,()) and memory.validate_memory_descent_request_v01(request)==(True,())
            and memory.validate_memory_descent_budget_v01(budget)==(True,()),'descent_carriers')
        require(claim_value(rr)==memory.retrieval_plan_to_plain_data_v01(plan) and rr[2].selected_candidate_id==plan.retrieval_plan_id
            and rr[2].decision=='ACCEPT','descent_root_plan')
        root_hash=integrity.domain_separated_sha256_hex_v01(domain='hedgehog:drs:memory_descent_root_result_binding:v01',
            payload=canonical(roots.root_decision_result_to_plain_dict_v01(rr[2])))
        require((request.root_kernel_id,request.root_decision_input_id,request.root_decision_id,request.root_decision_hash)==
            (rr[0].kernel_id,rr[1].decision_input_id,rr[2].decision_id,root_hash),'descent_root_binding')
        require(request.retrieval_plan_id==plan.retrieval_plan_id and request.query_id==plan.query_id
            and request.approved_budget==budget and request.approved_record_ids==plan.proposed_record_ids
            and request.approved_artifact_pointer_ids==plan.proposed_artifact_pointer_ids,'descent_approved_boundary')
        require(a['source_records']==(value['restricted'],),'descent_source')
        require(case['payload_origin']=='CONTROLLED_IN_MEMORY_NOT_EXTERNAL_READ','descent_origin')
        observed_counts=counts(case['outcome']['observation'])
        require(observed_counts.get('descent')==1 and observed_counts.get('read',0)==observed_counts.get('effect',0)==0,'descent_counts')
    require(denied['outcome']['value']==dict(refusal='drs_pointer_access_policy_denied'),'restricted_refusal')
    require(counts(denied['outcome']['observation']).get('access')==1,'actual_access_check')
    denied_plan=denied['arguments']['retrieval_plan']
    require(not memory._b3_pointer_access_allowed(pointer=pointer,approved_descent_class='OPEN_ONE_ARTIFACT',
        required_access_policy_ids=denied_plan.required_access_policy_ids,artifact=True),'restricted_access_predicate')
    require(denied['arguments']['artifact_payloads']==((pointer.pointer_id,denied['arguments']['artifact_payloads'][0][1]),)
        and hashlib.sha256(denied['arguments']['artifact_payloads'][0][1]).hexdigest()==pointer.content_sha256,'restricted_payload_binding')
    result=allowed['outcome']['value']['result']
    require(memory.validate_memory_descent_result_v01(result)==(True,()) and result.bytes_opened==0
        and not allowed['arguments']['artifact_payloads'] and result.safe_summaries==(value['restricted'].safe_summary,)
        and result.opened_record_ids==(value['restricted'].meaning_record_id,)
        and result.memory_descent_request_id==allowed['arguments']['descent_request'].memory_descent_request_id,'summary_zero_payload')
    return dict(row='N4-05',current_record=current,predecessor_historically_valid=True,replaced_current_use='REFUSED',
        successor_writes=1,restricted_descent='REFUSED',summary_bytes=0,exact_failed_geometry='IDENTICAL')

def plain_root_record(cls,value):
    """Decode the retained dataclass projection, for pure Root checks only."""
    import typing
    hints=typing.get_type_hints(cls)
    require(set(value)=={f.name for f in dc.fields(cls)},'plain_root_fields')
    def convert(v,t):
        if typing.get_origin(t) is tuple:
            args=typing.get_args(t)
            return tuple(convert(x,args[0] if len(args)==2 and args[1] is Ellipsis else args[i]) for i,x in enumerate(v))
        if isinstance(t,type) and dc.is_dataclass(t):
            require(t.__module__+'.'+t.__name__ in _TYPES,'plain_root_type')
            return plain_root_record(t,v)
        if t is object:
            if type(v) is dict and set(v)=={'items'}:
                module=sys.modules[cls.__module__]
                return module._FrozenJSONObject(tuple((k,convert(x,object)) for k,x in v['items']))
            if type(v) is list:return tuple(convert(x,object) for x in v)
        return v
    return cls(**{k:convert(v,hints[k]) for k,v in value.items()})

def privacy_inputs(root=ROOT):
    index=read(root/'docs/gate6_reference_v01/evidence_index.json')['resources']
    def resource(name):
        pin=index['a/campaign/MODEL/MODEL/'+name];data=(root/pin['path']).read_bytes()
        require(len(data)==pin['bytes'] and hashlib.sha256(data).hexdigest()==pin['sha256'],'privacy_resource_pin')
        return json.loads(data)
    return dict(sealed=resource('sealed.json'),semantics=resource('semantic_records.json'),summary=resource('summary.json'),
        responses=[resource('adapter/response_'+str(i).zfill(2)+'.json') for i in range(1,5)])

def check_privacy(value):
    from hedgehog.domains.testflix import contracts_v01 as c, evidence_v01 as e
    payload=value['sealed']['payload'];request=payload['request'];semantics=value['semantics'];previous=[]
    require(semantics==payload['semantics'] and semantics['mode']=='LIVE_CAPTURED','retained_live_semantics')
    roles=('intent_interpreter','provider_terms_analyst','client_plan_selector','contract_reviewer')
    records=semantics['contributions'];require(len(records)==len(value['responses'])==4,'four_roles')
    require(request['preference']=='QUALITY','finite_quality_profile')
    markers=(request['bank_private'],request['user_private'])
    require(markers==('CANARY_BANK_PRIVATE_NO_ROLE_EXPORT','CANARY_USER_PRIVATE_NO_BANK_OR_DEVICE_EXPORT'),'retained_private_markers')
    for i,(role,record,response) in enumerate(zip(roles,records,value['responses'],strict=True)):
        # Independent finite oracle: only allowlisted request fields and prior outputs.
        expected={k:request[k] for k in ('request_id','preference','hard_ceiling_minor','currency')}
        expected['task_contract']=dict(subject='Testflix subscription selection from a supplied finite catalog',price_unit='minor currency units',
            required_inputs=['preference','hard_ceiling_minor','currency']+(['catalog','upstream'] if i else []),
            intent_scope='Interpret the explicit preference enum; content genre and viewing habits are not required inputs.',
            preference_definition=dict(enum='QUALITY',eligible='price_minor <= hard_ceiling_minor',
                priority_order=['resolution descending','ads false before true','price_minor ascending','plan_id ascending'],
                scope='Use catalog fields only. Advertising is a tie-breaker, not a veto on higher resolution. Premium content and simultaneous streams are not supplied requirements.'))
        if i:
            expected['catalog']=request['catalog']
            expected['upstream']=[dict(role=r['role'],output=r['output'],capture_ref=r['capture']['capture_id']) for r in previous]
        require(record['role']==role and record['projection']==response['projection']==expected,'independent_projection')
        require(not any(marker in canonical(expected).decode() for marker in markers),'private_export')
        capture=record['capture'];transport=capture['transport'];metadata=response['metadata']
        require(transport==response['transport'] and transport['origin_mode']=='LIVE' and json.loads(transport['raw_response'])==record['output'],'actual_transport')
        material=dict(role=role,request_ref=c.identity_v01('semantic_request',request),projection_ref=c.identity_v01('role_projection',expected),
            response_ref=c.identity_v01('role_response',record['output']),transport=transport)
        require(capture==dict(material,capture_id=c.identity_v01('semantic_capture',material)),'capture_binding')
        require(all(metadata[k]==material[k] for k in ('role','request_ref','projection_ref'))
            and all(metadata[k]==transport[k] for k in ('provider','model','attempt','started_utc')),'adapter_binding')
        previous.append(record)
    selected=records[2]['output']['selected_plan_id'];plan=next(p for p in request['catalog'] if p['plan_id']==selected)
    require(semantics['selected_plan']==plan and semantics['semantic_ref']==c.identity_v01('semantic',records),'selected_semantics')
    quote=next(x for x in payload['quote']['results'] if x['work_id']=='quote')
    expected_inputs=dict(period_seconds=plan['period_seconds'],plan_id=selected,price_minor=plan['price_minor'])
    actual_inputs={x['parameter_name']:x['value'] for x in quote['invocation']['inputs']}
    require(actual_inputs==expected_inputs and quote['status']=='COMPLETED','downstream_quote_input')
    admission=next(x for x in payload['quote']['admission_snapshots'] if x['admission_id']==quote['invocation']['admission_id'])
    # The accepted pure capability validators check the same actual native return.
    inv=firewall._native_read(firewall.BoundCapabilityInvocationV01,quote['invocation'])
    result=firewall._native_read(firewall.CapabilityExecutionResultV01,quote['result'])
    snapshot=firewall._native_read(firewall.CapabilityAdmissionSnapshotV01,admission)
    require(not firewall.validate_capability_admission_snapshot_v01(snapshot) and not firewall.validate_bound_capability_invocation_v01(inv,snapshot)
        and not firewall.validate_capability_execution_result_v01(result,inv,snapshot),'quote_native_result')
    user=payload['user_selection']
    triple=tuple(plain_root_record(cls,user[key]) for cls,key in ((roots.RootDecisionKernelV01,'kernel'),
        (roots.RootDecisionInputV01,'inputs'),(roots.RootDecisionResultV01,'result')))
    claim=claim_value(triple)
    require(triple[2].decision=='ACCEPT' and claim['semantic_ref']==semantics['semantic_ref']
        and claim['plan_id']==selected and claim['amount_minor']==plan['price_minor']
        and quote['result']['result_id'] in claim['work_result_refs'],'separate_root_consumption')
    require(value['summary']['consumed']['root_decision']==triple[2].decision_id
        and value['summary']['consumed']['quote']==payload['quote']['results'],'retained_summary_binding')
    replay=e.replay_v01(value['sealed'],expected_manifest_hash=value['sealed']['manifest_hash'])
    require(replay['replay_status']=='PASS','retained_replay')
    return dict(row='N4-07',origin='RETAINED_G6A4_LIVE',projections=4,upstream_links=6,new_model_calls=0,
        private_markers_exported=False,selected_plan=selected,downstream_result=quote['result']['result_id'],root_decision=triple[2].decision_id,
        limitations='Retained adapter evidence, not packet interception or certification of model prose.')

def imports():
    for n,m in tuple(sys.modules.items()):
        if getattr(m,'__file__',None) and n.startswith(('hedgehog.','demo.','tests.')):
            require(Path(m.__file__).resolve().is_relative_to(ROOT),'foreign_import:'+n)
    return {n:dict(path=str(Path(m.__file__).resolve().relative_to(ROOT)),sha256=hashlib.sha256(Path(m.__file__).read_bytes()).hexdigest())
        for n,m in tuple(sys.modules.items()) if getattr(m,'__file__',None) and n.startswith(('hedgehog.','demo.','tests.'))
        and Path(m.__file__).resolve().is_relative_to(ROOT)}

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('mode',choices=('avf','reuse','policy','privacy','supplied'));p.add_argument('--output',type=Path,required=True)
    p.add_argument('--evidence',type=Path)
    p.add_argument('--policy-time',type=int,help='Explicit logical decision time for a retained controlled input.')
    a=p.parse_args(argv);a.output.mkdir(parents=True,exist_ok=False)
    save(a.output/'start.json',dict(mode=a.mode,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()))
    try:
        if a.mode=='supplied':
            require(a.evidence is not None,'evidence_required')
            def consume():
                return {name:check(decode(read(a.evidence/name/'witness.json'))) for name,check in CHECKS.items()}
            observation=observed(a.output,'pure',pure_functions(),consume)
            check_counts(observation['observation'],{})
            save(a.output/'result.json',observation['value']);save(a.output/'imports.json',imports());return
        value=(collect_policy(a.output,a.policy_time) if a.mode=='policy' else privacy_inputs() if a.mode=='privacy'
            else {'avf':collect_avf,'reuse':collect_reuse}[a.mode](a.output))
        save(a.output/'witness.json',encode(value))
        loaded=decode(read(a.output/'witness.json'))
        checked=observed(a.output,'pure',pure_functions(),lambda:CHECKS[a.mode](loaded))
        check_counts(checked['observation'],{})
        save(a.output/'checked.json',checked['value']);save(a.output/'imports.json',imports())
    except Exception as error:
        chain=[];seen=set();current=error
        while current is not None and id(current) not in seen:
            seen.add(id(current));chain.append(dict(type=type(current).__name__,args=repr(current.args),
                traceback=[dict(file=t.filename,line=t.lineno,function=t.name,source=t.line) for t in traceback.extract_tb(current.__traceback__)]))
            current=current.__cause__ or current.__context__
        save(a.output/'failure.json',dict(chain=chain));save(a.output/'imports.json',imports());raise
    print(json.dumps(dict(mode=a.mode,status='WITNESS_COLLECTED',witness_sha256=hashlib.sha256((a.output/'witness.json').read_bytes()).hexdigest())))
CHECKS=dict(avf=check_avf,reuse=check_reuse,policy=check_policy,privacy=check_privacy)
def pure_functions():
    from hedgehog.domains.testflix.semantic_roles_v01 import ControlledRolesV01
    from hedgehog.domains.testflix.live_semantic_adapter_v01 import LiveSemanticProviderV01
    return dict(root=roots.decide_root_v01,work=host.execute_admitted_pure_work_v01,
        native=native.native_work,effect=firewall.execute_mock_effect_v01,bound_effect=firewall.execute_bound_effect_v01,
        write=LocalDRS.write_record,read=LocalDRS.read_record,descent=memory.execute_local_memory_descent_v01,
        controlled=ControlledRolesV01.respond_v01,live=LiveSemanticProviderV01.respond_v01)
if __name__=='__main__':main()
