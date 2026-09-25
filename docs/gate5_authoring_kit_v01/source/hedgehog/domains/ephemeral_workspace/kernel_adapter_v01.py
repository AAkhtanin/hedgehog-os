"""EWS uses public common builders, never a domain replacement for Root/Host."""
from dataclasses import replace, asdict
from datetime import datetime, timezone
import time
from hedgehog import action_commit_packet_v02 as a
from hedgehog import work_execution_host_v01 as h
from hedgehog import context_packets as packets, structured_rationale as rationale
from hedgehog.kernel import abi_v01 as abi, work_composition_v01 as w
from hedgehog.kernel import root_decision_v01 as roots, semantic_work_v01 as sw
from hedgehog.kernel import trust_model_v01 as trust, transition_registry_v01 as tr
from hedgehog.kernel import execution_mode_router_v01 as router, effect_firewall_v01 as fw
from . import contracts_v01 as c, capability_registry_v01 as caps


class CurrentSource:
    """Explicit local clock sampling at command intake and immediately before use."""
    def __init__(self):
        self.started = time.monotonic()
        self.epoch = int(time.time())
        self.offset = 0
        bridge = a.build_logical_time_bridge_v01(origin_utc_epoch_seconds=self.epoch,
            seconds_per_tick=1, bridge_policy_version='ews.monotonic.v01')
        self.snapshot = h.TrustedWorkSourceSnapshotV01((),bridge,self.epoch,'ews.monotonic_sample','ews:current',0)

    def read_current_v01(self):
        return self.snapshot

    def sample(self, observation=None):
        now = self.epoch + int(time.monotonic()-self.started) + self.offset
        observations = {v.dependency_id:v for v in self.snapshot.observations}
        if observation is not None:
            observations[observation.dependency_id] = observation
        self.snapshot = replace(self.snapshot,evaluation_time=now,observations=tuple(observations[k] for k in sorted(observations)),
            source_revision=self.snapshot.source_revision+1)
        return self.snapshot


def root_review(root, transaction, candidate, subject, checks, evidence_ref, bsep, topology, now,
                *, predicate='workspace_route_candidate', kind='ROUTE', permission=None, policy='ews:hard_policy', time_ref=None,
                claim_value=None):
    c.require(bool(checks) and all(type(v) is bool for v in checks.values()), 'root_checks_actual_boolean')
    req = sw.build_semantic_work_request_v01(request_id='review:'+candidate,transaction_id=transaction,target_root_id=root,
        runtime_topology_ref=topology,bounded_context_refs=(evidence_ref,),permitted_actor_ids=('ews:local_validator',),
        permitted_contribution_modes=('DETERMINISTIC',),requested_subjects=(subject,),required_evidence_classes=('DEPENDENCY_EVIDENCE',),
        forbidden_claims=('authority_creation',))
    ev = sw.build_evidence_binding_v01(evidence_id='binding:'+evidence_ref,evidence_ref=evidence_ref,evidence_class='DEPENDENCY_EVIDENCE',
        source_component_id='ews:local_validator',provenance_ref='ews:local_source',evidence_state='PRESENT')
    claim = sw.build_normalized_claim_v01(claim_id=candidate,subject=subject,predicate=predicate,
        object_or_value=dict(candidate_id=candidate,candidate_kind=kind) if claim_value is None else claim_value,time_envelope_ref='ews:time:'+str(now),
        provenance_refs=(evidence_ref,),evidence_refs=(ev.evidence_id,),confidence_micros=1000000,
        source_role='deterministic_runtime',source_mode='DETERMINISTIC')
    contribution = sw.build_actor_contribution_v01(contribution_id='contribution:'+candidate,request_id=req.request_id,
        actor_id='ews:local_validator',actor_role='deterministic_runtime',contribution_mode='DETERMINISTIC',bsep_projection_ref=bsep,
        scope=subject,bounded_context_refs=(evidence_ref,),claims=(claim,),evidence_bindings=(ev,),constraint_bindings=(),
        uncertainty_bindings=(),requested_validators=tuple(sorted(checks)),forbidden_claims_observed=())
    packet = sw.build_root_review_packet_from_contributions_v01(request=req,contributions=(contribution,),
        trust_profiles=trust.build_default_component_trust_profiles_v01())
    valid = all(checks.values())
    kernel = roots.build_root_decision_kernel_v01()
    inputs = roots.build_root_decision_input_v01(transaction_id=transaction,target_root_id=root,root_review_packet=packet,
        post_vv_bundle=dict(bundle_id=c.identity('checks',checks),post_vv_passed=valid,validated_candidate_ids=[candidate] if valid else [],
            rejected_candidate_ids=[] if valid else [candidate],required_evidence_refs=[evidence_ref],provided_evidence_refs=[evidence_ref],
            hard_failure_reasons=[k for k,v in checks.items() if not v]),
        gt_advisory=dict(advisory_id='gt:'+candidate,candidate_ids=[candidate],selected_candidate_id=candidate if valid else None,
            score_micros_by_candidate={candidate:1000000 if valid else 0},source_artifact_type='GTAdvisoryReport',source_lifecycle_state='VALIDATED',
            actor_role='gt',attempted_effect='CREATE_ROOT_DECISION',target_artifact_type='RootDecision',advisory_only=True,
            creates_final_output=False,requests_effect=False),
        policy_state=dict(policy_id=policy,identity_passed=valid,scope_passed=valid,hard_policy_passed=valid,allow_accept=valid,
            conflict_policy='DEFER',no_candidate_policy='NO_UPDATE'),
        permission_state=dict(permission_required=permission is not None,user_permission_present=permission is not None and valid,
            permission_scope_valid=valid,permission_ref=permission),
        temporal_state=dict(temporal_valid=True,expired=False,not_before_satisfied=True,time_envelope_ref=time_ref or 'ews:time:'+str(now)),
        conflict_state=dict(material_unresolved_conflict=bool(packet.conflict_set_ids),conflict_set_ids=list(packet.conflict_set_ids)),
        prior_root_state=dict(prior_decision_id=None,prior_decision=None,prior_selected_candidate_id=None))
    result = roots.decide_root_v01(kernel=kernel,decision_input=inputs)
    c.require(not roots.validate_root_decision_result_v01(kernel=kernel,decision_input=inputs,result=result), 'root_result_invalid')
    c.require(result.decision == 'ACCEPT', 'root_refusal:'+result.reason_code)
    return kernel, inputs, result


def semantic_source(request, request_id, root, now, orchestrator):
    ref = c.identity('orchestrator', dict(request=request,output=orchestrator))
    transaction = 'transaction:'+request_id
    decision = root_review(root,transaction,ref,request_id,dict(photo_scope='browse' in orchestrator['needs'],
        no_unresolved_questions=not orchestrator['uncertainty']),ref,'ews:intake:bounded','ews:route:proposal',now)
    business = packets.build_business_request_context_packet(packet_id='business:'+request_id,created_by='ews:local_intake',domain='EPHEMERAL_WORKSPACE',
        request_id=request_id,business_subject='temporary_photo_workspace',requested_action='bounded_workspace',user_visible_summary=request)
    source_ref = dict(source='G2C_BUSINESS_REQUEST_CONTEXT_PACKET_V01',packet_id=business['packet_id'],request_id=request_id,domain_id='EPHEMERAL_WORKSPACE')
    route_id = 'route:ews:photo'
    vectors, guards = ('vector:'+ref,), ('guard:ews:current_root',)
    route = packets.build_orchestrator_route_context_packet(packet_id='route_context:'+ref,created_by='ews:local_canonicalization',source_refs=(source_ref,),
        domain='EPHEMERAL_WORKSPACE',allowed_routes=(route_id,),required_guards=guards,selected_vector_ids=vectors,
        route_validation_expectations=dict(root_review_required=True,selected_only_allowed_vectors=True),orchestrator_is_root=False,
        creates_action_commit_packet=False,calls_connectors=False)
    proposal = dict(proposal_id='proposal:'+ref,suggested_route=route_id,selected_vector_ids=vectors,required_guards=guards,
        reason='Temporary photo work with separate save confirmation.',confidence=0.75,needs_review=True,
        uncertainty_notes=('Semantic proposal is not action permission.',),root_review_required=True,
        truth_claimed=False,authority_claimed=False,action_permission_claimed=False,final_output_claimed=False,
        connector_command_claimed=False,drs_write_claimed=False,plan_graph_claimed=False,bypass_root_claimed=False,
        semantic_observations=(c.canonical(orchestrator).decode(),),route_reasoning=('Bounded local photo work.',),
        rejected_route_reasoning=('No source edits or publication.',),guard_reasoning=('Current Root required per command.',),
        vector_reasoning=('Actual requested photo operations.',),authority_boundary_reasoning=('PersonalRoot alone accepts.',))
    structured = rationale.build_orchestrator_structured_rationale(observed_semantics=proposal['semantic_observations'],
        route_selection_reason=proposal['route_reasoning'],rejected_routes=proposal['rejected_route_reasoning'],
        required_guards_reasoning=proposal['guard_reasoning'],selected_vector_reasoning=proposal['vector_reasoning'],
        uncertainty_notes=proposal['uncertainty_notes'],authority_boundary=proposal['authority_boundary_reasoning'],root_review_required=True)
    def ev(text, kind):
        return packets.semantic_evidence_item(text,source='runtime_canonicalization',evidence_kind=kind,confidence_label='medium')
    bsep = packets.build_bounded_semantic_evidence_packet(packet_id='bsep:'+ref,source_refs=(source_ref,),domain='EPHEMERAL_WORKSPACE',
        source_role='orchestrator',target_role='architect',source_route_id=route_id,source_proposal_id=proposal['proposal_id'],
        source_context_packet_id=route['packet_id'],source_structured_rationale_ref='structured_rationale_v01:'+c.digest(structured),
        observed_semantic_facts=(ev(c.canonical(orchestrator).decode(),'observed_fact'),),
        missing_evidence=(ev('Device activation and save require their own current review.','missing_evidence'),),
        uncertainty_notes=(ev('Proposal only.','uncertainty'),),risk_boundary_notes=(ev('Local effects require finite packets.','risk_boundary'),),
        rejected_action_routes=(ev('No publication.','rejected_route'),),required_approvals_or_conditions=(ev(decision[2].decision_id,'approval_condition'),),
        authority_boundary_notes=(ev('No authority transfer.','authority_boundary'),),selected_vector_ids=vectors,required_guards=guards)
    source = router.build_execution_mode_source_context_v01(business_request_context_packet=business,bsep_packet=bsep,bsep_route_context_packet=route,
        bsep_orchestrator_proposal=proposal,bsep_structured_rationale=structured,sealed_replay_evidence=None,replay_source_manifest=None,
        replay_source_domain_projection=None,replay_source_safe_file_contents=(),replay_anchor_publication=None,replay_anchored_verification=None,
        replay_supplied_anchor_publication_id=None,replay_reconstructed_manifest=None,replay_reconstructed_domain_projection=None,
        replay_reconstructed_safe_file_contents=(),g2a_inspection=None,g2a_registry=None,g2a_packet_id=None,g2a_corridor=None,g2a_corridor_step=None,
        g2a_current_dependency_observations=(),g2a_logical_time_bridge=None,g2a_evaluation_time=now,g2a_evaluation_time_source='ews.monotonic_sample',
        g2a_evaluation_context_id='ews:current',g2a_transition_registry_profile=None,g2b_resolution_report=None,g2b_compatibility_projections=(),
        g2b_use_time=None,g2b_root_kernel=None,g2b_root_decision_input=None,g2b_root_decision_result=None,g2b_writeback_evidence=None)
    return source, decision


def materialize(session, responses, source):
    now = session.source.sample().evaluation_time
    stamp = lambda t: datetime.fromtimestamp(t,timezone.utc).isoformat()
    proposal = abi.build_kernel_artifact_v01(abi_version='v1.0',artifact_id=c.identity('semantics',responses),artifact_type='SemanticArchitectProposal',
        schema_version='v1',transaction_id='transaction:'+session.id,owner_root_id=session.root,source_component='semantic_architect',
        authority_class='ADVISORY',lifecycle_state='PROPOSED',payload=dict(roles=responses),trace_refs=('intent:'+session.id,),
        parent_refs=(source.bsep_packet['packet_id'],),time_envelope=dict(pt_created_at=stamp(now),kt_asof=stamp(now),et_observed_at=None,
            ct_session_anchor=session.id,ttl_seconds=1200,freshness_class='static',valid_from=stamp(now),valid_to=stamp(now+1200)))
    first, second = session.catalogue[:2]
    items = (w.WorkItemV01('compile_contract',first.definition.definition_id,session.root,
        (w.WorkInputBindingV01('material',w.WorkLiteralV01(caps.records(dict(material=('TEXT',c.canonical(responses).decode())))[0])),),(),(),None,None),
        w.WorkItemV01('consume_contract',second.definition.definition_id,session.root,
        (w.WorkInputBindingV01('material',w.WorkOutputBindingV01('compile_contract','material','TEXT')),),(),('compile_contract',),None,None))
    common = dict(catalogue=session.catalogue,source_context=source,semantic_proposal=proposal)
    candidate = w.build_work_program_candidate_v01(task_id=session.id,previous_revision_id=None,intent_ref='intent:'+session.id,
        bsep_ref=source.bsep_packet['packet_id'],semantic_proposal_ref=proposal.artifact_id,catalogue_revision=0,
        budget=w.WorkBudgetV01(2,0,0,2,0),items=items,trigger_evidence_refs=(),**common)
    program = w.materialize_work_program_v01(candidate,**common)
    results = w.advance_work_program_v01(program,host_map={session.root:session.host},**common)
    c.require(all(r.status=='COMPLETED' for r in results) and len(results[1].consumed_fields)==1, 'actual_work_consumption')
    artifact = w.work_program_result_to_artifact_v01(program,results,host_map={session.root:session.host},**common)
    return program, results, artifact


def prepare_command(session, values, checks):
    admitted = session.catalogue[2]
    inputs = caps.records(dict(command=('TEXT',c.canonical(values).decode()),session=('REFERENCE',session.id),version=('INTEGER',session.version)))
    clock = session.source.sample()
    now, root = clock.evaluation_time, session.root
    object_ref = c.identity('command', dict(session=session.id,version=session.version,command=values))
    dep = 'dependency:'+object_ref
    fact = dict(inputs=caps.values(inputs),source_sha256=session.source_hashes,contract=session.contract,expires=session.expires,
        resources=session.resource_plan,cleanup='owned_birth_nonce_and_preview_identity',output_slot='selection.json')
    if 'media' in session.contract:
        fact['media']=session.media_dependency()
    session.last_prepared_fact=fact
    sha = c.digest(fact)
    ref = 'evidence:'+sha
    expires = min(now+120, session.expires)
    c.require(now < expires, 'workspace_expired')
    env = a.build_action_dependency_time_envelope_id_v01(dependency_id=dep,evidence_ref=ref,content_sha256=sha,
        freshness_policy_id='ews:current',source_provenance_refs=('ews:local_source',),valid_from_utc=now,valid_to_utc=expires)
    dependency = a.build_dependency_set_candidate_v01(dependency_records=(a.build_dependency_set_candidate_record_v01(
        dependency_id=dep,dependency_class='DOMAIN_AUTHORIZATION_INPUT',evidence_ref=ref,content_sha256=sha,requirement_class='MANDATORY',
        time_envelope_id=env,freshness_policy_id='ews:current',source_provenance_refs=('ews:local_source',),expected_accepting_local_root_id=root),))
    permission = 'permission:'+object_ref
    policy = a.build_action_authority_policy_profile_v01(policy_version='ews.finite.v01',owning_local_root_id=root,
        authority_rule_refs=('ews:local_root_only',),kill_switch_condition_refs=('ews:owner_revoke',),retry_policy='NON_CONSUMING_RETRY',
        supersession_policy='ROOT_DECISION_ONLY',logical_effect_namespace='ews.command.v01',allowed_logical_effect_classes=('LOCAL_WORKSPACE_COMMAND',),
        allowed_business_object_namespaces=('ews.command',),allowed_corridor_classes=('ews.local.mock',))
    canonical = a.build_native_action_commit_packet_v01(transaction_id=getattr(session,'media_transaction','transaction:'+session.id),owning_local_root_id=root,
        canonical_permission_ref=permission,selected_canonical_action='mock_action:ews_finite_command',
        normalized_subject_scope=a.build_action_subject_scope_profile_v01(included_subject_refs=('ews:owner',),excluded_subject_refs=()),
        normalized_target_scope=a.build_action_target_scope_profile_v01(included_target_refs=(session.id,),excluded_target_refs=()),
        normalized_permission_scope=a.build_action_permission_scope_profile_v01(allowed_action_classes=('mock_action:ews_finite_command',),
            forbidden_action_classes=(),allowed_adapter_ids=('mock_adapter:ews_local',),forbidden_adapter_ids=(),required_approval_refs=(permission,),prohibited_effect_classes=()),
        adapter_binding=a.build_action_adapter_binding_profile_v01(corridor_class='ews.local.mock',adapter_id='mock_adapter:ews_local',
            adapter_kind='DETERMINISTIC_MOCK',adapter_version='v01'),dependency_candidate=dependency,
        temporal_authority=a.build_action_temporal_authority_profile_v01(issued_at_utc=now,expires_at_utc=expires,ttl_seconds=expires-now,temporal_policy_version='ews.finite.v01'),
        authority_policy=policy,business_object_identity=a.build_action_business_object_identity_profile_v01(business_object_class='DOMAIN_OBJECT',
            business_object_namespace='ews.command',business_object_ref=object_ref,owning_effect_root_id=root),
        consequential_effect_parameters=a.build_action_consequential_effect_parameters_profile_v01(amount_decimal=None,currency_code=None,quantity_decimal=None,parameter_records=inputs),
        evaluation_time=now,evaluation_time_source=clock.evaluation_time_source,evaluation_context_id=clock.evaluation_context_id,admitted_capability=admitted,inputs=inputs)
    candidate = canonical.authorization_candidate.root_packet_authorization_candidate_id
    review = root_review(root,canonical.transaction_id,candidate,object_ref,checks,ref,session.program.candidate.bsep_ref,
        session.program.topology_artifact.artifact_id,now,predicate='root_packet_authorization_candidate',kind='PACKET_AUTHORIZATION',
        permission=permission,policy=canonical.authority_policy_fingerprint,time_ref=canonical.temporal_authority_fingerprint)
    projection = a.build_root_decision_candidate_projection_v01(candidate_kind='PACKET_AUTHORIZATION',projected_candidate_id=candidate,
        root_decision_kernel=review[0],root_decision_input=review[1],root_decision_result=review[2])
    bound = a.build_native_root_bound_action_commit_packet_v01(canonical_projection=canonical,root_decision_projection=projection)
    profile = tr.build_action_packet_transition_registry_profile_v01()
    registry = a.record_action_packet_genesis_v01(a.build_empty_action_commit_packet_registry_v02(),root_bound_genesis=bound,action_packet_transition_registry_profile=profile)
    packet_id = bound.packet_identity.packet_id
    events = []
    for rule_id in ('g2a_t01_activate_root_authorization','g2a_t02_queue','g2a_t03_pending'):
        rule = tr.lookup_action_packet_transition_rule_v01(registry=profile,transition_rule_id=rule_id)
        bindings = tuple(a.build_transition_evidence_binding_v01(action_packet_transition_registry_profile=profile,transition_rule_id=rule_id,
            evidence_code=code,evidence_ref='evidence:ews:'+code,evidence_sha256=c.digest(dict(packet=packet_id,root=review[2].decision_id,code=code)),
            validator_profile_id='ews:public_lifecycle') for code in rule.required_evidence_codes)
        attempt = a.build_action_execution_attempt_identity_v01(packet_id=packet_id,idempotency_key=canonical.idempotency_identity.idempotency_key,
            attempt_ordinal=1,evaluation_context_id=clock.evaluation_context_id) if rule_id.endswith('pending') else None
        event = a.build_action_packet_transition_event_v01(action_packet_transition_registry_profile=profile,transition_rule_id=rule_id,
            packet_id=packet_id,idempotency_key=canonical.idempotency_identity.idempotency_key,
            previous_transition_event_id=events[-1].transition_event_id if events else None,owning_local_root_id=root,
            root_decision_ref=review[2].decision_id if not events else None,transition_evidence_bindings=bindings,
            dependency_set_candidate_fingerprint=canonical.dependency_set_candidate_fingerprint,temporal_authority_fingerprint=canonical.temporal_authority_fingerprint,
            evaluation_time=now,evaluation_time_source=clock.evaluation_time_source,evaluation_context_id=clock.evaluation_context_id,
            execution_attempt_identity=attempt,receipt_ref=None)
        if not events:
            reserve = a.build_idempotency_disposition_event_v01(idempotency_key=canonical.idempotency_identity.idempotency_key,
                event_class='RESERVE',from_disposition='UNCLAIMED',to_disposition='RESERVED',from_owner_packet_id=None,to_owner_packet_id=packet_id,
                previous_disposition_event_id=None,cause_transition_event_ids=(event.transition_event_id,),root_decision_ref=review[2].decision_id,
                predecessor_packet_id=None,successor_packet_id=None,evidence_refs=tuple(sorted(b.transition_evidence_binding_id for b in bindings
                    if b.evidence_code in ('packet_genesis_valid','source_root_authorization_valid','idempotency_acquisition_valid'))),
                evaluation_time=now,evaluation_time_source=clock.evaluation_time_source,evaluation_context_id=clock.evaluation_context_id)
            registry = a.activate_action_packet_lifecycle_v01(registry,packet_id=packet_id,transition_event=event,disposition_event=reserve,action_packet_transition_registry_profile=profile)
        else:
            registry = a.append_action_packet_lifecycle_transition_v01(registry,packet_id=packet_id,transition_event=event,action_packet_transition_registry_profile=profile)
        events.append(event)
    step = a.build_common_corridor_step_v01(transaction_id=canonical.transaction_id,owning_local_root_id=root,packet_id=packet_id,
        authorization_candidate_id=candidate,action_class=canonical.selected_canonical_action,adapter_binding=canonical.adapter_binding,
        subject_scope=canonical.normalized_subject_scope,target_scope=canonical.normalized_target_scope,effect_parameters=canonical.normalized_effect_parameters,
        issued_at_utc=now,expires_at_utc=expires)
    corridor = a.build_common_contract_fulfillment_corridor_v01(transaction_id=canonical.transaction_id,owning_local_root_id=root,
        packet_id=packet_id,corridor_class=canonical.adapter_binding.corridor_class,steps=(step,))
    observation = a.build_action_dependency_current_observation_v01(dependency_id=dep,evidence_ref=ref,observed_content_sha256=sha,
        time_envelope_id=env,freshness_policy_id='ews:current',source_provenance_refs=('ews:local_source',),valid_from_utc=now,valid_to_utc=expires,
        observed_at_utc=now,observation_context_id=clock.evaluation_context_id)
    return dict(root_bound=bound,corridor=corridor,corridor_step=step,transition_events=tuple(events),disposition_event=reserve), inputs, observation, review


def dispatch(session, value, checks):
    session.journal('ROOT_PREPARATION_START',op=value['op'])
    authorization, inputs, observation, review = prepare_command(session,value,checks)
    session.command_authority=dict(inputs_sha256=c.digest(caps.values(inputs)),
        expires=authorization['root_bound'].canonical_projection.temporal_authority.expires_at_utc)
    session.journal('ROOT_PREPARATION_RETURN',decision_id=review[2].decision_id)
    clock = session.source.sample(observation)
    args = dict(evaluation_time=clock.evaluation_time,evaluation_time_source=clock.evaluation_time_source,evaluation_context_id=clock.evaluation_context_id)
    packet_id, revision = h.install_current_action_v01(session.host,**authorization,inputs=inputs,
        admission_id=session.catalogue[2].admission_id,expected_revision=session.host.revision,**args)
    session.journal('HOST_INSTALLED',packet_id=packet_id)
    clock = session.source.sample()
    args.update(evaluation_time=clock.evaluation_time)
    registry, revision = h.dispatch_current_action_v01(session.host,packet_id=packet_id,task_id=session.id,expected_revision=revision,**args)
    session.journal('HOST_DISPATCH_RETURN',packet_id=packet_id)
    context = registry.action_packet_fulfillment_attempt_contexts[-1]
    c.require(context.receipt is not None, 'native_receipt_missing')
    receipt = abi.kernel_artifact_to_plain_dict_v01(context.receipt)
    execution = fw.native_execution_evidence_from_plain_data_v01(receipt['payload']['execution_evidence'])
    session.host.observe_receipt(packet_id=packet_id,attempt_evidence_id=context.attempt_evidence.attempt_evidence_id,
        expected_revision=revision,evaluation_time=clock.evaluation_time,evaluation_time_source=clock.evaluation_time_source)
    return dict(packet_id=packet_id,root_decision=roots.root_decision_result_to_plain_dict_v01(review[2]),
                receipt=receipt,output=caps.values(execution.result.output))
