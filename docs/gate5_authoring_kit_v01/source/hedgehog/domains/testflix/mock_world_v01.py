"""Recorded deterministic calls admitted by the common execution host."""
from dataclasses import replace
from decimal import Decimal
from hedgehog import action_commit_packet_v02 as action
from hedgehog import work_execution_host_v01 as hosts
from hedgehog.kernel import effect_firewall_v01 as firewall
from hedgehog.domains.testflix import contracts_v01 as c

CALLS = []


def records_v01(values):
    return tuple(action.build_action_effect_parameter_record_v01(parameter_name=n, value_type=t, value=v)
        for n, (t, v) in sorted(values.items()))


def values_v01(records):
    return {r.parameter_name: r.value for r in records}


def validate_inputs_v01(definition, inputs):
    CALLS.append(('INPUT_VALIDATOR', definition.definition_id, inputs))
    errors = firewall.validate_capability_values_v01(definition.input_fields, inputs)
    if not errors:
        values = values_v01(inputs)
        if 'amount' in values and Decimal(values['amount']) <= 0:
            errors = ('payment_amount_not_positive',)
        if 'price_minor' in values and values['price_minor'] <= 0:
            errors = ('quote_price_not_positive',)
        if 'valid_to' in values and values['valid_to'] <= values['valid_from']:
            errors = ('validity_interval',)
    return firewall.build_capability_validation_evidence_v01(definition=definition, values=inputs,
        invocation_id=None, valid=not errors, reason_codes=errors)


def compute_output_v01(operation, inputs):
    """Pure business transformations shared by output checks, never dispatch."""
    v = values_v01(inputs)
    if operation == 'testflix.quote.v01':
        return records_v01(dict(plan_id=('REFERENCE',v['plan_id']), price_minor=('INTEGER',v['price_minor']),
            period_seconds=('INTEGER',v['period_seconds']), quote_ref=('REFERENCE',c.identity_v01('quote', v))))
    if operation == 'testflix.period.v01':
        return records_v01(dict(quote_ref=('REFERENCE',v['quote_ref']), valid_to=('INTEGER',v['now']+v['period_seconds'])))
    if operation == 'testflix.payment.v01':
        return records_v01(dict(amount_minor=('INTEGER',int(Decimal(v['amount'])*100)), currency=('TEXT',v['currency']),
            merchant_id=('REFERENCE',v['merchant_id']), order_id=('REFERENCE',v['order_id']),
            payment_ref=('REFERENCE',c.identity_v01('payment',v))))
    if operation in ('testflix.entitlement.v01','testflix.session.v01','testflix.device_grant.v01'):
        output = {record.parameter_name:(record.value_type,record.value) for record in inputs}
        output['issuance_ref'] = ('REFERENCE',c.identity_v01(operation,v))
        return records_v01(output)
    if operation == 'testflix.playback.v01':
        return records_v01(dict(session_ref=('REFERENCE',v['session_ref']), device_id=('REFERENCE',v['device_id']),
            content_id=('REFERENCE',v['content_id']), playback_ref=('REFERENCE',c.identity_v01('playback',v)),
            playback_state=('TEXT','PLAYING')))
    if operation in ('testflix.stop.v01','testflix.close.v01'):
        output = {record.parameter_name:(record.value_type,record.value) for record in inputs}
        output['closure_ref'] = ('REFERENCE',c.identity_v01(operation,v))
        output['state'] = ('TEXT','STOPPED' if operation=='testflix.stop.v01' else 'CLOSED')
        return records_v01(output)
    raise ValueError('unknown_operation')


def execute_quote_v01(invocation):
    CALLS.append(('EXECUTOR', invocation.invocation_id, invocation.inputs))
    return compute_output_v01('testflix.quote.v01', invocation.inputs)


def execute_period_v01(invocation):
    CALLS.append(('EXECUTOR', invocation.invocation_id, invocation.inputs))
    return compute_output_v01('testflix.period.v01', invocation.inputs)


def execute_payment_v01(invocation):
    CALLS.append(('EXECUTOR', invocation.invocation_id, invocation.inputs))
    return compute_output_v01('testflix.payment.v01', invocation.inputs)


def execute_entitlement_v01(invocation):
    CALLS.append(('EXECUTOR', invocation.invocation_id, invocation.inputs))
    return compute_output_v01('testflix.entitlement.v01', invocation.inputs)


def execute_session_v01(invocation):
    CALLS.append(('EXECUTOR', invocation.invocation_id, invocation.inputs))
    return compute_output_v01('testflix.session.v01', invocation.inputs)


def execute_playback_v01(invocation):
    CALLS.append(('EXECUTOR', invocation.invocation_id, invocation.inputs))
    return compute_output_v01('testflix.playback.v01', invocation.inputs)


def execute_stop_v01(invocation):
    CALLS.append(('EXECUTOR', invocation.invocation_id, invocation.inputs))
    return compute_output_v01('testflix.stop.v01', invocation.inputs)


def execute_close_v01(invocation):
    CALLS.append(('EXECUTOR', invocation.invocation_id, invocation.inputs))
    return compute_output_v01('testflix.close.v01', invocation.inputs)


def execute_device_grant_v01(invocation):
    CALLS.append(('EXECUTOR', invocation.invocation_id, invocation.inputs))
    return compute_output_v01('testflix.device_grant.v01', invocation.inputs)


def validate_outputs_v01(definition, invocation, output):
    CALLS.append(('OUTPUT_VALIDATOR', invocation.invocation_id, output))
    errors = firewall.validate_capability_values_v01(definition.output_fields, output)
    if not errors and output != compute_output_v01(definition.operation_id, invocation.inputs):
        errors = ('actual_business_output_binding',)
    return firewall.build_capability_validation_evidence_v01(definition=definition, values=output,
        invocation_id=invocation.invocation_id, valid=not errors, reason_codes=errors)


def admit_v01(operation, root, inputs, outputs, *, selectors=None, targets=()):
    executors = {'testflix.quote.v01':execute_quote_v01, 'testflix.period.v01':execute_period_v01,
        'testflix.payment.v01':execute_payment_v01, 'testflix.entitlement.v01':execute_entitlement_v01,
        'testflix.session.v01':execute_session_v01, 'testflix.playback.v01':execute_playback_v01,
        'testflix.stop.v01':execute_stop_v01,'testflix.close.v01':execute_close_v01,
        'testflix.device_grant.v01':execute_device_grant_v01}
    functions = (validate_inputs_v01, validate_outputs_v01, executors[operation])
    sources = tuple(hosts.observe_local_capability_code_v01(f) for f in functions)
    consequential = selectors is not None
    semantics = None
    if consequential:
        selectors = dict(selectors)
        bindings = []
        for name, kind in inputs:
            source_kind, source_name = selectors.get(name, ('RECORD',name))
            bindings.append(firewall.build_capability_business_input_binding_v01(input_name=name,
                source_kind=source_kind, source_name=source_name, value_type=kind))
        semantics = firewall.build_capability_business_semantics_v01(operation_key=operation,
            selected_action_class='mock_action:testflix_' + operation.split('.')[1], logical_effect_class=operation.split('.')[1].upper(),
            logical_effect_namespace=operation, business_object_class='DOMAIN_OBJECT',
            business_object_namespace=operation + '.object', input_bindings=tuple(bindings))
    definition = firewall.build_capability_definition_v01(operation_id=operation, version='v01',
        effect_kind='MOCK_CONSEQUENTIAL' if consequential else 'PURE', business_semantics=semantics,
        input_fields=tuple(firewall.build_capability_field_v01(name=n, value_type=t, required=True,
            consequential=consequential) for n,t in inputs),
        output_fields=tuple(firewall.build_capability_field_v01(name=n, value_type=t, required=True,
            consequential=False) for n,t in outputs), resource_refs=tuple(targets),
        input_validator_ref=sources[0].public_symbol, output_validator_ref=sources[1].public_symbol,
        executor_ref=sources[2].public_symbol, code_sha256s=tuple((s.public_symbol,s.source_sha256) for s in sources))
    return hosts.admit_local_capability_v01(definition=definition, input_validator=functions[0],
        output_validator=functions[1], executor=functions[2], catalogue_revision=0, host_instance_ref='host:' + root)


class LocalSourceV01:
    """Application-owned authoritative logical clock/dependencies, not task input."""
    def __init__(self, now, observations=()):
        bridge = action.build_logical_time_bridge_v01(origin_utc_epoch_seconds=now, seconds_per_tick=1,
            bridge_policy_version='testflix.logical.v01')
        self.snapshot = hosts.TrustedWorkSourceSnapshotV01(tuple(observations), bridge, now+4,
            'testflix.controlled_utc', 'context:testflix:dispatch', 0)

    def read_current_v01(self):
        return self.snapshot

    def advance_clock_v01(self, now):
        c.require_v01(type(now) is int and now+4>=self.snapshot.evaluation_time,'clock_must_be_monotonic')
        self.snapshot = replace(self.snapshot,evaluation_time=now+4,source_revision=self.snapshot.source_revision+1)

    def install_observations_v01(self, observations):
        c.require_v01(type(observations) is tuple and all(action.validate_action_dependency_current_observation_v01(v)[0]
            for v in observations), 'source_observation_type')
        existing = {v.dependency_id:v for v in self.snapshot.observations}
        existing.update({v.dependency_id:v for v in observations})
        self.snapshot = replace(self.snapshot, observations=tuple(existing[k] for k in sorted(existing)),
            source_revision=self.snapshot.source_revision+1)

    def withdraw_observations_v01(self, dependency_ids):
        c.require_v01(type(dependency_ids) is tuple and all(type(v) is str for v in dependency_ids), 'source_withdrawal_type')
        self.snapshot = replace(self.snapshot,observations=tuple(v for v in self.snapshot.observations if v.dependency_id not in dependency_ids),
            source_revision=self.snapshot.source_revision+1)
