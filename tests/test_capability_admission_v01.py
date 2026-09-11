"""Actual closed-profile engine refusals, not mocked validation statuses."""
from dataclasses import asdict, replace
import hashlib
import json
import pytest
from hedgehog import wasm_pure_worker_v01 as worker
from hedgehog import capability_admission_v01 as pure
from hedgehog import work_execution_host_v01 as hosts
from demo import run_capability_cold_start_reuse_v01 as demo

IDENTITY=b'(module (func (export "transform") (param i32) (result i32) local.get 0))'


def emit(case, **values):
    print('U3_CASE '+json.dumps(dict(case=case,**values),sort_keys=True),flush=True)


def test_u3_engine_profile_and_actual_refusal_neighbors():
    positive=worker.run_pure_wasm_worker_v01(IDENTITY,source_format='wat',inputs=tuple(range(256)))
    assert positive.status=='SUCCEEDED' and positive.process_reaped and positive.return_code==0
    assert tuple(t[1] for t in positive.trials)==tuple(range(256))
    assert positive.measured_fuel==sum(t[2] for t in positive.trials)>0
    assert worker.validate_closed_pure_wasm_v01(positive.wasm)
    emit('PROFILE_POSITIVE_256',result=asdict(positive)|{'wasm_sha256':hashlib.sha256(positive.wasm).hexdigest(),
        'wasm':positive.wasm.hex(),'stdout':positive.stdout.decode(),'stderr':positive.stderr.decode()})
    cases=(
        ('IMPORT',b'(module (import "host" "f" (func (param i32) (result i32))) (export "transform" (func 0)))','profile_section_forbidden:2'),
        ('EXPORT',IDENTITY.replace(b'transform',b'other'),'profile_exact_export'),
        ('TYPE',b'(module (func (export "transform") (param i64) (result i32) i32.const 0))','profile_function_type'),
        ('MEMORY',IDENTITY.replace(b'(module',b'(module (memory 1)'),'profile_section_forbidden:5'),
        ('TABLE',IDENTITY.replace(b'(module',b'(module (table 1 funcref)'),'profile_section_forbidden:4'),
        ('FLOAT_LOCAL',b'(module (func (export "transform") (param i32) (result i32) (local f32) local.get 0))','profile_local_type_or_count'),
        ('FLOAT_OPCODE',b'(module (func (export "transform") (param i32) (result i32) f32.const 1 drop local.get 0))','profile_opcode_forbidden:67'),
        ('START',b'(module (func (export "transform") (param i32) (result i32) local.get 0) (start 0))','profile_section_forbidden:8'),
        ('TRAP',b'(module (func (export "transform") (param i32) (result i32) unreachable))','unreachable'),
        ('FUEL',b'(module (func (export "transform") (param i32) (result i32) (loop br 0) i32.const 0))','fuel'),
        ('OUTPUT_DOMAIN',b'(module (func (export "transform") (param i32) (result i32) i32.const 256))','worker_output_domain'),
    )
    for case,source,reason in cases:
        result=worker.run_pure_wasm_worker_v01(source,source_format='wat',inputs=(1,))
        assert result.status=='REFUSED' and result.process_reaped and result.return_code!=0
        assert reason in result.reason
        if case in ('TRAP','FUEL','OUTPUT_DOMAIN'):assert result.measured_fuel>0
        emit(case,reason=result.reason,phase=result.phase,return_code=result.return_code,
            measured_fuel=result.measured_fuel,raw_stdout=result.stdout.decode(),raw_stderr=result.stderr.decode())
    for value in (-1,256,True):
        with pytest.raises(ValueError,match='worker_input_domain'):
            worker.run_pure_wasm_worker_v01(IDENTITY,source_format='wat',inputs=(value,))
    with pytest.raises(ValueError,match='worker_source_limit'):
        worker.run_pure_wasm_worker_v01(b'x'*16385,source_format='wat',inputs=(1,))


def test_u3_actual_worker_deadline_and_standard_positive():
    timeout=worker.run_pure_wasm_worker_v01(IDENTITY,source_format='wat',inputs=(1,),wall_seconds=0.000001)
    assert timeout.status=='REFUSED' and timeout.reason=='worker_wall_timeout' and timeout.process_reaped
    emit('WALL_TIMEOUT',phase=timeout.phase,reason=timeout.reason,elapsed=timeout.elapsed_seconds,
        return_code=timeout.return_code,scope='SUPERVISOR_ACTUAL_PHASE_NOT_ASSUMED_GUEST_EXECUTION')
    positive=worker.run_pure_wasm_worker_v01(IDENTITY,source_format='wat',inputs=(1,))
    assert positive.status=='SUCCEEDED' and positive.trials[0][1]==1


def test_u3_admission_oracle_reservations_and_foreign_package():
    task=demo.build_pure_task_v01(task_id='task:u3:admission',multiplier=3,offset=7,value=31,memory_scope='memory:u3:local')
    host,need=task['host'],task['need']
    for scalar in (True,3.0):
        with pytest.raises(ValueError,match='pure_permission_field_types'):
            pure.validate_pure_need_permission_v01(replace(need.permission,multiplier=scalar))
    revision=host.state_revision
    with pytest.raises(ValueError,match='pure_drs_budget'):
        hosts.reserve_pure_need_work_v01(host,need=need,kind='drs',byte_count=need.permission.max_drs_bytes+1,
            expected_revision=revision)
    assert host.state_revision==revision
    proposal=pure.generate_controlled_pure_candidate_v01(host,need=need,expected_revision=host.state_revision)
    assert proposal.oracle==pure.pure_need_oracle_v01(need) and proposal.source_freeze==pure.pure_source_freeze_v01()
    refused,absent=pure.admit_pure_candidate_v01(host,need=need,source=IDENTITY,source_format='wat',
        contract_version=pure.CONTRACT_VERSION,expected_revision=host.state_revision)
    assert absent is None and refused.reason=='pure_oracle_mismatch' and len(refused.worker_result.trials)==256
    assert refused.worker_result.status=='SUCCEEDED'
    usage=hosts.inspect_pure_need_resources_v01(host,task_id=need.permission.task_id)
    assert usage.admission_attempts==1 and usage.reserved_trials==256 and usage.measured_fuel>0
    with pytest.raises(ValueError,match='pure_admission_contract_version'):
        pure.admit_pure_candidate_v01(host,need=need,source=proposal.wat,source_format='wat',
            contract_version='affine-u8-v00',expected_revision=host.state_revision)
    assert hosts.inspect_pure_need_resources_v01(host,task_id=need.permission.task_id).admission_attempts==2
    accepted,package=pure.admit_pure_candidate_v01(host,need=need,source=proposal.wat,source_format='wat',
        contract_version=pure.CONTRACT_VERSION,expected_revision=host.state_revision)
    assert accepted.admitted and pure.validate_admitted_pure_package_v01(package,host=host,need=need)
    changed=package.wasm[:-1]+b'\0'
    for altered in (replace(package,wasm=changed,wasm_sha256=hashlib.sha256(changed).hexdigest()),
                    replace(package,wasm_sha256='0'*64)):
        with pytest.raises(ValueError,match='pure_package_byte_drift'):
            pure.validate_admitted_pure_package_v01(altered,host=host,need=need)
    for altered in (replace(package,native_admission=host.admitted_catalogue[0]),):
        with pytest.raises(ValueError,match='pure_foreign_admission'):
            pure.validate_admitted_pure_package_v01(altered,host=host,need=need)
    emit('ADMISSION_ORACLE_AND_VERSION',reason=refused.reason,trials=refused.worker_result.trials,
        package=package.package_id,usage=asdict(hosts.inspect_pure_need_resources_v01(host,task_id=need.permission.task_id)),
        changed_package_boundary='OBSERVED_BYTE_BINDING_WITH_RECOMPUTED_CHANGED_HASH')
    for _ in range(need.permission.max_generation_attempts-1):
        pure.generate_controlled_pure_candidate_v01(host,need=need,expected_revision=host.state_revision)
    revision=host.state_revision
    with pytest.raises(ValueError,match='pure_generation_exhausted'):
        pure.generate_controlled_pure_candidate_v01(host,need=need,expected_revision=revision)
    assert host.state_revision==revision
    while hosts.inspect_pure_need_resources_v01(host,task_id=need.permission.task_id).admission_attempts<need.permission.max_admissions:
        with pytest.raises(ValueError,match='pure_admission_contract_version'):
            pure.admit_pure_candidate_v01(host,need=need,source=proposal.wat,source_format='wat',
                contract_version='wrong',expected_revision=host.state_revision)
    revision=host.state_revision
    with pytest.raises(ValueError,match='pure_admission_exhausted'):
        pure.admit_pure_candidate_v01(host,need=need,source=proposal.wat,source_format='wat',
            contract_version=pure.CONTRACT_VERSION,expected_revision=revision)
    assert host.state_revision==revision and len(host.work_attempts)==1
