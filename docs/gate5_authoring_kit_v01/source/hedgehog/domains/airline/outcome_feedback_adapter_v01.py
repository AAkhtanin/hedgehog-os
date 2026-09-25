"""Controlled selected-offer corridor with a consumed ordinary BankRoot review."""
from dataclasses import asdict, fields, replace
from hedgehog import outcome_feedback_v01 as f
from hedgehog.kernel import root_decision_v01 as roots, semantic_work_v01 as sw, trust_model_v01 as trust
from . import semantic_to_contract_binding_v01 as b, semantic_to_contract_causal_runtime_v01 as r
from . import ticket_purchase_corridor_v01 as c, ticket_purchase_corridor_runtime_v01 as runtime
from . import transaction_artifact_ledger_collector_v01 as ledger, transaction_artifact_ledger_v01 as ledger_contract


def controlled_semantics_v01(actor,request):
    """Request-bound local callbacks, not model calls or precollected acceptance."""
    if actor==b.ACTOR_CLIENT_PURCHASE_INTENT_REVIEWER:
        value={k:request[k] for k in ('transaction_id','actor_id','source_selection_input_id','source_bsep_projection_ref',
            'source_client_constraint_set_id','source_candidate_set_snapshot_id','source_candidate_set_digest')}
        value['candidate_set_ref']=request['source_candidate_set_ref']
        value.update(proposal_id='g35:airline:proposal',recommended_offer_id=b.OFFER_A_ID,ranked_offer_ids=(b.OFFER_A_ID,),
            decision_factors=('bounded_offer',),preference_matches=('aisle',),uncertainty_notes=('requires_root_review',),requires_root_review=True,
            semantic_summary='Controlled bounded offer recommendation.',real_world_effects_count=0)
        value.update({k:False for k in ('authority_created','action_permission_created','packet_created','receipt_created','payment_created','ticket_created','booking_created','final_output_created')})
        return value
    return dict(response_id='g35:review:'+actor,transaction_id=request['transaction_id'],actor_id=actor,source_request_id=request['request_id'],
        source_selection_input_id=request['source_selection_input_id'],source_candidate_set_snapshot_id=request['source_candidate_set_snapshot_id'],
        source_candidate_set_digest=request['source_candidate_set_digest'],reviewed_offer_id=request['proposed_offer_id'],review_role=request['actor_role'],
        review_status='PASS',semantic_factors=('bounded_consistency',),blocking_conflicts=(),supports_proposed_offer=True,validation_status='PASS',
        raw_output_used=False,authority_created=False,permission_created=False,real_world_effects_count=0)


def _bank_review(auth,approval,purchase):
    ref='g35:bank_input:'+f.g35_hash_v01(dict(authorization=asdict(auth),approval=asdict(approval),purchase=asdict(purchase)))
    candidate=auth.authorization_ref_id
    request=sw.build_semantic_work_request_v01(request_id='review:'+candidate,transaction_id=auth.transaction_id,target_root_id=c.BANK_ROOT_ID,
        runtime_topology_ref='g35:airline:bank_boundary',bounded_context_refs=(ref,),permitted_actor_ids=('g35:bank_validator',),
        permitted_contribution_modes=('DETERMINISTIC',),requested_subjects=(auth.offer_id,),required_evidence_classes=('PURCHASE_EVIDENCE',),forbidden_claims=('authority_creation',))
    evidence=sw.build_evidence_binding_v01(evidence_id='binding:'+ref,evidence_ref=ref,evidence_class='PURCHASE_EVIDENCE',
        source_component_id='g35:bank_validator',provenance_ref=approval.approval_ref,evidence_state='PRESENT')
    claim=sw.build_normalized_claim_v01(claim_id=candidate,subject=auth.offer_id,predicate='bounded_bank_authorization_review',
        object_or_value=dict(candidate_id=candidate,source_ref=ref),time_envelope_ref='g35:controlled_corridor',provenance_refs=(ref,),evidence_refs=(evidence.evidence_id,),
        confidence_micros=1000000,source_role='deterministic_runtime',source_mode='DETERMINISTIC')
    contribution=sw.build_actor_contribution_v01(contribution_id='contribution:'+candidate,request_id=request.request_id,actor_id='g35:bank_validator',
        actor_role='deterministic_runtime',contribution_mode='DETERMINISTIC',bsep_projection_ref='g35:bank:projection',scope=auth.offer_id,
        bounded_context_refs=(ref,),claims=(claim,),evidence_bindings=(evidence,),constraint_bindings=(),uncertainty_bindings=(),requested_validators=('bank:consent_scope',),forbidden_claims_observed=())
    packet=sw.build_root_review_packet_from_contributions_v01(request=request,contributions=(contribution,),trust_profiles=trust.build_default_component_trust_profiles_v01())
    valid=auth.amount<=approval.max_amount and auth.currency==approval.currency and auth.offer_id==approval.selected_offer_id and auth.source_purchase_intent_id==purchase.intent_id
    kernel=roots.build_root_decision_kernel_v01()
    inputs=roots.build_root_decision_input_v01(transaction_id=auth.transaction_id,target_root_id=c.BANK_ROOT_ID,root_review_packet=packet,
        post_vv_bundle=dict(bundle_id=ref,post_vv_passed=valid,validated_candidate_ids=[candidate] if valid else [],rejected_candidate_ids=[] if valid else [candidate],
            required_evidence_refs=[ref],provided_evidence_refs=[ref],hard_failure_reasons=[] if valid else ['bank_consent_scope']),
        gt_advisory=dict(advisory_id='gt:'+candidate,candidate_ids=[candidate],selected_candidate_id=candidate if valid else None,
            score_micros_by_candidate={candidate:1000000 if valid else 0},source_artifact_type='GTAdvisoryReport',source_lifecycle_state='VALIDATED',actor_role='gt',
            attempted_effect='CREATE_ROOT_DECISION',target_artifact_type='RootDecision',advisory_only=True,creates_final_output=False,requests_effect=False),
        policy_state=dict(policy_id='g35:bank:selected_offer',identity_passed=True,scope_passed=valid,hard_policy_passed=valid,allow_accept=valid,conflict_policy='DEFER',no_candidate_policy='NO_UPDATE'),
        permission_state=dict(permission_required=True,user_permission_present=valid,permission_scope_valid=valid,permission_ref=approval.approval_ref),
        temporal_state=dict(temporal_valid=not auth.expired,expired=auth.expired,not_before_satisfied=True,time_envelope_ref=ref),
        conflict_state=dict(material_unresolved_conflict=False,conflict_set_ids=[]),prior_root_state=dict(prior_decision_id=None,prior_decision=None,prior_selected_candidate_id=None))
    result=roots.decide_root_v01(kernel=kernel,decision_input=inputs)
    f._require(not roots.validate_root_decision_result_v01(kernel=kernel,decision_input=inputs,result=result) and result.decision=='ACCEPT','g35_bank_review')
    return kernel,inputs,result


def _fixtures(run):
    constructors=dict(airline_offer_hold_gate=c.build_valid_airline_root_offer_hold_gate_v01,offer_packet=c.build_valid_airline_offer_packet_v01,
        hold_packet=c.build_valid_airline_hold_commit_packet_v01,hold_receipt=c.build_valid_airline_offer_hold_receipt_v01,
        client_purchase_gate=c.build_valid_client_root_purchase_intent_gate_v01,human_approval=c.build_valid_human_approval_evidence_ref_v01,
        purchase_intent=c.build_valid_client_purchase_intent_v01,bank_gate=c.build_valid_bank_root_payment_authorization_gate_v01,
        authorization_ref=c.build_valid_bank_payment_authorization_ref_v01,airline_ticket_gate=c.build_valid_airline_root_ticket_issue_gate_v01,
        ticket_issue_intent=c.build_valid_airline_ticket_issue_intent_v01,ticket_receipt=c.build_valid_mock_ticket_receipt_v01,
        completion_gate=c.build_valid_client_root_completion_gate_v01,purchase_receipt=c.build_valid_mock_purchase_receipt_v01)
    fixtures={k:fn() for k,fn in constructors.items()};hold=run.hold_packet;resolution=run.airline_root_resolution
    substitutions={c.OFFER_ID:hold.offer_id,c.HOLD_ID:hold.hold_id,fixtures['offer_packet'].packet_id:hold.parent_offer_packet_id,
        fixtures['hold_packet'].packet_id:hold.packet_id,fixtures['hold_packet'].idempotency_key:hold.idempotency_key,c.ROUTE_REF:hold.route_ref}
    for key,value in fixtures.items():
        changes={}
        for field in fields(value):
            old=getattr(value,field.name)
            if type(old) is str and old in substitutions:changes[field.name]=substitutions[old]
            if field.name in ('amount','selected_amount'):changes[field.name]=resolution.resolved_amount
        fixtures[key]=replace(value,**changes)
    fixtures['hold_packet']=hold
    bank=_bank_review(fixtures['authorization_ref'],fixtures['human_approval'],fixtures['purchase_intent'])
    # The actually returned decision is consumed before the existing phase gate.
    fixtures['bank_gate']=replace(fixtures['bank_gate'],evidence_refs=fixtures['bank_gate'].evidence_refs+(bank[2].decision_id,))
    return fixtures,bank


def _ledger_source(run,execution):
    identity='g35:airline:source';report=execution.report
    refs=ledger_contract.AirlineTransactionArtifactLedgerExpectedSourceRefsV01('source_run:'+identity,
        'source_causal_report:'+run.run_id+':'+run.scenario_id,'source_corridor_report:'+report.run_id+':'+report.transaction_id)
    def projection(side):
        return ledger.AirlineTransactionArtifactLedgerBSEPProjectionSourceV01('g35:projection:'+side,
            run.proposer_request.source_bsep_projection_ref if side==ledger.SIDE_AIRLINE else 'g35:projection_ref:'+side,
            'g35:airline:bsep',run.transaction_id,side,'PASS',False,False,False,False,0)
    def final(root,refs):
        return ledger.AirlineTransactionArtifactLedgerRootFinalSourceV01('g35:final:'+root,run.transaction_id,root,root,'PASS',refs,False,False,0)
    return ledger.AirlineTransactionArtifactLedgerSourceBundleV01(source_bundle_id=identity,transaction_id=run.transaction_id,expected_source_refs=refs,
        client_bsep_projection=projection(ledger.SIDE_CLIENT),airline_bsep_projection=projection(ledger.SIDE_AIRLINE),
        bank_bsep_projection=projection(ledger.SIDE_BANK),cross_root_bsep_projection=projection(ledger.SIDE_CROSS_ROOT_ADVISORY),causal_report=run,
        **{k:getattr(execution,k) for k in ('offer_packet','hold_packet','hold_receipt','purchase_approval_evidence','purchase_intent','payment_authorization_ref',
            'ticket_issue_intent','mock_ticket_receipt','mock_purchase_receipt')},corridor_report=report,
        client_root_final=final(c.CLIENT_ROOT_ID,(run.client_root_decision.decision_id,execution.purchase_intent.intent_id,execution.mock_purchase_receipt.receipt_id)),
        airline_root_final=final(c.AIRLINE_ROOT_ID,(run.airline_root_resolution.resolution_id,execution.offer_packet.packet_id,execution.hold_packet.packet_id,
            execution.ticket_issue_intent.intent_id,execution.mock_ticket_receipt.receipt_id)),
        bank_root_final=final(c.BANK_ROOT_ID,(execution.payment_authorization_ref.authorization_ref_id,)),
        source_validation_refs=(refs.source_run_ref,refs.source_causal_report_ref,refs.source_corridor_report_ref),auxiliary_observation_refs=ledger.EXPECTED_AUXILIARY_OBSERVATION_REFS)


def collect_source_v01(directory):
    run=r.collect_airline_semantic_to_contract_causal_run_v01(scenario_id='G35-AIRLINE',constraints=b.build_client_constraints_preference_a_v01(),semantic_provider=controlled_semantics_v01)
    f._require(r.validate_airline_semantic_causal_run_report_v01(run)[0] and run.hold_packet is not None,'g35_airline_causal:'+repr((run.failed_stage,run.validation_errors)))
    fixtures,bank=_fixtures(run)
    context=c.build_airline_ticket_purchase_contract_context_from_resolution_v01(resolution=run.airline_root_resolution,hold_packet=run.hold_packet)
    execution=runtime.collect_airline_ticket_purchase_corridor_execution_result_v01(fixtures=fixtures,contract_context=context)
    f._require(execution.report.final_status=='PASS','g35_airline_corridor:'+repr(execution.report.validation_errors))
    source=_ledger_source(run,execution)
    body=dict(source=f.g35_record_to_plain_v01(source),fixtures=f.g35_record_to_plain_v01(fixtures),bank_review=[f.g35_record_to_plain_v01(v) for v in bank],
        receipt_provenance='CONTROLLED_FIXTURE_INPUT_NOT_NATIVE_HOST_OR_LIVE_BANKING')
    return body


def validate_source_v01(body):
    f._keys(body,('source','fixtures','bank_review','receipt_provenance'))
    f._require(body['receipt_provenance']=='CONTROLLED_FIXTURE_INPUT_NOT_NATIVE_HOST_OR_LIVE_BANKING','g35_airline_provenance')
    source=f.g35_record_from_plain_v01(body['source']);fixtures=f.g35_record_from_plain_v01(body['fixtures'])
    report=ledger.validate_airline_transaction_artifact_ledger_source_bundle_v01(source)
    f._require(report.validation_status=='PASS','g35_airline_source:'+repr(report.validation_errors))
    valid=runtime.validate_airline_ticket_purchase_corridor_report_against_fixture_bundle_v01(fixtures,source.corridor_report,contract_context=source.corridor_report.contract_context)
    f._require(valid[0],'g35_airline_supplied_corridor:'+repr(valid))
    f._require(c.validate_no_cross_root_authority_transfer_v01(*fixtures.values()).validation_status=='PASS','g35_airline_cross_root')
    inputs,bank=f.g35_validate_root_v01(body['bank_review']);auth=source.payment_authorization_ref
    f._require(bank.target_root_id==c.BANK_ROOT_ID and bank.transaction_id==source.transaction_id and bank.decision=='ACCEPT' and
        bank.selected_candidate_id==auth.authorization_ref_id and bank.decision_id in fixtures['bank_gate'].evidence_refs,'g35_airline_bank_consumption')
    ref='g35:bank_input:'+f.g35_hash_v01(dict(authorization=asdict(auth),approval=asdict(source.purchase_approval_evidence),purchase=asdict(source.purchase_intent)))
    f._require(ref in roots.root_decision_input_to_plain_dict_v01(inputs)['post_vv_bundle']['provided_evidence_refs'],'g35_airline_bank_input')
    run=source.causal_report
    decisions=(run.client_root_decision.decision_id,run.airline_root_resolution.resolution_id,bank.decision_id)
    return [f.g35_fact_v01(root=root,transaction=source.transaction_id,proposal=run.proposal.proposal_id,decision=decision,
        receipts=(receipt,),other_roots=tuple(d for d in decisions if d!=decision)) for root,decision,receipt in
        ((c.CLIENT_ROOT_ID,decisions[0],source.mock_purchase_receipt.receipt_id),(c.AIRLINE_ROOT_ID,decisions[1],source.mock_ticket_receipt.receipt_id),
         (c.BANK_ROOT_ID,decisions[2],auth.source_payment_receipt_id))]
