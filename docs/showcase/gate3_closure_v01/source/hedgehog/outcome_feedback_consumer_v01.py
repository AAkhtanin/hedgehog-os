"""Current evidence-only history projection, ordinary Root review and pure Work.

No domain import, effect dispatch, learned permission or replacement AVF engine.
"""
from dataclasses import dataclass, asdict
from decimal import Decimal, ROUND_HALF_EVEN
import hashlib
import json
import math

from hedgehog import avf_v02 as avf
from hedgehog import outcome_calibration_v01 as cal
from hedgehog.kernel import abi_v01 as abi, semantic_work_v01 as sw
from hedgehog.kernel import root_decision_v01 as roots, trust_model_v01 as trust
from hedgehog.kernel import work_composition_v01 as work
from hedgehog.kernel import execution_mode_router_v01 as router
from hedgehog.kernel.integrity_replay_v01 import canonical_json_bytes_v01 as canonical
from hedgehog.kernel.integrity_replay_v01 import domain_separated_sha256_hex_v01


def require(condition, reason):
    if not condition: raise ValueError(reason)


def identity(domain, value):
    return domain_separated_sha256_hex_v01(domain='g34:'+domain,payload=canonical(value))


def ordinary_review_v01(*, root, transaction, candidates, selected, scores, evidence_ref,
                        now, predicate, required=(), provided=(), subjects=None):
    """Build the same public multi-candidate packet consumed by ordinary Root."""
    require(type(now) is int and candidates and selected in candidates,'g34_review_input')
    subjects = subjects or {key:key for key in candidates}
    request=sw.build_semantic_work_request_v01(request_id='g34:request:'+identity('request',dict(
        root=root,transaction=transaction,candidates=candidates,predicate=predicate,now=now)),
        transaction_id=transaction,target_root_id=root,runtime_topology_ref='g34:bounded_review',
        bounded_context_refs=(evidence_ref,),permitted_actor_ids=('g34:local_validator',),
        permitted_contribution_modes=('DETERMINISTIC',),requested_subjects=tuple(sorted(set(subjects.values()))),
        required_evidence_classes=('DEPENDENCY_EVIDENCE',),forbidden_claims=('authority_creation',))
    binding=sw.build_evidence_binding_v01(evidence_id='binding:'+evidence_ref,evidence_ref=evidence_ref,
        evidence_class='DEPENDENCY_EVIDENCE',source_component_id='g34:local_validator',
        provenance_ref='g34:independent_sources',evidence_state='PRESENT')
    claims=tuple(sw.build_normalized_claim_v01(claim_id=key,subject=subjects[key],predicate=predicate,
        object_or_value=value,time_envelope_ref='g34:time:'+str(now),provenance_refs=(evidence_ref,),
        evidence_refs=(binding.evidence_id,),confidence_micros=1000000,
        source_role='deterministic_runtime',source_mode='DETERMINISTIC') for key,value in sorted(candidates.items()))
    contribution=sw.build_actor_contribution_v01(contribution_id='g34:contribution:'+request.request_id,
        request_id=request.request_id,actor_id='g34:local_validator',actor_role='deterministic_runtime',
        contribution_mode='DETERMINISTIC',bsep_projection_ref='g34:bounded_review:bsep',scope='g34:current_review',
        bounded_context_refs=(evidence_ref,),claims=claims,evidence_bindings=(binding,),constraint_bindings=(),
        uncertainty_bindings=(),requested_validators=('g34:source_binding',),forbidden_claims_observed=())
    packet=sw.build_root_review_packet_from_contributions_v01(request=request,contributions=(contribution,),
        trust_profiles=trust.build_default_component_trust_profiles_v01())
    kernel=roots.build_root_decision_kernel_v01()
    decision_input=roots.build_root_decision_input_v01(transaction_id=transaction,target_root_id=root,root_review_packet=packet,
        post_vv_bundle=dict(bundle_id=identity('postvv',dict(candidates=candidates,required=required,provided=provided)),
            post_vv_passed=True,validated_candidate_ids=sorted(candidates),rejected_candidate_ids=[],
            required_evidence_refs=[evidence_ref,*required],provided_evidence_refs=[evidence_ref,*provided],hard_failure_reasons=[]),
        gt_advisory=dict(advisory_id='g34:gt:'+identity('ranking',dict(selected=selected,scores=scores)),
            candidate_ids=sorted(candidates),selected_candidate_id=selected,score_micros_by_candidate=scores,
            source_artifact_type='GTAdvisoryReport',source_lifecycle_state='VALIDATED',actor_role='gt',
            attempted_effect='CREATE_ROOT_DECISION',target_artifact_type='RootDecision',advisory_only=True,
            creates_final_output=False,requests_effect=False),
        policy_state=dict(policy_id='g34:bounded_current_review',identity_passed=True,scope_passed=True,hard_policy_passed=True,
            allow_accept=True,conflict_policy='DEFER',no_candidate_policy='NO_UPDATE'),
        permission_state=dict(permission_required=False,user_permission_present=False,permission_scope_valid=True,permission_ref=None),
        temporal_state=dict(temporal_valid=True,expired=False,not_before_satisfied=True,time_envelope_ref='g34:time:'+str(now)),
        conflict_state=dict(material_unresolved_conflict=bool(packet.conflict_set_ids),conflict_set_ids=list(packet.conflict_set_ids)),
        prior_root_state=dict(prior_decision_id=None,prior_decision=None,prior_selected_candidate_id=None))
    result=roots.decide_root_v01(kernel=kernel,decision_input=decision_input)
    require(not roots.validate_root_decision_result_v01(kernel=kernel,decision_input=decision_input,result=result),'g34_root_result')
    return kernel,decision_input,result


def review_to_plain_v01(review):
    return dict(kernel=roots.root_decision_kernel_to_plain_dict_v01(review[0]),
        input=roots.root_decision_input_to_plain_dict_v01(review[1]),result=roots.root_decision_result_to_plain_dict_v01(review[2]))


def current_context_v01(source, *, root, transaction, policy_ref):
    """Independent current source, not context recovered from a supplied report."""
    report=router.validate_execution_mode_source_context_v01(source)
    require(report.validation_status=='PASS','g34_current_source_invalid')
    require(transaction=='transaction:'+source.business_request_context_packet['request_id'],'g34_current_transaction')
    require(type(root) is str and root and type(policy_ref) is str and policy_ref,'g34_current_scope')
    return dict(root=root,transaction=transaction,policy_ref=policy_ref,domain=source.business_request_context_packet['domain'],
        source_id=identity('current_source',dict(business=source.business_request_context_packet,
            bsep=source.bsep_packet,route=source.bsep_route_context_packet)),
        evaluation_time=source.g2a_evaluation_time,evaluation_source=source.g2a_evaluation_time_source,
        evaluation_context=source.g2a_evaluation_context_id,bsep_ref=source.bsep_packet['packet_id'])


@dataclass(frozen=True, slots=True)
class CurrentReviewContractV01:
    """Application-supplied finite contract, separate from candidate projections."""
    canonical: bytes

    def to_plain_data(self):
        from . import outcome_feedback_v01 as feedback
        require(type(self.canonical) is bytes and len(self.canonical)<=524288,'g34_contract_bound')
        v=json.loads(self.canonical)
        require(canonical(v)==self.canonical and set(v)=={'profile','context','claims','checks','role','mandatory','contract_id','check_request'},'g34_contract_shape')
        require(v['profile']=='G34_CURRENT_REVIEW_CONTRACT_V01' and v['role'] in ('MAIN','EVIDENCE_CHECK'),'g34_contract_profile')
        require(v['mandatory']==['CURRENT_SOURCE','EXACT_PURE_MATERIAL','CURRENT_ROOT'],'g34_mandatory_checks')
        require(type(v['claims']) is dict and 1<=len(v['claims'])<=8 and set(v['checks'])==set(v['claims']),'g34_contract_claims')
        for claim in v['claims'].values():
            require(set(claim)=={'operation','definition_id','material_sha256','observation_refs','subject','history_key','claim_id'},'g34_claim_shape')
            require(set(claim['subject'])==set(feedback._SUBJECT_FIELDS) and set(claim['history_key'])==set(feedback._HISTORY_FIELDS),'g34_claim_keys')
            require(all(type(x) is str and x for x in claim['subject'].values()),'g34_claim_subject')
            require(claim['subject']['local_root_scope_id']==v['context']['root']
                and claim['subject']['policy_semantics_version']==v['context']['policy_ref']
                and claim['subject']['domain_scope_id']==v['context']['domain'],'g34_claim_scope')
            require(claim['claim_id']==identity('current_claim',{k:x for k,x in claim.items() if k!='claim_id'}),'g34_claim_identity')
        for candidate,check in v['checks'].items():
            if check is None:continue
            require(type(check) is dict and set(check)=={'profile','root','target_claim_id','target_subject','observation_refs',
                'task_inputs_sha256','epoch','evaluated_at','policy_ref','operation','definition_id','material','result_facts','check_id'},'g34_check_shape')
            require(check['profile']=='G34_BOUNDED_CURRENT_ADEQUACY_V01' and
                check['check_id']==identity('bounded_check',{k:x for k,x in check.items() if k!='check_id'}),'g34_check_profile')
            claim=v['claims'][candidate]
            require(check['target_claim_id']==claim['claim_id'] and check['target_subject']==claim['subject']
                and check['observation_refs']==claim['observation_refs'] and check['root']==v['context']['root']
                and check['evaluated_at']==v['context']['evaluation_time'] and check['policy_ref']==v['context']['policy_ref'],'g34_check_scope')
        if v['role']=='MAIN':require(v['check_request'] is None,'g34_main_contract_role')
        else:
            check=v['check_request']
            require(type(check) is dict and check['check_id']==identity('bounded_check',{k:x for k,x in check.items() if k!='check_id'}),
                'g34_fixed_check_request')
            require(v['context']['transaction']=='transaction:g34:check:'+check['check_id']
                and v['context']['root']==check['root'] and v['context']['evaluation_time']==check['evaluated_at']
                and v['context']['policy_ref']==check['policy_ref'] and len(v['claims'])==1
                and all(x is None for x in v['checks'].values()),'g34_fixed_check_context')
            claim=next(iter(v['claims'].values()))
            require(claim['operation']==check['operation'] and claim['definition_id']==check['definition_id']
                and claim['material_sha256']==hashlib.sha256(canonical(check['material'])).hexdigest()
                and claim['observation_refs']==check['observation_refs'],'g34_fixed_check_material')
        require(v['contract_id']==identity('review_contract',{k:x for k,x in v.items() if k!='contract_id'}),'g34_contract_identity')
        return v


def build_current_review_contract_v01(*, source_context, root, transaction, policy_ref, claims, checks, role='MAIN', check_request=None):
    value=dict(profile='G34_CURRENT_REVIEW_CONTRACT_V01',context=current_context_v01(source_context,root=root,
        transaction=transaction,policy_ref=policy_ref),claims=claims,checks=checks,role=role,
        mandatory=['CURRENT_SOURCE','EXACT_PURE_MATERIAL','CURRENT_ROOT'],check_request=check_request)
    value['contract_id']=identity('review_contract',value)
    contract=CurrentReviewContractV01(canonical(value));contract.to_plain_data();return contract


@dataclass(frozen=True, slots=True)
class CurrentAdvisoryProjectionV01:
    canonical: bytes

    def to_plain_data(self):
        require(type(self.canonical) is bytes and len(self.canonical)<=524288,'g34_projection_bound')
        value=json.loads(self.canonical)
        require(set(value)=={'profile','projection_id','bridge_ref','rows','selected','trust','history_ref','evaluated_at','contract_id','context'},'g34_projection_shape')
        require(value['profile']=='G34_CURRENT_ADVISORY_V01' and canonical(value)==self.canonical,'g34_projection_profile')
        require(type(value['evaluated_at']) is int and 0<=value['evaluated_at']<=253402300799,'g34_projection_time')
        require(type(value['bridge_ref']) is str and 0<len(value['bridge_ref'])<=4096,'g34_projection_bridge')
        require(value['history_ref'] is None or type(value['history_ref']) is str and len(value['history_ref'])==64,'g34_projection_history')
        require(type(value['rows']) is list and 1<=len(value['rows'])<=8,'g34_projection_rows')
        for row in value['rows']:
            require(type(row) is dict and set(row)=={'candidate_id','base_fp','prior_fp','adjusted_fp','score_micros',
                'eligible','base_field','base_decimal','prior_ref','trust','subject_status','claim_id'},'g34_projection_row_shape')
            require(type(row['candidate_id']) is str and 0<len(row['candidate_id'])<=4096
                and type(row['eligible']) is bool,'g34_projection_candidate')
            require(type(row['base_fp']) is int and 0<=row['base_fp']<=cal.Q
                and type(row['prior_fp']) is int and -cal.Q<=row['prior_fp']<=cal.Q,'g34_projection_score')
            require(row['base_field']=='score_explanation.final_avf_score' and type(row['base_decimal']) is str
                and 0<len(row['base_decimal'])<=64,'g34_projection_base')
            require(row['prior_ref'] is None or type(row['prior_ref']) is str and len(row['prior_ref'])==64,'g34_projection_prior')
            cal.GTTrustAtV01(canonical(row['trust']))
            require(row['subject_status'] in ('MATCHED','COLD_OR_NONMATCHING'),'g34_subject_status')
            if row['eligible']:
                require(type(row['adjusted_fp']) is int and 0<=row['adjusted_fp']<=cal.Q
                    and type(row['score_micros']) is int and 0<=row['score_micros']<=1000000,'g34_projection_adjusted')
            else: require(row['adjusted_fp'] is None and row['score_micros'] is None,'g34_masked_projection')
        ids=[row['candidate_id'] for row in value['rows']]
        require(len(ids)==len(set(ids)) and value['selected'] in [r['candidate_id'] for r in value['rows'] if r['eligible']],
            'g34_projection_selection')
        if value['trust'] is not None: cal.GTTrustAtV01(canonical(value['trust']))
        require(value['projection_id']==identity('advisory',{k:v for k,v in value.items() if k!='projection_id'}),'g34_projection_identity')
        return value


def build_current_advisory_v01(*, candidates, history_keys, opened_history, bridge, evaluated_at, contract, source_context):
    """Actual AVF output is the base. History cannot re-enable a hardmasked row."""
    require(type(candidates) is tuple and 1<=len(candidates)<=8,'g34_candidate_bound')
    require(set(history_keys)=={c.candidate_id for c in candidates},'g34_candidate_keys')
    require(type(contract) is CurrentReviewContractV01,'g34_review_contract_required')
    policy=contract.to_plain_data();ctx=policy['context']
    require(ctx==current_context_v01(source_context,root=ctx['root'],transaction=ctx['transaction'],policy_ref=ctx['policy_ref'])
        and evaluated_at==ctx['evaluation_time'],'g34_current_context_changed')
    require(bridge.owner_root_id==ctx['root'] and bridge.transaction_id==ctx['transaction'],'g34_current_bridge_scope')
    from . import outcome_feedback_v01 as feedback
    envelope=abi.kernel_artifact_to_plain_dict_v01(bridge)['time_envelope']
    require(envelope['pt_created_at']==feedback._utc(evaluated_at) and envelope['kt_asof']==feedback._utc(evaluated_at)
        and cal._iso_epoch(envelope['valid_from'])<=evaluated_at<cal._iso_epoch(envelope['valid_to']),'g34_current_bridge_time')
    require(set(policy['claims'])==set(history_keys) and all(history_keys[k]==v['history_key'] for k,v in policy['claims'].items()),'g34_contract_history_keys')
    if opened_history is not None:
        from .outcome_feedback_history_v01 import OutcomeHistoryV01
        require(type(opened_history.get('store')) is OutcomeHistoryV01,'g34_independent_history_store')
        opened_history['store'].validate_opened_v01(opened_history,bridge=bridge,evaluation_time=evaluated_at)
    reports=avf.evaluate_avf_candidates_v02(avf.AVFEvaluationInputV02(
        evaluation_id='g34:'+bridge.artifact_id,resolver_mode='CURRENT_CONTEXT',candidates=candidates))
    prior=opened_history['prior'] if opened_history else None
    rows=[]
    for report in reports.decision_reports:
        valid,reasons=avf.validate_avf_decision_report_v02(report)
        require(valid and not reasons,'g34_avf_report')
        base=report.score_explanation.final_avf_score
        require(type(base) in (int,float) and math.isfinite(base) and 0<=base<=1,'g34_avf_base')
        fp=int((Decimal(str(base))*Decimal(cal.Q)).to_integral_value(rounding=ROUND_HALF_EVEN))
        usable=prior is not None and prior['history_key']==history_keys[report.candidate_id]
        claim=policy['claims'][report.candidate_id]
        matched=opened_history is not None and opened_history['trust']['subject_key']==claim['subject']
        advice=opened_history['trust'] if matched else cal.evaluate_gt_trust_at_v01(None,evaluation_time=evaluated_at).to_plain_data()
        p=prior['prior_fp'] if usable else 0
        adjusted,micros=cal.adjusted_avf_score_v01(fp,p)
        eligible=report.hard_mask.hard_mask_value!=0
        rows.append(dict(candidate_id=report.candidate_id,base_fp=fp,prior_fp=p,
            adjusted_fp=adjusted if eligible else None,score_micros=micros if eligible else None,
            eligible=eligible,base_field='score_explanation.final_avf_score',
            base_decimal=str(base),avf_report=asdict(report),prior_ref=prior['prior_id'] if usable else None,
            trust=advice,subject_status='MATCHED' if matched else 'COLD_OR_NONMATCHING',claim_id=claim['claim_id']))
    # Float-free canonical projection retains the exact decimal AVF source value.
    report_evidence={row['candidate_id']:row.pop('avf_report') for row in rows}
    eligible=sorted((row for row in rows if row['eligible']),key=lambda row:(-row['adjusted_fp'],row['candidate_id']))
    require(bool(eligible),'g34_no_eligible_candidate')
    material=dict(profile='G34_CURRENT_ADVISORY_V01',bridge_ref=bridge.artifact_id,rows=rows,selected=eligible[0]['candidate_id'],
        trust=eligible[0]['trust'],history_ref=opened_history['snapshot_id'] if opened_history else None,evaluated_at=evaluated_at,
        contract_id=policy['contract_id'],context=ctx)
    material['projection_id']=identity('advisory',material)
    return CurrentAdvisoryProjectionV01(canonical(material)),report_evidence


def validate_current_advisory_v01(value, **trusted_inputs):
    try:
        require(type(value) is CurrentAdvisoryProjectionV01,'g34_projection_type')
        value.to_plain_data()
        expected,_=build_current_advisory_v01(**trusted_inputs)
        require(value.canonical==expected.canonical,'g34_advisory_source_mismatch')
        return ()
    except (ValueError,TypeError,KeyError,AttributeError) as error: return (str(error),)


def current_check_receipt_bridge_v01(*, check, receipt, current_bridge):
    """Validate the original invocation; reference it without rebasing its ID/time."""
    require(check is not None,'g34_contract_offers_no_check')
    from . import outcome_feedback_v01 as feedback
    require(check['check_id']==identity('bounded_check',{k:v for k,v in check.items() if k!='check_id'}),'g34_check_identity')
    require(current_bridge.owner_root_id==check['root'] and
        abi.kernel_artifact_to_plain_dict_v01(current_bridge)['time_envelope']['pt_created_at']==feedback._utc(check['evaluated_at']),
        'g34_check_current_bridge')
    program,results,common,host_map=receipt
    artifact=work.work_program_result_to_artifact_v01(program,results,host_map=host_map,**common)
    require(len(results)==1 and all(r.status=='COMPLETED' for r in results),'g34_additional_work_incomplete')
    proposal=abi.kernel_artifact_to_plain_dict_v01(common['semantic_proposal'])
    require(proposal['payload'].get('check_request')==check and artifact.owner_root_id==check['root']
        and common['source_context'].g2a_evaluation_time==check['evaluated_at'],'g34_obligation_receipt_binding')
    require(len(program.candidate.items)==1,'g34_check_item_count')
    require(program.candidate.task_id=='g34:check:'+check['check_id'],'g34_check_executed_task_binding')
    item=program.candidate.items[0]
    require(item.definition_id==check['definition_id'] and item.owning_root_id==check['root']
        and _literal_material_v01(item)==check['material'],'g34_check_actual_input')
    require(proposal['payload']['operation']==check['operation'],'g34_check_operation')
    output=json.loads(next(v.value for v in results[0].result.output if v.parameter_name=='material'))
    require(output==check['result_facts'],'g34_check_actual_output')
    payload=dict(profile='G34_CURRENT_CHECK_RECEIPT_BRIDGE_V01',check=check,
        original_ref=asdict(abi.kernel_artifact_to_canonical_ref_v01(artifact)),
        original_envelope=abi.kernel_artifact_to_plain_dict_v01(artifact)['time_envelope'],result_facts=output,
        current_transaction_ref=current_bridge.transaction_id,current_bridge_ref=current_bridge.artifact_id)
    return abi.build_kernel_artifact_v01(abi_version='v1.0',artifact_id='g34:check_bridge:'+identity('check_receipt',payload),
        artifact_type='SemanticEvidence',schema_version='v1',transaction_id=current_bridge.transaction_id,
        owner_root_id=current_bridge.owner_root_id,source_component='g34_check_receipt',authority_class='EVIDENCE_ONLY',lifecycle_state='VALIDATED',
        payload=payload,trace_refs=(check['check_id'],),parent_refs=(current_bridge.artifact_id,),
        time_envelope=abi.kernel_artifact_to_plain_dict_v01(current_bridge)['time_envelope'])


def validate_current_causal_proof_v01(*, projection, trusted_inputs, artifacts, causal_refs, program, common):
    try:
        require(not validate_current_advisory_v01(projection,**trusted_inputs),'g34_causal_current_projection')
        require(program==work.materialize_work_program_v01(program.candidate,**common),'g34_causal_native_program')
        require(all(ref in causal_refs for ref in program.source_bindings),'g34_causal_native_refs_missing')
        require(not abi.validate_causal_consumption_bundle_v01(artifacts=artifacts,causal_refs=causal_refs),'g34_causal_bundle')
        by_id={v.artifact_id:v for v in artifacts};value=projection.to_plain_data()
        require(abi.kernel_artifact_to_plain_dict_v01(by_id[value['bridge_ref']])==
            abi.kernel_artifact_to_plain_dict_v01(trusted_inputs['bridge']),'g34_causal_source_substitution')
        advisory=by_id['g34:advisory:'+value['projection_id']]
        require(abi.kernel_artifact_to_plain_dict_v01(advisory)['payload']==dict(advisory=value),'g34_causal_numeric_substitution')
        return ()
    except (ValueError,KeyError,TypeError) as error:return (str(error),)


def review_current_advisory_v01(*, projection, trusted_inputs, root, transaction, candidate_materials,
                               additional_receipt=None):
    require(not validate_current_advisory_v01(projection,**trusted_inputs),'g34_current_projection')
    value=projection.to_plain_data()
    policy=trusted_inputs['contract'].to_plain_data()
    require(value['context']['root']==root and value['context']['transaction']==transaction,'g34_review_current_scope')
    require(set(candidate_materials)=={row['candidate_id'] for row in value['rows']},'g34_current_materials')
    require(candidate_materials==policy['claims'],'g34_review_claim_substitution')
    candidates={row['candidate_id']:dict(candidate_materials[row['candidate_id']],advisory_ref=value['projection_id'],
        bridge_ref=value['bridge_ref']) for row in value['rows'] if row['eligible']}
    required=();provided=()
    if policy['role']=='MAIN' and value['trust']['review_recommended']:
        check=policy['checks'][value['selected']]
        for claim in candidates.values():claim['review_requirement']=dict(recommended=True,offered=check is not None,
            check_ref=check['check_id'] if check is not None else None)
        required=('g34:required_current_check',)
        if additional_receipt is not None:
            artifact=current_check_receipt_bridge_v01(check=check,receipt=additional_receipt,current_bridge=trusted_inputs['bridge'])
            for claim in candidates.values():
                claim['additional_receipt_ref']=asdict(abi.kernel_artifact_to_canonical_ref_v01(artifact))
            provided=required
    scores={row['candidate_id']:row['score_micros'] for row in value['rows'] if row['eligible']}
    return ordinary_review_v01(root=root,transaction=transaction,candidates=candidates,selected=value['selected'],scores=scores,
        evidence_ref=value['projection_id'],now=value['evaluated_at'],predicate='g34_current_pure_work',required=required,provided=provided)


def _literal_material_v01(item):
    require(type(item) is work.WorkItemV01 and len(item.inputs)==1,'g34_work_input_shape')
    binding=item.inputs[0]
    require(binding.input_field=='material' and type(binding.source) is work.WorkLiteralV01,'g34_work_literal_required')
    record=binding.source.value
    require(record.parameter_name=='material' and record.value_type=='TEXT','g34_work_literal_type')
    return json.loads(record.value)


def execute_reviewed_pure_work_v01(*, review, projection, source_context, semantic_proposal,
                                  catalogue, host, item, material, budget, task_id, trusted_inputs,
                                  additional_receipt=None):
    """No action candidate: current accepted proposal must bind this exact material."""
    kernel,inputs,result=review
    require(not validate_current_advisory_v01(projection,**dict(trusted_inputs,source_context=source_context)),'g34_execution_current_projection')
    policy=trusted_inputs['contract'].to_plain_data();ctx=policy['context']
    require(inputs.target_root_id==ctx['root']==item.owning_root_id and inputs.transaction_id==ctx['transaction'],'g34_execution_scope')
    current=host.current_sources
    require(host.owning_root_id==ctx['root'] and (current.evaluation_time,current.evaluation_time_source,current.evaluation_context_id)==
        (ctx['evaluation_time'],ctx['evaluation_source'],ctx['evaluation_context']),'g34_execution_host_context')
    expected=review_current_advisory_v01(projection=projection,trusted_inputs=trusted_inputs,root=ctx['root'],transaction=ctx['transaction'],
        candidate_materials=policy['claims'],additional_receipt=additional_receipt)
    require(review_to_plain_v01(review)==review_to_plain_v01(expected),'g34_execution_review_substitution')
    require(not roots.validate_root_decision_result_v01(kernel=kernel,decision_input=inputs,result=result)
        and result.decision=='ACCEPT','g34_work_root_refusal')
    require(result.selected_candidate_id==projection.to_plain_data()['selected'],'g34_work_selection')
    plain=roots.root_decision_input_to_plain_dict_v01(inputs)
    claims=plain['root_review_packet']['synthesis_proposal']['normalized_claims']
    selected=next(row['object_or_value'] for row in claims if row['claim_id']==result.selected_candidate_id)
    require(_literal_material_v01(item)==material and selected['material_sha256']==hashlib.sha256(canonical(material)).hexdigest()
        and selected['definition_id']==item.definition_id,'g34_work_material_changed')
    require(selected['advisory_ref']==projection.to_plain_data()['projection_id'],'g34_work_advisory')
    proposal=abi.kernel_artifact_to_plain_dict_v01(semantic_proposal)
    receipt_ref=selected.get('additional_receipt_ref')
    receipt_id=receipt_ref['artifact_id'] if receipt_ref else None
    expected_parents=(source_context.bsep_packet['packet_id'],projection.to_plain_data()['bridge_ref'],
        'g34:advisory:'+projection.to_plain_data()['projection_id'])+((receipt_id,) if receipt_id else ())
    require(semantic_proposal.owner_root_id==ctx['root'] and semantic_proposal.transaction_id==ctx['transaction']
        and proposal['payload']['advisory_ref']==selected['advisory_ref']
        and proposal['payload']['bridge_ref']==projection.to_plain_data()['bridge_ref']
        and proposal['payload']['root_decision_ref']==result.decision_id
        and proposal['payload']['material']==material and proposal['payload']['operation']==selected['operation']
        and proposal['payload']['check_receipt_ref']==receipt_id
        and semantic_proposal.parent_refs==expected_parents,'g34_proposal_consumption')
    from . import outcome_feedback_v01 as feedback
    require(proposal['time_envelope']['pt_created_at']==feedback._utc(ctx['evaluation_time'])
        and proposal['time_envelope']['kt_asof']==feedback._utc(ctx['evaluation_time']),'g34_proposal_time')
    common=dict(catalogue=catalogue,source_context=source_context,semantic_proposal=semantic_proposal)
    candidate=work.build_work_program_candidate_v01(task_id=task_id,previous_revision_id=None,intent_ref='g34:intent:'+task_id,
        bsep_ref=source_context.bsep_packet['packet_id'],semantic_proposal_ref=semantic_proposal.artifact_id,
        catalogue_revision=0,budget=budget,items=(item,),trigger_evidence_refs=(),**common)
    program=work.materialize_work_program_v01(candidate,**common)
    results=work.advance_work_program_v01(program,host_map={inputs.target_root_id:host},**common)
    artifact=work.work_program_result_to_artifact_v01(program,results,host_map={inputs.target_root_id:host},**common)
    require(len(results)==1 and results[0].status=='COMPLETED','g34_work_incomplete')
    return program,results,artifact,common
