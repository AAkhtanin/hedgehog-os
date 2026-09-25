"""Application records use the existing native Root/host/lifecycle boundary."""
from dataclasses import asdict
from hedgehog import action_commit_packet_v02 as action
from hedgehog import work_execution_host_v01 as hosts
from hedgehog.kernel import effect_firewall_v01 as firewall
from hedgehog.kernel import abi_v01 as abi
from hedgehog.kernel import root_decision_v01 as roots
from hedgehog.kernel import semantic_work_v01 as semantic_work
from hedgehog.kernel import trust_model_v01 as trust
from hedgehog.kernel import transition_registry_v01 as transitions
from hedgehog.domains.testflix import contracts_v01 as c
from hedgehog.domains.testflix import mock_world_v01 as world


def new_host_v01(root, catalogue, now):
    source = world.LocalSourceV01(now)
    host = hosts.build_root_work_execution_host_v01(owning_root_id=root,
        registry=action.build_empty_action_commit_packet_registry_v02(),catalogue=tuple(catalogue),packet_bindings=(),
        current_dependency_observations=(),logical_time_bridge=source.snapshot.logical_time_bridge,trusted_source=source)
    return host,source


def canonical_action_v01(request, root, admitted, inputs, object_ref, target_ref, evidence, *, valid_to=None, transaction_id=None):
    definition = admitted.definition
    semantics = definition.business_semantics
    dependency_id = 'dependency:' + object_ref
    digest = action.domain_separated_sha256_hex_v01(domain='testflix.authoritative_dependency.v01',
        payload=c.canonical_v01(evidence))
    evidence_ref = 'evidence:' + digest
    expires = request.now+120 if valid_to is None else min(request.now+120,valid_to)
    c.require_v01(type(expires) is int and request.now+4<expires, 'action_current_validity')
    temporal = action.build_action_temporal_authority_profile_v01(issued_at_utc=request.now,
        expires_at_utc=expires,ttl_seconds=expires-request.now,temporal_policy_version='testflix.action_ttl.v01')
    envelope = action.build_action_dependency_time_envelope_id_v01(dependency_id=dependency_id,evidence_ref=evidence_ref,
        content_sha256=digest,freshness_policy_id='freshness:testflix:current',source_provenance_refs=('source:testflix:authoritative',),
        valid_from_utc=request.now,valid_to_utc=expires)
    dependency = action.build_dependency_set_candidate_v01(dependency_records=(action.build_dependency_set_candidate_record_v01(
        dependency_id=dependency_id,dependency_class='DOMAIN_AUTHORIZATION_INPUT',evidence_ref=evidence_ref,content_sha256=digest,
        requirement_class='MANDATORY',time_envelope_id=envelope,freshness_policy_id='freshness:testflix:current',
        source_provenance_refs=('source:testflix:authoritative',),expected_accepting_local_root_id=root),))
    policy = action.build_action_authority_policy_profile_v01(policy_version='testflix.bounded.v01',owning_local_root_id=root,
        authority_rule_refs=('authority:testflix:local_root_only',),kill_switch_condition_refs=('kill_switch:testflix:root_revocation',),
        retry_policy='NON_CONSUMING_RETRY',supersession_policy='ROOT_DECISION_ONLY',logical_effect_namespace=semantics.logical_effect_namespace,
        allowed_logical_effect_classes=(semantics.logical_effect_class,),allowed_business_object_namespaces=(semantics.business_object_namespace,),
        allowed_corridor_classes=('testflix.mock',))
    actual = {v.parameter_name:v for v in inputs}
    records = tuple(actual[b.input_name] for b in semantics.input_bindings if b.source_kind in ('RECORD','SUBJECT_RECORD','TARGET_RECORD'))
    amount = next((actual[b.input_name].value for b in semantics.input_bindings if b.source_kind=='AMOUNT'),None)
    currency = next((actual[b.input_name].value for b in semantics.input_bindings if b.source_kind=='CURRENCY'),None)
    permission = 'permission:' + root + ':' + object_ref
    canonical = action.build_native_action_commit_packet_v01(transaction_id='transaction:'+request.request_id+':'+root if transaction_id is None else transaction_id,
        owning_local_root_id=root,canonical_permission_ref=permission,selected_canonical_action=semantics.selected_action_class,
        normalized_subject_scope=action.build_action_subject_scope_profile_v01(included_subject_refs=(request.user_id,),excluded_subject_refs=()),
        normalized_target_scope=action.build_action_target_scope_profile_v01(included_target_refs=(target_ref,),excluded_target_refs=()),
        normalized_permission_scope=action.build_action_permission_scope_profile_v01(allowed_action_classes=(semantics.selected_action_class,),
            forbidden_action_classes=(),allowed_adapter_ids=('mock_adapter:testflix',),forbidden_adapter_ids=(),
            required_approval_refs=(permission,),prohibited_effect_classes=()),
        adapter_binding=action.build_action_adapter_binding_profile_v01(corridor_class='testflix.mock',adapter_id='mock_adapter:testflix',
            adapter_kind='DETERMINISTIC_MOCK',adapter_version='v01'),dependency_candidate=dependency,temporal_authority=temporal,
        authority_policy=policy,business_object_identity=action.build_action_business_object_identity_profile_v01(
            business_object_class=semantics.business_object_class,business_object_namespace=semantics.business_object_namespace,
            business_object_ref=object_ref,owning_effect_root_id=root),
        consequential_effect_parameters=action.build_action_consequential_effect_parameters_profile_v01(amount_decimal=amount,
            currency_code=currency,quantity_decimal=None,parameter_records=records),evaluation_time=request.now,
        evaluation_time_source='testflix.controlled_utc',evaluation_context_id='context:testflix:canonical',admitted_capability=admitted,inputs=inputs)
    observation = action.build_action_dependency_current_observation_v01(dependency_id=dependency_id,evidence_ref=evidence_ref,
        observed_content_sha256=digest,time_envelope_id=envelope,freshness_policy_id='freshness:testflix:current',
        source_provenance_refs=('source:testflix:authoritative',),valid_from_utc=request.now,valid_to_utc=expires,
        observed_at_utc=request.now+4,observation_context_id='context:testflix:dispatch')
    return canonical,observation


def review_candidate_v01(canonical, *, bsep_ref, topology_ref, checks, candidate_kind='PACKET_AUTHORIZATION', candidate_id=None, predecessor=None):
    """Local policy checks are evaluated upstream on actual typed domain inputs."""
    c.require_v01(type(checks) is dict and bool(checks) and all(type(v) is bool for v in checks.values()),'root_check_shape')
    candidate_id = candidate_id or canonical.authorization_candidate.root_packet_authorization_candidate_id
    subject = canonical.business_object_identity.business_object_ref
    local = canonical.owning_local_root_id
    context_ref = 'context:' + canonical.dependency_set_candidate_fingerprint
    request = semantic_work.build_semantic_work_request_v01(request_id='review:'+candidate_id,transaction_id=canonical.transaction_id,
        target_root_id=local,runtime_topology_ref=topology_ref,bounded_context_refs=(context_ref,),permitted_actor_ids=('testflix:bounded_validator',),
        permitted_contribution_modes=('DETERMINISTIC',),requested_subjects=(subject,),required_evidence_classes=('DEPENDENCY_EVIDENCE',),
        forbidden_claims=('authority_creation',))
    dependency = canonical.dependency_candidate.dependency_records[0]
    evidence = semantic_work.build_evidence_binding_v01(evidence_id='binding:'+dependency.evidence_ref,evidence_ref=dependency.evidence_ref,
        evidence_class='DEPENDENCY_EVIDENCE',source_component_id='testflix:bounded_validator',provenance_ref=dependency.source_provenance_refs[0],
        evidence_state='PRESENT')
    claim = semantic_work.build_normalized_claim_v01(claim_id=candidate_id,subject=subject,
        predicate='root_packet_authorization_candidate' if candidate_kind=='PACKET_AUTHORIZATION' else action.ROOT_DECISION_CLAIM_PREDICATE_REVOCATION_V01,
        object_or_value=dict(candidate_id=candidate_id,candidate_kind=candidate_kind),time_envelope_ref=canonical.temporal_authority_fingerprint,
        provenance_refs=(context_ref,),evidence_refs=(evidence.evidence_id,),confidence_micros=1000000,
        source_role='deterministic_runtime',source_mode='DETERMINISTIC')
    contribution = semantic_work.build_actor_contribution_v01(contribution_id='contribution:'+candidate_id,request_id=request.request_id,
        actor_id='testflix:bounded_validator',actor_role='deterministic_runtime',contribution_mode='DETERMINISTIC',bsep_projection_ref=bsep_ref,
        scope=subject,bounded_context_refs=(context_ref,),claims=(claim,),evidence_bindings=(evidence,),constraint_bindings=(),
        uncertainty_bindings=(),requested_validators=tuple(sorted(checks)),forbidden_claims_observed=())
    review = semantic_work.build_root_review_packet_from_contributions_v01(request=request,contributions=(contribution,),
        trust_profiles=trust.build_default_component_trust_profiles_v01())
    valid = all(checks.values()) and action.validate_native_action_commit_packet_v01(canonical)[0]
    failures = [k for k,v in checks.items() if not v]
    required = [d.evidence_ref for d in canonical.dependency_candidate.dependency_records if d.requirement_class=='MANDATORY']
    kernel = roots.build_root_decision_kernel_v01()
    decision_input = roots.build_root_decision_input_v01(transaction_id=canonical.transaction_id,target_root_id=local,root_review_packet=review,
        post_vv_bundle=dict(bundle_id='post_vv:'+c.identity_v01('checks',checks),post_vv_passed=valid,
            validated_candidate_ids=[candidate_id] if valid else [],rejected_candidate_ids=[] if valid else [candidate_id],
            required_evidence_refs=required,provided_evidence_refs=required,hard_failure_reasons=failures),
        gt_advisory=dict(advisory_id='gt:'+candidate_id,candidate_ids=[candidate_id],selected_candidate_id=candidate_id if valid else None,
            score_micros_by_candidate={candidate_id:1000000 if valid else 0},source_artifact_type='GTAdvisoryReport',source_lifecycle_state='VALIDATED',
            actor_role='gt',attempted_effect='CREATE_ROOT_DECISION',target_artifact_type='RootDecision',advisory_only=True,
            creates_final_output=False,requests_effect=False),
        policy_state=dict(policy_id=canonical.authority_policy_fingerprint,identity_passed=valid,scope_passed=valid,
            hard_policy_passed=valid,allow_accept=valid,conflict_policy='DEFER',no_candidate_policy='NO_UPDATE'),
        permission_state=dict(permission_required=candidate_kind=='PACKET_AUTHORIZATION',user_permission_present=valid and candidate_kind=='PACKET_AUTHORIZATION',
            permission_scope_valid=valid,permission_ref=canonical.canonical_permission_ref if candidate_kind=='PACKET_AUTHORIZATION' else None),
        temporal_state=dict(temporal_valid=canonical.temporal_evaluation.executable,expired=canonical.evaluation_time>=canonical.temporal_authority.expires_at_utc,
            not_before_satisfied=canonical.evaluation_time>=canonical.temporal_authority.issued_at_utc,time_envelope_ref=canonical.temporal_authority_fingerprint),
        conflict_state=dict(material_unresolved_conflict=bool(review.conflict_set_ids),conflict_set_ids=list(review.conflict_set_ids)),
        prior_root_state=dict(prior_decision_id=None if predecessor is None else predecessor.root_decision_projection.root_decision_result.decision_id,
            prior_decision=None if predecessor is None else predecessor.root_decision_projection.root_decision_result.decision,
            prior_selected_candidate_id=None if predecessor is None else predecessor.canonical_projection.authorization_candidate.root_packet_authorization_candidate_id))
    result = roots.decide_root_v01(kernel=kernel,decision_input=decision_input)
    errors = roots.validate_root_decision_result_v01(kernel=kernel,decision_input=decision_input,result=result)
    c.require_v01(not errors,'local_root_result:'+repr(errors))
    c.require_v01(result.decision == 'ACCEPT','local_root_refusal:'+result.reason_code)
    projection = action.build_root_decision_candidate_projection_v01(candidate_kind=candidate_kind,projected_candidate_id=candidate_id,
        root_decision_kernel=kernel,root_decision_input=decision_input,root_decision_result=result)
    return projection,dict(request=request,contribution=contribution,review=review)


def pending_material_v01(bound):
    canonical = bound.canonical_projection
    result = bound.root_decision_projection.root_decision_result
    profile = transitions.build_action_packet_transition_registry_profile_v01()
    registry = action.record_action_packet_genesis_v01(action.build_empty_action_commit_packet_registry_v02(),
        root_bound_genesis=bound,action_packet_transition_registry_profile=profile)
    packet_id = bound.packet_identity.packet_id
    for rule_id in ('g2a_t01_activate_root_authorization','g2a_t02_queue','g2a_t03_pending'):
        entry = next(e for e in registry.action_packet_lifecycle_entries if e.root_bound_genesis.packet_identity.packet_id==packet_id)
        rule = transitions.lookup_action_packet_transition_rule_v01(registry=profile,transition_rule_id=rule_id)
        context = 'context:testflix:'+rule_id
        attempt = action.build_action_execution_attempt_identity_v01(packet_id=packet_id,
            idempotency_key=canonical.idempotency_identity.idempotency_key,attempt_ordinal=1,evaluation_context_id=context) if rule_id=='g2a_t03_pending' else None
        bindings = tuple(action.build_transition_evidence_binding_v01(action_packet_transition_registry_profile=profile,
            transition_rule_id=rule_id,evidence_code=code,evidence_ref='evidence:testflix:'+code,
            evidence_sha256=action.domain_separated_sha256_hex_v01(domain='testflix.transition_evidence.v01',
                payload=action.canonical_material_bytes_v01((('packet_id',packet_id),('root_decision_id',result.decision_id),('evidence_code',code)))),
            validator_profile_id='validator:testflix:public_lifecycle') for code in rule.required_evidence_codes)
        event = action.build_action_packet_transition_event_v01(action_packet_transition_registry_profile=profile,transition_rule_id=rule_id,
            packet_id=packet_id,idempotency_key=canonical.idempotency_identity.idempotency_key,
            previous_transition_event_id=entry.transition_events[-1].transition_event_id if entry.transition_events else None,
            owning_local_root_id=canonical.owning_local_root_id,root_decision_ref=result.decision_id if rule_id=='g2a_t01_activate_root_authorization' else None,
            transition_evidence_bindings=bindings,dependency_set_candidate_fingerprint=canonical.dependency_set_candidate_fingerprint,
            temporal_authority_fingerprint=canonical.temporal_authority_fingerprint,evaluation_time=canonical.evaluation_time+1+len(entry.transition_events),
            evaluation_time_source='testflix.controlled_utc',evaluation_context_id=context,execution_attempt_identity=attempt,receipt_ref=None)
        if rule_id=='g2a_t01_activate_root_authorization':
            reserve = action.build_idempotency_disposition_event_v01(idempotency_key=canonical.idempotency_identity.idempotency_key,
                event_class='RESERVE',from_disposition='UNCLAIMED',to_disposition='RESERVED',from_owner_packet_id=None,to_owner_packet_id=packet_id,
                previous_disposition_event_id=None,cause_transition_event_ids=(event.transition_event_id,),root_decision_ref=result.decision_id,
                predecessor_packet_id=None,successor_packet_id=None,evidence_refs=tuple(sorted(b.transition_evidence_binding_id for b in bindings
                    if b.evidence_code in ('packet_genesis_valid','source_root_authorization_valid','idempotency_acquisition_valid'))),
                evaluation_time=event.evaluation_time,evaluation_time_source=event.evaluation_time_source,evaluation_context_id=context)
            registry = action.activate_action_packet_lifecycle_v01(registry,packet_id=packet_id,transition_event=event,
                disposition_event=reserve,action_packet_transition_registry_profile=profile)
        else:
            registry = action.append_action_packet_lifecycle_transition_v01(registry,packet_id=packet_id,transition_event=event,
                action_packet_transition_registry_profile=profile)
    temporal = canonical.temporal_authority
    step = action.build_common_corridor_step_v01(transaction_id=canonical.transaction_id,owning_local_root_id=canonical.owning_local_root_id,
        packet_id=packet_id,authorization_candidate_id=canonical.authorization_candidate.root_packet_authorization_candidate_id,
        action_class=canonical.selected_canonical_action,adapter_binding=canonical.adapter_binding,subject_scope=canonical.normalized_subject_scope,
        target_scope=canonical.normalized_target_scope,effect_parameters=canonical.normalized_effect_parameters,
        issued_at_utc=temporal.issued_at_utc,expires_at_utc=temporal.expires_at_utc)
    corridor = action.build_common_contract_fulfillment_corridor_v01(transaction_id=canonical.transaction_id,
        owning_local_root_id=canonical.owning_local_root_id,packet_id=packet_id,corridor_class=canonical.adapter_binding.corridor_class,steps=(step,))
    return dict(transition_events=entry.transition_events+(event,),disposition_event=reserve,corridor=corridor,corridor_step=step)


def install_v01(host, source, request, admitted, inputs, object_ref, target_ref, evidence, quote_work, checks, *, valid_to=None, transaction_id=None):
    canonical,observation = canonical_action_v01(request,host.owning_root_id,admitted,inputs,object_ref,target_ref,evidence,
        valid_to=valid_to,transaction_id=transaction_id)
    projection,review = review_candidate_v01(canonical,bsep_ref=quote_work['program'].candidate.bsep_ref,
        topology_ref=quote_work['program'].topology_artifact.artifact_id,checks=checks)
    bound = action.build_native_root_bound_action_commit_packet_v01(canonical_projection=canonical,root_decision_projection=projection)
    material = pending_material_v01(bound)
    source.install_observations_v01((observation,))
    hosts.install_current_action_v01(host,root_bound=bound,admission_id=admitted.admission_id,inputs=inputs,
        **material,expected_revision=host.revision,evaluation_time=source.snapshot.evaluation_time,
        evaluation_time_source=source.snapshot.evaluation_time_source,evaluation_context_id=source.snapshot.evaluation_context_id)
    return dict(bound=bound,admitted=admitted,inputs=inputs,material=material,observation=observation,
        evidence=evidence,checks=checks,root_review=review,host=host,source=source,pending_registry=host.registry)


def refresh_dependency_v01(prepared, evidence, valid_to):
    """Publish changed current facts, without altering the already accepted packet."""
    source = prepared['source']; canonical = prepared['bound'].canonical_projection
    old = prepared['observation']; now = source.read_current_v01().evaluation_time
    expires = min(canonical.temporal_authority.expires_at_utc,valid_to)
    if now>=expires:
        source.withdraw_observations_v01((old.dependency_id,))
        return None
    digest = action.domain_separated_sha256_hex_v01(domain='testflix.authoritative_dependency.v01',payload=c.canonical_v01(evidence))
    evidence_ref = 'evidence:'+digest
    envelope = action.build_action_dependency_time_envelope_id_v01(dependency_id=old.dependency_id,evidence_ref=evidence_ref,
        content_sha256=digest,freshness_policy_id=old.freshness_policy_id,source_provenance_refs=old.source_provenance_refs,
        valid_from_utc=old.valid_from_utc,valid_to_utc=expires)
    observed = action.build_action_dependency_current_observation_v01(dependency_id=old.dependency_id,evidence_ref=evidence_ref,
        observed_content_sha256=digest,time_envelope_id=envelope,freshness_policy_id=old.freshness_policy_id,
        source_provenance_refs=old.source_provenance_refs,valid_from_utc=old.valid_from_utc,valid_to_utc=expires,
        observed_at_utc=now,observation_context_id=source.snapshot.evaluation_context_id)
    source.install_observations_v01((observed,))
    return observed


def dispatch_v01(prepared, task_id):
    host = prepared['host']
    source = prepared['source'].read_current_v01()
    registry,revision = hosts.dispatch_current_action_v01(host,packet_id=prepared['bound'].packet_identity.packet_id,
        task_id=task_id,expected_revision=host.revision,evaluation_time=source.evaluation_time,
        evaluation_time_source=source.evaluation_time_source,evaluation_context_id=source.evaluation_context_id)
    c.require_v01(registry is host.registry and revision==host.revision,'host_update_binding')
    context = registry.action_packet_fulfillment_attempt_contexts[-1]
    c.require_v01(context.receipt is not None,'native_dispatch_no_receipt')
    execution = firewall.native_execution_evidence_from_plain_data_v01(abi.kernel_artifact_to_plain_dict_v01(context.receipt)['payload']['execution_evidence'])
    registry = host.observe_receipt(packet_id=prepared['bound'].packet_identity.packet_id,
        attempt_evidence_id=context.attempt_evidence.attempt_evidence_id,expected_revision=host.revision,
        evaluation_time=source.evaluation_time+1,evaluation_time_source=source.evaluation_time_source)
    return dict(prepared,registry=registry,context=context,receipt=context.receipt,execution=execution,
        output=world.values_v01(execution.result.output))


def revoke_current_v01(prepared, *, bsep_ref, topology_ref):
    host = prepared['host']
    bound = prepared['bound']
    canonical = bound.canonical_projection
    packet_id = bound.packet_identity.packet_id
    now = prepared['source'].read_current_v01().evaluation_time
    candidate = action.build_revocation_candidate_v01(owning_local_root_id=host.owning_root_id,packet_id=packet_id,
        source_authorization_decision_id=bound.root_decision_projection.root_decision_result.decision_id,
        idempotency_key=canonical.idempotency_identity.idempotency_key,revocation_reason_class='LOCAL_OWNER_WITHDRAWAL',
        evidence_refs=('evidence:testflix:owner_revocation',),evidence_hashes=(action.domain_separated_sha256_hex_v01(
            domain='testflix.revocation.v01',payload=action.canonical_material_bytes_v01((('packet_id',packet_id),('requested_at',now)))),),
        evaluation_time=now,policy_fingerprint=canonical.authority_policy_fingerprint)
    projection,review = review_candidate_v01(canonical,bsep_ref=bsep_ref,topology_ref=topology_ref,
        checks=dict(owning_root=canonical.owning_local_root_id==host.owning_root_id,
            authorization_bound=action.validate_native_root_bound_action_commit_packet_v01(bound)[0]),
        candidate_kind='REVOCATION',candidate_id=candidate.revocation_candidate_id,predecessor=bound)
    accepted = action.build_accepted_revocation_binding_v01(candidate=candidate,root_projection=projection,packet=bound)
    dependency = canonical.dependency_candidate.dependency_records[0]
    invalidation = action.build_action_invalidation_evidence_v01(source_invalidation_event_ref='source:testflix:accepted_root_revocation',
        packet_id=packet_id,dependency_id='dependency:testflix:root_revocation',invalidation_class='ROOT_REVOCATION',
        evidence_ref=accepted.accepted_revocation_binding_id,evidence_sha256=accepted.accepted_revocation_binding_id.split(':',1)[1],
        observed_status='OBSERVED_ROOT_REVOCATION',time_envelope_id=dependency.time_envelope_id,freshness_policy_id=dependency.freshness_policy_id,
        owning_local_root_id=host.owning_root_id,accepted_by_local_root_id=host.owning_root_id,
        acceptance_root_decision_id=accepted.revocation_root_decision_id,acceptance_root_decision_hash=accepted.revocation_root_decision_hash,
        authority_effect='ROOT_REVOCATION',root_decision_ref=accepted.revocation_root_decision_id,evaluation_time=now,
        evaluation_time_source='testflix.controlled_utc',evaluation_context_id='context:testflix:revocation')
    profile = transitions.build_action_packet_transition_registry_profile_v01()
    rule_id = 'g2a_t18_pending_revoke'
    rule = transitions.lookup_action_packet_transition_rule_v01(registry=profile,transition_rule_id=rule_id)
    entry = next(e for e in host.registry.action_packet_lifecycle_entries if e.root_bound_genesis.packet_identity.packet_id==packet_id)
    state = action.derive_action_packet_lifecycle_state_v01(host.registry,packet_id=packet_id)
    latest = entry.transition_events[-1]
    materials = {
        'blocking_evidence_valid':(invalidation.invalidation_evidence_id,invalidation.invalidation_evidence_id,action.ACTION_INVALIDATION_EVIDENCE_PROFILE_ID_V01),
        'accepted_revocation_binding_valid':(accepted.accepted_revocation_binding_id,accepted.accepted_revocation_binding_id.split(':',1)[1],'accepted_revocation_binding_v01'),
        'source_authorization_binding_valid':(bound.root_decision_projection.root_decision_result.decision_id,bound.root_decision_projection.source_root_decision_hash,'root_decision_result_v01'),
        'packet_genesis_valid':(packet_id,packet_id.split(':',1)[1],'action_commit_packet_identity_profile_v01'),
        'authority_policy_valid':(canonical.authority_policy_fingerprint,canonical.authority_policy_fingerprint,action.ACTION_AUTHORITY_POLICY_PROFILE_ID_V01),
        'idempotency_reservation_owned':(state.latest_disposition_event_id,state.latest_disposition_event_id.split(':',1)[1],action.IDEMPOTENCY_DISPOSITION_EVENT_PROFILE_ID_V01),
        'adapter_not_called':(latest.execution_attempt_id,latest.execution_attempt_id.split(':',1)[1],action.EXECUTION_ATTEMPT_IDENTITY_PROFILE_ID_V01)}
    bindings = tuple(action.build_transition_evidence_binding_v01(action_packet_transition_registry_profile=profile,transition_rule_id=rule_id,
        evidence_code=code,evidence_ref=materials[code][0],evidence_sha256=materials[code][1],validator_profile_id=materials[code][2])
        for code in rule.required_evidence_codes)
    event = action.build_action_packet_transition_event_v01(action_packet_transition_registry_profile=profile,transition_rule_id=rule_id,
        packet_id=packet_id,idempotency_key=canonical.idempotency_identity.idempotency_key,previous_transition_event_id=latest.transition_event_id,
        owning_local_root_id=host.owning_root_id,root_decision_ref=projection.root_decision_result.decision_id,transition_evidence_bindings=bindings,
        dependency_set_candidate_fingerprint=canonical.dependency_set_candidate_fingerprint,temporal_authority_fingerprint=canonical.temporal_authority_fingerprint,
        evaluation_time=now,evaluation_time_source=invalidation.evaluation_time_source,evaluation_context_id=invalidation.evaluation_context_id,
        execution_attempt_identity=None,receipt_ref=None)
    return hosts.accept_current_revocation_v01(host,packet_id=packet_id,expected_revision=host.revision,revocation_candidate=candidate,
        revocation_root_projection=projection,accepted_revocation_binding=accepted,invalidation_evidence=invalidation,transition_event=event)
