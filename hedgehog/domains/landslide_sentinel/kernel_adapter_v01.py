"""EWS uses public common builders, never a domain replacement for Root/Host."""
from dataclasses import replace, asdict, dataclass
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
        self.reads = 0
        bridge = a.build_logical_time_bridge_v01(origin_utc_epoch_seconds=self.epoch,
            seconds_per_tick=1, bridge_policy_version='sentinel.monotonic.v01')
        self.snapshot = h.TrustedWorkSourceSnapshotV01((),bridge,self.epoch,'sentinel.monotonic_sample','sentinel:current',0)

    def read_current_v01(self):
        self.reads += 1
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
                *, predicate='monitoring_route_candidate', kind='ROUTE', permission=None, policy='sentinel:hard_policy', time_ref=None,
                claim_value=None):
    c.require(bool(checks) and all(type(v) is bool for v in checks.values()), 'root_checks_actual_boolean')
    req = sw.build_semantic_work_request_v01(request_id='review:'+candidate,transaction_id=transaction,target_root_id=root,
        runtime_topology_ref=topology,bounded_context_refs=(evidence_ref,),permitted_actor_ids=('sentinel:local_validator',),
        permitted_contribution_modes=('DETERMINISTIC',),requested_subjects=(subject,),required_evidence_classes=('DEPENDENCY_EVIDENCE',),
        forbidden_claims=('authority_creation',))
    ev = sw.build_evidence_binding_v01(evidence_id='binding:'+evidence_ref,evidence_ref=evidence_ref,evidence_class='DEPENDENCY_EVIDENCE',
        source_component_id='sentinel:local_validator',provenance_ref='sentinel:local_source',evidence_state='PRESENT')
    claim = sw.build_normalized_claim_v01(claim_id=candidate,subject=subject,predicate=predicate,
        object_or_value=dict(candidate_id=candidate,candidate_kind=kind) if claim_value is None else claim_value,time_envelope_ref='sentinel:time:'+str(now),
        provenance_refs=(evidence_ref,),evidence_refs=(ev.evidence_id,),confidence_micros=1000000,
        source_role='deterministic_runtime',source_mode='DETERMINISTIC')
    contribution = sw.build_actor_contribution_v01(contribution_id='contribution:'+candidate,request_id=req.request_id,
        actor_id='sentinel:local_validator',actor_role='deterministic_runtime',contribution_mode='DETERMINISTIC',bsep_projection_ref=bsep,
        scope=subject,bounded_context_refs=(evidence_ref,),claims=(claim,),evidence_bindings=(ev,),constraint_bindings=(),
        uncertainty_bindings=(),requested_validators=tuple(sorted(checks)),forbidden_claims_observed=())
    packet = sw.build_root_review_packet_from_contributions_v01(request=req,contributions=(contribution,),
        trust_profiles=trust.build_default_component_trust_profiles_v01())
    valid = all(checks.values())
    kernel = roots.build_root_decision_kernel_v01()
    inputs = roots.build_root_decision_input_v01(transaction_id=transaction,target_root_id=root,root_review_packet=packet,
        post_vv_bundle=dict(bundle_id=c.identity('checks',checks),post_vv_passed=valid,validated_candidate_ids=[candidate] if valid else [],
            rejected_candidate_ids=[] if valid else [candidate],required_evidence_refs=[evidence_ref],provided_evidence_refs=[evidence_ref],
            hard_failure_reasons=[] if valid else ['candidate_validation_failed']),
        gt_advisory=dict(advisory_id='gt:'+candidate,candidate_ids=[candidate],selected_candidate_id=candidate if valid else None,
            score_micros_by_candidate={candidate:1000000 if valid else 0},source_artifact_type='GTAdvisoryReport',source_lifecycle_state='VALIDATED',
            actor_role='gt',attempted_effect='CREATE_ROOT_DECISION',target_artifact_type='RootDecision',advisory_only=True,
            creates_final_output=False,requests_effect=False),
        policy_state=dict(policy_id=policy,identity_passed=valid,scope_passed=valid,hard_policy_passed=valid,allow_accept=valid,
            conflict_policy='DEFER',no_candidate_policy='NO_UPDATE'),
        permission_state=dict(permission_required=permission is not None,user_permission_present=permission is not None and valid,
            permission_scope_valid=valid,permission_ref=permission),
        temporal_state=dict(temporal_valid=True,expired=False,not_before_satisfied=True,time_envelope_ref=time_ref or 'sentinel:time:'+str(now)),
        conflict_state=dict(material_unresolved_conflict=bool(packet.conflict_set_ids),conflict_set_ids=list(packet.conflict_set_ids)),
        prior_root_state=dict(prior_decision_id=None,prior_decision=None,prior_selected_candidate_id=None))
    result = roots.decide_root_v01(kernel=kernel,decision_input=inputs)
    c.require(not roots.validate_root_decision_result_v01(kernel=kernel,decision_input=inputs,result=result), 'root_result_invalid')
    c.require(result.decision == 'ACCEPT', 'root_refusal:'+result.reason_code)
    return kernel, inputs, result


def semantic_source(request, request_id, root, now, orchestrator):
    if 'semantic_bindings' in orchestrator:
        from .semantic_adapter_v01 import validate_material
        validate_material(orchestrator)
        c.require(all(v['request']['target_root_id']==root for v in orchestrator['semantic_bindings']),'semantic_source_root')
    ref = c.identity('orchestrator', dict(request=request,output=orchestrator))
    bounded_meaning = c.canonical(dict(selection=orchestrator['selection'], input_ref=c.identity('diagnostic_inputs',orchestrator))).decode()
    semantic_facts=[bounded_meaning]
    for value in orchestrator.get('semantic_bindings',[]):
        semantic_facts.extend((value['request']['request_id'],value['contribution']['bounded_context_refs'][0],
            value['contribution']['contribution_id']+' '+value['intended_role']+' '+value['response']['diagnostic']))
    transaction = 'transaction:'+request_id
    decision = root_review(root,transaction,ref,request_id,dict(finite_diagnostic=orchestrator['selection'] in c.DIAGNOSTICS,
        source_bound=orchestrator['frames']==session_free_frames(orchestrator['frames'])),ref,'sentinel:intake:bounded','sentinel:route:proposal',now)
    business = packets.build_business_request_context_packet(packet_id='business:'+request_id,created_by='sentinel:local_intake',domain='LANDSLIDE_SENTINEL',
        request_id=request_id,business_subject='bounded_slope_monitoring',requested_action='bounded_monitoring',user_visible_summary=request)
    source_ref = dict(source='G2C_BUSINESS_REQUEST_CONTEXT_PACKET_V01',packet_id=business['packet_id'],request_id=request_id,domain_id='LANDSLIDE_SENTINEL')
    route_id = 'route:sentinel:monitor'
    vectors, guards = ('vector:'+ref,), ('guard:sentinel:current_root',)
    route = packets.build_orchestrator_route_context_packet(packet_id='route_context:'+ref,created_by='sentinel:local_canonicalization',source_refs=(source_ref,),
        domain='LANDSLIDE_SENTINEL',allowed_routes=(route_id,),required_guards=guards,selected_vector_ids=vectors,
        route_validation_expectations=dict(root_review_required=True,selected_only_allowed_vectors=True),orchestrator_is_root=False,
        creates_action_commit_packet=False,calls_connectors=False)
    proposal = dict(proposal_id='proposal:'+ref,suggested_route=route_id,selected_vector_ids=vectors,required_guards=guards,
        reason='Bounded diagnostic work with independent monitoring action review.',confidence=0.75,needs_review=True,
        uncertainty_notes=('Semantic proposal is not action permission.',),root_review_required=True,
        truth_claimed=False,authority_claimed=False,action_permission_claimed=False,final_output_claimed=False,
        connector_command_claimed=False,drs_write_claimed=False,plan_graph_claimed=False,bypass_root_claimed=False,
        semantic_observations=(bounded_meaning,),route_reasoning=('Bounded local sensor work.',),
        rejected_route_reasoning=('No physical equipment or public warning endpoints.',),guard_reasoning=('Current Root required per command.',),
        vector_reasoning=('Actual finite diagnostic selection.',),authority_boundary_reasoning=('SentinelRoot alone accepts.',))
    structured = rationale.build_orchestrator_structured_rationale(observed_semantics=proposal['semantic_observations'],
        route_selection_reason=proposal['route_reasoning'],rejected_routes=proposal['rejected_route_reasoning'],
        required_guards_reasoning=proposal['guard_reasoning'],selected_vector_reasoning=proposal['vector_reasoning'],
        uncertainty_notes=proposal['uncertainty_notes'],authority_boundary=proposal['authority_boundary_reasoning'],root_review_required=True)
    def ev(text, kind):
        return packets.semantic_evidence_item(text,source='runtime_canonicalization',evidence_kind=kind,confidence_label='medium')
    bsep = packets.build_bounded_semantic_evidence_packet(packet_id='bsep:'+ref,source_refs=(source_ref,),domain='LANDSLIDE_SENTINEL',
        source_role='orchestrator',target_role='architect',source_route_id=route_id,source_proposal_id=proposal['proposal_id'],
        source_context_packet_id=route['packet_id'],source_structured_rationale_ref='structured_rationale_v01:'+c.digest(structured),
        observed_semantic_facts=tuple(ev(text,'observed_fact') for text in semantic_facts),
        missing_evidence=(ev('Configuration and mock signal require independent current Root review.','missing_evidence'),),
        uncertainty_notes=(ev('Proposal only.','uncertainty'),),risk_boundary_notes=(ev('Local effects require finite packets.','risk_boundary'),),
        rejected_action_routes=(ev('No publication.','rejected_route'),),required_approvals_or_conditions=(ev(decision[2].decision_id,'approval_condition'),),
        authority_boundary_notes=(ev('No authority transfer.','authority_boundary'),),selected_vector_ids=vectors,required_guards=guards)
    source = router.build_execution_mode_source_context_v01(business_request_context_packet=business,bsep_packet=bsep,bsep_route_context_packet=route,
        bsep_orchestrator_proposal=proposal,bsep_structured_rationale=structured,sealed_replay_evidence=None,replay_source_manifest=None,
        replay_source_domain_projection=None,replay_source_safe_file_contents=(),replay_anchor_publication=None,replay_anchored_verification=None,
        replay_supplied_anchor_publication_id=None,replay_reconstructed_manifest=None,replay_reconstructed_domain_projection=None,
        replay_reconstructed_safe_file_contents=(),g2a_inspection=None,g2a_registry=None,g2a_packet_id=None,g2a_corridor=None,g2a_corridor_step=None,
        g2a_current_dependency_observations=(),g2a_logical_time_bridge=None,g2a_evaluation_time=now,g2a_evaluation_time_source='sentinel.monotonic_sample',
        g2a_evaluation_context_id='sentinel:current',g2a_transition_registry_profile=None,g2b_resolution_report=None,g2b_compatibility_projections=(),
        g2b_use_time=None,g2b_root_kernel=None,g2b_root_decision_input=None,g2b_root_decision_result=None,g2b_writeback_evidence=None)
    return source, decision


def materialize(session, responses, source):
    now = session.source.sample().evaluation_time
    stamp = lambda t: datetime.fromtimestamp(t,timezone.utc).isoformat()
    proposal = abi.build_kernel_artifact_v01(abi_version='v1.0',artifact_id=c.identity('semantics',responses),artifact_type='SemanticArchitectProposal',
        schema_version='v1',transaction_id='transaction:'+session.id,owner_root_id=session.root,source_component='semantic_architect',
        authority_class='ADVISORY',lifecycle_state='PROPOSED',payload=dict(roles=responses),trace_refs=('intent:'+session.id,),
        parent_refs=(source.bsep_packet['packet_id'],),time_envelope=dict(pt_created_at=stamp(now),kt_asof=stamp(now),et_observed_at=None,
            ct_session_anchor=session.id,ttl_seconds=3600,freshness_class='static',valid_from=stamp(now),valid_to=stamp(now+3600)))
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


@dataclass(frozen=True)
class ReviewedWorkBasis:
    """Live actual Work and Root evidence, not a public permission token."""
    host: object
    program: object
    results: tuple
    artifact: object
    common: dict
    review_bindings: tuple
    material: bytes
    dependencies: bytes
    review: tuple


def work_dependencies(session):
    state=getattr(session,'capabilities',None)
    return c.canonical(dict(root=session.root,task=session.id,policy=session.contract,frames=session.frames,tick=session.tick,
        observations=getattr(getattr(session,'book',None),'latest',None),
        capability=None if state is None else dict(profile=state.profile,harness=state.harness,site_online=state.site_online,revision=state.revision),
        series_source=c.digest(session.fixture.get('reserve_series') or session.fixture.get('reserve_series_raw'))))


def review_work(session,work,material,*,common=None,review_bindings=()):
    program,results,artifact=work
    if common is None:
        saved_program,common=session.last_work_common
        c.require(saved_program is program,'work_context_exact_program')
    ok,reasons=w.validate_work_program_result_v01(program,results,**common,host_map={session.root:session.host},review_bindings=review_bindings)
    c.require(ok and all(v.status=='COMPLETED' for v in results),'reviewed_work_result:'+repr(reasons))
    output=json.loads(caps.values(results[0].result.output)['material'])
    c.require(output['input_sha256']==c.digest(material),'reviewed_work_actual_material')
    candidate=c.identity('accepted_work',dict(artifact=artifact.artifact_id,output=output))
    review=root_review(session.root,'transaction:'+session.id,candidate,session.id,
        dict(actual_work=True,exact_input=True),artifact.artifact_id,program.candidate.bsep_ref,
        program.topology_artifact.artifact_id,session.source.sample().evaluation_time,claim_value=output)
    basis=ReviewedWorkBasis(session.host,program,results,artifact,common,review_bindings,c.canonical(material),work_dependencies(session),review)
    session.journal('CURRENT_WORK_ROOT_ACCEPTED',artifact_ref=artifact.artifact_id,root_decision=review[2].decision_id,
        bsep_ref=program.candidate.bsep_ref,topology_ref=program.topology_artifact.artifact_id,stage=material.get('phase','CONFIGURATION'))
    return basis


def validate_reviewed_work(session,basis):
    c.require(type(basis) is ReviewedWorkBasis and basis.host is session.host,'reviewed_work_host')
    c.require(basis.dependencies==work_dependencies(session),'reviewed_work_current_dependencies')
    material=__import__('json').loads(basis.material)
    if 'semantic_bindings' in material:
        from .semantic_adapter_v01 import validate_current
        validate_current(material,session,check_plan=False)
    ok,reasons=w.validate_work_program_result_v01(basis.program,basis.results,**basis.common,
        host_map={session.root:session.host},review_bindings=basis.review_bindings)
    c.require(ok,'reviewed_work_public_validation:'+repr(reasons))
    artifact=w.work_program_result_to_artifact_v01(basis.program,basis.results,**basis.common,
        host_map={session.root:session.host},review_bindings=basis.review_bindings)
    c.require(artifact==basis.artifact,'reviewed_work_artifact')
    output=json.loads(caps.values(basis.results[0].result.output)['material'])
    c.require(output['input_sha256']==c.digest(material),'reviewed_work_material')
    kernel,inputs,result=basis.review
    c.require(not roots.validate_root_decision_result_v01(kernel=kernel,decision_input=inputs,result=result)
        and result.decision=='ACCEPT' and result.target_root_id==session.root,'reviewed_work_root')
    packet=inputs.root_review_packet
    claims=packet.synthesis_proposal.normalized_claims
    c.require(len(claims)==1 and packet.runtime_topology_ref==basis.program.topology_artifact.artifact_id,'reviewed_work_root_topology')
    claim=sw.semantic_work_to_plain_dict_v01(claims[0])
    c.require(claim['object_or_value']==output and basis.artifact.artifact_id in claim['provenance_refs']
        and result.selected_candidate_id==c.identity('accepted_work',dict(artifact=artifact.artifact_id,output=output)),
        'reviewed_work_root_consumption')
    return output


def reviewed_work_refs(basis):
    return dict(work_artifact_ref=basis.artifact.artifact_id,root_decision_ref=basis.review[2].decision_id,
        bsep_ref=basis.program.candidate.bsep_ref,topology_ref=basis.program.topology_artifact.artifact_id,
        material_sha256=c.digest(basis.material),result_refs=[v.result.result_id for v in basis.results])


def prepare_command(session, values, checks, *, accepted_work=None):
    if values['op']=='READ_RESERVE_SERIES':c.require(accepted_work is not None,'series_requires_reviewed_plan')
    if accepted_work is not None:
        output=validate_reviewed_work(session,accepted_work)
        c.require(values['basis_ref']==accepted_work.artifact.artifact_id,'command_actual_work_basis')
        if values['op']=='READ_RESERVE_SERIES':
            c.require(output['stage']=='PLAN' and any(v['action']=='READ_RESERVE_SERIES' and
                v['source_ref']==values['source_ref'] for v in output['checks']),'series_plan_selected_read')
    admitted = session.catalogue[2]
    inputs = caps.records(dict(command=('TEXT',c.canonical(values).decode()),session=('REFERENCE',session.id),version=('INTEGER',session.version)))
    clock = session.source.sample()
    now, root = clock.evaluation_time, session.root
    object_ref = c.identity('command', dict(session=session.id,version=session.version,command=values))
    dep = 'dependency:'+object_ref
    fact = session.authorization_fact(values)
    if accepted_work is not None:fact=dict(fact,accepted_work=reviewed_work_refs(accepted_work))
    session.last_prepared_fact=fact
    sha = c.digest(fact)
    ref = 'evidence:'+sha
    expires = min(now+3600, session.expires)
    c.require(now < expires, 'monitoring_expired')
    env = a.build_action_dependency_time_envelope_id_v01(dependency_id=dep,evidence_ref=ref,content_sha256=sha,
        freshness_policy_id='sentinel:current',source_provenance_refs=('sentinel:local_source',),valid_from_utc=now,valid_to_utc=expires)
    dependency = a.build_dependency_set_candidate_v01(dependency_records=(a.build_dependency_set_candidate_record_v01(
        dependency_id=dep,dependency_class='DOMAIN_AUTHORIZATION_INPUT',evidence_ref=ref,content_sha256=sha,requirement_class='MANDATORY',
        time_envelope_id=env,freshness_policy_id='sentinel:current',source_provenance_refs=('sentinel:local_source',),expected_accepting_local_root_id=root),))
    permission = 'permission:'+object_ref
    policy = a.build_action_authority_policy_profile_v01(policy_version='sentinel.finite.v01',owning_local_root_id=root,
        authority_rule_refs=('sentinel:local_root_only',),kill_switch_condition_refs=('sentinel:owner_revoke',),retry_policy='NON_CONSUMING_RETRY',
        supersession_policy='ROOT_DECISION_ONLY',logical_effect_namespace='sentinel.command.v01',allowed_logical_effect_classes=('LOCAL_MONITORING_COMMAND',),
        allowed_business_object_namespaces=('sentinel.command',),allowed_corridor_classes=('sentinel.local.mock',))
    canonical = a.build_native_action_commit_packet_v01(transaction_id=getattr(session,'monitor_transaction','transaction:'+session.id),owning_local_root_id=root,
        canonical_permission_ref=permission,selected_canonical_action='mock_action:sentinel_monitoring_command',
        normalized_subject_scope=a.build_action_subject_scope_profile_v01(included_subject_refs=('sentinel:owner',),excluded_subject_refs=()),
        normalized_target_scope=a.build_action_target_scope_profile_v01(included_target_refs=(session.id,),excluded_target_refs=()),
        normalized_permission_scope=a.build_action_permission_scope_profile_v01(allowed_action_classes=('mock_action:sentinel_monitoring_command',),
            forbidden_action_classes=(),allowed_adapter_ids=('mock_adapter:sentinel_local',),forbidden_adapter_ids=(),required_approval_refs=(permission,),prohibited_effect_classes=()),
        adapter_binding=a.build_action_adapter_binding_profile_v01(corridor_class='sentinel.local.mock',adapter_id='mock_adapter:sentinel_local',
            adapter_kind='DETERMINISTIC_MOCK',adapter_version='v01'),dependency_candidate=dependency,
        temporal_authority=a.build_action_temporal_authority_profile_v01(issued_at_utc=now,expires_at_utc=expires,ttl_seconds=expires-now,temporal_policy_version='sentinel.finite.v01'),
        authority_policy=policy,business_object_identity=a.build_action_business_object_identity_profile_v01(business_object_class='DOMAIN_OBJECT',
            business_object_namespace='sentinel.command',business_object_ref=object_ref,owning_effect_root_id=root),
        consequential_effect_parameters=a.build_action_consequential_effect_parameters_profile_v01(amount_decimal=None,currency_code=None,quantity_decimal=None,parameter_records=inputs),
        evaluation_time=now,evaluation_time_source=clock.evaluation_time_source,evaluation_context_id=clock.evaluation_context_id,admitted_capability=admitted,inputs=inputs)
    candidate = canonical.authorization_candidate.root_packet_authorization_candidate_id
    basis_program=session.program if accepted_work is None else accepted_work.program
    review = root_review(root,canonical.transaction_id,candidate,object_ref,checks,ref,basis_program.candidate.bsep_ref,
        basis_program.topology_artifact.artifact_id,now,predicate='root_packet_authorization_candidate',kind='PACKET_AUTHORIZATION',
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
            evidence_code=code,evidence_ref='evidence:sentinel:'+code,evidence_sha256=c.digest(dict(packet=packet_id,root=review[2].decision_id,code=code)),
            validator_profile_id='sentinel:public_lifecycle') for code in rule.required_evidence_codes)
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
        time_envelope_id=env,freshness_policy_id='sentinel:current',source_provenance_refs=('sentinel:local_source',),valid_from_utc=now,valid_to_utc=expires,
        observed_at_utc=now,observation_context_id=clock.evaluation_context_id)
    return dict(root_bound=bound,corridor=corridor,corridor_step=step,transition_events=tuple(events),disposition_event=reserve), inputs, observation, review


def dispatch(session, value, checks, *, accepted_work=None):
    session.journal('ROOT_PREPARATION_START',op=value['op'])
    authorization, inputs, observation, review = prepare_command(session,value,checks,accepted_work=accepted_work)
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


def session_free_frames(frames):
    return [c.measurement(v) for v in frames]

from dataclasses import fields, replace, asdict
from datetime import datetime, timezone
import json
import time

from hedgehog import action_commit_packet_v02 as a, work_execution_host_v01 as hosts
from hedgehog import drs_semantic_address_v01 as address, drs_memory_resolution_v01 as memory
from hedgehog import drs_g2b_compatibility_v01 as compatibility, reuse_certificate_v01 as reuse
from hedgehog.kernel import abi_v01 as abi, execution_mode_router_v01 as router
from hedgehog.kernel import fractal_runtime_v02 as d, continuous_delta_runtime_v01 as e
from hedgehog.kernel import work_composition_v01 as w, transition_registry_v01 as transitions
from hedgehog.kernel import integrity_replay_v01 as integrity



def stamp(now):
    return datetime.fromtimestamp(now, timezone.utc).isoformat()

def information(session, material, now):
    """Session-local historical information for E's B contract; not warm DRS reuse."""
    scope=c.digest(dict(session=session.id,material=material))
    ref=c.digest(material)
    review=root_review(session.root,'transaction:'+session.id,ref,session.id,
        dict(actual_contract=material['contract']==session.contract),ref,session.program.candidate.bsep_ref,
        session.program.topology_artifact.artifact_id,now,claim_value=material)
    addr=address.build_semantic_address_v01(namespace='sentinel',domain='LANDSLIDE_SENTINEL',
        subject_class='bounded_diagnostic',intent_class='informational_summary',
        meaning_schema_id='sentinel.diagnostic',meaning_schema_version='v0.1')
    envelope=address.build_drs_time_envelope_v01(pt_created_at=now,kt_as_of=now,et_observed_at=now,ct_context_anchor=now,
        ttl_seconds=3600,valid_from=now,valid_to=now+3600,source_observed_at=now,source_reported_at=now,
        system_ingested_at=now,system_verified_at=now,freshness_policy_id='freshness:sentinel:media')
    authority=address.build_drs_authority_envelope_v01(authority_class='ROOT_ACCEPTED_WORK',owning_local_root_id=session.root,
        source_root_decision_input_id=review[1].decision_input_id,source_root_decision_id=review[2].decision_id,
        source_root_decision_hash=c.digest(roots.root_decision_result_to_plain_dict_v01(review[2])),
        authority_scope_fingerprint=scope,root_acceptance_state='ACCEPTED_WORK',recording_component='sentinel:monitor_information')
    record=address.build_meaning_record_v01(semantic_address=addr,predecessor_record_id=None,supersession_reason=None,
        safe_summary='Locally validated monitoring diagnostics. Preserve independent displacement, health, site and policy evidence.',
        semantic_tags=('monitoring',),resonance_reason='Exact current monitoring policy.',
        memory_pointers=(),artifact_pointers=(),source_reference_ids=(ref,),lineage_edges=(),time_envelope=envelope,
        authority_envelope=authority,persistent_lifecycle_state='ACTIVE',risk_hints=(),conflict_hints=(),
        reuse_policy_class='ANSWER_SHORTCUT',policy_version='sentinel.monitor.v01',schema_versions=('sentinel.monitor.v01',),
        content_fingerprint=c.digest(material),recording_component='sentinel:monitor_information')
    query=memory.build_drs_temporal_query_v01(query_mode='DIRECT_REUSE_CANDIDATE',semantic_address_id=addr.semantic_address_id,
        scope_fingerprint=scope,as_of=now,evaluation_time=now,evaluation_time_source='INJECTED_CURRENT_DECISION_TIME',
        time_range_start=now,time_range_end=now+3600,required_time_axes=('PT','KT','ET','CT','TTL','VALIDITY'),
        freshness_policy_id=envelope.freshness_policy_id,max_age_seconds=3600,domain=addr.domain,risk_class='LOW',
        reuse_intent='INFORMATIONAL_SHORTCUT_CONSIDERATION',requested_reuse_classes=('ANSWER_SHORTCUT',),
        required_evidence_classes=('SOURCE_IDENTITY','SOURCE_INTEGRITY','PROVENANCE_CHAIN','TIME_FITNESS','POLICY_COMPATIBILITY',
            'SCHEMA_COMPATIBILITY','CONFLICT_CLEARANCE','ROOT_DECISION','SOURCE_HISTORY'),forbidden_changes=('POLICY_CHANGED',),
        policy_version=record.policy_version,schema_versions=record.schema_versions,owning_local_root_id=session.root)
    ev=memory.evaluate_drs_candidate_v01(semantic_address=addr,query=query,meaning_record=record)
    c.require(ev.eligible_for_ranking,'monitor_information_ineligible:'+repr(ev.reason_codes))
    candidate=memory.build_resolution_candidate_v01(query_id=query.query_id,semantic_address_id=addr.semantic_address_id,
        meaning_record_id=record.meaning_record_id,query_evaluation_id=ev.query_evaluation_id,safe_summary=record.safe_summary,
        evidence_ref_ids=record.source_reference_ids,source_history_hash=ev.source_history_hash,action_history_binding_id=None,
        semantic_similarity_units=10000,freshness_units=ev.current_freshness_units,source_authority_prior_units=10000,
        lineage_proximity_units=10000,historical_utility_units=0,gt_advisory_prior_units=0,conflict_penalty_units=0,risk_penalty_units=0,retrieval_cost_units=1)
    ranked=memory.rank_eligible_drs_candidates_v01(query=query,query_evaluations=(ev,),candidates=(candidate,))
    budget=memory.build_memory_descent_budget_v01(max_depth=0,max_records_opened=1,max_pointers_opened=0,max_artifacts_opened=0,
        max_bytes_opened=0,max_lineage_edges=0,max_conflict_records=0)
    plan=memory.build_retrieval_plan_v01(query_id=query.query_id,semantic_address_id=addr.semantic_address_id,
        proposed_record_ids=(record.meaning_record_id,),proposed_memory_pointer_ids=(),proposed_artifact_pointer_ids=(),
        requested_descent_class='SUMMARY_ONLY',proposed_budget_id=budget.memory_descent_budget_id,required_access_policy_ids=(),reason_codes=())
    claim=dict(profile_version='v0.1',semantic_address_id=addr.semantic_address_id,meaning_record_id=record.meaning_record_id,
        query_id=query.query_id,query_evaluation_id=ev.query_evaluation_id,resolution_candidate_id=candidate.resolution_candidate_id,
        reuse_class='ANSWER_SHORTCUT',case_type='NON_ACTION_INFORMATIONAL',scope_fingerprint=scope,policy_version=query.policy_version,
        schema_versions=list(query.schema_versions),required_evidence_classes=list(query.required_evidence_classes),
        observed_evidence_fingerprint=ev.observed_evidence_fingerprint,forbidden_changes=list(query.forbidden_changes),
        checked_dependency_fingerprint=ev.checked_dependency_fingerprint,source_history_hash=ev.source_history_hash,
        action_history_binding_id=None,valid_from=now,valid_to=now+3600,issued_at=now,evaluated_at=now,
        root_shortcut_policy_ref='policy:drs_answer_shortcut:v0.1')
    review=root_review(session.root,query.query_id,candidate.resolution_candidate_id,addr.semantic_address_id,
        dict(eligible=ev.eligible_for_ranking,ranking=ranked==(candidate,)),ref,session.program.candidate.bsep_ref,
        session.program.topology_artifact.artifact_id,now,predicate='authorize_non_action_informational_answer_shortcut_v01',claim_value=claim)
    root_hash=a.domain_separated_sha256_hex_v01(domain='hedgehog:drs:root_shortcut_root_result_binding:v01',
        payload=c.canonical(roots.root_decision_result_to_plain_dict_v01(review[2])))
    shortcut=reuse.build_root_shortcut_authorization_projection_v01(owning_local_root_id=session.root,root_kernel_id=review[0].kernel_id,
        root_decision_input_id=review[1].decision_input_id,root_decision_id=review[2].decision_id,root_decision_hash=root_hash,
        selected_candidate_id=candidate.resolution_candidate_id,semantic_address_id=addr.semantic_address_id,meaning_record_id=record.meaning_record_id,
        query_id=query.query_id,query_evaluation_id=ev.query_evaluation_id,allowed_reuse_class='ANSWER_SHORTCUT',scope_fingerprint=scope,
        policy_version=query.policy_version,schema_versions=query.schema_versions,valid_from=now,valid_to=now+3600,
        root_shortcut_policy_ref=claim['root_shortcut_policy_ref'])
    certificate=reuse.build_reuse_certificate_v01(semantic_address_id=addr.semantic_address_id,meaning_record_id=record.meaning_record_id,
        query_id=query.query_id,query_evaluation_id=ev.query_evaluation_id,resolution_candidate_id=candidate.resolution_candidate_id,
        root_shortcut_authorization_projection=shortcut,case_type=claim['case_type'],required_evidence_classes=query.required_evidence_classes,
        observed_evidence_fingerprint=ev.observed_evidence_fingerprint,forbidden_changes=query.forbidden_changes,
        checked_dependency_fingerprint=ev.checked_dependency_fingerprint,valid_from=now,valid_to=now+3600,reuse_class='ANSWER_SHORTCUT',
        source_history_hash=ev.source_history_hash,action_history_binding_id=None,issued_at=now,evaluated_at=now)
    legacy=dict(record_id=record.meaning_record_id,layer='work',type='generic',domain=addr.domain,content=dict(summary=record.safe_summary),
        time_envelope=dict(pt_created_at=stamp(now),kt_asof=stamp(now),et_observed_at=stamp(now),ct_session_anchor=session.id,
            ttl_seconds=3600,freshness_class='static',valid_from=stamp(now),valid_to=stamp(now+3600)),
        provenance=dict(request_id=session.id,created_by='root_orchestrator',trace_refs=[dict(trace_id=ref)]),status='active')
    projection=compatibility.build_legacy_drs_projection_v01(source_family='LOCAL_DRS_DICT',source=legacy,target_semantic_address=addr)
    report=memory.build_drs_resolution_report_v01(semantic_address=addr,query=query,source_projections=(projection,),source_records=(record,),
        query_evaluations=(ev,),eligible_candidates=(candidate,),ranked_candidate_ids=(candidate.resolution_candidate_id,),
        selected_candidate_id=candidate.resolution_candidate_id,retrieval_plan=plan,memory_descent_result=None,root_shortcut_projection=shortcut,
        reuse_certificate=certificate,context_only_record_ids=(),historical_only_record_ids=(),warning_only_record_ids=(),
        rerun_required_record_ids=(),blocked_record_ids=(),provider_calls=0,network_calls=0,gemini_calls=0,external_drs_calls=0,
        connector_calls=0,real_world_effects_count=0,final_status='PASS',reason_codes=())
    c.require(reuse.validate_existing_root_shortcut_decision_v01(resolution_report=report,root_kernel=review[0],
        root_decision_input=review[1],root_decision_result=review[2],use_time=now)[0],'monitor_information_root_binding')
    return report,review

def source_family(session, common, item, candidate, now, information_pair, *, selected_mode='full_fractal'):
    report,review=information_pair
    scope=w.build_work_review_scope_ref_v01(candidate=candidate,item=item,source_context=common['source_context'],semantic_proposal=common['semantic_proposal'])
    ids=dict(request_id=session.id,transaction_id=report.query.query_id,owning_root_id=session.root,domain_id=report.query.domain)
    state=getattr(session,'capabilities',None)
    capability_snapshot='capabilities:sentinel:local' if state is None else c.identity('capabilities',dict(
        profile=state.profile,harness=state.harness,site_online=state.site_online,revision=state.revision,physical_local_slm=False))
    profiles=tuple(router.build_execution_mode_local_mode_profile_v01(**ids,mode=mode,policy_snapshot_id='policy:sentinel:monitor_review',
        capability_snapshot_id=capability_snapshot,cost_model_id='cost:sentinel:bounded',policy_allowed=mode==selected_mode,
        scope_allowed=True,risk_allowed=True,privacy_allowed=True,capability_state='NOT_REQUIRED' if mode in
        ('sealed_replay','direct_informational_reuse') else mode_availability(session,mode),capability_id=None if mode in
        ('sealed_replay','direct_informational_reuse') else 'capability:sentinel:'+mode,cost_units=i+1)
        for i,mode in enumerate(router.EXECUTABLE_EXECUTION_MODES_V01))
    snapshot=router.build_execution_mode_local_routing_snapshot_v01(**ids,request_class='BOUNDED_REVIEW',action_class='NON_ACTION',
        action_packet_relation='NOT_APPLICABLE',scope_class='BOUNDED',scope_ref=scope,permitted_narrower_scope_refs=(),risk_class='LOW',
        policy_snapshot_id='policy:sentinel:monitor_review',capability_snapshot_id=capability_snapshot,cost_model_id='cost:sentinel:bounded',
        required_user_input_state='COMPLETE',hard_block_state='CLEAR',evaluation_time_epoch_seconds=now,pt_created_at_utc=stamp(now),
        et_observed_at_utc=stamp(now),ct_session_anchor=session.id,ttl_seconds=3600,freshness_class='static',
        valid_from_utc=stamp(now),valid_to_utc=stamp(now+3600),mode_profiles=profiles)
    source=router.build_execution_mode_source_context_v01(**dict({f.name:getattr(common['source_context'],f.name) for f in fields(common['source_context'])},
        g2a_evaluation_time=now,g2a_evaluation_time_source=snapshot.created_by,g2a_evaluation_context_id=snapshot.local_routing_snapshot_id,
        g2b_resolution_report=report,g2b_compatibility_projections=report.source_projections,g2b_use_time=now,
        g2b_root_kernel=review[0],g2b_root_decision_input=review[1],g2b_root_decision_result=review[2]))
    routing=router.build_execution_mode_router_input_v01(request_id=session.id,transaction_id=ids['transaction_id'],owning_root_id=session.root,
        bsep_binding=router.build_execution_mode_bsep_binding_v01(**ids,source_context=source),local_routing_snapshot=snapshot,
        replay_binding=router.build_execution_mode_replay_not_applicable_binding_v01(**ids),
        g2a_binding=router.build_execution_mode_g2a_no_packet_binding_v01(**ids,evaluation_time=now,
            evaluation_time_source=snapshot.created_by,evaluation_context_id=snapshot.local_routing_snapshot_id),
        g2b_binding=router.build_execution_mode_g2b_binding_v01(**ids,source_context=source))
    proposal,validated=router.route_execution_mode_v01(router_input=routing,source_context=source)
    c.require(validated.validation_status=='PASS' and proposal.selected_mode==selected_mode,'monitor_C_route')
    artifact=router.project_execution_mode_proposal_kernel_artifact_v01(proposal=proposal,router_input=routing,source_context=source)
    registry=transitions.build_execution_mode_transition_registry_profile_v01()
    before=router.evaluate_execution_mode_proposal_to_root_transition_v01(registry=registry,proposal=proposal,router_input=routing,
        source_context=source,proposal_artifact=artifact)
    ri=router.build_root_execution_mode_review_input_v01(proposal=proposal,router_input=routing,source_context=source,proposal_artifact=artifact,
        proposal_transition_decision=before,review_action='ACCEPT',accepted_scope_ref=scope,narrowing_basis_refs=())
    decision,rk,rinput,result,validated=router.review_execution_mode_proposal_v01(review_input=ri,proposal=proposal,router_input=routing,
        source_context=source,proposal_artifact=artifact,proposal_transition_decision=before)
    c.require(validated.validation_status=='PASS' and decision.outcome=='ACCEPT','monitor_C_Root')
    args=dict(review_input=ri,decision=decision,proposal=proposal,router_input=routing,source_context=source,proposal_artifact=artifact,
        proposal_transition_decision=before,root_kernel=rk,root_decision_input=rinput,root_decision_result=result)
    da=router.project_root_execution_mode_decision_kernel_artifact_v01(**args)
    after=router.evaluate_execution_mode_root_route_transition_v01(registry=registry,**args,decision_artifact=da)
    eligibility=router.project_execution_mode_route_eligibility_kernel_artifact_v01(**args,decision_artifact=da,root_route_transition_decision=after)
    if hasattr(session,'routes'):
        from .evidence_v01 import plain
        session.routes.append(dict(tick=session.tick,snapshot=plain(snapshot),proposal=plain(proposal),
            decision=plain(decision),root=plain(result),eligibility=abi.kernel_artifact_to_plain_dict_v01(eligibility)))
    if selected_mode not in ('full_fractal','full_semantic'):
        return None,dict(common,source_context=source)
    args['g2c_source_context']=args.pop('source_context')
    ds=d.build_fractal_runtime_source_context_v02(**args,transition_registry=registry,decision_artifact=da,root_route_transition_decision=after,
        route_eligibility_artifact=eligibility,runtime_policy=d.build_fractal_runtime_policy_v02(
            required_downstream_capability_ids=proposal.required_downstream_capability_ids,permitted_child_scope_refs=()))
    return ds,dict(common,source_context=source)


def mode_availability(session,mode):
    if mode=='local_slm':return 'UNAVAILABLE'
    if mode=='cloud_llm':
        state=getattr(session,'capabilities',None)
        return 'AVAILABLE' if state is not None and state.available('harness') else 'UNAVAILABLE'
    return 'AVAILABLE'

def assemble(session, material):
    """D review gates a real pure Work item whose output is the finite monitoring plan."""
    now=session.source.sample().evaluation_time
    info=information(session,material,now)
    session.monitor_transaction=info[0].query.query_id
    if 'semantic_bindings' in material:
        from .semantic_adapter_v01 import validate_current
        validate_current(material,session)
    source,_=semantic_source(session.request,session.id,session.root,now,material)
    proposal=abi.build_kernel_artifact_v01(abi_version='v1.0',artifact_id=c.identity('monitor_semantics',material),
        artifact_type='SemanticArchitectProposal',schema_version='v1',transaction_id=session.monitor_transaction,owner_root_id=session.root,
        source_component='semantic_architect',authority_class='ADVISORY',lifecycle_state='PROPOSED',payload=material,
        trace_refs=('intent:'+session.id,),parent_refs=(source.bsep_packet['packet_id'],),time_envelope=dict(pt_created_at=stamp(now),
            kt_asof=stamp(now),et_observed_at=None,ct_session_anchor=session.id,ttl_seconds=3600,freshness_class='static',
            valid_from=stamp(now),valid_to=stamp(now+3600)))
    admitted=next(x for x in session.catalogue if x.definition.operation_id=='sentinel.diagnostic.v01')
    common=dict(catalogue=session.catalogue,source_context=source,semantic_proposal=proposal)
    item=w.WorkItemV01('diagnostic',admitted.definition.definition_id,session.root,
        (w.WorkInputBindingV01('material',w.WorkLiteralV01(caps.records(dict(material=('TEXT',c.canonical(
            material if 'semantic_bindings' in material else {k:material[k] for k in ('selection','frames','contract')}).decode())))[0])),),(),(),None,None)
    params=dict(task_id=session.id,previous_revision_id=None,intent_ref='intent:'+session.id,bsep_ref=source.bsep_packet['packet_id'],
        semantic_proposal_ref=proposal.artifact_id,catalogue_revision=0,budget=w.WorkBudgetV01(4,4,0,4,0),items=(item,),trigger_evidence_refs=())
    candidate=w.build_work_program_candidate_v01(**params,**common)
    ds,common=source_family(session,common,item,candidate,now,info)
    candidate=w.build_work_program_candidate_v01(**params,**common)
    obligation=w.build_work_review_obligation_v01(candidate=candidate,item=item,source_context=ds)
    item=replace(item,review_obligation_id=obligation.obligation_id)
    candidate=w.build_work_program_candidate_v01(**dict(params,items=(item,)),**common)
    program=w.materialize_work_program_v01(candidate,**common)
    obligation=w.build_work_review_obligation_v01(candidate=candidate,item=item,source_context=ds)
    session.journal('COMMON_D_START')
    start=time.monotonic();bundle,report=d.run_fractal_runtime_v02(ds)
    session.timings.append(dict(phase='common_D',seconds=time.monotonic()-start))
    session.journal('COMMON_D_RETURN',status=report.status,reasons=list(report.reason_codes))
    c.require(bundle is not None and report.status=='PASS','monitor_D:'+repr(report.reason_codes))
    bindings=((obligation,ds,bundle),)
    c.require(w.validate_work_review_binding_v01(obligation,candidate=candidate,item=item,source_context=ds,
        execution_bundle=bundle,semantic_proposal=proposal)[0],'monitor_D_work_binding')
    results=w.advance_work_program_v01(program,**common,host_map={session.root:session.host},review_bindings=bindings)
    ok,reasons=w.validate_work_program_result_v01(program,results,**common,host_map={session.root:session.host},review_bindings=bindings)
    c.require(ok and len(results)==1 and results[0].status=='COMPLETED','monitor_work:'+repr(reasons))
    artifact=w.work_program_result_to_artifact_v01(program,results,**common,host_map={session.root:session.host},review_bindings=bindings)
    output=json.loads(caps.values(results[0].result.output)['material'])
    return dict(now=now,information=info,source=ds,bundle=bundle,report=report,program=program,common=common,
        obligation=obligation,results=results,artifact=artifact,output=output,material=material)

def source_artifact(payload, session, now, parents=()):
    ref=c.identity('monitor_source',dict(payload=payload,transaction=session.monitor_transaction,root=session.root,time=now,parents=parents))
    return abi.build_kernel_artifact_v01(abi_version='v1.0',artifact_id=ref,artifact_type='SemanticEvidence',schema_version='v1',
        transaction_id=session.monitor_transaction,owner_root_id=session.root,source_component='sentinel:local_monitor_observation',
        authority_class='EVIDENCE_ONLY',lifecycle_state='VALIDATED',payload=payload,trace_refs=('trace:'+ref,),parent_refs=parents,
        time_envelope=dict(pt_created_at=stamp(now),kt_asof=stamp(now),et_observed_at=stamp(now),ct_session_anchor=session.monitor_transaction,
            ttl_seconds=3600,freshness_class='static',valid_from=stamp(now),valid_to=stamp(now+3600)))

def prepare_delta_baseline(session):
    baseline=session.monitor_review['bundle'];pending=session.monitor_pending
    now=session.source.sample().evaluation_time
    prior=pending['authorization']['root_bound'].canonical_projection.dependency_candidate.dependency_records[0]
    original=source_artifact(dict(asdict(prior),source_provenance_refs=list(prior.source_provenance_refs),
        rainfall_source=session.rain_dependency()),session,now)
    sibling=source_artifact(session.monitor_review['material']['stable_sources'],session,now)
    projections=[]
    for index in (0,1):
        topology=baseline.topology;source=baseline.source_context
        child=d.derive_fractal_child_cell_id_v02(topology_seed_id=topology.topology_seed_id,parent_cell_id=topology.root_cell_id,
            canonical_child_index=index,accepted_mode=topology.accepted_mode,
            selected_local_mode_profile_id=source.proposal.selected_local_mode_profile_id,
            source_mode_profile_set_id=source.router_input.local_routing_snapshot.mode_profile_set_id,
            child_scope_ref=topology.accepted_scope_ref,runtime_policy_id=topology.runtime_policy_id,
            required_capability_ids=source.proposal.required_downstream_capability_ids,forbidden_claims=source.runtime_policy.forbidden_claims,child_depth=1)
        entries=[q for q in baseline.queue_entries if q.cell_id==child and q.predecessor_queue_entry_id is None]
        c.require(bool(entries),'monitor_actual_D_child')
        q=min(entries,key=lambda v:(v.canonical_priority,v.node_instance_sequence,v.snapshot_sequence))
        artifact=next(a for v,a in zip(baseline.queue_entries,baseline.queue_artifacts,strict=True) if v.queue_entry_id==q.queue_entry_id)
        plain=abi.kernel_artifact_to_plain_dict_v01(artifact)
        projection=source_artifact(dict(projection_profile_id='g2e_baseline_runtime_artifact_projection_v01',
            projected_runtime_artifact=plain,projected_runtime_artifact_sha256=c.digest(plain)),session,now,(artifact.artifact_id,))
        projections.append((child,projection))
    artifacts=(original,projections[0][1],sibling,projections[1][1])
    edges=(integrity.ArtifactDependencyEdgeV01(projections[0][1].artifact_id,original.artifact_id),
        integrity.ArtifactDependencyEdgeV01(projections[1][1].artifact_id,sibling.artifact_id))
    manifest=integrity.build_artifact_manifest_v01(transaction_id=session.monitor_transaction,profile=integrity.build_default_seal_profile_v01(),
        artifacts=tuple(abi.kernel_artifact_to_canonical_ref_v01(v) for v in artifacts),dependency_edges=edges,
        root_ownership_bindings=tuple(integrity.RootOwnershipBindingV01(v.artifact_id,session.root) for v in artifacts),
        evidence_class_bindings=tuple(integrity.EvidenceClassBindingV01(v.artifact_id,'SOURCE_EVIDENCE') for v in artifacts),
        authority_class_bindings=tuple(integrity.AuthorityClassBindingV01(v.artifact_id,v.authority_class) for v in artifacts))
    replay=integrity.verify_artifact_replay_v01(manifest=manifest,
        payload_rows=tuple((v.artifact_id,abi.kernel_artifact_to_plain_dict_v01(v)['payload']) for v in artifacts),expected_manifest_hash=manifest.manifest_hash)
    return dict(artifacts=artifacts,edges=edges,projections=projections,manifest=manifest,replay=replay)

def delta_arguments(session, capture, invalidation, observed_time):
    base=session.monitor_baseline;review=session.monitor_review;baseline=review['bundle'];b=review['information'][0]
    prior=base['artifacts'][0];old=abi.kernel_artifact_to_plain_dict_v01(prior)
    observed=source_artifact(dict(old['payload'],content_sha256=invalidation.evidence_sha256,rainfall_source=session.rain_dependency(),
        observed_status=invalidation.observed_status,invalidation_evidence_id=invalidation.invalidation_evidence_id,
        packet_id=invalidation.packet_id),session,observed_time,(prior.artifact_id,))
    source=e.build_continuous_delta_source_context_v01(integrity_manifest=base['manifest'],integrity_replay=base['replay'],
        baseline_source_artifacts=base['artifacts'],observed_source_artifacts=(observed,*base['artifacts'][1:]),
        g2a_registry=capture.registry,g2a_packet=capture.root_bound_packet,
        g2a_dependency_candidate=capture.root_bound_packet.canonical_projection.dependency_candidate,
        g2a_current_observations=capture.observations,g2a_root_invalidation_material=invalidation,
        g2b_resolution_report=b,g2b_reuse_certificate=b.reuse_certificate,g2b_writeback_evidence=None,
        g2c_source_context=baseline.source_context.g2c_source_context,
        baseline_g2c_route_eligibility_artifact=baseline.source_context.route_eligibility_artifact,baseline_g2d_execution_bundle=baseline,
        root_kernel=baseline.source_context.root_kernel,post_vv_profile=None,gt_profile=None,
        current_source_host=session.host,current_source_capture=capture)
    common=dict(transaction_id=b.query.query_id,owning_root_id=session.root,domain_id=b.query.domain,policy_version=b.query.policy_version,
        schema_versions=b.query.schema_versions,source_history_hash=b.query_evaluations[0].source_history_hash)
    edge_bindings=tuple((v.artifact_id,v.depends_on_artifact_id,('/content_sha256',) if v.depends_on_artifact_id==prior.artifact_id else (),
        'FIELD_CAUSAL' if v.depends_on_artifact_id==prior.artifact_id else 'ARTIFACT_DEPENDENCY') for v in base['edges'])
    basis,edges=e.project_integrity_replay_dependency_edges_v01(manifest=base['manifest'],replay=base['replay'],
        source_artifacts=base['artifacts'],graph_version=e.CONTINUOUS_DELTA_GRAPH_VERSION_V01,edge_projection_bindings=edge_bindings,**common)
    graph=e.build_dependency_graph_index_v01(graph_basis_sha256=basis,graph_version=e.CONTINUOUS_DELTA_GRAPH_VERSION_V01,
        manifest=base['manifest'],replay=base['replay'],source_artifacts=base['artifacts'],dependency_edges=edges,trace_refs=(prior.artifact_id,),**common)
    profile=e.build_dependency_fingerprint_profile_v01()
    fingerprints=tuple(e.build_dependency_fingerprint_v01(profile=profile,graph=graph,dependency_edges=edges,source_artifacts=artifacts,
        policy_version=b.query.policy_version,schema_versions=b.query.schema_versions,source_history_hash=common['source_history_hash'])
        for artifacts in (source.baseline_source_artifacts,source.observed_source_artifacts))
    new=abi.kernel_artifact_to_plain_dict_v01(observed)
    binding=e.build_delta_source_binding_v01(request_id=baseline.runtime_report.request_id,transaction_id=common['transaction_id'],
        owning_root_id=session.root,domain_id=common['domain_id'],baseline_source_artifact_id=prior.artifact_id,
        baseline_source_artifact_type=prior.artifact_type,baseline_source_artifact_sha256=c.digest(old),baseline_source_payload_sha256=c.digest(old['payload']),
        observed_source_artifact_id=observed.artifact_id,observed_source_artifact_type=observed.artifact_type,
        observed_source_artifact_sha256=c.digest(new),observed_source_payload_sha256=c.digest(new['payload']),
        baseline_report_id=baseline.runtime_report.report_id,baseline_graph_id=graph.graph_id,baseline_graph_version=graph.graph_version,
        baseline_policy_version=b.query.policy_version,observed_policy_version=b.query.policy_version,
        baseline_schema_versions=b.query.schema_versions,observed_schema_versions=b.query.schema_versions,
        baseline_source_history_hash=common['source_history_hash'],observed_source_history_hash=common['source_history_hash'],
        valid_from_utc=stamp(observed_time),valid_to_utc=stamp(observed_time+3600),trace_refs=(prior.artifact_id,observed.artifact_id))
    changed=e.build_changed_field_binding_v01(source_binding_id=binding.source_binding_id,json_pointer='/payload/content_sha256',
        prior_value_sha256=c.digest(old['payload']['content_sha256']),observed_value_sha256=c.digest(new['payload']['content_sha256']),
        change_class='FIELD_VALUE_CHANGE',observed_at_utc=stamp(observed_time),trace_refs=(binding.source_binding_id,))
    artifact=e.build_changed_artifact_binding_v01(source_binding_id=binding.source_binding_id,baseline_artifact_id=prior.artifact_id,
        baseline_artifact_type=prior.artifact_type,baseline_payload_sha256=c.digest(old['payload']),observed_artifact_id=observed.artifact_id,
        observed_artifact_type=observed.artifact_type,observed_payload_sha256=c.digest(new['payload']),baseline_dependency_fingerprint=fingerprints[0],
        observed_dependency_fingerprint=fingerprints[1],change_class='ARTIFACT_SUCCESSOR',observed_at_utc=stamp(observed_time),trace_refs=(binding.source_binding_id,))
    delta=e.build_world_state_delta_v01(ordered_source_binding_ids=(binding.source_binding_id,),request_id=binding.request_id,
        transaction_id=binding.transaction_id,owning_root_id=binding.owning_root_id,domain_id=binding.domain_id,
        baseline_report_id=baseline.runtime_report.report_id,baseline_graph_id=graph.graph_id,baseline_graph_version=graph.graph_version,
        observed_at_utc=stamp(observed_time),valid_from_utc=stamp(observed_time),valid_to_utc=stamp(observed_time+3600),
        baseline_policy_version=b.query.policy_version,observed_policy_version=b.query.policy_version,
        baseline_schema_versions=b.query.schema_versions,observed_schema_versions=b.query.schema_versions,
        baseline_source_history_hash=common['source_history_hash'],observed_source_history_hash=common['source_history_hash'],
        ordered_changed_field_binding_ids=(changed.changed_field_binding_id,),ordered_changed_artifact_binding_ids=(artifact.changed_artifact_binding_id,),
        dependency_fingerprint_before=fingerprints[0],dependency_fingerprint_after=fingerprints[1],trace_refs=(graph.graph_id,))
    return dict(source_context=source,source_bindings=(binding,),changed_field_bindings=(changed,),changed_artifact_bindings=(artifact,),
        delta=delta,dependency_edges=edges,dependency_graph=graph,retained_profile='fractal_retained_work_v01')

def consume_delta(session, bundle):
    """Follow the real changed-source -> D output chain before consuming availability."""
    source=bundle.source_context.observed_source_artifacts[0]
    payload=abi.kernel_artifact_to_plain_dict_v01(source)['payload']
    c.require(payload['rainfall_source']==session.changed_dependency, 'sentinel_delta_actual_source')
    c.require(bundle.final_root_decision_result.target_root_id==session.root and bundle.final_root_decision_result.decision=='ACCEPT','monitor_delta_Root')
    baseline=bundle.source_context.baseline_g2d_execution_bundle
    cell=session.monitor_baseline['projections'][0][0]
    prior=next(v.artifact_id for r,v in zip(baseline.cell_results,baseline.result_artifacts,strict=True) if r.cell_id==cell)
    bindings=tuple(v for v in bundle.recomputed_bindings if v.prior_artifact_id==prior)
    c.require(len(bindings)==1,'monitor_recomputed_result_binding')
    recomputed=bundle.recomputed_g2d_execution_bundle
    results=tuple(v for v in recomputed.cell_results if v.result_id==bindings[0].g2d_cell_result_ref)
    c.require(len(results)==1 and results[0].cell_id==cell and results[0].outcome=='COMPLETED' and
        results[0].accepted_output_refs and bindings[0].g2d_runtime_report_ref==recomputed.runtime_report.report_id,'monitor_completed_result')
    observed=recomputed.observed_work_context
    consumed=tuple(v for v in observed.ordered_binding_artifacts if
        abi.kernel_artifact_to_plain_dict_v01(v)['payload']['source_pair']['observed_identity_ref']==source.artifact_id and
        abi.kernel_artifact_to_plain_dict_v01(v)['payload']['topology_binding']['cell_ref']==cell)
    c.require(len(consumed)==1,'monitor_observed_source_consumption')
    rows=tuple(q for q in recomputed.queue_entries if q.cell_id==cell and q.state=='COMPLETED' and
        set(q.observed_output_refs).intersection(results[0].accepted_output_refs))
    c.require(rows and all(consumed[0].artifact_id in q.observed_evidence_refs for q in rows),'monitor_actual_output_evidence')
    artifacts={v.artifact_id:v for v in (*recomputed.queue_artifacts,*recomputed.result_artifacts,*observed.ordered_binding_artifacts)}
    frontier=[v.artifact_id for q,v in zip(recomputed.queue_entries,recomputed.queue_artifacts,strict=True) if q in rows];reached=set()
    while frontier:
        ref=frontier.pop()
        if ref in reached:continue
        reached.add(ref)
        if ref in artifacts:frontier.extend(artifacts[ref].parent_refs)
    c.require(consumed[0].artifact_id in reached,'monitor_causal_parent_chain')
    retained_sources=session.monitor_review['material']['stable_sources']
    c.require(abi.kernel_artifact_to_plain_dict_v01(bundle.source_context.observed_source_artifacts[2])['payload']==retained_sources,
        'sentinel_retained_source_evidence_changed')
    c.require(session.stable_sources()==retained_sources,'sentinel_unaffected_sources_changed')
    sibling=session.monitor_baseline['projections'][1][0]
    old=next(v for v in baseline.cell_results if v.cell_id==sibling)
    retained=tuple(v for v in recomputed.retained_consumptions if v.consumed_result==old)
    c.require(len(retained)==1,'monitor_unaffected_D_result_changed')
    old_artifact=next(v for r,v in zip(baseline.cell_results,baseline.result_artifacts,strict=True) if r==old)
    c.require(retained[0].consumed_result_artifact==old_artifact and
        retained[0].admission.evidence.historical_cell_result==old,'monitor_retained_original_evidence')
    c.require(any(old.result_id in v.ordered_child_result_ids for v in recomputed.cell_results),'monitor_retained_parent_consumption')
    return dict(rainfall=payload['rainfall_source']['rainfall'],contract=retained_sources['policy'],
        delta_result_ref=bundle.recomputation_result.recomputation_result_id,source_artifact_ref=source.artifact_id,
        recomputed_result_ref=results[0].result_id,output_refs=list(results[0].accepted_output_refs),consumed_binding_ref=consumed[0].artifact_id,
        preserved_source_sha256=c.digest(retained_sources),preserved_D_result_ref=old.result_id,
        retained_consumption_ref=retained[0].consumption_id,final_Root_review=bundle.final_root_decision_result.decision_id)


def recompute(session, capture, invalidation, observed_time):
    args=delta_arguments(session,capture,invalidation,observed_time)
    session.delta_arguments=args
    session.journal('COMMON_E_START')
    start=time.monotonic();bundle,report=e.run_continuous_delta_runtime_v01(**args)
    session.timings.append(dict(phase='common_E',seconds=time.monotonic()-start))
    session.journal('COMMON_E_RETURN',status=report.status,reasons=list(report.reason_codes))
    c.require(bundle is not None and report.status=='PASS','monitor_E:'+repr(report.reason_codes))
    session.delta_return=bundle
    from .evidence_v01 import plain,save
    retained=bundle.recomputed_g2d_execution_bundle
    save(session.directory/'logs'/'delta_causal_material.json',dict(delta=plain(args['delta']),
        current_temporal_binding=plain(retained.temporal_binding),
        graph=plain(args['dependency_graph']),source_bindings=plain(args['source_bindings']),
        baseline_artifacts=[abi.kernel_artifact_to_plain_dict_v01(v) for v in args['source_context'].baseline_source_artifacts],
        observed_artifacts=[abi.kernel_artifact_to_plain_dict_v01(v) for v in args['source_context'].observed_source_artifacts],
        observed_bindings=[abi.kernel_artifact_to_plain_dict_v01(v) for v in retained.observed_work_context.ordered_binding_artifacts],
        retained=[dict(consumption_id=v.consumption_id,admission_id=v.admission.admission_id,
            evaluation_time=v.admission.evaluation_time_epoch_seconds,temporal_binding=plain(v.admission.temporal_binding),
            historical_bundle_sha256=v.admission.evidence.historical_bundle_sha256,
            accepted_plan=abi.kernel_artifact_to_plain_dict_v01(v.admission.current_plan_artifact),
            parent_input=plain(v.admission.current_parent_input),field_bindings=plain(v.admission.field_bindings),
            historical_result=plain(v.consumed_result),historical_artifact=abi.kernel_artifact_to_plain_dict_v01(v.consumed_result_artifact))
            for v in retained.retained_consumptions],new_results=plain(retained.cell_results),queue_entries=plain(retained.queue_entries)))
    (session.directory/'logs'/'common_E_return.json').write_bytes(c.canonical(dict(
        report=plain(report),result=plain(bundle.recomputation_result),plan=plain(bundle.recomputation_plan),
        affected=plain(bundle.affected_result),bindings=plain(bundle.recomputed_bindings),
        final_Root=plain(bundle.final_root_decision_result))))
    for label,validator,value in (('supplied_D',d.validate_fractal_retained_work_execution_bundle_v01,bundle.recomputed_g2d_execution_bundle),
                                  ('supplied_E',e.validate_continuous_delta_execution_bundle_v01,bundle)):
        session.journal(label+'_START');start=time.monotonic();validation=validator(value)
        session.timings.append(dict(phase=label,seconds=time.monotonic()-start))
        session.journal(label+'_RETURN',status=validation.status,reasons=list(validation.reason_codes))
        c.require(validation.status=='PASS',label+':'+repr(validation.reason_codes))
    consumed=consume_delta(session,bundle)
    review=root_review(session.root,session.monitor_transaction,c.identity('monitor_continuation',consumed),session.id,
        dict(actual_E_consumed=consumed['rainfall']==session.changed_dependency['rainfall'],
             preserved_work=consumed['preserved_source_sha256']==c.digest(session.stable_sources())),
        consumed['recomputed_result_ref'],session.program.candidate.bsep_ref,
        session.program.topology_artifact.artifact_id,session.source.sample().evaluation_time,claim_value=consumed)
    return dict(arguments=args,bundle=bundle,report=report,consumed=consumed,review=review)
