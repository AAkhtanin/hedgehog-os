import json


from hedgehog import outcome_feedback_v01 as feedback, outcome_calibration_v01 as cal


from hedgehog import action_commit_packet_v02 as actions


from hedgehog.kernel import abi_v01 as abi, root_decision_v01 as roots, semantic_work_v01 as sw, trust_model_v01 as trust


from hedgehog.kernel import effect_firewall_v01 as firewall, transition_registry_v01 as transitions


from hedgehog.incident_atlas_v01 import canonical_v01 as canonical, digest_v01 as digest, require_v01 as require


from hedgehog.incident_atlas_history_v01 import validate_snapshot_v01, validate_epoch_v01, validate_recording_review_v01


from hedgehog.domains.ephemeral_workspace import incident_atlas_work_v01 as native


def validate_review_v01(value):
    kernel, inputs, result=feedback.g35_record_from_plain_v01(value)
    require(not roots.validate_root_decision_result_v01(kernel=kernel,decision_input=inputs,result=result),'atlas_workspace_root_result')
    return inputs,result


def validate_work_v01(value):
    records = feedback.g35_validate_work_records_v01(value['results'], value['admissions'])
    program = feedback.g35_record_from_plain_v01(value['program'])
    feedback._g35_checked_work_relation_v01(abi.kernel_artifact_to_plain_dict_v01(program.topology_artifact), value['artifact'], records, value['admissions'])
    ri, rr = validate_review_v01(value['output_review'])
    require(rr.decision=='ACCEPT' and rr.selected_candidate_id==value['artifact']['artifact_id'], 'atlas_workspace_work_review')
    claims = roots.root_decision_input_to_plain_dict_v01(ri)['root_review_packet']['synthesis_proposal']['normalized_claims']
    require(len(claims)==1 and claims[0]['object_or_value']==value['output'] and ri.root_review_packet.runtime_topology_ref==program.topology_artifact.artifact_id, 'atlas_workspace_output_consumption')
    material = json.loads(native.values(records[0].invocation.inputs)['material'])
    output = json.loads(native.values(records[0].result.output)['material'])
    require(material==value['material'] and output==value['output']==native.evaluate_v01(material, provenance=value['projection']['selected']=='provenance'), 'atlas_workspace_work_material')
    require(value['artifact']['owner_root_id']==native.ROOT and value['artifact']['transaction_id']==rr.transaction_id, 'atlas_workspace_work_owner')
    current_input,current_result=validate_review_v01(value['current_review'])
    selected=value['projection']['selected']
    raw=roots.root_decision_input_to_plain_dict_v01(current_input)
    selected_claim=next(c['object_or_value'] for c in raw['root_review_packet']['synthesis_proposal']['normalized_claims'] if c['claim_id']==selected)
    require(current_result.decision=='ACCEPT' and current_result.selected_candidate_id==selected
        and current_result.transaction_id==rr.transaction_id and current_result.target_root_id==native.ROOT,'atlas_workspace_current_work_review')
    require(selected_claim['advisory_ref']==value['projection']['projection_id'] and selected_claim['bridge_ref']==value['bridge']['artifact_id']
        and selected_claim['material_sha256']==digest(material) and selected_claim['definition_id']==records[0].invocation.definition_id,'atlas_workspace_current_claim')
    proposal=feedback.g35_validate_artifact_v01(value['proposal']); payload=value['proposal']['payload']
    require(payload['material']==material and payload['root_decision_ref']==current_result.decision_id
        and payload['advisory_ref']==selected_claim['advisory_ref'] and payload['bridge_ref']==selected_claim['bridge_ref']
        and payload['operation']==selected_claim['operation'] and program.candidate.semantic_proposal_ref==proposal.artifact_id,'atlas_workspace_program_consumption')
    if value['additional'] is not None:
        validate_work_v01(value['additional'])
        check=value['contract']['checks'][selected]
        extra=value['additional']; receipt=value['receipt_bridge']
        feedback.g35_validate_artifact_v01(receipt)
        require(extra['proposal']['payload']['check_request']==check and extra['material']==check['material']
            and extra['output']==check['result_facts'] and receipt['payload']['result_facts']==extra['output']
            and receipt['payload']['original_ref']['artifact_id']==extra['artifact']['artifact_id']
            and payload['check_receipt_ref']==receipt['artifact_id'] and selected_claim['additional_receipt_ref']['artifact_id']==receipt['artifact_id'], 'atlas_workspace_required_check')


def validate_current_projection_v01(value, snapshot=None, head=None):
    """Pure numerical/source reconstruction, not a re-opened live history handle."""
    from dataclasses import asdict
    from decimal import Decimal, ROUND_HALF_EVEN
    from types import SimpleNamespace
    from hedgehog import avf_v02 as avf, outcome_feedback_consumer_v01 as consumer
    from hedgehog.incident_atlas_history_v01 import review_from_plain_v01
    contract=consumer.CurrentReviewContractV01(canonical(value['contract'])).to_plain_data()
    projection=consumer.CurrentAdvisoryProjectionV01(canonical(value['projection'])).to_plain_data()
    ctx=contract['context']; material=value['material']
    clock=SimpleNamespace(evaluation_time=ctx['evaluation_time'], evaluation_time_source=ctx['evaluation_source'],evaluation_context_id=ctx['evaluation_context'])
    source=native.current_source_v01(ctx['transaction'].removeprefix('transaction:'),clock,material)
    require(ctx==consumer.current_context_v01(source,root=native.ROOT,transaction=ctx['transaction'],policy_ref=native.subject_v01(material)[0]['policy_semantics_version']), 'atlas_workspace_current_source')
    require(canonical(value['source'])==canonical({k:getattr(source,k) for k in value['source']}), 'atlas_workspace_saved_source')
    require(projection['context']==ctx and projection['contract_id']==contract['contract_id'], 'atlas_workspace_current_contract')
    strategies=tuple(contract['claims'])
    candidates=tuple(avf.AVFCandidateV02(candidate_id=s,candidate_label='atlas.workspace.'+s,base_viability_score=0.79 if s=='constraint' else 0.80,ttl_valid=True) for s in strategies)
    reports=avf.evaluate_avf_candidates_v02(avf.AVFEvaluationInputV02(evaluation_id='g34:'+value['bridge']['artifact_id'],resolver_mode='CURRENT_CONTEXT',candidates=candidates))
    require(canonical(value['reports'])==canonical({r.candidate_id:asdict(r) for r in reports.decision_reports}), 'atlas_workspace_actual_avf')
    prior=snapshot['prior'] if snapshot else None
    update=cal.GTTrustUpdateV01(canonical(snapshot['updates'][-1])) if snapshot else None
    for row in projection['rows']:
        strategy=row['candidate_id'];subject,key=native.subject_v01(material,strategy)
        claim=contract['claims'][strategy]
        require(claim['subject']==subject and claim['history_key']==key and claim['material_sha256']==digest(material)
            and claim['observation_refs']==[v['observation_id'] for v in material['checks'][0]['observations']], 'atlas_workspace_current_material')
        p=prior['prior_fp'] if prior and key==prior['history_key'] else 0
        report=next(r for r in reports.decision_reports if r.candidate_id==strategy)
        base=report.score_explanation.final_avf_score; fp=int((Decimal(str(base))*cal.Q).to_integral_value(rounding=ROUND_HALF_EVEN))
        adjusted,micros=cal.adjusted_avf_score_v01(fp,p)
        match=bool(snapshot and subject==snapshot['fold']['subject_key'])
        trust=cal.evaluate_gt_trust_at_v01(update if match else None,evaluation_time=projection['evaluated_at']).to_plain_data()
        require(row==dict(candidate_id=strategy,base_fp=fp,prior_fp=p,adjusted_fp=adjusted,score_micros=micros,eligible=report.hard_mask.hard_mask_value!=0,
            base_field='score_explanation.final_avf_score',base_decimal=str(base),prior_ref=prior['prior_id'] if prior and key==prior['history_key'] else None,
            trust=trust,subject_status='MATCHED' if match else 'COLD_OR_NONMATCHING',claim_id=claim['claim_id']), 'atlas_workspace_applied_history')
    winner=sorted((r for r in projection['rows'] if r['eligible']),key=lambda r:(-r['adjusted_fp'],r['candidate_id']))[0]
    require(projection['selected']==winner['candidate_id'] and projection['trust']==winner['trust']
        and projection['history_ref']==(snapshot['snapshot_id'] if snapshot else None), 'atlas_workspace_actual_selection')
    if snapshot:
        discovery=value['discovery']; bridge=value['bridge']; payload=bridge['payload']
        review=review_from_plain_v01(discovery['review'])
        require(review[2].decision=='ACCEPT' and review[2].selected_candidate_id==discovery['plan']['retrieval_plan_id']
            and [v['stage'] for v in discovery['read_audit']]==['DESCRIPTOR','ROOT_APPROVED','PAYLOAD_READ','PUBLIC_OPEN_VALIDATED','NUMERIC_SOURCE_VALIDATED']
            and discovery['read_audit'][1]['decision']==review[2].decision_id, 'atlas_workspace_current_descent_review')
        claims=roots.root_decision_input_to_plain_dict_v01(review[1])['root_review_packet']['synthesis_proposal']['normalized_claims']
        require(len(claims)==1 and claims[0]['object_or_value']==discovery['plan'], 'atlas_workspace_descent_plan')
        require(discovery['payload_sha256']==digest(snapshot) and discovery['opened']==[head['record_id']]
            and payload['head']==head and payload['prior']==prior and payload['descent_id']==discovery['descent']['memory_descent_result_id']
            and payload['current_local_root_ref']==native.ROOT and payload['current_transaction_ref']==ctx['transaction']
            and payload['evaluated_at']==projection['evaluated_at'], 'atlas_workspace_opened_history_binding')

    if value['additional'] is not None: validate_current_projection_v01(value['additional'])


def validate_experience_v01(value):
    exp=value['experience']
    for key in ('observation','before','after'):validate_work_v01(exp[key])
    predictive=feedback.PredictiveOutcomeSourceContextV01(canonical(exp['observation']['predictive']))
    ofe=feedback.OutcomeFeedbackEnvelopeV01(canonical(exp['observation']['feedback']))
    require(not feedback.validate_outcome_feedback_against_sources_v01(ofe,source_bundle=predictive,profile=feedback.PREDICTIVE_SOURCE_PROFILE_ID)
        and exp['observation']['predictive']['result_artifact']==exp['observation']['artifact'],'atlas_workspace_predictive_source')
    event=cal.bind_outcome_feedback_event_v01(ofe,source_bundle=predictive,profile=feedback.PREDICTIVE_SOURCE_PROFILE_ID)
    validate_snapshot_v01(exp['snapshot'],{json.loads(event.feedback_canonical)['feedback_id']:event})
    recording=feedback.g35_record_from_plain_v01(exp['recording_review'])
    validate_recording_review_v01(exp['snapshot'],recording);validate_epoch_v01(exp['snapshot'],exp['head'],recording,exp['storage'])
    validate_current_projection_v01(exp['observation']);validate_current_projection_v01(exp['before'])
    validate_current_projection_v01(exp['after'],exp['snapshot'],exp['head'])
    require(exp['before']['material']==exp['after']['material']==exp['observation']['material']
        and exp['before']['contract']['claims']==exp['after']['contract']['claims']
        and exp['before']['projection']['selected']=='provenance' and exp['after']['projection']['selected']=='constraint'
        and exp['snapshot']['prior']['effective_count']==1 and exp['snapshot']['prior']['prior_fp']>0,'atlas_workspace_effective_history')
    return True
