"""Controlled native-action slice using public producers and real Root review."""
from dataclasses import dataclass, replace, fields, is_dataclass
from collections.abc import Mapping
import json
import math
from hedgehog import action_commit_packet_v02 as acp
from hedgehog.kernel import root_decision_v01 as root_decision
from hedgehog.kernel import semantic_work_v01 as semantic_work
from hedgehog.kernel import trust_model_v01 as trust_model
from hedgehog.kernel import transition_registry_v01 as transition_registry
from hedgehog.kernel import effect_firewall_v01 as firewall
from hedgehog.kernel import abi_v01 as abi
from demo import work_composition_mock_capabilities_v01 as mocks
from hedgehog.kernel import work_composition_v01 as work
from hedgehog import work_execution_host_v01 as hosts


@dataclass(frozen=True)
class ActionPortabilityCaseV01:
    name: str
    prepared: 'PreparedNativeActionV01'
    consumed_registry: acp.ActionCommitPacketRegistryV02
    receipt_registry: acp.ActionCommitPacketRegistryV02
    replay: acp.ActionPacketLifecycleReplayReportV01
    host_events: tuple
    observed_mock_calls: tuple


@dataclass(frozen=True)
class ActionPortabilityReportV01:
    cases: tuple[ActionPortabilityCaseV01, ...]


def collect_action_packet_portability_v01():
    prepared = (
        ('PLAYBACK_ALPHA', prepare_native_playback_v01(content_ref='content:u1:alpha')),
        ('PLAYBACK_BETA', prepare_native_playback_v01(content_ref='content:u1:beta')),
        ('LEGACY_PAYMENT', authorize_and_prepare_action_v01(build_legacy_payment_candidate_v01())),
        ('NATIVE_PAYMENT', authorize_and_prepare_action_v01(*build_native_payment_candidate_v01())))
    cases = []
    for name, value in prepared:
        start = len(mocks.observed_mock_calls_v01())
        host, consumed = dispatch_prepared_action_v01(value)
        context = consumed.action_packet_fulfillment_attempt_contexts[-1]
        received = host.observe_receipt(packet_id=value.root_bound.packet_identity.packet_id,
            attempt_evidence_id=context.attempt_evidence.attempt_evidence_id,
            expected_revision=host.revision, evaluation_time=value.root_bound.canonical_projection.evaluation_time + 5,
            evaluation_time_source='u1.controlled_utc')
        replay = host.replay(packet_id=value.root_bound.packet_identity.packet_id)
        cases.append(ActionPortabilityCaseV01(name, value, consumed, received, replay,
            host.events, mocks.observed_mock_calls_v01()[start:]))
    report = ActionPortabilityReportV01(tuple(cases))
    valid, reasons = validate_action_packet_portability_report_v01(report)
    if not valid:
        raise ValueError(reasons[0])
    return report


def validate_action_packet_portability_report_v01(report):
    """Check the supplied typed histories; never recollect or run business code."""
    def require(condition, reason):
        if not condition:
            raise ValueError(reason)
    try:
        require(type(report) is ActionPortabilityReportV01 and type(report.cases) is tuple,
            'portability_report_type')
        require(tuple(c.name for c in report.cases) == ('PLAYBACK_ALPHA', 'PLAYBACK_BETA', 'LEGACY_PAYMENT', 'NATIVE_PAYMENT'),
            'portability_case_set')
        outputs = []
        keys = {}
        for case in report.cases:
            require(type(case) is ActionPortabilityCaseV01 and type(case.prepared) is PreparedNativeActionV01,
                'portability_case_type')
            p = case.prepared
            view = acp.common_action_view_v01(p.root_bound)
            c = view.canonical_projection
            packet_id = view.packet_identity.packet_id
            for registry in (p.registry, case.consumed_registry, case.receipt_registry):
                valid, reasons = acp.validate_action_commit_packet_registry_v02(registry)
                require(valid, 'portability_registry:' + repr(reasons))
                require(len(registry.action_packet_lifecycle_entries) == 1 and
                    registry.action_packet_lifecycle_entries[0].root_bound_genesis is p.root_bound,
                    'portability_root_bound_alias')
            before = p.registry.action_packet_lifecycle_entries[0]
            consumed = case.consumed_registry.action_packet_lifecycle_entries[0]
            received = case.receipt_registry.action_packet_lifecycle_entries[0]
            require(consumed.transition_events[:-1] == before.transition_events and
                received.transition_events[:-1] == consumed.transition_events, 'portability_history_prefix')
            require(len(case.consumed_registry.action_packet_fulfillment_attempt_contexts) == 1 and
                case.receipt_registry.action_packet_fulfillment_attempt_contexts == case.consumed_registry.action_packet_fulfillment_attempt_contexts,
                'portability_attempt_set')
            context = case.consumed_registry.action_packet_fulfillment_attempt_contexts[0]
            require(context.corridor == p.corridor and context.corridor_step == p.corridor_step and
                context.current_dependency_observations == p.observations and context.logical_time_bridge == p.bridge,
                'portability_supplied_context')
            require(context.attempt_evidence.outcome_class == 'CONSUMED' and context.attempt_evidence.adapter_call_count == 1,
                'portability_consumption')
            native = type(c) is acp.NativeActionCommitPacketV01
            require(type(case.host_events) is tuple and len(case.host_events) == (3 if native else 2) and
                case.host_events[0][:3] == ('DISPATCH_REQUESTED', 0, packet_id) and
                case.host_events[-1] == ('DISPATCH_OUTCOME', 1, packet_id, context.attempt_evidence.outcome_class,
                    context.attempt_evidence.reason_code, context.attempt_evidence.adapter_call_count), 'portability_host_sequence')
            receipt = abi.kernel_artifact_to_plain_dict_v01(context.receipt)
            payload = receipt['payload']
            require(payload['real_world_effects_count'] == 0 and type(payload['real_world_effects_count']) is int,
                'portability_real_effect')
            for name in ('future_permission_created', 'root_decision_created', 'final_output_created', 'effect_handle_exposed'):
                require(payload[name] is False, 'portability_non_authority:' + name)
            require(acp.validate_action_packet_lifecycle_replay_report_v01(case.replay, case.receipt_registry, packet_id=packet_id)[0],
                'portability_replay_binding')
            require(case.replay.reconstructed_state.lifecycle_state == 'RECEIPT_RECEIVED' and
                case.replay.reconstructed_state.idempotency_disposition == 'CONSUMED' and
                not case.replay.reconstructed_state.executable and case.replay.adapter_calls == 0 and
                not case.replay.creates_permission and not case.replay.creates_authority, 'portability_history_not_permission')
            if type(c) is acp.NativeActionCommitPacketV01:
                evidence = firewall.native_execution_evidence_from_plain_data_v01(payload['execution_evidence'])
                require(case.host_events[1] == ('EXECUTOR_STARTED', 0, packet_id, evidence.invocation.invocation_id),
                    'portability_actual_host_start')
                require(len(payload) == 21 and firewall.snapshot_admitted_capability_v01(p.admitted) == evidence.admission,
                    'portability_admission')
                require(evidence.invocation.inputs == p.inputs and evidence.invocation.task_id == case.host_events[0][3] and
                    evidence.invocation.packet_id == packet_id and evidence.invocation.execution_attempt_id == context.attempt_evidence.execution_attempt_id,
                    'portability_invocation')
                require(not firewall.validate_bound_capability_invocation_v01(evidence.invocation, evidence.admission, c),
                    'portability_input_business')
                calls = case.observed_mock_calls
                require(type(calls) is tuple and calls == (
                    ('INPUT_VALIDATOR', p.admitted.definition.definition_id, p.inputs),
                    ('INPUT_VALIDATOR', p.admitted.definition.definition_id, p.inputs),
                    ('EXECUTOR_STARTED', evidence.invocation.invocation_id, p.inputs),
                    ('OUTPUT_VALIDATOR', evidence.invocation.invocation_id, evidence.result.output)), 'portability_observed_calls')
                if case.name.startswith('PLAYBACK_'):
                    output = {row.parameter_name: row.value for row in evidence.result.output}
                    inputs = {row.parameter_name: row.value for row in p.inputs}
                    require(output['content_ref'] == inputs['content_ref'] and output['device_ref'] == inputs['device_ref'] and
                        output['playback_state'] == 'playing:' + inputs['content_ref'] + '@' + inputs['device_ref'],
                        'portability_actual_playback_output')
                    outputs.append(output)
            else:
                require(case.name == 'LEGACY_PAYMENT' and len(payload) == 19 and p.admitted is None and p.inputs is None
                    and case.observed_mock_calls == (), 'portability_legacy_encoding')
            if case.name.endswith('PAYMENT'):
                keys[case.name] = c.idempotency_identity
        require(len(outputs) == 2 and outputs[0] != outputs[1], 'portability_two_inputs')
        require(keys['LEGACY_PAYMENT'] == keys['NATIVE_PAYMENT'], 'portability_common_business_key')
        return True, ()
    except (ValueError, TypeError, KeyError, AttributeError, IndexError) as exc:
        return False, (str(exc) if type(exc) is ValueError else 'portability_report_shape',)


def action_packet_portability_report_to_plain_data_v01(report):
    valid, reasons = validate_action_packet_portability_report_v01(report)
    if not valid:
        raise ValueError(reasons[0])
    def plain(value):
        if value is None or type(value) in (str, int, bool):
            return value
        if type(value) is abi.KernelArtifactV01:
            return abi.kernel_artifact_to_plain_dict_v01(value)
        if type(value) is firewall.AdmittedCapabilityV01:
            return plain(firewall.snapshot_admitted_capability_v01(value))
        if isinstance(value, Mapping):
            return {key: plain(value[key]) for key in sorted(value)}
        if type(value) is tuple:
            return [plain(v) for v in value]
        if is_dataclass(value) and not isinstance(value, type):
            return {'public_type': type(value).__module__ + '.' + type(value).__name__,
                'fields': {f.name: plain(getattr(value, f.name)) for f in fields(value)}}
        raise ValueError('portability_export_type')
    return plain(report)


def render_action_packet_portability_v01(report):
    return json.dumps(action_packet_portability_report_to_plain_data_v01(report), sort_keys=True,
        separators=(',', ':'), ensure_ascii=True) + '\n'


def main():
    import sys
    sys.stdout.write(render_action_packet_portability_v01(collect_action_packet_portability_v01()))


@dataclass(frozen=True)
class PreparedNativeActionV01:
    root_bound: acp.NativeRootBoundActionCommitPacketV01 | acp.SupplierRootBoundActionCommitPacketV02ProjectionV01
    registry: acp.ActionCommitPacketRegistryV02
    corridor: acp.CommonContractFulfillmentCorridorV01 | acp.ContractFulfillmentCorridorV01
    corridor_step: acp.CommonCorridorStepV01 | acp.CorridorStepV01
    observations: tuple[acp.ActionDependencyCurrentObservationV01, ...]
    bridge: acp.LogicalTimeBridgeV01
    admitted: firewall.AdmittedCapabilityV01 | None
    inputs: tuple[acp.ActionEffectParameterRecordV01, ...] | None


def build_native_playback_candidate_v01(device_ref='device:u1:one', content_ref='content:u1:alpha'):
    admitted = mocks.admit_playback_v01(device_ref, 'host:u1:playback')
    definition = admitted.definition
    semantics = definition.business_semantics
    inputs = tuple(acp.build_action_effect_parameter_record_v01(parameter_name=n, value_type='REFERENCE', value=v)
        for n, v in (('content_ref', content_ref), ('device_ref', device_ref)))
    root_id = 'root:u1:playback'
    temporal = acp.build_action_temporal_authority_profile_v01(issued_at_utc=1000,
        expires_at_utc=4600, ttl_seconds=3600, temporal_policy_version='u1.logical_utc.v01')
    source_hash = acp.domain_separated_sha256_hex_v01(domain='demo.u1.dependency.v01',
        payload=acp.canonical_material_bytes_v01((('device_ref', device_ref), ('availability', 'CONTROLLED_MOCK_AVAILABLE'))))
    envelope = acp.build_action_dependency_time_envelope_id_v01(dependency_id='dependency:u1:device',
        evidence_ref='evidence:u1:availability', content_sha256=source_hash, freshness_policy_id='freshness:u1:session',
        source_provenance_refs=('source:u1:controlled_mock',), valid_from_utc=1000, valid_to_utc=4600)
    dependency = acp.build_dependency_set_candidate_v01(dependency_records=(
        acp.build_dependency_set_candidate_record_v01(dependency_id='dependency:u1:device',
            dependency_class='CONTROLLED_MOCK_AVAILABILITY', evidence_ref='evidence:u1:availability',
            content_sha256=source_hash, requirement_class='MANDATORY', time_envelope_id=envelope,
            freshness_policy_id='freshness:u1:session', source_provenance_refs=('source:u1:controlled_mock',),
            expected_accepting_local_root_id=root_id),))
    policy = acp.build_action_authority_policy_profile_v01(policy_version='u1.controlled_mock.v01',
        owning_local_root_id=root_id, authority_rule_refs=('authority:u1:root_only',),
        kill_switch_condition_refs=('kill_switch:u1:root_revocation',), retry_policy='NON_CONSUMING_RETRY',
        supersession_policy='ROOT_DECISION_ONLY', logical_effect_namespace=semantics.logical_effect_namespace,
        allowed_logical_effect_classes=(semantics.logical_effect_class,),
        allowed_business_object_namespaces=(semantics.business_object_namespace,), allowed_corridor_classes=('u1.mock',))
    canonical = acp.build_native_action_commit_packet_v01(transaction_id='transaction:u1:playback',
        owning_local_root_id=root_id, canonical_permission_ref='permission:u1:mock_playback',
        selected_canonical_action=semantics.selected_action_class,
        normalized_subject_scope=acp.build_action_subject_scope_profile_v01(included_subject_refs=('subject:u1:owner',), excluded_subject_refs=()),
        normalized_target_scope=acp.build_action_target_scope_profile_v01(included_target_refs=(device_ref,), excluded_target_refs=()),
        normalized_permission_scope=acp.build_action_permission_scope_profile_v01(
            allowed_action_classes=(semantics.selected_action_class,), forbidden_action_classes=(),
            allowed_adapter_ids=('mock_adapter:playback',), forbidden_adapter_ids=(),
            required_approval_refs=('permission:u1:mock_playback',), prohibited_effect_classes=()),
        adapter_binding=acp.build_action_adapter_binding_profile_v01(corridor_class='u1.mock',
            adapter_id='mock_adapter:playback', adapter_kind='DETERMINISTIC_MOCK', adapter_version='v0.1'),
        dependency_candidate=dependency, temporal_authority=temporal, authority_policy=policy,
        business_object_identity=acp.build_action_business_object_identity_profile_v01(
            business_object_class=semantics.business_object_class, business_object_namespace=semantics.business_object_namespace,
            business_object_ref=content_ref, owning_effect_root_id=root_id),
        consequential_effect_parameters=acp.build_action_consequential_effect_parameters_profile_v01(
            amount_decimal=None, currency_code=None, quantity_decimal=None, parameter_records=(inputs[1],)),
        evaluation_time=1010, evaluation_time_source='u1.controlled_utc', evaluation_context_id='context:u1:canonical',
        admitted_capability=admitted, inputs=inputs)
    return canonical, admitted, inputs


def prepare_native_playback_v01(device_ref='device:u1:one', content_ref='content:u1:alpha'):
    canonical, admitted, inputs = build_native_playback_candidate_v01(device_ref, content_ref)
    return authorize_and_prepare_action_v01(canonical, admitted, inputs)


def build_work_dependency_v01(device_ref, root_id):
    temporal = acp.build_action_temporal_authority_profile_v01(issued_at_utc=1000, expires_at_utc=4600,
        ttl_seconds=3600, temporal_policy_version='u1.logical_utc.v01')
    dependency_id = 'dependency:' + device_ref
    sha = acp.domain_separated_sha256_hex_v01(domain='demo.u1.work_availability.v01',
        payload=acp.canonical_material_bytes_v01((('device_ref', device_ref), ('availability', 'MOCK_AVAILABLE'))))
    envelope = acp.build_action_dependency_time_envelope_id_v01(dependency_id=dependency_id,
        evidence_ref='evidence:' + device_ref, content_sha256=sha, freshness_policy_id='freshness:u1:session',
        source_provenance_refs=('source:u1:controlled_mock',), valid_from_utc=1000, valid_to_utc=4600)
    dependency = acp.build_dependency_set_candidate_v01(dependency_records=(
        acp.build_dependency_set_candidate_record_v01(dependency_id=dependency_id,
            dependency_class='CONTROLLED_MOCK_AVAILABILITY', evidence_ref='evidence:' + device_ref,
            content_sha256=sha, requirement_class='MANDATORY', time_envelope_id=envelope,
            freshness_policy_id='freshness:u1:session', source_provenance_refs=('source:u1:controlled_mock',),
            expected_accepting_local_root_id=root_id),))
    observation = acp.build_action_dependency_current_observation_v01(dependency_id=dependency_id,
        evidence_ref='evidence:' + device_ref, observed_content_sha256=sha, time_envelope_id=envelope,
        freshness_policy_id='freshness:u1:session', source_provenance_refs=('source:u1:controlled_mock',),
        valid_from_utc=1000, valid_to_utc=4600, observed_at_utc=1014, observation_context_id='context:u1:dispatch')
    return dependency, temporal, observation


def build_native_work_action_v01(*, admitted, inputs, root_id, transaction_id, business_object_ref):
    """Build only after inputs were resolved; capability semantics own the mapping."""
    definition = admitted.definition
    semantics = definition.business_semantics
    actual = {r.parameter_name: r for r in inputs}
    device_ref = actual['device_ref'].value
    dependency, temporal, _ = build_work_dependency_v01(device_ref, root_id)
    records = tuple(actual[b.input_name] for b in semantics.input_bindings
        if b.source_kind in ('RECORD', 'SUBJECT_RECORD', 'TARGET_RECORD'))
    policy = acp.build_action_authority_policy_profile_v01(policy_version='u1.controlled_mock.v01',
        owning_local_root_id=root_id, authority_rule_refs=('authority:u1:root_only',),
        kill_switch_condition_refs=('kill_switch:u1:root_revocation',), retry_policy='NON_CONSUMING_RETRY',
        supersession_policy='ROOT_DECISION_ONLY', logical_effect_namespace=semantics.logical_effect_namespace,
        allowed_logical_effect_classes=(semantics.logical_effect_class,),
        allowed_business_object_namespaces=(semantics.business_object_namespace,), allowed_corridor_classes=('u1.mock',))
    return acp.build_native_action_commit_packet_v01(transaction_id=transaction_id, owning_local_root_id=root_id,
        canonical_permission_ref='permission:' + root_id + ':' + device_ref, selected_canonical_action=semantics.selected_action_class,
        normalized_subject_scope=acp.build_action_subject_scope_profile_v01(included_subject_refs=('subject:u1:owner',), excluded_subject_refs=()),
        normalized_target_scope=acp.build_action_target_scope_profile_v01(included_target_refs=(device_ref,), excluded_target_refs=()),
        normalized_permission_scope=acp.build_action_permission_scope_profile_v01(
            allowed_action_classes=(semantics.selected_action_class,), forbidden_action_classes=(),
            allowed_adapter_ids=('mock_adapter:work',), forbidden_adapter_ids=(),
            required_approval_refs=('permission:' + root_id + ':' + device_ref,), prohibited_effect_classes=()),
        adapter_binding=acp.build_action_adapter_binding_profile_v01(corridor_class='u1.mock',
            adapter_id='mock_adapter:work', adapter_kind='DETERMINISTIC_MOCK', adapter_version='v01'),
        dependency_candidate=dependency, temporal_authority=temporal, authority_policy=policy,
        business_object_identity=acp.build_action_business_object_identity_profile_v01(
            business_object_class=semantics.business_object_class, business_object_namespace=semantics.business_object_namespace,
            business_object_ref=business_object_ref, owning_effect_root_id=root_id),
        consequential_effect_parameters=acp.build_action_consequential_effect_parameters_profile_v01(
            amount_decimal=None, currency_code=None, quantity_decimal=None, parameter_records=records),
        evaluation_time=1010, evaluation_time_source='u1.controlled_utc', evaluation_context_id='context:u1:canonical',
        admitted_capability=admitted, inputs=inputs)


def authorize_resolved_work_v01(candidate, item, inputs, admitted):
    values = {v.parameter_name: v.value for v in inputs}
    canonical = build_native_work_action_v01(admitted=admitted, inputs=inputs, root_id=item.owning_root_id,
        transaction_id='transaction:' + candidate.task_id, business_object_ref=values.get('content_ref', 'signal:' + item.work_id))
    prepared = authorize_and_prepare_action_v01(canonical, admitted, inputs)
    return dict(root_bound=prepared.root_bound, corridor=prepared.corridor, corridor_step=prepared.corridor_step,
        transition_events=prepared.registry.action_packet_lifecycle_entries[0].transition_events,
        disposition_event=prepared.registry.idempotency_disposition_events[0])


def work_literal_v01(name, value_type, value):
    return work.WorkInputBindingV01(name, work.WorkLiteralV01(acp.build_action_effect_parameter_record_v01(
        parameter_name=name, value_type=value_type, value=value)))


def prepare_work_program_v01(*, task_id, root_id, admitted, items, device_refs):
    context = mocks.build_work_source_context_v01(task_id)
    semantic = abi.build_kernel_artifact_v01(abi_version='v1.0', artifact_id='semantic:' + task_id,
        artifact_type='SemanticArchitectProposal', schema_version='v1', transaction_id='transaction:' + task_id,
        owner_root_id=root_id, source_component='semantic_architect', authority_class='ADVISORY', lifecycle_state='PROPOSED',
        payload={'bounded_work_ids': [i.work_id for i in items], 'provenance': 'CONTROLLED_OFFLINE_PROPOSAL'},
        trace_refs=('intent:' + task_id,), parent_refs=(context.bsep_packet['packet_id'],),
        time_envelope={'pt_created_at': '2026-01-01T00:00:00+00:00', 'kt_asof': '2026-01-01T00:00:00+00:00',
            'et_observed_at': None, 'ct_session_anchor': 'session:' + task_id, 'ttl_seconds': 3600,
            'freshness_class': 'static', 'valid_from': '2026-01-01T00:00:00+00:00', 'valid_to': '2026-01-01T01:00:00+00:00'})
    common = dict(catalogue=admitted, source_context=context, semantic_proposal=semantic)
    candidate = work.build_work_program_candidate_v01(task_id=task_id, previous_revision_id=None,
        intent_ref='intent:' + task_id, bsep_ref=context.bsep_packet['packet_id'], semantic_proposal_ref=semantic.artifact_id,
        catalogue_revision=0, budget=work.WorkBudgetV01(16, 8, 0, 16, 0), items=items, trigger_evidence_refs=(), **common)
    program = work.materialize_work_program_v01(candidate, **common)
    observations = tuple(build_work_dependency_v01(d, root_id)[2] for d in device_refs)
    bridge = acp.build_logical_time_bridge_v01(origin_utc_epoch_seconds=1000, seconds_per_tick=1,
        bridge_policy_version='u1.controlled_ticks.v01')
    source = mocks.TrustedMockWorkSourceV01(observations, bridge, 1014, 'u1.controlled_utc', 'context:u1:dispatch')
    host = hosts.build_root_work_execution_host_v01(owning_root_id=root_id,
        registry=acp.build_empty_action_commit_packet_registry_v02(), catalogue=admitted, packet_bindings=(),
        current_dependency_observations=observations, logical_time_bridge=bridge, trusted_source=source)
    return program, common, host


def prepare_content_program_v01(content_ref='content:composition:actual', device_refs=('device:composition:one',), root_id='root:composition:display'):
    host_ref = 'host:' + root_id
    first = mocks.admit_pure_operation_v01(operation_id='u1.property', input_fields=(('property', 'REFERENCE'),),
        output_fields=(('content_ref', 'REFERENCE'),), executor=mocks.read_property_v01,
        output_validator=mocks.validate_property_output_v01, host_instance_ref=host_ref)
    second = mocks.admit_pure_operation_v01(operation_id='u1.transform', input_fields=(('content_ref', 'REFERENCE'),),
        output_fields=(('transformed_ref', 'REFERENCE'),), executor=mocks.transform_content_v01,
        output_validator=mocks.validate_transform_output_v01, host_instance_ref=host_ref)
    effects = tuple(mocks.admit_playback_v01(d, host_ref) for d in device_refs)
    items = (work.WorkItemV01('property', first.definition.definition_id, root_id,
        (work_literal_v01('property', 'REFERENCE', content_ref),), (), (), None, None),
        work.WorkItemV01('transform', second.definition.definition_id, root_id,
            (work.WorkInputBindingV01('content_ref', work.WorkOutputBindingV01('property', 'content_ref', 'REFERENCE')),),
            (), ('property',), None, None)) + tuple(work.WorkItemV01('display:' + d, a.definition.definition_id, root_id,
                (work.WorkInputBindingV01('content_ref', work.WorkOutputBindingV01('transform', 'transformed_ref', 'REFERENCE')),
                 work_literal_v01('device_ref', 'REFERENCE', d)), (d,), ('transform',), None, None) for d, a in zip(device_refs, effects))
    return prepare_work_program_v01(task_id='task:composition:content', root_id=root_id,
        admitted=(first, second) + effects, items=items, device_refs=device_refs)


def prepare_alarm_program_v01(reading=8, threshold=5, root_id='root:composition:alarm'):
    device = 'device:composition:alarm'
    host_ref = 'host:' + root_id
    observation = mocks.admit_pure_operation_v01(operation_id='u1.observation', input_fields=(('reading', 'INTEGER'),),
        output_fields=(('observed_level', 'INTEGER'),), executor=mocks.observe_level_v01,
        output_validator=mocks.validate_level_output_v01, host_instance_ref=host_ref)
    comparison = mocks.admit_pure_operation_v01(operation_id='u1.comparison', input_fields=(('level', 'INTEGER'), ('threshold', 'INTEGER')),
        output_fields=(('exceeds', 'BOOLEAN'),), executor=mocks.compare_level_v01,
        output_validator=mocks.validate_comparison_output_v01, host_instance_ref=host_ref)
    alarm = mocks.admit_alarm_v01(device, host_ref)
    guard = work.WorkOutputBindingV01('compare', 'exceeds', 'BOOLEAN')
    items = (work.WorkItemV01('observe', observation.definition.definition_id, root_id,
        (work_literal_v01('reading', 'INTEGER', reading),), (), (), None, None),
        work.WorkItemV01('compare', comparison.definition.definition_id, root_id,
            (work.WorkInputBindingV01('level', work.WorkOutputBindingV01('observe', 'observed_level', 'INTEGER')),
             work_literal_v01('threshold', 'INTEGER', threshold)), (), ('observe',), None, None),
        work.WorkItemV01('alarm', alarm.definition.definition_id, root_id,
            (work_literal_v01('device_ref', 'REFERENCE', device), work.WorkInputBindingV01('enabled', guard)),
            (device,), ('compare',), guard, None))
    return prepare_work_program_v01(task_id='task:composition:alarm', root_id=root_id,
        admitted=(observation, comparison, alarm), items=items, device_refs=(device,))


@dataclass(frozen=True)
class WorkCompositionEvidenceV01:
    program: work.MaterializedWorkProgramV01
    source_context: object
    semantic_proposal: abi.KernelArtifactV01
    host: hosts.RootWorkExecutionHostV01
    results: tuple[work.WorkItemResultV01, ...]
    proposal_artifact: abi.KernelArtifactV01
    result_artifact: abi.KernelArtifactV01


def collect_work_composition_evidence_v01():
    cases = []
    for prepare in (prepare_content_program_v01, prepare_alarm_program_v01):
        program, common, host = prepare()
        results = work.advance_work_program_v01(program, **common, host_map={host.owning_root_id: host},
            action_authorizers={host.owning_root_id: authorize_resolved_work_v01})
        proposal = work.work_program_candidate_to_artifact_v01(program.candidate, **common)
        result = work.work_program_result_to_artifact_v01(program, results, **common, host_map={host.owning_root_id: host})
        cases.append(WorkCompositionEvidenceV01(program, common['source_context'], common['semantic_proposal'],
            host, results, proposal, result))
    report = tuple(cases)
    if not validate_work_composition_evidence_v01(report):
        raise ValueError('composition_evidence_invalid')
    return report


def validate_work_composition_evidence_v01(report):
    try:
        if type(report) is not tuple or len(report) != 2 or any(type(c) is not WorkCompositionEvidenceV01 for c in report):
            return False
        definition_orders = []
        for case in report:
            host = case.host
            if type(host) is not hosts.RootWorkExecutionHostV01:
                return False
            common = dict(catalogue=host.admitted_catalogue, source_context=case.source_context,
                semantic_proposal=case.semantic_proposal)
            if not work.validate_work_program_result_v01(case.program, case.results, **common,
                host_map={host.owning_root_id: host})[0]:
                return False
            if tuple(r.work_id for r in case.results) != case.program.ordered_work_ids or any(r.status != 'COMPLETED' for r in case.results):
                return False
            if case.proposal_artifact != work.work_program_candidate_to_artifact_v01(case.program.candidate, **common):
                return False
            if case.result_artifact != work.work_program_result_to_artifact_v01(case.program, case.results, **common,
                host_map={host.owning_root_id: host}):
                return False
            if not acp.validate_action_commit_packet_registry_v02(host.registry)[0]:
                return False
            actions = tuple(r for r in case.results if r.invocation.packet_id is not None)
            contexts = host.registry.action_packet_fulfillment_attempt_contexts
            if len(contexts) != len(actions) or len(host.work_attempts) != len(case.results):
                return False
            for result, context in zip(actions, contexts, strict=True):
                payload = abi.kernel_artifact_to_plain_dict_v01(context.receipt)['payload']
                actual = firewall.native_execution_evidence_from_plain_data_v01(payload['execution_evidence'])
                if (actual.invocation, actual.result) != (result.invocation, result.result):
                    return False
                if payload['real_world_effects_count'] != 0 or any(payload[name] is not False for name in
                    ('future_permission_created', 'root_decision_created', 'final_output_created', 'effect_handle_exposed')):
                    return False
            definition_orders.append(tuple(i.definition_id for i in case.program.candidate.items))
        return definition_orders[0] != definition_orders[1]
    except (ValueError, KeyError, TypeError, AttributeError):
        return False


def work_composition_evidence_to_plain_data_v01(report):
    if not validate_work_composition_evidence_v01(report):
        raise ValueError('composition_evidence_invalid')
    def plain(value):
        if value is None or type(value) in (str, int, bool):
            return value
        if type(value) is float and math.isfinite(value):
            return value
        if type(value) is abi.KernelArtifactV01:
            return abi.kernel_artifact_to_plain_dict_v01(value)
        if isinstance(value, Mapping):
            return {key: plain(value[key]) for key in sorted(value)}
        if type(value) in (tuple, list):
            return [plain(v) for v in value]
        if is_dataclass(value) and not isinstance(value, type):
            return {f.name: plain(getattr(value, f.name)) for f in fields(value)}
        raise ValueError('composition_plain_type')
    return {'cases': [dict(program=plain(c.program), proposal=plain(c.proposal_artifact), result=plain(c.result_artifact),
        results=plain(c.results), semantic_source=plain(c.semantic_proposal), source_context=plain(c.source_context),
        admitted_sources=plain(tuple(firewall.snapshot_admitted_capability_v01(a) for a in c.host.admitted_catalogue)),
        registry=plain(c.host.registry), host_events=plain(c.host.events), attempts=plain(c.host.work_attempts)) for c in report],
        'provenance': 'CONTROLLED_OFFLINE_PROPOSALS_AND_LOCAL_MOCK_EXECUTION',
        'zero_effect_scope': 'Typed receipt checks; not independent operating-system monitoring.'}


def authorize_action_v01(canonical):
    kernel, decision_input, result = review_native_candidate_v01(canonical, canonical.business_object_identity.business_object_ref)
    root = acp.build_root_decision_candidate_projection_v01(
        candidate_kind=acp.ROOT_DECISION_CANDIDATE_KIND_PACKET_AUTHORIZATION_V01,
        projected_candidate_id=canonical.authorization_candidate.root_packet_authorization_candidate_id,
        root_decision_kernel=kernel, root_decision_input=decision_input, root_decision_result=result)
    bound = (acp.build_native_root_bound_action_commit_packet_v01(canonical_projection=canonical, root_decision_projection=root)
        if type(canonical) is acp.NativeActionCommitPacketV01 else
        acp.build_supplier_root_bound_action_commit_packet_v02_projection_v01(canonical_projection=canonical, root_decision_projection=root))
    return bound


def authorize_and_prepare_action_v01(canonical, admitted=None, inputs=None):
    bound = authorize_action_v01(canonical)
    result = bound.root_decision_projection.root_decision_result
    profile = transition_registry.build_action_packet_transition_registry_profile_v01()
    registry = acp.record_action_packet_genesis_v01(acp.build_empty_action_commit_packet_registry_v02(),
        root_bound_genesis=bound, action_packet_transition_registry_profile=profile)
    packet_id = bound.packet_identity.packet_id
    for rule_id in ('g2a_t01_activate_root_authorization', 'g2a_t02_queue', 'g2a_t03_pending'):
        entry = next(e for e in registry.action_packet_lifecycle_entries if e.root_bound_genesis.packet_identity.packet_id == packet_id)
        rule = transition_registry.lookup_action_packet_transition_rule_v01(registry=profile, transition_rule_id=rule_id)
        context = 'context:u1:' + rule_id
        attempt = acp.build_action_execution_attempt_identity_v01(packet_id=packet_id,
            idempotency_key=canonical.idempotency_identity.idempotency_key, attempt_ordinal=1,
            evaluation_context_id=context) if rule_id == 'g2a_t03_pending' else None
        bindings = tuple(acp.build_transition_evidence_binding_v01(action_packet_transition_registry_profile=profile,
            transition_rule_id=rule_id, evidence_code=code, evidence_ref='evidence:u1:' + code,
            evidence_sha256=acp.domain_separated_sha256_hex_v01(domain='demo.u1.transition_evidence.v01',
                payload=acp.canonical_material_bytes_v01((('packet_id', packet_id), ('root_decision_id', result.decision_id), ('evidence_code', code)))),
            validator_profile_id='validator:u1:public_lifecycle') for code in rule.required_evidence_codes)
        event = acp.build_action_packet_transition_event_v01(action_packet_transition_registry_profile=profile,
            transition_rule_id=rule_id, packet_id=packet_id, idempotency_key=canonical.idempotency_identity.idempotency_key,
            previous_transition_event_id=entry.transition_events[-1].transition_event_id if entry.transition_events else None,
            owning_local_root_id=canonical.owning_local_root_id,
            root_decision_ref=result.decision_id if rule_id == 'g2a_t01_activate_root_authorization' else None,
            transition_evidence_bindings=bindings, dependency_set_candidate_fingerprint=canonical.dependency_set_candidate_fingerprint,
            temporal_authority_fingerprint=canonical.temporal_authority_fingerprint, evaluation_time=canonical.evaluation_time+1+len(entry.transition_events),
            evaluation_time_source='u1.controlled_utc', evaluation_context_id=context,
            execution_attempt_identity=attempt, receipt_ref=None)
        if rule_id == 'g2a_t01_activate_root_authorization':
            reserve = acp.build_idempotency_disposition_event_v01(idempotency_key=canonical.idempotency_identity.idempotency_key,
                event_class='RESERVE', from_disposition='UNCLAIMED', to_disposition='RESERVED', from_owner_packet_id=None,
                to_owner_packet_id=packet_id, previous_disposition_event_id=None, cause_transition_event_ids=(event.transition_event_id,),
                root_decision_ref=result.decision_id, predecessor_packet_id=None, successor_packet_id=None,
                evidence_refs=tuple(sorted(b.transition_evidence_binding_id for b in bindings if b.evidence_code in
                    ('packet_genesis_valid', 'source_root_authorization_valid', 'idempotency_acquisition_valid'))),
                evaluation_time=event.evaluation_time, evaluation_time_source=event.evaluation_time_source,
                evaluation_context_id=event.evaluation_context_id)
            registry = acp.activate_action_packet_lifecycle_v01(registry, packet_id=packet_id,
                transition_event=event, disposition_event=reserve, action_packet_transition_registry_profile=profile)
        else:
            registry = acp.append_action_packet_lifecycle_transition_v01(registry, packet_id=packet_id,
                transition_event=event, action_packet_transition_registry_profile=profile)
    temporal = canonical.temporal_authority
    if type(canonical) is acp.NativeActionCommitPacketV01:
        step = acp.build_common_corridor_step_v01(transaction_id=canonical.transaction_id,
            owning_local_root_id=canonical.owning_local_root_id, packet_id=packet_id,
            authorization_candidate_id=canonical.authorization_candidate.root_packet_authorization_candidate_id,
            action_class=canonical.selected_canonical_action, adapter_binding=canonical.adapter_binding,
            subject_scope=canonical.normalized_subject_scope, target_scope=canonical.normalized_target_scope,
            effect_parameters=canonical.normalized_effect_parameters,
            issued_at_utc=temporal.issued_at_utc, expires_at_utc=temporal.expires_at_utc)
        corridor = acp.build_common_contract_fulfillment_corridor_v01(transaction_id=canonical.transaction_id,
            owning_local_root_id=canonical.owning_local_root_id, packet_id=packet_id,
            corridor_class=canonical.adapter_binding.corridor_class, steps=(step,))
    else:
        source = canonical.source_packet
        step = replace(acp.build_supplier_a_corridor_step_fixture_v01(source), parent_packet_id=packet_id,
            allowed_subjects=source.scope.allowed_subjects)
        corridor = acp.ContractFulfillmentCorridorV01(corridor_id='corridor:u1:legacy', packet_id=packet_id,
            corridor_kind=canonical.adapter_binding.corridor_class, allowed_steps=(step.step_id,))
    dep = canonical.dependency_candidate.dependency_records[0]
    observations = (acp.build_action_dependency_current_observation_v01(dependency_id=dep.dependency_id,
        evidence_ref=dep.evidence_ref, observed_content_sha256=dep.content_sha256, time_envelope_id=dep.time_envelope_id,
        freshness_policy_id=dep.freshness_policy_id, source_provenance_refs=dep.source_provenance_refs,
        valid_from_utc=temporal.issued_at_utc, valid_to_utc=temporal.expires_at_utc,
        observed_at_utc=canonical.evaluation_time+4, observation_context_id='context:u1:dispatch'),)
    bridge = acp.build_logical_time_bridge_v01(origin_utc_epoch_seconds=temporal.issued_at_utc, seconds_per_tick=1,
        bridge_policy_version='u1.controlled_ticks.v01')
    return PreparedNativeActionV01(bound, registry, corridor, step, observations, bridge, admitted, inputs)


def review_native_candidate_v01(
    canonical: acp.NativeActionCommitPacketV01,
    domain_shape: str,
    *, candidate_kind='PACKET_AUTHORIZATION', candidate_id=None, predecessor=None,
) -> tuple[
    root_decision.RootDecisionKernelV01,
    root_decision.RootDecisionInputV01,
    root_decision.RootDecisionResultV01,
]:
    candidate_id = candidate_id or (
        canonical.authorization_candidate
        .root_packet_authorization_candidate_id
    )
    context_ref = f"context:u1_native:{domain_shape.lower()}"
    actor_id = "runtime:u1_native_synthetic_authorization"
    request = semantic_work.build_semantic_work_request_v01(
        request_id=f"semantic_request:u1_native:{domain_shape.lower()}",
        transaction_id=canonical.transaction_id,
        target_root_id=canonical.owning_local_root_id,
        runtime_topology_ref="runtime_topology:u1_native_bounded_synthetic",
        bounded_context_refs=(context_ref,),
        permitted_actor_ids=(actor_id,),
        permitted_contribution_modes=("DETERMINISTIC",),
        requested_subjects=(
            f"action_commit_packet:{domain_shape.lower()}",
        ),
        required_evidence_classes=("DEPENDENCY_EVIDENCE",),
        forbidden_claims=("authority_creation",),
    )
    dependency = canonical.dependency_candidate.dependency_records[0]
    evidence = semantic_work.build_evidence_binding_v01(
        evidence_id=f"evidence_binding:u1_native:{domain_shape.lower()}",
        evidence_ref=dependency.evidence_ref,
        evidence_class="DEPENDENCY_EVIDENCE",
        source_component_id="deterministic_runtime",
        provenance_ref=dependency.source_provenance_refs[0],
        evidence_state="PRESENT",
    )
    claim = semantic_work.build_normalized_claim_v01(
        claim_id=candidate_id,
        subject=f"action_commit_packet:{domain_shape.lower()}",
        predicate={
            'PACKET_AUTHORIZATION': 'root_packet_authorization_candidate',
            'REVOCATION': acp.ROOT_DECISION_CLAIM_PREDICATE_REVOCATION_V01,
            'SUPERSESSION': acp.ROOT_DECISION_CLAIM_PREDICATE_SUPERSESSION_V01,
        }[candidate_kind],
        object_or_value={
            "candidate_id": candidate_id,
            "candidate_kind": candidate_kind,
        },
        time_envelope_ref=canonical.temporal_authority_fingerprint,
        provenance_refs=("provenance:u1_native_synthetic_authorization",),
        evidence_refs=(evidence.evidence_id,),
        confidence_micros=1_000_000,
        source_role="deterministic_runtime",
        source_mode="DETERMINISTIC",
    )
    contribution = semantic_work.build_actor_contribution_v01(
        contribution_id=f"contribution:u1_native:{domain_shape.lower()}",
        request_id=request.request_id,
        actor_id=actor_id,
        actor_role="deterministic_runtime",
        contribution_mode="DETERMINISTIC",
        bsep_projection_ref="bsep:u1_native_synthetic",
        scope="scope:u1_native_synthetic_authorization",
        bounded_context_refs=(context_ref,),
        claims=(claim,),
        evidence_bindings=(evidence,),
        constraint_bindings=(),
        uncertainty_bindings=(),
        requested_validators=("validator:u1_native_synthetic_authorization",),
        forbidden_claims_observed=(),
    )
    review = semantic_work.build_root_review_packet_from_contributions_v01(
        request=request,
        contributions=(contribution,),
        trust_profiles=(
            trust_model.build_default_component_trust_profiles_v01()
        ),
    )
    mandatory_refs = [
        record.evidence_ref
        for record in canonical.dependency_candidate.dependency_records
        if record.requirement_class == "MANDATORY"
    ]
    kernel = root_decision.build_root_decision_kernel_v01()
    decision_input = root_decision.build_root_decision_input_v01(
        transaction_id=canonical.transaction_id,
        target_root_id=canonical.owning_local_root_id,
        root_review_packet=review,
        post_vv_bundle={
            "bundle_id": "post_vv:u1_native_synthetic",
            "post_vv_passed": True,
            "validated_candidate_ids": [candidate_id],
            "rejected_candidate_ids": [],
            "required_evidence_refs": mandatory_refs,
            "provided_evidence_refs": mandatory_refs,
            "hard_failure_reasons": [],
        },
        gt_advisory={
            "advisory_id": "gt:u1_native_synthetic",
            "candidate_ids": [candidate_id],
            "selected_candidate_id": candidate_id,
            "score_micros_by_candidate": {candidate_id: 1_000_000},
            "source_artifact_type": "GTAdvisoryReport",
            "source_lifecycle_state": "VALIDATED",
            "actor_role": "gt",
            "attempted_effect": "CREATE_ROOT_DECISION",
            "target_artifact_type": "RootDecision",
            "advisory_only": True,
            "creates_final_output": False,
            "requests_effect": False,
        },
        policy_state={
            "policy_id": canonical.authority_policy_fingerprint,
            "identity_passed": True,
            "scope_passed": True,
            "hard_policy_passed": True,
            "allow_accept": True,
            "conflict_policy": "DEFER",
            "no_candidate_policy": "NO_UPDATE",
        },
        permission_state={
            "permission_required": candidate_kind == 'PACKET_AUTHORIZATION',
            "user_permission_present": candidate_kind == 'PACKET_AUTHORIZATION',
            "permission_scope_valid": True,
            "permission_ref": canonical.canonical_permission_ref if candidate_kind == 'PACKET_AUTHORIZATION' else None,
        },
        temporal_state={
            "temporal_valid": True,
            "expired": False,
            "not_before_satisfied": True,
            "time_envelope_ref": canonical.temporal_authority_fingerprint,
        },
        conflict_state={
            "material_unresolved_conflict": False,
            "conflict_set_ids": list(review.conflict_set_ids),
        },
        prior_root_state={
            "prior_decision_id": None if predecessor is None else predecessor.root_decision_projection.root_decision_result.decision_id,
            "prior_decision": None if predecessor is None else predecessor.root_decision_projection.root_decision_result.decision,
            "prior_selected_candidate_id": None if predecessor is None else predecessor.canonical_projection.authorization_candidate.root_packet_authorization_candidate_id,
        },
    )
    result = root_decision.decide_root_v01(
        kernel=kernel,
        decision_input=decision_input,
    )
    return kernel, decision_input, result


def build_legacy_payment_candidate_v01(*, predecessor_packet_id=None):
    source = acp.build_supplier_a_mock_action_commit_packet_fixture_v02()
    # Creditor account and subject are distinct scopes, as required by the
    # existing exclusive Firewall projection. This is a new controlled input.
    source = replace(source, scope=replace(source.scope, creditor_ref='creditor:u1:supplier_a'))
    now = 1783470600
    temporal = acp.project_packet_ttl_compatibility_v01(source.ttl, evaluation_time=now,
        temporal_policy_version='packet_ttl_v01').temporal_authority
    root_id = 'root:u1:payment'
    source_hash = acp.domain_separated_sha256_hex_v01(domain='demo.u1.payment_evidence.v01',
        payload=acp.canonical_material_bytes_v01((('creditor', source.scope.creditor_ref), ('slot', source.scope.payment_slot_ref))))
    envelope = acp.build_action_dependency_time_envelope_id_v01(dependency_id='dependency:u1:payment', evidence_ref='evidence:u1:payment',
        content_sha256=source_hash, freshness_policy_id='freshness:u1:payment', source_provenance_refs=('source:u1:mock_payment',),
        valid_from_utc=temporal.issued_at_utc, valid_to_utc=temporal.expires_at_utc)
    dependency = acp.build_dependency_set_candidate_v01(dependency_records=(acp.build_dependency_set_candidate_record_v01(
        dependency_id='dependency:u1:payment', dependency_class='CONTROLLED_MOCK_PAYMENT', evidence_ref='evidence:u1:payment',
        content_sha256=source_hash, requirement_class='MANDATORY', time_envelope_id=envelope, freshness_policy_id='freshness:u1:payment',
        source_provenance_refs=('source:u1:mock_payment',), expected_accepting_local_root_id=root_id),))
    policy = acp.build_action_authority_policy_profile_v01(policy_version='u1.mock_payment.v01', owning_local_root_id=root_id,
        authority_rule_refs=('authority:u1:root_only',), kill_switch_condition_refs=('kill_switch:u1:root_revocation',),
        retry_policy='NON_CONSUMING_RETRY', supersession_policy='ROOT_DECISION_ONLY', logical_effect_namespace='u1.payment.v01',
        allowed_logical_effect_classes=('PAYMENT',), allowed_business_object_namespaces=('u1.payment_slot.v01',),
        allowed_corridor_classes=('u1.mock_payment',))
    return acp.build_supplier_action_commit_packet_canonical_projection_v01(source, transaction_id='transaction:u1:payment',
        owning_local_root_id=root_id, canonical_permission_ref='permission:u1:mock_payment',
        selected_legacy_action=acp.ACTION_MOCK_SUPPLIER_A_PAYMENT_ORDER, logical_effect_namespace='u1.payment.v01',
        business_object_namespace='u1.payment_slot.v01', corridor_class='u1.mock_payment', adapter_version=acp.PRE_G2A_ADAPTER_VERSION_V01,
        temporal_policy_version='packet_ttl_v01', authority_policy=policy, dependency_candidate=dependency,
        evaluation_time=now, evaluation_time_source='u1.controlled_utc', evaluation_context_id='context:u1:payment_canonical',
        predecessor_packet_id=predecessor_packet_id, supersession_reason_class=None if predecessor_packet_id is None else 'ENCODING_SUCCESSOR')


def build_native_from_business_v01(canonical, admitted, inputs, *, predecessor_packet_id=None):
    return acp.build_native_action_commit_packet_v01(transaction_id=canonical.transaction_id, owning_local_root_id=canonical.owning_local_root_id,
        canonical_permission_ref=canonical.canonical_permission_ref, selected_canonical_action=canonical.selected_canonical_action,
        normalized_subject_scope=canonical.normalized_subject_scope, normalized_target_scope=canonical.normalized_target_scope,
        normalized_permission_scope=canonical.normalized_permission_scope, adapter_binding=canonical.adapter_binding,
        dependency_candidate=canonical.dependency_candidate, temporal_authority=canonical.temporal_authority,
        authority_policy=canonical.authority_policy, business_object_identity=canonical.business_object_identity,
        consequential_effect_parameters=canonical.consequential_effect_parameters, evaluation_time=canonical.evaluation_time,
        evaluation_time_source=canonical.evaluation_time_source, evaluation_context_id=canonical.evaluation_context_id,
        admitted_capability=admitted, inputs=inputs, predecessor_packet_id=predecessor_packet_id,
        supersession_reason_class=None if predecessor_packet_id is None else 'CODE_OR_ENCODING_SUCCESSOR')


def build_native_payment_candidate_v01(*, executor=mocks.execute_payment_v01, predecessor_packet_id=None):
    legacy = build_legacy_payment_candidate_v01()
    admitted = mocks.admit_payment_v01(legacy, 'host:u1:payment', executor=executor)
    q = legacy.consequential_effect_parameters
    inputs = tuple(acp.build_action_effect_parameter_record_v01(parameter_name=n, value_type=k, value=v)
        for n, k, v in (('amount', 'DECIMAL', q.amount_decimal), ('currency', 'TEXT', q.currency_code),
            ('payment_slot_ref', 'REFERENCE', legacy.business_object_identity.business_object_ref)))
    return build_native_from_business_v01(legacy, admitted, inputs, predecessor_packet_id=predecessor_packet_id), admitted, inputs


def host_for_prepared_action_v01(prepared, trusted_source=None):
    from hedgehog.work_execution_host_v01 import build_root_work_execution_host_v01
    p = prepared
    if trusted_source is None:
        trusted_source = mocks.TrustedMockWorkSourceV01(p.observations, p.bridge,
            p.root_bound.canonical_projection.evaluation_time + 4, 'u1.controlled_utc', 'context:u1:dispatch')
    return build_root_work_execution_host_v01(owning_root_id=p.root_bound.canonical_projection.owning_local_root_id, registry=p.registry,
        catalogue=() if p.admitted is None else (p.admitted,), packet_bindings=((p.root_bound.packet_identity.packet_id,
            p.corridor, p.corridor_step, None if p.admitted is None else p.admitted.admission_id, p.inputs),),
        current_dependency_observations=p.observations, logical_time_bridge=p.bridge, trusted_source=trusted_source)


def dispatch_prepared_action_v01(prepared, host=None):
    from hedgehog.work_execution_host_v01 import dispatch_current_action_v01
    if host is None:
        host = host_for_prepared_action_v01(prepared)
    p = prepared
    result, revision = dispatch_current_action_v01(host, packet_id=p.root_bound.packet_identity.packet_id, task_id='task:u1:controlled_dispatch',
        expected_revision=host.revision, evaluation_time=p.root_bound.canonical_projection.evaluation_time+4,
        evaluation_time_source='u1.controlled_utc', evaluation_context_id='context:u1:dispatch')
    if revision != host.state_revision or result is not host.registry:
        raise ValueError('public_host_update_revision_binding')
    return host, result


def build_prestart_root_revocation_v01(prepared):
    p = prepared
    bound = p.root_bound
    canonical = bound.canonical_projection
    packet_id = bound.packet_identity.packet_id
    now = canonical.evaluation_time + 4
    candidate = acp.build_revocation_candidate_v01(owning_local_root_id=canonical.owning_local_root_id,
        packet_id=packet_id, source_authorization_decision_id=bound.root_decision_projection.root_decision_result.decision_id,
        idempotency_key=canonical.idempotency_identity.idempotency_key, revocation_reason_class='CONTROLLED_ROOT_REVOCATION',
        evidence_refs=('evidence:u1:owner_revocation',),
        evidence_hashes=(acp.domain_separated_sha256_hex_v01(domain='demo.u1.revocation_request.v01',
            payload=acp.canonical_material_bytes_v01((('packet_id', packet_id), ('requested_at', now)))),),
        evaluation_time=now, policy_fingerprint=canonical.authority_policy_fingerprint)
    kernel, decision_input, result = review_native_candidate_v01(canonical, 'revocation', candidate_kind='REVOCATION',
        candidate_id=candidate.revocation_candidate_id, predecessor=bound)
    root = acp.build_root_decision_candidate_projection_v01(candidate_kind='REVOCATION',
        projected_candidate_id=candidate.revocation_candidate_id, root_decision_kernel=kernel,
        root_decision_input=decision_input, root_decision_result=result)
    accepted = acp.build_accepted_revocation_binding_v01(candidate=candidate, root_projection=root, packet=bound)
    dep = canonical.dependency_candidate.dependency_records[0]
    invalidation = acp.build_action_invalidation_evidence_v01(source_invalidation_event_ref='source:u1:accepted_root_revocation',
        packet_id=packet_id, dependency_id='dependency:u1:root_revocation', invalidation_class='ROOT_REVOCATION',
        evidence_ref=accepted.accepted_revocation_binding_id,
        evidence_sha256=accepted.accepted_revocation_binding_id.split(':', 1)[1], observed_status='OBSERVED_ROOT_REVOCATION',
        time_envelope_id=dep.time_envelope_id, freshness_policy_id=dep.freshness_policy_id,
        owning_local_root_id=canonical.owning_local_root_id, accepted_by_local_root_id=canonical.owning_local_root_id,
        acceptance_root_decision_id=accepted.revocation_root_decision_id,
        acceptance_root_decision_hash=accepted.revocation_root_decision_hash, authority_effect='ROOT_REVOCATION',
        root_decision_ref=accepted.revocation_root_decision_id, evaluation_time=now,
        evaluation_time_source='u1.controlled_utc', evaluation_context_id='context:u1:root_revocation')
    profile = transition_registry.build_action_packet_transition_registry_profile_v01()
    rule_id = 'g2a_t18_pending_revoke'
    rule = transition_registry.lookup_action_packet_transition_rule_v01(registry=profile, transition_rule_id=rule_id)
    entry = next(e for e in p.registry.action_packet_lifecycle_entries if e.root_bound_genesis.packet_identity.packet_id == packet_id)
    state = acp.derive_action_packet_lifecycle_state_v01(p.registry, packet_id=packet_id)
    latest = entry.transition_events[-1]
    materials = {
        'blocking_evidence_valid': (invalidation.invalidation_evidence_id, invalidation.invalidation_evidence_id, acp.ACTION_INVALIDATION_EVIDENCE_PROFILE_ID_V01),
        'accepted_revocation_binding_valid': (accepted.accepted_revocation_binding_id, accepted.accepted_revocation_binding_id.split(':', 1)[1], 'accepted_revocation_binding_v01'),
        'source_authorization_binding_valid': (bound.root_decision_projection.root_decision_result.decision_id, bound.root_decision_projection.source_root_decision_hash, 'root_decision_result_v01'),
        'packet_genesis_valid': (packet_id, packet_id.split(':', 1)[1], 'action_commit_packet_identity_profile_v01'),
        'authority_policy_valid': (canonical.authority_policy_fingerprint, canonical.authority_policy_fingerprint, acp.ACTION_AUTHORITY_POLICY_PROFILE_ID_V01),
        'idempotency_reservation_owned': (state.latest_disposition_event_id, state.latest_disposition_event_id.split(':', 1)[1], acp.IDEMPOTENCY_DISPOSITION_EVENT_PROFILE_ID_V01),
        'adapter_not_called': (latest.execution_attempt_id, latest.execution_attempt_id.split(':', 1)[1], acp.EXECUTION_ATTEMPT_IDENTITY_PROFILE_ID_V01),
    }
    bindings = tuple(acp.build_transition_evidence_binding_v01(action_packet_transition_registry_profile=profile,
        transition_rule_id=rule_id, evidence_code=code, evidence_ref=materials[code][0], evidence_sha256=materials[code][1],
        validator_profile_id=materials[code][2]) for code in rule.required_evidence_codes)
    event = acp.build_action_packet_transition_event_v01(action_packet_transition_registry_profile=profile,
        transition_rule_id=rule_id, packet_id=packet_id, idempotency_key=canonical.idempotency_identity.idempotency_key,
        previous_transition_event_id=latest.transition_event_id, owning_local_root_id=canonical.owning_local_root_id,
        root_decision_ref=result.decision_id, transition_evidence_bindings=bindings,
        dependency_set_candidate_fingerprint=canonical.dependency_set_candidate_fingerprint,
        temporal_authority_fingerprint=canonical.temporal_authority_fingerprint, evaluation_time=now,
        evaluation_time_source=invalidation.evaluation_time_source, evaluation_context_id=invalidation.evaluation_context_id,
        execution_attempt_identity=None, receipt_ref=None)
    return dict(packet_id=packet_id, revocation_candidate=candidate, revocation_root_projection=root,
        accepted_revocation_binding=accepted, invalidation_evidence=invalidation, transition_event=event)


if __name__ == '__main__':
    main()
