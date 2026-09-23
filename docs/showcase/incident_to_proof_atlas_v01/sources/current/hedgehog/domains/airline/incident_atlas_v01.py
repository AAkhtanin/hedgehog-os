"""Airline incident cards over accepted boundaries and one generic history consumer."""
import json
from pathlib import Path
import time

from hedgehog import action_commit_packet_v02 as actions, outcome_feedback_v01 as feedback
from hedgehog import outcome_calibration_v01 as cal, outcome_feedback_history_v01 as history
from hedgehog.kernel import abi_v01 as abi, effect_firewall_v01 as firewall, root_decision_v01 as roots
from hedgehog.incident_atlas_v01 import canonical_v01 as canonical, digest_v01 as digest, require_v01 as require
from hedgehog.incident_atlas_history_v01 import validate_snapshot_v01, validate_epoch_v01
from hedgehog.domains.supplier_water_filter import incident_atlas_backend_v01 as backend
from . import semantic_to_contract_binding_v01 as b, semantic_to_contract_causal_runtime_v01 as r
from .outcome_feedback_adapter_v01 import controlled_semantics_v01
from . import incident_atlas_work_v01 as native


def specification_v01():
    return json.loads((Path(__file__).resolve().parents[3]/'fixtures/incident_atlas_airline_v01.json').read_bytes())


def validate_review_v01(saved):
    review = feedback.g35_record_from_plain_v01(saved)
    require(type(review) is tuple and len(review)==3, 'atlas_airline_review_shape')
    require(not roots.validate_root_decision_result_v01(kernel=review[0],decision_input=review[1],result=review[2]), 'atlas_airline_review_invalid')
    return review[1],review[2]


def selection_v01(offer, scenario):
    def provider(actor, request):
        payload = controlled_semantics_v01(actor, request)
        if actor == b.ACTOR_CLIENT_PURCHASE_INTENT_REVIEWER:
            payload.update(proposal_id='atlas:proposal:' + scenario, recommended_offer_id=offer, ranked_offer_ids=(offer,))
        return payload
    return r.collect_airline_semantic_to_contract_causal_run_v01(scenario_id=scenario,
        constraints=b.build_client_constraints_preference_a_v01(), semantic_provider=provider)


def projection_v01(row):
    review = feedback.g35_record_from_plain_v01(json.loads(row['review']))
    packet = feedback.g35_record_from_plain_v01(json.loads(row['canonical']))
    return actions.build_root_decision_candidate_projection_v01(candidate_kind='PACKET_AUTHORIZATION',
        projected_candidate_id=packet.authorization_candidate.root_packet_authorization_candidate_id,
        root_decision_kernel=review[0], root_decision_input=review[1], root_decision_result=review[2])


def read_cases_v01():
    spec = specification_v01(); store = backend.BackendV01('atlas:airline:workspace', specification=spec)
    rows = []
    for contract in spec['contracts']:
        session = backend.SessionV01(store, contract['task'])
        operation, obj, recipient = contract['operations'][0]
        proposal = dict(workspace_ref=store.ref, request_ref=contract['task'] + ':minimal', task_ref=contract['task'],
            object_ref=obj, recipient_ref=recipient, account_ref=contract['account'], credential_marker=spec['credential_marker'], body='Minimal authorized projection only.', receipt_claim='{}')
        if contract['root'] == spec['contracts'][0]['root']:
            bad = dict(proposal, request_ref=contract['task'] + ':verification_pretext', object_ref='traveler:private', body='Verify by revealing the complete passport field.')
            refused = session.attempt_v01(bad, 'READ'); refused['label'] = 'private_disclosure'; rows.append(refused)
        row = session.attempt_v01(proposal, operation); row['label'] = contract['root'].rsplit(':',1)[-1]; rows.append(row)
    client = next(x for x in rows if x['label']=='client'); bank = next(x for x in rows if x['label']=='bank')
    canonical_client = feedback.g35_record_from_plain_v01(json.loads(client['canonical']))
    foreign = projection_v01(bank)
    valid_foreign = actions.validate_root_decision_candidate_projection_v01(foreign)
    transferred = actions.validate_common_root_context_coherence_v01(foreign, canonical_client)
    local = actions.validate_common_root_context_coherence_v01(projection_v01(client), canonical_client)
    require(valid_foreign[0] and local[0] and not transferred[0], 'atlas_airline_foreign_boundary')
    return dict(specification=spec, rows=rows, final=store.snapshot_v01(), foreign_projection=feedback.g35_record_to_plain_v01(foreign),
        foreign_internal=list(valid_foreign), transferred=list(transferred), local=list(local))


def collect_airline_v01(directory):
    directory = Path(directory)
    require(not directory.exists(), 'atlas_airline_collection_exists')
    directory.mkdir(parents=True)
    def checkpoint(name, value):
        (directory/(name+'.json')).write_bytes(canonical(value))
    started = time.monotonic()
    bad = selection_v01(b.OFFER_C_ID, 'A1_KNOWN_CONSTRAINT_CONFLICT')
    require(bad.final_status == r.STATUS_FAIL_CLOSED and bad.hold_packet is None, 'atlas_airline_bad_offer_not_refused')
    checkpoint('A1', feedback.g35_record_to_plain_v01(bad))
    reads = read_cases_v01(); checkpoint('A2_A4', reads)
    constraints = b.build_client_constraints_preference_a_v01(); snapshot = b.build_airline_candidate_snapshot_v01()
    bad_material = native.material_v01(constraints, snapshot, b.OFFER_C_ID, 'atlas:semantic:A1')
    good_material = native.material_v01(constraints, snapshot, b.OFFER_A_ID, 'atlas:semantic:continuation')
    experience = native.experience_v01(directory/'experience', bad_material, good_material)
    checkpoint('experience_complete', experience)
    # The actual completed current Work is consumed before selection/hold.
    consumed = experience['after']['output']
    require(consumed['checks'][0]['healthy'] and consumed['offer_id'] == b.OFFER_A_ID, 'atlas_airline_consumed_work')
    good = selection_v01(consumed['offer_id'], 'A1_LAWFUL_FROM_CURRENT_WORK')
    other = selection_v01(b.OFFER_B_ID, 'A3_VALID_OTHER_OFFER')
    checkpoint('lawful_selection', feedback.g35_record_to_plain_v01(good))
    checkpoint('other_selection', feedback.g35_record_to_plain_v01(other))
    require(good.final_status == other.final_status == r.STATUS_LOCAL_MODEL_PASS, 'atlas_airline_lawful_chain')
    selection = b.build_selection_input_v01(b.build_valid_airline_bsep_projection_ref_v01(), constraints, snapshot)
    wrong = b.validate_client_root_offer_selection_decision_v01(selection, other.canonical_evidence, good.client_root_decision)
    matching = b.validate_client_root_offer_selection_decision_v01(selection, good.canonical_evidence, good.client_root_decision)
    require(wrong.validation_status != 'PASS' and matching.validation_status == 'PASS', 'atlas_airline_offer_transfer')
    value = dict(profile='AT2_AIRLINE_V01', execution='FRESH_CONTROLLED', origin='AUTHORED_FIXTURE',
        bad=feedback.g35_record_to_plain_v01(bad), good=feedback.g35_record_to_plain_v01(good), other=feedback.g35_record_to_plain_v01(other), reads=reads,
        transfer=feedback.g35_record_to_plain_v01(wrong), matching=feedback.g35_record_to_plain_v01(matching), experience=experience,
        consumption=dict(work_artifact_ref=experience['after']['artifact']['artifact_id'], output_sha256=digest(consumed),
            selected_offer_id=good.root_selected_offer_id, hold_id=good.hold_packet.packet_id),
        elapsed_seconds=time.monotonic()-started,
        limits=['Selected-offer/hold only; ticket/payment corridor NOT_RUN.', 'Controlled callbacks are not provider calls.',
                'Historical fixture offer times do not claim a current live Airline quote.'])
    checkpoint('airline_unvalidated', value)
    validate_airline_v01(value)
    checkpoint('airline', value)
    return value


def validate_reads_v01(value):
    from types import SimpleNamespace
    require(value['specification'] == specification_v01(), 'atlas_airline_independent_read_contract')
    rows = value['rows']; by = {x['label']:x for x in rows}
    previous = None
    for row in rows:
        require(row['record_id'] == digest({k:v for k,v in row.items() if k not in ('record_id','label')}), 'atlas_airline_read_identity')
        packet = feedback.g35_record_from_plain_v01(json.loads(row['canonical']))
        review = feedback.g35_record_from_plain_v01(json.loads(row['review']))
        validate_review_v01(json.loads(row['review']))
        material = dict(contract=row['contract'], proposal=row['proposal'], operation=row['operation'])
        require(row['contract'] in value['specification']['contracts'], 'atlas_airline_read_contract')
        require(row['operation']=='READ' and actions.validate_native_action_commit_packet_v01(packet)[0], 'atlas_airline_read_packet')
        errors=backend.contract_errors_v01(row['contract'],row['proposal'],'READ',backend=SimpleNamespace(ref='atlas:airline:workspace'))
        raw=roots.root_decision_input_to_plain_dict_v01(review[1])
        require(list(errors)==row['contract_errors'] and raw['policy_state']['scope_passed']==(not errors)
            and raw['policy_state']['hard_policy_passed']==(not errors) and row['decision']==review[2].decision, 'atlas_airline_independent_read_policy')
        claims = raw['root_review_packet']['synthesis_proposal']['normalized_claims']
        candidate = packet.authorization_candidate.root_packet_authorization_candidate_id
        reference = 'supplier:material:' + feedback.g35_hash_v01(material)
        require(len(claims)==1 and claims[0]['claim_id']==candidate and claims[0]['object_or_value']==dict(candidate_id=candidate,candidate_kind='PACKET_AUTHORIZATION')
            and claims[0]['provenance_refs']==[reference] and claims[0]['subject']==row['proposal']['object_ref'], 'atlas_airline_read_material')
        require(review[1].target_root_id==review[2].target_root_id==packet.owning_local_root_id==row['contract']['root']
            and review[1].transaction_id==review[2].transaction_id==packet.transaction_id, 'atlas_airline_read_owner')
        require(native.values(packet.consequential_effect_parameters.parameter_records)==row['proposal']
            and packet.dependency_candidate.dependency_records[0].content_sha256==digest(material), 'atlas_airline_read_canonical')
        dependencies=[v.evidence_ref for v in packet.dependency_candidate.dependency_records if v.requirement_class=='MANDATORY']
        require(raw['post_vv_bundle']['required_evidence_refs']==raw['post_vv_bundle']['provided_evidence_refs']==[reference,*dependencies]
            and raw['policy_state']['policy_id']==packet.authority_policy_fingerprint
            and raw['permission_state']['permission_ref']==packet.canonical_permission_ref==row['contract']['permission'], 'atlas_airline_read_dependencies')
        require(review[2].selected_candidate_id == packet.authorization_candidate.root_packet_authorization_candidate_id or row['decision'] != 'ACCEPT', 'atlas_airline_read_selected')
        if previous is not None: require(row['before']==previous, 'atlas_airline_backend_continuity')
        previous = row['after']
        before = feedback.g35_record_from_plain_v01(json.loads(row['registry_before']))
        after = feedback.g35_record_from_plain_v01(json.loads(row['registry_after']))
        require(actions.validate_action_commit_packet_registry_v02(before)[0] and actions.validate_action_commit_packet_registry_v02(after)[0], 'atlas_airline_registry')
        if row['label']=='private_disclosure':
            require(row['decision']!='ACCEPT' and row['receipt'] is None and row['before']==row['after'] and before==after, 'atlas_airline_disclosure')
        else:
            require(row['decision']=='ACCEPT' and actions.validate_common_root_context_coherence_v01(projection_v01(row), packet)[0], 'atlas_airline_local_authority')
            require(len(after.action_packet_fulfillment_attempt_contexts)==len(before.action_packet_fulfillment_attempt_contexts)+1, 'atlas_airline_current_receipt')
            receipt = after.action_packet_fulfillment_attempt_contexts[-1].receipt
            require(abi.kernel_artifact_to_plain_dict_v01(receipt)==row['receipt'], 'atlas_airline_exact_receipt')
            evidence = firewall.native_execution_evidence_from_plain_data_v01(row['receipt']['payload']['execution_evidence'])
            require(not firewall.validate_native_execution_evidence_v01(evidence), 'atlas_airline_read_execution')
            require(native.values(evidence.invocation.inputs)==row['proposal'] and evidence.invocation.task_id==row['contract']['task'], 'atlas_airline_read_invocation')
            expected = dict(operation='READ',request_ref=row['proposal']['request_ref'], task=row['contract']['task'], object_ref=row['proposal']['object_ref'],recipient=row['proposal']['recipient_ref'])
            require(row['after']['calls']==row['before']['calls']+[expected], 'atlas_airline_read_call')
            projected=value['specification']['objects'][row['proposal']['object_ref']]
            require(native.values(evidence.result.output)['result']==projected
                and row['after']['reads']==row['before']['reads']+1 and row['after']['object_hashes']==row['before']['object_hashes']
                and row['after']['writes']==row['before']['writes']==0, 'atlas_airline_read_projection')
    require(value['final']==previous and value['final']['reads']==3 and value['final']['writes']==0, 'atlas_airline_backend_final')
    visible = value['final']['context_by_task'][value['specification']['contracts'][0]['task']]
    require(visible == [value['specification']['objects']['offer:public']] and value['specification']['objects']['traveler:private'] not in canonical(visible).decode(), 'atlas_airline_canary_leak')
    foreign = feedback.g35_record_from_plain_v01(value['foreign_projection'])
    local_packet = feedback.g35_record_from_plain_v01(json.loads(by['client']['canonical']))
    require(foreign==projection_v01(by['bank']), 'atlas_airline_foreign_source')
    require(actions.validate_root_decision_candidate_projection_v01(foreign)[0], 'atlas_airline_foreign_internal')
    actual = actions.validate_common_root_context_coherence_v01(foreign, local_packet)
    require(not actual[0] and canonical(list(actual))==canonical(value['transferred']), 'atlas_airline_contextual_refusal')


def validate_work_v01(value):
    records = feedback.g35_validate_work_records_v01(value['results'], value['admissions'])
    program = feedback.g35_record_from_plain_v01(value['program'])
    feedback._g35_checked_work_relation_v01(abi.kernel_artifact_to_plain_dict_v01(program.topology_artifact), value['artifact'], records, value['admissions'])
    ri, rr = validate_review_v01(value['output_review'])
    require(rr.decision=='ACCEPT' and rr.selected_candidate_id==value['artifact']['artifact_id'], 'atlas_airline_work_review')
    claims = roots.root_decision_input_to_plain_dict_v01(ri)['root_review_packet']['synthesis_proposal']['normalized_claims']
    require(len(claims)==1 and claims[0]['object_or_value']==value['output'] and ri.root_review_packet.runtime_topology_ref==program.topology_artifact.artifact_id, 'atlas_airline_output_consumption')
    material = json.loads(native.values(records[0].invocation.inputs)['material'])
    output = json.loads(native.values(records[0].result.output)['material'])
    require(material==value['material'] and output==value['output']==native.evaluate_v01(material, provenance=value['projection']['selected']=='provenance'), 'atlas_airline_work_material')
    require(value['artifact']['owner_root_id']==native.ROOT and value['artifact']['transaction_id']==rr.transaction_id, 'atlas_airline_work_owner')
    current_input,current_result=validate_review_v01(value['current_review'])
    selected=value['projection']['selected']
    raw=roots.root_decision_input_to_plain_dict_v01(current_input)
    selected_claim=next(c['object_or_value'] for c in raw['root_review_packet']['synthesis_proposal']['normalized_claims'] if c['claim_id']==selected)
    require(current_result.decision=='ACCEPT' and current_result.selected_candidate_id==selected
        and current_result.transaction_id==rr.transaction_id and current_result.target_root_id==native.ROOT,'atlas_airline_current_work_review')
    require(selected_claim['advisory_ref']==value['projection']['projection_id'] and selected_claim['bridge_ref']==value['bridge']['artifact_id']
        and selected_claim['material_sha256']==digest(material) and selected_claim['definition_id']==records[0].invocation.definition_id,'atlas_airline_current_claim')
    proposal=feedback.g35_validate_artifact_v01(value['proposal']); payload=value['proposal']['payload']
    require(payload['material']==material and payload['root_decision_ref']==current_result.decision_id
        and payload['advisory_ref']==selected_claim['advisory_ref'] and payload['bridge_ref']==selected_claim['bridge_ref']
        and payload['operation']==selected_claim['operation'] and program.candidate.semantic_proposal_ref==proposal.artifact_id,'atlas_airline_program_consumption')
    if value['additional'] is not None:
        validate_work_v01(value['additional'])
        check=value['contract']['checks'][selected]
        extra=value['additional']; receipt=value['receipt_bridge']
        feedback.g35_validate_artifact_v01(receipt)
        require(extra['proposal']['payload']['check_request']==check and extra['material']==check['material']
            and extra['output']==check['result_facts'] and receipt['payload']['result_facts']==extra['output']
            and receipt['payload']['original_ref']['artifact_id']==extra['artifact']['artifact_id']
            and payload['check_receipt_ref']==receipt['artifact_id'] and selected_claim['additional_receipt_ref']['artifact_id']==receipt['artifact_id'], 'atlas_airline_required_check')


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
    require(ctx==consumer.current_context_v01(source,root=native.ROOT,transaction=ctx['transaction'],policy_ref=native.subject_v01(material)[0]['policy_semantics_version']), 'atlas_airline_current_source')
    require(canonical(value['source'])==canonical({k:getattr(source,k) for k in value['source']}), 'atlas_airline_saved_source')
    require(projection['context']==ctx and projection['contract_id']==contract['contract_id'], 'atlas_airline_current_contract')
    strategies=tuple(contract['claims'])
    candidates=tuple(avf.AVFCandidateV02(candidate_id=s,candidate_label='atlas.airline.'+s,base_viability_score=0.80 if s=='constraint' else 0.79,ttl_valid=True) for s in strategies)
    reports=avf.evaluate_avf_candidates_v02(avf.AVFEvaluationInputV02(evaluation_id='g34:'+value['bridge']['artifact_id'],resolver_mode='CURRENT_CONTEXT',candidates=candidates))
    require(canonical(value['reports'])==canonical({r.candidate_id:asdict(r) for r in reports.decision_reports}), 'atlas_airline_actual_avf')
    prior=snapshot['prior'] if snapshot else None
    update=cal.GTTrustUpdateV01(canonical(snapshot['updates'][-1])) if snapshot else None
    for row in projection['rows']:
        strategy=row['candidate_id'];subject,key=native.subject_v01(material,strategy)
        claim=contract['claims'][strategy]
        require(claim['subject']==subject and claim['history_key']==key and claim['material_sha256']==digest(material)
            and claim['observation_refs']==[v['observation_id'] for v in material['checks'][0]['observations']], 'atlas_airline_current_material')
        p=prior['prior_fp'] if prior and key==prior['history_key'] else 0
        report=next(r for r in reports.decision_reports if r.candidate_id==strategy)
        base=report.score_explanation.final_avf_score; fp=int((Decimal(str(base))*cal.Q).to_integral_value(rounding=ROUND_HALF_EVEN))
        adjusted,micros=cal.adjusted_avf_score_v01(fp,p)
        match=bool(snapshot and subject==snapshot['fold']['subject_key'])
        trust=cal.evaluate_gt_trust_at_v01(update if match else None,evaluation_time=projection['evaluated_at']).to_plain_data()
        require(row==dict(candidate_id=strategy,base_fp=fp,prior_fp=p,adjusted_fp=adjusted,score_micros=micros,eligible=report.hard_mask.hard_mask_value!=0,
            base_field='score_explanation.final_avf_score',base_decimal=str(base),prior_ref=prior['prior_id'] if prior and key==prior['history_key'] else None,
            trust=trust,subject_status='MATCHED' if match else 'COLD_OR_NONMATCHING',claim_id=claim['claim_id']), 'atlas_airline_applied_history')
    winner=sorted((r for r in projection['rows'] if r['eligible']),key=lambda r:(-r['adjusted_fp'],r['candidate_id']))[0]
    require(projection['selected']==winner['candidate_id'] and projection['trust']==winner['trust']
        and projection['history_ref']==(snapshot['snapshot_id'] if snapshot else None), 'atlas_airline_actual_selection')
    if snapshot:
        discovery=value['discovery']; bridge=value['bridge']; payload=bridge['payload']
        review=review_from_plain_v01(discovery['review'])
        require(review[2].decision=='ACCEPT' and review[2].selected_candidate_id==discovery['plan']['retrieval_plan_id']
            and [v['stage'] for v in discovery['read_audit']]==['DESCRIPTOR','ROOT_APPROVED','PAYLOAD_READ','PUBLIC_OPEN_VALIDATED','NUMERIC_SOURCE_VALIDATED']
            and discovery['read_audit'][1]['decision']==review[2].decision_id, 'atlas_airline_current_descent_review')
        claims=roots.root_decision_input_to_plain_dict_v01(review[1])['root_review_packet']['synthesis_proposal']['normalized_claims']
        require(len(claims)==1 and claims[0]['object_or_value']==discovery['plan'], 'atlas_airline_descent_plan')
        require(discovery['payload_sha256']==digest(snapshot) and discovery['opened']==[head['record_id']]
            and payload['head']==head and payload['prior']==prior and payload['descent_id']==discovery['descent']['memory_descent_result_id']
            and payload['current_local_root_ref']==native.ROOT and payload['current_transaction_ref']==ctx['transaction']
            and payload['evaluated_at']==projection['evaluated_at'], 'atlas_airline_opened_history_binding')
    if value['additional'] is not None: validate_current_projection_v01(value['additional'])


def validate_airline_v01(value):
    bad, good, other = (feedback.g35_record_from_plain_v01(value[k]) for k in ('bad','good','other'))
    for run in (bad, good, other):
        valid, reasons = r.validate_airline_semantic_causal_run_report_v01(run)
        require(valid, 'atlas_airline_causal_report:' + repr(reasons))
        require(run.provider_network_call_count==run.gemini_call_count==run.real_world_effects_count==0, 'atlas_airline_no_live')
    require(bad.hold_packet is None and bad.proposal.recommended_offer_id==b.OFFER_C_ID, 'atlas_airline_A1')
    require(good.final_status==other.final_status==r.STATUS_LOCAL_MODEL_PASS and good.hold_packet is not None, 'atlas_airline_lawful_hold')
    selection = b.build_selection_input_v01(b.build_valid_airline_bsep_projection_ref_v01(), b.build_client_constraints_preference_a_v01(), b.build_airline_candidate_snapshot_v01())
    wrong = b.validate_client_root_offer_selection_decision_v01(selection, other.canonical_evidence, good.client_root_decision)
    matching = b.validate_client_root_offer_selection_decision_v01(selection, good.canonical_evidence, good.client_root_decision)
    require(wrong.validation_status!='PASS' and feedback.g35_record_to_plain_v01(wrong)==value['transfer'], 'atlas_airline_A3_transfer')
    require(matching.validation_status=='PASS' and feedback.g35_record_to_plain_v01(matching)==value['matching'], 'atlas_airline_A3_neighbor')
    validate_reads_v01(value['reads'])
    exp = value['experience']
    for label in ('observation','before','after'): validate_work_v01(exp[label])
    predictive = feedback.PredictiveOutcomeSourceContextV01(canonical(exp['observation']['predictive']))
    ofe = feedback.OutcomeFeedbackEnvelopeV01(canonical(exp['observation']['feedback']))
    require(not feedback.validate_outcome_feedback_against_sources_v01(ofe, source_bundle=predictive, profile=feedback.PREDICTIVE_SOURCE_PROFILE_ID), 'atlas_airline_feedback')
    require(exp['observation']['predictive']['result_artifact']==exp['observation']['artifact'], 'atlas_airline_prediction_work')
    event = cal.bind_outcome_feedback_event_v01(ofe, source_bundle=predictive, profile=feedback.PREDICTIVE_SOURCE_PROFILE_ID)
    validate_snapshot_v01(exp['snapshot'], {json.loads(event.feedback_canonical)['feedback_id']:event})
    from hedgehog.incident_atlas_history_v01 import validate_recording_review_v01
    recording_review = feedback.g35_record_from_plain_v01(exp['recording_review'])
    validate_recording_review_v01(exp['snapshot'], recording_review)
    validate_epoch_v01(exp['snapshot'], exp['head'], recording_review, exp['storage'])
    validate_current_projection_v01(exp['observation'])
    validate_current_projection_v01(exp['before'])
    validate_current_projection_v01(exp['after'],exp['snapshot'],exp['head'])
    require(exp['snapshot']['predecessor'] is None and exp['snapshot']['epoch']==0, 'atlas_airline_history_genesis')
    require(exp['before']['material']==exp['after']['material'] and exp['before']['contract']['claims']==exp['after']['contract']['claims'], 'atlas_airline_same_current_case')
    require(exp['before']['projection']['selected']!=exp['after']['projection']['selected'], 'atlas_airline_work_changed')
    consumed = exp['after']['output']
    require(value['consumption']==dict(work_artifact_ref=exp['after']['artifact']['artifact_id'],output_sha256=digest(consumed),
        selected_offer_id=good.root_selected_offer_id,hold_id=good.hold_packet.packet_id), 'atlas_airline_consumed_result_reference')
    require(consumed['checks'][0]['healthy'] and consumed['offer_id']==good.root_selected_offer_id, 'atlas_airline_consumed_offer')
    return True
