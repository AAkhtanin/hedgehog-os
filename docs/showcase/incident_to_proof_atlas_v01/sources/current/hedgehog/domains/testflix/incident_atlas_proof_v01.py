"""Pure Testflix saved-relation checks. No Host reconstruction or fresh decisions."""
import json
from hedgehog import outcome_feedback_v01 as feedback, outcome_calibration_v01 as cal
from hedgehog import action_commit_packet_v02 as actions
from hedgehog.kernel import abi_v01 as abi, root_decision_v01 as roots, semantic_work_v01 as sw, trust_model_v01 as trust
from hedgehog.kernel import effect_firewall_v01 as firewall, transition_registry_v01 as transitions
from hedgehog.incident_atlas_v01 import canonical_v01 as canonical, digest_v01 as digest, require_v01 as require
from hedgehog.incident_atlas_history_v01 import validate_snapshot_v01, validate_epoch_v01, validate_recording_review_v01
from hedgehog.domains.testflix import incident_atlas_work_v01 as native
from hedgehog.domains.testflix import contracts_v01 as c, mock_world_v01 as world

def validate_review_v01(value):
    kernel, inputs, result=feedback.g35_record_from_plain_v01(value)
    require(not roots.validate_root_decision_result_v01(kernel=kernel,decision_input=inputs,result=result),'atlas_testflix_root_result')
    return inputs,result

def validate_work_v01(value):
    records = feedback.g35_validate_work_records_v01(value['results'], value['admissions'])
    program = feedback.g35_record_from_plain_v01(value['program'])
    feedback._g35_checked_work_relation_v01(abi.kernel_artifact_to_plain_dict_v01(program.topology_artifact), value['artifact'], records, value['admissions'])
    ri, rr = validate_review_v01(value['output_review'])
    require(rr.decision=='ACCEPT' and rr.selected_candidate_id==value['artifact']['artifact_id'], 'atlas_testflix_work_review')
    claims = roots.root_decision_input_to_plain_dict_v01(ri)['root_review_packet']['synthesis_proposal']['normalized_claims']
    require(len(claims)==1 and claims[0]['object_or_value']==value['output'] and ri.root_review_packet.runtime_topology_ref==program.topology_artifact.artifact_id, 'atlas_testflix_output_consumption')
    material = json.loads(native.values(records[0].invocation.inputs)['material'])
    output = json.loads(native.values(records[0].result.output)['material'])
    require(material==value['material'] and output==value['output']==native.evaluate_v01(material, provenance=value['projection']['selected']=='provenance'), 'atlas_testflix_work_material')
    require(value['artifact']['owner_root_id']==native.ROOT and value['artifact']['transaction_id']==rr.transaction_id, 'atlas_testflix_work_owner')
    current_input,current_result=validate_review_v01(value['current_review'])
    selected=value['projection']['selected']
    raw=roots.root_decision_input_to_plain_dict_v01(current_input)
    selected_claim=next(c['object_or_value'] for c in raw['root_review_packet']['synthesis_proposal']['normalized_claims'] if c['claim_id']==selected)
    require(current_result.decision=='ACCEPT' and current_result.selected_candidate_id==selected
        and current_result.transaction_id==rr.transaction_id and current_result.target_root_id==native.ROOT,'atlas_testflix_current_work_review')
    require(selected_claim['advisory_ref']==value['projection']['projection_id'] and selected_claim['bridge_ref']==value['bridge']['artifact_id']
        and selected_claim['material_sha256']==digest(material) and selected_claim['definition_id']==records[0].invocation.definition_id,'atlas_testflix_current_claim')
    proposal=feedback.g35_validate_artifact_v01(value['proposal']); payload=value['proposal']['payload']
    require(payload['material']==material and payload['root_decision_ref']==current_result.decision_id
        and payload['advisory_ref']==selected_claim['advisory_ref'] and payload['bridge_ref']==selected_claim['bridge_ref']
        and payload['operation']==selected_claim['operation'] and program.candidate.semantic_proposal_ref==proposal.artifact_id,'atlas_testflix_program_consumption')
    if value['additional'] is not None:
        validate_work_v01(value['additional'])
        check=value['contract']['checks'][selected]
        extra=value['additional']; receipt=value['receipt_bridge']
        feedback.g35_validate_artifact_v01(receipt)
        require(extra['proposal']['payload']['check_request']==check and extra['material']==check['material']
            and extra['output']==check['result_facts'] and receipt['payload']['result_facts']==extra['output']
            and receipt['payload']['original_ref']['artifact_id']==extra['artifact']['artifact_id']
            and payload['check_receipt_ref']==receipt['artifact_id'] and selected_claim['additional_receipt_ref']['artifact_id']==receipt['artifact_id'], 'atlas_testflix_required_check')


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
    require(ctx==consumer.current_context_v01(source,root=native.ROOT,transaction=ctx['transaction'],policy_ref=native.subject_v01(material)[0]['policy_semantics_version']), 'atlas_testflix_current_source')
    require(canonical(value['source'])==canonical({k:getattr(source,k) for k in value['source']}), 'atlas_testflix_saved_source')
    require(projection['context']==ctx and projection['contract_id']==contract['contract_id'], 'atlas_testflix_current_contract')
    strategies=tuple(contract['claims'])
    candidates=tuple(avf.AVFCandidateV02(candidate_id=s,candidate_label='atlas.testflix.'+s,base_viability_score=0.79 if s=='constraint' else 0.80,ttl_valid=True) for s in strategies)
    reports=avf.evaluate_avf_candidates_v02(avf.AVFEvaluationInputV02(evaluation_id='g34:'+value['bridge']['artifact_id'],resolver_mode='CURRENT_CONTEXT',candidates=candidates))
    require(canonical(value['reports'])==canonical({r.candidate_id:asdict(r) for r in reports.decision_reports}), 'atlas_testflix_actual_avf')
    prior=snapshot['prior'] if snapshot else None
    update=cal.GTTrustUpdateV01(canonical(snapshot['updates'][-1])) if snapshot else None
    for row in projection['rows']:
        strategy=row['candidate_id'];subject,key=native.subject_v01(material,strategy)
        claim=contract['claims'][strategy]
        require(claim['subject']==subject and claim['history_key']==key and claim['material_sha256']==digest(material)
            and claim['observation_refs']==[v['observation_id'] for v in material['checks'][0]['observations']], 'atlas_testflix_current_material')
        p=prior['prior_fp'] if prior and key==prior['history_key'] else 0
        report=next(r for r in reports.decision_reports if r.candidate_id==strategy)
        base=report.score_explanation.final_avf_score; fp=int((Decimal(str(base))*cal.Q).to_integral_value(rounding=ROUND_HALF_EVEN))
        adjusted,micros=cal.adjusted_avf_score_v01(fp,p)
        match=bool(snapshot and subject==snapshot['fold']['subject_key'])
        trust=cal.evaluate_gt_trust_at_v01(update if match else None,evaluation_time=projection['evaluated_at']).to_plain_data()
        require(row==dict(candidate_id=strategy,base_fp=fp,prior_fp=p,adjusted_fp=adjusted,score_micros=micros,eligible=report.hard_mask.hard_mask_value!=0,
            base_field='score_explanation.final_avf_score',base_decimal=str(base),prior_ref=prior['prior_id'] if prior and key==prior['history_key'] else None,
            trust=trust,subject_status='MATCHED' if match else 'COLD_OR_NONMATCHING',claim_id=claim['claim_id']), 'atlas_testflix_applied_history')
    winner=sorted((r for r in projection['rows'] if r['eligible']),key=lambda r:(-r['adjusted_fp'],r['candidate_id']))[0]
    require(projection['selected']==winner['candidate_id'] and projection['trust']==winner['trust']
        and projection['history_ref']==(snapshot['snapshot_id'] if snapshot else None), 'atlas_testflix_actual_selection')
    if snapshot:
        discovery=value['discovery']; bridge=value['bridge']; payload=bridge['payload']
        review=review_from_plain_v01(discovery['review'])
        require(review[2].decision=='ACCEPT' and review[2].selected_candidate_id==discovery['plan']['retrieval_plan_id']
            and [v['stage'] for v in discovery['read_audit']]==['DESCRIPTOR','ROOT_APPROVED','PAYLOAD_READ','PUBLIC_OPEN_VALIDATED','NUMERIC_SOURCE_VALIDATED']
            and discovery['read_audit'][1]['decision']==review[2].decision_id, 'atlas_testflix_current_descent_review')
        claims=roots.root_decision_input_to_plain_dict_v01(review[1])['root_review_packet']['synthesis_proposal']['normalized_claims']
        require(len(claims)==1 and claims[0]['object_or_value']==discovery['plan'], 'atlas_testflix_descent_plan')
        require(discovery['payload_sha256']==digest(snapshot) and discovery['opened']==[head['record_id']]
            and payload['head']==head and payload['prior']==prior and payload['descent_id']==discovery['descent']['memory_descent_result_id']
            and payload['current_local_root_ref']==native.ROOT and payload['current_transaction_ref']==ctx['transaction']
            and payload['evaluated_at']==projection['evaluated_at'], 'atlas_testflix_opened_history_binding')

    if value['additional'] is not None: validate_current_projection_v01(value['additional'])


def validate_action_v01(value):
    bound=feedback.g35_record_from_plain_v01(value['bound']);packet=bound.canonical_projection
    registry=feedback.g35_record_from_plain_v01(value['registry'])
    pending=feedback.g35_record_from_plain_v01(value['pending_registry'])
    require(actions.validate_native_root_bound_action_commit_packet_v01(bound)[0]
        and actions.validate_action_commit_packet_registry_v02(registry)[0]
        and actions.validate_action_commit_packet_registry_v02(pending)[0],'atlas_testflix_native_history')
    entry=next(v for v in registry.action_packet_lifecycle_entries if v.root_bound_genesis.packet_identity.packet_id==bound.packet_identity.packet_id)
    require(entry.root_bound_genesis==bound,'atlas_testflix_genesis_binding')
    dep=packet.dependency_candidate.dependency_records[0]
    evidence_hash=actions.domain_separated_sha256_hex_v01(domain='testflix.authoritative_dependency.v01',payload=c.canonical_v01(value['evidence']))
    require(dep.content_sha256==evidence_hash,'atlas_testflix_action_material')
    admission=feedback.g35_record_from_plain_v01(value['admission'])
    require(packet.execution_source==admission and not firewall.validate_capability_admission_snapshot_v01(admission),'atlas_testflix_admission')
    review=feedback.g35_record_from_plain_v01(value['root_review']);projection=bound.root_decision_projection
    require(not sw.validate_root_review_packet_v01(request=review['request'],contributions=(review['contribution'],),
        packet=review['review'],trust_profiles=trust.build_default_component_trust_profiles_v01())
        and projection.root_decision_input.root_review_packet==review['review'],'atlas_testflix_action_root_review')
    state=actions.derive_action_packet_lifecycle_state_v01(registry,packet_id=bound.packet_identity.packet_id)
    if 'receipt' in value:
        receipt=feedback.g35_validate_artifact_v01(value['receipt'])
        execution=firewall.native_execution_evidence_from_plain_data_v01(value['receipt']['payload']['execution_evidence'])
        context=feedback.g35_record_from_plain_v01(value['context'])
        require(not firewall.validate_native_execution_evidence_v01(execution) and execution==feedback.g35_record_from_plain_v01(value['execution'])
            and execution.invocation.inputs==feedback.g35_record_from_plain_v01(value['inputs'])
            and execution.invocation.packet_id==bound.packet_identity.packet_id and execution.invocation.owning_root_id==packet.owning_local_root_id
            and receipt.transaction_id==packet.transaction_id and receipt.owner_root_id==packet.owning_local_root_id
            and context.receipt==receipt and context in registry.action_packet_fulfillment_attempt_contexts,
            'atlas_testflix_receipt_context')
        require(value['receipt']['payload']['root_decision_id']==projection.root_decision_result.decision_id
            and state.lifecycle_state=='RECEIPT_RECEIVED' and state.idempotency_disposition=='CONSUMED'
            and state.terminal_receipt_ref==receipt.artifact_id and not state.executable,'atlas_testflix_receipt_terminal')
        expected=world.compute_output_v01(admission.definition.operation_id,execution.invocation.inputs)
        require(execution.result.output==expected and world.values_v01(expected)==value['output'],'atlas_testflix_action_output')
    return bound,registry,state


def inspect_saved_v01(value):
    bound,registry,_=validate_action_v01(value);clock=value['clock']
    material=feedback.g35_record_from_plain_v01(value['material'])
    observations=feedback.g35_record_from_plain_v01(clock['observations'])
    ids={v.dependency_id for v in bound.canonical_projection.dependency_candidate.dependency_records}
    return actions.inspect_action_packet_present_eligibility_v01(registry,packet_id=bound.packet_identity.packet_id,
        corridor=material['corridor'],corridor_step=material['corridor_step'],current_dependency_observations=tuple(v for v in observations if v.dependency_id in ids),
        logical_time_bridge=feedback.g35_record_from_plain_v01(clock['bridge']),evaluation_time=clock['evaluation_time'],
        evaluation_time_source=clock['evaluation_source'],evaluation_context_id=clock['evaluation_context'],
        action_packet_transition_registry_profile=transitions.build_action_packet_transition_registry_profile_v01())


def validate_refusal_v01(value):
    actual=inspect_saved_v01(value['action'])
    require(not actual.present_executable and feedback.g35_record_to_plain_v01(actual)==value['inspection']
        and value['reason']=='host_current_action_not_executable' and value['executor_delta']==0,'atlas_testflix_saved_current_refusal')
    return actual


def validate_quote_v01(value):
    q=value['quote_records'];purchase=value['purchase'];request=c.request_from_plain_v01(value['request'])
    rows=feedback.g35_validate_work_records_v01(q['results'],q['admissions'])
    feedback._g35_checked_work_relation_v01(q['topology'],q['artifact'],rows,q['admissions'])
    require([r.work_id for r in rows]==['quote','period'],'atlas_testflix_quote_inventory')
    for row,operation in zip(rows,('testflix.quote.v01','testflix.period.v01')):
        require(row.result.output==world.compute_output_v01(operation,row.invocation.inputs),'atlas_testflix_quote_output')
    quote,period=(world.values_v01(r.result.output) for r in rows)
    require(period['quote_ref']==quote['quote_ref'] and period['valid_to']==request.now+quote['period_seconds']
        and purchase['semantics']['selected_plan']['price_minor']==quote['price_minor'],'atlas_testflix_quote_period')
    ri,rr=validate_review_v01(q['selection'])
    candidate=purchase['user_selection']['candidate']
    claims=roots.root_decision_input_to_plain_dict_v01(ri)['root_review_packet']['synthesis_proposal']['normalized_claims']
    require(rr.decision=='ACCEPT' and rr.target_root_id=='root:testflix:user'
        and claims[0]['object_or_value']==candidate and candidate['quote_ref']==quote['quote_ref']
        and candidate['work_result_refs']==[r.result.result_id for r in rows]
        and candidate['amount_minor']==quote['price_minor'] and candidate['order_id']==request.order_id
        and candidate['device_id']==request.approved_device_id and request.purchase_consent
        and candidate['amount_minor'] in request.approved_prices_minor,'atlas_testflix_quote_consent')
    require(purchase['quote']['d_report']['status']=='PASS' and
        purchase['quote']['program']['topology_artifact']==q['topology'],'atlas_testflix_D_projection')
    return quote,period,rr


def validate_cards_v01(value):
    quote,period,user=validate_quote_v01(value)
    actions_by=value['actions']
    for row in actions_by.values():validate_action_v01(row)
    payment=actions_by['payment'];paid=value['purchase']['entitlement']
    require(payment['evidence']['quote_ref']==quote['quote_ref'] and payment['evidence']['user_selection']==user.decision_id
        and payment['output']['amount_minor']==quote['price_minor'] and payment['output']['currency']==value['request']['currency']
        and paid['candidate']['payment_receipt_ref']==payment['output']['payment_ref']
        and paid['candidate']['valid_to']==period['valid_to'],'atlas_testflix_paid_period')
    t1=value['T1'];before,_,state=validate_action_v01(t1['before']);refusal=validate_refusal_v01(t1['refusal'])
    require(state.lifecycle_state=='PENDING_FULFILLMENT' and state.idempotency_disposition!='CONSUMED' and inspect_saved_v01(t1['before']).present_executable,
        'atlas_testflix_T1_pending_positive')
    require(t1['before']['bound']==t1['refusal']['action']['bound'] and t1['before']['evidence']==payment['evidence']
        and t1['positive_initial_payment_ref']==payment['receipt']['artifact_id'],'atlas_testflix_T1_original_quote')
    changed=feedback.g35_record_from_plain_v01(t1['current_observation'])
    changed_hash=actions.domain_separated_sha256_hex_v01(domain='testflix.authoritative_dependency.v01',payload=c.canonical_v01(t1['changed_terms']))
    require(changed.observed_content_sha256==changed_hash and changed.observed_content_sha256!=before.canonical_projection.dependency_candidate.dependency_records[0].content_sha256
        and t1['changed_terms']['amount_minor']==value['fixture']['changed_price_minor'] and t1['changed_terms']['amount_minor']!=quote['price_minor']
        and changed in feedback.g35_record_from_plain_v01(t1['refusal']['action']['clock']['observations'])
        and refusal.historical_state.lifecycle_state=='PENDING_FULFILLMENT' and refusal.evaluation_time<before.canonical_projection.temporal_authority.expires_at_utc,
        'atlas_testflix_T1_changed_current_quote')
    t2=value['T2'];expiry=validate_refusal_v01(t2['expiry']);revoked=validate_refusal_v01(t2['revocation'])
    prepared=value['prepared_session'];pending=prepared['pending_device'];bound=feedback.g35_record_from_plain_v01(pending['bound'])
    require(expiry.historical_state.lifecycle_state=='PENDING_FULFILLMENT' and expiry.historical_state.idempotency_disposition!='CONSUMED'
        and expiry.evaluation_time==t2['deadline']==bound.canonical_projection.temporal_authority.expires_at_utc==prepared['session']['candidate']['valid_to']
        and t2['expiry']['action']['bound']==t2['revocation']['action']['bound']==pending['bound'],'atlas_testflix_T2_exact_expiry')
    require(revoked.historical_state.lifecycle_state=='REVOKED' and revoked.evaluation_time<t2['deadline']
        and bound.canonical_projection.owning_local_root_id==t2['owning_root']=='root:testflix:device'
        and t2['period_unchanged']==paid,'atlas_testflix_T2_owner_revocation')
    validate_action_v01(prepared['issued']);require(inspect_saved_v01(pending).present_executable,'atlas_testflix_current_neighbor')
    t3=value['T3'];retry=validate_refusal_v01(t3['retry'])
    registry=feedback.g35_record_from_plain_v01(t3['before']['registry'])
    payment_bound=feedback.g35_record_from_plain_v01(payment['bound'])
    replay=actions.replay_action_packet_lifecycle_history_v01(registry,packet_id=payment_bound.packet_identity.packet_id)
    require(t3['before']==t3['after'] and t3['receipt']==payment['receipt'] and
        feedback.g35_record_to_plain_v01(replay)==t3['lifecycle_replay'] and retry.historical_state.idempotency_disposition=='CONSUMED'
        and t3['extension_reason']=='payment_period_already_consumed','atlas_testflix_T3_no_second_purchase')
    return True


def validate_experience_v01(value):
    exp=value['experience']
    for key in ('observation','before','after'):validate_work_v01(exp[key])
    predictive=feedback.PredictiveOutcomeSourceContextV01(canonical(exp['observation']['predictive']))
    ofe=feedback.OutcomeFeedbackEnvelopeV01(canonical(exp['observation']['feedback']))
    require(not feedback.validate_outcome_feedback_against_sources_v01(ofe,source_bundle=predictive,profile=feedback.PREDICTIVE_SOURCE_PROFILE_ID)
        and exp['observation']['predictive']['result_artifact']==exp['observation']['artifact'],'atlas_testflix_predictive_source')
    event=cal.bind_outcome_feedback_event_v01(ofe,source_bundle=predictive,profile=feedback.PREDICTIVE_SOURCE_PROFILE_ID)
    validate_snapshot_v01(exp['snapshot'],{json.loads(event.feedback_canonical)['feedback_id']:event})
    recording=feedback.g35_record_from_plain_v01(exp['recording_review'])
    validate_recording_review_v01(exp['snapshot'],recording);validate_epoch_v01(exp['snapshot'],exp['head'],recording,exp['storage'])
    validate_current_projection_v01(exp['observation']);validate_current_projection_v01(exp['before'])
    validate_current_projection_v01(exp['after'],exp['snapshot'],exp['head'])
    require(exp['before']['material']==exp['after']['material']==exp['observation']['material']
        and exp['before']['contract']['claims']==exp['after']['contract']['claims']
        and exp['before']['projection']['selected']=='provenance' and exp['after']['projection']['selected']=='constraint'
        and exp['snapshot']['prior']['effective_count']==1 and exp['snapshot']['prior']['prior_fp']>0,'atlas_testflix_effective_history')
    material=exp['after']['material'];prepared=value['prepared_session'];pending=prepared['pending_device']
    canonical_packet=feedback.g35_record_from_plain_v01(pending['bound']).canonical_projection
    require(material['canonical']==feedback.g35_record_to_plain_v01(canonical_packet)
        and material['event']==prepared['event'] and material['entitlement']==value['purchase']['entitlement']
        and canonical(material['devices'])==canonical(prepared['view']['devices'])
        and material['clock']==dict(evaluation_time=pending['clock']['evaluation_time'],source=pending['clock']['evaluation_source'],context=pending['clock']['evaluation_context'])
        and material['checks'][0]['observations'][0]['observed']==pending['clock']['observations'],'atlas_testflix_work_native_source')
    return True


def validate_memory_v01(value):
    t4=value['T4'];exp=value['experience']
    require(t4['before']==t4['after'] and t4['D1']=='PENDING','atlas_testflix_memory_no_effect')
    for key,consent,outcome in (('no_consent',False,'NEEDS_USER'),('explicit_consent',True,'ACCEPT')):
        row=t4[key];source=feedback.g35_record_from_plain_v01(row['source']);contribution=feedback.g35_record_from_plain_v01(row['contribution'])
        inputs,result=validate_review_v01(row['review'])
        require(not sw.validate_root_review_packet_v01(request=source,contributions=(contribution,),packet=inputs.root_review_packet,
            trust_profiles=trust.build_default_component_trust_profiles_v01()),'atlas_testflix_memory_packet')
        advice=row['advice'];raw=roots.root_decision_input_to_plain_dict_v01(inputs)
        require(advice==dict(suggestion=value['fixture']['memory_suggestion'],authority='ADVISORY_ONLY',snapshot_ref=exp['snapshot']['snapshot_id'],
            prior=exp['snapshot']['prior'],current_projection=exp['after']['projection'],work_artifact_ref=exp['after']['artifact']['artifact_id'])
            and sw.semantic_work_to_plain_dict_v01(contribution.claims[0])['object_or_value']==dict(candidate=row['candidate'],memory_advice=advice)
            and 'atlas:memory:'+digest(advice) in source.bounded_context_refs,'atlas_testflix_memory_consumption')
        require(row['candidate']==value['purchase']['user_selection']['candidate'] and row['request']['purchase_consent'] is consent
            and raw['permission_state']['user_permission_present'] is consent and raw['permission_state']['permission_required']
            and result.decision==outcome and result.target_root_id=='root:testflix:user'
            and row['current_logical_time']==value['prepared_session']['pending_device']['clock']['evaluation_time']
            and row['request']['now']<=row['current_logical_time']<row['candidate']['valid_to'],'atlas_testflix_memory_current_consent')
    return True


def validate_consumption_v01(value):
    exp=value['experience'];row=value['consumption'];selected=exp['after'];pending=value['prepared_session']['pending_device']
    bound=feedback.g35_record_from_plain_v01(pending['bound']);session=value['prepared_session']['session']
    grant=c.SessionV01(c.SessionCandidateV01(**session['candidate']),session['provider_decision_id'],session['issuance_receipt_ref'])
    expected=dict(packet_id=bound.packet_identity.packet_id,operation='testflix.playback.v01',work_artifact_ref=selected['artifact']['artifact_id'],
        input_sha256=digest(selected['material']),output_sha256=digest(selected['output']),session_ref=grant.session_id)
    require(row['material']==expected,'atlas_testflix_consumed_result_reference')
    inputs,result=validate_review_v01(row['review']);raw=roots.root_decision_input_to_plain_dict_v01(inputs)
    claims=raw['root_review_packet']['synthesis_proposal']['normalized_claims']
    require(result.decision=='ACCEPT' and result.selected_candidate_id==bound.packet_identity.packet_id
        and result.target_root_id=='root:testflix:device' and result.transaction_id==bound.canonical_projection.transaction_id
        and len(claims)==1 and claims[0]['object_or_value']==expected,'atlas_testflix_consumer_root')
    validate_action_v01(row['playback'])
    require(row['playback']['bound']==pending['bound'] and row['event']==value['prepared_session']['event'] and row['session']==session
        and row['playback']['output']['session_ref']==grant.session_id and row['playback']['output']['playback_state']=='PLAYING'
        and selected['output']['checks'][0]['healthy'] and row['executor_delta']==1
        and row['after']['entitlements']==row['before']['entitlements']==[value['purchase']['entitlement']]
        and row['after']['consumed_periods']==row['before']['consumed_periods']
        and row['wrong_work_control']==dict(reason='atlas_testflix_wrong_consumer_work',executor_delta=0),'atlas_testflix_native_continuation')
    return True


def validate_testflix_v01(value):
    validate_cards_v01(value);validate_experience_v01(value);validate_memory_v01(value);validate_consumption_v01(value)
    require(set(value['roots'].values())=={'root:testflix:user','root:testflix:bank','root:testflix:provider','root:testflix:device'},'atlas_testflix_roots')
    require(value['counts']==dict(main_payments=1,new_paid_periods=1,new_current_sessions=1,native_prediction_events=1,
        unique_experience_consumers=1,new_provider_calls=0,captured_reexecutions=0),'atlas_testflix_counts')
    require(value['final_view']==value['consumption']['after'],'atlas_testflix_final_view')
    return True
