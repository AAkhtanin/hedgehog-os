"""Domain-to-public-BSEP, C/D CONTROL and actual typed work bindings."""
from dataclasses import asdict, fields, replace
from datetime import datetime, timezone
import hashlib
import json
from hedgehog import drs_semantic_address_v01 as address_api
from hedgehog import drs_memory_resolution_v01 as memory
from hedgehog import drs_g2b_compatibility_v01 as compatibility
from hedgehog import reuse_certificate_v01 as reuse
from hedgehog import local_drs_resolver as resolver
from hedgehog.kernel import root_decision_v01 as roots
from hedgehog.kernel import semantic_work_v01 as semantic_work
from hedgehog.kernel import trust_model_v01 as trust
from hedgehog import context_packets, structured_rationale
from hedgehog import action_commit_packet_v02 as action
from hedgehog import work_execution_host_v01 as hosts
from hedgehog.kernel import abi_v01 as abi
from hedgehog.kernel import execution_mode_router_v01 as router
from hedgehog.kernel import fractal_runtime_v02 as fractal
from hedgehog.kernel import work_composition_v01 as work
from hedgehog.kernel import transition_registry_v01 as transitions
from hedgehog.kernel import continuous_delta_runtime_v01 as delta_api
from hedgehog.kernel import integrity_replay_v01 as integrity
from hedgehog.domains.testflix import contracts_v01 as c
from hedgehog.domains.testflix import mock_world_v01 as world


def review_information_v01(*, transaction, selected, subject, predicate, value, quote, valid, root='root:testflix:user', provenance_ref=None):
    """A real local Root review of bounded information, never action permission."""
    c.require_v01(type(valid) is bool, 'information_validity_type')
    ref = c.identity_v01('information_review', dict(transaction=transaction,selected=selected,value=value))
    source = semantic_work.build_semantic_work_request_v01(request_id='request:'+ref,
        transaction_id=transaction,target_root_id=root,
        runtime_topology_ref=quote['program'].topology_artifact.artifact_id,
        bounded_context_refs=(ref,),permitted_actor_ids=('testflix:information_validator',),
        permitted_contribution_modes=('DETERMINISTIC',),requested_subjects=(subject,),
        required_evidence_classes=('INFORMATION',),forbidden_claims=('create_permission',))
    binding = semantic_work.build_evidence_binding_v01(evidence_id='evidence:'+ref,evidence_ref=ref,
        evidence_class='INFORMATION',source_component_id='testflix:information_validator',
        provenance_ref=quote['results'][0].result.result_id if provenance_ref is None else provenance_ref,evidence_state='PRESENT')
    claim = semantic_work.build_normalized_claim_v01(claim_id=selected,subject=subject,predicate=predicate,
        object_or_value=value,time_envelope_ref=ref,provenance_refs=(ref,),evidence_refs=(binding.evidence_id,),
        confidence_micros=1000000,source_role='deterministic_runtime',source_mode='DETERMINISTIC')
    contribution = semantic_work.build_actor_contribution_v01(contribution_id='contribution:'+ref,
        request_id=source.request_id,actor_id='testflix:information_validator',actor_role='deterministic_runtime',
        contribution_mode='DETERMINISTIC',bsep_projection_ref=quote['program'].candidate.bsep_ref,
        scope=subject,bounded_context_refs=(ref,),claims=(claim,),evidence_bindings=(binding,),
        constraint_bindings=(),uncertainty_bindings=(),requested_validators=(),forbidden_claims_observed=())
    packet = semantic_work.build_root_review_packet_from_contributions_v01(request=source,
        contributions=(contribution,),trust_profiles=trust.build_default_component_trust_profiles_v01())
    kernel = roots.build_root_decision_kernel_v01()
    inputs = roots.build_root_decision_input_v01(transaction_id=transaction,target_root_id=source.target_root_id,
        root_review_packet=packet,
        post_vv_bundle=dict(bundle_id='post_vv:'+ref,post_vv_passed=valid,
            validated_candidate_ids=[selected] if valid else [],rejected_candidate_ids=[] if valid else [selected],
            required_evidence_refs=[ref],provided_evidence_refs=[ref],hard_failure_reasons=[] if valid else ['candidate_validation_failed']),
        gt_advisory=dict(advisory_id='gt:'+ref,candidate_ids=[selected],selected_candidate_id=selected if valid else None,
            score_micros_by_candidate={selected:1000000 if valid else 0},source_artifact_type='GTAdvisoryReport',
            source_lifecycle_state='VALIDATED',actor_role='gt',attempted_effect='CREATE_ROOT_DECISION',
            target_artifact_type='RootDecision',advisory_only=True,creates_final_output=False,requests_effect=False),
        policy_state=dict(policy_id='policy:testflix:information',identity_passed=True,scope_passed=True,
            hard_policy_passed=valid,allow_accept=valid,conflict_policy='DEFER',no_candidate_policy='NO_UPDATE'),
        permission_state=dict(permission_required=False,user_permission_present=False,permission_scope_valid=True,permission_ref=None),
        temporal_state=dict(temporal_valid=True,expired=False,not_before_satisfied=True,time_envelope_ref=ref),
        conflict_state=dict(material_unresolved_conflict=bool(packet.conflict_set_ids),conflict_set_ids=list(packet.conflict_set_ids)),
        prior_root_state=dict(prior_decision_id=None,prior_decision=None,prior_selected_candidate_id=None))
    result = roots.decide_root_v01(kernel=kernel,decision_input=inputs)
    c.require_v01(not roots.validate_root_decision_result_v01(kernel=kernel,decision_input=inputs,result=result), 'information_root_result')
    return dict(source=source,contribution=contribution,review=packet,kernel=kernel,inputs=inputs,result=result)


def summary_facts_v01(report):
    e = report['entitlement']
    return dict(user_id=e.candidate.user_id,entitlement_id=e.entitlement_id,plan=asdict(e.candidate.plan),
        valid_from=e.candidate.valid_from,valid_to=e.candidate.valid_to,renewal=e.candidate.renewal)


def write_summary_v01(drs, report):
    facts = summary_facts_v01(report)
    request = report['request']
    summary = c.canonical_v01(facts).decode()
    fingerprint = hashlib.sha256(summary.encode()).hexdigest()
    scope = hashlib.sha256(c.canonical_v01(dict(user_id=request.user_id,entitlement_id=report['entitlement'].entitlement_id))).hexdigest()
    review = review_information_v01(transaction='transaction:summary:'+request.request_id,
        selected='summary:'+fingerprint,subject=request.user_id,predicate='record_factual_subscription_summary',
        value=facts,quote=report['quote'],valid=report['entitlement_issuance']['output']['candidate_ref']==report['entitlement'].candidate.candidate_id)
    c.require_v01(review['result'].decision=='ACCEPT','summary_root_refusal')
    addr = address_api.build_semantic_address_v01(namespace='testflix',domain='testflix',subject_class='subscription',
        intent_class='informational_summary',meaning_schema_id='testflix.subscription_summary',meaning_schema_version='v0.1')
    time = address_api.build_drs_time_envelope_v01(pt_created_at=request.now,kt_as_of=request.now,
        et_observed_at=request.now,ct_context_anchor=request.now,ttl_seconds=3600,valid_from=request.now,
        valid_to=min(request.now+3600,facts['valid_to']),source_observed_at=request.now,source_reported_at=request.now,
        system_ingested_at=request.now,system_verified_at=request.now,freshness_policy_id='freshness:testflix:summary')
    authority = address_api.build_drs_authority_envelope_v01(authority_class='ROOT_ACCEPTED_WORK',
        owning_local_root_id='root:testflix:user',source_root_decision_input_id=review['inputs'].decision_input_id,
        source_root_decision_id=review['result'].decision_id,
        source_root_decision_hash=hashlib.sha256(c.canonical_v01(roots.root_decision_result_to_plain_dict_v01(review['result']))).hexdigest(),
        authority_scope_fingerprint=scope,root_acceptance_state='ACCEPTED_WORK',recording_component='testflix:summary')
    meaning = address_api.build_meaning_record_v01(semantic_address=addr,predecessor_record_id=None,supersession_reason=None,
        safe_summary=summary,semantic_tags=('subscription',),resonance_reason='Exact subject and subscription identity.',
        memory_pointers=(),artifact_pointers=(),source_reference_ids=(report['entitlement'].issuance_receipt_ref,),
        lineage_edges=(),time_envelope=time,authority_envelope=authority,persistent_lifecycle_state='ACTIVE',
        risk_hints=(),conflict_hints=(),reuse_policy_class='ANSWER_SHORTCUT',policy_version='testflix.summary.v01',
        schema_versions=('testflix.subscription_summary.v01',),content_fingerprint=fingerprint,recording_component='testflix:summary')
    start = datetime.fromtimestamp(request.now,timezone.utc).isoformat()
    end = datetime.fromtimestamp(time.valid_to,timezone.utc).isoformat()
    written = resolver.write_semantic_record(drs,resolver.SemanticDRSRecordInput(record_id=meaning.meaning_record_id,
        domain='testflix',record_type='generic',content=dict(meaning=address_api.meaning_record_to_plain_data_v01(meaning),answer=facts),
        semantic_keys=('subscription',),time_envelope=dict(pt_created_at=start,kt_asof=start,et_observed_at=start,
            ct_session_anchor=request.request_id,ttl_seconds=3600,freshness_class='static',valid_from=start,valid_to=end),
        source_refs=(dict(source='executor',source_id=report['entitlement'].issuance_receipt_ref),)))
    return dict(meaning=meaning,stored=written,stored_bytes=c.canonical_v01(written),review=review)


def resolve_summary_v01(*, drs, writeback, event, quote):
    original = writeback['meaning']
    stored = drs.read_record('work',original.meaning_record_id)
    c.require_v01(stored is not None and c.canonical_v01(stored)==writeback['stored_bytes'],'stored_summary_changed_or_missing')
    # The exact stored public MeaningRecord projection is the source, not a new answer.
    c.require_v01(stored['content']['meaning']==address_api.meaning_record_to_plain_data_v01(original),'stored_meaning_binding')
    scope = hashlib.sha256(c.canonical_v01(dict(user_id=event.user_id,entitlement_id=event.entitlement_id))).hexdigest()
    query = memory.build_drs_temporal_query_v01(query_mode='DIRECT_REUSE_CANDIDATE',
        semantic_address_id=original.semantic_address.semantic_address_id,scope_fingerprint=scope,as_of=event.now,
        evaluation_time=event.now,evaluation_time_source='INJECTED_CURRENT_DECISION_TIME',time_range_start=0,
        time_range_end=event.now+1,required_time_axes=('PT','KT','ET','CT','TTL','VALIDITY'),
        freshness_policy_id=original.time_envelope.freshness_policy_id,max_age_seconds=3600,domain=original.semantic_address.domain,risk_class='LOW',
        reuse_intent='INFORMATIONAL_SHORTCUT_CONSIDERATION',requested_reuse_classes=('ANSWER_SHORTCUT',),
        required_evidence_classes=('SOURCE_IDENTITY','SOURCE_INTEGRITY','PROVENANCE_CHAIN','TIME_FITNESS',
            'POLICY_COMPATIBILITY','SCHEMA_COMPATIBILITY','CONFLICT_CLEARANCE','ROOT_DECISION','SOURCE_HISTORY'),
        forbidden_changes=('POLICY_CHANGED',),policy_version=original.policy_version,
        schema_versions=original.schema_versions,owning_local_root_id=original.authority_envelope.owning_local_root_id)
    evaluated = memory.evaluate_drs_candidate_v01(semantic_address=original.semantic_address,query=query,meaning_record=original)
    c.require_v01(evaluated.eligible_for_ranking,'summary_ineligible:'+repr(evaluated.reason_codes))
    candidate = memory.build_resolution_candidate_v01(query_id=query.query_id,semantic_address_id=query.semantic_address_id,
        meaning_record_id=original.meaning_record_id,query_evaluation_id=evaluated.query_evaluation_id,
        safe_summary=original.safe_summary,evidence_ref_ids=original.source_reference_ids,
        source_history_hash=evaluated.source_history_hash,action_history_binding_id=None,semantic_similarity_units=10000,
        freshness_units=evaluated.current_freshness_units,source_authority_prior_units=10000,lineage_proximity_units=10000,
        historical_utility_units=0,gt_advisory_prior_units=0,conflict_penalty_units=0,risk_penalty_units=0,retrieval_cost_units=1)
    ranked = memory.rank_eligible_drs_candidates_v01(query=query,query_evaluations=(evaluated,),candidates=(candidate,))
    budget = memory.build_memory_descent_budget_v01(max_depth=1,max_records_opened=1,max_pointers_opened=0,
        max_artifacts_opened=0,max_bytes_opened=0,max_lineage_edges=0,max_conflict_records=0)
    plan = memory.build_retrieval_plan_v01(query_id=query.query_id,semantic_address_id=query.semantic_address_id,
        proposed_record_ids=(original.meaning_record_id,),proposed_memory_pointer_ids=(),proposed_artifact_pointer_ids=(),
        requested_descent_class='SUMMARY_ONLY',proposed_budget_id=budget.memory_descent_budget_id,required_access_policy_ids=(),reason_codes=())
    until = original.time_envelope.valid_to
    claim = dict(profile_version='v0.1',semantic_address_id=query.semantic_address_id,meaning_record_id=original.meaning_record_id,
        query_id=query.query_id,query_evaluation_id=evaluated.query_evaluation_id,resolution_candidate_id=candidate.resolution_candidate_id,
        reuse_class='ANSWER_SHORTCUT',case_type='NON_ACTION_INFORMATIONAL',scope_fingerprint=scope,policy_version=query.policy_version,
        schema_versions=list(query.schema_versions),required_evidence_classes=list(query.required_evidence_classes),
        observed_evidence_fingerprint=evaluated.observed_evidence_fingerprint,forbidden_changes=list(query.forbidden_changes),
        checked_dependency_fingerprint=evaluated.checked_dependency_fingerprint,source_history_hash=evaluated.source_history_hash,
        action_history_binding_id=None,valid_from=event.now,valid_to=until,issued_at=event.now,evaluated_at=event.now,
        root_shortcut_policy_ref='policy:drs_answer_shortcut:v0.1')
    review = review_information_v01(transaction=query.query_id,selected=candidate.resolution_candidate_id,
        subject=query.semantic_address_id,predicate='authorize_non_action_informational_answer_shortcut_v01',value=claim,
        quote=quote,valid=evaluated.eligible_for_ranking and ranked==(candidate,),root=query.owning_local_root_id)
    root_hash = action.domain_separated_sha256_hex_v01(domain='hedgehog:drs:root_shortcut_root_result_binding:v01',
        payload=c.canonical_v01(roots.root_decision_result_to_plain_dict_v01(review['result'])))
    projection = reuse.build_root_shortcut_authorization_projection_v01(owning_local_root_id=query.owning_local_root_id,
        root_kernel_id=review['kernel'].kernel_id,root_decision_input_id=review['inputs'].decision_input_id,
        root_decision_id=review['result'].decision_id,root_decision_hash=root_hash,selected_candidate_id=candidate.resolution_candidate_id,
        semantic_address_id=query.semantic_address_id,meaning_record_id=original.meaning_record_id,query_id=query.query_id,
        query_evaluation_id=evaluated.query_evaluation_id,allowed_reuse_class='ANSWER_SHORTCUT',scope_fingerprint=scope,
        policy_version=query.policy_version,schema_versions=query.schema_versions,valid_from=event.now,valid_to=until,
        root_shortcut_policy_ref=claim['root_shortcut_policy_ref'])
    certificate = reuse.build_reuse_certificate_v01(semantic_address_id=query.semantic_address_id,meaning_record_id=original.meaning_record_id,
        query_id=query.query_id,query_evaluation_id=evaluated.query_evaluation_id,resolution_candidate_id=candidate.resolution_candidate_id,
        root_shortcut_authorization_projection=projection,case_type=claim['case_type'],required_evidence_classes=query.required_evidence_classes,
        observed_evidence_fingerprint=evaluated.observed_evidence_fingerprint,forbidden_changes=query.forbidden_changes,
        checked_dependency_fingerprint=evaluated.checked_dependency_fingerprint,valid_from=event.now,valid_to=until,
        reuse_class='ANSWER_SHORTCUT',source_history_hash=evaluated.source_history_hash,action_history_binding_id=None,
        issued_at=event.now,evaluated_at=event.now)
    legacy = compatibility.project_legacy_drs_source_v01(source_family='LOCAL_DRS_DICT',source=stored,
        target_semantic_address=original.semantic_address,target_meaning_record=None)
    c.require_v01(compatibility.validate_legacy_drs_projection_v01(legacy)[0],'stored_compatibility')
    report = memory.build_drs_resolution_report_v01(semantic_address=original.semantic_address,query=query,source_projections=(legacy,),
        source_records=(original,),query_evaluations=(evaluated,),eligible_candidates=(candidate,),
        ranked_candidate_ids=tuple(v.resolution_candidate_id for v in ranked),selected_candidate_id=candidate.resolution_candidate_id,
        retrieval_plan=plan,memory_descent_result=None,root_shortcut_projection=projection,reuse_certificate=certificate,
        context_only_record_ids=(),historical_only_record_ids=(),warning_only_record_ids=(),rerun_required_record_ids=(),blocked_record_ids=(),
        provider_calls=0,network_calls=0,gemini_calls=0,external_drs_calls=0,connector_calls=0,real_world_effects_count=0,
        final_status=abi.STATUS_PASS,reason_codes=())
    ok,reasons = reuse.validate_existing_root_shortcut_decision_v01(resolution_report=report,root_kernel=review['kernel'],
        root_decision_input=review['inputs'],root_decision_result=review['result'],use_time=event.now)
    c.require_v01(ok,'summary_shortcut:'+repr(reasons))
    return dict(event=event,stored=stored,report=report,review=review,budget=budget,answer=json.loads(candidate.safe_summary))


def write_quote_summary_v01(drs, original, event, quote):
    """Bank-local memory of a real controlled quote, not permission to pay it."""
    c.validate_provider_quote_v01(quote)
    c.require_v01(quote.observed_at<=event.now<quote.valid_to,'quote_memory_current_source')
    facts = dict(quote=asdict(quote),quote_id=quote.quote_id,entitlement_id=event.entitlement_id,
        user_id=event.user_id,plan=asdict(quote.plan))
    summary = c.canonical_v01(facts).decode();fingerprint = hashlib.sha256(summary.encode()).hexdigest()
    scope = hashlib.sha256(c.canonical_v01(dict(user_id=event.user_id,entitlement_id=event.entitlement_id))).hexdigest()
    review = review_information_v01(transaction='transaction:quote-memory:'+event.request_id,
        selected='summary:'+fingerprint,subject=quote.quote_id,predicate='record_observed_renewal_quote',value=facts,
        quote=original['quote'],valid=quote.merchant_id==original['request'].merchant_id,
        root='root:testflix:bank',provenance_ref=quote.quote_id)
    c.require_v01(review['result'].decision=='ACCEPT','quote_memory_root_refusal')
    addr = address_api.build_semantic_address_v01(namespace='testflix',domain='TESTFLIX',subject_class='renewal_quote',
        intent_class='informational_summary',meaning_schema_id='testflix.renewal_quote',meaning_schema_version='v0.1')
    time = address_api.build_drs_time_envelope_v01(pt_created_at=event.now,kt_as_of=quote.observed_at,
        et_observed_at=quote.observed_at,ct_context_anchor=event.now,ttl_seconds=3600,valid_from=event.now,
        valid_to=quote.valid_to,source_observed_at=quote.observed_at,source_reported_at=quote.observed_at,
        system_ingested_at=event.now,system_verified_at=event.now,freshness_policy_id='freshness:testflix:quote')
    authority = address_api.build_drs_authority_envelope_v01(authority_class='ROOT_ACCEPTED_WORK',
        owning_local_root_id='root:testflix:bank',source_root_decision_input_id=review['inputs'].decision_input_id,
        source_root_decision_id=review['result'].decision_id,
        source_root_decision_hash=hashlib.sha256(c.canonical_v01(roots.root_decision_result_to_plain_dict_v01(review['result']))).hexdigest(),
        authority_scope_fingerprint=scope,root_acceptance_state='ACCEPTED_WORK',recording_component='testflix:quote-memory')
    meaning = address_api.build_meaning_record_v01(semantic_address=addr,predecessor_record_id=None,supersession_reason=None,
        safe_summary=summary,semantic_tags=('renewal_quote',),resonance_reason='Recorded quote for the named paid period.',
        memory_pointers=(),artifact_pointers=(),source_reference_ids=(quote.quote_id,),lineage_edges=(),time_envelope=time,
        authority_envelope=authority,persistent_lifecycle_state='ACTIVE',risk_hints=(),conflict_hints=(),reuse_policy_class='ANSWER_SHORTCUT',
        policy_version='testflix.quote.v01',schema_versions=('testflix.renewal_quote.v01',),content_fingerprint=fingerprint,
        recording_component='testflix:quote-memory')
    start = datetime.fromtimestamp(event.now,timezone.utc).isoformat();end = datetime.fromtimestamp(quote.valid_to,timezone.utc).isoformat()
    written = resolver.write_semantic_record(drs,resolver.SemanticDRSRecordInput(record_id=meaning.meaning_record_id,
        domain='TESTFLIX',record_type='generic',content=dict(meaning=address_api.meaning_record_to_plain_data_v01(meaning),answer=facts),
        semantic_keys=('renewal_quote',),time_envelope=dict(pt_created_at=start,kt_asof=start,et_observed_at=start,
            ct_session_anchor=event.request_id,ttl_seconds=3600,freshness_class='static',valid_from=start,valid_to=end),
        source_refs=(dict(source='system',source_id=quote.quote_id),)))
    writeback = dict(meaning=meaning,stored=written,stored_bytes=c.canonical_v01(written),review=review)
    informational = c.InformationRequestV01(event.request_id+':quote-memory',event.user_id,event.entitlement_id,event.now)
    resolved = resolve_summary_v01(drs=drs,writeback=writeback,event=informational,quote=original['quote'])
    c.require_v01(resolved['answer']==facts,'quote_memory_answer_binding')
    return writeback,resolved


def bsep_source_v01(request, semantic, domain='TESTFLIX'):
    ref = semantic['semantic_ref']
    plan = semantic['selected_plan']
    fact = c.canonical_v01(dict(plan=asdict(plan), source=ref, hard_ceiling_minor=request.hard_ceiling_minor)).decode()
    route_id = 'route:testflix:bounded'
    vectors = ('vector:' + ref,)
    guards = ('guard:testflix:local_root',)
    business = context_packets.build_business_request_context_packet(packet_id='business:' + request.request_id,
        created_by='testflix:local_intake', domain=domain, request_id=request.request_id,
        business_subject='subscription_and_local_playback', requested_action='bounded_review', user_visible_summary='Review a bounded subscription quote')
    source_ref = dict(source='G2C_BUSINESS_REQUEST_CONTEXT_PACKET_V01', packet_id=business['packet_id'],
        request_id=request.request_id, domain_id=domain)
    route = context_packets.build_orchestrator_route_context_packet(packet_id='route_context:' + ref,
        created_by='testflix:canonicalization', source_refs=(source_ref,), domain=domain, allowed_routes=(route_id,),
        required_guards=guards, selected_vector_ids=vectors,
        route_validation_expectations=dict(root_review_required=True,selected_only_allowed_vectors=True),
        orchestrator_is_root=False, creates_action_commit_packet=False, calls_connectors=False)
    proposal = dict(proposal_id='route_proposal:' + ref, suggested_route=route_id, selected_vector_ids=vectors,
        required_guards=guards, reason='Selected bounded catalog proposal requires source-bound review.', confidence=0.75,
        needs_review=True, uncertainty_notes=('Controlled proposal is not authority.',), root_review_required=True,
        truth_claimed=False, authority_claimed=False, action_permission_claimed=False, final_output_claimed=False,
        connector_command_claimed=False, drs_write_claimed=False, plan_graph_claimed=False, bypass_root_claimed=False,
        semantic_observations=(fact,), route_reasoning=('Review actual proposed quote.',),
        rejected_route_reasoning=('No direct action from semantic output.',), guard_reasoning=('Independent local Roots required.',),
        vector_reasoning=('Actual selected catalog record.',), authority_boundary_reasoning=('Root alone accepts.',))
    rationale = structured_rationale.build_orchestrator_structured_rationale(observed_semantics=proposal['semantic_observations'],
        route_selection_reason=proposal['route_reasoning'], rejected_routes=proposal['rejected_route_reasoning'],
        required_guards_reasoning=proposal['guard_reasoning'], selected_vector_reasoning=proposal['vector_reasoning'],
        uncertainty_notes=proposal['uncertainty_notes'], authority_boundary=proposal['authority_boundary_reasoning'], root_review_required=True)
    def evidence(text, kind):
        return context_packets.semantic_evidence_item(text, source='runtime_canonicalization', evidence_kind=kind, confidence_label='medium')
    bsep = context_packets.build_bounded_semantic_evidence_packet(packet_id='bsep:' + ref, source_refs=(source_ref,),
        domain=domain, source_role='orchestrator', target_role='architect', source_route_id=route_id,
        source_proposal_id=proposal['proposal_id'], source_context_packet_id=route['packet_id'],
        source_structured_rationale_ref='structured_rationale_v01:' + hashlib.sha256(c.canonical_v01(rationale)).hexdigest(),
        observed_semantic_facts=(evidence(fact,'observed_fact'),), missing_evidence=(evidence('Local Root review pending.','missing_evidence'),),
        uncertainty_notes=(evidence('Controlled proposal only.','uncertainty'),), risk_boundary_notes=(evidence('Evidence is not action permission.','risk_boundary'),),
        rejected_action_routes=(evidence('Semantic output cannot execute.','rejected_route'),),
        required_approvals_or_conditions=(evidence('Each owning Root reviews independently.','approval_condition'),),
        authority_boundary_notes=(evidence('No authority transfer.','authority_boundary'),), selected_vector_ids=vectors, required_guards=guards)
    return router.build_execution_mode_source_context_v01(business_request_context_packet=business,bsep_packet=bsep,
        bsep_route_context_packet=route,bsep_orchestrator_proposal=proposal,bsep_structured_rationale=rationale,
        sealed_replay_evidence=None,replay_source_manifest=None,replay_source_domain_projection=None,
        replay_source_safe_file_contents=(),replay_anchor_publication=None,replay_anchored_verification=None,
        replay_supplied_anchor_publication_id=None,replay_reconstructed_manifest=None,replay_reconstructed_domain_projection=None,
        replay_reconstructed_safe_file_contents=(),g2a_inspection=None,g2a_registry=None,g2a_packet_id=None,
        g2a_corridor=None,g2a_corridor_step=None,g2a_current_dependency_observations=(),g2a_logical_time_bridge=None,
        g2a_evaluation_time=request.now,g2a_evaluation_time_source='testflix.controlled_utc',g2a_evaluation_context_id='context:testflix:review',
        g2a_transition_registry_profile=None,g2b_resolution_report=None,g2b_compatibility_projections=(),g2b_use_time=None,
        g2b_root_kernel=None,g2b_root_decision_input=None,g2b_root_decision_result=None,g2b_writeback_evidence=None)


def literal_v01(name, kind, value):
    return work.WorkInputBindingV01(name, work.WorkLiteralV01(action.build_action_effect_parameter_record_v01(
        parameter_name=name,value_type=kind,value=value)))


def route_summary_v01(original, information):
    event = information['event']; report = information['report']; review = information['review']
    request = replace(original['request'],request_id=event.request_id,now=event.now)
    source = bsep_source_v01(request,dict(semantic_ref=report.source_records[0].meaning_record_id,
        selected_plan=c.PlanV01(**information['answer']['plan'])),domain=report.query.domain)
    identities = dict(request_id=event.request_id,transaction_id=report.query.query_id,
        owning_root_id='root:testflix:user',domain_id=report.query.domain)
    profiles = tuple(router.build_execution_mode_local_mode_profile_v01(**identities,mode=mode,
        policy_snapshot_id='policy:testflix:information',capability_snapshot_id='caps:testflix:local',cost_model_id='cost:testflix:bounded',
        policy_allowed=mode in ('direct_informational_reuse','memory_informed'),scope_allowed=True,risk_allowed=True,privacy_allowed=True,
        capability_state='NOT_REQUIRED' if mode in ('sealed_replay','direct_informational_reuse') else 'AVAILABLE',
        capability_id=None if mode in ('sealed_replay','direct_informational_reuse') else 'capability:testflix:'+mode,
        cost_units=index+1) for index,mode in enumerate(router.EXECUTABLE_EXECUTION_MODES_V01))
    start = datetime.fromtimestamp(event.now,timezone.utc).isoformat()
    end = datetime.fromtimestamp(event.now+60,timezone.utc).isoformat()
    scope = report.query.scope_fingerprint
    snapshot = router.build_execution_mode_local_routing_snapshot_v01(**identities,request_class='INFORMATIONAL',
        action_class='NON_ACTION',action_packet_relation='NOT_APPLICABLE',scope_class='BOUNDED',scope_ref='scope:'+scope,
        permitted_narrower_scope_refs=(),risk_class='LOW',policy_snapshot_id='policy:testflix:information',
        capability_snapshot_id='caps:testflix:local',cost_model_id='cost:testflix:bounded',required_user_input_state='COMPLETE',hard_block_state='CLEAR',
        evaluation_time_epoch_seconds=event.now,pt_created_at_utc=start,et_observed_at_utc=start,ct_session_anchor=event.request_id,
        ttl_seconds=60,freshness_class='static',valid_from_utc=start,valid_to_utc=end,mode_profiles=profiles)
    source = router.build_execution_mode_source_context_v01(**dict({f.name:getattr(source,f.name) for f in fields(source)},
        g2a_evaluation_time=event.now,g2a_evaluation_time_source=snapshot.created_by,g2a_evaluation_context_id=snapshot.local_routing_snapshot_id,
        g2b_resolution_report=report,g2b_compatibility_projections=report.source_projections,g2b_use_time=event.now,
        g2b_root_kernel=review['kernel'],g2b_root_decision_input=review['inputs'],g2b_root_decision_result=review['result']))
    routing = router.build_execution_mode_router_input_v01(request_id=event.request_id,transaction_id=report.query.query_id,
        owning_root_id=identities['owning_root_id'],bsep_binding=router.build_execution_mode_bsep_binding_v01(**identities,source_context=source),
        local_routing_snapshot=snapshot,replay_binding=router.build_execution_mode_replay_not_applicable_binding_v01(**identities),
        g2a_binding=router.build_execution_mode_g2a_no_packet_binding_v01(**identities,evaluation_time=event.now,
            evaluation_time_source=snapshot.created_by,evaluation_context_id=snapshot.local_routing_snapshot_id),
        g2b_binding=router.build_execution_mode_g2b_binding_v01(**identities,source_context=source))
    proposal,validation = router.route_execution_mode_v01(router_input=routing,source_context=source)
    c.require_v01(validation.validation_status=='PASS' and proposal.selected_mode=='direct_informational_reuse',
        'informational_route:'+repr((validation,proposal.selected_mode)))
    artifact = router.project_execution_mode_proposal_kernel_artifact_v01(proposal=proposal,router_input=routing,source_context=source)
    registry = transitions.build_execution_mode_transition_registry_profile_v01()
    before = router.evaluate_execution_mode_proposal_to_root_transition_v01(registry=registry,proposal=proposal,
        router_input=routing,source_context=source,proposal_artifact=artifact)
    root_review = router.build_root_execution_mode_review_input_v01(proposal=proposal,router_input=routing,source_context=source,
        proposal_artifact=artifact,proposal_transition_decision=before,review_action='ACCEPT',accepted_scope_ref='scope:'+scope,narrowing_basis_refs=())
    decision,root_kernel,root_input,root_result,validated = router.review_execution_mode_proposal_v01(review_input=root_review,
        proposal=proposal,router_input=routing,source_context=source,proposal_artifact=artifact,proposal_transition_decision=before)
    c.require_v01(validated.validation_status=='PASS' and decision.outcome=='ACCEPT','information_route_root')
    return dict(review_input=root_review,decision=decision,proposal=proposal,router_input=routing,source_context=source,
        proposal_artifact=artifact,proposal_transition_decision=before,root_kernel=root_kernel,
        root_decision_input=root_input,root_decision_result=root_result)


def materialize_v01(candidate, common, items):
    args = {f.name:getattr(candidate,f.name) for f in fields(candidate) if f.name != 'revision_id'}
    updated = work.build_work_program_candidate_v01(**dict(args,items=tuple(items)), **common)
    return work.materialize_work_program_v01(updated, **common)


def exact_d_source_v01(program, common, now, *, information=None, child_scopes=()):
    child_scopes = tuple(sorted(child_scopes))
    candidate = program.candidate
    item = next(i for i in candidate.items if i.work_id == 'quote')
    scope = work.build_work_review_scope_ref_v01(candidate=candidate,item=item,
        source_context=common['source_context'],semantic_proposal=common['semantic_proposal'])
    identities = dict(request_id=candidate.task_id,transaction_id=common['semantic_proposal'].transaction_id,
        owning_root_id=item.owning_root_id,domain_id='TESTFLIX')
    profiles = tuple(router.build_execution_mode_local_mode_profile_v01(**identities, mode=mode,
        policy_snapshot_id='policy:testflix:quote_review',capability_snapshot_id='caps:testflix:local',cost_model_id='cost:testflix:bounded',
        policy_allowed=mode == 'full_fractal',scope_allowed=True,risk_allowed=True,privacy_allowed=True,
        capability_state='NOT_REQUIRED' if mode in ('sealed_replay','direct_informational_reuse') else 'AVAILABLE',
        capability_id=None if mode in ('sealed_replay','direct_informational_reuse') else 'capability:testflix:' + mode,
        cost_units=index+1) for index,mode in enumerate(router.EXECUTABLE_EXECUTION_MODES_V01))
    start = datetime.fromtimestamp(now, timezone.utc).isoformat()
    end = datetime.fromtimestamp(now+3600, timezone.utc).isoformat()
    snapshot = router.build_execution_mode_local_routing_snapshot_v01(**identities,request_class='BOUNDED_REVIEW',
        action_class='NON_ACTION',action_packet_relation='NOT_APPLICABLE',scope_class='BOUNDED',scope_ref=scope,
        permitted_narrower_scope_refs=child_scopes,risk_class='LOW',policy_snapshot_id='policy:testflix:quote_review',
        capability_snapshot_id='caps:testflix:local',cost_model_id='cost:testflix:bounded',required_user_input_state='COMPLETE',hard_block_state='CLEAR',
        evaluation_time_epoch_seconds=now,pt_created_at_utc=start,et_observed_at_utc=start,ct_session_anchor='session:'+candidate.task_id,
        ttl_seconds=3600,freshness_class='static',valid_from_utc=start,valid_to_utc=end,mode_profiles=profiles)
    old = common['source_context']
    changes = dict(g2a_evaluation_time=now,g2a_evaluation_time_source=snapshot.created_by,g2a_evaluation_context_id=snapshot.local_routing_snapshot_id)
    if information is not None:
        report = information['report']; review = information['review']
        changes.update(g2b_resolution_report=report,g2b_compatibility_projections=report.source_projections,g2b_use_time=now,
            g2b_root_kernel=review['kernel'],g2b_root_decision_input=review['inputs'],g2b_root_decision_result=review['result'])
    source = router.build_execution_mode_source_context_v01(**dict({f.name:getattr(old,f.name) for f in fields(old)},**changes))
    routing = router.build_execution_mode_router_input_v01(request_id=candidate.task_id,transaction_id=identities['transaction_id'],
        owning_root_id=item.owning_root_id,bsep_binding=router.build_execution_mode_bsep_binding_v01(**identities,source_context=source),
        local_routing_snapshot=snapshot,replay_binding=router.build_execution_mode_replay_not_applicable_binding_v01(**identities),
        g2a_binding=router.build_execution_mode_g2a_no_packet_binding_v01(**identities,evaluation_time=now,
            evaluation_time_source=snapshot.created_by,evaluation_context_id=snapshot.local_routing_snapshot_id),
        g2b_binding=router.build_execution_mode_g2b_not_applicable_binding_v01(**identities) if information is None else
            router.build_execution_mode_g2b_binding_v01(**identities,source_context=source))
    proposal, report = router.route_execution_mode_v01(router_input=routing,source_context=source)
    c.require_v01(report.validation_status == 'PASS' and proposal.selected_mode == 'full_fractal','quote_route_invalid')
    artifact = router.project_execution_mode_proposal_kernel_artifact_v01(proposal=proposal,router_input=routing,source_context=source)
    registry = transitions.build_execution_mode_transition_registry_profile_v01()
    before = router.evaluate_execution_mode_proposal_to_root_transition_v01(registry=registry,proposal=proposal,
        router_input=routing,source_context=source,proposal_artifact=artifact)
    review = router.build_root_execution_mode_review_input_v01(proposal=proposal,router_input=routing,source_context=source,
        proposal_artifact=artifact,proposal_transition_decision=before,review_action='ACCEPT',accepted_scope_ref=scope,narrowing_basis_refs=())
    decision,kernel,root_input,root_result,reviewed = router.review_execution_mode_proposal_v01(review_input=review,
        proposal=proposal,router_input=routing,source_context=source,proposal_artifact=artifact,proposal_transition_decision=before)
    c.require_v01(reviewed.validation_status == 'PASS' and decision.outcome == 'ACCEPT','quote_root_route_refused')
    roots = dict(review_input=review,decision=decision,proposal=proposal,router_input=routing,source_context=source,
        proposal_artifact=artifact,proposal_transition_decision=before,root_kernel=kernel,root_decision_input=root_input,root_decision_result=root_result)
    decision_artifact = router.project_root_execution_mode_decision_kernel_artifact_v01(**roots)
    after = router.evaluate_execution_mode_root_route_transition_v01(registry=registry,**roots,decision_artifact=decision_artifact)
    eligibility = router.project_execution_mode_route_eligibility_kernel_artifact_v01(**roots,decision_artifact=decision_artifact,
        root_route_transition_decision=after)
    policy = fractal.build_fractal_runtime_policy_v02(required_downstream_capability_ids=proposal.required_downstream_capability_ids,
        permitted_child_scope_refs=child_scopes)
    arguments = dict(roots)
    arguments['g2c_source_context'] = arguments.pop('source_context')
    runtime_source = fractal.build_fractal_runtime_source_context_v02(**arguments,transition_registry=registry,
        decision_artifact=decision_artifact,root_route_transition_decision=after,route_eligibility_artifact=eligibility,runtime_policy=policy)
    return runtime_source,dict(common,source_context=source)


def collect_quote_work_v01(request, semantic, *, host_pair=None, root='root:testflix:user', information=None, child_scopes=(), period_start=None,
    paid_period_basis=None):
    plan = semantic['selected_plan']
    source = bsep_source_v01(request,semantic)
    start = datetime.fromtimestamp(request.now,timezone.utc).isoformat()
    end = datetime.fromtimestamp(request.now+3600,timezone.utc).isoformat()
    proposal = abi.build_kernel_artifact_v01(abi_version='v1.0',artifact_id=semantic['semantic_ref'],
        artifact_type='SemanticArchitectProposal',schema_version='v1',transaction_id='transaction:'+request.request_id+':user' if information is None else information['report'].query.query_id,
        owner_root_id=root,source_component='semantic_architect',authority_class='ADVISORY',lifecycle_state='PROPOSED',
        payload=dict(selected_plan=asdict(plan),semantic_contributions=list(semantic['contributions'])),
        trace_refs=('intent:'+request.request_id,),parent_refs=(source.bsep_packet['packet_id'],),
        time_envelope=dict(pt_created_at=start,kt_asof=start,et_observed_at=None,ct_session_anchor='session:'+request.request_id,
            ttl_seconds=3600,freshness_class='static',valid_from=start,valid_to=end))
    if host_pair is None:
        quote = world.admit_v01('testflix.quote.v01',root,(('plan_id','REFERENCE'),('price_minor','INTEGER'),('period_seconds','INTEGER')),
            (('plan_id','REFERENCE'),('price_minor','INTEGER'),('period_seconds','INTEGER'),('quote_ref','REFERENCE')))
        period = world.admit_v01('testflix.period.v01',root,(('quote_ref','REFERENCE'),('period_seconds','INTEGER'),('now','INTEGER')),
            (('quote_ref','REFERENCE'),('valid_to','INTEGER')))
    else:
        catalogue = host_pair[0].admitted_catalogue
        quote = next(a for a in catalogue if a.definition.operation_id=='testflix.quote.v01')
        period = next(a for a in catalogue if a.definition.operation_id=='testflix.period.v01')
    common = dict(catalogue=(quote,period),source_context=source,semantic_proposal=proposal)
    first = work.WorkItemV01('quote',quote.definition.definition_id,root,
        tuple(literal_v01(n,t,v) for n,t,v in (('plan_id','REFERENCE',plan.plan_id),('price_minor','INTEGER',plan.price_minor),
            ('period_seconds','INTEGER',plan.period_seconds))),(),(),None,None)
    second = work.WorkItemV01('period',period.definition.definition_id,root,
        (work.WorkInputBindingV01('quote_ref',work.WorkOutputBindingV01('quote','quote_ref','REFERENCE')),
         work.WorkInputBindingV01('period_seconds',work.WorkOutputBindingV01('quote','period_seconds','INTEGER')),
         literal_v01('now','INTEGER',request.now if period_start is None else period_start)),(),('quote',),None,None)
    if paid_period_basis is not None:
        entitlement, paid_quote = paid_period_basis
        c.require_v01(type(entitlement) is c.EntitlementV01 and period_start==entitlement.candidate.valid_to and
            paid_quote['plan_id']==entitlement.candidate.plan.plan_id==plan.plan_id and
            paid_quote['period_seconds']==entitlement.candidate.plan.period_seconds==plan.period_seconds,
            'independent_paid_period_basis')
        second = replace(second, inputs=(literal_v01('quote_ref','REFERENCE',paid_quote['quote_ref']),
            literal_v01('period_seconds','INTEGER',entitlement.candidate.plan.period_seconds),
            literal_v01('now','INTEGER',entitlement.candidate.valid_to)), depends_on=())
    candidate = work.build_work_program_candidate_v01(task_id=request.request_id,previous_revision_id=None,intent_ref='intent:'+request.request_id,
        bsep_ref=source.bsep_packet['packet_id'],semantic_proposal_ref=proposal.artifact_id,catalogue_revision=0,
        budget=work.WorkBudgetV01(8,8,0,8,0),items=(first,second),trigger_evidence_refs=(),**common)
    program = work.materialize_work_program_v01(candidate,**common)
    d_source,common = exact_d_source_v01(program,common,request.now,information=information,child_scopes=child_scopes)
    base = materialize_v01(program.candidate,common,(first,second))
    obligation = work.build_work_review_obligation_v01(candidate=base.candidate,item=first,source_context=d_source)
    first = replace(first,review_obligation_id=obligation.obligation_id)
    program = materialize_v01(base.candidate,common,(first,second))
    obligation = work.build_work_review_obligation_v01(candidate=program.candidate,item=first,source_context=d_source)
    bundle,d_report = fractal.run_fractal_runtime_v02(d_source)
    c.require_v01(d_report.status == 'PASS' and bundle is not None,'quote_D_control_failure')
    ok,reasons = work.validate_work_review_binding_v01(obligation,candidate=program.candidate,item=first,
        source_context=d_source,execution_bundle=bundle,semantic_proposal=proposal)
    c.require_v01(ok,'quote_D_context:' + repr(reasons))
    if host_pair is None:
        trusted = world.LocalSourceV01(request.now)
        host = hosts.build_root_work_execution_host_v01(owning_root_id=root,registry=action.build_empty_action_commit_packet_registry_v02(),
            catalogue=common['catalogue'],packet_bindings=(),current_dependency_observations=(),
            logical_time_bridge=trusted.snapshot.logical_time_bridge,trusted_source=trusted)
    else:
        host,trusted = host_pair
    bindings = ((obligation,d_source,bundle),)
    results = work.advance_work_program_v01(program,**common,host_map={root:host},review_bindings=bindings)
    ok,reasons = work.validate_work_program_result_v01(program,results,**common,host_map={root:host},review_bindings=bindings)
    c.require_v01(ok and all(r.status == 'COMPLETED' for r in results),'quote_work_result:' + repr(reasons))
    return dict(program=program,common=common,host=host,trusted=trusted,obligation=obligation,d_source=d_source,
        d_bundle=bundle,d_report=d_report,results=results,host_attempts=host.work_attempts,host_events=host.events)


def delta_artifact_v01(payload, transaction, root, now, *, parents=()):
    identity = c.identity_v01('delta_source',dict(payload=payload,transaction=transaction,root=root,now=now,parents=parents))
    timestamp = datetime.fromtimestamp(now,timezone.utc).isoformat()
    return abi.build_kernel_artifact_v01(abi_version='v1.0',artifact_id=identity,artifact_type='SemanticEvidence',schema_version='v1',
        transaction_id=transaction,owner_root_id=root,source_component='testflix:delta_source',authority_class='EVIDENCE_ONLY',
        lifecycle_state='VALIDATED',payload=payload,trace_refs=('trace:'+identity,),parent_refs=parents,
        time_envelope=dict(pt_created_at=timestamp,kt_asof=timestamp,et_observed_at=timestamp,ct_session_anchor=transaction,
            ttl_seconds=3600,freshness_class='static',valid_from=timestamp,
            valid_to=datetime.fromtimestamp(now+3600,timezone.utc).isoformat()))


def delta_material_v01(pending, observed_quote, baseline, evaluation_time, *, current_capture=None):
    """Actual packet-local dependency and independently scoped D projection sources."""
    c.validate_provider_quote_v01(observed_quote)
    payment = pending['payment'];canonical = payment['bound'].canonical_projection
    transaction = canonical.transaction_id;root = canonical.owning_local_root_id
    c.require_v01(baseline.runtime_report.transaction_id==transaction and baseline.runtime_report.owning_root_id==root,
        'delta_actual_bank_baseline')
    prior = canonical.dependency_candidate.dependency_records[0]
    changed_evidence = dict(payment['evidence'],provider_quote=asdict(observed_quote))
    changed_hash = action.domain_separated_sha256_hex_v01(domain='testflix.authoritative_dependency.v01',payload=c.canonical_v01(changed_evidence))
    invalidation = action.build_action_invalidation_evidence_v01(source_invalidation_event_ref=observed_quote.quote_id,
        packet_id=payment['bound'].packet_identity.packet_id,dependency_id=prior.dependency_id,invalidation_class='DEPENDENCY_CHANGED',
        evidence_ref=prior.evidence_ref,evidence_sha256=changed_hash,observed_status='CHANGED',time_envelope_id=prior.time_envelope_id,
        freshness_policy_id=prior.freshness_policy_id,owning_local_root_id=root,accepted_by_local_root_id=root,
        authority_effect='DETERMINISTIC_BLOCK',evaluation_time=evaluation_time,evaluation_time_source='testflix.controlled_utc',
        evaluation_context_id='context:testflix:quote_delta' if current_capture is None else current_capture.evaluation_context_id)
    c.require_v01(action.validate_action_invalidation_evidence_against_packet_v01(invalidation,payment['bound'])[0],
        'delta_actual_packet_observation')
    prior_body = dict(asdict(prior),source_provenance_refs=list(prior.source_provenance_refs),provider_quote=asdict(pending['provider_quote']))
    original = delta_artifact_v01(prior_body,transaction,root,pending['provider_quote'].observed_at)
    changed_body = dict(prior_body,content_sha256=changed_hash,provider_quote=asdict(observed_quote),observed_status=invalidation.observed_status,
        invalidation_evidence_id=invalidation.invalidation_evidence_id,packet_id=invalidation.packet_id)
    observed = delta_artifact_v01(changed_body,transaction,root,observed_quote.observed_at,parents=(original.artifact_id,))
    projections = []
    period_item = next(v for v in pending['quote_work']['program'].candidate.items if v.work_id=='period')
    c.require_v01(all(type(v.source) is work.WorkLiteralV01 for v in period_item.inputs),
        'delta_paid_period_must_be_independent')
    topology = baseline.topology;source = baseline.source_context
    for index in (0,1):
        child_id = fractal.derive_fractal_child_cell_id_v02(topology_seed_id=topology.topology_seed_id,
            parent_cell_id=topology.root_cell_id,canonical_child_index=index,accepted_mode=topology.accepted_mode,
            selected_local_mode_profile_id=source.proposal.selected_local_mode_profile_id,
            source_mode_profile_set_id=source.router_input.local_routing_snapshot.mode_profile_set_id,
            child_scope_ref=topology.accepted_scope_ref,runtime_policy_id=topology.runtime_policy_id,
            required_capability_ids=source.proposal.required_downstream_capability_ids,
            forbidden_claims=source.runtime_policy.forbidden_claims,child_depth=1)
        cells = tuple(v for v in baseline.cell_inputs if v.cell_id==child_id and
            v.scope_ref==topology.accepted_scope_ref and v.parent_cell_id==topology.root_cell_id)
        c.require_v01(len(cells)==1,'delta_child_scope_identity')
        cell = cells[0]
        entries = tuple(v for v in baseline.queue_entries if v.cell_id==cell.cell_id and v.predecessor_queue_entry_id is None)
        c.require_v01(bool(entries),'delta_initial_queue')
        entry = min(entries,key=lambda v:(v.canonical_priority,v.node_instance_sequence,v.snapshot_sequence))
        artifact = next(a for q,a in zip(baseline.queue_entries,baseline.queue_artifacts,strict=True) if q.queue_entry_id==entry.queue_entry_id)
        plain = abi.kernel_artifact_to_plain_dict_v01(artifact)
        projection = delta_artifact_v01(dict(projection_profile_id='g2e_baseline_runtime_artifact_projection_v01',
            projected_runtime_artifact=plain,projected_runtime_artifact_sha256=hashlib.sha256(c.canonical_v01(plain)).hexdigest()),
            transaction,root,pending['event'].now,parents=(artifact.artifact_id,))
        projections.append((cell,entry,artifact,projection))
    period_result = next(v for v in pending['quote_work']['results'] if v.work_id=='period')
    periods = tuple(v for v in pending['before']['entitlements'] if v.entitlement_id==pending['event'].entitlement_id)
    c.require_v01(len(periods)==1,'delta_paid_period_identity')
    paid_period = delta_artifact_v01(dict(entitlement=asdict(periods[0]),
        inputs=[asdict(v) for v in period_item.inputs],output=world.values_v01(period_result.result.output)),
        transaction,root,pending['event'].now)
    baseline_artifacts = (original,projections[0][3],paid_period,projections[1][3])
    observed_artifacts = (observed,*baseline_artifacts[1:])
    replay_edges = (integrity.ArtifactDependencyEdgeV01(projections[0][3].artifact_id,original.artifact_id),
        integrity.ArtifactDependencyEdgeV01(projections[1][3].artifact_id,paid_period.artifact_id))
    manifest = integrity.build_artifact_manifest_v01(transaction_id=transaction,profile=integrity.build_default_seal_profile_v01(),
        artifacts=tuple(abi.kernel_artifact_to_canonical_ref_v01(a) for a in baseline_artifacts),dependency_edges=replay_edges,
        root_ownership_bindings=tuple(integrity.RootOwnershipBindingV01(a.artifact_id,root) for a in baseline_artifacts),
        evidence_class_bindings=tuple(integrity.EvidenceClassBindingV01(a.artifact_id,'SOURCE_EVIDENCE') for a in baseline_artifacts),
        authority_class_bindings=tuple(integrity.AuthorityClassBindingV01(a.artifact_id,a.authority_class) for a in baseline_artifacts))
    replay = integrity.verify_artifact_replay_v01(manifest=manifest,
        payload_rows=tuple((a.artifact_id,abi.kernel_artifact_to_plain_dict_v01(a)['payload']) for a in baseline_artifacts),
        expected_manifest_hash=manifest.manifest_hash)
    b = pending['information']['report'];source = baseline.source_context
    source_kwargs = dict(integrity_manifest=manifest,integrity_replay=replay,baseline_source_artifacts=baseline_artifacts,
        observed_source_artifacts=observed_artifacts,g2a_registry=payment['pending_registry'],g2a_packet=payment['bound'],
        g2a_dependency_candidate=canonical.dependency_candidate,g2a_current_observations=(payment['observation'],),
        g2a_root_invalidation_material=invalidation,g2b_resolution_report=b,g2b_reuse_certificate=b.reuse_certificate,g2b_writeback_evidence=None,
        g2c_source_context=source.g2c_source_context,baseline_g2c_route_eligibility_artifact=source.route_eligibility_artifact,
        baseline_g2d_execution_bundle=baseline,root_kernel=source.root_kernel,post_vv_profile=None,gt_profile=None)
    if current_capture is not None:
        c.require_v01(current_capture.evaluation_time==evaluation_time,'delta_capture_time')
        actual = tuple(v for v in current_capture.observations if v.dependency_id==prior.dependency_id)
        c.require_v01(len(actual)==1 and actual[0].observed_content_sha256==changed_hash and
            observed_quote.observed_at<=actual[0].observed_at_utc<=evaluation_time,'delta_capture_actual_quote')
        source_kwargs.update(current_source_host=payment['host'],current_source_capture=current_capture,
            g2a_registry=current_capture.registry,g2a_current_observations=current_capture.observations)
    source_check = delta_api.validate_continuous_delta_source_context_v01(delta_api.ContinuousDeltaSourceContextV01(**source_kwargs))
    return dict(source_kwargs=source_kwargs,source_validation=source_check,projections=tuple(projections),
        replay_edges=replay_edges,pending=pending,observed_quote=observed_quote)


def revalidate_renewal_baseline_v01(pending, evaluation_time):
    """Capture current Host evidence without changing the historical B/C/D family."""
    quote = pending['quote_work']
    payment = pending['payment'];host=payment['host'];clock=host.current_sources
    capture = hosts.capture_current_action_source_v01(host,packet_id=payment['bound'].packet_identity.packet_id,
        expected_revision=host.revision,evaluation_time=evaluation_time,
        evaluation_time_source=clock.evaluation_time_source,evaluation_context_id=clock.evaluation_context_id)
    return dict(source=quote['d_source'],common=quote['common'],bundle=quote['d_bundle'],
        validation=fractal.validate_fractal_runtime_execution_bundle_v02(quote['d_bundle']),
        prior_bundle=quote['d_bundle'],capture=capture)


def run_quote_delta_v01(material):
    args = material['source_kwargs']
    context = delta_api.build_continuous_delta_source_context_v01(**args)
    prior,observed = context.baseline_source_artifacts[0],context.observed_source_artifacts[0]
    baseline = context.baseline_g2d_execution_bundle
    b = context.g2b_resolution_report
    common = dict(transaction_id=b.query.query_id,owning_root_id=b.query.owning_local_root_id,domain_id=b.query.domain,
        policy_version=b.query.policy_version,schema_versions=b.query.schema_versions,source_history_hash=b.query_evaluations[0].source_history_hash)
    edge_projection_bindings = tuple((edge.artifact_id,edge.depends_on_artifact_id,
        ('/content_sha256',) if edge.depends_on_artifact_id==prior.artifact_id else (),
        'FIELD_CAUSAL' if edge.depends_on_artifact_id==prior.artifact_id else 'ARTIFACT_DEPENDENCY') for edge in material['replay_edges'])
    basis,edges = delta_api.project_integrity_replay_dependency_edges_v01(manifest=context.integrity_manifest,replay=context.integrity_replay,
        source_artifacts=context.baseline_source_artifacts,graph_version=delta_api.CONTINUOUS_DELTA_GRAPH_VERSION_V01,
        edge_projection_bindings=edge_projection_bindings,**common)
    graph = delta_api.build_dependency_graph_index_v01(graph_basis_sha256=basis,graph_version=delta_api.CONTINUOUS_DELTA_GRAPH_VERSION_V01,
        manifest=context.integrity_manifest,replay=context.integrity_replay,source_artifacts=context.baseline_source_artifacts,
        dependency_edges=edges,trace_refs=(prior.artifact_id,),**common)
    profile = delta_api.build_dependency_fingerprint_profile_v01()
    fingerprints = tuple(delta_api.build_dependency_fingerprint_v01(profile=profile,graph=graph,dependency_edges=edges,
        source_artifacts=artifacts,policy_version=b.query.policy_version,schema_versions=b.query.schema_versions,
        source_history_hash=b.query_evaluations[0].source_history_hash) for artifacts in (context.baseline_source_artifacts,context.observed_source_artifacts))
    def sha(value):
        return hashlib.sha256(c.canonical_v01(value)).hexdigest()
    old_plain = abi.kernel_artifact_to_plain_dict_v01(prior);new_plain = abi.kernel_artifact_to_plain_dict_v01(observed)
    observed_fact_time = material['observed_quote'].observed_at
    timestamp = datetime.fromtimestamp(observed_fact_time,timezone.utc).isoformat()
    until = datetime.fromtimestamp(material['observed_quote'].valid_to,timezone.utc).isoformat()
    binding = delta_api.build_delta_source_binding_v01(request_id=baseline.runtime_report.request_id,
        transaction_id=common['transaction_id'],owning_root_id=common['owning_root_id'],domain_id=common['domain_id'],
        baseline_source_artifact_id=prior.artifact_id,baseline_source_artifact_type=prior.artifact_type,
        baseline_source_artifact_sha256=sha(old_plain),baseline_source_payload_sha256=sha(old_plain['payload']),
        observed_source_artifact_id=observed.artifact_id,observed_source_artifact_type=observed.artifact_type,
        observed_source_artifact_sha256=sha(new_plain),observed_source_payload_sha256=sha(new_plain['payload']),
        baseline_report_id=baseline.runtime_report.report_id,baseline_graph_id=graph.graph_id,baseline_graph_version=graph.graph_version,
        baseline_policy_version=b.query.policy_version,observed_policy_version=b.query.policy_version,
        baseline_schema_versions=b.query.schema_versions,observed_schema_versions=b.query.schema_versions,
        baseline_source_history_hash=common['source_history_hash'],observed_source_history_hash=common['source_history_hash'],
        valid_from_utc=timestamp,valid_to_utc=until,trace_refs=(prior.artifact_id,observed.artifact_id))
    field = delta_api.build_changed_field_binding_v01(source_binding_id=binding.source_binding_id,json_pointer='/payload/content_sha256',
        prior_value_sha256=sha(old_plain['payload']['content_sha256']),observed_value_sha256=sha(new_plain['payload']['content_sha256']),
        change_class='FIELD_VALUE_CHANGE',observed_at_utc=datetime.fromtimestamp(material['observed_quote'].observed_at,timezone.utc).isoformat(),
        trace_refs=(binding.source_binding_id,))
    artifact = delta_api.build_changed_artifact_binding_v01(source_binding_id=binding.source_binding_id,
        baseline_artifact_id=prior.artifact_id,baseline_artifact_type=prior.artifact_type,baseline_payload_sha256=sha(old_plain['payload']),
        observed_artifact_id=observed.artifact_id,observed_artifact_type=observed.artifact_type,observed_payload_sha256=sha(new_plain['payload']),
        baseline_dependency_fingerprint=fingerprints[0],observed_dependency_fingerprint=fingerprints[1],change_class='ARTIFACT_SUCCESSOR',
        observed_at_utc=field.observed_at_utc,trace_refs=(binding.source_binding_id,))
    delta = delta_api.build_world_state_delta_v01(ordered_source_binding_ids=(binding.source_binding_id,),
        request_id=binding.request_id,transaction_id=binding.transaction_id,owning_root_id=binding.owning_root_id,domain_id=binding.domain_id,
        baseline_report_id=baseline.runtime_report.report_id,baseline_graph_id=graph.graph_id,baseline_graph_version=graph.graph_version,
        observed_at_utc=timestamp,valid_from_utc=timestamp,valid_to_utc=until,
        baseline_policy_version=b.query.policy_version,observed_policy_version=b.query.policy_version,
        baseline_schema_versions=b.query.schema_versions,observed_schema_versions=b.query.schema_versions,
        baseline_source_history_hash=common['source_history_hash'],observed_source_history_hash=common['source_history_hash'],
        ordered_changed_field_binding_ids=(field.changed_field_binding_id,),ordered_changed_artifact_binding_ids=(artifact.changed_artifact_binding_id,),
        dependency_fingerprint_before=fingerprints[0],dependency_fingerprint_after=fingerprints[1],trace_refs=(graph.graph_id,))
    arguments = dict(source_context=context,source_bindings=(binding,),changed_field_bindings=(field,),changed_artifact_bindings=(artifact,),
        delta=delta,dependency_edges=edges,dependency_graph=graph,retained_profile='fractal_retained_work_v01')
    bundle,validation = delta_api.run_continuous_delta_runtime_v01(**arguments)
    c.require_v01(validation.status=='PASS' and bundle is not None,'testflix_E_recomputation:'+repr(validation.reason_codes))
    return dict(arguments=arguments,bundle=bundle,validation=validation,material=material)
