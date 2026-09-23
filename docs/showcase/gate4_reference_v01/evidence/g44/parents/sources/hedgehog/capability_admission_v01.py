"""Finite PURE needs, independent admission and the fixed native bridge.

Generated code is data. Host-held origins and resource reservations distinguish
an observed admission from a caller-created evidence value.
"""
from contextvars import ContextVar
from dataclasses import dataclass, asdict, field, replace
import hashlib
import json
from pathlib import Path
import jsonschema
from hedgehog import action_commit_packet_v02 as action
from hedgehog import wasm_pure_worker_v01 as worker
from hedgehog.kernel import effect_firewall_v01 as firewall

CONTRACT_VERSION = 'affine-u8-v01'
MISSING_DEFINITION = 'need:pure:affine-u8-v01'
_BRIDGE = ContextVar('radiolaria_pure_bridge', default=None)


@dataclass(frozen=True)
class PureNeedPermissionV01:
    task_id: str
    owning_root_id: str
    initial_revision_id: str
    source_ref: str
    work_id: str
    contract_version: str
    multiplier: int
    offset: int
    memory_scope: str
    profile_version: str
    max_generation_attempts: int
    max_admissions: int
    max_drs_bytes: int


@dataclass(frozen=True)
class PureCapabilityNeedV01:
    need_id: str
    permission: PureNeedPermissionV01
    revision_id: str
    topology_id: str
    observation_id: str
    input_value: int


@dataclass(frozen=True)
class PureResourceUsageV01:
    generation_attempts: int = 0
    admission_attempts: int = 0
    reserved_trials: int = 0
    reserved_fuel: int = 0
    measured_fuel: int = 0
    drs_bytes: int = 0
    measured_drs_bytes: int = 0
    guest_calls: int = 0
    reserved_guest_fuel: int = 0
    measured_guest_fuel: int = 0


@dataclass(frozen=True)
class PureCodeProposalV01:
    need: PureCapabilityNeedV01
    wat: bytes
    oracle: tuple[int, ...]
    source_freeze: tuple[tuple[str, str], ...]
    generation_ordinal: int


@dataclass(frozen=True)
class PureAdmissionAttemptV01:
    need: PureCapabilityNeedV01
    source: bytes
    source_format: str
    oracle: tuple[int, ...]
    worker_result: worker.PureWorkerResultV01
    admitted: bool
    reason: str | None
    ordinal: int


@dataclass(frozen=True)
class AdmittedPurePackageV01:
    package_id: str
    need: PureCapabilityNeedV01
    wasm: bytes
    wasm_sha256: str
    oracle_sha256: str
    attempt: PureAdmissionAttemptV01
    native_admission: firewall.AdmittedCapabilityV01
    _origin: object = field(default=None, repr=False, compare=False)


@dataclass(frozen=True)
class PureNeedResolutionV01:
    resolution_id: str
    need: PureCapabilityNeedV01
    package_id: str
    definition_id: str
    admission_id: str
    membership_epoch: int


@dataclass(frozen=True)
class PureMissingNeedTriggerV01:
    trigger_id: str
    need: PureCapabilityNeedV01
    resolution: PureNeedResolutionV01


@dataclass(frozen=True)
class PureGuestInvocationEvidenceV01:
    invocation: firewall.BoundCapabilityInvocationV01
    native_result_id: str
    package_id: str
    guest_sha256: str
    oracle_sha256: str
    worker_result: worker.PureWorkerResultV01


class _Origin:
    def __init__(self, host):
        self.host, self.package = host, None


def _require(value, reason):
    if not value:
        raise ValueError(reason)


def _digest(value):
    return hashlib.sha256(value).hexdigest()


def _json(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def pure_evidence_identity_v01(kind, value):
    return kind + ':' + _digest(_json(value))


def _schema(value, name):
    schema = json.loads((Path(__file__).resolve().parents[1]/'schemas/capability_admission_v01.schema.json').read_text())
    schema['$ref'] = '#/$defs/'+name
    try:jsonschema.Draft202012Validator(schema).validate(asdict(value))
    except jsonschema.ValidationError as exc:raise ValueError('pure_'+name+'_schema:'+exc.message) from exc


def validate_pure_need_permission_v01(value):
    _require(type(value) is PureNeedPermissionV01, 'pure_permission_type')
    numeric=('multiplier','offset','max_generation_attempts','max_admissions','max_drs_bytes')
    _require(all(type(v) is (int if k in numeric else str) for k,v in asdict(value).items()), 'pure_permission_field_types')
    _schema(value,'permission')
    _require(value.contract_version == CONTRACT_VERSION and value.profile_version == worker.PROFILE_VERSION, 'pure_permission_contract')
    return True


def validate_pure_need_v01(need):
    _require(type(need) is PureCapabilityNeedV01, 'pure_need_type')
    validate_pure_need_permission_v01(need.permission)
    _schema(need,'need')
    _require(type(need.input_value) is int and 0 <= need.input_value <= 255, 'pure_need_input_domain')
    material = asdict(need)
    del material['need_id']
    _require(all(type(getattr(need,n)) is str and getattr(need,n) for n in ('revision_id','topology_id','observation_id'))
        and need.need_id == pure_evidence_identity_v01('pure_need', material), 'pure_need_identity')
    return True


def validate_pure_resolution_v01(value):
    _require(type(value) is PureNeedResolutionV01, 'pure_resolution_type')
    validate_pure_need_v01(value.need)
    _schema(value,'resolution')
    _require(type(value.membership_epoch) is int,'pure_resolution_epoch_type')
    material=asdict(value);del material['resolution_id']
    _require(value.resolution_id==pure_evidence_identity_v01('pure_resolution',material),'pure_resolution_identity')
    return True


def validate_pure_missing_trigger_shape_v01(value):
    _require(type(value) is PureMissingNeedTriggerV01,'pure_trigger_type')
    validate_pure_need_v01(value.need)
    validate_pure_resolution_v01(value.resolution)
    _schema(value,'trigger')
    _require(value.need==value.resolution.need and value.trigger_id==pure_evidence_identity_v01('pure_missing_trigger',
        dict(need=asdict(value.need),resolution=asdict(value.resolution))),'pure_trigger_identity')
    return True


def validate_pure_resource_usage_v01(value):
    _require(type(value) is PureResourceUsageV01 and all(type(v) is int and v >= 0
        for v in asdict(value).values()), 'pure_resource_shape')
    _require(value.reserved_trials == value.admission_attempts * 256
        and value.reserved_fuel == value.reserved_trials * worker.MAX_FUEL
        and value.measured_fuel <= value.reserved_fuel and value.measured_drs_bytes <= value.drs_bytes
        and value.reserved_guest_fuel == value.guest_calls * worker.MAX_FUEL
        and value.measured_guest_fuel <= value.reserved_guest_fuel, 'pure_resource_binding')
    return True


def pure_need_oracle_v01(need):
    """Independent finite mathematical oracle, no guest output is consulted."""
    validate_pure_need_v01(need)
    p = need.permission
    return tuple((x * p.multiplier + p.offset) % 256 for x in range(256))


def pure_source_freeze_v01():
    root = Path(__file__).resolve().parents[1]
    paths = ('hedgehog/capability_admission_v01.py', 'hedgehog/wasm_pure_worker_v01.py',
        'hedgehog/capability_memory_binding_v01.py', 'hedgehog/kernel/work_composition_v01.py',
        'hedgehog/work_execution_host_v01.py', 'schemas/capability_admission_v01.schema.json',
        'schemas/work_composition_v01.schema.json')
    return tuple((p, _digest((root/p).read_bytes())) for p in paths)


def generate_controlled_pure_candidate_v01(host, *, need, expected_revision):
    from hedgehog import work_execution_host_v01 as hosts
    with host._lock:
        hosts.reserve_pure_need_work_v01(host, need=need, kind='generation', byte_count=0, expected_revision=expected_revision)
        # Both independent inputs are frozen before the controlled proposer runs.
        oracle = pure_need_oracle_v01(need)
        freeze = pure_source_freeze_v01()
        p = need.permission
        wat = ('(module (func (export "transform") (param i32) (result i32) '
            'local.get 0 i32.const ' + str(p.multiplier) + ' i32.mul i32.const ' + str(p.offset)
            + ' i32.add i32.const 255 i32.and))').encode('ascii')
        proposal = PureCodeProposalV01(need, wat, oracle, freeze, host._pure_usage[p.task_id].generation_attempts)
        host._pure_proposals.append(proposal)
        return proposal


def _field(name, kind, *, allowed=()):
    return firewall.build_capability_field_v01(name=name, value_type=kind, required=True,
        consequential=False, minimum=0 if kind == 'INTEGER' else None,
        maximum=255 if kind == 'INTEGER' else None, allowed_values=allowed)


def _native_definition(package_id):
    from hedgehog import work_execution_host_v01 as hosts
    callbacks = (validate_pure_bridge_inputs_v01, validate_pure_bridge_output_v01, execute_pure_bridge_v01)
    snapshots = tuple(hosts.observe_local_capability_code_v01(c) for c in callbacks)
    return firewall.build_capability_definition_v01(operation_id='pure.affine_u8', version=CONTRACT_VERSION,
        effect_kind='PURE', business_semantics=None,
        input_fields=(_field('package_ref','REFERENCE',allowed=(package_id,)), _field('value','INTEGER')),
        output_fields=(_field('value','INTEGER'),), resource_refs=(),
        input_validator_ref=snapshots[0].public_symbol, output_validator_ref=snapshots[1].public_symbol,
        executor_ref=snapshots[2].public_symbol,
        code_sha256s=tuple((s.public_symbol,s.source_sha256) for s in snapshots))


def admit_pure_candidate_v01(host, *, need, source, source_format, contract_version, expected_revision,
    fuel=worker.MAX_FUEL, wall_seconds=worker.MAX_WALL):
    from hedgehog import work_execution_host_v01 as hosts
    with host._lock:
        hosts.reserve_pure_need_work_v01(host, need=need, kind='admission', byte_count=0, expected_revision=expected_revision)
        _require(contract_version == need.permission.contract_version == CONTRACT_VERSION, 'pure_admission_contract_version')
        oracle = pure_need_oracle_v01(need)
        result = worker.run_pure_wasm_worker_v01(source, source_format=source_format,
            inputs=tuple(range(256)), fuel=fuel, wall_seconds=wall_seconds)
        reason = result.reason
        if reason is None and tuple(t[1] for t in result.trials) != oracle:
            reason = 'pure_oracle_mismatch'
        attempt = PureAdmissionAttemptV01(need,source,source_format,oracle,result,reason is None,reason,
            host._pure_usage[need.permission.task_id].admission_attempts)
        host._pure_attempts.append(attempt)
        usage = host._pure_usage[need.permission.task_id]
        host._pure_usage[need.permission.task_id] = replace(usage,
            measured_fuel=usage.measured_fuel + result.measured_fuel)
        if reason is not None:
            return attempt, None
        oracle_hash = _digest(_json(oracle))
        package_id = pure_evidence_identity_v01('pure_package', dict(wasm_sha256=_digest(result.wasm),
            contract=CONTRACT_VERSION, multiplier=need.permission.multiplier, offset=need.permission.offset,
            oracle_sha256=oracle_hash, configuration_sha256=result.configuration_sha256))
        definition = _native_definition(package_id)
        admitted = hosts.admit_local_capability_v01(definition=definition,
            input_validator=validate_pure_bridge_inputs_v01, output_validator=validate_pure_bridge_output_v01,
            executor=execute_pure_bridge_v01, catalogue_revision=len(host._catalogue_history),
            host_instance_ref='host:' + host.owning_root_id)
        origin = _Origin(host)
        package = AdmittedPurePackageV01(package_id,need,result.wasm,_digest(result.wasm),oracle_hash,attempt,admitted,origin)
        origin.package = package
        host._pure_pending.append(package)
        return attempt, package


def validate_admitted_pure_package_v01(package, *, host, need):
    _require(type(package) is AdmittedPurePackageV01 and type(package.attempt) is PureAdmissionAttemptV01
        and type(package.attempt.worker_result) is worker.PureWorkerResultV01, 'pure_package_type')
    _require(type(package.wasm) is bytes and package.wasm == package.attempt.worker_result.wasm
        and _digest(package.wasm) == package.wasm_sha256, 'pure_package_byte_drift')
    _require(type(package._origin) is _Origin
        and package._origin.host is host and package._origin.package is package, 'pure_foreign_admission')
    validate_pure_need_v01(need)
    _require(package.need == need and any(package.attempt is a for a in host._pure_attempts)
        and host._pure_permissions.get(need.permission.task_id) == need.permission, 'pure_admission_need')
    result = package.attempt.worker_result
    _require(package.attempt.admitted and package.attempt.reason is None and result.status == 'SUCCEEDED'
        and result.process_reaped and result.return_code == 0, 'pure_admission_not_successful')
    worker.validate_closed_pure_wasm_v01(package.wasm)
    oracle = pure_need_oracle_v01(need)
    _require(tuple(t[0] for t in result.trials) == tuple(range(256)) and tuple(t[1] for t in result.trials) == oracle
        and package.oracle_sha256 == _digest(_json(oracle)) and package.attempt.oracle == oracle,
        'pure_admission_oracle_binding')
    _require(result.engine_version == worker.ENGINE_VERSION and result.profile_version == worker.PROFILE_VERSION
        and result.configuration_sha256 == worker._config_digest(), 'pure_admission_profile')
    _require(not firewall.validate_admitted_capability_v01(package.native_admission)
        and package.native_admission.definition == _native_definition(package.package_id), 'pure_native_bridge_binding')
    return True


def _bridge_package(definition, inputs):
    context = _BRIDGE.get()
    _require(context is not None, 'pure_bridge_host_context')
    host, package, task_id = context
    _require(host._active and package.need.permission.task_id == task_id and host._pure_packages.get(
        package.native_admission.admission_id) is package, 'pure_bridge_host_binding')
    validate_admitted_pure_package_v01(package, host=host, need=package.need)
    _require(definition == package.native_admission.definition, 'pure_bridge_definition')
    errors = firewall.validate_capability_values_v01(definition.input_fields, inputs)
    _require(not errors, errors[0] if errors else 'pure_input_fields')
    values = {v.parameter_name:v.value for v in inputs}
    _require(values['package_ref'] == package.package_id, 'pure_input_package_selection')
    return host, package, values['value']


def validate_pure_bridge_inputs_v01(definition, inputs):
    try:
        _bridge_package(definition, inputs)
        reasons = ()
    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        reasons = (str(exc),)
    return firewall.build_capability_validation_evidence_v01(definition=definition, values=inputs,
        invocation_id=None, valid=not reasons, reason_codes=reasons)


def execute_pure_bridge_v01(invocation):
    host, package, _ = _BRIDGE.get()
    host, package, value = _bridge_package(package.native_admission.definition, invocation.inputs)
    _require(invocation.admission_id == package.native_admission.admission_id and
        invocation.task_id == package.need.permission.task_id and invocation.owning_root_id == host.owning_root_id,
        'pure_guest_invocation_binding')
    usage = host._pure_usage[invocation.task_id]
    host._pure_usage[invocation.task_id] = replace(usage,guest_calls=usage.guest_calls+1,
        reserved_guest_fuel=usage.reserved_guest_fuel+worker.MAX_FUEL)
    result = worker.run_pure_wasm_worker_v01(package.wasm, source_format='wasm', inputs=(value,))
    usage = host._pure_usage[invocation.task_id]
    host._pure_usage[invocation.task_id] = replace(usage,measured_guest_fuel=usage.measured_guest_fuel+result.measured_fuel)
    host._pure_guest_runs.append((invocation, package, result))
    _require(result.status == 'SUCCEEDED', result.reason or 'pure_guest_failed')
    return (action.build_action_effect_parameter_record_v01(parameter_name='value', value_type='INTEGER', value=result.trials[0][1]),)


def validate_pure_bridge_output_v01(definition, invocation, output):
    try:
        host, package, value = _bridge_package(definition, invocation.inputs)
        errors = firewall.validate_capability_values_v01(definition.output_fields, output)
        _require(not errors, errors[0] if errors else 'pure_output_fields')
        observed = [r for i,p,r in host._pure_guest_runs if i is invocation and p is package]
        _require(len(observed) == 1 and observed[0].status == 'SUCCEEDED' and output[0].value ==
            observed[0].trials[0][1] == pure_need_oracle_v01(package.need)[value], 'pure_output_actual_guest')
        reasons = ()
    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        reasons = (str(exc),)
    return firewall.build_capability_validation_evidence_v01(definition=definition, values=output,
        invocation_id=invocation.invocation_id, valid=not reasons, reason_codes=reasons)


def validate_pure_guest_evidence_v01(evidence, *, host):
    _require(type(evidence) is PureGuestInvocationEvidenceV01 and evidence in host._pure_guest_evidence, 'pure_guest_not_observed')
    package = host._pure_packages[evidence.invocation.admission_id]
    validate_admitted_pure_package_v01(package, host=host, need=package.need)
    pairs = [(i,r) for i,r in host.completed_work if i is evidence.invocation and r.result_id == evidence.native_result_id]
    _require(len(pairs) == 1, 'pure_guest_native_result')
    invocation, result = pairs[0]
    _require(not firewall.validate_capability_execution_result_v01(result,invocation,
        firewall.snapshot_admitted_capability_v01(package.native_admission)), 'pure_guest_native_validation')
    _require((evidence.package_id,evidence.guest_sha256,evidence.oracle_sha256) ==
        (package.package_id,package.wasm_sha256,package.oracle_sha256), 'pure_guest_identity')
    _require(evidence.worker_result.status == 'SUCCEEDED' and evidence.worker_result.wasm == package.wasm
        and result.output[0].value == evidence.worker_result.trials[0][1]
        and evidence.worker_result.trials[0][0] == next(v.value for v in invocation.inputs if v.parameter_name=='value'),
        'pure_guest_actual_result')
    return True
