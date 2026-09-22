"""Finite Supplier current-action session using ordinary public Root and Host laws."""
from dataclasses import replace
from decimal import Decimal
import time
from hedgehog import action_commit_packet_v02 as a, work_execution_host_v01 as h
from hedgehog.kernel import effect_firewall_v01 as fw, semantic_work_v01 as sw
from hedgehog.kernel import root_decision_v01 as roots, trust_model_v01 as trust, transition_registry_v01 as tr
from hedgehog.kernel import abi_v01 as abi
from hedgehog import outcome_feedback_v01 as f

CALLS=[]


def records(values):
    return tuple(a.build_action_effect_parameter_record_v01(parameter_name=n,value_type=t,value=v) for n,(t,v) in sorted(values.items()))


def values(records):
    return {v.parameter_name:v.value for v in records}


def input_check(definition,inputs):
    errors=fw.validate_capability_values_v01(definition.input_fields,inputs)
    return fw.build_capability_validation_evidence_v01(definition=definition,values=inputs,invocation_id=None,valid=not errors,reason_codes=errors)


def output_check(definition,invocation,output):
    expected=records(dict(order=('REFERENCE',values(invocation.inputs)['order']),state=('TEXT','CONFIRMED_MOCK')))
    errors=fw.validate_capability_values_v01(definition.output_fields,output)
    if output!=expected:errors+=('supplier_output_mismatch',)
    return fw.build_capability_validation_evidence_v01(definition=definition,values=output,invocation_id=invocation.invocation_id,valid=not errors,reason_codes=errors)


def execute_mock(invocation):
    CALLS.append(dict(invocation=invocation.invocation_id,inputs=values(invocation.inputs)))
    return records(dict(order=('REFERENCE',values(invocation.inputs)['order']),state=('TEXT','CONFIRMED_MOCK')))


class CurrentSourceV01:
    def __init__(self,now):
        self.snapshot=h.TrustedWorkSourceSnapshotV01((),a.build_logical_time_bridge_v01(origin_utc_epoch_seconds=now,
            seconds_per_tick=1,bridge_policy_version='supplier.current.v01'),now+4,'supplier.controlled_utc','supplier:dispatch',0)
    def read_current_v01(self):return self.snapshot
    def install(self,observation):
        self.snapshot=replace(self.snapshot,observations=(observation,),source_revision=self.snapshot.source_revision+1)


def review_operation_v01(root,transaction,candidate,subject,material,checks,*,canonical,permission=None,predicate='root_packet_authorization_candidate'):
    """Compose evidence and consume the ordinary public Root result; no authority algorithm."""
    ref='supplier:material:'+f.g35_hash_v01(material)
    request=sw.build_semantic_work_request_v01(request_id='review:'+candidate,transaction_id=transaction,target_root_id=root,
        runtime_topology_ref='supplier:bounded_native_operation',bounded_context_refs=(ref,),permitted_actor_ids=('supplier:validator',),
        permitted_contribution_modes=('DETERMINISTIC',),requested_subjects=(subject,),required_evidence_classes=('DEPENDENCY_EVIDENCE',),forbidden_claims=('authority_creation',))
    ev=sw.build_evidence_binding_v01(evidence_id='binding:'+ref,evidence_ref=ref,evidence_class='DEPENDENCY_EVIDENCE',
        source_component_id='supplier:validator',provenance_ref='supplier:local_consent',evidence_state='PRESENT')
    claim=sw.build_normalized_claim_v01(claim_id=candidate,subject=subject,predicate=predicate,
        object_or_value=dict(candidate_id=candidate,candidate_kind='PACKET_AUTHORIZATION'),time_envelope_ref=ref,
        provenance_refs=(ref,),evidence_refs=(ev.evidence_id,),confidence_micros=1000000,source_role='deterministic_runtime',source_mode='DETERMINISTIC')
    contribution=sw.build_actor_contribution_v01(contribution_id='contribution:'+candidate,request_id=request.request_id,
        actor_id='supplier:validator',actor_role='deterministic_runtime',contribution_mode='DETERMINISTIC',bsep_projection_ref=ref,
        scope=subject,bounded_context_refs=(ref,),claims=(claim,),evidence_bindings=(ev,),constraint_bindings=(),uncertainty_bindings=(),
        requested_validators=tuple(checks),forbidden_claims_observed=())
    packet=sw.build_root_review_packet_from_contributions_v01(request=request,contributions=(contribution,),trust_profiles=trust.build_default_component_trust_profiles_v01())
    valid=all(checks.values());kernel=roots.build_root_decision_kernel_v01()
    required=[ref]+[v.evidence_ref for v in canonical.dependency_candidate.dependency_records if v.requirement_class=='MANDATORY']
    inputs=roots.build_root_decision_input_v01(transaction_id=transaction,target_root_id=root,root_review_packet=packet,
        post_vv_bundle=dict(bundle_id=ref,post_vv_passed=valid,validated_candidate_ids=[candidate] if valid else [],rejected_candidate_ids=[] if valid else [candidate],
            required_evidence_refs=required,provided_evidence_refs=required,hard_failure_reasons=[] if valid else ['permission_scope_validation_failed']),
        gt_advisory=dict(advisory_id='gt:'+candidate,candidate_ids=[candidate],selected_candidate_id=candidate if valid else None,
            score_micros_by_candidate={candidate:1000000 if valid else 0},source_artifact_type='GTAdvisoryReport',source_lifecycle_state='VALIDATED',actor_role='gt',
            attempted_effect='CREATE_ROOT_DECISION',target_artifact_type='RootDecision',advisory_only=True,creates_final_output=False,requests_effect=False),
        policy_state=dict(policy_id=canonical.authority_policy_fingerprint,identity_passed=True,scope_passed=valid,hard_policy_passed=valid,allow_accept=valid,conflict_policy='DEFER',no_candidate_policy='NO_UPDATE'),
        permission_state=dict(permission_required=True,user_permission_present=permission is not None,permission_scope_valid=valid,permission_ref=permission),
        temporal_state=dict(temporal_valid=canonical.temporal_evaluation.executable,expired=canonical.evaluation_time>=canonical.temporal_authority.expires_at_utc,
            not_before_satisfied=canonical.evaluation_time>=canonical.temporal_authority.issued_at_utc,time_envelope_ref=canonical.temporal_authority_fingerprint),
        conflict_state=dict(material_unresolved_conflict=False,conflict_set_ids=[]),prior_root_state=dict(prior_decision_id=None,prior_decision=None,prior_selected_candidate_id=None))
    result=roots.decide_root_v01(kernel=kernel,decision_input=inputs)
    f._require(not roots.validate_root_decision_result_v01(kernel=kernel,decision_input=inputs,result=result),'g35_supplier_root')
    return kernel,inputs,result


def pending_material_v01(bound):
    canonical=bound.canonical_projection;result=bound.root_decision_projection.root_decision_result
    profile=tr.build_action_packet_transition_registry_profile_v01()
    registry=a.record_action_packet_genesis_v01(a.build_empty_action_commit_packet_registry_v02(),root_bound_genesis=bound,action_packet_transition_registry_profile=profile)
    packet=bound.packet_identity.packet_id;events=[]
    for index,rule_id in enumerate(('g2a_t01_activate_root_authorization','g2a_t02_queue','g2a_t03_pending')):
        rule=tr.lookup_action_packet_transition_rule_v01(registry=profile,transition_rule_id=rule_id);context='supplier:'+rule_id
        attempt=a.build_action_execution_attempt_identity_v01(packet_id=packet,idempotency_key=canonical.idempotency_identity.idempotency_key,
            attempt_ordinal=1,evaluation_context_id=context) if index==2 else None
        bindings=tuple(a.build_transition_evidence_binding_v01(action_packet_transition_registry_profile=profile,transition_rule_id=rule_id,
            evidence_code=code,evidence_ref='supplier:evidence:'+code,evidence_sha256=f.g35_hash_v01(dict(packet=packet,root=result.decision_id,code=code)),
            validator_profile_id='supplier:public_lifecycle') for code in rule.required_evidence_codes)
        event=a.build_action_packet_transition_event_v01(action_packet_transition_registry_profile=profile,transition_rule_id=rule_id,
            packet_id=packet,idempotency_key=canonical.idempotency_identity.idempotency_key,previous_transition_event_id=events[-1].transition_event_id if events else None,
            owning_local_root_id=canonical.owning_local_root_id,root_decision_ref=result.decision_id if index==0 else None,transition_evidence_bindings=bindings,
            dependency_set_candidate_fingerprint=canonical.dependency_set_candidate_fingerprint,temporal_authority_fingerprint=canonical.temporal_authority_fingerprint,
            evaluation_time=canonical.evaluation_time+index+1,evaluation_time_source='supplier.controlled_utc',evaluation_context_id=context,
            execution_attempt_identity=attempt,receipt_ref=None)
        events.append(event)
        if index==0:
            reserve=a.build_idempotency_disposition_event_v01(idempotency_key=canonical.idempotency_identity.idempotency_key,event_class='RESERVE',
                from_disposition='UNCLAIMED',to_disposition='RESERVED',from_owner_packet_id=None,to_owner_packet_id=packet,previous_disposition_event_id=None,
                cause_transition_event_ids=(event.transition_event_id,),root_decision_ref=result.decision_id,predecessor_packet_id=None,successor_packet_id=None,
                evidence_refs=tuple(sorted(v.transition_evidence_binding_id for v in bindings if v.evidence_code in ('packet_genesis_valid','source_root_authorization_valid','idempotency_acquisition_valid'))),
                evaluation_time=event.evaluation_time,evaluation_time_source=event.evaluation_time_source,evaluation_context_id=context)
            registry=a.activate_action_packet_lifecycle_v01(registry,packet_id=packet,transition_event=event,disposition_event=reserve,action_packet_transition_registry_profile=profile)
        else:registry=a.append_action_packet_lifecycle_transition_v01(registry,packet_id=packet,transition_event=event,action_packet_transition_registry_profile=profile)
    step=a.build_common_corridor_step_v01(transaction_id=canonical.transaction_id,owning_local_root_id=canonical.owning_local_root_id,packet_id=packet,
        authorization_candidate_id=canonical.authorization_candidate.root_packet_authorization_candidate_id,action_class=canonical.selected_canonical_action,
        adapter_binding=canonical.adapter_binding,subject_scope=canonical.normalized_subject_scope,target_scope=canonical.normalized_target_scope,
        effect_parameters=canonical.normalized_effect_parameters,issued_at_utc=canonical.temporal_authority.issued_at_utc,expires_at_utc=canonical.temporal_authority.expires_at_utc)
    corridor=a.build_common_contract_fulfillment_corridor_v01(transaction_id=canonical.transaction_id,owning_local_root_id=canonical.owning_local_root_id,
        packet_id=packet,corridor_class=canonical.adapter_binding.corridor_class,steps=(step,))
    return dict(transition_events=tuple(events),disposition_event=reserve,corridor=corridor,corridor_step=step)


class SupplierSessionV01:
    """A local controlled confirmation policy. Documents cannot grant consent."""
    def __init__(self, *, episode=None, now=None, review_catalogue=()):
        self.root='root:gate3:supplier:bank';self.now=int(time.time());self.source=CurrentSourceV01(self.now)
        if now is not None:
            f._require(type(now) is int and now>0,'g36_clock')
            self.now=now;self.source=CurrentSourceV01(now)
        self.episode=episode
        self.consent={'supplier:A':('permission:owner:supplier:A',1500)};self.results=[];self.call_start=len(CALLS)
        functions=(input_check,output_check,execute_mock);codes=tuple(h.observe_local_capability_code_v01(v) for v in functions)
        bindings=(fw.build_capability_business_input_binding_v01(input_name='amount',source_kind='AMOUNT',source_name='amount_decimal',value_type='DECIMAL'),
            fw.build_capability_business_input_binding_v01(input_name='order',source_kind='BUSINESS_OBJECT_REF',source_name='business_object_ref',value_type='REFERENCE'),
            fw.build_capability_business_input_binding_v01(input_name='supplier',source_kind='TARGET_RECORD',source_name='supplier',value_type='REFERENCE'))
        semantics=fw.build_capability_business_semantics_v01(operation_key='supplier.confirm.v01',selected_action_class='mock_action:supplier_confirm',
            logical_effect_class='SUPPLIER_CONFIRM',logical_effect_namespace='supplier.confirm.v01',business_object_class='DOMAIN_OBJECT',
            business_object_namespace='supplier.order',input_bindings=bindings)
        definition_fields=dict(operation_id='supplier.confirm.v01',version='v01',effect_kind='MOCK_CONSEQUENTIAL',business_semantics=semantics,
            input_fields=tuple(fw.build_capability_field_v01(name=n,value_type=t,required=True,consequential=True) for n,t in (('amount','DECIMAL'),('order','REFERENCE'),('supplier','REFERENCE'))),
            output_fields=tuple(fw.build_capability_field_v01(name=n,value_type=t,required=True,consequential=False) for n,t in (('order','REFERENCE'),('state','TEXT'))),
            input_validator_ref=codes[0].public_symbol,output_validator_ref=codes[1].public_symbol,executor_ref=codes[2].public_symbol,
            code_sha256s=tuple((v.public_symbol,v.source_sha256) for v in codes))
        self.admissions={}
        for supplier in ('supplier:A','supplier:B'):
            definition=fw.build_capability_definition_v01(**definition_fields,resource_refs=(supplier,))
            self.admissions[supplier]=h.admit_local_capability_v01(definition=definition,input_validator=input_check,output_validator=output_check,executor=execute_mock,catalogue_revision=0,host_instance_ref='host:'+self.root)
        self.host=h.build_root_work_execution_host_v01(owning_root_id=self.root,registry=a.build_empty_action_commit_packet_registry_v02(),catalogue=tuple(self.admissions.values())+tuple(review_catalogue),
            packet_bindings=(),current_dependency_observations=(),logical_time_bridge=self.source.snapshot.logical_time_bridge,trusted_source=self.source)

    def prepare_v01(self,supplier,*,document_claim=None,amount='10',order=None,install=True):
        f._require(type(install) is bool,'g36_install_mode')
        f._require(supplier in self.admissions and type(amount) is str and amount in ('10','16'),'g36_finite_proposal')
        f._require(order is None or self.episode is not None and order in ('order:'+self.episode+':objective','order:'+self.episode+':historical'),'g36_order_scope')
        admitted=self.admissions[supplier]
        order=order or 'order:gate3:'+supplier;transaction='transaction:'+order
        approved=self.consent.get(supplier);material=dict(supplier=supplier,order=order,amount=amount,document_claim=document_claim)
        valid=approved is not None and int(Decimal(amount)*100)<=approved[1]
        permission=approved[0] if approved else None;digest=f.g35_hash_v01(material);ref='supplier:evidence:'+digest;dep='dependency:'+order
        expires=self.now+120;provenance=('supplier:owner_confirmation',)
        time_id=a.build_action_dependency_time_envelope_id_v01(dependency_id=dep,evidence_ref=ref,content_sha256=digest,
            freshness_policy_id='supplier:current',source_provenance_refs=provenance,valid_from_utc=self.now,valid_to_utc=expires)
        dependency=a.build_dependency_set_candidate_v01(dependency_records=(a.build_dependency_set_candidate_record_v01(dependency_id=dep,
            dependency_class='DOMAIN_AUTHORIZATION_INPUT',evidence_ref=ref,content_sha256=digest,requirement_class='MANDATORY',time_envelope_id=time_id,
            freshness_policy_id='supplier:current',source_provenance_refs=provenance,expected_accepting_local_root_id=self.root),))
        inputs=records(dict(amount=('DECIMAL',amount),order=('REFERENCE',order),supplier=('REFERENCE',supplier)))
        canonical=a.build_native_action_commit_packet_v01(transaction_id=transaction,owning_local_root_id=self.root,canonical_permission_ref=permission or 'permission:supplier:missing_confirmation',
            selected_canonical_action='mock_action:supplier_confirm',normalized_subject_scope=a.build_action_subject_scope_profile_v01(included_subject_refs=('subject:gate3:buyer',),excluded_subject_refs=()),
            normalized_target_scope=a.build_action_target_scope_profile_v01(included_target_refs=(supplier,),excluded_target_refs=()),
            normalized_permission_scope=a.build_action_permission_scope_profile_v01(allowed_action_classes=('mock_action:supplier_confirm',),forbidden_action_classes=(),
                allowed_adapter_ids=('mock_adapter:supplier',),forbidden_adapter_ids=(),required_approval_refs=(permission or 'permission:supplier:missing_confirmation',),prohibited_effect_classes=()),
            adapter_binding=a.build_action_adapter_binding_profile_v01(corridor_class='supplier.mock',adapter_id='mock_adapter:supplier',adapter_kind='DETERMINISTIC_MOCK',adapter_version='v01'),
            dependency_candidate=dependency,temporal_authority=a.build_action_temporal_authority_profile_v01(issued_at_utc=self.now,expires_at_utc=expires,ttl_seconds=120,temporal_policy_version='supplier:ttl:v01'),
            authority_policy=a.build_action_authority_policy_profile_v01(policy_version='supplier:consent:v01',owning_local_root_id=self.root,authority_rule_refs=('supplier:local_root',),
                kill_switch_condition_refs=('supplier:revocation',),retry_policy='NON_CONSUMING_RETRY',supersession_policy='ROOT_DECISION_ONLY',logical_effect_namespace='supplier.confirm.v01',
                allowed_logical_effect_classes=('SUPPLIER_CONFIRM',),allowed_business_object_namespaces=('supplier.order',),allowed_corridor_classes=('supplier.mock',)),
            business_object_identity=a.build_action_business_object_identity_profile_v01(business_object_class='DOMAIN_OBJECT',business_object_namespace='supplier.order',business_object_ref=order,owning_effect_root_id=self.root),
            consequential_effect_parameters=a.build_action_consequential_effect_parameters_profile_v01(amount_decimal=amount,currency_code='EUR',quantity_decimal=None,
                parameter_records=tuple(v for v in inputs if v.parameter_name=='supplier')),evaluation_time=self.now,evaluation_time_source='supplier.controlled_utc',evaluation_context_id='supplier:canonical',
            admitted_capability=admitted,inputs=inputs)
        review=review_operation_v01(self.root,transaction,canonical.authorization_candidate.root_packet_authorization_candidate_id,order,material,
            dict(explicit_local_confirmation=valid,document_is_not_confirmation=True),canonical=canonical,permission=permission)
        prepared=dict(material=material,canonical=canonical,review=review,inputs=inputs,bound=None)
        if review[2].decision=='ACCEPT':
            projection=a.build_root_decision_candidate_projection_v01(candidate_kind='PACKET_AUTHORIZATION',projected_candidate_id=canonical.authorization_candidate.root_packet_authorization_candidate_id,
                root_decision_kernel=review[0],root_decision_input=review[1],root_decision_result=review[2])
            bound=a.build_native_root_bound_action_commit_packet_v01(canonical_projection=canonical,root_decision_projection=projection)
            if not install:
                prepared.update(bound=bound,review_only=True)
                self.results.append(prepared)
                return prepared
            observation=a.build_action_dependency_current_observation_v01(dependency_id=dep,evidence_ref=ref,observed_content_sha256=digest,time_envelope_id=time_id,
                freshness_policy_id='supplier:current',source_provenance_refs=provenance,valid_from_utc=self.now,valid_to_utc=expires,observed_at_utc=self.now+4,observation_context_id='supplier:dispatch')
            self.source.install(observation)
            if self.episode is not None:
                if self.episode.startswith('g36:live:'):
                    time.sleep(max(0,self.now+4-time.time()))
                self.source.snapshot=replace(self.source.snapshot,evaluation_time=self.now+4)
            clock=self.source.snapshot
            prepared['bound']=bound
            try:
                h.install_current_action_v01(self.host,root_bound=bound,admission_id=admitted.admission_id,inputs=inputs,**pending_material_v01(bound),
                    expected_revision=self.host.revision,evaluation_time=clock.evaluation_time,evaluation_time_source=clock.evaluation_time_source,evaluation_context_id=clock.evaluation_context_id)
            except ValueError as error:
                if self.episode is None or str(error)!='consumed_key_permanently_closed':raise
                prepared['install_refusal']=str(error)
        self.results.append(prepared);return prepared

    def observe_current_v01(self, now):
        """Explicit trusted time observation; never extends old packet authority."""
        f._require(type(now) is int and now>=self.source.snapshot.evaluation_time,'g36_clock_rollback')
        self.now=now
        self.source.snapshot=replace(self.source.snapshot,evaluation_time=now,source_revision=self.source.snapshot.source_revision+1)
        clock=self.source.snapshot
        bound=next((p['bound'] for p in reversed(self.results) if p['bound'] is not None and not p.get('install_refusal') and not p.get('review_only')),None)
        if bound is not None:
            return h.inspect_current_action_v01(self.host,packet_id=bound.packet_identity.packet_id,expected_revision=self.host.revision,
                evaluation_time=clock.evaluation_time,evaluation_time_source=clock.evaluation_time_source,evaluation_context_id=clock.evaluation_context_id)

    def dispatch_v01(self,prepared):
        f._require(prepared in self.results and prepared['bound'] is not None and not prepared.get('review_only'),'g35_supplier_not_authorized')
        clock=self.source.snapshot;packet=prepared['bound'].packet_identity.packet_id
        h.dispatch_current_action_v01(self.host,packet_id=packet,task_id='supplier:gate3',expected_revision=self.host.revision,
            evaluation_time=clock.evaluation_time,evaluation_time_source=clock.evaluation_time_source,evaluation_context_id=clock.evaluation_context_id)
        context=self.host.registry.action_packet_fulfillment_attempt_contexts[-1]
        f._require(context.receipt is not None,'g35_supplier_receipt')
        self.host.observe_receipt(packet_id=packet,attempt_evidence_id=context.attempt_evidence.attempt_evidence_id,expected_revision=self.host.revision,
            evaluation_time=clock.evaluation_time+1,evaluation_time_source=clock.evaluation_time_source)
        return abi.kernel_artifact_to_plain_dict_v01(context.receipt)
