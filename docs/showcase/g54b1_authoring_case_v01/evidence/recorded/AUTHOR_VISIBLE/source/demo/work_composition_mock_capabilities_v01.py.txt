"""Offline controlled capability definitions and real deterministic mock calls.

These callables produce domain values, not device or payment integrations.
"""
from hedgehog import action_commit_packet_v02 as action
from hedgehog.kernel import effect_firewall_v01 as firewall
from hedgehog import work_execution_host_v01 as hosts
from dataclasses import replace
import hashlib
from hedgehog import context_packets, structured_rationale
from hedgehog.kernel.integrity_replay_v01 import canonical_json_bytes_v01
from hedgehog.kernel import execution_mode_router_v01 as router

_MOCK_CALLS = []


def build_work_bsep_v01(
    *,
    request_id: str = "task:composition",
    domain_id: str = "WORK_COMPOSITION",
) -> dict[str, dict[str, object]]:
    route_id = "route:g2c:c2:bounded"
    proposal_id = "proposal:g2c:c2:bounded"
    vectors = ("vector:g2c:c2:bounded",)
    guards = ("guard:g2c:c2:root_review",)
    business = context_packets.build_business_request_context_packet(
        packet_id="context_packet:g2c:c2:business",
        created_by="runtime:g2c:c2",
        domain=domain_id,
        request_id=request_id,
        business_subject="certificate_request",
        requested_action="bounded_review",
        user_visible_summary="Bounded certificate request for Root review",
    )
    business_ref = {
        "source": "G2C_BUSINESS_REQUEST_CONTEXT_PACKET_V01",
        "packet_id": business["packet_id"],
        "request_id": request_id,
        "domain_id": domain_id,
    }
    route = context_packets.build_orchestrator_route_context_packet(
        packet_id="context_packet:g2c:c2:route",
        created_by="runtime:g2c:c2",
        source_refs=(business_ref,),
        domain=domain_id,
        allowed_routes=(route_id,),
        required_guards=guards,
        selected_vector_ids=vectors,
        route_validation_expectations={
            "root_review_required": True,
            "selected_only_allowed_vectors": True,
        },
        orchestrator_is_root=False,
        creates_action_commit_packet=False,
        calls_connectors=False,
    )
    proposal: dict[str, object] = {
        "proposal_id": proposal_id,
        "suggested_route": route_id,
        "selected_vector_ids": vectors,
        "required_guards": guards,
        "reason": "Bounded semantic review is required.",
        "confidence": 0.66,
        "needs_review": True,
        "uncertainty_notes": ("Evidence remains bounded and incomplete.",),
        "root_review_required": True,
        "truth_claimed": False,
        "authority_claimed": False,
        "action_permission_claimed": False,
        "final_output_claimed": False,
        "connector_command_claimed": False,
        "drs_write_claimed": False,
        "plan_graph_claimed": False,
        "bypass_root_claimed": False,
        "semantic_observations": (
            "A certificate request requires bounded review.",
        ),
        "route_reasoning": ("Use the bounded Root review route.",),
        "rejected_route_reasoning": ("Direct action remains forbidden.",),
        "guard_reasoning": ("Root review is mandatory.",),
        "vector_reasoning": ("The bounded vector is relevant.",),
        "authority_boundary_reasoning": ("Root remains final authority.",),
    }
    rationale = structured_rationale.build_orchestrator_structured_rationale(
        observed_semantics=proposal["semantic_observations"],
        route_selection_reason=proposal["route_reasoning"],
        rejected_routes=proposal["rejected_route_reasoning"],
        required_guards_reasoning=proposal["guard_reasoning"],
        selected_vector_reasoning=proposal["vector_reasoning"],
        uncertainty_notes=proposal["uncertainty_notes"],
        authority_boundary=proposal["authority_boundary_reasoning"],
        root_review_required=True,
    )
    rationale_sha = hashlib.sha256(
        canonical_json_bytes_v01(rationale)
    ).hexdigest()

    def item(text: str, evidence_kind: str) -> dict[str, object]:
        return context_packets.semantic_evidence_item(
            text,
            source="runtime_canonicalization",
            evidence_kind=evidence_kind,
            confidence_label="medium",
        )

    packet = context_packets.build_bounded_semantic_evidence_packet(
        packet_id="context_packet:g2c:c2:bsep",
        source_refs=(business_ref,),
        domain=domain_id,
        source_role="orchestrator",
        target_role="architect",
        source_route_id=route_id,
        source_proposal_id=proposal_id,
        source_context_packet_id=route["packet_id"],
        source_structured_rationale_ref=(
            "structured_rationale_v01:" + rationale_sha
        ),
        observed_semantic_facts=(
            item("A certificate request requires bounded review.", "observed_fact"),
        ),
        missing_evidence=(
            item("Root decision evidence is pending.", "missing_evidence"),
        ),
        uncertainty_notes=(
            item("Evidence remains bounded and incomplete.", "uncertainty"),
        ),
        risk_boundary_notes=(
            item("No action authority is present.", "risk_boundary"),
        ),
        rejected_action_routes=(
            item("Direct action remains forbidden.", "rejected_route"),
        ),
        required_approvals_or_conditions=(
            item("Root review is required.", "approval_condition"),
        ),
        authority_boundary_notes=(
            item("Root remains final authority.", "authority_boundary"),
        ),
        selected_vector_ids=vectors,
        required_guards=guards,
    )
    return {'business': business, 'route': route, 'proposal': proposal,
        'rationale': rationale, 'packet': packet}


class TrustedMockWorkSourceV01:
    """Explicit trusted fixture source, held by setup rather than task input."""
    def __init__(self, observations, bridge, evaluation_time, evaluation_time_source, evaluation_context_id):
        self._snapshot = hosts.TrustedWorkSourceSnapshotV01(observations, bridge, evaluation_time,
            evaluation_time_source, evaluation_context_id, 0)

    def read_current_v01(self):
        return self._snapshot

    def advance_v01(self, *, evaluation_time, observations=None):
        self._snapshot = replace(self._snapshot, evaluation_time=evaluation_time,
            observations=self._snapshot.observations if observations is None else observations,
            source_revision=self._snapshot.source_revision + 1)


def build_work_source_context_v01(task_id):
    bsep = build_work_bsep_v01(request_id=task_id)
    return router.build_execution_mode_source_context_v01(
        business_request_context_packet=bsep['business'], bsep_packet=bsep['packet'],
        bsep_route_context_packet=bsep['route'], bsep_orchestrator_proposal=bsep['proposal'], bsep_structured_rationale=bsep['rationale'],
        sealed_replay_evidence=None, replay_source_manifest=None, replay_source_domain_projection=None,
        replay_source_safe_file_contents=(), replay_anchor_publication=None, replay_anchored_verification=None,
        replay_supplied_anchor_publication_id=None, replay_reconstructed_manifest=None,
        replay_reconstructed_domain_projection=None, replay_reconstructed_safe_file_contents=(),
        g2a_inspection=None, g2a_registry=None, g2a_packet_id=None, g2a_corridor=None, g2a_corridor_step=None,
        g2a_current_dependency_observations=(), g2a_logical_time_bridge=None, g2a_evaluation_time=1014,
        g2a_evaluation_time_source='u1.controlled_utc', g2a_evaluation_context_id='context:u1:dispatch',
        g2a_transition_registry_profile=None, g2b_resolution_report=None, g2b_compatibility_projections=(),
        g2b_use_time=None, g2b_root_kernel=None, g2b_root_decision_input=None, g2b_root_decision_result=None,
        g2b_writeback_evidence=None)


def observed_mock_calls_v01():
    return tuple(_MOCK_CALLS)


def validate_playback_plan_inputs_v01(definition, inputs):
    errors = firewall.validate_capability_values_v01(definition.input_fields, inputs)
    return firewall.build_capability_validation_evidence_v01(definition=definition, values=inputs,
        invocation_id=None, valid=not errors, reason_codes=errors)


def compute_playback_plan_v01(invocation):
    values = {v.parameter_name: v.value for v in invocation.inputs}
    return (action.build_action_effect_parameter_record_v01(parameter_name='plan', value_type='TEXT',
        value='would_play:' + values['content_ref'] + '@' + values['device_ref']),)


def validate_playback_plan_output_v01(definition, invocation, output):
    errors = firewall.validate_capability_values_v01(definition.output_fields, output)
    if not errors:
        values = {v.parameter_name: v.value for v in invocation.inputs}
        if output[0].value != 'would_play:' + values['content_ref'] + '@' + values['device_ref']:
            errors = ('playback_plan_mismatch',)
    return firewall.build_capability_validation_evidence_v01(definition=definition, values=output,
        invocation_id=invocation.invocation_id, valid=not errors, reason_codes=errors)


def admit_playback_plan_v01(host_instance_ref):
    functions = (validate_playback_plan_inputs_v01, validate_playback_plan_output_v01, compute_playback_plan_v01)
    sources = tuple(hosts.observe_local_capability_code_v01(v) for v in functions)
    definition = firewall.build_capability_definition_v01(operation_id='u1.playback_plan', version='v01',
        effect_kind='PURE', business_semantics=None, input_fields=tuple(firewall.build_capability_field_v01(
            name=n, value_type='REFERENCE', required=True, consequential=False) for n in ('content_ref', 'device_ref')),
        output_fields=(firewall.build_capability_field_v01(name='plan', value_type='TEXT', required=True, consequential=False),),
        resource_refs=(), input_validator_ref=sources[0].public_symbol, output_validator_ref=sources[1].public_symbol,
        executor_ref=sources[2].public_symbol, code_sha256s=tuple((s.public_symbol, s.source_sha256) for s in sources))
    return hosts.admit_local_capability_v01(definition=definition, input_validator=functions[0],
        output_validator=functions[1], executor=functions[2], catalogue_revision=0, host_instance_ref=host_instance_ref)


def validate_work_inputs_v01(definition, inputs):
    errors = firewall.validate_capability_values_v01(definition.input_fields, inputs)
    return firewall.build_capability_validation_evidence_v01(definition=definition, values=inputs,
        invocation_id=None, valid=not errors, reason_codes=errors)


def read_property_v01(invocation):
    source = next(v for v in invocation.inputs if v.parameter_name == 'property')
    return (action.build_action_effect_parameter_record_v01(parameter_name='content_ref',
        value_type='REFERENCE', value=source.value),)


def validate_property_output_v01(definition, invocation, output):
    errors = firewall.validate_capability_values_v01(definition.output_fields, output)
    if not errors and output[0].value != next(v.value for v in invocation.inputs if v.parameter_name == 'property'):
        errors = ('property_output_mismatch',)
    return firewall.build_capability_validation_evidence_v01(definition=definition, values=output,
        invocation_id=invocation.invocation_id, valid=not errors, reason_codes=errors)


def transform_content_v01(invocation):
    source = next(v for v in invocation.inputs if v.parameter_name == 'content_ref')
    return (action.build_action_effect_parameter_record_v01(parameter_name='transformed_ref',
        value_type='REFERENCE', value=source.value + ':rendered'),)


def validate_transform_output_v01(definition, invocation, output):
    errors = firewall.validate_capability_values_v01(definition.output_fields, output)
    if not errors and output[0].value != next(v.value for v in invocation.inputs if v.parameter_name == 'content_ref') + ':rendered':
        errors = ('transform_output_mismatch',)
    return firewall.build_capability_validation_evidence_v01(definition=definition, values=output,
        invocation_id=invocation.invocation_id, valid=not errors, reason_codes=errors)


def observe_level_v01(invocation):
    value = next(v.value for v in invocation.inputs if v.parameter_name == 'reading')
    return (action.build_action_effect_parameter_record_v01(parameter_name='observed_level', value_type='INTEGER', value=value),)


def validate_level_output_v01(definition, invocation, output):
    errors = firewall.validate_capability_values_v01(definition.output_fields, output)
    if not errors and output[0].value != next(v.value for v in invocation.inputs if v.parameter_name == 'reading'):
        errors = ('level_output_mismatch',)
    return firewall.build_capability_validation_evidence_v01(definition=definition, values=output,
        invocation_id=invocation.invocation_id, valid=not errors, reason_codes=errors)


def compare_level_v01(invocation):
    values = {v.parameter_name: v.value for v in invocation.inputs}
    return (action.build_action_effect_parameter_record_v01(parameter_name='exceeds', value_type='BOOLEAN',
        value=values['level'] > values['threshold']),)


def validate_comparison_output_v01(definition, invocation, output):
    errors = firewall.validate_capability_values_v01(definition.output_fields, output)
    values = {v.parameter_name: v.value for v in invocation.inputs}
    if not errors and output[0].value is not (values['level'] > values['threshold']):
        errors = ('comparison_output_mismatch',)
    return firewall.build_capability_validation_evidence_v01(definition=definition, values=output,
        invocation_id=invocation.invocation_id, valid=not errors, reason_codes=errors)


def admit_pure_operation_v01(*, operation_id, input_fields, output_fields, executor, output_validator, host_instance_ref):
    functions = (validate_work_inputs_v01, output_validator, executor)
    sources = tuple(hosts.observe_local_capability_code_v01(c) for c in functions)
    definition = firewall.build_capability_definition_v01(operation_id=operation_id, version='v01', effect_kind='PURE',
        business_semantics=None, input_fields=tuple(firewall.build_capability_field_v01(name=n, value_type=t,
            required=True, consequential=False) for n, t in input_fields),
        output_fields=tuple(firewall.build_capability_field_v01(name=n, value_type=t,
            required=True, consequential=False) for n, t in output_fields), resource_refs=(),
        input_validator_ref=sources[0].public_symbol, output_validator_ref=sources[1].public_symbol,
        executor_ref=sources[2].public_symbol, code_sha256s=tuple((s.public_symbol, s.source_sha256) for s in sources))
    return hosts.admit_local_capability_v01(definition=definition, input_validator=functions[0], output_validator=functions[1],
        executor=functions[2], catalogue_revision=0, host_instance_ref=host_instance_ref)


def execute_alarm_v01(invocation):
    _MOCK_CALLS.append(('EXECUTOR_STARTED', invocation.invocation_id, invocation.inputs))
    values = {v.parameter_name: v.value for v in invocation.inputs}
    return tuple(action.build_action_effect_parameter_record_v01(parameter_name=n, value_type=t, value=v)
        for n, t, v in (('alarm_state', 'TEXT', ('sounding:' if values['enabled'] else 'silent:') + values['device_ref']),
            ('device_ref', 'REFERENCE', values['device_ref']), ('enabled', 'BOOLEAN', values['enabled'])))


def validate_alarm_output_v01(definition, invocation, output):
    _MOCK_CALLS.append(('OUTPUT_VALIDATOR', invocation.invocation_id, output))
    errors = firewall.validate_capability_values_v01(definition.output_fields, output)
    if not errors:
        actual = {v.parameter_name: v.value for v in output}
        inputs = {v.parameter_name: v.value for v in invocation.inputs}
        if actual != dict(inputs, alarm_state=('sounding:' if inputs['enabled'] else 'silent:') + inputs['device_ref']):
            errors = ('alarm_output_binding_mismatch',)
    return firewall.build_capability_validation_evidence_v01(definition=definition, values=output,
        invocation_id=invocation.invocation_id, valid=not errors, reason_codes=errors)


def admit_alarm_v01(device_ref, host_instance_ref):
    functions = (validate_playback_inputs_v01, validate_alarm_output_v01, execute_alarm_v01)
    sources = tuple(hosts.observe_local_capability_code_v01(c) for c in functions)
    semantics = firewall.build_capability_business_semantics_v01(operation_key='u1.alarm.v01',
        selected_action_class='mock_action:alarm', logical_effect_class='ALARM', logical_effect_namespace='u1.alarm.v01',
        business_object_class='SIGNAL', business_object_namespace='u1.signal.v01', input_bindings=(
            firewall.build_capability_business_input_binding_v01(input_name='device_ref', source_kind='TARGET_RECORD', source_name='device_ref', value_type='REFERENCE'),
            firewall.build_capability_business_input_binding_v01(input_name='enabled', source_kind='RECORD', source_name='enabled', value_type='BOOLEAN')))
    definition = firewall.build_capability_definition_v01(operation_id=semantics.operation_key, version='v01',
        effect_kind='MOCK_CONSEQUENTIAL', business_semantics=semantics,
        input_fields=tuple(firewall.build_capability_field_v01(name=n, value_type=t, required=True, consequential=True)
            for n, t in (('device_ref', 'REFERENCE'), ('enabled', 'BOOLEAN'))),
        output_fields=tuple(firewall.build_capability_field_v01(name=n, value_type=t, required=True, consequential=False)
            for n, t in (('device_ref', 'REFERENCE'), ('enabled', 'BOOLEAN'), ('alarm_state', 'TEXT'))),
        resource_refs=(device_ref,), input_validator_ref=sources[0].public_symbol, output_validator_ref=sources[1].public_symbol,
        executor_ref=sources[2].public_symbol, code_sha256s=tuple((s.public_symbol, s.source_sha256) for s in sources))
    return hosts.admit_local_capability_v01(definition=definition, input_validator=functions[0], output_validator=functions[1],
        executor=functions[2], catalogue_revision=0, host_instance_ref=host_instance_ref)


def validate_playback_inputs_v01(definition, inputs):
    _MOCK_CALLS.append(('INPUT_VALIDATOR', definition.definition_id, inputs))
    errors = firewall.validate_capability_values_v01(definition.input_fields, inputs)
    return firewall.build_capability_validation_evidence_v01(
        definition=definition, values=inputs, invocation_id=None,
        valid=not errors, reason_codes=errors)


def execute_playback_v01(invocation):
    _MOCK_CALLS.append(('EXECUTOR_STARTED', invocation.invocation_id, invocation.inputs))
    values = {r.parameter_name: r.value for r in invocation.inputs}
    return tuple(action.build_action_effect_parameter_record_v01(
        parameter_name=name, value_type=kind, value=value)
        for name, kind, value in (
            ('content_ref', 'REFERENCE', values['content_ref']),
            ('device_ref', 'REFERENCE', values['device_ref']),
            ('playback_state', 'TEXT', 'playing:' + values['content_ref'] + '@' + values['device_ref'])))


def validate_playback_output_v01(definition, invocation, output):
    _MOCK_CALLS.append(('OUTPUT_VALIDATOR', invocation.invocation_id, output))
    errors = firewall.validate_capability_values_v01(definition.output_fields, output)
    if not errors:
        inputs = {r.parameter_name: r.value for r in invocation.inputs}
        values = {r.parameter_name: r.value for r in output}
        if (values['device_ref'] != inputs['device_ref'] or values['content_ref'] != inputs['content_ref']
            or values['playback_state'] != 'playing:' + inputs['content_ref'] + '@' + inputs['device_ref']):
            errors = ('playback_output_binding_mismatch',)
    return firewall.build_capability_validation_evidence_v01(
        definition=definition, values=output, invocation_id=invocation.invocation_id,
        valid=not errors, reason_codes=errors)


def build_playback_definition_v01(device_ref):
    callables = (validate_playback_inputs_v01, validate_playback_output_v01, execute_playback_v01)
    sources = tuple(hosts.observe_local_capability_code_v01(c) for c in callables)
    inputs = tuple(firewall.build_capability_field_v01(name=name, value_type='REFERENCE',
        required=True, consequential=True) for name in ('content_ref', 'device_ref'))
    outputs = inputs + (firewall.build_capability_field_v01(name='playback_state', value_type='TEXT',
        required=True, consequential=False),)
    semantics = firewall.build_capability_business_semantics_v01(
        operation_key='u1.playback.v01', selected_action_class='mock_action:playback',
        logical_effect_class='PLAYBACK', logical_effect_namespace='u1.playback.v01',
        business_object_class='CONTENT', business_object_namespace='u1.content.v01',
        input_bindings=(
            firewall.build_capability_business_input_binding_v01(input_name='content_ref',
                source_kind='BUSINESS_OBJECT_REF', source_name='business_object_ref', value_type='REFERENCE'),
            firewall.build_capability_business_input_binding_v01(input_name='device_ref',
                source_kind='TARGET_RECORD', source_name='device_ref', value_type='REFERENCE')))
    return firewall.build_capability_definition_v01(operation_id=semantics.operation_key, version='v0.1',
        effect_kind='MOCK_CONSEQUENTIAL', business_semantics=semantics,
        input_fields=inputs, output_fields=outputs, resource_refs=(device_ref,),
        input_validator_ref=sources[0].public_symbol, output_validator_ref=sources[1].public_symbol,
        executor_ref=sources[2].public_symbol,
        code_sha256s=tuple((s.public_symbol, s.source_sha256) for s in sources))


def admit_playback_v01(device_ref, host_instance_ref, catalogue_revision=0):
    return hosts.admit_local_capability_v01(definition=build_playback_definition_v01(device_ref),
        input_validator=validate_playback_inputs_v01, output_validator=validate_playback_output_v01,
        executor=execute_playback_v01, catalogue_revision=catalogue_revision, host_instance_ref=host_instance_ref)


def admit_playback_variant_v01(device_ref, host_instance_ref, executor, catalogue_revision=0):
    original = build_playback_definition_v01(device_ref)
    sources = tuple(hosts.observe_local_capability_code_v01(c) for c in
        (validate_playback_inputs_v01, validate_playback_output_v01, executor))
    definition = firewall.build_capability_definition_v01(operation_id=original.operation_id, version=original.version,
        effect_kind=original.effect_kind, business_semantics=original.business_semantics,
        input_fields=original.input_fields, output_fields=original.output_fields, resource_refs=original.resource_refs,
        input_validator_ref=sources[0].public_symbol, output_validator_ref=sources[1].public_symbol, executor_ref=sources[2].public_symbol,
        code_sha256s=tuple((s.public_symbol, s.source_sha256) for s in sources))
    return hosts.admit_local_capability_v01(definition=definition, input_validator=validate_playback_inputs_v01,
        output_validator=validate_playback_output_v01, executor=executor, catalogue_revision=catalogue_revision, host_instance_ref=host_instance_ref)


def execute_playback_uncertain_v01(invocation):
    _MOCK_CALLS.append(('EXECUTOR_STARTED_UNCERTAIN', invocation.invocation_id, invocation.inputs))
    raise RuntimeError('controlled_mock_exception_after_start')


def execute_playback_wrong_output_v01(invocation):
    _MOCK_CALLS.append(('EXECUTOR_STARTED_WRONG_OUTPUT', invocation.invocation_id, invocation.inputs))
    values = {r.parameter_name: r.value for r in invocation.inputs}
    return tuple(action.build_action_effect_parameter_record_v01(parameter_name=n, value_type=k, value=v)
        for n, k, v in (('content_ref', 'REFERENCE', values['content_ref']),
            ('device_ref', 'REFERENCE', values['device_ref']), ('playback_state', 'TEXT', 'stopped')))


def validate_payment_inputs_v01(definition, inputs):
    _MOCK_CALLS.append(('INPUT_VALIDATOR', definition.definition_id, inputs))
    errors = firewall.validate_capability_values_v01(definition.input_fields, inputs)
    if not errors:
        slot = next(r.value for r in inputs if r.parameter_name == 'payment_slot_ref')
        if len(definition.resource_refs) != 2 or slot not in definition.resource_refs:
            errors = ('payment_target_role_mismatch',)
    return firewall.build_capability_validation_evidence_v01(definition=definition, values=inputs,
        invocation_id=None, valid=not errors, reason_codes=errors)


def execute_payment_v01(invocation):
    _MOCK_CALLS.append(('EXECUTOR_STARTED', invocation.invocation_id, invocation.inputs))
    values = {r.parameter_name: r.value for r in invocation.inputs}
    creditor = next(ref for ref in invocation.resource_refs if ref != values['payment_slot_ref'])
    return tuple(action.build_action_effect_parameter_record_v01(parameter_name=n, value_type=k, value=v)
        for n, k, v in (('amount', 'DECIMAL', values['amount']), ('creditor_ref', 'REFERENCE', creditor),
            ('currency', 'TEXT', values['currency']), ('payment_slot_ref', 'REFERENCE', values['payment_slot_ref']),
            ('settlement', 'TEXT', values['amount'] + ' ' + values['currency'] + ' -> ' + creditor)))


def execute_payment_revision_v01(invocation):
    _MOCK_CALLS.append(('EXECUTOR_STARTED_REVISION', invocation.invocation_id, invocation.inputs))
    values = dict((r.parameter_name, r.value) for r in invocation.inputs)
    creditor = next(ref for ref in invocation.resource_refs if ref != values['payment_slot_ref'])
    records = {'amount': ('DECIMAL', values['amount']), 'creditor_ref': ('REFERENCE', creditor),
        'currency': ('TEXT', values['currency']), 'payment_slot_ref': ('REFERENCE', values['payment_slot_ref']),
        'settlement': ('TEXT', '{} {} -> {}'.format(values['amount'], values['currency'], creditor))}
    return tuple(action.build_action_effect_parameter_record_v01(parameter_name=name, value_type=records[name][0],
        value=records[name][1]) for name in sorted(records))


def validate_payment_output_v01(definition, invocation, output):
    _MOCK_CALLS.append(('OUTPUT_VALIDATOR', invocation.invocation_id, output))
    errors = firewall.validate_capability_values_v01(definition.output_fields, output)
    if not errors:
        inputs = {r.parameter_name: r.value for r in invocation.inputs}
        values = {r.parameter_name: r.value for r in output}
        creditor = next(ref for ref in invocation.resource_refs if ref != inputs['payment_slot_ref'])
        if (any(values[k] != inputs[k] for k in ('amount', 'currency', 'payment_slot_ref')) or
            values['creditor_ref'] != creditor or values['settlement'] != inputs['amount'] + ' ' + inputs['currency'] + ' -> ' + creditor):
            errors = ('payment_output_binding_mismatch',)
    return firewall.build_capability_validation_evidence_v01(definition=definition, values=output,
        invocation_id=invocation.invocation_id, valid=not errors, reason_codes=errors)


def admit_payment_v01(canonical, host_instance_ref, executor=execute_payment_v01, catalogue_revision=0):
    selected = (validate_payment_inputs_v01, validate_payment_output_v01, executor)
    sources = tuple(hosts.observe_local_capability_code_v01(c) for c in selected)
    semantics = firewall.build_capability_business_semantics_v01(operation_key=canonical.authority_policy.logical_effect_namespace,
        selected_action_class=canonical.selected_canonical_action, logical_effect_class=canonical.logical_intent.logical_effect_class,
        logical_effect_namespace=canonical.authority_policy.logical_effect_namespace,
        business_object_class=canonical.business_object_identity.business_object_class,
        business_object_namespace=canonical.business_object_identity.business_object_namespace,
        input_bindings=tuple(firewall.build_capability_business_input_binding_v01(input_name=n, source_kind=k, source_name=s, value_type=t)
            for n, k, s, t in (('amount', 'AMOUNT', 'amount_decimal', 'DECIMAL'), ('currency', 'CURRENCY', 'currency_code', 'TEXT'),
                ('payment_slot_ref', 'BUSINESS_OBJECT_REF', 'business_object_ref', 'REFERENCE'))))
    definition = firewall.build_capability_definition_v01(operation_id=semantics.operation_key, version='v0.1',
        effect_kind='MOCK_CONSEQUENTIAL', business_semantics=semantics,
        input_fields=tuple(firewall.build_capability_field_v01(name=n, value_type=t, required=True, consequential=True)
            for n, t in (('amount', 'DECIMAL'), ('currency', 'TEXT'), ('payment_slot_ref', 'REFERENCE'))),
        output_fields=tuple(firewall.build_capability_field_v01(name=n, value_type=t, required=True, consequential=False)
            for n, t in (('amount', 'DECIMAL'), ('creditor_ref', 'REFERENCE'), ('currency', 'TEXT'), ('payment_slot_ref', 'REFERENCE'), ('settlement', 'TEXT'))),
        resource_refs=canonical.normalized_target_scope.included_target_refs,
        input_validator_ref=sources[0].public_symbol, output_validator_ref=sources[1].public_symbol, executor_ref=sources[2].public_symbol,
        code_sha256s=tuple((s.public_symbol, s.source_sha256) for s in sources))
    return hosts.admit_local_capability_v01(definition=definition, input_validator=selected[0], output_validator=selected[1],
        executor=executor, catalogue_revision=catalogue_revision, host_instance_ref=host_instance_ref)
