"""Finite admitted transforms and an effect executor, with no authority cache."""
from contextvars import ContextVar
import json
from hedgehog import action_commit_packet_v02 as action
from hedgehog import work_execution_host_v01 as hosts
from hedgehog.kernel import effect_firewall_v01 as firewall
from . import contracts_v01 as c

EXECUTION = ContextVar('sentinel_current_finite_execution', default=None)


def records(values):
    return tuple(action.build_action_effect_parameter_record_v01(parameter_name=n, value_type=t, value=v)
                 for n,(t,v) in sorted(values.items()))


def values(records):
    return {r.parameter_name:r.value for r in records}


def compute(operation, inputs):
    data = json.loads(values(inputs)['material'])
    if operation == 'sentinel.compile.v01' or operation == 'sentinel.diagnostic.v01':
        data = c.diagnostic(data)
    elif operation == 'sentinel.contract.v01':
        c.require(data['selection'] in c.DIAGNOSTICS and type(data['healthy']) is bool, 'diagnostic_result_required')
    elif operation == 'sentinel.information.v01':
        c.require(type(data['summary']) is str and bool(data['record_id']), 'actual_memory_summary_required')
        data = dict(record_id=data['record_id'], summary=data['summary'], informational_only=True)
    elif operation == 'sentinel.configuration.v01':
        c.validate_policy(data['contract'])
        if data.get('kind')=='CURRENT_CONFIGURATION':
            c.require(set(data)=={'kind','rainfall','contract','diagnostic_result_ref'} and bool(data['diagnostic_result_ref']),
                'current_configuration_material')
            refs=dict(diagnostic_result_ref=data['diagnostic_result_ref'])
        else:
            c.require(bool(data['recomputed_result_ref']) and bool(data['consumed_binding_ref']), 'consumed_delta_required')
            refs={k:data[k] for k in ('delta_result_ref','recomputed_result_ref','source_artifact_ref')}
        data=dict(cadence_seconds=c.cadence(data['rainfall'],data['contract']),contract=data['contract'],
            input_sha256=c.digest(data),**refs)
    elif operation == 'sentinel.observability.v01':
        data=c.observability(data)
    else:
        raise ValueError('unknown_admitted_operation')
    return records(dict(material=('TEXT',c.canonical(data).decode()), fingerprint=('REFERENCE',c.identity('work',data))))


def validate_inputs_v01(definition, inputs):
    errors = firewall.validate_capability_values_v01(definition.input_fields, inputs)
    if not errors and definition.effect_kind == 'MOCK_CONSEQUENTIAL':
        try:
            session = EXECUTION.get()
            c.require(session is not None, 'finite_execution_context_missing')
            session.validate_effect(values(inputs))
        except (ValueError, KeyError, TypeError) as exc:
            errors = (str(exc),)
    return firewall.build_capability_validation_evidence_v01(definition=definition, values=inputs,
        invocation_id=None, valid=not errors, reason_codes=errors)


def execute_compile_v01(invocation):
    return compute('sentinel.compile.v01', invocation.inputs)


def execute_contract_v01(invocation):
    return compute('sentinel.contract.v01', invocation.inputs)


def execute_diagnostic_v01(invocation):
    return compute('sentinel.diagnostic.v01', invocation.inputs)


def execute_command_v01(invocation):
    session = EXECUTION.get()
    c.require(session is not None and invocation.owning_root_id == session.root, 'executor_local_root')
    result = session.execute_effect(values(invocation.inputs), invocation.invocation_id)
    return records(dict(material=('TEXT',c.canonical(result).decode()), fingerprint=('REFERENCE',c.identity('result',result))))


def validate_outputs_v01(definition, invocation, output):
    errors = firewall.validate_capability_values_v01(definition.output_fields, output)
    if not errors:
        if definition.effect_kind == 'PURE':
            if output != compute(definition.operation_id, invocation.inputs):
                errors = ('actual_contract_output',)
        else:
            session = EXECUTION.get()
            actual = None if session is None else session.executed.get(invocation.invocation_id)
            if actual is None or values(output) != dict(material=c.canonical(actual).decode(),fingerprint=c.identity('result',actual)):
                errors = ('actual_effect_output',)
    return firewall.build_capability_validation_evidence_v01(definition=definition, values=output,
        invocation_id=invocation.invocation_id, valid=not errors, reason_codes=errors)


def admit(root, operation, executor, consequential=False, resource_refs=()):
    functions = (validate_inputs_v01, validate_outputs_v01, executor)
    sources = tuple(hosts.observe_local_capability_code_v01(f) for f in functions)
    fields = [('material','TEXT')] if not consequential else [('command','TEXT'),('session','REFERENCE'),('version','INTEGER')]
    semantics = None
    if consequential:
        semantics = firewall.build_capability_business_semantics_v01(operation_key=operation,
            selected_action_class='mock_action:sentinel_monitoring_command', logical_effect_class='LOCAL_MONITORING_COMMAND',
            logical_effect_namespace=operation, business_object_class='DOMAIN_OBJECT', business_object_namespace='sentinel.command',
            input_bindings=tuple(firewall.build_capability_business_input_binding_v01(input_name=n,
                source_kind='RECORD',source_name=n,value_type=t) for n,t in fields))
    definition = firewall.build_capability_definition_v01(operation_id=operation,version='v01',
        effect_kind='MOCK_CONSEQUENTIAL' if consequential else 'PURE',business_semantics=semantics,
        input_fields=tuple(firewall.build_capability_field_v01(name=n,value_type=t,required=True,consequential=consequential) for n,t in fields),
        output_fields=tuple(firewall.build_capability_field_v01(name=n,value_type=t,required=True,consequential=False)
            for n,t in [('material','TEXT'),('fingerprint','REFERENCE')]),resource_refs=resource_refs,
        input_validator_ref=sources[0].public_symbol,output_validator_ref=sources[1].public_symbol,executor_ref=sources[2].public_symbol,
        code_sha256s=tuple((s.public_symbol,s.source_sha256) for s in sources))
    return hosts.admit_local_capability_v01(definition=definition,input_validator=functions[0],output_validator=functions[1],
        executor=functions[2],catalogue_revision=0,host_instance_ref='host:'+root)


def execute_information_v01(invocation):
    return compute('sentinel.information.v01', invocation.inputs)


def execute_configuration_v01(invocation):
    return compute('sentinel.configuration.v01', invocation.inputs)


def execute_observability_v01(invocation):
    return compute('sentinel.observability.v01',invocation.inputs)


def catalogue(root, session):
    return (admit(root,'sentinel.compile.v01',execute_compile_v01),
            admit(root,'sentinel.contract.v01',execute_contract_v01),
            admit(root,'sentinel.command.v01',execute_command_v01,True,(session,)),
            admit(root,'sentinel.diagnostic.v01',execute_diagnostic_v01),
            admit(root,'sentinel.information.v01',execute_information_v01),
            admit(root,'sentinel.configuration.v01',execute_configuration_v01),
            admit(root,'sentinel.observability.v01',execute_observability_v01))
